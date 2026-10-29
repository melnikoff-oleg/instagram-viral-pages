# Viral Page Studio

A window onto Claude Code that builds a viral Instagram theme page from nothing: the idea, the packaging (username, profile picture, bio), the first reels, the posting routine, and later the autopilot. You talk in the middle; the page fills in on the right; the seven steps on the left tell you where you are.

It is a thin wrapper and nothing more. The work is done by Claude Code inside this folder, with the Higgsfield MCP for images and video, and a few small Python scripts for the repeatable parts (username checks, music research, reference photos, stitching).

If you have never opened a terminal, there is a click-by-click version of everything below, one step at a time:
**https://oleg.ae/instagram-viral-pages**

This folder is the starter. The account it was built for is in its own repository; its concept, its prompts and one complete run are included here as the worked example.

## What you need

1. **Claude Code, version 2.1 or newer**: `curl -fsSL https://claude.ai/install.sh | bash` on macOS and Linux, `irm https://claude.ai/install.ps1 | iex` in PowerShell on Windows. Run `claude` once in a terminal and sign in. It needs a Claude subscription (Pro or better; the free plan does not include Claude Code). This is the thing that does the work, so `claude --version` has to print a number before anything else will.
2. **Python 3** (already on macOS and Linux; python.org on Windows), with `pip3 install pillow`.
3. **The Higgsfield MCP**, which is where the images and the video come from. Connecting it has two parts. In a terminal: `claude mcp add --scope user --transport http higgsfield https://mcp.higgsfield.ai/mcp` (it prints `Added HTTP MCP server higgsfield`). Then start `claude`, type `/mcp`, put the cursor on **higgsfield**, press Enter, pick **Authenticate**, sign in on higgsfield.ai in the browser and approve; the line now says connected. Check from the terminal with `claude mcp list`: the higgsfield line must end in `✔ Connected`. `! Needs authentication` means the second part did not happen. `--scope user` matters: without it the server is tied to the folder the line was run in, and Claude Code started in this folder would not see it. A Higgsfield plan with credits; a full reel is about 85 credits.
4. **The Higgsfield CLI**, only so the studio can show your balance: `npm install -g @higgsfield/cli` (or the installer on higgsfield.ai), then `higgsfield auth login`. Everything else works without it.
5. **An Apify key** (console.apify.com, free tier is enough; Settings → API & Integrations → Personal API token, it starts with `apify_api_`): username checks, Pinterest references and music research run through Apify actors, for cents per run. It goes into the `.env` file, see **Keys** below.
6. **ffmpeg, node 22 and yt-dlp** for the reels: `brew install ffmpeg node yt-dlp` on a Mac. Claude Code will install what is missing if you ask it.

## Get it

    git clone https://github.com/melnikoff-oleg/instagram-viral-pages.git

No git? Open the GitHub page, press the green **Code** button, choose **Download ZIP**, unzip it, and put the folder somewhere you will find it again (Documents is fine; the name does not matter).

Everything happens inside this folder. Claude Code works on the folder it is started in and nothing else: it reads the instructions here, writes your concept and reels here, and the studio serves from here. So the order is always the same three moves:

1. **Open the folder in VS Code**: File → Open Folder (Open on a Mac), pick it, trust the authors.
2. **Open a terminal inside it**: Terminal → New Terminal. The prompt ends with the folder name.
3. **Start Claude Code in that terminal**: type `claude` and press Enter. The welcome box shows the folder's path.

The same three moves bring you back tomorrow.

## Keys: the `.env` file

The scripts read your keys from one small file called `.env` at the top level of this folder, next to this README. It is not in the download; you create it:

1. In VS Code, right-click the empty space under the file list (the Explorer) → **New File**. Name it exactly `.env`: a dot, then `env`, nothing else.
2. Paste one line per key, `NAME=value`, no spaces around the equals sign, no quotes, nothing else on the line:

       APIFY_API_KEY=apify_api_xxxxxxxxxxxxxxxxxxxxxxxx

3. Save. That is all for today.

The name must be exactly `APIFY_API_KEY`, in capitals; that is what the scripts look for. An optional second line, `GEMINI_API_KEY=...` (free tier at aistudio.google.com/apikey), is only for the motion analysis in the autopilot stage; skip it until then. The **Keys** button at the top right of the studio writes the same file for you if you prefer to paste the key there. `.env` is git-ignored, so it never leaves your machine, and Claude Code is told never to print a key back. Files starting with a dot are hidden by Finder and Windows Explorer; VS Code shows them. On Windows, if it came out as `.env.txt`, rename it to `.env`.

