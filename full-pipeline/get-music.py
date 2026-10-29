#!/usr/bin/env python3
"""Download the chosen tracks for a run with yt-dlp (local only, for the cut; the real music is added in Instagram).

    python3 full-pipeline/get-music.py <run> "Freddie Dredd Wrath" "ASHEZ Chmura Say Nothing" "Gladiator Honor Him"

Each query is searched on YouTube (first result) and saved as <run>/music/<nn>-<slug>.m4a.
Listen to them: the music finder picks by titles and usage numbers, nobody has heard them yet.
"""
import re, subprocess, sys
from pathlib import Path


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    out = Path(sys.argv[1]) / "music"
    out.mkdir(parents=True, exist_ok=True)
    for i, q in enumerate(sys.argv[2:], 1):
        target = out / f"{i:02d}-{slug(q)}.%(ext)s"
        print(f"== {i}. {q}", flush=True)
        subprocess.run(["yt-dlp", "-q", "--no-warnings", "-x", "--audio-format", "m4a", "-o", str(target),
                        f"ytsearch1:{q}"], check=True)
    for p in sorted(out.glob("*.m4a")):
        dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                             capture_output=True, text=True).stdout.strip()
        print(f"   {p.name}  {float(dur):.0f}s")


if __name__ == "__main__":
    main()
