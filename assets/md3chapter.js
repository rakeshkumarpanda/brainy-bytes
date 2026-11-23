/* ===== Material 3 layer for chapter pages =====
   Works on both chapter engines (pathskin.js with .ps-stepper and cv.js with .cv-stepper) without changing them:
     - the scrolling lesson strip on top becomes a lesson panel on the left (a menu button on a narrow screen)
     - inside subject.html the drawer shows the lessons instead, so the page hides its own panel while the
       portal says so ({lh:'tree', on}), and it reports its lessons to the portal ({lh:'lessons'})
     - every animation gets a full screen button, and a chapter opened on its own page gets one for the page.
       Both use the browser Fullscreen API, and Esc always leaves full screen.
   Lessons still open through the engines themselves: a click sets the address hash, which both engines follow. */
(() => {
  const html = document.documentElement;
  html.classList.add('md3ch');
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const icon = n => `<span class="msr" aria-hidden="true">${n}</span>`;
  const inFrame = (() => { try { return window.self !== window.top; } catch (e) { return true; } })();
  const post = m => { if (inFrame) { try { parent.postMessage(m, '*'); } catch (e) { /* no parent */ } } };
  const fsOK = !!(document.fullscreenEnabled && html.requestFullscreen);

  window.addEventListener('message', e => {
    const d = e.data || {};
    if (d.lh === 'tree') html.classList.toggle('md-tree-on', !!d.on);
  });

  /* ---------- full screen ---------- */
  function fsButton(target, label) {
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'md-fsb';
    b.title = label + ' (Esc to leave)'; b.setAttribute('aria-label', label);
    b.innerHTML = icon('fullscreen');
    b.addEventListener('click', e => {
      e.stopPropagation();
      if (document.fullscreenElement) { document.exitFullscreen(); return; }
      /* remember the size on the page, so the animation can be scaled up to fill the screen */
      const w = target.offsetWidth, h = target.offsetHeight;
      target.requestFullscreen().then(() => {
        const k = Math.max(1, Math.min((innerWidth - 48) / Math.max(1, w), (innerHeight - 48) / Math.max(1, h), 2.2));
        target.style.setProperty('--md-fsz', k.toFixed(3));
        window.dispatchEvent(new Event('resize'));
      }).catch(() => { /* the browser refused */ });
    });
    return b;
  }
  document.addEventListener('fullscreenchange', () => {
    const el = document.fullscreenElement;
    $$('.md-fsb').forEach(b => { b.innerHTML = icon(b.parentElement === el || (el === html && b.classList.contains('md-pagefs')) ? 'fullscreen_exit' : 'fullscreen'); });
    if (!el) $$('.md-fsel').forEach(x => x.style.removeProperty('--md-fsz'));
    setTimeout(() => window.dispatchEvent(new Event('resize')), 60);
  });
  /* the animation roots of every widget library on the site */
  const ANIM = ['.vz', '.cj-card', '[data-viz]:has(> .z-head)'];
  function addAnimButtons(root = document) {
    if (!fsOK) return;
    ANIM.forEach(sel => {
      let list;
      try { list = $$(sel, root); } catch (e) { return; }  /* a browser without :has() skips that selector */
      list.forEach(el => {
        if (el.classList.contains('md-fsel') || el.closest('.md-fsel')) return;
        el.classList.add('md-fsel');
        el.appendChild(fsButton(el, 'Show this animation full screen'));
      });
    });
  }
  let pend = 0;
  new MutationObserver(() => { if (!pend) pend = requestAnimationFrame(() => { pend = 0; addAnimButtons(); }); })
    .observe(document.body || html, { childList: true, subtree: true });

  /* ---------- the lesson panel ---------- */
  function buildLessons() {
    const strip = $('.ps-stepper, .cv-stepper');
    if (!strip) return;
    const links = $$('a[data-l]', strip);
    if (!links.length) return;
    const pane = strip.closest('.ps-pane, .cv-pane') || strip.parentElement;
    const tabsEl = $('.ps-tabs, .cv-tabs');
    const tabBtns = () => $$('.ps-tab, .cv-tab');
    const lessons = links.map(a => ({ id: a.dataset.l, t: ($('.t', a) || a).textContent.trim(), a }));

    /* the grid: lesson panel on the left, the lesson on the right */
    const grid = document.createElement('div');
    grid.className = 'md-chgrid';
    const rail = document.createElement('aside');
    rail.className = 'md-lrail';
    rail.setAttribute('aria-label', 'Lessons of this chapter');
    const body = document.createElement('div');
    body.className = 'md-chbody';
    const menu = document.createElement('div');
    menu.className = 'md-lmenu';
    menu.innerHTML = `<button type="button" aria-expanded="false">${icon('list')}<span class="t"></span>${icon('expand_more')}</button><aside class="md-lrail" aria-label="Lessons of this chapter"></aside>`;
    while (pane.firstChild) body.appendChild(pane.firstChild);
    grid.append(rail, body);
    pane.append(grid);
    body.prepend(menu);

    const listHtml = () => `<h4>Lessons</h4><ol>${lessons.map((L, i) => `<li><a href="#${esc(L.id)}" data-md-l="${esc(L.id)}" class="${L.a.classList.contains('on') ? 'on' : ''}${L.a.classList.contains('seen') ? ' seen' : ''}"><span class="n">${i + 1}</span><span>${esc(L.t)}</span></a></li>`).join('')}</ol>`;
    const menuRail = $('.md-lrail', menu), menuBtn = $(':scope > button', menu);
    function paint() {
      rail.innerHTML = listHtml();
      menuRail.innerHTML = listHtml();
      const i = lessons.findIndex(L => L.a.classList.contains('on'));
      $('.t', menuBtn).textContent = i >= 0 ? `Lesson ${i + 1} of ${lessons.length}: ${lessons[i].t}` : `${lessons.length} lessons`;
      const on = $('a.on', rail);
      if (on && rail.scrollHeight > rail.clientHeight) { const r = on.offsetTop - rail.clientHeight / 2; rail.scrollTop = Math.max(0, r); }
      if (tabsEl) html.style.setProperty('--md-tabs-h', tabsEl.offsetHeight + 'px');
      post({
        lh: 'lessons',
        items: lessons.map(L => ({ id: L.id, t: L.t, on: L.a.classList.contains('on') && !pane.hidden, seen: L.a.classList.contains('seen') })),
        tabs: tabBtns().map(b => ({ id: b.dataset.tab, t: b.childNodes[0] ? b.childNodes[0].textContent.trim() : b.textContent.trim(), on: b.classList.contains('on') }))
      });
    }
    let pp = 0;
    const later = () => { if (!pp) pp = requestAnimationFrame(() => { pp = 0; paint(); }); };
    new MutationObserver(later).observe(strip, { attributes: true, subtree: true, attributeFilter: ['class'] });
    if (tabsEl) new MutationObserver(later).observe(tabsEl, { attributes: true, subtree: true, attributeFilter: ['class'] });
    new MutationObserver(later).observe(pane, { attributes: true, attributeFilter: ['hidden'] });
    addEventListener('resize', later);

    const toTop = () => {
      const y = pane.getBoundingClientRect().top + scrollY - (tabsEl ? tabsEl.offsetHeight : 0) - 6;
      scrollTo({ top: Math.max(0, y), behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    };
    grid.addEventListener('click', e => {
      const a = e.target.closest('[data-md-l]');
      if (a) {
        e.preventDefault(); e.stopPropagation();
        menu.classList.remove('open'); menuBtn.setAttribute('aria-expanded', 'false');
        const h = '#' + a.dataset.mdL;
        if (location.hash !== h) location.hash = h; else { const L = lessons.find(x => x.id === a.dataset.mdL); if (L) L.a.click(); }
        setTimeout(toTop, 30);
        return;
      }
      if (e.target.closest('.md-lmenu > button')) {
        const open = menu.classList.toggle('open');
        menuBtn.setAttribute('aria-expanded', open);
      }
    }, true);
    paint();
    setTimeout(paint, 300);
  }

  /* ---------- the standalone page gets a full screen button for the whole chapter ---------- */
  function pageButton() {
    if (inFrame || !fsOK) return;
    const b = fsButton(html, 'Show this chapter full screen');
    b.classList.add('md-pagefs');
    b.style.position = 'fixed';
    document.body.appendChild(b);
  }

  /* the engines build their tabs while the page loads, so start once they are done */
  function start() {
    try { buildLessons(); } catch (e) { console.warn('Lesson panel', e); }
    addAnimButtons();
    pageButton();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => setTimeout(start, 0));
  else setTimeout(start, 0);
})();
