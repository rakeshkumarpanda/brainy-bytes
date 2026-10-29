/* ===== Selenium animations, one block per chapter. The framework is assets/cvviz.js.
   Every animation is declared with CVZ.def(name, spec), so every value it uses has a control the reader can change,
   and its "Try this" list suggests which values to change and what to look for. Facts come from the Selenium
   documentation (selenium.dev) and the W3C WebDriver specification. ===== */
const SEZ = (() => {
  const { D } = CVZ;
  const FONT = (o = {}) => `${o.b ? '800 ' : '600 '}${o.s || 13}px ${o.mono ? '"JetBrains Mono", monospace' : 'Nunito, system-ui, sans-serif'}`;
  function tw(g, s, o = {}) { g.save(); g.font = FONT(o); const w = g.measureText(String(s)).width; g.restore(); return w; }
  function rr(g, x, y, w, h, r, o = {}) {
    g.save(); g.beginPath();
    r = Math.max(0, Math.min(r, w / 2, h / 2));
    g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath();
    if (o.fill) { g.fillStyle = o.fill; g.fill(); }
    if (o.stroke) { g.strokeStyle = o.stroke; g.lineWidth = o.w || 1.5; if (o.dash) g.setLineDash(o.dash); g.stroke(); }
    g.restore();
  }
  /* write text that wraps at maxW. Returns the y of the next line */
  function wrap(g, s, x, y, maxW, o = {}) {
    const lh = o.lh || (o.s || 13) + 5;
    const words = String(s).split(/\s+/).filter(Boolean);
    let line = '';
    words.forEach(w => {
      const t = line ? line + ' ' + w : w;
      if (line && tw(g, t, o) > maxW) { D.text(g, line, x, y, o); y += lh; line = w; } else line = t;
    });
    if (line) { D.text(g, line, x, y, o); y += lh; }
    return y;
  }
  function fit(g, s, maxW, size = 13, o = {}) { let fs = size; while (fs > 8 && tw(g, s, Object.assign({}, o, { s: fs })) > maxW) fs -= 0.5; return fs; }
  /* a labelled box with a title and up to two wrapped lines */
  function box(g, z, x, y, w, h, title, sub, o = {}) {
    rr(g, x, y, w, h, 10, { fill: o.fill || z.col.surf, stroke: o.stroke || z.col.line, w: o.lw || 1.5, dash: o.dash });
    const fs = fit(g, title, w - 12, o.s || 13.5, { b: true });
    D.text(g, title, x + w / 2, y + (sub ? 20 : h / 2 + 5), { a: 'center', b: true, s: fs, c: o.c || z.col.ink });
    if (sub) wrap(g, sub, x + 8, y + 38, w - 16, { s: o.ss || 11.5, c: z.col.ink2, lh: 15 });
  }
  const ms = v => v >= 1000 ? (v / 1000).toFixed(v % 1000 ? 2 : 0).replace(/\.?0+$/, '') + ' s' : Math.round(v) + ' ms';
  return { tw, rr, wrap, fit, box, ms };
})();

(() => {
  const { def, D, esc } = CVZ;
  const { tw, rr, wrap, fit, box, ms } = SEZ;

  /* ---------------------------------------------------------------- Chapter 1.1: what Selenium is */
  const HISTORY = [
    ['2004', 'JavaScriptTestRunner', 'Jason Huggins at ThoughtWorks writes a JavaScript library that drives a page from inside the browser to test an internal time and expenses app. It becomes Selenium Core.'],
    ['RC', 'Selenium Remote Control', 'Core runs inside the page, so the browser same origin policy limits what it can reach. A driven mode that works around the policy grows into a standalone server with the Jetty web server built in: Selenium Remote Control. Tests in many languages can now drive Core.'],
    ['IDE', 'Selenium IDE', 'Shinya Kasatani wraps Core in a Firefox extension that records clicks and typing and plays them back.'],
    ['WebDriver', 'Simon Stewart builds WebDriver', 'Instead of JavaScript inside the page, WebDriver uses a separate client for each browser and drives it from outside, closer to a real user.'],
    ['2011', 'Selenium 2.0', 'Released 8 July 2011. WebDriver and Selenium merge. The WebDriver APIs for Java, C#, Python and Ruby are the new heart, and Grid 2 ships in the standalone server.'],
    ['2016', 'Selenium 3.0', 'Released 13 October 2016. The original Selenium Core implementation is removed. All major browser vendors now ship their own drivers.'],
    ['2018', 'W3C Recommendation', 'WebDriver becomes a W3C Recommendation on 5 June 2018. Browser automation now has an official, browser neutral standard.'],
    ['2021', 'Selenium 4.0', 'Released 13 October 2021. Only the W3C protocol is spoken, and it adds relative locators, network interception and basic authentication for Chromium and Firefox, and a rebuilt Grid. Later releases add Selenium Manager (4.6) and WebDriver BiDi.']
  ];
  def('se-timeline', {
    title: 'From a small JavaScript runner to a W3C standard',
    sub: 'Step through the history. Each step shows what changed and why it mattered.',
    W: 640, H: 300,
    params: [{ k: 'detail', label: 'Show the reason for each change', type: 'check', v: true }],
    tips: [{ t: 'Press Play and watch how the way Selenium talks to the browser moves from inside the page to outside it.', play: true }],
    steps: () => HISTORY.length - 1,
    startAtZero: true,
    draw(z) {
      const g = z.g, c = z.col, n = HISTORY.length;
      const x0 = 40, x1 = z.W - 40, y = 70;
      D.line(g, x0, y, x1, y, c.line, 3);
      HISTORY.forEach((h, i) => {
        const x = x0 + (x1 - x0) * i / (n - 1);
        const on = i <= z.step, cur = i === z.step;
        D.circle(g, x, y, cur ? 11 : 8, { fill: on ? c.cv : c.surf, stroke: on ? c.cv : c.line, w: 2 });
        const lbl = h[0];
        D.text(g, lbl, x, y - 20, { a: 'center', b: cur, s: fit(g, lbl, (x1 - x0) / (n - 1) + 6, 12, { b: cur }), c: on ? c.ink : c.ink2 });
      });
      const h = HISTORY[z.step];
      rr(g, 30, 110, z.W - 60, 170, 14, { fill: c.bg, stroke: c.cv, w: 2 });
      D.text(g, h[1], 50, 142, { b: true, s: 18, c: c.cv });
      if (z.p.detail) wrap(g, h[2], 50, 172, z.W - 100, { s: 14.5, c: c.ink, lh: 22 });
      const inside = z.step < 3;
      D.text(g, inside ? 'How it drives the browser: JavaScript running inside the page' : 'How it drives the browser: from outside, through a driver', 50, 266, { s: 12.5, b: true, c: inside ? c.orange : c.green });
      return `<b>${esc(h[0])}</b>: ${esc(h[1])}.`;
    }
  });
})();

(() => {
  const { def, D, esc } = CVZ;
  const { tw, rr, wrap, fit, box, ms } = SEZ;

  /* ---------------------------------------------------------------- Chapter 1.2: the W3C wire protocol */
  const ELEM = 'element-6066-11e4-a52e-4f735466cecf';
  const CMDS = {
    session: { py: 'driver = webdriver.Chrome()', java: 'WebDriver driver = new ChromeDriver();', js: "await new Builder().forBrowser('chrome').build()",
      m: 'POST', path: '/session', body: '{"capabilities": {"alwaysMatch": {"browserName": "chrome"}}}', act: 'chromedriver starts Chrome with a fresh profile', ok: '{"value": {"sessionId": "5c1e…", "capabilities": {…}}}', ret: 'a driver object that remembers the session id' },
    get: { py: 'driver.get(url)', java: 'driver.get(url);', js: 'await driver.get(url)', m: 'POST', path: '/session/5c1e…/url', body: '{"url": "https://www.selenium.dev/…/web-form.html"}', act: 'Chrome loads the page and the driver waits until document.readyState is complete', ok: '{"value": null}', ret: 'nothing, once the page has loaded' },
    find: { py: 'driver.find_element(By.NAME, "my-text")', java: 'driver.findElement(By.name("my-text"));', js: "await driver.findElement(By.name('my-text'))", m: 'POST', path: '/session/5c1e…/element', body: '{"using": "css selector", "value": "[name=\\"my-text\\"]"}', act: 'Chrome runs the CSS query in the page', ok: `{"value": {"${ELEM}": "f.C6…e.6"}}`, ret: 'a WebElement that holds the element reference', err: ['404', '{"value": {"error": "no such element", "message": "no such element: Unable to locate element …"}}', 'NoSuchElementException'] },
    click: { py: 'button.click()', java: 'button.click();', js: 'await button.click()', m: 'POST', path: '/session/5c1e…/element/f.C6…e.7/click', body: '{}', act: 'the driver scrolls the element into view, checks nothing covers its centre, then clicks it', ok: '{"value": null}', ret: 'nothing', err: ['400', '{"value": {"error": "element click intercepted", "message": "… Other element would receive the click …"}}', 'ElementClickInterceptedException'] },
    text: { py: 'message.text', java: 'message.getText();', js: 'await message.getText()', m: 'GET', path: '/session/5c1e…/element/f.C6…e.9/text', body: '', act: 'Chrome reads the visible text of the element', ok: '{"value": "Received!"}', ret: 'the string "Received!"', err: ['404', '{"value": {"error": "stale element reference", "message": "stale element reference: element is not attached to the page document"}}', 'StaleElementReferenceException'] },
    quit: { py: 'driver.quit()', java: 'driver.quit();', js: 'await driver.quit()', m: 'DELETE', path: '/session/5c1e…', body: '', act: 'Chrome closes every window and the session ends', ok: '{"value": null}', ret: 'nothing. The binding then stops the chromedriver process' }
  };
  const LANGN = { java: 'Java', py: 'Python', js: 'JavaScript' };
  def('se-wire', {
    title: 'One command, from your code to the browser and back',
    sub: 'Pick a command and a language, then step through the journey. Tick "make it fail" to see an error answer.',
    W: 660, H: 380,
    params: [
      { k: 'cmd', label: 'Command', type: 'select', v: 'find', opts: [['session', 'Start a session'], ['get', 'Open a page'], ['find', 'Find an element'], ['click', 'Click it'], ['text', 'Read its text'], ['quit', 'Quit']] },
      { k: 'lang', label: 'Language', type: 'select', v: 'py', opts: [['java', 'Java'], ['py', 'Python'], ['js', 'JavaScript']] },
      { k: 'fail', label: 'Make it fail', type: 'check', v: false, help: 'Only find, click and read can fail here.' }
    ],
    tips: [
      { t: 'Play "Find an element". The answer carries a long element reference under a fixed key. That key is the same in every browser.', set: { cmd: 'find', fail: false }, play: true },
      { t: 'Tick "make it fail" for Find. The driver answers 404 with "no such element", and the binding turns it into an exception in your language.', set: { cmd: 'find', fail: true }, play: true },
      { t: 'Switch the language between Java, Python and JavaScript. The request on the wire does not change, only your line of code does.', set: { lang: 'java' } }
    ],
    steps: () => 5,
    startAtZero: true,
    draw(z) {
      const g = z.g, c = z.col, C = CMDS[z.p.cmd], s = z.step;
      const fail = z.p.fail && C.err;
      const X = [20, 250, 480], Wd = 160, top = 20;
      const names = [['Your code', LANGN[z.p.lang] + ' binding'], ['chromedriver', 'the remote end'], ['Chrome', 'the browser']];
      names.forEach((n, i) => box(g, z, X[i], top, Wd, 54, n[0], null, { fill: s >= [0, 2, 3][i] && s <= 5 ? c.bg : c.surf, stroke: [1, 2, 3].includes(s) && i === [0, 1, 2][s - 1] || (s === 0 && i === 0) || (s === 4 && i === 1) || (s === 5 && i === 0) ? c.cv : c.line, lw: 2 }));
      names.forEach((n, i) => D.text(g, n[1], X[i] + Wd / 2, top + 70, { a: 'center', s: 11.5, c: c.ink2 }));
      const y1 = 112, y2 = 132;
      if (s >= 1) { D.arrow(g, X[0] + Wd, y1, X[1], y1, c.accent, 2.5); D.text(g, 'HTTP ' + C.m, (X[0] + Wd + X[1]) / 2, y1 - 6, { a: 'center', s: 11, b: true, c: c.accent }); }
      if (s >= 2) { D.arrow(g, X[1] + Wd, y1, X[2], y1, c.purple, 2.5); D.text(g, 'browser automation', (X[1] + Wd + X[2]) / 2, y1 - 6, { a: 'center', s: 11, b: true, c: c.purple }); }
      if (s >= 4) D.arrow(g, X[1], y2, X[0] + Wd, y2, fail ? c.red : c.green, 2.5);
      if (s >= 3) D.arrow(g, X[2], y2, X[1] + Wd, y2, c.purple, 2.5);
      rr(g, 20, 156, z.W - 40, 206, 12, { fill: c.bg, stroke: c.line });
      const L = 34, maxW = z.W - 68;
      let y = 182;
      const head = (t, col) => { D.text(g, t, L, y, { b: true, s: 13, c: col || c.cv }); y += 20; };
      const mono = t => { y = wrap(g, t, L, y, maxW, { mono: true, s: 12, c: c.ink, lh: 17 }); y += 4; };
      const prose = t => { y = wrap(g, t, L, y, maxW, { s: 13, c: c.ink, lh: 18 }); };
      if (s === 0) { head('1. Your line of code runs'); mono(C[z.p.lang]); prose('The binding does not touch the browser itself. It builds a W3C WebDriver command.'); }
      if (s === 1) { head('2. The binding sends an HTTP request'); mono(C.m + ' ' + C.path); if (C.body) mono(C.body); prose('JSON in, JSON out. The session id in the path tells the driver which browser this is for.'); }
      if (s === 2) { head('3. The driver carries it out', c.purple); prose('chromedriver turns the W3C command into the browser\'s own automation calls: ' + C.act + '.'); }
      if (s === 3) { head('4. The browser answers the driver', c.purple); prose(fail ? 'The browser reports a problem with this command.' : 'The browser reports the result back to chromedriver.'); }
      if (s === 4) { head(fail ? '5. An error answer comes back' : '5. A success answer comes back', fail ? c.red : c.green); mono(fail ? 'HTTP ' + C.err[0] : 'HTTP 200'); mono(fail ? C.err[1] : C.ok); prose(fail ? 'Every error has the same shape: an error code, a message and a stacktrace inside value.' : 'Every success has the same shape: the result sits under the key value.'); }
      if (s === 5) { head('6. The binding hands you a result', fail ? c.red : c.green); prose(fail ? `The binding reads the error code and raises ${C.err[2]} in ${LANGN[z.p.lang]}.` : 'Your code receives ' + C.ret + '.'); }
      return `<b>${['Your code', 'Request', 'Driver', 'Browser', 'Response', 'Result'][s]}</b> for ${esc(z.el.querySelector('select').selectedOptions[0].text)}.`;
    }
  });
})();

