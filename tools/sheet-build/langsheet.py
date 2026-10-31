"""Cheatsheets for one programming language at a time, for the Selenium and Playwright subjects.

Selenium teaches every example in Java, Python and JavaScript, and Playwright in Java, Python, JavaScript and
TypeScript. A learner works in one language, so each language gets its own cheatsheet, full and compact, each with a
PDF. A sheet shows only that language's code, so nobody needs another language's sheet.

Nothing on a sheet is written by hand. Everything comes from the chapter topic files:

  Selenium (tools/se-build/topics)
    Key ideas      the chapter's K.must() points
    Code           every annotated line of every example in this language, with its line note
    Numbers        the fx() cards (defaults, timeouts, the Grid sum)
    Tables         every table() from the lessons, with the columns and rows for other languages taken out
    Tips and traps every note(): Remember, Common mistake and In the exam
  Playwright (tools/pw-build/topics)
    Key ideas      the chapter's picture panels and its "remember" line
    Code           every example program in this language (full sheet), and its commented lines and the lines of
                   its recorded walks (compact sheet)
    Tables         every table from the lessons, filtered the same way
    Tips and traps the tip, warn, pro and new boxes, with text for other languages taken out

Text that names only other languages (a note about Python on the Java sheet) is left out as well.

Files written into content/<subject>/:
    cheatsheet.html                                     pick your language, links to every sheet and PDF
    cheatsheet-<lang>.html, <subject>-<lang>-cheatsheet.pdf
    cheatsheet-<lang>-compact.html, <subject>-<lang>-cheatsheet-compact.pdf   (the build stops past COMPACT_MAX pages)

Usage:  python3 tools/sheet-build/langsheet.py [selenium] [playwright]     (no name builds both)
The PDFs are rendered by tools/cv-build/sheet-pdf.js (node with playwright).
"""
import html
import importlib.util
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(ROOT, 'tools')
COMPACT_MAX = 6

SUBJECTS = {
    'selenium': {'name': 'Selenium', 'langs': [('java', 'Java'), ('py', 'Python'), ('js', 'JavaScript')], 'badge': 'SE'},
    'playwright': {'name': 'Playwright', 'langs': [('java', 'Java'), ('py', 'Python'), ('js', 'JavaScript'), ('ts', 'TypeScript')],
                   'badge': 'PW'},
}

# Words that tie a table column, a table row or a sentence to one language.
TERMS = {
    'java': [r'\bJava\b', r'JUnit', r'TestNG', r'\bMaven\b', r'@UsePlaywright'],
    'py': [r'Python', r'\bpytest'],
    'js': [r'JavaScript', r'\bMocha\b', r'Playwright Test', r'\bJS\b'],
    'ts': [r'TypeScript', r'Playwright Test', r'\bTS\b'],
    'cs': [r'C#', r'\.NET\b', r'\bNUnit\b', r'\bMSTest\b'],
}


def langs_in(s):
    t = re.sub(r'<[^>]+>', ' ', str(s))
    return {k for k, pats in TERMS.items() if any(re.search(p, t) for p in pats)}


def mine(found, lang, fallback=False):
    """True when text tagged with the languages in found belongs on the sheet for lang."""
    if not found or lang in found:
        return True
    return fallback and lang == 'ts' and 'js' in found


def text_of(s):
    s = re.sub(r'<[^>]+>', ' ', str(s))
    return re.sub(r'\s+', ' ', html.unescape(s)).strip().lower()


def find(s):
    return html.escape(text_of(s), quote=True)


def only_lang(s, lang):
    """Keep the by() text for lang and drop the text for every other language."""
    s = re.sub(r'<span class="only-(\w+)">([\s\S]*?)</span>', lambda m: m.group(2) if m.group(1) == lang else '', s)
    return re.sub(r'\s{2,}', ' ', s)


NAMES = {'Java': 'java', 'Python': 'py', 'JavaScript': 'js', 'TypeScript': 'ts', 'C#': 'cs'}


