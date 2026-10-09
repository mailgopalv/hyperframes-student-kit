const fs = require('fs');
const path = require('path');
const PROJECT = path.resolve(__dirname, '..');
const segJs = fs.readFileSync(path.join(__dirname, 'segments.js'), 'utf8').trimEnd();

const template = `<template id="captions-template">
  <div data-composition-id="captions" data-start="0" data-width="1920" data-height="1080" data-duration="485">
    <div class="cap-stage" id="cap-stage"></div>

    <style>
      [data-composition-id="captions"] {
        position: absolute;
        inset: 0;
        pointer-events: none;
      }
      [data-composition-id="captions"] .cap-stage {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 92px;
        height: 0;
        pointer-events: none;
      }
      [data-composition-id="captions"] .cap-line-wrap {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        display: flex;
        justify-content: center;
        padding: 0 160px;
        opacity: 0;
        visibility: hidden;
      }
      [data-composition-id="captions"] .cap-line {
        display: inline-block;
        max-width: 1600px;
        text-align: center;
        font-family: "Montserrat", sans-serif;
        font-weight: 800;
        font-size: 50px;
        line-height: 1.2;
        letter-spacing: -0.005em;
        color: #ffffff;
        text-shadow:
          -3px -3px 0 #07121c,
          3px -3px 0 #07121c,
          -3px 3px 0 #07121c,
          3px 3px 0 #07121c,
          -4px 0 0 #07121c,
          4px 0 0 #07121c,
          0 -4px 0 #07121c,
          0 4px 0 #07121c,
          0 6px 16px rgba(0, 0, 0, 0.6);
        white-space: normal;
      }
      [data-composition-id="captions"] .cap-word {
        display: inline-block;
        transform-origin: center center;
        will-change: transform, color;
      }
    </style>

    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      (function () {
        const SEGMENTS = [
${segJs}
        ];

        const COMP_DURATION = 485;
        const DIM = "rgba(255,255,255,0.55)";
        const ACTIVE = "#37bdf8";
        const SPOKEN = "#ffffff";
        const ACTIVE_SCALE = 1.12;

        const stage = document.querySelector('[data-composition-id="captions"] #cap-stage');
        if (!stage) return;

        SEGMENTS.forEach(function (seg, segIdx) {
          const wrap = document.createElement("div");
          wrap.className = "cap-line-wrap";
          wrap.id = "cap-seg-" + segIdx;

          const line = document.createElement("div");
          line.className = "cap-line";

          seg.words.forEach(function (w, wIdx) {
            const span = document.createElement("span");
            span.className = "cap-word";
            span.id = "cap-w-" + segIdx + "-" + wIdx;
            span.textContent = w.word;
            line.appendChild(span);
            if (wIdx < seg.words.length - 1) {
              line.appendChild(document.createTextNode(" "));
            }
          });

          wrap.appendChild(line);
          stage.appendChild(wrap);
        });

        const tl = gsap.timeline({ paused: true });
        const FADE_IN = 0.16;
        const FADE_OUT = 0.16;
        const PRE_ROLL = 0.1;
        const POST_HOLD = 0.1;

        SEGMENTS.forEach(function (seg, segIdx) {
          const wrapSel = '[data-composition-id="captions"] #cap-seg-' + segIdx;
          const segStart = seg.words[0].start;
          const segEnd = seg.words[seg.words.length - 1].end;

          const fadeInAt = Math.max(segStart - PRE_ROLL, 0);
          const fadeOutAt = segEnd + POST_HOLD;
          const hideAt = fadeOutAt + FADE_OUT + 0.05;

          seg.words.forEach(function (w, wIdx) {
            const wordSel = '[data-composition-id="captions"] #cap-w-' + segIdx + "-" + wIdx;
            tl.set(wordSel, { color: DIM, scale: 1.0 }, fadeInAt);
          });

          tl.set(wrapSel, { visibility: "visible" }, fadeInAt);
          tl.fromTo(
            wrapSel,
            { opacity: 0, y: 8 },
            { opacity: 1, y: 0, duration: FADE_IN, ease: "power2.out" },
            fadeInAt,
          );

          seg.words.forEach(function (w, wIdx) {
            const wordSel = '[data-composition-id="captions"] #cap-w-' + segIdx + "-" + wIdx;
            tl.to(
              wordSel,
              { color: ACTIVE, scale: ACTIVE_SCALE, duration: 0.08, ease: "back.out(3)" },
              w.start,
            );
            tl.to(
              wordSel,
              { color: SPOKEN, scale: 1.0, duration: 0.12, ease: "power2.out" },
              w.end,
            );
          });

          tl.to(wrapSel, { opacity: 0, duration: FADE_OUT, ease: "power2.in" }, fadeOutAt);
          tl.set(wrapSel, { visibility: "hidden" }, hideAt);
        });

        tl.set({}, {}, COMP_DURATION);

        window.__timelines = window.__timelines || {};
        window.__timelines["captions"] = tl;
      })();
    </script>
  </div>
</template>
`;

fs.writeFileSync(path.join(PROJECT, 'compositions', 'captions.html'), template);
console.log('Wrote compositions/captions.html,', fs.statSync(path.join(PROJECT, 'compositions', 'captions.html')).size, 'bytes');
