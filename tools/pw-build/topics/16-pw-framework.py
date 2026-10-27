import os

from pkit import part, say, quiz, calc, panel, four, js, ts, py, jv, table, tip, figure

MODULE = ('🏗️', 'Framework design', 'pw-framework', 'Page objects and components, a real framework built step by step in each language, CI pipelines and reports that teams read every day.')

FW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frameworks')
LANGS = {'ts': 'TypeScript', 'js': 'JavaScript', 'python': 'Python', 'java': 'Java'}
NOT_RUN = ('README.md', '.gitignore', '.env.example', 'requirements.txt')


def read_tree(lang):
    """Every file of one framework project, read from tools/pw-build/frameworks/<lang>."""
    base = os.path.join(FW, lang)
    out = {}
    for d, dirs, files in os.walk(base):
        dirs[:] = sorted(x for x in dirs if x not in ('__pycache__', 'node_modules'))
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(d, f), base).replace(os.sep, '/')
            out[rel] = open(os.path.join(d, f), encoding='utf-8').read().rstrip('\n')
    return out


TREE = {lang: read_tree(lang) for lang in LANGS}


def run_files(lang):
    """The files a run needs: the framework without the CI file, the README and the examples of local settings."""
    return {k: v for k, v in TREE[lang].items() if not k.startswith('.github/') and k not in NOT_RUN and not k.endswith('__init__.py')}


def pick(lang, *names):
    return [n for n in names if n in TREE[lang]]


JM = 'src/main/java/com/brainy/shop/'
JT = 'src/test/java/com/brainy/shop/'


def js_show(ext, *names):
    return [n.replace('.ts', '.' + ext) for n in names]


TS_CORE = ['src/data/users.ts', 'src/data/products.ts', 'src/api/ShopApi.ts', 'src/components/Header.ts', 'src/components/ProductCard.ts',
           'src/pages/BasePage.ts', 'src/pages/LoginPage.ts', 'src/pages/ProductsPage.ts', 'src/pages/CartPage.ts', 'src/fixtures/index.ts']
TS_TESTS = ['tests/smoke/sign-in.spec.ts', 'tests/products/search.spec.ts', 'tests/cart/add-to-cart.spec.ts', 'tests/cart/checkout.spec.ts']
PY_CORE = ['framework/data/users.py', 'framework/data/products.py', 'framework/api/shop_api.py', 'framework/components/header.py',
           'framework/components/product_card.py', 'framework/pages/base_page.py', 'framework/pages/login_page.py',
           'framework/pages/products_page.py', 'framework/pages/cart_page.py', 'conftest.py']
PY_TESTS = ['tests/smoke/test_sign_in.py', 'tests/products/test_search.py', 'tests/cart/test_add_to_cart.py', 'tests/cart/test_checkout.py']
JAVA_CORE = [JM + 'data/User.java', JM + 'data/Users.java', JM + 'data/Product.java', JM + 'api/ShopApi.java', JM + 'components/Header.java',
             JM + 'components/ProductCard.java', JM + 'pages/BasePage.java', JM + 'pages/LoginPage.java', JM + 'pages/ProductsPage.java',
             JM + 'pages/CartPage.java', JT + 'base/BaseTest.java']
JAVA_TESTS = [JT + 'tests/smoke/SignInTest.java', JT + 'tests/products/SearchTest.java', JT + 'tests/cart/AddToCartTest.java', JT + 'tests/cart/CheckoutTest.java']

JAVA_NOISE = [(r'(?m)^SLF4J\(W\).*\n', '')]

CODES = {
    'config': four('Step 1: the project, its settings and its runner config',
                   java=jv(run_files('java'), kind='testng', cmd='mvn -q test-compile && find src/test -name "*Test.java" | sort',
                           show=['pom.xml', 'testng.xml', 'testng-smoke.xml', 'src/test/resources/config.properties', JM + 'config/Config.java'], replace=JAVA_NOISE),
                   py=py(run_files('python'), ini=None, cmd='pytest --collect-only -q',
                         show=['pytest.ini', 'framework/config.py']),
                   js=js(run_files('js'), config=None, cmd='npx playwright test --list', show=['package.json', 'playwright.config.js', 'src/config/env.js']),
                   ts=ts(run_files('ts'), cmd='npx playwright test --list', show=['package.json', 'playwright.config.ts', 'src/config/env.ts']),
                   result='The runner found all seven tests in the folders it was told to look in, before running any of them. That is the first thing to check in a new framework. Every setting that changes between a laptop and CI, here the shop address, comes from one place: an environment variable if it is set, otherwise a default. The Java project compiled, and its test classes sit in one package per feature.'),
    'core': four('Step 2: data, API helpers, components, page objects and fixtures',
                 java=jv(run_files('java'), kind='testng', show=JAVA_CORE, replace=JAVA_NOISE),
                 py=py(run_files('python'), ini=None, cmd='pytest -v', show=PY_CORE),
                 js=js(run_files('js'), config=None, show=js_show('js', *TS_CORE)),
                 ts=ts(run_files('ts'), show=TS_CORE),
                 result='All seven tests passed in every language. Each layer has one job. Data holds the users and products. The API helper signs in and fills a cart in a fraction of a second. Components and page objects hold every locator. The fixtures, or BaseTest in Java, give each test fresh page objects and its own session, so no two tests share a cart, even when they run at the same time.'),
    'tests': four('Step 3: tests by feature, tagged so a smaller set can run',
                  java=jv(run_files('java'), kind='testng', cmd='mvn test -Dsuite=testng-smoke.xml', show=JAVA_TESTS, replace=JAVA_NOISE),
                  py=py(run_files('python'), ini=None, cmd='pytest -m smoke -v', show=PY_TESTS),
                  js=js(run_files('js'), config=None, cmd='npx playwright test --grep @smoke', show=js_show('js', *TS_TESTS)),
                  ts=ts(run_files('ts'), cmd='npx playwright test --grep @smoke', show=TS_TESTS),
                  result='Only the three smoke tests ran: the two sign in checks and the checkout. Tests live in one folder per feature and contain no locators at all, only steps and checks. Playwright Test filters by tag with --grep, pytest by marker with -m, and TestNG by group in its own suite file. In TestNG the set up methods need alwaysRun = true, or they are skipped when a group is chosen.'),
}


