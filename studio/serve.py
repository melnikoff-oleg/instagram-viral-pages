#!/usr/bin/env python3
"""Viral Page Studio: a local window onto Claude Code for building one viral Instagram page.

    python3 studio/serve.py                   # the folder this file lives in is the project
    python3 studio/serve.py --project ..      # any other project folder with the same layout
    python3 studio/serve.py --port 8788 --no-open

The browser page (studio/index.html) shows the project's parts (concept, references, packaging, reels),
a chat that runs Claude Code headlessly inside the project folder, and the Higgsfield balance.
Nothing here is clever: the server reads files, spawns `claude -p` and streams what it says.
Standard library only, so it runs wherever Python 3 does.
"""
import argparse
import json
import mimetypes
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

STUDIO = Path(__file__).resolve().parent
PROJECT = STUDIO.parent  # overridden by --project
STATE_DIR_NAME = '.studio'  # per-project: chats/<id>/ (session id + history), manual step marks (git-ignored)

# Tools the headless agent may use without asking. dontAsk denies everything else, so this list is the
# whole permission surface. Bash is unscoped because the pipeline shells out to python, ffmpeg and node.
# The MCP entries cover the Higgsfield server under the names it usually gets (a claude.ai connector, or
# `claude mcp add higgsfield ...`).
ALLOWED_TOOLS = ','.join([
    'Read', 'Write', 'Edit', 'MultiEdit', 'Glob', 'Grep', 'Bash', 'WebFetch', 'WebSearch',
    'Skill', 'Task', 'TodoWrite', 'NotebookEdit',
    'mcp__claude_ai_Higgsfield', 'mcp__higgsfield', 'mcp__Higgsfield', 'mcp__higgsfield-ai',
])

# Where the agent may be installed when the server is started by a double-click (no shell profile).
for extra in [str(Path.home() / '.local' / 'bin'), '/opt/homebrew/bin', '/usr/local/bin',
              str(Path.home() / '.npm-global' / 'bin'), '/opt/homebrew/opt/node@22/bin']:
    if extra not in os.environ.get('PATH', ''):
        os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + extra


# ---------------------------------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------------------------------

def run(cmd, timeout=20, cwd=None):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError:
        return 127, '', f'{cmd[0]}: not found'
    except subprocess.TimeoutExpired:
        return 124, '', f'{cmd[0]}: timed out'
    except Exception as e:  # noqa: BLE001
        return 1, '', str(e)


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(PROJECT))
    except ValueError:
        return str(p)


def file_url(p: Path) -> str:
    return '/files/' + urllib.parse.quote(rel(p))


def state_dir() -> Path:
    d = PROJECT / STATE_DIR_NAME
    d.mkdir(exist_ok=True)
    return d


def read_json(p: Path, default):
    try:
        return json.loads(p.read_text())
    except Exception:  # noqa: BLE001
        return default


def write_json(p: Path, data):
    p.write_text(json.dumps(data, indent=1, ensure_ascii=False))


IMAGE_EXT = {'.jpg', '.jpeg', '.png', '.webp'}


# ---------------------------------------------------------------------------------------------------
# Project state: what exists in the folder, read fresh on every request
# ---------------------------------------------------------------------------------------------------

class Cached:
    """A value recomputed at most every `ttl` seconds (tool versions, the balance)."""

    def __init__(self, fn, ttl):
        self.fn, self.ttl, self.at, self.value = fn, ttl, 0.0, None
        self.lock = threading.Lock()

    def get(self, force=False):
        with self.lock:
            if force or time.time() - self.at > self.ttl:
                self.value = self.fn()
                self.at = time.time()
            return self.value


def _tools():
    checks = {
        'claude': ['claude', '--version'],
        'higgsfield': ['higgsfield', 'version'],
        'ffmpeg': ['ffmpeg', '-version'],
        'node': ['node', '-v'],
        'python3': ['python3', '--version'],
        'yt-dlp': ['yt-dlp', '--version'],
    }
    out = {}
    for name, cmd in checks.items():
        rc, so, se = run(cmd, timeout=15)
        first = (so or se).strip().splitlines()[0] if (so or se).strip() else ''
        out[name] = {'ok': rc == 0, 'version': re.sub(r'^[^\d]*', '', first)[:40] if rc == 0 else None}
    return out


def _balance():
    rc, so, se = run(['higgsfield', 'account', 'status', '--json'], timeout=25)
    if rc == 127:
        return {'ok': False, 'error': 'Higgsfield CLI is not installed', 'at': time.time()}
    if rc != 0:
        msg = (se or so).strip().splitlines()[-1:] or ['not signed in']
        return {'ok': False, 'error': msg[0][:160], 'at': time.time()}
    try:
        d = json.loads(so)
    except Exception:  # noqa: BLE001
        return {'ok': False, 'error': 'unexpected answer from the Higgsfield CLI', 'at': time.time()}
    return {'ok': True, 'credits': d.get('credits'), 'plan': d.get('subscription_plan_type'),
            'email': d.get('email'), 'at': time.time()}


TOOLS = Cached(_tools, 300)
BALANCE = Cached(_balance, 90)


def env_status():
    env = PROJECT / '.env'
    keys = {}
    if env.exists():
        for line in env.read_text().splitlines():
            m = re.match(r'^\s*([A-Z0-9_]+)\s*=\s*(.*)$', line)
            if m:
                keys[m.group(1)] = bool(m.group(2).strip().strip('"\''))
    return {
        'exists': env.exists(),
        'APIFY_API_KEY': keys.get('APIFY_API_KEY', False),
        'GEMINI_API_KEY': keys.get('GEMINI_API_KEY', False) or keys.get('GEMINI_API_KEY_2', False),
    }


