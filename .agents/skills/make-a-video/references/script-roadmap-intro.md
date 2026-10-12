# Script rule: open with a roadmap

**Applies to:** every narration script or transcript you write, draft, outline or plan for an explainer, tutorial, walkthrough or any video with chapters, and to any video that involves code. This is a standing preference from the channel owner. Don't skip it.

**Scale it:** long-form (over ~90s) gets the full roadmap below. Shorts and reels get a single preview sentence, and **shorts cut from a long video point to that full video instead of GitHub** ("Watch the full video, linked below", with the long video set as the short's Related video). Pure promo/ad spots (15–60s, hook → proof → CTA) skip the chapter list but still mention the GitHub code if there is any.

## What the intro must do (before chapter 1)

1. **Say what we're doing, and why.** One or two sentences: what we're building or explaining, and what the viewer will be able to do afterwards.
2. **Walk through the process: name every chapter, in order.** Tell the viewer exactly what's coming, e.g.:
   > "First, we'll look at the architecture. Then we'll go through the design. And finally, we'll walk through the code."

   - Use the **same chapter names** the video shows on screen (chapter cards / kickers), so the roadmap and the chapters match word for word.
   - Mention every chapter (group small ones if there are more than ~6: "then a few quick chapters on sessions and hand-offs").
3. **If there's code: say it's on GitHub.** In the intro, not only at the end:
   > "All the code is on GitHub. The link is in the description, so you can follow along or try it yourself."

   If the repo is runnable and has a README, say so ("it's fully working, and the README walks you through setup").

Keep the whole intro to **about 20–40 seconds** of narration for long-form.

## Point to videos that already exist, without breaking the flow

Continuity comes first. A viewer who gets pulled toward another video mid-explanation loses the thread.

- **Keep the intro focused.** Besides the roadmap and GitHub, mention only the previous part of a series, as the bridge into this one (e.g. "Part 2 picks up where Part 1 left off"). Don't list other videos in the intro.
- **Mid-video plugs: one short sentence, then straight back to the topic.** For example: "I show the full Gemini setup step by step in my agent-from-scratch video, link in the description." The next line returns to the current point.
- **Collect the "go deeper" references in the outro.** That's where to name the related videos or a playlist's parts, and to say once that all the links are in the description.
- Never write "in the next video" or "coming soon" for a topic the channel already covers. Check what's published, say the video exists, and point to the description. Put a matching "link in description" card on screen.

## Code demos: cue every step

When the speaker demos code live while reading the script, every demo step needs a stage-direction note under the line it goes with, so the teleprompter shows what to do:

- `> [VS Code] DEMO 1 START. Open demos/<file>.py` at the hand-off line ("I'm switching over to VS Code").
- `> [VS Code] Highlight lines 26-33: <what they are>` for each part of the code the narration explains, with **exact line numbers** checked against the file.
- `> [Terminal] Run: python <file>.py` for each run, plus what to point at in the output (`[Claude asks] ...`).
- `> ... DEMO 1 END` and a cue for returning to camera.

**Camera-only recording (code shown as graphics).** When the speaker records only camera and voice and the code is built as motion graphics afterwards, write no keyboard actions. Narration goes to camera ("Let's try it. Here's the code." rather than "I'm switching to VS Code. This is live."), and each step becomes a `> SCREEN:` note for the editor: the file, exact lines to highlight, the terminal command and which output line to highlight. Build the editor and terminal from the real source files and real run output, not screenshots or invented output.

Write the narration as a walk-through of the code itself (what this line does, why it matters), not "look at the code". When a later chapter explains something the demo already showed (e.g. "this loop is the harness"), add a short code callback with its own cues. Re-check the line numbers whenever the demo files change, and give the user a run sheet: each demo's file, lines, commands, and where it sits in the script.

## Pair it with a visual

Put an **agenda / roadmap card** on screen while the roadmap is spoken: every chapter listed, each lighting up as it's named, plus a small "code on GitHub · link in description" badge when there's code. Later chapter cards can call back to it (the current chapter highlighted), which gives viewers a sense of progress.

## When you plan or present a script

- In the plan you show the user, list the intro/roadmap **first**, with the chapter list, before the chapter-by-chapter breakdown.
- Before handing over a script, check:
  - [ ] The intro states what we're doing and why
  - [ ] Every chapter is named in order, matching the on-screen chapter titles
  - [ ] If code is involved: GitHub + "link in the description" is mentioned in the intro
  - [ ] The roadmap has a matching on-screen agenda beat
  - [ ] The intro mentions no other videos (except the previous part of a series)
  - [ ] Mid-video plugs are one sentence and return to the topic; related videos are collected in the outro
  - [ ] Follow-up topics that already have videos are referenced as "link in the description", not "next video"
  - [ ] Every live code step has a `[VS Code]` / `[Terminal]` cue with exact file, lines, and command

## Example (from "Agent with Sub-Agents")

> In the last video, we built one AI agent. Today we'll build an agent that has sub-agents: a small team of agents that work together, using Google's Agent Development Kit.
> Here's the plan. First, a quick refresher on what an agent is, and what a session is. Then we'll look at the problem with one big agent, and how sub-agents fix it. Next, we'll see how control moves between agents, and follow a real customer through the whole architecture. Finally, we'll walk through the code, line by line.
> All the code is on GitHub. The link is in the description, and it's fully working, with a README that walks you through setup.
