"""Extra boxes for the GPU Programming topic files, on top of tools/cv-build/cvkit.py.

    cu(path, src, notes={}, title='', check=True, out='')
        a CUDA C++ file or kernel with line numbers, a Copy button and a note for chosen lines (notes maps a line
        number to what that line does and why). Every listing with check=True is compiled by build.py when
        BB_CUDA_PATH is set (device code through clang and ptxas, host code checked for syntax), so the code on the
        page is known to compile. out is the output the program prints, shown under the code.
    sh(title, src, out='')    terminal commands with a $ prompt (nvcc, nsys, ncu, compute-sanitizer)
    nb(file, title, what)     a card that downloads a Jupyter notebook from content/cuda/notebooks/
    flow(*items)              a numbered left to right flow of boxes. items are (title, text)

Everything inside <pre> and <code> is skipped by the house style check, so C++ keeps its own semicolons.
"""
import html as _h

LISTINGS = []          # (path, src, check) of every cu() listing, compiled by build.py


def _esc(s):
    return _h.escape(s, quote=False)


def cu(path, src, notes=None, title='', check=True, out='', lang='cuda'):
    notes = notes or {}
    rows = src.strip('\n').split('\n')
    for n in notes:
        if not 1 <= n <= len(rows):
            raise SystemExit(f'listing {path}: note for line {n}, but it has {len(rows)} lines')
    LISTINGS.append((path, src.strip('\n') + '\n', check and lang == 'cuda'))
    body = ''.join(f'<span class="ln{" ck-has" if i in notes else ""}" data-n="{i}">{_esc(l) or " "}</span>' for i, l in enumerate(rows, 1))
    nl = ''
    if notes:
        items = ''.join(f'<li data-n="{n}"><b>Line {n}</b><code>{_esc(rows[n - 1].strip())}</code><span>{t}</span></li>' for n, t in sorted(notes.items()))
        nl = f'<details class="ck-notes" open><summary>What each marked line does and why</summary><ol>{items}</ol></details>'
    o = f'<div class="cc-cap">What it prints</div><pre class="cc-out">{_esc(out.strip(chr(10)))}</pre>' if out else ''
    head = f'<span class="ck-path">{_esc(path)}</span>' + (f'<span class="ck-ft">{_esc(title)}</span>' if title else '')
    return (f'<div class="cv-code ck-file"><div class="cc-bar">{head}<span class="grow"></span>'
            f'<button type="button" class="ck-copy">Copy</button></div><pre class="cc-src ck-hl" data-hl="{lang}">{body}</pre>{nl}{o}</div>')


def sh(title, src, out='', cap='What you will see'):
    lines = []
    for l in src.strip('\n').split('\n'):
        cls = 'ln ck-c' if l.startswith('#') else 'ln'
        lines.append(f'<span class="{cls}">{_esc(l) or " "}</span>')
    o = f'<div class="cc-cap">{cap}</div><pre class="cc-out">{_esc(out.strip(chr(10)))}</pre>' if out else ''
    return (f'<div class="cv-code ck-sh"><div class="cc-bar"><span class="lbl">{_esc(title)}</span><span class="grow"></span>'
            f'<button type="button" class="ck-copy">Copy</button></div><pre class="cc-src">{"".join(lines)}</pre>{o}</div>')


def nb(file, title, what):
    return (f'<div class="ck-nb"><div class="ck-nb-i">ipynb</div><div class="ck-nb-t"><b>{title}</b><span>{what}</span>'
            f'<small>Open it in Google Colab (Runtime, Change runtime type, T4 GPU) or in Jupyter on a machine with an NVIDIA GPU. '
            f'Every code line is explained in the cell under it.</small></div>'
            f'<a class="ck-nb-a" href="./notebooks/{file}" download>Download notebook</a></div>')


def flow(*items):
    return '<ol class="ck-flow">' + ''.join(f'<li><b>{t}</b><span>{x}</span></li>' for t, x in items) + '</ol>'
