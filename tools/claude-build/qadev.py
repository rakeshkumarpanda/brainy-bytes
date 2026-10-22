"""Skill and rule files for a QA engineer's day and a developer's day.

The rules chapter (06), the skills chapter (07) and the screenshot captures in shots/ all use these,
so the text on the page and the text in the screenshots is the same file.
The example project is a small Python shop app: FastAPI, pytest, Playwright for Python and Alembic.
"""

# ---------- rules a QA engineer keeps in .claude/rules/qa/ ----------
QA_RULES = {
    '.claude/rules/qa/test-design.md': '''
---
paths:
  - "tests/**/*.py"
  - "testcases/**/*.md"
---

# How we design tests
- Every test case has an ID like TC-CART-001, a title, steps, test data and one expected result.
- Cover three kinds for each rule: a positive case, a negative case and the boundary values.
- For a limit like "1 to 10 items", test 0, 1, 2, 9, 10 and 11.
- One behaviour per test. If the title needs the word "and", split it.
- Test names read like sentences: test_free_delivery_starts_at_499.
''',
    '.claude/rules/qa/api-tests.md': '''
---
paths:
  - "tests/api/**/*.py"
---

# API test rules
- Use the `api` fixture from tests/api/conftest.py. Never build URLs or tokens by hand.
- Check the status code, then the JSON shape, then the values. In that order.
- Every error test checks the body has the shape {"error": {"code", "message"}}.
- No real payment gateway calls. Use the sandbox base URL from the API_BASE_URL variable.
- Mark slow tests with @pytest.mark.slow so the PR pipeline can skip them.
''',
    '.claude/rules/qa/ui-tests.md': '''
---
paths:
  - "tests/ui/**/*.py"
---

# UI test rules (Playwright for Python)
- Find elements the way a user would: page.get_by_role, get_by_label, get_by_text.
- Use CSS selectors only when nothing else works, and never XPath.
- Never use time.sleep. Use expect(...) which waits by itself.
- Page actions live in page objects in tests/ui/pages/. Tests only call those.
- Each test logs in through the `logged_in_page` fixture, not through the login form.
''',
    '.claude/rules/qa/bug-reports.md': '''
---
paths:
  - "bugs/**/*.md"
---

# Bug report rules
- Title: what is broken, where, and when. "Coupon SAVE10 not applied on cart above Rs 2,000".
- Steps start from a clean state and are numbered. Anyone must be able to repeat them.
- Write Expected and Actual as two separate lines.
- Severity is about impact (Critical, Major, Minor). Priority is about urgency (P1 to P3).
- Never guess the cause. Put guesses under "Notes" and say they are guesses.
''',
}

# ---------- rules a developer keeps in .claude/rules/dev/ ----------
DEV_RULES = {
    '.claude/rules/dev/python.md': '''
# Python rules for this repo
- Python 3.12. Type hints on every function. `ruff check` and `mypy` must pass.
- Raise our own errors from app/errors.py, never a bare Exception.
- Log with `logger = logging.getLogger(__name__)`. Never print().
- New code needs a test in the matching file under tests/.
''',
    '.claude/rules/dev/db-migrations.md': '''
---
paths:
  - "migrations/**/*.py"
  - "app/models/**/*.py"
---

# Database changes
- Every model change gets a new Alembic migration: `alembic revision --autogenerate -m "..."`.
- Never edit a migration that is already on main. Write a new one.
- Every upgrade() has a working downgrade().
- Adding a NOT NULL column to a big table: add it nullable, backfill, then add the constraint.
''',
    '.claude/rules/dev/pull-requests.md': '''
# Pull requests
- One change per PR. Under 400 changed lines where possible.
- The description says what changed, why, and how it was tested.
- Link the issue with "Fixes #123".
- Run `pytest -q` and `ruff check .` before saying a change is done.
''',
}

# ---------- skills for a QA engineer ----------
TEST_CASES_SKILL = '''
---
name: test-cases
description: Writes manual test cases from a user story or acceptance criteria. Use when the user pastes a story, a ticket or acceptance criteria and asks for test cases, test scenarios or a test plan.
argument-hint: "[story id]"
---

# Write test cases for $ARGUMENTS

1. Read the story. List every rule it states, one line each.
2. For each rule write test cases in this table:
   | ID | Title | Steps | Test data | Expected result | Type |
   Type is Positive, Negative or Boundary.
3. For every number limit, add boundary cases just below, on and just above each edge.
4. Add cases for empty input, wrong format and a user without permission.
5. End with "Questions for the product owner": anything the story does not say.

Follow the ID format and naming in .claude/rules/qa/test-design.md.
Save the table to testcases/$ARGUMENTS.md.
'''

