# pinterest-refs

Give it a car, get ten real Pinterest photographs of it that fit our look.

The pipeline:

1. **Search.** One Apify run (`epctex/pinterest-scraper`) over eight queries built from the car name (`Ferrari F40`, `... photography`, `... night`, `... cinematic`, `... rear`, `... street`, `... sunset`, `... film photo`), three result pages each. About 480 pins.
2. **Filter.** Dedupe by image, drop anything under 600 px on a side and anything whose title smells like merch (lego, diecast, t-shirt, poster print ...). Sort by likes.
3. **Screen.** Claude looks at the 80 most-liked in batches of eight and scores each one: is it the exact car, is it a real photograph, technical quality, fit with our twilight-and-one-hot-light look, camera angle, one line of notes. Renders, posters, toys and wrong models are out.
4. **Shortlist.** Best 20 by score, no near-duplicate frames (perceptual hash), at most three per camera angle.
5. **Curate.** Claude sees the shortlist again and picks the final ten, as varied in place, light and angle as possible, best first.
6. **Save.** Originals downloaded into `results/<car-slug>/images/`, plus `contact.html`, `refs.md` and `refs.json`.

```
python3 pinterest-refs/find-refs.py "Ferrari F40"
python3 pinterest-refs/find-refs.py "Ferrari F40" --count 15
python3 pinterest-refs/find-refs.py "Ferrari F40" --pool 120
python3 pinterest-refs/find-refs.py "Ferrari F40" --query "Ferrari F40 LM" --query "F40 tunnel"
python3 pinterest-refs/find-refs.py "Ferrari F40" --no-judge       # likes only, no Claude
python3 pinterest-refs/find-refs.py "Ferrari F40" --no-download    # URLs only
```

## Setup

- `pip3 install anthropic pillow` (Pillow is only used for the duplicate check and the script runs without it).
- `.env` at the repo root with `APIFY_API_KEY` and `ANTHROPIC_API_KEY`. Two lines, `ANTHROPIC_API_KEY=...` and `APIFY_API_KEY=...`; the file is git-ignored.

## Cost

- Apify: the first page of every query is free, extra pins are $0.0001 each. A run is under 10 cents.
- Claude: 80 thumbnails screened in ten calls plus one curation call, roughly 20 cents at Opus 5.5 rates.

## Notes

- The Claude API cannot fetch `i.pinimg.com` itself (robots.txt), so thumbnails are downloaded and sent inline.
- Pinterest results are what Pinterest ranks today; rerunning gives a slightly different pool.
- References only. Nothing from here is posted.
