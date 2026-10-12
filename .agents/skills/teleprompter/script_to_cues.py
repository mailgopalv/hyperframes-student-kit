"""Turn a plain Markdown voiceover script into the cues.json the teleprompter reads.

Script format (one narration line per paragraph line):

    # Video title
    ## Chapter title
    First line of narration.
    > optional on-screen note for the line above
    Second line of narration.
    ## Next chapter
    ...

Usage:
    python script_to_cues.py SCRIPT.md scripts/cues.json [--wpm 140] [--gap 0.8] [--lead 0.6] [--tail 1.5] [--outro 6]

Timing is estimated from word count, so it's a starting point. Record with the teleprompter,
then run timings_report.py to replace the estimates with your real delivery.
"""
import argparse
import json
import math
import pathlib
import sys
import re


def fr(x):
    """Snap to a 30fps frame boundary."""
    return round(round(x * 30) / 30, 2)


def parse(md):
    title, chapters = "", []
    for raw in md.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# ") and not title:
            title = re.sub(r"^voiceover script:\s*", "", line[2:].strip(), flags=re.I)
        elif line.startswith("## "):
            name = re.sub(r"\s+·\s+[\d:.]+\s+–\s+[\d:.]+\s*$", "", line[3:]).strip()  # drop "· 0:00 – 0:27"
            chapters.append({"title": name, "lines": []})
        elif not chapters:
            continue  # preamble before the first chapter
        elif line.startswith(">") or re.match(r"^(<br>)?\*On screen:", line):
            if chapters[-1]["lines"]:
                note = re.sub(r"^(>\s*|<br>\*On screen:\s*|\*On screen:\s*)", "", line).rstrip("*").strip()
                chapters[-1]["lines"][-1]["note"] = note
        else:
            text = re.sub(r"^\*\*[\d:.]+\*\*\s*", "", line)  # tolerate "**0:12.3** text" (SCRIPT.md style)
            chapters[-1]["lines"].append({"text": text})
    return title, chapters


def build(chapters, wpm, gap, lead, tail, outro):
    wps, t, out = wpm / 60, 0.0, []
    for ci, ch in enumerate(chapters):
        local, cues = lead, []
        for i, ln in enumerate(ch["lines"], 1):
            dur = len(ln["text"].split()) / wps
            cue = {"id": f"ch{ci}.{i}", "start": fr(local), "dur": fr(dur), "text": ln["text"]}
            if ln.get("note"):
                cue["note"] = ln["note"]
            cues.append(cue)
            local += dur + gap
        length = local - gap + tail + (outro if ci == len(chapters) - 1 else 0)
        length = math.ceil(length * 2) / 2
        out.append({"id": f"ch{ci}", "title": ch["title"], "start": fr(t), "duration": length, "cues": cues})
        t += length
    return out, t


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script"); ap.add_argument("out")
    ap.add_argument("--wpm", type=float, default=140); ap.add_argument("--gap", type=float, default=0.8)
    ap.add_argument("--lead", type=float, default=0.6); ap.add_argument("--tail", type=float, default=1.5)
    ap.add_argument("--outro", type=float, default=6.0)
    a = ap.parse_args()
    title, chapters = parse(pathlib.Path(a.script).read_text(encoding="utf-8"))
    if not chapters:
        raise SystemExit("No narration lines found. Use '## Chapter' headings and one line of narration per line.")
    chs, total = build(chapters, a.wpm, a.gap, a.lead, a.tail, a.outro)
    out = pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"title": title, "total": total, "chapters": chs}, indent=1), encoding="utf-8")
    n = sum(len(c["cues"]) for c in chs)
    print(f"wrote {out}: {len(chs)} chapters, {n} lines, {int(total // 60)}:{total % 60:04.1f}")
