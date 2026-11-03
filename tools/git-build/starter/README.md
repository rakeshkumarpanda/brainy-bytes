# calc-app

A tiny calculator used by the Brainy Bytes Git and CI/CD course.

- `app/` is the code, `tests/unit` are the developer's unit tests, `tests/smoke` are the QA smoke tests.
- `.github/workflows/ci.yml` and `.github/workflows/qa-regression.yml` run it on GitHub Actions.
- `.gitlab-ci.yml` runs it on GitLab CI/CD.

Run it on your own computer:

    python -m venv .venv
    . .venv/bin/activate        # on Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python -m pytest -q tests/unit
