#!/usr/bin/env python3
"""Find reference photos of a car on Pinterest.

Give it a car, it searches Pinterest through Apify with a handful of queries
(plain, photography, night, cinematic, rear, street ...), pools a few hundred
pins, drops the junk (toys, merch, tiny images, duplicates), has Claude look at
the best candidates and keep only real photographs that actually show the car
and fit our look, and saves the top ten with the originals downloaded.

  python3 pinterest-refs/find-refs.py "Ferrari F40"
  python3 pinterest-refs/find-refs.py "Ferrari F40" --count 15      # keep 15 instead of 10
  python3 pinterest-refs/find-refs.py "Ferrari F40" --pool 120      # let Claude judge 120 candidates (default 80)
  python3 pinterest-refs/find-refs.py "Ferrari F40" --query "Ferrari F40 LM" --query "F40 tunnel"
  python3 pinterest-refs/find-refs.py "Ferrari F40" --no-judge      # rank by likes only, no Claude call
  python3 pinterest-refs/find-refs.py "Ferrari F40" --no-download   # keep URLs only, no image files

Keys come from the .env at the repo root: APIFY_API_KEY (search) and
ANTHROPIC_API_KEY (judging). One run is a few cents on Apify (the first page
of every query is free, extra pins are $0.0001 each) and roughly 10 to 20
cents on Claude for 80 images.

Results land in pinterest-refs/results/<car-slug>/:
  refs.json     every judged candidate with scores, plus the picks
  refs.md       the picks as a readable list (pin URL, image URL, why)
  contact.html  the picks as a contact sheet, open it in a browser
  images/       the picks, original resolution, numbered by rank
"""
import argparse
import base64
import concurrent.futures as cf
import datetime as dt
import html
import json
import math
import os
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE / "results"

MODEL = "claude-opus-5-5"
ACTOR = "epctex~pinterest-scraper"
PAGES = 3                 # search result pages per query (about 15 pins each)
JUDGE_BATCH = 8           # images per Claude request
JUDGE_WORKERS = 4         # parallel Claude requests
MIN_SIDE = 600            # smallest acceptable image side, px
QUERY_SUFFIXES = ["", "photography", "night", "cinematic", "rear", "street",
                  "sunset", "film photo"]
JUNK = re.compile(r"\b(lego|hot ?wheels|diecast|die-cast|1[:/]18|1[:/]43|1[:/]64|model kit|tamiya|"
                  r"sticker|t-?shirt|hoodie|mug|phone case|coloring|colouring|clipart|svg|"
                  r"blueprint|wiring)\b", re.I)


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


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# ---------------------------------------------------------------- search

def search_pinterest(queries, max_items):
    """One Apify run over every query. Returns the raw pin items."""
    token = need("APIFY_API_KEY")
    start = [{"url": "https://www.pinterest.com/search/pins/?q=" + urllib.parse.quote(q)}
             for q in queries]
    url = (f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items"
           f"?token={token}&timeout=600")
    body = json.dumps({"startUrls": start, "maxItems": max_items, "endPage": PAGES,
                       "getDetails": False}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            items = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"apify {e.code}: {e.read().decode(errors='replace')[:400]}")
    return items if isinstance(items, list) else []


