"""Generates compositions/ch7-code.html from the real Python files in code/ and the ch7 cue times.

Run from the project folder after any code or script change:
    python scripts/cues.py        # recompute narration timings (writes scripts/cues.json)
    python scripts/build_ch7.py   # rebuild the code chapter

Every file is shown in full with its real line numbers, so the video always matches the repo."""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PKG = ROOT / "code" / "ecommerce_agent"
LH = 29  # code line height (px)

# view id → (tab label, file)
FILES = [
    ("agent", "agent.py"),
    ("data", "data.py"),
    ("cat", "catalog_agent.py"),
    ("cart", "cart_agent.py"),
    ("ord", "order_agent.py"),
    ("init", "__init__.py"),
]
# extra token wraps: (file, line, text, css class) — lets the timeline glow a single token
TOKENS = [
    ("agent.py", 16, "tool_context: ToolContext", "tok-tc"),
    ("agent.py", 24, "root_agent", "tok-ra"),
]
KW = r"\b(def|return|if|not|in|from|import|for|del|True|False|None)\b"


def string_span(chunk):
    esc = html.escape(chunk, quote=False)
    esc = re.sub(r"\{([a-z_]+)\?\}", r'<span class="ph">{\1<span class="q">?</span>}</span>', esc)
    return '<span class="str">' + esc + "</span>"


def color_line(src, in_triple):
    """Tiny Python highlighter → (html, still_in_triple)."""
    out, i = [], 0
    while i < len(src):
        if in_triple or src.startswith('"""', i):
            start = i if in_triple else i + 3
            end = src.find('"""', start)
            chunk = src[i:] if end < 0 else src[i:end + 3]
            out.append(string_span(chunk))
            i += len(chunk)
            in_triple = end < 0
            continue
        if src[i] == '"' or (src[i] == "f" and src[i + 1:i + 2] == '"'):
            j = src.find('"', i + (2 if src[i] == "f" else 1))
            chunk = src[i:j + 1]
            out.append(string_span(chunk))
            i = j + 1
            continue
        if src[i] == "#":
            out.append('<span class="cm">' + html.escape(src[i:], quote=False) + "</span>")
            break
        tok = re.match(r"[A-Za-z_][A-Za-z_0-9]*|\s+|.", src[i:]).group(0)
        out.append('<span class="kw">' + tok + "</span>" if re.fullmatch(KW, tok) else html.escape(tok, quote=False))
        i += len(tok)
    return "".join(out), in_triple


def file_view(vid, fname):
    lines = (PKG / fname).read_text(encoding="utf-8").splitlines()
    rows, in_triple = [], False
    for n, src in enumerate(lines, 1):
        code, in_triple = color_line(src, in_triple)
        for f, ln, text, cls in TOKENS:
            if f == fname and ln == n:
                code = code.replace(html.escape(text, quote=False), f'<span class="{cls}">{html.escape(text, quote=False)}</span>', 1)
        rows.append(f'<div class="ln"><span class="no">{n}</span><span class="tx">{code}</span></div>')
    return (f'<div class="view code-view" id="v-{vid}" data-n="{len(lines)}"><div class="scroller" id="sc-{vid}">'
            f'<div class="band a" id="ba-{vid}"></div><div class="band b" id="bb-{vid}"></div>\n' + "\n".join(rows) + "\n</div></div>")


cues = json.loads((ROOT / "scripts" / "cues.json").read_text())
ch7 = next(c for c in cues["chapters"] if c["id"] == "ch7")
cue_map = {int(c["id"].split(".")[1]): c["start"] for c in ch7["cues"]}

views = "\n".join(file_view(v, f) for v, f in FILES)
tabs = "".join(f'<div class="tab" id="tab-{v}">{f}</div>' for v, f in FILES)
req = html.escape((ROOT / "code" / "requirements.txt").read_text(encoding="utf-8").strip(), quote=False)
env = html.escape((ROOT / "code" / ".env.example").read_text(encoding="utf-8").strip(), quote=False)
env = "\n".join(l for l in env.splitlines() if not l.startswith("#"))

out = (ROOT / "scripts" / "ch7-template.html").read_text(encoding="utf-8")
out = (out.replace("<!--TABS-->", tabs).replace("<!--VIEWS-->", views)
          .replace("__REQ__", req).replace("__ENV__", env)
          .replace("__LH__", str(LH)).replace("__DURATION__", str(ch7["duration"]))
          .replace("__CUES__", json.dumps(cue_map)))
(ROOT / "compositions" / "ch7-code.html").write_text(out, encoding="utf-8")
print(f"wrote compositions/ch7-code.html  (duration {ch7['duration']}s, {len(cue_map)} cues)")
