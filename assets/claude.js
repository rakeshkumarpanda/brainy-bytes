/* Master the Claude chapters: the "beginner path only" switch, step by step screenshot guides and growing bars. The rest of the page comes from assets/jsplay.js. */
(function () {
  function wire() {
    const b = document.getElementById('easyOnly');
    if (!b) return;
    const set = on => {
      document.body.classList.toggle('easy-only', on);
      b.setAttribute('aria-pressed', on);
      b.textContent = on ? '📖 Show every part' : '🧒 Show the beginner path only';
      try { localStorage.setItem('claude-easy-only', on ? '1' : ''); } catch (e) { /* storage unavailable */ }
    };
    let on = false;
    try { on = localStorage.getItem('claude-easy-only') === '1'; } catch (e) { /* storage unavailable */ }
    set(on);
    b.onclick = () => set(!document.body.classList.contains('easy-only'));
    wireShots();
    wireBars();
  }

  // Step by step screenshot guides: show one step at a time.
  function wireShots() {
    document.querySelectorAll('.cl-shots').forEach(box => {
      const steps = [...box.querySelectorAll('.cl-step')];
      const dots = [...box.querySelectorAll('.cl-dot')];
      const prev = box.querySelector('.cl-prev'), next = box.querySelector('.cl-next'), count = box.querySelector('.cl-count');
      let at = 0;
      const go = i => {
        at = Math.max(0, Math.min(steps.length - 1, i));
        steps.forEach((s, k) => { s.hidden = k !== at; });
        dots.forEach((d, k) => { if (k === at) d.setAttribute('aria-current', 'step'); else d.removeAttribute('aria-current'); });
        prev.disabled = at === 0;
        next.disabled = at === steps.length - 1;
        count.textContent = `Step ${at + 1} of ${steps.length}`;
      };
      dots.forEach((d, k) => { d.onclick = () => go(k); });
      prev.onclick = () => go(at - 1);
      next.onclick = () => go(at + 1);
      go(0);
    });
  }

  // Bars that grow to their width when they scroll into view.
  function wireBars() {
    const bars = document.querySelectorAll('.cl-bar');
    if (!bars.length) return;
    if (!('IntersectionObserver' in window)) { bars.forEach(b => b.classList.add('in')); return; }
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: 0.3 });
    bars.forEach(b => io.observe(b));
  }
  window.CLAUDE_PAGE = { wire };
})();
