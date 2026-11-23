"""Add the Material 3 layer to chapter pages.

Usage: python3 tools/md3-build/inject.py content/java/*.html
Adds, once per page (marked with <!-- md3 -->), the Material fonts, assets/md3.css as the last stylesheet and
assets/md3chapter.js. Run it again after a subject builder rewrites its pages. --remove takes the layer out.
"""
import os, re, sys

FONTS = ('https://fonts.googleapis.com/css2?family=Google+Sans+Flex:wght@400;500;600;700'
         '&family=Roboto+Mono:wght@500;700&display=swap')
# Material Symbols, only the icons the site uses. Google Fonts needs the names in A to Z order.
ICONS = sorted(set('''account_tree arrow_back arrow_forward auto_stories bug_report casino check_circle chevron_right close code
computer dark_mode dns emoji_events expand_more fullscreen fullscreen_exit history home light_mode lightbulb list menu
menu_open open_in_new play_arrow psychology quiz school search shield task_alt timer travel_explore'''.split()))
SYMBOLS = ('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400..500,0..1,0'
           '&icon_names=' + ','.join(ICONS) + '&display=block')
MARK = '<!-- md3 -->'
BLOCK = re.compile(r'\n?<!-- md3 -->.*?<!-- /md3 -->', re.S)


def rel_assets(path):
    d = os.path.dirname(os.path.abspath(path))
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.relpath(os.path.join(root, 'assets'), d).replace(os.sep, '/')


def process(path, remove=False):
    s = open(path, encoding='utf-8').read()
    s = BLOCK.sub('', s)
    if not remove:
        a = rel_assets(path)
        head = (f'\n{MARK}<link href="{FONTS}" rel="stylesheet">\n<link href="{SYMBOLS}" rel="stylesheet">\n'
                f'<link rel="stylesheet" href="{a}/md3.css"><!-- /md3 -->\n')
        body = f'\n{MARK}<script src="{a}/md3chapter.js"></script><!-- /md3 -->\n'
        if '</head>' not in s or '</body>' not in s:
            print('skip (no head or body end):', path)
            return False
        i = s.rindex('</head>'); s = s[:i] + head + s[i:]
        i = s.rindex('</body>'); s = s[:i] + body + s[i:]
    open(path, 'w', encoding='utf-8').write(s)
    return True


if __name__ == '__main__':
    args = sys.argv[1:]
    remove = '--remove' in args
    files = [f for f in args if f != '--remove']
    n = sum(process(f, remove) for f in files)
    print(('removed from' if remove else 'added to'), n, 'pages')
