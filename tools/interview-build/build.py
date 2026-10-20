"""Build the Interview Questions page of each subject from the question sets in sets/.

Each set is a Python file in sets/ that defines SUBJECT (page settings) and ITEMS (the questions).
The build writes two files per set:
  data/interview/<name>.js                 the questions as a JS array for assets/interview.js
  content/<folder>/interview-questions.html  the page that shows them

It also checks the house style: no em dashes, en dashes or semicolons in prose fields.
Code fields are not checked, since code needs its semicolons.

Usage:  python3 tools/interview-build/build.py [--run] [name ...]   (no name builds every set)
        --run also runs every Output question (Java with the JDK, Python, JavaScript with Node.js)
        and fails if the program does not print exactly the expected answer.
"""
import html
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SETS = os.path.join(HERE, 'sets')

PROSE = ('q', 'hint', 'answer', 'explain')
LEVELS = {'e', 'm', 'h', 'x'}
KINDS = {'Concept', 'Scenario', 'Coding', 'Output', 'Design'}


def Q(id, topic, lv, q, hint, answer, explain, **more):
    """One question. Optional: points, code, acode, lang, kind, follow."""
    item = dict(id=id, topic=topic, lv=lv, q=q, hint=hint, answer=answer, explain=explain)
    item.update({k: v for k, v in more.items() if v})
    return item


def prose_text(s):
    s = re.sub(r'<pre[\s\S]*?</pre>|<code>[\s\S]*?</code>', ' ', s)
    s = re.sub(r'&[#\w]+;', ' ', s)
    return s


def check(name, subject, items):
    bad = []
    seen = set()

    def look(where, s):
        t = prose_text(s)
        for ch, label in (('—', 'em dash'), ('–', 'en dash'), (';', 'semicolon')):
            if ch in t:
                i = t.index(ch)
                bad.append(f'{where}: {label} in "...{t[max(0, i - 40):i + 20]}..."')

    for k in ('title', 'intro', 'sub'):
        if subject.get(k):
            look(f'SUBJECT.{k}', subject[k])
    for m in subject.get('must', []):
        look('SUBJECT.must', m[1] + ' ' + m[2])
    for it in items:
        where = f'{name}:{it["id"]}'
        if it['id'] in seen:
            bad.append(f'{where}: duplicate id')
        seen.add(it['id'])
        if it['lv'] not in LEVELS:
            bad.append(f'{where}: level {it["lv"]!r}')
        if it.get('kind', 'Concept') not in KINDS:
            bad.append(f'{where}: kind {it["kind"]!r}')
        for k in PROSE:
            look(f'{where}.{k}', it[k])
        for k in ('points', 'follow'):
            for p in it.get(k, []):
                look(f'{where}.{k}', p)
    return bad


PAGE = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Nunito:wght@500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/theme.css">
<link rel="stylesheet" href="../../assets/learn.css">
<link rel="stylesheet" href="../../assets/interview.css">
<style>
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0; background:var(--bg); color:var(--ink); font-family:var(--font); font-size:16.5px; line-height:1.65}}
.wrap{{max-width:980px; margin:0 auto; padding:26px 20px 80px}}
h1,h2,h3{{font-family:var(--font-head); line-height:1.15; margin:0}}
h1{{font-size:clamp(30px,5vw,42px)}}
.crumb{{color:var(--ink2); font-weight:800; font-size:14px}}
.crumb a{{color:inherit}}
.hero{{display:flex; align-items:center; gap:14px; margin:6px 0 10px}}
.hero .em{{font-size:48px; animation:fun-float 3.5s ease-in-out infinite}}
.lead{{color:var(--ink2); font-weight:600; margin:0 0 6px}}
.card{{background:var(--surface); border:1px solid var(--line); border-radius:20px; padding:20px 22px; margin-top:16px; box-shadow:var(--shadow)}}
.how{{display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:10px; margin:0; padding:0; list-style:none}}
.how li{{display:flex; gap:10px; align-items:flex-start; padding:10px 12px; border-radius:14px; background:var(--surface2); font-weight:600; font-size:14.5px}}
.how li span{{font-size:24px; line-height:1}}
html.embedded .wrap{{padding-top:16px}}
@media (max-width:560px){{.wrap{{padding:18px 16px 60px}} .card{{padding:16px 14px}}}}
</style>
</head>
<body>
<div class="wrap">
  <div class="crumb"><a class="home-link" href="../../subject.html?s={sid}" target="_top">{subject}</a> · Interview Questions</div>
  <div class="hero"><span class="em">🎤</span><h1>{title}</h1></div>
  <p class="lead">{intro}</p>
  <section class="card">
    <ul class="how">
      <li><span>✍️</span><div>Read the question and write your own answer in the box, as you would say it in the interview.</div></li>
      <li><span>💡</span><div>Stuck? Open the hint. It points you in the right direction without giving the answer away.</div></li>
      <li><span>✅</span><div>Open the answer to compare. You get the model answer, key points and a detailed explanation.</div></li>
      <li><span>🎯</span><div>Rate yourself. Your notes and ratings stay in this browser, so you can filter to the ones to review.</div></li>
    </ul>
  </section>
  <section class="card" id="interview"></section>
