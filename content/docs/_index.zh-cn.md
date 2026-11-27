---
title: "文档"
description: "安装、输入准备、首次运行与五类分析模式，按项目搭建的顺序编排。"
weight: 1
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: false
type: "docs-index"
aliases: ["/docs/manual/"]
---

手册围绕首次成功运行组织，而非内部软件包结构；内容覆盖安装、输入准备、五类分析模式，以及 `otter` 在运行边界强制执行的各项契约。

## 开始之前

- amd64 或 arm64 架构的 Linux 或 macOS；配备 SLURM 的 Linux 仍是主要生产目标环境。
- 供 `otter create` 使用的配对 FASTQ 文件与样本表。
- 一个已发布的参考基因组注册表版本，按 `<id>@<release>` 指定。
- 使用发布版工作流时，需要 `enva` 及由其管理的运行环境。

## 执行模型

```text
otter -> craftmake -> enva -> 算子 -> bamdriver
```

`craftmake` 执行不可变的 `otter.run/v1` 快照，是 `otter build` 与 `otter config resolve` 的默认执行器。`snakemake` 仍是既有 Snakemake 工作流的兼容执行器。

以下章节在 [otterlab-bio/otter](https://github.com/otterlab-bio/otter) 的 `docs/manual/` 中编写，并在此以英文、简体中文、繁体中文三种语言同步呈现。
