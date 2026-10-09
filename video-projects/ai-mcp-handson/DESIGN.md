# DESIGN — AI MCP Hands-on: chapter progress cards

## Style Prompt

A callback to the video's own "Where we're headed" agenda slide. The card is that slide, shrunk into a compact white panel that sits in the lower-left of the frame for ~4 seconds at each of the three part transitions (Part 02, 03, 04). Clean, editorial, calm — navy serif titles, a teal eyebrow, numbered circles, hairline dividers. It is an overlay on a live screen recording, so it must read instantly and never compete with the code: small footprint, no background texture, no glow. The one piece of storytelling motion is **progress moving forward** — the highlight slides from the previous part to the current one, and the finished part's number turns into a check.

This deliberately does not use the workspace dark/chrome aesthetic: the brand brief here is the source slide deck. The MOTION_PHILOSOPHY discipline still applies (one idea per beat, motion-blurred entry/exit, a callback, frame-snapped timings).

## Colors (4 active)

| Role | Hex | Usage |
|---|---|---|
| Card | `#ffffff` | Panel background (matches the slide) |
| Navy | `#0f2447` | Titles, numbered circles for upcoming parts |
| Teal | `#1f6f94` | Eyebrow, current-part circle + highlight, completed checks |
| Slate | `#5b6675` | Descriptions, dimmed titles; dividers use `#dde3ea` |

## Typography

- **Source Serif 4** 700 — part titles (the slide's bold serif voice)
- **IBM Plex Sans** 400/600/700 — eyebrow (tracked caps), descriptions, circle numerals (tabular)

## Motion rules

- Entry: card slides in from the left edge with a horizontal blur that resolves (0.5s, expo.out)
- Rows stagger in (0.06s), then the teal highlight travels from the previous part to the current one (power3.inOut)
- Previous part's numeral swaps to a check; current circle recolors navy → teal with a small back.out settle
- Exit: slide left with blur (0.37s, power2.in) — the overlay must leave cleanly, it is not a scene cut
- All tween boundaries snap to 1/30s

## What NOT to do

- No full-screen takeover — the lesson content stays visible
- No dark/chrome/grain treatment — it must look like the slide deck viewers already saw
- No 5th color, no gradients
- No text under 20px (video legibility at 1440p)
- Never hold longer than ~4s — it is a signpost, not a slide
