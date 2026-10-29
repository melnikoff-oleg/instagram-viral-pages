#!/usr/bin/env python3
"""Find viral Instagram tracks for a video topic.

Give it what the video is about, it returns the 10 Instagram tracks that fit
it best and that people are using a lot right now. Same method as the tracks
picked by hand for the first reels (28 Oct 2026):

  1. the house sound: the tracks on the reference account's latest reels (@iamnotsrc)
  2. today's trending sounds in one country (cached for the day)
  3. Claude turns the topic into ~12 searches for Instagram's sound library
     (genre, place, car, weather, local language); Apify runs them
  4. Claude shortlists ~22 tracks; Apify counts the reels using each one and
     pulls the reels posted with it in the last month
  5. Claude ranks the best 10 from those numbers

  python3 music-finder/find-music.py "Lamborghini Murciélago at the Giza pyramids, light desert storm"
  python3 music-finder/find-music.py "G-Wagon on Red Square in deep snow" --count 8
  python3 music-finder/find-music.py "..." --reference iamnotsrc,otherpage   # house sound from these accounts
  python3 music-finder/find-music.py "..." --reference none                 # no house sound
  python3 music-finder/find-music.py "..." --country GB                     # another country's trending list
  python3 music-finder/find-music.py "..." --dry-run                        # show the searches only, no Apify
  python3 music-finder/find-music.py --show                                 # list past runs

Keys come from the .env at the repo root: ANTHROPIC_API_KEY (searches and
picks) and APIFY_API_KEY (Instagram data). A run costs about $0.65 on Apify,
plus about $0.20 for the first run of the day (trending list and house sound,
cached in results/cache/ after that).

Each run writes results/<date>-<topic>.md (the 10 tracks with links) and a
.json next to it with everything that was scraped. Nobody listens to the
tracks: the picks come from titles, artists, searches and usage numbers, so
listen before posting.
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE / "results"
CACHE = RESULTS / "cache"

MODEL = "claude-opus-5-5"
APIFY = "https://api.apify.com/v2"
AUDIO_ACTOR = "memo23~instagram-audio-scraper"      # search, track lookups, profile scans
TRENDING_ACTOR = "s_actors~instagram-trending-audio"  # Instagram's trending arrow, per country
REFERENCE = "iamnotsrc"   # the account whose packaging we model, see CLAUDE.md
REFERENCE_REELS = 8       # newest reels scanned per reference account
REFERENCE_DAYS = 90       # older reels don't count as the house sound
QUERIES = 12              # searches per run, ~10 sounds each, $0.0032 a sound
SHORTLIST = 22            # tracks checked for usage
REELS_PER_SOUND = 8       # last-month reels pulled per checked track, $0.0012 a reel
COUNT = 10
DROP = {"coverArtworkUrl", "audioDownloadUrl", "previewUrl", "videoUrl"}  # expiring CDN links

RUNS = []  # Apify run ids started by this process, for the cost line


# ---------------------------------------------------------------- env

def load_env():
    """Read KEY=value lines from ROOT/.env into the environment (existing vars win)."""
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def need(key):
    v = os.environ.get(key)
    if not v:
        sys.exit(f"{key} is not set. Put it in {ROOT / '.env'} or export it.")
    return v


# ---------------------------------------------------------------- apify

def http_json(url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Apify {e.code}: {e.read().decode(errors='replace')[:300]}")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        sys.exit(f"Apify unreachable: {e}")


def apify(actor, run_input, label):
    """Run an actor, wait for it, return its dataset items without the CDN links."""
    token = need("APIFY_API_KEY")
    print(f"   apify: {label} ...", flush=True)
    run = http_json(f"{APIFY}/acts/{actor}/runs?token={token}", run_input)["data"]
    RUNS.append(run["id"])
    while run["status"] in ("READY", "RUNNING"):
        run = http_json(f"{APIFY}/actor-runs/{run['id']}?token={token}&waitForFinish=60")["data"]
    if run["status"] != "SUCCEEDED":
        sys.exit(f"Apify {label} ended {run['status']}: https://console.apify.com/view/runs/{run['id']}")
    items = http_json(f"{APIFY}/datasets/{run['defaultDatasetId']}/items?token={token}&clean=true")
    return [{k: v for k, v in it.items() if k not in DROP} for it in items]


def apify_spent():
    """What this process's runs cost so far. Apify settles the last charges a minute or two late."""
    token = need("APIFY_API_KEY")
    return sum(http_json(f"{APIFY}/actor-runs/{rid}?token={token}")["data"].get("usageTotalUsd") or 0
               for rid in RUNS)


