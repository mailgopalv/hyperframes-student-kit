"""Build an .srt for the edited video from its word-level transcript.

  python scripts/make_srt.py renders/v2/transcript.json renders/multi-agents-draft-v2.srt

Keeps what was actually said (ad-libs included), fixes words the recogniser misheard, and writes
code terms the way they appear on screen (tool_context, agent.py, pip install -r requirements.txt).
"""
import json
import re
import sys

MAX_LINE, MAX_LINES, MAX_DUR, MIN_DUR, GAP_BREAK = 42, 2, 6.0, 1.0, 0.6

# (heard, write) — matched case-insensitively on words, ignoring punctuation. Order matters (longer first).
FIXES = [
    # misheard words
    ("Every tool calls and two results", "Even tool calls and tool results"),
    ("key value pass", "key-value pairs"),
    ("The model states picking", "The model starts picking"),
    ("in code that just one line subagents equals", "In code, that's just one line: sub_agents equals"),
    ("The root agent e-commerce agent is like a friend desk", "The root agent, ecommerce_agent, is like a front desk"),
    ("Controls can move done", "Control can move down"),
    ("the agent and control", "the agent in control"),
    ("shares a name", "shares her name"),
    ("Three keys appears", "Three keys appear"),
    ("wants to see charges now", "wants to see chargers now"),
    ("adds phone charges", "adds a phone charger"),
    ("places order at the last two keys", "place_order adds the last two keys"),
    ("That's the old idea", "That's the whole idea"),
    ("readme.md file", "README.md file"),
    ("It's docstring, that's what it matters", "Its docstring, that's what matters"),
    ("Your tool underscore context, a tool", "Without tool_context, a tool"),
    ("only need state A, that is where", "only need state, that is where"),
    ("Read the customer", "Greet the customer"),
    ("Tools list the root agent's own tools and sub-agents list", "tools lists the root agent's own tool, and sub_agents lists"),
    ("That's one line turns", "That one line turns"),
    ("Add to cart doesn't need it", "add_to_cart does need it"),
    ("reads the cart from state as the quantity", "reads the cart from state, adds the quantity"),
    ("Having the dictionary in place is enough", "Changing the dictionary in place isn't enough"),
    ("Its instruction puts the name", "Its instruction pulls the name"),
    ("your visual environment", "your virtual environment"),
    ("Create dot venv.example file and create dot venv file", "Copy .env.example and create a .env file"),
    ("Gemini APA key from Google AI studio", "Gemini API key from Google AI Studio"),
    ("once this is all set, undone", "once this is all set and done"),
    ("like I'm interested", "like \"I'm interested\""),
    ("explore AI with Gobal", "Explore AI with Gopal"),
    ("see you the next one", "see you in the next one"),
    ("normal Python function. The agent can call", "normal Python function the agent can call"),
    # commands & file names, written as they appear on screen
    ("python dash m, venv dot venv", "python -m venv .venv"),
    ("dot venv script activate", ".venv\\Scripts\\activate"),
    ("source dot venv slash bin slash activate", "source .venv/bin/activate"),
    ("starts with dot venv", "starts with (.venv)"),
    ("called dot venv", "called .venv"),
    ("pip install dash or requirements dot txt", "pip install -r requirements.txt"),
    ("run ADK web", "run adk web"),
    ("State dot get, write does too, state key equals value", "state.get(). Writing does too: state[key] = value"),
    ("tool underscore context dot state", "tool_context.state"),
    ("tool underscore context", "tool_context"),
    ("root underscore agent", "root_agent"),
    ("of type tool context", "of type ToolContext"),
    ("type hint, tool context", "type hint, ToolContext"),
    ("import agent and tool context from ADK", "import Agent and ToolContext from ADK"),
    ("Next catalog agent dot py", "Next, catalog_agent.py"),
    ("cart agent dot py", "cart_agent.py"),
    ("order agent dot py", "order_agent.py"),
    ("init dot py", "__init__.py"),
    ("data dot py", "data.py"),
    ("one folder, e-commerce agent", "one folder, ecommerce_agent"),
    ("pick ecommerce agent", "pick ecommerce_agent"),
    # tool / function names
    ("calls, save customer details", "calls save_customer_details"),
    ("save customer details", "save_customer_details"),
    ("calls, add to cart", "calls add_to_cart"),
    ("reuses add to cart", "reuses add_to_cart"),
    ("List products has", "list_products has"),
    ("View cart reads", "view_cart reads"),
    ("remove from cart, deletes", "remove_from_cart deletes"),
    ("calls confirm cart", "calls confirm_cart"),
    ("Confirm cart saves", "confirm_cart saves"),
    ("place order first reads cart confirmed", "place_order first reads cart_confirmed"),
    ("transfer to agent", "transfer_to_agent"),
    # spelling
    ("subagents", "sub-agents"),
    ("subagent", "sub-agent"),
]

