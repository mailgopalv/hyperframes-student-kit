"""Re-times index.html + ambient-bg from scripts/cues.json (chapter starts, durations, whips, total).
Run from the project folder after `python scripts/cues.py`:  python scripts/sync_index.py"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "scripts" / "cues.json"
cues = json.loads(src.read_text(encoding="utf-8"))
chapters, total = cues["chapters"], cues["total"]
NO_WHIP_BEFORE = {"ch4"}  # ch3 → ch4 is a match cut

idx = ROOT / "index.html"
s = idx.read_text(encoding="utf-8")
for ch in chapters:
    s, n = re.subn(rf'(id="c-{ch["id"]}"[^>]*?data-start=")[^"]*(" data-duration=")[^"]*(")',
                   lambda m: f'{m.group(1)}{ch["start"]:g}{m.group(2)}{ch["duration"]:g}{m.group(3)}', s)
    assert n == 1, ch["id"]

# whips: one per seam (skipping match cuts), 0.2s before the next chapter starts
whips = [ch["start"] - 0.2 for ch in chapters[1:] if ch["id"] not in NO_WHIP_BEFORE]
block = "\n".join(f'      <div id="whip-{i}" class="whip clip" data-start="{t:.2f}" data-duration="0.4" data-track-index="2"></div>'
                  for i, t in enumerate(whips))
s = re.sub(r'(      <div [^>]*id="whip-\d+"[^>]*></div>\n)+', block + "\n", s, count=1)
s = re.sub(r'(id="ambient-bg"[^>]*?data-duration=")[^"]*(")', rf'\g<1>{total:g}\g<2>', s)
s = re.sub(r"tl\.set\(\{\}, \{\}, [\d.]+\);", f"tl.set({{}}, {{}}, {total:g});", s)
s = re.sub(r"Total [\d.]+s = [\d:]+\.", f"Total {total:g}s = {int(total // 60)}:{int(total % 60):02d}.", s)
idx.write_text(s, encoding="utf-8")

amb = ROOT / "compositions" / "ambient-bg.html"
a = amb.read_text(encoding="utf-8")
a = re.sub(r'(data-composition-id="ambient-bg"[^>]*?data-duration=")[^"]*(")', rf'\g<1>{total:g}\g<2>', a)
a = re.sub(r"const TOTAL = [\d.]+;", f"const TOTAL = {total:g};", a)
amb.write_text(a, encoding="utf-8")
print(f"index + ambient synced: {len(chapters)} chapters, {len(whips)} whips, total {total}s")
