"""Build the Python chapter pages in content/python/ from the topic files in topics/.

Every example on a page is run for real with CPython 3.14 when the page is built, and the real output is shown under it:
  run    one Python file, run with python3.14. It also gets a line by line recording (pytrace.py) for the
         "Line by line" viewer, and in the reader's browser "Edit and run" runs it again with Pyodide.
  test   a small project (several files and a shell command, for example python -m pytest or a look inside
         __pycache__). The terminal output is shown exactly as it was printed.
  show   code that is shown but not run here. The label says so.

Practice exercises are checked too: every model solution must pass its tests and every starter must fail one.

The page frame (styles, quiz, number crunch, narrator, comic, diagrams and lanes) is the same one the JavaScript
chapters use. assets/pyplay.js adds the Python runner, the line by line viewer and the exercises, and
assets/pyviz.js adds the Python animations. The Python block in data/catalog.js (between the py-build markers)
is rewritten from the same topic files.

Usage:  python3 tools/py-build/build.py [slug ...]        (no slug builds every chapter)
Needs:  CPython 3.14 (set PY_BUILD_PYTHON to its binary if python3.14 is not on PATH), Node.js for the
        animation check, and the test tools in box/ (see README.md).
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
OUT = os.path.join(ROOT, 'content', 'python')
CACHE = os.path.join(HERE, '.cache')
BOX = os.path.join(HERE, 'box')
VENV = os.path.join(BOX, '.venv')
RUNS = os.path.join(BOX, 'runs')
PY = os.environ.get('PY_BUILD_PYTHON') or shutil.which('python3.14')
SUBJECT = 'python'
RUN_STAMP = 1  # bump to rerun every example after changing how examples are run
LANGS = ['en', 'hi', 'kn', 'or', 'ar', 'de']
TRACER = os.path.join(HERE, 'pytrace.py')


# ---------- syntax colouring, the same classes the other chapters use ----------
KW = {
    'py': set(('and as assert async await break case class continue def del elif else except False finally for from global if import in '
               'is lambda match None nonlocal not or pass raise return True try type while with yield').split()),
    'json': {'true', 'false', 'null'},
    'bash': {'python', 'python3', 'python3.14', 'pip', 'cd', 'export', 'ls', 'cat', 'echo', 'mkdir', 'rm', 'py'},
    'yaml': {'true', 'false', 'null'},
    'toml': {'true', 'false'},
    'java': set(('class public static void int return new').split()),
}


def hl(code, lang='py'):
    kws = KW.get(lang, KW['py'])
    comment = r'#[^\n]*' if lang in ('py', 'bash', 'yaml', 'toml', 'txt') else r'//[^\n]*'
    if lang == 'txt':
        return html.escape(code, quote=False)
    strings = r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\''
    if lang == 'py':
        strings = r'[rbfRBFt]{0,2}(?:"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|' + strings + ')'
    tok = re.compile('(?P<c>' + comment + ')|(?P<s>' + strings + r')|(?P<n>\b\d[\d_]*(?:\.\d+)?(?:[eE][+-]?\d+)?j?\b|\b0[xXbBoO][0-9a-fA-F_]+\b)'
                     r'|(?P<a>@[A-Za-z_][\w.]*)|(?P<w>[A-Za-z_][\w]*)|(?P<o>[\s\S])')
    out = []
    for m in tok.finditer(code):
        kind = m.lastgroup
        t = html.escape(m.group(), quote=False)
        if kind == 'w':
            w = m.group()
            if w in kws:
                out.append(f'<span class="k">{t}</span>')
            elif w[0].isupper() and lang == 'py':
                out.append(f'<span class="t">{t}</span>')
            else:
                out.append(t)
        elif kind == 'o':
            out.append(t)
        elif kind == 'a' and lang != 'py':
            out.append(t)
        else:
            out.append(f'<span class="{kind}">{t}</span>')
    return ''.join(out)


# ---------- running the examples ----------
ANSI = re.compile(r'\x1b\[[0-9;?]*[A-Za-z]')
_py_version = None


def py_version():
    global _py_version
    if _py_version is None:
        _py_version = subprocess.run([PY, '-c', 'import sys; print(sys.version.split()[0])'], capture_output=True, text=True).stdout.strip()
    return _py_version


def shim():
    """A folder whose python, python3 and python3.14 all start the build's CPython, put first on PATH."""
    d = os.path.join(BOX, 'bin')
    os.makedirs(d, exist_ok=True)
    for n in ('python', 'python3', 'python3.14'):
        p = os.path.join(d, n)
        if os.path.lexists(p) and os.path.realpath(p) != os.path.realpath(PY):
            os.remove(p)
        if not os.path.lexists(p):
            os.symlink(PY, p)
    return d


