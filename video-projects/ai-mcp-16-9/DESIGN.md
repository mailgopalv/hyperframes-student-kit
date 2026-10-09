# DESIGN — What is MCP? (Support Agent Walkthrough)

## Style Prompt

Dark-tech explainer aesthetic per workspace `MOTION_PHILOSOPHY.md`: navy-black canvas, faint perspective grid + crosshair registration marks, vignette + grain on every scene, chrome-gradient type with halo glow on every headline. Unlike a 30s brand spot, this is a ~20-minute narrated technical walkthrough — beats hold as long as the narration needs them to, but every beat still has continuous camera drift, entrance motion, and whip/morph transitions between scenes. No hard cuts, no static frames.

The core storytelling device: the **Support Agent system diagram is one persistent object that evolves**, not a deck of unrelated slides. The same agent box, LLM box, and API boxes carry through v1 → v2 → v3, with new nodes sliding in and connecting live rather than the diagram being redrawn from scratch. This is the literal MOTION_PHILOSOPHY Law #6 (object metaphors carry meaning / same object returns) applied to a technical diagram instead of a product shot.

## Colors (5 active hues, matches MOTION_PHILOSOPHY's ≤5-color law)

| Role | Hex | Usage |
|---|---|---|
| Canvas | `#07121c` | Background navy-black (never flat `#000`) |
| Chrome text | `linear-gradient(180deg, #ffffff 0%, #999999 60%, #cccccc 100%)` | All headline/section-title type — `background-clip: text` |
| Core / agent / solution | `#37bdf8` (bright) / `#1c6f96` (dim) | Support Agent box, LLM box, connectors, MCP later on |
| Problem / broken / drawback | `#e10b1f` | Tight-coupling lines, "doesn't scale", failure states |
| New / attention | `#f5a623` | Newly-added API box on arrival, highlighted code/flow callouts (matches the source deck's own amber highlight convention) |

Body/dim text: `#8fa2b8` (desaturated blue-gray, reads on navy). No 6th color — reuse one of the five above.

## Typography

- **Montserrat** (400/600/700/900) — headlines, section titles, diagram labels, captions
- **JetBrains Mono** (400/500/700) — API names, JSON/code snippets, stage badges (the source recording shows real JSON request/response bodies — keep those authentically monospaced)

Load: `family=Montserrat:wght@400;600;700;900&family=JetBrains+Mono:wght@400;500;700`

## Motion rules

- Chrome gradient + halo glow (`text-shadow: 0 0 20px rgba(255,255,255,.6), 0 0 40px rgba(255,255,255,.3)`) on every headline/section title — no flat white
- Perspective grid + crosshairs + vignette + grain present continuously via a shared `ambient-bg` composition
- Diagram connectors draw on via SVG `stroke-dasharray`/`dashoffset` (energy-pulse-along-path), not instant fades
- New nodes arrive with a slide-in + amber highlight pulse that settles to the core teal — same move every time a capability is added, so the viewer learns the visual grammar
- Entrance-only within a beat; scene-to-scene handoffs are whip-streak or blur-cut transitions per MOTION_PHILOSOPHY 2.5 — never a hard jump cut
- No `repeat: -1` — all idle motion (grid drift, particle twinkle, vignette breathe) uses finite computed repeat counts sized to the beat's duration
- No `Math.random()` / `Date.now()` — deterministic harmonic-hash values for any "randomized" particle placement

## What NOT to do

- No flat `#000` — always `#07121c` + grid/vignette stack
- No 6th color
- No hard cuts between beats — every transition is a whip-streak, blur-cut, or the color-recolor trick
- No redrawing the agent/LLM/API diagram from scratch between v1/v2/v3 — it must visibly be the same object gaining nodes
- No exit tweens mid-beat (per hyperframes skill) — transitions own the exit, entrances own the arrival
