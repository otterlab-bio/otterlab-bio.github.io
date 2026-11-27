---
title: "分析模式"
weight: 13
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

`otter create --mode` 用于选择场景。在规范路径（canonical track）中，**参考携带物种信息**：发布版本（release）自身记录了生物体与基因组组装信息，因此只需指定发布版本，无需指定物种。

| `--mode` | 场景 | 参考角色 |
| --- | --- | --- |
| `RRBS` | `rrbs`，或搭配移植物（graft）+宿主（host）的 `bs-pdx` | `--reference-primary`，或 `--reference-graft` + `--reference-host` |
| `WGBS` | `wgbs`（无 PDX 变体） | `--reference-primary` |
| `RNASEQ` | `rnaseq`，或搭配移植物+宿主的 `rna-pdx` | `--reference-primary`，或 `--reference-graft` + `--reference-host` |

`BSSEQ` 会被拒绝：它无法区分 RRBS 与 WGBS，请明确指定其中之一。

以下示例均假设你已先运行 `otter init <dir>`，以锁定规范路径所需的工作流资产。

## RRBS

简化基因组亚硫酸氢盐测序（Reduced Representation Bisulfite Sequencing）采用酶切感知的预处理与甲基化定量：

```bash
otter create \
  --output my_project \
  --fastq ./fastq \
  --pdata ./samples.csv \
  --mode RRBS \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-primary hg38@GRCh38.p14
```

典型输出包括修剪后的 FASTQ、比对后的 BAM/BAI、Bismark 覆盖度文件、甲基化矩阵/HDF5 以及 QC 报告。

## WGBS

全基因组亚硫酸氢盐测序（Whole-Genome Bisulfite Sequencing）共用亚硫酸氢盐工作流接口，但输入规模与预期覆盖度不同：

```bash
otter create \
  --output my_project \
  --fastq ./fastq \
  --pdata ./samples.csv \
  --mode WGBS \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-primary hg38@GRCh38.p14
```

WGBS 没有 PDX 场景，因此传入 `--reference-graft`/`--reference-host` 会以此为由被直接拒绝，而不会被静默忽略。

文档中将 WGBS 列为受支持的工作流形态，但完整生产规模的资质验证仍属于独立的证据边界。

## RNA-seq

RNA-seq 采用兼容 STAR 的比对、兼容 HTSeq 的计数、`seq2mat` 矩阵转换，以及可选的 `matsrun`/rMATS 剪接分析。它需要注释文件，该文件包含在发布版本中：

```bash
otter create \
  --output my_project \
  --fastq ./fastq \
  --pdata ./samples.csv \
  --mode RNASEQ \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-primary hg38@GRCh38.p14
```

主要数据流如下：

```text
FASTQ → fastqcx/Trim Galore → STAR → counts → seq2mat → matsrun/rMATS → qctb
```

## PDX

移植物与宿主是两个**角色**，因此 PDX 通过同时声明这两个角色来指定，而非指定两个物种：

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

两个角色必须同时提供，仅提供其中一个会被拒绝。RNA-PDX 场景下的 `--mode RNASEQ` 遵循相同模式。声明这两个角色即选择了 PDX 场景，无需设置单独开关。

项目记录的是这两个角色，而非单一主参考：

```yaml
references:
  species:
    - role: graft
      selection: hg38@GRCh38.p14
    - role: host
      selection: mm10@GRCm38.p6
```

PDX 路径在此基础上增加：

```text
dual-reference evidence → xenofilx → pairbam/bamdriver → downstream analysis
```

命令不提供物种参数：移植物与宿主物种均来自所选发布版本自身的生物体元数据。未指定任何参考角色的 `create` 调用会失败，并报错 `scenario "rrbs" requires --reference-primary as id@release`。

## 组件映射

| 阶段 | 主要组件 |
| --- | --- |
| 原始 FASTQ QC | `fastqcx` |
| 移植物/宿主分类 | `xenofilx` |
| 配对 BAM 过滤 | `pairbam`、`bamdriver` |
| 表达矩阵 | `seq2mat` |
| 剪接分析 | `matsrun`、外部 rMATS |
| 甲基化/HDF5 | `methx`、外部 Methrix/R |
| QC 汇总 | `qctb` |

[返回手册](README.md) · [下一章：高级用法](05-advanced-usage.md)
