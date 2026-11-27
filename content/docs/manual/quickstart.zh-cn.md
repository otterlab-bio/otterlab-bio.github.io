---
title: "快速开始"
weight: 12
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

Otter 编写以磁盘上的 `project.lock.yaml` 为标记的规范（canonical）v1 项目。早期发布版本（release）在旧版兼容布局（legacy compatibility layout）中创建的项目（以 `.otter/assets.manifest.json` 为标记，且 `userspace/<jobid>/` 下包含 `config/otter.yaml`）仍可被检测到：编写类命令会拒绝此类项目，而[迁移](#migrating-a-legacy-project-to-v1)可将其转换为规范项目。

## 规范 v1 项目

### 1. 初始化项目

```bash
otter init my_project
```

该命令会将打包的工作流资产固定到 `my_project/` 并记录其摘要：

```text
my_project/
├── project.lock.yaml   # track marker and pinned asset digests
├── workflows/          # packaged workflow assets, including the Snakefiles
│   └── rules/          # Snakemake compatibility rules
├── environments/       # packaged environment declarations
├── schemas/            # packaged JSON schemas
└── runs/               # immutable run snapshots, written by config resolve
```

规则位于 `workflows/` 下而非项目根目录，因为 Snakefile 的 `include:` 指令是相对于 Snakefile 自身路径解析的。将它们放在一起，可使规范项目在不向项目根目录写入任何资产的情况下运行。

### 2. 提供参考注册表（reference registry）发布版本

规范项目锁定逻辑参考 ID 与发布版本摘要，从不将基因组文件复制到项目中。构建一次发布版本，或选择一个现有发布版本：

```bash
export OTTER_REFERENCE_ROOT=/shared/otter/references
otter reference build \
  --id hg38 --release GRCh38.p14 \
  --organism 'Homo sapiens' --assembly GRCh38 \
  --fasta /staging/genome.fa.gz --gtf /staging/genes.gtf.gz
```

有关布局、清单（manifest）和校验和契约，见[参考迁移](08-reference-migration.md)。

### 3. 创建项目意图

```bash
otter create \
  --output my_project \
  --fastq /data/fastq \
  --pdata /data/samples.csv \
  --mode RRBS \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-primary hg38@GRCh38.p14
```

该命令会对照参考注册表校验每个声明的参考，并写入 `project.yaml`、`samples.tsv` 和 `references.lock.yaml`。`samples.tsv` 记录相对于项目根目录的每条 FASTQ 路径，以及分组和接头（adapter）列；后续若修改该文件，则需要发起一次新的运行（run）。

对于 PDX 场景，改为指定移植物（graft）和宿主（host）参考：

```bash
otter create \
  --output my_project \
  --fastq /data/fastq \
  --mode RNASEQ \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-graft hg38@GRCh38.p14 \
  --reference-host mm10@GRCm38.p6
```

### 4. 解析（resolve）不可变运行

```bash
otter config validate --config my_project/project.yaml --schema v1

otter config resolve \
  --project my_project/project.yaml \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --backend local
```

在共享集群上，只需记录一次站点（site）配置，无需重复传入参数。`otter site generate` 会探测集群并写入配置文件；在 SLURM 站点上，需要提供它无法自动发现的策略字段：

```bash
otter site generate --id production --backend slurm \
  --partition cpu112c --account genomics \
  --reference-root "$OTTER_REFERENCE_ROOT"
otter site validate production

otter config resolve --project my_project/project.yaml --site production --backend slurm
```

使用 `--site` 且未指定 `--reference-root` 时，注册表根目录来自站点配置文件。

解析过程会输出快照（snapshot）路径。快照为只读，并绑定了场景、执行器（executor）、后端（backend）、参考、输入、摘要和资源：

```text
my_project/runs/run-20260915T094657Z-eghubq/run.yaml
```

### 5. 试运行，再正式运行

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

`--dry-run` 对应 `craftmake plan`：它会解析工作流目录（workflow catalog）并报告任务图，而不执行任何操作。去掉 `--dry-run` 即可执行；在已配置的集群上，可将 `--backend local` 替换为 `--backend slurm`。

`--run-id` 是 `--config my_project/runs/<run-id>/run.yaml` 的简写形式。Otter 从不在运行时隐式解析 `project.yaml`；快照必须预先存在。

### 从任意目录运行

无需 `cd` 进入项目目录。快照是执行边界，它将每条路径都记录为绝对路径：运行根目录、work/results/logs/state 目录、项目配置、固定的工作流资产、已解析的参考发布版本，以及每个样本的 FASTQ 路径及其校验和。运行时不会从工作目录探测任何内容，且 `OTTER_REFERENCE_ROOT` 仅作为构建时输入，因此运行过程不会读取它。

```bash
# works from anywhere: the path printed by "otter build" is absolute
otter run \
  --config /data/projects/my_project/runs/run-20260915T094657Z-eghubq/run.yaml \
  --executor craftmake --phase step1 --backend local --foreground
```

只有以下三项输入仍相对于当前 shell 解析：

| 输入 | 行为 |
| --- | --- |
| `--config <path>` | 相对于工作目录解析，因此在其他目录运行时请使用绝对路径。 |
| `--run-id <id>` | 展开为 `<working-directory>/runs/<id>/run.yaml`，因此它**确实**假定你当前位于项目目录中。在其他目录时请改用 `--project-dir <dir>`，或先执行 `cd`。 |
| `--catalog <path>` | 相对于工作目录解析。通常省略即可：快照已固定该运行所解析的工作流目录。 |

随后各执行器会自行定位到正确目录：Snakemake 路径会在内部切换到项目目录，而 Craftmake worker 则以项目目录作为工作目录启动。

### 一步完成编写

步骤 1–4 也可通过单条命令完成：

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

`otter build` 会串联执行 init、create、validate 和 resolve，随后在执行前停止并输出快照路径。它生成的项目与上述四个步骤完全一致；端到端演练（e2e rehearsal）会逐一核对产出的每件产物。

它默认使用 `craftmake` 执行器。传入 `--executor snakemake` 则可在快照中改记录为 Snakemake 兼容执行器。执行器归属于运行快照，因此该选择不会更改 `project.yaml` 中的任何内容，且不同运行之间可以不同。

若目标目录已包含 `project.yaml`，命令会拒绝执行而非覆盖。编写意图不会原地重写，因为那样会静默使基于它解析的所有现有快照失效；请使用 `otter config resolve` 基于现有项目冻结新的运行。

## 将旧版项目迁移到 v1 {#migrating-a-legacy-project-to-v1}

Otter 不再编写旧版项目，但早期发布版本创建的项目仍会在 `userspace/<jobid>/` 下保留 `config/otter.yaml`。该文件**不被任何执行器接受**：运行它必须先将其转换为规范项目。

迁移前，可先对旧版文件进行健全性检查（`--schema auto` 也可检测该格式），且仍可验证旧检出目录中固定的资产：

```bash
otter config validate --config old_project/userspace/demo_rrbs/config/otter.yaml --schema legacy
otter assets verify --project old_project --strict
```

`otter config migrate` 将配置转换为规范项目意图。由于旧版配置记录的是文件系统路径而非注册表发布版本，因此每个参考都必须以 `id@release` 的形式命名：

```bash
otter init migrated
otter config migrate \
  --input old_project/userspace/demo_rrbs/config/otter.yaml \
  --output migrated/project.yaml \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-primary hg38@GRCh38.p14
```

迁移过程会报告采纳的字段、已弃用的字段以及冲突项；若仍存在冲突，则不写入任何内容。

该命令仅写入项目意图，因此需要一个已包含解析器所摘要的固定工作流资产的规范项目根目录（如上文 `otter init` 所创建）。若迁移到空目录，所得项目将无法解析，命令也会对此发出警告。

解析并运行迁移后的项目（注意这里会选择 Snakemake 执行器，因为旧版适配器将兼容轨道映射到该执行器）：

```bash
otter config validate --config migrated/project.yaml --schema v1

otter config resolve --project migrated/project.yaml \
  --reference-root "$OTTER_REFERENCE_ROOT" --backend local

otter run --config migrated/runs/<run-id>/run.yaml \
  --executor snakemake --dry-run --foreground
```

实际执行该流程需要提供 Snakemake 的 `enva` 或 conda 运行时；`--dry-run` 无需该运行时即可验证配置与工作流规划。

## 查看与控制任务

```bash
otter task list
otter task status <task-id>
otter task logs <task-id> --follow
otter task stop <task-id>
otter status my_project
```

未指定 `--foreground` 时，Otter 会创建后台任务并输出其任务 ID。

[返回手册](README.md) · [下一章：分析模式](04-analysis-modes.md)
