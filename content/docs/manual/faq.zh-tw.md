---
title: "常見問題"
weight: 16
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

## 為什麼找不到 `otter`？

檢查安裝目錄與 `PATH`：

```bash
command -v otter
printf '%s\n' "$PATH"
```

從原始碼構建的二進位制檔案可能仍包含相容期遺留的 `xdxtools` 符號。部署前請執行 `./otter --help` 確認。

## 為什麼安裝程式返回 404？

核對規範儲存庫地址，並在資產為私有時進行身份驗證：

```text
https://github.com/otterlab-bio/otter
```

僅通過安裝程式支援的環境變數介面傳遞 `GITHUB_TOKEN`、`GH_TOKEN` 或 `GITHUB_PAT`。切勿提交令牌或將其寫入 URL。

## 為什麼子模組目錄為空？

```bash
git submodule sync --recursive
git submodule update --init --recursive
git submodule status --recursive
```

## 可以立即用 Craftmake 替代 Snakemake 嗎？

基本可以。OTTER 為每個執行（run）快照（snapshot）記錄單一執行器（executor）。`craftmake` 為預設執行器，負責執行規範 v1 快照；`snakemake` 仍作為相容執行器保留，可通過 `--executor snakemake` 指定。同一快照不能同時由兩者執行。

## 為什麼 FASTQ 配對失敗？

檢查以下各項：

- R1/R2 字尾與 `--suffix1` 和 `--suffix2` 匹配。
- 從檔名提取的樣本 ID 與 pdata 中的 `sampleid` 完全一致。
- 每個樣本均包含雙端配對（mate）。
- 已移除重複的樣本 ID。

## 為什麼 SLURM 作業提交失敗？

檢查站點資源可用性以及所請求的資源邊界（envelope）：

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

通過空執行區分工作流/配置問題與排程器提交問題。將分區、帳戶/QOS、CPU、記憶體及檢查器設定與叢集策略進行比對。

資源邊界已在快照中固定，因此執行時的 `--slurm-partition`、`--slurm-cores` 與 `--stepN-*` 參數會被拒絕。若資源邊界有誤，請修改 `project.yaml` 或站點配置檔案中的 `resources:` 並**解析（resolve）一次新的執行**；切勿僅更換參數重試同一快照。

## 為什麼 `methx` 報告 HDF5 錯誤？

釋出版本（release）的二進位制檔案已靜態連結 HDF5 執行時，通常無需設定 `HDF5_DIR` 或 `LD_LIBRARY_PATH`。請先驗證二進位制檔案：

```bash
methx --version
file "$(command -v methx)"
ldd "$(command -v methx)" | grep -E 'hdf5|not found' || true
```

若錯誤發生在原始碼構建過程中，請遵循 [`methx/docs/BUILD.md`](../../methx/docs/BUILD.md) 中的原生構建說明。如需原生 Methrix 載入，請使用 `methx/scripts/export_methrix_hdf5.R` 轉換自訂 HDF5 輸出；切勿將自訂檔案稱為原生 Methrix HDF5 目錄。

## 如何檢視或恢復後台執行？

執行始終基於快照執行，因此請指定快照而非舊版配置檔案：

```bash
otter task list --all
otter task status <task-id>
otter task logs <task-id> --follow

# without --foreground, Otter submits a background task and prints its task ID
otter run \
  --config my_project/runs/<run-id>/run.yaml \
  --executor craftmake --phase step1 --backend local
```

恢復操作使用快照中的執行標識。Craftmake 為每個按階段劃分的執行記錄一行狀態，因此請針對同一快照與階段執行恢復：

```bash
craftmake resume \
  --state my_project/runs/<run-id>/state/state.sqlite \
  --run <run-id>--step1 --gate
```

完整的控制器執行順序與 `--gate` 參數要求請參閱[第 6 章](../subtools/)。

## 為什麼文檔中仍提及 FastQC、Bismark、Methrix 或 rMATS？

這些名稱對應外部工具、資料格式、標準或科學領域，並非歷史遺留的產品名稱；在描述實際相容契約時應保持原樣不變。

[返回手冊](README.md) · [文檔中心](../README.md)
