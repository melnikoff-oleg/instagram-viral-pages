#!/usr/bin/env python3
"""Builds index.html + me.html (icon sprite inlined into template.html) and data.js from assets/ captured from instagram.com/iamnotsrc.
my-account.js (our draft, shown on me.html) is hand-edited and never regenerated."""
import json, re, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, 'assets')

svgs = json.load(open(os.path.join(A, 'svgs.json')))
# The starter ships without the captured @iamnotsrc feed; then only me.html is built.
pp = os.path.join(A, 'posts.json')
posts = json.load(open(pp)) if os.path.exists(pp) else None

ID = {
    'Instagram': 'logo', 'Home': 'home', 'Reels': 'reels', 'Messages': 'messages', 'Search': 'search',
    'Notifications': 'heart', 'New post': 'plus', 'Professional dashboard': 'dash', 'Settings': 'menu',
    'Also from Meta': 'meta', 'Verified': 'verified', 'Options': 'options', 'Link icon': 'link',
    'Threads': 'threads', 'Similar accounts': 'similar', 'Posts': 'tab-posts', 'noLabel_16': 'tab-reposts',
    'Tagged': 'tab-tagged', 'Pinned post icon': 'pin', 'Clip': 'clip', 'Carousel': 'carousel',
    'Down chevron icon': 'chevron-down',
}

def to_symbol(name, svg):
    vb = re.search(r'viewBox="([^"]+)"', svg).group(1)
    fill = re.search(r'<svg[^>]*\sfill="([^"]+)"', svg)
    fill = fill.group(1) if fill else 'currentColor'
    inner = re.sub(r'^<svg[^>]*>', '', svg.strip())
    inner = re.sub(r'</svg>$', '', inner)
    inner = re.sub(r'<title>.*?</title>', '', inner)
    inner = re.sub(r'\sclass="[^"]*"', '', inner)
    inner = re.sub(r'\sstyle="[^"]*"', '', inner)
    return f'<symbol id="ic-{name}" viewBox="{vb}" fill="{fill}">{inner}</symbol>'

symbols = [to_symbol(ID[k], v) for k, v in svgs.items() if k in ID]

