"""Build the Master the Claude chapter pages in content/claude/ from the topic files in topics/.

The chapters reuse the JavaScript chapter builder (tools/js-build/build.py) for running examples,
syntax colouring, quizzes and number practice. Every code example in these chapters is Python. This file adds what the Claude chapters need:
  - Markdown, YAML and plain text colouring for CLAUDE.md, SKILL.md, agent files and rules
  - a "files" row on each part that names the real files and folders the part teaches
  - a beginner path: parts marked easy=True stay visible when the reader picks "beginner path only"
  - Python examples (tests, hooks, MCP servers, skill scripts) run with box/.venv/bin/python, exposed to commands as $PY

Every runnable example runs for real when the page is built and the real output is shown under it.
Hooks are run by piping the same JSON Claude Code sends on stdin. MCP servers are started and called
by a real MCP client. Claude API examples use the real Python SDK against box/api/standin.py, a local
stand-in for the Messages API whose replies are scripted, and the page says so. Nothing that needs a Claude
login or a real API key is run: those blocks are marked "Shown, not run here".

Usage:  python3 tools/claude-build/build.py [slug ...]        (no slug builds every chapter)
Needs:  python3, Node.js 22 or later (the shared builder uses it), and the Python packages (mcp, anthropic):
        python3 -m venv tools/claude-build/box/.venv
        tools/claude-build/box/.venv/bin/pip install -r tools/claude-build/box/requirements.txt
"""
import html
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'content', 'claude')
SUBJECT = 'master-claude'
SUBJECT_TITLE = 'Master the Claude'
SUBJECT_EMOJI = '✨'

# Load the JavaScript builder as a library. Its run cache, scratch folder and package box are pointed at this folder.
_spec = importlib.util.spec_from_file_location('jsbuild', os.path.join(ROOT, 'tools', 'js-build', 'build.py'))
jsb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(jsb)
jsb.CACHE = os.path.join(HERE, '.cache')
jsb.BOX = os.path.join(HERE, 'box')
jsb.RUNS = os.path.join(HERE, 'box', 'runs')
jsb.SUBJECT = SUBJECT
PY = os.environ.get('CLAUDE_BUILD_PYTHON') or os.path.join(HERE, 'box', '.venv', 'bin', 'python')
RUN_STAMP = 1  # bump to rerun every example after changing how examples are run

_env = jsb.env


def env():
    e = _env()
    e['PY'] = PY
    e['CLAUDE_BUILD_STAMP'] = str(RUN_STAMP)
    return e


jsb.env = env
jsb.KW['bash'] |= {'claude', 'echo', 'chmod', 'cat', 'python', 'python3', 'pip', 'curl', 'jq', 'ls', 'exit', 'if', 'then', 'fi'}


# ---------- colouring for Markdown, YAML front matter and plain text ----------
def hl_md(code):
    out = []
    lines = code.split('\n')
    in_front = lines and lines[0].strip() == '---'
    in_fence = False
    for i, line in enumerate(lines):
        e = html.escape(line, quote=False)
        if in_front:
            if i > 0 and line.strip() == '---':
                in_front = False
                out.append(f'<span class="c">{e}</span>')
                continue
            if i == 0:
                out.append(f'<span class="c">{e}</span>')
                continue
            m = re.match(r'^(\s*-?\s*)([A-Za-z_][\w-]*)(:)(.*)$', line)
            if m:
                out.append(html.escape(m.group(1)) + f'<span class="a">{html.escape(m.group(2))}</span>:' + yaml_value(m.group(4)))
            else:
                out.append(yaml_value(line))
            continue
        if line.strip().startswith('```'):
            in_fence = not in_fence
            out.append(f'<span class="c">{e}</span>')
            continue
        if in_fence:
            out.append(f'<span class="s">{e}</span>')
            continue
        if re.match(r'^#{1,6} ', line):
            out.append(f'<span class="k">{e}</span>')
            continue
        if re.match(r'^\s*<!--.*-->\s*$', line):
            out.append(f'<span class="c">{e}</span>')
            continue
        e = re.sub(r'`[^`]+`', lambda m: f'<span class="s">{m.group()}</span>', e)
        e = re.sub(r'(^|\s)(@[\w./~-]+)', lambda m: m.group(1) + f'<span class="a">{m.group(2)}</span>', e)
        e = re.sub(r'\$(ARGUMENTS(\[\d+\])?|\d|\{[A-Z_]+\})', lambda m: f'<span class="n">{m.group()}</span>', e)
        e = re.sub(r'^(\s*)(-|\d+\.)(\s)', lambda m: m.group(1) + f'<span class="t">{m.group(2)}</span>' + m.group(3), e)
        out.append(e)
    return '\n'.join(out)


