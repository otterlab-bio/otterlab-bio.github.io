---
title: "高階用法"
weight: 14
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

## 自訂參考序列

在規範路徑（canonical track）中，參考不是檔案系統路徑，而是通過 `<id>@<release>` 定址的**登錄檔釋出版本（registry release）**。要使用自訂基因組，只需將其釋出到參考登錄檔（reference registry）一次，之後即可按名稱選擇：

```bash
otter reference build \
  --id myspecies --release ASM123-ensembl-110 \
  --organism 'Mus musculus' --assembly ASM123 \
  --fasta /refs/asm123.fa.gz --gtf /refs/asm123.gtf.gz

otter create \
  --output my_project \
  --fastq ./fastq --pdata ./samples.csv --mode RNASEQ \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-primary myspecies@ASM123-ensembl-110
```

`create` 會根據參考登錄檔驗證該釋出版本並鎖定其清單（manifest）摘要，從而避免專案儲存可能因檔案移動而失效的檔案系統路徑。對於 PDX，請使用 `--reference-graft` 和 `--reference-host` 分別指定角色。不存在接受字面基因組路徑的參數：參考始終以鎖定的登錄檔釋出版本形式進入專案。

## FASTQ 字尾

對於非標準命名，需顯式設定兩個字尾：

```bash
otter create \
  --fastq ./raw_fastq \
  --mode WGBS \
  --suffix1 _1.fq.gz \
  --suffix2 _2.fq.gz \
  --pdata ./samples.xlsx
```

## 資源與 SLURM

資源邊界（envelope）**不是**執行時參數。你需要在 `project.yaml` 中宣告它；`otter config resolve` 會將其解析（resolve）並鎖定到執行（run）快照（snapshot）中，`otter run` 則強制執行這些限制且不接受覆蓋：

```yaml
resources:
  defaults:
    cores: 4
    memory: 8GiB
    time: 08:00:00
    partition: normal
  phases:
    step2:
      cores: 8
      memory: 16GiB
      partition: fat
```

`memory` 接受 `MiB` 或 `GiB`；`time` 接受 `HH:MM:SS`。`phases` 用於覆蓋指定階段的 `defaults` 配置。

執行 `otter config resolve` 時需選擇後端（backend）與站點，以便快照儲存對應的資源邊界：

```bash
otter site generate --id production --backend slurm \
  --partition normal --account genomics \
  --reference-root "$OTTER_REFERENCE_ROOT"

otter config resolve --project my_project/project.yaml \
  --site production --backend slurm
```

`otter config resolve` 會對照目標後端檢查資源邊界，並在作業提交前的解析階段拒絕不可達的分區或超出上限的資源請求。

解析前，請通過 `sinfo` 並向站點管理員確認分區名稱以及帳戶/QOS 限制。

## 試執行、恢復與後台控制

每次執行均基於快照執行，因此在投入計算資源前應先驗證快照：

```bash
otter run \
  --config my_project/runs/<run-id>/run.yaml \
  --executor craftmake \
  --phase step1 \
  --backend local \
  --dry-run \
  --foreground
```

`--dry-run` 會輸出已解析的任務圖及通過驗證的資源邊界，而不實際執行任何任務。

`resume` 是恢復操作，不能用於在原位修改輸入或參考序列。

## 修改執行契約

快照是不可變的，因此任何會改變其契約的執行時參數都會被直接拒絕，而不會被靜默應用：

```text
Error: --step1-cores cannot override an immutable run snapshot; resolve a new run.yaml instead
Error: --engine slurm conflicts with immutable run backend local
```

被拒絕的執行時參數包括 `--backend`、`--engine`、所有 `--stepN-*` 和 `--slurm-*` 資源參數以及 `--copy-fastq`。你仍可傳入 `--parallel-jobs` 和 `--load-ratio`，因為它們僅用於調整本地工作池大小，不會改變任務輸入、命令或單任務資源。

要修改契約，請解析生成新的快照。編輯 `project.yaml` 也會使已有執行失效：快照鎖定了專案摘要，因此若 `project.yaml` 在解析後發生更改，後續執行 `otter run` 時會報告 `run snapshot drift detected` 並拒絕執行。

```bash
otter config resolve --project project.yaml --backend slurm --site production
otter run --config runs/<new-run-id>/run.yaml \
  --executor craftmake --phase step1 --dry-run
```

## 產物驗證

執行完成後，可對已釋出的執行產物進行驗證：

```bash
otter artifact verify runs/<run-id>/run.yaml
```

清單將產物綁定到不可變的執行標識並驗證宣告的校驗和。通過產物驗證僅表明預期輸出檔案存在且校驗和匹配，並不驗證結果的科學準確性。

[返回手冊](README.md) · [下一章：元件參考](06-subtools.md)
