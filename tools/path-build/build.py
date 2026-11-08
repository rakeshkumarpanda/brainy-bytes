"""Give an older subject the look and the extras of the Python subject, without rewriting its chapters.

The chapters of DSA, Manual Testing, Java, TestNG, JavaScript, Master the Claude, Playwright and Maths for ML were
written by their own builders before the Python subject existed. They all share one page shape: a hero, a row of part
links, a comic, the parts (section.jsec), Real life, Practice, Quiz and Number crunch. For each subject this tool:

  1. reads the subject from data/catalog.js (asPath() there already numbers its steps like the Python learning path)
  2. reads every chapter page and counts its lessons, quiz questions, worked problems, practice tasks and minutes,
     and writes them into the pathMeta() block of data/catalog.js, so the learning path shows the same numbers
     as the Python one
  3. adds assets/pathskin.css and assets/pathskin.js to every chapter page. They switch the page to the Python
     chapter layout (tabs, one lesson at a time) and the script tag tells it the step, the level and the link to
     the chapter on the cheatsheet
  4. writes the full and compact cheatsheets with their PDFs through tools/cv-build/cheatsheet.py, from what the
     chapters already teach: the key idea of every lesson, formulas and rules, short code examples, tables,
     tips, common mistakes and exam notes. Nothing on a cheatsheet is written by hand.

Usage:  python3 tools/path-build/build.py <subject id> [...]     (or: all)
        --no-sheet   skip the cheatsheets (steps 1 to 3 only)
Needs:  beautifulsoup4, node with playwright (for the PDFs, the same as the other cheatsheets).
Run it again after any chapter of the subject is rebuilt by its own builder, because that rewrites the page without
the two pathskin tags.
"""
import html
import json
import os
import re
import subprocess
import sys

from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'cv-build'))
import cheatsheet  # noqa: E402

# name: shown on the cheatsheet. dir: the folder under content/. code: short code examples go on the cheatsheet.
# sheet: False when the subject already has its own cheatsheets (Playwright has one per language).
SUBJECTS = {
    'dsa': {'name': 'Data Structures and Algorithms', 'dir': 'dsa', 'badge': 'DSA', 'code': False, 'compact_max': 8},
    'manual-testing': {'name': 'Manual Testing', 'dir': 'manual-testing', 'badge': 'MT', 'code': False, 'compact_max': 8},
    'java': {'name': 'Java', 'dir': 'java', 'badge': 'JAVA', 'code': True, 'compact_max': 12},
    'testng': {'name': 'TestNG', 'dir': 'testng', 'badge': 'TNG', 'code': True},
    'javascript': {'name': 'JavaScript and TypeScript', 'dir': 'javascript', 'badge': 'JS', 'code': True, 'compact_max': 12},
    'master-claude': {'name': 'Master the Claude', 'dir': 'claude', 'badge': 'AI', 'code': True, 'compact_max': 8},
    'playwright': {'name': 'Playwright', 'dir': 'playwright', 'badge': 'PW', 'code': True, 'sheet': False, 'sheet_link': './cheatsheet.html'},
    'api-manual-testing': {'name': 'Manual API Testing', 'dir': 'api-testing', 'badge': 'API', 'code': False},
    'ml-maths': {'name': 'Maths for Machine Learning', 'dir': 'ml-maths', 'badge': 'MATH', 'code': False, 'compact_max': 8},
}
MARK = '<!-- pathskin -->'
META_START, META_END = '/* path-build meta: start */', '/* path-build meta: end */'