def tree_spec(lang, title, intro, why):
    files = TREE[lang]
    dirs = sorted({'/'.join(p.split('/')[:i]) + '/' for p in files for i in range(1, p.count('/') + 1)})
    entries = [{'p': 'shop-tests/', 'why': f'the {title} framework, as it sits in a company repository'}]
    for d in dirs:
        entries.append({'p': 'shop-tests/' + d, 'why': why.get(d.rstrip('/'), '')})
    for p, body in files.items():
        if p.endswith('__init__.py'):
            continue
        entries.append({'p': 'shop-tests/' + p, 'why': why.get(p, ''), 'body': body})
    return {'t': f'The {title} framework, file by file', 's': intro, 'files': entries}


WHY_TS = {'.github': 'GitHub settings', '.github/workflows': 'CI pipelines',
          '.github/workflows/playwright.yml': 'Runs every test on each push and pull request, with passwords from GitHub secrets, and keeps the HTML report.',
          'src': 'the framework: everything that is not a test', 'src/config': 'settings that change between machines',
          'src/config/env.ts': 'The shop address from BASE_URL, with a local default. Nothing else reads environment variables directly.',
          'src/data': 'test data', 'src/data/users.ts': 'Test accounts. Passwords come from the environment in CI.',
          'src/data/products.ts': 'Product names, ids and prices, so a renamed product is changed once.',
          'src/api': 'helpers that talk to the API', 'src/api/ShopApi.ts': 'Signs in and fills carts through the API, much faster than clicking.',
          'src/components': 'parts that appear on many pages', 'src/components/Header.ts': 'The header: greeting, cart count, sign out.',
          'src/components/ProductCard.ts': 'One product card, with every locator inside the card.',
          'src/pages': 'one page object per screen', 'src/pages/BasePage.ts': 'What every page shares: its address, open() and the header.',
          'src/pages/LoginPage.ts': 'The sign in screen.', 'src/pages/ProductsPage.ts': 'The product list, search and cards.',
          'src/pages/CartPage.ts': 'The cart, its total and placing an order.',
          'src/fixtures': 'what tests receive', 'src/fixtures/index.ts': 'test.extend with the API helper, a signed in session and every page object. Tests import test from here.',
          'tests': 'only tests, one folder per feature', 'tests/smoke': 'the fastest, most important checks', 'tests/products': 'search and the product list',
          'tests/cart': 'the cart and checkout', 'tests/smoke/sign-in.spec.ts': 'Signing in, right and wrong password. Tagged @smoke.',
          'tests/products/search.spec.ts': 'Search results, no results, and an out of stock product.',
          'tests/cart/add-to-cart.spec.ts': 'Adding from the cards, then checking the cart page.',
          'tests/cart/checkout.spec.ts': 'A cart filled through the API, then an order placed in the UI.',
          '.env.example': 'The settings a new team member copies to .env. The real .env is never committed.',
          '.gitignore': 'Keeps reports, results, packages and .env out of Git.', 'package.json': 'Exact versions and short npm scripts such as test:smoke.',
          'playwright.config.ts': 'Runner settings: folders, parallel runs, retries and reporters on CI, traces and evidence.',
          'README.md': 'How to install and run, for the next person.', 'tsconfig.json': 'TypeScript settings for type checking.'}
WHY_JS = {k.replace('.ts', '.js'): v for k, v in WHY_TS.items() if k != 'tsconfig.json'}
WHY_PY = {'.github': 'GitHub settings', '.github/workflows': 'CI pipelines',
          '.github/workflows/tests.yml': 'Runs every test on two workers on each push and pull request, and keeps the results.',
          'framework': 'the framework: everything that is not a test', 'framework/config.py': 'The shop address from BASE_URL or .env, with a local default.',
          'framework/data': 'test data', 'framework/data/users.py': 'Test accounts as frozen dataclasses. Passwords come from the environment in CI.',
          'framework/data/products.py': 'Product names, ids and prices.', 'framework/api': 'helpers that talk to the API',
          'framework/api/shop_api.py': 'Signs in and fills carts through the API.', 'framework/components': 'parts that appear on many pages',
          'framework/components/header.py': 'The header: greeting, cart count, sign out.', 'framework/components/product_card.py': 'One product card.',
          'framework/pages': 'one page object per screen', 'framework/pages/base_page.py': 'What every page shares: its path, open() and the header.',
          'framework/pages/login_page.py': 'The sign in screen.', 'framework/pages/products_page.py': 'The product list, search and cards.',
          'framework/pages/cart_page.py': 'The cart, its total and placing an order.',
          'conftest.py': 'Fixtures for the whole project: base_url, the API helper, a signed in session and every page object.',
          'tests': 'only tests, one folder per feature', 'tests/smoke': 'the fastest, most important checks', 'tests/products': 'search and the product list',
          'tests/cart': 'the cart and checkout', 'tests/smoke/test_sign_in.py': 'Signing in. pytestmark marks the whole file smoke.',
          'tests/products/test_search.py': 'Search results, no results, and an out of stock product.',
          'tests/cart/test_add_to_cart.py': 'Adding from the cards, then checking the cart page.',
          'tests/cart/test_checkout.py': 'A cart filled through the API, then an order placed in the UI.',
          '.env.example': 'The settings a new team member copies to .env.', '.gitignore': 'Keeps the venv, caches, results and .env out of Git.',
          'pytest.ini': 'Where tests are, the import path, default options and the registered markers.',
          'requirements.txt': 'Exact package versions, so every machine installs the same ones.', 'README.md': 'How to install and run.'}
