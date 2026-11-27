---
title: "高级用法"
weight: 14
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

## 自定义参考序列

在规范路径（canonical track）中，参考不是文件系统路径，而是通过 `<id>@<release>` 寻址的**注册表发布版本（registry release）**。要使用自定义基因组，只需将其发布到参考注册表（reference registry）一次，之后即可按名称选择：

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

`create` 会根据参考注册表校验该发布版本并锁定其清单（manifest）摘要，从而避免项目保存可能因文件移动而失效的文件系统路径。对于 PDX，请使用 `--reference-graft` 和 `--reference-host` 分别指定角色。不存在接受字面基因组路径的参数：参考始终以锁定的注册表发布版本形式进入项目。

## FASTQ 后缀

对于非标准命名，需显式设置两个后缀：

```bash
otter create \
  --fastq ./raw_fastq \
  --mode WGBS \
  --suffix1 _1.fq.gz \
  --suffix2 _2.fq.gz \
  --pdata ./samples.xlsx
```

## 资源与 SLURM

资源边界（envelope）**不是**运行时参数。你需要在 `project.yaml` 中声明它；`otter config resolve` 会将其解析（resolve）并锁定到运行（run）快照（snapshot）中，`otter run` 则强制执行这些限制且不接受覆盖：

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

`memory` 接受 `MiB` 或 `GiB`；`time` 接受 `HH:MM:SS`。`phases` 用于覆盖指定阶段的 `defaults` 配置。

运行 `otter config resolve` 时需选择后端（backend）与站点，以便快照存储对应的资源边界：

```bash
otter site generate --id production --backend slurm \
  --partition normal --account genomics \
  --reference-root "$OTTER_REFERENCE_ROOT"

otter config resolve --project my_project/project.yaml \
  --site production --backend slurm
```

`otter config resolve` 会对照目标后端检查资源边界，并在作业提交前的解析阶段拒绝不可达的分区或超出上限的资源请求。

解析前，请通过 `sinfo` 并向站点管理员确认分区名称以及账户/QOS 限制。

## 试运行、恢复与后台控制

每次运行均基于快照执行，因此在投入计算资源前应先校验快照：

```bash
otter run \
  --config my_project/runs/<run-id>/run.yaml \
  --executor craftmake \
  --phase step1 \
  --backend local \
  --dry-run \
  --foreground
```

`--dry-run` 会输出已解析的任务图及通过校验的资源边界，而不实际执行任何任务。

`resume` 是恢复操作，不能用于在原位修改输入或参考序列。

## 修改运行契约

快照是不可变的，因此任何会改变其契约的运行时参数都会被直接拒绝，而不会被静默应用：

```text
Error: --step1-cores cannot override an immutable run snapshot; resolve a new run.yaml instead
Error: --engine slurm conflicts with immutable run backend local
```

被拒绝的运行时参数包括 `--backend`、`--engine`、所有 `--stepN-*` 和 `--slurm-*` 资源参数以及 `--copy-fastq`。你仍可传入 `--parallel-jobs` 和 `--load-ratio`，因为它们仅用于调整本地工作池大小，不会改变任务输入、命令或单任务资源。

要修改契约，请解析生成新的快照。编辑 `project.yaml` 也会使已有运行失效：快照锁定了项目摘要，因此若 `project.yaml` 在解析后发生更改，后续执行 `otter run` 时会报告 `run snapshot drift detected` 并拒绝执行。

```bash
otter config resolve --project project.yaml --backend slurm --site production
otter run --config runs/<new-run-id>/run.yaml \
  --executor craftmake --phase step1 --dry-run
```

## 产物校验

执行完成后，可对已发布的运行产物进行校验：

```bash
otter artifact verify runs/<run-id>/run.yaml
```

清单将产物绑定到不可变的运行标识并校验声明的校验和。通过产物校验仅表明预期输出文件存在且校验和匹配，并不验证结果的科学准确性。

[返回手册](README.md) · [下一章：组件参考](06-subtools.md)