def candidates_from(items):
    """Dedupe, drop junk and small images, return candidate dicts sorted by likes."""
    seen, out = set(), []
    for it in items:
        if it.get("type") not in (None, "pin"):
            continue
        imgs = it.get("images") or {}
        orig = imgs.get("orig") or {}
        if not orig.get("url"):
            continue
        key = re.sub(r"^.*/", "", orig["url"]).split(".")[0]  # pinimg content hash
        if key in seen:
            continue
        w, h = orig.get("width") or 0, orig.get("height") or 0
        if min(w, h) < MIN_SIDE:
            continue
        title = (it.get("grid_title") or "").strip()
        desc = (it.get("description") or "").strip()
        if JUNK.search(title + " " + desc):
            continue
        seen.add(key)
        thumb = (imgs.get("474x") or imgs.get("736x") or orig)["url"]
        out.append({
            "id": it.get("id"),
            "pin_url": it.get("url") or f"https://www.pinterest.com/pin/{it.get('id')}/",
            "image_url": orig["url"],
            "thumb_url": thumb,
            "width": w, "height": h,
            "likes": it.get("like_count") or 0,
            "title": title, "description": desc[:200],
            "pinner": ((it.get("pinner") or {}).get("username")) or "",
            "domain": it.get("domain") or "",
            "query": re.sub(r"^.*[?&]q=", "", it.get("inputSource") or ""),
        })
    out.sort(key=lambda c: c["likes"], reverse=True)
    return out


# ---------------------------------------------------------------- judge

SYSTEM = """You are picking reference photographs of a specific car for a cinematic
Instagram account ("iconic cars in iconic places", stills from films that were
never made). You are shown a numbered batch of Pinterest images. Judge each one
on its own.

For every image report:
- is_car: true only if the exact car asked for is clearly the subject. A different
  model from the same brand, a kit car, a toy or a car so hidden it cannot be
  identified is false.
- real_photo: true only for a real photograph of a real car. Renders, AI images,
  illustrations, paintings, video-game screenshots, collages, posters with large
  text, memes and images with heavy overlays, watermarks or borders are false.
  Film grain, strong grading and motion blur are fine, that is the look we want.
- quality (1-10): technical and compositional quality. Sharp enough where it
  matters, good exposure, deliberate framing, no crops that cut the car badly,
  no compression mush.
- fit (1-10): how useful this is as a reference for our look: cinematic and
  atmospheric, low or directional light (dusk, night, headlights, tunnel, rain,
  fog), strong readable silhouette, a sense of place. A bright flat showroom or
  auction shot on grey tarmac is a 3; a moody dusk shot that reads instantly is 9.
- angle: one short tag like front-3/4, rear-3/4, side, rear, front, detail, top,
  interior, tracking.
- note: a dry, specific sentence on what this image gives us (or why it is out).

Be strict: it is better to reject a good image than to pass a bad one."""

