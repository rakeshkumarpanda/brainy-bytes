/* Master the Claude chapters: the "beginner path only" switch. The rest of the page comes from assets/jsplay.js. */
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
  }
  window.CLAUDE_PAGE = { wire };
})();
