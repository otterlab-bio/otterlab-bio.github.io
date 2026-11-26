# Design review: gemini-frontend-design

Skill: [`google-gemini/demolab` → `gemini-frontend-design`](https://github.com/google-gemini/demolab/tree/main/skills/gemini-frontend-design) v1.0.0, Apache-2.0.
Installed with `npx skills add google-gemini/demolab --skill gemini-frontend-design` into
`.agents/skills/gemini-frontend-design`, pinned in `skills-lock.json` at commit `cd0c1f8`.

The review was measured, not eyeballed: every row below was read out of the rendered
DOM with Playwright at 1440×900 and 390×844, before and after the changes.

## Findings and fixes

| # | Rule | Measured before | Change |
| :--- | :--- | :--- | :--- |
| 1 | Sections start with `<h1>`/`<h2>`, no eyebrow or kicker | 5 `.ot-kicker` labels above every `<h2>`, plus a hero eyebrow | Kickers deleted; all six sections now begin with `<h2>` |
| 2 | No decorative non-interactive chips or badges | `.ot-pill` "Open source", three `.ot-tag` backend pills, seven operator pills | Pills deleted. The eyebrow is gone, backend values became plain monospace text, and operators became one dotted line |
| 3 | Hero supporting copy ≤ 25 words | 34 words | 21 words |
| 4 | No KPI or spec strip at the foot of the hero | `.ot-hero-meta`: "MIT licensed · Linux and macOS · amd64 and arm64" | Removed from the hero; the same facts moved into the quick-start points and the footer line |
| 5 | At most 3 body type sizes | 19 distinct sizes (10.9 to 78.4 px) | Two body sizes (16 px, 14 px). Hero, `<h2>`, and the four numerals share the display scale, which the skill exempts |
| 6 | No text below 13 px above the fold | 22 elements at 10.9 to 12.5 px | 0 |
| 7 | Brand wordmark visibly stronger than menu links | 16 px / 500 vs nav 14 px / 500 | 22 px / 700 serif vs nav 14 px / 500 |
| 8 | At most one primary CTA per section | Two side-by-side bordered buttons in the hero | One button; the source link is now a text link with an arrow |
| 9 | Header borderless at `y = 0`, separated once scrolled | Floating capsule with border and shadow at rest | Transparent at rest; border, shadow, and translucent blur appear after 24 px of scroll |
| 10 | No decorative numbering | `.ot-order` 01/02/03 | Removed (the phase sequence is real, but the numbers added noise, not meaning) |
| 11 | Generic three-column card rows below the hero | 3-up card grid with rounded bordered boxes | Replaced with hairline-separated rows in two columns |
| 12 | `transition: all` and idle bobbing | none | unchanged, already compliant |

## Structural change worth naming

The card grid was the page's biggest tell. Five rounded boxes with an icon, a bold
title, and two lines of prose is the default template shape the skill calls out. They
are now a two-column list of dividers, read in column order, with no boxes at all. The
evaluation numerals follow the same hairline logic and sit at the section heading's
size, so the numbers read as data rather than as decoration.

## What was kept and why

| Decision | Reason |
| :--- | :--- |
| Two font families plus mono | The mono stack only appears in the terminal panel and code blocks, which the skill exempts for code and terminal tools |
| Terminal panel in the hero | The skill asks for a wide tactile stage above the fold rather than a photograph. The panel carries real `otter build` output from `cmd/build.go` |
| Deep-sea blue and river cyan | The skill warns against defaulting to beige-and-rust or slate-and-neon. This palette is taken from the project's own mark |
| Paper-tone background | It matches the manuscript's typeset pages and keeps the site distinct from the reference layout's warm cream |

## Re-verified after the change

| Check | Result (en and zh) |
| :--- | :--- |
| Body type sizes | 16 px and 14 px |
| Text under 13 px above the fold | 0 |
| Kicker, pill, or tag elements | 0 |
| Section first children | `h2, h2, h2, h2, h2, h2` |
| Hero buttons | 1 |
| Horizontal overflow, 320 to 1920 px | 0 |
| Em dashes and spaced en dashes in copy | 0 |
| Contrast, light and dark | every inspected pair at or above WCAG AA |
| Tab panel, keyboard focus, reduced motion | working, and reveal elements stay visible under `prefers-reduced-motion` |
| Missing assets or 4xx | 0 |
