"""Extra boxes for the NLP topic files, on top of tools/cv-build/cvkit.py."""
import html as _h


def listing(src, out='', title='Python with NLTK, as run in the class notebook', cap='Output recorded in the notebook'):
    """A program that is shown but not run on the page (it needs NLTK data), with the output the notebook printed."""
    lines = ''.join(f'<span class="ln">{_h.escape(l)}</span>' for l in src.strip('\n').split('\n'))
    o = f'<div class="cc-cap">{cap}</div><pre class="cc-out">{_h.escape(out.strip(chr(10)))}</pre>' if out else ''
    return f'<div class="cv-code"><div class="cc-bar"><span class="lbl">{title}</span></div><pre class="cc-src">{lines}</pre>{o}</div>'
