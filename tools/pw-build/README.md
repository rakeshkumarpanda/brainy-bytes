# Playwright chapter builder

This folder builds the Playwright subject: the chapter pages in `content/playwright/`, the Playwright block in `data/catalog.js`, and a static copy of Brainy Shop in `content/playwright/shop/` for the in page playground.

Every example on a chapter page is a small real project in Java, Python, JavaScript or TypeScript. The builder runs each one against Brainy Shop (`app/server.mjs`) and puts the real terminal output under the code. Nothing in a terminal box is typed by hand.

## Folders

| Path | What it holds |
| --- | --- |
| `build.py` | The builder. `python3 build.py` builds every chapter, `python3 build.py pw-ci pw-reports` builds the chapters you name. |
| `pkit.py` | Helpers the topic files use: `four`, `one`, `ts`, `js`, `py`, `jv`, `shown`, `table`, `tip`, `figure`, `walk`. |
| `topics/NN-slug.py` | One chapter each. A topic file defines the dict `T` with parts, examples, quiz, number crunch and labs. |
| `app/` | Brainy Shop, the practice site every example tests. Changing it resets the whole run cache. |
| `frameworks/{ts,js,python,java}` | The four company style frameworks from the framework chapter. `make_js.mjs` writes `js` from `ts`. |
| `screens/` | Scripts that take real screenshots: folder trees, codegen, the Inspector, the trace viewer and the reports. |
| `labgen.mjs` | Translates lab answers into each language for the playground. |
| `box/` | The tools the examples run with. Ignored by Git, see the set up below. |
| `.cache/` | Saved results of earlier runs. Ignored by Git. |

## One time set up

You need Node.js 22 or later, Python 3.10 or later, JDK 21 with Maven, and Chromium for Playwright 1.63. The builder looks for browsers in `PLAYWRIGHT_BROWSERS_PATH`, which is `/opt/pw-browsers` when it is not set.

```bash
cd tools/pw-build/box
npm ci                                   # JavaScript and TypeScript tools from package-lock.json
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
npx playwright install chromium          # skip when /opt/pw-browsers already has it
```

Maven runs with `-o` (offline) so builds do not depend on the network. Fill the local Maven repository once by running the framework project online:

```bash
cd tools/pw-build/frameworks/java && mvn -B test-compile
```

If a later build stops with an artifact missing in offline mode, run `mvn -B test-compile` once without `-o` in that example's folder under `box/runs/`.

The CI chapter runs examples inside the official Playwright Docker images, so it needs a running Docker daemon. Behind a proxy, the topic passes the proxy settings and CA file into the container (see `PROXY` in `topics/17-pw-ci.py`).

The screenshot scripts for codegen and the Inspector need a real window, so they run under Xvfb and need ImageMagick and python-xlib.

## How a build works

1. `copy_shop()` copies Brainy Shop into `content/playwright/shop/`, with `fakeapi.js` answering its API calls in the browser.
2. For each chapter, every example is written to its own folder under `box/runs/` and run against the copy of Brainy Shop the builder starts on a free port. TypeScript runs `tsc` first and the build stops on a type error.
3. A run is cached in `.cache/` by its files, its command, the shop's hash and `RUN_STAMP`. An example only runs again when one of those changes. Bump `RUN_STAMP` in `build.py` to rerun everything.
4. An example's `after` hook runs only when the example really ran, not when it came from the cache. The reporting chapter uses these hooks to screenshot the report a run just wrote.
5. The page is written to `content/playwright/<slug>.html` and the catalog block in `data/catalog.js` is replaced.

To rerun a single cached example, delete its cache file. The key is the first 24 characters of the SHA-256 of `json.dumps([files, cmd, app_hash, RUN_STAMP], sort_keys=True)`.

## Checks before a commit

- Every example's output reads as expected, with no stack traces from the builder itself.
- The labs pass in every language in the in page playground.
- The page has no sideways scroll at 1280 and 390 pixels wide.
- The house style holds: no em dashes or semicolons in prose, and plain sentences.

## Gotchas

- Strings that a topic passes to `table()` or `tip()` inside an f-string use single braces.
- `pkit` keeps files whose names start with `pom`, `playwright`, `pytest`, `conftest`, `package`, `tsconfig`, `testng`, `.env` or `requirements` at the project root. Other files go under `tests/` or `src/`.
- Report tools that load files from a CDN (Extent) get local copies through `screens/report_shot.py`, since the build machine may have no direct internet access.
- TestNG calls `onTestFailure` before `@AfterMethod`, so a listener can still screenshot the page.
- `-Dtest` overrides the Surefire suite files, so listeners declared in `testng.xml` do not load with it.
- Do not use `pkill -f` with a pattern that matches your own shell.

## Cheatsheets

A full build also writes one full and one compact cheatsheet per language, each with a PDF, through tools/sheet-build/langsheet.py. Each sheet shows only that language's code. To rebuild only the cheatsheets, run `python3 tools/sheet-build/langsheet.py playwright` (needs node with playwright for the PDFs).
