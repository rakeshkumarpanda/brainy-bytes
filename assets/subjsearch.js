/* ===== Search inside one subject =====
   The subject page gets a "Search in <subject>" button. It looks through the
   words written inside every chapter of that subject, using the small file
   data/search/<subject>.js made by tools/search-build/build.js.
   The file loads only when the learner first opens the search (or hovers the
   button), so the subject page itself stays as fast as before.
   Picking a result opens the chapter at that part and marks the word on the page. */
(() => {
  const subjId = new URLSearchParams(location.search).get('s');
  const btn = document.querySelector('[data-subjsearch]');
  if (!subjId || !btn) return;
  const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const reEsc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const lc = s => String(s ?? '').toLowerCase();

  /* ----- loading the files, each one only once ----- */
  const loadScript = src => new Promise((res, rej) => {
    const s = document.createElement('script');
    s.src = src; s.async = true;
    s.onload = res; s.onerror = () => rej(new Error('Could not load ' + src));
    document.head.appendChild(s);
  });
  let manifestP = null, indexP = null, IDX = null;
  const loadManifest = () => manifestP || (manifestP = loadScript('data/search/manifest.js?t=' + Math.floor(Date.now() / 60000))
    .then(() => window.LH_SEARCH_MANIFEST || {}).catch(() => ({})));
  function loadIndex() {
    if (indexP) return indexP;
    indexP = loadManifest().then(m => {
      if (!m[subjId]) throw new Error('This subject has no search file yet.');
      return loadScript(`data/search/${encodeURIComponent(subjId)}.js?v=${m[subjId]}`);
    }).then(() => {
      const d = (window.LH_SEARCH || {})[subjId];
      if (!d) throw new Error('The search file did not load.');
      /* prepare once: lower case copies for matching */
      d.c.forEach(c => { c.lt = lc(c[2]); c.lx = lc(c[3]); c.ltt = lc(d.t[c[0]][1]); });
      IDX = d;
      return d;
    });
    indexP.catch(() => { indexP = null; });
    return indexP;
  }

  /* show the button only when this subject has a search file */
  const idle = window.requestIdleCallback || (f => setTimeout(f, 400));
  idle(() => loadManifest().then(m => {
    if (m[subjId]) btn.hidden = false;
    let tries = 0;
    (function retry() { label(); if (!subjInfo().title && ++tries < 20) setTimeout(retry, 300); })();
  }));
  btn.addEventListener('pointerenter', () => { loadIndex().catch(() => {}); }, { once: true });
  btn.addEventListener('focus', () => { loadIndex().catch(() => {}); }, { once: true });

  /* ----- matching ----- */
  function parse(q) {
    const phrases = [];
    q = q.replace(/"([^"]+)"/g, (m, p) => { if (p.trim()) phrases.push(lc(p.trim())); return ' '; });
    const words = lc(q).split(/[^a-z0-9+#._$@-]+/).map(w => w.replace(/^[.\-_]+|[.\-_]+$/g, '')).filter(w => w.length > 0);
    return { terms: [...phrases, ...words], phrases };
  }
  const countOf = (hay, term, cap) => { let n = 0, i = hay.indexOf(term); while (i !== -1 && n < cap) { n++; i = hay.indexOf(term, i + term.length); } return n; };
  function run(q) {
    const { terms } = parse(q);
    if (!terms.length || !IDX) return [];
    const whole = lc(q.replace(/"/g, '').trim());
    const wordRe = terms.map(t => new RegExp('(^|[^a-z0-9])' + reEsc(t) + '($|[^a-z0-9])'));
    const out = [];
    for (const c of IDX.c) {
      let score = 0, ok = true;
      for (let k = 0; k < terms.length; k++) {
        const t = terms[k];
        const inT = c.lt.includes(t), inTT = c.ltt.includes(t);
        const n = countOf(c.lx, t, 6);
        if (!inT && !inTT && !n) { ok = false; break; }
        if (inT) score += 14 + (wordRe[k].test(c.lt) ? 6 : 0);
        if (inTT) score += 5;
        score += n * 2;
        if (n && wordRe[k].test(c.lx)) score += 3;
      }
      if (!ok) continue;
      if (terms.length > 1 && (c.lt.includes(whole) || c.lx.includes(whole))) score += 12;
      if (c.lt === whole) score += 20;
      if (!c[1] && !c[2]) score += 4; /* the chapter itself */
      out.push({ c, score });
    }
    out.sort((a, b) => b.score - a.score);
    /* one row per place: parts of the same long section collapse into the best one */
    const seen = new Set();
    return out.filter(r => { const k = r.c[0] + '|' + r.c[1] + '|' + r.c[2]; if (seen.has(k)) return false; seen.add(k); return true; });
  }
  /* a close spelling when nothing matches, such as "recusion" for "recursion" */
  let WORDS = null;
  function lev(a, b, max) {
    if (Math.abs(a.length - b.length) > max) return max + 1;
    let prev = Array.from({ length: b.length + 1 }, (_, j) => j);
    for (let i = 1; i <= a.length; i++) {
      const cur = [i];
      let best = i;
      for (let j = 1; j <= b.length; j++) {
        cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
        if (cur[j] < best) best = cur[j];
      }
      if (best > max) return max + 1;
      prev = cur;
    }
    return prev[b.length];
  }
  function suggest(q) {
    if (!WORDS) {
      const f = new Map();
      for (const c of IDX.c) for (const w of (c.lt + ' ' + c.lx).split(/[^a-z0-9]+/)) if (w.length > 2 && w.length < 24) f.set(w, (f.get(w) || 0) + 1);
      WORDS = [...f.entries()];
    }
    const { terms } = parse(q);
    let changed = false;
    const fixed = terms.map(t => {
      if (t.length < 4 || t.includes(' ') || WORDS.some(([w]) => w === t)) return t;
      const max = t.length > 7 ? 2 : 1;
      let best = null;
      for (const [w, n] of WORDS) {
        const d = lev(t, w, max);
        if (d <= max && (!best || d < best.d || (d === best.d && n > best.n))) best = { w, d, n };
      }
      if (best) { changed = true; return best.w; }
      return t;
    });
    return changed ? fixed.join(' ') : '';
  }

  /* ----- drawing the results ----- */
  function hl(text, terms) {
    let h = esc(text);
    const ts = [...new Set(terms)].filter(Boolean).sort((a, b) => b.length - a.length);
    if (!ts.length) return h;
    const re = new RegExp('(' + ts.map(t => reEsc(esc(t))).join('|') + ')', 'gi');
    return h.replace(/(&[a-z]+;)|([^&]+)/g, (m, ent, txt) => ent || txt.replace(re, '<mark>$1</mark>'));
  }
  function snippet(c, terms) {
    const text = c[3];
    let at = -1;
    for (const t of terms) { const i = c.lx.indexOf(t); if (i !== -1 && (at === -1 || i < at)) at = i; }
    if (at === -1) return text.length > 170 ? text.slice(0, 168).replace(/\s+\S*$/, '') + '…' : text;
    let a = Math.max(0, at - 70), b = Math.min(text.length, at + 150);
    if (a > 0) { const sp = text.indexOf(' ', a); if (sp !== -1 && sp < at) a = sp + 1; }
    if (b < text.length) { const sp = text.lastIndexOf(' ', b); if (sp > at) b = sp; }
    return (a > 0 ? '…' : '') + text.slice(a, b) + (b < text.length ? '…' : '');
  }
  const topicUrl = (tid, anchor) => `subject.html?s=${encodeURIComponent(subjId)}&t=${encodeURIComponent(tid)}${anchor ? '#' + encodeURIComponent(anchor) : ''}`;

  let modal, inp, box, chips, foot, sel = 0, lastQ = '', lastRes = [], topicFilter = -1, shown = 60;
  /* the subject name and example words come from the catalog that the page already loaded */
  const subjInfo = () => ((window.CATALOG && window.CATALOG.subjects) || []).find(s => s.id === subjId) || {};
  let subjTitle = 'this subject';
  function label() {
    const s = subjInfo();
    if (!s.title) return;
    subjTitle = s.title;
    btn.title = `Search any word inside the ${s.title} chapters (press /)`;
    btn.querySelector('.lbl').textContent = 'Search in ' + s.title;
  }
  function build() {
    label();
    modal = document.createElement('div');
    modal.className = 'smodal ssmodal';
    modal.innerHTML = `<div class="sbox" role="dialog" aria-modal="true" aria-label="Search in ${esc(subjTitle)}">
      <div class="sinput"><span>🔎</span><input type="search" placeholder="Search any word in ${esc(subjTitle)}…" aria-label="Search in ${esc(subjTitle)}" autocomplete="off" spellcheck="false"><button class="ibtn" data-close>Esc</button></div>
      <div class="ss-chips" hidden></div>
      <div class="sresults" aria-live="polite"></div>
      <div class="sfoot"><span>↑ ↓ to move</span><span>Enter to open</span><span>"Quotes" find an exact phrase</span><a href="#" class="ss-all" data-all>🌐 Search every subject</a></div></div>`;
    document.body.appendChild(modal);
    inp = modal.querySelector('input'); box = modal.querySelector('.sresults'); chips = modal.querySelector('.ss-chips'); foot = modal.querySelector('.sfoot');
    let timer = 0;
    inp.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(() => { topicFilter = -1; render(); }, 90); });
    inp.addEventListener('keydown', e => {
      const items = [...box.querySelectorAll('.sres')];
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        if (!items.length) return;
        sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
        items.forEach((x, k) => x.classList.toggle('act', k === sel));
        items[sel].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter') {
        clearTimeout(timer);
        if (inp.value !== lastQ) render();
        const a = box.querySelectorAll('.sres')[sel];
        if (a) { e.preventDefault(); go(a); }
      } else if (e.key === 'Escape') { e.preventDefault(); close(); }
    });
    modal.addEventListener('click', e => {
      if (e.target === modal || e.target.closest('[data-close]')) { close(); return; }
      if (e.target.closest('[data-all]')) { e.preventDefault(); const q = inp.value; close(); if (window.LH) LH.openSearch(q); return; }
      const chip = e.target.closest('.ss-chip');
      if (chip) { topicFilter = +chip.dataset.ti; shown = 60; draw(); return; }
      const qc = e.target.closest('.qchip');
      if (qc) { inp.value = qc.dataset.q; render(); inp.focus(); return; }
      if (e.target.closest('[data-more]')) { shown += 60; draw(); return; }
      const row = e.target.closest('.sres');
      if (row && !(e.target.closest('a') && (e.ctrlKey || e.metaKey || e.shiftKey || e.button === 1))) { e.preventDefault(); go(row); }
    });
  }
  function hint(html) { chips.hidden = true; box.innerHTML = `<div class="shint">${html}</div>`; }
  function render() {
    const q = inp.value;
    lastQ = q; sel = 0; shown = 60;
    if (!IDX) {
      hint('<div class="dots" style="justify-content:flex-start"><i></i><i></i><i></i></div> Getting the search ready…');
      loadIndex().then(() => { if (modal.classList.contains('open')) render(); }).catch(err => hint(`<b>Search is not ready for this subject.</b> ${esc(err.message)} You can still <a href="#" data-all>search every subject</a>.`));
      return;
    }
    if (!q.trim()) {
      const ex = (subjInfo().tags || []).slice(0, 10);
      hint(`<b>Type any word or phrase.</b> Search looks inside every chapter of ${esc(subjTitle)}: the explanations, examples, code and questions. ${IDX.t.length} chapters are searchable.
        ${ex.length ? `<div class="chiprow">${ex.map(s => `<button class="qchip" data-q="${esc(s)}">${esc(s)}</button>`).join('')}</div>` : ''}`);
      return;
    }
    const t0 = performance.now();
    lastRes = run(q);
    lastRes.ms = performance.now() - t0;
    if (!lastRes.length) {
      const s = suggest(q);
      hint(`<b>No match for “${esc(q)}” in ${esc(subjTitle)}.</b> ${s ? `Did you mean <button class="qchip" data-q="${esc(s)}">${esc(s)}</button>` : 'Try a shorter word, or a different spelling.'}
        <div style="margin-top:10px"><a href="#" data-all>🌐 Look for “${esc(q)}” in every subject</a></div>`);
      return;
    }
    draw();
  }
  function draw() {
    const { terms } = parse(lastQ);
    /* chapter chips: how many hits each chapter has, click to keep only that chapter */
    const per = new Map();
    for (const r of lastRes) per.set(r.c[0], (per.get(r.c[0]) || 0) + 1);
    const tops = [...per.entries()].sort((a, b) => b[1] - a[1]);
    if (tops.length > 1) {
      chips.hidden = false;
      chips.innerHTML = `<button class="ss-chip${topicFilter === -1 ? ' on' : ''}" data-ti="-1">All chapters <span class="cnt">${lastRes.length}</span></button>` +
        tops.slice(0, 14).map(([ti, n]) => `<button class="ss-chip${topicFilter === ti ? ' on' : ''}" data-ti="${ti}" title="${esc(IDX.t[ti][1])}">${esc(IDX.t[ti][2])} ${esc(IDX.t[ti][1].length > 28 ? IDX.t[ti][1].slice(0, 26) + '…' : IDX.t[ti][1])} <span class="cnt">${n}</span></button>`).join('');
    } else chips.hidden = true;
    const list = topicFilter === -1 ? lastRes : lastRes.filter(r => r.c[0] === topicFilter);
    const head = `<div class="sgroup">${list.length} place${list.length === 1 ? '' : 's'} in ${topicFilter === -1 ? `${per.size} chapter${per.size === 1 ? '' : 's'}` : 'this chapter'} · ${lastRes.ms < 1 ? 'under 1' : Math.round(lastRes.ms)} ms</div>`;
    box.innerHTML = head + list.slice(0, shown).map((r, i) => {
      const c = r.c, tp = IDX.t[c[0]];
      const url = topicUrl(tp[0], c[1]);
      return `<a class="sres${i === sel ? ' act' : ''}" href="${esc(url)}" data-ti="${c[0]}" data-a="${esc(c[1])}">
        <div class="t"><span class="em">${esc(tp[2])}</span><span class="tl">${hl(c[2] || tp[1], terms)}</span>${c[2] ? '' : '<span class="kind">Chapter</span>'}</div>
        ${c[2] ? `<div class="crumbs"><span class="lead">In:</span><span class="ss-tp">${hl(tp[1], terms)}</span></div>` : ''}
        <div class="snip">${hl(snippet(c, terms), terms)}</div></a>`;
    }).join('') + (list.length > shown ? `<button class="ibtn ss-more" data-more>Show ${Math.min(60, list.length - shown)} more</button>` : '');
    box.scrollTop = 0;
  }

  /* ----- opening a result: the subject page shows the chapter, then the word is marked inside it ----- */
  function go(row) {
    const ti = +row.dataset.ti, anchor = row.dataset.a, tp = IDX.t[ti];
    const { terms } = parse(lastQ);
    close();
    history.pushState(null, '', topicUrl(tp[0], anchor));
    window.dispatchEvent(new PopStateEvent('popstate'));
    const fr = document.getElementById('frame');
    if (fr) fr.addEventListener('load', () => setTimeout(() => markInFrame(fr, terms, anchor), 350), { once: true });
  }
  function markInFrame(fr, terms, anchor) {
    let doc;
    try { doc = fr.contentDocument; if (!doc || !doc.body) return; } catch (e) { return; } /* opened from a file, the browser blocks this */
    doc.querySelectorAll('mark.lh-hit').forEach(m => m.replaceWith(...m.childNodes));
    const ts = terms.filter(t => t.length > 1).sort((a, b) => b.length - a.length);
    if (!ts.length) return;
    const re = new RegExp(ts.map(reEsc).join('|'), 'i');
    const start = anchor ? doc.getElementById(anchor) : null;
    const SKIP = /^(SCRIPT|STYLE|NOSCRIPT|TEXTAREA|BUTTON|OPTION|SELECT)$/;
    const visible = el => !!(el.offsetParent || el.getClientRects().length);
    const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, {
      acceptNode: n => (n.parentElement && !SKIP.test(n.parentElement.tagName) && re.test(n.nodeValue)) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT
    });
    let first = null, firstAfter = null, n;
    while ((n = walker.nextNode())) {
      if (!visible(n.parentElement)) continue;
      if (!first) first = n;
      if (!start || start.contains(n) || (start.compareDocumentPosition(n) & 4)) { firstAfter = n; break; }
    }
    const node = firstAfter || first;
    if (!node) return;
    const m = re.exec(node.nodeValue);
    const range = doc.createRange();
    range.setStart(node, m.index); range.setEnd(node, m.index + m[0].length);
    const mark = doc.createElement('mark');
    mark.className = 'lh-hit';
    mark.style.cssText = 'background:#ffd84d;color:#111;border-radius:4px;padding:0 2px;box-shadow:0 0 0 3px rgba(255,201,40,.55);transition:box-shadow 1.2s';
    range.surroundContents(mark);
    mark.scrollIntoView({ block: 'center', behavior: 'smooth' });
    setTimeout(() => { mark.style.boxShadow = 'none'; }, 2200);
  }

  function open() {
    if (!modal) build();
    if (window.LH) LH.closeSearch();
    modal.classList.add('open');
    render();
    setTimeout(() => { inp.focus(); inp.select(); }, 30);
  }
  function close() { if (modal) modal.classList.remove('open'); }

  btn.addEventListener('click', open);
  /* "/" opens this subject's search. Ctrl K still searches every subject. */
  window.addEventListener('keydown', e => {
    const typing = /INPUT|TEXTAREA|SELECT/.test((document.activeElement || {}).tagName || '') || (document.activeElement && document.activeElement.isContentEditable);
    if (e.key === '/' && !typing && !e.ctrlKey && !e.metaKey && !btn.hidden) { e.preventDefault(); e.stopPropagation(); open(); }
    else if (e.key === 'Escape' && modal && modal.classList.contains('open')) close();
  }, true);
})();
