"""Prints the lessons of chapter pages with their ids and a short digest of what each lesson says.

    python3 tools/voice/digest.py content/python/py-start.html [more pages] [--words 120]

Used to write data/talk/<subject>/<page>.js talks that match the lesson, and to check them.
"""
import re, sys, html

def lessons(s):
    out = []
    pat = re.compile(r'<(article) class="cv-lesson[^"]*" id="([^"]+)"[^>]*>(.*?)</article>|<(section) class="[^"]*\bjsec\b[^"]*" id="([^"]+)"[^>]*>(.*?)</section>', re.S)
    for m in pat.finditer(s):
        lid = m.group(2) or m.group(5)
        body = m.group(3) or m.group(6)
        out.append((lid, body))
    return out

def text(body):
    b = re.sub(r'<(script|style|pre|table|canvas|svg|code)[^>]*>.*?</\1>', ' ', body, flags=re.S)
    b = re.sub(r'<div class="cvz[^>]*>.*?</div>', ' ', b, flags=re.S)
    h = re.search(r'<h2[^>]*>(.*?)</h2>', b, re.S)
    title = html.unescape(re.sub(r'<[^>]+>', '', h.group(1))).strip() if h else ''
    heads = [html.unescape(re.sub(r'<[^>]+>', '', x)).strip() for x in re.findall(r'<h[34][^>]*>(.*?)</h[34]>', b, re.S)]
    t = html.unescape(re.sub(r'<[^>]+>', ' ', b))
    t = re.sub(r'\s+', ' ', t).strip()
    return title, heads, t

if __name__ == '__main__':
    args = sys.argv[1:]
    words = 120
    if '--words' in args:
        k = args.index('--words'); words = int(args[k + 1]); del args[k:k + 2]
    for f in args:
        s = open(f, encoding='utf-8').read()
        print('=====', f)
        for lid, body in lessons(s):
            title, heads, t = text(body)
            w = t.split()
            print(f'[{lid}] {title}')
            if heads: print('  parts: ' + ' | '.join(h for h in heads if h)[:300])
            print('  ' + ' '.join(w[:words]))
