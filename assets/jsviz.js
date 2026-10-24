/* ===== Animations written for the JavaScript chapters, added to the shared VIZ widgets =====
   <div class="viz" data-viz="lanes" data-k="key"></div>   PAGE.lanes[key] = { t, s, code, lanes: [names], steps: [{ l: line or [lines], v: [[items of lane 0], ...], m: message }] }
                                                           A step by step story told with code on the left and boxes on the right
                                                           (event loop, scopes, prototype chains, test hooks, auto-waiting).
   <div class="viz" data-viz="coerce"></div>               type two values and see ==, === and Object.is side by side
   <div class="viz" data-viz="arr"></div>                  map, filter, reduce, find, some, every and sort, one element at a time
   <div class="viz" data-viz="bubble"></div>               capture, target and bubble phases of a click
   <div class="viz" data-viz="wait"></div>                 a fixed sleep against an auto-waiting locator
   <div class="viz" data-viz="regex"></div>                a live regular expression tester */
(() => {
  const K = VIZ.kit, W = VIZ.widgets, esc = K.esc, $ = K.$;

  /* ---------- lanes: a generic step story ---------- */
  W.lanes = el => {
    const spec = (typeof PAGE !== 'undefined' && PAGE.lanes && PAGE.lanes[el.dataset.k]) || null;
    if (!spec) { el.textContent = 'Missing animation ' + el.dataset.k; return; }
    const b = K.shell(el, spec.t, spec.s || 'Press Play, or step with the arrows, and watch each box change.');
    const lines = (spec.code || '').split('\n');
    b.innerHTML = `<div class="${spec.code ? 'jv-grid2' : ''}">${spec.code ? `<pre class="jv-code">${lines.map((l, i) => `<div data-l="${i + 1}">${typeof LEARN !== 'undefined' ? LEARN.hl(l, 'js') : esc(l)}${l ? '' : ' '}</div>`).join('')}</pre>` : ''}<div class="jv-lanes">${spec.lanes.map((n, i) => `<div class="jv-lane"><b>${esc(n)}</b><div data-lane="${i}"></div></div>`).join('')}</div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const msg = $('.vz-msg', b);
    const show = f => {
      const st = f ? spec.steps[f - 1] : { v: spec.start || [], m: spec.m || 'Press ▶ Play to start.' };
      const on = new Set([].concat(st.l || []));
      b.querySelectorAll('.jv-code div').forEach(d => d.classList.toggle('on', on.has(+d.dataset.l)));
      const prev = f > 1 ? spec.steps[f - 2].v || [] : [];
      spec.lanes.forEach((_, i) => {
        const items = (st.v && st.v[i]) || [], before = prev[i] || [];
        b.querySelector(`[data-lane="${i}"]`).innerHTML = items.map(x => `<span class="jv-chip t${(spec.tone && spec.tone[i]) ?? i % 6}${before.includes(x) ? '' : ' new'}">${esc(x)}</span>`).join('');
      });
      msg.innerHTML = f ? `<b>Step ${f} of ${spec.steps.length}.</b> ${st.m}` : st.m;
    };
    const P = K.Player($('.vz-p', b), show, spec.ms || 1600);
    P.load(spec.steps.length + 1);
  };

  /* ---------- coerce: == against === against Object.is ---------- */
  function parse(src) {
    const s = src.trim();
    if (s === '') return { ok: false };
    try { return { ok: true, v: Function('"use strict"; return (' + s + ');')() }; } catch (e) { return { ok: false, e: e.message }; }
  }
  function show(v) {
    if (typeof v === 'string') return JSON.stringify(v);
    if (typeof v === 'bigint') return v + 'n';
    if (Object.is(v, -0)) return '-0';
    if (Array.isArray(v)) return '[' + v.map(show).join(', ') + ']';
    if (v && typeof v === 'object') { try { return JSON.stringify(v); } catch (e) { return '{…}'; } }
    return String(v);
  }
  function why(a, b) {
    const ta = typeof a, tb = typeof b;
    if (ta === tb && !(a === null) !== !(b === null)) return 'Different kinds of value with the same typeof. No conversion happens.';
    if (ta === tb) return 'Same type, so == behaves exactly like ===.' + (Number.isNaN(a) ? ' NaN is never equal to anything, even itself.' : '');
    if ((a === null || a === undefined) && (b === null || b === undefined)) return 'null and undefined are loosely equal to each other and to nothing else.';
    if (a === null || a === undefined || b === null || b === undefined) return 'null and undefined are only loosely equal to each other, so this is false.';
    if (ta === 'boolean' || tb === 'boolean') return 'A boolean is turned into a number first (true is 1, false is 0), then the comparison starts again.';
    if ((ta === 'number' && tb === 'string') || (ta === 'string' && tb === 'number')) return 'The string is turned into a number, then the two numbers are compared.';
    if (ta === 'object' || tb === 'object') return 'The object is turned into a primitive (valueOf, then toString), then the comparison starts again.';
    return 'The values are converted following the loose equality rules.';
  }
  W.coerce = el => {
    const b = K.shell(el, 'Equality playground', 'Type any two JavaScript values, such as 0, "0", [], null or NaN.');
    b.innerHTML = `<div class="vz-row"><label class="jv-lbl">Left <input class="jv-in" data-a value='"5"'></label><label class="jv-lbl">Right <input class="jv-in" data-b value="5"></label></div>
      <div class="vz-row" data-pre></div>
      <div class="tw"><table class="jt"><tr><th>Check</th><th>Result</th><th>Types</th></tr>
      <tr><td><code>a == b</code></td><td data-r="0"></td><td rowspan="3" data-t></td></tr><tr><td><code>a === b</code></td><td data-r="1"></td></tr><tr><td><code>Object.is(a, b)</code></td><td data-r="2"></td></tr></table></div>
      <div class="vz-msg" aria-live="polite"></div>`;
    const presets = [['"5"', '5'], ['0', 'false'], ['""', '0'], ['null', 'undefined'], ['null', '0'], ['NaN', 'NaN'], ['[]', 'false'], ['[1]', '1'], ['-0', '0'], ['"b"', '"B"']];
    b.querySelector('[data-pre]').innerHTML = presets.map(([x, y], i) => `<button type="button" class="qa-toggle" data-i="${i}">${esc(x)} vs ${esc(y)}</button>`).join('');
    const A = $('[data-a]', b), B = $('[data-b]', b), msg = $('.vz-msg', b);
    const run = () => {
      const pa = parse(A.value), pb = parse(B.value);
      if (!pa.ok || !pb.ok) { msg.textContent = 'Type a value JavaScript understands, such as 42, "text", true, null, [1, 2] or {}.'; return; }
      const a = pa.v, c = pb.v;
      const r = [a == c, a === c, Object.is(a, c)];
      r.forEach((x, i) => { const td = b.querySelector(`[data-r="${i}"]`); td.innerHTML = `<span class="jv-res ${x ? 'yes' : 'no'}">${x}</span>`; });
      b.querySelector('[data-t]').innerHTML = `<code>${esc(show(a))}</code> is ${esc(a === null ? 'null' : typeof a)}<br><code>${esc(show(c))}</code> is ${esc(c === null ? 'null' : typeof c)}`;
      msg.innerHTML = `<b>Why:</b> ${esc(why(a, c))} ${r[1] !== r[2] ? '<br><b>=== and Object.is differ here</b> because === treats NaN as unequal to itself and -0 as equal to 0. Object.is does neither.' : ''}`;
    };
    b.addEventListener('click', e => { const p = e.target.closest('[data-i]'); if (!p) return; [A.value, B.value] = presets[+p.dataset.i]; run(); });
    A.addEventListener('input', run); B.addEventListener('input', run);
    run();
  };

  /* ---------- arr: array methods one element at a time ---------- */
  const OPS = {
    map: { code: 'nums.map(n => n * 2)', start: () => [], step: (acc, n) => ({ acc: [...acc, n * 2], mark: 'ok', note: `${n} * 2 is ${n * 2}, push it` }) },
    filter: { code: 'nums.filter(n => n % 2 === 0)', start: () => [], step: (acc, n) => n % 2 === 0 ? { acc: [...acc, n], mark: 'ok', note: `${n} is even, keep it` } : { acc, mark: 'bad', note: `${n} is odd, skip it` } },
    reduce: { code: 'nums.reduce((sum, n) => sum + n, 0)', start: () => 0, step: (acc, n) => ({ acc: acc + n, mark: 'ok', note: `sum was ${acc}, add ${n}, sum is now ${acc + n}` }) },
    find: { code: 'nums.find(n => n > 4)', start: () => undefined, step: (acc, n) => n > 4 ? { acc: n, mark: 'ok', note: `${n} > 4 is true, return ${n} and stop`, stop: true } : { acc, mark: 'bad', note: `${n} > 4 is false, keep looking` } },
    some: { code: 'nums.some(n => n > 6)', start: () => false, step: (acc, n) => n > 6 ? { acc: true, mark: 'ok', note: `${n} > 6, one is enough, return true and stop`, stop: true } : { acc, mark: 'bad', note: `${n} > 6 is false, keep looking` } },
    every: { code: 'nums.every(n => n > 0)', start: () => true, step: (acc, n) => n > 0 ? { acc, mark: 'ok', note: `${n} > 0 is true, check the next one` } : { acc: false, mark: 'bad', note: `${n} > 0 is false, one failure is enough, return false`, stop: true } }
  };
  W.arr = el => {
    const b = K.shell(el, 'Array methods, one element at a time', 'Change the numbers, pick a method and press Play.');
    b.innerHTML = `<div class="vz-row"><label class="jv-lbl">nums <input class="jv-in" data-in value="3, 8, 1, 6, 5" style="width:190px"></label>${K.seg('op', Object.keys(OPS).map(k => [k, k]), 'map')}</div>
      <pre class="jv-code"><div data-code></div></pre>
      <div class="vz-row"><span class="jv-lbl">input</span><div class="jv-cells" data-cells></div></div>
      <div class="vz-row"><span class="jv-lbl">result</span><div class="jv-cells" data-out></div></div>
      <div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let op = 'map', nums = [], frames = [];
    const msg = $('.vz-msg', b);
    const outHtml = v => Array.isArray(v) ? (v.length ? v.map(x => K.cell(x, 'ok')).join('') : '<span class="jv-res">[ ]</span>') : `<span class="jv-res">${esc(String(v))}</span>`;
    function plan() {
      nums = $('[data-in]', b).value.split(/[\s,]+/).filter(Boolean).map(Number).filter(n => !isNaN(n)).slice(0, 10);
      $('[data-code]', b).innerHTML = typeof LEARN !== 'undefined' ? LEARN.hl(OPS[op].code, 'js') : esc(OPS[op].code);
      frames = [];
      let acc = OPS[op].start();
      const marks = nums.map(() => '');
      frames.push({ marks: [...marks], cur: -1, acc, note: 'Start. ' + (op === 'reduce' ? 'The running total starts at 0.' : op === 'map' || op === 'filter' ? 'The result starts as a new empty array. nums is never changed.' : 'Nothing found yet.') });
      for (let i = 0; i < nums.length; i++) {
        const r = OPS[op].step(acc, nums[i]);
        acc = r.acc; marks[i] = r.mark;
        frames.push({ marks: [...marks], cur: i, acc, note: r.note });
        if (r.stop) { for (let j = i + 1; j < nums.length; j++) marks[j] = 'dim'; frames.push({ marks: [...marks], cur: -1, acc, note: `Done early. The rest are never visited. Result: ${String(acc)}` }); break; }
      }
      if (!frames[frames.length - 1].note.startsWith('Done')) frames.push({ marks: [...marks], cur: -1, acc, note: `Done. Result: ${Array.isArray(acc) ? '[' + acc.join(', ') + ']' : String(acc)}` });
      P.load(frames.length);
    }
    const P = K.Player($('.vz-p', b), f => {
      const fr = frames[f];
      $('[data-cells]', b).innerHTML = nums.map((n, i) => K.cell(n, i === fr.cur ? 'hl' : fr.marks[i], 'i' + i)).join('');
      $('[data-out]', b).innerHTML = outHtml(fr.acc);
      msg.textContent = fr.note;
    }, 1000);
    K.wireSeg(b, 'op', v => { op = v; plan(); });
    $('[data-in]', b).addEventListener('change', plan);
    plan();
  };

  /* ---------- bubble: capture, target, bubble ---------- */
  W.bubble = el => {
    const b = K.shell(el, 'Where does a click travel', 'Click the button inside the boxes, or press Play. Turn on stopPropagation to see the journey cut short.');
    const path = ['window', 'document', 'body', 'div.card', 'button'];
    b.innerHTML = `<div class="vz-row"><label class="jv-lbl"><input type="checkbox" data-stop> stopPropagation() on div.card</label><label class="jv-lbl"><input type="checkbox" data-cap checked> listen in the capture phase too</label></div>
      <div class="jv-tree" data-tree></div><ol class="jv-steps" data-log></ol><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    $('[data-tree]', b).innerHTML = path.map((p, i) => `<div class="jv-node" data-n="${i}" style="margin-left:${i * 22}px">${p === 'button' ? '🔘 ' : ''}${esc(p)}</div>`).join('');
    let frames = [];
    const msg = $('.vz-msg', b);
    function plan() {
      const stop = $('[data-stop]', b).checked, cap = $('[data-cap]', b).checked;
      frames = [{ on: -1, log: [], m: 'A click on the button starts at the very top and travels down, then back up.' }];
      const log = [];
      if (cap) for (let i = 0; i < path.length - 1; i++) { log.push(`capture: ${path[i]}`); frames.push({ on: i, log: [...log], m: `Capture phase. The event passes ${path[i]} on the way down.` }); }
      log.push('target: button'); frames.push({ on: 4, log: [...log], m: 'Target phase. The listeners on the button itself run.' });
      for (let i = path.length - 2; i >= 0; i--) {
        log.push(`bubble: ${path[i]}`); frames.push({ on: i, log: [...log], m: `Bubble phase. The event rises through ${path[i]}.` });
        if (stop && path[i] === 'div.card') { frames.push({ on: i, log: [...log], m: 'stopPropagation() ran here, so body, document and window never hear about the click.', end: true }); break; }
      }
      P.load(frames.length);
    }
    const P = K.Player($('.vz-p', b), f => {
      const fr = frames[f];
      b.querySelectorAll('.jv-node').forEach(n => n.classList.toggle('on', +n.dataset.n === fr.on));
      $('[data-log]', b).innerHTML = fr.log.map((x, i) => `<li${i === fr.log.length - 1 ? ' class="on"' : ''}>${esc(x)}</li>`).join('');
      msg.textContent = fr.m;
    }, 900);
    b.addEventListener('change', plan);
    $('[data-tree]', b).addEventListener('click', e => { if (e.target.closest('[data-n="4"]')) { plan(); P.play(); } });
    plan();
  };

  /* ---------- wait: a fixed sleep against auto-waiting ---------- */
  W.wait = el => {
    const b = K.shell(el, 'Sleep or wait for the element', 'Move the slider to change when the Pay button appears, then compare the two strategies.');
    b.innerHTML = `<div class="vz-row">${K.slider('t', 'The button appears after', 100, 4000, 1800, 100)} ms</div>
      <div class="jv-time"><span>sleep(2000)</span><div data-a></div><span>auto-wait</span><div data-b></div><span>timeout 5000</span><div data-c></div></div><div class="vz-msg" aria-live="polite"></div>`;
    const msg = $('.vz-msg', b);
    const bar = (w, txt, col) => `<div class="jv-bar" style="width:${Math.max(6, Math.min(100, w))}%; background:${col}">${txt}</div>`;
    const draw = t => {
      const s = 2000, poll = Math.ceil(t / 100) * 100;
      $('[data-a]', b).innerHTML = bar(s / 50, t <= s ? `waited 2000 ms, wasted ${s - t} ms` : 'clicked at 2000 ms: not there yet, test fails', t <= s ? 'var(--orange)' : 'var(--red)');
      $('[data-b]', b).innerHTML = bar(poll / 50, `clicked at about ${poll} ms`, 'var(--green)');
      $('[data-c]', b).innerHTML = bar(100, 'the most it would ever wait', 'var(--ink2)');
      msg.innerHTML = t <= s ? `The fixed sleep passes but wastes <b>${s - t} ms</b> on every run. Auto-waiting moves on the moment the button is ready.` : `The fixed sleep <b>fails</b> because the page was slower than the guess. Auto-waiting keeps checking and passes at about ${poll} ms. This is why flaky tests usually hide a fixed sleep.`;
    };
    K.wireSlider(b, 't', draw);
    draw(1800);
  };

  /* ---------- regex: live tester ---------- */
  W.regex = el => {
    const b = K.shell(el, 'Regular expression tester', 'Edit the pattern, the flags or the text. Matches light up as you type.');
    b.innerHTML = `<div class="vz-row"><label class="jv-lbl">/ <input class="jv-in" data-p value="(\\d{3})-(\\d{4})" style="width:220px"> /</label><label class="jv-lbl">flags <input class="jv-in" data-f value="g" style="width:60px"></label></div>
      <textarea class="jp-ed" data-t style="min-height:70px; border-radius:12px">Call 555-1234 or 555-9876. Order ORD-2024 ships today.</textarea>
      <div class="vz-msg" data-o aria-live="polite"></div>`;
    const P = $('[data-p]', b), F = $('[data-f]', b), T = $('[data-t]', b), O = $('[data-o]', b);
    const run = () => {
      let re;
      try { re = new RegExp(P.value, F.value.includes('g') ? F.value : F.value + 'g'); } catch (e) { O.innerHTML = `<b>Not a valid pattern:</b> ${esc(e.message)}`; return; }
      const text = T.value;
      const ms = [...text.matchAll(re)].filter(m => m[0] !== '' || true).slice(0, 50);
      let html = '', i = 0;
      for (const m of ms) { html += esc(text.slice(i, m.index)) + `<mark>${esc(m[0])}</mark>`; i = m.index + m[0].length; }
      html += esc(text.slice(i));
      const groups = ms.map((m, k) => `<li><code>${esc(m[0])}</code> at ${m.index}${m.length > 1 ? ', groups: ' + m.slice(1).map(g => `<code>${esc(g ?? 'undefined')}</code>`).join(' ') : ''}</li>`).join('');
      O.innerHTML = `<div style="white-space:pre-wrap; font-family:var(--font-mono)">${html}</div><b>${ms.length} match${ms.length === 1 ? '' : 'es'}</b><ol class="jv-steps">${groups}</ol>`;
    };
    [P, F, T].forEach(x => x.addEventListener('input', run));
    run();
  };
})();

/* ===== More animations for the JavaScript chapters =====
   <div class="viz" data-viz="engine"></div>    type a few lines and watch the scanner, parser, creation phase,
                                                 bytecode generator and interpreter work on them, one step at a time
   <div class="viz" data-viz="loopsim"></div>   type console.log, setTimeout, promise and queueMicrotask calls and watch the
                                                 call stack, the timers, both queues and the console, one step at a time */
(() => {
  const K = VIZ.kit, W = VIZ.widgets, esc = K.esc, $ = K.$;
  const hl = s => (typeof LEARN !== 'undefined' ? LEARN.hl(s, 'js') : esc(s));
  const show = v => (typeof v === 'string' ? JSON.stringify(v) : v === undefined ? 'undefined' : String(v));
  const err = (name, message, line) => ({ jsErr: true, name, message, line });

  /* ---------- engine: from text to output for a tiny part of JavaScript ---------- */
  const DECL = new Set(['let', 'const', 'var']);
  function scan(src) {
    const out = [];
    let i = 0, line = 1;
    while (i < src.length) {
      const c = src[i];
      if (c === '\n') { line++; i++; continue; }
      if (/\s/.test(c)) { i++; continue; }
      if (c === '/' && src[i + 1] === '/') { while (i < src.length && src[i] !== '\n') i++; continue; }
      const rest = src.slice(i);
      const m = /^\d+(?:\.\d+)?/.exec(rest) || /^"[^"\\\n]*"|^'[^'\\\n]*'/.exec(rest) || /^[A-Za-z_$][\w$]*/.exec(rest) || /^[-+*/%=().,;]/.exec(rest);
      if (!m) throw err('SyntaxError', c === '"' || c === "'" ? 'Invalid or unexpected token (a string is not closed)' : `Invalid or unexpected token ${c}`, line);
      const v = m[0];
      const k = /^\d/.test(v) ? 'number' : /^["']/.test(v) ? 'string' : /^[A-Za-z_$]/.test(v) ? (DECL.has(v) ? 'keyword' : 'name') : 'punctuator';
      out.push({ k, v, line });
      i += v.length;
    }
    return out;
  }
  const PREC = { '+': 1, '-': 1, '*': 2, '/': 2, '%': 2 };
  function parse(toks) {
    let p = 0;
    const peek = () => toks[p], next = () => toks[p++];
    const last = () => toks[p - 1] || { line: 1 };
    const fail = t => { throw err('SyntaxError', t ? `Unexpected token '${t.v}'` : 'Unexpected end of input', t ? t.line : last().line); };
    const eat = v => { const t = next(); if (!t || t.v !== v) fail(t); return t; };
    function primary() {
      const t = next();
      if (!t) fail();
      if (t.k === 'number') return { type: 'NumericLiteral', value: Number(t.v) };
      if (t.k === 'string') return { type: 'StringLiteral', value: t.v.slice(1, -1) };
      if (t.v === '(') { const e = expr(0); eat(')'); return e; }
      if (t.v === '-') return { type: 'UnaryExpression', op: '-', arg: primary() };
      if (t.k !== 'name') fail(t);
      if (peek() && peek().v === '.') {
        next();
        const prop = next();
        if (!prop || prop.k !== 'name') fail(prop);
        const args = [];
        eat('(');
        if (peek() && peek().v !== ')') { args.push(expr(0)); while (peek() && peek().v === ',') { next(); args.push(expr(0)); } }
        eat(')');
        return { type: 'CallExpression', object: t.v, prop: prop.v, args };
      }
      return { type: 'Identifier', name: t.v };
    }
    function expr(min) {
      let left = primary();
      while (peek() && PREC[peek().v] > min) {
        const op = next().v;
        left = { type: 'BinaryExpression', op, left, right: expr(PREC[op]) };
      }
      return left;
    }
    function statement() {
      const t = peek();
      let node;
      if (t.k === 'keyword') {
        next();
        const id = next();
        if (!id || id.k !== 'name') fail(id);
        eat('=');
        node = { type: 'VariableDeclaration', kind: t.v, name: id.v, init: expr(0), line: t.line };
      } else if (t.k === 'name' && toks[p + 1] && toks[p + 1].v === '=') {
        next(); next();
        node = { type: 'AssignmentExpression', name: t.v, value: expr(0), line: t.line };
      } else node = { type: 'ExpressionStatement', expr: expr(0), line: t.line };
      if (peek() && peek().v === ';') next();
      else if (peek() && peek().line === last().line) fail(peek());
      return node;
    }
    const body = [];
    while (p < toks.length) { if (peek().v === ';') { next(); continue; } body.push(statement()); }
    // Early errors are found while parsing, before a single line runs
    const seen = {};
    for (const s of body) {
      if (s.type !== 'VariableDeclaration') continue;
      if (seen[s.name] && (seen[s.name] !== 'var' || s.kind !== 'var')) throw err('SyntaxError', `Identifier '${s.name}' has already been declared`, s.line);
      seen[s.name] = s.kind;
    }
    return { type: 'Program', body };
  }
  function treeLines(n, depth = 0, label = '') {
    const pad = '  '.repeat(depth) + (label ? label + ': ' : '');
    switch (n.type) {
      case 'Program': return [pad + 'Program', ...n.body.flatMap(s => treeLines(s, depth + 1))];
      case 'VariableDeclaration': return [pad + `VariableDeclaration ${n.kind} ${n.name}`, ...treeLines(n.init, depth + 1, 'init')];
      case 'AssignmentExpression': return [pad + `AssignmentExpression ${n.name} =`, ...treeLines(n.value, depth + 1, 'value')];
      case 'ExpressionStatement': return [pad + 'ExpressionStatement', ...treeLines(n.expr, depth + 1)];
      case 'BinaryExpression': return [pad + `BinaryExpression ${n.op}`, ...treeLines(n.left, depth + 1, 'left'), ...treeLines(n.right, depth + 1, 'right')];
      case 'UnaryExpression': return [pad + 'UnaryExpression -', ...treeLines(n.arg, depth + 1)];
      case 'CallExpression': return [pad + `CallExpression ${n.object}.${n.prop}`, ...n.args.flatMap((a, i) => treeLines(a, depth + 1, 'arg ' + i))];
      case 'NumericLiteral': return [pad + `NumericLiteral ${n.value}`];
      case 'StringLiteral': return [pad + `StringLiteral ${JSON.stringify(n.value)}`];
      case 'Identifier': return [pad + `Identifier ${n.name}`];
    }
    return [pad + n.type];
  }
  const OPS = { '+': 'Add', '-': 'Sub', '*': 'Mul', '/': 'Div', '%': 'Mod' };
  function generate(prog) {
    const code = [], consts = [];
    let reg = 0, used = 0;
    const R = () => { const r = reg++; used = Math.max(used, reg); return r; };
    const emit = (ins, line) => code.push({ ...ins, line });
    const konst = v => { let i = consts.findIndex(c => Object.is(c, v)); if (i < 0) { consts.push(v); i = consts.length - 1; } return i; };
    function e(n, line) {
      if (n.type === 'NumericLiteral') {
        if (Number.isInteger(n.value) && Math.abs(n.value) < 2 ** 30) emit({ op: 'LdaSmi', txt: `[${n.value}]`, v: n.value, why: `put the small whole number ${n.value} in the accumulator` }, line);
        else emit({ op: 'LdaConstant', txt: `[${konst(n.value)}]`, v: n.value, why: `load ${n.value} from the constant pool` }, line);
      } else if (n.type === 'StringLiteral') emit({ op: 'LdaConstant', txt: `[${konst(n.value)}]`, v: n.value, why: `load the string ${JSON.stringify(n.value)} from the constant pool` }, line);
      else if (n.type === 'Identifier') emit({ op: 'LdaGlobal', txt: `[${n.name}]`, name: n.name, why: `read the variable ${n.name} into the accumulator` }, line);
      else if (n.type === 'UnaryExpression') { e(n.arg, line); emit({ op: 'Negate', txt: '', why: 'flip the sign of the accumulator' }, line); }
      else if (n.type === 'BinaryExpression') {
        e(n.left, line);
        const r = R();
        emit({ op: 'Star', txt: `r${r}`, r, why: `park the left side in register r${r}` }, line);
        e(n.right, line);
        emit({ op: OPS[n.op], txt: `r${r}`, r, sym: n.op, why: `r${r} ${n.op} accumulator, result in the accumulator` }, line);
        reg--;
      } else if (n.type === 'CallExpression') {
        const base = reg;
        const regs = n.args.map(a => { e(a, line); const r = R(); emit({ op: 'Star', txt: `r${r}`, r, why: `keep argument ${r - base + 1} in r${r}` }, line); return r; });
        const ro = R();
        emit({ op: 'LdaGlobal', txt: `[${n.object}]`, name: n.object, why: `find the object ${n.object}` }, line);
        emit({ op: 'Star', txt: `r${ro}`, r: ro, why: `keep ${n.object} in r${ro}` }, line);
        emit({ op: 'GetNamedProperty', txt: `r${ro}, [${n.prop}]`, r: ro, prop: n.prop, why: `look up ${n.object}.${n.prop}` }, line);
        emit({ op: 'CallProperty', txt: `acc, r${ro}, ${regs.length ? 'r' + regs[0] + (regs.length > 1 ? '-r' + regs[regs.length - 1] : '') : '()'}`, r: ro, args: regs, label: `${n.object}.${n.prop}`, why: `call ${n.object}.${n.prop} with ${regs.length} argument${regs.length === 1 ? '' : 's'}` }, line);
        reg = base;
      }
    }
    for (const s of prog.body) {
      const start = code.length;
      if (s.type === 'VariableDeclaration') { e(s.init, s.line); emit({ op: 'StaGlobal', txt: `[${s.name}]`, name: s.name, init: true, why: `store the accumulator in ${s.name}, which ends its temporal dead zone` }, s.line); }
      else if (s.type === 'AssignmentExpression') { e(s.value, s.line); emit({ op: 'StaGlobal', txt: `[${s.name}]`, name: s.name, why: `store the accumulator in ${s.name}` }, s.line); }
      else e(s.expr, s.line);
      s.range = [start, code.length];
    }
    emit({ op: 'Return', txt: '', why: 'the script is finished' }, 0);
    return { code, consts, regs: used };
  }
  const BUILTIN = { console: { log: 'console.log', info: 'console.log', error: 'console.log' }, Math: { max: 'Math.max' } };
  function plan(src) {
    const frames = [];
    const st = { stage: 0, lines: [], toks: [], tokOn: [], tree: [], scope: [], code: [], pc: -1, acc: undefined, regs: [], out: [], m: '', bad: false };
    const push = o => frames.push(JSON.parse(JSON.stringify({ ...st, ...o })));
    let toks, prog, gen;
    try { toks = scan(src); } catch (e) { push({ stage: 1, lines: [e.line], bad: true, m: `<b>${e.name}</b> on line ${e.line}: ${esc(e.message)}. The scanner stops here, so <b>not one line runs</b>, not even the lines above.` }); return frames; }
    if (!toks.length) { push({ m: 'Type a few lines of code first.' }); return frames; }
    const byLine = {};
    toks.forEach((t, i) => (byLine[t.line] = byLine[t.line] || []).push(i));
    st.toks = toks;
    for (const ln of Object.keys(byLine).map(Number)) {
      st.tokOn = byLine[ln];
      push({ stage: 1, lines: [ln], m: `<b>Scanner</b>, line ${ln}: the characters are cut into ${byLine[ln].length} tokens: ${byLine[ln].map(i => `<code>${esc(toks[i].v)}</code> (${toks[i].k})`).join(', ')}. Spaces and comments are thrown away.` });
    }
    st.tokOn = [];
    try { prog = parse(toks); } catch (e) {
      push({ stage: 2, lines: [e.line], bad: true, m: `<b>${e.name}</b> on line ${e.line}: ${esc(e.message)}. The parser rejects the whole file, so <b>not one line runs</b>. This is why a single typo stops every test in a spec file.` });
      return frames;
    }
    const lines = [];
    for (const s of prog.body) {
      lines.push(...treeLines(s, 1));
      st.tree = ['Program', ...lines];
      push({ stage: 2, lines: [s.line], m: `<b>Parser</b>, line ${s.line}: the tokens become a <b>${s.type}</b> node in the syntax tree (the AST). The tree shows what belongs to what, so <code>2 + 3 * 4</code> keeps the multiply below the add.` });
    }
    const scope = [];
    for (const s of prog.body) if (s.type === 'VariableDeclaration' && !scope.some(x => x.name === s.name)) scope.push({ name: s.name, kind: s.kind, v: s.kind === 'var' ? 'undefined' : '<uninitialised>', init: s.kind === 'var' });
    st.scope = scope;
    push({ stage: 3, lines: [], m: scope.length ? `<b>Creation phase</b>: before running, the engine creates a memory slot for every declared name. ${scope.filter(x => x.kind === 'var').length ? '<code>var</code> names start as <code>undefined</code>. ' : ''}${scope.filter(x => x.kind !== 'var').length ? '<code>let</code> and <code>const</code> names exist but stay <b>uninitialised</b> (the temporal dead zone) until their line runs. ' : ''}This is what people call hoisting.` : '<b>Creation phase</b>: no names are declared, so the global scope has nothing new in it.' });
    gen = generate(prog);
    for (const s of prog.body) {
      st.code = gen.code.slice(0, s.range[1]).map(c => c.op + ' ' + c.txt);
      push({ stage: 4, lines: [s.line], m: `<b>Bytecode</b>, line ${s.line}: the interpreter (Ignition in V8) turns this part of the tree into ${s.range[1] - s.range[0]} small instructions. Most of them work on one special register, the <b>accumulator</b>.` });
    }
    st.code = gen.code.map(c => c.op + ' ' + c.txt);
    const vars = Object.fromEntries(scope.map(x => [x.name, x]));
    const regs = [];
    let acc;
    const setScope = () => scope.map(x => ({ ...x, v: x.init ? show(x.v === '<uninitialised>' ? undefined : x.v) : '<uninitialised>' }));
    scope.forEach(x => { if (x.kind === 'var') x.v = undefined; });
    let steps = 0;
    for (let pc = 0; pc < gen.code.length; pc++) {
      const c = gen.code[pc];
      if (++steps > 160) { push({ stage: 5, pc, m: 'Stopped after 160 steps to keep the animation short.' }); break; }
      try {
        switch (c.op) {
          case 'LdaSmi': case 'LdaConstant': acc = c.v; break;
          case 'Star': regs[c.r] = acc; break;
          case 'LdaGlobal':
            if (BUILTIN[c.name]) { acc = { builtin: c.name }; break; }
            if (!vars[c.name]) throw err('ReferenceError', `${c.name} is not defined`, c.line);
            if (!vars[c.name].init) throw err('ReferenceError', `Cannot access '${c.name}' before initialization`, c.line);
            acc = vars[c.name].v; break;
          case 'Negate': acc = -acc; break;
          case 'Add': acc = regs[c.r] + acc; break;
          case 'Sub': acc = regs[c.r] - acc; break;
          case 'Mul': acc = regs[c.r] * acc; break;
          case 'Div': acc = regs[c.r] / acc; break;
          case 'Mod': acc = regs[c.r] % acc; break;
          case 'StaGlobal': {
            const x = vars[c.name];
            if (!x) throw err('ReferenceError', `${c.name} is not defined`, c.line);
            if (!c.init && !x.init) throw err('ReferenceError', `Cannot access '${c.name}' before initialization`, c.line);
            if (!c.init && x.kind === 'const') throw err('TypeError', 'Assignment to constant variable.', c.line);
            x.v = acc; x.init = true; break;
          }
          case 'GetNamedProperty': { const o = regs[c.r]; acc = o && o.builtin && BUILTIN[o.builtin][c.prop] ? { fn: BUILTIN[o.builtin][c.prop] } : undefined; c.missing = `${o && o.builtin}.${c.prop}`; break; }
          case 'CallProperty': {
            if (!acc || !acc.fn) throw err('TypeError', `${gen.code[pc - 1].missing} is not a function`, c.line);
            const args = c.args.map(r => regs[r]);
            if (acc.fn === 'console.log') { st.out = [...st.out, args.map(a => (typeof a === 'string' ? a : show(a))).join(' ')]; acc = undefined; }
            else acc = Math.max(...args);
            break;
          }
        }
      } catch (e) {
        if (!e.jsErr) throw e;
        push({ stage: 5, pc, lines: [e.line], scope: setScope(), acc: show(acc), regs: regs.map(show), bad: true, m: `<b>Uncaught ${e.name}</b> on line ${e.line}: ${esc(e.message.replace(/\.$/, ''))}. Parsing went fine, so the lines before this one <b>did</b> run. A runtime error stops the program at this instruction.` });
        return frames;
      }
      const accTxt = acc && acc.builtin ? `<${acc.builtin}>` : acc && acc.fn ? `<function ${acc.fn}>` : show(acc);
      push({ stage: 5, pc, lines: c.line ? [c.line] : [], scope: setScope(), acc: accTxt, regs: regs.map(r => (r && r.builtin ? `<${r.builtin}>` : show(r))),
        m: `<b>Run</b> <code>${esc(c.op + ' ' + c.txt)}</code>: ${esc(c.why)}.${c.op === 'CallProperty' && st.out.length ? ' The console prints a line.' : ''}${c.op === 'Return' ? ' Functions that run many times would now be handed to the optimising compilers.' : ''}` });
    }
    return frames;
  }
  const PRESETS = [
    ['Cart total', 'let price = 250;\nlet qty = 3;\nconst total = price * qty + 40;\nconsole.log("Total:", total);'],
    ['Hoisting', 'console.log(coupon);\nvar coupon = "SAVE10";\nconsole.log(coupon);'],
    ['TDZ error', 'console.log("start");\nconsole.log(discount);\nlet discount = 10;'],
    ['Syntax error', 'console.log("line 1 never prints");\nlet x = (2 + 3;'],
    ['const', 'const retries = 2;\nconsole.log(retries);\nretries = 3;'],
    ['Strings', 'let id = 42;\nconsole.log("Order-" + id, 10 - "4", "3" * "5");'],
  ];
  W.engine = el => {
    const b = K.shell(el, 'Watch the engine run your code', 'Pick an example or type your own lines (let, const, var, numbers, strings, + - * / %, brackets and console.log). Press Play or step with the arrows.');
    b.innerHTML = `<div class="vz-row" data-pre></div>
      <textarea class="jp-ed jv-src" spellcheck="false" aria-label="Code for the engine to run"></textarea>
      <div class="vz-row"><button type="button" class="jv-go" data-go>⚙️ Send it to the engine</button></div>
      <ol class="jv-stages" data-stages>${['Scan', 'Parse', 'Create scope', 'Bytecode', 'Run'].map((s, i) => `<li data-s="${i + 1}"><b>${i + 1}</b> ${s}</li>`).join('')}</ol>
      <div class="jv-eng">
        <div class="jv-lane"><b>📝 Source</b><pre class="jv-code" data-src></pre></div>
        <div class="jv-lane"><b>🔤 Tokens</b><div class="jv-toks" data-toks></div></div>
        <div class="jv-lane"><b>🌳 Syntax tree (AST)</b><pre class="jv-ast" data-ast></pre></div>
        <div class="jv-lane"><b>🧠 Global scope</b><div data-scope></div><b class="jv-sub">Accumulator and registers</b><div data-regs></div></div>
        <div class="jv-lane"><b>⚙️ Bytecode</b><pre class="jv-code" data-bc></pre></div>
        <div class="jv-lane"><b>🖥️ Console</b><pre class="jv-out" data-out></pre></div>
      </div>
      <div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>
      <p class="jv-note">A teaching model of V8's pipeline for a small part of the language. The instruction names follow V8's Ignition bytecode, and real V8 also adds feedback slots and treats top level <code>let</code> slightly differently.</p>`;
    const ta = $('.jv-src', b), msg = $('.vz-msg', b);
    $('[data-pre]', b).innerHTML = PRESETS.map(([n], i) => `<button type="button" class="qa-toggle" data-i="${i}">${esc(n)}</button>`).join('');
    ta.value = PRESETS[0][1];
    let frames = [], src = [];
    const P = K.Player($('.vz-p', b), f => {
      const fr = frames[f] || frames[0];
      b.querySelectorAll('[data-stages] li').forEach(li => { const s = +li.dataset.s; li.className = s === fr.stage ? (fr.bad ? 'bad' : 'on') : s < fr.stage ? 'done' : ''; });
      const on = new Set(fr.lines);
      $('[data-src]', b).innerHTML = src.map((l, i) => `<div class="${on.has(i + 1) ? (fr.bad ? 'on bad' : 'on') : ''}">${hl(l) || ' '}</div>`).join('');
      const tokOn = new Set(fr.tokOn);
      $('[data-toks]', b).innerHTML = fr.stage >= 1 ? fr.toks.map((t, i) => `<span class="jv-tok ${t.k}${tokOn.has(i) ? ' on' : ''}" title="${t.k}">${esc(t.v)}</span>`).join('') : '';
      $('[data-ast]', b).textContent = fr.tree.join('\n');
      $('[data-scope]', b).innerHTML = fr.scope.map(x => `<span class="jv-chip ${x.v === '<uninitialised>' ? 't5' : 't1'}">${esc(x.kind)} ${esc(x.name)} = ${esc(x.v)}</span>`).join('') || '<span class="jv-dim">nothing yet</span>';
      $('[data-regs]', b).innerHTML = fr.stage === 5 ? `<span class="jv-chip t2">acc = ${esc(fr.acc)}</span>${fr.regs.map((r, i) => (r === undefined || r === null ? '' : `<span class="jv-chip t0">r${i} = ${esc(r)}</span>`)).join('')}` : '<span class="jv-dim">used while running</span>';
      $('[data-bc]', b).innerHTML = fr.code.map((c, i) => `<div class="${i === fr.pc ? (fr.bad ? 'on bad' : 'on') : ''}">${esc(c)}</div>`).join('');
      const bc = $('[data-bc] .on', b);
      if (bc) bc.parentNode.scrollTop = bc.offsetTop - bc.parentNode.clientHeight / 2;
      $('[data-out]', b).textContent = fr.out.join('\n');
      msg.innerHTML = f ? `<b>Step ${f} of ${frames.length - 1}.</b> ${fr.m}` : 'Press ▶ Play to send the code through the engine.';
    }, 1500);
    const go = () => {
      src = ta.value.split('\n');
      try { frames = plan(ta.value); } catch (e) { frames = [{ stage: 0, lines: [], toks: [], tokOn: [], tree: [], scope: [], code: [], pc: -1, regs: [], out: [], m: 'This tiny engine does not understand that code yet.' }]; }
      frames.unshift({ ...frames[0], stage: 0, lines: [], tokOn: [], toks: [], tree: [], scope: [], code: [], pc: -1, regs: [], out: [], bad: false });
      P.load(frames.length);
    };
    $('[data-pre]', b).addEventListener('click', e => { const t = e.target.closest('[data-i]'); if (!t) return; ta.value = PRESETS[+t.dataset.i][1]; go(); P.play(); });
    $('[data-go]', b).addEventListener('click', () => { go(); P.play(); });
    go();
  };
  W.engine.plan = plan;

  /* ---------- loopsim: the browser event loop for code you type ---------- */
  function loopParse(src) {
    let i = 0;
    const ws = () => { for (;;) { while (i < src.length && /\s/.test(src[i])) i++; if (src.startsWith('//', i)) { while (i < src.length && src[i] !== '\n') i++; } else return; } };
    const fail = what => { throw new Error(`I could not read the code near "${src.slice(i, i + 24).split('\n')[0]}". ${what || ''}`); };
    const lit = s => { ws(); if (!src.startsWith(s, i)) fail(`Expected ${s}`); i += s.length; };
    const peekLit = s => { ws(); return src.startsWith(s, i); };
    function value() {
      ws();
      const m = /^"([^"\\\n]*)"|^'([^'\\\n]*)'|^`([^`\\]*)`|^-?\d+(?:\.\d+)?/.exec(src.slice(i));
      if (!m) fail('console.log here takes text in quotes or numbers.');
      i += m[0].length;
      return m[1] ?? m[2] ?? m[3] ?? m[0];
    }
    function fn() {
      ws();
      if (peekLit('async')) fail('Use plain arrow functions here.');
      if (peekLit('function')) { lit('function'); ws(); lit('('); lit(')'); lit('{'); return block(); }
      lit('('); lit(')'); lit('=>');
      if (peekLit('{')) { lit('{'); return block(); }
      return [stmt()];
    }
    function block() { const out = []; while (!peekLit('}')) { if (i >= src.length) fail('A { is never closed.'); if (peekLit(';')) { i++; continue; } out.push(stmt()); } lit('}'); return out; }
    function stmt() {
      ws();
      const at = i;
      let s;
      if (peekLit('console.log')) {
        lit('console.log'); lit('(');
        const args = [];
        if (!peekLit(')')) { args.push(value()); while (peekLit(',')) { lit(','); args.push(value()); } }
        lit(')');
        s = { t: 'log', text: args.join(' ') };
      } else if (peekLit('setTimeout')) {
        lit('setTimeout'); lit('(');
        const body = fn();
        let ms = 0;
        if (peekLit(',')) { lit(','); ws(); const m = /^\d+/.exec(src.slice(i)); if (!m) fail('The delay must be a number.'); ms = +m[0]; i += m[0].length; }
        lit(')');
        s = { t: 'timeout', body, ms };
      } else if (peekLit('queueMicrotask')) {
        lit('queueMicrotask'); lit('('); const body = fn(); lit(')');
        s = { t: 'micro', body, via: 'queueMicrotask' };
      } else if (peekLit('Promise.resolve()')) {
        lit('Promise.resolve()');
        const chain = [];
        while (peekLit('.then')) { lit('.then'); lit('('); chain.push(fn()); lit(')'); }
        if (!chain.length) fail('Add .then(() => ...) after Promise.resolve().');
        s = { t: 'then', chain };
      } else fail('Use console.log, setTimeout, queueMicrotask or Promise.resolve().then.');
      s.src = src.slice(at, i).replace(/\s+/g, ' ').trim();
      ws();
      if (peekLit(';')) i++;
      return s;
    }
    const prog = [];
    ws();
    while (i < src.length) { if (peekLit(';')) { i++; ws(); continue; } prog.push(stmt()); ws(); }
    return prog;
  }
  const short = s => (s.length > 34 ? s.slice(0, 32) + '…' : s);
  function loopPlan(src) {
    const frames = [];
    let prog;
    try { prog = loopParse(src); } catch (e) { return [{ stack: [], apis: [], micro: [], tasks: [], out: [], m: esc(e.message), t: 0 }]; }
    const S = { stack: [], apis: [], micro: [], tasks: [], out: [], t: 0 };
    const snap = m => frames.push({ stack: S.stack.map(x => x.name), apis: S.apis.map(x => `${x.name} at ${x.due} ms`), micro: S.micro.map(x => x.name), tasks: S.tasks.map(x => x.name), out: [...S.out], t: S.t, m });
    let nT = 0, nM = 0, steps = 0;
    function run(stmts) {
      for (const s of stmts) {
        if (++steps > 120) throw new Error('stop');
        S.stack.push({ name: short(s.src) });
        if (s.t === 'log') { S.out.push(s.text); snap(`<code>${esc(short(s.src))}</code> runs on the call stack and prints <b>${esc(s.text)}</b> straight away. Synchronous code never waits.`); }
        else if (s.t === 'timeout') { const name = `timer ${++nT}`; S.apis.push({ name, due: S.t + s.ms, body: s.body, seq: nT }); snap(`<code>setTimeout</code> hands <b>${name}</b> to the browser's timer (a Web API) for ${s.ms} ms and returns at once. JavaScript does not wait for it.`); }
        else if (s.t === 'micro') { const name = `micro ${++nM}`; S.micro.push({ name, body: s.body }); snap(`<code>queueMicrotask</code> puts <b>${name}</b> in the microtask queue. It runs as soon as the call stack is empty, before any timer.`); }
        else { const name = `then ${++nM}`; S.micro.push({ name, body: s.chain[0], rest: s.chain.slice(1) }); snap(`The promise is already resolved, so its <code>.then</code> callback <b>${name}</b> goes straight into the microtask queue.${s.chain.length > 1 ? ' The next .then waits until this one has run.' : ''}`); }
        S.stack.pop();
      }
    }
    function drain() {
      while (S.micro.length) {
        const job = S.micro.shift();
        S.stack.push({ name: job.name });
        snap(`The stack is empty, so the event loop runs every microtask first. <b>${job.name}</b> moves onto the call stack.`);
        run(job.body);
        S.stack.pop();
        if (job.rest && job.rest.length) { const name = `then ${++nM}`; S.micro.push({ name, body: job.rest[0], rest: job.rest.slice(1) }); snap(`${job.name} finished, which resolves the next promise in the chain. <b>${name}</b> joins the end of the microtask queue.`); }
        else snap(`<b>${job.name}</b> is done and leaves the stack.${S.micro.length ? ' More microtasks are waiting, so they run next.' : ' The microtask queue is now empty.'}`);
      }
    }
    try {
      S.stack.push({ name: 'main script' });
      snap('The whole script is the first task. It goes onto the call stack and runs from top to bottom.');
      run(prog);
      S.stack.pop();
      snap('The script reached its last line and leaves the stack. Now the event loop takes over.');
      drain();
      while (S.apis.length || S.tasks.length) {
        if (!S.tasks.length) {
          const next = S.apis.reduce((a, x) => (x.due < a.due || (x.due === a.due && x.seq < a.seq) ? x : a));
          S.t = Math.max(S.t, next.due);
          const ready = S.apis.filter(x => x.due <= S.t).sort((a, b) => a.due - b.due || a.seq - b.seq);
          S.apis = S.apis.filter(x => !ready.includes(x));
          S.tasks.push(...ready);
          snap(`The clock reaches ${S.t} ms. ${ready.map(x => `<b>${x.name}</b>`).join(' and ')} ${ready.length > 1 ? 'are' : 'is'} due, so the browser moves ${ready.length > 1 ? 'them' : 'it'} into the task queue (also called the callback or macrotask queue).`);
        }
        const task = S.tasks.shift();
        S.stack.push({ name: task.name });
        snap(`The event loop takes <b>one</b> task, <b>${task.name}</b>, and runs it on the empty call stack.`);
        run(task.body);
        S.stack.pop();
        snap(`<b>${task.name}</b> is done. Before the next task, the browser empties the microtask queue${S.micro.length ? ', which has work waiting' : ''} and may paint the screen.`);
        drain();
      }
      snap(`Everything has run. Read the console from top to bottom: synchronous lines first, then microtasks, then timers in the order they became due.`);
    } catch (e) { snap('Stopped after 120 steps to keep the animation short.'); }
    return frames;
  }
  const LOOP_PRESETS = [
    ['Classic order', 'console.log("A sync");\nsetTimeout(() => console.log("B timer"), 0);\nPromise.resolve().then(() => console.log("C promise"));\nconsole.log("D sync");'],
    ['Timers by delay', 'setTimeout(() => console.log("slow 100 ms"), 100);\nsetTimeout(() => console.log("fast 10 ms"), 10);\nconsole.log("sync first");'],
    ['Chained then', 'Promise.resolve()\n  .then(() => console.log("then 1"))\n  .then(() => console.log("then 2"));\nqueueMicrotask(() => console.log("micro"));\nconsole.log("sync");'],
    ['Nested', 'setTimeout(() => {\n  console.log("timer");\n  Promise.resolve().then(() => console.log("promise inside timer"));\n}, 0);\nsetTimeout(() => console.log("second timer"), 0);\nconsole.log("sync");'],
  ];
  W.loopsim = el => {
    const b = K.shell(el, 'Event loop simulator', 'Pick an example or write your own with console.log, setTimeout, queueMicrotask and Promise.resolve().then. Then press Play.');
    b.innerHTML = `<div class="vz-row" data-pre></div>
      <textarea class="jp-ed jv-src" spellcheck="false" aria-label="Code for the event loop simulator"></textarea>
      <div class="vz-row"><button type="button" class="jv-go" data-go>🔄 Simulate</button><span class="jv-dim" data-clock></span></div>
      <div class="jv-eng">
        <div class="jv-lane"><b>📚 Call stack</b><div data-k="stack"></div></div>
        <div class="jv-lane"><b>⏲️ Web APIs (timers)</b><div data-k="apis"></div></div>
        <div class="jv-lane"><b>⚡ Microtask queue</b><div class="jv-q" data-k="micro"></div></div>
        <div class="jv-lane"><b>📬 Task queue</b><div class="jv-q" data-k="tasks"></div></div>
        <div class="jv-lane"><b>🖥️ Console</b><pre class="jv-out" data-out></pre></div>
      </div>
      <div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const ta = $('.jv-src', b), msg = $('.vz-msg', b);
    $('[data-pre]', b).innerHTML = LOOP_PRESETS.map(([n], i) => `<button type="button" class="qa-toggle" data-i="${i}">${esc(n)}</button>`).join('');
    ta.value = LOOP_PRESETS[0][1];
    let frames = [];
    const tone = { stack: 't2', apis: 't0', micro: 't3', tasks: 't4' };
    const P = K.Player($('.vz-p', b), f => {
      const fr = frames[f];
      const prev = frames[f - 1] || {};
      for (const k of ['stack', 'apis', 'micro', 'tasks']) {
        const items = k === 'stack' ? [...fr[k]].reverse() : fr[k];
        $(`[data-k="${k}"]`, b).innerHTML = items.map(x => `<span class="jv-chip ${tone[k]}${(prev[k] || []).includes(x) ? '' : ' new'}">${esc(x)}</span>`).join('') || '<span class="jv-dim">empty</span>';
      }
      $('[data-out]', b).textContent = fr.out.join('\n');
      $('[data-clock]', b).textContent = `⏱️ clock: ${fr.t} ms`;
      msg.innerHTML = f ? `<b>Step ${f} of ${frames.length - 1}.</b> ${fr.m}` : fr.m;
    }, 1400);
    const go = () => {
      frames = loopPlan(ta.value);
      frames.unshift({ stack: [], apis: [], micro: [], tasks: [], out: [], t: 0, m: frames.length > 1 ? 'Press ▶ Play to watch each line move through the browser.' : frames[0].m });
      P.load(frames.length);
    };
    $('[data-pre]', b).addEventListener('click', e => { const t = e.target.closest('[data-i]'); if (!t) return; ta.value = LOOP_PRESETS[+t.dataset.i][1]; go(); P.play(); });
    $('[data-go]', b).addEventListener('click', () => { go(); P.play(); });
    go();
  };
  W.loopsim.plan = loopPlan;
})();
