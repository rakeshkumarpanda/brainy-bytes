"""Build the Playwright chapter pages in content/playwright/ from the topic files in topics/.

Most examples are shown in four languages: Java, Python, JavaScript and TypeScript. Every language version is a
small real project that runs against Brainy Shop (app/server.mjs) when the page is built, and the real terminal
output is shown under it:
  java   a Maven project with Playwright for Java and JUnit 5 or TestNG, run with  mvn test
  py     a pytest project with pytest-playwright, run with  pytest -v  (or a plain script with python)
  js     a Playwright Test project, run with  npx playwright test
  ts     the same in TypeScript. tsc checks the types first, then Playwright Test runs it

Walks (walk() in pkit.py) run a script line by line in Chromium and save a screenshot after every line.
The page shows the line in the reader's language next to the screenshot. The Python and Java versions of every
walk are run too, so a walk can only reach the page when all of its languages work.

The page frame (styles, quiz, number crunch, narrator, comic, diagrams) is the one the JavaScript chapters use,
plus assets/pw.css, assets/pwviz.js (Playwright animations and the language switch) and assets/pwplay.js
(the Playwright playground that runs a test line by line in the reader's browser).

Usage:  python3 tools/pw-build/build.py [slug ...]          (no slug builds every chapter)
Needs:  Node.js 22 or later, Python 3.10 or later, JDK 21 and Maven, Chromium for Playwright 1.63
        (PLAYWRIGHT_BROWSERS_PATH, /opt/pw-browsers by default), and the one time set up in README.md.
"""
import concurrent.futures as cf
import hashlib
import html
import importlib.util
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'content', 'playwright')
CACHE = os.path.join(HERE, '.cache')
BOX = os.path.join(HERE, 'box')
RUNS = os.path.join(BOX, 'runs')
APP = os.path.join(HERE, 'app')
SUBJECT = 'playwright'
SUBJECT_TITLE = 'Playwright'
SUBJECT_EMOJI = '🎭'
NODE = os.environ.get('PW_BUILD_NODE') or shutil.which('node')
PYBIN = os.path.join(BOX, '.venv', 'bin')
BROWSERS = os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '/opt/pw-browsers')
RUN_STAMP = 2  # bump to rerun every example after changing how examples are run
LANGS = ['en', 'hi', 'kn', 'or', 'ar', 'de']
L4 = {'java': ('☕', 'Java'), 'py': ('🐍', 'Python'), 'js': ('🟨', 'JavaScript'), 'ts': ('🔷', 'TypeScript')}
JAVA_SLOTS = threading.Semaphore(2)

# The JavaScript builder is loaded as a library for syntax colouring, quiz text clean up and the shared checks.
_spec = importlib.util.spec_from_file_location('jsbuild', os.path.join(ROOT, 'tools', 'js-build', 'build.py'))
jsb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(jsb)
jsb.KW['bash'] |= {'pip', 'pip3', 'python', 'python3', 'pytest', 'mvn', 'java', 'playwright', 'allure', 'docker', 'echo', 'ls', 'cat',
                   'source', 'set', 'run', 'install', 'test', 'show-report', 'codegen'}
jsb.KW['cs'] = set(('abstract as async await base bool break case catch class const continue decimal default do double else enum false '
                    'finally float for foreach if in int interface internal is lock namespace new null object out override private '
                    'protected public readonly return sealed static string struct switch this throw true try typeof using var virtual void '
                    'while record').split())


def esc(s):
    return html.escape(str(s))


def hl(code, lang):
    if lang in ('xml', 'html'):
        return jsb.hl_html(code)
    if lang == 'text':
        return html.escape(code, quote=False)
    if lang in ('ini', 'properties', 'toml', 'env'):
        out = []
        for ln in code.split('\n'):
            e = html.escape(ln, quote=False)
            if ln.strip().startswith(('#', ';')):
                out.append(f'<span class="c">{e}</span>')
            elif ln.strip().startswith('['):
                out.append(f'<span class="k">{e}</span>')
            elif '=' in ln:
                k, v = ln.split('=', 1)
                out.append(f'<span class="a">{html.escape(k, quote=False)}</span>=<span class="s">{html.escape(v, quote=False)}</span>')
            else:
                out.append(e)
        return '\n'.join(out)
    if lang == 'yaml':
        return '\n'.join(
            (f'<span class="c">{html.escape(ln, quote=False)}</span>' if ln.strip().startswith('#') else
             re.sub(r'^(\s*-?\s*)([\w./-]+)(:)(.*)$', lambda m: html.escape(m.group(1)) + f'<span class="a">{html.escape(m.group(2))}</span>:'
                    + (f'<span class="s">{html.escape(m.group(4), quote=False)}</span>' if m.group(4).strip() else ''), ln)
             if re.match(r'^\s*-?\s*[\w./-]+:', ln) else html.escape(ln, quote=False)) for ln in code.split('\n'))
    if lang == 'tree':
        return '\n'.join(re.sub(r'^([│├└─\s]*)(.*?)(\s+#.*)?$', lambda m: html.escape(m.group(1)) + (
            f'<span class="k">{html.escape(m.group(2))}</span>' if m.group(2).endswith('/') else html.escape(m.group(2)))
            + (f'<span class="c">{html.escape(m.group(3))}</span>' if m.group(3) else ''), ln) for ln in code.split('\n'))
    return jsb.hl(code, lang)