def cached(name, fetch):
    """Return today's copy of `name` from results/cache/, fetching it once a day."""
    path = CACHE / f"{name}-{dt.date.today().isoformat()}.json"
    if path.exists():
        return json.loads(path.read_text())
    rows = fetch()
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n")
    return rows


def house_sound(handles):
    """Tracks on the reference accounts' reels from the last REFERENCE_DAYS days."""
    if not handles:
        return []

    def fetch():
        rows = apify(AUDIO_ACTOR, {"profileHandles": handles, "maxReelsPerProfile": REFERENCE_REELS},
                     f"house sound from @{', @'.join(handles)}")
        # The scan leaves some reels' sound unnamed at random; asking for those reels again fills most in.
        for _ in range(2):
            missing = [r["postUrl"] for r in rows if not r.get("title") and r.get("postUrl")]
            if not missing:
                break
            named = {r["postUrl"]: r for r in apify(AUDIO_ACTOR, {"postUrls": missing},
                                                    f"{len(missing)} unnamed house sounds")
                     if r.get("title")}
            rows = [named.get(r.get("postUrl"), r) for r in rows]
        missing = [r["postUrl"] for r in rows if not r.get("title") and r.get("postUrl")]
        if missing:
            print(f"   could not name the sound on {', '.join(missing)}", file=sys.stderr)
        return rows

    rows = cached(f"reference-{'+'.join(handles)}", fetch)
    cutoff = time.time() - REFERENCE_DAYS * 86400
    return [r for r in rows if r.get("rowType") == "post-sound" and r.get("title")
            and (r.get("takenAt") or 0) >= cutoff]


def trending(country):
    """Sounds with Instagram's trending arrow in `country` today, each with a trackId."""
    def fetch():
        rows = apify(TRENDING_ACTOR, {"countries": [country], "maxSounds": 100, "soundType": "all",
                                      "trendingOnly": True, "topReels": 0},
                     f"today's trending sounds in {country}")
        for r in rows:
            m = re.search(r"/reels/audio/(\d+)", r.get("audioUrl") or "")
            r["trackId"] = m.group(1) if m else None
        return rows
    return [r for r in cached(f"trending-{country.lower()}", fetch) if r.get("trackId")]


# ---------------------------------------------------------------- claude

SYSTEM = """You pick music for short vertical videos on an Instagram theme page: iconic cars
in iconic places, shot like stolen frames from a feature film that never existed (dusk,
film grain, no text, no voice). The music is added in Instagram from its own sound library.

A good track for a video:
- fits the topic: the car, the place, the weather and the mood of the shots
- sits close to the house sound, the tracks the reference account put on its recent reels
- is used a lot on Instagram right now, so the reel rides a sound people already know
- works with no words on screen: no voiceovers, memes, prayers or kids' songs
- is a released track from the library rather than someone's original audio, unless the
  original audio is clearly a music track

You cannot hear the tracks. Judge from the title, the artist, the search that found the
track, what you know about it and the numbers you are given."""


def schema(key, fields):
    """JSON schema for {key: [{field: string, ...}]}."""
    item = {"type": "object", "properties": {f: {"type": "string"} for f in fields},
            "required": list(fields), "additionalProperties": False}
    return {"type": "object", "properties": {key: {"type": "array", "items": item}},
            "required": [key], "additionalProperties": False}


def ask(prompt, out_schema):
    import anthropic

    client = anthropic.Anthropic(api_key=need("ANTHROPIC_API_KEY"))
    resp = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "high", "format": {"type": "json_schema", "schema": out_schema}},
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    if resp.stop_reason == "refusal":
        sys.exit(f"Claude declined the request: {resp.stop_details}")
    return json.loads(next(b.text for b in resp.content if b.type == "text"))


def house_lines(house):
    if not house:
        return "House sound: none given.\n"
    return "House sound (tracks on the reference account's recent reels):\n" + "\n".join(
        f"- {r['title']} — {r['artist']} (@{r.get('postAuthor', '?')}, "
        f"{dt.date.fromtimestamp(r['takenAt']).isoformat()})" for r in house) + "\n"


