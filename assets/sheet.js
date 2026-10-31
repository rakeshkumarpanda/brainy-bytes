/* ===== Subject cheatsheet page: search, show or hide parts, exam favourites, print, theme and links in the app =====
   The page is written by tools/cv-build/cheatsheet.py. Every item carries data-kind (must, fx, table, tip, warn, exam)
   and data-find (its plain text in lower case), so filtering never has to read the formulas themselves. */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const subject = document.body.dataset.subject;
  const KEY = 'sheet-' + subject + '-';
  const store = {
    get(k, d) { try { const v = localStorage.getItem(KEY + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(KEY + k, JSON.stringify(v)); } catch (e) { /* storage unavailable */ } }
  };

  /* theme button on the standalone page */
  const tb = $('#cvTheme');
  const paintTheme = () => { if (tb) tb.textContent = FUN.currentTheme() === 'dark' ? 'Light mode' : 'Dark mode'; };
  if (tb) tb.onclick = () => { FUN.toggleTheme(); paintTheme(); };
  paintTheme();

  /* inside the app, chapter links open the chapter in the app rather than inside this frame */
  if (FUN.inFrame) $$('a[data-topic]').forEach(a => {
    a.href = '../../subject.html?s=' + subject + '&t=' + a.dataset.topic + (a.dataset.h ? '#' + a.dataset.h : '');
    a.target = '_top';
  });

  /* filters */
  const items = $$('.sh-it'), blocks = $$('.sh-blk'), chs = $$('.sh-ch'), steps = $$('.sh-step');
  const kindBtns = $$('.sh-k'), find = $('#shFind'), fav = $('#shFav'), count = $('#shCount'), none = $('#shNone');
  const off = new Set(store.get('off', []));
  fav.checked = !!store.get('fav', false);

  function apply() {
    const words = find.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let shown = 0;
    kindBtns.forEach(b => b.setAttribute('aria-pressed', !off.has(b.dataset.k)));
    items.forEach(it => {
      const k = it.dataset.kind;
      let ok = !off.has(k) && words.every(w => it.dataset.find.includes(w));
      if (ok && fav.checked && k === 'fx') ok = it.dataset.key === '1';
      it.hidden = !ok;
      if (ok) shown++;
    });
    blocks.forEach(b => { b.hidden = !b.querySelector('.sh-it:not([hidden])'); });
    chs.forEach(c => { c.hidden = !c.querySelector('.sh-blk:not([hidden])'); });
    steps.forEach(s => { s.hidden = !s.querySelector('.sh-ch:not([hidden])'); });
    if (words.length) $$('details.sh-it:not([hidden])').forEach(d => { d.open = true; });
    count.textContent = shown === items.length ? `Showing all ${shown} items` : `Showing ${shown} of ${items.length} items`;
    none.hidden = shown > 0;
  }
  kindBtns.forEach(b => b.addEventListener('click', () => {
    const k = b.dataset.k;
    if (off.has(k)) off.delete(k); else off.add(k);
    store.set('off', [...off]);
    apply();
  }));
  let t = 0;
  find.addEventListener('input', () => { clearTimeout(t); t = setTimeout(apply, 120); });
  fav.addEventListener('change', () => { store.set('fav', fav.checked); apply(); });
  apply();

  /* print what is shown: light colours and every table open, then put things back */
  let saved = null;
  window.addEventListener('beforeprint', () => {
    saved = { theme: document.documentElement.dataset.theme, closed: $$('details.sh-it:not([open])') };
    document.documentElement.dataset.theme = 'light';
    saved.closed.forEach(d => { d.open = true; });
  });
  window.addEventListener('afterprint', () => {
    if (!saved) return;
    if (saved.theme) document.documentElement.dataset.theme = saved.theme; else delete document.documentElement.dataset.theme;
    saved.closed.forEach(d => { d.open = false; });
    saved = null;
  });
  $('#shPrint').addEventListener('click', () => window.print());

  /* keep chapter headings clear of the sticky search bar when jumping to them */
  const bar = $('.sh-bar');
  const barH = () => document.documentElement.style.setProperty('--shbar', bar.offsetHeight + 'px');
  barH();
  window.addEventListener('resize', barH);

  /* a link to #<chapter slug> or #step-N scrolls there after the page is drawn */
  if (location.hash) {
    const el = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    const go = () => el.scrollIntoView({ block: 'start', behavior: 'instant' });
    if (el) { setTimeout(go, 60); if (document.fonts) document.fonts.ready.then(() => setTimeout(go, 30)); }
  }
})();
