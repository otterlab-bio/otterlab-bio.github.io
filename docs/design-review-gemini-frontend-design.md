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
| 13 | Body prose ≤ 65 characters per line | section leads measured 72 | 64 |
| 14 | No text collisions in the rendered page | the theme's 50%-opacity scroll-to-top glyph collided with body text on mobile | opaque surface and hairline border |
| 15 | Display hierarchy must stay legible at every width | at 320 to 480 px the hero h1 and the h2 both computed to 28 px, so the hierarchy collapsed | h1 floor raised to 2rem (32 px on mobile, 80 px on desktop), h2 floor lowered to 1.5rem |
| 16 | Multi-column lists must not split a paragraph | Chrome's multicolumn split the Chinese methx description across columns and broke two CTA labels mid-phrase | row-major two-column grid, and unbreakable link labels |

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

## Second pass: the skill's own audit of the live site

After the first round, the installed skill was run against the deployed pages by
Antigravity (`gemini-4-hydrogen-high`, workspace mode). It returned 12 findings. Each
was re-measured here before acting; two were already stale because they described the
pre-fix build.

Confirmed and fixed:

| Finding | Measured evidence | Fix |
| :--- | :--- | :--- |
| `.ot-reveal` left six sections at `opacity: 0` with JavaScript disabled | Playwright with `javaScriptEnabled: false` returned `0` for all six | The hidden start state is scoped to `html.ot-js`, set by an inline probe in `extend-head`; with JS off the measured opacity is `1` |
| Hero did not start at `y = 0`; the theme's 128 px spacer and a live `blur(24px)` sat behind it | `heroTop: 128`, `backdropFilter: blur(24px)` at rest | Spacer hidden on the home page, hero starts at `0`, backdrop is `none` until scrolled |
| `.ot-metrics` stayed two columns under 900 px | each cell measured 147 px wide, 112 px at 320 px | Included in the single-column rule; mobile cell is now 342 px |
| Hero `<h1>` collapsed to 28 px on mobile | identical to `<h2>` at 390 px | Floor raised; h1 is 32 px and h2 24 px at 390 px |
| The Chinese Colab tab linked to the English notebook | the page contained both URLs | A `quick.colabUrl` key per language, wired into the tab partial |
| A second hero action competed with the primary button | two controls in `.ot-hero-actions` | One button; the source link lives in the header nav and the component list |
| A fourth type size on the scroll control | `20px` on `#scroll-to-top a` | Set to the body step |
| Touch targets under 44 px and missing focus rings | button 43 px, link 28 px | 44 px minimum below 900 px, and `:focus-visible` rings on all interactive elements |
| Dark skip link at 1.95:1 | `rgb(92,151,186)` on `rgb(107,95,82)` | Page surface and ink tokens; measured 9.44:1 |
| Orphan cell in the five-item grid | item 3 left a dangling border | Final item spans both columns |
| Decorative traffic lights and a CSS-generated middot | `.ot-dot` had no function; `.name::after` injected text | Lights removed; the language is a real `<span>` |
| `prefers-reduced-motion` missed the arrow nudge and smooth scrolling | `.ot-hero-link:hover svg` still translated | Both suppressed |

Two findings were stale, describing the build before the first round: the missing
`.ot-metrics` media query and the 28 px mobile `<h1>`. Both were re-measured after the
fix and now read 342 px and 32 px.

One suggestion was declined: rewording "Four compiled layers" and "Twelve repositories"
into benefit-led headings. Those two counts are the page's actual subject, and the
numbers are checkable against the release; a benefit-led paraphrase would be less
informative.

## Re-verified after the change

| Check | Result (en and zh) |
| :--- | :--- |
| Body type sizes | 16 px and 14 px, plus the exempt display scale |
| Text under 13 px above the fold | 0 |
| Kicker, pill, or tag elements | 0 |
| Section first children | `h2, h2, h2, h2, h2, h2` |
| Hero buttons | 1 |
| Horizontal overflow, 320 to 1920 px | 0 |
| Em dashes and spaced en dashes in copy | 0 |
| Contrast, light and dark | every inspected pair at or above WCAG AA |
| Tab panel, keyboard focus, reduced motion | working, and reveal elements stay visible under `prefers-reduced-motion` |
| Missing assets or 4xx | 0 |
