"""Build the Computer Vision chapter pages in content/computer-vision/ from the topic files in topics/.

Each chapter page is split into tabs so a reader sees one thing at a time:
  Learn             the lessons, one at a time, with a numbered stepper
  Formulas          every formula card from the lessons, collected in one place
  Worked problems   typed answers checked on the page, with the full working
  Quiz              four levels, easy to expert
  Assignments       Python tasks checked by tests that run in the browser (Pyodide)
  Summary           what you must know from the chapter

What the build checks before it writes a page:
  - house style: no em dashes, en dashes, semicolons or emojis in prose
  - at least 10 quiz questions and 10 worked problems per chapter, and every worked problem's written answer
    matches its check value worked out in Python
  - every Python example runs with CPython. Its real output and a line by line recording (tools/py-build/pytrace.py)
    are stored in the page
  - every assignment's model solution passes its own tests, and the starter code does not
  - every animation named in a lesson exists in assets/cvviz.js

It also writes the cvModules() block in data/catalog.js between markers.

Usage:  python3 tools/cv-build/build.py [slug ...]      (no slug builds every chapter)
The Interview Questions page is built by:  python3 tools/interview-build/build.py --run computer-vision
"""
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

# Everything that differs between subjects. tools/nlp-build/build.py changes these and then calls main().
CFG = {
    'subject': 'computer-vision', 'name': 'Computer Vision', 'topics': os.path.join(HERE, 'topics'),
    'func': 'cvModules', 'marker': 'cv-build', 'builder': 'tools/cv-build/build.py', 'badge': 'CV',
    'widgets': ['cvviz.js', 'cvwidgets.js'], 'css': ['cv.css'], 'body': 'cvp',
}
TRACER = os.path.join(ROOT, 'tools', 'py-build', 'pytrace.py')
LVN = {'e': 'Easy', 'm': 'Medium', 'h': 'Hard', 'x': 'Expert'}
EMOJI = re.compile('[\U0001F000-\U0001FAFF☀-➿⭐⬆↔-↪️]')


def out_dir():
    return os.path.join(ROOT, 'content', CFG['subject'])


def js(v):
    return json.dumps(v, ensure_ascii=False).replace('</', '<\\/')


# ---------- loading the chapters ----------
def chapters():
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    out = []
    for f in sorted(f for f in os.listdir(CFG['topics']) if re.match(r'\d\d-.*\.py$', f)):
        spec = importlib.util.spec_from_file_location(f[:-3], os.path.join(CFG['topics'], f))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        T = m.T
        T['file'] = f[:-3]
        out.append(T)
    return out


# ---------- house style and content checks ----------
def prose(s):
    s = re.sub(r'<pre[\s\S]*?</pre>|<code>[\s\S]*?</code>', ' ', str(s))
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'&[#\w]+;', ' ', s)


def style_errors(T):
    bad = []

    def look(where, s):
        t = prose(s)
        for ch, label in (('—', 'em dash'), ('–', 'en dash'), (';', 'semicolon'), ('\\', 'stray backslash')):
            if ch in t:
                i = t.index(ch)
                bad.append(f'{where}: {label} in "...{t[max(0, i - 50):i + 20]}..."')
        m = EMOJI.search(t)
        if m:
            bad.append(f'{where}: emoji {m.group(0)!r} in "...{t[max(0, m.start() - 40):m.start() + 10]}..."')

    for k in ('title', 'short', 'lead', 'desc', 'summary'):
        look(k, T.get(k, ''))
    for p in T['lessons']:
        look(f'lesson {p["id"]}', p['html'])
        look(f'lesson {p["id"]} title', p['title'])
    for i, q in enumerate(T['quiz']):
        for k in ('q', 'hint', 'why'):
            look(f'quiz {i + 1}.{k}', q[k])
        for o in q['o']:
            look(f'quiz {i + 1} option', o)
    for i, c in enumerate(T['calc']):
        look(f'calc {i + 1}.q', c['q'])
        look(f'calc {i + 1}.hint', c['hint'])
        for s in c['steps']:
            look(f'calc {i + 1} step', s)
    for a in T['assign']:
        for k in ('title', 'task', 'hint', 'why'):
            look(f'assignment {a["id"]}.{k}', a[k])
    for m in T['must']:
        look('must', m[0] + ' ' + m[1])
    return bad


