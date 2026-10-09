# DESIGN — AI MCP Shorts

## Style Prompt

Dark-tech explainer aesthetic: black/navy canvas, chrome-gradient headline type with halo glow, faint cyan grid + drifting particles for depth. Diagrams read as evidence (nodes, connectors, code) not decoration. Palette is symbolic — red marks what's broken, teal/blue marks the MCP solution, green marks success. No brand lock-in (generic engineering-explainer, not AIS-branded).

## Colors

| Role | Hex | Usage |
|---|---|---|
| Canvas | `#07121c` | Background navy-black (matches workspace's proven non-banding dark) |
| Accent / solution | `#37bdf8` | MCP, "decoupled", grid lines, particles, active caption word |
| Problem / broken | `#e10b1f` | UNSCALABLE, NO CONTEXT, BRITTLE tags; glitch/shatter accents |
| Success | `#22c55e` | Checkmarks (Decoupled / Dynamic / Extensible) |
| Chrome text | `linear-gradient(180deg, #ffffff 0%, #999999 60%, #cccccc 100%)` | All headline/badge type — background-clip: text |
| Body / dim | `#96a2b6` | Secondary labels, dimmed caption words |

5 active hues total (navy canvas, chrome white-gray, teal, red, green) — stays within MOTION_PHILOSOPHY's ≤5 color law.

## Typography

- **Montserrat** (300/500/700/900) — headlines, badges, kinetic type, captions
- **Roboto Mono** (400/500/700) — stage badges, code-snippet overlay, mono labels

Both loaded via the same Google Fonts request used across this workspace: `family=Montserrat:wght@300;500;700;900&family=Roboto+Mono:wght@400;500;700`.

## Motion rules

- Chrome gradient + halo glow (`text-shadow: 0 0 20px rgba(255,255,255,.6), 0 0 40px rgba(255,255,255,.3)`) on every headline — no flat white
- Faint perspective/grid texture + vignette + grain present continuously (ambient-bg layer)
- Diagrams build via energy-pulse-along-path (SVG `stroke-dasharray`/`dashoffset`), not simple fades
- Stage 3's "shatters" moment gets a real glitch: chromatic-aberration pulse + line fragmenting, timed to the word onset, not the scene start
- Entrance-only per scene; transitions (face-mode change, panel crossfade) handle exits — no exit tweens mid-scene
- No `repeat: -1` anywhere; all idle/secondary motion uses finite computed repeat counts
- No `Math.random()` / `Date.now()` — static layouts, deterministic secondary motion only

## What NOT to do

- No flat `#000` — always the navy `#07121c` + grid/vignette stack
- No 6th color — if a new element needs a color, reuse one of the five above
- No hard cuts between scenes — every stage transition uses a face-mode change and/or panel crossfade
- No stamp/tag firing before its target text is visible (reveal logic > word-sync, per short-form skill lesson)
- No BOTTOM face-mode at the unscaled default — tune scale/x against the actual source framing before shipping
