"""Generates short1.html … short5.html (1080×1920 standalone compositions).

  python scripts/build_shorts.py          # build all
  python scripts/build_shorts.py 3        # build one

Timing source, per short k (chapter ch{k-1} in scripts/cues.json):
  * if assets/voiceover/short{k}.words.json exists (word-level transcript of the recorded take)
    → line starts + captions come from the recording, and <audio> uses assets/voiceover/short{k}.m4a
  * otherwise → scripted timing from cues.json, captions spread evenly over each line (silent preview)
"""
import difflib
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOLD = 2.5          # end-card hold after the last word
CAP_MAX = 24        # caption chunk: max characters
MAIN_TITLE = "Stop Building One Giant AI Agent. Use Sub-Agents Instead"

SHORTS = {
    1: {"kicker": "GOOGLE ADK · SUB-AGENTS", "hook": "1 Agent. 7 Jobs."},
    2: {"kicker": "GOOGLE ADK · HAND-OFFS", "hook": "How Agents Hand Off"},
    3: {"kicker": "GOOGLE ADK · TOOLCONTEXT", "hook": "The Parameter AI Never Sees"},
    4: {"kicker": "GOOGLE ADK · SESSION STATE", "hook": "4 Agents. 1 Notebook."},
    5: {"kicker": "GOOGLE ADK · QUICK START", "hook": "4 Commands"},
}

# words spoken a certain way → how captions should show them
CAPTION_FIXES = [
    ("tool underscore context", "tool_context"), ("tool context", "ToolContext"),
    ("transfer to agent", "transfer_to_agent"), ("sub agents equals", "sub_agents equals"), ("subagents equals", "sub_agents equals"),
    ("save customer details", "save_customer_details"),
    ("python dash m venv dot venv", "python -m venv .venv"),
    ("dot venv scripts activate", ".venv\\Scripts\\activate"), ("dot venv, scripts, activate", ".venv\\Scripts\\activate"),
    ("source dot venv slash bin slash activate", "source .venv/bin/activate"),
    ("pip install dash r requirements dot txt", "pip install -r requirements.txt"),
    ("dot env", ".env"), ("adk web", "adk web"), ("state dot get", "state.get"),
    ("subagents", "sub-agents"), ("gobal", "Gopal"), ("apa key", "API key"),
]


# ---------------------------------------------------------------- timing
def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def scripted_words(cues):
    words = []
    for c in cues:
        toks = c["text"].split()
        total = sum(len(t) + 1 for t in toks)
        t, span = c["start"], c["dur"]
        for tok in toks:
            d = span * (len(tok) + 1) / total
            words.append({"text": tok, "start": round(t, 3), "end": round(t + d * 0.92, 3)})
            t += d
    return words


def recorded(cues, words):
    """Line starts from the recording: first matched word of each line."""
    script, owner = [], []
    for i, c in enumerate(cues):
        for w in c["text"].split():
            script.append(norm(w)); owner.append(i)
    sm = difflib.SequenceMatcher(None, script, [norm(w["text"]) for w in words], autojunk=False)
    match = {a + k: b + k for a, b, n in sm.get_matching_blocks() for k in range(n)}
    starts = []
    for i in range(len(cues)):
        hits = [match[j] for j, o in enumerate(owner) if o == i and j in match]
        starts.append(words[hits[0]]["start"] if hits else None)
    for i, s in enumerate(starts):  # fill gaps
        if s is None:
            starts[i] = (starts[i - 1] + 2.0) if i else 0.2
    for i in range(1, len(starts)):
        starts[i] = max(starts[i], starts[i - 1] + 0.2)
    return starts


def fix_caption_words(words):
    for heard, show in CAPTION_FIXES:
        pat = [norm(w) for w in heard.split()]
        out, i = [], 0
        while i < len(words):
            seg = words[i:i + len(pat)]
            if len(seg) == len(pat) and [norm(w["text"]) for w in seg] == pat:
                tail = seg[-1]["text"][-1] if seg[-1]["text"][-1] in ",.?!:" else ""
                out.append({"text": show + tail, "start": seg[0]["start"], "end": seg[-1]["end"]}); i += len(pat)
            else:
                out.append(words[i]); i += 1
        words = out
    return words


def chunk_captions(words):
    chunks, cur = [], []
    for w in words:
        cand = " ".join(x["text"] for x in cur + [w])
        if cur and (len(cand) > CAP_MAX or w["start"] - cur[-1]["end"] > 0.5):
            chunks.append(cur); cur = []
        cur.append(w)
        if w["text"][-1] in ".?!," and len(" ".join(x["text"] for x in cur)) >= 10:
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    return chunks


