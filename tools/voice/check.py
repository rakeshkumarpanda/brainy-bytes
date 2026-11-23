"""Reports, per subject, how many lessons have a background talk, lists lessons without one,
and talk ids that match no lesson.  python3 tools/voice/check.py [subject ...] [--missing]"""
import re, sys, glob, os, json
sys.path.insert(0, os.path.dirname(__file__))
from digest import lessons

def talk_ids(path):
    if not os.path.exists(path): return {}
    s = open(path, encoding='utf-8').read()
    body = s[s.index('{'): s.rindex('}') + 1]
    return json.loads(body)

args = sys.argv[1:]
show = '--missing' in args
subs = [a for a in args if not a.startswith('--')] or sorted(os.listdir('content'))
grand = [0, 0]
for sub in subs:
    if sub in ('_template', 'cyber-security'): continue
    have = tot = 0
    for f in sorted(glob.glob(f'content/{sub}/*.html')):
        s = open(f, encoding='utf-8').read()
        if 'voiceteach.js' not in s: continue
        ids = [l for l, _ in lessons(s)]
        if not ids: continue
        page = os.path.basename(f)[:-5]
        t = talk_ids(f'data/talk/{sub}/{page}.js')
        miss = [i for i in ids if i not in t]
        extra = [i for i in t if i not in ids]
        have += len(ids) - len(miss); tot += len(ids)
        if extra: print(f'  {sub}/{page}: talk ids with no lesson: {extra}')
        if show and miss: print(f'  {sub}/{page}: {len(miss)} missing')
    grand[0] += have; grand[1] += tot
    if tot: print(f'{sub}: {have} of {tot} lessons have a talk')
print(f'all: {grand[0]} of {grand[1]}')
