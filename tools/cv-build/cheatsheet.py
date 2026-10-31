"""The subject cheatsheet: one page, and a PDF of it, made only from what the chapters already teach.

Nothing on the cheatsheet is written by hand. While build.py loads the topic files, record() wraps the cvkit
boxes fx(), table() and note() and Kit.lesson(), so every formula card, table and note is captured together with the
lesson it sits in. A box that is built but never placed in a lesson (for example inside a worked problem) is left
out. The page then lists, chapter by chapter:
  Key ideas        the chapter's K.must() points (the Summary tab)
  Formulas         every fx() card, exam favourites marked
  Tables           every table() from the lessons, closed until opened on screen and printed open
  Tips and traps   every note(): Remember, Common mistake and In the exam
Each item links back to the lesson that teaches it.

write(chs, cfg, root) writes content/<subject>/cheatsheet.html and renders content/<subject>/<name>-cheatsheet.pdf with
headless Chromium (tools/cv-build/sheet-pdf.js), so the PDF is a static file that downloads and opens offline.

It also writes the compact cheatsheet, content/<subject>/cheatsheet-compact.html and <name>-cheatsheet-compact.pdf:
only the key ideas, the formulas the chapters mark as exam favourites, and the Common mistake and In the exam
notes, in three narrow columns. The build stops
if its PDF grows past COMPACT_MAX pages.
"""
import html
import os
import re
import subprocess

import cvkit

HERE = os.path.dirname(os.path.abspath(__file__))
_orig = {}
_cur = None


# ---------- recording the boxes while the topic files load ----------
def record():
    """Wrap the cvkit boxes once. Call begin() before a topic file runs and take() after it."""
    if _orig:
        return
    _orig.update(fx=cvkit.fx, note=cvkit.note, table=cvkit.table, lesson=cvkit.Kit.lesson)

    def keep(item):
        if _cur is not None:
            _cur['pend'].append(item)
        return item['html']

    def fx(title, body, note='', key=False):
        return keep({'k': 'fx', 'title': title, 'body': body, 'note': note, 'key': key,
                     'html': _orig['fx'](title, body, note, key)})

    def note(text, kind='tip'):
        return keep({'k': kind, 'text': text, 'html': _orig['note'](text, kind)})

    def table(head, rows, cls=''):
        return keep({'k': 'table', 'head': head, 'rows': rows, 'html': _orig['table'](head, rows, cls)})

    def lesson(self, id, title, html, kw=None):
        if _cur is not None:
            rest = []
            for it in _cur['pend']:
                if it['html'] in html:
                    it.update(lesson=id, ltitle=title)
                    _cur['items'].append(it)
                else:
                    rest.append(it)
            _cur['pend'] = rest
        return _orig['lesson'](self, id, title, html, kw)

    cvkit.fx, cvkit.note, cvkit.table, cvkit.Kit.lesson = fx, note, table, lesson


def begin():
    global _cur
    _cur = {'pend': [], 'items': []}


def take():
    global _cur
    items, _cur = _cur['items'], None
    return items


# ---------- the page ----------
LABEL = {'tip': 'Remember', 'warn': 'Common mistake', 'exam': 'In the exam'}
KINDS = [('must', 'Key ideas'), ('fx', 'Formulas'), ('table', 'Tables'), ('tip', 'Remember'),
         ('warn', 'Common mistakes'), ('exam', 'In the exam')]


COMPACT_MAX = 6


def file_name(cfg, compact=False):
    return re.sub(r'[^a-z0-9]+', '-', cfg['name'].lower()).strip('-') + ('-cheatsheet-compact.pdf' if compact else '-cheatsheet.pdf')


def pdf_label(meta):
    bits = [f'{meta["pages"]} pages' if meta.get('pages') else '', f'{meta["kb"]} KB' if meta.get('kb') else '']
    return 'PDF' + (', ' + ', '.join(b for b in bits if b) if any(bits) else '')


def text_of(s):
    s = re.sub(r'<[^>]+>', ' ', str(s))
    return re.sub(r'\s+', ' ', html.unescape(s)).strip().lower()


