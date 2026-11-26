---
title: "Documentation"
description: "Installation, data preparation, a first run, and the five analysis modes."
weight: 1
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: false
type: "docs-index"
---

OTTER turns FASTQ inputs and sample metadata into validated workflow projects, then
runs them locally or on SLURM. The manual is task-oriented: read it in order for a
first run, or jump to the chapter you need.

## Start here

| Need | Read |
| :--- | :--- |
| Install a release or build from source | [Installation](#installation) |
| Prepare FASTQ files and sample metadata | [Data preparation](#data-preparation) |
| Run a first workflow | [Quick start](#quick-start) |
| Choose an assay | [Analysis modes](#analysis-modes) |
| Look up a command | [CLI reference](https://github.com/otterlab-bio/otter/blob/main/docs/manual/09-cli-reference.md) |

## Installation

Releases ship native binaries for Linux and macOS on both amd64 and arm64. The shell
installer detects the platform, downloads the matching asset, and verifies it against
the published checksums.

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/otterlab-bio/otter/main/scripts/install.sh)
```

On Intel macOS the installer places the binaries only, because the pinned Bismark
environment has no `osx-64` build. The container image is an alternative:

```bash
docker run --rm -it -p 2222:2222 ghcr.io/otterlab-bio/holt-run:latest otter --version
```

## Data preparation

`otter create` scans a directory of FASTQ files, pairs the reads by sample name, and
reads one row per sample from a phenotype table. Pairing rules, the `pdata` format, and
the sample-naming contract are documented in
[Data preparation](https://github.com/otterlab-bio/otter/blob/main/docs/manual/02-data-preparation.md).

## Quick start

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

`otter build` chains `init`, `create`, validation, and resolution into one step and stops
before execution.

A reference is always selected as `<id>@<release>`. `create` verifies that selection
against the registry and writes the resolved identity to `references.lock.yaml`;
`config resolve` then writes the immutable `otter.run/v1` snapshot that the executor
consumes. The registry root is a deployment input, so supply it with `--reference-root`,
with `OTTER_REFERENCE_ROOT`, or through a site profile.

## Analysis modes

| Mode | Input | What it produces |
| :--- | :--- | :--- |
| RRBS | Bisulfite FASTQ pairs | CpG matrices after host removal |
| WGBS | Bisulfite FASTQ pairs | Genome-wide methylation matrices |
| RNA-seq | RNA FASTQ pairs | Expression matrices and splicing calls |
| BS-PDX | Bisulfite FASTQ pairs | Graft-only methylation matrices |
| RNA-PDX | RNA FASTQ pairs | Graft-only expression matrices |

Each mode fixes its phase order, resource envelope, and operator set when the run is
resolved. See
[Analysis modes](https://github.com/otterlab-bio/otter/blob/main/docs/manual/04-analysis-modes.md).

## Reproducing the evaluation

The benchmark corpus, the Xengsort comparison tables, and the cluster run records are
archived in the manuscript repository and on Hugging Face:

- [Evaluation data](https://huggingface.co/datasets/fallingstar10/otter-data)
- [Worked examples and schemas](https://github.com/otterlab-bio/otter/tree/main/docs/examples)
- [Colab walkthrough](https://colab.research.google.com/github/otterlab-bio/otter/blob/main/notebooks/otter-colab-walkthrough.ipynb)
