/* ===== Python chapters: real Python in the browser, the line by line viewer and the exercises =====
   PYPLAY.page({ title, subject, tracer }) draws the comic, real life cards, exercises, quiz and number crunch from PAGE,
   then turns on the animations, the narrator and every button on the page.

   Python runs with Pyodide (CPython compiled to WebAssembly) inside a Web Worker, so a runaway loop can be stopped.
   It loads from the jsDelivr CDN the first time a reader presses a run button, and the browser caches it after that.

   Line by line: PAGE.tr[key] is a recording made with CPython when the page was built (tools/py-build/pytrace.py).
   After an edit, the same recorder runs inside Pyodide, so the reader can step through their own code too.

   Exercises: PAGE.ex = [{ id, lv: 'e'|'m'|'h'|'x', title, task, starter, tests: [{ call, want }], hint, solution, why }]
   Each test call is a Python expression evaluated after the learner's code. Its value is compared with want as JSON. */
const PYPLAY = (() => {
  const PYODIDE = 'https://cdn.jsdelivr.net/npm/pyodide@314.0.7/';
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const LV = { e: ['Easy', '🌱', 'easy'], m: ['Medium', '🌿', 'med'], h: ['Hard', '🔥', 'hard'], x: ['Expert', '🧠', 'exp'] };
  let TRACER = '';

  /* ---------- the worker ---------- */
  const HELPERS = `
import sys, json, traceback, linecache
def _bb_run(src):
    linecache.cache['main.py'] = (len(src), None, src.splitlines(True), 'main.py')
    try:
        code = compile(src, 'main.py', 'exec')
        exec(code, {'__name__': '__main__'})
    except SystemExit:
        pass
    except BaseException as e:
        tb = e.__traceback__
        while tb is not None and tb.tb_frame.f_code.co_filename != 'main.py':
            tb = tb.tb_next
        sys.stdout.flush()
        traceback.print_exception(type(e), e, tb)
    sys.stdout.flush(); sys.stderr.flush()

def _bb_tests(code, tests_json):
    tests = json.loads(tests_json)
    ns = {'__name__': 'exercise'}
    try:
        exec(compile(code, 'exercise.py', 'exec'), ns)
    except BaseException as e:
        return json.dumps({'error': type(e).__name__ + ': ' + str(e)})
    res = []
    for t in tests:
        try:
            got = eval(t['call'], ns)
            ok = json.dumps(got, sort_keys=True, default=repr) == json.dumps(t['want'], sort_keys=True, default=repr)
            res.append({'ok': ok, 'got': repr(got), 'err': None})
        except BaseException as e:
            res.append({'ok': False, 'got': None, 'err': type(e).__name__ + ': ' + str(e)})
    return json.dumps({'res': res})
`;
  function workerSource() {
    return `
import { loadPyodide } from ${JSON.stringify(PYODIDE + 'pyodide.mjs')};
let stdinText = '';
const ready = loadPyodide({ indexURL: ${JSON.stringify(PYODIDE)} }).then(py => {
  py.setStdout({ batched: t => postMessage({ k: 'log', t }) });
  py.setStderr({ batched: t => postMessage({ k: 'error', t }) });
  py.setStdin({ stdin: () => { const t = stdinText; stdinText = null; return t; } });
  py.runPython(${JSON.stringify(HELPERS)});
  postMessage({ k: 'ready', t: py.runPython('import sys; sys.version.split()[0]') });
  return py;
}).catch(e => { postMessage({ k: 'fatal', t: String(e && e.message || e) }); throw e; });
let traceNs = null;
onmessage = async ev => {
  const d = ev.data;
  let py;
  try { py = await ready; } catch (e) { return; }
  try {
    if (d.mode === 'run') {
      stdinText = d.stdin || '';
      py.globals.get('_bb_run')(d.code);
      postMessage({ k: 'done' });
    } else if (d.mode === 'trace') {
      if (!traceNs) { traceNs = py.toPy({ __name__: 'pytrace' }); py.runPython(d.tracer, { globals: traceNs }); }
      const rec = traceNs.get('record')(d.code, d.stdin || '');
      const json = py.pyimport('json').dumps(rec);
      rec.destroy && rec.destroy();
      postMessage({ k: 'trace', t: json });
    } else if (d.mode === 'ex') {
      postMessage({ k: 'ex', t: py.globals.get('_bb_tests')(d.code, JSON.stringify(d.tests)) });
    }
  } catch (e) {
    postMessage({ k: 'fatal', t: String(e && e.message || e) });
  }
};`;
  }
  let worker = null, workerReady = null, workerUrl = null, version = '';
  function getWorker(onStatus) {
    if (worker) return workerReady;
    if (!workerUrl) workerUrl = URL.createObjectURL(new Blob([workerSource()], { type: 'text/javascript' }));
    worker = new Worker(workerUrl, { type: 'module' });
    onStatus && onStatus('Loading Python into your browser. The first time takes a few seconds, after that it is cached.');
    workerReady = new Promise((resolve, reject) => {
      const first = ev => {
        if (ev.data.k === 'ready') { version = ev.data.t; worker.removeEventListener('message', first); resolve(worker); }
        if (ev.data.k === 'fatal') { worker.removeEventListener('message', first); kill(); reject(new Error(ev.data.t)); }
      };
      worker.addEventListener('message', first);
      worker.addEventListener('error', ev => { ev.preventDefault && ev.preventDefault(); kill(); reject(new Error('Python could not be loaded. Check your internet connection, then try again.')); });
    });
    return workerReady;
  }
  function kill() { if (worker) worker.terminate(); worker = null; workerReady = null; }

  // Send one job; onMsg sees every message; resolves with the final message, or 'stopped' / 'timeout'.
  let current = null;
  async function job(msg, onMsg, onStatus, limit = 10000) {
    let w;
    try { w = await getWorker(onStatus); } catch (e) { return { k: 'fatal', t: e.message }; }
    onStatus && onStatus('');
    return new Promise(resolve => {
      const end = r => { clearTimeout(timer); w.removeEventListener('message', on); current = null; resolve(r); };
      const on = ev => {
        const m = ev.data;
        if (m.k === 'log' || m.k === 'error') { onMsg && onMsg(m.k, m.t); return; }
        end(m);
      };
      const timer = setTimeout(() => { kill(); end({ k: 'timeout' }); }, limit);
      current = { stop: () => { kill(); end({ k: 'stopped' }); } };
      w.addEventListener('message', on);
      w.postMessage(msg);
    });
  }
  const run = (code, stdin, onLine, onStatus) => job({ mode: 'run', code, stdin }, onLine, onStatus);
  const trace = async (code, stdin, onStatus) => {
    const r = await job({ mode: 'trace', code, stdin, tracer: TRACER }, null, onStatus, 15000);
    if (r.k === 'trace') return { rec: JSON.parse(r.t) };
    return { error: r.k === 'timeout' ? 'The program ran for more than 15 seconds. Look for an endless loop.' : r.t || 'Stopped.' };
  };
  const runTests = async (code, tests, onStatus) => {
    const r = await job({ mode: 'ex', code, tests }, null, onStatus, 10000);
    if (r.k === 'ex') return JSON.parse(r.t);
    return { error: r.k === 'timeout' ? 'The tests did not finish within 10 seconds. Look for an endless loop.' : r.t || 'Stopped.' };
  };

  /* ---------- a light code editor ---------- */
  function editor(code, onRun) {
    const ta = document.createElement('textarea');
    ta.className = 'jp-ed';
    ta.spellcheck = false;
    ta.setAttribute('autocapitalize', 'off');
    ta.setAttribute('aria-label', 'Python code editor');
    ta.value = code;
    const fit = () => { ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight + 4, 640) + 'px'; };
    ta.addEventListener('input', fit);
    ta.addEventListener('keydown', e => {
      if (e.key === 'Tab' && !e.shiftKey) { e.preventDefault(); const s = ta.selectionStart; ta.setRangeText('    ', s, ta.selectionEnd, 'end'); fit(); }
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); onRun(); }
    });
    requestAnimationFrame(fit);
    return ta;
  }
  const lineHtml = (k, t) => (k === 'error' ? `<span class="jp-e">${esc(t)}</span>\n` : esc(t) + '\n');

  /* ---------- the line by line viewer ---------- */
  function stepper(host, code, rec, title) {
    const lines = code.split('\n');
    const states = [];
    let vars = {}, stack = ['module'], out = '';
    rec.steps.forEach(st => {
      if (st.s) stack = st.s;
      if (st.d) { vars = { ...vars }; Object.entries(st.d).forEach(([k, v]) => { if (v === null) delete vars[k]; else vars[k] = v; }); }
      if (st.o) out += st.o;
      states.push({ l: st.l, ev: st.ev, stack, vars, out, changed: st.d ? Object.keys(st.d).filter(k => st.d[k] !== null) : [] });
    });
    const finalOut = out + (rec.tail || '');
    host.innerHTML = `<div class="st-box"><div class="st-head"><b>👣 ${esc(title)}</b><button type="button" class="st-close">✕ Close</button></div>
      <div class="st-grid"><pre class="st-code">${lines.map((l, i) => `<div data-l="${i + 1}"><span class="st-n">${i + 1}</span>${typeof LEARN !== 'undefined' ? LEARN.hl(l, 'py') : esc(l)}${l ? '' : ' '}</div>`).join('')}</pre>
      <div class="st-side"><div class="st-blk"><span>Call stack</span><div class="st-stack"></div></div><div class="st-blk"><span>Variables</span><div class="st-vars"></div></div><div class="st-blk"><span>Output so far</span><pre class="st-out"></pre></div></div></div>
      <div class="vz-msg st-msg" aria-live="polite"></div><div class="vz-p"></div></div>`;
    const msg = host.querySelector('.st-msg');
    const show = i => {
      const n = states.length;
      const done = i === n;
      const s = done ? (states[n - 1] || { l: 0, stack: [], vars: {}, out: '', changed: [] }) : states[i];
      host.querySelectorAll('.st-code div').forEach(d => { d.classList.toggle('on', !done && +d.dataset.l === s.l); });
      const on = host.querySelector('.st-code div.on');
      if (on) { const box = host.querySelector('.st-code'); if (on.offsetTop < box.scrollTop || on.offsetTop > box.scrollTop + box.clientHeight - 30) box.scrollTop = on.offsetTop - 40; }
      host.querySelector('.st-stack').innerHTML = (done ? [] : s.stack).slice().reverse().map((f, j) => `<span class="st-frame${j === 0 ? ' top' : ''}">${esc(f)}</span>`).join('') || '<span class="pv-empty">empty</span>';
      const entries = Object.entries(s.vars);
      const g = entries.filter(([k]) => k.startsWith('G.')), l = entries.filter(([k]) => k.startsWith('L.'));
      const row = ([k, v]) => `<div class="st-var${s.changed.includes(k) && !done ? ' new' : ''}"><b>${esc(k.slice(2))}</b><code>${esc(v)}</code></div>`;
      host.querySelector('.st-vars').innerHTML = (l.length ? `<small>Local to ${esc(s.stack[s.stack.length - 1])}</small>${l.map(row).join('')}` : '') + (g.length ? `<small>Global</small>${g.map(row).join('')}` : '') || '<span class="pv-empty">no variables yet</span>';
      host.querySelector('.st-out').textContent = (done ? finalOut + (rec.err ? (finalOut && !finalOut.endsWith('\n') ? '\n' : '') + rec.err : '') : s.out) || '';
      if (done) msg.innerHTML = rec.err ? '<b>The program stopped with an error.</b> The traceback is in the output box.' : rec.cut ? '<b>Stopped after 600 steps.</b> Long loops are cut short here.' : '<b>Finished.</b> The program ran to the end.';
      else {
        const what = s.ev === 'call' ? `Python calls <code>${esc(s.stack[s.stack.length - 1])}</code> and creates a new frame for it.` : s.ev === 'return' ? `<code>${esc(s.stack[s.stack.length - 1])}</code> returns from line ${s.l}. Its frame is about to be thrown away.` : `Line ${s.l} is about to run.`;
        msg.innerHTML = `<b>Step ${i + 1} of ${n}.</b> ${what}${s.changed.length ? ' Changed: ' + s.changed.map(k => `<code>${esc(k.slice(2))}</code>`).join(', ') + '.' : ''}`;
      }
    };
    const P = VIZ.kit.Player(host.querySelector('.vz-p'), show, 900);
    P.load(states.length + 1);
    host.querySelector('.st-close').onclick = () => { P.pause(); host.innerHTML = ''; };
    host.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }
  function stepHost(wrap) {
    let h = wrap.querySelector(':scope > .st-host');
    if (!h) { h = document.createElement('div'); h.className = 'st-host'; wrap.appendChild(h); }
    return h;
  }

  /* ---------- "Edit and run" on a recorded example ---------- */
  function openPlay(wrap) {
    if (wrap.classList.contains('jp-open')) return;
    wrap.classList.add('jp-open');
    const src = wrap.querySelector('pre.src.main');
    const original = src.textContent;
    const box = document.createElement('div');
    box.className = 'jp-box';
    box.innerHTML = `<div class="jp-bar"><button type="button" class="jp-run">▶ Run</button><button type="button" class="jp-step">👣 Line by line</button><button type="button" class="jp-stop" hidden>■ Stop</button><button type="button" class="jp-reset">↺ Reset</button><button type="button" class="jp-close">✕ Close</button><span class="jp-tipk">Ctrl + Enter runs the code</span></div>
      <div class="pp-stdin" hidden><label>⌨️ Keyboard input for <code>input()</code>, one line per call<textarea rows="2" spellcheck="false"></textarea></label></div>
      <div class="pp-status" hidden></div><div class="jp-out"><span>Your output</span><pre aria-live="polite"></pre></div>`;
    const ta = editor(original, () => runIt());
    box.prepend(ta);
    src.after(box);
    src.hidden = true;
    const pre = box.querySelector('.jp-out pre'), runB = box.querySelector('.jp-run'), stopB = box.querySelector('.jp-stop'), stepB = box.querySelector('.jp-step');
    const stdinBox = box.querySelector('.pp-stdin'), stdinTa = stdinBox.querySelector('textarea'), status = box.querySelector('.pp-status');
    stdinTa.value = wrap.dataset.stdin || '';
    const syncStdin = () => { stdinBox.hidden = !/\binput\s*\(/.test(ta.value); };
    ta.addEventListener('input', syncStdin);
    syncStdin();
    const setStatus = t => { status.hidden = !t; status.textContent = t ? '⏳ ' + t : ''; };
    const busy = on => { runB.disabled = on; stepB.disabled = on; stopB.hidden = !on; };
    async function runIt() {
      pre.innerHTML = '';
      busy(true);
      let n = 0;
      const r = await run(ta.value, stdinTa.value, (k, t) => { n++; pre.insertAdjacentHTML('beforeend', lineHtml(k, t)); }, setStatus);
      busy(false);
      setStatus('');
      if (r.k === 'timeout') pre.insertAdjacentHTML('beforeend', '<span class="jp-w">Stopped after 10 seconds. Look for an endless loop, or a loop that is very long.</span>\n');
      else if (r.k === 'stopped') pre.insertAdjacentHTML('beforeend', '<span class="jp-w">Stopped.</span>\n');
      else if (r.k === 'fatal') pre.insertAdjacentHTML('beforeend', `<span class="jp-e">${esc(r.t)}</span>\n`);
      else if (!n) pre.innerHTML = '<span class="jp-none">(prints nothing)</span>';
    }
    async function stepIt() {
      busy(true);
      const r = await trace(ta.value, stdinTa.value, setStatus);
      busy(false);
      setStatus('');
      if (r.error) { pre.innerHTML = `<span class="jp-e">${esc(r.error)}</span>`; return; }
      stepper(stepHost(wrap), ta.value, r.rec, 'Your code, line by line');
    }
    runB.onclick = runIt;
    stepB.onclick = stepIt;
    stopB.onclick = () => current && current.stop();
    box.querySelector('.jp-reset').onclick = () => { ta.value = original; ta.dispatchEvent(new Event('input')); pre.innerHTML = ''; };
    box.querySelector('.jp-close').onclick = () => { box.remove(); src.hidden = false; wrap.classList.remove('jp-open'); };
    ta.focus();
    runIt();
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
        <div class="ex-sol" hidden><pre class="src">${typeof LEARN !== 'undefined' ? LEARN.hl(e.solution, 'py') : esc(e.solution)}</pre>${e.why ? `<div class="ex-why">${e.why}</div>` : ''}</div>
      </div>`).join('');
    return `<h2><span class="sec-em">🏋️</span><span>Hands-on exercises</span></h2>
      <p class="ex-lead">Write real Python in the box, then press <b>Run the tests</b>. The tests run in your browser with real Python (Pyodide) and tell you exactly which cases pass. Every model answer was checked against the same tests with CPython when this page was built.</p>${items}`;
  }
  function wireExercises(root) {
    root.querySelectorAll('.ex').forEach(box => {
      const e = PAGE.ex[+box.dataset.i];
      const store = 'pyplay-ex-' + location.pathname + '-' + e.id;
      let saved = null;
      try { saved = localStorage.getItem(store); } catch (err) { /* storage unavailable */ }
      const ul = box.querySelector('.ex-res'), st = box.querySelector('.ex-st');
      const go = async () => {
        try { localStorage.setItem(store, ta.value); } catch (err) { /* storage unavailable */ }
        ul.innerHTML = '<li class="wait">Running…</li>';
        const r = await runTests(ta.value, e.tests, t => { if (t) ul.innerHTML = `<li class="wait">⏳ ${esc(t)}</li>`; });
        if (r.error) { ul.innerHTML = `<li class="bad">❌ Your code did not run: ${esc(r.error)}</li>`; st.textContent = ''; box.classList.remove('pass'); return; }
        const good = r.res.filter(x => x.ok).length;
        ul.innerHTML = r.res.map((x, i) => `<li class="${x.ok ? 'ok' : 'bad'}">${x.ok ? '✅' : '❌'} <code>${esc(e.tests[i].call)}</code> ${x.err ? `raised <b>${esc(x.err)}</b>` : `gave <code>${esc(x.got)}</code>`}${x.ok ? '' : `, expected <code>${esc(JSON.stringify(e.tests[i].want))}</code>`}</li>`).join('');
        st.textContent = `${good} of ${r.res.length} tests pass`;
        const all = good === r.res.length;
        if (all && !box.classList.contains('pass') && typeof FUN !== 'undefined') {
          const b = st.getBoundingClientRect();
          FUN.confetti(b.left + b.width / 2, b.top + b.height / 2, 70);
        }
        box.classList.toggle('pass', all);
      };
      const ta = editor(saved || e.starter, go);
      box.querySelector('.ex-edhost').appendChild(ta);
      box.querySelector('.ex-run').onclick = go;
      box.querySelector('.ex-reset').onclick = () => { ta.value = e.starter; ta.dispatchEvent(new Event('input')); ul.innerHTML = ''; st.textContent = ''; box.classList.remove('pass'); };
      const hb = box.querySelector('.ex-hintb');
      if (hb) hb.onclick = () => { const h = box.querySelector('.ex-hint'); h.hidden = !h.hidden; };
      box.querySelector('.ex-solb').onclick = ev => { const s = box.querySelector('.ex-sol'); s.hidden = !s.hidden; ev.target.textContent = s.hidden ? '👀 Model answer' : '🙈 Hide the answer'; };
    });
  }

  /* ---------- the QA path ---------- */
  function wireQa() {
    const b = document.getElementById('qaOnly');
    if (!b) return;
    const set = on => {
      document.body.classList.toggle('qa-only', on);
      b.setAttribute('aria-pressed', on);
      b.textContent = on ? '📖 Show every part' : '🧪 Show the QA path only';
      try { localStorage.setItem('pyplay-qa-only', on ? '1' : ''); } catch (e) { /* storage unavailable */ }
    };
    let on = false;
    try { on = localStorage.getItem('pyplay-qa-only') === '1'; } catch (e) { /* storage unavailable */ }
    set(on);
    b.onclick = () => set(!document.body.classList.contains('qa-only'));
  }

  function page(o) {
    TRACER = o.tracer || '';
    const $ = id => document.getElementById(id);
    $('comic').innerHTML = PAGE.info ? XTRA.infoHtml(PAGE.info) : '';
    $('real-life').innerHTML = PAGE.real ? XTRA.realHtml(PAGE.real) : '';
    $('practice').innerHTML = exercisesHtml(PAGE.ex);
    $('quiz').innerHTML = LEARN.quizHtml(PAGE.quiz || [], { lang: 'py' });
    $('numbers').innerHTML = LEARN.calcHtml(PAGE.calc || [], { lang: 'py', sub: 'Work out the answer, type it and press Check. Stuck? Peek at the hint, then the full working.' });
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
      if (t) { openPlay(t.closest('.codewrap')); return; }
      const s = e.target.closest('.codebar .step');
      if (s) {
        const w = s.closest('.codewrap'), k = w.dataset.k;
        if (PAGE.tr && PAGE.tr[k]) stepper(stepHost(w), w.querySelector('pre.src.main').textContent, PAGE.tr[k], 'This example, line by line');
      }
    });
    if (FUN.inFrame) document.querySelectorAll('.pager a[data-topic]').forEach(a => { a.href = '../../subject.html?s=' + o.subject + '&t=' + a.dataset.topic; a.target = '_top'; });
    else document.querySelector('.home-link').removeAttribute('target');
  }

  /* pages that draw their own layout (Computer Vision) set the recorder source and stop a run directly */
  const setTracer = src => { TRACER = src; };
  const stop = () => { if (current) current.stop(); };
  return { page, run, trace, runTests, setTracer, stop, get version() { return version; } };
})();
