# music-finder

Finds viral Instagram tracks for a video. Give it the topic, it returns the 10 tracks
that fit the video best and that people are using a lot right now, each with a link that
opens the sound in Instagram.

```
python3 music-finder/find-music.py "Lamborghini Murciélago at the Giza pyramids, light desert storm"
python3 music-finder/find-music.py "G-Wagon on Red Square in deep snow" --count 8
python3 music-finder/find-music.py "..." --reference iamnotsrc,otherpage   # house sound from these accounts
python3 music-finder/find-music.py "..." --reference none                 # no house sound
python3 music-finder/find-music.py "..." --country GB                     # another country's trending list
python3 music-finder/find-music.py "..." --dry-run                        # show the searches only, no Apify
python3 music-finder/find-music.py --show                                 # list past runs
```

## How it picks

1. **House sound.** Reads the tracks on the latest reels of `@iamnotsrc` (the account we
   model our packaging on), last 90 days only. Their reels run on dark phonk, so that is
   the default feel.
2. **Trending list.** Reads the sounds that carry Instagram's trending arrow in one
   country today. Mostly pop, so it only helps when something there fits.
3. **Searches.** Claude turns the topic into 12 short searches for Instagram's sound
   library: the house genre, the place and its culture, the car, the weather, the house
   artists, some in the place's own language (`москва`, `гелик`). Apify runs them,
   about 10 sounds each.
4. **Usage check.** Claude shortlists 22 tracks. Apify counts the reels that use each
   one and pulls the reels posted with it in the last month, with their plays.
5. **Ranking.** Claude ranks the best 10: fit first, then the trending arrow, big plays
   this month and total reels. Tracks used in under ~500 reels need an exact fit.

Nobody listens to the tracks. The picks come from titles, artists, searches and usage
numbers, so listen before posting.

## Setup

- `pip3 install anthropic` (the only dependency; Apify is called with the standard library).
- `.env` at the repo root with `ANTHROPIC_API_KEY` and `APIFY_API_KEY`. Two lines, `ANTHROPIC_API_KEY=...` and `APIFY_API_KEY=...`; the file is git-ignored.

## Cost

- Apify: about $0.65 a run (12 searches $0.38, usage check $0.27), plus about $0.20 for
  the first run of the day (trending list $0.18, house sound $0.02). Those two are cached
  in `results/cache/` for the rest of the day. The run prints what it spent.
- Claude: three Opus calls, a few cents.

## Results

- `results/<date>-<topic>.md`: the 10 tracks, why each fits, how many reels use it, its
  best reel this month and the Instagram link. Also the house sound and the searches.
- `results/<date>-<topic>.json`: everything scraped for that run (searches, checked
  tracks, last-month reels, picks, cost).
- `results/cache/`: today's trending list and house sound. Git-ignored.

Scrapers: `memo23~instagram-audio-scraper` (library search $0.0032 a sound, track lookups,
reels using a sound $0.0012 a reel, profile scans) and `s_actors~instagram-trending-audio`
(trending list, $0.0016 a sound). The profile scan sometimes leaves a reel's sound
unnamed; the script asks for those reels again, twice, and warns if one stays unnamed.
