# OTTER homepage

The public site for **OTTER** and the `otterlab-bio` organisation, built with
Hugo and the [Blowfish](https://blowfish.page/) theme and deployed to GitHub
Pages. The design rationale, the reference-site measurements, and the copy
rules live in [`DESIGN.md`](./DESIGN.md).

- Live target: `https://otter.rainoffallingstar.com/` (custom domain); `https://otterlab-bio.github.io/` redirects to it
- Languages: English at `/`, Simplified Chinese at `/zh-cn/`, Traditional Chinese at `/zh-tw/`
- Theme: `github.com/nunocoracao/blowfish/v3` v3.11.0, consumed as a Hugo Module
- Design skill: [`gemini-frontend-design`](https://github.com/google-gemini/demolab/tree/main/skills/gemini-frontend-design), installed into `.agents/skills/` and pinned in `skills-lock.json`

```bash
npx skills add google-gemini/demolab --skill gemini-frontend-design
```

## Layout

```text
config/_default/     hugo.toml, params.toml, languages.*, menus.*
content/             _index.md (hero front matter), docs/ pages
data/home/           en.yaml, zh-cn.yaml, zh-tw.yaml — every string on the homepage
data/docs/manual.yaml chapter map for the /docs/ hub (tracks, badges, blurbs)
content/paper/       the /paper/ page: preprint metadata, full text, PDF downloads
assets/css/          schemes/otter.css (palette), custom.css (layout)
assets/img/          logo.svg, mark.png
static/              fonts, favicons, robots.txt
layouts/partials/    home/custom.html, ot/*, extend-head.html, extend-footer.html
layouts/docs-index/  the /docs/ hub: primary action, prerequisites, chapter cards
layouts/paper/       the /paper/ page template
static/paper/        the preprint PDFs and the figure used on /paper/
layouts/_default/_markup/render-link.html  resolves the manual's GitHub-style links
scripts/convert-zh-tw.py  regenerates zh-tw chapter bodies from zh-cn (+ --check)
.github/workflows/   pages.yml
```

Copy is never in the templates. To change a headline, an evaluation number, or a
component description, edit `data/home/en.yaml` and `data/home/zh-cn.yaml`; both
files share the same keys, and the Chinese file must not introduce a fact that
the English file does not state.

## The paper page

`/paper/` publishes the preprint: the title, the DOI, the abstract, and the full
text of the manuscript, with download buttons for the manuscript PDF and the
supplementary PDF.

The two PDFs under `static/paper/` are publication copies of the preprint build,
not archives. The archived originals stay in `previews/` under the manuscript
repository's naming contract; the site needs its own copy because GitHub Pages
can only serve files that live in this repository. Together they are about 11 MB,
which is why they carry the stage in the filename: a new stage adds a new pair
rather than silently overwriting the published one.

To publish a new stage, build the preprint in the manuscript repository, copy
both files here under the new stage name, then update `paper_pdf`,
`paper_supp`, `paper_pdf_pages`, and `paper_supp_pages` in the three
`content/paper/_index*.md` files:
`paper_pdf_pages` and `paper_supp_pages` feed the labels next to each download. The full text in those files comes from
`manuscript.Rmd`: run it through `pandoc --citeproc --bibliography=reference0912.bib`
with `-t gfm` so the tables stay pipe tables, strip the reference list, and
demote each heading one level because the page supplies its own `h1`.

Only the labels are translated. The body is the English manuscript in all three
locales, and the page says so in its note.

## Documentation structure

`/docs/` is the hub. It is an orientation page, not a copy of chapter 1: a single
primary action into Installation, the prerequisite list, the execution model, then
a card for each manual chapter grouped into three tracks (get running, configure and
operate, look up and recover). The chapter map, the track labels, the `01`..`09`
badges, and the one-line purposes live in `data/docs/manual.yaml` in all three
languages, because `content/docs/manual/` is synced verbatim from
`otterlab-bio/otter:docs/manual` and cannot carry site-only front matter.

`/docs/manual/` no longer renders a page of its own. Its section index sets
`build.render: never` so the chapters keep their URLs, and `/docs/` declares
`/docs/manual/` as an alias, so the old address redirects to the hub instead of
competing with it for search results. The hub carries no sticky sidebar, because the
card grid already lists all nine chapters; chapter pages keep the sidebar and the
prev/next pager, which now opens with an Overview link and closes the last chapter
with a link back to the hub.

The chapters link to each other with GitHub-style relative paths (`README.md`,
`03-quickstart.md`, `../subtools/`, `../../holt`). `layouts/_default/_markup/render-link.html`
resolves those to site pages, and sends paths that leave the docs section to the
software repository on GitHub, so the synced sources stay untouched.

## Local build

The site needs Hugo 0.162 or newer and Go, because the theme is a module.

```bash
hugo mod download          # first run only
hugo server --port 1313
```

A production build:

```bash
hugo --minify --gc --baseURL "https://otter.rainoffallingstar.com/"
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

## Localisation

Three locales ship: `en`, `zh-cn`, `zh-tw`. `data/home/*.yaml` holds one file per
language with identical keys; `zh-tw` is generated from `zh-cn` with OpenCC (`s2twp`)
and then corrected by hand where the conversion is wrong for this domain (for example
`質量` → `品質`, `校驗` → `驗證`). Partials decide "is Chinese" with
`hasPrefix $lang "zh"`, so a fourth Chinese locale would need no template change.

The manual under `content/docs/manual/` is synced from `otterlab-bio/otter:docs/manual`
and translated in full: nine chapters, each in `en`, `zh-cn`, and `zh-tw`. Translation
keeps code blocks, inline code, URLs, and table structure byte-identical to the English
source.

`zh-cn` is translated by hand. `zh-tw` is generated from `zh-cn` by
`scripts/convert-zh-tw.py`, which runs OpenCC (`s2twp`) and then applies the glossary
that keeps the manual on the same terms as `data/home/zh-tw.yaml`. The glossary
records Taiwan technical usage rather than mainland equivalents: `釋出` not `發佈`,
`執行` not `運行`, `運算子` not `運算元` (operand) or `算子`, `基因體` not `基因組`,
`轉錄體` not `轉錄組`, `定序` not `測序`, `品管` not `質控`, `建置` not `構建` for a
software build, `二進位` not `二進位制`, `設定` not `配置`, `註解` not `註釋`. A
software build is `建置` but constructing a matrix is `建構`, so those phrases are
shielded before the build rule runs.

Documentation is `文檔` and a file is `檔案`: OpenCC renders both `文档` and `文件`
as `文件`, so `文档` is shielded before conversion, which keeps the two words apart. Code spans, fenced
blocks, and URLs are shielded before conversion, because the manual documents literal
column aliases such as `样本编号` that must stay Simplified to keep matching the
parser. After editing a `zh-cn` chapter, regenerate its `zh-tw` sibling and run

```bash
python3 scripts/convert-zh-tw.py --check content/docs/manual/*.zh-tw.md
```

which fails if a Simplified character survives outside code. Any future edit to the
English chapter must be mirrored in `zh-cn` first.

## Benchmark data

`data/benchmark.yaml` is generated, not typed. It holds the per-fraction means from
`docs/benchmarks/xengsort-gradient-2026-11-24/results/per-fraction-mean-sd.csv` in the
manuscript repository, and the comparison basis matches the manuscript: OTTER is the
`modern` method; RNA-seq uses Xengsort's `xengsort_graft` output checked against STAR,
and RRBS uses `bismark_replay` checked against Bismark. Regenerate the file when the
archive changes.

## Warm palette

The surfaces, inks, and accents were designed in review and are defined once in the
`:root` and `html.dark` blocks of `assets/css/custom.css`. Light mode uses rag paper
`#f7f0e5`, sand `#ede3d2`, and ivory cards `#fdfaf4`; dark mode uses warm umber-charcoal
`#171310` / `#27201a` rather than a blue-black. The accent is mineral ink-teal
`#0e515e` (light) and `#6fc0cc` (dark), and the ochre highlight `#8f5127` / `#d99d68`
comes from the otter fur in the logo. Every foreground pair was measured at or above
5.50:1 against the page background.

Two rules follow from that review: the ochre is used only for small type (the hero's
second line and the four numerals), never as a large fill, so it does not compete with
the brown in the logo; and dark cards always keep a 1px `--ot-line` border, because the
three dark surfaces are close enough to merge on an uncalibrated display.

## Layout notes

- The header is fixed and full width on every page. Three theme defaults had to go:
  the `<header>` wrapper box (set to `display: contents` so the bar can stick for
  the whole document), the `100vh` body height (`min-height: 100svh` instead), and
  the centred `max-width` body column. That last one mattered: with the body still
  constrained, the bar's background spanned only the 7xl column on pages without a
  hero, so it looked like a narrow block instead of a full-width bar. Each page now
  constrains its own text with `.ot-wrap` instead.
- The footer is a single left-aligned column, not the theme's two-column layout.
- Documentation pages use a two-column layout: text at a 46rem measure on the left,
  the manual's chapter list sticky on the right, and previous/next pager links at
  the end of each chapter. Wide tables scroll inside their own box.
- The assay section states RRBS, WGBS, and RNA-seq with their PDX/CDX variants as
  separate cards, because the xenograft pairing is the point.

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
| Languages | three locales built; the header menu lists all three |
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
