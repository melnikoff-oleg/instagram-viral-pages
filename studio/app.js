/* Viral Page Studio, browser side. Vanilla JS, no build step.
   Talks to serve.py: /api/state (what exists), /api/events (the Claude Code stream), /api/chat (send). */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const S = {
    stepsDef: [], state: null,
    events: new Map(), nodes: new Map(), toolNodes: new Map(),
    lastSeq: -1, busy: false, selected: null, es: null, tick: null, chipMinutes: {},
    chat: null, confirmDelete: null,
  };

  // ---------------------------------------------------------------------------------------------
  // tiny markdown
  // ---------------------------------------------------------------------------------------------
  function inline(s) {
    s = esc(s);
    s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
    s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>');
    s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+|\/files\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    s = s.replace(/(^|\s)(https?:\/\/[^\s<]+)/g, '$1<a href="$2" target="_blank" rel="noopener">$2</a>');
    return s;
  }
  function md(text) {
    const lines = String(text ?? '').replace(/\r/g, '').split('\n');
    let out = '', i = 0;
    const para = [];
    const flush = () => { if (para.length) { out += `<p>${inline(para.join(' '))}</p>`; para.length = 0; } };
    while (i < lines.length) {
      const l = lines[i];
      if (/^```/.test(l)) {
        flush(); const buf = []; i++;
        while (i < lines.length && !/^```/.test(lines[i])) buf.push(lines[i++]);
        i++; out += `<pre><code>${esc(buf.join('\n'))}</code></pre>`; continue;
      }
      const h = /^(#{1,6})\s+(.*)$/.exec(l);
      if (h) { flush(); const n = Math.min(h[1].length, 3); out += `<h${n}>${inline(h[2])}</h${n}>`; i++; continue; }
      if (/^\s*([-*_]){3,}\s*$/.test(l)) { flush(); out += '<hr>'; i++; continue; }
      if (/^\s*\|.*\|\s*$/.test(l) && i + 1 < lines.length && /^\s*\|[\s:|-]+\|\s*$/.test(lines[i + 1])) {
        flush();
        const cells = (r) => r.trim().replace(/^\||\|$/g, '').split('|').map((c) => inline(c.trim()));
        let t = `<table><thead><tr>${cells(l).map((c) => `<th>${c}</th>`).join('')}</tr></thead><tbody>`;
        i += 2;
        while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) { t += `<tr>${cells(lines[i]).map((c) => `<td>${c}</td>`).join('')}</tr>`; i++; }
        out += t + '</tbody></table>'; continue;
      }
      const ul = /^\s*[-*+]\s+(.*)$/.exec(l), ol = /^\s*\d+[.)]\s+(.*)$/.exec(l);
      if (ul || ol) {
        flush();
        const tag = ul ? 'ul' : 'ol', re = ul ? /^\s*[-*+]\s+(.*)$/ : /^\s*\d+[.)]\s+(.*)$/;
        out += `<${tag}>`;
        while (i < lines.length) {
          const m = re.exec(lines[i]);
          if (!m) {
            if (/^\s{2,}\S/.test(lines[i]) && out.endsWith('</li>')) { out = out.slice(0, -5) + ' ' + inline(lines[i].trim()) + '</li>'; i++; continue; }
            break;
          }
          out += `<li>${inline(m[1])}</li>`; i++;
        }
        out += `</${tag}>`; continue;
      }
      if (!l.trim()) { flush(); i++; continue; }
      para.push(l.trim()); i++;
    }
    flush();
    return out;
  }

  // ---------------------------------------------------------------------------------------------
  // api + state
  // ---------------------------------------------------------------------------------------------
  async function api(path, opts) {
    const r = await fetch(path, opts);
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(j.error || r.statusText);
    return j;
  }
  const post = (path, body) => api(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) });

  let stateTimer = null, stateInFlight = false;
  async function refreshState() {
    if (stateInFlight) return;
    stateInFlight = true;
    try {
      S.state = await api('/api/state');
      if (!S.selected || !S.stepsDef.find((s) => s.id === S.selected)) S.selected = S.state.current;
      if (S.chat && S.state.chat.id && S.state.chat.id !== S.chat) { S.chat = S.state.chat.id; loadChat(); }
      S.chat = S.state.chat.id;
      renderHeader(); renderRail(); renderChips(); renderCards();
    } catch (e) { /* the server is away; the next poll will say */ }
    finally { stateInFlight = false; }
  }
  function scheduleState() { clearTimeout(stateTimer); stateTimer = setTimeout(refreshState, S.busy ? 2500 : 20000); }
  function stateSoon(ms = 600) { clearTimeout(stateTimer); stateTimer = setTimeout(refreshState, ms); }

  // ---------------------------------------------------------------------------------------------
  // header
  // ---------------------------------------------------------------------------------------------
  function renderHeader() {
    const st = S.state;
    $('projectName').textContent = st.project.name;
    const b = st.balance || {}, pill = $('balancePill');
    if (b.ok) {
      const c = Math.round(b.credits);
      pill.className = 'pill ' + (c < 100 ? 'bad' : c < 300 ? 'warn' : 'ok');
      pill.innerHTML = `<b>${c.toLocaleString()}</b> credits`;
      pill.title = `Higgsfield ${esc(b.plan || '')} · ${esc(b.email || '')}. Click to refresh.`;
    } else {
      pill.className = 'pill bad'; pill.textContent = 'Higgsfield: ' + (b.error || 'unknown');
      pill.title = 'Install the Higgsfield CLI and sign in (higgsfield auth login) to see the balance. Click to retry.';
    }
    const mcp = (st.mcp || []).find((m) => /higgsfield/i.test(m.name || ''));
    const mcpBad = st.mcp && st.mcp.length && !(mcp && ['connected', 'pending'].includes(mcp.status));
    const kb = $('keysBtn');
    kb.className = 'pill ' + (st.env.APIFY_API_KEY && !mcpBad ? 'ok' : 'warn');
    kb.textContent = 'Keys';
  }
  $('balancePill').onclick = async () => { $('balancePill').textContent = '…'; await api('/api/balance?refresh=1'); refreshState(); };
  $('keysBtn').onclick = () => openKeys();

  // ---------------------------------------------------------------------------------------------
  // steps rail
  // ---------------------------------------------------------------------------------------------
  function stepDef(id) { return S.stepsDef.find((s) => s.id === id) || {}; }
  function renderRail() {
    const rail = $('rail'), st = S.state;
    let h = '<div class="steps"><div class="eyebrow">Seven steps</div>';
    for (const s of st.steps) {
      const cls = ['step', 'st-' + s.status, s.id === st.current ? 'current' : '', s.id === S.selected ? 'selected' : ''].join(' ');
      let sub = '';
      if (s.id === 'packaging' && s.status === 'done') sub = s.detail;
      if (s.id === 'reels' && s.count) sub = s.count >= 3 ? `${s.count} made` : `${s.count} of 3`;
      h += `<div class="${cls}" data-step="${s.id}" title="${esc(stepDef(s.id).what || '')}">
        <div class="dot">${s.status === 'done' ? '✓' : ''}</div>
        <div><div class="title"><span class="n">${s.n}</span>${esc(s.title)}</div>${sub ? `<div class="sub">${esc(sub)}</div>` : ''}</div></div>`;
      if (['posting', 'autopilot', 'monetize'].includes(s.id) && s.status !== 'later' && s.id === S.selected) {
        h += `<button class="mark" data-mark="${s.id}" data-done="${s.status === 'done' ? 0 : 1}">${s.status === 'done' ? 'undo' : 'mark done'}</button>`;
      }
    }
    h += '</div>' + chatsHtml();
    rail.innerHTML = h;
    rail.querySelectorAll('.step').forEach((el) => el.addEventListener('click', () => { S.selected = el.dataset.step; renderRail(); renderChips(); renderCards(); }));
    rail.querySelectorAll('.mark').forEach((b) => b.addEventListener('click', async (e) => {
      e.stopPropagation(); await post('/api/mark', { step: b.dataset.mark, done: b.dataset.done === '1' }); refreshState();
    }));
    bindChats(rail);
  }

  // ---------------------------------------------------------------------------------------------
  // chats: one Claude Code session each, listed newest first, like any chat app
  // ---------------------------------------------------------------------------------------------
  function when(ms) {
    if (!ms) return '';
    const d = new Date(ms), now = new Date();
    const day = (x) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime();
    const diff = Math.round((day(now) - day(d)) / 86400000);
    if (diff === 0) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    if (diff === 1) return 'yesterday';
    return d.toLocaleDateString([], { day: 'numeric', month: 'short' });
  }
  function chatsHtml() {
    const chats = (S.state && S.state.chats) || [];
    const busyTip = S.busy ? 'Stop Claude first' : '';
    let h = `<div class="chats"><div class="chats-head"><span class="eyebrow">Chats</span>
      <button class="newchat" data-newchat ${S.busy ? 'disabled' : ''} title="${esc(busyTip || 'A fresh chat; the files and steps stay')}">+ new</button></div><div class="chatlist">`;
    for (const c of chats) {
      const cur = c.id === S.chat;
      if (S.confirmDelete === c.id) {
        h += `<div class="chatrow confirm"><span>Delete this chat?</span><button class="yes" data-delyes="${c.id}">Delete</button><button data-delno>Keep</button></div>`;
        continue;
      }
      h += `<div class="chatrow ${cur ? 'current' : ''}" data-chat="${c.id}" title="${esc(c.title || 'New chat')}">
        <div class="ctitle">${esc(c.title || 'New chat')}</div>
        <div class="cwhen">${esc(when(c.updated))}</div>
        <button class="cdel" data-del="${c.id}" title="Delete this chat" aria-label="Delete this chat">×</button></div>`;
    }
    if (!chats.length) h += '<div class="chatrow empty">No chats yet</div>';
    return h + '</div></div>';
  }
  function bindChats(rail) {
    const hint = (msg) => { const i = $('input'); const old = i.placeholder; i.placeholder = msg; setTimeout(() => { i.placeholder = old; }, 2500); };
    rail.querySelectorAll('[data-newchat]').forEach((b) => b.addEventListener('click', async () => {
      if (S.busy) return hint('Stop Claude first');
      try { const r = await post('/api/chats/new'); if (r.id !== S.chat) { S.chat = r.id; loadChat(); } else $('input').focus(); }
      catch (e) { hint(e.message); }
    }));
    rail.querySelectorAll('.chatrow[data-chat]').forEach((el) => el.addEventListener('click', async () => {
      const id = el.dataset.chat;
      if (id === S.chat) return;
      if (S.busy) return hint('Stop Claude first');
      try { await post('/api/chats/open', { id }); S.chat = id; loadChat(); }
      catch (e) { hint(e.message); }
    }));
    rail.querySelectorAll('[data-del]').forEach((b) => b.addEventListener('click', (e) => {
      e.stopPropagation(); S.confirmDelete = b.dataset.del; renderRail();
    }));
    rail.querySelectorAll('[data-delno]').forEach((b) => b.addEventListener('click', (e) => { e.stopPropagation(); S.confirmDelete = null; renderRail(); }));
    rail.querySelectorAll('[data-delyes]').forEach((b) => b.addEventListener('click', async (e) => {
      e.stopPropagation();
      const id = b.dataset.delyes; S.confirmDelete = null;
      try {
        const r = await api(`/api/chats?id=${encodeURIComponent(id)}`, { method: 'DELETE' });
        if (r.current !== S.chat) { S.chat = r.current; loadChat(); } else refreshState();
      } catch (err) { hint(err.message); renderRail(); }
    }));
  }
  function loadChat() {
    if (S.es) { S.es.close(); S.es = null; }
    S.events.clear(); S.nodes.clear(); S.toolNodes.clear(); S.lastSeq = -1;
    $('transcript').innerHTML = '';
    connect();
    stateSoon(100);
  }

  // ---------------------------------------------------------------------------------------------
  // chips + composer
  // ---------------------------------------------------------------------------------------------
  function renderChips() {
    const def = stepDef(S.selected), box = $('chips');
    if (!def.id) { box.innerHTML = ''; return; }
    let h = `<span class="chip step-label eyebrow">Step ${def.n}</span>`;
    for (const c of def.chips || []) {
      S.chipMinutes[c.id] = c.minutes;
      const blocked = c.id === 'pack-picture' && !S.state.references.headshot;
      h += `<button class="chip" data-chip="${c.id}" ${S.busy ? 'disabled' : ''} title="${esc(blocked ? 'Drop a headshot on the References card first' : c.prompt.slice(0, 300))}">${esc(c.label)}</button>`;
    }
    box.innerHTML = h;
    box.querySelectorAll('[data-chip]').forEach((b) => b.addEventListener('click', () => {
      const c = (def.chips || []).find((x) => x.id === b.dataset.chip);
      if (c) send(c.prompt, c.label, c.id);
    }));
  }

  async function send(text, shown, chipId) {
    text = (text || '').trim();
    if (!text || S.busy) return;
    try {
      await post('/api/chat', { message: text, shown: shown || text, step: chipId || null });
      $('input').value = ''; autosize(); setBusy(true);
    } catch (e) { $('input').placeholder = e.message; }
  }
  $('send').onclick = () => send($('input').value);
  $('input').addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send($('input').value); } });
  function autosize() { const t = $('input'); t.style.height = 'auto'; t.style.height = Math.min(220, t.scrollHeight) + 'px'; }
  $('input').addEventListener('input', autosize);
  $('stop').onclick = () => post('/api/stop');

  function setBusy(b) {
    if (S.busy === b) return;
    S.busy = b;
    $('send').disabled = b;
    $('working').hidden = !b;
    document.querySelectorAll('.chip[data-chip]').forEach((c) => { c.disabled = b; });
    document.querySelectorAll('[data-newchat]').forEach((c) => { c.disabled = b; });
    if (b) { S.tick = setInterval(renderWorking, 1000); renderWorking(); }
    else { clearInterval(S.tick); S.tick = null; stateSoon(400); }
    scheduleState();
  }

  function lastEvent(pred) { let f = null; for (const ev of S.events.values()) if (pred(ev)) f = ev; return f; }
  function fmt(secs) { secs = Math.max(0, Math.floor(secs)); return `${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, '0')}`; }
  function renderWorking() {
    const asked = lastEvent((e) => e.kind === 'asked');
    if (!asked) return;
    const elapsed = (Date.now() - asked.at) / 1000;
    $('elapsed').textContent = fmt(elapsed);
    const mins = asked.label ? S.chipMinutes[asked.label] : null;
    const tool = lastEvent((e) => e.kind === 'tool' && e.seq > asked.seq && !e.resolved);
    const talking = lastEvent((e) => e.kind === 'text' && e.seq > asked.seq && !e.final);
    let title = 'Thinking', sub = '';
    if (tool) { title = prettyTool(tool.label); sub = tool.body || ''; }
    else if (talking) title = 'Writing';
    $('workingTitle').textContent = title;
    $('workingSub').textContent = (mins ? `usually ${mins[0]}–${mins[1]} min` : '') + (sub ? (mins ? ' · ' : '') + sub : '');
    const target = mins ? mins[1] * 60 : Math.max(120, elapsed * 1.3);
    $('barFill').style.width = Math.min(96, (elapsed / target) * 100) + '%';
  }
  function prettyTool(name) {
    if (!name) return 'Working';
    const m = /^mcp__(.+?)__(.+)$/.exec(name);
    if (m) {
      const t = m[2];
      const map = { generate_image_batch: 'Generating images', generate_image: 'Generating an image', generate_video_batch: 'Generating video', generate_video: 'Generating video', jobs_wait: 'Waiting for Higgsfield', media_upload: 'Uploading references', media_confirm: 'Confirming upload', balance: 'Checking the balance', show_generation_by_ids: 'Looking at results' };
      return map[t] || `Higgsfield: ${t.replace(/_/g, ' ')}`;
    }
    const map = { Bash: 'Running a command', Read: 'Reading', Write: 'Writing a file', Edit: 'Editing a file', MultiEdit: 'Editing files', Glob: 'Looking for files', Grep: 'Searching', WebFetch: 'Reading a web page', WebSearch: 'Searching the web', Task: 'Delegating to a helper', Skill: 'Loading a skill', TodoWrite: 'Planning' };
    return map[name] || name;
  }

  // ---------------------------------------------------------------------------------------------
  // transcript
  // ---------------------------------------------------------------------------------------------
  function nearBottom() { const t = $('transcript'); return t.scrollHeight - t.scrollTop - t.clientHeight < 160; }
  function scrollBottom() { const t = $('transcript'); t.scrollTop = t.scrollHeight; }

  function onEvent(ev) {
    if (ev.kind === 'chat') { if (ev.chat && ev.chat !== S.chat) { S.chat = ev.chat; loadChat(); } return; }
    const existed = S.events.has(ev.seq);
    S.events.set(ev.seq, ev);
    S.lastSeq = Math.max(S.lastSeq, ev.seq);
    const stick = nearBottom();
    if (ev.kind === 'asked') { setBusy(true); welcomeOff(); }
    if (ev.kind === 'done') setBusy(false);
    if (ev.kind === 'init' && S.state) { S.state.mcp = ev.mcp || []; renderHeader(); }
    if (ev.kind === 'tool_result') {
      const t = S.toolNodes.get(ev.tool_use_id);
      const te = lastEvent((e) => e.kind === 'tool' && e.tool_use_id === ev.tool_use_id);
      if (te) te.resolved = true;
      if (t) {
        t.classList.remove('running');
        if (ev.label === 'error') t.classList.add('failed');
        if (ev.body) { const pre = document.createElement('pre'); pre.textContent = ev.body; t.appendChild(pre); }
      }
      stateSoon(800);
      if (stick) scrollBottom();
      return;
    }
    if (ev.kind === 'status' && ev.label === 'cost') return;
    let node = S.nodes.get(ev.seq);
    if (!node) { node = makeNode(ev); if (node) { S.nodes.set(ev.seq, node); $('transcript').appendChild(node); } }
    else updateNode(node, ev);
    if (stick) scrollBottom();
    if (!existed && (ev.kind === 'done' || ev.kind === 'error')) stateSoon(500);
  }

  function makeNode(ev) {
    let el;
    switch (ev.kind) {
      case 'asked': {
        el = document.createElement('div'); el.className = 'msg user';
        const chip = ev.label ? findChip(ev.label) : null;
        el.innerHTML = `<div class="bubble">${chip ? `<span class="chip-tag">${esc(chip.label)}</span>` : ''}${esc(chip ? '' : ev.body)}</div>`;
        return el;
      }
      case 'text':
        el = document.createElement('div'); el.className = 'msg assistant' + (ev.sub ? ' sub' : '');
        el.innerHTML = `<div class="bubble">${md(ev.body)}</div>`;
        return el;
      case 'thinking':
        el = document.createElement('details'); el.className = 'thinking';
        el.innerHTML = `<summary>thinking…</summary><div class="tbody">${esc(ev.body)}</div>`;
        return el;
      case 'tool':
        el = document.createElement('details'); el.className = 'tool running' + (ev.sub ? ' sub' : '');
        el.innerHTML = `<summary><span class="tname">${esc(prettyTool(ev.label))}</span><span class="tbody">${esc(ev.body || '')}</span></summary>`;
        if (ev.tool_use_id) S.toolNodes.set(ev.tool_use_id, el);
        if (ev.resolved) el.classList.remove('running');
        return el;
      case 'done':
        el = document.createElement('div'); el.className = 'sysline'; el.textContent = ev.body || 'Done.';
        return el;
      case 'error': case 'stderr':
        if (ev.kind === 'stderr' && /^\s*$/.test(ev.body || '')) return null;
        el = document.createElement('div'); el.className = 'sysline bad'; el.textContent = ev.body || ev.label || 'error';
        return el;
      case 'status':
        if (ev.label === 'retry') { el = document.createElement('div'); el.className = 'sysline'; el.textContent = ev.body; return el; }
        return null;
      default: return null;
    }
  }
  function updateNode(node, ev) {
    if (ev.kind === 'text') node.querySelector('.bubble').innerHTML = md(ev.body);
    else if (ev.kind === 'thinking') node.querySelector('.tbody').textContent = ev.body;
    else if (ev.kind === 'tool') { node.querySelector('.tbody').textContent = ev.body || ''; node.querySelector('.tname').textContent = prettyTool(ev.label); if (ev.resolved) node.classList.remove('running'); }
  }
  function findChip(id) { for (const s of S.stepsDef) for (const c of s.chips || []) if (c.id === id) return c; return null; }

  function welcome() {
    if (S.events.size || document.getElementById('welcome')) return;
    const el = document.createElement('div'); el.id = 'welcome'; el.className = 'hello';
    const cur = S.state ? S.state.steps.find((s) => s.id === S.state.current) : null;
    const def = cur ? stepDef(cur.id) : {};
    el.innerHTML = `<div class="hello-eyebrow eyebrow">${cur ? `Step ${cur.n} of 7` : 'Viral Page Studio'}</div>
      <h1 class="hello-title">${esc(cur ? cur.title : 'Hi')}</h1>
      <p class="hello-sub">${esc(def.what || 'Steps on the left, your page on the right, Claude Code in here.')}</p>
      <p class="hello-hint">Press a button below, or just say what you want.</p>`;
    $('transcript').appendChild(el);
  }
  function welcomeOff() { const w = document.getElementById('welcome'); if (w) w.remove(); }

  // ---------------------------------------------------------------------------------------------
  // SSE
  // ---------------------------------------------------------------------------------------------
  function connect() {
    if (S.es) S.es.close();
    const es = new EventSource(`/api/events?since=${S.lastSeq}`);
    S.es = es;
    es.onmessage = (m) => { try { onEvent(JSON.parse(m.data)); } catch (e) { /* ignore */ } };
    es.addEventListener('hello', (m) => {
      try { const h = JSON.parse(m.data); setBusy(!!h.busy); if (h.chat && S.chat && h.chat !== S.chat) { S.chat = h.chat; loadChat(); return; } } catch (e) { /* ignore */ }
      welcome();
    });
    es.onerror = () => { es.close(); setTimeout(connect, 2000); };
  }

  // ---------------------------------------------------------------------------------------------
  // cards
  // ---------------------------------------------------------------------------------------------
  function head(title, status, actions) {
    return `<div class="card-head"><span class="eyebrow"><i class="s-${status || 'none'}"></i>${esc(title)}</span><div class="actions">${actions || ''}</div></div>`;
  }
  const chipBtn = (id, label, cls) => `<button class="btn ${cls || ''}" data-chipbtn="${id}">${esc(label)}</button>`;
  function wireChipBtns(root) {
    root.querySelectorAll('[data-chipbtn]').forEach((b) => b.addEventListener('click', () => {
      const c = findChip(b.dataset.chipbtn);
      if (c) { S.selected = S.stepsDef.find((s) => (s.chips || []).includes(c)).id; renderRail(); renderChips(); send(c.prompt, c.label, c.id); }
    }));
  }

  function renderCards() {
    const st = S.state;
    const steps = Object.fromEntries(st.steps.map((s) => [s.id, s]));
    const cur = (id) => 'card' + (st.current === id ? ' current' : '');

    // Packaging: who the page is
    {
      const p = st.packaging, el = $('cardPack');
      el.className = cur('packaging');
      let h = head('Packaging', steps.packaging.status, p.previewUrl ? `<a class="btn" href="${p.previewUrl}" target="_blank" rel="noopener">Preview ↗</a>` : '');
      if (!p.exists) h += `<div class="empty">No preview account yet.</div>`;
      else {
        const avatar = p.avatarUrl ? `<div class="ring"><img src="${p.avatarUrl}?v=${Date.now() >> 14}" alt="profile picture"></div>` : `<div class="avatar none">no picture</div>`;
        h += `<div class="pack">${avatar}<div>
          <div class="handle ${p.placeholder ? 'placeholder' : ''}">@${esc(p.username || 'yourhandle')}</div>
          <div class="bio ${p.bio ? '' : 'none'}">${p.bio ? esc(p.bio) : 'no bio yet'}</div></div></div>`;
        const todo = [];
        if (p.placeholder) todo.push(chipBtn('pack-username', 'Find a username', 'hot'));
        if (!p.avatarUrl) todo.push(chipBtn('pack-picture', 'Profile picture', p.placeholder ? '' : 'hot'));
        if (!p.bio) todo.push(chipBtn('pack-bio', 'Bio'));
        if (p.freeHandleCount) todo.push(`<button class="btn quiet" id="showHandles">${p.freeHandleCount} free handles</button>`);
        if (todo.length) h += `<div class="row">${todo.join('')}</div>`;
      }
      el.innerHTML = h;
      wireChipBtns(el);
      const sh = el.querySelector('#showHandles'); if (sh) sh.onclick = openHandles;
    }
    // Reels
    {
      const el = $('cardReels'), s = steps.reels;
      el.className = cur('reels');
      let h = head('Reels', s.status, chipBtn('reel-make', st.reels.length ? 'Make the next' : 'Make reel 1', st.reels.length >= 3 ? 'quiet' : 'hot'));
      const cells = st.reels.map((r) => r.cover
        ? `<div class="reel" data-reel="${r.n}"><img src="${r.cover}" alt="${esc(r.slug)}" loading="lazy"><span class="num">${r.n}</span>${r.videoUrl ? '<span class="play">▶</span>' : ''}<div class="cap">${esc((r.caption || r.slug).split('\n')[0])}</div></div>`
        : `<div class="reel nocover" data-reel="${r.n}">${r.n} · ${esc(r.slug)}</div>`);
      for (let i = st.reels.length; i < 3; i++) cells.push(`<div class="reel slot">reel ${i + 1}</div>`);
      h += `<div class="reels-grid">${cells.join('')}</div>`;
      const run = st.runs.find((r) => !r.notes);
      if (run) h += `<div class="run"><span>${esc(run.name.replace(/^\d{4}-\d\d-\d\d-/, ''))}</span><span class="stages"><span class="${run.plan ? 'on' : ''}">plan</span><span class="${run.candidates ? 'on' : ''}">frames</span><span class="${run.selected ? 'on' : ''}">picks</span><span class="${run.clips ? 'on' : ''}">clips</span><span class="${run.music ? 'on' : ''}">music</span></span>${run.contact ? `<a class="btn quiet" href="${run.contact}" target="_blank" rel="noopener">sheet</a>` : ''}</div>`;
      el.innerHTML = h;
      wireChipBtns(el);
      el.querySelectorAll('.reel[data-reel]').forEach((x) => x.addEventListener('click', () => openReel(+x.dataset.reel)));
    }
    // References
    {
      const r = st.references, el = $('cardRefs');
      el.className = cur('references');
      let h = head('References', r.style.length ? 'done' : '', r.style.length ? chipBtn(r.defaultSet ? 'refs-default' : 'refs-mine', 'Describe the look', 'quiet') : '');
      h += `<div class="refs-row">${r.style.slice(0, 7).map((s) => `<div class="ref"><img src="${s.url}" alt="${esc(s.name)}" loading="lazy"><button class="del" data-del="references/visual-style/${esc(s.name)}" title="remove">×</button></div>`).join('')}
             <label class="drop" id="dropStyle"><input type="file" accept="image/*" multiple>+</label></div>`;
      h += `<div class="headshot-row">${r.headshot ? `<img class="headshot" src="${r.headshot.url}" alt="headshot">` : '<div class="headshot"></div>'}
             <label class="drop" id="dropHead"><input type="file" accept="image/*">${r.headshot ? 'Replace headshot' : 'Drop your headshot'}</label></div>`;
      el.innerHTML = h;
      wireChipBtns(el);
      wireDrop(el.querySelector('#dropStyle'), 'style');
      wireDrop(el.querySelector('#dropHead'), 'headshot');
      el.querySelectorAll('[data-del]').forEach((b) => b.addEventListener('click', async () => {
        if (!confirm('Remove this reference?')) return;
        await fetch('/api/reference?path=' + encodeURIComponent(b.dataset.del), { method: 'DELETE' }); refreshState();
      }));
    }
    // Concept
    {
      const c = st.concept, el = $('cardConcept');
      el.className = cur('concept');
      if (c.exists) {
        el.innerHTML = head('Concept', 'done', `<button class="btn quiet" id="openConcept">Read</button>`) +
          `<p class="concept-title t">${esc(c.title.replace(/^Concept:\s*/i, ''))}</p><p class="concept-line">${esc(c.oneLiner)}</p>`;
        el.querySelector('#openConcept').onclick = () => openFile(c.path);
      } else {
        el.innerHTML = head('Concept', '') + `<div class="empty"><span class="t">No idea yet</span>${chipBtn('concept-interview', 'Help me find one', 'hot')} ${c.examples.length ? chipBtn('concept-example', 'Use the example') : ''}</div>`;
        wireChipBtns(el);
      }
    }
  }


  function wireDrop(label, kind) {
    if (!label) return;
    const input = label.querySelector('input');
    const upload = async (files) => {
      for (const f of files) {
        if (!/^image\//.test(f.type)) continue;
        label.textContent = '…';
        try { await fetch(`/api/upload?kind=${kind}&name=${encodeURIComponent(f.name)}`, { method: 'POST', body: f }); }
        catch (e) { alert('Upload failed: ' + e.message); }
      }
      refreshState();
    };
    input.addEventListener('change', () => upload([...input.files]));
    label.addEventListener('dragover', (e) => { e.preventDefault(); label.classList.add('over'); });
    label.addEventListener('dragleave', () => label.classList.remove('over'));
    label.addEventListener('drop', (e) => { e.preventDefault(); label.classList.remove('over'); upload([...e.dataTransfer.files]); });
  }

  // ---------------------------------------------------------------------------------------------
  // modal: concept, reel, handles, keys
  // ---------------------------------------------------------------------------------------------
  function openModal(html) { $('modalBody').innerHTML = html; $('modal').hidden = false; }
  function closeModal() { $('modal').hidden = true; $('modalBody').innerHTML = ''; }
  $('modalClose').onclick = closeModal;
  $('modal').addEventListener('click', (e) => { if (e.target === $('modal')) closeModal(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });

  async function openFile(path) {
    try {
      const f = await api('/api/file?path=' + encodeURIComponent(path));
      openModal(`<div class="md">${md(f.text)}</div><div class="row"><button class="btn" id="openInEditor">Open the file</button></div>`);
      $('openInEditor').onclick = () => post('/api/open', { path });
    } catch (e) { openModal(`<p>${esc(e.message)}</p>`); }
  }
  function openReel(n) {
    const r = S.state.reels.find((x) => x.n === n);
    if (!r) return;
    const cap = r.caption || '';
    openModal(`<h2>${esc(cap.split('\n')[0] || r.slug)}</h2>
      ${r.videoUrl ? `<video src="${r.videoUrl}" controls autoplay playsinline></video>` : `<div class="empty">No video on this machine. The job ids in the run folder let Claude re-download it.</div>`}
      ${cap ? `<div class="caption-box">${esc(cap)}</div>` : ''}
      <div class="row"><button class="btn" id="revealReel">Show in Finder</button>${cap ? `<button class="btn" id="copyCap">Copy caption</button>` : ''}</div>`);
    $('revealReel').onclick = () => post('/api/open', { path: r.folder });
    const cc = $('copyCap'); if (cc) cc.onclick = () => navigator.clipboard.writeText(cap).then(() => { cc.textContent = 'copied'; });
  }
  function openHandles() {
    const p = S.state.packaging;
    openModal(`<h2>${p.freeHandleCount} free handles</h2><p class="small">Checked against Instagram's signup form. Click one to use it.</p>
      <div class="handles">${p.freeHandles.map((x) => `<span data-handle="${esc(x)}">${esc(x)}</span>`).join('')}</div>`);
    $('modalBody').querySelectorAll('[data-handle]').forEach((x) => x.addEventListener('click', () => {
      closeModal();
      send(`Use @${x.dataset.handle} as my handle: set HANDLE in instagram-preview/my-account.js and tell me when the Packaging card shows it.`, `Use @${x.dataset.handle}`, null);
    }));
  }
  function openKeys() {
    const e = S.state.env, t = S.state.tools || {};
    const mcp = (S.state.mcp || []).find((m) => /higgsfield/i.test(m.name || ''));
    const row = (k, ok, v) => `<span class="k">${k}</span><span class="${ok ? 'ok' : 'bad'}">${ok ? (v ? esc(v) : 'ok') : 'missing'}</span>`;
    openModal(`<h2>Keys and tools</h2>
      <p class="small">Keys go into <code>.env</code> in the project folder and never leave your machine. No Anthropic key: Claude Code runs on your plan.</p>
      <label>Apify key <span>· usernames, references, music · <a href="https://console.apify.com/account/integrations" target="_blank" rel="noopener">get one</a></span></label>
      <input type="password" id="kApify" placeholder="${e.APIFY_API_KEY ? 'set (paste to replace)' : 'apify_api_…'}">
      <label>Gemini key <span>· optional, motion analysis · <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener">get one</a></span></label>
      <input type="password" id="kGemini" placeholder="${e.GEMINI_API_KEY ? 'set (paste to replace)' : 'AIza…'}">
      <div class="kv" style="margin-top:16px">
        ${row('Claude Code', t.claude && t.claude.ok, t.claude && t.claude.version)}
        ${row('Higgsfield MCP', mcp && ['connected', 'pending'].includes(mcp.status), mcp ? mcp.status : (S.state.mcp && S.state.mcp.length ? '' : 'checked on the first message'))}
        ${row('Higgsfield CLI', t.higgsfield && t.higgsfield.ok, t.higgsfield && t.higgsfield.version)}
        ${row('ffmpeg', t.ffmpeg && t.ffmpeg.ok, t.ffmpeg && t.ffmpeg.version)}
        ${row('node', t.node && t.node.ok, t.node && t.node.version)}
        ${row('yt-dlp', t['yt-dlp'] && t['yt-dlp'].ok, t['yt-dlp'] && t['yt-dlp'].version)}
      </div>
      <p class="small">Missing something? Say "install what is missing from the Keys box" in the chat. MCP: <code>claude mcp add --scope user --transport http higgsfield https://mcp.higgsfield.ai/mcp</code> in the terminal, then <code>/mcp</code> in Claude Code and Authenticate; <code>claude mcp list</code> must say Connected. Balance: <code>higgsfield auth login</code>.</p>
      <div class="row"><button class="btn" id="kCancel">Close</button><button class="btn hot" id="kSave">Save</button></div>`);
    $('kCancel').onclick = closeModal;
    $('kSave').onclick = async () => {
      const body = {};
      if ($('kApify').value.trim()) body.APIFY_API_KEY = $('kApify').value.trim();
      if ($('kGemini').value.trim()) body.GEMINI_API_KEY = $('kGemini').value.trim();
      if (Object.keys(body).length) await post('/api/env', body);
      closeModal(); refreshState();
    };
  }

  // ---------------------------------------------------------------------------------------------
  // boot
  // ---------------------------------------------------------------------------------------------
  (async () => {
    try { S.stepsDef = (await api('/api/steps')).steps; } catch (e) { S.stepsDef = []; }
    await refreshState();
    connect();
    scheduleState();
  })();
})();
