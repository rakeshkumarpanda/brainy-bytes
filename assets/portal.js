/* ===== Portal core: loads the catalog, checks it, builds the universal search, shared header bits ===== */
const LH = (() => {
  const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const norm = s => String(s ?? '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');

  /* Load data/catalog.js fresh every time, so an edit shows up on the next page load. */
  function loadCatalog() {
    return new Promise((resolve, reject) => {
      if (window.CATALOG) { resolve(prepare(window.CATALOG)); return; }
      const s = document.createElement('script');
      s.src = 'data/catalog.js?v=' + Date.now();
      s.onload = () => (window.CATALOG ? resolve(prepare(window.CATALOG)) : reject(new Error('data/catalog.js loaded but did not set window.CATALOG')));
      s.onerror = () => reject(new Error('Could not load data/catalog.js'));
      document.head.appendChild(s);
    });
  }

  /* Fill in defaults and links between levels, and collect friendly warnings about mistakes in the catalog. */
  function prepare(cat) {
    const warnings = [];
    cat.site = Object.assign({ name: 'Learning Hub', tagline: '', jokes: [] }, cat.site || {});
    cat.subjects = Array.isArray(cat.subjects) ? cat.subjects : [];
    const sids = new Set();
    cat.subjects.forEach((s, si) => {
      if (!s.id) { s.id = 'subject-' + (si + 1); warnings.push(`Subject number ${si + 1} has no id.`); }
      if (sids.has(s.id)) warnings.push(`Two subjects use the id "${s.id}". Each id must be unique.`);
      sids.add(s.id);
      if (!s.title) warnings.push(`Subject "${s.id}" has no title.`);
      s.modules = Array.isArray(s.modules) ? s.modules : [];
      s.emoji = s.emoji || '📘';
      const tids = new Set();
      s.modules.forEach((m, mi) => {
        m.id = m.id || 'module-' + (mi + 1);
        m.subject = s;
        m.topics = Array.isArray(m.topics) ? m.topics : [];
        m.topics.forEach((t, ti) => {
          if (!t.id) { t.id = m.id + '-' + (ti + 1); warnings.push(`A topic in "${s.title}" / "${m.title}" has no id.`); }
          if (tids.has(t.id)) warnings.push(`Two topics in "${s.title}" use the id "${t.id}".`);
          tids.add(t.id);
          if (!t.title) warnings.push(`Topic "${t.id}" in "${s.title}" has no title.`);
          t.subject = s; t.module = m;
          t.emoji = t.emoji || '📄';
          t.soon = !!t.soon || !t.page;
          t.sections = Array.isArray(t.sections) ? t.sections : [];
          t.sections.forEach(sec => { sec.topic = t; sec.items = Array.isArray(sec.items) ? sec.items : []; });
        });
      });
      s.topics = s.modules.flatMap(m => m.topics);
      s.liveTopics = s.topics.filter(t => !t.soon);
      s.soon = !s.page && s.liveTopics.length === 0;
    });
    cat.warnings = warnings;
    return cat;
  }

  /* links */
  const subjectUrl = s => `subject.html?s=${encodeURIComponent(s.id)}`;
  const moduleUrl = m => `${subjectUrl(m.subject)}&m=${encodeURIComponent(m.id)}`;
  const topicUrl = t => `${subjectUrl(t.subject)}&t=${encodeURIComponent(t.id)}`;
  const sectionUrl = (t, anchor) => `${topicUrl(t)}#${encodeURIComponent(anchor).replace(/%2F/g, '/')}`;

  /* ===== universal search ===== */
  let INDEX = [];
  function buildIndex(cat) {
    INDEX = [];
    const add = (e) => { e.hay = norm([e.title, ...(e.keywords || []), e.summary || '', ...e.path.map(p => p.label)].join(' | ')); e.ntitle = norm(e.title); INDEX.push(e); };
    for (const s of cat.subjects) {
      const sp = [{ label: s.title, url: subjectUrl(s) }];
      add({ kind: 'Subject', emoji: s.emoji, title: s.title, url: subjectUrl(s), path: [], keywords: s.tags || [], summary: s.blurb, soon: s.soon });
      for (const m of s.modules) {
        const mp = [...sp, { label: m.title, url: moduleUrl(m) }];
        add({ kind: 'Module', emoji: m.emoji || '🗂️', title: m.title, url: moduleUrl(m), path: sp, keywords: m.keywords || [], summary: m.blurb });
        for (const t of m.topics) {
          const tp = [...mp, { label: t.title, url: topicUrl(t) }];
          add({ kind: 'Topic', emoji: t.emoji, title: t.title, url: topicUrl(t), path: mp, keywords: t.keywords || [], summary: t.summary, soon: t.soon });
          for (const sec of t.sections) {
            const su = sectionUrl(t, sec.id);
            const secPath = sec.group ? [...tp, { label: sec.group, url: su }] : tp;
            add({ kind: sec.kind || 'Section', emoji: sec.emoji || t.emoji, title: sec.title, url: su, path: secPath, keywords: sec.keywords || [], summary: sec.summary });
            for (const it of sec.items) {
              add({ kind: it.kind || 'Item', emoji: it.emoji || '🎯', title: it.title, url: sectionUrl(t, it.id), path: [...secPath, { label: sec.title, url: su }], keywords: it.keywords || [], summary: it.summary, level: it.level });
            }
          }
        }
      }
    }
    return INDEX;
  }

  function lev1(a, b) { // true when a and b differ by at most one edit
    if (Math.abs(a.length - b.length) > 1) return false;
    let i = 0, j = 0, e = 0;
    while (i < a.length && j < b.length) {
      if (a[i] === b[j]) { i++; j++; continue; }
      if (++e > 1) return false;
      if (a.length > b.length) i++; else if (b.length > a.length) j++; else { i++; j++; }
    }
    return e + (a.length - i) + (b.length - j) <= 1;
  }
  const KIND_W = { Subject: 30, Module: 18, Topic: 26, Section: 14, Practice: 8, Item: 6 };
  function search(q, limit = 60) {
    const terms = norm(q).split(/[^a-z0-9+#.]+/).filter(Boolean);
    if (!terms.length) return [];
    const out = [];
    for (const e of INDEX) {
      let score = 0, ok = true;
      const hits = [];
      for (const term of terms) {
        if (e.hay.includes(term)) {
          hits.push(term);
          score += e.ntitle.includes(term) ? 10 : 3;
          if (e.ntitle.startsWith(term)) score += 6;
          if (new RegExp('\\b' + term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).test(e.ntitle)) score += 3;
        } else if (term.length >= 4) {
          const w = e.hay.split(/[^a-z0-9]+/).find(x => x.length >= 3 && lev1(x, term));
          if (w) { hits.push(w); score += 2; } else { ok = false; break; }
        } else { ok = false; break; }
      }
      if (!ok) continue;
      if (e.ntitle === norm(q).trim()) score += 25;
      score += KIND_W[e.kind] || 5;
      if (e.soon) score -= 8;
      out.push({ e, score, hits });
    }
    out.sort((a, b) => b.score - a.score || a.e.title.length - b.e.title.length);
    return out.slice(0, limit);
  }
  function hl(text, hits) {
    let h = esc(text);
    const ts = [...new Set(hits)].filter(t => t.length > 1).sort((a, b) => b.length - a.length);
    if (!ts.length) return h;
    const re = new RegExp('(' + ts.map(t => esc(t).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')', 'gi');
    return h.replace(/(<[^>]*>)|([^<]+)/g, (m, tag, txt) => tag || txt.replace(re, '<mark>$1</mark>'));
  }
  function resultHtml(r, i, target) {
    const e = r.e;
    const tgt = target ? ` target="${target}" rel="noopener"` : '';
    const crumbs = e.path.length ? `<div class="crumbs"><span class="lead">Path:</span>${e.path.map(p => `<a href="${esc(p.url)}"${tgt}>${hl(p.label, r.hits)}</a>`).join('<i>›</i>')}<i>›</i><a href="${esc(e.url)}"${tgt}><b>${hl(e.title, r.hits)}</b></a></div>` : '';
    const kw = (e.keywords || []).filter(k => r.hits.some(h => norm(k).includes(h))).slice(0, 4);
    const snip = e.summary ? hl(e.summary.length > 150 ? e.summary.slice(0, 148) + '…' : e.summary, r.hits) : (kw.length ? 'Matches: ' + kw.map(k => hl(k, r.hits)).join(', ') : '');
    return `<div class="sres${i === 0 ? ' act' : ''}" data-url="${esc(e.url)}" data-i="${i}">
      <div class="t"><span class="em">${esc(e.emoji || '📄')}</span><a class="tl" href="${esc(e.url)}"${tgt}>${hl(e.title, r.hits)}</a>${e.soon ? '<span class="soon">Coming soon</span>' : ''}${e.level ? `<span class="soon" style="color:var(--accent-deep);background:var(--accent-soft)">${esc(e.level)}</span>` : ''}<span class="kind">${esc(e.kind)}</span></div>
      ${crumbs}${snip ? `<div class="snip">${snip}</div>` : ''}</div>`;
  }

  /* search dialog, opened from any page with the search button, Ctrl+K or / */
  let modal = null, sel = 0, target = '';
  function openSearch(initial = '') {
    if (!modal) {
      modal = document.createElement('div');
      modal.className = 'smodal';
      modal.innerHTML = `<div class="sbox" role="dialog" aria-modal="true" aria-label="Search everything">
        <div class="sinput"><span>🔎</span><input type="search" placeholder="Search subjects, topics, sections, problems…" aria-label="Search" autocomplete="off"><button class="ibtn" data-close>Esc</button></div>
        <div class="sresults"></div>
        <div class="sfoot"><span>↑ ↓ to move</span><span>Enter to open</span><span>Every grey chip is a link to that level</span></div></div>`;
      document.body.appendChild(modal);
      const inp = modal.querySelector('input');
      inp.addEventListener('input', () => renderSearch(inp.value));
      inp.addEventListener('keydown', e => {
        const items = [...modal.querySelectorAll('.sres')];
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
          e.preventDefault();
          if (!items.length) return;
          sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
          items.forEach((x, k) => x.classList.toggle('act', k === sel));
          items[sel].scrollIntoView({ block: 'nearest' });
        } else if (e.key === 'Enter') {
          const a = items[sel];
          if (a) { e.preventDefault(); a.querySelector('a.tl').click(); }
        }
      });
      modal.addEventListener('click', e => {
        if (e.target === modal || e.target.closest('[data-close]')) closeSearch();
        const c = e.target.closest('.qchip');
        if (c) { inp.value = c.dataset.q; renderSearch(inp.value); inp.focus(); }
        if (e.target.closest('a')) { setTimeout(closeSearch, 50); return; }
        const row = e.target.closest('.sres');
        if (row) row.querySelector('a.tl').click();
      });
    }
    modal.classList.add('open');
    const inp = modal.querySelector('input');
    inp.value = initial;
    renderSearch(initial);
    setTimeout(() => inp.focus(), 30);
  }
  function closeSearch() { if (modal) modal.classList.remove('open'); }
  let SUGGEST = [];
  function renderSearch(q) {
    const box = modal.querySelector('.sresults');
    sel = 0;
    if (!q.trim()) {
      box.innerHTML = `<div class="shint"><b>Type any word.</b> Search looks through every subject, module, topic, section and practice problem, and shows the full path to reach it. Every step of the path is a link.
        <div class="chiprow">${SUGGEST.map(s => `<button class="qchip" data-q="${esc(s)}">${esc(s)}</button>`).join('')}</div></div>`;
      return;
    }
    const res = search(q);
    if (!res.length) { box.innerHTML = `<div class="shint"><b>No match for “${esc(q)}”.</b> Try a shorter word, or one of these:<div class="chiprow">${SUGGEST.map(s => `<button class="qchip" data-q="${esc(s)}">${esc(s)}</button>`).join('')}</div></div>`; return; }
    const order = ['Subject', 'Module', 'Topic', 'Section'];
    const groups = new Map();
    res.forEach(r => { const g = order.includes(r.e.kind) ? r.e.kind : 'Inside the notes'; if (!groups.has(g)) groups.set(g, []); groups.get(g).push(r); });
    const names = { Subject: 'Subjects', Module: 'Modules', Topic: 'Topics', Section: 'Sections', 'Inside the notes': 'Inside the notes' };
    let i = 0, h = '';
    for (const g of [...order, 'Inside the notes']) {
      if (!groups.has(g)) continue;
      h += `<div class="sgroup">${names[g]} · ${groups.get(g).length}</div>` + groups.get(g).map(r => resultHtml(r, i++, target)).join('');
    }
    box.innerHTML = h;
  }
  function initSearch(opts = {}) {
    target = opts.target || '';
    SUGGEST = opts.suggest || [];
    document.addEventListener('keydown', e => {
      const typing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName);
      if ((e.key === 'k' || e.key === 'K') && (e.ctrlKey || e.metaKey)) { e.preventDefault(); openSearch(); }
      else if (e.key === '/' && !typing) { e.preventDefault(); openSearch(); }
      else if (e.key === 'Escape') closeSearch();
    });
    document.querySelectorAll('[data-search]').forEach(b => {
      b.addEventListener('click', () => openSearch());
      b.addEventListener('keydown', e => { if (e.key === 'Enter' && b.tagName !== 'BUTTON') openSearch(); });
    });
  }

  /* the little mascot used as the logo and on the home page */
  function mascotSvg(big) {
    return `<svg viewBox="0 0 120 120" ${big ? 'class="mascot" id="mascot" role="img" aria-label="Bit the mascot. Click for a joke."' : 'aria-hidden="true"'}>
      <defs><linearGradient id="mg${big ? 1 : 0}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7cc8ff"/><stop offset="1" stop-color="#2b7de9"/></linearGradient></defs>
      <line x1="60" y1="20" x2="60" y2="8" stroke="#2b7de9" stroke-width="4" stroke-linecap="round"/>
      <circle cx="60" cy="8" r="7" fill="#ffc928" class="bulb"/>
      <rect x="14" y="20" width="92" height="86" rx="34" fill="url(#mg${big ? 1 : 0})"/>
      <ellipse cx="60" cy="96" rx="28" ry="6" fill="#ffffff" opacity=".25"/>
      <g class="eyes">
        <ellipse cx="42" cy="56" rx="13" ry="${big ? 15 : 14}" fill="#fff" class="eyewhite"/>
        <ellipse cx="78" cy="56" rx="13" ry="${big ? 15 : 14}" fill="#fff" class="eyewhite"/>
        <circle cx="44" cy="58" r="6.5" fill="#0f2747" class="pupil"/>
        <circle cx="80" cy="58" r="6.5" fill="#0f2747" class="pupil"/>
        <circle cx="46" cy="55" r="2.2" fill="#fff" class="pupil"/>
        <circle cx="82" cy="55" r="2.2" fill="#fff" class="pupil"/>
      </g>
      <circle cx="30" cy="76" r="6" fill="#ff8fb8" opacity=".75"/>
      <circle cx="90" cy="76" r="6" fill="#ff8fb8" opacity=".75"/>
      <path d="M48 80 Q60 92 72 80" stroke="#0f2747" stroke-width="4" fill="none" stroke-linecap="round" class="mouth"/>
      ${big ? '<path d="M14 70 Q2 62 6 50" stroke="#2b7de9" stroke-width="7" fill="none" stroke-linecap="round" class="arm"/><path d="M106 70 Q118 62 114 50" stroke="#2b7de9" stroke-width="7" fill="none" stroke-linecap="round"/>' : ''}
    </svg>`;
  }
  function brandHtml(site, href = 'index.html') {
    return `<a class="brand" href="${href}" title="Home">${mascotSvg(false)}<span><b>${esc(site.name)}</b><small>${esc(site.tagline || '')}</small></span></a>`;
  }
  function themeButton(onToggle) {
    const b = document.createElement('button');
    b.className = 'ibtn';
    const label = () => { b.innerHTML = FUN.currentTheme() === 'dark' ? '☀️ <span class="lbl">Light</span>' : '🌙 <span class="lbl">Dark</span>'; };
    label();
    b.title = 'Switch light or dark';
    b.onclick = () => { const t = FUN.toggleTheme(); label(); if (onToggle) onToggle(t); };
    return b;
  }
  function showWarnings(cat, where) {
    if (!cat.warnings.length) return;
    const d = document.createElement('div');
    d.className = 'warn';
    d.innerHTML = `Heads up: data/catalog.js has ${cat.warnings.length} problem${cat.warnings.length > 1 ? 's' : ''}.<ul>${cat.warnings.map(w => `<li>${esc(w)}</li>`).join('')}</ul>`;
    where.prepend(d);
    console.warn('Catalog problems:', cat.warnings);
  }
  function errorPage(err) {
    document.body.innerHTML = `<div class="empty" style="height:100vh"><div><div class="em">🙈</div><h2>The catalog could not be read</h2><p>${esc(err.message)}. Check that data/catalog.js exists and that it has no typing mistakes such as a missing comma or bracket. Your browser's developer console shows the exact line.</p></div></div>`;
  }

  return { esc, norm, loadCatalog, buildIndex, search, openSearch, closeSearch, initSearch, subjectUrl, moduleUrl, topicUrl, sectionUrl, mascotSvg, brandHtml, themeButton, showWarnings, errorPage };
})();
