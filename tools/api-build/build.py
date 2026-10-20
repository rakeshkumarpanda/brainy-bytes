"""Builds the standalone API testing pages.

The shared theme, quiz, comic and narrator code is copied from an existing
TestNG page so every page on the site looks and behaves the same. The lesson
itself lives in the files under manual/, which are plain HTML, CSS and JS.

    python3 tools/api-build/build.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SHARED = ROOT / 'content/testng/testng-foundations.html'


def between(text, start, end):
    a = text.index(start)
    b = text.index(end, a)
    return text[a:b]


def shared_parts():
    src = SHARED.read_text(encoding='utf-8')
    css = between(src, '/* ===== Shared platform theme', '/* ===== Animations ===== */')
    js = between(src, '/* ===== Shared fun layer', '/* ===================== Line by line execution viewer')
    return css, js


def build(name, out):
    css, js = shared_parts()
    d = HERE / name
    page = (d / 'page.html').read_text(encoding='utf-8')
    page = page.replace('/*@SHARED_CSS@*/', css)
    page = page.replace('/*@PAGE_CSS@*/', (d / 'style.css').read_text(encoding='utf-8'))
    page = page.replace('/*@SHARED_JS@*/', js)
    page = page.replace('/*@IQ_CSS@*/', (ROOT / 'assets/interview.css').read_text(encoding='utf-8'))
    page = page.replace('/*@IQ_JS@*/', (ROOT / 'assets/interview.js').read_text(encoding='utf-8'))
    page = page.replace('/*@PAGE_JS@*/', '\n'.join((d / f).read_text(encoding='utf-8') for f in ('data.js', 'interview.js', 'widgets.js', 'glue.js')))
    target = ROOT / out
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page, encoding='utf-8')
    print(f'wrote {out} ({len(page) // 1024} KB)')


if __name__ == '__main__':
    build('manual', 'content/api-testing/manual-api-testing.html')
