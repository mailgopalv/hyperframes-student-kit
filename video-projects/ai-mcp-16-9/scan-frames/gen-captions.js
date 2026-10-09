// One-off generator: groups transcript.json words (0-POC_END) into caption
// segments and emits the SEGMENTS array + full captions.html for the project.
const fs = require('fs');
const path = require('path');

const PROJECT = path.resolve(__dirname, '..');
const transcript = require(path.join(PROJECT, 'transcript.json'));
const POC_END = 484.9;

const words = transcript.filter(w => w.start < POC_END);

// Group into 4-6 word segments, breaking on sentence-ending punctuation or a
// pause > 0.5s between words, capped at 6 words per group.
const segments = [];
let current = [];
function flush() {
  if (current.length) segments.push(current);
  current = [];
}
for (let i = 0; i < words.length; i++) {
  const w = words[i];
  current.push(w);
  const next = words[i + 1];
  const endsSentence = /[.!?]$/.test(w.text);
  const longPause = next && (next.start - w.end) > 0.5;
  if (current.length >= 6 || endsSentence || longPause || !next) {
    flush();
  }
}
flush();

// Merge any segment with only 1 word into the previous one (avoids orphan
// single-word caption cards from punctuation splits), unless it's the first.
for (let i = segments.length - 1; i > 0; i--) {
  if (segments[i].length === 1 && segments[i - 1].length < 6) {
    segments[i - 1] = segments[i - 1].concat(segments[i]);
    segments.splice(i, 1);
  }
}

console.log('Total words:', words.length, 'Segments:', segments.length);

function esc(s) {
  return s.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
}

const segJs = segments.map(seg => {
  const wordsJs = seg.map(w => `{ word: "${esc(w.text)}", start: ${w.start.toFixed(3)}, end: ${w.end.toFixed(3)} }`).join(', ');
  return `          { words: [${wordsJs}] }`;
}).join(',\n');

fs.writeFileSync(path.join(__dirname, 'segments.json'), JSON.stringify(segments, null, 0));
fs.writeFileSync(path.join(__dirname, 'segments.js'), segJs);
console.log('Wrote segments.js and segments.json');
