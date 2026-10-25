/* ===== Playwright chapters: the language switch and the Playwright animations =====
   PW.page() runs after JSPLAY.page(). It sets the reader's language (Java, Python, JavaScript or TypeScript) on every
   four language code block, walk and playground, and mounts the labs (assets/pwplay.js).

   Animations, added to the shared VIZ widgets:
     <div class="viz" data-viz="pwwalk" data-walk="{...}">   a recorded run, one line at a time, with a real screenshot per line
     <div class="viz" data-viz="pwarch">                     how one line of a test travels: your code, the client, the driver, the browser
     <div class="viz" data-viz="pwloc">                      locator lab: type a locator and see what it matches, strict mode included
     <div class="viz" data-viz="pwact">                      auto-waiting: switch the button's problems on and off and watch the checks
     <div class="viz" data-viz="pwctx">                      browsers, contexts and pages: build them and see what each one shares
     <div class="viz" data-viz="pwpar">                      workers, fullyParallel and shards: a timeline of where each test runs
     <div class="viz" data-viz="pwretry">                    retries and flaky tests, run many times with a chosen failure rate
     <div class="viz" data-viz="pwnet">                      page.route: pick what happens to each request and watch the page
     <div class="viz" data-viz="pwtree" data-k="key">        a project explorer: click a file to see it and why it is there (PAGE.trees[key])
     <div class="viz" data-viz="pwtime">                     the timeouts that wrap a test, one inside another */