def plan_searches(topic, house, n):
    prompt = (f"Video topic: {topic}\n\n{house_lines(house)}\n"
              f"Write {n} searches for Instagram's sound library that will surface tracks for "
              "this video. Instagram matches a search on titles and artists and returns about 10 "
              "sounds, so short searches of 1 to 3 words work best. Spread them across: the "
              "house genre and its close cousins (\"dark phonk\", \"slowed phonk\"), the place "
              "and its culture (\"arabic phonk\", \"москва\"), the car or object (\"gelik\"), "
              "the weather or season (\"winter phonk\"), and one or two artists of the house "
              "sound. When the place has its own language, write some searches in it. "
              "Give each a one-line reason.")
    out = ask(prompt, schema("searches", ["query", "why"]))["searches"]
    seen, keep = set(), []
    for s in out:
        q = s["query"].strip()
        if q and q.lower() not in seen:
            seen.add(q.lower())
            keep.append({"query": q, "why": s["why"].strip()})
    return keep[:n]


def pool_lines(pool):
    lines = []
    for t in pool.values():
        found = "; ".join(t["found"])
        orig = ", original audio" if t.get("orig") else ""
        lines.append(f"{t['trackId']} | {t['title']} — {t['artist']}{orig} | {found}")
    return "\n".join(lines)


def shortlist(topic, house, pool, k):
    prompt = (f"Video topic: {topic}\n\n{house_lines(house)}\n"
              "Candidate tracks (track id | title — artist | how it was found):\n"
              f"{pool_lines(pool)}\n\n"
              f"Pick up to {k} tracks worth checking how much they are used on Instagram. "
              "Keep the house tracks that fit this topic. Cover several directions (the house "
              "genre, the place and its culture, cinematic or luxury), not many versions of one "
              "song. Return the track ids exactly as given, each with a one-line reason.")
    out = ask(prompt, schema("tracks", ["trackId", "why"]))["tracks"]
    ids = []
    for t in out:
        tid = t["trackId"].strip()
        if tid in pool and tid not in ids:
            ids.append(tid)
    return ids[:k]


def stats_lines(checked, reels, trend):
    lines = []
    for s in checked:
        tid = s["trackId"]
        top = sorted(reels.get(tid, []), key=lambda r: -(r.get("playCount") or 0))[:3]
        recent = "; ".join(
            f"{human(r.get('playCount'))} plays {day(r.get('takenAt'))} @{r.get('creatorUsername')}: "
            f"{(r.get('reelCaption') or '').replace(chr(10), ' ')[:50]}" for r in top) or "none"
        tr = trend.get(tid)
        arrow = "yes" if s.get("isTrending") or tr else "no"
        growth = f", {tr['reelsGrowthPerDay']:+,}/day" if tr and tr.get("reelsGrowthPerDay") else ""
        lines.append(f"{tid} | {s['title']} — {s['artist']} | reels in total: "
                     f"{human(s.get('totalReelsUsingSound'))} | trending arrow: {arrow}{growth} | "
                     f"top reels this month: {recent}")
    return "\n".join(lines)


def rank(topic, house, checked, reels, trend, count):
    prompt = (f"Video topic: {topic}\n\n{house_lines(house)}\n"
              "Checked tracks, with how much Instagram uses them:\n"
              f"{stats_lines(checked, reels, trend)}\n\n"
              f"Rank the {count} best tracks for this video, best first. Fit comes first, then "
              "how alive the sound is: the trending arrow, big plays on reels posted this month, "
              "many reels in total. A track used in fewer than about 500 reels needs an unusually "
              "exact fit to make the list. Keep the list varied. For each, write `why`: one short "
              "sentence in plain words a 10-year-old can read, saying what it sounds like and why "
              "it fits this video. Leave numbers out; they are shown next to it. Return the "
              "track ids exactly as given.")
    out = ask(prompt, schema("tracks", ["trackId", "why"]))["tracks"]
    by_id = {s["trackId"]: s for s in checked}
    picks, seen = [], set()
    for t in out:
        tid = t["trackId"].strip()
        if tid in by_id and tid not in seen:
            seen.add(tid)
            picks.append({"trackId": tid, "why": t["why"].strip()})
    return picks[:count]


# ---------------------------------------------------------------- output

def human(n):
    if n is None:
        return "?"
    for size, unit in ((1_000_000, "M"), (1_000, "K")):
        if n >= size:
            v = n / size
            return f"{v:.1f}{unit}".replace(".0", "") if v < 10 else f"{v:.0f}{unit}"
    return str(n)


def day(ts):
    return dt.date.fromtimestamp(ts).strftime("%-d %b") if ts else "?"


def link(tid):
    return f"https://www.instagram.com/reels/audio/{tid}/"


def slugify(text):
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    words = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-").split("-")
    return "-".join(w for w in words[:8] if w) or "topic"