def set_env(values: dict):
    env = PROJECT / '.env'
    lines = env.read_text().splitlines() if env.exists() else ['# Keys for the scripts. Never commit this file.']
    for k, v in values.items():
        if not re.match(r'^[A-Z0-9_]+$', k):
            continue
        v = v.strip()
        for i, line in enumerate(lines):
            if re.match(rf'^\s*{k}\s*=', line):
                lines[i] = f'{k}={v}'
                break
        else:
            lines.append(f'{k}={v}')
    env.write_text('\n'.join(lines).rstrip('\n') + '\n')
    try:
        os.chmod(env, 0o600)
    except OSError:
        pass


def concept_info():
    p = PROJECT / 'concept' / 'instagram-concept.md'
    examples = sorted(x.name for x in (PROJECT / 'concept' / 'examples').glob('*.md')) if (PROJECT / 'concept' / 'examples').exists() else []
    if not p.exists():
        return {'exists': False, 'examples': examples}
    text = p.read_text(errors='replace')
    lines = text.splitlines()
    title = next((l[2:].strip() for l in lines if l.startswith('# ')), p.stem)
    sections = [l[3:].strip() for l in lines if l.startswith('## ')]
    one = ''
    for i, l in enumerate(lines):
        if l.startswith('## ') and 'one line' in l.lower():
            one = next((x.strip() for x in lines[i + 1:] if x.strip()), '')
            break
    if not one:
        one = next((l.strip() for l in lines if l.strip() and not l.startswith('#')), '')
    return {'exists': True, 'path': rel(p), 'url': file_url(p), 'title': title, 'oneLiner': one[:300],
            'sections': sections[:14], 'words': len(text.split()),
            'modified': int(p.stat().st_mtime), 'examples': examples}


def references_info():
    style_dir = PROJECT / 'references' / 'visual-style'
    style = []
    if style_dir.exists():
        for f in sorted(style_dir.iterdir(), key=lambda x: (len(x.stem), x.name)):
            if f.suffix.lower() in IMAGE_EXT:
                style.append({'name': f.name, 'url': file_url(f)})
    headshot = None
    refs = PROJECT / 'references'
    if refs.exists():
        for f in sorted(refs.iterdir()):
            if f.is_file() and f.suffix.lower() in IMAGE_EXT and 'headshot' in f.name.lower():
                headshot = {'name': f.name, 'url': file_url(f)}
                break
    notes = refs / 'README.md'
    return {'style': style, 'headshot': headshot, 'notes': rel(notes) if notes.exists() else None,
            'defaultSet': all(re.match(r'^\d+\.(jpg|jpeg|png|webp)$', s['name']) for s in style) and len(style) >= 5}


def _node_eval_account(js: Path):
    script = ("global.window={};const p=process.argv[1];require(p);"
              "console.log(JSON.stringify({profile:window.IG_PROFILE||null,posts:window.IG_POSTS||[]}))")
    rc, so, se = run(['node', '-e', script, str(js)], timeout=15)
    if rc != 0:
        return None
    try:
        return json.loads(so)
    except Exception:  # noqa: BLE001
        return None


def _regex_account(js: Path):
    text = js.read_text(errors='replace')

    def grab(key):
        m = re.search(rf"{key}\s*:\s*'((?:[^'\\]|\\.)*)'", text)
        return m.group(1).encode().decode('unicode_escape') if m else ''
    handle = re.search(r"var HANDLE\s*=\s*'([^']*)'", text)
    return {'profile': {'username': handle.group(1) if handle else grab('username'), 'bio': grab('bio'),
                        'note': grab('note'), 'category': grab('category'), 'avatar': grab('avatar'),
                        'followers': grab('followers'), 'following': grab('following'), 'posts': grab('posts')},
            'posts': [{'file': m, 'caption': ''} for m in re.findall(r"file:\s*'([^']+)'", text)]}


def packaging_info():
    js = PROJECT / 'instagram-preview' / 'my-account.js'
    preview = PROJECT / 'instagram-preview' / 'me.html'
    out = {'exists': js.exists(), 'previewUrl': file_url(preview) if preview.exists() else None}
    if not js.exists():
        return out
    data = _node_eval_account(js) or _regex_account(js)
    prof = data.get('profile') or {}
    posts = data.get('posts') or []
    avatar = prof.get('avatar') or ''
    avatar_path = PROJECT / 'instagram-preview' / avatar if avatar else None
    avatar_ok = bool(avatar_path and avatar_path.exists() and 'placeholder' not in avatar_path.name)
    username = (prof.get('username') or '').strip()
    placeholder = username.lower() in {'', 'yourhandle', 'your.handle', 'your_handle', 'handle'}
    free = []
    av = PROJECT / 'username-finder' / 'results' / 'available.md'
    if av.exists():
        for line in av.read_text(errors='replace').splitlines():
            s = re.split(r'\s+[\u2014\u2013-]\s+', line.strip().lstrip('-*@ ').strip(), 1)[0].strip()
            if s and re.match(r'^[a-z0-9._]{1,30}$', s):
                free.append(s)
    out.update({
        'username': username, 'placeholder': placeholder, 'bio': prof.get('bio') or '', 'note': prof.get('note') or '',
        'category': prof.get('category') or '', 'avatarUrl': file_url(avatar_path) if avatar_ok else None,
        'counts': {'posts': prof.get('posts'), 'followers': prof.get('followers'), 'following': prof.get('following')},
        'postCount': len(posts), 'freeHandles': free[:12], 'freeHandleCount': len(free),
        'posts': [{'file': p.get('file'), 'video': p.get('video'), 'caption': p.get('caption', ''),
                   'kind': p.get('kind'), 'pinned': bool(p.get('pinned'))} for p in posts],
    })
    alts = sorted((PROJECT / 'instagram-preview' / 'assets' / 'mine').glob('profile-alt-*.*')) if (PROJECT / 'instagram-preview' / 'assets' / 'mine').exists() else []
    out['avatarAlternates'] = [file_url(a) for a in alts if a.suffix.lower() in IMAGE_EXT]
    return out


