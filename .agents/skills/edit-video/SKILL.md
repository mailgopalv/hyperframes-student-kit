---
name: edit-video
description: Edit a raw talking-head video through transcription, silence trimming, mistake review, visual storytelling, motion graphics, and verified HyperFrames rendering. Use for a complete edit; route a single requested operation directly to its specialist skill.
---

# Edit a video

Keep each project in `video-projects/<slug>/`, preserving the source recording.
Read the workspace guide and the project's brief or DESIGN.md. If a direction is
missing, propose a style from `style-library/registry.json` based on the footage.

1. Inspect duration, streams, resolution, frame rate (count frames for VFR
   recordings), and loudness. Flag low fps or quiet audio before more takes are
   recorded. Copy the source into the project's assets or reference an explicitly
   provided local path.
2. Read `docs/TOOLS-AND-API-KEYS.md` before service setup. Reuse a matching word
   transcript. Otherwise use the student's chosen provider; Nate defaults to
   `node scripts/transcribe-elevenlabs.mjs <source>`. OpenAI Whisper and local
   Whisper are supported workflow alternatives after transcript normalization;
   `npx hyperframes transcribe <file> -m medium.en` runs Whisper locally for free.
   Check available credentials or local dependencies. Explain uploads and costs
   before any service call whose authorization is still missing.
3. Read `../cut-silences/SKILL.md`. With Whisper timestamps, use its audio mode
   (`cut-silences-audio.mjs`) so no cut lands inside a word. Produce an EDL, render
   the silence pass when editing is authorized, and re-transcribe the cut.
4. Read `../cut-mistakes/SKILL.md`. Inspect candidates in context and preserve
   intentional emphasis. Record the reviewed cuts. If no mistakes need cutting,
   carry forward the silence output. Match every transcript to its actual video.
5. Review the first 30 seconds against
   `../make-a-video/references/script-roadmap-intro.md`: the hook comes first,
   with no greeting, logo sting or "in the last video". Propose cuts or a
   reorder, and a ~5s preview of the demo pulled into the 10–20s slot when the
   footage allows; flag a demo that lands after the first third.
   Read `../video-storytelling/SKILL.md` for the visual arc and
   `../hyperframes-video-beats/SKILL.md` for overlays. Write a beat sheet with
   transcript anchors, one visual idea per beat, and deliberate callbacks.
6. Read `MOTION_PHILOSOPHY.md`, `../hyperframes/SKILL.md`, and relevant GSAP
   references before authoring. Use `../style-library/SKILL.md` to select or
   adapt a card. Localize every asset used by the composition.
7. Run preflight and HyperFrames lint from the project, plus the transcript-sync
   validator for anchored sub-compositions. Review Studio before the draft.
8. Render a draft, inspect encoded frames and transitions, and listen across cut
   boundaries. Check face framing, text legibility, black frames, and A/V sync.
   Resolve failures before the final render. Follow any review approvals already
   provided; do not repeat approval requests for the same authorized action.
   Never start another render (a new draft or the final) on your own: after QA,
   report findings and prepared fixes, then stop and wait for approval.

Read `references/production-lessons.md` before building: camera sub-composition,
transform-only camera moves, banners that never appear empty, SVG rotation,
loudness, render settings and draft QA all come from a shipped edit.

Deliver the final MP4 path, edit decisions, retimed transcript, composition,
and `VERIFY.md` describing what was checked and any remaining limitations.
For a YouTube upload, prepare `publish/YOUTUBE.md` (3 titles, 2–3 thumbnail
briefs, chapters from the final render, Shorts ideas) with
`../youtube-packaging/SKILL.md` and its pre-publish checklist.
An automated detector proposes edits; editorial judgment remains necessary.