# Extra icons (post dialog) – drawn to match Instagram's glyphs
extra = {
 'like': '<symbol id="ic-like" viewBox="0 0 24 24" fill="currentColor"><path d="M16.792 3.904A4.989 4.989 0 0 1 21.5 9.122c0 3.072-2.652 4.959-5.197 7.222-2.512 2.243-3.865 3.469-4.303 3.752-.477-.309-2.143-1.823-4.303-3.752C5.141 14.072 2.5 12.167 2.5 9.122a4.989 4.989 0 0 1 4.708-5.218 4.21 4.21 0 0 1 3.675 1.941c.84 1.175.98 1.763 1.12 1.763s.278-.588 1.11-1.766a4.17 4.17 0 0 1 3.679-1.938m0-2a6.04 6.04 0 0 0-4.797 2.127 6.052 6.052 0 0 0-4.787-2.127A6.985 6.985 0 0 0 .5 9.122c0 3.61 2.55 5.827 5.015 7.97.283.246.569.494.853.747l1.027.918a44.998 44.998 0 0 0 3.518 3.018 2 2 0 0 0 2.174 0 45.263 45.263 0 0 0 3.626-3.115l.922-.824c.293-.26.59-.519.885-.774 2.334-2.025 4.98-4.32 4.98-7.94a6.985 6.985 0 0 0-6.708-7.218Z"/></symbol>',
 'like-filled': '<symbol id="ic-like-filled" viewBox="0 0 48 48" fill="currentColor"><path d="M34.6 3.1c-4.5 0-7.9 1.8-10.6 5.6-2.7-3.7-6.1-5.5-10.6-5.5C6 3.1 0 9.6 0 17.6c0 7.3 5.4 12 10.6 16.5.6.5 1.3 1.1 1.9 1.7l2.3 2c4.4 3.9 6.6 5.9 7.6 6.5.5.3 1.1.5 1.6.5s1.1-.2 1.6-.5c1-.6 2.8-2.2 7.8-6.8l2-1.8c.7-.6 1.3-1.2 2-1.7C42.7 29.6 48 25 48 17.6c0-8-6-14.5-13.4-14.5z"/></symbol>',
 'comment': '<symbol id="ic-comment" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M20.656 17.008a9.993 9.993 0 1 0-3.59 3.615L22 22Z"/></symbol>',
 'share': '<symbol id="ic-share" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><line x1="22" x2="9.218" y1="3" y2="10.083"/><polygon points="11.698 20.334 22 3.001 2 3.001 9.218 10.084 11.698 20.334"/></symbol>',
 'save': '<symbol id="ic-save" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><polygon points="20 21 12 13.44 4 21 4 3 20 3 20 21"/></symbol>',
 'emoji': '<symbol id="ic-emoji" viewBox="0 0 24 24" fill="currentColor"><path d="M15.83 10.997a1.167 1.167 0 1 0 1.167 1.167 1.167 1.167 0 0 0-1.167-1.167Zm-6.5 1.167a1.167 1.167 0 1 0-1.166 1.167 1.167 1.167 0 0 0 1.166-1.167Zm5.163 3.24a3.406 3.406 0 0 1-4.982 0 1 1 0 1 0-1.46 1.368 5.4 5.4 0 0 0 7.902 0 1 1 0 0 0-1.46-1.368ZM12 .503a11.5 11.5 0 1 0 11.5 11.5A11.513 11.513 0 0 0 12 .503Zm0 21a9.5 9.5 0 1 1 9.5-9.5 9.51 9.51 0 0 1-9.5 9.5Z"/></symbol>',
 'close': '<symbol id="ic-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="20.643 3.357 12 12 3.353 20.647"/><line x1="20.649" x2="3.354" y1="20.649" y2="3.354"/></symbol>',
 'chevron-left': '<symbol id="ic-chevron-left" viewBox="0 0 24 24" fill="currentColor"><path d="M16.707 20.293 8.414 12l8.293-8.293a1 1 0 1 0-1.414-1.414l-9 9a1 1 0 0 0 0 1.414l9 9a1 1 0 0 0 1.414-1.414Z"/></symbol>',
 'chevron-right': '<symbol id="ic-chevron-right" viewBox="0 0 24 24" fill="currentColor"><path d="M7.293 3.707 15.586 12l-8.293 8.293a1 1 0 1 0 1.414 1.414l9-9a1 1 0 0 0 0-1.414l-9-9a1 1 0 0 0-1.414 1.414Z"/></symbol>',
 'audio-off': '<symbol id="ic-audio-off" viewBox="0 0 48 48" fill="currentColor"><path d="M1.5 13.3c-.8 0-1.5.7-1.5 1.5v18.4c0 .8.7 1.5 1.5 1.5h8.7l12.9 12.9c.9.9 2.5.3 2.5-1v-9.8c0-.4-.2-.8-.4-1.1l-22-22c-.3-.3-.7-.4-1.1-.4h-.6zm46.8 31.4-5.5-5.5C44.9 36.6 48 31.4 48 24c0-11.4-7.2-17.4-7.2-17.4-.6-.6-1.6-.6-2.2 0L37.2 8c-.6.6-.6 1.6 0 2.2 0 0 5.7 5 5.7 13.8 0 5.4-2.1 9.3-3.8 11.6L35.5 32c1.1-1.7 2.3-4.4 2.3-8 0-6.8-4.1-10.3-4.1-10.3-.6-.6-1.6-.6-2.2 0l-1.4 1.4c-.6.6-.6 1.6 0 2.2 0 0 2.6 2 2.6 6.7 0 1.8-.4 3.2-.9 4.3L25.6 22V1.4c0-1.3-1.6-1.9-2.5-1L13.5 10 3.3-.2c-.6-.6-1.6-.6-2.2 0L-.2 1.1c-.6.6-.6 1.6 0 2.2L45 48.3c.6.6 1.6.6 2.2 0l1.1-1.1c.6-.6.6-1.7 0-2.5z"/></symbol>',
 'audio-on': '<symbol id="ic-audio-on" viewBox="0 0 24 24" fill="currentColor"><path d="M16.636 7.028a1.5 1.5 0 1 0-2.395 1.807 5.365 5.365 0 0 1 1.103 3.17 5.378 5.378 0 0 1-1.105 3.176 1.5 1.5 0 1 0 2.395 1.806 8.396 8.396 0 0 0 1.71-4.981 8.39 8.39 0 0 0-1.708-4.978Zm3.73-2.332A1.5 1.5 0 1 0 18.04 6.59 8.823 8.823 0 0 1 20 12.007a8.798 8.798 0 0 1-1.96 5.415 1.5 1.5 0 0 0 2.326 1.894 11.672 11.672 0 0 0 2.635-7.31 11.682 11.682 0 0 0-2.635-7.31Zm-8.963-3.613a1.001 1.001 0 0 0-1.082.187L5.265 6H2a1 1 0 0 0-1 1v10.003a1 1 0 0 0 1 1h3.265l5.01 4.682.02.021a1 1 0 0 0 1.704-.814L12.005 2a1 1 0 0 0-.602-.917Z"/></symbol>',
 'play': '<symbol id="ic-play" viewBox="0 0 24 24" fill="currentColor"><path d="M5.888 22.5a3.46 3.46 0 0 1-1.721-.46l-.003-.002a3.451 3.451 0 0 1-1.72-2.982V4.943a3.445 3.445 0 0 1 5.163-2.987l12.226 7.059a3.444 3.444 0 0 1-.001 5.967l-12.22 7.056a3.462 3.462 0 0 1-1.724.462Z"/></symbol>',
}
symbols += extra.values()
sprite = '<svg xmlns="http://www.w3.org/2000/svg" style="display:none">' + ''.join(symbols) + '</svg>'