def reels_info(posts):
    out = []
    reels = PROJECT / 'reels'
    if reels.exists():
        for d in sorted(reels.iterdir()):
            m = re.match(r'^(\d+)-(.+)$', d.name)
            if not d.is_dir() or not m:
                continue
            n = int(m.group(1))
            post = next((p for p in posts if p.get('file', '').endswith(f'reel-{n}.jpg')), None)
            cover = d / 'cover.jpg'
            mp4s = sorted(x.name for x in d.glob('*.mp4'))
            video_url = None
            if post and post.get('video') and (PROJECT / 'instagram-preview' / post['video']).exists():
                video_url = file_url(PROJECT / 'instagram-preview' / post['video'])
            elif mp4s:
                video_url = file_url(d / mp4s[0])
            out.append({'n': n, 'slug': m.group(2), 'folder': rel(d), 'cover': file_url(cover) if cover.exists() else None,
                        'videos': mp4s, 'videoUrl': video_url, 'caption': (post or {}).get('caption', ''),
                        'inPreview': post is not None, 'pinned': bool((post or {}).get('pinned'))})
    runs = []
    rd = PROJECT / 'full-pipeline' / 'runs'
    if rd.exists():
        for r in sorted(rd.iterdir(), reverse=True):
            if not r.is_dir() or r.name.startswith('example'):
                continue
            runs.append({
                'name': r.name, 'plan': (r / 'plan.md').exists(),
                'candidates': len([x for x in (r / 'candidates').glob('*') if x.suffix.lower() in IMAGE_EXT]) if (r / 'candidates').exists() else 0,
                'selected': len([x for x in (r / 'selected').glob('*') if x.suffix.lower() in IMAGE_EXT]) if (r / 'selected').exists() else 0,
                'clips': len(list((r / 'clips').glob('*.mp4'))) if (r / 'clips').exists() else 0,
                'music': len([x for x in (r / 'music').glob('*') if x.suffix in {'.m4a', '.mp3'}]) if (r / 'music').exists() else 0,
                'notes': (r / 'run.md').exists(),
                'contact': file_url(r / 'contact-candidates.jpg') if (r / 'contact-candidates.jpg').exists() else None,
            })
    return out, runs[:6]


def manual_marks():
    return read_json(state_dir() / 'state.json', {}).get('manual', {})


def compute_steps(concept, refs, pack, reels):
    marks = manual_marks()
    n_reels = len([r for r in reels if r['inPreview'] or r['videos']])
    pack_done = pack.get('exists') and not pack.get('placeholder') and pack.get('avatarUrl') and pack.get('bio')
    pack_parts = {'handle': bool(pack.get('exists') and not pack.get('placeholder')), 'picture': bool(pack.get('avatarUrl')),
                  'bio': bool(pack.get('bio'))}
    steps = [
        {'id': 'concept', 'n': 1, 'title': 'Choose the idea',
         'status': 'done' if concept['exists'] else 'empty',
         'detail': concept.get('title') if concept['exists'] else 'What the page is about, in one document Claude reads before everything else.'},
        {'id': 'references', 'n': 2, 'title': 'Pick the vibe', 'optional': True,
         'status': 'done' if refs['style'] else 'empty',
         'detail': (f"{len(refs['style'])} style references" + (' (the default set)' if refs.get('defaultSet') else ''))
         if refs['style'] else 'Drop a few stills that look how your page should look.'},
        {'id': 'packaging', 'n': 3, 'title': 'Packaging',
         'status': 'done' if pack_done else ('partial' if any(pack_parts.values()) else 'empty'),
         'parts': pack_parts,
         'detail': ('@' + pack['username']) if pack_done else 'Username, profile picture, bio.'},
        {'id': 'reels', 'n': 4, 'title': 'First 3 reels',
         'status': 'done' if n_reels >= 3 else ('partial' if n_reels else 'empty'),
         'count': n_reels, 'detail': f'{n_reels} of 3' if n_reels < 3 else f'{n_reels} reels made'},
        {'id': 'posting', 'n': 5, 'title': 'Start posting',
         'status': 'done' if marks.get('posting') else ('empty' if n_reels >= 3 else 'later'),
         'detail': 'Through the Edits app at first. Keep going; improve the prompts from what you see.'},
        {'id': 'autopilot', 'n': 6, 'title': 'Autopilot',
         'status': 'done' if marks.get('autopilot') else ('empty' if marks.get('posting') else 'later'),
         'detail': 'Blotato publishes on a schedule; Apify + Gemini read the numbers and tune the prompts.'},
        {'id': 'monetize', 'n': 7, 'title': 'Monetize',
         'status': 'done' if marks.get('monetize') else ('empty' if marks.get('autopilot') else 'later'),
         'detail': 'Referral links, a digital product, a service. Not before the audience is there.'},
    ]
    current = next((s['id'] for s in steps if s['status'] not in ('done', 'later')), steps[-1]['id'])
    return steps, current


def full_state():
    concept = concept_info()
    refs = references_info()
    pack = packaging_info()
    reels, runs = reels_info(pack.get('posts', []))
    steps, current = compute_steps(concept, refs, pack, reels)
    return {
        'project': {'path': str(PROJECT), 'name': PROJECT.name, 'isTemplate': PROJECT == STUDIO.parent},
        'tools': TOOLS.get(), 'env': env_status(), 'balance': BALANCE.get(),
        'mcp': SESSION.mcp_servers, 'concept': concept, 'references': refs, 'packaging': pack,
        'reels': reels, 'runs': runs, 'steps': steps, 'current': current,
        'chat': {'busy': SESSION.running, 'seq': SESSION.seq, 'sessionId': SESSION.session_id,
                 'id': SESSION.chat_id, 'title': SESSION.title},
        'chats': SESSION.list_chats(),
    }


