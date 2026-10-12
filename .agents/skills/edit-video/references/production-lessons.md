# Production lessons

Learned on a complete 10-minute talking-head edit (teleprompter takes, local
Whisper, 29 transcript-anchored beats, PiP camera). Each item cost a revision.

## Footage and audio

- **Check frame rate and resolution on the first take.** Browser and webcam
  recordings come in as VP9 WebM with a variable frame rate. A dim room dropped one
  webcam to ~15 fps at 720p for every take. Count frames
  (`ffprobe -count_packets -select_streams v:0 -show_entries stream=nb_read_packets`)
  against the audio length, and warn before the whole session is recorded: more
  front light usually restores 30 fps. Transcode every take to constant 30 fps
  H.264 + AAC before any cutting (`-vf fps=30`).
- **Measure loudness.** Browser recordings measured -36 LUFS. Normalize the voice
  track with two-pass `loudnorm` to about -14 to -16 LUFS integrated, -1.5 dBTP,
  and keep the raw track. Check the rendered MP4 again; the render landed at
  -12.9 LUFS.
- **Per-chapter takes:** process each take separately (silence pass, mistakes),
  then concatenate with each take's audio padded or trimmed to its exact video
  length (`apad,atrim=0:<video duration>`), so small A/V differences cannot add up
  across joins. Verify by cross-correlating the edit's audio against each take
  at its chapter offset: a constant ~20 ms (AAC priming) is fine; growth is drift.
- **Whisper smears a take's first words into the silence before them.** Two
  Part 2 takes open with 7-8 s of silence; Whisper spread "Okay, this is the
  problem we..." across that silence and squeezed the rest into the real speech.
  Trusting those timestamps, a cut started mid-sentence and dropped a sentence
  that was recorded. (A first pass wrongly called it "never recorded"; the
  presenter caught it.) Find the speech onset from 0.25 s RMS levels, then
  transcribe a window starting just before it to confirm the words. Never call
  speech missing until you have measured the levels and transcribed that window.

## Transcription and cutting

- Local Whisper through `npx hyperframes transcribe <file> -m medium.en -l en` is
  free, keeps audio on the machine, and took ~1-2 min per minute of audio.
  `small.en` misheard key terms ("proms" for prompts). Timing is usable for
  anchors; treat the text as approximate.
- **Never cut on Whisper word gaps.** Use `cut-silences-audio.mjs` (see the
  cut-silences skill). Then re-transcribe the cut video and time all graphics to
  that transcript.
- Zero-length duplicate words from Whisper ("let's let's" with 0 ms) look like
  stutters to `cut-mistakes`. Check the audio; drop the phantom word, don't cut.
- After any recut, re-anchor every beat from the new transcript. Phrase anchors
  survive; absolute times don't. Re-check anchors whose spelling changed between
  transcriptions ("part one" -> "part 1", "ChatGPT" -> "Chad GPT").

## Composition

- **Camera footage goes in its own sub-composition** (`compositions/camera.html`)
  with a non-timed wrapper div and the timed `<video>` inside. Lint requires
  `data-start="0"` on the root, and preflight rejects a root `data-start` next to
  an inline `<video>`; the sub-composition satisfies both. Keep the voice as a
  sibling `<audio>` in the root.
- **Move the camera with transforms only:** `x`, `y`, `scale` with
  `transform-origin: 0 0`. Animating `left/top/width/height` snaps to whole pixels
  and lint flags it. Scale `borderRadius` and `borderWidth` by `1/scale` so the
  PiP card keeps its intended corner and border.
- Sub-composition asset paths are root-relative (`assets/gsap.min.js`), never
  `../assets/...`.
- Give each sub-composition root an id and scope its styles with that id, not the
  `[data-composition-id]` attribute.
- **Rotating SVG parts (needles, dials, hands) needs `svgOrigin: "cx cy"`** on every
  tween. GSAP otherwise rotates around the element's own bounding box and the
  needle swings out of its dial.
- State changes on a board or list (lit, done, ghost) must be tweened properties
  (opacity of overlay layers, color), not class toggles inside callbacks. Class
  toggles don't reverse when Studio scrubs backwards.
- A full-frame overlay that should start hidden needs `opacity: 0` in its CSS and a
  `tl.to` reveal; lint flags a `from` tween here.
- Generate the beats from a script (`scripts/build.py` writing `index.html` and
  `compositions/*.html`) that resolves every time from transcript phrases. A recut
  then becomes "re-transcribe, rebuild", not hand edits.

- **Inline `font: 600 26px Inter` has no fallback.** Inter isn't shipped as a
  local file; Studio snapshots showed sans, but the render drew those labels in a
  serif. Use the local brand font (Poppins) or classes whose stack ends in
  `Arial, sans-serif`, and check label fonts in the encoded draft.

## Lower thirds and banners

- **A banner must never be on screen without text.** Viewers read an empty card
  as a malfunction. The card and its headline enter together (wipe the card open,
  headline lands as the wipe finishes); only follow-up lines wait for their words.
  If a beat's first key word is seconds after the beat starts, give the card a
  headline or kicker that is true from the start.

## Rendering and review

- Render with `--workers 1` for camera footage. On a laptop, 10 minutes at 1080p30
  took ~27 min at `--quality draft` and ~31 min at `--quality high` (294 MB).
- Draft QA that caught or cleared real issues:
  `blackdetect`; `freezedetect` on the PiP crop only (full-frame freeze hits during
  static diagram holds are expected); contiguous frame strips across every camera
  move; video PSNR against the source at ±2 frames; audio cross-correlation against
  the voice track (render drift stayed under 50 ms); silence measured at every
  chapter join with `silencedetect`.
- None of this replaces a human watch-through. The user's review found the empty
  banners, the clipped words and the dials; every automated gate had passed.
