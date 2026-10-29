# Instagram profile preview (local clone)

A static, clickable desktop recreation of the Instagram profile page, showing your draft account before it exists on Instagram. The studio embeds it in the Packaging card and opens it with "Open full preview".

- `me.html`: your draft account (data in `my-account.js`, media in `assets/mine/`)

## Run on its own
    ./instagram-preview/serve.sh          (from the project folder; builds, serves on :8787 and opens me.html)

## Edit your draft
- `my-account.js` holds everything shown: handle (`HANDLE`, one place), bio, note, counts, avatar and the post list
  (`file`, `kind` = image | carousel | reel, `pinned`, `caption`, `label`). Edit it and reload the page.
- Reels: put the mp4 in `assets/mine/` (H.264), a 3:4 cover jpg next to it, set `video`, `audio` ("handle • Original audio"),
  `taken_at` (unix seconds, drives the "x hours ago" text). Opening a reel autoplays it with sound.
- Comments: `thread` is a list of `{user, text, ago, likes, replies}`; `self: true` renders the comment as the account itself.
- `assets/mine/profile.jpg` is the profile picture (made in step 3 from your headshot plus the style references);
  `profile-alt-1.jpg` and `profile-alt-2.jpg` are the other variants from the same run.

## Files
- `template.html` + `build.py` generate `me.html` (the SVG icon sprite from `assets/svgs.json` is inlined).
  Only re-run `python3 build.py` if you change `template.html`; `my-account.js` is read live and never regenerated.
