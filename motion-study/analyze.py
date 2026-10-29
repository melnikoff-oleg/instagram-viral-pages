#!/usr/bin/env python3
"""
Clip-by-clip motion analysis of a reel with Gemini.

    python3 motion-study/analyze.py                         # every mp4 in motion-study/videos/
    python3 motion-study/analyze.py videos/iamnotsrc-1-batman.mp4
    python3 motion-study/analyze.py --model gemini-2.5-pro  # another model
    python3 motion-study/analyze.py --fps 10                # denser sampling (default 8)

For each video the script
  1. finds the hard cuts with ffmpeg scene detection (hints for the model, it verifies them),
  2. uploads the file to the Gemini Files API,
  3. asks the model for a shot-by-shot breakdown focused on the camera/subject
     relationship, subject speed, camera speed, what makes the frame dynamic,
     and what makes it look real,
  4. writes analysis/<name>.gemini.md (the model's report, verbatim) and
     analysis/<name>.gemini.json (the structured clip table parsed from it).

Keys come from the .env at the repo root: GEMINI_API_KEY, GEMINI_API_KEY_2, ... are tried in
order, and so are the models in MODELS, until a (key, model) pair answers (the first key is a
prepaid project that can run dry, the second is a free-tier key that only runs flash models).
`pip3 install google-genai` once. A 20 s reel at 8 fps is roughly 50k input tokens.
"""

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
VIDEOS = HERE / "videos"
OUT = HERE / "analysis"

MODELS = ["gemini-3.1-pro-preview", "gemini-3.6-flash", "gemini-3.5-flash",
          "gemini-3-flash-preview"]


def load_env():
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate:format=duration",
         "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    s = j["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return {"width": s["width"], "height": s["height"], "fps": round(int(num) / int(den), 3),
            "duration": round(float(j["format"]["duration"]), 3)}


def cuts(path, threshold=0.25):
    """Timestamps where ffmpeg's scene score exceeds the threshold."""
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vf",
         f"select='gt(scene,{threshold})',metadata=print:file=-", "-an", "-f", "null", "-"],
        capture_output=True, text=True).stdout
    times = [round(float(t), 2) for t in re.findall(r"pts_time:([0-9.]+)", out)]
    merged = []
    for t in times:
        if not merged or t - merged[-1] > 0.3:
            merged.append(t)
    return merged


