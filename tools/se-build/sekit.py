"""Extra boxes for the Selenium topic files, on top of tools/cv-build/cvkit.py.

    tri(key, title, java=..., py=..., js=..., mode=..., needs=None, extra=None, fail=False)

writes one example in Java, Python and JavaScript. Each source line may end with  ## explanation , which is cut off
before the code runs and shown on the page as the note for that line, so a reader can walk the program line by line.
Every example runs for real at build time (runner.py) and the page shows what it printed.

    mode    'script' (default), or a dict per language such as {'java': 'junit', 'py': 'pytest', 'js': 'mocha'}
    needs   'grid' starts a Selenium Grid on http://localhost:4444 first
    extra   {'py': {'pages/login_page.py': src}, ...} more files of the same project, shown above the main file
    fail    True when the example is meant to end with an error, so the page shows the real error
    expect  a string every output must contain, a cheap check that the run did what the lesson says

    shell(title, src, out='', cap=...) shows terminal commands that are not run on the page.
"""
import html as _h
import re

import runner

LANGS = (('java', 'Java'), ('py', 'Python'), ('js', 'JavaScript'))
NOTE = re.compile(r'\s+## (.*)$')
BAD = (('—', 'em dash'), ('–', 'en dash'), (';', 'semicolon'))
_keys = set()


def _style(where, s):
    t = re.sub(r'<code>[\s\S]*?</code>|<[^>]+>|&[#\w]+;', ' ', s)
    for ch, label in BAD:
        if ch in t:
            raise SystemExit(f'{where}: {label} in note "{s}"')


def _split(src, where):
    """Return the clean code and a list of (line number, note)."""
    code, notes = [], []
    for i, line in enumerate(src.strip('\n').split('\n'), 1):
        m = NOTE.search(line)
        if m:
            _style(where, m.group(1))
            notes.append((i, m.group(1)))
            line = line[:m.start()]
        code.append(line.rstrip())
    return '\n'.join(code), notes


def _main_name(lang, mode, code):
    if lang == 'py':
        return 'test_example.py' if mode == 'pytest' else 'main.py'
    if lang == 'js':
        return 'example.spec.js' if mode == 'mocha' else 'main.js'
    m = re.search(r'public\s+(?:final\s+)?class\s+(\w+)', code)
    pkg = re.search(r'^package\s+([\w.]+);', code, re.M)
    name = (m.group(1) if m else 'Main') + '.java'
    return (pkg.group(1).replace('.', '/') + '/' if pkg else '') + name


def _file_html(path, code, notes, lang):
    lines = ''.join(f'<span class="ln"{" data-n=" + chr(34) + str(k) + chr(34) if any(n == i for n, _ in notes) else ""}>{_h.escape(l) or " "}</span>'
                    for i, l in enumerate(code.split('\n'), 1) for k in [i])
    note_html = ''.join(f'<li data-n="{n}">{t}</li>' for n, t in notes)
    return (f'<div class="se-file" data-lang="{lang}"><div class="se-fname">{_h.escape(path)}</div>'
            f'<pre class="cc-src se-src">{lines}</pre><ol class="se-notes" hidden>{note_html}</ol></div>')


