# DESIGN — Agent with Sub-Agents (Google ADK E-commerce)

## Style Prompt

Continues the "What is MCP?" series look (`../ai-mcp-16-9/DESIGN.md`): navy-black canvas, faint drifting grid + crosshair registration marks, vignette + grain on every beat, chrome-gradient headlines with halo glow. A ~2-minute beginner explainer meant to be narrated over, so beats hold for narration, but every beat keeps ambient drift and every seam is a whip-streak.

Core storytelling device: **the agent box is one persistent object.** The single overloaded "E-commerce Agent" in the problem beat becomes the root agent, handing its tool chips down to three sub-agents. The same root + three-child tree returns in the architecture walkthrough and, shrunk, in the outro (callback). A white "hand-off pulse" travels between agents every time `transfer_to_agent` fires, which is the one visual grammar viewers learn.

## Colors (4 hues + chrome)

| Role | Hex | Meaning |
|---|---|---|
| Canvas | `#07121c` | Background (never flat `#000`) |
| Chrome text | `linear-gradient(180deg, #ffffff 0%, #999999 60%, #cccccc 100%)` | All headlines |
| Agent | `#37bdf8` / dim `#1c6f96` | Every agent box, connectors, the active-agent glow |
| Session state | `#f5a623` | The shared `session.state` bar, state keys/values, highlighted code lines |
| Problem | `#e10b1f` | Only the overloaded single agent |
| Hand-off | `#ffffff` glow | The transfer pulse |

Body / dim text: `#8fa2b8`.

## Typography

- **Montserrat** 400/700/900 for headlines, labels, chat bubbles
- **JetBrains Mono** 400/500/700 for code, tool names, state keys, kickers

## Motion rules

- Chrome + halo on every headline
- Connectors draw on via `stroke-dashoffset`; nodes enter with a scale/blur settle
- Hand-off = white pulse along the connector + the target box lights up (glow) while the previous one dims
- State values land with an amber flash that settles
- Whip-streak on every cut between compositions (in `index.html`)
- No `repeat: -1`; deterministic only; every timeline anchored to its slot length

## What NOT to do

- No 5th hue; per-agent differences come from labels/icons, not new colors
- No redrawing the agent tree from scratch without it reading as the same object
- No text under 20px (code 24px+)
- No hard cuts