# ---------------------------------------------------------------- shared shell
BASE_CSS = r"""
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #07121c; font-family: "Montserrat", sans-serif; color: #fff; }
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; }
.amb-base { position: absolute; inset: 0; background: radial-gradient(ellipse 90% 60% at 50% 35%, #10243a 0%, #0a1828 45%, #07121c 78%, #040a12 100%); }
.amb-grid { position: absolute; inset: -96px; background-image: linear-gradient(rgba(55,189,248,0.055) 1px, transparent 1px), linear-gradient(90deg, rgba(55,189,248,0.055) 1px, transparent 1px); background-size: 96px 96px; }
.amb-cross { position: absolute; inset: 0; width: 100%; height: 100%; opacity: 0.55; }
.amb-dot { position: absolute; width: 5px; height: 5px; border-radius: 50%; background: #37bdf8; box-shadow: 0 0 10px rgba(55,189,248,0.6); opacity: 0.5; }
.amb-grain { position: absolute; inset: 0; background-image: radial-gradient(circle at 20% 30%, rgba(255,255,255,0.03) 0.5px, transparent 0.5px), radial-gradient(circle at 60% 70%, rgba(255,255,255,0.02) 0.5px, transparent 0.5px); background-size: 3px 3px, 5px 5px; }
.amb-vig { position: absolute; inset: 0; background: radial-gradient(ellipse 100% 75% at 50% 45%, transparent 48%, rgba(4,10,18,0.6) 85%, rgba(4,10,18,0.9) 100%); }
.chrome { background: linear-gradient(180deg, #ffffff 0%, #9aa3ad 60%, #d0d6dc 100%); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 0 0 22px rgba(255,255,255,0.5), 0 0 44px rgba(255,255,255,0.25); }
.top { position: absolute; left: 60px; right: 60px; top: 120px; text-align: center; }
.kicker { font-family: "JetBrains Mono", monospace; font-size: 26px; letter-spacing: 0.22em; color: #37bdf8; }
.hook { margin-top: 18px; font-size: 76px; line-height: 1.05; font-weight: 900; letter-spacing: -0.02em; }
.stage { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
.caps { position: absolute; left: 50px; right: 50px; top: 1350px; height: 220px; }
.cap { position: absolute; left: 0; right: 0; top: 0; text-align: center; font-size: 60px; font-weight: 900; line-height: 1.15; opacity: 0;
  text-shadow: 0 4px 0 #04101b, 3px 0 0 #04101b, -3px 0 0 #04101b, 0 -3px 0 #04101b, 3px 3px 0 #04101b, -3px 3px 0 #04101b, 3px -3px 0 #04101b, -3px -3px 0 #04101b, 0 0 26px rgba(0,0,0,0.6); }
.cap span { display: inline-block; color: #ffffff; margin: 0 0.2em; }
.handle { position: absolute; left: 0; right: 0; bottom: 120px; text-align: center; font-family: "JetBrains Mono", monospace; font-size: 26px; letter-spacing: 0.16em; color: rgba(143,162,184,0.85); }
.handle b { color: #37bdf8; font-weight: 700; }

/* shared scene vocabulary */
.box { position: absolute; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; gap: 6px; border-radius: 20px;
  background: linear-gradient(180deg, #123a52 0%, #0c2638 100%); border: 2.5px solid rgba(55,189,248,0.65); box-shadow: 0 0 30px rgba(55,189,248,0.25); }
.box .n { font-family: "JetBrains Mono", monospace; font-weight: 700; color: #fff; }
.box .s { font-size: 24px; color: #b9c6d4; }
.chip { position: absolute; white-space: nowrap; font-family: "JetBrains Mono", monospace; font-size: 27px; font-weight: 500; color: #e2f5ff; padding: 10px 18px; border-radius: 12px;
  background: rgba(55,189,248,0.12); border: 2px solid rgba(55,189,248,0.6); }
.tag { position: absolute; white-space: nowrap; font-family: "JetBrains Mono", monospace; font-size: 22px; font-weight: 700; letter-spacing: 0.12em; padding: 5px 14px; border-radius: 8px; }
.pill { display: inline-block; font-size: 30px; font-weight: 800; color: #b9c6d4; padding: 12px 28px; border-radius: 40px; background: rgba(143,162,184,0.1); border: 2px solid rgba(143,162,184,0.35); }
.pills { position: absolute; left: 0; right: 0; top: 380px; display: flex; justify-content: center; gap: 22px; }
.code { position: absolute; font-family: "JetBrains Mono", monospace; font-variant-ligatures: none; color: #fff; padding: 26px 32px; border-radius: 18px;
  background: rgba(5,11,19,0.92); border: 2px solid rgba(143,162,184,0.35); box-shadow: 0 24px 60px rgba(0,0,0,0.5); white-space: pre; }
.code .k { color: #37bdf8; font-weight: 700; } .code .s { color: #8fd8fb; } .code .a { color: #f5a623; font-weight: 700; }
.card { position: absolute; border-radius: 22px; padding: 30px 34px; display: flex; flex-direction: column; gap: 14px; }
.card.blue { background: rgba(55,189,248,0.09); border: 2.5px solid rgba(55,189,248,0.65); }
.card.amber { background: rgba(245,166,35,0.09); border: 2.5px solid #f5a623; box-shadow: 0 0 40px rgba(245,166,35,0.2); }
.card .h { font-size: 34px; font-weight: 900; }
.card.blue .h { color: #37bdf8; } .card.amber .h { color: #f5a623; }
.card .m { font-family: "JetBrains Mono", monospace; font-variant-ligatures: none; font-size: 28px; line-height: 1.6; color: #fff; white-space: pre; }
.pulse { position: absolute; left: 0; top: 0; width: 30px; height: 30px; margin: -15px 0 0 -15px; border-radius: 50%; background: #fff; box-shadow: 0 0 22px #fff, 0 0 48px rgba(255,255,255,0.8); opacity: 0; z-index: 30; }
.lines { position: absolute; inset: 0; width: 100%; height: 100%; }
.lines path { fill: none; }

/* end card */
.end { position: absolute; left: 70px; right: 70px; top: 470px; display: flex; flex-direction: column; align-items: center; gap: 34px; text-align: center; opacity: 0; z-index: 40; }
.end .w { font-size: 84px; font-weight: 900; line-height: 1.05; }
.end .vid { width: 100%; border-radius: 26px; padding: 36px 40px; background: linear-gradient(160deg, rgba(18,58,82,0.95), rgba(12,38,56,0.95)); border: 2.5px solid #37bdf8; box-shadow: 0 0 60px rgba(55,189,248,0.35);
  display: flex; flex-direction: column; gap: 18px; align-items: center; }
.end .vid .t { font-size: 44px; font-weight: 900; line-height: 1.2; color: #fff; }
.end .vid .c { font-family: "JetBrains Mono", monospace; font-size: 26px; letter-spacing: 0.14em; color: #37bdf8; }
.end .arrow { font-size: 120px; font-weight: 900; color: #37bdf8; text-shadow: 0 0 40px rgba(55,189,248,0.8); line-height: 1; }
"""

AMBIENT = """
  <div class="amb-base"></div><div class="amb-grid" id="amb-grid"></div>
  <svg class="amb-cross" viewBox="0 0 1080 1920"><g stroke="rgba(55,189,248,0.4)" stroke-width="2">
    <path d="M80,90 h24 M92,78 v24"/><path d="M1000,90 h-24 M988,78 v24"/><path d="M80,1830 h24 M92,1818 v24"/><path d="M1000,1830 h-24 M988,1818 v24"/></g></svg>
  <div class="amb-dot" style="left:12%;top:20%"></div><div class="amb-dot" style="left:86%;top:16%"></div><div class="amb-dot" style="left:8%;top:58%"></div>
  <div class="amb-dot" style="left:92%;top:62%"></div><div class="amb-dot" style="left:30%;top:88%"></div><div class="amb-dot" style="left:72%;top:84%"></div>
  <div class="amb-grain"></div><div class="amb-vig"></div>
"""

