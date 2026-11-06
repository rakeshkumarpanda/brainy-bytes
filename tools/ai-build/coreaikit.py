"""Extra boxes for the Core AI topic files, on top of tools/cv-build/cvkit.py.

    wwh(what, why, how)          the three questions every concept answers: what it is, why we need it, how it works
    versus(title, head, rows, verdict)
                                 a comparison with similar methods, as a table and a one line verdict
    nbcard(slug, what)           a card that downloads the chapter's practice notebook from content/ai/notebooks/
    recap(points, nxt)           the "Chapter summary" lesson body: numbered points and what comes next
    src(text)                    a small line that says where the material comes from (slides, transcript, textbook)
    algo(title, lines)           pseudocode lines in a box (kept in <pre>, so the style check skips it)

Every box only uses plain HTML, so the cheatsheet recorder in tools/cv-build/cheatsheet.py still sees the fx(),
table() and note() boxes placed inside them.
"""
import html as _h

from cvkit import table


def wwh(what, why, how):
    cell = lambda k, t, body: f'<div class="wwh-c wwh-{k}"><b class="wwh-t">{t}</b><div>{body}</div></div>'
    return ('<div class="wwh">' + cell('what', 'What it is', what) + cell('why', 'Why we need it', why)
            + cell('how', 'How it works', how) + '</div>')


def versus(title, head, rows, verdict=''):
    v = f'<p class="vs-v"><b>Bottom line:</b> {verdict}</p>' if verdict else ''
    return f'<div class="vs"><div class="vs-h">{title}</div>{table(head, rows)}{v}</div>'


def nbcard(slug, what):
    return (f'<div class="ck-nb"><div class="ck-nb-i">ipynb</div><div class="ck-nb-t"><b>Practice notebook for this chapter</b>'
            f'<span>{what}</span><small>Open it in Jupyter, VS Code or Google Colab. It needs only plain Python 3, no extra '
            f'packages. Each task has a starter cell, a check cell that tells you which tests pass, and a full solution '
            f'further down in case you get stuck.</small></div>'
            f'<a class="ck-nb-a" href="./notebooks/{slug}.ipynb" download>Download notebook</a></div>')


def recap(points, nxt=''):
    lis = ''.join(f'<li>{p}</li>' for p in points)
    n = f'<p class="rc-next"><b>Next:</b> {nxt}</p>' if nxt else ''
    return f'<ol class="rc">{lis}</ol>{n}'


def src(text):
    return f'<p class="src-line">Source: {text}</p>'


def algo(title, lines):
    body = _h.escape('\n'.join(lines), quote=False)
    return f'<div class="algo"><div class="algo-h">{title}</div><pre>{body}</pre></div>'
