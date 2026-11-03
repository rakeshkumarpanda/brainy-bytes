/* ===== Python chapter page: tabs and one lesson at a time, in the same layout as the Computer Vision and NLP pages =====
   The page is written by tools/py-build/build.py. assets/pyplay.js has already filled the quiz, the worked problems,
   the assignments and the summary when this file runs. This file only decides what is visible.
   Hashes: #<lesson id> opens that lesson. #problems, #quiz, #assign and #summary open a tab. The older hashes
   #numbers, #practice, #comic, #real-life and the exercise ids still work, so links from the catalog keep working. */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const KEY = 'py-path-' + location.pathname.split('/').pop().replace(/\.html$/, '') + '-';
  const store = {
    get(k, d) { try { const v = localStorage.getItem(KEY + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(KEY + k, JSON.stringify(v)); } catch (e) { /* storage unavailable */ } }
  };

  /* theme button on the standalone page */
  const tb = $('#cvTheme');
  const paintTheme = () => { if (tb) tb.textContent = FUN.currentTheme() === 'dark' ? 'Light mode' : 'Dark mode'; };
  if (tb) tb.onclick = () => { FUN.toggleTheme(); paintTheme(); };
  paintTheme();

  const tabs = $$('.cv-tab'), panes = $$('.cv-pane'), lessons = $$('.cv-lesson'), stepLinks = $$('.cv-stepper a');
  const lessonIds = lessons.map(l => l.dataset.l);
  const tabIds = tabs.map(t => t.dataset.tab);
  const exIds = (typeof PAGE !== 'undefined' && PAGE.ex ? PAGE.ex : []).map(e => e.id);
  const ALIAS = { numbers: 'problems', practice: 'assign', comic: 'summary', 'real-life': 'summary' };
  const seen = new Set(store.get('seen', []));

  function setHash(h) {
    const nh = h ? '#' + h : '';
    if (location.hash !== nh) { history.replaceState(null, '', location.pathname + location.search + nh); if (FUN.reportHash) FUN.reportHash(); }
  }
  /* back to the top of the visible part, just under the sticky tabs */
  function toTop() {
    const bar = $('.cv-tabs'), pane = panes.find(p => !p.hidden);
    const y = pane ? pane.getBoundingClientRect().top + window.scrollY - (bar ? bar.offsetHeight : 0) - 6 : 0;
    window.scrollTo({ top: Math.max(0, y), behavior: FUN.reduce ? 'auto' : 'smooth' });
  }
  function openTab(id, lessonId, scroll) {
    if (!tabIds.includes(id)) id = 'learn';
    tabs.forEach(t => { const on = t.dataset.tab === id; t.classList.toggle('on', on); t.setAttribute('aria-selected', on); });
    panes.forEach(p => { p.hidden = p.dataset.pane !== id; });
    if (id === 'learn') {
      const lid = lessonIds.includes(lessonId) ? lessonId : (lessonIds.includes(store.get('lesson')) ? store.get('lesson') : lessonIds[0]);
      showLesson(lid);
      setHash(lid);
    } else setHash(id);
    if (scroll) toTop();
  }
  function showLesson(id) {
    lessons.forEach(l => { l.hidden = l.dataset.l !== id; });
    seen.add(id); store.set('seen', [...seen]); store.set('lesson', id);
    stepLinks.forEach(a => { a.classList.toggle('on', a.dataset.l === id); a.classList.toggle('seen', seen.has(a.dataset.l)); });
    const on = stepLinks.find(a => a.dataset.l === id);
    if (on) { const ol = on.closest('.cv-stepper'), li = on.parentElement; ol.scrollLeft = Math.max(0, li.offsetLeft - ol.offsetLeft - (ol.clientWidth - li.offsetWidth) / 2); }
    const art = lessons.find(l => l.dataset.l === id);
    if (art) art.dispatchEvent(new CustomEvent('lesson-shown', { bubbles: true }));
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
        : '<button type="button" class="cv-btn primary" data-tab-go="problems">Lessons done. Practise now</button>');
  });
  document.addEventListener('click', e => {
    const g = e.target.closest('[data-go]');
    if (g) { if (!panes.find(p => p.dataset.pane === 'learn' && !p.hidden)) { openTab('learn', g.dataset.go, true); return; } showLesson(g.dataset.go); setHash(g.dataset.go); toTop(); return; }
    const tg = e.target.closest('[data-tab-go]');
    if (tg) { openTab(tg.dataset.tabGo, null, true); return; }
    /* links inside a lesson to another lesson, such as <a href="#pyc"> */
    const a = e.target.closest('a[href^="#"]');
    if (a && !a.closest('.cv-stepper')) {
      const h = decodeURIComponent(a.getAttribute('href').slice(1));
      if (lessonIds.includes(h)) { e.preventDefault(); openTab('learn', h, true); }
    }
  });

  function route() {
    const h = decodeURIComponent(location.hash.slice(1));
    if (lessonIds.includes(h)) openTab('learn', h);
    else if (tabIds.includes(h)) openTab(h);
    else if (ALIAS[h]) openTab(ALIAS[h]);
    else if (exIds.includes(h)) { openTab('assign'); const el = document.getElementById(h) || $(`[data-id="${h}"]`); if (el) el.scrollIntoView(); }
    else openTab('learn');
  }
  window.addEventListener('hashchange', route);
  route();
})();