WHY_JAVA = {'.github': 'GitHub settings', '.github/workflows': 'CI pipelines',
            '.github/workflows/tests.yml': 'Compiles, installs Chromium through the Playwright CLI, runs the suite and keeps the reports and traces.',
            'src': 'Maven sources', 'src/main': 'code that is not a test', 'src/main/java': '', 'src/main/java/com': '', 'src/main/java/com/brainy': '',
            'src/main/java/com/brainy/shop': 'the framework, packaged by layer', JM + 'config': 'settings that change between machines',
            JM + 'config/Config.java': 'Reads a -D option, then an environment variable, then config.properties.',
            JM + 'data': 'test data', JM + 'data/User.java': 'A record for a test account.', JM + 'data/Users.java': 'The test accounts. Passwords come from the environment in CI.',
            JM + 'data/Product.java': 'An enum of products with ids and prices.', JM + 'api': 'helpers that talk to the API',
            JM + 'api/ShopApi.java': 'Signs in and fills carts through the API.', JM + 'components': 'parts that appear on many pages',
            JM + 'components/Header.java': 'The header.', JM + 'components/ProductCard.java': 'One product card.',
            JM + 'pages': 'one page object per screen', JM + 'pages/BasePage.java': 'What every page shares.', JM + 'pages/LoginPage.java': 'The sign in screen.',
            JM + 'pages/ProductsPage.java': 'The product list, search and cards.', JM + 'pages/CartPage.java': 'The cart and placing an order.',
            'src/test': 'tests and what they need', 'src/test/java': '', 'src/test/java/com': '', 'src/test/java/com/brainy': '', 'src/test/java/com/brainy/shop': '',
            JT + 'base': 'the parent class of every test', JT + 'base/BaseTest.java': 'Starts Playwright and the browser per class, a fresh context per test, and saves a trace when a test fails.',
            JT + 'tests': 'only tests, one package per feature', JT + 'tests/smoke': 'the fastest checks', JT + 'tests/products': 'search and the product list',
            JT + 'tests/cart': 'the cart and checkout', JT + 'tests/smoke/SignInTest.java': 'Signing in. The class is in the smoke group.',
            JT + 'tests/products/SearchTest.java': 'Search results, no results, and an out of stock product.',
            JT + 'tests/cart/AddToCartTest.java': 'Adding from the cards, then checking the cart page.',
            JT + 'tests/cart/CheckoutTest.java': 'A cart filled through the API, then an order placed in the UI. In the cart and smoke groups.',
            'src/test/resources': 'files on the test classpath', 'src/test/resources/config.properties': 'Default settings.',
            '.gitignore': 'Keeps target, traces and .env out of Git.', 'pom.xml': 'Playwright and TestNG versions, and which suite file Surefire runs.',
            'testng.xml': 'The full suite: every test package, two classes at a time.', 'testng-smoke.xml': 'Only the smoke group.', 'README.md': 'How to run.'}

TREES = {
    'fw-ts': tree_spec('ts', 'TypeScript', 'The real files of the framework the examples above run. Click a file to read it.', WHY_TS),
    'fw-js': tree_spec('js', 'JavaScript', 'The same framework without types. Local imports end in .js, as Node needs for ES modules.', WHY_JS),
    'fw-python': tree_spec('python', 'Python', 'The pytest framework the examples above run. Click a file to read it.', WHY_PY),
    'fw-java': tree_spec('java', 'Java', 'The Maven and TestNG framework the examples above run. Click a file to read it.', WHY_JAVA),
}

DG = {
    'stack': {'t': 'The layers of a test framework', 'w': 900, 'h': 250,
              'n': [['cfg', 20, 20, 150, 56, 'config', {'c': 5, 'sub': 'per machine', 'i': 'The address, the browser and secrets, read from the environment.'}],
                    ['data', 20, 100, 150, 56, 'data', {'c': 5, 'sub': 'users, products', 'i': 'Test data in one place, so a change is made once.'}],
                    ['api', 20, 180, 150, 56, 'API helpers', {'c': 5, 'sub': 'fast set up', 'i': 'Sign in and fill carts without clicking.'}],
                    ['ui', 230, 100, 170, 56, 'pages and components', {'c': 1, 'sub': 'every locator', 'i': 'One class per screen and per repeated part.'}],
                    ['fix', 460, 100, 150, 56, 'fixtures', {'c': 3, 'sub': 'or BaseTest', 'i': 'Hand each test fresh objects and its own session.'}],
                    ['tests', 670, 60, 150, 56, 'tests', {'c': 2, 'sub': 'by feature, tagged', 'i': 'Steps and checks only. No locators, no waits.'}],
                    ['ci', 670, 150, 150, 56, 'CI and reports', {'c': 0, 'sub': 'every push', 'i': 'Runs the suite and keeps the evidence.'}]],
              'e': [['cfg', 'ui'], ['data', 'ui'], ['api', 'fix'], ['ui', 'fix'], ['fix', 'tests'], ['tests', 'ci']],
              'st': [[['cfg', 'data', 'api'], 'At the bottom: settings, test data and API helpers.'],
                     [['ui', 'cfg>ui', 'data>ui'], 'Page objects and components hold every locator.'],
                     [['fix', 'ui>fix', 'api>fix'], 'Fixtures build them and sign in through the API for each test.'],
                     [['tests', 'fix>tests'], 'Tests only describe steps and checks.'],
                     [['ci', 'tests>ci'], 'CI runs them on every push and keeps the reports.']]},
}


