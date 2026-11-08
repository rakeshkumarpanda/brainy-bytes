/* ===== Python style chapter layout for the older chapter pages =====
   The chapter pages of DSA, Java, TestNG, JavaScript, Manual Testing, Master the Claude, Playwright and Maths for ML
   all share one shape: a hero, a row of part links, a comic, the parts (section.jsec), Real life, Practice, Quiz
   and Number crunch. This file turns that page into the layout of the Python chapters without rebuilding anything:
     Learn            one part at a time, with a numbered lesson row and Previous and Next buttons
     Formulas         copies of the formula boxes of the lessons (only when the chapter has some)
     Worked problems  the Number crunch section
     Quiz             the quiz
     Practice         the practice problems or hands-on tasks
     Summary          the key idea of every lesson, the comic and the real life examples
   The existing sections are moved, never copied, so every animation, quiz and runnable example keeps its state.
   The script tag may carry data-kicker (for example "Step 2 · Topic 1 of 3 · Beginner") and data-sheet (the link
   to this chapter on the subject cheatsheet). tools/path-build/build.py writes both. */
(() => {
  const me = document.currentScript;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const wrap = $('.wrap'), hero = $('header.hero');
  const parts = $$('section.jsec');
  if (!wrap || !hero || !parts.length || document.body.classList.contains('pskin')) return;
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const F = typeof FUN !== 'undefined' ? FUN : {};
  const KEY = 'ps-' + location.pathname.split('/').slice(-2).join('-').replace(/\.html$/, '') + '-';
  const store = {
    get(k, d) { try { const v = localStorage.getItem(KEY + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(KEY + k, JSON.stringify(v)); } catch (e) { /* storage unavailable */ } }
  };
  const cfg = me ? me.dataset : {};
  document.body.classList.add('pskin');

  /* ---------- the header ---------- */
  const crumbBits = $$('.crumb > span').map(s => s.textContent.trim()).filter(t => t && t !== '›');
  const kicker = cfg.kicker || crumbBits.slice(-2).join(' · ');
  const h1 = $('h1', hero);
  if (h1 && kicker) {
    const k = document.createElement('div');
    k.className = 'ps-kicker';
    k.textContent = kicker;
    h1.parentNode.insertBefore(k, h1);
  }
  const chips = $('.chips', hero);
  if (chips && cfg.sheet) {
    const a = document.createElement('a');
    a.className = 'ps-sheet'; a.href = cfg.sheet; a.textContent = cfg.sheet.includes('#') ? 'This chapter on the cheatsheet' : 'Cheatsheets for this subject';
    const topic = cfg.sheet.split('/').pop().split('#')[0].replace(/\.html$/, '');
    a.dataset.topic = topic; a.dataset.h = (cfg.sheet.split('#')[1] || '');
    chips.appendChild(a);
  }
  /* the QA path and beginner path switches live in the part links row, which the tabs replace: keep them */
  $$('nav.toc .qa-toggle, nav.toc .cl-toggle').forEach(b => { b.classList.add('ps-toggle'); (chips || hero).appendChild(b); });
  $$('.reveal').forEach(e => e.classList.add('in'));

  /* ---------- the panes ---------- */
  /* a lesson may share an id with these (the Java program bank has a lesson called numbers), so skip the parts */
  const byId = id => $('section#' + id + ':not(.jsec)');
  const special = { comic: byId('comic'), real: byId('real-life'), practice: byId('practice'), quiz: byId('quiz'), numbers: byId('numbers') };
  const usable = el => el && !el.hasAttribute('hidden') && el.tagName === 'SECTION';
  const titleOf = sec => {
    const h = $('h2', sec);
    if (!h) return sec.id;
    /* the title is the plain span after the emoji; the narrator may add more spans to the heading */
    const t = $(':scope > span:not([class])', h);
    return (t ? t.textContent : h.textContent).trim();
  };
  const tabs = [];
  const anchor = document.createElement('div');
  hero.parentNode.insertBefore(anchor, (special.comic && special.comic.previousElementSibling === $('nav.toc')) ? special.comic : parts[0]);
  const bar = document.createElement('nav');
  bar.className = 'ps-tabs'; bar.setAttribute('role', 'tablist'); bar.setAttribute('aria-label', 'Parts of this chapter');
  anchor.appendChild(bar);
  function pane(id, label, count, intro) {
    const p = document.createElement('section');
    p.className = 'ps-pane'; p.dataset.pane = id; p.hidden = true;
    if (intro) p.innerHTML = `<h2 class="ps-ph">${esc(label)}</h2>${intro ? `<p class="ps-sub">${intro}</p>` : ''}`;
    anchor.appendChild(p);
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'ps-tab'; b.dataset.tab = id; b.setAttribute('role', 'tab');
    b.innerHTML = esc(label) + (count ? `<span class="ct">${count}</span>` : '');
    bar.appendChild(b);
    tabs.push({ id, b, p });
    return p;
  }

  /* Learn */
  const learn = pane('learn', 'Learn');
  const ol = document.createElement('ol');
  ol.className = 'ps-stepper';
  const sw = document.createElement('div');
  sw.className = 'ps-stepwrap';
  sw.appendChild(ol);
  learn.appendChild(sw);
  const lessons = parts.map((sec, i) => {
    sec.classList.add('ps-lesson', 'in');
    const num = $(':scope > .sec-num', sec);
    if (num) num.textContent = `Lesson ${i + 1} of ${parts.length}`;
    const t = titleOf(sec);
    const li = document.createElement('li');
    li.dataset.qa = sec.classList.contains('qa-part') ? '1' : '0';
    li.dataset.easy = sec.classList.contains('easy-part') ? '1' : '0';
    li.innerHTML = `<a href="#${esc(sec.id)}" data-l="${esc(sec.id)}"><span class="n">${i + 1}</span><span class="t">${esc(t)}</span></a>`;
    ol.appendChild(li);
    learn.appendChild(sec);
    return { id: sec.id, sec, title: t, link: $('a', li) };
  });
  const lessonIds = lessons.map(l => l.id);

  /* Formulas: copies of the formula boxes, each with a link back to its lesson */
  const fx = [];
  lessons.forEach(L => {
    $$('.fx', L.sec).forEach(card => fx.push({ L, html: card.outerHTML }));
    $$('.eq', L.sec).forEach(eq => {
      if (eq.closest('.fx')) return;
      const box = eq.closest('.box, .rule, .deep');
      const h = box && $('h4, .deep-h', box);
      fx.push({ L, title: h ? h.textContent.trim() : L.title, html: `<span class="eq">${eq.innerHTML}</span>` });
    });
  });
  if (fx.length >= 3) {
    const p = pane('formulas', 'Formulas', fx.length, 'Every formula and rule of this chapter in one place. Each card links back to the lesson that explains it.');
    const g = document.createElement('div');
    g.className = 'ps-fx';
    g.innerHTML = fx.map(f => f.title !== undefined
      ? `<div class="ps-fxc"><h4>${esc(f.title)}</h4>${f.html}<button type="button" class="ps-from" data-go="${esc(f.L.id)}">Lesson: ${esc(f.L.title)}</button></div>`
      : `<div class="ps-fxw">${f.html}<button type="button" class="ps-from" data-go="${esc(f.L.id)}">Lesson: ${esc(f.L.title)}</button></div>`).join('');
    p.appendChild(g);
  }
  /* the quiz and Number crunch widgets show their size as "0/8" in their score box */
  const countIn = el => { const s = el && $('.lq-score span', el); const m = s && s.textContent.match(/\d+/); return m ? +m[0] : 0; };
  if (usable(special.numbers)) pane('problems', 'Worked problems', countIn(special.numbers), '').appendChild(special.numbers);
  if (usable(special.quiz)) pane('quiz', 'Quiz', countIn(special.quiz), '').appendChild(special.quiz);
  if (usable(special.practice)) pane('practice', 'Practice', 0, '').appendChild(special.practice);

  /* Summary: the key idea of every lesson, then the comic and the real life examples */
  /* the same rules as tools/path-build/build.py uses for the cheatsheet: the first real paragraph of the lesson
     (not an instruction for an animation), and its rule box as the line to remember */
  const INSTR = /^(explore|press|click|tap|try|drag|pick|type|use the|step through|change|move|watch|choose|play|open|run)\b/i;
  const textOf = el => {
    const c = el.cloneNode(true);
    $$('.fr', c).forEach(f => { const s = $$(':scope > span', f); if (s.length === 2) f.textContent = `(${s[0].textContent})/(${s[1].textContent})`; });
    return c.textContent.replace(/\s+/g, ' ').trim();
  };
  const shorten = t => {
    if (t.length <= 260) return t;
    const cut = t.slice(0, 260), end = cut.lastIndexOf('. ');
    return end > 80 ? cut.slice(0, end + 1) : cut.replace(/\s+\S*$/, '') + ' ...';
  };
  const keyOf = sec => {
    const p = $$(':scope > p', sec).map(textOf).find(t => t.length > 40 && !INSTR.test(t));
    const rule = $('.rule', sec);
    return { idea: shorten(p || (rule ? textOf(rule) : '')), rule: p && rule ? shorten(textOf(rule)) : '' };
  };
  const sum = pane('summary', 'Summary', 0, 'The one idea to keep from each lesson. Open a lesson again when a line does not make sense yet.');
  const keys = document.createElement('ol');
  keys.className = 'ps-keys';
  keys.innerHTML = lessons.map(L => {
    const k = keyOf(L.sec);
    return `<li><b>${esc(L.title)}</b>${esc(k.idea)}${k.rule ? `<span class="ps-rule">Remember: ${esc(k.rule)}</span>` : ''}<br><button type="button" data-go="${esc(L.id)}">Open the lesson</button></li>`;
  }).join('');
  sum.appendChild(keys);
  if (usable(special.comic)) sum.appendChild(special.comic);
  if (usable(special.real)) sum.appendChild(special.real);

  /* Previous and Next under every lesson. They skip the lessons that the QA path or beginner path switch hides,
     so they are drawn again each time a lesson opens. */
  const firstPractice = ['problems', 'quiz', 'practice', 'summary'].find(id => tabs.some(t => t.id === id));
  const filtered = L => (document.body.classList.contains('qa-only') && !L.sec.classList.contains('qa-part')) ||
    (document.body.classList.contains('easy-only') && !L.sec.classList.contains('easy-part'));
  lessons.forEach(L => { L.nav = document.createElement('nav'); L.nav.className = 'ps-lnav'; L.sec.appendChild(L.nav); });
  function drawNav(L) {
    const list = lessons.filter(x => x === L || !filtered(x)), i = list.indexOf(L);
    const pv = list[i - 1], nx = list[i + 1];
    L.nav.innerHTML = (pv ? `<button type="button" class="ps-btn" data-go="${esc(pv.id)}">Previous: ${esc(pv.title)}</button>` : '<span></span>') +
      (nx ? `<button type="button" class="ps-btn primary" data-go="${esc(nx.id)}">Next: ${esc(nx.title)}</button>`
        : `<button type="button" class="ps-btn primary" data-tab-go="${firstPractice}">Lessons done. Practise now</button>`);
  }

  /* ---------- showing one thing at a time ---------- */
  const seen = new Set(store.get('seen', []));
  const tabIds = tabs.map(t => t.id);
  const ALIAS = { numbers: 'problems', assign: 'practice', comic: 'summary', 'real-life': 'summary', formulas: 'formulas' };
  function setHash(h) {
    const nh = h ? '#' + h : '';
    if (location.hash !== nh) { history.replaceState(null, '', location.pathname + location.search + nh); if (F.reportHash) F.reportHash(); }
  }
  /* a standalone page may have its own sticky top bar: the tabs stick just under it */
  const topbar = $('.topbar');
  const above = () => { if (!topbar) return 0; const cs = getComputedStyle(topbar); return cs.display !== 'none' && (cs.position === 'sticky' || cs.position === 'fixed') ? topbar.offsetHeight : 0; };
  const placeBar = () => { bar.style.top = above() + 'px'; };
  placeBar();
  window.addEventListener('resize', placeBar);
  function toTop() {
    const p = tabs.find(t => !t.p.hidden);
    const y = p ? p.p.getBoundingClientRect().top + window.scrollY - bar.offsetHeight - above() - 6 : 0;
    window.scrollTo({ top: Math.max(0, y), behavior: F.reduce ? 'auto' : 'smooth' });
  }
  const kick = () => { window.dispatchEvent(new Event('resize')); if (F.observe) F.observe(); };
  function showLesson(id) {
    lessons.forEach(L => { L.sec.hidden = L.id !== id; });
    seen.add(id); store.set('seen', [...seen]); store.set('lesson', id);
    lessons.forEach(L => { L.link.classList.toggle('on', L.id === id); L.link.classList.toggle('seen', seen.has(L.id)); });
    const on = lessons.find(L => L.id === id);
    if (on) drawNav(on);
    if (on) { const li = on.link.parentElement; ol.scrollLeft = Math.max(0, li.offsetLeft - ol.offsetLeft - (ol.clientWidth - li.offsetWidth) / 2); }
    kick();
  }
  function openTab(id, lessonId, scroll, quiet) {
    if (!tabIds.includes(id)) id = 'learn';
    tabs.forEach(t => { const on = t.id === id; t.b.classList.toggle('on', on); t.b.setAttribute('aria-selected', on); t.p.hidden = !on; });
    if (id === 'learn') {
      const lid = lessonIds.includes(lessonId) ? lessonId : (lessonIds.includes(store.get('lesson')) ? store.get('lesson') : lessonIds[0]);
      showLesson(lid);
      if (!quiet) setHash(lid);
    } else { if (!quiet) setHash(id); kick(); }
    if (scroll) toTop();
  }
  /* open whatever holds an element (a lesson or a tab) without scrolling */
  function reveal(el) {
    const L = lessons.find(x => x.sec.contains(el));
    const T = tabs.find(t => t.p.contains(el));
    if (!T || !T.p.hidden && (!L || !L.sec.hidden)) return;
    if (L) { tabs.forEach(t => { const on = t.id === 'learn'; t.b.classList.toggle('on', on); t.p.hidden = !on; }); showLesson(L.id); }
    else { tabs.forEach(t => { const on = t === T; t.b.classList.toggle('on', on); t.p.hidden = !on; }); kick(); }
  }
  /* the narrator and other scripts scroll to parts that may be hidden now, so open them first */
  const nativeScroll = Element.prototype.scrollIntoView;
  Element.prototype.scrollIntoView = function (...a) { try { reveal(this); } catch (e) { /* keep scrolling */ } return nativeScroll.apply(this, a); };

  /* arrows on both ends of the lesson row */
  const arrow = (dir, label) => {
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'ps-sarrow ' + dir; b.setAttribute('aria-label', label); b.hidden = true;
    b.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="' + (dir === 'left' ? 'M15 5l-7 7 7 7' : 'M9 5l7 7-7 7') + '" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    b.addEventListener('click', () => ol.scrollBy({ left: (dir === 'left' ? -1 : 1) * Math.max(160, ol.clientWidth * 0.7), behavior: F.reduce ? 'auto' : 'smooth' }));
    return b;
  };
  const lb = arrow('left', 'Show earlier lessons'), rb = arrow('right', 'Show more lessons');
  sw.insertBefore(lb, ol); sw.appendChild(rb);
  const paint = () => {
    const max = ol.scrollWidth - ol.clientWidth;
    lb.hidden = ol.scrollLeft <= 2; rb.hidden = ol.scrollLeft >= max - 2;
    sw.classList.toggle('fade-l', !lb.hidden); sw.classList.toggle('fade-r', !rb.hidden);
  };
  ol.addEventListener('scroll', paint, { passive: true });
  window.addEventListener('resize', paint);
  setTimeout(paint, 60);

  tabs.forEach(t => t.b.addEventListener('click', () => openTab(t.id, null, false)));
  document.addEventListener('click', e => {
    const s = e.target.closest('.ps-stepper a');
    if (s) { e.preventDefault(); showLesson(s.dataset.l); setHash(s.dataset.l); toTop(); return; }
    const g = e.target.closest('[data-go]');
    if (g && lessonIds.includes(g.dataset.go)) { openTab('learn', g.dataset.go, true); return; }
    const tg = e.target.closest('[data-tab-go]');
    if (tg) { openTab(tg.dataset.tabGo, null, true); return; }
    const a = e.target.closest('a[href^="#"]');
    if (a && !a.closest('.ps-stepper')) {
      const h = decodeURIComponent(a.getAttribute('href').slice(1));
      if (lessonIds.includes(h)) { e.preventDefault(); openTab('learn', h, true); return; }
      const id = tabIds.includes(h) ? h : ALIAS[h];
      if (id && tabIds.includes(id)) { e.preventDefault(); openTab(id, null, true); return; }
      const el = h && document.getElementById(h);
      if (el) reveal(el);
    }
  }, true);

  function route() {
    const h = decodeURIComponent(location.hash.slice(1));
    if (lessonIds.includes(h)) return openTab('learn', h);
    if (tabIds.includes(h)) return openTab(h);
    if (ALIAS[h] && tabIds.includes(ALIAS[h])) return openTab(ALIAS[h]);
    const el = h && document.getElementById(h);
    if (el && el !== document.body) { openTab('learn'); reveal(el); setTimeout(() => nativeScroll.call(el, { block: 'start' }), 80); return; }
    openTab('learn', null, false, true);  /* no hash yet: open the last lesson without touching the address */
  }
  window.addEventListener('hashchange', route);
  /* when a path switch hides the open lesson, open the first lesson that is still shown */
  const refilter = () => {
    const cur = lessons.find(L => !L.sec.hidden);
    if (!cur) return;
    if (filtered(cur)) { const first = lessons.find(L => !filtered(L)); if (first) showLesson(first.id); }
    else drawNav(cur);
  };
  new MutationObserver(refilter).observe(document.body, { attributes: true, attributeFilter: ['class'] });
  route();
  refilter();
})();
