# Viral Page Studio

One viral Instagram theme page, built end to end from this folder: the concept, the packaging, the reels, the posting routine, the autopilot. The person working with you is probably not a programmer. The local studio (`studio/`) is their window onto you: it shows the project as cards (Concept, References, Packaging with a live profile preview, Reels), runs you headlessly inside this folder, and fills the cards from the files you write. **Where you write a file decides what they see.** The list of paths is in `studio/system-prompt.md`.

`concept/instagram-concept.md` is the source of truth for the creative direction once it exists. Read it before generating or judging any image, video, caption or profile asset. Until it exists, the only job is to make it (step 1).

## The seven steps

1. **Choose the idea.** `concept/instagram-concept.md`, in the shape of `concept/examples/iconic-cars-x-iconic-places.md` (the worked example this system was built on: iconic cars in iconic places, shot like stills from a film that was never made).
2. **Pick the vibe** (optional). `references/visual-style/` holds the default set; the person can replace it. `references/README.md` describes the look in words.
3. **Build the packaging.** A free username (`username-finder/`), a profile picture in the same world as the content (Higgsfield, from `references/headshot.*` plus the style references), a bio with no hype. All of it lands in `instagram-preview/my-account.js` and `instagram-preview/assets/mine/`, and the preview (`instagram-preview/me.html`) shows how it reads.
4. **First 3 reels.** `full-pipeline/README.md` is the procedure, `full-pipeline/runs/example-mustang-monument-valley/` the worked example, `motion-study/sop.md` the motion rules. After every reel, judge it and improve the prompts.
5. **Create the account and start posting**, through the Edits app at first, one reel a day. Keep going; improve from the numbers.
6. **Autopilot after about 100k views**: Blotato publishing, an Apify + Gemini loop that reads the performance and tunes the prompts. Built with the person when they get there (`publishing/`, `analytics/`).
7. **Monetize after about 1M views**: referral links, a digital product, a service (`monetization/`).

## Layout