def trim(text, lang):
    """Take the other languages out of sentences that name languages in turn.
       "Java: x. Python: y."                 keeps only the sentence for lang
       "Defaults: Java 500 ms, Python 0.5 s"  keeps only the part for lang after the colon
       "JavaScript waits forever."           a sentence that starts with another language is left out,
                                             and a note whose first sentence does that is left out whole
    A sentence that names lang next to others, such as a comparison, stays as it is."""
    out = []
    for i, s in enumerate(re.split(r'(?<=\.)\s+(?=[A-Z<])', text)):
        found = langs_in(s)
        lead = langs_in(' '.join(re.sub(r'<[^>]+>', ' ', s).split()[:3]))
        if found and not mine(found, lang, True) and (lead or '<code>' in s):
            continue
        if lead and not mine(lead, lang, True):
            if i == 0:
                return ''  # the whole note is about another language
            continue
        m = re.match(r'^(Java|Python|JavaScript|TypeScript|C#)(?:\s+[\d.]+\+?)?(?:\s*\([^)]*\))?:', s)
        if ':' in s and not m:
            head, tail = s.split(':', 1)
            end = '.' if tail.rstrip().endswith('.') else ''
            bits = re.split(r'(,\s+(?:or\s+|and\s+)?|\s+or\s+(?=[A-Z<a]))', tail.strip().rstrip('.'))
            parts, seps = bits[0::2], [''] + bits[1::2]
            tags = [langs_in(c) for c in parts]
            tagged = [t for t in tags if t]
            if len(tagged) >= 2 and len(set().union(*tagged)) >= 2 and all(len(t) == 1 for t in tagged) \
                    and any(t and mine(t, lang, True) for t in tags):
                kept = [(sp, c) for sp, c, t in zip(seps, parts, tags) if mine(t, lang, True)]
                s = head + ': ' + kept[0][1] + ''.join(sp + c for sp, c in kept[1:]) + end
        out.append(s)
    return ' '.join(out)


def note_ok(text, lang):
    return mine(langs_in(text), lang, fallback=True)


def filter_table(head, rows, lang):
    """Drop the columns and rows that belong to other languages. Returns (head, rows) or None when nothing is left."""
    tags = [langs_in(h) for h in head]
    has_mine = any(lang in t for t in tags)
    fb = lang == 'ts' and not has_mine
    keep = [i for i, t in enumerate(tags) if mine(t, lang, fb)]
    if len(keep) < 2:
        return None
    rtags = [langs_in(r[0]) if r else set() for r in rows]
    rfb = lang == 'ts' and not any(lang in t for t in rtags)
    out = [[r[i] if i < len(r) else '' for i in keep] for r, t in zip(rows, rtags) if mine(t, lang, rfb)]
    if not out:
        return None
    return [head[i] for i in keep], out


def table_html(head, rows):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'<div class="tw"><table class="cvt"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def load_pw_build():
    """tools/pw-build/build.py, for its topic loader and its syntax colouring."""
    if 'pwbuild' in sys.modules:
        return sys.modules['pwbuild']
    d = os.path.join(TOOLS, 'pw-build')
    if d not in sys.path:
        sys.path.insert(0, d)
    spec = importlib.util.spec_from_file_location('pwbuild', os.path.join(d, 'build.py'))
    m = importlib.util.module_from_spec(spec)
    sys.modules['pwbuild'] = m
    spec.loader.exec_module(m)
    return m


def hl(code, lang):
    return load_pw_build().hl(code, lang)


# ---------- Selenium: the chapters as cv-build loads them, plus every example's code and line notes ----------
_se_cache = []  # the topic files run once per process, since an example key may only be written once


def selenium_chapters():
    cv = os.path.join(TOOLS, 'cv-build')
    se = os.path.join(TOOLS, 'se-build')
    if cv not in sys.path:
        sys.path.insert(0, cv)
    import build as B
    import cheatsheet
    if se not in sys.path:
        sys.path.append(se)
    import sekit
    B.CFG.update({'subject': 'selenium', 'name': 'Selenium', 'topics': os.path.join(se, 'topics')})

    if not getattr(sekit, '_sheet_wrapped', False):
        tri0, solo0 = sekit.tri, sekit.solo

        def lines_of(src):
            code, notes = sekit._split(src, 'cheatsheet')
            ls = code.split('\n')
            return [(ls[n - 1].strip(), t) for n, t in notes]

        def keep(item):
            if cheatsheet._cur is not None:
                cheatsheet._cur['pend'].append(item)
            return item['html']

        def tri(key, title, java, py, js, mode='script', needs=None, extra=None, fail=False, expect=None):
            h = tri0(key, title, java=java, py=py, js=js, mode=mode, needs=needs, extra=extra, fail=fail, expect=expect)
            per = {}
            for lang, src in (('java', java), ('py', py), ('js', js)):
                ls = []
                for s in ((extra or {}).get(lang) or {}).values():
                    ls += lines_of(s)
                per[lang] = ls + lines_of(src)
            return keep({'k': 'code', 'title': title, 'per': per, 'html': h})

        def solo(key, title, lang, src, mode='script', needs=None, fail=False, expect=None, why=''):
            h = solo0(key, title, lang, src, mode=mode, needs=needs, fail=fail, expect=expect, why=why)
            return keep({'k': 'code', 'title': title, 'per': {lang: lines_of(src)}, 'html': h})

        sekit.tri, sekit.solo = tri, solo
        sekit._sheet_wrapped = True
    if not _se_cache:
        _se_cache.extend(B.chapters())
    return _se_cache


