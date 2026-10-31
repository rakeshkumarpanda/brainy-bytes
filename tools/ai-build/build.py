"""Build the Advanced AI chapter pages in content/ai/ from the topic files in topics/.

The Artificial Intelligence subject has two sections, Core AI and Advanced AI (see 'parts' of the subject in
data/catalog.js). This builder writes the Advanced AI chapters. It uses the same layout, checks and tabs as the
Computer Vision subject, so it only changes the settings in tools/cv-build/build.py and runs it. Topic files use
the same kit (tools/cv-build/cvkit.py). The animations live in assets/aiwidgets.js on top of assets/cvviz.js.

Source: the Advanced AI lecture notes 1 to 6 (decision theory and game theory) and Quiz 1.

Usage:  python3 tools/ai-build/build.py [slug ...]      (no slug builds every chapter)
The Interview Questions page is built by:  python3 tools/interview-build/build.py --run ai
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'cv-build'))
import build as B  # noqa: E402

sys.path.append(HERE)

B.CFG.update({
    'subject': 'ai', 'name': 'Advanced AI', 'topics': os.path.join(HERE, 'topics'),
    'func': 'advAiModules', 'marker': 'ai-build', 'builder': 'tools/ai-build/build.py', 'badge': 'AI',
    'widgets': ['cvviz.js', 'aiwidgets.js', 'aigames.js'], 'css': ['cv.css', 'ai.css'], 'body': 'cvp aip',
    'part': 'advanced', 'part_name': 'Advanced AI',
})

if __name__ == '__main__':
    B.main()
