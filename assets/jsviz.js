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
