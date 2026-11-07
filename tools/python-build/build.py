"""Build the Complete Python chapter pages in content/python/ from the topic files.

The subject has three sections, each with its own learning path (see 'parts' of the subject in data/catalog.js):
  Core Python      core-topics/   from your first program to classes and inheritance. Follows the Python Institute
                                  PCEP-30-02 and PCAP-31-03 syllabi, plus what a student still needs (match, f-strings,
                                  exception groups, pathlib, json, venv and pip)
  Advanced Python  adv-topics/    the PCPP-32-101 syllabus (advanced OOP, PEPs, GUI, network, files and sqlite3) plus
                                  iterators, generators, context managers, testing, complexity, collections, regular
                                  expressions and concurrency. The older chapter "How Python runs" (tools/py-build)
                                  sits in this section as its step 7
  Web and APIs     web-topics/    HTTP and REST, sockets, the requests library, API data, Flask, Django, Django REST
                                  framework, FastAPI and API security

The pages use the same layout, checks and tabs as the Artificial Intelligence subject, so this file only changes the
settings in tools/cv-build/build.py and runs it once per section. Topic files use the same kit
(tools/cv-build/cvkit.py and tools/ai-build/coreaikit.py) plus pykit.py (download links, listings that need your
own computer, LeetCode tables). The animations live in assets/pywidgets.js, assets/pywidgets2.js and
assets/pywidgets3.js on top of assets/cvviz.js. Every animation starts empty and adds one step each time Step is
pressed, with a plain English line for that step.

Downloads (written by pyfiles.py into content/python/files/<slug>/):
  <example>.py   every program of the chapter, the same code the Learn tab runs
  practice.py    every assignment with its starter code and tests, to solve on your own computer
  solutions.py   the model solutions with the same tests
  leetcode.py    the solutions to the LeetCode problems listed in the chapter (never shown on the page)
The build runs solutions.py and leetcode.py and stops if any test fails.

Every example runs with the Python that runs this script, so use Python 3.14 with Flask, Django, Django REST
framework, requests, FastAPI, httpx and pytest installed:
  uv venv .venv --python 3.14 && VIRTUAL_ENV=.venv uv pip install -r tools/python-build/requirements.txt
  .venv/bin/python tools/python-build/build.py [--part core|advanced|web] [--fast] [slug ...]
--fast skips the cheatsheet PDFs. The Interview Questions page:  python3 tools/interview-build/build.py --run python
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'cv-build'))
import build as B  # noqa: E402

sys.path.append(os.path.join(os.path.dirname(HERE), 'ai-build'))
sys.path.append(HERE)  # after the import above, so that 'build' still means the Computer Vision builder

WIDGETS = ['cvviz.js', 'aiwidgets.js', 'pywidgets.js', 'pywidgets2.js', 'pywidgets3.js']
BASE = {
    'subject': 'python', 'builder': 'tools/python-build/build.py', 'badge': 'PY', 'css': ['cv.css', 'ai.css', 'python.css'],
    'body': 'cvp aip caip pyp', 'widgets': WIDGETS, 'name': 'Python',
}
PARTS = [
    {'part': 'core', 'part_name': 'Core Python', 'topics': os.path.join(HERE, 'core-topics'), 'func': 'pyCoreModules', 'marker': 'python-core-build'},
    {'part': 'advanced', 'part_name': 'Advanced Python', 'topics': os.path.join(HERE, 'adv-topics'), 'func': 'pyAdvModules', 'marker': 'python-adv-build'},
    {'part': 'web', 'part_name': 'Web and APIs', 'topics': os.path.join(HERE, 'web-topics'), 'func': 'pyWebModules', 'marker': 'python-web-build'},
]
# one compact sheet covers all three sections
SHEET = dict(BASE, compact_max=16)


def main():
    args = sys.argv[1:]
    only, fast = None, False
    if '--fast' in args:
        fast = True
        args.remove('--fast')
    if args[:1] == ['--part']:
        only, args = args[1], args[2:]
    every = []
    import pyfiles
    for P in PARTS:
        B.CFG.clear()
        B.CFG.update(BASE)
        B.CFG.update(P)
        if not os.listdir(P['topics']):
            continue
        if only and P['part'] != only:
            # still load the chapters so that the shared cheatsheet covers every section
            chs = B.chapters()
            for T in chs:
                T['part'], T['part_name'] = P['part'], P['part_name']
        else:
            chs = B.build(args)
            pyfiles.write_all([T for T in chs if not args or T['slug'] in args], os.path.join(B.ROOT, 'content', 'python', 'files'))
        every += chs
    if fast:
        return
    import cheatsheet
    cheatsheet.write(every, SHEET, B.ROOT)


if __name__ == '__main__':
    main()
