/* ===== Learner progress, saved in this browser only (localStorage) =====
   Shape: { done: { 'subject/topic': time }, quiz: { 'subject/topic': { good, total, best, at } }, last: { s, t, hash, at } }
   Everything is keyed by subject id and topic id from data/catalog.js. */
const PROGRESS = (() => {
  const KEY = 'lh-progress-v1';
  const key = t => t.subject.id + '/' + t.id;
  function load() {
    try {
      const p = JSON.parse(localStorage.getItem(KEY) || '{}');
      return { done: p.done || {}, quiz: p.quiz || {}, last: p.last || null };
    } catch (e) { return { done: {}, quiz: {}, last: null }; }
  }
  function save(p) {
    try { localStorage.setItem(KEY, JSON.stringify(p)); } catch (e) { /* storage unavailable */ }
  }

  const isDone = t => !!load().done[key(t)];
  function setDone(t, on) {
    const p = load();
    if (on) p.done[key(t)] = Date.now(); else delete p.done[key(t)];
    save(p);
  }
  const quiz = t => load().quiz[key(t)] || null;
  function recordQuiz(t, good, total) {
    if (!total) return;
    const p = load(), old = p.quiz[key(t)];
    p.quiz[key(t)] = { good, total, best: Math.max(good, old && old.total === total ? old.best : 0), at: Date.now() };
    save(p);
  }
  function visit(t, hash) {
    const p = load();
    p.last = { s: t.subject.id, t: t.id, hash: hash || '', at: Date.now() };
    save(p);
  }

  /* the last topic opened, looked up in the catalog so a removed topic is ignored */
  function lastTopic(cat) {
    const l = load().last;
    if (!l) return null;
    const s = cat.subjects.find(x => x.id === l.s);
    const t = s && s.liveTopics.find(x => x.id === l.t);
    return t ? { topic: t, hash: l.hash } : null;
  }
  function stats(topics) {
    const p = load();
    const live = topics.filter(t => !t.soon);
    return { done: live.filter(t => p.done[key(t)]).length, total: live.length };
  }

  /* Read the quiz and number practice score from a topic page's DOM.
     Works for every page, whether it loads assets/learn.js or carries its own copy. */
  function scoreFrom(doc) {
    const items = doc.querySelectorAll('.lq .lq-item, .lq .lc-item');
    let good = 0, tried = 0;
    items.forEach(it => {
      if (it.classList.contains('right')) good++;
      if (it.classList.contains('right') || it.classList.contains('wrong')) tried++;
    });
    return { good, tried, total: items.length };
  }
  /* Watch a topic page shown in an iframe and record its score after each answer. */
  function watchFrame(frame, t) {
    let doc;
    try { doc = frame.contentDocument; } catch (e) { return; }
    if (!doc) return;
    const check = () => setTimeout(() => {
      const s = scoreFrom(doc);
      if (s.tried) recordQuiz(t, s.good, s.total);
    }, 0);
    doc.addEventListener('click', e => { if (e.target.closest && e.target.closest('.lq')) check(); });
    doc.addEventListener('keydown', e => { if (e.key === 'Enter' && e.target.closest && e.target.closest('.lq')) check(); });
  }

  return { isDone, setDone, quiz, recordQuiz, visit, lastTopic, stats, scoreFrom, watchFrame };
})();