def trees_fig(lang, title):
    return (f'<div class="only-{lang if lang != "python" else "py"}" style="max-width:540px">'
            + figure(f'framework-tree-{lang}.png', f'The {title} framework folders in an editor explorer, with a note next to each folder',
                     f'The {title} project in an editor. Framework code and tests live in separate folders, and every folder has one job.')
            + '</div>')


PARTS = [
    part('what', '🗺️', 'What a framework is, and the finished result', f'''
<p>A <b>test framework</b> is the code around your tests that makes hundreds of them easy to write, read and run: settings, test data, helpers, page objects and fixtures. The tests themselves become short. This chapter builds the same framework in all four languages, in the layout teams use at work, and runs it against the shop at every step.</p>
<div class="viz" data-viz="flow" data-k="stack"></div>
<p>Here is where we will end up. Pick your language at the top of the page to see its project.</p>
{trees_fig('ts', 'TypeScript')}{trees_fig('js', 'JavaScript')}{trees_fig('python', 'Python')}{trees_fig('java', 'Java')}
{table(['Folder', 'TypeScript and JavaScript', 'Python', 'Java'], [
    ['framework code', 'src/', 'framework/', 'src/main/java/.../shop'],
    ['settings', 'src/config/env.ts', 'framework/config.py', 'config/Config.java with config.properties'],
    ['page objects', 'src/pages/', 'framework/pages/', '.../shop/pages/'],
    ['fixtures', 'src/fixtures/index.ts', 'conftest.py', 'base/BaseTest.java'],
    ['tests', 'tests/&lt;feature&gt;/*.spec.ts', 'tests/&lt;feature&gt;/test_*.py', 'src/test/java/.../tests/&lt;feature&gt;/*Test.java'],
    ['runner settings', 'playwright.config.ts', 'pytest.ini', 'pom.xml and testng.xml'],
])}
''', easy=True, kw=['framework', 'folder structure', 'project layout', 'architecture', 'layers', 'hierarchy']),

    part('step1', '1️⃣', 'Step 1: project, settings and runner config', f'''
<p>Start with an empty project that can find tests and knows where the app is. Three rules matter from the first day.</p>
{table(['Rule', 'Why'], [
    ['settings come from the environment, with a local default', 'the same code runs on a laptop, in CI and against staging'],
    ['secrets never go in the repository', 'passwords live in CI secrets and in a local .env that Git ignores'],
    ['exact versions of every package', 'every machine, and every CI run, uses the same Playwright'],
])}
[[config]]
{tip('Commit a .env.example with the names of the settings and no values. A new team member copies it to .env and fills it in. The real .env is listed in .gitignore.', 'pro')}
''', kw=['config', 'environment variables', 'dotenv', '.env', 'BASE_URL', 'secrets', 'pom.xml', 'testng.xml', 'pytest.ini']),

    part('step2', '2️⃣', 'Step 2: data, API helpers, page objects and fixtures', f'''
<p>Now add the layers, from the bottom up. Each one depends only on the layers below it, so a change in one place does not ripple through the suite.</p>
{table(['Layer', 'Its one job', 'In this framework'], [
    ['data', 'test users and products', 'users, products'],
    ['API helper', 'fast set up without the browser', 'ShopApi: signIn, addToCart'],
    ['components', 'parts on many pages', 'Header, ProductCard'],
    ['page objects', 'one screen each', 'BasePage, LoginPage, ProductsPage, CartPage'],
    ['fixtures', 'hand objects and a session to each test', 'test.extend, conftest.py, BaseTest'],
])}
[[core]]
{tip('The session fixture signs in through the API and puts the token in the page before it loads. Each test gets its own session, so its cart is its own, and parallel tests cannot disturb each other. This is the isolation rule from the parallel runs chapter, built into the framework.', 'tip')}
{tip('Java has no fixtures like Playwright Test or pytest. BaseTest plays that part: TestNG runs @BeforeClass, @BeforeMethod and @AfterMethod around every test, and with parallel="classes" each class keeps its own Playwright on its own thread. Playwright objects are not safe to share between threads.', 'warn')}
''', kw=['test data', 'API helper', 'BasePage', 'fixtures', 'BaseTest', 'TestNG', 'isolation', 'session']),

    part('step3', '3️⃣', 'Step 3: tests by feature, with tags', f'''
<p>Tests go in one folder per feature, so the folder tree reads like the app. Tag the few tests that must pass on every commit as <b>smoke</b>, and run the rest less often or in parallel shards.</p>
[[tests]]
{table(['', 'Playwright Test', 'pytest', 'TestNG'], [
    ['mark a test', "{ tag: '@smoke' }", '@pytest.mark.smoke or pytestmark', '@Test(groups = "smoke")'],
    ['run only those', 'npx playwright test --grep @smoke', 'pytest -m smoke', 'a suite file with &lt;include name="smoke"/&gt;'],
    ['leave them out', '--grep-invert @slow', "pytest -m 'not slow'", '&lt;exclude name="slow"/&gt;'],
    ['register the names', 'not needed', 'markers = in pytest.ini', 'not needed'],
])}
''', kw=['tags', 'smoke', 'grep', 'markers', 'groups', 'testng.xml', 'feature folders']),

    part('files', '📂', 'Every file, explained', f'''
<p>Open each file of the finished framework and read why it is there. These are the same files the examples above ran.</p>
<div class="only-ts"><div class="viz" data-viz="pwtree" data-k="fw-ts"></div></div>
<div class="only-js"><div class="viz" data-viz="pwtree" data-k="fw-js"></div></div>
<div class="only-py"><div class="viz" data-viz="pwtree" data-k="fw-python"></div></div>
<div class="only-java"><div class="viz" data-viz="pwtree" data-k="fw-java"></div></div>
''', kw=['files', 'project tree', 'explorer']),

    part('grow', '📈', 'How the framework grows', f'''
<p>A framework starts small and grows with the product. These are the additions teams usually make next, and the chapter that covers each.</p>
{table(['When you need', 'Add', 'Covered in'], [
    ['several environments', 'one .env per environment, or CI variables per job', 'this chapter, step 1'],
    ['many signed in roles', 'a setup step that saves storage state per role', 'API testing'],
    ['a run on every pull request', 'a CI workflow with shards and a merged report', 'CI/CD'],
    ['reports for managers and testers', 'Allure, pytest-html or ExtentReports next to the built-in reports', 'Reporting labs'],
    ['visual and accessibility checks', 'toHaveScreenshot, aria snapshots and axe in their own folder', 'Visual, accessibility and time'],
    ['lots of varied test data', 'small factory functions that build users and orders with unique names', 'Parallel runs'],
    ['consistent code', 'a linter, a formatter and code review rules', 'your team'],
])}
{tip('Grow the framework when the tests ask for it. A layer nobody needs yet is code to maintain. The best frameworks are the ones where a new test takes ten lines and needs no new helper.', 'pro')}
''', kw=['scaling', 'environments', 'roles', 'factories', 'lint', 'maintenance']),
]

