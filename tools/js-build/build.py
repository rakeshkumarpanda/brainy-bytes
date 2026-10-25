"""Build the JavaScript chapter pages in content/javascript/ from the topic files in topics/.

Every example on a page is run for real when the page is built, and the real output is shown under it:
  run    plain JavaScript, run with Node.js (the same code also runs in the reader's browser with "Edit and run")
  dom    browser code, run against its HTML with jsdom (in the browser it runs inside a small sandboxed frame)
  test   a small project (test files, config, an app to test) run with a real runner: node:test, Jest, Vitest,
         Mocha, Playwright or Selenium WebDriver. The terminal output is shown exactly as the runner printed it.
  show   code that is shown but not run here, such as Cypress specs and CI files. The label says so.

Practice exercises are checked too: every model solution must pass its tests and every starter must fail one.

The page frame (styles, quiz, number crunch, narrator, diagrams) is the same one the Java chapters use,
plus assets/jsplay.js and assets/jsplay.css for the editable examples, the exercises and the QA path.
The JavaScript block in data/catalog.js (between the js-build markers) is rewritten from the same topic files.

Usage:  python3 tools/js-build/build.py [slug ...]        (no slug builds every chapter)
Needs:  python3, Node.js 26 (set JS_BUILD_NODE to its binary if it is not first on PATH),
        npm ci inside tools/js-build/box, a Chromium for Playwright (PLAYWRIGHT_BROWSERS_PATH),
        and for the Selenium examples a chromedriver that matches that Chromium (CHROMEDRIVER).
"""
import concurrent.futures as cf
import hashlib
import html
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'content', 'javascript')
CACHE = os.path.join(HERE, '.cache')
BOX = os.path.join(HERE, 'box')
RUNS = os.path.join(BOX, 'runs')
NODE = os.environ.get('JS_BUILD_NODE') or shutil.which('node')
CHROME = os.environ.get('CHROME_BIN', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
CHROMEDRIVER = os.environ.get('CHROMEDRIVER', '')
SUBJECT = 'javascript'
RUN_STAMP = 4  # bump to rerun every example after changing how examples are run
LANGS = ['en', 'hi', 'kn', 'or', 'ar', 'de']


# ---------- syntax colouring, the same classes the Java chapters use ----------
KW = {
    'js': set(('break case catch class const continue debugger default delete do else export extends false finally for function if '
               'import in instanceof let new null return super switch this throw true try typeof undefined var void while with yield '
               'of async await static get set using from as').split()),
    'ts': set(('break case catch class const continue debugger default delete do else export extends false finally for function if '
               'import in instanceof let new null return super switch this throw true try typeof undefined var void while with yield '
               'of async await static get set using from as type interface implements private public protected readonly enum '
               'number string boolean unknown any never keyof satisfies').split()),
    'java': set(('abstract assert boolean break byte case catch char class const continue default do double else enum extends final '
                 'finally float for if implements import instanceof int interface long new package private protected public return '
                 'short static super switch this throw throws try var void while true false null record').split()),
    'py': set(('and as assert async await break class continue def del elif else except False finally for from global if import in '
               'is lambda None nonlocal not or pass raise return True try while with yield').split()),
    'json': {'true', 'false', 'null'},
    'bash': {'npm', 'npx', 'node', 'cd', 'export', 'git', 'mkdir'},
    'yaml': {'true', 'false', 'null'},
}


def hl(code, lang='js'):
    if lang == 'html':
        return hl_html(code)
    kws = KW.get(lang, KW['js'])
    if lang in ('py', 'bash', 'yaml'):
        comment = r'#[^\n]*'
    elif lang == 'json':
        comment = r'(?!x)x'
    else:
        comment = r'//[^\n]*|/\*[\s\S]*?\*/'
    strings = r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\''
    if lang in ('js', 'ts'):
        strings = r'`(?:[^`\\]|\\.)*`|' + strings
    tok = re.compile('(?P<c>' + comment + ')|(?P<s>' + strings + r')|(?P<n>\b\d[\d_]*(?:\.\d+)?(?:[eE][+-]?\d+)?n?\b|\b0[xXbBoO][0-9a-fA-F_]+n?\b)'
                     r'|(?P<a>@[A-Za-z]+)|(?P<w>[A-Za-z_$#][\w$]*)|(?P<o>[\s\S])')
    out = []
    for m in tok.finditer(code):
        kind = m.lastgroup
        t = html.escape(m.group(), quote=False)
        if kind == 'w':
            w = m.group()
            if w in kws:
                out.append(f'<span class="k">{t}</span>')
            elif w[0].isupper() and lang not in ('bash', 'yaml'):
                out.append(f'<span class="t">{t}</span>')
            else:
                out.append(t)
        elif kind == 'o':
            out.append(t)
        elif kind == 'a' and lang in ('json', 'bash', 'yaml'):
            out.append(t)
        else:
            out.append(f'<span class="{kind}">{t}</span>')
    return ''.join(out)


def hl_html(code):
    out, i = [], 0
    for m in re.finditer(r'<!--[\s\S]*?-->|<script\b[^>]*>[\s\S]*?</script>|</?[A-Za-z][^>]*>', code):
        out.append(html.escape(code[i:m.start()], quote=False))
        t = m.group()
        if t.startswith('<!--'):
            out.append(f'<span class="c">{html.escape(t, quote=False)}</span>')
        elif t.lower().startswith('<script'):
            open_tag = re.match(r'<script\b[^>]*>', t).group()
            body = t[len(open_tag):-len('</script>')]
            out.append(tag_html(open_tag) + hl(body, 'js') + tag_html('</script>'))
        else:
            out.append(tag_html(t))
        i = m.end()
    out.append(html.escape(code[i:], quote=False))
    return ''.join(out)


def tag_html(t):
    m = re.match(r'(</?)([A-Za-z][\w-]*)([\s\S]*?)(/?>)$', t)
    if not m:
        return html.escape(t, quote=False)
    attrs = []
    for a in re.finditer(r'([^\s=]+)(\s*=\s*)("[^"]*"|\'[^\']*\'|[^\s>]+)|([^\s=]+)|(\s+)', m.group(3)):
        if a.group(1):
            attrs.append(f'<span class="a">{html.escape(a.group(1))}</span>{a.group(2)}<span class="s">{html.escape(a.group(3), quote=False)}</span>')
        elif a.group(4):
            attrs.append(f'<span class="a">{html.escape(a.group(4))}</span>')
        else:
            attrs.append(a.group(5))
    return f'{html.escape(m.group(1))}<span class="k">{m.group(2)}</span>{"".join(attrs)}{html.escape(m.group(4))}'


# ---------- running the examples ----------
ANSI = re.compile(r'\x1b\[[0-9;?]*[A-Za-z]')
_node_version = None


def node_version():
    global _node_version
    if _node_version is None:
        _node_version = subprocess.run([NODE, '-v'], capture_output=True, text=True).stdout.strip()
    return _node_version


def env():
    # A plain terminal environment: some runners shorten their output when they detect an AI agent or a CI service.
    e = {k: v for k, v in os.environ.items() if not re.match(r'(CLAUDE|AI_AGENT|CCR_|CURSOR|CODEX|GITHUB_ACTIONS|GITLAB|BUILDKITE|TF_BUILD)', k)}
    e['PATH'] = os.pathsep.join([os.path.join(BOX, 'node_modules', '.bin'), os.path.dirname(NODE), e.get('PATH', '')])
    e.update({'CI': '1', 'NO_COLOR': '1', 'TZ': 'UTC', 'LANG': 'en_US.UTF-8',
              'CHROME_BIN': CHROME, 'CHROMEDRIVER': CHROMEDRIVER})
    e.setdefault('PLAYWRIGHT_BROWSERS_PATH', '/opt/pw-browsers')
    e.pop('NODE_OPTIONS', None)
    return e


def clean(text, d):
    text = ANSI.sub('', text).replace('\r\n', '\n')
    real = os.path.realpath(d)
    for p in {d, real}:
        text = text.replace('file://' + p + '/', '').replace(p + '/', '').replace(p, 'project')
    # Runtime deprecation notices come from the tools, not from the example, so they are left out.
    text = re.sub(r'\(node:\d+\) \[DEP\d+\] DeprecationWarning.*\n(\(Use `node --trace-deprecation.*\n)?', '', text)
    text = re.sub(r"\(node:\d+\) Warning: The 'NO_COLOR' env is ignored.*\n(\(Use `node --trace-warnings.*\n)?", '', text)
    lines = [ln for ln in text.split('\n') if not re.match(r'\s+at .*\bnode:[a-z_]', ln) and not re.match(r'\s+at .*node_modules', ln)]
    return '\n'.join(lines).rstrip()


DOM_HARNESS = r'''
const { JSDOM, VirtualConsole } = require('jsdom');
const fs = require('fs');
const vc = new VirtualConsole();
vc.forwardTo(console, { jsdomErrors: 'none' });
vc.on('jsdomError', e => console.error(String(e.detail || e.message)));
const dom = new JSDOM(fs.readFileSync('page.html', 'utf8'), { runScripts: 'dangerously', virtualConsole: vc, url: 'https://shop.example/' });
// Wrapped like the in-browser runner does, so top level await works the same in both.
dom.window.__fail = e => { console.error(e && e.stack ? String(e.stack).split('\n').slice(0, 2).join('\n') : String(e)); process.exitCode = 1; };
dom.window.eval('(async () => {\n' + fs.readFileSync('code.js', 'utf8') + '\n})().catch(window.__fail);');
setTimeout(() => dom.window.close(), 1500);
'''


def run_spec(spec):
    """Run one example and return {'out': text, 'code': exit status}. Results are cached by content."""
    key = hashlib.sha256(json.dumps([spec, node_version(), DOM_HARNESS, RUN_STAMP], sort_keys=True).encode()).hexdigest()[:24]
    cpath = os.path.join(CACHE, key + '.json')
    if os.path.exists(cpath):
        return json.load(open(cpath, encoding='utf-8'))
    os.makedirs(RUNS, exist_ok=True)
    d = tempfile.mkdtemp(prefix='r', dir=RUNS)
    try:
        t = spec['t']
        if t == 'run':
            name = spec.get('file', 'main.mjs')
            write(d, {name: spec['code'], **spec.get('extra', {})})
            cmd = [NODE, *spec.get('flags', []), name]
            p = subprocess.run(cmd, cwd=d, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120, env=env(), input=spec.get('stdin', ''))
            out = p.stdout
        elif t == 'dom':
            write(d, {'page.html': spec['html'], 'code.js': spec['code'], 'harness.cjs': DOM_HARNESS})
            p = subprocess.run([NODE, 'harness.cjs'], cwd=d, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120, env=env())
            out = p.stdout
        elif t == 'test':
            write(d, spec['files'])
            p = subprocess.run(spec['cmd'], cwd=d, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=400, env=env())
            out = p.stdout
        else:
            raise ValueError('unknown example type ' + t)
        res = {'out': clean(out, d), 'code': p.returncode}
    finally:
        shutil.rmtree(d, ignore_errors=True)
    os.makedirs(CACHE, exist_ok=True)
    json.dump(res, open(cpath, 'w', encoding='utf-8'), ensure_ascii=False)
    return res


def write(d, files):
    for name, body in files.items():
        p = os.path.join(d, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(body.strip('\n') + '\n')


EX_HARNESS = r'''
const ex = JSON.parse(require('fs').readFileSync('ex.json', 'utf8'));
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
(async () => {
  const AsyncFunction = (async () => {}).constructor;
  let fails = 0;
  try {
    const body = ex.code + '\n;return [' + ex.tests.map(t => 'async () => (' + t.call + ')').join(',') + '];';
    const fns = await new AsyncFunction('console', body)({ log() {}, info() {}, warn() {}, error() {}, table() {} });
    for (let i = 0; i < fns.length; i++) {
      let got;
      try { got = await fns[i](); } catch (e) { got = 'threw ' + (e && e.message); }
      if (!same(got, ex.tests[i].want)) { fails++; console.log('FAIL ' + ex.tests[i].call + ' gave ' + JSON.stringify(got) + ', wanted ' + JSON.stringify(ex.tests[i].want)); }
    }
  } catch (e) { fails = ex.tests.length; console.log('ERROR ' + e.message); }
  console.log('fails=' + fails);
})();
'''


def check_exercise(code, tests):
    spec = {'t': 'run', 'file': 'harness.cjs', 'code': EX_HARNESS, 'extra': {'ex.json': json.dumps({'code': code, 'tests': tests})}}
    r = run_spec(spec)
    m = re.search(r'fails=(\d+)', r['out'])
    return (int(m.group(1)) if m else -1), r['out']


# ---------- page parts ----------
def esc(s):
    return html.escape(str(s))


def js(v):
    return json.dumps(v, ensure_ascii=False).replace('</', '<\\/')


def badge(spec):
    if spec.get('badge'):
        return spec['badge']
    if spec['t'] == 'run':
        return '▶ Runs' if spec.get('expect', 'ok') == 'ok' else '💥 Throws'
    if spec['t'] == 'dom':
        return '▶ Runs in the browser'
    if spec['t'] == 'test':
        return '🧪 Tests run' if spec.get('expect', 'pass') == 'pass' else '🧪 Tests run, one fails on purpose'
    return spec.get('note', 'Not run on this page')


def block(key, spec, res):
    label = esc(spec.get('label', 'Example'))
    play = ''
    if spec['t'] == 'run' and spec.get('play', True):
        play = ' data-play="worker"' + (' data-strict="1"' if spec.get('file', 'main.mjs').endswith('.mjs') else '')
    elif spec['t'] == 'dom' and spec.get('play', True):
        play = ' data-play="dom"'
    bar = (f'<div class="codebar"><span class="dots"><i></i><i></i><i></i></span><span class="lbl">{label} · {badge(spec)}</span>'
           f'{"<button type=\"button\" class=\"try\">✏️ Edit and run</button>" if play else ""}<button type="button" class="copy">Copy</button></div>')
    if spec['t'] == 'test':
        shown = spec.get('show') or list(spec['files'])
        body = ''
        for n in shown:
            lang = lang_of(n)
            body += f'<div class="fname">📄 {esc(n)}</div><pre class="src" data-file="{esc(n)}">{hl(spec["files"][n].strip(chr(10)), lang)}</pre>'
        cmd = spec.get('shown_cmd', spec['cmd'])
        body += f'<div class="cmd"><span>Terminal</span><pre>$ {esc(cmd)}</pre></div>'
        ok = (res['code'] == 0) == (spec.get('expect', 'pass') == 'pass')
        if not ok:
            raise SystemExit(f'{key}: test run ended with exit code {res["code"]}, expected {spec.get("expect", "pass")}\n{res["out"]}')
        if 'ts_errors' in spec:
            found = len(re.findall(r'error TS\d+', res['out']))
            if found != spec['ts_errors']:
                raise SystemExit(f'{key}: tsc reported {found} type errors, expected {spec["ts_errors"]}\n{res["out"]}')
        cls = 'out' if res['code'] == 0 else 'err'
        body += f'<div class="{cls}"><span>Terminal output</span><pre>{esc(trim(res["out"], spec))}</pre></div>'
        return f'<div class="codewrap tests" data-k="{key}">{bar}{body}</div>'
    code = spec['code'].strip('\n')
    lang = spec.get('lang', 'js')
    body = ''
    if spec['t'] == 'run' and spec.get('extra'):
        # A small multi file program: show the helper files, then the file that is run and the command.
        for n, src in spec['extra'].items():
            body += f'<div class="fname">📄 {esc(n)}</div><pre class="src" data-file="{esc(n)}">{hl(src.strip(chr(10)), lang_of(n))}</pre>'
        body += f'<div class="fname">📄 {esc(spec.get("file", "main.mjs"))}</div>'
    if spec['t'] == 'dom':
        body += f'<div class="fname">📄 page.html</div><pre class="src fixture">{hl(spec["html"].strip(chr(10)), "html")}</pre><div class="fname">📄 script.js</div>'
    body += f'<pre class="src main">{hl(code, lang)}</pre>'
    if spec['t'] == 'run' and (spec.get('extra') or spec.get('flags')):
        body += f'<div class="cmd"><span>Terminal</span><pre>$ {esc(" ".join(["node", *spec.get("flags", []), spec.get("file", "main.mjs")]))}</pre></div>'
    if spec['t'] in ('run', 'dom'):
        want_fail = spec.get('expect', 'ok') != 'ok'
        if (res['code'] != 0) != want_fail:
            raise SystemExit(f'{key}: exit code {res["code"]} but expect is {spec.get("expect", "ok")}\n{res["out"]}')
        out = trim(res['out'], spec)
        if spec.get('expect', 'ok') == 'ok':
            body += f'<div class="out"><span>Output</span><pre>{esc(out)}</pre></div>' if out else '<div class="out"><span>Output</span><pre class="none">(prints nothing)</pre></div>'
        else:
            body += f'<div class="err"><span>Output</span><pre>{esc(out)}</pre></div>'
    elif spec.get('result'):
        body += f'<div class="note-out"><span>What happens</span><p>{spec["result"]}</p></div>'
    return f'<div class="codewrap" data-k="{key}"{play}>{bar}{body}</div>'


def trim(out, spec):
    for a, b in spec.get('replace', []):
        out = re.sub(a, b, out)
    if spec.get('tail'):
        out = '\n'.join(out.split('\n')[-spec['tail']:])
    return out


def lang_of(name):
    ext = name.rsplit('.', 1)[-1]
    return {'js': 'js', 'mjs': 'js', 'cjs': 'js', 'ts': 'ts', 'json': 'json', 'html': 'html', 'yml': 'yaml', 'yaml': 'yaml',
            'java': 'java', 'py': 'py', 'sh': 'bash', 'env': 'bash', 'txt': 'bash'}.get(ext, 'js')


def load_topic(path):
    sys.path.insert(0, HERE)
    spec = importlib.util.spec_from_file_location('topic_' + re.sub(r'\W', '_', os.path.basename(path)[:-3]), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.T


def check(T):
    errs = []
    keys = set(T['codes'])
    used = set()
    for p in T['parts']:
        used |= set(re.findall(r'\[\[([\w-]+)\]\]', p['html']))
    for k in used - keys:
        errs.append(f'code block {k} is used but not written')
    for k in keys - used:
        errs.append(f'code block {k} is written but never shown')
    says = {'top', 'practice'} | {p['id'] for p in T['parts']}
    given = {s['id'] for s in T['say']}
    for s in says - given:
        errs.append(f'narration missing for {s}')
    for s in given - says:
        errs.append(f'narration {s} has no matching part')
    for s in T['say']:
        for lang in LANGS:
            if not s.get(lang):
                errs.append(f'narration {s["id"]} has no {lang} text')
    for q in T['quiz']:
        if not 0 <= q['a'] < len(q['o']):
            errs.append('quiz answer out of range: ' + q['q'])
    ids = [p['id'] for p in T['parts']] + [e['id'] for e in T['ex']]
    if len(ids) != len(set(ids)):
        errs.append('duplicate part or exercise id')
    for k in list(T.get('dg', {})) + list(T.get('lanes', {})):
        if not any(f'data-k="{k}"' in p['html'] for p in T['parts']):
            errs.append(f'animation {k} is never shown')
    # House style for reader facing text: no em or en dashes and no semicolons outside code.
    for where, t in prose_pieces(T):
        bare = re.sub(r'<pre[\s\S]*?</pre>|<code>[\s\S]*?</code>|<span class="eq">[\s\S]*?</span>|\[\[[\w-]+\]\]|&#?\w+;', ' ', t)
        for bad, name in (('—', 'an em dash'), ('–', 'an en dash'), (';', 'a semicolon')):
            if bad in bare:
                i = bare.index(bad)
                errs.append(f'{name} in {where}: ...{bare[max(0, i - 50):i + 20].strip()}...')
    return errs


def prose_pieces(T):
    yield 'lead', T['lead']
    for k in ('summary', 'desc', 'qa_intro', 'title'):
        yield k, T.get(k, '')
    for p in T['parts']:
        yield 'part ' + p['id'], p['html'] + ' ' + p['title'] + ' ' + (p.get('qa_why') or '')
    for q in T['quiz']:
        yield 'quiz', ' '.join([q['q'], q['hint'], q['why']])
    for c in T['calc']:
        yield 'calc', ' '.join([c['q'], c['hint'], *c['steps']])
    for s in T['say']:
        yield 'narration ' + s['id'], ' '.join(s[l] for l in LANGS)
    for e in T['ex']:
        yield 'exercise ' + e['id'], ' '.join([e['title'], e['task'], e['hint'], e['why']])
    for pn in T['info']['panels']:
        yield 'comic', ' '.join([pn['h'], pn['t'], pn['more']])
    yield 'comic', T['info']['title'] + ' ' + T['info']['remember']
    for r in T['real']:
        yield 'real life', ' '.join(r[1:])
    for spec in T['codes'].values():
        if spec.get('result'):
            yield 'result note', spec['result']


def topic_files():
    return sorted(f for f in os.listdir(os.path.join(HERE, 'topics')) if re.match(r'\d\d[a-z]?-.*\.py$', f))


def all_topics():
    return [load_topic(os.path.join(HERE, 'topics', f)) for f in topic_files()]


def build(T, chapters):
    errs = check(T)
    if errs:
        raise SystemExit(f'{T["slug"]}:\n  ' + '\n  '.join(errs))

    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        jobs = {k: ex.submit(run_spec, s) for k, s in T['codes'].items() if s['t'] != 'show'}
        res = {}
        for k, f in jobs.items():
            try:
                res[k] = f.result()
            except subprocess.TimeoutExpired:
                raise SystemExit(f'{T["slug"]}: {k} timed out')
    for e in T['ex']:
        fails, out = check_exercise(e['solution'], e['tests'])
        if fails:
            raise SystemExit(f'{T["slug"]}: the solution to exercise {e["id"]} fails {fails} test(s)\n{out}')
        fails, out = check_exercise(e['starter'], e['tests'])
        if fails == 0:
            raise SystemExit(f'{T["slug"]}: the starter for exercise {e["id"]} already passes every test')

    blocks = {k: block(k, s, res.get(k)) for k, s in T['codes'].items()}
    play = {k: {'html': s['html']} for k, s in T['codes'].items() if s['t'] == 'dom'}

    parts = T['parts']
    n_viz = sum(len(re.findall(r'data-viz="', p['html'])) for p in parts)
    n_run = sum(1 for s in T['codes'].values() if s['t'] in ('run', 'dom'))
    n_test = sum(1 for s in T['codes'].values() if s['t'] == 'test' and 'ts_errors' not in s)
    n_ts = sum(1 for s in T['codes'].values() if 'ts_errors' in s)
    n_qa = sum(1 for p in parts if p.get('qa'))
    chips = [f'⏱️ About {T["minutes"]} min read', f'📚 {len(parts)} parts', f'🎬 {n_viz} animations'] + ([f'▶ {n_run} runnable examples'] if n_run else []) + ([f'🔷 {n_ts} type checked example' + ('s' if n_ts > 1 else '')] if n_ts else []) + ([f'🧪 {n_test} real test run' + ('s' if n_test > 1 else '')] if n_test else []) + [
             f'🏋️ {len(T["ex"])} hands-on exercises', f'🎯 {len(T["quiz"])} quiz questions', f'🧮 {len(T["calc"])} calculations',
             f'🧪 {n_qa} QA essential parts']
    chip_html = ''.join(f'<span class="chip">{c}</span>' for c in chips)
    toc = ''.join(f'<a href="#{p["id"]}"{" class=\"qa\"" if p.get("qa") else ""}><span>{p["emoji"]}</span>{esc(p["title"])}</a>' for p in parts)
    toc += ('<a class="spec" href="#comic">🖼️ Comic</a><a class="spec" href="#real-life">🌍 Real life</a>'
            '<a class="spec" href="#practice">🏋️ Hands-on</a><a class="spec" href="#quiz">🎯 Quiz</a>'
            '<a class="spec" href="#numbers">🧮 Number crunch</a>')
    secs = []
    for i, p in enumerate(parts, 1):
        body = re.sub(r'\[\[([\w-]+)\]\]', lambda m: blocks[m.group(1)], p['html'].strip())
        qa = p.get('qa')
        tag = ''
        if qa:
            tools = qa if isinstance(qa, list) else []
            tag = ('<div class="qa-tag"><span class="qa-badge">🧪 QA essential</span>'
                   + ''.join(f'<span class="qa-tool">{esc(t)}</span>' for t in tools)
                   + (f'<span class="qa-why">{p["qa_why"]}</span>' if p.get('qa_why') else '') + '</div>')
        secs.append(f'<section class="card reveal jsec{" qa-part" if qa else ""}" id="{p["id"]}" data-say="{p["id"]}"><div class="sec-num">Part {i}</div>'
                    f'<h2><span class="sec-em">{p["emoji"]}</span><span>{esc(p["title"])}</span></h2>\n{tag}\n{body}\n</section>\n')

    idx = [c['slug'] for c in chapters].index(T['slug'])
    pv = chapters[idx - 1] if idx else None
    nx = chapters[idx + 1] if idx + 1 < len(chapters) else None
    a = (f'<a class="prev" href="./{pv["slug"]}.html" data-topic="{pv["slug"]}"><small>← Previous chapter</small><b>{pv["emoji"]} {esc(pv["short"])}</b></a>' if pv else '<span></span>')
    b = (f'<a class="next" href="./{nx["slug"]}.html" data-topic="{nx["slug"]}"><small>Next chapter →</small><b>{nx["emoji"]} {esc(nx["short"])}</b></a>' if nx else '<span></span>')
    pager = f'<nav class="pager">{a}{b}</nav>'

    page = {k: T[k] for k in ['info', 'real', 'quiz', 'calc', 'say', 'ex']}
    page['quiz'] = [{**q, 'q': inline(q['q']), 'o': [inline(o) for o in q['o']], 'hint': inline(q['hint']), 'why': inline(q['why'])} for q in T['quiz']]
    page['calc'] = [{**c, 'q': inline(c['q']), 'hint': inline(c['hint']), 'steps': [inline(x) for x in c['steps']]} for c in T['calc']]
    page['dg'] = T.get('dg', {})
    page['lanes'] = T.get('lanes', {})
    page['play'] = play
    mod = T['module']
    qa_box = f'<div class="qa-intro"><b>🧪 For QA engineers</b><p>{T["qa_intro"]}</p></div>' if T.get('qa_intro') else ''
    out = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(T["title"])} · JavaScript</title>
<meta name="description" content="{esc(T["desc"])}">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Nunito:wght@500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/theme.css">
<link rel="stylesheet" href="../../assets/extras.css">
<link rel="stylesheet" href="../../assets/learn.css">
<link rel="stylesheet" href="../../assets/lesson.css">
<link rel="stylesheet" href="../../assets/viz.css">
<link rel="stylesheet" href="../../assets/jsplay.css">
</head>
<body>
<div class="wrap">
  <div class="crumb"><a class="home-link" href="../../subject.html?s={SUBJECT}" target="_top">🟨 JavaScript</a><span>›</span><span>{mod[0]} {esc(mod[1])}</span><span>›</span><span>Chapter {idx + 1} of {len(chapters)}</span></div>
  <header class="hero" id="top" data-say="top">
    <div class="hero-row"><span class="em">{T["emoji"]}</span><div><h1>{esc(T["title"])}</h1><p class="lead">{T["lead"]}</p></div></div>
    <div class="chips">{chip_html}<button type="button" class="listen-btn" id="listenAll">🎧 Listen in 6 languages</button></div>
    {qa_box}
  </header>
  <nav class="toc" aria-label="Parts of this chapter">{toc}<button type="button" class="qa-toggle" id="qaOnly" aria-pressed="false">🧪 Show the QA path only</button></nav>
  <section class="card reveal" id="comic"></section>

{"".join(secs)}
  <section class="card reveal" id="real-life"></section>
  <section class="card reveal" id="practice" data-say="practice"></section>
  <section class="card reveal" id="quiz"></section>
  <section class="card reveal" id="numbers"></section>
  {pager}
</div>
<script src="../../assets/fun.js"></script>
<script src="../../assets/extras.js"></script>
<script src="../../assets/learn.js"></script>
<script src="../../assets/voice.js"></script>
<script src="../../assets/viz.js"></script>
<script src="../../assets/jsviz.js"></script>
<script src="../../assets/jsplay.js"></script>
<script>
const PAGE = {js(page)};
JSPLAY.page({{ title: {js(T["title"])}, subject: {js(SUBJECT)} }});
</script>
</body>
</html>
'''
    dest = os.path.join(OUT, T['slug'] + '.html')
    os.makedirs(OUT, exist_ok=True)
    open(dest, 'w', encoding='utf-8').write(out)
    print(f'{T["slug"]}: {len(parts)} parts, {n_viz} animations, {n_run} runnable, {n_ts} type checked, {n_test} test runs, {len(T["ex"])} exercises, '
          f'{len(out) // 1024} KB -> {os.path.relpath(dest, ROOT)}')


# ---------- the catalog block ----------
INLINE_TAGS = r'(?:code|b|i|em|strong|span|sup|sub|br)'


def inline(s):
    """Quiz and calc text is shown as HTML. Keep the few inline tags the topics use and escape every other <,
    so code such as <T>, <button> or a < b shows as text."""
    return re.sub(r'<(?!/?' + INLINE_TAGS + r'[\s>/])', '&lt;', s)


def strip_tags(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()


def catalog(chapters):
    mods = []
    for T in chapters:
        if not mods or mods[-1]['key'] != T['module']:
            mods.append({'key': T['module'], 'topics': []})
        mods[-1]['topics'].append(T)
    L = ['function jsModules() {', '  return [']
    for mi, m in enumerate(mods):
        em, title, mid, blurb = m['key']
        L.append(f'    {{ id: {js(mid)}, title: {js(title)}, emoji: {js(em)}, blurb: {js(blurb)}, topics: [')
        for ti, T in enumerate(m['topics']):
            secs = []
            for p in T['parts']:
                secs.append(f'        {{ id: {js(p["id"])}, title: {js(p["title"])}, emoji: {js(p["emoji"])}, group: {js("QA essential" if p.get("qa") else "Lesson")}, keywords: {js(p.get("kw", []))} }}')
            lvn = {'e': 'Easy', 'm': 'Medium', 'h': 'Hard', 'x': 'Expert'}
            for e in T['ex']:
                secs.append(f'        {{ id: {js(e["id"])}, title: {js(e["title"])}, emoji: "🏋️", group: {js(lvn[e["lv"]] + " practice")} }}')
            secs.append("        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' }")
            secs.append("        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }")
            L.append(f'      {{ id: {js(T["slug"])}, title: {js(T["title"])}, emoji: {js(T["emoji"])}, page: {js("content/javascript/" + T["slug"] + ".html")},')
            L.append(f'        summary: {js(T["summary"])},')
            L.append(f'        keywords: {js(T["keywords"])},')
            L.append(f'        added: {js(T.get("added", "2026-10-20"))},')
            L.append('        sections: [')
            L.append(',\n'.join(secs))
            L.append('      ] }' + (',' if ti + 1 < len(m['topics']) else ''))
        L.append('    ] }' + (',' if mi + 1 < len(mods) else ''))
    L.append('  ];')
    L.append('}')
    block_text = '\n'.join(L)
    path = os.path.join(ROOT, 'data', 'catalog.js')
    src = open(path, encoding='utf-8').read()
    start, end = '/* ===== js-build: JavaScript chapters. Generated by tools/js-build/build.py, edit the topic files instead. ===== */', '/* ===== end of js-build ===== */'
    new = f'{start}\n{block_text}\n{end}'
    if start in src:
        src = re.sub(re.escape(start) + r'[\s\S]*?' + re.escape(end), lambda _: new, src)
    else:
        src = src.rstrip('\n') + '\n\n' + new + '\n'
    open(path, 'w', encoding='utf-8').write(src)
    print(f'catalog: {len(chapters)} chapters in {len(mods)} modules -> data/catalog.js')


def main():
    if not NODE:
        raise SystemExit('Node.js was not found. Set JS_BUILD_NODE.')
    print('Node', node_version())
    chapters = all_topics()
    want = sys.argv[1:]
    for T in chapters:
        if not want or T['slug'] in want:
            build(T, chapters)
    catalog(chapters)


if __name__ == '__main__':
    main()
