/* ===== Interactive widgets for the manual API testing page =====
   Each widget mounts into <div class="w" data-w="name">. Sequence players mount into <div class="seq" data-seq="name">. */
const APIW = (() => {
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const store = { get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage unavailable */ } } };
  const cheer = el => { if (window.FUN && FUN.confetti) { const r = el.getBoundingClientRect(); FUN.confetti(r.left + r.width / 2, r.top + 10, 50); } };
  const REASON = { 200: 'OK', 201: 'Created', 202: 'Accepted', 204: 'No Content', 206: 'Partial Content', 301: 'Moved Permanently', 304: 'Not Modified', 400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden', 404: 'Not Found', 405: 'Method Not Allowed', 406: 'Not Acceptable', 409: 'Conflict', 412: 'Precondition Failed', 413: 'Content Too Large', 415: 'Unsupported Media Type', 422: 'Unprocessable Content', 428: 'Precondition Required', 429: 'Too Many Requests', 500: 'Internal Server Error', 502: 'Bad Gateway', 503: 'Service Unavailable', 504: 'Gateway Timeout' };
  const pill = code => `<span class="pill s${String(code)[0]}">${code} ${esc(REASON[code] || '')}</span>`;

  /* ---------- sequence player ---------- */
  function seq(host, def) {
    const L = def.lanes, W = Math.max(560, L.length * 150), colW = W / L.length, top = 58, rowH = 46;
    const x = id => (L.findIndex(l => l.id === id) + 0.5) * colW;
    const H = top + def.steps.length * rowH + 16;
    let i = -1, timer = null;
    host.innerHTML = `<div class="sq-top"><b>🎬 ${esc(def.title)}</b><span class="sq-count"></span>
      <button type="button" class="wb" data-a="prev" aria-label="Previous step">◀</button><button type="button" class="wb pri" data-a="play">▶ Play</button><button type="button" class="wb" data-a="next" aria-label="Next step">▶|</button><button type="button" class="wb" data-a="reset">↺</button></div>
      <div class="sq-scroll"><div class="sq-art"></div></div><div class="sq-say" aria-live="polite"></div>`;
    const art = host.querySelector('.sq-art'), say = host.querySelector('.sq-say'), cnt = host.querySelector('.sq-count'), pb = host.querySelector('[data-a="play"]');
    function draw() {
      let s = `<svg class="sq-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(def.title)}">`;
      L.forEach(l => {
        const cx = x(l.id);
        s += `<line class="ll" x1="${cx}" y1="${top - 6}" x2="${cx}" y2="${H - 6}"/>`;
        s += `<g class="lh"><rect x="${cx - colW / 2 + 8}" y="4" width="${colW - 16}" height="44" rx="12"/><text class="le" x="${cx}" y="24" text-anchor="middle">${esc(l.e)}</text><text x="${cx}" y="42" text-anchor="middle">${esc(l.label)}</text></g>`;
      });
      def.steps.forEach((st, k) => {
        const y = top + k * rowH + 28, cls = k === i ? 'cur' : k < i ? 'past' : 'fut';
        s += `<g class="st ${cls}${st.k ? ' k-' + st.k : ''}">`;
        if (st.f === st.t) {
          const cx = x(st.f), bw = Math.min(colW * 1.6, 12 + st.m.length * 6.4);
          s += `<rect class="self" x="${cx - bw / 2}" y="${y - 22}" width="${bw}" height="26" rx="8"/><text x="${cx}" y="${y - 5}" text-anchor="middle">${esc(st.m)}</text>`;
        } else {
          const x1 = x(st.f), x2 = x(st.t), dir = x2 > x1 ? 1 : -1, xm = (x1 + x2) / 2;
          s += `<line x1="${x1}" y1="${y}" x2="${x2 - dir * 8}" y2="${y}"/><path class="ah" d="M${x2} ${y} l${-dir * 10} -5 v10 z"/>`;
          s += `<text x="${xm}" y="${y - 7}" text-anchor="middle">${esc(st.m)}</text>`;
          if (k === i) s += `<circle class="dot" r="6" cx="${x1}" cy="${y}"><animate attributeName="cx" from="${x1}" to="${x2 - dir * 10}" dur="0.7s" fill="freeze"/></circle>`;
        }
        s += '</g>';
      });
      art.innerHTML = s + '</svg>';
      const st = def.steps[i];
      say.className = 'sq-say' + (st && st.k ? ' k-' + st.k : '');
      say.innerHTML = st ? `<b>Step ${i + 1}.</b> ${st.n}` : (def.intro || 'Press Play to start, or step through with the arrow buttons.');
      cnt.textContent = `${Math.max(i + 1, 0)} / ${def.steps.length}`;
    }
    function stop() { clearInterval(timer); timer = null; pb.textContent = i >= def.steps.length - 1 ? '↻ Replay' : '▶ Play'; }
    function go(n) { i = Math.max(-1, Math.min(def.steps.length - 1, n)); draw(); }
    host.addEventListener('click', e => {
      const a = e.target.closest('[data-a]');
      if (!a) return;
      const act = a.dataset.a;
      if (act === 'play') {
        if (timer) { stop(); return; }
        if (i >= def.steps.length - 1) go(-1);
        pb.textContent = '❚❚ Pause';
        go(i + 1);
        timer = setInterval(() => { if (i >= def.steps.length - 1) { stop(); return; } go(i + 1); if (i >= def.steps.length - 1) stop(); }, 2300);
      } else { stop(); if (act === 'prev') go(i - 1); if (act === 'next') go(i + 1); if (act === 'reset') go(-1); stop(); }
    });
    draw();
  }

  /* ---------- test pyramid ---------- */
  function pyramid(host) {
    const lv = [
      ['UI / end to end', 'few, slow, costly', 'Click through real screens in a browser. Catch layout and flow problems. Slow and brittle, so keep them few.', 'var(--g4)'],
      ['API / service', 'many, fast, stable', 'Call endpoints directly. Cover business rules, validation, auth and integration. This course lives here.', 'var(--g2)'],
      ['Unit', 'most, fastest', 'Developers test single functions and classes in milliseconds, with no network.', 'var(--g1)']
    ];
    const pts = [[[260, 10], [340, 110], [180, 110]], [[180, 116], [340, 116], [420, 216], [100, 216]], [[100, 222], [420, 222], [500, 322], [20, 322]]];
    const ty = [80, 170, 278];
    host.innerHTML = `<svg viewBox="0 0 520 330" role="img" aria-label="Test pyramid">${lv.map((l, k) => `<g class="lay" data-k="${k}" tabindex="0"><path d="M${pts[k].map(p => p.join(' ')).join(' L')} Z" fill="${l[3]}"/><text x="260" y="${ty[k]}" text-anchor="middle">${l[0]}</text><text class="s" x="260" y="${ty[k] + 17}" text-anchor="middle">${l[1]}</text></g>`).join('')}</svg><div class="pyr-note">Tap a layer to read about it.</div>`;
    const note = host.querySelector('.pyr-note'), lays = [...host.querySelectorAll('.lay')];
    const pick = k => { lays.forEach((g, j) => g.classList.toggle('dim', j !== k)); note.textContent = lv[k][2]; };
    lays.forEach((g, k) => { g.addEventListener('click', () => pick(k)); g.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(k); } }); });
  }

  /* ---------- url anatomy ---------- */
  function url(host) {
    host.innerHTML = `<div class="w-h"><b>🔍 URL anatomy</b><span class="w-sp"></span><button type="button" class="wb" data-u="https://api.shop.com:8443/v1/customers/42/orders?status=PAID&amp;page=2&amp;sort=-date#latest">Shop example</button><button type="button" class="wb" data-u="https://api.github.com/repos/octocat/hello-world/issues?state=open&amp;per_page=5">GitHub example</button></div>
      <input class="wi" type="text" spellcheck="false" aria-label="URL to split" value="https://api.shop.com:8443/v1/customers/42/orders?status=PAID&amp;page=2&amp;sort=-date#latest"><div class="ua-out"></div>`;
    const inp = host.querySelector('input'), out = host.querySelector('.ua-out');
    function render() {
      let u;
      try { u = new URL(inp.value.trim()); } catch (e) { out.innerHTML = '<div class="wmsg bad">This is not a complete URL yet. Start with https:// and a host name.</div>'; return; }
      const parts = [];
      parts.push([u.protocol + '//', 'scheme']);
      parts.push([u.hostname, 'host']);
      if (u.port) parts.push([':' + u.port, 'port']);
      u.pathname.split('/').filter(Boolean).forEach(seg => parts.push(['/' + seg, /^(\d+|[0-9a-f-]{36})$/i.test(seg) ? 'path param' : /^v\d+$/i.test(seg) ? 'version' : 'path']));
      if (u.search) parts.push([u.search, 'query']);
      if (u.hash) parts.push([u.hash, 'fragment']);
      const color = { scheme: 0, host: 1, port: 5, version: 3, path: 2, 'path param': 4, query: 5, fragment: 3 };
      let html = `<div class="ua">${parts.map(([t, k], n) => `<span class="p${color[k]}" style="--i:${n}">${esc(t)}<i>${k}</i></span>`).join('')}</div>`;
      const q = [...u.searchParams];
      if (q.length) html += `<table class="qtab"><tr><th>Query parameter</th><th>Value</th></tr>${q.map(([k, v]) => `<tr><td><code>${esc(k)}</code></td><td><code>${esc(v)}</code></td></tr>`).join('')}</table>`;
      const notes = [];
      notes.push(u.protocol === 'https:' ? '✅ HTTPS, so the request is encrypted.' : '⚠️ Not HTTPS. Tokens and data travel in plain text. Report it for any real API.');
      if (!u.port) notes.push(`The port is not written, so the default ${u.protocol === 'https:' ? '443' : '80'} is used.`);
      if (u.hash) notes.push('The fragment after # is never sent to the server. It stays in the browser.');
      if (q.some(([k]) => /key|token|password|secret/i.test(k))) notes.push('⚠️ A secret in the query string ends up in server logs, browser history and proxies. Send it in a header instead.');
      html += `<div class="wmsg">${notes.join('<br>')}</div>`;
      out.innerHTML = html;
    }
    inp.addEventListener('input', render);
    host.addEventListener('click', e => { const b = e.target.closest('[data-u]'); if (b) { inp.value = b.dataset.u; render(); } });
    render();
  }

  /* ---------- idempotency simulator ---------- */
  function idem(host) {
    const REQ = {
      POST: ['POST /orders', '{ "item": "pen" }', 'Creates a new order every time. Not idempotent.'],
      PUT: ['PUT /orders/5', '{ "item": "pen", "qty": 3 }', 'Replaces order 5 with the same content every time. Idempotent.'],
      PATCH: ['PATCH /orders/5', '{ "op": "add", "qty": 1 }', 'This PATCH adds 1 each time, so it is not idempotent. A PATCH that sets a value would be.'],
      DELETE: ['DELETE /orders/5', '', 'Removes order 5. The second call finds nothing, but the state is the same.'],
      GET: ['GET /orders/5', '', 'Only reads. Safe and idempotent.']
    };
    let m = 'POST', st, next, n;
    const reset = () => { st = { 5: { item: 'pen', qty: 1 } }; next = 6; n = 0; };
    reset();
    host.innerHTML = `<div class="w-h"><b>🔁 Same request, many times</b><span class="w-sp"></span>${Object.keys(REQ).map(k => `<button type="button" class="wb${k === m ? ' on' : ''}" data-m="${k}">${k}</button>`).join('')}</div>
      <div class="wgrid"><div><span class="wl">Request</span><pre class="wout idm-req"></pre><div class="wrow" style="margin-top:8px"><button type="button" class="wb pri" data-send>📨 Send</button><button type="button" class="wb" data-reset>↺ Reset server</button></div><div class="wmsg idm-note"></div></div>
      <div><span class="wl">Server state: orders table</span><div class="idm-state"></div><span class="wl">Responses</span><ul class="idm-log"></ul></div></div>`;
    const $ = s => host.querySelector(s);
    function paint(changed) {
      $('.idm-req').textContent = REQ[m][0] + (REQ[m][1] ? '\n\n' + REQ[m][1] : '');
      $('.idm-note').textContent = REQ[m][2];
      $('.idm-state').innerHTML = Object.keys(st).length ? Object.entries(st).map(([id, o]) => `<span class="idm-o${changed === +id ? (o._new ? ' new' : ' chg') : ''}">#${id} ${esc(o.item)} × ${o.qty}</span>`).join('') : '<small>No orders</small>';
      host.querySelectorAll('[data-m]').forEach(b => b.classList.toggle('on', b.dataset.m === m));
    }
    function send() {
      n++;
      let code, changed = null;
      Object.values(st).forEach(o => { delete o._new; });
      if (m === 'POST') { st[next] = { item: 'pen', qty: 1, _new: true }; changed = next; next++; code = 201; }
      if (m === 'PUT') { const had = !!st[5]; st[5] = { item: 'pen', qty: 3 }; changed = 5; code = had ? 200 : 201; }
      if (m === 'PATCH') { if (st[5]) { st[5].qty += 1; changed = 5; code = 200; } else code = 404; }
      if (m === 'DELETE') { if (st[5]) { delete st[5]; code = 204; } else code = 404; }
      if (m === 'GET') code = st[5] ? 200 : 404;
      const li = document.createElement('li');
      li.innerHTML = `<b>#${n}</b> ${esc(REQ[m][0])} → ${pill(code)}`;
      $('.idm-log').prepend(li);
      paint(changed);
    }
    host.addEventListener('click', e => {
      const b = e.target.closest('button');
      if (!b) return;
      if (b.dataset.m) { m = b.dataset.m; paint(); }
      if ('send' in b.dataset) send();
      if ('reset' in b.dataset) { reset(); $('.idm-log').innerHTML = ''; paint(); }
    });
    paint();
  }

  /* ---------- status code game ---------- */
  function status(host) {
    const Q = DATA.statusGame;
    let k = 0, score = 0, answered = false;
    function render() {
      if (k >= Q.length) {
        host.innerHTML = `<div class="w-h"><b>🚦 Pick the right status</b></div><div class="wmsg ok">You scored <b>${score} / ${Q.length}</b>. ${score === Q.length ? 'Perfect. You read status codes like a pro.' : 'Read the table above once more and try again.'}</div><div class="wrow" style="margin-top:8px"><button type="button" class="wb pri" data-again>↺ Play again</button></div>`;
        if (score === Q.length) cheer(host);
        return;
      }
      const q = Q[k];
      answered = false;
      host.innerHTML = `<div class="w-h"><b>🚦 Pick the right status</b><span class="w-sp"></span><small>Question ${k + 1} of ${Q.length} · Score ${score}</small></div>
        <div class="sg-q">${q.q}</div><div class="sg-opts">${q.o.map((c, j) => `<button type="button" class="sg-opt" data-j="${j}">${c} ${esc(REASON[c] || '')}</button>`).join('')}</div>
        <div class="sg-fb"></div><div class="sg-prog"><i style="width:${k / Q.length * 100}%"></i></div>`;
    }
    host.addEventListener('click', e => {
      if (e.target.closest('[data-again]')) { k = 0; score = 0; render(); return; }
      if (e.target.closest('[data-nx]')) { k++; render(); return; }
      const b = e.target.closest('.sg-opt');
      if (!b || answered) return;
      answered = true;
      const q = Q[k], j = +b.dataset.j, right = q.o[j] === q.a;
      if (right) score++;
      host.querySelectorAll('.sg-opt').forEach(x => { x.disabled = true; if (q.o[+x.dataset.j] === q.a) x.classList.add('ok'); });
      if (!right) b.classList.add('bad');
      host.querySelector('.sg-fb').innerHTML = `<div class="wmsg ${right ? 'ok' : 'bad'}">${right ? '✅ Right.' : `❌ The best answer is ${q.a}.`} ${q.why}</div><div class="wrow" style="margin-top:8px"><button type="button" class="wb pri" data-nx>Next ▶</button></div>`;
    });
    render();
  }

  /* ---------- JSON explorer ---------- */
  function evalPath(obj, path) {
    const p = path.trim();
    if (!p.startsWith('$')) throw new Error('A path starts with $, the root of the document.');
    const toks = [];
    const re = /\.([A-Za-z_$][\w$-]*)|\.\*|\[(\d+)\]|\[\*\]|\["([^"]+)"\]|\['([^']+)'\]/y;
    let i = 1;
    while (i < p.length) {
      re.lastIndex = i;
      const m = re.exec(p);
      if (!m) throw new Error(`I cannot read the path near "${p.slice(i)}". Use .name, [0], [*] or ["name"].`);
      toks.push(m[1] ?? m[3] ?? m[4] ?? (m[2] !== undefined ? +m[2] : '*'));
      i = re.lastIndex;
    }
    let cur = [{ v: obj, p: '$' }];
    for (const t of toks) {
      const nx = [];
      for (const c of cur) {
        if (c.v === null || typeof c.v !== 'object') continue;
        if (t === '*') Object.keys(c.v).forEach(key => nx.push({ v: c.v[key], p: Array.isArray(c.v) ? `${c.p}[${key}]` : `${c.p}.${key}` }));
        else if (Object.prototype.hasOwnProperty.call(c.v, t)) nx.push({ v: c.v[t], p: typeof t === 'number' ? `${c.p}[${t}]` : `${c.p}.${t}` });
      }
      cur = nx;
    }
    return cur;
  }
  const typeOf = v => v === null ? 'null' : Array.isArray(v) ? 'array' : typeof v;
  function json(host) {
    const sample = '{\n  "id": 1042,\n  "status": "PLACED",\n  "customer": { "name": "Asha", "vip": true },\n  "items": [\n    { "sku": "PEN-01", "qty": 2, "price": 1550 },\n    { "sku": "INK-07", "qty": 1, "price": "899" }\n  ],\n  "coupon": null\n}';
    host.innerHTML = `<div class="w-h"><b>🧾 JSON explorer</b><span class="w-sp"></span><button type="button" class="wb" data-p="$.items[0].price">$.items[0].price</button><button type="button" class="wb" data-p="$.items[*].sku">$.items[*].sku</button><button type="button" class="wb" data-p="$.items[*].price">$.items[*].price</button><button type="button" class="wb" data-p="$.coupon">$.coupon</button></div>
      <div class="wgrid"><div><span class="wl">Response body</span><textarea class="wt" spellcheck="false" aria-label="JSON to explore" style="min-height:230px">${esc(sample)}</textarea></div>
      <div><span class="wl">Path</span><input class="wi" type="text" value="$.items[*].price" spellcheck="false" aria-label="JSON path"><div class="js-out"></div></div></div>`;
    const ta = host.querySelector('textarea'), inp = host.querySelector('input'), out = host.querySelector('.js-out');
    function run() {
      let obj;
      try { obj = JSON.parse(ta.value); } catch (e) { out.innerHTML = `<div class="wmsg bad">❌ Invalid JSON. A server would answer 400 Bad Request.<br><code>${esc(e.message)}</code></div>`; return; }
      let res;
      try { res = evalPath(obj, inp.value); } catch (e) { out.innerHTML = `<div class="wmsg warn">${esc(e.message)}</div>`; return; }
      let html = '<div class="wmsg ok">✅ Valid JSON.</div>';
      if (!res.length) html += '<div class="wmsg warn">No value at this path. In a test this would mean a missing field.</div>';
      else html += `<table class="qtab"><tr><th>Path</th><th>Value</th><th>Type</th></tr>${res.map(r => `<tr><td><code>${esc(r.p)}</code></td><td><code>${esc(JSON.stringify(r.v))}</code></td><td>${typeOf(r.v)}</td></tr>`).join('')}</table>`;
      const types = [...new Set(res.map(r => typeOf(r.v)))];
      if (types.length > 1) html += `<div class="wmsg bad">🐞 Mixed types at the same path: ${types.join(' and ')}. A schema check would fail here, and typed clients may crash.</div>`;
      out.innerHTML = html;
    }
    ta.addEventListener('input', run);
    inp.addEventListener('input', run);
    host.addEventListener('click', e => { const b = e.target.closest('[data-p]'); if (b) { inp.value = b.dataset.p; run(); } });
    run();
  }

  /* ---------- JWT decoder ---------- */
  const b64u = o => btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/=+$/, '').replace(/\+/g, '-').replace(/\//g, '_');
  const unb64u = s => decodeURIComponent(escape(atob(s.replace(/-/g, '+').replace(/_/g, '/') + '==='.slice((s.length + 3) % 4))));
  function makeJwt(payload, alg = 'HS256', sig = 'q3zR9mX0e1Lk7VdP4sYt2cWnHuJbAoGf8iE5lTxQyZw') { return `${b64u({ alg, typ: 'JWT' })}.${b64u(payload)}.${alg === 'none' ? '' : sig}`; }
  function jwt(host) {
    const now = Math.floor(Date.now() / 1000);
    const samples = {
      good: makeJwt({ sub: '1', name: 'Alice', role: 'customer', scope: 'orders:read orders:write', iss: 'https://auth.shop.test', aud: 'shop-api', iat: now - 300, exp: now + 3300 }),
      expired: makeJwt({ sub: '1', name: 'Alice', role: 'customer', iat: now - 7500, exp: now - 3900 }),
      none: makeJwt({ sub: '1', name: 'Alice', role: 'admin', iat: now }, 'none'),
      leaky: makeJwt({ sub: '2', email: 'bob@example.com', password: 'bob123', role: 'customer', iat: now, exp: now + 86400 * 30 })
    };
    host.innerHTML = `<div class="w-h"><b>🔑 JWT decoder</b><span class="w-sp"></span><button type="button" class="wb" data-s="good">Good token</button><button type="button" class="wb" data-s="expired">Expired</button><button type="button" class="wb" data-s="none">alg none</button><button type="button" class="wb" data-s="leaky">Leaky payload</button></div>
      <textarea class="wt" spellcheck="false" aria-label="JWT to decode" style="min-height:80px">${samples.good}</textarea><div class="jwt-out"></div>`;
    const ta = host.querySelector('textarea'), out = host.querySelector('.jwt-out');
    const when = t => new Date(t * 1000).toISOString().replace('.000', '');
    function run() {
      const raw = ta.value.trim(), parts = raw.split('.');
      if (parts.length !== 3) { out.innerHTML = '<div class="wmsg bad">A JWT has exactly three parts separated by dots: header.payload.signature.</div>'; return; }
      let hd, pl;
      try { hd = JSON.parse(unb64u(parts[0])); pl = JSON.parse(unb64u(parts[1])); } catch (e) { out.innerHTML = '<div class="wmsg bad">The header or payload is not valid base64url encoded JSON.</div>'; return; }
      const f = [], t = Math.floor(Date.now() / 1000);
      if (String(hd.alg).toLowerCase() === 'none' || !parts[2]) f.push(['bad', '<b>alg is none or the signature is empty.</b> Anyone can forge this token. The API must reject it with 401.']);
      else f.push(['ok', `Signed with ${esc(hd.alg)}. Only the server can check the signature, so try changing one payload character and resending. Expect 401.`]);
      if (pl.exp === undefined) f.push(['warn', 'No exp claim, so the token never expires.']);
      else if (pl.exp < t) f.push(['bad', `Expired at ${when(pl.exp)}. The API must answer 401.`]);
      else f.push(['ok', `Valid until ${when(pl.exp)}, about ${Math.round((pl.exp - t) / 60)} minutes from now.`]);
      if (pl.exp && pl.iat && pl.exp - pl.iat > 86400) f.push(['warn', `Lifetime of ${Math.round((pl.exp - pl.iat) / 86400)} days. Long lived access tokens are risky if stolen.`]);
      const secret = Object.keys(pl).filter(k => /pass|secret|ssn|card|pin|otp/i.test(k));
      if (secret.length) f.push(['bad', `Sensitive data in the payload: <code>${esc(secret.join(', '))}</code>. The payload is readable by anyone.`]);
      if (pl.role) f.push(['warn', `Role claim <code>${esc(pl.role)}</code>. Test that changing it (without a valid signature) gives 401 and never extra access.`]);
      if (!pl.aud) f.push(['warn', 'No aud (audience) claim, so a token issued for another service might be accepted here.']);
      out.innerHTML = `<div class="jwt-raw"><span class="j0">${esc(parts[0])}</span>.<span class="j1">${esc(parts[1])}</span>.<span class="j2">${esc(parts[2])}</span></div>
        <div class="wgrid" style="margin-top:8px"><div><span class="wl">Header</span><pre class="wout">${esc(JSON.stringify(hd, null, 2))}</pre></div><div><span class="wl">Payload (claims)</span><pre class="wout">${esc(JSON.stringify(pl, null, 2))}</pre></div></div>
        <ul class="flags">${f.map(([k, m]) => `<li class="${k}">${m}</li>`).join('')}</ul>`;
    }
    ta.addEventListener('input', run);
    host.addEventListener('click', e => { const b = e.target.closest('[data-s]'); if (b) { ta.value = samples[b.dataset.s]; run(); } });
    run();
  }

  /* ---------- boundary values ---------- */
  function bva(host) {
    host.innerHTML = `<div class="w-h"><b>📏 Boundary and partition builder</b></div>
      <div class="wrow"><label class="wrow">Field <input class="wi" style="width:130px" data-f="name" value="quantity"></label><label class="wrow">Min <input class="wi" style="width:90px" type="number" data-f="min" value="1"></label><label class="wrow">Max <input class="wi" style="width:90px" type="number" data-f="max" value="10"></label></div>
      <div class="bva-out"></div>`;
    const out = host.querySelector('.bva-out'), get = f => host.querySelector(`[data-f="${f}"]`).value;
    function run() {
      const name = get('name').trim() || 'value', min = Math.round(+get('min')), max = Math.round(+get('max'));
      if (!Number.isFinite(min) || !Number.isFinite(max) || get('min') === '' || get('max') === '') { out.innerHTML = '<div class="wmsg warn">Enter whole numbers for Min and Max.</div>'; return; }
      if (min > max) { out.innerHTML = '<div class="wmsg bad">Min is larger than Max. That is a bug in the requirement itself, so raise it with the product owner.</div>'; return; }
      const mid = Math.floor((min + max) / 2);
      const pts = [...new Set([min - 1, min, min + 1, mid, max - 1, max, max + 1])].filter(v => v >= min - 1 && v <= max + 1).sort((a, b) => a - b);
      const ok = v => v >= min && v <= max, span = (max + 1) - (min - 1) || 1, pos = v => 4 + (v - (min - 1)) / span * 92;
      const rows = pts.map(v => [String(v), ok(v) ? 'Valid partition' : v < min ? 'Below the range' : 'Above the range', ok(v) ? '201 or 200' : '422 or 400', ok(v) ? 'ok' : 'bad']);
      const extra = [['-1', 'Negative', '422 or 400'], [`${min}.5`, 'Not a whole number', '422 or 400'], [`"${mid}"`, 'Number sent as a string', '400 (or 2xx only if the contract allows coercion)'], ['null', 'Null', '400 or 422'], ['(missing)', 'Field left out', '400 or 422'], ['99999999999', 'Huge number', '422 or 400, never 500']].filter(r => !(r[0] === '-1' && min <= -1));
      out.innerHTML = `<div class="bva-line"><div class="bva-axis"></div><div class="bva-ok" style="left:${pos(min)}%; width:${pos(max) - pos(min)}%"></div>${pts.map((v, n) => `<span class="bva-pt${ok(v) ? ' ok' : ''}" style="left:${pos(v)}%; --i:${n}"><b>${v}</b></span>`).join('')}</div>
        <div class="tw"><table class="jt"><tr><th>${esc(name)}</th><th>Partition</th><th>Expected status</th></tr>${rows.map(r => `<tr><td><code>${r[0]}</code></td><td class="${r[3] === 'ok' ? 'yes' : 'no'}">${r[1]}</td><td>${r[2]}</td></tr>`).join('')}${extra.map(r => `<tr><td><code>${esc(r[0])}</code></td><td class="no">${r[1]}</td><td>${r[2]}</td></tr>`).join('')}</table></div>
        <div class="wmsg">That is ${rows.length + extra.length} focused tests instead of trying every number from ${min - 1} to ${max + 1}. Boundary bugs come from <code>&lt;</code> written where <code>&lt;=</code> was meant, so the values at and next to each edge catch them.</div>`;
    }
    host.addEventListener('input', run);
    run();
  }

  /* ---------- token bucket ---------- */
  function bucket(host) {
    const CAP = 5, REFILL_MS = 2000;
    let tokens = CAP, last = Date.now(), n = 0;
    host.innerHTML = `<div class="w-h"><b>🪣 Token bucket rate limiter</b><span class="w-sp"></span><small>5 tokens, 1 new token every 2 seconds</small></div>
      <div class="tb-wrap"><div class="tb-bucket" aria-label="Tokens left">${'<div class="tb-tok"></div>'.repeat(CAP)}</div>
      <div class="tb-side"><div class="wrow"><button type="button" class="wb pri" data-one>📨 Send 1 request</button><button type="button" class="wb" data-burst>💥 Send 8 at once</button><button type="button" class="wb" data-clear>↺ Reset</button></div>
      <pre class="wout tb-h" style="margin-top:8px"></pre><ul class="tb-log"></ul></div></div>`;
    const toks = [...host.querySelectorAll('.tb-tok')], log = host.querySelector('.tb-log'), hd = host.querySelector('.tb-h');
    function refill() { const now = Date.now(), add = Math.floor((now - last) / REFILL_MS); if (add > 0) { tokens = Math.min(CAP, tokens + add); last = tokens === CAP ? now : last + add * REFILL_MS; } }
    function paint() { refill(); toks.forEach((t, i) => t.classList.toggle('full', i < tokens)); hd.textContent = `X-RateLimit-Limit: ${CAP}\nX-RateLimit-Remaining: ${tokens}`; }
    function one() {
      refill(); n++;
      let line;
      if (tokens > 0) { if (tokens === CAP) last = Date.now(); tokens--; line = `#${n} ${pill(200)}`; }
      else { const wait = Math.ceil((REFILL_MS - (Date.now() - last)) / 1000); line = `#${n} ${pill(429)} Retry-After: ${Math.max(1, wait)}`; }
      const li = document.createElement('li'); li.innerHTML = line; log.prepend(li);
      paint();
    }
    host.addEventListener('click', e => {
      if (e.target.closest('[data-one]')) one();
      if (e.target.closest('[data-burst]')) for (let k = 0; k < 8; k++) one();
      if (e.target.closest('[data-clear]')) { tokens = CAP; last = Date.now(); n = 0; log.innerHTML = ''; paint(); }
    });
    setInterval(() => { if (host.isConnected && tokens < CAP) paint(); }, 400);
    paint();
  }

  /* ---------- percentiles ---------- */
  function perc(host) {
    let seed = 7;
    const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
    host.innerHTML = `<div class="w-h"><b>📊 Average versus percentiles</b><span class="w-sp"></span><button type="button" class="wb" data-new>🎲 New sample</button></div>
      <label class="wrow" style="font-weight:800; font-size:14px">Slow requests: <input type="range" min="0" max="10" value="3" data-slow style="flex:1; min-width:140px; accent-color:var(--red)"> <span class="pc-v">3%</span></label>
      <div class="pc-stats"></div><div class="pc-art"></div><div class="wmsg pc-note"></div>`;
    const slow = host.querySelector('[data-slow]');
    function run() {
      const share = +slow.value / 100, N = 200, xs = [];
      for (let k = 0; k < N; k++) {
        const base = 80 + (rnd() + rnd() + rnd()) / 3 * 120;
        xs.push(Math.round(k < N * share ? 1200 + rnd() * 1800 : base));
      }
      const s = [...xs].sort((a, b) => a - b), pct = p => s[Math.max(0, Math.ceil(p / 100 * N) - 1)];
      const avg = Math.round(xs.reduce((a, b) => a + b, 0) / N);
      const st = [['Average', avg, 'avg'], ['p50', pct(50), ''], ['p90', pct(90), ''], ['p95', pct(95), ''], ['p99', pct(99), 'p99'], ['Max', s[N - 1], '']];
      host.querySelector('.pc-v').textContent = slow.value + '%';
      host.querySelector('.pc-stats').innerHTML = st.map(([l, v, c]) => `<div class="pc-s ${c}"><small>${l}</small><b>${v} ms</b></div>`).join('');
      const W = 600, H = 150, mx = Math.max(s[N - 1], 400), bw = W / N;
      const y = v => H - 10 - v / mx * (H - 24);
      let svg = `<svg class="pc-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="Sorted response times">`;
      s.forEach((v, k) => { svg += `<rect class="bar${v > 1000 ? ' slow' : ''}" x="${k * bw}" y="${y(v)}" width="${Math.max(1, bw - 0.6)}" height="${H - 10 - y(v)}"/>`; });
      [['avg', avg, 'average', 4], ['p95', pct(95), 'p95', 190], ['p99', pct(99), 'p99', 370]].forEach(([c, v, l, tx]) => { svg += `<line class="ln ${c}" x1="0" x2="${W}" y1="${y(v)}" y2="${y(v)}"/><text class="t-${c}" x="${tx}" y="${y(v) - 4}">${l} ${v} ms</text>`; });
      host.querySelector('.pc-art').innerHTML = svg + '</svg>';
      host.querySelector('.pc-note').innerHTML = `The ${N} requests are sorted from fastest to slowest. With ${slow.value}% slow requests the average is <b>${avg} ms</b>, which looks fine, but 1 in 100 users waits <b>${pct(99)} ms</b> or more. Write performance targets with percentiles, for example "p95 under 300 ms".`;
    }
    slow.addEventListener('input', run);
    host.addEventListener('click', e => { if (e.target.closest('[data-new]')) { seed = Math.floor(Math.random() * 1e6) + 1; run(); } });
    run();
  }

  /* ---------- contract diff ---------- */
  function shape(v, p, out) {
    out[p] = typeOf(v);
    if (Array.isArray(v)) { if (v.length) shape(v[0], p + '[]', out); }
    else if (v && typeof v === 'object') Object.keys(v).forEach(k => shape(v[k], p + '.' + k, out));
    return out;
  }
  function diff(host) {
    const oldObj = { id: 1042, status: 'PLACED', total: 1998, customer: { id: 1, name: 'Asha' }, items: [{ sku: 'PEN-01', qty: 2 }] };
    const presets = {
      add: { id: 1042, status: 'PLACED', total: 1998, currency: 'INR', customer: { id: 1, name: 'Asha' }, items: [{ sku: 'PEN-01', qty: 2 }] },
      rename: { id: 1042, state: 'PLACED', total: 1998, customer: { id: 1, name: 'Asha' }, items: [{ sku: 'PEN-01', qty: 2 }] },
      type: { id: '1042', status: 'PLACED', total: '19.98', customer: { id: 1, name: 'Asha' }, items: [{ sku: 'PEN-01', qty: 2 }] },
      nest: { id: 1042, status: 'PLACED', total: { amount: 1998, currency: 'INR' }, customer: { id: 1, name: 'Asha' }, items: [{ sku: 'PEN-01', qty: 2 }] }
    };
    host.innerHTML = `<div class="w-h"><b>🤝 Breaking change checker</b><span class="w-sp"></span><button type="button" class="wb" data-pr="add">Add a field</button><button type="button" class="wb" data-pr="rename">Rename a field</button><button type="button" class="wb" data-pr="type">Change a type</button><button type="button" class="wb" data-pr="nest">Wrap in an object</button></div>
      <div class="wgrid"><div><span class="wl">Version 1 response (what clients use today)</span><pre class="wout">${esc(JSON.stringify(oldObj, null, 2))}</pre></div>
      <div><span class="wl">Version 2 response (edit me)</span><textarea class="wt" spellcheck="false" aria-label="New response" style="min-height:200px">${esc(JSON.stringify(presets.add, null, 2))}</textarea></div></div><div class="df-out"></div>`;
    const ta = host.querySelector('textarea'), out = host.querySelector('.df-out');
    function run() {
      let nv;
      try { nv = JSON.parse(ta.value); } catch (e) { out.innerHTML = '<div class="wmsg bad">Version 2 is not valid JSON yet.</div>'; return; }
      const a = shape(oldObj, '$', {}), b = shape(nv, '$', {}), res = [];
      Object.keys(a).forEach(p => {
        if (!(p in b)) res.push(['brk', `<code>${esc(p)}</code> was removed or renamed. Clients that read it will break.`]);
        else if (a[p] !== b[p]) res.push(['brk', `<code>${esc(p)}</code> changed type from ${a[p]} to ${b[p]}. Typed clients will fail to parse it.`]);
      });
      Object.keys(b).forEach(p => { if (!(p in a)) res.push(['safe', `<code>${esc(p)}</code> was added. Safe for clients that ignore unknown fields.`]); });
      if (!res.length) res.push(['info', 'Same structure. Values may differ, but the contract is unchanged.']);
      const brk = res.filter(r => r[0] === 'brk').length;
      out.innerHTML = `<div class="wmsg ${brk ? 'bad' : 'ok'}">${brk ? `❌ ${brk} breaking change${brk > 1 ? 's' : ''}. Ship this as a new version, or keep the old field alongside the new one and deprecate it.` : '✅ Backward compatible. Existing clients keep working.'}</div><ul class="df-list">${res.map(([k, m]) => `<li class="${k}">${m}</li>`).join('')}</ul>`;
    }
    ta.addEventListener('input', run);
    host.addEventListener('click', e => { const b = e.target.closest('[data-pr]'); if (b) { ta.value = JSON.stringify(presets[b.dataset.pr], null, 2); run(); } });
    run();
  }

  /* ---------- endpoint checklist ---------- */
  function checklist(host) {
    const items = DATA.checklist, key = 'lh-api-checklist';
    let done = new Set(JSON.parse(store.get(key) || '[]'));
    host.innerHTML = `<div class="w-h"><b>☑️ Coverage for one endpoint</b><span class="w-sp"></span><small class="ck-n"></small><button type="button" class="wb" data-clear>↺ Clear</button></div><div class="ck-bar"><i></i></div><ul class="ck">${items.map((t, k) => `<li><label><input type="checkbox" data-k="${k}"> <span>${t}</span></label></li>`).join('')}</ul>`;
    function paint() {
      host.querySelectorAll('input[data-k]').forEach(c => { c.checked = done.has(+c.dataset.k); c.parentElement.classList.toggle('done', c.checked); });
      host.querySelector('.ck-n').textContent = `${done.size} of ${items.length} covered`;
      host.querySelector('.ck-bar i').style.width = done.size / items.length * 100 + '%';
    }
    host.addEventListener('change', e => {
      const c = e.target.closest('input[data-k]');
      if (!c) return;
      if (c.checked) done.add(+c.dataset.k); else done.delete(+c.dataset.k);
      store.set(key, JSON.stringify([...done]));
      paint();
      if (done.size === items.length) cheer(host);
    });
    host.addEventListener('click', e => { if (e.target.closest('[data-clear]')) { done = new Set(); store.set(key, '[]'); paint(); } });
    paint();
  }

  /* ---------- API versus web service ---------- */
  function venn(host) {
    const items = DATA.venn;
    host.innerHTML = `<div class="w-h"><b>🔵 API or web service</b><span class="w-sp"></span><small>Tap an example to place it</small></div>
      <div class="vn-wrap"><svg class="vn-svg" viewBox="0 0 420 220" role="img" aria-label="Web services are a subset of APIs"><ellipse class="vn-api" cx="210" cy="110" rx="200" ry="102"/><ellipse class="vn-ws" cx="270" cy="118" rx="118" ry="72"/><text x="60" y="58">All APIs</text><text x="250" y="70">Web services</text><circle class="vn-dot" r="9" cx="-40" cy="-40"/></svg>
      <div class="vn-chips">${items.map((it, k) => `<button type="button" class="wb" data-k="${k}">${esc(it.n)}</button>`).join('')}</div></div><div class="wmsg vn-say">Every web service sits inside the API circle. Pick an example.</div>`;
    const dot = host.querySelector('.vn-dot'), say = host.querySelector('.vn-say');
    host.addEventListener('click', e => {
      const b = e.target.closest('[data-k]');
      if (!b) return;
      const it = items[+b.dataset.k];
      host.querySelectorAll('[data-k]').forEach(x => x.classList.toggle('on', x === b));
      dot.setAttribute('cx', it.ws ? 270 + (Math.random() * 60 - 30) : 70 + Math.random() * 40);
      dot.setAttribute('cy', it.ws ? 130 + (Math.random() * 30 - 15) : 120 + Math.random() * 40);
      dot.classList.toggle('in', it.ws);
      say.innerHTML = `<b>${esc(it.n)}</b>: ${it.ws ? 'an API and also a web service.' : 'an API, but not a web service.'} ${it.why}`;
    });
  }

  /* ---------- SOAP and REST side by side ---------- */
  function soaprest(host) {
    const V = DATA.soapRest;
    let k = 'soap', c = 'ok';
    host.innerHTML = `<div class="w-h"><b>🔀 Same operation, two styles</b><span class="w-sp"></span><button type="button" class="wb" data-s="soap">🧼 SOAP</button><button type="button" class="wb" data-s="rest">🏛️ REST</button><span style="width:8px"></span><button type="button" class="wb" data-c="ok">Order exists</button><button type="button" class="wb" data-c="missing">Order 99 missing</button></div>
      <div class="wgrid"><div><span class="wl">Request</span><pre class="wout sr-req"></pre></div><div><span class="wl">Response</span><pre class="wout sr-res"></pre></div></div><div class="wmsg sr-note"></div>`;
    function paint() {
      const v = V[k][c];
      host.querySelector('.sr-req').textContent = v.req;
      host.querySelector('.sr-res').textContent = v.res;
      host.querySelector('.sr-note').innerHTML = v.note;
      host.querySelectorAll('[data-s]').forEach(b => b.classList.toggle('on', b.dataset.s === k));
      host.querySelectorAll('[data-c]').forEach(b => b.classList.toggle('on', b.dataset.c === c));
    }
    host.addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; if (b.dataset.s) k = b.dataset.s; if (b.dataset.c) c = b.dataset.c; paint(); });
    paint();
  }

  /* ---------- Richardson maturity model ---------- */
  function rmm(host) {
    const L = DATA.rmm;
    let k = 2;
    host.innerHTML = `<div class="w-h"><b>🪜 Richardson Maturity Model</b></div>
      <div class="rm-steps">${L.map((l, i) => `<button type="button" class="rm-step" data-k="${i}" style="--h:${40 + i * 22}px"><b>Level ${i}</b><span>${esc(l.name)}</span></button>`).join('')}</div>
      <div class="wgrid" style="margin-top:10px"><div><span class="wl">What the calls look like</span><pre class="wout rm-ex"></pre></div><div><span class="wl">What it means</span><div class="rm-txt"></div></div></div>`;
    function paint() {
      const l = L[k];
      host.querySelectorAll('.rm-step').forEach((b, i) => { b.classList.toggle('on', i === k); b.classList.toggle('below', i < k); });
      host.querySelector('.rm-ex').textContent = l.ex;
      host.querySelector('.rm-txt').innerHTML = `<p>${l.what}</p><div class="wmsg">🧪 <b>Testing note.</b> ${l.test}</div>`;
    }
    host.addEventListener('click', e => { const b = e.target.closest('.rm-step'); if (b) { k = +b.dataset.k; paint(); } });
    paint();
  }

  /* ---------- test type game ---------- */
  function ttype(host) {
    const Q = DATA.typeGame;
    let k = 0, score = 0, answered = false;
    function render() {
      if (k >= Q.length) {
        host.innerHTML = `<div class="w-h"><b>🧩 Pick the test type</b></div><div class="wmsg ok">You scored <b>${score} / ${Q.length}</b>. ${score === Q.length ? 'Perfect. You know which test answers which question.' : 'Look at the table above once more and try again.'}</div><div class="wrow" style="margin-top:8px"><button type="button" class="wb pri" data-again>↺ Play again</button></div>`;
        if (score === Q.length) cheer(host);
        return;
      }
      const q = Q[k];
      answered = false;
      host.innerHTML = `<div class="w-h"><b>🧩 Pick the test type</b><span class="w-sp"></span><small>Situation ${k + 1} of ${Q.length} · Score ${score}</small></div>
        <div class="sg-q">${esc(q.q)}</div><div class="sg-opts">${q.o.map((c, j) => `<button type="button" class="sg-opt" data-j="${j}">${esc(c)}</button>`).join('')}</div>
        <div class="sg-fb"></div><div class="sg-prog"><i style="width:${k / Q.length * 100}%"></i></div>`;
    }
    host.addEventListener('click', e => {
      if (e.target.closest('[data-again]')) { k = 0; score = 0; render(); return; }
      if (e.target.closest('[data-nx]')) { k++; render(); return; }
      const b = e.target.closest('.sg-opt');
      if (!b || answered) return;
      answered = true;
      const q = Q[k], j = +b.dataset.j, right = j === q.a;
      if (right) score++;
      host.querySelectorAll('.sg-opt').forEach(x => { x.disabled = true; if (+x.dataset.j === q.a) x.classList.add('ok'); });
      if (!right) b.classList.add('bad');
      host.querySelector('.sg-fb').innerHTML = `<div class="wmsg ${right ? 'ok' : 'bad'}">${right ? '✅ Right.' : `❌ The best answer is ${esc(q.o[q.a])}.`} ${esc(q.why)}</div><div class="wrow" style="margin-top:8px"><button type="button" class="wb pri" data-nx>Next ▶</button></div>`;
    });
    render();
  }

  /* ---------- date, money and text edge cases ---------- */
  function edge(host) {
    const ZONES = [['UTC', 'UTC'], ['Asia/Kolkata', 'Mumbai'], ['Asia/Tokyo', 'Tokyo'], ['Europe/London', 'London'], ['America/New_York', 'New York'], ['Australia/Sydney', 'Sydney']];
    host.innerHTML = `<div class="w-h"><b>🧪 Edge case labs</b><span class="w-sp"></span><button type="button" class="wb on" data-t="time">🕒 Time zones</button><button type="button" class="wb" data-t="money">💰 Money</button><button type="button" class="wb" data-t="text">🔤 Text</button></div>
      <div class="ed-pane" data-p="time"><label class="wl" for="edT">A moment in Mumbai time (IST, UTC+05:30)</label><input class="wi" id="edT" type="datetime-local" value="2026-03-31T23:30"><div class="ed-zones"></div><div class="wmsg ed-tnote"></div></div>
      <div class="ed-pane" data-p="money" hidden><div class="wgrid"><div><label class="wl" for="edP">Price in rupees</label><input class="wi" id="edP" value="19.99" inputmode="decimal"></div><div><label class="wl" for="edQ">Quantity</label><input class="wi" id="edQ" value="3" inputmode="numeric"></div><div><label class="wl" for="edD">Discount %</label><input class="wi" id="edD" value="15" inputmode="decimal"></div></div><div class="wgrid" style="margin-top:8px"><div><span class="wl">Floating point (risky)</span><pre class="wout ed-f"></pre></div><div><span class="wl">Integer paise (safe)</span><pre class="wout ed-i"></pre></div></div><div class="wmsg ed-mnote"></div></div>
      <div class="ed-pane" data-p="text" hidden><label class="wl" for="edS">Type a name or any text</label><input class="wi" id="edS" value="José 👨‍👩‍👧"><div class="pc-stats ed-len"></div><div class="wmsg ed-xnote"></div><div class="wrow" style="margin-top:8px"><button type="button" class="wb" data-s="O'Brien">O'Brien</button><button type="button" class="wb" data-s="Nguyễn">Nguyễn</button><button type="button" class="wb" data-s="प्रिया शर्मा">प्रिया शर्मा</button><button type="button" class="wb" data-s="محمد">محمد</button><button type="button" class="wb" data-s="🇮🇳👍🏽">🇮🇳👍🏽</button></div></div>`;
    const $q = s => host.querySelector(s);
    const ymd = (d, tz) => new Intl.DateTimeFormat('en-CA', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit' }).format(d);
    function time() {
      const v = $q('#edT').value;
      if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(v)) { $q('.ed-tnote').textContent = 'Pick a date and time.'; return; }
      const d = new Date(v.slice(0, 16) + ':00+05:30');
      const base = ymd(d, 'Asia/Kolkata');
      $q('.ed-zones').innerHTML = `<div class="ed-iso">ISO 8601 in UTC: <code>${d.toISOString().replace('.000', '')}</code></div>` + ZONES.map(([tz, n]) => {
        const day = ymd(d, tz), t = new Intl.DateTimeFormat('en-GB', { timeZone: tz, weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' }).format(d);
        return `<div class="ed-z${day !== base ? ' diff' : ''}"><b>${n}</b><span>${esc(t)}</span>${day !== base ? '<small>different date</small>' : ''}</div>`;
      }).join('');
      const n = ZONES.filter(([tz]) => ymd(d, tz) !== base).length;
      $q('.ed-tnote').innerHTML = n ? `The same moment falls on a <b>different calendar date</b> in ${n} of these cities. A report "by day", a coupon that "expires today" or a daily limit can give different answers depending on whose day the server uses.` : 'All these cities share the same date for this moment. Try a time close to midnight, such as 23:30 or 04:00.';
    }
    function money() {
      const p = parseFloat($q('#edP').value), qn = parseInt($q('#edQ').value, 10), dc = parseFloat($q('#edD').value) || 0;
      if (!isFinite(p) || !isFinite(qn)) { $q('.ed-mnote').textContent = 'Enter a price and a whole number quantity.'; return; }
      const f = p * qn * (1 - dc / 100);
      const paise = Math.round(p * 100), sub = paise * qn, off = Math.round(sub * dc / 100), tot = sub - off;
      const rs = x => (x / 100).toFixed(2);
      $q('.ed-f').textContent = `${p} × ${qn} × (1 − ${dc}/100)\n= ${f}\n\n0.1 + 0.2 = ${0.1 + 0.2}`;
      $q('.ed-i').textContent = `${paise} paise × ${qn} = ${sub}\ndiscount ${dc}% = round(${sub * dc / 100}) = ${off}\ntotal = ${tot} paise = ₹${rs(tot)}`;
      const exact = String(f) === rs(tot) || String(f) === String(Number(rs(tot)));
      $q('.ed-mnote').innerHTML = exact ? 'This time the floating point answer happens to look clean. Try 0.1 with quantity 3, or 19.99 with a 15% discount, and watch the digits.' : `The floating point result <code>${f}</code> is not a clean amount. If one service rounds it and another truncates it, the customer is charged one value and the invoice shows another. Send money as integer paise or as a decimal string such as <code>"${rs(tot)}"</code>, plus a currency code.`;
    }
    function text() {
      const s = $q('#edS').value;
      const units = s.length, cps = [...s].length, bytes = new TextEncoder().encode(s).length;
      let gr = cps;
      try { gr = [...new Intl.Segmenter(undefined, { granularity: 'grapheme' }).segment(s)].length; } catch (e) { /* older browser */ }
      const nfc = s.normalize('NFC') === s.normalize('NFD');
      $q('.ed-len').innerHTML = [['What a person sees', gr], ['Code points', cps], ['UTF-16 units (JS length)', units], ['UTF-8 bytes', bytes]].map(([l, v]) => `<div class="pc-s"><small>${l}</small><b>${v}</b></div>`).join('');
      $q('.ed-xnote').innerHTML = (gr !== bytes ? `The same text has a length of <b>${gr}</b>, <b>${cps}</b>, <b>${units}</b> or <b>${bytes}</b> depending on who counts. Ask which one a "max length" rule means, then test right at that limit with text like this.` : 'Plain English letters give the same length every way. Try an accent, Hindi text or an emoji.') + (nfc ? '' : ' This text also has two Unicode forms (NFC and NFD). Search and duplicate checks should treat them as equal.');
    }
    host.addEventListener('click', e => {
      const t = e.target.closest('[data-t]');
      if (t) { host.querySelectorAll('[data-t]').forEach(b => b.classList.toggle('on', b === t)); host.querySelectorAll('.ed-pane').forEach(p => { p.hidden = p.dataset.p !== t.dataset.t; }); }
      const s = e.target.closest('[data-s]');
      if (s) { $q('#edS').value = s.dataset.s; text(); }
    });
    $q('#edT').addEventListener('input', time);
    ['#edP', '#edQ', '#edD'].forEach(id => $q(id).addEventListener('input', money));
    $q('#edS').addEventListener('input', text);
    time(); money(); text();
  }

  /* ---------- race condition simulator ---------- */
  function race(host) {
    const MODES = {
      none: { label: 'No protection', steps: [
        ['A', 'GET /items/7', 'reads stock = 1', 1], ['B', 'GET /items/7', 'reads stock = 1', 1],
        ['A', 'POST /orders', 'stock 1 > 0, so save order. stock = 0', 0, 201], ['B', 'POST /orders', 'B still believes stock is 1, so save order. stock = −1', -1, 201]],
        end: 'bad', note: 'Both buyers got 201 Created and stock is now −1. The shop sold one item twice. This is the classic oversell bug.' },
      etag: { label: 'ETag and If-Match', steps: [
        ['A', 'GET /items/7', 'reads stock = 1, ETag "v7"', 1], ['B', 'GET /items/7', 'reads stock = 1, ETag "v7"', 1],
        ['A', 'PATCH If-Match: "v7"', 'version matches, stock = 0, ETag now "v8"', 0, 200], ['B', 'PATCH If-Match: "v7"', 'version is "v8" now, so refuse', 0, 412]],
        end: 'ok', note: 'Buyer B gets 412 Precondition Failed because the item changed after B read it. The app should read again and tell B the item is sold out.' },
      atomic: { label: 'Atomic update', steps: [
        ['A', 'POST /orders', 'UPDATE stock = stock − 1 WHERE stock > 0  (1 row changed)', 0, 201], ['B', 'POST /orders', 'same UPDATE, but stock is 0 (0 rows changed)', 0, 409],
        ['A', '', 'order saved for A', 0], ['B', '', 'no order for B, nothing half saved', 0]],
        end: 'ok', note: 'The check and the change happen in one database step, so only one request can win. Buyer B gets 409 Conflict with an "out of stock" message.' }
    };
    let mode = 'none', i = -1, timer = null;
    host.innerHTML = `<div class="w-h"><b>🏁 Two buyers, one last item</b><span class="w-sp"></span>${Object.entries(MODES).map(([k, m]) => `<button type="button" class="wb" data-m="${k}">${m.label}</button>`).join('')}</div>
      <div class="rc-board"><div class="rc-col"><b>🙋‍♀️ Buyer A (Asha)</b><ul class="rc-a"></ul></div><div class="rc-stock"><small>Stock of item 7</small><b class="rc-n">1</b></div><div class="rc-col"><b>🙋‍♂️ Buyer B (Ben)</b><ul class="rc-b"></ul></div></div>
      <div class="wrow" style="margin-top:8px"><button type="button" class="wb" data-a="prev" aria-label="Previous step">◀</button><button type="button" class="wb pri" data-a="play">▶ Play</button><button type="button" class="wb" data-a="next" aria-label="Next step">▶|</button><button type="button" class="wb" data-a="reset">↺</button><span class="rc-cnt"></span></div>
      <div class="wmsg rc-note" aria-live="polite"></div>`;
    const $q = s => host.querySelector(s), pb = $q('[data-a="play"]');
    function draw() {
      const m = MODES[mode];
      host.querySelectorAll('[data-m]').forEach(b => b.classList.toggle('on', b.dataset.m === mode));
      const li = who => m.steps.map((s, k) => s[0] !== who || k > i ? '' : `<li class="${k === i ? 'cur' : ''}">${s[1] ? `<code>${esc(s[1])}</code>` : ''}<span>${esc(s[2])}</span>${s[4] ? pill(s[4]) : ''}</li>`).join('');
      $q('.rc-a').innerHTML = li('A');
      $q('.rc-b').innerHTML = li('B');
      const stock = i < 0 ? 1 : m.steps[i][3];
      const n = $q('.rc-n');
      n.textContent = stock;
      n.className = 'rc-n' + (stock < 0 ? ' neg' : '');
      $q('.rc-cnt').textContent = `${i + 1} / ${m.steps.length}`;
      const nt = $q('.rc-note');
      nt.className = 'wmsg rc-note' + (i === m.steps.length - 1 ? ' ' + m.end : '');
      nt.innerHTML = i < 0 ? 'Both buyers press Buy at the same moment. Press Play, or step through one request at a time.' : i === m.steps.length - 1 ? m.note : `<b>Step ${i + 1}.</b> Buyer ${m.steps[i][0]}: ${esc(m.steps[i][2])}`;
    }
    function stop() { clearInterval(timer); timer = null; pb.textContent = '▶ Play'; }
    function go(n) { i = Math.max(-1, Math.min(MODES[mode].steps.length - 1, n)); draw(); }
    host.addEventListener('click', e => {
      const mb = e.target.closest('[data-m]');
      if (mb) { stop(); mode = mb.dataset.m; go(-1); return; }
      const a = e.target.closest('[data-a]');
      if (!a) return;
      const act = a.dataset.a, last = MODES[mode].steps.length - 1;
      if (act === 'play') {
        if (timer) { stop(); return; }
        if (i >= last) go(-1);
        pb.textContent = '❚❚ Pause';
        go(i + 1);
        timer = setInterval(() => { if (i >= last) { stop(); return; } go(i + 1); if (i >= last) stop(); }, 1800);
      } else { stop(); if (act === 'prev') go(i - 1); if (act === 'next') go(i + 1); if (act === 'reset') go(-1); }
    });
    draw();
  }

  /* ---------- fuzzing a quantity field ---------- */
  function fuzz(host) {
    // The pretend server: it should accept whole numbers 1 to 10 and reject everything else with 422
    function server(v) {
      if (v === null || v === '') return [500, 'NullPointerException at OrderService.java:88'];
      if (typeof v === 'string') { if (/^\d+$/.test(v)) v = Number(v); else return [422, 'quantity must be a number']; }
      if (typeof v !== 'number') return [400, 'quantity has the wrong type'];
      if (!Number.isFinite(v)) return [400, 'quantity is not a valid number'];
      if (v > 2147483647) return [500, 'integer overflow in stock service'];
      if (v === 0) return [422, 'quantity must be at least 1'];
      if (v > 10) return [422, 'quantity must be at most 10'];
      return [201, 'order created'];
    }
    const spec = v => Number.isInteger(v) && v >= 1 && v <= 10;
    function parse(raw) { try { return { v: JSON.parse(raw), ok: true }; } catch (e) { return { v: raw, ok: false }; } }
    function verdict(raw) {
      const p = parse(raw);
      if (!p.ok) return { st: 400, msg: 'invalid JSON body', kind: 'ok', why: 'Malformed JSON should give 400, and it does.' };
      const v = p.v, [st, msg] = server(v), good = spec(v);
      if (st >= 500) return { st, msg, kind: 'bug', why: 'A 5xx error means the server crashed on input it should have rejected.' };
      if (st < 300 && !good) return { st, msg, kind: 'bug', why: typeof v === 'string' ? 'The spec asks for a number, but a string was accepted. This may be fine if documented, so raise it as a question.' : 'The spec forbids this value, yet the order was created. Bad data is now in the system.' };
      if (st >= 400 && good) return { st, msg, kind: 'bug', why: 'A valid value was rejected.' };
      return { st, msg, kind: 'ok', why: good ? 'Valid input accepted.' : 'Invalid input rejected with a clear 4xx.' };
    }
    host.innerHTML = `<div class="w-h"><b>🐛 Fuzz the quantity field</b><span class="w-sp"></span><small>Spec: whole number from 1 to 10</small></div>
      <div class="wrow"><button type="button" class="wb pri" data-run>▶ Run the fuzz list</button><button type="button" class="wb" data-clear>↺ Clear</button></div>
      <div class="wrow" style="margin-top:8px"><label class="wl" for="fzIn" style="margin:0">Your own value (JSON)</label><input class="wi" id="fzIn" value="-1" style="flex:1; min-width:140px"><button type="button" class="wb" data-one>📨 Send</button></div>
      <pre class="wout fz-req">POST /v1/orders  {"productId": 7, "quantity": ?}</pre>
      <div class="tw fz-tw"><table class="jt fz-t"><thead><tr><th>quantity</th><th>Status</th><th>Server said</th><th>Verdict</th></tr></thead><tbody></tbody></table></div>
      <div class="wmsg fz-sum">Press Run to send each value in the list, one after another.</div>`;
    const $q = s => host.querySelector(s), body = $q('.fz-t tbody');
    let timer = null, bugs = new Set(), sent = 0;
    function add(raw) {
      const r = verdict(raw);
      sent++;
      if (r.kind === 'bug') bugs.add(raw);
      $q('.fz-req').textContent = `POST /v1/orders  {"productId": 7, "quantity": ${raw}}`;
      const tr = document.createElement('tr');
      tr.className = 'fz-row ' + r.kind;
      tr.innerHTML = `<td><code>${esc(raw)}</code></td><td>${pill(r.st)}</td><td>${esc(r.msg)}</td><td>${r.kind === 'bug' ? '🐞 Bug' : '✅ Fine'}<small>${esc(r.why)}</small></td>`;
      body.prepend(tr);
      $q('.fz-sum').className = 'wmsg fz-sum' + (bugs.size ? ' bad' : ' ok');
      $q('.fz-sum').innerHTML = `${sent} requests sent. <b>${bugs.size}</b> distinct input${bugs.size === 1 ? '' : 's'} revealed a problem${bugs.size ? ': ' + [...bugs].map(b => `<code>${esc(b)}</code>`).join(' ') : ''}.`;
    }
    host.addEventListener('click', e => {
      if (e.target.closest('[data-run]')) {
        clearInterval(timer);
        const list = DATA.fuzzList.slice();
        timer = setInterval(() => { if (!list.length || !host.isConnected) { clearInterval(timer); if (bugs.size >= 5) cheer(host); return; } add(list.shift()); }, 380);
      }
      if (e.target.closest('[data-one]')) { const v = $q('#fzIn').value.trim(); if (v) add(v); }
      if (e.target.closest('[data-clear]')) { clearInterval(timer); body.innerHTML = ''; bugs = new Set(); sent = 0; $q('.fz-sum').className = 'wmsg fz-sum'; $q('.fz-sum').textContent = 'Press Run to send each value in the list, one after another.'; }
    });
    $q('#fzIn').addEventListener('keydown', e => { if (e.key === 'Enter') { const v = e.target.value.trim(); if (v) add(v); } });
  }

  const W = { pyramid, url, idem, status, json, jwt, bva, bucket, perc, diff, checklist, venn, soaprest, rmm, ttype, edge, race, fuzz };
  function mountAll(root = document) {
    root.querySelectorAll('[data-w]').forEach(el => { if (el._m) return; el._m = true; const f = el.dataset.w === 'lab' ? LAB.mount : W[el.dataset.w]; if (f) f(el); });
    root.querySelectorAll('[data-seq]').forEach(el => { if (el._m) return; el._m = true; if (DATA.seqs[el.dataset.seq]) seq(el, DATA.seqs[el.dataset.seq]); });
  }
  return { mountAll, esc, pill, REASON, makeJwt, unb64u, cheer, store };
})();