(() => {
  const { def, D, esc } = CVZ;
  const { rr, wrap, box } = SEZ;

  /* ---------------------------------------------------------------- Chapter 1.3: how a binding finds its driver */
  /* the decision path, following the Selenium Manager documentation: a driver you give wins, Selenium Manager is
     only the fallback, it uses a driver on PATH, then the cache, then downloads. Browser management since 4.11. */
  function path(p) {
    const out = [['Your code starts a session', 'new ChromeDriver(), webdriver.Chrome() or Builder().build() runs.', 'ink']];
    if (p.given) {
      out.push(['A driver location was given', 'You passed a Service with the path, or set a system property. The binding uses that file and never calls Selenium Manager.', 'green']);
      out.push(['The binding starts the driver', 'If the driver and the browser do not match, the New Session request fails here with "session not created".', p.match ? 'green' : 'red']);
      return out;
    }
    out.push(['No driver given, so the fallback runs', 'The binding calls the selenium-manager program shipped inside the library, passing the browser name and options.', 'cv']);
    if (p.browser === 'missing') {
      if (!p.online) { out.push(['Chrome is not installed and you are offline', 'Selenium Manager cannot download Chrome for Testing, so the session cannot start.', 'red']); return out; }
      out.push(['Chrome is not installed', 'Since Selenium 4.11, Selenium Manager downloads Chrome for Testing into ~/.cache/selenium/chrome.', 'purple']);
    } else out.push(['Step 1: browser version discovery', 'It runs a shell command such as chrome --version and reads the version, for example 153.', 'cv']);
    if (p.onpath) {
      out.push([p.match ? 'A driver on PATH matches' : 'A driver on PATH does not match', p.match ? 'Selenium Manager reports the chromedriver it found on PATH and stops looking.' : 'Selenium Manager compares its version with the browser and tries to resolve the right driver instead.', p.match ? 'green' : 'orange']);
      if (p.match) { out.push(['The binding starts the driver', 'Selenium Manager prints the driver path and the browser path. The binding launches the driver and sends New Session.', 'green']); return out; }
      if (!p.online) {
        out.push(['It cannot resolve a better one', 'Offline, it warns that the driver on PATH might not be compatible and advises deleting it, then hands it over anyway.', 'orange']);
        out.push(['New Session fails', 'chromedriver answers: session not created, this version of ChromeDriver only supports an older Chrome.', 'red']);
        return out;
      }
    }
    out.push(['Step 2: driver version discovery', 'It asks the vendor metadata (Chrome for Testing endpoints for chromedriver) which driver fits the browser. Answers are kept for the TTL, 3600 seconds by default.', 'cv']);
    if (p.cached) out.push(['Step 4: found in the cache', 'The right chromedriver is already in ~/.cache/selenium, so nothing is downloaded.', 'green']);
    else if (!p.online) { out.push(['Offline and not cached', 'Offline mode disables downloads, so there is no driver and the session cannot start.', 'red']); return out; }
    else {
      out.push(['Step 3: driver download', 'It downloads the archive, unpacks it and stores the driver.', 'purple']);
      out.push(['Step 4: driver cache', 'The driver now lives in ~/.cache/selenium. The next run reuses it.', 'green']);
    }
    out.push(['The binding starts the driver', 'The binding launches the driver it was given and sends New Session. Chrome opens.', 'green']);
    return out;
  }
  def('se-manager', {
    title: 'How Selenium finds a driver before the browser opens',
    sub: 'Change what this machine has, then step through what the binding and Selenium Manager do.',
    W: 640, H: 360,
    params: [
      { k: 'given', label: 'You give the driver path yourself', type: 'check', v: false },
      { k: 'onpath', label: 'A chromedriver is on PATH', type: 'check', v: false },
      { k: 'match', label: 'That driver matches the browser', type: 'check', v: true },
      { k: 'cached', label: 'The right driver is already cached', type: 'check', v: false },
      { k: 'browser', label: 'Chrome on this machine', type: 'select', v: 'installed', opts: [['installed', 'Installed'], ['missing', 'Not installed']] },
      { k: 'online', label: 'Internet available', type: 'check', v: true }
    ],
    tips: [
      { t: 'The usual first run: nothing on PATH, nothing cached. Watch the four management steps.', set: { given: false, onpath: false, cached: false, browser: 'installed', online: true }, play: true },
      { t: 'Run it again with the driver cached. Step 3 disappears, which is why the second run starts faster.', set: { given: false, onpath: false, cached: true, online: true }, play: true },
      { t: 'Give a path to a driver that does not match. Selenium Manager never runs, so nothing rescues you and the session fails.', set: { given: true, match: false }, play: true },
      { t: 'Remove Chrome and go offline. There is nothing to download from, so the session cannot start.', set: { given: false, browser: 'missing', online: false }, play: true }
    ],
    steps: z => path(z.p).length - 1,
    startAtZero: true,
    draw(z) {
      const g = z.g, c = z.col, P = path(z.p), s = z.step;
      const n = P.length, gap = 8, x = 24, w = z.W - 48;
      const h = Math.min(44, (z.H - 120 - gap * (n - 1)) / n);
      P.forEach((it, i) => {
        const y = 14 + i * (h + gap), on = i <= s, col = c[it[2]] || c.ink;
        rr(g, x, y, w, h, 10, { fill: i === s ? c.bg : c.surf, stroke: on ? col : c.line, w: i === s ? 2.5 : 1.5 });
        D.text(g, String(i + 1), x + 16, y + h / 2 + 5, { a: 'center', b: true, s: 13, c: on ? col : c.ink2 });
        D.text(g, it[0], x + 34, y + h / 2 + 5, { b: i === s, s: 13.5, c: on ? c.ink : c.ink2 });
      });
      const cur = P[s];
      const yb = z.H - 96;
      rr(g, x, yb, w, 84, 12, { fill: c.bg, stroke: c[cur[2]] || c.line, w: 2 });
      D.text(g, cur[0], x + 14, yb + 24, { b: true, s: 14, c: c[cur[2]] || c.ink });
      wrap(g, cur[1], x + 14, yb + 46, w - 28, { s: 13, c: c.ink, lh: 18 });
      const end = P[n - 1][2];
      return `<b>${esc(cur[0])}</b>.${s === n - 1 ? (end === 'red' ? ' The session does not start.' : ' The session starts.') : ''}`;
    }
  });
})();

