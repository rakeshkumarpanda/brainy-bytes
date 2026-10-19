/* ===== Listen mode: a friendly narrator reads the lesson aloud in six languages =====
   VOICE.setup({ title, segments }) sets what can be read. Each segment is
   { id?: 'element id it describes', h?: 'short label', en: '...', hi: '...', kn: '...', or: '...', ar: '...', de: '...' }.
   Elements with data-say="segment id" get a small speaker button in their heading.
   It uses the speech voices already installed in the browser and prefers a female voice. */
const VOICE = (() => {
  const LANGS = [
    { k: 'en', native: 'English', bcp: 'en-US', listen: 'Listen' },
    { k: 'hi', native: 'हिन्दी', bcp: 'hi-IN', listen: 'सुनिए' },
    { k: 'kn', native: 'ಕನ್ನಡ', bcp: 'kn-IN', listen: 'ಆಲಿಸಿ' },
    { k: 'or', native: 'ଓଡ଼ିଆ', bcp: 'or-IN', listen: 'ଶୁଣନ୍ତୁ' },
    { k: 'ar', native: 'العربية', bcp: 'ar-SA', listen: 'استمع', rtl: true },
    { k: 'de', native: 'Deutsch', bcp: 'de-DE', listen: 'Anhören' }
  ];
  const NAMES = { en: 'English', hi: 'Hindi', kn: 'Kannada', or: 'Odia', ar: 'Arabic', de: 'German' };
  const FEMALE = new Set('female woman girl samantha zira aria jenny ava emma michelle sonia libby maisie natasha clara swara kalpana heera neerja sapna subhasini hoda zariyah salma amina fatima layla laila mariam rana katja hedda amala seraphina tanja louisa marlene vicki anna petra helena karen moira tessa fiona victoria allison susan serena kate lekha veena kanya aditi raveena shruti kajal ananya isha lisa sara sarah amy joanna kendra kimberly salli ivy ruth olivia nicole marie'.split(' '));
  const MALE = new Set('male man david mark guy ryan prabhat madhur gagan sukant hamed shakir conrad killian kasper ralf daniel alex fred thomas majed maged tarik rishi aaron arthur george james christopher eric roger steffan brian andrew florian jonas bernd christoph kai hemant ravi naayf hans markus stefan'.split(' '));
  const GOOD = new Set('natural online neural premium enhanced'.split(' '));
  const synth = 'speechSynthesis' in window ? window.speechSynthesis : null;
  const store = { get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage unavailable */ } } };
  const S = { lang: store.get('lh-voice-lang') || 'en', rate: +(store.get('lh-voice-rate') || 0.95), full: false, segs: [], title: '', si: 0, ti: 0, playing: false, run: 0, follow: true, voiceName: '', single: false };
  if (!LANGS.some(l => l.k === S.lang)) S.lang = 'en';
  if (!(S.rate >= 0.6 && S.rate <= 1.4)) S.rate = 0.95;
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const L = k => LANGS.find(l => l.k === k);

  /* ----- choosing a voice ----- */
  function score(v) {
    const toks = v.name.toLowerCase().split(/[^a-zऀ-෿]+/).filter(Boolean);
    let s = 0;
    if (toks.some(t => FEMALE.has(t))) s += 6;
    if (toks.some(t => MALE.has(t))) s -= 8;
    if (/google/i.test(v.name) && !toks.includes('male')) s += 3;
    if (toks.some(t => GOOD.has(t))) s += 3;
    if (/en-(us|gb|in)/i.test(v.lang)) s += 1;
    return s;
  }
  function voicesFor(k) {
    if (!synth) return [];
    return synth.getVoices().filter(v => v.lang.replace('_', '-').toLowerCase().split('-')[0] === k).sort((a, b) => score(b) - score(a));
  }
  function pickVoice() {
    const list = voicesFor(S.lang);
    const saved = store.get('lh-voice-' + S.lang);
    return list.find(v => v.name === saved) || list[0] || null;
  }

  /* ----- text handling ----- */
  function sentences(text) {
    const t = String(text || '').replace(/\s+/g, ' ').trim();
    const out = [];
    const push = p => {
      p = p.trim();
      while (p.length > 220) { const c = p.lastIndexOf(',', 200) > 60 ? p.lastIndexOf(',', 200) + 1 : 200; out.push(p.slice(0, c).trim()); p = p.slice(c).trim(); }
      if (p) out.push(p);
    };
    const re = /[.!?।॥؟]+["')\]]*\s+/g;
    let m, last = 0;
    while ((m = re.exec(t))) { push(t.slice(last, m.index + m[0].length)); last = m.index + m[0].length; }
    push(t.slice(last));
    return out;
  }
  function plainOf(el) {
    if (!el) return '';
    const c = el.cloneNode(true);
    c.querySelectorAll('pre, code, .lq, .vx-say, script, style, svg, table, .out, button').forEach(x => x.remove());
    return c.textContent.replace(/\s+/g, ' ').trim();
  }
  function segText(seg) {
    if (!seg) return '';
    if (S.lang === 'en' && S.full && seg.id) { const el = document.getElementById(seg.id); const t = plainOf(el); if (t) return t; }
    return seg[S.lang] || seg.en || '';
  }

  /* ----- the panel ----- */
  let fab, panel;
  function build() {
    if (fab) return;
    fab = document.createElement('button');
    fab.className = 'vx-fab';
    fab.type = 'button';
    fab.setAttribute('aria-label', 'Open listen mode');
    document.body.appendChild(fab);
    panel = document.createElement('div');
    panel.className = 'vx-panel';
    panel.hidden = true;
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', 'Listen mode');
    panel.innerHTML = `
      <div class="vx-top"><div class="vx-face" aria-hidden="true"><svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="22" fill="#ffd9c2"/><path d="M6 22c0-12 8-19 18-19s18 7 18 19c-3-6-8-9-18-9S9 16 6 22z" fill="#5b3a29"/><circle cx="17" cy="25" r="2.6" fill="#1b2a44"/><circle cx="31" cy="25" r="2.6" fill="#1b2a44"/><circle cx="13" cy="31" r="3" fill="#ff9fb0" opacity=".6"/><circle cx="35" cy="31" r="3" fill="#ff9fb0" opacity=".6"/><path class="vx-mouth" d="M19 32q5 4 10 0" stroke="#c2445a" stroke-width="2.4" fill="none" stroke-linecap="round"/></svg></div>
        <div class="vx-tt"><b>Hi, I am Mira</b><span class="vx-sub">I will read this lesson to you</span></div>
        <button class="vx-x" type="button" aria-label="Close listen mode">✕</button></div>
      <div class="vx-langs" role="radiogroup" aria-label="Language">${LANGS.map(l => `<button type="button" role="radio" data-k="${l.k}" lang="${l.k}">${l.native}</button>`).join('')}</div>
      <div class="vx-ctrl">
        <button type="button" class="vx-b" data-act="prev" title="Previous part">⏮</button>
        <button type="button" class="vx-b vx-play" data-act="play" title="Play or pause">▶</button>
        <button type="button" class="vx-b" data-act="stop" title="Stop">⏹</button>
        <button type="button" class="vx-b" data-act="next" title="Next part">⏭</button>
        <label class="vx-rate" title="Speaking speed">🐢<input type="range" min="0.6" max="1.4" step="0.05" aria-label="Speaking speed">🐇</label>
      </div>
      <div class="vx-where"></div>
      <div class="vx-cap" aria-live="polite"></div>
      <details class="vx-more"><summary>Voice settings</summary>
        <label class="vx-row">Voice <select class="vx-voice" aria-label="Voice"></select></label>
        <label class="vx-row vx-fullrow"><input type="checkbox" class="vx-full"> In English, read the full notes of each part instead of the short summary</label>
        <label class="vx-row"><input type="checkbox" class="vx-follow" checked> Scroll the page along with me</label>
      </details>
      <div class="vx-note"></div>`;
    document.body.appendChild(panel);
    fab.onclick = () => toggle(true);
    panel.querySelector('.vx-x').onclick = () => toggle(false);
    panel.addEventListener('click', e => {
      const lb = e.target.closest('.vx-langs button');
      if (lb) { setLang(lb.dataset.k); return; }
      const b = e.target.closest('.vx-b');
      if (!b) return;
      const act = b.dataset.act;
      if (act === 'play') S.playing ? pause() : play();
      else if (act === 'stop') stop();
      else if (act === 'next') jump(S.si + 1);
      else if (act === 'prev') jump(S.ti > 0 ? S.si : S.si - 1);
    });
    const rate = panel.querySelector('.vx-rate input');
    rate.value = S.rate;
    rate.oninput = () => { S.rate = +rate.value; store.set('lh-voice-rate', S.rate); };
    rate.onchange = () => { if (S.playing) speakNow(); };
    panel.querySelector('.vx-voice').onchange = e => { store.set('lh-voice-' + S.lang, e.target.value); if (S.playing) speakNow(); refreshNote(); };
    panel.querySelector('.vx-full').onchange = e => { S.full = e.target.checked; S.ti = 0; renderCap(); if (S.playing) speakNow(); };
    panel.querySelector('.vx-follow').onchange = e => { S.follow = e.target.checked; };
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && !panel.hidden) toggle(false); });
    if (synth) synth.addEventListener ? synth.addEventListener('voiceschanged', () => { fillVoices(); refreshNote(); }) : (synth.onvoiceschanged = () => { fillVoices(); refreshNote(); });
    setLang(S.lang, true);
  }
  function toggle(on) {
    panel.hidden = !on;
    fab.classList.toggle('open', on);
    if (on) { fillVoices(); refreshNote(); renderCap(); }
  }
  function fillVoices() {
    const sel = panel.querySelector('.vx-voice');
    const list = voicesFor(S.lang), cur = pickVoice();
    sel.innerHTML = list.length ? list.map(v => `<option value="${esc(v.name)}"${cur && v.name === cur.name ? ' selected' : ''}>${esc(v.name)}${score(v) > 4 ? ' ♀' : ''}</option>`).join('') : '<option value="">Device default</option>';
  }
  function refreshNote() {
    const note = panel.querySelector('.vx-note');
    if (!synth) { note.innerHTML = '🙈 This browser cannot speak out loud. You can still read along with the captions above.'; return; }
    const v = pickVoice();
    if (v) note.innerHTML = `🎙️ Voice: <b>${esc(v.name)}</b>`;
    else note.innerHTML = `⚠️ No ${NAMES[S.lang]} voice is installed on this device, so your browser may read in another accent or stay silent. Microsoft Edge offers free online ${NAMES[S.lang]} voices, or you can add one in your device's speech settings. The captions above are always there to read along.`;
  }
  function setLang(k, quiet) {
    S.lang = k;
    store.set('lh-voice-lang', k);
    const l = L(k);
    fab.innerHTML = `<span class="vx-fem">🎧</span><span class="vx-flbl">${l.listen}</span>`;
    panel.querySelectorAll('.vx-langs button').forEach(b => { const on = b.dataset.k === k; b.classList.toggle('on', on); b.setAttribute('aria-checked', on); });
    panel.querySelector('.vx-fullrow').hidden = k !== 'en';
    const cap = panel.querySelector('.vx-cap');
    cap.dir = l.rtl ? 'rtl' : 'ltr';
    cap.lang = k;
    fillVoices(); refreshNote();
    S.ti = 0;
    renderCap();
    if (!quiet && S.playing) speakNow();
  }

  /* ----- playing ----- */
  function current() { return sentences(segText(S.segs[S.si])); }
  function renderCap() {
    if (!panel) return;
    const seg = S.segs[S.si];
    const where = panel.querySelector('.vx-where');
    const cap = panel.querySelector('.vx-cap');
    if (!seg) { where.textContent = ''; cap.innerHTML = '<span class="vx-empty">Nothing to read on this page yet.</span>'; return; }
    where.innerHTML = `<span>Part ${S.si + 1} of ${S.segs.length}</span>${seg.h ? `<b>${esc(seg.h)}</b>` : ''}`;
    const ss = current();
    cap.innerHTML = ss.length ? ss.map((s, i) => `<span class="vx-s${i === S.ti && S.playing ? ' now' : ''}${i < S.ti && S.playing ? ' said' : ''}">${esc(s)} </span>`).join('') : `<span class="vx-empty">This part has no ${NAMES[S.lang]} text yet.</span>`;
    const now = cap.querySelector('.now');
    if (now) cap.scrollTop = Math.max(0, now.offsetTop - cap.offsetTop - 20);
    panel.querySelector('.vx-play').textContent = S.playing ? '⏸' : '▶';
    panel.classList.toggle('talking', S.playing);
    fab.classList.toggle('talking', S.playing);
    document.querySelectorAll('.vx-on').forEach(x => x.classList.remove('vx-on'));
    document.querySelectorAll('.vx-say.on').forEach(x => x.classList.remove('on'));
    if (S.playing && seg.id) {
      const el = document.getElementById(seg.id);
      if (el) el.classList.add('vx-on');
      document.querySelectorAll(`.vx-say[data-seg="${CSS.escape(seg.id)}"]`).forEach(x => x.classList.add('on'));
    }
  }
  function speakNow() {
    if (!synth) { renderCap(); return; }
    const run = ++S.run;
    synth.cancel();
    const ss = current();
    if (!ss.length) { setTimeout(() => { if (run === S.run && S.playing) advance(run); }, 400); renderCap(); return; }
    if (S.ti >= ss.length) S.ti = 0;
    renderCap();
    const u = new SpeechSynthesisUtterance(ss[S.ti]);
    const v = pickVoice();
    if (v) { u.voice = v; u.lang = v.lang; } else u.lang = L(S.lang).bcp;
    u.rate = S.rate;
    u.pitch = 1.12;
    u.onend = () => { if (run === S.run && S.playing) { S.ti++; if (S.ti < current().length) speakNow(); else advance(run); } };
    u.onerror = ev => {
      if (run !== S.run || !S.playing || ev.error === 'interrupted' || ev.error === 'canceled') return;
      /* the browser cannot speak right now: stop politely instead of racing through every part */
      S.playing = false; S.single = false;
      renderCap();
      panel.querySelector('.vx-note').innerHTML = `🙊 Your browser could not speak this part (${esc(ev.error || 'unknown reason')}). ${pickVoice() ? 'Try another voice in Voice settings.' : 'No ' + NAMES[S.lang] + ' voice seems to be installed. Microsoft Edge offers free online ' + NAMES[S.lang] + ' voices.'} The captions above are always there to read along.`;
    };
    /* Chrome sometimes needs a moment after cancel() before it accepts new speech */
    setTimeout(() => { if (run === S.run) synth.speak(u); }, 60);
  }
  function advance(run) {
    if (run !== S.run) return;
    if (S.single || S.si >= S.segs.length - 1) { S.playing = false; S.ti = 0; S.single = false; renderCap(); return; }
    S.si++; S.ti = 0;
    scrollToSeg();
    speakNow();
  }
  function scrollToSeg() {
    const seg = S.segs[S.si];
    if (!S.follow || !seg || !seg.id) return;
    const el = document.getElementById(seg.id);
    if (el) el.scrollIntoView({ behavior: (typeof FUN !== 'undefined' && FUN.reduce) ? 'auto' : 'smooth', block: 'start' });
  }
  function play() { if (!S.segs.length) return; S.playing = true; scrollToSeg(); speakNow(); }
  function pause() { S.playing = false; S.run++; if (synth) synth.cancel(); renderCap(); }
  function stop() { S.playing = false; S.run++; S.ti = 0; S.single = false; if (synth) synth.cancel(); renderCap(); }
  function jump(i) {
    if (!S.segs.length) return;
    S.si = Math.max(0, Math.min(S.segs.length - 1, i)); S.ti = 0;
    if (S.playing) { scrollToSeg(); speakNow(); } else renderCap();
  }
  function playSegment(id) {
    build();
    const i = S.segs.findIndex(s => s.id === id);
    if (i < 0) return;
    if (S.playing && S.si === i) { pause(); return; }
    S.si = i; S.ti = 0; S.single = true; S.playing = true;
    toggle(true);
    speakNow();
  }

  /* ----- speaker buttons inside the page ----- */
  function attach(root = document) {
    root.querySelectorAll('[data-say]').forEach(el => {
      if (el.querySelector(':scope .vx-say')) return;
      const h = el.querySelector('h1, h2, h3') || el;
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'vx-say';
      b.dataset.seg = el.dataset.say;
      b.title = 'Listen to this part';
      b.setAttribute('aria-label', 'Listen to this part');
      b.textContent = '🔊';
      b.onclick = e => { e.stopPropagation(); playSegment(el.dataset.say); };
      h.appendChild(b);
    });
  }

  function setup(opts = {}) {
    build();
    stop();
    S.segs = (opts.segments || []).filter(Boolean);
    S.title = opts.title || '';
    S.si = 0; S.ti = 0;
    panel.querySelector('.vx-sub').textContent = S.title ? `I will read "${S.title}" to you` : 'I will read this lesson to you';
    renderCap();
    attach(opts.root || document);
  }
  function playAll() { build(); toggle(true); stop(); S.si = 0; S.ti = 0; S.single = false; play(); }
  function open() { build(); toggle(true); }
  window.addEventListener('pagehide', () => { if (synth) synth.cancel(); });
  return { setup, attach, playSegment, playAll, open, play, pause, stop, setLang, LANGS, state: S, _score: score, _sentences: sentences };
})();
