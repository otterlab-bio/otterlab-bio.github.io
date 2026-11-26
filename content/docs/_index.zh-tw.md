---
title: "文件"
description: "安裝、資料準備、首次執行與五類分析模式。"
weight: 1
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: false
---

OTTER 將 FASTQ 與樣本資訊轉換為經過驗證的工作流專案，支援本地與 SLURM 執行。文件按任務
組織：首次執行請順序閱讀，也可以直接跳到需要的章節。

## 從這裡開始

| 需求 | 閱讀 |
| :--- | :--- |
| 安裝 release 或從原始碼構建 | [安裝](#安裝) |
| 準備 FASTQ 與樣本資訊 | [資料準備](#資料準備) |
| 跑通第一個工作流 | [快速開始](#快速開始) |
| 選擇分析型別 | [分析模式](#分析模式) |
| 查詢命令 | [CLI 參考](https://github.com/otterlab-bio/otter/blob/main/docs/manual/09-cli-reference.md) |

## 安裝

Release 為 Linux 與 macOS 的 amd64、arm64 提供原生二進位制。安裝指令碼會識別平臺、下載匹配的
資產，並用已釋出的 checksums 驗證。

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/otterlab-bio/otter/main/scripts/install.sh)
```

在 Intel macOS 上安裝器只安裝二進位制，因為鎖定的 Bismark 環境沒有 `osx-64` 構建。也可以使用
容器映象：

```bash
docker run --rm -it -p 2222:2222 ghcr.io/otterlab-bio/holt-run:latest otter --version
```

## 資料準備

`otter create` 掃描 FASTQ 目錄，按樣本名配對讀段，並從表型表讀取每個樣本一行。配對規則、
`pdata` 格式與樣本命名規範見
[資料準備](https://github.com/otterlab-bio/otter/blob/main/docs/manual/02-data-preparation.md)。

## 快速開始

```bash
otter init my_project

otter create \
  --output my_project \
  --fastq /data/fastq \
  --mode RRBS \
  --pdata /data/samples.csv \
  --jobid demo_rrbs \
  --reference-root /shared/otter/references \
  --reference-primary hg19@GRCh37.p13-gencode-v19

otter config validate --config my_project/project.yaml --schema v1
otter config resolve --project my_project/project.yaml --backend local \
  --reference-root /shared/otter/references

otter run --config my_project/runs/<run-id>/run.yaml \
  --executor craftmake --phase step1 --backend local --foreground
```

`otter build` 把 `init`、`create`、驗證與解析合併為一步，並在執行前停止。

參考基因組始終以 `<id>@<release>` 選擇。`create` 會用登錄檔驗證該選擇，並把解析結果寫入
`references.lock.yaml`；`config resolve` 隨後寫出執行器消費的不可變 `otter.run/v1` 快照。
登錄檔根目錄屬於部署輸入，可透過 `--reference-root`、`OTTER_REFERENCE_ROOT` 或站點配置提供。

## 分析模式

| 模式 | 輸入 | 產物 |
| :--- | :--- | :--- |
| RRBS | 亞硫酸氫鹽 FASTQ 雙端 | 去除宿主後的 CpG 矩陣 |
| WGBS | 亞硫酸氫鹽 FASTQ 雙端 | 全基因組甲基化矩陣 |
| RNA-seq | RNA FASTQ 雙端 | 表達矩陣與可變剪接結果 |
| BS-PDX | 亞硫酸氫鹽 FASTQ 雙端 | 僅含移植物的甲基化矩陣 |
| RNA-PDX | RNA FASTQ 雙端 | 僅含移植物的表達矩陣 |

每種模式在解析 run 時固定階段順序、資源邊界與運算元組合。詳見
[分析模式](https://github.com/otterlab-bio/otter/blob/main/docs/manual/04-analysis-modes.md)。

## 復現評測

基準資料、Xengsort 對比表與叢集執行記錄歸檔在手稿儲存庫與 Hugging Face：

- [評測資料](https://huggingface.co/datasets/fallingstar10/otter-data)
- [示例與 Schema](https://github.com/otterlab-bio/otter/tree/main/docs/examples)
- [Colab 演練](https://colab.research.google.com/github/otterlab-bio/otter/blob/main/notebooks/otter-colab-walkthrough-zh.ipynb)
