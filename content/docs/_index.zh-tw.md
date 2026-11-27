---
title: "文檔"
description: "安裝、輸入準備、首次執行與五類分析模式，按專案搭建的順序編排。"
weight: 1
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: false
type: "docs-index"
aliases: ["/docs/manual/"]
---

手冊圍繞首次成功執行組織，而非內部軟體套件結構；內容覆蓋安裝、輸入準備、五類分析模式，以及 `otter` 在執行邊界強制執行的各項契約。

## 開始之前

- amd64 或 arm64 架構的 Linux 或 macOS；配備 SLURM 的 Linux 仍是主要生產目標環境。
- 供 `otter create` 使用的配對 FASTQ 檔案與樣本表。
- 一個已釋出的參考基因體登錄檔版本，按 `<id>@<release>` 指定。
- 使用釋出版工作流時，需要 `enva` 及由其管理的執行環境。

## 執行模型

```text
otter -> craftmake -> enva -> 運算子 -> bamdriver
```

`craftmake` 執行不可變的 `otter.run/v1` 快照，是 `otter build` 與 `otter config resolve` 的預設執行器。`snakemake` 仍是既有 Snakemake 工作流的相容執行器。

以下章節在 [otterlab-bio/otter](https://github.com/otterlab-bio/otter) 的 `docs/manual/` 中編寫，並在此以英文、簡體中文、繁體中文三種語言同步呈現。
