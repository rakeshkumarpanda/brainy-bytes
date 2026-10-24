"""Helpers the Java topic files use to describe a chapter. See build.py for what each kind of example does."""


def part(id, emoji, title, html, kw=None):
    """One part of a chapter. [[key]] in html places the code block CODES[key]."""
    return {'id': id, 'emoji': emoji, 'title': title, 'html': html, 'kw': kw or []}


def j(code, label, expect='ok', jdk=25, preview=False, trace=True, more=None, args=None, stdin='', tail=None, replace=None, note=None):
    """A Java program compiled with javac and run with java at build time. The real output is shown under it.
    expect: 'ok' runs cleanly, 'throw' ends with an exception on purpose, 'compile' must not compile.
    jdk: 25 (the current LTS) or 27 (the newest release, for preview features with preview=True).
    trace: record the run line by line for the step viewer (only for single threaded programs).
    more: extra source files {name: code} compiled together with Main.java."""
    return {'t': 'java', 'code': code, 'label': label, 'expect': expect, 'jdk': jdk, 'preview': preview,
            'trace': trace and expect != 'compile', 'more': more or {}, 'args': args or [], 'stdin': stdin,
            'tail': tail, 'replace': replace or [], 'note': note}


def sh(files, cmd, label, jdk=25, shown=None, expect='ok', tail=None, replace=None, keep=None):
    """A small project run with a shell command (javac, java, javap, jar, jshell ...) with the JDK on PATH.
    files: {path: text}. The terminal output is shown exactly as printed. keep lists the files to print (all by default)."""
    return {'t': 'sh', 'files': files, 'cmd': cmd, 'label': label, 'jdk': jdk, 'shown': shown or cmd, 'expect': expect,
            'tail': tail, 'replace': replace or [], 'keep': keep}


def show(code, label, lang='java', note='Not run on this page', result=None):
    """Code that is shown but not run here. result is a sentence about what it does."""
    return {'t': 'show', 'code': code, 'label': label, 'lang': lang, 'note': note, 'result': result}


def say(id, h, en, hi, kn, od, ar, de):
    """Narration for one part in the six narrator languages."""
    return {'id': id, 'h': h, 'en': en, 'hi': hi, 'kn': kn, 'or': od, 'ar': ar, 'de': de}


def quiz(lv, q, o, a, hint, why, code=None, run=False, jdk=25, preview=False):
    """A quiz question. With run=True the code is run at build time and its output must equal option a."""
    d = {'lv': lv, 'q': q, 'o': o, 'a': a, 'hint': hint, 'why': why}
    if code:
        d['code'] = code.strip('\n')
    if run:
        d['run'] = 1
        d['_jdk'] = jdk
        d['_preview'] = preview
    return d


def calc(lv, q, ans, hint, steps, code=None, run=False, alt=None):
    """A number crunch question. With run=True the code is run at build time and must print ans."""
    d = {'lv': lv, 'q': q, 'ans': ans, 'hint': hint, 'steps': steps}
    if code:
        d['code'] = code.strip('\n')
    if run:
        d['run'] = 1
    if alt:
        d['alt'] = alt
    return d


def panel(scene, h, t, more):
    return {'s': scene, 'h': h, 't': t, 'more': more}
