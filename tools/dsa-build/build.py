"""Build the standalone DSA topic pages in content/dsa/ from the topic files in topics/.

Every program on a page is run for real in Python, JavaScript and Java. The real output is shown
under the code, and a line by line recording powers the "Run line by line" viewer.

The page frame (styles, quiz, narrator, step viewer, animations and page glue) is copied from
content/dsa/dsa-introduction.html, so every DSA page looks and behaves the same.

Usage:  python3 tools/dsa-build/build.py [slug ...]        (no slug builds every topic)
Needs:  python3, node 22+, a JDK 21 (javac and java).
"""
import concurrent.futures as cf
import hashlib
import html
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DSA = os.path.join(ROOT, 'content', 'dsa')
CACHE = os.path.join(HERE, '.cache')
JTOOL = os.path.join(CACHE, 'jtool')
LANGS = ['py', 'js', 'java']
# Other subjects reuse this builder (see tools/mlmath-build/build.py). They change these settings before building.
OUT = DSA
TOPICS = os.path.join(HERE, 'topics')
SUBJ = {'id': 'dsa', 'crumb': '🧩 Data Structures &amp; Algorithms', 'tag': 'DSA', 'langs': '🐍 Python · 🟨 JavaScript · ☕ Java'}
PATCH = None  # optional function(css, topbar, shared, glue) -> the same four, to adapt the shared frame


# ---------- the shared page frame ----------
def frame():
    src = open(os.path.join(DSA, 'dsa-introduction.html'), encoding='utf-8').read()
    css = re.search(r'<style>\n(.*?)</style>', src, re.S).group(1)
    topbar = re.search(r'<header class="topbar">.*?</header>', src).group(0)
    shared = re.search(r'<script>\n(/\* ===== Shared fun layer.*?)\nconst META = ', src, re.S).group(1)
    glue = re.search(r'\n(/\* ===== Page glue.*?)</script>', src, re.S).group(1)
    if PATCH:
        return PATCH(css, topbar, shared, glue)
    return css, topbar, shared, glue


# ---------- running and recording programs ----------
def java_tool():
    os.makedirs(JTOOL, exist_ok=True)
    jar = os.path.join(JTOOL, 'JavaTrace.class')
    srcf = os.path.join(HERE, 'JavaTrace.java')
    if not os.path.exists(jar) or os.path.getmtime(jar) < os.path.getmtime(srcf):
        subprocess.run(['javac', '-d', JTOOL, srcf], check=True, capture_output=True)


def run_one(lang, code):
    key = hashlib.sha256((lang + '\0' + code + '\0' + tracer_stamp(lang)).encode()).hexdigest()[:24]
    cf_path = os.path.join(CACHE, key + '.json')
    if os.path.exists(cf_path):
        return json.load(open(cf_path, encoding='utf-8'))
    with tempfile.TemporaryDirectory() as d:
        if lang == 'py':
            p = os.path.join(d, 'prog.py')
            open(p, 'w', encoding='utf-8').write(code)
            plain = subprocess.run([sys.executable, p], capture_output=True, text=True, timeout=60)
            r = subprocess.run([sys.executable, os.path.join(HERE, 'py_trace.py'), p], capture_output=True, text=True, timeout=300)
        elif lang in ('js', 'ts'):
            if lang == 'ts':
                code = strip_types(d, code)
            p = os.path.join(d, 'prog.js')
            open(p, 'w', encoding='utf-8').write(code)
            plain = subprocess.run(['node', p], capture_output=True, text=True, timeout=60)
            r = subprocess.run(['node', os.path.join(HERE, 'js_trace.mjs'), p], capture_output=True, text=True, timeout=600)
        else:
            cls = re.search(r'public class (\w+)', code).group(1)
            p = os.path.join(d, cls + '.java')
            open(p, 'w', encoding='utf-8').write(code)
            c = subprocess.run(['javac', '-g', '-d', d, p], capture_output=True, text=True)
            if c.returncode:
                raise RuntimeError('javac failed:\n' + c.stderr)
            plain = subprocess.run(['java', '-cp', d, cls], capture_output=True, text=True, timeout=60)
            r = subprocess.run(['java', '-cp', JTOOL, 'JavaTrace', d, cls], capture_output=True, text=True, timeout=600)
        if plain.returncode:
            raise RuntimeError(f'{lang} program failed:\n{plain.stderr}')
        res = json.loads(r.stdout)
        if res['out'] != plain.stdout:
            raise RuntimeError(f'{lang} recording printed something different from the plain run:\n{res["out"]!r}\n{plain.stdout!r}')
    os.makedirs(CACHE, exist_ok=True)
    json.dump(res, open(cf_path, 'w', encoding='utf-8'), ensure_ascii=False)
    return res


