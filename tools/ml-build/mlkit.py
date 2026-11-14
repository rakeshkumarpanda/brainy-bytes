"""Small boxes the Machine Learning topic files use on top of cvkit, coreaikit and pykit.

    ossteps(title, mac, win, linux, chrome)   one setup task with a panel for each operating system
    link(sid, title, why, label)   a card that links to another subject on the site, for example the Complete
                                   Python subject (all of Python, Django, Flask and API handling) or Maths for ML
"""


def link(sid, title, why, label='Open the subject'):
    return (f'<div class="ml-link"><div><b>{title}</b><span>{why}</span></div>'
            f'<a class="ck-nb-a" href="../../subject.html?s={sid}" target="_top">{label}</a></div>')


OS_NAMES = (('mac', 'macOS'), ('win', 'Windows 10 and 11'), ('linux', 'Linux (Ubuntu, Debian, Fedora)'), ('chrome', 'ChromeOS (Chromebook)'))


def ossteps(title, mac, win, linux, chrome, open_first=True):
    """One setup task with separate instructions for each operating system. Each argument is HTML (steps and
    pykit.term() blocks). Every system is a collapsible panel, and the first one starts open."""
    out = [f'<div class="ml-os"><div class="ml-os-h">{title}</div>']
    for i, ((key, name), body) in enumerate(zip(OS_NAMES, (mac, win, linux, chrome))):
        out.append(f'<details class="ml-os-{key}"{" open" if open_first and i == 0 else ""}><summary>{name}</summary><div class="ml-os-b">{body}</div></details>')
    return ''.join(out) + '</div>'
