from pkit import part, say, quiz, calc, panel, four, one, js, ts, py, jv, shown, walk, step, table, tip, by, viz, figure, real_file, PYTEST_INI

MODULE = ('🚀', 'Getting started', 'pw-start', 'What Playwright is, how one line of a test travels to the browser, and the tools you get in Java, Python, JavaScript and TypeScript.')

CLI_POM = '''<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.brainy</groupId>
  <artifactId>shop-tests</artifactId>
  <version>1.0.0</version>
  <properties>
    <maven.compiler.release>21</maven.compiler.release>
  </properties>
  <dependencies>
    <dependency>
      <groupId>com.microsoft.playwright</groupId>
      <artifactId>playwright</artifactId>
      <version>1.63.0</version>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.codehaus.mojo</groupId>
        <artifactId>exec-maven-plugin</artifactId>
        <version>3.5.1</version>
      </plugin>
    </plugins>
  </build>
</project>'''

NO_FALLBACK = [(r'(?m)^  Download fallback.*\n', '')]

JAVA_CLI = 'mvn -q exec:java -D exec.mainClass=com.microsoft.playwright.CLI -D exec.args="{}"'

# A small suite with two tests, used to show how to run only one of them.
SUITE_TS = '''import { test, expect } from '@playwright/test';

test('a customer can sign in', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('s3cret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByText('Hello, Asha')).toBeVisible();
});

test('the products page has a title', async ({ page }) => {
  await page.goto('/products');
  await expect(page).toHaveTitle('Products · Brainy Shop');
});'''

SUITE_PY = '''from playwright.sync_api import Page, expect


def test_a_customer_can_sign_in(page: Page):
    page.goto("/login")
    page.get_by_label("Email").fill("asha@shop.example")
    page.get_by_label("Password").fill("s3cret")
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_text("Hello, Asha")).to_be_visible()


def test_the_products_page_has_a_title(page: Page):
    page.goto("/products")
    expect(page).to_have_title("Products · Brainy Shop")'''

SUITE_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class ShopTest {
  @Test
  void aCustomerCanSignIn(Page page) {
    page.navigate("/login");
    page.getByLabel("Email").fill("asha@shop.example");
    page.getByLabel("Password").fill("s3cret");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in")).click();
    assertThat(page.getByText("Hello, Asha")).isVisible();
  }

  @Test
  void theProductsPageHasATitle(Page page) {
    page.navigate("/products");
    assertThat(page).hasTitle("Products · Brainy Shop");
  }
}'''

CG = {k: real_file(f'codegen-{k}.txt') for k in ('ts', 'py', 'java', 'js-library')}

CLEAN_TS = '''import { test, expect } from '@playwright/test';

test('a customer can sign in', async ({ page }) => {
  await page.goto('/login');
  await page.getByRole('textbox', { name: 'Email' }).fill('asha@shop.example');
  await page.getByRole('textbox', { name: 'Password' }).fill('s3cret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByText('Hello, Asha')).toBeVisible();
});'''

SCAFFOLD_RUN_TS = '''import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('/');

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/Brainy Shop/);
});

test('get started link', async ({ page }) => {
  await page.goto('/');

  // Click the products link.
  await page.getByRole('link', { name: 'Products' }).first().click();

  // Expects page to have a heading with the name of Products.
  await expect(page.getByRole('heading', { name: 'Products' })).toBeVisible();
});'''

SCAFFOLD_CFG = real_file('init/playwright.config.ts').replace("    // baseURL: 'http://localhost:3000',", "    baseURL: 'http://localhost:4173',")

CODES = {
    'version': four('Check what is installed',
                    java=jv({}, cmd=JAVA_CLI.format('--version'), pom_xml=CLI_POM, options=False, show=['pom.xml']),
                    py=py({}, ini=None, cmd='pip list 2>/dev/null | grep -i playwright && python -m playwright --version', show=[]),
                    js=js({}, config=None, cmd='npx playwright --version', show=[]),
                    result='The Java and Python packages carry the same driver as the npm package, so all three print the same Playwright version. In Java the command line tool is the class <code>com.microsoft.playwright.CLI</code>, which Maven runs for you.'),
    'browsers': four('Where the browsers live',
                     java=jv({}, cmd=JAVA_CLI.format('install --dry-run chromium'), pom_xml=CLI_POM, options=False, show=[], replace=NO_FALLBACK),
                     py=py({}, ini=None, cmd='playwright install --dry-run chromium', show=[], replace=NO_FALLBACK),
                     js=js({}, config=None, cmd='npx playwright install --dry-run chromium', show=[], replace=NO_FALLBACK),
                     result='<code>--dry-run</code> shows what would be downloaded and where, without downloading. On this build machine the variable <code>PLAYWRIGHT_BROWSERS_PATH</code> points to <code>/opt/pw-browsers</code>. On your own computer the default is <code>~/.cache/ms-playwright</code> on Linux, <code>~/Library/Caches/ms-playwright</code> on macOS and <code>%USERPROFILE%\\AppData\\Local\\ms-playwright</code> on Windows. Since version 1.57, Chromium means a Chrome for Testing build, and headless runs use the smaller Chrome Headless Shell.'),
    'scaffold': one('The test that npm init playwright wrote, pointed at the shop',
                    ts({'example.spec.ts': SCAFFOLD_RUN_TS}, config=SCAFFOLD_CFG.replace("reporter: 'html'", "reporter: 'list'").replace(
                        """    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
""", ''), show=['tests/example.spec.ts', 'playwright.config.ts']),
                    result='The two starter tests visit playwright.dev, so here they were changed to visit the shop, and the config got a <code>baseURL</code>. The Firefox and WebKit projects were removed for this run because only Chromium is installed on the build machine. With all three projects, each test runs three times, once per browser.'),
    'codegen': four('What codegen recorded, run as it is',
                    java=jv({'src/test/java/TestExample.java': CG['java']}),
                    py=py({'test_example.py': CG['py']}),
                    js=js({'example.spec.js': CG['ts']}),
                    ts=ts({'example.spec.ts': CG['ts']}),
                    result='This is exactly the code codegen wrote while the build clicked and typed into the recording browser. It runs and passes, but it has no check at the end. A test without a check only proves that nothing crashed.'),
    'clean': four('The same test after a clean up',
                  java=jv({'SignInTest.java': '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class SignInTest {
  @Test
  void aCustomerCanSignIn(Page page) {
    page.navigate("/login");
    page.getByRole(AriaRole.TEXTBOX, new Page.GetByRoleOptions().setName("Email")).fill("asha@shop.example");
    page.getByRole(AriaRole.TEXTBOX, new Page.GetByRoleOptions().setName("Password")).fill("s3cret");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in")).click();
    assertThat(page.getByText("Hello, Asha")).isVisible();
  }
}'''}),
                  py=py({'test_sign_in.py': '''from playwright.sync_api import Page, expect


def test_a_customer_can_sign_in(page: Page):
    page.goto("/login")
    page.get_by_role("textbox", name="Email").fill("asha@shop.example")
    page.get_by_role("textbox", name="Password").fill("s3cret")
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_text("Hello, Asha")).to_be_visible()'''}),
                  js=js({'sign-in.spec.js': CLEAN_TS}),
                  ts=ts({'sign-in.spec.ts': CLEAN_TS}),
                  result='Four changes: a clear test name, a relative address that uses the base URL from the config, no extra <code>click</code> before <code>fill</code> (fill focuses the box by itself), and a check at the end.'),
    'pick': four('Run only one test from a file',
                 java=jv({'ShopTest.java': SUITE_JAVA}, cmd='mvn test -Dtest="ShopTest#aCustomerCanSignIn"'),
                 py=py({'test_shop.py': SUITE_PY}, cmd='pytest -v -k sign_in'),
                 js=js({'shop.spec.js': SUITE_TS}, cmd='npx playwright test -g "sign in"'),
                 ts=ts({'shop.spec.ts': SUITE_TS}, cmd='npx playwright test -g "sign in"'),
                 result='Each runner picks tests by name. Playwright Test uses <code>-g</code> (grep) with part of the title. pytest uses <code>-k</code> with part of the function name, and reports the other test as deselected. Maven Surefire uses <code>-Dtest=Class#method</code>.'),
    'list': four('List the tests without running them',
                 java=jv({'ShopTest.java': SUITE_JAVA}, cmd='mvn -q test-compile && find target/test-classes -name "*Test.class"', show=[]),
                 py=py({'test_shop.py': SUITE_PY}, cmd='pytest --collect-only -q', show=[]),
                 js=js({'shop.spec.js': SUITE_TS}, cmd='npx playwright test --list', show=[]),
                 ts=ts({'shop.spec.ts': SUITE_TS}, cmd='npx playwright test --list', show=[]),
                 result='Listing is a quick way to check that a filter or a tag selects the tests you expect before a long run. Maven has no list option, so the Java tab compiles the tests and shows the compiled test classes.'),
}

