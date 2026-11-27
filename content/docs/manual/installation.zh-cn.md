---
title: "安装"
weight: 10
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

本章介绍 **OTTER**（**O**rchestrated **T**ranscriptomic, **T**umor-xenograft (PDX/CDX), and **E**pigenomic **R**eporting Workflow）的发布版本（release）安装、源码编译、运行环境以及首次验证。

## 环境要求

- 运行于 amd64（x86-64）或 arm64（AArch64/Apple Silicon）架构的 Linux 或 macOS。配备 SLURM 的 Linux 仍是主要生产目标环境。
- 源码编译要求：递归拉取的 Git 子模块、用于完整工具链的 Go 1.26.3 或更高版本，以及用于 Rust CLI 的稳定版 Rust/Cargo 与原生 C/CMake 工具。仅顶层 Go 模块本身声明为 Go 1.24。

## 发布版本安装

由四平台工作流构建的 [OTTER 发布版本](https://github.com/otterlab-bio/otter/releases) 对 Go 安装程序采用以下命名规则。其余工具使用相同的平台后缀。

| 宿主机 | 安装程序资产 | 链接方式 |
| --- | --- | --- |
| Linux x86-64 | `otter-install-linux-amd64-static` | 静态链接 |
| Linux AArch64 | `otter-install-linux-arm64-static` | 静态链接 |
| macOS Intel | `otter-install-darwin-amd64` | macOS 系统库 |
| macOS Apple Silicon | `otter-install-darwin-arm64` | macOS 系统库 |

Shell 安装脚本会自动检测当前平台并选择对应的二进制文件：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/otterlab-bio/otter/main/scripts/install.sh) --skip-envs
```

也可以从发布版本中下载对应的 Go 安装程序资产，赋予可执行权限后运行。两种安装程序均支持 `--version TAG` 参数以指定单个发布版本。较旧的发布版本可能不包含对应平台的二进制文件。未指定标签时，安装程序会查找包含匹配工具资产的已发布版本，包括每日预发布版本。使用 `--skip-envs` 可仅安装二进制文件而不创建可选的环境配置。在 Intel macOS 上，两种安装程序均会自动跳过环境配置：所固定的 Bismark 软件包没有 `osx-64` 构建版本。这不影响原生 OTTER 工具的安装与运行。

安装完成后，确认 `otter` 已加入 `PATH` 并检查已安装的版本：

```bash
otter --help
otter --version
command -v otter
```

## 源码安装

```bash
git clone --recurse-submodules https://github.com/otterlab-bio/otter.git
cd otter
conda activate go-env
go build -o otter .
./otter --help
```

若克隆仓库时未包含子模块：

```bash
git submodule sync --recursive
git submodule update --init --recursive
git submodule status --recursive
```

各独立组件目录包括 `craftmake`、`enva`、`fastqcx`、`xenofilx`、`pairbam`、`seq2mat`、`matsrun`、`qctb`、`methx`、`bamdriver`，以及容器仓库 `holt`。

## 容器镜像

[`holt`](../../holt) 子模块用于构建容器化工作台，其 `holt-run` 镜像取代了原位于本仓库根目录的旧 Dockerfile。该镜像在构建时解析（resolve）最新的稳定版 OTTER 发布版本，因此会跟随本仓库更新而不固定版本：

```bash
docker run --rm -it -p 2222:2222 ghcr.io/otterlab-bio/holt-run:latest otter --version
```

`holt-run` 每周重新构建一次，并在本仓库发布新版本时同步重建。若需本地构建并获得可复现的镜像，可固定发布版本：

```bash
git submodule update --init holt
docker build --build-arg OTTER_VERSION=v1.3.0 -t holt-run ./holt/holt-run
```

`OTTER_VERSION` 默认为 `latest`。构建过程会在安装前根据该发布版本的 `checksums.txt` 校验每个工具，并从同一发布版本获取环境 YAML 文件，从而保证二进制文件与运行时定义始终一致。

该镜像针对 **`linux/amd64` 和 `linux/arm64`** 发布。两者均基于同一多架构基础镜像（`menci/archlinuxarm`，将 amd64 映射为常规 Arch Linux，将 arm64 映射为 Arch Linux ARM）在原生 runner 上构建，随后合并为单一清单（manifest）。发布前，每种架构都会使用完整工具链及已创建的 `otter-core` 进行冒烟测试。

镜像内还包含 SSH、配备 Posit Ark 内核的 JupyterLab，以及由 `enva` 预先初始化的 `otter-core` 环境；端口与用户管理请参阅 [holt](https://github.com/otterlab-bio/holt)。


## 运行时环境

使用 `enva` 创建所需的核心环境：

```bash
enva create --core
```

仅在需要时创建兼容层：

```bash
enva create --core --snakemake
enva create --core --extra
enva list --detailed
enva validate --all
```

Rust 版 Bismark 3.1.0 与 Bowtie2 2.5.5 由 `otter-core` 环境统一提供。安装程序不再单独安装 Bismark 或 Bowtie2；请通过 `enva run otter-core -- ...` 运行相关命令。

| 环境 | 用途 |
| --- | --- |
| `otter-core` | 必需的工作流依赖与算子（operator）。 |
| `otter-snakemake` | 可选的 Snakemake 兼容运行时。 |
| `otter-extra` | 可选的分析与可视化工具。 |

OTTER 提供两种执行器（executor）。`craftmake` 为默认执行器，用于运行规范的 `otter.run/v1` 快照（snapshot）。仅当需要为现有工作流使用 Snakemake 兼容执行器时，才需安装 `otter-snakemake`。

## 验证组件二进制文件

```bash
enva run otter-core -- bismark --version
enva run otter-core -- bowtie2 --version
enva run otter-core -- bismark_genome_preparation --help
```

核心环境规范固定了 `bismark=3.1.0` 与 `bowtie2=2.5.5`，安装程序会在环境创建后校验这些版本。Bioconda 为 Linux x86_64、Linux aarch64 和 macOS arm64 提供此 Bismark 构建版本；该配方不支持 macOS x86_64。

并非所有算子都提供 `--version` 参数；对于这类工具，请改用 `--help`。

## HDF5 编译环境

`methx` 发布版二进制文件在两种操作系统上均静态链接 HDF5，无需单独安装 HDF5。若从源码编译，请安装 CMake 及 C 编译器（例如 Linux 上的 `build-essential` 或 macOS 上的 Xcode Command Line Tools），然后在 `methx` 目录中运行 `cargo build --locked --release --features download`。Linux 平台的发布构建使用原生 musl 编译器，使 libc 也保持静态链接。

## 构建与发布检查

**Build Toolchain Platforms** GitHub 工作流会在原生 runner 上为全部四个平台构建 `otter`、`otter-install`、`craftmake`、`matsrun`、`pairbam`、`seq2mat`、`xenofilx`、`enva`、`fastqcx`、`methx` 和 `qctb`。`bamdriver` 作为 Go 库进行构建，因此没有可下载的 `bamdriver` 二进制文件。各组件仓库也配有各自的原生构建工作流。顶层发布工作流仅在全部四个作业通过后，才会发布汇总后的资产、校验和与清单。检查范围涵盖二进制格式、架构、CLI 启动、Linux 静态链接以及安装程序的离线计划；这些检查不运行完整的科学工作流，也不验证每个操作系统上第三方软件包的可用性。


## 兼容性说明

部分源码级符号、生成的状态路径或早期发布版本资产仍可能使用 `xdxtools`。`xdxtools` 为早期兼容名称。输出文件可能以 OTTER 命名，而部分内部符号和运行时路径仍沿用 `xdxtools`。

[返回手册目录](README.md) · [文档中心](../README.md)
