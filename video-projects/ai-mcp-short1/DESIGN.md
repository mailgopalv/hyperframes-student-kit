# DESIGN — Short 1: "My AI Agent Refused to Lie to Me"

Inherits the channel's MCP series look (`video-projects/ai-mcp-16-9/DESIGN.md`) adapted to 1080×1920 vertical.

## Style Prompt

Dark-tech vertical short: navy-black canvas with a faint drifting grid, vignette and grain. The real screen recording sits in a rounded "device" panel in the middle third; a chrome-gradient beat headline above it changes with each story beat; heavy karaoke captions below. Color carries meaning: **red = refused / no data**, **cyan = the agent working correctly**, **amber = something newly added (the docs MCP server)**. Every panel cut is bridged by motion (streak, push, flash) — never a bare jump cut.

## Colors (4 active + neutrals)

| Role | Hex |
|---|---|
| Canvas | `#07121c` (radial to `#0d2233` center) |
| Core / correct / active caption word | `#37bdf8` |
| Refused / no data | `#e10b1f` (text uses `#ff4d5e` for contrast) |
| New / added | `#f5a623` |
| Body dim | `#8fa2b8` |

## Typography

- **Montserrat** 800/900 — beat headlines, captions, stamps
- **JetBrains Mono** 500/700 — panel labels, file/tool names

## Motion rules

- Beat headline: whip up + blur out, new one rises in from below with blur (0.33s / 0.5s)
- Panel cuts rotate flavors: light-streak whip → push → flash-through-white → zoom punch
- Callouts land AFTER their target is visible on screen (stamp ≥ 0.2s after the answer bubble)
- Ken Burns 1.00 → 1.03 on the panel within each segment
- Captions: 3-word groups, active word cyan + 1.08 pop

## What NOT to do

- No flat background — grid + vignette + grain always on
- No text under 36px except panel labels (28px mono)
- Never cover the answer bubble with a stamp
- No 5th accent color
