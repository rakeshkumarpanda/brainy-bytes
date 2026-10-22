"""Helpers the Maths for Machine Learning topic files use. See build.py for how a topic becomes a page.

A topic file makes one Kit, fills it, and ends with  T = K.topic(...).

    K = Kit()
    K.code('dot', py=..., js=..., ts=..., java=...)       a program in all four languages, run for real at build time
    K.quiz('e', question, options, answer_index, hint, why)
    K.calc('e', question, '12', hint, [step, step, ...], check=3 * 4)
    K.practice(id, 'm', title, code_key, statement, example, hint, approach, time, space)
    K.say(part_id, heading, en, hi, kn, od, ar, de)       narration in the six narrator languages

calc(check=...) is the answer worked out in Python. The build fails if it does not match the written answer,
so a typing slip in an answer can never reach the page.

The small functions below write the boxes that the lessons share: formulas, memory tricks, worked examples,
"where machine learning uses this" notes and stacked fractions.
"""
import json
import html as _html


class Kit:
    def __init__(self):
        self.codes, self.quizzes, self.calcs, self.practices, self.says = {}, [], [], [], []

    def code(self, key, py, js, ts, java):
        if key in self.codes:
            raise SystemExit(f'code block {key} is written twice')
        self.codes[key] = {'py': py, 'js': js, 'ts': ts, 'java': java}

    def quiz(self, lv, q, o, a, hint, why, code=None, lang=None):
        d = {'lv': lv, 'q': q, 'o': o, 'a': a, 'hint': hint, 'why': why}
        if code:
            d['code'] = code.strip('\n')
            d['lang'] = lang or 'py'
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

    def practice(self, id, lv, title, code, statement, example, hint, approach, time, space):
        self.practices.append({'id': id, 'lv': lv, 'title': title, 'code': code, 'statement': statement, 'example': example,
                               'hint': hint, 'approach': approach, 'time': time, 'space': space})

    def say(self, id, h, en, hi, kn, od, ar, de):
        self.says.append({'id': id, 'h': h, 'en': en, 'hi': hi, 'kn': kn, 'or': od, 'ar': ar, 'de': de})

    def topic(self, **t):
        t.update(codes=self.codes, quiz=self.quizzes, calc=self.calcs, practice=self.practices, say=self.says)
        return t


def part(id, emoji, title, html, kw=None):
    return {'id': id, 'emoji': emoji, 'title': title, 'html': html, 'kw': kw or []}


# ---------- boxes used inside the lessons ----------
def fx(title, body, note=''):
    """A highlighted formula card. body is the formula, note says what each letter means."""
    n = f'<div class="fx-n">{note}</div>' if note else ''
    return f'<div class="fx"><div class="fx-h">🧮 {title}</div><div class="fx-b">{body}</div>{n}</div>'


def fxs(*cards):
    """Several formula cards side by side."""
    return '<div class="fx-grid">' + ''.join(cards) + '</div>'


def trick(text):
    return f'<div class="trick">{text}</div>'


def ml(text):
    return f'<div class="mlnote">{text}</div>'


def life(text):
    return f'<div class="life">{text}</div>'


def frac(a, b):
    """A stacked fraction: a over b."""
    return f'<span class="fr"><span>{a}</span><span>{b}</span></span>'


def mat(rows, cls=''):
    """A matrix with square brackets. rows is a list of lists of numbers or html."""
    body = ''.join('<span class="mr">' + ''.join(f'<span>{v}</span>' for v in r) + '</span>' for r in rows)
    return f'<span class="mx {cls}">{body}</span>'


def vec(vals):
    """A column vector."""
    return mat([[v] for v in vals])


def worked(title, steps, sub='Press Play, or step through it one line at a time.'):
    """A worked example that reveals its steps one by one."""
    return (f'<div class="viz" data-viz="walk" data-title="{_html.escape(title)}" data-sub="{_html.escape(sub)}" '
            f'data-steps="{_html.escape(json.dumps(steps, ensure_ascii=False))}"></div>')


def table(head, rows):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'<div class="tw"><table class="jt"><tr>{h}</tr>{b}</table></div>'


def code(key, label):
    return f'<div class="c3" data-k="{key}" data-label="{_html.escape(label)}"></div>'


def viz(name, **data):
    attrs = ''.join(f' data-{k}="{_html.escape(str(v))}"' for k, v in data.items())
    return f'<div class="viz" data-viz="{name}"{attrs}></div>'