HELPERS = r"""
  const q = (s) => document.querySelector(s);
  const qa = (s) => Array.from(document.querySelectorAll(s));
  const C = __CUES__;            // line number → start (s)
  const D = __DURATION__;
  const END = __ENDT__;          // end-card time
  const tl = gsap.timeline({ paused: true });
  const center = (els) => els.forEach((e) => gsap.set(e, { xPercent: -50, yPercent: -50 }));
  const pop = (sel, t, extra) => tl.fromTo(q(sel), { opacity: 0, y: 30, scale: 0.9 }, Object.assign({ opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "back.out(1.7)" }, extra || {}), t);
  const fadeOut = (sel, t, d) => tl.to(sel.startsWith ? qa(sel) : sel, { opacity: 0, duration: d || 0.3, ease: "power2.in" }, t);
  const travel = (pathSel, t, dur, reverse) => {
    const p = q(pathSel), len = p.getTotalLength(), pts = [];
    for (let i = 0; i <= 60; i++) { const pt = p.getPointAtLength(len * i / 60); pts.push([pt.x, pt.y]); }
    if (reverse) pts.reverse();
    tl.set("#pulse", { opacity: 1, x: pts[0][0], y: pts[0][1] }, t);
    tl.to("#pulse", { keyframes: { x: pts.map((p) => p[0]), y: pts.map((p) => p[1]), easeEach: "none" }, duration: dur, ease: "power2.inOut" }, t);
    tl.set("#pulse", { opacity: 0 }, t + dur + 0.05);
  };
  const draw = (sel, t, d) => { const p = q(sel), len = p.getTotalLength(); gsap.set(p, { strokeDasharray: len, strokeDashoffset: len }); tl.to(p, { strokeDashoffset: 0, duration: d || 0.5, ease: "power2.inOut" }, t); };
  const lit = (sel, on, t) => tl.to(qa(sel), on
      ? { opacity: 1, borderColor: "#ffffff", boxShadow: "0 0 50px rgba(255,255,255,0.45)", duration: 0.35, ease: "power2.out" }
      : { opacity: 0.35, borderColor: "rgba(55,189,248,0.5)", boxShadow: "0 0 0px rgba(0,0,0,0)", duration: 0.35, ease: "power2.out" }, t);
  const pillOn = (sel, t) => { tl.to(qa(".pill"), { color: "#b9c6d4", backgroundColor: "rgba(143,162,184,0.1)", borderColor: "rgba(143,162,184,0.35)", duration: 0.3 }, t);
                                tl.to(q(sel), { color: "#07121c", backgroundColor: "#37bdf8", borderColor: "#37bdf8", duration: 0.3, ease: "power2.out" }, t); };

  // ambient: grid drift, dot drift (finite repeats)
  tl.to("#amb-grid", { x: -96, y: -96, duration: 12, ease: "none", repeat: Math.ceil(D / 12) }, 0);
  qa(".amb-dot").forEach((d, i) => tl.to(d, { y: -30 - (i % 3) * 10, x: 14 * ((i % 2) ? 1 : -1), opacity: 0.85, duration: 4 + (i % 3), ease: "sine.inOut", yoyo: true, repeat: Math.ceil(D / (4 + (i % 3))) }, 0));

  // top: kicker + hook slam
  tl.from(".kicker", { y: -30, opacity: 0, duration: 0.4, ease: "power3.out" }, 0.05);
  tl.fromTo(".hook", { scale: 1.6, opacity: 0, filter: "blur(18px)" }, { scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }, 0.1);
  tl.from(".handle", { opacity: 0, duration: 0.6, ease: "power2.out" }, 0.6);

  // captions
  qa(".cap").forEach((c) => {
    const s = +c.dataset.s, e = +c.dataset.e;
    tl.set(c, { opacity: 1 }, s);
    tl.from(c, { scale: 0.85, y: 24, duration: 0.18, ease: "back.out(2.5)" }, s);
    tl.set(c, { opacity: 0 }, e);
    c.querySelectorAll("span").forEach((w) => {
      const ws = +w.dataset.s, we = +w.dataset.e;
      tl.to(w, { color: "#37bdf8", scale: 1.04, duration: 0.08, ease: "power2.out" }, ws);
      tl.to(w, { color: "#ffffff", scale: 1, duration: 0.1, ease: "power2.out" }, Math.max(we, ws + 0.12));
    });
  });

  // end card (shared): scene clears, "watch the full video"
  const endIn = () => {
    tl.to("#scene", { opacity: 0, filter: "blur(10px)", duration: 0.4, ease: "power2.in" }, END - 0.1);
    tl.to(".hook", { opacity: 0.25, duration: 0.4, ease: "power2.in" }, END - 0.1);
    tl.set("#end", { opacity: 1 }, END + 0.25);
    tl.from("#end .w", { scale: 1.5, opacity: 0, filter: "blur(16px)", duration: 0.5, ease: "expo.out" }, END + 0.25);
    tl.from("#end .vid", { y: 80, opacity: 0, duration: 0.6, ease: "back.out(1.5)" }, END + 0.6);
    tl.from("#end .arrow", { y: -40, opacity: 0, duration: 0.4, ease: "back.out(2)" }, END + 1.0);
    tl.to("#end .arrow", { y: 22, duration: 0.45, ease: "sine.inOut", yoyo: true, repeat: Math.max(1, Math.floor((D - END - 1.4) / 0.45)) }, END + 1.4);
  };
"""

# ---------------------------------------------------------------- per-short scenes
SCENES = {}

# ---------- Short 1: one giant agent → root + sub-agents
SCENES[1] = (r"""
  <div class="pills" id="pills"><span class="pill" id="p1">Problem</span><span class="pill" id="p2">Fix</span><span class="pill" id="p3">Code</span></div>
  <svg class="lines" viewBox="0 0 1080 1920">
    <path id="l1" d="M540,585 V650 H210 V705" stroke="#37bdf8" stroke-width="4" opacity="0.75"/>
    <path id="l2" d="M540,585 V705" stroke="#37bdf8" stroke-width="4" opacity="0.75"/>
    <path id="l3" d="M540,585 V650 H870 V705" stroke="#37bdf8" stroke-width="4" opacity="0.75"/>
  </svg>
  <div class="box" id="ag" style="left:540px;top:760px;width:560px;height:160px"><div class="n" style="font-size:40px">ecommerce_agent</div><div class="s" id="ag-s">one agent</div>
    <div class="tag" id="over" style="top:-22px;right:-24px;background:#e10b1f;color:#fff;box-shadow:0 0 24px rgba(225,11,31,.7)">OVERLOADED</div>
    <div class="tag" id="roottag" style="top:-20px;left:50%;transform:translateX(-50%);background:#37bdf8;color:#07121c">ROOT AGENT</div></div>
  <div class="box sub" id="s1" style="left:210px;top:760px;width:300px;height:110px"><div class="n" style="font-size:28px">catalog_agent</div></div>
  <div class="box sub" id="s2" style="left:540px;top:760px;width:300px;height:110px"><div class="n" style="font-size:28px">cart_agent</div></div>
  <div class="box sub" id="s3" style="left:870px;top:760px;width:300px;height:110px"><div class="n" style="font-size:28px">order_agent</div></div>
  <div class="chip" id="c1" style="left:300px;top:500px">save_customer_details()</div>
  <div class="chip" id="c2" style="left:800px;top:500px">list_products()</div>
  <div class="chip" id="c3" style="left:250px;top:610px">add_to_cart()</div>
  <div class="chip" id="c4" style="left:830px;top:610px">view_cart()</div>
  <div class="chip" id="c5" style="left:290px;top:920px">remove_from_cart()</div>
  <div class="chip" id="c6" style="left:800px;top:920px">confirm_cart()</div>
  <div class="chip" id="c7" style="left:540px;top:1030px">place_order()</div>
  <div class="tag" id="badge" style="left:540px;top:1140px;font-size:28px;background:rgba(225,11,31,.15);border:2px solid #e10b1f;color:#fff">7 tools · 1 giant instruction</div>
  <div class="code" id="code" style="left:540px;top:1150px;font-size:34px;line-height:1.5"><span class="a">sub_agents</span>=[catalog_agent,
           cart_agent, order_agent]</div>
""", r"""
  const chips = ["#c1","#c2","#c3","#c4","#c5","#c6","#c7"];
  center([q("#ag"), q("#s1"), q("#s2"), q("#s3"), q("#badge"), q("#code"), ...chips.map(q)]);
  gsap.set([q("#s1"), q("#s2"), q("#s3"), q("#code"), q("#badge"), q("#over"), q("#roottag"), q("#pills")], { opacity: 0 });
  gsap.set(qa(".lines path"), { opacity: 0 });
  // 1 — hook: the overloaded agent
  tl.fromTo("#ag", { scale: 0.4, opacity: 0, filter: "blur(14px)" }, { scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.6, ease: "back.out(1.6)" }, 0.25);
  // 2 — preview pills
  tl.to("#pills", { opacity: 1, duration: 0.01 }, C[2]);
  tl.from(qa(".pill"), { y: 30, opacity: 0, scale: 0.8, duration: 0.4, ease: "back.out(2)", stagger: 0.35 }, C[2]);
  pillOn("#p1", C[3]);
  // 3 — the tools pile on, one per tool named
  const home = { "#c1": [300,500], "#c2": [800,500], "#c3": [250,610], "#c4": [830,610], "#c5": [290,920], "#c6": [800,920], "#c7": [540,1030] };
  const span = (C[4] - C[3]) * 0.85;
  chips.forEach((id, i) => {
    const [x, y] = home[id], t = C[3] + 0.3 + i * span / 7;
    tl.from(id, { x: 540 - x, y: 760 - y, scale: 0.2, opacity: 0, duration: 0.45, ease: "power3.out" }, t);
    tl.to("#ag", { scale: 1.04, duration: 0.1, ease: "power2.out", yoyo: true, repeat: 1 }, t);
  });
  // 4 — 7 tools, 1 giant instruction → red
  tl.set("#ag-s", { textContent: "7 tools · 1 giant instruction" }, C[4]);
  tl.to("#ag", { borderColor: "#e10b1f", boxShadow: "0 0 60px rgba(225,11,31,0.6)", background: "linear-gradient(180deg,#3a1219 0%,#230b10 100%)", duration: 0.4 }, C[4] + 0.2);
  tl.to(qa(".chip"), { borderColor: "rgba(225,11,31,0.75)", backgroundColor: "rgba(225,11,31,0.12)", duration: 0.4, stagger: 0.04 }, C[4] + 0.2);
  // 5 — wrong tool, shake, OVERLOADED
  tl.fromTo("#c5", { scale: 1 }, { scale: 1.2, backgroundColor: "rgba(225,11,31,0.5)", duration: 0.18, yoyo: true, repeat: 3 }, C[5] + 0.6);
  tl.fromTo("#over", { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.5)" }, C[5] + 1.4);
  tl.to("#ag", { keyframes: { x: [0, -10, 10, -10, 10, -8, 8, -4, 4, 0] }, duration: 0.5, ease: "none" }, C[5] + 1.4);
  // 6 — the fix: same box turns blue, rises as ROOT, sub-agents arrive
  pillOn("#p2", C[6]);
  tl.to("#over", { opacity: 0, duration: 0.2 }, C[6]);
  tl.to("#ag", { borderColor: "rgba(55,189,248,0.65)", boxShadow: "0 0 30px rgba(55,189,248,0.25)", background: "linear-gradient(180deg,#123a52 0%,#0c2638 100%)", duration: 0.5 }, C[6]);
  tl.to(qa(".chip"), { borderColor: "rgba(55,189,248,0.6)", backgroundColor: "rgba(55,189,248,0.12)", duration: 0.5 }, C[6]);
  tl.set("#ag-s", { textContent: "the front desk" }, C[6] + 0.3);
  tl.to("#ag", { y: 520 - 760, scale: 0.8, duration: 0.8, ease: "power3.inOut" }, C[6] + 0.3);
  tl.to(chips.map(q), { opacity: 0, scale: 0.6, duration: 0.3, ease: "power2.in" }, C[6]);
  tl.fromTo("#roottag", { opacity: 0 }, { opacity: 1, duration: 0.3 }, C[6] + 1.1);
  ["#l1", "#l2", "#l3"].forEach((id, i) => { tl.set(id, { opacity: 0.75 }, C[6] + 1.2); draw(id, C[6] + 1.2 + i * 0.2, 0.45); });
  tl.fromTo([q("#s1"), q("#s2"), q("#s3")], { opacity: 0, y: 60, scale: 0.6 }, { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "back.out(1.6)", stagger: 0.3 }, C[6] + 1.6);
  // 7 — every tool flies to its owner
  const dest = { "#c1": [540,410], "#c2": [210,870], "#c3": [210,930], "#c4": [540,870], "#c5": [540,930], "#c6": [540,990], "#c7": [870,870] };
  tl.to("#pills", { opacity: 0, duration: 0.3 }, C[7] - 0.2);
  chips.forEach((id, i) => {
    const [hx, hy] = home[id], [dx, dy] = dest[id];
    tl.to(id, { x: dx - hx, y: dy - hy, scale: 0.85, opacity: 1, duration: 0.7, ease: "power3.inOut" }, C[7] + 0.2 + i * 0.25);
  });
  // 8 — the one line of code
  tl.fromTo("#code", { opacity: 0, y: 60, filter: "blur(10px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.6, ease: "expo.out" }, C[8] + 0.3);
  tl.fromTo("#code .a", { textShadow: "0 0 0px rgba(245,166,35,0)" }, { textShadow: "0 0 22px rgba(245,166,35,1)", duration: 0.4, yoyo: true, repeat: 5 }, C[8] + 1.2);
  tl.to([q("#s1"), q("#s3")], { y: -8, duration: 1.2, ease: "sine.inOut", yoyo: true, repeat: 3 }, C[8] + 1.0);
""")