def content_errors(T, known_viz):
    bad = []
    if T.get('kind') != 'revision':
        if len(T['quiz']) < 10:
            bad.append(f'only {len(T["quiz"])} quiz questions, at least 10 are needed')
        if len(T['calc']) < 10:
            bad.append(f'only {len(T["calc"])} worked problems, at least 10 are needed')
        if len(T['assign']) < 2:
            bad.append('at least 2 assignments are needed')
        if len(T['must']) < 5:
            bad.append('the summary needs at least 5 must know points')
        if 'class="ladder"' not in ''.join(p['html'] for p in T['lessons']):
            bad.append('at least one lesson needs a ladder (school to research)')
    for i, c in enumerate(T['calc']):
        if c.get('check') is None:
            bad.append(f'calc {i + 1} has no check value')
            continue
        want = c['check']
        try:
            got = float(c['ans'].replace('−', '-').replace(',', ''))
        except ValueError:
            if str(want) != c['ans']:
                bad.append(f'calc {i + 1}: written answer {c["ans"]!r} but the check says {want!r}')
            continue
        tol = c.get('tol', 1e-9 * max(1, abs(float(want))))
        if abs(got - float(want)) > tol + 1e-12:
            bad.append(f'calc {i + 1}: written answer {c["ans"]} but the check says {want}')
        if len(c['steps']) < 3:
            bad.append(f'calc {i + 1}: needs at least 3 steps so a beginner can follow it')
    for q in T['quiz']:
        if len(set(q['o'])) != len(q['o']):
            bad.append('quiz has two identical options: ' + q['q'][:50])
        if not 0 <= q['a'] < len(q['o']):
            bad.append('quiz answer out of range: ' + q['q'][:50])
    allhtml = ''.join(p['html'] for p in T['lessons'])
    used = set(re.findall(r'class="cv-code" data-k="([^"]+)"', allhtml))
    for k in used - set(T['codes']):
        bad.append(f'code block {k} is used but not written')
    for k in set(T['codes']) - used:
        bad.append(f'code block {k} is written but never shown')
    for v in set(re.findall(r'data-viz="([^"]+)"', allhtml)) - known_viz:
        bad.append(f'animation {v} is not defined in assets/' + CFG['widgets'][-1])
    ids = [p['id'] for p in T['lessons']]
    reserved = {'formulas', 'problems', 'quiz', 'assign', 'summary', 'learn'}
    if len(set(ids)) != len(ids) or reserved & set(ids):
        bad.append('lesson ids must be unique and must not be a tab name')
    return bad


def viz_names():
    src = ''.join(open(os.path.join(ROOT, 'assets', f), encoding='utf-8').read() for f in CFG['widgets'])
    return set(re.findall(r"def\('([\w-]+)'", src))


# ---------- running Python ----------
def py(*args, inp=None, timeout=60):
    return subprocess.run([sys.executable, '-I', *args], input=inp, capture_output=True, text=True, timeout=timeout)


def run_code(key, c):
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, 'main.py')
        open(src, 'w', encoding='utf-8').write(c['src'] + '\n')
        r = py(src, inp=c['stdin'])
        if r.returncode:
            raise SystemExit(f'example {key} failed:\n{r.stderr}')
        sin = os.path.join(d, 'stdin.txt')
        open(sin, 'w', encoding='utf-8').write(c['stdin'])
        t = py(TRACER, src, sin)
        if t.returncode:
            raise SystemExit(f'recording {key} failed:\n{t.stderr}')
        rec = json.loads(t.stdout)
        if rec['err']:
            raise SystemExit(f'example {key} raised while recording:\n{rec["err"]}')
        if rec['cut']:
            raise SystemExit(f'the recording of {key} was cut at 600 steps, make the example shorter')
        return r.stdout.rstrip('\n'), rec