def catalog(sid):
    r = subprocess.run(['node', os.path.join(HERE, 'catalog-dump.js'), sid], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def clean(s):
    return re.sub(r'\s+', ' ', s or '').strip()


def short(t, n=260):
    t = clean(t)
    if len(t) <= n:
        return t
    cut = t[:n]
    end = cut.rfind('. ')
    return cut[:end + 1] if end > 80 else re.sub(r'\s+\S*$', '', cut) + ' ...'


def inner(tag):
    return ''.join(str(c) for c in tag.contents)


def part_title(sec):
    h = sec.find('h2')
    if not h:
        return sec.get('id', '')
    spans = h.find_all('span', recursive=False)
    return clean((spans[-1] if spans else h).get_text())


INSTR = re.compile(r'^(explore|press|click|tap|try|drag|pick|type|use the|step through|change|move|watch|choose|play|open|run)\b', re.I)


def text_of(tag):
    """Plain text of a tag, with fractions written as (a)/(b) instead of running both parts together."""
    t = BeautifulSoup(str(tag), 'html.parser')
    for f in t.select('.fr'):
        s = f.find_all('span', recursive=False)
        if len(s) == 2:
            f.replace_with(f'({clean(s[0].get_text())})/({clean(s[1].get_text())})')
    return clean(t.get_text(' '))


def key_idea(sec):
    """The one idea to keep from a lesson: its first real paragraph (not an instruction for an animation),
    or its rule box when it has no such paragraph. The same rule as the Summary tab of assets/pathskin.js."""
    p = next((t for t in (text_of(p) for p in sec.find_all('p', recursive=False)) if len(t) > 40 and not INSTR.match(t)), '')
    if p:
        return short(p)
    rule = sec.find(class_='rule')
    return short(text_of(rule)) if rule else ''


def chip_number(chips, *words):
    for c in chips:
        for w in words:
            m = re.search(r'(\d[\d,]*)\s+' + w, c)
            if m:
                return int(m.group(1).replace(',', ''))
    return 0


def minutes_of(chips):
    for c in chips:
        m = re.search(r'About\s+(\d+)\s*min', c)
        if m:
            return int(m.group(1))
        m = re.search(r'About\s+(\d+(?:\.\d+)?)\s*hours?', c)
        if m:
            return round(float(m.group(1)) * 60)
    return 0


def table_item(tw):
    t = tw.find('table')
    rows = t.find_all('tr') if t else []
    if len(rows) < 2:
        return None
    head = [inner(c) for c in rows[0].find_all(['th', 'td'])]
    body = [[inner(c) for c in r.find_all(['th', 'td'])] for r in rows[1:]]
    return {'k': 'table', 'head': head, 'rows': body, 'html': cheatsheet.cvkit.table(head, body)}


def code_item(sec, lesson):
    """The first short runnable example of a lesson, as a card with highlighted code."""
    for cw in sec.find_all(class_='codewrap'):
        pre = cw.find('pre', class_='src')
        if not pre:
            continue
        lines = pre.get_text().rstrip('\n').split('\n')
        if not 2 <= len(lines) <= 10 or max(len(x) for x in lines) > 90:
            continue
        lbl = cw.find(class_='lbl')
        title = clean(re.split(r'\s+·\s+', lbl.get_text())[0]) if lbl else lesson
        body = f'<pre class="ls-pre">{inner(pre).rstrip()}</pre>'
        return {'k': 'fx', 'title': html.escape(title), 'body': body, 'note': '', 'key': False,
                'html': cheatsheet.cvkit.fx(html.escape(title), body)}
    return None


JS_STR = r"'((?:[^'\\]|\\.)*)'"


def js_entries(src, call):
    """The object literals passed to call({...}) in a page script, cut at the next call."""
    starts = [m.start() for m in re.finditer(re.escape(call) + r'\(\{', src)]
    return [src[a:(starts[i + 1] if i + 1 < len(starts) else len(src))] for i, a in enumerate(starts)]


def js_field(block, name, kind='str'):
    m = re.search(r'\b' + name + r':\s*' + (JS_STR if kind == 'str' else r'`((?:[^`\\]|\\.)*)`'), block, re.S)
    return m.group(1).replace("\\'", "'") if m else ''


def app_chapter(src, info):
    """The two DSA pages that are apps of their own (Mathematics in DSA and Array Adventure) keep their layout.
    Their lessons live in a script as P({...}) or T({...}) calls, so the cheatsheet reads them from there."""
    T = {'slug': '', 'topic': info['id'], 'title': info['title'], 'summary': info['summary'], 'badge': info['badge'],
         'step': (info['step'], info['step_title']), 'must': [], 'sheet': []}
    probs, lessons = js_entries(src, 'P'), js_entries(src, 'T')
    for b in probs:
        pid, title = js_field(b, 'id'), js_field(b, 'title')
        opt = re.search(r'opt:\s*\{\s*name:\s*' + JS_STR + r'.*?time:\s*' + JS_STR, b, re.S)
        naive = re.search(r'naive:\s*\{\s*name:\s*' + JS_STR + r'.*?time:\s*' + JS_STR, b, re.S)
        if opt:
            idea = f'{opt.group(1)}: {opt.group(2)}' + (f', against {naive.group(2)} for {naive.group(1).lower()}' if naive else '') + '.'
            T['must'].append((html.escape(title), html.escape(idea.replace("\\'", "'"))))
        boxes = re.findall(r'<div class="mathbox">(.*?)</div>', js_field(b, 'formula', 'tpl'), re.S)
        for i, body in enumerate(boxes):
            T['sheet'].append({'k': 'fx', 'title': html.escape(title), 'body': body, 'note': '', 'key': i == 0,
                               'html': cheatsheet.cvkit.fx(html.escape(title), body, '', i == 0), 'lesson': pid, 'ltitle': title})
    for b in lessons:
        lid, title = js_field(b, 'id'), js_field(b, 'title')
        notes = re.findall(r'<li>(.*?)</li>', js_field(b, 'notes', 'tpl'), re.S)
        if notes:
            T['must'].append((html.escape(title), clean(notes[0])))
        for n in notes[1:]:
            T['sheet'].append({'k': 'tip', 'text': clean(n), 'html': cheatsheet.cvkit.note(clean(n)), 'lesson': lid, 'ltitle': title})
    return T, len(probs) + len(lessons)


def chapter(path, info, cfg):
    """Read one chapter page. Returns the counts for the learning path and the cheatsheet entry."""
    src = open(path, encoding='utf-8').read()
    if 'section class="card reveal jsec' not in src and re.search(r'\b[PT]\(\{', src):
        T, n = app_chapter(src, info)
        T['slug'] = os.path.basename(path)[:-5]
        m = re.search(r'(\d+) practice problems', info['summary'])
        counts = {'lessons': n}
        if m:
            counts['assign'] = int(m.group(1))
        return {'minutes': 0, 'counts': counts}, T
    soup = BeautifulSoup(src, 'html.parser')
    hero = soup.find('header', class_='hero')
    parts = soup.select('section.jsec')
    chips = [clean(c.get_text()) for c in (hero.select('.chip') if hero else [])]
    counts = {'lessons': len(parts), 'problems': chip_number(chips, 'calculations?'),
              'quiz': chip_number(chips, 'quiz questions?'),
              'assign': chip_number(chips, 'practice problems?', 'practice tasks?', 'hands-on exercises?', 'exercises?', 'labs?')}
    meta = {'minutes': minutes_of(chips), 'counts': {k: v for k, v in counts.items() if v}}
    if not parts:
        return meta, None
    lead = hero.find(class_='lead') if hero else None
    T = {'slug': os.path.basename(path)[:-5], 'topic': info['id'], 'title': info['title'],
         'summary': clean(lead.get_text()) if lead else info['summary'], 'badge': info['badge'],
         'step': (info['step'], info['step_title']), 'must': [], 'sheet': []}
    seen_eq = set()
    for sec in parts:
        lid, ltitle = sec.get('id'), part_title(sec)
        T['must'].append((html.escape(ltitle), html.escape(key_idea(sec))))
        first = True
        items = []
        for card in sec.select('.fx'):
            h, b, n = card.find(class_='fx-h'), card.find(class_='fx-b'), card.find(class_='fx-n')
            if not b:
                continue
            title = inner(h) if h else html.escape(ltitle)
            items.append({'k': 'fx', 'title': title, 'body': inner(b), 'note': inner(n) if n else '', 'key': first,
                          'html': cheatsheet.cvkit.fx(title, inner(b), inner(n) if n else '', first)})
            first = False
        for eq in sec.select('.eq'):
            if eq.find_parent(class_='fx'):
                continue
            body = inner(eq)
            sig = clean(eq.get_text())
            if sig in seen_eq or len(sig) < 3:
                continue
            seen_eq.add(sig)
            box = eq.find_parent(class_=['box', 'rule', 'deep'])
            h = box.find(['h4']) if box else None
            title = html.escape(clean(h.get_text()) if h else ltitle)
            items.append({'k': 'fx', 'title': title, 'body': body, 'note': '', 'key': first,
                          'html': cheatsheet.cvkit.fx(title, body, '', first)})
            first = False
        if cfg.get('code'):
            c = code_item(sec, ltitle)
            if c:
                items.append(c)
        for tw in sec.select('.tw'):
            if tw.find_parent(class_='tw'):
                continue
            t = table_item(tw)
            if t:
                items.append(t)
        rule = sec.find(class_='rule')
        if rule and clean(rule.get_text()) and short(text_of(rule)) != T['must'][-1][1]:
            text = inner(rule).strip()
            items.append({'k': 'tip', 'text': text, 'html': cheatsheet.cvkit.note(text, 'tip')})
        for kind, cls in (('tip', 'tip'), ('tip', 'trick'), ('warn', 'warn'), ('exam', 'exam')):
            for d in sec.find_all('div', class_=cls):
                if d.get('class') != [cls]:
                    continue
                text = inner(d).strip()
                items.append({'k': kind, 'text': text, 'html': cheatsheet.cvkit.note(text, kind)})
        for it in items:
            it.update(lesson=lid, ltitle=ltitle)
        T['sheet'] += items
    return meta, T


def inject(path, kicker, sheet_href):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'\n?' + re.escape(MARK) + r'[^\n]*', '', s)
    css = f'{MARK}<link rel="stylesheet" href="../../assets/pathskin.css">'
    data = f' data-kicker="{html.escape(kicker, quote=True)}"' + (f' data-sheet="{sheet_href}"' if sheet_href else '')
    js = f'{MARK}<script src="../../assets/pathskin.js"{data}></script>'
    s = s.replace('</head>', css + '\n</head>', 1)
    i = s.rfind('</body>')
    s = s[:i] + js + '\n' + s[i:]
    open(path, 'w', encoding='utf-8').write(s)


