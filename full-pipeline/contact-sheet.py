#!/usr/bin/env python3
"""Contact sheet of the image candidates of a run: one row per frame, four candidates per row.

    python3 full-pipeline/contact-sheet.py <run>                # writes <run>/contact-candidates.jpg
    python3 full-pipeline/contact-sheet.py <run> --rows out/    # also one jpg per row, for looking at one frame at a time

Candidates are <run>/candidates/<frame><candidate>.png, e.g. 11.png .. 54.png.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    run = Path(sys.argv[1])
    rows_dir = Path(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == "--rows" else None
    files = sorted(p for p in (run / "candidates").iterdir() if p.suffix.lower() in (".png", ".jpg", ".webp"))
    if not files:
        sys.exit("no candidates")
    frames = sorted({int(p.stem[0]) for p in files})
    per_row = max(int(p.stem[1]) for p in files)
    tw, th = 540, 960
    sheet = Image.new("RGB", (per_row * (tw + 20), len(frames) * (th + 40)), "black")
    d = ImageDraw.Draw(sheet)
    for p in files:
        r, c = frames.index(int(p.stem[0])), int(p.stem[1]) - 1
        im = Image.open(p).convert("RGB")
        im.thumbnail((tw, th))
        x, y = c * (tw + 20) + 10, r * (th + 40) + 10
        sheet.paste(im, (x, y))
        d.text((x + 8, y + 8), p.name, fill="yellow")
    sheet.save(run / "contact-candidates.jpg", quality=80)
    print(f"   {run / 'contact-candidates.jpg'}")
    if rows_dir:
        rows_dir.mkdir(parents=True, exist_ok=True)
        for i, f in enumerate(frames):
            sheet.crop((0, i * (th + 40), sheet.width, (i + 1) * (th + 40))).save(rows_dir / f"row{f}.jpg", quality=85)
        print(f"   rows in {rows_dir}")


if __name__ == "__main__":
    main()