TREES = {
    'init': {'t': 'What npm init playwright created', 's': 'These are the real files from running npm init playwright@latest with TypeScript and the GitHub Actions option. Click a file to read it.',
             'files': [
                 {'p': 'my-tests/', 'why': 'your project folder'},
                 {'p': 'my-tests/.github/', 'why': ''},
                 {'p': 'my-tests/.github/workflows/', 'why': ''},
                 {'p': 'my-tests/.github/workflows/playwright.yml', 'why': 'A GitHub Actions pipeline. On every push and pull request it installs the packages and browsers, runs the tests and uploads the HTML report.', 'body': real_file('init/.github/workflows/playwright.yml')},
                 {'p': 'my-tests/tests/', 'why': 'every test file lives here'},
                 {'p': 'my-tests/tests/example.spec.ts', 'why': 'Two starter tests. A file ending in .spec.ts or .test.ts is picked up as a test file.', 'body': real_file('init/tests/example.spec.ts')},
                 {'p': 'my-tests/.gitignore', 'why': 'Keeps reports, results and saved logins out of Git.', 'body': real_file('init/.gitignore')},
                 {'p': 'my-tests/package.json', 'why': 'Lists @playwright/test and @types/node as development packages.', 'body': real_file('init/package.json')},
                 {'p': 'my-tests/playwright.config.ts', 'why': 'All settings in one place: where the tests are, parallel runs, retries on CI, the reporter, trace and one project per browser.', 'body': real_file('init/playwright.config.ts')},
             ]},
    'py': {'t': 'A Python project with pytest-playwright', 's': 'pip does not create files, so this is the layout teams usually start with. Click a file to read it.',
           'files': [
               {'p': 'shop-tests/', 'why': 'your project folder'},
               {'p': 'shop-tests/tests/', 'why': 'pytest collects files named test_*.py'},
               {'p': 'shop-tests/tests/test_sign_in.py', 'why': 'A test is a function whose name starts with test_. It asks for the page fixture.', 'body': SUITE_PY},
               {'p': 'shop-tests/.venv/', 'why': 'the virtual environment, never committed'},
               {'p': 'shop-tests/pytest.ini', 'why': 'pytest settings. addopts adds options to every run, here the base URL.', 'body': PYTEST_INI},
               {'p': 'shop-tests/requirements.txt', 'why': 'The exact package versions, so every machine installs the same ones.', 'body': 'playwright==1.63.0\npytest==9.1.1\npytest-playwright==0.10.0'},
           ]},
    'java': {'t': 'A Java project with Maven and JUnit 5', 's': 'The standard Maven layout. Test code goes in src/test/java. Click a file to read it.',
             'files': [
                 {'p': 'shop-tests/', 'why': 'your project folder'},
                 {'p': 'shop-tests/src/', 'why': ''},
                 {'p': 'shop-tests/src/test/', 'why': ''},
                 {'p': 'shop-tests/src/test/java/', 'why': 'Maven compiles and runs tests from here'},
                 {'p': 'shop-tests/src/test/java/com/', 'why': ''},
                 {'p': 'shop-tests/src/test/java/com/brainy/', 'why': 'the package of your tests'},
                 {'p': 'shop-tests/src/test/java/com/brainy/ShopOptions.java', 'why': 'Shared settings for @UsePlaywright: headless and the base URL.', 'body': __import__('pkit').SHOP_OPTIONS},
                 {'p': 'shop-tests/src/test/java/com/brainy/ShopTest.java', 'why': 'A JUnit 5 test class. Surefire runs classes whose names end in Test.', 'body': SUITE_JAVA},
                 {'p': 'shop-tests/pom.xml', 'why': 'Maven reads this: the Playwright and JUnit dependencies and the Surefire plugin that runs the tests.', 'body': __import__('pkit').pom('junit')},
             ]},
}