def state_summary_for_agent():
    """A few lines the agent gets at the top of every turn so it never has to explore to know where things stand."""
    s = full_state()
    lines = [f"Project folder (your cwd): {PROJECT}"]
    for st in s['steps']:
        lines.append(f"Step {st['n']} {st['title']}: {st['status']} - {st['detail']}")
    lines.append(f"Current step: {s['current']}")
    b = s['balance']
    lines.append(f"Higgsfield balance: {b.get('credits')} credits ({b.get('plan')})" if b.get('ok') else f"Higgsfield balance: unknown ({b.get('error')})")
    e = s['env']
    lines.append(f".env keys: APIFY_API_KEY={'set' if e['APIFY_API_KEY'] else 'missing'}, GEMINI_API_KEY={'set' if e['GEMINI_API_KEY'] else 'missing'}")
    r = s['references']
    lines.append(f"Headshot: {r['headshot']['name'] if r['headshot'] else 'none yet (ask the person to drop one in the studio, or skip the profile picture)'}")
    p = s['packaging']
    if p.get('exists'):
        lines.append(f"Preview account: @{p.get('username')} ({'placeholder' if p.get('placeholder') else 'chosen'}), {p.get('postCount')} posts, "
                     f"{p.get('freeHandleCount', 0)} free handles already found")
    if s['runs']:
        r0 = s['runs'][0]
        lines.append(f"Latest pipeline run: {r0['name']} (plan {r0['plan']}, {r0['candidates']} candidates, {r0['selected']} picks, {r0['clips']} clips)")
    return '\n'.join(lines)


# ---------------------------------------------------------------------------------------------------
# The Claude Code session: one headless `claude -p` per turn, resumed by session id
# ---------------------------------------------------------------------------------------------------

