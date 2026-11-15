"""Build the Complete Cybersecurity subject (content/cyber-security/) from the topic files in this folder.

The subject has six sections. Each one is a tab on the learning path (see 'parts' of the subject in
data/catalog.js), and each section is split into steps, so the path reads Section, then Step, then Chapter:
  Foundations           found-topics/    what security is, risk, the maths for security, operating systems,
                                         networks and Python for security work
  Cryptography          crypto-topics/   classical ciphers, AES, hashing and passwords, number theory, RSA,
                                         Diffie-Hellman and ElGamal, elliptic curves, PKI and TLS, post quantum
                                         crypto, secret sharing and zero knowledge
  Network and Systems   sys-topics/      network attacks, firewalls and IDS, wireless, authentication, access
                                         control, malware, hardening and vulnerability scores
  Application Security  app-topics/      the web and OWASP Top 10, injection, XSS and CSRF, memory safety,
                                         ethical hacking, social engineering
  Security Operations   ops-topics/      logging and SIEM, incident response, forensics, threat intelligence,
                                         cloud security, governance and law
  Advanced              adv-topics/      machine learning for security, attacks on ML, federated learning and its
                                         privacy and attacks, differential privacy, certification revision

The pages use the same layout, checks and tabs as the Machine Learning subject, so this file only changes the
settings in tools/cv-build/build.py and runs it once per section. Topic files use the kits in tools/cv-build/cvkit.py,
tools/ai-build/coreaikit.py, tools/python-build/pykit.py and cykit.py in this folder (the background voice talk).
The animations live in assets/cywidgets*.js on top of assets/cvviz.js and the MLZ.trace framework of
assets/mlwidgets.js. Every animation starts empty and adds one step each time Step is pressed, with a plain English
line for that step. assets/voiceteach.js reads those lines aloud when the reader turns the voice on, and reads each
lesson, starting with its background talk, when the reader presses "Listen to this lesson".

Every attack in this subject is shown on toy data inside the page or on the reader's own computer. Nothing here
scans, connects to or attacks a real system.

Downloads (written by tools/python-build/pyfiles.py into content/cyber-security/files/<slug>/):
  <example>.py   every program of the chapter, the same code the Learn tab runs
  practice.py    every assignment with its starter code and tests
  solutions.py   the model solutions with the same tests (the build runs it and stops if a test fails)

Use Python 3.14 with the same library versions the browser (Pyodide 314.0.7) has, so the outputs on the page match
what a reader sees:
  uv venv .venv --python 3.14 && VIRTUAL_ENV=.venv uv pip install -r tools/cyber-build/requirements.txt
  .venv/bin/python tools/cyber-build/build.py [--part foundations|crypto|systems|appsec|secops|advanced] [--fast] [slug ...]
--fast skips the cheatsheet PDFs. The search index:  node tools/search-build/build.js cyber-security
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(TOOLS, 'cv-build'))
import build as B  # noqa: E402

sys.path.append(os.path.join(TOOLS, 'ai-build'))
sys.path.append(os.path.join(TOOLS, 'python-build'))
sys.path.append(os.path.join(TOOLS, 'ml-build'))
sys.path.append(HERE)  # after the import above, so that 'build' still means the Computer Vision builder

WIDGETS = ['cvviz.js', 'aiwidgets.js', 'mlwidgets.js', 'cywidgets.js', 'cywidgets2.js', 'cywidgets3.js']
BASE = {'builder': 'tools/cyber-build/build.py', 'css': ['cv.css', 'ai.css', 'python.css', 'ml.css', 'cyber.css'],
        'body': 'cvp aip caip pyp mlp cyp', 'widgets': WIDGETS, 'subject': 'cyber-security', 'badge': 'CY',
        'name': 'Cybersecurity'}
PARTS = [
    {'part': 'foundations', 'part_name': 'Foundations', 'topics': 'found-topics', 'func': 'cyFoundModules'},
    {'part': 'crypto', 'part_name': 'Cryptography', 'topics': 'crypto-topics', 'func': 'cyCryptoModules'},
    {'part': 'systems', 'part_name': 'Network and Systems Security', 'topics': 'sys-topics', 'func': 'cySysModules'},
    {'part': 'appsec', 'part_name': 'Application Security', 'topics': 'app-topics', 'func': 'cyAppModules'},
    {'part': 'secops', 'part_name': 'Security Operations', 'topics': 'ops-topics', 'func': 'cyOpsModules'},
    {'part': 'advanced', 'part_name': 'Advanced: AI, Federated Learning and Privacy', 'topics': 'adv-topics', 'func': 'cyAdvModules'},
]
COMPACT_MAX = 14


def header(T, what):
    return (f'# {T["badge"]} {T["title"]}\n# {what}\n'
            '# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>\n'
            '# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.\n')


def drop_placeholder(fn):
    """data/catalog.js holds an empty cyXModules() for every section that has no chapters yet, so the subject entry
    works from the start. Once a section gets its first chapter the builder writes the real function, and the empty
    one is removed here so that the name is declared only once."""
    if not fn:
        return
    path = os.path.join(B.ROOT, 'data', 'catalog.js')
    text = open(path, encoding='utf-8').read()
    stub = ('\n/* placeholder until the first chapter of this section is built by tools/cyber-build/build.py */\n'
            f'function {fn}() {{ return []; }}\n')
    if stub in text:
        open(path, 'w', encoding='utf-8').write(text.replace(stub, ''))


def main():
    args = sys.argv[1:]
    only, fast = None, False
    if '--fast' in args:
        fast = True
        args.remove('--fast')
    if args[:1] == ['--part']:
        only, args = args[1], args[2:]
    import pyfiles
    pyfiles.header = header
    every = []
    for P in PARTS:
        folder = os.path.join(HERE, P['topics'])
        if not os.path.isdir(folder) or not [f for f in os.listdir(folder) if f.endswith('.py')]:
            continue
        B.CFG.clear()
        B.CFG.update(BASE)
        B.CFG.update(P, topics=folder, marker='cy-' + P['part'] + '-build')
        if (only and P['part'] != only) or (args and not any(a in ' '.join(os.listdir(folder)) for a in args)):
            # still load the chapters so that the cheatsheet covers every section
            chs = B.chapters()
            for T in chs:
                T['part'], T['part_name'] = P['part'], P['part_name']
        else:
            drop_placeholder(P['func'])
            chs = B.build(args)
            pyfiles.write_all([T for T in chs if not args or T['slug'] in args], os.path.join(B.ROOT, 'content', BASE['subject'], 'files'))
        every += chs
    if fast or not every:
        return
    import cheatsheet
    cheatsheet.write(every, dict(BASE, compact_max=COMPACT_MAX), B.ROOT)


if __name__ == '__main__':
    main()
