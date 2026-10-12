#!/usr/bin/env node
// Agent 1 (audio mode) — Cut Silences from the waveform, not the transcript.
//
// Whisper-style word timestamps can show gaps inside real speech. Cutting on
// those gaps deletes syllables ("learns patterns" -> "learns ...tterns"). This
// mode finds pauses in the audio itself with ffmpeg silencedetect, so every cut
// lands on true silence. Each trimmed pause keeps --tail after the last sound
// and --head before the next one, with 10-12 ms fades at every join.
//
// The threshold is automatic by default: it sits between the recording's noise
// floor (10th percentile of 50 ms RMS windows) and its median level, because
// browser and webcam recordings vary from -30 to -50 dBFS speech.
//
// Outputs (in --out-dir, default next to the video):
//   <stem>.audio-edl.json         keep/delete ranges, threshold, levels
//   <stem>.audio-decisions.md     human-readable summary
//   <stem>.audio-filter.txt       ffmpeg filtergraph
//   <stem>.silenced.mp4           with --apply
//   <stem>.audio-transcript.json  with --transcript: words re-timed onto the cut
//                                 (re-transcribe the cut video for exact timing)
//
// Usage:
//   node cut-silences-audio.mjs <video> [--out-dir dir] [--output path]
//        [--noise auto|-62] [--min-sil 0.55] [--tail 0.20] [--head 0.14]
//        [--edge-head 0.25] [--edge-tail 0.35] [--transcript words.json] [--apply]

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join, resolve, basename, extname } from "node:path";
import { spawnSync } from "node:child_process";
import { argv, exit } from "node:process";

const args = argv.slice(2);
if (args.length === 0 || args.includes("--help") || args.includes("-h")) {
  console.log("Usage: node cut-silences-audio.mjs <video> [--out-dir dir] [--output path] [--noise auto|-62]\n" +
    "       [--min-sil 0.55] [--tail 0.20] [--head 0.14] [--edge-head 0.25] [--edge-tail 0.35]\n" +
    "       [--transcript words.json] [--apply]");
  exit(args.length === 0 ? 1 : 0);
}
const opts = { video: null, outDir: null, output: null, noise: "auto", minSil: 0.55, tail: 0.2, head: 0.14,
  edgeHead: 0.25, edgeTail: 0.35, transcript: null, apply: false };
const num = (v, f) => { const n = Number(v); if (!Number.isFinite(n)) { console.error(`${f} needs a number`); exit(1); } return n; };
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === "--out-dir") opts.outDir = args[++i];
  else if (a === "--output") opts.output = args[++i];
  else if (a === "--noise") opts.noise = args[++i];
  else if (a === "--min-sil") opts.minSil = num(args[++i], a);
  else if (a === "--tail") opts.tail = num(args[++i], a);
  else if (a === "--head") opts.head = num(args[++i], a);
  else if (a === "--edge-head") opts.edgeHead = num(args[++i], a);
  else if (a === "--edge-tail") opts.edgeTail = num(args[++i], a);
  else if (a === "--transcript") opts.transcript = args[++i];
  else if (a === "--apply") opts.apply = true;
  else if (!a.startsWith("--") && !opts.video) opts.video = a;
  else { console.error(`Unknown argument: ${a}`); exit(1); }
}

const video = resolve(opts.video);
const stem = basename(video, extname(video));
const outDir = resolve(opts.outDir ?? dirname(video));
mkdirSync(outDir, { recursive: true });
const run = (cmd, a, extra = {}) => {
  const r = spawnSync(cmd, a, { maxBuffer: 1 << 30, ...extra });
  if (r.status !== 0) { console.error(`${cmd} failed:\n${r.stderr?.toString().slice(-2000)}`); exit(1); }
  return r;
};
const r3 = (x) => Math.round(x * 1000) / 1000;