CHECK = r'''
import json, sys
code, tests = json.load(sys.stdin)
ns = {'__name__': 'exercise'}
try:
    exec(compile(code, 'exercise.py', 'exec'), ns)
except BaseException as e:
    print(json.dumps(['error', type(e).__name__ + ': ' + str(e)])); raise SystemExit
res = []
for t in tests:
    try:
        got = eval(t['call'], ns)
        res.append(json.dumps(got, sort_keys=True, default=repr) == json.dumps(t['want'], sort_keys=True, default=repr))
    except BaseException as e:
        res.append(False)
print(json.dumps(['ok', res]))
'''


def check_assign(a):
    def run(code):
        r = py('-c', CHECK, inp=json.dumps([code, a['tests']]))
        if r.returncode:
            raise SystemExit(f'assignment {a["id"]}: checker failed\n{r.stderr}')
        return json.loads(r.stdout)
    st, res = run(a['solution'])
    if st != 'ok' or not all(res):
        raise SystemExit(f'assignment {a["id"]}: the model solution fails its tests: {res}')
    st, res = run(a['starter'])
    if st == 'ok' and res and all(res):
        raise SystemExit(f'assignment {a["id"]}: the starter code already passes every test')


def tracer_src():
    src = open(TRACER, encoding='utf-8').read()
    if '</' in src:
        raise SystemExit('pytrace.py contains "</", which would end the script tag that carries it')
    return src


# ---------- page ----------
def page(T, chs, steps_by_id):
    i = [c['slug'] for c in chs].index(T['slug'])
    pv = chs[i - 1] if i else None
    nx = chs[i + 1] if i + 1 < len(chs) else None
    stp = T['step']
    in_step = [c for c in chs if c['step'][0] == stp[0]]
    pos = in_step.index(T) + 1

    outs, recs = {}, {}
    for k, c in T['codes'].items():
        outs[k], recs[k] = run_code(k, c)
    for a in T['assign']:
        check_assign(a)

    lessons = T['lessons']
    n_viz = sum(len(re.findall(r'data-viz="', p['html'])) for p in lessons)
    n_fx = sum(len(re.findall(r'class="fx[ "]', p['html'])) for p in lessons)
    def cnt(n, word, many=None):
        return f'{n} {word if n == 1 else (many or word + "s")}'
    chips = [f'About {T["minutes"]} min', cnt(len(lessons), 'lesson'), cnt(n_viz, 'animation'), cnt(n_fx, 'formula'),
             cnt(len(T["calc"]), 'worked problem'), cnt(len(T["quiz"]), 'quiz question'), cnt(len(T["assign"]), 'assignment')]
    chip_html = ''.join(f'<span class="cv-chip">{c}</span>' for c in chips if not c.startswith('0 '))
    stepper = ''.join(f'<li><a href="#{p["id"]}" data-l="{p["id"]}"><span class="n">{n}</span><span class="t">{html.escape(p["title"])}</span></a></li>'
                      for n, p in enumerate(lessons, 1))
    arts = []
    for n, p in enumerate(lessons, 1):
        arts.append(f'<article class="cv-lesson" id="{p["id"]}" data-l="{p["id"]}" hidden>'
                    f'<div class="cv-lno">Lesson {n} of {len(lessons)}</div><h2>{html.escape(p["title"])}</h2>\n{p["html"].strip()}\n'
                    f'<nav class="cv-lnav"></nav></article>')
    tabs = [('learn', 'Learn'), ('formulas', 'Formulas'), ('problems', 'Worked problems'), ('quiz', 'Quiz'),
            ('assign', 'Assignments'), ('summary', 'Summary')]
    if T.get('kind') == 'revision':
        tabs = [('learn', 'Revise')] + [t for t in tabs[1:] if t[0] in ('formulas', 'problems', 'quiz')]
    tab_html = ''.join(f'<button type="button" class="cv-tab" role="tab" data-tab="{k}">{v}</button>' for k, v in tabs)
    panes = ''.join(f'<section class="cv-pane" data-pane="{k}" role="tabpanel" hidden></section>' for k, _ in tabs if k != 'learn')

    def link(c, lbl):
        return (f'<a class="{lbl[0]}" href="./{c["slug"]}.html" data-topic="{c["topic"]}"><small>{lbl[1]}</small><b>{html.escape(c["short"])}</b></a>')
    pager = (link(pv, ('prev', 'Previous topic')) if pv else '<span></span>') + \
        (link(nx, ('next', 'Next topic')) if nx else '<a class="next" href="./interview-questions.html" data-topic="interview-questions"><small>Next</small><b>Interview Questions</b></a>')

    data = {'slug': T['slug'], 'topic': T['topic'], 'subject': CFG['subject'], 'title': T['title'],
            'codes': {k: {'src': c['src'], 'stdin': c['stdin'], 'out': outs[k]} for k, c in T['codes'].items()},
            'quiz': T['quiz'], 'calc': [{k: v for k, v in c.items() if k != 'check'} for c in T['calc']],
            'assign': [{k: v for k, v in a.items()} for a in T['assign']], 'must': T['must'],
            'summary': T.get('recap', '')}
    css = '\n'.join(f'<link rel="stylesheet" href="../../assets/{c}">' for c in CFG['css'])
    scripts = '\n'.join(f'<script src="../../assets/{w}"></script>' for w in CFG['widgets'])
    out = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(T["title"])} · {CFG["name"]}</title>
