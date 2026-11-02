/* ===== Quiz and calculation practice, shared by every topic page =====
   LEARN.quizHtml(items, opts) and LEARN.calcHtml(items, opts) return HTML for a card.
   LEARN.wire() turns on the buttons once for the whole page.
   Quiz item: { lv: 'e'|'m'|'h'|'x', q: 'question html', code?: 'source', o: ['option html', ...], a: index of the right option, hint: 'html', why: 'html' }
   Calc item: { lv, q, code?, ans: 'expected answer', alt?: ['other accepted forms'], unit?: 'text after the box', tol?: number, hint, steps: ['html', ...] }
   Inside steps, wrap an equation in <span class="eq">...</span> to show it on its own line. */
const LEARN = (() => {
  const LV = { e: ['Easy', '🌱', 'easy'], m: ['Medium', '🌿', 'med'], h: ['Hard', '🔥', 'hard'], x: ['Expert', '🧠', 'exp'] };
  const ORDER = ['e', 'm', 'h', 'x'];
  const KEYS = 'ABCDEFGH';
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const KW = {
    java: 'abstract assert boolean break byte case catch char class const continue default do double else enum extends final finally float for goto if implements import instanceof int interface long native new package private protected public return short static strictfp super switch synchronized this throw throws transient try var void volatile while true false null record yield sealed permits',
    py: 'and as assert break class continue def del elif else except False finally for from global if import in is lambda None nonlocal not or pass raise return True try while with yield print len range',
    js: 'break case catch class const continue debugger default delete do else export extends false finally for function if import in instanceof let new null return super switch this throw true try typeof undefined var void while with yield of async await'
  };
  const kwSets = {};
  function hl(code, lang = 'java') {
    const kws = kwSets[lang] || (kwSets[lang] = new Set((KW[lang] || KW.java).split(' ')));
    const comment = lang === 'py' ? /#[^\n]*/y : /\/\/[^\n]*|\/\*[\s\S]*?\*\//y;
    let out = '', i = 0;
    const tok = [[comment, 'c'], [/"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*'/y, 's'], [/\b\d[\d_]*(?:\.\d+)?(?:[eE][+-]?\d+)?[lLfFdD]?\b|\b0[xX][0-9a-fA-F_]+[lL]?\b/y, 'n'], [/@[A-Za-z]+/y, 'a'], [/[A-Za-z_$][\w$]*/y, 'w']];
    outer: while (i < code.length) {
      for (const [re, cls] of tok) {
        re.lastIndex = i;
        const m = re.exec(code);
        if (m && m.index === i && m[0].length) {
          const t = esc(m[0]);
          if (cls === 'w') out += kws.has(m[0]) ? `<span class="k">${t}</span>` : (/^[A-Z]/.test(m[0]) ? `<span class="t">${t}</span>` : t);
          else out += `<span class="${cls}">${t}</span>`;
          i += m[0].length;
          continue outer;
        }
      }
      out += esc(code[i]); i++;
    }
    return out;
  }
  const codeHtml = (c, lang) => c ? `<pre class="lq-code">${hl(c, lang)}</pre>` : '';
  const levels = items => ORDER.filter(l => items.some(it => it.lv === l));

  function tabs(items, kind) {
    return `<div class="lq-tabs" role="tablist">${levels(items).map((l, n) => {
      const c = items.filter(it => it.lv === l).length;
      return `<button class="lq-tab lv-${LV[l][2]}${n ? '' : ' on'}" role="tab" data-lv="${l}" aria-selected="${!n}"><span class="lq-tem">${LV[l][1]}</span><span>${LV[l][0]}</span><span class="lq-tct" data-kind="${kind}">0/${c}</span></button>`;
    }).join('')}</div>`;
  }
  function head(title, sub, total, icon) {
    return `<div class="lq-head"><div class="lq-ic">${icon}</div><div class="lq-ht"><h3>${title}</h3><p class="lq-sub">${sub}</p></div><div class="lq-score" aria-live="polite"><b>0</b><span>/${total}</span><small>correct</small></div></div>`;
  }

  function quizHtml(items, opts = {}) {
    if (!items || !items.length) return '';
    const lang = opts.lang || 'java';
    const panes = levels(items).map((l, n) => {
      const list = items.filter(it => it.lv === l);
      return `<div class="lq-pane" data-lv="${l}"${n ? ' hidden' : ''}>${list.map((it, k) => `
        <div class="lq-item" data-a="${it.a}">
          <div class="lq-q"><span class="lq-n lv-${LV[l][2]}">Q${k + 1}</span><div>${it.q}</div></div>
          ${codeHtml(it.code, it.lang || lang)}
          <div class="lq-opts">${it.o.map((o, j) => `<button class="lq-opt" data-k="${j}"><span class="lq-key">${KEYS[j]}</span><span class="lq-ot">${o}</span></button>`).join('')}</div>
          <div class="lq-tools"><button class="lq-hintbtn">💡 Hint</button></div>
          <div class="lq-hint" hidden>${it.hint || 'Read the question once more, slowly.'}</div>
          <div class="lq-why" hidden><div class="lq-verdict"></div><div class="lq-wt">${it.why || ''}</div></div>
        </div>`).join('')}
        <div class="lq-foot"><button class="lq-reset">↺ Try this level again</button></div>
      </div>`;
    }).join('');
    return `<div class="lq quiz" data-kind="quiz">${head(opts.title || 'Quiz time', opts.sub || 'Four levels from easy to expert. Every answer comes with the reason behind it.', items.length, '🎯')}${tabs(items, 'quiz')}${panes}</div>`;
  }

  function calcHtml(items, opts = {}) {
    if (!items || !items.length) return '';
    const lang = opts.lang || 'java';
    const panes = levels(items).map((l, n) => {
      const list = items.filter(it => it.lv === l);
      return `<div class="lq-pane" data-lv="${l}"${n ? ' hidden' : ''}>${list.map((it, k) => `
        <div class="lc-item" data-ans="${esc(it.ans)}" data-alt="${esc(JSON.stringify(it.alt || []))}"${it.tol != null ? ` data-tol="${it.tol}"` : ''}>
          <div class="lq-q"><span class="lq-n lv-${LV[l][2]}">C${k + 1}</span><div>${it.q}</div></div>
          ${codeHtml(it.code, it.lang || lang)}
          <div class="lc-row"><input class="lc-in" type="text" autocomplete="off" spellcheck="false" placeholder="Your answer" aria-label="Your answer">${it.unit ? `<span class="lc-unit">${it.unit}</span>` : ''}<button class="lc-check">Check</button></div>
          <div class="lc-fb" aria-live="polite"></div>
          <div class="lq-tools"><button class="lq-hintbtn">💡 Hint</button><button class="lc-show">📝 Show the working</button></div>
          <div class="lq-hint" hidden>${it.hint || ''}</div>
          <div class="lc-work" hidden><div class="lc-ans">Answer: <b>${esc(it.ans)}</b>${it.unit ? ' ' + it.unit : ''}</div><ol class="lc-steps">${(it.steps || []).map(s => `<li>${s}</li>`).join('')}</ol></div>
        </div>`).join('')}
        <div class="lq-foot"><button class="lq-reset">↺ Try this level again</button></div>
      </div>`;
    }).join('');
    return `<div class="lq calc" data-kind="calc">${head(opts.title || 'Number crunch', opts.sub || 'Work it out, type your answer and press Check. Stuck? Peek at the hint, then the full working.', items.length, '🧮')}${tabs(items, 'calc')}${panes}</div>`;
  }

  /* ----- answer checking for calculations ----- */
  const norm = s => String(s).trim().toLowerCase().replace(/^["'`]|["'`]$/g, '').replace(/\s+/g, ' ').replace(/(\d),(?=\d{3}\b)/g, '$1');
  function num(s) {
    const t = norm(s).replace(/\s/g, '');
    if (/^[-+]?\d+\/\d+$/.test(t)) { const [a, b] = t.split('/'); return +a / +b; }
    if (/^[-+]?(\d+\.?\d*|\.\d+)(e[-+]?\d+)?[lfd]?$/.test(t)) return parseFloat(t);
    return NaN;
  }
  function matches(input, item) {
    const want = [item.dataset.ans, ...JSON.parse(item.dataset.alt || '[]')];
    const tol = item.dataset.tol != null ? +item.dataset.tol : null;
    const a = norm(input);
    if (!a) return null;
    for (const w of want) {
      if (norm(w) === a || norm(w).replace(/\s/g, '') === a.replace(/\s/g, '')) return true;
      const x = num(input), y = num(w);
      if (!isNaN(x) && !isNaN(y)) {
        const t = tol != null ? tol : 1e-9 * Math.max(1, Math.abs(y));
        if (Math.abs(x - y) <= t) return true;
      }
    }
    return false;
  }

  /* ----- scoring ----- */
  function refresh(box) {
    const kind = box.dataset.kind;
    const sel = kind === 'quiz' ? '.lq-item' : '.lc-item';
    const all = box.querySelectorAll(sel);
    const good = box.querySelectorAll(sel + '.right').length;
    box.querySelector('.lq-score b').textContent = good;
    box.querySelectorAll('.lq-tab').forEach(t => {
      const pane = box.querySelector(`.lq-pane[data-lv="${t.dataset.lv}"]`);
      const items = pane.querySelectorAll(sel), r = pane.querySelectorAll(sel + '.right').length;
      t.querySelector('.lq-tct').textContent = `${r}/${items.length}`;
      const full = r === items.length;
      if (full && !t.classList.contains('done') && typeof FUN !== 'undefined') {
        const b = t.getBoundingClientRect();
        FUN.confetti(b.left + b.width / 2, b.top + b.height / 2, 60);
      }
      t.classList.toggle('done', full);
    });
    return { good, total: all.length };
  }
  function bump(el) { el.classList.remove('bump'); void el.offsetWidth; el.classList.add('bump'); }

  function onClick(e) {
    const box = e.target.closest('.lq');
    if (!box) return;
    const tab = e.target.closest('.lq-tab');
    if (tab) {
      box.querySelectorAll('.lq-tab').forEach(t => { const on = t === tab; t.classList.toggle('on', on); t.setAttribute('aria-selected', on); });
      box.querySelectorAll('.lq-pane').forEach(p => { p.hidden = p.dataset.lv !== tab.dataset.lv; });
      return;
    }
    const hb = e.target.closest('.lq-hintbtn');
    if (hb) { const h = hb.closest('.lq-item,.lc-item').querySelector('.lq-hint'); h.hidden = !h.hidden; hb.classList.toggle('on', !h.hidden); return; }
    const opt = e.target.closest('.lq-opt');
    if (opt) {
      const it = opt.closest('.lq-item');
      if (it.classList.contains('answered')) return;
      const k = +opt.dataset.k, a = +it.dataset.a;
      it.classList.add('answered', k === a ? 'right' : 'wrong');
      it.querySelectorAll('.lq-opt').forEach(b => { b.disabled = true; const j = +b.dataset.k; if (j === a) b.classList.add('ok'); else if (j === k) b.classList.add('bad'); });
      const why = it.querySelector('.lq-why');
      why.querySelector('.lq-verdict').innerHTML = k === a ? '✅ <b>Correct!</b>' : `❌ <b>Not quite.</b> The right answer is <b>${KEYS[a]}</b>.`;
      why.hidden = false;
      bump(box.querySelector('.lq-score'));
      refresh(box);
      return;
    }
    const chk = e.target.closest('.lc-check');
    if (chk) { check(chk.closest('.lc-item')); return; }
    const show = e.target.closest('.lc-show');
    if (show) { const w = show.closest('.lc-item').querySelector('.lc-work'); w.hidden = !w.hidden; show.classList.toggle('on', !w.hidden); return; }
    const rs = e.target.closest('.lq-reset');
    if (rs) {
      const pane = rs.closest('.lq-pane');
      pane.querySelectorAll('.lq-item').forEach(it => {
        it.classList.remove('answered', 'right', 'wrong');
        it.querySelectorAll('.lq-opt').forEach(b => { b.disabled = false; b.classList.remove('ok', 'bad'); });
        it.querySelector('.lq-why').hidden = true; it.querySelector('.lq-hint').hidden = true;
      });
      pane.querySelectorAll('.lc-item').forEach(it => {
        it.classList.remove('right', 'wrong'); it.dataset.tries = 0;
        const inp = it.querySelector('.lc-in'); inp.value = ''; inp.disabled = false;
        it.querySelector('.lc-fb').innerHTML = ''; it.querySelector('.lc-work').hidden = true; it.querySelector('.lq-hint').hidden = true;
        it.querySelector('.lc-check').disabled = false;
      });
      pane.querySelectorAll('.on').forEach(b => { if (!b.classList.contains('lq-tab')) b.classList.remove('on'); });
      const tab = box.querySelector(`.lq-tab[data-lv="${pane.dataset.lv}"]`); if (tab) tab.classList.remove('done');
      refresh(box);
    }
  }
  function check(it) {
    const inp = it.querySelector('.lc-in'), fb = it.querySelector('.lc-fb');
    const r = matches(inp.value, it);
    if (r === null) { fb.innerHTML = '<span class="lc-meh">✏️ Type an answer first.</span>'; inp.focus(); return; }
    if (r) {
      it.classList.remove('wrong'); it.classList.add('right');
      fb.innerHTML = '<span class="lc-yes">✅ <b>Correct!</b> Here is the full working, so you can compare it with yours.</span>';
      inp.disabled = true; it.querySelector('.lc-check').disabled = true;
      it.querySelector('.lc-work').hidden = false; it.querySelector('.lc-show').classList.add('on');
    } else {
      const n = (+it.dataset.tries || 0) + 1; it.dataset.tries = n;
      it.classList.add('wrong');
      fb.innerHTML = `<span class="lc-no">❌ <b>Not yet.</b> ${n === 1 ? 'Check each step and try again, or open the hint.' : 'Open the working to see each step.'}</span>`;
      if (n >= 2) bump(it.querySelector('.lc-show'));
    }
    refresh(it.closest('.lq'));
  }
  let wired = false;
  function wire() {
    if (wired) return;
    wired = true;
    document.addEventListener('click', onClick);
    document.addEventListener('keydown', e => { if (e.key === 'Enter' && e.target.classList && e.target.classList.contains('lc-in')) check(e.target.closest('.lc-item')); });
    /* a shown working belongs to the old answer, so typing a new answer hides it again */
    document.addEventListener('input', e => {
      const inp = e.target;
      if (!inp.classList || !inp.classList.contains('lc-in')) return;
      const it = inp.closest('.lc-item');
      if (!it) return;
      const w = it.querySelector('.lc-work'), sh = it.querySelector('.lc-show'), fb = it.querySelector('.lc-fb');
      if (w) w.hidden = true;
      if (sh) sh.classList.remove('on');
      if (fb) fb.innerHTML = '';
      it.classList.remove('wrong');
    });
  }
  return { quizHtml, calcHtml, wire, hl, matches, LV };
})();