(() => {
  const { def, D, esc } = CVZ;
  const { rr, wrap, box } = SEZ;

  /* ---------------------------------------------------------------- Chapter 2.1: page load strategy */
  /* normal waits for readyState complete (the load event), eager for interactive (DOMContentLoaded), none only for the
     first download of the page. The times are a made up page so the reader can change them. */
  def('se-loadstrategy', {
    title: 'When does get() hand control back?',
    sub: 'A page loads in stages. Pick a strategy and change how slow the parts are, then step through the load.',
    W: 660, H: 330,
    params: [
      { k: 'st', label: 'pageLoadStrategy', type: 'select', v: 'normal', opts: [['normal', 'normal (default)'], ['eager', 'eager'], ['none', 'none']] },
      { k: 'html', label: 'HTML download (ms)', type: 'range', v: 400, min: 100, max: 2000, step: 100 },
      { k: 'dom', label: 'Parsing and scripts (ms)', type: 'range', v: 300, min: 100, max: 2000, step: 100 },
      { k: 'img', label: 'Images, fonts and styles (ms)', type: 'range', v: 2500, min: 0, max: 6000, step: 250 }
    ],
    tips: [
      { t: 'With normal, get() waits for every image. Drag the images slider and watch the return time move.', set: { st: 'normal' }, play: true },
      { t: 'Switch to eager. get() returns at DOMContentLoaded, while the images still load. Elements exist, pictures may not.', set: { st: 'eager' }, play: true },
      { t: 'Switch to none. get() returns as soon as the first bytes are in. Your waits now carry all the weight.', set: { st: 'none' }, play: true }
    ],
    steps: () => 4,
    startAtZero: true,
    draw(z) {
      const g = z.g, c = z.col, p = z.p, s = z.step;
      const t1 = p.html, t2 = t1 + p.dom, t3 = t2 + p.img;
      const ret = { normal: t3, eager: t2, none: t1 }[p.st];
      const L = 40, R = z.W - 40, y = 120, scale = (R - L) / Math.max(t3, 1);
      const X = t => L + t * scale;
      D.text(g, 'time since get() was called', L, 30, { s: 12, c: c.ink2 });
      const bars = [[0, t1, 'download HTML', c.accent], [t1, t2, 'parse, run scripts', c.purple], [t2, t3, 'images, fonts, styles', c.orange]];
      bars.forEach((b, i) => {
        if (i > s - 1 && s < 4) return;
        if (b[1] <= b[0]) return;
        rr(g, X(b[0]), y - 22, Math.max(2, X(b[1]) - X(b[0])), 26, 6, { fill: b[3] });
        if (X(b[1]) - X(b[0]) > 90) D.text(g, b[2], (X(b[0]) + X(b[1])) / 2, y - 4, { a: 'center', s: 11.5, b: true, c: '#fff' });
      });
      D.line(g, L, y + 14, R, y + 14, c.line, 2);
      const marks = [[0, 'get() sent', 'loading'], [t1, 'first bytes in', 'loading'], [t2, 'DOMContentLoaded', 'interactive'], [t3, 'load event', 'complete']];
      marks.forEach((m, i) => {
        if (i > s) return;
        const x = X(m[0]);
        D.line(g, x, y + 8, x, y + 20, c.ink, 2);
        const lab = i % 2 ? 46 : 62;
        D.text(g, m[1], x, y + lab, { a: i === 0 ? 'left' : i === 3 ? 'right' : 'center', s: 11.5, b: true, c: c.ink });
        D.text(g, 'readyState ' + m[2], x, y + lab + 15, { a: i === 0 ? 'left' : i === 3 ? 'right' : 'center', s: 10.5, c: c.ink2 });
      });
      const retIdx = { none: 1, eager: 2, normal: 3 }[p.st];
      if (s >= retIdx) {
        const x = X(ret);
        D.arrow(g, x, 46, x, y - 26, c.green, 3);
        D.text(g, 'get() returns at ' + ret + ' ms', Math.min(Math.max(x, L + 70), R - 70), 52 - 12, { a: 'center', b: true, s: 13, c: c.green });
      }
      rr(g, 20, 222, z.W - 40, 92, 12, { fill: c.bg, stroke: c.line });
      const msg = [
        'get() sends the address. The browser starts to fetch the page.',
        'The first bytes of HTML arrive. With none, WebDriver stops waiting here.',
        'The HTML is parsed and its scripts have run: DOMContentLoaded fires and readyState becomes interactive. With eager, WebDriver stops waiting here.',
        'Every image, font and style sheet is in: the load event fires and readyState becomes complete. With normal, WebDriver stops waiting here.',
        p.st === 'normal' ? `normal saved nothing but is the safest: every element and every resource is ready when get() returns at ${ret} ms.` : `${p.st} returned ${t3 - ret} ms earlier than normal would. Anything that loads later needs an explicit wait in your test.`
      ][s];
      wrap(g, msg, 36, 248, z.W - 72, { s: 13.5, c: c.ink, lh: 20 });
      return `With <b>${esc(p.st)}</b>, get() returns after ${ret} ms. The whole page takes ${t3} ms.`;
    }
  });
})();

(() => {
  const { def, D, esc } = CVZ;
  const { rr, wrap, fit } = SEZ;

  /* ---------------------------------------------------------------- Chapter 2.2: browser history */
  /* the session history of one tab: get adds a page and throws away anything ahead, back and forward move the
     pointer, refresh reloads the current page. Mirrors what a user does with the toolbar buttons. */
  const PLANS = {
    shop: ['get home', 'get search', 'get product', 'back', 'back', 'forward', 'refresh', 'get basket'],
    simple: ['get home', 'get search', 'back', 'forward'],
    edge: ['get home', 'back', 'get search', 'forward', 'back', 'back']
  };
  function run(plan, upto) {
    let hist = [], at = -1, msg = '';
    plan.slice(0, upto + 1).forEach(a => {
      const [cmd, page] = a.split(' ');
      if (cmd === 'get') { hist = hist.slice(0, at + 1); hist.push(page); at = hist.length - 1; msg = `get opens ${page}. Any pages ahead of the current one are thrown away.`; }
      if (cmd === 'back') { if (at > 0) { at--; msg = `back moves to ${hist[at]}, the same as the toolbar Back button.`; } else msg = 'back with nothing behind: the browser stays where it is and no error is raised.'; }
      if (cmd === 'forward') { if (at < hist.length - 1) { at++; msg = `forward moves to ${hist[at]}.`; } else msg = 'forward with nothing ahead: nothing happens.'; }
      if (cmd === 'refresh') msg = `refresh reloads ${hist[at]}. Form fields typed into may be cleared, and any element you found before is now stale.`;
    });
    return { hist, at, msg };
  }
  const CALL = { java: { get: p => `driver.get(".../${p}")`, back: () => 'driver.navigate().back()', forward: () => 'driver.navigate().forward()', refresh: () => 'driver.navigate().refresh()' },
    py: { get: p => `driver.get(".../${p}")`, back: () => 'driver.back()', forward: () => 'driver.forward()', refresh: () => 'driver.refresh()' },
    js: { get: p => `await driver.get('.../${p}')`, back: () => 'await driver.navigate().back()', forward: () => 'await driver.navigate().forward()', refresh: () => 'await driver.navigate().refresh()' } };
  def('se-history', {
    title: 'Back, forward and the history of a tab',
    sub: 'Pick a plan and step through it. The highlighted card is the page the browser shows.',
    W: 640, H: 300,
    params: [
      { k: 'plan', label: 'Plan', type: 'select', v: 'shop', opts: [['shop', 'Shopping trip'], ['simple', 'Short trip'], ['edge', 'Pressing too far']] },
      { k: 'lang', label: 'Show the code in', type: 'select', v: 'py', opts: [['java', 'Java'], ['py', 'Python'], ['js', 'JavaScript']] }
    ],
    tips: [
      { t: 'In the shopping trip, watch what happens to product when you go back and then get basket. A new get cuts off the pages ahead.', set: { plan: 'shop' }, play: true },
      { t: 'Pressing too far: back on the first page does nothing and raises no error. Check the title if your test depends on it.', set: { plan: 'edge' }, play: true }
    ],
    steps: z => PLANS[z.p.plan].length - 1,
    startAtZero: true,
    draw(z) {
      const g = z.g, c = z.col, plan = PLANS[z.p.plan], s = z.step;
      const { hist, at, msg } = run(plan, s);
      const [cmd, page] = plan[s].split(' ');
      D.text(g, 'Line run: ' + CALL[z.p.lang][cmd](page), 24, 30, { mono: true, s: 13, b: true, c: c.cv });
      const w = 120, gap = 16, x0 = 24, y = 70;
      hist.forEach((p, i) => {
        const x = x0 + i * (w + gap), cur = i === at;
        rr(g, x, y, w, 70, 12, { fill: cur ? c.bg : c.surf, stroke: cur ? c.cv : c.line, w: cur ? 3 : 1.5 });
        D.text(g, p, x + w / 2, y + 32, { a: 'center', b: true, s: fit(g, p, w - 12, 15, { b: true }), c: cur ? c.ink : c.ink2 });
        D.text(g, i < at ? 'behind' : i > at ? 'ahead' : 'showing', x + w / 2, y + 54, { a: 'center', s: 11.5, c: cur ? c.cv : c.ink2 });
        if (i) D.arrow(g, x - gap + 2, y + 35, x - 2, y + 35, c.line, 1.5);
      });
      rr(g, 24, 170, z.W - 48, 110, 12, { fill: c.bg, stroke: c.line });
      wrap(g, msg, 40, 198, z.W - 80, { s: 14, c: c.ink, lh: 21 });
      D.text(g, `getTitle() would now return the title of ${hist[at]}`, 40, 262, { s: 12.5, c: c.ink2 });
      return `Showing <b>${esc(hist[at])}</b>, with ${at} page${at === 1 ? '' : 's'} behind and ${hist.length - 1 - at} ahead.`;
    }
  });
})();