def lang_of(name, fallback='text'):
    base = name.rsplit('/', 1)[-1]
    ext = base.rsplit('.', 1)[-1] if '.' in base else ''
    if base in ('Dockerfile', 'Jenkinsfile'):
        return 'bash' if base == 'Dockerfile' else 'java'
    if base.startswith('.env'):
        return 'env'
    return {'js': 'js', 'mjs': 'js', 'cjs': 'js', 'ts': 'ts', 'json': 'json', 'html': 'html', 'xml': 'xml', 'yml': 'yaml', 'yaml': 'yaml',
            'java': 'java', 'py': 'py', 'sh': 'bash', 'ini': 'ini', 'cfg': 'ini', 'toml': 'toml', 'properties': 'properties', 'cs': 'cs',
            'txt': 'text', 'md': 'text', 'csv': 'text', 'gradle': 'java', 'kts': 'java', 'feature': 'text'}.get(ext, fallback)


# ---------- running the examples ----------
ANSI = re.compile(r'\x1b\[[0-9;?]*[A-Za-z]')


def app_hash():
    h = hashlib.sha256()
    for d, _, fs in sorted(os.walk(APP)):
        for f in sorted(fs):
            h.update(f.encode())
            h.update(open(os.path.join(d, f), 'rb').read())
    return h.hexdigest()[:12]


_APPH = None


def free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]
    s.close()
    return p


def env(port):
    e = {k: v for k, v in os.environ.items() if not re.match(r'(CLAUDE|AI_AGENT|CCR_|CURSOR|CODEX|GITHUB_ACTIONS|GITLAB|BUILDKITE|TF_BUILD|CI$)', k)}
    e['PATH'] = os.pathsep.join([os.path.join(BOX, 'node_modules', '.bin'), PYBIN, os.path.dirname(NODE), e.get('PATH', '')])
    e['JAVA_TOOL_OPTIONS'] = (e.get('JAVA_TOOL_OPTIONS', '') + ' -Dstdout.encoding=UTF-8 -Dstderr.encoding=UTF-8 -Dfile.encoding=UTF-8').strip()
    e.pop('NO_COLOR', None)
    e.update({'FORCE_COLOR': '0', 'TZ': 'UTC', 'LANG': 'en_US.UTF-8', 'PLAYWRIGHT_BROWSERS_PATH': BROWSERS,
              'PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD': '1', 'PW_TEST_HTML_REPORT_OPEN': 'never', 'SHOP_PORT': str(port),
              'NODE_PATH': os.path.join(BOX, 'node_modules')})
    e.pop('NODE_OPTIONS', None)
    return e


