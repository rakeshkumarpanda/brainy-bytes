/* ===== Selenium chapter pages: examples in Java, Python and JavaScript with a note for each line =====
   The build (tools/se-build/sekit.py) writes each example as .se-tri with one .se-pane per language. Inside a pane,
   lines that have a note carry data-n, and the notes sit in a hidden <ol class="se-notes">.
   The chosen language is shared by every example on every Selenium page. "Explain line by line" walks the notes. */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const HL = { java: 'java', py: 'py', js: 'js' };
  const NAME = { java: 'Java', py: 'Python', js: 'JavaScript' };
  let lang = 'java';
  try { lang = localStorage.getItem('se-lang') || 'java'; } catch (e) { /* storage unavailable */ }
  if (!NAME[lang]) lang = 'java';

  function paintCode() {
    if (typeof LEARN === 'undefined') return;
    $$('.se-tri .se-pane').forEach(p => {
      const l = HL[p.dataset.lang];
      $$('.se-src .ln', p).forEach(ln => { const t = ln.textContent; ln.innerHTML = t.trim() ? LEARN.hl(t, l) : ' '; });
    });
    $$('.se-hl').forEach(pre => {
      const l = HL[pre.dataset.hl] || pre.dataset.hl;
      pre.innerHTML = pre.textContent.split('\n').map(t => `<span class="ln">${t.trim() ? LEARN.hl(t, l) : ' '}</span>`).join('');
    });
  }

  const paneOf = box => box.classList.contains('se-solo') ? $('.se-pane', box) : $(`.se-pane[data-lang="${lang}"]`, box);
  function setLang(l) {
    lang = l;
    try { localStorage.setItem('se-lang', l); } catch (e) { /* storage unavailable */ }
    $$('.se-tri:not(.se-solo)').forEach(box => {
      $$('.se-lt', box).forEach(b => { const on = b.dataset.lang === l; b.classList.toggle('on', on); b.setAttribute('aria-selected', on); });
      $$('.se-pane', box).forEach(p => { p.hidden = p.dataset.lang !== l; });
      if (box.classList.contains('walking')) walk(box, 0);
      else close(box);
    });
  }

  /* every note of the visible pane, in file order: [{ file, line element, n, text }] */
  function notes(box) {
    const pane = paneOf(box);
    const out = [];
    $$('.se-file', pane).forEach(f => {
      const lines = $$('.se-src .ln', f);
      $$('.se-notes li', f).forEach(li => out.push({ file: $('.se-fname', f).textContent, el: lines[+li.dataset.n - 1], n: +li.dataset.n, html: li.innerHTML }));
    });
    return out;
  }
  function close(box) {
    box.classList.remove('walking');
    $$('.se-ex, .se-allnotes', box).forEach(e => e.remove());
    $$('.ln.cur', box).forEach(l => l.classList.remove('cur'));
    const b = $('.se-walk', box); if (b) { b.classList.remove('on'); b.textContent = 'Explain line by line'; }
    stop(box);
  }
  function stop(box) { if (box._t) { clearInterval(box._t); box._t = null; } const p = $('.se-ex .play', box); if (p) p.textContent = 'Play'; }

  function walk(box, i) {
    const list = notes(box);
    if (!list.length) return;
    i = Math.max(0, Math.min(list.length - 1, i));
    box._i = i;
    box.classList.add('walking');
    const b = $('.se-walk', box); b.classList.add('on'); b.textContent = 'Close the notes';
    const pane = paneOf(box);
    let ex = $('.se-ex', pane);
    if (!ex) {
      $$('.se-ex, .se-allnotes', box).forEach(e => e.remove());
      ex = document.createElement('div');
      ex.className = 'se-ex';
      ex.setAttribute('aria-live', 'polite');
      $$('.se-file', pane).pop().after(ex);
    }
    const it = list[i];
    $$('.ln.cur', box).forEach(l => l.classList.remove('cur'));
    if (it.el) {
      it.el.classList.add('cur');
      const pre = it.el.parentElement;
      pre.scrollTop = Math.max(0, it.el.offsetTop - pre.clientHeight / 2);
    }
    const multi = $$('.se-file', pane).length > 1;
    ex.innerHTML = `<div class="se-exn">${multi ? esc(it.file) + ' · ' : ''}Line ${it.n}</div><div class="se-ext">${it.html}</div>
      <div class="se-exl">${esc(it.el ? it.el.textContent : '')}</div>
      <div class="se-exc"><button type="button" class="first">First</button><button type="button" class="back">Back</button><button type="button" class="pri next">Next line</button><button type="button" class="play">Play</button><button type="button" class="all">Show every note</button><span class="se-exp">Note ${i + 1} of ${list.length} in ${NAME[pane.dataset.lang]}</span></div>`;
    $('.first', ex).onclick = () => { stop(box); walk(box, 0); };
    $('.back', ex).onclick = () => { stop(box); walk(box, box._i - 1); };
    $('.next', ex).onclick = () => { stop(box); walk(box, box._i + 1); };
    $('.play', ex).textContent = box._t ? 'Pause' : 'Play';
    $('.play', ex).onclick = () => {
      if (box._t) { stop(box); return; }
      if (box._i >= list.length - 1) walk(box, 0);
      $('.se-ex .play', box).textContent = 'Pause';
      box._t = setInterval(() => { if (!box.isConnected || box._i >= list.length - 1) { stop(box); return; } walk(box, box._i + 1); }, 2600);
    };
    $('.all', ex).onclick = () => {
      const old = $('.se-allnotes', pane);
      if (old) { old.remove(); return; }
      const ol = document.createElement('ol');
      ol.className = 'se-allnotes';
      ol.innerHTML = list.map(x => `<li><b>${multi ? esc(x.file) + ', ' : ''}line ${x.n}:</b> ${x.html}</li>`).join('');
      ex.after(ol);
    };
  }

  document.addEventListener('click', e => {
    const lt = e.target.closest('.se-lt');
    if (lt) { setLang(lt.dataset.lang); return; }
    const w = e.target.closest('.se-walk');
    if (w) { const box = w.closest('.se-tri'); if (box.classList.contains('walking')) close(box); else walk(box, 0); return; }
    const c = e.target.closest('.se-copy');
    if (c) {
      const pane = paneOf(c.closest('.se-tri'));
      const text = $$('.se-file', pane).map(f => $$('.se-src .ln', f).map(l => l.textContent.replace(/^ $/, '')).join('\n')).join('\n\n');
      const done = () => { c.textContent = 'Copied'; setTimeout(() => { c.textContent = 'Copy'; }, 1200); };
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, done); else done();
      return;
    }
    const ln = e.target.closest('.se-tri .se-src .ln[data-n]');
    if (ln) {
      const box = ln.closest('.se-tri');
      const k = notes(box).findIndex(x => x.el === ln);
      if (k >= 0) { stop(box); walk(box, k); }
    }
  });

  paintCode();
  setLang(lang);
})();
