---
title: "CLI 参考"
weight: 18
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

本章将公开命令树映射到其所属契约。请以已安装发布版本（release）的 `otter <command> --help` 输出作为准确的选项参数来源。

## 项目与执行命令

| 命令 | 用途 | 重要边界 |
| --- | --- | --- |
| `otter init <project>` | 将工作流资产与 schema 固定到规范项目中 | 若存在规范项目或旧版项目标记则拒绝执行。 |
| `otter create` | 配对 FASTQ、校验 pdata/参考基因组并写入项目意图 | 仅支持规范项目；PDX 需要同时提供移植物（graft）和宿主（host）参考角色。 |
| `otter build` | 依次执行 init → create → validate → resolve | 在执行前停止；输出快照（snapshot）的绝对路径。 |
| `otter config validate` | 校验 `v1`、`legacy` 或自动检测的配置 | 旧版校验仅用于支持迁移。 |
| `otter config migrate` | 将现有旧版 `otter.yaml` 转换为 v1 意图 | 需要参考发布版本标识以及规范根目录。 |
| `otter config resolve` | 将意图、参考基因组、站点/后端（backend）及资源冻结到 `run.yaml` | 快照在运行（run）时不可变且具有权威性。 |
| `otter run` | 通过 Craftmake 或 Snakemake 规划或执行一个已解析（resolve）的阶段 | 拒绝原始 `project.yaml` 与旧版 `otter.yaml`。 |
| `otter status [project]` | 汇总项目/运行状态 | 只读。 |
| `otter task list/status/logs/report/stop` | 监控并控制后台 Otter 任务 | `task report` 导出控制器/执行器（executor）证据；它不是科学性比对工具。 |

## 站点与资产命令

```bash
otter site list
otter site generate --id production --backend slurm \
  --partition cpu --account genomics \
  --reference-root /shared/otter/references
otter site validate production
```

`site generate` 会探测机器信息，但需要显式指定集群策略。

```bash
otter assets stamp  --project old_project
otter assets verify --project old_project --strict
otter assets print  --project old_project
```

`assets` 管理兼容时期的 `.otter/assets.manifest.json`；规范 v1 项目使用 `project.lock.yaml` 与已解析的工作流摘要。

## 参考基因组命令

构建并以原子方式发布不可变注册表发布版本：

```bash
otter reference build \
  --registry-root /shared/otter/references \
  --id hg38 --release GRCh38.p14 \
  --organism "Homo sapiens" --assembly GRCh38 \
  --fasta genome.fa.gz --gtf genes.gtf.gz \
  --indexes bismark,bowtie2,star \
  --index-build-threads 16
```

`samtools`、`bismark_genome_preparation`、`bowtie2-build` 和 `STAR` 为默认工具名称。在发布版本运行时中，它们由 `otter-core` 提供。

将某次运行的实际参考基因组选择提升回项目锁定文件：

```bash
# Preview only.
otter reference promote runs/<run-id>/run.yaml

# Apply atomically and append the promotion audit record.
otter reference promote runs/<run-id>/run.yaml --confirm
```

## 产物命令

```bash
# Build and immutably publish results/artifacts.json from declarations.
otter artifact publish runs/<run-id>/run.yaml artifact-declarations.json

# Verify the snapshot boundary, manifest, and checksums.
otter artifact verify runs/<run-id>/run.yaml

# Or verify an explicitly located manifest.
otter artifact verify runs/<run-id>/run.yaml \
  --manifest /absolute/results/artifacts.json

# Compare two already verified publications.
otter artifact compare \
  runs/<left-run-id>/run.yaml \
  runs/<right-run-id>/run.yaml
```

清单（manifest）完成仅证明所声明的标识与完整性，不代表科学结果等价。

## 获取溯源

将已校验的 Craftmake SRA 解码清单转换为不可变的 Otter 溯源记录：

```bash
otter acquisition publish \
  --decode-manifest decode-manifest.json \
  --output acquisition.json \
  --scenario rrbs \
  --primary-id hg38 \
  --primary-release GRCh38.p14 \
  --primary-manifest-sha256 <digest>
```

对于 `bs-pdx`/`rna-pdx`，请将 primary 相关参数替换为完整的移植物与宿主三元组参数：`--graft-id`、`--graft-release`、`--graft-manifest-sha256`、`--host-id`、`--host-release` 和 `--host-manifest-sha256`。该命令会校验所引用的文件，并拒绝覆盖仅限新建的输出文件。

## 执行器基准测试证据

收集已匹配且已完成的 SLURM 记账单元：

```bash
otter benchmark collect \
  --left-run runs/craftmake/run.yaml \
  --left-jobs 123,124 \
  --right-run runs/snakemake/run.yaml \
  --right-jobs 200,201 \
  --phase step2 \
  --output executor-benchmark.json
```

两个快照必须代表相同的不可变比较边界。输出为仅限新建的证据文件，并不意味着某一执行器在所有情况下都更快。

[返回手册](README.md)