def env():
    # A plain terminal: some tools shorten their output when they detect an AI agent or a CI service.
    e = {k: v for k, v in os.environ.items() if not re.match(r'(CLAUDE|AI_AGENT|CCR_|CURSOR|CODEX|GITHUB_ACTIONS|GITLAB|BUILDKITE|TF_BUILD|PYTHON|VIRTUAL_ENV)', k)}
    paths = [os.path.join(VENV, 'bin')] if os.path.isdir(VENV) else []
    e['PATH'] = os.pathsep.join(paths + [shim(), e.get('PATH', '')])
    e.update({'NO_COLOR': '1', 'TZ': 'UTC', 'LANG': 'en_US.UTF-8', 'PYTHONHASHSEED': '0', 'COLUMNS': '100', 'TERM': 'dumb'})
    return e


def clean(text, d):
    text = ANSI.sub('', text).replace('\r\n', '\n')
    real = os.path.realpath(d)
    for p in {d, real}:
        text = text.replace(p + '/', '').replace(p, 'project')
    for p in {sys.prefix, os.path.dirname(os.path.dirname(os.path.realpath(PY)))}:
        text = text.replace(p + '/lib/python3.14/', '/usr/lib/python3.14/')
    return text.rstrip()


def run_spec(spec):
    """Run one example and return {'out': text, 'code': exit status, 'trace': recording or None}. Cached by content."""
    tracer_src = open(TRACER, encoding='utf-8').read()
    key = hashlib.sha256(json.dumps([spec, py_version(), tracer_src, RUN_STAMP], sort_keys=True).encode()).hexdigest()[:24]
    cpath = os.path.join(CACHE, key + '.json')
    if os.path.exists(cpath):
        return json.load(open(cpath, encoding='utf-8'))
    os.makedirs(RUNS, exist_ok=True)
    d = tempfile.mkdtemp(prefix='r', dir=RUNS)
    trace = None
    try:
        t = spec['t']
        if t == 'run':
            name = spec.get('file', 'main.py')
            write(d, {name: spec['code'], **spec.get('extra', {})})
            cmd = [PY, *spec.get('flags', []), name, *spec.get('args', [])]
            p = subprocess.run(cmd, cwd=d, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120, env=env(), input=spec.get('stdin', ''))
            out = p.stdout
            if spec.get('trace', True) and not spec.get('extra') and not spec.get('flags') and name == 'main.py':
                open(os.path.join(d, '_stdin.txt'), 'w', encoding='utf-8').write(spec.get('stdin', ''))
                tp = subprocess.run([PY, TRACER, name, '_stdin.txt'], cwd=d, capture_output=True, text=True, timeout=120, env=env())
                if tp.returncode:
                    raise SystemExit('the line by line recorder failed:\n' + tp.stderr)
                trace = json.loads(tp.stdout)
        elif t == 'test':
            write(d, spec['files'])
            p = subprocess.run(spec['cmd'], cwd=d, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=400, env=env())
            out = p.stdout
        else:
            raise ValueError('unknown example type ' + t)
        res = {'out': clean(out, d), 'code': p.returncode, 'trace': trace}
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
import json, sys
ex = json.load(open('ex.json', encoding='utf-8'))
fails = 0
try:
    ns = {'__name__': 'exercise'}
    exec(compile(ex['code'], 'exercise.py', 'exec'), ns)
    for t in ex['tests']:
        try:
            got = eval(t['call'], ns)
            same = json.dumps(got, sort_keys=True, default=repr) == json.dumps(t['want'], sort_keys=True, default=repr)
        except Exception as e:
            got, same = 'raised ' + type(e).__name__ + ': ' + str(e), False
        if not same:
            fails += 1
            print('FAIL', t['call'], 'gave', repr(got), 'wanted', repr(t['want']))
