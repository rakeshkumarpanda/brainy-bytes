/* ===== Voice teaching, the same on every chapter page of every subject (English).
   1. Every step by step animation gets a "Voice off / Voice on" button in its control row, next to Play, Step,
      Back and Reset. While it is on, each time the reader steps forward or back (or presses Play) the explanation
      of that step is read aloud. The choice is remembered for the whole site. While Play runs with the voice on,
      the animation waits for the voice to finish explaining a step before it moves to the next one
      (window.__vtHold, asked by assets/cvviz.js and assets/viz.js before each automatic step).
   2. Every lesson gets a "Listen to this lesson" bar under its title, with a Speed choice. It first reads the
      lesson's background talk (div.vt-talk, hidden on the page). The Cybersecurity builder writes it into the page.
      Every other subject keeps it in data/talk/<subject>/<page>.js, loaded from here, so a rebuild never loses it.
      After the talk it reads
      then the lesson's explanations in order (headings, paragraphs, boxes, scenarios, notes and summary points) and marks the part
      being read. Code, tables and the animations themselves are skipped, because they are read by the eye.
   It works on both page families of the site:
     the chapter pages built by tools/cv-build (article.cv-lesson lessons, .cvz animations from assets/cvviz.js)
     the older chapter pages laid out by assets/pathskin.js (section.jsec lessons, .viz players from assets/viz.js)
   It uses the speech voices already installed in the browser. Nothing is sent anywhere.
   Its look is injected from here, so a page needs only this one script tag. ===== */
/* the side by side Code Playground on lessons that teach code (assets/playside.js decides where it shows) */
(() => { const me = document.currentScript; if (!me || !me.src || window.__playSideLoad) return; window.__playSideLoad = true;
  const s = document.createElement('script'); s.src = new URL('playside.js', me.src).href; s.defer = true; document.head.appendChild(s); })();