# ---------- Short 2: hand-offs
SCENES[2] = (r"""
  <div class="pills" id="pills"><span class="pill" id="p1">1 · description</span><span class="pill" id="p2">2 · transfer</span><span class="pill" id="p3">3 · session</span></div>
  <svg class="lines" viewBox="0 0 1080 1920">
    <path class="tree" id="l1" d="M540,600 V660 H210 V705" stroke="#37bdf8" stroke-width="4" opacity="0.75"/>
    <path class="tree" id="l2" d="M540,600 V705" stroke="#37bdf8" stroke-width="4" opacity="0.75"/>
    <path class="tree" id="l3" d="M540,600 V660 H870 V705" stroke="#37bdf8" stroke-width="4" opacity="0.75"/>
    <path class="arc" id="a1" d="M210,815 Q375,900 540,815" stroke="rgba(55,189,248,0.55)" stroke-width="3" stroke-dasharray="8 8"/>
    <path id="m-down" d="M540,600 V660 H210 V705" stroke="none"/>
    <path id="m-up" d="M540,705 V600" stroke="none"/>
    <path class="link" d="M540,600 V560 H1030 V1150" stroke="rgba(245,166,35,.7)" stroke-width="3" stroke-dasharray="6 8"/>
    <path class="link" d="M210,815 V1095" stroke="rgba(245,166,35,.7)" stroke-width="3" stroke-dasharray="6 8"/>
    <path class="link" d="M540,815 V1095" stroke="rgba(245,166,35,.7)" stroke-width="3" stroke-dasharray="6 8"/>
    <path class="link" d="M870,815 V1095" stroke="rgba(245,166,35,.7)" stroke-width="3" stroke-dasharray="6 8"/>
  </svg>
  <div class="box ag" id="rootag" style="left:540px;top:540px;width:420px;height:120px"><div class="tag ctl" style="top:-20px;left:50%;transform:translateX(-50%);background:#fff;color:#07121c">IN CONTROL</div><div class="n" style="font-size:34px">ecommerce_agent</div></div>
  <div class="box ag" id="cat" style="left:210px;top:760px;width:300px;height:110px"><div class="tag ctl" style="top:-20px;left:50%;transform:translateX(-50%);background:#fff;color:#07121c">IN CONTROL</div><div class="n" style="font-size:28px">catalog_agent</div></div>
  <div class="box ag" id="cart" style="left:540px;top:760px;width:300px;height:110px"><div class="tag ctl" style="top:-20px;left:50%;transform:translateX(-50%);background:#fff;color:#07121c">IN CONTROL</div><div class="n" style="font-size:28px">cart_agent</div></div>
  <div class="box ag" id="ord" style="left:870px;top:760px;width:300px;height:110px"><div class="tag ctl" style="top:-20px;left:50%;transform:translateX(-50%);background:#fff;color:#07121c">IN CONTROL</div><div class="n" style="font-size:28px">order_agent</div></div>
  <div class="desc" id="d1" style="position:absolute;left:70px;top:860px;width:290px;font-size:23px;font-style:italic;color:#b9c6d4;line-height:1.35;border-left:4px solid rgba(55,189,248,.6);padding-left:12px">"Shows the products, adds picks to the cart"</div>
  <div class="desc" id="d2" style="position:absolute;left:400px;top:860px;width:290px;font-size:23px;font-style:italic;color:#b9c6d4;line-height:1.35;border-left:4px solid rgba(55,189,248,.6);padding-left:12px">"Shows the cart, adds or removes items"</div>
  <div class="desc" id="d3" style="position:absolute;left:730px;top:860px;width:290px;font-size:23px;font-style:italic;color:#b9c6d4;line-height:1.35;border-left:4px solid rgba(55,189,248,.6);padding-left:12px">"Confirms details, places the order"</div>
  <div class="dir" id="dl1" style="position:absolute;left:250px;top:610px;font-family:'JetBrains Mono',monospace;font-size:28px;font-weight:700;color:#fff;text-shadow:0 0 14px #fff">↓ down</div>
  <div class="dir" id="dl2" style="position:absolute;left:300px;top:880px;font-family:'JetBrains Mono',monospace;font-size:28px;font-weight:700;color:#fff;text-shadow:0 0 14px #fff">→ sideways</div>
  <div class="dir" id="dl3" style="position:absolute;left:560px;top:618px;font-family:'JetBrains Mono',monospace;font-size:28px;font-weight:700;color:#fff;text-shadow:0 0 14px #fff">↑ back up</div>
  <div class="chip" id="xfer" style="left:540px;top:1110px;font-size:30px;border-color:#fff;background:rgba(255,255,255,.08)"><b>transfer_to_agent</b>(<span style="color:#8fd8fb">"cart_agent"</span>)</div>
  <div class="card" id="slab" style="left:60px;right:60px;top:1100px;flex-direction:row;align-items:center;justify-content:space-between;background:rgba(18,58,82,.92);border:2.5px solid #f5a623;box-shadow:0 0 40px rgba(245,166,35,.25)">
    <div style="font-family:'JetBrains Mono',monospace;font-size:26px;font-weight:700;letter-spacing:.12em;line-height:1.3">ONE SHARED<br>SESSION</div>
    <div style="display:flex;flex-direction:column;gap:10px;font-family:'JetBrains Mono',monospace;font-size:26px">
      <div><b style="color:#37bdf8">events</b> same history</div><div><b style="color:#f5a623">state</b> same notebook</div></div></div>
""", r"""
  const boxes = ["#rootag", "#cat", "#cart", "#ord"];
  center([...boxes.map(q), q("#xfer")]);
  gsap.set([q("#pills"), q("#xfer"), q("#slab"), ...qa(".desc"), ...qa(".dir"), ...qa(".ctl"), ...qa(".link")], { opacity: 0 });
  gsap.set([q("#cart"), q("#ord")], { opacity: 0 });
  gsap.set(qa(".tree, .arc"), { opacity: 0 });
  const control = (id, t) => boxes.forEach((b) => {
    const on = b === id;
    lit(b, on, t);
    tl.to(q(b + " .ctl"), { opacity: on ? 1 : 0, duration: 0.25 }, t);
  });
  // 1 — hook: a hand-off between two agents
  tl.from("#rootag", { scale: 0.5, opacity: 0, duration: 0.5, ease: "back.out(1.6)" }, 0.2);
  tl.from("#cat", { scale: 0.5, opacity: 0, duration: 0.5, ease: "back.out(1.6)" }, 0.45);
  tl.set("#l1", { opacity: 0.75 }, 0.6); draw("#l1", 0.6, 0.4);
  control("#rootag", 0.8); travel("#m-down", 1.1, 0.8); control("#cat", 1.9);
  // 2 — three things
  tl.to("#pills", { opacity: 1, duration: 0.01 }, C[2]);
  tl.from(qa(".pill"), { y: 30, opacity: 0, scale: 0.8, duration: 0.4, ease: "back.out(2)", stagger: 0.4 }, C[2] + 0.2);
  tl.set(["#l2", "#l3"], { opacity: 0.75 }, C[2]); draw("#l2", C[2], 0.4); draw("#l3", C[2] + 0.2, 0.4);
  tl.fromTo([q("#cart"), q("#ord")], { opacity: 0, y: 40 }, { opacity: 0.35, y: 0, duration: 0.5, ease: "back.out(1.6)", stagger: 0.2 }, C[2] + 0.3);
  // 3 — descriptions; the LLM scans and picks one
  pillOn("#p1", C[3]);
  boxes.forEach((b) => lit(b, false, C[3]));
  tl.to(qa(".ctl"), { opacity: 0, duration: 0.2 }, C[3]);
  tl.fromTo(qa(".desc"), { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out", stagger: 0.3 }, C[3] + 0.6);
  ["#d1", "#d2", "#d3"].forEach((d, i) => tl.to(d, { color: "#ffffff", borderLeftColor: "#ffffff", duration: 0.2, yoyo: true, repeat: 1 }, C[3] + 2.6 + i * 0.4));
  tl.to("#d2", { color: "#ffffff", borderLeftColor: "#ffffff", duration: 0.3 }, C[3] + 3.9);
  lit("#cart", true, C[3] + 3.9);
  // 4 — transfer_to_agent
  pillOn("#p2", C[4]);
  tl.to(qa(".desc"), { opacity: 0, duration: 0.3 }, C[4]);
  tl.fromTo("#xfer", { opacity: 0, y: 30, scale: 0.9 }, { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "expo.out" }, C[4] + 0.4);
  // 5 — down, sideways, back up
  tl.set(".arc", { opacity: 1 }, C[5]);
  control("#rootag", C[5]);
  travel("#m-down", C[5] + 0.6, 0.8); tl.fromTo("#dl1", { opacity: 0 }, { opacity: 1, duration: 0.3 }, C[5] + 0.6); control("#cat", C[5] + 1.4);
  travel("#a1", C[5] + 2.4, 0.7); tl.fromTo("#dl2", { opacity: 0 }, { opacity: 1, duration: 0.3 }, C[5] + 2.4); control("#cart", C[5] + 3.1);
  travel("#m-up", C[5] + 4.2, 0.7); tl.fromTo("#dl3", { opacity: 0 }, { opacity: 1, duration: 0.3 }, C[5] + 4.2); control("#rootag", C[5] + 4.9);
  // 6 — only one in control
  tl.to(qa(".dir"), { opacity: 0, duration: 0.3 }, C[6]);
  control("#cart", C[6] + 0.2);
  tl.to("#cart .ctl", { scale: 1.25, duration: 0.25, yoyo: true, repeat: 3 }, C[6] + 0.6);
  // 7 — one shared session
  pillOn("#p3", C[7]);
  tl.to("#xfer", { opacity: 0, duration: 0.3 }, C[7]);
  boxes.forEach((b) => tl.to(b, { opacity: 1, borderColor: "rgba(55,189,248,0.65)", boxShadow: "0 0 30px rgba(55,189,248,0.25)", duration: 0.4 }, C[7] + 0.2));
  tl.to(qa(".ctl"), { opacity: 0, duration: 0.2 }, C[7] + 0.2);
  tl.fromTo("#slab", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 0.6, ease: "expo.out" }, C[7] + 0.4);
  tl.to(qa(".link"), { opacity: 1, duration: 0.4, stagger: 0.15 }, C[7] + 1.0);
  tl.to("#slab", { boxShadow: "0 0 70px rgba(245,166,35,0.5)", duration: 0.6, yoyo: true, repeat: 3 }, C[7] + 2.0);
""")

