"""Build the Natural Language Processing chapter pages in content/nlp/ from the topic files.

The subject has two sections, each with its own learning path (see 'parts' of the subject in data/catalog.js):
  NLU   topics/       the first part of the course: language, text as data, information theory, n-gram language
                      models, smoothing, tagging and syntax (19 chapters)
  NLP   nlp-topics/   the neural part of the course (FoVL lectures 1 to 3, the class notebooks and transcripts):
                      neurons and gradient descent, word vectors, neural language models and RNNs, LSTM and GRU,
                      sequence to sequence models, attention and decoding

The pages use the same layout, checks and tabs as the Computer Vision subject, so this file only changes the
settings in tools/cv-build/build.py and runs it once per section. Topic files use the same kit
(tools/cv-build/cvkit.py). The animations live in assets/nlpwidgets.js (NLU) and assets/nnwidgets.js (NLP) on top of
the framework in assets/cvviz.js. One cheatsheet covers both sections.

Usage:  python3 tools/nlp-build/build.py [--part nlu|nlp] [slug ...]      (no slug builds every chapter)
The Interview Questions page is built by:  python3 tools/interview-build/build.py --run nlp
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'cv-build'))
import build as B  # noqa: E402

sys.path.append(HERE)  # after the import above, so that 'build' still means the Computer Vision builder

BASE = {
    'subject': 'nlp', 'name': 'Natural Language Processing', 'builder': 'tools/nlp-build/build.py', 'badge': 'NLP',
    'widgets': ['cvviz.js', 'nlpstem.js', 'nlpwidgets.js'], 'css': ['cv.css', 'nlp.css'], 'body': 'cvp nlpp',
    # one compact sheet covers both sections (NLU and NLP), so it may use 6 pages per section
    'compact_max': 12,
}
PARTS = [
    {'part': 'nlu', 'part_name': 'NLU', 'topics': os.path.join(HERE, 'topics'), 'func': 'nlpModules', 'marker': 'nlp-build'},
    {'part': 'nlp', 'part_name': 'NLP', 'topics': os.path.join(HERE, 'nlp-topics'), 'func': 'nlpNeuralModules', 'marker': 'nlp-neural-build',
     'widgets': ['cvviz.js', 'nlpwidgets.js', 'nnwidgets.js']},
]


def main():
    args = sys.argv[1:]
    only = None
    if args[:1] == ['--part']:
        only, args = args[1], args[2:]
    every = []
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
        every += chs
    cfg = dict(BASE)
    import cheatsheet
    cheatsheet.write(every, cfg, B.ROOT)


if __name__ == '__main__':
    main()
