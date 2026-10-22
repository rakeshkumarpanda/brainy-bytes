"""Build the Maths for Machine Learning chapter pages in content/ml-maths/ from the topic files in topics/.

The chapters reuse the DSA page builder (tools/dsa-build/build.py): the same page frame, quiz, number crunch,
narrator, comic and line by line viewer. This file points that builder at this subject and adds:
  - a fourth language, TypeScript. Each TypeScript program is checked by tsc in strict mode, then its types are
    stripped by Node.js (lines keep their numbers) and it is run and recorded like the JavaScript version
  - formula cards, memory tricks, matrices, fractions and a small SVG plotting kit (math.css and mviz.js)
  - checks for the house style (no em dashes, en dashes or semicolons in prose) and for at least ten quiz
    questions and ten worked problems per chapter
  - every worked problem states its answer twice: as text for the reader and as a Python value (check=...).
    The build stops if the two disagree
  - the mlMathModules() block in data/catalog.js, written between markers

Usage:  python3 tools/mlmath-build/build.py [slug ...]      (no slug builds every chapter)
Needs:  python3, Node.js 22.18 or later, tsc (TypeScript) on PATH and a JDK 21 (javac and java).
The Interview Questions page is built by:  python3 tools/interview-build/build.py --run ml-maths
"""
import html
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOPICS = os.path.join(HERE, 'topics')
OUT = os.path.join(ROOT, 'content', 'ml-maths')
SUBJECT = 'ml-maths'

_spec = importlib.util.spec_from_file_location('dsabuild', os.path.join(ROOT, 'tools', 'dsa-build', 'build.py'))
dsb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dsb)
dsb.LANGS = ['py', 'js', 'ts', 'java']
dsb.OUT = OUT
dsb.TOPICS = TOPICS
dsb.CACHE = os.path.join(HERE, '.cache')
dsb.SUBJ = {'id': SUBJECT, 'crumb': '📐 Maths for Machine Learning', 'tag': 'Maths for ML',
            'langs': '🐍 Python · 🟨 JavaScript · 🔷 TypeScript · ☕ Java'}

TS_KW = ("break case catch class const continue debugger default delete do else export extends false finally for function if import in "
         "instanceof let new null return super switch this throw true try typeof undefined var void while with yield of async await "
         "type interface number string boolean readonly as")


def patch(css, topbar, shared, glue):
    def swap(text, a, b):
        if a not in text:
            raise SystemExit(f'the shared DSA frame changed, cannot find: {a[:60]}')
        return text.replace(a, b)
    css += '\n' + open(os.path.join(HERE, 'math.css'), encoding='utf-8').read()
    topbar = swap(topbar, 'Brainy Bytes · DSA', 'Brainy Bytes · Maths for ML').replace('🧩', '📐')
    js_kw = "    js: 'break case catch class const continue debugger default delete do else export extends false finally for function if import in instanceof let new null return super switch this throw true try typeof undefined var void while with yield of async await'"
    shared = swap(shared, js_kw, js_kw + f",\n    ts: '{TS_KW}'")
    shared += '\n' + open(os.path.join(HERE, 'mviz.js'), encoding='utf-8').read()
    glue = swap(glue, "js: ['🟨', 'JavaScript'], java: ['☕', 'Java'] };", "js: ['🟨', 'JavaScript'], ts: ['🔷', 'TypeScript'], java: ['☕', 'Java'] };")
    glue = swap(glue, 'identical in all three languages', 'identical in all four languages')
    return css, topbar, shared, glue


dsb.PATCH = patch


# ---------- loading the chapters ----------
def topic_files():
    return sorted(f for f in os.listdir(TOPICS) if re.match(r'\d\d-.*\.py$', f))


def load(f):
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    return dsb.load_topic(os.path.join(TOPICS, f))


def chapters():
    out = []
    for f in topic_files():
        T = load(f)
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
        for ch, label in (('—', 'em dash'), ('–', 'en dash'), (';', 'semicolon')):
            if ch in t:
                i = t.index(ch)
                bad.append(f'{where}: {label} in "...{t[max(0, i - 50):i + 20]}..."')

    for k in ('title', 'lead', 'desc', 'summary'):
        look(k, T.get(k, ''))
    for p in T['parts']:
        look(f'part {p["id"]}', p['html'])
        look(f'part {p["id"]} title', p['title'])
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
    for p in T['practice']:
        for k in ('title', 'statement', 'hint', 'approach'):
            look(f'practice {p["id"]}.{k}', p[k])
    for r in T['real']:
        look('real', r[1] + ' ' + r[2])
    info = T['info']
    look('info', info['title'] + ' ' + info['remember'])
    for p in info['panels']:
        look('info panel', p['h'] + ' ' + p['t'] + ' ' + p['more'])
    for s in T['say']:
        for l in ('h', 'en', 'hi', 'kn', 'or', 'de', 'ar'):
            look(f'narration {s["id"]}.{l}', s[l])
    return bad


