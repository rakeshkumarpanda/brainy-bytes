"""Helpers for the newer DSA chapters (four languages, English voice, playful animations, LeetCode practice).

    from kit4 import Topic
    t = Topic()
    t.code('key', py=..., js=..., java=..., ts=...)
    t.leet(136, 'e', 'p_single', statement=..., example=..., hint=..., approach=..., time=..., space=...)
    T = t.finish({...})      # checks the prose style rules and fills in the shared fields
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
IDX_PATH = os.path.join(HERE, 'leetcode_index.json')


def lc_index():
    """Every LeetCode solution already on the site: number -> list of {t, d, u, p, f}. Rebuilt from content/*/files."""
    rows = {}
    base = os.path.join(ROOT, 'content')
    for subj in sorted(os.listdir(base)):
        fd = os.path.join(base, subj, 'files')
        if not os.path.isdir(fd):
            continue
        for ch in sorted(os.listdir(fd)):
            if not os.path.isdir(os.path.join(fd, ch)):
                continue
            for fn in sorted(os.listdir(os.path.join(fd, ch))):
                if not (fn.startswith('leetcode') and fn.endswith('.py')):
                    continue
                s = open(os.path.join(fd, ch, fn), encoding='utf-8').read()
                for m in re.finditer(r'^# =+ (\d+)\. (.+?) \((Easy|Medium|Hard)\)\n# (https://leetcode.com/problems/[^/\s]+/?)\n(?:# Pattern: (.*)\n)?', s, re.M):
                    rows.setdefault(int(m.group(1)), []).append({'t': m.group(2), 'd': m.group(3), 'u': m.group(4), 'p': m.group(5) or '',
                                                                 'f': f'{subj}/files/{ch}/{fn}'})
    return rows


SUBJECT_NAME = {'python': 'Python', 'machine-learning': 'Machine Learning', 'deep-learning': 'Deep Learning'}
BAD = [('—', 'em dash'), ('–', 'en dash'), (';', 'semicolon')]


def prose_errors(where, text):
    t = re.sub(r'<code>.*?</code>|<pre>.*?</pre>|&[a-z]+;|&#\d+;', '', text, flags=re.S)
    return [f'{where}: {name} in prose' for ch, name in BAD if ch in t]


class Topic:
    def __init__(self):
        self.codes = {}
        self.practice = []
        self.idx = lc_index()

    def code(self, key, py, js, java, ts):
        self.codes[key] = {'py': py, 'js': js, 'java': java, 'ts': ts}

    def leet(self, num, lv, code, statement, example, hint, approach, time, space, title=None, url=None, diff=None):
        known = self.idx.get(num, [])
        k0 = known[0] if known else {}
        title = title or k0.get('t')
        url = url or k0.get('u') or ''
        diff = diff or k0.get('d', '')
        if not title or not url:
            raise SystemExit(f'LeetCode {num}: give title= and url= because it is not solved anywhere on the site yet')
        also = ''
        if known:
            links = ', '.join(f'<a href="../{html.escape(k["f"])}" download>{SUBJECT_NAME.get(k["f"].split("/")[0], k["f"].split("/")[0])} chapter file</a>' for k in known)
            also = f'<p class="lc-also">📁 Also solved in Python on this site: {links}.</p>'
        st = (f'<p class="lc-link"><a href="{html.escape(url)}" target="_blank" rel="noopener">LeetCode {num}. {html.escape(title)}</a>'
              f'{f" <span class=lc-d>{diff}</span>" if diff else ""}</p>{statement}{also}')
        self.practice.append({'id': f'lc{num}', 'lv': lv, 'title': f'{num}. {title}', 'code': code, 'statement': st, 'example': example,
                              'hint': hint, 'approach': approach, 'time': time, 'space': space, 'num': num})

    def finish(self, T):
        errs = []
        for p in T['parts']:
            errs += prose_errors('part ' + p['id'], p['html'] + p['title'])
        for p in self.practice:
            for f in ('statement', 'hint', 'approach'):
                errs += prose_errors(f'practice {p["id"]} {f}', p[f])
        for i, q in enumerate(T['quiz']):
            errs += prose_errors(f'quiz {i}', q['q'] + ' '.join(q['o']) + q.get('hint', '') + q.get('why', ''))
        for i, q in enumerate(T['calc']):
            errs += prose_errors(f'calc {i}', q['q'] + q.get('hint', '') + ' '.join(q['steps']))
        for s in T['say']:
            errs += prose_errors('say ' + s['id'], s['en'])
        for r in T['real']:
            errs += prose_errors('real', ' '.join(r))
        errs += prose_errors('lead', T['lead'])
        for k, txt in T.get('talk', {}).items():
            errs += prose_errors('talk ' + k, txt)
            n = len(txt.split())
            if n < 110:
                errs.append(f'talk {k}: only {n} words, write 120 to 180')
        if errs:
            raise SystemExit('style problems:\n  ' + '\n  '.join(errs))
        T.update({'codes': self.codes, 'practice': self.practice, 'langs': ['py', 'js', 'java', 'ts'], 'voice': ['en'], 'play': True})
        return T