INFO = {'title': 'A framework that teams can live with', 'panels': [
    panel([['e', '⚙️'], ['t', 'config', {'b': 1}]], 'Settings', 'From the environment.', 'No secrets in Git.'),
    panel([['e', '🧱'], ['t', 'layers', {'b': 1}]], 'Layers', 'One job each.', 'Data, API, pages.'),
    panel([['e', '🔧'], ['t', 'fixtures', {'b': 1}]], 'Fixtures', 'Fresh session per test.', 'Safe in parallel.'),
    panel([['e', '🏷️'], ['t', 'tags', {'b': 1}]], 'Tests', 'By feature, tagged.', 'Steps and checks only.')],
    'remember': 'Framework code and tests live apart. Tests say what, the framework says how, and the environment says where.'}

REAL = [
    ['🏢', 'One layout, four teams', 'A retailer has web, mobile web, admin and API test teams. They share one framework layout, so people move between teams and find the pages, fixtures and data in the same places.'],
    ['🔐', 'A leaked password that never happened', 'A new tester pastes a staging password into a test. The framework only reads passwords from the environment, so the review spots it at once and the password goes into CI secrets instead.'],
    ['⚡', 'Twenty minutes to four', 'A suite signs in through the login page in every test. Moving the sign in to an API fixture, as in step 2, cuts each test by a few seconds and the whole run from twenty minutes to four.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter builds a complete test framework step by step in TypeScript, JavaScript, Python and Java, in the folder layout teams use at work, and runs it against the shop at every step.',
        'यह अध्याय TypeScript, JavaScript, Python और Java में कदम दर कदम एक पूरा test framework बनाता है, उसी folder layout में जो teams काम पर इस्तेमाल करती हैं, और हर कदम पर उसे shop पर चलाता है।',
        'ಈ ಅಧ್ಯಾಯ TypeScript, JavaScript, Python ಮತ್ತು Java ನಲ್ಲಿ ಹಂತ ಹಂತವಾಗಿ ಪೂರ್ಣ test framework ಕಟ್ಟುತ್ತದೆ, teams ಕೆಲಸದಲ್ಲಿ ಬಳಸುವ folder layout ನಲ್ಲಿ, ಮತ್ತು ಪ್ರತಿ ಹಂತದಲ್ಲಿ shop ಮೇಲೆ ನಡೆಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ TypeScript, JavaScript, Python ଓ Java ରେ ପାଦେ ପାଦେ ଏକ ସମ୍ପୂର୍ଣ୍ଣ test framework ତିଆରି କରେ, teams କାମରେ ବ୍ୟବହାର କରୁଥିବା folder layout ରେ, ଏବଂ ପ୍ରତି ପାଦରେ shop ଉପରେ ଚଳାଏ।',
        'يبني هذا الفصل إطار اختبار كاملًا خطوة بخطوة بلغات TypeScript وJavaScript وPython وJava، بتنظيم المجلدات الذي تستخدمه الفرق في العمل، ويشغّله على المتجر في كل خطوة.',
        'Dieses Kapitel baut Schritt für Schritt ein vollständiges Test-Framework in TypeScript, JavaScript, Python und Java, in der Ordnerstruktur, die Teams bei der Arbeit nutzen, und führt es bei jedem Schritt gegen den Shop aus.'),
    say('what', 'The layers', 'A framework has layers: settings, test data, API helpers, components and page objects, fixtures, and finally the tests. Framework code and tests live in separate folders.',
        'Framework की परतें होती हैं: settings, test data, API helpers, components और page objects, fixtures, और आख़िर में tests। Framework code और tests अलग folders में रहते हैं।',
        'Framework ಗೆ ಪದರಗಳಿವೆ: settings, test data, API helpers, components ಮತ್ತು page objects, fixtures, ಕೊನೆಯಲ್ಲಿ tests. Framework code ಮತ್ತು tests ಬೇರೆ folders ನಲ್ಲಿ ಇರುತ್ತವೆ.',
        'Framework ର ସ୍ତର ଅଛି: settings, test data, API helpers, components ଓ page objects, fixtures, ଏବଂ ଶେଷରେ tests। Framework code ଓ tests ଅଲଗା folders ରେ ରହେ।',
        'للإطار طبقات: الإعدادات، وبيانات الاختبار، ومساعدات API، والمكونات وكائنات الصفحات، والمثبتات، وأخيرًا الاختبارات. ويعيش كود الإطار والاختبارات في مجلدات منفصلة.',
        'Ein Framework hat Schichten: Einstellungen, Testdaten, API-Helfer, Komponenten und Page Objects, Fixtures und zuletzt die Tests. Framework-Code und Tests liegen in getrennten Ordnern.'),
    say('step1', 'Step 1', 'Settings such as the shop address come from the environment, with a local default. Passwords live in CI secrets and a local .env file that Git ignores. Versions are exact.',
        'Shop address जैसी settings environment से आती हैं, local default के साथ। Passwords CI secrets और Git द्वारा ignore की गई local .env file में रहते हैं। Versions पक्के होते हैं।',
        'Shop address ನಂತಹ settings environment ನಿಂದ ಬರುತ್ತವೆ, local default ಜೊತೆ. Passwords CI secrets ಮತ್ತು Git ignore ಮಾಡುವ local .env file ನಲ್ಲಿ ಇರುತ್ತವೆ. Versions ನಿಖರ.',
        'Shop address ପରି settings environment ରୁ ଆସେ, local default ସହ। Passwords CI secrets ଓ Git ignore କରୁଥିବା local .env file ରେ ରହେ। Versions ସଠିକ।',
        'تأتي الإعدادات مثل عنوان المتجر من البيئة مع قيمة محلية افتراضية. وتعيش كلمات المرور في أسرار CI وفي ملف ‎.env محلي يتجاهله Git. والإصدارات محددة بدقة.',
        'Einstellungen wie die Shop-Adresse kommen aus der Umgebung, mit einem lokalen Standardwert. Passwörter liegen in CI-Secrets und einer lokalen .env-Datei, die Git ignoriert. Versionen sind fest.'),
    say('step2', 'Step 2', 'Add the layers from the bottom up: data, an API helper, components, page objects and fixtures. A session fixture signs in through the API, so every test has its own cart.',
        'परतें नीचे से ऊपर जोड़ें: data, API helper, components, page objects और fixtures। Session fixture API से sign in करता है, इसलिए हर test की अपनी cart होती है।',
        'ಪದರಗಳನ್ನು ಕೆಳಗಿನಿಂದ ಸೇರಿಸಿ: data, API helper, components, page objects ಮತ್ತು fixtures. Session fixture API ಮೂಲಕ sign in ಮಾಡುತ್ತದೆ, ಆದ್ದರಿಂದ ಪ್ರತಿ test ಗೆ ತನ್ನದೇ cart.',
        'ସ୍ତରଗୁଡିକ ତଳୁ ଉପରକୁ ଯୋଡନ୍ତୁ: data, API helper, components, page objects ଓ fixtures। Session fixture API ରେ sign in କରେ, ତେଣୁ ପ୍ରତି test ର ନିଜ cart ଥାଏ।',
        'أضف الطبقات من الأسفل إلى الأعلى: البيانات، ومساعد API، والمكونات، وكائنات الصفحات، والمثبتات. ويسجل مثبت الجلسة الدخول عبر API، فلكل اختبار سلته الخاصة.',
        'Füge die Schichten von unten nach oben hinzu: Daten, einen API-Helfer, Komponenten, Page Objects und Fixtures. Eine Session-Fixture meldet sich über die API an, also hat jeder Test seinen eigenen Warenkorb.'),
    say('step3', 'Step 3', 'Put tests in one folder per feature and tag the most important ones as smoke. Playwright Test filters with --grep, pytest with -m, and TestNG with groups in a suite file.',
        'Tests को हर feature के लिए एक folder में रखें और सबसे ज़रूरी tests को smoke tag दें। Playwright Test --grep से, pytest -m से, और TestNG suite file के groups से छाँटता है।',
        'Tests ಅನ್ನು ಪ್ರತಿ feature ಗೆ ಒಂದು folder ನಲ್ಲಿ ಇಡಿ, ಮುಖ್ಯ tests ಗೆ smoke tag ಕೊಡಿ. Playwright Test --grep, pytest -m, TestNG suite file ನ groups ಮೂಲಕ ಆರಿಸುತ್ತದೆ.',
        'Tests କୁ ପ୍ରତି feature ପାଇଁ ଗୋଟିଏ folder ରେ ରଖନ୍ତୁ ଏବଂ ମୁଖ୍ୟ tests କୁ smoke tag ଦିଅନ୍ତୁ। Playwright Test --grep, pytest -m, ଏବଂ TestNG suite file ର groups ରେ ବାଛେ।',
        'ضع الاختبارات في مجلد لكل ميزة، ووسم أهمها بالوسم smoke. يرشّح Playwright Test بالخيار ‎--grep، وpytest بالخيار ‎-m، وTestNG بالمجموعات في ملف المجموعة.',
        'Lege Tests in einen Ordner pro Funktion und markiere die wichtigsten als smoke. Playwright Test filtert mit --grep, pytest mit -m und TestNG mit Gruppen in einer Suite-Datei.'),
    say('files', 'Every file', 'Open each file of the finished framework to read it and see why it is there. They are the same files the examples ran.',
        'पूरे framework की हर file खोलें, पढ़ें और देखें कि वह क्यों है। ये वही files हैं जो examples में चलीं।',
        'ಮುಗಿದ framework ನ ಪ್ರತಿ file ತೆರೆದು ಓದಿ, ಅದು ಏಕೆ ಇದೆ ಎಂದು ನೋಡಿ. ಇವು examples ನಡೆಸಿದ ಅದೇ files.',
        'ସମ୍ପୂର୍ଣ୍ଣ framework ର ପ୍ରତି file ଖୋଲି ପଢନ୍ତୁ ଏବଂ ଏହା କାହିଁକି ଅଛି ଦେଖନ୍ତୁ। ଏଗୁଡିକ examples ଚଳାଇଥିବା ସେହି files।',
        'افتح كل ملف من الإطار المكتمل لتقرأه وترى سبب وجوده. إنها الملفات نفسها التي شغّلتها الأمثلة.',
        'Öffne jede Datei des fertigen Frameworks, lies sie und sieh, warum sie da ist. Es sind dieselben Dateien, die die Beispiele ausgeführt haben.'),
    say('grow', 'Growing', 'Grow the framework when the tests ask for it: more environments, more roles, CI, reports, visual checks and data factories. A layer nobody needs yet is only more code to maintain.',
        'Framework तभी बढ़ाएँ जब tests को ज़रूरत हो: ज़्यादा environments, roles, CI, reports, visual checks और data factories। जिस परत की अभी किसी को ज़रूरत नहीं, वह बस संभालने वाला और code है।',
        'Tests ಬೇಡಿದಾಗ framework ಬೆಳೆಸಿ: ಹೆಚ್ಚು environments, roles, CI, reports, visual checks ಮತ್ತು data factories. ಯಾರಿಗೂ ಈಗ ಬೇಡದ ಪದರ ಕೇವಲ ನಿರ್ವಹಿಸಬೇಕಾದ ಹೆಚ್ಚಿನ code.',
        'Tests ଆବଶ୍ୟକ କଲେ framework ବଢାନ୍ତୁ: ଅଧିକ environments, roles, CI, reports, visual checks ଓ data factories। ଯେଉଁ ସ୍ତର ଏବେ କାହାକୁ ଦରକାର ନାହିଁ, ତାହା କେବଳ ସମ୍ଭାଳିବାକୁ ଥିବା ଅଧିକ code।',
        'وسّع الإطار حين تحتاجه الاختبارات: بيئات وأدوار أكثر، وCI، وتقارير، وفحوص مرئية، ومصانع بيانات. والطبقة التي لا يحتاجها أحد بعد ليست إلا كودًا إضافيًا للصيانة.',
        'Erweitere das Framework, wenn die Tests es brauchen: mehr Umgebungen, Rollen, CI, Berichte, visuelle Prüfungen und Datenfabriken. Eine Schicht, die noch niemand braucht, ist nur mehr Code zum Pflegen.'),
    say('practice', 'Playground labs', 'In the labs you write two of the framework tests yourself: the wrong password check and the search that finds nothing.',
        'Labs में आप framework के दो tests खुद लिखते हैं: गलत password वाला check और कुछ न मिलने वाली search।',
        'Labs ನಲ್ಲಿ framework ನ ಎರಡು tests ನೀವೇ ಬರೆಯುತ್ತೀರಿ: ತಪ್ಪು password check ಮತ್ತು ಏನೂ ಸಿಗದ search.',
        'Labs ରେ ଆପଣ framework ର ଦୁଇଟି tests ନିଜେ ଲେଖନ୍ତି: ଭୁଲ password check ଓ କିଛି ନମିଳୁଥିବା search।',
        'في المختبرات تكتب بنفسك اختبارين من الإطار: فحص كلمة المرور الخاطئة والبحث الذي لا يجد شيئًا.',
        'In den Labs schreibst du zwei Tests des Frameworks selbst: die Prüfung mit falschem Passwort und die Suche, die nichts findet.'),
]

