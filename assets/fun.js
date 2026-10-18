/* ===== Shared fun layer: scroll progress bar, reveal on scroll, rocket back-to-top, confetti, theme sync with the portal ===== */
const FUN = (() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const inFrame = (() => { try { return window.self !== window.top; } catch (e) { return true; } })();
  if (inFrame) document.documentElement.classList.add('embedded');
  const THEME_KEY = 'lh-theme';

  function getTheme() { try { return localStorage.getItem(THEME_KEY); } catch (e) { return null; } }
  function applyTheme(t) {
    if (t === 'dark' || t === 'light') document.documentElement.dataset.theme = t;
    else delete document.documentElement.dataset.theme;
  }
  function currentTheme() {
    return document.documentElement.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  }
  function toggleTheme() {
    const nx = currentTheme() === 'dark' ? 'light' : 'dark';
    applyTheme(nx);
    try { localStorage.setItem(THEME_KEY, nx); } catch (e) { /* storage unavailable */ }
    if (inFrame) { try { parent.postMessage({ lh: 'theme', value: nx }, '*'); } catch (e) { /* no parent */ } }
    return nx;
  }
  applyTheme(getTheme());
  window.addEventListener('message', e => {
    const d = e.data || {};
    if (d.lh === 'theme') applyTheme(d.value);
    else if (d.lh === 'goto' && typeof d.hash === 'string' && d.hash !== location.hash) location.hash = d.hash;
  });
  window.addEventListener('storage', e => { if (e.key === THEME_KEY) applyTheme(e.newValue); });

  /* tell the portal where we are, so it can keep a shareable link */
  function reportHash() {
    if (inFrame) { try { parent.postMessage({ lh: 'hash', hash: location.hash, title: document.title }, '*'); } catch (e) { /* no parent */ } }
  }
  window.addEventListener('hashchange', reportHash);
  window.addEventListener('load', reportHash);

  function confetti(x, y, n = 70) {
    if (reduce) return;
    const c = document.createElement('canvas');
    c.className = 'fun-confetti';
    const dpr = window.devicePixelRatio || 1;
    c.width = innerWidth * dpr; c.height = innerHeight * dpr;
    document.body.appendChild(c);
    const g = c.getContext('2d');
    g.scale(dpr, dpr);
    const cs = getComputedStyle(document.documentElement);
    const cols = ['--accent', '--accent2', '--yellow', '--pink', '--green', '--purple', '--orange'].map(v => cs.getPropertyValue(v).trim() || '#2b7de9');
    const ox = x ?? innerWidth / 2, oy = y ?? innerHeight / 3;
    const ps = Array.from({ length: n }, () => ({
      x: ox, y: oy, vx: (Math.random() - .5) * 13, vy: -Math.random() * 11 - 3,
      r: 4 + Math.random() * 5, a: Math.random() * 6.3, va: (Math.random() - .5) * .4, c: cols[(Math.random() * cols.length) | 0], s: Math.random() < .5
    }));
    let t = 0;
    (function frame() {
      g.clearRect(0, 0, innerWidth, innerHeight);
      for (const p of ps) {
        p.vy += .38; p.vx *= .985; p.x += p.vx; p.y += p.vy; p.a += p.va;
        g.save(); g.translate(p.x, p.y); g.rotate(p.a); g.fillStyle = p.c;
        if (p.s) g.fillRect(-p.r, -p.r / 2, p.r * 2, p.r); else { g.beginPath(); g.arc(0, 0, p.r / 1.4, 0, 6.3); g.fill(); }
        g.restore();
      }
      if (++t < 110) requestAnimationFrame(frame); else c.remove();
    })();
  }

  function initScroll(opts = {}) {
    const bar = document.createElement('div');
    bar.className = 'fun-progress';
    document.body.appendChild(bar);
    const scroller = opts.scroller || null;
    const top = document.createElement('button');
    top.className = 'fun-top';
    top.title = 'Back to the top';
    top.setAttribute('aria-label', 'Back to the top');
    top.textContent = '🚀';
    document.body.appendChild(top);
    const metrics = () => {
      if (scroller) return [scroller.scrollTop, scroller.scrollHeight - scroller.clientHeight];
      const d = document.documentElement;
      return [d.scrollTop || document.body.scrollTop, d.scrollHeight - d.clientHeight];
    };
    const upd = () => {
      const [y, max] = metrics();
      bar.style.width = (max > 0 ? Math.min(100, (y / max) * 100) : 0) + '%';
      top.classList.toggle('show', y > 600);
    };
    (scroller || window).addEventListener('scroll', upd, { passive: true });
    window.addEventListener('resize', upd);
    top.onclick = () => {
      top.classList.add('launch');
      (scroller || window).scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
      setTimeout(() => top.classList.remove('launch', 'show'), 750);
    };
    upd();
    observe();
  }

  let io = null;
  function observe(root = document) {
    const els = root.querySelectorAll('.reveal:not(.in)');
    if (reduce || !('IntersectionObserver' in window)) { els.forEach(e => e.classList.add('in')); return; }
    if (!io) io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });
    els.forEach(e => io.observe(e));
  }

  return { confetti, initScroll, observe, toggleTheme, currentTheme, applyTheme, reportHash, inFrame, reduce };
})();
