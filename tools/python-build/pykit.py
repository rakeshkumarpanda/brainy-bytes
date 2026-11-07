"""Extra boxes for the Python topic files, on top of tools/cv-build/cvkit.py and tools/ai-build/coreaikit.py.

    chapter(slug)              call first in a topic file. Download links and the LeetCode list belong to this chapter
    run(key)                   a Python example (cvkit code()) with a "Download this program" link under it
    local(key, why)            the same, for a program that needs your own computer (threads, sockets, a web server).
                               The build still runs it with CPython and shows the real output
    show(title, src, notes)    a listing that is not run here (a Django project file, a tkinter window, a shell command).
                               notes = {line number: what this line does}
    term(lines)                a terminal session: commands and what they print
    lc(num, title, slug, level, pattern, hint, solution, tests)
                               one LeetCode problem. The page shows the number, title, link, level, pattern and a hint.
                               The solution goes only into files/<slug>/leetcode.py, which the build runs against tests
    leet()                     the LeetCode table for this chapter with the download card
    files(what)                the download card for this chapter's practice files
    grow(levels)               a short "beginner, intermediate, expert" ladder made of three short paragraphs
    compare(...)               coreaikit.versus with a Python flavoured title

The prose rules of the CV builder apply: no em dashes, en dashes, semicolons or emojis, and no backslashes outside
<pre> and <code>.
"""
import html as _h

from cvkit import code, table, note

STATE = {'slug': None, 'leet': [], 'local': set()}
LEVEL = {'e': 'Easy', 'm': 'Medium', 'h': 'Hard'}


def chapter(slug):
    STATE.update(slug=slug, leet=[], local=set())


def _dl(key, text='Download this program (.py)'):
    return f'<a class="py-dl" href="./files/{STATE["slug"]}/{key}.py" download>{text}</a>'


def run(key):
    return code(key) + f'<div class="py-dlrow">{_dl(key)}<span>Save it, open it in any editor and run it with <code>python3 {key}.py</code>.</span></div>'


def local(key, why):
    STATE['local'].add(key)
    return (code(key) + f'<div class="py-local"><b>Run this one on your own computer.</b> {why} The output above comes from a real run '
            f'with CPython when this page was built.</div><div class="py-dlrow">{_dl(key)}<span>Run it with <code>python3 {key}.py</code>.</span></div>')


def show(title, src, notes=None, lang='python'):
    lines = src.strip('\n').split('\n')
    notes = notes or {}
    body = ''.join(f'<span class="pl-r"><span class="pl-n">{i}</span><span class="pl-c">{_h.escape(t) or " "}</span></span>'
                   for i, t in enumerate(lines, 1))
    nl = ''.join(f'<li><b>Line {n}</b> {t}</li>' for n, t in sorted(notes.items()))
    nb = f'<ol class="pl-notes">{nl}</ol>' if nl else ''
    return f'<div class="pl"><div class="pl-h"><span>{title}</span><small>{lang}</small></div><pre class="pl-b">{body}</pre>{nb}</div>'


def term(lines, title='Terminal'):
    body = '\n'.join(_h.escape(t) for t in lines)
    return f'<div class="pl pl-t"><div class="pl-h"><span>{title}</span><small>shell</small></div><pre class="pl-b">{body}</pre></div>'


def lc(num, title, slug, level, pattern, hint, solution, tests):
    STATE['leet'].append({'num': num, 'title': title, 'slug': slug, 'level': level, 'pattern': pattern, 'hint': hint,
                          'solution': solution.strip('\n') + '\n', 'tests': [{'call': c, 'want': w} for c, w in tests]})


def leet(intro=''):
    rows = [[f'{p["num"]}', f'<a href="https://leetcode.com/problems/{p["slug"]}/" target="_blank" rel="noopener">{p["title"]}</a>',
             f'<span class="lc-{p["level"]}">{LEVEL[p["level"]]}</span>', p['pattern'], p['hint']] for p in STATE['leet']]
    card = (f'<div class="ck-nb"><div class="ck-nb-i">.py</div><div class="ck-nb-t"><b>Solutions to these LeetCode problems</b>'
            f'<span>One simple solution per problem, with the idea, the time and space cost, and tests you can run.</span>'
            f'<small>Try each problem on leetcode.com first. Open the file only when you are stuck. Run it with python3 leetcode.py to see every test pass.</small></div>'
            f'<a class="ck-nb-a" href="./files/{STATE["slug"]}/leetcode.py" download>Download solutions</a></div>')
    return (intro or '<p>These problems use exactly what this chapter teaches. The page gives only a hint. Write your own answer on LeetCode first, then compare with the downloadable solution.</p>') + \
        table(['No.', 'Problem', 'Level', 'Pattern', 'Hint'], rows, 'lc-t') + card


def files(what):
    s = STATE['slug']
    return (f'<div class="ck-nb"><div class="ck-nb-i">.py</div><div class="ck-nb-t"><b>Practice files for this chapter</b>'
            f'<span>{what}</span><small>practice.py has every assignment with its starter code and tests. solutions.py has the model answers. '
            f'Each program of the lessons also has its own download link under it.</small></div>'
            f'<span class="py-dl2"><a class="ck-nb-a" href="./files/{s}/practice.py" download>Download practice.py</a>'
            f'<a class="ck-nb-a alt" href="./files/{s}/solutions.py" download>Download solutions.py</a></span></div>')


def grow(beginner, middle, expert):
    return ('<div class="py-grow">' + ''.join(f'<div class="pg-c pg-{k}"><b>{t}</b><div>{v}</div></div>' for k, t, v in
            (('b', 'Beginner', beginner), ('m', 'Intermediate', middle), ('x', 'Expert', expert))) + '</div>')


def leet_items():
    return list(STATE['leet'])


def local_keys():
    return sorted(STATE['local'])
