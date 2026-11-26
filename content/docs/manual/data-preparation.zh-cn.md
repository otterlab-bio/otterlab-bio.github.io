---
title: "数据准备"
weight: 11
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

成功执行 `otter create` 需要每个样本都具备可识别的一对 FASTQ 文件。pdata 文件为可选项；传入 `--pdata` 时，其中的 `sampleid` 值必须与 FASTQ 样本名称一致。

## FASTQ 命名

默认的配对后缀为：

```text
sample1_R1.fastq.gz
sample1_R2.fastq.gz
```

也可以显式指定其他后缀：

```bash
otter create \
  --fastq ./fastq \
  --mode RRBS \
  --suffix1 _1.fq.gz \
  --suffix2 _2.fq.gz
```

样本匹配对扫描器识别到的后缀及由此解析出的样本名称敏感。请在文件名与 pdata 中保持样本 ID 一致（包括大小写）。

## pdata

`--pdata` 接受 Excel 或 CSV 文件。必需列为 `sampleid`。用于分组与下游比较时，请使用 `sample_group` 或 `condition`。

支持的别名包括：

| 规范字段 | 常见别名 |
| --- | --- |
| `sampleid` | `样本编号`, `样本ID`, `sample_id` |
| `sample_group` | `样本分组`, `分组`, `group` |
| `condition` | `条件`, `treatment` |

CSV 示例：

```csv
sampleid,sample_group,condition
sample1,control,control
sample2,control,control
sample3,treated,treated
sample4,treated,treated
```

`create` 会校验配对样本，并在提供 pdata 时校验其对应关系。运行前应修正重复的 ID 与空的分组值。

## 项目目录结构

推荐的输入目录结构如下：

```text
my_analysis/
├── fastq/
│   ├── sample1_R1.fastq.gz
│   ├── sample1_R2.fastq.gz
│   └── ...
└── samples.xlsx
```

`otter init my_project` 会创建工作流资产目录结构。条件允许时尽量将原始数据保存在项目目录之外，并在受控生产环境中使用绝对路径。

## 运行前检查

```bash
ls fastq/*_R1.fastq.gz
ls fastq/*_R2.fastq.gz
otter create \
  --output my_project \
  --fastq ./fastq \
  --mode RRBS \
  --pdata ./samples.xlsx \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-primary hg38@GRCh38.p14
```

规范流程始终会指定一个参考发布版本（release），因此运行前检查需要一个已发布该版本的参考注册表（reference registry）（参见[快速开始](03-quickstart.md)）。

若配对失败，请先比对实际文件后缀、样本名大小写以及 pdata 中的 `sampleid` 值。若有其他流程依赖当前文件名，请向 `otter create` 传入匹配的 `--suffix1` 与 `--suffix2` 参数，而不要重命名文件。

[返回手册目录](README.md) · [下一章：快速开始](03-quickstart.md)