SCHEMA = {
    "type": "object",
    "properties": {
        "images": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "is_car": {"type": "boolean"},
                    "real_photo": {"type": "boolean"},
                    "quality": {"type": "integer"},
                    "fit": {"type": "integer"},
                    "angle": {"type": "string"},
                    "note": {"type": "string"},
                },
                "required": ["index", "is_car", "real_photo", "quality", "fit", "angle", "note"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["images"],
    "additionalProperties": False,
}


def fetch(url, timeout=60):
    """Download a URL and return (bytes, media_type), or (None, None) on failure."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"  could not fetch {url}: {e}", file=sys.stderr)
        return None, None
    if data[:3] == b"\xff\xd8\xff":
        mt = "image/jpeg"
    elif data[:8] == b"\x89PNG\r\n\x1a\n":
        mt = "image/png"
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        mt = "image/webp"
    elif data[:4] == b"GIF8":
        mt = "image/gif"
    else:
        return None, None
    return data, mt


def dhash(data):
    """64-bit difference hash of an image, or None if it cannot be read."""
    try:
        import io
        from PIL import Image
        im = Image.open(io.BytesIO(data)).convert("L").resize((9, 8))
        px = list(im.tobytes())
        bits = 0
        for row in range(8):
            for col in range(8):
                bits = (bits << 1) | (px[row * 9 + col] > px[row * 9 + col + 1])
        return bits
    except Exception:
        return None


def near_duplicate(a, b, max_bits=10):
    return a is not None and b is not None and bin(a ^ b).count("1") <= max_bits


def judge_batch(client, car, batch):
    """Score one batch of candidates. Returns {index: verdict}."""
    # Pinterest's CDN is off limits to the API's own fetcher, so the thumbnails go inline.
    content = []
    for i, c in enumerate(batch, 1):
        data, mt = fetch(c["thumb_url"])
        if data is None:
            data, mt = b"", "image/jpeg"  # the judge will see nothing and reject it
        c["dhash"] = dhash(data)
        content.append({"type": "text", "text": f"Image {i}:"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": mt,
                                                    "data": base64.b64encode(data).decode()}})
    content.append({"type": "text", "text":
                    f"The car we want: {car}. Judge all {len(batch)} images, index 1 to {len(batch)}."})
    try:
        resp = client.beta.messages.create(
            model=MODEL,
            max_tokens=8000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": "medium",
                           "format": {"type": "json_schema", "schema": SCHEMA}},
            system=SYSTEM,
            messages=[{"role": "user", "content": content}],
        )
    except Exception as e:  # one failed batch should not sink the run
        print(f"  claude failed on a batch of {len(batch)}: {e}", file=sys.stderr)
        return {}
    if resp.stop_reason == "refusal":
        print(f"  claude declined a batch: {resp.stop_details}", file=sys.stderr)
        return {}
    text = next((b.text for b in resp.content if b.type == "text"), "{}")
    out = {}
    for v in json.loads(text).get("images", []):
        if 1 <= v["index"] <= len(batch):
            out[v["index"] - 1] = v
    return out


def judge(car, cands):
    """Attach a verdict to every candidate (missing verdicts count as rejected)."""
    import anthropic
    client = anthropic.Anthropic(api_key=need("ANTHROPIC_API_KEY"))
    batches = [cands[i:i + JUDGE_BATCH] for i in range(0, len(cands), JUDGE_BATCH)]
    with cf.ThreadPoolExecutor(max_workers=JUDGE_WORKERS) as ex:
        results = list(ex.map(lambda b: judge_batch(client, car, b), batches))
    for batch, verdicts in zip(batches, results):
        for i, c in enumerate(batch):
            v = verdicts.get(i)
            if v is None:
                c["verdict"] = {"is_car": False, "real_photo": False, "quality": 0, "fit": 0,
                                "angle": "", "note": "no verdict from the judge"}
            else:
                c["verdict"] = {k: v[k] for k in ("is_car", "real_photo", "quality", "fit",
                                                  "angle", "note")}
            c["score"] = score(c)


def score(c):
    v = c["verdict"]
    if not (v["is_car"] and v["real_photo"]):
        return 0.0
    return round(0.6 * v["fit"] + 0.4 * v["quality"] + 0.3 * math.log10(1 + c["likes"]), 2)


def shortlist(cands, count, max_per_angle=3):
    """Best `count` by score that pass the gates, no near-duplicates, capped per camera angle."""
    ok = [c for c in cands if c.get("score", 0) > 0 and c["verdict"]["quality"] >= 6]
    ok.sort(key=lambda c: c["score"], reverse=True)
    picks, per_angle = [], {}
    for c in ok:
        if any(near_duplicate(c.get("dhash"), p.get("dhash")) for p in picks):
            continue
        a = c["verdict"]["angle"].lower()
        if per_angle.get(a, 0) >= max_per_angle:
            continue
        per_angle[a] = per_angle.get(a, 0) + 1
        picks.append(c)
        if len(picks) == count:
            break
    return picks


CURATE = """You are the photo editor of a cinematic Instagram account ("iconic cars in
iconic places", stills from films that were never made). You get a numbered
shortlist of real photographs of one car that already passed a first screening.
Choose the final set: the strongest images, as different from each other as
possible. Never keep two frames from the same shoot, place or angle when one
will do; prefer variety of location, light and camera angle. Order the picks
from best to tenth-best. Drop anything that on a second look is not the exact
car, not a real photo, or carries text, borders or watermarks."""

CURATE_SCHEMA = {
    "type": "object",
    "properties": {
        "picks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"index": {"type": "integer"}, "why": {"type": "string"}},
                "required": ["index", "why"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["picks"],
    "additionalProperties": False,
}


def curate(car, short, count):
    """Have Claude choose a varied final set of `count` from the shortlist."""
    import anthropic
    client = anthropic.Anthropic(api_key=need("ANTHROPIC_API_KEY"))
    content = []
    for i, c in enumerate(short, 1):
        data, mt = fetch(c["thumb_url"])
        if data is None:
            continue
        content.append({"type": "text", "text": f"Image {i} ({c['verdict']['angle']}):"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": mt,
                                                    "data": base64.b64encode(data).decode()}})
    content.append({"type": "text", "text":
                    f"The car: {car}. Pick exactly {count} images from these {len(short)}, "
                    "best first, with one line each on why it earns its place."})
    try:
        resp = client.beta.messages.create(
            model=MODEL, max_tokens=4000,
            betas=["server-side-fallback-2026-07-01"], fallbacks="default",
            output_config={"effort": "medium",
                           "format": {"type": "json_schema", "schema": CURATE_SCHEMA}},
            system=CURATE, messages=[{"role": "user", "content": content}],
        )
    except Exception as e:
        print(f"  curation failed, keeping the shortlist order: {e}", file=sys.stderr)
        return short[:count]
    if resp.stop_reason == "refusal":
        print(f"  curation declined, keeping the shortlist order: {resp.stop_details}", file=sys.stderr)
        return short[:count]
    text = next((b.text for b in resp.content if b.type == "text"), "{}")
    picks, seen = [], set()
    for p in json.loads(text).get("picks", []):
        i = p["index"] - 1
        if 0 <= i < len(short) and i not in seen:
            seen.add(i)
            short[i]["verdict"]["note"] = p["why"].strip()
            picks.append(short[i])
    # Pad from the shortlist if Claude returned fewer than asked.
    for c in short:
        if len(picks) >= count:
            break
        if c not in picks:
            picks.append(c)
    return picks[:count]


# ---------------------------------------------------------------- output

def download(picks, folder):
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("*"):
        old.unlink()

    def one(args):
        rank, c = args
        ext = pathlib.Path(urllib.parse.urlparse(c["image_url"]).path).suffix or ".jpg"
        dest = folder / f"{rank:02d}{ext}"
        data, _ = fetch(c["image_url"])
        if data:
            dest.write_bytes(data)
            c["file"] = str(dest.relative_to(folder.parent))

    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        list(ex.map(one, enumerate(picks, 1)))


def write_md(car, picks, judged, path):
    lines = [f"# {car}: Pinterest references", "",
             f"{len(picks)} picks out of {len(judged)} judged, {dt.date.today().isoformat()}. "
             "Generated by find-refs.py.", ""]
    for i, c in enumerate(picks, 1):
        v = c["verdict"]
        lines.append(f"## {i}. {v['angle']} · fit {v['fit']} · quality {v['quality']} · "
                     f"{c['likes']} likes")
        lines.append("")
        lines.append(f"- pin: {c['pin_url']}")
        lines.append(f"- image: {c['image_url']} ({c['width']}×{c['height']})")
        if c.get("file"):
            lines.append(f"- file: {c['file']}")
        lines.append(f"- {v['note']}")
        lines.append("")
    path.write_text("\n".join(lines))


def write_html(car, picks, path):
    cards = []
    for i, c in enumerate(picks, 1):
        v = c["verdict"]
        src = c.get("file") or c["thumb_url"]
        cards.append(f"""
<figure>
  <a href="{html.escape(c['pin_url'])}" target="_blank"><img src="{html.escape(src)}" loading="lazy"></a>
  <figcaption><b>{i}</b> · {html.escape(v['angle'])} · fit {v['fit']} · q {v['quality']} · {c['likes']} likes
  <span>{html.escape(v['note'])}</span></figcaption>
</figure>""")
    path.write_text(f"""<!doctype html><meta charset="utf-8"><title>{html.escape(car)} refs</title>
<style>
body{{margin:0;padding:24px;background:#0e0e10;color:#ddd;font:14px/1.4 -apple-system,system-ui,sans-serif}}
h1{{font-weight:500;margin:0 0 16px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px}}
figure{{margin:0;background:#17171a;border-radius:8px;overflow:hidden}}
img{{display:block;width:100%;height:auto}}
figcaption{{padding:10px 12px}} figcaption span{{display:block;color:#999;margin-top:4px}}
</style>
<h1>{html.escape(car)} · {len(picks)} Pinterest references</h1>
<div class="grid">{''.join(cards)}</div>
""")


# ---------------------------------------------------------------- main

# ---------------------------------------------------------------- screen by eye (no Claude)

def big_url(c):
    """A 736px Pinterest rendition of the pin image, enough to judge the car and the light."""
    return c["image_url"].replace("/originals/", "/736x/")


def screen(car, cands, out_dir, n, per_sheet=20, cols=5):
    """Download the n most-liked candidates and lay them out on numbered contact sheets."""
    from PIL import Image, ImageDraw

    pool = cands[:n]
    folder = out_dir / "screen"
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("*"):
        old.unlink()

    def one(args):
        i, c = args
        data, _ = fetch(big_url(c))
        if not data:
            data, _ = fetch(c["thumb_url"])
        if data:
            (folder / f"{i:02d}.jpg").write_bytes(data)
        return i

    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(one, enumerate(pool, 1)))

    tw, th = 360, 480
    sheets = []
    for start in range(0, len(pool), per_sheet):
        chunk = list(range(start + 1, min(start + per_sheet, len(pool)) + 1))
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (tw + 12), rows * (th + 36)), "black")
        d = ImageDraw.Draw(sheet)
        for k, i in enumerate(chunk):
            f = folder / f"{i:02d}.jpg"
            if not f.exists():
                continue
            try:
                im = Image.open(f).convert("RGB")
            except Exception:
                continue
            im.thumbnail((tw, th))
            x, y = (k % cols) * (tw + 12) + 6, (k // cols) * (th + 36) + 6
            sheet.paste(im, (x, y))
            d.text((x + 6, y + th + 8), f"#{i}  {pool[i - 1]['likes']} likes  {pool[i - 1]['width']}x{pool[i - 1]['height']}",
                   fill="yellow")
        name = out_dir / f"screen-sheet-{len(sheets) + 1}.jpg"
        sheet.save(name, quality=80)
        sheets.append(name)

    (out_dir / "screen.json").write_text(json.dumps({
        "car": car, "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "candidates": [dict(c, screen_index=i) for i, c in enumerate(pool, 1)]}, indent=1, ensure_ascii=False) + "\n")
    print(f"\n   {len(pool)} candidates in {folder.relative_to(ROOT)}, numbered by likes")
    for sh in sheets:
        print(f"   look at {sh.relative_to(ROOT)}")
    print(f"   then: python3 pinterest-refs/find-refs.py \"{car}\" --pick <n> [--pick <n> ...]")


def pick(car, out_dir, numbers):
    """Download the originals of the screened candidates you chose, best first, and write refs.md."""
    data = json.loads((out_dir / "screen.json").read_text())
    by_index = {c["screen_index"]: c for c in data["candidates"]}
    picks = []
    for n in numbers:
        if n not in by_index:
            sys.exit(f"#{n} is not on the screen sheets (1..{len(by_index)})")
        c = dict(by_index[n])
        c["verdict"] = {"is_car": True, "real_photo": True, "quality": 0, "fit": 0, "angle": "",
                        "note": f"picked by eye from screen sheet (#{n})"}
        picks.append(c)
    download(picks, out_dir / "images")
    write_md(car, picks, [], out_dir / "refs.md")
    write_html(car, picks, out_dir / "contact.html")
    (out_dir / "refs.json").write_text(json.dumps({
        "car": car, "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "picks": picks, "judged": []}, indent=1, ensure_ascii=False) + "\n")
    print(f"\n   {len(picks)} picked -> {out_dir.relative_to(ROOT)}/images/")
    for i, c in enumerate(picks, 1):
        print(f"   {i:>2}. #{c['screen_index']}  {c['likes']} likes  {c['width']}x{c['height']}  {c['pin_url']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("car", help='the car, e.g. "Ferrari F40"')
    ap.add_argument("--count", type=int, default=10, help="how many references to keep (default 10)")
    ap.add_argument("--pool", type=int, default=80,
                    help="how many of the most-liked candidates Claude judges (default 80)")
    ap.add_argument("--query", action="append",
                    help="search query; repeatable; replaces the default set built from the car")
    ap.add_argument("--no-judge", action="store_true", help="skip Claude, rank by likes only")
    ap.add_argument("--no-download", action="store_true", help="do not download the picks")
    ap.add_argument("--screen", type=int, metavar="N",
                    help="no Claude: download the N most-liked candidates and build numbered contact sheets to judge by eye")
    ap.add_argument("--pick", type=int, action="append", metavar="N",
                    help="after --screen: keep candidate #N as a reference (repeatable, best first)")
    args = ap.parse_args()

    load_env()
    car = args.car.strip()
    queries = args.query or [f"{car} {s}".strip() for s in QUERY_SUFFIXES]
    out_dir = RESULTS / slugify(car)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.pick:
        return pick(car, out_dir, args.pick)

    print(f"== {car}: searching Pinterest with {len(queries)} queries ...", flush=True)
    items = search_pinterest(queries, max_items=len(queries) * PAGES * 20)
    cands = candidates_from(items)
    print(f"   {len(items)} pins, {len(cands)} usable candidates after dedupe and filters")
    if not cands:
        sys.exit("nothing usable came back; try other --query values")
    if args.screen:
        return screen(car, cands, out_dir, args.screen)

    pool = cands[:args.pool]
    if args.no_judge:
        for c in pool:
            c["verdict"] = {"is_car": True, "real_photo": True, "quality": 6, "fit": 5,
                            "angle": "", "note": "not judged (--no-judge)"}
            c["score"] = score(c)
    else:
        print(f"   asking Claude to judge the {len(pool)} most-liked ...", flush=True)
        judge(car, pool)
        passed = sum(1 for c in pool if c["score"] > 0)
        print(f"   {passed} are real photos of the {car}")

    short = shortlist(pool, args.count * 2 if not args.no_judge else args.count)
    if args.no_judge or len(short) <= args.count:
        picks = short[:args.count]
    else:
        print(f"   curating the final {args.count} from a shortlist of {len(short)} ...", flush=True)
        picks = curate(car, short, args.count)
    if not args.no_download and picks:
        print(f"   downloading {len(picks)} originals ...", flush=True)
        download(picks, out_dir / "images")

    (out_dir / "refs.json").write_text(json.dumps({
        "car": car, "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "queries": queries, "picks": picks, "judged": pool,
    }, indent=1, ensure_ascii=False) + "\n")
    write_md(car, picks, pool, out_dir / "refs.md")
    write_html(car, picks, out_dir / "contact.html")

    print(f"\n   {len(picks)} references -> {out_dir.relative_to(ROOT)}\n")
    for i, c in enumerate(picks, 1):
        v = c["verdict"]
        print(f"   {i:>2}. {v['angle']:<10} fit {v['fit']}  q {v['quality']}  {c['likes']:>5} likes  "
              f"{c['pin_url']}")
        print(f"       {v['note']}")
    if len(picks) < args.count:
        print(f"\n   only {len(picks)} passed; raise --pool or add --query variants for more")


if __name__ == "__main__":
    main()