def start_app(port):
    p = subprocess.Popen([NODE, os.path.join(APP, 'server.mjs')], env={**os.environ, 'PORT': str(port)},
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    p.stdout.readline()
    return p


def clean(text, d, port, lang):
    text = ANSI.sub('', text).replace('\r\n', '\n')
    real = os.path.realpath(d)
    for pth in sorted({d, real}, key=len, reverse=True):
        text = text.replace('file://' + pth + '/', '').replace(pth + '/', '').replace(pth, 'project')
    text = text.replace(f'localhost:{port}', 'localhost:4173').replace(f'127.0.0.1:{port}', '127.0.0.1:4173')
    text = re.sub(r'Picked up JAVA_TOOL_OPTIONS:.*\n', '', text)
    text = text.replace(BOX + '/node_modules/', 'node_modules/').replace(PYBIN, '.venv/bin')
    lines = text.split('\n')
    if lang == 'py' and any(ln.startswith('collect') for ln in lines):
        lines = [ln for ln in lines if not re.match(r'(platform |cachedir|rootdir|configfile|plugins|base_url|=+ test session starts)', ln)]
    if lang == 'java':
        keep, on = [], False
        for ln in lines:
            if 'T E S T S' in ln:
                on = True
                if keep and keep[-1].endswith('---'):
                    pass
            if on:
                keep.append(ln)
            if on and re.search(r'BUILD (SUCCESS|FAILURE)', ln):
                break
        if keep:
            lines = ['[INFO] -------------------------------------------------------'] + keep
        lines = [ln for ln in lines if not re.search(r'\[ERROR\] (To see the full|Re-run Maven|For more information|$)|\[ERROR\] -> \[Help', ln)]
    lines = [ln for ln in lines if not re.match(r'\s+at .*node_modules|metadata: \{|\(node:\d+\) Warning|\(Use `node --trace-warnings', ln)]
    return '\n'.join(lines).strip('\n')


def write(d, files, port):
    for name, body in files.items():
        p = os.path.join(d, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(body.replace('localhost:4173', f'localhost:{port}').strip('\n') + '\n')


def run_lang(spec, key=''):
    """Run one language version of an example. The result is cached by its content."""
    global _APPH
    if _APPH is None:
        _APPH = app_hash()
    ck = hashlib.sha256(json.dumps([spec['files'], spec['cmd'], _APPH, RUN_STAMP], sort_keys=True).encode()).hexdigest()[:24]
    cpath = os.path.join(CACHE, ck + '.json')
    if os.path.exists(cpath):
        return json.load(open(cpath, encoding='utf-8'))
    os.makedirs(RUNS, exist_ok=True)
    d = tempfile.mkdtemp(prefix='r', dir=RUNS)
    port = free_port()
    srv = start_app(port)
    slot = JAVA_SLOTS if spec['lang'] == 'java' else None
    try:
        write(d, spec['files'], port)
        cmd = spec['cmd'].replace('localhost:4173', f'localhost:{port}')
        if spec['lang'] == 'java':
            cmd = re.sub(r'^mvn ', 'mvn -o -B -Dstyle.color=never ', cmd)
        if slot:
            slot.acquire()
        t0 = time.time()
        try:
            p = subprocess.run(cmd, cwd=d, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=600, env=env(port))
        finally:
            if slot:
                slot.release()
        res = {'out': clean(p.stdout, d, port, spec['lang']), 'code': p.returncode, 'secs': round(time.time() - t0, 1)}
        if spec.get('collect'):
            res['files'] = {}
            for rel in spec['collect']:
                fp = os.path.join(d, rel)
                if os.path.exists(fp):
                    res['files'][rel] = open(fp, encoding='utf-8', errors='replace').read()
        if spec.get('after'):
            spec['after'](d, port, res)
    finally:
        srv.kill()
        if not os.environ.get('PW_KEEP_RUNS'):
            shutil.rmtree(d, ignore_errors=True)
    os.makedirs(CACHE, exist_ok=True)
    json.dump(res, open(cpath, 'w', encoding='utf-8'), ensure_ascii=False)
    return res


# ---------- blocks on the page ----------
def badge(spec, res):
    if spec.get('shown'):
        return '📄 ' + (spec.get('note') or 'Shown, not run here')
    want_fail = spec.get('expect') == 'fail'
    lab = {'java': 'mvn test ran', 'py': 'pytest ran', 'js': 'Playwright Test ran', 'ts': 'tsc checked, Playwright Test ran'}[spec['lang']]
    if not spec['cmd'].startswith(('mvn test', 'pytest', 'npx playwright test', 'npx tsc -p . && npx playwright test')):
        lab = 'ran for real'
    return ('💥 ' + lab + ', fails on purpose') if want_fail else ('✅ ' + lab)


def trim(out, spec):
    for a, b in spec.get('replace', []):
        out = re.sub(a, b, out)
    if spec.get('tail'):
        out = '\n'.join(out.split('\n')[-spec['tail']:])
    return out


def lang_body(key, lg, spec, res):
    body = ''
    for n in spec['show']:
        src = spec['files'][n].strip('\n')
        if n:
            body += f'<div class="fname">📄 {esc(n)}</div>'
        body += f'<pre class="src" data-file="{esc(n)}">{hl(src, lang_of(n, lg if lg != "py" else "py"))}</pre>'
    if spec.get('shown_cmd'):
        body += f'<div class="cmd"><span>Terminal</span><pre>$ {esc(spec["shown_cmd"])}</pre></div>'
    if spec.get('shown'):
        if spec.get('result'):
            body += f'<div class="note-out"><span>What happens</span><p>{spec["result"]}</p></div>'
        return body
    ok = (res['code'] == 0) == (spec.get('expect', 'pass') == 'pass')
    if not ok:
        raise SystemExit(f'{key} [{lg}]: the run ended with exit code {res["code"]}, expected {spec.get("expect", "pass")}\n{res["out"][-6000:]}')
    cls = 'out' if res['code'] == 0 else 'err'
    body += f'<div class="{cls}"><span>Terminal output</span><pre>{esc(trim(res["out"], spec))}</pre></div>'
    return body


def four_block(key, ex, results):
    langs = ex['langs']
    tabs = ''.join(f'<button type="button" class="pw-tab" data-l="{lg}" role="tab">{L4[lg][0]} {L4[lg][1]}</button>' for lg in langs)
    panes = ''.join(f'<div class="pw-pane" data-l="{lg}" data-badge="{esc(badge(sp, results.get((key, lg))))}">{lang_body(key, lg, sp, results.get((key, lg)))}</div>'
                    for lg, sp in langs.items())
    first = next(iter(langs.values()))
    bar = (f'<div class="codebar"><span class="dots"><i></i><i></i><i></i></span><span class="lbl">{esc(ex["label"])} · <b class="pw-badge">{esc(badge(first, results.get((key, next(iter(langs))))))}</b></span>'
           f'<button type="button" class="copy">Copy</button></div>')
    tabrow = f'<div class="pw-tabs" role="tablist">{tabs}</div>' if len(langs) > 1 else ''
    note = f'<div class="note-out"><span>What happens</span><p>{ex["result"]}</p></div>' if ex.get('result') else ''
    return f'<div class="codewrap tests pw4{" pw-single" if len(langs) == 1 else ""}" data-k="{key}" data-langs="{" ".join(langs)}">{bar}{tabrow}{panes}{note}</div>'


# ---------- walks: a line by line run with a screenshot after each line ----------
WALK_JS = r'''
import { chromium, expect } from '@playwright/test';
const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: %W%, height: %H% } });
const page = await context.newPage();
page.on('dialog', d => d.accept());
const shot = async i => { await page.waitForTimeout(250); await page.screenshot({ path: `step-${i}.jpg`, type: 'jpeg', quality: 72 }); };
%START%
%BODY%
await browser.close();
'''


def walk_programs(w):
    body = []
    for i, s in enumerate(w['steps']):
        body.append(s['js'])
        body.append(f'await shot({i});')
    js_prog = WALK_JS.replace('%W%', str(w['size'][0])).replace('%H%', str(w['size'][1])).replace('%START%', w.get('start', '')).replace('%BODY%', '\n'.join(body))
    py_prog = ('from playwright.sync_api import sync_playwright, expect\n\nwith sync_playwright() as p:\n    browser = p.chromium.launch()\n'
               '    page = browser.new_page()\n    page.on("dialog", lambda d: d.accept())\n'
               + ''.join('    ' + ln + '\n' for s in w['steps'] for ln in s['py'].split('\n')) + '    browser.close()\n    print("all steps passed")\n')
    java_prog = ('package com.brainy;\n\nimport com.microsoft.playwright.*;\nimport com.microsoft.playwright.options.*;\nimport org.junit.jupiter.api.Test;\n'
                 'import java.util.regex.Pattern;\nimport static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;\n\n'
                 'public class WalkTest {\n  @Test\n  void walk() {\n    try (Playwright playwright = Playwright.create()) {\n'
                 '      Browser browser = playwright.chromium().launch();\n      Page page = browser.newPage();\n      page.onDialog(d -> d.accept());\n'
                 + ''.join('      ' + ln + '\n' for s in w['steps'] for ln in s['java'].split('\n')) + '      System.out.println("all steps passed");\n    }\n  }\n}\n')
    return js_prog, py_prog, java_prog


def run_walk(key, w):
    js_prog, py_prog, java_prog = walk_programs(w)
    shots_dir = os.path.join(OUT, 'walks')
    os.makedirs(shots_dir, exist_ok=True)
    n = len(w['steps'])

    def keep_shots(d, port, res):
        res['shots'] = []
        for i in range(n):
            src = os.path.join(d, f'step-{i}.jpg')
            if os.path.exists(src):
                name = f'{key}-{i}.jpg'
                shutil.copy(src, os.path.join(shots_dir, name))
                res['shots'].append(name)

    jspec = {'lang': 'js', 'files': {'package.json': '{"type": "module"}', 'walk.mjs': js_prog}, 'cmd': 'node walk.mjs', 'after': keep_shots}
    pspec = {'lang': 'py', 'files': {'walk.py': py_prog}, 'cmd': 'python walk.py'}
    vspec = {'lang': 'java', 'files': {'pom.xml': PK.pom('junit'), 'src/test/java/com/brainy/WalkTest.java': java_prog}, 'cmd': 'mvn test'}
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        fs = {lg: ex.submit(run_lang, sp, key) for lg, sp in (('js', jspec), ('py', pspec), ('java', vspec))}
        res = {lg: f.result() for lg, f in fs.items()}
    for lg, r in res.items():
        if r['code'] != 0:
            raise SystemExit(f'walk {key} [{lg}] failed\n{r["out"][-5000:]}')
    shots = res['js'].get('shots') or []
    if len(shots) != n or not all(os.path.exists(os.path.join(shots_dir, s)) for s in shots):
        # The run came from the cache but the pictures are gone: run the JavaScript version again.
        ck = hashlib.sha256(json.dumps([jspec['files'], jspec['cmd'], _APPH, RUN_STAMP], sort_keys=True).encode()).hexdigest()[:24]
        os.remove(os.path.join(CACHE, ck + '.json'))
        shots = run_lang(jspec, key).get('shots') or []
    return shots


def walk_block(key, w, shots):
    data = {'title': w['title'], 'steps': [{'cap': s['cap'], 'img': f'walks/{shots[i]}' if i < len(shots) else '', 'js': s['js'], 'ts': s['ts'], 'py': s['py'], 'java': s['java']}
                                         for i, s in enumerate(w['steps'])], 'w': w['size'][0], 'h': w['size'][1]}
    sub = w.get('sub') or 'Each screen was recorded from a real run in Chromium when this page was built. Press Play, or step one line at a time, and switch the language to see the same line in Java, Python, JavaScript or TypeScript.'
    return f'<div class="viz" data-viz="pwwalk" data-sub="{esc(sub)}" data-walk="{esc(json.dumps(data, ensure_ascii=False))}"></div>'


# ---------- loading and checking topics ----------
_pk = importlib.util.spec_from_file_location('pkit', os.path.join(HERE, 'pkit.py'))
PK = importlib.util.module_from_spec(_pk)
_pk.loader.exec_module(PK)


def topic_files():
    return sorted(f for f in os.listdir(os.path.join(HERE, 'topics')) if re.match(r'\d\d-.*\.py$', f))


def load_topic(path):
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    spec = importlib.util.spec_from_file_location('pwtopic_' + re.sub(r'\W', '_', os.path.basename(path)[:-3]), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.T


def all_topics():
    return [load_topic(os.path.join(HERE, 'topics', f)) for f in topic_files()]


def check(T):
    T2 = dict(T)
    T2['ex'] = []
    T2['codes'] = {k: {'result': v.get('result') or ''} for k, v in T['codes'].items()}
    errs = jsb.check(T2)
    for k, v in T['codes'].items():
        if v['t'] == 'four':
            for lg, sp in v['langs'].items():
                for n in sp['show']:
                    if n not in sp['files']:
                        errs.append(f'{k} [{lg}]: shows {n} but has no such file')
        if v['t'] == 'walk':
            for s in v['steps']:
                for bad in ('—', '–', ';'):
                    if bad in s['cap']:
                        errs.append(f'walk {k}: {bad!r} in a caption')
            errs += [f'walk {k}: caption {s["cap"]!r}' for s in v['steps'] if not s['cap']]
    for lab in T.get('labs', []):
        for t in (lab['title'], lab['task'], lab.get('hint', '')):
            if re.search(r'[—–;]', re.sub(r'<code>[\s\S]*?</code>', '', t)):
                errs.append(f'lab {lab["id"]}: an em dash, en dash or semicolon in its text')
    if not any(p.get('easy') for p in T['parts']):
        errs.append('no part is marked easy=True')
    return errs


# ---------- labs: every answer runs for real in all four languages ----------
def lab_versions(labs):
    """Translate each lab answer into the four languages with the playground's own translator (labgen.mjs)."""
    if not labs:
        return {}
    items = [{'id': lab['id'], 'name': lab.get('name') or lab['title'], 'from': 'ts' if 'ts' in lab['answer'] else next(iter(lab['answer'])),
              'src': lab['answer'].get('ts') or next(iter(lab['answer'].values()))} for lab in labs]
    p = subprocess.run([NODE, os.path.join(HERE, 'labgen.mjs')], input=json.dumps(items), capture_output=True, text=True)
    if p.returncode:
        raise SystemExit('labgen.mjs failed\n' + p.stderr)
    out = json.loads(p.stdout)
    for lab in labs:
        for lg, src in lab['answer'].items():
            out[lab['id']][lg] = src
    return out


def lab_spec(lg, src, lab):
    if lg == 'java':
        cls = re.search(r'public class (\w+)', src).group(1)
        return PK.jv({cls + '.java': src})
    if lg == 'py':
        return PK.py({'test_lab.py': src})
    if lg == 'js':
        return PK.js({'lab.spec.js': src})
    return PK.ts({'lab.spec.ts': src})


# ---------- the page ----------
def build(T, chapters):
    errs = check(T)
    if errs:
        raise SystemExit(f'{T["slug"]}:\n  ' + '\n  '.join(errs))
    jobs, results, walks = {}, {}, {}
    with cf.ThreadPoolExecutor(max_workers=int(os.environ.get('PW_BUILD_JOBS', '4'))) as ex:
        for k, v in T['codes'].items():
            if v['t'] == 'four':
                for lg, sp in v['langs'].items():
                    if not sp.get('shown'):
                        jobs[(k, lg)] = ex.submit(run_lang, sp, k)
            elif v['t'] == 'walk':
                jobs[(k, 'walk')] = ex.submit(run_walk, k, v)
        versions = lab_versions(T.get('labs', []))
        for lab in T.get('labs', []):
            for lg, src in versions[lab['id']].items():
                jobs[('lab:' + lab['id'], lg)] = ex.submit(run_lang, lab_spec(lg, src, lab), lab['id'])
        for kk, f in jobs.items():
            try:
                r = f.result()
            except subprocess.TimeoutExpired:
                raise SystemExit(f'{T["slug"]}: {kk} timed out')
            if kk[1] == 'walk':
                walks[kk[0]] = r
            elif kk[0].startswith('lab:'):
                if r['code'] != 0:
                    raise SystemExit(f'{T["slug"]}: the answer of {kk[0]} fails with real Playwright in {kk[1]}\n{r["out"][-5000:]}')
            else:
                results[kk] = r

    blocks = {}
    for k, v in T['codes'].items():
        blocks[k] = four_block(k, v, results) if v['t'] == 'four' else walk_block(k, v, walks[k])

    parts = T['parts']
    n_viz = sum(len(re.findall(r'data-viz="', p['html'])) for p in parts) + sum(1 for v in T['codes'].values() if v['t'] == 'walk')
    n_runs = sum(1 for v in T['codes'].values() if v['t'] == 'four' for sp in v['langs'].values() if not sp.get('shown'))
    n_easy = sum(1 for p in parts if p.get('easy'))
    chips = [f'⏱️ About {T["minutes"]} min read', f'📚 {len(parts)} parts', f'🎬 {n_viz} animations', f'▶ {n_runs} real runs in 4 languages',
             f'🧪 {len(T.get("labs", []))} playground labs', f'🎯 {len(T["quiz"])} quiz questions', f'🧮 {len(T["calc"])} calculations', f'🧒 {n_easy} beginner parts']
    chip_html = ''.join(f'<span class="chip">{c}</span>' for c in chips)
    toc = ''.join(f'<a href="#{p["id"]}"{" class=\"easy\"" if p.get("easy") else ""}><span>{p["emoji"]}</span>{esc(p["title"])}</a>' for p in parts)
    toc += ('<a class="spec" href="#comic">🖼️ Comic</a><a class="spec" href="#real-life">🌍 Real life</a>'
            + ('<a class="spec" href="#practice">🧪 Playground labs</a>' if T.get('labs') else '') + '<a class="spec" href="#quiz">🎯 Quiz</a>'
            '<a class="spec" href="#numbers">🧮 Number crunch</a>')
    secs = []
    for i, p in enumerate(parts, 1):
        body = re.sub(r'\[\[([\w-]+)\]\]', lambda m: blocks[m.group(1)], p['html'].strip())
        tags = '<div class="cl-tags"><span class="cl-easy">🧒 Beginner friendly</span></div>' if p.get('easy') else ''
        secs.append(f'<section class="card reveal jsec{" easy-part" if p.get("easy") else ""}" id="{p["id"]}" data-say="{p["id"]}"><div class="sec-num">Part {i}</div>'
                    f'<h2><span class="sec-em">{p["emoji"]}</span><span>{esc(p["title"])}</span></h2>\n{tags}\n{body}\n</section>\n')

    idx = [c['slug'] for c in chapters].index(T['slug'])
    pv = chapters[idx - 1] if idx else None
    nx = chapters[idx + 1] if idx + 1 < len(chapters) else None
    a = (f'<a class="prev" href="./{pv["slug"]}.html" data-topic="{pv["slug"]}"><small>← Previous chapter</small><b>{pv["emoji"]} {esc(pv["short"])}</b></a>' if pv else '<span></span>')
    b = (f'<a class="next" href="./{nx["slug"]}.html" data-topic="{nx["slug"]}"><small>Next chapter →</small><b>{nx["emoji"]} {esc(nx["short"])}</b></a>'
         if nx else '<a class="next" href="./interview-questions.html" data-topic="interview-questions"><small>Next →</small><b>🎤 Interview Questions</b></a>')
    pager = f'<nav class="pager">{a}{b}</nav>'

    page = {k: T[k] for k in ['info', 'real', 'quiz', 'calc', 'say']}
    page['ex'] = []
    page['quiz'] = [{**q, 'q': jsb.inline(q['q']), 'o': [jsb.inline(o) for o in q['o']], 'hint': jsb.inline(q['hint']), 'why': jsb.inline(q['why'])} for q in T['quiz']]
    page['calc'] = [{**c, 'q': jsb.inline(c['q']), 'hint': jsb.inline(c['hint']), 'steps': [jsb.inline(x) for x in c['steps']]} for c in T['calc']]
    page['dg'] = T.get('dg', {})
    page['lanes'] = T.get('lanes', {})
    page['play'] = {}
    page['labs'] = [{**lab, 'answer': {**versions.get(lab['id'], {}), **lab['answer']}} for lab in T.get('labs', [])]
    page['trees'] = T.get('trees', {})
    mod = T['module']
    plain = f'<div class="cl-plain"><b>🧒 In plain words</b><p>{T["plain"]}</p></div>' if T.get('plain') else ''
    picker = ''.join(f'<button type="button" data-l="{lg}">{em} {nm}</button>' for lg, (em, nm) in L4.items())
    out = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(T["title"])} · {SUBJECT_TITLE}</title>
<meta name="description" content="{esc(T["desc"])}">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Nunito:wght@500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/theme.css">
<link rel="stylesheet" href="../../assets/extras.css">
<link rel="stylesheet" href="../../assets/learn.css">
<link rel="stylesheet" href="../../assets/lesson.css">
<link rel="stylesheet" href="../../assets/viz.css">
<link rel="stylesheet" href="../../assets/jsplay.css">
<link rel="stylesheet" href="../../assets/claude.css">
<link rel="stylesheet" href="../../assets/pw.css">
</head>
<body>
<div class="wrap">
  <div class="crumb"><a class="home-link" href="../../subject.html?s={SUBJECT}" target="_top">{SUBJECT_EMOJI} {SUBJECT_TITLE}</a><span>›</span><span>{mod[0]} {esc(mod[1])}</span><span>›</span><span>Chapter {idx + 1} of {len(chapters)}</span></div>
  <header class="hero" id="top" data-say="top">
    <div class="hero-row"><span class="em">{T["emoji"]}</span><div><h1>{esc(T["title"])}</h1><p class="lead">{T["lead"]}</p></div></div>
    <div class="chips">{chip_html}<button type="button" class="listen-btn" id="listenAll">🎧 Listen in 6 languages</button></div>
    <div class="pw-pick" role="group" aria-label="Your programming language"><span>I write my tests in</span>{picker}</div>
    {plain}
  </header>
  <nav class="toc" aria-label="Parts of this chapter">{toc}<button type="button" class="cl-toggle" id="easyOnly" aria-pressed="false">🧒 Show the beginner path only</button></nav>
  <section class="card reveal" id="comic"></section>

{"".join(secs)}
  <section class="card reveal" id="real-life"></section>
  {'<section class="card" id="practice" data-say="practice"></section>' if T.get('labs') else '<section id="practice" hidden></section>'}
  <section class="card reveal" id="quiz"{'' if T.get('labs') else ' data-say="practice"'}></section>
  <section class="card reveal" id="numbers"></section>
  <p class="cl-checked">📖 {T.get("checked", "Every API, option and command on this page was checked against the official Playwright documentation and release notes (version 1.64, October 2026). Every example was run with Playwright 1.63 in Chromium when the page was built, and the output shown is what it printed.")}</p>
  {pager}
</div>
<script src="../../assets/fun.js"></script>
<script src="../../assets/extras.js"></script>
<script src="../../assets/learn.js"></script>
<script src="../../assets/voice.js"></script>
<script src="../../assets/viz.js"></script>
<script src="../../assets/jsviz.js"></script>
<script src="../../assets/jsplay.js"></script>
<script src="../../assets/claude.js"></script>
<script src="../../assets/pwviz.js"></script>
<script src="../../assets/pwplay.js"></script>
<script>
const PAGE = {jsb.js(page)};
JSPLAY.page({{ title: {jsb.js(T["title"])}, subject: {jsb.js(SUBJECT)} }});
CLAUDE_PAGE.wire();
PW.page();
</script>
</body>
</html>
'''
    dest = os.path.join(OUT, T['slug'] + '.html')
    os.makedirs(OUT, exist_ok=True)
    open(dest, 'w', encoding='utf-8').write(out)
    print(f'{T["slug"]}: {len(parts)} parts, {n_viz} animations, {n_runs} runs, {len(T.get("labs", []))} labs, {len(out) // 1024} KB -> {os.path.relpath(dest, ROOT)}')


# ---------- the catalog block ----------
def catalog(chapters):
    js = jsb.js
    mods = []
    for T in chapters:
        if not mods or mods[-1]['key'] != T['module']:
            mods.append({'key': T['module'], 'topics': []})
        mods[-1]['topics'].append(T)
    L = ['function pwModules() {', '  return [']
    for mi, m in enumerate(mods):
        em, title, mid, blurb = m['key']
        L.append(f'    {{ id: {js(mid)}, title: {js(title)}, emoji: {js(em)}, blurb: {js(blurb)}, topics: [')
        for ti, T in enumerate(m['topics']):
            secs = []
            for p in T['parts']:
                secs.append(f'        {{ id: {js(p["id"])}, title: {js(p["title"])}, emoji: {js(p["emoji"])}, group: {js("Beginner path" if p.get("easy") else "Lesson")}, keywords: {js(p.get("kw", []))} }}')
            for lab in T.get('labs', []):
                secs.append(f'        {{ id: {js("lab-" + lab["id"])}, title: {js(lab["title"])}, emoji: "🧪", group: "Playground lab" }}')
            secs.append("        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' }")
            secs.append("        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }")
            L.append(f'      {{ id: {js(T["slug"])}, title: {js(T["title"])}, emoji: {js(T["emoji"])}, page: {js("content/playwright/" + T["slug"] + ".html")},')
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
    start = '/* ===== pw-build: Playwright chapters. Generated by tools/pw-build/build.py, edit the topic files instead. ===== */'
    end = '/* ===== end of pw-build ===== */'
    new = f'{start}\n{block_text}\n{end}'
    if start in src:
        src = re.sub(re.escape(start) + r'[\s\S]*?' + re.escape(end), lambda _: new, src)
    else:
        src = src.rstrip('\n') + '\n\n' + new + '\n'
    open(path, 'w', encoding='utf-8').write(src)
    print(f'catalog: {len(chapters)} chapters in {len(mods)} modules -> data/catalog.js')


# ---------- a copy of the shop for the playground ----------
PAGES = ('index', 'login', 'products', 'cart', 'forms', 'widgets', 'orders', 'frames', 'payment', 'help', 'shadow', 'a11y', 'clock', 'about-you')


def copy_shop():
    """Copy Brainy Shop into content/playwright/shop/ for the playground. Paths become relative files, and fakeapi.js
    answers the /api/ calls in the browser, so the shop works on a static web host with no server."""
    dest = os.path.join(OUT, 'shop')
    os.makedirs(dest, exist_ok=True)
    site = os.path.join(APP, 'site')
    names = '|'.join(p for p in PAGES if p != 'index')
    for f in sorted(os.listdir(site)):
        src = open(os.path.join(site, f), encoding='utf-8').read() if not f.endswith('.png') else None
        if src is None:
            shutil.copy(os.path.join(site, f), os.path.join(dest, f))
            continue
        src = re.sub(r'([\'"(])/(' + names + r')(\?[^\'"()\s]*)?(?=[\'"\s)])', lambda m: f'{m.group(1)}{m.group(2)}.html{m.group(3) or ""}', src)
        src = re.sub(r'href="/"', 'href="index.html"', src)
        src = src.replace('"/style.css"', '"style.css"').replace('"/app.js"', '"app.js"').replace('"/lamp.svg"', '"lamp.svg"')
        src = src.replace('href="/download/report.csv"', 'href="report.csv" download="orders-report.csv"')
        if f.endswith('.html'):
            src = src.replace('<head>', '<head><script src="fakeapi.js"></script>', 1)
        open(os.path.join(dest, f), 'w', encoding='utf-8').write(src)
    shutil.copy(os.path.join(APP, 'fakeapi.js'), os.path.join(dest, 'fakeapi.js'))
    open(os.path.join(dest, 'report.csv'), 'w').write('order,total\n1001,219\n1002,1299\n')


def main():
    copy_shop()
    if not NODE:
        raise SystemExit('Node.js was not found. Set PW_BUILD_NODE.')
    if not os.path.exists(os.path.join(PYBIN, 'pytest')):
        raise SystemExit('The Python box is missing. See README.md for the one time set up.')
    chapters = all_topics()
    want = [a for a in sys.argv[1:] if not a.startswith('-')]
    for T in chapters:
        if not want or T['slug'] in want:
            build(T, chapters)
    catalog(chapters)


if __name__ == '__main__':
    main()
