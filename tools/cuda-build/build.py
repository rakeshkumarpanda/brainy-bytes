"""Build the GPU Programming chapter pages in content/cuda/ from the topic files in topics/.

The pages use the same layout, checks and tabs as the Computer Vision and NLP subjects, so this file only changes the
settings in tools/cv-build/build.py and runs it. Topic files use the same kit (tools/cv-build/cvkit.py) plus
cudakit.py (CUDA listings with line notes, terminal blocks, notebook download cards). The animations live in
assets/cudawidgets.js on top of the framework in assets/cvviz.js.

Source: Rakesh's GPU Programming notes for lectures 1 to 12 (IIT Jodhpur, PG Diploma in AI), the formula workbook,
Quiz 1 and its worked solutions. Chapters marked "beyond the lectures" add what a student still needs (unified
memory, grid stride loops, warp shuffles, scan, histograms, events, Python on the GPU), checked against the CUDA
C++ Programming Guide.

Checks on top of the CV builder:
  - every CUDA listing written with cu(..., check=True) is compiled when BB_CUDA_PATH points to a CUDA tree
    (see check_cuda.py). Device code goes through clang and ptxas for sm_80, host code is checked for syntax.
  - notebooks.py writes content/cuda/notebooks/*.ipynb and stops if a code line has no explanation.

Usage:  python3 tools/cuda-build/build.py [--fast] [slug ...]     (--fast skips notebooks and cheatsheet PDFs)
The Interview Questions page is built by:  python3 tools/interview-build/build.py cuda
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'cv-build'))
import build as B  # noqa: E402

sys.path.append(HERE)  # after the import above, so that 'build' still means the Computer Vision builder

B.CFG.update({
    'subject': 'cuda', 'name': 'GPU Programming', 'topics': os.path.join(HERE, 'topics'),
    'func': 'cudaModules', 'marker': 'cuda-build', 'builder': 'tools/cuda-build/build.py', 'badge': 'GPU',
    'widgets': ['cvviz.js', 'cudalist.js', 'cudawidgets.js'], 'css': ['cv.css', 'cuda.css'], 'body': 'cvp cudap',
    'compact_max': 8,
})

if __name__ == '__main__':
    fast = '--fast' in sys.argv
    chs = B.build([a for a in sys.argv[1:] if a != '--fast'])
    import check_cuda
    import cudakit
    import notebooks
    check_cuda.run(cudakit.LISTINGS + notebooks.cu_files())
    if fast:
        sys.exit(0)
    notebooks.write_all(B.out_dir())
    import cheatsheet
    cheatsheet.write(chs, B.CFG, B.ROOT)
