"""Write one practice notebook per Core AI chapter to content/ai/notebooks/<slug>.ipynb, and run each one.

A notebook is made from what the chapter already has, so the page and the notebook never disagree:
  1. a title cell with the chapter lead and how to use the notebook
  2. a helper cell with check(tests), which runs a task's tests and prints which ones pass
  3. every Python example of the chapter (the same code the Learn tab runs), each under a short heading.
     A topic file can give the heading text with nb={code_key: 'what this example shows'} in K.topic(...)
  4. "Your turn": every assignment with its task, a starter cell and a check cell
  5. "Solutions": the model solution of every assignment, again followed by its check cell

run(nb) executes all code cells from top to bottom in a fresh Python, the way "Run all" does in Jupyter. The build
stops if a cell raises, or if a check cell under a solution does not report that every test passes.

Usage on its own:  python3 tools/ai-build/notebooks.py      (loads the Core AI chapters, writes and runs every notebook)
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HELPER = '''# A small helper. check(tests) runs each test of a task and tells you which ones pass.
# Each test is a pair: the call to make, and the answer we expect.
import json

def check(tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + str(error)
        same = json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr)
        if same:
            passed = passed + 1
            print("PASS ", call)
        else:
            print("FAIL ", call, " expected", expected, " but got", got)
    if passed == len(tests):
        print("All", len(tests), "tests pass. Well done!")
    else:
        print(passed, "of", len(tests), "tests pass. Keep going, or look at the solution below.")'''


def _lines(text):
    parts = text.split('\n')
    return [p + '\n' for p in parts[:-1]] + [parts[-1]]


def _md_text(s):
    """Lesson HTML is fine in Jupyter Markdown, but code tags read better as backticks."""
    s = re.sub(r'<code>(.*?)</code>', r'`\1`', str(s))
    s = re.sub(r'</?p>', '\n', s)
    return re.sub(r'\n{3,}', '\n\n', s).strip()


def cells_for(T):
    md = lambda t: {'t': 'md', 'src': t.strip('\n')}
    cd = lambda t: {'t': 'code', 'src': t.strip('\n')}
    about = T.get('nb', {})
    out = [md(f"# {T['badge']} {T['title']}: practice notebook\n\n{_md_text(T['lead'])}\n\n"
              "How to use it: run the cells from top to bottom (Shift + Enter). First read and run the examples. "
              "Then try each task in its starter cell and run the check cell under it. "
              "The full solutions are at the end, so try on your own first.\n\n"
              "Everything here is plain Python 3. No extra packages are needed."),
           md('## Setup'), cd(HELPER)]
    if T['codes']:
        out.append(md('## Examples from the chapter'))
        for k, c in T['codes'].items():
            out.append(md(f"### {about.get(k, 'Example: ' + k)}"))
            out.append(cd(c['src']))
    if T['assign']:
        out.append(md('## Your turn'))
        for i, a in enumerate(T['assign'], 1):
            tests = repr([(t['call'], t['want']) for t in a['tests']])
            out.append(md(f"### Task {i}: {a['title']}\n\n{_md_text(a['task'])}\n\nHint: {_md_text(a['hint'])}"))
            out.append(cd(a['starter']))
            out.append(md('Run this cell to check your answer:'))
            out.append(cd(f'check({tests})'))
        out.append(md('## Solutions\n\nTry the tasks yourself first. Running a solution cell replaces your own function with the model one.'))
        for i, a in enumerate(T['assign'], 1):
            tests = repr([(t['call'], t['want']) for t in a['tests']])
            out.append(md(f"### Solution to task {i}: {a['title']}\n\n{_md_text(a['why'])}"))
            out.append(cd(a['solution']))
            out.append({'t': 'code', 'src': f'check({tests})', 'must_pass': True})
    return out


def to_ipynb(cells):
    nb = []
    for k, c in enumerate(cells):
        if c['t'] == 'md':
            nb.append({'cell_type': 'markdown', 'id': f'cell-{k:02d}', 'metadata': {}, 'source': _lines(c['src'])})
        else:
            nb.append({'cell_type': 'code', 'id': f'cell-{k:02d}', 'metadata': {}, 'execution_count': None, 'outputs': [],
                       'source': _lines(c['src'])})
    return {'cells': nb, 'nbformat': 4, 'nbformat_minor': 5,
            'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                         'language_info': {'name': 'python'}}}


RUNNER = r'''
import json, sys, io, contextlib
cells = json.load(open(sys.argv[1]))
ns = {"__name__": "__main__"}
for i, c in enumerate(cells):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(c["src"], "cell%d" % i, "exec"), ns)
    except BaseException as e:
        print(json.dumps({"cell": i, "error": type(e).__name__ + ": " + str(e), "src": c["src"][:300]}))
        raise SystemExit(1)
    if c.get("must_pass") and "All " not in buf.getvalue():
        print(json.dumps({"cell": i, "error": "a solution does not pass its tests", "out": buf.getvalue()[-800:]}))
        raise SystemExit(1)
print(json.dumps({"ok": True}))
'''


def run(cells, name):
    code = [c for c in cells if c['t'] == 'code']
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'cells.json')
        json.dump(code, open(p, 'w'))
        r = subprocess.run([sys.executable, '-I', '-c', RUNNER, p], capture_output=True, text=True, timeout=300, cwd=d)
    if r.returncode:
        raise SystemExit(f'notebook {name} failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}')


def write_all(chs, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    n = 0
    for T in chs:
        if T.get('kind') == 'revision' or not (T['codes'] or T['assign']):
            continue
        cells = cells_for(T)
        run(cells, T['slug'])
        with open(os.path.join(out_dir, T['slug'] + '.ipynb'), 'w') as f:
            json.dump(to_ipynb(cells), f, indent=1, ensure_ascii=False)
            f.write('\n')
        n += 1
    print(f'notebooks: {n} written to {os.path.relpath(out_dir)} and every one runs from top to bottom')


if __name__ == '__main__':
    HERE = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'cv-build'))
    import build as B
    B.CFG.update({'topics': os.path.join(HERE, 'core-topics')})
    write_all(B.chapters(), os.path.join(B.ROOT, 'content', 'ai', 'notebooks'))
