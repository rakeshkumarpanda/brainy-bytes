"""Build three subjects from one set of tools: Machine Learning, Deep Learning and MLOps.

Machine Learning (content/machine-learning/) has four sections. Each one is a tab on the learning path (see 'parts'
of the subject in data/catalog.js), and each section is split into steps, so the path reads Section, then Step,
then Chapter:
  Foundations       found-topics/   what machine learning is, the project workflow, the Python tools (NumPy, pandas,
                                    scikit-learn), the maths you need, and cleaning and preparing data
  Supervised        sup-topics/     regression, classification, trees and ensembles, and how to evaluate and tune
  Unsupervised      unsup-topics/   clustering, dimensionality reduction, anomalies, association rules, recommenders
  Reinforcement     rl-topics/      agents and rewards, bandits, Markov decision processes, Q learning, deep RL
Deep Learning (content/deep-learning/, dl-topics/): neurons, backpropagation, training, CNNs, RNNs, transformers and
  generative models, in steps without section tabs.
MLOps (content/mlops/, mlops-topics/): setting up a machine on macOS, Windows, Linux and ChromeOS, pipelines,
  serving models with Flask, FastAPI and Django, Docker and CI/CD, tracking, monitoring, explainability and fairness,
  ML system design and the revision.

The pages use the same layout, checks and tabs as the Complete Python and Artificial Intelligence subjects, so this
file only changes the settings in tools/cv-build/build.py and runs it once per section. Topic files use the kits in
tools/cv-build/cvkit.py, tools/ai-build/coreaikit.py and tools/python-build/pykit.py (download links, LeetCode tables).
The animations live in assets/mlwidgets*.js on top of assets/cvviz.js. Every animation starts empty and adds one step
each time Step is pressed, with a plain English line for that step. assets/voiceteach.js (added to every chapter page by tools/cv-build)
reads those lines aloud when the
reader turns the voice on, and adds a "Listen to this lesson" button to every lesson.

Downloads (written by tools/python-build/pyfiles.py into content/<subject>/files/<slug>/):
  <example>.py   every program of the chapter, the same code the Learn tab runs
  practice.py    every assignment with its starter code and tests
  solutions.py   the model solutions with the same tests
  leetcode.py    the solutions to the LeetCode problems listed in the chapter (never shown on the page)
The build runs solutions.py and leetcode.py and stops if any test fails. LeetCode numbers must be unique across all
three subjects.

Every example runs with the Python that runs this script. Use Python 3.14 with the same library versions the
browser (Pyodide 314.0.7) has, so the outputs on the page match what a reader sees:
  uv venv .venv --python 3.14 && VIRTUAL_ENV=.venv uv pip install -r tools/ml-build/requirements.txt
  .venv/bin/python tools/ml-build/build.py [--part foundations|supervised|unsupervised|reinforcement|deep|mlops] [--fast] [slug ...]
--fast skips the cheatsheet PDFs. The Interview Questions page:  python3 tools/interview-build/build.py --run machine-learning
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(TOOLS, 'cv-build'))
import build as B  # noqa: E402

sys.path.append(os.path.join(TOOLS, 'ai-build'))
sys.path.append(os.path.join(TOOLS, 'python-build'))
sys.path.append(HERE)  # after the import above, so that 'build' still means the Computer Vision builder

WIDGETS = ['cvviz.js', 'aiwidgets.js', 'mlwidgets.js', 'mlwidgets2.js', 'mlwidgets3.js', 'mlwidgets4.js', 'mlwidgets5.js']
COMMON = {'builder': 'tools/ml-build/build.py', 'css': ['cv.css', 'ai.css', 'python.css', 'ml.css'],
          'body': 'cvp aip caip pyp mlp', 'widgets': WIDGETS}
SUBJECTS = [
    {'base': dict(COMMON, subject='machine-learning', badge='ML', name='Machine Learning'), 'compact_max': 18, 'parts': [
        {'part': 'foundations', 'part_name': 'Foundations', 'topics': os.path.join(HERE, 'found-topics'), 'func': 'mlFoundModules', 'marker': 'ml-found-build'},
        {'part': 'supervised', 'part_name': 'Supervised Learning', 'topics': os.path.join(HERE, 'sup-topics'), 'func': 'mlSupModules', 'marker': 'ml-sup-build'},
        {'part': 'unsupervised', 'part_name': 'Unsupervised Learning', 'topics': os.path.join(HERE, 'unsup-topics'), 'func': 'mlUnsupModules', 'marker': 'ml-unsup-build'},
        {'part': 'reinforcement', 'part_name': 'Reinforcement Learning', 'topics': os.path.join(HERE, 'rl-topics'), 'func': 'mlRlModules', 'marker': 'ml-rl-build'}]},
    {'base': dict(COMMON, subject='deep-learning', badge='DL', name='Deep Learning'), 'compact_max': 8, 'parts': [
        {'key': 'deep', 'topics': os.path.join(HERE, 'dl-topics'), 'func': 'dlModules', 'marker': 'dl-build'}]},
    {'base': dict(COMMON, subject='mlops', badge='MLOps', name='MLOps'), 'compact_max': 8, 'parts': [
        {'key': 'mlops', 'topics': os.path.join(HERE, 'mlops-topics'), 'func': 'mlopsModules', 'marker': 'mlops-build'}]},
]


def make_header(name):
    def header(T, what):
        return (f'# {T["badge"]} {T["title"]}\n# {what}\n'
                f'# From the Brainy Bytes {name} subject. Run it with: python3 <this file>\n'
                f'# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn\n')
    return header


def main():
    args = sys.argv[1:]
    only, fast = None, False
    if '--fast' in args:
        fast = True
        args.remove('--fast')
    if args[:1] == ['--part']:
        only, args = args[1], args[2:]
    import pyfiles
    seen, sheets = {}, []
    for S in SUBJECTS:
        every = []
        pyfiles.header = make_header(S['base']['name'])
        for P in S['parts']:
            B.CFG.clear()
            B.CFG.update(S['base'])
            B.CFG.update({k: v for k, v in P.items() if k != 'key'})
            if not [f for f in os.listdir(P['topics']) if f.endswith('.py')]:
                continue
            key = P.get('part', P.get('key'))
            if (only and key != only) or (args and not any(a in ' '.join(os.listdir(P['topics'])) for a in args)):
                # still load the chapters so that the cheatsheet and the LeetCode check cover every section
                chs = B.chapters()
                for T in chs:
                    T['part'], T['part_name'] = P.get('part'), P.get('part_name')
            else:
                chs = B.build(args)
                pyfiles.write_all([T for T in chs if not args or T['slug'] in args], os.path.join(B.ROOT, 'content', S['base']['subject'], 'files'))
            every += chs
        for T in every:
            for item in T.get('leet') or []:
                if item['num'] in seen:
                    raise SystemExit(f'LeetCode {item["num"]} is in both {seen[item["num"]]} and {T["slug"]}: pick another problem')
                seen[item['num']] = T['slug']
        if every:
            sheets.append((every, dict(S['base'], compact_max=S['compact_max'])))
    if fast:
        return
    import cheatsheet
    for every, cfg in sheets:
        cheatsheet.write(every, cfg, B.ROOT)


if __name__ == '__main__':
    main()
