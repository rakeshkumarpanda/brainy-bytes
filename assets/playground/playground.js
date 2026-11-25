/* ===== Code Playground: an online editor for Java, Python, C, C++, JavaScript, TypeScript and C# =====
   The editor is Monaco (the editor inside VS Code), loaded from the jsDelivr CDN.
   Run all runs the whole program. Step line by line runs it once while recording every line, then lets the
   reader move forward and back through that recording, with the variables of every function call.

   Who runs what:
     Python       real CPython 3 (Pyodide, WebAssembly) in a module worker   pg-python.js
     JavaScript   the browser's own JavaScript engine, in a worker           pg-worker.js + js-trace.js
     TypeScript   checked and compiled by the TypeScript compiler inside Monaco, then run like JavaScript
     Java, C, C++ and C#   the playground's own teaching runner, in a worker  pg-worker.js + cf-*.js
   Every run happens in a worker, so Stop can always end a program that never finishes. */
(() => {
  const MONACO = 'https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/';
  const HERE = (document.currentScript && document.currentScript.src) || location.href;
  const url = f => new URL(f, HERE).href;
  const $ = s => document.querySelector(s);
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage unavailable */ } },
    del(k) { try { localStorage.removeItem(k); } catch (e) { /* storage unavailable */ } }
  };

  const LANGS = {
    java: { name: 'Java', mon: 'java', file: 'Main.java', note: '<b>Java</b> runs on the playground’s own teaching runner, inside your browser. It understands what Java courses use: classes, interfaces, records, enums, arrays, strings, ArrayList, HashMap and the other collections, streams, lambdas, exceptions and Scanner input. Output and error messages follow real Java.' },
    python: { name: 'Python', mon: 'python', file: 'main.py', note: '<b>Python</b> is the real CPython 3, running inside your browser with Pyodide. The first run downloads Python once, which takes a few seconds. After that it starts at once.' },
    c: { name: 'C', mon: 'c', file: 'main.c', note: '<b>C</b> runs on the playground’s own teaching runner, inside your browser. It understands printf and scanf, arrays, strings, pointers, structs, malloc and free, and the usual standard library. Where real C would quietly do something unsafe, the runner stops and explains what went wrong.' },
    cpp: { name: 'C++', mon: 'cpp', file: 'main.cpp', note: '<b>C++</b> runs on the playground’s own teaching runner, inside your browser. It understands cout and cin, classes and inheritance, references, templates, lambdas, vector, map, set, string and the common algorithms. Output and error messages follow g++.' },
    js: { name: 'JavaScript', mon: 'javascript', file: 'main.js', note: '<b>JavaScript</b> runs in your browser’s own JavaScript engine. <code>console.log</code> prints to Output, and <code>prompt()</code> reads the next line of the Input box.' },
    ts: { name: 'TypeScript', mon: 'typescript', file: 'main.ts', note: '<b>TypeScript</b> is checked by the real TypeScript compiler, the same one inside VS Code. If the types are right, the compiled JavaScript runs in your browser. <code>prompt()</code> reads the next line of the Input box.' },
    cs: { name: 'C#', mon: 'csharp', file: 'Program.cs', note: '<b>C#</b> runs on the playground’s own teaching runner, inside your browser. It understands classes, structs, records, properties, List and Dictionary, LINQ, string interpolation, ref and out, exceptions and Console input. Output and error messages follow .NET.' }
  };
  const ORDER = ['java', 'python', 'c', 'cpp', 'js', 'ts', 'cs'];

  /* ---------- page parts ---------- */
  const el = {
    lang: $('#pgLang'), ex: $('#pgEx'), sug: $('#pgSug'), sugSt: $('#pgSugSt'), run: $('#pgRun'), step: $('#pgStep'), stop: $('#pgStop'), reset: $('#pgReset'),
    note: $('#pgNote'), status: $('#pgStatus'), ed: $('#pgEditor'), edName: $('#pgFile'), ro: $('#pgRO'), input: $('#pgIn'), out: $('#pgOut'), tips: $('#pgTips'),
    steps: $('#pgSteps'), msg: $('#pgMsg'), frames: $('#pgFrames'), range: $('#pgRange'), cnt: $('#pgCnt'), play: $('#pgPlay'), edit: $('#pgEdit')
  };
  let lang = LANGS[store.get('pg-lang')] ? store.get('pg-lang') : 'java';
  /* embed mode: the side panel on lesson pages opens this page as ?embed=1&lang=java and may send code with
     postMessage({ pg: 'load', lang, code }). The page answers { pg: 'ready' } once the editor is up */
  const QS = new URLSearchParams(location.search);
  const EMBED = QS.has('embed');
  if (EMBED) document.documentElement.classList.add('pg-embed');
  if (LANGS[QS.get('lang')]) lang = QS.get('lang');
  let suggestOn = store.get('pg-suggest') !== '0';
  let monaco = null, editor = null, plain = null;
  const models = {};
  let running = null; /* { worker, timer, mode } */
  let rec = null;     /* the recording being stepped: { trace, text, i } */
  let deco = [];
  let playTimer = null;

  /* ---------- toolbar ---------- */
  el.lang.innerHTML = ORDER.map(k => `<option value="${k}">${LANGS[k].name}</option>`).join('');
  el.lang.value = lang;
  el.sug.checked = suggestOn;
  function fillExamples() {
    el.ex.innerHTML = PG_EXAMPLES[lang].map((e, i) => `<option value="${i}">${esc(e.title)}</option>`).join('');
    el.ex.value = store.get('pg-ex-' + lang) || '0';
  }
  fillExamples();
  function setNote() { el.note.innerHTML = LANGS[lang].note; el.edName.textContent = LANGS[lang].file; }
  setNote();
  function status(t, bad) { el.status.textContent = t || ''; el.status.classList.toggle('err', !!bad); }
  function paintSuggest() { el.sugSt.textContent = suggestOn ? 'On' : 'Off'; }
  paintSuggest();

  /* ---------- code storage: what the reader typed is kept per language ---------- */
  function exampleCode(l) { const i = +(store.get('pg-ex-' + l) || 0); return (PG_EXAMPLES[l][i] || PG_EXAMPLES[l][0]); }
  function savedCode(l) { return store.get('pg-code-' + l); }
  function startCode(l) { return savedCode(l) ?? exampleCode(l).code; }
  function getCode() { return editor ? editor.getValue() : plain ? plain.value : ''; }
  function setCode(c) { if (editor) editor.setValue(c); else if (plain) plain.value = c; }
  let saveT = 0;
  function remember() {
    clearTimeout(saveT);
    saveT = setTimeout(() => {
      const c = getCode();
      if (c === exampleCode(lang).code) store.del('pg-code-' + lang); else store.set('pg-code-' + lang, c);
    }, 400);
  }
  el.input.value = store.get('pg-in-' + lang) ?? exampleCode(lang).stdin;
  el.input.addEventListener('input', () => store.set('pg-in-' + lang, el.input.value));

  /* ---------- the editor ---------- */
  function loadMonaco() {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('timeout')), 20000);
      window.MonacoEnvironment = {
        getWorkerUrl() {
          const src = `self.MonacoEnvironment = { baseUrl: ${JSON.stringify(MONACO)} }; importScripts(${JSON.stringify(MONACO + 'vs/base/worker/workerMain.js')});`;
          return URL.createObjectURL(new Blob([src], { type: 'text/javascript' }));
        }
      };
      const s = document.createElement('script');
      s.src = MONACO + 'vs/loader.js';
      s.onerror = () => { clearTimeout(timer); reject(new Error('loader')); };
      s.onload = () => {
        window.require.config({ paths: { vs: MONACO + 'vs' } });
        window.require(['vs/editor/editor.main'], () => { clearTimeout(timer); resolve(window.monaco); }, e => { clearTimeout(timer); reject(e); });
      };
      document.head.appendChild(s);
    });
  }
  function isDark() { return document.documentElement.dataset.theme === 'dark' || (!document.documentElement.dataset.theme && matchMedia('(prefers-color-scheme: dark)').matches); }
  function suggestOptions(on) {
    return on ? {
      quickSuggestions: { other: true, comments: false, strings: false }, suggestOnTriggerCharacters: true, wordBasedSuggestions: 'currentDocument',
      parameterHints: { enabled: true }, snippetSuggestions: 'inline', tabCompletion: 'on', acceptSuggestionOnEnter: 'on', inlineSuggest: { enabled: true },
      acceptSuggestionOnCommitCharacter: true, suggest: { showWords: true, preview: true }, lightbulb: { enabled: 'onCode' }
    } : {
      quickSuggestions: false, suggestOnTriggerCharacters: false, wordBasedSuggestions: 'off', parameterHints: { enabled: false }, snippetSuggestions: 'none',
      tabCompletion: 'off', acceptSuggestionOnEnter: 'off', inlineSuggest: { enabled: false }, acceptSuggestionOnCommitCharacter: false,
      suggest: { showWords: false, preview: false }, lightbulb: { enabled: 'off' }
    };
  }
  let offKey = null;
  async function startEditor() {
    try {
      monaco = await loadMonaco();
    } catch (e) {
      /* no CDN: a plain text box still lets the reader write and run code */
      el.ed.innerHTML = '<textarea spellcheck="false" aria-label="Code editor"></textarea>';
      plain = el.ed.querySelector('textarea');
      plain.value = startCode(lang);
      plain.addEventListener('input', () => { remember(); endSteps(); });
      plain.addEventListener('keydown', e => { if (e.key === 'Tab') { e.preventDefault(); const s = plain.selectionStart; plain.setRangeText('    ', s, plain.selectionEnd, 'end'); } });
      status('The full editor could not load, so this is a plain text box. Run and Step still work. Autosuggest and TypeScript need the full editor, so check your internet connection and reload.', true);
      return;
    }
    const ts = monaco.languages.typescript;
    ts.typescriptDefaults.setCompilerOptions({ target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.ESNext, strict: true, sourceMap: true, moduleDetection: 3, allowNonTsExtensions: true, noEmitOnError: false });
    ts.javascriptDefaults.setCompilerOptions({ target: ts.ScriptTarget.ES2020, allowNonTsExtensions: true, allowJs: true, moduleDetection: 3 });
    ts.typescriptDefaults.setEagerModelSync(true);
    for (const k of ORDER) models[k] = monaco.editor.createModel(startCode(k), LANGS[k].mon, monaco.Uri.parse('file:///' + LANGS[k].file));
    editor = monaco.editor.create(el.ed, Object.assign({
      model: models[lang], theme: isDark() ? 'vs-dark' : 'vs', automaticLayout: true, fontSize: 14, fontFamily: '"JetBrains Mono", "Roboto Mono", Menlo, Consolas, monospace',
      minimap: { enabled: false }, scrollbar: { alwaysConsumeMouseWheel: false }, /* the page scrolls when the editor has nothing more to scroll */ scrollBeyondLastLine: false, glyphMargin: true, tabSize: 4, renderLineHighlight: 'line', padding: { top: 8 },
      readOnlyMessage: { value: 'The program is being shown step by step. Press Edit code to change it.' }, fixedOverflowWidgets: true, ariaLabel: 'Code editor'
    }, suggestOptions(suggestOn)));
    offKey = editor.createContextKey('pgSuggestOff', !suggestOn);
    /* with autosuggest off, Ctrl+Space does nothing either */
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Space, () => {}, 'pgSuggestOff');
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => run('run'));
    editor.onDidChangeModelContent(() => { remember(); monaco.editor.setModelMarkers(editor.getModel(), 'pg', []); });
    for (const k of ['java', 'python', 'c', 'cpp', 'cs']) registerCompletions(k);
    new MutationObserver(() => monaco.editor.setTheme(isDark() ? 'vs-dark' : 'vs')).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => monaco.editor.setTheme(isDark() ? 'vs-dark' : 'vs'));
    status('');
  }
  function applySuggest() {
    store.set('pg-suggest', suggestOn ? '1' : '0');
    paintSuggest();
    if (!editor) return;
    editor.updateOptions(suggestOptions(suggestOn));
    offKey.set(!suggestOn);
    if (!suggestOn) { editor.trigger('pg', 'hideSuggestWidget', {}); editor.trigger('pg', 'closeParameterHints', {}); }
  }

  /* ---------- autosuggest lists for the languages Monaco has no language service for ---------- */
  const W = s => s.split(/\s+/).filter(Boolean);
  const SUG = {
    java: {
      kw: W('abstract boolean break byte case catch char class continue default do double else enum extends final finally float for if implements import instanceof int interface long new null package private protected public record return short static super switch this throw throws try var void while true false'),
      types: W('String Scanner System Math Integer Double Character Boolean Long ArrayList List LinkedList HashMap Map TreeMap HashSet Set TreeSet ArrayDeque Deque Queue Stack PriorityQueue Arrays Collections StringBuilder Random Optional Exception RuntimeException IllegalArgumentException Comparator Objects'),
      stat: {
        Math: W('max min abs sqrt pow round floor ceil random PI E'), System: W('out in currentTimeMillis exit'), 'System.out': W('println print printf'),
        Arrays: W('toString sort fill asList copyOf stream deepToString binarySearch equals'), Collections: W('sort reverse max min shuffle unmodifiableList frequency swap'),
        Integer: W('parseInt valueOf toString MAX_VALUE MIN_VALUE toBinaryString compare'), Double: W('parseDouble valueOf compare MAX_VALUE'), Character: W('isDigit isLetter isUpperCase isLowerCase toUpperCase toLowerCase isWhitespace getNumericValue'),
        String: W('valueOf join format'), List: W('of copyOf'), Map: W('of entry')
      },
      mem: W('length charAt substring indexOf lastIndexOf equals equalsIgnoreCase toUpperCase toLowerCase trim split contains replace isEmpty startsWith endsWith compareTo toCharArray chars repeat strip add get set remove size clear contains isEmpty sort indexOf forEach stream put getOrDefault containsKey containsValue keySet values entrySet getKey getValue push pop peek offer poll nextInt nextLine next nextDouble nextLong hasNext hasNextInt append insert reverse toString filter map collect toList sum count'),
      snip: [
        ['sout', 'System.out.println(${1});', 'Print a line'], ['main', 'public static void main(String[] args) {\n\t${1}\n}', 'The main method'],
        ['fori', 'for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++) {\n\t${3}\n}', 'Counting for loop'], ['foreach', 'for (${1:int} ${2:x} : ${3:items}) {\n\t${4}\n}', 'For each item'],
        ['if', 'if (${1:condition}) {\n\t${2}\n}', 'If'], ['ifelse', 'if (${1:condition}) {\n\t${2}\n} else {\n\t${3}\n}', 'If and else'], ['while', 'while (${1:condition}) {\n\t${2}\n}', 'While loop'],
        ['scanner', 'Scanner ${1:in} = new Scanner(System.in);', 'Read input'], ['class', 'class ${1:Name} {\n\t${2}\n}', 'A class'], ['try', 'try {\n\t${1}\n} catch (${2:Exception} e) {\n\t${3}\n}', 'Try and catch']
      ]
    },
    python: {
      kw: W('and as assert break class continue def del elif else except False finally for from global if import in is lambda None nonlocal not or pass raise return True try while with yield match case'),
      types: W('print input len range int str float bool list dict set tuple sorted reversed sum min max abs round enumerate zip map filter isinstance type open any all ord chr divmod pow format repr id hex bin'),
      stat: { math: W('sqrt pi e floor ceil pow factorial gcd log log10 sin cos tan inf isclose'), random: W('randint random choice shuffle sample uniform seed'), string: W('ascii_letters ascii_lowercase ascii_uppercase digits punctuation') },
      mem: W('append extend insert pop remove sort reverse index count copy clear upper lower strip lstrip rstrip split join replace find startswith endswith format isdigit isalpha isupper islower title capitalize keys values items get update setdefault add discard union intersection difference'),
      snip: [
        ['def', 'def ${1:name}(${2}):\n\t${3:pass}', 'A function'], ['for', 'for ${1:x} in ${2:items}:\n\t${3:pass}', 'For loop'], ['forr', 'for ${1:i} in range(${2:10}):\n\t${3:pass}', 'For with range'],
        ['if', 'if ${1:condition}:\n\t${2:pass}', 'If'], ['ifelse', 'if ${1:condition}:\n\t${2:pass}\nelse:\n\t${3:pass}', 'If and else'], ['while', 'while ${1:condition}:\n\t${2:pass}', 'While loop'],
        ['class', 'class ${1:Name}:\n\tdef __init__(self${2}):\n\t\t${3:pass}', 'A class'], ['try', 'try:\n\t${1:pass}\nexcept ${2:Exception} as e:\n\t${3:print(e)}', 'Try and except'],
        ['main', 'if __name__ == "__main__":\n\t${1:main()}', 'Run when started'], ['listcomp', '[${1:x} for ${1:x} in ${2:items}]', 'List comprehension']
      ]
    },
    c: {
      kw: W('auto break case char const continue default do double else enum extern float for goto if int long register return short signed sizeof static struct switch typedef union unsigned void volatile while NULL bool true false'),
      types: W('printf scanf puts putchar getchar fgets strlen strcpy strncpy strcat strcmp strncmp strchr strstr malloc calloc realloc free memset memcpy abs sqrt pow fabs floor ceil rand srand time atoi atof exit toupper tolower isdigit isalpha isspace sprintf'),
      stat: {}, mem: [],
      snip: [
        ['main', 'int main(void) {\n\t${1}\n\treturn 0;\n}', 'The main function'], ['printf', 'printf("${1:%d}\\n", ${2});', 'Print'], ['scanf', 'scanf("${1:%d}", &${2:x});', 'Read a number'],
        ['fori', 'for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++) {\n\t${3}\n}', 'Counting for loop'], ['if', 'if (${1:condition}) {\n\t${2}\n}', 'If'], ['while', 'while (${1:condition}) {\n\t${2}\n}', 'While loop'],
        ['struct', 'struct ${1:Name} {\n\t${2:int x;}\n};', 'A struct'], ['inc', '#include <${1:stdio.h}>', 'Include a header']
      ]
    },
    cpp: {
      kw: W('auto bool break case catch char class const constexpr continue default delete do double else enum explicit false float for friend if inline int long namespace new nullptr operator private protected public return short signed sizeof static struct switch template this throw true try typedef typename using virtual void while override'),
      types: W('std cout cin cerr endl string vector map unordered_map set unordered_set pair make_pair stack queue deque priority_queue sort reverse max min swap find count accumulate to_string stoi stod getline fixed setprecision setw abs sqrt pow begin end greater less'),
      stat: {},
      mem: W('push_back pop_back size empty clear begin end front back insert erase find count at first second top push pop substr length find_first_of append c_str emplace_back resize'),
      snip: [
        ['main', 'int main() {\n\t${1}\n\treturn 0;\n}', 'The main function'], ['cout', 'cout << ${1} << endl;', 'Print'], ['cin', 'cin >> ${1:x};', 'Read a value'],
        ['fori', 'for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++) {\n\t${3}\n}', 'Counting for loop'], ['foreach', 'for (auto &${1:x} : ${2:items}) {\n\t${3}\n}', 'For each item'],
        ['if', 'if (${1:condition}) {\n\t${2}\n}', 'If'], ['class', 'class ${1:Name} {\npublic:\n\t${2}\n};', 'A class'], ['inc', '#include <${1:iostream}>', 'Include a header']
      ]
    },
    cs: {
      kw: W('abstract as base bool break byte case catch char class const continue decimal default do double else enum false finally float for foreach if in int interface internal is long namespace new null object out override params private protected public readonly record ref return sealed short static string struct switch this throw true try using var virtual void while'),
      types: W('Console Math List Dictionary HashSet Queue Stack StringBuilder Convert String Array Random Exception Enumerable DateTime int double string bool char'),
      stat: {
        Console: W('WriteLine Write ReadLine'), Math: W('Max Min Abs Sqrt Pow Round Floor Ceiling PI'), Convert: W('ToInt32 ToDouble ToString ToBoolean'), int: W('Parse TryParse MaxValue MinValue'),
        double: W('Parse TryParse'), string: W('Join Format IsNullOrEmpty Concat'), String: W('Join Format IsNullOrEmpty Concat'), Array: W('Sort Reverse IndexOf Fill Resize')
      },
      mem: W('Length Count Add Remove RemoveAt Insert Contains IndexOf Clear Sort Reverse ToUpper ToLower Trim Split Substring Replace StartsWith EndsWith ToString Equals ContainsKey TryGetValue Keys Values Push Pop Peek Enqueue Dequeue Append Where Select OrderBy OrderByDescending Sum Average Max Min First FirstOrDefault Any All ToList ToArray Distinct Take Skip GroupBy'),
      snip: [
        ['cw', 'Console.WriteLine(${1});', 'Print a line'], ['main', 'static void Main()\n{\n\t${1}\n}', 'The Main method'], ['for', 'for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++)\n{\n\t${3}\n}', 'Counting for loop'],
        ['foreach', 'foreach (var ${1:x} in ${2:items})\n{\n\t${3}\n}', 'For each item'], ['if', 'if (${1:condition})\n{\n\t${2}\n}', 'If'], ['class', 'class ${1:Name}\n{\n\t${2}\n}', 'A class'],
        ['prop', 'public ${1:int} ${2:Name} { get; set; }', 'A property'], ['try', 'try\n{\n\t${1}\n}\ncatch (${2:Exception} e)\n{\n\t${3}\n}', 'Try and catch']
      ]
    }
  };
  function registerCompletions(k) {
    const S = SUG[k];
    monaco.languages.registerCompletionItemProvider(LANGS[k].mon, {
      triggerCharacters: ['.'],
      provideCompletionItems(model, pos) {
        if (!suggestOn || model !== models[k]) return { suggestions: [] };
        const word = model.getWordUntilPosition(pos);
        const range = { startLineNumber: pos.lineNumber, endLineNumber: pos.lineNumber, startColumn: word.startColumn, endColumn: word.endColumn };
        const before = model.getValueInRange({ startLineNumber: pos.lineNumber, startColumn: 1, endLineNumber: pos.lineNumber, endColumn: word.startColumn });
        const K = monaco.languages.CompletionItemKind;
        const m = before.match(/([A-Za-z_][\w.]*)\s*(\.|->|::)$/);
        if (m) {
          const owner = m[1];
          const list = S.stat[owner] || (/^[A-Z]/.test(owner) && k !== 'python' ? null : null) || S.mem;
          return { suggestions: [...new Set(list)].map(w => ({ label: w, kind: S.stat[owner] ? K.Field : K.Method, insertText: w, range })) };
        }
        const out = [];
        S.kw.forEach(w => out.push({ label: w, kind: K.Keyword, insertText: w, range }));
        S.types.forEach(w => out.push({ label: w, kind: K.Class, insertText: w, range }));
        S.snip.forEach(([label, body, doc]) => out.push({ label, kind: K.Snippet, insertText: body, insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: doc, detail: doc, range }));
        return { suggestions: out };
      }
    });
  }

  /* ---------- running ---------- */
  let pyWorker = null, pyReady = null, pyVersion = '';
  function getPython() {
    if (pyReady) return pyReady;
    pyWorker = new Worker(url('pg-python.js'), { type: 'module' });
    status('Loading Python into your browser. The first time takes a few seconds, after that the browser keeps it.');
    pyReady = new Promise((resolve, reject) => {
      const first = ev => {
        if (ev.data.k === 'ready') { pyVersion = ev.data.v; pyWorker.removeEventListener('message', first); resolve(pyWorker); }
        if (ev.data.k === 'fail') { pyWorker.removeEventListener('message', first); killPython(); reject(new Error(ev.data.msg)); }
      };
      pyWorker.addEventListener('message', first);
      pyWorker.addEventListener('error', ev => { ev.preventDefault && ev.preventDefault(); killPython(); reject(new Error('Python could not be loaded. Check your internet connection, then try again.')); });
    });
    return pyReady;
  }
  function killPython() { if (pyWorker) pyWorker.terminate(); pyWorker = null; pyReady = null; }

  function busy(on) {
    el.run.disabled = on; el.step.disabled = on; el.stop.disabled = !on; el.lang.disabled = on; el.ex.disabled = on; el.reset.disabled = on;
  }
  busy(false);
  function stop(why) {
    if (!running) return;
    clearTimeout(running.timer);
    if (running.worker === pyWorker) killPython(); else if (running.worker) running.worker.terminate();
    running = null;
    busy(false);
    if (why) { appendOut('\n' + why + '\n', true); status(why, true); }
  }

  async function run(mode) {
    if (running) return;
    endSteps();
    clearMarkers();
    el.tips.innerHTML = '';
    const code = getCode();
    const stdin = el.input.value.replace(/\r\n/g, '\n');
    const L = lang;
    if (!code.trim()) { status('The editor is empty. Write a program first, or pick an example.', true); return; }
    el.out.innerHTML = '';
    busy(true);
    running = { mode };
    status(mode === 'step' ? 'Running the program once and recording every line...' : 'Running...');
    let payload = { lang: L, code, stdin, trace: mode === 'step' };
    if (L === 'ts') {
      const c = await compileTs();
      if (!running) return;
      if (c.errors) { finish({ out: [{ s: c.errors, e: true }], compile: c.first, trace: null, notes: [] }, L, mode); return; }
      payload = { lang: 'ts', code: c.js, lineMap: c.map, stdin, trace: mode === 'step' };
    }
    if (L === 'python') {
      let w;
      try { w = await getPython(); } catch (e) { running = null; busy(false); status(e.message, true); return; }
      if (!running) return;
      running.worker = w;
      status(mode === 'step' ? 'Running the program once and recording every line...' : 'Running Python ' + pyVersion + '...');
      const onMsg = ev => {
        const d = ev.data;
        if (d.k === 'chunk') appendOut(d.s, d.e);
        else if (d.k === 'done') { w.removeEventListener('message', onMsg); finish(d.res, L, mode); }
        else if (d.k === 'fail') { w.removeEventListener('message', onMsg); running && clearTimeout(running.timer); running = null; busy(false); status(d.msg, true); }
      };
      w.addEventListener('message', onMsg);
      running.timer = setTimeout(() => stop('The program ran for 30 seconds, so the playground stopped it. Check for a loop whose condition never becomes false, or for input() waiting for text that is not in the Input box.'), 30000);
      w.postMessage(payload);
      return;
    }
    const w = new Worker(url('pg-worker.js'));
    running.worker = w;
    w.onmessage = ev => {
      const d = ev.data;
      if (d.k === 'done') finish(d.res, L, mode);
      else if (d.k === 'fail') { stop(); status(d.msg, true); }
    };
    w.onerror = ev => { ev.preventDefault && ev.preventDefault(); stop(); status('The runner could not start. Reload the page and try again.', true); };
    running.timer = setTimeout(() => stop('The program ran for 30 seconds, so the playground stopped it. Check for a loop whose condition never becomes false.'), 30000);
    w.postMessage(payload);
  }

  function finish(res, L, mode) {
    if (!running) return;
    clearTimeout(running.timer);
    if (running.worker && running.worker !== pyWorker) running.worker.terminate();
    running = null;
    busy(false);
    const text = (res.out || []).map(o => o.s).join('');
    if (res.compile) {
      const c = res.compile;
      if (!text) el.out.innerHTML = `<span class="e">${esc(compileText(L, c))}</span>`; else renderOut(res.out);
      markLine(c.line, 'err', c.msg);
      status(`The program did not start: there is a mistake on line ${c.line}.`, true);
      addTip(friendlyCompile(L, c), true);
      return;
    }
    if (mode === 'step' && res.trace && res.trace.length) {
      startSteps(res, text);
    } else {
      if (L !== 'python' || !el.out.childNodes.length) renderOut(res.out || []);
      if (!text) el.out.innerHTML = '<span class="none">The program finished without printing anything.</span>';
      if (res.error) { markLine(res.error.line, 'err', firstLine(res.error.msg)); status(`The program stopped with an error on line ${res.error.line}.`, true); addTip(friendlyError(L, res.error), true); }
      else if (res.stopped) status(res.stopped, true);
      else status(res.exit ? `The program finished with exit code ${res.exit}.` : 'The program finished.');
    }
    (res.notes || []).forEach(n => addTip(n));
    if (res.stopped && mode === 'step') addTip(res.stopped);
  }
  function compileText(L, c) {
    switch (L) {
      case 'java': return `Main.java:${c.line}: error: ${c.msg}`;
      case 'c': return `main.c:${c.line}: error: ${c.msg}`;
      case 'cpp': return `main.cpp:${c.line}: error: ${c.msg}`;
      case 'cs': { const m = /^(CS\d{4}): ([\s\S]*)$/.exec(c.msg); return m ? `Program.cs(${c.line}): error ${m[1]}: ${m[2]}` : `Program.cs(${c.line}): error: ${c.msg}`; }
      case 'js': return `${c.msg}\n    at line ${c.line}`;
      default: return `Line ${c.line}: ${c.msg}`;
    }
  }
  function friendlyCompile(L, c) {
    const base = `The ${LANGS[L].name} checker found a mistake on line ${c.line} before the program could start, so no line has run yet. The red mark in the editor shows the line.`;
    return c.hint ? `${base} ${c.hint}` : `${base} Fix it and press Run again.`;
  }
  function friendlyError(L, e) {
    const m = e.msg || '';
    if (/IndexOutOfRange|ArrayIndexOutOfBounds|IndexError|out_of_range|outside the (vector|array)/.test(m)) return `Line ${e.line} asked for an item that is not there. Lists and arrays count from 0, so a list of 3 items has positions 0, 1 and 2 only.`;
    if (/ZeroDivision|by zero|divided .* by zero/i.test(m)) return `Line ${e.line} divides by zero. No number times zero gives a non zero number, so the computer cannot answer it.`;
    if (/NullPointer|NullReference|null|undefined/.test(m) && /read|invoke|Cannot|reference/i.test(m)) return `Line ${e.line} used something that is empty (null). Give it a real value first, or check for null before you use it.`;
    if (/StackOverflow|recursion|call stack/i.test(m)) return `A function kept calling itself and never stopped. Every recursive function needs a base case that returns without calling itself again.`;
    if (/NumberFormat|FormatException|invalid literal|ValueError/.test(m)) return `Line ${e.line} tried to turn text into a number, but the text was not a number. Check what you typed in the Input box.`;
    if (/EOFError|NoSuchElement|no line|Input box/i.test(m)) return `The program wanted more input than the Input box had. Type each value on its own line in the Input box and run again.`;
    if (/NameError|cannot find symbol|not defined|was not declared/.test(m)) return `Line ${e.line} uses a name the program does not know. Check the spelling, and that it is created before this line.`;
    if (/TypeError/.test(m)) return `Line ${e.line} used a value in a way its type does not allow, for example adding a number to text or calling something that is not a function.`;
    return `The program stopped on line ${e.line}. Read the last line of the red message: it names the problem.`;
  }
  function firstLine(s) { const l = String(s || '').trim().split('\n'); return l[l.length - 1]; }
  function addTip(t, bad) { const d = document.createElement('div'); d.className = 'pg-tip' + (bad ? ' bad' : ''); d.textContent = t; el.tips.appendChild(d); }
  function renderOut(out) {
    el.out.innerHTML = out.map(o => o.e ? `<span class="e">${esc(o.s)}</span>` : esc(o.s)).join('');
  }
  function appendOut(s, e) {
    const n = el.out.querySelector('.none'); if (n) n.remove();
    if (e) { const sp = document.createElement('span'); sp.className = 'e'; sp.textContent = s; el.out.appendChild(sp); }
    else el.out.appendChild(document.createTextNode(s));
    el.out.scrollTop = el.out.scrollHeight;
  }

  /* ---------- TypeScript: check, compile and map lines back ---------- */
  async function compileTs() {
    if (!monaco) return { errors: 'TypeScript needs the full editor, which could not load. Check your internet connection and reload the page.', first: { line: 1, msg: 'TypeScript is not available' } };
    const model = models.ts;
    const getW = await monaco.languages.typescript.getTypeScriptWorker();
    const w = await getW(model.uri);
    const uri = model.uri.toString();
    const diags = [...await w.getSyntacticDiagnostics(uri), ...await w.getSemanticDiagnostics(uri)].filter(d => d.category === 1);
    if (diags.length) {
      const lines = diags.map(d => {
        const p = model.getPositionAt(d.start || 0);
        return { line: p.lineNumber, col: p.column, text: `main.ts(${p.lineNumber},${p.column}): error TS${d.code}: ${flat(d.messageText)}` };
      });
      lines.forEach(l => markLine(l.line, 'err', l.text));
      return { errors: lines.map(l => l.text).join('\n') + `\n\nFound ${lines.length} error${lines.length > 1 ? 's' : ''}.`, first: { line: lines[0].line, msg: lines[0].text } };
    }
    const emit = await w.getEmitOutput(uri);
    const jsFile = emit.outputFiles.find(f => /\.js$/.test(f.name));
    const mapFile = emit.outputFiles.find(f => /\.js\.map$/.test(f.name));
    let js = jsFile ? jsFile.text : '';
    js = js.replace(/^\/\/# sourceMappingURL=.*$/m, '').replace(/^export \{\};?\s*$/m, '');
    return { js, map: mapFile ? lineMap(JSON.parse(mapFile.text).mappings) : null };
  }
  function flat(m) { if (typeof m === 'string') return m; let s = m.messageText; if (m.next) s += ' ' + m.next.map(flat).join(' '); return s; }
  /* source map "mappings": for each line of the JavaScript, the line of TypeScript it came from */
  function lineMap(mappings) {
    const B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
    const map = [0];
    let srcLine = 0;
    mappings.split(';').forEach((group, gi) => {
      let first = null;
      for (const seg of group.split(',')) {
        if (!seg) continue;
        const vals = []; let v = 0, shift = 0;
        for (const ch of seg) {
          const d = B64.indexOf(ch);
          v += (d & 31) << shift;
          if (d & 32) shift += 5; else { vals.push(v & 1 ? -(v >> 1) : v >> 1); v = 0; shift = 0; }
        }
        if (vals.length >= 4) { srcLine += vals[2]; if (first === null) first = srcLine; }
      }
      map[gi + 1] = first !== null ? first + 1 : (map[gi] || 1);
    });
    return map;
  }

  /* ---------- editor marks ---------- */
  function markLine(line, kind, msg) {
    if (!editor || !line) return;
    const model = editor.getModel();
    const n = Math.min(Math.max(1, line), model.getLineCount());
    if (kind === 'err') {
      const old = monaco.editor.getModelMarkers({ owner: 'pg', resource: model.uri });
      monaco.editor.setModelMarkers(model, 'pg', old.concat([{ severity: monaco.MarkerSeverity.Error, message: msg || 'Error', startLineNumber: n, startColumn: 1, endLineNumber: n, endColumn: model.getLineMaxColumn(n) }]));
      deco = editor.deltaDecorations(deco, [{ range: new monaco.Range(n, 1, n, 1), options: { isWholeLine: true, className: 'pg-line-err', glyphMarginClassName: 'pg-glyph-err' } }]);
      editor.revealLineInCenterIfOutsideViewport(n);
    }
  }
  function clearMarkers() { if (!editor) return; monaco.editor.setModelMarkers(editor.getModel(), 'pg', []); deco = editor.deltaDecorations(deco, []); }

  /* ---------- step by step ---------- */
  function startSteps(res, text) {
    rec = { trace: res.trace, text, i: 0, res };
    el.steps.hidden = false;
    el.range.max = String(rec.trace.length - 1);
    el.range.value = '0';
    if (editor) editor.updateOptions({ readOnly: true });
    if (plain) plain.readOnly = true;
    el.ro.hidden = false;
    status(`Recorded ${rec.trace.length} steps. Press Next to move one line forward.`);
    show(0);
    el.steps.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }
  function endSteps() {
    pause();
    if (!rec) return;
    rec = null;
    el.steps.hidden = true;
    el.ro.hidden = true;
    if (editor) { editor.updateOptions({ readOnly: false }); deco = editor.deltaDecorations(deco, []); }
    if (plain) plain.readOnly = false;
  }
  function topOf(s) { return s.stack && s.stack.length ? s.stack[s.stack.length - 1] : null; }
  function show(i) {
    if (!rec) return;
    i = Math.max(0, Math.min(rec.trace.length - 1, i));
    rec.i = i;
    const s = rec.trace[i], p = i > 0 ? rec.trace[i - 1] : null;
    el.range.value = String(i);
    el.cnt.textContent = `Step ${i + 1} of ${rec.trace.length}`;
    el.steps.querySelectorAll('[data-a="first"], [data-a="back"]').forEach(b => { b.disabled = i === 0; });
    el.steps.querySelectorAll('[data-a="fwd"], [data-a="last"]').forEach(b => { b.disabled = i === rec.trace.length - 1; });
    /* the editor */
    if (editor) {
      const model = editor.getModel(), max = model.getLineCount();
      const ds = [];
      const cl = Math.min(max, Math.max(1, s.line));
      if (s.ev !== 'end') ds.push({ range: new monaco.Range(cl, 1, cl, 1), options: { isWholeLine: true, className: s.ev === 'error' ? 'pg-line-err' : 'pg-line-cur', glyphMarginClassName: s.ev === 'error' ? 'pg-glyph-err' : 'pg-glyph-cur' } });
      if (p && p.line !== s.line && p.ev !== 'end') { const pl = Math.min(max, Math.max(1, p.line)); ds.push({ range: new monaco.Range(pl, 1, pl, 1), options: { isWholeLine: true, className: 'pg-line-prev' } }); }
      deco = editor.deltaDecorations(deco, ds);
      if (s.ev !== 'end') editor.revealLineInCenterIfOutsideViewport(cl);
    }
    /* output so far, with what this step printed marked */
    const upto = Math.min(rec.text.length, s.out), from = p ? Math.min(upto, p.out) : 0;
    const older = rec.text.slice(0, from), fresh = rec.text.slice(from, upto);
    el.out.innerHTML = upto ? outHtml(older, 0) + (fresh ? '<mark>' + outHtml(fresh, from) + '</mark>' : '') : '<span class="none">Nothing printed yet.</span>';
    el.out.scrollTop = el.out.scrollHeight;
    /* variables */
    el.frames.innerHTML = framesHtml(s, p);
    el.msg.innerHTML = explain(i);
  }
  /* parts of the output that were errors are shown in red */
  function outHtml(t, start) {
    let pos = 0, h = '';
    const parts = rec.res.out || [];
    let at = 0;
    for (const o of parts) {
      const a = Math.max(at, start), b = Math.min(at + o.s.length, start + t.length);
      if (b > a) { const piece = rec.text.slice(a, b); h += o.e ? `<span class="e">${esc(piece)}</span>` : esc(piece); pos += b - a; }
      at += o.s.length;
    }
    if (pos < t.length) h += esc(t.slice(pos));
    return h;
  }
  function same(fa, fb) { return fa && fb && fa.fn === fb.fn; }
  function framesHtml(s, p) {
    const st = s.stack || [];
    if (!st.length && s.ev === 'end') return '<div class="pg-frame"><div class="empty">The program has finished, so its variables are gone.</div></div>';
    const blocks = [];
    for (let k = st.length - 1; k >= 0; k--) {
      const f = st[k], old = p && p.stack && p.stack.length > k && same(p.stack[k], f) && (p.stack.length >= st.length || k < p.stack.length - 1 || p.ev !== 'ret') ? p.stack[k] : null;
      const oldMap = new Map((old ? old.vars : []).map(v => [v[0], v[1]]));
      const rows = f.vars.map(v => {
        const cls = v[2] === 'tdz' ? 'tdz' : old && !oldMap.has(v[0]) ? 'new' : old && oldMap.get(v[0]) !== v[1] ? 'chg' : '';
        const tag = cls === 'new' ? '<span class="tag">new</span>' : cls === 'chg' ? '<span class="tag">changed</span>' : '';
        return `<tr class="${cls}"><td>${esc(v[0])}${v[2] === 'ref' ? ' &amp;' : ''}</td><td>${esc(v[1])}${tag}</td></tr>`;
      }).join('');
      const title = esc(f.fn === 'Main program' ? f.fn : f.fn.replace(/\(\)$/, '') + '()');
      blocks.push(`<div class="pg-frame${k === st.length - 1 ? ' top' : ''}"><h3>${title} <small>line ${f.line}${k === st.length - 1 ? ', running now' : ', waiting for the call above to finish'}</small></h3>${rows ? `<table>${rows}</table>` : '<div class="empty">No variables yet.</div>'}</div>`);
    }
    if (s.globals && s.globals.length) {
      const og = new Map(((p && p.globals) || []).map(v => [v[0], v[1]]));
      blocks.push(`<div class="pg-frame"><h3>Global and static variables</h3><table>${s.globals.map(v => { const c = p && og.has(v[0]) && og.get(v[0]) !== v[1] ? 'chg' : ''; return `<tr class="${c}"><td>${esc(v[0])}</td><td>${esc(v[1])}${c ? '<span class="tag">changed</span>' : ''}</td></tr>`; }).join('')}</table></div>`);
    }
    return blocks.join('');
  }
  function fname(f) { return f ? (f.fn === 'Main program' ? 'the main program' : `<code>${esc(f.fn.replace(/\(\)$/, ''))}()</code>`) : ''; }
  function changes(s, p) {
    const out = [];
    if (!p || !s.stack) return out;
    for (let k = 0; k < s.stack.length; k++) {
      const f = s.stack[k], o = p.stack && p.stack[k];
      if (!same(f, o)) continue;
      if (p.ev === 'call' && k === p.stack.length - 1 && s.stack.length === p.stack.length) { /* first line inside a call: parameters already shown */ }
      const om = new Map(o.vars.map(v => [v[0], v[1]]));
      for (const v of f.vars) {
        if (v[2] === 'tdz') continue;
        if (!om.has(v[0])) out.push(`<code>${esc(v[0])}</code> is created with the value <code>${esc(v[1])}</code>`);
        else if (om.get(v[0]) !== v[1] && om.get(v[0]) !== 'not set yet') out.push(`<code>${esc(v[0])}</code> changes from <code>${esc(om.get(v[0]))}</code> to <code>${esc(v[1])}</code>`);
        else if (om.get(v[0]) === 'not set yet') out.push(`<code>${esc(v[0])}</code> gets the value <code>${esc(v[1])}</code>`);
      }
    }
    return out;
  }
  function printed(s, p) {
    const a = p ? p.out : 0, b = s.out;
    if (b <= a) return '';
    let t = rec.text.slice(a, b).replace(/\n$/, '');
    if (t.length > 80) t = t.slice(0, 77) + '...';
    return t.includes('\n') ? 'It prints some lines (see Output).' : `It prints <code>${esc(t)}</code>.`;
  }
  function list(xs) { return xs.length <= 1 ? xs.join('') : xs.slice(0, -1).join(', ') + ' and ' + xs[xs.length - 1]; }
  function explain(i) {
    const s = rec.trace[i], p = i > 0 ? rec.trace[i - 1] : null;
    const top = topOf(s), ptop = p && topOf(p);
    const parts = [];
    if (s.ev === 'end') {
      const pr = printed(s, p);
      parts.push(rec.res.error ? 'The program has ended because of the error.' : 'The program has finished.');
      if (pr) parts.push(pr);
      if (rec.res.stopped) parts.push(esc(rec.res.stopped) + '.');
      return parts.join(' ');
    }
    if (s.ev === 'error') {
      return `Line ${s.line} causes an error, and the program stops here: <code>${esc(firstLine(s.msg || (rec.res.error && rec.res.error.msg)))}</code>. ${esc(friendlyError(lang, { msg: s.msg || '', line: s.line }))}`;
    }
    if (!p) {
      parts.push(`The program starts. The first line to run is line ${s.line}.`);
      if (s.ev === 'call') parts.push(`It begins inside ${fname(top)}.`);
      return parts.join(' ');
    }
    const ch = changes(s, p), pr = printed(s, p);
    if (s.ev === 'call') {
      const caller = s.stack[s.stack.length - 2];
      const params = top.vars.filter(v => v[2] !== 'this').map(v => `<code>${esc(v[0])} = ${esc(v[1])}</code>`);
      parts.push(`Line ${caller ? caller.line : p.line} calls ${fname(top)}. The program jumps to line ${s.line}${params.length ? ', with ' + list(params) : ''}.`);
      if (pr) parts.push(pr);
      return parts.join(' ');
    }
    if (s.ev === 'ret') {
      if (p.ev !== 'ret' && p.line === s.line && !ch.length && !pr) parts.push(`Line ${s.line} runs.`);
      else if (ch.length) parts.push(`Line ${p.line} runs: ${list(ch)}.`);
      if (pr) parts.push(pr);
      parts.push(`${fname(top)} is finished${s.ret !== undefined && s.ret !== 'null' && s.ret !== 'None' && s.ret !== 'undefined' && s.ret !== '' ? ` and gives back <code>${esc(s.ret)}</code>` : ''}. The program goes back to the line that called it.`);
      return parts.join(' ');
    }
    if (p.ev === 'call' && same(top, ptop) && s.stack.length === p.stack.length) {
      parts.push(`Inside ${fname(top)}, the first line to run is line ${s.line}.`);
      if (pr) parts.push(pr);
      return parts.join(' ');
    }
    if (p.ev === 'ret' && ptop && (!top || s.stack.length < p.stack.length)) {
      parts.push(`Back in ${fname(top)} on line ${p.stack.length >= 2 ? p.stack[p.stack.length - 2].line : s.line}, the answer from ${fname(ptop)} is used.`);
      if (ch.length) parts.push(`Now ${list(ch)}.`);
      if (pr) parts.push(pr);
      parts.push(`Next comes line ${s.line}.`);
      return parts.join(' ');
    }
    parts.push(`Line ${p.line} ran${ch.length ? ': ' + list(ch) : ''}.`);
    if (pr) parts.push(pr);
    if (s.line < p.line && same(top, ptop)) parts.push(`The program goes back up to line ${s.line}, so a loop is repeating or its condition is checked again.`);
    else if (s.line > p.line + 1 && same(top, ptop)) parts.push(`It skips ahead to line ${s.line}.`);
    else parts.push(`Next comes line ${s.line}.`);
    return parts.join(' ');
  }
  function pause() { if (playTimer) { clearInterval(playTimer); playTimer = null; } el.play.textContent = 'Play'; }
  function play() {
    if (!rec) return;
    if (playTimer) { pause(); return; }
    if (rec.i >= rec.trace.length - 1) show(0);
    el.play.textContent = 'Pause';
    playTimer = setInterval(() => {
      if (!rec) { pause(); return; }
      if (window.__vtHold && window.__vtHold(el.steps)) return;
      if (rec.i >= rec.trace.length - 1) { pause(); return; }
      show(rec.i + 1);
    }, 900);
  }
  el.steps.addEventListener('click', e => {
    const b = e.target.closest('button[data-a]');
    if (!b || !rec) return;
    const a = b.dataset.a;
    if (a !== 'play') pause();
    if (a === 'first' || a === 'reset') show(0);
    else if (a === 'back') show(rec.i - 1);
    else if (a === 'fwd') show(rec.i + 1);
    else if (a === 'last') show(rec.trace.length - 1);
    else if (a === 'play') play();
  });
  el.range.addEventListener('input', () => { pause(); show(+el.range.value); });
  el.edit.addEventListener('click', () => { endSteps(); status('You can edit the code again.'); if (editor) editor.focus(); });
  document.addEventListener('keydown', e => {
    if (!rec || e.target.closest('textarea, select, input:not([type=range])')) return;
    if (editor && editor.hasTextFocus() && !e.altKey) { /* the editor is read only while stepping, so arrows move the cursor there */ }
    if (e.key === 'ArrowRight' && e.altKey) { e.preventDefault(); pause(); show(rec.i + 1); }
    if (e.key === 'ArrowLeft' && e.altKey) { e.preventDefault(); pause(); show(rec.i - 1); }
  });

  /* ---------- toolbar actions ---------- */
  function switchLang(k) {
    endSteps();
    clearMarkers();
    lang = k;
    store.set('pg-lang', k);
    fillExamples();
    setNote();
    if (editor) editor.setModel(models[k]); else if (plain) plain.value = startCode(k);
    el.input.value = store.get('pg-in-' + k) ?? exampleCode(k).stdin;
    el.out.innerHTML = '<span class="none">Press Run all or Step line by line to see what the program prints.</span>';
    el.tips.innerHTML = '';
    status('');
  }
  el.lang.addEventListener('change', () => switchLang(el.lang.value));
  el.ex.addEventListener('change', () => {
    const cur = getCode();
    const changed = savedCode(lang) !== null && cur !== exampleCode(lang).code;
    store.set('pg-ex-' + lang, el.ex.value);
    const ex = exampleCode(lang);
    if (changed) status('Your earlier code was replaced by the example. Press Ctrl+Z in the editor to get it back.');
    endSteps(); clearMarkers();
    setCode(ex.code);
    store.del('pg-code-' + lang);
    el.input.value = ex.stdin; store.set('pg-in-' + lang, ex.stdin);
    el.out.innerHTML = '<span class="none">Press Run all or Step line by line to see what the program prints.</span>';
    el.tips.innerHTML = '';
  });
  el.sug.addEventListener('change', () => { suggestOn = el.sug.checked; applySuggest(); });
  el.run.addEventListener('click', () => run('run'));
  el.step.addEventListener('click', () => run('step'));
  el.stop.addEventListener('click', () => stop('Stopped by you.'));
  el.reset.addEventListener('click', () => {
    endSteps(); clearMarkers();
    const ex = exampleCode(lang);
    setCode(ex.code);
    store.del('pg-code-' + lang);
    el.input.value = ex.stdin; store.set('pg-in-' + lang, ex.stdin);
    el.out.innerHTML = '<span class="none">Press Run all or Step line by line to see what the program prints.</span>';
    el.tips.innerHTML = '';
    status('The example is back as it was. Press Ctrl+Z in the editor to undo this.');
  });
  el.out.innerHTML = '<span class="none">Press Run all or Step line by line to see what the program prints.</span>';
  /* Monaco cancels its own pending work when the model changes, and reports that as an unhandled "Canceled" */
  window.addEventListener('unhandledrejection', e => { if (e.reason && (e.reason.name === 'Canceled' || e.reason.message === 'Canceled')) e.preventDefault(); });
  window.addEventListener('error', e => { if (e.message && /\bCanceled\b/.test(e.message)) { e.preventDefault(); e.stopImmediatePropagation(); } }, true);
  /* code sent from a lesson: it replaces what is in the editor for that language. Ctrl+Z brings the old code back */
  let pending = null, ready = false;
  function loadSent(d) {
    if (d.lang && LANGS[d.lang] && d.lang !== lang) { switchLang(d.lang); el.lang.value = d.lang; }
    endSteps(); clearMarkers();
    setCode(d.code);
    el.out.innerHTML = '<span class="none">Press Run all or Step line by line to see what the program prints.</span>';
    el.tips.innerHTML = '';
    status(d.note || 'The code from the lesson is in the editor. Press Run all, or Step line by line.');
    if (editor) editor.focus();
  }
  window.addEventListener('message', e => {
    const d = e.data || {};
    if (d.pg !== 'load' || typeof d.code !== 'string' || e.origin !== location.origin) return;
    if (ready) loadSent(d); else pending = d;
  });
  startEditor().then(() => {
    ready = true;
    if (pending) { loadSent(pending); pending = null; }
    if (EMBED && window.parent !== window) { try { parent.postMessage({ pg: 'ready' }, location.origin === 'null' ? '*' : location.origin); } catch (e) { /* no parent */ } }
  });
})();