PARTS = [
    part('need', '🧰', 'What you need before you start', f'''
<p>Every language needs its own runtime, plus the browsers that Playwright downloads. These are the requirements from the official installation pages for the current release.</p>
{table(['', '☕ Java', '🐍 Python', '🟨 JavaScript and 🔷 TypeScript'], [
    ['Runtime', 'Java 8 or later (this page uses Java 21)', 'Python 3.8 or later (this page uses 3.13, and the newest pytest needs 3.10)', 'Node.js 22, 24 or 26'],
    ['Package tool', 'Maven or Gradle', 'pip, Poetry or uv', 'npm, yarn or pnpm'],
    ['Editor most teams use', 'IntelliJ IDEA', 'PyCharm or VS Code', 'VS Code with the Playwright extension'],
    ['Operating system', 'Windows 11, macOS 14 or later, Debian 12 or 13, Ubuntu 22.04, 24.04 or 26.04', 'same', 'same'],
])}
{tip('Install the runtime first and check it from a terminal: <code>java -version</code>, <code>python --version</code> or <code>node --version</code>. If the command is not found, the runtime is not on your PATH yet, and nothing below will work.', 'kid')}
''', easy=True, kw=['requirements', 'node version', 'python version', 'java version', 'install']),

    part('install', '📦', 'Install Playwright in your language', f'''
<p>Choose your language below. Each tab shows the commands you type, in order.</p>
<div class="only-java">
<p><b>Java.</b> Add one dependency to <code>pom.xml</code>. Add JUnit 5 too if you want the <code>@UsePlaywright</code> annotation that gives each test a page.</p>
<pre class="src">{'&lt;dependency&gt;'}
  &lt;groupId&gt;com.microsoft.playwright&lt;/groupId&gt;
  &lt;artifactId&gt;playwright&lt;/artifactId&gt;
  &lt;version&gt;1.63.0&lt;/version&gt;
&lt;/dependency&gt;</pre>
<p>Maven downloads the jar the first time you build. The first time your code calls <code>Playwright.create()</code>, it downloads the browsers too. To download them yourself, for example in a CI image, run the command line tool through Maven:</p>
<pre class="src">mvn exec:java -e -D exec.mainClass=com.microsoft.playwright.CLI -D exec.args="install --with-deps"</pre>
</div>
<div class="only-py">
<p><b>Python.</b> Make a virtual environment, install the pytest plugin, then download the browsers.</p>
<pre class="src">python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\\Scripts\\activate
pip install pytest-playwright     # installs playwright and pytest too
playwright install --with-deps    # downloads the browsers and the system libraries they need</pre>
</div>
<div class="only-js only-ts">
<p><b>JavaScript and TypeScript.</b> One command creates the project, asks four questions and downloads the browsers.</p>
<pre class="src">npm init playwright@latest</pre>
<p>It asks: TypeScript or JavaScript (TypeScript is the default), the name of the tests folder, whether to add a GitHub Actions workflow, and whether to install the browsers. In an existing project the same command adds Playwright to your <code>package.json</code>.</p>
</div>
<p>Now check what you have. These commands ran on the build machine of this page.</p>
[[version]]
<p>Playwright downloads its own browsers so that every machine tests with exactly the same versions. The <code>--with-deps</code> option also installs the operating system libraries the browsers need on Linux, which is what you want on a CI server.</p>
[[browsers]]
{tip('Keep one Playwright version per project and update on purpose. Each Playwright release expects its own browser builds. After you update the package, run the install command again, or the tests stop with an error that says the browser executable does not exist.', 'warn')}
''', easy=True, kw=['install', 'npm init playwright', 'pip install pytest-playwright', 'maven dependency', 'playwright install', 'with-deps']),

    part('project', '🗂️', 'The files of a new project', f'''
<p>A Playwright project is a handful of files. Click through the three projects below. The first one contains the real files that <code>npm init playwright@latest</code> wrote when this page was built.</p>
<div class="only-js only-ts">{viz('pwtree', k='init')}</div>
<div class="only-py">{viz('pwtree', k='py')}</div>
<div class="only-java">{viz('pwtree', k='java')}</div>
<p>Switch the language at the top of the page to see the other projects. The scaffolded starter tests visit playwright.dev. Here they were pointed at the shop and run for real:</p>
[[scaffold]]
<p>Three ideas are the same in every language:</p>
<ul>
<li><b>Tests live in their own folder</b>: <code>tests/</code>, or <code>src/test/java</code> in Maven.</li>
<li><b>A naming rule tells the runner what is a test</b>: <code>*.spec.ts</code>, <code>test_*.py</code>, or a class ending in <code>Test</code>.</li>
<li><b>Settings live in one file</b>: <code>playwright.config.ts</code>, <code>pytest.ini</code> and <code>conftest.py</code>, or an options class in Java.</li>
</ul>
''', easy=True, kw=['project structure', 'playwright.config.ts', 'pytest.ini', 'pom.xml', 'scaffold']),

    part('codegen', '🎬', 'Record a test with codegen', f'''
<p>Codegen opens a browser and a second window called the Playwright Inspector. Everything you do in the browser is written down as code, in the language you choose. It is the fastest way to find good locators for a page you do not know yet.</p>
<pre class="src">{by(java='mvn exec:java -e -D exec.mainClass=com.microsoft.playwright.CLI -D exec.args="codegen --target java-junit http://localhost:4173/login"',
         py='playwright codegen --target python-pytest http://localhost:4173/login',
         js='npx playwright codegen http://localhost:4173/login')}</pre>
<p>These pictures are real. The build started codegen on a virtual screen, then clicked into the boxes and typed, exactly as you would.</p>
{figure('codegen-start.jpg', 'The Brainy Shop sign in page on the left and an almost empty Playwright Inspector on the right', 'Codegen just started. The recording browser is on the left, the Inspector on the right. The small toolbar over the page has buttons to pick a locator and to add checks.')}
<div class="only-ts only-js">{figure('codegen-ts.jpg', 'The products page after signing in, with the recorded TypeScript test in the Inspector', 'After typing the email and password and clicking Sign in. The Inspector shows the recorded Playwright Test code.')}</div>
<div class="only-py">{figure('codegen-py.jpg', 'The products page after signing in, with the recorded pytest code in the Inspector', 'The same recording with the target set to Pytest.')}</div>
<div class="only-java">{figure('codegen-java.jpg', 'The products page after signing in, with the recorded JUnit code in the Inspector', 'The same recording with the target set to Java JUnit.')}</div>
[[codegen]]
<p>Treat recorded code as a first draft. Clean it up before you commit it:</p>
[[clean]]
{tip('Codegen picks locators the same way you should: role and accessible name first, then label, placeholder or text, and a test id only when nothing better exists. When the recorded locator looks odd, the page itself is often missing a label, which is worth reporting to the developers.', 'pro')}
''', easy=True, kw=['codegen', 'record', 'inspector', 'target', 'python-pytest', 'java-junit']),

    part('run', '▶️', 'Running tests from the terminal', f'''
<p>You will type these commands every day. Find your language in the table.</p>
{table(['I want to', '☕ Java (Maven)', '🐍 Python (pytest)', '🟨🔷 Playwright Test'], [
    ['run every test', '<code>mvn test</code>', '<code>pytest</code>', '<code>npx playwright test</code>'],
    ['run one file', '<code>mvn test -Dtest=ShopTest</code>', '<code>pytest tests/test_shop.py</code>', '<code>npx playwright test tests/shop.spec.ts</code>'],
    ['run tests by name', '<code>-Dtest="ShopTest#signIn"</code>', '<code>-k sign_in</code>', '<code>-g "sign in"</code>'],
    ['see the browser', '<code>setHeadless(false)</code> in the options', '<code>--headed</code>', '<code>--headed</code>'],
    ['slow every action down', '<code>setSlowMo(500)</code> in the launch options', '<code>--slowmo 500</code>', '<code>launchOptions: { slowMo: 500 }</code> in the config'],
    ['pick a browser', '<code>setBrowserName("firefox")</code>', '<code>--browser firefox</code>', '<code>--project=firefox</code>'],
    ['debug step by step', '<code>PWDEBUG=1 mvn test</code>', '<code>PWDEBUG=1 pytest -s</code>', '<code>--debug</code> or <code>--ui</code>'],
    ['run 4 at a time', 'JUnit parallel settings', '<code>-n 4</code> (pytest-xdist)', '<code>--workers=4</code>'],
])}
[[pick]]
[[list]]
''', kw=['run tests', 'cli', 'headed', 'grep', '-k', '-Dtest', 'list', 'debug']),

    part('ide', '🧑‍💻', 'Your editor', f'''
<p>You can write Playwright tests in any editor, but these make life easier:</p>
<ul>
<li><b>VS Code with the Playwright Test extension</b> (JavaScript and TypeScript). It adds a Testing panel to run or debug one test with a click, a <b>Show browser</b> option, <b>Pick locator</b> to hover the page and copy a locator, and <b>Record new</b> to start codegen inside the editor. Since version 1.56 it can also set up the Playwright test agents.</li>
<li><b>IntelliJ IDEA</b> (Java). JUnit and TestNG tests get a green run button next to every method. Add <code>PWDEBUG=1</code> to the run configuration to open the Inspector.</li>
<li><b>PyCharm or VS Code with the Python extension</b> (Python). Both understand pytest, so every <code>test_</code> function gets a run button. Set the interpreter to the project's <code>.venv</code>.</li>
</ul>
{tip('Turn on format on save and a linter in your editor from day one. In TypeScript, the ESLint rule <code>@typescript-eslint/no-floating-promises</code> catches a missing <code>await</code>, the bug from chapter 1, before you even run the test.', 'pro')}
''', easy=True, kw=['vs code', 'extension', 'intellij', 'pycharm', 'pick locator']),

    part('update', '🔄', 'Updating Playwright safely', f'''
<p>Playwright ships a new minor version about once a month. Update on a branch, run the whole suite, read the release notes, then merge.</p>
{table(['Language', 'Update the package', 'Then'], [
    ['☕ Java', 'change <code>&lt;version&gt;</code> in pom.xml', 'run the tests. The new browsers download on first use, or run the CLI <code>install</code> command'],
    ['🐍 Python', '<code>pip install -U pytest-playwright playwright</code>', '<code>playwright install --with-deps</code>'],
    ['🟨🔷 JavaScript and TypeScript', '<code>npm install -D @playwright/test@latest</code>', '<code>npx playwright install --with-deps</code>'],
])}
{tip('Pin exact versions in your project (no ^ in package.json, == in requirements.txt). Then a teammate and the CI server always run the same Playwright, and an update is a change you can see and review.', 'tip')}
''', kw=['update', 'upgrade', 'version', 'release notes']),
]