QUIZ = [
    quiz(1, 'What is a test framework?', ['a browser', 'the code around tests that makes them easy to write, read and run', 'a CI server', 'a single test file'], 1,
         'Settings, data, helpers, pages, fixtures.', 'It is everything except the tests that the tests rely on.'),
    quiz(1, 'Where should a staging password live?', ['in users.ts', 'in CI secrets and a local .env that Git ignores', 'in the README', 'in playwright.config'], 1,
         'Never in the repository.', 'Secrets come from the environment, set by CI or a local .env file.'),
    quiz(1, 'Which pytest file holds fixtures for the whole project?', ['pytest.ini', 'conftest.py', 'requirements.txt', 'setup.py'], 1,
         'pytest finds it by name.', 'conftest.py fixtures are available to every test below it.'),
    quiz(1, 'How do you run only smoke tests in Playwright Test?', ['npx playwright test --smoke', 'npx playwright test --grep @smoke', 'npx playwright smoke', 'npm smoke'], 1,
         'Tags are filtered with grep.', '--grep @smoke runs the tests tagged @smoke.'),
    quiz(2, 'Why does the session fixture sign in through the API?', ['the UI cannot sign in', 'it is fast and gives each test its own cart', 'to skip the checks', 'Playwright requires it'], 1,
         'Speed and isolation.', 'An API sign in takes a fraction of a second and makes a fresh session per test.'),
    quiz(2, 'In the Java framework, what plays the part of fixtures?', ['pom.xml', 'BaseTest with @BeforeMethod and @AfterMethod', 'testng.xml', 'Config.java'], 1,
         'A parent class.', 'BaseTest opens and closes the browser and pages around every test.'),
    quiz(2, 'Why do TestNG set up methods need alwaysRun = true?', ['for speed', 'otherwise they are skipped when a group such as smoke is chosen', 'to run them twice', 'TestNG needs it for parallel runs'], 1,
         'Set up methods are not in the smoke group.', 'With a group filter, configuration methods outside the group are skipped unless alwaysRun is true.'),
    quiz(2, 'What do test files in a good framework contain?', ['locators and sleeps', 'steps and checks, using page objects', 'only configuration', 'copies of the page HTML'], 1,
         'Tests say what, not how.', 'Locators live in page objects. Tests read as steps and checks.'),
    quiz(2, 'Why must each TestNG class have its own Playwright when classes run in parallel?', ['Playwright objects are not safe to share between threads', 'TestNG cannot share objects', 'for the reports', 'it is faster to start'], 0,
         'Threads.', 'Playwright for Java objects must be used from one thread, so each class gets its own.'),
    quiz(3, 'Which file tells a new team member which settings to fill in?', ['.gitignore', '.env.example', 'package-lock.json', 'tsconfig.json'], 1,
         'It is committed without values.', '.env.example lists the setting names. The real .env is never committed.'),
    quiz(3, 'What should a framework add first when tests start repeating the same five page object calls?', ['nothing', 'a small business step such as checkout()', 'a new language', 'more retries'], 1,
         'Remove the repetition.', 'A business step built from page objects removes real repetition.'),
    quiz(3, 'Why do JavaScript ES module imports in the framework end in .js?', ['style only', 'Node needs the file extension for ES modules', 'Playwright requires it', 'for TypeScript'], 1,
         'type: module in package.json.', 'Node resolves ES module imports by exact path, so local imports name the file with its extension.'),
]