def strip_types(d, code):
    """Check a TypeScript program with tsc in strict mode, then remove its types with Node.js.
    Node replaces each type with spaces, so every line keeps its number for the line by line viewer."""
    src = os.path.join(d, 'prog.ts')
    open(src, 'w', encoding='utf-8').write(code)
    c = subprocess.run(['tsc', '--strict', '--noEmit', '--target', 'es2022', '--lib', 'es2022,dom', src], capture_output=True, text=True)
    if c.returncode:
        raise RuntimeError('tsc found type errors:\n' + c.stdout + c.stderr)
    s = subprocess.run(['node', '--no-warnings', '-e', 'process.stdout.write(require("node:module").stripTypeScriptTypes(require("fs").readFileSync(process.argv[1], "utf8")))', src],
                       capture_output=True, text=True, check=True)
    return s.stdout


_stamps = {}


def tracer_stamp(lang):
    if lang not in _stamps:
        f = {'py': 'py_trace.py', 'js': 'js_trace.mjs', 'ts': 'js_trace.mjs', 'java': 'JavaTrace.java'}[lang]
        _stamps[lang] = hashlib.sha256(open(os.path.join(HERE, f), 'rb').read()).hexdigest()[:12]
    return _stamps[lang]


# ---------- page assembly ----------
def js(v):
    return json.dumps(v, ensure_ascii=False).replace('</', '<\\/')


def load_topic(path):
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.T


def check(T):
    errs = []
    keys = set(T['codes'])
    used = set(re.findall(r'data-k="([^"]+)"', ''.join(p['html'] for p in T['parts'])))
    used |= {p['code'] for p in T['practice']}
    for k in used - keys:
        errs.append(f'code block {k} is used but not written')
    for k in keys - used:
        errs.append(f'code block {k} is written but never shown')
    for k, c in T['codes'].items():
        for l in LANGS:
            if l not in c:
                errs.append(f'code block {k} has no {l} version')
    says = {'top', 'practice'} | {p['id'] for p in T['parts']}
    given = {s['id'] for s in T['say']}
    for s in says - given:
        errs.append(f'narration missing for {s}')
    for s in T['say']:
        for l in ['en', 'hi', 'kn', 'or', 'ar', 'de']:
            if not s.get(l):
                errs.append(f'narration {s["id"]} has no {l} text')
    for q in T['quiz']:
        if not 0 <= q['a'] < len(q['o']):
            errs.append('quiz answer out of range: ' + q['q'])
    return errs


