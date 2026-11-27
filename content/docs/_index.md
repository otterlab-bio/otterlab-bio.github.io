---
title: "Documentation"
description: "Installation, input preparation, a first run, and the five analysis modes, in the order a project is built."
weight: 1
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: false
type: "docs-index"
aliases: ["/docs/manual/"]
---

The manual follows the path from a first successful run rather than the internal package layout. It covers installation, input preparation, the five analysis modes, and the contracts `otter` enforces at the run boundary.

## Before you begin

- Linux or macOS on amd64 or arm64; Linux with SLURM remains the primary production target.
- Paired FASTQ files and a sample table for `otter create`.
- A published reference registry release, addressed as `<id>@<release>`.
- `enva` and the managed runtime environments when you use the release workflow setup.

## Execution model

```text
otter -> craftmake -> enva -> operators -> bamdriver
```

`craftmake` executes canonical immutable `otter.run/v1` snapshots and is the default for `otter build` and `otter config resolve`. `snakemake` remains the compatibility executor for existing Snakemake workflows.

The chapters below are authored in `docs/manual/` of [otterlab-bio/otter](https://github.com/otterlab-bio/otter) and mirrored here in English, Simplified Chinese, and Traditional Chinese.