INFO = {'title': 'From nothing to a running test', 'panels': [
    panel([['e', '🧰'], ['t', 'java · python · node', {'b': 1}]], 'Runtime', 'Install your language first.', 'Check it with a version command.'),
    panel([['e', '📦'], ['t', 'install the package', {'b': 1}]], 'Package', 'Maven, pip or npm.', 'Pin the exact version.'),
    panel([['e', '🌐'], ['t', 'playwright install', {'b': 1}]], 'Browsers', 'Playwright brings its own.', '--with-deps adds the Linux libraries.'),
    panel([['e', '🎬'], ['t', 'codegen', {'b': 1}]], 'Record', 'Click around, get code.', 'Then clean it up and add a check.')],
    'remember': 'Install the runtime, the Playwright package and its browsers, record a first draft with codegen, then turn it into a real test with a clear name and a check.'}

REAL = [
    ['🆕', 'First day in a QA team', 'A new tester clones the repository, runs the install command from the README and then the whole suite. If that takes more than ten minutes to get working, the team writes the missing steps into the README.'],
    ['🔁', 'A monthly update', 'One person updates Playwright on a branch every month, runs the suite in CI and reads the release notes, so the team never falls a year behind and faces one huge jump.'],
    ['🎬', 'Learning a new page fast', 'A tester has to cover a new checkout screen. Five minutes of codegen gives working locators for every field, and the next half hour goes into good checks and test data.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter installs Playwright in Java, Python, JavaScript and TypeScript, explains the project files, records a test with codegen and shows how to run tests from the terminal.',
        'यह अध्याय Java, Python, JavaScript और TypeScript में Playwright install करता है, project की files समझाता है, codegen से टेस्ट रिकॉर्ड करता है और terminal से टेस्ट चलाना दिखाता है।',
        'ಈ ಅಧ್ಯಾಯ Java, Python, JavaScript ಮತ್ತು TypeScript ನಲ್ಲಿ Playwright install ಮಾಡುತ್ತದೆ, project files ವಿವರಿಸುತ್ತದೆ, codegen ಮೂಲಕ ಟೆಸ್ಟ್ ರೆಕಾರ್ಡ್ ಮಾಡುತ್ತದೆ ಮತ್ತು terminal ನಿಂದ ಟೆಸ್ಟ್ ನಡೆಸುವುದನ್ನು ತೋರಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ Java, Python, JavaScript ଓ TypeScript ରେ Playwright install କରେ, project files ବୁଝାଏ, codegen ଦ୍ୱାରା ଟେଷ୍ଟ ରେକର୍ଡ କରେ ଏବଂ terminal ରୁ ଟେଷ୍ଟ ଚଳାଇବା ଦେଖାଏ।',
        'يثبّت هذا الفصل Playwright في Java وPython وJavaScript وTypeScript، ويشرح ملفات المشروع، ويسجّل اختبارًا باستخدام codegen، ويبيّن كيفية تشغيل الاختبارات من الطرفية.',
        'Dieses Kapitel installiert Playwright in Java, Python, JavaScript und TypeScript, erklärt die Projektdateien, nimmt einen Test mit Codegen auf und zeigt, wie man Tests im Terminal startet.'),
    say('need', 'What you need', 'You need Java 8 or later, Python 3.8 or later, or Node.js 22, 24 or 26, plus a package tool such as Maven, pip or npm, and a good editor.',
        'आपको Java 8 या नया, Python 3.8 या नया, या Node.js 22, 24 या 26 चाहिए, साथ में Maven, pip या npm जैसा package tool और एक अच्छा editor।',
        'ನಿಮಗೆ Java 8 ಅಥವಾ ಹೊಸದು, Python 3.8 ಅಥವಾ ಹೊಸದು, ಅಥವಾ Node.js 22, 24 ಅಥವಾ 26, ಜೊತೆಗೆ Maven, pip ಅಥವಾ npm ನಂತಹ package tool ಮತ್ತು ಒಳ್ಳೆಯ editor ಬೇಕು.',
        'ଆପଣଙ୍କୁ Java 8 କିମ୍ବା ନୂଆ, Python 3.8 କିମ୍ବା ନୂଆ, କିମ୍ବା Node.js 22, 24 ବା 26, ସହିତ Maven, pip ବା npm ଭଳି package tool ଏବଂ ଏକ ଭଲ editor ଦରକାର।',
        'تحتاج إلى Java 8 أو أحدث، أو Python 3.8 أو أحدث، أو Node.js 22 أو 24 أو 26، مع أداة حزم مثل Maven أو pip أو npm، ومحرر جيد.',
        'Du brauchst Java 8 oder neuer, Python 3.8 oder neuer oder Node.js 22, 24 oder 26, dazu ein Paketwerkzeug wie Maven, pip oder npm und einen guten Editor.'),
    say('install', 'Install Playwright', 'In Java add the Maven dependency. In Python run pip install pytest-playwright and then playwright install. In JavaScript and TypeScript run npm init playwright at latest. Then check the version.',
        'Java में Maven dependency जोड़ें। Python में pip install pytest-playwright और फिर playwright install चलाएँ। JavaScript और TypeScript में npm init playwright at latest चलाएँ। फिर version जाँचें।',
        'Java ದಲ್ಲಿ Maven dependency ಸೇರಿಸಿ. Python ನಲ್ಲಿ pip install pytest-playwright ಮತ್ತು ನಂತರ playwright install ನಡೆಸಿ. JavaScript ಮತ್ತು TypeScript ನಲ್ಲಿ npm init playwright at latest ನಡೆಸಿ. ನಂತರ version ಪರಿಶೀಲಿಸಿ.',
        'Java ରେ Maven dependency ଯୋଡନ୍ତୁ। Python ରେ pip install pytest-playwright ଏବଂ ପରେ playwright install ଚଳାନ୍ତୁ। JavaScript ଓ TypeScript ରେ npm init playwright at latest ଚଳାନ୍ତୁ। ତାପରେ version ଯାଞ୍ଚ କରନ୍ତୁ।',
        'في Java أضف اعتمادية Maven. في Python شغّل pip install pytest-playwright ثم playwright install. في JavaScript وTypeScript شغّل npm init playwright at latest. ثم تحقق من الإصدار.',
        'In Java fügst du die Maven-Abhängigkeit hinzu. In Python führst du pip install pytest-playwright und dann playwright install aus. In JavaScript und TypeScript führst du npm init playwright at latest aus. Danach prüfst du die Version.'),
    say('project', 'Project files', 'A project keeps tests in their own folder, uses a naming rule so the runner finds them, and keeps all settings in one file such as playwright config, pytest ini or an options class.',
        'Project में टेस्ट अलग folder में रहते हैं, एक naming rule से runner उन्हें ढूँढता है, और सारी settings एक file में रहती हैं जैसे playwright config, pytest ini या options class।',
        'Project ನಲ್ಲಿ ಟೆಸ್ಟ್‌ಗಳು ಪ್ರತ್ಯೇಕ folder ನಲ್ಲಿರುತ್ತವೆ, naming rule ಮೂಲಕ runner ಅವುಗಳನ್ನು ಹುಡುಕುತ್ತದೆ ಮತ್ತು ಎಲ್ಲಾ settings playwright config, pytest ini ಅಥವಾ options class ನಂತಹ ಒಂದೇ file ನಲ್ಲಿರುತ್ತವೆ.',
        'Project ରେ ଟେଷ୍ଟ ଅଲଗା folder ରେ ରହେ, naming rule ଦ୍ୱାରା runner ସେମାନଙ୍କୁ ଖୋଜେ, ଏବଂ ସବୁ settings playwright config, pytest ini ବା options class ଭଳି ଗୋଟିଏ file ରେ ରହେ।',
        'يحتفظ المشروع بالاختبارات في مجلد خاص، ويستخدم قاعدة تسمية ليجدها المشغّل، ويضع كل الإعدادات في ملف واحد مثل playwright config أو pytest ini أو صنف الخيارات.',
        'Ein Projekt hält die Tests in einem eigenen Ordner, nutzt eine Namensregel, damit der Runner sie findet, und bündelt alle Einstellungen in einer Datei wie playwright config, pytest ini oder einer Options-Klasse.'),
    say('codegen', 'Codegen', 'Codegen records what you do in a browser and writes it as code in your language. Use it as a first draft, then remove extra clicks, use the base URL and add a check at the end.',
        'Codegen ब्राउज़र में आपके काम रिकॉर्ड करके आपकी भाषा में code लिखता है। इसे पहला draft मानें, फिर फालतू clicks हटाएँ, base URL इस्तेमाल करें और अंत में check जोड़ें।',
        'Codegen ಬ್ರೌಸರ್‌ನಲ್ಲಿ ನೀವು ಮಾಡುವುದನ್ನು ರೆಕಾರ್ಡ್ ಮಾಡಿ ನಿಮ್ಮ ಭಾಷೆಯಲ್ಲಿ code ಬರೆಯುತ್ತದೆ. ಅದನ್ನು ಮೊದಲ draft ಆಗಿ ಬಳಸಿ, ಹೆಚ್ಚುವರಿ clicks ತೆಗೆದು, base URL ಬಳಸಿ, ಕೊನೆಗೆ check ಸೇರಿಸಿ.',
        'Codegen ବ୍ରାଉଜରରେ ଆପଣ ଯାହା କରନ୍ତି ତାହା ରେକର୍ଡ କରି ଆପଣଙ୍କ ଭାଷାରେ code ଲେଖେ। ଏହାକୁ ପ୍ରଥମ draft ଭାବେ ନିଅନ୍ତୁ, ଅଧିକ clicks ହଟାନ୍ତୁ, base URL ବ୍ୟବହାର କରନ୍ତୁ ଏବଂ ଶେଷରେ check ଯୋଡନ୍ତୁ।',
        'يسجّل codegen ما تفعله في المتصفح ويكتبه شيفرة بلغتك. استخدمه كمسودة أولى، ثم احذف النقرات الزائدة واستخدم العنوان الأساسي وأضف تحققًا في النهاية.',
        'Codegen zeichnet auf, was du im Browser tust, und schreibt es als Code in deiner Sprache. Nutze es als ersten Entwurf, entferne dann überflüssige Klicks, verwende die Basis-URL und füge am Ende eine Prüfung hinzu.'),
    say('run', 'Running tests', 'Run all tests with mvn test, pytest or npx playwright test. Pick tests by name with minus D test, minus k or minus g, and list them first to check your filter.',
        'सारे टेस्ट mvn test, pytest या npx playwright test से चलाएँ। नाम से टेस्ट चुनने के लिए minus D test, minus k या minus g लगाएँ, और filter जाँचने के लिए पहले उनकी सूची देखें।',
        'ಎಲ್ಲಾ ಟೆಸ್ಟ್‌ಗಳನ್ನು mvn test, pytest ಅಥವಾ npx playwright test ಮೂಲಕ ನಡೆಸಿ. ಹೆಸರಿನಿಂದ ಆಯ್ಕೆ ಮಾಡಲು minus D test, minus k ಅಥವಾ minus g ಬಳಸಿ, filter ಪರಿಶೀಲಿಸಲು ಮೊದಲು ಪಟ್ಟಿ ನೋಡಿ.',
        'ସବୁ ଟେଷ୍ଟ mvn test, pytest ବା npx playwright test ରେ ଚଳାନ୍ତୁ। ନାମ ଅନୁସାରେ ବାଛିବାକୁ minus D test, minus k ବା minus g ବ୍ୟବହାର କରନ୍ତୁ, ଏବଂ filter ଯାଞ୍ଚ ପାଇଁ ପ୍ରଥମେ ତାଲିକା ଦେଖନ୍ତୁ।',
        'شغّل كل الاختبارات بـ mvn test أو pytest أو npx playwright test. اختر الاختبارات بالاسم باستخدام ناقص D test أو ناقص k أو ناقص g، واعرض قائمتها أولًا للتحقق من المرشح.',
        'Starte alle Tests mit mvn test, pytest oder npx playwright test. Wähle Tests per Name mit minus D test, minus k oder minus g und liste sie vorher auf, um deinen Filter zu prüfen.'),
    say('ide', 'Your editor', 'VS Code has a Playwright extension with run buttons, pick locator and record. IntelliJ suits Java and PyCharm suits Python, and both give every test a run button.',
        'VS Code में Playwright extension है जिसमें run buttons, pick locator और record हैं। Java के लिए IntelliJ और Python के लिए PyCharm अच्छे हैं, दोनों हर टेस्ट को run button देते हैं।',
        'VS Code ನಲ್ಲಿ run buttons, pick locator ಮತ್ತು record ಇರುವ Playwright extension ಇದೆ. Java ಗೆ IntelliJ ಮತ್ತು Python ಗೆ PyCharm ಸೂಕ್ತ, ಎರಡೂ ಪ್ರತಿ ಟೆಸ್ಟ್‌ಗೆ run button ನೀಡುತ್ತವೆ.',
        'VS Code ରେ run buttons, pick locator ଓ record ଥିବା Playwright extension ଅଛି। Java ପାଇଁ IntelliJ ଓ Python ପାଇଁ PyCharm ଉପଯୁକ୍ତ, ଦୁହେଁ ପ୍ରତ୍ୟେକ ଟେଷ୍ଟକୁ run button ଦିଅନ୍ତି।',
        'يحتوي VS Code على إضافة Playwright فيها أزرار تشغيل واختيار المحدد والتسجيل. يناسب IntelliJ لغة Java ويناسب PyCharm لغة Python، وكلاهما يعطي كل اختبار زر تشغيل.',
        'VS Code hat eine Playwright-Erweiterung mit Startknöpfen, Pick Locator und Aufnahme. IntelliJ passt zu Java und PyCharm zu Python, und beide geben jedem Test einen Startknopf.'),
    say('update', 'Updating safely', 'Update Playwright on a branch, install the matching browsers again, run the whole suite and read the release notes. Pin exact versions so everyone runs the same one.',
        'Playwright को branch पर update करें, matching browsers फिर से install करें, पूरा suite चलाएँ और release notes पढ़ें। Exact versions pin करें ताकि सब एक ही version चलाएँ।',
        'Playwright ಅನ್ನು branch ನಲ್ಲಿ update ಮಾಡಿ, ಹೊಂದುವ browsers ಮತ್ತೆ install ಮಾಡಿ, ಪೂರ್ಣ suite ನಡೆಸಿ ಮತ್ತು release notes ಓದಿ. ಎಲ್ಲರೂ ಒಂದೇ version ನಡೆಸಲು exact versions pin ಮಾಡಿ.',
        'Playwright କୁ branch ରେ update କରନ୍ତୁ, ମେଳ ଖାଉଥିବା browsers ପୁଣି install କରନ୍ତୁ, ପୂରା suite ଚଳାନ୍ତୁ ଏବଂ release notes ପଢ଼ନ୍ତୁ। ସମସ୍ତେ ଏକା version ଚଳାଇବା ପାଇଁ exact versions pin କରନ୍ତୁ।',
        'حدّث Playwright في فرع منفصل، وثبّت المتصفحات المطابقة مرة أخرى، وشغّل كل الاختبارات واقرأ ملاحظات الإصدار. ثبّت الإصدارات بدقة ليعمل الجميع على الإصدار نفسه.',
        'Aktualisiere Playwright auf einem Branch, installiere die passenden Browser erneut, führe die ganze Suite aus und lies die Release Notes. Lege exakte Versionen fest, damit alle dieselbe nutzen.'),
    say('practice', 'Playground labs', 'In the labs you clean up a recorded test and write a search test, then run them against the practice shop in your language.',
        'Labs में आप एक रिकॉर्ड किया गया टेस्ट साफ़ करते हैं और एक search टेस्ट लिखते हैं, फिर उन्हें अपनी भाषा में practice shop पर चलाते हैं।',
        'Labs ನಲ್ಲಿ ನೀವು ರೆಕಾರ್ಡ್ ಮಾಡಿದ ಟೆಸ್ಟ್ ಸ್ವಚ್ಛಗೊಳಿಸಿ ಒಂದು search ಟೆಸ್ಟ್ ಬರೆಯುತ್ತೀರಿ, ನಂತರ ನಿಮ್ಮ ಭಾಷೆಯಲ್ಲಿ practice shop ಮೇಲೆ ನಡೆಸುತ್ತೀರಿ.',
        'Labs ରେ ଆପଣ ଏକ ରେକର୍ଡ ହୋଇଥିବା ଟେଷ୍ଟ ସଫା କରନ୍ତି ଏବଂ ଏକ search ଟେଷ୍ଟ ଲେଖନ୍ତି, ତାପରେ ନିଜ ଭାଷାରେ practice shop ଉପରେ ଚଳାନ୍ତି।',
        'في المختبرات تنظّف اختبارًا مسجّلًا وتكتب اختبار بحث، ثم تشغّلهما على متجر التدريب بلغتك.',
        'In den Labs räumst du einen aufgenommenen Test auf und schreibst einen Suchtest, dann führst du beide in deiner Sprache gegen den Übungsshop aus.'),
]