def write_meta(sid, meta):
    p = os.path.join(ROOT, 'data', 'catalog.js')
    src = open(p, encoding='utf-8').read()
    a, b = src.index(META_START), src.index(META_END)
    m = re.search(r'return (\{.*\});', src[a:b], re.S)
    allm = json.loads(m.group(1)) if m else {}
    allm[sid] = meta
    body = json.dumps(allm, separators=(',', ':'), sort_keys=True)
    block = f'{META_START}\nfunction pathMeta() {{\n  return {body};\n}}\n'
    open(p, 'w', encoding='utf-8').write(src[:a] + block + src[b:])


def build(sid, sheet=True):
    cfg = SUBJECTS[sid]
    cat = catalog(sid)
    if cat['layout'] != 'path':
        raise SystemExit(f'{sid}: give it layout: \'path\' and asPath() in data/catalog.js first')
    want_sheet = sheet and cfg.get('sheet', True)
    meta, chs = {}, []
    for m in cat['modules']:
        if not m['step']:
            continue
        ready = [t for t in m['topics'] if not t['soon'] and t['page']]
        for i, t in enumerate(ready):
            path = os.path.join(ROOT, t['page'])
            if not os.path.exists(path):
                print(f'{sid}: missing page {t["page"]}')
                continue
            info = dict(t, step=m['step'], step_title=m['title'], badge=f'{m["step"]}.{i + 1}')
            tm, T = chapter(path, info, cfg)
            meta[t['id']] = tm
            kicker = f'Step {m["step"]} · Topic {i + 1} of {len(ready)}' + (f' · {m["level"]}' if m['level'] else '')
            slug = os.path.basename(path)[:-5]
            if T:
                chs.append(T)
            if T and T['must'] and 'section class="card reveal jsec' in open(path, encoding='utf-8').read():
                inject(path, kicker, f'./cheatsheet.html#{slug}' if want_sheet else cfg.get('sheet_link', ''))
            else:
                print(f'{sid}: {t["page"]} has its own layout, kept as it is')
    write_meta(sid, meta)
    n_l = sum(x['counts'].get('lessons', 0) for x in meta.values())
    print(f'{sid}: {len(meta)} chapters, {n_l} lessons, {len(chs)} chapters on the cheatsheet')
    if want_sheet and chs:
        sc = {'subject': sid, 'dir': cfg['dir'], 'name': cfg['name'], 'badge': cfg['badge'],
              'css': ['cv.css'], 'body': 'cvp langp', 'compact_max': cfg.get('compact_max', cheatsheet.COMPACT_MAX)}
        cheatsheet.write(chs, sc, ROOT)


def main():
    args = sys.argv[1:]
    sheet = '--no-sheet' not in args
    args = [a for a in args if a != '--no-sheet']
    if args == ['all']:
        args = list(SUBJECTS)
    if not args:
        raise SystemExit(__doc__)
    for sid in args:
        build(sid, sheet)


if __name__ == '__main__':
    main()
