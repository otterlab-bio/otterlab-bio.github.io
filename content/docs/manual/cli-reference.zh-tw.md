---
title: "CLI 參考"
weight: 18
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

本章將公開命令樹對映到其所屬契約。請以已安裝釋出版本（release）的 `otter <command> --help` 輸出作為準確的選項參數來源。

## 專案與執行命令

| 命令 | 用途 | 重要邊界 |
| --- | --- | --- |
| `otter init <project>` | 將工作流資產與 schema 固定到規範專案中 | 若存在規範專案或舊版專案標記則拒絕執行。 |
| `otter create` | 配對 FASTQ、驗證 pdata/參考基因體並寫入專案意圖 | 僅支援規範專案；PDX 需要同時提供移植物（graft）和宿主（host）參考角色。 |
| `otter build` | 依次執行 init → create → validate → resolve | 在執行前停止；輸出快照（snapshot）的絕對路徑。 |
| `otter config validate` | 驗證 `v1`、`legacy` 或自動檢測的設定 | 舊版驗證僅用於支援遷移。 |
| `otter config migrate` | 將現有舊版 `otter.yaml` 轉換為 v1 意圖 | 需要參考釋出版本標識以及規範根目錄。 |
| `otter config resolve` | 將意圖、參考基因體、站點/後端（backend）及資源凍結到 `run.yaml` | 快照在執行（run）時不可變且具有權威性。 |
| `otter run` | 通過 Craftmake 或 Snakemake 規劃或執行一個已解析（resolve）的階段 | 拒絕原始 `project.yaml` 與舊版 `otter.yaml`。 |
| `otter status [project]` | 彙總專案/執行狀態 | 只讀。 |
| `otter task list/status/logs/report/stop` | 監控並控制後台 Otter 任務 | `task report` 匯出控制器/執行器（executor）證據；它不是科學性比對工具。 |

## 站點與資產命令

```bash
otter site list
otter site generate --id production --backend slurm \
  --partition cpu --account genomics \
  --reference-root /shared/otter/references
otter site validate production
```

`site generate` 會探測機器資訊，但需要顯式指定叢集策略。

```bash
otter assets stamp  --project old_project
otter assets verify --project old_project --strict
otter assets print  --project old_project
```

`assets` 管理相容時期的 `.otter/assets.manifest.json`；規範 v1 專案使用 `project.lock.yaml` 與已解析的工作流摘要。

## 參考基因體命令

建置並以原子方式釋出不可變登錄檔釋出版本：

```bash
otter reference build \
  --registry-root /shared/otter/references \
  --id hg38 --release GRCh38.p14 \
  --organism "Homo sapiens" --assembly GRCh38 \
  --fasta genome.fa.gz --gtf genes.gtf.gz \
  --indexes bismark,bowtie2,star \
  --index-build-threads 16
```

`samtools`、`bismark_genome_preparation`、`bowtie2-build` 和 `STAR` 為預設工具名稱。在釋出版本執行時中，它們由 `otter-core` 提供。

將某次執行的實際參考基因體選擇提升回專案鎖定檔案：

```bash
# Preview only.
otter reference promote runs/<run-id>/run.yaml

# Apply atomically and append the promotion audit record.
otter reference promote runs/<run-id>/run.yaml --confirm
```

## 產物命令

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

清單（manifest）完成僅證明所宣告的標識與完整性，不代表科學結果等價。

## 獲取溯源

將已驗證的 Craftmake SRA 解碼清單轉換為不可變的 Otter 溯源記錄：

```bash
otter acquisition publish \
  --decode-manifest decode-manifest.json \
  --output acquisition.json \
  --scenario rrbs \
  --primary-id hg38 \
  --primary-release GRCh38.p14 \
  --primary-manifest-sha256 <digest>
```

對於 `bs-pdx`/`rna-pdx`，請將 primary 相關參數替換為完整的移植物與宿主三元組參數：`--graft-id`、`--graft-release`、`--graft-manifest-sha256`、`--host-id`、`--host-release` 和 `--host-manifest-sha256`。該命令會驗證所引用的檔案，並拒絕覆蓋僅限新建的輸出檔案。

## 執行器基準測試證據

收集已匹配且已完成的 SLURM 記賬單元：

```bash
otter benchmark collect \
  --left-run runs/craftmake/run.yaml \
  --left-jobs 123,124 \
  --right-run runs/snakemake/run.yaml \
  --right-jobs 200,201 \
  --phase step2 \
  --output executor-benchmark.json
```

兩個快照必須代表相同的不可變比較邊界。輸出為僅限新建的證據檔案，並不意味著某一執行器在所有情況下都更快。

[返回手冊](README.md)