def selenium_sheet(lang):
    """The chapters of one language's Selenium sheet, in the shape render() reads."""
    out = []
    for T in selenium_chapters():
        ch = {'slug': T['slug'], 'topic': T['topic'], 'title': T['title'], 'badge': T.get('badge', ''),
              'step': T['step'], 'summary': T['summary'], 'must': [], 'items': []}
        ch['must'] = [(t, trim(d, lang)) for t, d in T['must'] if trim(d, lang) and note_ok(t + ' ' + trim(d, lang), lang)]
        for it in T.get('sheet', []):
            base = {'lesson': it['lesson'], 'ltitle': it['ltitle']}
            if it['k'] == 'code':
                ls = it['per'].get(lang)
                if ls:
                    ch['items'].append({**base, 'k': 'code', 'title': it['title'], 'lines': ls, 'lang': lang})
            elif it['k'] == 'fx':
                if note_ok(it['title'] + ' ' + it['body'] + ' ' + it['note'], lang):
                    ch['items'].append({**base, 'k': 'fx', 'title': it['title'], 'body': it['body'], 'key': it['key'], 'html': it['html']})
            elif it['k'] == 'table':
                ft = filter_table(it['head'], it['rows'], lang)
                if ft:
                    ch['items'].append({**base, 'k': 'table', 'head': ft[0], 'rows': ft[1]})
            elif trim(it['text'], lang) and note_ok(trim(it['text'], lang), lang):
                ch['items'].append({**base, 'k': it['k'], 'text': trim(it['text'], lang)})
        out.append(ch)
    return out


# ---------- Playwright: parts, boxes and examples from the topic files ----------
PW_KIND = {'tip': 'tip', 'warn': 'warn', 'pro': 'pro', 'new': 'new'}
COMMENT = {'py': '#', 'java': '//', 'js': '//', 'ts': '//'}


def commented(code, lang):
    """Lines that end with a comment: (code, comment)."""
    mark = re.escape(COMMENT[lang])
    out = []
    for ln in code.split('\n'):
        m = re.match(r'^\s*(\S.*?)\s{2,}' + mark + r'\s+(.+)$', ln)
        if m and not m.group(1).startswith(COMMENT[lang]):
            out.append((m.group(1).rstrip(), m.group(2).strip()))
    return out


def pw_table(tbl):
    head = re.findall(r'<th>([\s\S]*?)</th>', re.search(r'<tr>([\s\S]*?)</tr>', tbl).group(1))
    rows = [re.findall(r'<td>([\s\S]*?)</td>', r) for r in re.findall(r'<tr>([\s\S]*?)</tr>', tbl)[1:]]
    return head, rows


def playwright_sheet(lang):
    PB = load_pw_build()
    out, mods = [], []
    for T in PB.all_topics():
        if T['module'] not in mods:
            mods.append(T['module'])
        n = mods.index(T['module']) + 1
        ch = {'slug': T['slug'], 'topic': T['slug'], 'title': T['title'], 'badge': f'{n}.{sum(1 for c in out if c["step"][0] == n) + 1}',
              'step': (n, T['module'][1]), 'summary': T['summary'], 'must': [], 'items': []}
        info = T.get('info') or {}
        for p in info.get('panels', []):
            t = trim(f'{p["t"]} {p.get("more", "")}'.strip(), lang)
            if note_ok(p['h'] + ' ' + t, lang):
                ch['must'].append((p['h'], t))
        if info.get('remember'):
            ch['must'].append(('Remember', info['remember']))
        for p in T['parts']:
            base = {'lesson': p['id'], 'ltitle': p['title']}
            pat = (r'\[\[(\w+)\]\]|<div class="tw"><table class="jt[^"]*">[\s\S]*?</table></div>'
                   r'|<div class="pw-box pw-(\w+)"><span class="pw-ic">[^<]*</span><div>([\s\S]*?)</div></div>')
            for m in re.finditer(pat, p['html']):
                if m.group(1):
                    ex = T['codes'].get(m.group(1))
                    if not ex:
                        continue
                    if ex['t'] == 'walk':
                        ls = [(s[lang].strip(), s['cap']) for s in ex['steps'] if s.get(lang)]
                        if ls:
                            ch['items'].append({**base, 'k': 'code', 'title': ex['title'], 'lines': ls, 'lang': lang})
                        continue
                    sp = ex['langs'].get(lang)
                    if sp is None:
                        # files every language shares, such as a CI workflow, go on every sheet
                        others = [s for k, s in ex['langs'].items() if k not in ('java', 'py', 'js', 'ts', 'cs')]
                        if not others:
                            continue
                        sp = others[0]
                    files = [(f, sp['files'][f], PB.lang_of(f, sp['lang'] if sp['lang'] in COMMENT else 'text')) for f in sp['show'] if f in sp['files']]
                    lines = []
                    if sp['lang'] == lang:
                        for f, c, lg in files:
                            if lg == lang:
                                lines += commented(c, lang)
                    ch['items'].append({**base, 'k': 'prog', 'title': ex['label'], 'files': files, 'cmd': sp.get('shown_cmd') or '',
                                        'lines': lines, 'lang': lang})
                elif m.group(2):
                    kind = PW_KIND.get(m.group(2))
                    text = trim(only_lang(m.group(3), lang).strip(), lang)
                    if kind and text and note_ok(text, lang):  # trim() gives '' for a note about another language
                        ch['items'].append({**base, 'k': kind, 'text': text})
                else:
                    head, rows = pw_table(only_lang(m.group(0), lang))
                    ft = filter_table(head, rows, lang)
                    if ft:
                        ch['items'].append({**base, 'k': 'table', 'head': ft[0], 'rows': ft[1]})
        out.append(ch)
    return out


