---
title: "组件参考"
weight: 15
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

`otter` 负责工作流编排；下方每个组件仓库实现一部分领域计算。

## `craftmake`

面向不可变 `otter.run/v1` 快照（snapshot）的原生工作流编译器与 Local/SLURM 执行器（executor），负责 DAG 编译、SQLite 状态管理、缓存、恢复、取消与报告生成。

```bash
craftmake doctor --backend local
craftmake plan --config run.yaml --phase step1 --catalog workflows/
```

`craftmake` 是规范 v1 快照的默认执行器。`snakemake` 仍作为现有基于 Snakemake 工作流的兼容执行器保留，可通过 `--executor snakemake` 指定。

## `enva`

Rattler 优先的环境生命周期管理器：

```bash
enva create --core
enva create --core --snakemake  # optional legacy compatibility
enva create --core --extra      # optional analysis dependencies
enva list --detailed
enva run otter-core -- <command>
enva validate --all
```

Bismark 3.1.0 与 Bowtie2 2.5.5 由 `otter-core` 环境提供；安装程序会在创建环境后校验固定版本。维护中的甲基化规则通过 `enva run otter-core -- ...` 调用它们，而非使用用户全局安装版本。

`enva` 不会自动接管外部 conda、mamba 或 micromamba 环境。需将该环境配置为兼容状态，或将其依赖迁移至 `enva` 环境中。

## `fastqcx`

FASTQ QC 报告工具，将 HTML 输出至标准输出（stdout），并生成兼容 FastQC 的摘要文件供 MultiQC 与 `qctb` 使用：

```bash
fastqcx --fastq sample.fastq.gz --summary qc/sample > reports/sample.html
```

## `xenofilx`

针对 PDX BAM 输入的移植物/宿主（graft/host）分类器，支持基于参考序列的 NM 重算与亚硫酸氢盐感知评分：

```bash
xenofilx run --graft graft.bam --host host.bam --output filtered
```

## `pairbam` 与 `bamdriver`

`pairbam` 用于过滤双端 BAM 记录。`bamdriver` 提供共用的 BAM/BGZF、排序、索引、FASTA 与比对辅助功能：

```bash
pairbam --coord-sort input_R1.bam input_R2.bam filtered
```

## `seq2mat`

将 HTSeq 计数文件转换为 TSV 计数/归一化矩阵及带版本信息的清单（manifest）：

```bash
seq2mat --htseq_dir ./htseq --output_dir ./matrix
```

## `matsrun`

根据分组 BAM 文件、pdata、SeqKit 统计信息与 GTF 注释生成并运行所有成对 rMATS 对比：

```bash
matsrun run --root ./bam --pdata samples.xlsx \
  --seqlengthQC ./qc --gtf hg38.gtf
```

## `qctb`

从旧版配置或不可变运行快照中汇总工作流 QC 至 Excel 或 TSV：

```bash
qctb --config-dir runs/<run-id> --output qc_summary.xlsx
```

## `methx`

将 Bismark 覆盖度文件转换为自定义 HDF5 及 QC/注释输出。如需原生 `methrix::load_HDF5_methrix()` 加载，请使用独立 R 导出脚本：

```r
source("methx/scripts/export_methrix_hdf5.R")
```

[返回手册](README.md) · [下一章：常见问题](07-faq.md)
