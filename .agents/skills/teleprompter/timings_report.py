"""Compare recorded takes with the script, and write cues retimed to the real delivery.

Usage:
    python timings_report.py scripts/cues.json path/to/*.timings.json [--out scripts/cues.recorded.json]

For each chapter it prints how far your delivery drifted from the script (per line and overall),
then writes a cues file with the same shape as cues.json where:
  - every marked line starts when you actually started it
  - unmarked lines keep their spacing relative to the nearest marked line before them
  - each chapter's duration stretches or shrinks to fit (keeping the original tail after the last line)
If several takes cover the same chapter, the newest take wins.

The output is a drop-in replacement for cues.json. Point your composition timing at it
(or copy it over cues.json) once you're happy with the takes.
"""
import argparse
import glob
import json
import math
import pathlib
import sys


def load_takes(patterns):
    takes = []
    for pat in patterns:
        for f in glob.glob(pat):
            d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
            d["_file"] = f
            takes.append(d)
    takes.sort(key=lambda d: d.get("recordedAt", ""))
    return takes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cues"); ap.add_argument("timings", nargs="+")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    cues = json.loads(pathlib.Path(a.cues).read_text(encoding="utf-8"))
    takes = load_takes(a.timings)
    if not takes:
        raise SystemExit("No *.timings.json files matched.")

    actual = {}  # cue id → absolute actual start (newest take wins)
    for tk in takes:
        for m in tk.get("marks", []):
            actual[m["id"]] = m["actual"]
        print(f"take: {pathlib.Path(tk['_file']).name}  scope={tk.get('scope')}  marks={len(tk.get('marks', []))}")

    # The teleprompter clock runs on the *scripted* timeline, so a mark's chapter-local time is
    # simply actual − (scripted chapter start). Chapters are then re-stacked back to back.
    t, new_chapters = 0.0, []
    print()
    for ch in cues["chapters"]:
        deltas, new_cues, drift = [], [], 0.0
        for c in ch["cues"]:
            if c["id"] in actual:
                local = actual[c["id"]] - ch["start"]
                drift = local - c["start"]
                deltas.append(drift)
            else:
                local = c["start"] + drift  # keep spacing relative to the last marked line
            new_cues.append({**c, "start": round(max(local, 0.0), 2)})
        last_old = ch["cues"][-1]
        tail = ch["duration"] - (last_old["start"] + last_old["dur"])
        last_new = new_cues[-1]
        length = math.ceil((last_new["start"] + last_old["dur"] + tail) * 2) / 2
        new_chapters.append({**ch, "start": round(t, 2), "duration": length, "cues": new_cues})
        if deltas:
            avg = sum(deltas) / len(deltas); worst = max(deltas, key=abs)
            print(f"{ch['id']:5} {ch['title'][:32]:32}  marked {len(deltas):2}/{len(ch['cues']):2}  avg {avg:+5.1f}s  worst {worst:+5.1f}s  "
                  f"duration {ch['duration']:6.1f}s → {length:6.1f}s")
        else:
            print(f"{ch['id']:5} {ch['title'][:32]:32}  not recorded (kept as scripted)")
        t += length

    out = pathlib.Path(a.out or pathlib.Path(a.cues).with_name("cues.recorded.json"))
    out.write_text(json.dumps({**cues, "total": t, "chapters": new_chapters}, indent=1), encoding="utf-8")
    print(f"\nscripted total {cues['total']:.1f}s → recorded total {t:.1f}s")
    print(f"wrote {out}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
