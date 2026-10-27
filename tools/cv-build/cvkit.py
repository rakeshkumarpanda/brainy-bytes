"""Helpers the Computer Vision topic files use. See build.py for how a topic becomes a page.

A topic file makes one Kit, fills it, and ends with  T = K.topic(...).

    K = Kit()
    K.lesson(id, title, html, kw=[...])                 one lesson, shown one at a time in the Learn tab
    K.code(key, src, stdin='')                          a Python example, run with CPython at build time and recorded line by line
    K.quiz('e', question, options, answer_index, hint, why)
    K.calc('e', question, '12', hint, [step, ...], check=3 * 4)
    K.assign(id, 'm', title, task, starter, tests, solution, hint, why)
    K.must(title, text)                                 one line of the "what you must know" list in the Summary tab

calc(check=...) is the answer worked out in Python. The build stops if it does not match the written answer.
assign(tests=[(call, want), ...]) are Python expressions run after the learner's code. The build runs the model
solution against them with CPython, so every assignment is known to be solvable.

The functions below write the boxes the lessons share. Prose must not contain em dashes, en dashes, semicolons
or emojis (the build checks), so keep sentences short and plain.
"""
import html as _html
import json

LEVELS = (('school', 'School'), ('college', 'College'), ('masters', 'Masters'), ('research', 'Research'))


class Kit:
    def __init__(self):
        self.lessons, self.codes, self.quizzes, self.calcs, self.assigns, self.musts = [], {}, [], [], [], []

    def lesson(self, id, title, html, kw=None):
        self.lessons.append({'id': id, 'title': title, 'html': html, 'kw': kw or []})

    def code(self, key, src, stdin=''):
        if key in self.codes:
            raise SystemExit(f'code block {key} is written twice')
        self.codes[key] = {'src': src.strip('\n'), 'stdin': stdin}

    def quiz(self, lv, q, o, a, hint, why, code=None):
        d = {'lv': lv, 'q': q, 'o': o, 'a': a, 'hint': hint, 'why': why}
        if code:
            d['code'] = code.strip('\n')
            d['lang'] = 'py'
        self.quizzes.append(d)

    def calc(self, lv, q, ans, hint, steps, check=None, tol=None, alt=None, unit=None):
        d = {'lv': lv, 'q': q, 'ans': ans, 'hint': hint, 'steps': steps, 'check': check}
        if tol is not None:
            d['tol'] = tol
        if alt:
            d['alt'] = alt
        if unit:
            d['unit'] = unit
        self.calcs.append(d)

    def assign(self, id, lv, title, task, starter, tests, solution, hint, why):
        self.assigns.append({'id': id, 'lv': lv, 'title': title, 'task': task, 'starter': starter.strip('\n') + '\n',
                             'tests': [{'call': c, 'want': w} for c, w in tests], 'solution': solution.strip('\n') + '\n',
                             'hint': hint, 'why': why})

    def must(self, title, text):
        self.musts.append([title, text])

    def topic(self, **t):
        t.update(lessons=self.lessons, codes=self.codes, quiz=self.quizzes, calc=self.calcs, assign=self.assigns, must=self.musts)
        return t


# ---------- boxes used inside the lessons ----------
def fx(title, body, note='', key=False):
    """A highlighted formula card. body is the formula, note says what each symbol means. key=True marks an exam favourite."""
    n = f'<div class="fx-n">{note}</div>' if note else ''
    k = ' fx-key' if key else ''
    tag = '<span class="fx-tag">Exam favourite</span>' if key else ''
    return f'<div class="fx{k}"><div class="fx-h"><span>{title}</span>{tag}</div><div class="fx-b">{body}</div>{n}</div>'


def fxs(*cards):
    return '<div class="fx-grid">' + ''.join(cards) + '</div>'


def frac(a, b):
    return f'<span class="fr"><span>{a}</span><span>{b}</span></span>'


def sqrt(x):
    return f'<span class="sq">√<span>{x}</span></span>'


def mat(rows, cls=''):
    body = ''.join('<span class="mr">' + ''.join(f'<span>{v}</span>' for v in r) + '</span>' for r in rows)
    return f'<span class="mx {cls}">{body}</span>'


def ladder(school, college, masters, research, title='One idea, four depths'):
    """The same idea explained at four depths, from school to research. The reader picks a tab."""
    texts = dict(school=school, college=college, masters=masters, research=research)
    tabs = ''.join(f'<button type="button" class="ld-t{" on" if i == 0 else ""}" data-ld="{k}">{v}</button>' for i, (k, v) in enumerate(LEVELS))
    panes = ''.join(f'<div class="ld-p" data-ld="{k}"{"" if i == 0 else " hidden"}>{texts[k]}</div>' for i, (k, _) in enumerate(LEVELS))
    return f'<div class="ladder"><div class="ld-h">{title}</div><div class="ld-tabs" role="tablist">{tabs}</div>{panes}</div>'


def scene(title, body):
    """A real world scenario walkthrough."""
    return f'<div class="scene"><div class="scene-h">Real world scenario: {title}</div>{body}</div>'


def note(text, kind='tip'):
    """kind is tip (a memory aid), warn (a common mistake) or exam (how examiners ask about it)."""
    label = {'tip': 'Remember', 'warn': 'Common mistake', 'exam': 'In the exam'}[kind]
    return f'<div class="note note-{kind}"><b>{label}</b><div>{text}</div></div>'


def deep(title, body):
    """A going deeper box for the masters and research level detail. Closed until opened."""
    return f'<details class="deep"><summary>Going deeper: {title}</summary><div class="deep-b">{body}</div></details>'


def table(head, rows, cls=''):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'<div class="tw"><table class="cvt {cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def steps(title, items):
    """A worked example whose steps open one at a time."""
    lis = ''.join(f'<li>{s}</li>' for s in items)
    return (f'<div class="walk"><div class="walk-h"><span>{title}</span><span class="walk-ctl">'
            f'<button type="button" class="wk-next">Show next step</button><button type="button" class="wk-all">Show all</button>'
            f'<button type="button" class="wk-reset">Reset</button></span></div><ol class="walk-l">{lis}</ol></div>')


def code(key):
    return f'<div class="cv-code" data-k="{key}"></div>'


def viz(name, **data):
    """An animation from assets/cvviz.js. Extra keyword arguments become starting values for its parameters."""
    cfg = _html.escape(json.dumps(data, ensure_ascii=False)) if data else ''
    return f'<div class="cvz" data-viz="{name}"' + (f' data-cfg="{cfg}"' if cfg else '') + '></div>'


def eq(s):
    """An equation on its own line, used inside worked problem steps."""
    return f'<span class="eq">{s}</span>'
