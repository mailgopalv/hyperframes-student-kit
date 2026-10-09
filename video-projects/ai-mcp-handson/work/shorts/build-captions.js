// Word-level captions for a short: transcribe each segment's audio on its own (whisper drifts
// on long files and borrows words across joins), offset to comp time, then apply phrase fixes.
// usage: node build-captions.js <project-dir>   → <project-dir>/assets/captions.json
const { execSync } = require('child_process');
const fs = require('fs'), path = require('path');

const proj = path.resolve(process.argv[2]);
const W = (...p) => path.join(proj, 'work', ...p);
const segs = JSON.parse(fs.readFileSync(W('segments.json'), 'utf8'));
const spec = JSON.parse(fs.readFileSync(W('spec.json'), 'utf8'));

// [spoken tokens] → [caption tokens]; matched case-insensitively, punctuation ignored
const COMMON = [
  ['mcp', 'MCP'], ['llm', 'LLM'], ['alum', 'LLM'], ['aa', 'AI'], ['ai', 'AI'],
  ['odd writing', 'order ID'], ['odd ready', 'order ID'], ['example of ready', 'example order ID'],
  ['0 5 0 0 1', 'O-5001'], ['0 5001', 'O-5001'], ['05001', 'O-5001'],
  ['generate order status', 'get_order_status'], ['get order status', 'get_order_status'],
  ['mcp said initialize', 'MCP send initialize'], ['execute to', 'execute tool'],
  ['mcp-inspect', 'MCP Inspector'], ['mcp-inspector', 'MCP Inspector'],
  ['on save device', 'on same device'], ['under relevant', 'unrelated'], ['nightingame', 'Nottingham'],
  ['duck duck go', 'DuckDuckGo'], ['duckduckgomc', 'DuckDuckGo MCP'], ['stdio', 'stdio'],
  ['the a agent', 'the agent'], ['a agent', 'agent'], ['agents involved', "agent's involved"],
  ['links right below', "link's right below"], ['i built this', 'I build this'], ['i walked through', 'I walk through'],
  ['model-context-protocol/inspector', 'modelcontextprotocol/inspector'],
];
const FIXES = [...COMMON, ...(spec.captionFixes || [])].map(([a, b]) => [a.toLowerCase().split(/\s+/), b.split(/\s+/)]);
const norm = (s) => s.toLowerCase().replace(/[.,?!…:;"]/g, '');

let words = [];
segs.forEach((s, i) => {
  const dir = W('cap', String(i));
  fs.mkdirSync(dir, { recursive: true });
  const wav = fs.readdirSync(W()).find((f) => f.startsWith(`seg-${String(i).padStart(2, '0')}-`) && f.endsWith('.wav'));
  execSync(`ffmpeg -y -v error -i "${W(wav)}" -ac 1 -ar 16000 "${path.join(dir, 'a.wav')}"`);
  if (fs.existsSync(path.join(dir, 'transcript.json'))) fs.unlinkSync(path.join(dir, 'transcript.json'));
  execSync('npx hyperframes transcribe a.wav --model small.en --json', { cwd: dir, stdio: 'ignore' });
  let w = JSON.parse(fs.readFileSync(path.join(dir, 'transcript.json'), 'utf8'));
  // drop words whisper invents before the segment actually starts speaking (spec: dropLead: {lab: n})
  const drop = (spec.dropLead || {})[s.lab] || 0;
  w = w.slice(drop);
  w.forEach((x) => words.push({ t: x.text, s: +(s.start + x.start).toFixed(3), e: +(s.start + Math.min(x.end, s.dur)).toFixed(3) }));
});

// apply phrase fixes
for (const [from, to] of FIXES) {
  for (let i = 0; i + from.length <= words.length; i++) {
    if (!from.every((f, k) => norm(words[i + k].t) === f)) continue;
    const span = words.slice(i, i + from.length), s0 = span[0].s, e1 = span[span.length - 1].e;
    const tail = (span[span.length - 1].t.match(/[.,?!]$/) || [''])[0];
    const rep = to.map((t, k) => ({ t: k === to.length - 1 && !/[.,?!]$/.test(t) ? t + tail : t,
      s: +(s0 + ((e1 - s0) * k) / to.length).toFixed(3), e: +(s0 + ((e1 - s0) * (k + 1)) / to.length).toFixed(3) }));
    words.splice(i, from.length, ...rep);
    i += rep.length - 1;
  }
}
fs.writeFileSync(path.join(proj, 'assets/captions.json'), JSON.stringify(words));
console.log(words.length, 'words');
console.log(words.map((w) => w.t).join(' '));