except Exception as e:
    fails = len(ex['tests'])
    print('ERROR', type(e).__name__, e)
print('fails=' + str(fails))
'''


def check_exercise(code, tests):
    spec = {'t': 'run', 'file': 'harness.py', 'code': EX_HARNESS, 'trace': False, 'extra': {'ex.json': json.dumps({'code': code, 'tests': tests})}}
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
        return '▶ Runs' if spec.get('expect', 'ok') == 'ok' else '💥 Raises an error'
    if spec['t'] == 'test':
        return '🧪 Run in a terminal' if spec.get('expect', 'pass') == 'pass' else '🧪 Run in a terminal, fails on purpose'
    return spec.get('note', 'Not run on this page')


def block(key, spec, res, traces):
    label = esc(spec.get('label', 'Example'))
    play = ''
    if spec['t'] == 'run' and spec.get('play', True):
        play = ' data-play="py"'
        if spec.get('stdin'):
            play += f' data-stdin="{esc(spec["stdin"])}"'
    btns = ''
    if key in traces:
        btns += '<button type="button" class="step">👣 Line by line</button>'
    if play:
        btns += '<button type="button" class="try">✏️ Edit and run</button>'
    bar = (f'<div class="codebar"><span class="dots"><i></i><i></i><i></i></span><span class="lbl">{label} · {badge(spec)}</span>'
           f'{btns}<button type="button" class="copy">Copy</button></div>')
    if spec['t'] == 'test':
        shown = spec.get('show') or list(spec['files'])
        body = ''
        for n in shown:
            body += f'<div class="fname">📄 {esc(n)}</div><pre class="src" data-file="{esc(n)}">{hl(spec["files"][n].strip(chr(10)), lang_of(n))}</pre>'
        cmd = spec.get('shown_cmd', spec['cmd'])
        body += f'<div class="cmd"><span>Terminal</span><pre>$ {esc(cmd)}</pre></div>'
        ok = (res['code'] == 0) == (spec.get('expect', 'pass') == 'pass')
        if not ok:
            raise SystemExit(f'{key}: the command ended with exit code {res["code"]}, expected {spec.get("expect", "pass")}\n{res["out"]}')
        cls = 'out' if res['code'] == 0 else 'err'
        body += f'<div class="{cls}"><span>Terminal output</span><pre>{esc(trim(res["out"], spec))}</pre></div>'
        return f'<div class="codewrap tests" data-k="{key}">{bar}{body}</div>'
    code = spec['code'].strip('\n')
    lang = spec.get('lang', 'py')
    body = ''
    if spec['t'] == 'run' and spec.get('extra'):
        for n, src in spec['extra'].items():
            body += f'<div class="fname">📄 {esc(n)}</div><pre class="src" data-file="{esc(n)}">{hl(src.strip(chr(10)), lang_of(n))}</pre>'
        body += f'<div class="fname">📄 {esc(spec.get("file", "main.py"))}</div>'
    body += f'<pre class="src main">{hl(code, lang)}</pre>'
    if spec['t'] == 'run' and (spec.get('extra') or spec.get('flags') or spec.get('args')):
        body += f'<div class="cmd"><span>Terminal</span><pre>$ {esc(" ".join(["python", *spec.get("flags", []), spec.get("file", "main.py"), *spec.get("args", [])]))}</pre></div>'
    if spec.get('stdin'):
        body += f'<div class="cmd stdin"><span>Typed at the keyboard</span><pre>{esc(spec["stdin"].rstrip())}</pre></div>'
    if spec['t'] == 'run':
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
    return {'py': 'py', 'json': 'json', 'yml': 'yaml', 'yaml': 'yaml', 'toml': 'toml', 'ini': 'toml', 'cfg': 'toml',
            'sh': 'bash', 'txt': 'txt', 'java': 'java'}.get(ext, 'py')


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
        yield 'quiz', ' '.join([q['q'], q['hint'], q['why'], *q['o']])
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
    for k, l in T.get('lanes', {}).items():
        yield 'lanes ' + k, ' '.join([l['t'], l.get('s', '')] + [s['m'] for s in l['steps']])
    for k, g in T.get('dg', {}).items():
        yield 'diagram ' + k, ' '.join([g.get('t', '')] + [s[1] for s in g.get('st', [])])


def topic_files():
    return sorted(f for f in os.listdir(os.path.join(HERE, 'topics')) if re.match(r'\d\d-.*\.py$', f))


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

    traces = {k: r['trace'] for k, r in res.items() if r.get('trace') and T['codes'][k].get('trace', True)}
    blocks = {k: block(k, s, res.get(k), traces) for k, s in T['codes'].items()}

    parts = T['parts']
    n_viz = sum(len(re.findall(r'data-viz="', p['html'])) for p in parts)
    n_run = sum(1 for s in T['codes'].values() if s['t'] == 'run')
    n_term = sum(1 for s in T['codes'].values() if s['t'] == 'test')
    n_qa = sum(1 for p in parts if p.get('qa'))
    chips = [f'⏱️ About {T["minutes"]} min read', f'📚 {len(parts)} parts', f'🎬 {n_viz} animations', f'▶ {n_run} runnable examples',
             f'👣 {len(traces)} line by line'] + ([f'🧪 {n_term} terminal run' + ('s' if n_term > 1 else '')] if n_term else []) + [
             f'🏋️ {len(T["ex"])} hands-on exercises', f'🎯 {len(T["quiz"])} quiz questions', f'🧮 {len(T["calc"])} calculations']
    if n_qa:
        chips.append(f'🧪 {n_qa} QA essential parts')
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
        lvl = f'<span class="lvl-tag lvl-{p["lvl"]}">{ {"b": "🌱 Beginner", "i": "🌿 Intermediate", "a": "🔥 Advanced", "x": "🧠 Expert"}[p["lvl"]] }</span>' if p.get('lvl') else ''
        secs.append(f'<section class="card reveal jsec{" qa-part" if qa else ""}" id="{p["id"]}" data-say="{p["id"]}"><div class="sec-num">Part {i}{lvl}</div>'
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
    page['lanes'] = {k: {**v, 'lang': v.get('lang', 'py')} for k, v in T.get('lanes', {}).items()}
    page['tr'] = traces
    mod = T['module']
    qa_box = f'<div class="qa-intro"><b>🧪 For QA engineers</b><p>{T["qa_intro"]}</p></div>' if T.get('qa_intro') else ''
    out = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(T["title"])} · Python</title>
<meta name="description" content="{esc(T["desc"])}">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Nunito:wght@500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/theme.css">
<link rel="stylesheet" href="../../assets/extras.css">
<link rel="stylesheet" href="../../assets/learn.css">
<link rel="stylesheet" href="../../assets/lesson.css">
<link rel="stylesheet" href="../../assets/viz.css">
<link rel="stylesheet" href="../../assets/jsplay.css">
<link rel="stylesheet" href="../../assets/pyplay.css">
</head>
<body>
<div class="wrap">
  <div class="crumb"><a class="home-link" href="../../subject.html?s={SUBJECT}" target="_top">🐍 Python</a><span>›</span><span>{mod[0]} {esc(mod[1])}</span><span>›</span><span>Chapter {idx + 1} of {len(chapters)}</span></div>
  <header class="hero" id="top" data-say="top">
    <div class="hero-row"><span class="em">{T["emoji"]}</span><div><h1>{esc(T["title"])}</h1><p class="lead">{T["lead"]}</p></div></div>
    <div class="chips">{chip_html}<span class="chip">🐍 Run with CPython {py_version()}</span><button type="button" class="listen-btn" id="listenAll">🎧 Listen in 6 languages</button></div>
    {qa_box}
  </header>
  <nav class="toc" aria-label="Parts of this chapter">{toc}{'<button type="button" class="qa-toggle" id="qaOnly" aria-pressed="false">🧪 Show the QA path only</button>' if n_qa else ''}</nav>
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
<script src="../../assets/pyviz.js"></script>
<script src="../../assets/pyplay.js"></script>
<script>
const PAGE = {js(page)};
PYPLAY.page({{ title: {js(T["title"])}, subject: {js(SUBJECT)}, tracer: {js(open(TRACER, encoding="utf-8").read())} }});
</script>
</body>
</html>
'''
    dest = os.path.join(OUT, T['slug'] + '.html')
    os.makedirs(OUT, exist_ok=True)
    open(dest, 'w', encoding='utf-8').write(out)
    print(f'{T["slug"]}: {len(parts)} parts, {n_viz} animations, {n_run} runnable, {len(traces)} recorded line by line, {n_term} terminal runs, '
          f'{len(T["ex"])} exercises, {len(out) // 1024} KB -> {os.path.relpath(dest, ROOT)}')