<meta name="description" content="{html.escape(T["desc"])}">
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/theme.css">
<link rel="stylesheet" href="../../assets/learn.css">
{css}
</head>
<body class="{CFG["body"]}">
<header class="cv-top"><a class="cv-brand" href="../../index.html">Brainy Bytes</a><a class="cv-home" href="../../subject.html?s={CFG["subject"]}">{CFG["name"]} learning path</a><span class="grow"></span><button type="button" class="cv-theme" id="cvTheme">Dark mode</button></header>
<div class="cv-wrap">
  <div class="cv-crumb"><a class="home-link" href="../../subject.html?s={CFG["subject"]}" target="_top">{CFG["name"]}</a><span>›</span><span>Step {stp[0]}: {html.escape(stp[1])}</span><span>›</span><span>{html.escape(T["short"])}</span></div>
  <header class="cv-hero">
    <div class="cv-kicker">Step {stp[0]} · Topic {pos} of {len(in_step)} · {html.escape(stp[4])}</div>
    <h1>{html.escape(T["title"])}</h1>
    <p class="lead">{T["lead"]}</p>
    <div class="cv-chips">{chip_html}</div>
  </header>
  <nav class="cv-tabs" role="tablist" aria-label="Parts of this chapter">{tab_html}</nav>
  <section class="cv-pane" data-pane="learn" role="tabpanel">
    <ol class="cv-stepper" aria-label="Lessons">{stepper}</ol>
    {"".join(arts)}
  </section>
  {panes}
  <nav class="cv-pager">{pager}</nav>