SHEET = {'selenium': selenium_sheet, 'playwright': playwright_sheet}


# ---------- the pages ----------
LABEL = {'tip': 'Remember', 'warn': 'Common mistake', 'exam': 'In the exam', 'pro': 'In real teams', 'new': 'New in Playwright'}
KINDS = [('must', 'Key ideas'), ('code', 'Code'), ('fx', 'Numbers'), ('table', 'Tables'), ('tip', 'Remember'),
         ('pro', 'In real teams'), ('new', 'New'), ('warn', 'Common mistakes'), ('exam', 'In the exam')]
HEAD_FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@500;600;700;800&family=JetBrains+Mono:wght@500;700'
              '&display=swap" rel="stylesheet">')


def slug_name(sid, lang, compact=False):
    return f'cheatsheet-{lang}' + ('-compact' if compact else '')


def pdf_name(sid, lang, compact=False):
    return f'{sid}-{lang}-cheatsheet' + ('-compact' if compact else '') + '.pdf'


def pdf_label(meta):
    bits = [f'{meta["pages"]} pages' if meta.get('pages') else '', f'{meta["kb"]} KB' if meta.get('kb') else '']
    return 'PDF' + (', ' + ', '.join(b for b in bits if b) if any(bits) else '')


def lines_html(lines, lang, cls='ls-lines'):
    lis = ''.join(f'<li><code class="ls-l">{hl(c, lang)}</code><span>{n}</span></li>' for c, n in lines)
    return f'<ul class="{cls}">{lis}</ul>'


def steps_of(chs):
    steps, order = {}, []
    for ch in chs:
        n = ch['step'][0]
        if n not in steps:
            steps[n] = (ch['step'], [])
            order.append(n)
        steps[n][1].append(ch)
    return steps, order


def chapter_html(ch, lang, seen):
    slug, topic = ch['slug'], ch['topic']

    def back(it):
        return (f'<a class="sh-from" href="./{slug}.html#{it["lesson"]}" data-topic="{topic}" data-h="{it["lesson"]}">'
                f'Lesson: {html.escape(it["ltitle"])}</a>')

    blocks = []
    if ch['must']:
        lis = ''.join(f'<li class="sh-it" data-kind="must" data-find="{find(t + " " + d)}"><b>{t}</b> {d}</li>' for t, d in ch['must'])
        blocks.append(f'<div class="sh-blk"><h4>Key ideas</h4><ul class="sh-must">{lis}</ul></div>')
    codes, fxs, tables, notes = [], [], [], []
    for it in ch['items']:
        k = it['k']
        if k == 'code':
            ls = [(c, n) for c, n in it['lines'] if c]
            if not ls:
                continue
            codes.append(f'<div class="sh-it ls-ex" data-kind="code" data-find="{find(it["title"] + " " + " ".join(c + " " + n for c, n in ls))}">'
                         f'<div class="ls-t">{html.escape(it["title"])}</div>{lines_html(ls, it["lang"])}{back(it)}</div>')
        elif k == 'prog':
            fs = ''.join(f'<div class="ls-fname">{html.escape(f)}</div><pre class="ls-pre">{hl(c, lg)}</pre>' for f, c, lg in it['files'])
            cmd = f'<div class="ls-cmd">Run it: <code>{html.escape(it["cmd"])}</code></div>' if it['cmd'] else ''
            codes.append(f'<div class="sh-it ls-ex ls-prog" data-kind="code" data-find="{find(it["title"] + " " + " ".join(c for _, c, _ in it["files"]))}">'
                         f'<div class="ls-t">{html.escape(it["title"])}</div>{fs}{cmd}{back(it)}</div>')
        elif k == 'fx':
            sig = text_of(it['title'] + '|' + it['body'])
            if sig in seen:
                continue
            seen.add(sig)
            fxs.append(f'<div class="sh-it sh-fxc" data-kind="fx" data-key="{int(bool(it["key"]))}" data-find="{find(it["title"] + " " + it["body"])}">'
                       f'{it["html"]}{back(it)}</div>')
        elif k == 'table':
            th = table_html(it['head'], it['rows'])
            sig = text_of(th)
            if sig in seen:
                continue
            seen.add(sig)
            cap = ' · '.join(text_of(h) for h in it['head'][:4] if text_of(h))
            tables.append(f'<details class="sh-it sh-tab" data-kind="table" data-find="{find(th)}" open>'
                          f'<summary><span>Table: {html.escape(cap)}</span></summary>{th}{back(it)}</details>')
        else:
            kind = 'tip' if k in ('tip', 'pro', 'new') else k
            notes.append(f'<li class="sh-it note note-{kind}" data-kind="{k}" data-find="{find(it["text"])}">'
                         f'<b>{LABEL[k]}</b><div>{it["text"]}{back(it)}</div></li>')
    if codes:
        blocks.append(f'<div class="sh-blk"><h4>Code</h4>{"".join(codes)}</div>')
    if fxs:
        blocks.append(f'<div class="sh-blk"><h4>Numbers to remember</h4><div class="sh-fx">{"".join(fxs)}</div></div>')
    if tables:
        blocks.append(f'<div class="sh-blk"><h4>Tables</h4>{"".join(tables)}</div>')
    if notes:
        blocks.append(f'<div class="sh-blk"><h4>Tips and traps</h4><ul class="sh-notes">{"".join(notes)}</ul></div>')
    return (f'<article class="sh-ch" id="{slug}"><header class="sh-chh"><span class="sh-no">{html.escape(ch["badge"])}</span>'
            f'<h3>{html.escape(ch["title"])}</h3><a class="sh-open" href="./{slug}.html" data-topic="{topic}" data-h="">Open chapter</a></header>'
            f'<p class="sh-sum">{html.escape(ch["summary"])}</p>{"".join(blocks)}</article>')


