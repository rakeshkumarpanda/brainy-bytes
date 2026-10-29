/* ===== Selenium playground: a pretend browser you drive with real Selenium lines =====
   A lesson places <div class="sp" data-sp="scenario"></div>. The reader edits a short Selenium script in Java, Python
   or JavaScript, then runs it all or one line at a time. Each line is read by a small interpreter that knows the
   common Selenium calls, turns them into the W3C WebDriver request a real binding would send, and carries it out on a
   practice page inside an iframe. Time is virtual, so waits, sleeps and late elements play out in a moment while the
   log shows the clock. It is a teaching model: the request shapes, error names and waiting rules follow the W3C
   specification and the Selenium docs, but the pages are small copies of the Selenium test pages. */
const SEPLAY = (() => {
  const $ = (s, r = document) => r.querySelector(s);
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const ELEM = 'element-6066-11e4-a52e-4f735466cecf';
  const BASE = 'https://www.selenium.dev/selenium/web/';

  /* ---------------- practice pages: small copies of https://www.selenium.dev/selenium/web/ ---------------- */
  const CSS = '<style>body{font-family:system-ui,sans-serif;font-size:14px;margin:10px;color:#1b2a3c}label{display:block;margin:6px 0}input,select,textarea,button{font:inherit;margin-top:2px}h1,h2{font-size:20px;margin:0 0 8px}.redbox{background:red;width:60px;height:60px;border:1px solid #000;margin:5px;display:inline-block}</style>';
  const PAGES = {
    'web-form.html': {
      title: 'Web form',
      html: `${CSS}<h1>Web form</h1><form method="get" action="submitted-form.html">
        <label>Text input <input type="text" name="my-text" id="my-text-id" myprop="myvalue"></label>
        <label>Password <input type="password" name="my-password" autocomplete="off"></label>
        <label>Textarea <textarea name="my-textarea" rows="2"></textarea></label>
        <label>Disabled input <input type="text" name="my-disabled" placeholder="Disabled input" disabled></label>
        <label>Readonly input <input type="text" name="my-readonly" value="Readonly input" readonly></label>
        <label>Dropdown (select) <select name="my-select"><option selected>Open this select menu</option><option value="1">One</option><option value="2">Two</option><option value="3">Three</option></select></label>
        <label><input type="checkbox" name="my-check" id="my-check-1" checked> Checked checkbox</label>
        <label><input type="checkbox" name="my-check" id="my-check-2"> Default checkbox</label>
        <label><input type="radio" name="my-radio" id="my-radio-1" checked> Checked radio</label>
        <label><input type="radio" name="my-radio" id="my-radio-2"> Default radio</label>
        <button type="submit">Submit</button> <a href="./index.html">Return to index</a></form>`
    },
    'submitted-form.html': { title: 'Web form - target page', html: `${CSS}<h1>Form submitted</h1><p id="message">Received!</p>` },
    'dynamic.html': {
      title: '',
      html: `${CSS}<input id="adder" type="button" value="Add a box!"> <input id="reveal" type="button" value="Reveal a new input"> <input id="revealed" style="display:none">`,
      init(sim, doc) {
        let next = 0;
        doc.getElementById('adder').addEventListener('click', () => {
          const id = 'box' + next++;
          sim.later(1000, () => { const b = doc.createElement('div'); b.id = id; b.className = 'redbox'; doc.body.appendChild(b); }, 'the page adds a red box');
        });
        doc.getElementById('reveal').addEventListener('click', () => {
          sim.later(1000, () => { doc.getElementById('revealed').style.display = ''; }, 'the page shows the hidden input');
        });
      }
    },
    'alerts.html': {
      title: 'Testing Alerts',
      html: `${CSS}<h2>Alerts</h2><p><a href="#" id="alert">click me</a> opens an alert.</p><p><a href="#" id="slow-alert">slow alert</a> opens one after 2 seconds.</p><p><a href="#" id="confirm">confirm</a> asks OK or Cancel.</p><p><a href="#" id="prompt">prompt</a> asks for text.</p><p id="text">Result shows here</p>`,
      init(sim, doc) {
        const w = doc.defaultView;
        const on = (id, f) => doc.getElementById(id).addEventListener('click', e => { e.preventDefault(); f(); });
        on('alert', () => w.alert('cheese'));
        on('slow-alert', () => sim.later(2000, () => w.alert('Slow'), 'the page opens an alert'));
        on('confirm', () => { doc.getElementById('text').textContent = w.confirm('Are you sure?') ? 'You clicked OK' : 'You clicked Cancel'; });
        on('prompt', () => { const v = w.prompt('Enter something'); doc.getElementById('text').textContent = v === null ? 'You cancelled' : 'You typed: ' + v; });
      }
    },
    'locators_tests/locators.html': {
      title: '',
      html: `${CSS}<h2>Contact Selenium</h2><form>
        <input type="radio" name="gender" value="m">Male <input type="radio" name="gender" value="f">Female<br><br>
        <label for="fname">First name:</label><input class="information" type="text" id="fname" name="fname" value="Jane"><br>
        <label for="lname">Last name:</label><input class="information" type="text" id="lname" name="lname" value="Doe"><br>
        <label for="newsletter">Newsletter:</label> <input type="checkbox" name="newsletter" value="1"><br><br>
        <input type="submit" value="Submit"></form>
        <p>To know more about Selenium, visit the official page <a href="https://www.selenium.dev/">Selenium Official Page</a></p>`
    },
    'iframes.html': {
      title: 'This page has iframes',
      html: `${CSS}<h1 id="iframe_page_heading">This page has iframes</h1><iframe id="iframe1" name="iframe1-name" style="width:100%;height:150px;border:1px solid #999"></iframe>`,
      init(sim, doc) {
        const f = doc.getElementById('iframe1');
        f.srcdoc = `${CSS}<h2>Inside the frame</h2><label>Email <input type="text" name="email_input" id="email"></label><button id="submitButton">Sign in</button><p id="out"></p>`;
        f.addEventListener('load', () => {
          const d = f.contentDocument;
          d.getElementById('submitButton').addEventListener('click', () => { d.getElementById('out').textContent = 'Signed in as ' + d.getElementById('email').value; });
        });
      }
    },
    'index.html': { title: 'Index of Available Pages', html: `${CSS}<h1>Index of Available Pages</h1><ul><li><a href="web-form.html">web-form.html</a></li><li><a href="dynamic.html">dynamic.html</a></li><li><a href="alerts.html">alerts.html</a></li><li><a href="iframes.html">iframes.html</a></li></ul>` }
  };

  /* ---------------- a small expression parser for Java, Python and JavaScript lines ---------------- */
  function lex(s) {
    const out = [];
    let i = 0;
    while (i < s.length) {
      const c = s[i];
      if (/\s/.test(c)) { i++; continue; }
      if (c === '"' || c === "'" || c === '`') {
        let j = i + 1, v = '';
        while (j < s.length && s[j] !== c) { if (s[j] === '\\' && j + 1 < s.length) { j++; v += { n: '\n', t: '\t' }[s[j]] || s[j]; } else v += s[j]; j++; }
        if (j >= s.length) throw new Error('A string is not closed');
        out.push({ t: 'str', v }); i = j + 1; continue;
      }
      const num = /^\d+(?:\.\d+)?[LlFfDd]?/.exec(s.slice(i));
      if (num) { out.push({ t: 'num', v: parseFloat(num[0]) }); i += num[0].length; continue; }
      const id = /^[A-Za-z_$][\w$]*/.exec(s.slice(i));
      if (id) { out.push({ t: 'id', v: id[0] }); i += id[0].length; continue; }
      const op = /^(=>|->|==|!=|===|!==|&&|\|\||<=|>=|[().,\[\]{}:+\-*\/<>!=])/.exec(s.slice(i));
      if (op) { out.push({ t: 'op', v: op[0] }); i += op[0].length; continue; }
      throw new Error('Cannot read the character ' + c);
    }
    return out;
  }
  function parse(src) {
    const T = lex(src);
    let p = 0;
    const peek = (v, k = 0) => T[p + k] && T[p + k].v === v && T[p + k].t !== 'str';
    const eat = v => { if (!peek(v)) throw new Error(`Expected "${v}"`); p++; };
    function expr() {
      // lambdas: Python  lambda d: x   Java  d -> x   JS  d => x  or  () => x
      if (T[p] && T[p].t === 'id' && T[p].v === 'lambda') { p++; while (T[p] && !peek(':')) p++; eat(':'); return { k: 'fn', body: expr() }; }
      if (T[p] && T[p].t === 'id' && (peek('->', 1) || peek('=>', 1))) { p += 2; return { k: 'fn', body: expr() }; }
      if (peek('(') && peek(')', 1) && peek('=>', 2)) { p += 3; return { k: 'fn', body: expr() }; }
      return cmp();
    }
    function cmp() {
      let a = add();
      while (T[p] && T[p].t === 'op' && ['==', '!=', '===', '!==', '<', '>', '<=', '>='].includes(T[p].v)) { const o = T[p++].v; a = { k: 'bin', o, a, b: add() }; }
      return a;
    }
    function add() {
      let a = post();
      while (peek('+') || peek('-') || peek('*')) { const o = T[p++].v; a = { k: 'bin', o, a, b: post() }; }
      return a;
    }
    function args(close) {
      const list = [];
      while (!peek(close)) {
        if (T[p] && T[p].t === 'id' && peek('=', 1) && !peek('==', 1)) p += 2;   // Python keyword argument
        list.push(expr());
        if (!peek(close)) eat(',');
      }
      eat(close);
      return list;
    }
    function primary() {
      const t = T[p++];
      if (!t) throw new Error('The line ends too early');
      if (t.t === 'str') return { k: 'lit', v: t.v };
      if (t.t === 'num') return { k: 'lit', v: t.v };
      if (t.t === 'op' && t.v === '-') { const n = primary(); return { k: 'bin', o: '-', a: { k: 'lit', v: 0 }, b: n }; }
      if (t.t === 'op' && t.v === '(') {
        const items = args(')');
        return items.length === 1 ? items[0] : { k: 'tuple', items };
      }
      if (t.t === 'op' && t.v === '[') return { k: 'tuple', items: args(']') };
      if (t.t === 'op' && t.v === '{') {
        const obj = {};
        while (!peek('}')) { const key = T[p++].v; eat(':'); obj[key] = expr(); if (!peek('}')) eat(','); }
        eat('}');
        return { k: 'obj', obj };
      }
      if (t.t === 'id') {
        if (t.v === 'new') { const callee = postfix({ k: 'name', v: T[p++].v }, true); return { k: 'new', e: callee }; }
        if (t.v === 'await') return expr();
        if (t.v === 'true' || t.v === 'True') return { k: 'lit', v: true };
        if (t.v === 'false' || t.v === 'False') return { k: 'lit', v: false };
        if (t.v === 'null' || t.v === 'None' || t.v === 'undefined') return { k: 'lit', v: null };
        if (t.v === 'not') return { k: 'not', e: post() };
        return { k: 'name', v: t.v };
      }
      if (t.t === 'op' && t.v === '!') return { k: 'not', e: post() };
      throw new Error('Unexpected "' + t.v + '"');
    }
    function postfix(e, once) {
      for (;;) {
        if (peek('.')) { p++; const name = T[p++].v; e = { k: 'get', o: e, n: name }; continue; }
        if (peek('(')) { p++; e = { k: 'call', f: e, args: args(')') }; if (once) return e; continue; }
        if (peek('[')) { p++; const i = expr(); eat(']'); e = { k: 'idx', o: e, i }; continue; }
        if (peek('<') && T[p + 1] && T[p + 1].t === 'id' && peek('>', 2)) { p += 3; continue; }  // Java generics such as new ArrayList<>()
        return e;
      }
    }
    function post() { return postfix(primary()); }
    const e = expr();
    if (p < T.length) throw new Error('Did not understand "' + T.slice(p).map(t => t.t === 'str' ? JSON.stringify(t.v) : t.v).join(' ') + '"');
    return e;
  }

  /* ---------------- names: snake_case and camelCase are the same call ---------------- */
  const camel = s => s.replace(/_([a-z])/g, (m, c) => c.toUpperCase());
  const BY = {
    ID: 'id', id: 'id', NAME: 'name', name: 'name', CLASS_NAME: 'className', className: 'className', CSS_SELECTOR: 'css', cssSelector: 'css', css: 'css',
    XPATH: 'xpath', xpath: 'xpath', TAG_NAME: 'tagName', tagName: 'tagName', LINK_TEXT: 'linkText', linkText: 'linkText', PARTIAL_LINK_TEXT: 'partialLinkText', partialLinkText: 'partialLinkText'
  };
  const KEYS = { ENTER: '', RETURN: '', TAB: '', BACK_SPACE: '', BACKSPACE: '', ESCAPE: '', SHIFT: '', CONTROL: '' };

  class SeError extends Error { constructor(w3c, msg) { super(msg); this.w3c = w3c; } }
  const ERR = {
    'no such element': ['NoSuchElementException', 'NoSuchElementException', 'NoSuchElementError', 404],
    'stale element reference': ['StaleElementReferenceException', 'StaleElementReferenceException', 'StaleElementReferenceError', 404],
    'element not interactable': ['ElementNotInteractableException', 'ElementNotInteractableException', 'ElementNotInteractableError', 400],
    'element click intercepted': ['ElementClickInterceptedException', 'ElementClickInterceptedException', 'ElementClickInterceptedError', 400],
    'invalid element state': ['InvalidElementStateException', 'InvalidElementStateException', 'InvalidElementStateError', 400],
    'invalid selector': ['InvalidSelectorException', 'InvalidSelectorException', 'InvalidSelectorError', 400],
    'no such alert': ['NoAlertPresentException', 'NoAlertPresentException', 'NoSuchAlertError', 404],
    'unexpected alert open': ['UnexpectedAlertPresentException', 'UnhandledAlertException', 'UnexpectedAlertOpenError', 500],
    'no such frame': ['NoSuchFrameException', 'NoSuchFrameException', 'NoSuchFrameError', 404],
    'invalid session id': ['InvalidSessionIdException', 'NoSuchSessionException', 'NoSuchSessionError', 404],
    'invalid argument': ['InvalidArgumentException', 'InvalidArgumentException', 'InvalidArgumentError', 400],
    'timeout': ['TimeoutException', 'TimeoutException', 'TimeoutError', 500],
    'unsupported operation': ['NotImplementedError', 'UnsupportedOperationException', 'UnsupportedOperationError', 0]
  };
  const LI = { py: 0, java: 1, js: 2 };

  /* ---------------- one pretend browser session ---------------- */
  function Sim(ui) {
    const S = {
      ui, clock: 0, queue: [], session: null, implicit: 0, pageLoad: 300000, script: 30000, frame: null, dialog: null, url: 'about:blank', elems: [], log: [],
      later(ms, fn, what) { S.queue.push({ at: S.clock + ms, fn, what }); },
      /* move the virtual clock forward and run what the page scheduled */
      tick(ms) {
        const end = S.clock + ms;
        for (;;) {
          S.queue.sort((a, b) => a.at - b.at);
          const q = S.queue[0];
          if (!q || q.at > end) break;
          S.queue.shift();
          S.clock = q.at;
          q.fn();
          if (q.what) S.note(`At ${S.fmt(S.clock)} ${q.what}.`);
        }
        S.clock = end;
      },
      fmt: ms => (ms / 1000).toFixed(ms % 1000 ? 2 : 0) + ' s',
      sid: () => S.session,
      note(t) { ui.line('note', t); }
    };
    return S;
  }

  function mount(el) {
    if (el.dataset.on) return;
    el.dataset.on = '1';
    const sc = SCEN[el.dataset.sp] || SCEN.first;
    let lang = 'py';
    try { lang = { java: 'java', py: 'py', js: 'js' }[localStorage.getItem('se-lang')] || 'java'; } catch (e) { lang = 'java'; }
    el.innerHTML = `<div class="sp-head"><b>${sc.title}</b><span>${sc.sub}</span></div>
      <div class="sp-body"><div class="sp-left"><textarea class="sp-ed" spellcheck="false" aria-label="Selenium script"></textarea>
        <div class="sp-ctl"><select class="sp-lang" aria-label="Language"><option value="java">Java</option><option value="py">Python</option><option value="js">JavaScript</option></select>
        <button type="button" class="pri sp-run">Run all</button><button type="button" class="sp-step">Run one line</button><button type="button" class="sp-reset">Reset</button><span class="pos"></span></div>
        <div class="sp-log" aria-live="polite"></div></div>
      <div class="sp-page"><div class="sp-url">about:blank</div><iframe class="sp-frame" title="Practice page" style="width:100%;height:330px;border:1px solid var(--line);border-radius:10px;background:#fff"></iframe></div></div>`;
    const ed = $('.sp-ed', el), logEl = $('.sp-log', el), sel = $('.sp-lang', el), frame = $('.sp-frame', el), urlEl = $('.sp-url', el), pos = $('.pos', el);
    sel.value = lang;
    const starter = () => (sc.code[lang] || '').replace(/^\n/, '');
    ed.value = starter();
    ed.style.height = Math.min(420, 30 + 21 * ed.value.split('\n').length) + 'px';
    let S, lines, pc, vars;
    const ui = {
      line(kind, html) {
        const d = document.createElement('div');
        d.className = kind;
        d.innerHTML = html;
        logEl.appendChild(d);
        logEl.scrollTop = logEl.scrollHeight;
      }
    };
    function reset() {
      S = Sim(ui); vars = {}; pc = 0;
      lines = ed.value.split('\n');
      logEl.innerHTML = '';
      frame.srcdoc = '<body style="font-family:system-ui;color:#556;padding:10px">No browser yet. Run the line that starts the driver.</body>';
      urlEl.textContent = 'no session';
      pos.textContent = '';
    }
    sel.onchange = () => { lang = sel.value; ed.value = starter(); try { localStorage.setItem('se-lang', lang); } catch (e) { /* storage unavailable */ } reset(); };
    $('.sp-reset', el).onclick = () => { ed.value = starter(); reset(); };
    ed.addEventListener('input', () => { pc = 0; S = null; });

    /* ---------- the browser side: what the driver does for each W3C command ---------- */
    const doc = () => S.frame ? S.frame.contentDocument : frame.contentDocument;
    function send(method, path, body, result) {
      const p = path.replace('{s}', S.session ? S.session.slice(0, 8) + '…' : '');
      ui.line('rq', `→ ${method} ${esc(p)}${body !== undefined ? ' ' + esc(JSON.stringify(body)) : ''}`);
      let v;
      try { v = result(); } catch (e) {
        if (e instanceof SeError) {
          const code = ERR[e.w3c] ? ERR[e.w3c][3] : 500;
          ui.line('bad', `← ${code} ${esc(JSON.stringify({ value: { error: e.w3c, message: e.message } }))}`);
        }
        throw e;
      }
      ui.line('ok', `← 200 ${esc(JSON.stringify({ value: v === undefined ? null : v }, (k, x) => x && x.__el ? { [ELEM]: x.id } : x)).slice(0, 220)}`);
      return v;
    }
    function needSession() { if (!S.session) throw new SeError('invalid session id', 'There is no session yet. Start the driver first.'); }
    function blockDialog() { if (S.dialog) { const d = S.dialog; S.dialog = null; throw new SeError('unexpected alert open', `unexpected alert open: {Alert text : ${d.text}}`); } }

    function load(url) {
      let path = url.startsWith(BASE) ? url.slice(BASE.length) : null;
      const page = path != null ? PAGES[path.split('#')[0] || 'index.html'] : null;
      S.frame = null; S.queue = [];
      return new Promise(res => {
        frame.onload = () => {
          const d = frame.contentDocument, w = frame.contentWindow;
          w.alert = t => { S.dialog = { type: 'alert', text: String(t) }; S.note('The page opened an alert.'); };
          w.confirm = t => { S.dialog = { type: 'confirm', text: String(t), wait: true }; S.note('The page opened a confirm box.'); return S._answer === true; };
          w.prompt = t => { S.dialog = { type: 'prompt', text: String(t) }; S.note('The page opened a prompt.'); return S._answer === undefined ? null : S._answer; };
          if (page && page.init) page.init(S, d);
          d.addEventListener('submit', e => { e.preventDefault(); const a = e.target.getAttribute('action'); if (a) S._nav = BASE + a.replace('./', ''); }, true);
          d.addEventListener('click', e => {
            const a = e.target.closest('a[href]');
            if (a && !a.getAttribute('href').startsWith('#')) { e.preventDefault(); const h = a.getAttribute('href'); S._nav = h.startsWith('http') ? h : BASE + h.replace('./', ''); }
          }, true);
          res();
        };
        S.url = url; urlEl.textContent = url;
        frame.srcdoc = page ? `<title>${esc(page.title)}</title>${page.html}` : `<title>404 Not Found</title><h1 style="font-family:system-ui">Not Found</h1><p style="font-family:system-ui">This pretend browser only has a few of the Selenium practice pages: ${Object.keys(PAGES).map(k => BASE + k).join(', ')}</p>`;
        S.elems.forEach(x => { x.stale = true; });
      });
    }
    async function afterAction() {
      if (S._nav) { const u = S._nav; S._nav = null; S.note('The browser goes to ' + esc(u)); await load(u); }
    }

    function locate(by, value, root) {
      const d = doc();
      const base = root ? root.node : d;
      let list = [];
      try {
        if (by === 'xpath') {
          const r = d.evaluate(value, base, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
          for (let i = 0; i < r.snapshotLength; i++) if (r.snapshotItem(i).nodeType === 1) list.push(r.snapshotItem(i));
        } else if (by === 'linkText' || by === 'partialLinkText') {
          list = [...base.querySelectorAll('a')].filter(a => by === 'linkText' ? a.textContent.trim() === value : a.textContent.includes(value));
        } else list = [...base.querySelectorAll(wire(by, value).value)];
      } catch (e) { throw new SeError('invalid selector', `invalid selector: ${value}`); }
      return list;
    }
    /* what the bindings put on the wire: id, name and class name become CSS selectors */
    function wire(by, value) {
      if (by === 'id') return { using: 'css selector', value: lang === 'js' ? `*[id="${value}"]` : lang === 'py' ? `[id="${value}"]` : `#${value}` };
      if (by === 'name') return { using: 'css selector', value: lang === 'js' ? `*[name="${value}"]` : `[name="${value}"]` };
      if (by === 'className') return { using: 'css selector', value: '.' + value };
      if (by === 'css') return { using: 'css selector', value };
      if (by === 'tagName') return { using: 'tag name', value };
      if (by === 'linkText') return { using: 'link text', value };
      if (by === 'partialLinkText') return { using: 'partial link text', value };
      return { using: 'xpath', value };
    }
    function wrap(node) {
      let w = S.elems.find(x => x.node === node && !x.stale);
      if (!w) { w = { __el: true, node, id: 'f.' + Math.random().toString(16).slice(2, 10).toUpperCase(), stale: false, doc: node.ownerDocument }; S.elems.push(w); }
      return w;
    }
    function shown(n) {
      const w = n.ownerDocument.defaultView, st = w.getComputedStyle(n);
      if (n.type === 'hidden') return false;
      if (st.display === 'none' || st.visibility === 'hidden' || st.opacity === '0') return false;
      const r = n.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    }
    function check(e) {
      if (!e || !e.__el) throw new SeError('invalid argument', 'This is not a web element.');
      if (e.stale || !e.node.isConnected || e.node.ownerDocument !== doc()) throw new SeError('stale element reference', 'stale element reference: element is not attached to the page document');
    }
    function hit(node) {
      try { doc().querySelectorAll('.sp-hit').forEach(n => n.classList.remove('sp-hit')); } catch (e) { /* page changed */ }
      if (node && node.classList) { node.classList.add('sp-hit'); node.scrollIntoView({ block: 'nearest' }); }
    }

    /* find with the implicit wait: the driver keeps looking until the element shows up or the time runs out */
    function findWait(by, value, root, many) {
      const start = S.clock;
      for (;;) {
        const list = locate(by, value, root);
        if (list.length || S.clock - start >= S.implicit) {
          if (S.implicit && S.clock > start) S.note(`The implicit wait looked for ${S.fmt(S.clock - start)}.`);
          if (!list.length && !many) throw new SeError('no such element', `no such element: Unable to locate element: {"method":"${wire(by, value).using}","selector":"${wire(by, value).value}"}`);
          return many ? list.map(wrap) : wrap(list[0]);
        }
        S.tick(Math.min(100, S.implicit - (S.clock - start)));
      }
    }

    /* ---------- objects the script can reach ---------- */
    const Driver = { __drv: true };
    const NS = {
      By: { __ns: 'By' }, EC: { __ns: 'EC' }, ExpectedConditions: { __ns: 'EC' }, until: { __ns: 'EC' }, Keys: { __ns: 'Keys' }, Key: { __ns: 'Keys' },
      Duration: { __ns: 'Duration' }, time: { __ns: 'time' }, Thread: { __ns: 'time' }, System: { __ns: 'System' }, console: { __ns: 'console' },
      webdriver: { __ns: 'webdriver' }, Browser: { __ns: 'Browser' }, Math: { __ns: 'Math' }
    };
    const out = v => ui.line('note', '<b>Prints:</b> ' + esc(show(v)));
    function show(v) {
      if (v === null || v === undefined) return lang === 'py' ? 'None' : 'null';
      if (v === true || v === false) return lang === 'py' ? (v ? 'True' : 'False') : String(v);
      if (v.__el) return lang === 'py' ? `<selenium.webdriver.remote.webelement.WebElement (session="${S.session.slice(0, 8)}…", element="${v.id}")>` : `[[ChromeDriver: chrome] -> element ${v.id}]`;
      if (Array.isArray(v)) return '[' + v.map(show).join(', ') + ']';
      if (typeof v === 'object') return JSON.stringify(v);
      return String(v);
    }

    async function startSession() {
      if (S.session) throw new SeError('invalid argument', 'A session is already running.');
      send('POST', '/session', { capabilities: { firstMatch: [{ browserName: 'chrome', 'goog:chromeOptions': {} }] } }, () => {
        S.session = Array.from({ length: 32 }, () => '0123456789abcdef'[Math.floor(Math.random() * 16)]).join('');
        return { sessionId: S.session, capabilities: { browserName: 'chrome', browserVersion: '153.0', pageLoadStrategy: 'normal', timeouts: { implicit: 0, pageLoad: 300000, script: 30000 } } };
      });
      S.note('Chrome opens with a fresh profile.');
      await load('about:blank');
      frame.srcdoc = '<body></body>';
      return Driver;
    }

    function cond(name, a) {
      return { __cond: name, a };
    }
    /* run one wait condition once: returns a truthy value when it holds */
    async function tryCond(c) {
      const n = c.__cond, a = c.a;
      const loc = () => Array.isArray(a[0]) ? { by: BY[a[0][0]] || a[0][0], v: a[0][1] } : { by: a[0].__by, v: a[0].v };
      if (n === 'fn') return evalExpr(c.body, vars);
      if (n === 'presence') { const l = locate(loc().by, loc().v); return l.length ? wrap(l[0]) : false; }
      if (n === 'visible') { const x = a[0] && a[0].__el ? a[0] : null; if (x) { check(x); return shown(x.node) ? x : false; } const l = locate(loc().by, loc().v); return l.length && shown(l[0]) ? wrap(l[0]) : false; }
      if (n === 'clickable') { const x = a[0] && a[0].__el ? a[0] : null; const node = x ? (check(x), x.node) : locate(loc().by, loc().v)[0]; return node && shown(node) && !node.disabled ? wrap(node) : false; }
      if (n === 'invisible') { const l = locate(loc().by, loc().v); return !l.length || !shown(l[0]); }
      if (n === 'titleIs') return doc().title === a[0];
      if (n === 'titleContains') return doc().title.includes(a[0]);
      if (n === 'alert') return S.dialog ? Alert : false;
      if (n === 'textIn') { const l = locate(loc().by, loc().v); return l.length && l[0].textContent.includes(a[1]); }
      if (n === 'count') { const l = locate(loc().by, loc().v); return l.length === a[1]; }
      throw new SeError('invalid argument', 'This playground does not know that condition.');
    }
    async function waitFor(c, timeout, poll, msg) {
      const start = S.clock;
      let last;
      for (;;) {
        let v;
        try { v = await tryCond(c); last = null; } catch (e) {
          if (!(e instanceof SeError) || !['no such element', 'stale element reference'].includes(e.w3c)) throw e;
          last = e; v = false;
        }
        if (v) { S.note(`The explicit wait passed after ${S.fmt(S.clock - start)}.`); return v; }
        if (S.clock - start >= timeout) throw new SeError('timeout', (msg ? msg + ' ' : '') + `Waited ${S.fmt(timeout)} for the condition` + (last ? ` (last error: ${last.w3c})` : ''));
        S.tick(Math.min(poll, timeout - (S.clock - start)));
      }
    }

    const Alert = { __alert: true };
    const Switch = { __switch: true };
    const Nav = { __nav: true };
    const Manage = { __manage: true };
    const Timeouts = { __timeouts: true };

    async function member(o, name, args, isCall) {
      const n = camel(name);
      if (o && o.__ns) {
        const ns = o.__ns;
        if (ns === 'By') {
          const k = BY[name];
          if (!k) throw new SeError('invalid argument', 'Unknown locator By.' + name);
          return isCall ? { __by: k, v: args[0] } : k;
        }
        if (ns === 'Keys') return KEYS[name] || '';
        if (ns === 'Duration') return n === 'ofMillis' ? args[0] : n === 'ofSeconds' ? args[0] * 1000 : n === 'ofMinutes' ? args[0] * 60000 : 0;
        if (ns === 'time' && (n === 'sleep')) { const ms = o === NS.Thread ? args[0] : args[0] * 1000; S.note(`Sleeping ${S.fmt(ms)}. Nothing else happens in the script meanwhile.`); S.tick(ms); return null; }
        if (ns === 'System') return name === 'out' ? { __ns: 'sysout' } : null;
        if (ns === 'sysout' || ns === 'console') { if (/print|log/.test(name)) out(args[0]); return null; }
        if (ns === 'webdriver') return isCall ? startSession() : { __start: true };
        if (ns === 'Browser') return name.toLowerCase();
        if (ns === 'EC') {
          const map = { presenceOfElementLocated: 'presence', elementLocated: 'presence', visibilityOfElementLocated: 'visible', elementIsVisible: 'visible', visibilityOf: 'visible',
            elementToBeClickable: 'clickable', invisibilityOfElementLocated: 'invisible', titleIs: 'titleIs', titleContains: 'titleContains', alertIsPresent: 'alert',
            textToBePresentInElementLocated: 'textIn', textToBePresentInElement: 'textIn', numberOfElementsToBe: 'count' };
          if (!map[n]) throw new SeError('invalid argument', 'This playground does not know ' + name);
          return cond(map[n], args);
        }
        if (ns === 'Math') return Math[name] ? Math[name](...args) : null;
      }
      if (o && o.__start) return o;
      if (o && o.__builder) { if (n === 'build') return startSession(); return o; }
      if (o && o.__wait) {
        if (n === 'until') return waitFor(args[0], o.t, o.poll, args[1]);
        if (n === 'pollingEvery') { o.poll = args[0]; return o; }
        if (n === 'withTimeout') { o.t = args[0]; return o; }
        if (n === 'ignoring' || n === 'withMessage') return o;
      }
      if (o === Driver) {
        if (!S.session && n !== 'quit') throw new SeError('invalid session id', 'There is no session. It was never started or it was quit.');
        if (n === 'get' || n === 'to') {
          needSession(); blockDialog();
          if (!/^(https?|about|data|file):/.test(args[0])) throw new SeError('invalid argument', 'invalid argument: the URL must be absolute');
          send('POST', '/session/{s}/url', { url: args[0] }, () => null);
          await load(args[0]);
          S.tick(150);
          S.note(`The page finished loading (readyState is complete) at ${S.fmt(S.clock)}.`);
          return null;
        }
        if (n === 'title' || n === 'getTitle') { blockDialog(); return send('GET', '/session/{s}/title', undefined, () => doc().title); }
        if (n === 'currentUrl' || n === 'getCurrentUrl') { blockDialog(); return send('GET', '/session/{s}/url', undefined, () => S.url); }
        if (n === 'pageSource' || n === 'getPageSource') return send('GET', '/session/{s}/source', undefined, () => doc().documentElement.outerHTML.slice(0, 120) + '…');
        if (n === 'findElement' || n === 'findElements') {
          blockDialog();
          const L = args.length === 2 ? { __by: BY[args[0]] || args[0], v: args[1] } : args[0];
          const many = n === 'findElements';
          return send('POST', `/session/{s}/element${many ? 's' : ''}`, wire(L.__by, L.v), () => { const r = findWait(L.__by, L.v, null, many); hit(many ? (r[0] && r[0].node) : r.node); return r; });
        }
        if (n === 'implicitlyWait') { S.implicit = args[0] * 1000; return send('POST', '/session/{s}/timeouts', { implicit: S.implicit }, () => null); }
        if (n === 'navigate') return Nav;
        if (n === 'manage') return Manage;
        if (n === 'switchTo') return Switch;
        if (n === 'back' || n === 'forward' || n === 'refresh') return member(Nav, n, args, true);
        if (n === 'wait') return waitFor(args[0], args[1] ?? 0, 50, args[2]);
        if (n === 'sleep') { S.note(`Sleeping ${S.fmt(args[0])}.`); S.tick(args[0]); return null; }
        if (n === 'quit') {
          if (!S.session) return null;
          send('DELETE', '/session/{s}', undefined, () => null);
          S.session = null; frame.srcdoc = '<body style="font-family:system-ui;color:#556;padding:10px">The browser has closed. The session is gone.</body>'; urlEl.textContent = 'no session';
          return null;
        }
        if (n === 'close') { send('DELETE', '/session/{s}/window', undefined, () => []); S.session = null; frame.srcdoc = '<body></body>'; S.note('That was the last window, so the session ended too.'); return null; }
        if (n === 'setTimeouts') { const t = args[0] || {}; if (t.implicit !== undefined) S.implicit = t.implicit; return send('POST', '/session/{s}/timeouts', t, () => null); }
        if (n === 'executeScript') return send('POST', '/session/{s}/execute/sync', { script: args[0], args: args.slice(1) }, () => { try { return frame.contentWindow.Function(args[0])(); } catch (e) { throw new SeError('javascript error', e.message); } });
        throw new SeError('unsupported operation', 'This playground does not know driver.' + name);
      }
      if (o === Nav) {
        if (n === 'to') return member(Driver, 'get', args, true);
        if (n === 'refresh') { send('POST', '/session/{s}/refresh', {}, () => null); await load(S.url); return null; }
        if (n === 'back' || n === 'forward') { send('POST', `/session/{s}/${n}`, {}, () => null); S.note('The pretend browser keeps no history, so it stays on this page.'); return null; }
      }
      if (o === Manage) { if (n === 'timeouts') return Timeouts; if (n === 'setTimeouts') return member(Driver, 'setTimeouts', args, true); if (n === 'window') return { __win: true }; }
      if (o && o.__win) return null;
      if (o === Timeouts) { if (n === 'implicitlyWait') { S.implicit = args[0]; send('POST', '/session/{s}/timeouts', { implicit: args[0] }, () => null); return Timeouts; } if (n === 'pageLoadTimeout') return Timeouts; }
      if (o === Switch) {
        if (n === 'alert') {
          return send('GET', '/session/{s}/alert/text', undefined, () => { if (!S.dialog) throw new SeError('no such alert', 'no such alert'); return S.dialog.text; }) !== undefined ? Alert : Alert;
        }
        if (n === 'frame') {
          blockDialog();
          const a = args[0];
          return send('POST', '/session/{s}/frame', { id: a && a.__el ? { [ELEM]: a.id } : a }, () => {
            const d = doc(), fr = [...d.querySelectorAll('iframe,frame')];
            let f = a && a.__el ? a.node : typeof a === 'number' ? fr[a] : fr.find(x => x.id === a || x.name === a);
            if (!f) throw new SeError('no such frame', 'no such frame');
            S.frame = f; return null;
          });
        }
        if (n === 'defaultContent' || n === 'parentFrame') return send('POST', n === 'defaultContent' ? '/session/{s}/frame' : '/session/{s}/frame/parent', n === 'defaultContent' ? { id: null } : {}, () => { S.frame = null; return null; });
        if (n === 'activeElement') return send('GET', '/session/{s}/element/active', undefined, () => wrap(doc().activeElement));
      }
      if (o === Alert) {
        if (n === 'text' || n === 'getText') return send('GET', '/session/{s}/alert/text', undefined, () => { if (!S.dialog) throw new SeError('no such alert', 'no such alert'); return S.dialog.text; });
        if (n === 'accept' || n === 'dismiss') return send('POST', `/session/{s}/alert/${n}`, {}, () => {
          if (!S.dialog) throw new SeError('no such alert', 'no such alert');
          const d = S.dialog; S.dialog = null;
          if (d.type !== 'alert') {
            S._answer = n === 'accept' ? (d.type === 'prompt' ? (d.typed ?? '') : true) : (d.type === 'prompt' ? undefined : false);
            const w = doc().defaultView, t = doc().getElementById('text');
            if (t) t.textContent = d.type === 'confirm' ? (n === 'accept' ? 'You clicked OK' : 'You clicked Cancel') : (n === 'accept' ? 'You typed: ' + (d.typed ?? '') : 'You cancelled');
            S._answer = undefined; void w;
          }
          return null;
        });
        if (n === 'sendKeys') return send('POST', '/session/{s}/alert/text', { text: args[0] }, () => { if (!S.dialog) throw new SeError('no such alert', 'no such alert'); S.dialog.typed = args[0]; return null; });
      }
      if (o && o.__select) {
        const s = o.el.node;
        const opts = [...s.options];
        const pick = (f, what) => {
          const op = opts.find(f);
          if (!op) throw new SeError('no such element', 'Cannot locate option with ' + what);
          if (op.disabled) throw new SeError('unsupported operation', 'You may not select a disabled option');
          send('POST', `/session/{s}/element/${wrap(op).id}/click`, {}, () => { op.selected = true; s.dispatchEvent(new Event('change')); return null; });
          return null;
        };
        if (n === 'selectByVisibleText') return pick(x => x.text.trim() === args[0], 'text: ' + args[0]);
        if (n === 'selectByValue') return pick(x => x.value === args[0], 'value: ' + args[0]);
        if (n === 'selectByIndex') return pick((x, i) => i === args[0], 'index: ' + args[0]);
        if (n === 'options' || n === 'getOptions') return opts.map(wrap);
        if (n === 'firstSelectedOption' || n === 'getFirstSelectedOption') return wrap(opts[s.selectedIndex]);
      }
      if (Array.isArray(o)) {
        if (n === 'size' || n === 'length') return o.length;
        if (n === 'get') return o[args[0]];
      }
      if (typeof o === 'string') {
        if (n === 'length') return o.length;
        if (n === 'upper' || n === 'toUpperCase') return o.toUpperCase();
        if (n === 'strip' || n === 'trim') return o.trim();
        if (n === 'contains' || n === 'includes') return o.includes(args[0]);
        if (n === 'equals') return o === args[0];
      }
      if (o && o.__el) {
        const id = o.id;
        if (n === 'findElement' || n === 'findElements') {
          check(o);
          const L = args.length === 2 ? { __by: BY[args[0]] || args[0], v: args[1] } : args[0];
          const many = n === 'findElements';
          return send('POST', `/session/{s}/element/${id}/element${many ? 's' : ''}`, wire(L.__by, L.v), () => { const r = findWait(L.__by, L.v, o, many); hit(many ? (r[0] && r[0].node) : r.node); return r; });
        }
        const E = (method, path, body, f) => send(method, `/session/{s}/element/${id}${path}`, body, () => { blockDialog(); check(o); hit(o.node); return f(o.node); });
        if (n === 'click') {
          E('POST', '/click', {}, node => {
            if (!shown(node)) throw new SeError('element not interactable', 'element not interactable')
            node.click(); return null;
          });
          await afterAction(); return null;
        }
        if (n === 'sendKeys') {
          const text = args.join('');
          E('POST', '/value', { text }, node => {
            if (!shown(node)) throw new SeError('element not interactable', 'element not interactable');
            if (node.disabled || node.readOnly || !('value' in node)) throw new SeError('invalid element state', 'invalid element state');
            node.focus();
            for (const ch of text) {
              if (ch === KEYS.ENTER || ch === KEYS.RETURN) { if (node.form) node.form.requestSubmit ? node.form.requestSubmit() : node.form.submit(); }
              else if (ch === KEYS.BACK_SPACE) node.value = node.value.slice(0, -1);
              else if (ch.charCodeAt(0) < 0xE000) node.value += ch;
            }
            node.dispatchEvent(new Event('input', { bubbles: true }));
            return null;
          });
          await afterAction(); return null;
        }
        if (n === 'clear') return E('POST', '/clear', {}, node => { if (node.disabled || node.readOnly) throw new SeError('invalid element state', 'invalid element state: Element must be user-editable in order to clear it.'); node.value = ''; return null; });
        if (n === 'submit') { E('POST', '/click', {}, node => { const f = node.form || node.closest('form'); if (f) f.requestSubmit(); return null; }); await afterAction(); return null; }
        if (n === 'text' || n === 'getText') return E('GET', '/text', undefined, node => shown(node) ? node.innerText.trim() : '');
        if (n === 'tagName' || n === 'getTagName') return E('GET', '/name', undefined, node => node.tagName.toLowerCase());
        if (n === 'getAttribute') return E('POST', '/execute/sync', { script: '/* getAttribute atom */', args: [args[0]] }, node => { const v = node[args[0]]; return typeof v === 'string' || typeof v === 'boolean' ? (v === false ? null : String(v)) : node.getAttribute(args[0]); });
        if (n === 'getDomAttribute') return E('GET', `/attribute/${args[0]}`, undefined, node => node.getAttribute(args[0]));
        if (n === 'getDomProperty' || n === 'getProperty') return E('GET', `/property/${args[0]}`, undefined, node => node[args[0]] ?? null);
        if (n === 'isDisplayed') return E('POST', '/execute/sync', { script: '/* isDisplayed atom */' }, node => shown(node));
        if (n === 'isEnabled') return E('GET', '/enabled', undefined, node => !node.disabled);
        if (n === 'isSelected') return E('GET', '/selected', undefined, node => !!(node.checked || node.selected));
        if (n === 'rect' || n === 'getRect') return E('GET', '/rect', undefined, node => { const r = node.getBoundingClientRect(); return { x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height) }; });
        if (n === 'valueOfCssProperty' || n === 'getCssValue') return E('GET', `/css/${args[0]}`, undefined, node => node.ownerDocument.defaultView.getComputedStyle(node)[camel(args[0].replace(/-/g, '_'))]);
      }
      throw new SeError('unsupported operation', `This playground does not know ${name}${isCall ? '()' : ''} here`);
    }

    async function evalExpr(e, scope) {
      switch (e.k) {
        case 'lit': return e.v;
        case 'tuple': { const r = []; for (const x of e.items) r.push(await evalExpr(x, scope)); return r; }
        case 'obj': { const r = {}; for (const k in e.obj) r[k] = await evalExpr(e.obj[k], scope); return r; }
        case 'not': return !(await evalExpr(e.e, scope));
        case 'fn': return { __cond: 'fn', body: e.body };
        case 'bin': {
          const a = await evalExpr(e.a, scope), b = await evalExpr(e.b, scope);
          return { '+': () => (typeof a === 'string' || typeof b === 'string') ? show(a) + show(b) : a + b, '-': () => a - b, '*': () => a * b, '==': () => a === b, '===': () => a === b, '!=': () => a !== b, '!==': () => a !== b, '<': () => a < b, '>': () => a > b, '<=': () => a <= b, '>=': () => a >= b }[e.o]();
        }
        case 'name': {
          if (e.v in scope) return scope[e.v];
          if (e.v in NS) return NS[e.v];
          if (e.v === 'driver') return Driver;
          throw new Error(`"${e.v}" is not defined yet`);
        }
        case 'get': {
          const o = await evalExpr(e.o, scope);
          if (o === Driver && e.n === 'switch_to') return Switch;
          if (o === Switch && e.n === 'alert') return member(Switch, 'alert', [], false);
          if (o === Switch && e.n === 'active_element') return member(Switch, 'activeElement', [], false);
          if (o && o.__ns === 'By' && BY[e.n]) return BY[e.n];
          if (o && (o.__ns === 'Keys')) return KEYS[e.n] || '';
          if (o && o.__ns === 'System' && e.n === 'out') return { __ns: 'sysout' };
          if (o && o.__ns === 'Browser') return member(o, e.n, [], false);
          if (o && o.__ns) return { __bound: true, o, n: e.n };
          // properties in Python (driver.title, element.text) and JS (list.length)
          const props = ['title', 'current_url', 'page_source', 'text', 'tag_name', 'rect', 'length', 'options', 'first_selected_option'];
          if (props.includes(e.n)) return member(o, e.n, [], false);
          return { __bound: true, o, n: e.n };
        }
        case 'call': {
          if (e.f.k === 'name') {
            const f = e.f.v, args = []; for (const a of e.args) args.push(await evalExpr(a, scope));
            if (f === 'print') { out(args.length > 1 ? args.map(show).join(' ') : args[0]); return null; }
            if (f === 'len') return args[0].length;
            if (f === 'str' || f === 'String') return show(args[0]);
            if (f === 'WebDriverWait') return { __wait: true, t: args[1] * 1000, poll: (args[2] ?? 0.5) * 1000 };
            if (f === 'Select') { check(args[0]); if (args[0].node.disabled) throw new SeError('unsupported operation', 'You may not create a Select for a disabled select element'); return { __select: true, el: args[0] }; }
            if (f === 'Builder') return { __builder: true };
            throw new Error(`The playground does not know the function ${f}()`);
          }
          const target = e.f.k === 'get' ? await evalExpr(e.f.o, scope) : await evalExpr(e.f, scope);
          const name = e.f.k === 'get' ? e.f.n : null;
          const args = []; for (const a of e.args) args.push(await evalExpr(a, scope));
          if (target && target.__start && !name) return startSession();
          if (target && target.__bound) return member(target.o, target.n, args, true);
          return member(target, name, args, true);
        }
        case 'new': {
          const c = e.e;
          const cname = c.k === 'call' ? c.f.v : c.v;
          const args = []; for (const a of (c.args || [])) args.push(await evalExpr(a, scope));
          if (/Driver$/.test(cname)) return startSession();
          if (cname === 'WebDriverWait') return { __wait: true, t: args[1], poll: 500 };
          if (cname === 'FluentWait') return { __wait: true, t: 30000, poll: 500 };
          if (cname === 'Select') return evalExpr({ k: 'call', f: { k: 'name', v: 'Select' }, args: c.args }, scope);
          if (cname === 'Builder') return { __builder: true };
          if (cname === 'Actions') return { __actions: true };
          throw new Error(`The playground cannot make a new ${cname}`);
        }
        case 'idx': { const o = await evalExpr(e.o, scope), i = await evalExpr(e.i, scope); return o[i < 0 ? o.length + i : i]; }
      }
      throw new Error('Unknown expression');
    }

    /* ---------- statements ---------- */
    const SKIP = /^\s*(?:$|#|\/\/|\/\*|\*|import\b|from\b|package\b|public\b|class\b|static\b|try\b|finally\b|catch\b|}|{|\)|const\s*{|async\b|\(async|describe\(|it\(|def\b|if __name__|@)/;
    async function exec(raw, no) {
      let s = raw.replace(/;\s*$/, '').replace(/\s+(#|\/\/).*$/, '').trim();
      if (SKIP.test(raw) && !/^\s*(?:const|let|var)\s+\w+\s*=/.test(raw)) return false;
      ui.line('cur', `<b>Line ${no}:</b> ${esc(s)}  <small>(clock ${S.fmt(S.clock)})</small>`);
      s = s.replace(/^await\s+/, '');
      const m = /^(?:(?:const|let|var|final)\s+)?(?:[A-Z][\w.]*(?:<[^=]*>)?(?:\[\])?\s+)?([A-Za-z_]\w*)\s*=(?!=)\s*(.+)$/.exec(s);
      if (/^assert\s/.test(s)) {
        const v = await evalExpr(parse(s.replace(/^assert\s+/, '').replace(/,.*$/, '')), vars);
        if (!v) throw new SeError('assertion', 'AssertionError');
        ui.line('note', 'The assertion holds.');
        return true;
      }
      if (m) { vars[m[1]] = await evalExpr(parse(m[2]), vars); return true; }
      await evalExpr(parse(s), vars);
      return true;
    }
    async function step() {
      if (!S) reset();
      while (pc < lines.length) {
        const no = pc + 1, raw = lines[pc++];
        try {
          if (await exec(raw, no)) { S.tick(20); pos.textContent = `Next: line ${pc + 1} of ${lines.length}`; return true; }
        } catch (e) {
          const name = e instanceof SeError ? (e.w3c === 'assertion' ? 'AssertionError' : (ERR[e.w3c] ? ERR[e.w3c][LI[lang]] : e.w3c)) : 'Playground';
          ui.line('bad', `<b>${esc(name)}:</b> ${esc(e.message)}`);
          if (!(e instanceof SeError)) ui.line('note', 'This playground understands common Selenium lines only. Check the spelling, or try one of the calls used in the lesson.');
          pc = lines.length; pos.textContent = 'Stopped at line ' + no;
          return false;
        }
      }
      pos.textContent = 'Finished';
      if (S.session) ui.line('note', 'The script ended without quit(), so in real life the browser and driver would keep running.');
      return false;
    }
    $('.sp-step', el).onclick = () => step();
    $('.sp-run', el).onclick = async () => { reset(); while (await step()) { /* run every line */ } };
    reset();
  }

  /* ---------------- the scenarios lessons can use ---------------- */
  const SCEN = {
    first: {
      title: 'Try it: the eight steps of a first script',
      sub: 'Run it one line at a time. Watch the request each line sends, then change the text that is typed.',
      code: {
        py: `driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/web-form.html")
title = driver.title
print(title)
driver.implicitly_wait(0.5)
text_box = driver.find_element(By.NAME, "my-text")
submit_button = driver.find_element(By.CSS_SELECTOR, "button")
text_box.send_keys("Selenium")
submit_button.click()
message = driver.find_element(By.ID, "message")
print(message.text)
driver.quit()`,
        java: `WebDriver driver = new ChromeDriver();
driver.get("https://www.selenium.dev/selenium/web/web-form.html");
String title = driver.getTitle();
System.out.println(title);
driver.manage().timeouts().implicitlyWait(Duration.ofMillis(500));
WebElement textBox = driver.findElement(By.name("my-text"));
WebElement submitButton = driver.findElement(By.cssSelector("button"));
textBox.sendKeys("Selenium");
submitButton.click();
WebElement message = driver.findElement(By.id("message"));
System.out.println(message.getText());
driver.quit();`,
        js: `let driver = await new Builder().forBrowser(Browser.CHROME).build();
await driver.get('https://www.selenium.dev/selenium/web/web-form.html');
let title = await driver.getTitle();
console.log(title);
await driver.manage().setTimeouts({implicit: 500});
let textBox = await driver.findElement(By.name('my-text'));
let submitButton = await driver.findElement(By.css('button'));
await textBox.sendKeys('Selenium');
await submitButton.click();
let message = await driver.findElement(By.id('message'));
console.log(await message.getText());
await driver.quit();`
      }
    },
    locators: {
      title: 'Try it: find elements with every locator',
      sub: 'Change a locator and run it again. The element found is outlined in orange on the page.',
      code: {
        py: `driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/locators_tests/locators.html")
first = driver.find_element(By.CLASS_NAME, "information")
print(first.get_attribute("value"))
last = driver.find_element(By.ID, "lname")
news = driver.find_element(By.NAME, "newsletter")
link = driver.find_element(By.LINK_TEXT, "Selenium Official Page")
female = driver.find_element(By.XPATH, "//input[@value='f']")
both = driver.find_elements(By.CSS_SELECTOR, "input.information")
print(len(both))
driver.quit()`,
        java: `WebDriver driver = new ChromeDriver();
driver.get("https://www.selenium.dev/selenium/web/locators_tests/locators.html");
WebElement first = driver.findElement(By.className("information"));
System.out.println(first.getAttribute("value"));
WebElement last = driver.findElement(By.id("lname"));
WebElement news = driver.findElement(By.name("newsletter"));
WebElement link = driver.findElement(By.linkText("Selenium Official Page"));
WebElement female = driver.findElement(By.xpath("//input[@value='f']"));
List<WebElement> both = driver.findElements(By.cssSelector("input.information"));
System.out.println(both.size());
driver.quit();`,
        js: `let driver = await new Builder().forBrowser(Browser.CHROME).build();
await driver.get('https://www.selenium.dev/selenium/web/locators_tests/locators.html');
let first = await driver.findElement(By.className('information'));
console.log(await first.getAttribute('value'));
let last = await driver.findElement(By.id('lname'));
let news = await driver.findElement(By.name('newsletter'));
let link = await driver.findElement(By.linkText('Selenium Official Page'));
let female = await driver.findElement(By.xpath("//input[@value='f']"));
let both = await driver.findElements(By.css('input.information'));
console.log(both.length);
await driver.quit();`
      }
    },
    waits: {
      title: 'Try it: a box that arrives one second late',
      sub: 'Run it as it is and it fails. Then uncomment the implicit wait line, or swap the find for the explicit wait, and run again.',
      code: {
        py: `driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/dynamic.html")
# driver.implicitly_wait(2)
driver.find_element(By.ID, "adder").click()
added = driver.find_element(By.ID, "box0")
# added = WebDriverWait(driver, timeout=2).until(EC.presence_of_element_located((By.ID, "box0")))
print(added.get_dom_attribute("class"))
driver.quit()`,
        java: `WebDriver driver = new ChromeDriver();
driver.get("https://www.selenium.dev/selenium/web/dynamic.html");
// driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(2));
driver.findElement(By.id("adder")).click();
WebElement added = driver.findElement(By.id("box0"));
// WebElement added = new WebDriverWait(driver, Duration.ofSeconds(2)).until(ExpectedConditions.presenceOfElementLocated(By.id("box0")));
System.out.println(added.getDomAttribute("class"));
driver.quit();`,
        js: `let driver = await new Builder().forBrowser(Browser.CHROME).build();
await driver.get('https://www.selenium.dev/selenium/web/dynamic.html');
// await driver.manage().setTimeouts({implicit: 2000});
await driver.findElement(By.id('adder')).click();
let added = await driver.findElement(By.id('box0'));
// let added = await driver.wait(until.elementLocated(By.id('box0')), 2000);
console.log(await added.getDomAttribute('class'));
await driver.quit();`
      }
    },
    reveal: {
      title: 'Try it: present is not the same as visible',
      sub: 'The input is in the page from the start but hidden. Typing into it too early fails. Add a wait for visibility.',
      code: {
        py: `driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/dynamic.html")
revealed = driver.find_element(By.ID, "revealed")
driver.find_element(By.ID, "reveal").click()
# WebDriverWait(driver, timeout=2).until(lambda d: revealed.is_displayed())
revealed.send_keys("Displayed")
print(revealed.get_property("value"))
driver.quit()`,
        java: `WebDriver driver = new ChromeDriver();
driver.get("https://www.selenium.dev/selenium/web/dynamic.html");
WebElement revealed = driver.findElement(By.id("revealed"));
driver.findElement(By.id("reveal")).click();
// new WebDriverWait(driver, Duration.ofSeconds(2)).until(d -> revealed.isDisplayed());
revealed.sendKeys("Displayed");
System.out.println(revealed.getDomProperty("value"));
driver.quit();`,
        js: `let driver = await new Builder().forBrowser(Browser.CHROME).build();
await driver.get('https://www.selenium.dev/selenium/web/dynamic.html');
let revealed = await driver.findElement(By.id('revealed'));
await driver.findElement(By.id('reveal')).click();
// await driver.wait(until.elementIsVisible(revealed), 2000);
await revealed.sendKeys('Displayed');
console.log(await revealed.getDomProperty('value'));
await driver.quit();`
      }
    },
    alerts: {
      title: 'Try it: alerts, confirms and prompts',
      sub: 'The slow alert opens two seconds after the click. Remove the wait and see what switching too early gives you.',
      code: {
        py: `driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/alerts.html")
driver.find_element(By.ID, "slow-alert").click()
alert = WebDriverWait(driver, timeout=3).until(EC.alert_is_present())
print(alert.text)
alert.accept()
driver.find_element(By.ID, "prompt").click()
prompt = driver.switch_to.alert
prompt.send_keys("Selenium")
prompt.accept()
print(driver.find_element(By.ID, "text").text)
driver.quit()`,
        java: `WebDriver driver = new ChromeDriver();
driver.get("https://www.selenium.dev/selenium/web/alerts.html");
driver.findElement(By.id("slow-alert")).click();
Alert alert = new WebDriverWait(driver, Duration.ofSeconds(3)).until(ExpectedConditions.alertIsPresent());
System.out.println(alert.getText());
alert.accept();
driver.findElement(By.id("prompt")).click();
Alert prompt = driver.switchTo().alert();
prompt.sendKeys("Selenium");
prompt.accept();
System.out.println(driver.findElement(By.id("text")).getText());
driver.quit();`,
        js: `let driver = await new Builder().forBrowser(Browser.CHROME).build();
await driver.get('https://www.selenium.dev/selenium/web/alerts.html');
await driver.findElement(By.id('slow-alert')).click();
let alert = await driver.wait(until.alertIsPresent(), 3000);
console.log(await alert.getText());
await alert.accept();
await driver.findElement(By.id('prompt')).click();
let prompt = await driver.switchTo().alert();
await prompt.sendKeys('Selenium');
await prompt.accept();
console.log(await driver.findElement(By.id('text')).getText());
await driver.quit();`
      }
    },
    frames: {
      title: 'Try it: elements inside an iframe',
      sub: 'Run it once as it is. Then delete the switch line and see the NoSuchElement error, because the driver only looks in the current document.',
      code: {
        py: `driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/iframes.html")
iframe = driver.find_element(By.ID, "iframe1")
driver.switch_to.frame(iframe)
driver.find_element(By.NAME, "email_input").send_keys("admin@selenium.dev")
driver.find_element(By.ID, "submitButton").click()
print(driver.find_element(By.ID, "out").text)
driver.switch_to.default_content()
print(driver.find_element(By.TAG_NAME, "h1").text)
driver.quit()`,
        java: `WebDriver driver = new ChromeDriver();
driver.get("https://www.selenium.dev/selenium/web/iframes.html");
WebElement iframe = driver.findElement(By.id("iframe1"));
driver.switchTo().frame(iframe);
driver.findElement(By.name("email_input")).sendKeys("admin@selenium.dev");
driver.findElement(By.id("submitButton")).click();
System.out.println(driver.findElement(By.id("out")).getText());
driver.switchTo().defaultContent();
System.out.println(driver.findElement(By.tagName("h1")).getText());
driver.quit();`,
        js: `let driver = await new Builder().forBrowser(Browser.CHROME).build();
await driver.get('https://www.selenium.dev/selenium/web/iframes.html');
let iframe = await driver.findElement(By.id('iframe1'));
await driver.switchTo().frame(iframe);
await driver.findElement(By.name('email_input')).sendKeys('admin@selenium.dev');
await driver.findElement(By.id('submitButton')).click();
console.log(await driver.findElement(By.id('out')).getText());
await driver.switchTo().defaultContent();
console.log(await driver.findElement(By.tagName('h1')).getText());
await driver.quit();`
      }
    },
    elements: {
      title: 'Try it: act on elements and read them back',
      sub: 'Try clearing the disabled input, or typing into the readonly one, to meet the invalid element state error.',
      code: {
        py: `driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/web-form.html")
box = driver.find_element(By.ID, "my-text-id")
box.send_keys("hello")
print(box.get_attribute("value"))
box.clear()
print(box.get_dom_attribute("myprop"))
check = driver.find_element(By.ID, "my-check-2")
check.click()
print(check.is_selected())
Select(driver.find_element(By.NAME, "my-select")).select_by_visible_text("Two")
print(driver.find_element(By.NAME, "my-disabled").is_enabled())
driver.quit()`,
        java: `WebDriver driver = new ChromeDriver();
driver.get("https://www.selenium.dev/selenium/web/web-form.html");
WebElement box = driver.findElement(By.id("my-text-id"));
box.sendKeys("hello");
System.out.println(box.getAttribute("value"));
box.clear();
System.out.println(box.getDomAttribute("myprop"));
WebElement check = driver.findElement(By.id("my-check-2"));
check.click();
System.out.println(check.isSelected());
new Select(driver.findElement(By.name("my-select"))).selectByVisibleText("Two");
System.out.println(driver.findElement(By.name("my-disabled")).isEnabled());
driver.quit();`,
        js: `let driver = await new Builder().forBrowser(Browser.CHROME).build();
await driver.get('https://www.selenium.dev/selenium/web/web-form.html');
let box = await driver.findElement(By.id('my-text-id'));
await box.sendKeys('hello');
console.log(await box.getAttribute('value'));
await box.clear();
console.log(await box.getDomAttribute('myprop'));
let check = await driver.findElement(By.id('my-check-2'));
await check.click();
console.log(await check.isSelected());
await new Select(await driver.findElement(By.name('my-select'))).selectByVisibleText('Two');
console.log(await driver.findElement(By.name('my-disabled')).isEnabled());
await driver.quit();`
      }
    }
  };

  function mountAll(root = document) { root.querySelectorAll('.sp[data-sp]').forEach(mount); }
  const obs = () => mountAll();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', obs); else obs();
  /* lessons are hidden until opened, so mount again when a lesson appears */
  new MutationObserver(() => mountAll()).observe(document.documentElement, { subtree: true, attributes: true, attributeFilter: ['hidden'] });
  return { mount, mountAll, SCEN, PAGES, parse };
})();
