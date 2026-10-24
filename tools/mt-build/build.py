"""Builds the newer Manual Testing pages and merges new parts into the older ones.

    python3 build.py            build everything
    python3 build.py --check    only run the style and data checks

pages/<name>.py   a whole new page, written to content/manual-testing/<file>
adds/<name>.py    new parts, quiz questions, numbers and diagrams merged into an existing page
widgets.css/js    the shared widgets for the new animations, copied into every Manual Testing page

The older pages are hand kept single files, so the merge only touches what lies between the
mt2 markers and the PAGE data entries that it owns. Running the build twice gives the same files.
"""
import html as H
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'content' / 'manual-testing'
TEMPLATE = OUT / 'testing-fundamentals.html'
LANGS = ('en', 'hi', 'kn', 'or', 'ar', 'de')

CSS_A, CSS_B = '/* ===== mt2 widgets: start ===== */', '/* ===== mt2 widgets: end ===== */'
JS_A, JS_B = '/* ===== mt2 widgets js: start ===== */', '/* ===== mt2 widgets js: end ===== */'
SEC_A, SEC_B = '<!-- mt2 parts -->', '<!-- /mt2 parts -->'
TOC_A, TOC_B = '<!-- mt2 toc -->', '<!-- /mt2 toc -->'

problems = []


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(HERE))
    spec.loader.exec_module(mod)
    return mod


# ---------- style checks: the user asked for no em dashes and no semicolons in prose ----------
def prose(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'&[#\w]+;', ' ', s)
    return s


def check_text(where, s):
    t = prose(s)
    if '—' in t:
        problems.append(f'{where}: em dash')
    if ';' in t:
        problems.append(f'{where}: semicolon in "{t[max(0, t.find(";") - 40):t.find(";") + 20]}"')


def walk(where, v):
    if isinstance(v, str):
        check_text(where, v)
    elif isinstance(v, dict):
        for k, x in v.items():
            if k in ('py',):
                continue
            walk(f'{where}.{k}', x)
    elif isinstance(v, (list, tuple)):
        for i, x in enumerate(v):
            walk(f'{where}[{i}]', x)


def check_calc(where, calc):
    for i, c in enumerate(calc):
        got = eval(c['py'], {'math': math})
        want = float(c['ans'])
        if abs(float(got) - want) > 0.011 * max(1, abs(want)) and abs(float(got) - want) > 0.01:
            problems.append(f'{where} calc {i}: py gives {got}, answer says {c["ans"]}')


def check_quiz(where, quiz):
    for i, q in enumerate(quiz):
        if not 0 <= q['a'] < len(q['o']):
            problems.append(f'{where} quiz {i}: answer index out of range')


def check_dg(where, dg):
    for k, d in dg.items():
        ids = {n[0] for n in d.get('n', [])}
        for e in d.get('e', []):
            if e[0] not in ids or e[1] not in ids:
                problems.append(f'{where} diagram {k}: arrow {e[0]} > {e[1]} names a missing node')
        for st in d.get('st', []):
            for x in st[0]:
                if x in ids or x.startswith('g') and x[1:].isdigit():
                    continue
                if '>' in x and all(p in ids for p in x.split('>')):
                    continue
                if any(len(e) > 2 and e[2].get('id') == x for e in d.get('e', [])):
                    continue
                problems.append(f'{where} diagram {k}: step names unknown id {x}')
        for n in d.get('n', []):
            x, y, w, h = n[1:5]
            if x < 0 or y < 0 or x + w > d['w'] or y + h > d['h']:
                problems.append(f'{where} diagram {k}: node {n[0]} sticks out of the drawing')


# ---------- page pieces ----------
def section_html(num, s):
    return (f'<section class="card reveal jsec" id="{s["id"]}" data-say="{s["id"]}"><div class="sec-num">Part {num}</div>'
            f'<h2><span class="sec-em">{s["emoji"]}</span><span>{s["title"]}</span></h2>\n{s["html"]}\n</section>')


def toc_html(secs):
    return ''.join(f'<a href="#{s["id"]}"><span>{s["emoji"]}</span>{s["title"]}</a>' for s in secs)


def say_entry(id, h, d):
    e = {'id': id, 'h': h}
    for k in LANGS:
        if d.get(k):
            e[k] = d[k]
    return e


def dump_page(P):
    return json.dumps(P, ensure_ascii=False).replace('</', '<\\/')


def find_page(s):
    i = s.find('const PAGE = ') + len('const PAGE = ')
    P, end = json.JSONDecoder().raw_decode(s, i)
    return P, i, end


def words(s):
    a = s.find('<h1>')
    b = s.find('id="real-life"')
    body = re.sub(r'<script[\s\S]*?</script>', ' ', s[a:b])
    return len(prose(body).split())


