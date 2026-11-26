# OTTER homepage

The public site for **OTTER** and the `otterlab-bio` organisation, built with
Hugo and the [Blowfish](https://blowfish.page/) theme and deployed to GitHub
Pages. The design rationale, the reference-site measurements, and the copy
rules live in [`DESIGN.md`](./DESIGN.md).

- Live target: `https://otterlab-bio.github.io/`
- Languages: English at `/`, Simplified Chinese at `/zh-cn/`
- Theme: `github.com/nunocoracao/blowfish/v3` v3.11.0, consumed as a Hugo Module

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

## Deployment

`.github/workflows/pages.yml` builds on every push to `main` and publishes with
`actions/deploy-pages`. One repository setting is required before the first
deploy: **Settings → Pages → Build and deployment → Source: GitHub Actions**.

## Verified in this repository

| Check | Result |
| :--- | :--- |
| Production build | `hugo --minify --gc --panicOnWarning` exits 0 |
| Lighthouse, mobile, simulated throttling | performance 99, accessibility 100, best practices 100, SEO 100 |
| Largest contentful paint | 1.9 s |
| Cumulative layout shift | 0 |
| Horizontal overflow | none at 320, 390, 768, 1024, 1440, 1920 px |
| Text contrast (WCAG AA) | every inspected pair passes, light and dark |
| Tabs | keyboard-focusable, `aria-selected` toggles, panels hide correctly |
| Reduced motion | `prefers-reduced-motion: reduce` disables rise, reveal, hover lift |
| Em dashes in rendered text | 0 |
| Missing assets or 4xx | none across `/`, `/zh-cn/`, `/docs/`, `/zh-cn/docs/` |
| Heading order | h1 → h2 → h3, no skipped level |
| Bilingual key parity | 163 keys in each locale, identical for values that must not be translated |
