/* ===== Code Playground: the standard library pieces beginners use =====
   Printing and reading (System.out, Scanner, Console, printf, scanf, cout, cin), strings, maths,
   lists, maps, sets, stacks, queues, priority queues, StringBuilder, Java streams, C# LINQ and the C++ algorithms.
   Each container prints the way its language prints it, and Java's HashMap lists keys in Java's own order. */
(() => {
  const G = typeof self !== 'undefined' ? self : globalThis;
  const CF = G.CF;
  const { Arr, Obj, Fn, Ptr, Box, ClassRef, NS, Fatal, Throw, TY } = CF;
  const { kindOf, promote, KT, NK, toNum, toBig, isArrTy, isPtrTy, plain, valTy, chr, i32 } = CF;
  const NONE = { none: true };
  const R = (v, ty) => [v, ty || CF.valTy(v)];
  const T = (n, extra) => Object.assign({ n }, extra || {});
  const L = I => I.lang;

  /* ---------- input ---------- */
  function noInput(I) {
    if (I.stdin && I.stdin.trim()) return; /* reading until the input runs out is normal */
    I.warn('noinput', 'The program asked for input, but the Input box had nothing left to read. Type the values in the Input box (one per line or separated by spaces) and run again.');
  }
  const Input = {
    skipWs(I) { while (I.inPos < I.stdin.length && /\s/.test(I.stdin[I.inPos])) I.inPos++; },
    token(I) {
      Input.skipWs(I);
      if (I.inPos >= I.stdin.length) { noInput(I); return null; }
      let s = '';
      while (I.inPos < I.stdin.length && !/\s/.test(I.stdin[I.inPos])) s += I.stdin[I.inPos++];
      return s;
    },
    peekToken(I) { const save = I.inPos; const t = Input.token(I); I.inPos = save; I.warned.delete('noinput'); if (t === null) I.notes = I.notes.filter(x => !x.startsWith('The program asked for input')); return t; },
    line(I) {
      if (I.inPos >= I.stdin.length) { noInput(I); return null; }
      const e = I.stdin.indexOf('\n', I.inPos);
      let s;
      if (e < 0) { s = I.stdin.slice(I.inPos); I.inPos = I.stdin.length; }
      else { s = I.stdin.slice(I.inPos, e); I.inPos = e + 1; }
      return s.replace(/\r$/, '');
    },
    char(I) { if (I.inPos >= I.stdin.length) { noInput(I); return -1; } return I.stdin.charCodeAt(I.inPos++); }
  };
  CF.Input = Input;

  /* ---------- comparing and sorting ---------- */
  const csColl = typeof Intl !== 'undefined' ? new Intl.Collator('en') : null;
  function natCmp(I, a, b) {
    if (typeof a === 'string' && typeof b === 'string') {
      if (I.lang === 'cs' && csColl) return csColl.compare(a, b);
      return a < b ? -1 : a > b ? 1 : 0;
    }
    if (a instanceof Obj) {
      const m = I.findMethod(a.ci, I.lang === 'cs' ? 'CompareTo' : 'compareTo', 1);
      if (m) return toNum(I.invoke(m, a, [b], [null], a.ci.name + '.compareTo'));
      if (a.ci.isEnum) return a.f.$ord - b.f.$ord;
      const lt = I.findMethod(a.ci, 'operator<', 1);
      if (lt) return I.invoke(lt, a, [b], [null], 'operator<') ? -1 : I.invoke(lt, b, [a], [null], 'operator<') ? 1 : 0;
      if (I.lang === 'java') throw I.ex('ClassCastException', `class ${a.ci.name} cannot be cast to class java.lang.Comparable. Implement Comparable or pass a Comparator`);
      if (I.lang === 'cs') throw I.ex('InvalidOperationException', 'Failed to compare two elements in the array. Implement IComparable or pass a comparison');
      throw new CF.CompileError(`no match for operator< on ${a.ci.name}. Add bool operator<(const ${a.ci.name}& o) const`, I.lastLine);
    }
    if (a && a.$lib && a.$cmp) return a.$cmp(b, I);
    if (a && a.$enum) return a.val - b.val;
    if (typeof a === 'boolean') return (a ? 1 : 0) - (b ? 1 : 0);
    if (a === null || b === null) { if (I.lang === 'java') throw I.ex('NullPointerException', null); return a === b ? 0 : a === null ? -1 : 1; }
    return a < b ? -1 : a > b ? 1 : 0;
  }
  function cmpFrom(I, fn, kind) {
    if (!fn) return (a, b) => natCmp(I, a, b);
    if (fn.$greater) return (a, b) => natCmp(I, b, a);
    if (fn.$less) return (a, b) => natCmp(I, a, b);
    if (fn instanceof Obj && I.lang === 'cpp') {
      const m = I.findMethod(fn.ci, 'operator()', 2);
      return (a, b) => I.invoke(m, fn, [a, b], [null, null], 'compare') ? -1 : I.invoke(m, fn, [b, a], [null, null], 'compare') ? 1 : 0;
    }
    if (fn instanceof Obj) {
      const m = I.findMethod(fn.ci, I.lang === 'cs' ? 'Compare' : 'compare', 2);
      if (m) return (a, b) => toNum(I.invoke(m, fn, [a, b], [null, null], 'compare'));
    }
    if (I.lang === 'cpp' || kind === 'less') return (a, b) => { const r = I.callFn(fn, [a, b], [null, null]); if (typeof r !== 'boolean' && I.lang !== 'cpp') return toNum(r); return I.truthy(r) ? -1 : I.truthy(I.callFn(fn, [b, a], [null, null])) ? 1 : 0; };
    return (a, b) => toNum(I.callFn(fn, [a, b], [null, null]));
  }
  function sortArr(I, a, cmp) { a.sort((x, y) => cmp(x, y)); return a; }
  CF.natCmp = natCmp;

  /* ---------- text forms of values inside containers ---------- */
  function el(I, v, ty) { return I.str(v, ty); }
  function shortEl(I, v, ty, d) { return I.short(v, ty, d + 1); }

  /* ---------- base for library objects ---------- */
  const Base = {
    $lib: true,
    $short(I, d) { return this.$str(I); },
    $truthy() { return true; }
  };
  function proto(base, obj) { return Object.defineProperties(Object.create(base), Object.getOwnPropertyDescriptors(obj)); }
  function mk(proto, fields) { const o = Object.create(proto); Object.assign(o, fields); o.id = ++CF.$ids; return o; }
  CF.$ids = 100000;

  /* ===== lists, stacks and queues ===== */
  const ListP = proto(Base, {
    $ty() { return T(this.kind, { args: [this.et || TY.dyn] }); },
    $is(n) { return ['List', 'ArrayList', 'LinkedList', 'Collection', 'Iterable', 'IList', 'IEnumerable', 'ICollection', 'vector', 'Stack', 'Queue', 'Deque', 'ArrayDeque', 'stack', 'queue', 'deque', 'list', 'IReadOnlyList', 'AbstractList', 'Vector'].includes(n) && (n === this.kind || !['Stack', 'Queue', 'stack', 'queue'].includes(n) || this.kind === n); },
    $setTy(ty) { if (!this.et || this.et.n === 'dyn') { if (ty.args && ty.args[0]) this.et = ty.args[0]; } },
    $str(I) {
      if (I.lang === 'java') { const items = this.view(I).map(x => x === this ? '(this Collection)' : el(I, x, this.et)); return '[' + items.join(', ') + ']'; }
      if (I.lang === 'cs') return 'System.Collections.Generic.' + ({ StackCS: 'Stack', QueueCS: 'Queue' }[this.kind] || this.kind === 'LinkedList' ? (this.kind === 'StackCS' ? 'Stack' : this.kind === 'QueueCS' ? 'Queue' : this.kind) : 'List') + '`1[System.' + csTn(this.et) + ']';
      throw new CF.CompileError(`cout cannot print a whole ${this.kind}. Print it with a loop: for (auto x : v) cout << x << " ";`, I.lastLine);
    },
    $short(I, d) {
      const v = this.view(I);
      const items = v.slice(0, 20).map(x => shortEl(I, x, this.et, d));
      const lab = { StackCS: 'top first', stack: 'top is last', queue: 'front first' }[this.kind];
      return '[' + items.join(', ') + (v.length > 20 ? ', … ' + v.length + ' items' : '') + ']' + (lab && v.length > 1 ? ' (' + lab + ')' : '');
    },
    view() { return this.kind === 'StackCS' ? this.a.slice().reverse() : this.a; },
    $copy(I) { return mk(ListP, { a: this.a.map(x => I.copyVal(x)), et: this.et, kind: this.kind }); },
    $eq(b, I) { return b && b.$lib && b.a && b.a.length === this.a.length && this.a.every((x, i) => I.equals(x, b.a[i])); },
    $hash(I) { let h = 1; for (const x of this.a) h = (Math.imul(31, h) + I.hashOf(x)) | 0; return h; },
    $cmp(b) { /* C++ vectors compare element by element */ for (let i = 0; i < Math.min(this.a.length, b.a.length); i++) { if (this.a[i] < b.a[i]) return -1; if (this.a[i] > b.a[i]) return 1; } return this.a.length - b.a.length; }
  });
  function newList(I, kind, et, items) { return mk(ListP, { a: items || [], et: et || null, kind }); }
  function csTn(t) { if (!t) return 'Object'; return { int: 'Int32', long: 'Int64', double: 'Double', string: 'String', char: 'Char', bool: 'Boolean', float: 'Single' }[t.n] || t.n; }

  /* ===== maps ===== */
  function keyOf(I, k) {
    if (k === null || k === undefined) return 'null';
    if (typeof k === 'number' || typeof k === 'bigint' || typeof k === 'boolean') return typeof k === 'bigint' ? 'n' + k : (typeof k === 'boolean' ? 'b' + k : k);
    if (typeof k === 'string') return 's' + k;
    if (k instanceof Obj && (k.ci.record || I.findMethod(k.ci, I.lang === 'cs' ? 'Equals' : 'equals', 1) || I.lang === 'cpp')) return 'o' + I.hashOf(k) + ':' + JSON.stringify(Object.keys(k.f).map(x => String(k.f[x])));
    if (k && k.$lib && k.$key) return k.$key(I);
    if (k && k.$lib && k.a) return 'l' + k.a.map(x => keyOf(I, x)).join(',');
    return k;
  }
  const SORTED = new Set(['TreeMap', 'SortedDictionary', 'map', 'TreeSet', 'SortedSet', 'set', 'multiset', 'multimap', 'SortedList']);
  const JHASH = new Set(['HashMap', 'HashSet', 'Hashtable']);
  const REVINS = new Set(['unordered_map', 'unordered_set']);
  function orderOf(I, c, keys) {
    /* keys: [[normKey, rec]] in insertion order */
    if (SORTED.has(c.kind)) { const cmp = c.cmp ? cmpFrom(I, c.cmp) : (a, b) => natCmp(I, a, b); return keys.slice().sort((x, y) => cmp(x[1].k, y[1].k)); }
    if (JHASH.has(c.kind) && I.lang === 'java') {
      const cap = c.cap || 16;
      return keys.slice().sort((x, y) => { const hx = spread(I, x[1].k, c.kt || c.et) & (cap - 1), hy = spread(I, y[1].k, c.kt || c.et) & (cap - 1); return hx - hy || x[1].seq - y[1].seq; });
    }
    if (REVINS.has(c.kind)) return keys.slice().reverse();
    return keys;
  }
  function spread(I, k, kt) {
    let h;
    if (kt && kt.n === 'double' && typeof k === 'number') h = CF.dblHash(k);
    else if (kt && kt.n === 'long' && typeof k === 'bigint') h = Number(BigInt.asIntN(32, k ^ (k >> 32n)));
    else h = I.hashOf(k);
    return (h ^ (h >>> 16)) >>> 0;
  }
  function grow(c) { if (c.cap) { while (c.m.size > c.cap * 0.75) c.cap *= 2; } }
  const MapP = proto(Base, {
    $ty() { return T(this.kind, { args: [this.kt || TY.dyn, this.vt || TY.dyn] }); },
    $is(n) { return ['Map', 'HashMap', 'TreeMap', 'LinkedHashMap', 'Dictionary', 'IDictionary', 'SortedDictionary', 'map', 'unordered_map', 'IEnumerable', 'SortedMap', 'NavigableMap', 'IReadOnlyDictionary', 'multimap'].includes(n); },
    $setTy(ty) { if (ty.args && ty.args.length >= 2) { if (!this.kt || this.kt.n === 'dyn') this.kt = ty.args[0]; if (!this.vt || this.vt.n === 'dyn') this.vt = ty.args[1]; } },
    ents(I) { return orderOf(I, this, [...this.m.entries()]).map(x => x[1]); },
    get(I, k) { const r = this.m.get(keyOf(I, k)); return r; },
    put(I, k, v) {
      const key = keyOf(I, k);
      const r = this.m.get(key);
      if (r) { const old = r.v; r.v = v; return old; }
      if (this.kind === 'TreeMap' && k === null) throw I.ex('NullPointerException', null);
      this.m.set(key, { k, v, seq: ++this.seq }); grow(this);
      return undefined;
    },
    del(I, k) { const key = keyOf(I, k); const r = this.m.get(key); if (r) this.m.delete(key); return r; },
    $str(I) {
      if (I.lang === 'java') return '{' + this.ents(I).map(e => el(I, e.k, this.kt) + '=' + (e.v === this ? '(this Map)' : el(I, e.v, this.vt))).join(', ') + '}';
      if (I.lang === 'cs') return 'System.Collections.Generic.' + this.kind + '`2[System.' + csTn(this.kt) + ',System.' + csTn(this.vt) + ']';
      throw new CF.CompileError(`cout cannot print a whole map. Print it with a loop: for (auto& [k, v] : m) cout << k << " " << v << "\\n";`, I.lastLine);
    },
    $short(I, d) { const es = this.ents(I); return '{' + es.slice(0, 15).map(e => shortEl(I, e.k, this.kt, d) + ': ' + shortEl(I, e.v, this.vt, d)).join(', ') + (es.length > 15 ? ', …' : '') + '}'; },
    $copy(I) { const c = mk(MapP, { m: new Map(), kt: this.kt, vt: this.vt, kind: this.kind, seq: this.seq, cap: this.cap, cmp: this.cmp }); for (const [k, r] of this.m) c.m.set(k, { k: r.k, v: I.copyVal(r.v), seq: r.seq }); return c; },
    $eq(b, I) { if (!b || !b.m || b.m.size !== this.m.size) return false; for (const [k, r] of this.m) { const o = b.m.get(k); if (!o || !I.equals(r.v, o.v)) return false; } return true; }
  });
  function newMap(I, kind, kt, vt, cap) {
    const c = mk(MapP, { m: new Map(), kt: kt || null, vt: vt || null, kind, seq: 0 });
    if (JHASH.has(kind) && I.lang === 'java') { let n = 16; if (cap) { n = 1; while (n < cap) n *= 2; } c.cap = n; }
    return c;
  }
  /* ===== sets ===== */
  const SetP = proto(Base, {
    $ty() { return T(this.kind, { args: [this.et || TY.dyn] }); },
    $is(n) { return ['Set', 'HashSet', 'TreeSet', 'LinkedHashSet', 'SortedSet', 'ISet', 'set', 'unordered_set', 'multiset', 'Collection', 'Iterable', 'IEnumerable', 'NavigableSet'].includes(n); },
    $setTy(ty) { if ((!this.et || this.et.n === 'dyn') && ty.args && ty.args[0]) this.et = ty.args[0]; },
    items(I) { if (this.kind === 'multiset') return this.multi.slice().sort((a, b) => (this.cmp ? cmpFrom(I, this.cmp) : (x, y) => natCmp(I, x, y))(a, b)); return orderOf(I, this, [...this.m.entries()]).map(x => x[1].k); },
    has(I, v) { if (this.kind === 'multiset') return this.multi.some(x => I.equals(x, v)); return this.m.has(keyOf(I, v)); },
    add(I, v) { if (this.kind === 'multiset') { this.multi.push(v); return true; } const k = keyOf(I, v); if (this.m.has(k)) return false; if (this.kind === 'TreeSet' && v === null) throw I.ex('NullPointerException', null); this.m.set(k, { k: v, seq: ++this.seq }); grow(this); return true; },
    del(I, v) { if (this.kind === 'multiset') { const i = this.multi.findIndex(x => I.equals(x, v)); if (i >= 0) { this.multi.splice(i, 1); return true; } return false; } return this.m.delete(keyOf(I, v)); },
    size() { return this.kind === 'multiset' ? this.multi.length : this.m.size; },
    $str(I) {
      if (I.lang === 'java') return '[' + this.items(I).map(x => el(I, x, this.et)).join(', ') + ']';
      if (I.lang === 'cs') return 'System.Collections.Generic.' + this.kind + '`1[System.' + csTn(this.et) + ']';
      throw new CF.CompileError('cout cannot print a whole set. Print it with a loop: for (auto x : s) cout << x << " ";', I.lastLine);
    },
    $short(I, d) { const it = this.items(I); return '{' + it.slice(0, 20).map(x => shortEl(I, x, this.et, d)).join(', ') + (it.length > 20 ? ', …' : '') + '}'; },
    $copy(I) { const c = mk(SetP, { m: new Map(this.m), et: this.et, kind: this.kind, seq: this.seq, cap: this.cap, cmp: this.cmp, multi: this.multi && this.multi.slice() }); return c; },
    $eq(b, I) { return b && b.m && b.size() === this.size() && this.items(I).every(x => b.has(I, x)); },
    $hash(I) { let h = 0; for (const x of this.items(I)) h = (h + I.hashOf(x)) | 0; return h; }
  });
  function newSet(I, kind, et, cap) {
    const c = mk(SetP, { m: new Map(), et: et || null, kind, seq: 0 });
    if (kind === 'multiset') c.multi = [];
    if (JHASH.has(kind) && I.lang === 'java') { let n = 16; if (cap) { n = 1; while (n < cap) n *= 2; } c.cap = n; }
    return c;
  }
  /* ===== priority queues (binary heaps, the same sift steps as Java) ===== */
  const PQP = proto(Base, {
    $ty() { return T('PriorityQueue', { args: [this.et || TY.dyn] }); },
    $is(n) { return ['PriorityQueue', 'Queue', 'Collection', 'priority_queue', 'AbstractQueue'].includes(n); },
    $setTy(ty) { if ((!this.et || this.et.n === 'dyn') && ty.args && ty.args[0]) this.et = ty.args[0]; },
    less(I, a, b) { const c = this.cmpf(I)(a, b); return this.max ? c > 0 : c < 0; },
    cmpf(I) { return this.$c || (this.$c = cmpFrom(I, this.cmp)); },
    push(I, x, pr) {
      const q = this.q; let k = q.length; q.push(null);
      const item = pr === undefined ? x : { e: x, p: pr };
      const key = v => pr === undefined ? v : v.p;
      while (k > 0) { const p = (k - 1) >>> 1; const e = q[p]; if (!this.less(I, key(item), key(e))) break; q[k] = e; k = p; }
      q[k] = item;
    },
    pop(I) {
      const q = this.q; if (!q.length) return undefined;
      const top = q[0]; const last = q.pop();
      if (q.length) {
        const key = v => this.cs ? v.p : v;
        let k = 0; const n = q.length, half = n >>> 1;
        while (k < half) {
          let c = 2 * k + 1; const r = c + 1;
          if (r < n && this.less(I, key(q[r]), key(q[c]))) c = r;
          if (!this.less(I, key(q[c]), key(last))) break;
          q[k] = q[c]; k = c;
        }
        q[k] = last;
      }
      return top;
    },
    $str(I) { if (I.lang === 'java') return '[' + this.q.map(x => el(I, x, this.et)).join(', ') + ']'; if (I.lang === 'cs') return 'System.Collections.Generic.PriorityQueue`2'; throw new CF.CompileError('cout cannot print a priority_queue', I.lastLine); },
    $short(I, d) { const items = this.cs ? this.q.map(x => shortEl(I, x.e, null, d) + ' (priority ' + shortEl(I, x.p, null, d) + ')') : this.q.map(x => shortEl(I, x, this.et, d)); return '[' + items.slice(0, 20).join(', ') + ']' + (this.q.length > 1 ? ' (heap order, top first)' : ''); },
    $copy(I) { return mk(PQP, { q: this.q.slice(), et: this.et, cmp: this.cmp, max: this.max, cs: this.cs }); }
  });
  /* ===== StringBuilder ===== */
  const SBP = proto(Base, {
    $ty() { return T('StringBuilder'); }, $is(n) { return n === 'StringBuilder' || n === 'CharSequence' || n === 'StringBuffer'; },
    $str() { return this.s; }, $short() { return JSON.stringify(this.s); }
  });
  /* ===== pairs, entries and tuples ===== */
  const PairP = proto(Base, {
    $ty() { return T('pair', { args: [this.t1 || TY.dyn, this.t2 || TY.dyn] }); }, $is(n) { return ['pair', 'Entry', 'KeyValuePair', 'Map.Entry'].includes(n); },
    $setTy(ty) { if (ty.args && ty.args.length === 2) { this.t1 = this.t1 && this.t1.n !== 'dyn' ? this.t1 : ty.args[0]; this.t2 = this.t2 && this.t2.n !== 'dyn' ? this.t2 : ty.args[1]; this.a = this.a !== undefined ? this.a : null; } },
    get first() { return this.rec ? this.rec.k : this.a; }, get second() { return this.rec ? this.rec.v : this.b; },
    $str(I) { if (I.lang === 'java') return el(I, this.first, this.t1) + '=' + el(I, this.second, this.t2); if (I.lang === 'cs') return '[' + el(I, this.first, this.t1) + ', ' + el(I, this.second, this.t2) + ']'; throw new CF.CompileError('cout cannot print a pair. Print p.first and p.second', I.lastLine); },
    $short(I, d) { return '(' + shortEl(I, this.first, this.t1, d) + ', ' + shortEl(I, this.second, this.t2, d) + ')'; },
    $copy(I) { return mk(PairP, { a: I.copyVal(this.first), b: I.copyVal(this.second), t1: this.t1, t2: this.t2 }); },
    $eq(o, I) { return o && o.$is && o.$is('pair') && I.equals(this.first, o.first) && I.equals(this.second, o.second); },
    $cmp(o, I) { return natCmp(I, this.first, o.first) || natCmp(I, this.second, o.second); },
    $key(I) { return 'p' + keyOf(I, this.first) + '|' + keyOf(I, this.second); },
    $hash(I) { return I.hashOf(this.first) ^ I.hashOf(this.second); }
  });
  function pair(a, b, t1, t2) { return mk(PairP, { a, b, t1, t2 }); }
  const TupleP = proto(Base, {
    $ty() { return T('tuple'); }, $is(n) { return n === 'tuple' || n === 'ValueTuple' || n === 'Tuple'; },
    $str(I) { return '(' + this.items.map((x, i) => el(I, x, this.tys[i])).join(', ') + ')'; },
    $short(I, d) { return '(' + this.items.map((x, i) => shortEl(I, x, this.tys[i], d)).join(', ') + ')'; },
    $eq(o, I) { return o && o.items && o.items.length === this.items.length && this.items.every((x, i) => I.equals(x, o.items[i])); },
    $key(I) { return 't' + this.items.map(x => keyOf(I, x)).join('|'); },
    $cmp(o, I) { for (let i = 0; i < this.items.length; i++) { const c = natCmp(I, this.items[i], o.items[i]); if (c) return c; } return 0; },
    $hash(I) { let h = 0; for (const x of this.items) h = (Math.imul(31, h) + I.hashOf(x)) | 0; return h; }
  });
  /* ===== Java Optional ===== */
  const OptP = proto(Base, {
    $ty() { return T('Optional'); }, $is(n) { return /^Optional/.test(n); },
    $str(I) { return this.has ? (this.kind || 'Optional') + '[' + el(I, this.v, this.ty) + ']' : (this.kind || 'Optional') + '.empty'; }
  });
  function opt(v, ty, kind) { return mk(OptP, { v, has: v !== undefined && v !== null, ty, kind }); }
  /* ===== sequences: Java streams and C# LINQ results ===== */
  const SeqP = proto(Base, {
    $ty() { return T('Stream', { args: [this.et || TY.dyn] }); }, $is(n) { return ['Stream', 'IntStream', 'IEnumerable', 'IOrderedEnumerable', 'DoubleStream', 'LongStream'].includes(n); },
    $str(I) { if (I.lang === 'cs') return 'System.Linq.Enumerable+Iterator`1[System.' + csTn(this.et) + ']'; return 'java.util.stream.ReferencePipeline@' + I.hashHex(this); },
    $short(I, d) { return 'sequence [' + this.a.slice(0, 20).map(x => shortEl(I, x, this.et, d)).join(', ') + ']'; }
  });
  function seq(a, et, prim) { return mk(SeqP, { a, et, prim }); }
  /* ===== C# anonymous objects and C++ stringstreams ===== */
  const AnonP = proto(Base, {
    $ty() { return T('anon'); }, $is() { return false; },
    $str(I) { return '{ ' + this.keys.map(k => k + ' = ' + el(I, this.f[k], this.t[k])).join(', ') + ' }'; }
  });
  const SSP = proto(Base, {
    $ty() { return T('stringstream'); }, $is(n) { return /stringstream/.test(n); },
    $str() { return this.buf; }, $short() { return 'stream ' + JSON.stringify(this.buf); }
  });
  const RandomP = proto(Base, { $ty() { return T('Random'); }, $is(n) { return n === 'Random'; }, $str(I) { return I.lang === 'java' ? 'java.util.Random@' + I.hashHex(this) : 'System.Random'; } });
  const ScannerP = proto(Base, { $ty() { return T('Scanner'); }, $is(n) { return n === 'Scanner' || n === 'BufferedReader'; }, $str() { return 'java.util.Scanner'; }, $short() { return 'Scanner (reads the Input box)'; } });
  const IterP = proto(Base, {
    $iter: true,
    $ty() { return T('iterator'); }, $is(n) { return n === 'iterator' || n === 'Iterator'; },
    arr() { return this.keys || (this.c.a !== undefined ? this.c.a : this.c.q); },
    get(I) {
      if (this.jit) return undefined;
      const a = this.arr();
      const i = this.rev ? a.length - 1 - this.i : this.i;
      if (this.str) { const s = this.ref.get(); if (i < 0 || i >= s.length) throw new Fatal('The iterator points past the end of the string. Reading it is undefined behaviour'); return s.charCodeAt(i); }
      if (i < 0 || i >= a.length) throw new Fatal('The iterator points past the end of the container (end() is one step after the last item). Reading *it there is undefined behaviour, and real programs often crash or print garbage');
      if (this.map) { const r = this.map.m.get(a[i]); return mk(PairP, { rec: r, t1: this.map.kt, t2: this.map.vt }); }
      if (this.set) return a[i];
      return a[i];
    },
    set(v) { const a = this.arr(); const i = this.rev ? a.length - 1 - this.i : this.i; if (this.str) { const s = this.ref.get(); this.ref.set(s.slice(0, i) + chr(v) + s.slice(i + 1)); return; } a[i] = v; },
    move(n) { this.i += n; }, clone() { return mk(IterP, Object.assign({}, this, { id: ++CF.$ids })); },
    $eqIter(b) { return this.c === b.c && this.i === b.i && !!this.rev === !!b.rev; },
    $eq(b) { return b && b.$iter && this.$eqIter(b); },
    $str() { return 'iterator'; }, $short() { return 'iterator at position ' + this.i; }
  });
  function iter(c, i, extra) { return mk(IterP, Object.assign({ c, i }, extra || {})); }

  /* ===== making library values ===== */
  const LIBTYPES = new Set(['ArrayList', 'List', 'LinkedList', 'Vector', 'HashMap', 'Map', 'TreeMap', 'LinkedHashMap', 'HashSet', 'Set', 'TreeSet', 'LinkedHashSet', 'Stack', 'Queue', 'Deque', 'ArrayDeque',
    'PriorityQueue', 'StringBuilder', 'StringBuffer', 'Random', 'Scanner', 'BufferedReader', 'InputStreamReader', 'Dictionary', 'SortedDictionary', 'SortedSet', 'SortedList', 'KeyValuePair', 'Tuple', 'Entry',
    'vector', 'map', 'unordered_map', 'set', 'unordered_set', 'multiset', 'stack', 'queue', 'deque', 'priority_queue', 'pair', 'list', 'array', 'stringstream', 'ostringstream', 'istringstream',
    'function', 'Func', 'Action', 'Predicate', 'Comparison', 'greater', 'less', 'Object', 'object', 'Thread', 'Exception', 'AbstractMap.SimpleEntry', 'SimpleEntry', 'numeric_limits', 'IList', 'IDictionary', 'Collection', 'tuple', 'Optional']);
  const LIB = CF.LIB = {
    NONE,
    isLibType(n) { return LIBTYPES.has(n); },
    tuple(I, items, tys) { return mk(TupleP, { items, tys: tys || items.map(valTy) }); },
    csEnumVal(I, ci, v) {
      I.clinit(ci);
      for (const b of ci.sf.values()) if (b.v && b.v.$enum && b.v.val === v) return b.v;
      const o = Object.create(CF.CSENUM); Object.assign(o, { $lib: true, $enum: ci, name: String(v), val: v }); return o;
    },
    anon(I, pairs) { const o = mk(AnonP, { keys: pairs.map(p => p[0]), f: {}, t: {} }); pairs.forEach(([k, v, t]) => { o.f[k] = v; o.t[k] = t; }); return o; },
    make(I, ty, args, tys, nodes, initVals, initTys, csInit, env, refs) {
      const n = ty.n, a0 = ty.args && ty.args[0], a1 = ty.args && ty.args[1];
      const lang = I.lang;
      let v;
      if (ty.of && ty.of.n === 'numeric_limits') return limits(I, ty.of.args[0], n);
      switch (n) {
        case 'ArrayList': case 'LinkedList': case 'List': case 'Vector': case 'IList': case 'Collection':
          v = newList(I, lang === 'cs' ? (n === 'LinkedList' ? 'LinkedList' : 'List') : (n === 'List' ? 'ArrayList' : n), a0);
          if (args.length && args[0] && typeof args[0] === 'object') v.a = collItems(I, args[0]);
          break;
        case 'vector': case 'list': case 'deque': case 'array': {
          v = newList(I, n, a0);
          if (n === 'array') { const len = ty.args && ty.args[1] && ty.args[1].val; v.a = Array.from({ length: len || 0 }, () => I.defaultVal(a0)); v.std = true; }
          if (args.length === 1 && typeof args[0] === 'object' && args[0] && args[0].a) v.a = args[0].a.map(x => I.copyVal(x));
          else if (args.length >= 1 && (typeof args[0] === 'number' || typeof args[0] === 'bigint')) {
            if (nodes && nodes.length && nodes[0] && nodes[0].k === 'arr') { v.a = args[0].a; }
            else { const cnt = toNum(args[0]); if (cnt < 0 || cnt > 5e6) throw new Fatal('A vector of ' + cnt + ' elements cannot be made'); v.a = Array.from({ length: cnt }, () => args.length > 1 ? I.copyVal(I.conv(args[1], a0)) : I.defaultVal(a0)); }
          } else if (args.length === 2 && args[0] && args[0].$iter) { v.a = range(I, args[0], args[1]).a.slice(range(I, args[0], args[1]).lo, range(I, args[0], args[1]).hi); }
          else if (args.length === 2 && args[0] instanceof Ptr) { const r = range(I, args[0], args[1]); v.a = r.a.slice(r.lo, r.hi); }
          else if (args.length && args[0] instanceof Arr) v.a = args[0].a.slice();
          break;
        }
        case 'Stack': v = newList(I, lang === 'cs' ? 'StackCS' : 'Stack', a0); if (args[0] && args[0].$lib) { v.a = collItems(I, args[0]); } break;
        case 'Queue': if (lang === 'java') throw new CF.CompileError('Queue is an interface and cannot be created with new. Use new LinkedList<>() or new ArrayDeque<>()', nodes && nodes[0] ? nodes[0].line : I.lastLine);
          v = newList(I, 'QueueCS', a0); if (args[0] && args[0].$lib) v.a = collItems(I, args[0]); break;
        case 'ArrayDeque': case 'Deque': v = newList(I, 'ArrayDeque', a0); if (args[0] && args[0].$lib) v.a = collItems(I, args[0]); break;
        case 'stack': case 'queue': v = newList(I, n, a0); if (args[0] && args[0].a) v.a = args[0].a.slice(); break;
        case 'HashMap': case 'TreeMap': case 'LinkedHashMap': case 'Map': case 'Dictionary': case 'SortedDictionary': case 'SortedList': case 'IDictionary': case 'map': case 'unordered_map': case 'multimap':
          v = newMap(I, n === 'Map' ? 'HashMap' : n === 'IDictionary' ? 'Dictionary' : n, a0, a1, typeof args[0] === 'number' ? args[0] : 0);
          if (n === 'TreeMap' && args[0] instanceof Fn) v.cmp = args[0];
          if (args[0] && args[0].$lib && args[0].m) { for (const e of args[0].ents(I)) v.put(I, e.k, e.v); }
          break;
        case 'HashSet': case 'TreeSet': case 'LinkedHashSet': case 'Set': case 'SortedSet': case 'set': case 'unordered_set': case 'multiset':
          v = newSet(I, n === 'Set' ? 'HashSet' : n, a0, typeof args[0] === 'number' ? Math.max(Math.floor(args[0] / 0.75) + 1, 16) : 0);
          if (args[0] instanceof Fn || (args[0] && args[0].$greater)) v.cmp = args[0];
          else if (args.length && args[0] && typeof args[0] === 'object') { const items = args[0].$iter ? (() => { const r = range(I, args[0], args[1]); return r.a.slice(r.lo, r.hi); })() : collItems(I, args[0]); if (JHASH.has(v.kind) && lang === 'java' && args[0].$lib) { v.cap = 16; let need = Math.max(Math.floor(items.length / 0.75) + 1, 16); while (v.cap < need) v.cap *= 2; } items.forEach(x => v.add(I, x)); }
          break;
        case 'PriorityQueue': case 'priority_queue': {
          v = mk(PQP, { q: [], et: a0, cmp: null, max: n === 'priority_queue', cs: lang === 'cs' });
          if (lang === 'cs') v.et = a1 || a0;
          const fnArg = args.find(x => x instanceof Fn || (x && (x.$greater || x.$less)) || x instanceof Obj);
          if (fnArg) v.cmp = fnArg;
          if (n === 'priority_queue' && ty.args && ty.args[2]) { if (ty.args[2].n === 'greater') { v.max = false; } else if (ty.args[2].n !== 'less') { const ci = I.classes.get(ty.args[2].n); if (ci) { v.cmp = I.construct(ci, [], [], null, null); v.max = true; } } }
          if (n === 'priority_queue' && fnArg instanceof Fn) { v.max = true; }
          if (args[0] && args[0].$lib && args[0].a) args[0].a.forEach(x => v.push(I, x));
          break;
        }
        case 'StringBuilder': case 'StringBuffer': v = mk(SBP, { s: args.length && typeof args[0] !== 'number' ? I.str(args[0], tys[0]) : '' }); break;
        case 'Random': v = mk(RandomP, { seed: args.length ? javaSeed(toBig(args[0])) : javaSeed(BigInt(Date.now()) ^ 0x5DEECE66Dn * 7n), csSeed: args.length ? toNum(args[0]) : null }); if (lang === 'cs') v.rng = mulberry(args.length ? toNum(args[0]) : (Date.now() & 0x7fffffff)); break;
        case 'Scanner': case 'BufferedReader': case 'InputStreamReader': v = mk(ScannerP, {}); break;
        case 'pair': case 'KeyValuePair': case 'Entry': case 'SimpleEntry': case 'AbstractMap.SimpleEntry': v = pair(args[0] !== undefined ? I.conv(args[0], a0) : I.defaultVal(a0), args[1] !== undefined ? I.conv(args[1], a1) : I.defaultVal(a1), a0 || tys[0], a1 || tys[1]); break;
        case 'tuple': case 'Tuple': v = LIB.tuple(I, args, tys); break;
        case 'stringstream': case 'ostringstream': case 'istringstream': v = mk(SSP, { buf: args.length ? I.cstr(args[0]) : '', pos: 0, kind: n === 'ostringstream' ? 'out' : 'in', fail: false, prec: 6, fixed: false, width: 0, fill: ' ', alpha: false, base: 10 }); v.kind = n === 'ostringstream' ? 'out' : 'in'; if (n === 'stringstream') v.both = true; break;
        case 'greater': v = { $lib: true, $greater: true, $str: () => 'greater', $ty: () => T('greater') }; break;
        case 'less': v = { $lib: true, $less: true, $str: () => 'less', $ty: () => T('less') }; break;
        case 'function': case 'Func': case 'Action': case 'Predicate': case 'Comparison': v = args[0] || null; break;
        case 'Object': case 'object': { const ci = I.synthClass('Object', null); ci.builtin = true; const o = new Obj(ci); return o; }
        case 'Optional': v = opt(args[0], tys[0]); break;
        case 'string':
          if (lang === 'cs' && args.length === 2) return chr(toNum(args[0])).repeat(Math.max(0, toNum(args[1])));
          if (lang === 'cs' && args.length === 1 && args[0] instanceof Arr) return args[0].a.map(c => chr(c)).join('');
          return args.length ? (args.length === 2 && typeof args[1] === 'number' && typeof args[0] !== 'string' ? chr(args[1]).repeat(toNum(args[0])) : I.cstr(args[0])) : '';
        case 'Thread': return { $lib: true, $str: () => 'Thread', $ty: () => T('Thread'), run: args[0] };
        default:
          if (NK[n] || n === 'bool') return args.length ? I.conv(args[0], ty) : I.defaultVal(ty);
          throw new CF.CompileError(`${n} is not available in this playground`, I.lastLine);
      }
      if (initVals) {
        if (v.put) initVals.forEach((x, i) => { const p = unpackPair(I, x); v.put(I, p[0], p[1]); });
        else if (v.add) initVals.forEach(x => v.add(I, x));
        else if (v.q) initVals.forEach(x => v.push(I, x));
        else if (v.a) v.a = initVals.map(x => I.conv(x, v.et));
      }
      if (csInit) {
        for (const it of csInit) {
          const vals = (it.add || [it.e]).map(e => I.ev(e, env));
          if (it.key !== undefined) { const k = I.ev(it.key, env); v.put(I, k, I.conv(vals[0], v.vt)); }
          else if (v.put) v.put(I, vals[0], vals[1]);
          else if (v.add) v.add(I, vals[0]);
          else if (v.a) v.a.push(I.conv(vals[0], v.et));
        }
      }
      return v;
    }
  };
  function unpackPair(I, x) {
    if (x && x.$is && x.$is('pair')) return [x.first, x.second];
    if (x instanceof Arr) return [x.a[0], x.a[1]];
    if (x && x.items) return [x.items[0], x.items[1]];
    return [x, undefined];
  }
  function limits(I, t, what) {
    const n = t.n;
    const tbl = { int: [-2147483648, 2147483647], long: [-9223372036854775808n, 9223372036854775807n], short: [-32768, 32767], char: [-128, 127], uint: [0, 4294967295], ulong: [0n, 18446744073709551615n], double: [-Number.MAX_VALUE, Number.MAX_VALUE], float: [-3.4028234663852886e38, 3.4028234663852886e38], bool: [false, true] };
    const r = tbl[n] || tbl.int;
    if (what === 'max') return r[1];
    if (what === 'min') return n === 'double' ? 2.2250738585072014e-308 : r[0];
    if (what === 'lowest') return r[0];
    if (what === 'infinity') return Infinity;
    if (what === 'epsilon') return Number.EPSILON;
    return r[1];
  }
  function collItems(I, c) {
    if (c instanceof Arr) return c.a.slice();
    if (c.a) return c.view ? c.view(I).slice() : c.a.slice();
    if (c.m && c.items) return c.items(I);
    if (c.m && c.ents) return c.ents(I).map(e => entryOf(I, c, e));
    if (c.q) return c.q.slice();
    if (typeof c === 'string') return Array.from(c, x => x.charCodeAt(0));
    return [];
  }
  function entryOf(I, m, e) { const p = mk(PairP, { rec: e, t1: m.kt, t2: m.vt }); return p; }

  /* ===== Java's Random, so new Random(42) gives the same numbers as real Java ===== */
  function javaSeed(s) { return (s ^ 0x5DEECE66Dn) & ((1n << 48n) - 1n); }
  function jnext(r, bits) { r.seed = (r.seed * 0x5DEECE66Dn + 0xBn) & ((1n << 48n) - 1n); return Number(BigInt.asIntN(32, r.seed >> BigInt(48 - bits))); }
  function jnextInt(r, bound) {
    if (bound === undefined) return jnext(r, 32);
    if (bound <= 0) throw new Error('bound must be positive');
    if ((bound & -bound) === bound) return Number((BigInt(bound) * BigInt(jnext(r, 31))) >> 31n);
    let bits, val;
    do { bits = jnext(r, 31); val = bits % bound; } while (bits - val + (bound - 1) < 0 || bits - val + (bound - 1) > 2147483647);
    return val;
  }
  function jnextDouble(r) { return (jnext(r, 26) * 2 ** 27 + jnext(r, 27)) * 2 ** -53; }
  function mulberry(a) { return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  /* glibc rand(): the TYPE_3 additive generator, so srand(1) gives 1804289383 first like Linux */
  function glibcInit(seed) {
    const r = new Array(34); r[0] = seed | 0 || 1;
    for (let i = 1; i < 31; i++) { const hi = Math.floor(r[i - 1] / 127773), lo = r[i - 1] % 127773; let w = 16807 * lo - 2836 * hi; if (w < 0) w += 2147483647; r[i] = w; }
    for (let i = 31; i < 34; i++) r[i] = r[i - 31];
    const st = { r, k: 34 };
    for (let i = 0; i < 310; i++) glibcNext(st);
    return st;
  }
  function glibcNext(st) { const r = st.r; const v = (r[st.k - 31] + r[st.k - 3]) | 0; r.push(v); st.k++; if (r.length > 400) { r.splice(0, r.length - 40); st.k = r.length; } return v >>> 1; }

  /* ===== iteration and unpacking ===== */
  LIB.iterate = function (I, v, ty, wantRef) {
    if (v instanceof Arr) return v.a.map((x, i) => [x, v.et, wantRef ? { get: () => v.a[i], set: y => { v.a[i] = y; } } : null]);
    if (typeof v === 'string') return Array.from(v).map(c => [c.charCodeAt(0), TY.char]);
    if (v instanceof Ptr) throw new CF.CompileError('A range for loop cannot walk a pointer, because the pointer does not know how long the array is', I.lastLine);
    if (v && v.$lib) {
      if (v.a) { const items = v.view ? v.view(I) : v.a; return items.map((x, i) => [x, v.et, wantRef && !v.view ? { get: () => v.a[i], set: y => { v.a[i] = y; } } : (wantRef ? { get: () => v.a[i], set: y => { v.a[i] = y; } } : null)]); }
      if (v.m && v.ents) return v.ents(I).map(e => [entryOf(I, v, e), T(I.lang === 'cs' ? 'KeyValuePair' : I.lang === 'cpp' ? 'pair' : 'Entry', { args: [v.kt, v.vt] })]);
      if (v.m && v.items) return v.items(I).map(x => [x, v.et]);
      if (v.q) { if (I.lang === 'cpp') throw new CF.CompileError('A priority_queue cannot be walked with a for loop. Pop items with top() and pop()', I.lastLine); return (v.cs ? v.q.map(x => x.e) : v.q).map(x => [x, v.et]); }
      if (v.$is && v.$is('Stream')) return v.a.map(x => [x, v.et]);
      if (v.items) return v.items.map((x, i) => [x, v.tys[i]]);
      if (v.grp) return v.a.map(x => [x, v.et]);
    }
    throw new CF.CompileError('This value cannot be walked with a for each loop', I.lastLine);
  };
  LIB.unpack = function (I, v, n) {
    if (v && v.$lib && v.$is && v.$is('pair')) return [[v.first, v.t1 || valTy(v.first)], [v.second, v.t2 || valTy(v.second)]];
    if (v && v.items) return v.items.map((x, i) => [x, v.tys[i] || valTy(x)]);
    if (v instanceof Arr) return v.a.map(x => [x, v.et]);
    if (v instanceof Obj) { const fs = I.fieldNames(v.ci); const dec = I.findMethod(v.ci, 'Deconstruct', n); if (dec) { const boxes = Array.from({ length: n }, () => new Box(null, TY.dyn)); I.invoke(dec, v, boxes.map(b => b.v), [], 'Deconstruct', null, null, boxes.map(b => ({ get: () => b.v, set: x => { b.v = x; } }))); return boxes.map(b => [b.v, valTy(b.v)]); } return fs.map(k => [v.f[k], I.fieldTy(v.ci, k)]); }
    throw new CF.CompileError('This value cannot be split into parts', I.lastLine);
  };

  /* ===== names: namespaces, constants and C++ stream objects ===== */
  const NSNAMES = {
    java: ['System', 'Math', 'Integer', 'Long', 'Double', 'Float', 'Character', 'Boolean', 'String', 'Arrays', 'Collections', 'List', 'Set', 'Map', 'Objects', 'IntStream', 'Stream', 'Collectors', 'Comparator', 'Thread', 'Optional', 'LongStream', 'DoubleStream', 'Short', 'Byte', 'Function', 'StrictMath', 'Entry'],
    cs: ['Console', 'Math', 'int', 'long', 'double', 'float', 'char', 'string', 'String', 'bool', 'Convert', 'Array', 'Enumerable', 'Environment', 'Int32', 'Int64', 'Double', 'Char', 'Boolean', 'Thread', 'Tuple', 'decimal', 'Enum', 'MathF', 'StringComparer', 'Comparer', 'byte', 'short', 'uint', 'ulong', 'DateTime', 'TimeSpan', 'BitConverter', 'Single'],
    c: [], cpp: ['std', 'string']
  };
  LIB.name = function (I, id, n) {
    const lang = I.lang;
    if (NSNAMES[lang].includes(id)) return [new NS(id), TY.dyn];
    if (lang === 'c' || lang === 'cpp') {
      switch (id) {
        case 'cout': return [I.cout, TY.dyn];
        case 'cerr': case 'clog': return [I.cerr, TY.dyn];
        case 'cin': return [I.cin, TY.dyn];
        case 'endl': return [{ manip: 'endl' }, TY.dyn];
        case 'fixed': case 'scientific': case 'boolalpha': case 'noboolalpha': case 'left': case 'right': case 'hex': case 'dec': case 'oct': case 'showpoint': case 'noshowpoint': case 'flush': case 'ws': case 'uppercase': case 'nouppercase': case 'showpos': case 'noshowpos': case 'internal':
          if (lang === 'cpp') return [{ manip: id }, TY.dyn]; break;
        case 'stdin': return [{ file: 'stdin' }, TY.dyn];
        case 'stdout': return [{ file: 'stdout' }, TY.dyn];
        case 'stderr': return [{ file: 'stderr' }, TY.dyn];
        case 'EOF': return [-1, TY.int];
        case 'RAND_MAX': return [2147483647, TY.int];
        case 'INT_MAX': return [2147483647, TY.int];
        case 'INT_MIN': return [-2147483648, TY.int];
        case 'UINT_MAX': return [4294967295, TY.uint];
        case 'LONG_MAX': case 'LLONG_MAX': return [9223372036854775807n, TY.long];
        case 'LONG_MIN': case 'LLONG_MIN': return [-9223372036854775808n, TY.long];
        case 'ULLONG_MAX': return [18446744073709551615n, TY.ulong];
        case 'SHRT_MAX': return [32767, TY.int]; case 'SHRT_MIN': return [-32768, TY.int];
        case 'CHAR_MAX': return [127, TY.int]; case 'CHAR_MIN': return [-128, TY.int]; case 'CHAR_BIT': return [8, TY.int];
        case 'DBL_MAX': return [Number.MAX_VALUE, TY.double]; case 'DBL_MIN': return [2.2250738585072014e-308, TY.double]; case 'DBL_EPSILON': return [Number.EPSILON, TY.double];
        case 'FLT_MAX': return [3.4028234663852886e38, TY.float];
        case 'M_PI': return [Math.PI, TY.double]; case 'M_E': return [Math.E, TY.double];
        case 'INFINITY': return [Infinity, TY.double]; case 'NAN': return [NaN, TY.double];
        case 'true': return [true, TY.bool]; case 'false': return [false, TY.bool];
        case 'EXIT_SUCCESS': return [0, TY.int]; case 'EXIT_FAILURE': return [1, TY.int];
        case 'npos': return [18446744073709551615n, TY.ulong];
      }
      if (lang === 'cpp' && (GLOBAL_CPP.has(id) || GLOBAL_C.has(id))) return [new Fn({ fname: id, native: (args, tys, refs) => { const r = LIB.callGlobal(I, id, args, tys, refs || [], { line: I.lastLine }, null); return r[0]; } }), TY.dyn];
      if (lang === 'c' && GLOBAL_C.has(id)) return [new Fn({ fname: id, native: (args, tys, refs) => LIB.callGlobal(I, id, args, tys, refs || [], { line: I.lastLine }, null)[0] }), TY.dyn];
    }
    return undefined;
  };
  const GLOBAL_C = new Set('printf puts putchar scanf getchar fgets gets sprintf snprintf malloc calloc realloc free exit abs labs llabs atoi atof atol atoll rand srand time qsort strlen strcpy strncpy strcat strncat strcmp strncmp strchr strrchr strstr strdup memset memcpy memmove toupper tolower isdigit isalpha isalnum isspace isupper islower ispunct isxdigit sqrt pow fabs floor ceil round fmod log log10 log2 exp sin cos tan asin acos atan atan2 hypot cbrt trunc fmax fmin fflush clock sscanf fprintf fputs fputc assert'.split(' '));
  const GLOBAL_CPP = new Set('max min swap sort stable_sort reverse find find_if count count_if accumulate max_element min_element fill iota unique binary_search lower_bound upper_bound next_permutation prev_permutation all_of any_of none_of distance advance to_string stoi stol stoll stod stof getline make_pair make_tuple begin end gcd __gcd lcm setw setprecision setfill transform copy partial_sort nth_element rotate equal is_sorted for_each move remove remove_if abs tie get'.split(' '));

  /* ===== C++ streams ===== */
  LIB.streamOut = function (I, s, v, ty, node) {
    if (v && v.manip) {
      switch (v.manip) {
        case 'endl': return wr(I, s, '\n');
        case 'fixed': s.fixed = true; s.sci = false; return;
        case 'scientific': s.sci = true; s.fixed = false; return;
        case 'boolalpha': s.alpha = true; return; case 'noboolalpha': s.alpha = false; return;
        case 'left': s.left = true; return; case 'right': s.left = false; return;
        case 'hex': s.base = 16; return; case 'dec': s.base = 10; return; case 'oct': s.base = 8; return;
        case 'showpoint': s.showpoint = true; return; case 'noshowpoint': s.showpoint = false; return;
        case 'uppercase': s.upper = true; return; case 'nouppercase': s.upper = false; return;
        case 'showpos': s.showpos = true; return; case 'noshowpos': s.showpos = false; return;
        case 'setw': s.width = v.n; return; case 'setprecision': s.prec = v.n; return; case 'setfill': s.fill = chr(v.n); return;
        case 'flush': case 'ws': case 'internal': return;
      }
    }
    let t;
    if (v === null || v === undefined) {
      if (ty && ty.n === 'char' && ty.ptr) throw new Fatal('cout was given a NULL char pointer. That is undefined behaviour and real programs usually crash', 'segv');
      t = v === null && ty && ty.ptr ? '0' : '0';
    }
    else if (typeof v === 'string') t = v;
    else if (typeof v === 'boolean') t = s.alpha ? String(v) : (v ? '1' : '0');
    else if (ty && plain(ty) && (ty.n === 'char' || ty.n === 'ubyte' || ty.n === 'byte') && typeof v === 'number') t = chr(v & 0xff);
    else if (typeof v === 'bigint' || (typeof v === 'number' && kindOf(ty, v) !== 'd' && kindOf(ty, v) !== 'f')) {
      if (s.base !== 10) t = (typeof v === 'bigint' ? BigInt.asUintN(64, v) : (v >>> 0)).toString(s.base);
      else t = String(v);
      if (s.upper) t = t.toUpperCase();
      if (s.showpos && !t.startsWith('-')) t = '+' + t;
    }
    else if (typeof v === 'number') {
      if (s.fixed) t = CF.fmt.fixedExact(v, s.prec);
      else if (s.sci) t = CF.fmt.expC(v, s.prec, s.upper);
      else t = CF.fmt.fmtG(v, s.prec, s.showpoint, s.upper);
      if (!Number.isFinite(v)) t = Number.isNaN(v) ? 'nan' : v > 0 ? 'inf' : '-inf';
      if (s.showpos && !t.startsWith('-')) t = '+' + t;
    }
    else if (v instanceof Ptr) { t = v.et && v.et.n === 'char' && !v.box ? I.cstr(v) : I.str(v); }
    else if (v instanceof Arr) { t = v.et && v.et.n === 'char' ? I.cstr(v) : I.str(v); }
    else if (v instanceof Obj) {
      const m = I.funcs.get('operator<<');
      if (m) { const f = m.find(x => x.params[1] && x.params[1].ty.n === v.ci.name) || m[0]; I.invoke(f, null, [s, v], [TY.dyn, { n: v.ci.name }], 'operator<<', null, node && node.line, [{ get: () => s, set: () => {} }, { get: () => v, set: () => {} }]); return; }
      throw new CF.CompileError(`no match for operator<< on a ${v.ci.name}. Print its fields, or write an ostream& operator<<(ostream& os, const ${v.ci.name}& x) function`, node ? node.line : I.lastLine);
    }
    else t = I.str(v, ty);
    if (s.width && t.length < s.width) t = s.left ? t + s.fill.repeat(s.width - t.length) : s.fill.repeat(s.width - t.length) + t;
    s.width = 0;
    wr(I, s, t);
  };
  function wr(I, s, t) { if (s.buf !== undefined && s.kind !== undefined && s.$lib) s.buf += t; else I.write(t, s.err); }
  LIB.streamIn = function (I, s, r, node) {
    const ty = r.ty && r.ty.n !== 'var' ? r.ty : TY.dyn;
    const src = s.$lib ? { get stdin() { return s.buf; }, get inPos() { return s.pos; }, set inPos(x) { s.pos = x; }, warn() {}, warned: new Set(), notes: [] } : I;
    if (s.fail) return;
    if (ty.n === 'char' && plain(ty)) {
      Input.skipWs(src);
      if (src.inPos >= src.stdin.length) { s.fail = true; if (!s.$lib) noInput(I); return; }
      r.set(src.stdin.charCodeAt(src.inPos++)); if (r.box) r.box.uninit = false; return;
    }
    const tok = Input.token(src);
    if (tok === null) { s.fail = true; if (!s.$lib) noInput(I); else s.fail = true; if (NK[ty.n] && plain(ty)) { r.set(I.conv(0, ty)); if (r.box) r.box.uninit = false; } return; }
    if (ty.n === 'string' || (ty.n === 'char' && ty.ptr) || (ty.n === 'char' && ty.dim)) {
      if (ty.n === 'string') r.set(tok);
      else { const arr = r.get(); const p = arr instanceof Arr ? new Ptr(arr.a, 0) : arr; const cs = I.cchars(tok); cs.forEach((c, i) => { if (p.arr) p.arr[p.i + i] = c; }); }
      if (r.box) r.box.uninit = false;
      return;
    }
    const k = NK[ty.n];
    if (k === 'd' || k === 'f') {
      const m = tok.match(/^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?/);
      if (!m) { s.fail = true; r.set(0); return; }
      r.set(I.conv(parseFloat(m[0]), ty)); if (r.box) r.box.uninit = false;
      if (m[0].length < tok.length) src.inPos -= tok.length - m[0].length;
      return;
    }
    if (ty.n === 'bool') { r.set(tok === '1'); if (r.box) r.box.uninit = false; return; }
    const m = tok.match(/^[+-]?\d+/);
    if (!m) { s.fail = true; r.set(I.conv(0, ty)); src.inPos -= tok.length; return; }
    if (m[0].length < tok.length) src.inPos -= tok.length - m[0].length;
    r.set(I.conv(k === 'l' || k === 'ul' ? BigInt(m[0]) : Number(m[0]), ty)); if (r.box) r.box.uninit = false;
  };

  /* ===== printing in Java and C# ===== */
  function jprint(I, args, tys, nl, err, n) {
    let s = '';
    if (args.length) {
      const v = args[0], t = tys[0];
      if (v instanceof Arr && v.et && v.et.n === 'char' && !v.et.dim) s = v.a.map(chr).join('');
      else s = I.str(v, t);
    }
    I.write(s + (nl ? '\n' : ''), err);
  }
  function csWrite(I, args, tys, nl, err) {
    let s = '';
    if (args.length === 1) {
      const v = args[0];
      if (v instanceof Arr && v.et && v.et.n === 'char') s = v.a.map(chr).join('');
      else s = I.str(v, tys[0]);
    } else if (args.length > 1) s = CF.csComposite(I, I.str(args[0]), args.slice(1), tys.slice(1));
    I.write(s + (nl ? '\n' : ''), err);
  }

  /* ===== parse numbers from text ===== */
  function parseIntJ(I, s, radix = 10, kind = 'int') {
    if (typeof s !== 'string') { if (s === null) throw I.ex('NumberFormatException', 'Cannot parse null string: null'); s = String(s); }
    const ok = radix === 10 ? /^[+-]?\d+$/.test(s) : /^[+-]?[0-9a-zA-Z]+$/.test(s);
    if (!ok) throw I.ex('NumberFormatException', `For input string: "${s}"` + (radix !== 10 ? ` under radix ${radix}` : ''));
    const b = radix === 10 ? BigInt(s) : BigInt.asIntN(64, BigInt(parseInt(s, radix)));
    const lim = kind === 'long' ? [-(2n ** 63n), 2n ** 63n - 1n] : [-(2n ** 31n), 2n ** 31n - 1n];
    if (b < lim[0] || b > lim[1]) throw I.ex('NumberFormatException', `For input string: "${s}"` + (radix !== 10 ? ` under radix ${radix}` : ''));
    return kind === 'long' ? b : Number(b);
  }
  function parseIntCs(I, s, kind = 'int') {
    if (s === null || s === undefined) throw I.ex('ArgumentNullException', "Value cannot be null. (Parameter 's')");
    const t = String(s).trim();
    if (!/^[+-]?\d+$/.test(t)) throw I.ex('FormatException', `The input string '${s}' was not in a correct format.`);
    const b = BigInt(t);
    const lim = kind === 'long' ? [-(2n ** 63n), 2n ** 63n - 1n] : [-(2n ** 31n), 2n ** 31n - 1n];
    if (b < lim[0] || b > lim[1]) throw I.ex('OverflowException', `Value was either too large or too small for an ${kind === 'long' ? 'Int64' : 'Int32'}.`);
    return kind === 'long' ? b : Number(b);
  }
  function parseDbl(I, s) {
    const t = String(s).trim();
    if (I.lang === 'java') { if (!/^[+-]?(NaN|Infinity|(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?[dDfF]?)$/.test(t)) throw I.ex('NumberFormatException', t ? `For input string: "${s}"` : 'empty String'); return parseFloat(t.replace(/[dDfF]$/, '')); }
    if (!/^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/.test(t) && !/^(NaN|[+-]?∞|[+-]?Infinity)$/.test(t)) throw I.ex('FormatException', `The input string '${s}' was not in a correct format.`);
    return parseFloat(t);
  }
  const roundEven = x => { const r = Math.round(x); return (Math.abs(x % 1) === 0.5) ? 2 * Math.round(x / 2) : r; };

  /* ===== maths shared by every language ===== */
  function mathFn(I, id, args, tys) {
    const x = toNum(args[0]), y = toNum(args[1]);
    const k0 = kindOf(tys[0], args[0]), k1 = kindOf(tys[1], args[1]);
    const lang = I.lang;
    switch (id) {
      case 'abs': case 'Abs': case 'fabs': case 'labs': case 'llabs':
        if (typeof args[0] === 'bigint') return R(args[0] < 0n ? BigInt.asIntN(64, -args[0]) : args[0], TY.long);
        if (k0 === 'i' && id !== 'fabs') return R(x === -2147483648 ? x : Math.abs(x), TY.int);
        return R(Math.abs(x), id === 'fabs' || k0 === 'd' ? TY.double : KT[k0] || TY.double);
      case 'max': case 'Max': case 'min': case 'Min': case 'fmax': case 'fmin': {
        if (args.length === 1 && args[0] instanceof Arr) { const a = args[0].a; const r = a.reduce((m, v) => (id.toLowerCase() === 'max' ? natCmp(I, v, m) > 0 : natCmp(I, v, m) < 0) ? v : m); return R(r, args[0].et); }
        if (lang === 'cpp' && args.length === 3 && args[2] instanceof Fn) { const less = I.truthy(I.callFn(args[2], [args[0], args[1]], tys)); return R(id === 'max' ? (less ? args[1] : args[0]) : (I.truthy(I.callFn(args[2], [args[1], args[0]], tys)) ? args[1] : args[0]), tys[0]); }
        const k = promote(k0 || 'i', k1 || 'i');
        if (lang === 'cpp' && tys[0] && tys[1] && plain(tys[0]) && plain(tys[1]) && NK[tys[0].n] && NK[tys[1].n] && tys[0].n !== tys[1].n && !(tys[0].n === 'char' || tys[1].n === 'char')) {
          throw new CF.CompileError(`no matching function for call to '${id}(${tys[0].n}, ${tys[1].n})'. std::${id} needs both values of the same type, for example ${id}(a, (${tys[0].n}) b)`, I.lastLine);
        }
        const big = id.toLowerCase().includes('max');
        if (typeof args[0] === 'string') return R(big ? (args[0] > args[1] ? args[0] : args[1]) : (args[0] < args[1] ? args[0] : args[1]), TY.string);
        if (k === 'l' || k === 'ul') { const a = toBig(args[0]), b = toBig(args[1]); return R(big ? (a > b ? a : b) : (a < b ? a : b), KT[k]); }
        if (args[0] instanceof Obj || (args[0] && args[0].$lib)) { const c = natCmp(I, args[0], args[1]); return R(big ? (c < 0 ? args[1] : args[0]) : (c > 0 ? args[1] : args[0]), tys[0]); }
        const r = big ? Math.max(x, y) : Math.min(x, y);
        return R(r, id[0] === 'f' ? TY.double : KT[k]);
      }
      case 'pow': case 'Pow': return R(Math.pow(x, y), TY.double);
      case 'sqrt': case 'Sqrt': return R(Math.sqrt(x), TY.double);
      case 'cbrt': case 'Cbrt': return R(Math.cbrt(x), TY.double);
      case 'floor': case 'Floor': return R(Math.floor(x), TY.double);
      case 'ceil': case 'Ceiling': return R(Math.ceil(x), TY.double);
      case 'trunc': case 'Truncate': return R(Math.trunc(x), TY.double);
      case 'round': if (lang === 'java') { if (k0 === 'f') return R(Math.floor(x + 0.5) | 0, TY.int); return R(BigInt(Math.floor(x + 0.5)), TY.long); } return R(x < 0 ? -Math.round(-x) : Math.round(x), TY.double);
      case 'Round': {
        if (args.length >= 2 && typeof args[1] === 'number') { const f = 10 ** y; return R(roundEven(x * f) / f, TY.double); }
        return R(roundEven(x), TY.double);
      }
      case 'rint': return R(roundEven(x), TY.double);
      case 'exp': case 'Exp': return R(Math.exp(x), TY.double);
      case 'log': case 'Log': return R(args.length === 2 ? Math.log(x) / Math.log(y) : Math.log(x), TY.double);
      case 'log10': case 'Log10': return R(Math.log10(x), TY.double);
      case 'log2': case 'Log2': return R(Math.log2(x), TY.double);
      case 'sin': case 'Sin': return R(Math.sin(x), TY.double); case 'cos': case 'Cos': return R(Math.cos(x), TY.double); case 'tan': case 'Tan': return R(Math.tan(x), TY.double);
      case 'asin': case 'Asin': return R(Math.asin(x), TY.double); case 'acos': case 'Acos': return R(Math.acos(x), TY.double);
      case 'atan': case 'Atan': return R(Math.atan(x), TY.double); case 'atan2': case 'Atan2': return R(Math.atan2(x, y), TY.double);
      case 'hypot': return R(Math.hypot(x, y), TY.double);
      case 'fmod': return R(x % y, TY.double);
      case 'signum': return R(Math.sign(x), k0 === 'f' ? TY.float : TY.double);
      case 'Sign': return R(Math.sign(x), TY.int);
      case 'random': return R(Math.random(), TY.double);
      case 'toRadians': return R(x * Math.PI / 180, TY.double);
      case 'toDegrees': return R(x * 180 / Math.PI, TY.double);
      case 'floorDiv': { if (y === 0) throw I.divZero(); return R(Math.floor(x / y), k0 === 'l' ? TY.long : TY.int); }
      case 'floorMod': { if (y === 0) throw I.divZero(); return R(((x % y) + y) % y, TY.int); }
      case 'Clamp': return R(Math.min(Math.max(x, y), toNum(args[2])), tys[0]);
      case 'addExact': { const r = x + y; if (r > 2147483647 || r < -2147483648) throw I.ex('ArithmeticException', 'integer overflow'); return R(r, TY.int); }
      case 'multiplyExact': { const r = x * y; if (k0 === 'i' && k1 === 'i' && (r > 2147483647 || r < -2147483648)) throw I.ex('ArithmeticException', 'integer overflow'); return R(r, TY.int); }
    }
    return NONE;
  }

  /* ===== static calls: Math.max, Integer.parseInt, Arrays.sort, Console.WriteLine, int.Parse ... ===== */
  LIB.callStatic = function (I, ns, id, args, tys, refs, n, quiet) {
    const lang = I.lang;
    const fail = () => NONE;
    if (ns === 'std') { const r = LIB.callGlobal(I, id, args, tys, refs, n, null); return r; }
    if (ns === 'System.out' || ns === 'System.err') {
      const err = ns === 'System.err';
      switch (id) {
        case 'println': jprint(I, args, tys, true, err, n); return R(undefined, TY.void);
        case 'print': if (!args.length) throw new CF.CompileError('System.out.print needs something to print. Use System.out.println() for an empty line', n.line); jprint(I, args, tys, false, err, n); return R(undefined, TY.void);
        case 'printf': case 'format': I.write(CF.printf(I, I.str(args[0]), args.slice(1), tys.slice(1), 'java'), err); return R(new NS(ns), TY.dyn);
        case 'flush': return R(undefined, TY.void);
        case 'write': I.write(chr(args[0]), err); return R(undefined, TY.void);
      }
      return fail();
    }
    if (ns === 'Math' || ns === 'MathF' || ns === 'StrictMath') { const r = mathFn(I, id, args, tys); if (r !== NONE) return r; }
    if (lang === 'java') {
      switch (ns) {
        case 'System':
          if (id === 'exit') throw new CF.ExitSig(toNum(args[0]));
          if (id === 'currentTimeMillis') return R(BigInt(Date.now()), TY.long);
          if (id === 'nanoTime') return R(BigInt(Math.round((typeof performance !== 'undefined' ? performance.now() : Date.now()) * 1e6)), TY.long);
          if (id === 'lineSeparator') return R('\n', TY.string);
          if (id === 'arraycopy') { const [src, sp, dst, dp, len] = args; if (!src || !dst) throw I.ex('NullPointerException', null); const s = toNum(sp), d = toNum(dp), l = toNum(len); if (s < 0 || d < 0 || l < 0 || s + l > src.a.length || d + l > dst.a.length) throw I.ex('ArrayIndexOutOfBoundsException', `arraycopy: last source index ${s + l} out of bounds for length ${src.a.length}`); const part = src.a.slice(s, s + l); for (let i = 0; i < l; i++) dst.a[d + i] = part[i]; return R(undefined, TY.void); }
          if (id === 'identityHashCode') return R(I.idHash(args[0]), TY.int);
          if (id === 'getProperty' || id === 'getenv') return R(null, TY.string);
          if (id === 'gc') return R(undefined, TY.void);
          break;
        case 'Integer': case 'Long': case 'Short': case 'Byte': {
          const kind = ns === 'Long' ? 'long' : 'int', ty = ns === 'Long' ? TY.long : TY.int;
          switch (id) {
            case 'parseInt': case 'parseLong': case 'parseShort': case 'parseByte': return R(parseIntJ(I, args[0], args[1] ? toNum(args[1]) : 10, kind), ty);
            case 'valueOf': return R(typeof args[0] === 'string' ? parseIntJ(I, args[0], args[1] ? toNum(args[1]) : 10, kind) : I.conv(args[0], ty), Object.assign({}, ty, { box: true }));
            case 'toString': return R(args.length > 1 ? (typeof args[0] === 'bigint' ? args[0] : toNum(args[0])).toString(toNum(args[1])) : I.str(args[0], ty), TY.string);
            case 'toBinaryString': return R((typeof args[0] === 'bigint' ? BigInt.asUintN(64, args[0]) : toNum(args[0]) >>> 0).toString(2), TY.string);
            case 'toHexString': return R((typeof args[0] === 'bigint' ? BigInt.asUintN(64, args[0]) : toNum(args[0]) >>> 0).toString(16), TY.string);
            case 'toOctalString': return R((toNum(args[0]) >>> 0).toString(8), TY.string);
            case 'bitCount': { let v = typeof args[0] === 'bigint' ? BigInt.asUintN(64, args[0]) : BigInt(toNum(args[0]) >>> 0), c = 0; while (v) { c += Number(v & 1n); v >>= 1n; } return R(c, TY.int); }
            case 'compare': return R(args[0] < args[1] ? -1 : args[0] > args[1] ? 1 : 0, TY.int);
            case 'sum': return I.arith('+', args[0], kind === 'long' ? 'l' : 'i', args[1], kind === 'long' ? 'l' : 'i', n).slice(0, 1).concat([ty]);
            case 'max': return R(args[0] > args[1] ? args[0] : args[1], ty);
            case 'min': return R(args[0] < args[1] ? args[0] : args[1], ty);
            case 'signum': return R(Math.sign(toNum(args[0])), TY.int);
            case 'abs': return mathFn(I, 'abs', args, tys);
            case 'reverse': { let v = toNum(args[0]) >>> 0, r = 0; for (let i = 0; i < 32; i++) { r = (r << 1) | (v & 1); v >>>= 1; } return R(r | 0, TY.int); }
            case 'highestOneBit': { const v = toNum(args[0]); return R(v === 0 ? 0 : (1 << (31 - Math.clz32(v))) | 0, TY.int); }
            case 'numberOfTrailingZeros': { const v = toNum(args[0]); return R(v === 0 ? 32 : 31 - Math.clz32(v & -v), TY.int); }
            case 'numberOfLeadingZeros': return R(Math.clz32(toNum(args[0])), TY.int);
            case 'hashCode': return R(I.hashOf(args[0]), TY.int);
          }
          break;
        }
        case 'Double': case 'Float':
          switch (id) {
            case 'parseDouble': case 'parseFloat': case 'valueOf': { const v = typeof args[0] === 'string' ? parseDbl(I, args[0]) : toNum(args[0]); return R(ns === 'Float' ? Math.fround(v) : v, ns === 'Float' ? TY.float : TY.double); }
            case 'isNaN': return R(Number.isNaN(toNum(args[0])), TY.bool);
            case 'isInfinite': return R(!Number.isFinite(toNum(args[0])) && !Number.isNaN(toNum(args[0])), TY.bool);
            case 'compare': return R(Math.sign(toNum(args[0]) - toNum(args[1])), TY.int);
            case 'toString': return R(I.str(toNum(args[0]), ns === 'Float' ? TY.float : TY.double), TY.string);
            case 'max': return R(Math.max(toNum(args[0]), toNum(args[1])), TY.double);
            case 'min': return R(Math.min(toNum(args[0]), toNum(args[1])), TY.double);
            case 'sum': return R(toNum(args[0]) + toNum(args[1]), TY.double);
          }
          break;
        case 'Boolean':
          if (id === 'parseBoolean' || id === 'valueOf') return R(typeof args[0] === 'string' ? args[0].toLowerCase() === 'true' : !!args[0], TY.bool);
          if (id === 'toString') return R(String(args[0]), TY.string);
          if (id === 'compare') return R((args[0] ? 1 : 0) - (args[1] ? 1 : 0), TY.int);
          break;
        case 'Character': {
          const c = toNum(args[0]), s = chr(c);
          switch (id) {
            case 'isDigit': return R(/\p{Nd}/u.test(s), TY.bool);
            case 'isLetter': case 'isAlphabetic': return R(/\p{L}/u.test(s), TY.bool);
            case 'isLetterOrDigit': return R(/[\p{L}\p{Nd}]/u.test(s), TY.bool);
            case 'isUpperCase': return R(/\p{Lu}/u.test(s), TY.bool);
            case 'isLowerCase': return R(/\p{Ll}/u.test(s), TY.bool);
            case 'isWhitespace': case 'isSpaceChar': return R(/\s/.test(s), TY.bool);
            case 'toUpperCase': return R(typeof args[0] === 'number' && tys[0] && tys[0].n === 'int' ? s.toUpperCase().charCodeAt(0) : s.toUpperCase().charCodeAt(0), tys[0] && tys[0].n === 'int' ? TY.int : TY.char);
            case 'toLowerCase': return R(s.toLowerCase().charCodeAt(0), tys[0] && tys[0].n === 'int' ? TY.int : TY.char);
            case 'getNumericValue': return R(/[0-9]/.test(s) ? c - 48 : /[a-z]/i.test(s) ? s.toLowerCase().charCodeAt(0) - 87 : -1, TY.int);
            case 'toString': case 'valueOf': return R(id === 'toString' ? s : c, id === 'toString' ? TY.string : T('char', { box: true }));
            case 'compare': return R(c - toNum(args[1]), TY.int);
            case 'isVowel': break;
            case 'toChars': return R(new Arr([c], TY.char), T('char', { dim: 1 }));
          }
          break;
        }
        case 'String':
          switch (id) {
            case 'valueOf': case 'copyValueOf': return R(args[0] instanceof Arr && args[0].et && args[0].et.n === 'char' ? args[0].a.map(chr).join('') : I.str(args[0], tys[0]), TY.string);
            case 'format': return R(CF.printf(I, I.str(args[0]), args.slice(1), tys.slice(1), 'java'), TY.string);
            case 'join': { const items = args.length === 2 && args[1] && typeof args[1] === 'object' ? collItems(I, args[1]) : args.slice(1); return R(items.map(x => I.str(x)).join(I.str(args[0])), TY.string); }
          }
          break;
        case 'Arrays': return arraysFn(I, id, args, tys, n);
        case 'Collections': return collectionsFn(I, id, args, tys, n);
        case 'List': case 'Set':
          if (id === 'of' || id === 'copyOf') {
            const items = id === 'copyOf' ? collItems(I, args[0]) : (args.length === 1 && args[0] instanceof Arr && tys[0] && tys[0].dim ? args[0].a : args);
            if (items.some(x => x === null)) throw I.ex('NullPointerException', null);
            const v = ns === 'List' ? newList(I, 'ImmutableList', tys[0] && !tys[0].dim ? tys[0] : null, items.slice()) : newSet(I, 'ImmutableSet', tys[0]);
            if (ns === 'Set') { items.forEach(x => { if (!v.add(I, x)) throw I.ex('IllegalArgumentException', 'duplicate element: ' + I.str(x)); }); v.kind = 'ImmutableSet'; }
            v.immutable = true;
            return R(v, v.$ty());
          }
          break;
        case 'Map':
          if (id === 'of') { const m = newMap(I, 'ImmutableMap', tys[0], tys[1]); for (let i = 0; i + 1 < args.length; i += 2) m.put(I, args[i], args[i + 1]); m.immutable = true; return R(m, m.$ty()); }
          if (id === 'entry') return R(pair(args[0], args[1], tys[0], tys[1]), T('Entry'));
          break;
        case 'Objects':
          if (id === 'equals') return R(I.equals(args[0], args[1]) || (args[0] === null && args[1] === null), TY.bool);
          if (id === 'hash') { let h = 1; for (const a of args) h = (Math.imul(31, h) + I.hashOf(a)) | 0; return R(h, TY.int); }
          if (id === 'hashCode') return R(I.hashOf(args[0]), TY.int);
          if (id === 'isNull') return R(args[0] === null, TY.bool);
          if (id === 'nonNull') return R(args[0] !== null, TY.bool);
          if (id === 'toString') return R(args[0] === null && args.length > 1 ? args[1] : I.str(args[0], tys[0]), TY.string);
          if (id === 'requireNonNull') { if (args[0] === null) throw I.ex('NullPointerException', args[1] || null); return R(args[0], tys[0]); }
          break;
        case 'IntStream': case 'LongStream': case 'Stream': case 'DoubleStream':
          if (id === 'range' || id === 'rangeClosed') { const a = toNum(args[0]), b = toNum(args[1]) + (id === 'rangeClosed' ? 1 : 0); const out = []; for (let i = a; i < b; i++) out.push(i); return R(seq(out, TY.int, 'Int'), T('IntStream')); }
          if (id === 'of') return R(seq(args.length === 1 && args[0] instanceof Arr ? args[0].a.slice() : args.slice(), tys[0], ns === 'IntStream' ? 'Int' : null), T(ns));
          if (id === 'iterate' && args.length === 3) { const out = []; let v = args[0]; while (I.truthy(I.callFn(args[1], [v], [tys[0]]))) { out.push(v); v = I.callFn(args[2], [v], [tys[0]]); if (out.length > 1e6) break; } return R(seq(out, tys[0], ns === 'IntStream' ? 'Int' : null), T(ns)); }
          if (id === 'empty') return R(seq([], TY.dyn), T(ns));
          break;
        case 'Collectors': return R({ $lib: true, coll: id, args, tys, $str: () => 'Collector', $ty: () => T('Collector') }, T('Collector'));
        case 'Comparator': return comparatorStatic(I, id, args, tys);
        case 'Entry': if (id === 'comparingByKey') return R(new Fn({ native: (a) => natCmp(I, a[0].first, a[1].first) }), TY.dyn); if (id === 'comparingByValue') return R(new Fn({ native: (a) => args.length ? toNum(I.callFn(args[0], [a[0].second, a[1].second], [])) : natCmp(I, a[0].second, a[1].second) }), TY.dyn); break;
        case 'Thread': if (id === 'sleep') return R(undefined, TY.void); if (id === 'currentThread') return R({ $lib: true, $str: () => 'Thread[main,5,main]', $ty: () => T('Thread'), name: 'main' }, T('Thread')); break;
        case 'Optional': if (id === 'of') { if (args[0] === null) throw I.ex('NullPointerException', null); return R(opt(args[0], tys[0]), T('Optional')); } if (id === 'empty') return R(opt(null), T('Optional')); if (id === 'ofNullable') return R(opt(args[0], tys[0]), T('Optional')); break;
      }
      return fail();
    }
    if (lang === 'cs') {
      const nsn = { Int32: 'int', Int64: 'long', Double: 'double', Char: 'char', Boolean: 'bool', String: 'string', Single: 'float' }[ns] || ns;
      switch (nsn) {
        case 'Console':
          switch (id) {
            case 'WriteLine': csWrite(I, args, tys, true); return R(undefined, TY.void);
            case 'Write': csWrite(I, args, tys, false); return R(undefined, TY.void);
            case 'ReadLine': { const l = Input.line(I); return R(l, TY.string); }
            case 'Read': return R(Input.char(I), TY.int);
            case 'ReadKey': return R(null, TY.dyn);
            case 'Clear': case 'Beep': case 'ResetColor': return R(undefined, TY.void);
          }
          break;
        case 'int': case 'long': case 'short': case 'byte': case 'uint': case 'ulong': {
          const kind = nsn === 'long' || nsn === 'ulong' ? 'long' : 'int';
          if (id === 'Parse') return R(parseIntCs(I, args[0], kind), kind === 'long' ? TY.long : TY.int);
          if (id === 'TryParse') { let ok = true, v = 0; try { v = parseIntCs(I, args[0], kind); } catch (e) { ok = false; v = kind === 'long' ? 0n : 0; } if (refs[1]) refs[1].set(v); return R(ok, TY.bool); }
          if (id === 'MaxValue' || id === 'MinValue') break;
          if (id === 'IsEven' || id === 'IsOddInteger') break;
          break;
        }
        case 'double': case 'float': case 'decimal':
          if (id === 'Parse') return R(parseDbl(I, args[0]), TY.double);
          if (id === 'TryParse') { let ok = true, v = 0; try { v = parseDbl(I, args[0]); } catch (e) { ok = false; } if (refs[1]) refs[1].set(v); return R(ok, TY.bool); }
          if (id === 'IsNaN') return R(Number.isNaN(toNum(args[0])), TY.bool);
          if (id === 'IsInfinity') return R(!Number.isFinite(toNum(args[0])) && !Number.isNaN(toNum(args[0])), TY.bool);
          break;
        case 'bool': if (id === 'Parse') return R(String(args[0]).trim().toLowerCase() === 'true', TY.bool); break;
        case 'char': {
          const s = chr(toNum(args[0]));
          switch (id) {
            case 'IsDigit': return R(/\p{Nd}/u.test(s), TY.bool);
            case 'IsLetter': return R(/\p{L}/u.test(s), TY.bool);
            case 'IsLetterOrDigit': return R(/[\p{L}\p{Nd}]/u.test(s), TY.bool);
            case 'IsUpper': return R(/\p{Lu}/u.test(s), TY.bool);
            case 'IsLower': return R(/\p{Ll}/u.test(s), TY.bool);
            case 'IsWhiteSpace': return R(/\s/.test(s), TY.bool);
            case 'IsPunctuation': return R(/\p{P}/u.test(s), TY.bool);
            case 'ToUpper': return R(s.toUpperCase().charCodeAt(0), TY.char);
            case 'ToLower': return R(s.toLowerCase().charCodeAt(0), TY.char);
            case 'GetNumericValue': return R(/[0-9]/.test(s) ? toNum(args[0]) - 48 : -1, TY.double);
            case 'ToString': return R(s, TY.string);
            case 'Parse': return R(String(args[0]).charCodeAt(0), TY.char);
          }
          break;
        }
        case 'string':
          switch (id) {
            case 'Join': { const items = args.length === 2 && args[1] && typeof args[1] === 'object' && !(args[1] instanceof Obj) ? collItems(I, args[1]) : args.slice(1); const et = args[1] && args[1].et; return R(items.map(x => I.str(x, et && !et.dim ? et : valTyIn(x))).join(I.str(args[0], tys[0])), TY.string); }
            case 'Concat': return R(args.map((x, i) => I.str(x, tys[i])).join(''), TY.string);
            case 'IsNullOrEmpty': return R(args[0] === null || args[0] === '', TY.bool);
            case 'IsNullOrWhiteSpace': return R(args[0] === null || !String(args[0]).trim(), TY.bool);
            case 'Format': return R(CF.csComposite(I, I.str(args[0]), args.slice(1), tys.slice(1)), TY.string);
            case 'Compare': return R(Math.sign(natCmp(I, args[0], args[1])), TY.int);
            case 'CompareOrdinal': return R(args[0] < args[1] ? -1 : args[0] > args[1] ? 1 : 0, TY.int);
            case 'Equals': return R(args[0] === args[1], TY.bool);
            case 'Empty': break;
          }
          if (id === 'new' || id === 'String') return R(chr(args[0]).repeat(toNum(args[1])), TY.string);
          break;
        case 'Convert': {
          const v = args[0];
          switch (id) {
            case 'ToInt32': case 'ToInt16': case 'ToByte': if (typeof v === 'string') return R(parseIntCs(I, v), TY.int); if (typeof v === 'boolean') return R(v ? 1 : 0, TY.int); if (kindOf(tys[0], v) === 'd' || kindOf(tys[0], v) === 'f') { const r = roundEven(toNum(v)); if (r > 2147483647 || r < -2147483648) throw I.ex('OverflowException', 'Value was either too large or too small for an Int32.'); return R(r, TY.int); } return R(i32(v), TY.int);
            case 'ToInt64': if (typeof v === 'string') return R(parseIntCs(I, v, 'long'), TY.long); return R(BigInt(roundEven(toNum(v))), TY.long);
            case 'ToDouble': case 'ToSingle': case 'ToDecimal': return R(typeof v === 'string' ? parseDbl(I, v) : toNum(v), TY.double);
            case 'ToString': if (args.length === 2 && typeof args[1] === 'number') return R((typeof v === 'bigint' ? v : toNum(v)).toString(args[1]), TY.string); return R(I.str(v, tys[0]), TY.string);
            case 'ToChar': return R(toNum(v), TY.char);
            case 'ToBoolean': return R(typeof v === 'string' ? v.trim().toLowerCase() === 'true' : !!toNum(v), TY.bool);
          }
          break;
        }
        case 'Array': return csArrayFn(I, id, args, tys, refs, n);
        case 'Enumerable':
          if (id === 'Range') { const out = []; for (let i = 0; i < toNum(args[1]); i++) out.push(toNum(args[0]) + i); return R(seq(out, TY.int), T('IEnumerable')); }
          if (id === 'Repeat') return R(seq(Array(toNum(args[1])).fill(args[0]), tys[0]), T('IEnumerable'));
          if (id === 'Empty') return R(seq([], TY.dyn), T('IEnumerable'));
          break;
        case 'Thread': if (id === 'Sleep') return R(undefined, TY.void); break;
        case 'Tuple': if (id === 'Create') return R(LIB.tuple(I, args, tys), T('Tuple')); break;
        case 'Environment': if (id === 'Exit') throw new CF.ExitSig(toNum(args[0])); break;
        case 'Enum': if (id === 'GetValues' || id === 'GetNames') break; break;
      }
      return fail();
    }
    return fail();
  };
  function valTyIn(x) { return valTy(x); }
  function comparatorStatic(I, id, args, tys) {
    const key = args[0];
    const mk2 = f => R(new Fn({ native: f, fname: 'Comparator' }), TY.dyn);
    switch (id) {
      case 'naturalOrder': return mk2(a => natCmp(I, a[0], a[1]));
      case 'reverseOrder': return mk2(a => natCmp(I, a[1], a[0]));
      case 'comparing': case 'comparingInt': case 'comparingDouble': case 'comparingLong':
        if (args[1]) return mk2(a => toNum(I.callFn(args[1], [I.callFn(key, [a[0]], []), I.callFn(key, [a[1]], [])], [])));
        return mk2(a => natCmp(I, I.callFn(key, [a[0]], []), I.callFn(key, [a[1]], [])));
    }
    return NONE;
  }
  function reversedCmp(cmp) { return (a, b) => cmp(b, a); }

  /* ===== Java Arrays and Collections ===== */
  function arrStr(I, arr, deep) {
    if (arr === null) return 'null';
    return '[' + arr.a.map(x => deep && x instanceof Arr ? arrStr(I, x, true) : I.str(x, arr.et)).join(', ') + ']';
  }
  function arraysFn(I, id, args, tys, n) {
    const a = args[0];
    switch (id) {
      case 'toString': return R(a === null ? 'null' : arrStr(I, a), TY.string);
      case 'deepToString': return R(arrStr(I, a, true), TY.string);
      case 'sort': {
        if (a === null) throw I.ex('NullPointerException', null);
        const from = args.length >= 3 && typeof args[1] === 'number' ? toNum(args[1]) : 0, to = args.length >= 3 && typeof args[2] === 'number' ? toNum(args[2]) : a.a.length;
        const cmpArg = args.find((x, i) => i > 0 && (x instanceof Fn || x instanceof Obj));
        if (cmpArg && a.et && NK[a.et.n] && !a.et.box) throw new CF.CompileError('A Comparator cannot sort a primitive array like int[]. Use Integer[] instead', n.line);
        const part = a.a.slice(from, to);
        const prim = a.et && NK[a.et.n] && !a.et.dim;
        sortArr(I, part, cmpArg ? cmpFrom(I, cmpArg) : prim ? (x, y) => (x < y ? -1 : x > y ? 1 : (Object.is(x, -0) && y === 0 ? -1 : 0)) : (x, y) => natCmp(I, x, y));
        for (let i = from; i < to; i++) a.a[i] = part[i - from];
        return R(undefined, TY.void);
      }
      case 'fill': { const v = args[args.length - 1]; const from = args.length === 4 ? toNum(args[1]) : 0, to = args.length === 4 ? toNum(args[2]) : a.a.length; for (let i = from; i < to; i++) a.a[i] = I.conv(v, a.et); return R(undefined, TY.void); }
      case 'asList': { const items = args.length === 1 && a instanceof Arr && !(a.et && NK[a.et.n] && !a.et.box && !a.et.dim) ? a.a : args; const l = newList(I, 'ArraysList', args.length === 1 && a instanceof Arr ? a.et : tys[0], items === a.a ? a.a : items.slice()); l.fixed = true; return R(l, T('List', { args: [l.et] })); }
      case 'copyOf': { const len = toNum(args[1]); const out = a.a.slice(0, len); while (out.length < len) out.push(I.defaultVal(a.et)); return R(new Arr(out, a.et), tys[0]); }
      case 'copyOfRange': { const from = toNum(args[1]), to = toNum(args[2]); if (from < 0 || from > a.a.length) throw I.ex('ArrayIndexOutOfBoundsException', `Array index out of range: ${from}`); const out = a.a.slice(from, to); while (out.length < to - from) out.push(I.defaultVal(a.et)); return R(new Arr(out, a.et), tys[0]); }
      case 'equals': return R(a === args[1] || (a && args[1] && a.a.length === args[1].a.length && a.a.every((x, i) => I.equals(x, args[1].a[i]))), TY.bool);
      case 'deepEquals': return R(arrStr(I, a, true) === arrStr(I, args[1], true), TY.bool);
      case 'stream': return R(seq(a.a.slice(), a.et, a.et && a.et.n === 'int' ? 'Int' : a.et && a.et.n === 'double' ? 'Double' : null), T('Stream'));
      case 'binarySearch': { const key = args[1]; let lo = 0, hi = a.a.length - 1; while (lo <= hi) { const mid = (lo + hi) >>> 1; const c = natCmp(I, a.a[mid], key); if (c < 0) lo = mid + 1; else if (c > 0) hi = mid - 1; else return R(mid, TY.int); } return R(-(lo + 1), TY.int); }
      case 'hashCode': { let h = 1; for (const x of a.a) h = (Math.imul(31, h) + I.hashOf(x)) | 0; return R(h, TY.int); }
      case 'setAll': { for (let i = 0; i < a.a.length; i++) a.a[i] = I.conv(I.callFn(args[1], [i], [TY.int]), a.et); return R(undefined, TY.void); }
    }
    return NONE;
  }
  function collectionsFn(I, id, args, tys, n) {
    const c = args[0];
    switch (id) {
      case 'sort': { if (c.immutable) throw I.ex('UnsupportedOperationException', null); sortArr(I, c.a, cmpFrom(I, args[1])); return R(undefined, TY.void); }
      case 'reverse': c.a.reverse(); return R(undefined, TY.void);
      case 'max': case 'min': { const items = collItems(I, c); if (!items.length) throw I.ex('NoSuchElementException', null); const cmp = cmpFrom(I, args[1]); const r = items.reduce((m, v) => (id === 'max' ? cmp(v, m) > 0 : cmp(v, m) < 0) ? v : m); return R(r, c.et); }
      case 'swap': { const i = toNum(args[1]), j = toNum(args[2]); const t = c.a[i]; c.a[i] = c.a[j]; c.a[j] = t; return R(undefined, TY.void); }
      case 'frequency': return R(collItems(I, c).filter(x => I.equals(x, args[1]) || x === args[1]).length, TY.int);
      case 'unmodifiableList': case 'unmodifiableSet': case 'unmodifiableMap': case 'synchronizedList': return R(c, tys[0]);
      case 'emptyList': return R(newList(I, 'ImmutableList', null), T('List'));
      case 'emptyMap': return R(newMap(I, 'HashMap', null, null), T('Map'));
      case 'nCopies': return R(newList(I, 'ImmutableList', tys[1], Array(toNum(args[0])).fill(args[1])), T('List', { args: [tys[1]] }));
      case 'reverseOrder': if (args.length) { const f = cmpFrom(I, args[0]); return R(new Fn({ native: a => f(a[1], a[0]) }), TY.dyn); } return R(new Fn({ native: a => natCmp(I, a[1], a[0]), fname: 'reverseOrder' }), TY.dyn);
      case 'shuffle': { const a = c.a; const r = args[1] && args[1].seed !== undefined ? args[1] : null; for (let i = a.length - 1; i > 0; i--) { const j = r ? jnextInt(r, i + 1) : Math.floor(Math.random() * (i + 1)); const t = a[i]; a[i] = a[j]; a[j] = t; } return R(undefined, TY.void); }
      case 'addAll': { args.slice(1).forEach(x => c.add ? c.add(I, x) : c.a.push(x)); return R(true, TY.bool); }
      case 'singletonList': return R(newList(I, 'ImmutableList', tys[0], [args[0]]), T('List'));
      case 'binarySearch': return arraysFn(I, 'binarySearch', [{ a: c.a }, args[1]], tys, n);
    }
    return NONE;
  }
  function csArrayFn(I, id, args, tys, refs, n) {
    const a = args[0];
    switch (id) {
      case 'Sort': {
        if (args.length >= 2 && args[1] instanceof Arr) { const idx = a.a.map((k, i) => i).sort((x, y) => natCmp(I, a.a[x], a.a[y])); const ks = idx.map(i => a.a[i]), vs = idx.map(i => args[1].a[i]); a.a.splice(0, a.a.length, ...ks); args[1].a.splice(0, vs.length, ...vs); return R(undefined, TY.void); }
        sortArr(I, a.a, args[1] ? cmpFrom(I, args[1]) : (x, y) => natCmp(I, x, y)); return R(undefined, TY.void);
      }
      case 'Reverse': a.a.reverse(); return R(undefined, TY.void);
      case 'IndexOf': return R(a.a.findIndex(x => I.equals(x, args[1]) || x === args[1]), TY.int);
      case 'Fill': for (let i = 0; i < a.a.length; i++) a.a[i] = args[1]; return R(undefined, TY.void);
      case 'Copy': { const len = toNum(args[args.length - 1]); if (args.length === 3) for (let i = 0; i < len; i++) args[1].a[i] = a.a[i]; else for (let i = 0; i < len; i++) args[2].a[toNum(args[3]) + i] = a.a[toNum(args[1]) + i]; return R(undefined, TY.void); }
      case 'Resize': { const r = refs[0]; const old = r.get(); const len = toNum(args[1]); const out = old ? old.a.slice(0, len) : []; while (out.length < len) out.push(I.defaultVal(old ? old.et : TY.int)); r.set(new Arr(out, old ? old.et : TY.int)); return R(undefined, TY.void); }
      case 'Exists': return R(a.a.some(x => I.truthy(I.callFn(args[1], [x], [a.et]))), TY.bool);
      case 'Find': { const r = a.a.find(x => I.truthy(I.callFn(args[1], [x], [a.et]))); return R(r === undefined ? I.defaultVal(a.et) : r, a.et); }
      case 'BinarySearch': return arraysFn(I, 'binarySearch', args, tys, n);
      case 'Empty': return R(new Arr([], tys[0]), tys[0]);
      case 'Clear': for (let i = toNum(args[1] || 0); i < (args[2] !== undefined ? toNum(args[1]) + toNum(args[2]) : a.a.length); i++) a.a[i] = I.defaultVal(a.et); return R(undefined, TY.void);
    }
    return NONE;
  }

  /* ===== C and C++ functions ===== */
  function range(I, b, e) {
    if (b instanceof Arr) b = new Ptr(b.a, 0, null, b.et);
    if (e instanceof Arr) e = new Ptr(e.a, e.a.length, null, e.et);
    if (b instanceof Ptr) return { a: b.arr, lo: b.i, hi: e.i, et: b.et };
    if (b && b.$iter) {
      if (b.str) { const s = b.ref.get(); const chars = Array.from(s, c => c.charCodeAt(0)); return { a: chars, lo: b.i, hi: e.i, et: TY.char, str: b.ref }; }
      if (b.rev) { const a = b.arr(); const n = a.length; const view = a.slice().reverse(); return { a: view, lo: b.i, hi: e.i, et: b.c.et, rev: a }; }
      if (b.keys) { return { a: b.keys.map(k => b.map ? mk(PairP, { rec: b.map.m.get(k), t1: b.map.kt, t2: b.map.vt }) : (b.set ? k : k)), lo: b.i, hi: e.i, et: b.c.et, ro: true }; }
      return { a: b.arr(), lo: b.i, hi: e.i, et: b.c.et };
    }
    throw new CF.CompileError('Expected two iterators like v.begin(), v.end()', I.lastLine);
  }
  function commit(r) { if (r.str) r.str.set(r.a.map(chr).join('')); if (r.rev) { const n = r.rev.length; for (let i = 0; i < n; i++) r.rev[i] = r.a[n - 1 - i]; } }
  function itAt(I, b, idx) { if (b instanceof Ptr) return b.add(idx - b.i); if (b instanceof Arr) return new Ptr(b.a, idx, null, b.et); const c = b.clone(); c.i = idx; return c; }
  LIB.callGlobal = function (I, id, args, tys, refs, n, env) {
    const lang = I.lang;
    if (lang !== 'c' && lang !== 'cpp') {
      if (lang === 'java' && (id === 'println' || id === 'print')) { jprint(I, args, tys, id === 'println', false, n); return R(undefined, TY.void); }
      return NONE;
    }
    const a0 = args[0];
    const S = s => I.cstr(s);
    switch (id) {
      case 'printf': if (!args.length) throw new CF.CompileError('printf needs a format string, like printf("%d\\n", x)', n.line); { const s = CF.printf(I, S(a0), args.slice(1), tys.slice(1), lang); I.write(s); return R(s.length, TY.int); }
      case 'fprintf': { const s = CF.printf(I, S(args[1]), args.slice(2), tys.slice(2), lang); I.write(s, a0 && a0.file === 'stderr'); return R(s.length, TY.int); }
      case 'puts': I.write(S(a0) + '\n'); return R(1, TY.int);
      case 'fputs': I.write(S(a0), args[1] && args[1].file === 'stderr'); return R(1, TY.int);
      case 'putchar': case 'fputc': I.write(chr(toNum(a0) & 0xff)); return R(toNum(a0), TY.int);
      case 'sprintf': case 'snprintf': {
        const fmtI = id === 'sprintf' ? 1 : 2;
        let s = CF.printf(I, S(args[fmtI]), args.slice(fmtI + 1), tys.slice(fmtI + 1), lang);
        if (id === 'snprintf') s = s.slice(0, Math.max(0, toNum(args[1]) - 1));
        writeC(I, a0, s); return R(s.length, TY.int);
      }
      case 'scanf': case 'sscanf': {
        let src = I;
        let fi = 0;
        if (id === 'sscanf') { const str = S(a0); src = { stdin: str, inPos: 0, warned: new Set(), notes: [], warn() {} }; fi = 1; }
        const fmt = S(args[fi]);
        let ai = fi + 1, count = 0;
        const re = /%(\d*)(l{0,2}|h)?([dfsciu]|lf)|(\s+)|([^%\s]+)/g;
        let m;
        while ((m = re.exec(fmt))) {
          if (m[4]) { Input.skipWs(src); continue; }
          if (m[5]) { Input.skipWs(src); for (const ch of m[5]) { if (src.stdin[src.inPos] === ch) src.inPos++; else return R(count, TY.int); } continue; }
          const conv = m[3];
          let p = args[ai++];
          if (p instanceof Arr) p = new Ptr(p.a, 0, null, p.et);
          if (!(p instanceof Ptr)) throw new CF.CompileError('scanf needs the address of each variable, like scanf("%d", &x). The & is missing', n.line);
          if (conv === 'c') { if (src.inPos >= src.stdin.length) { if (id === 'scanf') noInput(I); return R(count || -1, TY.int); } p.set(src.stdin.charCodeAt(src.inPos++)); count++; continue; }
          const tok = Input.token(src);
          if (tok === null) return R(count || -1, TY.int);
          if (conv === 's') { const cs = I.cchars(tok); if (p.box) p.set(tok); else cs.forEach((c, i) => { p.arr[p.i + i] = c; }); count++; continue; }
          if (conv === 'f' || conv === 'lf') { const mm = tok.match(/^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?/); if (!mm) { src.inPos -= tok.length; return R(count, TY.int); } src.inPos -= tok.length - mm[0].length; p.set(I.conv(parseFloat(mm[0]), p.et || TY.double)); count++; continue; }
          const mm = tok.match(/^[+-]?\d+/);
          if (!mm) { src.inPos -= tok.length; return R(count, TY.int); }
          src.inPos -= tok.length - mm[0].length;
          p.set(I.conv(m[2] && m[2].startsWith('l') && p.et && (p.et.n === 'long' || p.et.n === 'ulong') ? BigInt(mm[0]) : Number(mm[0]), p.et || TY.int));
          if (p.box) p.box.uninit = false;
          count++;
        }
        return R(count, TY.int);
      }
      case 'getchar': { const c = Input.char(I); return R(c, TY.int); }
      case 'fgets': case 'gets': {
        const l = Input.line(I);
        if (l === null) return R(null, TY.dyn);
        const max = id === 'fgets' ? toNum(args[1]) - 1 : 1e9;
        let s = l;
        if (id === 'fgets') { const hadNl = I.stdin[I.inPos - 1] === '\n'; if (s.length + 1 <= max && hadNl) s += '\n'; s = s.slice(0, max); }
        writeC(I, a0, s);
        return R(a0, tys[0]);
      }
      case 'malloc': { const bytes = toNum(a0); if (bytes > 5e7) throw new Fatal('malloc asked for more memory than the playground allows'); const p = new Ptr([], 0, null, null); p.raw = bytes; p.garbage = true; return R(p, T('void', { ptr: 1 })); }
      case 'calloc': { const p = new Ptr([], 0, null, null); p.raw = toNum(a0) * toNum(args[1]); p.zero = true; return R(p, T('void', { ptr: 1 })); }
      case 'realloc': { const old = a0; const bytes = toNum(args[1]); if (!old) { const p = new Ptr([], 0, null, null); p.raw = bytes; return R(p, T('void', { ptr: 1 })); } const size = I.sizeOf(old.et) || 1; const nn = Math.floor(bytes / size); while (old.arr.length < nn) old.arr.push(I.defaultVal(old.et)); old.arr.length = nn; return R(old, tys[0]); }
      case 'free': if (a0 instanceof Ptr && a0.arr) { if (a0.arr.freed) throw new Fatal('free() was called twice on the same memory (a double free). Real programs crash with "free(): double free detected"'); a0.arr.freed = true; } return R(undefined, TY.void);
      case 'exit': throw new CF.ExitSig(toNum(a0));
      case 'assert': if (!I.truthy(a0)) throw new Fatal(`Assertion failed on line ${n.line}`); return R(undefined, TY.void);
      case 'atoi': case 'atol': case 'atoll': { const m = S(a0).trim().match(/^[+-]?\d+/); const v = m ? Number(m[0]) : 0; return R(id === 'atoi' ? i32(v) : BigInt(m ? m[0] : 0), id === 'atoi' ? TY.int : TY.long); }
      case 'atof': { const m = S(a0).trim().match(/^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?/); return R(m ? parseFloat(m[0]) : 0, TY.double); }
      case 'rand': { if (!I.glibc) I.glibc = glibcInit(1); return R(glibcNext(I.glibc), TY.int); }
      case 'srand': I.glibc = glibcInit(toNum(a0) >>> 0); return R(undefined, TY.void);
      case 'time': return R(BigInt(Math.floor(Date.now() / 1000)), TY.long);
      case 'clock': return R(BigInt(Math.round((typeof performance !== 'undefined' ? performance.now() : Date.now()) * 1000)), TY.long);
      case 'qsort': {
        const p = a0 instanceof Arr ? new Ptr(a0.a, 0, null, a0.et) : a0;
        const cnt = toNum(args[1]);
        const part = p.arr.slice(p.i, p.i + cnt);
        part.sort((x, y) => toNum(I.callFn(args[3], [new Ptr([x], 0, null, p.et), new Ptr([y], 0, null, p.et)], [T('void', { ptr: 1 }), T('void', { ptr: 1 })])));
        for (let i = 0; i < cnt; i++) p.arr[p.i + i] = part[i];
        return R(undefined, TY.void);
      }
      case 'strlen': return R(BigInt(S(a0).length), TY.ulong);
      case 'strcpy': case 'strncpy': { let s = S(args[1]); if (id === 'strncpy') s = s.slice(0, toNum(args[2])); writeC(I, a0, s, id === 'strncpy' && s.length >= toNum(args[2])); return R(a0, tys[0]); }
      case 'strcat': case 'strncat': { let s = S(args[1]); if (id === 'strncat') s = s.slice(0, toNum(args[2])); writeC(I, a0, S(a0) + s); return R(a0, tys[0]); }
      case 'strcmp': { const x = S(a0), y = S(args[1]); return R(x < y ? -1 : x > y ? 1 : 0, TY.int); }
      case 'strncmp': { const k = toNum(args[2]); const x = S(a0).slice(0, k), y = S(args[1]).slice(0, k); return R(x < y ? -1 : x > y ? 1 : 0, TY.int); }
      case 'strchr': case 'strrchr': { const s = S(a0); const i = id === 'strchr' ? s.indexOf(chr(args[1])) : s.lastIndexOf(chr(args[1])); if (i < 0) return R(null, tys[0]); const p = a0 instanceof Arr ? new Ptr(a0.a, 0, null, TY.char) : a0; return R(p.add(i), T('char', { ptr: 1 })); }
      case 'strstr': { const s = S(a0); const i = s.indexOf(S(args[1])); if (i < 0) return R(null, tys[0]); const p = a0 instanceof Arr ? new Ptr(a0.a, 0, null, TY.char) : a0; return R(p.add(i), T('char', { ptr: 1 })); }
      case 'strcspn': case 'strspn': { const s = S(a0), set = S(args[1]); let i = 0; while (i < s.length && (id === 'strcspn' ? !set.includes(s[i]) : set.includes(s[i]))) i++; return R(BigInt(i), TY.ulong); }
      case 'strdup': return R(new Ptr(I.cchars(S(a0)), 0, null, TY.char), T('char', { ptr: 1 }));
      case 'memset': { const p = a0 instanceof Arr ? new Ptr(a0.a, 0) : a0; const cnt = toNum(args[2]); const sz = I.sizeOf(p.et) || 4; const v = toNum(args[1]); const per = v === 0 ? 0 : v === -1 || v === 255 ? -1 : (sz === 1 ? v : v * 0x01010101); const target = a0 instanceof Arr ? a0.a : p.arr; for (let i = 0; i < Math.ceil(cnt / (a0 instanceof Arr ? I.sizeOf(a0.et) : sz)) && p.i + i < target.length; i++) target[p.i + i] = (a0 instanceof Arr && a0.et.n === 'char') || sz === 1 ? v : per; return R(a0, tys[0]); }
      case 'memcpy': case 'memmove': { const d = a0 instanceof Arr ? new Ptr(a0.a, 0) : a0, s = args[1] instanceof Arr ? new Ptr(args[1].a, 0) : args[1]; const sz = I.sizeOf((args[1] instanceof Arr ? args[1].et : s.et)) || 1; const cnt = Math.ceil(toNum(args[2]) / sz); const part = s.arr.slice(s.i, s.i + cnt); part.forEach((x, i) => { d.arr[d.i + i] = I.copyVal(x); }); return R(a0, tys[0]); }
      case 'toupper': return R(chr(a0).toUpperCase().charCodeAt(0), TY.int);
      case 'tolower': return R(chr(a0).toLowerCase().charCodeAt(0), TY.int);
      case 'isdigit': return R(/[0-9]/.test(chr(a0)) ? 2048 : 0, TY.int);
      case 'isalpha': return R(/[A-Za-z]/.test(chr(a0)) ? 1024 : 0, TY.int);
      case 'isalnum': return R(/[A-Za-z0-9]/.test(chr(a0)) ? 8 : 0, TY.int);
      case 'isspace': return R(/[ \t\n\r\f\v]/.test(chr(a0)) ? 8192 : 0, TY.int);
      case 'isupper': return R(/[A-Z]/.test(chr(a0)) ? 256 : 0, TY.int);
      case 'islower': return R(/[a-z]/.test(chr(a0)) ? 512 : 0, TY.int);
      case 'ispunct': return R(/[!-\/:-@\[-`{-~]/.test(chr(a0)) ? 4 : 0, TY.int);
      case 'isxdigit': return R(/[0-9a-fA-F]/.test(chr(a0)) ? 4096 : 0, TY.int);
      case 'fflush': return R(0, TY.int);
    }
    if (lang === 'c') { const r = mathFn(I, id, args, tys); if (r !== NONE) { if (id === 'abs') return R(i32(r[0]), TY.int); return r; } return NONE; }
    /* C++ only */
    switch (id) {
      case 'setw': return R({ manip: 'setw', n: toNum(a0) }, TY.dyn);
      case 'setprecision': return R({ manip: 'setprecision', n: toNum(a0) }, TY.dyn);
      case 'setfill': return R({ manip: 'setfill', n: toNum(a0) }, TY.dyn);
      case 'to_string': { const k = kindOf(tys[0], a0); return R(k === 'd' || k === 'f' ? CF.fmt.fixedExact(toNum(a0), 6) : String(a0), TY.string); }
      case 'stoi': case 'stol': case 'stoll': {
        const s = S(a0); const m = s.trim().match(/^[+-]?\d+/);
        if (!m) throw I.ex('invalid_argument', id);
        const b = BigInt(m[0]);
        if (id === 'stoi' && (b > 2147483647n || b < -2147483648n)) throw I.ex('out_of_range', id);
        if (refs[1] || args[1] instanceof Ptr) { const p = args[1]; if (p) p.set(BigInt(s.indexOf(m[0]) + m[0].length)); }
        return R(id === 'stoi' ? Number(b) : b, id === 'stoi' ? TY.int : TY.long);
      }
      case 'stod': case 'stof': { const m = S(a0).trim().match(/^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?/); if (!m) throw I.ex('invalid_argument', id); return R(parseFloat(m[0]), TY.double); }
      case 'getline': {
        const s = a0, r = refs[1];
        if (!r) throw new CF.CompileError('getline needs a string variable: getline(cin, line)', n.line);
        const delim = args[2] !== undefined ? chr(args[2]) : '\n';
        if (s && s.$lib) { if (s.pos >= s.buf.length) { s.fail = true; return R(s, TY.dyn); } let e = s.buf.indexOf(delim, s.pos); if (e < 0) e = s.buf.length; r.set(s.buf.slice(s.pos, e)); s.pos = e + 1; return R(s, TY.dyn); }
        if (I.inPos >= I.stdin.length) { s.fail = true; noInput(I); r.set(''); return R(s, TY.dyn); }
        let e = I.stdin.indexOf(delim, I.inPos); if (e < 0) e = I.stdin.length;
        r.set(I.stdin.slice(I.inPos, e).replace(/\r$/, '')); I.inPos = e + 1;
        if (r.box) r.box.uninit = false;
        return R(s, TY.dyn);
      }
      case 'swap': { if (!refs[0] || !refs[1]) throw new CF.CompileError('swap needs two variables', n.line); const x = refs[0].get(), y = refs[1].get(); refs[0].set(y); refs[1].set(x); return R(undefined, TY.void); }
      case 'make_pair': return R(pair(a0, args[1], tys[0], tys[1]), T('pair', { args: [tys[0], tys[1]] }));
      case 'make_tuple': case 'tie': return R(LIB.tuple(I, args, tys), T('tuple'));
      case 'gcd': case '__gcd': { let x = Math.abs(toNum(a0)), y = Math.abs(toNum(args[1])); while (y) [x, y] = [y, x % y]; return R(x, tys[0]); }
      case 'lcm': { let x = Math.abs(toNum(a0)), y = Math.abs(toNum(args[1])); let g = x, h = y; while (h) [g, h] = [h, g % h]; return R(g ? x / g * y : 0, tys[0]); }
      case 'begin': return R(a0 instanceof Arr ? new Ptr(a0.a, 0, null, a0.et) : iter(a0, 0), TY.dyn);
      case 'end': return R(a0 instanceof Arr ? new Ptr(a0.a, a0.a.length, null, a0.et) : iter(a0, a0.a.length), TY.dyn);
      case 'distance': return R(BigInt((args[1].i) - a0.i), TY.long);
      case 'advance': if (refs[0]) { const it = refs[0].get(); if (it.$iter) it.move(toNum(args[1])); else refs[0].set(it.add(toNum(args[1]))); } return R(undefined, TY.void);
      case 'max': case 'min': {
        if (args.length === 1 && a0 instanceof Arr) { const r = a0.a.reduce((m, v) => (id === 'max' ? natCmp(I, v, m) > 0 : natCmp(I, v, m) < 0) ? v : m); return R(r, (a0.tys && a0.tys[0]) || a0.et); }
        return mathFn(I, id, args, tys);
      }
      case 'abs': { const r = mathFn(I, 'abs', args, tys); return r; }
      case 'move': return R(a0, tys[0]);
      case 'get': return R(a0 && a0.items ? a0.items[0] : a0, TY.dyn);
    }
    if (['sort', 'stable_sort', 'reverse', 'find', 'find_if', 'count', 'count_if', 'accumulate', 'max_element', 'min_element', 'fill', 'iota', 'unique', 'binary_search', 'lower_bound', 'upper_bound', 'next_permutation', 'prev_permutation', 'all_of', 'any_of', 'none_of', 'transform', 'copy', 'partial_sort', 'nth_element', 'rotate', 'equal', 'is_sorted', 'for_each', 'remove', 'remove_if'].includes(id)) {
      const r = range(I, a0, args[1]);
      const part = r.a.slice(r.lo, r.hi);
      const put = vals => { vals.forEach((v, i) => { r.a[r.lo + i] = v; }); commit(r); };
      switch (id) {
        case 'sort': case 'stable_sort': case 'partial_sort': case 'nth_element': { const cmpArg = id === 'partial_sort' || id === 'nth_element' ? args[3] : args[2]; if (id === 'partial_sort' || id === 'nth_element') { const rr = range(I, a0, args[2]); const p2 = rr.a.slice(rr.lo, rr.hi); sortArr(I, p2, cmpFrom(I, cmpArg, 'less')); p2.forEach((v, i) => { rr.a[rr.lo + i] = v; }); commit(rr); return R(undefined, TY.void); } sortArr(I, part, cmpFrom(I, cmpArg, 'less')); put(part); return R(undefined, TY.void); }
        case 'reverse': part.reverse(); put(part); return R(undefined, TY.void);
        case 'rotate': { const mid = args[1]; const rr = range(I, a0, args[2]); const p = rr.a.slice(rr.lo, rr.hi); const k = mid.i - rr.lo; const rot = p.slice(k).concat(p.slice(0, k)); rot.forEach((v, i) => { rr.a[rr.lo + i] = v; }); commit(rr); return R(itAt(I, a0, rr.lo + (p.length - k)), TY.dyn); }
        case 'fill': part.fill(I.conv(args[2], r.et)); put(part); return R(undefined, TY.void);
        case 'iota': { let v = toNum(args[2]); put(part.map(() => v++)); return R(undefined, TY.void); }
        case 'find': { const i = part.findIndex(x => I.equals(x, args[2]) || x == args[2]); return R(itAt(I, a0, r.lo + (i < 0 ? part.length : i)), TY.dyn); }
        case 'find_if': { const i = part.findIndex(x => I.truthy(I.callFn(args[2], [x], [r.et]))); return R(itAt(I, a0, r.lo + (i < 0 ? part.length : i)), TY.dyn); }
        case 'count': return R(BigInt(part.filter(x => I.equals(x, args[2]) || x == args[2]).length), TY.long);
        case 'count_if': return R(BigInt(part.filter(x => I.truthy(I.callFn(args[2], [x], [r.et]))).length), TY.long);
        case 'all_of': return R(part.every(x => I.truthy(I.callFn(args[2], [x], [r.et]))), TY.bool);
        case 'any_of': return R(part.some(x => I.truthy(I.callFn(args[2], [x], [r.et]))), TY.bool);
        case 'none_of': return R(!part.some(x => I.truthy(I.callFn(args[2], [x], [r.et]))), TY.bool);
        case 'for_each': part.forEach(x => I.callFn(args[2], [x], [r.et])); return R(undefined, TY.void);
        case 'accumulate': {
          let acc = args[2], at = tys[2];
          for (const x of part) {
            if (args[3]) acc = I.callFn(args[3], [acc, x], [at, r.et]);
            else if (typeof acc === 'string') acc = acc + (typeof x === 'string' ? x : chr(x));
            else { const k = kindOf(at, acc); const [v] = I.arith('+', acc, k, x, kindOf(r.et, x), n); acc = I.conv(v, at); }
          }
          return R(acc, at);
        }
        case 'max_element': case 'min_element': {
          if (!part.length) return R(itAt(I, a0, r.hi), TY.dyn);
          const cmp = cmpFrom(I, args[2], 'less');
          let best = 0;
          for (let i = 1; i < part.length; i++) { if (id === 'max_element' ? cmp(part[best], part[i]) < 0 : cmp(part[i], part[best]) < 0) best = i; }
          return R(itAt(I, a0, r.lo + best), TY.dyn);
        }
        case 'unique': { const out = []; for (const x of part) if (!out.length || !I.equals(out[out.length - 1], x) && out[out.length - 1] !== x) out.push(x); put(out); return R(itAt(I, a0, r.lo + out.length), TY.dyn); }
        case 'remove': case 'remove_if': { const keep = part.filter(x => id === 'remove' ? !(I.equals(x, args[2]) || x == args[2]) : !I.truthy(I.callFn(args[2], [x], [r.et]))); put(keep); return R(itAt(I, a0, r.lo + keep.length), TY.dyn); }
        case 'binary_search': return R(part.some(x => natCmp(I, x, args[2]) === 0), TY.bool);
        case 'lower_bound': case 'upper_bound': { let lo = 0, hi = part.length; while (lo < hi) { const mid = (lo + hi) >> 1; const c = natCmp(I, part[mid], args[2]); if (id === 'lower_bound' ? c < 0 : c <= 0) lo = mid + 1; else hi = mid; } return R(itAt(I, a0, r.lo + lo), TY.dyn); }
        case 'is_sorted': return R(part.every((x, i) => i === 0 || natCmp(I, part[i - 1], x) <= 0), TY.bool);
        case 'equal': { const r2 = range(I, args[2], itAt(I, args[2], (args[2].i || 0) + part.length)); return R(part.every((x, i) => I.equals(x, r2.a[r2.lo + i]) || x == r2.a[r2.lo + i]), TY.bool); }
        case 'next_permutation': case 'prev_permutation': {
          const a = part, nx = id === 'next_permutation';
          const c = (x, y) => nx ? natCmp(I, x, y) : natCmp(I, y, x);
          let i = a.length - 2; while (i >= 0 && c(a[i], a[i + 1]) >= 0) i--;
          if (i < 0) { a.reverse(); put(a); return R(false, TY.bool); }
          let j = a.length - 1; while (c(a[j], a[i]) <= 0) j--;
          [a[i], a[j]] = [a[j], a[i]];
          const tail = a.splice(i + 1).reverse(); a.push(...tail);
          put(a); return R(true, TY.bool);
        }
        case 'transform': { const out = args[2]; const fn = args.length === 4 ? args[3] : args[4]; const res = part.map(x => I.conv(I.callFn(fn, [x], [r.et]), r.et)); const ro = range(I, out, itAt(I, out, (out.i || 0) + res.length)); res.forEach((v, i) => { ro.a[ro.lo + i] = v; }); commit(ro); return R(itAt(I, out, (out.i || 0) + res.length), TY.dyn); }
        case 'copy': { const out = args[2]; if (out && out.inserter) { part.forEach(x => out.c.a.push(x)); return R(out, TY.dyn); } const ro = range(I, out, itAt(I, out, (out.i || 0) + part.length)); part.forEach((v, i) => { ro.a[ro.lo + i] = v; }); commit(ro); return R(itAt(I, out, (out.i || 0) + part.length), TY.dyn); }
      }
    }
    if (id === 'back_inserter') return R({ $lib: true, inserter: true, c: a0, $str: () => 'inserter', $ty: () => T('iterator') }, TY.dyn);
    const r = mathFn(I, id, args, tys);
    if (r !== NONE) return r;
    return NONE;
  };
  function writeC(I, dst, s, noTerm) {
    const codes = Array.from(s, c => c.charCodeAt(0));
    if (!noTerm) codes.push(0);
    if (dst instanceof Arr) { if (codes.length > dst.a.length) throw new Fatal(`The text "${s}" needs ${codes.length} chars but the array holds only ${dst.a.length}. Writing past the end is a buffer overflow`); codes.forEach((c, i) => { dst.a[i] = c; }); return; }
    if (dst instanceof Ptr && dst.arr) { if (dst.i + codes.length > dst.arr.length) throw new Fatal(`The text "${s}" needs ${codes.length} chars but only ${dst.arr.length - dst.i} are left in that memory. Writing past the end is a buffer overflow`); codes.forEach((c, i) => { dst.arr[dst.i + i] = c; }); return; }
    if (dst instanceof Ptr && dst.box) { dst.box.v = s; return; }
    throw new Fatal('The destination for the text is not a char array');
  }

  /* ===== properties: arr.length, list.Count, p.first, Math.PI, Integer.MAX_VALUE ===== */
  LIB.member = function (I, o, id, n) {
    const lang = I.lang;
    const ro = (v, ty) => ({ ty: ty || valTy(v), get: () => v, set: () => { throw new CF.CompileError(`${id} cannot be changed`, n.line); } });
    if (o instanceof NS) {
      const ns = o.name;
      if (ns === 'std' || ns === 'string') { const r = LIB.name(I, id, n); if (r) return ro(r[0], r[1]); if (ns === 'std' && (GLOBAL_CPP.has(id) || GLOBAL_C.has(id))) return ro(new Fn({ fname: id, native: (args, tys, refs) => LIB.callGlobal(I, id, args, tys, refs || [], n, null)[0] })); if (id === 'npos') return ro(18446744073709551615n, TY.ulong); }
      if (ns === 'System' && (id === 'out' || id === 'err')) return ro(new NS('System.' + id));
      if (ns === 'System' && id === 'in') return ro({ $lib: true, $str: () => 'System.in', $ty: () => T('InputStream') });
      const C = {
        Math: { PI: [Math.PI, TY.double], E: [Math.E, TY.double], Tau: [2 * Math.PI, TY.double] },
        MathF: { PI: [Math.fround(Math.PI), TY.float] },
        Integer: { MAX_VALUE: [2147483647, TY.int], MIN_VALUE: [-2147483648, TY.int], SIZE: [32, TY.int] },
        Long: { MAX_VALUE: [9223372036854775807n, TY.long], MIN_VALUE: [-9223372036854775808n, TY.long] },
        Short: { MAX_VALUE: [32767, TY.short], MIN_VALUE: [-32768, TY.short] }, Byte: { MAX_VALUE: [127, TY.byte], MIN_VALUE: [-128, TY.byte] },
        Character: { MAX_VALUE: [65535, TY.char], MIN_VALUE: [0, TY.char] },
        Double: { MAX_VALUE: [Number.MAX_VALUE, TY.double], MIN_VALUE: [5e-324, TY.double], POSITIVE_INFINITY: [Infinity, TY.double], NEGATIVE_INFINITY: [-Infinity, TY.double], NaN: [NaN, TY.double] },
        Float: { MAX_VALUE: [3.4028234663852886e38, TY.float], MIN_VALUE: [1.401298464324817e-45, TY.float] },
        Boolean: { TRUE: [true, TY.bool], FALSE: [false, TY.bool] },
        int: { MaxValue: [2147483647, TY.int], MinValue: [-2147483648, TY.int] }, Int32: { MaxValue: [2147483647, TY.int], MinValue: [-2147483648, TY.int] },
        long: { MaxValue: [9223372036854775807n, TY.long], MinValue: [-9223372036854775808n, TY.long] }, Int64: { MaxValue: [9223372036854775807n, TY.long], MinValue: [-9223372036854775808n, TY.long] },
        double: { MaxValue: [Number.MAX_VALUE, TY.double], MinValue: [-Number.MAX_VALUE, TY.double], Epsilon: [5e-324, TY.double], NaN: [NaN, TY.double], PositiveInfinity: [Infinity, TY.double], NegativeInfinity: [-Infinity, TY.double] },
        float: { MaxValue: [3.4028234663852886e38, TY.float] }, byte: { MaxValue: [255, TY.ubyte], MinValue: [0, TY.ubyte] }, short: { MaxValue: [32767, TY.short] },
        char: { MaxValue: [65535, TY.char], MinValue: [0, TY.char] }, uint: { MaxValue: [4294967295, TY.uint] }, ulong: { MaxValue: [18446744073709551615n, TY.ulong] },
        string: { Empty: ['', TY.string] }, String: { Empty: ['', TY.string], CASE_INSENSITIVE_ORDER: [new Fn({ native: a => { const x = a[0].toLowerCase(), y = a[1].toLowerCase(); return x < y ? -1 : x > y ? 1 : 0; } }), TY.dyn] },
        Environment: { NewLine: ['\n', TY.string], TickCount: [Date.now() & 0x7fffffff, TY.int] },
        decimal: { MaxValue: [7.922816251426434e28, TY.double] }
      };
      const tbl = C[ns];
      if (tbl && tbl[id]) return ro(tbl[id][0], tbl[id][1]);
      if (ns === 'Console' && (id === 'In' || id === 'Out')) return ro(new NS('Console'));
      if (ns === 'Comparator' || ns === 'Collections' || ns === 'Integer' || ns === 'Math' || ns === 'String' || ns === 'int' || ns === 'Character' || ns === 'Objects' || ns === 'Double' || ns === 'Long' || ns === 'Arrays' || ns === 'Console' || ns === 'char' || ns === 'string') {
        /* a method used as a value: Integer::compare or Console.WriteLine passed to ForEach */
        return ro(new Fn({ native: (args, tys) => { const r = LIB.callStatic(I, ns, id, args, tys, [], n); if (r === NONE) throw new CF.CompileError(`cannot find ${ns}.${id}`, n.line); return r[0]; }, fname: ns + '.' + id }));
      }
      return null;
    }
    if (o instanceof Arr) {
      if ((lang === 'java' && id === 'length') || (lang === 'cs' && (id === 'Length' || id === 'LongLength'))) return ro(o.rank ? o.a.length * (o.a[0] ? o.a[0].a.length : 0) : o.a.length, TY.int);
      if (lang === 'cs' && id === 'Rank') return ro(o.rank || 1, TY.int);
      return null;
    }
    if (typeof o === 'string') {
      if (lang === 'cs' && id === 'Length') return ro(o.length, TY.int);
      if (lang === 'java' && id === 'length') throw new CF.CompileError('For a String, length is a method: write s.length() with brackets. Arrays use arr.length without brackets', n.line);
      return null;
    }
    if (o && o.$lib) {
      if (o.$is && o.$is('pair')) {
        if (id === 'first' || id === 'Key' || id === 'Item1') return { ty: o.t1 || valTy(o.first), get: () => o.first, set: v => { if (o.rec) throw new CF.CompileError('The key of a map entry cannot be changed', n.line); o.a = v; } };
        if (id === 'second' || id === 'Value' || id === 'Item2') return { ty: o.t2 || valTy(o.second), get: () => o.second, set: v => { if (o.rec) o.rec.v = v; else o.b = v; } };
      }
      if (o.items && /^Item\d+$/.test(id)) { const k = +id.slice(4) - 1; return { ty: o.tys[k], get: () => o.items[k], set: v => { o.items[k] = v; } }; }
      if (o.items && o.names && o.names.includes(id)) { const k = o.names.indexOf(id); return { ty: o.tys[k], get: () => o.items[k], set: v => { o.items[k] = v; } }; }
      if (o.f && o.keys && o.keys.includes(id)) return ro(o.f[id], o.t[id]);
      if (lang === 'cs') {
        if (id === 'Count') { const c = o.a ? o.a.length : o.m ? (o.size ? o.size() : o.m.size) : o.q ? o.q.length : o.grp ? o.a.length : null; if (c !== null) return ro(c, TY.int); }
        if (id === 'Length' && o.s !== undefined) return { ty: TY.int, get: () => o.s.length, set: v => { o.s = o.s.slice(0, toNum(v)).padEnd(toNum(v), '\0'); } };
        if (id === 'Keys' && o.m) return ro(newList(I, 'KeyCollection', o.kt, o.ents(I).map(e => e.k)), T('IEnumerable', { args: [o.kt] }));
        if (id === 'Values' && o.m) return ro(newList(I, 'ValueCollection', o.vt, o.ents(I).map(e => e.v)), T('IEnumerable', { args: [o.vt] }));
        if (id === 'Key' && o.grp) return ro(o.key, o.kt);
        if (id === 'Min' && o.m && o.items) { const it = o.items(I); return ro(it[0], o.et); }
        if (id === 'Max' && o.m && o.items) { const it = o.items(I); return ro(it[it.length - 1], o.et); }
        if (id === 'Capacity' && o.a) return ro(Math.max(4, o.a.length), TY.int);
        if (id === 'First' && o.a && o.kind === 'LinkedList') return ro(o.a[0], o.et);
        if (id === 'Last' && o.a && o.kind === 'LinkedList') return ro(o.a[o.a.length - 1], o.et);
      }
      if (lang === 'java' && o.coll) return null;
    }
    if (o && o.$enum) { if (id === 'value__') return ro(o.val, TY.int); }
    if (o instanceof Obj && o.ci.exc && lang === 'cs' && id === 'Message') return ro(o.f.$msg ?? '', TY.string);
    if (typeof o === 'number' || typeof o === 'bigint' || typeof o === 'boolean') return null;
    return null;
  };
  LIB.index = function (I, o, i, ity, n, env) {
    const lang = I.lang;
    if (o && o.$lib && o.a !== undefined && !o.m) {
      const k = toNum(i);
      const len = () => o.a.length;
      if (lang === 'java') throw new CF.CompileError(`array required, but ${o.kind} found. Use list.get(${n.i.k === 'name' ? n.i.id : 'i'}) to read and list.set(i, value) to change an item`, n.line);
      const bad = () => lang === 'cs' ? I.ex('ArgumentOutOfRangeException', "Index was out of range. Must be non-negative and less than the size of the collection. (Parameter 'index')")
        : new Fatal(`v[${k}] is outside the ${o.kind} of size ${len()}. operator[] does not check, so a real program may print garbage or crash (undefined behaviour). Use v.at(${k}) to get a clear out_of_range error`, 'ub');
      if (lang === 'cpp' && (o.kind === 'stack' || o.kind === 'queue')) throw new CF.CompileError(`A ${o.kind} has no [] operator. Use ${o.kind === 'stack' ? 'top()' : 'front()'}`, n.line);
      return { ty: o.et || TY.dyn, get: () => { if (k < 0 || k >= len()) throw bad(); return o.a[k]; }, set: v => { if (k < 0 || k >= len()) throw bad(); o.a[k] = I.conv(v, o.et); } };
    }
    if (o && o.$lib && o.m && o.put) {
      if (lang === 'java') throw new CF.CompileError('Java maps use map.get(key) and map.put(key, value), not [ ]', n.line);
      return { ty: o.vt || TY.dyn, get: () => {
        const r = o.get(I, i);
        if (r) return r.v;
        if (lang === 'cs') throw I.ex('KeyNotFoundException', `The given key '${I.str(i, o.kt)}' was not present in the dictionary.`);
        const d = I.defaultVal(o.vt || TY.int); o.put(I, i, d); return d;
      }, set: v => { o.put(I, i, I.conv(v, o.vt)); } };
    }
    if (o && o.$lib && o.s !== undefined) { const k = toNum(i); return { ty: TY.char, get: () => { if (k < 0 || k >= o.s.length) throw lang === 'java' ? I.ex('StringIndexOutOfBoundsException', `index ${k},length ${o.s.length}`) : I.ex('IndexOutOfRangeException', 'Index was outside the bounds of the array.'); return o.s.charCodeAt(k); }, set: v => { o.s = o.s.slice(0, k) + chr(v) + o.s.slice(k + 1); } }; }
    if (o && o.$iter) { const k = toNum(i); return { ty: TY.dyn, get: () => { const c = o.clone(); c.move(k); return c.get(I); }, set: v => { const c = o.clone(); c.move(k); c.set(v); } }; }
    if (o && o.$lib && o.$enum) return null;
    return null;
  };

  /* ===== builtin object methods ===== */
  LIB.objMethod = function (I, o, id, args, tys, n, isSuper) {
    const lang = I.lang;
    const set = (v, ty) => { n.ty = ty; return v; };
    switch (id) {
      case 'toString': case 'ToString': return set(isSuper && !o.ci.exc ? (lang === 'java' ? o.ci.name + '@' + I.hashHex(o) : o.ci.name) : I.objStr(o), TY.string);
      case 'equals': case 'Equals': return set(isSuper ? o === args[0] : I.equals(o, args[0]), TY.bool);
      case 'hashCode': case 'GetHashCode': return set(isSuper ? I.idHash(o) : I.hashOf(o), TY.int);
      case 'getClass': case 'GetType': return set({ $lib: true, ci: o.ci, $str: () => (lang === 'java' ? 'class ' : '') + o.ci.name, $ty: () => T('Class'), getSimpleName: true }, T('Class'));
      case 'getMessage': case 'getLocalizedMessage': if (o.ci.exc) return set(o.f.$msg ?? null, TY.string); break;
      case 'what': if (o.ci.exc) return set(o.f.$msg ?? '', TY.string); break;
      case 'getCause': if (o.ci.exc) return set(o.f.$cause || null, TY.dyn); break;
      case 'printStackTrace': if (o.ci.exc) { I.write(I.objStr(o) + '\n\tat Main.main(Main.java:' + n.line + ')\n', true); return set(undefined, TY.void); } break;
      case 'getStackTrace': return set(new Arr([], TY.dyn), TY.dyn);
      case 'name': if (o.ci.isEnum) return set(o.f.$name, TY.string); break;
      case 'ordinal': if (o.ci.isEnum) return set(o.f.$ord, TY.int); break;
      case 'compareTo': if (o.ci.isEnum) return set(o.f.$ord - args[0].f.$ord, TY.int); break;
      case 'clone': { const c = new Obj(o.ci); Object.assign(c.f, o.f); return set(c, { n: o.ci.name }); }
    }
    /* record accessors: p.x() */
    if (o.ci.record && args.length === 0 && id in o.f) return set(o.f[id], I.fieldTy(o.ci, id));
    if (o.ci.exc && args.length === 0 && /^(getMessage)$/.test(id)) return set(o.f.$msg, TY.string);
    throw new CF.CompileError(lang === 'java' ? `cannot find symbol: method ${id}() in class ${o.ci.name}` : lang === 'cs' ? `'${o.ci.name}' does not contain a definition for '${id}'` : `'${o.ci.name}' has no member function '${id}'`, n.line);
  };
  LIB.classStatic = function (I, ci, id, args, tys, n) {
    if (ci.isEnum && I.lang === 'java') {
      I.clinit(ci);
      if (id === 'values') return R(new Arr(ci.d.consts.map(c => ci.sf.get(c.id).v), { n: ci.name }), { n: ci.name, dim: 1 });
      if (id === 'valueOf') { const b = ci.sf.get(args[0]); if (!b) throw I.ex('IllegalArgumentException', `No enum constant ${ci.name}.${args[0]}`); return R(b.v, { n: ci.name }); }
    }
    return NONE;
  };
  LIB.fnMethod = function (I, fn, id, args, tys, refs, n) {
    const L = I.lang;
    const wrap = f => R(new Fn({ native: f }), TY.dyn);
    switch (id) {
      case 'reversed': return wrap(a => -toNum(I.callFn(fn, a, [])));
      case 'thenComparing': case 'thenComparingInt': case 'thenComparingDouble': { const other = args[0]; const isKey = other instanceof Fn && (other.params ? other.params.length === 1 : other.native && false); return wrap(a => { const c = toNum(I.callFn(fn, a, [])); if (c) return c; if (isKey || (other.params && other.params.length === 1)) return natCmp(I, I.callFn(other, [a[0]], []), I.callFn(other, [a[1]], [])); return toNum(I.callFn(other, a, [])); }); }
      case 'negate': return wrap(a => !I.truthy(I.callFn(fn, a, [])));
      case 'and': return wrap(a => I.truthy(I.callFn(fn, a, [])) && I.truthy(I.callFn(args[0], a, [])));
      case 'or': return wrap(a => I.truthy(I.callFn(fn, a, [])) || I.truthy(I.callFn(args[0], a, [])));
      case 'andThen': return wrap(a => { const r = I.callFn(fn, a, []); return fn.params && fn.params.length && r !== undefined && args[0].params && args[0].params.length === 1 && !(n.f && false) ? I.callFn(args[0], [r], []) : (I.callFn(args[0], r === undefined ? a : [r], [])); });
      case 'compose': return wrap(a => I.callFn(fn, [I.callFn(args[0], a, [])], []));
      case 'identity': return wrap(a => a[0]);
      case 'start': case 'run': if (fn.params && fn.params.length === 0 || fn.native) { const r = I.callFn(fn, args, tys, refs, n.line); return R(r, valTy(r)); } break;
      case 'join': return R(undefined, TY.void);
      case 'DynamicInvoke': case 'Invoke': break;
      case 'equals': return R(fn === args[0], TY.bool);
    }
    const r = I.callFn(fn, args, tys, refs, n.line);
    return R(r, fn.ret || valTy(r));
  };

  /* ===== methods on values: strings, numbers, arrays and containers ===== */
  LIB.callMethod = function (I, o, id, args, tys, refs, n, recvRef, onode) {
    const lang = I.lang;
    if (typeof o === 'string') return strMethod(I, o, id, args, tys, refs, n, recvRef);
    if (typeof o === 'number' || typeof o === 'bigint' || typeof o === 'boolean') return numMethod(I, o, id, args, tys, n, onode);
    if (o instanceof Arr) return arrMethod(I, o, id, args, tys, n);
    if (o && o.kind === 'in' && o.isCin || (o && o.kind === 'out' && !o.$lib)) return streamMethod(I, o, id, args, tys, refs, n);
    if (o && o.$enum) {
      if (id === 'ToString') return R(o.name, TY.string);
      if (id === 'HasFlag') return R((o.val & args[0].val) === args[0].val, TY.bool);
      if (id === 'CompareTo') return R(o.val - args[0].val, TY.int);
      if (id === 'Equals') return R(I.equals(o, args[0]), TY.bool);
      if (id === 'GetHashCode') return R(o.val, TY.int);
    }
    if (o && o.$lib) {
      if (o.$is && o.$is('pair')) return pairMethod(I, o, id, args, tys, n);
      if (o.s !== undefined && o.$is('StringBuilder')) return sbMethod(I, o, id, args, tys, n);
      if (o.q) return pqMethod(I, o, id, args, tys, n);
      if (o.a !== undefined && !o.m && o.$is && o.$is('Stream') && (o.prim !== undefined || lang === 'java')) return streamOps(I, o, id, args, tys, n);
      if (o.a !== undefined && !o.m && o.kind) return listMethod(I, o, id, args, tys, refs, n, recvRef);
      if (o.m && o.put) return mapMethod(I, o, id, args, tys, refs, n, recvRef);
      if (o.m && o.add) return setMethod(I, o, id, args, tys, refs, n, recvRef);
      if (o.$is && o.$is('Stream')) return streamOps(I, o, id, args, tys, n);
      if (o.$is && o.$is('Optional')) return optMethod(I, o, id, args, tys, n);
      if (o.$is && o.$is('Random')) return randMethod(I, o, id, args, tys, n);
      if (o.$is && o.$is('Scanner')) return scanMethod(I, o, id, args, tys, n);
      if (o.$is && o.$is('stringstream')) return ssMethod(I, o, id, args, tys, refs, n);
      if (o.$iter) { if (id === 'hasNext') return R(o.i < o.arr().length, TY.bool); if (id === 'next') { if (o.i >= o.arr().length) throw I.ex('NoSuchElementException', null); return R(o.arr()[o.i++], o.c.et); } if (id === 'remove') { o.arr().splice(--o.i, 1); return R(undefined, TY.void); } }
      if (o.ci && o.getSimpleName) { if (id === 'getSimpleName' || id === 'getName' || id === 'Name') return R(o.ci.name, TY.string); }
      if (o.items && o.$is('tuple')) { if (id === 'ToString') return R(o.$str(I), TY.string); if (id === 'Equals') return R(o.$eq(args[0], I), TY.bool); }
      if (o.grp && lang === 'cs') return linq(I, o, id, args, tys, n);
      if (o.coll) return NONE;
      if (o.$is && o.$is('Thread') && o.run) { if (id === 'start' || id === 'run') { I.callFn(o.run, [], []); return R(undefined, TY.void); } if (id === 'join') return R(undefined, TY.void); }
      if (o.$is && o.$is('Thread')) { if (id === 'getName') return R(o.name || 'main', TY.string); }
    }
    if (o instanceof Ptr) {
      if (id === 'get') return R(o, TY.dyn);
    }
    return NONE;
  };

  function strMethod(I, s, id, args, tys, refs, n, recvRef) {
    const lang = I.lang;
    const a0 = args[0], a1 = args[1];
    const S = x => typeof x === 'string' ? x : x === null ? 'null' : (x instanceof Ptr || x instanceof Arr ? I.cstr(x) : (typeof x === 'number' && tys && tys[0] && tys[0].n === 'char') ? chr(x) : I.str(x));
    const idx = (k, len, what) => {
      if (lang === 'java') return I.ex('StringIndexOutOfBoundsException', what || `index ${k}, length ${len}`);
      if (lang === 'cs') return I.ex('ArgumentOutOfRangeException', "Index and length must refer to a location within the string. (Parameter 'length')");
      return I.ex('out_of_range', what || `basic_string::at: __n (which is ${k}) >= this->size() (which is ${len})`);
    };
    const charArg = x => typeof x === 'string' ? x : chr(x);
    if (lang === 'java') {
      switch (id) {
        case 'length': return R(s.length, TY.int);
        case 'charAt': { const k = toNum(a0); if (k < 0 || k >= s.length) throw I.ex('StringIndexOutOfBoundsException', `Index ${k} out of bounds for length ${s.length}`); return R(s.charCodeAt(k), TY.char); }
        case 'substring': { const b = toNum(a0), e = a1 === undefined ? s.length : toNum(a1); if (b < 0 || e > s.length || b > e) throw I.ex('StringIndexOutOfBoundsException', `begin ${b}, end ${e}, length ${s.length}`); return R(s.slice(b, e), TY.string); }
        case 'indexOf': return R(s.indexOf(charArg(a0), a1 !== undefined ? toNum(a1) : 0), TY.int);
        case 'lastIndexOf': return R(a1 !== undefined ? s.lastIndexOf(charArg(a0), toNum(a1)) : s.lastIndexOf(charArg(a0)), TY.int);
        case 'contains': return R(s.includes(S(a0)), TY.bool);
        case 'startsWith': return R(s.startsWith(S(a0), a1 !== undefined ? toNum(a1) : 0), TY.bool);
        case 'endsWith': return R(s.endsWith(S(a0)), TY.bool);
        case 'equals': return R(typeof a0 === 'string' && s === a0, TY.bool);
        case 'equalsIgnoreCase': return R(typeof a0 === 'string' && s.toLowerCase() === a0.toLowerCase(), TY.bool);
        case 'compareTo': { const t = S(a0); for (let i = 0; i < Math.min(s.length, t.length); i++) if (s[i] !== t[i]) return R(s.charCodeAt(i) - t.charCodeAt(i), TY.int); return R(s.length - t.length, TY.int); }
        case 'compareToIgnoreCase': { const x = s.toLowerCase(), t = S(a0).toLowerCase(); for (let i = 0; i < Math.min(x.length, t.length); i++) if (x[i] !== t[i]) return R(x.charCodeAt(i) - t.charCodeAt(i), TY.int); return R(x.length - t.length, TY.int); }
        case 'toUpperCase': return R(s.toUpperCase(), TY.string);
        case 'toLowerCase': return R(s.toLowerCase(), TY.string);
        case 'trim': return R(s.replace(/^[\x00-\x20]+|[\x00-\x20]+$/g, ''), TY.string);
        case 'strip': return R(s.trim(), TY.string);
        case 'stripLeading': return R(s.trimStart(), TY.string);
        case 'stripTrailing': return R(s.trimEnd(), TY.string);
        case 'isEmpty': return R(s.length === 0, TY.bool);
        case 'isBlank': return R(s.trim().length === 0, TY.bool);
        case 'concat': return R(s + S(a0), TY.string);
        case 'repeat': { const k = toNum(a0); if (k < 0) throw I.ex('IllegalArgumentException', 'count is negative: ' + k); return R(s.repeat(k), TY.string); }
        case 'replace': return R(s.split(charArg(a0)).join(charArg(a1)), TY.string);
        case 'replaceAll': return R(s.replace(new RegExp(javaRe(S(a0)), 'g'), S(a1).replace(/\$(\d)/g, '$$$1')), TY.string);
        case 'replaceFirst': return R(s.replace(new RegExp(javaRe(S(a0))), S(a1)), TY.string);
        case 'matches': return R(new RegExp('^(?:' + javaRe(S(a0)) + ')$').test(s), TY.bool);
        case 'split': {
          let parts = s.split(new RegExp(javaRe(S(a0))));
          if (a1 !== undefined && toNum(a1) > 0) { const lim = toNum(a1); const re = new RegExp(javaRe(S(a0)), 'g'); parts = []; let last = 0, m; while ((m = re.exec(s)) && parts.length < lim - 1) { if (m[0] === '' ) { re.lastIndex++; continue; } parts.push(s.slice(last, m.index)); last = m.index + m[0].length; } parts.push(s.slice(last)); }
          else { while (parts.length > 1 && parts[parts.length - 1] === '') parts.pop(); if (s === '') parts = ['']; if (parts.length > 1 && parts[0] === '' && S(a0) === '') parts.shift(); }
          return R(new Arr(parts, TY.string), T('string', { dim: 1 }));
        }
        case 'toCharArray': return R(new Arr(Array.from(s, c => c.charCodeAt(0)), TY.char), T('char', { dim: 1 }));
        case 'chars': return R(seq(Array.from(s, c => c.charCodeAt(0)), TY.int, 'Int'), T('IntStream'));
        case 'hashCode': return R(CF.strHash(s), TY.int);
        case 'intern': return R(s, TY.string);
        case 'toString': return R(s, TY.string);
        case 'format': case 'formatted': return R(CF.printf(I, s, args, tys, 'java'), TY.string);
        case 'codePointAt': return R(s.codePointAt(toNum(a0)), TY.int);
        case 'lines': return R(seq(s.split(/\r?\n/), TY.string), T('Stream'));
        case 'indent': return R(s.split('\n').map(l => ' '.repeat(toNum(a0)) + l).join('\n') + '\n', TY.string);
      }
      return NONE;
    }
    if (lang === 'cs') {
      const ignoreCase = args.some(x => x && x.$enum && /IgnoreCase/.test(x.name));
      switch (id) {
        case 'Substring': { const b = toNum(a0), len = a1 === undefined ? s.length - b : toNum(a1); if (b < 0 || b > s.length || len < 0 || b + len > s.length) throw I.ex('ArgumentOutOfRangeException', a1 === undefined ? "startIndex cannot be larger than length of string. (Parameter 'startIndex')" : "Index and length must refer to a location within the string. (Parameter 'length')"); return R(s.substr(b, len), TY.string); }
        case 'IndexOf': return R(ignoreCase ? s.toLowerCase().indexOf(charArg(a0).toLowerCase()) : s.indexOf(charArg(a0), a1 !== undefined && !a1.$enum ? toNum(a1) : 0), TY.int);
        case 'LastIndexOf': return R(s.lastIndexOf(charArg(a0)), TY.int);
        case 'Contains': return R(ignoreCase ? s.toLowerCase().includes(charArg(a0).toLowerCase()) : s.includes(charArg(a0)), TY.bool);
        case 'StartsWith': return R(ignoreCase ? s.toLowerCase().startsWith(charArg(a0).toLowerCase()) : s.startsWith(charArg(a0)), TY.bool);
        case 'EndsWith': return R(ignoreCase ? s.toLowerCase().endsWith(charArg(a0).toLowerCase()) : s.endsWith(charArg(a0)), TY.bool);
        case 'ToUpper': case 'ToUpperInvariant': return R(s.toUpperCase(), TY.string);
        case 'ToLower': case 'ToLowerInvariant': return R(s.toLowerCase(), TY.string);
        case 'Trim': return R(args.length ? trimChars(s, args.map(charArg), 3) : s.trim(), TY.string);
        case 'TrimStart': return R(args.length ? trimChars(s, args.map(charArg), 1) : s.trimStart(), TY.string);
        case 'TrimEnd': return R(args.length ? trimChars(s, args.map(charArg), 2) : s.trimEnd(), TY.string);
        case 'Replace': return R(s.split(charArg(a0)).join(charArg(a1)), TY.string);
        case 'Split': {
          let seps = args.filter(x => typeof x === 'string' || typeof x === 'number' || x instanceof Arr).flatMap(x => x instanceof Arr ? x.a.map(charArg) : [charArg(x)]);
          const opts = args.find(x => x && x.$enum);
          if (!seps.length) seps = [' '];
          let parts = s.split(new RegExp(seps.map(x => x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')));
          if (opts && /RemoveEmptyEntries/.test(opts.name)) parts = parts.filter(Boolean);
          if (opts && /TrimEntries/.test(opts.name)) parts = parts.map(x => x.trim());
          return R(new Arr(parts, TY.string), T('string', { dim: 1 }));
        }
        case 'ToCharArray': return R(new Arr(Array.from(s, c => c.charCodeAt(0)), TY.char), T('char', { dim: 1 }));
        case 'Equals': return R(ignoreCase ? typeof a0 === 'string' && s.toLowerCase() === a0.toLowerCase() : s === a0, TY.bool);
        case 'CompareTo': return R(Math.sign(natCmp(I, s, a0)), TY.int);
        case 'PadLeft': return R(s.padStart(toNum(a0), a1 !== undefined ? charArg(a1) : ' '), TY.string);
        case 'PadRight': return R(s.padEnd(toNum(a0), a1 !== undefined ? charArg(a1) : ' '), TY.string);
        case 'Insert': return R(s.slice(0, toNum(a0)) + S(a1) + s.slice(toNum(a0)), TY.string);
        case 'Remove': return R(a1 === undefined ? s.slice(0, toNum(a0)) : s.slice(0, toNum(a0)) + s.slice(toNum(a0) + toNum(a1)), TY.string);
        case 'ToString': return R(s, TY.string);
        case 'GetHashCode': return R(CF.strHash(s), TY.int);
        case 'Count': if (!args.length) return R(s.length, TY.int); break;
        case 'IsNormalized': return R(true, TY.bool);
      }
      return linq(I, seq(Array.from(s, c => c.charCodeAt(0)), TY.char), id, args, tys, n);
    }
    /* C++ std::string */
    const setS = v => { if (!recvRef) throw new CF.CompileError(`This string cannot be changed here`, n.line); recvRef.set(v); };
    switch (id) {
      case 'length': case 'size': return R(BigInt(s.length), TY.ulong);
      case 'empty': return R(s.length === 0, TY.bool);
      case 'at': { const k = toNum(a0); if (k < 0 || k >= s.length) throw idx(k, s.length); return R(s.charCodeAt(k), TY.char); }
      case 'substr': { const b = toNum(a0); if (b > s.length) throw I.ex('out_of_range', `basic_string::substr: __pos (which is ${b}) > this->size() (which is ${s.length})`); return R(a1 === undefined ? s.slice(b) : s.substr(b, toNum(a1)), TY.string); }
      case 'find': case 'rfind': { const t = typeof a0 === 'number' ? chr(a0) : S(a0); const k = id === 'find' ? s.indexOf(t, a1 !== undefined ? toNum(a1) : 0) : (a1 !== undefined ? s.lastIndexOf(t, toNum(a1)) : s.lastIndexOf(t)); return R(k < 0 ? 18446744073709551615n : BigInt(k), TY.ulong); }
      case 'find_first_of': { const set = S(a0); for (let i = a1 !== undefined ? toNum(a1) : 0; i < s.length; i++) if (set.includes(s[i])) return R(BigInt(i), TY.ulong); return R(18446744073709551615n, TY.ulong); }
      case 'find_last_of': { const set = S(a0); for (let i = s.length - 1; i >= 0; i--) if (set.includes(s[i])) return R(BigInt(i), TY.ulong); return R(18446744073709551615n, TY.ulong); }
      case 'find_first_not_of': { const set = S(a0); for (let i = 0; i < s.length; i++) if (!set.includes(s[i])) return R(BigInt(i), TY.ulong); return R(18446744073709551615n, TY.ulong); }
      case 'find_last_not_of': { const set = S(a0); for (let i = s.length - 1; i >= 0; i--) if (!set.includes(s[i])) return R(BigInt(i), TY.ulong); return R(18446744073709551615n, TY.ulong); }
      case 'c_str': case 'data': return R(new Ptr(I.cchars(s), 0, null, TY.char), T('char', { ptr: 1 }));
      case 'compare': { const t = S(a0); return R(s < t ? -1 : s > t ? 1 : 0, TY.int); }
      case 'push_back': setS(s + chr(a0)); return R(undefined, TY.void);
      case 'pop_back': if (!s.length) throw new Fatal('pop_back on an empty string is undefined behaviour'); setS(s.slice(0, -1)); return R(undefined, TY.void);
      case 'append': setS(s + (typeof a0 === 'number' && a1 !== undefined ? chr(a1).repeat(toNum(a0)) : S(a0))); return R(s, TY.string);
      case 'insert': setS(s.slice(0, toNum(a0)) + (a1 === undefined ? '' : typeof a1 === 'number' ? chr(args[2] !== undefined ? args[2] : a1).repeat(args[2] !== undefined ? toNum(a1) : 1) : S(a1)) + s.slice(toNum(a0))); return R(recvRef.get(), TY.string);
      case 'erase': { if (a0 && a0.$iter) { const k = a0.i; setS(s.slice(0, k) + s.slice(a1 && a1.$iter ? a1.i : k + 1)); return R(iter(a0.c, k, { str: true, ref: recvRef }), TY.dyn); } const b = a0 === undefined ? 0 : toNum(a0); setS(a1 === undefined ? s.slice(0, b) : s.slice(0, b) + s.slice(b + toNum(a1))); return R(recvRef.get(), TY.string); }
      case 'replace': { const b = toNum(a0), len = toNum(a1); setS(s.slice(0, b) + S(args[2]) + s.slice(b + len)); return R(recvRef.get(), TY.string); }
      case 'clear': setS(''); return R(undefined, TY.void);
      case 'front': return R(s.charCodeAt(0), TY.char);
      case 'back': return R(s.charCodeAt(s.length - 1), TY.char);
      case 'begin': return R(iter({ a: null }, 0, { str: true, ref: recvRef || { get: () => s, set: () => {} } }), TY.dyn);
      case 'end': return R(iter({ a: null }, s.length, { str: true, ref: recvRef || { get: () => s, set: () => {} } }), TY.dyn);
      case 'rbegin': case 'rend': { const chars = Array.from(s, c => c.charCodeAt(0)); const c = { a: chars, et: TY.char }; return R(iter(c, id === 'rbegin' ? 0 : chars.length, { rev: true }), TY.dyn); }
      case 'resize': { const k = toNum(a0); setS(s.length >= k ? s.slice(0, k) : s + (a1 !== undefined ? chr(a1) : '\0').repeat(k - s.length)); return R(undefined, TY.void); }
      case 'swap': { const other = refs[0]; const t = other.get(); other.set(s); setS(t); return R(undefined, TY.void); }
      case 'starts_with': return R(s.startsWith(S(a0)), TY.bool);
      case 'ends_with': return R(s.endsWith(S(a0)), TY.bool);
      case 'contains': return R(s.includes(S(a0)), TY.bool);
      case 'reserve': case 'shrink_to_fit': return R(undefined, TY.void);
      case 'capacity': return R(BigInt(Math.max(15, s.length)), TY.ulong);
    }
    return NONE;
  }
  function trimChars(s, cs, mode) { let a = 0, b = s.length; if (mode & 1) while (a < b && cs.includes(s[a])) a++; if (mode & 2) while (b > a && cs.includes(s[b - 1])) b--; return s.slice(a, b); }
  function javaRe(p) { return p.replace(/\\p\{Alpha\}/g, '[A-Za-z]').replace(/\\p\{Punct\}/g, '[!-\\/:-@\\[-`{-~]').replace(/\\p\{Upper\}/g, '[A-Z]').replace(/\\p\{Lower\}/g, '[a-z]').replace(/\(\?<([a-zA-Z]\w*)>/g, '(?<$1>'); }

  function numMethod(I, v, id, args, tys, n, onode) {
    const lang = I.lang;
    const ty = onode && onode.ty;
    switch (id) {
      case 'ToString': if (args.length && typeof args[0] === 'string') return R(CF.csFormat(I, v, ty, args[0]), TY.string); return R(I.str(v, ty), TY.string);
      case 'toString': return R(I.str(v, ty), TY.string);
      case 'equals': case 'Equals': return R(v == args[0] && (lang !== 'java' || kindOf(ty, v) === kindOf(tys[0], args[0])), TY.bool);
      case 'compareTo': case 'CompareTo': return R(v < args[0] ? -1 : v > args[0] ? 1 : 0, TY.int);
      case 'hashCode': case 'GetHashCode': return R(I.hashOf(v), TY.int);
      case 'intValue': return R(i32(v), TY.int);
      case 'longValue': return R(toBig(v), TY.long);
      case 'doubleValue': return R(toNum(v), TY.double);
      case 'charValue': return R(v, TY.char);
      case 'booleanValue': return R(v, TY.bool);
      case 'isNaN': return R(Number.isNaN(v), TY.bool);
      case 'GetType': return R({ $lib: true, $str: () => 'System.' + ({ int: 'Int32', double: 'Double', long: 'Int64', bool: 'Boolean', char: 'Char' }[(ty || valTy(v)).n] || 'Object'), $ty: () => T('Type') }, TY.dyn);
    }
    if (lang === 'java' && ty && NK[ty.n] && !ty.box) throw new CF.CompileError(`${ty.n} cannot be dereferenced. A primitive like ${ty.n} has no methods. Use Integer.toString(x) or wrap it as Integer`, n.line);
    return NONE;
  }
  function arrMethod(I, a, id, args, tys, n) {
    const lang = I.lang;
    if (lang === 'java') {
      if (id === 'clone') return R(new Arr(a.a.slice(), a.et), Object.assign({}, a.et, { dim: (a.et.dim || 0) + 1 }));
      if (id === 'length') throw new CF.CompileError('For an array, length is a field: write arr.length without brackets', n.line);
      if (id === 'equals') return R(a === args[0], TY.bool);
      if (id === 'getClass') return R({ $lib: true, $str: () => 'class [I', $ty: () => T('Class') }, TY.dyn);
      if (id === 'hashCode') return R(I.idHash(a), TY.int);
      return NONE;
    }
    if (lang === 'cs') {
      if (id === 'GetLength') return R(toNum(args[0]) === 0 ? a.a.length : (a.a[0] ? a.a[0].a.length : 0), TY.int);
      if (id === 'Clone') return R(new Arr(a.a.slice(), a.et), TY.dyn);
      if (id === 'CopyTo') { for (let i = 0; i < a.a.length; i++) args[0].a[toNum(args[1]) + i] = a.a[i]; return R(undefined, TY.void); }
      if (id === 'GetUpperBound') return R((toNum(args[0]) === 0 ? a.a.length : a.a[0].a.length) - 1, TY.int);
      return linq(I, seq(a.a, a.et), id, args, tys, n, a);
    }
    if (lang === 'cpp' && a.std) return listMethod(I, Object.assign(Object.create(ListP), { a: a.a, et: a.et, kind: 'array' }), id, args, tys, [], n);
    return NONE;
  }
  function streamMethod(I, s, id, args, tys, refs, n) {
    switch (id) {
      case 'get': { const c = Input.char(I); if (refs[0]) { if (c < 0) { s.fail = true; return R(s, TY.dyn); } refs[0].set(c); return R(s, TY.dyn); } return R(c, TY.int); }
      case 'ignore': { const cnt = args.length ? Math.min(toNum(args[0]), 1e9) : 1; const delim = args[1] !== undefined ? chr(args[1]) : null; for (let i = 0; i < cnt && I.inPos < I.stdin.length; i++) { const c = I.stdin[I.inPos++]; if (c === delim) break; } return R(s, TY.dyn); }
      case 'peek': return R(I.inPos < I.stdin.length ? I.stdin.charCodeAt(I.inPos) : -1, TY.int);
      case 'fail': return R(!!s.fail, TY.bool);
      case 'good': return R(!s.fail, TY.bool);
      case 'eof': return R(I.inPos >= I.stdin.length, TY.bool);
      case 'clear': s.fail = false; return R(undefined, TY.void);
      case 'precision': if (args.length) s.prec = toNum(args[0]); return R(BigInt(s.prec), TY.long);
      case 'setf': case 'unsetf': {
        const on = id === 'setf';
        for (const a of args) if (a && a.manip) { if (a.manip === 'fixed') s.fixed = on; else if (a.manip === 'scientific') s.sci = on; else if (a.manip === 'showpoint') s.showpoint = on; else if (a.manip === 'boolalpha') s.alpha = on; else if (a.manip === 'left') s.left = on; else if (a.manip === 'showpos') s.showpos = on; else if (a.manip === 'uppercase') s.upper = on; }
        return R(s, TY.dyn);
      }
      case 'tie': case 'sync_with_stdio': case 'flush': return R(s, TY.dyn);
      case 'width': s.width = toNum(args[0] || 0); return R(0n, TY.long);
      case 'put': I.write(chr(args[0]), s.err); return R(s, TY.dyn);
    }
    return NONE;
  }
  function ssMethod(I, s, id, args, tys, refs, n) {
    switch (id) {
      case 'str': if (args.length) { s.buf = I.cstr(args[0]); s.pos = 0; s.fail = false; return R(undefined, TY.void); } return R(s.buf, TY.string);
      case 'clear': s.fail = false; return R(undefined, TY.void);
      case 'eof': return R(s.pos >= s.buf.length, TY.bool);
      case 'fail': return R(!!s.fail, TY.bool);
      case 'good': return R(!s.fail, TY.bool);
      case 'precision': if (args.length) s.prec = toNum(args[0]); return R(BigInt(s.prec), TY.long);
    }
    return NONE;
  }
  function pairMethod(I, p, id, args, tys, n) {
    switch (id) {
      case 'getKey': return R(p.first, p.t1);
      case 'getValue': return R(p.second, p.t2);
      case 'setValue': { const old = p.second; if (p.rec) p.rec.v = args[0]; else p.b = args[0]; return R(old, p.t2); }
      case 'toString': case 'ToString': return R(p.$str(I), TY.string);
      case 'equals': case 'Equals': return R(p.$eq(args[0], I), TY.bool);
      case 'hashCode': return R(I.hashOf(p.first) ^ I.hashOf(p.second), TY.int);
      case 'swap': { const o = args[0]; const t = [p.a, p.b]; p.a = o.a; p.b = o.b; o.a = t[0]; o.b = t[1]; return R(undefined, TY.void); }
      case 'Deconstruct': return R(undefined, TY.void);
    }
    return NONE;
  }
  function sbMethod(I, o, id, args, tys, n) {
    const lang = I.lang;
    const S = (x, t) => x instanceof Arr && x.et && x.et.n === 'char' ? x.a.map(chr).join('') : I.str(x, t);
    const self = R(o, T('StringBuilder'));
    const chk = (k, max) => { if (k < 0 || k > max) throw lang === 'java' ? I.ex('StringIndexOutOfBoundsException', `index ${k},length ${o.s.length}`) : I.ex('ArgumentOutOfRangeException', 'Index was out of range. Must be non-negative and less than the size of the collection.'); };
    switch (id) {
      case 'append': case 'Append': o.s += args.length === 3 && lang === 'java' ? S(args[0]).slice(toNum(args[1]), toNum(args[2])) : (args.length === 2 && lang === 'cs' && typeof args[1] === 'number' ? chr(args[0]).repeat(toNum(args[1])) : S(args[0], tys[0])); return self;
      case 'AppendLine': o.s += (args.length ? S(args[0], tys[0]) : '') + '\n'; return self;
      case 'AppendFormat': o.s += CF.csComposite(I, I.str(args[0]), args.slice(1), tys.slice(1)); return self;
      case 'insert': case 'Insert': { const k = toNum(args[0]); chk(k, o.s.length); o.s = o.s.slice(0, k) + S(args[1], tys[1]) + o.s.slice(k); return self; }
      case 'reverse': o.s = Array.from(o.s).reverse().join(''); return self;
      case 'toString': case 'ToString': return R(o.s, TY.string);
      case 'length': return R(o.s.length, TY.int);
      case 'charAt': { const k = toNum(args[0]); if (k < 0 || k >= o.s.length) throw I.ex('StringIndexOutOfBoundsException', `index ${k},length ${o.s.length}`); return R(o.s.charCodeAt(k), TY.char); }
      case 'setCharAt': { const k = toNum(args[0]); chk(k, o.s.length - 1); o.s = o.s.slice(0, k) + chr(args[1]) + o.s.slice(k + 1); return R(undefined, TY.void); }
      case 'deleteCharAt': { const k = toNum(args[0]); if (k < 0 || k >= o.s.length) throw I.ex('StringIndexOutOfBoundsException', `index ${k},length ${o.s.length}`); o.s = o.s.slice(0, k) + o.s.slice(k + 1); return self; }
      case 'delete': { const a = toNum(args[0]), b = Math.min(toNum(args[1]), o.s.length); o.s = o.s.slice(0, a) + o.s.slice(b); return self; }
      case 'Remove': { const a = toNum(args[0]), len = toNum(args[1]); if (a < 0 || a + len > o.s.length) throw I.ex('ArgumentOutOfRangeException', 'Index was out of range.'); o.s = o.s.slice(0, a) + o.s.slice(a + len); return self; }
      case 'replace': { const a = toNum(args[0]), b = Math.min(toNum(args[1]), o.s.length); o.s = o.s.slice(0, a) + S(args[2]) + o.s.slice(b); return self; }
      case 'Replace': o.s = o.s.split(typeof args[0] === 'string' ? args[0] : chr(args[0])).join(typeof args[1] === 'string' ? args[1] : chr(args[1])); return self;
      case 'indexOf': return R(o.s.indexOf(S(args[0])), TY.int);
      case 'lastIndexOf': return R(o.s.lastIndexOf(S(args[0])), TY.int);
      case 'setLength': { const k = toNum(args[0]); o.s = o.s.length >= k ? o.s.slice(0, k) : o.s + '\0'.repeat(k - o.s.length); return R(undefined, TY.void); }
      case 'isEmpty': return R(o.s.length === 0, TY.bool);
      case 'Clear': o.s = ''; return self;
      case 'substring': return R(o.s.slice(toNum(args[0]), args[1] === undefined ? undefined : toNum(args[1])), TY.string);
      case 'capacity': return R(Math.max(16, o.s.length), TY.int);
      case 'equals': case 'Equals': return R(o === args[0], TY.bool);
      case 'chars': return R(seq(Array.from(o.s, c => c.charCodeAt(0)), TY.int, 'Int'), T('IntStream'));
      case 'compareTo': return R(o.s < args[0].s ? -1 : o.s > args[0].s ? 1 : 0, TY.int);
    }
    return NONE;
  }
  function pqMethod(I, q, id, args, tys, n) {
    const lang = I.lang;
    const et = q.et;
    switch (id) {
      case 'add': case 'offer': if (args[0] === null) throw I.ex('NullPointerException', null); q.push(I, I.conv(args[0], et)); return R(true, TY.bool);
      case 'addAll': collItems(I, args[0]).forEach(x => q.push(I, I.conv(x, et))); return R(true, TY.bool);
      case 'push': case 'emplace': q.push(I, I.conv(args[0], et)); return R(undefined, TY.void);
      case 'Enqueue': q.push(I, args[0], args[1]); return R(undefined, TY.void);
      case 'poll': { const r = q.pop(I); return R(r === undefined ? null : r, et); }
      case 'remove': if (!args.length) { if (!q.q.length) throw I.ex('NoSuchElementException', null); return R(q.pop(I), et); } { const i = q.q.findIndex(x => I.equals(x, args[0]) || x === args[0]); if (i < 0) return R(false, TY.bool); const rest = q.q.filter((x, k) => k !== i); q.q = []; rest.forEach(x => q.push(I, x)); return R(true, TY.bool); }
      case 'pop': if (!q.q.length) throw new Fatal('pop() on an empty priority_queue is undefined behaviour. Check empty() first'); q.pop(I); return R(undefined, TY.void);
      case 'Dequeue': { if (!q.q.length) throw I.ex('InvalidOperationException', 'Queue empty.'); const r = q.pop(I); return R(r.e, et); }
      case 'TryDequeue': { if (!q.q.length) return R(false, TY.bool); const r = q.pop(I); refs0(n, 0, r.e); return R(true, TY.bool); }
      case 'peek': return R(q.q.length ? q.q[0] : null, et);
      case 'element': if (!q.q.length) throw I.ex('NoSuchElementException', null); return R(q.q[0], et);
      case 'top': if (!q.q.length) throw new Fatal('top() on an empty priority_queue is undefined behaviour. Check empty() first'); return R(q.q[0], et);
      case 'Peek': if (!q.q.length) throw I.ex('InvalidOperationException', 'Queue empty.'); return R(q.q[0].e, et);
      case 'size': return R(lang === 'cpp' ? BigInt(q.q.length) : q.q.length, lang === 'cpp' ? TY.ulong : TY.int);
      case 'isEmpty': return R(q.q.length === 0, TY.bool);
      case 'empty': return R(q.q.length === 0, TY.bool);
      case 'clear': case 'Clear': q.q = []; return R(undefined, TY.void);
      case 'contains': return R(q.q.some(x => I.equals(x, args[0]) || x === args[0]), TY.bool);
      case 'toString': return R(q.$str(I), TY.string);
      case 'stream': return R(seq(q.q.slice(), et), T('Stream'));
      case 'iterator': return R(iter({ a: q.q.slice(), et }, 0, { jitter: true }), TY.dyn);
      case 'toArray': return R(new Arr(q.q.slice(), et), TY.dyn);
      case 'forEach': q.q.slice().forEach(x => I.callFn(args[0], [x], [et])); return R(undefined, TY.void);
    }
    return NONE;
  }
  function refs0() {}
  function listMethod(I, l, id, args, tys, refs, n, recvRef) {
    const lang = I.lang, kind = l.kind, a = l.a, et = l.et;
    const a0 = args[0], a1 = args[1];
    const C = v => I.conv(v, et);
    const isStackJ = kind === 'Stack', isDeque = kind === 'ArrayDeque' || kind === 'LinkedList';
    const immut = () => { if (l.immutable || l.fixed) throw I.ex('UnsupportedOperationException', null); };
    const outJ = k => I.ex('IndexOutOfBoundsException', `Index ${k} out of bounds for length ${a.length}`);
    const outCs = () => I.ex('ArgumentOutOfRangeException', "Index was out of range. Must be non-negative and less than the size of the collection. (Parameter 'index')");
    const eqIdx = v => a.findIndex(x => I.equals(x, v) || (x === v));
    if (lang === 'java') {
      switch (id) {
        case 'add': case 'addLast': case 'offer': case 'offerLast':
          if (l.immutable || l.fixed) throw I.ex('UnsupportedOperationException', null);
          if (args.length === 2) { const k = toNum(a0); if (k < 0 || k > a.length) throw outJ(k); a.splice(k, 0, C(a1)); return R(undefined, TY.void); }
          if (kind === 'ArrayDeque' && a0 === null) throw I.ex('NullPointerException', null);
          a.push(C(a0)); return R(true, TY.bool);
        case 'addFirst': case 'offerFirst': a.unshift(C(a0)); return R(undefined, TY.void);
        case 'push': if (isStackJ) { a.push(C(a0)); return R(a0, et); } a.unshift(C(a0)); return R(undefined, TY.void);
        case 'pop': if (isStackJ) { if (!a.length) throw I.ex('EmptyStackException', null); return R(a.pop(), et); } if (!a.length) throw I.ex('NoSuchElementException', null); return R(a.shift(), et);
        case 'peek': if (isStackJ) { if (!a.length) throw I.ex('EmptyStackException', null); return R(a[a.length - 1], et); } return R(a.length ? a[0] : null, et);
        case 'peekFirst': return R(a.length ? a[0] : null, et);
        case 'peekLast': return R(a.length ? a[a.length - 1] : null, et);
        case 'element': case 'getFirst': case 'firstElement': if (!a.length) throw I.ex('NoSuchElementException', null); return R(a[0], et);
        case 'getLast': case 'lastElement': if (!a.length) throw I.ex('NoSuchElementException', null); return R(a[a.length - 1], et);
        case 'poll': case 'pollFirst': return R(a.length ? a.shift() : null, et);
        case 'pollLast': return R(a.length ? a.pop() : null, et);
        case 'removeFirst': if (!a.length) throw I.ex('NoSuchElementException', null); return R(a.shift(), et);
        case 'removeLast': if (!a.length) throw I.ex('NoSuchElementException', null); return R(a.pop(), et);
        case 'empty': return R(a.length === 0, TY.bool);
        case 'search': { const i = a.lastIndexOf(a0); const k = a.map((x, j) => I.equals(x, a0) || x === a0 ? j : -1).filter(j => j >= 0).pop(); return R(k === undefined ? -1 : a.length - k, TY.int); }
        case 'get': { const k = toNum(a0); if (k < 0 || k >= a.length) throw outJ(k); return R(a[k], et); }
        case 'set': { if (l.immutable) throw I.ex('UnsupportedOperationException', null); const k = toNum(a0); if (k < 0 || k >= a.length) throw outJ(k); const old = a[k]; a[k] = C(a1); return R(old, et); }
        case 'remove': {
          immut();
          if (!args.length) { if (!a.length) throw I.ex('NoSuchElementException', null); return R(a.shift(), et); }
          const t = tys[0];
          if (t && NK[t.n] === 'i' && !t.box && !(et && et.n === 'char' && t.n === 'char')) { const k = toNum(a0); if (k < 0 || k >= a.length) throw outJ(k); return R(a.splice(k, 1)[0], et); }
          const k = eqIdx(a0); if (k >= 0) { a.splice(k, 1); return R(true, TY.bool); } return R(false, TY.bool);
        }
        case 'removeIf': { immut(); const before = a.length; const keep = a.filter(x => !I.truthy(I.callFn(a0, [x], [et]))); a.splice(0, a.length, ...keep); return R(keep.length !== before, TY.bool); }
        case 'removeAll': { const other = collItems(I, a0); const keep = a.filter(x => !other.some(y => I.equals(x, y) || x === y)); const ch = keep.length !== a.length; a.splice(0, a.length, ...keep); return R(ch, TY.bool); }
        case 'retainAll': { const other = collItems(I, a0); const keep = a.filter(x => other.some(y => I.equals(x, y) || x === y)); const ch = keep.length !== a.length; a.splice(0, a.length, ...keep); return R(ch, TY.bool); }
        case 'size': return R(a.length, TY.int);
        case 'isEmpty': return R(a.length === 0, TY.bool);
        case 'contains': return R(eqIdx(a0) >= 0, TY.bool);
        case 'containsAll': return R(collItems(I, a0).every(y => a.some(x => I.equals(x, y) || x === y)), TY.bool);
        case 'indexOf': return R(eqIdx(a0), TY.int);
        case 'lastIndexOf': { for (let i = a.length - 1; i >= 0; i--) if (I.equals(a[i], a0) || a[i] === a0) return R(i, TY.int); return R(-1, TY.int); }
        case 'clear': immut(); a.length = 0; return R(undefined, TY.void);
        case 'addAll': immut(); if (args.length === 2) { a.splice(toNum(a0), 0, ...collItems(I, a1)); return R(true, TY.bool); } a.push(...collItems(I, a0)); return R(true, TY.bool);
        case 'sort': if (l.immutable) throw I.ex('UnsupportedOperationException', null); sortArr(I, a, cmpFrom(I, a0)); return R(undefined, TY.void);
        case 'forEach': a.slice().forEach(x => I.callFn(a0, [x], [et])); return R(undefined, TY.void);
        case 'replaceAll': for (let i = 0; i < a.length; i++) a[i] = C(I.callFn(a0, [a[i]], [et])); return R(undefined, TY.void);
        case 'stream': return R(seq(a.slice(), et), T('Stream', { args: [et] }));
        case 'iterator': case 'listIterator': return R(iter(l, 0), T('Iterator'));
        case 'descendingIterator': return R(iter({ a: a.slice().reverse(), et }, 0), T('Iterator'));
        case 'subList': { const b = toNum(a0), e = toNum(a1); if (b < 0 || e > a.length || b > e) throw I.ex('IndexOutOfBoundsException', `fromIndex: ${b}, toIndex: ${e}, size: ${a.length}`); return R(newList(I, 'ArrayList', et, a.slice(b, e)), l.$ty()); }
        case 'toArray': return R(new Arr(a.slice(), et), Object.assign({}, et || TY.dyn, { dim: 1 }));
        case 'reversed': return R(newList(I, 'ArrayList', et, a.slice().reverse()), l.$ty());
        case 'toString': return R(l.$str(I), TY.string);
        case 'equals': return R(l.$eq(a0, I), TY.bool);
        case 'hashCode': return R(l.$hash(I), TY.int);
        case 'getClass': return R({ $lib: true, $str: () => 'class java.util.' + kind, $ty: () => T('Class'), ci: { name: kind }, getSimpleName: true }, TY.dyn);
        case 'ensureCapacity': case 'trimToSize': return R(undefined, TY.void);
      }
      return NONE;
    }
    if (lang === 'cs') {
      switch (id) {
        case 'Add': case 'Enqueue': case 'AddLast': a.push(C(a0)); return R(undefined, TY.void);
        case 'AddFirst': a.unshift(C(a0)); return R(undefined, TY.void);
        case 'Push': a.push(C(a0)); return R(undefined, TY.void);
        case 'Pop': if (!a.length) throw I.ex('InvalidOperationException', 'Stack empty.'); return R(a.pop(), et);
        case 'Dequeue': if (!a.length) throw I.ex('InvalidOperationException', 'Queue empty.'); return R(a.shift(), et);
        case 'Peek': if (!a.length) throw I.ex('InvalidOperationException', kind === 'StackCS' ? 'Stack empty.' : 'Queue empty.'); return R(kind === 'StackCS' ? a[a.length - 1] : a[0], et);
        case 'TryPop': case 'TryDequeue': case 'TryPeek': { if (!a.length) { if (refs[0]) refs[0].set(I.defaultVal(et)); return R(false, TY.bool); } const v = id === 'TryPop' ? a.pop() : id === 'TryDequeue' ? a.shift() : (kind === 'StackCS' ? a[a.length - 1] : a[0]); if (refs[0]) refs[0].set(v); return R(true, TY.bool); }
        case 'RemoveFirst': a.shift(); return R(undefined, TY.void);
        case 'RemoveLast': a.pop(); return R(undefined, TY.void);
        case 'AddRange': a.push(...collItems(I, a0)); return R(undefined, TY.void);
        case 'Insert': { const k = toNum(a0); if (k < 0 || k > a.length) throw outCs(); a.splice(k, 0, C(a1)); return R(undefined, TY.void); }
        case 'InsertRange': a.splice(toNum(a0), 0, ...collItems(I, a1)); return R(undefined, TY.void);
        case 'Remove': { const k = eqIdx(a0); if (k >= 0) { a.splice(k, 1); return R(true, TY.bool); } return R(false, TY.bool); }
        case 'RemoveAt': { const k = toNum(a0); if (k < 0 || k >= a.length) throw outCs(); a.splice(k, 1); return R(undefined, TY.void); }
        case 'RemoveRange': a.splice(toNum(a0), toNum(a1)); return R(undefined, TY.void);
        case 'RemoveAll': { const before = a.length; const keep = a.filter(x => !I.truthy(I.callFn(a0, [x], [et]))); a.splice(0, a.length, ...keep); return R(before - keep.length, TY.int); }
        case 'Clear': a.length = 0; return R(undefined, TY.void);
        case 'Contains': return R(eqIdx(a0) >= 0, TY.bool);
        case 'IndexOf': return R(eqIdx(a0), TY.int);
        case 'LastIndexOf': { for (let i = a.length - 1; i >= 0; i--) if (I.equals(a[i], a0) || a[i] === a0) return R(i, TY.int); return R(-1, TY.int); }
        case 'Sort': sortArr(I, a, cmpFrom(I, a0)); return R(undefined, TY.void);
        case 'Reverse': if (!args.length) { a.reverse(); return R(undefined, TY.void); } break;
        case 'ForEach': a.slice().forEach(x => I.callFn(a0, [x], [et])); return R(undefined, TY.void);
        case 'Find': { const r = a.find(x => I.truthy(I.callFn(a0, [x], [et]))); return R(r === undefined ? I.defaultVal(et) : r, et); }
        case 'FindIndex': return R(a.findIndex(x => I.truthy(I.callFn(a0, [x], [et]))), TY.int);
        case 'FindLast': { const r = a.slice().reverse().find(x => I.truthy(I.callFn(a0, [x], [et]))); return R(r === undefined ? I.defaultVal(et) : r, et); }
        case 'FindAll': return R(newList(I, 'List', et, a.filter(x => I.truthy(I.callFn(a0, [x], [et])))), l.$ty());
        case 'Exists': return R(a.some(x => I.truthy(I.callFn(a0, [x], [et]))), TY.bool);
        case 'TrueForAll': return R(a.every(x => I.truthy(I.callFn(a0, [x], [et]))), TY.bool);
        case 'GetRange': return R(newList(I, 'List', et, a.slice(toNum(a0), toNum(a0) + toNum(a1))), l.$ty());
        case 'ConvertAll': return R(newList(I, 'List', null, a.map(x => I.callFn(a0, [x], [et]))), T('List'));
        case 'BinarySearch': return arraysFn(I, 'binarySearch', [{ a }, a0], tys, n);
        case 'CopyTo': a.forEach((x, i) => { a0.a[i] = x; }); return R(undefined, TY.void);
        case 'ToString': return R(l.$str(I), TY.string);
        case 'Equals': return R(l === a0, TY.bool);
        case 'TrimExcess': case 'EnsureCapacity': return R(undefined, TY.void);
        case 'GetEnumerator': return R(iter(l, 0), TY.dyn);
      }
      return linq(I, seq(l.view(I), et), id, args, tys, n, l);
    }
    /* C++ containers */
    const U = x => R(BigInt(x), TY.ulong);
    const ub = what => new Fatal(`${what} on an empty ${kind} is undefined behaviour, and real programs often crash here. Check empty() first`, 'ub');
    switch (id) {
      case 'push_back': case 'emplace_back': a.push(C(args.length > 1 ? (I.classes.get(et && et.n) ? I.construct(I.classes.get(et.n), args, tys, null, n.line) : pair(a0, a1, tys[0], tys[1])) : I.copyVal(a0))); return R(undefined, TY.void);
      case 'push_front': case 'emplace_front': a.unshift(C(a0)); return R(undefined, TY.void);
      case 'push': case 'emplace': a.push(C(I.copyVal(a0))); return R(undefined, TY.void);
      case 'pop_back': if (!a.length) throw ub('pop_back()'); a.pop(); return R(undefined, TY.void);
      case 'pop_front': if (!a.length) throw ub('pop_front()'); a.shift(); return R(undefined, TY.void);
      case 'pop': if (!a.length) throw ub('pop()'); if (kind === 'stack') a.pop(); else a.shift(); return R(undefined, TY.void);
      case 'top': if (!a.length) throw ub('top()'); return R(a[a.length - 1], et);
      case 'front': if (!a.length) throw ub('front()'); return R(a[0], et);
      case 'back': if (!a.length) throw ub('back()'); return R(a[a.length - 1], et);
      case 'size': return U(a.length);
      case 'max_size': return U(2305843009213693951);
      case 'empty': return R(a.length === 0, TY.bool);
      case 'clear': a.length = 0; return R(undefined, TY.void);
      case 'at': { const k = toNum(a0); if (k < 0 || k >= a.length) throw I.ex('out_of_range', `vector::_M_range_check: __n (which is ${k}) >= this->size() (which is ${a.length})`); return R(a[k], et); }
      case 'begin': case 'cbegin': return R(iter(l, 0), TY.dyn);
      case 'end': case 'cend': return R(iter(l, a.length), TY.dyn);
      case 'rbegin': return R(iter(l, 0, { rev: true }), TY.dyn);
      case 'rend': return R(iter(l, a.length, { rev: true }), TY.dyn);
      case 'insert': case 'emplace': {
        const k = a0 && a0.$iter ? a0.i : toNum(a0);
        if (args.length === 3) { const items = a1 && a1.$iter ? (() => { const r = range(I, a1, args[2]); return r.a.slice(r.lo, r.hi); })() : Array(toNum(a1)).fill(args[2]); a.splice(k, 0, ...items.map(C)); }
        else if (a1 instanceof Arr) a.splice(k, 0, ...a1.a.map(C));
        else a.splice(k, 0, C(a1));
        return R(iter(l, k), TY.dyn);
      }
      case 'erase': {
        const k = a0 && a0.$iter ? a0.i : toNum(a0);
        if (k < 0 || k >= a.length) throw new Fatal('erase() was given a position outside the vector. That is undefined behaviour');
        const e = a1 && a1.$iter ? a1.i : k + 1;
        a.splice(k, e - k);
        return R(iter(l, k), TY.dyn);
      }
      case 'resize': { const k = toNum(a0); if (a.length > k) a.length = k; else while (a.length < k) a.push(a1 !== undefined ? I.copyVal(C(a1)) : I.defaultVal(et)); return R(undefined, TY.void); }
      case 'assign': { const k = toNum(a0); a.length = 0; for (let i = 0; i < k; i++) a.push(I.copyVal(C(a1))); return R(undefined, TY.void); }
      case 'reserve': case 'shrink_to_fit': return R(undefined, TY.void);
      case 'capacity': { let c = 1; while (c < a.length) c *= 2; return U(a.length ? c : 0); }
      case 'swap': { const o = a0; const t = l.a; l.a = o.a; o.a = t; return R(undefined, TY.void); }
      case 'data': return R(new Ptr(a, 0, null, et), Object.assign({}, et, { ptr: 1 }));
      case 'sort': sortArr(I, a, cmpFrom(I, a0, 'less')); return R(undefined, TY.void);
      case 'reverse': a.reverse(); return R(undefined, TY.void);
      case 'remove': { const keep = a.filter(x => !(I.equals(x, a0) || x == a0)); a.splice(0, a.length, ...keep); return R(undefined, TY.void); }
      case 'unique': { const out = []; for (const x of a) if (!out.length || !(I.equals(out[out.length - 1], x) || out[out.length - 1] === x)) out.push(x); a.splice(0, a.length, ...out); return R(undefined, TY.void); }
      case 'fill': a.fill(C(a0)); return R(undefined, TY.void);
    }
    return NONE;
  }
  function mapMethod(I, m, id, args, tys, refs, n, recvRef) {
    const lang = I.lang;
    const a0 = args[0], a1 = args[1];
    const K = v => I.conv(v, m.kt), V = v => I.conv(v, m.vt);
    const immut = () => { if (m.immutable) throw I.ex('UnsupportedOperationException', null); };
    if (lang === 'java') {
      switch (id) {
        case 'put': { immut(); const old = m.put(I, K(a0), V(a1)); return R(old === undefined ? null : old, m.vt); }
        case 'get': { const r = m.get(I, a0); return R(r ? r.v : null, m.vt); }
        case 'getOrDefault': { const r = m.get(I, a0); return R(r ? r.v : a1, m.vt); }
        case 'containsKey': return R(!!m.get(I, a0), TY.bool);
        case 'containsValue': return R([...m.m.values()].some(r => I.equals(r.v, a0) || r.v === a0), TY.bool);
        case 'remove': { immut(); const r = m.del(I, a0); return R(r ? r.v : null, m.vt); }
        case 'size': return R(m.m.size, TY.int);
        case 'isEmpty': return R(m.m.size === 0, TY.bool);
        case 'clear': m.m.clear(); return R(undefined, TY.void);
        case 'putIfAbsent': { const r = m.get(I, a0); if (r && r.v !== null) return R(r.v, m.vt); m.put(I, K(a0), V(a1)); return R(null, m.vt); }
        case 'merge': { const r = m.get(I, a0); if (!r || r.v === null) { m.put(I, K(a0), V(a1)); return R(a1, m.vt); } const nv = I.callFn(args[2], [r.v, a1], [m.vt, tys[1]]); if (nv === null) m.del(I, a0); else r.v = V(nv); return R(nv, m.vt); }
        case 'compute': { const r = m.get(I, a0); const nv = I.callFn(a1, [a0, r ? r.v : null], [m.kt, m.vt]); if (nv === null) m.del(I, a0); else m.put(I, K(a0), V(nv)); return R(nv, m.vt); }
        case 'computeIfAbsent': { const r = m.get(I, a0); if (r && r.v !== null) return R(r.v, m.vt); const nv = I.callFn(a1, [a0], [m.kt]); if (nv !== null) m.put(I, K(a0), V(nv)); return R(nv, m.vt); }
        case 'computeIfPresent': { const r = m.get(I, a0); if (!r || r.v === null) return R(null, m.vt); const nv = I.callFn(a1, [a0, r.v], [m.kt, m.vt]); if (nv === null) m.del(I, a0); else r.v = V(nv); return R(nv, m.vt); }
        case 'putAll': for (const e of a0.ents(I)) m.put(I, e.k, e.v); return R(undefined, TY.void);
        case 'keySet': { const s = newSet(I, 'KeyView', m.kt); m.ents(I).forEach(e => s.add(I, e.k)); s.kind = 'LinkedHashSet'; s.view = m; return R(s, T('Set', { args: [m.kt] })); }
        case 'values': return R(newList(I, 'ValuesView', m.vt, m.ents(I).map(e => e.v)), T('Collection', { args: [m.vt] }));
        case 'entrySet': { const l = newList(I, 'EntrySet', T('Entry', { args: [m.kt, m.vt] }), m.ents(I).map(e => entryOf(I, m, e))); return R(l, T('Set')); }
        case 'forEach': for (const e of m.ents(I)) I.callFn(a0, [e.k, e.v], [m.kt, m.vt]); return R(undefined, TY.void);
        case 'replaceAll': for (const e of m.ents(I)) e.v = V(I.callFn(a0, [e.k, e.v], [m.kt, m.vt])); return R(undefined, TY.void);
        case 'toString': return R(m.$str(I), TY.string);
        case 'equals': return R(m.$eq(a0, I), TY.bool);
        case 'hashCode': { let h = 0; for (const e of m.m.values()) h = (h + (I.hashOf(e.k) ^ I.hashOf(e.v))) | 0; return R(h, TY.int); }
        case 'firstKey': case 'lastKey': { const es = m.ents(I); if (!es.length) throw I.ex('NoSuchElementException', null); return R(id === 'firstKey' ? es[0].k : es[es.length - 1].k, m.kt); }
        case 'firstEntry': case 'lastEntry': case 'pollFirstEntry': case 'pollLastEntry': { const es = m.ents(I); if (!es.length) return R(null, TY.dyn); const e = id.includes('irst') ? es[0] : es[es.length - 1]; if (id.startsWith('poll')) m.del(I, e.k); return R(id.startsWith('poll') ? pair(e.k, e.v, m.kt, m.vt) : entryOf(I, m, e), T('Entry')); }
        case 'floorKey': case 'ceilingKey': case 'higherKey': case 'lowerKey': case 'floorEntry': case 'ceilingEntry': case 'higherEntry': case 'lowerEntry': {
          const es = m.ents(I); let pick = null;
          for (const e of es) { const c = natCmp(I, e.k, a0); if ((/floor/.test(id) && c <= 0) || (/lower/.test(id) && c < 0)) pick = e; if ((/ceiling/.test(id) && c >= 0) || (/higher/.test(id) && c > 0)) { pick = e; break; } }
          if (/Entry$/.test(id)) return R(pick ? entryOf(I, m, pick) : null, T('Entry'));
          return R(pick ? pick.k : null, m.kt);
        }
        case 'headMap': case 'tailMap': { const c = newMap(I, 'TreeMap', m.kt, m.vt); for (const e of m.ents(I)) { const x = natCmp(I, e.k, a0); if (id === 'headMap' ? x < 0 || (a1 && x === 0) : x >= 0) c.put(I, e.k, e.v); } return R(c, m.$ty()); }
        case 'descendingMap': { const c = newMap(I, 'LinkedHashMap', m.kt, m.vt); m.ents(I).reverse().forEach(e => c.put(I, e.k, e.v)); return R(c, m.$ty()); }
        case 'navigableKeySet': case 'descendingKeySet': { const s = newSet(I, 'LinkedHashSet', m.kt); (id === 'descendingKeySet' ? m.ents(I).reverse() : m.ents(I)).forEach(e => s.add(I, e.k)); return R(s, T('Set')); }
      }
      return NONE;
    }
    if (lang === 'cs') {
      switch (id) {
        case 'Add': { if (m.get(I, a0)) throw I.ex('ArgumentException', `An item with the same key has already been added. Key: ${I.str(a0, m.kt)}`); m.put(I, K(a0), V(a1)); return R(undefined, TY.void); }
        case 'TryAdd': { if (m.get(I, a0)) return R(false, TY.bool); m.put(I, K(a0), V(a1)); return R(true, TY.bool); }
        case 'ContainsKey': return R(!!m.get(I, a0), TY.bool);
        case 'ContainsValue': return R([...m.m.values()].some(r => I.equals(r.v, a0) || r.v === a0), TY.bool);
        case 'Remove': { const r = m.del(I, a0); if (args.length === 2 && refs[1]) refs[1].set(r ? r.v : I.defaultVal(m.vt)); return R(!!r, TY.bool); }
        case 'TryGetValue': { const r = m.get(I, a0); if (refs[1]) refs[1].set(r ? r.v : I.defaultVal(m.vt)); return R(!!r, TY.bool); }
        case 'GetValueOrDefault': { const r = m.get(I, a0); return R(r ? r.v : (a1 !== undefined ? a1 : I.defaultVal(m.vt)), m.vt); }
        case 'Clear': m.m.clear(); return R(undefined, TY.void);
        case 'ToString': return R(m.$str(I), TY.string);
      }
      return linq(I, seq(m.ents(I).map(e => entryOf(I, m, e)), T('KeyValuePair', { args: [m.kt, m.vt] })), id, args, tys, n, m);
    }
    /* C++ map */
    const U = x => R(BigInt(x), TY.ulong);
    const keysIter = (pos) => { const keys = orderOf(I, m, [...m.m.entries()]).map(x => x[0]); return iter(m, pos === 'end' ? keys.length : pos, { keys, map: m }); };
    switch (id) {
      case 'insert': case 'emplace': case 'try_emplace': {
        let k, v;
        if (args.length === 2) { k = a0; v = a1; } else { const p = unpackPair(I, a0); k = p[0]; v = p[1]; }
        const had = !!m.get(I, k);
        if (!had || m.kind === 'multimap') m.put(I, K(k), V(v));
        return R(pair(keysIter(0), !had, TY.dyn, TY.bool), T('pair'));
      }
      case 'count': return U(m.get(I, a0) ? 1 : 0);
      case 'contains': return R(!!m.get(I, a0), TY.bool);
      case 'find': { const keys = orderOf(I, m, [...m.m.entries()]).map(x => x[0]); const kk = keyOf(I, a0); const i = keys.indexOf(kk); return R(iter(m, i < 0 ? keys.length : i, { keys, map: m }), TY.dyn); }
      case 'at': { const r = m.get(I, a0); if (!r) throw I.ex('out_of_range', 'map::at'); return R(r.v, m.vt); }
      case 'erase': { if (a0 && a0.$iter) { const k = a0.keys[a0.i]; const r = m.m.get(k); m.m.delete(k); return R(keysIter(a0.i), TY.dyn); } return U(m.del(I, a0) ? 1 : 0); }
      case 'size': return U(m.m.size);
      case 'empty': return R(m.m.size === 0, TY.bool);
      case 'clear': m.m.clear(); return R(undefined, TY.void);
      case 'begin': case 'cbegin': return R(keysIter(0), TY.dyn);
      case 'end': case 'cend': return R(keysIter('end'), TY.dyn);
      case 'rbegin': { const keys = orderOf(I, m, [...m.m.entries()]).map(x => x[0]).reverse(); return R(iter(m, 0, { keys, map: m }), TY.dyn); }
      case 'rend': { const keys = orderOf(I, m, [...m.m.entries()]).map(x => x[0]).reverse(); return R(iter(m, keys.length, { keys, map: m }), TY.dyn); }
      case 'lower_bound': case 'upper_bound': { const ents = orderOf(I, m, [...m.m.entries()]); const keys = ents.map(x => x[0]); let i = ents.findIndex(x => id === 'lower_bound' ? natCmp(I, x[1].k, a0) >= 0 : natCmp(I, x[1].k, a0) > 0); if (i < 0) i = keys.length; return R(iter(m, i, { keys, map: m }), TY.dyn); }
    }
    return NONE;
  }
  function setMethod(I, s, id, args, tys, refs, n, recvRef) {
    const lang = I.lang;
    const a0 = args[0];
    const C = v => I.conv(v, s.et);
    if (lang === 'java') {
      switch (id) {
        case 'add': if (s.immutable) throw I.ex('UnsupportedOperationException', null); return R(s.add(I, C(a0)), TY.bool);
        case 'remove': if (s.view) s.view.del(I, a0); return R(s.del(I, a0), TY.bool);
        case 'contains': return R(s.has(I, a0), TY.bool);
        case 'size': return R(s.size(), TY.int);
        case 'isEmpty': return R(s.size() === 0, TY.bool);
        case 'clear': s.m.clear(); return R(undefined, TY.void);
        case 'addAll': { let ch = false; collItems(I, a0).forEach(x => { if (s.add(I, C(x))) ch = true; }); return R(ch, TY.bool); }
        case 'retainAll': { const other = collItems(I, a0); let ch = false; for (const x of s.items(I)) if (!other.some(y => I.equals(x, y) || x === y)) { s.del(I, x); ch = true; } return R(ch, TY.bool); }
        case 'removeAll': { let ch = false; collItems(I, a0).forEach(x => { if (s.del(I, x)) ch = true; }); return R(ch, TY.bool); }
        case 'removeIf': { let ch = false; for (const x of s.items(I)) if (I.truthy(I.callFn(a0, [x], [s.et]))) { s.del(I, x); ch = true; } return R(ch, TY.bool); }
        case 'containsAll': return R(collItems(I, a0).every(x => s.has(I, x)), TY.bool);
        case 'stream': return R(seq(s.items(I), s.et), T('Stream'));
        case 'iterator': return R(iter({ a: s.items(I), et: s.et }, 0), T('Iterator'));
        case 'forEach': s.items(I).forEach(x => I.callFn(a0, [x], [s.et])); return R(undefined, TY.void);
        case 'toString': return R(s.$str(I), TY.string);
        case 'equals': return R(s.$eq(a0, I), TY.bool);
        case 'hashCode': return R(s.$hash(I), TY.int);
        case 'toArray': return R(new Arr(s.items(I), s.et), TY.dyn);
        case 'first': case 'last': { const it = s.items(I); if (!it.length) throw I.ex('NoSuchElementException', null); return R(id === 'first' ? it[0] : it[it.length - 1], s.et); }
        case 'pollFirst': case 'pollLast': { const it = s.items(I); if (!it.length) return R(null, s.et); const v = id === 'pollFirst' ? it[0] : it[it.length - 1]; s.del(I, v); return R(v, s.et); }
        case 'floor': case 'lower': case 'ceiling': case 'higher': {
          const it = s.items(I); let pick = null;
          for (const x of it) { const c = natCmp(I, x, a0); if ((id === 'floor' && c <= 0) || (id === 'lower' && c < 0)) pick = x; if ((id === 'ceiling' && c >= 0) || (id === 'higher' && c > 0)) { pick = x; break; } }
          return R(pick, s.et);
        }
        case 'headSet': case 'tailSet': case 'subSet': { const c = newSet(I, 'TreeSet', s.et); for (const x of s.items(I)) { const lo = id === 'tailSet' ? natCmp(I, x, a0) >= 0 : id === 'subSet' ? natCmp(I, x, a0) >= 0 && natCmp(I, x, args[1]) < 0 : natCmp(I, x, a0) < 0; if (lo) c.add(I, x); } return R(c, s.$ty()); }
        case 'descendingSet': { const c = newSet(I, 'LinkedHashSet', s.et); s.items(I).reverse().forEach(x => c.add(I, x)); return R(c, s.$ty()); }
      }
      return NONE;
    }
    if (lang === 'cs') {
      switch (id) {
        case 'Add': return R(s.add(I, C(a0)), TY.bool);
        case 'Remove': return R(s.del(I, a0), TY.bool);
        case 'Contains': return R(s.has(I, a0), TY.bool);
        case 'Clear': s.m.clear(); return R(undefined, TY.void);
        case 'UnionWith': collItems(I, a0).forEach(x => s.add(I, x)); return R(undefined, TY.void);
        case 'IntersectWith': { const o = collItems(I, a0); for (const x of s.items(I)) if (!o.some(y => I.equals(x, y) || x === y)) s.del(I, x); return R(undefined, TY.void); }
        case 'ExceptWith': collItems(I, a0).forEach(x => s.del(I, x)); return R(undefined, TY.void);
        case 'SymmetricExceptWith': collItems(I, a0).forEach(x => { if (!s.del(I, x)) s.add(I, x); }); return R(undefined, TY.void);
        case 'IsSubsetOf': { const o = collItems(I, a0); return R(s.items(I).every(x => o.some(y => I.equals(x, y) || x === y)), TY.bool); }
        case 'IsSupersetOf': return R(collItems(I, a0).every(x => s.has(I, x)), TY.bool);
        case 'Overlaps': return R(collItems(I, a0).some(x => s.has(I, x)), TY.bool);
        case 'SetEquals': { const o = collItems(I, a0); return R(o.length === s.size() && o.every(x => s.has(I, x)), TY.bool); }
        case 'RemoveWhere': { let c = 0; for (const x of s.items(I)) if (I.truthy(I.callFn(a0, [x], [s.et]))) { s.del(I, x); c++; } return R(c, TY.int); }
        case 'ToString': return R(s.$str(I), TY.string);
      }
      return linq(I, seq(s.items(I), s.et), id, args, tys, n, s);
    }
    const U = x => R(BigInt(x), TY.ulong);
    const it = (pos, items) => { const its = items || s.items(I); return iter({ a: its, et: s.et }, pos === 'end' ? its.length : pos, { set: s }); };
    switch (id) {
      case 'insert': case 'emplace': { if (a0 && a0.$iter) { const r = range(I, a0, args[1]); r.a.slice(r.lo, r.hi).forEach(x => s.add(I, x)); return R(undefined, TY.void); } const ok = s.add(I, C(a0)); return R(pair(it(0), ok, TY.dyn, TY.bool), T('pair')); }
      case 'erase': { if (a0 && a0.$iter) { const v = a0.c.a[a0.i]; s.del(I, v); return R(it(a0.i), TY.dyn); } let c = 0; while (s.del(I, a0)) { c++; if (s.kind !== 'multiset') break; } return U(c); }
      case 'count': return U(s.kind === 'multiset' ? s.multi.filter(x => I.equals(x, a0) || x === a0).length : (s.has(I, a0) ? 1 : 0));
      case 'contains': return R(s.has(I, a0), TY.bool);
      case 'find': { const items = s.items(I); const i = items.findIndex(x => I.equals(x, a0) || x === a0); return R(it(i < 0 ? items.length : i, items), TY.dyn); }
      case 'size': return U(s.size());
      case 'empty': return R(s.size() === 0, TY.bool);
      case 'clear': s.m.clear(); if (s.multi) s.multi.length = 0; return R(undefined, TY.void);
      case 'begin': case 'cbegin': return R(it(0), TY.dyn);
      case 'end': case 'cend': return R(it('end'), TY.dyn);
      case 'rbegin': return R(iter({ a: s.items(I).reverse(), et: s.et }, 0, { set: s }), TY.dyn);
      case 'rend': { const its = s.items(I).reverse(); return R(iter({ a: its, et: s.et }, its.length, { set: s }), TY.dyn); }
      case 'lower_bound': case 'upper_bound': { const items = s.items(I); let i = items.findIndex(x => id === 'lower_bound' ? natCmp(I, x, a0) >= 0 : natCmp(I, x, a0) > 0); if (i < 0) i = items.length; return R(it(i, items), TY.dyn); }
    }
    return NONE;
  }
  function optMethod(I, o, id, args, tys, n) {
    switch (id) {
      case 'isPresent': case 'HasValue': return R(o.has, TY.bool);
      case 'isEmpty': return R(!o.has, TY.bool);
      case 'get': case 'getAsInt': case 'getAsDouble': case 'getAsLong': case 'orElseThrow': if (!o.has) throw args.length ? new Throw(I.callFn(args[0], [], []), n.line) : I.ex('NoSuchElementException', 'No value present'); return R(o.v, o.ty);
      case 'orElse': return R(o.has ? o.v : args[0], o.ty || tys[0]);
      case 'orElseGet': return R(o.has ? o.v : I.callFn(args[0], [], []), o.ty);
      case 'ifPresent': if (o.has) I.callFn(args[0], [o.v], [o.ty]); return R(undefined, TY.void);
      case 'ifPresentOrElse': if (o.has) I.callFn(args[0], [o.v], [o.ty]); else I.callFn(args[1], [], []); return R(undefined, TY.void);
      case 'map': return R(o.has ? opt(I.callFn(args[0], [o.v], [o.ty])) : o, T('Optional'));
      case 'filter': return R(o.has && I.truthy(I.callFn(args[0], [o.v], [o.ty])) ? o : opt(null), T('Optional'));
      case 'toString': return R(o.$str(I), TY.string);
    }
    return NONE;
  }
  function randMethod(I, r, id, args, tys, n) {
    if (I.lang === 'cs') {
      const f = r.rng;
      switch (id) {
        case 'Next': if (!args.length) return R(Math.floor(f() * 2147483647), TY.int); if (args.length === 1) return R(Math.floor(f() * toNum(args[0])), TY.int); return R(toNum(args[0]) + Math.floor(f() * (toNum(args[1]) - toNum(args[0]))), TY.int);
        case 'NextDouble': return R(f(), TY.double);
        case 'NextInt64': return R(BigInt(Math.floor(f() * Number(toNum(args[0] || 2 ** 53)))), TY.long);
      }
      return NONE;
    }
    switch (id) {
      case 'nextInt': if (!args.length) return R(jnextInt(r), TY.int); if (args.length === 2) return R(toNum(args[0]) + jnextInt(r, toNum(args[1]) - toNum(args[0])), TY.int); if (toNum(args[0]) <= 0) throw I.ex('IllegalArgumentException', 'bound must be positive'); return R(jnextInt(r, toNum(args[0])), TY.int);
      case 'nextDouble': return R(jnextDouble(r), TY.double);
      case 'nextBoolean': return R(jnext(r, 1) !== 0, TY.bool);
      case 'nextLong': return R(BigInt.asIntN(64, (BigInt(jnext(r, 32)) << 32n) + BigInt(jnext(r, 32))), TY.long);
      case 'nextFloat': return R(jnext(r, 24) / (1 << 24), TY.float);
      case 'nextGaussian': { const u = jnextDouble(r), v = jnextDouble(r); return R(Math.sqrt(-2 * Math.log(u || 1e-12)) * Math.cos(2 * Math.PI * v), TY.double); }
      case 'setSeed': r.seed = javaSeed(toBig(args[0])); return R(undefined, TY.void);
    }
    return NONE;
  }
  function scanMethod(I, s, id, args, tys, n) {
    const need = what => { const t = Input.token(I); if (t === null) throw I.ex('NoSuchElementException', what); return t; };
    switch (id) {
      case 'nextInt': case 'nextLong': case 'nextShort': case 'nextByte': {
        const t = need(null);
        if (!/^[+-]?\d+$/.test(t)) { I.inPos -= t.length; throw I.ex('InputMismatchException', `For input string: "${t}"`); }
        return R(id === 'nextLong' ? BigInt(t) : i32(Number(t)), id === 'nextLong' ? TY.long : TY.int);
      }
      case 'nextDouble': case 'nextFloat': { const t = need(null); if (!/^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/.test(t)) { I.inPos -= t.length; throw I.ex('InputMismatchException', `For input string: "${t}"`); } return R(parseFloat(t), TY.double); }
      case 'nextBoolean': { const t = need(null); if (!/^(true|false)$/i.test(t)) throw I.ex('InputMismatchException', t); return R(t.toLowerCase() === 'true', TY.bool); }
      case 'next': return R(need(null), TY.string);
      case 'nextLine': case 'readLine': { const l = Input.line(I); if (l === null) { if (id === 'readLine') return R(null, TY.string); throw I.ex('NoSuchElementException', 'No line found'); } return R(l, TY.string); }
      case 'hasNext': return R(Input.peekToken(I) !== null, TY.bool);
      case 'hasNextInt': case 'hasNextLong': { const t = Input.peekToken(I); return R(t !== null && /^[+-]?\d+$/.test(t), TY.bool); }
      case 'hasNextDouble': { const t = Input.peekToken(I); return R(t !== null && /^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/.test(t), TY.bool); }
      case 'hasNextLine': return R(I.inPos < I.stdin.length, TY.bool);
      case 'read': return R(Input.char(I), TY.int);
      case 'close': return R(undefined, TY.void);
      case 'lines': return R(seq(I.stdin.slice(I.inPos).split('\n').filter((x, i, a) => i < a.length - 1 || x), TY.string), T('Stream'));
    }
    return NONE;
  }

  /* ===== Java streams ===== */
  function numericSeq(s) { return s.prim === 'Int' || s.prim === 'Double' || s.prim === 'Long'; }
  function streamOps(I, s, id, args, tys, n) {
    if (I.lang === 'cs') return linq(I, s, id, args, tys, n);
    const a = s.a, et = s.et, f = args[0];
    const call = (x, t) => I.callFn(f, [x], [t || et]);
    const S = (arr, t, prim) => R(seq(arr, t, prim), T('Stream'));
    switch (id) {
      case 'filter': return S(a.filter(x => I.truthy(call(x))), et, s.prim);
      case 'map': { const out = a.map(x => call(x)); const t = s.prim === 'Int' ? TY.int : s.prim === 'Double' ? TY.double : (out.length ? valTy(out[0]) : TY.dyn); return S(s.prim === 'Int' ? out.map(i32) : out, t, s.prim); }
      case 'mapToInt': return S(a.map(x => i32(call(x))), TY.int, 'Int');
      case 'mapToLong': return S(a.map(x => toBig(call(x))), TY.long, 'Long');
      case 'mapToDouble': case 'asDoubleStream': return S(id === 'asDoubleStream' ? a.map(toNum) : a.map(x => toNum(call(x))), TY.double, 'Double');
      case 'mapToObj': { const out = a.map(x => call(x)); return S(out, out.length ? valTy(out[0]) : TY.dyn, null); }
      case 'boxed': return S(a.slice(), Object.assign({}, et, { box: true }), null);
      case 'flatMap': { const out = []; a.forEach(x => { const r = call(x); out.push(...(r && r.a ? r.a : collItems(I, r))); }); return S(out, out.length ? valTy(out[0]) : TY.dyn, null); }
      case 'sorted': return S(sortArr(I, a.slice(), cmpFrom(I, f)), et, s.prim);
      case 'distinct': { const seen = new Set(), out = []; a.forEach(x => { const k = keyOf(I, x); if (!seen.has(k)) { seen.add(k); out.push(x); } }); return S(out, et, s.prim); }
      case 'limit': return S(a.slice(0, toNum(f)), et, s.prim);
      case 'skip': return S(a.slice(toNum(f)), et, s.prim);
      case 'peek': a.forEach(x => call(x)); return S(a.slice(), et, s.prim);
      case 'takeWhile': { const out = []; for (const x of a) { if (!I.truthy(call(x))) break; out.push(x); } return S(out, et, s.prim); }
      case 'dropWhile': { let i = 0; while (i < a.length && I.truthy(call(a[i]))) i++; return S(a.slice(i), et, s.prim); }
      case 'forEach': case 'forEachOrdered': a.forEach(x => call(x)); return R(undefined, TY.void);
      case 'toList': return R(newList(I, 'ImmutableList', et, a.slice()), T('List', { args: [et] }));
      case 'toArray': return R(new Arr(a.slice(), et), Object.assign({}, et, { dim: 1 }));
      case 'count': return R(BigInt(a.length), TY.long);
      case 'sum': { if (s.prim === 'Int') return R(a.reduce((p, x) => (p + toNum(x)) | 0, 0), TY.int); if (s.prim === 'Long') return R(a.reduce((p, x) => p + toBig(x), 0n), TY.long); return R(a.reduce((p, x) => p + toNum(x), 0), TY.double); }
      case 'average': return R(opt(a.length ? a.reduce((p, x) => p + toNum(x), 0) / a.length : null, TY.double, 'OptionalDouble'), T('OptionalDouble'));
      case 'max': case 'min': {
        if (!a.length) return R(opt(null, et, numericSeq(s) ? 'Optional' + s.prim : 'Optional'), T('Optional'));
        const cmp = cmpFrom(I, f);
        const r = a.reduce((m, x) => (id === 'max' ? cmp(x, m) > 0 : cmp(x, m) < 0) ? x : m);
        return R(opt(r, et, numericSeq(s) ? 'Optional' + s.prim : 'Optional'), T('Optional'));
      }
      case 'reduce': {
        if (args.length === 1) { if (!a.length) return R(opt(null), T('Optional')); let acc = a[0]; for (let i = 1; i < a.length; i++) acc = I.callFn(f, [acc, a[i]], [et, et]); return R(opt(acc, et, numericSeq(s) ? 'Optional' + s.prim : null), T('Optional')); }
        let acc = args[0]; for (const x of a) acc = I.callFn(args[1], [acc, x], [tys[0], et]); return R(s.prim === 'Int' ? i32(acc) : acc, tys[0]);
      }
      case 'anyMatch': return R(a.some(x => I.truthy(call(x))), TY.bool);
      case 'allMatch': return R(a.every(x => I.truthy(call(x))), TY.bool);
      case 'noneMatch': return R(!a.some(x => I.truthy(call(x))), TY.bool);
      case 'findFirst': case 'findAny': return R(opt(a.length ? a[0] : null, et, numericSeq(s) ? 'Optional' + s.prim : null), T('Optional'));
      case 'summaryStatistics': { const nums = a.map(toNum); return R({ $lib: true, $ty: () => T('Stats'), $str: () => `IntSummaryStatistics{count=${nums.length}, sum=${nums.reduce((p, x) => p + x, 0)}, min=${Math.min(...nums)}, average=${CF.fmt.fixedJava(nums.reduce((p, x) => p + x, 0) / nums.length, 6)}, max=${Math.max(...nums)}}`, getMax: Math.max(...nums), getMin: Math.min(...nums), getSum: nums.reduce((p, x) => p + x, 0), getCount: nums.length, getAverage: nums.length ? nums.reduce((p, x) => p + x, 0) / nums.length : 0 }, T('Stats')); }
      case 'collect': return R(collect(I, a, et, f), TY.dyn);
      case 'iterator': return R(iter({ a: a.slice(), et }, 0), T('Iterator'));
      case 'parallel': case 'sequential': case 'unordered': case 'onClose': return R(s, T('Stream'));
    }
    return NONE;
  }
  function collect(I, a, et, c) {
    const k = c.coll, args = c.args;
    switch (k) {
      case 'toList': case 'toUnmodifiableList': return newList(I, 'ArrayList', et, a.slice());
      case 'toSet': case 'toUnmodifiableSet': { const s = newSet(I, 'HashSet', et); a.forEach(x => s.add(I, x)); return s; }
      case 'joining': return (args[1] !== undefined ? args[1] : '') + a.map(x => I.str(x, et)).join(args[0] !== undefined ? args[0] : '') + (args[2] !== undefined ? args[2] : '');
      case 'counting': return BigInt(a.length);
      case 'summingInt': return a.reduce((p, x) => (p + toNum(I.callFn(args[0], [x], [et]))) | 0, 0);
      case 'summingDouble': return a.reduce((p, x) => p + toNum(I.callFn(args[0], [x], [et])), 0);
      case 'averagingInt': case 'averagingDouble': return a.length ? a.reduce((p, x) => p + toNum(I.callFn(args[0], [x], [et])), 0) / a.length : 0;
      case 'toMap': { const m = newMap(I, 'HashMap', null, null); a.forEach(x => { const kk = I.callFn(args[0], [x], [et]), vv = I.callFn(args[1], [x], [et]); const r = m.get(I, kk); if (r) { if (!args[2]) throw I.ex('IllegalStateException', `Duplicate key ${I.str(kk)} (attempted merging values ${I.str(r.v)} and ${I.str(vv)})`); r.v = I.callFn(args[2], [r.v, vv], []); } else m.put(I, kk, vv); }); if (a.length) { m.kt = valTy(m.ents(I)[0].k); m.vt = valTy(m.ents(I)[0].v); } return m; }
      case 'groupingBy': case 'partitioningBy': {
        const m = k === 'partitioningBy' ? newMap(I, 'LinkedHashMap', TY.bool, null) : (args[1] && args[1].$lib && args[1].coll === undefined && false) ? null : newMap(I, 'HashMap', null, null);
        if (k === 'partitioningBy') { m.put(I, false, []); m.put(I, true, []); }
        const groups = new Map();
        a.forEach(x => { const kk = I.callFn(args[0], [x], [et]); const key = keyOf(I, kk); if (!groups.has(key)) groups.set(key, [kk, []]); groups.get(key)[1].push(x); });
        if (k === 'partitioningBy') { groups.forEach(([kk, items]) => { m.put(I, kk, items); }); }
        else groups.forEach(([kk, items]) => m.put(I, kk, items));
        const down = args.find((x, i) => i > 0 && x && x.coll);
        for (const e of m.m.values()) e.v = down ? collect(I, e.v, et, down) : newList(I, 'ArrayList', et, e.v);
        if (m.m.size) { const first = [...m.m.values()][0]; m.kt = valTy(first.k); m.vt = valTy(first.v); }
        if (down && down.coll === 'counting') m.vt = TY.long;
        return m;
      }
      case 'mapping': return collect(I, a.map(x => I.callFn(args[0], [x], [et])), TY.dyn, args[1]);
    }
    throw new CF.CompileError(`Collectors.${k} is not available in this playground`, I.lastLine);
  }

  /* ===== C# LINQ ===== */
  function linq(I, s, id, args, tys, n, orig) {
    const a = s.a, et = s.et, f = args[0];
    const call = (x, i) => I.callFn(f, f.params && f.params.length === 2 ? [x, i] : [x], [et, TY.int]);
    const S = (arr, t) => R(seq(arr, t || et), T('IEnumerable'));
    const none = () => I.ex('InvalidOperationException', 'Sequence contains no elements');
    switch (id) {
      case 'Where': return S(a.filter((x, i) => I.truthy(call(x, i))));
      case 'Select': { const out = a.map((x, i) => call(x, i)); return S(out, out.length ? (f.exprBody && f.body && f.body.ty) || valTy(out[0]) : TY.dyn); }
      case 'SelectMany': { const out = []; a.forEach(x => out.push(...collItems(I, call(x)))); return S(out, out.length ? valTy(out[0]) : TY.dyn); }
      case 'OrderBy': case 'ThenBy': { const r = seq(sortArr(I, a.slice(), (x, y) => natCmp(I, call(x), call(y))), et); r.keys = [[f, 1]]; return R(r, T('IOrderedEnumerable')); }
      case 'OrderByDescending': case 'ThenByDescending': { const r = seq(sortArr(I, a.slice(), (x, y) => natCmp(I, call(y), call(x))), et); return R(r, T('IOrderedEnumerable')); }
      case 'Order': return S(sortArr(I, a.slice(), (x, y) => natCmp(I, x, y)));
      case 'OrderDescending': return S(sortArr(I, a.slice(), (x, y) => natCmp(I, y, x)));
      case 'Reverse': return S(a.slice().reverse());
      case 'Distinct': { const seen = new Set(), out = []; a.forEach(x => { const k = keyOf(I, x); if (!seen.has(k)) { seen.add(k); out.push(x); } }); return S(out); }
      case 'Take': return S(a.slice(0, toNum(f)));
      case 'Skip': return S(a.slice(toNum(f)));
      case 'TakeWhile': { const out = []; for (const x of a) { if (!I.truthy(call(x))) break; out.push(x); } return S(out); }
      case 'SkipWhile': { let i = 0; while (i < a.length && I.truthy(call(a[i]))) i++; return S(a.slice(i)); }
      case 'Concat': case 'Union': { let out = a.concat(collItems(I, f)); if (id === 'Union') { const seen = new Set(); out = out.filter(x => { const k = keyOf(I, x); if (seen.has(k)) return false; seen.add(k); return true; }); } return S(out); }
      case 'Intersect': { const o = collItems(I, f); return S(a.filter((x, i) => o.some(y => I.equals(x, y) || x === y) && a.findIndex(z => z === x) === i)); }
      case 'Except': { const o = collItems(I, f); return S(a.filter(x => !o.some(y => I.equals(x, y) || x === y))); }
      case 'Zip': { const o = collItems(I, f); const out = []; for (let i = 0; i < Math.min(a.length, o.length); i++) out.push(args[1] ? I.callFn(args[1], [a[i], o[i]], []) : LIB.tuple(I, [a[i], o[i]])); return S(out, out.length ? valTy(out[0]) : TY.dyn); }
      case 'ToList': return R(newList(I, 'List', et, a.slice()), T('List', { args: [et] }));
      case 'ToArray': return R(new Arr(a.slice(), et), Object.assign({}, et, { dim: 1 }));
      case 'ToHashSet': { const st = newSet(I, 'HashSet', et); a.forEach(x => st.add(I, x)); return R(st, st.$ty()); }
      case 'ToDictionary': { const m = newMap(I, 'Dictionary', null, null); a.forEach(x => { const k = I.callFn(f, [x], [et]); if (m.get(I, k)) throw I.ex('ArgumentException', `An item with the same key has already been added. Key: ${I.str(k)}`); m.put(I, k, args[1] ? I.callFn(args[1], [x], [et]) : x); }); if (a.length) { const e = m.ents(I)[0]; m.kt = valTy(e.k); m.vt = args[1] ? valTy(e.v) : et; } return R(m, m.$ty()); }
      case 'Count': case 'LongCount': return R(f ? a.filter(x => I.truthy(call(x))).length : a.length, TY.int);
      case 'Sum': { const vals = f ? a.map(x => call(x)) : a; const t = f ? (vals.length ? valTy(vals[0]) : TY.int) : et; if (t && (t.n === 'double' || t.n === 'float')) return R(vals.reduce((p, x) => p + toNum(x), 0), TY.double); if (t && t.n === 'long') return R(vals.reduce((p, x) => p + toBig(x), 0n), TY.long); const tot = vals.reduce((p, x) => p + toNum(x), 0); if (tot > 2147483647 || tot < -2147483648) throw I.ex('OverflowException', 'Arithmetic operation resulted in an overflow.'); return R(Number.isInteger(tot) && !(vals.some(x => !Number.isInteger(x))) ? tot : tot, vals.some(x => !Number.isInteger(toNum(x))) ? TY.double : TY.int); }
      case 'Average': { if (!a.length) throw none(); const vals = f ? a.map(x => toNum(call(x))) : a.map(toNum); return R(vals.reduce((p, x) => p + x, 0) / vals.length, TY.double); }
      case 'Max': case 'Min': { if (!a.length) throw none(); const vals = f ? a.map(x => call(x)) : a; const r = vals.reduce((m, x) => (id === 'Max' ? natCmp(I, x, m) > 0 : natCmp(I, x, m) < 0) ? x : m); return R(r, f ? valTy(r) : et); }
      case 'MaxBy': case 'MinBy': { if (!a.length) throw none(); const r = a.reduce((m, x) => (id === 'MaxBy' ? natCmp(I, call(x), call(m)) > 0 : natCmp(I, call(x), call(m)) < 0) ? x : m); return R(r, et); }
      case 'First': case 'Last': case 'Single': { const items = f ? a.filter(x => I.truthy(call(x))) : a; if (!items.length) throw f ? I.ex('InvalidOperationException', 'Sequence contains no matching element') : none(); if (id === 'Single' && items.length > 1) throw I.ex('InvalidOperationException', 'Sequence contains more than one element'); return R(id === 'Last' ? items[items.length - 1] : items[0], et); }
      case 'FirstOrDefault': case 'LastOrDefault': case 'SingleOrDefault': { const items = f && f instanceof Fn ? a.filter(x => I.truthy(call(x))) : a; if (!items.length) return R(f && !(f instanceof Fn) ? f : I.defaultVal(et), et); return R(id === 'LastOrDefault' ? items[items.length - 1] : items[0], et); }
      case 'ElementAt': { const k = toNum(f); if (k < 0 || k >= a.length) throw I.ex('ArgumentOutOfRangeException', "Index was out of range. Must be non-negative and less than the size of the collection. (Parameter 'index')"); return R(a[k], et); }
      case 'Any': return R(f ? a.some(x => I.truthy(call(x))) : a.length > 0, TY.bool);
      case 'All': return R(a.every(x => I.truthy(call(x))), TY.bool);
      case 'Contains': return R(a.some(x => I.equals(x, f) || x === f), TY.bool);
      case 'Aggregate': { if (args.length === 1) { if (!a.length) throw none(); let acc = a[0]; for (let i = 1; i < a.length; i++) acc = I.callFn(f, [acc, a[i]], [et, et]); return R(acc, et); } let acc = args[0]; for (const x of a) acc = I.callFn(args[1], [acc, x], [tys[0], et]); return R(args[2] ? I.callFn(args[2], [acc], []) : acc, tys[0]); }
      case 'GroupBy': {
        const groups = new Map();
        a.forEach(x => { const k = call(x); const kk = keyOf(I, k); if (!groups.has(kk)) groups.set(kk, mk(SeqP, { a: [], et, key: k, kt: valTy(k), grp: true })); groups.get(kk).a.push(args[1] ? I.callFn(args[1], [x], [et]) : x); });
        return S([...groups.values()], T('IGrouping'));
      }
      case 'ToLookup': return linq(I, s, 'GroupBy', args, tys, n);
      case 'Append': return S(a.concat([f]));
      case 'Prepend': return S([f].concat(a));
      case 'DefaultIfEmpty': return S(a.length ? a.slice() : [f !== undefined ? f : I.defaultVal(et)]);
      case 'SequenceEqual': { const o = collItems(I, f); return R(o.length === a.length && a.every((x, i) => I.equals(x, o[i]) || x === o[i]), TY.bool); }
      case 'Cast': case 'OfType': case 'AsEnumerable': return S(a.slice());
      case 'Chunk': { const k = toNum(f); const out = []; for (let i = 0; i < a.length; i += k) out.push(new Arr(a.slice(i, i + k), et)); return S(out, Object.assign({}, et, { dim: 1 })); }
      case 'ToString': return R(s.$str(I), TY.string);
      case 'GetEnumerator': return R(iter(s, 0), TY.dyn);
      case 'ForEach': if (orig) break; break;
      case 'Length': break;
    }
    return NONE;
  }
})();
