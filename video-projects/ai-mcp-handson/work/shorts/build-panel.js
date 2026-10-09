// Build the edited 1080x1080 panel video + audio for a short from a spec.
// usage: node build-panel.js <project-dir>   (reads <project-dir>/work/spec.json)
//
// Video and audio are rendered in separate passes. Audio is cut with a sample-exact atrim
// (never limited by a video frame count), so filters with look-ahead like loudnorm always
// flush their tail — a frame-limited mux silently drops the last words.
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');

const proj = path.resolve(process.argv[2]);
const spec = JSON.parse(fs.readFileSync(path.join(proj, 'work/spec.json'), 'utf8'));
const W = (...p) => path.join(proj, 'work', ...p);
const SRC = path.resolve(proj, spec.src), VO = path.resolve(proj, spec.vo);
const FPS = 30, snap = (d) => Math.round(d * FPS) / FPS;
const ff = (args) => execFileSync('ffmpeg', ['-y', '-v', 'error', ...args]);

// quietest 20ms point of the source audio in [a, b] — where a cut is least audible
function quietest(a, b) {
  let txt;
  try {
    txt = execFileSync('ffmpeg', ['-v', 'info', '-ss', a.toFixed(3), '-t', (b - a).toFixed(3), '-i', SRC, '-vn',
      '-af', 'asetnsamples=n=882,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level', '-f', 'null', '-'],
      { stdio: ['ignore', 'ignore', 'pipe'] }).toString();
  } catch (e) { txt = e.stderr ? e.stderr.toString() : ''; }
  const v = [...txt.matchAll(/RMS_level=(-?[0-9.]+|-inf)/g)].map((m) => (m[1] === '-inf' ? -120 : +m[1]));
  if (!v.length) return (a + b) / 2;
  let k = 0; v.forEach((x, i) => { if (x < v[k]) k = i; });
  return a + k * 0.02 + 0.01;
}

const cropF = (c) => { const [w, h, x, y] = spec.crops[c]; return `crop=${w}:${h}:${x}:${y},scale=1080:1080:flags=lanczos,fps=30,setsar=1`; };
const NORM = 'loudnorm=I=-16:TP=-1.5:LRA=11';

let t = 0; const vlist = [], alist = [], meta = [];
spec.segments.forEach((s, i) => {
  const next = spec.segments[i + 1];
  const contIn = !!s.cont;                 // continues the previous segment's audio (same take)
  const contOut = !!(next && next.cont);   // next segment continues this one
  let file, a, dur, vs;
  if (s.clip) {
    let [ca, cb] = s.clip;
    if (!contIn && s.refine !== false && s.refineStart !== false) ca = quietest(ca - 0.12, ca + 0.06);
    if (!contOut && s.refine !== false) cb = quietest(cb - 0.05, cb + 0.35);
    file = SRC; a = ca; dur = snap(cb - ca); vs = ca;
    s._range = [ca, ca + dur];
  } else {
    file = VO; a = s.vo[0]; dur = snap(s.vo[1] - s.vo[0]); vs = s.video;
  }
  const base = W(`seg-${String(i).padStart(2, '0')}-${s.lab}`);

  // video pass
  const vIn = s.freeze != null
    ? (ff(['-ss', s.freeze.toFixed(3), '-i', SRC, '-frames:v', '1', W('freeze.png')]),
       ['-loop', '1', '-framerate', '30', '-t', dur.toFixed(4), '-i', W('freeze.png')])
    : ['-ss', vs.toFixed(3), '-t', dur.toFixed(4), '-i', SRC];
  ff([...vIn, '-vf', cropF(s.crop), '-an', '-frames:v', String(Math.round(dur * FPS)),
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', base + '.mp4']);

  // audio pass: coarse seek 2s early, then sample-exact atrim
  const pre = Math.max(0, a - 2), off = a - pre;
  const fin = contIn ? '' : ',afade=t=in:d=0.02';
  const fout = contOut ? '' : `,afade=t=out:st=${(dur - 0.03).toFixed(3)}:d=0.03`;
  ff(['-ss', pre.toFixed(3), '-i', file, '-vn', '-af',
    `atrim=start=${off.toFixed(4)}:end=${(off + dur).toFixed(4)},asetpts=PTS-STARTPTS,aresample=48000,` +
    `aformat=channel_layouts=stereo,${NORM},aresample=48000,asetpts=N/SR/TB${fin}${fout},apad=whole_len=${Math.round(dur * 48000)},atrim=end_sample=${Math.round(dur * 48000)}`,
    '-c:a', 'pcm_s16le', base + '.wav']);

  vlist.push(`file '${path.basename(base)}.mp4'`); alist.push(`file '${path.basename(base)}.wav'`);
  meta.push({ lab: s.lab, start: +t.toFixed(4), dur, src: s._range || null });
  t += dur;
});

fs.writeFileSync(W('vlist.txt'), vlist.join('\n'));
fs.writeFileSync(W('alist.txt'), alist.join('\n'));
fs.writeFileSync(W('segments.json'), JSON.stringify(meta, null, 1));
fs.mkdirSync(path.join(proj, 'assets'), { recursive: true });
fs.mkdirSync(W('edit'), { recursive: true });
const id = spec.id;
ff(['-f', 'concat', '-safe', '0', '-i', W('vlist.txt'), '-c:v', 'copy', path.join(proj, `assets/${id}-panel.mp4`)]);
ff(['-f', 'concat', '-safe', '0', '-i', W('alist.txt'), '-c:a', 'aac', '-b:a', '192k', path.join(proj, `assets/${id}-audio.m4a`)]);
ff(['-f', 'concat', '-safe', '0', '-i', W('alist.txt'), '-ac', '1', '-ar', '16000', W('edit', 'edit.wav')]);
console.log(meta.map((m) => `${m.lab.padEnd(6)} ${m.start.toFixed(2).padStart(6)} +${m.dur.toFixed(2)}  ${m.src ? m.src.map((x) => x.toFixed(2)).join('-') : ''}`).join('\n'));
console.log('TOTAL', t.toFixed(3));
