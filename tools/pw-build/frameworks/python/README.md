# Brainy Shop tests

End to end tests for Brainy Shop, written with pytest and pytest-playwright.

## Run them

    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python -m playwright install chromium
    cp .env.example .env        # then fill in the passwords
    pytest                      # every test
    pytest -m smoke             # only the tests marked smoke
    pytest -n 2                 # two workers at once

## Folders

- framework/config.py: settings that change between machines
- framework/data: test users and products
- framework/api: API helpers for fast set up
- framework/components: parts that appear on many pages
- framework/pages: one page object per screen
- conftest.py: fixtures that hand page objects and a signed in session to tests
- tests: test files, one folder per feature
