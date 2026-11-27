---
title: "安裝"
weight: 10
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

本章介紹 **OTTER**（**O**rchestrated **T**ranscriptomic, **T**umor-xenograft (PDX/CDX), and **E**pigenomic **R**eporting Workflow）的釋出版本（release）安裝、原始碼編譯、執行環境以及首次驗證。

## 環境要求

- 執行於 amd64（x86-64）或 arm64（AArch64/Apple Silicon）架構的 Linux 或 macOS。配備 SLURM 的 Linux 仍是主要生產目標環境。
- 原始碼編譯要求：遞迴拉取的 Git 子模組、用於完整工具鏈的 Go 1.26.3 或更高版本，以及用於 Rust CLI 的穩定版 Rust/Cargo 與原生 C/CMake 工具。僅頂層 Go 模組本身宣告為 Go 1.24。

## 釋出版本安裝

由四平臺工作流構建的 [OTTER 釋出版本](https://github.com/otterlab-bio/otter/releases) 對 Go 安裝程式採用以下命名規則。其餘工具使用相同的平臺字尾。

| 宿主機 | 安裝程式資產 | 連結方式 |
| --- | --- | --- |
| Linux x86-64 | `otter-install-linux-amd64-static` | 靜態連結 |
| Linux AArch64 | `otter-install-linux-arm64-static` | 靜態連結 |
| macOS Intel | `otter-install-darwin-amd64` | macOS 系統庫 |
| macOS Apple Silicon | `otter-install-darwin-arm64` | macOS 系統庫 |

Shell 安裝指令碼會自動檢測當前平臺並選擇對應的二進位制檔案：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/otterlab-bio/otter/main/scripts/install.sh) --skip-envs
```

也可以從釋出版本中下載對應的 Go 安裝程式資產，賦予可執行權限後執行。兩種安裝程式均支援 `--version TAG` 參數以指定單個釋出版本。較舊的釋出版本可能不包含對應平臺的二進位制檔案。未指定標籤時，安裝程式會查詢包含匹配工具資產的已釋出版本，包括每日預釋出版本。使用 `--skip-envs` 可僅安裝二進位制檔案而不建立可選的環境配置。在 Intel macOS 上，兩種安裝程式均會自動跳過環境配置：所固定的 Bismark 軟體套件沒有 `osx-64` 構建版本。這不影響原生 OTTER 工具的安裝與執行。

安裝完成後，確認 `otter` 已加入 `PATH` 並檢查已安裝的版本：

```bash
otter --help
otter --version
command -v otter
```

## 原始碼安裝

```bash
git clone --recurse-submodules https://github.com/otterlab-bio/otter.git
cd otter
conda activate go-env
go build -o otter .
./otter --help
```

若克隆儲存庫時未包含子模組：

```bash
git submodule sync --recursive
git submodule update --init --recursive
git submodule status --recursive
```

各獨立元件目錄包括 `craftmake`、`enva`、`fastqcx`、`xenofilx`、`pairbam`、`seq2mat`、`matsrun`、`qctb`、`methx`、`bamdriver`，以及容器儲存庫 `holt`。

## 容器映象

[`holt`](../../holt) 子模組用於構建容器化工作臺，其 `holt-run` 映象取代了原位於本儲存庫根目錄的舊 Dockerfile。該映象在構建時解析（resolve）最新的穩定版 OTTER 釋出版本，因此會跟隨本儲存庫更新而不固定版本：

```bash
docker run --rm -it -p 2222:2222 ghcr.io/otterlab-bio/holt-run:latest otter --version
```

`holt-run` 每週重新構建一次，並在本儲存庫釋出新版本時同步重建。若需本地構建並獲得可復現的映象，可固定釋出版本：

```bash
git submodule update --init holt
docker build --build-arg OTTER_VERSION=v1.3.0 -t holt-run ./holt/holt-run
```

`OTTER_VERSION` 預設為 `latest`。構建過程會在安裝前根據該釋出版本的 `checksums.txt` 驗證每個工具，並從同一釋出版本獲取環境 YAML 檔案，從而保證二進位制檔案與執行時定義始終一致。

該映象針對 **`linux/amd64` 和 `linux/arm64`** 釋出。兩者均基於同一多架構基礎映象（`menci/archlinuxarm`，將 amd64 對映為常規 Arch Linux，將 arm64 對映為 Arch Linux ARM）在原生 runner 上構建，隨後合併為單一清單（manifest）。釋出前，每種架構都會使用完整工具鏈及已建立的 `otter-core` 進行冒煙測試。

映象內還包含 SSH、配備 Posit Ark 核心的 JupyterLab，以及由 `enva` 預先初始化的 `otter-core` 環境；埠與使用者管理請參閱 [holt](https://github.com/otterlab-bio/holt)。


## 執行時環境

使用 `enva` 建立所需的核心環境：

```bash
enva create --core
```

僅在需要時建立相容層：

```bash
enva create --core --snakemake
enva create --core --extra
enva list --detailed
enva validate --all
```

Rust 版 Bismark 3.1.0 與 Bowtie2 2.5.5 由 `otter-core` 環境統一提供。安裝程式不再單獨安裝 Bismark 或 Bowtie2；請通過 `enva run otter-core -- ...` 執行相關命令。

| 環境 | 用途 |
| --- | --- |
| `otter-core` | 必需的工作流依賴與運算元（operator）。 |
| `otter-snakemake` | 可選的 Snakemake 相容執行時。 |
| `otter-extra` | 可選的分析與視覺化工具。 |

OTTER 提供兩種執行器（executor）。`craftmake` 為預設執行器，用於執行規範的 `otter.run/v1` 快照（snapshot）。僅當需要為現有工作流使用 Snakemake 相容執行器時，才需安裝 `otter-snakemake`。

## 驗證元件二進位制檔案

```bash
enva run otter-core -- bismark --version
enva run otter-core -- bowtie2 --version
enva run otter-core -- bismark_genome_preparation --help
```

核心環境規範固定了 `bismark=3.1.0` 與 `bowtie2=2.5.5`，安裝程式會在環境建立後驗證這些版本。Bioconda 為 Linux x86_64、Linux aarch64 和 macOS arm64 提供此 Bismark 構建版本；該配方不支援 macOS x86_64。

並非所有運算元都提供 `--version` 參數；對於這類工具，請改用 `--help`。

## HDF5 編譯環境

`methx` 釋出版二進位制檔案在兩種作業系統上均靜態連結 HDF5，無需單獨安裝 HDF5。若從原始碼編譯，請安裝 CMake 及 C 編譯器（例如 Linux 上的 `build-essential` 或 macOS 上的 Xcode Command Line Tools），然後在 `methx` 目錄中執行 `cargo build --locked --release --features download`。Linux 平臺的釋出構建使用原生 musl 編譯器，使 libc 也保持靜態連結。

## 構建與釋出檢查

**Build Toolchain Platforms** GitHub 工作流會在原生 runner 上為全部四個平臺構建 `otter`、`otter-install`、`craftmake`、`matsrun`、`pairbam`、`seq2mat`、`xenofilx`、`enva`、`fastqcx`、`methx` 和 `qctb`。`bamdriver` 作為 Go 庫進行構建，因此沒有可下載的 `bamdriver` 二進位制檔案。各元件儲存庫也配有各自的原生構建工作流。頂層釋出工作流僅在全部四個作業通過後，才會釋出彙總後的資產、校驗和與清單。檢查範圍涵蓋二進位制格式、架構、CLI 啟動、Linux 靜態連結以及安裝程式的離線計劃；這些檢查不執行完整的科學工作流，也不驗證每個作業系統上第三方軟體套件的可用性。


## 相容性說明

部分原始碼級符號、生成的狀態路徑或早期釋出版本資產仍可能使用 `xdxtools`。`xdxtools` 為早期相容名稱。輸出檔案可能以 OTTER 命名，而部分內部符號和執行時路徑仍沿用 `xdxtools`。

[返回手冊目錄](README.md) · [文檔中心](../README.md)
