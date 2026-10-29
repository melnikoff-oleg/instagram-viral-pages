#!/usr/bin/env python3
"""3:4 cover from a reel, for the Instagram grid and the preview.

    python3 full-pipeline/cover.py reels/03-f40-colosseum/f40-colosseum-wrath.mp4 reels/03-f40-colosseum/cover.jpg
    python3 full-pipeline/cover.py <reel.mp4> <cover.jpg> --at 0.5     # a different moment, in seconds

Takes the frame at --at (default the first frame) and crops the middle 3:4 out of the 9:16 frame.
"""
import subprocess, sys


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    at = sys.argv[sys.argv.index("--at") + 1] if "--at" in sys.argv else "0"
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip().split(",")
    w, h = int(probe[0]), int(probe[1])
    ch = min(h, w * 4 // 3)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", at, "-i", src, "-vf", f"crop={w}:{ch}:0:{(h - ch) // 2}",
                    "-frames:v", "1", "-q:v", "2", dst], check=True)
    print(f"   {dst}  {w}x{ch}")


if __name__ == "__main__":
    main()
