"""Build the Selenium chapter pages in content/selenium/ from the topic files in topics/.

The pages use the same layout, checks and tabs as the Computer Vision and NLP subjects, so this file only changes the
settings in tools/cv-build/build.py and runs it. Topic files use the same kit (tools/cv-build/cvkit.py) plus sekit.py,
whose tri() writes one example in Java, Python and JavaScript with a note for every line. Every such example runs
for real against Chrome when it is first built (runner.py) and the output is saved in runs.json.

Usage:  python3 tools/se-build/build.py [slug ...]          (no slug builds every chapter)
        SE_RUN=1 python3 tools/se-build/build.py [slug ...]  (also runs examples that have no saved output yet)
The Interview Questions page is built by:  python3 tools/interview-build/build.py selenium
One time set up for running examples: tools/se-build/setup.sh (see README.md)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'cv-build'))
import build as B  # noqa: E402

sys.path.append(HERE)  # after the import above, so that 'build' still means the Computer Vision builder
import runner  # noqa: E402

B.CFG.update({
    'subject': 'selenium', 'name': 'Selenium', 'topics': os.path.join(HERE, 'topics'),
    'func': 'seModules', 'marker': 'se-build', 'builder': 'tools/se-build/build.py', 'badge': 'SE',
    'widgets': ['cvviz.js', 'setri.js', 'seplay.js', 'sewidgets.js'], 'css': ['cv.css', 'se.css'], 'body': 'cvp sep',
    'min_calc': 6, 'langsheet': True,
})


def prune():
    """After a full build, drop saved runs that no example uses any more."""
    used = runner.USED
    c = runner.cache()
    stale = [k for k in c if k not in used]
    for k in stale:
        del c[k]
    if stale:
        runner.save()
        print(f'runs.json: removed {len(stale)} saved runs no example uses')


if __name__ == '__main__':
    try:
        B.main()
        if not sys.argv[1:]:
            prune()
    finally:
        runner.stop_services()