def shortlist_round_robin(pool, searches, k):
    """No Claude: house tracks first, then one hit per search in turn, skipping original audio."""
    ids = [t["trackId"] for t in pool.values() if any(f.startswith("house sound") for f in t["found"])]
    per_search = {s["query"]: [] for s in searches}
    for t in pool.values():
        if t.get("orig") or t["trackId"] in ids:
            continue
        for f in t["found"]:
            if f.startswith("search \""):
                q = f[len("search \""):-1]
                if q in per_search:
                    per_search[q].append(t["trackId"])
                    break
    while len(ids) < k and any(per_search.values()):
        for q in list(per_search):
            if per_search[q] and len(ids) < k:
                tid = per_search[q].pop(0)
                if tid not in ids:
                    ids.append(tid)
    return ids[:k]


def rank_by_usage(checked, reels, trend, count):
    """No Claude: trending arrow first, then best plays this month, then reels in total."""
    def key(s):
        tid = s["trackId"]
        best = max((r.get("playCount") or 0) for r in reels.get(tid, [])) if reels.get(tid) else 0
        return (1 if (s.get("isTrending") or trend.get(tid)) else 0, best, s.get("totalReelsUsingSound") or 0)
    ordered = sorted(checked, key=key, reverse=True)
    return [{"trackId": s["trackId"], "why": "ranked by usage only; judge the fit from the title"}
            for s in ordered[:count]]


def rows_for(picks, checked, reels, trend):
    by_id = {s["trackId"]: s for s in checked}
    rows = []
    for i, p in enumerate(picks, 1):
        s = by_id[p["trackId"]]
        tr = trend.get(p["trackId"])
        used = f"{human(s.get('totalReelsUsingSound'))} reels"
        if s.get("isTrending") or tr:
            used += ", trending"
        best = max(reels.get(p["trackId"], []), key=lambda r: r.get("playCount") or 0, default=None)
        best_txt = (f"{human(best.get('playCount'))} plays ({day(best.get('takenAt'))})"
                    if best and best.get("playCount") else "none")
        rows.append({"n": i, "track": f"{s['artist']}, \"{s['title']}\"", "why": p["why"],
                     "used": used, "best": best_txt, "link": link(p["trackId"])})
    return rows