class Session:
    MAX_EVENTS = 6000

    def __init__(self):
        self.events = []
        self.seq = 0
        self.proc = None
        self.session_id = None
        self.mcp_servers = []
        self.subscribers = set()
        self.lock = threading.Lock()
        self.blocks = {}
        self.message_ordinal = 0
        self.turn_started = None
        self.chat_id = None
        self.title = ''
        self.created = 0
        self.messages = 0
        self.load()

    # -- persistence: one folder per chat, .studio/chats/<id>/{session.json,history.jsonl} ---------
    @staticmethod
    def chats_root() -> Path:
        d = state_dir() / 'chats'
        d.mkdir(exist_ok=True)
        return d

    def chat_dir(self) -> Path:
        d = self.chats_root() / self.chat_id
        d.mkdir(exist_ok=True)
        return d

    def hist_path(self) -> Path:
        return self.chat_dir() / 'history.jsonl'

    @staticmethod
    def new_id() -> str:
        return time.strftime('%Y%m%d-%H%M%S') + '-' + os.urandom(2).hex()

    @staticmethod
    def valid_id(cid) -> bool:
        return isinstance(cid, str) and re.fullmatch(r'[\w-]{1,64}', cid) is not None

    def load(self):
        """Open the chat the studio was last on. Older studios kept one chat at the root of .studio/;
        that one becomes the first entry of the list."""
        legacy = [state_dir() / n for n in ('session.json', 'history.jsonl') if (state_dir() / n).exists()]
        if legacy:
            cid = self.new_id()
            d = self.chats_root() / cid
            d.mkdir(exist_ok=True)
            for p in legacy:
                p.rename(d / p.name)
            meta = read_json(d / 'session.json', {})
            meta.setdefault('title', '')
            meta.setdefault('created', int(d.stat().st_mtime * 1000))
            meta.setdefault('messages', 0)
            for line in (d / 'history.jsonl').read_text(errors='replace').splitlines() if (d / 'history.jsonl').exists() else []:
                try:
                    ev = json.loads(line)
                except Exception:  # noqa: BLE001
                    continue
                if ev.get('kind') == 'asked':
                    meta['messages'] += 1
                    meta['created'] = min(meta['created'], ev.get('at') or meta['created'])
                    if not meta['title']:
                        meta['title'] = self.make_title(ev.get('body') or '')
            write_json(d / 'session.json', meta)
            self.set_current(cid)
        cid = read_json(state_dir() / 'state.json', {}).get('chat')
        if not self.valid_id(cid) or not (self.chats_root() / cid / 'session.json').exists():
            chats = self.list_chats()
            cid = chats[0]['id'] if chats else None
        if cid:
            self.open_chat(cid)
        else:
            self.new_chat()

    @staticmethod
    def make_title(text: str) -> str:
        t = ' '.join(str(text).split())
        return t if len(t) <= 60 else t[:57].rstrip() + '…'

    def set_current(self, cid):
        st = read_json(state_dir() / 'state.json', {})
        st['chat'] = cid
        write_json(state_dir() / 'state.json', st)

    def list_chats(self):
        out = []
        for d in self.chats_root().iterdir():
            meta = read_json(d / 'session.json', None) if d.is_dir() else None
            if not isinstance(meta, dict):
                continue
            hist = d / 'history.jsonl'
            created = int(meta.get('created') or 0)
            out.append({'id': d.name, 'title': meta.get('title') or '', 'created': created,
                        'updated': int(hist.stat().st_mtime * 1000) if hist.exists() else created,
                        'messages': int(meta.get('messages') or 0)})
        out.sort(key=lambda c: c['updated'], reverse=True)
        return out

    def open_chat(self, cid) -> bool:
        if self.running or not self.valid_id(cid):
            return False
        self.chat_id = cid
        meta = read_json(self.chat_dir() / 'session.json', {})
        self.session_id = meta.get('session_id')
        self.mcp_servers = meta.get('mcp_servers', [])
        self.title = meta.get('title') or ''
        self.created = int(meta.get('created') or time.time() * 1000)
        self.messages = int(meta.get('messages') or 0)
        self.events, self.seq, self.blocks = [], 0, {}
        hist = self.hist_path()
        if hist.exists():
            for line in hist.read_text(errors='replace').splitlines():
                try:
                    ev = json.loads(line)
                except Exception:  # noqa: BLE001
                    continue
                self.events.append(ev)
            if self.events:
                self.seq = max(e['seq'] for e in self.events) + 1
        # A turn that was running when the server died is over now.
        if self.events and self.events[-1]['kind'] not in ('done', 'error', 'asked'):
            self.emit('done', 'stopped', 'The studio was restarted while this was running.')
        self.set_current(cid)
        self.save_meta()
        # Tell every open page which chat is on screen now (not recorded).
        self.broadcast({'seq': -1, 'at': int(time.time() * 1000), 'kind': 'chat', 'label': 'opened', 'body': None, 'chat': cid})
        return True

    def new_chat(self):
        """Start an empty chat (a fresh Claude Code session). An empty current chat is simply reused."""
        if self.running:
            return None
        if self.chat_id and self.messages == 0 and (self.chats_root() / self.chat_id / 'session.json').exists():
            return self.chat_id
        cid = self.new_id()
        (self.chats_root() / cid).mkdir(exist_ok=True)
        write_json(self.chats_root() / cid / 'session.json',
                   {'session_id': None, 'mcp_servers': self.mcp_servers, 'title': '', 'created': int(time.time() * 1000), 'messages': 0})
        self.open_chat(cid)
        return cid

    def delete_chat(self, cid) -> bool:
        if not self.valid_id(cid) or (cid == self.chat_id and self.running):
            return False
        shutil.rmtree(self.chats_root() / cid, ignore_errors=True)
        if cid == self.chat_id:
            chats = self.list_chats()
            self.chat_id = None
            if chats:
                self.open_chat(chats[0]['id'])
            else:
                self.new_chat()
        return True

    def save_meta(self):
        write_json(self.chat_dir() / 'session.json',
                   {'session_id': self.session_id, 'mcp_servers': self.mcp_servers, 'title': self.title,
                    'created': self.created, 'messages': self.messages})

    def reset(self):
        return self.new_chat()

    # -- events ------------------------------------------------------------------------------------
    @property
    def running(self):
        return self.proc is not None

    def subscribe(self):
        q = queue.Queue()
        with self.lock:
            self.subscribers.add(q)
        return q

    def unsubscribe(self, q):
        with self.lock:
            self.subscribers.discard(q)

    def emit(self, kind, label=None, body=None, **extra):
        ev = {'seq': self.seq, 'at': int(time.time() * 1000), 'kind': kind, 'label': label, 'body': body}
        ev.update(extra)
        self.seq += 1
        self.events.append(ev)
        if len(self.events) > self.MAX_EVENTS:
            self.events = self.events[-self.MAX_EVENTS:]
        self.broadcast(ev, record=True)
        return ev

    def broadcast(self, ev, record=False):
        if record:
            try:
                with open(self.hist_path(), 'a') as f:
                    f.write(json.dumps(ev, ensure_ascii=False) + '\n')
            except OSError:
                pass
        with self.lock:
            subs = list(self.subscribers)
        for q in subs:
            q.put(ev)

    def update(self, ev):
        """Re-broadcast an event whose body grew (streamed text). Not recorded until final."""
        self.broadcast(ev)

    def record(self, ev):
        """Write the final form of a grown event to history."""
        try:
            with open(self.hist_path(), 'a') as f:
                f.write(json.dumps(ev, ensure_ascii=False) + '\n')
        except OSError:
            pass

    # -- a turn ------------------------------------------------------------------------------------
    def start(self, prompt, shown=None, step=None):
        if self.running:
            return False
        self.blocks = {}
        self.turn_started = time.time()
        self.emit('asked', step, shown or prompt)
        self.messages += 1
        if not self.title:
            self.title = self.make_title(shown or prompt)
        self.save_meta()
        system = (STUDIO / 'system-prompt.md').read_text(errors='replace') if (STUDIO / 'system-prompt.md').exists() else ''
        system = system.replace('{{STUDIO_DIR}}', str(STUDIO)) + '\n\n## Where things stand right now\n' + state_summary_for_agent()
        args = ['claude', '-p', prompt, '--output-format', 'stream-json', '--verbose', '--include-partial-messages',
                '--forward-subagent-text', '--permission-mode', 'dontAsk', '--allowedTools', ALLOWED_TOOLS,
                '--append-system-prompt', system]
        if self.session_id:
            args += ['--resume', self.session_id]
        env = dict(os.environ, CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS='0')
        try:
            self.proc = subprocess.Popen(args, cwd=str(PROJECT), env=env, stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
        except FileNotFoundError:
            self.proc = None
            self.emit('error', 'spawn', 'Claude Code is not installed, or not on the PATH. Run `claude` in a terminal first.')
            self.emit('done', 'stopped', 'Nothing ran.')
            return True
        threading.Thread(target=self._pump, args=(self.proc,), daemon=True).start()
        threading.Thread(target=self._stderr, args=(self.proc,), daemon=True).start()
        return True

    def stop(self):
        p = self.proc
        if p:
            try:
                p.terminate()
            except OSError:
                pass

    def _stderr(self, proc):
        for line in proc.stderr:
            t = line.strip()
            if t and 'ExperimentalWarning' not in t:
                self.emit('stderr', None, t[:2000])

    def _pump(self, proc):
        for line in proc.stdout:
            t = line.strip()
            if not t:
                continue
            try:
                obj = json.loads(t)
            except Exception:  # noqa: BLE001
                self.emit('text', None, t[:4000])
                continue
            try:
                self.translate(obj)
            except Exception as e:  # noqa: BLE001
                self.emit('stderr', None, f'studio: could not read an event: {e}')
        code = proc.wait()
        self.proc = None
        # Flush any block still open (a turn killed mid-sentence).
        for key, slot in list(self.blocks.items()):
            if slot.get('event'):
                self.record(slot['event'])
        self.blocks = {}
        BALANCE.get(force=True)
        secs = int(time.time() - (self.turn_started or time.time()))
        if code == 0:
            self.emit('done', 'done', f'Finished in {secs // 60} min {secs % 60} s.' if secs >= 60 else f'Finished in {secs} s.')
        elif code in (-15, 143):
            self.emit('done', 'stopped', 'Stopped.')
        else:
            self.emit('done', 'stopped', f'Claude Code exited with code {code}.')

    # -- translate one stream-json line into studio events ---------------------------------------
    def translate(self, o):
        if not isinstance(o, dict):
            return
        sid = o.get('session_id')
        if isinstance(sid, str) and sid and sid != self.session_id:
            self.session_id = sid
            self.save_meta()
        t = o.get('type')
        if t == 'system':
            if o.get('subtype') == 'init':
                servers = o.get('mcp_servers') or []
                self.mcp_servers = [{'name': s.get('name'), 'status': s.get('status')} for s in servers if isinstance(s, dict)]
                self.save_meta()
                self.emit('init', None, None, mcp=self.mcp_servers, model=o.get('model'))
            elif o.get('subtype') == 'api_retry':
                self.emit('status', 'retry', f"Retrying (attempt {o.get('attempt', '?')} of {o.get('max_retries', '?')}).")
            return
        if t == 'stream_event':
            self.on_stream_event(o.get('event') or {}, o.get('parent_tool_use_id'))
            return
        if t == 'user':
            content = (o.get('message') or {}).get('content')
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'tool_result':
                        body = flatten_result(block.get('content'))
                        self.emit('tool_result', 'error' if block.get('is_error') else 'result', body,
                                  tool_use_id=block.get('tool_use_id'))
            return
        if t == 'result':
            if o.get('is_error'):
                self.emit('error', 'result', str(o.get('result') or o.get('subtype') or 'failed'))
            cost = o.get('total_cost_usd')
            if cost is not None:
                self.emit('status', 'cost', None, cost=cost, turns=o.get('num_turns'))
            return

    def on_stream_event(self, ev, parent):
        scope = f'sub:{parent}' if parent else 'main'
        et = ev.get('type')
        if et == 'message_start':
            self.message_ordinal += 1
            return
        key = f"{scope}:{self.message_ordinal}:{ev.get('index')}"
        if et == 'content_block_start':
            cb = ev.get('content_block') or {}
            kind = cb.get('type')
            if kind == 'text':
                self.blocks[key] = {'kind': 'text', 'event': None, 'json': '', 'sub': bool(parent)}
            elif kind == 'thinking':
                self.blocks[key] = {'kind': 'thinking', 'event': None, 'json': '', 'sub': bool(parent)}
            elif kind == 'tool_use':
                name = str(cb.get('name') or 'tool')
                e = self.emit('tool', name, '', tool_use_id=cb.get('id'), sub=bool(parent))
                self.blocks[key] = {'kind': 'tool', 'event': e, 'json': '', 'sub': bool(parent)}
            return
        slot = self.blocks.get(key)
        if not slot:
            return
        if et == 'content_block_delta':
            d = ev.get('delta') or {}
            chunk = None
            if d.get('type') == 'text_delta':
                chunk = d.get('text')
            elif d.get('type') == 'thinking_delta':
                chunk = d.get('thinking')
            if isinstance(chunk, str):
                if slot['event'] is None:
                    if not chunk.strip():
                        return
                    slot['event'] = self.emit_unrecorded(slot['kind'], None, chunk, sub=slot['sub'])
                else:
                    slot['event']['body'] = (slot['event']['body'] or '') + chunk
                    slot['last'] = slot.get('last', 0)
                    now = time.time()
                    if now - slot['last'] > 0.08:
                        slot['last'] = now
                        self.update(slot['event'])
            elif d.get('type') == 'input_json_delta' and isinstance(d.get('partial_json'), str):
                slot['json'] += d['partial_json']
            return
        if et == 'content_block_stop':
            self.blocks.pop(key, None)
            e = slot.get('event')
            if not e:
                return
            if e['kind'] == 'tool' and slot['json']:
                try:
                    parsed = json.loads(slot['json'])
                except Exception:  # noqa: BLE001
                    parsed = slot['json']
                e['body'] = summarize_tool_input(parsed)
                e['input'] = parsed if isinstance(parsed, dict) else None
                self.update(e)
                self.record(e)
            else:
                e['final'] = True
                self.update(e)
                self.record(e)

    def emit_unrecorded(self, kind, label, body, **extra):
        """A streamed block: broadcast now, write to history only when it stops growing."""
        ev = {'seq': self.seq, 'at': int(time.time() * 1000), 'kind': kind, 'label': label, 'body': body}
        ev.update(extra)
        self.seq += 1
        self.events.append(ev)
        self.broadcast(ev)
        return ev


def tidy(text: str) -> str:
    text = text.replace(str(PROJECT) + os.sep, '').replace(str(PROJECT), '.')
    home = str(Path.home())
    return text.replace(home, '~')


def summarize_tool_input(inp):
    if inp is None:
        return ''
    if isinstance(inp, str):
        return tidy(inp[:400])
    if not isinstance(inp, dict):
        return str(inp)[:400]
    for k in ('command', 'file_path', 'pattern', 'path', 'description', 'skill', 'prompt', 'query', 'url'):
        v = inp.get(k)
        if isinstance(v, str) and v.strip():
            return tidy(v[:400])
    if 'requests' in inp and isinstance(inp['requests'], list):
        return f"{len(inp['requests'])} requests"
    return tidy(json.dumps(inp, ensure_ascii=False)[:400])


def flatten_result(content):
    if isinstance(content, str):
        return tidy(content[:1500])
    if not isinstance(content, list):
        return ''
    parts = [str(b.get('text')) for b in content if isinstance(b, dict) and b.get('type') == 'text']
    return tidy('\n'.join(parts)[:1500])


SESSION = None  # created in main() once PROJECT is known


# ---------------------------------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    server_version = 'ViralPageStudio/1.0'
    protocol_version = 'HTTP/1.1'

    def log_message(self, fmt, *args):
        if '/api/events' in str(args[0]) or '/api/state' in str(args[0]) or '/files/' in str(args[0]):
            return
        sys.stderr.write('%s - %s\n' % (self.address_string(), fmt % args))

    # -- helpers ----------------------------------------------------------------------------------
    def send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        n = int(self.headers.get('Content-Length') or 0)
        return self.rfile.read(n) if n else b''

    def read_json_body(self):
        try:
            return json.loads(self.read_body() or b'{}')
        except Exception:  # noqa: BLE001
            return {}

    def send_file(self, path: Path, download=False):
        if not path.is_file():
            self.send_json({'error': 'not found'}, 404)
            return
        ctype = mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
        size = path.stat().st_size
        start, end = 0, size - 1
        rng = self.headers.get('Range')
        status = 200
        if rng and rng.startswith('bytes='):
            m = re.match(r'bytes=(\d*)-(\d*)', rng)
            if m:
                if m.group(1):
                    start = int(m.group(1))
                if m.group(2):
                    end = min(int(m.group(2)), size - 1)
                elif not m.group(1):
                    start = 0
                if start > end or start >= size:
                    self.send_response(416)
                    self.send_header('Content-Range', f'bytes */{size}')
                    self.send_header('Content-Length', '0')
                    self.end_headers()
                    return
                status = 206
        self.send_response(status)
        self.send_header('Content-Type', ctype)
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(end - start + 1))
        if status == 206:
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        if path.suffix in ('.html', '.js', '.css', '.json', '.md'):
            self.send_header('Cache-Control', 'no-store')
        else:
            self.send_header('Cache-Control', 'no-cache')
        if download:
            self.send_header('Content-Disposition', f'attachment; filename="{path.name}"')
        self.end_headers()
        if self.command == 'HEAD':
            return
        with open(path, 'rb') as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(1 << 16, left))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                left -= len(chunk)

    def safe_project_path(self, rel_path: str):
        p = (PROJECT / urllib.parse.unquote(rel_path)).resolve()
        if PROJECT not in p.parents and p != PROJECT:
            return None
        if any(part.startswith('.') for part in p.relative_to(PROJECT).parts):
            return None  # no .env, no .git, no .studio
        return p

    # -- routes -----------------------------------------------------------------------------------
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        path = u.path
        if path in ('/', '/index.html'):
            return self.send_file(STUDIO / 'index.html')
        if path.startswith('/studio/'):
            p = (STUDIO / path[len('/studio/'):]).resolve()
            if STUDIO in p.parents:
                return self.send_file(p)
            return self.send_json({'error': 'not found'}, 404)
        if path.startswith('/files/'):
            p = self.safe_project_path(path[len('/files/'):])
            if p is None:
                return self.send_json({'error': 'forbidden'}, 403)
            return self.send_file(p)
        if path == '/api/state':
            return self.send_json(full_state())
        if path == '/api/balance':
            return self.send_json(BALANCE.get(force='refresh' in q))
        if path == '/api/tools':
            return self.send_json(TOOLS.get(force='refresh' in q))
        if path == '/api/steps':
            return self.send_json(json.loads((STUDIO / 'steps.json').read_text()))
        if path == '/api/history':
            since = int(q.get('since', ['-1'])[0])
            return self.send_json({'events': [e for e in SESSION.events if e['seq'] > since], 'busy': SESSION.running,
                                   'sessionId': SESSION.session_id, 'chat': SESSION.chat_id})
        if path == '/api/chats':
            return self.send_json({'chats': SESSION.list_chats(), 'current': SESSION.chat_id})
        if path == '/api/file':
            p = self.safe_project_path(q.get('path', [''])[0])
            if p is None or not p.is_file() or p.suffix not in ('.md', '.txt', '.json', '.js'):
                return self.send_json({'error': 'not found'}, 404)
            return self.send_json({'path': rel(p), 'text': p.read_text(errors='replace')[:200000]})
        if path == '/api/events':
            return self.sse(int(q.get('since', ['-1'])[0]))
        self.send_json({'error': 'not found'}, 404)

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        path = u.path
        if path == '/api/chat':
            body = self.read_json_body()
            msg = (body.get('message') or '').strip()
            if not msg:
                return self.send_json({'error': 'message is required'}, 400)
            if SESSION.running:
                return self.send_json({'error': 'Claude is still working on the last message.'}, 409)
            shown = (body.get('shown') or msg).strip()
            SESSION.start(msg, shown=shown, step=body.get('step'))
            return self.send_json({'ok': True})
        if path == '/api/stop':
            SESSION.stop()
            return self.send_json({'ok': True})
        if path in ('/api/reset', '/api/chats/new'):
            if SESSION.running:
                return self.send_json({'error': 'Claude is still working. Stop it first.'}, 409)
            return self.send_json({'ok': True, 'id': SESSION.new_chat()})
        if path == '/api/chats/open':
            cid = self.read_json_body().get('id')
            if not SESSION.valid_id(cid) or not (SESSION.chats_root() / cid / 'session.json').exists():
                return self.send_json({'error': 'no such chat'}, 404)
            if cid == SESSION.chat_id:
                return self.send_json({'ok': True, 'id': cid})
            if SESSION.running:
                return self.send_json({'error': 'Claude is still working. Stop it first.'}, 409)
            SESSION.open_chat(cid)
            return self.send_json({'ok': True, 'id': cid})
        if path == '/api/mark':
            body = self.read_json_body()
            st = read_json(state_dir() / 'state.json', {})
            st.setdefault('manual', {})[str(body.get('step'))] = bool(body.get('done'))
            write_json(state_dir() / 'state.json', st)
            return self.send_json({'ok': True})
        if path == '/api/env':
            body = self.read_json_body()
            set_env({k: str(v) for k, v in body.items() if isinstance(v, str)})
            return self.send_json(env_status())
        if path == '/api/upload':
            return self.upload(q)
        if path == '/api/open':
            body = self.read_json_body()
            p = self.safe_project_path(body.get('path') or '')
            if p is None or not p.exists():
                return self.send_json({'error': 'not found'}, 404)
            opener = 'open' if sys.platform == 'darwin' else ('xdg-open' if sys.platform.startswith('linux') else 'explorer')
            subprocess.Popen([opener, str(p)])
            return self.send_json({'ok': True})
        self.send_json({'error': 'not found'}, 404)

    def upload(self, q):
        kind = q.get('kind', [''])[0]
        name = Path(q.get('name', ['upload'])[0]).name
        ext = Path(name).suffix.lower() or '.jpg'
        if ext not in IMAGE_EXT:
            return self.send_json({'error': 'images only (jpg, png, webp)'}, 400)
        data = self.read_body()
        if not data or len(data) > 60 * 1024 * 1024:
            return self.send_json({'error': 'empty or too large'}, 400)
        if kind == 'headshot':
            refs = PROJECT / 'references'
            refs.mkdir(exist_ok=True)
            for old in refs.glob('headshot.*'):
                old.unlink()
            target = refs / f'headshot{ext}'
        elif kind == 'style':
            d = PROJECT / 'references' / 'visual-style'
            d.mkdir(parents=True, exist_ok=True)
            nums = [int(p.stem) for p in d.iterdir() if p.stem.isdigit()]
            target = d / f'{(max(nums) + 1) if nums else 1}{ext}'
        else:
            return self.send_json({'error': 'kind must be headshot or style'}, 400)
        target.write_bytes(data)
        return self.send_json({'ok': True, 'path': rel(target), 'url': file_url(target)})

    def do_DELETE(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == '/api/reference':
            p = self.safe_project_path(q.get('path', [''])[0])
            if p is None or not p.is_file() or 'references' not in p.parts:
                return self.send_json({'error': 'not found'}, 404)
            p.unlink()
            return self.send_json({'ok': True})
        if u.path == '/api/chats':
            cid = q.get('id', [''])[0]
            if not SESSION.valid_id(cid) or not (SESSION.chats_root() / cid).is_dir():
                return self.send_json({'error': 'no such chat'}, 404)
            if cid == SESSION.chat_id and SESSION.running:
                return self.send_json({'error': 'Claude is still working in this chat. Stop it first.'}, 409)
            SESSION.delete_chat(cid)
            return self.send_json({'ok': True, 'current': SESSION.chat_id})
        self.send_json({'error': 'not found'}, 404)

    def sse(self, since):
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()
        q = SESSION.subscribe()
        try:
            for ev in [e for e in SESSION.events if e['seq'] > since]:
                self.wfile.write(f'data: {json.dumps(ev, ensure_ascii=False)}\n\n'.encode())
            self.wfile.write(f'event: hello\ndata: {json.dumps({"busy": SESSION.running, "chat": SESSION.chat_id})}\n\n'.encode())
            self.wfile.flush()
            while True:
                try:
                    ev = q.get(timeout=15)
                    self.wfile.write(f'data: {json.dumps(ev, ensure_ascii=False)}\n\n'.encode())
                except queue.Empty:
                    self.wfile.write(b': ping\n\n')
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            SESSION.unsubscribe(q)


def main():
    global PROJECT, SESSION
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--project', default=str(STUDIO.parent), help='project folder (default: the folder above studio/)')
    ap.add_argument('--port', type=int, default=int(os.environ.get('PORT', 8788)))
    ap.add_argument('--no-open', action='store_true', help='do not open the browser')
    a = ap.parse_args()
    PROJECT = Path(a.project).resolve()
    if not PROJECT.is_dir():
        sys.exit(f'No such folder: {PROJECT}')
    SESSION = Session()
    gi = PROJECT / '.gitignore'
    if gi.exists() and STATE_DIR_NAME + '/' not in gi.read_text():
        with open(gi, 'a') as f:
            f.write(f'\n# studio: chats (session ids, history), step marks\n{STATE_DIR_NAME}/\n')
    url = f'http://localhost:{a.port}'
    try:
        httpd = ThreadingHTTPServer(('127.0.0.1', a.port), Handler)
    except OSError as e:
        sys.exit(f'Port {a.port} is busy ({e}). Is the studio already running? Open {url}')
    httpd.daemon_threads = True
    print(f'Viral Page Studio on {url}  (project: {PROJECT})  Ctrl+C to stop', flush=True)
    if not a.no_open:
        threading.Thread(target=lambda: (time.sleep(0.6), open_browser(url)), daemon=True).start()
    threading.Thread(target=TOOLS.get, daemon=True).start()
    threading.Thread(target=BALANCE.get, daemon=True).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nbye')


def open_browser(url):
    try:
        if sys.platform == 'darwin':
            subprocess.Popen(['open', url])
        elif sys.platform.startswith('win'):
            os.startfile(url)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(['xdg-open', url])
    except Exception:  # noqa: BLE001
        pass


if __name__ == '__main__':
    main()
