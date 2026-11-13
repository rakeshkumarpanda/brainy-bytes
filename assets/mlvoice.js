/* ===== Voice notes for the Machine Learning chapter pages (English).
   1. Every step by step animation gets a "Voice off / Voice on" button next to Play, Step, Back and Reset.
      While it is on, each time the reader steps forward or back (or presses Play) the explanation of that step is
      read aloud. The choice is remembered for the whole site.
   2. Every lesson gets a "Listen to this lesson" button under its title. It reads the lesson's explanations in
      order (headings, paragraphs, the what, why and how boxes, scenarios, notes and summary points) and marks the
      part being read. Code, tables and the animations themselves are skipped, because they are read by the eye.
   It uses the speech voices already installed in the browser. Nothing is sent anywhere. ===== */
(() => {
  const synth = 'speechSynthesis' in window ? window.speechSynthesis : null;
  if (!synth) return;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage unavailable */ } }
  };
  let voiceOn = store.get('ml-voice-steps') === '1';
  let rate = +(store.get('ml-voice-rate') || 0.95);
  if (!(rate >= 0.6 && rate <= 1.4)) rate = 0.95;
  let lessonRun = 0;

  function pickVoice() {
    const vs = synth.getVoices().filter(v => /^en[-_]/i.test(v.lang) || v.lang === 'en');
    const good = v => (/natural|neural|online|premium|enhanced/i.test(v.name) ? 3 : 0) + (/google/i.test(v.name) ? 2 : 0) + (/en[-_](us|gb|in)/i.test(v.lang) ? 1 : 0);
    return vs.sort((a, b) => good(b) - good(a))[0] || null;
  }
  /* turn shown text into words that sound right when read aloud */
  function spoken(t) {
    return String(t)
      .replace(/\s+/g, ' ')
      .replace(/×/g, ' times ').replace(/÷/g, ' divided by ').replace(/−/g, ' minus ').replace(/≈/g, ' about ')
      .replace(/≤/g, ' less than or equal to ').replace(/≥/g, ' greater than or equal to ').replace(/≠/g, ' not equal to ')
      .replace(/→/g, ' to ').replace(/²/g, ' squared').replace(/³/g, ' cubed').replace(/√/g, ' square root of ')
      .replace(/Σ/g, ' sum of ').replace(/θ/g, ' theta ').replace(/λ/g, ' lambda ').replace(/α/g, ' alpha ').replace(/β/g, ' beta ')
      .replace(/γ/g, ' gamma ').replace(/ε/g, ' epsilon ').replace(/σ/g, ' sigma ').replace(/μ/g, ' mu ').replace(/η/g, ' eta ')
      .replace(/ŷ/g, ' y hat ').replace(/x̄/g, ' x bar ').replace(/ȳ/g, ' y bar ')
      .replace(/\s+/g, ' ').trim();
  }
  function say(text, onend) {
    synth.cancel();
    const u = new SpeechSynthesisUtterance(spoken(text));
    const v = pickVoice();
    if (v) u.voice = v;
    u.lang = v ? v.lang : 'en-US';
    u.rate = rate;
    if (onend) { u.onend = onend; u.onerror = onend; }
    synth.speak(u);
    return u;
  }

  /* ---------- 1. animations ---------- */
  const lastSaid = new WeakMap();
  function addToggle(el) {
    const ctl = el.querySelector('.z-ctl');
    if (!ctl || ctl.querySelector('.ml-vb') || !ctl.querySelector('.stp')) return;
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'ml-vb';
    b.title = 'Read each step aloud when you press Step, Back or Play';
    const paint = () => { b.textContent = voiceOn ? 'Voice on' : 'Voice off'; b.classList.toggle('on', voiceOn); b.setAttribute('aria-pressed', voiceOn ? 'true' : 'false'); };
    paint();
    b.addEventListener('click', () => {
      voiceOn = !voiceOn;
      store.set('ml-voice-steps', voiceOn ? '1' : '0');
      document.querySelectorAll('.ml-vb').forEach(x => { x.textContent = voiceOn ? 'Voice on' : 'Voice off'; x.classList.toggle('on', voiceOn); x.setAttribute('aria-pressed', voiceOn ? 'true' : 'false'); });
      if (voiceOn) { const now = el.querySelector('.z-read .cai-now'); if (now) { lastSaid.set(el, now.textContent); say(now.textContent); } } else synth.cancel();
    });
    ctl.insertBefore(b, ctl.querySelector('.z-pos'));
    const read = el.querySelector('.z-read');
    new MutationObserver(() => {
      if (!voiceOn) return;
      const now = read.querySelector('.cai-now');
      if (!now) return;
      const t = now.textContent;
      if (lastSaid.get(el) === t) return;
      lastSaid.set(el, t);
      lessonRun++;
      document.querySelectorAll('.ml-listen.on').forEach(x => x.click());
      say(t);
    }).observe(read, { childList: true, subtree: true, characterData: true });
  }
  function scanWidgets(root) {
    (root.querySelectorAll ? root : document).querySelectorAll('.cvz[data-on]').forEach(addToggle);
  }

  /* ---------- 2. lessons ---------- */
  const READ = 'h2, h3, h4, p, li, .wwh-c, .scene-h, .note > div, .fx-h, .fx-n, .vs-h, .vs-v, .pg-c, .ld-p:not([hidden]) p';
  const SKIP = '.cvz, .cv-code, pre, code, table, .tw, .z-read, .pl, .ck-nb, .walk, .cv-lnav, .cv-lno, .ml-listen, .py-dlrow, details.deep:not([open]) .deep-b, .algo, .cai-log';
  function chunks(article) {
    const out = [];
    article.querySelectorAll(READ).forEach(n => {
      if (n.closest(SKIP)) return;
      if (n.matches('li, p') && n.parentElement.closest('.wwh-c, .pg-c, li')) return;  /* read once, as part of its box */
      if (n.matches('.wwh-c') || n.matches('.pg-c')) { out.push({ n, t: n.innerText }); return; }
      const t = (n.innerText || '').trim();
      if (t && t.length > 1) out.push({ n, t });
    });
    return out;
  }
  function addListen(article) {
    if (article.querySelector('.ml-listen')) return;
    const h = article.querySelector('h2');
    if (!h) return;
    const bar = document.createElement('div');
    bar.className = 'ml-lbar';
    bar.innerHTML = '<button type="button" class="ml-listen" aria-pressed="false">Listen to this lesson</button>' +
      '<label class="ml-rate">Speed <select><option value="0.8">Slow</option><option value="0.95">Normal</option><option value="1.15">Fast</option></select></label>' +
      '<span class="ml-lnote">Reads the explanations aloud. Code and tables are skipped.</span>';
    h.insertAdjacentElement('afterend', bar);
    const sel = bar.querySelector('select');
    sel.value = [0.8, 0.95, 1.15].reduce((a, b) => Math.abs(b - rate) < Math.abs(a - rate) ? b : a, 0.95);
    sel.addEventListener('change', () => { rate = +sel.value; store.set('ml-voice-rate', String(rate)); });
    const btn = bar.querySelector('.ml-listen');
    btn.addEventListener('click', () => {
      if (btn.classList.contains('on')) {
        lessonRun++;
        synth.cancel();
        stopLesson(btn, article);
        return;
      }
      document.querySelectorAll('.ml-listen.on').forEach(x => x.click());
      const run = ++lessonRun;
      const parts = chunks(article);
      btn.classList.add('on'); btn.textContent = 'Stop reading'; btn.setAttribute('aria-pressed', 'true');
      let i = 0;
      const next = () => {
        if (run !== lessonRun) return;
        article.querySelectorAll('.ml-reading').forEach(x => x.classList.remove('ml-reading'));
        if (i >= parts.length) { stopLesson(btn, article); return; }
        const p = parts[i++];
        p.n.classList.add('ml-reading');
        const r = p.n.getBoundingClientRect();
        if (r.top < 90 || r.bottom > innerHeight) p.n.scrollIntoView({ block: 'center', behavior: 'smooth' });
        say(p.t, next);
      };
      next();
    });
  }
  function stopLesson(btn, article) {
    btn.classList.remove('on'); btn.textContent = 'Listen to this lesson'; btn.setAttribute('aria-pressed', 'false');
    article.querySelectorAll('.ml-reading').forEach(x => x.classList.remove('ml-reading'));
  }

  function start() {
    document.querySelectorAll('article.cv-lesson').forEach(addListen);
    scanWidgets(document);
    /* animations mount when their lesson opens, so watch for new ones */
    new MutationObserver(ms => {
      for (const m of ms) {
        if (m.type === 'attributes' && m.target.matches && m.target.matches('.cvz[data-on]')) addToggle(m.target);
      }
    }).observe(document.body, { subtree: true, attributes: true, attributeFilter: ['data-on'] });
    setTimeout(() => scanWidgets(document), 800);
    /* stop talking when the reader leaves the lesson or the page */
    document.addEventListener('click', e => {
      if (e.target.closest('.cv-tab, .cv-stepper a, .cv-lnav a, .cv-lnav button')) { lessonRun++; synth.cancel(); document.querySelectorAll('.ml-listen.on').forEach(b => stopLesson(b, b.closest('article'))); }
    });
    addEventListener('pagehide', () => synth.cancel());
  }
  if (synth.onvoiceschanged !== undefined) synth.onvoiceschanged = () => {};
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