def shell_html(sid, cfg, lname, title, desc, body_cls, crumb, inner):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
{HEAD_FONTS}
<link rel="stylesheet" href="../../assets/theme.css">
<link rel="stylesheet" href="../../assets/cv.css">
<link rel="stylesheet" href="../../assets/sheet.css">
</head>
<body class="cvp sheetp langp {body_cls}" data-subject="{sid}" data-lang="{lname}">
<header class="cv-top"><a class="cv-brand" href="../../index.html">Brainy Bytes</a><a class="cv-home" href="../../subject.html?s={sid}">{cfg["name"]} learning path</a><span class="grow"></span><button type="button" class="cv-theme" id="cvTheme">Dark mode</button></header>
<div class="cv-wrap sh-wrap">
  <div class="cv-crumb"><a class="home-link" href="../../subject.html?s={sid}" target="_top">{cfg["name"]}</a><span>›</span><a href="./cheatsheet.html" data-topic="cheatsheet" data-h="">Cheatsheets</a><span>›</span><span>{crumb}</span></div>
{inner}
</div>
<script src="../../assets/fun.js"></script>
<script src="../../assets/sheet.js"></script>
</body>
</html>
'''


def full_page(sid, cfg, lang, lname, chs, meta):
    seen = set()
    steps, order = steps_of(chs)
    body = ''.join(f'<section class="sh-step" id="step-{n}"><h2><span>Step {n}</span>{html.escape(steps[n][0][1])}</h2>'
                   + ''.join(chapter_html(c, lang, seen) for c in steps[n][1]) + '</section>' for n in order)
    count = {k: body.count(f'data-kind="{k}"') for k, _ in KINDS}
    n_note = sum(count[k] for k in ('tip', 'pro', 'new', 'warn', 'exam'))
    kinds = ''.join(f'<button type="button" class="sh-k" data-k="{k}" aria-pressed="true">{v}</button>' for k, v in KINDS if count[k])
    toc = ''.join(f'<a href="#step-{n}"><b>{n}</b>{html.escape(steps[n][0][1])}</a>' for n in order)
    pdf = pdf_name(sid, lang)
    cp = meta['compact'].get('pages')
    what = 'every annotated line of every example' if sid == 'selenium' else 'every example program'
    chips = (f'<span class="cv-chip">{count["must"]} key ideas</span><span class="cv-chip">{count["code"]} code examples</span>'
             + (f'<span class="cv-chip">{count["fx"]} numbers</span>' if count['fx'] else '')
             + f'<span class="cv-chip">{count["table"]} tables</span><span class="cv-chip">{n_note} tips and traps</span>')
    inner = f'''  <header class="cv-hero">
    <div class="cv-kicker">{lname} cheatsheet · {len(chs)} chapters · only {lname} code</div>
    <h1>{cfg["name"]} with {lname}: cheatsheet</h1>
    <p class="lead">The key ideas, {what} in {lname}, the tables and the common mistakes from every chapter, in one place for quick revision. Everything here comes from the chapters and shows {lname} only, so this sheet is all you need. Each card links back to the lesson that teaches it.</p>
    <div class="cv-chips">{chips}</div>
    <div class="sh-actions">
      <a class="sh-btn primary" href="./{pdf}" download="{pdf}" type="application/pdf">Download PDF</a>
      <a class="sh-btn" href="./{slug_name(sid, lang, True)}.html" data-topic="{slug_name(sid, lang, True)}" data-h="">Compact {lname} version{f", {cp} pages" if cp else ""}</a>
      <button type="button" class="sh-btn" id="shPrint">Print or save what is shown</button>
      <span class="sh-meta">{pdf_label(meta["full"])}. The full {lname} cheatsheet, ready to keep offline.</span>
    </div>
  </header>
  <div class="sh-bar" role="search">
    <input type="search" id="shFind" placeholder="Find a method, word or idea" aria-label="Find in the cheatsheet">
    <div class="sh-kinds" role="group" aria-label="Show these parts">{kinds}</div>
    <span class="sh-count" id="shCount" aria-live="polite"></span>
  </div>
  <nav class="sh-toc" aria-label="Steps">{toc}</nav>
  <main id="shBody">{body}</main>
  <p class="sh-none" id="shNone" hidden>Nothing matches. Clear the search box or switch more parts back on.</p>'''
    desc = f'{cfg["name"]} cheatsheet for {lname}: key ideas, {lname} code, tables and common mistakes from all {len(chs)} chapters, with a PDF to download.'
    return shell_html(sid, cfg, lang, f'{lname} cheatsheet · {cfg["name"]}', desc, '', f'{lname}', inner)


# Lines that say little on their own: imports, printing the result, closing the browser.
BOILER = re.compile(r'^(import |from \S+ import |const \{.*\} = require|package |System\.out\.print|print\(|console\.log\(|'
                    r'(await )?driver\.quit\(\)|(await )?browser\.close\(\)|try ?[{:]|public (final )?class |\}|\)|\]|end$)')


def compact_lines(ch, lang, seen):
    """The code lines for the compact sheet: annotated or commented lines, each line once across the sheet."""
    out = []
    for it in ch['items']:
        if it['k'] in ('code', 'prog'):
            for c, n in it['lines']:
                sig = re.sub(r'\s+', ' ', c)
                if c and sig not in seen and len(c) <= 110 and not BOILER.match(c):
                    seen.add(sig)
                    out.append((c, n))
    return out


def compact_page(sid, cfg, lang, lname, chs, meta, limit=None):
    seen, seen_code = set(), set()
    steps, order = steps_of(chs)
    tot = {'must': 0, 'code': 0, 'fx': 0, 'trap': 0}
    body = []
    for n in order:
        arts = []
        for ch in steps[n][1]:
            musts = ''.join(f'<li class="sh-it" data-kind="must" data-find="{find(t + " " + d)}"><b>{t}</b> {d}</li>' for t, d in ch['must'])
            lines = compact_lines(ch, lang, seen_code)
            if limit is not None:
                lines = lines[:limit]
            code = ''.join(f'<li class="sh-it" data-kind="code" data-find="{find(c + " " + t)}"><code class="ls-l">{hl(c, lang)}</code><span>{t}</span></li>'
                           for c, t in lines)
            fxs, traps = [], []
            for it in ch['items']:
                if it['k'] == 'fx' and it['key']:
                    sig = text_of(it['title'] + '|' + it['body'])
                    if sig not in seen:
                        seen.add(sig)
                        fxs.append(f'<li class="sh-it" data-kind="fx" data-find="{find(it["title"] + " " + it["body"])}"><b>{it["title"]}</b>'
                                   f'<span class="cs-f">{it["body"]}</span></li>')
                elif it['k'] in ('warn', 'exam') and text_of(it['text']) not in seen:
                    seen.add(text_of(it['text']))
                    traps.append(f'<li class="sh-it cs-{it["k"]}" data-kind="{it["k"]}" data-find="{find(it["text"])}">'
                                 f'<b>{"Trap" if it["k"] == "warn" else "Exam"}</b> {it["text"]}</li>')
            if not (musts or code or fxs or traps):
                continue
            tot['must'] += len(ch['must'])
            tot['code'] += len(lines)
            tot['fx'] += len(fxs)
            tot['trap'] += len(traps)
            blk = ((f'<div class="sh-blk"><ul class="cs-must">{musts}</ul></div>' if musts else '')
                   + (f'<div class="sh-blk"><ul class="cs-code">{code}</ul></div>' if code else '')
                   + (f'<div class="sh-blk"><ul class="cs-fx">{"".join(fxs)}</ul></div>' if fxs else '')
                   + (f'<div class="sh-blk"><ul class="cs-trap">{"".join(traps)}</ul></div>' if traps else ''))
            arts.append(f'<article class="sh-ch cs-ch" id="{ch["slug"]}"><h3><a href="./{ch["slug"]}.html" data-topic="{ch["topic"]}" data-h="">'
                        f'<span class="sh-no">{html.escape(ch["badge"])}</span>{html.escape(ch["title"])}</a></h3>{blk}</article>')
        if arts:
            body.append(f'<section class="sh-step cs-step" id="step-{n}"><h2><span>Step {n}</span>{html.escape(steps[n][0][1])}</h2>{"".join(arts)}</section>')
    pdf = pdf_name(sid, lang, True)
    inner = f'''  <header class="cv-hero">
    <div class="cv-kicker">Compact {lname} cheatsheet · at most {COMPACT_MAX} printed pages · only {lname} code</div>
    <h1>{cfg["name"]} with {lname}: compact cheatsheet</h1>
    <p class="lead">The key ideas, the {lname} lines you type most and the common traps of every chapter, packed tight for a last look before an interview or a test run. It keeps only {lname}. The full {lname} cheatsheet has every example, table and tip.</p>
    <div class="cv-chips"><span class="cv-chip">{tot["must"]} key ideas</span><span class="cv-chip">{tot["code"]} {lname} lines</span>{f'<span class="cv-chip">{tot["fx"]} numbers</span>' if tot["fx"] else ''}<span class="cv-chip">{tot["trap"]} traps</span></div>
    <div class="sh-actions">
      <a class="sh-btn primary" href="./{pdf}" download="{pdf}" type="application/pdf">Download PDF</a>
      <a class="sh-btn" href="./{slug_name(sid, lang)}.html" data-topic="{slug_name(sid, lang)}" data-h="">Full {lname} cheatsheet</a>
      <button type="button" class="sh-btn" id="shPrint">Print</button>
      <span class="sh-meta">{pdf_label(meta["compact"])}. Ready to keep offline.</span>
    </div>
  </header>
  <div class="sh-bar" role="search">
    <input type="search" id="shFind" placeholder="Find a method, word or idea" aria-label="Find in the compact cheatsheet">
    <span class="sh-count" id="shCount" aria-live="polite"></span>
  </div>
  <main id="shBody" class="cs-cols">{"".join(body)}</main>
  <p class="sh-none" id="shNone" hidden>Nothing matches. Clear the search box.</p>'''
    desc = f'{cfg["name"]} compact cheatsheet for {lname}: key ideas, the {lname} lines you type most and the common traps in at most {COMPACT_MAX} printed pages, with a PDF.'
    return shell_html(sid, cfg, lang, f'Compact {lname} cheatsheet · {cfg["name"]}', desc, 'compactp', f'Compact {lname}', inner)


def chooser_page(sid, cfg, metas, n_ch):
    cards = []
    for lang, lname in cfg['langs']:
        m = metas[lang]
        full, comp = slug_name(sid, lang), slug_name(sid, lang, True)
        cards.append(f'''<article class="ls-card">
      <h2>{lname}</h2>
      <p>Only {lname} code, from all {n_ch} chapters.</p>
      <div class="ls-row"><a class="sh-btn primary" href="./{full}.html" data-topic="{full}" data-h="">Full cheatsheet</a>
        <a class="ls-dl" href="./{pdf_name(sid, lang)}" download="{pdf_name(sid, lang)}" type="application/pdf">{pdf_label(m["full"])}</a></div>
      <div class="ls-row"><a class="sh-btn" href="./{comp}.html" data-topic="{comp}" data-h="">Compact cheatsheet</a>
        <a class="ls-dl" href="./{pdf_name(sid, lang, True)}" download="{pdf_name(sid, lang, True)}" type="application/pdf">{pdf_label(m["compact"])}</a></div>
    </article>''')
    langs = ', '.join(n for _, n in cfg['langs'][:-1]) + ' and ' + cfg['langs'][-1][1]
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cheatsheets · {cfg["name"]}</title>
<meta name="description" content="{cfg["name"]} cheatsheets for {langs}. Each language has its own full and compact cheatsheet with a PDF, showing only that language's code.">
{HEAD_FONTS}
<link rel="stylesheet" href="../../assets/theme.css">
<link rel="stylesheet" href="../../assets/cv.css">
<link rel="stylesheet" href="../../assets/sheet.css">
</head>
<body class="cvp sheetp pickp" data-subject="{sid}">
<header class="cv-top"><a class="cv-brand" href="../../index.html">Brainy Bytes</a><a class="cv-home" href="../../subject.html?s={sid}">{cfg["name"]} learning path</a><span class="grow"></span><button type="button" class="cv-theme" id="cvTheme">Dark mode</button></header>
<div class="cv-wrap sh-wrap">
  <div class="cv-crumb"><a class="home-link" href="../../subject.html?s={sid}" target="_top">{cfg["name"]}</a><span>›</span><span>Cheatsheets</span></div>
  <header class="cv-hero">
    <div class="cv-kicker">Cheatsheets · one per language</div>
    <h1>{cfg["name"]} cheatsheets</h1>
    <p class="lead">Pick the language you write your tests in. Each language has its own cheatsheet that shows only that language's code, so you never need another one. The full cheatsheet has every key idea, example, table and tip from the chapters. The compact one fits in at most {COMPACT_MAX} printed pages. Both come as a PDF that works offline.</p>
  </header>
  <main class="ls-cards">
    {"".join(cards)}
  </main>
</div>
<script src="../../assets/fun.js"></script>
<script>
(() => {{
  const tb = document.getElementById('cvTheme');
  const paint = () => {{ tb.textContent = FUN.currentTheme() === 'dark' ? 'Light mode' : 'Dark mode'; }};
  tb.onclick = () => {{ FUN.toggleTheme(); paint(); }};
  paint();
  /* a link to #<chapter> passes on to the sheet the reader picks */
  const hash = location.hash;
  document.querySelectorAll('a[data-topic]').forEach(a => {{
    if (FUN.inFrame) {{
      a.href = '../../subject.html?s={sid}&t=' + a.dataset.topic + (hash ? hash : '');
      a.target = '_top';
    }} else if (hash) a.href += hash;
  }});
}})();
</script>
</body>
</html>
'''