(() => {
  const synth = 'speechSynthesis' in window ? window.speechSynthesis : null;
  if (!synth || window.__voiceTeach) return;
  window.__voiceTeach = true;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage unavailable */ } }
  };
  /* the old Machine Learning keys are read once, so a reader's earlier choice carries over */
  const steps0 = store.get('vt-voice-steps') ?? store.get('ml-voice-steps');
  let voiceOn = steps0 === '1';
  const RATES = [0.8, 0.95, 1.15];
  let rate = +(store.get('vt-voice-rate') || store.get('ml-voice-rate') || 0.95);
  if (!(rate >= 0.6 && rate <= 1.4)) rate = 0.95;
  let lessonRun = 0;
  const here = (document.currentScript && document.currentScript.src) || '';

  /* ---------- look ---------- */
  const css = `
.vt-lbar{display:flex; flex-wrap:wrap; gap:8px 12px; align-items:center; margin:2px 0 14px}
.vt-listen{border:1px solid var(--cv, var(--accent)); background:var(--cv, var(--accent)); color:#fff; font:800 13.5px Nunito, system-ui, sans-serif;
  border-radius:999px; padding:6px 14px; cursor:pointer}
.vt-listen::before{content:"\\25B6  "}
.vt-listen.on{background:var(--surface); color:var(--cv, var(--accent))}
.vt-listen.on::before{content:"\\25A0  "}
.vt-rate{font-size:13px; color:var(--ink2); display:inline-flex; gap:6px; align-items:center}
.vt-rate select{font:600 13px Nunito, system-ui, sans-serif; border:1px solid var(--line); border-radius:8px; background:var(--surface); color:var(--ink); padding:2px 6px}
.vt-lnote{font-size:12.5px; color:var(--ink2)}
.vt-reading{outline:3px solid var(--cv-line, var(--accent)); outline-offset:3px; border-radius:6px; background:var(--cv-soft, var(--accent-soft))}
button.vt-vb{border:1px dashed var(--cv, var(--accent)); color:var(--cv, var(--accent)); background:var(--surface); font-weight:700; cursor:pointer}
button.vt-vb::before{content:"\\1F508  "}
button.vt-vb.on{border-style:solid; background:var(--cv-soft, var(--accent-soft))}
button.vt-vb.on::before{content:"\\1F50A  "}
@media print{.vt-lbar, button.vt-vb{display:none}}`;
  const st = document.createElement('style');
  st.id = 'vt-style';
  st.textContent = css;
  (document.head || document.documentElement).appendChild(st);

  /* ---------- speaking ---------- */
  let voice = null;
  function pickVoice() {
    const vs = synth.getVoices().filter(v => /^en[-_]/i.test(v.lang) || v.lang === 'en');
    const good = v => (/natural|neural|online|premium|enhanced/i.test(v.name) ? 3 : 0) + (/google/i.test(v.name) ? 2 : 0) + (/en[-_](us|gb|in)/i.test(v.lang) ? 1 : 0);
    return vs.sort((a, b) => good(b) - good(a))[0] || null;
  }
  synth.addEventListener && synth.addEventListener('voiceschanged', () => { voice = pickVoice(); });
  /* turn shown text into words that sound right when read aloud */
  function spoken(t) {
    return String(t)
      .replace(/\p{Extended_Pictographic}️?/gu, ' ')
      .replace(/\s+/g, ' ')
      .replace(/×/g, ' times ').replace(/÷/g, ' divided by ').replace(/−/g, ' minus ').replace(/≈/g, ' about ')
      .replace(/≤/g, ' less than or equal to ').replace(/≥/g, ' greater than or equal to ').replace(/≠/g, ' not equal to ')
      .replace(/→/g, ' to ').replace(/²/g, ' squared').replace(/³/g, ' cubed').replace(/√/g, ' square root of ')
      .replace(/Σ/g, ' sum of ').replace(/θ/g, ' theta ').replace(/λ/g, ' lambda ').replace(/α/g, ' alpha ').replace(/β/g, ' beta ')
      .replace(/γ/g, ' gamma ').replace(/ε/g, ' epsilon ').replace(/σ/g, ' sigma ').replace(/μ/g, ' mu ').replace(/η/g, ' eta ')
      .replace(/ŷ/g, ' y hat ').replace(/x̄/g, ' x bar ').replace(/ȳ/g, ' y bar ')
      .replace(/[▶◀⏮⏭⏸■↺]/g, ' ')
      .replace(/\s+/g, ' ').trim();
  }
  /* the six-language narrator of the older pages shares the one speech engine, so pause it first */
  function quietNarrator() {
    try { if (typeof VOICE !== 'undefined' && VOICE.state && VOICE.state.playing) VOICE.pause(); } catch (e) { /* narrator absent */ }
  }
  function say(text, onend) {
    quietNarrator();
    synth.cancel();
    const u = new SpeechSynthesisUtterance(spoken(text));
    const v = voice || (voice = pickVoice());
    if (v) u.voice = v;
    u.lang = v ? v.lang : 'en-US';
    u.rate = rate;
    if (onend) { u.onend = onend; u.onerror = onend; }
    synth.speak(u);
    return u;
  }
  function stopAll() {
    lessonRun++;
    holdEl = null;
    synth.cancel();
    document.querySelectorAll('.vt-listen.on').forEach(b => stopLesson(b));
  }

  /* ---------- 1. animations ---------- */
  /* where each kind of animation keeps its controls and the line that explains the current step */
  const KINDS = [
    { ctl: '.cvz[data-on] > .z-body .z-ctl', stepped: c => !!c.querySelector('.stp'), host: c => c.closest('.cvz'),
      read: h => h.querySelector(':scope > .z-read'), before: c => c.querySelector('.z-pos') },
    { ctl: '.vz-ctl', stepped: c => !!c.querySelector('[data-a="fwd"], .vz-play'), host: c => c.closest('.viz') || c.closest('.vz-body') || c.parentElement,
      read: h => h.querySelector('.vz-msg') || h.querySelector('[aria-live]') || h.querySelector('.wk-steps'), before: c => c.querySelector('.vz-cnt') }
  ];
  function stepText(read) {
    /* a player may hold a longer spoken explanation of the step in data-say on its message line (DSA pages) */
    if (read.matches && read.matches('.vz-msg') && read.dataset.say && read.dataset.say.trim()) return read.dataset.say.trim().slice(0, 1500);
    const now = read.querySelector('.cai-now') || read.querySelector('li.cur');
    if (now) return now.innerText || now.textContent;
    /* a copy without tables, code and drawings, so only the explanation is read */
    const copy = read.cloneNode(true);
    copy.querySelectorAll('table, pre, .tw, canvas, svg, .cai-log').forEach(k => k.remove());
    copy.querySelectorAll('p, div, li, br, h4, h5').forEach(k => k.append(' '));
    const t = copy.textContent;
    return t.replace(/\s+/g, ' ').trim().slice(0, 700);
  }
  function paintAll() {
    document.querySelectorAll('button.vt-vb').forEach(x => {
      x.textContent = voiceOn ? 'Voice on' : 'Voice off';
      x.classList.toggle('on', voiceOn);
      x.setAttribute('aria-pressed', voiceOn ? 'true' : 'false');
    });
  }
  const lastSaid = new WeakMap();
  /* Play asks this before each automatic step. It says yes while the voice is still explaining the step shown
     in that animation, and for a short breath after, so the reader hears every step in full. If a browser never
     reports the end of the speech, the wait still ends after a generous time worked out from the length. */
  let holdEl = null, holdUntil = 0, holdTok = 0;
  window.__vtHold = x => {
    if (!voiceOn || !holdEl || !x) return false;
    if (Date.now() > holdUntil) { holdEl = null; return false; }
    return holdEl === x || holdEl.contains(x) || x.contains(holdEl);
  };
  function sayStep(host, t) {
    const tok = ++holdTok;
    holdEl = host;
    const words = spoken(t).split(' ').length;
    holdUntil = Date.now() + 2500 + words * 650 / rate;
    say(t, () => { if (tok === holdTok) holdUntil = Math.min(holdUntil, Date.now() + 350); });
  }
  function addToggle(ctl, kind) {
    if (ctl.dataset.vt || !kind.stepped(ctl)) return;
    const host = kind.host(ctl);
    const read = host && kind.read(host);
    if (!read) return;
    ctl.dataset.vt = '1';
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'vt-vb';
    b.title = 'Read each step aloud when you press Step, Back or Play';
    ctl.insertBefore(b, kind.before(ctl) || null);
    paintAll();
    /* speak only after the reader works the player, not while they move a slider */
    let touched = 0;
    const touch = e => { if (!e.target.closest('.vt-vb')) touched = Date.now(); };
    ctl.addEventListener('click', touch, true);
    ctl.addEventListener('input', touch, true);
    const playing = () => /pause/i.test((ctl.querySelector('.play, .vz-play') || {}).textContent || '');
    b.addEventListener('click', () => {
      voiceOn = !voiceOn;
      store.set('vt-voice-steps', voiceOn ? '1' : '0');
      paintAll();
      if (voiceOn) { const t = stepText(read); if (t) { lastSaid.set(read, t); stopAll(); sayStep(host, t); } } else { holdEl = null; synth.cancel(); }
    });
    new MutationObserver(() => {
      if (!voiceOn || !read.isConnected) return;
      if (!playing() && Date.now() - touched > 2000) return;
      const t = stepText(read);
      if (!t || lastSaid.get(read) === t) return;
      lastSaid.set(read, t);
      stopAll();
      sayStep(host, t);
    }).observe(read, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ['class', 'data-say'] });
  }
  function scanWidgets() {
    KINDS.forEach(k => document.querySelectorAll(k.ctl + ':not([data-vt])').forEach(c => addToggle(c, k)));
  }
  let scanQueued = false;
  function queueScan() {
    if (scanQueued) return;
    scanQueued = true;
    setTimeout(() => { scanQueued = false; scanWidgets(); }, 250);
  }

  /* ---------- 2. lessons ---------- */
  const LESSONS = 'article.cv-lesson, section.jsec.ps-lesson';
  /* boxes are read whole, once, so the paragraphs inside them are not read twice */
  const BOX = '.wwh-c, .pg-c, .rule, .tip, .warn, .fun, .exam, .modern, .scenario, .cl-put, .mlnote, .life, .qa-box, .jsec .box, .jsec .note';
  const READ = 'h2, h3, h4, p, li, .scene-h, .note > div, .fx-h, .fx-n, .vs-h, .vs-v, ' + BOX;
  const SKIP = '.cvz, .viz, .vz, .cv-code, pre, code, table, .tw, .z-read, .pl, .ck-nb, .walk, .cv-lnav, .cv-lno, .ps-lnav, .sec-num, ' +
    '.vt-lbar, .vx-say, .py-dlrow, details.deep:not([open]) .deep-b, details:not([open]) > :not(summary), .algo, .cai-log, .codewrap, .codebar, .out, .err, [hidden], [aria-hidden="true"]';
  function chunks(lesson) {
    const out = [];
    lesson.querySelectorAll(READ).forEach(n => {
      if (n.closest(SKIP)) return;
      const up = n.parentElement && n.parentElement.closest(BOX + ', li, .note');
      if (up && lesson.contains(up)) return;
      const t = (n.innerText || '').replace(/\s+/g, ' ').trim();
      if (t.length > 1 && spoken(t)) out.push({ n, t });
    });
    /* a lesson may carry a background talk (div.vt-talk, hidden on the page): the story behind the lesson, read
       first, while the lesson title is marked */
    const h = lesson.querySelector(':scope > h2') || lesson.querySelector('h2');
    const talks = [...lesson.querySelectorAll(':scope > .vt-talk')].map(n => (n.textContent || '').replace(/\s+/g, ' ').trim()).filter(t => t && spoken(t));
    /* long speech is cut short by some browser voices, so the talk is spoken a few sentences at a time */
    const parts = [];
    talks.forEach(t => (t.match(/[^.!?]+[.!?]+(\s|$)|[^.!?]+$/g) || [t]).forEach(x => {
      const last = parts[parts.length - 1];
      if (last && last.length + x.length < 260) parts[parts.length - 1] = (last + ' ' + x.trim()).trim(); else parts.push(x.trim());
    }));
    return parts.filter(Boolean).map(t => ({ n: h || lesson, t })).concat(out);
  }
  function addListen(lesson) {
    if (lesson.querySelector(':scope > .vt-lbar')) return;
    const h = lesson.querySelector(':scope > h2') || lesson.querySelector('h2');
    if (!h) return;
    const bar = document.createElement('div');
    bar.className = 'vt-lbar';
    bar.innerHTML = '<button type="button" class="vt-listen" aria-pressed="false">Listen to this lesson</button>' +
      '<label class="vt-rate">Speed <select><option value="0.8">Slow</option><option value="0.95">Normal</option><option value="1.15">Fast</option></select></label>' +
      '<span class="vt-lnote">' + (lesson.querySelector(':scope > .vt-talk') ? 'Starts with the background story of this lesson, then reads the explanations aloud. Code and tables are skipped.' : 'Reads the explanations aloud. Code and tables are skipped.') + '</span>';
    h.insertAdjacentElement('afterend', bar);
    const sel = bar.querySelector('select');
    sel.value = String(RATES.reduce((a, b) => Math.abs(b - rate) < Math.abs(a - rate) ? b : a, 0.95));
    sel.addEventListener('change', () => {
      rate = +sel.value;
      store.set('vt-voice-rate', String(rate));
      document.querySelectorAll('.vt-rate select').forEach(s => { s.value = sel.value; });
    });
    const btn = bar.querySelector('.vt-listen');
    btn.addEventListener('click', () => {
      if (btn.classList.contains('on')) { stopAll(); return; }
      stopAll();
      const run = lessonRun;
      const parts = chunks(lesson);
      btn.classList.add('on'); btn.textContent = 'Stop reading'; btn.setAttribute('aria-pressed', 'true');
      let i = 0;
      const next = () => {
        if (run !== lessonRun) return;
        lesson.querySelectorAll('.vt-reading').forEach(x => x.classList.remove('vt-reading'));
        if (i >= parts.length) { stopLesson(btn); return; }
        const p = parts[i++];
        p.n.classList.add('vt-reading');
        const r = p.n.getBoundingClientRect();
        if (r.top < 90 || r.bottom > innerHeight) p.n.scrollIntoView({ block: 'center', behavior: 'smooth' });
        say(p.t, next);
      };
      next();
    });
  }
  function stopLesson(btn) {
    btn.classList.remove('on'); btn.textContent = 'Listen to this lesson'; btn.setAttribute('aria-pressed', 'false');
    const lesson = btn.closest(LESSONS);
    if (lesson) lesson.querySelectorAll('.vt-reading').forEach(x => x.classList.remove('vt-reading'));
  }

  /* the background talks of a page that keeps them outside the page: data/talk/<subject>/<page>.js calls
     window.VT_TALK('<subject>/<page>', { 'lesson id': 'talk', ... }) */
  function placeTalks(map) {
    document.querySelectorAll(LESSONS).forEach(l => {
      const t = l.id && map[l.id];
      if (!t || l.querySelector(':scope > .vt-talk')) return;
      const d = document.createElement('div');
      d.className = 'vt-talk';
      d.hidden = true;
      d.textContent = t;
      l.appendChild(d);
      const note = l.querySelector(':scope > .vt-lbar .vt-lnote');
      if (note) note.textContent = 'Starts with the background story of this lesson, then reads the explanations aloud. Code and tables are skipped.';
    });
  }
  const TALKS = {};
  window.VT_TALK = (key, map) => { TALKS[key] = map; if (key === pageKey) placeTalks(map); };
  const pm = decodeURIComponent(location.pathname).match(/\/content\/([^/]+)\/([^/]+)\.html$/);
  const pageKey = pm ? pm[1] + '/' + pm[2] : '';
  function loadTalks() {
    if (!pageKey || !here || document.querySelector('.vt-talk') || !document.querySelector(LESSONS)) return; /* a page without lessons has no talks */
    const s = document.createElement('script');
    s.src = new URL('../data/talk/' + pageKey + '.js', here).href;
    s.async = true;
    s.onerror = () => s.remove();
    document.head.appendChild(s);
  }

  function start() {
    document.querySelectorAll(LESSONS).forEach(addListen);
    loadTalks();
    if (TALKS[pageKey]) placeTalks(TALKS[pageKey]);
    scanWidgets();
    /* animations mount when their lesson opens, so look again whenever new controls appear */
    new MutationObserver(ms => {
      for (const m of ms) {
        if (m.type === 'attributes' || [...m.addedNodes].some(n => n.nodeType === 1 && (n.matches('.vz-ctl, .z-body, .vz') || n.querySelector && n.querySelector('.vz-ctl, .z-ctl')))) { queueScan(); return; }
      }
    }).observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ['data-on'] });
    setTimeout(scanWidgets, 800);
    /* stop talking when the reader moves to another lesson or tab, starts the narrator, or leaves the page */
    document.addEventListener('click', e => {
      if (e.target.closest('.cv-tab, .cv-stepper a, .cv-lnav a, .cv-lnav button, .ps-tab, .ps-stepper, .ps-lnav, .vx-fab, .vx-panel, .vx-say, #listenAll')) stopAll();
    });
    addEventListener('pagehide', () => synth.cancel());
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
