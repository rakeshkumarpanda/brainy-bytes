/* ===== JavaScript chapters: editable examples, hands-on exercises and the QA path =====
   JSPLAY.page({ title, subject }) draws the comic, real life cards, exercises, quiz and number crunch from PAGE,
   then turns on the animations, the narrator and every button on the page.

   Editable examples: a .codewrap with data-play="worker" runs in a Web Worker, so a runaway loop can be stopped.
   data-play="dom" runs inside a sandboxed frame that holds the example's page.html (PAGE.play[key].html).
   console.log output is formatted the way Node.js prints it, close enough to compare with the recorded output.

   Exercises: PAGE.ex = [{ id, lv: 'e'|'m'|'h'|'x', title, task, starter, tests: [{ call, want }], hint, solution, why }]
   Each test call is an expression evaluated after the learner's code. Its value is compared with want as JSON. */
const JSPLAY = (() => {
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const LV = { e: ['Easy', '🌱', 'easy'], m: ['Medium', '🌿', 'med'], h: ['Hard', '🔥', 'hard'], x: ['Expert', '🧠', 'exp'] };

  /* ---------- a small Node style inspector, shared by the worker and the frame ---------- */
  function inspectorSource() {
    return String(function makeInspect() {
      const ident = /^[A-Za-z_$][\w$]*$/;
      function q(s) { return "'" + String(s).replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, '\\n') + "'"; }
      function key(k) { return typeof k === 'symbol' ? '[' + k.toString() + ']' : ident.test(k) ? k : q(k); }
      function wrap(open, items, close, ind) {
        if (!items.length) return open.trim() === '[' ? '[]' : (open.replace(/\s*\{\s*$/, '') + ' {}').trim();
        const one = open + ' ' + items.join(', ') + ' ' + close;
        if (one.length + ind.length <= 72 && !items.some(x => x.includes('\n'))) return one;
        const pad = ind + '  ';
        return open + '\n' + items.map(x => pad + x.replace(/\n/g, '\n' + pad)).join(',\n') + '\n' + ind + close;
      }
      function inspect(v, depth, seen, ind) {
        depth = depth || 0; seen = seen || new Set(); ind = ind || '';
        const t = typeof v;
        if (v === null) return 'null';
        if (t === 'string') return depth ? q(v) : v;
        if (t === 'number') return Object.is(v, -0) ? '-0' : String(v);
        if (t === 'bigint') return v + 'n';
        if (t === 'undefined' || t === 'boolean') return String(v);
        if (t === 'symbol') return v.toString();
        if (t === 'function') {
          const src = Function.prototype.toString.call(v);
          if (/^class\b/.test(src)) return '[class ' + (v.name || '(anonymous)') + ']';
          const kind = /^async\s/.test(src) ? 'AsyncFunction' : 'Function';
          return v.name ? '[' + kind + ': ' + v.name + ']' : '[' + kind + ' (anonymous)]';
        }
        if (seen.has(v)) return '[Circular *1]';
        if (v instanceof Error) return (v.stack && depth === 0 ? String(v.name) + ': ' + v.message : '[' + v.name + ': ' + v.message + ']');
        if (v instanceof Date) return isNaN(v) ? 'Invalid Date' : v.toISOString();
        if (v instanceof RegExp) return String(v);
        if (typeof Promise !== 'undefined' && v instanceof Promise) return 'Promise { <pending> }';
        if (depth > 2) return Array.isArray(v) ? '[Array]' : '[Object]';
        seen.add(v);
        try {
          if (Array.isArray(v)) {
            const items = [];
            for (let i = 0; i < v.length; i++) items.push(i in v ? inspect(v[i], depth + 1, seen, ind + '  ') : '<1 empty item>');
            Object.keys(v).filter(k => !/^\d+$/.test(k)).forEach(k => items.push(key(k) + ': ' + inspect(v[k], depth + 1, seen, ind + '  ')));
            return wrap('[', items, ']', ind);
          }
          if (ArrayBuffer.isView(v) && !(v instanceof DataView)) {
            return wrap(v.constructor.name + '(' + v.length + ') [', Array.from(v, x => inspect(x, depth + 1, seen)), ']', ind);
          }
          if (v instanceof Map) return wrap('Map(' + v.size + ') {', [...v].map(([a, b]) => inspect(a, depth + 1, seen, ind + '  ') + ' => ' + inspect(b, depth + 1, seen, ind + '  ')), '}', ind);
          if (v instanceof Set) return wrap('Set(' + v.size + ') {', [...v].map(a => inspect(a, depth + 1, seen, ind + '  ')), '}', ind);
          if (typeof WeakMap !== 'undefined' && v instanceof WeakMap) return 'WeakMap { <items unknown> }';
          if (typeof WeakSet !== 'undefined' && v instanceof WeakSet) return 'WeakSet { <items unknown> }';
          const proto = Object.getPrototypeOf(v);
          let name = proto === null ? '[Object: null prototype]' : (proto.constructor && proto.constructor.name) || '';
          if (name === 'Object') name = '';
          const items = [];
          for (const k of Reflect.ownKeys(v)) {
            const d = Object.getOwnPropertyDescriptor(v, k);
            if (!d.enumerable) continue;
            let val;
            if (d.get && d.set) val = '[Getter/Setter]'; else if (d.get) val = '[Getter]'; else if (d.set) val = '[Setter]';
            else val = inspect(d.value, depth + 1, seen, ind + '  ');
            items.push(key(k) + ': ' + val);
          }
          return wrap((name ? name + ' ' : '') + '{', items, '}', ind);
        } finally { seen.delete(v); }
      }
      function table(data) {
        const rows = Object.entries(data || {});
        const cols = [];
        let values = false;
        rows.forEach(([, r]) => { if (r !== null && typeof r === 'object') Object.keys(r).forEach(c => { if (!cols.includes(c)) cols.push(c); }); else values = true; });
        const head = ['(index)', ...cols, ...(values ? ['Values'] : [])];
        const body = rows.map(([i, r]) => [i, ...cols.map(c => r !== null && typeof r === 'object' && c in r ? inspect(r[c], 1) : ''), ...(values ? [r !== null && typeof r === 'object' ? '' : inspect(r, 1)] : [])]);
        const w = head.map((h, c) => Math.max(h.length, ...body.map(b => String(b[c]).length)) + 2);
        const line = (l, m, r) => l + w.map(n => '─'.repeat(n)).join(m) + r;
        const row = cells => '│' + cells.map((x, c) => ' ' + String(x).padEnd(w[c] - 1)).join('│') + '│';
        return [line('┌', '┬', '┐'), row(head), line('├', '┼', '┤'), ...body.map(row), line('└', '┴', '┘')].join('\n');
      }
      function format(args) {
        if (typeof args[0] === 'string' && /%[sdifoOjc%]/.test(args[0]) && args.length > 1) {
          let i = 1;
          const first = args[0].replace(/%[sdifoOjc%]/g, m => {
            if (m === '%%') return '%';
            if (i >= args.length) return m;
            const a = args[i++];
            if (m === '%s') return typeof a === 'string' ? a : inspect(a, 1);
            if (m === '%d' || m === '%i') return String(m === '%i' ? parseInt(a) : Number(a));
            if (m === '%f') return String(parseFloat(a));
            if (m === '%c') return '';
            return inspect(a, 1);
          });
          return [first, ...args.slice(i).map(a => inspect(a))].join(' ');
        }
        return args.map(a => inspect(a)).join(' ');
      }
      return { inspect, table, format };
    });
  }

  /* the console the learner's code sees; send(kind, text) delivers each line */
  function consoleSource() {
    return String(function makeConsole(send, I) {
      const counts = {}, timers = {};
      let depth = 0;
      const pad = () => '  '.repeat(depth);
      const out = k => (...a) => send(k, I.format(a).replace(/^/gm, pad()));
      return {
        log: out('log'), info: out('log'), debug: out('log'), warn: out('warn'), error: out('error'), trace: out('error'),
        dir: v => send('log', I.inspect(v, 1).replace(/^/gm, pad())),
        table: d => send('log', d && typeof d === 'object' ? I.table(d) : I.format([d])),
        group: (...a) => { if (a.length) send('log', pad() + I.format(a)); depth++; },
        groupCollapsed: (...a) => { if (a.length) send('log', pad() + I.format(a)); depth++; },
        groupEnd: () => { depth = Math.max(0, depth - 1); },
        count: (l = 'default') => { counts[l] = (counts[l] || 0) + 1; send('log', pad() + l + ': ' + counts[l]); },
        countReset: (l = 'default') => { counts[l] = 0; },
        time: (l = 'default') => { timers[l] = performance.now(); },
        timeLog: (l = 'default') => send('log', pad() + l + ': ' + (performance.now() - timers[l]).toFixed(3) + 'ms'),
        timeEnd: (l = 'default') => { send('log', pad() + l + ': ' + (performance.now() - timers[l]).toFixed(3) + 'ms'); delete timers[l]; },
        assert: (c, ...a) => { if (!c) send('error', 'Assertion failed' + (a.length ? ': ' + I.format(a) : '')); },
        clear: () => send('clear', '')
      };
    });
  }

  function describe(e) {
    if (e && typeof e === 'object' && 'message' in e) return 'Uncaught ' + (e.name || 'Error') + ': ' + e.message;
    return 'Uncaught ' + String(e);
  }

  /* ---------- the worker: runs plain JavaScript, tracks timers so it knows when the program is finished ---------- */
  let workerUrl = null;
  function workerSource() {
    return `
const I = (${inspectorSource()})();
const send = (k, t) => postMessage({ k, t });
const con = (${consoleSource()})(send, I);
const describe = ${String(describe)};
const live = new Set();
const _st = setTimeout, _ct = clearTimeout, _si = setInterval, _ci = clearInterval;
let mainDone = false;
function idle() { _st(() => { if (mainDone && !live.size) send('done', ''); }, 40); }
self.setTimeout = (f, ms, ...a) => { const id = _st(() => { live.delete(id); try { typeof f === 'function' && f(...a); } catch (e) { send('error', describe(e)); } idle(); }, ms); live.add(id); return id; };
self.clearTimeout = id => { if (live.delete(id)) _ct(id); idle(); };
self.setInterval = (f, ms, ...a) => { const id = _si(() => { try { f(...a); } catch (e) { send('error', describe(e)); } }, ms); live.add(id); return id; };
self.clearInterval = id => { if (live.delete(id)) _ci(id); idle(); };
self.addEventListener('unhandledrejection', ev => { ev.preventDefault(); send('error', describe(ev.reason)); });
const AsyncFunction = (async () => {}).constructor;
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
self.onmessage = async ev => {
  const d = ev.data;
  if (d.mode === 'ex') {
    const quiet = { log() {}, info() {}, warn() {}, error() {}, table() {}, dir() {} };
    const res = [];
    try {
      const body = d.code + '\\n;return [' + d.tests.map(t => 'async () => (' + t.call + ')').join(',') + '];';
      const fns = await new AsyncFunction('console', body)(quiet);
      for (let i = 0; i < fns.length; i++) {
        let got, err = null;
        try { got = await fns[i](); } catch (e) { err = describe(e).replace('Uncaught ', ''); }
        res.push({ ok: !err && same(got, d.tests[i].want), got: err ? null : I.inspect(got, 1), err });
      }
      send('ex', JSON.stringify(res));
    } catch (e) { send('exerr', describe(e).replace('Uncaught ', '')); }
    return;
  }
  try { await new AsyncFunction('console', d.code)(con); } catch (e) { send('error', describe(e)); }
  mainDone = true; idle();
};`;
  }
  function newWorker() {
    if (!workerUrl) workerUrl = URL.createObjectURL(new Blob([workerSource()], { type: 'text/javascript' }));
    return new Worker(workerUrl);
  }

  /* run code in a worker; onLine(kind, text) gets every console line; resolves when finished or stopped */
  function runWorker(code, onLine, limit = 5000) {
    return new Promise(resolve => {
      let w;
      try { w = newWorker(); } catch (e) { onLine('error', 'This browser blocked the code runner: ' + e.message); resolve('blocked'); return; }
      const end = why => { clearTimeout(timer); w.terminate(); resolve(why); };
      const timer = setTimeout(() => { onLine('warn', `Stopped after ${limit / 1000} seconds. Timers or an endless loop were still running.`); end('timeout'); }, limit);
      w.onmessage = ev => {
        const { k, t } = ev.data;
        if (k === 'done') end('done');
        else if (k === 'ex' || k === 'exerr') { onLine(k, t); end('done'); }
        else onLine(k, t);
      };
      w.onerror = ev => { ev.preventDefault(); onLine('error', 'Uncaught ' + (ev.message || 'error').replace(/^Uncaught /, '')); end('error'); };
      w.postMessage({ code });
      runWorker.stop = () => { onLine('warn', 'Stopped.'); end('stopped'); };
    });
  }
  function runTests(code, tests) {
    return new Promise(resolve => {
      let w;
      try { w = newWorker(); } catch (e) { resolve({ error: 'This browser blocked the code runner: ' + e.message }); return; }
      const timer = setTimeout(() => { w.terminate(); resolve({ error: 'The tests did not finish within 5 seconds. Look for an endless loop.' }); }, 5000);
      w.onmessage = ev => {
        const { k, t } = ev.data;
        if (k !== 'ex' && k !== 'exerr') return;
        clearTimeout(timer); w.terminate();
        resolve(k === 'ex' ? { res: JSON.parse(t) } : { error: t });
      };
      w.onerror = ev => { ev.preventDefault(); clearTimeout(timer); w.terminate(); resolve({ error: ev.message }); };
      w.postMessage({ mode: 'ex', code, tests });
    });
  }

  /* ---------- the frame: runs browser code against the example's own page ---------- */
  let frameSeq = 0;
  function runFrame(host, page, code, onLine) {
    const id = 'f' + (++frameSeq) + Math.random().toString(36).slice(2, 7);
    const boot = `<script>
(() => {
  const I = (${inspectorSource()})();
  const send = (k, t) => parent.postMessage({ jsplay: '${id}', k, t }, '*');
  window.__con = (${consoleSource()})(send, I);
  const describe = ${String(describe)};
  window.__describe = describe;
  ['log', 'info', 'warn', 'error', 'table', 'dir', 'group', 'groupEnd', 'count', 'time', 'timeEnd', 'assert', 'debug'].forEach(k => { console[k] = window.__con[k]; });
  window.addEventListener('error', e => send('error', describe(e.error || e.message)));
  window.addEventListener('unhandledrejection', e => send('error', describe(e.reason)));
  for (const s of ['localStorage', 'sessionStorage']) {
    try { window[s].length; } catch (e) {
      const m = new Map();
      const store = { getItem: k => m.has(String(k)) ? m.get(String(k)) : null, setItem: (k, v) => { m.set(String(k), String(v)); }, removeItem: k => { m.delete(String(k)); }, clear: () => m.clear(), key: i => [...m.keys()][i] ?? null, get length() { return m.size; } };
      Object.defineProperty(window, s, { value: store, configurable: true });
    }
  }
})();
<\/script>`;
    const run = `<script>(async () => { try {\n${code.replace(/<\/script/gi, '<\\/script')}\n} catch (e) { window.__con.error(window.__describe(e)); } })();<\/script>`;
    let doc = page;
    doc = /<head[^>]*>/i.test(doc) ? doc.replace(/<head[^>]*>/i, m => m + boot) : boot + doc;
    doc = /<\/body>/i.test(doc) ? doc.replace(/<\/body>/i, run + '</body>') : doc + run;
    const f = document.createElement('iframe');
    f.className = 'jp-frame';
    f.setAttribute('sandbox', 'allow-scripts allow-forms allow-modals');
    f.setAttribute('title', 'Example page');
    const listener = ev => { if (ev.data && ev.data.jsplay === id) onLine(ev.data.k, ev.data.t); };
    window.addEventListener('message', listener);
    host.innerHTML = '';
    host.appendChild(f);
    f.srcdoc = doc;
    return () => window.removeEventListener('message', listener);
  }

  /* ---------- a light code editor: a textarea with tab support that grows with its text ---------- */
  function editor(code, onRun) {
    const ta = document.createElement('textarea');
    ta.className = 'jp-ed';
    ta.spellcheck = false;
    ta.setAttribute('autocapitalize', 'off');
    ta.setAttribute('aria-label', 'Code editor');
    ta.value = code;
    const fit = () => { ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight + 4, 640) + 'px'; };
    ta.addEventListener('input', fit);
    ta.addEventListener('keydown', e => {
      if (e.key === 'Tab' && !e.shiftKey) { e.preventDefault(); const s = ta.selectionStart; ta.setRangeText('  ', s, ta.selectionEnd, 'end'); fit(); }
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); onRun(); }
    });
    requestAnimationFrame(fit);
    return ta;
  }

  function lineHtml(k, t) {
    const cls = k === 'error' ? 'jp-e' : k === 'warn' ? 'jp-w' : '';
    return cls ? `<span class="${cls}">${esc(t)}</span>\n` : esc(t) + '\n';
  }

  /* ---------- "Edit and run" on a recorded example ---------- */
  function openPlay(wrap) {
    if (wrap.classList.contains('jp-open')) return;
    wrap.classList.add('jp-open');
    const mode = wrap.dataset.play;
    const src = wrap.querySelector('pre.src.main');
    const original = src.textContent;
    const box = document.createElement('div');
    box.className = 'jp-box';
    box.innerHTML = `<div class="jp-bar"><button type="button" class="jp-run">▶ Run</button><button type="button" class="jp-stop" hidden>■ Stop</button><button type="button" class="jp-reset">↺ Reset</button><button type="button" class="jp-close">✕ Close</button><span class="jp-tipk">Ctrl + Enter runs the code</span></div>${mode === 'dom' ? '<div class="jp-page"><span>Your page</span><div class="jp-fhost"></div></div>' : ''}<div class="jp-out"><span>Your output</span><pre aria-live="polite"></pre></div>`;
    const ta = editor(original, () => run());
    box.prepend(ta);
    src.after(box);
    src.hidden = true;
    const pre = box.querySelector('.jp-out pre'), runB = box.querySelector('.jp-run'), stopB = box.querySelector('.jp-stop');
    let detach = null;
    async function run() {
      pre.innerHTML = '';
      let n = 0;
      const onLine = (k, t) => { if (k === 'clear') { pre.innerHTML = ''; return; } n++; pre.insertAdjacentHTML('beforeend', lineHtml(k, t)); };
      if (mode === 'dom') {
        if (detach) detach();
        const k = wrap.dataset.k, page = (PAGE.play && PAGE.play[k] && PAGE.play[k].html) || '<!doctype html><body></body>';
        detach = runFrame(box.querySelector('.jp-fhost'), page, ta.value, onLine);
        setTimeout(() => { if (!n && !pre.innerHTML) pre.innerHTML = '<span class="jp-none">(nothing printed yet, try the page above)</span>'; }, 900);
        return;
      }
      runB.disabled = true; stopB.hidden = false;
      await runWorker((wrap.dataset.strict ? '"use strict";\n' : '') + ta.value, onLine);
      runB.disabled = false; stopB.hidden = true;
      if (!n) pre.innerHTML = '<span class="jp-none">(prints nothing)</span>';
    }
    runB.onclick = run;
    stopB.onclick = () => runWorker.stop && runWorker.stop();
    box.querySelector('.jp-reset').onclick = () => { ta.value = original; ta.dispatchEvent(new Event('input')); pre.innerHTML = ''; };
    box.querySelector('.jp-close').onclick = () => { if (detach) detach(); box.remove(); src.hidden = false; wrap.classList.remove('jp-open'); };
    ta.focus();
    run();
  }

  /* ---------- hands-on exercises ---------- */
  function exercisesHtml(list) {
    if (!list || !list.length) return '';
    const items = list.map((e, i) => `
      <div class="ex" id="${esc(e.id)}" data-i="${i}">
        <div class="ex-head"><span class="ex-lv lv-${LV[e.lv][2]}">${LV[e.lv][1]} ${LV[e.lv][0]}</span><h3>${esc(e.title)}</h3><span class="ex-st" aria-live="polite"></span></div>
        <div class="ex-task">${e.task}</div>
        <div class="ex-edhost"></div>
        <div class="ex-btns"><button type="button" class="ex-run">▶ Run the tests</button><button type="button" class="ex-reset">↺ Start again</button>${e.hint ? '<button type="button" class="ex-hintb">💡 Hint</button>' : ''}<button type="button" class="ex-solb">👀 Model answer</button></div>
        <div class="ex-hint" hidden>${e.hint || ''}</div>
        <ul class="ex-res"></ul>
        <div class="ex-sol" hidden><pre class="src">${typeof LEARN !== 'undefined' ? LEARN.hl(e.solution, 'js') : esc(e.solution)}</pre>${e.why ? `<div class="ex-why">${e.why}</div>` : ''}</div>
      </div>`).join('');
    return `<h2><span class="sec-em">🏋️</span><span>Hands-on exercises</span></h2>
      <p class="ex-lead">Write real code in the box, then press <b>Run the tests</b>. The tests run in your browser and tell you exactly which cases pass. Every model answer was checked against the same tests when this page was built.</p>${items}`;
  }
  function wireExercises(root) {
    root.querySelectorAll('.ex').forEach(box => {
      const e = PAGE.ex[+box.dataset.i];
      const store = 'jsplay-ex-' + location.pathname + '-' + e.id;
      let saved = null;
      try { saved = localStorage.getItem(store); } catch (err) { /* storage unavailable */ }
      const run = async () => {
        try { localStorage.setItem(store, ta.value); } catch (err) { /* storage unavailable */ }
        const ul = box.querySelector('.ex-res'), st = box.querySelector('.ex-st');
        ul.innerHTML = '<li class="wait">Running…</li>';
        const r = await runTests(ta.value, e.tests);
        if (r.error) { ul.innerHTML = `<li class="bad">❌ Your code did not run: ${esc(r.error)}</li>`; st.textContent = ''; box.classList.remove('pass'); return; }
        const good = r.res.filter(x => x.ok).length;
        ul.innerHTML = r.res.map((x, i) => `<li class="${x.ok ? 'ok' : 'bad'}">${x.ok ? '✅' : '❌'} <code>${esc(e.tests[i].call)}</code> ${x.err ? `threw <b>${esc(x.err)}</b>` : `gave <code>${esc(x.got)}</code>`}${x.ok ? '' : `, expected <code>${esc(JSON.stringify(e.tests[i].want))}</code>`}</li>`).join('');
        st.textContent = `${good} of ${r.res.length} tests pass`;
        const all = good === r.res.length;
        if (all && !box.classList.contains('pass') && typeof FUN !== 'undefined') {
          const b = st.getBoundingClientRect();
          FUN.confetti(b.left + b.width / 2, b.top + b.height / 2, 70);
        }
        box.classList.toggle('pass', all);
      };
      const ta = editor(saved || e.starter, run);
      box.querySelector('.ex-edhost').appendChild(ta);
      box.querySelector('.ex-run').onclick = run;
      box.querySelector('.ex-reset').onclick = () => { ta.value = e.starter; ta.dispatchEvent(new Event('input')); box.querySelector('.ex-res').innerHTML = ''; box.querySelector('.ex-st').textContent = ''; box.classList.remove('pass'); };
      const hb = box.querySelector('.ex-hintb');
      if (hb) hb.onclick = () => { const h = box.querySelector('.ex-hint'); h.hidden = !h.hidden; };
      box.querySelector('.ex-solb').onclick = ev => { const s = box.querySelector('.ex-sol'); s.hidden = !s.hidden; ev.target.textContent = s.hidden ? '👀 Model answer' : '🙈 Hide the answer'; };
    });
  }

  /* ---------- the QA path: show only the parts test automation needs ---------- */
  function wireQa() {
    const b = document.getElementById('qaOnly');
    if (!b) return;
    const set = on => {
      document.body.classList.toggle('qa-only', on);
      b.setAttribute('aria-pressed', on);
      b.textContent = on ? '📖 Show every part' : '🧪 Show the QA path only';
      try { localStorage.setItem('jsplay-qa-only', on ? '1' : ''); } catch (e) { /* storage unavailable */ }
    };
    let on = false;
    try { on = localStorage.getItem('jsplay-qa-only') === '1'; } catch (e) { /* storage unavailable */ }
    set(on);
    b.onclick = () => set(!document.body.classList.contains('qa-only'));
  }

  function page(o) {
    const $ = id => document.getElementById(id);
    $('comic').innerHTML = PAGE.info ? XTRA.infoHtml(PAGE.info) : '';
    $('real-life').innerHTML = PAGE.real ? XTRA.realHtml(PAGE.real) : '';
    $('practice').innerHTML = exercisesHtml(PAGE.ex);
    $('quiz').innerHTML = LEARN.quizHtml(PAGE.quiz || [], { lang: 'js' });
    $('numbers').innerHTML = LEARN.calcHtml(PAGE.calc || [], { lang: 'js', sub: 'Work out what the code gives, type it and press Check. Stuck? Peek at the hint, then the full working.' });
    wireExercises($('practice'));
    VIZ.mountAll(document);
    XTRA.wire(document);
    LEARN.wire();
    FUN.initScroll();
    FUN.observe();
    VOICE.setup({ title: o.title, segments: PAGE.say || [] });
    $('listenAll').onclick = () => VOICE.playAll();
    wireQa();
    document.addEventListener('click', e => {
      const c = e.target.closest('.codebar .copy');
      if (c) {
        const w = c.closest('.codewrap');
        const ed = w.querySelector('.jp-ed');
        const txt = ed ? ed.value : [...w.querySelectorAll('pre.src')].map(p => p.textContent).join('\n\n');
        const done = () => { c.textContent = 'Copied'; setTimeout(() => { c.textContent = 'Copy'; }, 1200); };
        if (navigator.clipboard) navigator.clipboard.writeText(txt).then(done, done); else done();
        return;
      }
      const t = e.target.closest('.codebar .try');
      if (t) openPlay(t.closest('.codewrap'));
    });
    if (FUN.inFrame) document.querySelectorAll('.pager a[data-topic]').forEach(a => { a.href = '../../subject.html?s=' + o.subject + '&t=' + a.dataset.topic; a.target = '_top'; });
    else document.querySelector('.home-link').removeAttribute('target');
  }

  return { page, runWorker, runTests, runFrame };
})();
