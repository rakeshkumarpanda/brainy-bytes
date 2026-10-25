"""Helpers for the Manual Testing page sources in pages/ and adds/.

Every helper returns plain HTML or plain data. build.py turns a page source into a finished page,
or merges an add source into an existing page.
"""

LANGS = ('en', 'hi', 'kn', 'or', 'ar', 'de')


def sec(id, emoji, title, html, say):
    """One lesson part. say is a dict with the narration per language, en is required."""
    assert 'en' in say, id
    return dict(id=id, emoji=emoji, title=title, html=html.strip(), say=say)


def table(head, *rows, cls=''):
    th = ''.join(f'<th>{h}</th>' for h in head)
    tr = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<div class="tw"><table class="jt{(" " + cls) if cls else ""}"><tr>{th}</tr>\n{tr}</table></div>'


def box(h, p):
    return f'<div class="box"><h4>{h}</h4><p>{p}</p></div>'


def grid(*boxes):
    return '<div class="grid2">\n' + '\n'.join(boxes) + '\n</div>'


def tip(t):
    return f'<div class="tip">{t}</div>'


def rule(t):
    return f'<div class="rule">{t}</div>'


def exam(t):
    return f'<div class="exam">{t}</div>'


def warn(t):
    return f'<div class="warn">{t}</div>'


def viz(name, k=''):
    return f'<div class="viz" data-viz="{name}"' + (f' data-k="{k}"' if k else '') + '></div>'


def flow(k):
    return viz('flow', k)


def deep(title, html):
    """A 'go deeper' panel that opens on click, for the expert level detail."""
    return f'<details class="m2-deep"><summary>🔎 Go deeper: {title}</summary><div class="m2-dbody">{html}</div></details>'


def say(en, hi='', kn='', or_='', ar='', de=''):
    d = dict(en=en, hi=hi, kn=kn, ar=ar, de=de)
    d['or'] = or_
    return {k: v for k, v in d.items() if v}


def Qz(lv, q, options, answer, hint, why):
    return dict(lv=lv, q=q, o=list(options), a=answer, hint=hint, why=why)


def Calc(lv, q, ans, py, hint, steps, unit=''):
    d = dict(lv=lv, q=q, ans=str(ans), py=py, hint=hint, steps=list(steps))
    if unit:
        d['unit'] = unit
    return d


def eq(t):
    return f'<span class="eq">{t}</span>'


def fr(top, bottom):
    return f'<span class="fr"><i>{top}</i><i>{bottom}</i></span>'
