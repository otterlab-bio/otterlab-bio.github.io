---
title: "常见问题"
weight: 16
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

## 为什么找不到 `otter`？

检查安装目录与 `PATH`：

```bash
command -v otter
printf '%s\n' "$PATH"
```

从源码构建的二进制文件可能仍包含兼容期遗留的 `xdxtools` 符号。部署前请运行 `./otter --help` 确认。

## 为什么安装程序返回 404？

核对规范仓库地址，并在资产为私有时进行身份验证：

```text
https://github.com/otterlab-bio/otter
```

仅通过安装程序支持的环境变量接口传递 `GITHUB_TOKEN`、`GH_TOKEN` 或 `GITHUB_PAT`。切勿提交令牌或将其写入 URL。

## 为什么子模块目录为空？

```bash
git submodule sync --recursive
git submodule update --init --recursive
git submodule status --recursive
```

## 可以立即用 Craftmake 替代 Snakemake 吗？

基本可以。OTTER 为每个运行（run）快照（snapshot）记录单一执行器（executor）。`craftmake` 为默认执行器，负责执行规范 v1 快照；`snakemake` 仍作为兼容执行器保留，可通过 `--executor snakemake` 指定。同一快照不能同时由两者执行。

## 为什么 FASTQ 配对失败？

检查以下各项：

- R1/R2 后缀与 `--suffix1` 和 `--suffix2` 匹配。
- 从文件名提取的样本 ID 与 pdata 中的 `sampleid` 完全一致。
- 每个样本均包含双端配对（mate）。
- 已移除重复的样本 ID。

## 为什么 SLURM 作业提交失败？

检查站点资源可用性以及所请求的资源边界（envelope）：

```bash
sinfo
squeue -u "$(whoami)"

# what the run actually asked for
sed -n '/^execution:/,/^samples:/p' \
  my_project/runs/<run-id>/run.yaml

# re-plan without submitting
otter run \
  --config my_project/runs/<run-id>/run.yaml \
  --executor craftmake --phase step1 --dry-run --foreground
```

通过空运行区分工作流/配置问题与调度器提交问题。将分区、账户/QOS、CPU、内存及检查器设置与集群策略进行比对。

资源边界已在快照中固定，因此运行时的 `--slurm-partition`、`--slurm-cores` 与 `--stepN-*` 参数会被拒绝。若资源边界有误，请修改 `project.yaml` 或站点配置文件中的 `resources:` 并**解析（resolve）一次新的运行**；切勿仅更换参数重试同一快照。

## 为什么 `methx` 报告 HDF5 错误？

发布版本（release）的二进制文件已静态链接 HDF5 运行时，通常无需设置 `HDF5_DIR` 或 `LD_LIBRARY_PATH`。请先校验二进制文件：

```bash
methx --version
file "$(command -v methx)"
ldd "$(command -v methx)" | grep -E 'hdf5|not found' || true
```

若错误发生在源码构建过程中，请遵循 [`methx/docs/BUILD.md`](../../methx/docs/BUILD.md) 中的原生构建说明。如需原生 Methrix 加载，请使用 `methx/scripts/export_methrix_hdf5.R` 转换自定义 HDF5 输出；切勿将自定义文件称为原生 Methrix HDF5 目录。

## 如何查看或恢复后台运行？

运行始终基于快照执行，因此请指定快照而非旧版配置文件：

```bash
otter task list --all
otter task status <task-id>
otter task logs <task-id> --follow

# without --foreground, Otter submits a background task and prints its task ID
otter run \
  --config my_project/runs/<run-id>/run.yaml \
  --executor craftmake --phase step1 --backend local
```

恢复操作使用快照中的运行标识。Craftmake 为每个按阶段划分的运行记录一行状态，因此请针对同一快照与阶段执行恢复：

```bash
craftmake resume \
  --state my_project/runs/<run-id>/state/state.sqlite \
  --run <run-id>--step1 --gate
```

完整的控制器执行顺序与 `--gate` 参数要求请参阅[第 6 章](../subtools/)。

## 为什么文档中仍提及 FastQC、Bismark、Methrix 或 rMATS？

这些名称对应外部工具、数据格式、标准或科学领域，并非历史遗留的产品名称；在描述实际兼容契约时应保持原样不变。

[返回手册](README.md) · [文档中心](../README.md)
