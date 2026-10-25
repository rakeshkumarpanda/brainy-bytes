/* ===== Playwright playground: write a test in Java, Python, JavaScript, TypeScript or C# and run it line by line =====
   Everything runs in the reader's browser. The test drives Brainy Shop (content/playwright/shop/) inside a frame.
   The pieces:
     1. a small lexer and parser that read Playwright code in five languages
     2. a code generator that writes the same test in every language (used by "Show in" and by the build)
     3. a locator engine: getByRole, getByText, getByLabel, getByPlaceholder, getByAltText, getByTitle, getByTestId,
        CSS, XPath, filter, nth, first, last, and, or, frames and strict mode, close to how Playwright resolves them
     4. a runtime with auto-waiting actions and web first assertions that retry until they pass or time out
     5. the playground and the labs on each chapter page (PAGE.labs)
   It is a teaching model of Playwright, not Playwright itself. The build runs every lab answer with real
   Playwright in Java, Python, JavaScript and TypeScript against the real shop, so the code you learn here is real. */
const PWPLAY = (() => {
  const isNode = typeof window === 'undefined';
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const LANGS = { ts: ['🔷', 'TypeScript'], js: ['🟨', 'JavaScript'], py: ['🐍', 'Python'], java: ['☕', 'Java'], cs: ['🟪', 'C#'] };

  /* ================= 1. lexer ================= */
  function lex(src, lang) {
    const out = [];
    let i = 0, line = 1;
    const isId = c => /[A-Za-z0-9_$]/.test(c);
    const prevSig = () => { for (let k = out.length - 1; k >= 0; k--) return out[k]; return null; };
    while (i < src.length) {
      const c = src[i];
      if (c === '\n') { line++; i++; continue; }
      if (/\s/.test(c)) { i++; continue; }
      if ((c === '/' && src[i + 1] === '/' && lang !== 'py') || (c === '#' && lang === 'py')) { while (i < src.length && src[i] !== '\n') i++; continue; }
      if (c === '/' && src[i + 1] === '*') { const e = src.indexOf('*/', i + 2); const body = src.slice(i, e < 0 ? src.length : e + 2); line += (body.match(/\n/g) || []).length; i += body.length; continue; }
      // strings, with Python r and f prefixes and C# @ verbatim strings
      let raw = false, j = i;
      if (lang === 'py' && /[rRfFbBuU]/.test(c) && /['"]/.test(src[i + 1] || '')) { raw = /[rR]/.test(c); j = i + 1; }
      if (lang === 'cs' && c === '@' && src[i + 1] === '"') { raw = true; j = i + 1; }
      if (lang === 'cs' && c === '$' && src[i + 1] === '"') { j = i + 1; }
      const q = src[j];
      if (q === '"' || q === "'" || (q === '`' && lang !== 'py')) {
        const triple = lang === 'py' && src.slice(j, j + 3) === q.repeat(3);
        let k = j + (triple ? 3 : 1), s = '';
        while (k < src.length) {
          if (triple ? src.slice(k, k + 3) === q.repeat(3) : src[k] === q) break;
          if (src[k] === '\\' && !raw) {
            const n = src[k + 1];
            s += n === 'n' ? '\n' : n === 't' ? '\t' : n === '\\' ? '\\' : n === q ? q : n === '"' || n === "'" || n === '`' ? n : '\\' + n;
            k += 2;
            continue;
          }
          if (src[k] === '\n') line++;
          s += src[k++];
        }
        out.push({ t: 'str', v: s, line, quote: q });
        i = k + (triple ? 3 : 1);
        continue;
      }
      // JavaScript regular expression literals
      if (c === '/' && (lang === 'js' || lang === 'ts')) {
        const p = prevSig();
        if (!p || (p.t === 'p' && '(,=:[!&|?{};'.includes(p.v)) || (p.t === 'id' && /^(return|await|typeof)$/.test(p.v))) {
          let k = i + 1, cls = false;
          while (k < src.length && src[k] !== '\n') {
            if (src[k] === '\\') { k += 2; continue; }
            if (src[k] === '[') cls = true; else if (src[k] === ']') cls = false; else if (src[k] === '/' && !cls) break;
            k++;
          }
          const body = src.slice(i + 1, k);
          let f = '';
          k++;
          while (k < src.length && /[a-z]/.test(src[k])) f += src[k++];
          out.push({ t: 're', v: body, flags: f, line });
          i = k;
          continue;
        }
      }
      if (/[0-9]/.test(c)) { let k = i; while (k < src.length && /[0-9._]/.test(src[k])) k++; out.push({ t: 'num', v: Number(src.slice(i, k).replace(/_/g, '')), line }); i = k; continue; }
      if (isId(c)) { let k = i; while (k < src.length && isId(src[k])) k++; out.push({ t: 'id', v: src.slice(i, k), line }); i = k; continue; }
      const three = src.slice(i, i + 3), two = src.slice(i, i + 2);
      if (['===', '!=='].includes(three)) { out.push({ t: 'p', v: three, line }); i += 3; continue; }
      if (['=>', '->', '==', '!=', '&&', '||', '+=', '<=', '>=', '?.', '::'].includes(two)) { out.push({ t: 'p', v: two, line }); i += 2; continue; }
      out.push({ t: 'p', v: c, line });
      i++;
    }
    return out;
  }

  /* ================= 2. parser ================= */
  // Lines that only hold the shape of a test (imports, classes, test functions, braces) are skipped.
  const STRUCT = [
    /^\s*(?:(?:import|package|namespace)\b|from\s+\S+\s+import\b|using\s+[\w.]+\s*;)/,
    /^\s*@\w+/, /^\s*\[\w+(\(.*\))?\]\s*$/,
    /^\s*(public|private|protected|internal|static|final|abstract|sealed|partial)?\s*(public|private|static|final)?\s*(class|record|interface)\b/,
    /^\s*(public\s+|private\s+|protected\s+)?(static\s+)?(async\s+)?(void|Task)\s+\w+\s*\(.*\)\s*(throws\s+[\w, ]+)?\s*\{?\s*$/,
    /^\s*(async\s+)?def\s+\w+\s*\(.*\)\s*(->\s*\w+)?\s*:\s*$/,
    /^\s*test(\.describe|\.step|\.beforeEach|\.afterEach|\.beforeAll|\.afterAll|\.only|\.skip)?\s*\(.*(=>|function).*\{\s*$/,
    /^\s*(await\s+)?test\.step\(.*(=>|function).*\{\s*$/,
    /^\s*[})\];]+\s*$/, /^\s*\{\s*$/, /^\s*(pass|return)\s*;?\s*$/,
    /^\s*with\s+sync_playwright\(\)/, /^\s*try\s*\(?\s*Playwright\b.*\{?\s*$/, /^\s*try\s*\{\s*$/,
  ];
  const SETUP = /(\b(chromium|firefox|webkit)\s*(\(\))?\s*\.\s*(launch|Launch)|Playwright\.(create|CreateAsync)\b|\bnew_page\(\)|\bnewPage\(\)|NewPageAsync\(\)|\bnew_context\(|\bnewContext\(|NewContextAsync\(|\bbrowser\.close\(|\bBrowser\.CloseAsync)/;

  function splitStatements(src, lang) {
    const lines = src.split('\n');
    const stmts = [];
    let buf = [], start = 0, depth = 0;
    const flush = end => { if (buf.length) stmts.push({ line: start + 1, end: end + 1, src: buf.join('\n') }); buf = []; depth = 0; };
    for (let n = 0; n < lines.length; n++) {
      const raw = lines[n];
      const t = raw.replace(lang === 'py' ? /\s+#.*$/ : /\s+\/\/.*$/, '').trim();
      if (!buf.length) {
        if (!t || t.startsWith('//') || (lang === 'py' && t.startsWith('#')) || t.startsWith('/*') || t.startsWith('*')) continue;
        if (STRUCT.some(r => r.test(raw))) { stmts.push({ line: n + 1, end: n + 1, src: t, skip: true }); continue; }
        start = n;
      }
      buf.push(t);
      for (const tok of lex(t, lang)) {
        if (tok.t !== 'p') continue;
        if ('([{'.includes(tok.v)) depth++;
        else if (')]}'.includes(tok.v)) depth--;
      }
      const next = (lines.slice(n + 1).find(l => l.trim()) || '').trim();
      const cont = depth > 0 || /[.,(+=&|]$/.test(t) || /^\.(?!\.)/.test(next) || /^(\)|\]|\})[^\s]/.test(next) && depth > 0;
      if (!cont) flush(n);
    }
    flush(lines.length - 1);
    return stmts;
  }

  function Parser(tokens, lang) {
    let i = 0;
    const peek = (k = 0) => tokens[i + k];
    const next = () => tokens[i++];
    const is = (v, k = 0) => { const t = peek(k); return t && (t.t === 'p' || t.t === 'id') && t.v === v; };
    const expect = v => { const t = next(); if (!t || t.v !== v) throw new Error(`I expected "${v}" but found ${t ? '"' + t.v + '"' : 'the end of the line'}`); return t; };
    function args(close) {
      const pos = [], named = {};
      while (peek() && !is(close)) {
        if (peek().t === 'id' && is('=', 1) && !is('==', 1) && (lang === 'py')) { const k = next().v; next(); named[k] = expr(); }
        else if (peek().t === 'id' && is(':', 1) && lang === 'cs') { const k = next().v; next(); named[k] = expr(); }
        else pos.push(expr());
        if (is(',')) next();
      }
      expect(close);
      return { pos, named };
    }
    function objLit() {
      const o = {};
      while (peek() && !is('}')) {
        let k = next();
        if (k.t === 'p' && k.v === '[') { k = { v: expr().v }; expect(']'); }
        if (is(':')) { next(); o[k.v] = expr(); }
        else if (is('=') && lang === 'cs') { next(); o[k.v] = expr(); }
        else o[k.v] = { k: 'id', v: k.v };
        if (is(',')) next();
      }
      expect('}');
      return { k: 'obj', v: o };
    }
    function primary() {
      const t = peek();
      if (!t) throw new Error('The line ends too early');
      if (t.t === 'id' && (t.v === 'await' || t.v === 'Await')) { next(); return primary(); }
      if (t.t === 'str') { next(); return { k: 'lit', v: t.v }; }
      if (t.t === 'num') { next(); return { k: 'lit', v: t.v }; }
      if (t.t === 're') { next(); return { k: 're', v: t.v, f: t.flags }; }
      if (t.t === 'id' && /^(true|True)$/.test(t.v)) { next(); return { k: 'lit', v: true }; }
      if (t.t === 'id' && /^(false|False)$/.test(t.v)) { next(); return { k: 'lit', v: false }; }
      if (t.t === 'id' && /^(null|None|undefined)$/.test(t.v)) { next(); return { k: 'lit', v: null }; }
      if (t.t === 'id' && t.v === 'lambda') {
        next();
        const ps = [];
        while (!is(':')) { const p = next(); if (p.t === 'id') ps.push(p.v); }
        next();
        return { k: 'fn', ps, body: expr() };
      }
      if (t.t === 'id' && t.v === 'new') {
        next();
        if (is('(') && lang === 'cs') { next(); expect(')'); expect('{'); return objLit(); }
        if (is('[')) { next(); expect(']'); expect('{'); const a = []; while (!is('}')) { a.push(expr()); if (is(',')) next(); } next(); return { k: 'arr', v: a }; }
        let name = next().v;
        while (is('.')) { next(); name += '.' + next().v; }
        if (is('<')) { while (!is('>')) next(); next(); }
        if (is('[')) { next(); expect(']'); expect('{'); const a = []; while (!is('}')) { a.push(expr()); if (is(',')) next(); } next(); return { k: 'arr', v: a }; }
        let a = { pos: [], named: {} };
        if (is('(')) { next(); a = args(')'); }
        let init = null;
        if (is('{') && lang === 'cs') { next(); init = objLit(); }
        return { k: 'new', name, args: a, init };
      }
      if (t.t === 'p' && t.v === '{') { next(); return objLit(); }
      if (t.t === 'p' && t.v === '[') { next(); const a = []; while (!is(']')) { a.push(expr()); if (is(',')) next(); } next(); return { k: 'arr', v: a }; }
      if (t.t === 'p' && t.v === '(') {
        // an arrow function (a, b) => body, or a group
        let k = i + 1, d = 1;
        while (k < tokens.length && d) { if (tokens[k].v === '(') d++; else if (tokens[k].v === ')') d--; k++; }
        if (tokens[k] && (tokens[k].v === '=>' || tokens[k].v === '->')) {
          next();
          const ps = [];
          while (!is(')')) { const p = next(); if (p.t === 'id' && !is(':') ) ps.push(p.v); else if (p.t === 'id') { ps.push(p.v); next(); next(); } }
          next(); next();
          return { k: 'fn', ps, body: fnBody() };
        }
        next();
        const e = expr();
        expect(')');
        return e;
      }
      if (t.t === 'id') {
        if (is('=>', 1) || is('->', 1)) { next(); next(); return { k: 'fn', ps: [t.v], body: fnBody() }; }
        next();
        return { k: 'id', v: t.v };
      }
      if (t.t === 'p' && t.v === '!') { next(); return { k: 'not', v: postfix(primary()) }; }
      if (t.t === 'p' && t.v === '-') { next(); const e = primary(); return { k: 'lit', v: -e.v }; }
      throw new Error(`I did not expect "${t.v}" here`);
    }
    function fnBody() {
      if (is('{')) {
        next();
        if (is('await') || is('return')) next();
        const e = expr();
        if (is(';')) next();
        expect('}');
        return e;
      }
      if (is('async')) next();
      return expr();
    }
    function postfix(e) {
      for (;;) {
        if (is('.') || is('?.')) { next(); const n = next(); e = { k: 'get', o: e, n: n.v }; continue; }
        if (is('(')) { next(); const a = args(')'); e = { k: 'call', f: e, args: a }; continue; }
        if (is('[') ) { next(); const ix = expr(); expect(']'); e = { k: 'idx', o: e, i: ix }; continue; }
        if (is('!') && lang === 'ts') { next(); continue; }
        if (is('as') && (lang === 'ts')) { next(); next(); continue; }
        return e;
      }
    }
    function unary() {
      if (is('async')) next();
      if (is('await') || is('Await')) { next(); }
      if (is('not') && lang === 'py') { next(); return { k: 'not', v: unary() }; }
      return postfix(primary());
    }
    function binary() {
      let e = unary();
      for (;;) {
        const t = peek();
        if (!t) return e;
        const op = t.v;
        if (t.t === 'p' && ['+', '==', '===', '!=', '!==', '>', '<', '>=', '<=', '&&', '||'].includes(op)) { next(); e = { k: 'bin', op, a: e, b: unary() }; continue; }
        if (t.t === 'id' && lang === 'py' && ['in', 'and', 'or'].includes(op)) { next(); e = { k: 'bin', op: op === 'and' ? '&&' : op === 'or' ? '||' : 'in', a: e, b: unary() }; continue; }
        if (t.t === 'id' && lang === 'py' && op === 'not' && is('in', 1)) { next(); next(); e = { k: 'not', v: { k: 'bin', op: 'in', a: e, b: unary() } }; continue; }
        return e;
      }
    }
    function expr() { return binary(); }
    function statement() {
      if (is('assert') && lang === 'py') { next(); const e = expr(); return { k: 'assert', e }; }
      if (peek() && peek().t === 'id' && /^(const|let|var|final|val)$/.test(peek().v)) {
        next();
        if (peek().t === 'id' && peek(1) && peek(1).t === 'id') next();
        const name = next().v;
        if (is(':') ) { next(); while (peek() && !is('=')) next(); }
        expect('=');
        return { k: 'let', name, e: expr() };
      }
      // Java and C# typed declarations: Locator button = ...   String text = ...   List<String> names = ...
      if (peek() && peek().t === 'id' && /^[A-Za-z]/.test(peek().v) && (lang === 'java' || lang === 'cs')) {
        let k = 1;
        if (is('<', 1)) { k = 2; let d = 1; while (peek(k) && d) { if (peek(k).v === '<') d++; if (peek(k).v === '>') d--; k++; } }
        if (is('[', k) && is(']', k + 1)) k += 2;
        if (peek(k) && peek(k).t === 'id' && is('=', k + 1)) { i += k; const name = next().v; next(); return { k: 'let', name, e: expr() }; }
      }
      if (peek() && peek().t === 'id' && is('=', 1) && lang === 'py') { const name = next().v; next(); return { k: 'let', name, e: expr() }; }
      if (peek() && peek().t === 'id' && peek().v === 'page' && is(':', 1) && lang === 'py') { next(); next(); next(); expect('='); return { k: 'let', name: 'page', e: expr() }; }
      const e = expr();
      if (is('+=')) { next(); return { k: 'sub', target: e, fn: expr() }; }
      if (is('=')) { next(); if (e.k === 'id') return { k: 'let', name: e.v, e: expr() }; }
      return { k: 'expr', e };
    }
    return { statement, done: () => i >= tokens.length || tokens.slice(i).every(t => t.v === ';') };
  }

  function parse(src, lang) {
    const stmts = splitStatements(src, lang);
    return stmts.map(s => {
      if (s.skip) return { ...s, k: 'skip' };
      if (SETUP.test(s.src)) return { ...s, k: 'setup' };
      try {
        const toks = lex(s.src, lang).map(t => ({ ...t, line: t.line + s.line - 1 }));
        const P = Parser(toks, lang);
        const node = P.statement();
        if (!P.done()) throw new Error('There is something extra at the end of this line');
        return { ...s, ...node };
      } catch (e) {
        return { ...s, k: 'error', msg: e.message };
      }
    });
  }

  /* ================= 3. names: every language maps onto one set of Playwright names ================= */
  const camel = s => s.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
  const snake = s => s.replace(/([A-Z])/g, '_$1').toLowerCase();
  const JAVA_ASSERT = { hasText: 'toHaveText', containsText: 'toContainText', isVisible: 'toBeVisible', isHidden: 'toBeHidden', isEnabled: 'toBeEnabled',
    isDisabled: 'toBeDisabled', isChecked: 'toBeChecked', hasCount: 'toHaveCount', hasValue: 'toHaveValue', hasValues: 'toHaveValues', hasAttribute: 'toHaveAttribute',
    hasClass: 'toHaveClass', containsClass: 'toContainClass', hasURL: 'toHaveURL', hasTitle: 'toHaveTitle', isEditable: 'toBeEditable', isFocused: 'toBeFocused', isEmpty: 'toBeEmpty',
    isAttached: 'toBeAttached', hasId: 'toHaveId', hasCSS: 'toHaveCSS', hasAccessibleName: 'toHaveAccessibleName', hasRole: 'toHaveRole', isInViewport: 'toBeInViewport',
    hasAccessibleDescription: 'toHaveAccessibleDescription', isOK: 'toBeOK' };
  const TO_JAVA = Object.fromEntries(Object.entries(JAVA_ASSERT).map(([a, b]) => [b, a]));
  function norm(name, lang) {
    let n = name;
    if (lang === 'cs') { n = n.replace(/Async$/, ''); n = n[0].toLowerCase() + n.slice(1); }
    if (lang === 'py') n = camel(n);
    if (lang === 'java' && n === 'navigate') n = 'goto';
    return n;
  }

  /* ================= 4. code generator: one parsed test, written in any of the five languages ================= */
  const ROLE_TYPES = { getByRole: 1 };
  const JAVA_OPT = { getByRole: 'GetByRoleOptions', getByText: 'GetByTextOptions', getByLabel: 'GetByLabelOptions', getByPlaceholder: 'GetByPlaceholderOptions',
    getByAltText: 'GetByAltTextOptions', getByTitle: 'GetByTitleOptions', filter: 'FilterOptions', locator: 'LocatorOptions', click: 'ClickOptions', fill: 'FillOptions',
    press: 'PressOptions', check: 'CheckOptions', hover: 'HoverOptions', dblclick: 'DblclickOptions', waitFor: 'WaitForOptions', goto: 'NavigateOptions',
    selectOption: 'SelectOptionOptions', screenshot: 'ScreenshotOptions', pressSequentially: 'PressSequentiallyOptions', dragTo: 'DragToOptions', setChecked: 'SetCheckedOptions' };
  const JAVA_AOPT = { toHaveText: 'HasTextOptions', toContainText: 'ContainsTextOptions', toBeVisible: 'IsVisibleOptions', toHaveCount: 'HasCountOptions', toHaveURL: 'HasURLOptions',
    toHaveTitle: 'HasTitleOptions', toBeHidden: 'IsHiddenOptions', toHaveValue: 'HasValueOptions', toBeEnabled: 'IsEnabledOptions', toBeChecked: 'IsCheckedOptions' };
  const STRINGY = /^(textContent|innerText|inputValue|getAttribute|title|url|innerHTML)$/;
  const BOOLY = /^(isVisible|isHidden|isEnabled|isDisabled|isChecked|isEditable)$/;

  function quote(s, lang) {
    const v = String(s);
    if (lang === 'js' || lang === 'ts') return "'" + v.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, '\\n') + "'";
    return '"' + v.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n') + '"';
  }
  function reGen(n, lang) {
    const ci = n.f && n.f.includes('i');
    if (lang === 'js' || lang === 'ts') return '/' + n.v + '/' + (n.f || '');
    if (lang === 'py') return `re.compile(r"${n.v.replace(/"/g, '\\"')}"${ci ? ', re.IGNORECASE' : ''})`;
    if (lang === 'java') return `Pattern.compile(${quote(n.v, lang)}${ci ? ', Pattern.CASE_INSENSITIVE' : ''})`;
    return `new Regex(${quote(n.v, lang)}${ci ? ', RegexOptions.IgnoreCase' : ''})`;
  }
  // Split a call chain into its root and a list of { name, args } steps.
  function flat(n) {
    const steps = [];
    let cur = n;
    while (cur) {
      if (cur.k === 'call' && cur.f.k === 'get') { steps.unshift({ name: cur.f.n, args: cur.args }); cur = cur.f.o; continue; }
      if (cur.k === 'get') { steps.unshift({ name: cur.n, prop: true }); cur = cur.o; continue; }
      break;
    }
    return { root: cur, steps };
  }
  function owner(prev) { return prev === 'page' ? 'Page' : prev === 'frame' ? 'FrameLocator' : 'Locator'; }
  function gen(n, lang, ctx = { owner: 'page' }) {
    if (!n) return '';
    switch (n.k) {
      case 'lit':
        if (typeof n.v === 'string') return quote(n.v, lang);
        if (n.v === null) return lang === 'py' ? 'None' : 'null';
        if (typeof n.v === 'boolean') return lang === 'py' ? (n.v ? 'True' : 'False') : String(n.v);
        return String(n.v);
      case 're': return reGen(n, lang);
      case 'id':
        if (lang === 'cs' && n.v === 'page') return 'Page';
        return n.v;
      case 'arr': {
        const items = n.v.map(x => gen(x, lang)).join(', ');
        if (lang === 'java') return `new String[] {${items}}`;
        if (lang === 'cs') return `new[] { ${items} }`;
        return `[${items}]`;
      }
      case 'obj': return genObjAsJs(n, lang);
      case 'bin': return `${gen(n.a, lang)} ${n.op} ${gen(n.b, lang)}`;
      case 'not': return (lang === 'py' ? 'not ' : '!') + gen(n.v, lang);
      case 'fn': {
        const p = n.ps[0] || 'x';
        if (lang === 'py') return `lambda ${p}: ${gen(n.body, lang)}`;
        if (lang === 'java') return `${p} -> ${gen(n.body, lang)}`;
        if (lang === 'cs') return `async (_, ${p}) => await ${gen(n.body, lang)}`;
        return `${p} => ${gen(n.body, lang)}`;
      }
      case 'call': case 'get': return genChain(n, lang);
      default: return '/* ? */';
    }
  }
  function genObjAsJs(n, lang) {
    const kv = Object.entries(n.v).map(([k, v]) => `${k}: ${gen(v, lang)}`).join(', ');
    return `{ ${kv} }`;
  }
  function optsFor(method, optNode, lang, own) {
    if (!optNode || optNode.k !== 'obj') return null;
    const ent = Object.entries(optNode.v);
    if (!ent.length) return null;
    if (lang === 'py') return ent.map(([k, v]) => `${snake(k)}=${gen(v, lang)}`).join(', ');
    if (lang === 'java') {
      const cls = JAVA_AOPT[method] ? `LocatorAssertions.${JAVA_AOPT[method]}` : `${own}.${JAVA_OPT[method] || (method[0].toUpperCase() + method.slice(1) + 'Options')}`;
      return `new ${cls}()` + ent.map(([k, v]) => `.set${k[0].toUpperCase()}${k.slice(1)}(${gen(v, lang)})`).join('');
    }
    if (lang === 'cs') return 'new() { ' + ent.map(([k, v]) => `${k[0].toUpperCase()}${k.slice(1)} = ${gen(v, lang)}`).join(', ') + ' }';
    return `{ ${ent.map(([k, v]) => `${k}: ${gen(v, lang)}`).join(', ')} }`;
  }
  function genArgs(method, args, lang, own) {
    const pos = args.pos.slice();
    let opt = null;
    if (pos.length && pos[pos.length - 1].k === 'obj' && method !== 'fulfill' && method !== 'evaluate') opt = pos.pop();
    const parts = pos.map((a, k) => {
      if (method === 'getByRole' && k === 0 && a.k === 'lit') {
        if (lang === 'java') return 'AriaRole.' + String(a.v).toUpperCase();
        if (lang === 'cs') return 'AriaRole.' + String(a.v)[0].toUpperCase() + String(a.v).slice(1);
      }
      return gen(a, lang);
    });
    const o = optsFor(method, opt, lang, own);
    if (o) parts.push(o);
    if (opt && method === 'fulfill') parts.push(gen(opt, lang));
    return parts.join(', ');
  }
  function genChain(n, lang) {
    const { root, steps } = flat(n);
    // expect(x).not.toHaveText(...)
    if (root && root.k === 'call' && root.f.k === 'id' && /^(expect|assertThat|Expect)$/.test(root.f.v)) {
      const target = root.args.pos[0];
      const neg = steps.some(s => s.name === 'not' || s.name === 'Not');
      const m = steps.filter(s => s.name !== 'not' && s.name !== 'Not').pop();
      const isLoc = isLocatorExpr(target);
      const t = gen(target, lang);
      if (!m) return t;
      if (!isLoc && !/^(page|Page)$/.test(target.v || '') && !(target.k === 'call' && /response|request/i.test(gen(target, 'js')))) return genGenericAssert(t, m, lang, neg);
      const a = m.args ? genArgs(m.name, m.args, lang, 'Locator') : '';
      if (lang === 'py') return `expect(${t}).${neg ? 'not_' : ''}${snake(m.name)}(${a})`;
      if (lang === 'java') return `assertThat(${t})${neg ? '.not()' : ''}.${TO_JAVA[m.name] || m.name}(${a})`;
      if (lang === 'cs') return `await Expect(${t})${neg ? '.Not' : ''}.${m.name[0].toUpperCase() + m.name.slice(1)}Async(${a})`;
      return `await expect(${t})${neg ? '.not' : ''}.${m.name}(${a})`;
    }
    let out = gen(root, lang);
    let own = root && root.k === 'id' && root.v === 'page' ? 'page' : 'loc';
    let awaited = false;
    steps.forEach((s, k) => {
      let name = s.name;
      if (s.prop) {
        if (lang === 'py' && /^(first|last)$/.test(name)) { out += '.' + name; return; }
        if (lang === 'cs') { out += '.' + name[0].toUpperCase() + name.slice(1); return; }
        if (lang === 'java' && /^(first|last|keyboard|mouse)$/.test(name)) { out += '.' + name + '()'; return; }
        out += '.' + name;
        return;
      }
      const action = !/^(getBy\w+|locator|filter|nth|first|last|and|or|frameLocator|contentFrame|within|visible|describe|keyboard|mouse)$/.test(name);
      const a = genArgs(name, s.args || { pos: [], named: {} }, lang, owner(own === 'page' ? 'page' : own));
      if (name === 'frameLocator') own = 'frame'; else if (/^(getBy|locator|filter|nth|first|last|and|or)/.test(name)) own = own === 'frame' && /^getBy|^locator/.test(name) ? 'loc' : own === 'page' ? 'loc' : own;
      if (lang === 'py') {
        if (/^(first|last)$/.test(name)) out += '.' + name;
        else out += '.' + snake(name) + '(' + a + ')';
      } else if (lang === 'java') {
        out += '.' + (name === 'goto' ? 'navigate' : name) + '(' + a + ')';
      } else if (lang === 'cs') {
        const N = name[0].toUpperCase() + name.slice(1);
        if (/^(first|last)$/.test(name)) out += '.' + N;
        else out += '.' + N + (action ? 'Async' : '') + '(' + a + ')';
      } else {
        out += '.' + name + '(' + a + ')';
      }
      if (action && k === steps.length - 1) awaited = true;
    });
    if (awaited && (lang === 'js' || lang === 'ts' || lang === 'cs')) out = 'await ' + out;
    return out;
  }
  function isLocatorExpr(n) {
    const { root, steps } = flat(n || {});
    if (root && root.k === 'id' && root.v !== 'page' && root.v !== 'Page') return !steps.length || steps.every(s => /^(getBy|locator|filter|nth|first|last|and|or|frameLocator)/.test(s.name));
    return steps.length > 0 && steps.every(s => /^(getBy|locator|filter|nth|first|last|and|or|frameLocator|within|visible)/.test(s.name) || s.prop);
  }
  function genGenericAssert(t, m, lang, neg) {
    const v = m.args && m.args.pos[0] ? gen(m.args.pos[0], lang) : '';
    const name = m.name;
    if (lang === 'py') {
      if (name === 'toBe' || name === 'toEqual') return `assert ${t} ${neg ? '!=' : '=='} ${v}`;
      if (name === 'toContain') return `assert ${v} ${neg ? 'not in' : 'in'} ${t}`;
      if (name === 'toBeTruthy') return `assert ${neg ? 'not ' : ''}${t}`;
      if (name === 'toBeGreaterThan') return `assert ${t} > ${v}`;
    }
    if (lang === 'java') {
      if (name === 'toBe' || name === 'toEqual') return `${neg ? 'assertNotEquals' : 'assertEquals'}(${v}, ${t})`;
      if (name === 'toContain') return `assertTrue(${neg ? '!' : ''}${t}.contains(${v}))`;
      if (name === 'toBeTruthy') return `assertTrue(${neg ? '!' : ''}${t})`;
      if (name === 'toBeGreaterThan') return `assertTrue(${t} > ${v})`;
    }
    if (lang === 'cs') {
      if (name === 'toBe' || name === 'toEqual') return `Assert.That(${t}, Is.${neg ? 'Not.' : ''}EqualTo(${v}))`;
      if (name === 'toContain') return `Assert.That(${t}, ${neg ? 'Does.Not.Contain' : 'Does.Contain'}(${v}))`;
      if (name === 'toBeTruthy') return `Assert.That(${t}, Is.${neg ? 'False' : 'True'})`;
      if (name === 'toBeGreaterThan') return `Assert.That(${t}, Is.GreaterThan(${v}))`;
    }
    return `expect(${t})${neg ? '.not' : ''}.${name}(${v})`;
  }
  function genStatement(s, lang, vars) {
    if (s.k === 'let') {
      const rhs = gen(s.e, lang);
      const { steps } = flat(s.e);
      const last = steps.length ? steps[steps.length - 1].name : '';
      if (lang === 'py') return `${s.name} = ${rhs}`;
      if (lang === 'java') {
        const type = isLocatorExpr(s.e) ? 'Locator' : STRINGY.test(last) ? 'String' : last === 'count' ? 'int' : BOOLY.test(last) ? 'boolean' : /allTextContents|allInnerTexts/.test(last) ? 'List<String>' : 'var';
        vars[s.name] = type;
        return `${type} ${s.name} = ${rhs};`;
      }
      if (lang === 'cs') return `var ${s.name} = ${rhs};`;
      return `const ${s.name} = ${rhs};`;
    }
    if (s.k === 'expr') {
      const e = s.e;
      // console.log(x)  print(x)  System.out.println(x)
      if (e.k === 'call' && isPrint(e.f)) {
        const v = e.args.pos.map(x => gen(x, lang)).join(lang === 'py' ? ', ' : ' + ');
        if (lang === 'py') return `print(${v})`;
        if (lang === 'java') return `System.out.println(${v});`;
        if (lang === 'cs') return `Console.WriteLine(${v});`;
        return `console.log(${v});`;
      }
      // page.on('dialog', d => d.accept())
      if (e.k === 'call' && e.f.k === 'get' && e.f.n === 'on' && e.args.pos[0] && e.args.pos[0].v === 'dialog') {
        const fn = e.args.pos[1];
        const act = fn ? gen(fn.body, lang) : 'dialog.accept()';
        const p = fn && fn.ps[0] ? fn.ps[0] : 'dialog';
        if (lang === 'py') return `page.on("dialog", lambda ${p}: ${act})`;
        if (lang === 'java') return `page.onDialog(${p} -> ${act});`;
        if (lang === 'cs') return `Page.Dialog += async (_, ${p}) => ${act};`;
        return `page.on('dialog', ${p} => ${act});`;
      }
      const code = gen(e, lang);
      return lang === 'py' ? code : code + ';';
    }
    if (s.k === 'assert') return lang === 'py' ? 'assert ' + gen(s.e, lang) : `// assert ${gen(s.e, 'js')}`;
    return '';
  }
  const isPrint = f => (f.k === 'id' && /^print$/.test(f.v)) || (f.k === 'get' && /^(log|println|WriteLine)$/.test(f.n));
  function genStatements(stmts, lang) {
    const vars = {};
    return stmts.filter(s => s.k === 'let' || s.k === 'expr' || s.k === 'assert').map(s => ({ line: s.line, code: genStatement(s, lang, vars) }));
  }
  const pascal = s => s.replace(/(^|[^A-Za-z0-9])([a-z])/g, (_, a, c) => c.toUpperCase()).replace(/[^A-Za-z0-9]/g, '');
  function wrap(lang, name, body, opts = {}) {
    const ind = n => body.map(l => (l ? ' '.repeat(n) + l : '')).join('\n');
    const cls = opts.cls || pascal(name) + 'Test';
    const needRe = body.some(l => /re\.compile|Pattern\.compile|new Regex/.test(l));
    if (lang === 'py') return `${needRe ? 'import re\n' : ''}from playwright.sync_api import Page, expect\n\n\ndef test_${snake(name.replace(/[^A-Za-z0-9]+/g, '_')).replace(/_+/g, '_').replace(/^_|_$/g, '')}(page: Page):\n${ind(4)}\n`;
    if (lang === 'java') {
      const im = ['import com.microsoft.playwright.*;', 'import com.microsoft.playwright.junit.UsePlaywright;'];
      if (body.some(l => l.includes('AriaRole'))) im.push('import com.microsoft.playwright.options.AriaRole;');
      if (body.some(l => l.includes('LocatorAssertions'))) im.push('import com.microsoft.playwright.assertions.LocatorAssertions;');
      im.push('import org.junit.jupiter.api.Test;');
      if (needRe) im.push('import java.util.regex.Pattern;');
      if (body.some(l => l.includes('List<String>'))) im.push('import java.util.List;');
      const st = ['import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;'];
      if (body.some(l => /assert(Equals|True|NotEquals)\(/.test(l))) st.push('import static org.junit.jupiter.api.Assertions.*;');
      const m = name.replace(/[^A-Za-z0-9]+(.)/g, (_, c) => c.toUpperCase()).replace(/^./, c => c.toLowerCase()).replace(/[^A-Za-z0-9]/g, '');
      return `package com.brainy;\n\n${im.join('\n')}\n\n${st.join('\n')}\n\n@UsePlaywright(ShopOptions.class)\npublic class ${cls} {\n  @Test\n  void ${m}(Page page) {\n${ind(4)}\n  }\n}\n`;
    }
    if (lang === 'cs') return `using System.Text.RegularExpressions;\nusing Microsoft.Playwright;\nusing Microsoft.Playwright.NUnit;\n\n[TestFixture]\npublic class ${cls.replace(/Test$/, 'Tests')} : PageTest\n{\n    [Test]\n    public async Task ${pascal(name)}()\n    {\n${ind(8)}\n    }\n}\n`;
    return `import { test, expect } from '@playwright/test';\n\ntest(${quote(name, 'js')}, async ({ page }) => {\n${ind(2)}\n});\n`;
  }
  // Rewrite a statement read from any language into the JavaScript names, so the generator can write it again.
  function canon(n, lang) {
    if (!n || typeof n !== 'object') return n;
    const C = x => canon(x, lang);
    switch (n.k) {
      case 'id': return lang === 'cs' && n.v === 'Page' ? { k: 'id', v: 'page' } : /^(assertThat|Expect)$/.test(n.v) ? { k: 'id', v: 'expect' } : n;
      case 'arr': return { k: 'arr', v: n.v.map(C) };
      case 'bin': return { ...n, a: C(n.a), b: C(n.b) };
      case 'not': return { k: 'not', v: C(n.v) };
      case 'fn': return { ...n, ps: lang === 'cs' ? n.ps.slice(-1) : n.ps, body: C(n.body) };
      case 'obj': return { k: 'obj', v: Object.fromEntries(Object.entries(n.v).map(([k, v]) => [lang === 'cs' ? k[0].toLowerCase() + k.slice(1) : lang === 'py' ? camel(k) : k, C(v)])) };
      case 'new': {
        const name = n.name.split('.').pop();
        if (name === 'Regex') return { k: 're', v: n.args.pos[0].v, f: n.args.pos[1] ? 'i' : '' };
        if (/Options$/.test(name)) return n.init ? C(n.init) : { k: 'obj', v: {} };
        return n;
      }
      case 'get': {
        const o = C(n.o);
        if (o.k === 'id' && o.v === 'AriaRole') return { k: 'lit', v: n.n.toLowerCase() };
        if (o.k === 'id' && /^(re|Pattern|RegexOptions)$/.test(o.v)) return { k: 'lit', v: n.n };
        let m = norm(n.n, lang);
        if (lang === 'cs' && m === 'not') return { k: 'get', o, n: 'not' };
        if ((lang === 'py' || lang === 'cs') && /^(first|last)$/.test(m)) return { k: 'call', f: { k: 'get', o, n: m }, args: { pos: [], named: {} } };
        return { k: 'get', o, n: m };
      }
      case 'call': {
        if (n.f.k === 'get' && n.f.o.k === 'id' && /^(re|Pattern)$/.test(n.f.o.v) && n.f.n === 'compile') return { k: 're', v: n.args.pos[0].v, f: n.args.pos[1] ? 'i' : '' };
        const pos = n.args.pos.map(C);
        const named = Object.entries(n.args.named);
        if (named.length) pos.push({ k: 'obj', v: Object.fromEntries(named.map(([k, v]) => [lang === 'py' ? camel(k) : k[0].toLowerCase() + k.slice(1), C(v)])) });
        if (n.f.k === 'get') {
          const o = C(n.f.o);
          // Java option builders: new Page.GetByRoleOptions().setName("x") becomes { name: 'x' }
          if (/^set[A-Z]/.test(n.f.n) && o.k === 'obj') return { k: 'obj', v: { ...o.v, [n.f.n[3].toLowerCase() + n.f.n.slice(4)]: pos[0] } };
          let m = norm(n.f.n, lang);
          if (m === 'not' && !pos.length) return { k: 'get', o, n: 'not' };
          if (/^(first|last)$/.test(m) && o.k === 'call' && o.f.k === 'get' && o.f.n === m) return o;
          if (expectRoot(o)) {
            if (lang === 'java' && JAVA_ASSERT[m]) m = JAVA_ASSERT[m];
            if (lang === 'py' && /^not[A-Z]/.test(m)) return { k: 'call', f: { k: 'get', o: { k: 'get', o, n: 'not' }, n: m[3].toLowerCase() + m.slice(4) }, args: { pos, named: {} } };
          }
          if (lang === 'java' && m === 'onDialog') return { k: 'call', f: { k: 'get', o, n: 'on' }, args: { pos: [{ k: 'lit', v: 'dialog' }, ...pos], named: {} } };
          return { k: 'call', f: { k: 'get', o, n: m }, args: { pos, named: {} } };
        }
        return { k: 'call', f: C(n.f), args: { pos, named: {} } };
      }
      default: return n;
    }
  }
  function expectRoot(o) {
    let c = o;
    while (c) {
      if (c.k === 'call' && c.f.k === 'id' && c.f.v === 'expect') return true;
      c = c.k === 'get' ? c.o : c.k === 'call' && c.f.k === 'get' ? c.f.o : null;
    }
    return false;
  }
  function canonStatement(s, lang) {
    if (s.k === 'let' || s.k === 'expr' || s.k === 'assert') return { ...s, e: canon(s.e, lang) };
    if (s.k === 'sub' && lang === 'cs') {
      const fn = canon(s.fn, lang);
      return { ...s, k: 'expr', e: { k: 'call', f: { k: 'get', o: { k: 'id', v: 'page' }, n: 'on' }, args: { pos: [{ k: 'lit', v: /Dialog/.test(s.target.n) ? 'dialog' : 'console' }, fn], named: {} } } };
    }
    return s;
  }
  function translate(src, from, to, name = 'my test') {
    const st = parse(src, from);
    const bad = st.find(s => s.k === 'error');
    if (bad) throw new Error(`Line ${bad.line}: ${bad.msg}`);
    return wrap(to, name, genStatements(st.map(s => canonStatement(s, from)), to).map(x => x.code));
  }

  /* ================= 5. locator engine ================= */
  const IMPLICIT = (el) => {
    const tag = el.tagName.toLowerCase(), type = (el.getAttribute('type') || '').toLowerCase();
    const r = el.getAttribute('role');
    if (r) return r.split(' ')[0];
    if (tag === 'button' || (tag === 'input' && ['button', 'submit', 'reset', 'image'].includes(type)) || tag === 'summary') return 'button';
    if (tag === 'a' && el.hasAttribute('href')) return 'link';
    if (tag === 'input') {
      if (type === 'checkbox') return 'checkbox';
      if (type === 'radio') return 'radio';
      if (type === 'range') return 'slider';
      if (type === 'number') return 'spinbutton';
      if (type === 'search') return 'searchbox';
      if (['hidden', 'file', 'date', 'color', 'time'].includes(type)) return type === 'hidden' ? null : (type === 'file' ? 'button' : 'textbox');
      return 'textbox';
    }
    if (tag === 'textarea') return 'textbox';
    if (tag === 'select') return el.multiple || +el.size > 1 ? 'listbox' : 'combobox';
    if (tag === 'option') return 'option';
    if (/^h[1-6]$/.test(tag)) return 'heading';
    if (tag === 'img') return el.getAttribute('alt') === '' ? 'presentation' : 'img';
    if (tag === 'ul' || tag === 'ol') return 'list';
    if (tag === 'li') return 'listitem';
    if (tag === 'nav') return 'navigation';
    if (tag === 'main') return 'main';
    if (tag === 'header') return el.closest('main,article,section') ? null : 'banner';
    if (tag === 'footer') return 'contentinfo';
    if (tag === 'form') return el.hasAttribute('aria-label') || el.hasAttribute('aria-labelledby') ? 'form' : null;
    if (tag === 'section') return el.hasAttribute('aria-label') || el.hasAttribute('aria-labelledby') ? 'region' : null;
    if (tag === 'table') return 'table';
    if (tag === 'tr') return 'row';
    if (tag === 'td') return 'cell';
    if (tag === 'th') return el.getAttribute('scope') === 'row' ? 'rowheader' : 'columnheader';
    if (tag === 'thead' || tag === 'tbody' || tag === 'tfoot') return 'rowgroup';
    if (tag === 'dialog') return 'dialog';
    if (tag === 'fieldset') return 'group';
    if (tag === 'output') return 'status';
    if (tag === 'article') return 'article';
    if (tag === 'progress') return 'progressbar';
    if (tag === 'iframe') return 'iframe';
    if (tag === 'p') return 'paragraph';
    if (tag === 'dl') return null;
    return null;
  };
  const NAME_FROM_CONTENT = new Set(['button', 'link', 'heading', 'cell', 'columnheader', 'rowheader', 'checkbox', 'radio', 'option', 'tab', 'menuitem', 'treeitem', 'switch', 'listitem', 'row', 'tooltip']);
  const norms = s => String(s || '').replace(/\s+/g, ' ').trim();
  function textOf(el) {
    if (el.nodeType === 3) return el.nodeValue;
    if (el.nodeType !== 1) return '';
    const tag = el.tagName.toLowerCase();
    if (tag === 'script' || tag === 'style' || tag === 'template') return '';
    let s = '';
    if (el.shadowRoot) for (const c of el.shadowRoot.childNodes) s += textOf(c);
    for (const c of el.childNodes) {
      if (c.nodeType === 1 && c.tagName === 'SLOT') continue;
      s += textOf(c);
    }
    return s;
  }
  function hidden(el) {
    if (!el || !el.isConnected) return true;
    const win = el.ownerDocument.defaultView;
    let e = el;
    while (e && e.nodeType === 1) {
      const cs = win.getComputedStyle(e);
      if (cs.display === 'none') return true;
      if (e.hidden) return true;
      e = e.parentElement || (e.getRootNode() && e.getRootNode().host) || null;
    }
    const cs = win.getComputedStyle(el);
    if (cs.visibility === 'hidden') return true;
    const r = el.getBoundingClientRect();
    return r.width === 0 && r.height === 0 && el.tagName !== 'OPTION';
  }
  function accName(el) {
    const doc = el.getRootNode();
    const lb = el.getAttribute('aria-labelledby');
    if (lb) return norms(lb.split(/\s+/).map(id => { const x = (doc.getElementById ? doc.getElementById(id) : null) || el.ownerDocument.getElementById(id); return x ? textOf(x) : ''; }).join(' '));
    const al = el.getAttribute('aria-label');
    if (al && al.trim()) return norms(al);
    const tag = el.tagName.toLowerCase();
    if (['input', 'select', 'textarea'].includes(tag)) {
      const type = (el.getAttribute('type') || '').toLowerCase();
      if (['button', 'submit', 'reset'].includes(type)) return norms(el.value || (type === 'submit' ? 'Submit' : type === 'reset' ? 'Reset' : ''));
      const labels = el.labels ? [...el.labels] : [];
      if (labels.length) return norms(labels.map(l => labelText(l, el)).join(' '));
      if (el.title) return norms(el.title);
      if (el.placeholder) return norms(el.placeholder);
      return '';
    }
    if (tag === 'img') return norms(el.getAttribute('alt') || el.getAttribute('title') || '');
    if (tag === 'fieldset') { const lg = el.querySelector('legend'); if (lg) return norms(textOf(lg)); }
    if (tag === 'table') { const cp = el.querySelector('caption'); if (cp) return norms(textOf(cp)); }
    const role = IMPLICIT(el);
    if (NAME_FROM_CONTENT.has(role)) return norms(nameFromContent(el));
    if (el.title) return norms(el.title);
    return '';
  }
  function nameFromContent(el) {
    let s = '';
    const kids = el.shadowRoot ? [...el.shadowRoot.childNodes] : [...el.childNodes];
    for (const c of kids) {
      if (c.nodeType === 3) s += c.nodeValue;
      else if (c.nodeType === 1) {
        if (hidden(c)) continue;
        if (c.tagName === 'SLOT') { for (const a of c.assignedNodes()) s += a.nodeType === 3 ? a.nodeValue : nameFromContent(a); continue; }
        const al = c.getAttribute('aria-label');
        if (al) s += ' ' + al + ' ';
        else if (c.tagName === 'IMG') s += c.getAttribute('alt') || '';
        else s += ' ' + nameFromContent(c) + ' ';
      }
    }
    return s;
  }
  function labelText(label, control) {
    let s = '';
    for (const c of label.childNodes) {
      if (c === control || (c.nodeType === 1 && c.contains(control))) { if (c !== control) s += labelText(c, control); continue; }
      if (c.nodeType === 1 && /^(INPUT|SELECT|TEXTAREA)$/.test(c.tagName)) continue;
      s += c.nodeType === 3 ? c.nodeValue : textOf(c);
    }
    return s;
  }
  function textMatch(actual, want, exact) {
    const a = norms(actual);
    if (want instanceof RegExp) return want.test(a);
    const w = norms(want);
    return exact ? a === w : a.toLowerCase().includes(w.toLowerCase());
  }
  function allEls(root) {
    const out = [];
    const walk = node => {
      for (const el of node.querySelectorAll('*')) {
        out.push(el);
        if (el.shadowRoot) walk(el.shadowRoot);
      }
    };
    walk(root);
    return out;
  }
  function checkedState(el) {
    if (el.type === 'checkbox' || el.type === 'radio') return el.checked;
    const a = el.getAttribute('aria-checked');
    return a === 'true' ? true : a === 'false' ? false : undefined;
  }
  const BY = {
    getByRole(root, role, o = {}) {
      return allEls(root).filter(el => {
        if (IMPLICIT(el) !== role) return false;
        if (!o.includeHidden && hidden(el)) return false;
        if (o.name !== undefined && !textMatch(accName(el), o.name, o.exact)) return false;
        if (o.checked !== undefined && checkedState(el) !== o.checked) return false;
        if (o.disabled !== undefined && !!(el.disabled || el.getAttribute('aria-disabled') === 'true') !== o.disabled) return false;
        if (o.level !== undefined && Number((el.tagName.match(/^H(\d)$/) || [])[1] || el.getAttribute('aria-level')) !== o.level) return false;
        if (o.selected !== undefined && !!(el.selected || el.getAttribute('aria-selected') === 'true') !== o.selected) return false;
        if (o.expanded !== undefined && (el.getAttribute('aria-expanded') === 'true') !== o.expanded) return false;
        if (o.pressed !== undefined && (el.getAttribute('aria-pressed') === 'true') !== o.pressed) return false;
        return true;
      });
    },
    getByText(root, text, o = {}) {
      const cands = allEls(root).filter(el => !/^(SCRIPT|STYLE|HEAD|TITLE|HTML|BODY|OPTION|TEMPLATE)$/.test(el.tagName) && textMatch(textOf(el), text, o.exact));
      return cands.filter(el => !cands.some(c => c !== el && el.contains(c)) && !(el.shadowRoot && cands.some(c => el.shadowRoot.contains(c))));
    },
    getByLabel(root, text, o = {}) {
      return allEls(root).filter(el => {
        if (!/^(INPUT|SELECT|TEXTAREA)$/.test(el.tagName) && !el.hasAttribute('aria-label') && !el.hasAttribute('aria-labelledby')) return false;
        const labels = el.labels ? [...el.labels].map(l => labelText(l, el)) : [];
        const names = [...labels, el.getAttribute('aria-label') || ''];
        const lb = el.getAttribute('aria-labelledby');
        if (lb) names.push(accName(el));
        return names.some(n => n && textMatch(n, text, o.exact));
      });
    },
    getByPlaceholder: (root, text, o = {}) => allEls(root).filter(el => el.hasAttribute('placeholder') && textMatch(el.getAttribute('placeholder'), text, o.exact)),
    getByAltText: (root, text, o = {}) => allEls(root).filter(el => el.hasAttribute('alt') && textMatch(el.getAttribute('alt'), text, o.exact)),
    getByTitle: (root, text, o = {}) => allEls(root).filter(el => el.hasAttribute('title') && textMatch(el.getAttribute('title'), text, o.exact)),
    getByTestId: (root, id) => allEls(root).filter(el => id instanceof RegExp ? id.test(el.getAttribute(TESTID.attr) || '') : el.getAttribute(TESTID.attr) === id),
  };
  const TESTID = { attr: 'data-testid' };
  function css(root, sel) {
    if (/^(xpath=|\/\/|\.\.)/.test(sel)) {
      const doc = root.ownerDocument || root;
      const r = doc.evaluate(sel.replace(/^xpath=/, ''), root.nodeType === 9 ? root : root, null, 7, null);
      const out = [];
      for (let k = 0; k < r.snapshotLength; k++) out.push(r.snapshotItem(k));
      return out;
    }
    if (/^text=/.test(sel)) { const t = sel.slice(5).replace(/^"|"$/g, ''); return BY.getByText(root, t, { exact: /^text="/.test(sel) }); }
    if (/^(id|data-testid)=/.test(sel)) { const [k, v] = sel.split('='); return [...root.querySelectorAll(k === 'id' ? '#' + v : `[data-testid="${v}"]`)]; }
    let s = sel.replace(/^css=/, '');
    let vis = false;
    if (/:visible$/.test(s)) { vis = true; s = s.replace(/:visible$/, ''); }
    const hasText = s.match(/^(.*):has-text\((['"])(.*)\2\)$/);
    let found;
    if (hasText) found = css(root, hasText[1]).filter(el => textMatch(textOf(el), hasText[3]));
    else {
      found = [...root.querySelectorAll(s)];
      for (const el of allEls(root)) if (el.shadowRoot) found.push(...el.shadowRoot.querySelectorAll(s));
    }
    return vis ? found.filter(el => !hidden(el)) : found;
  }
  function describeArgs(args) {
    return args.map(a => a instanceof RegExp ? String(a) : typeof a === 'object' && a !== null ? '{ ' + Object.entries(a).map(([k, v]) => `${k}: ${v instanceof RegExp ? String(v) : JSON.stringify(v).replace(/"/g, "'")}`).join(', ') + ' }' : JSON.stringify(a).replace(/"/g, "'")).join(', ');
  }

  class Locator {
    constructor(page, steps, frame) { this._page = page; this._steps = steps; this._frame = frame || null; }
    _with(step) { return new Locator(this._page, [...this._steps, step], this._frame); }
    toString() { return this._steps.map(s => s.desc).join('.'); }
    _resolve() {
      const doc = this._page._doc();
      if (!doc) return [];
      let set = [doc];
      for (const s of this._steps) {
        if (s.k === 'frame') {
          set = set.flatMap(r => css(r, s.sel)).map(f => { try { return f.contentDocument; } catch (e) { return null; } }).filter(Boolean);
          continue;
        }
        if (s.k === 'pick') { set = s.fn(set); continue; }
        if (s.k === 'filter') { set = set.filter(s.fn); continue; }
        if (s.k === 'and') { const other = new Set(s.other._resolve()); set = set.filter(e => other.has(e)); continue; }
        if (s.k === 'or') { const other = s.other._resolve(); set = [...new Set([...set, ...other])].sort((a, b) => (a.compareDocumentPosition(b) & 4 ? -1 : 1)); continue; }
        const next = [];
        for (const r of set) for (const el of s.find(r.nodeType === 9 ? r : r)) if (!next.includes(el) && (r.nodeType === 9 || r !== el)) next.push(el);
        set = next;
      }
      return set.filter(x => x && x.nodeType === 1);
    }
    getByRole(role, o = {}) { return this._with({ desc: `getByRole(${describeArgs([role, ...(Object.keys(o).length ? [o] : [])])})`, find: r => BY.getByRole(r, role, o) }); }
    getByText(t, o = {}) { return this._with({ desc: `getByText(${describeArgs([t, ...(Object.keys(o).length ? [o] : [])])})`, find: r => BY.getByText(r, t, o) }); }
    getByLabel(t, o = {}) { return this._with({ desc: `getByLabel(${describeArgs([t, ...(Object.keys(o).length ? [o] : [])])})`, find: r => BY.getByLabel(r, t, o) }); }
    getByPlaceholder(t, o = {}) { return this._with({ desc: `getByPlaceholder(${describeArgs([t])})`, find: r => BY.getByPlaceholder(r, t, o) }); }
    getByAltText(t, o = {}) { return this._with({ desc: `getByAltText(${describeArgs([t])})`, find: r => BY.getByAltText(r, t, o) }); }
    getByTitle(t, o = {}) { return this._with({ desc: `getByTitle(${describeArgs([t])})`, find: r => BY.getByTitle(r, t, o) }); }
    getByTestId(t) { return this._with({ desc: `getByTestId(${describeArgs([t])})`, find: r => BY.getByTestId(r, t) }); }
    locator(sel, o = {}) {
      let l = this._with({ desc: `locator(${describeArgs([sel])})`, find: r => css(r, sel) });
      if (o.hasText !== undefined || o.has || o.hasNot || o.hasNotText !== undefined) l = l.filter(o);
      return l;
    }
    frameLocator(sel) { return new FrameLocator(this._page, [...this._steps, { k: 'frame', sel, desc: `frameLocator(${describeArgs([sel])})` }], this._frame); }
    contentFrame() { const s = this._steps[this._steps.length - 1]; return new FrameLocator(this._page, [...this._steps.slice(0, -1), { k: 'frame', sel: 'iframe', desc: s.desc + '.contentFrame()' }]); }
    filter(o = {}) {
      const fns = [];
      if (o.hasText !== undefined) fns.push(el => textMatch(textOf(el), o.hasText));
      if (o.hasNotText !== undefined) fns.push(el => !textMatch(textOf(el), o.hasNotText));
      if (o.has) fns.push(el => o.has._resolveIn(el).length > 0);
      if (o.hasNot) fns.push(el => o.hasNot._resolveIn(el).length === 0);
      if (o.visible !== undefined) fns.push(el => hidden(el) !== o.visible);
      return this._with({ k: 'filter', desc: `filter(${describeArgs([Object.fromEntries(Object.entries(o).map(([k, v]) => [k, v instanceof Locator ? v.toString() : v]))])})`, fn: el => fns.every(f => f(el)) });
    }
    _resolveIn(el) {
      let set = [el];
      for (const s of this._steps) {
        if (s.find) { const next = []; for (const r of set) for (const x of s.find(r)) if (x !== r && !next.includes(x)) next.push(x); set = next; }
        else if (s.k === 'filter') set = set.filter(s.fn);
        else if (s.k === 'pick') set = s.fn(set);
      }
      return set;
    }
    nth(i) { return this._with({ k: 'pick', desc: `nth(${i})`, fn: s => (i < 0 ? (s[s.length + i] ? [s[s.length + i]] : []) : s[i] ? [s[i]] : []) }); }
    first() { return this._with({ k: 'pick', desc: 'first()', fn: s => s.slice(0, 1) }); }
    last() { return this._with({ k: 'pick', desc: 'last()', fn: s => s.slice(-1) }); }
    visible(v = true) { return this.filter({ visible: v }); }
    and(other) { return this._with({ k: 'and', desc: `and(${other})`, other }); }
    or(other) { return this._with({ k: 'or', desc: `or(${other})`, other }); }
    within(parent) { return new Locator(this._page, [...parent._steps, ...this._steps], this._frame); }
    describe(text) { const l = this._with({ k: 'pick', desc: `describe(${describeArgs([text])})`, fn: s => s }); l._name = text; return l; }

    async _one(action, opts = {}) {
      return this._page._rt.waitFor(this, action, opts);
    }
    async click(o = {}) { const el = await this._one('click', { ...o, need: ['visible', 'stable', 'enabled', 'events'] }); await this._page._rt.doClick(el, o); }
    async dblclick(o = {}) { const el = await this._one('dblclick', { ...o, need: ['visible', 'stable', 'enabled', 'events'] }); await this._page._rt.doClick(el, o); await this._page._rt.doClick(el, o); el.dispatchEvent(new el.ownerDocument.defaultView.MouseEvent('dblclick', { bubbles: true })); }
    async fill(v, o = {}) { const el = await this._one('fill', { ...o, arg: String(v), need: ['visible', 'enabled', 'editable'] }); this._page._rt.doFill(el, String(v)); }
    async clear(o = {}) { return this.fill('', o); }
    async type(v, o = {}) { return this.pressSequentially(v, o); }
    async pressSequentially(v, o = {}) {
      const el = await this._one('pressSequentially', { ...o, arg: String(v), need: ['visible'] });
      el.focus();
      for (const ch of String(v)) { this._page._rt.key(el, ch); el.value = (el.value || '') + ch; el.dispatchEvent(new Event('input', { bubbles: true })); if (o.delay) await sleep(Math.min(o.delay, 200)); }
      el.dispatchEvent(new Event('change', { bubbles: true }));
    }
    async press(key, o = {}) { const el = await this._one('press', { ...o, arg: key, need: ['visible'] }); el.focus(); this._page._rt.press(el, key); }
    async check(o = {}) { const el = await this._one('check', { ...o, need: ['visible', 'stable', 'enabled', 'events'] }); if (!checkedState(el)) await this._page._rt.doClick(el, o); if (!checkedState(el)) throw new Error('Clicking the checkbox did not change its state'); }
    async uncheck(o = {}) { const el = await this._one('uncheck', { ...o, need: ['visible', 'stable', 'enabled', 'events'] }); if (checkedState(el)) await this._page._rt.doClick(el, o); }
    async setChecked(v, o = {}) { return v ? this.check(o) : this.uncheck(o); }
    async selectOption(v, o = {}) {
      const el = await this._one('selectOption', { ...o, arg: v, need: ['visible', 'enabled'] });
      const want = [].concat(v).map(x => (typeof x === 'object' && x ? x.label || x.value : x));
      const opts = [...el.options];
      const picked = want.map(w => opts.find(op => op.value === w) || opts.find(op => norms(op.label || op.textContent) === w));
      if (picked.some(p => !p)) throw new Error(`No option matches ${JSON.stringify(want)}`);
      opts.forEach(op => { op.selected = picked.includes(op); });
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
      return picked.map(p => p.value);
    }
    async hover(o = {}) { const el = await this._one('hover', { ...o, need: ['visible', 'stable', 'events'] }); el.dispatchEvent(new MouseEvent('mouseover', { bubbles: true })); el.dispatchEvent(new MouseEvent('mouseenter')); el.classList.add('pg-hover'); }
    async focus() { const el = await this._one('focus', {}); el.focus(); }
    async blur() { const el = await this._one('blur', {}); el.blur(); }
    async scrollIntoViewIfNeeded() { const el = await this._one('scrollIntoViewIfNeeded', { need: ['visible'] }); el.scrollIntoView({ block: 'center' }); }
    async setInputFiles(files) {
      const el = await this._one('setInputFiles', {});
      const win = el.ownerDocument.defaultView;
      const dt = new win.DataTransfer();
      [].concat(files).forEach(f => { const name = typeof f === 'string' ? f.split(/[\\/]/).pop() : f.name; dt.items.add(new win.File([typeof f === 'object' && f.buffer ? String(f.buffer) : 'file'], name)); });
      el.files = dt.files;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    }
    async dragTo(target) {
      const a = await this._one('dragTo', { need: ['visible', 'stable'] });
      const b = await target._one('drop target', { need: ['visible'] });
      const win = a.ownerDocument.defaultView;
      const dt = new win.DataTransfer();
      a.dispatchEvent(new win.DragEvent('dragstart', { bubbles: true, dataTransfer: dt }));
      b.dispatchEvent(new win.DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: dt }));
      b.dispatchEvent(new win.DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt }));
      a.dispatchEvent(new win.DragEvent('dragend', { bubbles: true, dataTransfer: dt }));
    }
    async waitFor(o = {}) {
      const state = o.state || 'visible';
      return this._page._rt.poll(`waitFor(${state})`, () => {
        const els = this._resolve();
        if (state === 'attached') return els.length > 0;
        if (state === 'detached') return els.length === 0;
        if (state === 'hidden') return els.length === 0 || els.every(hidden);
        return els.some(e => !hidden(e));
      }, o.timeout, this);
    }
    async highlight() { const el = (this._resolve())[0]; if (el) this._page._rt.flash(el, 1200); }
    async count() { return this._resolve().length; }
    async textContent() { const el = await this._one('textContent', { need: [] }); return el.textContent; }
    async innerText() { const el = await this._one('innerText', { need: [] }); return el.innerText; }
    async innerHTML() { const el = await this._one('innerHTML', { need: [] }); return el.innerHTML; }
    async inputValue() { const el = await this._one('inputValue', { need: [] }); return el.value; }
    async getAttribute(n) { const el = await this._one('getAttribute', { need: [] }); return el.getAttribute(n); }
    async isVisible() { const els = this._resolve(); this._page._rt.strict(this, els, true); return !!els[0] && !hidden(els[0]); }
    async isHidden() { return !(await this.isVisible()); }
    async isEnabled() { const el = await this._one('isEnabled', { need: [] }); return !el.disabled; }
    async isDisabled() { return !(await this.isEnabled()); }
    async isChecked() { const el = await this._one('isChecked', { need: [] }); return !!checkedState(el); }
    async isEditable() { const el = await this._one('isEditable', { need: [] }); return !el.disabled && !el.readOnly; }
    async allTextContents() { return this._resolve().map(e => e.textContent); }
    async allInnerTexts() { return this._resolve().map(e => e.innerText); }
    async all() { return this._resolve().map((_, i) => this.nth(i)); }
    async boundingBox() { const el = (this._resolve())[0]; if (!el) return null; const r = el.getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; }
    async screenshot() { this._page._rt.log('dim', '📸 (the playground does not save files, a real run would save the picture)'); }
    async evaluate(fn) { const el = await this._one('evaluate', { need: [] }); return typeof fn === 'function' ? fn(el) : null; }
  }
  // Python reads first and last as properties.
  Object.defineProperty(Locator.prototype, 'first', { get() { const f = () => this._with({ k: 'pick', desc: 'first', fn: s => s.slice(0, 1) }); return Object.assign(f(), { __call: f }); } });
  Object.defineProperty(Locator.prototype, 'last', { get() { const f = () => this._with({ k: 'pick', desc: 'last', fn: s => s.slice(-1) }); return Object.assign(f(), { __call: f }); } });

  class FrameLocator extends Locator {
    constructor(page, steps) { super(page, steps); }
    owner() { return new Locator(this._page, this._steps.slice(0, -1).concat([{ desc: 'owner()', find: r => css(r, 'iframe') }])); }
    locator(sel) { return new Locator(this._page, this._steps).locator(sel); }
  }

  const sleep = ms => new Promise(r => setTimeout(r, ms));

  /* ================= 6. runtime ================= */
  class Expectation {
    constructor(rt, target, neg = false, soft = false, msg = '') { this.rt = rt; this.t = target; this.neg = neg; this.soft = soft; this.msg = msg; }
    get not() { return new Expectation(this.rt, this.t, !this.neg, this.soft, this.msg); }
    _isLoc() { return this.t instanceof Locator; }
    async _poll(name, test, expected, o = {}) {
      const rt = this.rt;
      rt.used.push(name);
      const loc = this._isLoc() ? this.t : null;
      const what = loc ? `expect(${loc})${this.neg ? '.not' : ''}.${name}` : `expect(page)${this.neg ? '.not' : ''}.${name}`;
      const timeout = o.timeout !== undefined ? o.timeout : rt.expectTimeout;
      const start = Date.now();
      let last = { ok: false, actual: undefined };
      let waited = false;
      while (true) {
        rt.checkStop();
        let els = null;
        try {
          if (loc) { els = loc._resolve(); if (!['toHaveCount', 'toBeHidden', 'toBeAttached', 'toHaveText', 'toContainText', 'toHaveValues'].includes(name) || (name !== 'toHaveCount' && !Array.isArray(expected))) { if (els.length > 1 && name !== 'toBeHidden') throw rt.strictError(loc, els); } }
          last = await test(els);
        } catch (e) {
          if (/strict mode/.test(e.message)) throw e;
          last = { ok: false, actual: undefined, err: e.message };
        }
        if (last.ok !== this.neg) {
          if (loc && els && els[0]) rt.flash(els[0], 500, 'ok');
          rt.log('ok', `✓ ${what}(${expected === undefined ? '' : fmt(expected)})${waited ? ` passed after ${Date.now() - start} ms` : ''}`);
          return;
        }
        if (Date.now() - start >= timeout) break;
        if (!waited) { rt.log('wait', `⏳ ${what} is not true yet, retrying until it passes (timeout ${timeout} ms)`); waited = true; }
        await sleep(100);
      }
      const lines = [`${this.msg ? this.msg + '\n\n' : ''}expect(${loc ? 'locator' : 'page'})${this.neg ? '.not' : ''}.${name}(expected) failed`, '',
        ...(loc ? [`Locator:  ${loc}`] : []), `Expected${this.neg ? ' not' : ''}: ${fmt(expected)}`, `Received: ${last.actual === undefined ? '<element(s) not found>' : fmt(last.actual)}`, `Timeout:  ${timeout}ms`];
      const err = new Error(lines.join('\n'));
      if (this.soft) { rt.softErrors.push(err); rt.log('bad', '✗ (soft) ' + err.message.split('\n')[0] + ', the test goes on'); return; }
      throw err;
    }
    async toBeVisible(o) { return this._poll('toBeVisible', els => ({ ok: els.length > 0 && !hidden(els[0]), actual: els.length ? (hidden(els[0]) ? 'hidden' : 'visible') : undefined }), undefined, o); }
    async toBeHidden(o) { return this._poll('toBeHidden', els => ({ ok: els.length === 0 || els.every(hidden), actual: els.length ? (els.every(hidden) ? 'hidden' : 'visible') : 'hidden' }), undefined, o); }
    async toBeAttached(o) { return this._poll('toBeAttached', els => ({ ok: els.length > 0, actual: els.length ? 'attached' : 'detached' }), undefined, o); }
    async toBeEnabled(o) { return this._poll('toBeEnabled', els => ({ ok: !!els[0] && !els[0].disabled, actual: els[0] ? (els[0].disabled ? 'disabled' : 'enabled') : undefined }), undefined, o); }
    async toBeDisabled(o) { return this._poll('toBeDisabled', els => ({ ok: !!els[0] && !!els[0].disabled, actual: els[0] ? (els[0].disabled ? 'disabled' : 'enabled') : undefined }), undefined, o); }
    async toBeEditable(o) { return this._poll('toBeEditable', els => ({ ok: !!els[0] && !els[0].disabled && !els[0].readOnly, actual: els[0] ? 'checked' : undefined }), undefined, o); }
    async toBeChecked(o = {}) { const want = o.checked === undefined ? true : o.checked; return this._poll('toBeChecked', els => ({ ok: !!els[0] && !!checkedState(els[0]) === want, actual: els[0] ? (checkedState(els[0]) ? 'checked' : 'unchecked') : undefined }), undefined, o); }
    async toBeFocused(o) { return this._poll('toBeFocused', els => ({ ok: !!els[0] && els[0].ownerDocument.activeElement === els[0], actual: els[0] ? 'focused?' : undefined }), undefined, o); }
    async toBeEmpty(o) { return this._poll('toBeEmpty', els => ({ ok: !!els[0] && (('value' in els[0] && /INPUT|TEXTAREA/.test(els[0].tagName)) ? !els[0].value : !norms(textOf(els[0]))), actual: els[0] ? norms(els[0].value || textOf(els[0])) : undefined }), undefined, o); }
    async toBeInViewport(o) { return this._poll('toBeInViewport', els => { const e = els[0]; if (!e) return { ok: false }; const r = e.getBoundingClientRect(), w = e.ownerDocument.defaultView; return { ok: r.bottom > 0 && r.top < w.innerHeight, actual: 'outside' }; }, undefined, o); }
    async toHaveText(want, o = {}) {
      if (Array.isArray(want)) return this._poll('toHaveText', els => { const got = els.map(e => norms(o.useInnerText ? e.innerText : textOf(e))); return { ok: got.length === want.length && got.every((g, k) => (want[k] instanceof RegExp ? want[k].test(g) : g === norms(want[k]))), actual: got }; }, want, o);
      return this._poll('toHaveText', els => { const g = els[0] ? norms(o.useInnerText ? els[0].innerText : textOf(els[0])) : undefined; return { ok: g !== undefined && (want instanceof RegExp ? want.test(g) : (o.ignoreCase ? g.toLowerCase() === norms(want).toLowerCase() : g === norms(want))), actual: g }; }, want, o);
    }
    async toContainText(want, o = {}) {
      if (Array.isArray(want)) return this._poll('toContainText', els => { const got = els.map(e => norms(textOf(e))); let k = 0; for (const g of got) if (k < want.length && (want[k] instanceof RegExp ? want[k].test(g) : g.includes(norms(want[k])))) k++; return { ok: k === want.length, actual: got }; }, want, o);
      return this._poll('toContainText', els => { const g = els[0] ? norms(textOf(els[0])) : undefined; return { ok: g !== undefined && (want instanceof RegExp ? want.test(g) : (o.ignoreCase ? g.toLowerCase().includes(norms(want).toLowerCase()) : g.includes(norms(want)))), actual: g }; }, want, o);
    }
    async toHaveValue(want, o) { return this._poll('toHaveValue', els => { const g = els[0] ? els[0].value : undefined; return { ok: g !== undefined && (want instanceof RegExp ? want.test(g) : g === String(want)), actual: g }; }, want, o); }
    async toHaveValues(want, o) { return this._poll('toHaveValues', els => { const g = els[0] ? [...els[0].selectedOptions].map(x => x.value) : undefined; return { ok: !!g && g.length === want.length && g.every((x, k) => x === want[k]), actual: g }; }, want, o); }
    async toHaveCount(n, o) { return this._poll('toHaveCount', els => ({ ok: els.length === n, actual: els.length }), n, o); }
    async toHaveAttribute(name, want, o) { return this._poll('toHaveAttribute', els => { const g = els[0] ? els[0].getAttribute(name) : undefined; return { ok: g !== null && g !== undefined && (want === undefined || (want instanceof RegExp ? want.test(g) : g === String(want))), actual: g }; }, want === undefined ? name : want, o); }
    async toHaveClass(want, o) { return this._poll('toHaveClass', els => { const g = els[0] ? els[0].className : undefined; return { ok: g !== undefined && (want instanceof RegExp ? want.test(g) : g === want), actual: g }; }, want, o); }
    async toContainClass(want, o) { return this._poll('toContainClass', els => { const g = els[0] ? els[0].className : undefined; return { ok: g !== undefined && String(want).split(/\s+/).every(c => els[0].classList.contains(c)), actual: g }; }, want, o); }
    async toHaveId(want, o) { return this._poll('toHaveId', els => ({ ok: !!els[0] && els[0].id === want, actual: els[0] && els[0].id }), want, o); }
    async toHaveCSS(prop, want, o) { return this._poll('toHaveCSS', els => { const g = els[0] ? els[0].ownerDocument.defaultView.getComputedStyle(els[0])[camel(prop.replace(/-/g, '_'))] : undefined; return { ok: g !== undefined && (want instanceof RegExp ? want.test(g) : g === want), actual: g }; }, want, o); }
    async toHaveAccessibleName(want, o) { return this._poll('toHaveAccessibleName', els => { const g = els[0] ? accName(els[0]) : undefined; return { ok: g !== undefined && (want instanceof RegExp ? want.test(g) : g === norms(want)), actual: g }; }, want, o); }
    async toHaveRole(want, o) { return this._poll('toHaveRole', els => ({ ok: !!els[0] && IMPLICIT(els[0]) === want, actual: els[0] ? IMPLICIT(els[0]) : undefined }), want, o); }
    async toHaveURL(want, o) { return this._poll('toHaveURL', () => { const g = this.rt.page.url(); return { ok: want instanceof RegExp ? want.test(g) : g === this.rt.abs(want), actual: g }; }, want, o); }
    async toHaveTitle(want, o) { return this._poll('toHaveTitle', () => { const g = this.rt.page._title(); return { ok: want instanceof RegExp ? want.test(g) : g === want, actual: g }; }, want, o); }
    async toBeOK() { const s = this.t && this.t.status ? this.t.status() : 0; this.rt.used.push('toBeOK'); if ((s >= 200 && s < 300) === this.neg) throw new Error(`expect(response).toBeOK() failed, the status was ${s}`); this.rt.log('ok', `✓ expect(response).toBeOK(), status ${s}`); }
    // plain values: no retrying, just like the generic expect in Playwright Test
    _plain(name, ok, want) { this.rt.used.push(name); if (ok === this.neg) throw new Error(`expect(received)${this.neg ? '.not' : ''}.${name}(expected)\n\nExpected: ${fmt(want)}\nReceived: ${fmt(this.t)}`); this.rt.log('ok', `✓ expect(${fmt(this.t)})${this.neg ? '.not' : ''}.${name}(${want === undefined ? '' : fmt(want)})`); }
    toBe(v) { this._plain('toBe', Object.is(this.t, v), v); }
    toEqual(v) { this._plain('toEqual', JSON.stringify(this.t) === JSON.stringify(v), v); }
    toContain(v) { this._plain('toContain', this.t != null && this.t.includes(v), v); }
    toBeTruthy() { this._plain('toBeTruthy', !!this.t); }
    toBeFalsy() { this._plain('toBeFalsy', !this.t); }
    toBeGreaterThan(v) { this._plain('toBeGreaterThan', this.t > v, v); }
    toBeLessThan(v) { this._plain('toBeLessThan', this.t < v, v); }
    toMatch(v) { this._plain('toMatch', (v instanceof RegExp ? v : new RegExp(v)).test(this.t), v); }
    toHaveLength(v) { this._plain('toHaveLength', this.t != null && this.t.length === v, v); }
  }
  function fmt(v) {
    if (v instanceof RegExp) return String(v);
    if (Array.isArray(v)) return '[' + v.map(fmt).join(', ') + ']';
    if (typeof v === 'string') return JSON.stringify(v);
    if (v instanceof Locator) return v.toString();
    if (v && typeof v === 'object') return JSON.stringify(v);
    return String(v);
  }

  // A small model of a Playwright page that drives the shop inside the playground frame.
  function makeRuntime(ui) {
    const rt = {
      frame: ui.frame, used: [], softErrors: [], printed: [], dialogs: [], handlers: { dialog: [], console: [], request: [], response: [], pageerror: [] },
      routes: [], expectTimeout: 5000, actionTimeout: 5000, slow: 0, stopped: false, history: [], hpos: -1, net: [],
      log: ui.log, checkStop() { if (rt.stopped) throw new Error('Stopped'); },
    };
    const BASE = 'http://localhost:4173';
    rt.abs = u => (/^https?:/.test(u) ? u : BASE + (u.startsWith('/') ? u : '/' + u));
    rt.file = u => {
      const url = new URL(rt.abs(u));
      let p = url.pathname.replace(/^\/+/, '') || 'index';
      p = p.replace(/\.html$/, '');
      return ui.shopBase + p + '.html' + url.search;
    };
    rt.flash = (el, ms = 600, kind = 'hl') => {
      try {
        const doc = el.ownerDocument;
        if (!doc.getElementById('pg-style')) { const s = doc.createElement('style'); s.id = 'pg-style'; s.textContent = '.pg-hl{outline:3px solid #f59e0b!important;outline-offset:2px;background:rgba(245,158,11,.18)!important}.pg-ok{outline:3px solid #16a34a!important;outline-offset:2px}'; doc.head.appendChild(s); }
        el.classList.add(kind === 'ok' ? 'pg-ok' : 'pg-hl');
        el.scrollIntoView({ block: 'nearest' });
        setTimeout(() => el.classList.remove('pg-hl', 'pg-ok'), ms);
      } catch (e) { /* the element went away */ }
    };
    rt.strictError = (loc, els) => new Error(`Error: strict mode violation: ${loc} resolved to ${els.length} elements:\n` + els.slice(0, 5).map((e, k) => `    ${k + 1}) <${e.tagName.toLowerCase()}${e.id ? ' id="' + e.id + '"' : ''}>${norms(textOf(e)).slice(0, 40)}</${e.tagName.toLowerCase()}>`).join('\n') + '\n\nUse a more exact locator, or .first(), .nth() or .filter() to pick one.');
    rt.strict = (loc, els, quiet) => { if (els.length > 1) { if (quiet) throw rt.strictError(loc, els); throw rt.strictError(loc, els); } };
    rt.poll = async (what, test, timeout, loc) => {
      const t = timeout !== undefined ? timeout : rt.actionTimeout, start = Date.now();
      let waited = false;
      while (true) {
        rt.checkStop();
        if (test()) { rt.log('ok', `✓ ${loc ? loc + '.' : ''}${what}${waited ? ` after ${Date.now() - start} ms` : ''}`); return; }
        if (Date.now() - start > t) throw new Error(`TimeoutError: ${loc ? loc + '.' : ''}${what}: Timeout ${t}ms exceeded.`);
        if (!waited) { rt.log('wait', `⏳ waiting for ${loc || 'the page'} (${what})`); waited = true; }
        await sleep(100);
      }
    };
    // Auto-waiting: find exactly one element, then wait until it is ready for the action.
    rt.waitFor = async (loc, action, o) => {
      const t = o.timeout !== undefined ? o.timeout : rt.actionTimeout, start = Date.now();
      const need = o.force ? ['visible'].filter(x => (o.need || []).includes(x) && false) : (o.need || []);
      let reason = '', said = '';
      while (true) {
        rt.checkStop();
        const els = loc._resolve();
        if (els.length > 1) throw rt.strictError(loc, els);
        const el = els[0];
        if (!el) reason = 'waiting for the element to appear in the page';
        else if (need.includes('visible') && hidden(el)) reason = 'element is not visible';
        else if (need.includes('stable') && el.getAnimations && el.getAnimations().some(a => a.playState === 'running')) reason = 'element is not stable, it is still moving';
        else if (need.includes('enabled') && (el.disabled || el.getAttribute('aria-disabled') === 'true')) reason = 'element is not enabled';
        else if (need.includes('editable') && (el.readOnly || !/^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName) && !el.isContentEditable)) reason = 'element is not editable';
        else if (need.includes('events') && !receives(el)) reason = 'another element would receive the click';
        else {
          if (said) rt.log('ok', `  ready after ${Date.now() - start} ms`);
          rt.flash(el, Math.max(500, rt.slow + 300));
          rt.log('', `→ ${loc}.${action}(${o.arg !== undefined ? fmt(o.arg) : ''})`);
          if (rt.slow) await sleep(rt.slow);
          return el;
        }
        if (reason !== said) { rt.log('wait', `⏳ ${loc}.${action}: ${reason}, retrying`); said = reason; }
        if (Date.now() - start > t) throw new Error(`TimeoutError: ${loc}.${action}: Timeout ${t}ms exceeded.\nCall log:\n  - waiting for ${loc}\n  - ${reason}`);
        await sleep(100);
      }
    };
    function receives(el) {
      const r = el.getBoundingClientRect();
      const doc = el.ownerDocument;
      if (r.bottom < 0 || r.top > doc.defaultView.innerHeight) { el.scrollIntoView({ block: 'center' }); }
      const r2 = el.getBoundingClientRect();
      const x = r2.left + r2.width / 2, y = r2.top + r2.height / 2;
      let hit = doc.elementFromPoint(x, y);
      if (!hit) return true;
      while (hit && hit.shadowRoot) { const inner = hit.shadowRoot.elementFromPoint(x, y); if (!inner || inner === hit) break; hit = inner; }
      return hit === el || el.contains(hit) || (hit.getRootNode && hit.getRootNode().host && el.contains(hit.getRootNode().host)) || (el.labels && [...el.labels].some(l => l.contains(hit)));
    }
    rt.doClick = async (el) => {
      const win = el.ownerDocument.defaultView;
      ['pointerdown', 'mousedown'].forEach(t => el.dispatchEvent(new win.MouseEvent(t, { bubbles: true, cancelable: true })));
      el.focus && el.focus();
      ['pointerup', 'mouseup'].forEach(t => el.dispatchEvent(new win.MouseEvent(t, { bubbles: true, cancelable: true })));
      el.click();
      await sleep(30);
    };
    rt.doFill = (el, v) => {
      el.focus();
      if (el.isContentEditable) el.textContent = v; else el.value = v;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    };
    rt.key = (el, k) => {
      const win = el.ownerDocument.defaultView;
      el.dispatchEvent(new win.KeyboardEvent('keydown', { key: k, bubbles: true, cancelable: true }));
      el.dispatchEvent(new win.KeyboardEvent('keyup', { key: k, bubbles: true }));
    };
    rt.press = (el, combo) => {
      const win = el.ownerDocument.defaultView;
      const parts = combo.split('+'), key = parts.pop();
      const mods = { ctrlKey: parts.includes('Control') || parts.includes('ControlOrMeta'), shiftKey: parts.includes('Shift'), altKey: parts.includes('Alt'), metaKey: parts.includes('Meta') };
      const ev = new win.KeyboardEvent('keydown', { key: key.length === 1 && !mods.shiftKey ? key.toLowerCase() : key, bubbles: true, cancelable: true, ...mods });
      const ok = el.dispatchEvent(ev);
      el.dispatchEvent(new win.KeyboardEvent('keyup', { key, bubbles: true, ...mods }));
      if (ok && key === 'Enter' && el.form && /^(INPUT)$/.test(el.tagName)) el.form.requestSubmit();
      if (ok && key === 'Backspace' && 'value' in el) { el.value = el.value.slice(0, -1); el.dispatchEvent(new Event('input', { bubbles: true })); }
      if (ok && key === 'Tab') { const f = [...el.ownerDocument.querySelectorAll('input,button,select,textarea,a[href]')].filter(x => !x.disabled); const i = f.indexOf(el); if (f[i + 1]) f[i + 1].focus(); }
    };
    rt.load = async (url) => {
      const target = rt.file(url);
      const done = new Promise(res => { ui.frame.onload = () => res(); });
      ui.setUrl(rt.abs(url).replace(/\.html(?=$|\?)/, ''));
      ui.frame.src = target;
      await Promise.race([done, sleep(8000)]);
      rt.attach();
    };
    // Watch navigations the page makes by itself (links, location.href).
    rt.attach = () => {
      try {
        const w = ui.frame.contentWindow;
        const path = w.location.pathname.split('/').pop().replace(/\.html$/, '');
        ui.setUrl(BASE + '/' + (path === 'index' ? '' : path) + w.location.search);
        w.document.querySelectorAll('a[target=_blank]').forEach(a => a.addEventListener('click', e => { e.preventDefault(); rt.log('dim', `🗂️ the link opens a new tab: ${a.getAttribute('href')} (use page.waitForEvent('popup') in a real test)`); }));
      } catch (e) { /* cross origin */ }
    };
    ui.frame.addEventListener('load', () => rt.attach());
    const doc = () => { try { return ui.frame.contentDocument; } catch (e) { return null; } };
    const page = {
      _rt: rt, _doc: doc,
      _title: () => (doc() ? doc().title : ''),
      async goto(url, o = {}) { rt.log('', `→ page.goto(${fmt(url)})`); await rt.load(url); rt.history = rt.history.slice(0, rt.hpos + 1); rt.history.push(url); rt.hpos++; rt.log('ok', `✓ loaded ${rt.abs(url)}`); if (rt.slow) await sleep(rt.slow); return { status: () => 200, ok: () => true }; },
      async reload() { rt.log('', '→ page.reload()'); ui.frame.contentWindow.location.reload(); await new Promise(r => { ui.frame.onload = r; }); rt.attach(); },
      async goBack() { rt.log('', '→ page.goBack()'); ui.frame.contentWindow.history.back(); await sleep(400); rt.attach(); },
      async goForward() { ui.frame.contentWindow.history.forward(); await sleep(400); rt.attach(); },
      url: () => ui.getUrl(),
      async title() { return page._title(); },
      async content() { return doc().documentElement.outerHTML; },
      async waitForTimeout(ms) { rt.log('wait', `⏳ page.waitForTimeout(${ms}), a fixed wait. Real tests avoid this, it makes them slow and flaky.`); await sleep(Math.min(ms, 5000)); },
      async waitForLoadState() { await sleep(50); rt.log('ok', '✓ page.waitForLoadState()'); },
      async waitForURL(want, o = {}) { const ok = () => { const u = page.url(); return want instanceof RegExp ? want.test(u) : (String(want).includes('*') ? new RegExp('^' + String(want).replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*\*/g, '.*').replace(/\*/g, '[^/]*') + '$').test(u) : u === rt.abs(want)); }; return rt.poll(`waitForURL(${fmt(want)})`, ok, o.timeout); },
      async waitForSelector(sel, o) { return page.locator(sel).waitFor(o); },
      async setViewportSize(s) { ui.frame.style.width = Math.min(s.width, ui.frame.parentElement.clientWidth) + 'px'; rt.log('ok', `✓ viewport ${s.width}×${s.height}`); },
      async pause() { rt.log('wait', '⏸ page.pause() opens the Playwright Inspector in a real run. Here, press Step to go on.'); ui.pauseHere(); },
      async screenshot() { rt.log('dim', '📸 page.screenshot() saves a picture in a real run.'); },
      on(evt, fn) { (rt.handlers[evt] = rt.handlers[evt] || []).push(fn); rt.log('dim', `👂 listening for "${evt}" events`); },
      once(evt, fn) { page.on(evt, fn); },
      onDialog(fn) { page.on('dialog', fn); },
      onConsoleMessage(fn) { page.on('console', fn); },
      onRequest(fn) { page.on('request', fn); },
      onResponse(fn) { page.on('response', fn); },
      async route(url, handler) { rt.routes.push({ url, handler }); rt.log('dim', `🛰️ page.route(${fmt(url)}) is ready to catch requests`); },
      async unroute(url) { rt.routes = rt.routes.filter(r => String(r.url) !== String(url)); },
      async waitForResponse(match, o = {}) {
        const start = rt.net.length;
        let found = null;
        await rt.poll(`waitForResponse(${fmt(match)})`, () => { found = rt.net.slice(start).find(n => n.status && urlMatch(match, n.url)); return !!found; }, o.timeout);
        return { status: () => found.status, url: () => BASE + found.url, ok: () => found.status < 400, json: async () => found.body };
      },
      async evaluate(fn) { rt.log('dim', '🧮 page.evaluate runs code inside the page'); return typeof fn === 'function' ? fn() : null; },
      context() { return { clearCookies: async () => { ui.host.state.storage = {}; rt.log('ok', '✓ cookies and storage cleared'); }, storageState: async () => ({ cookies: [], origins: [{ origin: BASE, localStorage: Object.entries(ui.host.state.storage || {}).map(([name, value]) => ({ name, value })) }] }) }; },
      keyboard: {
        async press(k) { const el = doc().activeElement || doc().body; rt.log('', `→ page.keyboard.press(${fmt(k)})`); rt.press(el, k); },
        async type(t) { const el = doc().activeElement; for (const ch of t) { rt.key(el, ch); if ('value' in el) el.value += ch; } el.dispatchEvent(new Event('input', { bubbles: true })); },
        async insertText(t) { const el = doc().activeElement; if ('value' in el) el.value += t; el.dispatchEvent(new Event('input', { bubbles: true })); },
      },
      mouse: { async click(x, y) { const el = doc().elementFromPoint(x, y); if (el) await rt.doClick(el); }, async wheel(dx, dy) { doc().defaultView.scrollBy(dx, dy); } },
    };
    const root = new Locator(page, []);
    ['getByRole', 'getByText', 'getByLabel', 'getByPlaceholder', 'getByAltText', 'getByTitle', 'getByTestId', 'locator', 'frameLocator'].forEach(m => { page[m] = (...a) => root[m](...a); });
    rt.page = page;
    const urlMatch = (m, u) => (m instanceof RegExp ? m.test(BASE + u) : typeof m === 'function' ? m({ url: () => BASE + u }) : (String(m).includes('*') ? new RegExp(String(m).replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*\*/g, '.*').replace(/\*/g, '[^/]*')).test(BASE + u) : (BASE + u).includes(m) || u.includes(m)));
    // the shop's fake server calls these
    ui.host.route = async (path, method, body) => {
      for (const r of rt.routes) {
        if (!urlMatch(r.url, path)) continue;
        let result = null;
        const route = {
          request: () => ({ url: () => BASE + path, method: () => method, postDataJSON: () => body, postData: () => JSON.stringify(body) }),
          async fulfill(o = {}) { const b = o.json !== undefined ? JSON.stringify(o.json) : (o.body || ''); result = new Response(b, { status: o.status || 200, headers: { 'Content-Type': o.contentType || 'application/json' } }); rt.log('ok', `🛰️ route.fulfill: ${method} ${path} answered with status ${o.status || 200}`); },
          async abort() { result = 'abort'; rt.log('ok', `🛰️ route.abort: ${method} ${path} failed on purpose`); },
          async continue() { result = null; rt.log('dim', `🛰️ route.continue: ${method} ${path} goes to the server`); },
          async fallback() { result = null; },
          async fetch() { return { json: async () => null }; },
        };
        await r.handler(route);
        if (result === 'abort') return Promise.reject(new TypeError('Failed to fetch'));
        if (result) { rt.net.push({ url: path, method, status: result.status, body: JSON.parse(await result.clone().text() || 'null') }); return result; }
      }
      return null;
    };
    ui.host.net = (method, path, status) => {
      if (status === undefined) { rt.handlers.request.forEach(f => f({ url: () => BASE + path, method: () => method })); return; }
      rt.net.push({ url: path, method, status });
      rt.handlers.response.forEach(f => f({ url: () => BASE + path, status: () => status }));
    };
    ui.host.dialog = (type, message, def) => {
      const d = { _done: null, type: () => type, message: () => message, defaultValue: () => def,
        accept(v) { d._done = { ok: true, v: v === undefined ? def : v }; }, dismiss() { d._done = { ok: false }; } };
      if (!rt.handlers.dialog.length) { rt.log('dim', `💬 ${type}("${message}") was dismissed, because no page.on('dialog') handler is set. That is what Playwright does too.`); rt.dialogs.push({ type, message, accepted: false }); return type === 'prompt' ? null : false; }
      rt.handlers.dialog.forEach(f => f(d));
      const res = d._done || { ok: false };
      rt.dialogs.push({ type, message, accepted: res.ok });
      rt.log('ok', `💬 ${type}("${message}") was ${res.ok ? 'accepted' : 'dismissed'}`);
      if (type === 'prompt') return res.ok ? (res.v ?? '') : null;
      return res.ok;
    };
    ui.host.popup = u => rt.log('dim', `🪟 the page opened a popup window: ${u}`);
    ui.host.pageError = m => { rt.log('bad', `💥 page error: ${m}`); rt.handlers.pageerror.forEach(f => f({ message: m })); };
    ui.host.console = (type, text) => { rt.handlers.console.forEach(f => f({ type: () => type, text: () => text })); };
    return rt;
  }

  /* ================= 7. the interpreter: runs parsed statements against the runtime ================= */
  function makeInterp(rt, lang) {
    const env = { page: rt.page, Page: rt.page };
    const builtins = {
      expect: (t, msg) => new Expectation(rt, t, false, false, typeof msg === 'string' ? msg : ''),
      assertThat: t => new Expectation(rt, t),
      Expect: t => new Expectation(rt, t),
      console: { log: (...a) => print(a) }, Console: { WriteLine: (...a) => print(a), writeLine: (...a) => print(a) },
      System: { out: { println: (...a) => print(a) } },
      print: (...a) => print(a),
      re: { compile: (s, f) => new RegExp(s, f ? 'i' : ''), IGNORECASE: 2, I: 2 },
      Pattern: { compile: (s, f) => new RegExp(s, f ? 'i' : ''), CASE_INSENSITIVE: 2 },
      RegexOptions: { IgnoreCase: 2 },
      AriaRole: new Proxy({}, { get: (_, k) => String(k).toLowerCase() }),
      assertEquals: (a, b) => new Expectation(rt, b).toEqual(a), assertTrue: v => new Expectation(rt, v).toBeTruthy(), assertFalse: v => new Expectation(rt, v).toBeFalsy(),
      assertNotEquals: (a, b) => new Expectation(rt, b).not.toEqual(a),
      Assert: { That: () => {}, AreEqual: (a, b) => new Expectation(rt, b).toEqual(a), IsTrue: v => new Expectation(rt, v).toBeTruthy() },
      String: { valueOf: v => String(v) }, Integer: { parseInt: v => parseInt(v, 10) }, int: v => parseInt(v, 10), str: v => String(v), len: v => v.length,
      Number: v => Number(v), JSON: { stringify: v => JSON.stringify(v) }, Math,
      test: { info: () => ({ annotations: { push() {} } }) },
    };
    builtins.expect.soft = (t, msg) => new Expectation(rt, t, false, true, msg || '');
    builtins.expect.poll = fn => ({ async toBe(v) { await rt.poll(`expect.poll(...).toBe(${fmt(v)})`, () => false, 1000); } });
    function print(a) {
      const s = a.map(v => (typeof v === 'string' ? v : v instanceof Locator ? `Locator@${v}` : Array.isArray(v) ? (lang === 'py' ? "['" + v.join("', '") + "']" : lang === 'java' || lang === 'cs' ? '[' + v.join(', ') + ']' : '[ ' + v.map(x => `'${x}'`).join(', ') + ' ]') : typeof v === 'boolean' && lang === 'py' ? (v ? 'True' : 'False') : String(v))).join(' ');
      rt.printed.push(s);
      rt.log('out', s);
    }
    function camelKeys(o) {
      const r = {};
      for (const [k, v] of Object.entries(o)) r[lang === 'cs' ? k[0].toLowerCase() + k.slice(1) : lang === 'py' ? camel(k) : k] = v;
      return r;
    }
    async function ev(n) {
      switch (n.k) {
        case 'lit': return n.v;
        case 're': return new RegExp(n.v, n.f.replace(/[^gimsuy]/g, ''));
        case 'id':
          if (n.v in env) return env[n.v];
          if (n.v in builtins) return builtins[n.v];
          throw new Error(`"${n.v}" is not defined here. The playground knows page, expect and the variables you create.`);
        case 'arr': { const out = []; for (const x of n.v) out.push(await ev(x)); return out; }
        case 'obj': { const o = {}; for (const [k, v] of Object.entries(n.v)) o[k] = await ev(v); return camelKeys(o); }
        case 'not': return !(await ev(n.v));
        case 'bin': {
          const a = await ev(n.a), b = await ev(n.b);
          switch (n.op) { case '+': return a + b; case '==': case '===': return a === b || a == b; case '!=': case '!==': return a !== b; case '>': return a > b; case '<': return a < b; case '>=': return a >= b; case '<=': return a <= b; case '&&': return a && b; case '||': return a || b; case 'in': return b != null && b.includes(a); }
          return null;
        }
        case 'fn': return (...args) => { const saved = {}; n.ps.forEach((p, k) => { saved[p] = env[p]; env[p] = args[k]; }); const r = ev(n.body); r.finally(() => n.ps.forEach(p => { env[p] = saved[p]; })); return r; };
        case 'new': {
          const name = n.name.split('.').pop();
          if (/^(Regex)$/.test(name)) { const a = await ev(n.args.pos[0]); return new RegExp(a, n.args.pos[1] ? 'i' : ''); }
          if (/Options$/.test(name) || name === 'PageGetByRoleOptions') {
            const o = n.init ? await ev(n.init) : {};
            return Object.assign(new OptionsBuilder(), camelKeys(o));
          }
          throw new Error(`The playground cannot create a new ${n.name}`);
        }
        case 'get': {
          const o = await ev(n.o);
          return getProp(o, n.n, false);
        }
        case 'idx': { const o = await ev(n.o); return o[await ev(n.i)]; }
        case 'call': {
          let self = null, fn;
          if (n.f.k === 'get') {
            self = await ev(n.f.o);
            fn = getProp(self, n.f.n, true);
          } else fn = await ev(n.f);
          if (typeof fn !== 'function') throw new Error(`${n.f.n || n.f.v || 'This'} is not something you can call here`);
          const pos = [];
          for (const a of n.args.pos) pos.push(unwrap(await ev(a)));
          const named = Object.keys(n.args.named);
          if (named.length) { const o = {}; for (const k of named) o[k] = unwrap(await ev(n.args.named[k])); pos.push(camelKeys(o)); }
          const r = fn.apply(self, pos);
          return r && typeof r.then === 'function' ? await r : r;
        }
        default: throw new Error('The playground cannot run this kind of code');
      }
    }
    function unwrap(v) { return v instanceof OptionsBuilder ? { ...v } : v && v.__call ? v : v; }
    function getProp(o, name, calling) {
      if (o == null) throw new Error(`Cannot read "${name}" of ${o}`);
      if (o instanceof OptionsBuilder && /^set[A-Z]/.test(name)) return v => { o[name[3].toLowerCase() + name.slice(4)] = v; return o; };
      let k = norm(name, lang);
      if (o instanceof Expectation) {
        if (lang === 'java' && JAVA_ASSERT[k]) k = JAVA_ASSERT[k];
        if (lang === 'py' && /^not[A-Z]/.test(k) && k !== 'not') { const real = k.slice(3); const fn = o.not[real[0].toLowerCase() + real.slice(1)]; return fn ? fn.bind(o.not) : undefined; }
        if (k === 'not' && calling) return () => o.not;
      }
      if (lang === 'java' && /^(first|last)$/.test(k) && o instanceof Locator && calling) return () => (k === 'first' ? o.first.__call() : o.last.__call());
      if (/^(first|last)$/.test(k) && o instanceof Locator && calling && lang !== 'py' && lang !== 'cs') return () => o[k].__call();
      let v = o[k];
      if (v === undefined && typeof o === 'object' && (o instanceof Locator || o === rt.page)) throw new Error(`"${name}" is not a Playwright method the playground knows`);
      if (typeof v === 'function' && !calling && o === rt.page && /^(keyboard|mouse)$/.test(k)) return v;
      if (typeof v === 'function' && !v.__call) return v.bind(o);
      return v;
    }
    async function run(s) {
      if (s.k === 'let') { env[s.name] = await ev(s.e); return; }
      if (s.k === 'assert') {
        rt.used.push('assert');
        const e = s.e;
        if (e.k === 'bin' && (e.op === '==' || e.op === 'in')) {
          const a = await ev(e.a), b = await ev(e.b);
          const ok = e.op === '==' ? a === b : b != null && b.includes(a);
          if (!ok) throw new Error(`AssertionError: assert ${fmt(a)} ${e.op} ${fmt(b)}`);
          rt.log('ok', `✓ assert ${fmt(a)} ${e.op} ${fmt(b)}`);
          return;
        }
        const v = await ev(e);
        if (!v) throw new Error('AssertionError: the assert was false');
        rt.log('ok', '✓ assert passed');
        return;
      }
      if (s.k === 'sub') {
        const fn = await ev(s.fn);
        const t = s.target.k === 'get' ? s.target.n : '';
        if (/Dialog/.test(t)) rt.page.on('dialog', d => fn(null, d));
        else if (/Console/.test(t)) rt.page.on('console', m => fn(null, m));
        else throw new Error('The playground only listens to Page.Dialog and Page.Console with +=');
        return;
      }
      if (s.k === 'expr') {
        const v = await ev(s.e);
        if (v instanceof Expectation) throw new Error('This expect has no check. Add one, such as .toBeVisible()');
        return;
      }
    }
    return { run, env };
  }
  class OptionsBuilder {}

  /* ================= 8. the playground on the page ================= */
  const STORE = 'pw-lang';
  let ID = 0;
  function pickLang() { try { const v = localStorage.getItem(STORE); if (LANGS[v]) return v; } catch (e) { /* storage unavailable */ } return 'ts'; }

  function mount(el, lab) {
    const id = ++ID;
    const shopBase = el.dataset.shop || 'shop/';
    let lang = pickLang();
    if (!lab.code[lang]) lang = Object.keys(lab.code)[0];
    const saved = k => { try { return localStorage.getItem(`pg-${location.pathname}-${lab.id}-${k}`); } catch (e) { return null; } };
    el.innerHTML = `<div class="pgx" id="lab-${esc(lab.id)}">
      <div class="pgx-head"><h3>🧪 ${esc(lab.title)}</h3><div class="pgx-langs" role="tablist">${Object.keys(LANGS).map(l => `<button type="button" data-l="${l}"${l === lang ? ' class="on"' : ''}>${LANGS[l][0]} ${LANGS[l][1]}</button>`).join('')}</div></div>
      <div class="pgx-task">${lab.task}</div>
      <div class="pgx-body">
        <div class="pgx-ed"><pre class="pgx-gut" aria-hidden="true"></pre><textarea class="pgx-ta" spellcheck="false" autocapitalize="off" aria-label="Your test code"></textarea></div>
        <div class="pgx-side"><div class="pgx-url"><i></i><i></i><i></i><span>about:blank</span></div><iframe class="pgx-frame" title="Brainy Shop, driven by your test"></iframe></div>
      </div>
      <div class="pgx-bar">
        <button type="button" class="go" data-a="run">▶ Run all</button><button type="button" data-a="step">⏭ Run the next line</button><button type="button" data-a="stop" disabled>■ Stop</button><button type="button" data-a="reset">↺ Start again</button>
        <label>Slow motion <select data-a="slow"><option value="0">off</option><option value="400" selected>0.4 s</option><option value="1000">1 s</option></select></label>
        ${lab.hint ? '<button type="button" data-a="hint">💡 Hint</button>' : ''}<button type="button" data-a="sol">👀 Answer</button><button type="button" data-a="xl">🔁 Show my code in every language</button>
      </div>
      <pre class="pgx-log" aria-live="polite"></pre>
      <div class="pgx-goal">${lab.goal ? '🎯 ' + lab.goal : '🎯 Make the test pass.'}</div>
      <div class="pgx-hint" hidden>${lab.hint || ''}</div>
      <div class="pgx-sol" hidden></div>
    </div>`;
    const $ = s => el.querySelector(s);
    const ta = $('.pgx-ta'), gut = $('.pgx-gut'), logEl = $('.pgx-log'), frame = $('.pgx-frame'), goal = $('.pgx-goal');
    const host = { state: { sessions: {}, orders: {}, nextOrder: 1001, storage: {} } };
    // Each playground keeps its own shop data. The frame finds it through frame.__pghost while it loads.
    const ui = {
      frame, shopBase, host,
      log(kind, text) { logEl.insertAdjacentHTML('beforeend', `<span class="${kind || ''}">${esc(text)}</span>\n`); logEl.scrollTop = logEl.scrollHeight; },
      setUrl(u) { $('.pgx-url span').textContent = u; ui._url = u; },
      getUrl() { return ui._url || 'about:blank'; },
      pauseHere() { stepMode = true; },
    };
    let code = saved(lang) || lab.code[lang];
    let stmts = [], at = 0, rt = null, interp = null, running = false, stepMode = false;
    const setCode = c => { ta.value = c; drawGutter(); };
    function drawGutter(marks = {}) {
      const n = ta.value.split('\n').length;
      gut.innerHTML = Array.from({ length: n }, (_, k) => `<span class="${marks[k + 1] || ''}">${marks[k + 1] === 'on' ? '▶' : marks[k + 1] === 'ok' ? '✓' : marks[k + 1] === 'bad' ? '✗' : ''}${k + 1}</span>`).join('\n');
    }
    ta.addEventListener('input', () => { drawGutter(); try { localStorage.setItem(`pg-${location.pathname}-${lab.id}-${lang}`, ta.value); } catch (e) { /* storage unavailable */ } prepared = false; });
    ta.addEventListener('scroll', () => { gut.scrollTop = ta.scrollTop; });
    ta.addEventListener('keydown', e => {
      if (e.key === 'Tab') { e.preventDefault(); const s = ta.selectionStart; ta.setRangeText('  ', s, ta.selectionEnd, 'end'); ta.dispatchEvent(new Event('input')); }
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); runAll(); }
    });
    setCode(code);
    let prepared = false, marks = {};
    frame.__pghost = host;
    async function prepare() {
      logEl.innerHTML = '';
      marks = {};
      host.state = { sessions: {}, orders: {}, nextOrder: 1001, storage: {} };
      host.productDelay = lab.productDelay;
      rt = makeRuntime(ui);
      rt.slow = +$('[data-a=slow]').value;
      interp = makeInterp(rt, lang);
      stmts = parse(ta.value, lang);
      const bad = stmts.find(s => s.k === 'error');
      if (bad) { marks[bad.line] = 'bad'; drawGutter(marks); ui.log('bad', `✗ Line ${bad.line}: ${bad.msg}`); return false; }
      at = 0;
      prepared = true;
      ui.log('dim', `${LANGS[lang][0]} ${LANGS[lang][1]}: ${stmts.filter(s => s.k !== 'skip' && s.k !== 'setup').length} lines to run. A fresh browser context is ready, like a new test.`);
      frame.src = 'about:blank';
      ui.setUrl('about:blank');
      if (lab.start) { await rt.load(lab.start); ui.log('dim', `(the test starts on ${lab.start})`); }
      return true;
    }
    async function stepOnce() {
      while (at < stmts.length && (stmts[at].k === 'skip' || stmts[at].k === 'setup')) {
        if (stmts[at].k === 'setup') ui.log('dim', `⚙️ line ${stmts[at].line}: the playground already has a browser and a page open, so this line is skipped`);
        at++;
      }
      if (at >= stmts.length) return false;
      const s = stmts[at];
      marks[s.line] = 'on';
      drawGutter(marks);
      try {
        await interp.run(s);
        marks[s.line] = 'ok';
      } catch (e) {
        marks[s.line] = 'bad';
        drawGutter(marks);
        ui.log('bad', `✗ line ${s.line}: ${e.message}`);
        at = stmts.length;
        finish(false);
        throw e;
      }
      drawGutter(marks);
      at++;
      return at < stmts.length && stmts.slice(at).some(x => x.k !== 'skip' && x.k !== 'setup');
    }
    function setRunning(on) {
      running = on;
      $('[data-a=stop]').disabled = !on;
      $('[data-a=run]').disabled = on;
      $('[data-a=step]').disabled = on;
    }
    function finish(passed) {
      setRunning(false);
      prepared = false;
      if (passed && rt.softErrors.length) passed = false;
      const results = (lab.check || []).map(([expr, text]) => {
        let ok = false;
        try { ok = !!Function('ctx', 'return (' + expr + ')')(context()); } catch (e) { ok = false; }
        return { ok, text };
      });
      const all = passed && results.every(r => r.ok);
      if (passed) ui.log('ok', '\n✅ 1 passed');
      else ui.log('bad', '\n❌ 1 failed');
      goal.classList.toggle('pass', all);
      goal.innerHTML = (lab.goal ? '🎯 ' + lab.goal : '🎯 Make the test pass.') + (results.length ? '<br>' + results.map(r => `${r.ok ? '✅' : '⬜'} ${r.text}`).join('<br>') : '') + (all ? '<br>🎉 Lab complete!' : '');
      if (all && typeof FUN !== 'undefined' && FUN.confetti) { const b = goal.getBoundingClientRect(); FUN.confetti(b.left + 40, b.top, 60); }
    }
    function context() {
      const sess = Object.values(host.state.sessions)[0];
      const count = sess ? Object.values(sess.cart).reduce((a, b) => a + b, 0) : 0;
      return { used: rt.used, printed: rt.printed.join('\n'), url: ui.getUrl(), cartCount: count, loggedIn: !!sess, orders: Object.keys(host.state.orders).length,
        dialogs: rt.dialogs, routes: rt.routes.length, code: ta.value, lang, text: (() => { try { return frame.contentDocument.body.innerText; } catch (e) { return ''; } })() };
    }
    async function runAll() {
      if (running) return;
      if (!(await prepare())) return;
      setRunning(true);
      try {
        while (await stepOnce()) { if (!running) return; await new Promise(r => setTimeout(r, 30)); }
        finish(true);
      } catch (e) { setRunning(false); }
    }
    async function stepBtn() {
      if (running) return;
      if (!prepared && !(await prepare())) return;
      setRunning(true);
      try {
        const more = await stepOnce();
        setRunning(false);
        if (!more) finish(true);
      } catch (e) { setRunning(false); }
    }
    el.addEventListener('click', async e => {
      const b = e.target.closest('button');
      if (!b) return;
      if (b.dataset.l) {
        const old = lang;
        lang = b.dataset.l;
        el.querySelectorAll('.pgx-langs button').forEach(x => x.classList.toggle('on', x === b));
        const mine = saved(lang);
        let next = mine || lab.code[lang];
        if (!next) { try { next = translate(ta.value, old, lang, lab.name || lab.title); } catch (err) { next = translate(lab.code.ts || lab.code.js, lab.code.ts ? 'ts' : 'js', lang, lab.name || lab.title); } }
        setCode(next);
        prepared = false;
        renderSol();
        try { localStorage.setItem(STORE, lang); } catch (err) { /* storage unavailable */ }
        return;
      }
      const a = b.dataset.a;
      if (a === 'run') runAll();
      if (a === 'step') stepBtn();
      if (a === 'stop') { if (rt) rt.stopped = true; setRunning(false); prepared = false; ui.log('bad', '■ stopped'); }
      if (a === 'reset') { setCode(lab.code[lang] || translate(lab.code.ts || lab.code.js, lab.code.ts ? 'ts' : 'js', lang, lab.name || lab.title)); try { localStorage.removeItem(`pg-${location.pathname}-${lab.id}-${lang}`); } catch (err) { /* storage unavailable */ } logEl.innerHTML = ''; prepared = false; drawGutter(); goal.classList.remove('pass'); goal.innerHTML = lab.goal ? '🎯 ' + lab.goal : '🎯 Make the test pass.'; }
      if (a === 'hint') { const h = $('.pgx-hint'); h.hidden = !h.hidden; }
      if (a === 'sol') { const s = $('.pgx-sol'); s.hidden = !s.hidden; b.textContent = s.hidden ? '👀 Answer' : '🙈 Hide the answer'; }
      if (a === 'xl') {
        try {
          const all = Object.keys(LANGS).filter(l => l !== lang).map(l => `${LANGS[l][0]} ${LANGS[l][1]}\n${translate(ta.value, lang, l, lab.name || lab.title)}`).join('\n');
          logEl.innerHTML = '';
          ui.log('dim', 'Your test, written in the other languages:\n');
          ui.log('out', all);
        } catch (err) { ui.log('bad', 'Fix this first: ' + err.message); }
      }
    });
    function renderSol() {
      const src = (lab.answer && lab.answer[lang]) || (lab.answer ? translate(lab.answer.ts || lab.answer.js, lab.answer.ts ? 'ts' : 'js', lang, lab.name || lab.title) : '');
      $('.pgx-sol').innerHTML = src ? `<pre>${typeof LEARN !== 'undefined' ? LEARN.hl(src, lang === 'py' ? 'py' : lang === 'java' ? 'java' : lang === 'cs' ? 'java' : 'js') : esc(src)}</pre>${lab.why ? `<div class="pgx-hint">${lab.why}</div>` : ''}` : '';
    }
    renderSol();
    $('[data-a=slow]').addEventListener('change', e => { if (rt) rt.slow = +e.target.value; });
    // Show the starting page so the reader can look around before running anything.
    if (lab.start) { const r0 = makeRuntime(ui); r0.load(lab.start); }
  }

  function mountLabs() {
    if (typeof PAGE === 'undefined' || !PAGE.labs || !PAGE.labs.length) return;
    const host = document.getElementById('practice');
    if (!host) return;
    host.innerHTML = `<h2><span class="sec-em">🧪</span><span>Playground labs</span></h2>
      <p class="ex-lead">Write a real Playwright test in the language you pick, then press <b>Run all</b>, or <b>Run the next line</b> to go one line at a time and watch the shop react. The playground understands the Playwright API in Java, Python, JavaScript, TypeScript and C#. It is a teaching copy that runs in your browser, so a few things differ from a real browser run, and the page says so when it happens. Every answer was also run with real Playwright in Java, Python, JavaScript and TypeScript when this page was built.</p>
      ${PAGE.labs.map((l, k) => `<div class="pg-lab" data-i="${k}"></div>`).join('')}`;
    host.querySelectorAll('.pg-lab').forEach(d => mount(d, PAGE.labs[+d.dataset.i]));
  }

  return { lex, parse, canon, canonStatement, translate, genStatements, wrap, mount, mountLabs, engine: { BY, accName, IMPLICIT, hidden, css, Locator, textOf }, makeRuntime, makeInterp, LANGS };
})();
if (typeof module !== 'undefined') module.exports = PWPLAY;