# ---------- Short 3: ToolContext
SCENES[3] = (r"""
  <div class="pills" id="pills"><span class="pill" id="p1">What</span><span class="pill" id="p2">Why</span><span class="pill" id="p3">The mistake</span></div>
  <div class="code" id="sig" style="left:540px;top:600px;font-size:32px;line-height:1.55"><span class="k">def</span> save_customer_details(
    name, email, phone,
    <span class="a" id="tc">tool_context: ToolContext</span>)</div>
  <div class="card blue" id="llm" style="left:60px;width:465px;top:780px;height:330px"><div class="h">What the LLM sees</div><div class="m">name
email
phone</div></div>
  <div class="card amber" id="fn" style="left:555px;width:465px;top:780px;height:330px"><div class="h">Your function gets</div><div class="m">name
email
phone
<b style="color:#f5a623">tool_context</b> ← ADK</div></div>
  <div class="card blue" id="rd" style="left:60px;right:60px;top:780px;flex-direction:row;align-items:center;gap:24px"><span class="tag" style="position:static;background:#37bdf8;color:#07121c;font-size:26px">READ</span><div class="m" style="font-size:31px">state.get(<span style="color:#f5a623">"cart"</span>, {})</div></div>
  <div class="card amber" id="wr" style="left:60px;right:60px;top:920px;flex-direction:row;align-items:center;gap:24px"><span class="tag" style="position:static;background:#f5a623;color:#07121c;font-size:26px">WRITE</span><div class="m" style="font-size:31px">state[<span style="color:#f5a623">"cart"</span>] = cart</div></div>
  <div class="card amber" id="sess" style="left:270px;right:270px;top:1080px;align-items:center;padding:22px"><div class="h" style="font-family:'JetBrains Mono',monospace;font-size:32px">session.state</div><div style="font-size:24px;color:#b9c6d4">saved by ADK ✓</div></div>
  <div class="card" id="bad" style="left:60px;right:60px;top:780px;flex-direction:row;align-items:center;gap:24px;background:rgba(225,11,31,.1);border:2.5px solid #e10b1f"><span style="font-size:46px;color:#e10b1f;font-weight:900">✕</span><div><div class="m" style="font-size:30px">cart["P-101"] = 1</div><div style="font-size:24px;color:#ffb3ba;margin-top:6px">changed in place: not saved</div></div></div>
  <div class="card amber" id="good" style="left:60px;right:60px;top:960px;flex-direction:row;align-items:center;gap:24px"><span style="font-size:46px;color:#f5a623;font-weight:900">✓</span><div><div class="m" style="font-size:30px">tool_context.state["cart"] = cart</div><div style="font-size:24px;color:#ffd08a;margin-top:6px">always assign it back</div></div></div>
""", r"""
  center([q("#sig")]);
  gsap.set([q("#pills"), q("#llm"), q("#fn"), q("#rd"), q("#wr"), q("#sess"), q("#bad"), q("#good")], { opacity: 0 });
  // 1 — hook: the hidden parameter
  tl.from("#sig", { y: 60, opacity: 0, duration: 0.6, ease: "expo.out" }, 0.25);
  tl.fromTo("#tc", { filter: "blur(12px)", opacity: 0.35 }, { filter: "blur(0px)", opacity: 1, duration: 0.6, ease: "power2.out" }, C[1] + 1.8);
  tl.to("#tc", { textShadow: "0 0 24px rgba(245,166,35,1)", duration: 0.4, yoyo: true, repeat: 3 }, C[1] + 2.3);
  // 2 — preview
  tl.to("#pills", { opacity: 1, duration: 0.01 }, C[2]);
  tl.from(qa(".pill"), { y: 30, opacity: 0, scale: 0.8, duration: 0.4, ease: "back.out(2)", stagger: 0.4 }, C[2] + 0.2);
  // 3 — what the LLM sees
  pillOn("#p1", C[3]);
  tl.to("#sig", { y: 460 - 600, scale: 0.85, duration: 0.6, ease: "power3.inOut" }, C[3]);
  tl.to("#pills", { y: -40, opacity: 0, duration: 0.3 }, C[3]);
  tl.fromTo("#llm", { opacity: 0, x: -60 }, { opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }, C[3] + 1.4);
  // 4 — what your function gets
  tl.fromTo("#fn", { opacity: 0, x: 60 }, { opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }, C[4] + 0.4);
  tl.fromTo("#fn b", { textShadow: "0 0 0px rgba(245,166,35,0)" }, { textShadow: "0 0 20px rgba(245,166,35,1)", duration: 0.4, yoyo: true, repeat: 3 }, C[4] + 2.0);
  // 5 — read / write
  tl.to([q("#llm"), q("#fn")], { opacity: 0, y: -30, duration: 0.3, ease: "power2.in" }, C[5]);
  tl.fromTo("#rd", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.45, ease: "back.out(1.6)" }, C[5] + 1.6);
  tl.fromTo("#wr", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.45, ease: "back.out(1.6)" }, C[5] + 3.8);
  // 6 — ADK saves every write
  tl.fromTo("#sess", { opacity: 0, scale: 0.7 }, { opacity: 1, scale: 1, duration: 0.5, ease: "back.out(2)" }, C[6] + 0.3);
  tl.to("#sess", { boxShadow: "0 0 70px rgba(245,166,35,0.55)", duration: 0.5, yoyo: true, repeat: 3 }, C[6] + 0.9);
  // 7 — the mistake
  pillOn("#p3", C[7]);
  tl.to("#pills", { y: 0, opacity: 1, duration: 0.3 }, C[7]);
  tl.to("#sig", { opacity: 0, duration: 0.3 }, C[7]);
  tl.to([q("#rd"), q("#wr"), q("#sess")], { opacity: 0, duration: 0.3 }, C[7]);
  tl.fromTo("#bad", { opacity: 0, x: -60 }, { opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }, C[7] + 0.5);
  tl.to("#bad", { keyframes: { x: [0, -8, 8, -8, 8, -4, 4, 0] }, duration: 0.4, ease: "none" }, C[7] + 1.2);
  tl.fromTo("#good", { opacity: 0, x: 60 }, { opacity: 1, x: 0, duration: 0.45, ease: "back.out(1.6)" }, C[7] + 2.6);
  tl.to("#good", { boxShadow: "0 0 60px rgba(245,166,35,0.5)", duration: 0.5, yoyo: true, repeat: 3 }, C[7] + 3.2);
""")

