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
