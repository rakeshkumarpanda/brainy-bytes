"""Writes data/talk/<subject>/<page>.js files from a plain text source.

    python3 tools/voice/write.py <subject> talks.txt

talks.txt holds one page after another:

    == branches
    what: The talk for the lesson with id "what", on one line.
    switch: ...

A page that already has a talk file keeps its other talks, and the ones given here replace theirs.
Typographic dashes and semicolons are turned into plain sentences' commas and full stops.
"""
import sys, os, json, re

sub, src = sys.argv[1], sys.argv[2]
pages, cur = {}, None
for line in open(src, encoding='utf-8'):
    line = line.strip()
    if not line: continue
    if line.startswith('== '):
        cur = line[3:].strip(); pages.setdefault(cur, {}); continue
    k, _, t = line.partition(': ')
    t = t.replace(' — ', ', ').replace('—', ', ').replace(' – ', ', ').replace('; ', '. ')
    pages[cur][k.strip()] = t.strip()
os.makedirs(f'data/talk/{sub}', exist_ok=True)
for page, m in pages.items():
    p = f'data/talk/{sub}/{page}.js'
    old = {}
    if os.path.exists(p):
        s = open(p, encoding='utf-8').read(); old = json.loads(s[s.index('{'): s.rindex('}') + 1])
    old.update(m)
    body = json.dumps(old, ensure_ascii=False, indent=1)
    open(p, 'w', encoding='utf-8').write(f"/* Background voice talks for content/{sub}/{page}.html, read by assets/voiceteach.js (see data/talk/README.md) */\nVT_TALK({json.dumps(sub + '/' + page)}, {body});\n")
    print(p, len(m), 'talks,', sum(len(x.split()) for x in m.values()), 'words')
