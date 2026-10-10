---
name: teleprompter
description: Local teleprompter web page for recording a video's voiceover (and optionally the camera) in time with its script. Scrolls the narration on the video's clock, shows a timer, a pace indicator (ahead / on time / behind) and "on screen" notes, records the mic, or camera + mic, in the browser per chapter or for the whole video, and saves each take with a timings file so the animation can be retimed to the real delivery. Use when the user says "teleprompter", "record my voiceover", "record myself on camera with the script", "talking-head recording", "read the script while recording", "help me keep timing while narrating", "record narration", or "retime the video to my voiceover".
---

# Teleprompter: record a voiceover (or camera) in time with the video

A single self-contained page (`teleprompter.html`) that runs on **localhost**. The browser only allows the microphone on `localhost` or `https`, so it must be served; it won't work as a double-clicked file. Everything stays on the user's machine: audio downloads to their browser's Downloads folder, nothing is uploaded.

## Files in this skill

| File | Purpose |
|---|---|
| `teleprompter.html` | The page. Copy it into the project as `teleprompter/index.html`. |
| `script_to_cues.py` | Turns a Markdown script into `scripts/cues.json` (the page's input) when the project doesn't already have one. |
| `timings_report.py` | After recording: compares takes with the script and writes `cues.recorded.json` retimed to the real delivery. |

## Input: `scripts/cues.json`

The page reads `../scripts/cues.json` relative to itself (override with `?cues=<url>`).

```json
{
  "title": "Video title",
  "total": 847.0,
  "chapters": [
    { "id": "ch0", "title": "Title", "start": 0, "duration": 27.0,
      "cues": [ { "id": "ch0.1", "start": 1.2, "dur": 7.3, "text": "Narration line…", "note": "What's on screen (optional)" } ] }
  ]
}
```

`chapter.start` is absolute video time; `cue.start` is chapter-local. Times are seconds.

## Workflow

### 1. Get a `cues.json`

- **The project already generates one** (e.g. `video-projects/multi-agents/scripts/cues.py`): run it (`python scripts/cues.py`).
- **Writing a new script?** It must **open with a roadmap**: what we're doing and why, every chapter named in order (matching the chapter headings), and, if there's code, a line saying the code is on GitHub, linked in the description. Full rule: `.agents/skills/make-a-video/references/script-roadmap-intro.md`.
- **Otherwise**, write or reuse a Markdown script and convert it:

  ```markdown
  # Video title
  ## Chapter title
  First narration line.
  > optional on-screen note for the line above
  Second narration line.
  ## Next chapter
  ```

  ```bash
  python .agents/skills/teleprompter/script_to_cues.py <project>/SCRIPT.md <project>/scripts/cues.json --wpm 140
  ```

  It also accepts the `SCRIPT.md` layout used in this workspace (`**0:12.3** line` + `<br>*On screen: …*`). Timings are word-count estimates (`--wpm`, `--gap`, `--lead`, `--tail`, `--outro`).

### 2. Install the page into the project

```bash
mkdir -p <project>/teleprompter
cp .agents/skills/teleprompter/teleprompter.html <project>/teleprompter/index.html
```

Always copy the latest version from the skill folder, so fixes reach every project.

### 3. Serve it and hand the user the URL

Run from the **project folder** (so `../scripts/cues.json` and `../renders/` resolve), in the background:

```bash
cd <project> && npx serve . -p 8090 -n
```

Open **http://localhost:8090/teleprompter/**. If 8090 is taken, use another port.

- Optional query params: `?cues=../scripts/other.json`, `?video=../renders/draft.mp4`.
- If `../renders/draft.mp4` exists, a muted copy plays in sync with the clock in the side panel. The user can also pick any MP4 with **Load MP4…**. A 404 for `draft.mp4` in the console just means no draft exists yet.

### 4. Explain how to use it (tell the user this)

- Pick a **Take**: one chapter (recommended; retakes are painless) or the whole video.
- **Record (R)** → 3-2-1 count-in → the clock starts at that chapter's scripted start.
- Press **Space as you start each line.** That logs the real start time and updates the pace pill:
  - green: on time
  - amber: ahead or behind by more than 1.5s
- **P** pauses and resumes (the mic pauses too). With "Stop at the end of the chapter" on, recording stops automatically at the chapter's end, or press **R** to stop early.
- **Camera (optional):** tick **Record camera too** in the *Camera & mic* panel. A mirrored live preview appears for framing. You can pick the camera, the microphone (this also works for audio-only takes) and the resolution (720p or 1080p, 30 fps ideal). The preview border turns red while recording, and camera controls lock during a take. Settings are remembered per browser.
- On stop, two files download:
  - audio only: `voiceover-<chapter>-take<N>.webm` (Opus)
  - with camera: `camera-<chapter>-take<N>.webm` (VP9 video + Opus audio; about 8 Mbps at 1080p, 5 Mbps at 720p)
  - either way, a matching `…-take<N>.timings.json` (includes `"hasVideo"`)
- **Rehearse (no mic)** runs the same clock and marking without recording.
- **Reading modes:**
  - **Follow the clock**: lines advance on the script's timing.
  - **Advance on Space**: each Space press moves to the next line, and the pace pill still compares against the script.
- **Other keys:** ←/→ jump lines (when not recording), +/− text size, **M** mirror mode for teleprompter glass. Clicking the chapter bar seeks.
- Browser: Chrome or Edge recommended. Allow microphone access when asked. Text size, mirror and mode are remembered per browser.

### 5. After recording: retime the video to the real voiceover

1. Ask the user for the downloaded files. Put them in `<project>/assets/voiceover/`.
2. Report and retime:
   ```bash
   python .agents/skills/teleprompter/timings_report.py <project>/scripts/cues.json "<project>/assets/voiceover/*.timings.json"
   ```
   This prints per-chapter drift (average / worst, old → new duration) and writes `scripts/cues.recorded.json`, the same shape as `cues.json`. The newest take of a chapter wins, and unmarked lines keep their spacing relative to the previous mark.
3. Apply it to the compositions. This is project-specific:
   - Compositions generated from `cues.json` (e.g. `multi-agents` ch7 via `scripts/build_ch7.py`): regenerate from the recorded cues.
   - Compositions with hard-coded cue times: shift each chapter's tween times by that chapter's new cue starts.
   - Update chapter `data-start` / `data-duration` in `index.html` (e.g. `multi-agents/scripts/sync_index.py` reads `cues.json`).
4. Convert and wire the media:
   ```bash
   # audio-only take → AAC
   ffmpeg -i voiceover-ch7-take2.webm -c:a aac -b:a 192k assets/voiceover/ch7.m4a
   # camera take → H.264 MP4 (HyperFrames <video> needs H.264, not VP9/webm)
   ffmpeg -i camera-ch7-take2.webm -c:v libx264 -preset medium -crf 20 -r 30 -c:a aac -b:a 192k -movflags +faststart assets/camera/ch7.mp4
   # camera take → just its audio
   ffmpeg -i camera-ch7-take2.webm -vn -c:a aac -b:a 192k assets/voiceover/ch7.m4a
   ```
   For camera footage: the `<video>` must be `muted`, with the sound in a sibling `<audio>` (same file or the extracted `.m4a`), per the render contract. Use a wrapper `<div>` for any picture-in-picture sizing or animation.
   Add one `<audio>` per chapter at that chapter's new `data-start`, with `data-volume="1"`. A chapter take's audio starts at `audioStartsAtVideoTime` on the *scripted* clock, which becomes the chapter's new start after retiming. If the user paused mid-take, the recording skips the paused time, so rely on the Space marks rather than raw offsets.
5. Lint, then preview-gate as usual before any render.

## Gotchas

- `file://` won't work (no mic or camera, and `fetch` of cues.json is blocked). Always serve it.
- Browser recordings are variable frame rate. Always re-encode camera takes with `-r 30` (above) before using them in a composition.
- Only one app can usually hold the camera. Close Zoom, Teams or OBS if the preview stays black.
- Don't use Python's `http.server` if the user wants to scrub the synced video. Use `npx serve` (it supports range requests).
- The take counter lives in the browser's localStorage, so it resets in a new browser profile. Filenames include the chapter id, so nothing gets overwritten silently: the browser adds `(1)` to duplicate names.