const PW = (() => {
  const K = VIZ.kit, W = VIZ.widgets, esc = K.esc, $ = K.$;
  const L4 = { java: ['☕', 'Java'], py: ['🐍', 'Python'], js: ['🟨', 'JavaScript'], ts: ['🔷', 'TypeScript'] };
  const listeners = [];
  let lang = 'ts';
  try { const v = localStorage.getItem('pw-lang'); if (L4[v]) lang = v; } catch (e) { /* storage unavailable */ }
  const hlLang = l => (l === 'py' ? 'py' : l === 'java' ? 'java' : l === 'ts' ? 'ts' : 'js');
  const hl = (code, l) => (typeof LEARN !== 'undefined' && LEARN.hl ? LEARN.hl(code, hlLang(l)) : esc(code));
  function setLang(l, save = true) {
    if (!L4[l]) return;
    lang = l;
    document.body.dataset.pwl = l;
    document.querySelectorAll('.pw-pick button').forEach(b => b.classList.toggle('on', b.dataset.l === l));
    document.querySelectorAll('.pw4').forEach(showPane);
    listeners.forEach(f => f(l));
    if (save) { try { localStorage.setItem('pw-lang', l); } catch (e) { /* storage unavailable */ } }
  }
  function showPane(w) {
    const panes = [...w.querySelectorAll(':scope > .pw-pane')];
    if (!panes.length) return;
    const pick = panes.find(p => p.dataset.l === lang) || panes[0];
    panes.forEach(p => p.classList.toggle('on', p === pick));
    w.querySelectorAll(':scope > .pw-tabs .pw-tab').forEach(t => { t.classList.toggle('on', t.dataset.l === pick.dataset.l); t.setAttribute('aria-selected', t.dataset.l === pick.dataset.l); });
    const b = w.querySelector(':scope > .codebar .pw-badge');
    if (b) b.textContent = pick.dataset.badge || '';
  }
  function page() {
    document.body.dataset.pwl = lang;
    document.addEventListener('click', e => {
      const t = e.target.closest('.pw-tab, .pw-pick button');
      if (t) { setLang(t.dataset.l); return; }
      const c = e.target.closest('.pw4 .codebar .copy');
      if (c) {
        e.stopImmediatePropagation();
        const pane = c.closest('.pw4').querySelector('.pw-pane.on') || c.closest('.pw4').querySelector('.pw-pane');
        const txt = [...pane.querySelectorAll('pre.src')].map(p => p.textContent).join('\n\n');
        const done = () => { c.textContent = 'Copied'; setTimeout(() => { c.textContent = 'Copy'; }, 1200); };
        if (navigator.clipboard) navigator.clipboard.writeText(txt).then(done, done); else done();
      }
    }, true);
    setLang(lang, false);
    if (typeof PWPLAY !== 'undefined') PWPLAY.mountLabs();
    if (typeof VIZ !== 'undefined') VIZ.mountAll(document);
  }

  /* ---------- pwwalk: a recorded run, line by line ---------- */
  W.pwwalk = el => {
    const d = JSON.parse(el.dataset.walk);
    const b = K.shell(el, '🎥 ' + esc(d.title), el.dataset.sub || 'Step through a real recorded run.');
    el.querySelector('.vz-badge').textContent = '🎥 Recorded run';
    b.innerHTML = `<div class="pww-langs" role="group" aria-label="Language">${Object.entries(L4).map(([k, v]) => `<button type="button" data-wl="${k}">${v[0]} ${v[1]}</button>`).join('')}</div>
      <div class="pww"><pre class="pww-code"></pre><div class="pww-shot"><div class="pww-bar"><i></i><i></i><i></i><span></span></div><img alt="" loading="lazy"></div></div>
      <div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const code = $('.pww-code', b), img = $('.pww-shot img', b), msg = $('.vz-msg', b), bar = $('.pww-bar span', b);
    let at = 0, wl = lang;
    const draw = () => {
      b.querySelectorAll('[data-wl]').forEach(x => x.classList.toggle('on', x.dataset.wl === wl));
      let n = 0;
      code.innerHTML = d.steps.map((s, i) => s[wl].split('\n').map(line => `<div data-i="${i}" class="${i === at ? 'on' : i < at ? 'done' : ''}"><span class="ln">${++n}</span>${hl(line, wl)}</div>`).join('')).join('');
      const on = code.querySelector('.on');
      if (on) code.scrollTop = Math.max(0, on.offsetTop - code.clientHeight / 2);
    };
    const show = i => {
      at = i;
      const s = d.steps[i];
      img.src = s.img ? s.img : '';
      img.alt = `The shop after step ${i + 1}: ${s.cap}`;
      bar.textContent = `after line ${i + 1} of ${d.steps.length}`;
      msg.innerHTML = `<b>Step ${i + 1} of ${d.steps.length}.</b> ${s.cap}`;
      const cnt = el.querySelector('.vz-cnt');
      if (cnt) cnt.textContent = `${i + 1} / ${d.steps.length}`;
      draw();
    };
    b.addEventListener('click', e => {
      const x = e.target.closest('[data-wl]');
      if (x) { wl = x.dataset.wl; draw(); return; }
      const ln = e.target.closest('.pww-code div[data-i]');
      if (ln) P.load(d.steps.length, +ln.dataset.i);
    });
    listeners.push(l => { wl = l; draw(); });
    const P = K.Player($('.vz-p', b), show, 1900);
    P.load(d.steps.length);
  };

  /* ---------- pwarch: one line of a test, from your code to the browser ---------- */
  const ARCH = {
    java: { code: 'page.getByRole(AriaRole.BUTTON,\n  new Page.GetByRoleOptions().setName("Sign in")).click();', client: 'Playwright for Java (the jar)', pipe: 'a pipe to the driver process' },
    py: { code: 'page.get_by_role("button", name="Sign in").click()', client: 'playwright Python package', pipe: 'a pipe to the driver process' },
    js: { code: "await page.getByRole('button', { name: 'Sign in' }).click();", client: 'playwright npm package', pipe: 'a direct call inside the same Node.js process' },
    ts: { code: "await page.getByRole('button', { name: 'Sign in' }).click();", client: 'playwright npm package', pipe: 'a direct call inside the same Node.js process' },
  };
  const BROWSER = {
    chromium: ['Chromium, Chrome or Edge', 'Chrome DevTools Protocol (CDP)', 'Input.dispatchMouseEvent {"type":"mousePressed","x":440,"y":358,"button":"left","clickCount":1}'],
    firefox: ['Firefox (a Playwright build)', 'Juggler, a protocol Playwright adds to its Firefox build', 'Page.dispatchMouseEvent {"type":"mousedown","x":440,"y":358,"button":0}'],
    webkit: ['WebKit (a Playwright build, the engine of Safari)', 'the WebKit inspector protocol, extended by Playwright', 'Input.dispatchMouseEvent {"type":"down","x":440,"y":358,"button":"left"}'],
  };
  W.pwarch = el => {
    const b = K.shell(el, 'How one line of your test reaches the browser', 'Pick your language and a browser, then press Play. Every message below has the shape Playwright 1.63 really sends, captured with DEBUG=pw:channel and DEBUG=pw:protocol.');
    b.innerHTML = `<div class="pwv-row">${K.seg('lang', Object.entries(L4).map(([k, v]) => [k, v[0] + ' ' + v[1]]), lang)}${K.seg('br', [['chromium', 'Chromium'], ['firefox', 'Firefox'], ['webkit', 'WebKit']], 'chromium')}</div>
      <div class="pwv-arch"></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const box = $('.pwv-arch', b), msg = $('.vz-msg', b);
    let L = lang, B = 'chromium';
    const STEPS = () => {
      const a = ARCH[L], br = BROWSER[B];
      const inproc = L === 'js' || L === 'ts';
      return [
        ['code', `Your test calls <code>click()</code> on a locator. Nothing has touched the browser yet. A locator is only a description of how to find the element.`],
        ['client', `The ${esc(a.client)} turns the call into a small JSON message. The locator becomes a selector string the driver understands: <code>internal:role=button[name="Sign in"i]</code>. The <code>i</code> means the name is matched ignoring case.`],
        ['wire', inproc ? 'In JavaScript and TypeScript the client and the driver live in the same Node.js process, so the message is handed over directly.' : `Java and Python start the Playwright driver, a small Node.js program shipped inside the package, and talk to it over ${esc(a.pipe)}. This is why the same features arrive in every language at the same time.`],
        ['driver', 'The driver resolves the locator in the page and runs the actionability checks: the button must be attached, visible, stable, enabled and not covered by another element. If a check fails it waits and tries again until the timeout.'],
        ['proto', `The driver speaks the browser's own protocol: ${esc(br[1])}. It moves the mouse to the middle of the button, presses and releases it.`],
        ['browser', `${esc(br[0])} receives real mouse events, exactly as if a person clicked. The page's JavaScript runs its click handler.`],
        ['back', 'The answer travels back the same way. Your <code>click()</code> returns (or the promise resolves), and the next line of the test runs.'],
      ];
    };
    const draw = f => {
      const a = ARCH[L], br = BROWSER[B], st = STEPS();
      const on = f ? st[f - 1][0] : '';
      const inproc = L === 'js' || L === 'ts';
      const node = (id, title, body, tone) => `<div class="pwa-n${on === id || (on === 'back' && id !== 'proto') ? ' on' : ''}" style="--t:${tone}"><b>${title}</b><div>${body}</div></div>`;
      const arrow = (id, t) => `<div class="pwa-a${on === id ? ' on' : ''}"><span>${t}</span></div>`;
      box.innerHTML = `<div class="pwa">
        ${node('code', '1. Your test', `<pre>${hl(a.code, L)}</pre>`, 'var(--blue)')}
        ${arrow('client', on === 'back' ? '⬆ returns' : '⬇ method call')}
        ${node('client', '2. Client library', `${esc(a.client)}<pre class="pwa-msg">SEND&gt; {"guid":"frame@14a3…","method":"click",\n  "params":{"selector":"internal:role=button[name=\\"Sign in\\"i]",\n  "strict":true}}</pre>`, 'var(--purple)')}
        ${arrow('wire', inproc ? '⬇ same process' : '⬇ JSON over a pipe')}
        ${node('driver', '3. Playwright driver (Node.js)', 'finds the element, waits until it is ready<div class="pwa-checks"><span>attached</span><span>visible</span><span>stable</span><span>enabled</span><span>receives events</span></div>', 'var(--green)')}
        ${arrow('proto', '⬇ ' + esc(br[1]))}
        ${node('proto', '4. Browser protocol', `<pre class="pwa-msg">SEND ► ${esc(br[2])}</pre>`, 'var(--orange)')}
        ${arrow('browser', '⬇ real input events')}
        ${node('browser', '5. ' + esc(br[0]), 'runs the click handler of <b>Sign in</b>', 'var(--pink)')}
      </div>`;
      msg.innerHTML = f ? `<b>Step ${f} of ${st.length}.</b> ${st[f - 1][1]}` : 'Press ▶ Play to follow one click through every layer.';
    };
    const P = K.Player($('.vz-p', b), draw, 2300);
    K.wireSeg(b, 'lang', v => { L = v; P.load(8, P.i); });
    K.wireSeg(b, 'br', v => { B = v; P.load(8, P.i); });
    P.load(8);
  };

  /* ---------- pwloc: the locator lab ---------- */
  const LOC_PAGE = `<h4>Products</h4>
<label>Search <input type="search" placeholder="Search products"></label>
<ul aria-label="Products">
  <li data-testid="product-1"><span>Gel pen ₹20</span><button>Add to cart</button></li>
  <li data-testid="product-2"><span>Coffee mug ₹199</span><button>Add to cart</button></li>
  <li data-testid="product-4"><span>Notebook ₹60</span><button disabled>Out of stock</button></li>
</ul>
<p>Need help? <a href="#help" title="Help centre">Contact us</a></p>
<img alt="Brainy Shop logo" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='24'%3E%3Crect width='60' height='24' rx='6' fill='%2316a34a'/%3E%3C/svg%3E">
<button class="checkout" style="margin-left:8px">Checkout</button>`;
  const LOC_EXAMPLES = {
    js: ["page.getByRole('button', { name: 'Add to cart' })", "page.getByRole('button', { name: 'Add to cart' }).nth(1)", "page.getByTestId('product-2').getByRole('button')", "page.getByRole('listitem').filter({ hasText: 'mug' })", "page.getByText('Notebook')", "page.getByLabel('Search')", "page.getByPlaceholder('Search products')", "page.getByAltText('Brainy Shop logo')", "page.getByTitle('Help centre')", "page.locator('li >> text=pen')", "page.locator('.checkout')", "page.locator('//button[text()=\"Checkout\"]')", "page.getByRole('button', { disabled: true })", "page.getByRole('link', { name: 'Contact us' })"],
    py: ['page.get_by_role("button", name="Add to cart")', 'page.get_by_role("button", name="Add to cart").nth(1)', 'page.get_by_test_id("product-2").get_by_role("button")', 'page.get_by_role("listitem").filter(has_text="mug")', 'page.get_by_text("Notebook")', 'page.get_by_label("Search")', 'page.locator(".checkout")'],
    java: ['page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Add to cart"))', 'page.getByRole(AriaRole.LISTITEM).filter(new Locator.FilterOptions().setHasText("mug"))', 'page.getByTestId("product-2").getByRole(AriaRole.BUTTON)', 'page.getByText("Notebook")', 'page.locator(".checkout")'],
  };
  W.pwloc = el => {
    const b = K.shell(el, 'Locator lab', 'Type a locator in any of the four languages, or pick an example. Matches light up on the page. Green means exactly one element, which is what an action needs. Orange means several, which is a strict mode error for click or fill.');
    b.innerHTML = `<div class="pwv-row"><input class="pwv-in" aria-label="Your locator" spellcheck="false"><button type="button" class="pwv-btn go" data-a="go">Find</button></div>
      <div class="pwv-row" data-ex></div>
      <div class="pwv-grid2"><div class="pwv-page"><div class="pwv-url"><i></i><i></i><i></i>localhost:4173/products</div><div class="pwv-doc">${LOC_PAGE}</div></div><pre class="pwv-log" aria-live="polite"></pre></div>`;
    const inp = $('.pwv-in', b), out = $('.pwv-log', b), doc = $('.pwv-doc', b);
    let exL = lang === 'ts' ? 'js' : lang;
    const exs = () => { const l = LOC_EXAMPLES[exL] || LOC_EXAMPLES.js; $('[data-ex]', b).innerHTML = '<span class="pwv-chip">Try</span>' + l.map((x, k) => `<button type="button" class="pwv-btn" data-k="${k}">${esc(x.replace(/^page\./, '').slice(0, 46))}${x.length > 52 ? '…' : ''}</button>`).join(''); };
    exs();
    const engine = () => PWPLAY.engine;
    function run() {
      doc.querySelectorAll('.pwv-match,.pwv-one').forEach(x => x.classList.remove('pwv-match', 'pwv-one'));
      const src = inp.value.trim();
      if (!src) return;
      const guess = /get_by_|has_text=/.test(src) ? 'py' : /AriaRole\.|new \w+\.\w+Options/.test(src) ? 'java' : 'js';
      try {
        const st = PWPLAY.parse(src, guess)[0];
        if (!st || st.k === 'error') throw new Error(st ? st.msg : 'Type a locator');
        const fakePage = { _doc: () => ({ querySelectorAll: s => doc.querySelectorAll(s), nodeType: 9, evaluate: (x, r, ns, t) => document.evaluate(x, doc, ns, t, null), ownerDocument: document }) };
        const rootLoc = new (engine().Locator)(fakePage, []);
        const pageObj = {};
        ['getByRole', 'getByText', 'getByLabel', 'getByPlaceholder', 'getByAltText', 'getByTitle', 'getByTestId', 'locator'].forEach(m => { pageObj[m] = (...a) => rootLoc[m](...a); });
        const rt = { page: pageObj, log() {}, used: [] };
        const I = PWPLAY.makeInterp(rt, guess);
        I.env.page = pageObj;
        I.env.Page = pageObj;
        Promise.resolve(I.run({ k: 'let', name: '__x', e: st.e })).then(() => {
          const loc = I.env.__x;
          if (!loc || !loc._resolve) throw new Error('That is not a locator');
          const els = loc._resolve();
          els.forEach(x => x.classList.add(els.length === 1 ? 'pwv-one' : 'pwv-match'));
          out.innerHTML = `<span class="dim">${esc(guess === 'py' ? '🐍 read as Python' : guess === 'java' ? '☕ read as Java' : '🟨 read as JavaScript or TypeScript')}</span>\n` +
            `<b>${esc(String(loc))}</b>\n` + (els.length === 1 ? `<span class="ok">✓ exactly 1 element: &lt;${els[0].tagName.toLowerCase()}&gt; "${esc(engine().textOf(els[0]).trim().slice(0, 40))}"\n  click(), fill() and expect() can all use it.</span>`
              : els.length ? `<span class="wait">⚠ ${els.length} elements match.\n  count() and toHaveCount() are fine, but click() would fail:\n  strict mode violation: resolved to ${els.length} elements.\n  Add a name, filter(), or nth() to pick one.</span>`
                : '<span class="bad">✗ nothing matches.\n  An action would wait for it, then time out.</span>');
        }).catch(e => { out.innerHTML = `<span class="bad">✗ ${esc(e.message)}</span>`; });
      } catch (e) { out.innerHTML = `<span class="bad">✗ ${esc(e.message)}</span>`; }
    }
    b.addEventListener('click', e => {
      const x = e.target.closest('[data-k]');
      if (x) { inp.value = (LOC_EXAMPLES[exL] || LOC_EXAMPLES.js)[+x.dataset.k]; run(); }
      if (e.target.closest('[data-a=go]')) run();
    });
    doc.addEventListener('click', e => e.preventDefault());
    inp.addEventListener('keydown', e => { if (e.key === 'Enter') run(); });
    listeners.push(l => { exL = l === 'ts' ? 'js' : l; exs(); });
    inp.value = (LOC_EXAMPLES[exL] || LOC_EXAMPLES.js)[0];
    setTimeout(run, 50);
  };

  /* ---------- pwact: the actionability checks ---------- */
  W.pwact = el => {
    const b = K.shell(el, 'Auto-waiting: what click() checks before it clicks', 'Give the Pay button some problems, then press click(). Playwright retries every check until all pass or the timeout ends. Problems marked with a clock fix themselves after the time you choose, like a real slow page.');
    const PROBS = [['missing', 'Not in the page yet', 'attached'], ['hidden', 'Hidden (display: none)', 'visible'], ['moving', 'Still sliding in', 'stable'], ['disabled', 'Disabled', 'enabled'], ['covered', 'Covered by a loading overlay', 'receives events']];
    b.innerHTML = `<div class="pwv-row">${PROBS.map(([k, t]) => `<label class="vz-sl"><input type="checkbox" data-p="${k}"> ${t}</label>`).join('')}</div>
      <div class="pwv-row">${K.slider('fix', 'The problems fix themselves after', 0, 8000, 1500, 250)} ms ${K.slider('to', 'timeout', 1000, 8000, 5000, 500)} ms</div>
      <div class="pwv-checks">${PROBS.map(([k, , c]) => `<div class="pwv-check na" data-c="${k}">${c}<small>not checked yet</small></div>`).join('')}</div>
      <div class="pwv-time"><b style="width:0"></b><span>0 ms</span></div>
      <div class="pwv-row"><button type="button" class="pwv-btn go" data-a="click">▶ click()</button></div>
      <div class="pwv-grid2"><div class="pwv-page"><div class="pwv-url"><i></i><i></i><i></i>localhost:4173/widgets</div><div class="pwv-doc" style="position:relative;min-height:120px"><p>Total: ₹219</p><span data-btn></span><div data-cover style="position:absolute;inset:0;background:rgba(15,23,42,.55);color:#fff;display:none;place-items:center;font-weight:700">Loading…</div></div></div><pre class="pwv-log" aria-live="polite">Pick some problems and press click().</pre></div>`;
    const log = $('.pwv-log', b), bar = $('.pwv-time b', b), barT = $('.pwv-time span', b);
    let timer = null;
    const prob = () => Object.fromEntries(PROBS.map(([k]) => [k, $(`[data-p=${k}]`, b).checked]));
    function paint(p, t) {
      const btnHost = $('[data-btn]', b);
      btnHost.innerHTML = p.missing ? '' : `<button type="button" ${p.disabled ? 'disabled' : ''} style="${p.hidden ? 'display:none;' : ''}${p.moving ? `position:relative;left:${Math.max(0, 140 - t / 10)}px;` : ''}">Pay now</button>`;
      $('[data-cover]', b).style.display = p.covered ? 'grid' : 'none';
    }
    paint(prob(), 0);
    b.addEventListener('change', () => { clearInterval(timer); paint(prob(), 0); });
    b.addEventListener('click', e => {
      if (!e.target.closest('[data-a=click]')) return;
      clearInterval(timer);
      const start = prob(), fix = +$('[data-sl=fix]', b).value, to = +$('[data-sl=to]', b).value;
      let t = 0;
      const lines = ["→ page.getByRole('button', { name: 'Pay now' }).click()"];
      let last = '';
      timer = setInterval(() => {
        t += 100;
        const now = Object.fromEntries(Object.entries(start).map(([k, v]) => [k, v && t < fix]));
        paint(now, t);
        const order = ['missing', 'hidden', 'moving', 'disabled', 'covered'];
        let fail = null;
        order.forEach((k, i) => {
          const c = $(`[data-c=${k}]`, b);
          const earlier = order.slice(0, i).some(x => now[x]);
          if (earlier) { c.className = 'pwv-check na'; c.querySelector('small').textContent = 'waits for the check before'; return; }
          c.className = 'pwv-check ' + (now[k] ? 'bad' : 'ok');
          c.querySelector('small').textContent = now[k] ? 'not yet, retrying' : 'passed';
          if (now[k] && !fail) fail = k;
        });
        bar.style.width = Math.min(100, (t / to) * 100) + '%';
        barT.textContent = `${t} ms of ${to} ms`;
        const why = { missing: 'waiting for the element to be attached', hidden: 'element is not visible', moving: 'element is not stable', disabled: 'element is not enabled', covered: '<div> intercepts pointer events' };
        if (fail && why[fail] !== last) { lines.push(`  - ${why[fail]}, retrying…`); last = why[fail]; }
        if (!fail) {
          clearInterval(timer);
          lines.push(`  - all checks passed after ${t} ms`, '  - clicking the middle of the button', '✓ done. No sleep was needed and none was wasted.');
          log.innerHTML = lines.map((x, k) => `<span class="${k === lines.length - 1 ? 'ok' : x.includes('retrying') ? 'wait' : ''}">${esc(x)}</span>`).join('\n');
          const btn = b.querySelector('[data-btn] button');
          if (btn) { btn.textContent = 'Paid ✓'; }
          return;
        }
        if (t >= to) {
          clearInterval(timer);
          lines.push(`✗ TimeoutError: locator.click: Timeout ${to}ms exceeded.`, '  The last check that failed is named in the call log, which is how you find the cause.');
        }
        log.innerHTML = lines.map(x => `<span class="${x.startsWith('✗') ? 'bad' : x.includes('retrying') ? 'wait' : ''}">${esc(x)}</span>`).join('\n');
      }, 100);
    });
  };

  /* ---------- pwctx: browser, contexts and pages ---------- */
  W.pwctx = el => {
    const b = K.shell(el, 'Browser, contexts and pages', 'One browser can hold many contexts. A context is like a fresh incognito profile with its own cookies and storage. Sign a context in, open pages, and see what is shared.');
    b.innerHTML = `<div class="pwv-row"><button type="button" class="pwv-btn go" data-a="ctx">➕ browser.newContext()</button><button type="button" class="pwv-btn" data-a="reset">↺ Close everything</button></div>
      <div class="pwv-browser"><h5>🧭 Browser (one Chromium process, started once by browserType.launch())</h5><div class="pwv-ctxs"></div></div><div class="vz-msg" aria-live="polite"></div>`;
    const host = $('.pwv-ctxs', b), msg = $('.vz-msg', b);
    let ctxs = [], n = 0;
    const draw = (fresh) => {
      host.innerHTML = ctxs.map((c, i) => `<div class="pwv-ctx${fresh === i ? ' pwv-new' : ''}"><h5>🗂️ Context ${c.id}</h5>
        <div class="pwv-store">cookies: ${c.user ? `session=${c.user.toLowerCase()}…` : '(none)'}<br>localStorage: ${c.user ? `token for ${c.user}` : '(empty)'}</div>
        <div class="pwv-tabs">${c.pages.map(p => `<span>📄 page ${p}${c.user ? ' · Hello, ' + c.user : ''}</span>`).join('')}</div>
        <div class="pwv-row"><button type="button" class="pwv-btn" data-a="page" data-i="${i}">➕ newPage()</button>${c.user ? '' : `<button type="button" class="pwv-btn" data-a="login" data-i="${i}" data-u="Asha">Sign in as Asha</button><button type="button" class="pwv-btn" data-a="login" data-i="${i}" data-u="Ravi">Sign in as Ravi</button>`}<button type="button" class="pwv-btn" data-a="close" data-i="${i}">✕ close()</button></div></div>`).join('') || '<p class="muted">No contexts yet. Press browser.newContext().</p>';
    };
    b.addEventListener('click', e => {
      const x = e.target.closest('[data-a]');
      if (!x) return;
      const i = +x.dataset.i, a = x.dataset.a;
      if (a === 'ctx') { ctxs.push({ id: ++n, user: null, pages: [] }); msg.innerHTML = `A new context starts empty: no cookies, no storage, no pages. Creating one takes a few milliseconds, so every test can have its own. Playwright Test does exactly this for each test.`; draw(ctxs.length - 1); return; }
      if (a === 'reset') { ctxs = []; n = 0; msg.innerHTML = 'Closing the browser closes every context and page inside it.'; draw(); return; }
      const c = ctxs[i];
      if (a === 'page') { c.pages.push(c.pages.length + 1); msg.innerHTML = c.user ? `The new page in context ${c.id} is already signed in as ${c.user}, because pages in one context share cookies and storage, like tabs in one browser window.` : `Context ${c.id} now has ${c.pages.length} page(s). Pages in one context share everything, like tabs in one profile.`; }
      if (a === 'login') { c.user = x.dataset.u; if (!c.pages.length) c.pages.push(1); msg.innerHTML = `Only context ${c.id} is signed in as ${c.user}. ${ctxs.length > 1 ? 'The other contexts are untouched, so one test can never leak a login into another.' : 'Add a second context and sign in as someone else: this is how you test a chat between two people in one test.'}`; }
      if (a === 'close') { ctxs.splice(i, 1); msg.innerHTML = 'context.close() throws away its cookies, storage and pages. Nothing is left for the next test.'; }
      draw();
    });
    draw();
  };

  /* ---------- pwpar: workers, fullyParallel and shards ---------- */
  W.pwpar = el => {
    const b = K.shell(el, 'Workers, fully parallel and shards', 'Change the settings and see how 4 test files with 3 tests each are spread out. Each test takes the seconds shown on it.');
    b.innerHTML = `<div class="pwv-row">${K.slider('w', 'workers', 1, 6, 2)}${K.slider('s', 'shards (machines)', 1, 3, 1)}<label class="vz-sl"><input type="checkbox" data-fp> fullyParallel: true</label></div>
      <div class="pwv-lanes"></div><div class="vz-msg" aria-live="polite"></div>`;
    const FILES = [['login', [4, 3, 3]], ['cart', [6, 5, 4]], ['search', [2, 2, 2]], ['checkout', [8, 7, 6]]];
    const COLS = ['var(--g0)', 'var(--g1)', 'var(--g2)', 'var(--g3)'];
    const draw = () => {
      const W_ = +$('[data-sl=w]', b).value, S = +$('[data-sl=s]', b).value, fp = $('[data-fp]', b).checked;
      // units of work: a whole file, or each test when fully parallel
      let units = [];
      FILES.forEach(([f, ts], fi) => { if (fp) ts.forEach((t, k) => units.push({ label: `${f} ${k + 1}`, secs: t, c: COLS[fi] })); else units.push({ label: f, secs: ts.reduce((a, x) => a + x, 0), parts: ts, c: COLS[fi] }); });
      // shards split the units into S nearly equal groups, in order
      const per = Math.ceil(units.length / S);
      const shards = Array.from({ length: S }, (_, k) => units.slice(k * per, k * per + per));
      let rows = '', worst = 0;
      shards.forEach((us, si) => {
        const lanes = Array.from({ length: W_ }, () => ({ t: 0, jobs: [] }));
        us.forEach(u => { const l = lanes.reduce((a, x) => (x.t < a.t ? x : a)); l.jobs.push({ ...u, at: l.t }); l.t += u.secs; });
        const end = Math.max(...lanes.map(l => l.t));
        worst = Math.max(worst, end);
        lanes.forEach((l, li) => { rows += `<div class="pwv-lane"><span>${S > 1 ? `shard ${si + 1}/${S}<br>` : ''}worker ${li}</span><div class="pwv-track" data-end="${l.t}">${l.jobs.map(j => `<div class="pwv-job" style="left:calc(${j.at} * var(--u));width:calc(${j.secs} * var(--u) - 2px);background:${j.c}" title="${esc(j.label)} ${j.secs} s">${esc(j.label)} ${j.secs}s</div>`).join('')}</div></div>`; });
      });
      const total = FILES.reduce((a, [, ts]) => a + ts.reduce((x, y) => x + y, 0), 0);
      const lanesEl = $('.pwv-lanes', b);
      lanesEl.style.setProperty('--u', `calc((100% ) / ${Math.max(total / Math.min(W_ * S, 1) / 1, 1)})`);
      lanesEl.innerHTML = rows;
      lanesEl.querySelectorAll('.pwv-track').forEach(t => t.style.setProperty('--u', `calc(100% / ${total})`));
      $('.vz-msg', b).innerHTML = `One worker alone would need <b>${total} s</b>. With these settings the run ends after <b>${worst} s</b>${S > 1 ? ' (the slowest shard decides)' : ''}. ${fp ? 'With fullyParallel every test is a separate piece of work, so the load is spread evenly.' : 'Without fullyParallel a whole file goes to one worker, so the long checkout file holds one worker for ' + FILES[3][1].reduce((a, x) => a + x, 0) + ' s.'}`;
    };
    b.addEventListener('input', draw);
    b.addEventListener('change', draw);
    draw();
  };

  /* ---------- pwretry: retries and flaky tests ---------- */
  W.pwretry = el => {
    const b = K.shell(el, 'Retries and flaky tests', 'A flaky test fails now and then for no real reason. Pick how often it fails and how many retries you allow, then run the suite 20 times.');
    b.innerHTML = `<div class="pwv-row">${K.slider('p', 'fails on', 0, 60, 15, 5)}% of runs ${K.slider('r', 'retries', 0, 3, 1)}<button type="button" class="pwv-btn go" data-a="go">▶ Run 20 times</button></div><div class="pwv-row" data-runs></div><div class="vz-msg" aria-live="polite"></div>`;
    b.addEventListener('click', e => {
      if (!e.target.closest('[data-a=go]')) return;
      const p = +$('[data-sl=p]', b).value / 100, r = +$('[data-sl=r]', b).value;
      let passed = 0, flaky = 0, failed = 0;
      const chips = [];
      for (let k = 0; k < 20; k++) {
        let tries = 0, ok = false;
        while (tries <= r && !ok) { ok = Math.random() >= p; tries++; }
        const kind = ok ? (tries > 1 ? 'flaky' : 'passed') : 'failed';
        if (kind === 'passed') passed++; else if (kind === 'flaky') flaky++; else failed++;
        chips.push(`<span class="pwv-chip ${kind === 'passed' ? 'pwv-ok' : kind === 'flaky' ? 'pwv-wait' : 'pwv-bad'}" title="${tries} attempt(s)">${kind === 'passed' ? '✓' : kind === 'flaky' ? '⚠' : '✗'} ${tries}</span>`);
      }
      $('[data-runs]', b).innerHTML = chips.join('');
      const chance = (Math.pow(p, r + 1) * 100).toFixed(2);
      $('.vz-msg', b).innerHTML = `<b>${passed}</b> passed first time, <b>${flaky}</b> flaky (failed, then passed on a retry), <b>${failed}</b> failed every attempt. With ${r} retr${r === 1 ? 'y' : 'ies'} the chance that one run still fails is ${(p * 100).toFixed(0)}% to the power ${r + 1}, about <b>${chance}%</b>. Retries hide the noise, but Playwright still reports every flaky test so the team can fix the real cause.`;
    });
  };

  /* ---------- pwnet: page.route ---------- */
  W.pwnet = el => {
    const b = K.shell(el, 'page.route: decide what happens to a request', 'The products page asks the server for GET /api/products. Choose what your route handler does with that request, then load the page.');
    const CH = [['none', 'No route (real server)'], ['fulfill', 'route.fulfill() with fake JSON'], ['empty', 'route.fulfill() with an empty list'], ['error', 'route.fulfill() with status 500'], ['abort', 'route.abort()'], ['slow', 'wait 3 s, then route.continue()']];
    b.innerHTML = `<div class="pwv-row">${K.seg('m', CH, 'fulfill')}</div><div class="pwv-row"><button type="button" class="pwv-btn go" data-a="go">▶ page.goto('/products')</button></div>
      <div class="pwv-grid2"><pre class="pwv-log" data-code></pre><div class="pwv-page"><div class="pwv-url"><i></i><i></i><i></i>localhost:4173/products</div><div class="pwv-doc" data-doc><p class="muted">Press the button to load the page.</p></div></div></div><pre class="pwv-log" data-net></pre>`;
    let mode = 'fulfill';
    const CODE = {
      none: '// no page.route(): the request goes to the real server',
      fulfill: "await page.route('**/api/products', route =>\n  route.fulfill({ json: [{ id: 9, name: 'Test teapot', price: 999 }] }));",
      empty: "await page.route('**/api/products', route =>\n  route.fulfill({ json: [] }));",
      error: "await page.route('**/api/products', route =>\n  route.fulfill({ status: 500, json: { error: 'down' } }));",
      abort: "await page.route('**/api/products', route => route.abort());",
      slow: "await page.route('**/api/products', async route => {\n  await new Promise(r => setTimeout(r, 3000));\n  await route.continue();\n});",
    };
    const showCode = () => { $('[data-code]', b).innerHTML = hl(CODE[mode], 'js'); };
    showCode();
    K.wireSeg(b, 'm', v => { mode = v; showCode(); });
    b.addEventListener('click', e => {
      if (!e.target.closest('[data-a=go]')) return;
      const doc = $('[data-doc]', b), net = $('[data-net]', b);
      doc.innerHTML = '<p class="muted">Loading products…</p>';
      net.innerHTML = '<span class="dim">→ GET /api/products</span>';
      const real = [['Gel pen', 20], ['Coffee mug', 199], ['Desk lamp', 1299]];
      const list = items => `<ul>${items.map(([n, p]) => `<li><span>${n}</span><b>₹${p}</b></li>`).join('')}</ul>`;
      const wait = mode === 'slow' ? 3600 : mode === 'none' ? 600 : 80;
      setTimeout(() => {
        const r = {
          none: ['200 from the real server (600 ms)', list(real)],
          fulfill: ['200 from your route, the server was never called', list([['Test teapot', 999]])],
          empty: ['200 with [], from your route', '<p>No products match your search</p>'],
          error: ['500 from your route', '<p role="alert" style="color:#b91c1c;font-weight:700">Something went wrong. Please try again.</p>'],
          abort: ['failed: net::ERR_FAILED (aborted by your route)', '<p class="muted">Loading products…</p><p style="color:#b91c1c">The page never got an answer. Does it show an error? This is the bug your test can now find.</p>'],
          slow: ['200 after 3.6 s (your route waited, then let it through)', list(real)],
        }[mode];
        doc.innerHTML = r[1];
        net.innerHTML += `\n<span class="${/500|failed/.test(r[0]) ? 'bad' : 'ok'}">← ${esc(r[0])}</span>`;
      }, wait);
    });
  };

  /* ---------- pwtree: a project explorer ---------- */
  W.pwtree = el => {
    const spec = (typeof PAGE !== 'undefined' && PAGE.trees && PAGE.trees[el.dataset.k]) || null;
    if (!spec) { el.textContent = 'Missing tree ' + el.dataset.k; return; }
    const b = K.shell(el, spec.t, spec.s || 'Click any file to open it and read why it is there.');
    el.querySelector('.vz-badge').textContent = '🗂️ Explore the project';
    b.innerHTML = `<div class="pwv-tree"><ul role="tree"></ul><div class="pwv-file"><div class="pwv-fh"></div><div class="pwv-fw"></div><pre></pre></div></div>`;
    const ul = $('ul', b), fh = $('.pwv-fh', b), fw = $('.pwv-fw', b), pre = $('pre', b);
    ul.innerHTML = spec.files.map((f, i) => {
      const depth = f.p.split('/').length - 1 - (f.p.endsWith('/') ? 1 : 0);
      const name = f.p.endsWith('/') ? f.p.split('/').slice(-2)[0] + '/' : f.p.split('/').pop();
      return `<li class="${f.p.endsWith('/') ? 'dir' : ''}" data-i="${i}" style="padding-left:${10 + depth * 16}px" role="treeitem">${f.p.endsWith('/') ? '📁' : '📄'} ${esc(name)}${f.why && f.p.endsWith('/') ? `<span class="why">${esc(f.why)}</span>` : ''}</li>`;
    }).join('');
    const open = i => {
      const f = spec.files[i];
      if (f.p.endsWith('/')) return;
      ul.querySelectorAll('li').forEach(x => x.classList.toggle('on', +x.dataset.i === i));
      fh.textContent = f.p;
      fw.innerHTML = f.why || '';
      const ext = f.p.split('.').pop();
      const hlx = { java: 'java', py: 'py', ts: 'ts', js: 'js', mjs: 'js', json: 'js' }[ext];
      pre.innerHTML = f.body ? (hlx ? hl(f.body, hlx) : esc(f.body)) : '<span class="dim">(this file is shown in the steps above)</span>';
    };
    ul.addEventListener('click', e => { const li = e.target.closest('li[data-i]'); if (li) open(+li.dataset.i); });
    const first = spec.files.findIndex(f => !f.p.endsWith('/') && f.body);
    if (first >= 0) open(first);
  };

  /* ---------- pwtime: the timeouts around a test ---------- */
  W.pwtime = el => {
    const b = K.shell(el, 'The timeouts that wrap a test', 'Each box is a timeout. Move the sliders and see which one ends the test first when the page is slow.');
    b.innerHTML = `<div class="pwv-row">${K.slider('slow', 'The page needs', 0, 40, 7)} s ${K.slider('test', 'test timeout', 5, 60, 30, 5)} s ${K.slider('exp', 'expect timeout', 1, 15, 5)} s ${K.slider('act', 'action timeout (0 = none)', 0, 20, 0)} s</div><div data-boxes></div><div class="vz-msg" aria-live="polite"></div>`;
    const draw = () => {
      const s = +$('[data-sl=slow]', b).value, T = +$('[data-sl=test]', b).value, E = +$('[data-sl=exp]', b).value, A = +$('[data-sl=act]', b).value;
      const actLimit = A || T;
      let verdict;
      if (s <= E && s <= actLimit && s <= T) verdict = `<b class="pwv-chip pwv-ok">passes</b> The page is ready after ${s} s, inside every limit.`;
      else if (A && s > A && A < T) verdict = `<b class="pwv-chip pwv-bad">fails</b> The click gives up after the action timeout of ${A} s.`;
      else if (s > E && E < T) verdict = `<b class="pwv-chip pwv-bad">fails</b> The click itself would wait, but the assertion that follows only retries for ${E} s. Raise the expect timeout, or wait for the right thing.`;
      else verdict = `<b class="pwv-chip pwv-bad">fails</b> The whole test hits its ${T} s test timeout first.`;
      $('[data-boxes]', b).innerHTML = `<div style="border:2px solid var(--purple);border-radius:14px;padding:8px"><b>test timeout ${T} s</b> (default 30 s, covers the test and its beforeEach hooks)
        <div style="border:2px solid var(--blue);border-radius:12px;padding:8px;margin-top:6px"><b>action timeout ${A ? A + ' s' : 'none'}</b> (click, fill... default none, so the test timeout limits them)</div>
        <div style="border:2px solid var(--green);border-radius:12px;padding:8px;margin-top:6px"><b>expect timeout ${E} s</b> (web first assertions, default 5 s)</div></div>`;
      $('.vz-msg', b).innerHTML = verdict;
    };
    b.addEventListener('input', draw);
    draw();
  };

  return { page, setLang, onLang: f => listeners.push(f), get lang() { return lang; } };
})();