def render(src, pdf, title):
    r = subprocess.run(['node', os.path.join(TOOLS, 'cv-build', 'sheet-pdf.js'), src, pdf, title], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f'{os.path.basename(src)}: the PDF was not made (needs node and playwright):\n{r.stderr.strip()[-600:]}')
    m = re.match(r'(\d+) pages', r.stdout.strip())
    return {'pages': int(m.group(1)) if m else 0, 'kb': os.path.getsize(pdf) // 1024}


def style_check(path):
    """The house style for prose: no em dash, en dash or semicolon outside code."""
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'<(script|style|pre|code)[\s\S]*?</\1>', ' ', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'&[#\w]+;', ' ', s)
    for ch, label in (('—', 'em dash'), ('–', 'en dash'), (';', 'semicolon')):
        if ch in s:
            i = s.index(ch)
            raise SystemExit(f'{os.path.relpath(path, ROOT)}: {label} in "...{s[max(0, i - 60):i + 20]}..."')


def write(sid):
    cfg = SUBJECTS[sid]
    out = os.path.join(ROOT, 'content', sid)
    metas, n_ch = {}, 0
    for lang, lname in cfg['langs']:
        chs = SHEET[sid](lang)
        n_ch = len(chs)
        full = os.path.join(out, slug_name(sid, lang) + '.html')
        comp = os.path.join(out, slug_name(sid, lang, True) + '.html')
        pdf, cpdf = os.path.join(out, pdf_name(sid, lang)), os.path.join(out, pdf_name(sid, lang, True))
        meta = {'full': {}, 'compact': {}}
        open(full, 'w', encoding='utf-8').write(full_page(sid, cfg, lang, lname, chs, meta))
        meta['full'] = render(full, pdf, f'{cfg["name"]} {lname} cheatsheet')
        # the compact sheet keeps every typed line when it fits, otherwise the first lines of each chapter
        for limit in (None, 16, 14, 12, 10, 8, 6):
            open(comp, 'w', encoding='utf-8').write(compact_page(sid, cfg, lang, lname, chs, meta, limit))
            meta['compact'] = render(comp, cpdf, f'{cfg["name"]} {lname} compact cheatsheet')
            if meta['compact']['pages'] <= COMPACT_MAX:
                break
        # write both pages again so each one names the real page counts
        open(full, 'w', encoding='utf-8').write(full_page(sid, cfg, lang, lname, chs, meta))
        open(comp, 'w', encoding='utf-8').write(compact_page(sid, cfg, lang, lname, chs, meta, limit))
        meta = {'full': render(full, pdf, f'{cfg["name"]} {lname} cheatsheet'),
                'compact': render(comp, cpdf, f'{cfg["name"]} {lname} compact cheatsheet')}
        for f in (full, comp):
            style_check(f)
        metas[lang] = meta
        print(f'{sid} {lname}: full {meta["full"]["pages"]} pages ({meta["full"]["kb"]} KB), '
              f'compact {meta["compact"]["pages"]} pages ({meta["compact"]["kb"]} KB, code lines per chapter: {limit or "all"})')
        if meta['compact']['pages'] > COMPACT_MAX:
            raise SystemExit(f'the compact {lname} PDF has {meta["compact"]["pages"]} pages, the limit is {COMPACT_MAX}.')
    pick = os.path.join(out, 'cheatsheet.html')
    open(pick, 'w', encoding='utf-8').write(chooser_page(sid, cfg, metas, n_ch))
    style_check(pick)


if __name__ == '__main__':
    for s in (sys.argv[1:] or list(SUBJECTS)):
        write(s)