def chips(s, P):
    a, b = s.find('<h1>'), s.find('id="real-life"')
    body = s[a:b]
    parts = len(re.findall(r'class="card reveal jsec"', body))
    anim = len(re.findall(r'data-viz="', body))
    mins = max(1, round(words(s) / 220))
    return (f'<span class="chip">⏱️ About {mins} min read</span><span class="chip">📚 {parts} parts</span>'
            f'<span class="chip">🎬 {anim} animations</span><span class="chip">🎯 {len(P["quiz"])} quiz questions</span>'
            f'<span class="chip">🧮 {len(P["calc"])} calculations</span>')


def set_chips(s, P):
    a = s.find('<div class="chips">') + len('<div class="chips">')
    b = s.find('<button type="button" class="listen-btn"', a)
    return s[:a] + chips(s, P) + s[b:]


def inject(s, a_mark, b_mark, content, before):
    """Put content between the two markers. The first time, the markers go just before `before`."""
    block = f'{a_mark}\n{content}\n{b_mark}\n'
    i = s.find(a_mark)
    if i >= 0:
        j = s.find(b_mark, i) + len(b_mark) + 1
        return s[:i] + block + s[j:]
    k = s.find(before)
    assert k >= 0, before
    return s[:k] + block + s[k:]


def inject_widgets(s):
    css = (HERE / 'widgets.css').read_text()
    js = (HERE / 'widgets.js').read_text()
    s = inject(s, CSS_A, CSS_B, css.strip(), '</style>')
    # the widget script goes at the end of the big shared script, before the page data script
    s = inject(s, JS_A, JS_B, js.strip(), '</script>\n<script>\nconst META')
    return s


# ---------- merging new parts into an existing page ----------
def apply_add(name, mod):
    path = OUT / mod.FILE
    s = path.read_text()
    secs = mod.SECTIONS
    where = f'adds/{name}'
    for x in secs:
        walk(f'{where}#{x["id"]}', [x['html'], x['title'], x['say']['en']])
    walk(where, [mod.QUIZ, mod.CALC, getattr(mod, 'DG', {}), getattr(mod, 'X', {})])
    check_calc(where, mod.CALC)
    check_quiz(where, mod.QUIZ)
    check_dg(where, getattr(mod, 'DG', {}))

    # drop an earlier merge so the part numbers count only the original parts
    if SEC_A in s:
        i = s.find(SEC_A)
        j = s.find(SEC_B, i) + len(SEC_B) + 1
        s = s[:i] + s[j:]
    a, b = s.find('<h1>'), s.find('id="real-life"')
    base = len(re.findall(r'class="card reveal jsec"', s[a:b]))
    body = '\n\n'.join(section_html(base + 1 + k, x) for k, x in enumerate(secs))
    s = inject(s, SEC_A, SEC_B, '\n' + body + '\n', '  <section class="card reveal" id="real-life">')
    s = inject(s, TOC_A, TOC_B, toc_html(secs), '<a class="spec" href="#comic">')

    P, i, end = find_page(s)
    ids = {x['id'] for x in secs}
    P['say'] = [e for e in P['say'] if e['id'] not in ids] + [say_entry(x['id'], x['title'], x['say']) for x in secs]
    P['quiz'] = [q for q in P['quiz'] if not q.get('mt2')] + [dict(q, mt2=1) for q in mod.QUIZ]
    P['calc'] = [c for c in P['calc'] if not c.get('mt2')] + [dict(c, mt2=1) for c in mod.CALC]
    if not P.get('dg'):
        P['dg'] = {}
    if not P.get('x'):
        P['x'] = {}
    P['dg'].update(getattr(mod, 'DG', {}))
    for k, v in getattr(mod, 'X', {}).items():
        if isinstance(v, dict) and isinstance(P['x'].get(k), dict):
            P['x'][k].update(v)
        else:
            P['x'][k] = v
    for r in getattr(mod, 'REAL', []):
        if r not in P['real']:
            P['real'].append(r)
    s = s[:i] + dump_page(P) + s[end:]
    s = set_chips(s, P)
    if hasattr(mod, 'DESCRIPTION'):
        s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{H.escape(mod.DESCRIPTION)}">', s, count=1)
    return path, s