const dur = Number(run("ffprobe", ["-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration",
  "-of", "csv=p=0", video]).stdout.toString().trim()) ||
  Number(run("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video]).stdout.toString().trim());

// ---- levels: 50 ms RMS windows ----
const pcm = run("ffmpeg", ["-v", "error", "-i", video, "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"]).stdout;
const samples = new Int16Array(pcm.buffer, pcm.byteOffset, Math.floor(pcm.length / 2));
const W = 400, levels = [];
for (let k = 0; k + W <= samples.length; k += W) {
  let s = 0; for (let j = k; j < k + W; j++) s += samples[j] * samples[j];
  levels.push(20 * Math.log10(Math.max(1e-9, Math.sqrt(s / W) / 32768)));
}
levels.sort((a, b) => a - b);
const pct = (q) => levels[Math.min(levels.length - 1, Math.floor(q * levels.length))];
const floor = pct(0.1), median = pct(0.5), loud = pct(0.9);
const noise = opts.noise === "auto" ? Math.round(Math.min(floor + 0.6 * (median - floor), median - 10)) : num(opts.noise, "--noise");

// ---- silences from the waveform ----
const sd = run("ffmpeg", ["-v", "info", "-i", video, "-vn", "-af", `silencedetect=noise=${noise}dB:d=${opts.minSil}`, "-f", "null", "-"]).stderr.toString();
const starts = [...sd.matchAll(/silence_start: ([0-9.]+)/g)].map((m) => Number(m[1]));
const ends = [...sd.matchAll(/silence_end: ([0-9.]+)/g)].map((m) => Number(m[1]));
const dels = [];
starts.forEach((s, i) => {
  const e = ends[i];
  if (e === undefined || e > dur - 0.05) dels.push([Math.min(dur, s + opts.edgeTail), dur, "tail trim"]);
  else if (s < 0.05) dels.push([0, Math.max(0, e - opts.edgeHead), "head trim"]);
  else if ((e - opts.head) - (s + opts.tail) > 0.12) dels.push([s + opts.tail, e - opts.head, `pause ${(e - s).toFixed(2)}s -> ${(opts.tail + opts.head).toFixed(2)}s`]);
});
const del = dels.filter(([a, b]) => b - a > 0.05).map(([a, b, r]) => ({ start: r3(a), end: r3(b), reason: r }));
const keep = []; let t = 0;
for (const d of del) { if (d.start > t) keep.push([t, d.start]); t = Math.max(t, d.end); }
if (t < dur) keep.push([t, dur]);
const keeps = keep.filter(([a, b]) => b - a > 0.04).map(([a, b]) => [r3(a), r3(b)]);
const edited = r3(keeps.reduce((s, [a, b]) => s + b - a, 0));

const edl = { source: video, duration: r3(dur), edited_duration: edited, removed: r3(dur - edited),
  levels_dbfs: { floor: r3(floor), median: r3(median), p90: r3(loud) }, noise_db: noise, min_silence: opts.minSil,
  keep: keeps, delete: del };
writeFileSync(join(outDir, `${stem}.audio-edl.json`), JSON.stringify(edl, null, 1));

// ---- filtergraph: trim/atrim with short fades, concat ----
const parts = [], labels = [];
keeps.forEach(([a, b], k) => {
  const len = b - a;
  parts.push(`[0:v]trim=${a}:${b},setpts=PTS-STARTPTS[v${k}];[0:a]atrim=${a}:${b},asetpts=PTS-STARTPTS,` +
    `afade=t=in:d=0.01,afade=t=out:st=${Math.max(0, len - 0.012).toFixed(3)}:d=0.012[a${k}]`);
  labels.push(`[v${k}][a${k}]`);
});
const filter = parts.join(";\n") + ";\n" + labels.join("") + `concat=n=${keeps.length}:v=1:a=1[v][a]`;
const filterPath = join(outDir, `${stem}.audio-filter.txt`);
writeFileSync(filterPath, filter);
const output = resolve(opts.output ?? join(outDir, `${stem}.silenced.mp4`));

const longest = [...del].filter((d) => d.reason.startsWith("pause")).sort((a, b) => (b.end - b.start) - (a.end - a.start)).slice(0, 8);
writeFileSync(join(outDir, `${stem}.audio-decisions.md`), [
  `# Audio silence cut: ${stem}`, "",
  `- Levels (50 ms RMS): floor ${floor.toFixed(1)} dBFS, median ${median.toFixed(1)}, p90 ${loud.toFixed(1)}`,
  `- Threshold: ${noise} dBFS for ${opts.minSil}s or more (${opts.noise === "auto" ? "auto" : "manual"})`,
  `- ${dur.toFixed(2)}s -> ${edited.toFixed(2)}s (${(dur - edited).toFixed(2)}s removed, ${del.length} cuts)`, "",
  "Largest pauses trimmed:", ...longest.map((d) => `- ${d.start.toFixed(2)}-${d.end.toFixed(2)}s: ${d.reason}`), ""].join("\n"));

// ---- optional: re-time an existing word transcript onto the cut ----
let transcriptOut = null;
if (opts.transcript) {
  const raw = JSON.parse(readFileSync(resolve(opts.transcript), "utf8"));
  const words = Array.isArray(raw) ? raw : raw.words;
  const offsets = []; let acc = 0;
  for (const [a, b] of keeps) { offsets.push([a, b, acc]); acc += b - a; }
  const map = (x) => { for (const [a, b, o] of offsets) if (x >= a - 1e-6 && x <= b + 1e-6) return o + (x - a); return null; };
  const out = [];
  for (const w of words) {
    const mid = (w.start + w.end) / 2, s = map(w.start) ?? map(mid), e = map(w.end) ?? map(mid);
    if (s === null || e === null) continue;
    out.push({ ...w, source_start: w.start, source_end: w.end, start: r3(s), end: r3(Math.max(s, e)) });
  }
  transcriptOut = join(outDir, `${stem}.audio-transcript.json`);
  writeFileSync(transcriptOut, JSON.stringify({ note: "Re-timed from the source transcript. Re-transcribe the cut video for exact word timing.",
    audio_duration_secs: edited, words: out }, null, 1));
}

if (opts.apply) {
  run("ffmpeg", ["-v", "error", "-y", "-i", video, "-/filter_complex", filterPath, "-map", "[v]", "-map", "[a]",
    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", output], { stdio: ["ignore", "ignore", "pipe"] });
}

console.log(JSON.stringify({ source: video, duration: r3(dur), editedDuration: edited, removed: r3(dur - edited),
  removedPct: r3((dur - edited) / dur * 100), cuts: del.length, noiseDb: noise,
  levels: { floor: r3(floor), median: r3(median), p90: r3(loud) },
  edl: join(outDir, `${stem}.audio-edl.json`), transcript: transcriptOut, output: opts.apply ? output : null }, null, 2));
