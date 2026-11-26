---
title: "5. Advanced usage"
weight: 14
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

## Custom references

On the canonical track, a reference is not a filesystem path — it is a **registry
release** addressed as `<id>@<release>`. To use your own genome, publish it to the
registry once, then select it by name:

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

`create` verifies the release against the registry and locks its manifest digest,
so the project never stores a filesystem path that can become invalid when files move. For PDX, name the roles
separately with `--reference-graft` and `--reference-host`. There are no flags
that take literal genome paths: a reference always enters a project as a locked
registry release.

## FASTQ suffixes

For non-standard names, set both suffixes explicitly:

```bash
otter create \
  --fastq ./raw_fastq \
  --mode WGBS \
  --suffix1 _1.fq.gz \
  --suffix2 _2.fq.gz \
  --pdata ./samples.xlsx
```

## Resources and SLURM

The resource envelope is **not** a run-time flag. You declare it in `project.yaml`;
`otter config resolve` locks it into the run snapshot, and `otter run` enforces
those limits without accepting overrides:

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

`memory` takes `MiB` or `GiB`; `time` takes `HH:MM:SS`. `phases` overrides
`defaults` for a named phase.

Select the backend and the site when you run `otter config resolve`, so the
snapshot stores that resource envelope:

```bash
otter site generate --id production --backend slurm \
  --partition normal --account genomics \
  --reference-root "$OTTER_REFERENCE_ROOT"

otter config resolve --project my_project/project.yaml \
  --site production --backend slurm
```

`otter config resolve` checks the resource envelope against the target backend and
rejects an unreachable partition or an oversized request during resolution, before
job submission.

Confirm partition names and account/QOS limits with `sinfo` and your site
administrator before resolving.

## Dry-run, resume, and background control

Every run is executed from a snapshot, so validate one before committing resources:

```bash
otter run \
  --config my_project/runs/<run-id>/run.yaml \
  --executor craftmake \
  --phase step1 \
  --backend local \
  --dry-run \
  --foreground
```

`--dry-run` reports the resolved task graph and the resource envelope it validated
without executing anything.

`resume` is a recovery operation, not a way to change inputs or references in
place.

## Changing a run contract

The snapshot is immutable, so the run-time flags that would change its contract are
refused rather than silently applied:

```text
Error: --step1-cores cannot override an immutable run snapshot; resolve a new run.yaml instead
Error: --engine slurm conflicts with immutable run backend local
```

Refused run-time flags include `--backend`, `--engine`, all `--stepN-*` and
`--slurm-*` resource flags, and `--copy-fastq`. You can still pass `--parallel-jobs`
and `--load-ratio` because they only size the local worker pool and do not change
task inputs, commands, or per-task resources.

To change the contract, resolve a new snapshot. Editing `project.yaml` also
invalidates existing runs: the snapshot pins the project digest, so a later
`otter run` reports `run snapshot drift detected` and refuses to execute a run
whose `project.yaml` has changed since resolution.

```bash
otter config resolve --project project.yaml --backend slurm --site production
otter run --config runs/<new-run-id>/run.yaml \
  --executor craftmake --phase step1 --dry-run
```

## Artifact verification

Published run artifacts can be checked after execution:

```bash
otter artifact verify runs/<run-id>/run.yaml
```

The manifest binds artifacts to the immutable run identity and verifies declared checksums. Passing artifact verification confirms only that the expected output files exist with matching checksums; it does not verify the scientific accuracy of the results.

[Back to the manual](README.md) · [Next: component reference](06-subtools.md)

