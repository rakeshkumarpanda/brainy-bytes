/* ===== Subject page: contents on the left, the chosen topic page on the right ===== */
(async () => {
  let cat;
  try { cat = await LH.loadCatalog(); } catch (e) { LH.errorPage(e); return; }
  const { esc } = LH;
  const site = cat.site;
  LH.buildIndex(cat);
  LH.initSearch({ suggest: site.searchExamples || [] });
  document.getElementById('brandSlot').outerHTML = LH.brandHtml(site);
  const frameMsg = msg => { const f = document.getElementById('frame'); if (f && f.contentWindow) { try { f.contentWindow.postMessage(msg, '*'); } catch (e) { /* frame gone */ } } };
  document.getElementById('themeSlot').replaceWith(LH.themeButton(t => frameMsg({ lh: 'theme', value: t })));

  const side = document.getElementById('side'), main = document.getElementById('main'), layout = document.getElementById('layout');
  const scrim = document.getElementById('scrim');
  const openDrawer = on => { side.classList.toggle('open', on); scrim.classList.toggle('open', on); };
  document.getElementById('drawerBtn').onclick = () => openDrawer(!side.classList.contains('open'));
  scrim.onclick = () => openDrawer(false);

  const q = new URLSearchParams(location.search);
  const subj = cat.subjects.find(s => s.id === q.get('s'));
  if (!subj) {
    document.title = 'Subject not found · ' + site.name;
    side.innerHTML = '';
    main.innerHTML = `<div class="empty"><div><div class="em">🧭</div><h2>We could not find that subject</h2><p>The link may be old. Head back to the home page and pick a subject from the dashboard.</p><a class="ibtn primary" href="index.html">🏠 Go home</a></div></div>`;
    return;
  }
  LH.showWarnings(cat, main);
  document.documentElement.style.setProperty('--c', subj.color || 'var(--accent)');
  const live = subj.liveTopics;
  let cur = null;
  /* a subject with layout 'path' shows a numbered learning path instead of the contents list on the left */
  const pathMode = subj.layout === 'path';
  if (pathMode) { document.body.classList.add('pathmode'); layout.classList.add('pathmode'); }

  /* ----- left side: subject card, filter and modules ----- */
  const closed = new Set();
  try { JSON.parse(localStorage.getItem('lh-closed-' + subj.id) || '[]').forEach(x => closed.add(x)); } catch (e) { /* storage unavailable */ }
  function renderSide(filter = '') {
    const f = LH.norm(filter);
    const mods = subj.modules.map(m => {
      const ts = m.topics.filter(t => !f || LH.norm(t.title + ' ' + (t.keywords || []).join(' ') + ' ' + t.sections.map(s => s.title).join(' ')).includes(f));
      if (!ts.length) return '';
      const isClosed = closed.has(m.id) && !f;
      return `<div class="mod${isClosed ? ' closed' : ''}" data-m="${esc(m.id)}"><button aria-expanded="${!isClosed}"><span>${esc(m.emoji || '🗂️')}</span><span>${esc(m.title)}</span><span class="cnt">${ts.length}</span><span class="chev">▾</span></button>
        <div class="tlist">${ts.map(t => `<a class="titem${t.soon ? ' is-soon' : ''}${cur === t ? ' on' : ''}" href="${LH.topicUrl(t)}" data-t="${esc(t.id)}"><span class="em">${esc(t.emoji)}</span><span class="nm">${esc(t.title)}</span>${t.soon ? '<span class="soon">Soon</span>' : PROGRESS.isDone(t) ? '<span class="tick" title="Completed">✅</span>' : ''}</a>`).join('')}</div></div>`;
    }).join('');
    side.querySelector('.mods').innerHTML = mods || '<p style="color:var(--ink2);font-weight:700;padding:8px">Nothing matches that filter.</p>';
  }
  side.innerHTML = `<a class="subjcard" href="${LH.subjectUrl(subj)}" style="display:block;text-decoration:none;color:inherit" data-home><div class="em">${esc(subj.emoji)}</div><h2>${esc(subj.title)}</h2><p>${esc(subj.blurb || '')}</p><div class="prog" id="sideProg"></div></a>
    ${subj.topics.length > 6 ? '<input class="sidefilter" placeholder="Filter topics…" aria-label="Filter topics">' : ''}
    <div class="mods"></div>`;
  /* progress: meter on the subject card, ticks in the list, and the overview when it is showing */
  function progHtml() {
    const p = PROGRESS.stats(subj.topics);
    if (!p.total) return '';
    const pct = Math.round(p.done / p.total * 100);
    return `<div class="meter"><i style="width:${pct}%"></i></div><span>${p.done ? `${p.done} of ${p.total} topics complete` : 'No topics complete yet'}</span>`;
  }
  function refreshProgress() {
    document.getElementById('sideProg').innerHTML = progHtml();
    renderSide(sf ? sf.value : '');
  }
  renderSide();
  const sf = side.querySelector('.sidefilter');
  if (sf) sf.addEventListener('input', () => renderSide(sf.value));
  document.getElementById('sideProg').innerHTML = progHtml();
  side.addEventListener('click', e => {
    const mb = e.target.closest('.mod>button');
    if (mb) {
      const m = mb.parentElement; m.classList.toggle('closed');
      if (m.classList.contains('closed')) closed.add(m.dataset.m); else closed.delete(m.dataset.m);
      try { localStorage.setItem('lh-closed-' + subj.id, JSON.stringify([...closed])); } catch (err) { /* storage unavailable */ }
      return;
    }
    const a = e.target.closest('.titem');
    if (a && !e.ctrlKey && !e.metaKey && !e.shiftKey) {
      e.preventDefault();
      const t = subj.topics.find(x => x.id === a.dataset.t);
      history.pushState(null, '', LH.topicUrl(t));
      show(t, '');
      openDrawer(false);
    }
    if (e.target.closest('[data-home]') && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      history.pushState(null, '', LH.subjectUrl(subj));
      show(null);
      openDrawer(false);
    }
  });

  /* ----- breadcrumb ----- */
  function crumbs(t, extra) {
    const parts = [`<a href="index.html">🏠 Home</a>`, `<a href="${LH.subjectUrl(subj)}">${esc(subj.title)}</a>`];
    if (t) parts.push(`<a href="${LH.moduleUrl(t.module)}">${esc(t.module.title)}</a>`, `<span class="cur">${esc(t.title)}${extra ? ' · ' + esc(extra) : ''}</span>`);
    document.getElementById('crumbbar').innerHTML = parts.join('<i>›</i>');
  }

  /* ----- right side ----- */
  function overview(focusModule) {
    crumbs(null);
    document.title = subj.title + ' · ' + site.name;
    if (pathMode) { pathOverview(focusModule); return; }
    if (subj.page && !subj.topics.length) { frame({ title: subj.title, emoji: subj.emoji, page: subj.page, summary: subj.blurb, subject: subj }, location.hash.slice(1)); return; }
    main.innerHTML = `<div class="overview">
      <h2>${esc(subj.emoji)} ${esc(subj.title)}</h2>
      <p class="lede">${esc(subj.intro || subj.blurb || '')}</p>
      ${resumeHtml()}
      ${subj.liveTopics.length ? `<div class="prog big">${progHtml()}</div>` : ''}
      ${subj.page ? `<p><a class="ibtn primary" href="#" data-subjpage>📖 Open the main ${esc(subj.title)} notes</a></p>` : ''}
      ${subj.modules.map(m => `<div class="ovmod reveal" id="m-${esc(m.id)}"><h3>${esc(m.emoji || '🗂️')} ${esc(m.title)} <small>${m.topics.filter(t => !t.soon).length} ready · ${m.topics.length} total${modDone(m)}</small></h3>
        ${m.blurb ? `<p class="lede" style="margin:4px 0 0">${esc(m.blurb)}</p>` : ''}
        <div class="tgrid">${m.topics.map(t => `<a class="tcard${t.soon ? ' is-soon' : ''}${PROGRESS.isDone(t) ? ' is-done' : ''}" href="${LH.topicUrl(t)}" data-t="${esc(t.id)}"><span class="em">${esc(t.emoji)}</span><b>${esc(t.title)}</b><span>${esc(t.summary || '')}</span>${t.soon ? '<span><span class="soon">Coming soon</span></span>' : t.sections.length ? `<span>${t.sections.length} lessons inside</span>` : ''}${t.soon ? '' : topicProg(t)}</a>`).join('')}</div></div>`).join('')}
      ${subj.modules.length ? '' : '<div class="empty"><div><div class="em">🍳</div><h2>This subject is cooking</h2><p>Topics will appear here as soon as they are added to the catalog.</p></div></div>'}
    </div>`;
    main.querySelectorAll('.tcard, [data-resume]').forEach(a => a.addEventListener('click', e => {
      if (e.ctrlKey || e.metaKey) return;
      e.preventDefault();
      const t = subj.topics.find(x => x.id === a.dataset.t), h = a.dataset.h || '';
      history.pushState(null, '', LH.topicUrl(t) + (h ? '#' + h : ''));
      show(t, h);
    }));
    const sp = main.querySelector('[data-subjpage]');
    if (sp) sp.onclick = e => { e.preventDefault(); frame({ title: subj.title, emoji: subj.emoji, page: subj.page, summary: subj.blurb, subject: subj }, ''); };
    FUN.observe(main);
    if (focusModule) {
      const el = document.getElementById('m-' + focusModule);
      if (el) { el.classList.add('in'); setTimeout(() => el.scrollIntoView({ behavior: FUN.reduce ? 'auto' : 'smooth', block: 'start' }), 60); }
    }
  }

  /* ----- the learning path: one numbered step per module, topics as links inside each step ----- */
  const openSteps = new Set();
  try { JSON.parse(localStorage.getItem('lh-open-' + subj.id) || '[]').forEach(x => openSteps.add(x)); } catch (e) { /* storage unavailable */ }
  const mins = ts => ts.reduce((a, t) => a + (t.minutes || 0), 0);
  const hrs = m => m >= 90 ? `about ${Math.round(m / 6) / 10} hours` : `about ${m} min`;
  function pathOverview(focusModule) {
    const steps = subj.modules.filter(m => m.step), extra = subj.modules.filter(m => !m.step);
    const all = steps.flatMap(m => m.topics.filter(t => !t.soon));
    const firstOpen = all.find(t => !PROGRESS.isDone(t));
    const curStep = firstOpen ? firstOpen.module : null;
    const r = PROGRESS.lastTopic(cat);
    const resume = r && r.topic.subject === subj ? r : null;
    const target = resume ? resume.topic : (firstOpen || all[0]);
    const count = k => all.reduce((a, t) => a + ((t.counts && t.counts[k]) || 0), 0);
    const p = PROGRESS.stats(all);
    const pct = p.total ? Math.round(p.done / p.total * 100) : 0;
    const status = t => {
      if (PROGRESS.isDone(t)) return '<span class="lp-st done">Completed</span>';
      const q = PROGRESS.quiz(t);
      if (q) return `<span class="lp-st prog">Quiz best ${q.best}/${q.total}</span>`;
      return '<span class="lp-st">Start</span>';
    };
    const topicRow = t => {
      const c = t.counts || {};
      const bits = [c.lessons && `${c.lessons} lessons`, c.problems && `${c.problems} problems`, c.quiz && `${c.quiz} quiz`, c.assign && `${c.assign} assignments`, t.minutes && `${t.minutes} min`].filter(Boolean).join(' · ');
      return `<li><a class="lp-topic${PROGRESS.isDone(t) ? ' is-done' : ''}${t.soon ? ' is-soon' : ''}" href="${LH.topicUrl(t)}" data-t="${esc(t.id)}">
        <span class="lp-tn">${esc(t.emoji || '')}</span><span class="lp-tb"><b>${esc(t.title)}</b><span class="lp-ts2">${esc(t.summary || '')}</span>${bits ? `<span class="lp-tc">${bits}</span>` : ''}</span>${t.soon ? '<span class="lp-st">Soon</span>' : status(t)}</a></li>`;
    };
    const stepHtml = m => {
      const ts = m.topics.filter(t => !t.soon), d = PROGRESS.stats(ts);
      const done = d.total && d.done === d.total, isCur = m === curStep;
      const open = openSteps.has(m.id) || isCur || m.id === focusModule;
      return `<li class="lp-step${done ? ' done' : ''}${isCur ? ' current' : ''}${open ? ' open' : ''}" id="m-${esc(m.id)}" data-m="${esc(m.id)}">
        <div class="lp-rail"><span class="lp-num">${done ? '✓' : m.step}</span></div>
        <div class="lp-card"><button type="button" class="lp-head" aria-expanded="${open}">
          <span class="lp-hb"><span class="lp-meta">Step ${m.step}${m.level ? ' · ' + esc(m.level) : ''} · ${ts.length} topic${ts.length === 1 ? '' : 's'} · ${hrs(mins(ts))}</span><span class="lp-title">${esc(m.title)}</span><span class="lp-blurb">${esc(m.blurb || '')}</span></span>
          <span class="lp-sp">${d.done}/${d.total}<small>done</small></span><span class="chev">▾</span></button>
          <ol class="lp-topics">${m.topics.map(topicRow).join('')}</ol></div></li>`;
    };
    main.innerHTML = `<div class="lpath">
      <header class="lp-hero">
        <div class="lp-kicker">Learning path</div>
        <h1>${esc(subj.title)}</h1>
        <p class="lede">${esc(subj.intro || subj.blurb || '')}</p>
        <div class="lp-stats"><span><b>${steps.length}</b> steps</span><span><b>${all.length}</b> topics</span><span><b>${count('problems')}</b> worked problems</span><span><b>${count('quiz')}</b> quiz questions</span><span><b>${count('assign')}</b> assignments</span><span><b>${hrs(mins(all))}</b></span></div>
        <div class="lp-prog"><div class="meter"><i style="width:${pct}%"></i></div><span>${p.done ? `${p.done} of ${p.total} topics complete` : 'Not started yet. Follow the steps in order, each one builds on the last.'}</span></div>
        ${target ? `<a class="ibtn primary lp-go" href="${LH.topicUrl(target)}${resume && resume.hash ? '#' + esc(resume.hash) : ''}" data-t="${esc(target.id)}" data-h="${esc(resume ? resume.hash : '')}">${resume ? 'Continue: ' + esc(target.title) : 'Start step 1: ' + esc(target.title)}</a>` : ''}
      </header>
      <ol class="lp-steps">${steps.map(stepHtml).join('')}</ol>
      ${extra.map(m => `<div class="lp-extra"><h3>${esc(m.title)}</h3><p class="lede">${esc(m.blurb || '')}</p><ol class="lp-topics">${m.topics.map(topicRow).join('')}</ol></div>`).join('')}
    </div>`;
    main.querySelectorAll('.lp-head').forEach(b => b.addEventListener('click', () => {
      const li = b.closest('.lp-step'), on = !li.classList.contains('open');
      li.classList.toggle('open', on); b.setAttribute('aria-expanded', on);
      if (on) openSteps.add(li.dataset.m); else openSteps.delete(li.dataset.m);
      try { localStorage.setItem('lh-open-' + subj.id, JSON.stringify([...openSteps])); } catch (e) { /* storage unavailable */ }
    }));
    main.querySelectorAll('a[data-t]').forEach(a => a.addEventListener('click', e => {
      if (e.ctrlKey || e.metaKey || e.shiftKey) return;
      e.preventDefault();
      const t = subj.topics.find(x => x.id === a.dataset.t), h = a.dataset.h || '';
      history.pushState(null, '', LH.topicUrl(t) + (h ? '#' + h : ''));
      show(t, h);
    }));
    if (focusModule) {
      const el = document.getElementById('m-' + focusModule);
      if (el) setTimeout(() => el.scrollIntoView({ behavior: FUN.reduce ? 'auto' : 'smooth', block: 'start' }), 60);
    }
  }

  function modDone(m) {
    const p = PROGRESS.stats(m.topics);
    return p.done ? ` · ${p.done} complete` : '';
  }
  function topicProg(t) {
    const q = PROGRESS.quiz(t), done = PROGRESS.isDone(t);
    if (!q && !done) return '';
    return `<span class="tprog">${done ? '<span class="donechip">✅ Complete</span>' : ''}${q ? `<span class="quizchip" title="Best quiz score, latest was ${q.good} of ${q.total}">🎯 Best ${q.best}/${q.total}</span>` : ''}</span>`;
  }
  function resumeHtml() {
    const r = PROGRESS.lastTopic(cat);
    if (!r || r.topic.subject !== subj) return '';
    return `<p><a class="ibtn primary" href="${LH.topicUrl(r.topic)}${r.hash ? '#' + esc(r.hash) : ''}" data-t="${esc(r.topic.id)}" data-h="${esc(r.hash)}" data-resume>▶ Continue with ${esc(r.topic.emoji)} ${esc(r.topic.title)}</a></p>`;
  }

  function soonPage(t) {
    crumbs(t);
    main.innerHTML = `<div class="empty"><div><div class="em">${esc(t.emoji)}</div><h2>${esc(t.title)} is still cooking</h2><p>${esc(t.summary || 'These notes are being written right now.')} Check back soon, or pick a topic that is ready.</p>
      ${live.length ? `<div class="chiprow" style="justify-content:center">${live.slice(0, 6).map(x => `<a class="qchip" style="text-decoration:none;color:inherit" href="${LH.topicUrl(x)}">${esc(x.emoji)} ${esc(x.title)}</a>`).join('')}</div>` : ''}</div></div>`;
  }

  function frame(t, hash) {
    const i = live.indexOf(t);
    const prev = live[i - 1], next = live[i + 1];
    const src = t.page + (hash ? '#' + hash : '');
    const inStep = t.module.topics.filter(x => !x.soon);
    const where = pathMode ? (t.module.step ? `Step ${t.module.step}: ${t.module.title} · Topic ${inStep.indexOf(t) + 1} of ${inStep.length}` : t.module.title) : '';
    main.innerHTML = `<div class="toolbar">
        ${pathMode ? `<a class="ibtn pathbtn" href="${LH.subjectUrl(subj)}" data-path title="Back to the learning path">← <span class="lbl">Learning path</span></a>` : ''}
        <div class="tt">${pathMode ? '' : `<span class="em">${esc(t.emoji)}</span>`}<div style="min-width:0"><h1>${esc(t.title)}</h1><div class="sum">${esc(pathMode ? where : t.summary || '')}</div></div></div>
        <button class="ibtn donebtn" id="doneBtn" aria-pressed="false"></button>
        ${pathMode ? '' : `<button class="ibtn focusbtn" id="focusBtn" title="Hide or show the contents list">${layout.classList.contains('focus') ? '📚 <span class="lbl">Show list</span>' : '🧘 <span class="lbl">Focus</span>'}</button>`}
        ${prev ? `<a class="ibtn" href="${LH.topicUrl(prev)}" data-t="${esc(prev.id)}" title="${esc(prev.title)}">← <span class="lbl">Prev</span></a>` : ''}
        ${next ? `<a class="ibtn" href="${LH.topicUrl(next)}" data-t="${esc(next.id)}" title="${esc(next.title)}"><span class="lbl">Next</span> →</a>` : ''}
        <a class="ibtn" id="fullBtn" href="${esc(src)}" target="_blank" rel="noopener" title="Open this page on its own">↗ <span class="lbl">Full page</span></a>
      </div>
      <div class="framewrap"><div class="loader" id="loader"><div><div class="dots"><i></i><i></i><i></i></div><p>Fetching your notes…</p></div></div>
      <iframe id="frame" title="${esc(t.title)}" src="${esc(src)}" allow="clipboard-write; fullscreen"></iframe></div>`;
    const doneBtn = document.getElementById('doneBtn');
    const paintDone = () => {
      const on = PROGRESS.isDone(t);
      doneBtn.classList.toggle('on', on);
      doneBtn.setAttribute('aria-pressed', on);
      doneBtn.title = on ? 'Click to mark this topic as not complete' : 'Mark this topic as complete';
      doneBtn.innerHTML = pathMode ? (on ? '✓ <span class="lbl">Completed</span>' : '<span class="lbl">Mark complete</span>') : on ? '✅ <span class="lbl">Completed</span>' : '☑️ <span class="lbl">Mark complete</span>';
    };
    paintDone();
    doneBtn.onclick = e => {
      const on = !PROGRESS.isDone(t);
      PROGRESS.setDone(t, on);
      paintDone();
      refreshProgress();
      if (on) FUN.confetti(e.clientX, e.clientY, 50);
    };
    const fr = document.getElementById('frame');
    fr.addEventListener('load', () => {
      document.getElementById('loader').classList.add('hide');
      PROGRESS.watchFrame(fr, t);
      frameMsg({ lh: 'theme', value: FUN.currentTheme() });
    });
    const pb = main.querySelector('[data-path]');
    if (pb) pb.onclick = e => {
      if (e.ctrlKey || e.metaKey) return;
      e.preventDefault();
      history.pushState(null, '', LH.moduleUrl(t.module));
      show(null, '', t.module.id);
    };
    if (!pathMode) document.getElementById('focusBtn').onclick = () => {
      layout.classList.toggle('focus');
      document.getElementById('focusBtn').innerHTML = layout.classList.contains('focus') ? '📚 <span class="lbl">Show list</span>' : '🧘 <span class="lbl">Focus</span>';
    };
    main.querySelectorAll('.toolbar [data-t]').forEach(a => a.addEventListener('click', e => {
      e.preventDefault();
      const nt = subj.topics.find(x => x.id === a.dataset.t);
      history.pushState(null, '', LH.topicUrl(nt));
      show(nt, '');
    }));
    if (/^https?:/.test(location.protocol)) {
      fetch(t.page, { method: 'HEAD', cache: 'no-store' }).then(r => {
        if (r.status === 404) {
          main.querySelector('.framewrap').innerHTML = `<div class="empty"><div><div class="em">📭</div><h2>This page is not uploaded yet</h2><p>The catalog points to <code>${esc(t.page)}</code>, but that file is not on the website. Upload it to that exact folder, or fix the page path in data/catalog.js.</p></div></div>`;
        }
      }).catch(() => { /* offline, let the frame try */ });
    }
  }

  function show(t, hash, focusModule) {
    cur = t;
    side.querySelectorAll('.titem').forEach(a => a.classList.toggle('on', !!t && a.dataset.t === t.id));
    if (!t) { overview(focusModule); return; }
    document.title = t.title + ' · ' + subj.title + ' · ' + site.name;
    if (t.soon) { soonPage(t); return; }
    crumbs(t, hashLabel(t, hash));
    PROGRESS.visit(t, hash);
    frame(t, hash);
    const on = side.querySelector('.titem.on');
    if (on) on.scrollIntoView({ block: 'nearest' });
  }
  function hashLabel(t, hash) {
    if (!hash) return '';
    const h = decodeURIComponent(hash);
    for (const sec of t.sections) {
      if (sec.id === h) return sec.title;
      const it = sec.items.find(x => x.id === h);
      if (it) return it.title;
    }
    return '';
  }

  /* the topic page tells us its own hash, so the address bar stays a shareable deep link */
  window.addEventListener('message', e => {
    const d = e.data || {};
    if (d.lh === 'hash' && cur && !cur.soon) {
      history.replaceState(null, '', LH.topicUrl(cur) + (d.hash || ''));
      PROGRESS.visit(cur, (d.hash || '').slice(1));
      crumbs(cur, hashLabel(cur, (d.hash || '').slice(1)));
    } else if (d.lh === 'theme') {
      FUN.applyTheme(d.value);
      const tb = document.querySelector('.hdr .ibtn[title="Switch light or dark"]');
      if (tb) tb.innerHTML = d.value === 'dark' ? '☀️ <span class="lbl">Light</span>' : '🌙 <span class="lbl">Dark</span>';
    }
  });
  window.addEventListener('hashchange', () => {
    if (cur && !cur.soon) frameMsg({ lh: 'goto', hash: location.hash });
  });
  window.addEventListener('popstate', route);

  function route() {
    const p = new URLSearchParams(location.search);
    const t = subj.topics.find(x => x.id === p.get('t'));
    if (t) show(t, location.hash.slice(1));
    else { cur = null; side.querySelectorAll('.titem').forEach(a => a.classList.remove('on')); overview(p.get('m')); }
  }
  route();
})();
