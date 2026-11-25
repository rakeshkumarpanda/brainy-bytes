/* ===== Code Playground: compile time checks for Java, C# and C++ =====
   javac and the C# compiler read the whole program before it runs. They reject a program whose types do not fit,
   even on a line that would never run. The runner in cf-run.js works line by line, so this file walks every class,
   method and statement first, the way a compiler does, and throws CF.CompileError for the mistakes below.

   Java and C#
     a value that does not fit its variable    byte b3 = b1 + b2;   int n = 3.5;   float f = 1.5;   String s = 5;
     the same rule for method arguments, return values and array lists
     a condition that is not true or false     if (n) { }
     operators used on the wrong types         "a" < "b"   true + 1   !n   (int) "5"
     names that are not declared anywhere, and methods called with the wrong number of arguments
     instance fields or methods used from a static method
     a final (Java) or const (C#) variable that is changed
     a method that can reach its end without returning a value
   Java only
     a statement that can never run, such as one after return, break or an endless loop
     s.length without brackets on a String, and arr.length() on an array
   C++
     brace initialisation that loses information        int a{3.5};   char c{300};
     a string literal given to a number                 int x = "hi";

   The checker only reports what it is sure about. When it cannot tell a type, it stays quiet and the runner
   decides when the line runs, so a correct program is never stopped here. */