def chapter_html(T, seen):
    slug, topic = T['slug'], T['topic']
    items = T.get('sheet', [])

    def back(it):
        return (f'<a class="sh-from" href="./{slug}.html#{it["lesson"]}" data-topic="{topic}" data-h="{it["lesson"]}">'
                f'Lesson: {html.escape(it["ltitle"])}</a>')

    def find(s):
        return html.escape(text_of(s), quote=True)

    blocks = []
    if T['must']:
        lis = ''.join(f'<li class="sh-it" data-kind="must" data-find="{find(t + " " + d)}"><b>{t}</b> {d}</li>' for t, d in T['must'])
        blocks.append(f'<div class="sh-blk"><h4>Key ideas</h4><ul class="sh-must">{lis}</ul></div>')

    fxs, tables, notes = [], [], []
    for it in items:
        if it['k'] == 'fx':
            sig = text_of(it['title'] + '|' + it['body'])
            if sig in seen:
                continue
            seen.add(sig)
            fxs.append(f'<div class="sh-it sh-fxc" data-kind="fx" data-key="{int(bool(it["key"]))}" '
                       f'data-find="{find(it["title"] + " " + it["body"] + " " + it["note"])}">{it["html"]}{back(it)}</div>')
        elif it['k'] == 'table':
            sig = text_of(it['html'])
            if sig in seen:
                continue
            seen.add(sig)
            cap = ' · '.join(text_of(h) for h in it['head'][:4])
            tables.append(f'<details class="sh-it sh-tab" data-kind="table" data-find="{find(it["html"])}" open>'
                          f'<summary><span>Table: {html.escape(cap)}</span></summary>{it["html"]}{back(it)}</details>')
        else:
            notes.append(f'<li class="sh-it note note-{it["k"]}" data-kind="{it["k"]}" data-find="{find(it["text"])}">'
                         f'<b>{LABEL[it["k"]]}</b><div>{it["text"]}{back(it)}</div></li>')
    if fxs:
        blocks.append(f'<div class="sh-blk"><h4>Formulas</h4><div class="sh-fx">{"".join(fxs)}</div></div>')
    if tables:
        blocks.append(f'<div class="sh-blk"><h4>Tables</h4>{"".join(tables)}</div>')
    if notes:
        blocks.append(f'<div class="sh-blk"><h4>Tips and traps</h4><ul class="sh-notes">{"".join(notes)}</ul></div>')
    return (f'<article class="sh-ch" id="{slug}"><header class="sh-chh"><span class="sh-no">{html.escape(T.get("badge", ""))}</span>'
            f'<h3>{html.escape(T["title"])}</h3><a class="sh-open" href="./{slug}.html" data-topic="{topic}" data-h="">Open chapter</a></header>'
            f'<p class="sh-sum">{html.escape(T["summary"])}</p>{"".join(blocks)}</article>')


def page(chs, cfg, meta):
    seen = set()
    steps, order = {}, []
    for T in chs:
        n = T['step'][0]
        if n not in steps:
            steps[n] = (T['step'], [])
            order.append(n)
        steps[n][1].append(T)
    body = []
    for n in order:
        stp, ts = steps[n]
        body.append(f'<section class="sh-step" id="step-{n}"><h2><span>Step {n}</span>{html.escape(stp[1])}</h2>'
                    + ''.join(chapter_html(T, seen) for T in ts) + '</section>')
    body = ''.join(body)
    n_fx = body.count('data-kind="fx"')
    n_tab = body.count('data-kind="table"')
    n_note = sum(body.count(f'data-kind="{k}"') for k in ('tip', 'warn', 'exam'))
    n_must = body.count('data-kind="must"')
    toc = ''.join(f'<a href="#step-{n}"><b>{n}</b>{html.escape(steps[n][0][1])}</a>' for n in order)
    kinds = ''.join(f'<button type="button" class="sh-k" data-k="{k}" aria-pressed="true">{v}</button>' for k, v in KINDS)
    pdf = file_name(cfg)
    size = pdf_label(meta['full'])
    cpages = meta['compact'].get('pages')
    sub = cfg['subject']
    home = 's=' + sub + (f'&amp;p={cfg["part"]}' if cfg.get('part') else '')
    css = '\n'.join(f'<link rel="stylesheet" href="../../assets/{c}">' for c in cfg['css'] + ['sheet.css'])
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cheatsheet · {cfg["name"]}</title>
<meta name="description" content="{cfg["name"]} cheatsheet: every formula, key idea, table, memory aid and common mistake from the {len(chs)} chapters, with a PDF to download.">
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/theme.css">
{css}
</head>
<body class="{cfg["body"]} sheetp" data-subject="{sub}">
<header class="cv-top"><a class="cv-brand" href="../../index.html">Brainy Bytes</a><a class="cv-home" href="../../subject.html?{home}">{cfg["name"]} learning path</a><span class="grow"></span><button type="button" class="cv-theme" id="cvTheme">Dark mode</button></header>
<div class="cv-wrap sh-wrap">
  <div class="cv-crumb"><a class="home-link" href="../../subject.html?{home}" target="_top">{cfg["name"]}</a><span>›</span><span>Cheatsheet</span></div>
  <header class="cv-hero">
    <div class="cv-kicker">Cheatsheet · {len(chs)} chapters on one page</div>
    <h1>{cfg["name"]} cheatsheet</h1>
    <p class="lead">Every formula, key idea, table, memory aid and common mistake from the chapters, gathered in one place for quick revision. Nothing here is new. Each card links back to the lesson that teaches it, so open the lesson when a line does not make sense yet.</p>
    <div class="cv-chips"><span class="cv-chip">{n_must} key ideas</span><span class="cv-chip">{n_fx} formulas</span><span class="cv-chip">{n_tab} tables</span><span class="cv-chip">{n_note} tips and traps</span></div>
    <div class="sh-actions">
      <a class="sh-btn primary" href="./{pdf}" download="{pdf}" type="application/pdf">Download PDF</a>
      <a class="sh-btn" href="./cheatsheet-compact.html" data-topic="cheatsheet-compact" data-h="">Compact version{f", {cpages} pages" if cpages else ""}</a>
      <button type="button" class="sh-btn" id="shPrint">Print or save what is shown</button>
      <span class="sh-meta">{size}. The full cheatsheet, ready to keep offline.</span>
    </div>
  </header>
  <div class="sh-bar" role="search">
    <input type="search" id="shFind" placeholder="Find a formula, word or idea" aria-label="Find in the cheatsheet">
    <div class="sh-kinds" role="group" aria-label="Show these parts">{kinds}</div>
    <label class="sh-fav"><input type="checkbox" id="shFav"> Exam favourite formulas only</label>
    <span class="sh-count" id="shCount" aria-live="polite"></span>
  </div>
  <nav class="sh-toc" aria-label="Steps">{toc}</nav>
  <main id="shBody">{body}</main>
  <p class="sh-none" id="shNone" hidden>Nothing matches. Clear the search box or switch more parts back on.</p>
