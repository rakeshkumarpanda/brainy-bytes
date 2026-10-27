# Manual Testing page builder

This folder builds the newer Manual Testing chapters and the extra sections added to the older ones.

## Files

- `kit.py` holds helpers for sections, tables, tips, diagrams, narration, quiz and number crunch items.
- `pages/*.py` each describe one new chapter. The page is built from the shell of `testing-fundamentals.html`.
- `adds/*.py` each add sections, quiz items, number crunch items and diagrams to an existing chapter. The added parts sit between the `<!-- mt2 parts -->` and `<!-- mt2 toc -->` markers, so a rebuild replaces them instead of adding them twice.
- `widgets.js` and `widgets.css` hold the interactive labs. They are copied into every page between mt2 markers.
- `check.js` opens every page in Chromium at 1280 and 390 pixels wide and reports console errors, sideways scrolling and diagram boxes or labels that overlap.

## Build

```
python3 tools/mt-build/build.py
node tools/mt-build/check.js            # add --shots <dir> to save screenshots
python3 tools/interview-build/build.py manual-testing
```

The build also updates `data/catalog.js`: new chapters, new sections and the "Modern testing practice" module. Running it twice gives the same output.

The build stops with an error when prose contains an em dash or a semicolon, when a number crunch answer does not match its formula, when a quiz answer index is wrong, or when a diagram arrow points to a missing box.

Manual Testing pages must not contain programming code, except the White Box Testing chapter.