PROMPT = """You are a cinematographer and VFX supervisor reverse-engineering a short vertical social video (9:16) that was made with AI video generation and cut together from several separate generated clips.

The video is "{title}". It lasts {duration} s at {fps} fps, {width}x{height}.
ffmpeg scene detection suggests hard cuts near these timestamps (seconds): {cuts}. Treat them as hints only: verify every cut by watching, add cuts it missed (including cuts between very similar shots), drop false ones.

Watch the whole video carefully, then write the analysis below. Be concrete and quantitative wherever you can: estimate how long the subject takes to cross the frame, how many frame-widths it travels per second, how far the camera turns in degrees, how fast the background slides. Prefer observations over adjectives. When unsure, say so.

Write the report in Markdown with exactly these sections:

# {title}

## 1. Overview
Subject, setting, time of day, weather, mood, colour palette, number of clips, average clip length, music/cut relationship if visible (cuts on hits?).

## 2. Clip by clip
For every clip, a block in this format:

### Clip N — MM:SS.s to MM:SS.s (D.D s)
- **Frame:** what is in frame at the first frame of the clip; framing (wide / medium / close / detail), lens feel (wide-angle, long lens), camera height (ground level, eye level, high).
- **Subject motion:** one of [linear travel, drift/slide, turn, action (shooting, jumping, transforming), stationary, stationary-but-camera-moves]; direction on screen (left→right, towards camera, away, diagonal); speed estimate (slow / real-time fast / very fast) with evidence (e.g. "crosses the full frame width in 0.8 s", "wheels blurred", "background streaks").
- **Camera motion:** one of [locked off, pan, tilt, tracking (parallel with subject), follow (behind), lead (in front), orbit/arc, dolly in/out, handheld, crash zoom]; speed and amount (e.g. "~30° arc over 3 s", "static"); whether it is a single move or changes mid-clip.
- **Camera–subject relationship:** how the two motions combine (e.g. "camera still, subject passes through frame", "camera tracks at matched speed so subject is near-static in frame while the background streaks", "subject still, camera orbits fast so the background sweeps", "subject moves toward a still camera, growing in frame").
- **Dynamism sources:** everything that adds motion energy besides the subject: dust, sand, sparks, rain, snow, smoke, debris, muzzle flash, headlight flare, light flicker, birds, crowd, cloth, hair. Rate the overall energy of the clip 1–5.
- **Realism cues:** what makes it look like real footage: motion blur, grain, lens flare, exposure behaviour, depth of field, shadow/lighting consistency, contact with ground, reflections, weight/physics, imperfections. Also list any AI tells you can see (morphing, wheel wobble, flicker, floating, wrong scale, texture swim) and rate realism 1–5.
- **Would a video model get this right?** one line: how simple/explicit the motion instruction is.

## 3. Structure and rhythm
Clip durations in order; how the first second works as a hook (is the subject readable immediately? is it already moving in the first frame?); screen direction consistency across cuts; whether the subject ever stands still and if so what the camera does; how the energy curve goes across the clips; how the video ends.

## 4. Patterns
The 5–10 rules this video seems to follow about motion, camera, speed and realism. Written as imperative rules someone could copy.

## 5. Clip table (JSON)
A fenced ```json block with a list of objects, one per clip:
{{"n": 1, "start": 0.0, "end": 3.0, "subject_motion": "...", "direction": "...", "subject_speed": "slow|real-time fast|very fast|static", "camera_motion": "...", "camera_speed": "static|slow|medium|fast", "relationship": "...", "dynamism": ["..."], "energy": 1-5, "realism": 1-5, "ai_tells": ["..."]}}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("videos", nargs="*", help="mp4 paths (default: all in motion-study/videos)")
    ap.add_argument("--model", action="append", help="model(s) to try, in order (default: MODELS)")
    ap.add_argument("--fps", type=float, default=8.0, help="frames per second the model sees")
    ap.add_argument("--force", action="store_true", help="redo videos that already have a report")
    args = ap.parse_args()

    load_env()
    keys = [v for k, v in sorted(os.environ.items()) if re.fullmatch(r"GEMINI_API_KEY(_\d+)?", k)]
    if not keys:
        sys.exit("GEMINI_API_KEY missing from .env")
    from google import genai
    from google.genai import types
    from google.genai import errors
    models = args.model or MODELS
    http = types.HttpOptions(retry_options=types.HttpRetryOptions(attempts=2))

    def ask(path, prompt):
        """Try every key, and for each key every model, until one answers. Returns (model, response)."""
        for ki, key in enumerate(keys, 1):
            client = genai.Client(api_key=key, http_options=http)
            try:
                f = client.files.upload(file=str(path))
                while f.state.name == "PROCESSING":
                    time.sleep(2)
                    f = client.files.get(name=f.name)
            except errors.APIError as e:
                print(f"   key {ki}: upload {e.code} {str(e)[60:120]}", flush=True)
                continue
            contents = [types.Content(role="user", parts=[
                types.Part(file_data=types.FileData(file_uri=f.uri, mime_type=f.mime_type),
                           video_metadata=types.VideoMetadata(fps=args.fps)),
                types.Part(text=prompt)])]
            try:
                for model in models:
                    try:
                        return model, client.models.generate_content(model=model, contents=contents)
                    except errors.APIError as e:
                        if e.code not in (402, 404, 429, 503):
                            raise
                        print(f"   key {ki} {model}: {e.code}", flush=True)
            finally:
                try:
                    client.files.delete(name=f.name)
                except Exception:
                    pass
        sys.exit("no working key/model pair")

    paths = [pathlib.Path(v) for v in args.videos] or sorted(VIDEOS.glob("*.mp4"))
    OUT.mkdir(exist_ok=True)
    for path in paths:
        name = path.stem
        md_out = OUT / f"{name}.gemini.md"
        if md_out.exists() and not args.force:
            print(f"skip {name} (exists)")
            continue
        meta = probe(path)
        hint = cuts(path)
        title = name.replace("-", " ")
        print(f"{name}: {meta['duration']} s, cuts≈{hint}", flush=True)
        prompt = PROMPT.format(title=title, duration=meta["duration"], fps=meta["fps"],
                               width=meta["width"], height=meta["height"],
                               cuts=", ".join(f"{t:.2f}" for t in hint) or "none found")
        t0 = time.time()
        model, resp = ask(path, prompt)
        text = resp.text or ""
        usage = resp.usage_metadata
        print(f"   {len(text)} chars in {time.time() - t0:.0f} s, "
              f"tokens in/out {usage.prompt_token_count}/{usage.candidates_token_count}", flush=True)
        header = (f"<!-- model {model}, {args.fps} fps sampling, generated {time.strftime('%Y-%m-%d %H:%M')} -->\n"
                  f"<!-- source {path.name}: {meta} ; ffmpeg cut hints {hint} -->\n\n")
        md_out.write_text(header + text)

        m = re.search(r"```json\s*(.*?)```", text, re.S)
        if m:
            try:
                clips = json.loads(m.group(1))
                (OUT / f"{name}.gemini.json").write_text(json.dumps(
                    {"video": path.name, "meta": meta, "ffmpeg_cuts": hint, "model": model,
                     "clips": clips}, indent=1, ensure_ascii=False))
            except json.JSONDecodeError as e:
                print(f"   clip table not parseable: {e}")


if __name__ == "__main__":
    main()
