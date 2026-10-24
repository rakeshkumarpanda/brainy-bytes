"""Small helpers the topic files use to describe a chapter. See build.py for what each kind of example does."""


def part(id, emoji, title, html, qa=None, kw=None, qa_why=None, lvl=None):
    """One part of a chapter. qa marks it as needed for test automation: True, or a list of tool names.
    lvl is 'b', 'i', 'a' or 'x' (beginner, intermediate, advanced, expert) and shows as a tag on the part."""
    return {'id': id, 'emoji': emoji, 'title': title, 'html': html, 'qa': qa, 'kw': kw or [], 'qa_why': qa_why, 'lvl': lvl}


def run(code, label, **kw):
    """One Python file run with CPython. stdin='...' types text at the keyboard, expect='throw' when it fails on purpose,
    flags=['-X', 'importtime'] adds interpreter options, extra={name: text} adds more files next to main.py,
    trace=False skips the line by line recording, play=False hides "Edit and run" (for code that needs a real terminal)."""
    return {'t': 'run', 'code': code, 'label': label, **kw}


def test(files, cmd, label, **kw):
    """A small project run with a shell command. show lists the files to print (all by default),
    shown_cmd is the command the reader sees, expect='fail' when the command fails on purpose."""
    return {'t': 'test', 'files': files, 'cmd': cmd, 'label': label, **kw}


def show(code, label, lang='py', note='Not run on this page', result=None):
    """Code that is shown but not run here. result is a sentence about what it does."""
    return {'t': 'show', 'code': code, 'label': label, 'lang': lang, 'note': note, 'result': result}


def say(id, h, en, hi, kn, od, ar, de):
    """Narration for one part in the six narrator languages."""
    return {'id': id, 'h': h, 'en': en, 'hi': hi, 'kn': kn, 'or': od, 'ar': ar, 'de': de}


def quiz(lv, q, o, a, hint, why, code=None):
    d = {'lv': lv, 'q': q, 'o': o, 'a': a, 'hint': hint, 'why': why}
    if code:
        d['code'] = code.strip('\n')
    return d


def calc(lv, q, ans, hint, steps, code=None, alt=None):
    d = {'lv': lv, 'q': q, 'ans': ans, 'hint': hint, 'steps': steps}
    if code:
        d['code'] = code.strip('\n')
    if alt:
        d['alt'] = alt
    return d


def ex(id, lv, title, task, starter, tests, solution, hint='', why=''):
    """A hands-on exercise. tests is a list of (Python expression, expected value as JSON)."""
    return {'id': id, 'lv': lv, 'title': title, 'task': task, 'starter': starter.strip('\n'),
            'tests': [{'call': c, 'want': w} for c, w in tests], 'solution': solution.strip('\n'), 'hint': hint, 'why': why}


def panel(scene, h, t, more):
    return {'s': scene, 'h': h, 't': t, 'more': more}