# ---------- the catalog block ----------
INLINE_TAGS = r'(?:code|b|i|em|strong|span|sup|sub|br)'


def inline(s):
    """Quiz and calc text is shown as HTML. Keep the few inline tags the topics use and escape every other <."""
    return re.sub(r'<(?!/?' + INLINE_TAGS + r'[\s>/])', '&lt;', s)


def catalog(chapters):
    mods = []
    for T in chapters:
        if not mods or mods[-1]['key'] != T['module']:
            mods.append({'key': T['module'], 'topics': []})
        mods[-1]['topics'].append(T)
    L = ['function pyModules() {', '  return [']
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
            L.append(f'      {{ id: {js(T["slug"])}, title: {js(T["title"])}, emoji: {js(T["emoji"])}, page: {js("content/python/" + T["slug"] + ".html")},')
            L.append(f'        summary: {js(T["summary"])},')
            L.append(f'        keywords: {js(T["keywords"])},')
            L.append(f'        added: {js(T.get("added", "2026-10-24"))},')
            L.append('        sections: [')
            L.append(',\n'.join(secs))
            L.append('      ] }' + (',' if ti + 1 < len(m['topics']) else ''))
        L.append('    ] }' + (',' if mi + 1 < len(mods) else ''))
    L.append('  ];')
    L.append('}')
    block_text = '\n'.join(L)
    path = os.path.join(ROOT, 'data', 'catalog.js')
    src = open(path, encoding='utf-8').read()
    start, end = '/* ===== py-build: Python chapters. Generated by tools/py-build/build.py, edit the topic files instead. ===== */', '/* ===== end of py-build ===== */'
    new = f'{start}\n{block_text}\n{end}'
    if start in src:
        src = re.sub(re.escape(start) + r'[\s\S]*?' + re.escape(end), lambda _: new, src)
    else:
        src = src.rstrip('\n') + '\n\n' + new + '\n'
    open(path, 'w', encoding='utf-8').write(src)
    print(f'catalog: {len(chapters)} chapters in {len(mods)} modules -> data/catalog.js')


def main():
    if not PY:
        raise SystemExit('CPython 3.14 was not found. Set PY_BUILD_PYTHON.')
    print('Python', py_version())
    chapters = all_topics()
    want = sys.argv[1:]
    for T in chapters:
        if not want or T['slug'] in want:
            build(T, chapters)
    catalog(chapters)


if __name__ == '__main__':
    main()
