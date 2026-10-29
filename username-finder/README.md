# username-finder

Finds Instagram usernames that are actually free, for a concept you describe.

One round: Claude reads the concept, proposes ~100 handles in different styles, each one
goes through Instagram's own signup availability check (via Apify), and the free ones are
printed and saved. The next
round sees everything that was checked, skips it, and moves away from the styles that
turned out to be crowded.

```
python3 username-finder/find-usernames.py                  # concept from concept/instagram-concept.md, 100 names
python3 username-finder/find-usernames.py --rounds 3       # three rounds in a row
python3 username-finder/find-usernames.py --concept "..."  # any other concept, as text
python3 username-finder/find-usernames.py --style "one invented word, 6 to 9 letters"
python3 username-finder/find-usernames.py --check a,b,c    # check specific handles, no generation
python3 username-finder/find-usernames.py --dry-run        # ideas only, nothing spent on Apify
python3 username-finder/find-usernames.py --show           # every free handle found so far
python3 username-finder/find-usernames.py --recheck        # re-check old verdicts with the signup check
```

## Setup

- `pip3 install anthropic` (the only dependency; Apify is called with the standard library).
- Handles longer than 13 characters are dropped by default; `--max-len` changes that.
- `.env` at the repo root with `ANTHROPIC_API_KEY` and `APIFY_API_KEY`. Two lines, `ANTHROPIC_API_KEY=...` and `APIFY_API_KEY=...`; the file is git-ignored.

## Cost

- Ideas: one Claude Opus call per round, a few cents.
- Checks: `maged120/instagram-username-checker`, about $0.009 per handle, so ~$1 per 100.

## Why this checker and not a profile scraper

Instagram holds thousands of handles that have no public profile (deleted, banned,
reserved). A profile scraper answers "not found" for those, the signup form answers
"not available". `@afterlit` and `@rosegrain` were both like that. The only actor on
Apify whose verdicts matched the signup form on a verified set was
`maged120/instagram-username-checker`; the five others tested
(`seemuapps`, `goat255`, `clovys`, `corent1robert`, `misterkhan`) only test profile existence.

The checker is rate-limited by Instagram after about 45 handles on one run and then
silently answers "taken" for everything. So handles go through in runs of 20, four in
parallel, and every run carries two canaries: a handle nobody has and `instagram`. A run
whose canaries come back wrong is thrown away and retried; if it fails twice its handles
are stored as `unknown`.

## Results

- `results/checked.json` is the memory: every handle ever checked, its status, the reason
  it was proposed, the round and the time. Committed, so rounds never repeat work.
- `results/available.md` is the readable list of free handles, regenerated on every run.

`available` is the signup form's answer at check time; it can change at any moment, so
claim the one you pick without delay. `unknown` means no trustworthy verdict (rate limit
or a failed run); re-check those with `--check`.
