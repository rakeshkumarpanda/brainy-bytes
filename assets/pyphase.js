/* ===== Python chapters: two step animations built on PYVM (assets/pyviz.js) =====
   <div class="viz" data-viz="pyjourney"></div>  the whole journey of a program through CPython. The map on the left
        grows one stage per step (nothing is shown before its step), and the panel beside it animates what that
        stage does to the reader's own code. The controls sit under both.
   <div class="viz" data-viz="pycvi"></div>      a compiler and an interpreter side by side on the same small program,
        with CPython as an optional third lane: the compiler translates the whole program before anything runs,
        the interpreter translates and runs one line at a time.
   Both take the reader's own code. PYVM supports assignments, numbers, strings, + - * / // % **, comparisons and
   print, len, max, min, abs, round, str, int and float. */
if (typeof VIZ !== 'undefined' && typeof PYVM !== 'undefined') (() => {
  const K = VIZ.kit, W = VIZ.widgets, esc = K.esc, $ = K.$;
  const reduce = () => typeof FUN !== 'undefined' && FUN.reduce;
  const FN_BUILTINS = ['print', 'len', 'max', 'min', 'abs', 'round'];
  const TYPE_BUILTINS = ['str', 'int', 'float'];
  const TOKEN_TIP = { NAME: 'name', NUMBER: 'number', STRING: 'string', OP: 'operator', NEWLINE: 'end of line', NL: 'blank line', COMMENT: 'comment', ENDMARKER: 'end of file' };
  /* items with the class pj-i fade in one after another. d is the gap in milliseconds */
  const stag = (k, d) => reduce() ? '' : ` style="animation-delay:${Math.round(k * d)}ms"`;
  const gap = (n, total = 2600, most = 260) => Math.max(40, Math.min(most, total / Math.max(1, n)));

  /* ---------------------------------------------------------------- the journey ---------- */
  const J_EXAMPLES = [
    ['Shopping bill', 'price = 40\nqty = 3\ntotal = price * qty + 5\nprint("Total:", total)'],
    ['Folding', 'seconds = 60 * 60 * 24\nprint(seconds)'],
    ['Built ins', 'name = "Asha"\nprint(len(name), max(3, 9, 4))'],
    ['NameError', 'speed = 60\nprint(distance / speed)'],
    ['Syntax error', 'price = 40\ntotal = (price * 3\nprint(total)']
  ];
  const STAGES = [
    { id: 'src', g: 0, t: 'main.py', s: 'source text', h: 'Read the file', p: 'CPython opens main.py and reads all of it as text, using UTF-8. Nothing runs yet.' },
    { id: 'tok', g: 0, t: 'Tokenizer', s: 'text to tokens', h: 'Tokenizer', p: 'The tokenizer reads the characters from left to right and groups them into tokens, the smallest pieces that mean something.' },
    { id: 'par', g: 0, t: 'Parser', s: 'tokens to a tree', h: 'Parser', p: 'The parser checks the tokens against the grammar and builds an abstract syntax tree. Brackets and spaces are gone, only the meaning is left.' },
    { id: 'cmp', g: 0, t: 'Compiler', s: 'tree to bytecode', h: 'Compiler', p: 'The compiler walks the tree and writes bytecode, one small instruction at a time. Arithmetic on plain numbers is worked out here, once.' },
    { id: 'pyc', g: 0, t: '.pyc file', s: 'imported modules only', side: 1, h: '__pycache__ and the .pyc file', p: 'For a module that another file imports, the bytecode is also saved to disk, so the next run can skip the first three stages.' },
    { id: 'code', g: 0, t: 'Code object', s: 'bytecode + names + constants', h: 'Code object', p: 'Everything the compiler made is packed into one code object: the instructions, the names they use and the constants.' },
    { id: 'loop', g: 1, t: 'Evaluation loop', s: 'one instruction at a time', h: 'Evaluation loop', p: 'A C function reads one instruction, does it, and moves to the next. Values wait on a value stack between instructions.' },
    { id: 'mem', g: 1, t: 'Objects and memory', s: 'names point at objects', h: 'Objects and memory', p: 'Every value is an object in memory. A name is only a label that points at one, and each object counts its references.' },
    { id: 'bi', g: 1, t: 'Built-ins and C code', s: 'print, len, max ...', h: 'Built-ins and C code', p: 'Names that your code never defines, such as print, are found in the builtins module. They are functions written in C.' },
    { id: 'out', g: 1, t: 'Output', s: 'what you see', h: 'Output', p: 'print writes text to sys.stdout and it appears on your screen. An error that nobody catches is printed as a traceback instead.' }
  ];
  const GROUPS = ['Compile time: before your first line runs', 'Run time: the Python Virtual Machine'];

  function typeOf(r) {
    if (r === 'True' || r === 'False') return 'bool';
    if (r === 'None') return 'NoneType';
    if (/^['"]/.test(r)) return 'str';
    if (/^-?\d+$/.test(r)) return 'int';
    return 'float';
  }
  function treeNode(n, depth, list) {
    let sub = '';
    const kids = [];
    switch (n.k) {
      case 'Assign': sub = n.target + ' ='; kids.push(n.value); break;
      case 'Expr': sub = 'expression'; kids.push(n.value); break;
      case 'Constant': sub = PYVM.repr(n.value); break;
      case 'Name': sub = n.id; break;
      case 'BinOp': case 'Compare': sub = n.op; kids.push(n.left, n.right); break;
      case 'UnaryOp': sub = '-'; kids.push(n.operand); break;
      case 'Call': sub = 'call'; kids.push(n.func, ...n.args); break;
    }
    const k = list.length;
    list.push(depth);
    return `<li><span class="pv-node k-${n.k} pj-i" data-k="${k}"><b>${esc(n.k)}</b>${sub ? `<code>${esc(sub)}</code>` : ''}</span>${kids.length ? `<ul>${kids.map(c => treeNode(c, depth + 1, list)).join('')}</ul>` : ''}</li>`;
  }

  /* the panel beside the map: one function per stage, each returns HTML whose .pj-i items appear one by one */
  const PANEL = {
    src(r, src) {
      const lines = src.split('\n');
      const d = gap(lines.length, 1600, 320);
      return `<div class="pj-file"><div class="pj-fh">main.py</div><ol class="pj-lines">${lines.map((l, k) => `<li class="pj-i"${stag(k, d)}><span>${k + 1}</span><code>${esc(l) || ' '}</code></li>`).join('')}</ol></div>
        <p class="pj-note pj-i"${stag(lines.length, d)}>${src.length} characters on ${lines.length} line${lines.length === 1 ? '' : 's'}. The whole file is read before anything else happens.</p>`;
    },
    tok(r, src) {
      let toks = r.tokens;
      if (!toks) { try { toks = PYVM.tokenize(src); } catch (e) { return `<p class="pj-err">The tokenizer stopped: ${esc(e.message)}</p>`; } }
      const shown = toks.slice(0, 40), d = gap(shown.length, 3000, 220);
      return `<div class="pj-toks">${shown.map((t, k) => `<span class="pv-tok tt-${t.type} pj-i"${stag(k, d)}><small>${esc(TOKEN_TIP[t.type] || t.type)}</small><code>${t.text ? esc(t.text) : '⏎'}</code></span>`).join('')}${toks.length > 40 ? `<span class="pj-more">and ${toks.length - 40} more</span>` : ''}</div>
        <p class="pj-note pj-i"${stag(shown.length, d)}>${toks.length} tokens. ⏎ marks a NEWLINE token, the end of one statement. Spaces between tokens are dropped.</p>`;
    },
    par(r) {
      if (r.stage === 'parse') return `<div class="pj-err pj-i"><b>${esc(r.error.type)}</b> on line ${r.error.line}: ${esc(r.error.msg)}</div><p class="pj-note pj-i"${stag(1, 500)}>The parser found a mistake. Because the whole file is parsed before anything runs, not even line 1 runs. The journey stops here.</p>`;
      const depths = [];
      const html = r.tree.map(st => treeNode(st, 1, depths)).join('');
      const d = gap(Math.max(...depths, 1), 2400, 600);
      const withDelay = html.replace(/class="(pv-node [^"]*pj-i)" data-k="(\d+)"/g, (m, c, k) => `class="${c}"${stag(depths[+k], d)}`);
      return `<div class="pj-tree"><ul><li><span class="pv-node k-Module pj-i"><b>Module</b></span><ul>${withDelay}</ul></li></ul></div>
        <p class="pj-note pj-i"${stag(Math.max(...depths) + 1, d)}>Each line became one branch. Read a branch from the bottom up: the deepest nodes are worked out first, so the tree already knows that * comes before +.</p>`;
    },
    cmp(r) {
      const code = r.code, d = gap(code.length, 3200, 260);
      const folded = r.tree.some(st => JSON.stringify(st, (k, v) => typeof v === 'bigint' ? String(v) : v).includes('"BinOp"')) && code.every(c => c.op !== 'BINARY_OP');
      return `<ol class="pj-code">${code.map((c, k) => `<li class="pj-i"${stag(k, d)}><span class="ln">${c.starts && c.line ? 'line ' + c.line : ''}</span><b>${esc(c.op)}</b>${c.arg !== null && c.arg !== undefined && c.op !== 'RESUME' ? ` <i>${esc(String(c.arg))}</i>` : ''}${c.rep ? ` <code>(${esc(c.rep)})</code>` : ''}</li>`).join('')}</ol>
        <p class="pj-note pj-i"${stag(code.length, d)}>${code.length} instructions. ${folded ? 'There is no BINARY_OP at all: the compiler already did the arithmetic on plain numbers. This is called constant folding.' : 'Every operator in your code became a BINARY_OP or COMPARE_OP that runs later, when the line runs.'}</p>`;
    },
    pyc() {
      const parts = [['Magic number', '4 bytes', 'changes with every bytecode format, so 3.13 and 3.14 never mix'], ['Flags', '4 bytes', '0 means: check the source time and size'],
        ['Source time', '4 bytes', 'when the .py file was last changed'], ['Source size', '4 bytes', 'the size of the .py file'], ['Code object', 'the rest', 'the bytecode, saved with the marshal module']];
      return `<div class="pj-pyc"><div class="pj-fh">__pycache__/shop.cpython-314.pyc</div>${parts.map((p, k) => `<div class="pj-byte pj-i b${k}"${stag(k, 420)}><b>${p[0]}</b><small>${p[1]}</small><span>${p[2]}</span></div>`).join('')}</div>
        <p class="pj-note pj-i"${stag(5, 420)}>Your own main.py is never saved like this. Only a module that some other file imports, such as <code>import shop</code>, gets a .pyc file. If the time or size no longer match, Python compiles the module again.</p>`;
    },
    code(r) {
      const consts = r.code.filter(c => c.op === 'LOAD_CONST').map(c => c.rep);
      const small = r.code.filter(c => c.op === 'LOAD_SMALL_INT').map(c => c.arg);
      const rows = [['co_filename', "'main.py'"], ['co_name', "'&lt;module&gt;'"], ['co_names', '(' + r.names.map(n => `'${esc(n)}'`).join(', ') + (r.names.length === 1 ? ',' : '') + ')'],
        ['co_consts', '(' + [...new Set(consts)].map(esc).join(', ') + (new Set(consts).size === 1 ? ',' : '') + ')'], ['instructions', String(r.code.length)]];
      return `<div class="pj-obj"><div class="pj-fh">code object &lt;module&gt;</div>${rows.map((x, k) => `<div class="pj-row pj-i"${stag(k, 380)}><b>${x[0]}</b><code>${x[1]}</code></div>`).join('')}</div>
        <p class="pj-note pj-i"${stag(rows.length, 380)}>${small.length ? `The small integers ${[...new Set(small)].join(', ')} are not in co_consts. Numbers from 0 to 255 have their own instruction, LOAD_SMALL_INT, new in 3.14.` : 'This is a real Python object. In your own code, a function keeps its code object in <code>func.__code__</code>.'}</p>`;
    },
    loop(r, src, host, seq) {
      const fr = r.exec.frames, code = r.code;
      host.innerHTML = `<div class="pj-run"><div class="pj-now"><span>Instruction now</span><b class="pj-op">ready</b><small class="pj-n"></small><ol class="pj-trail"></ol></div><div class="pj-stk"><span>Value stack</span><div class="pj-cells"></div></div></div><p class="pj-note pj-rn"></p>`;
      const paint = i => {
        const f = fr[i], c = f.pc >= 0 ? code[f.pc] : null;
        $('.pj-op', host).textContent = c ? c.op + (c.rep ? ' ' + c.rep : (c.arg !== null && c.arg !== undefined && c.op !== 'RESUME' ? ' ' + c.arg : '')) : 'ready';
        $('.pj-n', host).textContent = `step ${i} of ${fr.length - 1}`;
        $('.pj-trail', host).innerHTML = fr.slice(Math.max(1, i - 4), i).map(g => g.pc >= 0 ? `<li>${esc(code[g.pc].op)}${code[g.pc].rep ? ' ' + esc(code[g.pc].rep) : ''}</li>` : '').join('');
        $('.pj-cells', host).innerHTML = f.stack.length ? f.stack.map(s => `<span class="pv-cell t-${esc(s.t)}"><code>${esc(s.r)}</code><small>${esc(s.t)}</small></span>`).join('') : '<em>empty</em>';
        $('.pj-rn', host).textContent = f.note;
      };
      if (reduce()) { paint(fr.length - 1); return null; }
      const d = gap(fr.length, 3800, 520);
      seq.run(fr.map((_, i) => () => { if (host.isConnected) paint(i); }), d);
      return null;
    },
    mem(r) {
      const last = r.exec.frames[r.exec.frames.length - 1];
      const ns = Object.entries(last.names);
      if (!ns.length) return '<p class="pj-note">This program binds no names, so the only objects are the values it prints and throws away.</p>';
      return `<div class="pj-mem"><div class="pj-mh"><span>Names (module globals)</span><span>Objects in memory</span></div>${ns.map(([n, v], k) => `<div class="pj-ref pj-i"${stag(k, 420)}><b>${esc(n)}</b><i></i><span class="pj-objv t-${typeOf(v)}"><small>${typeOf(v)}</small><code>${esc(v)}</code></span></div>`).join('')}</div>
        <p class="pj-note pj-i"${stag(ns.length, 420)}>The names live in a dictionary. Each object keeps a reference count, and when it falls to 0 the memory is given back at once. Small integers, True, False and None are immortal since Python 3.12, so they are never freed.</p>`;
    },
    bi(r) {
      const used = [...new Set(r.code.filter(c => c.op === 'LOAD_NAME' && !r.tree.some(st => st.k === 'Assign' && st.target === c.rep) && (FN_BUILTINS.includes(c.rep) || TYPE_BUILTINS.includes(c.rep))).map(c => c.rep))];
      if (!used.length) return '<p class="pj-note">This program calls no built in function. Try the Built ins example above.</p>';
      const n = used[0];
      const chain = [[`LOAD_NAME ${n}`, `${n} is not in the module globals.`], ['builtins module', `So Python looks in the builtins module and finds ${n} there.`],
        FN_BUILTINS.includes(n) ? [`builtin_${n}()`, 'A function written in C, in the file Python/bltinmodule.c of the CPython source.'] : [`${n} type`, `${n} is a class written in C. Calling it makes a new object.`],
        n === 'print' ? ['sys.stdout', 'print turns each argument into text with str() and writes it out, with spaces between and a newline at the end.'] : ['return value', 'The result goes back on the value stack, ready for the next instruction.']];
      return `<div class="pj-chain">${chain.map((c, k) => `<div class="pj-link pj-i"${stag(k, 480)}><b>${esc(c[0])}</b><span>${esc(c[1])}</span></div>`).join('')}</div>
        <p class="pj-note pj-i"${stag(chain.length, 480)}>Built ins used here: ${used.map(u => `<code>${esc(u)}</code>`).join(', ')}. Because they are written in C, they run much faster than the same work written in Python.</p>`;
    },
    out(r) {
      const e = r.exec.error;
      const lines = r.exec.out.slice();
      if (e && e.type !== 'Demo') lines.push('Traceback (most recent call last):', `  File "main.py", line ${e.line}, in <module>`, `${e.type}: ${e.msg}`);
      const d = gap(lines.length, 1800, 320);
      return `<div class="pj-term"><div class="pj-fh">Terminal: python main.py</div><pre>${lines.length ? lines.map((l, k) => `<span class="pj-i${e && k >= r.exec.out.length ? ' bad' : ''}"${stag(k, d)}>${esc(l)}</span>`).join('\n') : '<span class="pj-i">(nothing printed)</span>'}</pre></div>
        <p class="pj-note pj-i"${stag(lines.length, d)}>${e && e.type !== 'Demo' ? `The program ran until line ${e.line}. ${e.type} was raised there, nothing caught it, so Python printed a traceback and stopped.` : 'The journey is complete. CPython does all of this every time you press Run, usually in a few milliseconds.'}</p>`;
    }
  };

  W.pyjourney = el => {
    const uid = el.dataset.k || 'pj';
    const b = K.shell(el, 'From main.py to output, one phase at a time', 'Each step adds the next phase to the map. The panel beside it shows what that phase does to your code. Edit the program to change every phase.');
    b.innerHTML = `<div class="pv-top"><label class="pv-lbl" for="pj-src-${uid}">Your program</label><div class="pv-ex">${J_EXAMPLES.map((e, i) => `<button type="button" data-ex="${i}">${esc(e[0])}</button>`).join('')}</div></div>
      <textarea class="pv-src pj-src" id="pj-src-${uid}" spellcheck="false" autocapitalize="off" rows="4" aria-label="Python code for the journey"></textarea>
      <div class="pj-grid"><div class="pj-map">${GROUPS.map((g, gi) => `<div class="pj-grp g${gi}" data-g="${gi}"><div class="pj-gt">${g}</div>${STAGES.filter(s => s.g === gi).map(s => `<div class="pj-s${s.side ? ' side' : ''}" data-s="${s.id}"><b>${s.t}</b><small>${s.s}</small></div>`).join('')}</div>`).join('')}</div>
      <div class="pj-panel" aria-live="polite"><div class="pj-ph"><span class="pj-kick"></span><h4></h4><p></p></div><div class="pj-body"></div><button type="button" class="pj-again" hidden>Play this phase again</button></div></div>
      <div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const ta = $('.pj-src', b), msg = $('.vz-msg', b), body = $('.pj-body', b), again = $('.pj-again', b);
    const seq = K.Seq();
    let res = null, src = '', steps = [];
    function render(i) {
      seq.stop();
      const upto = steps.slice(0, i);
      b.querySelectorAll('.pj-s').forEach(s => { const k = upto.indexOf(s.dataset.s); s.classList.toggle('seen', k >= 0); s.classList.toggle('cur', k >= 0 && k === i - 1); });
      b.querySelectorAll('.pj-grp').forEach(g => g.classList.toggle('seen', [...g.querySelectorAll('.pj-s')].some(s => s.classList.contains('seen'))));
      const kick = $('.pj-kick', b), h = $('.pj-ph h4', b), p = $('.pj-ph p', b);
      if (!i) {
        kick.textContent = 'Not started'; h.textContent = 'The map is empty'; p.textContent = 'Press Play, or the step arrow, and the first phase appears.';
        body.innerHTML = ''; again.hidden = true;
        msg.textContent = res.stage === 'demo' ? res.error.msg : 'Press ▶ Play to start the journey. Each phase appears only when the journey reaches it.';
        return;
      }
      const st = STAGES.find(s => s.id === steps[i - 1]);
      kick.textContent = `Phase ${i} of ${steps.length} · ${GROUPS[st.g].split(':')[0]}`;
      h.textContent = st.h; p.textContent = st.p;
      body.innerHTML = '';
      const html = PANEL[st.id](res, src, body, seq);
      if (html) body.innerHTML = html;
      again.hidden = false;
      const last = i === steps.length;
      msg.innerHTML = `<b>Step ${i} of ${steps.length}.</b> ${esc(st.p)}${last && steps.length < STAGES.length ? ' The program never reaches the run time phases.' : ''}`;
    }
    const P = K.Player($('.vz-p', b), render, 5200);
    again.onclick = () => render(P.i);
    function build() {
      src = ta.value.replace(/\s+$/, '');
      res = PYVM.analyse(src);
      if (res.stage === 'demo') steps = ['src'];
      else if (res.stage === 'parse') steps = ['src', 'tok', 'par'];
      else steps = STAGES.map(s => s.id);
      P.load(steps.length + 1);
    }
    b.querySelector('.pv-ex').addEventListener('click', e => { const t = e.target.closest('button'); if (!t) return; ta.value = J_EXAMPLES[+t.dataset.ex][1]; build(); });
    let timer = null;
    ta.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(build, 400); });
    ta.value = J_EXAMPLES[0][1];
    build();
  };

  /* ------------------------------------------------- compiler, interpreter and CPython ---------- */
  const C_EXAMPLES = [
    ['No mistake', 'price = 40\nqty = 3\ntotal = price * qty\nprint("Total:", total)\nprint("Thank you")'],
    ['Syntax mistake on line 3', 'price = 40\nprint("Price:", price)\ntotal = (price * 3\nprint("Total:", total)'],
    ['Unknown name on line 3', 'price = 40\nprint("Price:", price)\ntotal = price * qty\nprint("Total:", total)'],
    ['Divide by zero on line 3', 'total = 120\nprint("Total:", total)\neach = total / 0\nprint("Each:", each)']
  ];
  const COMPILE_TIME = new Set(['NameError', 'TypeError']);  /* a compiled language with declared, typed names catches these before it runs */

  /* everything each lane does, worked out once per program. A step is { lines: {n: state}, made: [...], out: [...], err, box } */
  function plan(src) {
    const lines = src.split('\n');
    const real = lines.map((l, k) => ({ n: k + 1, t: l })).filter(x => x.t.trim());
    const full = PYVM.analyse(src);
    if (full.stage === 'demo') return { demo: full.error.msg };
    const outAfter = n => { const r = PYVM.analyse(lines.slice(0, n).join('\n')); return r.exec ? r.exec.out.slice() : []; };
    const perr = full.stage === 'parse' ? full.error : null;
    const rerr = !perr && full.exec.error && full.exec.error.type !== 'Demo' ? full.exec.error : null;
    const allRead = st => Object.fromEntries(real.map(x => [x.n, st]));
    const errText = e => `${e.type} on line ${e.line}: ${e.msg}`;

    /* compiler: read all, translate all, save the program, then run it */
    const comp = [];
    comp.push({ lines: allRead('read'), made: [], out: [], box: 'Reading the whole program, every line, before translating any of it.' });
    const compErr = perr || (rerr && COMPILE_TIME.has(rerr.type) ? rerr : null);
    if (compErr) {
      comp.push({ lines: { ...allRead('read'), [compErr.line]: 'bad' }, made: [], out: [], err: (perr ? 'Compile error. ' : 'Compile error, the compiler checks names and types. ') + errText(compErr), box: 'The compiler found a mistake. No program is made, so not a single line runs.', end: 1 });
    } else {
      comp.push({ lines: allRead('done'), made: real.map(x => `line ${x.n} → machine code`), out: [], box: 'Translating every line into machine code, all in one go.' });
      comp.push({ lines: allRead('done'), made: real.map(x => `line ${x.n} → machine code`), file: 'program.exe saved', out: [], box: 'The whole translation is saved as one program file. It can now run again and again with no translating.' });
      const out = full.exec.out.slice();
      comp.push({ lines: allRead('done'), made: real.map(x => `line ${x.n} → machine code`), file: 'program.exe saved', out, err: rerr ? 'Run time error. ' + errText(rerr) : '', box: rerr ? 'The program runs fast, then crashes on a mistake that only shows up while running.' : 'The saved program runs straight away, at full speed.', end: 1, runs: 1 });
    }
    /* interpreter: read, translate and run one line, then the next */
    const intr = [];
    const stopAt = (perr || rerr || {}).line || Infinity;
    for (const x of real) {
      const prevLines = Object.fromEntries(real.filter(y => y.n < x.n).map(y => [y.n, 'done']));
      if (x.n >= stopAt) {
        intr.push({ lines: { ...prevLines, [x.n]: 'bad' }, made: real.filter(y => y.n < x.n).map(y => `line ${y.n} → done`), out: outAfter(x.n - 1), err: (perr ? 'Syntax error found only now. ' : 'Error while running. ') + errText(perr || rerr), box: `Line ${x.n} has a mistake. The lines before it have already run and printed.`, end: 1 });
        break;
      }
      intr.push({ lines: { ...prevLines, [x.n]: 'cur' }, made: real.filter(y => y.n <= x.n).map(y => `line ${y.n} → done`), out: outAfter(x.n), box: `Line ${x.n}: read it, translate it, run it. Then forget the translation and move on.`, runs: 1 });
    }
    if (intr.length && !intr[intr.length - 1].end) intr[intr.length - 1].end = 1;
    /* CPython: read and compile the whole file to bytecode, then the evaluation loop runs it line by line */
    const cpy = [];
    cpy.push({ lines: allRead('read'), made: [], out: [], box: 'Reading and parsing the whole file, as a compiler does.' });
    if (perr) cpy.push({ lines: { ...allRead('read'), [perr.line]: 'bad' }, made: [], out: [], err: 'SyntaxError before anything runs. ' + errText(perr), box: 'The parser found the mistake while reading. Not even line 1 runs, just like the compiler.', end: 1 });
    else {
      const bc = real.map(x => `line ${x.n} → bytecode`);
      cpy.push({ lines: allRead('done'), made: bc, file: 'code object in memory', out: [], box: 'The whole file becomes bytecode in one go. Names are not checked yet.' });
      for (const x of real) {
        const prevLines = { ...allRead('done') };
        if (rerr && x.n >= rerr.line) {
          cpy.push({ lines: { ...prevLines, [x.n]: 'bad' }, made: bc, file: 'code object in memory', out: outAfter(x.n - 1), err: 'Error while running. ' + errText(rerr), box: `The evaluation loop reaches line ${x.n} and the mistake is found only now, like an interpreter.`, end: 1 });
          break;
        }
        cpy.push({ lines: { ...prevLines, [x.n]: 'cur' }, made: bc, file: 'code object in memory', out: outAfter(x.n), box: `The evaluation loop runs the bytecode of line ${x.n}, one instruction at a time.`, runs: 1 });
      }
      if (!cpy[cpy.length - 1].end) cpy[cpy.length - 1].end = 1;
    }
    return { real, comp, intr, cpy };
  }

  W.pycvi = el => {
    const uid = el.dataset.k || 'ci';
    const b = K.shell(el, 'Compiler and interpreter, side by side', 'The same program goes to both. Watch when each one translates and when the first output appears. Pick a mistake to see who finds it first.');
    b.innerHTML = `<div class="pv-top"><label class="pv-lbl" for="ci-src-${uid}">The program</label><div class="pv-ex">${C_EXAMPLES.map((e, i) => `<button type="button" data-ex="${i}">${esc(e[0])}</button>`).join('')}</div></div>
      <textarea class="pv-src ci-src" id="ci-src-${uid}" spellcheck="false" autocapitalize="off" rows="5" aria-label="Program for the compiler and the interpreter"></textarea>
      <label class="ci-opt"><input type="checkbox" class="ci-cpy"> Show CPython as a third lane</label>
      <div class="ci-grid"></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const ta = $('.ci-src', b), grid = $('.ci-grid', b), msg = $('.vz-msg', b), cpyBox = $('.ci-cpy', b);
    const LANES = [
      { k: 'comp', t: 'Compiler', s: 'like C, C++ or Go', made: 'Translated program' },
      { k: 'intr', t: 'Interpreter', s: 'like an old BASIC, or a shell running a script', made: 'Translated so far' },
      { k: 'cpy', t: 'CPython', s: 'compiles first, then interprets bytecode', made: 'Bytecode' }
    ];
    let pl = null, total = 1;
    const lanes = () => LANES.filter(l => l.k !== 'cpy' || cpyBox.checked);
    function laneState(l, i) {
      const arr = pl[l.k];
      if (!i) return null;
      return arr[Math.min(i, arr.length) - 1];
    }
    function firstOut(l) { const k = pl[l.k].findIndex(s => s.out.length); return k < 0 ? null : k + 1; }
    function show(i) {
      if (pl.demo) { grid.innerHTML = ''; msg.textContent = pl.demo; return; }
      const ls = lanes();
      grid.className = 'ci-grid n' + ls.length;
      grid.innerHTML = ls.map(l => {
        const st = laneState(l, i);
        const done = st && i >= pl[l.k].length;
        const fo = firstOut(l);
        return `<div class="ci-lane ${l.k}${st ? ' on' : ''}"><div class="ci-h"><b>${l.t}</b><small>${l.s}</small></div>
          ${st ? `<ol class="ci-lines">${pl.real.map(x => `<li class="${st.lines[x.n] || ''}"><span>${x.n}</span><code>${esc(x.t)}</code></li>`).join('')}</ol>
          <div class="ci-box">${esc(st.box)}</div>
          ${st.made.length ? `<div class="ci-made"><span>${l.made}${st.file ? ' · ' + esc(st.file) : ''}</span>${st.made.map(m => `<i>${esc(m)}</i>`).join('')}</div>` : ''}
          ${st.out.length || st.err ? `<div class="ci-out"><span>Output</span><pre>${esc(st.out.join('\n'))}${st.err ? `${st.out.length ? '\n' : ''}<b>${esc(st.err)}</b>` : ''}</pre></div>` : ''}
          ${done ? `<div class="ci-end">Finished after step ${pl[l.k].length}. ${fo ? `First output at step ${fo}.` : 'No output at all.'}</div>` : ''}` : '<div class="ci-wait">Waiting for step 1</div>'}</div>`;
      }).join('');
      msg.innerHTML = i ? `<b>Step ${i} of ${total - 1}.</b> ${ls.map(l => { const st = laneState(l, i); return `<span class="ci-m">${l.t}: ${i > pl[l.k].length ? 'finished.' : esc(st.box)}</span>`; }).join(' ')}`
        : 'Press ▶ Play. Both lanes start at the same moment, and every box appears only when its step is reached.';
    }
    const P = K.Player($('.vz-p', b), show, 2200);
    function build(keep) {
      pl = plan(ta.value.replace(/\s+$/, ''));
      total = pl.demo ? 1 : 1 + Math.max(...lanes().map(l => pl[l.k].length));
      P.load(total, keep ? Math.min(P.i, total - 1) : 0);
    }
    b.querySelector('.pv-ex').addEventListener('click', e => { const t = e.target.closest('button'); if (!t) return; ta.value = C_EXAMPLES[+t.dataset.ex][1]; build(); });
    cpyBox.addEventListener('change', () => build(true));
    let timer = null;
    ta.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(() => build(), 400); });
    ta.value = C_EXAMPLES[0][1];
    build();
  };
})();
