// Generate a short's index.html (same design as ai-mcp-short1) from work/visual.json.
// usage: node gen-short.js <project-dir>
// Time refs in visual.json: number | "seg:<lab>[+/-n]" | "word:<prefix>[@minTime][+/-n]" | "end"
const fs = require('fs'), path = require('path');
const proj = path.resolve(process.argv[2]);
const spec = JSON.parse(fs.readFileSync(path.join(proj, 'work/spec.json'), 'utf8'));
const V = JSON.parse(fs.readFileSync(path.join(proj, 'work/visual.json'), 'utf8'));
const SEGS = JSON.parse(fs.readFileSync(path.join(proj, 'work/segments.json'), 'utf8'));
const WORDS = JSON.parse(fs.readFileSync(path.join(proj, 'assets/captions.json'), 'utf8'));
const id = spec.id;
const DUR = +SEGS.reduce((a, s) => a + s.dur, 0).toFixed(3);
const norm = (s) => s.toLowerCase().replace(/[.,?!…:;"']/g, '');

function T(ref) {
  if (typeof ref === 'number') return ref;
  if (ref === 'end') return DUR;
  let m = ref.match(/^seg:([\w-]+)([+-][\d.]+)?$/);
  if (m) { const s = SEGS.find((x) => x.lab === m[1]); if (!s) throw new Error('no seg ' + m[1]); return +(s.start + (+m[2] || 0)).toFixed(3); }
  m = ref.match(/^word:([^@+-]+?)(?:@([\d.]+))?([+-][\d.]+)?$/);
  if (m) {
    const w = WORDS.find((x) => norm(x.t).startsWith(norm(m[1])) && x.s >= (+m[2] || 0));
    if (!w) throw new Error('no word ' + ref);
    return +(w.s + (+m[3] || 0)).toFixed(3);
  }
  throw new Error('bad ref ' + ref);
}
const r = (x) => +x.toFixed(4);

// panel cut transitions: every segment boundary where the picture changes
const FLAVORS = ['streak', 'push', 'flash', 'punch'];
const cuts = SEGS.slice(1)
  .map((s, i) => ({ t: s.start, flavor: (V.cuts || {})[s.lab] || FLAVORS[i % FLAVORS.length] }))
  .filter((c) => c.flavor !== 'none');

const beats = V.beats.map((b, i) => ({ ...b, id: `b${i + 1}`, t: T(b.t) }));
const chips = V.chips.map((c, i) => ({ ...c, id: `chip${i + 1}`, a: T(c.a), b: T(c.b) }));
const boxes = V.boxes.map((b, i) => ({ ...b, id: `hl${i + 1}`, a: T(b.a), b: T(b.b) }));
const stamps = (V.stamps || []).map((s, i) => ({ ...s, id: `st${i + 1}`, t: T(s.t), b: s.b != null ? T(s.b) : null }));

const esc = (s) => s.replace(/&/g, '&amp;');
const html = `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    html, body { margin: 0; background: #07121c; }
    #${id} { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #07121c; font-family: "Montserrat", sans-serif; }
    .bg-radial { position: absolute; inset: 0; background: radial-gradient(ellipse 80% 55% at 50% 48%, #0f2a3f 0%, #0a1b2a 45%, #07121c 100%); }
    .bg-grid { position: absolute; inset: -80px;
      background-image: repeating-linear-gradient(0deg, rgba(55,189,248,0.07) 0 1px, transparent 1px 72px), repeating-linear-gradient(90deg, rgba(55,189,248,0.07) 0 1px, transparent 1px 72px);
      -webkit-mask-image: radial-gradient(ellipse 70% 60% at 50% 50%, #000 20%, transparent 85%); mask-image: radial-gradient(ellipse 70% 60% at 50% 50%, #000 20%, transparent 85%); }
    .bg-glow { position: absolute; left: 90px; right: 90px; top: 700px; height: 700px; border-radius: 50%; background: radial-gradient(ellipse at center, rgba(55,189,248,0.16), transparent 70%); filter: blur(30px); }
    .bg-grain { position: absolute; inset: 0; opacity: 0.5; pointer-events: none;
      background-image: radial-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), radial-gradient(rgba(255,255,255,0.025) 1px, transparent 1px), radial-gradient(rgba(0,0,0,0.05) 1px, transparent 1px);
      background-size: 3px 3px, 5px 5px, 7px 7px; background-position: 0 0, 1px 2px, 2px 1px; }
    .bg-vignette { position: absolute; inset: 0; pointer-events: none; background: radial-gradient(ellipse at center, transparent 45%, rgba(0,0,0,0.75) 100%); }

    .beats { position: absolute; left: 0; right: 0; top: 150px; height: 330px; }
    .beat { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 18px; padding: 0 70px; box-sizing: border-box; text-align: center; opacity: 0; }
    .beat h1 { margin: 0; font-weight: 900; font-size: 74px; line-height: 1.06; letter-spacing: -0.03em;
      background: linear-gradient(180deg, #ffffff 0%, #b9c4cf 62%, #e6ebf0 100%); -webkit-background-clip: text; background-clip: text; color: transparent; filter: drop-shadow(0 0 18px rgba(255,255,255,0.18)); }
    .beat h1 em { font-style: normal; -webkit-text-fill-color: currentColor; white-space: nowrap; }
    em.red { color: #ff4d5e; text-shadow: 0 0 24px rgba(225,11,31,0.55); }
    em.cyan { color: #37bdf8; text-shadow: 0 0 24px rgba(55,189,248,0.55); }
    em.amber { color: #f5a623; text-shadow: 0 0 24px rgba(245,166,35,0.5); }
    .beat .sub { font: 500 30px/1.2 "JetBrains Mono", monospace; color: #8fa2b8; letter-spacing: -0.01em; }

    .panel { position: absolute; left: 40px; top: 520px; width: 1000px; height: 1000px; border-radius: 30px; overflow: hidden; background: #0b1117;
      box-shadow: 0 0 0 2px rgba(55,189,248,0.35), 0 30px 80px rgba(0,0,0,0.6), 0 0 60px rgba(55,189,248,0.15); }
    .kb { position: absolute; left: 0; top: 0; width: 1080px; height: 1080px; transform-origin: 0 0; }
    .kb-inner { position: absolute; inset: 0; transform-origin: 50% 50%; }
    #panel-video { position: absolute; left: 0; top: 0; width: 1080px; height: 1080px; }
    .hl { position: absolute; border-radius: 14px; opacity: 0; box-sizing: border-box; }
    .hl.red { border: 5px solid #ff4d5e; box-shadow: 0 0 34px rgba(225,11,31,0.7), inset 0 0 24px rgba(225,11,31,0.25); }
    .hl.cyan { border: 5px solid #37bdf8; box-shadow: 0 0 34px rgba(55,189,248,0.7), inset 0 0 24px rgba(55,189,248,0.2); }
    .hl.amber { border: 5px solid #f5a623; box-shadow: 0 0 34px rgba(245,166,35,0.7), inset 0 0 24px rgba(245,166,35,0.2); }
    .tag { position: absolute; opacity: 0; padding: 10px 18px; border-radius: 10px; font: 700 30px/1 "JetBrains Mono", monospace; color: #07121c; white-space: nowrap; }
    .tag.amber { background: #f5a623; } .tag.cyan { background: #37bdf8; } .tag.red { background: #ff4d5e; color: #fff; }
    .chip { position: absolute; left: 22px; top: 22px; padding: 10px 16px; border-radius: 10px; opacity: 0; background: rgba(7,18,28,0.82); border: 1px solid rgba(55,189,248,0.4); font: 500 28px/1 "JetBrains Mono", monospace; color: #cfe9f7; }
    .streak { position: absolute; top: 0; bottom: 0; left: 0; width: 420px; opacity: 0; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.85), transparent); filter: blur(18px); }
    .flash { position: absolute; inset: 0; background: #ffffff; opacity: 0; }

    .stamp { position: absolute; left: 50%; top: 600px; opacity: 0; padding: 18px 34px; border-radius: 14px; white-space: nowrap; font-weight: 900; font-size: 56px; letter-spacing: 0.01em; transform: translateX(-50%); }
    .stamp.red { color: #fff; background: #e10b1f; box-shadow: 0 0 50px rgba(225,11,31,0.7), 0 12px 30px rgba(0,0,0,0.5); }
    .stamp.cyan { color: #07121c; background: #37bdf8; box-shadow: 0 0 50px rgba(55,189,248,0.7), 0 12px 30px rgba(0,0,0,0.5); }
    .stamp.amber { color: #07121c; background: #f5a623; box-shadow: 0 0 50px rgba(245,166,35,0.7), 0 12px 30px rgba(0,0,0,0.5); }

    .caps { position: absolute; left: 0; right: 0; top: 1570px; height: 260px; }
    .cap { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 0 34px; padding: 0 60px; box-sizing: border-box; opacity: 0; }
    .w { display: inline-block; font-weight: 900; font-size: 62px; line-height: 1.15; color: #ffffff; letter-spacing: -0.01em;
      text-shadow: 0 0 2px #000, 3px 3px 0 #000, -3px 3px 0 #000, 3px -3px 0 #000, -3px -3px 0 #000, 0 6px 18px rgba(0,0,0,0.6); }
  </style>
</head>
<body>
  <div id="${id}" data-composition-id="${id}" data-start="0" data-duration="${DUR}" data-width="1080" data-height="1920">
    <div class="bg-radial"></div>
    <div class="bg-grid" id="bg-grid"></div>
    <div class="bg-glow" id="bg-glow"></div>
    <div class="bg-grain"></div>
    <div class="bg-vignette"></div>

    <div class="beats">
${beats.map((b) => `      <div class="beat" id="${b.id}"><h1>${b.h}</h1>${b.sub ? `<div class="sub">${esc(b.sub)}</div>` : ''}</div>`).join('\n')}
    </div>

    <div class="panel" id="panel">
      <div class="kb"><div class="kb-inner" id="kb-inner">
        <video id="panel-video" src="assets/${id}-panel.mp4" muted playsinline data-start="0" data-duration="${DUR}" data-track-index="0"></video>
${boxes.map((b) => `        <div class="hl ${b.c}" id="${b.id}" style="left:${b.box[0]}px; top:${b.box[1]}px; width:${b.box[2]}px; height:${b.box[3]}px;"></div>` +
  (b.tag ? `\n        <div class="tag ${b.c}" id="${b.id}-tag" style="left:${b.tag.l}px; top:${b.tag.t}px;">${esc(b.tag.text)}</div>` : '')).join('\n')}
      </div></div>
${chips.map((c) => `      <div class="chip" id="${c.id}">${esc(c.text)}</div>`).join('\n')}
      <div class="streak" id="streak" data-layout-allow-overflow></div>
      <div class="flash" id="flash"></div>
    </div>

${stamps.map((s) => `    <div class="stamp ${s.c}" id="${s.id}"${s.top ? ` style="top:${s.top}px"` : ''}>${esc(s.text)}</div>`).join('\n')}

    <div class="caps" id="caps"></div>

    <audio id="vo" src="assets/${id}-audio.m4a" data-start="0" data-duration="${DUR}" data-track-index="1" data-volume="1"></audio>

    <script>
      (() => {
        const DUR = ${DUR};
        const WORDS = ${JSON.stringify(WORDS)};
        const BEATS = ${JSON.stringify(beats.map((b) => [b.id, r(b.t)]))};
        const CHIPS = ${JSON.stringify(chips.map((c) => [c.id, r(c.a), r(c.b)]))};
        const BOXES = ${JSON.stringify(boxes.map((b) => [b.id, r(b.a), r(b.b), !!b.tag]))};
        const STAMPS = ${JSON.stringify(stamps.map((s) => [s.id, r(s.t), s.b != null ? r(s.b) : null, s.rot || -4]))};
        const CUTS = ${JSON.stringify(cuts.map((c) => [r(c.t), c.flavor]))};
        const SEGS = ${JSON.stringify(SEGS.map((s) => r(s.start)).concat([DUR]))};

        // captions: 1–3 word groups, break on punctuation / pauses
        const groups = []; let g = [];
        WORDS.forEach((w, i) => {
          g.push(w); const nx = WORDS[i + 1];
          if (!nx || /[.,?!…]$/.test(w.t) || g.length >= 3 || nx.s - w.e > 0.35) { groups.push(g); g = []; }
        });
        const caps = document.getElementById("caps");
        groups.forEach((grp) => {
          const d = document.createElement("div"); d.className = "cap";
          grp.forEach((w) => { const s = document.createElement("span"); s.className = "w"; s.textContent = w.t; d.appendChild(s); });
          caps.appendChild(d);
        });

        const tl = gsap.timeline({ paused: true });
        gsap.set(".kb", { scale: 1000 / 1080 });

        // ambient
        tl.fromTo("#bg-grid", { backgroundPosition: "0px 0px, 0px 0px" }, { backgroundPosition: "0px 216px, 0px 0px", duration: DUR, ease: "none" }, 0);
        tl.fromTo("#bg-glow", { opacity: 0.7, scale: 0.96 }, { opacity: 1, scale: 1.04, duration: DUR / 4, ease: "sine.inOut", repeat: 3, yoyo: true }, 0);

        // beat headlines — ENTRY rises with blur; the outgoing beat whips up + blurs (mirrored)
        BEATS.forEach(([id, t], i) => {
          tl.fromTo("#" + id, { opacity: 0, y: 70, filter: "blur(18px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }, t);
          const nx = BEATS[i + 1];
          if (nx) tl.to("#" + id, { opacity: 0, y: -70, filter: "blur(18px)", duration: 0.2667, ease: "power2.in" }, nx[1] - 0.2667);
        });
        tl.from("#b1 em", { scale: 1.35, duration: 0.4, ease: "back.out(2)" }, 0.55);

        // panel entrance + Ken Burns per segment
        tl.from("#panel", { y: 120, opacity: 0, scale: 0.94, duration: 0.6, ease: "power3.out" }, 0.05);
        for (let i = 0; i < SEGS.length - 1; i++) {
          tl.fromTo("#kb-inner", { scale: 1.0 }, { scale: 1.03, duration: SEGS[i + 1] - SEGS[i], ease: "none", immediateRender: false }, SEGS[i]);
        }

        // panel cuts — rotating flavors
        CUTS.forEach(([t, f]) => {
          if (f === "streak") {
            tl.fromTo("#streak", { x: -460, opacity: 1 }, { x: 1100, opacity: 1, duration: 0.4, ease: "power3.in", immediateRender: false }, t - 0.2);
            tl.set("#streak", { opacity: 0 }, t + 0.2);
            tl.fromTo(".kb", { filter: "blur(10px)" }, { filter: "blur(0px)", duration: 0.3, ease: "power2.out", immediateRender: false }, t);
          } else if (f === "push") {
            tl.fromTo("#kb-inner", { y: 60 }, { y: 0, duration: 0.45, ease: "expo.out", immediateRender: false }, t);
            tl.fromTo(".kb", { filter: "blur(8px)" }, { filter: "blur(0px)", duration: 0.35, ease: "power2.out", immediateRender: false }, t);
          } else if (f === "flash") {
            tl.fromTo("#flash", { opacity: 0 }, { opacity: 0.8, duration: 0.12, ease: "power2.in", immediateRender: false }, t - 0.12);
            tl.to("#flash", { opacity: 0, duration: 0.33, ease: "power2.out" }, t);
          } else {
            tl.fromTo("#panel", { scale: 1.03 }, { scale: 1, duration: 0.35, ease: "power3.out", immediateRender: false }, t);
          }
        });

        // chips
        CHIPS.forEach(([id, a, b]) => {
          tl.fromTo("#" + id, { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: 0.3, ease: "power2.out", immediateRender: false }, a);
          tl.to("#" + id, { opacity: 0, duration: 0.2, ease: "power1.in" }, Math.max(a + 0.35, b - 0.2));
        });

        // highlight boxes (+ optional tag)
        BOXES.forEach(([id, a, b, tag]) => {
          tl.fromTo("#" + id, { opacity: 0, scale: 1.08 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)", immediateRender: false }, a);
          if (tag) tl.fromTo("#" + id + "-tag", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.3, ease: "power3.out", immediateRender: false }, a + 0.2);
          if (b < DUR - 0.05) tl.to(tag ? ["#" + id, "#" + id + "-tag"] : "#" + id, { opacity: 0, duration: 0.2 }, Math.max(a + 0.4, b - 0.2));
        });

        // stamps — slam in with a slight tilt
        STAMPS.forEach(([id, t, b, rot]) => {
          tl.fromTo("#" + id, { opacity: 0, scale: 1.8, rotation: rot }, { opacity: 1, scale: 1, rotation: rot, duration: 0.3, ease: "back.out(1.8)", immediateRender: false }, t);
          if (b != null && b < DUR - 0.05) tl.to("#" + id, { opacity: 0, scale: 0.9, duration: 0.25, ease: "power2.in" }, Math.max(t + 0.5, b - 0.25));
        });

        // captions
        const capEls = caps.querySelectorAll(".cap");
        groups.forEach((grp, gi) => {
          const el = capEls[gi], a = Math.max(0, grp[0].s - 0.05), nxg = groups[gi + 1];
          const b = nxg ? Math.max(a + 0.2, nxg[0].s - 0.05) : Math.min(DUR, grp[grp.length - 1].e + 0.4);
          tl.fromTo(el, { opacity: 0, y: 18, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.12, ease: "power2.out", immediateRender: false }, a);
          tl.set(el, { opacity: 0 }, b);
          el.querySelectorAll(".w").forEach((sp, wi) => {
            const w = grp[wi];
            tl.to(sp, { color: "#37bdf8", scale: 1.05, duration: 0.08, ease: "power2.out" }, w.s);
            tl.to(sp, { color: "#ffffff", scale: 1, duration: 0.1, ease: "power1.out" }, Math.max(w.s + 0.1, Math.min(w.e, (grp[wi + 1] ? grp[wi + 1].s : b) - 0.02)));
          });
        });

        tl.set({}, {}, DUR); // duration anchor
        window.__timelines = window.__timelines || {};
        window.__timelines["${id}"] = tl;
      })();
    </script>
  </div>
</body>
</html>
`;
fs.writeFileSync(path.join(proj, 'index.html'), html);
console.log(`${id}: ${DUR}s, ${beats.length} beats, ${boxes.length} boxes, ${stamps.length} stamps, ${cuts.length} cuts`);
console.log('beats @', beats.map((b) => b.t.toFixed(2)).join(' '), '| boxes @', boxes.map((b) => `${b.a.toFixed(1)}-${b.b.toFixed(1)}`).join(' '));
