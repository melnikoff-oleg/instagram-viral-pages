# motion-study

How the reels we model on move, studied clip by clip, and the SOP that comes out of it.

**Start with [`sop.md`](sop.md).** It is the rulebook for every frame and clip we generate from now on: the two allowed car motions (straight and fast, drifting), the camera behaviours that go with them, the speed numbers, the realism checklist and the prompt blocks. Everything else in this folder is the evidence behind it.

| Path | What it is |
|------|------------|
| `sop.md` | The SOP: motion vocabulary, shot archetypes, camera/subject rules, realism rules, prompt blocks, the pre-generation checklist. |
| `findings.md` | Cross-video findings: what the five @iamnotsrc reels have in common, where our Murciélago reel differs, the numbers (clip lengths, speeds, camera moves). |
| `analysis/<video>.md` | One analysis per video: a clip table from the contact sheet (eye), what the video is doing, lessons for cars. |
| `analysis/<video>.gemini.md` / `.gemini.json` | Gemini's shot-by-shot report for the same video (camera/subject relationship, speeds, dynamism sources, realism cues, AI tells), verbatim, plus the parsed clip table. |
| `frames/<video>.jpg` | Contact sheet: one frame every 0.5 s with timestamps. Open these to check any claim in the analyses. |
| `videos/` | Local copies of the six videos (git-ignored like all mp4s) and `sources.json` with the Instagram URLs, post dates, play/like counts and audio. |
| `analyze.py` | The Gemini analysis script. |

## The six videos

| File | Account | Posted | Length | Clips | Plays / likes |
|------|---------|--------|--------|-------|---------------|
| `iamnotsrc-1-batman` | @iamnotsrc | 2026-10-27 | 22.5 s | 7 | 150k / 13.6k |
| `iamnotsrc-2-rocket-raccoon` | @iamnotsrc | 2026-10-25 | 21.4 s | 5 | 114k / 9.8k |
| `iamnotsrc-3-iron-man` | @iamnotsrc | 2026-10-24 | 15.2 s | 3 | 138k / 12.3k |
| `iamnotsrc-4-silver-surfer` | @iamnotsrc | 2026-10-23 | 15.2 s | 2 | 457k / 34.6k |
| `iamnotsrc-5-ghost-rider` | @iamnotsrc | 2026-10-22 | 15.5 s | 2 | 4.2M / 433k |
| `ours-1-murcielago-giza` | ours (reel 1) | – | 14.8 s | 4 | – |

The five @iamnotsrc reels are the five latest on the account as of 2026-10-29 (scraped with the Apify actor `apify/instagram-reel-scraper`, a few cents). They are reference only, never post them.

## Re-running

```
python3 motion-study/analyze.py                          # Gemini report for every video without one
python3 motion-study/analyze.py videos/x.mp4 --force     # redo one
python3 motion-study/analyze.py --model gemini-3.1-pro-preview --fps 10
```

- Keys: `GEMINI_API_KEY` and `GEMINI_API_KEY_2` in the root `.env` (both copied from Oleg's other projects on 2026-10-29). The script tries each key, and for each key the models in `MODELS`, until one answers. The first key is a prepaid project that was already empty on 2026-10-29; the second is a free-tier key that runs the flash models (`gemini-3.6-flash` is the one that answered) but not pro. Top up the first key at https://ai.studio/projects to get `gemini-3.1-pro-preview` reports.
- `pip3 install google-genai` once. ffmpeg/ffprobe for the cut detection.
- Contact sheets: one frame every 0.5 s, 8 per row, built with ffmpeg (`fps=2,scale=200:-1,drawtext,tile=8xN`).
- To add a video: drop it in `videos/`, make its contact sheet, run `analyze.py`, write `analysis/<name>.md` by eye, then update `findings.md` and, if a rule changes, `sop.md`.
