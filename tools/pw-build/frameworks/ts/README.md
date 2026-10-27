# Brainy Shop tests

End to end tests for Brainy Shop, written with Playwright Test in TypeScript.

## Run them

    npm ci
    npx playwright install chromium
    cp .env.example .env        # then fill in the passwords
    npx playwright test         # every test
    npm run test:smoke          # only the tests tagged @smoke
    npm run report              # open the last HTML report

## Folders

- src/config: settings that change between machines
- src/data: test users and products
- src/api: API helpers for fast set up
- src/components: parts that appear on many pages
- src/pages: one page object per screen
- src/fixtures: hands page objects and a signed in session to tests
- tests: test files, one folder per feature
