/* ===================== Line by line execution viewer =====================
   The same viewer the Complete Java Session pages carry inline, shared here for the newer Java chapters.
   Every program on the page was run once for real and recorded line by line (tools/java-build/tracer).
   A recording (trace) holds, for each step, the line about to run, the call stack when it changed,
   the variables that changed, and any text printed since the previous step.
   XV.mount(host, {key, code, lang, html}) shows the step viewer for one program inside host. */
const XV = (() => {
  let ALL = null;
  const traces = () => {
    if (!ALL) {
      try { ALL = JSON.parse(document.getElementById('traces').textContent); } catch (e) { ALL = {}; }
    }
    return ALL;
  };
  const SPEEDS = [0.25, 0.5, 1, 2, 4, 8];
  const BASE_MS = 750;
  let mode = 'step';
  try { mode = localStorage.getItem('xv-mode') || 'step'; } catch (e) { mode = 'step'; }
  let speedIdx = 2;
  try { const s = +localStorage.getItem('xv-speed'); if (s >= 0 && s < SPEEDS.length && localStorage.getItem('xv-speed') !== null) speedIdx = s; } catch (e) { speedIdx = 2; }
  const live = new Set();
  const listeners = [];

  const escH = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

  /* Split highlighted HTML into one string per source line, closing and reopening spans at line breaks. */
  function splitLines(html) {
    const lines = [];
    const open = [];
    let cur = '';
    const re = /(<span[^>]*>)|(<\/span>)|(\n)|([^<\n]+)/g;
    let m;
    while ((m = re.exec(html))) {
      if (m[1]) { open.push(m[1]); cur += m[1]; }
      else if (m[2]) { open.pop(); cur += m[2]; }
      else if (m[3]) { cur += '</span>'.repeat(open.length); lines.push(cur); cur = open.join(''); }
      else cur += m[4];
    }
    lines.push(cur);
    return lines;
  }

  /* Rebuild the full state at every step from the recorded changes. */
  function prepare(t) {
    if (t._ready) return t;
    const vars = [], stacks = [], outLen = [];
    let cur = {}, stack = [], out = '';
    for (const s of t.steps) {
      if (s.s) stack = s.s;
      if (s.d) {
        cur = Object.assign({}, cur);
        for (const k in s.d) { if (s.d[k] === null) delete cur[k]; else cur[k] = s.d[k]; }
      }
      if (s.o) out += s.o;
      vars.push(cur); stacks.push(stack); outLen.push(out.length);
    }
    t._full = out + ((t.end && t.end.o) || '');
    vars.push(cur); stacks.push([]); outLen.push(t._full.length);
    t._vars = vars; t._stacks = stacks; t._outLen = outLen;
    t._ready = true;
    return t;
  }

  const nice = k => (k.startsWith('L.this.') ? 'this.' + k.slice(7) : k.slice(2));
  const showVal = v => escH(String(v).replace(/\n/g, '⏎'));
  const clip = (s, n) => (s.length > n ? s.slice(0, n - 1) + '…' : s);

  function controlsHtml() {
    return `<div class="xv-bar">
      <button class="xb" data-x="reset" title="Back to the start (Home)" aria-label="Back to the start">⏮</button>
      <button class="xb" data-x="back" title="One step back (left arrow)" aria-label="One step back">◀</button>
      <button class="xb xplay" data-x="play" title="Play or pause (space)">▶ Play</button>
      <button class="xb" data-x="fwd" title="Run one line (right arrow)" aria-label="Run one line">▶|</button>
      <button class="xb" data-x="end" title="Jump to the end (End)" aria-label="Jump to the end">⏭</button>
      <input type="range" class="xscrub" min="0" max="0" value="0" aria-label="Execution step">
      <span class="xcount"></span>
      <label class="xspeed">Speed <input type="range" class="xsp" min="0" max="${SPEEDS.length - 1}" step="1" value="${speedIdx}"><span class="xspl">${SPEEDS[speedIdx]}x</span></label>
    </div>`;
  }

  function mount(host, opt) {
    unmountIn(host);
    live.forEach(o => { if (!o.root.isConnected) { o.stop(); live.delete(o); } });
    const t0 = traces()[opt.key];
    if (!t0) {
      host.innerHTML = '<div class="xv"><div class="xv-say">A line by line recording is not available for this program.</div></div>';
      return null;
    }
    const t = prepare(t0);
    const src = opt.code.split('\n');
    const lines = splitLines(opt.html);
    const N = t.steps.length;
    host.innerHTML = `<div class="xv" tabindex="0" aria-label="Line by line execution viewer">
      <div class="xv-note">This is a recording of one real run of this exact program. Press Play, or press ▶| to run one line at a time. Click a line number to jump to the next time that line runs.</div>
      ${controlsHtml()}
      <div class="xv-say" aria-live="polite"></div>
      <div class="xv-grid">
        <div class="xv-code" role="list">${lines.map((h, i) => `<div class="xv-ln" data-l="${i + 1}" role="listitem"><span class="xv-g" title="Jump to the next time line ${i + 1} runs">${i + 1}</span><span class="xv-t">${h || ' '}</span></div>`).join('')}</div>
        <div class="xv-side">
          <div class="xv-box xv-varbox"><div class="xv-h">Variables <span>right now</span></div><div class="xv-vars"></div></div>
          <div class="xv-box"><div class="xv-h">Call stack <span>newest on top</span></div><div class="xv-stack"></div></div>
          <div class="xv-box xv-outbox"><div class="xv-h">Output <span>printed so far</span></div><pre class="xv-out"></pre></div>
        </div>
      </div>
    </div>`;
    const root = host.firstElementChild;
    const q = s => root.querySelector(s);
    const lineEls = [...root.querySelectorAll('.xv-ln')];
    const st = { i: 0, playing: false, timer: null };
    const inst = { root, stop: () => pause() };
    live.add(inst);
    host._xv = inst;
    q('.xscrub').max = N;

    function lineText(l) { return l && src[l - 1] !== undefined ? src[l - 1].trim() : ''; }
    function chip(l) { const s = lineText(l).replace(/\s+/g, ' '); return s ? ` <code class="xv-chip">${escH(clip(s, 70))}</code>` : ''; }
    function defNote(l) {
      const s = lineText(l);
      if (/^(async\s+)?def\s|^class\s|^(async\s+)?function\s/.test(s)) return 'This line only teaches the computer what the function or class is. Its body runs later, each time it is called.';
      if (/^[}\])]+;?$/.test(s)) return 'This closing bracket marks the end of a block of code.';
      return '';
    }

    function narrate(i) {
      const s = t.steps;
      const parts = [];
      if (i === 0) {
        parts.push(`<b>Ready.</b> The computer will start with line ${s[0].l}.${chip(s[0].l)}`);
        parts.push('Press ▶| to run it.');
        return parts.join(' ');
      }
      const ranL = s[i - 1].l;
      const atEnd = i === N;
      const same = !atEnd && s[i].l === ranL;
      parts.push(same ? `<b>Another part of line ${ranL} ran.</b>` : `<b>Line ${ranL} ran.</b>${chip(ranL)}`);
      if (!same && defNote(ranL)) parts.push(defNote(ranL));
      const before = t._stacks[i - 1], after = t._stacks[i];
      if (!atEnd && after.length > before.length) {
        const fn = after[after.length - 1];
        const args = Object.keys(t._vars[i]).filter(k => k.startsWith('L.') && !k.startsWith('L.this.') && !(k in t._vars[i - 1] && t._vars[i - 1][k] === t._vars[i][k]));
        const shown = args.slice(0, 4).map(k => `<span class="xv-k">${escH(nice(k))}</span> = ${showVal(clip(t._vars[i][k], 40))}`);
        parts.push(`The program jumped into <b>${escH(fn)}</b>${shown.length ? ' with ' + shown.join(', ') : ''}.`);
      } else if (!atEnd && after.length < before.length) {
        parts.push(`<b>${escH(before[before.length - 1])}</b> finished, so the program went back to <b>${escH(after[after.length - 1] || 'the main program')}</b>.`);
      } else if (!atEnd) {
        const d = s[i].d || {};
        const ch = [];
        for (const k in d) {
          if (d[k] === null) continue;
          const old = t._vars[i - 1][k];
          if (old === undefined) ch.push(`<span class="xv-k">${escH(nice(k))}</span> = ${showVal(clip(d[k], 40))} (new)`);
          else ch.push(`<span class="xv-k">${escH(nice(k))}</span>: ${showVal(clip(old, 30))} → ${showVal(clip(d[k], 40))}`);
        }
        if (ch.length) parts.push('Changed: ' + ch.slice(0, 4).join(', ') + (ch.length > 4 ? `, and ${ch.length - 4} more` : '') + '.');
      }
      const printed = atEnd ? (t.end.o || '') : (s[i].o || '');
      if (printed) parts.push(`It printed <code class="xv-chip">${showVal(clip(printed.replace(/\n$/, ''), 80))}</code>.`);
      if (!atEnd && s[i].f) parts.push('<span class="xv-ff">Fast forward</span> This part repeats many times, so the replay skipped ahead to save time. The values below are exactly where the real run was.');
      if (atEnd) parts.push(`<b>The program finished.</b> It ran ${N} recorded steps.${t.end.t ? ' The recording stopped early because the run was very long.' : ''}`);
      else parts.push(`Next up: line ${s[i].l}.`);
      return parts.join(' ');
    }

    function render() {
      const i = st.i;
      const s = t.steps;
      const cur = i < N ? s[i].l : null;
      const prev = i > 0 ? s[i - 1].l : null;
      lineEls.forEach(el => { el.classList.remove('cur', 'prev'); });
      if (prev && lineEls[prev - 1]) lineEls[prev - 1].classList.add('prev');
      if (cur && lineEls[cur - 1]) { lineEls[cur - 1].classList.remove('prev'); lineEls[cur - 1].classList.add('cur'); }
      const focus = lineEls[(cur || prev || 1) - 1];
      const pane = q('.xv-code');
      if (focus) {
        const top = focus.offsetTop, h = focus.offsetHeight;
        if (top < pane.scrollTop + 30 || top + h > pane.scrollTop + pane.clientHeight - 30) pane.scrollTop = Math.max(0, top - pane.clientHeight / 2 + h / 2);
      }
      q('.xv-say').innerHTML = narrate(i);
      q('.xscrub').value = i;
      q('.xcount').textContent = i === N ? `Finished · ${N} steps` : `Step ${i} of ${N}`;
      // variables
      const v = t._vars[i];
      const changed = i > 0 && i < N && s[i].d ? s[i].d : {};
      const prevVars = i > 0 ? t._vars[i - 1] : {};
      const groups = [['Local variables', k => k.startsWith('L.') && !k.startsWith('L.this.')], ['Fields of this object', k => k.startsWith('L.this.')], [opt.lang === 'java' ? 'Static fields of the class' : 'Global variables', k => k.startsWith('G.')]];
      let vh = '';
      for (const [title, f] of groups) {
        const ks = Object.keys(v).filter(f);
        if (!ks.length) continue;
        vh += `<div class="xv-vg">${title}</div>`;
        for (const k of ks) {
          const isNew = k in changed && changed[k] !== null;
          const was = isNew && prevVars[k] !== undefined ? `<div class="xv-was">was ${showVal(clip(prevVars[k], 80))}</div>` : '';
          vh += `<div class="xv-v${isNew ? ' chg' : ''}"><span class="xv-k">${escH(nice(k))}</span><span class="xv-val">${showVal(v[k])}${was}</span></div>`;
        }
      }
      q('.xv-vars').innerHTML = vh || '<div class="xv-empty">No variables yet.</div>';
      // stack
      const stack = t._stacks[i];
      q('.xv-stack').innerHTML = stack.length
        ? stack.slice().reverse().map((f, j) => `<div class="xv-fr${j === 0 ? ' top' : ''}">${escH(f)}</div>`).join('')
        : '<div class="xv-empty">Nothing is running.</div>';
      // output
      const end = t._outLen[i], start = i > 0 ? t._outLen[i - 1] : 0;
      const out = q('.xv-out');
      out.innerHTML = end ? escH(t._full.slice(0, start)) + (end > start ? `<mark>${escH(t._full.slice(start, end))}</mark>` : '') : '<span class="xv-empty">Nothing printed yet.</span>';
      out.scrollTop = out.scrollHeight;
      q('[data-x="play"]').textContent = st.playing ? '❚❚ Pause' : (i === N ? '↺ Replay' : '▶ Play');
    }

    function go(i) { st.i = Math.max(0, Math.min(N, i)); render(); }
    function tick() {
      if (!root.isConnected) { pause(); live.delete(inst); return; }
      if (st.i >= N) { pause(); return; }
      go(st.i + 1);
      st.timer = setTimeout(tick, BASE_MS / SPEEDS[speedIdx]);
    }
    function play() {
      live.forEach(o => { if (o !== inst) o.stop(); });
      if (st.i >= N) go(0);
      st.playing = true;
      render();
      st.timer = setTimeout(tick, BASE_MS / SPEEDS[speedIdx]);
    }
    function pause() { st.playing = false; clearTimeout(st.timer); if (root.isConnected) q('[data-x="play"]').textContent = st.i === N ? '↺ Replay' : '▶ Play'; }
    function jumpToLine(l) {
      for (let j = st.i + 1; j < N; j++) if (t.steps[j].l === l) return go(j);
      for (let j = 0; j <= st.i && j < N; j++) if (t.steps[j].l === l) return go(j);
      q('.xv-say').innerHTML = `<b>Line ${l} never runs</b> in this recording. It may be a comment, a blank line, a declaration, or code that this run did not need.`;
    }

    root.addEventListener('click', e => {
      const b = e.target.closest('[data-x]');
      if (b) {
        const a = b.dataset.x;
        if (a === 'play') { st.playing ? pause() : play(); return; }
        pause();
        if (a === 'reset') go(0);
        else if (a === 'back') go(st.i - 1);
        else if (a === 'fwd') go(st.i + 1);
        else if (a === 'end') go(N);
        return;
      }
      const g = e.target.closest('.xv-g');
      if (g) { pause(); jumpToLine(+g.parentElement.dataset.l); }
    });
    q('.xscrub').addEventListener('input', e => { pause(); go(+e.target.value); });
    q('.xsp').addEventListener('input', e => {
      speedIdx = +e.target.value;
      try { localStorage.setItem('xv-speed', String(speedIdx)); } catch (err) { /* storage unavailable */ }
      document.querySelectorAll('.xv .xsp').forEach(x => { x.value = speedIdx; });
      document.querySelectorAll('.xv .xspl').forEach(x => { x.textContent = SPEEDS[speedIdx] + 'x'; });
    });
    root.addEventListener('keydown', e => {
      const tag = e.target.tagName;
      if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') { e.stopPropagation(); return; }
      if (tag === 'BUTTON' && (e.key === ' ' || e.key === 'Enter')) { e.stopPropagation(); return; }
      let used = true;
      if (e.key === ' ') { st.playing ? pause() : play(); }
      else if (e.key === 'ArrowRight') { pause(); go(st.i + 1); }
      else if (e.key === 'ArrowLeft') { pause(); go(st.i - 1); }
      else if (e.key === 'Home') { pause(); go(0); }
      else if (e.key === 'End') { pause(); go(N); }
      else used = false;
      if (used) { e.preventDefault(); e.stopPropagation(); }
    });
    go(0);
    return inst;
  }

  function unmountIn(host) {
    if (host && host._xv) { host._xv.stop(); live.delete(host._xv); host._xv = null; }
  }
  function stopAll() { live.forEach(o => o.stop()); }

  /* The switch between the plain code view and the step viewer. */
  function toggleHtml() {
    return `<div class="xv-mode" role="group" aria-label="How to show the code">
      <button data-xmode="read" class="${mode === 'read' ? 'on' : ''}">Plain code</button>
      <button data-xmode="step" class="${mode === 'step' ? 'on' : ''}">▶ Run line by line</button>
    </div>`;
  }
  function setMode(m) {
    mode = m;
    try { localStorage.setItem('xv-mode', m); } catch (e) { /* storage unavailable */ }
    document.querySelectorAll('.xv-mode button').forEach(b => b.classList.toggle('on', b.dataset.xmode === mode));
    if (m === 'read') stopAll();
    listeners.forEach(f => f(m));
  }
  document.addEventListener('click', e => {
    const b = e.target.closest('.xv-mode button');
    if (b) setMode(b.dataset.xmode);
  });

  return { mount, unmountIn, stopAll, toggleHtml, setMode, mode: () => mode, onMode: f => listeners.push(f), splitLines, has: k => k in traces() };
})();