# ---------- Short 4: state grows
SCENES[4] = (r"""
  <svg class="lines" viewBox="0 0 1080 1920"><path id="row" d="M165,440 H915" stroke="rgba(55,189,248,.5)" stroke-width="3" stroke-dasharray="8 8"/>
    <path id="r12" d="M165,440 H415" stroke="none"/><path id="r23" d="M415,440 H665" stroke="none"/><path id="r34" d="M665,440 H915" stroke="none"/></svg>
  <div class="box ag" id="a1" style="left:165px;top:440px;width:220px;height:90px"><div class="n" style="font-size:26px">root</div></div>
  <div class="box ag" id="a2" style="left:415px;top:440px;width:220px;height:90px"><div class="n" style="font-size:26px">catalog</div></div>
  <div class="box ag" id="a3" style="left:665px;top:440px;width:220px;height:90px"><div class="n" style="font-size:26px">cart</div></div>
  <div class="box ag" id="a4" style="left:915px;top:440px;width:220px;height:90px"><div class="n" style="font-size:26px">order</div></div>
  <div class="card amber" id="panel" style="left:60px;right:60px;top:540px;height:740px;padding:26px 30px;gap:10px">
    <div class="h" style="font-family:'JetBrains Mono',monospace;font-size:32px;display:flex;justify-content:space-between">session.state <span id="empty" style="color:#f5a623">{ }</span></div>
    <div class="r" id="k1"><span>user_name</span><b>"Asha"</b><i>root</i></div>
    <div class="r" id="k2"><span>user_email</span><b>"asha@example.com"</b><i>root</i></div>
    <div class="r" id="k3"><span>user_phone</span><b>"555-0101"</b><i>root</i></div>
    <div class="r" id="k4"><span>cart</span><b class="cv"><em id="v1">{P-101: 1, P-103: 2}</em><em id="v2">{P-101: 1}</em><em id="v3">{P-101: 1, P-104: 1}</em></b><i>catalog · cart</i></div>
    <div class="r" id="k5"><span>cart_total</span><b>99.98</b><i>cart</i></div>
    <div class="r" id="k6"><span>cart_confirmed</span><b>true</b><i>cart</i></div>
    <div class="r" id="k7"><span>order_id</span><b>"ORD-7F3A2C"</b><i>order</i></div>
    <div class="r" id="k8"><span>order_status</span><b>"placed"</b><i>order</i></div>
  </div>
  <style>
    .r { display: grid; grid-template-columns: 250px 1fr; grid-template-rows: auto auto; padding: 10px 16px; border-radius: 12px; background: rgba(245,166,35,0.08); border: 1.5px solid rgba(245,166,35,0.45); opacity: 0; font-family: "JetBrains Mono", monospace; font-variant-ligatures: none; }
    .r span { font-size: 26px; font-weight: 700; color: #f5a623; } .r b { font-size: 26px; font-weight: 500; color: #fff; position: relative; height: 34px; }
    .r i { grid-column: 2; font-style: normal; font-size: 19px; color: #8fa2b8; }
    .cv em { position: absolute; left: 0; top: 0; font-style: normal; opacity: 0; white-space: nowrap; }
  </style>
""", r"""
  const ags = ["#a1", "#a2", "#a3", "#a4"];
  center(ags.map(q));
  gsap.set(ags.map(q), { opacity: 0.35 });
  const control = (id, t) => ags.forEach((a) => lit(a, a === id, t));
  const row = (id, t) => { tl.fromTo(id, { opacity: 0, x: 60 }, { opacity: 1, x: 0, duration: 0.45, ease: "expo.out" }, t);
                           tl.fromTo(id, { backgroundColor: "rgba(245,166,35,0.55)" }, { backgroundColor: "rgba(245,166,35,0.08)", duration: 1.0 }, t + 0.1); };
  const flash = (id, t, c) => tl.fromTo(id, { backgroundColor: c || "rgba(245,166,35,0.55)" }, { backgroundColor: "rgba(245,166,35,0.08)", duration: 1.0 }, t);
  // 1 — hook: four agents, one notebook
  tl.from(ags.map(q), { y: -40, opacity: 0, duration: 0.45, ease: "back.out(1.8)", stagger: 0.12 }, 0.2);
  tl.from("#panel", { y: 80, opacity: 0, duration: 0.6, ease: "expo.out" }, 0.6);
  tl.from("#row", { opacity: 0, duration: 0.4 }, 0.9);
  // 2 — empty state
  tl.fromTo("#empty", { scale: 1 }, { scale: 1.4, duration: 0.3, yoyo: true, repeat: 1 }, C[2] + 0.4);
  // 3 — root saves 3 keys, hands to catalog, cart appears
  control("#a1", C[3]);
  tl.to("#empty", { opacity: 0, duration: 0.3 }, C[3] + 1.5);
  const s3 = C[4] - C[3];
  row("#k1", C[3] + s3 * 0.38); row("#k2", C[3] + s3 * 0.38 + 0.3); row("#k3", C[3] + s3 * 0.38 + 0.6);
  travel("#r12", C[3] + s3 * 0.62, 0.6); control("#a2", C[3] + s3 * 0.62 + 0.6);
  row("#k4", C[3] + s3 * 0.86); tl.set("#v1", { opacity: 1 }, C[3] + s3 * 0.86);
  // 4 — cart edits, back to catalog, back again
  travel("#r23", C[4] + 0.2, 0.6); control("#a3", C[4] + 0.8);
  tl.set("#v1", { opacity: 0 }, C[4] + 1.6); tl.set("#v2", { opacity: 1 }, C[4] + 1.6); flash("#k4", C[4] + 1.6);
  travel("#r23", C[4] + 2.6, 0.6, true); control("#a2", C[4] + 3.2);
  tl.set("#v2", { opacity: 0 }, C[4] + 3.8); tl.set("#v3", { opacity: 1 }, C[4] + 3.8); flash("#k4", C[4] + 3.8);
  travel("#r23", C[4] + 4.4, 0.6); control("#a3", C[4] + 5.0);
  // 5 — total + confirmed
  row("#k5", C[5] + 1.6); row("#k6", C[5] + 2.4);
  // 6 — order agent reads email/phone, writes id + status
  travel("#r34", C[6] + 0.2, 0.6); control("#a4", C[6] + 0.8);
  flash("#k2", C[6] + 2.2, "rgba(55,189,248,0.55)"); flash("#k3", C[6] + 2.5, "rgba(55,189,248,0.55)");
  row("#k7", C[6] + 5.0); row("#k8", C[6] + 5.6);
  // 7 — eight keys, four agents, one session
  ags.forEach((a, i) => { lit(a, true, C[7] + i * 0.35); });
  ["#k1","#k2","#k3","#k4","#k5","#k6","#k7","#k8"].forEach((k, i) => flash(k, C[7] + 0.2 + i * 0.18));
  tl.to("#panel", { boxShadow: "0 0 70px rgba(245,166,35,0.45)", duration: 0.6, yoyo: true, repeat: 1 }, C[7] + 1.2);
""")

