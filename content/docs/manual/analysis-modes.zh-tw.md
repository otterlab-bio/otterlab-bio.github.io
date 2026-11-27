---
title: "分析模式"
weight: 13
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

`otter create --mode` 用於選擇場景。在規範路徑（canonical track）中，**參考攜帶物種資訊**：釋出版本（release）自身記錄了生物體與基因體組裝資訊，因此只需指定釋出版本，無需指定物種。

| `--mode` | 場景 | 參考角色 |
| --- | --- | --- |
| `RRBS` | `rrbs`，或搭配移植物（graft）+宿主（host）的 `bs-pdx` | `--reference-primary`，或 `--reference-graft` + `--reference-host` |
| `WGBS` | `wgbs`（無 PDX 變體） | `--reference-primary` |
| `RNASEQ` | `rnaseq`，或搭配移植物+宿主的 `rna-pdx` | `--reference-primary`，或 `--reference-graft` + `--reference-host` |

`BSSEQ` 會被拒絕：它無法區分 RRBS 與 WGBS，請明確指定其中之一。

以下範例均假設你已先執行 `otter init <dir>`，以鎖定規範路徑所需的工作流資產。

## RRBS

簡化基因體亞硫酸氫鹽定序（Reduced Representation Bisulfite Sequencing）採用酶切感知的預處理與甲基化定量：

```bash
otter create \
  --output my_project \
  --fastq ./fastq \
  --pdata ./samples.csv \
  --mode RRBS \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-primary hg38@GRCh38.p14
```

典型輸出包括修剪後的 FASTQ、比對後的 BAM/BAI、Bismark 覆蓋度檔案、甲基化矩陣/HDF5 以及 QC 報告。

## WGBS

全基因體亞硫酸氫鹽定序（Whole-Genome Bisulfite Sequencing）共用亞硫酸氫鹽工作流介面，但輸入規模與預期覆蓋度不同：

```bash
otter create \
  --output my_project \
  --fastq ./fastq \
  --pdata ./samples.csv \
  --mode WGBS \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-primary hg38@GRCh38.p14
```

WGBS 沒有 PDX 場景，因此傳入 `--reference-graft`/`--reference-host` 會以此為由被直接拒絕，而不會被靜默忽略。

文檔中將 WGBS 列為受支援的工作流形態，但完整生產規模的資質驗證仍屬於獨立的證據邊界。

## RNA-seq

RNA-seq 採用相容 STAR 的比對、相容 HTSeq 的計數、`seq2mat` 矩陣轉換，以及可選的 `matsrun`/rMATS 剪接分析。它需要註解檔案，該檔案包含在釋出版本中：

```bash
otter create \
  --output my_project \
  --fastq ./fastq \
  --pdata ./samples.csv \
  --mode RNASEQ \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-primary hg38@GRCh38.p14
```

主要資料流如下：

```text
FASTQ → fastqcx/Trim Galore → STAR → counts → seq2mat → matsrun/rMATS → qctb
```

## PDX

移植物與宿主是兩個**角色**，因此 PDX 通過同時宣告這兩個角色來指定，而非指定兩個物種：

```bash
otter create \
  --output my_project \
  --fastq ./fastq \
  --pdata ./samples.csv \
  --mode RRBS \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-graft hg38@GRCh38.p14 \
  --reference-host mm10@GRCm38.p6
```

兩個角色必須同時提供，僅提供其中一個會被拒絕。RNA-PDX 場景下的 `--mode RNASEQ` 遵循相同模式。宣告這兩個角色即選擇了 PDX 場景，無需設定單獨開關。

專案記錄的是這兩個角色，而非單一主參考：

```yaml
references:
  species:
    - role: graft
      selection: hg38@GRCh38.p14
    - role: host
      selection: mm10@GRCm38.p6
```

PDX 路徑在此基礎上增加：

```text
dual-reference evidence → xenofilx → pairbam/bamdriver → downstream analysis
```

命令不提供物種參數：移植物與宿主物種均來自所選釋出版本自身的生物體後設資料。未指定任何參考角色的 `create` 呼叫會失敗，並報錯 `scenario "rrbs" requires --reference-primary as id@release`。

## 元件對映

| 階段 | 主要元件 |
| --- | --- |
| 原始 FASTQ QC | `fastqcx` |
| 移植物/宿主分類 | `xenofilx` |
| 配對 BAM 過濾 | `pairbam`、`bamdriver` |
| 表達矩陣 | `seq2mat` |
| 剪接分析 | `matsrun`、外部 rMATS |
| 甲基化/HDF5 | `methx`、外部 Methrix/R |
| QC 彙總 | `qctb` |

[返回手冊](README.md) · [下一章：高階用法](05-advanced-usage.md)
