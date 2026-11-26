---
title: "参考基因组迁移"
weight: 17
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

本章介绍将现有参考目录树迁移到不可变 Otter 参考注册表（Reference Registry，`$OTTER_REFERENCE_ROOT`）的受支持兼容流程。源目录布局取决于具体部署：请使用 `--legacy-inst` 显式指定其根目录，不要依赖历史安装路径或目录约定。

---

## 1. 参考注册表契约

在 Otter 中，所有参考基因组均在项目空间之外的不可变注册表中集中管理：

```text
$OTTER_REFERENCE_ROOT/
└── genomes/<reference-id>/<release>/
    ├── reference.yaml          # Metadata (schema: otter.reference/v1)
    ├── manifest.json           # SHA-256 digests of every file in the release
    ├── checksums.sha256        # Standard sha256sum verification manifest
    ├── fasta/
    │   ├── <reference-id>.fa
    │   └── <reference-id>.fa.fai
    ├── annotations/
    │   └── <reference-id>.gtf
    └── indexes/
        ├── bismark/            # Bismark CT/GA converted genome
        ├── bowtie2/            # Bowtie2 index files
        └── star/               # STAR index files
```

**关键特性**：
- **一次写入且封存**：已发布的参考发布版本（release）会以原子方式重命名并封存为只读（`chmod 0555` / `0444`）。
- **可加密审计**：每个文件的 SHA-256 摘要均记录在 `manifest.json` 中。
- **与项目解耦**：项目仅在 `references.lock.yaml` 中记录逻辑标识与清单（manifest）摘要：
  ```yaml
  schema_version: otter.references.lock/v1
  references:
    primary:
      id: hg19
      release: GRCh37.p13-gencode-v19
      manifest_digest: sha256:4f8e...
  ```

  键为参考**角色**（`primary`、`secondary`、`graft`、`host`），而非参考 ID，摘要字段为 `manifest_digest`。发布版本标签为必填项；推荐使用 `<assembly>-<annotation-source>-<annotation-version>` 命名约定，但不强制要求（模式仅要求满足 `^[A-Za-z0-9._-]+$`）。目录布局与摘要契约在本节中定义。

---

## 2. 迁移工具：`migrate_legacy_reference.sh`

仓库提供了自动化迁移脚本：`scripts/migrate_legacy_reference.sh`。

### CLI 选项

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--legacy-inst PATH` | 设置 `$beaverhome` 时为 `$beaverhome/inst`；否则为必填 | 旧版 `inst/` 目录路径 |
| `--species NAME` | `all` | 要迁移的物种：`hg19`、`mm10` 或 `all` |
| `--registry-root PATH` | `$OTTER_REFERENCE_ROOT` 或 `~/.otter/references` | 目标参考注册表根目录 |
| `--mode MODE` | `rebuild` | 迁移模式：`ingest`（快速，对现有索引创建硬链接）或 `rebuild`（从源数据重新构建） |
| `--threads NUM` | `4` | `rebuild` 模式下构建索引使用的 CPU 线程数 |
| `--otter-core-bin PATH` | 自动检测 | `otter-core` 环境的 `bin/` 路径 |
| `--otter-bin PATH` | 自动检测 | `otter` 可执行文件路径 |
| `--dry-run` | `false` | 预览已发现的路径与计划执行的命令 |

---

## 3. 执行迁移

### 步骤 1：环境检查

确保 `otter` 与 `enva` 位于 `PATH` 中，且已创建 `otter-core`：

```bash
which otter enva craftmake
enva run otter-core -- bismark --version
enva run otter-core -- bowtie2 --version
```

### 步骤 2：运行预演（Dry-Run）

```bash
export LEGACY_INST=/path/to/legacy/inst
export OTTER_REFERENCE_ROOT=/path/to/otter/references

bash scripts/migrate_legacy_reference.sh \
  --legacy-inst "$LEGACY_INST" \
  --registry-root "$OTTER_REFERENCE_ROOT" \
  --species hg19 \
  --dry-run
```

预期输出：
```text
  [INFO]  Legacy inst root: /path/to/legacy/inst
  [INFO]  Target registry : /path/to/otter/references
  [INFO]  Source FASTA: <discovered source FASTA>
  [INFO]  Source GTF  : <discovered source GTF>
  [INFO]  Target indexes: bismark,bowtie2,star
  ✓ Migration procedure completed.
```

### 步骤 3：执行迁移

**选项 A：导入现有索引（推荐）**：
当旧版目录中已包含预构建的 Bismark 或 STAR 索引时，`--mode ingest` 会通过硬链接复用这些索引（在同一文件系统上不占用额外磁盘空间），并生成符合规范的 `reference.yaml`、`manifest.json` 和 `checksums.sha256`：

```bash
bash scripts/migrate_legacy_reference.sh \
  --legacy-inst "$LEGACY_INST" \
  --registry-root "$OTTER_REFERENCE_ROOT" \
  --species hg19 \
  --mode ingest
```

**选项 B：从源数据重建索引**：
使用 `otter reference build` 从源 FASTA 和 GTF 重建全部索引：

```bash
bash scripts/migrate_legacy_reference.sh \
  --legacy-inst "$LEGACY_INST" \
  --registry-root "$OTTER_REFERENCE_ROOT" \
  --species hg19 \
  --mode rebuild \
  --threads 16
```

---

## 4. 验证迁移后的参考发布版本

迁移完成后，验证目录权限与校验和：

```bash
export OTTER_REFERENCE_ROOT=/path/to/otter/references

# Verify directory permissions (sealed read-only)
ls -ld $OTTER_REFERENCE_ROOT/genomes/hg19/GRCh37.p13-gencode-v19
# Expect permissions: dr-xr-xr-x

# Verify manifest and checksums
cd $OTTER_REFERENCE_ROOT/genomes/hg19/GRCh37.p13-gencode-v19
sha256sum -c checksums.sha256
```

---

## 5. 项目锁定

在分析项目目录中，将参考发布版本记录在 `references.lock.yaml` 中：

```yaml
schema_version: otter.references.lock/v1
references:
  primary:
    id: hg19
    release: GRCh37.p13-gencode-v19
    manifest_digest: sha256:<sha256-of-manifest.json>
```

运行 `otter config resolve` 时，它会定位 `$OTTER_REFERENCE_ROOT/genomes/hg19/GRCh37.p13-gencode-v19`，校验清单摘要是否与锁定文件一致，并将已验证的路径写入不可变的 `run.yaml`。

实际使用时，`otter create --reference-primary hg19@GRCh37.p13-gencode-v19 --reference-root "$OTTER_REFERENCE_ROOT"` 会自动写入该锁定文件。

---

[返回用户手册](README.md) · [下一章：CLI 参考](09-cli-reference.md)