# ---------- Short 5: four commands
SCENES[5] = (r"""
  <div class="steps" id="steps">
    <div class="st" id="st1"><div class="num">1</div><div class="body"><div class="tt">Set up</div><div class="cmd" id="cmd1a">python -m venv .venv</div>
      <div class="cmd sm" id="cmd1b">.venv\Scripts\activate <i>Windows</i></div><div class="cmd sm" id="cmd1c">source .venv/bin/activate <i>Mac / Linux</i></div></div></div>
    <div class="st" id="st2"><div class="num">2</div><div class="body"><div class="tt">Install</div><div class="cmd" id="cmd2">pip install -r requirements.txt</div></div></div>
    <div class="st" id="st3"><div class="num">3</div><div class="body"><div class="tt">Add your key</div><div class="cmd" id="cmd3">.env → GOOGLE_API_KEY=…</div></div></div>
    <div class="st" id="st4"><div class="num">4</div><div class="body"><div class="tt">Run</div><div class="cmd" id="cmd4">adk web → localhost:8000</div></div></div>
  </div>
  <style>
    .steps { position: absolute; left: 60px; right: 60px; top: 380px; display: flex; flex-direction: column; gap: 22px; }
    .st { display: flex; gap: 26px; align-items: flex-start; padding: 26px 28px; border-radius: 20px; background: rgba(143,162,184,0.07); border: 2px solid rgba(143,162,184,0.3); opacity: 0.35; }
    .num { flex: none; width: 70px; height: 70px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 38px; font-weight: 900; color: #07121c; background: #8fa2b8; }
    .body { display: flex; flex-direction: column; gap: 12px; min-width: 0; }
    .tt { font-size: 38px; font-weight: 900; color: #fff; }
    .cmd { font-family: "JetBrains Mono", monospace; font-variant-ligatures: none; font-size: 31px; color: #8fd8fb; white-space: nowrap; opacity: 0; }
    .cmd.sm { font-size: 26px; color: #d0e6f2; } .cmd i { font-family: "Montserrat", sans-serif; font-style: normal; font-size: 19px; font-weight: 800; color: #07121c; background: #8fa2b8; padding: 2px 10px; border-radius: 6px; margin-left: 8px; }
  </style>
""", r"""
  const stepOn = (i, t) => {
    tl.to(qa(".st"), { opacity: 0.35, borderColor: "rgba(143,162,184,0.3)", boxShadow: "0 0 0px rgba(0,0,0,0)", duration: 0.3 }, t);
    tl.to(qa(".num"), { backgroundColor: "#8fa2b8", duration: 0.3 }, t);
    tl.to("#st" + i, { opacity: 1, borderColor: "#37bdf8", boxShadow: "0 0 40px rgba(55,189,248,0.35)", duration: 0.35, ease: "power2.out" }, t);
    tl.to("#st" + i + " .num", { backgroundColor: "#37bdf8", scale: 1.15, duration: 0.25, yoyo: true, repeat: 1 }, t);
  };
  const type = (sel, t) => tl.fromTo(sel, { opacity: 0, x: -24 }, { opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }, t);
  // 1 — hook: the four steps appear
  tl.from(qa(".st"), { x: -80, opacity: 0, duration: 0.45, ease: "back.out(1.6)", stagger: 0.18 }, 0.3);
  // 2 — set up, install, key, run: each title flashes as named
  [1, 2, 3, 4].forEach((i) => tl.to("#st" + i + " .tt", { color: "#37bdf8", duration: 0.15, yoyo: true, repeat: 1 }, C[2] + 0.3 + (i - 1) * 0.6));
  // 3 — python -m venv .venv
  stepOn(1, C[3]); type("#cmd1a", C[3] + 0.3);
  // 4 — activate (Windows, Mac/Linux)
  type("#cmd1b", C[4] + 0.8); type("#cmd1c", C[4] + 3.2);
  // 5 — pip install
  stepOn(2, C[5]); type("#cmd2", C[5] + 0.4);
  // 6 — .env key
  stepOn(3, C[6]); type("#cmd3", C[6] + 0.6);
  // 7 — adk web
  stepOn(4, C[7]); type("#cmd4", C[7] + 0.5);
  tl.to(qa(".st"), { opacity: 1, borderColor: "#37bdf8", duration: 0.4, stagger: 0.12 }, C[7] + 2.4);
  tl.to(qa(".num"), { backgroundColor: "#37bdf8", duration: 0.3, stagger: 0.12 }, C[7] + 2.4);
""")

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080, height=1920">
<title>Short __K__: __TITLE__</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=block" rel="stylesheet">
<style>__CSS__</style>
</head>
<body>
<!-- GENERATED by scripts/build_shorts.py. Edit the generator, not this file. -->
<div id="root" data-composition-id="__ID__" data-start="0" data-width="1080" data-height="1920" data-duration="__DURATION__">
__AMBIENT__
  <div class="top"><div class="kicker">__KICKER__</div><div class="hook chrome">__HOOK__</div></div>
  <div class="stage" id="scene">
