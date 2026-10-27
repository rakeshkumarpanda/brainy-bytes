"""Screenshots of the four framework projects' folders, drawn the way an editor's file explorer shows them.

Reads the real folders in tools/pw-build/frameworks/<lang>, so the picture always matches the code the
framework chapter runs. Folders come first, then files, both sorted by name, as VS Code sorts them.
A short note next to each folder says what goes in it.
Output: content/playwright/img/framework-tree-<lang>.png
Run:  tools/pw-build/box/.venv/bin/python tools/pw-build/screens/trees.py
"""
import html
import os

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
PW = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PW))
IMG = os.path.join(ROOT, 'content', 'playwright', 'img')
FW = os.path.join(PW, 'frameworks')
# folders that runs leave behind and Git ignores
SKIP = ('__pycache__', 'node_modules', 'target', 'traces', 'test-results', 'playwright-report', 'blob-report', 'results', '.pytest_cache')

NOTES = {
    'ts': {'.github/workflows': 'the CI pipeline', 'src': 'the framework code', 'src/api': 'fast set up through the API',
           'src/components': 'parts on many pages', 'src/config': 'settings per machine', 'src/data': 'test users and products',
           'src/fixtures': 'hands objects to tests', 'src/pages': 'one class per screen', 'tests': 'tests only, by feature'},
    'python': {'.github/workflows': 'the CI pipeline', 'framework': 'the framework code', 'framework/api': 'fast set up through the API',
               'framework/components': 'parts on many pages', 'framework/data': 'test users and products',
               'framework/pages': 'one class per screen', 'tests': 'tests only, by feature'},
    'java': {'.github/workflows': 'the CI pipeline', 'src/main/java/com/brainy/shop': 'the framework code',
             'src/main/java/com/brainy/shop/api': 'fast set up through the API', 'src/main/java/com/brainy/shop/components': 'parts on many pages',
             'src/main/java/com/brainy/shop/config': 'settings per machine', 'src/main/java/com/brainy/shop/data': 'test users and products',
             'src/main/java/com/brainy/shop/pages': 'one class per screen', 'src/test/java/com/brainy/shop/base': 'opens and closes the browser',
             'src/test/java/com/brainy/shop/tests': 'tests only, by feature', 'src/test/resources': 'default settings'},
}
NOTES['js'] = NOTES['ts']
FILE_NOTES = {'playwright.config.ts': 'runner settings', 'playwright.config.js': 'runner settings', 'conftest.py': 'fixtures',
              'pytest.ini': 'runner settings', 'testng.xml': 'the full suite', 'testng-smoke.xml': 'the smoke suite', 'pom.xml': 'dependencies',
              '.env.example': 'settings to copy', 'requirements.txt': 'exact versions', 'package.json': 'dependencies and scripts',
              'package-lock.json': 'exact versions'}

ICON = {'.ts': ('TS', '#3178c6'), '.js': ('JS', '#e8c400'), '.py': ('PY', '#3b7bbf'), '.java': ('J', '#e76f00'), '.json': ('{}', '#c9a227'),
        '.xml': ('<>', '#e37933'), '.yml': ('!', '#cb171e'), '.md': ('M', '#519aba'), '.properties': ('⚙', '#9aa4ae'),
        '.ini': ('⚙', '#9aa4ae'), '.txt': ('≡', '#9aa4ae'), '.gitignore': ('◆', '#f14e32'), '.example': ('$', '#e5c07b')}


def icon(name):
    for ext, v in ICON.items():
        if name.endswith(ext):
            return v
    return ('·', '#9aa4ae')


def rows(base, rel='', depth=0):
    out = []
    full = os.path.join(base, rel)
    names = sorted(os.listdir(full), key=str.lower)
    dirs = [n for n in names if os.path.isdir(os.path.join(full, n)) and n not in SKIP]
    files = [n for n in names if os.path.isfile(os.path.join(full, n)) and n != '__init__.py']
    for d in dirs:
        r = f'{rel}/{d}'.lstrip('/')
        # an editor folds a chain of single folders into one row, such as java/com/brainy/shop
        label, chain = d, r
        while True:
            inner = os.path.join(base, chain)
            kids = [k for k in os.listdir(inner) if k != '__pycache__']
            if len(kids) == 1 and os.path.isdir(os.path.join(inner, kids[0])) and chain not in NOTES_NOW:
                label += '/' + kids[0]
                chain += '/' + kids[0]
            else:
                break
        out.append(('dir', label, depth, NOTES_NOW.get(chain, '')))
        out += rows(base, chain, depth + 1)
    for f in files:
        out.append(('file', f, depth, FILE_NOTES.get(f, '')))
    return out


CSS = '''
body { margin: 0; background: #0f1115; font: 15px/1 "Segoe UI", "Inter", system-ui, sans-serif; }
.win { display: inline-block; margin: 0; background: #181a1f; color: #cccccc; min-width: 560px; border: 1px solid #2b2f36; }
.bar { height: 34px; display: flex; align-items: center; padding: 0 14px; font-size: 12px; letter-spacing: .08em; color: #9aa0a6; background: #181a1f; border-bottom: 1px solid #2b2f36; }
.root { padding: 7px 14px; font-weight: 700; font-size: 12px; letter-spacing: .06em; color: #e6e6e6; background: #20232a; }
.row { display: flex; align-items: center; height: 26px; padding-right: 18px; white-space: nowrap; }
.tw { color: #9aa0a6; width: 14px; display: inline-block; font-size: 11px; }
.ic { display: inline-flex; width: 22px; justify-content: center; font: 700 10px/1 ui-monospace, monospace; margin-right: 6px; }
.dir .name { color: #e6e6e6; }
.note { margin-left: auto; padding-left: 28px; color: #7c8591; font-size: 13px; font-style: italic; }
.guide { display: inline-block; width: 16px; height: 26px; border-left: 1px solid #2f343c; margin-left: 6px; box-sizing: border-box; }
'''


def page_html(lang, title):
    rs = rows(os.path.join(FW, lang))
    body = []
    for kind, name, depth, note in rs:
        guides = ''.join('<span class="guide"></span>' for _ in range(depth))
        if kind == 'dir':
            ic = '<span class="tw">⌄</span><span class="ic" style="color:#dcb67a">▰</span>'
        else:
            t, c = icon(name)
            ic = f'<span class="tw"></span><span class="ic" style="color:{c}">{html.escape(t)}</span>'
        n = f'<span class="note">{html.escape(note)}</span>' if note else ''
        body.append(f'<div class="row {kind}" style="padding-left:10px">{guides}{ic}<span class="name">{html.escape(name)}</span>{n}</div>')
    return (f'<!doctype html><meta charset="utf-8"><style>{CSS}</style><div class="win"><div class="bar">EXPLORER</div>'
            f'<div class="root">⌄ SHOP-TESTS · {html.escape(title)}</div>{"".join(body)}<div style="height:8px"></div></div>')


TITLES = {'ts': 'TypeScript', 'js': 'JavaScript', 'python': 'Python', 'java': 'Java'}
NOTES_NOW = {}

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(device_scale_factor=2, viewport={'width': 900, 'height': 900})
        for lang, title in TITLES.items():
            NOTES_NOW = NOTES[lang]
            pg.set_content(page_html(lang, title))
            out = os.path.join(IMG, f'framework-tree-{lang}.png')
            pg.locator('.win').screenshot(path=out)
            print('saved', out)
        b.close()