/* ===== The ShopLite mock API that runs in the browser, with seven planted bugs ===== */
const LAB = (() => {
  const { esc, pill, REASON, makeJwt, unb64u, cheer, store } = APIW;
  const BASE = 'https://api.shoplite.test';
  const BUGS = DATA.labBugs, MISSIONS = DATA.labMissions;
  const KEY = 'lh-api-lab';
  let prog = { bugs: [], missions: [] };
  try { prog = Object.assign(prog, JSON.parse(store.get(KEY) || '{}')); } catch (e) { /* fresh start */ }
  let db, host, vars = {};

  function seed() {
    const names = ['Ballpoint pen', 'Gel pen', 'Notebook A5', 'Notebook A4', 'Sticky notes', 'Highlighter', 'Stapler', 'Paper clips', 'Ruler 30 cm', 'Eraser', 'Sharpener', 'Pencil HB', 'Marker', 'Glue stick', 'Scissors'];
    const products = [];
    for (let i = 1; i <= 60; i++) products.push({ id: i, name: `${names[(i - 1) % names.length]}${i > 15 ? ' ' + (Math.floor((i - 1) / 15) + 1) : ''}`, price: 500 + ((i * 737) % 9500), stock: (i * 7) % 23, version: 1 });
    db = {
      users: [
        { id: 1, username: 'alice', password: 'alice123', name: 'Alice', email: 'alice@example.com', role: 'customer' },
        { id: 2, username: 'bob', password: 'bob123', name: 'Bob', email: 'bob@example.com', role: 'customer' },
        { id: 3, username: 'admin', password: 'admin123', name: 'Admin', email: 'admin@example.com', role: 'admin' }
      ],
      products,
      orders: [{ id: 1001, userId: 2, productId: 3, quantity: 1, total: products[2].price, status: 'PLACED', note: 'Deliver to 14 MG Road, Bengaluru', createdAt: '2026-10-19T09:12:00Z' }],
      nextOrder: 1042, idem: {}, failed: {}
    };
  }
  seed();

  const hashOf = s => { let h = 0; for (const c of s) h = (h * 31 + c.charCodeAt(0)) >>> 0; return h.toString(16); };
  const problem = (status, title, detail, extra = {}) => ({ status, headers: { 'Content-Type': 'application/problem+json' }, body: Object.assign({ type: `${BASE}/problems/${title.toLowerCase().replace(/[^a-z]+/g, '-').replace(/^-|-$/g, '')}`, title, status, detail }, extra) });
  const ok = (status, body, headers = {}) => ({ status, headers: Object.assign(body === null ? {} : { 'Content-Type': 'application/json' }, headers), body });
  const publicUser = u => ({ id: u.id, username: u.username, name: u.name, email: u.email, role: u.role });

  function whoami(h) {
    const a = h.authorization;
    if (!a) return { missing: true };
    const m = /^Bearer\s+(\S+)$/i.exec(a);
    if (!m) return { err: problem(401, 'Invalid credentials', 'Use the format: Authorization: Bearer <token>') };
    const parts = m[1].split('.');
    try {
      const pl = JSON.parse(unb64u(parts[1]));
      if (parts[2] !== 'sl-' + hashOf(parts[0] + '.' + parts[1])) return { err: problem(401, 'Invalid credentials', 'The token signature is not valid.') };
      if (pl.exp * 1000 < Date.now()) return { err: problem(401, 'Invalid credentials', 'The token has expired. Log in again.') };
      const u = db.users.find(x => x.id === +pl.sub);
      if (!u) return { err: problem(401, 'Invalid credentials', 'Unknown user.') };
      return { user: u };
    } catch (e) { return { err: problem(401, 'Invalid credentials', 'The token could not be read.') }; }
  }
  function issue(u) {
    const now = Math.floor(Date.now() / 1000);
    const unsigned = makeJwt({ sub: String(u.id), name: u.name, iat: now, exp: now + 3600 }).split('.').slice(0, 2).join('.');
    return unsigned + '.sl-' + hashOf(unsigned);
  }
  function parseBody(req) {
    if (!req.body.trim()) return { val: undefined };
    const ct = req.headers['content-type'] || '';
    if (!/application\/json/i.test(ct)) return { err: problem(415, 'Unsupported media type', 'Send the body as JSON with Content-Type: application/json.') };
    try { return { val: JSON.parse(req.body) }; } catch (e) { return { err: problem(400, 'Malformed JSON', 'The request body is not valid JSON: ' + e.message) }; }
  }
  const isInt = v => typeof v === 'number' && Number.isInteger(v);

  function route(req, hit) {
    const { method, path, query, headers } = req;
    let m;
    if (method === 'OPTIONS') return ok(204, null, { Allow: 'GET, POST, PATCH, DELETE, OPTIONS' });
    if (!path.startsWith('/v1/')) return problem(404, 'Not found', 'Every endpoint starts with /v1. Open the docs on the left for the list.');

    if (path === '/v1/auth/login') {
      if (method !== 'POST') return Object.assign(problem(405, 'Method not allowed', 'Use POST to log in.'), { headers: { 'Content-Type': 'application/problem+json', Allow: 'POST' } });
      const b = parseBody(req); if (b.err) return b.err;
      const { username, password } = b.val || {};
      if (typeof username !== 'string' || typeof password !== 'string') return problem(400, 'Validation failed', 'username and password are required strings.');
      const u = db.users.find(x => x.username === username);
      if (!u || u.password !== password) {
        db.failed[username] = (db.failed[username] || 0) + 1;
        if (db.failed[username] > 5) hit('lockout');
        return problem(401, 'Invalid credentials', 'Invalid username or password.');
      }
      db.failed[username] = 0;
      return ok(200, { token: issue(u), tokenType: 'Bearer', expiresIn: 3600 });
    }

    if (path === '/v1/products') {
      if (method !== 'GET') return Object.assign(problem(405, 'Method not allowed', 'Products are read only here. Admins delete through /v1/admin/products/{id}.'), { headers: { 'Content-Type': 'application/problem+json', Allow: 'GET' } });
      const page = query.page === undefined ? 1 : Number(query.page), limit = query.limit === undefined ? 10 : Number(query.limit);
      if (!Number.isInteger(page) || page < 1) return problem(400, 'Validation failed', 'page must be a whole number of 1 or more.');
      if (!Number.isInteger(limit) || limit < 1) return problem(400, 'Validation failed', 'limit must be a whole number from 1 to 50.');
      if (limit > 50) hit('pagesize');
      let list = db.products.slice();
      if (query.q) list = list.filter(p => p.name.toLowerCase().includes(String(query.q).toLowerCase()));
      if (query.sort) {
        const desc = query.sort.startsWith('-'), f = query.sort.replace(/^-/, '');
        if (!['price', 'name', 'id'].includes(f)) return problem(400, 'Validation failed', 'sort must be one of id, name, price, with an optional minus for descending.');
        list.sort((a, b) => (a[f] > b[f] ? 1 : a[f] < b[f] ? -1 : 0) * (desc ? -1 : 1));
      }
      const total = list.length, data = list.slice((page - 1) * limit, page * limit).map(({ version, ...p }) => p);
      return ok(200, { data, page, limit, total, pages: Math.ceil(total / limit) });
    }

    if ((m = /^\/v1\/products\/([^/]+)$/.exec(path))) {
      if (method !== 'GET') return Object.assign(problem(405, 'Method not allowed', 'Only GET is allowed on a product.'), { headers: { 'Content-Type': 'application/problem+json', Allow: 'GET' } });
      if (!/^\d+$/.test(m[1])) return problem(400, 'Validation failed', 'The product id must be a whole number.');
      const p = db.products.find(x => x.id === +m[1]);
      if (!p) return problem(404, 'Not found', `There is no product ${m[1]}.`);
      const etag = `"p${p.id}-v${p.version}"`;
      if (headers['if-none-match'] === etag) return ok(304, null, { ETag: etag, 'Cache-Control': 'public, max-age=60' });
      const { version, ...pub } = p;
      return ok(200, pub, { ETag: etag, 'Cache-Control': 'public, max-age=60' });
    }

    if (path === '/v1/orders' || /^\/v1\/orders\//.test(path) || /^\/v1\/users\//.test(path) || /^\/v1\/admin\//.test(path)) {
      const who = whoami(headers);
      if (who.missing) {
        if (path === '/v1/orders' && method === 'POST') {
          hit('noauth500');
          return { status: 500, headers: { 'Content-Type': 'text/plain' }, body: "TypeError: Cannot read properties of undefined (reading 'id')\n    at createOrder (/srv/shoplite/src/orders/controller.js:48:31)\n    at Layer.handle (/srv/shoplite/node_modules/express/lib/router/layer.js:95:5)\n    at next (/srv/shoplite/node_modules/express/lib/router/route.js:149:13)" };
        }
        return Object.assign(problem(401, 'Authentication required', 'Send Authorization: Bearer <token>. Get a token from POST /v1/auth/login.'), { headers: { 'Content-Type': 'application/problem+json', 'WWW-Authenticate': 'Bearer' } });
      }
      if (who.err) return who.err;
      const me = who.user;

      if (path === '/v1/users/me') {
        if (method === 'GET') { hit('exposure'); const { password, ...rest } = me; return ok(200, Object.assign(publicUser(me), { passwordHash: '$2b$10$' + hashOf(password).padEnd(22, 'x') + 'Qm9iYnlUYWJsZXM', createdAt: '2026-01-04T10:00:00Z' })); }
        if (method === 'PATCH') {
          const b = parseBody(req); if (b.err) return b.err;
          const v = b.val;
          if (!v || typeof v !== 'object' || Array.isArray(v)) return problem(400, 'Validation failed', 'Send a JSON object with the fields to change.');
          if (v.name !== undefined && (typeof v.name !== 'string' || !v.name.trim() || v.name.length > 50)) return problem(422, 'Validation failed', 'name must be 1 to 50 characters.', { errors: [{ field: 'name', message: 'must be 1 to 50 characters' }] });
          if (v.email !== undefined && (typeof v.email !== 'string' || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v.email))) return problem(422, 'Validation failed', 'email is not a valid address.', { errors: [{ field: 'email', message: 'invalid format' }] });
          ['name', 'email'].forEach(k => { if (v[k] !== undefined) me[k] = v[k].trim ? v[k].trim() : v[k]; });
          if (v.role !== undefined && v.role !== me.role) { me.role = String(v.role); hit('massassign'); }
          return ok(200, publicUser(me));
        }
        return Object.assign(problem(405, 'Method not allowed', 'Use GET or PATCH.'), { headers: { 'Content-Type': 'application/problem+json', Allow: 'GET, PATCH' } });
      }

      if ((m = /^\/v1\/admin\/products\/([^/]+)$/.exec(path))) {
        if (method !== 'DELETE') return Object.assign(problem(405, 'Method not allowed', 'Use DELETE.'), { headers: { 'Content-Type': 'application/problem+json', Allow: 'DELETE' } });
        if (me.role !== 'admin') return problem(403, 'Forbidden', 'Only admins can delete products.');
        const ix = db.products.findIndex(x => x.id === +m[1]);
        if (ix < 0) return problem(404, 'Not found', `There is no product ${m[1]}.`);
        db.products.splice(ix, 1);
        return ok(204, null);
      }

      if (path === '/v1/orders') {
        if (method === 'GET') return ok(200, { data: db.orders.filter(o => o.userId === me.id && o.status !== 'CANCELLED') });
        if (method !== 'POST') return Object.assign(problem(405, 'Method not allowed', 'Use GET or POST.'), { headers: { 'Content-Type': 'application/problem+json', Allow: 'GET, POST' } });
        const b = parseBody(req); if (b.err) return b.err;
        const v = b.val;
        const key = headers['idempotency-key'];
        if (key && db.idem[me.id + ':' + key]) {
          const prev = db.idem[me.id + ':' + key];
          if (prev.body !== req.body.trim()) return problem(422, 'Idempotency key reused', 'This Idempotency-Key was already used with a different body.');
          return Object.assign({}, prev.res, { headers: Object.assign({}, prev.res.headers, { 'Idempotent-Replayed': 'true' }), replay: true });
        }
        if (!v || typeof v !== 'object' || Array.isArray(v)) return problem(400, 'Validation failed', 'Send a JSON object with productId and quantity.');
        const errs = [];
        if (v.productId === undefined) errs.push({ field: 'productId', message: 'is required' });
        else if (!isInt(v.productId)) errs.push({ field: 'productId', message: 'must be a whole number' });
        if (v.quantity === undefined) errs.push({ field: 'quantity', message: 'is required' });
        else if (!isInt(v.quantity)) errs.push({ field: 'quantity', message: 'must be a whole number' });
        else if (v.quantity === 0 || v.quantity > 10) errs.push({ field: 'quantity', message: 'must be between 1 and 10' });
        if (v.note !== undefined && (typeof v.note !== 'string' || v.note.length > 200)) errs.push({ field: 'note', message: 'must be text of at most 200 characters' });
        if (errs.length) return problem(422, 'Validation failed', 'One or more fields are invalid.', { errors: errs });
        const p = db.products.find(x => x.id === v.productId);
        if (!p) return problem(422, 'Validation failed', `Product ${v.productId} does not exist.`, { errors: [{ field: 'productId', message: 'unknown product' }] });
        if (v.quantity > p.stock) return problem(409, 'Out of stock', `Only ${p.stock} left of product ${p.id}.`);
        if (v.quantity < 0) hit('negative');
        const o = { id: db.nextOrder++, userId: me.id, productId: p.id, quantity: v.quantity, total: p.price * v.quantity, status: 'PLACED', note: v.note || '', createdAt: new Date().toISOString().replace(/\.\d+Z$/, 'Z') };
        db.orders.push(o);
        p.stock -= v.quantity; p.version++;
        const res = ok(201, o, { Location: `/v1/orders/${o.id}` });
        if (key) db.idem[me.id + ':' + key] = { body: req.body.trim(), res };
        return res;
      }

      if ((m = /^\/v1\/orders\/([^/]+)$/.exec(path))) {
        if (!/^\d+$/.test(m[1])) return problem(400, 'Validation failed', 'The order id must be a whole number.');
        const o = db.orders.find(x => x.id === +m[1] && x.status !== 'CANCELLED');
        if (method === 'GET') {
          if (!o) return problem(404, 'Not found', `There is no order ${m[1]}.`);
          if (o.userId !== me.id) hit('bola');
          return ok(200, o);
        }
        if (method === 'PATCH' || method === 'DELETE') {
          if (!o || o.userId !== me.id) return problem(404, 'Not found', `There is no order ${m[1]}.`);
          if (method === 'DELETE') { o.status = 'CANCELLED'; const p = db.products.find(x => x.id === o.productId); if (p) { p.stock += o.quantity; p.version++; } return ok(204, null); }
          const b = parseBody(req); if (b.err) return b.err;
          const v = b.val || {};
          if (typeof v.note !== 'string' || v.note.length > 200) return problem(422, 'Validation failed', 'Only note can be changed, as text of at most 200 characters.', { errors: [{ field: 'note', message: 'must be text of at most 200 characters' }] });
          o.note = v.note;
          return ok(200, o);
        }
        return Object.assign(problem(405, 'Method not allowed', 'Use GET, PATCH or DELETE.'), { headers: { 'Content-Type': 'application/problem+json', Allow: 'GET, PATCH, DELETE' } });
      }
    }
    return problem(404, 'Not found', `No endpoint matches ${method} ${path}.`);
  }

  function handle(req) {
    const found = [];
    const res = route(req, id => found.push(id));
    res.headers = Object.assign({}, res.headers, { 'X-Request-Id': Math.random().toString(16).slice(2, 10) });
    return { res, found };
  }

  /* ----- missions are judged from each request and its response ----- */
  function missions(req, res) {
    const done = [];
    const s = res.status, p = req.path;
    if (p === '/v1/auth/login' && s === 200) done.push('login');
    if (s === 401) done.push('401');
    if (/^\/v1\/products\/\d+$/.test(p) && s === 200) done.push('product');
    if (s === 304) done.push('304');
    if (p === '/v1/orders' && req.method === 'POST' && s === 201) done.push('create');
    if (s === 422) done.push('422');
    if (s === 404) done.push('404');
    if (res.replay) done.push('idem');
    if (s === 403) done.push('403');
    if (s === 415) done.push('415');
    if (p === '/v1/products' && s === 200 && res.body && res.body.page === 2) done.push('page2');
    if (/^\/v1\/orders\/\d+$/.test(p) && req.method === 'DELETE' && s === 204) done.push('cancel');
    return done;
  }

  /* ----- user interface ----- */
  const PRESETS = DATA.labPresets;
  function parseHeaders(t) {
    const h = {}, list = [];
    t.split('\n').forEach(line => { const i = line.indexOf(':'); if (i > 0) { const k = line.slice(0, i).trim(), v = line.slice(i + 1).trim(); if (k) { h[k.toLowerCase()] = v; list.push([k, v]); } } });
    return { h, list };
  }
  const subst = s => s.replace(/\{\{(\w+)\}\}/g, (all, k) => vars[k] !== undefined ? vars[k] : all);

  function mount(el) {
    host = el;
    host.innerHTML = `<div class="lab">
      <div class="lab-top"><b style="font-family:var(--font-head); font-size:17px">🏪 ShopLite API v1</b><span class="w-sp" style="flex:1"></span>
        <label class="wrow" style="font-size:13.5px; font-weight:800">Try an example <select class="ws" data-preset aria-label="Example requests"><option value="">Choose…</option>${PRESETS.map((p, i) => `<option value="${i}">${esc(p.label)}</option>`).join('')}</select></label>
        <button type="button" class="wb" data-resetdb title="Restore the starting data">↺ Reset data</button></div>
      <div class="lab-req"><select class="ws" data-method aria-label="Method">${['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'].map(m => `<option>${m}</option>`).join('')}</select>
        <input class="wi" data-url type="text" spellcheck="false" aria-label="URL" value="${BASE}/v1/products?page=1&amp;limit=5"><button type="button" class="wb pri" data-send>📨 Send</button></div>
      <div class="lab-cols"><div><span class="wl">Headers (one per line)</span><textarea class="wt" data-headers spellcheck="false" aria-label="Headers" style="min-height:96px">Accept: application/json</textarea>
        <span class="wl">Body</span><textarea class="wt" data-body spellcheck="false" aria-label="Body" style="min-height:96px"></textarea>
        <div class="lab-vars" data-vars></div>
        <div class="wrow" style="margin-top:6px"><button type="button" class="wb" data-curl>📋 Copy as curl</button></div></div>
      <div><span class="wl">Response</span><div class="lab-res" data-res><small>Send a request to see the response here.</small></div></div></div>
      <div class="lab-cols">
        <div><h4>📘 API docs</h4><div class="lab-docs">${DATA.labDocs.map(d => `<details><summary><span class="m m-${d.m}">${d.m}</span>${esc(d.p)}</summary><div>${d.d}</div></details>`).join('')}</div></div>
        <div><h4>🎯 Missions <small class="lab-mn"></small></h4><ul class="mis">${MISSIONS.map(m => `<li data-mid="${m.id}">${m.t}</li>`).join('')}</ul>
          <h4>🕘 History</h4><ul class="lab-hist" data-hist><li><small>No requests yet.</small></li></ul></div></div>
      <div><h4>🐞 Bug board <small class="lab-bn"></small></h4><div class="lab-board">${BUGS.map(b => `<div class="bug" data-bid="${b.id}"><b>Hidden bug</b><span>${b.hint}</span></div>`).join('')}</div>
        <div class="wrow" style="margin-top:8px"><button type="button" class="wb" data-clearprog>↺ Forget my progress</button></div></div>
    </div>`;
    const q = s => host.querySelector(s);
    const hist = [];
    function paintProgress() {
      host.querySelectorAll('[data-mid]').forEach(li => li.classList.toggle('done', prog.missions.includes(li.dataset.mid)));
      host.querySelectorAll('[data-bid]').forEach(d => {
        const b = BUGS.find(x => x.id === d.dataset.bid), f = prog.bugs.includes(b.id);
        d.classList.toggle('found', f);
        d.innerHTML = f ? `<b>${esc(b.title)}</b><span>${b.what}</span>` : `<b>Hidden bug</b><span>${b.hint}</span>`;
      });
      q('.lab-mn').textContent = `${prog.missions.length} of ${MISSIONS.length}`;
      q('.lab-bn').textContent = `${prog.bugs.length} of ${BUGS.length} found`;
    }
    function paintVars() { q('[data-vars]').innerHTML = Object.keys(vars).length ? 'Variables: ' + Object.entries(vars).map(([k, v]) => `<code>{{${esc(k)}}}</code> = <code>${esc(String(v).slice(0, 28))}${String(v).length > 28 ? '…' : ''}</code>`).join(' ') : 'Tip: after you log in, the token is saved as <code>{{token}}</code> and you can use it in headers.'; }
    function save() { store.set(KEY, JSON.stringify(prog)); }
    function build() {
      const method = q('[data-method]').value, raw = subst(q('[data-url]').value.trim());
      let u;
      try { u = new URL(raw, BASE); } catch (e) { return { err: 'That URL cannot be read.' }; }
      if (u.host !== 'api.shoplite.test') return { err: 'This playground only answers on https://api.shoplite.test.' };
      const { h, list } = parseHeaders(subst(q('[data-headers]').value));
      const query = {};
      u.searchParams.forEach((v, k) => { query[k] = v; });
      return { method, url: u.href, path: u.pathname.replace(/\/+$/, '') || '/', query, headers: h, hlist: list, body: subst(q('[data-body]').value) };
    }
    function send() {
      const req = build(), box = q('[data-res]');
      if (req.err) { box.innerHTML = `<div class="wmsg bad">${esc(req.err)}</div>`; return; }
      box.innerHTML = '<small>⏳ Sending…</small>';
      const ms = 40 + Math.round(Math.random() * 140);
      setTimeout(() => {
        const { res, found } = handle(req);
        if (req.path === '/v1/auth/login' && res.status === 200) { vars.token = res.body.token; paintVars(); }
        const body = res.body === null ? '' : typeof res.body === 'string' ? res.body : JSON.stringify(res.body, null, 2);
        box.innerHTML = `<div class="lab-meta">${pill(res.status)}<span>⏱️ ${ms} ms</span><span>📦 ${body.length} bytes</span></div>
          <span class="wl">Headers</span><pre class="wout">${esc(Object.entries(res.headers).map(([k, v]) => `${k}: ${v}`).join('\n'))}</pre>
          ${body ? `<span class="wl">Body</span><pre class="wout">${esc(body)}</pre>` : '<span class="wl">Body</span><small>(empty)</small>'}
          ${req.path === '/v1/auth/login' && res.status === 200 ? '<div class="wmsg ok">Token saved as <code>{{token}}</code>. Add the header <code>Authorization: Bearer {{token}}</code> to call protected endpoints.</div>' : ''}`;
        const newM = missions(req, res).filter(id => !prog.missions.includes(id)), newB = found.filter(id => !prog.bugs.includes(id));
        prog.missions.push(...newM); prog.bugs.push(...newB); save(); paintProgress();
        if (newB.length) { const b = BUGS.find(x => x.id === newB[0]); box.insertAdjacentHTML('beforeend', `<div class="wmsg bad">🐞 <b>Bug found: ${esc(b.title)}.</b> ${b.what}</div>`); cheer(q(`[data-bid="${newB[0]}"]`)); }
        else if (newM.length) cheer(box);
        hist.unshift({ m: req.method, u: q('[data-url]').value, h: q('[data-headers]').value, b: q('[data-body]').value, s: res.status });
        q('[data-hist]').innerHTML = hist.slice(0, 20).map((x, i) => `<li data-hi="${i}">${pill(x.s)} ${esc(x.m)} ${esc(x.u.replace(BASE, ''))}</li>`).join('');
      }, ms);
    }
    host.addEventListener('click', e => {
      const t = e.target;
      if (t.closest('[data-send]')) send();
      if (t.closest('[data-resetdb]')) { seed(); vars = {}; paintVars(); q('[data-res]').innerHTML = '<small>Data restored to the starting state. Log in again.</small>'; }
      if (t.closest('[data-clearprog]')) { prog = { bugs: [], missions: [] }; save(); paintProgress(); }
      if (t.closest('[data-curl]')) {
        const r = build();
        if (r.err) return;
        const lines = [`curl -i -X ${r.method} '${r.url}'`].concat(r.hlist.map(([k, v]) => `  -H '${k}: ${v}'`));
        if (r.body.trim()) lines.push(`  --data '${r.body.replace(/'/g, "'\\''").replace(/\n\s*/g, ' ')}'`);
        const txt = lines.join(' \\\n'), b = t.closest('[data-curl]'), done = () => { b.textContent = '✅ Copied'; setTimeout(() => { b.textContent = '📋 Copy as curl'; }, 1400); };
        if (navigator.clipboard) navigator.clipboard.writeText(txt).then(done, () => { q('[data-res]').innerHTML = `<pre class="wout">${esc(txt)}</pre>`; });
        else q('[data-res]').innerHTML = `<pre class="wout">${esc(txt)}</pre>`;
      }
      const hi = t.closest('[data-hi]');
      if (hi) { const x = hist[+hi.dataset.hi]; q('[data-method]').value = x.m; q('[data-url]').value = x.u; q('[data-headers]').value = x.h; q('[data-body]').value = x.b; }
    });
    q('[data-preset]').addEventListener('change', e => {
      const p = PRESETS[+e.target.value];
      if (!p) return;
      q('[data-method]').value = p.m; q('[data-url]').value = BASE + p.u; q('[data-headers]').value = p.h || 'Accept: application/json'; q('[data-body]').value = p.b || '';
      e.target.value = '';
    });
    q('[data-url]').addEventListener('keydown', e => { if (e.key === 'Enter') send(); });
    paintVars(); paintProgress();
  }
  return { mount, handle, seed };
})();