(() => {
  const { def, D, esc } = CVZ;
  const { rr, wrap, fit } = SEZ;

  /* ---------------------------------------------------------------- Chapter 3.1: the eight locator strategies */
  /* the page is the locators example of the Selenium documentation. Matching uses the real browser: querySelectorAll
     for CSS, document.evaluate for XPath. id, name and class name are turned into CSS the way the Python binding does. */
  const HTML = `<h2>Contact Selenium</h2><form>
<input type="radio" name="gender" value="m">Male <input type="radio" name="gender" value="f">Female<br>
<label for="fname">First name:</label><input class="information" type="text" id="fname" name="fname" value="Jane">
<label for="lname">Last name:</label><input class="information" type="text" id="lname" name="lname" value="Doe">
<label for="newsletter">Newsletter:</label><input type="checkbox" name="newsletter" value="1">
<input type="submit" value="Submit"></form>
<p>To know more about Selenium, visit the official page <a href="https://www.selenium.dev/">Selenium Official Page</a></p>`;
  let docCache = null;
  const doc = () => docCache || (docCache = new DOMParser().parseFromString('<!doctype html><html><body>' + HTML + '</body></html>', 'text/html'));
  const cssq = s => '"' + s.replace(/["\\]/g, '\\$&') + '"';
  function locate(by, v) {
    const d = doc();
    let using = 'css selector', value = v, list = [];
    try {
      if (by === 'id') value = `[id=${cssq(v)}]`;
      if (by === 'name') value = `[name=${cssq(v)}]`;
      if (by === 'class') { if (/\s/.test(v.trim())) throw new Error('compound class names are not permitted'); value = '.' + v; }
      if (by === 'tag') { using = 'tag name'; list = [...d.body.getElementsByTagName(v)]; }
      else if (by === 'link' || by === 'partial') {
        using = by === 'link' ? 'link text' : 'partial link text';
        list = [...d.body.querySelectorAll('a')].filter(a => { const t = a.textContent.trim(); return by === 'link' ? t === v : t.includes(v); });
      } else if (by === 'xpath') {
        using = 'xpath';
        const r = d.evaluate(v, d, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (let i = 0; i < r.snapshotLength; i++) if (r.snapshotItem(i).nodeType === 1) list.push(r.snapshotItem(i));
      } else list = [...d.body.querySelectorAll(value)];
    } catch (e) { return { using, value, err: e.message.split('\n')[0] }; }
    return { using, value, list };
  }
  function label(el) {
    let s = '<' + el.tagName.toLowerCase();
    ['type', 'id', 'name', 'class', 'value', 'for', 'href'].forEach(a => { if (el.hasAttribute(a)) s += ` ${a}="${el.getAttribute(a)}"`; });
    s += '>';
    const t = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join(' ').trim();
    return t && el.tagName !== 'P' ? s + t : s;
  }
  const PRESET = { id: 'lname', name: 'newsletter', class: 'information', css: '#fname', xpath: "//input[@value='f']", tag: 'a', link: 'Selenium Official Page', partial: 'Official' };
  def('se-locate', {
    title: 'Try every locator strategy on one page',
    sub: 'Pick a strategy and type a value. Every element that matches lights up, and the first one is what find element returns.',
    W: 660, H: 470,
    params: [
      { k: 'by', label: 'Strategy', type: 'select', v: 'id', opts: [['id', 'id'], ['name', 'name'], ['class', 'class name'], ['css', 'css selector'], ['xpath', 'xpath'], ['tag', 'tag name'], ['link', 'link text'], ['partial', 'partial link text']] },
      { k: 'v', label: 'Value', type: 'text', v: 'lname' }
    ],
    tips: [
      { t: 'class name "information" matches two inputs. find element returns the first, First name, and find elements returns both.', set: { by: 'class', v: 'information' } },
      { t: 'Try tag name "input". Seven matches: the documentation calls tag name dangerous for a single element for this reason.', set: { by: 'tag', v: 'input' } },
      { t: 'Try class name "information extra". Compound class names are not allowed. Use the css selector .information.extra instead.', set: { by: 'class', v: 'information extra' } },
      { t: 'An XPath with text(): //label[text()="Last name:"]. XPath can match on text, CSS cannot.', set: { by: 'xpath', v: '//label[text()="Last name:"]' } },
      { t: 'id "email" matches nothing. find element raises no such element, find elements returns an empty list.', set: { by: 'id', v: 'email' } }
    ],
    change(z, k) { if (k === 'by' && PRESET[z.p.by]) z.set({ v: PRESET[z.p.by] }); },
    draw(z) {
      const g = z.g, c = z.col;
      const r = locate(z.p.by, z.p.v || '');
      const rows = [...doc().body.querySelectorAll('*')].filter(e => e.tagName !== 'BR');
      const depth = e => { let n = 0; while (e.parentElement && e.parentElement !== doc().body) { n++; e = e.parentElement; } return n; };
      const y0 = 16, h = 25;
      rows.forEach((el, i) => {
        const y = y0 + i * h, x = 20 + depth(el) * 22;
        const k = r.list ? r.list.indexOf(el) : -1;
        if (k >= 0) rr(g, x - 6, y - 2, z.W - x - 14, h - 4, 6, { fill: k === 0 ? c.cv : c.bg, stroke: c.cv, w: 1.5 });
        const t = label(el);
        D.text(g, t, x, y + 15, { mono: true, s: fit(g, t, z.W - x - 30, 12, { mono: true }), c: k === 0 ? '#fff' : k > 0 ? c.cv : c.ink2, b: k >= 0 });
      });
      const yb = y0 + rows.length * h + 10;
      rr(g, 16, yb, z.W - 32, z.H - yb - 10, 10, { fill: c.bg, stroke: c.line });
      D.text(g, 'W3C request body: ' + JSON.stringify({ using: r.using, value: r.value }), 30, yb + 24, { mono: true, s: fit(g, 'W3C request body: ' + JSON.stringify({ using: r.using, value: r.value }), z.W - 60, 12, { mono: true }), c: c.ink });
      let msg;
      if (r.err) msg = 'invalid selector: ' + r.err;
      else if (!r.list.length) msg = 'No match. find element raises no such element (NoSuchElementException), find elements returns an empty list.';
      else msg = `${r.list.length} match${r.list.length > 1 ? 'es' : ''}. find element returns the first one (filled). find elements returns all ${r.list.length}, in page order.`;
      wrap(g, msg, 30, yb + 48, z.W - 60, { s: 13, c: r.err || !r.list.length ? c.red : c.ink, lh: 18, b: true });
      return r.err ? 'The locator is invalid.' : `<b>${r.list.length}</b> element${r.list.length === 1 ? '' : 's'} match.`;
    }
  });
})();

(() => {
  const { def, D, esc } = CVZ;
  const { rr, wrap, fit } = SEZ;

  /* ---------------------------------------------------------------- Chapter 3.2: where a search looks */
  /* the rules shown here were checked against Chrome 153: CSS from an element only looks inside it, an XPath that
     starts with // always starts at the document, .// starts at the element, nothing crosses into a shadow root
     except a search from that shadow root, and Chrome rejects XPath and tag name inside a shadow root. */
  const T = [
    ['body', 0, 'doc'], ['h2', 1, 'doc'], ['form', 1, 'doc'], ['input radio', 2, 'form', 'input'], ['input radio', 2, 'form', 'input'],
    ['input #fname', 2, 'form', 'input'], ['input #lname', 2, 'form', 'input'], ['input checkbox', 2, 'form', 'input'], ['input submit', 2, 'form', 'input'],
    ['p', 1, 'doc'], ['a', 2, 'doc', 'a'], ['custom-checkbox-element', 1, 'doc'], ['#shadow-root', 2, 'host'], ['div', 3, 'shadow'], ['input checkbox', 4, 'shadow', 'input']
  ];
  const LOC = {
    css_input: ['css selector', 'input'], xp_a: ['xpath', '//a'], xp_dot: ['xpath', './/input'], css_box: ['css selector', "input[type='checkbox']"]
  };
  function search(ctx, loc) {
    const [using, v] = LOC[loc];
    if (ctx === 'shadow' && using === 'xpath') return { err: 'invalid argument: invalid locator. Chrome rejected XPath and tag name inside a shadow root when this page was built. Use a CSS selector there.' };
    const inScope = n => ctx === 'shadow' ? n[2] === 'shadow' : ctx === 'form' ? (using === 'xpath' && !v.startsWith('.') ? n[2] !== 'shadow' && n[2] !== 'host' : n[2] === 'form') : n[2] !== 'shadow' && n[2] !== 'host';
    const want = n => loc === 'css_input' || loc === 'xp_dot' ? n[3] === 'input' : loc === 'xp_a' ? n[3] === 'a' : n[3] === 'input' && n[0] === 'input checkbox';
    const visit = T.map((n, i) => i).filter(i => inScope(T[i]));
    return { visit, hits: visit.filter(i => want(T[i])) };
  }
  def('se-scope', {
    title: 'Where does a search look?',
    sub: 'A small page made of the locators example plus a shadow root. Pick where you call find from and a locator, then watch which elements the browser checks.',
    W: 660, H: 470,
    params: [
      { k: 'ctx', label: 'Search from', type: 'select', v: 'form', opts: [['doc', 'the driver (whole page)'], ['form', 'the form element'], ['shadow', 'the shadow root']] },
      { k: 'loc', label: 'Locator', type: 'select', v: 'css_input', opts: [['css_input', 'css selector input'], ['xp_a', 'xpath //a'], ['xp_dot', 'xpath .//input'], ['css_box', "css selector input[type='checkbox']"]] }
    ],
    tips: [
      { t: 'From the form, css input finds the six inputs of the form and nothing else.', set: { ctx: 'form', loc: 'css_input' }, play: true },
      { t: 'From the form, xpath //a still finds the link outside the form. // means start at the top of the document, whatever you call it on.', set: { ctx: 'form', loc: 'xp_a' }, play: true },
      { t: 'From the whole page, look for the checkbox. Only the one in the form is found: the search never enters the shadow root.', set: { ctx: 'doc', loc: 'css_box' }, play: true },
      { t: 'Now search from the shadow root itself. The hidden checkbox is found. Switch to an XPath and Chrome refuses it.', set: { ctx: 'shadow', loc: 'css_box' }, play: true }
    ],
    steps: z => { const r = search(z.p.ctx, z.p.loc); return r.err ? 0 : r.visit.length; },
    startAtZero: true,
    speed: () => 380,
    draw(z) {
      const g = z.g, c = z.col, r = search(z.p.ctx, z.p.loc), s = z.step;
      const y0 = 14, h = 24;
      const seen = r.err ? [] : r.visit.slice(0, s);
      T.forEach((n, i) => {
        const y = y0 + i * h, x = 24 + n[1] * 22;
        const inSc = !r.err && r.visit.includes(i), hit = !r.err && r.hits.includes(i) && seen.includes(i), cur = !r.err && r.visit[s - 1] === i;
        const shadowBox = n[2] === 'shadow' || n[2] === 'host';
        if (shadowBox) rr(g, x - 8, y - 1, z.W - x - 16, h - 4, 6, { stroke: c.purple, dash: [4, 3], w: 1.2 });
        if (hit) rr(g, x - 6, y, z.W - x - 20, h - 6, 6, { fill: c.cv });
        else if (cur) rr(g, x - 6, y, z.W - x - 20, h - 6, 6, { fill: c.bg, stroke: c.cv, w: 2 });
        D.text(g, '<' + n[0] + '>', x, y + 13, { mono: true, s: 12.5, b: hit || cur, c: hit ? '#fff' : inSc ? c.ink : c.ink2 });
        if (!inSc && !r.err) D.text(g, 'not searched', z.W - 30, y + 13, { a: 'right', s: 11, c: c.ink2 });
      });
      const yb = y0 + T.length * h + 8;
      rr(g, 16, yb, z.W - 32, z.H - yb - 10, 10, { fill: c.bg, stroke: r.err ? c.red : c.line });
      const L = LOC[z.p.loc];
      if (r.err) wrap(g, r.err, 30, yb + 24, z.W - 60, { s: 13.5, b: true, c: c.red, lh: 19 });
      else {
        const found = r.hits.filter(i => seen.includes(i)).length;
        D.text(g, `${L[0]} "${L[1]}" from ${{ doc: 'the driver', form: 'the form', shadow: 'the shadow root' }[z.p.ctx]}`, 30, yb + 24, { b: true, s: 13.5, c: c.ink });
        D.text(g, s >= r.visit.length ? `Done: find elements returns ${r.hits.length}, find element returns ${r.hits.length ? 'the first' : 'no such element'}.` : `Checked ${s} of ${r.visit.length} elements, ${found} matched so far.`, 30, yb + 46, { s: 13, c: c.ink2 });
      }
      return r.err ? 'Chrome rejects this locator in a shadow root.' : `<b>${r.hits.length}</b> match${r.hits.length === 1 ? '' : 'es'} in scope.`;
    }
  });
})();

(() => {
  const { def, D, esc } = CVZ;
  const { rr, wrap, box } = SEZ;

  /* ---------------------------------------------------------------- Chapter 3.3: what Element Click checks */
  /* the order follows the Selenium documentation and the W3C Element Click command: scroll the element into view,
     check that it can be interacted with, check that nothing covers its centre point, then send the mouse events. */
  function plan(p) {
    const out = [['Click requested', 'The binding sends POST /session/{id}/element/{id}/click.', 'ink']];
    if (p.where === 'below') out.push(['Scroll into view', 'The element is below the visible area, so the driver scrolls until its bottom edge lines up with the bottom of the viewport.', 'accent']);
    else out.push(['Already in view', 'The element is inside the viewport, so no scrolling is needed.', 'green']);
    if (p.state === 'hidden') { out.push(['Not displayed', 'The element has display: none, so it has no box to click.', 'red']); out.push(['Error: element not interactable', 'HTTP 400. Your code gets ElementNotInteractableException.', 'red']); return out; }
    out.push(['It can be interacted with', 'The element is displayed and has a size, so the driver can aim at it.', 'green']);
    out.push(['Find the centre point', 'The driver takes the centre of the element as the place to click.', 'accent']);
    if (p.state === 'disabled') { out.push(['The centre belongs to the parent', 'Chrome does not let a disabled button receive pointer events, so its parent counts as the element at that point.', 'red']); out.push(['Error: element click intercepted', 'This is what Chrome 153 answered when this page was built: "Other element would receive the click" naming the parent div. Check isEnabled() first so the failure message makes sense.', 'red']); return out; }
    if (p.cover) { out.push(['Something covers the centre', 'A cookie banner lies on top. The element at that point is the banner, not the button.', 'red']); out.push(['Error: element click intercepted', 'HTTP 400 with "Other element would receive the click". Your code gets ElementClickInterceptedException.', 'red']); return out; }
    out.push(['The centre is clear', 'The topmost element at the centre is the button itself.', 'green']);
    out.push(['Mouse events', 'The driver moves the pointer there and sends mouse down, mouse up and click, like a real hand.', 'accent']);
    out.push(['Done', 'The page reacts to the click. The command answers HTTP 200 with value null.', 'green']);
    return out;
  }
  def('se-click', {
    title: 'What happens inside one click',
    sub: 'Change where the button is and what is wrong with it, then step through the checks the driver makes.',
    W: 660, H: 400,
    params: [
      { k: 'where', label: 'Button position', type: 'select', v: 'below', opts: [['view', 'Inside the viewport'], ['below', 'Below the fold']] },
      { k: 'state', label: 'Button state', type: 'select', v: 'ok', opts: [['ok', 'Normal'], ['hidden', 'display: none'], ['disabled', 'disabled']] },
      { k: 'cover', label: 'A cookie banner covers it', type: 'check', v: false }
    ],
    tips: [
      { t: 'The happy path: the driver scrolls, checks, aims at the centre and clicks.', set: { where: 'below', state: 'ok', cover: false }, play: true },
      { t: 'Add the cookie banner. The click is intercepted. Close the banner in your test first, or wait for it to go.', set: { cover: true, state: 'ok' }, play: true },
      { t: 'Hide the button. The driver stops early with element not interactable.', set: { state: 'hidden', cover: false }, play: true },
      { t: 'Disable the button. Chrome reports the click as intercepted by the parent, a confusing message unless you check isEnabled() first.', set: { state: 'disabled', cover: false }, play: true }
    ],
    steps: z => plan(z.p).length - 1,
    startAtZero: true,
    speed: () => 1100,
    draw(z) {
      const g = z.g, c = z.col, p = z.p, P = plan(p), s = z.step, cur = P[s];
      /* left: a page with a viewport frame */
      const vx = 24, vy = 20, vw = 230, vh = 200;
      const scrolled = p.where === 'below' && s >= 1;
      const by = p.where === 'below' ? (scrolled ? vy + vh - 48 : vy + vh + 50) : vy + 90;
      rr(g, vx, vy, vw, vh + 110, 10, { fill: c.surf, stroke: c.line });
      rr(g, vx, vy, vw, vh, 10, { stroke: c.accent, w: 2.5 });
      D.text(g, 'viewport', vx + 8, vy + 16, { s: 11, b: true, c: c.accent });
      for (let i = 0; i < 4; i++) rr(g, vx + 16, (scrolled ? vy + 30 : vy + 34) + i * 26, vw - 32, 12, 4, { fill: c.bg });
      if (p.state !== 'hidden') {
        rr(g, vx + 60, by, 110, 36, 8, { fill: p.state === 'disabled' ? c.line : c.cv });
        D.text(g, 'Submit', vx + 115, by + 23, { a: 'center', b: true, s: 13, c: '#fff' });
        if (s >= 3) { D.circle(g, vx + 115, by + 18, 5, { fill: c.red }); }
      } else rr(g, vx + 60, by, 110, 36, 8, { stroke: c.line, dash: [4, 4] });
      if (p.cover && p.state !== 'hidden') { g.save(); g.globalAlpha = 0.92; rr(g, vx + 4, by + 4, vw - 8, 46, 6, { fill: c.orange }); g.restore(); D.text(g, 'We use cookies. Accept?', vx + 115, by + 32, { a: 'center', b: true, s: 12, c: '#fff' }); }
      /* right: the list of checks */
      const lx = 280, lw = z.W - lx - 20;
      P.forEach((it, i) => {
        const y = 20 + i * 34, on = i <= s, col = c[it[2]] || c.ink;
        rr(g, lx, y, lw, 28, 8, { fill: i === s ? c.bg : c.surf, stroke: on ? col : c.line, w: i === s ? 2.2 : 1.2 });
        D.text(g, it[0], lx + 12, y + 19, { s: 13, b: i === s, c: on ? c.ink : c.ink2 });
      });
      rr(g, 24, z.H - 76, z.W - 48, 64, 10, { fill: c.bg, stroke: c[cur[2]] || c.line, w: 2 });
      wrap(g, cur[1], 38, z.H - 50, z.W - 76, { s: 13.5, c: c.ink, lh: 19 });
      return `<b>${esc(cur[0])}</b>`;
    }
  });
})();

(() => {
  const { def, D, esc } = CVZ;
  const { rr, wrap } = SEZ;

  /* ---------------------------------------------------------------- Chapter 4.1: waiting strategies on one timeline */
  /* the explicit wait loop follows the Python WebDriverWait: check, give up if the time is past the timeout,
     otherwise sleep for the poll interval and check again. A check that uses find element blocks for the implicit wait when the element is
     missing, which is how mixing the two stretches the wait, as the Selenium documentation warns. Times in seconds. */
  function simulate(p) {
    const appear = p.never ? Infinity : p.appear;
    const ev = [];
    if (p.mode === 'none') {
      ev.push(appear <= 0 ? [0, 'hit', 'find succeeds at once'] : [0, 'fail', 'find fails at once: no such element']);
      return ev;
    }
    if (p.mode === 'sleep') {
      ev.push([0, 'sleep', `sleep(${p.sleep}) starts`]);
      ev.push(appear <= p.sleep ? [p.sleep, 'hit', `find after the sleep succeeds, but ${(p.sleep - Math.min(appear, p.sleep)).toFixed(1)} s were wasted`] : [p.sleep, 'fail', 'find after the sleep fails: the sleep was too short']);
      return ev;
    }
    if (p.mode === 'implicit') {
      ev.push([0, 'start', `find starts, the driver keeps looking for up to ${p.imp} s`]);
      ev.push(appear <= p.imp ? [appear, 'hit', 'the element appears and find returns at once'] : [p.imp, 'fail', 'implicit wait used up: no such element']);
      return ev;
    }
    const imp = p.mode === 'mixed' ? p.imp : 0, T = p.exp, P = p.poll;
    let t = 0, guard = 0;
    while (guard++ < 60) {
      if (appear <= t) { ev.push([t, 'hit', `check at ${t.toFixed(1)} s: condition true, the wait returns`]); return ev; }
      if (imp && appear <= t + imp) { ev.push([appear, 'hit', `the find inside the check at ${t.toFixed(1)} s was still waiting (implicit), and returns when the element appears`]); return ev; }
      const end = t + imp;
      ev.push([end, 'miss', imp ? `check started at ${t.toFixed(1)} s blocked ${imp} s on the implicit wait, then failed` : `check at ${t.toFixed(1)} s: not yet`]);
      if (end > T) { ev.push([end, 'fail', `${end.toFixed(1)} s is past the ${T} s timeout, so the wait raises TimeoutException instead of sleeping again`]); return ev; }
      t = end + P;
    }
    return ev;
  }
  def('se-waits', {
    title: 'Four ways to wait, on one clock',
    sub: 'The element appears after a delay. Pick a strategy and change the numbers, then step through what your code and the driver do.',
    W: 660, H: 300,
    params: [
      { k: 'mode', label: 'Strategy', type: 'select', v: 'explicit', opts: [['none', 'No wait'], ['sleep', 'Fixed sleep'], ['implicit', 'Implicit wait'], ['explicit', 'Explicit wait'], ['mixed', 'Implicit and explicit mixed']] },
      { k: 'appear', label: 'Element appears after (s)', type: 'range', v: 1, min: 0, max: 25, step: 0.5 },
      { k: 'never', label: 'The element never appears', type: 'check', v: false },
      { k: 'sleep', label: 'Sleep length (s)', type: 'range', v: 3, min: 0.5, max: 10, step: 0.5, show: p => p.mode === 'sleep' },
      { k: 'imp', label: 'Implicit wait (s)', type: 'range', v: 10, min: 0.5, max: 15, step: 0.5, show: p => p.mode === 'implicit' || p.mode === 'mixed' },
      { k: 'exp', label: 'Explicit timeout (s)', type: 'range', v: 15, min: 1, max: 20, step: 1, show: p => p.mode === 'explicit' || p.mode === 'mixed' },
      { k: 'poll', label: 'Polling interval (s)', type: 'range', v: 0.5, min: 0.1, max: 3, step: 0.1, show: p => p.mode === 'explicit' || p.mode === 'mixed' }
    ],
    tips: [
      { t: 'No wait: the box from dynamic.html appears 1 s after the click, so the find fails straight away. This is the race the documentation describes.', set: { mode: 'none', appear: 1, never: false }, play: true },
      { t: 'A 3 s sleep works, but wastes 2 s every time. Make the box take 4 s and the sleep fails.', set: { mode: 'sleep', appear: 1, sleep: 3, never: false }, play: true },
      { t: 'Explicit wait with polls every 0.5 s: it returns at the first check after the box appears.', set: { mode: 'explicit', appear: 1, exp: 15, poll: 0.5, never: false }, play: true },
      { t: 'The documentation warning: implicit 10 s mixed with explicit 15 s, and the element never comes. The wait ends after about 20.5 s, not 15.', set: { mode: 'mixed', imp: 10, exp: 15, poll: 0.5, never: true }, play: true }
    ],
    steps: z => simulate(z.p).length,
    startAtZero: true,
    speed: () => 900,
    draw(z) {
      const g = z.g, c = z.col, p = z.p, ev = simulate(p), s = z.step;
      const last = ev[ev.length - 1][0];
      const appear = p.never ? Infinity : p.appear;
      const tmax = Math.max(2, last, isFinite(appear) ? appear : 0, p.mode === 'explicit' || p.mode === 'mixed' ? p.exp : 0) * 1.08;
      const L = 30, R = z.W - 30, Y = 120, X = t => L + (R - L) * Math.min(t, tmax) / tmax;
      D.line(g, L, Y, R, Y, c.line, 3);
      for (let t = 0; t <= tmax; t += tmax > 12 ? 5 : 1) { D.line(g, X(t), Y - 5, X(t), Y + 5, c.line, 1.5); D.text(g, t + ' s', X(t), Y + 22, { a: 'center', s: 11, c: c.ink2 }); }
      if (isFinite(appear)) { rr(g, X(appear), Y - 46, Math.max(3, R - X(appear)), 20, 6, { fill: c.cv }); D.text(g, 'element present', X(appear) + 6, Y - 32, { s: 11.5, b: true, c: '#fff' }); }
      else D.text(g, 'the element never appears', L, Y - 32, { s: 12, b: true, c: c.ink2 });
      if (p.mode === 'explicit' || p.mode === 'mixed') { D.line(g, X(p.exp), Y - 60, X(p.exp), Y + 30, c.orange, 2); D.text(g, 'timeout ' + p.exp + ' s', X(p.exp), Y - 66, { a: 'center', s: 11.5, b: true, c: c.orange }); }
      let prev = 0;
      ev.slice(0, s).forEach((e, i) => {
        const col = e[1] === 'hit' ? c.green : e[1] === 'fail' ? c.red : e[1] === 'miss' ? c.accent : c.purple;
        if (e[0] > prev) rr(g, X(prev), Y + 34 + (i % 2) * 8, Math.max(2, X(e[0]) - X(prev)), 6, 3, { fill: col });
        D.circle(g, X(e[0]), Y, e[1] === 'hit' || e[1] === 'fail' ? 8 : 5, { fill: col });
        prev = e[0];
      });
      const cur = s ? ev[s - 1] : null;
      rr(g, 20, 200, z.W - 40, 86, 12, { fill: c.bg, stroke: cur ? (cur[1] === 'hit' ? c.green : cur[1] === 'fail' ? c.red : c.line) : c.line, w: 2 });
      const msg = cur ? `At ${cur[0].toFixed(1)} s: ${cur[2]}.` : 'Your code clicks the button at 0 s. Press Step or Play.';
      wrap(g, msg, 36, 228, z.W - 72, { s: 14, c: c.ink, lh: 20 });
      const end = ev[ev.length - 1];
      return `Result: <b>${end[1] === 'hit' ? 'found' : 'failed'}</b> after ${end[0].toFixed(1)} s.`;
    }
  });
})();

(() => {
  const { def, D, esc } = CVZ;
  const { rr, wrap, fit, ms } = SEZ;

  /* ---------------------------------------------------------------- Chapter 4.2: the current browsing context */
  /* WebDriver sends every command to one browsing context: one window or tab, and inside it the top document or a
     frame. Switching moves that pointer. The plans below use the Selenium test pages of this chapter. */
  const PLANS = {
    tabs: [
      ['', 'win1', 'top', 'The session starts with one window. Commands go to its top document.'],
      ['click "Create a new anonymous window"', 'win1', 'top', 'A second window opens and the browser shows it, but WebDriver still points at the first one.', 'win2'],
      ['switchTo().window(newHandle)', 'win2', 'top', 'Now commands go to the new window. getTitle() returns its title.', 'win2'],
      ['close()', 'gone', 'top', 'close() shuts the current window. The pointer now points at a window that no longer exists.', 'closed'],
      ['getTitle()', 'gone', 'top', 'Error: no such window. You must switch to a window that still exists.', 'closed', true],
      ['switchTo().window(original)', 'win1', 'top', 'Back on the first window. Commands work again.', 'closed']
    ],
    frames: [
      ['', 'win1', 'top', 'Commands go to the top document of iframes.html.'],
      ['findElement(By.id("email"))', 'win1', 'top', 'Error: no such element. The email box lives inside the iframe, and the top document cannot see into it.', null, true],
      ['switchTo().frame("iframe1")', 'win1', 'frame', 'Switch by id or name. Commands now go to the document inside the iframe.'],
      ['findElement(By.id("email"))', 'win1', 'frame', 'Found. The search ran inside the frame.'],
      ['switchTo().defaultContent()', 'win1', 'top', 'Back to the top document. The heading outside the frame is reachable again.']
    ],
    nested: [
      ['', 'win1', 'top', 'A made up page with a frame, and a second frame inside that one.'],
      ['switchTo().frame("outer")', 'win1', 'frame', 'Down one level, into the outer frame.'],
      ['switchTo().frame(0)', 'win1', 'inner', 'Down another level by index: the first frame inside the current document.'],
      ['switchTo().parentFrame()', 'win1', 'frame', 'Up one level only, back to the outer frame.'],
      ['switchTo().defaultContent()', 'win1', 'top', 'All the way up to the top document, whatever the depth.']
    ]
  };
  def('se-context', {
    title: 'Where do my commands go?',
    sub: 'WebDriver talks to one window and one document at a time. Step through a plan and watch the pointer move.',
    W: 660, H: 340,
    params: [{ k: 'plan', label: 'Plan', type: 'select', v: 'tabs', opts: [['tabs', 'A link opens a new window'], ['frames', 'An element inside an iframe'], ['nested', 'A frame inside a frame']] }],
    tips: [
      { t: 'In the window plan, notice step 2: the browser shows the new window, but WebDriver has not moved.', set: { plan: 'tabs' }, play: true },
      { t: 'In the iframe plan, the first find fails for a reason that has nothing to do with waiting.', set: { plan: 'frames' }, play: true },
      { t: 'parentFrame goes up one level, defaultContent goes to the top.', set: { plan: 'nested' }, play: true }
    ],
    steps: z => PLANS[z.p.plan].length - 1,
    startAtZero: true,
    speed: () => 1300,
    draw(z) {
      const g = z.g, c = z.col, P = PLANS[z.p.plan], s = z.step, cur = P[s];
      const nested = z.p.plan === 'nested', two = z.p.plan === 'tabs';
      const win2 = two && P.slice(0, s + 1).some(x => x[4] === 'win2') && !P.slice(0, s + 1).some(x => x[4] === 'closed');
      const wins = [['win1', two ? 'xhtmlTest.html' : nested ? 'nested frames (made up page)' : 'iframes.html']];
      if (win2) wins.push(['win2', 'iframes.html (new window)']);
      const W = two ? 300 : 420, x0 = 24;
      wins.forEach((w, i) => {
        const x = x0 + i * (W + 20), y = 20, h = 200, on = cur[1] === w[0];
        rr(g, x, y, W, h, 12, { fill: c.surf, stroke: on && cur[2] === 'top' ? c.cv : c.line, w: on && cur[2] === 'top' ? 3 : 1.5 });
        rr(g, x, y, W, 26, 12, { fill: c.bg });
        D.text(g, w[1], x + 12, y + 18, { s: 12, b: true, mono: true, c: c.ink2 });
        if (!two || w[0] === 'win1') {
          if (!two) {
            const fx = x + 30, fy = y + 50, fw = W - 60, fh = 130;
            const onF = on && (cur[2] === 'frame' || cur[2] === 'inner');
            rr(g, fx, fy, fw, fh, 10, { fill: c.surf, stroke: cur[2] === 'frame' && on ? c.cv : c.purple, w: cur[2] === 'frame' && on ? 3 : 1.5, dash: [5, 3] });
            D.text(g, nested ? 'iframe name="outer"' : 'iframe id="iframe1"', fx + 10, fy + 18, { s: 11.5, mono: true, c: c.purple });
            if (nested) {
              rr(g, fx + 30, fy + 34, fw - 60, 80, 10, { fill: c.surf, stroke: cur[2] === 'inner' && on ? c.cv : c.purple, w: cur[2] === 'inner' && on ? 3 : 1.5, dash: [5, 3] });
              D.text(g, 'frame 0 inside it', fx + 40, fy + 52, { s: 11.5, mono: true, c: c.purple });
            } else D.text(g, '<input id="email"> lives here', fx + 10, fy + 60, { s: 12, mono: true, c: onF ? c.ink : c.ink2 });
          } else D.text(g, '<a target="_blank">Create a new anonymous window</a>', x + 12, y + 70, { s: fit(g, '<a target="_blank">Create a new anonymous window</a>', W - 24, 11.5, { mono: true }), mono: true, c: c.ink2 });
        }
      });
      if (cur[1] === 'gone') { rr(g, x0 + W + 20, 20, W, 200, 12, { stroke: c.red, dash: [6, 4], w: 2 }); D.text(g, 'closed window', x0 + W + 20 + W / 2, 125, { a: 'center', b: true, s: 14, c: c.red }); }
      D.text(g, cur[0] ? 'Command: ' + cur[0] : 'Start', 24, 250, { mono: true, b: true, s: 13, c: c.cv });
      rr(g, 20, 262, z.W - 40, 66, 10, { fill: c.bg, stroke: cur[5] ? c.red : c.line, w: 2 });
      wrap(g, cur[3], 34, 286, z.W - 68, { s: 13.5, c: cur[5] ? c.red : c.ink, lh: 19 });
      return `Commands now go to: <b>${cur[1] === 'gone' ? 'a closed window' : cur[2] === 'top' ? 'the top document' : cur[2] === 'frame' ? 'the frame' : 'the inner frame'}</b>.`;
    }
  });
  /* ---------------------------------------------------------------- Chapter 4.3: the Actions API */
  /* Each plan is the real payload Python sent to POST /session/{id}/actions on this site. 'M' marks a pointerMove whose
     duration comes from the slider, as the bindings use one default for every move they build. */
  const TICKS = {
    hover: { name: 'move_to_element(hover).click()', src: {
      pointer: [['pointerMove', 'M', 'to #hover'], ['pointerDown', 0, 'button 0'], ['pointerUp', 0, 'button 0']],
      key: [['pause', 0, ''], ['pause', 0, ''], ['pause', 0, '']] } },
    drag: { name: 'drag_and_drop(draggable, droppable)', src: {
      pointer: [['pointerMove', 'M', 'to #draggable'], ['pointerDown', 0, 'button 0'], ['pointerMove', 'M', 'to #droppable'], ['pointerUp', 0, 'button 0']],
      key: [['pause', 0, ''], ['pause', 0, ''], ['pause', 0, ''], ['pause', 0, '']] } },
    shift: { name: 'key_down(SHIFT).send_keys("ab").key_up(SHIFT)', src: {
      pointer: [['pause', 0, ''], ['pause', 0, ''], ['pause', 0, ''], ['pause', 0, ''], ['pause', 0, ''], ['pause', 0, '']],
      key: [['keyDown', 0, 'SHIFT \\ue008'], ['keyDown', 0, 'a'], ['keyUp', 0, 'a'], ['keyDown', 0, 'b'], ['keyUp', 0, 'b'], ['keyUp', 0, 'SHIFT \\ue008']] } },
    wheel: { name: 'scroll_by_amount(0, 300)', src: {
      wheel: [['scroll', 0, 'deltaY 300 from the viewport']] } }
  };
  def('se-ticks', {
    title: 'How a chain of actions becomes ticks',
    sub: 'Every input source gets one list of actions. The driver runs them column by column. Each column, a tick, lasts as long as its slowest action.',
    W: 660, H: 360,
    params: [
      { k: 'plan', label: 'Chain', type: 'select', v: 'drag', opts: [['hover', 'Hover, then click'], ['drag', 'Drag and drop'], ['shift', 'Shift plus a and b'], ['wheel', 'Scroll the wheel']] },
      { k: 'dur', label: 'Pointer move duration (ms)', type: 'range', v: 250, min: 0, max: 1000, step: 50 }
    ],
    tips: [
      { t: 'In the drag plan, look at the key row: Python filled it with pauses so both rows have the same number of ticks.', set: { plan: 'drag', dur: 250 }, play: true },
      { t: 'Set the move duration to 0. The drag now takes 0 ms of pointer movement, which some drag libraries do not notice.', set: { plan: 'drag', dur: 0 }, play: true },
      { t: 'In the Shift plan, SHIFT stays down from the first tick to the last, so a and b arrive as capitals.', set: { plan: 'shift' }, play: true }
    ],
    steps: z => Object.values(TICKS[z.p.plan].src)[0].length,
    startAtZero: true,
    speed: () => 1100,
    draw(z) {
      const g = z.g, c = z.col, P = TICKS[z.p.plan], rows = Object.keys(P.src), n = P.src[rows[0]].length, s = z.step;
      const durOf = a => a[1] === 'M' ? z.p.dur : a[1];
      const tickDur = i => Math.max(...rows.map(r => durOf(P.src[r][i])));
      D.text(g, 'actions.perform() sends: ' + P.name, 24, 26, { s: fit(g, 'actions.perform() sends: ' + P.name, z.W - 48, 13, { mono: true }), mono: true, b: true, c: c.cv });
      const x0 = 110, cw = Math.min(124, (z.W - x0 - 24) / n), y0 = 50, rh = 62;
      for (let i = 0; i < n; i++) {
        const x = x0 + i * cw, on = s === i + 1, done = s > i + 1;
        if (on) rr(g, x + 1, y0 - 4, cw - 2, rows.length * rh + 34, 8, { fill: c.bg, stroke: c.cv, w: 2.5 });
        D.text(g, 'tick ' + (i + 1), x + cw / 2, y0 + 10, { a: 'center', s: 11, b: true, c: on ? c.cv : c.ink2 });
        rows.forEach((r, j) => {
          const a = P.src[r][i], y = y0 + 20 + j * rh, pause = a[0] === 'pause';
          rr(g, x + 5, y, cw - 10, rh - 10, 8, { fill: pause ? 'transparent' : c.surf, stroke: pause ? c.line : (done || on ? c.green : c.purple), dash: pause ? [4, 3] : null, w: 1.5 });
          D.text(g, a[0], x + cw / 2, y + 17, { a: 'center', s: fit(g, a[0], cw - 14, 11.5, { mono: true }), mono: true, b: !pause, c: pause ? c.ink2 : c.ink });
          if (a[2]) wrap(g, a[2], x + 10, y + 32, cw - 20, { s: 10, c: c.ink2, lh: 12 });
          D.text(g, ms(durOf(a)), x + cw - 9, y + rh - 14, { a: 'right', s: 10, c: c.ink2 });
        });
        D.text(g, ms(tickDur(i)), x + cw / 2, y0 + 30 + rows.length * rh, { a: 'center', s: 11.5, b: true, c: on ? c.cv : c.ink2 });
      }
      rows.forEach((r, j) => D.text(g, r === 'key' ? 'key' : r, 24, y0 + 50 + j * rh, { s: 13, b: true, mono: true, c: c.ink }));
      D.text(g, 'lasts', 24, y0 + 30 + rows.length * rh, { s: 12, b: true, c: c.ink2 });
      let t = 0; for (let i = 0; i < s; i++) t += tickDur(i);
      let total = 0; for (let i = 0; i < n; i++) total += tickDur(i);
      const yb = y0 + 50 + rows.length * rh;
      rr(g, 20, yb, z.W - 40, z.H - yb - 14, 10, { fill: c.bg, stroke: c.line });
      const msg = s === 0 ? `${rows.length} input source${rows.length > 1 ? 's' : ''}, ${n} tick${n > 1 ? 's' : ''}. Press Play to run them.`
        : `Tick ${s}: ` + rows.map(r => r + ' ' + P.src[r][s - 1][0]).join(', ') + `. The tick lasts ${ms(tickDur(s - 1))}, the longest action in its column.`;
      wrap(g, msg, 34, yb + 24, z.W - 68, { s: 13, c: c.ink, lh: 18 });
      return `Time used so far: <b>${ms(t)}</b> of ${ms(total)}.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 4.4: JavaScript execution */
  /* Type names are the ones the Java, Python and JavaScript runs printed on the chapter page. */
  const JSV = {
    int: ['return 42', '42', 'Long', 'int', 'number'],
    dec: ['return 4.5', '4.5', 'Double', 'float', 'number'],
    str: ["return 'hi'", '"hi"', 'String', 'str', 'string'],
    arr: ["return [1, 'a']", '[1, "a"]', 'ArrayList', 'list', 'Array'],
    obj: ['return {a: 1}', '{"a": 1}', 'LinkedHashMap', 'dict', 'Object'],
    undef: ['return undefined', 'null', 'null', 'NoneType (None)', 'null'],
    el: ["return document.getElementById('dynamo')", '{"element-6066-11e4-a52e-4f735466cecf": "f.1...e.7"}', 'RemoteWebElement', 'WebElement', 'WebElement'],
    noret: ['1 + 1', 'null', 'null', 'NoneType (None)', 'null']
  };
  def('se-script', {
    title: 'What happens to an executeScript call',
    sub: 'Pick a value to return and a language, then follow the script to the browser and the answer back.',
    W: 660, H: 260,
    params: [
      { k: 'v', label: 'The script returns', type: 'select', v: 'int', opts: [['int', 'A whole number'], ['dec', 'A decimal'], ['str', 'Text'], ['arr', 'An array'], ['obj', 'An object'], ['undef', 'undefined'], ['el', 'A DOM element'], ['noret', 'Nothing (no return)']] },
      { k: 'lang', label: 'Your language', type: 'select', v: 'java', opts: [['java', 'Java'], ['py', 'Python'], ['js', 'JavaScript']] },
      { k: 'mode', label: 'Command', type: 'select', v: 'sync', opts: [['sync', 'executeScript'], ['async', 'executeAsyncScript']] }
    ],
    tips: [
      { t: 'Return a whole number and switch the language. The JSON in step 4 stays the same, only the last step changes.', set: { v: 'int', lang: 'java' }, play: true },
      { t: 'Pick Nothing (no return). The browser runs 1 + 1 but the function gives back undefined, which travels as null.', set: { v: 'noret' }, play: true },
      { t: 'Switch to executeAsyncScript and watch step 3: the browser waits for the callback, not for return.', set: { mode: 'async' }, play: true }
    ],
    steps: () => 5,
    startAtZero: true,
    speed: () => 1300,
    draw(z) {
      const g = z.g, c = z.col, V = JSV[z.p.v], s = z.step, asy = z.p.mode === 'async';
      const li = { java: 2, py: 3, js: 4 }[z.p.lang], lname = { java: 'Java', py: 'Python', js: 'JavaScript' }[z.p.lang];
      const script = asy ? (V[0].startsWith('return ') ? 'arguments[arguments.length - 1](' + V[0].slice(7) + ')' : V[0]) : V[0];
      const names = ['Your code', 'Request', 'Browser', 'Response', 'Your value'];
      const bw = (z.W - 48 - 4 * 10) / 5;
      names.forEach((n, i) => {
        const x = 24 + i * (bw + 10), on = s === i + 1, done = s > i + 1;
        rr(g, x, 20, bw, 40, 10, { fill: on ? c.bg : c.surf, stroke: on ? c.cv : done ? c.green : c.line, w: on ? 3 : 1.5 });
        D.text(g, (i + 1) + '. ' + n, x + bw / 2, 45, { a: 'center', b: true, s: fit(g, (i + 1) + '. ' + n, bw - 10, 12.5, { b: true }), c: on ? c.cv : c.ink });
      });
      const detail = [
        ['Press Play to send the script.', ''],
        [lname + ' calls ' + (asy ? 'executeAsyncScript' : 'executeScript') + ' with the script text and no extra arguments.', script],
        ['The binding posts the text and an empty args list to the driver.', 'POST /session/{id}/execute/' + (asy ? 'async' : 'sync') + '\n{"script": "' + script.replace(/"/g, '\\"') + '", "args": []}'],
        [asy ? 'The browser makes a function from the text, adds a callback as the last argument and waits until the callback is called, or until the script timeout.' : 'The browser makes a function from the text and calls it. If it returns a promise, the browser waits for it.', 'function () { ' + script + ' }'],
        ['The browser turns the result into JSON. A DOM node becomes an element reference. undefined becomes null.', '{"value": ' + V[1] + '}'],
        ['The ' + lname + ' binding turns the JSON into a ' + lname + ' value.', lname + ' type: ' + V[li]]
      ][s];
      const never = asy && z.p.v === 'noret';
      if (never && s === 4) { detail[0] = 'The script never calls the callback, so nothing comes back. After the script timeout, 30 s by default, the driver answers with an error.'; detail[1] = '{"value": {"error": "script timeout", ...}}'; }
      if (never && s === 5) { detail[0] = 'The binding raises the timeout error.'; detail[1] = { java: 'ScriptTimeoutException', py: 'TimeoutException', js: 'ScriptTimeoutError' }[z.p.lang]; }
      rr(g, 20, 78, z.W - 40, z.H - 98, 10, { fill: c.bg, stroke: never && s >= 4 ? c.red : c.line, w: never && s >= 4 ? 2 : 1.5 });
      let y = wrap(g, detail[0], 36, 104, z.W - 72, { s: 13.5, c: c.ink, lh: 19 });
      String(detail[1]).split('\n').forEach(line => {
        if (!line) return;
        y = wrap(g, line, 36, y + 10, z.W - 72, { s: fit(g, line.slice(0, 60), z.W - 72, 12.5, { mono: true }), mono: true, c: c.cv, lh: 18 });
      });
      return s === 5 ? (never ? 'The call failed with a <b>script timeout</b>.' : `The script came back as <b>${esc(V[li])}</b> in ${lname}.`) : 'Step through the call.';
    }
  });

  /* ---------------------------------------------------------------- Chapter 5.1: test frameworks */
  const HOOKS = {
    junit: { start: '@BeforeEach', test: '@Test', shot: 'AfterTestExecutionCallback', stop: '@AfterEach', startAll: '@BeforeAll', stopAll: '@AfterAll' },
    pytest: { start: 'fixture, before yield', test: 'test_ function', shot: 'fixture sees rep_call.failed', stop: 'fixture, after yield', startAll: 'module fixture, before yield', stopAll: 'module fixture, after yield' },
    mocha: { start: 'beforeEach', test: 'it()', shot: 'afterEach, state failed', stop: 'afterEach, quit', startAll: 'before', stopAll: 'after' }
  };
  function lifecycle(p) {
    const H = HOOKS[p.fw], ev = [], n = +p.tests, bad = +p.fail;
    const T = i => ({ k: 'test', h: H.test, t: `Test ${i} ` + (i === bad ? 'fails' : 'passes') + (p.scope === 'all' && i > 1 ? ', in a browser earlier tests used.' : '.'), i, bad: i === bad });
    if (p.scope === 'all') ev.push({ k: 'start', h: H.startAll, t: 'Start one browser for the whole class or file.' });
    for (let i = 1; i <= n; i++) {
      if (p.scope === 'each') ev.push({ k: 'start', h: H.start, t: `Start a fresh browser for test ${i}.` });
      ev.push(T(i));
      if (i === bad) ev.push({ k: 'shot', h: H.shot, t: `The browser is still open, so take failure-test${i}.png.` });
      if (p.scope === 'each') ev.push({ k: 'stop', h: H.stop, t: i === bad ? 'Quit runs even though the test failed.' : 'Quit the browser.' });
    }
    if (p.scope === 'all') ev.push({ k: 'stop', h: H.stopAll, t: 'Quit the shared browser.' });
    return ev;
  }
  def('se-lifecycle', {
    title: 'What a test framework runs, and in which order',
    sub: 'Choose the framework, the number of tests and which one fails. Step through the hooks and watch the browsers.',
    W: 660, H: 340,
    params: [
      { k: 'fw', label: 'Framework', type: 'select', v: 'junit', opts: [['junit', 'JUnit 5'], ['pytest', 'pytest'], ['mocha', 'Mocha']] },
      { k: 'tests', label: 'Tests', type: 'range', v: 3, min: 1, max: 4, step: 1 },
      { k: 'fail', label: 'Failing test (0 for none)', type: 'range', v: 2, min: 0, max: 4, step: 1 },
      { k: 'scope', label: 'Browser', type: 'select', v: 'each', opts: [['each', 'A fresh browser per test'], ['all', 'One browser for all tests']] }
    ],
    tips: [
      { t: 'With a failing test, watch the screenshot step: it comes before quit, while the page is still there.', set: { fail: 2, scope: 'each' }, play: true },
      { t: 'Switch to one browser for all tests. Fewer starts, but every later test inherits what the earlier ones left behind.', set: { scope: 'all' }, play: true },
      { t: 'Switch the framework. The order stays the same, only the names of the hooks change.', set: { fw: 'pytest' }, play: true }
    ],
    steps: z => lifecycle(z.p).length,
    startAtZero: true,
    speed: () => 900,
    draw(z) {
      const g = z.g, c = z.col, ev = lifecycle(z.p), s = z.step;
      const rh = Math.min(26, (z.H - 40) / ev.length), x = 24, lw = 230;
      let open = 0, started = 0;
      const res = [];
      ev.forEach((e, i) => {
        const y = 22 + i * rh, on = s === i + 1, done = s > i + 1;
        if (done || on) {
          if (e.k === 'start') { open++; started++; }
          if (e.k === 'stop') open--;
          if (e.k === 'test') res.push(e.bad ? 'fail' : 'pass');
        }
        const col = e.k === 'test' ? (e.bad ? c.red : c.green) : e.k === 'shot' ? c.orange : e.k === 'start' ? c.cv : c.purple;
        if (on) rr(g, x - 6, y - 2, z.W - 2 * x + 12 - 170, rh - 2, 6, { fill: c.bg, stroke: c.cv, w: 2 });
        rr(g, x, y + 2, 8, rh - 8, 3, { fill: done || on ? col : c.line });
        D.text(g, e.h, x + 16, y + rh / 2 + 3, { s: fit(g, e.h, lw - 20, 12, { mono: true }), mono: true, b: on, c: done || on ? c.ink : c.ink2 });
        D.text(g, e.t, x + lw, y + rh / 2 + 3, { s: fit(g, e.t, z.W - lw - x - 200, 11.5), c: done || on ? c.ink : c.ink2 });
      });
      const px = z.W - 176;
      rr(g, px, 22, 156, 150, 10, { fill: c.surf, stroke: c.line });
      D.text(g, 'Browsers open', px + 12, 46, { s: 12, b: true, c: c.ink2 });
      D.text(g, String(open), px + 12, 76, { s: 26, b: true, c: open ? c.cv : c.ink2 });
      D.text(g, 'Browsers started', px + 12, 104, { s: 12, b: true, c: c.ink2 });
      D.text(g, String(started), px + 12, 134, { s: 26, b: true, c: c.ink });
      rr(g, px, 184, 156, 80, 10, { fill: c.surf, stroke: c.line });
      D.text(g, 'Results', px + 12, 206, { s: 12, b: true, c: c.ink2 });
      res.forEach((r, i) => { rr(g, px + 12 + i * 34, 220, 28, 28, 6, { fill: r === 'pass' ? c.green : c.red }); D.text(g, r === 'pass' ? 'P' : 'F', px + 26 + i * 34, 239, { a: 'center', b: true, s: 13, c: '#fff' }); });
      const cur = ev[s - 1];
      return cur ? `<b>${esc(cur.h)}</b>: ${esc(cur.t)}` : `${ev.length} steps. Press Play.`;
    }
  });

  /* ---------------------------------------------------------------- Chapter 5.2: page objects */
  const POMSTEPS = [
    'Every test below opens the checkout and presses the submit button.',
    'The developers rename the button. Its old locator no longer matches anything.',
    'The suite runs. Every place that holds the old locator fails with no such element.',
    'Someone edits every copy of the locator.',
    'The suite runs again.'
  ];
  def('se-pom', {
    title: 'One renamed button, with and without a page object',
    sub: 'Choose how many tests use the page and how often each one uses the button, then step through a UI change.',
    W: 660, H: 340,
    params: [
      { k: 'mode', label: 'Tests use', type: 'select', v: 'raw', opts: [['raw', 'Locators copied into each test'], ['pom', 'A page object']] },
      { k: 'tests', label: 'Tests that use the page', type: 'range', v: 30, min: 5, max: 60, step: 5 },
      { k: 'uses', label: 'Uses of the button per test', type: 'range', v: 2, min: 1, max: 3, step: 1 },
      { k: 'min', label: 'Minutes to fix one copy', type: 'range', v: 2, min: 1, max: 10, step: 1 }
    ],
    tips: [
      { t: 'Step to the end with copied locators and note the number of places to edit.', set: { mode: 'raw', tests: 30, uses: 2 }, play: true },
      { t: 'Switch to a page object and step again. The tests still fail in step 3, but the fix is one edit.', set: { mode: 'pom' }, play: true },
      { t: 'Raise the number of tests to 60. The page object number does not move.', set: { tests: 60 }, play: true }
    ],
    steps: () => POMSTEPS.length,
    startAtZero: true,
    speed: () => 1400,
    draw(z) {
      const g = z.g, c = z.col, s = z.step, pom = z.p.mode === 'pom', n = +z.p.tests, u = +z.p.uses;
      const copies = pom ? 1 : n * u, cols = 10, cell = 30, gx = 24, gy = 26;
      const broken = s >= 2 && s < 4, red = s === 3, fixed = s >= 4, green = s === 5;
      for (let i = 0; i < n; i++) {
        const x = gx + (i % cols) * (cell + 4), y = gy + Math.floor(i / cols) * (cell + 4);
        const fill = red ? c.red : green ? c.green : c.surf;
        rr(g, x, y, cell, cell, 5, { fill, stroke: c.line });
        if (!pom) for (let k = 0; k < u; k++) rr(g, x + 5 + k * 8, y + cell - 10, 6, 6, 2, { fill: broken ? c.orange : fixed ? c.cv : c.purple });
      }
      const gw = cols * (cell + 4), rows = Math.ceil(n / cols);
      D.text(g, n + ' tests' + (pom ? '' : ', ' + u + ' locator cop' + (u > 1 ? 'ies' : 'y') + ' in each'), gx, gy + rows * (cell + 4) + 16, { s: 12, b: true, c: c.ink2 });
      if (pom) {
        const bx = gx + gw + 20, by = gy + 40;
        g.save(); g.strokeStyle = c.line; g.setLineDash([4, 3]); g.beginPath(); g.moveTo(gx + gw - 4, by + 30); g.lineTo(bx, by + 30); g.stroke(); g.restore();
        rr(g, bx, by, z.W - bx - 20, 70, 10, { fill: c.surf, stroke: broken ? c.orange : fixed ? c.cv : c.purple, w: 2.5 });
        D.text(g, 'CheckoutPage', bx + 12, by + 24, { s: 13, b: true, mono: true, c: c.ink });
        D.text(g, 'submitBy: 1 locator', bx + 12, by + 48, { s: 12, mono: true, c: broken ? c.orange : c.ink2 });
      }
      const fixMin = copies * +z.p.min;
      const py = z.H - 96;
      rr(g, 20, py, z.W - 40, 80, 10, { fill: c.bg, stroke: red ? c.red : green ? c.green : c.line, w: 2 });
      wrap(g, s ? (pom && s === 4 ? 'Someone edits the one locator inside CheckoutPage. No test file changes.' : POMSTEPS[s - 1]) : 'Press Play to change the button.', 34, py + 24, z.W - 68, { s: 13.5, c: c.ink, lh: 18 });
      if (s >= 3) D.text(g, 'Places to edit: ' + copies + '    Time to fix: ' + fixMin + ' min', 34, py + 62, { s: 13, b: true, c: c.cv });
      return s >= 3 ? `<b>${copies}</b> place${copies > 1 ? 's' : ''} to edit, about <b>${fixMin} minutes</b> of fixing.` : 'Step through the change.';
    }
  });

  /* ---------------------------------------------------------------- Chapter 5.3: one grand test or small tests */
  const JOURNEY = ['Create an account', 'Configure the unicorn', 'Add it to the cart', 'Check out and pay', 'Give feedback'];
  def('se-split', {
    title: 'One grand test, or one small test per step',
    sub: 'The journey from the documentation. Change how often a step fails at random and which step really breaks.',
    W: 660, H: 330,
    params: [
      { k: 'flake', label: 'Random failure per step (%)', type: 'range', v: 2, min: 0, max: 10, step: 0.5 },
      { k: 'broken', label: 'Really broken step (0 for none)', type: 'range', v: 3, min: 0, max: 5, step: 1 }
    ],
    tips: [
      { t: 'With a broken step 3, compare what the two reports tell you in the last step.', set: { broken: 3 }, play: true },
      { t: 'Set no broken step and raise the random failure to 5 %. The grand test now fails more than one run in five.', set: { broken: 0, flake: 5 }, play: true }
    ],
    steps: () => 4,
    startAtZero: true,
    speed: () => 1500,
    draw(z) {
      const g = z.g, c = z.col, s = z.step, f = z.p.flake / 100, b = +z.p.broken;
      const n = JOURNEY.length, bw = (z.W - 48 - (n - 1) * 8) / n;
      const pGrand = Math.pow(1 - f, n);
      D.text(g, 'One grand test', 24, 26, { s: 13, b: true, c: c.ink });
      JOURNEY.forEach((t, i) => {
        const x = 24 + i * (bw + 8), st = i + 1;
        const ran = s >= 2 && (!b || st <= b), bad = s >= 2 && b === st, skipped = s >= 2 && b && st > b;
        rr(g, x, 36, bw, 46, 8, { fill: bad ? c.red : ran ? c.green : c.surf, stroke: skipped ? c.line : c.line, dash: skipped ? [4, 3] : null });
        wrap(g, t, x + 6, 54, bw - 12, { s: 11.5, c: bad || ran ? '#fff' : skipped ? c.ink2 : c.ink, lh: 14 });
      });
      if (s >= 1) D.text(g, `Passes when all 5 steps pass: ${(100 * pGrand).toFixed(1)} % of runs when nothing is broken`, 24, 104, { s: 12, c: c.ink2 });
      if (s >= 3) {
        D.text(g, 'Five small tests', 24, 140, { s: 13, b: true, c: c.ink });
        JOURNEY.forEach((t, i) => {
          const x = 24 + i * (bw + 8), bad = s >= 4 && b === i + 1, done = s >= 4;
          rr(g, x, 150, bw, 46, 8, { fill: bad ? c.red : done ? c.green : c.surf, stroke: c.line });
          wrap(g, t, x + 6, 168, bw - 12, { s: 11.5, c: done ? '#fff' : c.ink, lh: 14 });
        });
        D.text(g, `Each passes ${(100 * (1 - f)).toFixed(1)} % of runs on its own`, 24, 218, { s: 12, c: c.ink2 });
      }
      const msg = [
        'The journey from Larry\'s unicorn shop, as one test or as five.',
        `One test runs all five steps. With ${z.p.flake} % random failure per step, the chances multiply: ${(100 * pGrand).toFixed(1)} % of clean runs pass.`,
        b ? (b === n ? `Step ${b} is really broken. It is the last step, and the report only says that the long test failed.` : `Step ${b} is really broken. The grand test stops there, so steps ${b + 1} to ${n} are never checked, and the report only says the test failed.`) : 'Nothing is really broken. Every failure of the grand test is noise that someone must investigate.',
        'Each small test sets up its own state, through an API for example, and checks one step.',
        b ? `Only the test for step ${b} is red. The other four still give a result, and the report names the broken step at a glance.` : 'All five are green, and a random failure would hit one small test that is quick to rerun.'
      ][s];
      rr(g, 20, z.H - 82, z.W - 40, 66, 10, { fill: c.bg, stroke: c.line });
      wrap(g, msg, 34, z.H - 58, z.W - 68, { s: 13, c: c.ink, lh: 18 });
      return `Grand test pass rate with nothing broken: <b>${(100 * pGrand).toFixed(1)} %</b>.`;
    }
  });

})();
