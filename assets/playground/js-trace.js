/* ===== Code Playground: line by line runner for JavaScript and TypeScript =====
   The browser runs JavaScript itself. To step through it, this file first reads the code with acorn
   (a JavaScript parser) and adds a small call before every statement:  __t(line, getter, names)
   That call records the line, the call stack, each variable's value and how much output exists so far.
   Function bodies also get __e (enter) and __x (leave), and return values pass through __r.
   The program then runs once, and the page plays the recording forward and back.

   JT.run(code, { trace, stdin, lineMap, maxSteps, maxOps }) -> { out: [{s, e}], trace, error, stopped }
   lineMap (TypeScript only) turns a line of the compiled JavaScript back into the line you wrote. */
var JT = (typeof self !== 'undefined' ? self : globalThis).JT = {};

(() => {
  const ACORN = () => (typeof self !== 'undefined' ? self : globalThis).acorn;

  /* ---------- 1. values as text, close to how Node.js prints them ---------- */
  function q(s) { return "'" + String(s).replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, '\\n') + "'"; }
  function keyText(k) { return /^[A-Za-z_$][\w$]*$/.test(k) ? k : q(k); }
  function inspect(v, depth, seen, top) {
    depth = depth || 0; seen = seen || new Set();
    const t = typeof v;
    if (v === null) return 'null';
    if (t === 'undefined') return 'undefined';
    if (t === 'string') return top ? v : q(v);
    if (t === 'number') return Object.is(v, -0) ? '-0' : String(v);
    if (t === 'bigint') return v + 'n';
    if (t === 'boolean') return String(v);
    if (t === 'symbol') return v.toString();
    if (t === 'function') {
      if (/^class\s/.test(Function.prototype.toString.call(v))) return '[class ' + (v.name || '(anonymous)') + ']';
      return v.name ? '[Function: ' + v.name + ']' : '[Function (anonymous)]';
    }
    if (seen.has(v)) return '[Circular *1]';
    if (v instanceof Error) return v.stack && false ? v.stack : (v.name || 'Error') + ': ' + v.message;
    if (v instanceof Date) return isNaN(v) ? 'Invalid Date' : v.toISOString();
    if (v instanceof RegExp) return String(v);
    if (depth > 2) return Array.isArray(v) ? '[Array]' : '[Object]';
    seen.add(v);
    let parts, open, close, prefix = '';
    try {
      if (Array.isArray(v)) {
        parts = [];
        let holes = 0;
        for (let i = 0; i < v.length; i++) {
          if (!(i in v)) { holes++; continue; }
          if (holes) { parts.push(`<${holes} empty item${holes > 1 ? 's' : ''}>`); holes = 0; }
          if (parts.length >= 100) { parts.push(`... ${v.length - i} more item${v.length - i > 1 ? 's' : ''}`); break; }
          parts.push(inspect(v[i], depth + 1, seen));
        }
        if (holes) parts.push(`<${holes} empty item${holes > 1 ? 's' : ''}>`);
        for (const k of Object.keys(v)) if (!/^\d+$/.test(k)) parts.push(keyText(k) + ': ' + inspect(v[k], depth + 1, seen));
        open = '['; close = ']';
        if (!parts.length) return '[]';
      } else if (v instanceof Map) {
        parts = [...v].map(([k, x]) => inspect(k, depth + 1, seen) + ' => ' + inspect(x, depth + 1, seen));
        prefix = 'Map(' + v.size + ') '; open = '{'; close = '}';
        if (!parts.length) return prefix + '{}';
      } else if (v instanceof Set) {
        parts = [...v].map(x => inspect(x, depth + 1, seen));
        prefix = 'Set(' + v.size + ') '; open = '{'; close = '}';
        if (!parts.length) return prefix + '{}';
      } else if (ArrayBuffer.isView(v)) {
        parts = Array.from(v, x => inspect(x, depth + 1, seen));
        prefix = v.constructor.name + '(' + v.length + ') '; open = '['; close = ']';
      } else if (v instanceof Promise) {
        return 'Promise { <pending> }';
      } else {
        const proto = Object.getPrototypeOf(v);
        const cname = proto && proto.constructor && proto.constructor.name;
        if (proto === null) prefix = '[Object: null prototype] ';
        else if (cname && cname !== 'Object') prefix = cname + ' ';
        parts = Object.keys(v).map(k => keyText(k) + ': ' + inspect(v[k], depth + 1, seen));
        open = '{'; close = '}';
        if (!parts.length) return prefix + '{}';
      }
    } finally { seen.delete(v); }
    const one = prefix + open + ' ' + parts.join(', ') + ' ' + close;
    if (one.length <= 72 && !one.includes('\n')) return one;
    const pad = '  '.repeat(depth + 1);
    return prefix + open + '\n' + parts.map(p => pad + p).join(',\n') + '\n' + '  '.repeat(depth) + close;
  }
  /* short form for the Variables panel */
  function short(v) {
    let s;
    try { s = typeof v === 'string' ? q(v) : inspect(v, 1); } catch (e) { s = '?'; }
    s = s.replace(/\s*\n\s*/g, ' ');
    return s.length > 120 ? s.slice(0, 117) + '...' : s;
  }
  function format(args) {
    /* console.log('%d apples', 3) style */
    if (typeof args[0] === 'string' && /%[sdifoOjc%]/.test(args[0])) {
      let i = 1;
      const first = args[0].replace(/%([sdifoOjc%])/g, (m, c) => {
        if (c === '%') return '%';
        if (i >= args.length) return m;
        const a = args[i++];
        switch (c) {
          case 's': return typeof a === 'string' ? a : inspect(a, 1);
          case 'd': case 'i': return typeof a === 'bigint' ? a + 'n' : String(c === 'i' ? parseInt(a) : Number(a));
          case 'f': return String(parseFloat(a));
          case 'c': return '';
          default: return inspect(a);
        }
      });
      return [first].concat(args.slice(i).map(a => inspect(a, 0, null, true))).join(' ');
    }
    return args.map(a => inspect(a, 0, null, true)).join(' ');
  }
  JT.inspect = inspect;

  /* ---------- 2. adding the recording calls ---------- */
  function instrument(src, lineMap) {
    const acorn = ACORN();
    let ast;
    try {
      ast = acorn.parse(src, { ecmaVersion: 'latest', sourceType: 'script', locations: true, allowAwaitOutsideFunction: true, allowHashBang: true });
    } catch (e) {
      const line = e.loc ? e.loc.line : 1;
      return { error: { msg: 'SyntaxError: ' + e.message.replace(/\s*\(\d+:\d+\)$/, ''), line: mapLine(line, lineMap) } };
    }
    const ins = []; /* [pos, text, order] */
    const add = (pos, text, order) => ins.push([pos, text, order || 0]);
    const L = n => mapLine(n.loc.start.line, lineMap);

    /* names visible in each scope */
    function declNames(pat, out) {
      if (!pat) return;
      switch (pat.type) {
        case 'Identifier': out.push(pat.name); break;
        case 'ObjectPattern': pat.properties.forEach(p => declNames(p.type === 'RestElement' ? p.argument : p.value, out)); break;
        case 'ArrayPattern': pat.elements.forEach(e => declNames(e, out)); break;
        case 'RestElement': declNames(pat.argument, out); break;
        case 'AssignmentPattern': declNames(pat.left, out); break;
      }
    }
    /* var declarations and function declarations anywhere in a function body (they are hoisted) */
    function hoisted(body, out) {
      const visit = n => {
        if (!n || typeof n.type !== 'string') return;
        if (n.type === 'VariableDeclaration' && n.kind === 'var') n.declarations.forEach(d => declNames(d.id, out));
        if (n.type === 'FunctionDeclaration') { if (n.id) out.push(n.id.name); return; }
        if (/Function|Class/.test(n.type)) return;
        for (const k in n) {
          if (k === 'loc' || k === 'start' || k === 'end') continue;
          const c = n[k];
          if (Array.isArray(c)) c.forEach(visit); else if (c && typeof c.type === 'string') visit(c);
        }
      };
      visit(body);
    }
    function blockNames(stmts) {
      const out = [];
      for (const s of stmts) {
        if (s.type === 'VariableDeclaration' && s.kind !== 'var') s.declarations.forEach(d => declNames(d.id, out));
        if (s.type === 'ClassDeclaration' && s.id) out.push(s.id.name);
      }
      return out;
    }
    const scopes = []; /* stack of name lists */
    function visible() {
      const seen = new Set(), out = [];
      for (let i = scopes.length - 1; i >= 0; i--) {
        for (const n of scopes[i].names) if (!seen.has(n) && !n.startsWith('__')) { seen.add(n); out.push(n); }
        if (scopes[i].fn) break;
      }
      return out;
    }
    function mark(stmt) {
      const names = visible();
      const getter = names.length ? `function(__i){switch(__i){${names.map((n, i) => `case ${i}:return ${n};`).join('')}}}` : 'null';
      return `__t(${L(stmt)},${getter},${JSON.stringify(names)});`;
    }
    function stmtList(list, extra) {
      scopes.push({ names: blockNames(list).concat(extra || []), fn: false });
      for (const s of list) {
        if (s.type !== 'FunctionDeclaration' && s.type !== 'EmptyStatement') add(s.start, mark(s));
        walkStmt(s);
      }
      scopes.pop();
    }
    function single(s) {
      /* a statement without braces, like the body of  if (x) y = 1;  */
      if (!s) return;
      if (s.type === 'BlockStatement') { walkStmt(s); return; }
      add(s.start, '{' + mark(s), 1);
      walkStmt(s);
      add(s.end, '}', -1);
    }
    function fnName(n, parent) {
      if (n.id) return n.id.name;
      if (parent && parent.type === 'VariableDeclarator' && parent.id.type === 'Identifier') return parent.id.name;
      if (parent && parent.type === 'MethodDefinition') return (parent.key.name || parent.key.value || 'method');
      if (parent && parent.type === 'Property' && parent.key) return parent.key.name || parent.key.value || 'function';
      if (parent && parent.type === 'AssignmentExpression' && parent.left.type === 'MemberExpression' && parent.left.property) return parent.left.property.name || 'function';
      return n.type === 'ArrowFunctionExpression' ? 'arrow function' : 'function';
    }
    function walkFn(n, parent, cls) {
      const name = (cls ? cls + '.' : '') + fnName(n, parent);
      const params = []; n.params.forEach(p => declNames(p, params));
      const hv = []; hoisted(n.body, hv);
      scopes.push({ names: params.concat(hv), fn: true });
      n.params.forEach(p => walkExpr(p, n));
      const line = L(n);
      if (n.body.type === 'BlockStatement') {
        add(n.body.start + 1, `__e(${JSON.stringify(name)},${line});try{`, 1);
        stmtList(n.body.body);
        add(n.body.end - 1, `}finally{__x()}`, -1);
      } else {
        /* x => x * 2 becomes x => { enter; try { return record(x * 2) } finally { leave } } */
        const names = visible();
        const getter = names.length ? `function(__i){switch(__i){${names.map((v, i) => `case ${i}:return ${v};`).join('')}}}` : 'null';
        add(n.body.start, `{__e(${JSON.stringify(name)},${line});try{__t(${L(n.body)},${getter},${JSON.stringify(names)});return __r((`, 1);
        walkExpr(n.body, n);
        add(n.body.end, `),${L(n.body)})}finally{__x()}}`, -1);
      }
      scopes.pop();
    }
    function walkStmt(s) {
      if (!s) return;
      switch (s.type) {
        case 'BlockStatement': stmtList(s.body); break;
        case 'ExpressionStatement': walkExpr(s.expression, s); break;
        case 'VariableDeclaration': s.declarations.forEach(d => { walkExpr(d.id, d); walkExpr(d.init, d); }); break;
        case 'FunctionDeclaration': walkFn(s, s); break;
        case 'ClassDeclaration': case 'ClassExpression': walkClass(s); break;
        case 'ReturnStatement':
          if (s.argument) { add(s.argument.start, '__r((', 1); walkExpr(s.argument, s); add(s.argument.end, `),${L(s)})`, -1); }
          else add(s.start + 6, ` __r(undefined,${L(s)})`, 1);
          break;
        case 'IfStatement': walkExpr(s.test, s); single(s.consequent); if (s.alternate) single(s.alternate); break;
        case 'ForStatement': {
          const extra = []; if (s.init && s.init.type === 'VariableDeclaration' && s.init.kind !== 'var') s.init.declarations.forEach(d => declNames(d.id, extra));
          scopes.push({ names: extra, fn: false });
          if (s.init) { if (s.init.type === 'VariableDeclaration') walkStmt(s.init); else walkExpr(s.init, s); }
          walkExpr(s.test, s); walkExpr(s.update, s); single(s.body);
          scopes.pop();
          break;
        }
        case 'ForInStatement': case 'ForOfStatement': {
          const extra = []; if (s.left.type === 'VariableDeclaration' && s.left.kind !== 'var') s.left.declarations.forEach(d => declNames(d.id, extra));
          scopes.push({ names: extra, fn: false });
          walkExpr(s.right, s); single(s.body);
          scopes.pop();
          break;
        }
        case 'WhileStatement': walkExpr(s.test, s); single(s.body); break;
        case 'DoWhileStatement': single(s.body); walkExpr(s.test, s); break;
        case 'LabeledStatement': walkStmt(s.body); break;
        case 'SwitchStatement':
          walkExpr(s.discriminant, s);
          scopes.push({ names: blockNames(s.cases.flatMap(c => c.consequent)), fn: false });
          for (const c of s.cases) { walkExpr(c.test, c); for (const st of c.consequent) { if (st.type !== 'FunctionDeclaration') add(st.start, mark(st)); walkStmt(st); } }
          scopes.pop();
          break;
        case 'TryStatement': {
          walkStmt(s.block);
          if (s.handler) { const ex = []; declNames(s.handler.param, ex); scopes.push({ names: ex, fn: false }); walkStmt(s.handler.body); scopes.pop(); }
          if (s.finalizer) walkStmt(s.finalizer);
          break;
        }
        case 'ThrowStatement': walkExpr(s.argument, s); break;
      }
    }
    function walkClass(c) {
      if (c.superClass) walkExpr(c.superClass, c);
      const cname = c.id ? c.id.name : 'class';
      for (const m of c.body.body) {
        if (m.type === 'MethodDefinition') { if (m.computed) walkExpr(m.key, m); walkFn(m.value, m, cname); }
        else if (m.type === 'PropertyDefinition' && m.value) walkExpr(m.value, m);
        else if (m.type === 'StaticBlock') stmtList(m.body);
      }
    }
    function walkExpr(e, parent) {
      if (!e || typeof e.type !== 'string') return;
      if (e.type === 'FunctionExpression' || e.type === 'ArrowFunctionExpression') { walkFn(e, parent); return; }
      if (e.type === 'ClassExpression') { walkClass(e); return; }
      for (const k in e) {
        if (k === 'loc' || k === 'start' || k === 'end' || k === 'type') continue;
        const c = e[k];
        if (Array.isArray(c)) c.forEach(x => x && walkExpr(x, e));
        else if (c && typeof c.type === 'string') walkExpr(c, e);
      }
    }
    const top = []; hoisted(ast, top);
    scopes.push({ names: top, fn: true });
    stmtList(ast.body);
    scopes.pop();
    /* apply the insertions from the end, so earlier offsets stay right */
    /* at one position, closing text comes first (inner before outer), then opening text (outer before inner) */
    const byPos = new Map();
    ins.forEach((x, idx) => { const l = byPos.get(x[0]) || []; l.push({ text: x[1], order: x[2], idx }); byPos.set(x[0], l); });
    const keys = [...byPos.keys()].sort((a, b) => b - a);
    let out = src;
    for (const pos of keys) {
      const l = byPos.get(pos);
      const closers = l.filter(x => x.order < 0).sort((a, b) => a.idx - b.idx);
      const openers = l.filter(x => x.order >= 0).sort((a, b) => b.order - a.order || a.idx - b.idx);
      out = out.slice(0, pos) + closers.concat(openers).map(x => x.text).join('') + out.slice(pos);
    }
    return { code: out };
  }
  function mapLine(l, map) { return map ? (map[l] || l) : l; }
  JT.instrument = instrument;

  /* ---------- 3. running ---------- */
  class Stop { constructor(why) { this.why = why; } }
  JT.run = function (code, opts) {
    opts = opts || {};
    const res = { out: [], trace: opts.trace ? [] : null, error: null, stopped: null, notes: [] };
    const maxSteps = opts.maxSteps || 3000, maxOps = opts.maxOps || 5e6;
    let outText = '', ops = 0, lastLine = 1;
    const write = (s, e) => { outText += s; const last = res.out[res.out.length - 1]; if (last && last.e === !!e) last.s += s; else res.out.push({ s, e: !!e }); };
    const frames = [{ fn: 'Main program', line: 1, get: null, names: [] }];
    const snapVars = f => {
      const vars = [];
      if (!f.get) return vars;
      f.names.forEach((n, i) => {
        let v, ok = true;
        try { v = f.get(i); } catch (e) { ok = false; }
        if (!ok) { vars.push([n, 'not set yet', 'tdz']); return; }
        if (typeof v === 'function' && /^class\s/.test(Function.prototype.toString.call(v))) return;
        if (typeof v === 'function' && !f.fn2) return;
        vars.push([n, short(v), '']);
      });
      return vars;
    };
    const G = typeof self !== 'undefined' ? self : globalThis;
    const api = {
      __t(line, get, names) {
        lastLine = line;
        if (++ops > maxOps) throw new Stop('The program ran for a very long time, so the playground stopped it. Check for a loop whose condition never becomes false');
        const f = frames[frames.length - 1];
        f.line = line; f.get = get; f.names = names || [];
        if (!res.trace) return;
        if (res.trace.length >= maxSteps) throw new Stop(`Step by step shows the first ${maxSteps} steps. Use Run all to run the whole program`);
        res.trace.push({ line, ev: f.pendingCall ? 'call' : 'line', out: outText.length, stack: frames.map(fr => ({ fn: fr.fn, line: fr.line, vars: snapVars(fr) })) });
        f.pendingCall = false;
      },
      __e(name, line) {
        if (frames.length > 2000) throw new RangeError('Maximum call stack size exceeded');
        frames.push({ fn: name + '()', line, get: null, names: [], pendingCall: true, fn2: true });
      },
      __x() { if (frames.length > 1) frames.pop(); },
      __r(v, line) {
        if (res.trace && res.trace.length < maxSteps) {
          const f = frames[frames.length - 1];
          res.trace.push({ line, ev: 'ret', out: outText.length, ret: short(v), stack: frames.map(fr => ({ fn: fr.fn, line: fr === f ? line : fr.line, vars: snapVars(fr) })) });
        }
        return v;
      }
    };
    /* console and input */
    let inPos = 0;
    const stdin = String(opts.stdin || '');
    const readLine = () => { if (inPos >= stdin.length) return null; let j = stdin.indexOf('\n', inPos); if (j < 0) j = stdin.length; const l = stdin.slice(inPos, j).replace(/\r$/, ''); inPos = j + 1; return l; };
    const groups = { n: 0 };
    const ind = () => '  '.repeat(groups.n);
    const con = {
      log: (...a) => write(ind() + format(a).split('\n').join('\n' + ind()) + '\n'),
      info: (...a) => con.log(...a),
      debug: (...a) => con.log(...a),
      warn: (...a) => write(ind() + format(a) + '\n', true),
      error: (...a) => write(ind() + format(a) + '\n', true),
      table: (d) => con.log(d),
      group: (...a) => { if (a.length) con.log(...a); groups.n++; },
      groupEnd: () => { groups.n = Math.max(0, groups.n - 1); },
      assert: (c, ...a) => { if (!c) write('Assertion failed' + (a.length ? ': ' + format(a) : '') + '\n', true); },
      count: (l = 'default') => { con._c = con._c || {}; con._c[l] = (con._c[l] || 0) + 1; con.log(l + ': ' + con._c[l]); },
      time: () => {}, timeEnd: (l = 'default') => con.log(l + ': 0.1ms'), clear: () => {}
    };
    const prompt = msg => { if (msg !== undefined) write(String(msg)); const l = readLine(); if (l === null) { res.notes.push('The program asked for input with prompt(), but the Input box had nothing left to read. Type the values in the Input box, one per line, and run again.'); return null; } return l; };
    /* timers, so setTimeout and promises still finish before the run ends */
    const timers = [];
    let timerId = 0, clock = 0;
    const setT = (fn, ms, ...a) => { const id = ++timerId; timers.push({ id, at: clock + Math.max(0, +ms || 0), fn, a, seq: id }); return id; };
    const setI = (fn, ms, ...a) => { const id = ++timerId; const t = { id, at: clock + Math.max(1, +ms || 1), fn, a, every: Math.max(1, +ms || 1), seq: id }; timers.push(t); return id; };
    const clearT = id => { const i = timers.findIndex(t => t.id === id); if (i >= 0) timers.splice(i, 1); };
    const fail = e => {
      if (e instanceof Stop) { res.stopped = e.why; return; }
      const name = e && e.name ? e.name : 'Error';
      const msg = e && e.message !== undefined ? e.message : String(e);
      const text = (e instanceof Error ? `Uncaught ${name}: ${msg}` : `Uncaught ${inspect(e)}`) + `\n    at line ${lastLine}`;
      write(text + '\n', true);
      res.error = { msg: text, line: lastLine };
      if (res.trace) res.trace.push({ line: lastLine, ev: 'error', out: outText.length, msg: text, stack: frames.map(fr => ({ fn: fr.fn, line: fr.line, vars: snapVars(fr) })) });
    };
    let fn;
    try {
      fn = new Function('__t', '__e', '__x', '__r', 'console', 'prompt', 'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval', 'require', 'process', code);
    } catch (e) { res.error = { msg: 'SyntaxError: ' + e.message, line: 1 }; write(res.error.msg + '\n', true); return Promise.resolve(res); }
    const req = m => { throw new Error(`require('${m}') is not available here. The playground runs plain JavaScript in your browser, without Node.js modules`); };
    const proc = { argv: [], env: {}, stdout: { write: s => { write(String(s)); return true; } }, exit: c => { throw new Stop(null); } };
    let unhandled = null;
    const onRej = ev => { unhandled = ev.reason; ev.preventDefault && ev.preventDefault(); };
    if (G.addEventListener) G.addEventListener('unhandledrejection', onRej);
    try {
      const r = fn(api.__t, api.__e, api.__x, api.__r, con, prompt, setT, setI, clearT, clearT, req, proc);
      if (r && typeof r.then === 'function') r.catch(e => { unhandled = e; });
    } catch (e) { fail(e); finishSteps(); return Promise.resolve(res); }
    /* let promises and timers run, in time order, without really waiting */
    return (async () => {
      let rounds = 0;
      for (;;) {
        for (let i = 0; i < 20; i++) await null;
        if (unhandled !== null) { fail(unhandled); break; }
        if (res.stopped || res.error) break;
        if (!timers.length) break;
        if (++rounds > 5000) { res.stopped = 'Timers kept running, so the playground stopped them. Check that setInterval has a clearInterval'; break; }
        timers.sort((a, b) => a.at - b.at || a.seq - b.seq);
        const t = timers.shift();
        clock = t.at;
        if (t.every) { t.at += t.every; t.seq = ++timerId; timers.push(t); }
        try { t.fn(...t.a); } catch (e) { fail(e); break; }
      }
      if (G.removeEventListener) G.removeEventListener('unhandledrejection', onRej);
      finishSteps();
      return res;
    })();
    function finishSteps() {
      if (res.trace) res.trace.push({ line: lastLine, ev: 'end', out: outText.length, stack: [] });
    }
  };
})();
