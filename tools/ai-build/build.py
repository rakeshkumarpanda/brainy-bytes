"""Build the Artificial Intelligence chapter pages in content/ai/ from the topic files.

The subject has two sections, each with its own learning path (see 'parts' of the subject in data/catalog.js):
  Core AI      core-topics/   search (uninformed, informed, memory bounded, AND-OR, local and evolutionary),
                              constraint satisfaction, adversarial search, propositional and first order logic,
                              planning, Bayesian networks and causality, and reinforcement learning (34 chapters)
  Advanced AI  topics/        decision theory and game theory from the Advanced AI lectures 1 to 6 and Quiz 1

The pages use the same layout, checks and tabs as the Computer Vision subject, so this file only changes the
settings in tools/cv-build/build.py and runs it once per section. Topic files use the same kit
(tools/cv-build/cvkit.py), and the Core AI files also use coreaikit.py (what, why and how boxes, comparison
tables and the notebook download card). The animations live in assets/aiwidgets.js and assets/aigames.js
(Advanced AI) and assets/coreai.js and assets/coreai2.js (Core AI), on top of the framework in assets/cvviz.js.
One cheatsheet covers both sections.

Sources for Core AI: the course slides Set 1 to Set 4 (introduction, uninformed, informed and local search,
adversarial search, constraint satisfaction) and the class transcripts of January and February 2026. The other
syllabus parts (knowledge and reasoning, planning, Bayesian networks and causality, reinforcement learning)
follow Russell and Norvig, Artificial Intelligence: A Modern Approach (4th edition), Sutton and Barto,
Reinforcement Learning: An Introduction (2nd edition), and Pearl, Causality, as each chapter says.

Every Core AI chapter also gets a practice notebook, content/ai/notebooks/<slug>.ipynb, written by notebooks.py
from the chapter's examples and assignments. The build runs every notebook from top to bottom and stops if a cell
fails or a model solution does not pass its tests.

Usage:  python3 tools/ai-build/build.py [--part core|advanced] [--fast] [slug ...]   (no slug builds every chapter)
        --fast skips the notebooks and the cheatsheet PDFs
The Interview Questions page is built by:  python3 tools/interview-build/build.py --run ai
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'cv-build'))
import build as B  # noqa: E402

sys.path.append(HERE)  # after the import above, so that 'build' still means the Computer Vision builder

BASE = {
    'subject': 'ai', 'builder': 'tools/ai-build/build.py', 'badge': 'AI', 'css': ['cv.css', 'ai.css'], 'body': 'cvp aip',
}
PARTS = [
    {'part': 'core', 'part_name': 'Core AI', 'name': 'Artificial Intelligence', 'topics': os.path.join(HERE, 'core-topics'),
     'func': 'coreAiModules', 'marker': 'ai-core-build',
     'widgets': ['cvviz.js', 'aiwidgets.js', 'coreai.js', 'coreai2.js'], 'body': 'cvp aip caip'},
    {'part': 'advanced', 'part_name': 'Advanced AI', 'name': 'Advanced AI', 'topics': os.path.join(HERE, 'topics'),
     'func': 'advAiModules', 'marker': 'ai-build', 'widgets': ['cvviz.js', 'aiwidgets.js', 'aigames.js']},
]
# one compact sheet covers both sections, so it may use more pages than a one section subject
SHEET = dict(BASE, name='Artificial Intelligence', compact_max=14)


def main():
    args = sys.argv[1:]
    only, fast = None, False
    if '--fast' in args:
        fast = True
        args.remove('--fast')
    if args[:1] == ['--part']:
        only, args = args[1], args[2:]
    every, core = [], []
    for P in PARTS:
        B.CFG.clear()
        B.CFG.update(BASE)
        B.CFG.update(P)
        if only and P['part'] != only:
            # still load the chapters so that the shared cheatsheet covers both sections
            chs = B.chapters()
            for T in chs:
                T['part'], T['part_name'] = P['part'], P['part_name']
        else:
            chs = B.build(args)
        if P['part'] == 'core':
            core = chs
        every += chs
    if fast:
        return
    import notebooks
    notebooks.write_all(core, os.path.join(B.ROOT, 'content', 'ai', 'notebooks'))
    import cheatsheet
    cheatsheet.write(every, SHEET, B.ROOT)


if __name__ == '__main__':
    main()