def content_errors(T):
    bad = []
    if len(T['quiz']) < 10:
        bad.append(f'only {len(T["quiz"])} quiz questions, at least 10 are needed')
    if len(T['calc']) < 10:
        bad.append(f'only {len(T["calc"])} worked problems, at least 10 are needed')
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
    return bad


# ---------- build ----------
def build(T, chs):
    i = [c['slug'] for c in chs].index(T['slug'])
    pv = chs[i - 1] if i else None
    nx = chs[i + 1] if i + 1 < len(chs) else None
    T['prev'] = (pv['topic'], pv['slug'], f'{pv["emoji"]} {pv["short"]}') if pv else None
    T['next'] = (nx['topic'], nx['slug'], f'{nx["emoji"]} {nx["short"]}') if nx else ('interview-questions', 'interview-questions', '🎤 Interview Questions')
    T['x'] = {'ppSub': 'Every solution is written in Python, JavaScript, TypeScript and Java, was run for real, and can be replayed line by line.'}
    errs = style_errors(T) + content_errors(T)
    if errs:
        raise SystemExit(f'{T["slug"]}:\n  ' + '\n  '.join(errs))
    for c in T['calc']:
        c.pop('check', None)
    T['_built'] = True
    # the DSA builder loads the topic itself, so hand it this one
    dsb.load_topic = lambda path, _T=T: _T
    os.makedirs(OUT, exist_ok=True)
    dsb.build(T['slug'])


def catalog(chs):
    js = dsb.js
    mods = []
    for T in chs:
        if not mods or mods[-1]['key'] != T['module']:
            mods.append({'key': T['module'], 'topics': []})
        mods[-1]['topics'].append(T)
    L = ['function mlMathModules() {', '  return [']
    lvn = {'e': 'Easy', 'm': 'Medium', 'h': 'Hard', 'x': 'Expert'}
    for mi, m in enumerate(mods):
        em, title, mid, blurb = m['key']
        L.append(f'    {{ id: {js(mid)}, title: {js(title)}, emoji: {js(em)}, blurb: {js(blurb)}, topics: [')
        for ti, T in enumerate(m['topics']):
            secs = [f'        {{ id: {js(p["id"])}, title: {js(p["title"])}, emoji: {js(p["emoji"])}, group: "Lesson", keywords: {js(p.get("kw", []))} }}' for p in T['parts']]
            secs += [f'        {{ id: {js(p["id"])}, title: {js(p["title"])}, emoji: "🏋️", group: {js(lvn[p["lv"]] + " practice")} }}' for p in T['practice']]
            secs.append("        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' }")
            secs.append("        { id: 'numbers', title: 'Worked problems', emoji: '🧮', group: 'Check yourself' }")
            L.append(f'      {{ id: {js(T["topic"])}, title: {js(T["title"])}, emoji: {js(T["emoji"])}, page: {js("content/ml-maths/" + T["slug"] + ".html")},')
            L.append(f'        summary: {js(T["summary"])},')
            L.append(f'        keywords: {js(T["keywords"])},')
            L.append(f'        added: {js(T.get("added", "2026-10-22"))},')
            L.append('        sections: [')
            L.append(',\n'.join(secs))
            L.append('      ] }' + (',' if ti + 1 < len(m['topics']) else ''))
        L.append('    ] }' + (',' if mi + 1 < len(mods) else ''))
    L += ['  ];', '}']
    path = os.path.join(ROOT, 'data', 'catalog.js')
    src = open(path, encoding='utf-8').read()
    start = '/* ===== mlmath-build: Maths for Machine Learning chapters. Generated by tools/mlmath-build/build.py, edit the topic files instead. ===== */'
    end = '/* ===== end of mlmath-build ===== */'
    new = f'{start}\n' + '\n'.join(L) + f'\n{end}'
    if start in src:
        src = re.sub(re.escape(start) + r'[\s\S]*?' + re.escape(end), lambda _: new, src)
    else:
        src = src.rstrip('\n') + '\n\n' + new + '\n'
    open(path, 'w', encoding='utf-8').write(src)
    print(f'catalog: {len(chs)} chapters in {len(mods)} modules -> data/catalog.js')


def main():
    dsb.java_tool()
    chs = chapters()
    want = sys.argv[1:]
    for T in chs:
        if not want or T['slug'] in want:
            build(T, chs)
    catalog(chs)


if __name__ == '__main__':
    main()
