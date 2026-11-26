# OTTER homepage

The public site for **OTTER** and the `otterlab-bio` organisation, built with
Hugo and the [Blowfish](https://blowfish.page/) theme and deployed to GitHub
Pages. The design rationale, the reference-site measurements, and the copy
rules live in [`DESIGN.md`](./DESIGN.md).

- Live target: `https://otterlab-bio.github.io/`
- Languages: English at `/`, Simplified Chinese at `/zh-cn/`
- Theme: `github.com/nunocoracao/blowfish/v3` v3.11.0, consumed as a Hugo Module
- Design skill: [`gemini-frontend-design`](https://github.com/google-gemini/demolab/tree/main/skills/gemini-frontend-design), installed into `.agents/skills/` and pinned in `skills-lock.json`

```bash
npx skills add google-gemini/demolab --skill gemini-frontend-design
```

## Layout

```text
config/_default/     hugo.toml, params.toml, languages.*, menus.*
content/             _index.md (hero front matter), docs/ pages
data/home/           en.yaml, zh-cn.yaml — every string on the homepage
assets/css/          schemes/otter.css (palette), custom.css (layout)
assets/img/          logo.svg, mark.png
static/              fonts, favicons, robots.txt
layouts/partials/    home/custom.html, ot/*, extend-head.html, extend-footer.html
.github/workflows/   pages.yml
```

Copy is never in the templates. To change a headline, an evaluation number, or a
component description, edit `data/home/en.yaml` and `data/home/zh-cn.yaml`; both
files share the same keys, and the Chinese file must not introduce a fact that
the English file does not state.

## Local build

The site needs Hugo 0.162 or newer and Go, because the theme is a module.

```bash
hugo mod download          # first run only
hugo server --port 1313
```

A production build:

```bash
hugo --minify --gc --baseURL "https://otterlab-bio.github.io/"
```

The build does not run Node and does not compile Tailwind. Blowfish ships a
prebuilt stylesheet; site-specific styling uses plain CSS in
`assets/css/custom.css`, and templates use only utilities that already exist in
that prebuilt bundle.

## Design review

The page was audited against `gemini-frontend-design` twice: first by measurement, then by
running the installed skill against the deployed site. Both passes, with the measured
before and after values for every finding, are in
[`docs/design-review-gemini-frontend-design.md`](./docs/design-review-gemini-frontend-design.md).

## Benchmark data

`data/benchmark.yaml` is generated, not typed. It holds the per-fraction means from
`docs/benchmarks/xengsort-gradient-2026-11-24/results/per-fraction-mean-sd.csv` in the
manuscript repository, and the comparison basis matches the manuscript: OTTER is the
`modern` method; RNA-seq uses Xengsort's `xengsort_graft` output checked against STAR,
and RRBS uses `bismark_replay` checked against Bismark. Regenerate the file when the
archive changes.

## Design constraints worth keeping

1. **No em dashes in prose.** Use subordinate clauses, prepositional phrases, or
   parentheses. Numeric ranges use an en dash (`51.61%–54.03%`).
2. **Every number is traceable.** The evaluation cards restate values from
   `manuscript.typ` (sections 2.3, 3.2, S4.2, S4.4) and the release metadata.
   Adding a figure means adding its source.
3. **No CJK web font.** Display text falls back to the platform Songti or Noto
   Serif stack, which keeps the payload small. Only the Latin display face
   (Fraunces, 67 KB) is self-hosted.
4. **Content is bilingual but not duplicated.** `data/home/*.yaml` is the single
   source for both languages.
5. **Two body type sizes, one display scale.** Body text is 16 px or 14 px. The
   hero `<h1>`, section `<h2>`, and the four evaluation numerals share the display
   scale. Do not introduce an intermediate 17 to 28 px step.
6. **No eyebrow labels, decorative pills, or bordered card grids.** Sections open
   with their heading. List content is hairline-separated rows.

## Deployment

`.github/workflows/pages.yml` builds on every push to `main` and publishes with
`actions/deploy-pages`. One repository setting is required before the first
deploy: **Settings → Pages → Build and deployment → Source: GitHub Actions**.

## Verified in this repository

| Check | Result |
| :--- | :--- |
| Production build | `hugo --minify --gc --panicOnWarning` exits 0 |
| Lighthouse, mobile, simulated throttling | performance 100, accessibility 100, best practices 100, SEO 100 |
| Largest contentful paint | 1.3 s |
| Cumulative layout shift | 0 |
| Body type sizes | two (16 px, 14 px), down from nineteen |
| Benchmark data | 14 fractions x 3 replicates per assay, generated from the manuscript archive |
| Language switch | both directions verified, choice persists across reloads |
| Text under 13 px above the fold | none |
| Kicker labels, decorative pills, badges | none |
| Section first children | `h2, h2, h2, h2, h2, h2` |
| Hero primary buttons | one |
| Horizontal overflow | none at 320, 390, 768, 1024, 1440, 1920 px |
| Text contrast (WCAG AA) | every inspected pair passes, light and dark |
| Prose line length | 64 characters, against a 65 limit |
| Content without JavaScript | every section visible at full opacity |
| Hero starts at the page top | `y = 0`, header borderless until scrolled |
| Touch targets below 900 px | 44 px minimum |
| Tabs | keyboard-focusable, `aria-selected` toggles, panels hide correctly |
| Reduced motion | `prefers-reduced-motion: reduce` disables rise, reveal, hover lift |
| Em dashes and spaced en dashes in copy | 0 |
| Missing assets or 4xx | none across `/`, `/zh-cn/`, `/docs/`, `/zh-cn/docs/` |
| Heading order | h1 → h2 → h3, no skipped level |
| Bilingual key parity | 156 keys in each locale, identical for values that must not be translated |

The design review that produced the first six rows, with the measured before and
after values, is in [`docs/design-review-gemini-frontend-design.md`](./docs/design-review-gemini-frontend-design.md).