CALC = [
    calc(1, 'The framework has 7 tests and 3 are tagged smoke. How many run in the full suite but not in smoke?', 4, '7 - 3', ['7 - 3 = 4']),
    calc(1, 'Signing in through the page takes 3 s and through the API 0.2 s. How many tenths of a second does the API save per test?', 28, '(3 - 0.2) × 10', ['3 - 0.2 = 2.8 s', '2.8 s = 28 tenths']),
    calc(2, 'Across 400 tests, how many seconds does the API sign in save?', 1120, '400 × 2.8', ['400 × 2.8 = 1120 s']),
    calc(2, 'TestNG runs 4 test classes with thread-count 2. How many classes run at the same time?', 2, 'the thread count', ['2 threads, one class each']),
    calc(2, 'The cart test adds a ₹1,299 lamp and a ₹199 mug. What is the total in rupees?', 1498, '1299 + 199', ['1299 + 199 = 1498']),
    calc(3, 'The checkout test adds 2 water bottles at ₹349. What total does it check?', 698, '2 × 349', ['2 × 349 = 698']),
    calc(3, 'A framework has 4 page objects, 2 components, 1 API helper and 1 fixtures file. How many framework files hold locators?', 6, 'pages and components only', ['locators live in page objects and components', '4 + 2 = 6']),
    calc(3, 'A team adds 3 tests a week to a suite of 120. After how many weeks does it pass 180 tests?', 21, '(180 - 120) / 3, then one more week', ['60 more tests are needed to reach 180', '60 / 3 = 20 weeks reaches exactly 180', 'week 21 passes 180']),
]