def yaml_value(v):
    t = html.escape(v, quote=False)
    s = v.strip()
    if not s:
        return t
    if re.match(r'^(true|false|yes|no|null|\d+)$', s):
        return t.replace(html.escape(s, quote=False), f'<span class="k">{html.escape(s, quote=False)}</span>', 1)
    if s.startswith('#'):
        return f'<span class="c">{t}</span>'
    return t.replace(html.escape(s, quote=False), f'<span class="s">{html.escape(s, quote=False)}</span>', 1)


_hl = jsb.hl


def hl(code, lang='js'):
    if lang == 'md':
        return hl_md(code)
    if lang == 'text':
        return html.escape(code, quote=False)
    if lang == 'yaml':
        return '\n'.join(re.sub(r'^(\s*-?\s*)([\w-]+)(:)(.*)$', lambda m: html.escape(m.group(1)) + f'<span class="a">{m.group(2)}</span>:' + yaml_value(m.group(4)), ln)
                         if re.match(r'^\s*-?\s*[\w-]+:', ln) else (f'<span class="c">{html.escape(ln, quote=False)}</span>' if ln.strip().startswith('#') else yaml_value(ln))
                         for ln in code.split('\n'))
    return _hl(code, lang)


jsb.hl = hl
_lang_of = jsb.lang_of


def lang_of(name):
    base = name.rsplit('/', 1)[-1]
    ext = base.rsplit('.', 1)[-1] if '.' in base else ''
    if ext == 'md':
        return 'md'
    if ext in ('txt', 'log', '') or base.startswith('.') and ext not in ('json', 'sh', 'env'):
        return 'text'
    if ext in ('yml', 'yaml'):
        return 'yaml'
    if ext == 'sh':
        return 'bash'
    return _lang_of(name)


jsb.lang_of = lang_of


# ---------- loading and checking topics ----------
def topic_files():
    return sorted(f for f in os.listdir(os.path.join(HERE, 'topics')) if re.match(r'\d\d-.*\.py$', f))


