// Extract word-exact verification frames from a render and tile them into one grid PNG.
// usage: node verify-frames.js <project-dir> <render.mp4> <ref> [<ref> ...]
// refs use the same syntax as visual.json ("word:initializes+0.3", "seg:c2+1", 12.5)
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
const [proj, render, ...refs] = [path.resolve(process.argv[2]), process.argv[3], ...process.argv.slice(4)];
const SEGS = JSON.parse(fs.readFileSync(path.join(proj, 'work/segments.json'), 'utf8'));
const WORDS = JSON.parse(fs.readFileSync(path.join(proj, 'assets/captions.json'), 'utf8'));
const norm = (s) => s.toLowerCase().replace(/[.,?!…:;"']/g, '');
function T(ref) {
  if (!isNaN(+ref)) return +ref;
  let m = ref.match(/^seg:([\w-]+)([+-][\d.]+)?$/);
  if (m) return SEGS.find((x) => x.lab === m[1]).start + (+m[2] || 0);
  m = ref.match(/^word:([^@+-]+?)(?:@([\d.]+))?([+-][\d.]+)?$/);
  const w = WORDS.find((x) => norm(x.t).startsWith(norm(m[1])) && x.s >= (+m[2] || 0));
  return w.s + (+m[3] || 0);
}
const dir = path.join(proj, 'renders', 'frames-' + path.basename(render, '.mp4'));
fs.mkdirSync(dir, { recursive: true });
const files = refs.map((ref, i) => {
  const t = T(ref), f = path.join(dir, `${String(i).padStart(2, '0')}-t${t.toFixed(2)}.png`);
  execFileSync('ffmpeg', ['-y', '-v', 'error', '-ss', t.toFixed(3), '-i', path.join(proj, render), '-frames:v', '1', '-vf', 'scale=360:640', f]);
  console.log(`${String(i).padStart(2, '0')}  t=${t.toFixed(2)}  ${ref}`);
  return f;
});
execFileSync('ffmpeg', ['-y', '-v', 'error', ...files.flatMap((f) => ['-i', f]), '-filter_complex', `hstack=inputs=${files.length}`, path.join(dir, 'grid.png')]);
console.log('grid:', path.join(dir, 'grid.png'));
