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
