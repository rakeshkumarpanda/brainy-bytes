/* ===== Code Playground: reader for Java, C#, C and C++ =====
   The four languages share one family of syntax (braces, semicolons, typed variables), so one reader turns
   the source text into a tree for all of them. The tree is then run by cf-run.js, statement by statement,
   which is what lets the page step through a program line by line.

   CF.parse(src, lang) -> { classes, funcs, globals, top, lang }   lang is 'java', 'cs', 'c' or 'cpp'
   A mistake in the code throws CF.CompileError with a line number and a friendly message. */
var CF = (typeof self !== 'undefined' ? self : globalThis).CF || {};
(typeof self !== 'undefined' ? self : globalThis).CF = CF;

(() => {
  class CompileError extends Error {
    constructor(msg, line) { super(msg); this.line = line; }
  }
  CF.CompileError = CompileError;

  /* ---------- 1. tokens ---------- */
  const OPS = ['>>>=', '<<=', '>>=', '...', '->*', '->', '::', '++', '--', '&&', '||', '==', '!=', '<=', '>=', '+=', '-=', '*=', '/=', '%=',
    '&=', '|=', '^=', '<<', '=>', '??=', '??', '?.',
    '{', '}', '(', ')', '[', ']', ';', ',', '.', '=', '<', '>', '+', '-', '*', '/', '%', '!', '~', '?', ':', '&', '|', '^', '@', '#'];
  const ESC = { n: 10, t: 9, r: 13, '0': 0, '\\': 92, "'": 39, '"': 34, b: 8, f: 12, a: 7, v: 11, e: 27, s: 32 };

  function lex(src, lang) {
    const toks = [];
    let i = 0, line = 1;
    const n = src.length;
    const err = m => { throw new CompileError(m, line); };
    const readEsc = () => {
      /* at a backslash */
      i++;
      const c = src[i];
      if (c === 'u') { const h = src.substr(i + 1, 4); i += 5; return parseInt(h, 16); }
      if (c === 'x') { let h = ''; i++; while (/[0-9a-fA-F]/.test(src[i]) && h.length < 4) h += src[i++]; return parseInt(h, 16); }
      if (/[0-7]/.test(c) && lang !== 'cs') { let o = ''; while (/[0-7]/.test(src[i]) && o.length < 3) o += src[i++]; return parseInt(o, 8); }
      i++;
      if (c in ESC) return ESC[c];
      if (c === '\n') { line++; return -1; }
      return c.charCodeAt(0);
    };
    while (i < n) {
      const c = src[i];
      if (c === '\n') { line++; i++; continue; }
      if (c === ' ' || c === '\t' || c === '\r' || c === '\f') { i++; continue; }
      if (c === '/' && src[i + 1] === '/') { while (i < n && src[i] !== '\n') i++; continue; }
      if (c === '/' && src[i + 1] === '*') {
        const e = src.indexOf('*/', i + 2);
        const end = e < 0 ? n : e + 2;
        for (let k = i; k < end; k++) if (src[k] === '\n') line++;
        i = end; continue;
      }
      /* preprocessor lines in C and C++, and #region style lines in C# */
      if (c === '#' && (lang === 'c' || lang === 'cpp' || lang === 'cs')) {
        let s = '';
        while (i < n && src[i] !== '\n') {
          if (src[i] === '\\' && src[i + 1] === '\n') { i += 2; line++; continue; }
          s += src[i++];
        }
        toks.push({ t: 'pp', v: s.trim(), line });
        continue;
      }
      const start = line;
      /* text block (Java) */
      if (lang === 'java' && src.startsWith('"""', i)) {
        let j = src.indexOf('\n', i + 3); if (j < 0) err('A text block needs a new line after the opening """');
        const e = src.indexOf('"""', j + 1); if (e < 0) err('This text block has no closing """');
        let raw = src.slice(j + 1, e);
        for (let k = i; k < e + 3; k++) if (src[k] === '\n') line++;
        const lines = raw.split('\n');
        const last = lines[lines.length - 1];
        const ind = Math.min(...lines.filter((l, x) => l.trim() || x === lines.length - 1).map(l => l.match(/^[ \t]*/)[0].length));
        raw = lines.map(l => l.slice(ind).replace(/[ \t]+$/, '')).join('\n');
        if (!last.trim()) raw = raw.replace(/[^\n]*$/, ''); /* closing quotes on their own line keep the final new line */
        raw = raw.replace(/\\n/g, '\n').replace(/\\t/g, '\t').replace(/\\"/g, '"').replace(/\\\\/g, '\\');
        toks.push({ t: 'str', v: raw, line: start });
        i = e + 3; continue;
      }
      /* strings, with C# verbatim @"..." and interpolated $"..." forms */
      if (c === '"' || (lang === 'cs' && (c === '@' || c === '$') && (src[i + 1] === '"' || ((src[i + 1] === '@' || src[i + 1] === '$') && src[i + 2] === '"')))
        || (lang === 'cpp' && c === 'R' && src[i + 1] === '"')) {
        let verb = false, interp = false;
        if (lang === 'cpp' && c === 'R') {
          const p = src.indexOf('(', i + 2), d = src.slice(i + 2, p), e = src.indexOf(')' + d + '"', p);
          const raw = src.slice(p + 1, e);
          for (const ch of raw) if (ch === '\n') line++;
          toks.push({ t: 'str', v: raw, line: start }); i = e + d.length + 2; continue;
        }
        while (src[i] === '@' || src[i] === '$') { if (src[i] === '@') verb = true; else interp = true; i++; }
        i++; /* the opening quote */
        const parts = []; let s = '';
        for (;;) {
          if (i >= n) err('This string has no closing quote');
          const ch = src[i];
          if (ch === '\n' && !verb) err('A string cannot run over the end of a line. Close it with " on the same line');
          if (ch === '"') {
            if (verb && src[i + 1] === '"') { s += '"'; i += 2; continue; }
            i++; break;
          }
          if (ch === '\\' && !verb) { const v = readEsc(); if (v >= 0) s += String.fromCharCode(v); continue; }
          if (interp && ch === '{') {
            if (src[i + 1] === '{') { s += '{'; i += 2; continue; }
            parts.push(s); s = '';
            let depth = 1, j = i + 1, inner = '';
            while (j < n && depth) {
              if (src[j] === '{') depth++;
              else if (src[j] === '}') { depth--; if (!depth) break; }
              else if (src[j] === '"') { /* a string inside the hole */
                inner += src[j++]; while (j < n && src[j] !== '"') { if (src[j] === '\\') inner += src[j++]; inner += src[j++]; }
              }
              inner += src[j++];
            }
            /* split a format part after a top level colon, like {price:F2}, but not inside ?: */
            let fmt = null, align = null, dq = 0, par = 0;
            for (let k = 0; k < inner.length; k++) {
              const q = inner[k];
              if (q === '"') dq ^= 1;
              if (dq) continue;
              if (q === '(' || q === '[') par++;
              if (q === ')' || q === ']') par--;
              if (q === '?') { const nx = inner[k + 1]; if (nx !== '.' && nx !== '?' && nx !== '[') par += 100; }
              if (q === ':' && par >= 100) { par -= 100; continue; }
              if (q === ':' && par === 0) { fmt = inner.slice(k + 1); inner = inner.slice(0, k); break; }
            }
            const cm = inner.match(/^(.*[^,]),\s*(-?\d+)\s*$/);
            if (cm && !/["(]/.test(cm[2])) { inner = cm[1]; align = +cm[2]; }
            parts.push({ src: inner, fmt, align, line });
            i = j + 1; continue;
          }
          if (interp && ch === '}' && src[i + 1] === '}') { s += '}'; i += 2; continue; }
          s += ch; i++;
        }
        if (interp) { parts.push(s); toks.push({ t: 'istr', parts, line: start }); }
        else {
          /* C and C++ join neighbouring string literals: "ab" "cd" */
          const prev = toks[toks.length - 1];
          if (prev && prev.t === 'str' && (lang === 'c' || lang === 'cpp')) prev.v += s;
          else toks.push({ t: 'str', v: s, line: start });
        }
        continue;
      }
      if (c === "'") {
        i++;
        let v;
        if (src[i] === '\\') v = readEsc(); else { v = src.codePointAt(i); i += v > 0xffff ? 2 : 1; }
        if (src[i] !== "'") {
          /* multi character constants are rare, treat them as a mistake */
          err("A char holds exactly one character, written between single quotes like 'a'. Use double quotes for text");
        }
        i++;
        toks.push({ t: 'chr', v, line: start });
        continue;
      }
      if (/[0-9]/.test(c) || (c === '.' && /[0-9]/.test(src[i + 1]))) {
        let j = i, kind = 'int', text;
        if (c === '0' && /[xX]/.test(src[i + 1])) { j += 2; while (/[0-9a-fA-F_']/.test(src[j])) j++; text = src.slice(i, j).replace(/[_']/g, ''); }
        else if (c === '0' && /[bB]/.test(src[i + 1])) { j += 2; while (/[01_']/.test(src[j])) j++; text = '0b' + src.slice(i + 2, j).replace(/[_']/g, ''); }
        else {
          while (/[0-9_']/.test(src[j])) j++;
          if (src[j] === '.' && /[0-9]/.test(src[j + 1] || '')) { kind = 'double'; j++; while (/[0-9_']/.test(src[j])) j++; }
          else if (src[j] === '.' && !/[A-Za-z_.]/.test(src[j + 1] || '')) { kind = 'double'; j++; }
          if (/[eE]/.test(src[j]) && /[0-9+-]/.test(src[j + 1])) { kind = 'double'; j += 2; while (/[0-9]/.test(src[j])) j++; }
          text = src.slice(i, j).replace(/[_']/g, '');
        }
        let suf = '';
        while (/[lLuUfFdDmM]/.test(src[j] || '')) suf += src[j++];
        const s = suf.toLowerCase();
        if (s.includes('f') && !/^0x/i.test(text)) kind = 'float';
        else if (s.includes('d') || s.includes('m')) kind = 'double';
        else if (s.includes('l')) kind = s.includes('u') ? 'ulong' : 'long';
        else if (s.includes('u')) kind = 'uint';
        /* C and C++ write octal numbers with a leading 0 */
        if ((lang === 'c' || lang === 'cpp') && kind === 'int' && /^0[0-7]+$/.test(text)) text = '0o' + text.slice(1);
        if (kind === 'int' && (lang === 'c' || lang === 'cpp')) {
          const big = BigInt(text);
          if (big > 2147483647n) kind = 'long';
        }
        toks.push({ t: 'num', v: text, kind, line: start, dec: lang === 'cs' && s.includes('m') });
        i = j; continue;
      }
      if (/[A-Za-z_$À-￿]/.test(c) && !(c === '$' && lang === 'cs')) {
        let j = i + 1;
        while (j < n && /[A-Za-z0-9_$À-￿]/.test(src[j])) j++;
        toks.push({ t: 'id', v: src.slice(i, j), line: start, sp: i > 0 && /\s/.test(src[i - 1]) });
        i = j; continue;
      }
      if (c === '@' && lang === 'cs' && /[A-Za-z_]/.test(src[i + 1])) { i++; continue; }
      const op = OPS.find(o => src.startsWith(o, i));
      if (!op) err(`The character "${c}" does not belong here`);
      /* '>' is kept single so List<List<Integer>> closes cleanly. The parser joins > > into a shift when they touch */
      if (op === '>>>=' || op === '>>=') {
        for (let k = 0; k < op.length - 1; k++) toks.push({ t: 'op', v: '>', line: start, tight: true });
        toks.push({ t: 'op', v: '=', line: start, tight: true, sh: true });
        i += op.length; continue;
      }
      toks.push({ t: 'op', v: op, line: start, tight: i > 0 && src[i - 1] === '>' && op === '>' });
      i += op.length;
    }
    toks.push({ t: 'eof', v: '', line });
    return toks;
  }

  /* simple #define NAME value macros, and function like macros with plain parameters */
  function preprocess(toks, lang) {
    const macros = Object.create(null);
    const out = [];
    const includes = [];
    for (let i = 0; i < toks.length; i++) {
      const t = toks[i];
      if (t.t === 'pp') {
        const m = t.v.match(/^#\s*define\s+([A-Za-z_]\w*)(\(([^)]*)\))?\s*(.*)$/);
        if (m && (lang === 'c' || lang === 'cpp')) {
          const body = lex(m[4], lang).slice(0, -1).map(x => Object.assign(x, { line: t.line }));
          macros[m[1]] = { params: m[2] ? m[3].split(',').map(s => s.trim()).filter(Boolean) : null, body };
        }
        const inc = t.v.match(/^#\s*include\s*[<"]([^>"]+)[>"]/);
        if (inc) includes.push(inc[1]);
        continue;
      }
      if (t.t === 'id' && macros[t.v]) {
        const mac = macros[t.v];
        if (!mac.params) { mac.body.forEach(b => out.push(Object.assign({}, b, { line: t.line }))); continue; }
        if (toks[i + 1] && toks[i + 1].v === '(') {
          let depth = 0, j = i + 1; const args = [[]];
          for (; j < toks.length; j++) {
            const x = toks[j];
            if (x.v === '(' && x.t === 'op') { depth++; if (depth === 1) continue; }
            if (x.v === ')' && x.t === 'op') { depth--; if (!depth) break; }
            if (x.v === ',' && x.t === 'op' && depth === 1) { args.push([]); continue; }
            args[args.length - 1].push(x);
          }
          mac.body.forEach(b => {
            const k = b.t === 'id' ? mac.params.indexOf(b.v) : -1;
            if (k >= 0) { out.push({ t: 'op', v: '(', line: t.line }); (args[k] || []).forEach(a => out.push(Object.assign({}, a, { line: t.line }))); out.push({ t: 'op', v: ')', line: t.line }); }
            else out.push(Object.assign({}, b, { line: t.line }));
          });
          i = j; continue;
        }
      }
      out.push(t);
    }
    return { toks: out, includes };
  }

  /* ---------- 2. types ---------- */
  const PRIM = {
    java: { int: 'int', long: 'long', short: 'short', byte: 'byte', char: 'char', boolean: 'bool', float: 'float', double: 'double', void: 'void', var: 'var',
      String: 'string', Integer: 'int', Long: 'long', Short: 'short', Byte: 'byte', Character: 'char', Boolean: 'bool', Float: 'float', Double: 'double', Object: 'object', Number: 'double' },
    cs: { int: 'int', long: 'long', short: 'short', byte: 'ubyte', sbyte: 'byte', char: 'char', bool: 'bool', float: 'float', double: 'double', decimal: 'double', void: 'void', var: 'var',
      string: 'string', String: 'string', object: 'object', uint: 'uint', ulong: 'ulong', ushort: 'ushort', Int32: 'int', Int64: 'long', Double: 'double', Boolean: 'bool', Char: 'char', dynamic: 'dyn', nint: 'long' },
    c: { int: 'int', long: 'long', short: 'short', char: 'char', float: 'float', double: 'double', void: 'void', _Bool: 'bool', bool: 'bool', size_t: 'ulong', unsigned: 'uint', signed: 'int',
      int8_t: 'byte', int16_t: 'short', int32_t: 'int', int64_t: 'long', uint8_t: 'ubyte', uint16_t: 'ushort', uint32_t: 'uint', uint64_t: 'ulong', FILE: 'object' },
    cpp: { int: 'int', long: 'long', short: 'short', char: 'char', float: 'float', double: 'double', void: 'void', bool: 'bool', auto: 'var', size_t: 'ulong', unsigned: 'uint', signed: 'int',
      string: 'string', int8_t: 'byte', int16_t: 'short', int32_t: 'int', int64_t: 'long', uint8_t: 'ubyte', uint16_t: 'ushort', uint32_t: 'uint', uint64_t: 'ulong' }
  };
  /* library types each language knows, so the reader can tell a declaration from an expression */
  const LIBT = {
    java: 'Scanner,ArrayList,List,LinkedList,HashMap,Map,TreeMap,LinkedHashMap,HashSet,Set,TreeSet,LinkedHashSet,Stack,Queue,Deque,ArrayDeque,PriorityQueue,StringBuilder,StringBuffer,Random,Iterator,Collection,Exception,RuntimeException,Arrays,Collections,Math,System,Map.Entry,Entry,Optional,BufferedReader,InputStreamReader,Thread,Runnable,Comparator,Function,BiFunction,Supplier,Consumer,Predicate,IntStream,Stream,Collectors,Objects,Character,Iterable,BigInteger,Vector',
    cs: 'List,Dictionary,HashSet,SortedSet,SortedDictionary,Stack,Queue,LinkedList,StringBuilder,Random,Console,Math,Exception,KeyValuePair,IEnumerable,IList,ICollection,IDictionary,Func,Action,Predicate,Tuple,PriorityQueue,Array,Convert,Enumerable,Environment,Comparison,DateTime,TimeSpan,Nullable',
    c: '',
    cpp: 'vector,map,unordered_map,set,unordered_set,multiset,multimap,stack,queue,deque,priority_queue,pair,list,array,string,ostringstream,stringstream,istringstream,function,tuple,greater,less,optional,exception,runtime_error,out_of_range,invalid_argument,logic_error,iterator,size_type,unique_ptr,shared_ptr'
  };
  CF.PRIM = PRIM;

  /* ---------- 3. parser ---------- */
  function parse(src, lang) {
    const mode = lang;
    if (lang === 'csexpr') lang = 'cs';
    let nsDepth = 0, inCase = false;
    const lx = lex(src, lang);
    const { toks: rawToks, includes } = preprocess(lx, lang);
    /* drop full package names inside code, so java.util.List works like List */
    const toks = [];
    for (let i = 0; i < rawToks.length; i++) {
      const t = rawToks[i], prev = toks[toks.length - 1];
      /* C++: std::sort is the same as sort here, and ios::fixed is fixed */
      if (lang === 'cpp' && t.t === 'id' && (t.v === 'std' || t.v === 'ios' || t.v === 'ios_base') && rawToks[i + 1] && rawToks[i + 1].v === '::' && rawToks[i + 2] && rawToks[i + 2].t === 'id' && !(prev && prev.v === 'namespace')) { i++; continue; }
      const qual = lang === 'java' ? (t.v === 'java' || t.v === 'javax') : lang === 'cs' ? t.v === 'System' : false;
      if (qual && t.t === 'id' && rawToks[i + 1] && rawToks[i + 1].v === '.' && !(prev && (prev.v === 'import' || prev.v === 'package' || prev.v === 'using' || prev.v === '.'))) {
        let k = i;
        if (lang === 'java') { while (rawToks[k] && rawToks[k].t === 'id' && /^[a-z]/.test(rawToks[k].v) && rawToks[k + 1] && rawToks[k + 1].v === '.') k += 2; }
        else { while (rawToks[k] && ['System', 'Collections', 'Generic', 'Linq', 'Text'].includes(rawToks[k].v) && rawToks[k + 1] && rawToks[k + 1].v === '.' && rawToks[k + 2] && rawToks[k + 2].t === 'id') k += 2; }
        if (k > i && rawToks[k] && rawToks[k].t === 'id') { i = k - 1; continue; }
      }
      toks.push(t);
    }
    let p = 0;
    const prim = PRIM[lang];
    const typeNames = new Set(Object.keys(prim).concat(LIBT[lang].split(',').filter(Boolean)));
    const typeParams = [new Set()];
    /* pre-scan for class, struct, enum, record, interface and typedef names so declarations read right */
    for (let i = 0; i < toks.length - 1; i++) {
      const t = toks[i];
      if (t.t === 'id' && /^(class|struct|enum|interface|record|union)$/.test(t.v) && toks[i + 1].t === 'id') {
        let k = i + 1; if (toks[k].v === 'class' || toks[k].v === 'struct') k++;
        typeNames.add(toks[k].v);
      }
      if (t.t === 'id' && t.v === 'typedef') {
        let depth = 0, j = i + 1;
        for (; j < toks.length; j++) { const v = toks[j].v; if (v === '{') depth++; else if (v === '}') depth--; else if (v === ';' && !depth) break; }
        if (toks[j - 1] && toks[j - 1].t === 'id') typeNames.add(toks[j - 1].v);
        if (toks[j - 1] && toks[j - 1].v === ')') { /* typedef int (*fn)(int) */
          for (let k = i; k < j; k++) if (toks[k].v === '*' && toks[k + 1].t === 'id') { typeNames.add(toks[k + 1].v); break; }
        }
      }
      if (t.t === 'id' && (t.v === 'using') && toks[i + 1].t === 'id' && toks[i + 2] && toks[i + 2].v === '=' && lang === 'cpp') typeNames.add(toks[i + 1].v);
    }
    const typedefs = Object.create(null);

    const peek = (k = 0) => toks[p + k];
    const at = (v, k = 0) => { const t = toks[p + k]; return t && (t.t === 'op' || t.t === 'id') && t.v === v; };
    const next = () => toks[p++];
    const err = (m, t = peek()) => { throw new CompileError(m, t.line); };
    const desc = t => t.t === 'eof' ? 'the end of the program' : t.t === 'str' ? 'a string' : `"${t.v}"`;
    const expect = (v, why) => {
      if (!at(v)) {
        const t = peek();
        if (v === ';') err(`A semicolon ; is missing${why ? ' ' + why : ''}. The reader found ${desc(t)} instead. Every statement in ${LNAME[lang]} ends with ;`, toks[p - 1] && toks[p - 1].line !== t.line ? toks[p - 1] : t);
        err(`Expected "${v}"${why ? ' ' + why : ''}, but found ${desc(t)}`);
      }
      return next();
    };
    const ident = what => { const t = peek(); if (t.t !== 'id') err(`Expected a name${what ? ' for ' + what : ''}, but found ${desc(t)}`); p++; return t.v; };
    const isTypeName = v => typeNames.has(v) || typeParams.some(s => s.has(v)) || typedefs[v];

    const MODS = new Set(['public', 'private', 'protected', 'static', 'final', 'abstract', 'const', 'constexpr', 'virtual', 'override', 'inline', 'extern', 'readonly',
      'sealed', 'internal', 'unsafe', 'volatile', 'transient', 'synchronized', 'native', 'strictfp', 'register', 'explicit', 'mutable', 'partial', 'async', 'default', 'new', 'friend', 'signed', 'noexcept']);

    function skipAnnotations() {
      while (at('@') && lang === 'java' && peek(1).t === 'id' && peek(1).v !== 'interface') {
        p += 2; while (at('.')) p += 2;
        if (at('(')) skipBalanced('(', ')');
      }
      while (lang === 'cs' && at('[') && peek(1).t === 'id' && /^[A-Z]/.test(peek(1).v) && looksAttribute()) skipBalanced('[', ']');
      while (lang === 'cpp' && at('[') && at('[', 1)) skipBalanced('[', ']');
    }
    function looksAttribute() {
      let d = 0;
      for (let k = p; k < toks.length; k++) {
        const v = toks[k].v;
        if (v === '[') d++; else if (v === ']') { d--; if (!d) { const n = toks[k + 1]; return n && (n.t === 'id' || n.v === '['); } }
      }
      return false;
    }
    function skipBalanced(o, c) {
      let d = 0;
      do { const t = next(); if (t.t === 'eof') err(`"${o}" is never closed with "${c}"`); if (t.v === o) d++; else if (t.v === c) d--; } while (d > 0);
    }
    function mods() {
      const m = {};
      for (;;) {
        skipAnnotations();
        const t = peek();
        if (t.t === 'id' && MODS.has(t.v)) {
          if (t.v === 'default' && (at(':', 1) || at('->', 1))) break;
          if (t.v === 'new' && !(peek(1).t === 'id')) break;
          if (t.v === 'signed' || t.v === 'unsigned') break;
          if (t.v === 'noexcept') { p++; continue; }
          m[t.v] = true; p++;
          continue;
        }
        break;
      }
      return m;
    }

    /* a type: name, generic arguments, array brackets, pointer stars and reference marks */
    function tryType(allowArrayDims = true) {
      const save = p;
      try { const t = parseType(allowArrayDims); return t; } catch (e) { if (!(e instanceof CompileError)) throw e; p = save; return null; }
    }
    function parseType(allowArrayDims = true) {
      while (at('const') || at('final') || at('volatile') || at('struct') || at('enum') || at('class') || at('typename') || at('union') || at('unsigned') || at('signed') || at('long') || at('short')) {
        if (at('unsigned') || at('signed') || at('long') || at('short')) break;
        p++;
      }
      let t;
      const tk = peek();
      if (tk.t !== 'id') err(`Expected a type, but found ${desc(tk)}`);
      /* multi word C types: unsigned long long, long double, short int */
      if (/^(unsigned|signed|long|short)$/.test(tk.v) && (lang === 'c' || lang === 'cpp' || tk.v === 'long' || tk.v === 'short')) {
        const words = [];
        while (peek().t === 'id' && /^(unsigned|signed|long|short|int|char|double)$/.test(peek().v)) words.push(next().v);
        const w = words.join(' ');
        const uns = words.includes('unsigned');
        let n;
        if (words.includes('char')) n = uns ? 'ubyte' : 'char';
        else if (words.includes('double')) n = 'double';
        else if (words.filter(x => x === 'long').length >= 1) n = uns ? 'ulong' : 'long';
        else if (words.includes('short')) n = uns ? 'ushort' : 'short';
        else n = uns ? 'uint' : 'int';
        if (lang === 'c' && w === 'long' ) n = 'long';
        t = { n };
      } else {
        let name = next().v;
        /* qualified names: std::vector, java.util.List, System.Text.StringBuilder, Map.Entry */
        while ((at('::') || at('.')) && peek(1).t === 'id') {
          const sep = peek().v;
          if (sep === '.' && !(isTypeName(peek(1).v) || /^(java|util|io|lang|System|Collections|Generic|Text|Linq|Map)$/.test(name) || /^[a-z]/.test(name))) break;
          p++;
          const nx = next().v;
          if (name === 'std' || /^(java|util|io|lang|System|Collections|Generic|Text|Linq)$/.test(name) || /^(java\.|System\.)/.test(name)) name = nx;
          else name = name + '.' + nx;
        }
        if (name === 'Map.Entry') name = 'Entry';
        if (typedefs[name]) t = Object.assign({}, typedefs[name]);
        else if (prim[name] && !(lang === 'java' && name === 'var' && !(peek().t === 'id'))) t = { n: prim[name], box: /^[A-Z]/.test(name) && lang === 'java' && name !== 'String' && name !== 'Object' };
        else if (typeParams.some(s => s.has(name))) t = { n: 'dyn', tp: name };
        else t = { n: name };
        if (t.box) t.jn = name;
        if (name === 'decimal' && lang === 'cs') t.dec = true;
        if (at('<')) {
          const save = p;
          p++;
          const args = [];
          let ok = true;
          if (at('>')) { p++; t.args = []; t.diamond = true; }
          else {
            for (;;) {
              if (at('?')) { p++; if (at('extends') || at('super')) { p++; args.push(parseType()); } else args.push({ n: 'object' }); }
              else if (peek().t === 'num') { args.push({ n: 'int', val: +next().v }); }
              else { const a = tryType(); if (!a) { ok = false; break; } args.push(a); }
              if (at(',')) { p++; continue; }
              if (at('>')) { p++; break; }
              ok = false; break;
            }
            if (ok) t.args = args; else { p = save; }
          }
        }
        if (lang === 'cpp' && at('::') && peek(1).t === 'id') { /* vector<int>::iterator */
          p++; const nx = next().v; t = { n: nx === 'iterator' || nx === 'const_iterator' ? 'iterator' : nx === 'size_type' ? 'ulong' : nx, of: t };
        }
      }
      while (at('const')) p++;
      if (lang === 'cs' && at('?') && !(peek(1).t === 'id' && (at('=', 2) || at(';', 2) || at(',', 2) || at(')', 2))) === false) { p++; t.nullable = true; }
      else if (lang === 'cs' && at('?')) { /* int? x */ if (peek(1).t === 'id') { p++; t.nullable = true; } }
      while (at('*') && (lang === 'c' || lang === 'cpp')) { p++; t.ptr = (t.ptr || 0) + 1; while (at('const')) p++; }
      if ((at('&') || at('&&')) && lang === 'cpp') { p++; t.ref = true; }
      if (allowArrayDims) {
        while (at('[') && at(']', 1)) { p += 2; t.dim = (t.dim || 0) + 1; }
        if (lang === 'cs' && at('[') && at(',', 1)) { /* int[,] */ p++; let r = 1; while (at(',')) { p++; r++; } expect(']'); t.dim = 1; t.rank = r; }
      }
      if (lang === 'java' && at('...')) { p++; t.dim = (t.dim || 0) + 1; t.varargs = true; }
      if (lang === 'cs' && at('params')) p++;
      return t;
    }

    /* is there a declaration here, like "int x", "List<String> names", "Point p(1, 2)", "auto [a, b]"? */
    function looksDecl() {
      const t = peek();
      if (t.t !== 'id') return false;
      if (/^(return|new|throw|if|while|for|do|switch|case|break|continue|delete|this|super|null|true|false|nullptr|sizeof|typeof|yield|await|else|try|catch|goto|using|base|default)$/.test(t.v)) return false;
      const save = p;
      while (at('const') || at('final') || at('static') || at('constexpr') || at('register') || at('volatile') || at('struct') || at('enum') || at('unsigned') && false) p++;
      const ty = tryType();
      let ok = false;
      if (ty) {
        const n = peek();
        if (n.t === 'id' && !(lang === 'java' ? /^instanceof$/ : lang === 'cs' ? /^(is|as|in)$/ : /^$/).test(n.v)) {
          const after = peek(1);
          const known = isTypeName(ty.n) || ['int', 'long', 'short', 'byte', 'ubyte', 'char', 'bool', 'float', 'double', 'string', 'var', 'uint', 'ulong', 'ushort', 'object', 'dyn'].includes(ty.n)
            || ty.args || ty.dim || ty.ptr || ty.ref;
          ok = known || ['=', ';', ',', ':', '[', ')'].includes(after.v) || (after.v === '(' && false);
          if (!known && after.v === '(') ok = false;
          if (/^[a-z]/.test(ty.n) && !known && !(after.v === '=' || after.v === ';')) ok = false;
        }
        if (lang === 'cpp' && ty.n === 'var' && at('[')) ok = true; /* auto [a, b] = ... */
        if (lang === 'cs' && ty.n === 'var' && at('(')) ok = true; /* var (a, b) = ... */
      }
      p = save;
      return ok;
    }

    /* ---------- expressions ---------- */
    const BIN = [
      ['??'], ['||'], ['&&'], ['|'], ['^'], ['&'], ['==', '!='], ['<', '>', '<=', '>=', 'instanceof', 'is', 'as'], ['<<', '>>', '>>>'], ['+', '-'], ['*', '/', '%']
    ];
    function shiftAt() {
      /* '>' '>' that touch make '>>', three make '>>>' */
      if (at('>') && peek(1) && peek(1).v === '>' && peek(1).tight && !(peek(2) && peek(2).sh && peek(1).tight && peek(2).v === '=')) {
        if (peek(2) && peek(2).v === '>' && peek(2).tight && !(peek(3) && peek(3).sh)) return '>>>';
        if (peek(2) && peek(2).v === '=' && peek(2).sh) return null;
        return '>>';
      }
      return null;
    }
    function assignOpAt() {
      const t = peek();
      if (t.t !== 'op') return null;
      if (['=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '??='].includes(t.v)) {
        if (t.v === '=' && t.sh) return null;
        return t.v;
      }
      if (t.v === '>' && peek(1).v === '>' && peek(1).tight) {
        if (peek(2).v === '=' && peek(2).sh) return '>>=';
        if (peek(2).v === '>' && peek(3) && peek(3).v === '=' && peek(3).sh) return '>>>=';
      }
      return null;
    }
    function expr() { return assign(); }
    function assign() {
      if (isLambdaStart()) return lambda();
      const line = peek().line;
      const a = cond();
      const op = assignOpAt();
      if (op) {
        p += op === '>>=' ? 3 : op === '>>>=' ? 4 : 1;
        const b = assign();
        if (!['name', 'mem', 'idx', 'deref', 'tuple'].includes(a.k)) err('The left side of = must be a variable, a field or an array element, like x = 5', toks[p - 1]);
        return { k: 'asg', op, a, b, line };
      }
      return a;
    }
    function isLambdaStart() {
      const t = peek();
      if (lang === 'c') return false;
      if (lang === 'cpp' && at('[')) {
        /* [](int a) { ... } or [&] or [=] */
        let d = 0, k = p;
        for (; k < toks.length; k++) { if (toks[k].v === '[') d++; else if (toks[k].v === ']') { d--; if (!d) break; } }
        const n = toks[k + 1];
        return n && (n.v === '(' || n.v === '{');
      }
      if (inCase) return false;
      if (t.t === 'id' && (at('->', 1) || at('=>', 1))) return true;
      if (at('(')) {
        let d = 0, k = p;
        for (; k < toks.length; k++) { if (toks[k].v === '(') d++; else if (toks[k].v === ')') { d--; if (!d) break; } }
        const n = toks[k + 1];
        return n && ((n.v === '->' && lang === 'java') || (n.v === '=>' && lang === 'cs'));
      }
      return false;
    }
    function lambda() {
      const line = peek().line;
      const params = [];
      let capture = null;
      if (lang === 'cpp') {
        p++; capture = '';
        while (!at(']')) capture += next().v;
        p++;
        if (at('(')) {
          p++;
          while (!at(')')) { const ty = parseType(); params.push({ ty, id: ident('a lambda parameter') }); if (at(',')) p++; }
          p++;
        }
        mods(); while (at('mutable')) p++;
        let ret = null;
        if (at('->')) { p++; ret = parseType(); }
        const body = block();
        return { k: 'lam', params, body, ret, line, capture };
      }
      if (peek().t === 'id') params.push({ id: next().v, ty: null });
      else {
        p++;
        while (!at(')')) {
          if (peek(1).v === ',' || peek(1).v === ')') params.push({ id: ident(), ty: null });
          else { const ty = parseType(); params.push({ ty, id: ident('a lambda parameter') }); }
          if (at(',')) p++;
        }
        p++;
      }
      next(); /* -> or => */
      if (at('{')) return { k: 'lam', params, body: block(), line };
      const e = expr();
      return { k: 'lam', params, body: e, exprBody: true, line };
    }
    function cond() {
      const line = peek().line;
      const c = binary(0);
      if (at('?') ) {
        p++;
        const a = assign();
        expect(':', 'in the ? : choice (condition ? valueIfTrue : valueIfFalse)');
        const b = assign();
        return { k: 'cond', c, a, b, line };
      }
      return c;
    }
    function binary(lv) {
      if (lv >= BIN.length) return unary();
      let a = binary(lv + 1);
      for (;;) {
        const t = peek();
        let op = null;
        if (lv === 8) op = shiftAt() || (at('<<') ? '<<' : null);
        else if (BIN[lv].includes(t.v) && (t.t === 'op' || ['instanceof', 'is', 'as'].includes(t.v))) {
          op = t.v;
          if (op === '>' && shiftAt()) op = null;
          if (op === 'is' && lang !== 'cs') op = null;
          if (op === 'as' && lang !== 'cs') op = null;
          if (op === 'instanceof' && lang !== 'java') op = null;
        }
        if (!op) break;
        if ((op === '<' || op === '>') && t.v === '<' && false) break;
        const line = t.line;
        p += op === '>>' ? 2 : op === '>>>' ? 3 : 1;
        if (op === 'instanceof' || op === 'is' || op === 'as') {
          if (op === 'is' && at('not')) { p++; const ty = parseType(); a = { k: 'un', op: '!', a: { k: 'inst', a, tt: ty, line }, line }; continue; }
          if (op === 'is' && (at('null'))) { p++; a = { k: 'bin', op: '==', a, b: { k: 'lit', v: null, ty: { n: 'null' } }, line }; continue; }
          const ty = parseType();
          let bind = null;
          if (peek().t === 'id' && !/^(and|or|when)$/.test(peek().v)) bind = next().v;
          a = { k: op === 'as' ? 'as' : 'inst', a, tt: ty, bind, line };
          continue;
        }
        const b = binary(lv + 1);
        a = { k: 'bin', op, a, b, line };
      }
      return a;
    }
    function unary() {
      const t = peek();
      const line = t.line;
      if (t.t === 'op') {
        if (t.v === '++' || t.v === '--') { p++; return { k: 'pre', op: t.v, a: unary(), line }; }
        if (t.v === '-' || t.v === '+' || t.v === '!' || t.v === '~') { p++; return { k: 'un', op: t.v, a: unary(), line }; }
        if (t.v === '*' && (lang === 'c' || lang === 'cpp')) { p++; return { k: 'deref', a: unary(), line }; }
        if (t.v === '&' && (lang === 'c' || lang === 'cpp')) { p++; return { k: 'addr', a: unary(), line }; }
        if (t.v === '(') {
          /* a cast: (int) x, (double) sum / n, (Node*) malloc(...) */
          const save = p;
          p++;
          const ty = tryType();
          if (ty && at(')')) {
            const known = isTypeName(ty.n) || ['int', 'long', 'short', 'byte', 'ubyte', 'char', 'bool', 'float', 'double', 'string', 'uint', 'ulong', 'ushort', 'object', 'void'].includes(ty.n) || ty.ptr;
            const nx = peek(1);
            const castable = nx && (nx.t !== 'op' || ['(', '!', '~', '-', '+', '*', '&', '++', '--'].includes(nx.v) && (known || nx.v === '('))
              && !(nx.t === 'id' && /^(instanceof|is|as)$/.test(nx.v));
            if (known && castable && !(nx.t === 'op' && (nx.v === '-' || nx.v === '+') && !['int', 'long', 'short', 'byte', 'char', 'float', 'double', 'uint', 'ulong'].includes(ty.n))) {
              p++;
              return { k: 'cast', tt: ty, a: unary(), line };
            }
          }
          p = save;
        }
      }
      if (t.t === 'id' && t.v === 'sizeof') {
        p++;
        if (at('(')) {
          const save = p; p++;
          const ty = tryType();
          if (ty && at(')')) { p++; return { k: 'sizeof', tt: ty, line }; }
          p = save;
        }
        return { k: 'sizeof', a: unary(), line };
      }
      if (t.t === 'id' && (t.v === 'delete')) { p++; if (at('[')) { p += 2; } return { k: 'delete', a: unary(), line }; }
      if (t.t === 'id' && t.v === 'await') { p++; return unary(); }
      if (t.t === 'id' && t.v === 'throw' && (lang === 'cs' || lang === 'cpp')) { p++; return { k: 'throwx', a: unary(), line }; }
      return postfix(primary());
    }
    function args() {
      expect('(');
      const out = [];
      while (!at(')')) {
        if (lang === 'cs' && (at('ref') || at('out') || at('in'))) {
          const kind = next().v;
          if (kind === 'out' && looksDecl()) { const ty = parseType(); const id = ident(); out.push({ k: 'outdecl', tt: ty, id, line: peek().line }); }
          else out.push({ k: 'refarg', a: expr(), kind });
        } else if (lang === 'cs' && peek().t === 'id' && at(':', 1)) { p += 2; out.push(expr()); } /* named argument */
        else out.push(expr());
        if (at(',')) p++; else if (!at(')')) err(`Expected , or ) in the argument list, but found ${desc(peek())}`);
      }
      p++;
      return out;
    }
    function postfix(e) {
      for (;;) {
        const t = peek();
        const line = t.line;
        if (at('.') || at('?.') || (at('->') && (lang === 'c' || lang === 'cpp'))) {
          const q = t.v === '?.', arrow = t.v === '->';
          p++;
          if (lang === 'java' && at('<')) { skipBalanced('<', '>'); }
          const id = ident('a member after "' + t.v + '"');
          if (lang === 'cs' && at('<') && genericCallAhead()) skipBalanced('<', '>');
          e = { k: 'mem', o: e, id, q, arrow, line };
          continue;
        }
        if (at('::') && (lang === 'java')) { p++; const id = at('new') ? (p++, 'new') : ident(); e = { k: 'mref', o: e, id, line }; continue; }
        if (at('::') && lang === 'cpp') { p++; const id = ident(); e = { k: 'mem', o: e, id, scope: true, line }; continue; }
        if (at('(')) { e = { k: 'call', f: e, args: args(), line }; continue; }
        if (at('[')) {
          p++;
          const i = expr();
          if (lang === 'cs' && at(',')) { const more = [i]; while (at(',')) { p++; more.push(expr()); } expect(']'); e = { k: 'idx', o: e, i: more[0], i2: more.slice(1), line }; continue; }
          expect(']', 'to close the [ index');
          e = { k: 'idx', o: e, i, line };
          continue;
        }
        if (at('++') || at('--')) { p++; e = { k: 'post', op: t.v, a: e, line }; continue; }
        if (at('!') && lang === 'cs' && (at('.', 1) || at(';', 1) || at(')', 1))) { p++; continue; } /* null forgiving x! */
        if (lang === 'cs' && at('switch') && at('{', 1)) { e = switchExprCs(e); continue; }
        if (lang === 'cs' && at('with') && at('{', 1)) { p++; e = { k: 'with', o: e, init: objInit(), line }; continue; }
        break;
      }
      return e;
    }
    function genericCallAhead() {
      let d = 0;
      for (let k = p; k < toks.length; k++) {
        const v = toks[k].v;
        if (v === '<') d++; else if (v === '>') { d--; if (!d) return toks[k + 1] && toks[k + 1].v === '('; }
        else if (!(toks[k].t === 'id' || v === ',' || v === '.' || v === '[' || v === ']')) return false;
      }
      return false;
    }
    function objInit() {
      /* C# object initializer { Name = "x", Age = 3 } or collection initializer { 1, 2, 3 } or { {"a", 1} } */
      expect('{');
      const items = [];
      while (!at('}')) {
        if (peek().t === 'id' && at('=', 1)) { const id = next().v; p++; items.push({ id, e: expr() }); }
        else if (at('[')) { p++; const key = expr(); expect(']'); expect('='); items.push({ key, e: expr() }); }
        else if (at('{')) { p++; const parts = []; while (!at('}')) { parts.push(expr()); if (at(',')) p++; } p++; items.push({ add: parts }); }
        else items.push({ add: [expr()] });
        if (at(',')) p++;
      }
      p++;
      return items;
    }
    function arrayInit() {
      const line = peek().line;
      expect('{');
      const items = [];
      while (!at('}')) {
        if (at('{')) items.push(arrayInit());
        else if (at('.') && peek(1).t === 'id' && lang === 'c') { p += 2; expect('='); items.push({ k: 'desig', id: toks[p - 2].v, e: expr() }); }
        else items.push(expr());
        if (at(',')) p++; else if (!at('}')) err(`Expected , or } in the list of values, but found ${desc(peek())}`);
      }
      p++;
      return { k: 'arr', items, line };
    }
    function switchExprCs(subject) {
      const line = peek().line;
      p += 2;
      const arms = [];
      while (!at('}')) {
        let pat;
        if (at('_')) { p++; pat = null; }
        else pat = casePattern();
        let guard = null;
        if (at('when')) { p++; guard = expr(); }
        expect('=>');
        arms.push({ pat, guard, e: expr() });
        if (at(',')) p++;
      }
      p++;
      return { k: 'swx', e: subject, arms, cs: true, line };
    }
    function casePattern() {
      /* C# patterns: constants, < 5, >= 10 and < 20, or lists of constants */
      const one = () => {
        if (['<', '>', '<=', '>='].includes(peek().v)) { const op = next().v; return { rel: op, e: binary(8) }; }
        if (at('not')) { p++; return { not: one() }; }
        if (peek().t === 'id' && isTypeName(peek().v) && peek(1).t === 'id' && !/^(and|or|when)$/.test(peek(1).v)) { const ty = parseType(); return { ty, bind: next().v }; }
        if (peek().t === 'id' && isTypeName(peek().v) && (at('=>', 1) || at(':', 1))) { const ty = parseType(); return { ty }; }
        return { e: binary(1) };
      };
      let a = one();
      while (at('and') || at('or')) { const op = next().v; a = { [op]: [a, one()] }; }
      return a;
    }
    function primary() {
      const t = next();
      const line = t.line;
      if (t.t === 'num') return t.dec ? { k: 'lit', num: t.v, kind: t.kind, line, dec: true } : { k: 'lit', num: t.v, kind: t.kind, line };
      if (t.t === 'str') return { k: 'lit', v: t.v, ty: { n: 'string' }, cstr: lang === 'c' || lang === 'cpp', line };
      if (t.t === 'chr') return { k: 'lit', v: t.v, ty: { n: 'char' }, line };
      if (t.t === 'istr') {
        return { k: 'istr', parts: t.parts.map(x => typeof x === 'string' ? x : { e: subExpr(x.src, x.line), fmt: x.fmt, align: x.align }), line };
      }
      if (t.t === 'op') {
        if (t.v === '(') {
          const e = expr();
          if (lang === 'cs' && at(',')) { const items = [e]; while (at(',')) { p++; items.push(expr()); } expect(')'); return { k: 'tuple', items, line }; }
          expect(')', 'to close the bracket');
          return { k: 'paren', a: e, line };
        }
        if (t.v === '{' && (lang === 'cpp' || lang === 'c' || lang === 'java' || lang === 'cs')) { p--; return arrayInit(); }
        if (t.v === '[' && lang === 'cs') { /* collection expression [1, 2, 3] */
          const items = [];
          while (!at(']')) { items.push(expr()); if (at(',')) p++; }
          p++;
          return { k: 'arr', items, line, coll: true };
        }
        if (t.v === '::' && lang === 'cpp') { p--; p++; return primary(); }
        err(`"${t.v}" cannot start an expression here`, t);
      }
      if (t.t === 'eof') err('The program ends too early. A closing bracket or semicolon may be missing', t);
      const v = t.v;
      if (v === 'true' || v === 'false') return { k: 'lit', v: v === 'true', ty: { n: 'bool' }, line };
      if (v === 'null' || v === 'nullptr' || (v === 'NULL' && (lang === 'c' || lang === 'cpp'))) return { k: 'lit', v: null, ty: { n: 'null' }, line };
      if (v === 'this') return { k: 'this', line };
      if ((v === 'super' && lang === 'java') || (v === 'base' && lang === 'cs')) return { k: 'super', line };
      if (v === 'new') {
        if (lang === 'cs' && at('(')) { const a = args(); const init = at('{') ? objInit() : null; return { k: 'new', tt: null, args: a, init, line }; }
        if (lang === 'cs' && at('[')) { p += 2; const init = arrayInit(); return { k: 'newarr', tt: { n: 'var' }, dims: [null], init, line }; }
        if (lang === 'cs' && at('{')) { const init = objInit(); return { k: 'new', tt: { n: 'anon' }, args: [], init, line }; }
        const ty = parseType(false);
        if (at('[')) {
          const dims = [];
          while (at('[')) {
            p++;
            if (at(']')) { p++; dims.push(null); continue; }
            const d = expr();
            if (lang === 'cs' && at(',')) { const more = [d]; while (at(',')) { p++; more.push(expr()); } expect(']'); more.forEach(x => dims.push(x)); ty.rank = more.length; continue; }
            expect(']'); dims.push(d);
          }
          if (lang === 'cs' && at('[') ) {}
          const init = at('{') ? arrayInit() : null;
          return { k: 'newarr', tt: ty, dims, init, line };
        }
        if (at('{') && lang === 'java' && ty.dim) { return { k: 'newarr', tt: Object.assign({}, ty, { dim: 0 }), dims: Array(ty.dim).fill(null), init: arrayInit(), line }; }
        let a = [];
        if (at('(')) a = args();
        else if (at('{') && lang === 'cpp') { a = arrayInit().items; }
        let init = null, body = null;
        if (at('{') && lang === 'cs') init = objInit();
        if (at('{') && lang === 'java') body = classBody(ty.n + '$anon', 'class'); /* anonymous class */
        return { k: 'new', tt: ty, args: a, init, anon: body, line };
      }
      if (v === 'typeof' && lang === 'cs') { expect('('); const ty = parseType(); expect(')'); return { k: 'lit', v: ty.n, ty: { n: 'string' }, line }; }
      if (v === 'nameof' && lang === 'cs') { expect('('); let last = ''; while (!at(')')) last = next().v; p++; return { k: 'lit', v: last, ty: { n: 'string' }, line }; }
      if (v === 'default' && lang === 'cs') { if (at('(')) { p++; const ty = parseType(); expect(')'); return { k: 'default', tt: ty, line }; } return { k: 'lit', v: null, ty: { n: 'null' }, line }; }
      if (v === 'switch' && lang === 'java') return switchStmt(line, true);
      if ((v === 'static_cast' || v === 'dynamic_cast' || v === 'reinterpret_cast' || v === 'const_cast') && at('<')) {
        p++; const ty = parseType(); expect('>'); expect('('); const a = expr(); expect(')');
        return { k: 'cast', tt: ty, a, line };
      }
      /* C++ function-style cast: char(c + 1), int(3.7), double(n) */
      if (lang === 'cpp' && at('(') && /^(int|char|double|float|long|short|bool|unsigned)$/.test(v)) {
        p++; const a = expr(); expect(')');
        return { k: 'cast', tt: { n: v === 'unsigned' ? 'uint' : v }, a, line };
      }
      /* generic method call in C#: Max<int>(...) */
      if (lang === 'cs' && at('<') && genericCallAhead()) { skipBalanced('<', '>'); }
      /* C++ template call: max<int>(a, b) or a type with arguments as a constructor: pair<int,int>(1, 2), vector<int>(n, 0) */
      if (lang === 'cpp' && at('<') && isTypeName(v)) {
        const save = p; p--;
        const ty = tryType();
        if (ty && (at('(') || at('{'))) {
          const brace = at('{');
          const a = brace ? arrayInit().items : args();
          return { k: 'new', tt: ty, args: a, value: true, brace, line };
        }
        p = save;
      }
      if (lang === 'cpp' && at('<') && !isTypeName(v) && genericCallAhead()) skipBalanced('<', '>');
      if (lang === 'cpp' && (at('{')) && isTypeName(v) && !prim[v]) { const a = arrayInit().items; return { k: 'new', tt: { n: v }, args: a, value: true, brace: true, line }; }
      return { k: 'name', id: v, line };
    }
    function subExpr(src, line) {
      const sub = parse('__x = ' + src + ';', lang === 'cs' ? 'csexpr' : lang);
      return Object.assign(sub, { line });
    }

    /* ---------- statements ---------- */
    function block() {
      const line = peek().line;
      expect('{', 'to start a block');
      const body = [];
      while (!at('}')) {
        if (peek().t === 'eof') err('A { block is never closed. Add the missing }', toks[p - 1]);
        body.push(stmt());
      }
      const end = next().line;
      return { k: 'block', body, line, end };
    }
    function declRest(ty, line, isField) {
      const vars = [];
      for (;;) {
        let vty = ty;
        if (lang === 'c' || lang === 'cpp') {
          /* int *p, x;  int &r = x; */
          let stars = 0; while (at('*')) { p++; stars++; }
          let ref = false; if (at('&')) { p++; ref = true; }
          if (stars || ref) vty = Object.assign({}, ty, { ptr: (ty.ptr || 0) + stars, ref: ref || ty.ref });
          else if (vars.length) vty = Object.assign({}, ty, { ptr: ty.basePtr ?? ty.ptr });
        }
        if (lang === 'cpp' && at('[') && ty.n === 'var') {
          p++; const ids = []; while (!at(']')) { ids.push(ident()); if (at(',')) p++; } p++;
          expect('='); const init = expr();
          vars.push({ bind: ids, init, ty: vty });
          if (at(',')) { p++; continue; } break;
        }
        const id = ident('the variable');
        const v = { id, ty: vty, line: peek().line };
        const dims = [];
        while (at('[')) { p++; if (at(']')) { p++; dims.push(null); } else { dims.push(expr()); expect(']'); } }
        if (dims.length) { v.ty = Object.assign({}, vty, { dim: (vty.dim || 0) + dims.length, cdims: dims }); }
        if (at('=')) { p++; v.init = at('{') ? arrayInit() : expr(); }
        else if (at('(') && lang === 'cpp' && !isField) { v.ctor = args(); }
        else if (at('{') && lang === 'cpp') { v.ctor = arrayInit().items; v.brace = true; }
        else if (at(':') && isField && (lang === 'c' || lang === 'cpp')) { p++; next(); } /* bit field */
        vars.push(v);
        if (at(',')) { p++; continue; }
        break;
      }
      return { k: 'decl', ty, vars, line };
    }
    function stmt() {
      const t = peek();
      const line = t.line;
      if (t.t === 'pp') { p++; return { k: 'empty', line }; }
      if (at(';')) { p++; return { k: 'empty', line }; }
      if (at('{')) return block();
      if (t.t === 'id') {
        switch (t.v) {
          case 'if': {
            p++; expect('(', 'after if'); const c = expr(); expect(')', 'to close the if condition');
            const a = stmt();
            let b = null;
            if (at('else')) { p++; b = stmt(); }
            return { k: 'if', c, a, b, line };
          }
          case 'while': { p++; expect('(', 'after while'); const c = expr(); expect(')', 'to close the while condition'); return { k: 'while', c, body: stmt(), line }; }
          case 'do': {
            p++; const body = stmt(); const wl = peek().line;
            if (!at('while')) err('A do block must end with while (condition);');
            p++; expect('('); const c = expr(); expect(')'); expect(';', 'after the do while condition');
            return { k: 'do', c, body, line, wl };
          }
          case 'for': return forStmt(line);
          case 'foreach': {
            p++; expect('(');
            let ty = null, id;
            if (at('var') && at('(', 1)) { p += 2; const ids = []; while (!at(')')) { ids.push(ident()); if (at(',')) p++; } p++; id = ids; ty = { n: 'var' }; }
            else { ty = parseType(); if (at('(')) { p++; const ids = []; while (!at(')')) { if (looksDecl()) parseType(); ids.push(ident()); if (at(',')) p++; } p++; id = ids; } else id = ident('the loop variable'); }
            if (!at('in')) err('A foreach loop reads: foreach (var item in list)');
            p++; const it = expr(); expect(')');
            return { k: 'foreach', ty, id, it, body: stmt(), line };
          }
          case 'return': { p++; let e = null; if (!at(';')) e = expr(); expect(';', 'after return'); return { k: 'ret', e, line }; }
          case 'break': { p++; let label = null; if (peek().t === 'id') label = next().v; expect(';', 'after break'); return { k: 'brk', label, line }; }
          case 'continue': { p++; let label = null; if (peek().t === 'id') label = next().v; expect(';', 'after continue'); return { k: 'cont', label, line }; }
          case 'switch': return switchStmt(line, false);
          case 'throw': { p++; const e = at(';') ? null : expr(); expect(';', 'after throw'); return { k: 'throw', e, line }; }
          case 'try': return tryStmt(line);
          case 'yield': if (lang === 'java' && !at('=', 1) && !at('(', 1)) { p++; const e = expr(); expect(';'); return { k: 'yield', e, line }; } break;
          case 'goto': err('goto is not supported in this playground. Use a loop or a function instead');
          case 'using':
            if (lang === 'cs' && at('(', 1)) { p += 2; const d = looksDecl() ? declRest(parseType(), line) : { k: 'expr', e: expr(), line }; expect(')'); return { k: 'block', body: [d, stmt()], line }; }
            if (lang === 'cs' && at('var', 1)) { p++; break; }
            /* using namespace std; or using System; */
            while (!at(';')) p++; p++; return { k: 'empty', line };
          case 'typedef': return typedefStmt(line);
          case 'class': case 'struct': case 'record': case 'interface': case 'enum':
            if (peek(1).t === 'id' && (at('{', 2) || at(':', 2) || at('extends', 2) || at('implements', 2) || at('(', 2) || at('<', 2))) { const c = classDecl(); localClasses.push(c); return { k: 'empty', line }; }
            break;
          case 'else': err('This else has no matching if. Check the braces { } above it');
          case 'case': case 'default': if (at(':', 1) || t.v === 'case') err(`"${t.v}" can only be used inside a switch`); break;
          case 'catch': err('This catch has no matching try { } block above it');
        }
        /* labels: outer: for (...) */
        if (peek(1).v === ':' && !at('::', 1) && lang !== 'cs' && peek(1).t === 'op' && (peek(2).v === 'for' || peek(2).v === 'while' || peek(2).v === 'do' || peek(2).v === '{')) {
          const label = next().v; p++;
          const s = stmt(); s.label = label; return s;
        }
        /* local functions (C# and Java compact files are handled at the top level) */
        if (lang === 'cs' && looksLocalFunc()) { const n = funcs.length; member(null, mods()); const m = funcs.length > n ? funcs.pop() : null; return m ? { k: 'localfn', m, line } : { k: 'empty', line }; }
      }
      if (looksDecl()) {
        const m = mods();
        const ty = parseType();
        if (lang === 'cs' && ty.n === 'var' && at('(')) {
          p++; const ids = []; while (!at(')')) { ids.push(ident()); if (at(',')) p++; } p++;
          expect('='); const init = expr(); expect(';');
          return { k: 'decl', ty, vars: [{ bind: ids, init, ty }], line, deconstruct: true };
        }
        const d = declRest(ty, line);
        if (m.const && lang !== 'cs') d.konst = true;
        if (m.final) d.final = true;
        if (m.const) d.isConst = true;
        if (m.static) d.isStatic = true;
        expect(';', 'after the declaration');
        return d;
      }
      if (lang === 'cs' && at('(') ) {
        /* (a, b) = (b, a) */
      }
      const e = expr();
      expect(';', 'after this statement');
      return { k: 'expr', e, line };
    }
    function looksLocalFunc() {
      const save = p;
      mods();
      const ty = tryType();
      const ok = ty && peek().t === 'id' && at('(', 1) && (() => {
        let d = 0, k = p + 1;
        for (; k < toks.length; k++) { if (toks[k].v === '(') d++; else if (toks[k].v === ')') { d--; if (!d) break; } }
        return toks[k + 1] && (toks[k + 1].v === '{' || toks[k + 1].v === '=>');
      })();
      p = save;
      return ok;
    }
    function typedefStmt(line) {
      p++;
      if ((at('struct') || at('union') || at('enum')) && (at('{', 1) || (peek(1).t === 'id' && at('{', 2)))) {
        const c = classDecl(true);
        const alias = ident('the typedef name');
        while (at(',')) { p++; while (at('*')) p++; const a2 = ident(); typedefs[a2] = { n: c.name, ptr: 1 }; typeNames.add(a2); }
        expect(';');
        if (alias !== c.name) { typedefs[alias] = { n: c.name }; typeNames.add(alias); }
        localClasses.push(c);
        return { k: 'empty', line };
      }
      const ty = parseType();
      if (at('(')) { /* function pointer typedef */
        p++; expect('*'); const name = ident(); expect(')'); skipBalanced('(', ')'); expect(';');
        typedefs[name] = { n: 'fnptr' }; typeNames.add(name);
        return { k: 'empty', line };
      }
      const alias = ident('the typedef name');
      let t2 = ty;
      while (at('[')) { p++; next(); expect(']'); t2 = Object.assign({}, t2, { dim: (t2.dim || 0) + 1 }); }
      expect(';');
      typedefs[alias] = t2; typeNames.add(alias);
      return { k: 'empty', line };
    }
    function forStmt(line) {
      p++; expect('(', 'after for');
      /* for-each in Java and C++: for (int x : list) */
      {
        const save = p;
        mods();
        if (looksDecl() || (lang === 'cpp' && at('auto'))) {
          const ty = parseType();
          let id;
          if (lang === 'cpp' && at('[')) { p++; id = []; while (!at(']')) { id.push(ident()); if (at(',')) p++; } p++; }
          else if (peek().t === 'id') id = next().v;
          if (id && at(':')) {
            p++; const it = expr(); expect(')', 'to close the for loop header');
            return { k: 'foreach', ty, id, it, body: stmt(), line };
          }
        }
        p = save;
      }
      let init = null;
      if (!at(';')) {
        mods();
        if (looksDecl()) init = declRest(parseType(), line);
        else { const es = [expr()]; while (at(',')) { p++; es.push(expr()); } init = { k: 'exprs', es, line }; }
      }
      expect(';', 'in the for loop header (for (start; condition; step))');
      const c = at(';') ? null : expr();
      expect(';', 'in the for loop header (for (start; condition; step))');
      const upd = [];
      while (!at(')')) { upd.push(expr()); if (at(',')) p++; else break; }
      expect(')', 'to close the for loop header');
      const body = stmt();
      return { k: 'for', init, c, upd, body, line };
    }
    function switchStmt(line, isExpr) {
      if (!isExpr) p++;
      expect('(', 'after switch'); const e = expr(); expect(')');
      expect('{', 'to open the switch body');
      const cases = [];
      let arrow = false;
      while (!at('}')) {
        const cl = peek().line;
        let tests = [];
        if (at('default')) { p++; tests = null; }
        else if (at('case')) {
          p++;
          for (;;) {
            if (lang === 'cs' && (looksDecl() || ['<', '>', '<=', '>=', 'not'].includes(peek().v))) { tests.push({ k: 'pat', pat: casePattern(), line: cl }); }
            else if (lang === 'java' && peek().t === 'id' && isTypeName(peek().v) && peek(1).t === 'id') { const ty = parseType(); tests.push({ k: 'pat', pat: { ty, bind: next().v }, line: cl }); }
            else if (lang === 'java' && at('null')) { p++; tests.push({ k: 'lit', v: null, ty: { n: 'null' } }); }
            else { inCase = true; try { tests.push(lang === 'java' && at('default') ? (p++, null) : cond()); } finally { inCase = false; } }
            if (at(',')) { p++; continue; }
            break;
          }
          if (lang === 'cs' && at('when')) { p++; tests.guard = expr(); }
          if (lang === 'java' && at('when')) { p++; tests.guard = expr(); }
        } else err(`Inside a switch, each part starts with case or default, but found ${desc(peek())}`);
        if (at('->')) {
          arrow = true; p++;
          let body;
          if (at('{')) body = [block()];
          else if (at('throw')) body = [stmt()];
          else { const ex = expr(); expect(';'); body = [isExpr ? { k: 'yield', e: ex, line: cl } : { k: 'expr', e: ex, line: cl }]; }
          cases.push({ tests, body, line: cl, arrow: true });
          continue;
        }
        if (!at(':')) err(`A colon : must follow the case value, like case 1:`);
        p++;
        const body = [];
        while (!at('case') && !at('default') && !at('}')) body.push(stmt());
        if (at('default') && (at('->', 1) === false && at(':', 1) === false)) body.push(stmt());
        cases.push({ tests, body, line: cl });
      }
      p++;
      return { k: isExpr ? 'swx' : 'switch', e, cases, arrow, line };
    }
    function tryStmt(line) {
      p++;
      let res = null;
      if (at('(')) { /* try with resources */
        p++; res = [];
        while (!at(')')) { res.push(declRest(parseType(), line)); if (at(';')) p++; }
        p++;
      }
      const body = block();
      const catches = [];
      while (at('catch')) {
        const cl = next().line;
        const c = { types: [], id: null, line: cl };
        if (at('(')) {
          p++;
          if (at('...')) { p++; c.types.push({ n: '...' }); }
          else {
            mods();
            c.types.push(parseType());
            while (at('|')) { p++; c.types.push(parseType()); }
            if (peek().t === 'id') c.id = next().v;
          }
          expect(')');
        }
        if (at('when')) { p++; expect('('); c.when = expr(); expect(')'); }
        c.body = block();
        catches.push(c);
      }
      let fin = null;
      if (at('finally')) { p++; fin = block(); }
      if (!catches.length && !fin && !res) err('A try block needs at least one catch or a finally');
      const tr = { k: 'try', body, catches, fin, line };
      if (res) return { k: 'block', body: res.concat([tr]), line };
      return tr;
    }

    /* ---------- classes and members ---------- */
    const classes = [], funcs = [], globals = [], top = [], localClasses = [];
    const LNAME = { java: 'Java', cs: 'C#', c: 'C', cpp: 'C++', csexpr: 'C#' };

    function classDecl(anonymousOk) {
      const kindTok = next();
      let kind = kindTok.v;
      if (kind === 'enum' && (at('class') || at('struct'))) p++;
      let name = peek().t === 'id' && !at('{') ? next().v : '$anon' + classes.length;
      typeNames.add(name);
      const tps = new Set();
      if (at('<')) {
        p++;
        while (!at('>')) { const n = ident(); tps.add(n); if (at('extends') || at(':')) { p++; parseType(); while (at('&')) { p++; parseType(); } } if (at(',')) p++; }
        p++;
      }
      typeParams.push(tps);
      let recParams = null;
      if (kind === 'record' || (lang === 'cs' && at('('))) {
        if (at('(')) {
          p++; recParams = [];
          while (!at(')')) { skipAnnotations(); const ty = parseType(); recParams.push({ ty, id: ident() }); if (at(',')) p++; }
          p++;
          if (kind !== 'record') kind = 'class';
        }
      }
      let base = null; const ifaces = [];
      if (at('extends')) { p++; base = parseType(); while (at(',')) { p++; ifaces.push(parseType()); } }
      if (at('implements')) { p++; ifaces.push(parseType()); while (at(',')) { p++; ifaces.push(parseType()); } }
      if (at(':') && lang !== 'c') {
        p++;
        const list = [];
        do { if (at(',')) p++; while (at('public') || at('private') || at('protected') || at('virtual')) p++; const bt = parseType(); if (at('(')) args(); list.push(bt); } while (at(','));
        base = list[0]; list.slice(1).forEach(x => ifaces.push(x));
      }
      while (at('where')) { while (!at('{')) p++; }
      let c;
      if (at(';') && kind === 'record') { p++; c = { name, kind, fields: [], methods: [], ctors: [], nested: [], consts: [], line: kindTok.line, statics: [] }; }
      else if (at(';')) { p++; c = { name, kind, fields: [], methods: [], ctors: [], nested: [], consts: [], line: kindTok.line, statics: [], fwd: true }; }
      else c = classBody(name, kind);
      typeParams.pop();
      Object.assign(c, { base, ifaces, recParams, line: kindTok.line, tps: [...tps] });
      if (lang === 'cpp' || lang === 'c') { if (!at(';') && peek().t === 'id' && !anonymousOk) { /* struct P {..} a, b; */ const d = declRest({ n: name }, peek().line); globals.push(d); } if (at(';') && !anonymousOk) p++; }
      return c;
    }
    function classBody(name, kind) {
      const c = { name, kind, fields: [], methods: [], ctors: [], nested: [], consts: [], statics: [], line: peek().line };
      expect('{', 'to open the ' + kind + ' body');
      if (kind === 'enum') {
        /* enum constants come first */
        while (!at('}') && !at(';')) {
          skipAnnotations();
          const id = ident('an enum constant');
          let a = [], val = null;
          if (at('(')) a = args();
          if (at('=')) { p++; val = cond(); }
          let body = null;
          if (at('{')) body = classBody(name + '$' + id, 'class');
          c.consts.push({ id, args: a, val, body, line: toks[p - 1].line });
          if (at(',')) p++;
        }
        if (at(';')) p++;
      }
      while (!at('}')) {
        if (peek().t === 'eof') err(`The ${kind} ${name} is never closed with }`);
        if (at(';')) { p++; continue; }
        if (lang === 'cpp' && (at('public') || at('private') || at('protected')) && at(':', 1)) { p += 2; continue; }
        if (at('{')) { const b = block(); c.statics.push(b); continue; } /* instance initializer */
        if (at('static') && at('{', 1)) { p++; c.statics.push(block()); continue; }
        if (lang === 'cpp' && at('friend')) { while (!at(';') && !at('{')) p++; if (at('{')) block(); else p++; continue; }
        if (lang === 'cpp' && at('template')) { templateHeader(); }
        if (lang === 'cpp' && at('using')) { while (!at(';')) p++; p++; continue; }
        const m = mods();
        if (['class', 'struct', 'interface', 'enum', 'record'].includes(peek().v) && peek(1).t === 'id' && !(at('(', 2) === false && at(';', 2) && false)) {
          if (lang === 'cpp' || lang === 'c') { if (peek(2).v === '{' || peek(2).v === ':' || peek(2).v === ';') { const nc = classDecl(); nc.isStatic = true; c.nested.push(nc); continue; } }
          else { const nc = classDecl(); nc.mods = m; nc.isStatic = !!m.static || lang === 'cs' || nc.kind !== 'class'; c.nested.push(nc); continue; }
        }
        if (lang === 'cs' && at('event')) { p++; }
        if (lang === 'cs' && at('operator', 1)) { while (!at('{') && !at('=>')) p++; if (at('{')) block(); else { while (!at(';')) p++; p++; } continue; }
        if (lang === 'cpp' && (at('operator') || (peek(1) && peek(1).v === 'operator') || (at('operator', 2)))) { operatorMember(c, m); continue; }
        member(c, m);
      }
      p++;
      return c;
    }
    function operatorMember(c, m) {
      const line = peek().line;
      let ret = null;
      if (!at('operator')) ret = parseType();
      expect('operator');
      let op = '';
      if (at('(')) { p++; expect(')'); op = '()'; }
      else if (at('[')) { p++; expect(']'); op = '[]'; }
      else { op = next().v; if (op === '>' && at('>')) { p++; op = '>>'; } if (at('=') && ['=', '<', '>', '!'].includes(op) && false) op += next().v; }
      if (!ret) { ret = parseType(); }
      const params = paramList();
      mods(); while (at('const')) p++;
      const body = at('{') ? block() : (expect(';'), null);
      c.methods.push({ name: 'operator' + op, params, ret, body, line, static: false });
    }
    function templateHeader() {
      p++; expect('<');
      const tps = new Set();
      while (!at('>')) { if (at('typename') || at('class')) p++; else parseType(); const n = ident('the template parameter'); tps.add(n); typeNames.add(n); if (at('=')) { p++; parseType(); } if (at(',')) p++; }
      p++;
      typeParams.push(tps);
      return tps;
    }
    function paramList() {
      expect('(', 'to start the parameter list');
      const params = [];
      if (at('void') && at(')', 1)) p++;
      while (!at(')')) {
        mods(); skipAnnotations();
        let kind = null;
        if (lang === 'cs' && (at('ref') || at('out') || at('in') || at('params') || at('this'))) { kind = next().v; }
        const ty = parseType();
        let id = peek().t === 'id' ? next().v : '_p' + params.length;
        if (lang === 'cpp' || lang === 'c') {
          while (at('[')) { p++; while (!at(']')) p++; p++; ty.ptr = (ty.ptr || 0) + 1; ty.arrParam = true; }
        }
        if (lang === 'java') while (at('[') && at(']', 1)) { p += 2; ty.dim = (ty.dim || 0) + 1; }
        let def = null;
        if (at('=')) { p++; def = cond(); }
        if (kind === 'ref' || kind === 'out' || kind === 'in') ty.ref = true;
        params.push({ ty, id, def, kind });
        if (at(',')) p++; else if (!at(')')) err(`Expected , or ) between parameters, but found ${desc(peek())}`);
      }
      p++;
      return params;
    }
    /* a field, a method or a constructor. c is null for top level functions */
    function member(c, m) {
      const line = peek().line;
      let tps = null;
      if (at('<') && lang === 'java') { tps = new Set(); p++; while (!at('>')) { tps.add(ident()); if (at('extends')) { p++; parseType(); } if (at(',')) p++; } p++; typeParams.push(tps); }
      /* constructor: Name(  or  ~Name( */
      const cname = c && c.name.replace(/\$anon$/, '');
      let isDtor = false;
      if (at('~')) { p++; isDtor = true; }
      if (c && peek().t === 'id' && peek().v === cname && at('(', 1)) {
        p++;
        const params = paramList();
        let init = [];
        let chain = null;
        if (at(':') && lang === 'cpp') {
          p++;
          do {
            if (at(',')) p++;
            const id = ident(); const a = at('{') ? arrayInit().items : args();
            init.push({ id, args: a });
          } while (at(','));
        }
        if (at(':') && lang === 'cs') { p++; const kind = next().v; chain = { kind, args: args() }; }
        while (at('throws')) { p++; parseType(); while (at(',')) { p++; parseType(); } }
        mods();
        let body;
        if (at('=')) { p++; next(); expect(';'); body = { k: 'block', body: [], line }; }
        else if (at(';')) { p++; body = null; }
        else if (at('=>') ) { p++; const e = expr(); expect(';'); body = { k: 'block', body: [{ k: 'expr', e, line }], line }; }
        else body = block();
        if (isDtor) return;
        if (tps) typeParams.pop();
        c.ctors.push({ params, body, init, chain, line, mods: m });
        return;
      }
      if (c && c.kind === 'record' && lang === 'java' && peek().v === cname && at('{', 1)) { /* compact canonical constructor */
        p++; const body = block(); c.compact = body; return;
      }
      const ret = parseType();
      /* C++ operator written outside a class: ostream &operator<<(ostream &os, const Point &p) */
      if (lang === 'cpp' && !c && at('operator')) {
        p++;
        let op = next().v;
        if (op === '(' ) { expect(')'); op = '()'; } else if (op === '[') { expect(']'); op = '[]'; }
        else if ((op === '<' && at('<') && peek().tight) || (op === '>' && at('>') && peek().tight)) op += next().v;
        const params = paramList();
        while (at('const') || at('noexcept')) p++;
        const body = at('{') ? block() : (expect(';'), null);
        if (tps) typeParams.pop();
        funcs.push({ name: 'operator' + op, params, ret, body, line, static: true, mods: m, tps: tps ? [...tps] : null, freeOp: true });
        return;
      }
      /* C++ method defined outside its class: int Box::area() { } */
      let owner = null, name;
      if (lang === 'cpp' && peek().t === 'id' && at('::', 1)) {
        owner = next().v; p++;
        if (at('~')) { p++; isDtor = true; }
        name = ident();
      } else if (lang === 'cpp' && ret.n.includes('.') ) { name = null; }
      else if (lang === 'cpp' && at('(') && ret.of === undefined && toks[p - 2] && toks[p - 2].v === '::') { name = ret.n; }
      else {
        if (lang === 'cpp' && at('(') && !c && ret && typeNames.has(ret.n) && toks[p - 2] && toks[p - 2].v === '::') { /* Box::Box( */ }
        name = ident('the field or method');
      }
      if (lang === 'cpp' && !owner && at('(') && ret.n && toks[p - 3] && toks[p - 3].v === '::') {}
      if (at('(')) {
        const params = paramList();
        mods(); while (at('const') || at('override') || at('final') || at('noexcept')) p++;
        while (at('throws')) { p++; parseType(); while (at(',')) { p++; parseType(); } }
        let body = null;
        if (at('{')) body = block();
        else if (at('=>')) { p++; const e = expr(); expect(';'); body = { k: 'block', body: [ret.n === 'void' ? { k: 'expr', e, line } : { k: 'ret', e, line }], line }; }
        else if (at('=') && (at('0', 1) || at('default', 1) || at('delete', 1) || (peek(1).t === 'num'))) { p += 2; expect(';'); }
        else if (at(':') && lang === 'cpp' && owner) {
          /* Box::Box(int w) : w(w) { } parsed as a ctor of owner */
          p++; const init = [];
          do { if (at(',')) p++; const id = ident(); const a = at('{') ? arrayInit().items : args(); init.push({ id, args: a }); } while (at(','));
          body = block();
          outOfClass.push({ owner, ctor: true, params, body, init, line });
          return;
        }
        else expect(';', 'after the method header');
        if (tps) typeParams.pop();
        const fn = { name, params, ret, body, line, static: !!m.static, abstract: !!m.abstract || (!body && c && (c.kind === 'interface' || lang === 'cpp' || m.abstract)), mods: m, tps: tps ? [...tps] : null };
        if (owner) {
          if (isDtor) return;
          if (name === owner) outOfClass.push({ owner, ctor: true, params, body, init: [], line });
          else outOfClass.push({ owner, fn });
          return;
        }
        if (isDtor) return;
        if (c) c.methods.push(fn); else funcs.push(fn);
        return;
      }
      /* C# property: public int Age { get; set; } */
      if (lang === 'cs' && at('{') && c) {
        p++;
        const prop = { name, ty: ret, line, static: !!m.static };
        while (!at('}')) {
          mods();
          const acc = ident('get or set');
          if (at(';')) { p++; prop[acc] = 'auto'; continue; }
          if (at('=>')) { p++; const e = expr(); expect(';'); prop[acc] = { k: 'block', body: [acc === 'get' ? { k: 'ret', e, line } : { k: 'expr', e, line }], line }; continue; }
          prop[acc] = block();
        }
        p++;
        let init = null;
        if (at('=')) { p++; init = at('{') ? arrayInit() : expr(); expect(';'); }
        c.fields.push({ ty: ret, id: name, init, static: !!m.static, line, prop, konst: !!m.const, mods: m });
        return;
      }
      if (lang === 'cs' && at('=>') && c) { /* expression bodied property */
        p++; const e = expr(); expect(';');
        c.fields.push({ ty: ret, id: name, static: !!m.static, line, prop: { name, get: { k: 'block', body: [{ k: 'ret', e, line }], line } }, mods: m });
        return;
      }
      /* a field (or a C global variable) */
      p -= 1;
      const d = declRest(ret, line, true);
      expect(';', 'after the field');
      d.vars.forEach(v => {
        const f = { ty: v.ty, id: v.id, init: v.init, ctor: v.ctor, static: !!m.static || (lang === 'cs' && !!m.const) || (c && c.kind === 'interface'), line: v.line || line, konst: !!m.const || !!m.final, mods: m };
        if (c) c.fields.push(f); else globals.push({ k: 'decl', ty: v.ty, vars: [v], line, konst: f.konst });
      });
    }
    const outOfClass = [];

    /* ---------- the whole file ---------- */
    if (mode === 'csexpr') { /* an interpolation hole, parsed as one expression */
      p += 2;
      const e = expr();
      return e;
    }
    while (peek().t !== 'eof') {
      const t = peek();
      if (t.t === 'pp') { p++; continue; }
      if (at(';')) { p++; continue; }
      if (at('package') || at('import') || (at('using') && !(lang === 'cs' && at('(', 1))) || (at('namespace') && lang === 'cpp' && at('std', 1))) {
        if (lang === 'cs' && at('using') && (at('var', 1) || (peek(1).t === 'id' && peek(2).t === 'id' && at('=', 3)))) { top.push(stmt()); continue; }
        while (!at(';')) { if (peek().t === 'eof') break; p++; } p++; continue;
      }
      if (at('namespace')) {
        p++; while (!at('{') && !at(';')) p++;
        if (at(';')) { p++; continue; }
        p++; nsDepth++; continue;
      }
      if (at('}') && nsDepth) { p++; nsDepth--; continue; }
      if (lang === 'cpp' && at('template')) { templateHeader(); const save = p; mods(); if (['class', 'struct'].includes(peek().v)) { classes.push(classDecl()); } else { p = save; member(null, mods()); } typeParams.pop(); continue; }
      if (at('typedef')) { typedefStmt(t.line); continue; }
      const save = p;
      const m = mods();
      if (['class', 'struct', 'interface', 'enum', 'record', 'union'].includes(peek().v) && (peek(1).t === 'id' || at('{', 1))) {
        /* C: struct Point p1;  is a declaration, not a type */
        if ((lang === 'c' || lang === 'cpp') && peek(1).t === 'id' && peek(2).t === 'id') { p = save; member(null, mods()); continue; }
        if ((lang === 'c' || lang === 'cpp') && peek(1).t === 'id' && at('*', 2)) { p = save; member(null, mods()); continue; }
        { const cd = classDecl(); cd.mods = m; classes.push(cd); }
        continue;
      }
      if (lang === 'java' && at('@') && at('interface', 1)) { p++; classes.push(classDecl()); continue; }
      /* top level statements in C# and Java compact source files */
      if (lang === 'cs' || lang === 'java') {
        p = save;
        if (lang === 'java' || looksLocalFunc()) {
          if (looksLocalFunc()) { const fm = mods(); member(null, fm); continue; }
        }
        if (lang === 'java') { const fm = mods(); member(null, fm); continue; }
        top.push(stmt());
        continue;
      }
      p = save;
      member(null, mods());
    }
    localClasses.forEach(c => { c.local = true; });
    classes.push(...localClasses);
    /* attach C++ out of class definitions */
    const allClasses = [];
    const walk = cs => cs.forEach(c => { allClasses.push(c); walk(c.nested); });
    walk(classes);
    outOfClass.forEach(o => {
      const c = allClasses.find(x => x.name === o.owner);
      if (!c) throw new CompileError(`${o.owner}:: refers to a class that is not defined`, o.line);
      if (o.ctor) {
        const i = c.ctors.findIndex(k => !k.body && k.params.length === o.params.length);
        const k = { params: o.params, body: o.body, init: o.init, line: o.line, mods: {} };
        if (i >= 0) c.ctors[i] = k; else c.ctors.push(k);
      } else {
        const i = c.methods.findIndex(k => k.name === o.fn.name && !k.body && k.params.length === o.fn.params.length);
        o.fn.static = i >= 0 ? c.methods[i].static : false;
        if (i >= 0) { o.fn.mods = c.methods[i].mods; c.methods[i] = o.fn; } else c.methods.push(o.fn);
      }
    });
    return { classes, funcs, globals, top, lang, includes };
  }
  CF.parse = parse;
  CF.lex = lex;
})();