</div>
<script src="../../assets/fun.js"></script>
<script src="../../assets/learn.js"></script>
<script src="../../assets/interview.js"></script>
<script src="../../data/interview/{name}.js"></script>
<script>
IQ.mount('#interview', IQ_SETS[{name_js}].items, IQ_SETS[{name_js}].opts);
FUN.initScroll();
if (!FUN.inFrame) document.querySelector('.home-link').removeAttribute('target');
</script>
</body>
</html>
'''


def run_outputs(name, items):
    """Run every Output question that has a full Java program, Python script or JS file and compare with acode."""
    bad = []
    for it in items:
        if it.get('kind') != 'Output' or not it.get('code') or 'acode' not in it:
            continue
        lang = it.get('lang', 'java')
        with tempfile.TemporaryDirectory() as d:
            if lang == 'java' and 'class Main' in it['code'] and shutil.which('java'):
                f = os.path.join(d, 'Main.java')
                cmd = ['java', f]
            elif lang == 'py':
                f = os.path.join(d, 'main.py')
                cmd = [sys.executable, f]
            elif lang == 'js' and shutil.which('node'):
                f = os.path.join(d, 'main.js')
                cmd = ['node', f]
            else:
                continue
            with open(f, 'w', encoding='utf-8') as fh:
                fh.write(it['code'])
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            got = r.stdout.strip()
            if got != it['acode'].strip():
                bad.append(f'{name}:{it["id"]}: expected {it["acode"]!r} but the program printed {got!r} {r.stderr[-300:]}')
            else:
                print(f'  ran {it["id"]}: ok')
    return bad


def load(path):
    spec = importlib.util.spec_from_file_location('set_' + os.path.basename(path)[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    mod.Q = Q
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def build(name):
    mod = load(os.path.join(SETS, name + '.py'))
    S, items = mod.SUBJECT, mod.ITEMS
    bad = check(name, S, items)
    if RUN:
        bad += run_outputs(name, items)
    if bad:
        print('\n'.join(bad))
        raise SystemExit(f'{name}: {len(bad)} style problems')
    opts = {k: S[k] for k in ('title', 'sub', 'lang', 'must') if S.get(k)}
    opts['key'] = S['sid'] + '-interview'
    data = {'opts': opts, 'items': items}
    js = ('/* Generated by tools/interview-build/build.py from tools/interview-build/sets/' + name + '.py. Edit that file, not this one. */\n'
          'window.IQ_SETS = window.IQ_SETS || {};\n'
          f'IQ_SETS[{json.dumps(name)}] = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n')
    os.makedirs(os.path.join(ROOT, 'data', 'interview'), exist_ok=True)
    with open(os.path.join(ROOT, 'data', 'interview', name + '.js'), 'w', encoding='utf-8') as f:
        f.write(js)
    page = PAGE.format(title=html.escape(S['title']), intro=S['intro'], subject=html.escape(S['subject']), sid=S['sid'],
                       name=name, name_js=json.dumps(name))
    out = os.path.join(ROOT, 'content', S['folder'], 'interview-questions.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(page)
    lv = {l: sum(1 for it in items if it['lv'] == l) for l in 'emhx'}
    print(f'{name}: {len(items)} questions {lv} -> {os.path.relpath(out, ROOT)}')


RUN = False

if __name__ == '__main__':
    args = sys.argv[1:]
    if '--run' in args:
        RUN = True
        args.remove('--run')
    names = args or sorted(f[:-3] for f in os.listdir(SETS) if f.endswith('.py') and not f.startswith('_'))
    for n in names:
        build(n)
