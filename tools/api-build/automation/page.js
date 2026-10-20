/* ===== API Automation Testing page glue ===== */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage unavailable */ } }
  };
  const BASE = 'https://restful-booker.herokuapp.com';

  function highlight(root) {
    $$('pre[data-hl]', root).forEach(pre => {
      const code = pre.querySelector('code') || pre;
      const lang = pre.dataset.hl;
      if (lang) code.innerHTML = LEARN.hl(code.textContent, lang);
    });
  }
  async function copyText(text, btn) {
    try { await navigator.clipboard.writeText(text); }
    catch (e) {
      const ta = document.createElement('textarea');
      ta.value = text; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); } catch (er) { /* nothing more to try */ }
      ta.remove();
    }
    if (btn) { const o = btn.textContent; btn.textContent = 'Copied'; setTimeout(() => { btn.textContent = o; }, 1200); }
  }

  /* ---------- language and tool picker ---------- */
  const TOOLS = {
    java: [['rest-assured', 'Rest Assured'], ['playwright', 'Playwright'], ['native', 'Native Java (HttpClient)']],
    js: [['postman', 'Postman'], ['playwright', 'Playwright'], ['native', 'Native JS (fetch and node:test)']]
  };
  const LANG_NAME = { java: 'Java', py: 'Python', js: 'JavaScript' };
  const byId = Object.fromEntries(TRACKS.map(t => [t.id, t]));
  const langSel = $('#langSel'), toolSel = $('#toolSel'), toolBox = $('#toolBox'), msg = $('#pickMsg'), trackEl = $('#track');
  const trackId = (lang, tool) => lang === 'py' ? 'python' : lang && tool ? `${lang}-${tool}` : '';
  const hashOf = id => { const t = byId[id]; return t ? (t.lang === 'py' ? '#python' : `#${t.lang}/${t.tool}`) : ''; };
  let current = '';

  function fillTools(lang, tool) {
    const list = TOOLS[lang];
    toolBox.hidden = !list;
    if (!list) { toolSel.innerHTML = ''; return; }
    toolSel.innerHTML = `<option value="">Choose a ${LANG_NAME[lang]} tool</option>` + list.map(([v, l]) => `<option value="${v}">${esc(l)}</option>`).join('');
    toolSel.value = tool || '';
  }
  function sync(id) {
    const t = byId[id];
    if (!t) return;
    if (langSel.value !== t.lang) { langSel.value = t.lang; fillTools(t.lang, t.tool); }
    else if (TOOLS[t.lang]) toolSel.value = t.tool;
  }
  function clearTrack(text) {
    current = '';
    trackEl.innerHTML = '';
    msg.textContent = text;
  }

  langSel.addEventListener('change', () => {
    const lang = langSel.value;
    fillTools(lang, '');
    if (!lang) { clearTrack('Start by choosing the language you write tests in.'); setHash(''); return; }
    if (lang === 'py') { go('python', true); return; }
    clearTrack(`Great. Now pick the ${LANG_NAME[lang]} tool you want to learn.`);
    setHash('');
    toolBox.classList.remove('pop'); void toolBox.offsetWidth; toolBox.classList.add('pop');
    toolSel.focus();
  });
  toolSel.addEventListener('change', () => {
    const id = trackId(langSel.value, toolSel.value);
    if (id) go(id, true);
    else { clearTrack(`Pick the ${LANG_NAME[langSel.value]} tool you want to learn.`); setHash(''); }
  });

  function setHash(h) {
    if (location.hash === h) return;
    if (h) location.hash = h;
    else history.replaceState(null, '', location.pathname + location.search);
  }
  function go(id, scroll) {
    render(id);
    setHash(hashOf(id));
    if (scroll) setTimeout(() => trackEl.scrollIntoView({ behavior: FUN.reduce ? 'auto' : 'smooth', block: 'start' }), 40);
  }

  function render(id) {
    if (current === id) return;
    const t = byId[id], tpl = $('#tpl-' + id);
    if (!t || !tpl) return;
    current = id;
    store.set('api-auto-track', id);
    sync(id);
    trackEl.innerHTML = '';
    trackEl.appendChild(tpl.content.cloneNode(true));
    msg.textContent = `Showing ${t.title}. ${t.sections.length} lessons from basic to expert, then a quiz.`;
    highlight(trackEl);
    $('.quizslot', trackEl).innerHTML = LEARN.quizHtml(QUIZ[id], { lang: t.lang, title: `${t.title} quiz`, sub: 'Four levels from easy to expert. Every answer explains the reason behind it.' });
    highlight($('.quizslot', trackEl));
    wireTrack(trackEl, id);
    $('#sbGen').value = id;
    renderCode();
    FUN.observe(trackEl);
  }

  function wireTrack(root, id) {
    const secs = $$('.tsec', root), links = $$('.ttoc a', root);
    $$('.lvfilter button', root).forEach(b => b.addEventListener('click', () => {
      $$('.lvfilter button', root).forEach(x => x.classList.toggle('on', x === b));
      const lv = b.dataset.lv;
      secs.forEach(s => { s.hidden = !(lv === 'all' || s.dataset.level === lv || s.dataset.level === 'quiz'); });
      links.forEach(a => a.classList.toggle('dim', !(lv === 'all' || a.dataset.level === lv || !a.dataset.level)));
    }));
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver(es => es.forEach(e => {
        if (e.isIntersecting) links.forEach(a => a.classList.toggle('cur', a.getAttribute('href') === '#' + e.target.id));
      }), { rootMargin: '-20% 0px -70% 0px' });
      secs.forEach(s => io.observe(s));
    }
    $$('.flow', root).forEach(wireFlow);
  }

  function wireFlow(f) {
    const steps = $$('.fl-step', f);
    let timer = null;
    const light = i => steps.forEach((s, k) => { s.classList.toggle('lit', k === i); s.classList.toggle('done', k < i); });
    steps.forEach((s, i) => s.addEventListener('click', () => { clearInterval(timer); light(i); }));
    $('.fl-play', f).addEventListener('click', () => {
      clearInterval(timer);
      let i = 0;
      light(0);
      timer = setInterval(() => { i++; if (i >= steps.length) { clearInterval(timer); steps.forEach(s => { s.classList.remove('lit'); s.classList.add('done'); }); return; } light(i); }, FUN.reduce ? 600 : 1500);
    });
  }

  document.addEventListener('click', e => {
    const cp = e.target.closest('.cb-copy');
    if (cp) { copyText(cp.closest('.cb').querySelector('pre').textContent, cp); return; }
    const tb = e.target.closest('.trybtn');
    if (tb) { loadRequest(JSON.parse(tb.dataset.try)); $('#sandbox').scrollIntoView({ behavior: FUN.reduce ? 'auto' : 'smooth', block: 'start' }); }
  });

  function fromHash() {
    const h = decodeURIComponent(location.hash.slice(1));
    if (!h) return false;
    const m = h.match(/^([a-z-]+?)--([\w-]+)$/);
    if (m && byId[m[1]]) {
      render(m[1]);
      const el = document.getElementById(h);
      if (el) setTimeout(() => el.scrollIntoView({ block: 'start' }), 30);
      return true;
    }
    const [a, b] = h.split('/');
    const id = a === 'python' ? 'python' : trackId(a, b);
    if (byId[id]) { render(id); return true; }
    if (a === 'java' || a === 'js') { langSel.value = a; fillTools(a, ''); clearTrack(`Pick the ${LANG_NAME[a]} tool you want to learn.`); return true; }
    return false;
  }
  window.addEventListener('hashchange', () => {
    const h = location.hash.slice(1);
    if (h && document.getElementById(h) && !/^[a-z-]+--/.test(h)) return;
    if (fromHash() && /^(java|js|python)/.test(h)) trackEl.scrollIntoView({ block: 'start' });
  });

  /* ---------- the request animation ---------- */
  const STORIES = {
    get: [
      { k: 'arrange', t: 'Arrange: build GET /booking/1 and ask for JSON with the Accept header.', label: 'GET /booking/1' },
      { k: 'send', t: 'Act: send the request over HTTPS to the API.' },
      { k: 'server', t: 'The API looks up booking 1 and finds Sally Brown.', s: ['Find booking 1', 'Found it'] },
      { k: 'reply', t: 'The API replies with status 200 and a JSON body.', label: '200 OK + JSON' },
      { k: 'check', t: 'Assert the status code is 200.', label: 'status == 200', ok: true },
      { k: 'check', t: 'Assert the firstname field equals Sally.', label: 'firstname == "Sally"', ok: true },
      { k: 'check', t: 'Assert it answered in under 2 seconds. The test passes.', label: 'time < 2000 ms', ok: true }
    ],
    post: [
      { k: 'arrange', t: 'Arrange: build a booking as JSON and set Content-Type to application/json.', label: 'POST /booking' },
      { k: 'send', t: 'Act: send the request with the JSON body.' },
      { k: 'server', t: 'The API validates the fields and stores a new booking.', s: ['Validate body', 'Saved as id 42'] },
      { k: 'reply', t: 'It answers 200 with the new bookingid and the stored booking.', label: '200 {bookingid:42}' },
      { k: 'check', t: 'Assert the status code is 200.', label: 'status == 200', ok: true },
      { k: 'check', t: 'Assert the stored firstname equals what we sent.', label: 'booking.firstname == sent', ok: true },
      { k: 'check', t: 'Save bookingid so later steps can read, update and delete it.', label: 'save bookingid = 42', ok: true, info: true }
    ],
    forbidden: [
      { k: 'arrange', t: 'Arrange: build PUT /booking/1 with a new body, but no token. This is a negative test.', label: 'PUT /booking/1' },
      { k: 'send', t: 'Act: send it.' },
      { k: 'server', t: 'The API checks for a token cookie or Basic auth and finds neither.', s: ['Check auth', 'No token!'] },
      { k: 'reply', t: 'It refuses with 403 Forbidden.', label: '403 Forbidden', bad: true },
      { k: 'check', t: 'Assert the status is 403. The API said no, which is exactly what we wanted, so the test passes.', label: 'status == 403', ok: true },
      { k: 'check', t: 'Assert the booking did not change by reading it again.', label: 'firstname still "Sally"', ok: true }
    ],
    chain: [
      { k: 'arrange', t: 'Arrange: build POST /auth with admin and password123.', label: 'POST /auth' },
      { k: 'send', t: 'Act: send the login request.' },
      { k: 'server', t: 'The API checks the credentials and creates a token.', s: ['Check password', 'Token ready'] },
      { k: 'reply', t: 'It replies 200 with the token.', label: '200 {token}' },
      { k: 'check', t: 'Extract the token from the JSON and keep it in a variable.', label: 'token = "abc123"', ok: true, info: true },
      { k: 'arrange', t: 'Arrange: build PUT /booking/1 and add the cookie token=abc123.', label: 'PUT + Cookie' },
      { k: 'send', t: 'Act: send the update.' },
      { k: 'server', t: 'The token is valid, so the API replaces the booking.', s: ['Token OK', 'Updated'] },
      { k: 'reply', t: 'It replies 200 with the new booking.', label: '200 OK + JSON' },
      { k: 'check', t: 'Assert the new firstname came back. Chaining worked.', label: 'firstname == "Rakesh"', ok: true }
    ],
    missing: [
      { k: 'arrange', t: 'Arrange: ask for booking 999999, which was deleted earlier.', label: 'GET /booking/999999' },
      { k: 'send', t: 'Act: send it.' },
      { k: 'server', t: 'The API looks for the booking and cannot find it.', s: ['Find 999999', 'Not here'] },
      { k: 'reply', t: 'It replies 404 Not Found as plain text.', label: '404 Not Found', bad: true },
      { k: 'check', t: 'Assert the status is 404. Tests for missing data are as important as happy paths.', label: 'status == 404', ok: true },
      { k: 'check', t: 'Assert the body is not JSON, so code that calls .json() would crash. Good to know.', label: 'body == "Not Found"', ok: true }
    ]
  };
  const A = { req: $('#anReq'), res: $('#anRes'), reqT: $('#anReqT'), resT: $('#anResT'), steps: $('#animSteps'), checks: $('#animChecks') };
  const CX = 296, SX = 424, RY = 100, SY = 160;   // packets travel in the gap between the boxes, never over their text
  let story = 'get', pos = -1, animTimer = null;
  const place = (g, x, y) => { g.style.transform = `translate(${x}px, ${y}px)`; };
  function animReset() {
    clearInterval(animTimer); animTimer = null;
    pos = -1;
    const st = STORIES[story];
    A.steps.innerHTML = st.map(s => `<li>${esc(s.t)}</li>`).join('');
    A.checks.innerHTML = '';
    [A.req, A.res].forEach(g => { g.classList.remove('show'); g.style.transition = 'none'; });
    place(A.req, CX, RY); place(A.res, SX, SY);
    void A.req.getBoundingClientRect();
    [A.req, A.res].forEach(g => { g.style.transition = ''; });
    $$('.an-box').forEach(b => b.classList.remove('on'));
    $$('.an-s').forEach(t => t.classList.remove('on'));
    $('#anServer1').textContent = 'Waiting'; $('#anServer2').textContent = '';
    $('#animPlay').textContent = '▶ Play';
  }
  function clientLine(n) {
    $$('.an-client .an-s').forEach((t, i) => t.classList.toggle('on', i === n - 1));
    $('.an-client').classList.add('on'); $('.an-server').classList.remove('on');
  }
  function animStep() {
    const st = STORIES[story];
    if (pos >= st.length - 1) { clearInterval(animTimer); animTimer = null; $('#animPlay').textContent = '▶ Play again'; return false; }
    pos++;
    const s = st[pos];
    $$('li', A.steps).forEach((li, i) => { li.className = i < pos ? 'done' : i === pos ? 'cur' : ''; });
    if (s.k === 'arrange') {
      clientLine(1);
      A.res.classList.remove('show');
      A.req.style.transition = 'none'; place(A.req, CX, RY); void A.req.getBoundingClientRect(); A.req.style.transition = '';
      A.reqT.textContent = s.label; A.req.classList.add('show');
    } else if (s.k === 'send') {
      clientLine(2); place(A.req, SX, RY);
    } else if (s.k === 'server') {
      $('.an-server').classList.add('on'); $('.an-client').classList.remove('on');
      $('#anServer1').textContent = s.s[0]; $('#anServer2').textContent = s.s[1];
      $$('.an-server .an-s').forEach(t => t.classList.add('on'));
    } else if (s.k === 'reply') {
      A.req.classList.remove('show');
      A.res.style.transition = 'none'; place(A.res, SX, SY); void A.res.getBoundingClientRect(); A.res.style.transition = '';
      A.resT.textContent = s.label; A.res.classList.toggle('bad', !!s.bad); A.res.classList.add('show');
      requestAnimationFrame(() => place(A.res, CX, SY));
    } else if (s.k === 'check') {
      clientLine(3);
      A.checks.insertAdjacentHTML('beforeend', `<div class="chk ${s.info ? '' : s.ok ? 'ok' : 'bad'}">${s.info ? '📌' : s.ok ? '✅' : '❌'} ${esc(s.label)}</div>`);
      if (pos === st.length - 1 && !FUN.reduce) { const r = A.checks.lastElementChild.getBoundingClientRect(); FUN.confetti(r.left + r.width / 2, r.top, 30); }
    }
    return true;
  }
  $('#animSel').addEventListener('change', e => { story = e.target.value; animReset(); });
  $('#animStep').addEventListener('click', () => { clearInterval(animTimer); animTimer = null; $('#animPlay').textContent = '▶ Play'; animStep(); });
  $('#animReset').addEventListener('click', animReset);
  $('#animPlay').addEventListener('click', () => {
    if (animTimer) { clearInterval(animTimer); animTimer = null; $('#animPlay').textContent = '▶ Play'; return; }
    if (pos >= STORIES[story].length - 1) animReset();
    $('#animPlay').textContent = '⏸ Pause';
    animStep();
    animTimer = setInterval(animStep, FUN.reduce ? 900 : 1700);
  });
  animReset();

  /* ---------- the sandbox: a pretend Restful Booker in the browser ---------- */
  const DB = { next: 1, rows: new Map(), tokens: new Set() };
  const FIELDS = ['firstname', 'lastname', 'totalprice', 'depositpaid', 'bookingdates', 'additionalneeds'];
  [['Sally', 'Brown', 111, true, '2026-01-01', '2026-01-05', 'Breakfast'], ['Jim', 'Jones', 220, false, '2026-02-10', '2026-02-12', 'Late checkout'], ['Mary', 'Ericsson', 540, true, '2026-03-03', '2026-03-09', 'Lunch']]
    .forEach(([f, l, p, d, ci, co, n]) => DB.rows.set(DB.next++, { firstname: f, lastname: l, totalprice: p, depositpaid: d, bookingdates: { checkin: ci, checkout: co }, additionalneeds: n }));
  const pick = b => Object.fromEntries(FIELDS.filter(k => k in b).map(k => [k, b[k]]));
  const valid = b => b && typeof b === 'object' && typeof b.firstname === 'string' && typeof b.lastname === 'string' && typeof b.totalprice === 'number' && typeof b.depositpaid === 'boolean' && b.bookingdates && 'checkin' in b.bookingdates && 'checkout' in b.bookingdates;

  function api(method, path, headers, raw) {
    const text = (status, s) => ({ status, statusText: s, type: 'text/plain; charset=utf-8', body: s });
    const json = (status, body) => ({ status, statusText: status === 200 ? 'OK' : status === 201 ? 'Created' : '', type: 'application/json; charset=utf-8', body });
    let body = null, bad = false;
    if (raw && raw.trim()) { try { body = JSON.parse(raw); } catch (e) { bad = true; } }
    const u = new URL(path.startsWith('/') ? path : '/' + path, BASE);
    const parts = u.pathname.split('/').filter(Boolean);
    const id = parts[0] === 'booking' && /^\d+$/.test(parts[1] || '') && parts.length === 2 ? +parts[1] : null;
    const authed = () => {
      const c = (headers.Cookie || '').match(/(?:^|;\s*)token=([^;]+)/);
      if (c && DB.tokens.has(c[1])) return true;
      return headers.Authorization === 'Basic ' + btoa('admin:password123');
    };
    if (method === 'GET') {
      if (parts.join('/') === 'ping') return text(201, 'Created');
      if (parts.length === 1 && parts[0] === 'booking') {
        const q = Object.fromEntries(u.searchParams);
        const out = [...DB.rows].filter(([, b]) => (!q.firstname || b.firstname === q.firstname) && (!q.lastname || b.lastname === q.lastname)
          && (!q.checkin || b.bookingdates.checkin >= q.checkin) && (!q.checkout || b.bookingdates.checkout <= q.checkout)).map(([i]) => ({ bookingid: i }));
        return json(200, out);
      }
      if (id && DB.rows.has(id)) return json(200, DB.rows.get(id));
      return text(404, 'Not Found');
    }
    if (method === 'POST') {
      if (parts.join('/') === 'auth') {
        if (body && body.username === 'admin' && body.password === 'password123') { const t = Math.random().toString(16).slice(2, 17); DB.tokens.add(t); return json(200, { token: t }); }
        return json(200, { reason: 'Bad credentials' });
      }
      if (parts.length === 1 && parts[0] === 'booking') {
        if (bad || !valid(body)) return text(500, 'Internal Server Error');
        const b = pick(body), n = DB.next++;
        DB.rows.set(n, b);
        return json(200, { bookingid: n, booking: b });
      }
      return text(404, 'Not Found');
    }
    if (!id) return text(404, 'Not Found');
    if (!authed()) return text(403, 'Forbidden');
    if (!DB.rows.has(id)) return text(405, 'Method Not Allowed');
    if (method === 'DELETE') { DB.rows.delete(id); return text(201, 'Created'); }
    if (bad) return text(400, 'Bad Request');
    if (method === 'PUT') { if (!valid(body)) return text(400, 'Bad Request'); DB.rows.set(id, pick(body)); }
    else { if (!body || typeof body !== 'object') return text(400, 'Bad Request'); DB.rows.set(id, { ...DB.rows.get(id), ...pick(body) }); }
    return json(200, DB.rows.get(id));
  }

  const S = { method: $('#sbMethod'), path: $('#sbPath'), auth: $('#sbAuth'), token: $('#sbToken'), body: $('#sbBody') };
  const sample = { firstname: 'Rakesh', lastname: 'Panda', totalprice: 250, depositpaid: true, bookingdates: { checkin: '2026-11-01', checkout: '2026-11-04' }, additionalneeds: 'Breakfast' };
  const PRESETS = [
    ['Ping', { method: 'GET', path: '/ping' }],
    ['Get booking 1', { method: 'GET', path: '/booking/1' }],
    ['List all', { method: 'GET', path: '/booking' }],
    ['Filter by name', { method: 'GET', path: '/booking?firstname=Sally' }],
    ['Log in', { method: 'POST', path: '/auth', body: { username: 'admin', password: 'password123' } }],
    ['Create', { method: 'POST', path: '/booking', body: sample }],
    ['Update', { method: 'PUT', path: '/booking/1', auth: 'cookie', body: { ...sample, firstname: 'Sally', lastname: 'Brown' } }],
    ['Partial update', { method: 'PATCH', path: '/booking/1', auth: 'cookie', body: { additionalneeds: 'Dinner' } }],
    ['Delete', { method: 'DELETE', path: '/booking/2', auth: 'cookie' }]
  ];
  $('#sbPresets').innerHTML = PRESETS.map(([l], i) => `<button type="button" data-p="${i}">${esc(l)}</button>`).join('');
  $('#sbPresets').addEventListener('click', e => { const b = e.target.closest('[data-p]'); if (b) loadRequest(PRESETS[+b.dataset.p][1]); });

  function loadRequest(r) {
    S.method.value = r.method || 'GET';
    S.path.value = r.path || '/';
    S.auth.value = r.auth || 'none';
    S.body.value = r.body ? JSON.stringify(r.body, null, 2) : '';
    renderCode();
  }
  function headersNow() {
    const h = { Accept: 'application/json' };
    if (S.body.value.trim()) h['Content-Type'] = 'application/json';
    if (S.auth.value === 'cookie') h.Cookie = 'token=' + (S.token.value.trim() || 'missing');
    if (S.auth.value === 'basic') h.Authorization = 'Basic ' + btoa('admin:password123');
    return h;
  }

  let last = null;
  const history_ = [];
  function send() {
    const method = S.method.value, path = S.path.value.trim() || '/';
    const headers = headersNow();
    const t0 = performance.now();
    const r = api(method, path, headers, ['GET', 'DELETE'].includes(method) ? '' : S.body.value);
    r.time = Math.round(40 + Math.random() * 140 + (performance.now() - t0));
    if (method === 'POST' && path === '/auth' && r.body && r.body.token) S.token.value = r.body.token;
    last = { method, path, auth: S.auth.value, res: r };
    history_.push(last);
    const ok = r.status < 400;
    const st = $('#sbStatus');
    st.className = 'sb-status ' + (ok ? 'ok' : 'bad');
    st.textContent = `${method} ${path}  →  ${r.status} ${r.statusText}  ·  ${r.time} ms`;
    const hdr = `HTTP/1.1 ${r.status} ${r.statusText}\nContent-Type: ${r.type}\nX-Powered-By: Express\n\n`;
    $('#sbOut').textContent = hdr + (typeof r.body === 'string' ? r.body : JSON.stringify(r.body, null, 2));
    if (method === 'POST' && path === '/auth' && r.body.token && S.auth.value === 'none') S.auth.value = 'cookie';
    if (!S.checks.children.length) defaultChecks();
    challenges();
    renderCode();
  }
  $('#sbSend').addEventListener('click', send);
  S.path.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });
  [S.method, S.path, S.auth, S.body].forEach(el => el.addEventListener('input', renderCode));

  /* checks */
  S.checks = $('#sbChecks');
  const KINDS = [['status', 'Status code is'], ['json', 'JSON field equals'], ['has', 'JSON has field'], ['header', 'Header contains'], ['text', 'Body contains'], ['time', 'Time below (ms)']];
  function addCheck(kind = 'status', a = '', b = '') {
    const row = document.createElement('div');
    row.className = 'sbc';
    row.innerHTML = `<select class="kind" aria-label="Check type">${KINDS.map(([v, l]) => `<option value="${v}">${l}</option>`).join('')}</select>
      <input class="a" spellcheck="false"><input class="b" spellcheck="false"><span class="res" aria-live="polite"></span><button type="button" class="del" title="Remove this check" aria-label="Remove this check">✕</button>`;
    S.checks.appendChild(row);
    const k = $('.kind', row);
    k.value = kind; $('.a', row).value = a; $('.b', row).value = b;
    const paint = () => {
      const v = k.value, A_ = $('.a', row), B_ = $('.b', row);
      A_.style.visibility = ['json', 'has', 'header'].includes(v) ? '' : 'hidden';   // keep the grid cell so columns line up
      B_.style.visibility = v === 'has' ? 'hidden' : '';
      A_.placeholder = v === 'header' ? 'Header name' : 'Path, like booking.firstname or [0].bookingid';
      B_.placeholder = { status: '200', json: 'Expected value', header: 'Text it contains', text: 'Text it contains', time: '2000' }[v] || '';
    };
    k.addEventListener('change', () => { paint(); renderCode(); });
    row.addEventListener('input', renderCode);
    $('.del', row).addEventListener('click', () => { row.remove(); renderCode(); });
    paint();
  }
  function defaultChecks() {
    addCheck('status', '', last ? String(last.res.status) : '200');
    if (last && last.res.body && typeof last.res.body === 'object' && !Array.isArray(last.res.body)) {
      const k = Object.keys(last.res.body)[0];
      if (k && typeof last.res.body[k] !== 'object') addCheck('json', k, String(last.res.body[k]));
    }
    addCheck('time', '', '2000');
  }
  $('#sbAdd').addEventListener('click', () => { addCheck('json', '', ''); renderCode(); });
  const readChecks = () => $$('.sbc', S.checks).map(r => ({ kind: $('.kind', r).value, a: $('.a', r).value.trim(), b: $('.b', r).value.trim(), row: r }));

  function getPath(obj, path) {
    const keys = path.replace(/\[(\d+)\]/g, '.$1').split('.').filter(Boolean);
    let v = obj;
    for (const k of keys) { if (v == null || typeof v !== 'object' || !(k in v)) return undefined; v = v[k]; }
    return v;
  }
  const parseVal = s => { try { return JSON.parse(s); } catch (e) { return s; } };
  function evalCheck(c, r) {
    const body = r.body;
    switch (c.kind) {
      case 'status': return r.status === +c.b;
      case 'json': { const v = getPath(body, c.a); return v !== undefined && (JSON.stringify(v) === JSON.stringify(parseVal(c.b)) || String(v) === c.b); }
      case 'has': return getPath(body, c.a) !== undefined;
      case 'header': { const h = { 'content-type': r.type, 'x-powered-by': 'Express' }[c.a.toLowerCase()]; return !!h && h.includes(c.b); }
      case 'text': return (typeof body === 'string' ? body : JSON.stringify(body)).includes(c.b);
      case 'time': return r.time < +c.b;
    }
    return false;
  }
  let passedJsonCheck = false;
  $('#sbRun').addEventListener('click', () => {
    const cs = readChecks();
    if (!last) { $('#sbSum').textContent = 'Send a request first.'; return; }
    let ok = 0;
    cs.forEach(c => { const p = evalCheck(c, last.res); ok += p; $('.res', c.row).textContent = p ? '✅' : '❌'; if (p && c.kind === 'json') passedJsonCheck = true; });
    $('#sbSum').textContent = cs.length ? `${ok} of ${cs.length} checks passed` : 'Add a check first.';
    if (cs.length && ok === cs.length) { const r = $('#sbRun').getBoundingClientRect(); FUN.confetti(r.left + r.width / 2, r.top, 40); }
    challenges();
  });

  /* challenges */
  const CH = [
    ['Read booking 1 and get a 200.', h => h.some(x => x.method === 'GET' && /^\/booking\/1$/.test(x.path) && x.res.status === 200)],
    ['Run a JSON field check that passes, for example firstname equals Sally.', () => passedJsonCheck],
    ['Create a new booking with POST /booking.', h => h.some(x => x.method === 'POST' && x.path === '/booking' && x.res.status === 200)],
    ['Try to update a booking with no auth and see 403 Forbidden.', h => h.some(x => ['PUT', 'PATCH', 'DELETE'].includes(x.method) && x.res.status === 403)],
    ['Log in with POST /auth and get a token.', h => h.some(x => x.path === '/auth' && x.res.body && x.res.body.token)],
    ['Update a booking using the token cookie.', h => h.some(x => ['PUT', 'PATCH'].includes(x.method) && x.auth === 'cookie' && x.res.status === 200)],
    ['Delete a booking, then GET it again and see 404.', h => h.some((x, i) => x.method === 'DELETE' && x.res.status === 201 && h.slice(i + 1).some(y => y.method === 'GET' && y.path === x.path && y.res.status === 404))]
  ];
  const doneSet = new Set((store.get('api-auto-ch') || '').split(',').filter(Boolean).map(Number));
  function challenges() {
    let fresh = false;
    CH.forEach(([, f], i) => { if (!doneSet.has(i) && f(history_)) { doneSet.add(i); fresh = true; } });
    $('#sbChallenges').innerHTML = CH.map(([t], i) => `<li class="${doneSet.has(i) ? 'done' : ''}">${esc(t)}</li>`).join('') + `<p class="small">${doneSet.size} of ${CH.length} done.</p>`;
    store.set('api-auto-ch', [...doneSet].join(','));
    if (fresh && doneSet.size === CH.length) FUN.confetti(undefined, undefined, 120);
  }
  challenges();

  /* request as code */
  const GEN_LANG = { 'java-rest-assured': 'java', 'java-playwright': 'java', 'java-native': 'java', python: 'py', 'js-postman': 'js', 'js-playwright': 'js', 'js-native': 'js' };
  $('#sbGen').innerHTML = TRACKS.map(t => `<option value="${t.id}">${esc(t.title)}</option>`).join('');
  $('#sbGen').addEventListener('change', renderCode);
  $('#sbCopy').addEventListener('click', e => copyText($('#sbCodeOut').textContent, e.target));

  const jstr = s => JSON.stringify(s);
  const pyLit = v => JSON.stringify(v, null, 4).replace(/\btrue\b/g, 'True').replace(/\bfalse\b/g, 'False').replace(/\bnull\b/g, 'None');
  const pyPath = p => p.replace(/\[(\d+)\]/g, '.$1').split('.').filter(Boolean).map(k => /^\d+$/.test(k) ? `[${k}]` : `[${jstr(k)}]`).join('');
  const jsPath = p => p.replace(/\[(\d+)\]/g, '.$1').split('.').filter(Boolean).map(k => /^\d+$/.test(k) ? `[${k}]` : /^[A-Za-z_$][\w$]*$/.test(k) ? `.${k}` : `[${jstr(k)}]`).join('');
  const ptr = p => '/' + p.replace(/\[(\d+)\]/g, '.$1').split('.').filter(Boolean).join('/');
  const indent = (s, n) => s.split('\n').map((l, i) => i ? ' '.repeat(n) + l : l).join('\n');

  function renderCode() {
    const id = $('#sbGen').value || 'python';
    let body = null;
    if (S.body.value.trim() && !['GET', 'DELETE'].includes(S.method.value)) { try { body = JSON.parse(S.body.value); } catch (e) { body = null; } }
    const r = { m: S.method.value, path: S.path.value.trim() || '/', auth: S.auth.value, body, checks: readChecks().filter(c => c.kind === 'status' ? c.b : c.kind === 'time' ? c.b : c.a || c.b) };
    if (!r.checks.length) r.checks = [{ kind: 'status', b: last ? String(last.res.status) : '200' }];
    const out = GEN[id](r);
    const pre = $('#sbCodeOut');
    pre.dataset.hl = GEN_LANG[id];
    pre.querySelector('code').textContent = out;
    highlight(pre.parentElement);
  }
  const lit = (v, q = '"') => /^-?\d+(\.\d+)?$/.test(v) || v === 'true' || v === 'false' ? v : q + v.replace(/\\/g, '\\\\').replace(new RegExp(q, 'g'), '\\' + q) + q;
  const GEN = {
    'java-rest-assured': r => {
      const L = ['given()', '    .baseUri("https://restful-booker.herokuapp.com")', '    .accept(ContentType.JSON)'];
      if (r.body) L.push('    .contentType(ContentType.JSON)');
      if (r.auth === 'cookie') L.push('    .cookie("token", token)');
      if (r.auth === 'basic') L.push('    .auth().preemptive().basic("admin", "password123")');
      if (r.body) L.push('    .body("""\n        ' + indent(JSON.stringify(r.body, null, 2), 8) + '\n        """)');
      L.push('.when()', `    .${r.m.toLowerCase()}(${jstr(r.path)})`, '.then()', '    .log().ifValidationFails()');
      r.checks.forEach(c => {
        if (c.kind === 'status') L.push(`    .statusCode(${+c.b})`);
        if (c.kind === 'json') L.push(`    .body(${jstr(c.a)}, equalTo(${lit(c.b)}))`);
        if (c.kind === 'has') L.push(`    .body(${jstr(c.a)}, notNullValue())`);
        if (c.kind === 'header') L.push(`    .header(${jstr(c.a)}, containsString(${jstr(c.b)}))`);
        if (c.kind === 'text') L.push(`    .body(containsString(${jstr(c.b)}))`);
        if (c.kind === 'time') L.push(`    .time(lessThan(${+c.b}L))`);
      });
      L[L.length - 1] += ';';
      return '// static imports: io.restassured.RestAssured.*, org.hamcrest.Matchers.*\n' + L.join('\n');
    },
    'java-playwright': r => {
      const opts = [];
      if (r.auth === 'cookie') opts.push('.setHeader("Cookie", "token=" + token)');
      if (r.auth === 'basic') opts.push('.setHeader("Authorization", "Basic " + Base64.getEncoder().encodeToString("admin:password123".getBytes()))');
      if (r.body) opts.push('.setHeader("Content-Type", "application/json")', '.setData("""\n            ' + indent(JSON.stringify(r.body, null, 2), 12) + '\n            """)');
      const call = `APIResponse res = request.${r.m === 'DELETE' ? 'delete' : r.m.toLowerCase()}(${jstr(r.path)}${opts.length ? ',\n    RequestOptions.create()\n        ' + opts.join('\n        ') : ''});`;
      const L = ['// request is an APIRequestContext with baseURL https://restful-booker.herokuapp.com', call];
      const needJson = r.checks.some(c => ['json', 'has'].includes(c.kind));
      if (needJson) L.push('JsonNode body = new ObjectMapper().readTree(res.body());');
      r.checks.forEach(c => {
        if (c.kind === 'status') L.push(`assertEquals(${+c.b}, res.status());`);
        if (c.kind === 'json') L.push(`assertEquals(${jstr(c.b)}, body.at(${jstr(ptr(c.a))}).asText());`);
        if (c.kind === 'has') L.push(`assertFalse(body.at(${jstr(ptr(c.a))}).isMissingNode());`);
        if (c.kind === 'header') L.push(`assertTrue(res.headers().get(${jstr(c.a.toLowerCase())}).contains(${jstr(c.b)}));`);
        if (c.kind === 'text') L.push(`assertTrue(res.text().contains(${jstr(c.b)}));`);
        if (c.kind === 'time') L.push(`// Playwright does not time API calls for you. Wrap the call with System.nanoTime() to check under ${+c.b} ms.`);
      });
      return L.join('\n');
    },
    'java-native': r => {
      const L = ['HttpRequest req = HttpRequest.newBuilder()', `    .uri(URI.create(BASE + ${jstr(r.path)}))`, '    .header("Accept", "application/json")'];
      if (r.body) L.push('    .header("Content-Type", "application/json")');
      if (r.auth === 'cookie') L.push('    .header("Cookie", "token=" + token)');
      if (r.auth === 'basic') L.push('    .header("Authorization", "Basic " + Base64.getEncoder().encodeToString("admin:password123".getBytes()))');
      const pub = r.body ? 'HttpRequest.BodyPublishers.ofString("""\n        ' + indent(JSON.stringify(r.body, null, 2), 8) + '\n        """)' : 'HttpRequest.BodyPublishers.noBody()';
      L.push(r.m === 'GET' ? '    .GET()' : r.m === 'DELETE' ? '    .DELETE()' : `    .method(${jstr(r.m)}, ${pub})`, '    .build();');
      L.push('long start = System.nanoTime();', 'HttpResponse<String> res = client.send(req, HttpResponse.BodyHandlers.ofString());', 'long ms = (System.nanoTime() - start) / 1_000_000;');
      if (r.checks.some(c => ['json', 'has'].includes(c.kind))) L.push('JsonNode body = new ObjectMapper().readTree(res.body());   // Jackson, the one helper most native suites add');
      r.checks.forEach(c => {
        if (c.kind === 'status') L.push(`assertEquals(${+c.b}, res.statusCode());`);
        if (c.kind === 'json') L.push(`assertEquals(${jstr(c.b)}, body.at(${jstr(ptr(c.a))}).asText());`);
        if (c.kind === 'has') L.push(`assertFalse(body.at(${jstr(ptr(c.a))}).isMissingNode());`);
        if (c.kind === 'header') L.push(`assertTrue(res.headers().firstValue(${jstr(c.a)}).orElse("").contains(${jstr(c.b)}));`);
        if (c.kind === 'text') L.push(`assertTrue(res.body().contains(${jstr(c.b)}));`);
        if (c.kind === 'time') L.push(`assertTrue(ms < ${+c.b}, "took " + ms + " ms");`);
      });
      return L.join('\n');
    },
    python: r => {
      const args = [`f"{BASE}${r.path}"`];
      if (r.body) args.push('json=' + indent(pyLit(r.body), 4));
      if (r.auth === 'cookie') args.push('cookies={"token": token}');
      if (r.auth === 'basic') args.push('auth=("admin", "password123")');
      args.push('timeout=10');
      const L = [`res = requests.${r.m.toLowerCase()}(\n    ${args.join(',\n    ')},\n)`];
      if (r.checks.some(c => ['json', 'has'].includes(c.kind))) L.push('body = res.json()');
      r.checks.forEach(c => {
        if (c.kind === 'status') L.push(`assert res.status_code == ${+c.b}`);
        if (c.kind === 'json') L.push(`assert body${pyPath(c.a)} == ${pyLit(parseVal(c.b))}`);
        if (c.kind === 'has') L.push(`assert ${jstr(c.a.split('.').pop())} in body${pyPath(c.a.split('.').slice(0, -1).join('.'))}`);
        if (c.kind === 'header') L.push(`assert ${jstr(c.b)} in res.headers[${jstr(c.a)}]`);
        if (c.kind === 'text') L.push(`assert ${jstr(c.b)} in res.text`);
        if (c.kind === 'time') L.push(`assert res.elapsed.total_seconds() * 1000 < ${+c.b}`);
      });
      return L.join('\n');
    },
    'js-postman': r => {
      const L = [`// Request: ${r.m} {{baseUrl}}${r.path}`];
      if (r.auth === 'cookie') L.push('// Header:  Cookie: token={{token}}');
      if (r.auth === 'basic') L.push('// Auth tab: Basic Auth, admin / password123');
      if (r.body) L.push('// Body tab: raw, JSON');
      L.push('// Paste the lines below into the Scripts > Post-response tab', '');
      if (r.checks.some(c => ['json', 'has'].includes(c.kind))) L.push('const body = pm.response.json();');
      r.checks.forEach(c => {
        if (c.kind === 'status') L.push(`pm.test("Status is ${+c.b}", () => pm.response.to.have.status(${+c.b}));`);
        if (c.kind === 'json') L.push(`pm.test("${c.a} is ${c.b.replace(/"/g, '')}", () => pm.expect(body${jsPath(c.a)}).to.eql(${jstr(parseVal(c.b))}));`);
        if (c.kind === 'has') L.push(`pm.test("${c.a} exists", () => pm.expect(body${jsPath(c.a)}).to.not.be.undefined);`);
        if (c.kind === 'header') L.push(`pm.test("${c.a} header", () => pm.expect(pm.response.headers.get(${jstr(c.a)})).to.include(${jstr(c.b)}));`);
        if (c.kind === 'text') L.push(`pm.test("Body mentions ${c.b.replace(/"/g, '')}", () => pm.expect(pm.response.text()).to.include(${jstr(c.b)}));`);
        if (c.kind === 'time') L.push(`pm.test("Under ${+c.b} ms", () => pm.expect(pm.response.responseTime).to.be.below(${+c.b}));`);
      });
      if (r.path === '/auth') L.push('pm.collectionVariables.set("token", pm.response.json().token);');
      return L.join('\n');
    },
    'js-playwright': r => {
      const opts = [];
      if (r.auth === 'cookie') opts.push('headers: { Cookie: `token=${token}` }');
      if (r.auth === 'basic') opts.push(`headers: { Authorization: 'Basic ' + Buffer.from('admin:password123').toString('base64') }`);
      if (r.body) opts.push('data: ' + indent(JSON.stringify(r.body, null, 2), 4));
      const L = [`test('${r.m} ${r.path}', async ({ request }) => {`, `  const start = Date.now();`, `  const res = await request.${r.m === 'DELETE' ? 'delete' : r.m.toLowerCase()}('${r.path}'${opts.length ? ', {\n    ' + opts.join(',\n    ') + '\n  }' : ''});`];
      if (r.checks.some(c => ['json', 'has'].includes(c.kind))) L.push('  const body = await res.json();');
      r.checks.forEach(c => {
        if (c.kind === 'status') L.push(`  expect(res.status()).toBe(${+c.b});`);
        if (c.kind === 'json') L.push(`  expect(body${jsPath(c.a)}).toEqual(${jstr(parseVal(c.b))});`);
        if (c.kind === 'has') L.push(`  expect(body${jsPath(c.a)}).toBeDefined();`);
        if (c.kind === 'header') L.push(`  expect(res.headers()[${jstr(c.a.toLowerCase())}]).toContain(${jstr(c.b)});`);
        if (c.kind === 'text') L.push(`  expect(await res.text()).toContain(${jstr(c.b)});`);
        if (c.kind === 'time') L.push(`  expect(Date.now() - start).toBeLessThan(${+c.b});`);
      });
      L.push('});');
      return L.join('\n');
    },
    'js-native': r => {
      const h = ["Accept: 'application/json'"];
      if (r.body) h.push("'Content-Type': 'application/json'");
      if (r.auth === 'cookie') h.push('Cookie: `token=${token}`');
      if (r.auth === 'basic') h.push(`Authorization: 'Basic ' + btoa('admin:password123')`);
      const o = [`method: '${r.m}'`, `headers: { ${h.join(', ')} }`];
      if (r.body) o.push('body: JSON.stringify(' + indent(JSON.stringify(r.body, null, 2), 4) + ')');
      o.push('signal: AbortSignal.timeout(10_000)');
      const L = [`test('${r.m} ${r.path}', async () => {`, '  const start = performance.now();', `  const res = await fetch(\`\${BASE}${r.path}\`, {\n    ${o.join(',\n    ')}\n  });`];
      if (r.checks.some(c => ['json', 'has'].includes(c.kind))) L.push('  const body = await res.json();');
      r.checks.forEach(c => {
        if (c.kind === 'status') L.push(`  assert.equal(res.status, ${+c.b});`);
        if (c.kind === 'json') L.push(`  assert.deepEqual(body${jsPath(c.a)}, ${jstr(parseVal(c.b))});`);
        if (c.kind === 'has') L.push(`  assert.ok(body${jsPath(c.a)} !== undefined);`);
        if (c.kind === 'header') L.push(`  assert.match(res.headers.get(${jstr(c.a)}) ?? '', /${c.b.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&')}/);`);
        if (c.kind === 'text') L.push(`  assert.ok((await res.text()).includes(${jstr(c.b)}));`);
        if (c.kind === 'time') L.push(`  assert.ok(performance.now() - start < ${+c.b});`);
      });
      L.push('});');
      return L.join('\n');
    }
  };

  /* ---------- start ---------- */
  loadRequest(PRESETS[1][1]);
  if (!fromHash()) {
    const saved = store.get('api-auto-track');
    if (saved && byId[saved]) render(saved);
  }
  FUN.initScroll && FUN.initScroll();
  FUN.observe();
})();
