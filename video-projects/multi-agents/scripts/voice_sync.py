"""Sync the video to the recorded voiceover.

  python scripts/voice_sync.py            # align + write cues.recorded.json + warp compositions + wire audio
  python scripts/voice_sync.py --report   # alignment report only (no files changed)

Pipeline (run after scripts/cues.py and scripts/build_ch7.py, which rebuild files from the *scripted* timing):
 1. Load word-level transcripts of assets/PartN.m4a (assets/transcripts/PartN.raw.json).
 2. Align each script line to the spoken words (fuzzy, so ad-libbed words are fine) → real start/end per line.
 3. Lay chapters out on the real timeline; each Part's audio is placed so its lines land in their chapters.
 4. Inject a piecewise-linear TIME-WARP into every chapter composition: the authored (scripted) timeline is
    driven by a wrapper timeline so each line's animation spans exactly the real spoken line.
 5. Write scripts/cues.recorded.json, update index.html (chapter slots, whips, <audio> tracks, total).
"""
import argparse
import difflib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PARTS = [  # audio file → chapters it covers (in order)
    ("assets/Part1.m4a", ["ch0", "ch1", "ch2", "ch3", "ch4"]),
    ("assets/Part2.m4a", ["ch5", "ch6"]),
    ("assets/Part3.m4a", ["ch7"]),
    ("assets/Part4.m4a", ["ch8"]),
]
LEAD = 0.6         # silence before a chapter's first line (title chapter uses its scripted lead)
TAIL = 1.5         # hold after a chapter's last line
OUTRO_HOLD = 6.0   # final CTA hold
MIN_SEG = 0.05     # smallest warp segment (s)

NUM = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine"}


def norm_words(text):
    t = text.lower().replace("_", " ").replace("-", " ").replace(".", " ")
    t = re.sub(r"[^a-z0-9' ]+", " ", t)
    out = []
    for w in t.split():
        w = w.strip("'")
        if not w:
            continue
        if w.isdigit() and len(w) == 1:
            w = NUM[w]
        out.append(w)
    return out