(() => {
  const G = typeof self !== 'undefined' ? self : globalThis;
  const CF = G.CF;
  const CE = CF.CompileError;

  const INTS = new Set(['byte', 'ubyte', 'short', 'ushort', 'char', 'int', 'uint', 'long', 'ulong']);
  const NUMS = new Set([...INTS, 'float', 'double']);
  const R = {
    byte: [-128n, 127n], ubyte: [0n, 255n], short: [-32768n, 32767n], ushort: [0n, 65535n], char: [0n, 65535n],
    int: [-2147483648n, 2147483647n], uint: [0n, 4294967295n], long: [-(2n ** 63n), 2n ** 63n - 1n], ulong: [0n, 2n ** 64n - 1n]
  };
  const split = o => { const r = {}; for (const k in o) r[k] = new Set(o[k].split(' ')); return r; };
  /* widening conversions that need no cast */
  const WJ = split({ byte: 'short int long float double', short: 'int long float double', char: 'int long float double', int: 'long float double', long: 'float double', float: 'double' });
  const WC = split({
    byte: 'short int long float double', ubyte: 'short ushort int uint long ulong float double', short: 'int long float double',
    ushort: 'int uint long ulong float double', int: 'long float double', uint: 'long ulong float double', long: 'float double',
    ulong: 'float double', char: 'ushort int uint long ulong float double', float: 'double'
  });
  const BOXN = { int: 'Integer', long: 'Long', short: 'Short', byte: 'Byte', char: 'Character', bool: 'Boolean', float: 'Float', double: 'Double' };
  const T = n => ({ n });
  const TI = T('int'), TL = T('long'), TD = T('double'), TF = T('float'), TB = T('bool'), TS = T('string'), TC = T('char');
  const isPrim = t => !!t && !t.dim && !t.ptr && !t.nullable && !t.dec;
  const isNum = t => isPrim(t) && NUMS.has(t.n);
  const isInt = t => isPrim(t) && INTS.has(t.n);
  const isBool = t => isPrim(t) && t.n === 'bool';
  const isStr = t => !!t && !t.dim && !t.ptr && t.n === 'string';
  const known = t => isNum(t) || isBool(t) || isStr(t);
  const big = v => typeof v === 'bigint' ? v : (Number.isInteger(v) ? BigInt(v) : null);
  const fits = (v, n) => { const b = big(v); return b !== null && R[n] && b >= R[n][0] && b <= R[n][1]; };
  const lower = id => /^[a-z]/.test(id);

  /* ---------- type names as each compiler prints them ---------- */
  function jName(t) {
    if (!t) return '?';
    let s = t.box ? (t.jn || BOXN[t.n] || t.n) : ({ bool: 'boolean', string: 'String', object: 'Object', null: '<null>', dyn: t.tp || 'T' }[t.n] || t.n);
    return s + '[]'.repeat(t.dim || 0);
  }
  function cName(t) {
    if (!t) return '?';
    let s = t.dec ? 'decimal' : ({ ubyte: 'byte', byte: 'sbyte', bool: 'bool', string: 'string', object: 'object', dyn: 'dynamic' }[t.n] || t.n);
    return s + (t.nullable ? '?' : '') + '[]'.repeat(t.dim || 0);
  }
  function pName(t) {
    if (!t) return '?';
    if (t.ptr && t.n === 'char') return 'const char*';
    return ({ long: 'long int', ulong: 'long unsigned int', uint: 'unsigned int', short: 'short int', ushort: 'short unsigned int', ubyte: 'unsigned char', byte: 'signed char', string: 'std::string' }[t.n] || t.n) + '*'.repeat(t.ptr || 0);
  }

  /* ---------- binary numeric promotion ---------- */
  function promote(lang, a, b) {
    const x = a.n, y = b.n;
    if (x === 'double' || y === 'double') return TD;
    if (x === 'float' || y === 'float') return TF;
    if (lang === 'cs') {
      if (x === 'ulong' || y === 'ulong') return (['byte', 'short', 'int', 'long'].includes(x === 'ulong' ? y : x)) ? null : T('ulong');
      if (x === 'long' || y === 'long') return TL;
      if (x === 'uint' || y === 'uint') return (['byte', 'short', 'int'].includes(x === 'uint' ? y : x)) ? TL : T('uint');
      return TI;
    }
    if (lang === 'cpp' || lang === 'c') {
      for (const n of ['ulong', 'long', 'uint']) if (x === n || y === n) return T(n);
      return TI;
    }
    if (x === 'long' || y === 'long') return TL;
    return TI;
  }
  const unary = t => (['byte', 'ubyte', 'short', 'ushort', 'char'].includes(t.n) ? TI : T(t.n));

  /* a constant value converted to type n, the way a cast does it */
  function conv(v, n) {
    if (v === undefined || v === null || typeof v === 'boolean' || typeof v === 'string') return v;
    if (n === 'double') return Number(v);
    if (n === 'float') return Math.fround(Number(v));
    if (!R[n]) return undefined;
    let b = typeof v === 'bigint' ? v : (Number.isFinite(v) ? BigInt(Math.trunc(v)) : null);
    if (b === null) return undefined;
    const bits = { byte: 8, ubyte: 8, short: 16, ushort: 16, char: 16, int: 32, uint: 32, long: 64, ulong: 64 }[n];
    b = (n === 'ubyte' || n === 'ushort' || n === 'char' || n === 'uint' || n === 'ulong') ? BigInt.asUintN(bits, b) : BigInt.asIntN(bits, b);
    return bits === 64 ? b : Number(b);
  }
  function fold(op, a, b, t) {
    if (a === undefined || b === undefined || !t) return undefined;
    if (typeof a === 'boolean' || typeof b === 'boolean') {
      if (typeof a !== typeof b) return undefined;
      switch (op) { case '&&': case '&': return a && b; case '||': case '|': return a || b; case '^': case '!=': return a !== b; case '==': return a === b; }
      return undefined;
    }
    if (typeof a === 'string' || typeof b === 'string') return undefined;
    const fl = t.n === 'double' || t.n === 'float';
    const L = t.n === 'long' || t.n === 'ulong';
    const cmp = ['<', '>', '<=', '>=', '==', '!='].includes(op);
    try {
      if (cmp) {
        const x = Number(a), y = Number(b);
        return { '<': x < y, '>': x > y, '<=': x <= y, '>=': x >= y, '==': x === y, '!=': x !== y }[op];
      }
      if (fl) {
        const x = Number(a), y = Number(b);
        const r = { '+': x + y, '-': x - y, '*': x * y, '/': x / y, '%': x % y }[op];
        return r === undefined ? undefined : (t.n === 'float' ? Math.fround(r) : r);
      }
      const x = BigInt(a), y = BigInt(b);
      let r;
      switch (op) {
        case '+': r = x + y; break; case '-': r = x - y; break; case '*': r = x * y; break;
        case '/': if (y === 0n) return undefined; r = x / y; break;
        case '%': if (y === 0n) return undefined; r = x % y; break;
        case '&': r = x & y; break; case '|': r = x | y; break; case '^': r = x ^ y; break;
        case '<<': r = x << (y & (L ? 63n : 31n)); break; case '>>': r = x >> (y & (L ? 63n : 31n)); break;
        default: return undefined;
      }
      return conv(r, t.n);
    } catch (e) { return undefined; }
  }

  /* ---------- library methods whose result type is certain ---------- */
  const JSTATIC = {
    Math: {
      d: 'sqrt cbrt pow random floor ceil rint log log10 log1p exp expm1 sin cos tan asin acos atan atan2 sinh cosh tanh hypot toRadians toDegrees',
      p: 'abs max min floorDiv floorMod addExact subtractExact multiplyExact'
    },
    Integer: { int: 'parseInt sum max min compare bitCount signum reverse highestOneBit lowestOneBit numberOfTrailingZeros numberOfLeadingZeros', string: 'toString toBinaryString toHexString toOctalString' },
    Long: { long: 'parseLong sum max min', int: 'compare bitCount signum', string: 'toString toBinaryString toHexString' },
    Double: { double: 'parseDouble sum max min', int: 'compare', bool: 'isNaN isInfinite isFinite', string: 'toString' },
    Float: { float: 'parseFloat' }, Short: { short: 'parseShort' }, Byte: { byte: 'parseByte' },
    Boolean: { bool: 'parseBoolean logicalAnd logicalOr logicalXor', string: 'toString' },
    Character: { bool: 'isDigit isLetter isLetterOrDigit isUpperCase isLowerCase isWhitespace isAlphabetic isSpaceChar', int: 'getNumericValue', string: 'toString' },
    String: { string: 'valueOf format join copyValueOf' },
    System: { long: 'currentTimeMillis nanoTime', string: 'lineSeparator getProperty getenv' }
  };
  const JCONST = {
    Integer: { MAX_VALUE: [TI, 2147483647], MIN_VALUE: [TI, -2147483648], SIZE: [TI, 32], BYTES: [TI, 4] },
    Long: { MAX_VALUE: [TL, 2n ** 63n - 1n], MIN_VALUE: [TL, -(2n ** 63n)] },
    Short: { MAX_VALUE: [T('short'), 32767], MIN_VALUE: [T('short'), -32768] },
    Byte: { MAX_VALUE: [T('byte'), 127], MIN_VALUE: [T('byte'), -128] },
    Character: { MAX_VALUE: [TC, 65535], MIN_VALUE: [TC, 0] },
    Double: { MAX_VALUE: [TD, Number.MAX_VALUE], MIN_VALUE: [TD, Number.MIN_VALUE], POSITIVE_INFINITY: [TD, Infinity], NEGATIVE_INFINITY: [TD, -Infinity], NaN: [TD, NaN] },
    Float: { MAX_VALUE: [TF, 3.4028234663852886e38], MIN_VALUE: [TF, 1.401298464324817e-45] },
    Math: { PI: [TD, Math.PI], E: [TD, Math.E] }
  };
  const JSTR = { int: 'length indexOf lastIndexOf compareTo compareToIgnoreCase hashCode codePointAt', char: 'charAt', bool: 'equals equalsIgnoreCase contains startsWith endsWith isEmpty isBlank matches',
    string: 'substring trim strip stripLeading stripTrailing toUpperCase toLowerCase replace replaceAll replaceFirst concat repeat intern toString formatted' };
  const JSCAN = { int: 'nextInt', long: 'nextLong', double: 'nextDouble', float: 'nextFloat', bool: 'nextBoolean hasNext hasNextInt hasNextLine hasNextDouble', short: 'nextShort', byte: 'nextByte', string: 'next nextLine' };
  const CSTATIC = {
    Math: { d: 'Sqrt Pow Floor Ceiling Log Log10 Log2 Exp Sin Cos Tan Asin Acos Atan Atan2 Cbrt Truncate', p: 'Abs Max Min' },
    int: { int: 'Parse' }, Int32: { int: 'Parse' }, long: { long: 'Parse' }, Int64: { long: 'Parse' }, double: { double: 'Parse' }, Double: { double: 'Parse' },
    Convert: { int: 'ToInt32', long: 'ToInt64', double: 'ToDouble', string: 'ToString', bool: 'ToBoolean', char: 'ToChar' },
    Console: { string: 'ReadLine', int: 'Read' },
    string: { string: 'Join Format Concat', bool: 'IsNullOrEmpty IsNullOrWhiteSpace', int: 'Compare' },
    String: { string: 'Join Format Concat', bool: 'IsNullOrEmpty IsNullOrWhiteSpace', int: 'Compare' },
    char: { bool: 'IsDigit IsLetter IsLetterOrDigit IsUpper IsLower IsWhiteSpace', char: 'ToUpper ToLower' }
  };
  const CCONST = {
    int: { MaxValue: [TI, 2147483647], MinValue: [TI, -2147483648] }, long: { MaxValue: [TL, 2n ** 63n - 1n], MinValue: [TL, -(2n ** 63n)] },
    double: { MaxValue: [TD, Number.MAX_VALUE], MinValue: [TD, -Number.MAX_VALUE] }, Math: { PI: [TD, Math.PI], E: [TD, Math.E] }
  };
  const CSTR = { int: 'IndexOf LastIndexOf CompareTo', bool: 'Contains StartsWith EndsWith Equals', string: 'ToUpper ToLower Trim TrimStart TrimEnd Substring Replace Insert Remove PadLeft PadRight ToString' };
  const table = o => { const m = {}; for (const k in o) for (const w of o[k].split(' ')) m[w] = k; return m; };
  const tables = o => { const m = {}; for (const k in o) m[k] = table(o[k]); return m; };
  const JS_ = tables(JSTATIC), CS_ = tables(CSTATIC), JSTR_ = table(JSTR), JSCAN_ = table(JSCAN), CSTR_ = table(CSTR);
  const tyOf = k => k === 'string' ? TS : T(k);

  /* classes a Java program must import before it can use them */
  const JPKG = {};
  Object.entries({
    'java.util': 'ArrayList LinkedList List Map HashMap TreeMap LinkedHashMap Set HashSet TreeSet LinkedHashSet Scanner Arrays Collections Queue Deque ArrayDeque PriorityQueue Stack Iterator Random Optional Objects StringJoiner Vector Comparator Collection Hashtable EnumSet EnumMap BitSet UUID ListIterator NoSuchElementException InputMismatchException ConcurrentModificationException OptionalInt SortedMap NavigableMap SortedSet',
    'java.util.function': 'Function BiFunction Supplier Consumer BiConsumer Predicate BiPredicate UnaryOperator BinaryOperator IntFunction IntPredicate IntUnaryOperator IntBinaryOperator ToIntFunction',
    'java.util.stream': 'Stream Collectors IntStream LongStream DoubleStream',
    'java.util.regex': 'Pattern Matcher',
    'java.io': 'File FileReader FileWriter BufferedReader BufferedWriter InputStreamReader PrintWriter IOException FileNotFoundException UncheckedIOException',
    'java.math': 'BigInteger BigDecimal RoundingMode',
    'java.time': 'LocalDate LocalDateTime LocalTime Duration Instant',
    'java.util.concurrent': 'ExecutorService Executors ConcurrentHashMap TimeUnit CompletableFuture',
    'java.util.concurrent.atomic': 'AtomicInteger AtomicLong',
    'java.nio.file': 'Files Paths'
  }).forEach(([pkg, names]) => names.split(' ').forEach(n => { JPKG[n] = pkg; }));

  /* names a program may use without declaring them */
  const CS_IMPLICIT = new Set(['value', 'args', 'field', '_', 'nameof', 'var', 'dynamic', 'await']);
  const J_IMPLICIT = new Set(['_', 'length']);
  /* C and C++ library names that a program uses as values without declaring them */
  const C_LIB = new Set(('cout cin cerr clog endl ends flush ws fixed scientific defaultfloat hexfloat setprecision setw setfill left right internal '
    + 'boolalpha noboolalpha showpos noshowpos showpoint noshowpoint showbase noshowbase uppercase nouppercase skipws noskipws unitbuf hex dec oct '
    + 'stdin stdout stderr errno environ optarg npos nothrow ignore piecewise_construct in out app binary trunc ate beg end cur '
    + 'toupper tolower isdigit isalpha isalnum isspace isupper islower ispunct isxdigit abs labs fabs sqrt pow exp log floor ceil round '
    + 'strcmp strlen printf scanf puts putchar getchar malloc free rand srand time exit max min swap greater less plus minus multiplies '
    + 'equal_to not_equal_to greater_equal less_equal logical_and logical_or negate modulus divides hash identity this '
    + 'numeric_limits pair tuple make_pair make_tuple tie get function accumulate count find distance next prev advance move forward ref cref '
    + 'back_inserter inserter istream_iterator ostream_iterator begin end size string vector map set').split(' '));

  class Checker {
    constructor(prog, lang, src) {
      this.prog = prog; this.lang = lang;
      this.J = lang === 'java'; this.C = lang === 'cs'; this.P = lang === 'cpp';
      this.scopes = [];
      this.cur = { cls: null, static: true, ret: null, lambda: 0, fn: null };
      this.notes = [];
      this.src = src || '';
      this.macros = new Set();
      for (const m of this.src.matchAll(/#\s*define\s+(\w+)/g)) this.macros.add(m[1]);
      for (const m of this.src.matchAll(/template\s*<([^>]*)>/g)) for (const w of m[1].match(/\w+/g) || []) this.macros.add(w);
      this.staticImport = /\bimport\s+static\b|\busing\s+static\b/.test(src || '');
      this.unres = false;
      this.cls = new Map();
      const add = (c, outer) => {
        const info = { c, name: c.name, outer, fields: new Map(), methods: new Map(), ctors: c.ctors || [], base: c.base, ifaces: c.ifaces || [] };
        (c.fields || []).forEach(f => { if (c.kind === 'interface' && !f.prop) { f.konst = true; f.static = true; } info.fields.set(f.id, f); });
        (c.recParams || []).forEach(p => { if (!info.fields.has(p.id)) info.fields.set(p.id, { ty: p.ty, id: p.id, static: false, konst: this.J, rec: true }); });
        (c.consts || []).forEach(k => info.fields.set(k.id, { ty: { n: c.name }, id: k.id, static: true, konst: true, enumConst: true }));
        (c.methods || []).forEach(m => { if (!info.methods.has(m.name)) info.methods.set(m.name, []); info.methods.get(m.name).push(m); });
        if (!this.cls.has(c.name)) this.cls.set(c.name, info);
        (c.nested || []).forEach(n => add(n, info));
      };
      (prog.classes || []).forEach(c => add(c, null));
      /* top level functions: Java compact source files, C# local functions next to top level statements, C and C++ functions */
      this.top = { c: { name: this.C ? 'Program' : 'Main' }, name: this.C ? 'Program' : 'Main', outer: null, fields: new Map(), methods: new Map(), ctors: [], base: null, ifaces: [], implicit: true };
      (prog.funcs || []).forEach(m => { if (!this.top.methods.has(m.name)) this.top.methods.set(m.name, []); this.top.methods.get(m.name).push(m); });
      for (const info of this.cls.values()) info.open = this.isOpen(info);
      this.names = new Set();
      this.collect(prog, new WeakSet());
      /* methods every class or enum has without writing them */
      (this.J ? 'values valueOf ordinal name toString equals hashCode getClass compareTo clone finalize wait notify notifyAll' : 'ToString Equals GetHashCode GetType MemberwiseClone').split(' ').forEach(n => this.names.add(n));
    }

    /* ---------- helpers ---------- */
    err(msg, line, hint) { const e = new CE(msg, line); if (hint) e.hint = hint; throw e; }
    isOpen(info, seen = new Set()) {
      /* a class that extends a library class may use names this checker cannot see */
      if (seen.has(info)) return false; seen.add(info);
      const bases = [info.base].concat(info.ifaces).filter(Boolean);
      for (const b of bases) {
        const bi = this.cls.get(b.n);
        if (!bi) { if (b === info.base && !/^(Object|object)$/.test(b.n)) return true; continue; }
        if (this.isOpen(bi, seen)) return true;
      }
      return info.outer ? this.isOpen(info.outer, seen) : false;
    }
    collect(o, seen) {
      if (!o || typeof o !== 'object' || seen.has(o)) return;
      seen.add(o);
      if (Array.isArray(o)) { o.forEach(x => this.collect(x, seen)); return; }
      if (o instanceof Set || o instanceof Map) return;
      if (o.k !== 'name' && o.k !== 'mem' && o.k !== 'mref') {
        for (const key of ['id', 'bind', 'name']) {
          const v = o[key];
          if (typeof v === 'string') this.names.add(v);
          else if (Array.isArray(v)) v.forEach(x => { if (typeof x === 'string') this.names.add(x); });
        }
      }
      for (const key in o) { const v = o[key]; if (v && typeof v === 'object') this.collect(v, seen); }
    }
    push() { this.scopes.push(new Map()); }
    pop() { this.scopes.pop(); }
    declare(id, info) { if (typeof id === 'string' && this.scopes.length) this.scopes[this.scopes.length - 1].set(id, info); }
    local(id) { for (let i = this.scopes.length - 1; i >= 0; i--) { const v = this.scopes[i].get(id); if (v) { this.foundAt = i; return v; } } return null; }
    chain(info) { const out = []; const seen = new Set(); let c = info; while (c && !seen.has(c)) { seen.add(c); out.push(c); c = c.base ? this.cls.get(c.base.n) : null; } return out; }
    field(info, id) {
      for (const c of this.chain(info)) {
        if (c.fields.has(id)) return { f: c.fields.get(id), owner: c };
        for (const i of c.ifaces) { const ii = this.cls.get(i.n); if (ii && ii.fields.has(id)) return { f: ii.fields.get(id), owner: ii }; }
      }
      return null;
    }
    methods(info, id) {
      let list = [];
      for (const c of this.chain(info)) {
        if (c.methods.has(id)) list = list.concat(c.methods.get(id));
        for (const i of c.ifaces) { const ii = this.cls.get(i.n); if (ii && ii.methods.has(id)) list = list.concat(ii.methods.get(id)); }
      }
      return list.length ? list : null;
    }
    topOf(info) { let c = info; while (c && c.outer) c = c.outer; return c; }
    closed(info) {
      if (!info || info.open) return false;
      for (const c of this.chain(info)) {
        if (c.base && !this.cls.has(c.base.n) && !/^(Object|object)$/.test(c.base.n)) return false;
        for (const i of c.ifaces) if (!this.cls.has(i.n)) return false;
      }
      return true;
    }
    isPrivate(mods, owner, member) {
      if (this.J) return !!(mods && mods.private);
      if (!this.C) return false;
      if (!owner.c || owner.c.kind === 'interface' || owner.c.kind === 'enum' || (member && (member.rec || member.enumConst))) return false;
      return !(mods && (mods.public || mods.internal || mods.protected));
    }
    access(mods, owner, member, what, line) {
      if (!(this.J || this.C) || !owner || owner.implicit || !this.isPrivate(mods, owner, member)) return;
      const cur = this.cur.cls;
      if (!cur || (owner.c && owner.c.local) || (cur.c && cur.c.local)) return;
      if (this.topOf(owner) === this.topOf(cur)) return;
      if (this.J) this.err(`${what} has private access in ${owner.name}`, line);
      this.err(`CS0122: '${what.includes('(') ? owner.name + '.' + what : owner.name + '.' + what}' is inaccessible due to its protection level`, line);
    }
    tn(t) { return this.J ? jName(t) : this.C ? cName(t) : pName(t); }
    sig(owner, m) { return (this.C ? owner.name + '.' : '') + m.name + '(' + m.params.map(p => this.tn(p.ty)).join(this.C ? ', ' : ',') + ')'; }

    /* ---------- the whole program ---------- */
    imports() {
      let toks;
      try { toks = CF.lex(this.src, 'java'); } catch (e) { return; }
      const have = new Set();
      const own = new Set(this.names);
      for (let i = 0; i < toks.length; i++) {
        if (toks[i].v !== 'import' || (i && toks[i - 1].v === '.')) continue;
        let j = i + 1, path = '';
        if (toks[j] && toks[j].v === 'static') { j++; path = 'static '; }
        while (j < toks.length && toks[j].v !== ';') path += toks[j++].v;
        have.add(path);
        i = j;
      }
      const stack = [];
      let depth = 0, pending = null;
      for (let i = 0; i < toks.length; i++) {
        const t = toks[i], v = t.v;
        if (t.t === 'id' && /^(class|interface|enum|record)$/.test(v) && toks[i + 1] && toks[i + 1].t === 'id' && !(i && toks[i - 1].v === '.')) {
          let name = toks[i + 1].v, k = i + 2;
          if (toks[k] && toks[k].v === '<') { let d = 0; for (; k < toks.length; k++) { name += toks[k].v === ',' ? ',' : toks[k].v; if (toks[k].v === '<') d++; else if (toks[k].v === '>' && !--d) break; } }
          pending = name;
        }
        if (v === '{' && t.t === 'op') { depth++; if (pending) { stack.push([depth, pending]); pending = null; } continue; }
        if (v === '}' && t.t === 'op') { if (stack.length && stack[stack.length - 1][0] === depth) stack.pop(); depth--; continue; }
        if (t.t !== 'id' || !JPKG[v] || own.has(v) || this.cls.has(v)) continue;
        if (i && (toks[i - 1].v === '.' || toks[i - 1].v === 'import')) continue;
        if (toks[i - 1] && toks[i - 1].v === '::') continue;
        const pkg = JPKG[v];
        if (have.has(pkg + '.*') || have.has(pkg + '.' + v)) continue;
        if ([...have].some(h => h.startsWith(pkg + '.' + v + '.'))) continue;
        const where = stack.length ? stack[stack.length - 1][1] : (this.prog.classes[0] ? this.prog.classes[0].name : 'Main');
        const e = new CE(`cannot find symbol\n  symbol:   class ${v}\n  location: class ${where}`, t.line);
        e.hint = `Java keeps ${v} in the package ${pkg}. Add this line at the very top of the program: import ${pkg}.${v};`;
        throw e;
      }
    }
    run() {
      const P = this.prog;
      if (this.J && !this.staticImport) this.imports();
      this.push();
      this.cur = { cls: this.top, static: !this.J, ret: null, lambda: 0, fn: null, topLevel: true };
      (P.globals || []).forEach(s => this.stmt(s));
      for (const info of new Set(this.cls.values())) this.checkClass(info);
      /* top level code */
      this.cur = { cls: this.top, static: !this.J, ret: null, lambda: 0, fn: null, topLevel: true };
      this.uninit = [];
      (P.top || []).forEach(s => this.stmt(s));
      this.uninitCheck();
      (P.funcs || []).forEach(m => this.method(this.top, m));
      this.pop();
      if (this.J || this.C) this.flowAll();
    }
    classRules(info) {
      const c = info.c, J = this.J, C = this.C;
      if (!(J || C)) return;
      if (J && !info.outer && !c.local && c.mods && (c.mods.private || c.mods.protected || c.mods.static)) this.err(`modifier ${c.mods.private ? 'private' : c.mods.protected ? 'protected' : 'static'} not allowed here`, c.line);
      const base = c.base && this.cls.get(c.base.n);
      if (base && base.c.mods && (J ? base.c.mods.final : base.c.mods.sealed) && base.c.kind === 'class') {
        if (J) this.err(`cannot inherit from final ${base.name}`, c.line);
        this.err(`CS0509: '${info.name}': cannot derive from sealed type '${base.name}'`, c.line);
      }
      (c.methods || []).concat((c.ctors || []).map(k => ({ params: k.params, line: k.line }))).forEach(m => {
        if (J && m.params.some((p, i) => p.ty && p.ty.varargs && i < m.params.length - 1)) this.err('varargs parameter must be the last parameter', m.line);
      });
      if (J && c.kind === 'class' && !(c.mods && c.mods.abstract) && !c.ctors.length && !(c.statics || []).length) {
        const f = (c.fields || []).find(f => f.konst && !f.static && !f.init && !f.prop && !f.rec && f.mods && f.mods.final);
        if (f) this.err(`variable ${f.id} not initialized in the default constructor`, f.line);
      }
      /* a class that is not abstract must write every abstract method it receives */
      if ((c.kind === 'class' || c.kind === 'record' || c.kind === 'struct') && !(c.mods && c.mods.abstract) && this.closed(info)) {
        const has = (name, n) => this.chain(info).some(k => (k.methods.get(name) || []).some(m => m.body && m.params.length === n && !m.abstract))
          || (n === 0 && (c.recParams || []).some(p => p.id === name)) || (C && n === 0 && this.chain(info).some(k => k.fields.has(name)));
        const seen = new Set();
        const need = [];
        const visitIface = (ii) => { if (!ii || seen.has(ii)) return; seen.add(ii); (ii.c.methods || []).forEach(m => { if (!m.body && !m.static && !(m.mods && (m.mods.default || m.mods.static))) need.push([ii, m, true]); }); ii.ifaces.forEach(x => visitIface(this.cls.get(x.n))); };
        for (const k of this.chain(info)) {
          k.ifaces.forEach(x => visitIface(this.cls.get(x.n)));
          if (k !== info && k.c.kind === 'interface') visitIface(k);
          if (k !== info && k.c.mods && k.c.mods.abstract) (k.c.methods || []).forEach(m => { if (m.abstract && !m.body) need.push([k, m, false]); });
        }
        if ((c.ifaces || []).some(x => (this.cls.get(x.n) || {}).c && this.cls.get(x.n).c.tps && this.cls.get(x.n).c.tps.length) && false) return;
        for (const [owner, m, iface] of need) {
          if (has(m.name, m.params.length)) continue;
          if (J) this.err(`${info.name} is not abstract and does not override abstract method ${this.sig(owner, m)} in ${owner.name}`, c.line);
          if (iface) this.err(`CS0535: '${info.name}' does not implement interface member '${this.sig(owner, m)}'`, c.line);
          this.err(`CS0534: '${info.name}' does not implement inherited abstract member '${this.sig(owner, m)}'`, c.line);
        }
      }
    }
    checkClass(info) {
      const c = info.c;
      this.classRules(info);
      this.push();
      (c.fields || []).forEach(f => {
        this.cur = { cls: info, static: !!f.static, ret: null, lambda: 0, fn: null };
        if (f.init) {
          if (f.init.k === 'arr') this.arrInit(f.ty, f.init);
          else this.assign(f.ty, this.ex(f.init), f.init.line || f.line, 'init', f.init);
        }
        if (f.prop) ['get', 'set'].forEach(a => {
          if (f.prop[a] && typeof f.prop[a] === 'object') {
            this.cur = { cls: info, static: !!f.static, ret: a === 'get' ? f.ty : T('void'), lambda: 0, fn: null, prop: true };
            this.push(); if (a === 'set') this.declare('value', { ty: f.ty }); this.stmt(f.prop[a]); this.pop();
          }
        });
      });
      (c.consts || []).forEach(k => { this.cur = { cls: info, static: true, ret: null, lambda: 0, fn: null }; (k.args || []).forEach(a => this.ex(a)); });
      (c.statics || []).forEach(b => { this.cur = { cls: info, static: false, ret: T('void'), lambda: 0, fn: null, init: true }; this.stmt(b); });
      (c.ctors || []).forEach(k => {
        if (!k.body) return;
        this.cur = { cls: info, static: false, ret: T('void'), lambda: 0, fn: null, ctor: true, ctorOf: k };
        this.push();
        this.captures = [];
        k.params.forEach(p => this.declare(p.id, { ty: p.ty, param: true, hasInit: true }));
        (k.init || []).forEach(i => (i.args || []).forEach(a => this.ex(a)));
        if (k.chain) (k.chain.args || []).forEach(a => this.ex(a));
        this.uninit = [];
        this.stmt(k.body);
        this.capturesCheck();
        this.uninitCheck();
        this.pop();
      });
      if (c.compact) { this.cur = { cls: info, static: false, ret: T('void'), lambda: 0, fn: null, ctor: true }; this.push(); (c.recParams || []).forEach(p => this.declare(p.id, { ty: p.ty })); this.stmt(c.compact); this.pop(); }
      (c.methods || []).forEach(m => this.method(info, m));
      this.pop();
    }
    method(info, m) {
      if (!m.body) return;
      const saved = this.cur;
      this.cur = { cls: info, static: !!m.static && !info.implicit || (info.implicit && this.C), ret: m.ret, lambda: 0, fn: m, async: !!(m.mods && m.mods.async) };
      this.push();
      const caps = this.captures, un = this.uninit; this.captures = []; this.uninit = [];
      m.params.forEach(p => { this.declare(p.id, { ty: p.ty, param: true, hasInit: true }); if (p.def) this.ex(p.def); });
      this.stmt(m.body);
      this.capturesCheck();
      this.uninitCheck();
      this.captures = caps; this.uninit = un;
      this.pop();
      this.cur = saved;
    }

    /* ---------- statements ---------- */
    stmt(s) {
      if (!s || typeof s !== 'object') return;
      switch (s.k) {
        case 'block': this.push(); s.body.forEach(x => this.stmt(x)); this.pop(); return;
        case 'decl': return this.decl(s);
        case 'expr': this.ex(s.e); return;
        case 'exprs': s.es.forEach(e => this.ex(e)); return;
        case 'if': this.condition(s.c); this.scoped(s.a); this.scoped(s.b); return;
        case 'while': this.condition(s.c); this.scoped(s.body); return;
        case 'do': this.scoped(s.body); this.condition(s.c); return;
        case 'for':
          this.push();
          if (s.init) this.stmt(s.init);
          if (s.c) this.condition(s.c);
          (s.upd || []).forEach(e => this.ex(e));
          this.scoped(s.body);
          this.pop(); return;
        case 'foreach': {
          this.push();
          const it = this.ex(s.it).t;
          const elem = it && it.dim ? Object.assign({}, it, { dim: it.dim - 1, cdims: undefined }) : (it && it.n === 'string' && this.C ? TC : null);
          if (Array.isArray(s.id)) s.id.forEach(id => this.declare(id, { ty: null }));
          else {
            const vt = !s.ty || s.ty.n === 'var' ? elem : s.ty;
            if (s.ty && s.ty.n !== 'var' && elem && (this.J || this.C)) this.assign(s.ty, { t: elem }, s.line, 'init', null);
            this.declare(s.id, { ty: vt, hasInit: true });
          }
          this.scoped(s.body);
          this.pop(); return;
        }
        case 'ret': return this.ret(s);
        case 'throw': if (s.e) this.ex(s.e); return;
        case 'yield': this.ex(s.e); return;
        case 'switch': {
          this.ex(s.e);
          this.push();
          s.cases.forEach(c => {
            (c.tests || []).forEach(t => { if (!t) return; if (t.k === 'pat') this.pattern(t.pat); else this.ex(t); });
            if (c.tests && c.tests.guard) this.ex(c.tests.guard);
            if (c.arrow) this.push();
            c.body.forEach(x => this.stmt(x));
            if (c.arrow) this.pop();
          });
          this.pop(); return;
        }
        case 'try':
          this.stmt(s.body);
          s.catches.forEach(c => { this.push(); if (c.id) this.declare(c.id, { ty: c.types[0] || null }); if (c.when) this.ex(c.when); this.stmt(c.body); this.pop(); });
          if (s.fin) this.stmt(s.fin);
          return;
        case 'localfn': {
          const m = s.m;
          if (!m) return; /* the reader keeps local functions with the top level functions */
          this.declare(m.name, { ty: null, fn: m });
          const saved = this.cur;
          this.cur = Object.assign({}, saved, { ret: m.ret, lambda: 0, fn: m, async: !!(m.mods && m.mods.async), static: saved.static || !!m.static });
          this.push(); m.params.forEach(p => this.declare(p.id, { ty: p.ty, param: true })); this.stmt(m.body); this.pop();
          this.cur = saved;
          return;
        }
        default: return;
      }
    }
    uninitCheck() {
      for (const l of this.uninit || []) {
        if (l.set || !l.reads.length) continue;
        if (this.J) this.err(`variable ${l.id} might not have been initialized`, l.reads[0]);
        this.err(`CS0165: Use of unassigned local variable '${l.id}'`, l.reads[0]);
      }
      this.uninit = [];
    }
    capturesCheck() {
      for (const c of this.captures || []) {
        const l = c.l;
        if (l.param && !l.assigned) continue;
        if ((l.hasInit && l.assigned) || l.assigned > 1) this.err('local variables referenced from a lambda expression must be final or effectively final', c.line);
      }
      this.captures = [];
    }
    scoped(s) { if (!s) return; this.push(); this.stmt(s); this.pop(); }
    pattern(p) {
      if (!p || typeof p !== 'object') return;
      if (p.bind) this.declare(p.bind, { ty: p.ty || null });
      if (p.e) this.ex(p.e);
      if (p.not) this.pattern(p.not);
      if (p.and) p.and.forEach(x => this.pattern(x));
      if (p.or) p.or.forEach(x => this.pattern(x));
    }
    decl(s) {
      for (const v of s.vars) {
        if (v.bind) { if (v.init) this.ex(v.init); v.bind.forEach(id => this.declare(id, { ty: null })); continue; }
        let vt = v.ty;
        let r = null;
        if (v.init) {
          if (vt && vt.n === 'var' && (this.J || this.C) && !s.deconstruct) {
            if (v.init.k === 'arr') { if (this.J) this.err(`cannot infer type for local variable ${v.id}\n  (array initializer needs an explicit target-type)`, s.line); }
            if (v.init.k === 'lit' && v.init.ty && v.init.ty.n === 'null') {
              if (this.J) this.err(`cannot infer type for local variable ${v.id}\n  (variable initializer is 'null')`, s.line);
              this.err('CS0815: Cannot assign <null> to an implicitly-typed variable', s.line);
            }
          }
          if (v.init.k === 'arr' && vt && vt.n !== 'var') {
            if (this.P && !vt.dim && !vt.cdims && v.init.items.length === 1 && v.init.items[0].k !== 'arr') this.cppNarrow(vt, v.init.items[0]);
            else this.arrInit(vt, v.init);
          } else {
            r = this.ex(v.init);
            if (vt && vt.n === 'var') vt = r.t && r.t.n !== 'null' ? r.t : null;
            else this.assign(vt, r, v.init.line || s.line, 'init', v.init);
          }
        }
        if (!v.init && !v.ctor && vt && vt.n === 'var' && (this.J || this.C) && !this.cur.field) {
          if (this.J) this.err(`cannot infer type for local variable ${v.id}\n  (cannot use 'var' on variable without initializer)`, s.line);
          this.err('CS0818: Implicitly-typed variables must be initialized', s.line);
        }
        if (this.P && v.brace && v.ctor && v.ctor.length === 1 && isPrim(vt) && v.ctor[0].k !== 'arr') this.cppNarrow(vt, v.ctor[0]);
        else if (v.ctor) v.ctor.forEach(a => { if (a && a.k) this.ex(a); });
        const konst = (this.J && s.final) || (this.C && s.isConst) || (this.P && (s.konst));
        let cv;
        if (konst && r && r.v !== undefined && (isPrim(vt) || isStr(vt))) cv = isNum(vt) ? conv(r.v, vt.n) : r.v;
        const info = { ty: vt, final: !!(this.J && s.final), konst: !!(this.C && s.isConst), hasInit: !!(v.init || v.ctor), cv, id: v.id };
        if (!info.hasInit && (this.J || this.C) && this.uninit && !(this.C && vt && this.cls.get(vt.n) && this.cls.get(vt.n).c.kind === 'struct')) { info.reads = []; this.uninit.push(info); }
        this.declare(v.id, info);
      }
    }
    arrInit(t, arr) {
      const elem = t && t.dim ? Object.assign({}, t, { dim: t.dim - 1, cdims: t.cdims ? t.cdims.slice(1) : undefined }) : null;
      for (const it of arr.items) {
        if (!it) continue;
        if (it.k === 'arr') { if (elem && elem.dim) this.arrInit(elem, it); else it.items.forEach(x => x && x.k && x.k !== 'arr' && this.ex(x)); continue; }
        if (it.k === 'desig') { this.ex(it.e); continue; }
        const r = this.ex(it);
        if (!elem) continue;
        if (this.P) { if (isPrim(elem)) this.cppNarrow(elem, it, r); }
        else this.assign(elem, r, it.line || arr.line, 'init', it);
      }
    }
    ret(s) {
      const c = this.cur;
      if (c.lambda || c.async || !c.ret || !(this.J || this.C)) { if (s.e) this.ex(s.e); return; }
      const rt = c.ret;
      if (rt.n === 'void' && !rt.ptr) {
        if (s.e) {
          this.ex(s.e);
          if (c.ctor || c.init || c.prop) return;
          if (this.J) this.err('incompatible types: unexpected return value', s.line);
          if (this.C && c.fn) this.err(`CS0127: Since '${this.sig(c.cls, c.fn)}' returns void, a return keyword must not be followed by an object expression`, s.line);
        }
        return;
      }
      if (!s.e) {
        if (c.ctor || c.init) return;
        if (this.J) this.err('incompatible types: missing return value', s.line);
        if (this.C && known(rt)) this.err(`CS0126: An object of a type convertible to '${cName(rt)}' is required`, s.line);
        return;
      }
      const r = this.ex(s.e);
      this.assign(rt, r, s.e.line || s.line, 'ret', s.e);
    }
    condition(e) {
      if (!e) return;
      const was = this.unres; this.unres = false;
      const r = this.ex(e);
      e.$cv = r.v; e.$sure = !this.unres;
      this.unres = was || this.unres;
      if ((this.J || this.C) && r.t && !isBool(r.t) && known(r.t) && !(r.t.box && r.t.n === 'bool')) {
        if (this.J) this.err(`incompatible types: ${jName(r.t)} cannot be converted to boolean`, e.line);
        this.err(`CS0029: Cannot implicitly convert type '${cName(r.t)}' to 'bool'`, e.line);
      }
      return r;
    }

    /* ---------- can a value of type st go into a variable of type tt? ---------- */
    assign(tt, r, line, ctx, node) {
      if (this.P && r && r.t && r.t.ptr && r.t.n === 'char' && node && node.k === 'lit' && typeof node.v === 'string' && isNum(tt) && ctx !== 'arg') this.err(`invalid conversion from 'const char*' to '${pName(tt)}' [-fpermissive]`, line);
      if (!r || !tt || !(this.J || this.C)) return;
      const st = r.t;
      if (!st) return;
      const msg = this.J ? this.jAssign(tt, st, r.v, ctx) : this.cAssign(tt, st, r.v, ctx, node);
      if (msg) this.err(msg, line);
    }
    arrMismatch(tt, st) {
      /* int[] and int, or int[] and double[]: both sides are plain types the checker knows */
      const base = t => Object.assign({}, t, { dim: 0 });
      if (!(tt.dim || st.dim) || tt.rank || st.rank || st.n === 'null' || tt.n === 'var' || tt.n === 'object' || tt.n === 'dyn') return false;
      if (!known(base(tt)) || !known(base(st)) || tt.box || st.box) return false;
      return (tt.dim || 0) !== (st.dim || 0) || ((tt.dim || 0) > 0 && tt.n !== st.n);
    }
    jAssign(tt, st, v, ctx) {
      if (this.arrMismatch(tt, st)) return `incompatible types: ${jName(st)} cannot be converted to ${jName(tt)}`;
      if (tt.dim || st.dim || tt.n === 'var' || tt.n === 'object' || tt.n === 'dyn' || st.n === 'null' || st.box) return null;
      if (!known(st)) return null;
      const bad = () => `incompatible types: ${jName(st)} cannot be converted to ${jName(tt)}`;
      if (tt.box) {
        if (tt.jn === 'Number' || tt.jn === 'Object') return null;
        if (st.n === tt.n) return null;
        if (isInt(st) && ['byte', 'short', 'char'].includes(tt.n) && ['byte', 'short', 'char', 'int'].includes(st.n) && ctx !== 'arg' && v !== undefined && fits(v, tt.n)) return null;
        return bad();
      }
      if (isBool(tt)) return isBool(st) ? null : bad();
      if (isStr(tt)) return isStr(st) ? null : bad();
      if (isNum(tt)) {
        if (!isNum(st)) return bad();
        if (st.n === tt.n || WJ[st.n] && WJ[st.n].has(tt.n)) return null;
        if (ctx !== 'arg' && v !== undefined && ['byte', 'short', 'char', 'int'].includes(st.n) && ['byte', 'short', 'char'].includes(tt.n) && fits(v, tt.n)) return null;
        return `incompatible types: possible lossy conversion from ${jName(st)} to ${jName(tt)}`;
      }
      return null;
    }
    cAssign(tt, st, v, ctx, node) {
      if (this.arrMismatch(tt, st) && !tt.nullable && !st.nullable && !tt.dec && !st.dec) return ctx === 'arg' ? `CS1503: Argument ${node && node.$argNo || 1}: cannot convert from '${cName(st)}' to '${cName(tt)}'` : `CS0029: Cannot implicitly convert type '${cName(st)}' to '${cName(tt)}'`;
      if (tt.dim || st.dim || tt.n === 'var' || tt.n === 'object' || tt.n === 'dyn' || tt.nullable || tt.dec || st.nullable || st.dec || st.n === 'null') return null;
      if (!known(st) || !known(tt)) return null;
      const arg = ctx === 'arg' ? ctx : null;
      const bad = () => arg ? `CS1503: Argument ${node && node.$argNo || 1}: cannot convert from '${cName(st)}' to '${cName(tt)}'` : `CS0029: Cannot implicitly convert type '${cName(st)}' to '${cName(tt)}'`;
      if (isBool(tt) || isBool(st) || isStr(tt) || isStr(st)) return (tt.n === st.n) ? null : bad();
      if (st.n === tt.n || (WC[st.n] && WC[st.n].has(tt.n))) return null;
      if (v !== undefined && st.n === 'int' && ['byte', 'ubyte', 'short', 'ushort', 'uint', 'ulong'].includes(tt.n) && fits(v, tt.n)) return null;
      if (v !== undefined && st.n === 'long' && tt.n === 'ulong' && fits(v, 'ulong')) return null;
      if (arg) return bad();
      if (v !== undefined && isInt(st) && isInt(tt) && (st.n === 'int' || st.n === 'long')) return `CS0031: Constant value '${String(v)}' cannot be converted to a '${cName(tt)}'`;
      if (node && node.k === 'lit' && st.n === 'double' && tt.n === 'float') return `CS0664: Literal of type double cannot be implicitly converted to type 'float'; use an 'F' suffix to create a literal of this type`;
      return `CS0266: Cannot implicitly convert type '${cName(st)}' to '${cName(tt)}'. An explicit conversion exists (are you missing a cast?)`;
    }

    /* C++ list initialisation int a{3.5} may not lose information */
    cppNarrow(tt, e, r) {
      r = r || this.ex(e);
      const st = r.t;
      if (!st || !isPrim(tt)) return;
      if (st.ptr && st.n === 'char' && e.k === 'lit' && typeof e.v === 'string' && NUMS.has(tt.n)) this.err(`invalid conversion from 'const char*' to '${pName(tt)}' [-fpermissive]`, e.line);
      if (!isNum(st) || !NUMS.has(tt.n) || st.n === tt.n) return;
      const v = r.v;
      const fl = n => n === 'float' || n === 'double';
      let narrow = false;
      if (fl(st.n) && INTS.has(tt.n)) narrow = true;
      else if (st.n === 'double' && tt.n === 'float') narrow = v === undefined || !(Math.abs(Number(v)) <= 3.4028234663852886e38 || !Number.isFinite(Number(v)));
      else if (INTS.has(st.n) && fl(tt.n)) narrow = v === undefined ? !(tt.n === 'double' && ['byte', 'ubyte', 'short', 'ushort', 'char', 'int', 'uint'].includes(st.n)) && !(tt.n === 'float' && ['byte', 'ubyte', 'short', 'ushort', 'char'].includes(st.n)) : Number(Math.fround(Number(v))) !== Number(v) && tt.n === 'float';
      else if (INTS.has(st.n) && INTS.has(tt.n)) {
        const rs = R[st.n], rt = R[tt.n === 'char' ? 'byte' : tt.n];
        narrow = v === undefined ? (rs[0] < rt[0] || rs[1] > rt[1]) : !fits(v, tt.n === 'char' ? 'byte' : tt.n);
      }
      if (!narrow) return;
      const text = v !== undefined ? this.cppVal(v, st) : (e.k === 'name' ? e.id : null);
      if (v !== undefined) this.err(`narrowing conversion of '${text}' from '${pName(st)}' to '${pName(tt)}' [-Wnarrowing]`, e.line);
      if (text) this.notes.push(`main.cpp:${e.line}: warning: narrowing conversion of '${text}' from '${pName(st)}' to '${pName(tt)}' [-Wnarrowing]. The value may not fit, so g++ warns about it.`);
    }
    cppVal(v, t) {
      if (t.n === 'double' || t.n === 'float') {
        let s = Number(v).toExponential();
        s = s.replace(/^(-?\d)e/, '$1.0e');
        return s + (t.n === 'float' ? 'f' : '');
      }
      return String(v);
    }

    /* ---------- expressions: returns { t: type or null, v: constant value or undefined } ---------- */
    ex(e) {
      const U = { t: null };
      if (!e || typeof e !== 'object') return U;
      const J = this.J, C = this.C;
      switch (e.k) {
        case 'lit': return this.lit(e);
        case 'paren': return this.ex(e.a);
        case 'name': return this.name(e);
        case 'this':
          if ((J || C) && this.cur.static && !this.cur.lambda && this.cur.cls && !this.cur.cls.implicit && !this.cur.topLevel) {
            if (J) this.err('non-static variable this cannot be referenced from a static context', e.line);
            this.err(`CS0026: Keyword 'this' is not valid in a static property, static method, or static field initializer`, e.line);
          }
          return { t: this.cur.cls ? { n: this.cur.cls.name } : null };
        case 'istr': (e.parts || []).forEach(p => { if (p && typeof p === 'object') this.ex(p.e); }); return { t: TS };
        case 'bin': return this.bin(e);
        case 'un': return this.un(e);
        case 'pre': case 'post': {
          this.finalCheck(e.a);
          if (e.a && e.a.k === 'name') this.capAssign(e.a);
          const r = this.ex(e.a);
          if (J && r.t && (isBool(r.t) || isStr(r.t))) this.err(`bad operand type ${jName(r.t)} for unary operator '${e.op}'`, e.line);
          return { t: r.t };
        }
        case 'asg': return this.asg(e);
        case 'cast': return this.cast(e);
        case 'cond': {
          const c = this.condition(e.c);
          const a = this.ex(e.a), b = this.ex(e.b);
          let t = null;
          if (a.t && b.t) {
            if (isNum(a.t) && isNum(b.t)) {
              if (a.t.n === b.t.n) t = a.t;
              else if (J && ['byte', 'short', 'char'].includes(a.t.n) && b.t.n === 'int' && b.v !== undefined && fits(b.v, a.t.n)) t = a.t;
              else if (J && ['byte', 'short', 'char'].includes(b.t.n) && a.t.n === 'int' && a.v !== undefined && fits(a.v, b.t.n)) t = b.t;
              else t = promote(this.lang, a.t, b.t);
            } else if (isBool(a.t) && isBool(b.t)) t = TB;
            else if (isStr(a.t) && isStr(b.t)) t = TS;
          }
          let v;
          if (c && c.v !== undefined && t) v = c.v ? conv(a.v, t.n) : conv(b.v, t.n);
          return { t, v };
        }
        case 'call': return this.call(e);
        case 'mem': return this.mem(e, false);
        case 'idx': return this.idx(e);
        case 'new': {
          (e.args || []).forEach(a => this.ex(a));
          (e.init || []).forEach(i => { if (i.e) this.ex(i.e); if (i.key) this.ex(i.key); if (i.add) i.add.forEach(a => this.ex(a)); });
          if (e.tt && !e.anon) this.ctorCheck(e);
          return { t: e.tt && e.tt.n !== 'anon' ? e.tt : null };
        }
        case 'newarr': {
          (e.dims || []).forEach(d => { if (d) this.ex(d); });
          const t = e.tt ? Object.assign({}, e.tt, { dim: (e.tt.dim || 0) + (e.tt.rank ? 1 : (e.dims ? e.dims.length : 1)) }) : null;
          if (e.init && t && t.n !== 'var') this.arrInit(t, e.init); else if (e.init) this.ex(e.init);
          return { t: t && t.n !== 'var' ? t : null };
        }
        case 'arr': (e.items || []).forEach(x => this.ex(x)); return U;
        case 'inst': this.ex(e.a); if (e.bind) this.declare(e.bind, { ty: e.tt }); if (e.tt && typeof e.tt === 'object' && !e.tt.n) this.pattern(e.tt); return { t: TB };
        case 'as': this.ex(e.a); return { t: e.tt || null };
        case 'lam': {
          const saved = this.cur;
          this.cur = Object.assign({}, saved, { lambda: saved.lambda + 1, lamScope: saved.lambda ? saved.lamScope : this.scopes.length });
          this.push();
          (e.params || []).forEach(p => this.declare(p.id, { ty: p.ty && p.ty.n !== 'var' ? p.ty : null }));
          if (e.exprBody) this.ex(e.body); else this.stmt(e.body);
          this.pop();
          this.cur = saved;
          return U;
        }
        case 'swx': {
          this.ex(e.e);
          if (e.arms) e.arms.forEach(a => { this.push(); this.pattern(a.pat); if (a.guard) this.ex(a.guard); this.ex(a.e); this.pop(); });
          if (e.cases) {
            const saved = this.cur;
            this.cur = Object.assign({}, saved, { lambda: saved.lambda + 1 });
            this.push();
            e.cases.forEach(c => {
              (c.tests || []).forEach(t => { if (!t) return; if (t.k === 'pat') this.pattern(t.pat); else this.ex(t); });
              if (c.tests && c.tests.guard) this.ex(c.tests.guard);
              this.push(); c.body.forEach(x => this.stmt(x)); this.pop();
            });
            this.pop();
            this.cur = saved;
          }
          return U;
        }
        case 'outdecl': this.declare(e.id, { ty: e.tt && e.tt.n !== 'var' ? e.tt : null }); return U;
        case 'refarg': if (e.kind === 'out' && e.a && e.a.k === 'name') { e.a.$write = true; const l = this.local(e.a.id); if (l) l.set = true; } return this.ex(e.a);
        case 'tuple': e.items.forEach(x => this.ex(x)); return U;
        case 'with': this.ex(e.o); (e.init || []).forEach(i => i.e && this.ex(i.e)); return U;
        case 'mref': if (e.o && e.o.k !== 'name') this.ex(e.o); return U;
        case 'sizeof': if (e.a) this.ex(e.a); return { t: T('ulong') };
        case 'throwx': case 'deref': case 'addr': case 'delete': if (e.a) this.ex(e.a); return U;
        default:
          for (const key in e) { const v = e[key]; if (v && typeof v === 'object' && v.k) this.ex(v); }
          return U;
      }
    }
    lit(e) {
      if (e.num === undefined) {
        if (e.ty && e.ty.n === 'string') return { t: (this.P || this.lang === 'c') ? { n: 'char', ptr: 1 } : TS, v: e.v };
        if (e.ty && e.ty.n === 'char') return { t: TC, v: e.v };
        if (e.ty && e.ty.n === 'bool') return { t: TB, v: e.v };
        if (e.ty && e.ty.n === 'null') return { t: T('null') };
        return { t: null };
      }
      if (e.dec) return { t: { n: 'double', dec: true } };
      const t = e.num;
      switch (e.kind) {
        case 'int': {
          let b; try { b = BigInt(t); } catch (x) { return { t: null }; }
          const radix = /^0[xbo]/i.test(t);
          if (this.J) {
            if (!radix && b > 2147483647n) this.err('integer number too large', e.line, `An int stops at 2147483647. Write ${t}L, with an L at the end, to make it a long number.`);
            return { t: TI, v: Number(BigInt.asIntN(32, b)) };
          }
          if (this.C) {
            if (b <= 2147483647n) return { t: TI, v: Number(b) };
            if (b <= 4294967295n) return { t: T('uint'), v: Number(b) };
            if (b <= 2n ** 63n - 1n) return { t: TL, v: b };
            return { t: T('ulong'), v: b };
          }
          if (b > 2147483647n) return { t: TL, v: b };
          return { t: TI, v: Number(b) };
        }
        case 'uint': try { return { t: T('uint'), v: Number(BigInt.asUintN(32, BigInt(t))) }; } catch (x) { return { t: T('uint') }; }
        case 'long': try { return { t: TL, v: BigInt.asIntN(64, BigInt(t)) }; } catch (x) { return { t: TL }; }
        case 'ulong': try { return { t: T('ulong'), v: BigInt.asUintN(64, BigInt(t)) }; } catch (x) { return { t: T('ulong') }; }
        case 'float': return { t: TF, v: Math.fround(parseFloat(t)) };
        default: return { t: TD, v: /^0x/i.test(t) ? parseInt(t, 16) : parseFloat(t) };
      }
    }
    name(e) {
      const id = e.id;
      const l = this.local(id);
      if (l) {
        /* a lambda may only use local variables that never change after they get their value (Java) */
        if (this.J && this.cur.lambda && this.foundAt < this.cur.lamScope && !l.fn && this.captures) this.captures.push({ l, id, line: e.line });
        if (l.reads && !e.$write) l.reads.push(e.line);
        return { t: l.fn ? null : l.ty, v: l.cv };
      }
      const cur = this.cur.cls;
      if (cur) {
        const f = this.field(cur, id);
        if (f) {
          if ((this.J || this.C) && this.cur.static && !f.f.static && !(this.C && f.f.konst) && !cur.implicit && !this.cur.topLevel) {
            if (this.J) this.err(`non-static variable ${id} cannot be referenced from a static context`, e.line);
            this.err(`CS0120: An object reference is required for the non-static field, method, or property '${f.owner.name}.${id}'`, e.line);
          }
          return { t: f.f.ty, v: this.fieldConst(f.f, f.owner) };
        }
        for (let o = cur.outer; o; o = o.outer) { const g = this.field(o, id); if (g) return { t: g.f.ty, v: this.fieldConst(g.f, g.owner) }; }
      }
      if (this.top.methods.has(id) || this.cls.has(id)) { return { t: null }; }
      this.unres = true;
      this.notFound(e);
      return { t: null };
    }
    fieldConst(f, owner) {
      if (f.$cv !== undefined) return f.$cv === null ? undefined : f.$cv;
      f.$cv = null;
      const isConst = this.J ? f.konst && !f.prop : this.C ? f.konst : false;
      if (!isConst || !f.init || !(isPrim(f.ty) || isStr(f.ty)) || f.init.k === 'arr') return undefined;
      const saved = this.cur, savedScopes = this.scopes, savedUnres = this.unres;
      this.cur = { cls: owner, static: true, ret: null, lambda: 0, fn: null };
      this.scopes = [new Map()];
      let r;
      try { r = this.ex(f.init); } finally { this.cur = saved; this.scopes = savedScopes; this.unres = savedUnres; }
      const v = r && r.v !== undefined ? (isNum(f.ty) ? conv(r.v, f.ty.n) : r.v) : undefined;
      f.$cv = v === undefined ? null : v;
      return v;
    }
    notFound(e) {
      if (this.P || this.lang === 'c') {
        const id = e.id;
        if (!lower(id) || this.names.has(id) || C_LIB.has(id) || this.macros.has(id) || /^_/.test(id) || /^(int|long|short|char|double|float|bool|void|unsigned|signed|auto|size_t|wchar_t|int\d+_t|uint\d+_t)$/.test(id)) return;
        for (let c = this.cur.cls; c; c = c.outer) if (c.open) return;
        if (this.cur.cls && !this.cur.cls.implicit && this.cur.cls.c.tps && this.cur.cls.c.tps.length) return;
        if (this.P) this.err(`'${id}' was not declared in this scope`, e.line);
        this.err(`'${id}' undeclared (first use in this function)`, e.line);
      }
      if (!(this.J || this.C) || this.staticImport) return;
      const id = e.id;
      if (!lower(id) || this.names.has(id) || (this.C ? CS_IMPLICIT : J_IMPLICIT).has(id)) return;
      if (/^(int|long|short|byte|sbyte|char|bool|boolean|float|double|decimal|string|object|uint|ulong|ushort|var|dynamic|nint)$/.test(id)) return;
      for (let c = this.cur.cls; c; c = c.outer) if (c.open) return;
      if (this.J) this.err(`cannot find symbol\n  symbol:   variable ${id}\n  location: class ${this.cur.cls ? this.cur.cls.name : 'Main'}`, e.line);
      this.err(`CS0103: The name '${id}' does not exist in the current context`, e.line);
    }
    finalCheck(a) {
      if (!a || a.k !== 'name') return;
      const l = this.local(a.id);
      if (l) {
        l.assigned = (l.assigned || 0) + 1;
        if (this.J && l.final && l.hasInit) this.err(`cannot assign a value to final variable ${a.id}`, a.line);
        if (this.C && l.konst) this.err(`CS0131: The left-hand side of an assignment must be a variable, property or indexer`, a.line);
        return;
      }
      const cur = this.cur.cls;
      if (!cur) return;
      const f = this.field(cur, a.id);
      if (!f) return;
      if (this.J && f.f.konst && !f.f.prop && (f.f.init || !(this.cur.ctor || this.cur.init))) this.err(`cannot assign a value to ${f.f.static ? 'static ' : ''}final variable ${a.id}`, a.line);
      if (this.C && f.f.konst && !f.f.prop) this.err(`CS0131: The left-hand side of an assignment must be a variable, property or indexer`, a.line);
    }
    capAssign(a) {
      /* changing a captured local inside the lambda itself */
      if (!this.J || !this.cur.lambda) return;
      const l = this.local(a.id);
      if (l && this.foundAt < this.cur.lamScope && !l.fn) this.err('local variables referenced from a lambda expression must be final or effectively final', a.line);
    }
    asg(e) {
      this.finalCheck(e.a);
      if (e.a && e.a.k === 'name') {
        this.capAssign(e.a);
        if (e.op === '=') { e.a.$write = true; const l = this.local(e.a.id); if (l) l.set = true; }
      }
      const l = e.a && e.a.k === 'tuple' ? (e.a.items.forEach(x => this.ex(x)), { t: null }) : this.ex(e.a);
      const r = this.ex(e.b);
      if (e.op === '=' && l.t) this.assign(l.t, r, e.b.line || e.line, 'asg', e.b);
      return { t: l.t };
    }
    cast(e) {
      const r = this.ex(e.a);
      const tt = e.tt;
      if ((this.J || this.C) && r.t && tt && !tt.dim && known(r.t)) {
        const tn = tt.n;
        const numT = NUMS.has(tn) && !tt.box, boolT = tn === 'bool' && !tt.box;
        const bad = (isStr(r.t) && (numT || boolT)) || (isBool(r.t) && numT) || (isNum(r.t) && boolT) || (isNum(r.t) && !r.t.box && tn === 'string');
        if (bad) {
          if (this.J) this.err(`incompatible types: ${jName(r.t)} cannot be converted to ${jName(tt)}`, e.line);
          if (!tt.dec) this.err(`CS0030: Cannot convert type '${cName(r.t)}' to '${cName(tt)}'`, e.line);
        }
      }
      if (!tt) return { t: null };
      const v = r.v !== undefined && isPrim(tt) && NUMS.has(tt.n) && (typeof r.v === 'number' || typeof r.v === 'bigint') ? conv(r.v, tt.n) : (isStr(tt) && typeof r.v === 'string' ? r.v : undefined);
      return { t: tt, v };
    }
    un(e) {
      if (e.op === '-' && e.a && e.a.k === 'lit' && e.a.kind === 'int' && e.a.num === '2147483648') return { t: TI, v: -2147483648 };
      const r = this.ex(e.a);
      const t = r.t;
      if (e.op === '!') {
        if ((this.J || this.C) && t && known(t) && !isBool(t) && !(t.box && t.n === 'bool')) {
          if (this.J) this.err(`bad operand type ${jName(t)} for unary operator '!'`, e.line);
          this.err(`CS0023: Operator '!' cannot be applied to operand of type '${cName(t)}'`, e.line);
        }
        return { t: TB, v: typeof r.v === 'boolean' ? !r.v : undefined };
      }
      if (!t) return { t: null };
      if (this.J && (isBool(t) || isStr(t))) this.err(`bad operand type ${jName(t)} for unary operator '${e.op}'`, e.line);
      if (!isNum(t)) return { t: null };
      if (this.C && e.op === '-' && t.n === 'uint') return { t: TL, v: r.v !== undefined ? -BigInt(r.v) : undefined };
      if (this.C && e.op === '-' && t.n === 'ulong') return { t: null };
      const pt = unary(t);
      let v;
      if (r.v !== undefined) {
        if (e.op === '-') v = typeof r.v === 'bigint' ? conv(-r.v, pt.n) : (INTS.has(pt.n) ? conv(-r.v, pt.n) : -r.v);
        else if (e.op === '+') v = r.v;
        else if (e.op === '~' && INTS.has(pt.n)) v = conv(~BigInt(r.v), pt.n);
      }
      return { t: pt, v };
    }
    bin(e) {
      const op = e.op;
      if (op === '??') { const a = this.ex(e.a), b = this.ex(e.b); return { t: b.t && a.t && a.t.n === b.t.n ? b.t : null }; }
      const a = this.ex(e.a), b = this.ex(e.b);
      const at = a.t, bt = b.t;
      const JC = this.J || this.C;
      const fail = () => {
        if (this.J) this.err(`bad operand types for binary operator '${op}'\n  first type:  ${jName(at)}\n  second type: ${jName(bt)}`, e.line);
        this.err(`CS0019: Operator '${op}' cannot be applied to operands of type '${cName(at)}' and '${cName(bt)}'`, e.line);
      };
      const both = at && bt && known(at) && known(bt);
      const numA = at && isNum(at), numB = bt && isNum(bt);
      if (op === '&&' || op === '||') {
        if (JC && both && !(isBool(at) && isBool(bt))) fail();
        return { t: TB, v: fold(op, a.v, b.v, TB) };
      }
      if (op === '==' || op === '!=') {
        if (JC && both) {
          if (this.J && ((isBool(at) && numA === false && numB) || (isBool(bt) && numA))) this.err(`incomparable types: ${jName(at)} and ${jName(bt)}`, e.line);
          if ((isStr(at) !== isStr(bt)) || (isBool(at) !== isBool(bt) && !at.box && !bt.box)) fail();
        }
        return { t: TB, v: both && !isStr(at) ? fold(op, a.v, b.v, at.n === bt.n ? at : (numA && numB ? promote(this.lang, at, bt) : TB)) : undefined };
      }
      if (['<', '>', '<=', '>='].includes(op)) {
        if (JC && both && !(numA && numB)) fail();
        return { t: TB, v: numA && numB ? fold(op, a.v, b.v, promote(this.lang, at, bt) || TD) : undefined };
      }
      if (op === '+' && ((at && isStr(at)) || (bt && isStr(bt)))) {
        if (this.P && at && bt && at.ptr && bt.ptr) return { t: null };
        return { t: (this.J || this.C) ? TS : (isStr(at) || isStr(bt) ? TS : null) };
      }
      if (this.P || this.lang === 'c') {
        if (op === '+' || op === '-') { if ((at && at.ptr) || (bt && bt.ptr)) return { t: null }; }
      }
      if (['&', '|', '^'].includes(op) && at && bt && isBool(at) && isBool(bt)) return { t: TB, v: fold(op, a.v, b.v, TB) };
      if (JC && both && !(numA && numB)) fail();
      if (!(numA && numB)) return { t: null };
      if (['<<', '>>', '>>>'].includes(op)) {
        if (JC && (!INTS.has(at.n) || !INTS.has(bt.n))) fail();
        const pt = unary(at);
        return { t: pt, v: op === '>>>' ? undefined : fold(op, a.v, b.v, pt) };
      }
      if (['&', '|', '^', '%'].includes(op) && op !== '%' && JC && (!INTS.has(at.n) || !INTS.has(bt.n))) fail();
      const pt = promote(this.lang, at, bt);
      if (!pt) return { t: null };
      return { t: pt, v: fold(op, a.v, b.v, pt) };
    }
    staticClass(o) {
      /* o names a class (not a variable): Math, Integer, a class of the program */
      if (!o || o.k !== 'name' || this.local(o.id)) return null;
      if (this.cur.cls && this.field(this.cur.cls, o.id)) return null;
      return o.id;
    }
    mem(e, called) {
      const J = this.J, C = this.C;
      const sc = this.staticClass(e.o);
      if (sc) {
        const consts = J ? JCONST : C ? CCONST : null;
        if (consts && consts[sc] && consts[sc][e.id]) { const [t, v] = consts[sc][e.id]; return { t, v }; }
        const info = this.cls.get(sc);
        if (info) {
          const f = this.field(info, e.id);
          if (f) {
            this.access(f.f.mods, f.owner, f.f, e.id, e.line);
            if ((J || C) && !f.f.static && !(C && f.f.konst) && !called && !(this.cur.cls && this.chain(this.cur.cls).includes(info) && !this.cur.static)) {
              if (J) this.err(`non-static variable ${e.id} cannot be referenced from a static context`, e.line);
              this.err(`CS0120: An object reference is required for the non-static field, method, or property '${f.owner.name}.${e.id}'`, e.line);
            }
            return { t: f.f.ty, v: this.fieldConst(f.f, f.owner) };
          }
          if (!called && this.closed(info) && !this.methods(info, e.id) && !(info.c.nested || []).some(n => n.name === e.id) && !/^(this|class|super|length|new)$/.test(e.id) && !this.staticImport) this.missing('variable', e.id, null, info, e);
        }
        return { t: null };
      }
      const r = e.o && e.o.k === 'this' ? this.ex(e.o) : this.ex(e.o);
      const t = r.t;
      if (!t) return { t: null };
      if (J && e.id === 'length') {
        if (t.dim) return { t: TI };
        if (isStr(t) && !called && e.o.k === 'name') this.err(`cannot find symbol\n  symbol:   variable length\n  location: variable ${e.o.id} of type String`, e.line);
      }
      if (C && e.id === 'Length' && (t.dim || isStr(t))) return { t: TI };
      if (C && e.id === 'Count' && /^(List|Dictionary|HashSet|Queue|Stack|SortedSet|SortedDictionary|LinkedList)$/.test(t.n) && !t.dim) return { t: TI };
      if (!t.dim && !t.ptr) {
        const info = this.cls.get(t.n);
        if (info) {
          const f = this.field(info, e.id);
          if (f) { this.access(f.f.mods, f.owner, f.f, e.id, e.line); return { t: f.f.ty }; }
          if (!called && (this.J || this.C) && this.closed(info) && !this.methods(info, e.id) && !(info.c.nested || []).some(n => n.name === e.id) && e.id !== 'length') this.missing('variable', e.id, e.o, info, e);
        }
      }
      return { t: null };
    }
    missing(kind, id, o, info, e, args) {
      if (!(this.J || this.C)) return;
      if (kind === 'method' && /^(values|valueOf|ordinal|name|toString|equals|hashCode|getClass|compareTo|clone|finalize|wait|notify|notifyAll|describeConstable|getDeclaringClass|ToString|Equals|GetHashCode|GetType|MemberwiseClone|CompareTo|HasFlag)$/.test(id)) return;
      if (kind === 'method' && info.c.recParams && info.c.recParams.some(p => p.id === id)) return;
      const sym = kind === 'method' ? `method ${id}(${(args || []).map(a => jName(a.t)).join(',')})` : `variable ${id}`;
      if (this.J) {
        const loc = o && o.k === 'name' ? `variable ${o.id} of type ${jName(this.local(o.id) ? this.local(o.id).ty : { n: info.name })}` : `class ${info.name}`;
        this.err(`cannot find symbol\n  symbol:   ${sym}\n  location: ${loc}`, e.line);
      }
      if (o) this.err(`CS1061: '${info.name}' does not contain a definition for '${id}' and no accessible extension method '${id}' accepting a first argument of type '${info.name}' could be found (are you missing a using directive or an assembly reference?)`, e.line);
      this.err(`CS0117: '${info.name}' does not contain a definition for '${id}'`, e.line);
    }
    idx(e) {
      const o = this.ex(e.o), i = this.ex(e.i);
      (e.i2 || []).forEach(x => this.ex(x));
      const t = o.t;
      if (this.J && t && isStr(t)) this.err('array required, but String found', e.line);
      if (this.J && t && t.dim && i.t && isNum(i.t) && !['byte', 'short', 'char', 'int'].includes(i.t.n)) this.err(`incompatible types: possible lossy conversion from ${jName(i.t)} to int`, e.i.line || e.line);
      if (t && t.dim) return { t: Object.assign({}, t, { dim: t.dim - (1 + (e.i2 ? e.i2.length : 0) * 0), cdims: undefined }) };
      if (t && t.ptr && (this.P || this.lang === 'c')) return { t: Object.assign({}, t, { ptr: t.ptr - 1 }) };
      if (this.C && t && isStr(t)) return { t: TC };
      if ((this.P) && t && isStr(t)) return { t: TC };
      return { t: null };
    }
    args(e) {
      return (e.args || []).map((a, i) => { const r = this.ex(a); if (a && typeof a === 'object') a.$argNo = i + 1; return r; });
    }
    call(e) {
      const J = this.J, C = this.C;
      const f = e.f;
      if (!f) return { t: null };
      if (f.k === 'name') {
        const args = this.args(e);
        const l = this.local(f.id);
        if (l) { if (l.fn) return this.checkArgs(e, [l.fn], args, this.cur.cls, f.id, false); return { t: null }; }
        const cur = this.cur.cls;
        let list = cur ? this.methods(cur, f.id) : null, owner = cur;
        if (list && (J || C) && this.cur.static && !this.cur.topLevel && !cur.implicit && list.every(m => !m.static)) {
          const m = list.find(x => x.params.length === args.length) || list[0];
          if (J) this.err(`non-static method ${this.sig(cur, m)} cannot be referenced from a static context`, e.line);
          this.err(`CS0120: An object reference is required for the non-static field, method, or property '${this.sig(cur, m)}'`, e.line);
        }
        if (!list && cur) for (let o = cur.outer; o && !list; o = o.outer) { list = this.methods(o, f.id); owner = o; }
        if (!list && this.top.methods.has(f.id)) { list = this.top.methods.get(f.id); owner = this.top; }
        if (!list) {
          if ((J || C) && !this.staticImport && !this.names.has(f.id) && !(J && /^(super|this)$/.test(f.id)) && !(C && CS_IMPLICIT.has(f.id))) {
            let open = false; for (let c = cur; c; c = c.outer) if (c.open) open = true;
            if (!open) {
              if (J) this.err(`cannot find symbol\n  symbol:   method ${f.id}(${args.map(a => jName(a.t)).join(',')})\n  location: class ${cur ? cur.name : 'Main'}`, e.line);
              this.err(`CS0103: The name '${f.id}' does not exist in the current context`, e.line);
            }
          }
          return { t: null };
        }
        return this.checkArgs(e, list, args, owner, f.id, true);
      }
      if (f.k === 'mem') {
        const sc = this.staticClass(f.o);
        if (sc) {
          const args = this.args(e);
          const info = this.cls.get(sc);
          if (info) {
            const list = this.methods(info, f.id);
            if (list && list.every(m => !m.static) && (J || C) && !(this.cur.cls && this.chain(this.cur.cls).includes(info) && !this.cur.static)) {
              const m = list.find(x => x.params.length === args.length) || list[0];
              if (J) this.err(`non-static method ${this.sig(info, m)} cannot be referenced from a static context`, e.line);
              this.err(`CS0120: An object reference is required for the non-static field, method, or property '${this.sig(info, m)}'`, e.line);
            }
            if (list) return this.checkArgs(e, list, args, info, f.id, true);
            if (this.closed(info) && !this.staticImport && !(this.C && info.fields.has(f.id))) this.missing('method', f.id, null, info, e, args);
            return { t: null };
          }
          const lib = (J ? JS_ : C ? CS_ : {})[sc];
          if (lib && lib[f.id]) return { t: this.libRet(lib[f.id], f.id, args, sc) };
          return { t: null };
        }
        const isSuper = f.o && (f.o.k === 'super' || (f.o.k === 'name' && f.o.id === 'base'));
        const r = isSuper ? { t: null } : this.ex(f.o);
        const args = this.args(e);
        const t = r.t;
        if (!t) {
          if (f.id === 'toString' || f.id === 'ToString') return { t: TS };
          return { t: null };
        }
        if (J && f.id === 'length' && t.dim && f.o.k === 'name') this.err(`cannot find symbol\n  symbol:   method length()\n  location: variable ${f.o.id} of type ${jName(t)}`, e.line);
        if (C && f.id === 'Length' && (t.dim || isStr(t))) this.err(`CS1955: Non-invocable member '${isStr(t) ? 'string' : 'Array'}.Length' cannot be used like a method.`, e.line);
        if (J && isStr(t) && JSTR_[f.id]) return { t: tyOf(JSTR_[f.id]) };
        if (J && isStr(t) && f.id === 'split') return { t: { n: 'string', dim: 1 } };
        if (J && isStr(t) && f.id === 'toCharArray') return { t: { n: 'char', dim: 1 } };
        if (C && isStr(t) && CSTR_[f.id]) return { t: tyOf(CSTR_[f.id]) };
        if (C && isStr(t) && f.id === 'Split') return { t: { n: 'string', dim: 1 } };
        if (C && isStr(t) && f.id === 'ToCharArray') return { t: { n: 'char', dim: 1 } };
        if (J && t.n === 'Scanner' && JSCAN_[f.id]) return { t: tyOf(JSCAN_[f.id]) };
        if (J && f.id === 'size' && /^(List|ArrayList|LinkedList|Map|HashMap|TreeMap|LinkedHashMap|Set|HashSet|TreeSet|LinkedHashSet|Deque|ArrayDeque|Queue|PriorityQueue|Stack|Vector|Collection)$/.test(t.n)) return { t: TI };
        if (f.id === 'toString' || f.id === 'ToString') return { t: TS };
        if (!t.dim && !t.ptr) {
          const info = this.cls.get(t.n);
          if (info && !info.open) {
            const list = this.methods(info, f.id);
            if (list) return this.checkArgs(e, list, args, info, f.id, false);
            if (this.closed(info) && !(this.C && info.fields.has(f.id))) this.missing('method', f.id, f.o, info, e, args);
          }
        }
        return { t: null };
      }
      this.ex(f);
      this.args(e);
      return { t: null };
    }
    libRet(kind, id, args, cls) {
      if (kind === 'd') return TD;
      if (kind === 'p') {
        const ts = args.map(a => a.t);
        if (!ts.length || ts.some(t => !isNum(t))) return null;
        if (ts.length === 1) return unary(ts[0]);
        return promote(this.lang, ts[0], ts[1]);
      }
      return tyOf(kind);
    }
    checkArgs(e, list, args, owner, id, unq) {
      const J = this.J, C = this.C;
      const n = args.length;
      const flexible = m => m.params.some(p => (p.ty && p.ty.varargs) || p.def || p.kind === 'params');
      const fit = list.filter(m => m.params.length === n || flexible(m));
      const rets = fit.map(m => m.ret);
      const ret = rets.length && rets.every(r => r && rets[0] && r.n === rets[0].n && (r.dim || 0) === (rets[0].dim || 0)) && !rets[0].tp && rets[0].n !== 'dyn' ? rets[0] : null;
      if (!(J || C)) return { t: ret && ret.n !== 'void' ? ret : null };
      if (!fit.length) {
        if (owner && owner.open) return { t: null };
        if (J) {
          if (list.length === 1) {
            const m = list[0];
            const req = m.params.length ? m.params.map(p => jName(p.ty)).join(',') : 'no arguments';
            const found = n ? args.map(a => jName(a.t)).join(',') : 'no arguments';
            this.err(`method ${id} in ${owner && owner.c && owner.c.kind === 'interface' ? 'interface' : 'class'} ${owner ? owner.name : 'Main'} cannot be applied to given types;\n  required: ${req}\n  found:    ${found}\n  reason: actual and formal argument lists differ in length`, e.line);
          }
          this.err(`no suitable method found for ${id}(${args.map(a => jName(a.t)).join(',')})`, e.line);
        }
        this.err(`CS1501: No overload for method '${id}' takes ${n} arguments`, e.line);
      }
      if (J && fit.length > 1 && args.every(a => known(a.t) && !a.t.box) && fit.every(m => !m.tps && !flexible(m) && m.params.every(p => known(p.ty) && !p.ty.box))) {
        const why = fit.map(m => { for (let i = 0; i < n; i++) { const w = this.jAssign(m.params[i].ty, args[i].t, args[i].v, 'arg'); if (w) return w.replace('incompatible types: ', ''); } return null; });
        if (why.every(Boolean)) {
          this.err(`no suitable method found for ${id}(${args.map(a => jName(a.t)).join(',')})` + fit.map((m, i) => `\n    method ${owner.name}.${this.sig(owner, m)} is not applicable\n      (argument mismatch; ${why[i]})`).join(''), e.line);
        }
      }
      if (fit.length === 1) { const m = fit[0]; const o = this.ownerOf(owner, m) || owner; this.access(m.mods, o, m, this.sig(o, m).replace(/^[^.(]*\./, ''), e.line); }
      if (fit.length === 1 && !fit[0].tps && !flexible(fit[0])) {
        const m = fit[0];
        m.params.forEach((p, i) => {
          if (!p.ty || p.ty.n === 'dyn' || p.ty.tp || p.ty.ref) return;
          const a = e.args[i];
          if (a && (a.k === 'refarg' || a.k === 'outdecl')) return;
          this.assign(p.ty, args[i], (a && a.line) || e.line, 'arg', a);
        });
      }
      return { t: ret && ret.n !== 'void' ? ret : null };
    }
    ownerOf(info, m) { for (const c of this.chain(info)) if ((c.methods.get(m.name) || []).includes(m)) return c; return null; }
    ctorCheck(e) {
      const info = this.cls.get(e.tt.n);
      if (!info || e.tt.dim) return;
      if (this.J && info.c.kind === 'enum') this.err('enum classes may not be instantiated', e.line);
      if ((this.J || this.C) && (info.c.kind === 'interface' || (info.c.mods && info.c.mods.abstract))) {
        if (this.J) this.err(`${info.name} is abstract; cannot be instantiated`, e.line);
        this.err(`CS0144: Cannot create an instance of the abstract type or interface '${info.name}'`, e.line);
      }
      if (info.open || info.c.kind === 'interface' || info.c.isEnum || info.c.kind === 'enum') return;
      const n0 = (e.args || []).length;
      const hit = info.ctors.filter(k => k.params.length === n0);
      if (hit.length === 1 && (this.J || this.C)) {
        const k = hit[0];
        const what = this.J ? `${info.name}(${k.params.map(p => jName(p.ty)).join(',')})` : `${info.name}(${k.params.map(p => cName(p.ty)).join(', ')})`;
        this.access(k.mods, info, k, what, e.line);
      }
      const n = (e.args || []).length;
      let ctors = info.ctors.map(k => k.params);
      if (info.c.recParams) ctors.push(info.c.recParams);
      if (!ctors.length) ctors = [[]];
      if (info.c.kind === 'struct' && n === 0) return;
      if (ctors.some(ps => ps.length === n || ps.some(p => (p.ty && p.ty.varargs) || p.def || p.kind === 'params'))) return;
      if (this.J) {
        if (ctors.length === 1) {
          const req = ctors[0].length ? ctors[0].map(p => jName(p.ty)).join(',') : 'no arguments';
          const found = n ? e.args.map(a => jName(this.peek(a))).join(',') : 'no arguments';
          this.err(`constructor ${info.name} in class ${info.name} cannot be applied to given types;\n  required: ${req}\n  found:    ${found}\n  reason: actual and formal argument lists differ in length`, e.line);
        }
        this.err(`no suitable constructor found for ${info.name}(${e.args.map(a => jName(this.peek(a))).join(',')})`, e.line);
      }
      if (this.C) this.err(`CS1729: '${info.name}' does not contain a constructor that takes ${n} arguments`, e.line);
    }
    peek(a) { try { return this.ex(a).t; } catch (x) { return null; } }

    /* ---------- flow: missing return and statements that can never run ---------- */
    flowAll() {
      const methods = [];
      for (const info of new Set(this.cls.values())) {
        (info.c.methods || []).forEach(m => methods.push([info, m]));
        (info.c.ctors || []).forEach(k => k.body && this.cc(k.body));
        (info.c.statics || []).forEach(b => this.cc(b));
      }
      (this.prog.funcs || []).forEach(m => methods.push([this.top, m]));
      if (this.J) (this.prog.top || []).forEach(s => this.cc(s));
      const locals = [];
      const findLocal = s => { if (!s || typeof s !== 'object') return; if (Array.isArray(s)) { s.forEach(findLocal); return; } if (s.k === 'localfn' && s.m) locals.push(s.m); if (s.k === 'lam') return; for (const k in s) { const v = s[k]; if (v && typeof v === 'object' && k[0] !== '$') findLocal(v); } };
      methods.forEach(([, m]) => findLocal(m.body));
      findLocal(this.prog.top);
      locals.forEach(m => methods.push([this.top, m]));
      for (const [info, m] of methods) {
        if (!m.body) continue;
        const can = this.cc(m.body);
        const rt = m.ret;
        if (!rt || (rt.n === 'void' && !rt.ptr)) continue;
        if (this.C && ((m.mods && m.mods.async) || /^(Task|ValueTask|IEnumerable|IEnumerator|IAsyncEnumerable)$/.test(rt.n))) continue;
        if (can === true) {
          if (this.J) this.err('missing return statement', m.body.end || m.line);
          this.err(`CS0161: '${this.sig(info, m)}': not all code paths return a value`, m.line);
        }
      }
    }
    condKind(c) {
      if (!c) return 'true';
      if (c.$cv === true) return 'true';
      if (c.$cv === undefined && c.$sure) return 'var';
      return null;
    }
    /* can the statement finish and let the next one run? true, false, or null when not sure */
    cc(s) {
      if (!s || typeof s !== 'object') return true;
      switch (s.k) {
        case 'block': return this.seq(s.body);
        case 'ret': case 'throw': case 'brk': case 'cont': case 'yield': return false;
        case 'decl': case 'expr': case 'exprs': case 'empty': case 'localfn': return s.label ? null : true;
        case 'if': {
          const a = this.cc(s.a);
          if (!s.b) { if (this.J) return true; return this.condKind(s.c) === 'var' ? true : null; }
          const b = this.cc(s.b);
          if (a === true || b === true) return true;
          if (a === false && b === false) return false;
          return null;
        }
        case 'while': case 'for': {
          this.cc(s.body);
          const k = s.k === 'for' && !s.c ? 'true' : this.condKind(s.c);
          if (k === 'var') return true;
          if (k === 'true') return this.loopExit(s.body);
          return null;
        }
        case 'do': {
          const body = this.cc(s.body);
          const k = this.condKind(s.c);
          const b = this.breaks(s.body, false);
          if (b === 'label') return null;
          if (k === 'true') return b === 'yes';
          if (k !== 'var') return null;
          if (b === 'yes' || body === true || this.hasCont(s.body)) return true;
          if (body === false) return false;
          return null;
        }
        case 'foreach': this.cc(s.body); return true;
        case 'switch': {
          const hasDefault = s.cases.some(c => c.tests === null || (Array.isArray(c.tests) && c.tests.some(t => t === null)));
          const pats = s.cases.some(c => Array.isArray(c.tests) && c.tests.some(t => t && t.k === 'pat'));
          let last = true;
          const results = s.cases.map(c => { const r = this.seq(c.body); last = c.body.length ? r : true; return r; });
          const b = s.cases.map(c => this.breaks(c.body, false));
          if (b.includes('label')) return null;
          if (pats) return null;
          if (!hasDefault) return true;
          if (b.includes('yes')) return true;
          if (s.arrow) { if (results.includes(true)) return true; if (results.every(r => r === false)) return false; return null; }
          return last;
        }
        case 'try': {
          const t = this.cc(s.body);
          const cs = s.catches.map(c => this.cc(c.body));
          const f = s.fin ? this.cc(s.fin) : true;
          if (f === false) return false;
          if (f === null) return null;
          const all = [t, ...cs];
          if (all.includes(true)) return true;
          if (all.every(x => x === false)) return false;
          return null;
        }
        default: return null;
      }
    }
    seq(list) {
      let res = true;
      for (let i = 0; i < list.length; i++) {
        const r = this.cc(list[i]);
        if (r === false) {
          if (this.J) for (let j = i + 1; j < list.length; j++) { if (list[j].k !== 'empty') this.err('unreachable statement', list[j].line); }
          return false;
        }
        if (r === null) res = null;
      }
      return res;
    }
    loopExit(body) {
      const b = this.breaks(body, false);
      if (b === 'label') return null;
      return b === 'yes';
    }
    /* does a break leave this loop or switch? 'yes', 'no', or 'label' when a labelled break makes it unclear */
    breaks(s, nested) {
      if (!s || typeof s !== 'object') return 'no';
      if (Array.isArray(s)) { let r = 'no'; for (const x of s) { const b = this.breaks(x, nested); if (b === 'label') return 'label'; if (b === 'yes') r = 'yes'; } return r; }
      switch (s.k) {
        case 'brk': return s.label ? 'label' : (nested ? 'no' : 'yes');
        case 'block': return this.breaks(s.body, nested);
        case 'if': { const a = this.breaks(s.a, nested), b = this.breaks(s.b, nested); return a === 'label' || b === 'label' ? 'label' : (a === 'yes' || b === 'yes' ? 'yes' : 'no'); }
        case 'while': case 'do': case 'for': case 'foreach': return this.breaks(s.body, true);
        case 'switch': return this.breaks(s.cases.map(c => c.body), true);
        case 'try': return this.breaks([s.body, ...s.catches.map(c => c.body), s.fin].filter(Boolean), nested);
        default: return 'no';
      }
    }
    hasCont(s) {
      if (!s || typeof s !== 'object') return false;
      if (Array.isArray(s)) return s.some(x => this.hasCont(x));
      switch (s.k) {
        case 'cont': return true;
        case 'block': return this.hasCont(s.body);
        case 'if': return this.hasCont(s.a) || this.hasCont(s.b);
        case 'switch': return s.cases.some(c => this.hasCont(c.body));
        case 'try': return this.hasCont(s.body) || s.catches.some(c => this.hasCont(c.body)) || this.hasCont(s.fin);
        default: return false;
      }
    }
  }

  /* a short explanation in plain words for each kind of mistake, shown under the compiler's own message */
  const an = w => (/^[aeiouAEIOU]/.test(w) ? 'an ' : 'a ') + w;
  CF.hintFor = function (lang, msg) {
    const J = lang === 'java', m = String(msg || '');
    let x;
    if ((x = m.match(/possible lossy conversion from (\w+) to (\w+)/)) || (x = m.match(/CS0266: Cannot implicitly convert type '(\w+)' to '(\w+)'/))) {
      const [, a, b] = x;
      const math = /^(byte|short|char|sbyte|ushort)$/.test(b) && a === 'int' ? ` ${J ? 'Java' : 'C#'} turns byte, short and char values into int before it adds or multiplies, so the answer here is an int.` : '';
      return `The value here is ${an(a)}, and ${an(b)} is a smaller box. ${J ? 'Java' : 'C#'} will not squeeze it in by itself, because part of the number could be lost.${math} Put a cast like (${b}) in front of the value if you accept that, or make the variable ${an(a)}.`;
    }
    if ((x = m.match(/CS0031: Constant value '(.*)' cannot be converted to a '(\w+)'/))) return `The number ${x[1]} does not fit in ${an(x[2])}. Use a bigger type, or a number that fits.`;
    if (/CS0664/.test(m)) return 'A number with a decimal point is a double. Write 1.5f, with an f at the end, to make it a float.';
    if ((x = m.match(/incompatible types: (\w+) cannot be converted to (\w+)/)) || (x = m.match(/CS0029: Cannot implicitly convert type '(\w+)' to '(\w+)'/)) || (x = m.match(/CS1503: Argument \d+: cannot convert from '(\w+)' to '(\w+)'/)) || (x = m.match(/CS0030: Cannot convert type '(\w+)' to '(\w+)'/))) {
      const [, a, b] = x;
      if (/^(boolean|bool)$/.test(b)) return `${J ? 'Java' : 'C#'} needs a true or false value here, and ${a} is not one. Ask a question that gives true or false, such as apples > 0.`;
      if (/^(String|string)$/.test(a)) return `Text in quotes is ${an(a)}, not a number. To read a number from text, use ${J ? 'Integer.parseInt(text)' : 'int.Parse(text)'}.`;
      if (/^(String|string)$/.test(b)) return `${an(a)[0].toUpperCase() + an(a).slice(1)} is not text. Join it to a String with + "" or use ${J ? 'String.valueOf(value)' : 'value.ToString()'}.`;
      return `${an(a)[0].toUpperCase() + an(a).slice(1)} value cannot go into ${an(b)} variable. They are different kinds of data.`;
    }
    if (/missing return statement|not all code paths return a value/.test(m)) return 'Every way through this method must end with return and a value. Add a return for the case that is left, often at the very end.';
    if (/unreachable statement/.test(m)) return 'This line can never run, because the line before it always leaves: return, break, throw, or a loop that never ends. Remove it or move it up.';
    if (/unexpected return value|returns void, a return keyword/.test(m)) return 'This method is void, so it gives nothing back. Remove the value after return, or give the method a return type such as int.';
    if (/missing return value|CS0126/.test(m)) return 'This method promised to give back a value, so return needs one, like return 0;.';
    if (/symbol:\s+variable|CS0103|does not contain a definition/.test(m)) return 'This name is not known here. Check the spelling, capital letters too, and that it is created before this line.';
    if (/symbol:\s+method/.test(m)) return 'There is no method with this name here. Check the spelling, or write the method before you call it.';
    if (/static context|CS0120/.test(m)) return 'main is static, so it belongs to the class and not to one object. Make the field or method static too, or create an object first and use it through that object.';
    if (/final variable|CS0131/.test(m)) return 'A final or const variable keeps its first value forever. Remove final if it needs to change.';
    if (/private access|inaccessible due to its protection level/.test(m)) return 'Only code inside the same class can use a private member. Use a public method of that class instead.';
    if (/is abstract; cannot be instantiated|CS0144/.test(m)) return 'An abstract class or an interface is an unfinished plan. Create an object of a class that extends or implements it instead.';
    if (/does not override abstract method|does not implement/.test(m)) return 'A class that implements an interface, or extends an abstract class, must write every method that is still missing.';
    if (/effectively final/.test(m)) return 'A lambda can only use a local variable that never changes after it gets its value. Copy it into a new variable that does not change.';
    if (/might not have been initialized|CS0165/.test(m)) return 'This variable never gets a value. Give it one when you create it, for example int total = 0;.';
    if (/cannot infer type|CS0815|CS0818/.test(m)) return 'var takes its type from the starting value, so it needs a value that has a type. Write the real type instead, such as String or int.';
    if (/cannot be applied to given types|CS1501|no suitable (method|constructor)|does not contain a constructor/.test(m)) return 'The number or the types of the values inside the brackets do not match what the method or constructor asks for.';
    if (/bad operand types? .*operator|CS0019|CS0023|incomparable types/.test(m)) return 'This operator does not work with these kinds of values. Compare text with equals or compareTo, and use && and || only with true or false values.';
    if (/array required, but String found/.test(m)) return 'A String is not an array. Use word.charAt(0) to read one letter.';
    if (/narrowing conversion/.test(m)) return 'Braces { } do not allow a value that would lose information. Use a value that fits, or write a cast.';
    if (/invalid conversion from 'const char\*'/.test(m)) return 'Text in quotes is not a number. Use stoi("12") to turn text into an int.';
    if (/cannot inherit from final|cannot derive from sealed/.test(m)) return 'A final class cannot have child classes. Remove final, or extend a different class.';
    return null;
  };

  /* returns notes (warnings) to show, and throws CF.CompileError for a mistake */
  CF.check = function (prog, lang, src) {
    if (lang !== 'java' && lang !== 'cs' && lang !== 'cpp' && lang !== 'c') return [];
    const c = new Checker(prog, lang, src);
    try { c.run(); }
    catch (e) { if (e instanceof CE) throw e; if (G.CF_CHECK_DEBUG) throw e; return []; }
    return c.notes;
  };
})();