# ---------- a whole new page ----------
def build_page(name, mod):
    where = f'pages/{name}'
    secs = mod.SECTIONS
    for x in secs:
        walk(f'{where}#{x["id"]}', [x['html'], x['title'], x['say']['en']])
    walk(where, [mod.LEAD, mod.QUIZ, mod.CALC, mod.DG, mod.X, mod.INFO, mod.REAL, mod.TOP_SAY['en']])
    check_calc(where, mod.CALC)
    check_quiz(where, mod.QUIZ)
    check_dg(where, mod.DG)

    t = TEMPLATE.read_text()
    t = re.sub(r'<title>[^<]*</title>', f'<title>{H.escape(mod.TITLE)} · Manual Testing</title>', t, count=1)
    t = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{H.escape(mod.DESCRIPTION)}">', t, count=1)
    a = t.find('  <div class="crumb">')
    b = t.find('</nav>', t.find('<nav class="pager">')) + len('</nav>')
    prev, nxt = mod.PREV, mod.NEXT
    pager = '<nav class="pager">'
    pager += (f'<a class="prev" href="./{prev[0]}" data-topic="{prev[1]}"><small>← Previous topic</small><b>{prev[2]}</b></a>' if prev else '<span></span>')
    pager += (f'<a class="next" href="./{nxt[0]}" data-topic="{nxt[1]}"><small>Next topic →</small><b>{nxt[2]}</b></a>' if nxt else '<span></span>')
    pager += '</nav>'
    body = '\n\n'.join(section_html(k + 1, x) for k, x in enumerate(secs))
    main = f'''  <div class="crumb"><a class="home-link" href="../../subject.html?s=manual-testing" target="_top">🧪 Manual Testing</a><span>›</span><span>{mod.MODULE}</span><span>›</span><span>{mod.CRUMB}</span></div>
  <header class="hero" id="top" data-say="top">
    <div class="hero-row"><span class="em">{mod.EMOJI}</span><div><h1>{mod.TITLE}</h1><p class="lead">{mod.LEAD}</p></div></div>
    <div class="chips"><button type="button" class="listen-btn" id="listenAll">🎧 Listen in 6 languages</button></div>
  </header>
  <nav class="toc" aria-label="Parts of this page">{toc_html(secs)}<a class="spec" href="#comic">🖼️ Comic</a><a class="spec" href="#real-life">🌍 Real life</a><a class="spec" href="#quiz">🎯 Quiz</a><a class="spec" href="#numbers">🧮 Number crunch</a></nav>
  <section class="card reveal" id="comic"></section>

{body}

  <section class="card reveal" id="real-life"></section>
  <section class="card reveal" id="quiz"></section>
  <section class="card reveal" id="numbers"></section>
  {pager}'''
    t = t[:a] + main + t[b:]
    t = re.sub(r'const META = \{[^\n]*\};', 'const META = ' + json.dumps(dict(slug=mod.SLUG, title=mod.TITLE, topic=mod.TOPIC, prefix=mod.PREFIX, subject='manual-testing'), ensure_ascii=False) + ';', t, count=1)
    P = dict(info=mod.INFO, real=mod.REAL, quiz=mod.QUIZ, calc=mod.CALC,
             say=[say_entry('top', 'Welcome', mod.TOP_SAY)] + [say_entry(x['id'], x['title'], x['say']) for x in secs],
             dg=mod.DG, x=mod.X)
    _, i, end = find_page(t)
    t = t[:i] + dump_page(P) + t[end:]
    t = set_chips(t, P)
    return OUT / mod.FILE, t


# ---------- the subject catalog (data/catalog.js) ----------
CATALOG = ROOT / 'data' / 'catalog.js'
NEW_MODULE = dict(id='mt-modern', title='Modern testing practice', emoji='🧭',
                  blurb='How testing works in Agile and DevOps teams today, and how AI is changing the job.')
# where each new page sits: after the topic whose page is named, or in the new module
PLACE = {'static-testing.html': ('after', 'apps-environments.html'), 'specialised-testing.html': ('after', 'non-functional-testing.html'),
         'test-metrics.html': ('after', 'test-plan.html'), 'agile-devops-testing.html': ('module', None), 'ai-in-testing.html': ('module', None)}
INTRO_OLD = "intro: 'Ten chapters that follow the manual testing notes in order"
INTRO_NEW = ("intro: 'Fifteen chapters, from what testing is to the test plan, followed by the newer practices every tester now needs: static testing and reviews, "
             "security, accessibility, localization and mobile testing, estimation and metrics, Agile and DevOps testing, and AI in testing. Every diagram is an animation you can step through, "
             "every idea has an everyday example, and each chapter has hands on labs, quizzes from easy to expert, number practice and a narrator in six languages. "
             "The last chapter collects the interview questions asked most, with hints and full answers.',")


def js(v):
    return json.dumps(v, ensure_ascii=False)


