/* ===== Home page: fun dashboard built from data/catalog.js ===== */
(async () => {
  let cat;
  try { cat = await LH.loadCatalog(); } catch (e) { LH.errorPage(e); return; }
  const { esc } = LH;
  const site = cat.site;
  document.title = site.name + (site.tagline ? ' · ' + site.tagline : '');
  document.getElementById('brandSlot').outerHTML = LH.brandHtml(site);
  document.getElementById('themeSlot').replaceWith(LH.themeButton());
  LH.showWarnings(cat, document.getElementById('subjects'));
  LH.buildIndex(cat);

  const live = cat.subjects.flatMap(s => s.liveTopics);
  const examples = site.searchExamples && site.searchExamples.length ? site.searchExamples : live.slice(0, 6).map(t => t.title);
  LH.initSearch({ target: '_blank', suggest: examples });

  /* headline with letters that jump when touched */
  const head = site.headline || ['Learn it deep.', 'Laugh along.'];
  const letters = (txt, cls) => `<span class="${cls || ''}">${txt.split(' ').map(w => `<span style="white-space:nowrap">${[...w].map(ch => `<span class="wl">${esc(ch)}</span>`).join('')}</span>`).join(' ')}</span>`;
  document.getElementById('headline').innerHTML = letters(head[0]) + '<br>' + letters(head[1] || '', 'grad');
  document.getElementById('lede').textContent = site.intro || '';
  if (site.hello) document.getElementById('hello').textContent = site.hello;
  document.getElementById('foot').textContent = site.footer || `© ${new Date().getFullYear()} ${site.name}`;

  /* rotating search placeholder */
  let pi = 0;
  const ph = document.getElementById('ph');
  const rot = () => { ph.textContent = 'Try “' + examples[pi++ % examples.length] + '”'; };
  if (examples.length) { rot(); setInterval(rot, 2600); }

  /* stats that count up */
  const nSections = live.reduce((n, t) => n + t.sections.length, 0);
  const nItems = live.reduce((n, t) => n + t.sections.reduce((k, s) => k + s.items.length, 0), 0);
  const stats = [[cat.subjects.length, 'Subjects'], [live.length, 'Topics ready'], [nSections, 'Lessons inside'], [nItems, 'Practice problems']].filter(s => s[0] > 0);
  document.getElementById('stats').innerHTML = stats.map(([n, l]) => `<div class="stat"><b data-n="${n}">0</b><span>${l}</span></div>`).join('');
  document.querySelectorAll('.stat b').forEach(b => {
    const n = +b.dataset.n, t0 = performance.now();
    const step = t => { const k = Math.min(1, (t - t0) / 1200); b.textContent = Math.round(n * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(step); };
    FUN.reduce ? (b.textContent = n) : requestAnimationFrame(step);
  });

  /* floating doodles */
  const syms = site.doodles || ['{ }', 'O(n)', '[ ]', '∑', '🐞', '0101', '</>', 'π', '✓', 'if', '∞', '√', '++', '→'];
  const dd = document.getElementById('doodles');
  dd.innerHTML = Array.from({ length: 18 }, (_, i) => {
    const s = syms[i % syms.length];
    return `<span class="doodle" style="left:${(i * 53) % 96}%;top:${(i * 37) % 88}%;font-size:${18 + (i * 7) % 26}px;animation-delay:-${i * 1.3}s;animation-duration:${11 + (i % 6)}s">${esc(s)}</span>`;
  }).join('');
  document.addEventListener('mousemove', e => {
    if (FUN.reduce) return;
    const x = e.clientX / innerWidth - .5, y = e.clientY / innerHeight - .5;
    dd.style.transform = `translate(${x * -24}px, ${y * -18}px)`;
  }, { passive: true });

  /* mascot: eyes follow the pointer, a click tells a joke */
  document.getElementById('mascotSlot').outerHTML = LH.mascotSvg(true);
  const mascot = document.getElementById('mascot');
  const jokes = site.jokes && site.jokes.length ? site.jokes : [['Why did the array break up with the loop', 'It needed some space between elements.']];
  const bubble = document.getElementById('bubble');
  let ji = Math.floor(Math.random() * jokes.length);
  const say = () => {
    const j = jokes[ji++ % jokes.length];
    bubble.style.animation = 'none'; void bubble.offsetWidth; bubble.style.animation = '';
    bubble.innerHTML = Array.isArray(j) ? `${esc(j[0])}…<br><span style="color:var(--accent-deep)">${esc(j[1])}</span><small>Tap me for another one</small>` : `${esc(j)}<small>Tap me for another one</small>`;
  };
  say();
  mascot.addEventListener('click', e => {
    say();
    FUN.confetti(e.clientX, e.clientY, 60);
    mascot.animate([{ transform: 'translateY(0) scale(1)' }, { transform: 'translateY(-26px) scale(1.05,0.95)' }, { transform: 'translateY(0) scale(1)' }], { duration: 500, easing: 'cubic-bezier(.2,1.6,.4,1)' });
  });
  const pupils = mascot.querySelectorAll('.pupil');
  const base = [...pupils].map(p => [+p.getAttribute('cx'), +p.getAttribute('cy')]);
  document.addEventListener('mousemove', e => {
    const r = mascot.getBoundingClientRect();
    const dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
    const d = Math.hypot(dx, dy) || 1, k = Math.min(1, d / 300) * 4;
    pupils.forEach((p, i) => { p.setAttribute('cx', base[i][0] + dx / d * k); p.setAttribute('cy', base[i][1] + dy / d * k); });
  }, { passive: true });
  const whites = mascot.querySelectorAll('.eyewhite');
  setInterval(() => {
    if (FUN.reduce) return;
    whites.forEach(w => w.animate([{ transform: 'scaleY(1)' }, { transform: 'scaleY(.1)' }, { transform: 'scaleY(1)' }], { duration: 220, transformOrigin: 'center' }));
    pupils.forEach(w => w.animate([{ opacity: 1 }, { opacity: 0 }, { opacity: 1 }], { duration: 220 }));
  }, 4200);

  /* subject cards */
  let filter = 'all';
  const fbtns = [['all', 'All'], ['ready', 'Ready now'], ['soon', 'Coming soon']];
  const fbox = document.getElementById('filters');
  const grid = document.getElementById('subjectGrid');
  function card(s) {
    const total = s.topics.length, ready = s.liveTopics.length;
    const pct = s.page ? 100 : total ? Math.round(ready / total * 100) : 0;
    const status = s.page ? 'Ready to read' : ready ? `${ready} of ${total} topics ready` : 'Cooking right now';
    return `<a class="scard reveal ${s.soon ? 'soonc' : ''}" href="${LH.subjectUrl(s)}" target="_blank" rel="noopener" style="--c:${esc(s.color || 'var(--accent)')}">
      <span class="em">${esc(s.emoji)}</span>
      <h3>${esc(s.title)}</h3>
      <p>${esc(s.blurb || '')}</p>
      ${s.tags && s.tags.length ? `<div class="tags">${s.tags.slice(0, 5).map(t => `<span class="tag">${esc(t)}</span>`).join('')}</div>` : ''}
      <div class="meter"><i data-w="${pct}"></i></div>
      <div class="foot">${s.soon ? '<span class="soon">Coming soon</span>' : `<span>${status}</span>`}<span class="go">Open ↗</span></div>
    </a>`;
  }
  function renderGrid() {
    fbox.innerHTML = fbtns.map(([k, l]) => `<button class="qchip" data-f="${k}" style="${filter === k ? 'background:var(--accent);color:var(--accent-ink);border-color:var(--accent)' : ''}">${l}</button>`).join('');
    const list = cat.subjects.filter(s => filter === 'all' || (filter === 'ready' ? !s.soon : s.soon));
    grid.innerHTML = list.map(card).join('') || '<p>No subjects here yet.</p>';
    FUN.observe(grid);
    requestAnimationFrame(() => grid.querySelectorAll('.meter i').forEach(i => { i.style.width = i.dataset.w + '%'; }));
    grid.querySelectorAll('.scard').forEach(c => {
      c.addEventListener('mousemove', e => {
        if (FUN.reduce) return;
        const r = c.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        c.style.transform = `perspective(700px) rotateY(${x * 10}deg) rotateX(${-y * 10}deg) translateY(-4px)`;
      });
      c.addEventListener('mouseleave', () => { c.style.transform = ''; });
    });
  }
  fbox.addEventListener('click', e => { const b = e.target.closest('[data-f]'); if (b) { filter = b.dataset.f; renderGrid(); } });
  renderGrid();

  /* surprise me */
  document.getElementById('surprise').onclick = e => {
    if (!live.length) return;
    const t = live[Math.floor(Math.random() * live.length)];
    FUN.confetti(e.clientX, e.clientY, 40);
    setTimeout(() => window.open(LH.topicUrl(t), '_blank', 'noopener'), 250);
  };

  /* newest topics */
  const fresh = live.filter(t => t.added).sort((a, b) => String(b.added).localeCompare(String(a.added))).slice(0, 6);
  if (!fresh.length) document.getElementById('newSec').remove();
  else document.getElementById('newList').innerHTML = fresh.map(t => `<a class="ncard reveal" href="${LH.topicUrl(t)}" target="_blank" rel="noopener"><span class="em">${esc(t.emoji)}</span><span><b>${esc(t.title)}</b><small>${esc(t.subject.title)} · added ${esc(t.added)}</small></span></a>`).join('');

  /* joke of the day */
  const day = Math.floor(Date.now() / 864e5);
  const j = jokes[day % jokes.length];
  document.getElementById('jotd').textContent = Array.isArray(j) ? j[0] + '… ' + j[1] : j;

  FUN.initScroll();
  FUN.observe();
})();
