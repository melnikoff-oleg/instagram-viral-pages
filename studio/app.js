/* Viral Page Studio, browser side. Vanilla JS, no build step.
   Talks to serve.py: /api/state (what exists), /api/events (the Claude Code stream), /api/chat (send). */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const S = {
    stepsDef: [],      // from steps.json
    state: null,       // from /api/state
    events: new Map(), // seq -> event
    nodes: new Map(),  // seq -> DOM node
    toolNodes: new Map(), // tool_use_id -> tool <details>
    lastSeq: -1,
    busy: false,
    selected: null,    // selected step id in the rail
    es: null,
    tick: null,
    chipMinutes: {},   // chip id -> [lo, hi]
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
        flush();
        const buf = []; i++;
        while (i < lines.length && !/^```/.test(lines[i])) buf.push(lines[i++]);
        i++;
        out += `<pre><code>${esc(buf.join('\n'))}</code></pre>`;
        continue;
      }
      const h = /^(#{1,6})\s+(.*)$/.exec(l);
      if (h) { flush(); out += `<h${Math.min(h[1].length, 3)}>${inline(h[2])}</h${Math.min(h[1].length, 3)}>`; i++; continue; }
      if (/^\s*([-*_]){3,}\s*$/.test(l)) { flush(); out += '<hr>'; i++; continue; }
      if (/^\s*\|.*\|\s*$/.test(l) && i + 1 < lines.length && /^\s*\|[\s:|-]+\|\s*$/.test(lines[i + 1])) {
        flush();
        const cells = (r) => r.trim().replace(/^\||\|$/g, '').split('|').map((c) => inline(c.trim()));
        let t = `<table><thead><tr>${cells(l).map((c) => `<th>${c}</th>`).join('')}</tr></thead><tbody>`;
        i += 2;
        while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) { t += `<tr>${cells(lines[i]).map((c) => `<td>${c}</td>`).join('')}</tr>`; i++; }
        out += t + '</tbody></table>';
        continue;
      }
      const ul = /^\s*[-*+]\s+(.*)$/.exec(l), ol = /^\s*\d+[.)]\s+(.*)$/.exec(l);
      if (ul || ol) {
        flush();
        const tag = ul ? 'ul' : 'ol';
        const re = ul ? /^\s*[-*+]\s+(.*)$/ : /^\s*\d+[.)]\s+(.*)$/;
        out += `<${tag}>`;
        while (i < lines.length) {
          const m = re.exec(lines[i]);
          if (!m) {
            if (/^\s{2,}\S/.test(lines[i]) && out.endsWith('</li>')) { out = out.slice(0, -5) + ' ' + inline(lines[i].trim()) + '</li>'; i++; continue; }
            break;
          }
          out += `<li>${inline(m[1])}</li>`; i++;
        }
        out += `</${tag}>`;
        continue;
      }
      if (!l.trim()) { flush(); i++; continue; }
      para.push(l.trim()); i++;
    }
    flush();
    return out;
  }

  // ---------------------------------------------------------------------------------------------
  // api
  // ---------------------------------------------------------------------------------------------
  async function api(path, opts) {
    const r = await fetch(path, opts);
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(j.error || r.statusText);
    return j;
  }
  const post = (path, body) => api(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) });

  // ---------------------------------------------------------------------------------------------
  // state
  // ---------------------------------------------------------------------------------------------
  let stateTimer = null, stateInFlight = false;
  async function refreshState() {
    if (stateInFlight) return;
    stateInFlight = true;
    try {
      S.state = await api('/api/state');
      if (!S.selected || !S.stepsDef.find((s) => s.id === S.selected)) S.selected = S.state.current;
      renderHeader(); renderRail(); renderChips(); renderCards();
    } catch (e) {
      $('hint').textContent = 'The studio server is not answering. Is serve.py still running?';
    } finally { stateInFlight = false; }
  }
  function scheduleState() {
    clearTimeout(stateTimer);
    stateTimer = setTimeout(refreshState, S.busy ? 2500 : 20000);
  }
  function stateSoon(ms = 600) { clearTimeout(stateTimer); stateTimer = setTimeout(refreshState, ms); }

  // ---------------------------------------------------------------------------------------------
  // header
  // ---------------------------------------------------------------------------------------------
  function renderHeader() {
    const st = S.state;
    $('projectName').textContent = st.project.name + (st.project.isTemplate ? '' : '  (external project)');
    const b = st.balance || {};
    const pill = $('balancePill');
    if (b.ok) {
      const c = Math.round(b.credits);
      pill.className = 'pill ' + (c < 100 ? 'bad' : c < 300 ? 'warn' : 'ok');
      pill.innerHTML = `<b>${c.toLocaleString()}</b> credits${b.plan ? ` · ${esc(b.plan)}` : ''}`;
      pill.title = `Higgsfield: ${esc(b.email || '')}. Click to refresh.`;
    } else {
      pill.className = 'pill bad';
      pill.textContent = 'Higgsfield: ' + (b.error || 'unknown');
      pill.title = 'Install the Higgsfield CLI and sign in (higgsfield auth login) to see the balance here. Click to retry.';
    }
    const mcp = (st.mcp || []).find((m) => /higgsfield/i.test(m.name || ''));
    const mp = $('mcpPill');
    if (mcp) {
      const ok = mcp.status === 'connected', pend = mcp.status === 'pending';
      mp.className = 'pill ' + (ok ? 'ok' : pend ? 'warn' : 'bad');
      mp.textContent = 'Higgsfield MCP ' + (ok ? 'connected' : pend ? 'ready (connects on first use)' : mcp.status);
    }
    else if (st.mcp && st.mcp.length) { mp.className = 'pill bad'; mp.textContent = 'Higgsfield MCP missing'; mp.title = 'Claude Code sees: ' + st.mcp.map((m) => m.name).join(', '); }
    else { mp.className = 'pill'; mp.textContent = 'Higgsfield MCP: checked on the first message'; }
    const keysOk = st.env.APIFY_API_KEY;
    const kb = $('keysBtn');
    kb.className = 'pill ' + (keysOk ? 'ok' : 'warn');
    kb.textContent = keysOk ? 'Keys' : 'Keys missing';
    const prev = $('openPreview');
    if (st.packaging.previewUrl) { prev.href = st.packaging.previewUrl; prev.hidden = false; } else prev.hidden = true;
  }
  $('balancePill').onclick = async () => { $('balancePill').textContent = 'refreshing…'; await api('/api/balance?refresh=1'); refreshState(); };
  $('keysBtn').onclick = () => openKeys();

  // ---------------------------------------------------------------------------------------------
  // steps rail
  // ---------------------------------------------------------------------------------------------
  function stepDef(id) { return S.stepsDef.find((s) => s.id === id) || {}; }
  function renderRail() {
    const rail = $('rail');
    const st = S.state;
    let h = '<h2>The seven steps</h2>';
    for (const s of st.steps) {
      const def = stepDef(s.id);
      const cls = ['step', 'st-' + s.status, s.id === st.current ? 'current' : '', s.id === S.selected ? 'selected' : ''].join(' ');
      const dot = s.status === 'done' ? '✓' : '';
      let parts = '';
      if (s.parts) parts = `<div class="parts">${Object.entries(s.parts).map(([k, v]) => `<span class="${v ? 'on' : ''}">${k}</span>`).join('')}</div>`;
      let mark = '';
      if (['posting', 'autopilot', 'monetize'].includes(s.id) && s.status !== 'later') {
        mark = `<button class="mark" data-mark="${s.id}" data-done="${s.status === 'done' ? 0 : 1}">${s.status === 'done' ? 'undo' : 'mark done'}</button>`;
      }
      h += `<div class="${cls}" data-step="${s.id}" title="${esc(def.what || '')}">
        <div class="dot">${dot}</div>
        <div><div class="title"><span class="n">${s.n}</span>${esc(s.title)}${s.optional ? '<span class="tag">optional</span>' : ''}${s.status === 'later' ? '<span class="tag">later</span>' : ''}</div>
        <div class="detail">${esc(s.detail || '')}</div>${parts}${mark}</div></div>`;
    }
    rail.innerHTML = h;
    rail.querySelectorAll('.step').forEach((el) => el.addEventListener('click', () => { S.selected = el.dataset.step; renderRail(); renderChips(); renderCards(); }));
    rail.querySelectorAll('.mark').forEach((b) => b.addEventListener('click', async (e) => {
      e.stopPropagation();
      await post('/api/mark', { step: b.dataset.mark, done: b.dataset.done === '1' });
      refreshState();
    }));
  }

  // ---------------------------------------------------------------------------------------------
  // chips + composer
  // ---------------------------------------------------------------------------------------------
  function renderChips() {
    const def = stepDef(S.selected);
    const box = $('chips');
    if (!def.id) { box.innerHTML = ''; return; }
    const stStep = (S.state.steps || []).find((s) => s.id === def.id) || {};
    let h = `<span class="chip step-label">Step ${def.n} · ${esc(def.title)}</span>`;
    for (const c of def.chips || []) {
      S.chipMinutes[c.id] = c.minutes;
      const needsHeadshot = c.id === 'pack-picture' && !S.state.references.headshot;
      h += `<button class="chip" data-chip="${c.id}" ${S.busy ? 'disabled' : ''} title="${esc(c.prompt.slice(0, 300))}">${esc(c.label)}${needsHeadshot ? ' <span class="eta">drop a headshot first</span>' : `<span class="eta">~${c.minutes[0]}–${c.minutes[1]} min</span>`}</button>`;
    }
    box.innerHTML = h;
    box.querySelectorAll('[data-chip]').forEach((b) => b.addEventListener('click', () => {
      const c = (def.chips || []).find((x) => x.id === b.dataset.chip);
      if (c) send(c.prompt, c.label, c.id);
    }));
    $('hint').textContent = stStep.status === 'later' ? `${def.what || ''} This step unlocks once the one before it is marked done.` : (def.what || '');
  }

  async function send(text, shown, chipId) {
    text = (text || '').trim();
    if (!text || S.busy) return;
    try {
      await post('/api/chat', { message: text, shown: shown || text, step: chipId || null });
      $('input').value = ''; autosize();
      setBusy(true);
    } catch (e) {
      $('hint').textContent = e.message;
    }
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
    if (b) { S.tick = setInterval(renderWorking, 1000); renderWorking(); }
    else { clearInterval(S.tick); S.tick = null; stateSoon(400); }
    scheduleState();
  }

  function lastEvent(pred) {
    let found = null;
    for (const ev of S.events.values()) if (pred(ev)) found = ev;
    return found;
  }
  function fmt(secs) { secs = Math.max(0, Math.floor(secs)); const m = Math.floor(secs / 60), s = secs % 60; return `${m}:${String(s).padStart(2, '0')}`; }
  function renderWorking() {
    const asked = lastEvent((e) => e.kind === 'asked');
    if (!asked) return;
    const elapsed = (Date.now() - asked.at) / 1000;
    $('elapsed').textContent = fmt(elapsed);
    const mins = asked.label ? S.chipMinutes[asked.label] : null;
    const tool = lastEvent((e) => e.kind === 'tool' && e.seq > asked.seq && !e.resolved);
    const talking = lastEvent((e) => e.kind === 'text' && e.seq > asked.seq && !e.final);
    let title = 'Working', sub = '';
    if (tool) { title = prettyTool(tool.label); sub = tool.body || ''; }
    else if (talking) { title = 'Writing'; }
    else title = 'Thinking';
    $('workingTitle').textContent = title;
    $('workingSub').textContent = sub + (mins ? `${sub ? ' · ' : ''}this step usually takes ${mins[0]}–${mins[1]} min` : '');
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
    const existed = S.events.has(ev.seq);
    S.events.set(ev.seq, ev);
    S.lastSeq = Math.max(S.lastSeq, ev.seq);
    const stick = nearBottom();
    if (ev.kind === 'asked') { setBusy(true); welcomeOff(); }
    if (ev.kind === 'done') setBusy(false);
    if (ev.kind === 'init') { if (S.state) { S.state.mcp = ev.mcp || []; renderHeader(); } }
    if (ev.kind === 'tool_result') {
      const t = S.toolNodes.get(ev.tool_use_id);
      const te = lastEvent((e) => e.kind === 'tool' && e.tool_use_id === ev.tool_use_id);
      if (te) te.resolved = true;
      if (t) {
        t.classList.remove('running');
        if (ev.label === 'error') t.classList.add('failed');
        if (ev.body) { const pre = document.createElement('pre'); pre.textContent = ev.body; t.appendChild(pre); }
      }
      stateSoon(800); // something may have landed in a card
      if (stick) scrollBottom();
      return;
    }
    if (ev.kind === 'status' && ev.label === 'cost') { if (stick) scrollBottom(); return; }
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
        el.innerHTML = `<div class="bubble">${chip ? `<span class="chip-tag">${esc(chip.label)}</span>` : ''}${esc(ev.body)}</div>`;
        return el;
      }
      case 'text': {
        el = document.createElement('div'); el.className = 'msg assistant' + (ev.sub ? ' sub' : '');
        el.innerHTML = `<div class="bubble">${md(ev.body)}</div>`;
        return el;
      }
      case 'thinking': {
        el = document.createElement('details'); el.className = 'thinking';
        el.innerHTML = `<summary>thinking…</summary><div class="tbody">${esc(ev.body)}</div>`;
        return el;
      }
      case 'tool': {
        el = document.createElement('details'); el.className = 'tool running' + (ev.sub ? ' sub' : '');
        el.innerHTML = `<summary><span class="tname">${esc(prettyTool(ev.label))}</span><span class="tbody">${esc(ev.body || '')}</span></summary>`;
        if (ev.tool_use_id) S.toolNodes.set(ev.tool_use_id, el);
        if (ev.resolved) el.classList.remove('running');
        return el;
      }
      case 'done': {
        el = document.createElement('div'); el.className = 'sysline';
        el.textContent = ev.body || 'Done.';
        return el;
      }
      case 'error': case 'stderr': {
        if (ev.kind === 'stderr' && /^\s*$/.test(ev.body || '')) return null;
        el = document.createElement('div'); el.className = 'sysline bad';
        el.textContent = ev.body || ev.label || 'error';
        return el;
      }
      case 'status': {
        if (ev.label === 'retry') { el = document.createElement('div'); el.className = 'sysline'; el.textContent = ev.body; return el; }
        return null;
      }
      default: return null;
    }
  }
  function updateNode(node, ev) {
    if (ev.kind === 'text') node.querySelector('.bubble').innerHTML = md(ev.body);
    else if (ev.kind === 'thinking') node.querySelector('.tbody').textContent = ev.body;
    else if (ev.kind === 'tool') { node.querySelector('.tbody').textContent = ev.body || ''; node.querySelector('.tname').textContent = prettyTool(ev.label); if (ev.resolved) node.classList.remove('running'); }
  }
  function findChip(id) { for (const s of S.stepsDef) for (const c of s.chips || []) if (c.id === id) return c; return null; }

  // welcome bubble when the transcript is empty
  function welcome() {
    if (S.events.size || document.getElementById('welcome')) return;
    const el = document.createElement('div'); el.id = 'welcome'; el.className = 'msg assistant';
    const cur = S.state ? S.state.steps.find((s) => s.id === S.state.current) : null;
    el.innerHTML = `<div class="bubble">${md(
      `**Welcome to Viral Page Studio.**\n\nThe seven steps are on the left, your page is on the right, and this chat is Claude Code working inside your project folder. Press a button under this chat or just type.\n\n` +
      (cur ? `You are on **step ${cur.n}: ${cur.title}**. ${stepDef(cur.id).what || ''}` : '')
    )}</div>`;
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
    es.addEventListener('hello', (m) => { try { const d = JSON.parse(m.data); setBusy(!!d.busy); } catch (e) { /* ignore */ } welcome(); });
    es.onerror = () => { es.close(); setTimeout(connect, 2000); };
  }

  // ---------------------------------------------------------------------------------------------
  // cards
  // ---------------------------------------------------------------------------------------------
  function head(n, title, status, actions) {
    const st = status ? `<span class="state ${status}">${status === 'done' ? 'ready' : status === 'partial' ? 'in progress' : 'empty'}</span>` : '';
    return `<div class="card-head"><h3><span class="n">${n}</span>${esc(title)}${st}</h3><div class="actions">${actions || ''}</div></div>`;
  }
  function chipBtn(chipId, label, cls) {
    return `<button class="btn ${cls || ''}" data-chipbtn="${chipId}">${esc(label)}</button>`;
  }
  function wireChipBtns(root) {
    root.querySelectorAll('[data-chipbtn]').forEach((b) => b.addEventListener('click', () => {
      const c = findChip(b.dataset.chipbtn);
      if (c) { S.selected = S.stepsDef.find((s) => (s.chips || []).includes(c)).id; renderRail(); renderChips(); send(c.prompt, c.label, c.id); }
    }));
  }

  function renderCards() {
    const st = S.state;
    const steps = Object.fromEntries(st.steps.map((s) => [s.id, s]));
    // Concept
    {
      const c = st.concept, el = $('cardConcept');
      el.className = 'card' + (st.current === 'concept' ? ' current' : '');
      if (c.exists) {
        el.innerHTML = head(1, 'Concept', 'done', `<button class="btn" id="openConcept">Read</button>`) +
          `<p class="concept-title">${esc(c.title)}</p><p class="concept-line">${esc(c.oneLiner)}</p>
           <div class="pills">${c.sections.map((s) => `<span>${esc(s)}</span>`).join('')}</div>
           <div class="meta">${c.words.toLocaleString()} words · ${esc(c.path)} · ${new Date(c.modified * 1000).toLocaleString()}</div>`;
        el.querySelector('#openConcept').onclick = () => openFile(c.path);
      } else {
        el.innerHTML = head(1, 'Concept', 'empty') +
          `<div class="empty"><b>No concept yet.</b><br>Step 1: say what the page is about, or start from the example.<br>${chipBtn('concept-interview', 'Help me find my idea', 'hot')} ${c.examples.length ? chipBtn('concept-example', 'Use the example') : ''}</div>`;
        wireChipBtns(el);
      }
    }
    // References
    {
      const r = st.references, el = $('cardRefs');
      el.className = 'card' + (st.current === 'references' ? ' current' : '');
      let h = head(2, 'References', r.style.length ? 'done' : 'empty', r.style.length ? `<button class="btn" data-chipbtn="${r.defaultSet ? 'refs-default' : 'refs-mine'}">Describe the look</button>` : '');
      h += `<div class="refs-strip">${r.style.map((s) => `<div class="ref"><img src="${s.url}" alt="${esc(s.name)}" loading="lazy"><button class="del" data-del="references/visual-style/${esc(s.name)}" title="remove">×</button></div>`).join('')}
             <label class="drop" id="dropStyle"><input type="file" accept="image/*" multiple>+ add stills</label></div>`;
      h += `<div class="meta">${r.style.length ? `${r.style.length} style references${r.defaultSet ? ', the default set' : ''}. Style only, never posted.` : 'Drop a few stills that look how your page should look, or keep the default set.'}</div>`;
      h += `<div class="headshot-row">${r.headshot ? `<img class="headshot" src="${r.headshot.url}" alt="headshot">` : '<div class="headshot"></div>'}
             <label class="drop" id="dropHead"><input type="file" accept="image/*">${r.headshot ? 'Replace the headshot' : '<b>Drop your headshot here</b><br>for the profile picture'}</label></div>`;
      el.innerHTML = h;
      wireChipBtns(el);
      wireDrop(el.querySelector('#dropStyle'), 'style');
      wireDrop(el.querySelector('#dropHead'), 'headshot');
      el.querySelectorAll('[data-del]').forEach((b) => b.addEventListener('click', async () => {
        if (!confirm('Remove this reference?')) return;
        await fetch('/api/reference?path=' + encodeURIComponent(b.dataset.del), { method: 'DELETE' }); refreshState();
      }));
    }
    // Packaging
    {
      const p = st.packaging, el = $('cardPack'), s = steps.packaging;
      el.className = 'card' + (st.current === 'packaging' ? ' current' : '');
      const actions = (p.previewUrl ? `<a class="btn hot" href="${p.previewUrl}" target="_blank" rel="noopener">Open full preview ↗</a>` : '');
      let h = head(3, 'Packaging', s.status, actions);
      if (!p.exists) {
        h += `<div class="empty"><b>No preview account yet.</b><br>instagram-preview/my-account.js is missing.</div>`;
      } else {
        const avatar = p.avatarUrl ? `<img class="avatar" src="${p.avatarUrl}?v=${st.concept.modified || ''}${Date.now() >> 14}" alt="profile picture">` : `<div class="avatar none">no picture</div>`;
        const alts = p.avatarAlternates && p.avatarAlternates.length ? `<div class="alts">${p.avatarAlternates.map((a) => `<img src="${a}" title="alternate">`).join('')}</div>` : '';
        h += `<div class="pack"><div>${avatar}${alts}</div><div>
          <div class="handle ${p.placeholder ? 'placeholder' : ''}">@${esc(p.username || 'yourhandle')}${p.placeholder ? '<small>placeholder</small>' : ''}</div>
          <div class="counts"><span><b>${esc(p.counts.posts ?? p.postCount)}</b> posts</span><span><b>${esc(p.counts.followers ?? '0')}</b> followers</span><span><b>${esc(p.counts.following ?? '0')}</b> following</span></div>
          ${p.category ? `<div class="meta" style="margin:0 0 4px">${esc(p.category)}</div>` : ''}
          <div class="bio ${p.bio ? '' : 'none'}">${p.bio ? esc(p.bio) : 'no bio yet'}</div>
          ${p.note ? `<div class="note">${esc(p.note)}</div>` : ''}
        </div></div>`;
        const todo = [];
        if (p.placeholder) todo.push(chipBtn('pack-username', 'Find a free username'));
        if (!p.avatarUrl) todo.push(chipBtn('pack-picture', st.references.headshot ? 'Make my profile picture' : 'Profile picture (drop a headshot first)'));
        if (!p.bio) todo.push(chipBtn('pack-bio', 'Write my bio'));
        if (todo.length) h += `<div class="pills" style="margin-top:10px;gap:6px">${todo.join('')}</div>`;
        if (p.freeHandleCount) h += `<div class="free">${p.freeHandleCount} free handles found · click one to pick it<div class="pills" style="margin-top:4px">${p.freeHandles.map((x) => `<span data-handle="${esc(x)}">${esc(x)}</span>`).join('')}</div></div>`;
        if (p.previewUrl) {
          h += `<div class="mini-wrap"><div class="mini" id="mini"><iframe src="${p.previewUrl}" title="profile preview" tabindex="-1" loading="lazy"></iframe><a class="cover" href="${p.previewUrl}" target="_blank" rel="noopener" title="open the full preview"></a></div>
                <div class="mini-foot"><span>Live preview of the profile page, as Instagram shows it on desktop</span><a class="btn" href="${p.previewUrl}" target="_blank" rel="noopener">Open ↗</a></div></div>`;
        }
      }
      el.innerHTML = h;
      wireChipBtns(el);
      el.querySelectorAll('[data-handle]').forEach((x) => x.addEventListener('click', () => send(`Use @${x.dataset.handle} as my handle: set HANDLE in instagram-preview/my-account.js and tell me when the Packaging card shows it.`, `Pick @${x.dataset.handle}`, null)));
      fitMini();
    }
    // Reels
    {
      const el = $('cardReels'), s = steps.reels;
      el.className = 'card' + (st.current === 'reels' ? ' current' : '');
      let h = head(4, 'Reels', s.status, `<span class="meta" style="margin:0">${st.reels.length} made</span>`);
      const cells = st.reels.map((r) => r.cover
        ? `<div class="reel" data-reel="${r.n}"><img src="${r.cover}" alt="${esc(r.slug)}" loading="lazy"><span class="num">${r.n}</span>${r.pinned ? '<span class="pin">pinned</span>' : ''}${r.videoUrl ? '<span class="play">▶</span>' : ''}<div class="cap">${esc((r.caption || r.slug).split('\n')[0])}<small>${r.inPreview ? 'in the preview' : 'not in the preview yet'}${r.videos.length ? ` · ${r.videos.length} cut${r.videos.length > 1 ? 's' : ''}` : ''}</small></div></div>`
        : `<div class="reel nocover" data-reel="${r.n}">${r.n} · ${esc(r.slug)}<br><small>no cover yet</small></div>`);
      for (let i = st.reels.length; i < 3; i++) cells.push(`<div class="reel slot">reel ${i + 1}</div>`);
      h += `<div class="reels-grid">${cells.join('')}</div>`;
      if (st.reels.length < 3 || true) {
        h += `<div class="pills" style="margin-top:10px;gap:6px">${chipBtn('reel-plan', 'Plan the next reel')}${chipBtn('reel-make', st.reels.length ? 'Make the next reel' : 'Make reel 1', 'hot')}${st.reels.length ? chipBtn('reel-judge', 'Judge the last one') : ''}</div>`;
      }
      if (st.runs.length) {
        h += `<div class="runs"><div class="meta" style="margin:0 0 2px">Pipeline runs</div>${st.runs.map((r) => `<div class="run"><div><div class="name">${esc(r.name)}</div><div class="stages">
          <span class="${r.plan ? 'on' : ''}">plan</span><span class="${r.candidates ? 'on' : ''}">${r.candidates || ''} frames</span><span class="${r.selected ? 'on' : ''}">${r.selected || ''} picks</span><span class="${r.clips ? 'on' : ''}">${r.clips || ''} clips</span><span class="${r.music ? 'on' : ''}">music</span><span class="${r.notes ? 'on' : ''}">notes</span></div></div>
          ${r.contact ? `<a class="btn" href="${r.contact}" target="_blank" rel="noopener">sheet</a>` : ''}</div>`).join('')}</div>`;
      }
      el.innerHTML = h;
      wireChipBtns(el);
      el.querySelectorAll('.reel[data-reel]').forEach((x) => x.addEventListener('click', () => openReel(+x.dataset.reel)));
    }
  }

  function fitMini() {
    const m = document.getElementById('mini');
    if (!m) return;
    const f = m.querySelector('iframe');
    const s = m.clientWidth / 1280;
    f.style.transform = `scale(${s})`;
  }
  window.addEventListener('resize', fitMini);

  function wireDrop(label, kind) {
    if (!label) return;
    const input = label.querySelector('input');
    const upload = async (files) => {
      for (const f of files) {
        if (!/^image\//.test(f.type)) continue;
        label.textContent = 'uploading…';
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
  // modal: concept, reel, keys
  // ---------------------------------------------------------------------------------------------
  function openModal(html) { $('modalBody').innerHTML = html; $('modal').hidden = false; }
  function closeModal() { $('modal').hidden = true; $('modalBody').innerHTML = ''; }
  $('modalClose').onclick = closeModal;
  $('modal').addEventListener('click', (e) => { if (e.target === $('modal')) closeModal(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });

  async function openFile(path) {
    try {
      const f = await api('/api/file?path=' + encodeURIComponent(path));
      openModal(`<div class="md">${md(f.text)}</div><div class="row"><span class="small" style="margin-right:auto">${esc(f.path)}</span><button class="btn" id="openInEditor">Open the file</button></div>`);
      $('openInEditor').onclick = () => post('/api/open', { path });
    } catch (e) { openModal(`<p>${esc(e.message)}</p>`); }
  }
  function openReel(n) {
    const r = S.state.reels.find((x) => x.n === n);
    if (!r) return;
    const cap = r.caption || '';
    openModal(`<h2>Reel ${r.n} · ${esc(cap.split('\n')[0] || r.slug)}</h2>
      ${r.videoUrl ? `<video src="${r.videoUrl}" controls autoplay playsinline></video>` : `<div class="empty">No video file for this reel on this machine (mp4s are not in git). The job ids in full-pipeline/runs let Claude re-download it.</div>`}
      ${cap ? `<div class="caption-box">${esc(cap)}</div>` : ''}
      <div class="kv"><span class="k">folder</span><span>${esc(r.folder)}</span><span class="k">cuts</span><span>${r.videos.length ? esc(r.videos.join(', ')) : 'none locally'}</span></div>
      <div class="row"><button class="btn" id="revealReel">Show in Finder</button>${cap ? `<button class="btn" id="copyCap">Copy caption</button>` : ''}</div>`);
    $('revealReel').onclick = () => post('/api/open', { path: r.folder });
    const cc = $('copyCap'); if (cc) cc.onclick = () => navigator.clipboard.writeText(cap).then(() => { cc.textContent = 'copied'; });
  }
  function openKeys() {
    const e = S.state.env, t = S.state.tools || {};
    const row = (k, ok, v) => `<span class="k">${k}</span><span class="${ok ? 'ok' : 'bad'}">${ok ? (v ? esc(v) : 'ok') : 'missing'}</span>`;
    openModal(`<h2>Keys and tools</h2>
      <p class="small">Keys go into <code>.env</code> in the project folder and never leave your machine. Claude Code itself runs on your Claude subscription; no Anthropic API key is needed.</p>
      <label>Apify API key <span class="small">(username checks, Pinterest references, music: cents per run) · <a href="https://console.apify.com/account/integrations" target="_blank" rel="noopener">get one</a></span></label>
      <input type="password" id="kApify" placeholder="${e.APIFY_API_KEY ? 'set (paste to replace)' : 'apify_api_…'}">
      <label>Gemini API key <span class="small">(optional: clip-by-clip motion analysis) · <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener">get one</a></span></label>
      <input type="password" id="kGemini" placeholder="${e.GEMINI_API_KEY ? 'set (paste to replace)' : 'AIza…'}">
      <div class="kv" style="margin-top:16px">
        ${row('Claude Code', t.claude && t.claude.ok, t.claude && t.claude.version)}
        ${row('Higgsfield CLI', t.higgsfield && t.higgsfield.ok, t.higgsfield && t.higgsfield.version)}
        ${row('Higgsfield MCP', (S.state.mcp || []).some((m) => /higgsfield/i.test(m.name) && m.status === 'connected'), 'connected')}
        ${row('ffmpeg', t.ffmpeg && t.ffmpeg.ok, t.ffmpeg && t.ffmpeg.version)}
        ${row('node', t.node && t.node.ok, t.node && t.node.version)}
        ${row('yt-dlp', t['yt-dlp'] && t['yt-dlp'].ok, t['yt-dlp'] && t['yt-dlp'].version)}
      </div>
      <p class="small">Missing something? Tell Claude in the chat: "install what is missing from the Keys box". The Higgsfield MCP connects with <code>claude mcp add --transport http higgsfield https://mcp.higgsfield.ai/mcp</code>, then <code>/mcp</code> inside Claude Code to sign in; the balance pill needs the CLI: <code>higgsfield auth login</code>.</p>
      <div class="row"><button class="btn" id="kCancel">Close</button><button class="btn hot" id="kSave">Save keys</button></div>`);
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
