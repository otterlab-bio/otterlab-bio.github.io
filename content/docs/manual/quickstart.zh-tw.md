---
title: "快速開始"
weight: 12
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

Otter 編寫以磁碟上的 `project.lock.yaml` 為標記的規範（canonical）v1 專案。早期釋出版本（release）在舊版相容佈局（legacy compatibility layout）中建立的專案（以 `.otter/assets.manifest.json` 為標記，且 `userspace/<jobid>/` 下包含 `config/otter.yaml`）仍可被檢測到：編寫類命令會拒絕此類專案，而[遷移](#migrating-a-legacy-project-to-v1)可將其轉換為規範專案。

## 規範 v1 專案

### 1. 初始化專案

```bash
otter init my_project
```

該命令會將打包的工作流資產固定到 `my_project/` 並記錄其摘要：

```text
my_project/
├── project.lock.yaml   # track marker and pinned asset digests
├── workflows/          # packaged workflow assets, including the Snakefiles
│   └── rules/          # Snakemake compatibility rules
├── environments/       # packaged environment declarations
├── schemas/            # packaged JSON schemas
└── runs/               # immutable run snapshots, written by config resolve
```

規則位於 `workflows/` 下而非專案根目錄，因為 Snakefile 的 `include:` 指令是相對於 Snakefile 自身路徑解析的。將它們放在一起，可使規範專案在不向專案根目錄寫入任何資產的情況下執行。

### 2. 提供參考登錄檔（reference registry）釋出版本

規範專案鎖定邏輯參考 ID 與釋出版本摘要，從不將基因組檔案複製到專案中。構建一次釋出版本，或選擇一個現有釋出版本：

```bash
export OTTER_REFERENCE_ROOT=/shared/otter/references
otter reference build \
  --id hg38 --release GRCh38.p14 \
  --organism 'Homo sapiens' --assembly GRCh38 \
  --fasta /staging/genome.fa.gz --gtf /staging/genes.gtf.gz
```

有關佈局、清單（manifest）和校驗和契約，見[參考遷移](08-reference-migration.md)。

### 3. 建立專案意圖

```bash
otter create \
  --output my_project \
  --fastq /data/fastq \
  --pdata /data/samples.csv \
  --mode RRBS \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-primary hg38@GRCh38.p14
```

該命令會對照參考登錄檔驗證每個宣告的參考，並寫入 `project.yaml`、`samples.tsv` 和 `references.lock.yaml`。`samples.tsv` 記錄相對於專案根目錄的每條 FASTQ 路徑，以及分組和接頭（adapter）列；後續若修改該檔案，則需要發起一次新的執行（run）。

對於 PDX 場景，改為指定移植物（graft）和宿主（host）參考：

```bash
otter create \
  --output my_project \
  --fastq /data/fastq \
  --mode RNASEQ \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-graft hg38@GRCh38.p14 \
  --reference-host mm10@GRCm38.p6
```

### 4. 解析（resolve）不可變執行

```bash
otter config validate --config my_project/project.yaml --schema v1

otter config resolve \
  --project my_project/project.yaml \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --backend local
```

在共享叢集上，只需記錄一次站點（site）配置，無需重複傳入參數。`otter site generate` 會探測叢集並寫入配置檔案；在 SLURM 站點上，需要提供它無法自動發現的策略欄位：

```bash
otter site generate --id production --backend slurm \
  --partition cpu112c --account genomics \
  --reference-root "$OTTER_REFERENCE_ROOT"
otter site validate production

otter config resolve --project my_project/project.yaml --site production --backend slurm
```

使用 `--site` 且未指定 `--reference-root` 時，登錄檔根目錄來自站點配置檔案。

解析過程會輸出快照（snapshot）路徑。快照為只讀，並綁定了場景、執行器（executor）、後端（backend）、參考、輸入、摘要和資源：

```text
my_project/runs/run-20260915T094657Z-eghubq/run.yaml
```

### 5. 試執行，再正式執行

```bash
otter run \
  --run-id run-20260915T094657Z-eghubq \
  --project-dir my_project \
  --executor craftmake \
  --phase step1 \
  --backend local \
  --dry-run \
  --foreground
```

`--dry-run` 對應 `craftmake plan`：它會解析工作流目錄（workflow catalog）並報告任務圖，而不執行任何操作。去掉 `--dry-run` 即可執行；在已配置的叢集上，可將 `--backend local` 替換為 `--backend slurm`。

`--run-id` 是 `--config my_project/runs/<run-id>/run.yaml` 的簡寫形式。Otter 從不在執行時隱式解析 `project.yaml`；快照必須預先存在。

### 從任意目錄執行

無需 `cd` 進入專案目錄。快照是執行邊界，它將每條路徑都記錄為絕對路徑：執行根目錄、work/results/logs/state 目錄、專案配置、固定的工作流資產、已解析的參考釋出版本，以及每個樣本的 FASTQ 路徑及其校驗和。執行時不會從工作目錄探測任何內容，且 `OTTER_REFERENCE_ROOT` 僅作為構建時輸入，因此執行過程不會讀取它。

```bash
# works from anywhere: the path printed by "otter build" is absolute
otter run \
  --config /data/projects/my_project/runs/run-20260915T094657Z-eghubq/run.yaml \
  --executor craftmake --phase step1 --backend local --foreground
```

只有以下三項輸入仍相對於當前 shell 解析：

| 輸入 | 行為 |
| --- | --- |
| `--config <path>` | 相對於工作目錄解析，因此在其他目錄執行時請使用絕對路徑。 |
| `--run-id <id>` | 展開為 `<working-directory>/runs/<id>/run.yaml`，因此它**確實**假定你當前位於專案目錄中。在其他目錄時請改用 `--project-dir <dir>`，或先執行 `cd`。 |
| `--catalog <path>` | 相對於工作目錄解析。通常省略即可：快照已固定該執行所解析的工作流目錄。 |

隨後各執行器會自行定位到正確目錄：Snakemake 路徑會在內部切換到專案目錄，而 Craftmake worker 則以專案目錄作為工作目錄啟動。

### 一步完成編寫

步驟 1–4 也可通過單條命令完成：

```bash
otter build \
  --project-root my_project \
  --fastq /data/fastq \
  --pdata /data/samples.csv \
  --mode RRBS \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-primary hg38@GRCh38.p14 \
  --backend local
```

`otter build` 會串聯執行 init、create、validate 和 resolve，隨後在執行前停止並輸出快照路徑。它生成的專案與上述四個步驟完全一致；端到端演練（e2e rehearsal）會逐一核對產出的每件產物。

它預設使用 `craftmake` 執行器。傳入 `--executor snakemake` 則可在快照中改記錄為 Snakemake 相容執行器。執行器歸屬於執行快照，因此該選擇不會更改 `project.yaml` 中的任何內容，且不同執行之間可以不同。

若目標目錄已包含 `project.yaml`，命令會拒絕執行而非覆蓋。編寫意圖不會原地重寫，因為那樣會靜默使基於它解析的所有現有快照失效；請使用 `otter config resolve` 基於現有專案凍結新的執行。

## 將舊版專案遷移到 v1 {#migrating-a-legacy-project-to-v1}

Otter 不再編寫舊版專案，但早期釋出版本建立的專案仍會在 `userspace/<jobid>/` 下保留 `config/otter.yaml`。該檔案**不被任何執行器接受**：執行它必須先將其轉換為規範專案。

遷移前，可先對舊版檔案進行健全性檢查（`--schema auto` 也可檢測該格式），且仍可驗證舊檢出目錄中固定的資產：

```bash
otter config validate --config old_project/userspace/demo_rrbs/config/otter.yaml --schema legacy
otter assets verify --project old_project --strict
```

`otter config migrate` 將配置轉換為規範專案意圖。由於舊版配置記錄的是檔案系統路徑而非登錄檔釋出版本，因此每個參考都必須以 `id@release` 的形式命名：

```bash
otter init migrated
otter config migrate \
  --input old_project/userspace/demo_rrbs/config/otter.yaml \
  --output migrated/project.yaml \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-primary hg38@GRCh38.p14
```

遷移過程會報告採納的欄位、已棄用的欄位以及衝突項；若仍存在衝突，則不寫入任何內容。

該命令僅寫入專案意圖，因此需要一個已包含解析器所摘要的固定工作流資產的規範專案根目錄（如上文 `otter init` 所建立）。若遷移到空目錄，所得專案將無法解析，命令也會對此發出警告。

解析並執行遷移後的專案（注意這裡會選擇 Snakemake 執行器，因為舊版介面卡將相容軌道對映到該執行器）：

```bash
otter config validate --config migrated/project.yaml --schema v1

otter config resolve --project migrated/project.yaml \
  --reference-root "$OTTER_REFERENCE_ROOT" --backend local

otter run --config migrated/runs/<run-id>/run.yaml \
  --executor snakemake --dry-run --foreground
```

實際執行該流程需要提供 Snakemake 的 `enva` 或 conda 執行時；`--dry-run` 無需該執行時即可驗證配置與工作流規劃。

## 檢視與控制任務

```bash
otter task list
otter task status <task-id>
otter task logs <task-id> --follow
otter task stop <task-id>
otter status my_project
```

未指定 `--foreground` 時，Otter 會建立後台任務並輸出其任務 ID。

[返回手冊](README.md) · [下一章：分析模式](04-analysis-modes.md)
