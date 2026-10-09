"""Import recorded takes, transcribe them, and rebuild the shorts on the real voice.

  python scripts/ingest_voice.py <folder-with-downloads>

Picks the newest take per short from the teleprompter downloads (voiceover-ch0-take3.webm → short 1, ch1 → short 2, …),
converts it to assets/voiceover/short{k}.m4a, transcribes it with word timings (short{k}.words.json),
then rebuilds short{k}/index.html with real line timing, karaoke captions from your words, and the audio.
"""
import json, pathlib, re, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
VO = ROOT / "assets" / "voiceover"


def main(src):
    VO.mkdir(parents=True, exist_ok=True)
    takes = {}
    for f in pathlib.Path(src).glob("voiceover-ch*-take*.*"):
        m = re.match(r"voiceover-ch(\d+)-take(\d+)(?: \(\d+\))?\.(webm|m4a|mp4)$", f.name)
        if m:
            k, n = int(m.group(1)) + 1, int(m.group(2))
            if k not in takes or (n, f.stat().st_mtime) > takes[k][0]:
                takes[k] = ((n, f.stat().st_mtime), f)
    if not takes:
        sys.exit(f"No voiceover-chN-takeM files found in {src}")
    for k, (_, f) in sorted(takes.items()):
        m4a = VO / f"short{k}.m4a"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-ac", "1", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", str(m4a)], check=True)
        subprocess.run("npx hyperframes transcribe " + f'"{m4a}"' + " --model small.en --language en --json", shell=True, check=True,
                       cwd=ROOT, capture_output=True)
        shutil.move(str(VO / "transcript.json"), str(VO / f"short{k}.words.json"))
        n = len(json.loads((VO / f"short{k}.words.json").read_text(encoding="utf-8")))
        print(f"short {k}: {f.name} → {m4a.name}, {n} words")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_shorts.py"), *map(str, sorted(takes))], check=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main(sys.argv[1] if len(sys.argv) > 1 else str(pathlib.Path.home() / "Downloads"))
