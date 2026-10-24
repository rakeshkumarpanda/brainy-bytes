"""Build the newer Java chapter pages in content/java/ from the topic files in topics/.

Every example on a page is compiled and run on a real JDK when the page is built, and the real output is shown under it:
  java   a program compiled with javac and run with java. Programs marked for tracing are also run once under the
         Java debugger interface (tracer/Tracer.java), which records every line, variable change, call and print.
         The page replays that recording in the "Run line by line" viewer.
  sh     a small project run with a shell command such as javac, java, javap, jar or jshell.
  show   code that is shown but not run here. The label says so.

Quiz and number crunch questions marked run=True are run too, and the build stops if the printed output is not the
answer the page gives. The build also stops on an em dash, an en dash or a semicolon in reader facing prose.

The page frame (styles, comic, quiz, number crunch, narrator, diagrams) is the one the other Java chapters use, plus
assets/xv.js and assets/xv.css for the line by line viewer and assets/javaviz.js for the interactive animations.
The javaNewModules() block in data/catalog.js (between the java-build markers) is rewritten from the same topic files,
and the crumbs of the older Java chapters are updated to the new chapter count.

Usage:  python3 tools/java-build/build.py [slug ...]        (no slug builds every chapter)
Needs:  python3, JDK 25 (set JDK25_HOME) and JDK 27 (set JDK27_HOME). Both are free downloads from jdk.java.net or
        oracle.com/java. The JDBC chapter also downloads the H2 database jar from Maven Central once.
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
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'content', 'java')
CACHE = os.path.join(HERE, '.cache')
WORK = os.path.join(HERE, '.work')
LIB = os.path.join(HERE, '.lib')
JDKS = {25: os.environ.get('JDK25_HOME', ''), 27: os.environ.get('JDK27_HOME', '')}
RUN_STAMP = 3  # bump to rerun every example after changing how examples are run
LANGS = ['en', 'hi', 'kn', 'or', 'ar', 'de']
OLD_CHAPTERS = ['language-fundamentals', 'operators', 'flow-control', 'declarations-access-modifiers', 'oops-concepts', 'inner-classes',
                'java-lang', 'exception-handling', 'enum', 'regex', 'i18n', 'collections', 'generics', 'multithreading', 'file-io',
                'serialization', 'garbage-collection', 'assertions', 'development']
MAVEN = {'h2.jar': 'https://repo1.maven.org/maven2/com/h2database/h2/2.3.232/h2-2.3.232.jar'}
PRELUDE = 'import module java.base; '  # put on line 1 so line numbers stay the same as the code on the page


# ---------- syntax colouring, the same classes the other Java chapters use ----------
KW = set(('abstract assert boolean break byte case catch char class const continue default do double else enum extends final '
          'finally float for if implements import instanceof int interface long new package private protected public return '
          'short static super switch this throw throws try var void while true false null record sealed permits non-sealed '
          'yield when module exports requires opens uses provides transitive with to').split())


def hl(code, lang='java'):
    if lang != 'java':
        return JSB.hl(code, lang)
    tok = re.compile(r'(?P<c>//[^\n]*|/\*[\s\S]*?\*/)|(?P<s>"""[\s\S]*?"""|"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\')'
                     r'|(?P<n>\b\d[\d_]*(?:\.\d+)?(?:[eE][+-]?\d+)?[LlFfDd]?\b|\b0[xXbB][0-9a-fA-F_]+[Ll]?\b)'
                     r'|(?P<a>@[A-Za-z]+)|(?P<w>non-sealed|[A-Za-z_$][\w$]*)|(?P<o>[\s\S])')
    out = []
    for m in tok.finditer(code):
        kind, t = m.lastgroup, html.escape(m.group(), quote=False)
        if kind == 'w':
            w = m.group()
            if w in KW:
                out.append(f'<span class="k">{t}</span>')
            elif w[0].isupper():
                out.append(f'<span class="t">{t}</span>')
            else:
                out.append(t)
        elif kind == 'o':
            out.append(t)
        else:
            out.append(f'<span class="{kind}">{t}</span>')
    return ''.join(out)


def load_jsb():
    spec = importlib.util.spec_from_file_location('jsbuild', os.path.join(ROOT, 'tools', 'js-build', 'build.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


JSB = load_jsb()


# ---------- running the examples ----------
def jdk(v, tool):
    home = JDKS.get(v)
    if not home or not os.path.exists(os.path.join(home, 'bin', tool)):
        raise SystemExit(f'JDK {v} was not found. Set JDK{v}_HOME to its folder.')
    return os.path.join(home, 'bin', tool)


_versions = {}


def jdk_version(v):
    if v not in _versions:
        p = subprocess.run([jdk(v, 'java'), '-version'], capture_output=True, text=True, env=env(v))
        _versions[v] = p.stderr.strip().split('\n')[0]
    return _versions[v]


def env(v):
    e = {k: val for k, val in os.environ.items() if not k.startswith(('JAVA_TOOL_OPTIONS', 'JDK_JAVA_OPTIONS', '_JAVA_OPTIONS', 'CLAUDE', 'CCR_'))}
    e['PATH'] = os.pathsep.join([os.path.dirname(jdk(v, 'java')), e.get('PATH', '')])
    e['JAVA_HOME'] = JDKS[v]
    e.update({'TZ': 'UTC', 'LANG': 'en_US.UTF-8', 'LC_ALL': 'C.UTF-8'})
    return e


def lib(name):
    os.makedirs(LIB, exist_ok=True)
    p = os.path.join(LIB, name)
    if not os.path.exists(p):
        urllib.request.urlretrieve(MAVEN[name], p)
    return p


def write(d, files):
    for name, body in files.items():
        p = os.path.join(d, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(body.strip('\n') + '\n')


def is_unit(code):
    """A whole source file (it has a main method, imports or a package), not a snippet that needs a main around it."""
    return bool(re.search(r'\bvoid\s+main\s*\(', code) or re.match(r'\s*(import|package|@)\b', code))


def source(code):
    code = code.strip('\n')
    if not is_unit(code):
        code = 'void main() {\n' + code + '\n}'
    return code if code.lstrip().startswith('package') else PRELUDE + code


def compile_errors(text):
    """javac output to the short form the pages show: Line N: message, plus any detail lines."""
    lines = text.replace('\r\n', '\n').split('\n')
    out, i = [], 0
    while i < len(lines):
        m = re.match(r'(?:\S*/)?\w+\.java:(\d+): error: (.*)', lines[i])
        if m:
            block = [f'Line {m.group(1)}: {m.group(2)}']
            j2 = i + 1
            detail = []
            while j2 < len(lines) and not re.match(r'(?:\S*/)?\w+\.java:\d+: (?:error|warning)', lines[j2]) and not re.match(r'\d+ errors?$', lines[j2]):
                detail.append(lines[j2])
                j2 += 1
            # detail holds extra message lines, then the source line and a caret line, then maybe more lines
            caret = next((k for k, x in enumerate(detail) if re.match(r'^\s*\^\s*$', x)), None)
            keep = [x for k, x in enumerate(detail) if caret is None or (k != caret and k != caret - 1)]
            block += [x.strip() for x in keep if x.strip() and not x.startswith('Note:')]
            out.append('\n'.join(block))
            i = j2
        else:
            i += 1
    return '\n'.join(out)


def runtime_error(text):
    keep = []
    for ln in text.split('\n'):
        if ln.startswith('Exception in thread') or ln.startswith('Caused by:'):
            keep.append(ln)
    return '\n'.join(keep) or text.strip()


def clean(text, d):
    text = text.replace('\r\n', '\n')
    for p in {d, os.path.realpath(d)}:
        text = text.replace(p + '/', '').replace(p, 'project')
    text = re.sub(r'^Note: .*(preview|deprecat|unchecked|recompile).*\n', '', text, flags=re.M)
    text = re.sub(r'^Picked up .*\n', '', text, flags=re.M)
    return text.rstrip()


TRACER_DIRS = {}


def tracer(v):
    if v not in TRACER_DIRS:
        d = os.path.join(WORK, f'tracer{v}')
        os.makedirs(d, exist_ok=True)
        src = [os.path.join(HERE, 'tracer', f) for f in ('Tracer.java', 'Boot.java')]
        stamp = os.path.join(d, 'stamp')
        h = hashlib.sha256(b''.join(open(s, 'rb').read() for s in src)).hexdigest()
        if not os.path.exists(stamp) or open(stamp).read() != h:
            subprocess.run([jdk(v, 'javac'), '-d', d, *src], check=True, env=env(v))
            open(stamp, 'w').write(h)
        TRACER_DIRS[v] = d
    return TRACER_DIRS[v]


def run_spec(spec):
    """Run one example and return {'out', 'err', 'code', 'trace'}. Results are cached by content."""
    v = spec.get('jdk', 25)
    key = hashlib.sha256(json.dumps([spec, source(spec['code']) if 'code' in spec else '', jdk_version(v), RUN_STAMP, open(os.path.join(HERE, 'tracer', 'Tracer.java')).read()], sort_keys=True).encode()).hexdigest()[:24]
    cpath = os.path.join(CACHE, key + '.json')
    if os.path.exists(cpath):
        return json.load(open(cpath, encoding='utf-8'))
    os.makedirs(WORK, exist_ok=True)
    d = tempfile.mkdtemp(prefix='r', dir=WORK)
    try:
        if spec['t'] == 'java':
            res = run_java(spec, d, v)
        elif spec['t'] == 'sh':
            write(d, spec['files'])
            if 'h2.jar' in spec['cmd']:
                shutil.copy(lib('h2.jar'), os.path.join(d, 'h2.jar'))
            p = subprocess.run(spec['cmd'], cwd=d, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=300, env=env(v))
            res = {'out': clean(p.stdout, d), 'code': p.returncode}
        else:
            raise ValueError('unknown example type ' + spec['t'])
    finally:
        shutil.rmtree(d, ignore_errors=True)
    os.makedirs(CACHE, exist_ok=True)
    json.dump(res, open(cpath, 'w', encoding='utf-8'), ensure_ascii=False)
    return res


def run_java(spec, d, v):
    files = {'Main.java': source(spec['code'])}
    for n, c in spec.get('more', {}).items():
        files[n] = c if c.lstrip().startswith('package') else PRELUDE + c.strip('\n')
    write(d, files)
    pv = ['--enable-preview', '--release', str(v)] if spec.get('preview') else []
    cp = 'cls' + (os.pathsep + 'h2.jar' if spec.get('h2') else '')
    if spec.get('h2'):
        shutil.copy(lib('h2.jar'), os.path.join(d, 'h2.jar'))
    srcs = sorted(n for n in files if n.endswith('.java'))
    p = subprocess.run([jdk(v, 'javac'), '-g', '-encoding', 'UTF-8', '-cp', cp, '-d', 'cls', *pv, *srcs], cwd=d, capture_output=True, text=True, env=env(v), timeout=120)
    if p.returncode != 0:
        return {'out': '', 'err': compile_errors(clean(p.stdout + p.stderr, d)), 'code': 'compile'}
    run = [jdk(v, 'java'), '-cp', cp, *(['--enable-preview'] if spec.get('preview') else []), 'Main', *spec.get('args', [])]
    p = subprocess.run(run, cwd=d, capture_output=True, text=True, env=env(v), timeout=120, input=spec.get('stdin', ''))
    res = {'out': clean(p.stdout, d), 'err': runtime_error(clean(p.stderr, d)) if p.returncode else clean(p.stderr, d), 'code': p.returncode}
    if spec.get('trace'):
        tdir = tracer(v)
        extra = ['--enable-preview'] if spec.get('preview') else []
        cpt = os.pathsep.join([os.path.join(d, 'cls'), tdir] + ([os.path.join(d, 'h2.jar')] if spec.get('h2') else []))
        subprocess.run([jdk(v, 'java'), '-cp', tdir, 'Tracer', cpt, 'Main', os.path.join(d, 'trace.json'), str(spec.get('max_steps', 400)), *extra],
                       cwd=d, capture_output=True, text=True, env=env(v), timeout=180)
        if os.path.exists(os.path.join(d, 'trace.json')):
            t = json.load(open(os.path.join(d, 'trace.json'), encoding='utf-8'))
            if t['end'].get('o'):
                t['end']['o'] = runtime_error(t['end']['o']) if 'Exception in thread' in t['end']['o'] else t['end']['o']
            res['trace'] = t
    return res


# ---------- page parts ----------
def esc(s):
    return html.escape(str(s))


def js(v):
    return json.dumps(v, ensure_ascii=False).replace('</', '<\\/')


def trim(out, spec):
    for a, b in spec.get('replace', []):
        out = re.sub(a, b, out)
    if spec.get('tail'):
        out = '\n'.join(out.split('\n')[-spec['tail']:])
    return out


def jdk_tag(spec):
    v = spec.get('jdk', 25)
    return f'☕ JDK {v}' + (' preview' if spec.get('preview') else '')


def block(key, spec, res, traces):
    label = esc(spec.get('label', 'Example'))
    if spec['t'] == 'show':
        bar = (f'<div class="codebar"><span class="dots"><i></i><i></i><i></i></span><span class="lbl">{label} · {esc(spec.get("note") or "Not run on this page")}</span>'
               '<button type="button" class="copy">Copy</button></div>')
        body = f'<pre class="src">{hl(spec["code"].strip(chr(10)), spec.get("lang", "java"))}</pre>'
        if spec.get('result'):
            body += f'<div class="note-out"><span>What happens</span><p>{spec["result"]}</p></div>'
        return f'<div class="codewrap" data-k="{key}">{bar}{body}</div>'
    if spec['t'] == 'sh':
        ok = (res['code'] == 0) == (spec.get('expect', 'ok') == 'ok')
        if not ok:
            raise SystemExit(f'{key}: command ended with exit code {res["code"]}, expected {spec.get("expect")}\n{res["out"]}')
        bar = (f'<div class="codebar"><span class="dots"><i></i><i></i><i></i></span><span class="lbl">{label} · 🖥️ Run in a terminal · {jdk_tag(spec)}</span>'
               '<button type="button" class="copy">Copy</button></div>')
        body = ''
        for n in (spec.get('keep') if spec.get('keep') is not None else list(spec['files'])):
            body += f'<div class="fname">📄 {esc(n)}</div><pre class="src" data-file="{esc(n)}">{hl(spec["files"][n].strip(chr(10)), lang_of(n))}</pre>'
        body += f'<div class="cmd"><span>Terminal</span><pre>{esc(spec["shown"])}</pre></div>'
        body += f'<div class="{"out" if res["code"] == 0 else "err"}"><span>Terminal output</span><pre>{esc(trim(res["out"], spec))}</pre></div>'
        return f'<div class="codewrap tests" data-k="{key}">{bar}{body}</div>'

    want = spec.get('expect', 'ok')
    got = 'compile' if res['code'] == 'compile' else ('ok' if res['code'] == 0 else 'throw')
    if got != want:
        raise SystemExit(f'{key}: expected {want} but the program gave {got}\n{res.get("err", "")}\n{res.get("out", "")}')
    badge = {'ok': '▶ Runs', 'throw': '💥 Crashes at run time', 'compile': '❌ Does not compile'}[want]
    trace_btn = ''
    if res.get('trace') and want != 'compile':
        traces[key] = res['trace']
        trace_btn = '<button type="button" class="try xv-try" aria-pressed="false">👣 Run line by line</button>'
    bar = (f'<div class="codebar"><span class="dots"><i></i><i></i><i></i></span><span class="lbl">{label} · {badge} · {jdk_tag(spec)}</span>'
           f'{trace_btn}<button type="button" class="copy">Copy</button></div>')
    body = ''
    for n, src in spec.get('more', {}).items():
        body += f'<div class="fname">📄 {esc(n)}</div><pre class="src" data-file="{esc(n)}">{hl(src.strip(chr(10)))}</pre>'
    if spec.get('more'):
        body += '<div class="fname">📄 Main.java</div>'
    body += f'<pre class="src main">{hl(spec["code"].strip(chr(10)))}</pre>'
    if spec.get('args') or spec.get('preview'):
        cmd = 'java ' + ('--enable-preview ' if spec.get('preview') else '') + 'Main.java' + ''.join(' ' + a for a in spec.get('args', []))
        body += f'<div class="cmd"><span>Terminal</span><pre>$ {esc(cmd)}</pre></div>'
    out = trim(res.get('out', ''), spec)
    if want == 'compile':
        body += f'<div class="err"><span>❌ Compile error</span><pre>{esc(res["err"])}</pre></div>'
    elif want == 'throw':
        if out:
            body += f'<div class="out"><span>Output before the crash</span><pre>{esc(out)}</pre></div>'
        body += f'<div class="err"><span>💥 Runtime error</span><pre>{esc(res["err"])}</pre></div>'
    else:
        body += f'<div class="out"><span>Output</span><pre>{esc(out)}</pre></div>' if out else '<div class="out"><span>Output</span><pre class="none">(prints nothing)</pre></div>'
    if spec.get('note'):
        body += f'<div class="note-out"><span>Why</span><p>{spec["note"]}</p></div>'
    return f'<div class="codewrap" data-k="{key}"{" data-trace=\"" + key + "\"" if trace_btn else ""}>{bar}{body}</div>'


def lang_of(name):
    ext = name.rsplit('.', 1)[-1]
    return {'java': 'java', 'json': 'json', 'xml': 'html', 'html': 'html', 'yml': 'yaml', 'yaml': 'yaml', 'sh': 'bash', 'sql': 'bash', 'txt': 'bash',
            'properties': 'bash', 'MF': 'bash', 'jsh': 'java'}.get(ext, 'bash')


def load_topic(path):
    sys.path.insert(0, HERE)
    spec = importlib.util.spec_from_file_location('jtopic_' + re.sub(r'\W', '_', os.path.basename(path)[:-3]), path)
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
    says = {'top'} | {p['id'] for p in T['parts']}
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
    ids = [p['id'] for p in T['parts']]
    if len(ids) != len(set(ids)):
        errs.append('duplicate part id')
    for k in list(T.get('dg', {})) + list(T.get('lanes', {})):
        if not any(f'data-k="{k}"' in p['html'] for p in T['parts']):
            errs.append(f'animation {k} is never shown')
    for where, t in prose_pieces(T):
        bare = re.sub(r'<pre[\s\S]*?</pre>|<code>[\s\S]*?</code>|<span class="eq">[\s\S]*?</span>|\[\[[\w-]+\]\]|&#?\w+;', ' ', t)
        for bad, name in (('—', 'an em dash'), ('–', 'an en dash'), (';', 'a semicolon')):
            if bad in bare:
                i = bare.index(bad)
                errs.append(f'{name} in {where}: ...{bare[max(0, i - 50):i + 20].strip()}...')
    return errs


def prose_pieces(T):
    yield 'lead', T['lead']
    for k in ('summary', 'desc', 'title'):
        yield k, T.get(k, '')
    for p in T['parts']:
        yield 'part ' + p['id'], p['html'] + ' ' + p['title']
    for q in T['quiz']:
        yield 'quiz', ' '.join([q['q'], q['hint'], q['why'], *q['o']]) if not q.get('code') else ' '.join([q['q'], q['hint'], q['why']])
    for c in T['calc']:
        yield 'calc', ' '.join([c['q'], c['hint'], *c['steps']])
    for s in T['say']:
        yield 'narration ' + s['id'], ' '.join(s[l] for l in LANGS)
    for pn in T['info']['panels']:
        yield 'comic', ' '.join([pn['h'], pn['t'], pn['more']])
    yield 'comic', T['info']['title'] + ' ' + T['info']['remember']
    for r in T['real']:
        yield 'real life', ' '.join(r[1:])
    for spec in T['codes'].values():
        for k in ('result', 'note'):
            if spec.get(k):
                yield 'note', spec[k]


def check_questions(T):
    """Run every quiz and calc question marked run=True and compare what it prints with the answer on the page."""
    jobs = []
    for q in T['quiz']:
        if q.get('run'):
            jobs.append(('quiz', q, {'t': 'java', 'code': q['code'], 'jdk': q.get('_jdk', 25), 'preview': q.get('_preview', False)}, JSB.strip_tags(q['o'][q['a']])))
    for c in T['calc']:
        if c.get('run'):
            jobs.append(('calc', c, {'t': 'java', 'code': c['code'], 'jdk': 25}, c['ans']))
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(lambda x: run_spec(x[2]), jobs))
    for (kind, q, _, want), r in zip(jobs, res):
        if want == 'Compile error' or want == 'Does not compile':
            if r['code'] != 'compile':
                raise SystemExit(f'{T["slug"]}: {kind} "{q["q"][:60]}" compiles, but the answer says it does not')
            continue
        got = r['out'].strip() if r['code'] == 0 else ('Compile error: ' + r['err'] if r['code'] == 'compile' else r['err'])
        if got != want.strip():
            raise SystemExit(f'{T["slug"]}: {kind} "{q["q"][:70]}" prints\n{got}\nbut the answer on the page is\n{want}')
    for q in T['quiz']:
        q.pop('_jdk', None)
        q.pop('_preview', None)


def topic_files():
    return sorted(f for f in os.listdir(os.path.join(HERE, 'topics')) if re.match(r'\d\d[a-z]?-.*\.py$', f))


def all_topics():
    return [load_topic(os.path.join(HERE, 'topics', f)) for f in topic_files()]


def total_chapters(chapters):
    return len(OLD_CHAPTERS) + len(chapters)


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
    check_questions(T)
    traces = {}
    blocks = {k: block(k, s, res.get(k), traces) for k, s in T['codes'].items()}

    parts = T['parts']
    n_viz = sum(len(re.findall(r'data-viz="', p['html'])) for p in parts)
    n_run = sum(1 for s in T['codes'].values() if s['t'] in ('java', 'sh'))
    chips = [f'⏱️ About {T["minutes"]} min read', f'📚 {len(parts)} parts', f'🎬 {n_viz} animations', f'▶ {n_run} examples run on a real JDK',
             f'👣 {len(traces)} line by line replays', f'🎯 {len(T["quiz"])} quiz questions', f'🧮 {len(T["calc"])} calculations']
    chip_html = ''.join(f'<span class="chip">{c}</span>' for c in chips)
    toc = ''.join(f'<a href="#{p["id"]}"><span>{p["emoji"]}</span>{esc(p["title"])}</a>' for p in parts)
    toc += ('<a class="spec" href="#comic">🖼️ Comic</a><a class="spec" href="#real-life">🌍 Real life</a>'
            '<a class="spec" href="#quiz">🎯 Quiz</a><a class="spec" href="#numbers">🧮 Number crunch</a>')
    secs = []
    for i, p in enumerate(parts, 1):
        body = re.sub(r'\[\[([\w-]+)\]\]', lambda m: blocks[m.group(1)], p['html'].strip())
        secs.append(f'<section class="card reveal jsec" id="{p["id"]}" data-say="{p["id"]}"><div class="sec-num">Part {i}</div>'
                    f'<h2><span class="sec-em">{p["emoji"]}</span><span>{esc(p["title"])}</span></h2>\n{body}\n</section>\n')

    order = [{'slug': s, 'emoji': e, 'short': t} for s, e, t in old_meta()] + chapters
    idx = [c['slug'] for c in order].index(T['slug'])
    pv = order[idx - 1] if idx else None
    nx = order[idx + 1] if idx + 1 < len(order) else None
    a = (f'<a class="prev" href="./{pv["slug"]}.html" data-topic="{pv["slug"]}"><small>← Previous chapter</small><b>{pv["emoji"]} {esc(pv["short"])}</b></a>' if pv else '<span></span>')
    b = (f'<a class="next" href="./{nx["slug"]}.html" data-topic="{nx["slug"]}"><small>Next chapter →</small><b>{nx["emoji"]} {esc(nx["short"])}</b></a>' if nx else '<span></span>')

    page = {k: T[k] for k in ['info', 'real', 'quiz', 'calc', 'say']}
    page['quiz'] = [{**q, 'q': JSB.inline(q['q']), 'o': [JSB.inline(o) for o in q['o']], 'hint': JSB.inline(q['hint']), 'why': JSB.inline(q['why'])} for q in T['quiz']]
    page['calc'] = [{**c, 'q': JSB.inline(c['q']), 'hint': JSB.inline(c['hint']), 'steps': [JSB.inline(x) for x in c['steps']]} for c in T['calc']]
    page['dg'] = T.get('dg', {})
    page['lanes'] = T.get('lanes', {})
    page['jv'] = T.get('jv', {})
    mod = T['module']
    out = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(T["title"])} · Java</title>
<meta name="description" content="{esc(T["desc"])}">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Nunito:wght@500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/theme.css">
<link rel="stylesheet" href="../../assets/extras.css">
<link rel="stylesheet" href="../../assets/learn.css">
<link rel="stylesheet" href="../../assets/lesson.css">
<link rel="stylesheet" href="../../assets/viz.css">
<link rel="stylesheet" href="../../assets/jsplay.css">
<link rel="stylesheet" href="../../assets/xv.css">
</head>
<body>
<div class="wrap">
  <div class="crumb"><a class="home-link" href="../../subject.html?s=java" target="_top">☕ Java</a><span>›</span><span>{mod[0]} {esc(mod[1])}</span><span>›</span><span>Chapter {idx + 1} of {len(order)}</span></div>
  <header class="hero" id="top" data-say="top">
    <div class="hero-row"><span class="em">{T["emoji"]}</span><div><h1>{esc(T["title"])}</h1><p class="lead">{T["lead"]}</p></div></div>
    <div class="chips">{chip_html}<button type="button" class="listen-btn" id="listenAll">🎧 Listen in 6 languages</button></div>
    <div class="jdk-note">Every example below was compiled and run on {esc(jdk_version(25))}{" and " + esc(jdk_version(27)) if any(s.get("jdk") == 27 for s in T["codes"].values()) else ""} when this page was built, so each output is real. Press <b>👣 Run line by line</b> on an example to replay that run one line at a time.</div>
  </header>
  <nav class="toc" aria-label="Parts of this chapter">{toc}</nav>
  <section class="card reveal" id="comic"></section>

{"".join(secs)}
  <section class="card reveal" id="real-life"></section>
  <section class="card reveal" id="quiz"></section>
  <section class="card reveal" id="numbers"></section>
  <nav class="pager">{a}{b}</nav>
</div>
<script type="application/json" id="traces">{js(traces)}</script>
<script src="../../assets/fun.js"></script>
<script src="../../assets/extras.js"></script>
<script src="../../assets/learn.js"></script>
<script src="../../assets/voice.js"></script>
<script src="../../assets/viz.js"></script>
<script src="../../assets/jsviz.js"></script>
<script src="../../assets/javaviz.js"></script>
<script src="../../assets/xv.js"></script>
<script>
const PAGE = {js(page)};
JAVAPAGE.start({{ title: {js(T["title"])} }});
</script>
</body>
</html>
'''
    dest = os.path.join(OUT, T['slug'] + '.html')
    open(dest, 'w', encoding='utf-8').write(out)
    print(f'{T["slug"]}: {len(parts)} parts, {n_viz} animations, {n_run} run, {len(traces)} traced, {len(out) // 1024} KB -> {os.path.relpath(dest, ROOT)}')


def old_meta():
    """slug, emoji and short title of the older hand made chapters, read from their pages."""
    meta = []
    for s in OLD_CHAPTERS:
        src = open(os.path.join(OUT, s + '.html'), encoding='utf-8').read()
        em = re.search(r'<span class="em">([^<]+)</span>', src).group(1)
        t = html.unescape(re.search(r'<h1>([^<]+)</h1>', src).group(1))
        meta.append((s, em, t))
    return meta


def patch_old(chapters):
    """Keep the crumbs of the older chapters in step with the chapter count, and link the last one to the first new one."""
    n = total_chapters(chapters)
    for i, s in enumerate(OLD_CHAPTERS):
        p = os.path.join(OUT, s + '.html')
        src = open(p, encoding='utf-8').read()
        new = re.sub(r'(<span>Chapter \d+ of )\d+(</span>)', lambda m: f'{m.group(1)}{n}{m.group(2)}', src, count=1)
        if i == len(OLD_CHAPTERS) - 1 and chapters:
            c = chapters[0]
            link = f'<a class="next" href="./{c["slug"]}.html" data-topic="{c["slug"]}"><small>Next chapter →</small><b>{c["emoji"]} {esc(c["short"])}</b></a>'
            new = re.sub(r'(<nav class="pager">[\s\S]*?</a>)(<span></span>|<a class="next"[\s\S]*?</a>)(</nav>)', lambda m: m.group(1) + link + m.group(3), new, count=1)
        if new != src:
            open(p, 'w', encoding='utf-8').write(new)


# ---------- the catalog block ----------
def catalog(chapters):
    mods = []
    for T in chapters:
        if not mods or mods[-1]['key'] != T['module']:
            mods.append({'key': T['module'], 'topics': []})
        mods[-1]['topics'].append(T)
    L = ['function javaNewModules() {', '  return [']
    n0 = len(OLD_CHAPTERS)
    num = {T['slug']: n0 + i + 1 for i, T in enumerate(chapters)}
    for mi, m in enumerate(mods):
        em, title, mid, blurb = m['key']
        L.append(f'    {{ id: {js(mid)}, title: {js(title)}, emoji: {js(em)}, blurb: {js(blurb)}, topics: [')
        for ti, T in enumerate(m['topics']):
            secs = [f'        {{ id: {js(p["id"])}, title: {js(p["title"])}, emoji: {js(p["emoji"])}, group: {js("Chapter " + str(num[T["slug"]]))}, keywords: {js(p.get("kw", []))} }}' for p in T['parts']]
            secs.append("        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' }")
            secs.append("        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }")
            L.append(f'      {{ id: {js(T["slug"])}, title: {js(T["title"])}, emoji: {js(T["emoji"])}, page: {js("content/java/" + T["slug"] + ".html")},')
            L.append(f'        summary: {js(T["summary"])},')
            L.append(f'        keywords: {js(T["keywords"])},')
            L.append(f'        added: {js(T.get("added", "2026-10-24"))},')
            L.append('        sections: [')
            L.append(',\n'.join(secs))
            L.append('      ] }' + (',' if ti + 1 < len(m['topics']) else ''))
        L.append('    ] }' + (',' if mi + 1 < len(mods) else ''))
    L.append('  ];')
    L.append('}')
    text = '\n'.join(L)
    path = os.path.join(ROOT, 'data', 'catalog.js')
    src = open(path, encoding='utf-8').read()
    start, end = '/* ===== java-build: newer Java chapters. Generated by tools/java-build/build.py, edit the topic files instead. ===== */', '/* ===== end of java-build ===== */'
    new = f'{start}\n{text}\n{end}'
    if start in src:
        src = re.sub(re.escape(start) + r'[\s\S]*?' + re.escape(end), lambda _: new, src)
    else:
        src = src.rstrip('\n') + '\n\n' + new + '\n'
    hook_old, hook_new = "concat(javaModules(), iqModule('java'))", "concat(javaModules(), javaNewModules(), iqModule('java'))"
    if hook_new not in src:
        if hook_old not in src:
            raise SystemExit('Could not find where the Java subject lists its modules in data/catalog.js')
        src = src.replace(hook_old, hook_new)
    open(path, 'w', encoding='utf-8').write(src)
    print(f'catalog: {len(chapters)} new Java chapters in {len(mods)} modules -> data/catalog.js')


def main():
    print(jdk_version(25), '|', jdk_version(27))
    chapters = all_topics()
    want = sys.argv[1:]
    for T in chapters:
        if not want or T['slug'] in want:
            build(T, chapters)
    patch_old(chapters)
    catalog(chapters)


if __name__ == '__main__':
    main()
