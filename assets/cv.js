/* ===== Computer Vision chapter page: tabs, one lesson at a time, Python examples, assignments and summary =====
   The page is written by tools/cv-build/build.py. Data comes from three script tags:
     #cvdata    { slug, topic, subject, title, codes: { key: { src, stdin, out } }, quiz, calc, assign, must, summary }
     #cvtrace   { key: recording made with CPython by tools/py-build/pytrace.py }
     #cvtracer  the source of pytrace.py, so an edited program can be recorded in the browser with Pyodide
   Hashes: #<lesson id> opens that lesson. #formulas, #problems, #quiz, #assign and #summary open a tab. */
(() => {
  const D = JSON.parse(document.getElementById('cvdata').textContent);
  const REC = JSON.parse(document.getElementById('cvtrace').textContent);
  const tracerEl = document.getElementById('cvtracer');
  if (tracerEl && PYPLAY.setTracer) PYPLAY.setTracer(tracerEl.textContent);
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  /* Computer Vision keeps its original keys. Other subjects add their name so equal slugs do not share progress. */
  const KEY = !D.subject || D.subject === 'computer-vision' ? 'cv-' : 'cv-' + D.subject + '-';
  const store = {
    get(k, d) { try { const v = localStorage.getItem(KEY + D.slug + '-' + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(KEY + D.slug + '-' + k, JSON.stringify(v)); } catch (e) { /* storage unavailable */ } }
  };

  /* ---------- theme button on the standalone page ---------- */
  const tb = $('#cvTheme');
  const paintTheme = () => { if (tb) tb.textContent = FUN.currentTheme() === 'dark' ? 'Light mode' : 'Dark mode'; };
  if (tb) tb.onclick = () => { FUN.toggleTheme(); paintTheme(); };
  paintTheme();

  /* ---------- tabs and lessons ---------- */
  const tabs = $$('.cv-tab'), panes = $$('.cv-pane'), lessons = $$('.cv-lesson'), stepLinks = $$('.cv-stepper a');
  const lessonIds = lessons.map(l => l.dataset.l);
  const tabIds = tabs.map(t => t.dataset.tab);
  const built = {};
  const seen = new Set(store.get('seen', []));

  function setHash(h) {
    const nh = h ? '#' + h : '';
    if (location.hash !== nh) { history.replaceState(null, '', location.pathname + location.search + nh); FUN.reportHash(); }
  }
  function openTab(id, lessonId, scroll) {
    if (!tabIds.includes(id)) id = 'learn';
    tabs.forEach(t => { const on = t.dataset.tab === id; t.classList.toggle('on', on); t.setAttribute('aria-selected', on); });
    panes.forEach(p => { p.hidden = p.dataset.pane !== id; });
    if (!built[id]) { build(id); built[id] = true; }
    if (id === 'learn') {
      const lid = lessonIds.includes(lessonId) ? lessonId : (lessonIds.includes(store.get('lesson')) ? store.get('lesson') : lessonIds[0]);
      showLesson(lid);
      setHash(lid);
    } else setHash(id);
    if (scroll) toTop();
  }
  /* back to the top of the chapter part, just under the sticky tabs. scrollIntoView on the sticky tab bar does nothing once it is stuck */
  function toTop() {
    const bar = $('.cv-tabs'), pane = panes.find(p => !p.hidden);
    const y = pane ? pane.getBoundingClientRect().top + window.scrollY - (bar ? bar.offsetHeight : 0) - 6 : 0;
    window.scrollTo({ top: Math.max(0, y), behavior: FUN.reduce ? 'auto' : 'smooth' });
  }
  function showLesson(id) {
    lessons.forEach(l => { l.hidden = l.dataset.l !== id; });
    seen.add(id); store.set('seen', [...seen]); store.set('lesson', id);
    stepLinks.forEach(a => { a.classList.toggle('on', a.dataset.l === id); a.classList.toggle('seen', seen.has(a.dataset.l)); });
    const on = stepLinks.find(a => a.dataset.l === id);
    if (on) { const ol = on.closest('.cv-stepper'), li = on.parentElement; ol.scrollLeft = Math.max(0, li.offsetLeft - ol.offsetLeft - (ol.clientWidth - li.offsetWidth) / 2); }
    const art = lessons.find(l => l.dataset.l === id);
    if (art && typeof CVZ !== 'undefined') CVZ.mountAll(art);
    if (art) $$('.cv-code[data-k]', art).forEach(mountCode);
  }
  /* arrows on both ends of the lesson row, so a reader sees that more lessons are hidden to the side */
  $$('.cv-stepper').forEach(ol => {
    const wrap = document.createElement('div');
    wrap.className = 'cv-stepwrap';
    ol.parentNode.insertBefore(wrap, ol);
    const arrow = (dir, label) => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'cv-sarrow ' + dir; b.setAttribute('aria-label', label); b.hidden = true;
      b.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="' + (dir === 'left' ? 'M15 5l-7 7 7 7' : 'M9 5l7 7-7 7') + '" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
      b.addEventListener('click', () => ol.scrollBy({ left: (dir === 'left' ? -1 : 1) * Math.max(160, ol.clientWidth * 0.7), behavior: FUN.reduce ? 'auto' : 'smooth' }));
      return b;
    };
    const lb = arrow('left', 'Show earlier lessons'), rb = arrow('right', 'Show more lessons');
    wrap.append(lb, ol, rb);
    const paint = () => {
      const max = ol.scrollWidth - ol.clientWidth;
      lb.hidden = ol.scrollLeft <= 2; rb.hidden = ol.scrollLeft >= max - 2;
      wrap.classList.toggle('fade-l', !lb.hidden); wrap.classList.toggle('fade-r', !rb.hidden);
    };
    ol.addEventListener('scroll', paint, { passive: true });
    window.addEventListener('resize', paint);
    new MutationObserver(paint).observe(ol, { attributes: true, subtree: true, attributeFilter: ['class'] });
    setTimeout(paint, 50); paint();
  });

  tabs.forEach(t => t.addEventListener('click', () => openTab(t.dataset.tab, null, false)));
  stepLinks.forEach(a => a.addEventListener('click', e => { e.preventDefault(); showLesson(a.dataset.l); setHash(a.dataset.l); toTop(); }));

  lessons.forEach((art, i) => {
    const nav = $('.cv-lnav', art);
    const pv = lessons[i - 1], nx = lessons[i + 1];
    nav.innerHTML = (pv ? `<button type="button" class="cv-btn" data-go="${pv.dataset.l}">Previous: ${esc($('h2', pv).textContent)}</button>` : '<span></span>') +
      (nx ? `<button type="button" class="cv-btn primary" data-go="${nx.dataset.l}">Next: ${esc($('h2', nx).textContent)}</button>`
        : `<button type="button" class="cv-btn primary" data-tab-go="${tabIds.includes('problems') ? 'problems' : tabIds[1] || 'learn'}">Lessons done. Practise now</button>`);
  });
  document.addEventListener('click', e => {
    const g = e.target.closest('[data-go]');
    if (g) { if (!panes.find(p => p.dataset.pane === 'learn' && !p.hidden)) { openTab('learn', g.dataset.go, true); return; } showLesson(g.dataset.go); setHash(g.dataset.go); toTop(); return; }
    const tg = e.target.closest('[data-tab-go]');
    if (tg) { openTab(tg.dataset.tabGo, null, true); return; }
    const lt = e.target.closest('.ld-t');
    if (lt) {
      const box = lt.closest('.ladder');
      $$('.ld-t', box).forEach(b => b.classList.toggle('on', b === lt));
      $$('.ld-p', box).forEach(p => { p.hidden = p.dataset.ld !== lt.dataset.ld; });
      return;
    }
    const wk = e.target.closest('.walk-ctl button');
    if (wk) {
      const lis = $$('.walk-l li', wk.closest('.walk'));
      if (wk.classList.contains('wk-next')) { const h = lis.find(li => li.classList.contains('hide')); if (h) h.classList.remove('hide'); }
      else if (wk.classList.contains('wk-all')) lis.forEach(li => li.classList.remove('hide'));
      else lis.forEach((li, k) => li.classList.toggle('hide', k > 0));
    }
  });
  $$('.walk').forEach(w => $$('.walk-l li', w).forEach((li, k) => { if (k) li.classList.add('hide'); }));

  /* ---------- the other tabs ---------- */
  function build(id) {
    const pane = $(`.cv-pane[data-pane="${id}"]`);
    if (!pane || id === 'learn') return;
    if (id === 'formulas') {
      const groups = lessons.map((l, i) => {
        const cards = $$('.fx', l);
        if (!cards.length) return '';
        return `<h3>Lesson ${i + 1}: ${esc($('h2', l).textContent)}</h3><div class="fx-grid">${cards.map(c => c.outerHTML).join('')}</div>
          <p class="fx-from"><a href="#${l.dataset.l}" data-go="${l.dataset.l}">Open this lesson</a></p>`;
      }).join('');
      pane.innerHTML = `<h2>Formula sheet</h2><p class="sub">Every formula from this chapter in one place. Cards marked Exam favourite come up most often in tests.</p><div class="cv-formulas">${groups || '<p>This chapter has no formulas.</p>'}</div>`;
      $$('[data-go]', pane).forEach(a => a.addEventListener('click', e => { e.preventDefault(); openTab('learn', a.dataset.go, true); }));
    } else if (id === 'problems') {
      pane.innerHTML = `<h2>Worked problems</h2><p class="sub">Solve each one on paper with the formula sheet, type your answer and press Check. The full working opens after a correct answer, or when you ask for it.</p>` +
        LEARN.calcHtml(D.calc, { lang: 'py', title: 'Worked problems', sub: 'Four levels, from a first try to exam standard.' });
    } else if (id === 'quiz') {
      pane.innerHTML = `<h2>Quiz</h2><p class="sub">Pick an answer to see why it is right or wrong. Your best score is saved on the learning path.</p>` +
        LEARN.quizHtml(D.quiz, { lang: 'py', title: 'Check your understanding', sub: 'Easy questions test the idea, expert ones test the reasoning.' });
    } else if (id === 'assign') {
      pane.innerHTML = `<h2>Assignments</h2><p class="sub">Write real Python in the box and press Run the tests. The tests run in your browser with Pyodide, the same Python as on a computer. Every model answer passed the same tests when this page was built.</p>` +
        D.assign.map(assignHtml).join('');
      wireAssign(pane);
    } else if (id === 'summary') {
      const done = new Set(store.get('must', []));
      pane.innerHTML = `<h2>What you must know</h2><p class="sub">Tick each point once you can explain it to a friend without notes. This list is the minimum for an exam or an interview.</p>
        ${D.summary ? `<div class="cv-lesson" style="margin-bottom:14px">${D.summary}</div>` : ''}
        <ul class="must">${D.must.map((m, i) => `<li><input type="checkbox" data-m="${i}"${done.has(i) ? ' checked' : ''} aria-label="I know this"><div><b>${m[0]}</b><span>${m[1]}</span></div></li>`).join('')}</ul>`;
      pane.addEventListener('change', e => {
        const c = e.target.closest('[data-m]');
        if (!c) return;
        const s = new Set(store.get('must', []));
        if (c.checked) s.add(+c.dataset.m); else s.delete(+c.dataset.m);
        store.set('must', [...s]);
      });
    }
  }

  /* ---------- Python examples ---------- */
  const hl = code => LEARN.hl(code, 'py').split('\n').map(l => `<span class="ln">${l || ' '}</span>`).join('');
  function mountCode(box) {
    if (box.dataset.ready) return;
    box.dataset.ready = '1';
    const c = D.codes[box.dataset.k];
    const usesInput = /\binput\(/.test(c.src);
    box.innerHTML = `<div class="cc-bar"><span class="lbl">Python</span><button type="button" class="b-step">Run line by line</button><button type="button" class="b-edit">Edit and run</button><button type="button" class="b-copy">Copy</button></div>
      <pre class="cc-src">${hl(c.src)}</pre>
      <div class="cc-cap">Output${usesInput ? ` with the sample input ${esc(JSON.stringify(c.stdin.replace(/\n$/, '')))}` : ''}</div><pre class="cc-out">${esc(c.out)}</pre>
      <div class="cc-live"></div>`;
    const live = $('.cc-live', box);
    $('.b-copy', box).onclick = e => {
      const ed = $('.cc-ed', box);
      const t = ed ? ed.value : c.src;
      const b = e.target, done = () => { b.textContent = 'Copied'; setTimeout(() => { b.textContent = 'Copy'; }, 1200); };
      if (navigator.clipboard) navigator.clipboard.writeText(t).then(done, done); else done();
    };
    $('.b-step', box).onclick = e => {
      const on = !e.target.classList.contains('on');
      $$('.cc-bar button', box).forEach(b => b.classList.remove('on'));
      if (!on) { live.innerHTML = ''; return; }
      e.target.classList.add('on');
      stepper(live, c.src, REC[box.dataset.k], 'Recorded with CPython when this page was built.');
    };
    $('.b-edit', box).onclick = e => {
      const on = !e.target.classList.contains('on');
      $$('.cc-bar button', box).forEach(b => b.classList.remove('on'));
      if (!on) { live.innerHTML = ''; return; }
      e.target.classList.add('on');
      editor(live, c, usesInput);
    };
  }

  function editor(host, c, usesInput) {
    host.innerHTML = `<div class="cc-cap">Your copy. Change any value, then run it</div><textarea class="cc-ed" spellcheck="false" aria-label="Python code"></textarea>
      ${usesInput || c.stdin ? `<div class="cc-in"><label>Input, one value per line</label><textarea class="cc-stdin" spellcheck="false">${esc(c.stdin)}</textarea></div>` : ''}
      <div class="st-ctl"><button type="button" class="r-run">Run</button><button type="button" class="r-trace">Run my code line by line</button><button type="button" class="r-stop" hidden>Stop</button><button type="button" class="r-reset">Reset the code</button></div>
      <div class="cc-status"></div><pre class="cc-out"></pre><div class="cc-trace"></div>`;
    const ed = $('.cc-ed', host), out = $('.cc-out', host), status = $('.cc-status', host), stop = $('.r-stop', host);
    ed.value = c.src;
    ed.style.height = Math.min(520, 24 + 21 * c.src.split('\n').length) + 'px';
    ed.addEventListener('keydown', e => {
      if (e.key === 'Tab') { e.preventDefault(); const s = ed.selectionStart; ed.setRangeText('    ', s, ed.selectionEnd, 'end'); }
    });
    const stdin = () => { const s = $('.cc-stdin', host); return s ? s.value + (s.value.endsWith('\n') ? '' : '\n') : ''; };
    const onStatus = t => { status.textContent = t; };
    $('.r-run', host).onclick = async () => {
      out.textContent = ''; $('.cc-trace', host).innerHTML = ''; stop.hidden = false;
      const r = await PYPLAY.run(ed.value, stdin(), (k, t) => {
        const s = document.createElement('span'); if (k === 'error') s.className = 'err'; s.textContent = t + '\n'; out.appendChild(s);
      }, onStatus);
      stop.hidden = true;
      if (r.k === 'fatal') status.textContent = r.t;
      else if (r.k === 'timeout') status.textContent = 'Stopped after 10 seconds. Look for a loop that never ends.';
      else if (r.k === 'stopped') status.textContent = 'Stopped.';
      else status.textContent = 'Finished in your browser with Python ' + PYPLAY.version + '.';
    };
    $('.r-trace', host).onclick = async () => {
      out.textContent = ''; stop.hidden = false;
      const r = await PYPLAY.trace(ed.value, stdin(), onStatus);
      stop.hidden = true;
      if (r.error) { status.textContent = r.error; return; }
      status.textContent = '';
      stepper($('.cc-trace', host), ed.value, r.rec, 'Recorded in your browser just now.');
    };
    stop.onclick = () => PYPLAY.stop();
    $('.r-reset', host).onclick = () => { ed.value = c.src; };
  }

  /* the line by line viewer: replays a recording step by step */
  function stepper(host, src, rec, note) {
    if (!rec || !rec.steps.length) { host.innerHTML = '<div class="cc-status">There is nothing to step through.</div>'; return; }
    const N = rec.steps.length;
    const vars = [], outs = [], stacks = [];
    let v = {}, o = '', s = ['module'];
    rec.steps.forEach(st => {
      if (st.d) { v = { ...v }; for (const k in st.d) { if (st.d[k] === null) delete v[k]; else v[k] = st.d[k]; } }
      if (st.o) o += st.o;
      if (st.s) s = st.s;
      vars.push(v); outs.push(o); stacks.push(s);
    });
    host.innerHTML = `<div class="st"><div class="st-ctl"><button type="button" class="s-first">First</button><button type="button" class="s-prev">Back</button><button type="button" class="s-play">Play</button><button type="button" class="s-next">Step</button>
      <input type="range" min="0" max="${N - 1}" value="0" aria-label="Step"><span class="pos"></span></div>
      <div class="st-body"><pre class="cc-src">${hl(src)}</pre><div class="st-side"><div class="st-ev"></div><h4>Variables</h4><table class="st-vars"></table><h4>Output so far</h4><pre class="st-o"></pre>
      ${rec.err ? `<h4>Error</h4><pre class="err">${esc(rec.err)}</pre>` : ''}${rec.cut ? '<p>The recording stops after 600 steps.</p>' : ''}<p style="color:var(--ink2);font-size:12px">${esc(note)}</p></div></div></div>`;
    const lines = $$('.ln', host), rng = $('input[type=range]', host), pos = $('.pos', host);
    let i = 0, timer = null;
    function paint() {
      const st = rec.steps[i];
      lines.forEach((l, k) => l.classList.toggle('cur', k === st.l - 1));
      const cur = lines[st.l - 1];
      if (cur) { const pre = cur.parentElement; const top = cur.offsetTop - pre.clientHeight / 2; pre.scrollTop = Math.max(0, top); }
      rng.value = i; pos.textContent = `Step ${i + 1} of ${N}`;
      const ev = st.ev === 'call' ? 'Entering a function' : st.ev === 'return' ? 'Leaving a function' : 'About to run line ' + st.l;
      $('.st-ev', host).textContent = `${ev}. Inside: ${stacks[i].join(' › ')}`;
      const prev = i ? vars[i - 1] : {};
      $('.st-vars', host).innerHTML = Object.keys(vars[i]).map(k => `<tr class="${prev[k] !== vars[i][k] ? 'chg' : ''}"><td>${esc(k.slice(2))}${k[0] === 'L' ? ' <small>(local)</small>' : ''}</td><td>${esc(vars[i][k])}</td></tr>`).join('') || '<tr><td>No variables yet</td></tr>';
      $('.st-o', host).textContent = outs[i] + (i === N - 1 ? rec.tail : '');
    }
    const go = k => { i = Math.max(0, Math.min(N - 1, k)); paint(); };
    $('.s-first', host).onclick = () => go(0);
    $('.s-prev', host).onclick = () => go(i - 1);
    $('.s-next', host).onclick = () => go(i + 1);
    rng.oninput = () => go(+rng.value);
    $('.s-play', host).onclick = e => {
      if (timer) { clearInterval(timer); timer = null; e.target.textContent = 'Play'; return; }
      if (i >= N - 1) go(0);
      e.target.textContent = 'Pause';
      timer = setInterval(() => { if (i >= N - 1 || !host.isConnected) { clearInterval(timer); timer = null; e.target.textContent = 'Play'; return; } go(i + 1); }, 650);
    };
    paint();
  }

  /* ---------- assignments ---------- */
  const LVN = { e: 'Easy', m: 'Medium', h: 'Hard', x: 'Expert' };
  function assignHtml(a, n) {
    const ok = store.get('as-' + a.id, false);
    return `<div class="as-item" data-id="${esc(a.id)}"><div class="as-head"><span class="as-lv ${a.lv}">${LVN[a.lv]}</span><h3>Assignment ${n + 1}: ${a.title}</h3><span class="as-state${ok ? ' ok' : ''}">${ok ? 'Passed' : 'Not passed yet'}</span></div>
      <div class="as-task">${a.task}</div>
      <textarea class="cc-ed" spellcheck="false" aria-label="Your solution"></textarea>
      <div class="st-ctl"><button type="button" class="a-run">Run the tests</button><button type="button" class="a-hint">Hint</button><button type="button" class="a-sol">Show the model answer</button><button type="button" class="a-reset">Reset</button></div>
      <div class="cc-status"></div>
      <ul class="as-tests">${a.tests.map(t => `<li>${esc(t.call)} should give ${esc(JSON.stringify(t.want))}</li>`).join('')}</ul>
      <div class="as-more"><div class="a-hintbox" hidden>${a.hint}</div><div class="a-solbox" hidden><pre class="cc-src">${hl(a.solution.trimEnd())}</pre><div>${a.why}</div></div></div></div>`;
  }
  function wireAssign(pane) {
    $$('.as-item', pane).forEach(box => {
      const a = D.assign.find(x => x.id === box.dataset.id);
      const ed = $('.cc-ed', box);
      ed.value = store.get('code-' + a.id, a.starter);
      ed.style.height = Math.min(480, 30 + 21 * ed.value.split('\n').length) + 'px';
      ed.addEventListener('input', () => store.set('code-' + a.id, ed.value));
      ed.addEventListener('keydown', e => { if (e.key === 'Tab') { e.preventDefault(); ed.setRangeText('    ', ed.selectionStart, ed.selectionEnd, 'end'); } });
      const status = $('.cc-status', box);
      $('.a-hint', box).onclick = () => { const h = $('.a-hintbox', box); h.hidden = !h.hidden; };
      $('.a-sol', box).onclick = () => { const h = $('.a-solbox', box); h.hidden = !h.hidden; };
      $('.a-reset', box).onclick = () => { ed.value = a.starter; store.set('code-' + a.id, a.starter); };
      $('.a-run', box).onclick = async () => {
        status.textContent = 'Running the tests';
        const r = await PYPLAY.runTests(ed.value, a.tests, t => { status.textContent = t; });
        const lis = $$('.as-tests li', box);
        if (r.error) { status.textContent = r.error; return; }
        if (r.res === undefined) { status.textContent = 'Your code did not run.'; return; }
        let good = 0;
        r.res.forEach((x, k) => {
          lis[k].className = x.ok ? 'ok' : 'bad';
          if (x.ok) good++;
          lis[k].textContent = `${x.ok ? 'Pass' : 'Fail'}: ${a.tests[k].call} should give ${JSON.stringify(a.tests[k].want)}` + (x.ok ? '' : x.err ? `, it raised ${x.err}` : `, it gave ${x.got}`);
        });
        const all = good === r.res.length;
        status.textContent = all ? 'Every test passes. Well done.' : `${good} of ${r.res.length} tests pass.`;
        if (all) { store.set('as-' + a.id, true); const s = $('.as-state', box); s.textContent = 'Passed'; s.classList.add('ok'); FUN.confetti(); }
      };
    });
  }

  /* ---------- start ---------- */
  function route() {
    const h = decodeURIComponent(location.hash.slice(1));
    if (lessonIds.includes(h)) openTab('learn', h);
    else if (tabIds.includes(h)) openTab(h);
    else openTab('learn');
  }
  window.addEventListener('hashchange', route);
  LEARN.wire();
  FUN.initScroll();
  if (FUN.inFrame) $$('.cv-pager a[data-topic], a.cv-sheet[data-topic]').forEach(a => { a.href = '../../subject.html?s=' + D.subject + '&t=' + a.dataset.topic + (a.dataset.h ? '#' + a.dataset.h : ''); a.target = '_top'; });
  else { const hl2 = $('.home-link'); if (hl2) hl2.removeAttribute('target'); }
  route();
})();
