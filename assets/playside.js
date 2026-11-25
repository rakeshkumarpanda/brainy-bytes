/* ===== Code Playground side by side with the lesson, on every subject that teaches code =====
   A reader can write and run code next to the lesson they are reading, without leaving the page.
   It reuses the full Code Playground page (content/code-playground/code-playground.html) in embed mode
   (?embed=1&lang=...), shown in a panel on the right of the screen.

   It works in three places:
     host        subject.html, the portal page that shows a chapter in a frame. A "Playground" button joins the
                 chapter toolbar, and the panel sits to the right of the chapter frame.
     child       a chapter page shown inside that frame. It only adds "Try it in the playground" under each
                 code example and asks the host to open its panel with that code.
     standalone  a chapter page opened on its own. It adds a floating "Code playground" button and its own panel.
   The default language comes from the subject (the content folder). A code example's own language is guessed
   from the code, because some lessons compare languages. Examples that need a library the browser cannot run
   (Selenium, Playwright, TestNG, CUDA, PyTorch and so on) get no "Try it" button, so the button never promises
   a run that cannot work.
   fun.js, voiceteach.js and pathskin.js load this file, so a page needs no extra script tag and a rebuild keeps it.
   Its look is injected from here. ===== */
(() => {
  if (window.__playSide) return;
  window.__playSide = true;
  const ME = (document.currentScript && document.currentScript.src) || '';
  const ROOT = ME ? new URL('..', ME).href : new URL('../../', location.href).href;
  const PG_PAGE = 'content/code-playground/code-playground.html';
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage unavailable */ } }
  };

  /* content folder -> the language the playground opens with */
  const SUBJECT_LANG = {
    java: 'java', testng: 'java', 'api-automation': 'java', dsa: 'java', selenium: 'java',
    javascript: 'js', playwright: 'ts',
    python: 'python', 'machine-learning': 'python', 'deep-learning': 'python', mlops: 'python', ai: 'python', nlp: 'python',
    'computer-vision': 'python', 'ml-maths': 'python', 'neural-networks': 'python', 'data-science': 'python',
    cuda: 'cpp'
  };
  const LANG_NAME = { java: 'Java', python: 'Python', c: 'C', cpp: 'C++', js: 'JavaScript', ts: 'TypeScript', cs: 'C#' };
  const folderOf = href => { const m = /\/content\/([^/]+)\//.exec(new URL(href, location.href).pathname); return m ? m[1] : ''; };

  const path = location.pathname;
  let inFrame = false;
  try { inFrame = window.self !== window.top; } catch (e) { inFrame = true; }
  if (path.includes('/code-playground/')) return;
  let mode = '';
  if (!inFrame && /\/subject\.html$/.test(path)) mode = 'host';
  else if (SUBJECT_LANG[folderOf(location.href)]) {
    let parentHost = false;
    if (inFrame) { try { parentHost = /\/subject\.html$/.test(parent.location.pathname); } catch (e) { parentHost = false; } }
    mode = parentHost ? 'child' : inFrame ? '' : 'standalone';
  }
  if (!mode) return;

  /* ---------- guessing the language of a code example ---------- */
  function guessLang(t, def) {
    if (/^\s*#include\s*[<"]/m.test(t)) return /\b(std::|cout|cin|namespace|template\s*<|vector\s*<|class\s+\w+)/.test(t) ? 'cpp' : 'c';
    if (/\busing\s+System\s*;|\bConsole\.(Write|Read)|\bstatic\s+void\s+Main\s*\(/.test(t)) return 'cs';
    if (/\bSystem\.(out|err)\.|\bpublic\s+static\s+void\s+main\s*\(|^\s*import\s+java\.|^\s*package\s+[\w.]+\s*;/m.test(t)) return 'java';
    if (/\bconsole\.log\s*\(|=>|^\s*(const|let)\s+\w+|\bfunction\s*\*?\s*\w*\s*\(/m.test(t) && !/^\s*def\s+\w+\s*\(/m.test(t)) {
      return /:\s*(string|number|boolean|void|any|unknown)\b|^\s*(interface|type)\s+\w+|\bas\s+const\b|<\w+(\[\])?>\s*\(/m.test(t) ? 'ts' : 'js';
    }
    if (/^\s*(def\s+\w+\s*\(|class\s+\w+(\(.*\))?\s*:|from\s+[\w.]+\s+import\s|import\s+[\w.]+(\s+as\s+\w+)?\s*$|print\s*\()/m.test(t)) return 'python';
    if (/^\s*(cout|std::)/m.test(t)) return 'cpp';
    if (/^\s*printf\s*\(/m.test(t)) return def === 'cpp' ? 'cpp' : 'c';
    return def;
  }
  /* libraries and features the browser runners cannot run: an example that uses one gets no Try button */
  const CANNOT = {
    java: /\b(org\.openqa|com\.microsoft\.playwright|org\.testng|io\.restassured|org\.junit|org\.springframework|javax\.servlet|jakarta\.|@Test\b|@BeforeMethod|@DataProvider|WebDriver\b|\bdriver\.|\bnew\s+Actions\s*\()/,
    python: /^\s*(import|from)\s+(selenium|playwright|pytest|torch|tensorflow|keras|transformers|cupy|pycuda|numba|flask|django|fastapi|requests|boto3|mlflow|airflow|kafka|psycopg2|pymysql|cv2\.cuda)\b|@pytest\b|\bpage\.goto\(|\bdriver\./m,
    js: /\brequire\(\s*['"](selenium-webdriver|playwright|@playwright\/test|express|fs|http|axios)['"]|from\s+['"](@playwright\/test|playwright|selenium-webdriver|express|axios|node:\w+|fs|react)['"]|\bdocument\.|\bwindow\.|\bfetch\s*\(|\bpage\./,
    ts: null, c: /__global__|__device__|__shared__|__syncthreads|threadIdx|blockIdx|atomicAdd|<<<|cuda\w*\(|#include\s*<(pthread|unistd|sys\/|windows)/, cpp: null, cs: /\busing\s+(OpenQA|Microsoft\.Playwright|NUnit|Xunit)/
  };
  CANNOT.ts = CANNOT.js; CANNOT.cpp = CANNOT.c;
  /* does it look like code at all (not a command line, an output, a file tree or XML) */
  function looksLikeCode(t) {
    if (t.split('\n').length < 2 && t.length < 40) return false;
    if (/^\s*[$>]\s/m.test(t) && !/[;{}]/.test(t)) return false;
    if (/^\s*</.test(t) && !/^\s*<(script|\?php)/.test(t)) return false;
    if (/^\s*[[{]/.test(t) && /"[\w-]+"\s*:/.test(t)) return false; /* JSON data */
    return /[=();{}:]/.test(t);
  }
  /* a lesson often shows a few statements, not a whole program. Wrap them so Java and C or C++ can run them */
  function wrap(code, lang) {
    if (lang === 'java' && !/\bstatic\s+void\s+main\s*\(/.test(code)) {
      const imports = [], body = [];
      code.split('\n').forEach(l => (/^\s*import\s+[\w.*]+\s*;/.test(l) ? imports : body).push(l));
      const hasTypes = /^\s*(public\s+|abstract\s+|final\s+)*(class|interface|enum|record)\s+\w+/m.test(code);
      const hasMethods = /^\s*(public|private|protected|static)\b[^=;]*\)\s*(throws\s+[\w.,\s]+)?\{/m.test(code);
      const head = (imports.length ? imports.join('\n') : 'import java.util.*;') + '\n\n';
      if (hasTypes) return { code: head + body.join('\n').trim() + '\n\npublic class Main {\n    public static void main(String[] args) {\n        // Try the code above from here\n    }\n}\n', wrapped: 'types' };
      if (hasMethods) return { code: head + 'public class Main {\n' + indent(body.join('\n').trim(), 4) + '\n\n    public static void main(String[] args) {\n        // Call the methods above from here\n    }\n}\n', wrapped: 'methods' };
      return { code: head + 'public class Main {\n    public static void main(String[] args) {\n' + indent(body.join('\n').trim(), 8) + '\n    }\n}\n', wrapped: 'main' };
    }
    if ((lang === 'c' || lang === 'cpp') && !/\bmain\s*\(/.test(code)) {
      const inc = [], body = [];
      code.split('\n').forEach(l => (/^\s*#/.test(l) || /^\s*using\s+namespace\b/.test(l) ? inc : body).push(l));
      const head = inc.length ? inc.join('\n') : lang === 'c' ? '#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>' : '#include <iostream>\n#include <vector>\n#include <string>\n#include <map>\n#include <algorithm>\nusing namespace std;';
      const hasFns = /^\s*[\w:<>*&\s]+\s+\**\w+\s*\([^;]*\)\s*\{/m.test(body.join('\n')) && !/^\s*(if|for|while|switch)\b/m.test(body[0] || '');
      if (hasFns) return { code: head + '\n\n' + body.join('\n').trim() + '\n\nint main() {\n    // Call the functions above from here\n    return 0;\n}\n', wrapped: 'methods' };
      return { code: head + '\n\nint main() {\n' + indent(body.join('\n').trim(), 4) + '\n    return 0;\n}\n', wrapped: 'main' };
    }
    return { code, wrapped: '' };
  }
  function indent(s, n) { const p = ' '.repeat(n); return s.split('\n').map(l => l ? p + l : l).join('\n'); }
  function noteFor(w, lang) {
    if (w === 'main') return `The lesson code is in the editor, placed inside main so that ${LANG_NAME[lang]} can run it. Press Run all, or Step line by line.`;
    if (w === 'methods' || w === 'types') return 'The lesson code is in the editor. It defines code but does not call it, so add a call inside main and then press Run all.';
    return '';
  }

  /* ---------- look ---------- */
  const css = `
  .psd-try{display:inline-flex; align-items:center; gap:6px; margin:6px 0 2px; padding:5px 12px; border-radius:999px; cursor:pointer;
    font:700 12.5px/1.2 var(--md-font, system-ui, sans-serif); border:1px solid var(--md-outline-variant, #c4c6cf);
    background:var(--md-secondary-container, #dde3f5); color:var(--md-on-secondary-container, #141b2c)}
  .psd-try:hover{filter:brightness(.96)}
  .psd-try:focus-visible, .psd-fab:focus-visible, .psd-x:focus-visible, .psd-full:focus-visible, .psd-grip:focus-visible{outline:3px solid var(--md-primary, #3b5bdb); outline-offset:2px}
  .psd-tryrow{display:flex; justify-content:flex-end}
  .psd-fab{position:fixed; right:18px; bottom:86px; z-index:8990; display:inline-flex; align-items:center; gap:8px; padding:11px 16px; border-radius:16px; border:0; cursor:pointer;
    font:700 14px/1 var(--md-font, system-ui, sans-serif); background:var(--md-primary, #3b5bdb); color:var(--md-on-primary, #fff); box-shadow:0 3px 10px rgba(0,0,0,.25)}
  .psd-fab[hidden]{display:none}
  .psd-pane{position:fixed; right:0; bottom:0; top:var(--psd-top, 0px); width:var(--psd-w, 560px); z-index:8995; display:flex; flex-direction:column;
    background:var(--md-surface, #fff); border-left:1px solid var(--md-outline-variant, #c4c6cf); box-shadow:-4px 0 16px rgba(0,0,0,.12)}
  .psd-pane[hidden]{display:none}
  .psd-head{display:flex; align-items:center; gap:8px; padding:8px 10px 8px 16px; background:var(--md-sc-low, #f3f3fa); border-bottom:1px solid var(--md-outline-variant, #c4c6cf);
    font:700 14.5px var(--md-font, system-ui, sans-serif); color:var(--md-on-surface, #1a1b20)}
  .psd-head .grow{flex:1}
  .psd-full, .psd-x{font:700 13px var(--md-font, system-ui, sans-serif); padding:6px 12px; border-radius:999px; cursor:pointer; text-decoration:none;
    border:1px solid var(--md-outline-variant, #c4c6cf); background:var(--md-sc-lowest, #fff); color:var(--md-on-surface, #1a1b20)}
  .psd-x{background:var(--md-primary, #3b5bdb); color:var(--md-on-primary, #fff); border-color:transparent}
  .psd-pane iframe{flex:1; width:100%; border:0; background:var(--md-surface, #fff)}
  .psd-grip{position:absolute; left:-5px; top:0; bottom:0; width:10px; cursor:col-resize; background:transparent; border:0; padding:0; z-index:1}
  .psd-grip::after{content:""; position:absolute; left:3px; top:50%; width:4px; height:44px; margin-top:-22px; border-radius:2px; background:var(--md-outline, #74777f); opacity:.55}
  .psd-pane.drag iframe{pointer-events:none}
  .psd-open-pad{padding-right:var(--psd-w, 560px) !important; box-sizing:border-box}
  .psd-tbtn .msr{font-size:20px}
  @media (max-width:560px){ .psd-fab{padding:12px; border-radius:50%; font-size:20px} .psd-fab .t{display:none} }
  @media (max-width:899px){
    .psd-pane{width:100vw; left:0; border-left:0}
    .psd-grip{display:none}
    .psd-open-pad{padding-right:0 !important}
  }
  @media print{ .psd-try, .psd-fab, .psd-pane{display:none !important} }`;
  const st = document.createElement('style');
  st.textContent = css;
  document.head.appendChild(st);

  /* ---------- the panel (host and standalone) ---------- */
  let autoFolded = false;
  let pane = null, frame = null, frameReady = false, queued = null, curLang = '', padEl = null, opener = null;
  const wide = matchMedia('(min-width:900px)');
  function clampW(w) { return Math.round(Math.max(340, Math.min(w, window.innerWidth * 0.72))); }
  function setW(w) { document.documentElement.style.setProperty('--psd-w', clampW(w) + 'px'); }
  setW(+store.get('psd-w') || Math.min(640, Math.max(400, window.innerWidth * 0.4)));
  function placeTop() {
    let top = 0;
    if (mode === 'host') { const lay = document.getElementById('layout'); if (lay) top = Math.max(0, lay.getBoundingClientRect().top); }
    document.documentElement.style.setProperty('--psd-top', top + 'px');
  }
  function buildPane() {
    pane = document.createElement('aside');
    pane.className = 'psd-pane';
    pane.hidden = true;
    pane.setAttribute('aria-label', 'Code playground');
    pane.innerHTML = `<button class="psd-grip" type="button" title="Drag to make the playground wider or narrower" aria-label="Resize the playground (left and right arrow keys)"></button>
      <div class="psd-head"><span aria-hidden="true">🧑‍💻</span><span>Code Playground</span><span class="grow"></span>
      <a class="psd-full" target="_blank" rel="noopener" title="Open the playground on a page of its own">Full page</a>
      <button class="psd-x" type="button" title="Close the playground (Esc)">Close</button></div>`;
    (mode === 'host' && document.getElementById('layout') || document.body).appendChild(pane);
    pane.querySelector('.psd-x').onclick = () => toggle(false);
    const grip = pane.querySelector('.psd-grip');
    grip.addEventListener('pointerdown', e => {
      e.preventDefault();
      grip.setPointerCapture(e.pointerId);
      pane.classList.add('drag');
      const move = ev => setW(window.innerWidth - ev.clientX);
      const up = () => {
        pane.classList.remove('drag');
        grip.removeEventListener('pointermove', move); grip.removeEventListener('pointerup', up);
        store.set('psd-w', parseInt(getComputedStyle(document.documentElement).getPropertyValue('--psd-w'), 10));
      };
      grip.addEventListener('pointermove', move); grip.addEventListener('pointerup', up);
    });
    grip.addEventListener('keydown', e => {
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      e.preventDefault();
      const w = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--psd-w'), 10) + (e.key === 'ArrowLeft' ? 40 : -40);
      setW(w); store.set('psd-w', clampW(w));
    });
  }
  function ensureFrame(lang) {
    const src = ROOT + PG_PAGE + '?embed=1&lang=' + encodeURIComponent(lang);
    pane.querySelector('.psd-full').href = ROOT + PG_PAGE;
    if (frame) return;
    curLang = lang;
    frame = document.createElement('iframe');
    frame.title = 'Code playground';
    frame.setAttribute('allow', 'clipboard-write');
    frame.src = src;
    pane.appendChild(frame);
  }
  function toggle(on, lang) {
    if (!pane) buildPane();
    on = on === undefined ? pane.hidden : on;
    if (on) {
      ensureFrame(lang || defaultLang());
      placeTop();
      pane.hidden = false;
      padEl = mode === 'host' ? document.getElementById('layout') : document.body;
      if (padEl && wide.matches) padEl.classList.add('psd-open-pad');
      /* on a laptop screen the chapter list folds away while the playground is open, so the chapter keeps room */
      const lay = document.getElementById('layout'), db = document.getElementById('drawerBtn');
      if (mode === 'host' && lay && db && window.innerWidth >= 1101 && window.innerWidth < 1800 && !lay.classList.contains('closed')) { db.click(); autoFolded = true; }
      if (fab) fab.hidden = true;
    } else {
      pane.hidden = true;
      if (padEl) padEl.classList.remove('psd-open-pad');
      const lay = document.getElementById('layout'), db = document.getElementById('drawerBtn');
      if (autoFolded && lay && db && lay.classList.contains('closed')) db.click();
      autoFolded = false;
      if (fab) fab.hidden = false;
      if (opener && document.contains(opener)) opener.focus();
    }
    paintToolbar();
  }
  wide.addEventListener('change', () => { if (pane && !pane.hidden && padEl) padEl.classList.toggle('psd-open-pad', wide.matches); });
  window.addEventListener('resize', () => { if (pane && !pane.hidden) placeTop(); });
  document.addEventListener('fullscreenchange', () => setTimeout(placeTop, 50));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && pane && !pane.hidden) toggle(false); });
  window.addEventListener('message', e => {
    const d = e.data || {};
    if (frame && e.source === frame.contentWindow && d.pg === 'ready') {
      frameReady = true;
      if (queued) { frame.contentWindow.postMessage(queued, location.origin === 'null' ? '*' : location.origin); queued = null; }
      return;
    }
    if (mode === 'host' && d.lh === 'pg-try' && e.origin === location.origin && typeof d.code === 'string') sendCode(d);
  });
  function sendCode(d) {
    toggle(true, d.lang);
    const msg = { pg: 'load', lang: d.lang, code: d.code, note: d.note };
    if (frameReady) frame.contentWindow.postMessage(msg, location.origin === 'null' ? '*' : location.origin);
    else queued = msg;
  }

  /* ---------- which language: the subject's own ---------- */
  function defaultLang() {
    if (mode === 'host') {
      const f = document.getElementById('frame');
      return SUBJECT_LANG[f ? folderOf(f.getAttribute('src') || '') : ''] || 'java';
    }
    return SUBJECT_LANG[folderOf(location.href)] || 'java';
  }

  /* ---------- host: a Playground button in the chapter toolbar ---------- */
  let fab = null;
  function paintToolbar() {
    document.querySelectorAll('.psd-tbtn').forEach(b => {
      const on = pane && !pane.hidden;
      b.setAttribute('aria-pressed', on);
      b.classList.toggle('tonal', !on);
    });
  }
  if (mode === 'host') {
    const main = document.getElementById('main');
    const addBtn = () => {
      const bar = main && main.querySelector('.toolbar');
      const f = document.getElementById('frame');
      const coding = f && SUBJECT_LANG[folderOf(f.getAttribute('src') || '')];
      if (!bar || bar.querySelector('.psd-tbtn')) return;
      if (!coding) { if (pane && !pane.hidden) toggle(false); return; }
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'md-btn tonal psd-tbtn';
      b.title = 'Open the Code Playground next to this chapter, to write and run code while you read';
      b.innerHTML = '<span class="msr" aria-hidden="true">code</span><span class="lbl">Playground</span>';
      b.onclick = () => { opener = b; toggle(); };
      const before = bar.querySelector('#fsBtn');
      bar.insertBefore(b, before || null);
      paintToolbar();
    };
    if (main) new MutationObserver(addBtn).observe(main, { childList: true });
    addBtn();
    return;
  }

  /* ---------- child and standalone: Try buttons under code examples ---------- */
  const SEL = 'pre.src, pre.cc-src, pre.jv-code, pre.code, pre.ex-code, pre.sol-code, pre:not([class]) > code';
  const SKIP = '.vz, .cvz, .viz, .lq-item, .lc-item, .quiz, .psd-pane, [data-no-try]';
  const def = SUBJECT_LANG[folderOf(location.href)];
  function codeText(pre) {
    const c = pre.cloneNode(true);
    c.querySelectorAll('.lnum, .line-number, .gutter, button').forEach(x => x.remove());
    /* some pages draw each line as its own block (span.ln) with no newline between them */
    c.querySelectorAll('.ln').forEach(x => {
      const nx = x.nextSibling;
      if (!/\n$/.test(x.textContent) && !(nx && nx.nodeType === 3 && /^\n/.test(nx.textContent))) x.appendChild(document.createTextNode('\n'));
    });
    return (c.innerText || c.textContent || '').replace(/\u00a0/g, ' ').replace(/\s+$/, '') + '\n';
  }
  /* one Try row per code block. Some blocks change their code when the reader picks another language tab,
     so the row is checked again each time the block changes: its label follows the code, and it hides for
     code that cannot run here */
  function decorate(pre) {
    const text = codeText(pre);
    if (!text.trim()) return; /* filled later by the page's own script */
    if (pre.dataset.psText === String(text.length) + text.slice(0, 60)) return;
    pre.dataset.psText = String(text.length) + text.slice(0, 60);
    let row = pre.nextElementSibling && pre.nextElementSibling.classList.contains('psd-tryrow') ? pre.nextElementSibling : null;
    const lang = guessLang(text, def);
    const ok = looksLikeCode(text) && !(CANNOT[lang] && CANNOT[lang].test(text));
    if (!ok) { if (row) row.hidden = true; return; }
    if (!row) {
      row = document.createElement('div');
      row.className = 'psd-tryrow';
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'psd-try';
      b.onclick = () => {
        const l = b.dataset.lang, w = wrap(codeText(pre), l);
        const d = { lh: 'pg-try', lang: l, code: w.code, note: noteFor(w.wrapped, l) };
        opener = b;
        if (mode === 'child') parent.postMessage(d, location.origin === 'null' ? '*' : location.origin);
        else sendCode(d);
      };
      row.appendChild(b);
      pre.insertAdjacentElement('afterend', row);
    }
    row.hidden = false;
    const b = row.firstChild;
    b.dataset.lang = lang;
    b.title = `Copy this ${LANG_NAME[lang]} code into the Code Playground and open it next to the lesson`;
    b.innerHTML = `<span aria-hidden="true">▶</span> Try it in the playground <small>(${LANG_NAME[lang]})</small>`;
  }
  function scan() {
    document.querySelectorAll(SEL).forEach(node => {
      const pre = node.tagName === 'CODE' ? node.parentElement : node;
      if (pre.dataset.psSkip) return;
      if (pre.closest(SKIP)) { pre.dataset.psSkip = '1'; return; }
      decorate(pre);
    });
  }
  let scanT = 0;
  const queueScan = () => { clearTimeout(scanT); scanT = setTimeout(scan, 300); };
  function start() {
    scan();
    new MutationObserver(queueScan).observe(document.body, { childList: true, subtree: true });
    if (mode === 'standalone') {
      fab = document.createElement('button');
      fab.type = 'button';
      fab.className = 'psd-fab';
      fab.title = 'Open the Code Playground next to this lesson, to write and run code while you read';
      fab.innerHTML = '<span aria-hidden="true">🧑‍💻</span><span class="t">Code playground</span>';
      fab.setAttribute('aria-label', 'Code playground');
      fab.onclick = () => { opener = fab; toggle(true); };
      document.body.appendChild(fab);
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