QUIZ = [
    quiz(1, 'Which command creates a new JavaScript or TypeScript Playwright project?', ['npm install playwright', 'npm init playwright@latest', 'npx create-react-app', 'playwright new'], 1,
         'It asks four questions.', '<code>npm init playwright@latest</code> creates the config, a tests folder, an example test and optionally a GitHub Actions workflow.'),
    quiz(1, 'In Python, which package gives you the page fixture for pytest?', ['playwright-pytest', 'pytest-playwright', 'pytest-browser', 'selenium'], 1,
         'The plugin name starts with pytest.', '<code>pytest-playwright</code> installs Playwright and adds fixtures such as <code>page</code>, <code>context</code> and <code>browser</code>.'),
    quiz(1, 'What does playwright install --with-deps add on Linux?', ['Node.js', 'The operating system libraries the browsers need', 'Java', 'VS Code'], 1,
         'deps means dependencies.', 'It installs the browsers and the system libraries such as fonts and graphics libraries that the browsers need.'),
    quiz(1, 'Which file name will Playwright Test pick up as a test file?', ['login.ts', 'login.spec.ts', 'spec-login.ts', 'login.test.txt'], 1,
         'Look at the starter test.', 'By default Playwright Test runs files ending in <code>.spec</code> or <code>.test</code> with a JavaScript or TypeScript extension.'),
    quiz(2, 'Codegen wrote <code>click()</code> and then <code>fill()</code> on the same box. Why can you delete the click?', ['click is slower', 'fill focuses the box by itself', 'click is not allowed', 'fill clicks twice'], 1,
         'What does fill do first?', '<code>fill</code> waits for the box, focuses it and types the value, so a click before it adds nothing.'),
    quiz(2, 'How do you run only the tests whose names contain sign_in with pytest?', ['pytest -g sign_in', 'pytest -k sign_in', 'pytest --only sign_in', 'pytest sign_in'], 1,
         'pytest uses one letter for keyword expressions.', '<code>-k</code> selects tests by a keyword expression on their names.'),
    quiz(2, 'How do you run the Java test method signIn in class ShopTest with Maven?', ['mvn test -k signIn', 'mvn test -Dtest="ShopTest#signIn"', 'mvn signIn', 'mvn test --grep signIn'], 1,
         'Surefire reads a system property.', 'Maven Surefire takes <code>-Dtest=Class#method</code>.'),
    quiz(2, 'You updated Playwright and now tests fail saying the browser executable does not exist. What is missing?', ['A reboot', 'Installing the browsers for the new version', 'A new config file', 'Java 21'], 1,
         'Each version expects its own browser builds.', 'Run the install command again after every update so the matching browser builds are downloaded.'),
    quiz(2, 'Which target makes codegen write pytest code?', ['python', 'python-async', 'python-pytest', 'pytest'], 2,
         'The list of targets is in codegen --help.', '<code>--target python-pytest</code> writes a pytest test. <code>python</code> writes a plain script.'),
    quiz(3, 'Since version 1.57, what does Playwright run when you ask for headless Chromium?', ['Full Chromium', 'Chrome Headless Shell', 'Firefox', 'Edge'], 1,
         'Look at the dry run output.', 'Playwright now uses Chrome for Testing builds. Headed runs use chrome and headless runs use the smaller chrome-headless-shell.'),
    quiz(3, 'Why pin exact versions such as playwright==1.63.0?', ['It is faster', 'Every machine and the CI server run the same version, and updates become visible changes', 'pip needs it', 'It downloads fewer browsers'], 1,
         'Think about a teammate installing a month later.', 'Without a pin, a fresh install can bring a newer version than yours, and the suite behaves differently on different machines.'),
    quiz(3, 'Which environment variable tells Playwright where browsers are installed?', ['PW_HOME', 'PLAYWRIGHT_BROWSERS_PATH', 'BROWSER_DIR', 'PWDEBUG'], 1,
         'It appears in the dry run explanation.', '<code>PLAYWRIGHT_BROWSERS_PATH</code> overrides the default cache folder. <code>PWDEBUG</code> turns on the Inspector.'),
]

