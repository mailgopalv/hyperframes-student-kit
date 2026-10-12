# Script rule: hook first, then a short roadmap

**Applies to:** every narration script or transcript you write, draft, outline or plan for an explainer, tutorial, walkthrough or any video with chapters, and to any video that involves code. This is a standing preference from the channel owner (Explore AI with Gopal). Don't skip it.

**Why it changed (2026-10-12):** the "Stop Building One AI Agent" video lost viewers from ~85% to ~30% in the first 30–40 seconds, then held flat at ~20% to the end. Its intro opened with "In the last video, we built…", re-taught "What is an agent?" at 0:27, and showed the live demo only after ~2.5 minutes of theory. The body worked; the opening didn't. The old rule (roadmap first, previous-part bridge in the intro) is replaced by the rules below. Full data: `../../youtube-packaging/references/lessons-learned.md`.

**Scale it:** long-form (over ~90s) gets everything below. Shorts and reels get the hook plus a single preview sentence, and **shorts cut from a long video point to that full video instead of GitHub** ("Watch the full video, linked below", with the long video set as the short's Related video). Pure promo/ad spots (15–60s, hook → proof → CTA) skip the roadmap but still mention the GitHub code if there is any.

## The first 30 seconds: the hook

Nothing comes before the hook: **no greeting, no channel intro, no logo sting, no "in this video I'll…", no "in the last video…"**. The first spoken line is the hook.

1. **0–10s · a pain the viewer already has.** Concrete and relatable, in their words. "One agent, seven tools, and it keeps picking the wrong one."
2. **10–20s · show the end result.** A fast ~5-second preview of the finished demo or payoff (the working app, the agent team handing off, the final output). Mark it with a `> SCREEN: PREVIEW …` note naming the exact demo moment to pull forward.
3. **20–30s · the promise and the proof, then go.** "By the end you'll have a working team of agents, and the full code is on GitHub, linked in the description." Then go straight into the content.

The **repo / code link is mentioned inside these 30 seconds** whenever there's code. Repeat it later at the code chapter if useful, but never only at the end.

## Right after the hook: a short roadmap (optional, ≤10s)

If the video has several chapters, name them in **one sentence** after the hook, with the same names the chapter cards show: "We'll see the problem, build the team, then run it on a real customer." Pair it with a quick agenda card. Don't let the roadmap delay the content; the full chapter list lives in the description.

## Depth matches the title

- The title sets the level. If the title promises an advanced topic (sub-agents, multi-agent systems, MCP servers), **don't re-teach the basics**. Give a basic concept one line at most, or link to the video that teaches it: "New to agents? My agent-from-scratch video is linked."
- Never spend the first minute on "what is X?" when the viewer searched for "how to do advanced X".

## The demo comes early

Put the most visual or impressive part (the live demo, the customer walkthrough, the before/after) **in the first third of the video**, not after the theory. A good default for tutorials: problem → demo of the result → how it works → code. Theory that the demo motivates lands better after it.

## Point to videos that already exist, without breaking the flow

Continuity comes first. A viewer who gets pulled toward another video mid-explanation loses the thread.

- **Never open with a reference to a previous video**, and don't mention other videos (including the previous part of a series) in the first 30 seconds. New browse and search viewers don't have that context. Mention earlier parts later, briefly, with a link: "New to MCP? Part 1 is linked in the description."
- **Mid-video plugs: one short sentence, then straight back to the topic.** For example: "I show the full Gemini setup step by step in my agent-from-scratch video, link in the description." The next line returns to the current point.
- **Collect the "go deeper" references in the outro.** That's where to name the related videos or a playlist's parts, and to say once that all the links are in the description.
- Never write "in the next video" or "coming soon" for a topic the channel already covers. Check what's published, say the video exists, and point to the description. Put a matching "link in description" card on screen.

## The end: a short CTA

One line each for like, comment and subscribe, ideally with a specific comment prompt ("Tell me which tool your agent keeps getting wrong"). The whole CTA runs **30 seconds or less**.

## Chapter list

Every script ends with a **chapter list for the description**: `0:00 <name>` lines using the on-screen chapter names. Use estimated times in the script (word count at ~140 wpm) and correct them from the final render before upload. The first chapter is the hook ("0:00 The problem with one big agent"), not "Intro".

## Code demos: cue every step

When the speaker demos code live while reading the script, every demo step needs a stage-direction note under the line it goes with, so the teleprompter shows what to do:

- `> [VS Code] DEMO 1 START. Open demos/<file>.py` at the hand-off line ("I'm switching over to VS Code").
- `> [VS Code] Highlight lines 26-33: <what they are>` for each part of the code the narration explains, with **exact line numbers** checked against the file.
- `> [Terminal] Run: python <file>.py` for each run, plus what to point at in the output (`[Claude asks] ...`).
- `> ... DEMO 1 END` and a cue for returning to camera.

**Camera-only recording (code shown as graphics).** When the speaker records only camera and voice and the code is built as motion graphics afterwards, write no keyboard actions. Narration goes to camera ("Let's try it. Here's the code." rather than "I'm switching to VS Code. This is live."), and each step becomes a `> SCREEN:` note for the editor: the file, exact lines to highlight, the terminal command and which output line to highlight. Build the editor and terminal from the real source files and real run output, not screenshots or invented output.

Write the narration as a walk-through of the code itself (what this line does, why it matters), not "look at the code". When a later chapter explains something the demo already showed (e.g. "this loop is the harness"), add a short code callback with its own cues. Re-check the line numbers whenever the demo files change, and give the user a run sheet: each demo's file, lines, commands, and where it sits in the script.

## When you plan or present a script

- In the plan you show the user, list the **hook (pain → preview → promise) first**, then the one-line roadmap, then the chapter-by-chapter breakdown.
- Hand the script over together with the packaging (3 titles, 2–3 thumbnail briefs, 2–3 Shorts ideas) from `../../youtube-packaging/SKILL.md`, and run its **pre-publish checklist**. Script checks:
  - [ ] The first spoken line is the hook: no greeting, channel intro, logo sting or "in this video I'll…"
  - [ ] No reference to a previous video in the first 30 seconds
  - [ ] Hook follows pain → preview of the result → promise, within 30 seconds
  - [ ] Repo/code mentioned in the first 30 seconds (if there's code)
  - [ ] Demo or visual payoff appears in the first third
  - [ ] Depth matches the title; basics cut to one line or linked
  - [ ] Roadmap (if any) is one sentence, with chapter names matching the on-screen cards
  - [ ] Mid-video plugs are one sentence and return to the topic; related videos are collected in the outro
  - [ ] Follow-up topics that already have videos are referenced as "link in the description", not "next video"
  - [ ] End CTA is one line each for like, comment, subscribe, and 30 seconds or less
  - [ ] Chapter list with timestamps included for the description
  - [ ] Every live code step has a `[VS Code]` / `[Terminal]` cue (or a `> SCREEN:` note) with exact file, lines, and command

## Example: rewriting the "Agent with Sub-Agents" opening

**Before (lost ~55% of viewers in 40 seconds):**

> In the last video, we built one AI agent. Today we'll build an agent that has sub-agents… Here's the plan. First, a quick refresher on what an agent is, and what a session is…

**After:**

> One agent. Seven tools. A customer asks where their order is, and your agent goes and searches the product catalog instead.
> `> SCREEN: PREVIEW 5s of the finished demo: root agent hands the question to order_agent, the answer comes back.`
> Here's the fix: a team. A root agent that routes each question to a specialist, built with Google's Agent Development Kit. By the end you'll have this exact team running, and the full working code is on GitHub, linked in the description.
> We'll see why one big agent breaks, run the team on a real customer, then walk through the code.
