/* ===== Code Playground: expressions for Java, C#, C and C++ =====
   Every expression is worked out here: arithmetic with each language's integer rules, strings, calls,
   objects, arrays, pointers, lambdas and the C++ stream operators << and >>.
   Each node remembers its type in node.ty after it runs, so 7 / 2 gives 3 and 7.0 / 2 gives 3.5. */
(() => {
  const G = typeof self !== 'undefined' ? self : globalThis;
  const CF = G.CF;
  const { Arr, Obj, Fn, Ptr, Box, RefBox, ClassRef, NS, Fatal, Throw, TY, Env } = CF;
  const { kindOf, promote, KT, NK, toNum, toBig, isArrTy, isPtrTy, plain, valTy, varTy, chr, SIZE, i32 } = CF;
  const P = CF.Interp.prototype;
  const LIB = () => CF.LIB;

  const LITS = new Map();
  function litVal(n, lang) {
    if (n.v !== undefined && !n.num) return n.v;
    if (n.$v !== undefined) return n.$v;
    const t = n.num;
    let v;
    const big = () => t.startsWith('0b') ? BigInt(t) : t.startsWith('0o') ? BigInt(t) : BigInt(t);
    switch (n.kind) {
      case 'int': {
        const b = big();
        if ((lang === 'java' || lang === 'cs') && !/^0[xbo]/i.test(t) && b > 2147483647n) {
          if (lang === 'cs' && b <= 9223372036854775807n) { n.kind = 'long'; v = b; n.ty = TY.long; n.$v = v; return v; }
          throw new CF.CompileError(lang === 'java' ? `integer number too large: ${t}. Add L at the end to make it a long` : `Integral constant is too large`, n.line);
        }
        if (lang === 'cs' && /^0[xb]/i.test(t) && b > 2147483647n) { n.kind = b > 4294967295n ? 'long' : 'uint'; v = n.kind === 'long' ? b : Number(b); n.ty = TY[n.kind]; n.$v = v; return v; }
        v = Number(BigInt.asIntN(32, b)); n.ty = TY.int; break;
      }
      case 'uint': v = Number(BigInt.asUintN(32, big())); n.ty = TY.uint; break;
      case 'long': v = BigInt.asIntN(64, big()); n.ty = TY.long; break;
      case 'ulong': v = BigInt.asUintN(64, big()); n.ty = TY.ulong; break;
      case 'float': v = Math.fround(parseFloat(t)); n.ty = TY.float; break;
      default: v = /^0x/i.test(t) ? parseInt(t, 16) : parseFloat(t); n.ty = TY.double;
    }
    n.$v = v;
    return v;
  }
  const LVAL = new Set(['name', 'mem', 'idx', 'deref', 'paren']);
  const isLval = n => n && LVAL.has(n.k) && (n.k !== 'paren' || isLval(n.a));

  P.notFound = function (id, line) {
    const L = this.lang;
    const msg = L === 'java' ? `cannot find symbol: ${id}. Check the spelling and that it is declared before this line`
      : L === 'cs' ? `The name '${id}' does not exist in the current context`
      : `'${id}' was not declared in this scope`;
    throw new CF.CompileError(msg, line);
  };
  P.frame = function () { return this.frames[this.frames.length - 1]; };

  /* ---------- names ---------- */
  P.findField = function (ci, id) {
    for (let c = ci; c; c = c.base) { const f = c.fieldList.find(x => x.id === id); if (f) return { f, c }; }
    return null;
  };
  P.staticBox = function (ci, id) {
    for (let c = ci; c; c = c.base) {
      if (c.builtin) continue;
      if (!c.sinit) this.clinit(c);
      const b = c.sf.get(id);
      if (b) return b;
    }
    return null;
  };
  P.lookupBox = function (id, env, node) {
    const b = env.lookup(id);
    if (b) return { box: b };
    const fr = this.frame();
    if (fr && fr.self instanceof Obj) {
      const o = fr.self;
      const ff = this.findField(o.ci, id);
      if (ff && !ff.f.static) {
        if (ff.f.prop && ff.f.prop.get && ff.f.prop.get !== 'auto') return { prop: ff.f, obj: o };
        return { obj: o, key: id, ty: ff.f.ty };
      }
    }
    for (let ci = fr && fr.cls; ci; ci = ci.outer) {
      const sb = this.staticBox(ci, id);
      if (sb) {
        if (sb.prop) return { prop: { prop: sb.prop, ty: sb.ty, id }, obj: null, ci };
        return { box: sb };
      }
      if (fr.self && !(fr.self instanceof Obj)) break;
    }
    return null;
  };
  P.lookupName = function (n, env) {
    const id = n.id;
    const r = this.lookupBox(id, env, n);
    if (r) {
      if (r.box) {
        const b = r.box;
        if (b.uninit) {
          if (this.lang === 'java') throw new CF.CompileError(`variable ${id} might not have been initialized. Give it a value before you use it`, n.line);
          if (this.lang === 'cs') throw new CF.CompileError(`Use of unassigned local variable '${id}'`, n.line);
          this.warn('uninit:' + id, `${id} was used before it was given a value (line ${n.line}). In C and C++ that reads whatever was left in memory, so a real run may show a random number. The playground used 0.`);
          b.uninit = false;
        }
        n.ty = b.ty && b.ty.n === 'var' ? valTy(b.v) : b.ty;
        if (b.ty && b.ty.ref) n.ty = Object.assign({}, b.ty, { ref: false });
        return b.v;
      }
      if (r.prop) { n.ty = r.prop.ty; return this.getProp(r.obj, r.prop, r.ci); }
      n.ty = r.ty;
      const v = r.obj.f[r.key];
      return v;
    }
    /* functions as values: C function pointers, C# method groups */
    if (this.funcs.has(id)) { const list = this.funcs.get(id); n.ty = TY.dyn; return new Fn({ fname: id, overloads: list, native: null }); }
    const fr = this.frame();
    for (let ci = fr && fr.cls; ci; ci = ci.outer) {
      const ms = ci.methods && ci.methods.get(id);
      if (ms && !(this.classes.get(id))) { n.ty = TY.dyn; return new Fn({ fname: id, overloads: ms, self: fr.self, cls: ci }); }
    }
    const ci = this.classes.get(id) || (this.exClass(id));
    if (ci) { n.ty = TY.dyn; return new ClassRef(ci); }
    const lib = LIB().name(this, id, n);
    if (lib !== undefined) { n.ty = lib[1]; return lib[0]; }
    /* C library functions passed as values: transform(s.begin(), s.end(), s.begin(), ::toupper) */
    if ((this.lang === 'c' || this.lang === 'cpp') && /^(toupper|tolower|isdigit|isalpha|isalnum|isspace|isupper|islower|ispunct|abs|sqrt)$/.test(id)) {
      n.ty = TY.dyn;
      const I = this;
      return new Fn({ fname: id, native: (args, tys) => { const r = LIB().callGlobal(I, id, args, tys || args.map(a => valTy(a)), [], { line: n.line, args: [] }, I.globals); return r[0]; } });
    }
    this.notFound(id, n.line);
  };
  P.getProp = function (o, f, ci) {
    const pr = f.prop;
    if (pr.get === 'auto' || !pr.get) return o ? o.f[f.id] : ci.sf.get(f.id).v;
    const env = new Env(this.globals);
    const fr = { name: (o ? o.ci.name : ci.name) + '.' + f.id, cls: o ? o.ci : ci, self: o, root: env, cur: env, line: f.line };
    this.frames.push(fr);
    try { const r = this.execBlock(pr.get, env, true); return r instanceof CF.Ret ? this.conv(r.v, f.ty) : undefined; } finally { this.frames.pop(); }
  };
  P.setProp = function (o, f, v, ci) {
    const pr = f.prop;
    if (pr.set === 'auto' || (!pr.set && pr.get === 'auto')) { if (o) o.f[f.id] = this.conv(v, f.ty); else ci.sf.get(f.id).v = v; return; }
    if (!pr.set) throw new CF.CompileError(`Property or indexer '${f.id}' cannot be assigned to, it is read only`, this.lastLine);
    const env = new Env(this.globals);
    env.v.set('value', new Box(v, f.ty));
    const fr = { name: (o ? o.ci.name : ci.name) + '.' + f.id, cls: o ? o.ci : ci, self: o, root: env, cur: env, line: f.line };
    this.frames.push(fr);
    try { this.execBlock(pr.set, env, true); } finally { this.frames.pop(); }
  };

  /* ---------- places you can store into ---------- */
  P.ref = function (n, env) {
    switch (n.k) {
      case 'paren': return this.ref(n.a, env);
      case 'name': {
        const r = this.lookupBox(n.id, env, n);
        if (!r) {
          if (this.lang === 'cpp' || this.lang === 'c') { const lib = LIB().name(this, n.id, n); if (lib && lib[0] && lib[0].kind) return { get: () => lib[0], set: () => {}, ty: lib[1] }; }
          const v = this.ev(n, env); /* a function or library name used as a value */
          return { get: () => v, set: () => { throw new CF.CompileError(`${n.id} cannot be assigned to`, n.line); }, ty: n.ty, rvalue: true };
        }
        if (r.box) {
          const b = r.box, I = this, L = this.lang;
          return { box: b, ty: b.ty, name: n.id, get() { return b.v; }, set(v) {
            if (b.konst && !b.initing) throw new CF.CompileError(L === 'java' ? `cannot assign a value to final variable ${n.id}` : L === 'cs' ? `The left-hand side of an assignment must be a variable, property or indexer (${n.id} is a constant)` : `assignment of read-only variable '${n.id}'`, n.line);
            b.uninit = false; b.v = v;
          } };
        }
        if (r.prop) { const I = this; return { ty: r.prop.ty, get: () => I.getProp(r.obj, r.prop, r.ci), set: v => I.setProp(r.obj, r.prop, v, r.ci) }; }
        const o = r.obj, k = r.key;
        return { ty: r.ty, obj: o, key: k, get: () => o.f[k], set: v => { o.f[k] = v; } };
      }
      case 'mem': return this.memRef(n, env);
      case 'idx': return this.idxRef(n, env);
      case 'deref': {
        const p = this.ev(n.a, env);
        const pt = n.a.ty;
        n.ty = pt && pt.ptr ? Object.assign({}, pt, { ptr: pt.ptr - 1 }) : (p instanceof Ptr && p.et) || TY.dyn;
        if (p === null || p === undefined) throw new Fatal('The program followed a NULL pointer with *. There is nothing at address 0, so a real program crashes here', 'segv');
        if (p && p.$iter) return { ty: n.ty, get: () => p.get(), set: v => p.set(v) };
        if (!(p instanceof Ptr)) throw new CF.CompileError('* can only be used on a pointer', n.line);
        return { ty: n.ty, get: () => p.get(), set: v => p.set(v), ptr: p };
      }
      case 'tuple': {
        const refs = n.items.map(x => this.ref(x, env));
        return { ty: TY.dyn, get: () => LIB().tuple(this, refs.map(r => r.get()), refs.map(r => r.ty)), set: v => { const parts = LIB().unpack(this, v, refs.length); refs.forEach((r, i) => r.set(this.conv(parts[i][0], r.ty))); } };
      }
      case 'cast': return this.ref(n.a, env);
    }
    throw new CF.CompileError('This is not something you can assign to', n.line);
  };
  P.memRef = function (n, env) {
    let o;
    if (n.o.k === 'this' || n.o.k === 'super') o = this.frame().self;
    else o = this.ev(n.o, env);
    if (n.arrow) {
      if (o === null || o === undefined) throw new Fatal(`The program used -> on a NULL pointer (${n.o.k === 'name' ? n.o.id : 'pointer'}->${n.id}). There is no object there, so a real program crashes here`, 'segv');
      if (o instanceof Ptr) o = o.get();
      else if (o && o.$iter) o = o.get();
    }
    if (o instanceof Ptr && this.lang === 'cpp' && n.o.k === 'this') o = o.get();
    if ((o === null || o === undefined) && n.q) return { get: () => null, set: () => {}, ty: TY.dyn };
    if (o === null || o === undefined) throw this.nullEx(n);
    if (o instanceof Obj) {
      const ff = this.findField(o.ci, n.id);
      if (ff) {
        if (ff.f.static) { const b = this.staticBox(ff.c, n.id); return { ty: b.ty, get: () => b.v, set: v => { b.v = v; } }; }
        if (ff.f.prop && ff.f.prop.get && ff.f.prop.get !== 'auto') { const I = this; return { ty: ff.f.ty, get: () => I.getProp(o, ff.f), set: v => I.setProp(o, ff.f, v) }; }
        if (ff.f.prop && !ff.f.prop.set && this.lang === 'cs' && ff.f.prop.get === 'auto' && !ff.f.prop.init) {
          const fr = this.frame();
          if (!(fr && fr.self === o && /constructor/.test(fr.name))) {
            return { ty: ff.f.ty, get: () => o.f[n.id], set: () => { throw new CF.CompileError(`Property '${n.id}' cannot be assigned to, it is read only`, n.line); } };
          }
        }
        const I = this, L = this.lang;
        return { ty: ff.f.ty, obj: o, key: n.id, get: () => o.f[n.id], set: v => {
          if (ff.f.konst && L === 'java' && !/constructor/.test((I.frame() || {}).name || '')) throw new CF.CompileError(`cannot assign a value to final variable ${n.id}`, n.line);
          o.f[n.id] = v;
        } };
      }
      if (o.ci.exc && (n.id === 'Message')) return { ty: TY.string, get: () => o.f.$msg ?? '', set: () => {} };
      throw new CF.CompileError(this.lang === 'java' ? `cannot find symbol: ${n.id} is not a field of ${o.ci.name}` : this.lang === 'cs' ? `'${o.ci.name}' does not contain a definition for '${n.id}'` : `'${o.ci.name}' has no member named '${n.id}'`, n.line);
    }
    if (o instanceof ClassRef) {
      const b = this.staticBox(o.ci, n.id);
      if (b) {
        const L = this.lang;
        if (b.prop) { const I = this; const f = { prop: b.prop, ty: b.ty, id: n.id }; return { ty: b.ty, get: () => I.getProp(null, f, o.ci), set: v => I.setProp(null, f, v, o.ci) }; }
        return { ty: b.ty, box: b, get: () => b.v, set: v => { if (b.konst) throw new CF.CompileError(L === 'java' ? `cannot assign a value to final variable ${n.id}` : `cannot assign to ${n.id}, it is a constant`, n.line); b.v = v; } };
      }
      const nested = this.classes.get(o.ci.name + '.' + n.id);
      if (nested) return { ty: TY.dyn, get: () => new ClassRef(nested), set: () => {} };
      const ms = o.ci.methods.get(n.id);
      if (ms) return { ty: TY.dyn, get: () => new Fn({ fname: n.id, overloads: ms, cls: o.ci }), set: () => {} };
      throw new CF.CompileError(this.lang === 'java' ? `cannot find symbol: ${o.ci.name}.${n.id}` : `'${o.ci.name}' does not contain a definition for '${n.id}'`, n.line);
    }
    const r = LIB().member(this, o, n.id, n);
    if (r) return r;
    throw new CF.CompileError(this.lang === 'java' ? `cannot find symbol: ${n.id}` : this.lang === 'cs' ? `There is no member called '${n.id}' here` : `request for member '${n.id}' in something that is not a class or struct`, n.line);
  };
  P.nullEx = function (n, what) {
    const L = this.lang;
    const nm = n && n.o && n.o.k === 'name' ? n.o.id : 'the value';
    if (L === 'java') return this.ex('NullPointerException', what || `Cannot use "${nm}.${n ? n.id : ''}" because "${nm}" is null`);
    if (L === 'cs') return this.ex('NullReferenceException', 'Object reference not set to an instance of an object.');
    return new Fatal(`The program used ${nm} while it was NULL. There is no object there, so a real program crashes here`, 'segv');
  };
  P.idxRef = function (n, env) {
    const o = this.ev(n.o, env);
    const ot = n.o.ty;
    let i = this.ev(n.i, env);
    const it = n.i.ty;
    const L = this.lang;
    if (o === null || o === undefined) {
      if (L === 'java') throw this.ex('NullPointerException', `Cannot load from array because "${n.o.k === 'name' ? n.o.id : 'the array'}" is null`);
      if (L === 'cs') throw this.ex('NullReferenceException', 'Object reference not set to an instance of an object.');
      throw new Fatal('The program indexed a NULL pointer. There is no array there, so a real program crashes here', 'segv');
    }
    if (o instanceof Arr) {
      if (n.i2 && n.i2.length) { /* C# a[i, j] */
        const j = toNum(this.ev(n.i2[0], env));
        const row = o.a[toNum(i)];
        if (!row) throw this.ex('IndexOutOfRangeException', 'Index was outside the bounds of the array.');
        return this.arrRef(row, j, n);
      }
      if ((L === 'java' || L === 'cs') && NK[it && it.n] !== 'i' && it && it.n !== 'dyn' && plain(it) && !(L === 'cs' && (it.n === 'long'))) {
        if (L === 'java') throw new CF.CompileError(`incompatible types: ${it.n === 'string' ? 'String' : it.n} cannot be used as an array index. Indexes are whole numbers`, n.line);
      }
      return this.arrRef(o, toNum(i), n);
    }
    if (o instanceof Ptr) {
      const p = o.add(toNum(i));
      n.ty = ot && ot.ptr ? Object.assign({}, ot, { ptr: ot.ptr - 1, arrParam: false }) : p.et || (o.et) || TY.dyn;
      return { ty: n.ty, get: () => p.get(), set: v => p.set(v) };
    }
    if (typeof o === 'string') {
      i = toNum(i);
      if (L === 'java') throw new CF.CompileError(`array required, but String found. Use s.charAt(${n.i.k === 'name' ? n.i.id : 'i'}) to read one character of a String`, n.line);
      n.ty = TY.char;
      if (L === 'cs') {
        if (i < 0 || i >= o.length) throw this.ex('IndexOutOfRangeException', 'Index was outside the bounds of the array.');
        return { ty: TY.char, get: () => o.charCodeAt(i), set: () => { throw new CF.CompileError("Property or indexer 'string.this[int]' cannot be assigned to, it is read only. Strings cannot change in C#, use a StringBuilder or a char array", n.line); } };
      }
      /* C and C++: the string is changed through the variable that holds it */
      const base = isLvalNode(n.o) ? this.ref(n.o, env) : null;
      return { ty: TY.char, get: () => {
        const s = base ? base.get() : o;
        if (i === s.length) return 0;
        if (i < 0 || i > s.length) throw new Fatal(`s[${i}] is outside the string of length ${s.length}. In C++ this is undefined behaviour. Use s.at(${i}) to get a clear error instead`);
        return s.charCodeAt(i);
      }, set: v => {
        const s = base.get();
        if (i < 0 || i >= s.length) throw new Fatal(`s[${i}] is outside the string of length ${s.length}. Writing there is undefined behaviour`);
        base.set(s.slice(0, i) + chr(v) + s.slice(i + 1));
      } };
    }
    const r = LIB().index(this, o, i, it, n, env);
    if (r) { n.ty = r.ty; return r; }
    throw new CF.CompileError(L === 'java' ? 'array required, but found a ' + (valTy(o).n) + '. Lists use list.get(i) in Java' : 'This value cannot be indexed with [ ]', n.line);
  };
  function isLvalNode(n) { return isLval(n); }
  P.arrRef = function (arr, i, n) {
    const L = this.lang, I = this;
    const len = arr.a.length;
    n.ty = arr.et || TY.dyn;
    const bad = () => {
      if (L === 'java') return I.ex('ArrayIndexOutOfBoundsException', `Index ${i} out of bounds for length ${len}`);
      if (L === 'cs') return I.ex('IndexOutOfRangeException', 'Index was outside the bounds of the array.');
      return new Fatal(`Index ${i} is outside the array of ${len} element${len === 1 ? '' : 's'} (valid indexes are 0 to ${len - 1}). In C and C++ nothing stops this, so a real program may print a random value or crash. This is undefined behaviour`, 'ub');
    };
    if (!Number.isInteger(i)) i = Math.trunc(i);
    return { ty: n.ty, arr, i, get() { if (i < 0 || i >= len) throw bad(); return arr.a[i]; }, set(v) { if (i < 0 || i >= arr.a.length) throw bad(); arr.a[i] = v; } };
  };

  /* ---------- arithmetic ---------- */
  P.divZero = function () {
    if (this.lang === 'java') return this.ex('ArithmeticException', '/ by zero');
    if (this.lang === 'cs') return this.ex('DivideByZeroException', 'Attempted to divide by zero.');
    return new Fatal('The program divided a whole number by zero. That has no answer, so the processor stops the program', 'fpe');
  };
  P.arith = function (op, a, ka, b, kb, n) {
    const k = promote(ka, kb);
    if (k === 'd' || k === 'f') {
      const x = toNum(a), y = toNum(b);
      let r;
      switch (op) {
        case '+': r = x + y; break; case '-': r = x - y; break; case '*': r = x * y; break;
        case '/': r = x / y; break;
        case '%': if (this.lang === 'c') throw new CF.CompileError('invalid operands to binary % (have double). Use fmod(a, b) from math.h for decimals', n.line); r = x % y; break;
        default: throw new CF.CompileError(`The operator ${op} needs whole numbers, not decimals`, n.line);
      }
      if (k === 'f') r = Math.fround(r);
      return [r, k];
    }
    if (k === 'l' || k === 'ul') {
      const x = toBig(a), y = toBig(b);
      let r;
      switch (op) {
        case '+': r = x + y; break; case '-': r = x - y; break; case '*': r = x * y; break;
        case '/': if (y === 0n) throw this.divZero(); r = x / y; break;
        case '%': if (y === 0n) throw this.divZero(); r = x % y; break;
        case '&': r = x & y; break; case '|': r = x | y; break; case '^': r = x ^ y; break;
      }
      return [k === 'l' ? BigInt.asIntN(64, r) : BigInt.asUintN(64, r), k];
    }
    let x = toNum(a), y = toNum(b);
    if (k === 'u') {
      x = x >>> 0; y = y >>> 0;
      let r;
      switch (op) {
        case '+': r = x + y; break; case '-': r = x - y; break; case '*': r = Math.imul(x, y); break;
        case '/': if (y === 0) throw this.divZero(); r = Math.floor(x / y); break;
        case '%': if (y === 0) throw this.divZero(); r = x % y; break;
        case '&': r = x & y; break; case '|': r = x | y; break; case '^': r = x ^ y; break;
      }
      return [r >>> 0, 'u'];
    }
    let r;
    switch (op) {
      case '+': r = (x + y) | 0; break;
      case '-': r = (x - y) | 0; break;
      case '*': r = Math.imul(x, y); break;
      case '/': if (y === 0) throw this.divZero(); r = (x / y) | 0; if (x === -2147483648 && y === -1) r = -2147483648; break;
      case '%': if (y === 0) throw this.divZero(); r = (x % y) | 0; break;
      case '&': r = x & y; break; case '|': r = x | y; break; case '^': r = x ^ y; break;
    }
    if ((this.lang === 'c' || this.lang === 'cpp') && (op === '+' || op === '*' || op === '-')) {
      const exact = op === '+' ? x + y : op === '-' ? x - y : x * y;
      if (exact !== r && Number.isFinite(exact) && !(ka === 'b' || kb === 'b')) this.warn('ovf:' + n.line, `Line ${n.line}: the result ${exact} does not fit in an int, so it wrapped around to ${r}. In C and C++ signed overflow is undefined behaviour, so a real program may give a different number.`);
    }
    return [r, 'i'];
  };
  P.shift = function (op, a, ka, b, n) {
    if (ka === 'l' || ka === 'ul') {
      const s = BigInt(toNum(b) & 63), x = toBig(a);
      if (op === '<<') return [ka === 'l' ? BigInt.asIntN(64, x << s) : BigInt.asUintN(64, x << s), ka];
      if (op === '>>') return [ka === 'ul' ? x >> s : BigInt.asIntN(64, x) >> s, ka];
      return [BigInt.asIntN(64, BigInt.asUintN(64, x) >> s), ka];
    }
    const s = toNum(b) & 31, x = toNum(a);
    if (ka === 'u') { if (op === '<<') return [(x << s) >>> 0, 'u']; return [x >>> s, 'u']; }
    if (op === '<<') return [x << s, 'i'];
    if (op === '>>') return [x >> s, 'i'];
    return [x >>> s | 0, 'i'];
  };
  P.compare = function (op, a, b, at, bt, n) {
    if (op === '==' || op === '!=') {
      let eq;
      if (a instanceof Ptr && b instanceof Ptr) eq = a.arr === b.arr && a.i === b.i && a.box === b.box;
      else if ((typeof a === 'number' || typeof a === 'bigint' || typeof a === 'boolean') && (typeof b === 'number' || typeof b === 'bigint' || typeof b === 'boolean')) eq = typeof a === 'boolean' || typeof b === 'boolean' ? (this.lang === 'c' || this.lang === 'cpp' ? toNum(a) === toNum(b) : a === b) : a == b;
      else if (a && a.$enum || b && b.$enum) eq = this.equals(a, b) || (a && a.$enum && b && b.$enum && a.$enum === b.$enum && a.val === b.val);
      else if (typeof a === 'string' && typeof b === 'string') {
        eq = a === b;
        if (this.lang === 'java' && !(n.a.k === 'lit' || n.b.k === 'lit' || n.a.$interned || n.b.$interned)) this.warn('streq:' + n.line, `Line ${n.line} compares two Strings with ${op}. In Java == checks whether both are the same object, not the same text, so it can be false even when the text matches. Use a.equals(b) to compare text.`);
      }
      else if ((this.lang === 'c') && (typeof a === 'string' || typeof b === 'string')) eq = false;
      else if (a && a.$lib && a.$iter && b && b.$iter) eq = a.$eqIter(b);
      else if (a && a.$lib && (this.lang === 'cpp') && a.$eq) eq = a.$eq(b, this);
      else if (a instanceof Obj && b instanceof Obj && (this.lang === 'cpp' || this.lang === 'c')) {
        const m = this.findMethod(a.ci, 'operator==', 1);
        if (m) eq = !!this.invoke(m, a, [b], [bt], 'operator==');
        else eq = a === b;
      }
      else if (a instanceof Obj && this.lang === 'cs' && (a.ci.record || a.ci.isStruct)) eq = this.equals(a, b);
      else eq = a === b || (a === null && b === undefined) || (a === undefined && b === null) || (a === null && b === 0 && this.lang !== 'java') || (a === 0 && b === null);
      return op === '==' ? eq : !eq;
    }
    if (typeof a === 'string' && typeof b === 'string') {
      if (this.lang === 'java') throw new CF.CompileError(`bad operand types for binary operator '${op}'. Use a.compareTo(b) ${op} 0 to compare Strings`, n.line);
      if (this.lang === 'cs') throw new CF.CompileError(`Operator '${op}' cannot be applied to operands of type 'string' and 'string'. Use string.Compare(a, b) ${op} 0`, n.line);
      return { '<': a < b, '>': a > b, '<=': a <= b, '>=': a >= b }[op];
    }
    if (a instanceof Ptr && b instanceof Ptr) { a = a.i; b = b.i; }
    if (a && a.$iter) { a = a.i; b = b.i; }
    if (a instanceof Obj && (this.lang === 'cpp')) { const m = this.findMethod(a.ci, 'operator' + op, 1); if (m) return !!this.invoke(m, a, [b], [bt], 'operator' + op); const r = this.freeOp(op, a, b, at, bt, n); if (r !== NOFREE) return !!r; }
    if (a && a.$enum) a = a.val; if (b && b.$enum) b = b.val;
    if ((this.lang === 'java' || this.lang === 'cs') && (typeof a === 'boolean' || typeof b === 'boolean')) throw new CF.CompileError(`The operator ${op} cannot compare true and false values`, n.line);
    const ka = kindOf(at, a), kb = kindOf(bt, b);
    if ((ka === 'u' || kb === 'u') && (this.lang === 'c' || this.lang === 'cpp') && promote(ka, kb) === 'u') { a = toNum(a) >>> 0; b = toNum(b) >>> 0; }
    if ((ka === 'ul' || kb === 'ul') && (this.lang === 'c' || this.lang === 'cpp') && !(ka === 'd' || kb === 'd')) {
      const ua = BigInt.asUintN(64, toBig(a)), ub = BigInt.asUintN(64, toBig(b));
      if ((toNum(a) < 0 || toNum(b) < 0) && !(n.a.k === 'lit' || n.b.k === 'lit')) this.warn('signcmp:' + n.line, `Line ${n.line} compares a signed number with an unsigned one (like size()). A negative number turns into a huge positive one there, which is a classic C++ trap.`);
      a = ua; b = ub;
    }
    switch (op) { case '<': return a < b; case '>': return a > b; case '<=': return a <= b; case '>=': return a >= b; }
  };

  /* ---------- the expression evaluator ---------- */
  P.ev = function (n, env) {
    switch (n.k) {
      case 'lit': {
        if (n.num) return litVal(n, this.lang);
        return n.v;
      }
      case 'name': return this.lookupName(n, env);
      case 'paren': { const v = this.ev(n.a, env); n.ty = n.a.ty; return v; }
      case 'this': {
        const fr = this.frame();
        if (!fr || !fr.self) throw new CF.CompileError(this.lang === 'java' ? 'non-static variable this cannot be referenced from a static context' : 'Keyword this is not available in a static method', n.line);
        n.ty = { n: fr.self.ci ? fr.self.ci.name : 'dyn', ptr: this.lang === 'cpp' ? 1 : 0 };
        if (this.lang === 'cpp') { const arr = [fr.self]; arr.isObj = true; return new Ptr(arr, 0, null, { n: fr.self.ci.name }); }
        return fr.self;
      }
      case 'super': { const fr = this.frame(); n.ty = TY.dyn; return fr.self; }
      case 'bin': return this.evBin(n, env);
      case 'un': {
        const v = this.ev(n.a, env);
        const k = kindOf(n.a.ty, v);
        switch (n.op) {
          case '!': if ((this.lang === 'java' || this.lang === 'cs') && typeof v !== 'boolean') throw new CF.CompileError(`The ! operator needs a true or false value`, n.line); n.ty = TY.bool; return !this.truthy(v);
          case '-': {
            if (v && v.$enum) { n.ty = TY.int; return -v.val; }
            if (k === 'l') { n.ty = TY.long; return BigInt.asIntN(64, -v); }
            if (k === 'ul') { n.ty = TY.ulong; return BigInt.asUintN(64, -v); }
            if (k === 'd' || k === 'f') { n.ty = KT[k]; return -v; }
            if (k === 'u') { n.ty = TY.uint; return (-v) >>> 0; }
            n.ty = TY.int; return (-toNum(v)) | 0;
          }
          case '+': n.ty = k === 'd' || k === 'f' || k === 'l' || k === 'ul' || k === 'u' ? KT[k] : TY.int; return typeof v === 'boolean' ? +v : v;
          case '~': if (k === 'l' || k === 'ul') { n.ty = KT[k]; return k === 'l' ? ~v : BigInt.asUintN(64, ~v); } n.ty = k === 'u' ? TY.uint : TY.int; return k === 'u' ? (~v) >>> 0 : ~toNum(v);
        }
        break;
      }
      case 'pre': case 'post': {
        const r = this.ref(n.a, env);
        const old = r.get();
        if (r.box && r.box.uninit) { if (this.lang === 'java' || this.lang === 'cs') throw new CF.CompileError(`variable ${n.a.id} might not have been initialized`, n.line); }
        const ty = r.ty && r.ty.n !== 'var' ? r.ty : valTy(old);
        let nv;
        if (old instanceof Ptr) nv = old.add(n.op === '++' ? 1 : -1);
        else if (old && old.$iter) { if (n.k === 'pre') { old.move(n.op === '++' ? 1 : -1); n.ty = TY.dyn; return old; } const cp = old.clone(); old.move(n.op === '++' ? 1 : -1); n.ty = TY.dyn; return cp; }
        else if (old === null && (this.lang === 'java')) throw this.ex('NullPointerException', null);
        else {
          const k = kindOf(ty, old) || 'i';
          if (k === 'l' || k === 'ul') nv = old + (n.op === '++' ? 1n : -1n);
          else nv = toNum(old) + (n.op === '++' ? 1 : -1);
          if (k === 'i' || k === 'u') { if (k === 'i' && (nv > 2147483647 || nv < -2147483648) && (this.lang === 'c' || this.lang === 'cpp')) this.warn('ovf:' + n.line, `Line ${n.line}: the result ${nv} does not fit in an int, so it wrapped around to ${nv | 0}. In C and C++ signed overflow is undefined behaviour, so a real program may give a different number.`); nv = k === 'u' ? nv >>> 0 : nv | 0; }
          nv = this.conv(nv, plain(ty) && NK[ty.n] ? ty : KT[k]);
        }
        r.set(nv);
        n.ty = ty;
        return n.k === 'pre' ? nv : old;
      }
      case 'asg': return this.evAssign(n, env);
      case 'cond': {
        const c = this.truthy(this.ev(n.c, env), n.c);
        const br = c ? n.a : n.b;
        let v = this.ev(br, env);
        const ka = n.a.ty && plain(n.a.ty) ? NK[n.a.ty.n] : null, kb = n.b.ty && plain(n.b.ty) ? NK[n.b.ty.n] : null;
        if (ka && kb && ka !== kb && (this.lang !== 'cs' || true)) { const k = promote(ka, kb); if (!(n.a.ty.n === 'char' && n.b.ty.n === 'char')) { n.ty = KT[k]; return this.conv(v, KT[k]); } }
        n.ty = br.ty;
        return v;
      }
      case 'call': return this.evCall(n, env);
      case 'mem': {
        const r = this.memRef(n, env);
        n.ty = r.ty;
        return r.get();
      }
      case 'idx': { const r = this.idxRef(n, env); n.ty = r.ty; return r.get(); }
      case 'new': return this.evNew(n, env);
      case 'newarr': return this.evNewArr(n, env);
      case 'cast': return this.evCast(n, env);
      case 'lam': {
        const fr = this.frame();
        n.ty = TY.dyn;
        return new Fn({ params: n.params, body: n.body, exprBody: n.exprBody, closure: env, self: fr && fr.self, cls: fr && fr.cls, lambda: true, line: n.line, ret: n.ret || null });
      }
      case 'mref': return this.evMref(n, env);
      case 'arr': {
        /* a brace list used as a value: f({1, 2, 3}) */
        const vals = n.items.map(x => this.ev(x, env));
        n.ty = { n: (n.items[0] && n.items[0].ty && n.items[0].ty.n) || 'dyn', dim: 1 };
        if (n.coll) return LIB().make(this, { n: 'List', args: [n.items[0] ? n.items[0].ty : TY.dyn] }, [], [], null, vals, n.items.map(x => x.ty));
        const a = new Arr(vals, n.items[0] ? n.items[0].ty : TY.dyn); a.brace = true; a.tys = n.items.map(x => x.ty);
        return a;
      }
      case 'inst': {
        const v = this.ev(n.a, env);
        const ok = this.instOf(v, n.tt);
        if (ok && n.bind) env.v.set(n.bind, new Box(v, n.tt));
        n.ty = TY.bool;
        return ok;
      }
      case 'as': { const v = this.ev(n.a, env); n.ty = n.tt; return this.instOf(v, n.tt) ? v : null; }
      case 'istr': {
        let s = '';
        for (const p of n.parts) {
          if (typeof p === 'string') { s += p; continue; }
          const v = this.ev(p.e, env);
          let t = CF.csFormat(this, v, p.e.ty, p.fmt);
          if (p.align !== null && p.align !== undefined) t = p.align < 0 ? t.padEnd(-p.align) : t.padStart(p.align);
          s += t;
        }
        n.ty = TY.string;
        return s;
      }
      case 'sizeof': {
        n.ty = TY.ulong;
        if (n.a === undefined && n.tt && !n.tt.ptr && !n.tt.dim && env.lookup(n.tt.n) && !PRIM_T.has(n.tt.n) && !this.classes.get(n.tt.n)) n.a = { k: 'name', id: n.tt.n, line: n.line };
        if (n.a === undefined) return BigInt(this.sizeOf(this.resolveTy(n.tt)));
        let v;
        if (n.a.k === 'name') { const b = env.lookup(n.a.id); if (b && b.v instanceof Arr && !(b.ty && b.ty.ptr)) return BigInt(b.ty && b.ty.cdims && b.ty.cdims.length ? this.sizeOf(b.ty) || this.sizeOfVal(b.v) : this.sizeOfVal(b.v)); }
        v = this.ev(n.a, env);
        if (v instanceof Arr) return BigInt(this.sizeOfVal(v));
        if (typeof v === 'string' && n.a.k === 'lit') return BigInt(v.length + 1);
        return BigInt(this.sizeOf(n.a.ty || valTy(v)));
      }
      case 'addr': {
        const a = n.a;
        n.ty = Object.assign({}, a.ty || TY.dyn, { ptr: ((a.ty && a.ty.ptr) || 0) + 1 });
        if (a.k === 'name') {
          const r = this.lookupBox(a.id, env, a);
          if (r && r.box) {
            const v = r.box.v;
            if (v instanceof Arr && (this.lang === 'c' || this.lang === 'cpp')) { n.ty = Object.assign({}, r.box.ty, { ptr: 1 }); return new Ptr(v.a, 0, null, v.et); }
            n.ty = Object.assign({}, r.box.ty, { ptr: ((r.box.ty && r.box.ty.ptr) || 0) + 1, ref: false });
            const p = new Ptr(null, 0, r.box instanceof RefBox ? { get v() { return r.box.v; }, set v(x) { r.box.v = x; }, ty: r.box.ty } : r.box, r.box.ty); p.name = a.id;
            if (r.box.uninit) r.box.uninit = false;
            return p;
          }
          const fnv = this.ev(a, env);
          if (fnv instanceof Fn) return fnv;
        }
        if (a.k === 'idx') {
          const base = this.ev(a.o, env); const i = toNum(this.ev(a.i, env));
          if (base instanceof Arr) { n.ty = Object.assign({}, base.et, { ptr: 1 }); return new Ptr(base.a, i, null, base.et); }
          if (base instanceof Ptr) return base.add(i);
          if (base && base.$lib && base.a) return new Ptr(base.a, i, null, base.et);
        }
        const r = this.ref(a, env);
        n.ty = Object.assign({}, r.ty || TY.dyn, { ptr: ((r.ty && r.ty.ptr) || 0) + 1 });
        if (r.ptr) return r.ptr;
        const p = new Ptr(null, 0, { get v() { return r.get(); }, set v(x) { r.set(x); }, ty: r.ty }, r.ty);
        p.name = a.k === 'mem' ? (a.o.k === 'name' ? a.o.id + (a.arrow ? '->' : '.') : '') + a.id : 'value';
        return p;
      }
      case 'deref': {
        const r = this.ref(n, env);
        return r.get();
      }
      case 'swx': return this.evSwitchExpr(n, env);
      case 'tuple': {
        const vals = n.items.map(x => this.ev(x, env));
        n.ty = TY.dyn;
        return LIB().tuple(this, vals, n.items.map(x => x.ty));
      }
      case 'throwx': { const v = this.ev(n.a, env); throw new Throw(v, n.line); }
      case 'delete': { const v = this.ev(n.a, env); if (v instanceof Ptr && v.arr) v.arr.freed = true; n.ty = TY.void; return undefined; }
      case 'default': n.ty = n.tt; return this.defaultVal(n.tt);
      case 'with': {
        const o = this.ev(n.o, env);
        const c = new Obj(o.ci); Object.assign(c.f, o.f);
        for (const it of n.init) if (it.id) c.f[it.id] = this.conv(this.ev(it.e, env), this.fieldTy(o.ci, it.id));
        n.ty = n.o.ty;
        return c;
      }
      case 'outdecl': {
        const b = new Box(this.defaultVal(n.tt), n.tt);
        env.v.set(n.id, b);
        n.$box = b; n.ty = n.tt;
        return b.v;
      }
      case 'refarg': { const v = this.ev(n.a, env); n.ty = n.a.ty; return v; }
    }
    throw new Fatal('Unknown expression ' + n.k);
  };
  P.instOf = function (v, ty) {
    if (v === null || v === undefined) return false;
    const n = ty.n;
    if (ty.dim) return v instanceof Arr;
    if (v instanceof Obj) return this.isA(v.ci, n);
    if (typeof v === 'string') return ['string', 'object', 'Object', 'CharSequence', 'Comparable'].includes(n);
    if (typeof v === 'number') { const k = NK[n]; return n === 'object' || n === 'Object' || n === 'Number' || n === 'Comparable' || (k === 'i' ? Number.isInteger(v) : !!k); }
    if (typeof v === 'bigint') return ['long', 'object', 'Object', 'Number'].includes(n);
    if (typeof v === 'boolean') return ['bool', 'object', 'Object'].includes(n);
    if (v && v.$lib && v.$is) return v.$is(n) || n === 'object' || n === 'Object';
    return n === 'object' || n === 'Object';
  };
  P.sizeOf = function (ty) {
    if (!ty) return 4;
    if (ty.ptr) return 8;
    if (ty.cdims && ty.cdims.length) return ty.cdims.reduce((a, d) => a * (d ? toNum(this.ev(d, this.globals)) : 0), 1) * this.sizeOf(Object.assign({}, ty, { cdims: null, dim: 0 }));
    if (SIZE[ty.n]) return this.lang === 'c' && ty.n === 'string' ? 8 : SIZE[ty.n];
    const ci = this.classes.get(ty.n);
    if (ci) {
      let size = 0, align = 1;
      for (const f of ci.fieldList) {
        if (f.static) continue;
        const s = this.sizeOf(f.ty), al = Math.min(8, f.ty.ptr ? 8 : (SIZE[f.ty.n] || 8));
        align = Math.max(align, al);
        size = Math.ceil(size / al) * al + s;
      }
      return Math.max(1, Math.ceil(size / align) * align);
    }
    if (CF.LIB.isLibType(ty.n)) return 24;
    return 4;
  };
  const PRIM_T = new Set(['int', 'char', 'short', 'long', 'float', 'double', 'bool', 'unsigned', 'signed', 'void', 'size_t', 'string']);
  P.sizeOfVal = function (v) {
    if (v instanceof Arr) { if (!v.a.length) return 0; return v.a.length * (v.a[0] instanceof Arr ? this.sizeOfVal(v.a[0]) : this.sizeOf(v.et)); }
    return this.sizeOf(valTy(v));
  };

  /* C++ operators written as free functions, such as operator<<(ostream&, const Point&) */
  const NOFREE = { nofree: true };
  P.freeOp = function (op, a, b, at, bt, n) {
    const list = this.funcs.get('operator' + op);
    if (!list) return NOFREE;
    const tys = [at || valTy(a), bt || valTy(b)];
    const m = this.pick(list.filter(f => f.params.length === 2), [a, b], tys, n.line);
    if (!m || !m.body) return NOFREE;
    const refs = [{ get: () => a, set: () => {}, ty: tys[0] }, { get: () => b, set: () => {}, ty: tys[1] }];
    const r = this.invoke(m, null, [a, b], tys, 'operator' + op, null, n.line, refs);
    n.ty = m.ret && !m.ret.tp ? this.resolveTy(m.ret) : valTy(r);
    return r;
  };

  P.evBin = function (n, env) {
    const op = n.op;
    const L = this.lang;
    if (op === '&&' || op === '||') {
      const a = this.truthy(this.ev(n.a, env), n.a);
      n.ty = TY.bool;
      if (op === '&&' ? !a : a) return a;
      return this.truthy(this.ev(n.b, env), n.b);
    }
    if (op === '??') { const a = this.ev(n.a, env); if (a !== null && a !== undefined) { n.ty = n.a.ty; return a; } const b = this.ev(n.b, env); n.ty = n.b.ty; return b; }
    const a = this.ev(n.a, env);
    /* C++ streams: cout << x and cin >> x */
    if (a && (a.kind === 'out' || a.kind === 'in')) {
      if (op === '<<' && a.kind === 'out') { const b = this.ev(n.b, env); if (b instanceof Obj) { const r = this.freeOp('<<', a, b, n.a.ty, n.b.ty, n); if (r !== NOFREE) { n.ty = TY.dyn; return r; } } LIB().streamOut(this, a, b, n.b.ty, n.b); n.ty = TY.dyn; return a; }
      if (op === '>>' && a.kind === 'in' && this.funcs.has('operator>>')) { const r = this.ref(n.b, env); const v = r.get(); if (v instanceof Obj) { const res = this.freeOp('>>', a, v, n.a.ty, n.b.ty, n); if (res !== NOFREE) { n.ty = TY.dyn; return res; } } }
      if (op === '>>' && a.kind === 'in') { const r = this.ref(n.b, env); LIB().streamIn(this, a, r, n.b); n.ty = TY.dyn; return a; }
    }
    const b = this.ev(n.b, env);
    const at = n.a.ty, bt = n.b.ty;
    /* strings */
    if (op === '+') {
      const as = typeof a === 'string' && !(at && at.n === 'char' && plain(at)), bs = typeof b === 'string' && !(bt && bt.n === 'char' && plain(bt));
      const sa = at && at.n === 'string' && plain(at), sb = bt && bt.n === 'string' && plain(bt);
      if (L === 'java' || L === 'cs') {
        if (as || bs || sa || sb) { n.ty = TY.string; return this.str(a, at) + this.str(b, bt); }
      } else if (L === 'cpp' && (as || bs)) {
        if (as && bs && n.a.k === 'lit' && n.b.k === 'lit') throw new CF.CompileError(`invalid operands to binary + (two string literals). Make one a std::string first: string("${a}") + "${b}"`, n.line);
        if (as && !bs && typeof b === 'number' && !(bt && bt.n === 'char')) {
          if (n.a.k === 'lit' && a.length >= b) { n.ty = TY.string; this.warn('ptrlit:' + n.line, `Line ${n.line} adds a number to a string literal. In C++ that moves a pointer through the text, it does not join a number on. Use to_string(n) to join a number.`); return a.slice(b); }
          throw new CF.CompileError(`no match for operator+ between a string and an int. Use to_string(${n.b.k === 'name' ? n.b.id : 'n'}) to turn the number into text first`, n.line);
        }
        if (bs && !as && typeof a === 'number' && !(at && at.n === 'char')) throw new CF.CompileError(`no match for operator+ between an int and a string. Use to_string(...) on the number first`, n.line);
        n.ty = TY.string;
        return (typeof a === 'string' ? a : a instanceof Ptr ? this.cstr(a) : chr(a)) + (typeof b === 'string' ? b : b instanceof Ptr ? this.cstr(b) : chr(b));
      }
    }
    if (L === 'cpp' && (a instanceof Obj || (a && a.$lib && !a.$iter))) {
      const m = a instanceof Obj ? this.findMethod(a.ci, 'operator' + op, 1) : null;
      if (m) { const r = this.invoke(m, a, [b], [bt], a.ci.name + '::operator' + op); n.ty = m.ret; return r; }
    }
    if (L === 'cpp' && (a instanceof Obj || b instanceof Obj)) { const r = this.freeOp(op, a, b, at, bt, n); if (r !== NOFREE) return r; }
    if (op === '==' || op === '!=' || op === '<' || op === '>' || op === '<=' || op === '>=') {
      n.ty = TY.bool;
      return this.compare(op, a, b, at, bt, n);
    }
    /* pointer arithmetic */
    if (a instanceof Ptr || b instanceof Ptr || (a instanceof Arr && (L === 'c' || L === 'cpp') && (op === '+' || op === '-'))) {
      const pa = a instanceof Arr ? new Ptr(a.a, 0, null, a.et) : a;
      if (op === '+') { n.ty = n.a.ty && n.a.ty.ptr ? n.a.ty : Object.assign({}, (pa && pa.et) || TY.dyn, { ptr: 1 }); return pa instanceof Ptr ? pa.add(toNum(b)) : b.add(toNum(pa)); }
      if (op === '-') {
        if (b instanceof Ptr) { n.ty = TY.long; return BigInt(pa.i - b.i); }
        n.ty = n.a.ty; return pa.add(-toNum(b));
      }
    }
    if (a && a.$iter && (op === '+' || op === '-')) {
      if (b && b.$iter) { n.ty = TY.long; return BigInt(a.i - b.i); }
      const c = a.clone(); c.move(op === '+' ? toNum(b) : -toNum(b)); n.ty = TY.dyn; return c;
    }
    if (a === null || b === null) {
      if (L === 'java') throw this.ex('NullPointerException', null);
      if (L === 'cs') { n.ty = at || bt; return null; }
    }
    if (op === '&' || op === '|' || op === '^') {
      if (typeof a === 'boolean' && typeof b === 'boolean') { n.ty = TY.bool; return op === '&' ? a && b : op === '|' ? a || b : a !== b; }
    }
    if (a && a.$enum && b && b.$enum && (op === '|' || op === '&')) { const v = op === '|' ? a.val | b.val : a.val & b.val; n.ty = { n: a.$enum.name }; return LIB().csEnumVal(this, a.$enum, v); }
    let ka = kindOf(at, a), kb = kindOf(bt, b);
    if (typeof a === 'boolean') { if (L === 'java' || L === 'cs') throw new CF.CompileError(`bad operand types for ${op}: true and false values are not numbers`, n.line); ka = 'i'; }
    if (typeof b === 'boolean') { if (L === 'java' || L === 'cs') throw new CF.CompileError(`bad operand types for ${op}: true and false values are not numbers`, n.line); kb = 'i'; }
    if (a && a.$enum) ka = 'i'; if (b && b.$enum) kb = 'i';
    if (!ka || !kb) {
      if ((typeof a === 'string' || typeof b === 'string') && L !== 'java' && L !== 'cs') throw new CF.CompileError(`The operator ${op} cannot be used with text here`, n.line);
      throw new CF.CompileError(`bad operand types for binary operator '${op}'`, n.line);
    }
    if (op === '<<' || op === '>>' || op === '>>>') {
      const [v, k] = this.shift(op, a && a.$enum ? a.val : a, (ka === 'i' && (at && (at.n === 'long' || at.n === 'ulong'))) ? NK[at.n] : promote(ka, 'i'), b && b.$enum ? b.val : b, n);
      n.ty = KT[k];
      return v;
    }
    const [v, k] = this.arith(op, a && a.$enum ? a.val : a, ka, b && b.$enum ? b.val : b, kb, n);
    n.ty = KT[k];
    return v;
  };

  P.evAssign = function (n, env) {
    const op = n.op;
    const L = this.lang;
    if (op === '=') {
      if (n.a.k === 'tuple') { const v = this.ev(n.b, env); const r = this.ref(n.a, env); r.set(v); n.ty = TY.dyn; return v; }
      const r = this.ref(n.a, env);
      let ty = r.ty;
      if (ty && ty.tp) ty = this.resolveTy(ty);
      let v;
      if (n.b.k === 'arr' && ty && (L === 'cpp' || L === 'c')) v = this.evInit(n.b, ty, env);
      else v = this.ev(n.b, env);
      if (ty && ty.n === 'var') ty = valTy(v);
      const sv = ty ? this.convStore(ty, v, n.b) : this.copyVal(v);
      if (L === 'cpp' && sv instanceof Obj && r.get() instanceof Obj && !isPtrTy(ty)) {
        const m = this.findMethod(sv.ci, 'operator=', 1);
        if (m) { this.invoke(m, r.get(), [v], [n.b.ty], sv.ci.name + '::operator='); n.ty = ty; return r.get(); }
      }
      r.set(sv);
      n.ty = ty || n.b.ty;
      return sv;
    }
    const r = this.ref(n.a, env);
    const cur = r.get();
    if (r.box && r.box.uninit && (L === 'java' || L === 'cs')) throw new CF.CompileError(L === 'java' ? `variable ${n.a.id} might not have been initialized` : `Use of unassigned local variable '${n.a.id}'`, n.line);
    if (op === '??=') { if (cur !== null && cur !== undefined) return cur; const v = this.ev(n.b, env); r.set(this.conv(v, r.ty)); return v; }
    const b = this.ev(n.b, env);
    const bop = op.slice(0, -1);
    let ty = r.ty && r.ty.n !== 'var' ? r.ty : valTy(cur);
    let nv;
    if (cur && cur.kind === 'out' && bop === '<<') { LIB().streamOut(this, cur, b, n.b.ty, n.b); return cur; }
    if (bop === '+' && (typeof cur === 'string' || (ty && ty.n === 'string' && plain(ty)))) {
      if (L === 'cpp') nv = (cur || '') + (typeof b === 'string' ? b : b instanceof Ptr ? this.cstr(b) : chr(b));
      else nv = this.str(cur, ty) + this.str(b, n.b.ty);
      r.set(nv); n.ty = TY.string; return nv;
    }
    if (cur instanceof Ptr) { nv = cur.add(bop === '+' ? toNum(b) : -toNum(b)); r.set(nv); n.ty = ty; return nv; }
    if (cur && cur.$iter) { cur.move(bop === '+' ? toNum(b) : -toNum(b)); return cur; }
    if (cur === null && L === 'java') throw this.ex('NullPointerException', null);
    if (cur instanceof Obj && L === 'cpp') { const m = this.findMethod(cur.ci, 'operator' + op, 1); if (m) return this.invoke(m, cur, [b], [n.b.ty], 'operator' + op); }
    if (cur && cur.$enum && (bop === '|' || bop === '&')) { const nv2 = LIB().csEnumVal(this, cur.$enum, bop === '|' ? cur.val | b.val : cur.val & b.val); r.set(nv2); return nv2; }
    let ka = kindOf(ty, cur) || 'i', kb = kindOf(n.b.ty, b) || 'i';
    if (typeof cur === 'boolean' && typeof b === 'boolean') { nv = bop === '&' ? cur && b : bop === '|' ? cur || b : cur !== b; r.set(nv); n.ty = TY.bool; return nv; }
    if (bop === '<<' || bop === '>>' || bop === '>>>') nv = this.shift(bop, cur, ka, b, n)[0];
    else nv = this.arith(bop, cur, ka, b, kb, n)[0];
    nv = this.conv(nv, plain(ty) && NK[ty.n] ? ty : KT[ka]);
    r.set(nv);
    n.ty = ty;
    return nv;
  };

  P.evCast = function (n, env) {
    const v = this.ev(n.a, env);
    const ty = this.resolveTy(n.tt);
    const L = this.lang;
    n.ty = ty;
    if (ty.n === 'void') return undefined;
    if (isPtrTy(ty)) {
      if (v instanceof Ptr && v.raw !== undefined) return this.materialize(v, ty);
      if (v instanceof Ptr) { const p = new Ptr(v.arr, v.i, v.box, Object.assign({}, ty, { ptr: ty.ptr - 1 })); p.name = v.name; return p; }
      if (v instanceof Arr) return new Ptr(v.a, 0, null, v.et);
      return v;
    }
    if (plain(ty) && (NK[ty.n] || ty.n === 'bool')) {
      if (v && v.$enum) return this.conv(v.val, ty);
      if (typeof v === 'string' && (L === 'java' || L === 'cs') && ty.n !== 'char') throw new CF.CompileError(L === 'java' ? `incompatible types: String cannot be converted to ${ty.n}. Use Integer.parseInt(text) to read a number from text` : `Cannot convert type 'string' to '${ty.n}'. Use int.Parse(text)`, n.line);
      if (v === null && L === 'java') throw this.ex('NullPointerException', null);
      if (L === 'cs' && (ty.n === 'int' || ty.n === 'long') && typeof v === 'number' && !Number.isFinite(v)) return ty.n === 'int' ? -2147483648 : -9223372036854775808n;
      return this.conv(v, ty);
    }
    if (L === 'cs' && this.classes.get(ty.n) && this.classes.get(ty.n).isEnum && typeof v === 'number') return LIB().csEnumVal(this, this.classes.get(ty.n), v);
    if (v instanceof Obj && this.classes.get(ty.n) && !this.isA(v.ci, ty.n)) {
      if (L === 'java') throw this.ex('ClassCastException', `class ${v.ci.name} cannot be cast to class ${ty.n}`);
      if (L === 'cs') throw this.ex('InvalidCastException', `Unable to cast object of type '${v.ci.name}' to type '${ty.n}'.`);
    }
    if (ty.n === 'string' && L === 'cpp') return this.conv(v, ty);
    if (ty.n === 'string' && L === 'java' && typeof v !== 'string' && v !== null) throw this.ex('ClassCastException', `class ${valTy(v).n} cannot be cast to class java.lang.String`);
    return v;
  };

  P.evNew = function (n, env) {
    const L = this.lang;
    let ty = n.tt;
    if (!ty) { /* C#: new() with the target type, filled in by the declaration */
      ty = n.target || TY.dyn;
    }
    ty = this.resolveTy(ty);
    if (ty.n === 'anon') {
      const o = LIB().anon(this, n.init.map(it => [it.id, this.ev(it.e, env), it.e.ty]));
      n.rty = TY.dyn; return o;
    }
    const argNodes = n.args || [];
    const wantRefs = L === 'cpp' || L === 'cs';
    const refs = [];
    const args = argNodes.map((a, i) => {
      if (a.k === 'refarg' || a.k === 'outdecl') { const r = a.k === 'outdecl' ? (this.ev(a, env), { get: () => a.$box.v, set: v => { a.$box.v = v; }, ty: a.ty }) : this.ref(a.a, env); refs[i] = r; a.ty = r.ty; return r.get(); }
      if (wantRefs && isLval(a) && L === 'cpp') { try { const r = this.ref(a, env); refs[i] = r; const v = r.get(); a.ty = r.ty && r.ty.n !== 'var' ? Object.assign({}, r.ty, { ref: false }) : valTy(v); return v; } catch (e) { if (!(e instanceof CF.CompileError)) throw e; } }
      return this.ev(a, env);
    });
    const tys = argNodes.map(a => a.ty);
    let ci = this.classes.get(ty.n) || this.exClass(ty.n);
    let result;
    if (n.anon) {
      /* Java anonymous class: new Comparator<Integer>() { public int compare(...) {...} } */
      const base = ci;
      const fake = { name: (base ? base.name : ty.n) + '$1', d: Object.assign({ statics: [] }, n.anon, { kind: 'class', ctors: [] }), base: base && base.kind !== 'interface' ? base : null, fieldList: n.anon.fields, methods: new Map(), ctors: [], sf: new Map(), sinit: false, ifaces: [ty.n], outer: this.frame() && this.frame().cls };
      for (const m of n.anon.methods) { if (!fake.methods.has(m.name)) fake.methods.set(m.name, []); fake.methods.get(m.name).push(m); }
      if (!base || base.kind === 'interface' || !this.classes.has(ty.n)) {
        /* an interface from the library (Comparator, Runnable): make the object callable */
        const o = new Obj(fake); o.$cenv = env;
        this.initFields(o, fake, env); this.runFieldInits(o, fake, env);
        const only = n.anon.methods.filter(m => !m.static);
        if (!this.classes.has(ty.n) && only.length >= 1) {
          const m = only[0];
          const fn = new Fn({ params: m.params, body: m.body, closure: env, self: o, cls: fake, lambda: false, line: m.line, ret: m.ret, anonObj: o });
          fn.name = m.name;
          return fn;
        }
        return o;
      }
      const o = new Obj(fake); o.$cenv = env;
      this.initFields(o, fake, env);
      this.runCtor(base, o, args, tys, argNodes, n.line);
      this.runFieldInits(o, fake, env);
      return o;
    }
    if (ci && !ci.builtin || (ci && ci.exc)) {
      if (ci.isEnum) throw new CF.CompileError(`enum types cannot be created with new`, n.line);
      result = this.construct(ci, args, tys, argNodes, n.line, ty, refs, n.init, null);
      if (L === 'cpp' && !n.value) { const arr = [result]; arr.isObj = true; n.ty = Object.assign({}, ty, { ptr: 1 }); return new Ptr(arr, 0, null, ty); }
      n.ty = { n: ci.name, args: ty.args };
      return result;
    }
    if (L === 'cpp' && !n.value && (plain(ty) && (NK[ty.n] || ty.n === 'bool'))) { n.ty = Object.assign({}, ty, { ptr: 1 }); return new Ptr([args.length ? this.conv(args[0], ty) : 0], 0, null, ty); }
    if (LIB().isLibType(ty.n) || ty.n === 'string' || ty.n === 'object' || NK[ty.n] || ty.n === 'bool') {
      result = n.brace && LIB().isLibType(ty.n) ? LIB().make(this, ty, [], [], null, args, tys) : LIB().make(this, ty, args, tys, argNodes, null, null, n.init, env, refs);
      n.ty = result && result.$ty ? result.$ty() : ty;
      if (L === 'cpp' && !n.value) { const arr = [result]; arr.isObj = true; n.ty = Object.assign({}, ty, { ptr: 1 }); return new Ptr(arr, 0, null, ty); }
      return result;
    }
    throw new CF.CompileError(L === 'java' ? `cannot find symbol: class ${ty.n}` : L === 'cs' ? `The type or namespace name '${ty.n}' could not be found` : `'${ty.n}' does not name a type`, n.line);
  };
  P.evNewArr = function (n, env) {
    const L = this.lang;
    const base = this.resolveTy(n.tt);
    const rank = n.dims.length;
    if (n.init) {
      const t = Object.assign({}, base, { dim: rank });
      const a = this.arrayFrom(n.init, t, env);
      if (base.n === 'var' && a.a.length) { a.et = valTy(a.a[0]); }
      n.ty = Object.assign({}, a.et, { dim: (a.et.dim || 0) + 1 });
      if (L === 'cpp') return new Ptr(a.a, 0, null, a.et);
      return a;
    }
    const sizes = n.dims.map(d => d ? this.ev(d, env) : null).map(x => x === null ? null : toNum(x));
    const build = k => {
      const len = sizes[k];
      if (len === null) return null;
      if (len < 0) throw L === 'java' ? this.ex('NegativeArraySizeException', String(len)) : L === 'cs' ? this.ex('OverflowException', 'Arithmetic operation resulted in an overflow.') : new Fatal('new with a negative size', 'fatal');
      if (len > 5e6) throw new Fatal(`An array of ${len} elements is too big for the playground`);
      const et = Object.assign({}, base, { dim: rank - k - 1 });
      const a = new Array(len);
      for (let i = 0; i < len; i++) a[i] = k + 1 < rank ? build(k + 1) : (et.dim ? null : this.defaultVal(et));
      return new Arr(a, et);
    };
    const arr = build(0);
    if (n.tt.rank > 1 && L === 'cs') { arr.rank = n.tt.rank; }
    n.ty = Object.assign({}, base, { dim: rank });
    if (L === 'cpp' || L === 'c') { n.ty = Object.assign({}, base, { ptr: 1 }); if (this.classes.get(base.n)) arr.a.isObj = true; return new Ptr(arr.a, 0, null, base); }
    return arr;
  };
  P.evMref = function (n, env) {
    const I = this;
    n.ty = TY.dyn;
    let target = null;
    if (n.o.k === 'name' && !env.lookup(n.o.id)) { try { target = this.ev(n.o, env); } catch (e) { target = null; } }
    else target = this.ev(n.o, env);
    const id = n.id;
    return new Fn({ native: (args, tys) => {
      if (id === 'new') {
        if (target instanceof ClassRef) return I.construct(target.ci, args, tys, null, n.line);
        return LIB().make(I, { n: n.o.id }, args, tys, null);
      }
      if (target instanceof ClassRef) {
        const ms = target.ci.methods.get(id) || [];
        const st = ms.find(m => m.static && m.params.length === args.length);
        if (st) return I.invoke(st, null, args, tys, target.ci.name + '.' + id, target.ci);
        const inst = ms.find(m => !m.static && m.params.length === args.length - 1);
        if (inst) return I.invoke(inst, args[0], args.slice(1), tys.slice(1), target.ci.name + '.' + id);
        return I.callOn(args[0], id, args.slice(1), tys.slice(1), [], n);
      }
      if (target instanceof NS) {
        const r = LIB().callStatic(I, target.name, id, args, tys, [], n, true);
        if (r !== undefined && r !== LIB().NONE) return r[0];
        return I.callOn(args[0], id, args.slice(1), tys.slice(1), [], n);
      }
      return I.callOn(target, id, args, tys, [], n);
    }, fname: (n.o.id || '') + '::' + id });
  };
  P.evSwitchExpr = function (n, env) {
    const v = this.ev(n.e, env);
    if (n.cs) {
      for (const arm of n.arms) {
        const se = new Env(env);
        if (this.patMatch(arm.pat, v, n.e.ty, se) && (!arm.guard || this.truthy(this.ev(arm.guard, se)))) { const r = this.ev(arm.e, se); n.ty = arm.e.ty; return r; }
      }
      throw this.ex('InvalidOperationException', 'The switch expression did not match any case (SwitchExpressionException)');
    }
    const fake = { k: 'switch', e: { k: 'lit', v, ty: n.e.ty }, cases: n.cases, arrow: n.arrow, line: n.line };
    const r = this.execSwitch(fake, env);
    if (r instanceof CF.Yield) { n.ty = r.ty; return r.v; }
    if (r instanceof Throw) throw r;
    throw this.ex('IllegalStateException', 'switch expression did not produce a value');
  };

  /* ---------- calls ---------- */
  P.evArgs = function (argNodes, env) {
    const L = this.lang;
    const refs = [];
    const args = [];
    for (let i = 0; i < argNodes.length; i++) {
      const a = argNodes[i];
      if (a.k === 'refarg') { const r = this.ref(a.a, env); refs[i] = r; const v = r.get(); a.ty = r.ty; args.push(v); continue; }
      if (a.k === 'outdecl') { const b = new Box(this.defaultVal(a.tt), a.tt); a.ty = a.tt; env.v.set(a.id, b); refs[i] = { get: () => b.v, set: v => { b.v = v; b.uninit = false; }, ty: a.tt, box: b }; args.push(b.v); continue; }
      if (L === 'cpp' && isLval(a)) {
        const r = this.ref(a, env);
        refs[i] = r;
        let v;
        if (r.box && r.box.uninit) { v = r.box.v; }
        else v = r.get();
        a.ty = r.ty && r.ty.n !== 'var' ? Object.assign({}, r.ty, { ref: false }) : valTy(v);
        if (a.k === 'idx' || a.k === 'mem') { /* types come from the container */ if (!a.ty || a.ty.n === 'dyn') a.ty = valTy(v); }
        args.push(v);
        continue;
      }
      args.push(this.ev(a, env));
    }
    return { args, tys: argNodes.map((a, i) => a.ty || valTy(args[i])), refs };
  };
  P.callFn = function (fn, args, tys, refs, line) {
    if (fn.native) return fn.native(args, tys, refs);
    if (fn.overloads) {
      const m = this.pick(fn.overloads, args, tys, line);
      if (!m) throw new CF.CompileError(`No version of ${fn.fname} takes ${args.length} argument${args.length === 1 ? '' : 's'}`, line);
      return this.invoke(m, m.static ? null : fn.self, args, tys, (fn.cls ? fn.cls.name + '.' : '') + fn.fname, fn.cls, line, refs);
    }
    const m = { params: fn.params, body: fn.body, exprBody: fn.exprBody, closure: fn.closure, line: fn.line, ret: fn.ret, lambda: true, name: fn.name || 'lambda', fname: fn.fname };
    if (this.lang === 'cpp' && refs) { /* lambdas with int& parameters */ }
    const fr = this.frame();
    return this.invoke(m, fn.self || null, args, tys, fn.fname || (fn.anonObj ? fn.anonObj.ci.name + '.' + fn.name : 'lambda'), fn.cls, line, refs);
  };
  P.evCall = function (n, env) {
    const f = n.f;
    const L = this.lang;
    /* method on an object, a class or a library value */
    if (f.k === 'mem') {
      if (f.o.k === 'super') {
        const fr = this.frame();
        const { args, tys, refs } = this.evArgs(n.args, env);
        const base = fr.cls && fr.cls.base;
        const m = base && this.pick(this.allMethods(base, f.id), args, tys, n.line);
        if (!m) {
          if (fr.self && fr.self.ci.exc || (base && base.builtin)) return LIB().objMethod(this, fr.self, f.id, args, tys, n, true);
          throw new CF.CompileError(`The parent class has no method ${f.id}`, n.line);
        }
        n.ty = m.ret;
        return this.invoke(m, fr.self, args, tys, base.name + '.' + f.id, base, n.line, refs);
      }
      let recv, recvRef = null;
      if (f.o.k === 'name' && !env.lookup(f.o.id) && (L === 'java' || L === 'cs') && f.o.id === 'System' ) recv = new NS('System');
      else if ((L === 'cpp') && isLval(f.o) && !f.arrow) {
        try { recvRef = this.ref(f.o, env); recv = recvRef.get(); f.o.ty = recvRef.ty && recvRef.ty.n !== 'var' ? recvRef.ty : valTy(recv); }
        catch (e) { if (e instanceof CF.CompileError && f.o.k === 'name') { recvRef = null; recv = this.ev(f.o, env); } else throw e; }
      }
      else recv = this.ev(f.o, env);
      if (f.arrow) {
        if (recv === null || recv === undefined) throw new Fatal(`The program called ${f.id}() through a NULL pointer${f.o.k === 'name' ? ' (' + f.o.id + ' is NULL)' : ''}. There is no object there, so a real program crashes here`, 'segv');
        if (recv instanceof Ptr) recv = recv.get();
        else if (recv && recv.$iter) recv = recv.get();
      }
      if (f.q && (recv === null || recv === undefined)) { n.ty = TY.dyn; return null; }
      if (recv === null || recv === undefined) {
        if (L === 'java') throw this.ex('NullPointerException', `Cannot invoke "${f.id}()" because "${f.o.k === 'name' ? f.o.id : 'the value'}" is null`);
        if (L === 'cs') throw this.ex('NullReferenceException', 'Object reference not set to an instance of an object.');
        throw new Fatal(`The program called ${f.id}() on a NULL value. A real program crashes here`, 'segv');
      }
      const { args, tys, refs } = this.evArgs(n.args, env);
      return this.callOn(recv, f.id, args, tys, refs, n, recvRef, f.o);
    }
    if (f.k === 'name') {
      const id = f.id;
      const { args, tys, refs } = this.evArgs(n.args, env);
      /* a variable holding a function or lambda */
      const b = env.lookup(id);
      if (b && (b.v instanceof Fn)) { const r = this.callFn(b.v, args, tys, refs, n.line); n.ty = b.v.ret || valTy(r); return r; }
      if (b && b.v && b.v.$callable) { const r = b.v.$call(this, args, tys); n.ty = valTy(r); return r; }
      if (b && b.v instanceof Obj && L === 'cpp') { const m = this.findMethod(b.v.ci, 'operator()', args.length); if (m) { n.ty = m.ret; return this.invoke(m, b.v, args, tys, 'operator()', b.v.ci, n.line, refs); } }
      /* a method of the current class (or an outer class) */
      const fr = this.frame();
      for (let ci = fr && fr.cls; ci; ci = ci.outer) {
        const list = this.allMethods(fr.self && fr.self instanceof Obj && ci === fr.cls ? fr.self.ci : ci, id);
        if (list.length) {
          const m = this.pick(list, args, tys, n.line);
          if (!m) throw new CF.CompileError(L === 'java' ? `method ${id} cannot be applied to ${args.length} argument${args.length === 1 ? '' : 's'}. Check how many values you pass` : `No overload for method '${id}' takes ${args.length} arguments`, n.line);
          if (!m.static && !(fr.self instanceof Obj) && (L === 'java' || L === 'cs')) {
            if (L === 'java') throw new CF.CompileError(`non-static method ${id}() cannot be referenced from a static context. Mark it static, or create an object and call it on that object`, n.line);
            throw new CF.CompileError(`An object reference is required for the non-static method '${id}'. Mark it static, or call it on an object`, n.line);
          }
          n.ty = this.resolveTy(m.ret);
          const r = this.invoke(m, m.static ? null : fr.self, args, tys, (ci.name ? ci.name + '.' : '') + id, ci, n.line, refs);
          if (m.ret && (m.ret.tp || m.ret.n === 'var' || m.ret.n === 'dyn')) n.ty = valTy(r);
          return r;
        }
      }
      /* enum helpers used without a dot inside the enum: values(), ordinal(), name() */
      for (let ci = fr && fr.cls; ci; ci = ci.outer) {
        if (!ci.isEnum) continue;
        const R0 = LIB().classStatic(this, ci, id, args, tys, n);
        if (R0 !== LIB().NONE) { n.ty = R0[1]; return R0[0]; }
        if (fr.self instanceof Obj && fr.self.ci === ci && /^(ordinal|name|compareTo)$/.test(id)) return LIB().objMethod(this, fr.self, id, args, tys, n);
      }
      if (this.funcs.has(id)) {
        const list = this.funcs.get(id);
        const m = this.pick(list, args, tys, n.line);
        if (!m) throw new CF.CompileError(L === 'java' ? `method ${id} cannot be applied to these arguments` : `no matching function for call to '${id}' with ${args.length} argument${args.length === 1 ? '' : 's'}`, n.line);
        if (!m.body) throw new CF.CompileError(`${id} is declared but its body is never written`, n.line);
        const r = this.invoke(m, null, args, tys, id, null, n.line, refs);
        n.ty = m.ret && !m.ret.tp && m.ret.n !== 'var' ? this.resolveTy(m.ret) : valTy(r);
        return r;
      }
      if (b && b.v === null) {
        if (L === 'java') throw this.ex('NullPointerException', null);
        throw new Fatal(`${id} is a null function pointer`, 'segv');
      }
      /* C++ temporary object: Point(1, 2) */
      if (L === 'cpp' && this.classes.get(id) && !b) { const ci = this.classes.get(id); n.ty = { n: id }; return this.construct(ci, args, tys, n.args, n.line, { n: id }); }
      if (L === 'cpp' && !b && /^(runtime_error|out_of_range|invalid_argument|logic_error|exception|length_error|overflow_error|domain_error|range_error|underflow_error|bad_alloc)$/.test(id)) { const ci = this.exClass(id); if (ci) { n.ty = { n: id }; return this.construct(ci, args, tys, n.args, n.line, { n: id }); } }
      if (L === 'cpp' && !b && LIB().isLibType(id) && id !== 'function') { n.ty = { n: id }; return LIB().make(this, { n: id }, args, tys, n.args); }
      const r = LIB().callGlobal(this, id, args, tys, refs, n, env);
      if (r !== LIB().NONE) { n.ty = r[1]; return r[0]; }
      this.notFound(id, n.line);
    }
    if (f.k === 'this' || f.k === 'super') throw new CF.CompileError(`${f.k}(...) can only be the first line of a constructor`, n.line);
    /* anything else that gives a function: getAdder()(5), arr[i](x) */
    const fv = this.ev(f, env);
    const { args, tys, refs } = this.evArgs(n.args, env);
    if (fv instanceof Fn) { const r = this.callFn(fv, args, tys, refs, n.line); n.ty = valTy(r); return r; }
    if (fv instanceof Obj && L === 'cpp') { const m = this.findMethod(fv.ci, 'operator()', args.length); if (m) return this.invoke(m, fv, args, tys, 'operator()', fv.ci, n.line, refs); }
    if (fv && fv.$callable) return fv.$call(this, args, tys);
    throw new CF.CompileError('This value cannot be called like a function', n.line);
  };
  P.allMethods = function (ci, name) {
    const out = [];
    for (let c = ci; c; c = c.base) { const ms = c.methods.get(name); if (ms) ms.forEach(m => { if (!out.some(o => o.params.length === m.params.length && sameParams(o, m))) out.push(m); }); }
    for (const iname of this.allIfaces(ci)) { const ic = this.classes.get(iname); const ms = ic && ic.methods.get(name); if (ms) ms.forEach(m => { if (m.body && !out.some(o => o.params.length === m.params.length)) out.push(m); }); }
    return out;
  };
  function sameParams(a, b) { return a.params.every((p, i) => (p.ty && p.ty.n) === (b.params[i].ty && b.params[i].ty.n) && (p.ty && p.ty.dim) === (b.params[i].ty && b.params[i].ty.dim)); }
  /* call a method by name on any value */
  P.callOn = function (recv, id, args, tys, refs, n, recvRef, onode) {
    const L = this.lang;
    if (recv instanceof NS) {
      const r = LIB().callStatic(this, recv.name, id, args, tys, refs, n);
      if (r === LIB().NONE) throw new CF.CompileError(L === 'java' ? `cannot find symbol: method ${id} in ${recv.name}` : `'${recv.name}' does not contain a definition for '${id}'`, n.line);
      n.ty = r[1];
      return r[0];
    }
    if (recv instanceof ClassRef) {
      const ci = recv.ci;
      this.clinit(ci);
      const list = this.allMethods(ci, id).filter(m => m.static || L === 'cpp');
      if (list.length) {
        const m = this.pick(list, args, tys, n.line);
        if (m) { n.ty = this.resolveTy(m.ret); const r = this.invoke(m, null, args, tys, ci.name + '.' + id, ci, n.line, refs); if (m.ret && (m.ret.tp || m.ret.n === 'var')) n.ty = valTy(r); return r; }
      }
      const inst = this.allMethods(ci, id);
      if (inst.length && (L === 'java' || L === 'cs')) {
        const fr = this.frame();
        if (fr && fr.self instanceof Obj && this.isA(fr.self.ci, ci.name)) { const m = this.pick(inst, args, tys, n.line); n.ty = m.ret; return this.invoke(m, fr.self, args, tys, ci.name + '.' + id, ci, n.line, refs); }
        throw new CF.CompileError(L === 'java' ? `non-static method ${id}() cannot be referenced from a static context` : `An object reference is required for the non-static method '${ci.name}.${id}'`, n.line);
      }
      const r = LIB().classStatic(this, ci, id, args, tys, n);
      if (r !== LIB().NONE) { n.ty = r[1]; return r[0]; }
      throw new CF.CompileError(L === 'java' ? `cannot find symbol: method ${id} in class ${ci.name}` : `'${ci.name}' does not contain a definition for '${id}'`, n.line);
    }
    if (recv instanceof Obj && !recv.ci.builtin || (recv instanceof Obj && recv.ci.fake)) {
      const list = this.allMethods(recv.ci, id);
      if (list.length) {
        const m = this.pick(list, args, tys, n.line);
        if (m) {
          if (!m.body && m.abstract !== false && !m.builtin) throw new CF.CompileError(`${recv.ci.name}.${id} has no body to run`, n.line);
          const r = this.invoke(m, recv, args, tys, recv.ci.name + '.' + id, null, n.line, refs);
          n.ty = m.ret && !(m.ret.tp || m.ret.n === 'var' || m.ret.n === 'dyn') ? this.resolveTy(m.ret) : valTy(r);
          if (m.ret && m.ret.n === 'void') n.ty = TY.void;
          return r;
        }
      }
      /* a field that holds a lambda: obj.handler(x) */
      if (recv.f[id] instanceof Fn) { const r = this.callFn(recv.f[id], args, tys, refs, n.line); n.ty = valTy(r); return r; }
    }
    if (recv instanceof Fn) {
      const r = LIB().fnMethod(this, recv, id, args, tys, refs, n);
      n.ty = r[1];
      return r[0];
    }
    if (recv instanceof Obj) {
      const r = LIB().objMethod(this, recv, id, args, tys, n);
      return r;
    }
    const r = LIB().callMethod(this, recv, id, args, tys, refs, n, recvRef, onode);
    if (r === LIB().NONE) {
      const tn = valTy(recv);
      throw new CF.CompileError(L === 'java' ? `cannot find symbol: method ${id}(...) on a value of type ${javaName(tn)}` : L === 'cs' ? `'${csName(tn)}' does not contain a definition for '${id}'` : `'${tn.n}' has no member named '${id}'`, n.line);
    }
    n.ty = r[1];
    return r[0];
  };
  function javaName(t) { return ({ string: 'String', int: 'int', bool: 'boolean', double: 'double', char: 'char', long: 'long' }[t.n] || t.n) + (t.dim ? '[]'.repeat(t.dim) : ''); }
  function csName(t) { return ({ string: 'string', int: 'int', bool: 'bool', double: 'double', char: 'char', long: 'long' }[t.n] || t.n) + (t.dim ? '[]'.repeat(t.dim) : ''); }
  P.setMember = function (o, id, v, ty, line) {
    const ff = this.findField(o.ci, id);
    if (!ff) throw new CF.CompileError(`${o.ci.name} has no member called ${id}`, line);
    if (ff.f.prop && ff.f.prop.set && ff.f.prop.set !== 'auto') return this.setProp(o, ff.f, v);
    o.f[id] = this.convStore(ff.f.ty, v);
  };
  P.objStrPlain = function (o) { return this.objStr(o); };
  CF.isLval = isLval;
})();
