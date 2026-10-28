"""Build the Natural Language Processing chapter pages in content/nlp/ from the topic files in topics/.

The pages use the same layout, checks and tabs as the Computer Vision subject, so this file only changes the
settings in tools/cv-build/build.py and runs it. Topic files use the same kit (tools/cv-build/cvkit.py), and the
animations live in assets/nlpwidgets.js on top of the framework in assets/cvviz.js.

Usage:  python3 tools/nlp-build/build.py [slug ...]      (no slug builds every chapter)
The Interview Questions page is built by:  python3 tools/interview-build/build.py --run nlp
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'cv-build'))
import build as B  # noqa: E402

sys.path.append(HERE)  # after the import above, so that 'build' still means the Computer Vision builder

B.CFG.update({
    'subject': 'nlp', 'name': 'Natural Language Processing', 'topics': os.path.join(HERE, 'topics'),
    'func': 'nlpModules', 'marker': 'nlp-build', 'builder': 'tools/nlp-build/build.py', 'badge': 'NLP',
    'widgets': ['cvviz.js', 'nlpstem.js', 'nlpwidgets.js'], 'css': ['cv.css', 'nlp.css'], 'body': 'cvp nlpp',
})

if __name__ == '__main__':
    B.main()