def tri(key, title, java, py, js, mode='script', needs=None, extra=None, fail=False, expect=None):
    if key in _keys:
        raise SystemExit(f'example {key} is written twice')
    _keys.add(key)
    srcs = {'java': java, 'py': py, 'js': js}
    panes = []
    for lang, name in LANGS:
        md = mode.get(lang, 'script') if isinstance(mode, dict) else mode
        code, notes = _split(srcs[lang], f'example {key} {name}')
        if not notes:
            raise SystemExit(f'example {key} {name} has no line notes')
        files, shown = {}, []
        main = _main_name(lang, md, code)
        files[main] = code
        for p, s in ((extra or {}).get(lang) or {}).items():
            c2, n2 = _split(s, f'example {key} {name} {p}')
            files[p] = c2
            shown.append(_file_html(p, c2, n2, lang))
        shown.append(_file_html(main, code, notes, lang))
        out, rc = runner.run(lang, files, md, needs, label=key)
        if fail and not rc:
            raise SystemExit(f'example {key} {name} should fail but exited 0:\n{out}')
        if not fail and rc:
            raise SystemExit(f'example {key} {name} failed:\n{out}')
        if expect and expect not in out:
            raise SystemExit(f'example {key} {name}: the output does not contain {expect!r}:\n{out}')
        cap = (f'Real error from this run ({runner.VERSIONS})' if fail else f'Real output from this run ({runner.VERSIONS})')
        how = {'script': '', 'pytest': ' run with pytest', 'mocha': ' run with Mocha', 'junit': ' run with JUnit 5'}[md]
        panes.append(f'<div class="se-pane" data-lang="{lang}"{"" if lang == "java" else " hidden"}>{"".join(shown)}'
                     f'<div class="cc-cap">{cap}{how}</div><pre class="cc-out">{_h.escape(out) or "(nothing printed)"}</pre></div>')
    tabs = ''.join(f'<button type="button" class="se-lt" data-lang="{l}">{n}</button>' for l, n in LANGS)
    return (f'<div class="se-tri" data-k="{key}"><div class="cc-bar se-bar"><span class="lbl">{_h.escape(title)}</span>'
            f'<span class="se-lts" role="tablist">{tabs}</span><span class="grow"></span>'
            f'<button type="button" class="se-walk">Explain line by line</button><button type="button" class="se-copy">Copy</button></div>'
            f'{"".join(panes)}</div>')


def solo(key, title, lang, src, mode='script', needs=None, fail=False, expect=None, why=''):
    """One example in a single language, for things only one binding shows well. why says so on the page."""
    if key in _keys:
        raise SystemExit(f'example {key} is written twice')
    _keys.add(key)
    name = dict(LANGS)[lang]
    code, notes = _split(src, f'example {key} {name}')
    main = _main_name(lang, mode, code)
    out, rc = runner.run(lang, {main: code}, mode, needs, label=key)
    if bool(rc) != bool(fail):
        raise SystemExit(f'example {key} {name} exit {rc}:\n{out}')
    if expect and expect not in out:
        raise SystemExit(f'example {key} {name}: the output does not contain {expect!r}:\n{out}')
    cap = f'Real {"error" if fail else "output"} from this run ({runner.VERSIONS})'
    w = f'<div class="se-why">{why}</div>' if why else ''
    return (f'<div class="se-tri se-solo" data-k="{key}"><div class="cc-bar se-bar"><span class="lbl">{_h.escape(title)}</span>'
            f'<span class="se-lts"><button type="button" class="se-lt on" data-lang="{lang}" disabled>{name}</button></span><span class="grow"></span>'
            f'<button type="button" class="se-walk">Explain line by line</button><button type="button" class="se-copy">Copy</button></div>{w}'
            f'<div class="se-pane" data-lang="{lang}">{_file_html(main, code, notes, lang)}'
            f'<div class="cc-cap">{cap}</div><pre class="cc-out">{_h.escape(out) or "(nothing printed)"}</pre></div></div>')


def shell(title, src, out='', cap='What you will see'):
    """Terminal commands shown on the page but not run by the build."""
    lines = ''.join(f'<span class="ln">{_h.escape(l) or " "}</span>' for l in src.strip('\n').split('\n'))
    o = f'<div class="cc-cap">{cap}</div><pre class="cc-out">{_h.escape(out.strip(chr(10)))}</pre>' if out else ''
    return f'<div class="cv-code se-shell"><div class="cc-bar"><span class="lbl">{_h.escape(title)}</span></div><pre class="cc-src">{lines}</pre>{o}</div>'


def src(lang, s, title=''):
    """A short code fragment in one language, highlighted on the page, not run."""
    return f'<div class="se-snip" data-lang="{lang}">{"<div class=se-fname>" + _h.escape(title) + "</div>" if title else ""}<pre class="cc-src se-hl" data-hl="{lang}">{_h.escape(s.strip(chr(10)))}</pre></div>'


def flow(*items):
    """A numbered left to right flow of boxes, for request journeys. items are (title, text)."""
    return '<ol class="se-flow">' + ''.join(f'<li><b>{t}</b><span>{x}</span></li>' for t, x in items) + '</ol>'
