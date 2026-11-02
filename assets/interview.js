/* ===== Interview questions, shared by every subject =====
   Each question walks the learner through three steps:
     1. write your own answer in the box
     2. open the hint if you are stuck
     3. show the model answer with a detailed explanation, then rate yourself
   The answer button unlocks once the learner has typed something or opened the hint.
   Notes, opened hints, shown answers and ratings are saved in localStorage under opts.key.

   IQ.mount(el, items, opts)  draws the whole card into el and turns on the buttons.
   IQ.html(items, opts)       returns the HTML only, then call IQ.wire() once.

   Item:
     { id: 'unique-in-subject', topic: 'OOP', lv: 'e'|'m'|'h'|'x', kind?: 'Concept'|'Scenario'|'Coding'|'Output',
       q: 'question html', code?: 'source shown under the question', lang?: 'java'|'py'|'js',
       hint: 'html', answer: 'short model answer html', points?: ['key point html', ...],
       explain: 'detailed explanation html', acode?: 'source shown inside the answer', follow?: ['follow up question', ...] }
   Opts:
     { key: 'storage key, unique per subject', title?, sub?, lang?: default code language,
       must?: [['emoji', 'Topic', 'Why it matters html'], ...]  the most important topics shown first } */
const IQ = (() => {
  const LV = { e: ['Easy', '🌱', 'easy'], m: ['Medium', '🌿', 'med'], h: ['Hard', '🔥', 'hard'], x: ['Expert', '🧠', 'exp'] };
  const ORDER = ['e', 'm', 'h', 'x'];
  const KIND = { Concept: '📘', Scenario: '🌍', Coding: '⌨️', Output: '🖨️', Design: '🏗️' };
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const hl = (c, lang) => (typeof LEARN !== 'undefined' && LEARN.hl) ? LEARN.hl(c, lang) : esc(c);
  const codeHtml = (c, lang) => c ? `<pre class="lq-code">${hl(c, lang)}</pre>` : '';
  const boards = {};

  function load(key) {
    try { return JSON.parse(localStorage.getItem('iq:' + key)) || {}; } catch (e) { return {}; }
  }
  function save(key) {
    try { localStorage.setItem('iq:' + key, JSON.stringify(boards[key].state)); } catch (e) { /* private mode, keep going */ }
  }

  function mustHtml(must) {
    if (!must || !must.length) return '';
    return `<details class="iq-must" open><summary>⭐ Most important topics for interviews</summary><div class="iq-mgrid">${must.map(([em, t, why]) =>
      `<div class="iq-mcard"><span class="iq-mem">${em}</span><div><b>${t}</b><p>${why}</p></div></div>`).join('')}</div></details>`;
  }

  function itemHtml(it, n, lang) {
    const l = LV[it.lv] || LV.m;
    const kind = it.kind || 'Concept';
    return `<div class="iq-item" data-id="${esc(it.id)}" data-lv="${it.lv}" data-topic="${esc(it.topic)}">
      <div class="lq-q"><span class="lq-n lv-${l[2]}">Q${n}</span><div>
        <div class="iq-tags"><span class="iq-tag lv-${l[2]}">${l[1]} ${l[0]}</span><span class="iq-tag">${KIND[kind] || '📘'} ${esc(kind)}</span><span class="iq-tag">${esc(it.topic)}</span><span class="iq-mark" aria-live="polite"></span></div>
        <div class="iq-qt">${it.q}</div></div></div>
      ${codeHtml(it.code, it.lang || lang)}
      <label class="iq-lbl" for="iq-${esc(it.id)}">✍️ Step 1. Write your answer first</label>
      <textarea class="iq-in" id="iq-${esc(it.id)}" rows="3" placeholder="Answer as you would in the interview. Short points are fine."></textarea>
      <div class="lq-tools">
        <button type="button" class="lq-hintbtn iq-hb">💡 Step 2. Show hint</button>
        <button type="button" class="iq-ab" disabled title="Write something or open the hint first">✅ Step 3. Show answer</button>
      </div>
      <div class="lq-hint iq-hint" hidden>${it.hint}</div>
      <div class="iq-ans" hidden>
        <div class="iq-mine" hidden><b>Your answer</b><div class="iq-mtext"></div></div>
        <div class="iq-model"><b>Model answer</b><div>${it.answer}</div>${it.points && it.points.length ? `<ul class="iq-pts">${it.points.map(p => `<li>${p}</li>`).join('')}</ul>` : ''}</div>
        <div class="iq-explain"><b>Detailed explanation</b><div>${it.explain}</div>${codeHtml(it.acode, it.lang || lang)}</div>
        ${it.follow && it.follow.length ? `<div class="iq-follow"><b>Follow up questions the interviewer may ask</b><ul>${it.follow.map(f => `<li>${f}</li>`).join('')}</ul></div>` : ''}
        <div class="iq-rate"><span>How did you do?</span>
          <button type="button" class="iq-rb" data-r="k">🎯 I knew it</button>
          <button type="button" class="iq-rb" data-r="p">🤏 Partly</button>
          <button type="button" class="iq-rb" data-r="r">🔁 Review again</button>
        </div>
      </div>
    </div>`;
  }

  function html(items, opts = {}) {
    if (!items || !items.length) return '';
    const key = opts.key || 'default';
    const lang = opts.lang || 'java';
    const lvls = ORDER.filter(l => items.some(it => it.lv === l));
    const topics = [...new Set(items.map(it => it.topic))];
    let n = 0;
    return `<div class="iq" data-key="${esc(key)}">
      <div class="lq-head"><div class="lq-ic">🎤</div><div class="lq-ht"><h3>${opts.title || 'Interview questions'}</h3>
        <p class="lq-sub">${opts.sub || 'Try each one on your own first. Use the hint if you are stuck, then open the answer and rate yourself.'}</p></div>
        <div class="lq-score iq-score" aria-live="polite"><b>0</b><span>/${items.length}</span><small>known</small></div></div>
      ${mustHtml(opts.must)}
      <div class="iq-bar"><div class="iq-prog"><i></i></div><span class="iq-stat"></span></div>
      <div class="iq-filters">
        <div class="lq-tabs" role="group" aria-label="Level">
          <button type="button" class="lq-tab on iq-lv" data-lv="">🗂️ All <span class="lq-tct">${items.length}</span></button>
          ${lvls.map(l => `<button type="button" class="lq-tab lv-${LV[l][2]} iq-lv" data-lv="${l}">${LV[l][1]} ${LV[l][0]} <span class="lq-tct">${items.filter(it => it.lv === l).length}</span></button>`).join('')}
        </div>
        <div class="iq-chips" role="group" aria-label="Topic">
          <button type="button" class="iq-chip on" data-topic="">All topics</button>
          ${topics.map(t => `<button type="button" class="iq-chip" data-topic="${esc(t)}">${esc(t)}</button>`).join('')}
        </div>
        <div class="iq-row">
          <input class="iq-search" type="search" placeholder="🔎 Search questions" aria-label="Search questions">
          <select class="iq-show" aria-label="Show">
            <option value="">Every question</option><option value="todo">Not tried yet</option><option value="r">Marked review again</option><option value="k">Marked I knew it</option>
          </select>
          <button type="button" class="lq-reset iq-reset">↺ Reset my progress</button>
        </div>
      </div>
      <div class="iq-list">${topics.map(t => `<h4 class="iq-th" data-topic="${esc(t)}">${esc(t)}</h4>` +
        items.filter(it => it.topic === t).sort((a, b) => ORDER.indexOf(a.lv) - ORDER.indexOf(b.lv)).map(it => itemHtml(it, ++n, lang)).join('')).join('')}</div>
      <p class="iq-empty" hidden>No questions match these filters.</p>
    </div>`;
  }

  const MARK = { k: '🎯 Knew it', p: '🤏 Partly', r: '🔁 Review' };

  function paintItem(box, s) {
    s = s || {};
    const ta = box.querySelector('.iq-in');
    if (s.t != null && ta.value !== s.t) ta.value = s.t;
    const hint = box.querySelector('.iq-hint'), hb = box.querySelector('.iq-hb');
    hint.hidden = !s.h; hb.classList.toggle('on', !!s.h);
    hb.textContent = s.h ? '💡 Hide hint' : '💡 Step 2. Show hint';
    const ab = box.querySelector('.iq-ab');
    ab.disabled = !(s.h || (s.t && s.t.trim()) || s.a);
    ab.textContent = s.a ? '🙈 Hide answer' : '✅ Step 3. Show answer';
    ab.classList.toggle('on', !!s.a);
    box.querySelector('.iq-ans').hidden = !s.a;
    const mine = box.querySelector('.iq-mine');
    mine.hidden = !(s.a && s.t && s.t.trim());
    if (!mine.hidden) box.querySelector('.iq-mtext').textContent = s.t;
    box.querySelectorAll('.iq-rb').forEach(b => b.classList.toggle('on', b.dataset.r === s.r));
    box.classList.remove('rk', 'rp', 'rr');
    if (s.r) box.classList.add('r' + s.r);
    box.querySelector('.iq-mark').textContent = s.r ? MARK[s.r] : '';
  }

  function paintBoard(root) {
    const b = boards[root.dataset.key];
    const items = [...root.querySelectorAll('.iq-item')];
    const st = b.state;
    const vals = items.map(x => st[x.dataset.id] || {});
    const known = vals.filter(v => v.r === 'k').length;
    const tried = vals.filter(v => v.a || v.r).length;
    const review = vals.filter(v => v.r === 'r').length;
    const sc = root.querySelector('.iq-score b');
    if (sc.textContent !== String(known)) { sc.textContent = known; const p = sc.parentNode; p.classList.remove('bump'); void p.offsetWidth; p.classList.add('bump'); }
    root.querySelector('.iq-prog i').style.width = (items.length ? 100 * tried / items.length : 0) + '%';
    root.querySelector('.iq-stat').textContent = `${tried} of ${items.length} answers opened, ${known} known, ${review} to review`;
  }

  function filter(root) {
    const lv = root.querySelector('.iq-lv.on').dataset.lv;
    const tp = root.querySelector('.iq-chip.on').dataset.topic;
    const q = root.querySelector('.iq-search').value.trim().toLowerCase();
    const show = root.querySelector('.iq-show').value;
    const st = boards[root.dataset.key].state;
    let any = 0;
    root.querySelectorAll('.iq-item').forEach(box => {
      const s = st[box.dataset.id] || {};
      let ok = (!lv || box.dataset.lv === lv) && (!tp || box.dataset.topic === tp);
      if (ok && q) ok = box.textContent.toLowerCase().includes(q);
      if (ok && show === 'todo') ok = !s.a && !s.r;
      else if (ok && show) ok = s.r === show;
      box.hidden = !ok;
      if (ok) any++;
    });
    root.querySelectorAll('.iq-th').forEach(h => {
      h.hidden = ![...root.querySelectorAll(`.iq-item[data-topic="${CSS.escape(h.dataset.topic)}"]`)].some(x => !x.hidden);
    });
    root.querySelector('.iq-empty').hidden = !!any;
  }

  function setup(root) {
    const key = root.dataset.key;
    if (boards[key] && boards[key].root === root) return;
    boards[key] = { root, state: load(key) };
    root.querySelectorAll('.iq-item').forEach(box => paintItem(box, boards[key].state[box.dataset.id]));
    paintBoard(root);
  }

  let wired = false;
  function wire() {
    document.querySelectorAll('.iq').forEach(setup);
    if (wired) return;
    wired = true;
    const ctx = el => {
      const root = el.closest('.iq');
      if (!root) return null;
      setup(root);
      const b = boards[root.dataset.key];
      const box = el.closest('.iq-item');
      const s = box ? (b.state[box.dataset.id] = b.state[box.dataset.id] || {}) : null;
      return { root, b, box, s };
    };
    document.addEventListener('click', e => {
      const el = e.target.closest('.iq-hb, .iq-ab, .iq-rb, .iq-lv, .iq-chip, .iq-reset');
      const c = el && ctx(el);
      if (!c) return;
      const { root, b, box, s } = c;
      if (el.classList.contains('iq-lv') || el.classList.contains('iq-chip')) {
        const sel = el.classList.contains('iq-lv') ? '.iq-lv' : '.iq-chip';
        root.querySelectorAll(sel).forEach(x => x.classList.toggle('on', x === el));
        filter(root);
        return;
      }
      if (el.classList.contains('iq-reset')) {
        if (!confirm('Clear your notes and ratings for these interview questions?')) return;
        b.state = {};
        save(root.dataset.key);
        root.querySelectorAll('.iq-item').forEach(x => { x.querySelector('.iq-in').value = ''; paintItem(x, {}); });
        paintBoard(root); filter(root);
        return;
      }
      if (el.classList.contains('iq-hb')) s.h = !s.h;
      else if (el.classList.contains('iq-ab')) s.a = !s.a;
      else if (el.classList.contains('iq-rb')) {
        s.r = s.r === el.dataset.r ? undefined : el.dataset.r;
        if (s.r === 'k' && typeof FUN !== 'undefined' && FUN.confetti) { const r = el.getBoundingClientRect(); FUN.confetti(r.left + r.width / 2, r.top); }
      }
      paintItem(box, s);
      save(root.dataset.key);
      paintBoard(root);
    });
    document.addEventListener('input', e => {
      const el = e.target;
      const c = el.matches && el.matches('.iq-in, .iq-search') && ctx(el);
      if (!c) return;
      if (el.classList.contains('iq-search')) { filter(c.root); return; }
      c.s.t = el.value;
      c.s.a = false;  /* the shown answer goes away while the reader edits their own answer */
      paintItem(c.box, c.s);
      save(c.root.dataset.key);
    });
    document.addEventListener('change', e => {
      const c = e.target.matches && e.target.matches('.iq-show') && ctx(e.target);
      if (c) filter(c.root);
    });
  }

  function mount(el, items, opts) {
    if (typeof el === 'string') el = document.querySelector(el);
    if (!el) return;
    el.innerHTML = html(items, opts);
    wire();
  }

  return { html, wire, mount, LV };
})();
if (typeof window !== 'undefined') window.IQ = IQ;
