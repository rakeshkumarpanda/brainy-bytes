/* ===== Complete Python animations, part 1: the framework and the Core Python widgets.
   Every animation is a step by step trace. It starts empty. Each press of Step adds one piece of the picture and
   explains that piece in plain words under it, until the picture is complete. Play runs the steps, Back undoes one,
   and Reset puts every value back to how the page first showed it. Every trace is worked out again from the
   reader's own input whenever a value changes.

   PYZ.trace(name, spec) wraps CVZ.def (assets/cvviz.js):
     spec.frames(p) -> [ { say: 'what happens in this step', ...anything paint needs } ]
     spec.paint(z, frame, frames, index)   draws one frame on z.g
   Part 2 (advanced Python) is in assets/pywidgets2.js and part 3 (web and APIs) in assets/pywidgets3.js.
   Drawing helpers come from CVZ.D and AIZ (assets/aiwidgets.js). ===== */
const PYZ = (() => {
  const { D, def } = CVZ;
  const { tag, wrap, rr, tw, fit } = AIZ;
  const esc = CVZ.esc;
  const MAXF = 240;
  const MONO = '"JetBrains Mono", monospace';

  function blank(z) {
    D.text(z.g, 'Press Step to begin. The picture builds up one step at a time.', z.W / 2, z.H / 2, { a: 'center', s: 14, c: z.col.ink2 });
  }
  function trace(name, spec) {
    def(name, {
      title: spec.title, sub: spec.sub, W: spec.W || 600, H: spec.H || 340, params: spec.params || [], tips: spec.tips || [],
      startAtZero: true, init: spec.init, change: spec.change,
      speed: () => spec.speed || 1200,
      steps(z) {
        try { z.state.fr = spec.frames(z.p, z); z.state.err = ''; } catch (e) { z.state.fr = []; z.state.err = e.message; }
        if (z.state.fr.length > MAXF) z.state.fr = z.state.fr.slice(0, MAXF).concat([{ ...z.state.fr[MAXF - 1], say: `The trace is long, so it stops here after ${MAXF} steps. Try a smaller input.`, cut: true }]);
        return z.state.fr.length;
      },
      draw(z) {
        const fr = z.state.fr || [];
        if (z.state.err) { D.text(z.g, 'Please check the input.', z.W / 2, z.H / 2, { a: 'center', s: 14, c: z.col.red }); return `<p class="cai-now"><b class="k">Input problem.</b> ${esc(z.state.err)}</p>`; }
        if (!z.step) { blank(z); return '<p class="cai-now cai-start">Nothing is shown yet. Press <b>Step</b> to see the first step, or <b>Play</b> to watch every step. Each step adds one new piece and explains it here.</p>'; }
        const f = fr[z.step - 1];
        spec.paint(z, f, fr, z.step - 1);
        const log = fr.slice(0, z.step - 1).map(x => `<li>${x.say}</li>`).join('');
        return `<div class="cai-now"><b class="k">Step ${z.step} of ${fr.length}.</b> ${f.say}</div>` + (f.extra || '') +
          (z.step > 1 ? `<details class="cai-log"><summary>Earlier steps (${z.step - 1})</summary><ol>${log}</ol></details>` : '');
      }
    });
  }

  /* ---------- drawing helpers ---------- */
  /* a rounded box with a centred label that shrinks to fit */
  function box(z, x, y, w, h, label, o = {}) {
    const c = z.col;
    rr(z.g, x, y, w, h, o.r ?? 8, { fill: o.fill || c.surf, stroke: o.stroke || c.line, w: o.w || 1.5, dash: o.dash });
    if (label !== undefined && label !== '') {
      const s = fit(z.g, String(label), w - 8, o.s || 13, { mono: o.mono, b: o.b });
      D.text(z.g, String(label), x + w / 2, y + h / 2 + 1, { a: 'center', bl: 'middle', s, mono: o.mono, b: o.b, c: o.c || c.ink });
    }
  }
  /* a small heading over a column */
  const head = (z, s, x, y, o = {}) => D.text(z.g, s, x, y, { s: o.s || 12, b: true, c: o.c || z.col.ink2, a: o.a || 'left' });
  /* code lines with a highlight on line cur (0 based). Returns the y after the last line */
  function codeView(z, lines, cur, x, y, w, o = {}) {
    const lh = o.lh || 20, c = z.col;
    rr(z.g, x, y, w, lines.length * lh + 12, 8, { fill: c.bg, stroke: c.line });
    lines.forEach((ln, i) => {
      const yy = y + 6 + i * lh;
      if (i === cur) rr(z.g, x + 3, yy, w - 6, lh, 5, { fill: o.hl || (c.dark ? '#1e3a5f' : '#dbeafe') });
      if (o.done && o.done.includes(i)) D.text(z.g, '✓', x + w - 14, yy + lh - 6, { s: 12, c: c.green, b: true });
      if (o.bad === i) D.text(z.g, '✗', x + w - 14, yy + lh - 6, { s: 13, c: c.red, b: true });
      D.text(z.g, String(i + 1), x + 16, yy + lh - 6, { a: 'right', s: 11, c: c.ink2, mono: true });
      const s = fit(z.g, ln, w - 48, o.s || 12.5, { mono: true });
      D.text(z.g, ln, x + 24, yy + lh - 6, { s, mono: true, c: i === cur ? c.ink : (o.dim && i > cur ? c.ink2 : c.ink) });
    });
    return y + lines.length * lh + 12;
  }
  /* a console box that shows printed text. Lines are split on newlines */
  function consoleBox(z, text, x, y, w, h, o = {}) {
    const c = z.col;
    rr(z.g, x, y, w, h, 8, { fill: c.dark ? '#0b1220' : '#111827', stroke: c.line });
    D.text(z.g, o.title || 'Screen (console)', x + 10, y + 16, { s: 11, b: true, c: '#93c5fd' });
    const lines = String(text).split('\n');
    const max = Math.floor((h - 26) / 17);
    lines.slice(-max).forEach((ln, i) => {
      const s = fit(z.g, ln || ' ', w - 20, 12.5, { mono: true });
      D.text(z.g, ln, x + 10, y + 36 + i * 17, { s, mono: true, c: o.err && i === Math.min(lines.length, max) - 1 ? '#fca5a5' : '#e5e7eb' });
    });
  }
  const list = s => String(s).split(/[\s,]+/).map(x => x.trim()).filter(Boolean);
  const nums = s => list(String(s).replace(/−/g, '-')).map(Number).filter(v => !isNaN(v));

  /* ---------- Python values in JavaScript ----------
     A value is {t: 'int' | 'float' | 'str' | 'bool' | 'none' | 'list', v}. Ints are BigInt so big numbers stay exact. */
  function pyFloat(v) {
    if (Number.isNaN(v)) return 'nan';
    if (!isFinite(v)) return v > 0 ? 'inf' : '-inf';
    if (v === 0) return Object.is(v, -0) ? '-0.0' : '0.0';
    const a = Math.abs(v);
    if (a >= 1e16 || a < 1e-4) return v.toExponential().replace(/e([+-])(\d)$/, 'e$10$2');
    const s = String(v);
    return /[.e]/.test(s) ? s : s + '.0';
  }
  function repr(x) {
    if (x.t === 'int') return x.v.toString();
    if (x.t === 'float') return pyFloat(x.v);
    if (x.t === 'bool') return x.v ? 'True' : 'False';
    if (x.t === 'none') return 'None';
    if (x.t === 'str') return x.v.includes("'") && !x.v.includes('"') ? '"' + x.v + '"' : "'" + x.v.replace(/'/g, "\\'") + "'";
    if (x.t === 'list') return '[' + x.v.map(repr).join(', ') + ']';
    return '?';
  }
  const str = x => x.t === 'str' ? x.v : repr(x);
  const tname = x => ({ int: 'int', float: 'float', str: 'str', bool: 'bool', none: 'NoneType', list: 'list' }[x.t]);
  /* read one literal the way Python would: 42, 3.5, 1e3, 'text', "text", True, False, None */
  function literal(tok) {
    const s = tok.trim();
    if (/^(['"]).*\1$/.test(s)) return { t: 'str', v: s.slice(1, -1) };
    if (/^[+-]?\d[\d_]*$/.test(s)) return { t: 'int', v: BigInt(s.replace(/_/g, '')) };
    if (/^[+-]?(\d[\d_]*)?\.?\d*([eE][+-]?\d+)?$/.test(s) && /\d/.test(s)) return { t: 'float', v: parseFloat(s.replace(/_/g, '')) };
    if (s === 'True' || s === 'False') return { t: 'bool', v: s === 'True' };
    if (s === 'None') return { t: 'none', v: null };
    return null;
  }
  /* split "a, 'b, c', 3" on commas that are outside quotes */
  function splitArgs(s) {
    const out = [];
    let cur = '', q = '';
    for (const ch of String(s)) {
      if (q) { cur += ch; if (ch === q) q = ''; continue; }
      if (ch === '"' || ch === "'") { q = ch; cur += ch; continue; }
      if (ch === ',') { out.push(cur.trim()); cur = ''; continue; }
      cur += ch;
    }
    if (cur.trim()) out.push(cur.trim());
    return out;
  }
  const showWS = s => String(s).replace(/\n/g, '↵').replace(/ /g, '·');

  return { trace, box, head, codeView, consoleBox, list, nums, esc, D, tag, wrap, rr, tw, fit, MONO, pyFloat, repr, str, tname, literal, splitArgs, showWS };
})();

/* =====================================================================================================
   Core 1.1  print(): from arguments to the screen
   ===================================================================================================== */
(() => {
  const { trace, box, head, consoleBox, D, tag, wrap, repr, str, tname, literal, splitArgs, showWS, esc } = PYZ;
  trace('pyprint', {
    title: 'What print() does with your values',
    sub: 'Type the values you want to print, pick sep and end, then step through. A second print() shows where the next output starts.',
    W: 600, H: 330,
    params: [
      { k: 'args', label: 'Values inside print( ... ), separated by commas', type: 'text', v: '"Total", 3, "apples", 2.50', help: 'Use text in quotes, whole numbers, decimals, True, False or None. A word without quotes is a variable name.' },
      { k: 'sep', label: 'sep (what goes between the values)', type: 'select', v: ' ', opts: [[' ', 'a space (the default)'], ['', 'nothing'], [', ', 'a comma and a space'], ['-', 'a dash'], ['\n', 'a new line']] },
      { k: 'end', label: 'end (what goes after the last value)', type: 'select', v: '\n', opts: [['\n', 'a new line (the default)'], ['', 'nothing'], [' ', 'a space'], ['!\n', 'an ! and a new line']] },
      { k: 'second', label: 'Then run print("Done") as a second line', type: 'check', v: true }
    ],
    tips: [
      { t: 'Set sep to nothing. The values stick together: "Total3apples2.5". print() does not add spaces you did not ask for.', set: { sep: '' }, play: true },
      { t: 'Set end to nothing. "Done" from the second print() now appears on the same line, because the first print() did not move to a new line.', set: { end: '', second: true }, play: true },
      { t: 'Type a word without quotes, such as total. Python looks for a variable called total, cannot find one, and stops with a NameError before anything is printed.', set: { args: '"Total", total' }, play: true }
    ],
    frames(p) {
      const fr = [];
      const toks = splitArgs(p.args);
      const vals = [];
      fr.push({ ph: 'args', toks, vals: [], say: `Python calls print() with ${toks.length} argument${toks.length === 1 ? '' : 's'}: ${toks.map(t => '<code>' + esc(t) + '</code>').join(', ')}. First it works out the value of each one, from left to right.` });
      for (let i = 0; i < toks.length; i++) {
        const v = literal(toks[i]);
        if (!v) {
          fr.push({ ph: 'err', toks, vals: vals.slice(), bad: i, out: `NameError: name '${toks[i]}' is not defined`, say: `<code>${esc(toks[i])}</code> has no quotes and is not a number, so Python treats it as a <b>variable name</b>. No variable has that name, so Python stops with <b>NameError</b>. Nothing at all is printed, because print() never got all its values.` });
          return fr;
        }
        vals.push(v);
        fr.push({ ph: 'conv', toks, vals: vals.slice(), cur: i, say: `Argument ${i + 1} is the ${tname(v)} value <code>${esc(repr(v))}</code>. print() turns every value into text with str(), so it becomes <code>${esc(JSON.stringify(str(v)))}</code>${v.t === 'str' ? ' (it is already text, the quotes are not printed)' : ''}.` });
      }
      const text = vals.map(str).join(p.sep);
      fr.push({ ph: 'join', toks, vals, text, say: `Now print() puts the texts in a row with <b>sep</b> between each pair. sep is ${p.sep === ' ' ? 'one space' : p.sep === '' ? 'empty, so nothing goes between them' : '<code>' + esc(JSON.stringify(p.sep)) + '</code>'}. The joined text is <code>${esc(JSON.stringify(text))}</code>.` });
      const full = text + p.end;
      fr.push({ ph: 'end', toks, vals, text, full, say: `At the very end print() adds <b>end</b>, which is ${p.end === '\n' ? 'a new line character, so the next output starts on a fresh line' : p.end === '' ? 'empty, so the cursor stays right after the last character' : '<code>' + esc(JSON.stringify(p.end)) + '</code>'}.` });
      fr.push({ ph: 'show', toks, vals, text, full, out: full, say: 'The finished text goes to the screen (standard output). The dots and arrows in the picture above stand for spaces and new lines. They are not printed.' });
      if (p.second) {
        const out = full + 'Done\n';
        fr.push({ ph: 'show', toks, vals, text, full, out, second: true, say: `The second line <code>print("Done")</code> starts exactly where the cursor was left. ${p.end.endsWith('\n') ? 'The first print() ended with a new line, so Done sits on its own line.' : 'The first print() did not end with a new line, so Done is glued to the same line.'}` });
      }
      return fr;
    },
    paint(z, f) {
      const { g } = z, c = z.col;
      head(z, 'Arguments', 20, 22);
      const n = f.toks.length, w = Math.min(130, (560 - (n - 1) * 8) / Math.max(1, n));
      f.toks.forEach((t, i) => {
        const x = 20 + i * (w + 8);
        const on = f.cur === i, bad = f.bad === i;
        box(z, x, 30, w, 30, t, { mono: true, s: 12, stroke: bad ? c.red : on ? c.cv : c.line, w: on || bad ? 2.5 : 1.5 });
        if (i < f.vals.length) {
          D.arrow(g, x + w / 2, 62, x + w / 2, 80, c.ink2, 1.5);
          box(z, x, 82, w, 28, JSON.stringify(str(f.vals[i])), { mono: true, s: 12, fill: c.bg, stroke: c.cv });
          D.text(g, tname(f.vals[i]), x + w / 2, 124, { a: 'center', s: 10.5, c: c.ink2 });
        }
      });
      if (f.text !== undefined) {
        head(z, 'Joined with sep', 20, 152);
        box(z, 20, 160, 560, 30, showWS(f.text), { mono: true, s: 13, fill: c.bg, stroke: c.cv });
      }
      if (f.full !== undefined) {
        head(z, 'Plus end', 20, 208);
        box(z, 20, 216, 560, 30, showWS(f.full), { mono: true, s: 13, fill: c.bg, stroke: c.orange });
      }
      if (f.out !== undefined) consoleBox(z, f.out, 20, 256, 560, 70, { err: f.ph === 'err' });
    }
  });

  /* =====================================================================================================
     Core 1.1  three kinds of errors: when Python finds each one
     ===================================================================================================== */
  const ERRPROG = {
    none: { lines: ['print("Start")', 'price = 120', 'total = price * 2', 'print("Total:", total)', 'print("End")'], at: -1 },
    syntax: { lines: ['print("Start")', 'price = 120', 'total = price * 2', 'print("Total:", total', 'print("End")'], at: 3,
      msg: 'SyntaxError: \'(\' was never closed', why: 'The bracket opened on line 4 is never closed.' },
    name: { lines: ['print("Start")', 'price = 120', 'total = prise * 2', 'print("Total:", total)', 'print("End")'], at: 2,
      msg: "NameError: name 'prise' is not defined. Did you mean: 'price'?", why: 'prise is spelt wrong, so no variable has that name.' },
    zero: { lines: ['print("Start")', 'price = 120', 'total = price / 0', 'print("Total:", total)', 'print("End")'], at: 2,
      msg: 'ZeroDivisionError: division by zero', why: 'No number can be divided by zero.' },
    type: { lines: ['print("Start")', 'price = 120', 'total = price + "2"', 'print("Total:", total)', 'print("End")'], at: 2,
      msg: "TypeError: unsupported operand type(s) for +: 'int' and 'str'", why: 'A number and a piece of text cannot be added.' },
    logic: { lines: ['print("Start")', 'price = 120', 'total = price + 2', 'print("Total:", total)', 'print("End")'], at: 2, logic: true,
      why: 'We wanted two items, price * 2 = 240, but typed price + 2. Python happily prints 122.' }
  };
  trace('pyerrors', {
    title: 'Syntax, runtime and logic errors: who catches what, and when',
    sub: 'Pick a mistake. Watch Python check the whole file first, then run it line by line.',
    W: 600, H: 300,
    params: [
      { k: 'kind', label: 'Mistake in the program', type: 'select', v: 'syntax', opts: [['none', 'No mistake'], ['syntax', 'Syntax error: a missing bracket'], ['name', 'Runtime error: a misspelt name (NameError)'], ['zero', 'Runtime error: divide by zero'], ['type', 'Runtime error: number plus text (TypeError)'], ['logic', 'Logic error: + instead of *']] }
    ],
    tips: [
      { t: 'Syntax error. Not even "Start" is printed, because Python checks the whole file before it runs line 1.', set: { kind: 'syntax' }, play: true },
      { t: 'Divide by zero. "Start" is printed, then the program crashes on line 3. Lines 4 and 5 never run.', set: { kind: 'zero' }, play: true },
      { t: 'Logic error. No red message at all, the answer is just wrong. Only a test or a careful human finds this kind.', set: { kind: 'logic' }, play: true }
    ],
    frames(p) {
      const P = ERRPROG[p.kind], L = P.lines, fr = [];
      fr.push({ cur: -1, done: [], out: '', ph: 'read', say: 'You run <code>python3 shop.py</code>. Python first reads the <b>whole file</b> and checks the grammar (the syntax) of every line. Nothing runs yet.' });
      if (p.kind === 'syntax') {
        fr.push({ cur: P.at, done: [], out: `  File "shop.py", line 4\n    ${L[3]}\n${P.msg}`, err: true, bad: P.at, say: `The grammar check fails on line 4. ${P.why} This is a <b>syntax error</b>. Python stops before running anything, so even line 1 is not printed.` });
        return fr;
      }
      fr.push({ cur: -1, done: [], out: '', ph: 'ok', say: 'The grammar of every line is fine, so Python turns the file into bytecode and starts running it from line 1.' });
      let out = '', vars = {};
      const done = [];
      for (let i = 0; i < L.length; i++) {
        if (i === P.at && !P.logic) {
          out += `Traceback (most recent call last):\n  File "shop.py", line ${i + 1}\n${P.msg}`;
          fr.push({ cur: i, done: done.slice(), out, err: true, bad: i, say: `Line ${i + 1} runs and fails: ${P.why} This is a <b>runtime error</b> (an exception). It is only found when the line actually runs. The program stops here, so the lines after it never run.` });
          return fr;
        }
        let say = '';
        if (L[i].startsWith('print("Start")')) { out += 'Start\n'; say = 'Line 1 prints Start.'; }
        else if (L[i].startsWith('price')) { vars.price = 120; say = 'Line 2 stores 120 in the variable price.'; }
        else if (L[i].startsWith('total')) { vars.total = P.logic ? 122 : 240; say = `Line 3 works out ${P.logic ? '120 + 2 = 122' : '120 * 2 = 240'} and stores it in total.`; }
        else if (L[i].startsWith('print("Total')) { out += `Total: ${vars.total}\n`; say = `Line 4 prints Total: ${vars.total}.`; }
        else { out += 'End\n'; say = 'Line 5 prints End.'; }
        done.push(i);
        fr.push({ cur: i, done: done.slice(), out, say });
      }
      fr.push({ cur: -1, done, out, say: P.logic ? `The program finished with no error message, but the answer 122 is wrong. ${P.why} This is a <b>logic error</b>. Python cannot know what you meant, so you find it by testing with an answer you already know.` : 'The program finished without any error. Every line ran once, from top to bottom.' });
      return fr;
    },
    paint(z, f) {
      const P = ERRPROG[z.p.kind];
      head(z, 'shop.py', 20, 20);
      PYZ.codeView(z, P.lines, f.cur, 20, 28, 330, { done: f.done, bad: f.bad });
      const c = z.col;
      tag(z.g, f.ph === 'read' ? 'checking the grammar' : f.err ? 'stopped' : 'running', 470, 40, { s: 12, fill: f.err ? c.red : c.cv, stroke: f.err ? c.red : c.cv, c: '#fff' });
      consoleBox(z, f.out || '', 20, 160, 560, 130, { err: f.err });
    }
  });

  /* =====================================================================================================
     Core 1.2  names and objects
     ===================================================================================================== */
  function evalSimple(expr, env) {
    // a value, a name, or two of them joined by + - * with numbers or text
    const m = expr.match(/^(.+?)\s*([+*-])\s*(.+)$/);
    const one = s => {
      const lit = PYZ.literal(s);
      if (lit) return { lit: true, v: lit };
      if (/^[A-Za-z_]\w*$/.test(s)) { if (!(s in env)) throw new Error(`NameError: name '${s}' is not defined`); return { lit: false, id: env[s] }; }
      throw new Error(`Python could not read "${s}". Use a number, text in quotes, True, False, None or a name.`);
    };
    if (m && !/^(['"]).*\1$/.test(expr.trim())) return { op: m[2], a: one(m[1].trim()), b: one(m[3].trim()) };
    return { one: one(expr.trim()) };
  }
  trace('pynames', {
    title: 'Variables are names stuck on objects',
    sub: 'Type a few assignments, one per line. Each step shows the object Python makes and where each name points.',
    W: 600, H: 320,
    params: [
      { k: 'code', label: 'Assignments (name = value, name = other name, or a + b)', type: 'area', v: 'age = 25\nmy_age = age\nage = age + 1\nname = "Asha"\nname = name * 2' }
    ],
    tips: [
      { t: 'Watch line 3. age moves to a new object 26, but my_age still points to 25. Assignment never changes an object, it moves a name.', play: true },
      { t: 'x = 5, then y = x, then x = 7. y still points to 5. Changing what x points to never changes y.', set: { code: 'x = 5\ny = x\nx = 7' }, play: true },
      { t: 'Use a name before giving it a value: total = total + 1. Python stops with NameError, because a name only exists after its first assignment.', set: { code: 'count = 0\ntotal = total + 1' }, play: true }
    ],
    frames(p) {
      const lines = String(p.code).split('\n').map(s => s.trim()).filter(Boolean).slice(0, 7);
      const env = {}, objs = [], fr = [];
      let nextId = 1;
      const make = v => { const o = { id: nextId++, v, refs: 0 }; objs.push(o); return o.id; };
      const find = id => objs.find(o => o.id === id);
      const num = v => v.t === 'int' || v.t === 'float' || v.t === 'bool';
      for (let i = 0; i < lines.length; i++) {
        const m = lines[i].match(/^([A-Za-z_]\w*)\s*=\s*(.+)$/);
        if (!m) throw new Error(`Line ${i + 1} is not an assignment like name = value.`);
        const [, name, expr] = m;
        let e;
        try { e = evalSimple(expr, env); } catch (err) { fr.push({ env: { ...env }, objs: objs.map(o => ({ ...o })), cur: i, lines, err: err.message, say: `Line ${i + 1}: <code>${esc(lines[i])}</code>. ${esc(err.message)}. A name exists only after it has been given a value.` }); return fr; }
        let id, say;
        if (e.one) {
          if (e.one.lit) { id = make(e.one.v); say = `Python makes a new <b>${PYZ.tname(e.one.v)}</b> object with the value <code>${esc(PYZ.repr(e.one.v))}</code> (object #${id}), then sticks the name <b>${name}</b> on it.`; }
          else { id = e.one.id; say = `No new object is made. The name <b>${name}</b> is stuck on the <b>same</b> object #${id} that ${esc(expr.trim())} points to. Two names, one object.`; }
        } else {
          const A = e.a.lit ? e.a.v : find(e.a.id).v, B = e.b.lit ? e.b.v : find(e.b.id).v;
          let r;
          if (e.op === '+' && A.t === 'str' && B.t === 'str') r = { t: 'str', v: A.v + B.v };
          else if (e.op === '*' && A.t === 'str' && B.t === 'int') r = { t: 'str', v: A.v.repeat(Number(B.v)) };
          else if (num(A) && num(B)) {
            if (A.t === 'float' || B.t === 'float') { const x = Number(A.v), y = Number(B.v); r = { t: 'float', v: e.op === '+' ? x + y : e.op === '-' ? x - y : x * y }; }
            else { const x = BigInt(A.v), y = BigInt(B.v); r = { t: 'int', v: e.op === '+' ? x + y : e.op === '-' ? x - y : x * y }; }
          } else {
            fr.push({ env: { ...env }, objs: objs.map(o => ({ ...o })), cur: i, lines, err: 'TypeError', say: `Line ${i + 1}: Python cannot use ${e.op} between a ${PYZ.tname(A)} and a ${PYZ.tname(B)}, so it stops with <b>TypeError</b>.` });
            return fr;
          }
          id = make(r);
          say = `Python works out <code>${esc(PYZ.repr(A))} ${e.op} ${esc(PYZ.repr(B))}</code> = <code>${esc(PYZ.repr(r))}</code>. The result is a <b>new</b> object #${id}. Then the name <b>${name}</b> is moved onto it.`;
        }
        const old = env[name];
        env[name] = id;
        if (old && old !== id) say += ` The old object #${old} is no longer reached by ${name}.`;
        objs.forEach(o => { o.refs = Object.values(env).filter(x => x === o.id).length; });
        fr.push({ env: { ...env }, objs: objs.map(o => ({ ...o })), cur: i, lines, newId: id, name, say: `Line ${i + 1}: <code>${esc(lines[i])}</code>. ${say}` });
      }
      const gone = objs.filter(o => !Object.values(env).includes(o.id));
      fr.push({ env: { ...env }, objs: objs.map(o => ({ ...o })), cur: -1, lines, end: true, say: gone.length ? `Done. Object${gone.length > 1 ? 's' : ''} ${gone.map(o => '#' + o.id).join(', ')} ${gone.length > 1 ? 'have' : 'has'} no name left (reference count 0), so CPython frees ${gone.length > 1 ? 'them' : 'it'} at once.` : 'Done. Every object still has at least one name pointing to it.' });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      head(z, 'Program', 20, 20);
      PYZ.codeView(z, f.lines, f.cur, 20, 28, 210, { s: 12 });
      head(z, 'Names', 260, 20);
      head(z, 'Objects in memory', 420, 20);
      const names = Object.keys(f.env);
      const oy = {};
      f.objs.forEach((o, i) => { oy[o.id] = 30 + i * 40; });
      f.objs.forEach(o => {
        const y = oy[o.id], alive = o.refs > 0;
        box(z, 420, y, 160, 30, '', { stroke: o.id === f.newId ? c.cv : alive ? c.line : c.ink2, w: o.id === f.newId ? 2.5 : 1.5, dash: alive ? null : [4, 3], fill: alive ? c.surf : c.bg });
        D.text(g, '#' + o.id + ' ' + PYZ.tname(o.v), 428, y + 12, { s: 10, c: c.ink2 });
        const s = PYZ.repr(o.v);
        D.text(g, s, 500, y + 22, { a: 'center', s: PYZ.fit(g, s, 140, 13, { mono: true }), mono: true, b: true, c: alive ? c.ink : c.ink2 });
        D.text(g, 'refs ' + o.refs, 576, y + 12, { a: 'right', s: 10, c: alive ? c.green : c.red });
      });
      names.forEach((n, i) => {
        const y = 30 + i * 40;
        box(z, 260, y, 100, 30, n, { mono: true, b: true, stroke: n === f.name ? c.cv : c.line, w: n === f.name ? 2.5 : 1.5 });
        const ty = oy[f.env[n]] + 15;
        D.arrow(g, 362, y + 15, 418, ty, n === f.name ? c.cv : c.ink2, 1.8);
      });
      if (f.err) D.text(g, f.err.split(':')[0], 260, 300, { s: 14, b: true, c: c.red });
    }
  });

  /* =====================================================================================================
     Core 1.2  numeral systems: decimal to binary, octal or hexadecimal and back
     ===================================================================================================== */
  const DIG = '0123456789ABCDEF';
  trace('pybase', {
    title: 'Changing a number to base 2, 8 or 16',
    sub: 'Divide by the base again and again. The remainders, read from the bottom up, are the digits. Python does this inside bin(), oct() and hex().',
    W: 600, H: 330,
    params: [
      { k: 'n', label: 'A whole number (0 to 100000)', type: 'text', v: '156', num: true },
      { k: 'b', label: 'Target base', type: 'select', v: '2', opts: [['2', 'Binary (base 2), bin()'], ['8', 'Octal (base 8), oct()'], ['16', 'Hexadecimal (base 16), hex()']] },
      { k: 'back', label: 'Also show the check back to decimal', type: 'check', v: true }
    ],
    tips: [
      { t: '156 in binary. Eight divisions by 2 give the remainders 0, 0, 1, 1, 1, 0, 0, 1. Read upwards: 10011100, so bin(156) is 0b10011100.', set: { n: 156, b: '2' }, play: true },
      { t: '255 in hexadecimal is FF: 255 = 15 × 16 + 15. That is why colours like #FFFFFF use two hex digits per colour.', set: { n: 255, b: '16' }, play: true },
      { t: '493 in octal is 755. Linux file permissions such as chmod 755 are written in octal.', set: { n: 493, b: '8' }, play: true }
    ],
    frames(p) {
      const n = Math.floor(Number(p.n)), b = Number(p.b);
      if (!(n >= 0) || n > 100000) throw new Error('Please type a whole number from 0 to 100000.');
      const pre = { 2: '0b', 8: '0o', 16: '0x' }[b], fr = [], rows = [];
      fr.push({ rows: [], say: `We want ${n} in base ${b}. Rule: divide by ${b}, write down the remainder, and keep dividing the quotient until it becomes 0.` });
      let q = n;
      if (q === 0) rows.push({ q: 0, d: 0, r: 0 });
      while (q > 0) {
        const r = q % b, nq = Math.floor(q / b);
        rows.push({ q, nq, r });
        fr.push({ rows: rows.slice(), say: `${q} ÷ ${b} = ${nq} remainder <b>${r}</b>${b === 16 && r > 9 ? ` (the digit ${DIG[r]}, because hexadecimal uses A to F for 10 to 15)` : ''}. In Python: <code>${q} // ${b}</code> is ${nq} and <code>${q} % ${b}</code> is ${r}.` });
        q = nq;
      }
      const digits = rows.map(r => DIG[r.r]).reverse().join('') || '0';
      fr.push({ rows, digits, say: `The quotient is 0, so we stop. Read the remainders from the <b>bottom up</b>: <b>${digits}</b>. Python writes it as <code>${pre}${digits.toLowerCase()}</code>, the prefix tells the reader which base it is.` });
      if (p.back) {
        const terms = digits.split('').map((d, i) => ({ d: DIG.indexOf(d), pw: digits.length - 1 - i }));
        fr.push({ rows, digits, terms, say: `Check: each digit is worth digit × ${b}<sup>position</sup>, counting positions from 0 on the right. ${terms.filter(t => t.d).map(t => `${t.d}×${b}<sup>${t.pw}</sup>`).join(' + ') || '0'} = <b>${n}</b>. In Python <code>int("${digits}", ${b})</code> gives ${n}.` });
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, b = Number(z.p.b);
      head(z, 'Division', 20, 20); head(z, 'Remainder', 230, 20);
      const rh = Math.min(26, 290 / Math.max(1, f.rows.length)), fs = Math.min(14, rh * 0.62);
      f.rows.forEach((r, i) => {
        const y = 30 + i * rh;
        D.text(g, `${r.q} ÷ ${b} = ${r.nq ?? 0}`, 20, y + rh * 0.68, { s: fs, mono: true, c: c.ink });
        box(z, 230, y + 1, 44, rh - 3, DIG[r.r], { mono: true, b: true, stroke: c.cv, s: fs });
      });
      if (f.digits) {
        const h = f.rows.length * rh;
        D.arrow(g, 290, 30 + h, 290, 34, c.orange, 2.2);
        D.text(g, 'read upwards', 298, 30 + h / 2, { s: 12, b: true, c: c.orange });
        head(z, 'Result', 400, 20);
        box(z, 400, 30, 180, 36, { 2: '0b', 8: '0o', 16: '0x' }[b] + f.digits.toLowerCase(), { mono: true, b: true, s: 15, stroke: c.green, w: 2.5 });
      }
      if (f.terms) {
        head(z, 'Place values', 400, 96);
        f.terms.slice(0, 8).forEach((t, i) => {
          const y = 104 + i * 26;
          D.text(g, `${DIG[t.d]} × ${b}^${t.pw} = ${t.d * b ** t.pw}`, 400, y + 16, { s: 13, mono: true, c: t.d ? c.ink : c.ink2 });
        });
        if (f.terms.length > 8) D.text(g, `... ${f.terms.length - 8} more digits`, 400, 104 + 8 * 26 + 14, { s: 12, c: c.ink2 });
      }
    }
  });
})();

/* =====================================================================================================
   Core 1.3  operator precedence: Python works out an expression one operation at a time
   ===================================================================================================== */
(() => {
  const { trace, box, head, D, tag, esc, pyFloat } = PYZ;
  const PREC = { 'or': 1, 'and': 2, 'not': 3, '<': 4, '>': 4, '<=': 4, '>=': 4, '==': 4, '!=': 4, '|': 5, '^': 6, '&': 7, '<<': 8, '>>': 8, '+': 9, '-': 9, '*': 10, '/': 10, '//': 10, '%': 10, 'u': 11, '**': 12 };
  const LADDER = [['( )', 'brackets first'], ['**', 'power, right to left'], ['+x  -x  ~x', 'unary sign'], ['*  /  //  %', 'left to right'], ['+  -', 'left to right'], ['<<  >>', 'shifts'], ['&', 'bitwise and'], ['^', 'bitwise xor'], ['|', 'bitwise or'], ['<  <=  >  >=  ==  !=', 'comparisons'], ['not', 'logical not'], ['and', 'logical and'], ['or', 'logical or']];
  const LVL = { '**': 1, 'u': 2, '*': 3, '/': 3, '//': 3, '%': 3, '+': 4, '-': 4, '<<': 5, '>>': 5, '&': 6, '^': 7, '|': 8, '<': 9, '>': 9, '<=': 9, '>=': 9, '==': 9, '!=': 9, 'not': 10, 'and': 11, 'or': 12 };
  function lex(s) {
    const out = [], re = /\s*(\d+\.\d*(?:e[+-]?\d+)?|\.\d+(?:e[+-]?\d+)?|\d+e[+-]?\d+|\d+|\*\*|\/\/|<<|>>|<=|>=|==|!=|and\b|or\b|not\b|True\b|False\b|[-+*/%()<>&|^~])/iy;
    let i = 0;
    s = String(s).trim();
    while (i < s.length) {
      re.lastIndex = i;
      const m = re.exec(s);
      if (!m) throw new Error(`Python cannot read "${s.slice(i, i + 6)}". Use numbers, + - * / // % **, brackets, comparisons, and, or, not.`);
      out.push(m[1]); i = re.lastIndex;
      while (s[i] === ' ') i++;
    }
    return out;
  }
  function parse(toks) {
    let i = 0;
    const peek = () => toks[i], take = () => toks[i++];
    function atom() {
      const t = take();
      if (t === undefined) throw new Error('The expression ends too early.');
      if (t === '(') { const e = expr(0); if (take() !== ')') throw new Error('A bracket is not closed.'); e.paren = (e.paren || 0) + 1; return e; }
      if (t === 'True' || t === 'False') return { v: { t: 'bool', v: t === 'True' } };
      if (/^[\d.]/.test(t)) return { v: /[.eE]/.test(t) ? { t: 'float', v: parseFloat(t) } : { t: 'int', v: BigInt(t) } };
      throw new Error(`Unexpected "${t}".`);
    }
    function power() {
      const base = atom();
      if (peek() === '**') { take(); return { op: '**', a: base, b: unary() }; }
      return base;
    }
    function unary() {
      if (peek() === '-' || peek() === '+' || peek() === '~') { const o = take(); return { op: 'u' + o, a: unary() }; }
      return power();
    }
    function expr(minp) {
      let left;
      if (peek() === 'not') { take(); left = { op: 'not', a: expr(PREC.not) }; }
      else left = unary();
      for (;;) {
        const o = peek();
        if (o === undefined || o === ')' || PREC[o] === undefined || o === 'not' || PREC[o] < minp || o === '**') break;
        take();
        const right = expr(PREC[o] + 1);
        left = { op: o, a: left, b: right };
      }
      return left;
    }
    const e = expr(0);
    if (i < toks.length) throw new Error(`Unexpected "${toks[i]}".`);
    return e;
  }
  const isNum = x => x.t === 'int' || x.t === 'float' || x.t === 'bool';
  const asBig = x => x.t === 'bool' ? (x.v ? 1n : 0n) : x.v;
  const asNum = x => x.t === 'bool' ? (x.v ? 1 : 0) : Number(x.v);
  const show = x => x.t === 'int' ? x.v.toString() : x.t === 'float' ? pyFloat(x.v) : (x.v ? 'True' : 'False');
  const truthy = x => x.t === 'float' ? x.v !== 0 : x.t === 'int' ? x.v !== 0n : x.v;
  function apply(op, A, B) {
    const ints = (A.t !== 'float') && (B.t !== 'float');
    const zero = () => { throw new Error('ZeroDivisionError: division by zero'); };
    if (op === '+' || op === '-' || op === '*') {
      if (ints) { const a = asBig(A), b = asBig(B); return { t: 'int', v: op === '+' ? a + b : op === '-' ? a - b : a * b }; }
      const a = asNum(A), b = asNum(B); return { t: 'float', v: op === '+' ? a + b : op === '-' ? a - b : a * b };
    }
    if (op === '/') { if (asNum(B) === 0) zero(); return { t: 'float', v: asNum(A) / asNum(B) }; }
    if (op === '//' || op === '%') {
      if (ints) {
        const a = asBig(A), b = asBig(B); if (b === 0n) zero();
        let q = a / b, r = a % b;
        if (r !== 0n && ((r < 0n) !== (b < 0n))) { q -= 1n; r += b; }
        return { t: 'int', v: op === '//' ? q : r };
      }
      const a = asNum(A), b = asNum(B); if (b === 0) zero();
      const q = Math.floor(a / b);
      return { t: 'float', v: op === '//' ? q : a - b * q };
    }
    if (op === '**') {
      if (ints && asBig(B) >= 0n) { if (asBig(B) > 2000n) throw new Error('The power is too big to show here.'); return { t: 'int', v: asBig(A) ** asBig(B) }; }
      if (asNum(A) === 0 && asNum(B) < 0) throw new Error('ZeroDivisionError: zero cannot be raised to a negative power');
      return { t: 'float', v: Math.pow(asNum(A), asNum(B)) };
    }
    if (['&', '|', '^', '<<', '>>'].includes(op)) {
      if (!ints) throw new Error(`TypeError: ${op} needs whole numbers, not a float`);
      const a = asBig(A), b = asBig(B);
      if ((op === '<<' || op === '>>') && b < 0n) throw new Error('ValueError: negative shift count');
      if (op === '<<' && b > 512n) throw new Error('The shift is too big to show here.');
      return { t: 'int', v: op === '&' ? a & b : op === '|' ? a | b : op === '^' ? a ^ b : op === '<<' ? a << b : a >> b };
    }
    const a = A.t === 'float' || B.t === 'float' ? asNum(A) : asBig(A), b = A.t === 'float' || B.t === 'float' ? asNum(B) : asBig(B);
    const r = op === '<' ? a < b : op === '>' ? a > b : op === '<=' ? a <= b : op === '>=' ? a >= b : op === '==' ? a == b : a != b;  // eslint-disable-line eqeqeq
    return { t: 'bool', v: r };
  }
  const WHY = {
    '**': 'Power ** has the highest priority of all the operators here, and a chain of ** is done from the right.',
    'u-': 'A minus sign in front of a value (unary minus) comes after ** but before * and +. So -2 ** 2 is -(2 ** 2) = -4.',
    'u+': 'A plus sign in front of a value leaves it as it is.',
    'u~': '~x flips every bit. For whole numbers ~x is always -x - 1.',
    '*': '* / // % share one level and run from left to right, before + and -.',
    '/': 'True division / always gives a float, even 6 / 3 = 2.0.',
    '//': 'Floor division // divides and then rounds <b>down</b> to the next whole number (towards minus infinity).',
    '%': 'Modulo % gives the remainder. In Python the remainder has the same sign as the number you divide by.',
    '+': '+ and - come after * / // %, from left to right.',
    '-': '+ and - come after * / // %, from left to right.'
  };
  function render(n, hl) {
    // returns [{t: text, on: bool}] pieces, n.val is set once the node is worked out
    let parts;
    if (n.val) parts = [{ t: show(n.val), on: n === hl }];
    else if (n.v) parts = [{ t: show(n.v) }];
    else if (n.op.startsWith('u')) parts = [{ t: n.op.slice(1) }, ...render(n.a, hl)];
    else if (n.op === 'not') parts = [{ t: 'not ' }, ...render(n.a, hl)];
    else parts = [...render(n.a, hl), { t: ' ' + n.op + ' ' }, ...render(n.b, hl)];
    if (n.paren && !n.val) parts = [{ t: '('.repeat(n.paren) }, ...parts, { t: ')'.repeat(n.paren) }];
    if (n === hl && !n.val) parts.forEach(p => { p.on = true; });
    return parts;
  }
  trace('pyprec', {
    title: 'How Python works out an expression, one operation at a time',
    sub: 'Type any expression with numbers. Each step does the one operation Python does next, and says why that one comes first.',
    W: 600, H: 330,
    params: [
      { k: 'e', label: 'Expression', type: 'text', v: '2 + 3 * 4 ** 2 // 5 - -7 % 3', help: 'You can use + - * / // % ** ( ) < > == != and or not, True and False.' }
    ],
    tips: [
      { t: '-2 ** 2 gives -4, not 4: ** is done before the minus sign in front.', set: { e: '-2 ** 2' }, play: true },
      { t: '2 ** 3 ** 2 is 2 ** 9 = 512, because a chain of ** runs from the right.', set: { e: '2 ** 3 ** 2' }, play: true },
      { t: '-7 // 2 is -4 and -7 % 2 is 1. Floor division rounds down, towards minus infinity, and (-4) × 2 + 1 = -7.', set: { e: '-7 // 2 + -7 % 2' }, play: true },
      { t: '0.1 + 0.2 == 0.3 is False. The float 0.1 + 0.2 is really 0.30000000000000004.', set: { e: '0.1 + 0.2 == 0.3' }, play: true },
      { t: 'and stops early: 5 > 9 and 1 / 0 > 1 gives False without ever dividing by zero (short circuit).', set: { e: '5 > 9 and 1 / 0 > 1' }, play: true }
    ],
    frames(p) {
      const root = parse(lex(p.e)), fr = [];
      fr.push({ root, hl: null, hist: [], say: 'Python reads the whole expression and builds a tree from the priority rules (the ladder on the right). Then it works out the operations one by one, always finishing the left side of an operator before the right side.' });
      const hist = [];
      const snap = (n, say, lvl) => { const pieces = render(root, n); hist.push(pieces.map(x => x.t).join('')); fr.push({ root, hl: n, pieces, hist: hist.slice(), lvl, say }); };
      function ev(n) {
        if (n.v) return n.v;
        if (n.op === 'and' || n.op === 'or') {
          const A = ev(n.a);
          const t = truthy(A);
          if ((n.op === 'and' && !t) || (n.op === 'or' && t)) {
            n.val = A; snap(n, `<b>${n.op}</b> looks at the left side first. It is ${show(A)}, so the answer is already known and the right side is <b>never worked out</b> (short circuit). The result is ${show(A)}.`, LVL[n.op]);
            return A;
          }
          const B = ev(n.b);
          n.val = B; snap(n, `The left side of <b>${n.op}</b> is ${show(A)}, which does not decide the answer, so ${n.op} gives back the right side: ${show(B)}.`, LVL[n.op]);
          return B;
        }
        if (n.op === 'not') { const A = ev(n.a); n.val = { t: 'bool', v: !truthy(A) }; snap(n, `not flips the truth value: not ${show(A)} is ${show(n.val)}.`, LVL.not); return n.val; }
        if (n.op.startsWith('u')) {
          const A = ev(n.a);
          if (!isNum(A)) throw new Error('A sign needs a number.');
          if (n.op === 'u~') { if (A.t === 'float') throw new Error("TypeError: bad operand type for unary ~: 'float'"); n.val = { t: 'int', v: -asBig(A) - 1n }; }
          else if (n.op === 'u-') n.val = A.t === 'float' ? { t: 'float', v: -A.v } : { t: 'int', v: -asBig(A) };
          else n.val = A.t === 'bool' ? { t: 'int', v: asBig(A) } : A;
          snap(n, `${WHY[n.op]} ${n.op.slice(1)}${show(A)} = <b>${show(n.val)}</b>.`, LVL.u);
          return n.val;
        }
        const A = ev(n.a), B = ev(n.b);
        n.val = apply(n.op, A, B);
        let extra = '';
        if (n.op === '//' || n.op === '%') extra = ` Check: ${show(A)} = (${show(apply('//', A, B))}) × ${show(B)} + ${show(apply('%', A, B))}.`;
        if (n.op === '/' && n.val.t === 'float') extra = '';
        const why = WHY[n.op] || (LVL[n.op] === 9 ? 'Comparisons come after all the arithmetic and give True or False.' : 'Bit operators come after + and - but before comparisons.');
        snap(n, `${why} ${show(A)} ${n.op} ${show(B)} = <b>${show(n.val)}</b>.${extra}`, LVL[n.op]);
        return n.val;
      }
      const ans = ev(root);
      fr.push({ root, hl: null, pieces: [{ t: show(ans), on: true }], hist, lvl: 0, done: true, say: `Finished. The value of the whole expression is <b>${show(ans)}</b> (type ${ans.t}). Type the same line into Python to check it.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      head(z, 'Working, one line per step', 16, 18);
      const lines = f.hist.slice(-9);
      lines.forEach((ln, i) => {
        const last = i === lines.length - 1 && f.pieces;
        const s = PYZ.fit(g, ln, 360, 14, { mono: true });
        if (last) {
          let x = 16;
          f.pieces.forEach(pc => {
            const w = PYZ.tw(g, pc.t, { s, mono: true });
            if (pc.on) PYZ.rr(g, x - 2, 30 + i * 30, w + 4, 24, 5, { fill: c.dark ? '#1e3a5f' : '#dbeafe', stroke: c.cv });
            D.text(g, pc.t, x, 47 + i * 30, { s, mono: true, b: pc.on, c: c.ink });
            x += w;
          });
        } else D.text(g, ln, 16, 47 + i * 30, { s, mono: true, c: c.ink2 });
      });
      if (!f.hist.length) D.text(g, z.p.e, 16, 47, { s: 14, mono: true, c: c.ink });
      head(z, 'Priority, highest first', 400, 18);
      LADDER.forEach(([o, d], i) => {
        const on = f.lvl === i + 1;
        PYZ.rr(g, 400, 26 + i * 23, 190, 21, 5, { fill: on ? c.cv : c.surf, stroke: on ? c.cv : c.line });
        D.text(g, o, 408, 41 + i * 23, { s: 11.5, mono: true, b: true, c: on ? '#fff' : c.ink });
        D.text(g, d, 584, 41 + i * 23, { s: 10.5, a: 'right', c: on ? '#fff' : c.ink2 });
      });
    }
  });

  /* =====================================================================================================
     Core 1.3  bitwise operators on two whole numbers
     ===================================================================================================== */
  const bits = (v, n) => { let s = ''; for (let i = n - 1; i >= 0; i--) s += (BigInt.asUintN(n, BigInt(v)) >> BigInt(i)) & 1n ? '1' : '0'; return s; };
  trace('pybits', {
    title: 'Bitwise operators, bit by bit',
    sub: 'Each whole number is a row of bits. & | ^ work on each column. ~ flips every bit. << and >> slide the row.',
    W: 600, H: 300,
    params: [
      { k: 'a', label: 'a', type: 'range', v: 12, min: -16, max: 255 },
      { k: 'b', label: 'b (or the shift amount)', type: 'range', v: 10, min: 0, max: 255 },
      { k: 'op', label: 'Operator', type: 'select', v: '&', opts: [['&', 'a & b  (and: 1 only if both are 1)'], ['|', 'a | b  (or: 1 if either is 1)'], ['^', 'a ^ b  (xor: 1 if they differ)'], ['~', '~a  (not: flip every bit)'], ['<<', 'a << b  (shift left)'], ['>>', 'a >> b  (shift right)']] }
    ],
    tips: [
      { t: '12 & 10 = 8. Only the column worth 8 has a 1 in both numbers.', set: { a: 12, b: 10, op: '&' }, play: true },
      { t: '~12 = -13. Python uses two\'s complement for negative numbers, so ~x is always -x - 1.', set: { a: 12, op: '~' }, play: true },
      { t: '5 << 3 = 40. Shifting left by k multiplies by 2 to the power k: 5 × 8 = 40.', set: { a: 5, b: 3, op: '<<' }, play: true },
      { t: 'x & 1 tells you if x is odd: the last bit is 1 only for odd numbers. Try a = 13, b = 1.', set: { a: 13, b: 1, op: '&' }, play: true }
    ],
    frames(p) {
      const a = Math.round(p.a), b = Math.round(p.b), op = p.op, fr = [];
      const shift = op === '<<' || op === '>>';
      if (shift && b > 12) throw new Error('Use a shift amount from 0 to 12 so the bits fit on the screen.');
      const N = 16;
      fr.push({ rows: [['a', a]], say: `a = ${a} written in binary with ${N} bits: <code>${bits(a, N)}</code>. ${a < 0 ? 'It is negative, so Python shows it as if it had endless 1s on the left (two\'s complement).' : 'Each bit is worth 1, 2, 4, 8, ... from the right.'}` });
      if (op === '~') {
        const r = -a - 1;
        fr.push({ rows: [['a', a], ['~a', r]], flip: true, say: `~ flips every bit: 0 becomes 1 and 1 becomes 0. The new row <code>${bits(r, N)}</code> means ${r}. Rule to remember: <b>~x = -x - 1</b>, so ~${a} = ${r}.` });
        return fr;
      }
      if (shift) {
        const r = op === '<<' ? a * 2 ** b : Math.floor(a / 2 ** b);
        fr.push({ rows: [['a', a], [`a ${op} ${b}`, r]], say: `${op === '<<' ? 'Shift left' : 'Shift right'} by ${b}: every bit moves ${b} place${b === 1 ? '' : 's'} to the ${op === '<<' ? 'left and 0s come in on the right' : 'right and the bits that fall off the end are lost'}. ${op === '<<' ? `That is a × 2<sup>${b}</sup> = ${a} × ${2 ** b} = <b>${r}</b>.` : `That is a // 2<sup>${b}</sup> = ${a} // ${2 ** b} = <b>${r}</b> (rounded down).`}` });
        return fr;
      }
      fr.push({ rows: [['a', a], ['b', b]], say: `b = ${b} is <code>${bits(b, N)}</code>. Now ${op} looks at each column on its own.` });
      const f = op === '&' ? (x, y) => x & y : op === '|' ? (x, y) => x | y : (x, y) => x ^ y;
      const r = f(a, b);
      const sa = bits(a, N), sb = bits(b, N), sr = bits(r, N);
      const cols = [];
      for (let i = 0; i < N; i++) if (sa[i] === '1' || sb[i] === '1') cols.push(i);
      cols.slice(-6).forEach(i => {
        const w = 2 ** (N - 1 - i);
        fr.push({ rows: [['a', a], ['b', b]], col: i, part: sr.slice(0, i + 1), say: `Column worth ${w}: a has ${sa[i]}, b has ${sb[i]}. ${op === '&' ? 'and gives 1 only if both are 1' : op === '|' ? 'or gives 1 if at least one is 1' : 'xor gives 1 only if they are different'}, so the result bit is <b>${sr[i]}</b>.` });
      });
      fr.push({ rows: [['a', a], ['b', b], [`a ${op} b`, r]], say: `All columns done. The result <code>${sr}</code> is <b>${r}</b>. So ${a} ${op} ${b} = ${r}.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g, N = 16, cw = 26, x0 = 150;
      for (let i = 0; i < N; i++) D.text(g, String(2 ** (N - 1 - i)), x0 + i * cw + cw / 2, 30, { a: 'center', s: 8.5, c: c.ink2 });
      f.rows.forEach(([lab, v], r) => {
        const y = 44 + r * 46, s = bits(v, N);
        D.text(g, lab, 16, y + 22, { s: 14, b: true, mono: true, c: c.ink });
        D.text(g, '= ' + v, 16, y + 38, { s: 11, mono: true, c: c.ink2 });
        for (let i = 0; i < N; i++) {
          const on = f.col === i;
          box(z, x0 + i * cw, y, cw - 3, 30, s[i], { mono: true, b: s[i] === '1', fill: s[i] === '1' ? (c.dark ? '#1e3a5f' : '#dbeafe') : c.surf, stroke: on ? c.orange : c.line, w: on ? 2.5 : 1 });
        }
      });
      if (f.part !== undefined) {
        const y = 44 + f.rows.length * 46;
        D.text(g, 'result', 16, y + 22, { s: 14, b: true, c: c.cv });
        for (let i = 0; i < f.part.length; i++) if (f.part[i] === '1' || i >= N - 6 || i === f.col) box(z, x0 + i * cw, y, cw - 3, 30, f.part[i], { mono: true, b: true, stroke: c.cv });
      }
    }
  });

  /* =====================================================================================================
     Core 1.3  floats: how a decimal number is stored in 64 bits (IEEE 754)
     ===================================================================================================== */
  function exactDecimal(x) {
    // the exact decimal value of a double, as a string
    const dv = new DataView(new ArrayBuffer(8)); dv.setFloat64(0, x);
    const raw = dv.getBigUint64(0), neg = raw >> 63n, ex = Number((raw >> 52n) & 0x7ffn), fr = raw & ((1n << 52n) - 1n);
    if (ex === 0x7ff) return 'not a finite number';
    let m = ex === 0 ? fr : fr | (1n << 52n), e = (ex === 0 ? 1 : ex) - 1075;
    let s;
    if (e >= 0) s = (m << BigInt(e)).toString();
    else { const k = -e, num = m * 5n ** BigInt(k); let t = num.toString().padStart(k + 1, '0'); s = t.slice(0, t.length - k) + '.' + t.slice(t.length - k); s = s.replace(/0+$/, '').replace(/\.$/, ''); }
    return (neg ? '-' : '') + s;
  }
  PYZ.exactDecimal = exactDecimal;
  trace('pyfloat', {
    title: 'Why 0.1 is not exactly 0.1: a float inside the computer',
    sub: 'A float is stored as sign, exponent and 52 bits of fraction, all in base 2. Most decimals never end in base 2, so they are rounded.',
    W: 600, H: 320,
    params: [
      { k: 'x', label: 'A decimal number', type: 'text', v: '0.1' },
      { k: 'n', label: 'Fraction steps to show', type: 'range', v: 10, min: 4, max: 16 }
    ],
    tips: [
      { t: '0.1 in binary is 0.000110011001100... and the 1100 repeats for ever, so it must be cut and rounded.', set: { x: '0.1' }, play: true },
      { t: '0.5 and 0.375 are exact: 0.5 = 1/2 and 0.375 = 3/8 are made of halves, quarters and eighths.', set: { x: '0.375' }, play: true },
      { t: '2.675 is stored as 2.67499999... That is why round(2.675, 2) gives 2.67 in Python.', set: { x: '2.675' }, play: true }
    ],
    frames(p) {
      const x = parseFloat(String(p.x).replace(/_/g, ''));
      if (!isFinite(x)) throw new Error('Please type a decimal number such as 0.1 or 2.675.');
      const fr = [], a = Math.abs(x);
      const ip = Math.floor(a);
      let f = a - ip;
      fr.push({ ph: 1, x, say: `We store ${p.x}. The <b>sign bit</b> is ${x < 0 || Object.is(x, -0) ? '1 (negative)' : '0 (positive)'}. Now we write the number in base 2: the whole part ${ip} is <code>${ip.toString(2)}</code>.` });
      const digs = [];
      let ff = f;
      for (let i = 0; i < p.n; i++) {
        if (ff === 0) break;
        const t = ff * 2, d = t >= 1 ? 1 : 0;
        digs.push({ from: ff, t, d });
        fr.push({ ph: 2, x, digs: digs.slice(), say: `Fraction part: ${+ff.toPrecision(12)} × 2 = ${+t.toPrecision(12)}. The whole part of that, <b>${d}</b>, is the next binary digit. Keep the part after the point and repeat.` });
        ff = t - d;
      }
      const ends = ff === 0;
      const dv = new DataView(new ArrayBuffer(8)); dv.setFloat64(0, x);
      const raw = dv.getBigUint64(0), exb = Number((raw >> 52n) & 0x7ffn), man = (raw & ((1n << 52n) - 1n)).toString(2).padStart(52, '0');
      fr.push({ ph: 3, x, digs, ends, say: ends ? 'The fraction reached 0, so this number has an exact binary form. It is stored with no error.' : 'The fraction never reaches 0. The digits go on for ever, so the computer must stop after 52 bits and round. This rounding is the tiny error you see in Python.' });
      const e = exb - 1023;
      fr.push({ ph: 4, x, digs, ends, exb, e, man, say: `The number is written as 1.something × 2<sup>${e}</sup> (normalised). The exponent is stored as ${e} + 1023 = <b>${exb}</b> in 11 bits: <code>${exb.toString(2).padStart(11, '0')}</code>. The 52 bits after the leading 1 are the fraction (mantissa).` });
      const exact = exactDecimal(x);
      fr.push({ ph: 5, x, digs, ends, exb, e, man, exact, say: `The value really stored is <b>${exact.length > 60 ? exact.slice(0, 60) + '...' : exact}</b>. Python prints the shortest text that turns back into the same bits, ${PYZ.pyFloat(x)}, so you normally do not see the error. <code>from decimal import Decimal</code> then <code>Decimal(${p.x})</code> shows the exact value.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      head(z, 'Fraction × 2, again and again', 16, 18);
      (f.digs || []).slice(-8).forEach((d, i) => {
        D.text(g, `${(+d.from.toPrecision(8))} × 2 = ${(+d.t.toPrecision(8))}`, 16, 40 + i * 20, { s: 12, mono: true, c: c.ink });
        box(z, 230, 27 + i * 20, 22, 18, String(d.d), { mono: true, b: true, s: 11, stroke: c.cv });
      });
      if (f.digs && f.digs.length) {
        head(z, 'Binary so far', 290, 18);
        const s = Math.floor(Math.abs(f.x)).toString(2) + '.' + f.digs.map(d => d.d).join('') + (f.ph >= 3 && !f.ends ? '...' : '');
        D.text(g, s, 290, 40, { s: PYZ.fit(g, s, 300, 14, { mono: true }), mono: true, b: true, c: c.cv });
      }
      if (f.ph >= 4) {
        const y = 200;
        head(z, '64 bits in memory', 16, y - 8);
        const w = 568 / 64;
        const all = (f.x < 0 ? '1' : '0') + f.exb.toString(2).padStart(11, '0') + f.man;
        for (let i = 0; i < 64; i++) {
          const col = i === 0 ? c.red : i < 12 ? c.orange : c.cv;
          PYZ.rr(g, 16 + i * w, y, w - 1, 24, 2, { fill: all[i] === '1' ? col : c.surf, stroke: col, w: 1 });
        }
        D.text(g, 'sign 1 bit', 16, y + 40, { s: 11, b: true, c: c.red });
        D.text(g, `exponent 11 bits = ${f.exb}`, 60, y + 40, { s: 11, b: true, c: c.orange });
        D.text(g, 'fraction 52 bits', 584, y + 40, { s: 11, b: true, c: c.cv, a: 'right' });
      }
      if (f.exact) {
        const s = 'stored: ' + f.exact;
        D.text(g, s.length > 70 ? s.slice(0, 70) + '...' : s, 16, 290, { s: 12, mono: true, b: true, c: c.ink });
      }
    }
  });
})();

/* =====================================================================================================
   Core 1.4  input() always gives text, and the format specification mini language
   ===================================================================================================== */
(() => {
  const { trace, box, head, D, tag, esc, consoleBox } = PYZ;
  trace('pyinput', {
    title: 'input() gives text. int() and float() turn it into a number',
    sub: 'Type what the user types, pick a conversion, and watch each step, including the errors beginners meet.',
    W: 600, H: 290,
    params: [
      { k: 'typed', label: 'What the user types', type: 'text', v: ' 42 ' },
      { k: 'conv', label: 'Code', type: 'select', v: 'int', opts: [['none', 'age = input("Age: ")'], ['int', 'age = int(input("Age: "))'], ['float', 'age = float(input("Age: "))']] },
      { k: 'next', label: 'Then', type: 'select', v: 'add', opts: [['add', 'print(age + 1)'], ['mul', 'print(age * 2)']] }
    ],
    tips: [
      { t: 'No conversion and age + 1: text plus a number gives TypeError. This is the most common beginner error with input().', set: { conv: 'none', next: 'add', typed: '42' }, play: true },
      { t: 'No conversion and age * 2: text times 2 repeats it, so "42" * 2 is "4242", not 84.', set: { conv: 'none', next: 'mul', typed: '42' }, play: true },
      { t: 'int("3.5") fails with ValueError. Use float() for decimals, or int(float(text)) to cut off the decimal part.', set: { conv: 'int', typed: '3.5' }, play: true }
    ],
    frames(p) {
      const fr = [], code = { none: 'age = input("Age: ")', int: 'age = int(input("Age: "))', float: 'age = float(input("Age: "))' }[p.conv];
      const lines = [code, p.next === 'add' ? 'print(age + 1)' : 'print(age * 2)'];
      const typed = String(p.typed);
      fr.push({ lines, cur: 0, out: 'Age: ', say: 'input("Age: ") prints the prompt <code>Age: </code> and waits. The program is paused until the user presses Enter.' });
      fr.push({ lines, cur: 0, out: 'Age: ' + typed, val: JSON.stringify(typed), vt: 'str', say: `The user types <code>${esc(typed)}</code> and presses Enter. input() returns it as <b>text</b> (str): <code>${esc(JSON.stringify(typed))}</code>. The Enter key itself is not included. input() <b>never</b> gives a number.` });
      let v = { t: 'str', v: typed };
      if (p.conv !== 'none') {
        const s = typed.trim();
        const okInt = /^[+-]?\d[\d_]*$/.test(s) && !/__|_$/.test(s), okFloat = /^[+-]?(\d[\d_]*\.?\d*|\.\d+)([eE][+-]?\d+)?$/.test(s) || /^[+-]?(inf|infinity|nan)$/i.test(s);
        if ((p.conv === 'int' && !okInt) || (p.conv === 'float' && !okFloat)) {
          fr.push({ lines, cur: 0, out: `Age: ${typed}\nValueError: invalid literal for ${p.conv === 'int' ? "int() with base 10" : 'float()'}: ${JSON.stringify(typed).replace(/"/g, "'")}`, err: true, say: `${p.conv}() cannot read <code>${esc(typed)}</code> as a ${p.conv === 'int' ? 'whole number' : 'number'}, so it stops with <b>ValueError</b>. ${p.conv === 'int' && okFloat ? 'int() does not accept a decimal point in text. float() would.' : 'Only digits, an optional sign and spaces around them are allowed.'}` });
          return fr;
        }
        v = p.conv === 'int' ? { t: 'int', v: BigInt(s.replace(/_/g, '')) } : { t: 'float', v: parseFloat(s.replace(/_/g, '')) };
        fr.push({ lines, cur: 0, out: 'Age: ' + typed, val: PYZ.repr(v), vt: v.t, say: `${p.conv}() reads the text. Spaces at both ends are ignored. The result is the ${v.t} <b>${PYZ.repr(v)}</b>, and the name age now points to it.` });
      }
      let out, say, err = false;
      if (p.next === 'add') {
        if (v.t === 'str') { out = 'TypeError: can only concatenate str (not "int") to str'; err = true; say = 'age is text, and Python will not add text and a number. It stops with <b>TypeError</b>. Wrap input() in int() or float() first.'; }
        else { const r = v.t === 'int' ? { t: 'int', v: v.v + 1n } : { t: 'float', v: v.v + 1 }; out = PYZ.repr(r); say = `age + 1 = ${PYZ.repr(r)}. It works because age is a number.`; }
      } else {
        if (v.t === 'str') { const r = v.v.repeat(2); out = r; say = `Text times a whole number repeats the text: ${esc(JSON.stringify(v.v))} * 2 is ${esc(JSON.stringify(r))}. No error, but probably not what you wanted, a logic error.`; }
        else { const r = v.t === 'int' ? { t: 'int', v: v.v * 2n } : { t: 'float', v: v.v * 2 }; out = PYZ.repr(r); say = `age * 2 = ${PYZ.repr(r)}.`; }
      }
      fr.push({ lines, cur: 1, out: `Age: ${typed}\n${out}`, val: PYZ.repr(v), vt: v.t, err, say });
      return fr;
    },
    paint(z, f) {
      const c = z.col;
      head(z, 'Program', 16, 18);
      PYZ.codeView(z, f.lines, f.cur, 16, 26, 330);
      if (f.val) { head(z, 'age', 380, 18); box(z, 380, 26, 200, 34, f.val, { mono: true, b: true, stroke: c.cv }); D.text(z.g, 'type: ' + f.vt, 480, 76, { a: 'center', s: 12, c: c.ink2 }); }
      consoleBox(z, f.out, 16, 120, 568, 160, { err: f.err });
    }
  });

  /* ---------- format specification mini language ---------- */
  function fixedStr(x, p) {
    // Python style fixed point: round the exact binary value half to even
    const ex = PYZ.exactDecimal(Math.abs(x));
    let [ip, fp = ''] = ex.split('.');
    fp = fp.padEnd(p + 1, '0');
    let keep = ip + fp.slice(0, p), rest = fp.slice(p);
    const up = rest[0] > '5' || (rest[0] === '5' && (/[1-9]/.test(rest.slice(1)) || (+keep[keep.length - 1] % 2 === 1)));
    let n = BigInt(keep) + (up ? 1n : 0n);
    let s = n.toString().padStart(p + 1, '0');
    s = p ? s.slice(0, s.length - p) + '.' + s.slice(s.length - p) : s;
    return (x < 0 || Object.is(x, -0) ? '-' : '') + s;
  }
  PYZ.fixedStr = fixedStr;
  function expStr(x, p) {
    if (x === 0) return (Object.is(x, -0) ? '-' : '') + (0).toFixed(p) + 'e+00';
    let e = Math.floor(Math.log10(Math.abs(x)));
    let m = fixedStr(x / 10 ** e, p);
    if (Math.abs(parseFloat(m)) >= 10) { e += 1; m = fixedStr(x / 10 ** e, p); }
    return m + 'e' + (e < 0 ? '-' : '+') + String(Math.abs(e)).padStart(2, '0');
  }
  trace('pyfmt', {
    title: 'Reading a format spec such as >10,.2f, one part at a time',
    sub: 'An f-string like f"{price:>10,.2f}" formats a value with a small code after the colon. Change the value and the code and watch each part do its job.',
    W: 600, H: 300,
    params: [
      { k: 'v', label: 'Value', type: 'text', v: '1234.5678' },
      { k: 'spec', label: 'Format spec (the part after the colon)', type: 'text', v: '*>14,.2f', help: 'Order: fill, align (&lt; &gt; ^ =), sign (+ - space), #, 0, width, grouping (, or _), .precision, type (f e % d b o x X s).' }
    ],
    tips: [
      { t: '.2f rounds to 2 decimal places: the usual way to print money.', set: { v: '1234.5678', spec: '.2f' }, play: true },
      { t: '^20 centres the text in 20 characters. With a fill character, -^20 draws dashes around it.', set: { v: '"Menu"', spec: '-^20' }, play: true },
      { t: '.1% multiplies by 100 and adds a percent sign: 0.256 becomes 25.6%.', set: { v: '0.256', spec: '.1%' }, play: true },
      { t: '08b writes a whole number in binary, padded with 0s to 8 characters.', set: { v: '13', spec: '08b' }, play: true },
      { t: '2.675 with .2f gives 2.67, not 2.68, because 2.675 is really 2.67499999... inside the computer.', set: { v: '2.675', spec: '.2f' }, play: true }
    ],
    frames(p) {
      const lit = PYZ.literal(String(p.v));
      if (!lit) throw new Error('Type a number such as 1234.5 or a text in quotes such as "Menu".');
      const m = String(p.spec).match(/^(?:(.)?([<>^=]))?([+\- ])?(z)?(#)?(0)?(\d+)?([,_])?(?:\.(\d+))?([bcdeEfFgGnosxX%])?$/);
      if (!m) throw new Error('This spec is not valid. Example: *>14,.2f');
      let [, fill, align, sign, , alt, zero, width, group, prec, type] = m;
      const fr = [], parts = [];
      if (zero && !align) { fill = '0'; align = '='; }
      fill = fill || ' ';
      const num = lit.t !== 'str';
      align = align || (num ? '>' : '<');
      width = width ? +width : 0;
      fr.push({ parts: [], say: `Python reads the spec <code>${esc(p.spec || '(empty)')}</code> from left to right. Each part is optional. The value is the ${lit.t} <code>${esc(PYZ.repr(lit))}</code>.` });
      if (!type) type = lit.t === 'str' ? 's' : lit.t === 'int' ? 'd' : '';
      if (lit.t === 'str' && type !== 's') throw new Error(`ValueError: Unknown format code '${type}' for object of type 'str'`);
      if (lit.t === 'float' && 'bdoxXc'.includes(type)) throw new Error(`ValueError: Unknown format code '${type}' for object of type 'float'`);
      if (lit.t === 'str' && (sign || group)) throw new Error('ValueError: sign and grouping are not allowed with text');
      const x = lit.t === 'int' ? Number(lit.v) : lit.v;
      let body;
      const P = prec === undefined ? 6 : +prec;
      if (type === 's') body = prec !== undefined ? lit.v.slice(0, P) : lit.v;
      else if (type === 'f' || type === 'F') body = fixedStr(x, P);
      else if (type === 'e' || type === 'E') body = expStr(x, P);
      else if (type === '%') body = fixedStr(x * 100, P) + '%';
      else if (type === 'd') body = lit.v.toString();
      else if (type === 'b' || type === 'o' || type === 'x' || type === 'X') { const base = { b: 2, o: 8, x: 16, X: 16 }[type]; body = (lit.v < 0n ? '-' : '') + (alt ? '0' + type.toLowerCase().replace('x', 'x') : '') + (lit.v < 0n ? -lit.v : lit.v).toString(base); if (type === 'X') body = body.toUpperCase(); }
      else body = PYZ.str(lit);
      parts.push(['type', type || 'none']);
      fr.push({ parts: parts.slice(), body, say: type === 's' ? `Type s: the text as it is${prec !== undefined ? `, cut to ${P} characters by .${P}` : ''}: <code>${esc(body)}</code>.` : type === 'f' || type === 'F' ? `Type f with precision ${P}: fixed point with exactly ${P} digit${P === 1 ? '' : 's'} after the point, rounded: <code>${body}</code>.` : type === 'e' ? `Type e: scientific notation, one digit before the point and ${P} after, then the power of ten: <code>${body}</code>.` : type === '%' ? `Type %: the value × 100 with ${P} decimals and a % sign: <code>${body}</code>.` : type === 'd' ? `Type d: a whole number in base 10: <code>${body}</code>.` : type === '' ? `No type: the same text str() would give: <code>${esc(body)}</code>.` : `Type ${type}: the whole number in base ${{ b: 2, o: 8, x: 16, X: 16 }[type]}: <code>${body}</code>.` });
      if (group) {
        const neg = body.startsWith('-'), b0 = neg ? body.slice(1) : body;
        const i = b0.search(/[.e%]/), ip = i < 0 ? b0 : b0.slice(0, i), rest = i < 0 ? '' : b0.slice(i);
        const g = 'bxXo'.includes(type) ? 4 : 3;
        const grouped = ip.replace(new RegExp(`\\B(?=(\\w{${g}})+(?!\\w))`, 'g'), group);
        body = (neg ? '-' : '') + grouped + rest;
        fr.push({ parts: parts.slice(), body, say: `Grouping <code>${group}</code> puts a ${group === ',' ? 'comma' : 'underscore'} between every ${g} digits of the whole part, counting from the right: <code>${esc(body)}</code>.` });
      }
      if (sign === '+' && !body.startsWith('-')) { body = '+' + body; fr.push({ parts, body, say: 'Sign <code>+</code>: positive numbers also get a + in front.' }); }
      if (sign === ' ' && !body.startsWith('-')) { body = ' ' + body; fr.push({ parts, body, say: 'Sign space: positive numbers get a space in front, so they line up with negative ones.' }); }
      let out = body;
      if (width > body.length) {
        const padn = width - body.length;
        if (align === '<') out = body + fill.repeat(padn);
        else if (align === '>') out = fill.repeat(padn) + body;
        else if (align === '^') out = fill.repeat(Math.floor(padn / 2)) + body + fill.repeat(padn - Math.floor(padn / 2));
        else { const sg = /^[+\- ]/.test(body) ? body[0] : ''; out = sg + fill.repeat(padn) + body.slice(sg.length); }
        fr.push({ parts, body, out, say: `Width ${width}: the text is ${body.length} characters, so ${padn} fill character${padn === 1 ? '' : 's'} <code>${esc(fill)}</code> ${padn === 1 ? 'is' : 'are'} added. Align <code>${align}</code> means ${{ '<': 'text on the left (the default for text)', '>': 'text on the right (the default for numbers)', '^': 'text in the centre', '=': 'fill goes after the sign, before the digits' }[align]}.` });
      } else if (width) fr.push({ parts, body, out, say: `Width ${width} is not more than the ${body.length} characters we already have, so nothing is added. Width is a minimum, it never cuts.` });
      fr.push({ parts, body, out, done: true, say: `The final text is <code>${esc(JSON.stringify(out))}</code> (${out.length} characters). In Python: <code>f"{${esc(String(p.v))}:${esc(p.spec)}}"</code> or <code>format(${esc(String(p.v))}, "${esc(p.spec)}")</code>.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      head(z, 'Spec', 16, 20);
      const spec = String(z.p.spec);
      box(z, 16, 28, 568, 40, `f"{value:${spec}}"`, { mono: true, b: true, s: 16, stroke: c.cv });
      if (f.body !== undefined) {
        head(z, 'Formatted value', 16, 98);
        box(z, 16, 106, 568, 40, PYZ.showWS(f.body), { mono: true, s: 16, fill: c.bg, stroke: c.line });
      }
      if (f.out !== undefined) {
        head(z, 'After width, fill and align (· is a space)', 16, 176);
        const w = Math.min(36, 560 / Math.max(1, f.out.length));
        [...f.out].forEach((ch, i) => box(z, 16 + i * w, 186, w - 2, 36, ch === ' ' ? '·' : ch, { mono: true, b: true, s: Math.min(15, w * 0.6), fill: f.body.includes(ch) ? c.surf : c.bg, stroke: c.line, w: 1 }));
        D.text(g, `${f.out.length} characters`, 16, 246, { s: 12, c: c.ink2 });
      }
    }
  });
})();

/* =====================================================================================================
   Core 2.1  if, elif, else: which branch runs
   ===================================================================================================== */
(() => {
  const { trace, box, head, D, tag, esc, consoleBox, codeView } = PYZ;
  trace('pyif', {
    title: 'if, elif and else: Python checks the conditions from the top',
    sub: 'Type a score and pick how the program is written. Watch which conditions are checked and which are skipped.',
    W: 600, H: 320,
    params: [
      { k: 'score', label: 'score', type: 'range', v: 82, min: 0, max: 100 },
      { k: 'style', label: 'How the program is written', type: 'select', v: 'elif', opts: [['elif', 'if / elif / elif / else (correct)'], ['ifs', 'four separate if statements (a common bug)'], ['order', 'elif chain in the wrong order'], ['nested', 'nested if inside if']] }
    ],
    tips: [
      { t: 'Score 95 with the elif chain: only "A" is printed. Once a branch runs, the rest of the chain is skipped.', set: { score: 95, style: 'elif' }, play: true },
      { t: 'Score 95 with separate ifs: A, B and C are all printed, because every if is checked on its own.', set: { score: 95, style: 'ifs' }, play: true },
      { t: 'Wrong order: score >= 50 is checked first, so 95 gets a C. Put the strictest test first.', set: { score: 95, style: 'order' }, play: true }
    ],
    frames(p) {
      const s = p.score, fr = [];
      const P = {
        elif: [['if score >= 90:', s >= 90, 'A'], ['elif score >= 75:', s >= 75, 'B'], ['elif score >= 50:', s >= 50, 'C'], ['else:', true, 'F']],
        order: [['if score >= 50:', s >= 50, 'C'], ['elif score >= 75:', s >= 75, 'B'], ['elif score >= 90:', s >= 90, 'A'], ['else:', true, 'F']],
        ifs: [['if score >= 90:', s >= 90, 'A'], ['if score >= 75:', s >= 75, 'B'], ['if score >= 50:', s >= 50, 'C'], ['if score < 50:', s < 50, 'F']]
      };
      if (p.style === 'nested') {
        const lines = ['if score >= 50:', '    if score >= 75:', '        print("B or better")', '    else:', '        print("C")', 'else:', '    print("F")'];
        let out = '';
        fr.push({ lines, cur: 0, out, say: `score is ${s}. The outer if checks score >= 50: <b>${s >= 50}</b>.` });
        if (s >= 50) {
          fr.push({ lines, cur: 1, out, say: `Inside the outer block, the inner if checks score >= 75: <b>${s >= 75}</b>. The inner if is only reached because the outer one was True.` });
          if (s >= 75) { out = 'B or better'; fr.push({ lines, cur: 2, out, say: 'The inner condition is True, so its block prints "B or better". The inner else is skipped.' }); }
          else { out = 'C'; fr.push({ lines, cur: 4, out, say: 'The inner condition is False, so the inner else runs and prints "C".' }); }
          fr.push({ lines, cur: -1, out, say: 'The outer else is skipped because the outer if was True. Nesting reads like a decision tree, but deep nesting gets hard to read. An elif chain is usually flatter and clearer.' });
        } else {
          out = 'F'; fr.push({ lines, cur: 6, out, say: 'The outer condition is False, so Python jumps straight to the outer else and prints "F". The inner if is never looked at.' });
        }
        return fr;
      }
      const rows = P[p.style];
      const lines = [];
      rows.forEach(r => { lines.push(r[0]); lines.push(`    print("${r[2]}")`); });
      let out = '', done = false;
      fr.push({ lines, cur: -1, out, say: `score is ${s}. Python starts at the top of the ${p.style === 'ifs' ? 'four separate if statements' : 'chain'}.` });
      rows.forEach((r, i) => {
        if (done && p.style !== 'ifs') { fr.push({ lines, cur: i * 2, out, skip: true, say: `<code>${r[0]}</code> is <b>skipped</b> without being checked: a branch of this chain already ran.` }); return; }
        if (r[0] === 'else:') { out += (out ? '\n' : '') + r[2]; done = true; fr.push({ lines, cur: i * 2 + 1, out, say: 'No condition above was True, so the else block runs and prints "F". else has no condition of its own.' }); return; }
        fr.push({ lines, cur: i * 2, out, say: `Check <code>${r[0].replace(':', '')}</code>: ${s} ${r[0].match(/[<>]=?/)[0]} ${r[0].match(/\d+/)[0]} is <b>${r[1] ? 'True' : 'False'}</b>.${r[1] ? '' : ' Its block is skipped.'}` });
        if (r[1]) { out += (out ? '\n' : '') + r[2]; done = true; fr.push({ lines, cur: i * 2 + 1, out, say: `True, so its block runs and prints "${r[2]}".${p.style === 'ifs' ? ' These are separate if statements, so Python carries on checking the next one too.' : ' The rest of the chain will now be skipped.'}` }); }
      });
      const n = out.split('\n').filter(Boolean).length;
      fr.push({ lines, cur: -1, out, say: p.style === 'ifs' && n > 1 ? `Done. ${n} grades were printed for one score. Separate ifs are right when several things can be true together, but a grade needs exactly one branch: use elif.` : p.style === 'order' && s >= 75 ? 'Done. The answer is wrong because the weakest test (>= 50) came first and caught the score. In an elif chain, put the strictest test first.' : 'Done. Exactly one branch of the chain ran.' });
      return fr;
    },
    paint(z, f) {
      head(z, 'Program', 16, 18);
      codeView(z, f.lines, f.cur, 16, 26, 340, { s: 12.5, lh: 19 });
      PYZ.box(z, 390, 26, 190, 40, 'score = ' + z.p.score, { mono: true, b: true, stroke: z.col.cv });
      consoleBox(z, f.out, 390, 90, 190, 150);
    }
  });

  /* =====================================================================================================
     Core 2.1  match and case: structural pattern matching on a command
     ===================================================================================================== */
  trace('pymatch', {
    title: 'match and case: Python tries each pattern from the top',
    sub: 'Type a command for a small text game. The command is split into words, then each case pattern is tried until one fits.',
    W: 600, H: 320,
    params: [
      { k: 'cmd', label: 'Command', type: 'text', v: 'go north' }
    ],
    tips: [
      { t: '"go north" fits case ["go", direction], and the name direction captures "north".', set: { cmd: 'go north' }, play: true },
      { t: '"drop sword shield lamp" fits case ["drop", *things]. The star collects every remaining word into a list.', set: { cmd: 'drop sword shield lamp' }, play: true },
      { t: '"go up" fits the guard: case ["go", direction] if direction in ("up", "down") comes first and catches it.', set: { cmd: 'go up' }, play: true },
      { t: '"dance" fits nothing, so case _ (the wildcard) catches it, like else.', set: { cmd: 'dance' }, play: true }
    ],
    frames(p) {
      const words = String(p.cmd).trim().split(/\s+/).filter(Boolean);
      const cases = [
        { pat: 'case ["quit"] | ["exit"]:', test: w => w.length === 1 && (w[0] === 'quit' || w[0] === 'exit'), out: () => 'Goodbye!', bind: () => '' },
        { pat: 'case ["go", direction] if direction in ("up", "down"):', test: w => w.length === 2 && w[0] === 'go' && ['up', 'down'].includes(w[1]), out: w => `You climb ${w[1]}.`, bind: w => `direction = "${w[1]}"` },
        { pat: 'case ["go", direction]:', test: w => w.length === 2 && w[0] === 'go', out: w => `You walk ${w[1]}.`, bind: w => `direction = "${w[1]}"` },
        { pat: 'case ["drop", *things]:', test: w => w.length >= 1 && w[0] === 'drop', out: w => `You drop ${w.length - 1} thing(s).`, bind: w => `things = [${w.slice(1).map(x => '"' + x + '"').join(', ')}]` },
        { pat: 'case _:', test: () => true, out: w => `I do not understand "${w.join(' ')}".`, bind: () => '' }
      ];
      const lines = ['match command.split():'].concat(cases.flatMap(c => ['    ' + c.pat, '        print(...)']));
      const fr = [];
      fr.push({ lines, cur: 0, words, say: `command.split() turns the text into a list of words: <code>[${words.map(w => '"' + esc(w) + '"').join(', ')}]</code>. match will compare this list with each case, from the top.` });
      for (let i = 0; i < cases.length; i++) {
        const c = cases[i], ok = c.test(words);
        let why = '';
        if (i === 0) why = ok ? 'The list has exactly one word and it is "quit" or "exit". The | means "or".' : 'This needs exactly one word, "quit" or "exit".';
        if (i === 1) why = words.length === 2 && words[0] === 'go' ? (ok ? `The shape fits (two words, the first is "go"), and the guard <code>if direction in ("up", "down")</code> is True.` : `The shape fits, but the guard is False for "${esc(words[1])}", so this case is rejected and matching goes on.`) : 'This needs exactly two words, the first one "go".';
        if (i === 2) why = ok ? 'Two words and the first is "go". A plain name in a pattern captures the value.' : 'This needs exactly two words starting with "go".';
        if (i === 3) why = ok ? 'The first word is "drop". *things collects the rest, even zero words.' : 'This needs "drop" as the first word.';
        if (i === 4) why = 'The wildcard _ matches anything and binds nothing. It is the last resort.';
        fr.push({ lines, cur: 1 + i * 2, words, tried: i, say: `Try <code>${esc(c.pat)}</code>: ${ok ? '<b>it fits</b>.' : '<b>no</b>.'} ${why}` });
        if (ok) {
          const b = c.bind(words);
          fr.push({ lines, cur: 2 + i * 2, words, tried: i, bind: b, out: c.out(words), say: `${b ? `The capture sets <code>${esc(b)}</code>. ` : ''}The block runs and prints <code>${esc(c.out(words))}</code> Only the first case that fits runs, so matching stops here.` });
          break;
        }
      }
      return fr;
    },
    paint(z, f) {
      head(z, 'Program', 16, 18);
      codeView(z, f.lines, f.cur, 16, 26, 410, { s: 11.5, lh: 21 });
      head(z, 'Words', 440, 18);
      f.words.slice(0, 6).forEach((w, i) => PYZ.box(z, 440, 26 + i * 30, 140, 26, `[${i}] "${w}"`, { mono: true, s: 12 }));
      if (f.bind) { head(z, 'Captured', 440, 222); PYZ.box(z, 440, 230, 140, 30, f.bind, { mono: true, s: 11, stroke: z.col.green }); }
      if (f.out) consoleBox(z, f.out, 440, 268, 140, 46, { title: 'Output' });
    }
  });

  /* =====================================================================================================
     Core 2.2  loops: for over range(), while, break, continue and else
     ===================================================================================================== */
  trace('pyloop', {
    title: 'A loop, one turn at a time',
    sub: 'Pick a range, and optional break and continue rules. Each step is one check or one turn of the loop.',
    W: 600, H: 320,
    params: [
      { k: 'kind', label: 'Loop', type: 'select', v: 'for', opts: [['for', 'for i in range(start, stop, step)'], ['while', 'i = start, then while i < stop (i += step)']] },
      { k: 'start', label: 'start', type: 'range', v: 1, min: -5, max: 10 },
      { k: 'stop', label: 'stop', type: 'range', v: 10, min: -5, max: 20 },
      { k: 'step', label: 'step', type: 'range', v: 2, min: -3, max: 4, help: 'step 0 is not allowed. A negative step counts down.' },
      { k: 'cont', label: 'continue when i % 3 == 0', type: 'check', v: false },
      { k: 'brk', label: 'break when i > 6', type: 'check', v: false },
      { k: 'els', label: 'add an else block after the loop', type: 'check', v: true }
    ],
    tips: [
      { t: 'range(1, 10, 2) gives 1, 3, 5, 7, 9. The stop value 10 is never reached: stop is excluded.', set: { kind: 'for', start: 1, stop: 10, step: 2, cont: false, brk: false }, play: true },
      { t: 'Tick break. The loop leaves early at 7, and the else block does NOT run. else only runs when the loop ends normally.', set: { brk: true, cont: false, els: true }, play: true },
      { t: 'Tick continue with step 1. Multiples of 3 skip the rest of their turn, but the loop goes on.', set: { start: 1, stop: 10, step: 1, cont: true, brk: false }, play: true },
      { t: 'Count down: start 10, stop 0, step -3 gives 10, 7, 4, 1.', set: { start: 10, stop: 0, step: -3, cont: false, brk: false }, play: true }
    ],
    frames(p) {
      const { start, stop, step } = p, fr = [];
      if (step === 0) throw new Error('ValueError: range() arg 3 must not be zero');
      const W = p.kind === 'while';
      const lines = W ? [`i = ${start}`, `while i ${step > 0 ? '<' : '>'} ${stop}:`] : [`for i in range(${start}, ${stop}, ${step}):`];
      const bodyAt = lines.length;
      if (p.cont) lines.push('    if i % 3 == 0:', '        ' + (W ? 'i += ' + step + '; continue' : 'continue'));
      if (p.brk) lines.push('    if i > 6:', '        break');
      lines.push('    print(i)');
      if (W) lines.push(`    i += ${step}`);
      if (p.els) lines.push('else:', '    print("loop finished")');
      lines.push('print("after the loop")');
      const L = s => lines.findIndex(x => x.trim().startsWith(s));
      const seq = [];
      for (let i = start; step > 0 ? i < stop : i > stop; i += step) seq.push(i);
      let out = [];
      const head0 = W ? 1 : 0;
      fr.push({ lines, cur: 0, seq, out: '', say: W ? `i starts at ${start}. A while loop repeats while its condition is True, and you must change i yourself, or it never stops.` : `range(${start}, ${stop}, ${step}) gives the numbers ${seq.length ? seq.join(', ') : '(none at all)'}. It starts at ${start}, adds ${step} each time, and stops <b>before</b> reaching ${stop}.` });
      let broke = false, turns = 0;
      for (const i of seq) {
        turns++;
        if (turns > 40) break;
        fr.push({ lines, cur: head0, seq, i, out: out.join('\n'), say: W ? `Check i ${step > 0 ? '<' : '>'} ${stop}: ${i} ${step > 0 ? '<' : '>'} ${stop} is <b>True</b>, so the body runs with i = ${i}.` : `Next number: i = <b>${i}</b>. The body runs.` });
        if (p.cont && i % 3 === 0) { fr.push({ lines, cur: L('if i % 3'), seq, i, out: out.join('\n'), say: `${i} % 3 == 0 is True, so <b>continue</b> skips the rest of this turn and goes straight to the next one. Nothing is printed for ${i}.` }); continue; }
        if (p.brk && i > 6) { broke = true; fr.push({ lines, cur: L('break'), seq, i, out: out.join('\n'), say: `${i} > 6 is True, so <b>break</b> leaves the loop at once. No more turns${p.els ? ', and the else block is skipped' : ''}.` }); break; }
        out.push(String(i));
        fr.push({ lines, cur: L('print(i)'), seq, i, out: out.join('\n'), say: `print(i) shows ${i}.` });
      }
      if (!broke) {
        const last = seq.length ? seq[seq.length - 1] + step : start;
        fr.push({ lines, cur: head0, seq, out: out.join('\n'), say: W ? `Check i ${step > 0 ? '<' : '>'} ${stop}: ${last} ${step > 0 ? '<' : '>'} ${stop} is <b>False</b>, so the loop ends.` : 'range has no more numbers, so the loop ends normally.' });
        if (p.els) { out.push('loop finished'); fr.push({ lines, cur: L('print("loop finished")'), seq, out: out.join('\n'), say: 'The loop ended normally (no break), so its <b>else</b> block runs. Think of it as "if no break".' }); }
      }
      out.push('after the loop');
      fr.push({ lines, cur: L('print("after the loop")'), seq, out: out.join('\n'), say: `Python carries on after the loop. The body ran ${out.filter(x => /^-?\d+$/.test(x)).length} time${out.filter(x => /^-?\d+$/.test(x)).length === 1 ? '' : 's'} with print.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col;
      head(z, 'Program', 16, 18);
      codeView(z, f.lines, f.cur, 16, 26, 330, { s: 12, lh: 19 });
      head(z, 'Values of i', 370, 18);
      const n = Math.min(f.seq.length, 12), w = Math.min(40, 214 / Math.max(1, n));
      f.seq.slice(0, 12).forEach((v, k) => box(z, 370 + k * w, 26, w - 3, 26, String(v), { mono: true, s: Math.min(12, w * 0.45), fill: v === f.i ? c.cv : c.surf, stroke: v === f.i ? c.cv : c.line, c: v === f.i ? '#fff' : c.ink }));
      if (f.seq.length > 12) D.text(z.g, `+${f.seq.length - 12} more`, 370, 68, { s: 11, c: c.ink2 });
      consoleBox(z, f.out, 370, 80, 214, 230);
    }
  });
})();

/* =====================================================================================================
   Core 3.1  string indexing and slicing, and UTF-8 bytes
   ===================================================================================================== */
(() => {
  const { trace, box, head, D, esc } = PYZ;
  const optInt = s => { s = String(s).trim(); if (s === '') return null; if (!/^-?\d+$/.test(s)) throw new Error('start, stop and step must be whole numbers or empty.'); return parseInt(s, 10); };
  /* the same rules as CPython's PySlice_AdjustIndices */
  function sliceIdx(n, a, b, c) {
    const step = c === null ? 1 : c;
    if (step === 0) throw new Error('ValueError: slice step cannot be zero');
    const lower = step < 0 ? -1 : 0, upper = step < 0 ? n - 1 : n;
    const fix = (v, dflt) => { if (v === null) return dflt; if (v < 0) { v += n; if (v < lower) v = lower; } else if (v > upper) v = upper; return v; };
    const start = fix(a, step < 0 ? upper : lower), stop = fix(b, step < 0 ? lower : upper);
    const idx = [];
    for (let i = start; step > 0 ? i < stop : i > stop; i += step) idx.push(i);
    return { start, stop, step, idx };
  }
  PYZ.sliceIdx = sliceIdx;
  trace('pystr', {
    title: 'Indexing and slicing a string',
    sub: 'Every character has two numbers: a position from the left (0, 1, 2 ...) and one from the right (-1, -2 ...). A slice [start:stop:step] walks between them.',
    W: 600, H: 280,
    params: [
      { k: 's', label: 'Text', type: 'text', v: 'PYTHON ROCKS' },
      { k: 'a', label: 'start (empty for the default)', type: 'text', v: '1' },
      { k: 'b', label: 'stop (empty for the default)', type: 'text', v: '8' },
      { k: 'c', label: 'step (empty means 1)', type: 'text', v: '2' }
    ],
    tips: [
      { t: '[::-1] reverses the text: start at the end, step backwards to the front.', set: { a: '', b: '', c: '-1' }, play: true },
      { t: '[-5:] takes the last five characters. Negative numbers count from the right.', set: { a: '-5', b: '', c: '' }, play: true },
      { t: '[3:100] does not fail: a slice quietly stops at the end. Only a single index like s[100] raises IndexError.', set: { a: '3', b: '100', c: '' }, play: true },
      { t: '[8:2] is empty: with a positive step you cannot walk from 8 left to 2.', set: { a: '8', b: '2', c: '' }, play: true }
    ],
    frames(p) {
      const s = [...String(p.s)].slice(0, 20), n = s.length, fr = [];
      if (!n) throw new Error('Type some text first.');
      const a = optInt(p.a), b = optInt(p.b), c = optInt(p.c);
      const r = sliceIdx(n, a, b, c);
      const txt = `[${p.a}:${p.b}${String(p.c).trim() === '' ? '' : ':' + p.c}]`;
      fr.push({ s, say: `The text has ${n} characters. Positions go from 0 to ${n - 1} on the left, and from -1 to -${n} on the right. s[0] is "${esc(s[0])}" and s[-1] is "${esc(s[n - 1])}".` });
      fr.push({ s, r, ph: 'norm', say: `Python first turns <code>${esc(txt)}</code> into real positions. ${a === null ? `No start, so it starts at ${r.step > 0 ? '0 (the beginning)' : 'the last character'}` : a < 0 ? `start ${a} counts from the right: ${a} + ${n} = ${a + n}${r.start !== a + n ? `, then it is moved into range: ${r.start}` : ''}` : `start is ${a}${r.start !== a ? `, which is past the end, so it becomes ${r.start}` : ''}`}. ${b === null ? `No stop, so it goes ${r.step > 0 ? 'to the end' : 'to the very first character'}` : b < 0 ? `stop ${b} becomes ${b} + ${n} = ${b + n}${r.stop !== b + n ? ` (moved to ${r.stop})` : ''}` : `stop is ${b}${r.stop !== b ? `, moved to ${r.stop}` : ''}`}. The step is ${r.step}. The stop position itself is never taken.` });
      const got = [];
      r.idx.forEach((i, k) => { got.push(s[i]); fr.push({ s, r, ph: 'walk', cur: i, got: got.slice(), say: `Take position ${i} (also ${i - n}): "${esc(s[i])}". ${k + 1 < r.idx.length ? `Next position: ${i} + ${r.step} = ${i + r.step}.` : `Next would be ${i + r.step}, which ${r.step > 0 ? 'is not before' : 'is not after'} the stop ${r.stop}, so we stop.`}` }); });
      fr.push({ s, r, ph: 'done', got, say: r.idx.length ? `The slice is <b>"${esc(got.join(''))}"</b>, a new string of ${got.length} character${got.length === 1 ? '' : 's'}. The original text is not changed: strings are immutable.` : `No position fits between start ${r.start} and stop ${r.stop} with step ${r.step}, so the slice is the empty string "". A slice never raises IndexError.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, n = f.s.length, w = Math.min(44, 560 / n), x0 = (600 - n * w) / 2;
      D.text(z.g, 'from the left', x0 - 6, 34, { a: 'right', s: 10, c: c.ink2 });
      D.text(z.g, 'from the right', x0 - 6, 120, { a: 'right', s: 10, c: c.ink2 });
      f.s.forEach((ch, i) => {
        const x = x0 + i * w, inSl = f.r && f.r.idx.includes(i), taken = f.got && f.r.idx.indexOf(i) < f.got.length && inSl;
        D.text(z.g, String(i), x + w / 2, 34, { a: 'center', s: 12, mono: true, b: true, c: c.cv });
        box(z, x + 1, 44, w - 2, 50, ch === ' ' ? '·' : ch, { mono: true, b: true, s: Math.min(20, w * 0.5), fill: f.cur === i ? c.cv : taken ? (c.dark ? '#1e3a5f' : '#dbeafe') : c.surf, stroke: inSl ? c.cv : c.line, c: f.cur === i ? '#fff' : c.ink });
        D.text(z.g, String(i - n), x + w / 2, 120, { a: 'center', s: 12, mono: true, b: true, c: c.orange });
      });
      if (f.r) {
        const pos = v => x0 + Math.max(-0.5, Math.min(n + 0.5, v)) * w + w / 2;
        if (f.r.step > 0 || true) {
          D.line(z.g, pos(f.r.start) - w / 2 + 2, 140, pos(f.r.start) - w / 2 + 2, 160, c.green, 3);
          D.text(z.g, 'start ' + f.r.start, pos(f.r.start) - w / 2 + 6, 158, { s: 11, b: true, c: c.green });
          D.line(z.g, pos(f.r.stop) - w / 2 + 2, 166, pos(f.r.stop) - w / 2 + 2, 186, c.red, 3);
          D.text(z.g, 'stop ' + f.r.stop + ' (not taken)', pos(f.r.stop) - w / 2 + 6, 184, { s: 11, b: true, c: c.red });
        }
      }
      if (f.got) {
        head(z, 'Result so far', 20, 214);
        box(z, 20, 222, 560, 40, '"' + f.got.join('') + '"', { mono: true, b: true, s: 16, stroke: c.green, fill: c.bg });
      }
    }
  });

  trace('pyutf8', {
    title: 'From characters to bytes: Unicode code points and UTF-8',
    sub: 'Each character has a Unicode number (code point). UTF-8 stores small numbers in 1 byte and bigger ones in 2, 3 or 4 bytes.',
    W: 600, H: 300,
    params: [{ k: 's', label: 'Text (try letters from any language)', type: 'text', v: 'Aé₹नम' }],
    tips: [
      { t: 'English letters and digits are 1 byte each, the same as old ASCII. That is why UTF-8 became the web standard.', set: { s: 'Hi 5' }, play: true },
      { t: 'The rupee sign ₹ is U+20B9, so it needs 3 bytes. len("₹") is 1 but len("₹".encode()) is 3.', set: { s: '₹' }, play: true },
      { t: 'Hindi letters such as न are 3 bytes each in UTF-8.', set: { s: 'नमस्ते' }, play: true }
    ],
    frames(p) {
      const chars = [...String(p.s)].slice(0, 8), fr = [];
      if (!chars.length) throw new Error('Type some text first.');
      const rows = [];
      fr.push({ rows: [], say: `The text has ${chars.length} characters, so len() is ${chars.length}. Python stores text as Unicode characters. To save it in a file or send it over the internet it must become <b>bytes</b>, and UTF-8 is the usual way.` });
      let total = 0;
      chars.forEach(ch => {
        const cp = ch.codePointAt(0);
        const bytes = [...new TextEncoder().encode(ch)];
        total += bytes.length;
        const tmpl = bytes.length === 1 ? '0xxxxxxx' : bytes.length === 2 ? '110xxxxx 10xxxxxx' : bytes.length === 3 ? '1110xxxx 10xxxxxx 10xxxxxx' : '11110xxx 10xxxxxx 10xxxxxx 10xxxxxx';
        rows.push({ ch, cp, bytes, tmpl });
        fr.push({ rows: rows.slice(), say: `"${esc(ch)}" has code point <b>U+${cp.toString(16).toUpperCase().padStart(4, '0')}</b> (ord gives ${cp}). ${cp < 0x80 ? 'Below 128, so 1 byte, the same as ASCII.' : cp < 0x800 ? 'Below 2,048, so 2 bytes.' : cp < 0x10000 ? 'Below 65,536, so 3 bytes.' : 'Above 65,535, so 4 bytes (emoji and rare scripts live here).'} The pattern is <code>${tmpl}</code> and the bits of ${cp} fill the x places: ${bytes.map(b => b.toString(16).toUpperCase().padStart(2, '0')).join(' ')}.` });
      });
      fr.push({ rows, total, say: `In total <code>len(text.encode("utf-8"))</code> is <b>${total}</b> bytes for ${chars.length} characters. Decoding the bytes with .decode("utf-8") gives the same text back. Reading bytes with the wrong encoding gives strange characters or UnicodeDecodeError.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      ['char', 'code point', 'UTF-8 bytes (hex)', 'bits'].forEach((h, i) => head(z, h, [16, 70, 190, 330][i], 18));
      f.rows.forEach((r, i) => {
        const y = 28 + i * 32;
        box(z, 16, y, 40, 26, r.ch, { b: true, s: 15 });
        D.text(g, 'U+' + r.cp.toString(16).toUpperCase().padStart(4, '0'), 70, y + 18, { s: 13, mono: true, b: true, c: c.cv });
        r.bytes.forEach((b, k) => box(z, 190 + k * 34, y, 30, 26, b.toString(16).toUpperCase().padStart(2, '0'), { mono: true, s: 12, stroke: [c.cv, c.orange, c.green, c.purple][k] }));
        const bits = r.bytes.map(b => b.toString(2).padStart(8, '0')).join(' ');
        D.text(g, bits, 330, y + 18, { s: PYZ.fit(g, bits, 260, 11.5, { mono: true }), mono: true, c: c.ink });
      });
      if (f.total) D.text(g, `${f.rows.length} characters, ${f.total} bytes`, 16, 290, { s: 13, b: true, c: c.ink });
    }
  });
})();

/* =====================================================================================================
   Core 3.2  lists: names, aliasing and copies, and how CPython grows a list
   ===================================================================================================== */
(() => {
  const { trace, box, head, D, esc } = PYZ;
  const lit = s => { const v = PYZ.literal(s); if (!v) throw new Error(`"${s}" is not a value. Use numbers or text in quotes.`); return PYZ.repr(v); };
  const items = s => { s = s.trim(); if (!/^\[.*\]$/.test(s)) throw new Error(`Expected a list like [1, 2, 3], got ${s}`); const inner = s.slice(1, -1).trim(); return inner ? PYZ.splitArgs(inner).map(lit) : []; };
  trace('pylist', {
    title: 'Lists are shared, not copied: names, aliases and copies',
    sub: 'Write a few list commands, one per line. Each step shows which name points to which list object, and how the lists change.',
    W: 600, H: 330,
    params: [{ k: 'code', label: 'Commands', type: 'area', v: 'a = [1, 2, 3]\nb = a\nc = a[:]\na.append(4)\nb[0] = 99\nc.insert(0, "x")\na = a + [5]' }],
    tips: [
      { t: 'b = a does not copy. b[0] = 99 changes the one list both names share, so a sees it too. c = a[:] made a real copy, so c is safe.', play: true },
      { t: 'a += [5] changes the list in place (b sees it), but a = a + [5] builds a new list and moves only a.', set: { code: 'a = [1, 2]\nb = a\na += [5]\na = a + [6]' }, play: true },
      { t: 'pop, remove and del also change the shared list. remove deletes the first match only.', set: { code: 'a = [3, 1, 3, 2]\nb = a\na.remove(3)\nb.pop()\ndel a[0]\na.sort()' }, play: true }
    ],
    frames(p) {
      const lines = String(p.code).split('\n').map(s => s.trim()).filter(Boolean).slice(0, 9);
      const objs = [], env = {}, fr = [];
      let id = 0;
      const mk = arr => { objs.push({ id: ++id, v: arr }); return id; };
      const get = n => { if (!(n in env)) throw new Error(`NameError: name '${n}' is not defined`); return objs.find(o => o.id === env[n]); };
      const snap = (i, say, hl) => fr.push({ lines, cur: i, env: { ...env }, objs: objs.map(o => ({ id: o.id, v: o.v.slice() })), hl, say });
      lines.forEach((ln, i) => {
        let m;
        const L = `<code>${esc(ln)}</code>: `;
        if ((m = ln.match(/^(\w+)\s*=\s*(\[.*\])$/))) { const nid = mk(items(m[2])); env[m[1]] = nid; snap(i, L + `Python builds a <b>new list</b> object #${nid} and points the name ${m[1]} at it.`, nid); }
        else if ((m = ln.match(/^(\w+)\s*=\s*(\w+)(\[:\]|\.copy\(\)|)$/)) && !m[3]) { const o = get(m[2]); env[m[1]] = o.id; snap(i, L + `No copy is made. ${m[1]} becomes a second name for list #${o.id}. Now ${m[1]} is ${m[2]} is True. Changing the list through either name changes it for both.`, o.id); }
        else if ((m = ln.match(/^(\w+)\s*=\s*(?:(\w+)\[:\]|(\w+)\.copy\(\)|list\((\w+)\))$/))) { const src = m[2] || m[3] || m[4], o = get(src); const nid = mk(o.v.slice()); env[m[1]] = nid; snap(i, L + `This makes a <b>new list</b> #${nid} with the same items (a shallow copy). From now on ${m[1]} and ${src} are independent.`, nid); }
        else if ((m = ln.match(/^(\w+)\.append\((.+)\)$/))) { const o = get(m[1]); o.v.push(lit(m[2])); snap(i, L + `append adds ${esc(lit(m[2]))} at the end of list #${o.id}, <b>in place</b>. Every name pointing to #${o.id} sees it.`, o.id); }
        else if ((m = ln.match(/^(\w+)\.insert\((-?\d+),\s*(.+)\)$/))) { const o = get(m[1]); let k = +m[2]; if (k < 0) k = Math.max(0, o.v.length + k); k = Math.min(k, o.v.length); o.v.splice(k, 0, lit(m[3])); snap(i, L + `insert puts ${esc(lit(m[3]))} before position ${m[2]}. Items after it move one place right, which costs time on long lists.`, o.id); }
        else if ((m = ln.match(/^(\w+)\.extend\((\[.*\])\)$/)) || (m = ln.match(/^(\w+)\s*\+=\s*(\[.*\])$/))) { const o = get(m[1]); o.v.push(...items(m[2])); snap(i, L + `${ln.includes('+=') ? '+= on a list is the same as extend: it' : 'extend'} adds every item to the <b>same</b> list #${o.id}, in place.`, o.id); }
        else if ((m = ln.match(/^(\w+)\s*=\s*(\w+)\s*\+\s*(\[.*\])$/))) { const o = get(m[2]); const nid = mk(o.v.concat(items(m[3]))); env[m[1]] = nid; snap(i, L + `+ builds a <b>brand new</b> list #${nid}. Only the name ${m[1]} moves to it. Other names still see the old list #${o.id}.`, nid); }
        else if ((m = ln.match(/^(\w+)\[(-?\d+)\]\s*=\s*(.+)$/))) { const o = get(m[1]); let k = +m[2]; if (k < 0) k += o.v.length; if (k < 0 || k >= o.v.length) throw new Error('IndexError: list assignment index out of range'); o.v[k] = lit(m[3]); snap(i, L + `The item at position ${m[2]} of list #${o.id} is replaced by ${esc(lit(m[3]))}. Lists are mutable, so the object itself changes.`, o.id); }
        else if ((m = ln.match(/^(\w+)\.pop\((-?\d*)\)$/))) { const o = get(m[1]); if (!o.v.length) throw new Error('IndexError: pop from empty list'); let k = m[2] === '' ? o.v.length - 1 : +m[2]; if (k < 0) k += o.v.length; const x = o.v.splice(k, 1)[0]; snap(i, L + `pop removes and returns ${esc(x)} from position ${k}. pop() with no number takes the last item, which is fast. pop(0) has to move every other item.`, o.id); }
        else if ((m = ln.match(/^(\w+)\.remove\((.+)\)$/))) { const o = get(m[1]); const x = lit(m[2]), k = o.v.indexOf(x); if (k < 0) throw new Error(`ValueError: list.remove(x): x not in list`); o.v.splice(k, 1); snap(i, L + `remove finds the <b>first</b> ${esc(x)} (at position ${k}) and deletes it.`, o.id); }
        else if ((m = ln.match(/^del\s+(\w+)\[(-?\d+)\]$/))) { const o = get(m[1]); let k = +m[2]; if (k < 0) k += o.v.length; if (k < 0 || k >= o.v.length) throw new Error('IndexError: list assignment index out of range'); const x = o.v.splice(k, 1)[0]; snap(i, L + `del removes ${esc(x)} at position ${m[2]}. Unlike pop it gives nothing back.`, o.id); }
        else if ((m = ln.match(/^(\w+)\.(sort|reverse|clear)\(\)$/))) { const o = get(m[1]); if (m[2] === 'sort') { const num = o.v.every(x => /^-?[\d.]+$/.test(x)), str = o.v.every(x => /^['"]/.test(x)); if (!num && !str) throw new Error("TypeError: '<' not supported between instances of 'str' and 'int'"); o.v.sort((x, y) => num ? parseFloat(x) - parseFloat(y) : (x < y ? -1 : x > y ? 1 : 0)); } else if (m[2] === 'reverse') o.v.reverse(); else o.v.length = 0; snap(i, L + `${m[2]}() changes list #${o.id} in place and returns None. ${m[2] === 'sort' ? 'sorted(a) would instead make a new sorted list and leave a alone.' : ''}`, o.id); }
        else throw new Error(`Line ${i + 1} is not one of the commands this animation knows: x = [..], x = y, x = y[:], x.append(v), x.insert(i, v), x.extend([..]), x += [..], x = y + [..], x[i] = v, x.pop(), x.remove(v), del x[i], x.sort(), x.reverse(), x.clear().`);
      });
      const shared = Object.entries(env).filter(([n, o]) => Object.values(env).filter(x => x === o).length > 1).map(([n]) => n);
      fr.push({ lines, cur: -1, env: { ...env }, objs: objs.map(o => ({ id: o.id, v: o.v.slice() })), say: `Finished. ${Object.entries(env).map(([n, o]) => `${n} = [${objs.find(x => x.id === o).v.join(', ')}]`).join(', ')}. ${shared.length ? `${shared.join(' and ')} share one list.` : 'No two names share a list now.'}` });
      return fr;
    },
    paint(z, f) {
      const c = z.col;
      head(z, 'Commands', 16, 18);
      PYZ.codeView(z, f.lines, f.cur, 16, 26, 200, { s: 11.5, lh: 19 });
      head(z, 'Names', 236, 18); head(z, 'List objects', 330, 18);
      const live = f.objs.filter(o => Object.values(f.env).includes(o.id) || o.id === f.hl);
      const oy = {};
      live.forEach((o, i) => { oy[o.id] = 28 + i * 56; });
      live.forEach(o => {
        const y = oy[o.id];
        D.text(z.g, '#' + o.id, 330, y + 12, { s: 10, c: c.ink2 });
        const w = Math.min(36, 230 / Math.max(1, o.v.length));
        if (!o.v.length) box(z, 352, y, 40, 34, '[ ]', { mono: true, stroke: o.id === f.hl ? c.cv : c.line });
        o.v.forEach((v, k) => { box(z, 352 + k * w, y, w - 2, 34, v, { mono: true, s: Math.min(13, w * 0.42), stroke: o.id === f.hl ? c.cv : c.line, w: o.id === f.hl ? 2.2 : 1.2 }); D.text(z.g, String(k), 352 + k * w + w / 2, y + 46, { a: 'center', s: 9.5, c: c.ink2 }); });
      });
      Object.entries(f.env).forEach(([n, o], i) => {
        const y = 28 + i * 40;
        box(z, 236, y, 60, 28, n, { mono: true, b: true });
        D.arrow(z.g, 298, y + 14, 348, (oy[o] ?? y) + 17, o === f.hl ? c.cv : c.ink2, 1.6);
      });
    }
  });

  /* ---------- how append grows the hidden array ---------- */
  const grow = n => { if (n === 0) return 0; let a = (n + (n >> 3) + 6) & ~3; if (n - 0 > a - n && false) a = (n + 3) & ~3; return a; };
  trace('pygrow', {
    title: 'Why append is fast: CPython keeps spare room in a list',
    sub: 'A list stores pointers in a hidden array. When it is full, CPython makes a bigger array and copies everything. Watch how rarely that happens.',
    W: 600, H: 320,
    params: [{ k: 'n', label: 'Number of appends', type: 'range', v: 30, min: 5, max: 100 }],
    tips: [
      { t: '30 appends cause only 5 resizes. Most appends just fill a spare slot.', set: { n: 30 }, play: true },
      { t: '100 appends: the total number of items copied stays below about 4 per append, so append is O(1) on average (amortised).', set: { n: 100 }, play: true }
    ],
    frames(p) {
      const fr = [];
      let size = 0, cap = 0, copies = 0, resizes = 0;
      const hist = [];
      fr.push({ size, cap, copies, hist: [], say: 'Start with an empty list: a = []. The hidden array has room for 0 items.' });
      for (let i = 1; i <= p.n; i++) {
        if (i > cap) {
          const nc = grow(i);
          copies += size; resizes++;
          hist.push({ at: i, from: cap, to: nc });
          fr.push({ size: i, cap: nc, copies, hist: hist.slice(), resized: true, say: `Append number ${i}: the array (room for ${cap}) is full. CPython asks for a bigger one: new room = (n + n // 8 + 6) rounded down to a multiple of 4 = <b>${nc}</b>, then copies the ${size} old item${size === 1 ? '' : 's'}. Resizes so far: ${resizes}.` });
          cap = nc;
        } else if (i === p.n || (i <= 6) || i % 10 === 0) {
          fr.push({ size: i, cap, copies, hist: hist.slice(), say: `Append number ${i}: there is a free slot, so the item just goes in. No copying. ${cap - i} spare slot${cap - i === 1 ? '' : 's'} left.` });
        }
        size = i;
      }
      fr.push({ size, cap, copies, hist, done: true, say: `${p.n} appends needed only ${resizes} resizes and ${copies} item copies in total, that is ${(copies / p.n).toFixed(2)} copies per append. Because the room grows by about 12.5% plus a little each time, the average cost of append stays constant: <b>amortised O(1)</b>.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, cols = 25, cw = 22;
      head(z, `len(a) = ${f.size}, room = ${f.cap}`, 16, 18);
      for (let k = 0; k < Math.min(f.cap, 100); k++) {
        const x = 16 + (k % cols) * cw, y = 28 + Math.floor(k / cols) * 28;
        PYZ.rr(z.g, x, y, cw - 3, 22, 4, { fill: k < f.size ? (f.resized && k === f.size - 1 ? c.orange : c.cv) : c.surf, stroke: c.line });
      }
      head(z, 'Resizes: when, and the new room', 16, 160);
      f.hist.slice(-10).forEach((h, i) => D.text(z.g, `append ${h.at}: ${h.from} → ${h.to}`, 16 + (i % 5) * 116, 182 + Math.floor(i / 5) * 20, { s: 12, mono: true, c: c.ink }));
      D.text(z.g, `items copied so far: ${f.copies}`, 16, 240, { s: 13, b: true, c: c.ink });
      const bw = Math.min(560, f.copies * 2);
      PYZ.rr(z.g, 16, 250, Math.max(2, bw), 14, 4, { fill: c.orange });
      PYZ.rr(z.g, 16, 270, Math.max(2, Math.min(560, f.size * 2)), 14, 4, { fill: c.cv });
      D.text(z.g, 'copies (orange) against appends (blue)', 16, 302, { s: 11, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Core 3.3  set operations on a Venn diagram
   ===================================================================================================== */
(() => {
  const { trace, head, D, esc } = PYZ;
  trace('pyset', {
    title: 'Set operations on a picture',
    sub: 'Type two sets. Each element goes into the left part, the middle or the right part. Then the chosen operation lights up its region.',
    W: 600, H: 300,
    params: [
      { k: 'a', label: 'Set A', type: 'text', v: 'python, java, c, go' },
      { k: 'b', label: 'Set B', type: 'text', v: 'go, rust, java, kotlin' },
      { k: 'op', label: 'Operation', type: 'select', v: '&', opts: [['|', 'A | B  union: in A or B'], ['&', 'A & B  intersection: in both'], ['-', 'A - B  difference: in A, not in B'], ['^', 'A ^ B  symmetric difference: in exactly one']] }
    ],
    tips: [
      { t: 'Union of two class lists gives every student once, even those in both classes.', set: { op: '|' }, play: true },
      { t: 'Repeated items vanish: a set keeps only one copy. Type "a, a, b" as set A.', set: { a: 'a, a, b', b: 'b, c', op: '|' }, play: true },
      { t: 'A - B is not the same as B - A. Order matters for difference, but not for | & ^.', set: { op: '-' }, play: true }
    ],
    frames(p) {
      const uniq = s => [...new Set(PYZ.list(p[s]))];
      const A = uniq('a'), B = uniq('b'), fr = [];
      const only = A.filter(x => !B.includes(x)), both = A.filter(x => B.includes(x)), onlyB = B.filter(x => !A.includes(x));
      fr.push({ A, B, shown: [], say: `A = {${A.join(', ')}} has ${A.length} element${A.length === 1 ? '' : 's'}${PYZ.list(p.a).length !== A.length ? ' (duplicates were dropped, a set stores each value once)' : ''}. B = {${B.join(', ')}} has ${B.length}. Sets have no order, so Python may print them in any order.` });
      const shown = [];
      A.concat(onlyB).forEach(x => {
        shown.push(x);
        const where = both.includes(x) ? 'in both A and B, so it goes in the middle' : A.includes(x) ? 'only in A, so it goes on the left' : 'only in B, so it goes on the right';
        fr.push({ A, B, shown: shown.slice(), cur: x, say: `"${esc(x)}" is ${where}. Python checks "is it in B?" with a hash lookup, which takes about the same time however big the set is.` });
      });
      const res = p.op === '|' ? A.concat(onlyB) : p.op === '&' ? both : p.op === '-' ? only : only.concat(onlyB);
      fr.push({ A, B, shown, op: p.op, res, say: `A ${p.op} B = {${res.join(', ')}}: ${res.length} element${res.length === 1 ? '' : 's'}. ${{ '|': 'Union takes all three regions.', '&': 'Intersection takes only the middle.', '-': 'Difference takes only the left part.', '^': 'Symmetric difference takes the two outer parts, not the middle.' }[p.op]} Size check: |A ∪ B| = |A| + |B| − |A ∩ B| = ${A.length} + ${B.length} − ${both.length} = ${A.length + B.length - both.length}.` });
      return fr;
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const L = { x: 220, y: 150, r: 110 }, R = { x: 380, y: 150, r: 110 };
      const region = (inA, inB) => { if (!f.op) return false; return { '|': inA || inB, '&': inA && inB, '-': inA && !inB, '^': inA !== inB }[f.op]; };
      // shade regions by sampling
      if (f.op) {
        g.save(); g.globalAlpha = 0.28; g.fillStyle = c.cv;
        for (let x = 100; x < 500; x += 4) for (let y = 30; y < 270; y += 4) {
          const a = Math.hypot(x - L.x, y - L.y) < L.r, b = Math.hypot(x - R.x, y - R.y) < R.r;
          if ((a || b) && region(a, b)) g.fillRect(x, y, 4, 4);
        }
        g.restore();
      }
      D.circle(g, L.x, L.y, L.r, { stroke: c.cv, w: 2.5 }); D.circle(g, R.x, R.y, R.r, { stroke: c.orange, w: 2.5 });
      D.text(g, 'A', L.x - 90, 40, { s: 18, b: true, c: c.cv }); D.text(g, 'B', R.x + 80, 40, { s: 18, b: true, c: c.orange });
      const spots = { l: [], m: [], r: [] };
      f.shown.forEach(x => { const k = f.A.includes(x) && f.B.includes(x) ? 'm' : f.A.includes(x) ? 'l' : 'r'; spots[k].push(x); });
      const place = (arr, cx) => arr.slice(0, 7).forEach((x, i) => { const y = 75 + i * 26 + (arr.length < 4 ? 40 : 0); D.text(g, x, cx, y, { a: 'center', s: PYZ.fit(g, x, 80, 13), b: x === f.cur, c: x === f.cur ? c.red : c.ink }); });
      place(spots.l, 160); place(spots.m, 300); place(spots.r, 440);
    }
  });
})();

/* =====================================================================================================
   Core 3.4  a dictionary is a hash table: indices plus entries in insertion order
   ===================================================================================================== */
(() => {
  const { trace, box, head, D, esc } = PYZ;
  const toy = k => { if (/^-?\d+$/.test(k)) return Number(k) === -1 ? -2 : Number(k); let h = 0; for (const ch of k) h = (h * 31 + ch.codePointAt(0)) % 1000003; return h; };
  trace('pydict', {
    title: 'How a dict finds a key in one step: hashing',
    sub: 'Type keys to insert. Each key is hashed to a number, the number picks a slot, and a collision tries another slot. Watch the table grow when it is two thirds full.',
    W: 600, H: 330,
    params: [
      { k: 'keys', label: 'Keys to insert, in order', type: 'text', v: 'apple, mango, kiwi, fig, pear, plum, lime' },
      { k: 'look', label: 'Then look up', type: 'text', v: 'fig' }
    ],
    tips: [
      { t: 'The 6th key makes the table resize from 8 to 16 slots: a dict with 8 slots holds at most 5 keys (two thirds).', play: true },
      { t: 'Whole number keys hash to themselves, so 3, 11 and 19 all want slot 3 in a table of 8 and must probe.', set: { keys: '3, 11, 19, 4', look: '19' }, play: true },
      { t: 'Looking up a missing key also takes only a few probes, then hits an empty slot and raises KeyError (or get() returns None).', set: { look: 'banana' }, play: true }
    ],
    frames(p) {
      const keys = [...new Set(PYZ.list(p.keys))].slice(0, 12), fr = [];
      let size = 8, idx = new Array(8).fill(null), entries = [];
      const probe = (h, sz, want) => {
        const path = [];
        let perturb = h, i = h & (sz - 1);
        for (let t = 0; t < 40; t++) {
          path.push(i);
          if (want(i)) return path;
          perturb = Math.floor(perturb / 32);
          i = (5 * i + 1 + perturb) & (sz - 1);
        }
        return path;
      };
      fr.push({ size, idx: idx.slice(), entries: [], say: 'An empty dict starts with a table of 8 slots (the index) and an empty list of entries. Real Python hashes text with a random secret each run (PYTHONHASHSEED), so this picture uses a simpler hash. The steps are the same.' });
      for (const k of keys) {
        if ((entries.length + 1) > Math.floor(size * 2 / 3)) {
          const ns = (() => { let s = 8; while (s < entries.length * 3) s *= 2; return s; })();
          size = ns; idx = new Array(ns).fill(null);
          entries.forEach((e, n) => { const pth = probe(e.h, size, i => idx[i] === null); idx[pth[pth.length - 1]] = n; });
          fr.push({ size, idx: idx.slice(), entries: entries.map(e => ({ ...e })), resized: true, say: `The table would be more than two thirds full, so Python makes a bigger one: ${entries.length} keys × 3 = ${entries.length * 3}, next power of 2 is <b>${ns}</b>. Every key is placed again. The entries keep their order.` });
        }
        const h = toy(k);
        const path = probe(h, size, i => idx[i] === null);
        const slot = path[path.length - 1];
        idx[slot] = entries.length;
        entries.push({ k, h });
        fr.push({ size, idx: idx.slice(), entries: entries.map(e => ({ ...e })), path, key: k, say: `Insert "${esc(k)}": hash = ${h}. Slot = hash % ${size} = ${h % size}${path.length > 1 ? `, but that slot is taken (a <b>collision</b>), so Python probes ${path.slice(1).join(', ')}` : ''}. Slot ${slot} gets entry number ${entries.length - 1}.` });
      }
      if (String(p.look).trim()) {
        const k = String(p.look).trim(), h = toy(k);
        const path = probe(h, size, i => idx[i] === null || entries[idx[i]].k === k);
        const last = path[path.length - 1], hit = idx[last] !== null;
        fr.push({ size, idx: idx.slice(), entries: entries.map(e => ({ ...e })), path, key: k, look: true, hit, say: `Look up "${esc(k)}": hash ${h}, start at slot ${h % size}. ${path.length > 1 ? `Probe ${path.join(', ')}. ` : ''}${hit ? `Slot ${last} points to entry ${idx[last]}, whose key matches. Found in ${path.length} probe${path.length > 1 ? 's' : ''}, no matter how many keys the dict holds: <b>O(1) on average</b>.` : `Slot ${last} is empty, so the key is not in the dict: d["${esc(k)}"] raises KeyError and d.get("${esc(k)}") returns None.`}` });
      }
      return fr;
    },
    paint(z, f) {
      const c = z.col, n = f.size, w = Math.min(34, 560 / n);
      head(z, `Index table: ${n} slots`, 16, 18);
      for (let i = 0; i < n; i++) {
        const onPath = f.path && f.path.includes(i), last = f.path && f.path[f.path.length - 1] === i;
        box(z, 16 + i * w, 28, w - 3, 30, f.idx[i] === null ? '' : String(f.idx[i]), { mono: true, b: true, s: Math.min(13, w * 0.45), fill: last ? (f.look && !f.hit ? c.red : c.cv) : onPath ? (c.dark ? '#3b2a12' : '#fff1cc') : c.surf, stroke: onPath ? c.orange : c.line, c: last ? '#fff' : c.ink });
        D.text(z.g, String(i), 16 + i * w + w / 2 - 1, 72, { a: 'center', s: 9.5, c: c.ink2 });
      }
      head(z, 'Entries, in insertion order', 16, 98);
      f.entries.forEach((e, i) => {
        const x = 16 + (i % 4) * 142, y = 106 + Math.floor(i / 4) * 36;
        box(z, x, y, 136, 30, `${i}: ${e.k} (hash ${e.h})`, { mono: true, s: 11, stroke: e.k === f.key ? c.cv : c.line, w: e.k === f.key ? 2.4 : 1.2 });
      });
      D.text(z.g, `${f.entries.length} keys in ${n} slots, room for ${Math.floor(n * 2 / 3)} before the next resize`, 16, 318, { s: 12, b: true, c: f.resized ? c.orange : c.ink2 });
    }
  });
})();
