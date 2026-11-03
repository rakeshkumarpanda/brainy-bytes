"""Extra boxes for the Git and CI/CD topic files, on top of tools/cv-build/cvkit.py.

    sh(title, src, out='')            terminal commands with a $ prompt. Lines that start with # are comments.
    file(path, src, notes={})         a file to create, with line numbers, a Copy button and a note for chosen lines
                                      (notes maps a line number to what that line does and why)
    starter(path, notes={})           the same, but the text is read from tools/git-build/starter/<path>, the sample
                                      project that was run for real and checked with actionlint and the GitLab schema
    devqa(dev, qa, title)             the same topic seen by a developer and by a QA engineer, side by side
    changes(rows)                     a "what to change and why" table: [line or setting, change, why, who]
    flow(*items)                      a numbered left to right flow of boxes. items are (title, text)
    babystep(n, title, html)          one numbered baby step with a "Done" tick box

Everything inside <pre> and <code> is skipped by the house style check, so YAML and shell keep their own punctuation.
"""
import html as _h
import os

HERE = os.path.dirname(os.path.abspath(__file__))
STARTER = os.path.join(HERE, 'starter')


def _esc(s):
    return _h.escape(s, quote=False)


def sh(title, src, out='', cap='What you will see'):
    lines = []
    for l in src.strip('\n').split('\n'):
        if l.startswith('#'):
            lines.append(f'<span class="ln gc">{_esc(l)}</span>')
        else:
            lines.append(f'<span class="ln">{_esc(l) or " "}</span>')
    o = f'<div class="cc-cap">{cap}</div><pre class="cc-out">{_esc(out.strip(chr(10)))}</pre>' if out else ''
    return (f'<div class="cv-code gk-sh"><div class="cc-bar"><span class="lbl">{_esc(title)}</span>'
            f'<button type="button" class="gk-copy">Copy</button></div><pre class="cc-src">{"".join(lines)}</pre>{o}</div>')


def file(path, src, notes=None, lang='yaml', title=''):
    notes = notes or {}
    rows = src.strip('\n').split('\n')
    for n in notes:
        if not 1 <= n <= len(rows):
            raise SystemExit(f'file {path}: note for line {n}, but the file has {len(rows)} lines')
    body = ''.join(f'<span class="ln{" gk-has" if i in notes else ""}" data-n="{i}">{_esc(l) or " "}</span>' for i, l in enumerate(rows, 1))
    nl = ''
    if notes:
        items = ''.join(f'<li data-n="{n}"><b>Line {n}</b><code>{_esc(rows[n - 1].strip())}</code><span>{t}</span></li>' for n, t in sorted(notes.items()))
        nl = (f'<details class="gk-notes" open><summary>What each marked line does and why</summary><ol>{items}</ol></details>')
    head = f'<span class="gk-path">{_esc(path)}</span>' + (f'<span class="gk-ft">{_esc(title)}</span>' if title else '')
    return (f'<div class="cv-code gk-file" data-lang="{lang}"><div class="cc-bar">{head}<span class="grow"></span>'
            f'<button type="button" class="gk-copy">Copy</button></div><pre class="cc-src gk-hl" data-hl="{lang}">{body}</pre>{nl}</div>')


def read_starter(path):
    return open(os.path.join(STARTER, path), encoding='utf-8').read()


def starter(path, notes=None, lang=None, title=''):
    if lang is None:
        lang = 'yaml' if path.endswith(('.yml', '.yaml')) else 'py' if path.endswith('.py') else 'text'
    return file(path, read_starter(path), notes, lang, title)


def devqa(dev, qa, title='The same thing, seen by Dev and by QA'):
    return (f'<div class="gk-dq"><div class="gk-dq-h">{title}</div><div class="gk-dq-g">'
            f'<div class="gk-dev"><b>Developer view</b>{dev}</div><div class="gk-qa"><b>QA view</b>{qa}</div></div></div>')


def changes(rows, title='What to change and why'):
    h = '<tr><th>Line or setting</th><th>Change it to</th><th>Why</th><th>Who cares most</th></tr>'
    b = ''.join(f'<tr><td><code>{_esc(a)}</code></td><td>{c}</td><td>{w}</td><td><span class="gk-who gk-{who.lower()}">{who}</span></td></tr>'
                for a, c, w, who in rows)
    return f'<div class="gk-chg"><div class="gk-chg-h">{title}</div><div class="tw"><table class="cvt">{h}{b}</table></div></div>'


def flow(*items):
    return '<ol class="gk-flow">' + ''.join(f'<li><b>{t}</b><span>{x}</span></li>' for t, x in items) + '</ol>'


def babystep(n, title, body):
    return (f'<div class="gk-baby"><label class="gk-bh"><input type="checkbox" class="gk-done"><span class="gk-bn">Step {n}</span>'
            f'<span class="gk-bt">{title}</span></label><div class="gk-bb">{body}</div></div>')
