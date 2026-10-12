---
name: youtube-packaging
description: Package a long-form YouTube video for the Explore AI with Gopal channel - title options, thumbnail briefs and variants, description with chapters, Shorts spin-offs, and the pre-publish checklist - and log post-publish results as lessons learned. Use when writing or reviewing a script's hook, titles, thumbnails, a YouTube description or publish/YOUTUBE.md, planning Shorts from a long video, preparing an upload, or when the user shares YouTube Studio stats or post-publish feedback.
---

# YouTube packaging

The channel's production quality and teaching body already work. What decides
whether anyone sees them is the **packaging** (title + thumbnail → click-through)
and the **opening** (first 30 seconds → retention). These rules come from real
channel data; read `references/lessons-learned.md` before packaging a video and
add to it after each post-publish review.

When these rules conflict with an older instruction (a skill, a past
`publish/YOUTUBE.md`, a memory), **these rules win**. Tell the user which
instruction you overrode and why.

## What to hand over with every long-form script

A script is not finished until it comes with all of this, and passes the
checklist below:

1. The script itself, written to `../make-a-video/references/script-roadmap-intro.md`
   (hook first, demo early, depth matches the title, short CTA, chapter list).
2. **3 title options** (see Titles).
3. **2–3 thumbnail briefs** for YouTube Studio's Test & Compare (see Thumbnails).
4. **A chapter list** with timestamps for the description.
5. **2–3 Shorts ideas** (see Shorts).

At upload time, write `publish/YOUTUBE.md` in the project: the chosen title and
the alternatives, the description, the corrected chapter list, tags, and the
thumbnail variants.

## Titles

- **Front-load the hook.** The key phrase must fit in the **first ~45 characters**
  so it isn't cut off on mobile. Count the characters and show the count.
- **Never start with the series name.** Series names go in the description or a
  playlist, or at the very end of the title after the hook.
- **Provide 3 options**, one of each:
  - **Curiosity:** opens a gap ("Your AI Agent Is Doing Too Much").
  - **Search:** the exact words people type ("Google ADK Multi-Agent Tutorial
    (Python)").
  - **Problem/benefit:** names the pain or the win ("Fix an AI Agent That Picks
    the Wrong Tool").
- **Check YouTube search autocomplete** for keyword wording before choosing the
  search title: type the topic into YouTube search and note the suggestions. If
  you can't check it yourself (no browser access), list the phrases to check and
  ask the user to confirm.
- Title, thumbnail and opening line must agree on the same promise.

## Thumbnails

You write the brief; the user or an image tool makes the image. Each brief gives
the layout, the face expression, the text, the one visual, and colours from
`DESIGN.exploreai.md`.

- **Readable at phone size.** Before approving, view it at about **160px wide**
  (for example `ffmpeg -i thumb.png -vf scale=160:-1 thumb-160.png`, then look at
  the small file). If the text or the idea isn't clear at that size, redo it.
- **Max 3 words of text**, and they must **add to the title, not repeat it**.
- **One visual idea only**, e.g. a before/after contrast ("1 ❌ → team ✓").
- **Gopal's face is large**, with a clear expression that fits the idea.
- **At most one small logo**, in a corner.
- **No tool lists, bullet points or full diagrams.** A thumbnail is not a slide.
- **Every label matches the names used in the video** (if the video says
  `catalog_agent`, the thumbnail can't say "Product Agent").
- **Provide 2–3 variants** that test different ideas (different contrast, text or
  expression), not the same design in two colours.

## Description

- First 1–2 lines: the hook and the payoff, in plain words (they show in search).
- The code / repo link near the top when there's code.
- The chapter list, starting at `0:00` with the hook chapter, using the on-screen
  chapter names and times corrected from the final render.
- Earlier parts of a series and related videos go here, under a links section.
- Short subscribe line at the end; a few hashtags.

## Shorts

Plan **2–3 Shorts from every long video**. Each Short teases **one** insight
from the video, opens with its own hook, and ends by pointing to the full video
("Full video linked below", with the long video set as the Short's Related
video). List for each: the insight, the hook line, the source timestamp range,
and the on-screen payoff. Build them with `../short-form-edit/SKILL.md`.

## Pre-publish checklist (must pass before handing over)

Show this checklist, ticked, with every script, thumbnail brief and title list.
If an item fails, fix it before handing over, or say plainly why it can't pass.

- [ ] Script has no reference to a previous video in the first 30 seconds
- [ ] Hook follows pain → preview of result → promise, within 30 seconds
- [ ] No greeting, channel intro, logo sting or "in this video I'll…" before the hook
- [ ] Demo or visual payoff appears in the first third
- [ ] Depth matches the title; basics cut or linked
- [ ] Repo/code mentioned in the first 30 seconds (if applicable)
- [ ] End CTA is short (one line each) and 30 seconds or less
- [ ] Chapter list included
- [ ] Thumbnail: max 3 words, one idea, large face, readable at phone size (checked at ~160px), labels match the video
- [ ] 2–3 thumbnail variants and 3 title options provided
- [ ] Title hook fits in ~45 characters and doesn't start with a series name
- [ ] 2–3 Shorts ideas listed

## After publishing: log the lessons

When the user shares YouTube Studio stats or post-publish feedback, add a row to
`references/lessons-learned.md` (date, video, click-through rate, average view
duration, the key lesson) and a short diagnosis below the table. Read the
retention shape before concluding anything: a steep early drop then a flat line
means the opening failed and the body worked. If the lesson changes how scripts,
titles or thumbnails should be made, update this skill and
`script-roadmap-intro.md` too, then run `npm run sync:skills`.

Never invent or estimate stats. Use only the numbers the user gives you.