# ---- data.js --------------------------------------------------------------
profile = {
    'username': 'iamnotsrc',
    'verified': True,
    'note': 'iamnotsrc is typing...',
    'posts': '169', 'followers': '190K', 'following': '773',
    'category': 'Digital creator',
    'bio': 'designer, creative director and ai explorer',
    'link': {'text': 'iamnotsrc.com', 'href': 'https://iamnotsrc.com'},
    'threads': 'iamnotsrc',
    'avatar': 'assets/profile.jpg',
    'storyRing': True,
    'viewerAvatar': 'assets/viewer-avatar.jpg',
}
reels = {}
rp = os.path.join(A, 'reels.json')
if os.path.exists(rp):
    for r in json.load(open(rp)):
        reels[r['code']] = r

items = []
for p in (posts or []):
    cap = p['alt'] or ''
    item = {'file': 'assets/' + p['file'], 'href': p['href'], 'kind': p['kind'], 'pinned': p['pinned'], 'caption': cap, 'label': 'AI content'}
    code = p['href'].rstrip('/').split('/')[-1]
    if p['kind'] == 'reel' and code in reels:
        r = reels[code]
        item.update({'video': f'assets/reels/{code}.mp4', 'audio': ' \u2022 '.join(reversed(r['audio'].split(' \u00b7 ', 1))),  # 'Artist • Title' like Instagram's header
                     'likes': r['likes'], 'comments': r['comments'], 'reposts': r['reposts'],
                     'taken_at': r['taken_at'], 'caption': r['caption'] or cap})
    items.append(item)

data_js = (
    '// Edit this file to preview your own draft account.\n'
    '// kind: "image" | "carousel" | "reel"   pinned: true shows the pin icon.\n'
    '// Reels: "video" (mp4 in assets/reels/) plays in the dialog with sound; "audio" is the "Artist \u2022 Title" line,\n'
    '// "label" the small line under the username (e.g. "AI content"), "taken_at" a unix timestamp for the "x hours ago" text.\n'
    '// Drop your own images into assets/posts/ and point "file" at them.\n'
    'window.IG_PROFILE = ' + json.dumps(profile, indent=2, ensure_ascii=False) + ';\n\n'
    'window.IG_POSTS = ' + json.dumps(items, indent=2, ensure_ascii=False) + ';\n'
)
if posts is not None:
    open(os.path.join(ROOT, 'data.js'), 'w').write(data_js)

tpl = open(os.path.join(ROOT, 'template.html')).read().replace('<!--SPRITE-->', sprite)
if posts is None:  # no iamnotsrc capture: no index.html to switch to
    tpl = re.sub(r'<span class="preview-switch">.*?</span>', '', tpl)
assert '<script src="data.js"></script>' in tpl
# index.html = the iamnotsrc capture (data.js); me.html = our own draft account (my-account.js, hand-edited)
if posts is not None:
    open(os.path.join(ROOT, 'index.html'), 'w').write(tpl)
open(os.path.join(ROOT, 'me.html'), 'w').write(tpl.replace('<script src="data.js"></script>', '<script src="my-account.js"></script>'))
print(('built index.html + me.html + data.js; posts: %d' % len(items)) if posts is not None else 'built me.html', '; symbols:', len(symbols))