def build(slug):
    T = load_topic(os.path.join(TOPICS, slug + '.py'))
    errs = check(T)
    if errs:
        raise SystemExit(f'{slug}:\n  ' + '\n  '.join(errs))
    css, topbar, shared, glue = frame()

    jobs = {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for k, c in T['codes'].items():
            for l in LANGS:
                jobs[(k, l)] = ex.submit(run_one, l, c[l].strip('\n'))
        res = {}
        for (k, l), f in jobs.items():
            try:
                res[(k, l)] = f.result()
            except Exception as e:
                raise SystemExit(f'{slug}: {k} [{l}] {e}')

    codes, outs, traces, same, tr = {}, {}, {}, {}, {}
    for k, c in T['codes'].items():
        codes[k] = {l: c[l].strip('\n') for l in LANGS}
        outs[k] = {l: res[(k, l)]['out'].rstrip('\n') for l in LANGS}
        same[k] = len({outs[k][l] for l in LANGS}) == 1
        if not same[k] and not T.get('allow_diff', {}).get(k):
            print(f'  note: {k} prints different text per language')
        tr[k] = []
        for l in LANGS:
            t = res[(k, l)]['trace']
            if t['end'].get('t'):
                print(f'  note: {k} [{l}] recording was cut short')
            traces[f'{T["prefix"]}|{k}|{l}'] = t
            tr[k].append(l)

    meta = {'slug': T['slug'], 'title': T['title'], 'topic': T['topic'], 'prefix': T['prefix'], 'subject': SUBJ['id'],
            'same': same, 'trace': tr, 'outlbl': T.get('outlbl', {})}
    page = {k: T[k] for k in ['info', 'real', 'quiz', 'calc', 'say', 'practice']}
    page['dg'] = None
    page['x'] = T.get('x')

    parts = T['parts']
    n_viz = sum(len(re.findall(r'data-viz="', p['html'])) for p in parts)
    chips = [f'⏱️ About {T["minutes"]} min read', f'📚 {len(parts)} parts', f'🎬 {n_viz} animations',
             f'🏋️ {len(T["practice"])} practice problems', f'🎯 {len(T["quiz"])} quiz questions',
             f'🧮 {len(T["calc"])} calculations', SUBJ['langs']]
    chip_html = ''.join(f'<span class="chip">{c}</span>' for c in chips)
    toc = ''.join(f'<a href="#{p["id"]}"><span>{p["emoji"]}</span>{html.escape(p["title"])}</a>' for p in parts)
    toc += ('<a class="spec" href="#comic">🖼️ Comic</a><a class="spec" href="#real-life">🌍 Real life</a>'
            '<a class="spec" href="#practice">🏋️ Practice</a><a class="spec" href="#quiz">🎯 Quiz</a>'
            '<a class="spec" href="#numbers">🧮 Number crunch</a>')
    secs = []
    for i, p in enumerate(parts, 1):
        secs.append(f'<section class="card reveal jsec" id="{p["id"]}" data-say="{p["id"]}"><div class="sec-num">Part {i}</div>'
                    f'<h2><span class="sec-em">{p["emoji"]}</span><span>{html.escape(p["title"])}</span></h2>\n'
                    f'{p["html"].strip()}\n</section>\n')
    pager = ''
    pv, nx = T.get('prev'), T.get('next')
    a = (f'<a class="prev" href="./{pv[1]}.html" data-topic="{pv[0]}"><small>← Previous topic</small><b>{pv[2]}</b></a>' if pv else '<span></span>')
    b = (f'<a class="next" href="./{nx[1]}.html" data-topic="{nx[0]}"><small>Next topic →</small><b>{nx[2]}</b></a>' if nx else '<span></span>')
    pager = f'<nav class="pager">{a}{b}</nav>'

    mod = T['module']
    out = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(T["title"])} · {SUBJ["tag"]}</title>
<meta name="description" content="{html.escape(T["desc"])}">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Nunito:wght@500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
{css}
/* ===== Extra styles for this topic's animations ===== */
{T.get("css", "").strip()}
</style>
</head>
<body>
{topbar}
<div class="wrap">
  <div class="crumb"><a class="home-link" href="../../subject.html?s={SUBJ["id"]}" target="_top">{SUBJ["crumb"]}</a><span>›</span><span>{mod[0]} {html.escape(mod[1])}</span><span>›</span><span>{html.escape(T["short"])}</span></div>
  <header class="hero" id="top" data-say="top">
    <div class="hero-row"><span class="em">{T["emoji"]}</span><div><h1>{html.escape(T["title"])}</h1><p class="lead">{T["lead"]}</p></div></div>
    <div class="chips">{chip_html}<button type="button" class="listen-btn" id="listenAll">🎧 Listen in 6 languages</button></div>
  </header>
  <nav class="toc" aria-label="Parts of this page">{toc}</nav>
  <section class="card reveal" id="comic"></section>

{"".join(secs)}
  <section class="card reveal" id="real-life"></section>
  <section class="card reveal" id="practice" data-say="practice"></section>
  <section class="card reveal" id="quiz"></section>
  <section class="card reveal" id="numbers"></section>
  {pager}
</div>
<script type="application/json" id="traces">{js(traces)}</script>
<script>
{shared}
const META = {js(meta)};
const PAGE = {js(page)};
const CODES = {js(codes)};
const OUTS = {js(outs)};
/* ===== Animations written for this topic, added to the shared VIZ widgets ===== */
{T.get("viz", "").strip()}
{glue}</script>
</body>
</html>
'''
    dest = os.path.join(OUT, T['slug'] + '.html')
    open(dest, 'w', encoding='utf-8').write(out)
    print(f'{slug}: {len(parts)} parts, {n_viz} animations, {len(T["codes"])} programs, {len(out) // 1024} KB -> {os.path.relpath(dest, ROOT)}')


def main():
    java_tool()
    slugs = sys.argv[1:] or sorted(f[:-3] for f in os.listdir(TOPICS) if f.endswith('.py'))
    for s in slugs:
        build(s)


if __name__ == '__main__':
    main()
