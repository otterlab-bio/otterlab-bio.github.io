---
title: "參考基因體遷移"
weight: 17
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

本章介紹將現有參考目錄樹遷移到不可變 Otter 參考登錄檔（Reference Registry，`$OTTER_REFERENCE_ROOT`）的受支援相容流程。源目錄佈局取決於具體部署：請使用 `--legacy-inst` 顯式指定其根目錄，不要依賴歷史安裝路徑或目錄約定。

---

## 1. 參考登錄檔契約

在 Otter 中，所有參考基因體均在專案空間之外的不可變登錄檔中集中管理：

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

**關鍵特性**：
- **一次寫入且封存**：已釋出的參考釋出版本（release）會以原子方式重新命名並封存為只讀（`chmod 0555` / `0444`）。
- **密碼學可審計**：每個檔案的 SHA-256 摘要均記錄在 `manifest.json` 中。
- **與專案解耦**：專案僅在 `references.lock.yaml` 中記錄邏輯標識與清單（manifest）摘要：
  ```yaml
  schema_version: otter.references.lock/v1
  references:
    primary:
      id: hg19
      release: GRCh37.p13-gencode-v19
      manifest_digest: sha256:4f8e...
  ```

  鍵為參考**角色**（`primary`、`secondary`、`graft`、`host`），而非參考 ID，摘要欄位為 `manifest_digest`。釋出版本標籤為必填項；推薦使用 `<assembly>-<annotation-source>-<annotation-version>` 命名約定，但不強制要求（模式僅要求滿足 `^[A-Za-z0-9._-]+$`）。目錄佈局與摘要契約在本節中定義。

---

## 2. 遷移工具：`migrate_legacy_reference.sh`

儲存庫提供了自動化遷移指令碼：`scripts/migrate_legacy_reference.sh`。

### CLI 選項

| 參數 | 預設值 | 說明 |
| --- | --- | --- |
| `--legacy-inst PATH` | 設定 `$beaverhome` 時為 `$beaverhome/inst`；否則為必填 | 舊版 `inst/` 目錄路徑 |
| `--species NAME` | `all` | 要遷移的物種：`hg19`、`mm10` 或 `all` |
| `--registry-root PATH` | `$OTTER_REFERENCE_ROOT` 或 `~/.otter/references` | 目標參考登錄檔根目錄 |
| `--mode MODE` | `rebuild` | 遷移模式：`ingest`（快速，對現有索引建立硬連結）或 `rebuild`（從源資料重新建置） |
| `--threads NUM` | `4` | `rebuild` 模式下建置索引使用的 CPU 執行緒數 |
| `--otter-core-bin PATH` | 自動檢測 | `otter-core` 環境的 `bin/` 路徑 |
| `--otter-bin PATH` | 自動檢測 | `otter` 執行檔路徑 |
| `--dry-run` | `false` | 預覽已發現的路徑與計劃執行的命令 |

---

## 3. 執行遷移

### 步驟 1：環境檢查

確保 `otter` 與 `enva` 位於 `PATH` 中，且已建立 `otter-core`：

```bash
which otter enva craftmake
enva run otter-core -- bismark --version
enva run otter-core -- bowtie2 --version
```

### 步驟 2：試執行預覽（Dry-Run）

```bash
export LEGACY_INST=/path/to/legacy/inst
export OTTER_REFERENCE_ROOT=/path/to/otter/references

bash scripts/migrate_legacy_reference.sh \
  --legacy-inst "$LEGACY_INST" \
  --registry-root "$OTTER_REFERENCE_ROOT" \
  --species hg19 \
  --dry-run
```

預期輸出：
```text
  [INFO]  Legacy inst root: /path/to/legacy/inst
  [INFO]  Target registry : /path/to/otter/references
  [INFO]  Source FASTA: <discovered source FASTA>
  [INFO]  Source GTF  : <discovered source GTF>
  [INFO]  Target indexes: bismark,bowtie2,star
  ✓ Migration procedure completed.
```

### 步驟 3：執行遷移

**選項 A：匯入現有索引（推薦）**：
當舊版目錄中已包含預建置的 Bismark 或 STAR 索引時，`--mode ingest` 會通過硬連結複用這些索引（在同一檔案系統上不佔用額外磁碟空間），並生成符合規範的 `reference.yaml`、`manifest.json` 和 `checksums.sha256`：

```bash
bash scripts/migrate_legacy_reference.sh \
  --legacy-inst "$LEGACY_INST" \
  --registry-root "$OTTER_REFERENCE_ROOT" \
  --species hg19 \
  --mode ingest
```

**選項 B：從源資料重建索引**：
使用 `otter reference build` 從源 FASTA 和 GTF 重建全部索引：

```bash
bash scripts/migrate_legacy_reference.sh \
  --legacy-inst "$LEGACY_INST" \
  --registry-root "$OTTER_REFERENCE_ROOT" \
  --species hg19 \
  --mode rebuild \
  --threads 16
```

---

## 4. 驗證遷移後的參考釋出版本

遷移完成後，驗證目錄權限與校驗和：

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

## 5. 專案鎖定

在分析專案目錄中，將參考釋出版本記錄在 `references.lock.yaml` 中：

```yaml
schema_version: otter.references.lock/v1
references:
  primary:
    id: hg19
    release: GRCh37.p13-gencode-v19
    manifest_digest: sha256:<sha256-of-manifest.json>
```

執行 `otter config resolve` 時，它會定位 `$OTTER_REFERENCE_ROOT/genomes/hg19/GRCh37.p13-gencode-v19`，驗證清單摘要是否與鎖定檔案一致，並將已驗證的路徑寫入不可變的 `run.yaml`。

實際使用時，`otter create --reference-primary hg19@GRCh37.p13-gencode-v19 --reference-root "$OTTER_REFERENCE_ROOT"` 會自動寫入該鎖定檔案。

---

[返回使用者手冊](README.md) · [下一章：CLI 參考](09-cli-reference.md)