CALC = [
    calc(1, 'A suite has 2 tests and the scaffolded config has 3 browser projects. How many test runs does npx playwright test make?', 6, '2 × 3', ['2 tests × 3 projects', '= 6 runs']),
    calc(1, 'pytest found 2 tests and -k selected 1. How many were deselected?', 1, '2 minus 1', ['2 collected', '1 selected', '2 - 1 = 1 deselected']),
    calc(2, 'Chromium, Firefox and WebKit together download about 450 MB. A CI job installs them on every run, 40 runs a day. About how many GB a day is that?', 18,
         '450 × 40, then divide by 1000', ['450 MB × 40 = 18000 MB', '18000 ÷ 1000 = 18 GB a day, which is why CI images and caches matter']),
    calc(2, 'Recording a test with codegen took 4 minutes and cleaning it up took 6. Writing it by hand would take 25 minutes. How many minutes did codegen save?', 15,
         '25 minus the total of the two', ['4 + 6 = 10 minutes', '25 - 10 = 15 minutes saved']),
    calc(2, 'Playwright releases about one minor version a month. A team that never updates is how many versions behind after 2 years?', 24, '12 a year', ['12 × 2 = 24 versions behind']),
    calc(3, 'The codegen recording has 6 lines in the test body. Clean up removes the 2 extra clicks and adds 1 check. How many lines are left?', 5,
         '6 minus 2 plus 1', ['6 - 2 = 4', '4 + 1 = 5 lines']),
    calc(3, 'A team of 8 testers each loses 15 minutes a week to a missing install step in the README. How many hours a month (4 weeks) is that?', 8,
         '8 × 15 × 4 minutes, then divide by 60', ['8 × 15 = 120 minutes a week', '120 × 4 = 480 minutes', '480 ÷ 60 = 8 hours']),
    calc(3, 'A config sets 4 workers and the suite has 20 tests of equal length, 30 seconds each. About how many seconds does the run take?', 150,
         '20 tests share 4 workers', ['20 ÷ 4 = 5 tests per worker', '5 × 30 s = 150 s']),
]