</div>
<script src="../../assets/fun.js"></script>
<script src="../../assets/sheet.js"></script>
</body>
</html>
'''


def compact_page(chs, cfg, meta):
    seen, steps, order = set(), {}, []
    for T in chs:
        n = T['step'][0]
        if n not in steps:
            steps[n] = (T['step'], [])
            order.append(n)
        steps[n][1].append(T)

    def find(x):
        return html.escape(text_of(x), quote=True)

    n_must = n_fx = n_trap = 0
    body = []
    for n in order:
        stp, ts = steps[n]
        arts = []
        for T in ts:
            musts = ''.join(f'<li class="sh-it" data-kind="must" data-find="{find(t + " " + d)}"><b>{t}</b> {d}</li>' for t, d in T['must'])
            fxs = []
            for it in T.get('sheet', []):
                if it['k'] != 'fx' or not it['key']:
                    continue
                sig = text_of(it['title'] + '|' + it['body'])
                if sig in seen:
                    continue
                seen.add(sig)
                fxs.append(f'<li class="sh-it" data-kind="fx" data-find="{find(it["title"] + " " + it["body"])}">'
                           f'<b>{it["title"]}</b><span class="cs-f">{it["body"]}</span></li>')
            traps = []
            for it in T.get('sheet', []):
                if it['k'] in ('warn', 'exam') and text_of(it['text']) not in seen:
                    seen.add(text_of(it['text']))
                    traps.append(f'<li class="sh-it cs-{it["k"]}" data-kind="{it["k"]}" data-find="{find(it["text"])}">'
                                 f'<b>{"Trap" if it["k"] == "warn" else "Exam"}</b> {it["text"]}</li>')
            if not musts and not fxs and not traps:
                continue
            n_must += len(T['must'])
            n_fx += len(fxs)
            n_trap += len(traps)
            blk = (f'<div class="sh-blk"><ul class="cs-must">{musts}</ul></div>' if musts else '') + \
                  (f'<div class="sh-blk"><ul class="cs-fx">{"".join(fxs)}</ul></div>' if fxs else '') + \
                  (f'<div class="sh-blk"><ul class="cs-trap">{"".join(traps)}</ul></div>' if traps else '')
            arts.append(f'<article class="sh-ch cs-ch" id="{T["slug"]}"><h3><a href="./{T["slug"]}.html" data-topic="{T["topic"]}" data-h="">'
                        f'<span class="sh-no">{html.escape(T.get("badge", ""))}</span>{html.escape(T["title"])}</a></h3>{blk}</article>')
        if arts:
            body.append(f'<section class="sh-step cs-step" id="step-{n}"><h2><span>Step {n}</span>{html.escape(stp[1])}</h2>{"".join(arts)}</section>')
    pdf = file_name(cfg, True)
    sub = cfg['subject']
    home = 's=' + sub + (f'&amp;p={cfg["part"]}' if cfg.get('part') else '')
    css = '\n'.join(f'<link rel="stylesheet" href="../../assets/{c}">' for c in cfg['css'] + ['sheet.css'])
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Compact cheatsheet · {cfg["name"]}</title>
<meta name="description" content="{cfg["name"]} compact cheatsheet: the key ideas, exam favourite formulas and common traps of every chapter in at most {COMPACT_MAX} printed pages, with a PDF to download.">
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/theme.css">
{css}
</head>
<body class="{cfg["body"]} sheetp compactp" data-subject="{sub}">
<header class="cv-top"><a class="cv-brand" href="../../index.html">Brainy Bytes</a><a class="cv-home" href="../../subject.html?{home}">{cfg["name"]} learning path</a><span class="grow"></span><button type="button" class="cv-theme" id="cvTheme">Dark mode</button></header>
<div class="cv-wrap sh-wrap">
  <div class="cv-crumb"><a class="home-link" href="../../subject.html?{home}" target="_top">{cfg["name"]}</a><span>›</span><span>Compact cheatsheet</span></div>
  <header class="cv-hero">
    <div class="cv-kicker">Compact cheatsheet · at most {COMPACT_MAX} printed pages</div>
    <h1>{cfg["name"]} compact cheatsheet</h1>
    <p class="lead">The key ideas, the exam favourite formulas and the common traps of every chapter, packed tight for the last look before an exam. It keeps only what the chapters mark as most important. The full cheatsheet has every formula, table and tip.</p>
    <div class="cv-chips"><span class="cv-chip">{n_must} key ideas</span><span class="cv-chip">{n_fx} exam favourite formulas</span><span class="cv-chip">{n_trap} traps and exam tips</span></div>
    <div class="sh-actions">
      <a class="sh-btn primary" href="./{pdf}" download="{pdf}" type="application/pdf">Download PDF</a>
      <a class="sh-btn" href="./cheatsheet.html" data-topic="cheatsheet" data-h="">Full cheatsheet</a>
      <button type="button" class="sh-btn" id="shPrint">Print</button>
      <span class="sh-meta">{pdf_label(meta["compact"])}. Ready to keep offline.</span>
    </div>
  </header>
  <div class="sh-bar" role="search">
    <input type="search" id="shFind" placeholder="Find a formula, word or idea" aria-label="Find in the compact cheatsheet">
    <span class="sh-count" id="shCount" aria-live="polite"></span>
  </div>
  <main id="shBody" class="cs-cols">{"".join(body)}</main>
  <p class="sh-none" id="shNone" hidden>Nothing matches. Clear the search box.</p>
</div>
<script src="../../assets/fun.js"></script>
<script src="../../assets/sheet.js"></script>
</body>
</html>
'''


