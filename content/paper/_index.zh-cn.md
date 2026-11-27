---
title: "论文"
description: "OTTER 预印本：摘要、全文，以及正文与补充材料的 PDF 下载。"
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
layout: "paper"
paper_venue: "bioRxiv 预印本"
paper_title: "OTTER: Orchestrated Transcriptomic, Tumor-xenograft (PDX/CDX), and Epigenomic Reporting Workflow"
paper_doi: "10.64898/2026.10.24.761506"
paper_date: "2026-10-24"
paper_pdf: "paper/otter-preprint-rev31.pdf"
paper_supp: "paper/otter-preprint-rev31-supplement.pdf"
paper_pdf_pages: 4
paper_supp_pages: 27
paper_summary: "Tumor xenograft sequencing libraries contain mouse host reads that can confound downstream expression and methylation analyses. We present OTTER, an automated multi-omics workflow framework that decouples execution into compiled domain operators, an immutable reference registry, and a native strand-aware edit-distance engine. In matched mixtures, OTTER’s usable recall closely matched Xengsort’s in RNA-seq, with Xengsort higher by 0.200–0.900 percentage points across 42 nonzero replicate comparisons; OTTER’s usable recall was higher by 0.575–1.200 percentage points in RRBS. Requiring qualifying human alignments improved PPV at low human content, while OTTER maintained 51.6%–54.0% usable recall across the RRBS gradient and exact decision parity with XenofilteR on transcriptomics."
paper_availability: "OTTER is implemented in Go and Rust and distributed under the MIT License. We also provide native binaries for Linux and macOS on both amd64 and arm64. Source code is available at github.com/otterlab-bio/otter. Test and validation data are provided at huggingface.co/datasets/fallingstar10/otter-data."
paper_keywords: "patient-derived xenograft (PDX), cell line-derived xenograft (CDX), bisulfite sequencing (RRBS/WGBS), RNA-seq, XenofilteR, host-read deconvolution, workflow automation"
paper_i18n:
  download: "下载"
  main: "正文"
  supp: "补充材料"
  pages: "页"
  abstract: "摘要"
  availability: "可用性与实现"
  keywords: "关键词"
  doi: "DOI"
  note: "这是预印本版本。下方全文为英文原稿（稿件仅有英文版）。补充材料按预印本评议版式排版，并非期刊生产版式。"
  fulltextNote: "以下为投稿时的稿件全文。"
  fulltext: "全文"
  cite: "引用"
---

## 1 Introduction

Tumor xenografts, primarily patient-derived xenograft (PDX) and cell line-derived xenograft (CDX) models (collectively designated XDX models), represent a cornerstone of translational cancer biology, functional genomics, and preclinical drug evaluation (Woo et al. 2019). By engrafting human tumor biopsies or characterized cancer cell lines into immunodeficient mice, XDX models preserve cellular heterogeneity, histological architecture, and therapeutic responsiveness far more effectively than traditional in vitro two-dimensional cultures.

A fundamental computational challenge in xenograft profiling is the infiltration of murine host stroma (comprising fibroblasts, immune cells, endothelial cells, and extracellular matrix) into the human graft: xenograft sequencing libraries are invariably chimeric mixtures of human graft and mouse host reads, with murine content commonly ranging from 10% to over 70% depending on tumor type, passage number, and vascularization (Jo et al. 2019), (Woo et al. 2019). Unless these host reads are removed computationally, they cause severe downstream artifacts, including false somatic variant calls, distorted gene-expression counts, and skewed DNA methylation profiles.

Several tools have been developed to separate host from graft reads. Early strategies such as Xenome (Conway et al. 2012) use *k*-mer-based taxonomic classification, trading base-level precision for speed; alignment-based utilities such as Disambiguate (Ahdesmäki et al. 2016) and XenofilteR (Kluin et al. 2018) compare alignment scores and edit distances across dual-species alignments; and pseudo-alignment tools such as Xengsort (Zentgraf and Rahmann 2021) provide fast, memory-efficient transcriptomic read sorting.

