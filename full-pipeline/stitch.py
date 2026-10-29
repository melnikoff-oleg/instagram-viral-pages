#!/usr/bin/env python3
"""Stitch the four clips of a run into one reel with a music track, using HyperFrames.

    python3 full-pipeline/stitch.py full-pipeline/runs/<run> --track music/01-wrath.m4a --name wrath
    python3 full-pipeline/stitch.py full-pipeline/runs/<run> --all          # every track in music/

What it does:
  1. Analyses the track with `hyperframes audio` (bpm, beats, downbeats) and an RMS
     envelope (ffmpeg), and finds the DROP: the downbeat with the biggest jump in
     energy between the bars before it and the bars after it.
  2. Snaps the cuts to the beat grid: every clip except the last is trimmed from the
     end to a whole number of beats (never longer than the clip), the last clip keeps
     its full length so the gag lands.
  3. Offsets the music so the drop lands exactly on a cut (--drop-at, default 1: the
     cut from the opener into the "play" clip, so the opener rides the build).
  4. Writes a HyperFrames project in <run>/hyperframes/<name>/ (clips at --clip-vol
     under the music at --music-vol, with a short fade in and out) and renders it to
     --out (default reels/<run-slug>/<run-slug>-<name>.mp4, 1080x1920).

Clips are read from <run>/clips/01.mp4 .. 04.mp4 (every numbered mp4 in clips/). Rendered reels and the hyperframes
projects are local only (git-ignored).
"""
import argparse, json, math, os, shutil, subprocess, sys
from pathlib import Path

HF = ["npx", "--yes", "hyperframes@0.8.212"]
ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 1920


def sh(cmd, quiet_stderr=False):
    return subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL if quiet_stderr else None).stdout


def probe_duration(path):
    out = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
    return float(out.strip())


def analyse_track(track):
    out = sh(HF + ["audio", str(track), "--only", "bpm,beats,downbeats", "--json"], quiet_stderr=True)
    item = json.loads(out)["items"][0]
    bpm = item.get("bpm", {}).get("value")
    downbeats = item.get("downbeats", {}).get("times") or []
    if not bpm or len(downbeats) < 12:
        # No usable beat grid (orchestral, ambient): search on a plain 1 s grid instead.
        bpm, downbeats = None, [round(t * 1.0, 3) for t in range(int(item["duration"]))]
    return {"bpm": bpm, "beats": item.get("beats", {}).get("times") or [],
            "downbeats": downbeats, "duration": item["duration"]}


def envelope(track, hop=0.05):
    """RMS energy per `hop` seconds, from mono 16-bit PCM."""
    import array
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(track), "-ac", "1", "-ar", "22050",
                          "-f", "s16le", "-"], check=True, capture_output=True).stdout
    pcm = array.array("h"); pcm.frombytes(raw[: len(raw) - len(raw) % 2])
    n = int(22050 * hop)
    env = []
    for i in range(0, len(pcm) - n, n):
        chunk = pcm[i:i + n]
        env.append(math.sqrt(sum(s * s for s in chunk) / n))
    return env, hop


def energy_between(env, hop, a, b):
    i, j = int(a / hop), max(int(b / hop), int(a / hop) + 1)
    seg = env[i:j]
    return sum(seg) / len(seg) if seg else 0.0


def find_drop(track, info, bars_before=4, bars_after=4, search_until=0.7):
    """The downbeat where the mean energy of the next bars most exceeds the previous bars."""
    env, hop = envelope(track)
    db = info["downbeats"]
    best, cands = None, []
    for k in range(bars_before, len(db) - bars_after):
        t = db[k]
        if t > info["duration"] * search_until:
            break
        before = energy_between(env, hop, db[k - bars_before], t)
        after = energy_between(env, hop, t, db[k + bars_after])
        jump = after - before
        cands.append((jump, t, before, after))
        if best is None or jump > best[0]:
            best = (jump, t, before, after)
    cands.sort(reverse=True)
    return {"time": best[1], "jump": best[0], "before": best[2], "after": best[3],
            "runners_up": [{"time": c[1], "jump": c[0]} for c in cands[1:4]]}