Not needed, ever: an Anthropic API key. Nothing here calls the Claude API; Claude Code runs on your subscription.

## Run

The first time, with Claude Code started in the folder, paste:

> Set up Viral Page Studio for me. You are inside its folder. Read its README, install anything I am missing (Python 3 with pillow, ffmpeg, Node 22, yt-dlp, the Higgsfield CLI), check that the Higgsfield MCP is connected, start the studio, and tell me which link to open.

It installs what is missing, starts the studio and hands you http://localhost:8788. Say yes when it asks permission.

Every time after that, the same three moves and **"start the studio"** in Claude Code; it knows what that means. Or, without Claude Code, in the terminal inside the folder:

    python3 studio/serve.py

Then open http://localhost:8788. On a Mac, double-click `start.command` instead; it checks what is installed, starts the studio and opens the browser. Whichever way it was started, the terminal it leaves behind is the engine; closing it stops the studio.

## How it goes

1. **Choose the idea.** Press "Help me find my idea" and answer a few questions, or start from the example (iconic cars in iconic places). The Concept card fills.
2. **Pick the vibe.** The default style references are already in `references/visual-style/`. Drop your own if you want a different look.
3. **Build the packaging.** A free username (checked against Instagram's own signup form), a profile picture made from your headshot in the same world as the content, a bio with no hype. The Packaging card shows a live preview of the profile page.
4. **First 3 reels.** Each one is the full pipeline: a plan, a reference photo, 16 candidate frames, your 4 picks, 4 clips of 5 seconds, music, a stitched reel with a cover. About 85 Higgsfield credits and 40 minutes each. After each one: judge it, improve the prompts.
5. **Create the account, start posting.** Through the Edits app at first, one reel a day. Keep going.
6. **After about 100k views: autopilot.** Blotato posts on a schedule; an Apify + Gemini loop reads your numbers and tunes the prompts. Claude builds it with you when you get there.
7. **After about 1M views: monetize.**

## What is where

| Folder | What |
|--------|------|
| `studio/` | The app. `serve.py` is a standard-library Python server that runs `claude -p` and streams it to the page. |
| `concept/` | Your concept (`instagram-concept.md`, written in step 1), the example, the image prompt template. |
| `references/` | Style references and your headshot. |
| `instagram-preview/` | A static clone of the Instagram desktop profile page, showing your draft account. |
| `username-finder/`, `music-finder/`, `pinterest-refs/` | The Apify-backed scripts. |
| `full-pipeline/` | The reel pipeline: scripts, prompt templates, one folder per run. `runs/example-mustang-monument-valley/` is a complete worked example. |
| `motion-study/` | The motion rulebook (`sop.md`) and the evidence behind it. |
| `reels/` | Finished series, numbered in posting order. |
| `CLAUDE.md` | The instructions Claude Code reads in this folder. `AGENTS.md` points Codex at the same file. |

## If something is wrong

- **"Claude Code is not installed"** in the chat: run `claude` in a terminal; until that works, the studio cannot.
- **The balance pill says unknown**: the Higgsfield CLI is missing or not signed in (`higgsfield auth login`). Generation still works through the MCP.
- **"Higgsfield MCP missing"** at the top: Claude Code does not see the server. `claude mcp list` in the terminal says which part is missing: no higgsfield line, run the `claude mcp add` line above (with `--scope user`); `! Needs authentication`, start `claude`, `/mcp`, Authenticate.
- **A step says a key is missing**: the `.env` file (see **Keys** above), or the Keys button at the top right, which writes it for you.
- **Port 8788 is busy**: `python3 studio/serve.py --port 8790`.
- Anything else: say it in the chat. Claude Code wrote the setup and can read its own errors.

## Costs, honestly

- Claude: your subscription. A reel is a long session; Pro manages a reel or two a day, Max does not notice.
- Higgsfield: about 85 credits per reel (16 frames at 1.5, 4 draft clips of 5 s at about 15). Three reels for the launch is about 250 credits.
- Apify: a few cents per Pinterest or music run, about a dollar per 100 username checks.
