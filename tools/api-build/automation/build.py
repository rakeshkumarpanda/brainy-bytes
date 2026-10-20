"""Build content/api-automation/api-automation.html from the track files in tracks/.

The page asks for a programming language first. Java and JavaScript then ask for a tool, Python
opens its track straight away. Every track lives in its own file in tracks/ as plain Python data,
so code samples are written exactly as they run, with no HTML escaping by hand.

The shared theme, the quiz engine and the fun layer are copied in from assets/, so the page works
on its own as well as inside the portal.

Usage:   python3 tools/api-build/automation/build.py
Export:  python3 tools/api-build/automation/build.py --export DIR   also writes every code block that has a
         'save' path into DIR, so the samples can be compiled and run against mock_booker.py.
"""
import html
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(ROOT, 'content', 'api-automation', 'api-automation.html')
ORDER = ['java-rest-assured', 'java-playwright', 'java-native', 'python', 'js-postman', 'js-playwright', 'js-native']
LEVELS = ['Basic', 'Intermediate', 'Advanced', 'Expert']
HL = {'java', 'py', 'js'}
esc = html.escape


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, 'tracks', name.replace('-', '_') + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TRACK


def asset(name):
    return open(os.path.join(ROOT, 'assets', name), encoding='utf-8').read()


def part(name):
    return open(os.path.join(HERE, name), encoding='utf-8').read()


