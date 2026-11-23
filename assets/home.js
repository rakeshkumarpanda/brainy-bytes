/* ===== Home page on Material 3: one tile per domain, then its categories, then the subjects of a category =====
   Views live in the address hash so Back works and every level can be shared:
     index.html            the landing page with one tile per domain (today only Computer Science)
     index.html#/cs        the categories of Computer Science
     index.html#/cs/testing  the subjects of one category
   Everything is built from data/catalog.js (domains, categories and subjects). */
(async () => {
  let cat;
  try { cat = await LH.loadCatalog(); } catch (e) { LH.errorPage(e); return; }
  const { esc, icon } = LH;
  const site = cat.site;
  const view = document.getElementById('view');
  document.getElementById('brandSlot').outerHTML = LH.brandHtml(site).replace('class="brand"', 'class="md-brand"');
  document.getElementById('themeSlot').replaceWith(LH.themeButton());
  document.getElementById('foot').textContent = site.footer || `© ${new Date().getFullYear()} ${site.name}`;
  LH.buildIndex(cat);

  const live = cat.subjects.flatMap(s => s.liveTopics);
  const examples = site.searchExamples && site.searchExamples.length ? site.searchExamples : live.slice(0, 6).map(t => t.title);
  LH.initSearch({ suggest: examples });
  let pi = 0;
  const ph = document.getElementById('ph');
  if (examples.length) { const rot = () => { ph.textContent = 'Try “' + examples[pi++ % examples.length] + '”'; }; rot(); setInterval(rot, 2800); }

  /* the app bar lifts once the page scrolls, as Material top app bars do */
  const bar = document.getElementById('bar');
  addEventListener('scroll', () => bar.classList.toggle('lifted', scrollY > 4), { passive: true });

  const byTitle = (a, b) => a.title.localeCompare(b.title, undefined, { sensitivity: 'base', numeric: true });
  const ready = s => !s.soon;
  /* coming soon subjects and chapters are not shown anywhere on the home page (asked 2026-11-23) */
  cat.domains.forEach(d => d.categories.forEach(c => { c.items = c.items.filter(ready); }));
  cat.domains.forEach(d => { d.categories = d.categories.filter(c => c.items.length); });
  const counts = subs => {
    const ts = subs.flatMap(s => s.liveTopics);
    return { subjects: subs.length, ready: subs.filter(ready).length, topics: ts.length };
  };
  const crumbs = parts => `<nav class="md-crumbs" aria-label="Breadcrumb">${parts.map((p, i) => i === parts.length - 1
    ? `<span class="cur" aria-current="page">${esc(p[0])}</span>`
    : `<a href="${p[1]}">${i === 0 ? icon('home') : ''}${esc(p[0])}</a>${icon('chevron_right', 'sep')}`).join('')}</nav>`;

  function resumeHtml() {
    const last = PROGRESS.lastTopic(cat);
    if (!last) return '';
    const t = last.topic, p = PROGRESS.stats(t.subject.topics);
    return `<a class="md-resume" href="${LH.topicUrl(t)}${last.hash ? '#' + esc(last.hash) : ''}">
      <span class="em">${esc(t.subject.emoji)}</span>
      <span class="rt"><small>Pick up where you left off</small><b>${esc(t.title)}</b><small>${esc(t.subject.title)} · ${p.done} of ${p.total} topics complete</small></span>
      <span class="md-btn tonal">${icon('play_arrow')}Continue</span></a>`;
  }

  /* ---------- the landing page ---------- */
  function landing() {
    const all = counts(cat.subjects);
    const nLessons = live.reduce((n, t) => n + ((t.counts && t.counts.lessons) || t.sections.length), 0);
    const head = site.headline || ['Learn it deep.', 'Laugh along the way.'];
    document.title = site.name + (site.tagline ? ' · ' + site.tagline : '');
    view.innerHTML = `<div class="md-view">
      <section class="md-hero">
        <div>
          <span class="eyebrow">${icon('school')} Free and deep learning</span>
          <h1>${esc(head[0])}<br>${esc(head[1] || '')}</h1>
          <p>${esc(site.intro || '')}</p>
          <div class="row">
            <a class="md-btn" href="${cat.domains[0] ? LH.domainUrl(cat.domains[0]) : '#'}">${icon('auto_stories')}Start learning</a>
            <button class="md-btn tonal" type="button" id="surprise">${icon('casino')}Surprise me</button>
          </div>
          <div class="md-stats">
            <div><b>${all.ready}</b><span>Subjects ready</span></div>
            <div><b>${all.topics}</b><span>Chapters</span></div>
            ${nLessons ? `<div><b>${nLessons}</b><span>Lessons inside</span></div>` : ''}
          </div>
          ${resumeHtml()}
        </div>
        <div class="mascot-box"><div id="mascotSlot"></div></div>
      </section>
      <div class="md-sechead"><div><h2>Choose where to begin</h2><p>Open a domain to see its categories and courses.</p></div></div>
      <div class="md-tiles${cat.domains.length === 1 ? ' one' : ''}">${cat.domains.map(d => {
        const subs = d.categories.flatMap(c => c.items), c = counts(subs);
        return `<a class="md-tile hero-tile" href="${LH.domainUrl(d)}" style="--c:${esc(d.color || 'var(--md-primary)')}">
          <span class="ic">${icon(d.icon || 'school', 'fill')}</span>
          <span class="body"><h3>${esc(d.title)}</h3>
          <p>${esc(d.blurb || '')}</p>
          <span class="peek">${d.categories.map(x => `<span>${icon(x.icon || 'list')}${esc(x.title)}</span>`).join('')}</span>
          <span class="meta"><span>${d.categories.length} categories</span><span>·</span><span>${c.ready} subjects ready</span><span>·</span><span>${c.topics} chapters</span><span class="go">${icon('arrow_forward')}</span></span></span>
        </a>`;
      }).join('')}</div>
    </div>`;
    document.getElementById('mascotSlot').outerHTML = LH.mascotSvg(true);
    const m = document.getElementById('mascot');
    if (m) m.addEventListener('click', e => FUN.confetti(e.clientX, e.clientY, 50));
    document.getElementById('surprise').onclick = e => {
      if (!live.length) return;
      const t = live[Math.floor(Math.random() * live.length)];
      FUN.confetti(e.clientX, e.clientY, 40);
      setTimeout(() => { location.href = LH.topicUrl(t); }, 260);
    };
  }

  /* ---------- the categories of one domain ---------- */
  function domainView(d) {
    document.title = d.title + ' · ' + site.name;
    view.innerHTML = `<div class="md-view">
      ${crumbs([['Home', 'index.html'], [d.title]])}
      <div class="md-sechead"><div><h2>${esc(d.title)}</h2><p>${esc(d.blurb || '')}</p></div></div>
      <div class="md-tiles">${d.categories.map(c => {
        const n = counts(c.items);
        const done = c.items.reduce((a, s) => a + PROGRESS.stats(s.topics).done, 0);
        return `<a class="md-tile" href="${LH.categoryUrl(c)}" style="--c:${esc(c.color || 'var(--md-primary)')}">
          <span class="ic">${icon(c.icon || 'list', 'fill')}</span>
          <h3>${esc(c.title)}</h3>
          <p>${esc(c.blurb || '')}</p>
          <div class="peek">${c.items.slice().sort(byTitle).slice(0, 4).map(s => `<span>${esc(s.emoji)} ${esc(s.title)}</span>`).join('')}${c.items.length > 4 ? `<span>+${c.items.length - 4} more</span>` : ''}</div>
          <div class="meta"><span>${n.subjects} subject${n.subjects === 1 ? '' : 's'}</span><span>·</span><span>${n.topics} chapters</span>${done ? `<span class="md-done">${icon('task_alt')}${done} done</span>` : ''}<span class="go">${icon('arrow_forward')}</span></div>
        </a>`;
      }).join('')}</div>
    </div>`;
  }

  /* ---------- the subjects of one category ---------- */
  function categoryView(c) {
    document.title = c.title + ' · ' + c.domain.title + ' · ' + site.name;
    const subs = c.items.slice().sort(byTitle);
    view.innerHTML = `<div class="md-view">
      ${crumbs([['Home', 'index.html'], [c.domain.title, LH.domainUrl(c.domain)], [c.title]])}
      <div class="md-sechead"><div><h2>${esc(c.title)}</h2><p>${esc(c.blurb || '')}</p></div></div>
      <div class="md-cards">${subs.map(card).join('')}</div>
    </div>`;
    requestAnimationFrame(() => view.querySelectorAll('.md-meter i').forEach(i => { i.style.width = i.dataset.w + '%'; }));
  }
  function card(s) {
    const rd = s.liveTopics.length;
    const prog = PROGRESS.stats(s.liveTopics);
    const pct = rd ? Math.round(prog.done / rd * 100) : 0;
    const status = s.page && !rd ? 'Ready to read' : `${rd} chapter${rd === 1 ? '' : 's'}${prog.done ? '' : ' to explore'}`;
    const inner = `<div class="top"><span class="em">${esc(s.emoji)}</span><h3>${esc(s.title)}</h3></div>
      <p>${esc(s.blurb || '')}</p>
      ${s.tags && s.tags.length ? `<div class="tags">${s.tags.slice(0, 4).map(t => `<span>${esc(t)}</span>`).join('')}</div>` : ''}
      <div class="md-meter"><i data-w="${pct}"></i></div>
      <div class="foot"><span>${status}</span>${prog.done ? `<span class="md-done">${icon('task_alt')}${prog.done} done</span>` : ''}<span class="open">Open${icon('arrow_forward')}</span></div>`;
    return `<a class="md-card" href="${LH.subjectUrl(s)}" style="--c:${esc(s.color || 'var(--md-primary)')}">${inner}</a>`;
  }

  /* ---------- routing ---------- */
  function route() {
    const [dId, cId] = location.hash.replace(/^#\/?/, '').split('/').map(decodeURIComponent);
    const d = cat.domains.find(x => x.id === dId);
    const c = d && d.categories.find(x => x.id === cId);
    if (c) categoryView(c);
    else if (d) domainView(d);
    else landing();
    window.scrollTo({ top: 0 });
  }
  addEventListener('hashchange', route);
  route();
  LH.showWarnings(cat, view);
})();