def load_words(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    words = []

    def walk(o):
        if isinstance(o, dict):
            if "start" in o and "end" in o and any(k in o for k in ("word", "text")) and not any(isinstance(v, list) for v in o.values()):
                words.append({"w": o.get("word", o.get("text", "")), "s": float(o["start"]), "e": float(o["end"])})
            else:
                for v in o.values():
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(data)
    # split multi-word tokens, normalise
    toks = []
    for w in words:
        parts = norm_words(w["w"])
        for i, p in enumerate(parts):
            toks.append({"w": p, "s": w["s"] + (w["e"] - w["s"]) * i / max(len(parts), 1), "e": w["e"]})
    toks.sort(key=lambda x: x["s"])
    return toks


def align_part(lines, toks):
    """lines: [{'id','text'}] → {id: (real_start, real_end)} via sequence matching on words."""
    script, owner = [], []
    for li, l in enumerate(lines):
        for w in norm_words(l["text"]):
            script.append(w); owner.append(li)
    heard = [t["w"] for t in toks]
    sm = difflib.SequenceMatcher(None, script, heard, autojunk=False)
    match = {}  # script index → heard index
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            match[a + k] = b + k
    res, cover = {}, {}
    for li, l in enumerate(lines):
        idxs = [i for i, o in enumerate(owner) if o == li]
        hits = [(i, match[i]) for i in idxs if i in match]
        cover[l["id"]] = len(hits) / max(len(idxs), 1)
        if not hits:
            res[l["id"]] = None
            continue
        (si0, hi0), (si1, hi1) = hits[0], hits[-1]
        start = toks[hi0]["s"] - max(0, si0 - idxs[0]) * 0.35   # unmatched leading words ≈ 0.35 s each
        end = toks[hi1]["e"] + max(0, idxs[-1] - si1) * 0.35
        res[l["id"]] = [max(0.0, start), end]
    # fill gaps (lines with no matched words) by interpolation between neighbours
    ids = [l["id"] for l in lines]
    for i, cid in enumerate(ids):
        if res[cid] is None:
            prev = next((res[ids[j]] for j in range(i - 1, -1, -1) if res[ids[j]]), [0, 0])
            nxt = next((res[ids[j]] for j in range(i + 1, len(ids)) if res[ids[j]]), [prev[1] + 3, prev[1] + 3])
            res[cid] = [prev[1] + 0.3, max(prev[1] + 0.6, nxt[0] - 0.3)]
    # enforce monotonic starts
    for i in range(1, len(ids)):
        a, b = res[ids[i - 1]], res[ids[i]]
        if b[0] <= a[0] + 0.1:
            b[0] = a[0] + 0.1
        if b[1] <= b[0]:
            b[1] = b[0] + 0.3
    return res, cover


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    cues = json.loads((ROOT / "scripts" / "cues.json").read_text(encoding="utf-8"))
    chap = {c["id"]: c for c in cues["chapters"]}

    t = 0.0            # real timeline cursor
    audio = []         # [(src, start, duration)]
    recorded = []      # chapters with real timing
    warps = {}         # chapter id → [[real_local, scripted_local], ...]
    prev_audio_end = 0.0
    low_cover = []

    for pi, (src, ch_ids) in enumerate(PARTS):
        toks = load_words(ROOT / "assets" / "transcripts" / (pathlib.Path(src).stem + ".raw.json"))
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ROOT / src)],
                                   capture_output=True, text=True, check=True).stdout.strip())
        lines = [{"id": c["id"], "text": c["text"]} for cid in ch_ids for c in chap[cid]["cues"]]
        times, cover = align_part(lines, toks)
        low_cover += [(k, v) for k, v in cover.items() if v < 0.5]

        # place this part's audio: first chapter starts at cursor t, its first line after its lead
        first = chap[ch_ids[0]]
        lead0 = first["cues"][0]["start"] if first["id"] == "ch0" else LEAD
        a_off = t + lead0 - times[first["cues"][0]["id"]][0]
        if a_off < prev_audio_end:              # never overlap the previous part's audio
            t += prev_audio_end - a_off
            a_off = prev_audio_end
        audio.append((src, round(a_off, 3), round(dur, 3)))

        for ci, cid in enumerate(ch_ids):
            ch = chap[cid]
            first_real = a_off + times[ch["cues"][0]["id"]][0]
            lead = ch["cues"][0]["start"] if cid == "ch0" else LEAD
            if ci == 0:
                c_start = t
            else:
                prev_last_end = a_off + times[chap[ch_ids[ci - 1]]["cues"][-1]["id"]][1]
                c_start = max(prev_last_end + 0.3, first_real - lead)
                # close the previous chapter at this start
                recorded[-1]["duration"] = round(c_start - recorded[-1]["start"], 3)
            last_end = a_off + times[ch["cues"][-1]["id"]][1]
            c_end = last_end + TAIL + (OUTRO_HOLD if cid == "ch8" else 0)
            if ci == len(ch_ids) - 1:
                c_end = max(c_end, a_off + dur + 0.2)   # let the part's audio finish inside its last chapter
            new_cues = []
            for c in ch["cues"]:
                rs, re_ = times[c["id"]]
                new_cues.append({**c, "start": round(a_off + rs - c_start, 3), "dur": round(re_ - rs, 3)})
            recorded.append({**ch, "start": round(c_start, 3), "duration": round(c_end - c_start, 3), "cues": new_cues})
            t = c_end
        prev_audio_end = a_off + dur

    # warp maps (chapter-local): (0,0) → each line start/end → (real dur, scripted dur)
    for rc in recorded:
        sc = chap[rc["id"]]
        pts = [(0.0, 0.0, "start")]
        for c_real, c_scr in zip(rc["cues"], sc["cues"]):
            pts.append((c_real["start"], c_scr["start"], "start"))
            pts.append((c_real["start"] + c_real["dur"], c_scr["start"] + c_scr["dur"], "end"))
        pts.append((rc["duration"], sc["duration"], "end"))
        clean, kinds = [[0.0, 0.0]], ["start"]
        for r, s, kind in pts[1:]:
            if r > clean[-1][0] + MIN_SEG and s > clean[-1][1] + 0.01:
                clean.append([round(r, 3), round(s, 3)]); kinds.append(kind)
            elif kind == "start" and kinds[-1] == "end" and len(clean) > 1 and r > clean[-2][0] + MIN_SEG and s > clean[-2][1] + 0.01:
                # a line's end and the next line's start coincide: keep the START (the beat the animation keys on)
                clean[-1] = [round(r, 3), round(s, 3)]; kinds[-1] = kind
        if clean[-1][0] < rc["duration"]:
            clean[-1] = [round(rc["duration"], 3), sc["duration"]]
        warps[rc["id"]] = clean

    total = round(t, 3)
    print(f"{'chapter':8}{'scripted':>18}{'recorded':>18}   speed")
    for rc in recorded:
        sc = chap[rc["id"]]
        print(f"{rc['id']:8}{sc['start']:8.1f}+{sc['duration']:6.1f}s   {rc['start']:8.1f}+{rc['duration']:6.1f}s   {sc['duration'] / rc['duration']:.2f}x")
    print(f"total    {cues['total']:.1f}s → {total:.1f}s ({int(total // 60)}:{total % 60:04.1f})")
    for src, a, d in audio:
        print(f"audio  {src:18} at {a:8.2f}s  ({d:.1f}s)")
    if low_cover:
        print("lines with weak word match (<50%):", ", ".join(f"{k} {v:.0%}" for k, v in low_cover))
    if args.report:
        return

    out = {**cues, "total": total, "chapters": recorded,
           "voice": [{"src": s, "start": a, "duration": d} for s, a, d in audio]}
    (ROOT / "scripts" / "cues.recorded.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

    # ---- inject warps into each chapter composition
    files = {"ch0": "ch0-title.html", "ch1": "ch1-agent.html", "ch2": "ch2-session.html", "ch3": "ch3-problem.html",
             "ch4": "ch4-subagents.html", "ch5": "ch5-control.html", "ch6": "ch6-journey.html", "ch7": "ch7-code.html", "ch8": "ch8-recap.html"}
    for rc in recorded:
        p = ROOT / "compositions" / files[rc["id"]]
        s = p.read_text(encoding="utf-8")
        cid = rc["id"]
        reg = f'window.__timelines["{cid}"] = tl;'
        s = re.sub(r"/\*WARP-BEGIN\*/.*?/\*WARP-END\*/", lambda m: reg, s, flags=re.S)  # idempotent re-runs
        assert reg in s, f"{cid}: registration line not found"
        block = (
            f'/*WARP-BEGIN*/ // generated by scripts/voice_sync.py: plays the scripted timeline in step with the recorded voice\n'
            f'        const WARP = {json.dumps(warps[cid])}; // [real, scripted] chapter-local seconds\n'
            f'        const voiced = gsap.timeline({{ paused: true }});\n'
            f'        for (let i = 0; i < WARP.length - 1; i++) {{\n'
            f'          const [r0, s0] = WARP[i], [r1, s1] = WARP[i + 1];\n'
            f'          voiced.fromTo(tl, {{ time: s0 }}, {{ time: s1, duration: r1 - r0, ease: "none", immediateRender: false }}, r0);\n'
            f'        }}\n'
            f'        voiced.to({{}}, {{ duration: {rc["duration"]} }}, 0); // Law #11 anchor (recorded length)\n'
            f'        window.__timelines["{cid}"] = voiced; /*WARP-END*/'
        )
        s = s.replace(reg, block, 1)
        s = re.sub(rf'(data-composition-id="{cid}"[^>]*?data-duration=")[^"]*(")', rf'\g<1>{rc["duration"]:g}\g<2>', s, count=1)
        p.write_text(s, encoding="utf-8")
    print("warped", len(recorded), "compositions")

    # ---- index: chapter slots + whips + total (sync_index), then audio tracks
    subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_index.py"), str(ROOT / "scripts" / "cues.recorded.json")], check=True)
    idx = ROOT / "index.html"
    s = idx.read_text(encoding="utf-8")
    s = re.sub(r"\n      <!-- Voiceover -->.*?<!-- /Voiceover -->", "", s, flags=re.S)
    tags = "\n".join(
        f'      <audio id="vo-{i + 1}" src="{src}" data-start="{a:g}" data-duration="{d:g}" data-track-index="{10 + i}" data-volume="1"></audio>'
        for i, (src, a, d) in enumerate(audio))
    anchor = "      <!-- Whip-streaks"
    assert anchor in s
    s = s.replace(anchor, f"      <!-- Voiceover -->\n{tags}\n      <!-- /Voiceover -->\n\n{anchor}", 1)
    idx.write_text(s, encoding="utf-8")
    print("index: voiceover wired")


if __name__ == "__main__":
    main()
