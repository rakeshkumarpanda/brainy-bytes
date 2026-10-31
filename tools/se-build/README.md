# Selenium chapter builder

This folder builds the Selenium learning path: the chapter pages in `content/selenium/` and the `seModules()` part of
`data/catalog.js`. The pages share the layout, tabs and checks of the Computer Vision and NLP subjects, so
`build.py` only changes the settings of `tools/cv-build/build.py` and runs it.

## Files

| Path | What it is |
| --- | --- |
| `build.py` | Entry point. Sets the Selenium settings and runs the shared builder. |
| `topics/NN-slug.py` | One file per chapter: lessons, examples, worked problems, quiz, assignments and summary. |
| `sekit.py` | `tri()` for one example in Java, Python and JavaScript with a note per line, plus `solo`, `src`, `shell` and `flow`. |
| `runner.py` | Runs each example for real against Chrome, and saves the output in `runs.json`. |
| `runs.json` | Saved outputs, so pages rebuild without a browser. |
| `site/` | Local copies of the Selenium test pages from `https://www.selenium.dev/selenium/web/`. |
| `siteserver.py` | Serves `site/` and the CDN files on port 8443, so examples keep the real URLs. |
| `setup.sh` | One time set up of the run tools in `box/`, which Git ignores. |

The widgets used by `viz('se-...')` live in `assets/sewidgets.js`. The example tabs and the line by line walk live in
`assets/setri.js`, and the playground in `assets/seplay.js`.

## Build

```sh
python3 tools/se-build/build.py                 # every chapter, from saved outputs, then drop unused saved runs
python3 tools/se-build/build.py grid revision   # only these chapters
SE_RUN=1 python3 tools/se-build/build.py grid   # also run examples that have no saved output yet
python3 tools/interview-build/build.py selenium # the Interview Questions page
```

The build stops with a clear message when a page breaks the house style (no em dashes, en dashes or semicolons in
prose, notes on every code line), when a chapter has too few quiz questions or worked problems, when a worked
problem has no check value, or when an example output does not contain its `expect` text.

## Running examples

`setup.sh` needs Python 3.10 or later, Node.js 22 or later, JDK 21 with Maven, Chromium, Xvfb and openssl. It
installs Selenium 4.51.0 for each language, Mocha, pytest, JUnit 5, the Grid server and a matching ChromeDriver,
and writes a Chrome wrapper that sends `selenium.dev` and the CDN hosts to the local server.

With `SE_RUN=1`, `runner.py` starts Xvfb and the site server when needed, and a Grid standalone server on
`http://localhost:4444` for examples marked `needs='grid'`. A run that fails is saved too. To run an example again,
delete its entries from `runs.json` (keep `indent=1, sort_keys=True` when you write the file back).

## Writing a chapter

1. Copy the shape of an existing topic file. Each example is
   `tri(key, title, java, py, js, mode=..., needs=..., extra=..., fail=..., expect=...)` and every code line ends
   with `  ## note` that explains what the line achieves.
2. Use facts from the selenium.dev documentation, and let the real run decide what the prose says about output.
3. Build with `SE_RUN=1`, read the outputs in `runs.json`, and fix any sentence that does not match.
4. Check the page at 1280 and 390 pixels wide.

## Cheatsheets

A full build also writes one full and one compact cheatsheet per language, each with a PDF, through tools/sheet-build/langsheet.py. Each sheet shows only that language's code. To rebuild only the cheatsheets, run `python3 tools/sheet-build/langsheet.py selenium` (needs node with playwright for the PDFs).
