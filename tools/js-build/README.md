# JavaScript subject builder

This folder builds the 17 JavaScript chapters in `content/javascript/` and the `jsModules()` block in `data/catalog.js`.

Each chapter is a Python file in `topics/`. It lists its parts, code examples, quiz, number practice, exercises and narration with the helpers in `kit.py`.

The build runs every example with Node.js and stores the real output in the page. Unit, API and browser test examples run as small projects inside `box/`, which holds the pinned test tools (Jest, Vitest, Mocha, Playwright, Selenium WebDriver and others).

## Requirements

- Node.js 26 or later
- Python 3.10 or later
- `npm ci` inside `box/`
- Chromium for the Playwright and Selenium examples

## Build

Build every chapter:

```
cd tools/js-build
python3 build.py
```

Build one chapter by its slug:

```
python3 build.py js-expert
```

Results are cached in `.cache`, so only changed examples run again. The build stops if an example gives an unexpected result, an exercise model answer fails its tests, or the page text contains an em dash or a semicolon.
