---
title: "文档"
description: "安装、数据准备、首次运行与五类分析模式。"
weight: 1
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: false
---

OTTER 将 FASTQ 与样本信息转换为经过校验的工作流项目，支持本地与 SLURM 执行。文档按任务
组织：首次运行请顺序阅读，也可以直接跳到需要的章节。

## 从这里开始

| 需求 | 阅读 |
| :--- | :--- |
| 安装 release 或从源码构建 | [安装](#安装) |
| 准备 FASTQ 与样本信息 | [数据准备](#数据准备) |
| 跑通第一个工作流 | [快速开始](#快速开始) |
| 选择分析类型 | [分析模式](#分析模式) |
| 查询命令 | [CLI 参考](https://github.com/otterlab-bio/otter/blob/main/docs/manual/09-cli-reference.md) |

## 安装

Release 为 Linux 与 macOS 的 amd64、arm64 提供原生二进制。安装脚本会识别平台、下载匹配的
资产，并用已发布的 checksums 校验。

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/otterlab-bio/otter/main/scripts/install.sh)
```

在 Intel macOS 上安装器只安装二进制，因为锁定的 Bismark 环境没有 `osx-64` 构建。也可以使用
容器镜像：

```bash
docker run --rm -it -p 2222:2222 ghcr.io/otterlab-bio/holt-run:latest otter --version
```

## 数据准备

`otter create` 扫描 FASTQ 目录，按样本名配对读段，并从表型表读取每个样本一行。配对规则、
`pdata` 格式与样本命名规范见
[数据准备](https://github.com/otterlab-bio/otter/blob/main/docs/manual/02-data-preparation.md)。

## 快速开始

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

`otter build` 把 `init`、`create`、校验与解析合并为一步，并在执行前停止。

参考基因组始终以 `<id>@<release>` 选择。`create` 会用注册表校验该选择，并把解析结果写入
`references.lock.yaml`；`config resolve` 随后写出执行器消费的不可变 `otter.run/v1` 快照。
注册表根目录属于部署输入，可通过 `--reference-root`、`OTTER_REFERENCE_ROOT` 或站点配置提供。

## 分析模式

| 模式 | 输入 | 产物 |
| :--- | :--- | :--- |
| RRBS | 亚硫酸氢盐 FASTQ 双端 | 去除宿主后的 CpG 矩阵 |
| WGBS | 亚硫酸氢盐 FASTQ 双端 | 全基因组甲基化矩阵 |
| RNA-seq | RNA FASTQ 双端 | 表达矩阵与可变剪接结果 |
| BS-PDX | 亚硫酸氢盐 FASTQ 双端 | 仅含移植物的甲基化矩阵 |
| RNA-PDX | RNA FASTQ 双端 | 仅含移植物的表达矩阵 |

每种模式在解析 run 时固定阶段顺序、资源边界与算子组合。详见
[分析模式](https://github.com/otterlab-bio/otter/blob/main/docs/manual/04-analysis-modes.md)。

## 复现评测

基准数据、Xengsort 对比表与集群运行记录归档在手稿仓库与 Hugging Face：

- [评测数据](https://huggingface.co/datasets/fallingstar10/otter-data)
- [示例与 Schema](https://github.com/otterlab-bio/otter/tree/main/docs/examples)
- [Colab 演练](https://colab.research.google.com/github/otterlab-bio/otter/blob/main/notebooks/otter-colab-walkthrough-zh.ipynb)