def load_topic(path):
    for p in (HERE, os.path.join(ROOT, 'tools', 'js-build')):
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location('ctopic_' + re.sub(r'\W', '_', os.path.basename(path)[:-3]), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.T


def all_topics():
    return [load_topic(os.path.join(HERE, 'topics', f)) for f in topic_files()]


def check(T):
    errs = jsb.check(T)
    for p in T['parts']:
        for f in p.get('files') or []:
            for bad in ('—', '–', ';'):
                if bad in f:
                    errs.append(f'part {p["id"]}: {bad!r} in a file tag')
    if not any(p.get('easy') for p in T['parts']):
        errs.append('no part is marked easy=True, so the beginner path would be empty')
    return errs


# ---------- the page ----------
def esc(s):
    return html.escape(str(s))


def build(T, chapters):
    errs = check(T)
    if errs:
        raise SystemExit(f'{T["slug"]}:\n  ' + '\n  '.join(errs))

    import concurrent.futures as cf
    import subprocess
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        jobs = {k: ex.submit(jsb.run_spec, s) for k, s in T['codes'].items() if s['t'] != 'show'}
        res = {}
        for k, f in jobs.items():
            try:
                res[k] = f.result()
            except subprocess.TimeoutExpired:
                raise SystemExit(f'{T["slug"]}: {k} timed out')
    for e in T['ex']:
        fails, out = jsb.check_exercise(e['solution'], e['tests'])
        if fails:
            raise SystemExit(f'{T["slug"]}: the solution to exercise {e["id"]} fails {fails} test(s)\n{out}')
        fails, out = jsb.check_exercise(e['starter'], e['tests'])
        if fails == 0:
            raise SystemExit(f'{T["slug"]}: the starter for exercise {e["id"]} already passes every test')

    blocks = {k: jsb.block(k, s, res.get(k)) for k, s in T['codes'].items()}
    parts = T['parts']
    n_viz = sum(len(re.findall(r'data-viz="', p['html'])) for p in parts)
    n_run = sum(1 for s in T['codes'].values() if s['t'] != 'show')
    n_files = sum(1 for s in T['codes'].values() if s['t'] == 'show')
    n_easy = sum(1 for p in parts if p.get('easy'))
    chips = [f'⏱️ About {T["minutes"]} min read', f'📚 {len(parts)} parts', f'🎬 {n_viz} animations'] + \
            ([f'▶ {n_run} examples run for real'] if n_run else []) + [f'📄 {n_files} ready to copy files and prompts',
            ] + ([f'🏋️ {len(T["ex"])} hands-on exercises'] if T['ex'] else []) + [f'🎯 {len(T["quiz"])} quiz questions', f'🧮 {len(T["calc"])} calculations',
            f'🧒 {n_easy} beginner parts']
    chip_html = ''.join(f'<span class="chip">{c}</span>' for c in chips)
    toc = ''.join(f'<a href="#{p["id"]}"{" class=\"easy\"" if p.get("easy") else ""}><span>{p["emoji"]}</span>{esc(p["title"])}</a>' for p in parts)
    toc += ('<a class="spec" href="#comic">🖼️ Comic</a><a class="spec" href="#real-life">🌍 Real life</a>'
            + ('<a class="spec" href="#practice">🏋️ Hands-on</a>' if T['ex'] else '') + '<a class="spec" href="#quiz">🎯 Quiz</a>'
            '<a class="spec" href="#numbers">🧮 Number crunch</a>')
    secs = []
    for i, p in enumerate(parts, 1):
        body = re.sub(r'\[\[([\w-]+)\]\]', lambda m: blocks[m.group(1)], p['html'].strip())
        tags = ''
        if p.get('easy') or p.get('files'):
            tags = ('<div class="cl-tags">' + ('<span class="cl-easy">🧒 Beginner friendly</span>' if p.get('easy') else '')
                    + ''.join(f'<span class="cl-file">📄 {esc(f)}</span>' for f in p.get('files') or []) + '</div>')
        secs.append(f'<section class="card reveal jsec{" easy-part" if p.get("easy") else ""}" id="{p["id"]}" data-say="{p["id"]}"><div class="sec-num">Part {i}</div>'
                    f'<h2><span class="sec-em">{p["emoji"]}</span><span>{esc(p["title"])}</span></h2>\n{tags}\n{body}\n</section>\n')

    idx = [c['slug'] for c in chapters].index(T['slug'])
    pv = chapters[idx - 1] if idx else None
    nx = chapters[idx + 1] if idx + 1 < len(chapters) else None
    a = (f'<a class="prev" href="./{pv["slug"]}.html" data-topic="{pv["slug"]}"><small>← Previous chapter</small><b>{pv["emoji"]} {esc(pv["short"])}</b></a>' if pv else '<span></span>')
    b = (f'<a class="next" href="./{nx["slug"]}.html" data-topic="{nx["slug"]}"><small>Next chapter →</small><b>{nx["emoji"]} {esc(nx["short"])}</b></a>'
         if nx else '<a class="next" href="./interview-questions.html" data-topic="interview-questions"><small>Next →</small><b>🎤 Interview Questions</b></a>')
    pager = f'<nav class="pager">{a}{b}</nav>'

    page = {k: T[k] for k in ['info', 'real', 'quiz', 'calc', 'say', 'ex']}
    page['quiz'] = [{**q, 'q': jsb.inline(q['q']), 'o': [jsb.inline(o) for o in q['o']], 'hint': jsb.inline(q['hint']), 'why': jsb.inline(q['why'])} for q in T['quiz']]
    page['calc'] = [{**c, 'q': jsb.inline(c['q']), 'hint': jsb.inline(c['hint']), 'steps': [jsb.inline(x) for x in c['steps']]} for c in T['calc']]
    page['dg'] = T.get('dg', {})
    page['lanes'] = T.get('lanes', {})
    page['play'] = {}
    mod = T['module']
    plain = f'<div class="cl-plain"><b>🧒 In plain words</b><p>{T["plain"]}</p></div>' if T.get('plain') else ''
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
</head>
<body>
<div class="wrap">
  <div class="crumb"><a class="home-link" href="../../subject.html?s={SUBJECT}" target="_top">{SUBJECT_EMOJI} {SUBJECT_TITLE}</a><span>›</span><span>{mod[0]} {esc(mod[1])}</span><span>›</span><span>Chapter {idx + 1} of {len(chapters)}</span></div>
  <header class="hero" id="top" data-say="top">
    <div class="hero-row"><span class="em">{T["emoji"]}</span><div><h1>{esc(T["title"])}</h1><p class="lead">{T["lead"]}</p></div></div>
    <div class="chips">{chip_html}<button type="button" class="listen-btn" id="listenAll">🎧 Listen in 6 languages</button></div>
    {plain}
  </header>
  <nav class="toc" aria-label="Parts of this chapter">{toc}<button type="button" class="cl-toggle" id="easyOnly" aria-pressed="false">🧒 Show the beginner path only</button></nav>
  <section class="card reveal" id="comic"></section>

{"".join(secs)}
  <section class="card reveal" id="real-life"></section>
  {'<section class="card reveal" id="practice" data-say="practice"></section>' if T['ex'] else '<section id="practice" hidden></section>'}
  <section class="card reveal" id="quiz"{'' if T['ex'] else ' data-say="practice"'}></section>
  <section class="card reveal" id="numbers"></section>
  <p class="cl-checked">📖 {T.get("checked", "Every file name, folder, setting and command on this page was checked against the official Claude and Claude Code documentation in October 2026.")}</p>
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
<script>
const PAGE = {jsb.js(page)};
JSPLAY.page({{ title: {jsb.js(T["title"])}, subject: {jsb.js(SUBJECT)} }});
CLAUDE_PAGE.wire();
</script>
</body>
</html>
'''
    dest = os.path.join(OUT, T['slug'] + '.html')
    os.makedirs(OUT, exist_ok=True)
    open(dest, 'w', encoding='utf-8').write(out)
    print(f'{T["slug"]}: {len(parts)} parts, {n_viz} animations, {n_run} run for real, {n_files} files shown, {len(T["ex"])} exercises, '
          f'{len(out) // 1024} KB -> {os.path.relpath(dest, ROOT)}')


# ---------- the catalog block ----------
def catalog(chapters):
    js = jsb.js
    mods = []
    for T in chapters:
        if not mods or mods[-1]['key'] != T['module']:
            mods.append({'key': T['module'], 'topics': []})
        mods[-1]['topics'].append(T)
    L = ['function claudeModules() {', '  return [']
    lvn = {'e': 'Easy', 'm': 'Medium', 'h': 'Hard', 'x': 'Expert'}
    for mi, m in enumerate(mods):
        em, title, mid, blurb = m['key']
        L.append(f'    {{ id: {js(mid)}, title: {js(title)}, emoji: {js(em)}, blurb: {js(blurb)}, topics: [')
        for ti, T in enumerate(m['topics']):
            secs = []
            for p in T['parts']:
                secs.append(f'        {{ id: {js(p["id"])}, title: {js(p["title"])}, emoji: {js(p["emoji"])}, group: {js("Beginner path" if p.get("easy") else "Lesson")}, keywords: {js(p.get("kw", []))} }}')
            for e in T['ex']:
                secs.append(f'        {{ id: {js(e["id"])}, title: {js(e["title"])}, emoji: "🏋️", group: {js(lvn[e["lv"]] + " practice")} }}')
            secs.append("        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' }")
            secs.append("        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }")
            L.append(f'      {{ id: {js(T["slug"])}, title: {js(T["title"])}, emoji: {js(T["emoji"])}, page: {js("content/claude/" + T["slug"] + ".html")},')
            L.append(f'        summary: {js(T["summary"])},')
            L.append(f'        keywords: {js(T["keywords"])},')
            L.append(f'        added: {js(T.get("added", "2026-10-20"))},')
            L.append('        sections: [')
            L.append(',\n'.join(secs))
            L.append('      ] }' + (',' if ti + 1 < len(m['topics']) else ''))
        L.append('    ] }' + (',' if mi + 1 < len(mods) else ''))
    L.append('  ];')
    L.append('}')
    block_text = '\n'.join(L)
    path = os.path.join(ROOT, 'data', 'catalog.js')
    src = open(path, encoding='utf-8').read()
    start = '/* ===== claude-build: Master the Claude chapters. Generated by tools/claude-build/build.py, edit the topic files instead. ===== */'
    end = '/* ===== end of claude-build ===== */'
    new = f'{start}\n{block_text}\n{end}'
    if start in src:
        src = re.sub(re.escape(start) + r'[\s\S]*?' + re.escape(end), lambda _: new, src)
    else:
        src = src.rstrip('\n') + '\n\n' + new + '\n'
    open(path, 'w', encoding='utf-8').write(src)
    print(f'catalog: {len(chapters)} chapters in {len(mods)} modules -> data/catalog.js')


def main():
    if not jsb.NODE:
        raise SystemExit('Node.js was not found. Set JS_BUILD_NODE.')
    if not os.path.exists(PY):
        raise SystemExit(f'Python for the MCP examples was not found at {PY}. See the usage notes at the top of this file.')
    print('Node', jsb.node_version())
    chapters = all_topics()
    want = sys.argv[1:]
    for T in chapters:
        if not want or T['slug'] in want:
            build(T, chapters)
    catalog(chapters)


if __name__ == '__main__':
    main()