LABS = [
    {'id': 'wrongpw', 'title': 'Write the wrong password test', 'name': 'a wrong password shows an error',
     'task': 'On <code>/login</code>, sign in as <code>asha@shop.example</code> with the password <code>wrong</code>, and check that the alert says <b>Wrong email or password</b>.',
     'goal': 'The error is shown and nobody is signed in.', 'start': '/login',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('a wrong password shows an error', async ({ page }) => {
  await page.goto('/login');
  // fill in the email and a wrong password, click Sign in, check the alert
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('a wrong password shows an error', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('wrong');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('alert')).toHaveText('Wrong email or password');
});'''},
     'hint': "The error has the role <code>alert</code>: <code>page.getByRole('alert')</code>.",
     'why': 'In the framework the same steps are loginPage.signIn() with a user whose password is wrong, and the check uses loginPage.error.',
     'check': [['!ctx.loggedIn', 'Nobody is signed in'], ["/Wrong email or password/.test(ctx.text)", 'The error is on the page']]},
    {'id': 'noresults', 'title': 'Write the search that finds nothing', 'name': 'says so when nothing matches',
     'task': 'On <code>/products</code>, type <code>piano</code> into the search box and check that <b>No products match your search</b> is shown.',
     'goal': 'The empty result message is shown.', 'start': '/products',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('says so when nothing matches', async ({ page }) => {
  await page.goto('/products');
  // search for piano and check the message
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('says so when nothing matches', async ({ page }) => {
  await page.goto('/products');
  await page.getByPlaceholder('Search products').fill('piano');
  await expect(page.getByText('No products match your search')).toBeVisible();
});'''},
     'hint': "The search box has the placeholder <b>Search products</b>.",
     'why': 'In the framework this is productsPage.searchFor("piano") and a check on productsPage.noResults.',
     'check': [["/No products match your search/.test(ctx.text)", 'The message is on the page'], ["/piano/.test(ctx.code)", 'The test searches for piano']]},
]

T = {
    'slug': 'pw-framework', 'title': 'Framework design, step by step', 'short': 'Framework design', 'emoji': '🏗️', 'module': MODULE, 'minutes': 30,
    'lead': 'Build the framework a company team would use, in TypeScript, JavaScript, Python and Java. Settings from the environment, test data, API helpers, page objects, fixtures and tagged tests, with a picture of every project folder.',
    'desc': 'A real Playwright framework in four languages: folder structure and hierarchy, environment settings and secrets, test data, an API helper for set up, components and page objects with a base page, fixtures in Playwright Test and pytest, a TestNG BaseTest with parallel classes, feature folders, smoke tags, groups and markers.',
    'summary': 'The same framework built and run in TypeScript, JavaScript, Python and Java: the runner finds the tests, the full suite passes, the smoke set runs alone, and every file is shown with why it is there.',
    'keywords': ['framework', 'folder structure', 'project structure', 'architecture', 'page object', 'fixtures', 'BaseTest', 'TestNG', 'pytest', 'conftest', 'env', 'secrets', 'smoke', 'tags', 'company'],
    'plain': 'A framework is the shared code that lets a team write many short tests: where the app is, who signs in, how each page works and how each test starts. Once it exists, a new test is a few lines.',
    'parts': PARTS, 'codes': CODES, 'trees': TREES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