# ---------- blocks ----------
def block(b, tid):
    kind = b[0]
    if kind == 'p':
        return f'<p>{b[1]}</p>'
    if kind == 'h':
        return f'<h4>{b[1]}</h4>'
    if kind in ('ul', 'ol'):
        return f'<{kind}>' + ''.join(f'<li>{x}</li>' for x in b[1]) + f'</{kind}>'
    if kind == 'code':
        lang, label, src = b[1], b[2], b[3].strip('\n')
        hl = lang if lang in HL else ''
        return (f'<figure class="cb"><figcaption><span class="cb-l">{esc(label)}</span>'
                f'<button type="button" class="cb-copy">Copy</button></figcaption>'
                f'<pre data-hl="{hl}"><code>{esc(src)}</code></pre></figure>')
    if kind in ('tip', 'warn', 'qa', 'why'):
        icon = {'tip': '💡', 'warn': '⚠️', 'qa': '🧪', 'why': '🤔'}[kind]
        head = {'tip': 'Tip', 'warn': 'Watch out', 'qa': 'QA focus', 'why': 'Why it matters'}[kind]
        return f'<div class="note n-{kind}"><b>{icon} {head}</b><div>{b[1]}</div></div>'
    if kind == 'table':
        heads, rows = b[1], b[2]
        return ('<div class="tw"><table><thead><tr>' + ''.join(f'<th>{h}</th>' for h in heads) + '</tr></thead><tbody>'
                + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table></div>')
    if kind == 'flow':
        steps = ''.join(f'<li><button type="button" class="fl-step"><span class="fl-n">{i + 1}</span>'
                        f'<span class="fl-t"><b>{s[0]}</b><span>{s[1]}</span></span></button></li>'
                        for i, s in enumerate(b[1]))
        return (f'<div class="flow"><div class="fl-bar"><button type="button" class="fl-play">▶ Walk through it</button>'
                f'<span class="fl-hint">Or click any step</span></div><ol class="fl-list">{steps}</ol></div>')
    if kind == 'try':
        req = b[1]
        return (f'<button type="button" class="trybtn" data-try="{esc(json.dumps(req))}">🧪 Try this request in the sandbox</button>')
    raise ValueError(f'{tid}: unknown block {kind}')


def section(s, tid):
    lv = s['level']
    assert lv in LEVELS or lv == 'Scenario', f'{tid}/{s["id"]}: bad level {lv}'
    cls = 'lv-' + lv.lower()
    body = ''.join(block(b, tid) for b in s['blocks'])
    return (f'<section class="tsec reveal" id="{tid}--{s["id"]}" data-level="{lv}">'
            f'<div class="tsec-h"><span class="tsec-em">{s["emoji"]}</span><h3>{s["title"]}</h3>'
            f'<span class="lvchip {cls}">{lv}</span></div>{body}</section>')


def track_html(t):
    tid = t['id']
    stack = ''.join(f'<span class="stk"><b>{esc(n)}</b> <code>{esc(v)}</code><small>{w}</small></span>' for n, v, w in t['stack'])
    toc = ''.join(f'<a href="#{tid}--{s["id"]}" data-level="{s["level"]}"><span>{s["emoji"]}</span>{s["title"]}</a>' for s in t['sections'])
    secs = ''.join(section(s, tid) for s in t['sections'])
    return f'''<template id="tpl-{tid}">
<div class="thead card">
  <div class="thead-top"><span class="thead-em">{t['emoji']}</span><div><h2>{t['title']}</h2><p class="lede">{t['tagline']}</p></div></div>
  <p>{t['intro']}</p>
  <div class="stack">{stack}</div>
  <div class="lvfilter" role="group" aria-label="Show lessons by level">
    <button type="button" class="on" data-lv="all">All levels</button>{''.join(f'<button type="button" data-lv="{l}">{l}</button>' for l in LEVELS)}<button type="button" data-lv="Scenario">Real world</button>
  </div>
</div>
<div class="tbody">
  <nav class="ttoc card" aria-label="Lessons in this track"><b>Lessons</b>{toc}<a href="#{tid}--quiz"><span>🎯</span>Quiz</a></nav>
  <div class="tmain">{secs}
    <section class="tsec reveal" id="{tid}--quiz" data-level="quiz"><div class="quizslot"></div></section>
  </div>
</div>
</template>'''


def main():
    export = None
    if '--export' in sys.argv:
        export = sys.argv[sys.argv.index('--export') + 1]
    names = [n for n in ORDER if os.path.exists(os.path.join(HERE, 'tracks', n.replace('-', '_') + '.py'))]
    missing = sorted(set(ORDER) - set(names))
    if missing:
        print('warning: no track file yet for ' + ', '.join(missing))
    tracks = [load(n) for n in names]
    for t, n in zip(tracks, names):
        assert t['id'] == n, n
        ids = [s['id'] for s in t['sections']]
        assert len(ids) == len(set(ids)), f'{n}: duplicate section ids'
    meta = [{k: t[k] for k in ('id', 'lang', 'tool', 'title', 'emoji', 'tagline')} | {'sections': [[s['id'], s['title']] for s in t['sections']]} for t in tracks]
    quizzes = {t['id']: t['quiz'] for t in tracks}
    page = part('page.html')
    page = page.replace('/*@THEME@*/', asset('theme.css') + '\n' + asset('learn.css'))
    page = page.replace('/*@CSS@*/', part('page.css'))
    page = page.replace('<!--@TEMPLATES@-->', '\n'.join(track_html(t) for t in tracks))
    page = page.replace('/*@SHARED@*/', asset('fun.js') + '\n' + asset('learn.js'))
    js = lambda v: json.dumps(v, ensure_ascii=False).replace('</', '<\\/')
    page = page.replace('/*@DATA@*/', f'const TRACKS = {js(meta)};\nconst QUIZ = {js(quizzes)};')
    page = page.replace('/*@JS@*/', part('page.js'))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(page)
    print(f'wrote {os.path.relpath(OUT, ROOT)} ({len(page) // 1024} KB, {sum(len(t["sections"]) for t in tracks)} lessons)')
    if export:
        n = 0
        for t in tracks:
            for s in t['sections']:
                for b in s['blocks']:
                    if b[0] == 'code' and len(b) > 4 and b[4].get('save'):
                        p = os.path.join(export, t['id'], b[4]['save'])
                        os.makedirs(os.path.dirname(p), exist_ok=True)
                        open(p, 'w', encoding='utf-8').write(b[3].strip('\n') + '\n')
                        n += 1
        print(f'exported {n} code files to {export}')


if __name__ == '__main__':
    main()