LABS = [
    {'id': 'cleanup', 'title': 'Clean up a recorded test', 'name': 'a customer can sign in',
     'task': 'This is the code codegen recorded. Remove the two extra <code>click()</code> lines, use the relative address <code>/login</code> and add a check that <b>Hello, Asha</b> is visible.',
     'goal': 'The recorded test is cleaned up and ends with a check.', 'start': '/login',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('http://localhost:4173/login');
  await page.getByRole('textbox', { name: 'Email' }).click();
  await page.getByRole('textbox', { name: 'Email' }).fill('asha@shop.example');
  await page.getByRole('textbox', { name: 'Password' }).click();
  await page.getByRole('textbox', { name: 'Password' }).fill('s3cret');
  await page.getByRole('button', { name: 'Sign in' }).click();
});'''},
     'answer': {'ts': CLEAN_TS},
     'hint': '<code>fill</code> focuses the box by itself, so the clicks on the text boxes can go. End with <code>expect(page.getByText(\'Hello, Asha\')).toBeVisible()</code>.',
     'why': 'A recorded test is a draft. A good test has a clear name, uses the base URL so it can run against any environment, and ends with a check.',
     'check': [['ctx.loggedIn', 'Asha is signed in'], ["!/textbox[^\\n]*\\.click\\(/.test(ctx.code)", 'No extra clicks on the text boxes'], ["/Hello, Asha/.test(ctx.code)", 'The test checks the greeting']]},
    {'id': 'search', 'title': 'Search for a product', 'name': 'search finds the mug',
     'task': 'Open <code>/products</code>, type <b>mug</b> into the box with the placeholder <b>Search products</b>, and check that <b>Coffee mug</b> is visible and <b>Gel pen</b> is not.',
     'goal': 'The search shows the mug and hides the pen.', 'start': '/products',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('search finds the mug', async ({ page }) => {
  await page.goto('/products');
  // type into the search box, then check what is shown
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('search finds the mug', async ({ page }) => {
  await page.goto('/products');
  await page.getByPlaceholder('Search products').fill('mug');
  await expect(page.getByText('Coffee mug')).toBeVisible();
  await expect(page.getByText('Gel pen')).toBeHidden();
});'''},
     'hint': 'Use <code>getByPlaceholder</code> for the search box. To check that something is gone, use <code>toBeHidden()</code>.',
     'why': 'Checking what disappears is as important as checking what appears. A search that shows everything would pass the first check but fail the second.',
     'check': [["ctx.url.includes('/products')", 'The test opened the products page'], ["/[Hh]idden|isHidden|not_to_be_visible|ToBeHiddenAsync/.test(ctx.code)", 'The test checks that the pen is hidden']]},
]

T = {
    'slug': 'pw-setup', 'title': 'Installing Playwright and your first project', 'short': 'Install and set up', 'emoji': '🧰', 'module': MODULE, 'minutes': 18,
    'lead': 'Install Playwright in Java, Python, JavaScript and TypeScript, walk through the files of a new project, record a test with codegen and run tests from the terminal like you will every day at work.',
    'desc': 'Requirements, installing Playwright with Maven, pip and npm, browser downloads, the files of a new project, codegen with real screenshots, running and filtering tests, editors and safe updates.',
    'summary': 'Runtime and operating system requirements, installing with Maven, pip and npm init playwright, checking the version, where browsers are installed and Chrome for Testing, the real files of a scaffolded project and typical Python and Java layouts, codegen with real screenshots and the recorded code in four languages, cleaning up recorded code, running, filtering and listing tests, editors and updating safely.',
    'keywords': ['install', 'setup', 'npm init playwright', 'pytest-playwright', 'maven', 'playwright install', 'codegen', 'inspector', 'cli', 'vs code', 'project structure'],
    'plain': 'To start, you install your language, then the Playwright package, then the browsers it uses. Codegen can write a first test for you while you click around.',
    'parts': PARTS, 'codes': CODES, 'trees': TREES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