def plan_cuts(clip_durations, bpm, snap=True, min_beats=2, clip_max=None, clip_in=None):
    """Timeline durations for each clip: whole beats, never longer than what is left of the clip after its
    --clip-in offset (or its --clip-max), last clip full."""
    clip_max, clip_in = clip_max or {}, clip_in or {}
    clip_durations = [d - clip_in.get(i + 1, 0.0) for i, d in enumerate(clip_durations)]
    if not bpm:
        snap, period = False, 0.0
    else:
        period = 60.0 / bpm
    durs = []
    for i, d in enumerate(clip_durations):
        d = min(d, clip_max.get(i + 1, d))
        if not snap or (i == len(clip_durations) - 1 and (i + 1) not in clip_max):
            durs.append(round(d, 3))
        else:
            n = max(min_beats, int(math.floor((d - 0.02) / period)))
            durs.append(round(n * period, 3))
    starts = [round(sum(durs[:i]), 3) for i in range(len(durs))]
    return period, durs, starts


def write_project(proj, clips, track, durs, starts, media_start, clip_vol, music_vol, fade_in, fade_out, clip_in=None):
    clip_in = clip_in or {}
    assets = proj / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(clips, 1):
        shutil.copy2(c, assets / f"{i:02d}.mp4")
    shutil.copy2(track, assets / ("track" + track.suffix))
    total = round(starts[-1] + durs[-1], 3)
    videos = "\n".join(
        f'      <video id="c{i}" class="clip" src="assets/{i:02d}.mp4" playsinline data-has-audio="true" '
        f'data-start="{s}" data-duration="{d}" data-media-start="{clip_in.get(i, 0.0)}" data-track-index="0" '
        f'data-volume="{clip_vol}"></video>'
        for i, (s, d) in enumerate(zip(starts, durs), 1))
    lane = {"version": 1, "lanes": [{"target": "volume", "points": [
        {"t": 0, "v": 0}, {"t": fade_in, "v": 1}, {"t": round(total - fade_out, 3), "v": 1}, {"t": total, "v": 0}]}]}
    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>reel</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 100%; height: 100%; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; }}
      video.clip {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}" data-fps="24">
{videos}
      <audio id="music" src="assets/track{track.suffix}" data-start="0" data-duration="{total}" data-media-start="{media_start}" data-track-index="1" data-volume="{music_vol}" data-automation='{json.dumps(lane)}'></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.to("#root", {{ duration: {total} }}, 0);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (proj / "index.html").write_text(html)
    (proj / "hyperframes.json").write_text(json.dumps({
        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
        "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}}, indent=2))
    (proj / "meta.json").write_text(json.dumps({"id": proj.name, "name": proj.name}, indent=2))
    return total


def stitch(run, track, name, args):
    clips = sorted((run / "clips").glob("[0-9][0-9].mp4"))   # 01.mp4 .. 04.mp4 (any count)
    if not clips:
        sys.exit(f"no clips in {run / 'clips'} (expected 01.mp4 .. 04.mp4)")
    clip_durs = [probe_duration(c) for c in clips]

    print(f"== {name}: analysing {track.name} ...", flush=True)
    info = analyse_track(track)
    drop = find_drop(track, info)
    clip_max = {int(k): float(v) for k, v in (x.split("=") for x in (args.clip_max or []))}
    clip_in = {int(k): float(v) for k, v in (x.split("=") for x in (args.clip_in or []))}
    period, durs, starts = plan_cuts(clip_durs, info["bpm"], snap=not args.no_snap, clip_max=clip_max, clip_in=clip_in)
    cut_at = starts[args.drop_at] if args.drop_at < len(starts) else starts[-1] + durs[-1]
    media_start = round(drop["time"] - cut_at, 3)
    if media_start < 0:
        print(f"   drop at {drop['time']:.2f}s is too early for cut {args.drop_at}; starting the song on the drop")
        media_start, cut_at = round(drop["time"], 3), 0.0
    print(f"   bpm {info['bpm'] or 'none'} (beat {period:.3f}s)  drop at {drop['time']:.2f}s "
          f"(energy {drop['before']:.0f} -> {drop['after']:.0f})")
    print(f"   clips {['%.2f' % d for d in clip_durs]} -> on the grid {durs}")
    print(f"   music starts at {media_start}s so the drop lands at reel time {cut_at}s")

    proj = run / "hyperframes" / name
    if proj.exists():
        shutil.rmtree(proj)
    total = write_project(proj, clips, track, durs, starts, media_start, args.clip_vol, args.music_vol,
                          args.fade_in, args.fade_out, clip_in=clip_in)

    slug = run.name.split("-", 3)[-1]            # 2026-10-28-f40-colosseum -> f40-colosseum
    reel_dir = next(iter(sorted((ROOT / "reels").glob(f"*-{slug}"))), ROOT / "reels" / slug)
    out = Path(args.out) if args.out else reel_dir / f"{slug}-{name}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"   rendering {total}s -> {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out} ...", flush=True)
    subprocess.run(HF + ["render", str(proj), "-o", str(out), "--fps", "24", "--quality", args.quality, "--quiet"],
                   check=True)

    summary = {"name": name, "track": str(track.relative_to(run)), "bpm": info["bpm"], "beat": round(period, 4),
               "drop": drop, "drop_at_cut": args.drop_at, "media_start": media_start, "clip_durations": clip_durs,
               "clip_max": clip_max, "clip_in": clip_in,
               "timeline_durations": durs, "timeline_starts": starts, "total": total,
               "clip_vol": args.clip_vol, "music_vol": args.music_vol, "output": str(out)}
    (run / f"stitch-{name}.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(f"   done: {out}")
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("run", help="run folder, e.g. full-pipeline/runs/2026-10-28-f40-colosseum")
    ap.add_argument("--track", help="audio file, relative to the run folder or absolute")
    ap.add_argument("--name", help="variant name used in the output filename (default: track stem)")
    ap.add_argument("--all", action="store_true", help="stitch one reel per track in <run>/music/")
    ap.add_argument("--drop-at", type=int, default=1,
                    help="which cut the drop lands on: 0 = reel start, 1 = cut into clip 2 (default), ... 4")
    ap.add_argument("--no-snap", action="store_true", help="keep clips at full length, no beat snapping")
    ap.add_argument("--clip-in", action="append", metavar="N=SECONDS",
                    help="skip the first SECONDS of a clip, e.g. 2=0.8 drops a slow start (repeatable)")
    ap.add_argument("--clip-max", action="append", metavar="N=SECONDS",
                    help="cap a clip's timeline length, e.g. 1=1.6 cuts the opener right after the pass (repeatable)")
    ap.add_argument("--clip-vol", type=float, default=0.5, help="clip (engine, rain, pigeons) volume (default 0.5)")
    ap.add_argument("--music-vol", type=float, default=0.9, help="music volume (default 0.9)")
    ap.add_argument("--fade-in", type=float, default=0.25)
    ap.add_argument("--fade-out", type=float, default=0.8)
    ap.add_argument("--quality", default="delivery", help="hyperframes render quality (default delivery)")
    ap.add_argument("--out", help="output mp4 (single track only)")
    args = ap.parse_args()

    run = Path(args.run).resolve()
    if args.all:
        tracks = sorted(p for p in (run / "music").iterdir() if p.suffix.lower() in (".m4a", ".mp3", ".wav", ".aac"))
        if not tracks:
            sys.exit("no tracks in music/")
        for t in tracks:
            stitch(run, t, t.stem.split("-", 1)[-1] if "-" in t.stem else t.stem, args)
    else:
        if not args.track:
            sys.exit("--track or --all")
        t = Path(args.track)
        t = t if t.is_absolute() else run / t
        stitch(run, t, args.name or t.stem, args)


if __name__ == "__main__":
    main()