Bisulfite conversion changes the sequence composition of unmethylated reads and affects alignment-based species assignment and edit-distance scoring (Krueger and Andrews 2011). During this work, we made OTTER publicly available, while Altendorfer et al. reported a bisulfite mode for Xengsort in a preprint that supports cytosine-converted WGBS and RRBS data (Altendorfer et al. 2026). We evaluate both approaches on matched RNA-seq and bisulfite-sequencing mixtures, distinguishing raw species classification from usable recovery after alignment because only pairs with qualifying human alignments contribute to downstream matrices.

To address these challenges, we present **OTTER** (https://github.com/otterlab-bio/otter), an automated, production-scale multi-omics workflow for matched PDX/CDX models. OTTER integrates host-read separation with quality control, cluster execution, and downstream processing from raw FastQ files through expression quantification and genome-wide CpG methylation-matrix construction. We evaluated the workflow on production supercomputing clusters, public SRA cohorts spanning RNA-PDX and BS-PDX, and matched compositional gradients. This evaluation connects species assignment to the reads that remain available for downstream expression and methylation analyses.

## 2 System and methods

### 2.1 The xdxtools prototype

In 2025, we began `xdxtools` to add bisulfite-sequencing (RRBS/WGBS) processing to PDX/CDX workflows, with the aim of removing mouse host reads before downstream methylation-matrix construction. To our knowledge, no tool then claimed to support this specific task. We examined XenofilteR’s (Kluin et al. 2018) alignment-based scoring and found that Bismark’s (Krueger and Andrews 2011) stored `NM` includes bisulfite-conversion transitions, inflating mismatch scores for this application. We therefore hypothesized that conversion-aware `NM` recalculation could extend XenofilteR’s host–graft disambiguation to bisulfite data. The prototype tested this idea with Picard’s `IS_BISULFITE_SEQUENCE=true` option; its benchmark results are reported in Supplementary Note 4, Section S4.5.

`xdxtools` was an R package (R ≥ 3.5) built around Snakemake (Mölder et al. 2025) workflows that invoked FastQC, Trim Galore, Samtools, Bismark (Krueger and Andrews 2011), STAR (Dobin et al. 2013), Picard, HTSeq (Anders et al. 2015), XenofilteR (Kluin et al. 2018), and rMATS (Shen et al. 2014) for RRBS, WGBS, and RNA-seq XDX scenarios. An R6 controller (`BeaverGandalf`; Supplementary Note 1) coordinated the workflows, which processed raw FastQ files into analysis-ready `methrix` (Mayakonda et al. 2020) and `bsseq` (Hansen et al. 2012) objects. However, enterprise cluster deployments exposed three systems bottlenecks: (1) multi-omics Conda dependency graphs frequently triggered SAT-solver deadlocks and multi-gigabyte storage bloat; (2) institutional clusters running legacy Linux distributions failed with dynamic-linking symbol errors (`GLIBC_2.XX not found`); and (3) Snakemake’s shared-filesystem lock protocol suffered contention and false-positive aborts on parallel Lustre/NFS storage. These constraints motivated the architectural overhaul into OTTER.

### 2.2 The OTTER architecture

The R prototype allowed us to develop and validate the analytical workflow rapidly, but deploying it on shared clusters required matching R package versions to host system libraries. We chose Go and Rust for the production toolchain to resolve core dependencies at build time and ship prebuilt binaries, including statically linked Linux builds. This simplifies installation of the core tools, while `enva` provisions the workflow environment for upstream tools such as Bismark, Bowtie2, and STAR.

In this architecture (Figure 1), the embedded Go orchestrator (`craftmake`) coordinates asynchronous task execution through a single-writer transactional state store (one SQLite database per project, a single write connection, rollback journal, and memory mapping disabled), which serializes controller writes internally instead of arbitrating them through lock files (Supplementary Note 2, Sections S2.1–S2.4; Supplementary Note 4, Section S4.2). Reference genomic assets are cryptographically sealed in an immutable Reference Genome Registry (`$OTTER_REFERENCE_ROOT`), while canonical execution snapshots bind inputs, configurations, and toolchain manifests into versioned contracts (`otter.run/v1`; Supplementary Note 2, Section S2.5).

### 2.3 Compiled domain operators

Seven compiled domain operators replace the prototype’s legacy R scripts across each computational bottleneck:

- **`fastqcx`** merges the core quality-control metrics of FastQC and seqkit into a single pass, producing output numerically identical to the combined FastQC + SeqKit oracle on identical inputs (Supplementary Note 4, Section S4.3);
- **`xenofilx`** reimplements the Picard + XenofilteR flow via our Go `bamdriver` library with native strand-aware NM recalculation. Transcriptomic decision parity, bisulfite deconvolution benchmarks, and parameter audits are reported in Supplementary Note 4, Section S4.5;
- **`methx`** replaces the `methrix` R package (Mayakonda et al. 2020) in Bismark downstream processing, extracting CpG loci directly from FASTA and optionally annotating them against GTF; evaluated against Methrix’s canonical BSgenome workflow on full-genome eRRBS data, `methx` achieves a 2.41-fold speedup (1 m 32 s vs 3 m 41 s) and slashes peak RSS from 18.62 GiB to 6.42 GiB (a 65.5% memory reduction), emitting versioned HDF5 output whose covered CpG loci and methylation ratios are mathematically identical to `methrix` (zero beta discrepancies exceeding 10^-6^; Supplementary Note 4, Section S4.4);
- **`pairbam`**, **`seq2mat`**, **`matsrun`**, and **`qctb`** replace the remaining R scripts for mate-pair repair, expression-matrix quantification, rMATS splicing orchestration, and multi-modal QC aggregation, respectively.

![Figure 1. The decoupled OTTER system architecture. The otter Go control plane and immutable Reference Registry feed the craftmake orchestrator, which dispatches compiled domain operators (fastqcx, xenofilx, methx, pairbam, seq2mat, matsrun, qctb). The workflow uses the bamdriver primitive library, enva provisions the upstream software environment, and outputs are published under versioned contracts.](/paper/figure1.png)

## 3 Comparative evaluation

### 3.1 Comparison framework and representative benchmark

We compared OTTER and Xengsort using the same paired-end FASTQ inputs (Table 1). OTTER assigns species by comparing paired-end alignments to both genomes, whereas Xengsort classifies reads from *k*-mer evidence before alignment. Because downstream expression and methylation matrices use only pairs with qualifying human alignments, we report Xengsort at both its raw classification stage and after alignment, alongside OTTER’s qualified pairs.

| **A. Classification mechanism** | **OTTER** | **Xengsort** |
|:----|:---:|:---:|
| Workflow input | Paired-end FASTQ reads | Paired-end FASTQ reads |
| Species assignment | Compares human and mouse alignments for each fragment using `xenofilx`. | Assigns fragments to classes using *k*-mer evidence from a joint host–graft index. |
| Bisulfite handling | Uses Bismark alignments and strand-aware edit distances to assign fragments. | Uses a bisulfite index to classify converted reads. We aligned graft-classified pairs with Bismark to assess downstream usability. |

**Table 1.** **Read assignment and downstream usability of OTTER and Xengsort in human–mouse mixtures.** Values summarize three replicate mixtures (recall, mean ± SD; PPV, mean). Recall uses all true human input pairs as its denominator; PPV uses all pairs retained at the indicated stage. For Xengsort raw, we counted all graft calls. For OTTER and Xengsort pass, we counted only selected pairs with a qualifying human alignment. We verified RNA-seq pairs against archived STAR alignments and realigned RRBS graft calls with Bismark. Supplementary Note 5 reports the full gradients (Supplementary Table S11 and Supplementary Table S12).

| **B. Measured performance at 60% human input** | **RNA-seq recall (%)** | **RNA-seq PPV (%)** | **RRBS recall (%)** | **RRBS PPV (%)** |
|:----|:---:|:---:|:---:|:---:|
| OTTER (qualified human alignment) | 92.615 ± 0.035 | 99.9949 | 52.002 ± 0.024 | 99.8949 |
| Xengsort (raw graft calls) | 98.745 ± 0.022 | 99.4907 | 92.475 ± 0.010 | 99.0301 |
| Xengsort (`pass@STAR` / `pass@Bismark`) | 93.208 ± 0.039 | 99.9958 | 51.344 ± 0.031 | 99.9035 |

### 3.2 Performance across compositional gradients

We evaluated Xengsort 2.2.2 (acquired 2026-11-24 UTC) across 14 nonzero human fractions, with three replicates per fraction, and one mouse-only control for each assay, yielding 43 RNA-seq and 43 RRBS mixture results. In RNA-seq, OTTER’s usable recall ranged from 92.13% to 92.69%, while Xengsort’s `pass@STAR` usable recall ranged from 92.60% to 93.25%. Xengsort was higher by 0.200–0.900 percentage points in the 42 nonzero replicate comparisons. Full results are reported in Supplementary Table S11.

In RRBS, Xengsort’s raw classification recall ranged from 92.28% to 93.13%, while its usable recall after Bismark alignment ranged from 50.91% to 52.97%. OTTER’s usable recall ranged from 51.61% to 54.03% across the same nonzero mixture conditions. These matched results show that the large difference between raw and usable Xengsort recall arises at the transition from classification to qualifying human alignment. Full gradient results are reported in Supplementary Table S12; prototype comparisons, authentic SRA validation, and parameter audits are detailed in Supplementary Note 4.

### 3.3 Low-input purity and alignment dropout

At 0.1% human input in RRBS, Xengsort’s raw classification recall was 93.13%, while its raw PPV was 6.45% because false-positive mouse calls outnumbered true human calls. After retaining pairs with qualifying Bismark alignments, Xengsort achieved 52.97% usable recall and 42.73% mapped PPV. OTTER achieved 54.03% usable recall and 40.82% mapped PPV on the same condition (Supplementary Table S12). Thus, alignment filtering provides an important checkpoint for improving the purity of downstream input. In RNA-seq at the same dilution, Xengsort’s raw PPV was 11.66%, compared with a mapped PPV of 94.17% among pairs with qualifying STAR alignments (Supplementary Table S11).

Alignment yield also constrained RRBS recovery. Across three matched 60% human RRBS replicates, OTTER’s mean usable recall was 52.00% with `hg19`/`mm10` and 53.61% with `hg38`/`mm10`. In a stage-level audit of the first `hg38`/`mm10` replicate, Bismark uniquely aligned 324,083 of 600,000 true human pairs (54.01%), and OTTER retained 321,598 of these pairs (53.60% usable recall). This single-replicate audit locates most attrition before deconvolution (Supplementary Note 4, Sections S4.5.3–S4.5.4).

## 4 Discussion and conclusion

Our results connect read classification with downstream usability across transcriptomic and bisulfite-sequencing data. For RNA-seq, OTTER and Xengsort produced closely matched usable recall across the tested gradient. For the matched human–mouse RRBS mixtures, we recommend OTTER when recovery of human fragments is the priority: OTTER recovered more true human pairs with qualifying alignments in every nonzero RRBS replicate, while mapped PPV remained similar at 0.1% human input (40.82% for OTTER and 42.73% for Xengsort). Researchers using Xengsort graft calls should retain pairs with qualifying human alignments, particularly when human content is low, because raw classification alone can yield low PPV in that setting.

The RRBS audit also identifies alignment dropout as a central constraint on usable recovery. Across three matched 60% human RRBS mixtures, changing the human reference from `hg19` to `hg38` raised mean usable recall from 52.00% to 53.61%. In the separately audited `hg38` replicate, 45.99% of true human pairs lacked a unique Bismark alignment, while OTTER retained 99.23% of pairs that aligned uniquely. Future work should focus on improving bisulfite aligners’ handling of converted reads and ambiguous pairs, while evaluating both the additional true human pairs recovered and the mouse pairs accepted into downstream analyses.
