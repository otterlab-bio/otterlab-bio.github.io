---
title: "元件參考"
weight: 15
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

`otter` 負責工作流編排；下方每個元件儲存庫實現一部分領域計算。

## `craftmake`

面向不可變 `otter.run/v1` 快照（snapshot）的原生工作流編譯器與 Local/SLURM 執行器（executor），負責 DAG 編譯、SQLite 狀態管理、快取、恢復、取消與報告生成。

```bash
craftmake doctor --backend local
craftmake plan --config run.yaml --phase step1 --catalog workflows/
```

`craftmake` 是規範 v1 快照的預設執行器。`snakemake` 仍作為現有基於 Snakemake 工作流的相容執行器保留，可通過 `--executor snakemake` 指定。

## `enva`

Rattler 優先的環境生命週期管理器：

```bash
enva create --core
enva create --core --snakemake  # optional legacy compatibility
enva create --core --extra      # optional analysis dependencies
enva list --detailed
enva run otter-core -- <command>
enva validate --all
```

Bismark 3.1.0 與 Bowtie2 2.5.5 由 `otter-core` 環境提供；安裝程式會在建立環境後驗證固定版本。維護中的甲基化規則通過 `enva run otter-core -- ...` 呼叫它們，而非使用使用者全域安裝版本。

`enva` 不會自動接管外部 conda、mamba 或 micromamba 環境。需將該環境設定為相容狀態，或將其依賴遷移至 `enva` 環境中。

## `fastqcx`

FASTQ QC 報告工具，將 HTML 輸出至標準輸出（stdout），並生成相容 FastQC 的摘要檔案供 MultiQC 與 `qctb` 使用：

```bash
fastqcx --fastq sample.fastq.gz --summary qc/sample > reports/sample.html
```

## `xenofilx`

針對 PDX BAM 輸入的移植物/宿主（graft/host）分類器，支援基於參考序列的 NM 重算與亞硫酸氫鹽感知評分：

```bash
xenofilx run --graft graft.bam --host host.bam --output filtered
```

## `pairbam` 與 `bamdriver`

`pairbam` 用於過濾雙端 BAM 記錄。`bamdriver` 提供共用的 BAM/BGZF、排序、索引、FASTA 與比對輔助功能：

```bash
pairbam --coord-sort input_R1.bam input_R2.bam filtered
```

## `seq2mat`

將 HTSeq 計數檔案轉換為 TSV 計數/正規化矩陣及帶版本資訊的清單（manifest）：

```bash
seq2mat --htseq_dir ./htseq --output_dir ./matrix
```

## `matsrun`

根據分組 BAM 檔案、pdata、SeqKit 統計資訊與 GTF 註解生成並執行所有成對 rMATS 對比：

```bash
matsrun run --root ./bam --pdata samples.xlsx \
  --seqlengthQC ./qc --gtf hg38.gtf
```

## `qctb`

從舊版設定或不可變執行快照中彙總工作流 QC 至 Excel 或 TSV：

```bash
qctb --config-dir runs/<run-id> --output qc_summary.xlsx
```

## `methx`

將 Bismark 覆蓋度檔案轉換為自訂 HDF5 及 QC/註解輸出。如需原生 `methrix::load_HDF5_methrix()` 載入，請使用獨立 R 匯出指令碼：

```r
source("methx/scripts/export_methrix_hdf5.R")
```

[返回手冊](README.md) · [下一章：常見問題](07-faq.md)