def render(src, pdf, title):
    """Render one page to its PDF. Returns {'pages', 'kb'}, or None when node or playwright is missing."""
    r = subprocess.run(['node', os.path.join(HERE, 'sheet-pdf.js'), src, pdf, title], capture_output=True, text=True)
    if r.returncode:
        print(f'cheatsheet: {os.path.basename(src)} written, but its PDF was not made (needs node and playwright):\n{r.stderr.strip()[-600:]}')
        return None
    m = re.match(r'(\d+) pages', r.stdout.strip())
    return {'pages': int(m.group(1)) if m else 0, 'kb': os.path.getsize(pdf) // 1024}


def write(chs, cfg, root):
    out = os.path.join(root, 'content', cfg['subject'])
    full, comp = os.path.join(out, 'cheatsheet.html'), os.path.join(out, 'cheatsheet-compact.html')
    pdf, cpdf = os.path.join(out, file_name(cfg)), os.path.join(out, file_name(cfg, True))
    old = lambda f: {'kb': os.path.getsize(f) // 1024} if os.path.exists(f) else {}
    meta = {'full': old(pdf), 'compact': old(cpdf)}
    open(full, 'w', encoding='utf-8').write(page(chs, cfg, meta))
    open(comp, 'w', encoding='utf-8').write(compact_page(chs, cfg, meta))
    a = render(full, pdf, cfg['name'] + ' cheatsheet')
    b = render(comp, cpdf, cfg['name'] + ' compact cheatsheet')
    if not a or not b:
        return
    meta = {'full': a, 'compact': b}
    open(full, 'w', encoding='utf-8').write(page(chs, cfg, meta))
    open(comp, 'w', encoding='utf-8').write(compact_page(chs, cfg, meta))
    for f, p, m in ((full, pdf, a), (comp, cpdf, b)):
        print(f'cheatsheet: {os.path.relpath(f, root)} and {os.path.relpath(p, root)} ({m["pages"]} pages, {m["kb"]} KB)')
    if b['pages'] > COMPACT_MAX:
        raise SystemExit(f'the compact cheatsheet PDF has {b["pages"]} pages, the limit is {COMPACT_MAX}. Tighten the print rules in assets/sheet.css.')
