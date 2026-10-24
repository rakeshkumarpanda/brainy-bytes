# Python subject builder

This folder builds the Python chapters in `content/python/` and the `pyModules()` block in `data/catalog.js`.

Each chapter is a Python file in `topics/`. It lists its parts, code examples, animations, quiz, number practice, exercises and narration with the helpers in `kit.py`.

The build runs every example with CPython 3.14 and stores the real output in the page. Plain examples also get a line by line recording made by `pytrace.py`, which powers the "Line by line" viewer. Examples that need several files or a terminal (`__pycache__`, pytest, `-X importtime`) run as small projects with a shell command. Every exercise model answer must pass its tests and every starter must fail at least one.

In the browser, `assets/pyplay.js` runs edited examples, exercises and live line by line recordings with Pyodide (CPython 3.14 compiled to WebAssembly), loaded from jsDelivr on the first click. `assets/pyviz.js` holds the "Watch CPython run your code" animation, a small model of the CPython 3.14 tokenizer, parser, compiler and evaluation loop.

## Requirements

- CPython 3.14 (`uv python install 3.14` works), set `PY_BUILD_PYTHON` if `python3.14` is not on PATH
- Python 3.10 or later to run the build script itself
- The test tools: `uv venv box/.venv --python 3.14` then `VIRTUAL_ENV=box/.venv uv pip install -r box/requirements.txt`
- Node.js, only for `check_pyvm.py`

## Build

```
python3 tools/py-build/build.py                  # every chapter
python3 tools/py-build/build.py py-how-python-runs
```

Results are cached in `.cache`, so only changed examples run again. The build stops if an example gives an unexpected result, an exercise fails its check, or the page text contains an em dash or a semicolon.

## Check the animation against CPython

```
python3.14 tools/py-build/check_pyvm.py 2500 [seed]
```

It generates random programs and compares tokens, `ast.dump`, every bytecode instruction and the printed output of the animation's model with the real CPython.