def write_report(topic, args, house, searches, rows, cost, data):
    RESULTS.mkdir(parents=True, exist_ok=True)
    stem = f"{dt.date.today().isoformat()}-{slugify(topic)}"
    n = 2
    while (RESULTS / f"{stem}.md").exists():
        stem = f"{dt.date.today().isoformat()}-{slugify(topic)}-{n}"
        n += 1
    ref = ", ".join(f"@{h}" for h in args.reference) or "none"
    lines = [f"# Music for: {topic}", "",
             f"{dt.date.today().isoformat()}. House sound from {ref}, trending list {args.country}. "
             f"Apify cost about ${cost:.2f}.", "",
             "| # | Track | Why | Used in | Best reel this month | Link |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['n']} | {r['track']} | {r['why']} | {r['used']} | {r['best']} | {r['link']} |")
    lines += ["", "Nobody listened to these. The picks come from titles, artists, searches and "
              "usage numbers, so listen before posting.", "",
              "## House sound", ""]
    lines += [f"- {h['title']} — {h['artist']} (@{h.get('postAuthor')}, {day(h.get('takenAt'))})"
              for h in house] or ["- none"]
    lines += ["", "## Searches", ""] + [f"- `{s['query']}`: {s['why']}" for s in searches] + [""]
    (RESULTS / f"{stem}.md").write_text("\n".join(lines))
    (RESULTS / f"{stem}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    return RESULTS / f"{stem}.md"


def show():
    runs = sorted(RESULTS.glob("*.md"), reverse=True)
    if not runs:
        print("No runs yet.")
    for p in runs:
        title = p.read_text().splitlines()[0].removeprefix("# Music for: ")
        print(f"  {p.name:<60} {title}")


# ---------------------------------------------------------------- run

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("topic", nargs="?", help="what the video is about: car, place, weather, mood")
    ap.add_argument("--count", type=int, default=COUNT, help=f"tracks to return (default {COUNT})")
    ap.add_argument("--reference", default=REFERENCE,
                    help=f"comma-separated accounts for the house sound, or 'none' (default {REFERENCE})")
    ap.add_argument("--country", default="US", help="country of the trending list (default US)")
    ap.add_argument("--queries", type=int, default=QUERIES, help=f"library searches (default {QUERIES})")
    ap.add_argument("--shortlist", type=int, default=SHORTLIST,
                    help=f"tracks checked for usage (default {SHORTLIST})")
    ap.add_argument("--dry-run", action="store_true", help="plan the searches only, no Apify calls")
    ap.add_argument("--search", action="append", metavar="Q",
                    help="no Claude: a library search to run (repeatable). With --search the shortlist is "
                         "built round-robin (house sound first, then one hit per search) and the picks are "
                         "ranked by usage numbers only; judge the fit yourself from the table.")
    ap.add_argument("--show", action="store_true", help="list past runs")
    args = ap.parse_args()

    if args.show:
        return show()
    if not args.topic:
        ap.error("give the video topic, e.g. \"G-Wagon on Red Square in deep snow\"")
    args.reference = [] if args.reference.lower() == "none" else [
        h.strip().lstrip("@") for h in args.reference.split(",") if h.strip()]
    args.country = args.country.upper()
    load_env()

    print(f"\n== {args.topic}\n")
    house = [] if args.dry_run else house_sound(args.reference)
    trend_rows = [] if args.dry_run else trending(args.country)
    trend = {r["trackId"]: r for r in trend_rows}
    if house:
        print("   house sound: " + ", ".join(f"{h['title']} ({h['artist']})" for h in house))

    manual = bool(args.search)
    if manual:
        searches = [{"query": q.strip(), "why": "given on the command line"} for q in args.search if q.strip()]
        print(f"   {len(searches)} searches given, no Claude")
    else:
        print(f"   claude: planning {args.queries} searches ...", flush=True)
        searches = plan_searches(args.topic, house, args.queries)
    for s in searches:
        print(f"     {s['query']:<24} {s['why']}")
    if args.dry_run:
        return

    found = apify(AUDIO_ACTOR, {"queries": [s["query"] for s in searches], "maxSoundsPerQuery": 10},
                  f"{len(searches)} library searches")

    # Everything Claude may shortlist: house tracks, search hits, today's trending sounds.
    pool = {}
    def add(tid, title, artist, how, orig=False):
        if not tid or not title:
            return
        t = pool.setdefault(tid, {"trackId": tid, "title": title, "artist": artist,
                                  "orig": orig, "found": []})
        if how not in t["found"]:
            t["found"].append(how)
    for h in house:
        add(h["trackId"], h["title"], h["artist"], f"house sound (@{h.get('postAuthor')})")
    for r in found:
        add(r.get("trackId"), r.get("title"), r.get("artist"), f"search \"{r.get('source')}\"",
            r.get("isOriginalAudio"))
    for r in trend_rows:
        add(r["trackId"], r.get("title"), r.get("artist"),
            f"trending in {args.country}, {r.get('reelsCountText') or '?'}", r.get("isOriginalAudio"))

    if manual:
        ids = shortlist_round_robin(pool, searches, args.shortlist)
        print(f"   shortlisted {len(ids)} of {len(pool)} tracks round-robin (house first, then one per search)")
    else:
        print(f"   claude: shortlisting from {len(pool)} tracks ...", flush=True)
        ids = shortlist(args.topic, house, pool, args.shortlist)

    rows = apify(AUDIO_ACTOR, {"trackIds": ids, "includeReelsUsingSound": True,
                               "datePosted": "last-month", "maxReelsPerSound": REELS_PER_SOUND},
                 f"usage of {len(ids)} tracks")
    checked = [r for r in rows if r.get("rowType") == "sound" and r.get("title")]
    reels = {}
    for r in rows:
        if r.get("rowType") == "reel":
            reels.setdefault(r.get("soundTrackId"), []).append(r)

    if manual:
        picks = rank_by_usage(checked, reels, trend, args.count)
        print(f"   ranked {len(picks)} by usage numbers only (trending arrow, plays this month, reels in total)")
    else:
        print(f"   claude: ranking {len(checked)} checked tracks ...", flush=True)
        picks = rank(args.topic, house, checked, reels, trend, args.count)
    table = rows_for(picks, checked, reels, trend)
    cost = apify_spent()

    data = {"topic": args.topic, "date": dt.date.today().isoformat(), "reference": args.reference,
            "country": args.country, "house": house, "searches": searches, "found": found,
            "shortlist": ids, "checked": checked, "reels": [r for rs in reels.values() for r in rs],
            "picks": picks, "apify_usd": round(cost, 4)}
    path = write_report(args.topic, args, house, searches, table, cost, data)

    print()
    for r in table:
        print(f"  {r['n']:>2}. {r['track']}")
        print(f"      {r['why']}")
        print(f"      {r['used']} · best this month: {r['best']} · {r['link']}")
    print(f"\nApify cost about ${cost:.2f}. Saved to {path}")


if __name__ == "__main__":
    main()
