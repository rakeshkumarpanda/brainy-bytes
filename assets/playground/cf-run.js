/* ===== Code Playground: the runner for Java, C#, C and C++ =====
   cf-parse.js turns the code into a tree. This file walks that tree one statement at a time.
   Before each statement it can take a snapshot (line, call stack, variables and output so far), which is
   what the page plays back when you press Step line by line.

   CF.run(src, lang, { stdin, trace, maxSteps, maxOps }) -> { out: [{s, e}], trace: [...], error, compile, steps }
   The values follow each language's rules: int wraps around at 32 bits, long uses 64 bits, 7 / 2 is 3,
   char + 1 is a number, Java prints 1.0 where C# prints 1, C++ cout prints 6 significant digits. */
(() => {
  const G = typeof self !== 'undefined' ? self : globalThis;
  const CF = G.CF;

  /* ---------- values ---------- */
  let objIds = 0;
  class Arr { constructor(a, et) { this.a = a; this.et = et; this.id = ++objIds; } }
  class Obj { constructor(ci) { this.ci = ci; this.f = Object.create(null); this.id = ++objIds; } }
  class Fn { constructor(o) { Object.assign(this, o); this.id = ++objIds; } }
  /* a pointer: into an array (arr, i), at a variable (box) or at a field (obj, key) */
  class Ptr {
    constructor(arr, i, box, et) { this.arr = arr; this.i = i || 0; this.box = box || null; this.et = et || null; }
    get() {
      if (this.box) return this.box.v;
      if (this.arr.freed) throw new Fatal('This memory was already freed with free() or delete. Reading it is undefined behaviour');
      if (this.i < 0 || this.i >= this.arr.length) throw new Fatal(`The pointer reads element ${this.i} of a block that holds ${this.arr.length}. This is past the end of the memory, which is undefined behaviour in C and C++`);
      return this.arr[this.i];
    }
    set(v) {
      if (this.box) { this.box.v = v; return; }
      if (this.i < 0 || this.i >= this.arr.length) throw new Fatal(`The pointer writes element ${this.i} of a block that holds ${this.arr.length}. Writing outside the memory you own is undefined behaviour and real programs often crash here`);
      this.arr[this.i] = v;
    }
    add(n) { if (this.box) { if (n === 0) return this; return new Ptr([this.box.v], n, null, this.et); } return new Ptr(this.arr, this.i + n, null, this.et); }
  }
  class Box { constructor(v, ty) { this.v = v; this.ty = ty; } }
  /* a reference variable (C++ int& r, C# ref and out) reads and writes someone else's storage */
  class RefBox {
    constructor(ref, ty) { this.ref = ref; this.ty = ty; }
    get v() { return this.ref.get(); }
    set v(x) { this.ref.set(x); }
  }
  class ClassRef { constructor(ci) { this.ci = ci; } }
  class NS { constructor(name) { this.name = name; } }
  class Fatal extends Error { constructor(msg, kind) { super(msg); this.kind = kind || 'fatal'; } }
  class Throw { constructor(val, line) { this.val = val; this.line = line; } }
  class StopRun { constructor(why) { this.why = why; } }
  class ExitSig { constructor(code) { this.code = code; } }
  const BRK = { s: 'brk' }, CONT = { s: 'cont' };
  class Ret { constructor(v) { this.v = v; } }
  class Brk { constructor(label) { this.label = label; } }
  class Cont { constructor(label) { this.label = label; } }

  Object.assign(CF, { Arr, Obj, Fn, Ptr, Box, RefBox, ClassRef, NS, Fatal, Throw });

  /* ---------- types ---------- */
  const T = n => ({ n });
  const TY = { int: T('int'), long: T('long'), double: T('double'), float: T('float'), char: T('char'), bool: T('bool'), string: T('string'), void: T('void'),
    uint: T('uint'), ulong: T('ulong'), short: T('short'), byte: T('byte'), ubyte: T('ubyte'), null: T('null'), dyn: T('dyn'), object: T('object') };
  const NK = { byte: 'i', ubyte: 'i', short: 'i', ushort: 'i', int: 'i', char: 'i', uint: 'u', long: 'l', ulong: 'ul', float: 'f', double: 'd' };
  const isArrTy = t => t && (t.dim || 0) > 0;
  const isPtrTy = t => t && (t.ptr || 0) > 0;
  const plain = t => t && !isArrTy(t) && !isPtrTy(t);
  const SIZE = { char: 1, bool: 1, byte: 1, ubyte: 1, short: 2, ushort: 2, int: 4, uint: 4, float: 4, long: 8, ulong: 8, double: 8, string: 32 };
  CF.TY = TY;

  function kindOf(ty, v) {
    if (ty && plain(ty) && NK[ty.n]) return NK[ty.n];
    if (typeof v === 'bigint') return 'l';
    if (typeof v === 'number') return Number.isInteger(v) && !(ty && (ty.n === 'double' || ty.n === 'float')) ? 'i' : 'd';
    return null;
  }
  const KT = { i: TY.int, u: TY.uint, l: TY.long, ul: TY.ulong, f: TY.float, d: TY.double };
  function promote(a, b) {
    if (a === 'd' || b === 'd') return 'd';
    if (a === 'f' || b === 'f') return 'f';
    if (a === 'ul' || b === 'ul') return 'ul';
    if (a === 'l' || b === 'l') return 'l';
    if (a === 'u' || b === 'u') return 'u';
    return 'i';
  }
  const toNum = v => typeof v === 'bigint' ? Number(v) : typeof v === 'boolean' ? (v ? 1 : 0) : v === null ? 0 : v;
  const toBig = v => typeof v === 'bigint' ? v : BigInt(Math.trunc(toNum(v)) || 0);
  const i32 = v => {
    if (typeof v === 'bigint') return Number(BigInt.asIntN(32, v));
    if (typeof v === 'boolean') return v ? 1 : 0;
    if (!Number.isFinite(v)) return Number.isNaN(v) ? 0 : v > 0 ? 2147483647 : -2147483648;
    const t = Math.trunc(v);
    if (t > 2147483647 || t < -2147483648) {
      /* Java and C# saturate a double that is too big when cast to int */
      return t > 0 ? 2147483647 : -2147483648;
    }
    return t | 0;
  };
  const wrapInt = v => typeof v === 'bigint' ? Number(BigInt.asIntN(32, v)) : (Math.trunc(v) | 0);
  CF.i32 = i32;

  /* ---------- number to text, the way each language prints it ---------- */
  function shortest(v, isFloat) {
    if (!isFloat) return String(v);
    const f = Math.fround(v);
    for (let p = 1; p <= 9; p++) { const s = f.toPrecision(p); if (Math.fround(+s) === f) return String(+s); }
    return String(f);
  }
  /* split a shortest decimal into digits and exponent: 0.00123 -> ('123', -3) meaning 1.23e-3 */
  function digitsOf(s) {
    let neg = s[0] === '-'; if (neg) s = s.slice(1);
    let [m, e] = s.split('e'); e = +(e || 0);
    let [ip, fp = ''] = m.split('.');
    let digits = (ip + fp).replace(/^0+/, '');
    const lead = (ip + fp).length - (ip + fp).replace(/^0+/, '').length;
    const exp = ip.length - 1 - lead + e;
    digits = digits.replace(/0+$/, '') || '0';
    return { neg, digits, exp };
  }
  function javaDouble(v, isFloat) {
    if (Number.isNaN(v)) return 'NaN';
    if (!Number.isFinite(v)) return v > 0 ? 'Infinity' : '-Infinity';
    if (v === 0) return Object.is(v, -0) ? '-0.0' : '0.0';
    const s = shortest(v, isFloat);
    const a = Math.abs(v);
    if (a >= 1e-3 && a < 1e7) { return s.includes('.') ? s : (s.includes('e') ? (+s).toFixed(0) + '.0' : s + '.0'); }
    const { neg, digits, exp } = digitsOf(s);
    return (neg ? '-' : '') + digits[0] + '.' + (digits.slice(1) || '0') + 'E' + exp;
  }
  function csDouble(v, isFloat) {
    if (Number.isNaN(v)) return 'NaN';
    if (!Number.isFinite(v)) return v > 0 ? '∞' : '-∞';
    if (v === 0) return Object.is(v, -0) ? '-0' : '0';
    const s = shortest(v, isFloat);
    const { neg, digits, exp } = digitsOf(s);
    if (exp >= 15 || exp < -5) return (neg ? '-' : '') + digits[0] + (digits.length > 1 ? '.' + digits.slice(1) : '') + 'E' + (exp < 0 ? '-' : '+') + String(Math.abs(exp)).padStart(2, '0');
    return (+s).toString().includes('e') ? fixedExact(v, Math.max(0, digits.length - 1 - exp)) : String(+s);
  }
  /* exact decimal rounding, ties to even, the way C printf rounds */
  function fixedExact(v, f, mode) {
    if (!Number.isFinite(v)) return Number.isNaN(v) ? 'nan' : v > 0 ? 'inf' : '-inf';
    f = Math.min(f, 60);
    let s = Math.abs(v).toFixed(Math.min(100, f + 40));
    const neg = v < 0 || Object.is(v, -0);
    const [ip, fp] = s.split('.');
    const keep = fp.slice(0, f), rest = fp.slice(f);
    let digits = ip + keep;
    let up = false;
    if (rest[0] > '5') up = true;
    else if (rest[0] === '5') {
      const tail = rest.slice(1).replace(/0+$/, '');
      if (tail) up = true;
      else if (mode === 'up') up = true;
      else up = (+digits[digits.length - 1]) % 2 === 1;
    }
    if (up) {
      let arr = digits.split(''), k = arr.length - 1;
      while (k >= 0) { if (arr[k] === '9') { arr[k] = '0'; k--; } else { arr[k] = String(+arr[k] + 1); break; } }
      if (k < 0) arr.unshift('1');
      digits = arr.join('');
    }
    const il = digits.length - f;
    let out = digits.slice(0, il) + (f ? '.' + digits.slice(il) : '');
    if (out[0] === '.') out = '0' + out;
    const isZero = !/[1-9]/.test(out);
    return (neg && !(isZero && !Object.is(v, -0) && v >= 0) && (v < 0 || Object.is(v, -0)) ? '-' : '') + out;
  }
  /* Java rounds the shortest decimal form HALF_UP */
  function fixedJava(v, f) {
    if (!Number.isFinite(v)) return Number.isNaN(v) ? 'NaN' : v > 0 ? 'Infinity' : '-Infinity';
    const s = String(Math.abs(v));
    if (s.includes('e')) return fixedExact(v, f, 'up');
    const [ip, fp = ''] = s.split('.');
    if (fp.length <= f) return (v < 0 ? '-' : '') + ip + (f ? '.' + fp.padEnd(f, '0') : '');
    let digits = ip + fp.slice(0, f);
    if (fp[f] >= '5') {
      let arr = digits.split(''), k = arr.length - 1;
      while (k >= 0) { if (arr[k] === '9') { arr[k] = '0'; k--; } else { arr[k] = String(+arr[k] + 1); break; } }
      if (k < 0) arr.unshift('1');
      digits = arr.join('');
    }
    const il = digits.length - f;
    const out = digits.slice(0, il) + (f ? '.' + digits.slice(il) : '');
    return (v < 0 && /[1-9]/.test(out) ? '-' : '') + out;
  }
  function expC(v, p, upper) {
    if (!Number.isFinite(v)) return Number.isNaN(v) ? 'nan' : v > 0 ? 'inf' : '-inf';
    let s = v.toExponential(Math.min(p, 100));
    let [m, e] = s.split('e');
    const en = +e;
    return m + (upper ? 'E' : 'e') + (en < 0 ? '-' : '+') + String(Math.abs(en)).padStart(2, '0');
  }
  function fmtG(v, p, alt, upper) {
    if (!Number.isFinite(v)) return Number.isNaN(v) ? 'nan' : v > 0 ? 'inf' : '-inf';
    if (p === 0) p = 1;
    if (v === 0) return alt ? '0.' + '0'.repeat(p - 1) : (Object.is(v, -0) ? '-0' : '0');
    const e = +v.toExponential(p - 1).split('e')[1];
    let s;
    if (e < -4 || e >= p) {
      s = expC(v, p - 1, upper);
      if (!alt) s = s.replace(/\.?0+(e|E)/, '$1');
    } else {
      s = fixedExact(v, Math.max(0, p - 1 - e));
      if (!alt && s.includes('.')) s = s.replace(/\.?0+$/, '');
    }
    return s;
  }
  CF.fmt = { javaDouble, csDouble, fixedExact, fixedJava, fmtG, expC };

  /* ---------- printf, String.format and C# composite formatting ---------- */
  function group(intPart, sep = ',') { return intPart.replace(/\B(?=(\d{3})+(?!\d))/g, sep); }
  function printf(I, fmt, args, tys, lang) {
    let out = '', ai = 0;
    const re = /%([-+ 0#,(]*)(\*|\d+)?(?:\.(\*|\d+))?(hh|h|ll|l|L|z|j|t)?([diouxXeEfFgGcspnaAb%hHS])/g;
    let last = 0, m;
    while ((m = re.exec(fmt))) {
      out += fmt.slice(last, m.index); last = re.lastIndex;
      let [, flags, width, prec, len, conv] = m;
      if (conv === '%') { out += '%'; continue; }
      if (conv === 'n' && lang === 'java') { out += '\n'; continue; }
      if (width === '*') width = toNum(args[ai++]);
      if (prec === '*') prec = toNum(args[ai++]);
      width = width === undefined ? 0 : +width;
      prec = prec === undefined ? undefined : +prec;
      if (ai >= args.length) {
        if (lang === 'java') throw I.ex('MissingFormatArgumentException', `Format specifier '${m[0]}'`);
        out += lang === 'c' || lang === 'cpp' ? '' : m[0]; continue;
      }
      const v = args[ai], ty = tys[ai]; ai++;
      let s;
      const left = flags.includes('-'), zero = flags.includes('0') && !left, plus = flags.includes('+'), space = flags.includes(' '), comma = flags.includes(','), alt = flags.includes('#');
      const sign = (neg, body) => (neg ? '-' : plus ? '+' : space ? ' ' : '') + body;
      switch (conv) {
        case 'd': case 'i': case 'u': {
          if (lang === 'java' && (kindOf(ty, v) === 'd' || kindOf(ty, v) === 'f')) throw I.ex('IllegalFormatConversionException', `d != java.lang.Double`);
          let n = typeof v === 'bigint' ? v : (typeof v === 'number' ? Math.trunc(v) : v === true ? 1 : v === false ? 0 : v instanceof Ptr ? 0 : +v);
          if (conv === 'u' && typeof n === 'number' && n < 0) n = len === 'l' || len === 'll' ? BigInt.asUintN(64, BigInt(n)) : n >>> 0;
          if ((lang === 'c' || lang === 'cpp') && conv !== 'u' && typeof n === 'number' && !(len === 'l' || len === 'll')) n = n | 0;
          const neg = n < 0;
          let body = String(neg ? -n : n).replace('n', '');
          if (prec !== undefined) body = body.padStart(prec, '0');
          if (comma) body = group(body);
          s = sign(neg, body);
          if (zero && s.length < width) s = s.replace(/^([-+ ]?)/, '$1' + '0'.repeat(width - s.length));
          break;
        }
        case 'x': case 'X': case 'o': {
          let n = typeof v === 'bigint' ? BigInt.asUintN(64, v) : (toNum(v) >>> 0);
          if (typeof v === 'bigint' && lang !== 'java') n = BigInt.asUintN(64, v);
          let body = n.toString(conv === 'o' ? 8 : 16);
          if (conv === 'X') body = body.toUpperCase();
          if (alt && n != 0) body = (conv === 'o' ? '0' : conv === 'x' ? '0x' : '0X') + body;
          if (prec !== undefined) body = body.padStart(prec, '0');
          s = body;
          if (zero && s.length < width) s = '0'.repeat(width - s.length) + s;
          break;
        }
        case 'f': case 'F': case 'e': case 'E': case 'g': case 'G': case 'a': case 'A': {
          if (lang === 'java' && kindOf(ty, v) !== 'd' && kindOf(ty, v) !== 'f' && !(v instanceof Obj)) throw I.ex('IllegalFormatConversionException', `${conv} != java.lang.${typeof v === 'bigint' ? 'Long' : 'Integer'}`);
          const x = toNum(v);
          const p = prec === undefined ? 6 : prec;
          let body;
          const neg = x < 0 || Object.is(x, -0);
          const ax = Math.abs(x);
          if (conv === 'f' || conv === 'F') body = lang === 'java' ? fixedJava(ax, p) : fixedExact(ax, p);
          else if (conv === 'e' || conv === 'E') body = expC(ax, p, conv === 'E');
          else body = fmtG(ax, p, alt, conv === 'G');
          if (lang === 'java' && !Number.isFinite(x)) body = Number.isNaN(x) ? 'NaN' : 'Infinity';
          if (comma) { const [a, b] = body.split('.'); body = group(a) + (b !== undefined ? '.' + b : ''); }
          s = sign(neg && !Number.isNaN(x), body);
          if (zero && s.length < width && Number.isFinite(x)) s = s.replace(/^([-+ ]?)/, '$1' + '0'.repeat(width - s.length));
          break;
        }
        case 'c': s = typeof v === 'string' ? v[0] : String.fromCodePoint(toNum(v) & (lang === 'c' || lang === 'cpp' ? 0xff : 0x1fffff)); break;
        case 's': case 'S': {
          if (lang === 'c' || lang === 'cpp') s = v instanceof Ptr || v instanceof Arr ? I.cstr(v) : typeof v === 'string' ? v : (v === null ? '(null)' : String(v));
          else s = I.str(v, ty);
          if (prec !== undefined) s = s.slice(0, prec);
          if (conv === 'S') s = s.toUpperCase();
          break;
        }
        case 'b': case 'B': s = lang === 'java' ? String(v === null ? false : typeof v === 'boolean' ? v : true) : ''; break;
        case 'p': s = '0x7ffd' + (v && v.arr ? (0x5a3c00 + (v.i || 0) * 4).toString(16) : '00000000'); break;
        case 'h': case 'H': s = (I.hashOf(v) >>> 0).toString(16); break;
        default: s = m[0];
      }
      if (s.length < width) s = left ? s.padEnd(width) : s.padStart(width);
      out += s;
    }
    out += fmt.slice(last);
    if (lang === 'java') out = out.replace(/%n/g, '\n');
    return out;
  }
  /* C# format strings: F2, N0, D5, X, P1, E3, C, G, 0.00, #,##0 */
  function csFormat(I, v, ty, spec) {
    if (spec === null || spec === undefined || spec === '') return I.str(v, ty);
    const m = spec.match(/^([A-Za-z])(\d*)$/);
    const x = toNum(v);
    if (m) {
      const c = m[1], p = m[2] === '' ? null : +m[2];
      switch (c.toUpperCase()) {
        case 'F': return fixedExact(x, p ?? 2, 'up');
        case 'N': { const s = fixedExact(Math.abs(x), p ?? 2, 'up'); const [a, b] = s.split('.'); return (x < 0 ? '-' : '') + group(a) + (b ? '.' + b : ''); }
        case 'D': { const neg = x < 0; return (neg ? '-' : '') + String(Math.abs(typeof v === 'bigint' ? Number(v) : x)).padStart(p ?? 0, '0'); }
        case 'X': { let s = (typeof v === 'bigint' ? BigInt.asUintN(64, v) : x >>> 0).toString(16); if (c === 'X') s = s.toUpperCase(); return s.padStart(p ?? 0, '0'); }
        case 'P': return fixedExact(x * 100, p ?? 2, 'up') + '%';
        case 'E': return expC(x, p ?? 6, c === 'E').replace(/e([+-])(\d+)$/i, (a, s, d) => (c === 'E' ? 'E' : 'e') + s + d.padStart(3, '0'));
        case 'C': { const s = fixedExact(Math.abs(x), p ?? 2, 'up'); const [a, b] = s.split('.'); return (x < 0 ? '-' : '') + '¤' + group(a) + (b ? '.' + b : ''); }
        case 'G': return p ? String(+x.toPrecision(p)) : I.str(v, ty);
        case 'R': return I.str(v, ty);
      }
    }
    /* custom pattern like 0.00, #.##, #,##0.0, 000 */
    const pm = spec.match(/^([#0,]*)(?:\.([#0]*))?(%?)$/);
    if (pm) {
      const ip = pm[1], fp = pm[2] || '';
      let val = pm[3] ? x * 100 : x;
      const minF = (fp.match(/0/g) || []).length, maxF = fp.length;
      let s = fixedExact(Math.abs(val), maxF, 'up');
      let [a, b = ''] = s.split('.');
      while (b.length > minF && b.endsWith('0')) b = b.slice(0, -1);
      const minI = (ip.replace(/,/g, '').match(/0/g) || []).length;
      a = a.padStart(minI, '0');
      if (minI === 0 && a === '0') a = '';
      if (ip.includes(',')) a = group(a);
      return (val < 0 && /[1-9]/.test(a + b) ? '-' : '') + a + (b ? '.' + b : '') + pm[3];
    }
    return I.str(v, ty);
  }
  function csComposite(I, fmt, args, tys) {
    return fmt.replace(/\{\{|\}\}|\{(\d+)(?:,(-?\d+))?(?::([^}]*))?\}/g, (all, i, al, spec) => {
      if (all === '{{') return '{';
      if (all === '}}') return '}';
      if (+i >= args.length) throw I.ex('FormatException', 'Index (zero based) must be greater than or equal to zero and less than the size of the argument list.');
      let s = csFormat(I, args[+i], tys[+i], spec);
      if (al) { const w = +al; s = w < 0 ? s.padEnd(-w) : s.padStart(w); }
      return s;
    });
  }
  CF.printf = printf; CF.csFormat = csFormat; CF.csComposite = csComposite;

  /* ---------- Java's hash codes, so HashMap and HashSet list keys in the same order Java does ---------- */
  function strHash(s) { let h = 0; for (let i = 0; i < s.length; i++) h = (Math.imul(31, h) + s.charCodeAt(i)) | 0; return h; }
  const f64 = new Float64Array(1), u32 = new Uint32Array(f64.buffer);
  function dblHash(d) { f64[0] = d === 0 ? 0 : d; return (u32[0] ^ u32[1]) | 0; }

  /* ---------- the interpreter ---------- */
  class Interp {
    constructor(prog, lang, opts) {
      this.prog = prog; this.lang = lang; this.o = opts;
      this.out = []; this.outLen = 0;
      this.stdin = opts.stdin || ''; this.inPos = 0;
      this.trace = opts.trace ? [] : null;
      this.maxSteps = opts.maxSteps || 3000;
      this.maxOps = opts.maxOps || 30000000;
      this.ops = 0; this.depth = 0;
      this.frames = [];
      this.classes = new Map();
      this.funcs = new Map();
      this.globals = new Env(null);
      this.warned = new Set();
      this.notes = [];
      this.cout = { kind: 'out', prec: 6, fixed: false, sci: false, alpha: false, width: 0, fill: ' ', left: false, base: 10, showpoint: false, err: false };
      this.cerr = Object.assign({}, this.cout, { err: true });
      this.cin = { kind: 'in', fail: false, isCin: true };
      this.randSeed = 1; this.glibc = null;
      this.lastLine = 0;
    }
    /* output */
    write(s, err) {
      if (!s) return;
      s = String(s);
      const last = this.out[this.out.length - 1];
      if (last && !!last.e === !!err) last.s += s; else this.out.push({ s, e: !!err });
      this.outLen += s.length;
      if (this.outLen > 200000) throw new StopRun('The program printed more than 200000 characters, so the playground stopped it. A loop may be printing forever');
    }
    warn(key, msg) { if (!this.warned.has(key)) { this.warned.add(key); this.notes.push(msg); } }

    /* ---------- tracing ---------- */
    step(line, env, ev, extra) {
      this.lastLine = line;
      if (++this.ops > this.maxOps) throw new StopRun('The program ran for a very long time, so the playground stopped it. Check for a loop whose condition never becomes false');
      if (!this.trace) return;
      const fr = this.frames[this.frames.length - 1];
      if (fr) { fr.cur = env; fr.line = line; }
      if (this.trace.length >= this.maxSteps) throw new StopRun(`Step by step shows the first ${this.maxSteps} steps. Use Run all to run the whole program`);
      const snap = { line, ev: ev || 'line', out: this.outLen, stack: this.frames.map(f => this.snapFrame(f)) };
      if (extra) Object.assign(snap, extra);
      const gl = this.snapGlobals();
      if (gl.length) snap.globals = gl;
      this.trace.push(snap);
    }
    snapFrame(f) {
      const vars = [];
      const seen = new Set();
      const envs = [];
      for (let e = f.cur; e; e = e.p) { envs.push(e); if (e === f.root) break; }
      /* inner blocks hide outer names, and each block lists its variables in the order they were made */
      const groups = [];
      for (const e of envs) {
        const g = [];
        for (const [k, b] of e.v) {
          if (seen.has(k) || k.startsWith('$')) continue;
          seen.add(k);
          g.push([k, this.short(b instanceof RefBox ? safeGet(b) : b.v, b.ty, 0, b), b instanceof RefBox ? 'ref' : '']);
        }
        groups.push(g);
      }
      for (let gi = groups.length - 1; gi >= 0; gi--) vars.push(...groups[gi]);
      if (f.self) vars.unshift(['this', this.short(f.self, null, 0), 'this']);
      return { fn: f.name, line: f.line, vars };
    }
    snapGlobals() {
      const out = [];
      for (const [k, b] of this.globals.v) if (!b.konst && !(b.v instanceof Fn)) out.push([k, this.short(b.v, b.ty, 0)]);
      for (const ci of this.classes.values()) {
        if (!ci.sinit || ci.builtin) continue;
        for (const [k, b] of ci.sf) if (!b.konst) out.push([ci.name + '.' + k, this.short(b.v, b.ty, 0)]);
      }
      return out;
    }
    /* a short text for a value in the variables panel */
    short(v, ty, d, box) {
      if (box && box.uninit) return this.lang === 'c' || this.lang === 'cpp' ? '?' : 'not set yet';
      if (v === undefined) return '?';
      if (v === null) return this.lang === 'java' ? 'null' : this.lang === 'cs' ? 'null' : 'NULL';
      if (d > 2) return '…';
      if (typeof v === 'string') return ty && ty.n === 'char' ? "'" + v + "'" : JSON.stringify(v.length > 60 ? v.slice(0, 60) + '…' : v);
      if (ty && ty.n === 'char' && typeof v === 'number' && plain(ty)) return "'" + chr(v) + "'";
      if (typeof v === 'boolean') return this.lang === 'cs' ? (v ? 'True' : 'False') : String(v);
      if (typeof v === 'number' || typeof v === 'bigint') {
        if (ty && (ty.n === 'double' || ty.n === 'float') && plain(ty)) return this.str(v, ty);
        if (typeof v === 'number' && !Number.isInteger(v)) return String(+v.toPrecision(12));
        return String(v);
      }
      if (v instanceof Arr) {
        const items = v.a.slice(0, 20).map(x => this.short(x, v.et && v.et.dim ? v.et : elemTy(v), d + 1));
        return '[' + items.join(', ') + (v.a.length > 20 ? ', … ' + v.a.length + ' items' : '') + ']';
      }
      if (v instanceof Ptr) {
        if (v.box) return '&' + (v.name || 'variable') + (d === 0 ? ' (points to ' + this.short(v.box.v, v.box.ty, d + 1) + ')' : '');
        const blk = v.arr;
        if (blk.isObj) return 'pointer to ' + this.short(blk[0], null, d + 1);
        /* a char pointer is shown as the text it points to, like a debugger does */
        if (v.et && v.et.n === 'char' && !v.et.ptr && blk.every(x => typeof x === 'number')) {
          let t = ''; for (let k = v.i; k < blk.length && blk[k] !== 0 && t.length < 60; k++) t += String.fromCharCode(blk[k]);
          return JSON.stringify(t) + (v.i ? ' (from position ' + v.i + ')' : '');
        }
        return 'pointer to [' + v.i + '] of ' + (blk.length > 12 ? blk.length + ' items' : '[' + blk.map(x => this.short(x, v.et, d + 1)).join(', ') + ']');
      }
      if (v instanceof Fn) return v.fname ? 'function ' + v.fname : 'lambda';
      if (v instanceof ClassRef) return 'class ' + v.ci.name;
      if (v instanceof Obj) {
        if (v.ci.isEnum) return v.f.$name;
        if (v.ci.exc) return v.ci.name + '(' + JSON.stringify(v.f.$msg ?? '') + ')';
        const fs = this.fieldNames(v.ci).filter(k => k in v.f).slice(0, 8).map(k => k + '=' + this.short(v.f[k], this.fieldTy(v.ci, k), d + 1));
        return v.ci.name + '{' + fs.join(', ') + '}';
      }
      if (v && v.$lib) return v.$short(this, d);
      if (v && v.kind === 'out') return 'stream';
      return String(v);
    }
    fieldNames(ci) { const out = []; for (let c = ci; c; c = c.base) out.unshift(...c.fieldList.filter(f => !f.static).map(f => f.id)); return out; }
    fieldTy(ci, k) { for (let c = ci; c; c = c.base) { const f = c.fieldList.find(x => x.id === k); if (f) return f.ty; } return null; }

    /* ---------- values to text ---------- */
    str(v, ty, ctx) {
      const L = this.lang;
      if (v === null || v === undefined) return L === 'cs' ? '' : L === 'java' ? 'null' : '0';
      if (typeof v === 'string') return v;
      if (typeof v === 'boolean') return L === 'cs' ? (v ? 'True' : 'False') : L === 'java' ? String(v) : (v ? '1' : '0');
      if (ty && plain(ty) && ty.n === 'char' && typeof v === 'number') return chr(v);
      if (typeof v === 'bigint') return String(v);
      if (typeof v === 'number') {
        const k = kindOf(ty, v);
        if (k === 'd' || k === 'f') {
          if (L === 'java') return javaDouble(v, k === 'f');
          if (L === 'cs') return csDouble(v, k === 'f');
          return fmtG(v, 6);
        }
        return String(v);
      }
      if (v instanceof Arr) {
        if (L === 'java') { const et = v.et || {}; const code = { int: 'I', double: 'D', char: 'C', long: 'J', bool: 'Z', float: 'F', byte: 'B', short: 'S' }[et.n] || 'Ljava.lang.' + (et.n === 'string' ? 'String' : et.n) + ';'; if (et.n === 'char' && !et.dim && ctx === 'print') return v.a.map(chr).join(''); return '[' + '['.repeat(et.dim || 0) + code + '@' + this.hashHex(v); }
        if (L === 'cs') return 'System.' + csTypeName(v.et) + '[]';
        return '0x' + (0x7ffd5a3c00 + v.id * 64).toString(16);
      }
      if (v instanceof Ptr) { if (v.arr && v.et && v.et.n === 'char') return this.cstr(v); return '0x' + (0x55d4a3c2b0 + (v.arr ? v.i * 4 : 0) + v.id * 32 || 0).toString(16); }
      if (v instanceof Obj) return this.objStr(v);
      if (v instanceof Fn) return L === 'java' ? 'Main$$Lambda@' + this.hashHex(v) : 'System.Func`2';
      if (v instanceof ClassRef) return v.ci.name;
      if (v && v.$lib) return v.$str(this);
      return String(v);
    }
    objStr(o) {
      const ci = o.ci;
      const m = this.findMethod(ci, this.lang === 'cs' ? 'ToString' : 'toString', 0);
      if (m && !m.builtin) return this.str(this.invoke(m, o, [], [], ci.name + '.toString'), TY.string);
      if (ci.isEnum) return o.f.$name;
      if (ci.exc) {
        const msg = o.f.$msg;
        if (this.lang === 'java') return this.qualEx(ci) + (msg !== null && msg !== undefined ? ': ' + msg : '');
        if (this.lang === 'cs') return this.qualEx(ci) + ': ' + (msg ?? '');
      }
      if (ci.record) {
        const names = ci.recParams.map(p => p.id);
        if (this.lang === 'java') return ci.name + '[' + names.map(k => k + '=' + this.str(o.f[k], this.fieldTy(ci, k))).join(', ') + ']';
        return ci.name + ' { ' + names.map(k => k + ' = ' + this.str(o.f[k], this.fieldTy(ci, k))).join(', ') + ' }';
      }
      if (this.lang === 'java') return ci.name + '@' + this.hashHex(o);
      if (this.lang === 'cs') return ci.name;
      return ci.name;
    }
    hashOf(v) {
      if (v === null || v === undefined) return 0;
      if (typeof v === 'string') return strHash(v);
      if (typeof v === 'boolean') return v ? 1231 : 1237;
      if (typeof v === 'bigint') return Number(BigInt.asIntN(32, v ^ (v >> 32n)));
      if (typeof v === 'number') return Number.isInteger(v) && Math.abs(v) < 2 ** 31 ? v | 0 : dblHash(v);
      if (v instanceof Obj) {
        const m = this.findMethod(v.ci, this.lang === 'cs' ? 'GetHashCode' : 'hashCode', 0);
        if (m && !m.builtin) return toNum(this.invoke(m, v, [], [], 'hashCode')) | 0;
        if (v.ci.record) { let h = 0; for (const p of v.ci.recParams) h = (Math.imul(31, h) + this.hashOf(v.f[p.id])) | 0; return h; }
        if (v.ci.isEnum) return this.idHash(v);
        return this.idHash(v);
      }
      if (v && v.$lib && v.$hash) return v.$hash(this);
      return this.idHash(v);
    }
    idHash(v) { return (Math.imul(v.id || 7, 0x9e3779b1) ^ 0x1b6d3586) >>> 1; }
    hashHex(v) { return this.idHash(v).toString(16); }
    equals(a, b) {
      if (a === b) return true;
      if (a === null || b === null || a === undefined || b === undefined) return false;
      if (typeof a === 'bigint' || typeof b === 'bigint') return typeof a !== 'object' && typeof b !== 'object' && a == b;
      if (typeof a !== 'object') return a === b;
      if (a instanceof Obj) {
        const m = this.findMethod(a.ci, this.lang === 'cs' ? 'Equals' : 'equals', 1);
        if (m && !m.builtin) return !!this.invoke(m, a, [b], [null], 'equals');
        if (a.ci.record && b instanceof Obj && b.ci === a.ci) return a.ci.recParams.every(p => this.equals(a.f[p.id], b.f[p.id]));
        if ((this.lang === 'cpp' || this.lang === 'c') && b instanceof Obj && b.ci === a.ci) return Object.keys(a.f).every(k => this.equals(a.f[k], b.f[k]));
        return false;
      }
      if (a.$lib && a.$eq) return a.$eq(b, this);
      if (a instanceof Ptr && b instanceof Ptr) return a.arr === b.arr && a.i === b.i && a.box === b.box;
      return false;
    }
    cstr(v) {
      if (typeof v === 'string') return v;
      if (v instanceof Arr) v = new Ptr(v.a, 0);
      if (!(v instanceof Ptr)) return String(v);
      if (v.box) return typeof v.box.v === 'string' ? v.box.v : chr(v.box.v);
      let s = '';
      for (let i = v.i; i < v.arr.length; i++) { const c = v.arr[i]; if (c === 0 || c === undefined || c === null) break; s += typeof c === 'string' ? c : chr(c); }
      return s;
    }
    /* make a C char array from a JS string: "hi" -> ['h','i',0] as codes */
    cchars(s, len) { const a = Array.from(s, c => c.charCodeAt(0)); a.push(0); while (len && a.length < len) a.push(0); return a; }

    /* ---------- exceptions ---------- */
    exClass(name) {
      let ci = this.classes.get(name);
      if (ci) return ci;
      const base = EXC_BASE[this.lang][name];
      if (base === undefined) return null;
      ci = this.synthClass(name, base ? this.exClass(base) : null);
      ci.exc = true; ci.builtin = true;
      return ci;
    }
    synthClass(name, base) {
      const ci = { name, base, fieldList: [], methods: new Map(), ctors: [], sf: new Map(), sinit: true, ifaces: [], builtin: true, d: { kind: 'class' } };
      this.classes.set(name, ci);
      return ci;
    }
    ex(name, msg, cause) {
      const ci = this.exClass(name) || this.exClass(this.lang === 'cpp' ? 'runtime_error' : this.lang === 'java' ? 'RuntimeException' : 'Exception');
      const o = new Obj(ci);
      o.f.$msg = msg === undefined ? null : msg;
      if (cause) o.f.$cause = cause;
      return new Throw(o, this.lastLine);
    }
    qualEx(ci) {
      if (!ci.builtin) return ci.name;
      if (this.lang === 'java') return (JAVA_PKG[ci.name] || 'java.lang') + '.' + ci.name;
      if (this.lang === 'cs') return (CS_PKG[ci.name] || 'System') + '.' + ci.name;
      return 'std::' + ci.name;
    }
    isA(ci, name) {
      for (let c = ci; c; c = c.base) {
        if (c.name === name) return true;
        if (c.ifaces && c.ifaces.some(i => i === name || this.ifaceExtends(i, name))) return true;
      }
      if (name === 'Object' || name === 'object') return true;
      return false;
    }
    ifaceExtends(i, name) {
      const ci = this.classes.get(i);
      return ci && ci !== undefined && ci.name !== name && this.isA(ci, name);
    }

    /* ---------- set up classes, functions and globals ---------- */
    load() {
      const prog = this.prog;
      const add = (d, outer) => {
        const ci = { name: d.name, d, base: null, fieldList: d.fields, methods: new Map(), ctors: d.ctors, sf: new Map(), sinit: false, outer, kind: d.kind,
          ifaces: (d.ifaces || []).map(t => t.n), isEnum: d.kind === 'enum', record: d.kind === 'record', recParams: d.recParams, isStruct: d.kind === 'struct' };
        if (d.kind === 'record' || d.recParams) {
          ci.record = d.kind === 'record';
          ci.recParams = d.recParams || [];
          if (this.lang === 'java' || d.kind === 'record') {
            ci.fieldList = ci.recParams.map(p => ({ ty: p.ty, id: p.id, line: d.line, konst: true })).concat(d.fields);
          } else {
            ci.fieldList = ci.recParams.map(p => ({ ty: p.ty, id: p.id, line: d.line })).concat(d.fields);
          }
        }
        for (const m of d.methods) { if (!ci.methods.has(m.name)) ci.methods.set(m.name, []); ci.methods.get(m.name).push(m); }
        if (this.classes.has(d.name) && !this.classes.get(d.name).builtin && !this.classes.get(d.name).d.fwd && !d.fwd) throw new CF.CompileError(`The class ${d.name} is defined twice`, d.line);
        if (!(this.classes.has(d.name) && d.fwd)) this.classes.set(d.name, ci);
        if (outer) this.classes.set(outer.name + '.' + d.name, ci);
        d.nested.forEach(n => add(n, ci));
      };
      prog.classes.forEach(c => add(c, null));
      for (const ci of this.classes.values()) {
        if (ci.builtin) continue;
        const b = ci.d.base;
        if (b) {
          const bn = b.n;
          let bc = this.classes.get(bn) || this.exClass(bn);
          if (!bc && this.classes.get(bn) === undefined) {
            if (this.lang === 'cs' && /^I[A-Z]/.test(bn)) { ci.ifaces.push(bn); bc = null; }
            else if (['Object', 'object'].includes(bn)) bc = null;
            else if (this.lang === 'java' && ['Comparable', 'Runnable', 'Comparator', 'Iterable', 'Cloneable', 'Serializable'].includes(bn)) { ci.ifaces.push(bn); bc = null; }
            else if (this.lang === 'cs' && ['IComparable', 'IEquatable', 'IDisposable', 'IEnumerable'].includes(bn)) bc = null;
            else bc = this.synthClass(bn, null);
          }
          if (bc && bc.kind === 'interface') { ci.ifaces.push(bc.name); if (this.lang !== 'java') bc = null; else if (ci.kind !== 'interface') bc = null; }
          ci.base = bc || null;
        }
        if (ci.exc === undefined) ci.exc = !!(ci.base && this.isExc(ci.base));
      }
      prog.funcs.forEach(f => { if (!this.funcs.has(f.name)) this.funcs.set(f.name, []); const list = this.funcs.get(f.name); const i = list.findIndex(x => !x.body && x.params.length === f.params.length); if (i >= 0 && f.body) list[i] = f; else if (!(list.some(x => x.body) && !f.body)) list.push(f); });
    }
    isExc(ci) { for (let c = ci; c; c = c.base) if (c.exc) return true; return false; }
    initGlobals() {
      for (const d of this.prog.globals) this.execDecl(d, this.globals, true);
      /* C and C++ enums: their names become int constants */
      for (const ci of this.classes.values()) {
        if (ci.builtin || !ci.isEnum || this.lang === 'java' || this.lang === 'cs') continue;
        let next = 0;
        for (const c of ci.d.consts) {
          if (c.val) next = toNum(this.ev(c.val, this.globals));
          const b = new Box(next, TY.int); b.konst = true;
          if (!(ci.d.scoped)) this.globals.v.set(c.id, b);
          ci.sf.set(c.id, b);
          next++;
        }
        ci.sinit = true;
      }
    }
    /* static fields and static blocks run the first time a class is used */
    clinit(ci) {
      if (ci.sinit) return;
      ci.sinit = true;
      if (ci.builtin) return;
      if (ci.base) this.clinit(ci.base);
      const env = new Env(this.globals);
      const fr = { name: ci.name + ' (static setup)', cls: ci, self: null, root: env, cur: env, line: ci.d.line };
      if (ci.isEnum) {
        if (this.lang === 'java') {
          ci.d.consts.forEach((c, i) => {
            const o = new Obj(ci); o.f.$name = c.id; o.f.$ord = i;
            const b = new Box(o, { n: ci.name }); b.konst = true;
            ci.sf.set(c.id, b);
          });
          this.frames.push(fr);
          try {
            ci.d.consts.forEach(c => {
              const o = ci.sf.get(c.id).v;
              this.initFields(o, ci, env);
              const args = c.args.map(a => this.ev(a, env));
              const k = this.pickCtor(ci, args, c.args, c.line);
              if (k) this.runCtorBody(ci, k, o, args, c.args.map(a => a.ty), c.line);
            });
          } finally { this.frames.pop(); }
        } else {
          let next = 0;
          ci.d.consts.forEach(c => {
            if (c.val) next = toNum(this.ev(c.val, env));
            const o = { $lib: true, $enum: ci, name: c.id, val: next };
            Object.setPrototypeOf(o, CSENUM);
            const b = new Box(o, { n: ci.name }); b.konst = true;
            ci.sf.set(c.id, b);
            next++;
          });
        }
      }
      this.frames.push(fr);
      try {
        for (const f of ci.fieldList) {
          if (!f.static) continue;
          const ty = f.ty;
          let v = f.init ? this.convStore(ty, this.evInit(f.init, ty, env), f.init) : this.defaultVal(ty, f);
          const b = new Box(v, ty); b.konst = f.konst;
          ci.sf.set(f.id, b);
          if (f.prop && f.prop.get && f.prop.get !== 'auto') b.prop = f.prop;
        }
        for (const blk of ci.d.statics) if (blk.isStaticBlock !== false && ci.d.statics.length && blk.k === 'block' && blk.$static !== false) { /* handled below */ }
        (ci.d.staticBlocks || ci.d.statics).forEach(blk => { if (blk.$inst) return; this.execBlock(blk, new Env(env)); });
      } finally { this.frames.pop(); }
    }

    /* ---------- start ---------- */
    main() {
      const L = this.lang;
      this.load();
      /* instance initializer blocks are kept apart from static blocks */
      for (const ci of this.classes.values()) if (!ci.builtin) markInitBlocks(ci.d);
      this.initGlobals();
      let entry = null, owner = null;
      const want = L === 'cs' ? 'Main' : 'main';
      for (const ci of this.classes.values()) {
        if (ci.builtin) continue;
        const ms = ci.methods.get(want);
        if (ms) { const m = ms.find(x => x.static || L === 'cpp'); if (m && (L === 'java' || L === 'cs')) { if (!entry || ci.d.mods?.public) { entry = m; owner = ci; } } }
      }
      if (!entry && this.funcs.has(want)) entry = this.funcs.get(want)[0];
      if (!entry && L === 'java') {
        /* a compact source file may have an instance main inside a class */
        for (const ci of this.classes.values()) { const ms = ci.methods && ci.methods.get('main'); if (ms) { entry = ms[0]; owner = ci; break; } }
      }
      if (!entry && L === 'cs' && this.prog.top.length) {
        const fakeCls = this.synthClass('Program', null); fakeCls.builtin = false; fakeCls.fieldList = []; fakeCls.d = { kind: 'class', statics: [], fields: [], methods: [], ctors: [], nested: [], line: 1 };
        for (const s of this.prog.top) if (s.k === 'localfn') { if (!fakeCls.methods.has(s.m.name)) fakeCls.methods.set(s.m.name, []); fakeCls.methods.get(s.m.name).push(Object.assign(s.m, { static: true })); }
        this.prog.funcs.forEach(f => { if (!fakeCls.methods.has(f.name)) fakeCls.methods.set(f.name, []); fakeCls.methods.get(f.name).push(Object.assign(f, { static: true })); });
        entry = { name: 'Main', params: [], ret: TY.void, body: { k: 'block', body: this.prog.top.filter(s => s.k !== 'localfn'), line: this.prog.top[0].line }, static: true, line: this.prog.top[0].line };
        owner = fakeCls;
      }
      if (!entry) {
        const msg = { java: 'There is no main method to start from. Add: public static void main(String[] args) { ... } inside a class',
          cs: 'There is no Main method to start from. Add: static void Main() { ... } inside a class, or write your statements at the top of the file',
          c: 'There is no main function to start from. Add: int main() { ... return 0; }', cpp: 'There is no main function to start from. Add: int main() { ... return 0; }' }[L];
        throw new CF.CompileError(msg, 1);
      }
      if (owner) this.clinit(owner);
      const args = entry.params.length ? [new Arr([], TY.string)] : [];
      this.mainArgs = entry.params.length > 0;
      let self = null;
      if (owner && !entry.static && L === 'java') { self = new Obj(owner); this.initFields(self, owner, this.globals); }
      const rv = this.invoke(entry, self, args, args.map(() => ({ n: 'string', dim: 1 })), (owner ? owner.name + '.' : '') + entry.name, owner, entry.line);
      return rv;
    }

    /* ---------- functions and methods ---------- */
    invoke(m, self, args, argTys, name, cls, callLine, recvRefs) {
      if (m.builtin) return m.builtin(self, args, argTys);
      if (++this.depth > (this.o.maxDepth || 2200)) {
        this.depth = 0;
        if (this.lang === 'java') throw this.ex('StackOverflowError', null);
        if (this.lang === 'cs') throw new Fatal('Stack overflow. The method keeps calling itself without reaching a base case', 'so');
        throw new Fatal('Segmentation fault (stack overflow). The function keeps calling itself without reaching a base case', 'so');
      }
      const env = new Env(m.closure || (self && self.$cenv) || this.globals);
      const fr = { name: name || m.name, cls: cls || (self && self.ci) || m.owner || null, self, root: env, cur: env, line: m.line, tp: null };
      if (m.tps || (m.params.some(p => p.ty && p.ty.tp))) {
        fr.tp = {};
        m.params.forEach((p, i) => { if (p.ty && p.ty.tp && argTys[i] && argTys[i].n !== 'dyn') fr.tp[p.ty.tp] = Object.assign({}, argTys[i], { dim: (argTys[i].dim || 0) - (p.ty.dim || 0) }); });
      }
      this.frames.push(fr);
      try {
        this.bindParams(m.params, args, argTys, env, recvRefs, fr);
        if (this.trace) this.step(m.line, env, 'call', { fn: fr.name });
        let r;
        if (m.exprBody) { r = this.ev(m.body, env); }
        else {
          r = this.execBlock(m.body, env, true);
          if (r instanceof Ret) r = r.v; else r = undefined;
        }
        if (m.ret && m.ret.n !== 'void' && m.ret.n !== 'var' && r !== undefined) r = this.convStore(this.resolveTy(m.ret, fr), r, null, true);
        if (r === undefined && m.ret && m.ret.n !== 'void' && !m.lambda && !m.isCtor) {
          if (this.lang === 'c' || this.lang === 'cpp') {
            if (m.name !== 'main') this.warn('noreturn:' + m.name, `The function ${m.name} reached its end without a return statement. In C and C++ the value it hands back is then unpredictable. The playground used 0.`);
            r = this.defaultVal(m.ret);
          }
        }
        if (this.trace && !m.isCtor) {
          const retTy = m.ret && m.ret.n !== 'void' && m.ret.n !== 'var' ? m.ret : (m.lastTy || null);
          this.step(m.body && m.body.end ? m.body.end : this.lastLine, fr.cur, 'ret', { fn: fr.name, ret: r === undefined ? null : this.short(r, retTy, 0) });
        }
        return r;
      } finally {
        this.frames.pop();
        this.depth--;
      }
    }
    bindParams(params, args, argTys, env, recvRefs, fr) {
      for (let i = 0; i < params.length; i++) {
        const p = params[i];
        let ty = p.ty ? this.resolveTy(p.ty, fr) : (argTys[i] || TY.dyn);
        if (ty.n === 'var') ty = argTys[i] || TY.dyn;
        if (ty.varargs) {
          const rest = args.slice(i);
          if (rest.length === 1 && rest[0] instanceof Arr && argTys[i] && argTys[i].dim) { env.v.set(p.id, new Box(rest[0], ty)); }
          else env.v.set(p.id, new Box(new Arr(rest.map(x => this.conv(x, Object.assign({}, ty, { dim: ty.dim - 1, varargs: false }))), Object.assign({}, ty, { dim: ty.dim - 1, varargs: false })), ty));
          return;
        }
        if (i >= args.length) {
          if (p.def) { env.v.set(p.id, new Box(this.convStore(ty, this.ev(p.def, env), p.def), ty)); continue; }
          env.v.set(p.id, new Box(this.defaultVal(ty), ty)); continue;
        }
        if (ty.ref && recvRefs && recvRefs[i]) { env.v.set(p.id, new RefBox(recvRefs[i], ty)); continue; }
        env.v.set(p.id, new Box(this.convStore(ty, args[i], null, false, argTys[i]), ty));
      }
    }
    resolveTy(ty, fr) {
      if (!ty) return TY.dyn;
      if (ty.tp) {
        fr = fr || this.frames[this.frames.length - 1];
        for (let k = this.frames.length - 1; k >= 0; k--) { const f = this.frames[k]; if (f.tp && f.tp[ty.tp]) { const b = f.tp[ty.tp]; return Object.assign({}, b, { dim: (b.dim || 0) + (ty.dim || 0), ptr: (b.ptr || 0) + (ty.ptr || 0), ref: ty.ref }); } }
        return ty;
      }
      return ty;
    }
    findMethod(ci, name, nargs) {
      for (let c = ci; c; c = c.base) {
        const ms = c.methods.get(name);
        if (ms) { const m = ms.find(x => x.params.length === nargs || (x.params.length > nargs && x.params[nargs].def) || (x.params.length && x.params[x.params.length - 1].ty.varargs)); if (m) return m; }
      }
      for (const iname of this.allIfaces(ci)) {
        const ic = this.classes.get(iname);
        const ms = ic && ic.methods.get(name);
        if (ms) { const m = ms.find(x => x.params.length === nargs && x.body); if (m) return m; }
      }
      return null;
    }
    allIfaces(ci) { const out = []; for (let c = ci; c; c = c.base) (c.ifaces || []).forEach(i => out.push(i)); return out; }
    /* choose an overload: same number of arguments, then the best matching types */
    pick(list, args, argTys, line, what) {
      const n = args.length;
      const cands = list.filter(m => m.params.length === n || (m.params.length > n && m.params.slice(n).every(p => p.def)) || (m.params.length && m.params[m.params.length - 1].ty && m.params[m.params.length - 1].ty.varargs && n >= m.params.length - 1));
      if (!cands.length) return null;
      if (cands.length === 1) return cands[0];
      let best = null, bs = -1;
      for (const m of cands) {
        let s = 0;
        m.params.forEach((p, i) => { if (i < n) s += this.matchScore(p.ty, argTys[i], args[i]); });
        if (m.params.length === n) s += 1;
        if (s > bs) { bs = s; best = m; }
      }
      return best;
    }
    matchScore(pt, at, v) {
      if (!pt) return 1;
      if (pt.tp || pt.n === 'dyn' || pt.n === 'object' || pt.n === 'Object') return 1;
      if (!at) at = valTy(v);
      if (pt.varargs) return 1;
      if ((pt.dim || 0) !== (at.dim || 0) && !(v instanceof Arr && pt.ptr)) return v === null ? 2 : 0;
      if (pt.n === at.n) return 10;
      const pk = NK[pt.n], ak = NK[at.n];
      if (pk && ak) {
        const rank = { i: 1, u: 1, l: 2, ul: 2, f: 3, d: 4 };
        if (pt.n === 'char' && at.n !== 'char') return 1;
        if (rank[pk] >= rank[ak]) return 8 - (rank[pk] - rank[ak]);
        return 0;
      }
      if (v instanceof Obj && this.isA(v.ci, pt.n)) return 7;
      if (v && v.$lib && v.$is && v.$is(pt.n)) return 7;
      if (v === null && !pk) return 5;
      if (pt.n === 'string' && typeof v === 'string') return 10;
      return 0;
    }

    /* ---------- objects ---------- */
    defaultVal(ty, f) {
      if (!ty) return null;
      if (ty.ref) return null;
      if (isPtrTy(ty)) return null;
      if (ty.cdims && ty.cdims.length) return this.makeCArray(ty, ty.cdims.map(d => d ? toNum(this.ev(d, this.globals)) : 0), 0);
      if (isArrTy(ty)) return null;
      const L = this.lang;
      switch (ty.n) {
        case 'int': case 'short': case 'byte': case 'ubyte': case 'char': case 'uint': case 'ushort': return ty.box && L === 'java' ? null : 0;
        case 'long': case 'ulong': return ty.box && L === 'java' ? null : 0n;
        case 'float': case 'double': return ty.box && L === 'java' ? null : 0;
        case 'bool': return ty.box && L === 'java' ? null : false;
        case 'string': return L === 'cpp' ? '' : null;
        case 'var': case 'dyn': case 'object': case 'void': case 'null': return null;
      }
      if (ty.nullable) return null;
      const ci = this.classes.get(ty.n);
      if (ci && (L === 'cpp' || L === 'c' || ci.isStruct && L === 'cs')) {
        if (ci.isEnum) return 0;
        return this.construct(ci, [], [], null, null, ty);
      }
      if (ci && ci.isEnum && L === 'cs') { this.clinit(ci); const first = ci.d.consts[0]; return first ? ci.sf.get(first.id).v : 0; }
      if (L === 'cpp' && CF.LIB.isLibType(ty.n)) return CF.LIB.make(this, ty, [], [], null);
      return null;
    }
    makeCArray(ty, dims, k) {
      const et = Object.assign({}, ty, { dim: ty.dim - k - 1, cdims: null });
      const n = dims[k];
      const a = new Array(n);
      for (let i = 0; i < n; i++) a[i] = k + 1 < dims.length ? this.makeCArray(ty, dims, k + 1) : this.defaultVal(Object.assign({}, et, { dim: 0 }));
      return new Arr(a, et);
    }
    initFields(o, ci, env) {
      if (ci.base) this.initFields(o, ci.base, env);
      for (const f of ci.fieldList) {
        if (f.static) continue;
        if (f.prop && f.prop.get && f.prop.get !== 'auto') continue;
        o.f[f.id] = this.defaultVal(f.ty, f);
      }
    }
    runFieldInits(o, ci, env) {
      for (const f of ci.fieldList) {
        if (f.static) continue;
        if (f.init) o.f[f.id] = this.convStore(f.ty, this.evInit(f.init, f.ty, env), f.init);
        else if (f.ctor && this.lang === 'cpp') o.f[f.id] = this.makeValue(f.ty, f.ctor.map(a => this.ev(a, env)), f.ctor.map(a => a.ty), f.ctor);
      }
      for (const blk of ci.d.statics || []) if (blk.$inst) this.execBlock(blk, new Env(env));
    }
    pickCtor(ci, args, argNodes, line) {
      const ks = ci.ctors.filter(k => k.body || k.init || true);
      if (!ks.length) return null;
      const k = this.pick(ks, args, argNodes.map(a => a && a.ty ? a.ty : null), line, 'constructor');
      if (!k) {
        if (!args.length && (this.lang === 'cpp' || this.lang === 'c')) return null;
        throw new CF.CompileError(`No constructor of ${ci.name} takes ${args.length} argument${args.length === 1 ? '' : 's'}`, line);
      }
      return k;
    }
    construct(ci, args, argTys, argNodes, line, ty, recvRefs, initItems, cenv) {
      if (ci.d.kind === 'interface' || (ci.d.mods && ci.d.mods.abstract && this.lang !== 'cpp')) throw new CF.CompileError(`${ci.name} is ${ci.d.kind === 'interface' ? 'an interface' : 'abstract'} and cannot be created with new`, line);
      if (ci.exc && ci.builtin) {
        const o = new Obj(ci);
        o.f.$msg = args.length ? (typeof args[0] === 'string' ? args[0] : args[0] instanceof Obj && args[0].ci.exc ? this.str(args[0]) : this.str(args[0], argTys[0])) : null;
        if (args[1] instanceof Obj) o.f.$cause = args[1];
        return o;
      }
      this.clinit(ci);
      const o = new Obj(ci);
      if (cenv) o.$cenv = cenv;
      if (ty && ty.args) o.targs = ty.args;
      this.initFields(o, ci, this.globals);
      this.runCtor(ci, o, args, argTys, argNodes || args.map(() => null), line, recvRefs);
      if (initItems) {
        const env = this.frames.length ? this.frames[this.frames.length - 1].cur : this.globals;
        for (const it of initItems) {
          if (it.id) this.setMember(o, it.id, this.ev(it.e, env), it.e.ty, line);
        }
      }
      return o;
    }
    runCtor(ci, o, args, argTys, argNodes, line, recvRefs) {
      const L = this.lang;
      let k = null;
      if (ci.ctors.length) {
        k = this.pick(ci.ctors, args, argTys, line, 'constructor');
        if (!k) throw new CF.CompileError(`No constructor of ${ci.name} takes ${args.length} argument${args.length === 1 ? '' : 's'} like this`, line || this.lastLine);
      } else if (ci.record && args.length === ci.recParams.length) {
        const env = new Env(this.globals);
        ci.recParams.forEach((p, i) => env.v.set(p.id, new Box(this.convStore(p.ty, args[i]), p.ty)));
        if (ci.base) this.runCtor(ci.base, o, [], [], [], line);
        this.runFieldInits(o, ci, env);
        if (ci.d.compact) {
          const fr = { name: ci.name + ' constructor', cls: ci, self: o, root: env, cur: env, line };
          this.frames.push(fr);
          try { this.execBlock(ci.d.compact, env, true); } finally { this.frames.pop(); }
        }
        ci.recParams.forEach(p => { o.f[p.id] = env.v.get(p.id).v; });
        return;
      } else if (args.length && !(ci.builtin)) {
        if (L === 'c' || L === 'cpp' || L === 'cs' && ci.isStruct) {
          /* aggregate initialisation: Point p = {1, 2}; */
          const fs = this.fieldNames(ci);
          args.forEach((a, i) => { if (i < fs.length) o.f[fs[i]] = this.convStore(this.fieldTy(ci, fs[i]), a); });
          return;
        }
        throw new CF.CompileError(`${ci.name} has no constructor that takes ${args.length} argument${args.length === 1 ? '' : 's'}`, line || this.lastLine);
      }
      if (!k) {
        if (ci.base && !ci.base.builtin) this.runCtor(ci.base, o, [], [], [], line);
        const env = new Env(this.globals);
        const fr = { name: ci.name + ' setup', cls: ci, self: o, root: env, cur: env, line };
        this.frames.push(fr);
        try { this.runFieldInits(o, ci, env); } finally { this.frames.pop(); }
        return;
      }
      this.runCtorBody(ci, k, o, args, argTys, line, recvRefs);
    }
    runCtorBody(ci, k, o, args, argTys, line, recvRefs) {
      const L = this.lang;
      if (++this.depth > (this.o.maxDepth || 2200)) { this.depth = 0; throw L === 'java' ? this.ex('StackOverflowError', null) : new Fatal('Stack overflow in a constructor', 'so'); }
      const env = new Env(o.$cenv || this.globals);
      const fr = { name: ci.name + ' constructor', cls: ci, self: o, root: env, cur: env, line: k.line };
      this.frames.push(fr);
      try {
        this.bindParams(k.params, args, argTys, env, recvRefs, fr);
        if (this.trace) this.step(k.line, env, 'call', { fn: fr.name });
        let body = k.body ? k.body.body : [];
        /* this(...) and super(...) as the first statement (Java), : base(...) and : this(...) in C# */
        let chained = false;
        const first = body[0];
        const isChain = s => s && s.k === 'expr' && s.e.k === 'call' && (s.e.f.k === 'super' || s.e.f.k === 'this');
        if (L === 'cs' && k.chain) {
          const a = k.chain.args.map(x => this.ev(x, env));
          const at = k.chain.args.map(x => x.ty);
          if (k.chain.kind === 'this') { this.runCtor(ci, o, a, at, k.chain.args, k.line); chained = 'this'; }
          else { this.runFieldInits(o, ci, env); if (ci.base) this.runCtor(ci.base, o, a, at, k.chain.args, k.line); chained = 'base'; }
        } else if (L === 'java' && isChain(first)) {
          if (this.trace) this.step(first.line, env);
          const a = first.e.args.map(x => this.ev(x, env));
          const at = first.e.args.map(x => x.ty);
          if (first.e.f.k === 'this') { this.runCtor(ci, o, a, at, first.e.args, first.line); chained = 'this'; }
          else { if (ci.base) { if (ci.base.exc && ci.base.builtin) { o.f.$msg = a.length ? this.str(a[0], at[0]) : null; if (a[1] instanceof Obj) o.f.$cause = a[1]; } else this.runCtor(ci.base, o, a, at, first.e.args, first.line); } chained = 'super'; }
          body = body.slice(1);
        } else if (L === 'cpp') {
          /* base class from the initialiser list, then members */
          const baseInit = ci.base && k.init.find(x => x.id === ci.base.name);
          if (ci.base) {
            if (baseInit) { const a = baseInit.args.map(x => this.ev(x, env)); if (ci.base.exc && ci.base.builtin) o.f.$msg = a.length ? this.cstr(a[0]) : ''; else this.runCtor(ci.base, o, a, baseInit.args.map(x => x.ty), baseInit.args, k.line); }
            else if (!ci.base.builtin) this.runCtor(ci.base, o, [], [], [], k.line);
          }
          for (const f of ci.fieldList) {
            if (f.static) continue;
            const ini = k.init.find(x => x.id === f.id);
            if (ini) o.f[f.id] = this.makeValue(f.ty, ini.args.map(x => this.ev(x, env)), ini.args.map(x => x.ty), ini.args);
            else if (f.init) o.f[f.id] = this.convStore(f.ty, this.evInit(f.init, f.ty, env), f.init);
          }
          chained = 'cpp';
        }
        if (!chained) {
          if (ci.base && !ci.base.builtin) this.runCtor(ci.base, o, [], [], [], k.line);
          this.runFieldInits(o, ci, env);
        } else if (chained === 'super') this.runFieldInits(o, ci, env);
        const r = this.execStmts(body, env);
        if (r instanceof Throw) throw r;
        if (this.trace) this.step(k.body && k.body.end ? k.body.end : this.lastLine, env, 'ret', { fn: fr.name, ret: null, made: this.short(o, null, 0) });
      } finally { this.frames.pop(); this.depth--; }
    }
    /* C++ values made from arguments: int x(5), vector<int> v(3, 0), Point p(1, 2) */
    makeValue(ty, args, argTys, nodes) {
      if (plain(ty) && NK[ty.n] || ty.n === 'bool' || isPtrTy(ty) || ty.ref) return args.length ? this.convStore(ty, args[0]) : this.defaultVal(ty);
      if (ty.n === 'string') {
        if (!args.length) return '';
        if (args.length === 2 && typeof args[0] !== 'string' && !(args[0] instanceof Ptr)) return chr(toNum(args[1])).repeat(toNum(args[0]));
        return this.cstr(args[0]);
      }
      const ci = this.classes.get(ty.n);
      if (ci) return this.construct(ci, args, argTys, nodes, null, ty);
      if (CF.LIB.isLibType(ty.n)) return CF.LIB.make(this, ty, args, argTys, nodes);
      return args[0];
    }

    /* ---------- conversions when a value is stored ---------- */
    conv(v, ty) {
      if (!ty || v === undefined) return v;
      if (isPtrTy(ty)) {
        if (v instanceof Arr) return new Ptr(v.a, 0, null, v.et);
        if (v instanceof Ptr && v.raw !== undefined) return this.materialize(v, ty);
        if (typeof v === 'string' && ty.n === 'char') return new Ptr(this.cchars(v), 0, null, TY.char);
        if (v === 0) return null;
        return v;
      }
      if (isArrTy(ty)) { if (v instanceof Arr && !v.et && ty) v.et = Object.assign({}, ty, { dim: ty.dim - 1 }); return v; }
      if (v === null) return v;
      switch (ty.n) {
        case 'int': return typeof v === 'string' ? v : v && v.$enum ? v.val : i32(v);
        case 'short': return (i32(v) << 16) >> 16;
        case 'byte': return (i32(v) << 24) >> 24;
        case 'ubyte': return i32(v) & 0xff;
        case 'ushort': return i32(v) & 0xffff;
        case 'char': return typeof v === 'string' ? v.charCodeAt(0) : this.lang === 'c' || this.lang === 'cpp' ? (i32(v) << 24) >> 24 : i32(v) & 0xffff;
        case 'uint': return typeof v === 'bigint' ? Number(BigInt.asUintN(32, v)) : (Math.trunc(toNum(v)) >>> 0);
        case 'long': return typeof v === 'bigint' ? BigInt.asIntN(64, v) : (Number.isFinite(toNum(v)) ? BigInt.asIntN(64, BigInt(Math.trunc(toNum(v)))) : (toNum(v) > 0 ? 9223372036854775807n : -9223372036854775808n));
        case 'ulong': return typeof v === 'bigint' ? BigInt.asUintN(64, v) : BigInt.asUintN(64, BigInt(Math.trunc(toNum(v)) || 0));
        case 'double': return typeof v === 'number' || typeof v === 'bigint' || typeof v === 'boolean' ? toNum(v) : v && v.$enum ? v.val : v;
        case 'float': return typeof v === 'number' || typeof v === 'bigint' ? Math.fround(toNum(v)) : v;
        case 'bool': return typeof v === 'boolean' ? v : (this.lang === 'c' || this.lang === 'cpp') ? (v instanceof Ptr ? true : !!toNum(v)) : v;
        case 'string': if (this.lang === 'cpp' && v instanceof Ptr) return this.cstr(v); if (this.lang === 'cpp' && typeof v === 'number') return chr(v); return v;
      }
      if (v && v.$lib && v.$setTy) v.$setTy(ty);
      return v;
    }
    materialize(p, ty) {
      const et = Object.assign({}, ty, { ptr: ty.ptr - 1 });
      const size = this.sizeOf(et) || 1;
      const n = Math.max(1, Math.floor(p.raw / size));
      const arr = p.arr;
      arr.length = 0;
      for (let i = 0; i < n; i++) arr.push(p.zero ? this.defaultVal(et) : (plain(et) && !NK[et.n] && et.n !== 'bool' ? this.defaultVal(et) : (et.ptr ? null : this.lang === 'c' && p.garbage ? 0 : this.defaultVal(et))));
      if (et.n && this.classes.get(et.n)) arr.isObj = true;
      delete p.raw;
      p.et = et;
      return p;
    }
    /* store with the language's copy rules: C and C++ copy structs, vectors and strings */
    convStore(ty, v, node, isReturn, srcTy) {
      if (ty && ty.n === 'var' && !ty.dim) return this.copyVal(v);
      if (node && ty) this.checkAssign(ty, node.ty, node);
      const out = this.conv(v, ty);
      if ((this.lang === 'cpp' || this.lang === 'c' || this.lang === 'cs') && ty && !ty.ref && plain(ty)) return this.copyVal(out);
      return out;
    }
    copyVal(v) {
      if (this.lang === 'java') return v;
      if (v instanceof Obj && (this.lang === 'cpp' || this.lang === 'c' || (this.lang === 'cs' && v.ci.isStruct))) {
        const o = new Obj(v.ci);
        for (const k in v.f) o.f[k] = this.copyVal(v.f[k]);
        if (this.lang === 'cpp') { const cc = v.ci.ctors.find(k => k.params.length === 1 && k.params[0].ty.n === v.ci.name && k.params[0].ty.ref); if (cc && cc.body) { this.runCtorBody(v.ci, cc, o, [v], [{ n: v.ci.name }], this.lastLine); } }
        return o;
      }
      if (v instanceof Arr && (this.lang === 'c' || this.lang === 'cpp') && v.std) return new Arr(v.a.map(x => this.copyVal(x)), v.et);
      if (this.lang === 'cpp' && v && v.$lib && v.$copy) return v.$copy(this);
      return v;
    }
    /* a few compile time checks that beginners meet first */
    checkAssign(target, src, node) {
      const L = this.lang;
      if (!src || !target || L === 'c' || L === 'cpp') return;
      if (!plain(target) || !plain(src)) return;
      const tk = NK[target.n], sk = NK[src.n];
      const tn = L === 'java' ? { string: 'String', bool: 'boolean' } : { bool: 'bool' };
      const nm = t => (tn[t.n] || t.n);
      if (tk && (sk === 'd' || sk === 'f') && tk !== 'd' && tk !== 'f') {
        if (L === 'java') throw new CF.CompileError(`incompatible types: possible lossy conversion from ${nm(src)} to ${nm(target)}. Write (${nm(target)}) in front to cut off the decimals on purpose`, node.line);
        throw new CF.CompileError(`Cannot implicitly convert type '${nm(src)}' to '${nm(target)}'. An explicit conversion exists (are you missing a cast?)`, node.line);
      }
      if (tk === 'f' && sk === 'd' && !(node.k === 'lit' && false)) {
        if (L === 'java') throw new CF.CompileError(`incompatible types: possible lossy conversion from double to float. Write 1.5f for a float value`, node.line);
        throw new CF.CompileError(`Literal of type double cannot be implicitly converted to type 'float'. Use an 'F' suffix to create a literal of this type`, node.line);
      }
      if ((tk === 'i') && (sk === 'l') && !(node.k === 'lit')) {
        if (target.n === 'char' || target.n === 'byte' || target.n === 'short') return;
        if (L === 'java') throw new CF.CompileError(`incompatible types: possible lossy conversion from long to ${nm(target)}`, node.line);
        throw new CF.CompileError(`Cannot implicitly convert type 'long' to '${nm(target)}'. An explicit conversion exists (are you missing a cast?)`, node.line);
      }
      if ((tk && src.n === 'string') || (target.n === 'string' && sk) || (tk && src.n === 'bool') || (target.n === 'bool' && sk)) {
        if (L === 'java') throw new CF.CompileError(`incompatible types: ${nm(src)} cannot be converted to ${nm(target)}`, node.line);
        throw new CF.CompileError(`Cannot implicitly convert type '${nm(src)}' to '${nm(target)}'`, node.line);
      }
    }
    evInit(init, ty, env) {
      if (init.k === 'arr' && !init.coll) {
        if (isArrTy(ty) || (this.lang !== 'cs' && this.lang !== 'java' && !CF.LIB.isLibType(ty.n) && !this.classes.get(ty.n))) return this.arrayFrom(init, ty, env);
        /* C++ brace lists: vector<int> v = {1, 2, 3};  Point p = {1, 2}; */
        /* map<string, int> m = {{"Ann", 9}}: each inner list is a key and value pair */
        const isMap = /^(map|unordered_map|multimap)$/.test(ty.n);
        const vals = init.items.map(x => x.k === 'arr' ? (isMap ? this.ev(x, env) : this.evInit(x, (ty.args && ty.args[0]) || TY.dyn, env)) : this.ev(x, env));
        const ci = this.classes.get(ty.n);
        if (ci) return this.construct(ci, vals, init.items.map(x => x.ty), init.items, init.line, ty);
        return CF.LIB.make(this, ty, [], [], null, vals, init.items.map(x => x.ty));
      }
      if (init.k === 'arr' && init.coll) {
        const vals = init.items.map(x => this.ev(x, env));
        if (isArrTy(ty)) return new Arr(vals.map(v => this.conv(v, Object.assign({}, ty, { dim: ty.dim - 1 }))), Object.assign({}, ty, { dim: ty.dim - 1 }));
        return CF.LIB.make(this, ty, [], [], null, vals, init.items.map(x => x.ty));
      }
      if (init.k === 'new' && !init.tt) init.target = ty;
      if ((this.lang === 'c' || this.lang === 'cpp') && ty.n === 'char' && !ty.ptr && (isArrTy(ty) || (ty.cdims && ty.cdims.length)) && init.k === 'lit' && typeof init.v === 'string') {
        const want = ty.cdims && ty.cdims[0] ? toNum(this.ev(ty.cdims[0], env)) : 0;
        if (want && init.v.length > want) throw new CF.CompileError(`The text "${init.v}" needs ${init.v.length + 1} chars with the ending zero, but the array holds ${want}`, init.line);
        return new Arr(this.cchars(init.v, want), TY.char);
      }
      const v = this.ev(init, env);
      return v;
    }
    arrayFrom(init, ty, env, depth = 0) {
      const et = Object.assign({}, ty, { dim: Math.max(0, (ty.dim || 1) - 1), cdims: ty.cdims ? ty.cdims.slice(1) : null });
      if (!et.cdims || !et.cdims.length) delete et.cdims;
      const a = [];
      for (const it of init.items) {
        if (it.k === 'arr') a.push(et.dim ? this.arrayFrom(it, et, env, depth + 1) : (this.classes.get(et.n) ? this.construct(this.classes.get(et.n), it.items.map(x => this.ev(x, env)), it.items.map(x => x.ty), it.items, it.line, et) : this.evInit(it, et, env)));
        else if (it.k === 'desig') continue;
        else if (typeof (it.k === 'lit' && it.v) === 'string' && et.n === 'char' && !et.dim && (this.lang === 'c' || this.lang === 'cpp') && init.items.length === 1) return new Arr(this.cchars(it.v), TY.char);
        else a.push(this.convStore(et, this.ev(it, env), it));
      }
      /* C: int a[5] = {1, 2}; fills the rest with zeros */
      const want = ty.cdims && ty.cdims[0] ? toNum(this.ev(ty.cdims[0], env)) : null;
      if (want !== null) {
        if (a.length > want) throw new CF.CompileError(`Too many values for an array of ${want}`, init.line);
        while (a.length < want) a.push(et.dim && et.cdims ? this.makeCArray(et, et.cdims.map(d => d ? toNum(this.ev(d, env)) : 0), 0) : this.defaultVal(Object.assign({}, et, { cdims: null })));
      }
      return new Arr(a, et);
    }

    /* ---------- statements ---------- */
    execBlock(b, env, sameEnv) {
      const e = sameEnv ? env : new Env(env);
      return this.execStmts(b.body, e);
    }
    execStmts(list, env) {
      for (let i = 0; i < list.length; i++) {
        const r = this.exec(list[i], env);
        if (r !== undefined) return r;
      }
      return undefined;
    }
    exec(s, env) {
      switch (s.k) {
        case 'block': return this.execBlock(s, env);
        case 'empty': return undefined;
        case 'localfn': {
          const fr = this.frame();
          const fn = new Fn({ params: s.m.params, body: s.m.body, closure: env, ret: s.m.ret, name: s.m.name, fname: s.m.name, line: s.m.line, self: fr && fr.self, cls: fr && fr.cls });
          env.v.set(s.m.name, new Box(fn, TY.dyn));
          return undefined;
        }
      }
      this.step(s.line, env);
      switch (s.k) {
        case 'expr': this.ev(s.e, env); return undefined;
        case 'decl': this.execDecl(s, env); return undefined;
        case 'if': {
          const c = this.truthy(this.ev(s.c, env), s.c);
          if (c) return this.exec(s.a, new Env(env));
          if (s.b) return this.exec(s.b, new Env(env));
          return undefined;
        }
        case 'while': {
          for (;;) {
            if (!this.truthy(this.ev(s.c, env), s.c)) break;
            const r = this.exec(s.body, new Env(env));
            if (r !== undefined) {
              if (r instanceof Brk && (!r.label || r.label === s.label)) break;
              if (r instanceof Cont && (!r.label || r.label === s.label)) { this.step(s.line, env); continue; }
              return r;
            }
            this.step(s.line, env);
          }
          return undefined;
        }
        case 'do': {
          for (;;) {
            const r = this.exec(s.body, new Env(env));
            if (r !== undefined) {
              if (r instanceof Brk && (!r.label || r.label === s.label)) break;
              if (!(r instanceof Cont && (!r.label || r.label === s.label))) return r;
            }
            this.step(s.wl || s.line, env);
            if (!this.truthy(this.ev(s.c, env), s.c)) break;
          }
          return undefined;
        }
        case 'for': {
          const fe = new Env(env);
          if (s.init) { if (s.init.k === 'decl') this.execDecl(s.init, fe); else s.init.es.forEach(e => this.ev(e, fe)); }
          for (;;) {
            if (s.c && !this.truthy(this.ev(s.c, fe), s.c)) break;
            const r = this.exec(s.body, new Env(fe));
            if (r !== undefined) {
              if (r instanceof Brk && (!r.label || r.label === s.label)) break;
              if (!(r instanceof Cont && (!r.label || r.label === s.label))) return r;
            }
            this.step(s.line, fe);
            for (const u of s.upd) this.ev(u, fe);
          }
          return undefined;
        }
        case 'foreach': return this.execForeach(s, env);
        case 'ret': {
          if (!s.e) return new Ret(undefined);
          const v = this.ev(s.e, env);
          const fr = this.frames[this.frames.length - 1];
          return new Ret(v);
        }
        case 'brk': return s.label ? new Brk(s.label) : BRKI;
        case 'cont': return s.label ? new Cont(s.label) : CONTI;
        case 'yield': return new Yield(this.ev(s.e, env), s.e.ty);
        case 'switch': return this.execSwitch(s, env);
        case 'throw': {
          if (!s.e) { const cur = env.lookup('$exc'); if (cur) throw cur.v; throw new Fatal('throw; with nothing to rethrow'); }
          const v = this.ev(s.e, env);
          if (v === null && this.lang === 'java') throw this.ex('NullPointerException', 'Cannot throw a null exception');
          throw new Throw(v, s.line);
        }
        case 'try': return this.execTry(s, env);
        default: throw new Fatal('Unknown statement ' + s.k);
      }
    }
    execDecl(d, env, isGlobal) {
      for (const v of d.vars) {
        if (v.bind) { /* auto [a, b] = pair;  var (x, y) = tuple; */
          const val = this.ev(v.init, env);
          const parts = CF.LIB.unpack(this, val, v.bind.length);
          v.bind.forEach((id, i) => env.v.set(id, new Box(parts[i][0], parts[i][1])));
          continue;
        }
        let ty = v.ty;
        if (ty.tp) ty = this.resolveTy(ty);
        if (env.v.has(v.id) && !isGlobal && !(this.lang === 'c' || this.lang === 'cpp') && env.v.get(v.id).declLine !== v.line) {
          throw new CF.CompileError(this.lang === 'java' ? `variable ${v.id} is already defined in this method` : `A local variable named '${v.id}' is already defined in this scope`, d.line);
        }
        if ((this.lang === 'java' || this.lang === 'cs') && !isGlobal) {
          for (let e = env.p; e; e = e.p) { if (e.fnRoot) break; if (e.v.has(v.id) && !e.isGlobal) throw new CF.CompileError(this.lang === 'java' ? `variable ${v.id} is already defined in this method` : `A local variable named '${v.id}' cannot be declared in this scope because it would give a different meaning to '${v.id}'`, d.line); if (e === this.frames[this.frames.length - 1]?.root) break; }
        }
        let val, box;
        if (v.init) {
          if (ty.ref && this.lang === 'cpp') {
            const r = this.ref(v.init, env);
            box = new RefBox(r, ty);
            env.v.set(v.id, box);
            continue;
          }
          val = this.evInit(v.init, ty, env);
          if (ty.n === 'var' && !ty.dim) ty = varTy(v.init.ty, val);
          if (this.lang === 'cpp' && val instanceof Arr && !ty.dim && !isPtrTy(ty) && CF.LIB.isLibType(ty.n)) val = CF.LIB.make(this, ty, [], [], null, val.a, []);
          val = this.convStore(ty, val, v.init.k === 'arr' ? null : v.init);
          if (val && val.$lib && val.$setTy) val.$setTy(ty);
        } else if (v.ctor) {
          if (v.brace && CF.LIB.isLibType(ty.n)) { const vals = v.ctor.map(a => a.k === 'arr' ? this.evInit(a, (ty.args && ty.args[0]) || TY.dyn, env) : this.ev(a, env)); val = CF.LIB.make(this, ty, [], [], null, vals, v.ctor.map(a => a.ty)); }
          else val = this.makeValue(ty, v.ctor.map(a => this.ev(a, env)), v.ctor.map(a => a.ty), v.ctor);
        } else {
          val = this.defaultVal(ty);
          box = new Box(val, ty);
          if ((this.lang === 'java' || this.lang === 'cs' || ((this.lang === 'c' || this.lang === 'cpp') && plain(ty) && (NK[ty.n] || ty.n === 'bool'))) && !isGlobal && !ty.cdims) box.uninit = true;
        }
        if (!box) box = new Box(val, ty);
        box.declLine = v.line;
        if (d.konst) box.konst = true;
        env.v.set(v.id, box);
      }
    }
    execForeach(s, env) {
      const it = this.ev(s.it, env);
      if (it === null || it === undefined) {
        if (this.lang === 'java') throw this.ex('NullPointerException', `Cannot iterate over ${s.it.k === 'name' ? '"' + s.it.id + '"' : 'the value'} because it is null`);
        throw this.ex('NullReferenceException', 'Object reference not set to an instance of an object.');
      }
      const items = CF.LIB.iterate(this, it, s.it.ty, s.ty && s.ty.ref);
      let elTy = s.ty;
      for (let k = 0; k < items.length; k++) {
        const [val, ety, ref] = items[k];
        const fe = new Env(env);
        let ty = elTy && elTy.n !== 'var' ? elTy : (ety || valTy(val));
        if (Array.isArray(s.id)) {
          const parts = CF.LIB.unpack(this, val, s.id.length);
          s.id.forEach((id, i) => fe.v.set(id, new Box(parts[i][0], parts[i][1])));
        } else if (elTy && elTy.ref && ref) fe.v.set(s.id, new RefBox(ref, ty));
        else fe.v.set(s.id, new Box(this.convStore(ty, val), ty));
        if (k > 0) this.step(s.line, fe);
        const r = this.exec(s.body, fe);
        if (r !== undefined) {
          if (r instanceof Brk && (!r.label || r.label === s.label)) break;
          if (!(r instanceof Cont && (!r.label || r.label === s.label))) return r;
        }
      }
      return undefined;
    }
    caseMatches(test, v, vty, env, swEnv) {
      if (test.k === 'pat') return this.patMatch(test.pat, v, vty, swEnv || env);
      /* Java enum cases are written without the class name: case RED: */
      if (test.k === 'name' && v instanceof Obj && v.ci.isEnum) return v.f.$name === test.id;
      if (test.k === 'name' && v && v.$enum && v.$enum.sf.has(test.id)) return v.name === test.id;
      const c = this.ev(test, env);
      if (v && v.$enum) return c && c.$enum ? c.name === v.name : v.val == c;
      if (typeof v === 'string' && this.lang === 'java' && typeof c !== 'string') return false;
      return v == c || this.equals(v, c);
    }
    patMatch(pat, v, vty, env) {
      if (!pat) return true;
      if (pat.and) return pat.and.every(x => this.patMatch(x, v, vty, env));
      if (pat.or) return pat.or.some(x => this.patMatch(x, v, vty, env));
      if (pat.not) return !this.patMatch(pat.not, v, vty, env);
      if (pat.rel) { const c = this.ev(pat.e, env); return { '<': v < c, '>': v > c, '<=': v <= c, '>=': v >= c }[pat.rel]; }
      if (pat.ty) {
        const ok = this.instOf(v, pat.ty);
        if (ok && pat.bind) env.v.set(pat.bind, new Box(v, pat.ty));
        return ok;
      }
      const c = this.ev(pat.e, env);
      if (pat.e.k === 'name' && v instanceof Obj && v.ci.isEnum) return v.f.$name === pat.e.id;
      if (v && v.$enum) return c && c.$enum ? c.name === v.name : v.val == c;
      return v == c || this.equals(v, c);
    }
    execSwitch(s, env) {
      const v = this.ev(s.e, env);
      if (v === null && this.lang === 'java') throw this.ex('NullPointerException', null);
      const vty = s.e.ty;
      const se = new Env(env);
      let start = -1;
      for (let i = 0; i < s.cases.length && start < 0; i++) {
        const c = s.cases[i];
        if (c.tests === null) continue;
        for (const t of c.tests) { if (t && this.caseMatches(t, v, vty, se, se) && (!c.tests.guard || this.truthy(this.ev(c.tests.guard, se)))) { start = i; break; } }
        if (c.tests.includes(null) && start < 0) { /* case null, default */ }
      }
      if (start < 0) start = s.cases.findIndex(c => c.tests === null || c.tests.includes(null));
      if (start < 0) return undefined;
      for (let i = start; i < s.cases.length; i++) {
        const c = s.cases[i];
        const r = this.execStmts(c.body, se);
        if (r !== undefined) {
          if (r === BRKI) return undefined;
          if (r instanceof Yield) return r;
          return r;
        }
        if (c.arrow || s.arrow) return undefined;
        if (this.lang === 'cs' && c.body.length) throw new CF.CompileError(`Control cannot fall through from one case label ('case ...:') to another. End each case with break;`, c.line);
      }
      return undefined;
    }
    execTry(s, env) {
      let pending = null, result;
      try {
        result = this.execBlock(s.body, env);
      } catch (e) {
        let exv = null;
        if (e instanceof Throw) exv = e;
        else if (e instanceof Fatal && (this.lang === 'java' || this.lang === 'cs') && e.kind === 'so') exv = this.ex(this.lang === 'java' ? 'StackOverflowError' : 'StackOverflowException', null);
        else throw e;
        const val = exv.val;
        let handled = false;
        for (const c of s.catches) {
          if (this.catchMatches(c, val)) {
            const ce = new Env(env);
            if (c.id) ce.v.set(c.id, new Box(val, c.types[0]));
            ce.v.set('$exc', new Box(exv, TY.dyn));
            if (c.when && !this.truthy(this.ev(c.when, ce))) continue;
            handled = true;
            if (this.trace) this.step(c.line, ce, 'catch', { msg: this.lang === 'cpp' && !(val instanceof Obj) ? 'caught ' + this.str(val) : 'caught ' + (val instanceof Obj ? this.qualEx(val.ci).replace(/^(java\.\w+\.|System\.(\w+\.)*)/, '') : this.str(val)) });
            try { result = this.execBlock(c.body, ce, true); }
            catch (e2) { pending = e2; }
            break;
          }
        }
        if (!handled) pending = exv;
      }
      if (s.fin) {
        const r = this.execBlock(s.fin, env);
        if (r !== undefined) return r;
      }
      if (pending) throw pending;
      return result;
    }
    catchMatches(c, val) {
      if (!c.types.length) return true;
      for (const t of c.types) {
        if (t.n === '...') return true;
        if (val instanceof Obj) {
          if (this.isA(val.ci, t.n) || t.n === 'Exception' && this.lang === 'cs' || t.n === 'Throwable' || (t.n === 'exception' && this.lang === 'cpp' && val.ci.exc)) return true;
          if (t.n === 'Exception' && this.lang === 'java' && val.ci.exc && !this.isA(val.ci, 'Error')) return true;
        } else {
          const vt = valTy(val);
          if (this.lang === 'cpp' && (t.n === vt.n || (t.n === 'string' && typeof val === 'string') || (t.n === 'char' && t.ptr && (typeof val === 'string' || val instanceof Ptr)))) return true;
        }
      }
      return false;
    }
    truthy(v, node) {
      if (typeof v === 'boolean') return v;
      if (this.lang === 'java' || this.lang === 'cs') {
        if (v === null && node) throw this.ex(this.lang === 'java' ? 'NullPointerException' : 'NullReferenceException', null);
        if (typeof v === 'number' && node) throw new CF.CompileError(this.lang === 'java' ? 'incompatible types: int cannot be converted to boolean. A condition must be true or false, for example x != 0' : "Cannot implicitly convert type 'int' to 'bool'", node.line);
      }
      if (v === null || v === undefined) return false;
      if (typeof v === 'bigint') return v !== 0n;
      if (typeof v === 'number') return v !== 0;
      if (v && v.kind === 'in') return !v.fail;
      if (v && v.$lib && v.$truthy) return v.$truthy();
      return true;
    }
  }
  const BRKI = new Brk(null), CONTI = new Cont(null);
  class Yield { constructor(v, ty) { this.v = v; this.ty = ty; } }
  CF.Yield = Yield; CF.Ret = Ret;
  function safeGet(b) { try { return b.v; } catch (e) { return undefined; } }
  function chr(c) { return typeof c === 'string' ? c : String.fromCharCode(((c % 65536) + 65536) % 65536); }
  CF.chr = chr;
  function elemTy(a) { return a.et || null; }
  function valTy(v) {
    if (v === null || v === undefined) return TY.null;
    switch (typeof v) {
      case 'number': return Number.isInteger(v) ? TY.int : TY.double;
      case 'bigint': return TY.long;
      case 'string': return TY.string;
      case 'boolean': return TY.bool;
    }
    if (v instanceof Arr) return Object.assign({}, v.et || TY.dyn, { dim: ((v.et && v.et.dim) || 0) + 1 });
    if (v instanceof Obj) return { n: v.ci.name };
    if (v instanceof Ptr) return Object.assign({}, v.et || TY.dyn, { ptr: ((v.et && v.et.ptr) || 0) + 1 });
    if (v && v.$lib && v.$ty) return v.$ty();
    return TY.dyn;
  }
  function varTy(t, v) {
    if (t && t.n !== 'null' && t.n !== 'dyn' && t.n !== 'var') return Object.assign({}, t, { ref: false });
    return valTy(v);
  }
  function csTypeName(t) { if (!t) return 'Object'; return { int: 'Int32', long: 'Int64', double: 'Double', string: 'String', char: 'Char', bool: 'Boolean', float: 'Single' }[t.n] || t.n; }
  function markInitBlocks(d) {
    /* static { } blocks and plain { } instance blocks were both put in d.statics by the reader */
    if (d.$marked) return; d.$marked = true;
  }
  CF.valTy = valTy; CF.varTy = varTy; CF.kindOf = kindOf; CF.promote = promote; CF.KT = KT; CF.NK = NK; CF.toNum = toNum; CF.toBig = toBig; CF.SIZE = SIZE;
  CF.isArrTy = isArrTy; CF.isPtrTy = isPtrTy; CF.plain = plain; CF.Brk = Brk; CF.Cont = Cont; CF.BRKI = BRKI; CF.StopRun = StopRun; CF.ExitSig = ExitSig; CF.strHash = strHash; CF.dblHash = dblHash;

  /* ---------- scopes ---------- */
  class Env {
    constructor(p) { this.p = p; this.v = new Map(); }
    lookup(id) { for (let e = this; e; e = e.p) { const b = e.v.get(id); if (b) return b; } return null; }
  }
  CF.Env = Env;

  const EXC_BASE = {
    java: { Throwable: null, Exception: 'Throwable', Error: 'Throwable', RuntimeException: 'Exception', ArithmeticException: 'RuntimeException', IndexOutOfBoundsException: 'RuntimeException',
      ArrayIndexOutOfBoundsException: 'IndexOutOfBoundsException', StringIndexOutOfBoundsException: 'IndexOutOfBoundsException', NullPointerException: 'RuntimeException',
      IllegalArgumentException: 'RuntimeException', NumberFormatException: 'IllegalArgumentException', IllegalStateException: 'RuntimeException', ClassCastException: 'RuntimeException',
      UnsupportedOperationException: 'RuntimeException', ConcurrentModificationException: 'RuntimeException', NoSuchElementException: 'RuntimeException', InputMismatchException: 'NoSuchElementException',
      NegativeArraySizeException: 'RuntimeException', IOException: 'Exception', FileNotFoundException: 'IOException', InterruptedException: 'Exception', CloneNotSupportedException: 'Exception',
      StackOverflowError: 'Error', OutOfMemoryError: 'Error', AssertionError: 'Error', IllegalFormatConversionException: 'IllegalArgumentException', MissingFormatArgumentException: 'IllegalArgumentException',
      DateTimeException: 'RuntimeException', EmptyStackException: 'RuntimeException' },
    cs: { Exception: null, SystemException: 'Exception', ArithmeticException: 'SystemException', DivideByZeroException: 'ArithmeticException', OverflowException: 'ArithmeticException',
      IndexOutOfRangeException: 'SystemException', NullReferenceException: 'SystemException', ArgumentException: 'SystemException', ArgumentOutOfRangeException: 'ArgumentException',
      ArgumentNullException: 'ArgumentException', FormatException: 'SystemException', InvalidOperationException: 'SystemException', KeyNotFoundException: 'SystemException',
      InvalidCastException: 'SystemException', NotImplementedException: 'SystemException', NotSupportedException: 'SystemException', StackOverflowException: 'SystemException',
      ApplicationException: 'Exception', IOException: 'SystemException' },
    c: {},
    cpp: { exception: null, logic_error: 'exception', runtime_error: 'exception', out_of_range: 'logic_error', invalid_argument: 'logic_error', length_error: 'logic_error',
      domain_error: 'logic_error', overflow_error: 'runtime_error', underflow_error: 'runtime_error', range_error: 'runtime_error', bad_alloc: 'exception' }
  };
  const JAVA_PKG = { InputMismatchException: 'java.util', NoSuchElementException: 'java.util', ConcurrentModificationException: 'java.util', IOException: 'java.io', FileNotFoundException: 'java.io',
    IllegalFormatConversionException: 'java.util', MissingFormatArgumentException: 'java.util', EmptyStackException: 'java.util' };
  const CS_PKG = { KeyNotFoundException: 'System.Collections.Generic', IOException: 'System.IO' };
  CF.EXC_BASE = EXC_BASE;
  const CSENUM = {
    $str() { return this.name; }, $short() { return this.$enum.name + '.' + this.name; }, $eq(b) { return b && b.$enum === this.$enum && b.name === this.name || b === this.val; },
    $hash() { return this.val; }, valueOf() { return this.val; }, $ty() { return { n: this.$enum.name }; }
  };
  CF.CSENUM = CSENUM;

  CF.Interp = Interp;

  /* ---------- run a whole program ---------- */
  CF.run = function (src, lang, opts = {}) {
    objIds = 0;
    const res = { out: [], trace: null, error: null, compile: null, notes: [] };
    let I;
    try {
      const prog = CF.parse(src, lang);
      const warn = CF.check ? CF.check(prog, lang, src) : [];
      I = new Interp(prog, lang, opts);
      if (warn.length) I.notes.push(...warn);
      if (opts.trace) I.trace = [];
      try {
        const rv = I.main();
        if ((lang === 'c' || lang === 'cpp') && typeof rv === 'number' && rv !== 0) res.exit = rv;
      } catch (e) {
        CF.report(I, e, res);
      }
      if (I.trace && !res.stopped) {
        I.trace.push({ line: I.lastLine, ev: 'end', out: I.outLen, stack: [], globals: I.snapGlobals() });
      }
      res.out = I.out; res.trace = I.trace; res.notes = I.notes;
    } catch (e) {
      if (e instanceof CF.CompileError) { res.compile = { msg: e.message, line: e.line, hint: e.hint || (CF.hintFor ? CF.hintFor(lang, e.message) : null) }; if (I) { res.out = I.out; res.trace = I.trace; } }
      else { res.error = { msg: 'The playground itself tripped: ' + (e && e.message), line: I ? I.lastLine : 0, internal: true }; if (I) { res.out = I.out; res.trace = I.trace; } }
    }
    return res;
  };
  CF.report = function (I, e, res) {
    const L = I.lang;
    if (e instanceof CF.CompileError) throw e;
    if (e instanceof ExitSig) { res.exit = e.code; return; }
    if (e instanceof StopRun) { res.stopped = e.why; return; }
    if (e instanceof RangeError && /call stack/i.test(e.message)) e = L === 'java' ? I.ex('StackOverflowError', null) : new Fatal(L === 'cs' ? 'Stack overflow. The method keeps calling itself without reaching a base case' : 'Segmentation fault (stack overflow). The function keeps calling itself without reaching a base case', 'so');
    const line = e instanceof Throw ? e.line : I.lastLine;
    let text;
    if (e instanceof Throw) {
      const v = e.val;
      if (L === 'java') {
        text = 'Exception in thread "main" ' + (v instanceof Obj ? I.objStrPlain(v) : I.str(v)) + '\n\tat Main.main(Main.java:' + line + ')';
      } else if (L === 'cs') {
        text = 'Unhandled exception. ' + (v instanceof Obj ? I.objStrPlain(v) : I.str(v)) + '\n   at Program.Main(' + (I.mainArgs ? 'String[] args' : '') + ') in Program.cs:line ' + line;
      } else {
        const what = v instanceof Obj ? (v.ci.exc ? (v.f.$msg ?? '') : null) : null;
        const tn = v instanceof Obj ? (v.ci.builtin ? 'std::' + v.ci.name : v.ci.name) : typeof v === 'string' ? 'char const*' : valTy(v).n === 'double' ? 'double' : valTy(v).n;
        text = `terminate called after throwing an instance of '${tn}'` + (what !== null && v instanceof Obj && I.isExc(v.ci) ? `\n  what():  ${what}` : '') + '\nAborted (core dumped)';
      }
    } else if (e instanceof Fatal) {
      text = e.message;
      if (e.kind === 'fpe') text = 'Floating point exception (core dumped)\n' + e.message;
      if (e.kind === 'segv') text = 'Segmentation fault (core dumped)\n' + e.message;
    } else throw e;
    I.write((I.outLen && !I.out[I.out.length - 1].s.endsWith('\n') ? '\n' : '') + text + '\n', true);
    res.error = { msg: text, line };
    if (I.trace) I.trace.push({ line, ev: 'error', out: I.outLen, stack: I.frames.map(f => I.snapFrame(f)), msg: text });
  };
})();
