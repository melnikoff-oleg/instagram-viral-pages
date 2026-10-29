# full-pipeline

One reel, start to finish: idea → 4-frame plan → Pinterest reference → 16 Flux candidates →
4 picks → 4 Seedance clips of 5 s → music → 3 stitched reels (about 20 s). Everything repeatable is a script here,
everything that needs taste (the idea, the picks, the prompts) is Claude in a Claude Code session
with the Higgsfield MCP, and every run keeps its own folder under `runs/` so the next run can copy it.

The latest run is `runs/2026-10-29-mustang-monument-valley/` (1967 Mustang Fastback × Monument Valley), the first on the
4 × 5 s structure. Read its `plan.md`, `prompts/`, `jobs.json` and `run.md` for a complete worked example;
`runs/2026-10-28-f40-colosseum/run.md` lists what went wrong before the current rules.

## The steps

| # | Step | Who | Where it lands |
|---|------|-----|----------------|
| 1 | **Idea.** Read `concept/instagram-concept.md`, list the pairings already made (`reels/README.md`), pick a new iconic car × iconic place. Colour rule, instant recognition, a weather story. | Claude | `runs/<run>/plan.md` |
| 2 | **Four frames.** Opener, play, peak, funny ending, each with a shot code from `motion-study/sop.md` §4. One screen direction, light and weather progressing, landmark in at least 3 of 4. | Claude | `runs/<run>/plan.md` |
| 3 | **Car reference.** `python3 pinterest-refs/find-refs.py "<car>" --screen 60` (no Claude API: Apify search, the 60 most-liked laid out on numbered sheets), look at the sheets in the session, then `--pick <n>`. ONE photo that shows the whole car cleanly (shape, lights, wheels, wing), real, no text. Pick one that already faces the screen direction you want: Flux copies the reference's orientation. | script + Claude (in session) | `runs/<run>/refs/car.jpg` |
| 4 | **Style references.** `references/visual-style/2.png` and `3.png`, saved as JPG next to the car. | fixed | `runs/<run>/refs/style-2.jpg`, `style-3.jpg` |
| 5 | **Upload.** `media_upload` (3 files) → `curl PUT` each → `media_confirm`. A 400 on the PUT means a stale URL, ask for a new one. | MCP | media ids in `runs/<run>/jobs.json` |
| 6 | **Image prompts.** One CTLT prompt per frame (Camera → Tone → Lighting → Texture), with the reference header on top. Template in `prompts/image-prompt-template.md`. | Claude | `runs/<run>/prompts/images.json` |
| 7 | **Generate images.** `generate_image_batch`, model `flux_2`, `variant: pro`, `resolution: 2k`, `aspect_ratio: 9:16`, medias `[car, style-2, style-3]` all with role `image_references`, 4 requests per frame, index = frame×10 + candidate (11..44). Two batches (8 + 8). 1.5 credits each, 24 for the run. | MCP | job ids in `jobs.json` |
| 8 | **Fetch and judge.** `jobs_wait`, then `python3 full-pipeline/fetch-results.py <run> candidates <index>=<url> ...` and `python3 full-pipeline/contact-sheet.py <run>`. Look at each row, pick one per frame: car correct, landmark readable (the opener must have both large, it is the reel's first frame), one hot light, nothing tack sharp, screen direction consistent, physics believable. | script + Claude (in session) | `runs/<run>/candidates/`, `selected/01..04.jpg` |
| 9 | **Video prompts.** GOAL → SHOT (timecodes) → CAMERA → STYLE → AUDIO → EXCLUSIONS, written to the frames actually picked, 5 s, no music. Real-time speed with a number, one camera behaviour with a constant angle on the car (`motion-study/sop.md`), "No slow motion, no gentle movement". Template in `prompts/video-prompt-template.md`, house examples in `prompts/reference-video-prompts.md`. | Claude | `runs/<run>/prompts/videos.json` |
| 10 | **Generate videos.** Generate the opener alone first and check that its first frame is the picked image; then the rest. `generate_video_batch`, model `seedance_2_5`, `draft: true`, `resolution: 480p`, `duration: 5`, `aspect_ratio: 9:16`, `generate_audio: true`, media = the selected image's job id with role **`image`** (`start_image` gets redrawn). One shot per frame; a 4 s draft was 12 credits, so expect about 15 for 5 s (check the quote; 720p and 1080p scale the same way). If the server answers with a preset recommendation instead of a job, resend with `declined_preset_id`. | MCP | `jobs.json` → `clips/01..04.mp4` |
| 11 | **Music.** `python3 music-finder/find-music.py "<topic>" --search "dark phonk" --search "<place word>" ...` (no Claude API: you write the 12 searches, the shortlist is round-robin, the table is ranked by usage), pick 3 tracks from the table (two from the house sound, one that plays with the place), `python3 full-pipeline/get-music.py <run> "<artist> <title>" ...` downloads them with yt-dlp for the local cut. Listen before posting. | script + Claude (in session) | `runs/<run>/music/` |
| 12 | **Stitch.** `python3 full-pipeline/stitch.py <run> --all` builds one HyperFrames project per track, finds the drop, snaps the cuts to the beat and renders 1080×1920. `--clip-max N=s` cuts a clip that goes quiet after its action (the opener after the pass), `--clip-in N=s` skips a slow start. | script | `reels/<nn>-<slug>/<slug>-<track>.mp4` |
| 13 | **Cover and preview.** `python3 full-pipeline/cover.py <reel.mp4> <cover.jpg>` for the 3:4 cover, then add the post to `instagram-preview/my-account.js`. | script + Claude | `reels/<nn>-<slug>/cover.jpg` |
| 14 | **Write it up and commit.** `runs/<run>/run.md` with picks, credits and what to do differently. Commit everything except video and audio. | Claude | git |

## No Anthropic API

Nothing in this pipeline calls the Claude API. The judging (Pinterest screen, candidate picks, music picks) is done by Claude in the Claude Code session by looking at contact sheets and tables. `pinterest-refs` and `music-finder` keep their API modes for standalone use, but the pipeline uses `--screen/--pick` and `--search`.

## Costs (per run, 4 × 5 s structure; the F40 and R34 runs were 5 × 4 s: 30 + 60 credits)

| What | Credits / $ |
|------|-------------|
| 16 Flux 2 pro 2K images | 24 credits |
| 4 Seedance 2.5 draft 480p clips of 5 s | about 60 credits |
| Pinterest refs | under $0.10 Apify + ~$0.20 Claude |
| Music finder | $0.63 Apify |

Finalising a draft clip to 1080p is a separate Seedance call with `draft_job_id` (within seven days); not done here.

## How the stitch decides

- `hyperframes audio` gives BPM, beats and downbeats. An RMS envelope (ffmpeg) gives energy.
- The **drop** is the downbeat where the mean energy of the next 4 bars most exceeds the previous 4 bars, searched in the first 70% of the track.
- The music is offset so the drop lands on a cut: `--drop-at 1` (default) is the cut from the opener into the "play" clip, so the opener rides the build and the drop hits with the action. `--drop-at 0` starts the reel on the drop.
- Cuts snap to the beat: each clip except the last is trimmed from the end to a whole number of beats (never longer than the clip). The last clip keeps its full length so the gag lands. Tracks with no detectable beat (orchestral) keep every clip at full length and search the energy swell on a 1 s grid.
- Clip audio (engine, rain, pigeons) stays under the music at `--clip-vol 0.5`, music at `--music-vol 0.9`, with a short fade in and out.
- Every decision is written to `runs/<run>/stitch-<track>.json`.

## What's local only

`runs/*/candidates/`, `runs/*/clips/`, `runs/*/hyperframes/`, `runs/*/selected/*.png`, `runs/*/music/*.m4a` and
all of `reels/**/*.mp4` are git-ignored. The picks are kept as JPG, the contact sheet is kept, and every job id
is in `jobs.json`, so anything can be re-downloaded from Higgsfield.

## Setup

- Higgsfield MCP connected in Claude Code (`generate_image_batch`, `generate_video_batch`, `jobs_wait`, `media_upload`, `media_confirm`).
- `ffmpeg`, `node` 22 (`npx hyperframes@0.8.212` installs itself on first use, Chrome headless shell is downloaded by it), `yt-dlp`, `pip3 install pillow`.
- `.env` with `ANTHROPIC_API_KEY` and `APIFY_API_KEY` for the Pinterest and music finders.
