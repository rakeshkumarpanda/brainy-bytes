/* ===== Page glue: builds the comic, interview, practice, quiz and number sections, then wires everything ===== */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const { esc, store, cheer } = APIW;
  const SLUG = 'api-manual';
  const LV = { e: ['Easy', '🌱', 'easy'], m: ['Medium', '🌿', 'med'], h: ['Hard', '🔥', 'hard'], x: ['Expert', '🧠', 'exp'] };

  function practiceHtml(list) {
    const solved = new Set(JSON.parse(store.get('lh-solved-' + SLUG) || '[]'));
    const order = ['e', 'm', 'h', 'x'];
    const tabs = order.map((l, n) => `<button type="button" class="lq-tab lv-${LV[l][2]}${n ? '' : ' on'}" role="tab" data-lv="${l}" aria-selected="${!n}"><span class="lq-tem">${LV[l][1]}</span><span>${LV[l][0]}</span><span class="lq-tct">${list.filter(p => p.lv === l).length}</span></button>`).join('');
    const panes = order.map((l, n) => `<div class="lq-pane pp-pane" data-lv="${l}"${n ? ' hidden' : ''}>${list.filter(p => p.lv === l).map((p, i) => `
      <article class="pp-item" id="${esc(p.id)}">
        <div class="pp-top"><span class="lq-n lv-${LV[l][2]}">P${i + 1}</span><h3>${esc(p.title)}</h3>
          <label class="pp-done"><input type="checkbox" data-pid="${esc(p.id)}"${solved.has(p.id) ? ' checked' : ''}> I did it</label></div>
        <div class="pp-st">${p.statement}</div>
        <div class="lq-tools"><button type="button" class="pp-hint">💡 Hint</button><button type="button" class="pp-sol">🧠 Model answer</button></div>
        <div class="lq-hint" hidden>${p.hint}</div>
        <div class="pp-solution" hidden>${p.solution}</div>
      </article>`).join('')}</div>`).join('');
    return `<div class="lq pp"><div class="lq-head"><div class="lq-ic">🏋️</div><div class="lq-ht"><h3>Practice tasks</h3><p class="lq-sub">Real tester work from easy to expert. Try each one first, then compare with the model answer.</p></div>
      <div class="lq-score"><b class="pp-count">${solved.size}</b><span>/${list.length}</span><small>done</small></div></div>
      <div class="lq-tabs" role="tablist">${tabs}</div>${panes}</div>`;
  }
  function wirePractice(root) {
    root.addEventListener('click', e => {
      const item = e.target.closest('.pp-item');
      if (!item) return;
      if (e.target.closest('.pp-hint')) { const h = $('.lq-hint', item); h.hidden = !h.hidden; }
      if (e.target.closest('.pp-sol')) { const s = $('.pp-solution', item); s.hidden = !s.hidden; e.target.closest('.pp-sol').textContent = s.hidden ? '🧠 Model answer' : '🙈 Hide answer'; }
    });
    root.addEventListener('change', e => {
      const cb = e.target.closest('input[data-pid]');
      if (!cb) return;
      const solved = new Set(JSON.parse(store.get('lh-solved-' + SLUG) || '[]'));
      if (cb.checked) solved.add(cb.dataset.pid); else solved.delete(cb.dataset.pid);
      store.set('lh-solved-' + SLUG, JSON.stringify([...solved]));
      $('.pp-count', root).textContent = solved.size;
      if (cb.checked) cheer(cb);
    });
  }

  /* ----- assemble ----- */
  $('#comic').innerHTML = XTRA.infoHtml(PAGE.info);
  IQ.mount($('.iq-host'), INTERVIEW.questions, { key: 'api-manual', title: INTERVIEW.title, sub: 'Real interview questions from easy to expert. Write your answer first, open the hint if you are stuck, then compare with the model answer and rate yourself.', lang: 'js', must: INTERVIEW.must });
  $('#practice').innerHTML = practiceHtml(PAGE.practice);
  $('#quiz').innerHTML = LEARN.quizHtml(PAGE.quiz, { lang: 'js', sub: 'Six questions per level from easy to expert. Every answer comes with the reason behind it.' });
  $('#numbers').innerHTML = LEARN.calcHtml(PAGE.calc, { lang: 'js', sub: 'Pages, limits, SLAs, percentiles and retries. Type your answer and press Check, or open the working.' });
  wirePractice($('#practice'));
  document.querySelectorAll('.chain .ch-step').forEach((s, i) => s.style.setProperty('--i', i));
  APIW.mountAll(document);
  XTRA.wire(document);
  LEARN.wire();
  FUN.initScroll();
  FUN.observe();
  VOICE.setup({ title: 'Manual API Testing: Basics to Expert', segments: PAGE.say });
  $('#listenAll').onclick = () => VOICE.playAll();

  /* scenario tabs */
  document.querySelectorAll('.scn-tab').forEach(t => t.addEventListener('click', () => {
    document.querySelectorAll('.scn-tab').forEach(x => x.classList.toggle('on', x === t));
    document.querySelectorAll('.scn-pane').forEach(p => { p.hidden = p.dataset.scn !== t.dataset.scn; });
  }));

  /* theme button (hidden inside the portal, which has its own) */
  const tb = $('#themeBtn');
  const tbl = () => { tb.textContent = FUN.currentTheme() === 'dark' ? '☀️ Light' : '🌙 Dark'; };
  tb.onclick = () => { FUN.toggleTheme(); tbl(); };
  tbl();

  /* the home link works inside the portal folder, and becomes plain text anywhere else */
  if (!FUN.inFrame) {
    const h = $('.home-link');
    if (location.pathname.includes('/content/api-testing/')) h.removeAttribute('target');
    else h.replaceWith(Object.assign(document.createElement('span'), { textContent: h.textContent }));
  }

  /* a link straight to a practice task opens its level tab first */
  function revealHash() {
    let id = '';
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (e) { return; }
    const el = id && document.getElementById(id);
    if (!el) return;
    const pane = el.closest('.lq-pane');
    if (pane && pane.hidden) {
      const tab = pane.closest('.lq').querySelector(`.lq-tab[data-lv="${pane.dataset.lv}"]`);
      if (tab) tab.click();
    }
    setTimeout(() => el.scrollIntoView({ block: 'start' }), 80);
  }
  window.addEventListener('hashchange', revealHash);
  revealHash();
})();
