"""Write the downloadable .py files of each Python chapter into content/python/files/<slug>/ and run them.

  <key>.py       each example program, exactly as the Learn tab runs it, under a short header
  practice.py    every assignment: the task in plain words, the starter code and a check() call with its tests
  solutions.py   the model solutions with the same checks. The build runs it and stops unless every test passes
  leetcode.py    the solutions to the chapter's LeetCode problems (pykit.lc), each with its link, idea and tests.
                 The build runs it and stops unless every test passes

The files use only plain Python, short names and simple loops, so a beginner can read them.
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile

CHECK = '''

# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)
'''


def plain(s):
    """Lesson HTML to plain text for a comment."""
    s = re.sub(r'<code>(.*?)</code>', r'\1', str(s))
    s = re.sub(r'<br\s*/?>|</p>|</li>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    return re.sub(r'\n{2,}', '\n', s).strip()


def comment(text, width=100):
    out = []
    for para in plain(text).split('\n'):
        line = '#'
        for w in para.split():
            if len(line) + 1 + len(w) > width:
                out.append(line)
                line = '#'
            line += ' ' + w
        out.append(line)
    return '\n'.join(out)


def header(T, what):
    return (f'# {T["badge"]} {T["title"]}\n# {what}\n# From the Brainy Bytes Python subject. Run it with: python3 <this file>\n')


def tests_src(a):
    return repr([(t['call'], t['want']) for t in a['tests']])


def practice(T, solved):
    out = [header(T, 'Model solutions. Try practice.py first.' if solved else 'Practice tasks. Fill in each function, then run this file.')]
    out.append(CHECK)
    for i, a in enumerate(T['assign'], 1):
        out.append(f'\n\n# ================================================================== task {i}: {a["title"]}\n')
        out.append(comment(a['task']) + '\n')
        if not solved:
            out.append(comment('Hint: ' + a['hint']) + '\n')
        else:
            out.append(comment('Why it works: ' + a['why']) + '\n')
        out.append('\n' + (a['solution'] if solved else a['starter']))
    out.append('\n\nif __name__ == "__main__":\n    results = []\n')
    for i, a in enumerate(T['assign'], 1):
        out.append(f'    results.append(check("Task {i}: {a["title"]}", {tests_src(a)}))\n')
    out.append('    if all(results):\n        print("Every task passes. Well done!")\n'
               '    else:\n        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")\n')
    return ''.join(out)


def leetfile(T):
    out = [header(T, 'LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.')]
    out.append(CHECK)
    for p in T['leet']:
        out.append(f'\n\n# ================================================================== {p["num"]}. {p["title"]} ({ {"e": "Easy", "m": "Medium", "h": "Hard"}[p["level"]] })\n')
        out.append(f'# https://leetcode.com/problems/{p["slug"]}/\n')
        out.append(comment('Pattern: ' + p['pattern']) + '\n' + comment('Idea: ' + p['hint']) + '\n\n')
        out.append(p['solution'])
    out.append('\n\nif __name__ == "__main__":\n    results = []\n')
    for p in T['leet']:
        t = repr([(x['call'], x['want']) for x in p['tests']])
        out.append(f'    results.append(check("{p["num"]}. {p["title"]}", {t}))\n')
    out.append('    if all(results):\n        print("Every solution passes its tests.")\n')
    return ''.join(out)


def run_file(path, must):
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run([sys.executable, '-I', path], capture_output=True, text=True, timeout=300, cwd=d)
    if r.returncode or must not in r.stdout:
        raise SystemExit(f'{path} failed:\n{r.stdout[-3000:]}\n{r.stderr[-3000:]}')


def write_all(chs, out_dir):
    n = 0
    for T in chs:
        d = os.path.join(out_dir, T['slug'])
        os.makedirs(d, exist_ok=True)
        for k, c in T['codes'].items():
            if k in ('practice', 'solutions', 'leetcode'):
                raise SystemExit(f'{T["slug"]}: code key "{k}" clashes with the {k}.py download, rename it')
            head = header(T, f'Example "{k}" from the lesson.')
            if c['stdin']:
                head += '# This program reads input. Type these lines when it asks:\n' + ''.join(f'#   {x}\n' for x in c['stdin'].split('\n') if x)
            open(os.path.join(d, k + '.py'), 'w', encoding='utf-8').write(head + '\n' + c['src'] + '\n')
            n += 1
        if T['assign']:
            open(os.path.join(d, 'practice.py'), 'w', encoding='utf-8').write(practice(T, False))
            sp = os.path.join(d, 'solutions.py')
            open(sp, 'w', encoding='utf-8').write(practice(T, True))
            run_file(sp, 'Every task passes')
            n += 2
        if T.get('leet'):
            lp = os.path.join(d, 'leetcode.py')
            open(lp, 'w', encoding='utf-8').write(leetfile(T))
            run_file(lp, 'Every solution passes')
            n += 1
    print(f'downloads: {n} .py files written to {os.path.relpath(out_dir)}, and every solutions.py and leetcode.py passes')