BUG_REPORT_SKILL = '''
---
name: bug-report
description: Turns rough notes, a screenshot description or a failing test log into a clear bug report. Use when the user says they found a bug, pastes an error or asks to log or write up a defect.
---

# Write a bug report

Fill this template from what the user gave you. Do not invent steps or data.
If something is missing, write "Not given" and ask for it at the end.

## Title
## Environment   (build, browser or device, test data used)
## Steps to reproduce
## Expected result
## Actual result
## Severity and priority
## Evidence   (log lines, screenshot names, test name)
## Notes

Save it as bugs/<short-title>.md and show me the file.
'''

PICK_TESTS_SKILL = '''
---
name: pick-regression
description: Picks which tests to run for the current changes. Use when the user asks what to test, which regression tests to run, or whether a branch is safe to merge.
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/map_tests.py *)
---

## Files changed on this branch

!`git diff --name-only origin/main...HEAD`

## Steps

1. Run `python ${CLAUDE_SKILL_DIR}/scripts/map_tests.py` with the changed files above.
2. Show the list of tests it picked and the reason for each.
3. Give the exact pytest command to run them.
4. If a changed file has no tests, say so clearly. That is a gap to fix.
'''

MAP_TESTS = r'''
"""Pick the tests to run for a list of changed files.

For app/<area>/<name>.py it picks tests/**/test_<name>.py and any test that imports that module.
Smoke tests in tests/smoke/ always run. Usage: python map_tests.py <changed file> ...
"""
import sys
from pathlib import Path

ROOT = Path.cwd()
tests = sorted(p for p in (ROOT / "tests").rglob("test_*.py"))
picked = {}
no_tests = []

for changed in sys.argv[1:]:
    path = Path(changed)
    if path.suffix != ".py" or not changed.startswith("app/"):
        continue
    module = ".".join(path.with_suffix("").parts)          # app/cart/pricing.py -> app.cart.pricing
    found = False
    for t in tests:
        rel = str(t.relative_to(ROOT))
        if t.name == f"test_{path.stem}.py":
            picked.setdefault(rel, f"named after {changed}")
            found = True
        elif f"from {module} import" in t.read_text() or f"import {module}" in t.read_text():
            picked.setdefault(rel, f"imports {module}")
            found = True
    if not found:
        no_tests.append(changed)

for t in tests:
    rel = str(t.relative_to(ROOT))
    if rel.startswith("tests/smoke/"):
        picked.setdefault(rel, "smoke test, always runs")

for rel, why in sorted(picked.items()):
    print(f"{rel:<34} {why}")
print()
print("Run:", "pytest -q " + " ".join(sorted(picked)))
for f in no_tests:
    print("NO TESTS FOUND for", f)
'''

SHOP_FILES = {
    'tests/test_pricing.py': 'from app.cart.pricing import total\n\ndef test_total_adds_items():\n    assert total([100, 250]) == 350\n',
    'tests/api/test_checkout_api.py': 'from app.cart.pricing import total\n\ndef test_checkout_uses_cart_total(api):\n    ...\n',
    'tests/ui/test_login.py': 'def test_login_shows_name(logged_in_page):\n    ...\n',
    'tests/smoke/test_health.py': 'def test_health(api):\n    ...\n',
    'tests/test_coupons.py': 'from app.cart.coupons import apply\n\ndef test_save10():\n    ...\n',
}

# ---------- skills for a developer ----------
FIX_ISSUE_SKILL = '''
---
name: fix-issue
description: Fixes a GitHub issue end to end. Use when the user gives an issue number and asks to fix, solve or work on it.
argument-hint: "[issue number]"
disable-model-invocation: true
---

# Fix issue #$ARGUMENTS

1. Run `gh issue view $ARGUMENTS` and read the issue and its comments.
2. Find the code involved. Say in two lines what you think the cause is.
3. Write a failing test that shows the bug. Run it and show it fails.
4. Fix the code. Run the test again and show it passes.
5. Run `pytest -q` and `ruff check .`
6. Write a commit message that ends with "Fixes #$ARGUMENTS".
'''

PR_REVIEW_SKILL = '''
---
name: pr-review
description: Reviews the changes on the current branch before a pull request. Use when the user asks for a review, a self review, or whether the branch is ready for a PR.
context: fork
agent: Explore
---

## The diff to review

!`git diff origin/main...HEAD`

## Review it like a senior teammate

For each point give the file, the line and one sentence. Group them as:
1. Bugs: wrong logic, missing error handling, off by one, None not handled.
2. Tests: changed behaviour with no test, tests that only check the happy path.
3. Safety: secrets, SQL built from strings, user input not validated.
4. Readability: unclear names, functions over 40 lines.

Say "Nothing found" for an empty group. Do not rewrite the code.
'''

RELEASE_NOTES_SKILL = '''
---
name: release-notes
description: Writes release notes from git history between two tags. Use when the user asks for release notes, a changelog or what went into a release.
argument-hint: "[from-tag] [to-tag]"
arguments: [from, to]
---

# Release notes from $from to $to

1. Run `git log --oneline --no-merges $from..$to` and read every commit.
2. Group the commits under New, Fixed and Changed. One plain English line each.
3. Leave out commits that only touch tests or CI.
4. Put any breaking change at the top in bold.
'''
