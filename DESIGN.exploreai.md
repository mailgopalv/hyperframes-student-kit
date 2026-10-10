# ExploreAI with Gopal — Visual Identity

Ground truth extracted from `assets/exploreai-brand-guidelines.png` and `assets/exploreai-logo.png`. Every branded composition MUST trace its palette, typography, and motion choices back to this file. Tokens live in `assets/brand-token.css`.

Tagline: **EXPLORE · LEARN · BUILD · GROW WITH AI**

## Style Prompt

ExploreAI is a friendly, optimistic AI-education brand — "a bright classroom for future AI engineers." Compositions should feel clear, welcoming, and curious: light airy canvases with soft blue-to-violet washes, crisp navy headlines, rounded cards with gentle shadows, and a cyan → blue → violet gradient reserved for emphasis. Approachable, never childish. Clean, never sterile. The mood is clarity, momentum, and "you can build this too."

## Colors

| Token | Hex | Role |
|---|---|---|
| `--color-brand-primary` | `#3B82F6` | Primary Blue — trust, technology, clarity. Main accent, highlights, CTAs |
| `--color-brand-violet` | `#8B5CF6` | Violet — AI, creativity, innovation. Second accent, gradient end |
| `--color-brand-teal` | `#06B6D4` | Teal — learning, growth, exploration. Gradient start, "solution" beats |
| `--color-brand-coral` | `#F97316` | Coral — energy, highlights, action. Sparkles, warnings, one-word pops |
| `--color-brand-lime` | `#84CC16` | Lime — progress, success, positivity. Checkmarks, "done" states |
| `--color-text-primary` | `#0F172A` | Navy — main text and headings |
| `--color-text-secondary` | `#475569` | Slate — secondary text |
| `--color-text-muted` / Cool Grey | `#64748B` / `#94A3B8` | Meta text; borders and icons |
| `--color-surface-blue` / Light Blue | `#EFF6FF` / `#E0F2FE` | Section backgrounds |
| `--color-surface-violet` | `#F5F3FF` | Soft Lavender — surfaces and cards |
| `--color-background` | `#FFFFFF` | Base canvas |

Gradients (use sparingly, for emphasis):

- `--gradient-brand` — `#06B6D4 → #3B82F6 → #8B5CF6` at 110°. The "AI" in the wordmark, hero words, progress bars.
- `--gradient-brand-soft` — pale teal → blue → lavender. Section washes behind cards.
- `--gradient-primary-button` — `#3B82F6 → #6366F1`. Primary buttons.

Dark variant (`.theme-dark` in `brand-token.css`): canvas `#0B1220`, surface `#111827`, text `#F8FAFC`. Use for dark logo placements, code demos, and terminal scenes; keep the same accents.

## Typography

- **Poppins (Bold 700)** — headings, titles, key text, big numbers. Ships locally in `assets/fonts/` (weights 500–800, loaded by `brand-token.css`); never link Google Fonts for it.
- **Inter (Regular 400 / Medium 500)** — body text, descriptions, labels, UI text, captions. Bundled with HyperFrames; just name it in `font-family`.
- Mono (`--font-family-mono`) — code, terminal lines, file names only.

Poppins headline over Inter supporting line is the house pattern. Letter-spaced uppercase Inter (0.2em) for small eyebrow labels like the tagline.

## Logo

- File: `assets/exploreai-logo.png` — gradient circuit-brain icon with coral/violet sparkles, navy "Explore" + gradient "AI" wordmark, "with Gopal" subline, inside a rounded glass tile.
- Variations: Primary (white), Dark Background (navy tile, white wordmark), Gradient Background (soft brand wash).
- Clearspace: keep clear space equal to the height of the brain icon (X) on all sides.
- Never recolor, stretch, or add glows/effects beyond the provided art.

## Background

- File: `assets/exploreai-background.png` (1672×941, 16:9) — soft white canvas with a sky-blue bloom top-left and violet bloom bottom-right, small "Explore AI" wordmark top-right.
- Use as the default full-frame plate for 16:9 explainer scenes. Keep content clear of the top-right wordmark. If you add the full logo elsewhere in the frame, cover or crop the corner wordmark so the brand never appears twice.
- For 9:16, use `object-fit: cover` centered and check the wordmark is cropped cleanly, or rebuild the wash with `--gradient-brand-soft` plus two radial blooms.

## Shape, Depth, Iconography

- Radii: cards `--radius-lg` (16px) to `--radius-xl` (24px); buttons and chips `--radius-pill`.
- Shadows: `--shadow-md` for cards, `--shadow-lg` for the one hero card. No hard black shadows.
- Icons: rounded line icons, ~2px stroke, colored with one brand hue, sitting on a matching pale tile (`--color-surface-blue`, `--color-surface-violet`, `--color-surface-teal`, or pale coral/lime). Graduation cap, play, code `</>`, document, lightbulb, gear, robot, chart, cloud, people.

## Buttons

- **Primary:** pill, `--gradient-brand` (teal → violet) fill, white Inter Semibold text, arrow `→`. Example: `[ Watch Now → ]`
- **Secondary:** pill, white fill, 2px `--color-brand-primary` border, blue text, arrow `→`. Example: `[ Explore More → ]`

## Motion Rules

- **Entrance only** (per HyperFrames skill rule): elements animate in; scene transitions handle exits.
- **Easing palette:** `power3.out`, `expo.out`, `back.out(1.4)` (friendly pops for icons/sparkles), `power2.inOut` for camera moves, `sine.inOut` for ambient drift of background blooms.
- **Use at least 3 different eases per scene.**
- **Duration bands:** snap entrances 0.3–0.5s, headline entrances 0.5–0.8s, ambient drifts 3–6s.
- **Offset first animation** 0.1–0.3s from scene start.
- **Text stagger:** 0.12–0.18s per word for headlines. Educational pacing — give each idea room to land.
- **Numbers:** GSAP `{innerText: N, snap: {innerText: 1}}` count-up with `font-variant-numeric: tabular-nums`.
- **Sparkles:** small coral/violet four-point stars may twinkle (finite repeats) near the hero element — the brand's signature accent motion.

## What NOT to Do

1. **No dark, moody control-room canvases** as the default — the brand is light-first. Dark variant only where content calls for it (code, terminal).
2. **No gradient on everything.** The brand gradient marks emphasis: one hero word, one button, one progress bar per scene.
3. **No more than 5 active hues per scene**, each with a meaning (blue = tech, violet = AI, teal = learning, coral = action, lime = success).
4. **No fonts outside Poppins + Inter** (plus mono for code).
5. **No `transparent` keyword in gradients** — use `rgba(255,255,255,0)` or the matching color at 0 alpha.
6. **No `Math.random()` or `Date.now()`** — render determinism. Use a seeded PRNG.
7. **No stretching or recoloring the logo.** Respect clearspace.
8. **No low-contrast text on the background blooms** — keep body text navy `#0F172A` or slate `#475569` on light areas, and test readability over the blue/violet corners.

## File References

- `assets/exploreai-logo.png` — official logo tile
- `assets/exploreai-background.png` — default 16:9 background plate
- `assets/exploreai-brand-guidelines.png` — the one-pager these specs came from
- `assets/brand-token.css` — CSS design tokens and Poppins `@font-face` rules, imported by every branded composition
- `assets/fonts/` — local Poppins woff2 files (SIL OFL, `licenses/POPPINS-OFL.txt`)
- `assets/old/` — archived AI Automation Society (AIS) brand assets; do not use for new work