def kw_of(sec_):
    words = [re.sub(r'<[^>]+>', '', b).strip() for b in re.findall(r'<b>(.*?)</b>', sec_['html'])]
    out = []
    for w in [sec_['title']] + words:
        w = H.unescape(w).strip(' .:,"')
        if 2 < len(w) <= 40 and w.lower() not in [x.lower() for x in out]:
            out.append(w)
    return out[:10]


def sec_line(x):
    return f"          {{ id: {js(x['id'])}, title: {js(H.unescape(x['title']))}, emoji: {js(x['emoji'])}, group: 'Lesson', keywords: {js(kw_of(x))} }}, // mt2"


def topic_block(mod):
    secs = mod.SECTIONS
    kws = []
    for x in secs:
        for k in kw_of(x):
            if k.lower() not in [y.lower() for y in kws]:
                kws.append(k)
    lines = ['      { /* mt2-block-start */', f'        id: {js(mod.TOPIC)}, title: {js(mod.TITLE)}, emoji: {js(mod.EMOJI)},',
             f'        page: {js("content/manual-testing/" + mod.FILE)},', f'        summary: {js(mod.DESCRIPTION)},',
             f'        keywords: {js(kws[:24])},', '        added: "2026-10-24",', '        sections: [']
    lines += [sec_line(x).replace(' // mt2', '') for x in secs]
    lines += ["          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },",
              "          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }", '        ]', '      } /* mt2-block-end */']
    return '\n'.join(lines)


def topic_end(t, page):
    i = t.find(f'page: "content/manual-testing/{page}"')
    assert i > 0, page
    j = t.find("{ id: 'numbers'", i)
    k = t.find('\n      }', j) + len('\n      }')
    return k


def update_catalog(pages, adds):
    t = CATALOG.read_text()
    t = re.sub(r',\n    \{ /\* mt2-module-start \*/[\s\S]*?/\* mt2-module-end \*/', '', t)
    t = re.sub(r'(,\n|\n)      \{ /\* mt2-block-start \*/[\s\S]*?\} /\* mt2-block-end \*/', '', t)
    t = '\n'.join(l for l in t.split('\n') if not l.endswith('// mt2'))
    for mod in adds:
        i = t.find(f'page: "content/manual-testing/{mod.FILE}"')
        j = t.find("          { id: 'quiz'", i)
        t = t[:j] + '\n'.join(sec_line(x) for x in mod.SECTIONS) + '\n' + t[j:]
    for mod in pages:
        how, where = PLACE[mod.FILE]
        if how != 'after':
            continue
        k = topic_end(t, where)
        if t[k] == ',':
            t = t[:k + 1] + '\n' + topic_block(mod) + ',' + t[k + 1:]
        else:
            t = t[:k] + ',\n' + topic_block(mod) + t[k:]
    mods = [m for m in pages if PLACE[m.FILE][0] == 'module']
    order = ['agile-devops-testing.html', 'ai-in-testing.html']
    mods.sort(key=lambda m: order.index(m.FILE))
    a = t.find('function mtModules()')
    b = t.find('\n  ];', a)
    block = (',\n    { /* mt2-module-start */\n'
             f'      id: {js(NEW_MODULE["id"])}, title: {js(NEW_MODULE["title"])}, emoji: {js(NEW_MODULE["emoji"])}, blurb: {js(NEW_MODULE["blurb"])},\n'
             '      topics: [\n' + ',\n'.join(topic_block(m) for m in mods) + '\n      ]\n    } /* mt2-module-end */')
    t = t[:b] + block + t[b:]
    if INTRO_OLD in t:
        i = t.find(INTRO_OLD)
        j = t.find("',\n", i) + 3
        t = t[:i] + INTRO_NEW + '\n' + t[j:]
    CATALOG.write_text(t)


def main():
    only_check = '--check' in sys.argv
    outs, pmods, amods = [], [], []
    for p in sorted((HERE / 'pages').glob('*.py')):
        pmods.append(load(p))
        outs.append(build_page(p.stem, pmods[-1]))
    for p in sorted((HERE / 'adds').glob('*.py')):
        amods.append(load(p))
        outs.append(apply_add(p.stem, amods[-1]))
    if '—' in (HERE / 'widgets.js').read_text():
        problems.append('widgets.js: em dash')
    if problems:
        print('\n'.join(problems))
        sys.exit(1)
    if only_check:
        print('checks passed')
        return
    update_catalog(pmods, amods)
    print('wrote data/catalog.js')
    done = {}
    for path, s in outs:
        done[path] = s
    for path in sorted(set(OUT.glob('*.html')) | set(done)):
        if path.name == 'interview-questions.html':
            continue
        s = done.get(path) or path.read_text()
        path.write_text(inject_widgets(s))
        print('wrote', path.relative_to(ROOT))


if __name__ == '__main__':
    main()