__SCENE__
  </div>
  <div class="pulse" id="pulse"></div>
  <div class="end" id="end">
    <div class="w chrome">Watch the full video</div>
    <div class="vid"><div class="t">__MAIN_TITLE__</div><div class="c">EXPLORE AI WITH GOPAL</div></div>
    <div class="arrow">↓</div>
  </div>
  <div class="caps">
__CAPTIONS__
  </div>
  <div class="handle">@ <b>Explore AI with Gopal</b></div>
__AUDIO__
</div>
<script>
(function () {
__HELPERS__
__SCENE_JS__
  endIn();
  tl.to({}, { duration: D }, 0);
  window.__timelines = window.__timelines || {};
  window.__timelines["__ID__"] = tl;
})();
</script>
</body>
</html>
"""


def build(k):
    cues_all = json.loads((ROOT / "scripts" / "cues.json").read_text(encoding="utf-8"))
    ch = cues_all["chapters"][k - 1]
    cues = ch["cues"]
    wfile = ROOT / "assets" / "voiceover" / f"short{k}.words.json"
    audio = ROOT / "assets" / "voiceover" / f"short{k}.m4a"
    if wfile.exists():
        words = [{"text": w["text"], "start": float(w["start"]), "end": float(w["end"])} for w in json.loads(wfile.read_text(encoding="utf-8"))]
        starts = recorded(cues, words)
        source = "recorded"
    else:
        words = scripted_words(cues)
        starts = [c["start"] for c in cues]
        source = "scripted"
    last_line = len(cues)
    end_t = starts[-1]                                  # end card lands with the "watch the full video" line
    duration = round(max(words[-1]["end"] + HOLD, end_t + 4.0), 2)
    cap_words = fix_caption_words(words)
    caps = []
    chunks = chunk_captions(cap_words)
    for i, ck in enumerate(chunks):
        s = ck[0]["start"]
        e = chunks[i + 1][0]["start"] if i + 1 < len(chunks) else ck[-1]["end"] + 0.4
        e = min(e, ck[-1]["end"] + 0.8)
        spans = "".join(f'<span data-s="{w["start"]:.2f}" data-e="{w["end"]:.2f}">{html.escape(w["text"])}</span>' for w in ck)
        caps.append(f'    <div class="cap" data-s="{s:.2f}" data-e="{e:.2f}">{spans}</div>')
    cue_map = {i + 1: round(s, 2) for i, s in enumerate(starts)}
    scene_html, scene_js = SCENES[k]
    audio_tag = (f'  <audio id="vo" src="assets/voiceover/short{k}.m4a" data-start="0" data-duration="{duration}" data-track-index="2" data-volume="1"></audio>'
                 if audio.exists() else "  <!-- no voiceover yet: assets/voiceover/short%d.m4a -->" % k)
    title = ch["title"].split(":", 1)[-1].strip()
    out = (PAGE.replace("__CSS__", BASE_CSS).replace("__AMBIENT__", AMBIENT).replace("__HELPERS__", HELPERS)
           .replace("__SCENE__", scene_html).replace("__SCENE_JS__", scene_js)
           .replace("__CAPTIONS__", "\n".join(caps)).replace("__AUDIO__", audio_tag)
           .replace("__CUES__", json.dumps(cue_map)).replace("__DURATION__", str(duration)).replace("__ENDT__", str(round(end_t, 2)))
           .replace("__ID__", f"short{k}").replace("__K__", str(k)).replace("__TITLE__", html.escape(title))
           .replace("__KICKER__", SHORTS[k]["kicker"]).replace("__HOOK__", SHORTS[k]["hook"]).replace("__MAIN_TITLE__", MAIN_TITLE))
    # each short is its own HyperFrames project: short{k}/index.html (+ hyperframes.json, meta.json, assets/)
    proj = ROOT / f"short{k}"
    (proj / "assets" / "voiceover").mkdir(parents=True, exist_ok=True)
    (proj / "renders").mkdir(exist_ok=True)
    (proj / "hyperframes.json").write_text((ROOT / "hyperframes.json").read_text(encoding="utf-8"), encoding="utf-8")
    (proj / "meta.json").write_text(json.dumps({"id": f"multi-agents-short{k}", "name": f"Agent with Sub-Agents: Short {k}: {title}",
                                                "createdAt": "2026-10-01T00:00:00.000Z", "width": 1080, "height": 1920, "fps": 30}, indent=2), encoding="utf-8")
    if audio.exists():
        (proj / "assets" / "voiceover" / audio.name).write_bytes(audio.read_bytes())
    (proj / "index.html").write_text(out, encoding="utf-8")
    print(f"short{k}/index.html  {duration:5.1f}s  {source:8}  {len(chunks)} captions  end card at {end_t:.1f}s")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for k in ([int(a) for a in sys.argv[1:]] or [1, 2, 3, 4, 5]):
        build(k)
