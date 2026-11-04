"""Write the GPU Programming notebooks to content/cuda/notebooks/*.ipynb.

Each notebook lives in tools/cuda-build/nbsrc/nNN_*.py as a dict NB = {file, title, intro, cells}. A cell is either
    md(text)                         a text cell (Markdown)
    code(src, {line: why, ...})      a code cell, followed by a text cell that explains every line
The writer stops the build when a non blank code line has no explanation, so every line in every notebook says what
it does and why. Comment lines (starting with #) explain themselves and need no note.

The Python cells were run with Numba 0.68 in its CUDA simulator (NUMBA_ENABLE_CUDASIM=1, see run_sim below), and the
CUDA C files written by %%writefile cells are compiled by check_cuda.py with the chapter listings.
Usage on its own:  python3 tools/cuda-build/notebooks.py [--sim]   (--sim runs every notebook in the simulator)
"""
import glob
import html
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def md(text):
    return {'t': 'md', 'src': text.strip('\n')}


def code(src, notes=None):
    return {'t': 'code', 'src': src.strip('\n'), 'notes': notes or {}}


def _needs_note(line, c_like=False):
    s = line.strip()
    return bool(s) and not s.startswith('//' if c_like else '#')


def _check(nb):
    for c in nb['cells']:
        if c['t'] != 'code':
            continue
        rows = c['src'].split('\n')
        cl = rows[0].startswith('%%writefile') and rows[0].endswith(('.cu', '.cuh', '.cpp', '.h'))
        for n in c['notes']:
            if not 1 <= n <= len(rows):
                raise SystemExit(f"{nb['file']}: note for line {n}, but the cell has {len(rows)} lines:\n{c['src']}")
            if not _needs_note(rows[n - 1], cl):
                raise SystemExit(f"{nb['file']}: note for line {n}, which is blank or a comment: {rows[n - 1]!r}")
        for i, l in enumerate(rows, 1):
            if _needs_note(l, cl) and i not in c['notes']:
                raise SystemExit(f"{nb['file']}: line {i} has no explanation: {l!r}")


def _explain(c):
    rows = c['src'].split('\n')
    out = ['Line by line, what this cell does and why:', '', '| Line | Code | What and why |', '|---|---|---|']
    for n in sorted(c['notes']):
        src = html.escape(rows[n - 1].strip()).replace('|', '&#124;')
        out.append(f'| {n} | <code>{src}</code> | {c["notes"][n].replace("|", "&#124;")} |')
    return '\n'.join(out)


def _lines(text):
    parts = text.split('\n')
    return [p + '\n' for p in parts[:-1]] + [parts[-1]]


def to_ipynb(nb):
    cells = [{'cell_type': 'markdown', 'metadata': {}, 'source': _lines(f"# {nb['title']}\n\n{nb['intro'].strip()}")}]
    for c in nb['cells']:
        if c['t'] == 'md':
            cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': _lines(c['src'])})
        else:
            cells.append({'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [], 'source': _lines(c['src'])})
            if c['notes']:
                cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': _lines(_explain(c))})
    for k, c in enumerate(cells):
        c['id'] = f'cell-{k:02d}'
    return {'cells': cells, 'nbformat': 4, 'nbformat_minor': 5,
            'metadata': {'accelerator': 'GPU', 'colab': {'provenance': [], 'gpuType': 'T4'},
                         'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                         'language_info': {'name': 'python'}}}


def load():
    out = []
    for p in sorted(glob.glob(os.path.join(HERE, 'nbsrc', 'n[0-9]*.py'))):
        m = importlib.import_module('nbsrc.' + os.path.basename(p)[:-3])
        _check(m.NB)
        out.append(m.NB)
    return out


def cu_files():
    """(path, src, True) for every %%writefile *.cu cell, so check_cuda.py compiles them."""
    res = []
    for nb in load():
        for c in nb['cells']:
            if c['t'] == 'code' and c['src'].startswith('%%writefile ') and c['src'].split('\n')[0].endswith('.cu'):
                name = c['src'].split('\n')[0].split()[1]
                res.append((f"{nb['file']}:{name}", c['src'].split('\n', 1)[1] + '\n', True))
    return res


def write_all(out_dir):
    d = os.path.join(out_dir, 'notebooks')
    os.makedirs(d, exist_ok=True)
    nbs = load()
    for nb in nbs:
        with open(os.path.join(d, nb['file']), 'w') as f:
            json.dump(to_ipynb(nb), f, indent=1, ensure_ascii=False)
            f.write('\n')
    print(f'notebooks: {len(nbs)} written to {os.path.relpath(d)}')
    return nbs


def run_sim(nb, python=sys.executable):
    """Run the Python cells of one notebook in the Numba CUDA simulator. Shell and %% cells are skipped."""
    import subprocess
    import tempfile
    src = []
    for c in nb['cells']:
        if c['t'] != 'code' or c['src'].startswith('%%') or c['src'].startswith('!'):
            continue
        src.append('\n'.join(l for l in c['src'].split('\n') if not l.lstrip().startswith(('!', '%'))))
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, 'nb.py')
        open(p, 'w').write('\n\n'.join(src) + '\n')
        env = dict(os.environ, NUMBA_ENABLE_CUDASIM='1', MPLBACKEND='Agg')
        r = subprocess.run([python, p], cwd=tmp, env=env, capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout, r.stderr


if __name__ == '__main__':
    nbs = load()
    print(len(nbs), 'notebooks pass the line check')
    if '--sim' in sys.argv:
        py = os.environ.get('BB_NUMBA_PY', sys.executable)
        for nb in nbs:
            if '--only' in sys.argv and nb['file'] not in sys.argv:
                continue
            rc, out, err = run_sim(nb, py)
            print(f"--- {nb['file']}: exit {rc}")
            print(out[-3000:])
            if rc:
                print(err[-3000:])