</div>
<script type="application/json" id="cvdata">{js(data)}</script>
<script type="application/json" id="cvtrace">{js(recs)}</script>
<script type="text/plain" id="cvtracer">{tracer_src()}</script>
<script src="../../assets/fun.js"></script>
<script src="../../assets/learn.js"></script>
<script src="../../assets/pyplay.js"></script>
{scripts}
<script src="../../assets/cv.js"></script>
</body>
</html>
'''
    dest = os.path.join(out_dir(), T['slug'] + '.html')
    open(dest, 'w', encoding='utf-8').write(out)
    print(f'{T["slug"]}: {len(lessons)} lessons, {n_viz} animations, {len(T["codes"])} programs, '
          f'{len(T["calc"])} problems, {len(T["quiz"])} quiz, {len(T["assign"])} assignments, {len(out) // 1024} KB')


# ---------- catalog ----------
def catalog(chs):
    mods = []
    for T in chs:
        if not mods or mods[-1]['step'] != T['step']:
            mods.append({'step': T['step'], 'topics': []})
        mods[-1]['topics'].append(T)
    L = [f'function {CFG["func"]}() {{', '  return [']
    for mi, m in enumerate(mods):
        n, title, mid, blurb, level = m['step']
        L.append(f'    {{ id: {js(mid)}, title: {js(title)}, emoji: {js(str(n))}, step: {n}, level: {js(level)}, blurb: {js(blurb)}, topics: [')
        for ti, T in enumerate(m['topics']):
            secs = [f'        {{ id: {js(p["id"])}, title: {js(p["title"])}, emoji: "", group: "Lesson", keywords: {js(p["kw"])} }}' for p in T['lessons']]
            if T.get('kind') != 'revision':
                secs += ["        { id: 'formulas', title: 'Formulas', emoji: '', group: 'Check yourself' }",
                         "        { id: 'problems', title: 'Worked problems', emoji: '', group: 'Check yourself' }",
                         "        { id: 'quiz', title: 'Quiz', emoji: '', group: 'Check yourself' }",
                         "        { id: 'assign', title: 'Assignments', emoji: '', group: 'Check yourself' }"]
            else:
                secs += ["        { id: 'quiz', title: 'Mock quiz', emoji: '', group: 'Check yourself' }"]
            cnt = {'lessons': len(T['lessons']), 'problems': len(T['calc']), 'quiz': len(T['quiz']), 'assign': len(T['assign'])}
            L.append(f'      {{ id: {js(T["topic"])}, title: {js(T["title"])}, emoji: {js(T.get("badge", CFG["badge"]))}, page: {js("content/" + CFG["subject"] + "/" + T["slug"] + ".html")},')
            L.append(f'        summary: {js(T["summary"])},')
            L.append(f'        keywords: {js(T["keywords"])},')
            L.append(f'        minutes: {T["minutes"]}, counts: {js(cnt)},')
            L.append(f'        added: {js(T.get("added", "2026-10-27"))},')
            L.append('        sections: [')
            L.append(',\n'.join(secs))
            L.append('      ] }' + (',' if ti + 1 < len(m['topics']) else ''))
        L.append('    ] }' + (',' if mi + 1 < len(mods) else ''))
    L += ['  ];', '}']
    path = os.path.join(ROOT, 'data', 'catalog.js')
    src = open(path, encoding='utf-8').read()
    start = f'/* ===== {CFG["marker"]}: {CFG["name"]} chapters. Generated by {CFG["builder"]}, edit the topic files instead. ===== */'
    end = f'/* ===== end of {CFG["marker"]} ===== */'
    new = f'{start}\n' + '\n'.join(L) + f'\n{end}'
    if start in src:
        src = re.sub(re.escape(start) + r'[\s\S]*?' + re.escape(end), lambda _: new, src)
    else:
        src = src.rstrip('\n') + '\n\n' + new + '\n'
    open(path, 'w', encoding='utf-8').write(src)
    print(f'catalog: {len(chs)} chapters in {len(mods)} steps -> data/catalog.js')


def main():
    chs = chapters()
    known = viz_names()
    errs = []
    for T in chs:
        e = style_errors(T) + content_errors(T, known)
        if e:
            errs.append(f'{T["slug"]}:\n  ' + '\n  '.join(e))
    if errs:
        raise SystemExit('\n'.join(errs))
    os.makedirs(out_dir(), exist_ok=True)
    want = sys.argv[1:]
    for T in chs:
        if not want or T['slug'] in want:
            page(T, chs, None)
    catalog(chs)


if __name__ == '__main__':
    main()