| Path | What it is |
|------|------------|
| `studio/` | The local app: `serve.py` (standard-library server that runs `claude -p` and streams it), `index.html` + `app.js` + `style.css`, `steps.json` (the buttons under the chat and their prompts), `system-prompt.md` (what you are told on every turn). Do not change it unless asked. |
| `concept/` | `instagram-concept.md` (written in step 1), `examples/` (our concept and its raw idea list), `ctlt-image-prompt-template.md` (Camera → Tone → Lighting → Texture, the shape of every image prompt). |
| `references/` | `visual-style/` (style references, never posted), `headshot.*` (the person's face, dropped in the studio), `README.md` (the look in words). |
| `instagram-preview/` | Static, clickable clone of the Instagram desktop profile page. `me.html` shows `my-account.js`; `build.py` rebuilds it from `template.html` (only after editing the template). |
| `username-finder/` | Proposes handles and checks them with Instagram's own signup check through Apify. `results/checked.json` is the memory across rounds. |
| `music-finder/` | Finds viral Instagram tracks for a video topic through Apify; you write the searches (`--search`), the table is ranked by usage. |
| `pinterest-refs/` | Finds real photos of a subject for reference (`--screen 60`, then `--pick <n>`). |
| `full-pipeline/` | One reel start to finish: idea → 4 frames → reference → 16 image candidates → 4 picks → 4 clips of 5 s → music → stitched reels. Scripts for the repeatable parts, prompt templates in `prompts/`, one folder per run under `runs/`. |
| `motion-study/` | `sop.md` is the rulebook for every frame and clip (allowed motions, camera behaviours, speed numbers, realism checklist, prompt blocks). `findings.md` and `analysis/` are the evidence. `analyze.py` runs a Gemini clip-by-clip report. |
| `reels/` | One numbered folder per finished series (`01-slug`, `02-slug`): the mp4s (local only) and `cover.jpg`. `README.md` lists every series with its caption, music and status. |
| `posting/`, `publishing/`, `analytics/`, `monetization/` | Steps 5 to 7, created when they are reached. |

## Studio and preview

```
./start.command                         # macOS: double-click; starts the studio on :8788 and opens it
python3 studio/serve.py                 # any OS; --port, --no-open, --project <folder>
./instagram-preview/serve.sh            # the profile preview alone, on :8787
```

- The studio runs you with `claude -p ... --permission-mode dontAsk` and an allowlist (file tools, Bash, web, the Higgsfield MCP). Nothing may block on a permission prompt; if a tool is denied, say which one, do not retry it blindly.
- The person's messages come with a state summary (which step is current, what exists, the balance, which keys are set). Trust it; do not re-explore the folder to find out.
- Keys live in `.env` at the root (`APIFY_API_KEY`, `GEMINI_API_KEY`), written from the Keys box in the studio. Never ask the person to edit `.env`, never print a key. No Anthropic API key is needed anywhere: the scripts' `--check`, `--search`, `--screen/--pick` modes keep the judgement in this session.

## Generation tooling

- Images and video go through the Higgsfield MCP. Default image model `gpt_image_2_5` with `image_references` (identity or subject first, style references after); frames for reels: `flux_2` pro 2k (`generate_image_batch`); clips: `seedance_2_5` draft 480p 5 s (`generate_video_batch`, the picked frame with role `image`). Upload local files with `media_upload` → curl PUT → `media_confirm`; a 400 on the PUT means a stale presigned URL, request a new one.
- Credits are the person's money: about 1.5 per image, about 15 per 5 s draft clip, about 85 per reel. Check the balance before generating (`higgsfield account status --json`, or the MCP balance tool), say the expected cost, never spend more than 150 credits in one turn without a go, stop under 100.
- Download every result you keep into the project with curl. Generated originals stay out of git except what the preview uses (`*.mp4` is git-ignored; job ids in `runs/<run>/jobs.json` let anything be re-downloaded).

## Packaging conventions

- **Caption** = title line, blank line, 3–4 lowercase hashtags. Title is `Subject × Place` (or the concept's own formula). No description, no emojis in the title.
- **Label** under the username in the dialog: `AI content`. Audio line: `handle • Original audio`.
- **Bio**: lowercase, one idea per line, three lines, no hype. Category `Digital creator`. The note bubble is short and cheeky.
- **Profile picture**: the person's face lit by the one warm light that belongs to the concept, the concept's sky behind, heavy film grain, a hint of the subject behind. Same look as the content, so the avatar and the grid read as one world. No headshot: a faceless version from the concept, and say so.
- **Comments** in `thread` are placeholder voices for judging how the packaging reads: short, lowercase, reaction-style; the account replies in the same cheeky tone.

## Content rules (short version; the concept doc and `motion-study/sop.md` have the full lists)

- Always vertical 9:16. Subject and place readable in the first second. The landmark visible from frame 0.
- One look, defined by the concept and the references: for the default set, a twilight gradient sky, dark warm ground, one hot warm light that belongs to the subject, coarse grain, nothing tack sharp.
- A series is **4 frames → 4 clips of 5 s** (opener, play, peak, funny ending), about 20 s stitched. Screen direction stays consistent.
- **Motion:** the subject is always moving fast or sliding, never standing (one exception: a still subject with a fast camera, once per reel, never first or last). One camera behaviour per clip, the angle on the subject never changes. No orbits around a moving subject, no jumps, nothing airborne, closest pass 2 m, at least one emitter (dust, spray, smoke, sparks, lights) per clip, the same weather in every clip. **Wheels and rims visibly spinning in every SHOT line and "No frozen wheels" in EXCLUSIONS** (a moving car with static rims is the ugliest tell; reject on sight). **Near layers in every clip:** something 5–30 m from the subject that streaks and something 1–3 m from the lens that whips past; a distant landmark alone gives no motion. **Cut contrast:** the first frames of consecutive clips differ in at least two of angle, size, lens/height, vector.
- Image prompts: four short paragraphs, Camera → Tone → Lighting → Texture; `@image1` is the subject, the other references are style only. Video prompts: GOAL → CONTINUITY → SHOT → CAMERA → STYLE → AUDIO → EXCLUSIONS, 5 s, no music, no text; real-time speed with a number; the camera does not move from its spot (never name a tripod or any equipment); the first SHOT line says the first frame is exactly the picked image; a [CONTINUITY] floor-plan line (camera spot, the subject's line, where the landmark is): passed objects never return, the landmark never jumps sides, the heading changes only by driving and survives dust unchanged. Generate the opener alone first and check its first frame.
- The image model copies the reference photo's orientation. Pick or mirror the reference to match the screen direction before generating.
- Music is added in Instagram at upload, never baked into the file. Nobody has listened to a track the finder returns; the person listens before posting.

## Naming and git

- Every file and folder is lowercase with dashes. Series folders are numbered in posting order.
- When this folder is a git repository, commit after every finished action with a one-line message that describes the user-visible change. Video and audio never go into git.