PUNCT = ",.?!:;"


def key(w):
    return re.sub(r"[^\w'.\-]", "", w.lower()).strip(".")


def apply_fixes(words):
    for heard, write in FIXES:
        pat = [key(w) for w in heard.split()]
        rep = write.split()
        i, out = 0, []
        while i < len(words):
            seg = words[i:i + len(pat)]
            if len(seg) == len(pat) and [key(w["text"]) for w in seg] == pat:
                t0, t1 = seg[0]["start"], seg[-1]["end"]
                tail = seg[-1]["text"][-1] if seg[-1]["text"][-1] in PUNCT else ""
                new = list(rep)
                if tail and new[-1][-1] not in PUNCT + '"':
                    new[-1] += tail
                for k, w in enumerate(new):
                    a = t0 + (t1 - t0) * k / len(new)
                    out.append({"text": w, "start": a, "end": t0 + (t1 - t0) * (k + 1) / len(new)})
                i += len(pat)
            else:
                out.append(words[i]); i += 1
        words = out
    return words


def wrap(text):
    if len(text) <= MAX_LINE:
        return [text]
    ws = text.split()
    best = None
    for k in range(1, len(ws)):  # most balanced split into two lines
        a, b = " ".join(ws[:k]), " ".join(ws[k:])
        score = max(len(a), len(b))
        if best is None or score < best[0]:
            best = (score, [a, b])
    return best[1]


def fits(text):
    return all(len(l) <= MAX_LINE for l in wrap(text)) and len(wrap(text)) <= MAX_LINES


NO_BREAK_AFTER = {"pip", "install", "-r", "python", "-m", "source", "run", "the", "a", "an", "to", "of", "and"}


def text_of(ws):
    return " ".join(x["text"] for x in ws)


def ok(ws):
    return fits(text_of(ws)) and ws[-1]["end"] - ws[0]["start"] <= MAX_DUR


def split_chunk(ws):
    """Split a sentence into caption-sized pieces, preferring commas and balanced halves."""
    if ok(ws) or len(ws) == 1:
        return [ws]
    best = None
    total = len(text_of(ws))
    for k in range(1, len(ws)):
        left, right = ws[:k], ws[k:]
        prev = left[-1]["text"]
        if prev.lower().strip(",") in NO_BREAK_AFTER:
            continue
        score = abs(len(text_of(left)) - total / 2)
        if prev.endswith((",", ":", ";")):
            score -= 18          # strongly prefer clause boundaries
        if right[0]["start"] - left[-1]["end"] > GAP_BREAK:
            score -= 10          # and natural pauses
        if best is None or score < best[0]:
            best = (score, k)
    k = best[1] if best else len(ws) // 2
    return split_chunk(ws[:k]) + split_chunk(ws[k:])


def group(words):
    # 1) sentences
    sentences, cur = [], []
    for w in words:
        cur.append(w)
        if w["text"][-1] in ".?!" or w["text"].endswith('."'):
            sentences.append(cur); cur = []
    if cur:
        sentences.append(cur)
    # 2) caption-sized pieces per sentence
    pieces = [p for s in sentences for p in split_chunk(s)]
    # 3) merge very short pieces into a neighbour when the result still fits
    merged = []
    for p in pieces:
        short = (p[-1]["end"] - p[0]["start"] < 1.0) or len(p) <= 2
        if merged and short and ok(merged[-1] + p):
            merged[-1] = merged[-1] + p
        elif merged and (merged[-1][-1]["end"] - merged[-1][0]["start"] < 1.0 or len(merged[-1]) <= 2) and ok(merged[-1] + p):
            merged[-1] = merged[-1] + p
        else:
            merged.append(p)
    return merged


def ts(t):
    t = max(0, t); h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"


def main(src, dst):
    words = json.load(open(src, encoding="utf-8"))
    words = apply_fixes([{"text": w["text"], "start": w["start"], "end": w["end"]} for w in words])
    cues = group(words)
    out = []
    for i, c in enumerate(cues):
        start = c[0]["start"]
        end = max(c[-1]["end"] + 0.15, start + MIN_DUR)
        if i + 1 < len(cues):
            end = min(end, cues[i + 1][0]["start"] - 0.04)
        text = " ".join(x["text"] for x in c)
        out.append(f"{i + 1}\n{ts(start)} --> {ts(end)}\n" + "\n".join(wrap(text)) + "\n")
    open(dst, "w", encoding="utf-8").write("\n".join(out))
    print(f"wrote {dst}: {len(cues)} captions, {len(words)} words")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main(sys.argv[1], sys.argv[2])
