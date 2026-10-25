/* ===== Python chapters: animations that show what CPython does with your code =====
   <div class="viz" data-viz="pvm"></div>   type a few lines of Python and watch them become tokens, a syntax tree,
                                            bytecode, and finally run on the value stack one instruction at a time.

   PYVM is a small model of CPython 3.14 for a safe subset of the language: assignments, calls to a few built in
   functions, numbers, strings, names, + - * / // % ** and comparisons. Its tokens, ast.dump text, instruction
   names, arguments and printed output were compared with the real CPython 3.14 on thousands of generated
   programs (tools/py-build/check_pyvm.py). It leaves out the index of each LOAD_CONST in co_consts, which
   depends on compiler details that do not help a learner. One known gap: a power with a fractional exponent
   other than 0.5 can differ from CPython in its last digit, because browsers do not round pow() the same way. */
const PYVM = (() => {
  class PyErr extends Error {
    constructor(type, msg, line) { super(msg); this.type = type; this.line = line; }
  }
  class Limit extends Error {}

  /* ---------- values: ints are BigInt, floats are {f: number}, strings, booleans and None ---------- */
  const NONE = { none: true };
  const isInt = v => typeof v === 'bigint';
  const isFloat = v => v !== null && typeof v === 'object' && 'f' in v;
  const isBool = v => typeof v === 'boolean';
  const isStr = v => typeof v === 'string';
  const isNum = v => isInt(v) || isFloat(v) || isBool(v);
  const F = x => ({ f: x });
  function typeName(v) {
    if (isBool(v)) return 'bool';
    if (isInt(v)) return 'int';
    if (isFloat(v)) return 'float';
    if (isStr(v)) return 'str';
    if (v === NONE) return 'NoneType';
    if (v && v.fn) return 'builtin_function_or_method';
    return 'object';
  }
  function floatRepr(x) {
    if (Number.isNaN(x)) return 'nan';
    if (x === Infinity) return 'inf';
    if (x === -Infinity) return '-inf';
    if (x === 0) return Object.is(x, -0) ? '-0.0' : '0.0';
    // Shortest round trip digits, then Python's layout: plain between 1e-4 and 1e16, else scientific.
    const [mant, e] = x.toExponential().split('e');
    const exp = +e;
    const neg = mant[0] === '-';
    const digits = mant.replace('-', '').replace('.', '');
    let out;
    if (exp < -4 || exp >= 16) {
      out = digits[0] + (digits.length > 1 ? '.' + digits.slice(1) : '') + 'e' + (exp < 0 ? '-' : '+') + String(Math.abs(exp)).padStart(2, '0');
    } else if (exp < 0) {
      out = '0.' + '0'.repeat(-exp - 1) + digits;
    } else if (digits.length <= exp + 1) {
      out = digits + '0'.repeat(exp + 1 - digits.length) + '.0';
    } else {
      out = digits.slice(0, exp + 1) + '.' + digits.slice(exp + 1);
    }
    return (neg ? '-' : '') + out;
  }
  function strRepr(s) {
    const q = s.includes("'") && !s.includes('"') ? '"' : "'";
    let o = '';
    for (const ch of s) {
      if (ch === '\\') o += '\\\\';
      else if (ch === q) o += '\\' + q;
      else if (ch === '\n') o += '\\n';
      else if (ch === '\t') o += '\\t';
      else if (ch === '\r') o += '\\r';
      else if (ch < ' ' || ch === '\x7f') o += '\\x' + ch.charCodeAt(0).toString(16).padStart(2, '0');
      else o += ch;
    }
    return q + o + q;
  }
  function repr(v) {
    if (isBool(v)) return v ? 'True' : 'False';
    if (isInt(v)) return v.toString();
    if (isFloat(v)) return floatRepr(v.f);
    if (isStr(v)) return strRepr(v);
    if (v === NONE) return 'None';
    if (v && v.fn) return '<built-in function ' + v.fn + '>';
    return String(v);
  }
  const str = v => (isStr(v) ? v : repr(v));
  const toF = v => (isFloat(v) ? v.f : Number(isBool(v) ? (v ? 1 : 0) : v));
  const toI = v => (isBool(v) ? (v ? 1n : 0n) : v);
  const bits = n => (n < 0n ? -n : n).toString(2).length - ((n === 0n) ? 1 : 0);

  /* ---------- tokenizer: the same token types Python's tokenize module prints ---------- */
  const OPS = ['**', '//', '==', '!=', '<=', '>=', '+', '-', '*', '/', '%', '<', '>', '(', ')', ',', '='];
  function tokenize(src) {
    const toks = [];
    const lines = src.replace(/\r\n?/g, '\n').split('\n');
    let sawCode = false;
    lines.forEach((text, li) => {
      const line = li + 1;
      if (/^[ \t]+\S/.test(text) && !/^[ \t]+#/.test(text)) throw new PyErr('IndentationError', 'unexpected indent', line);
      let i = 0;
      const lineToks = [];
      while (i < text.length) {
        const c = text[i];
        if (c === ' ' || c === '\t') { i++; continue; }
        if (c === '#') { lineToks.push({ type: 'COMMENT', text: text.slice(i), line, col: i }); break; }
        let m;
        const rest = text.slice(i);
        if ((m = /^[A-Za-z_][A-Za-z0-9_]*/.exec(rest))) { lineToks.push({ type: 'NAME', text: m[0], line, col: i }); i += m[0].length; continue; }
        if ((m = /^(?:\d(?:_?\d)*(?:\.(?:\d(?:_?\d)*)?)?|\.\d(?:_?\d)*)(?:[eE][+-]?\d(?:_?\d)*)?/.exec(rest))) {
          if (/^[A-Za-z_]/.test(rest.slice(m[0].length))) throw new PyErr('SyntaxError', 'invalid decimal literal', line);
          lineToks.push({ type: 'NUMBER', text: m[0], line, col: i }); i += m[0].length; continue;
        }
        if (c === '"' || c === "'") {
          let j = i + 1, val = '';
          while (j < text.length && text[j] !== c) {
            if (text[j] === '\\' && j + 1 < text.length) {
              const e = text[j + 1];
              val += { n: '\n', t: '\t', '\\': '\\', "'": "'", '"': '"', r: '\r' }[e] ?? ('\\' + e);
              j += 2;
            } else { val += text[j]; j++; }
          }
          if (j >= text.length) throw new PyErr('SyntaxError', 'unterminated string literal (detected at line ' + line + ')', line);
          lineToks.push({ type: 'STRING', text: text.slice(i, j + 1), value: val, line, col: i }); i = j + 1; continue;
        }
        const op = OPS.find(o => rest.startsWith(o));
        if (op) { lineToks.push({ type: 'OP', text: op, line, col: i }); i += op.length; continue; }
        throw new PyErr('SyntaxError', 'invalid character ' + strRepr(c) + ' (U+' + c.codePointAt(0).toString(16).toUpperCase().padStart(4, '0') + ')', line);
      }
      const code = lineToks.filter(t => t.type !== 'COMMENT');
      toks.push(...lineToks);
      if (code.length) { toks.push({ type: 'NEWLINE', text: '', line, col: text.length }); sawCode = true; }
      else if (li < lines.length - 1 || text.length) toks.push({ type: 'NL', text: '', line, col: text.length });
    });
    if (!sawCode) throw new PyErr('Demo', 'Type at least one line of code.', 1);
    toks.push({ type: 'ENDMARKER', text: '', line: lines.length + 1, col: 0 });
    return toks;
  }

  /* ---------- parser: builds the same tree ast.parse builds for this subset ---------- */
  const BIN = { '+': 'Add', '-': 'Sub', '*': 'Mult', '/': 'Div', '//': 'FloorDiv', '%': 'Mod', '**': 'Pow' };
  const CMP = { '<': 'Lt', '<=': 'LtE', '==': 'Eq', '!=': 'NotEq', '>': 'Gt', '>=': 'GtE' };
  const KW = new Set('False None True and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield'.split(' '));
  function parse(src) {
    const all = tokenize(src);
    const toks = all.filter(t => t.type !== 'COMMENT' && t.type !== 'NL');
    let p = 0;
    const peek = () => toks[p];
    const next = () => toks[p++];
    const isOp = (t, o) => t.type === 'OP' && t.text === o;
    const fail = (t, msg) => { throw new PyErr('SyntaxError', msg || 'invalid syntax', t.line); };
    const demo = (t, msg) => { throw new PyErr('Demo', msg, t.line); };
    function expect(o) { const t = next(); if (!isOp(t, o)) fail(t, o === ')' ? "'(' was never closed" : 'invalid syntax'); return t; }
    function atom() {
      const t = next();
      if (t.type === 'NUMBER') {
        const raw = t.text.replace(/_/g, '');
        if (/[.eE]/.test(raw)) return { k: 'Constant', value: F(Number(raw)), line: t.line };
        if (/^0\d/.test(raw) && /[1-9]/.test(raw)) fail(t, 'leading zeros in decimal integer literals are not permitted; use an 0o prefix for octal integers');
        return { k: 'Constant', value: BigInt(raw), line: t.line };
      }
      if (t.type === 'STRING') {
        let v = t.value;
        while (peek().type === 'STRING') v += next().value;   // "a" "b" is one constant
        return { k: 'Constant', value: v, line: t.line };
      }
      if (t.type === 'NAME') {
        if (t.text === 'True' || t.text === 'False') return { k: 'Constant', value: t.text === 'True', line: t.line };
        if (t.text === 'None') return { k: 'Constant', value: NONE, line: t.line };
        if (KW.has(t.text)) demo(t, 'The keyword "' + t.text + '" is not part of this small demo. Try it in the editor of any example instead.');
        return { k: 'Name', id: t.text, line: t.line };
      }
      if (isOp(t, '(')) {
        if (isOp(peek(), ')')) demo(t, 'Tuples are not part of this small demo.');
        const e = expr();
        if (isOp(peek(), ',')) demo(t, 'Tuples are not part of this small demo.');
        expect(')');
        return e;
      }
      if (t.type === 'NEWLINE' || t.type === 'ENDMARKER') fail(t, 'invalid syntax');
      fail(t);
    }
    function primary() {
      let e = atom();
      while (isOp(peek(), '(')) {
        next();
        const args = [];
        while (!isOp(peek(), ')')) {
          if (peek().type === 'NEWLINE' || peek().type === 'ENDMARKER') fail(peek(), "'(' was never closed");
          if (peek().type === 'NAME' && isOp(toks[p + 1], '=')) demo(peek(), 'Keyword arguments are not part of this small demo.');
          args.push(expr());
          if (isOp(peek(), ',')) next(); else if (!isOp(peek(), ')')) fail(peek(), 'invalid syntax. Perhaps you forgot a comma?');
        }
        next();
        e = { k: 'Call', func: e, args, line: e.line };
      }
      return e;
    }
    function power() {
      const base = primary();
      if (isOp(peek(), '**')) { next(); return { k: 'BinOp', left: base, op: '**', right: unary(), line: base.line }; }
      return base;
    }
    function unary() {
      const t = peek();
      if (isOp(t, '-')) { next(); return { k: 'UnaryOp', op: '-', operand: unary(), line: t.line }; }
      if (isOp(t, '+')) demo(t, 'Unary plus is not part of this small demo. Use minus, or leave the sign out.');
      return power();
    }
    function term() {
      let e = unary();
      while (peek().type === 'OP' && ['*', '/', '//', '%'].includes(peek().text)) { const o = next().text; e = { k: 'BinOp', left: e, op: o, right: unary(), line: e.line }; }
      return e;
    }
    function arith() {
      let e = term();
      while (peek().type === 'OP' && (peek().text === '+' || peek().text === '-')) { const o = next().text; e = { k: 'BinOp', left: e, op: o, right: term(), line: e.line }; }
      return e;
    }
    function expr() {
      const e = arith();
      if (peek().type === 'OP' && CMP[peek().text]) {
        const o = next().text;
        const r = arith();
        if (peek().type === 'OP' && CMP[peek().text]) demo(peek(), 'Chained comparisons such as 1 < x < 5 are not part of this small demo.');
        return { k: 'Compare', left: e, op: o, right: r, line: e.line };
      }
      return e;
    }
    const body = [];
    while (peek().type !== 'ENDMARKER') {
      const t = peek();
      if (t.type === 'NAME' && isOp(toks[p + 1], '=')) {
        if (KW.has(t.text) || ['True', 'False', 'None'].includes(t.text)) fail(t, 'cannot assign to ' + t.text);
        next(); next();
        if (peek().type === 'NAME' && isOp(toks[p + 1], '=')) demo(peek(), 'Chained assignment such as a = b = 1 is not part of this small demo.');
        const value = expr();
        body.push({ k: 'Assign', target: t.text, value, line: t.line });
      } else {
        const value = expr();
        if (value.k !== 'Call') demo(t, 'Start each line with a name and =, or call a function such as print(...).');
        body.push({ k: 'Expr', value, line: t.line });
      }
      const end = next();
      if (end.type !== 'NEWLINE') {
        if (isOp(end, '=')) fail(end, "cannot assign to expression here. Maybe you meant '==' instead of '='?");
        if (isOp(end, ')')) fail(end, "unmatched ')'");
        fail(end, 'invalid syntax');
      }
    }
    if (body.length > 12) throw new PyErr('Demo', 'Keep it to 12 lines or fewer so every step stays readable.', 13);
    return { tokens: all, tree: body };
  }

  /* ---------- ast.dump, exactly as CPython 3.14 prints it ---------- */
  function dumpNode(n) {
    switch (n.k) {
      case 'Constant': return 'Constant(value=' + repr(n.value) + ')';
      case 'Name': return "Name(id='" + n.id + "', ctx=Load())";
      case 'BinOp': return 'BinOp(left=' + dumpNode(n.left) + ', op=' + BIN[n.op] + '(), right=' + dumpNode(n.right) + ')';
      case 'UnaryOp': return 'UnaryOp(op=USub(), operand=' + dumpNode(n.operand) + ')';
      case 'Compare': return 'Compare(left=' + dumpNode(n.left) + ', ops=[' + CMP[n.op] + '()], comparators=[' + dumpNode(n.right) + '])';
      case 'Call': return 'Call(func=' + dumpNode(n.func) + (n.args.length ? ', args=[' + n.args.map(dumpNode).join(', ') + ']' : '') + ')';
      case 'Assign': return "Assign(targets=[Name(id='" + n.target + "', ctx=Store())], value=" + dumpNode(n.value) + ')';
      case 'Expr': return 'Expr(value=' + dumpNode(n.value) + ')';
    }
    return '?';
  }
  const dump = tree => 'Module(body=[' + tree.map(dumpNode).join(', ') + '])';

  /* ---------- arithmetic with Python's rules ---------- */
  function floorDiv(a, b) { const q = a / b; return (a % b !== 0n && ((a < 0n) !== (b < 0n))) ? q - 1n : q; }
  function mod(a, b) { const r = a % b; return (r !== 0n && ((r < 0n) !== (b < 0n))) ? r + b : r; }
  // x ** n for a whole number n, rounded once like C's pow: the exact power is built with BigInt, then rounded.
  function exactPow(x, n) {
    if (!Number.isFinite(x) || x === 0 || Math.abs(n) > 64) return Math.pow(x, n);
    const dv = new DataView(new ArrayBuffer(8));
    dv.setFloat64(0, Math.abs(x));
    const hi = dv.getUint32(0), lo = dv.getUint32(4);
    const be = (hi >>> 20) & 0x7ff;
    let m = (BigInt(hi & 0xfffff) << 32n) | BigInt(lo), e = be - 1075;
    if (be) m |= 1n << 52n; else e = -1074;
    const mn = m ** BigInt(Math.abs(n)), en = e * Math.abs(n);
    let num = mn, den = 1n, k = en;
    if (n < 0) { num = 1n; den = mn; k = -en; }
    const r = roundRatio(num, den, k);
    return x < 0 && n % 2 ? -r : r;
  }
  const blen = v => v.toString(2).length;
  // int / int is rounded once from the exact quotient, so huge integers divide correctly.
  function intDiv(x, y) {
    if (x === 0n) return (y < 0n) ? -0 : 0;
    const neg = (x < 0n) !== (y < 0n);
    const r = roundRatio(x < 0n ? -x : x, y < 0n ? -y : y, 0);
    return neg ? -r : r;
  }
  function roundRatio(num, den, k) {
    // num / den * 2**k, rounded half to even to 53 bits
    const shift = 55 - (blen(num) - blen(den));
    const a = shift >= 0 ? num << BigInt(shift) : num, d = shift >= 0 ? den : den << BigInt(-shift);
    let q = a / d;
    const sticky = a % d !== 0n;
    let drop = blen(q) - 53;
    let exp2 = k - shift;
    // keep subnormal results on the right grid
    const lowest = -1074 - exp2;
    if (drop < lowest) drop = lowest;
    if (drop > 0) {
      const D = BigInt(drop), half = 1n << (D - 1n), rem = q & ((1n << D) - 1n);
      q >>= D;
      if (rem > half || (rem === half && (sticky || (q & 1n)))) q += 1n;
      exp2 += drop;
    }
    let v = Number(q);
    while (exp2 > 0) { const s = Math.min(exp2, 1000); v *= 2 ** s; exp2 -= s; }
    while (exp2 < 0) { const s = Math.min(-exp2, 1000); v /= 2 ** s; exp2 += s; }
    return v;
  }
  // CPython's float floor division: built from fmod so that it agrees with % exactly.
  function floatFloorDiv(vx, wx) {
    let mod = vx % wx, div = (vx - mod) / wx;
    if (mod && ((wx < 0) !== (mod < 0))) div -= 1;
    if (div) { let fd = Math.floor(div); if (div - fd > 0.5) fd += 1; return fd; }
    return (vx / wx < 0 || Object.is(vx / wx, -0)) ? -0 : 0;
  }
  function fmod(a, b) { const r = a % b; return (r !== 0 && ((r < 0) !== (b < 0))) ? r + b : (r === 0 ? (b < 0 ? -0 : 0) : r); }
  function binop(op, a, b) {
    const ta = typeName(a), tb = typeName(b);
    if (isNum(a) && isNum(b)) {
      const fl = isFloat(a) || isFloat(b);
      if (!fl) {
        const x = toI(a), y = toI(b);
        switch (op) {
          case '+': return x + y;
          case '-': return x - y;
          case '*': return x * y;
          case '/': if (y === 0n) throw new PyErr('ZeroDivisionError', 'division by zero'); return F(intDiv(x, y));
          case '//': if (y === 0n) throw new PyErr('ZeroDivisionError', 'division by zero'); return floorDiv(x, y);
          case '%': if (y === 0n) throw new PyErr('ZeroDivisionError', 'division by zero'); return mod(x, y);
          case '**':
            if (y < 0n) { if (x === 0n) throw new PyErr('ZeroDivisionError', 'zero to a negative power'); return F(exactPow(Number(x), Number(y))); }
            if (y > 10000n || bits(x) * Number(y) > 4000) throw new Limit('That power is too big for this small demo.');
            return x ** y;
        }
      }
      const x = toF(a), y = toF(b);
      let r;
      switch (op) {
        case '+': r = x + y; break;
        case '-': r = x - y; break;
        case '*': r = x * y; break;
        case '/': if (y === 0) throw new PyErr('ZeroDivisionError', 'division by zero'); r = x / y; break;
        case '//': if (y === 0) throw new PyErr('ZeroDivisionError', 'division by zero'); r = floatFloorDiv(x, y); break;
        case '%': if (y === 0) throw new PyErr('ZeroDivisionError', 'division by zero'); r = fmod(x, y); break;
        case '**':
          if (x === 0 && y < 0) throw new PyErr('ZeroDivisionError', 'zero to a negative power');
          if (x < 0 && !Number.isInteger(y)) throw new Limit('A negative number to a fractional power gives a complex number, which this small demo does not show.');
          r = Number.isInteger(y) ? exactPow(x, y) : y === 0.5 ? Math.sqrt(x) : Math.pow(x, y);
          if (!Number.isFinite(r) && Number.isFinite(x) && Number.isFinite(y)) throw new PyErr('OverflowError', "(34, 'Numerical result out of range')");
          break;
      }
      if (!Number.isFinite(r) && Number.isFinite(x) && Number.isFinite(y) && op !== '**') {
        if (op === '+' || op === '-' || op === '*') return F(r);
      }
      return F(r);
    }
    if (op === '+' && isStr(a) && isStr(b)) return lim(a + b);
    if (op === '*' && ((isStr(a) && (isInt(b) || isBool(b))) || (isStr(b) && (isInt(a) || isBool(a))))) {
      const s = isStr(a) ? a : b, n = Number(toI(isStr(a) ? b : a));
      if (n * s.length > 100000) throw new Limit('That string is too long for this small demo.');
      return n > 0 ? s.repeat(n) : '';
    }
    if (op === '*' && (isStr(a) || isStr(b))) throw new PyErr('TypeError', "can't multiply sequence by non-int of type '" + (isStr(a) ? tb : ta) + "'");
    if (op === '+' && isStr(a)) throw new PyErr('TypeError', 'can only concatenate str (not "' + tb + '") to str');
    if (op === '%' && isStr(a)) throw new Limit('The % operator on strings formats text. It is not part of this small demo.');
    throw new PyErr('TypeError', 'unsupported operand type(s) for ' + (op === '**' ? '** or pow()' : op) + ": '" + ta + "' and '" + tb + "'");
  }
  function lim(s) { if (s.length > 100000) throw new Limit('That string is too long for this small demo.'); return s; }
  function compare(op, a, b) {
    if (isNum(a) && isNum(b)) {
      if (isFloat(a) || isFloat(b)) {
        const x = toF(a), y = toF(b);
        return { '<': x < y, '<=': x <= y, '==': x === y, '!=': x !== y, '>': x > y, '>=': x >= y }[op];
      }
      const x = toI(a), y = toI(b);
      return { '<': x < y, '<=': x <= y, '==': x === y, '!=': x !== y, '>': x > y, '>=': x >= y }[op];
    }
    if (isStr(a) && isStr(b)) return { '<': a < b, '<=': a <= b, '==': a === b, '!=': a !== b, '>': a > b, '>=': a >= b }[op];
    if (op === '==') return a === b;
    if (op === '!=') return a !== b;
    throw new PyErr('TypeError', "'" + op + "' not supported between instances of '" + typeName(a) + "' and '" + typeName(b) + "'");
  }
  function negate(v) {
    if (isBool(v)) return v ? -1n : 0n;
    if (isInt(v)) return -v;
    if (isFloat(v)) return F(-v.f);
    throw new PyErr('TypeError', "bad operand type for unary -: '" + typeName(v) + "'");
  }

  /* ---------- the built in functions the demo knows ---------- */
  function cmpMax(sign, args, name) {
    if (!args.length) throw new PyErr('TypeError', name + ' expected at least 1 argument, got 0');
    if (args.length === 1) {
      if (isStr(args[0])) {
        if (!args[0].length) throw new PyErr('ValueError', name + '() iterable argument is empty');
        return [...args[0]].reduce((m, c) => (sign > 0 ? (c > m ? c : m) : (c < m ? c : m)));
      }
      throw new PyErr('TypeError', "'" + typeName(args[0]) + "' object is not iterable");
    }
    let best = args[0];
    for (const v of args.slice(1)) if (compare(sign > 0 ? '>' : '<', v, best)) best = v;
    return best;
  }
  function callBuiltin(name, args, out) {
    const one = () => { if (args.length !== 1) throw new PyErr('TypeError', name + '() takes exactly one argument (' + args.length + ' given)'); return args[0]; };
    switch (name) {
      case 'print': out.push(args.map(str).join(' ')); return NONE;
      case 'abs': { const v = one(); if (isBool(v)) return v ? 1n : 0n; if (isInt(v)) return v < 0n ? -v : v; if (isFloat(v)) return F(Math.abs(v.f)); throw new PyErr('TypeError', "bad operand type for abs(): '" + typeName(v) + "'"); }
      case 'len': { const v = one(); if (isStr(v)) return BigInt([...v].length); throw new PyErr('TypeError', "object of type '" + typeName(v) + "' has no len()"); }
      case 'max': return cmpMax(1, args, 'max');
      case 'min': return cmpMax(-1, args, 'min');
      case 'str': if (!args.length) return ''; return str(one());
      case 'int': {
        if (!args.length) return 0n;
        const v = one();
        if (isBool(v)) return v ? 1n : 0n;
        if (isInt(v)) return v;
        if (isFloat(v)) { if (!Number.isFinite(v.f)) throw new PyErr(Number.isNaN(v.f) ? 'ValueError' : 'OverflowError', Number.isNaN(v.f) ? 'cannot convert float NaN to integer' : 'cannot convert float infinity to integer'); return BigInt(Math.trunc(v.f)); }
        if (isStr(v)) { const s = v.trim().replace(/_/g, ''); if (/^[+-]?\d+$/.test(s) && !/__/.test(v)) return BigInt(s); throw new PyErr('ValueError', "invalid literal for int() with base 10: " + strRepr(v)); }
        throw new PyErr('TypeError', "int() argument must be a string, a bytes-like object or a real number, not '" + typeName(v) + "'");
      }
      case 'float': {
        if (!args.length) return F(0);
        const v = one();
        if (isNum(v)) return F(toF(v));
        if (isStr(v)) { const s = v.trim(); if (/^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/.test(s)) return F(Number(s)); throw new PyErr('ValueError', 'could not convert string to float: ' + strRepr(v)); }
        throw new PyErr('TypeError', "float() argument must be a string or a real number, not '" + typeName(v) + "'");
      }
      case 'round': {
        const v = one();
        if (isInt(v) || isBool(v)) return toI(v);
        if (isFloat(v)) {
          if (!Number.isFinite(v.f)) throw new PyErr(Number.isNaN(v.f) ? 'ValueError' : 'OverflowError', Number.isNaN(v.f) ? 'cannot convert float NaN to integer' : 'cannot convert float infinity to integer');
          const fl = Math.floor(v.f), d = v.f - fl;
          const r = d > 0.5 ? fl + 1 : d < 0.5 ? fl : (fl % 2 === 0 ? fl : fl + 1);   // ties go to the even neighbour
          return BigInt(r);
        }
        throw new PyErr('TypeError', "type " + typeName(v) + " doesn't define __round__ method");
      }
    }
    throw new PyErr('TypeError', "'" + typeName(name) + "' object is not callable");
  }
  const BUILTINS = new Set(['print', 'abs', 'len', 'max', 'min', 'str', 'int', 'float', 'round']);

  /* ---------- compiler: AST to the instructions dis.dis prints ---------- */
  const BIN_ARG = { '+': 0, '//': 2, '*': 5, '%': 6, '**': 8, '-': 10, '/': 11 };
  const CMP_ARG = { '<': 2, '<=': 42, '==': 72, '!=': 103, '>': 132, '>=': 172 };
  // Constant folding, with the same size limits CPython uses so that folding never builds a huge object.
  function fold(op, a, b) {
    if (isStr(a) || isStr(b)) {
      if (op === '+' && isStr(a) && isStr(b)) return (a.length + b.length <= 4096) ? { v: a + b } : null;
      if (op === '*' && isStr(a) && (isInt(b) || isBool(b))) { const n = Number(toI(b)); return (n >= 0 && n * a.length <= 4096) ? { v: a.repeat(n) } : null; }
      if (op === '*' && isStr(b) && (isInt(a) || isBool(a))) { const n = Number(toI(a)); return (n >= 0 && n * b.length <= 4096) ? { v: b.repeat(n) } : null; }
      return null;
    }
    if (a === NONE || b === NONE) return null;
    if (isInt(a) && isInt(b) || isBool(a) || isBool(b)) {
      if (!isFloat(a) && !isFloat(b)) {
        const x = toI(a), y = toI(b);
        if (op === '**' && y >= 0n && x !== 0n && x !== 1n && x !== -1n && bits(x) * Number(y) > 128) return null;
        if (op === '*' && x !== 0n && y !== 0n && bits(x) + bits(y) > 128) return null;
      }
    }
    try { return { v: binop(op, a, b) }; } catch (e) {
      // CPython folds this into a complex number constant, which the demo cannot show.
      if (e instanceof Limit && /complex/.test(e.message)) throw new PyErr('Demo', e.message);
      return null;
    }
  }
  function foldNode(n) {
    if (n.k === 'BinOp') {
      const l = foldNode(n.left), r = foldNode(n.right);
      if (l.k === 'Constant' && r.k === 'Constant') { const f = fold(n.op, l.value, r.value); if (f) return { k: 'Constant', value: f.v, line: n.line }; }
      return { ...n, left: l, right: r };
    }
    if (n.k === 'UnaryOp') {
      const o = foldNode(n.operand);
      if (o.k === 'Constant' && isNum(o.value)) return { k: 'Constant', value: negate(o.value), line: n.line };
      return { ...n, operand: o };
    }
    if (n.k === 'Compare') return { ...n, left: foldNode(n.left), right: foldNode(n.right) };
    if (n.k === 'Call') return { ...n, func: foldNode(n.func), args: n.args.map(foldNode) };
    return n;
  }
  function compile(tree) {
    const names = [];
    const nameIx = s => { let i = names.indexOf(s); if (i < 0) { names.push(s); i = names.length - 1; } return i; };
    const code = [{ op: 'RESUME', arg: 0, rep: '', line: 0 }];
    let line = 0;
    const emit = (op, arg, rep, extra) => code.push({ op, arg, rep: rep ?? '', line, ...extra });
    function loadConst(v) {
      if (isInt(v) && v >= 0n && v <= 255n) emit('LOAD_SMALL_INT', Number(v), '', { v });
      else emit('LOAD_CONST', null, repr(v), { v });
    }
    function ex(n) {
      switch (n.k) {
        case 'Constant': loadConst(n.value); break;
        case 'Name': emit('LOAD_NAME', nameIx(n.id), n.id); break;
        case 'BinOp': ex(n.left); ex(n.right); emit('BINARY_OP', BIN_ARG[n.op], n.op); break;
        case 'UnaryOp': ex(n.operand); emit('UNARY_NEGATIVE', null, ''); break;
        case 'Compare': ex(n.left); ex(n.right); emit('COMPARE_OP', CMP_ARG[n.op], n.op); break;
        case 'Call': ex(n.func); emit('PUSH_NULL', null, ''); n.args.forEach(ex); emit('CALL', n.args.length, ''); break;
      }
    }
    tree.forEach(st => {
      line = st.line;
      const v = foldNode(st.value);
      ex(v);
      if (st.k === 'Assign') emit('STORE_NAME', nameIx(st.target), st.target);
      else emit('POP_TOP', null, '');
    });
    emit('LOAD_CONST', null, 'None', { v: NONE });
    emit('RETURN_VALUE', null, '');
    let last = -1;
    code.forEach(c => { c.starts = c.line !== last; last = c.line; });
    return { code, names };
  }
  // The listing in the same layout as dis.dis, except that LOAD_CONST shows its value without the co_consts index.
  function disText(code) {
    return code.map((c, i) => {
      const ln = c.starts ? String(c.line).padStart(3) : '   ';
      const hasArg = c.arg !== null && c.arg !== undefined;
      let s = ln + '           ' + (hasArg || c.rep ? c.op.padEnd(20) + ' ' + (hasArg ? String(c.arg) : '').padStart(5) : c.op);
      if (c.rep) s += ' (' + c.rep + ')';
      return (c.starts && i > 0 ? '\n' : '') + s;
    }).join('\n');
  }

  /* ---------- the evaluation loop, recorded one instruction at a time ---------- */
  function run(code, maxSteps = 400) {
    const stack = [], names = {}, out = [], frames = [];
    const snap = (pc, note) => frames.push({ pc, stack: stack.map(v => ({ ...v })), names: Object.fromEntries(Object.entries(names).map(([k, v]) => [k, repr(v)])), out: out.slice(), note });
    const box = v => ({ r: repr(v), t: v === null ? 'NULL' : typeName(v) });
    const vals = [];
    let error = null;
    snap(-1, 'The frame is ready: an empty value stack and an empty namespace.');
    for (let pc = 0; pc < code.length; pc++) {
      if (frames.length > maxSteps) { error = { type: 'Demo', msg: 'Stopped after ' + maxSteps + ' steps.' }; break; }
      const c = code[pc];
      let note = '';
      try {
        switch (c.op) {
          case 'RESUME': note = 'RESUME marks the start of the code object. It is where Python checks for things such as a pending signal before running.'; break;
          case 'LOAD_SMALL_INT': vals.push(c.v); stack.push(box(c.v)); note = 'Push the small integer ' + c.arg + '. Integers from 0 to 255 have their own instruction, so no lookup is needed.'; break;
          case 'LOAD_CONST': vals.push(c.v); stack.push(box(c.v)); note = 'Push the constant ' + c.rep + ' from the code object\'s co_consts tuple.'; break;
          case 'LOAD_NAME': {
            const n = c.rep;
            if (n in names) { vals.push(names[n]); stack.push(box(names[n])); note = 'Look up ' + n + ' in the local namespace (here the module globals) and push its value ' + repr(names[n]) + '.'; }
            else if (BUILTINS.has(n)) { const f = { fn: n }; vals.push(f); stack.push({ r: n, t: 'builtin' }); note = n + ' is not a global, so Python looks it up in builtins and pushes the built in function.'; }
            else throw new PyErr('NameError', "name '" + n + "' is not defined");
            break;
          }
          case 'STORE_NAME': { const v = vals.pop(); stack.pop(); names[c.rep] = v; note = 'Pop the top value and bind the name ' + c.rep + ' to it. A name is only a label that points at an object.'; break; }
          case 'BINARY_OP': {
            const b = vals.pop(), a = vals.pop(); stack.pop(); stack.pop();
            const r = binop(c.rep, a, b); vals.push(r); stack.push(box(r));
            note = 'Pop two values, compute ' + repr(a) + ' ' + c.rep + ' ' + repr(b) + ' = ' + repr(r) + ', and push the result.';
            break;
          }
          case 'COMPARE_OP': {
            const b = vals.pop(), a = vals.pop(); stack.pop(); stack.pop();
            const r = compare(c.rep, a, b); vals.push(r); stack.push(box(r));
            note = 'Pop two values, compare ' + repr(a) + ' ' + c.rep + ' ' + repr(b) + ', and push ' + repr(r) + '.';
            break;
          }
          case 'UNARY_NEGATIVE': { const a = vals.pop(); stack.pop(); const r = negate(a); vals.push(r); stack.push(box(r)); note = 'Pop ' + repr(a) + ', push its negative ' + repr(r) + '.'; break; }
          case 'PUSH_NULL': vals.push(null); stack.push({ r: 'NULL', t: 'NULL' }); note = 'Push a NULL marker. CALL uses this slot for self when it calls a method, and leaves it empty for a plain function.'; break;
          case 'CALL': {
            const n = c.arg, args = vals.splice(vals.length - n, n);
            vals.pop(); const f = vals.pop();
            stack.splice(stack.length - n - 2, n + 2);
            if (!f || !f.fn) throw new PyErr('TypeError', "'" + typeName(f) + "' object is not callable");
            const r = callBuiltin(f.fn, args, out);
            vals.push(r); stack.push(box(r));
            note = 'Call ' + f.fn + '() with ' + n + ' argument' + (n === 1 ? '' : 's') + '. The function, the NULL and the arguments are popped and the return value ' + repr(r) + ' is pushed.' + (f.fn === 'print' ? ' print writes the text and returns None.' : '');
            break;
          }
          case 'POP_TOP': vals.pop(); stack.pop(); note = 'The result of this line is not stored anywhere, so pop it and throw it away.'; break;
          case 'RETURN_VALUE': vals.pop(); stack.pop(); note = 'Return None. The module code is finished and the frame is thrown away.'; break;
        }
      } catch (e) {
        if (e instanceof PyErr) { error = { type: e.type, msg: e.message, line: c.line }; snap(pc, 'This instruction raised ' + e.type + ': ' + e.message + '. Nothing catches it, so Python stops and prints a traceback.'); break; }
        if (e instanceof Limit) { error = { type: 'Demo', msg: e.message, line: c.line }; snap(pc, e.message); break; }
        throw e;
      }
      snap(pc, note);
    }
    return { frames, error, out };
  }

  // One call does everything the widget shows.
  function analyse(src) {
    let parsed;
    try { parsed = parse(src); } catch (e) {
      if (e instanceof PyErr) return { stage: e.type === 'Demo' ? 'demo' : 'parse', error: { type: e.type, msg: e.message, line: e.line } };
      throw e;
    }
    let comp;
    try { comp = compile(parsed.tree); } catch (e) {
      if (e instanceof PyErr) return { stage: 'demo', error: { type: e.type, msg: e.message, line: 1 } };
      throw e;
    }
    return { tokens: parsed.tokens, tree: parsed.tree, dump: dump(parsed.tree), ...comp, exec: run(comp.code) };
  }

  return { tokenize, parse, dump, compile, run, analyse, repr, str, disText, PyErr };
})();
if (typeof module !== 'undefined') module.exports = PYVM;

/* ---------- the widget ---------- */
if (typeof VIZ !== 'undefined') (() => {
  const K = VIZ.kit, W = VIZ.widgets, esc = K.esc, $ = K.$;
  const EXAMPLES = [
    ['Shopping bill', 'price = 40\nqty = 3\ntotal = price * qty + 5\nprint("Total:", total)'],
    ['Folding', 'seconds = 60 * 60 * 24\nprint(seconds)'],
    ['Mixed types', 'marks = 47\nout_of = 50\npercent = marks / out_of * 100\nprint(percent, percent >= 90)'],
    ['NameError', 'speed = 60\nprint(distance / speed)'],
    ['Built ins', 'name = "Asha"\nprint(len(name), max(3, 9, 4), round(2.5))']
  ];
  const TYPE_TIPS = { NAME: 'a name or a keyword', NUMBER: 'a number', STRING: 'a string', OP: 'an operator or punctuation', NEWLINE: 'the end of a logical line', NL: 'a blank line', COMMENT: 'a comment', ENDMARKER: 'the end of the file' };
  function treeHtml(n) {
    const kids = [];
    let label = n.k, sub = '';
    switch (n.k) {
      case 'Assign': sub = n.target + ' ='; kids.push(n.value); break;
      case 'Expr': sub = 'expression statement'; kids.push(n.value); break;
      case 'Constant': sub = PYVM.repr(n.value); break;
      case 'Name': sub = n.id; break;
      case 'BinOp': sub = n.op; kids.push(n.left, n.right); break;
      case 'UnaryOp': sub = '-'; kids.push(n.operand); break;
      case 'Compare': sub = n.op; kids.push(n.left, n.right); break;
      case 'Call': sub = 'call'; kids.push(n.func, ...n.args); break;
    }
    return `<li><span class="pv-node k-${n.k}"><b>${esc(label)}</b>${sub ? `<code>${esc(sub)}</code>` : ''}</span>${kids.length ? `<ul>${kids.map(treeHtml).join('')}</ul>` : ''}</li>`;
  }
  W.pvm = el => {
    const b = K.shell(el, 'Watch CPython run your code', 'Type a few lines (names, numbers, strings, + - * / // % **, comparisons, print and a few built ins). Then follow them through the four stages.');
    b.innerHTML = `<div class="pv-top"><label class="pv-lbl" for="pv-src-${el.dataset.k || 'x'}">Your program</label><div class="pv-ex">${EXAMPLES.map((e, i) => `<button type="button" data-ex="${i}">${esc(e[0])}</button>`).join('')}</div></div>
      <textarea class="pv-src" id="pv-src-${el.dataset.k || 'x'}" spellcheck="false" autocapitalize="off" rows="5" aria-label="Python code for the animation"></textarea>
      <div class="pv-tabs" role="tablist">${['1 Tokens', '2 Syntax tree', '3 Bytecode', '4 Run it'].map((t, i) => `<button type="button" role="tab" data-tab="${i}"${i === 3 ? ' class="on" aria-selected="true"' : ' aria-selected="false"'}>${t}</button>`).join('')}</div>
      <div class="pv-pane" data-pane="0" hidden></div><div class="pv-pane" data-pane="1" hidden></div><div class="pv-pane" data-pane="2" hidden></div>
      <div class="pv-pane" data-pane="3"><div class="pv-run"><div class="pv-col"><b>Bytecode</b><ol class="pv-code"></ol></div><div class="pv-col"><b>Value stack</b><div class="pv-stack"></div></div><div class="pv-col"><b>Names (globals)</b><div class="pv-names"></div><b class="pv-outh">Output</b><pre class="pv-out"></pre></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div></div>
      <div class="pv-err" hidden></div>`;
    const ta = $('.pv-src', b), err = $('.pv-err', b), msg = $('.vz-msg', b);
    const panes = [...b.querySelectorAll('.pv-pane')];
    let res = null;
    const P = K.Player($('.vz-p', b), i => show(i), 1500);
    function tab(i) {
      b.querySelectorAll('.pv-tabs button').forEach(x => { const on = +x.dataset.tab === i; x.classList.toggle('on', on); x.setAttribute('aria-selected', on); });
      panes.forEach((p, j) => { p.hidden = j !== i; });
    }
    b.querySelector('.pv-tabs').addEventListener('click', e => { const t = e.target.closest('button'); if (t) tab(+t.dataset.tab); });
    function show(i) {
      if (!res || !res.exec) return;
      const f = res.exec.frames[i];
      b.querySelectorAll('.pv-code li').forEach((li, j) => { li.classList.toggle('on', j === f.pc); li.classList.toggle('done', j < f.pc); });
      const prev = i > 0 ? res.exec.frames[i - 1] : null;
      $('.pv-stack', b).innerHTML = f.stack.length ? f.stack.slice().reverse().map((s, j) => `<span class="pv-cell t-${esc(s.t)}${prev && j === 0 && f.stack.length >= (prev.stack.length) ? ' new' : ''}"><code>${esc(s.r)}</code><small>${esc(s.t)}</small></span>`).join('') : '<span class="pv-empty">empty</span>';
      const ns = Object.entries(f.names);
      $('.pv-names', b).innerHTML = ns.length ? ns.map(([k, v]) => `<div class="pv-name${prev && prev.names[k] !== v ? ' new' : ''}"><b>${esc(k)}</b><span>→</span><code>${esc(v)}</code></div>`).join('') : '<span class="pv-empty">no names yet</span>';
      $('.pv-out', b).textContent = f.out.join('\n') + (i === res.exec.frames.length - 1 && res.exec.error && res.exec.error.type !== 'Demo' ? (f.out.length ? '\n' : '') + `Traceback (most recent call last):\n  File "main.py", line ${res.exec.error.line}, in <module>\n${res.exec.error.type}: ${res.exec.error.msg}` : '');
      const c = f.pc >= 0 ? res.code[f.pc] : null;
      msg.innerHTML = c ? `<b>${esc(c.op)}</b> ${esc(f.note)}` : esc(f.note);
      const on = b.querySelector('.pv-code li.on');
      if (on && on.parentElement.scrollHeight > on.parentElement.clientHeight) on.parentElement.scrollTop = on.offsetTop - on.parentElement.offsetTop - 40;
    }
    function build() {
      res = PYVM.analyse(ta.value);
      err.hidden = true;
      if (res.error) {
        err.hidden = false;
        err.innerHTML = res.stage === 'demo' ? `🙂 ${esc(res.error.msg)}` : `<b>${esc(res.error.type)}</b> on line ${res.error.line}: ${esc(res.error.msg)}<br><small>Python finds this while reading the file, before a single line runs. That is why a syntax error stops the whole program, even the lines above it.</small>`;
        panes.forEach(p => { if (+p.dataset.pane < 3) p.innerHTML = ''; });
        b.querySelector('.pv-code').innerHTML = ''; $('.pv-stack', b).innerHTML = ''; $('.pv-names', b).innerHTML = ''; $('.pv-out', b).textContent = '';
        msg.textContent = 'Fix the code above and the stages will appear again.';
        P.load(1);
        return;
      }
      panes[0].innerHTML = `<p class="pv-cap">The tokenizer reads characters and groups them into tokens, the same way <code>python -m tokenize main.py</code> does. Hover a token to see its type.</p><div class="pv-toks">${res.tokens.map(t => `<span class="pv-tok tt-${t.type}" title="${esc(t.type + ': ' + TYPE_TIPS[t.type])}"><small>${t.type}</small><code>${t.text ? esc(t.text) : '⏎'}</code></span>`).join('')}</div>`;
      panes[1].innerHTML = `<p class="pv-cap">The parser checks the grammar and builds an abstract syntax tree. Brackets and spaces are gone. Only the meaning is left.</p><div class="pv-tree vz-scroll"><ul>${'<li><span class="pv-node k-Module"><b>Module</b></span><ul>' + res.tree.map(treeHtml).join('') + '</ul></li>'}</ul></div><details class="pv-dump"><summary>The same tree as <code>ast.dump(ast.parse(code))</code> prints it</summary><pre>${esc(res.dump)}</pre></details>`;
      panes[2].innerHTML = `<p class="pv-cap">The compiler walks the tree and writes bytecode. Look for constant folding: arithmetic on plain numbers is done once, here, instead of every time the line runs.</p><pre class="pv-dis">${esc(PYVM.disText(res.code))}</pre><p class="pv-cap small">Same layout as <code>dis.dis</code>. LOAD_CONST shows its value. The real listing also shows its position in <code>co_consts</code>.</p>`;
      b.querySelector('.pv-code').innerHTML = res.code.map(c => `<li><span class="ln">${c.starts && c.line ? 'L' + c.line : ''}</span><b>${esc(c.op)}</b>${c.arg !== null && c.arg !== undefined && c.op !== 'RESUME' ? ` <i>${esc(String(c.arg))}</i>` : ''}${c.rep ? ` <code>(${esc(c.rep)})</code>` : ''}</li>`).join('');
      P.load(res.exec.frames.length);
    }
    b.querySelector('.pv-ex').addEventListener('click', e => { const t = e.target.closest('button'); if (!t) return; ta.value = EXAMPLES[+t.dataset.ex][1]; build(); });
    let timer = null;
    ta.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(build, 350); });
    ta.value = EXAMPLES[0][1];
    build();
  };
})();
