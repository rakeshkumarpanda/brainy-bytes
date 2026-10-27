from pkit import part, say, quiz, calc, panel, four, one, js, ts, py, jv, table, tip, by, figure

MODULE = ('🔍', 'Debugging and quality', 'pw-quality', 'Finding out why a test failed with errors, traces, reports, UI mode and the Inspector, then checking how pages look, read and behave on every device.')

JAVA_TRIM = [(r'(?ms)^\tat .*?(?=^\[INFO\]|^\[ERROR\]|^\[WARNING\]|^Run \d|^[a-z]|\Z)', ''), (r'(?m)^\[ERROR\] (Please refer|To see the full|Re-run Maven|For more information|-> \[Help|\s*$).*\n?', ''),
             (r'(?m)^\[ERROR\] Failed to execute goal.*\n', ''), (r'(?ms)^\[INFO\] \n\[INFO\] Results:.*?(?=^\[ERROR\] Tests run:|^\[WARNING\] Tests run:)', '')]

# ---------- 1. a failure to read: the greeting has no exclamation mark ----------
ERR_TS = '''import { test, expect } from '@playwright/test';

test('greets Asha after sign in', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('s3cret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.locator('#hello')).toHaveText('Hello, Asha!');   // the page says Hello, Asha
});'''

ERR_PY = '''from playwright.sync_api import Page, expect


def test_greets_asha_after_sign_in(page: Page):
    page.goto("/login")
    page.get_by_label("Email").fill("asha@shop.example")
    page.get_by_label("Password").fill("s3cret")
    page.get_by_role("button", name="Sign in").click()
    expect(page.locator("#hello")).to_have_text("Hello, Asha!")   # the page says Hello, Asha'''

ERR_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class GreetingTest {
  @Test
  void greetsAshaAfterSignIn(Page page) {
    page.navigate("/login");
    page.getByLabel("Email").fill("asha@shop.example");
    page.getByLabel("Password").fill("s3cret");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in")).click();
    assertThat(page.locator("#hello")).hasText("Hello, Asha!");   // the page says Hello, Asha
  }
}'''

# ---------- 2. evidence on failure: screenshot, video and trace ----------
ART_CONFIG = '''import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  reporter: 'list',
  use: {
    baseURL: 'http://localhost:4173',
    screenshot: 'only-on-failure',   // a picture of the page when a test fails
    video: 'retain-on-failure',      // a video of every test, kept only when it fails
    trace: 'retain-on-failure',      // a trace of every test, kept only when it fails
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});'''

ART_TS = '''import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('s3cret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('listitem')).toHaveCount(5);
});

test('add the lamp to the cart', async ({ page }) => {
  await page.getByTestId('product-3').getByRole('button', { name: 'Add to cart' }).click();
  await expect(page.getByTestId('cart-count')).toHaveText('1');
});

test('add the notebook to the cart', async ({ page }) => {
  // the Notebook is out of stock, so this button never appears
  await page.getByTestId('product-4').getByRole('button', { name: 'Add to cart' }).click({ timeout: 3000 });
});'''

ART_INI = '''[pytest]
addopts = --base-url http://localhost:4173 --screenshot only-on-failure --video retain-on-failure --tracing retain-on-failure'''

ART_PY = '''import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True)
def signed_in(page: Page):
    page.goto("/login")
    page.get_by_label("Email").fill("asha@shop.example")
    page.get_by_label("Password").fill("s3cret")
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_role("listitem")).to_have_count(5)


def test_add_the_lamp_to_the_cart(page: Page):
    page.get_by_test_id("product-3").get_by_role("button", name="Add to cart").click()
    expect(page.get_by_test_id("cart-count")).to_have_text("1")


def test_add_the_notebook_to_the_cart(page: Page):
    # the Notebook is out of stock, so this button never appears
    page.get_by_test_id("product-4").get_by_role("button", name="Add to cart").click(timeout=3000)'''

ART_OPTIONS_JAVA = '''package com.brainy;

import com.microsoft.playwright.Browser;
import com.microsoft.playwright.junit.Options;
import com.microsoft.playwright.junit.OptionsFactory;

import java.nio.file.Paths;

public class EvidenceOptions implements OptionsFactory {
  @Override
  public Options getOptions() {
    return new Options()
        .setHeadless(true)
        .setBaseUrl("http://localhost:4173")
        .setTrace(Options.Trace.RETAIN_ON_FAILURE)          // keep the trace only when a test fails
        .setOutputDir(Paths.get("test-results"))
        .setContextOptions(new Browser.NewContextOptions()
            .setRecordVideoDir(Paths.get("videos")));       // a video of every test
  }
}'''

ART_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(EvidenceOptions.class)
public class CartTest {
  @BeforeEach
  void signIn(Page page) {
    page.navigate("/login");
    page.getByLabel("Email").fill("asha@shop.example");
    page.getByLabel("Password").fill("s3cret");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in")).click();
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(5);
  }

  @Test
  void addTheLampToTheCart(Page page) {
    page.getByTestId("product-3").getByRole(AriaRole.BUTTON, new Locator.GetByRoleOptions().setName("Add to cart")).click();
    assertThat(page.getByTestId("cart-count")).hasText("1");
  }

  @Test
  void addTheNotebookToTheCart(Page page) {
    // the Notebook is out of stock, so this button never appears
    page.getByTestId("product-4").getByRole(AriaRole.BUTTON, new Locator.GetByRoleOptions().setName("Add to cart"))
        .click(new Locator.ClickOptions().setTimeout(3000));
  }
}'''

# ---------- 3. a trace by hand, with named groups of steps ----------
STEP_CONFIG = ART_CONFIG.replace('''    screenshot: 'only-on-failure',   // a picture of the page when a test fails
    video: 'retain-on-failure',      // a video of every test, kept only when it fails
    trace: 'retain-on-failure',      // a trace of every test, kept only when it fails''', '''    trace: 'on',                     // a trace for every test, passed or failed''')

STEP_TS = '''import { test, expect } from '@playwright/test';

test('buy a mug', async ({ page }) => {
  await test.step('sign in', async () => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('asha@shop.example');
    await page.getByLabel('Password').fill('s3cret');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page.locator('#hello')).toHaveText('Hello, Asha');
  });
  await test.step('add the mug', async () => {
    await page.getByTestId('product-2').getByRole('button', { name: 'Add to cart' }).click();
    await expect(page.getByTestId('cart-count')).toHaveText('1');
  });
});'''

STEP_PY = '''from playwright.sync_api import BrowserContext, Page, expect


def test_buy_a_mug(context: BrowserContext, page: Page):
    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    context.tracing.group("sign in")
    page.goto("/login")
    page.get_by_label("Email").fill("asha@shop.example")
    page.get_by_label("Password").fill("s3cret")
    page.get_by_role("button", name="Sign in").click()
    expect(page.locator("#hello")).to_have_text("Hello, Asha")
    context.tracing.group_end()

    context.tracing.group("add the mug")
    page.get_by_test_id("product-2").get_by_role("button", name="Add to cart").click()
    expect(page.get_by_test_id("cart-count")).to_have_text("1")
    context.tracing.group_end()

    context.tracing.stop(path="traces/buy-a-mug.zip")'''

STEP_JAVA = '''package com.brainy;

import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Tracing;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import java.nio.file.Paths;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class MugTest {
  @Test
  void buyAMug(BrowserContext context, Page page) {
    context.tracing().start(new Tracing.StartOptions().setScreenshots(true).setSnapshots(true));

    context.tracing().group("sign in");
    page.navigate("/login");
    page.getByLabel("Email").fill("asha@shop.example");
    page.getByLabel("Password").fill("s3cret");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in")).click();
    assertThat(page.locator("#hello")).hasText("Hello, Asha");
    context.tracing().groupEnd();

    context.tracing().group("add the mug");
    page.getByTestId("product-2").getByRole(AriaRole.BUTTON, new Locator.GetByRoleOptions().setName("Add to cart")).click();
    assertThat(page.getByTestId("cart-count")).hasText("1");
    context.tracing().groupEnd();

    context.tracing().stop(new Tracing.StopOptions().setPath(Paths.get("traces/buy-a-mug.zip")));
  }
}'''

# ---------- 4. verbose logs: every Playwright call with its timing ----------
LOG_TS = '''import { test, expect } from '@playwright/test';

test('find the lamp', async ({ page }) => {
  await page.goto('/products');
  await page.getByPlaceholder('Search products').fill('lamp');
  await expect(page.getByRole('listitem')).toHaveCount(1);
});'''

LOG_PY = '''from playwright.sync_api import Page, expect


def test_find_the_lamp(page: Page):
    page.goto("/products")
    page.get_by_placeholder("Search products").fill("lamp")
    expect(page.get_by_role("listitem")).to_have_count(1)'''

LOG_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class LampTest {
  @Test
  void findTheLamp(Page page) {
    page.navigate("/products");
    page.getByPlaceholder("Search products").fill("lamp");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(1);
  }
}'''

PY_TRIM = [(r'(?ms)^tests/test_cart\.py:21: \n_ _ .*?(?=^E   )', ''), (r'(?m)^\.\./\.\./\.venv/\S+: TimeoutError$', 'tests/test_cart.py:21: TimeoutError')]
JAVA_STACK = [(r'(?m)^    at .*coreBundle.*\n', '')]

LOG_TRIM = [(r'(?m)^.*pw:api.*(?:waiting for|=> |navigated to|"(?:load|domcontentloaded|commit)" event).*\n', ''), (r'\d{4}-\d\d-\d\dT[\d:.]+Z ', '')]

CODES = {
    'error': four('A failed check, and what the runner prints',
                  java=jv({'GreetingTest.java': ERR_JAVA}, expect='fail', replace=JAVA_TRIM),
                  py=py({'test_greeting.py': ERR_PY}, expect='fail'),
                  js=js({'greeting.spec.js': ERR_TS}, expect='fail'),
                  ts=ts({'greeting.spec.ts': ERR_TS}, expect='fail'),
                  result='Every runner names the same four things: the locator it checked, the text it expected, the text it received and how long it kept trying. The difference is one exclamation mark. The call log underneath shows that the check found the element straight away and retried until the 5 s limit, so the element was there and only the text was wrong. Playwright Test also prints the source line with a marker under the failing call.'),
    'evidence': four('A screenshot, a video and a trace when a test fails',
                     java=jv({'CartTest.java': ART_JAVA, 'EvidenceOptions.java': ART_OPTIONS_JAVA}, expect='fail', replace=JAVA_TRIM + JAVA_STACK,
                             cmd='mvn test ; s=$?; find test-results videos -type f | sort; exit $s', shown_cmd='mvn test ; find test-results videos -type f | sort',
                             show=['src/test/java/com/brainy/EvidenceOptions.java', 'src/test/java/com/brainy/CartTest.java']),
                     py=py({'test_cart.py': ART_PY}, ini=ART_INI, expect='fail', replace=PY_TRIM,
                           cmd='pytest -v ; s=$?; find test-results -type f | sort; exit $s', shown_cmd='pytest -v ; find test-results -type f | sort',
                           show=['pytest.ini', 'tests/test_cart.py']),
                     js=js({'cart.spec.js': ART_TS}, config=ART_CONFIG, expect='fail',
                           cmd='npx playwright test ; s=$?; find test-results -type f | sort; exit $s', shown_cmd='npx playwright test ; find test-results -type f | sort',
                           show=['playwright.config.js', 'tests/cart.spec.js']),
                     ts=ts({'cart.spec.ts': ART_TS}, config=ART_CONFIG, expect='fail',
                           cmd='npx playwright test ; s=$?; find test-results -type f | sort; exit $s', shown_cmd='npx playwright test ; find test-results -type f | sort',
                           show=['playwright.config.ts', 'tests/cart.spec.ts']),
                     result='The lamp test passed and left nothing behind. The notebook test failed, and its folder holds the evidence: a screenshot of the page at the moment of failure, a video of the whole test and a trace.zip to open in the trace viewer. pytest-playwright has the same three options as command line flags, so they sit in pytest.ini. The JUnit fixture keeps traces with setTrace, and records a video of every test, passed or failed, into the folder set by setRecordVideoDir. It has no screenshot on failure option.'),
    'steps': four('A trace with named steps',
                  java=jv({'MugTest.java': STEP_JAVA}, cmd='mvn test && ls -1 traces', shown_cmd='mvn test && ls traces'),
                  py=py({'test_mug.py': STEP_PY}, cmd='pytest -v && ls traces'),
                  js=js({'mug.spec.js': STEP_TS}, config=STEP_CONFIG, cmd='npx playwright test && find test-results -name trace.zip'),
                  ts=ts({'mug.spec.ts': STEP_TS}, config=STEP_CONFIG, cmd='npx playwright test && find test-results -name trace.zip'),
                  result='Each language saved a trace in which the actions sit under two names, sign in and add the mug, so a long test reads like a short list. Playwright Test does this with test.step, and the same steps also show up in the HTML report. In Python and Java the test starts and stops the trace itself with context.tracing, and tracing.group names the steps. Open any of the files with show-trace.'),
    'logs': four('Every Playwright call, written to the terminal',
                 java=jv({'LampTest.java': LOG_JAVA}, cmd='DEBUG=pw:api mvn -o -B -Dstyle.color=never test', shown_cmd='DEBUG=pw:api mvn test', replace=JAVA_TRIM + LOG_TRIM),
                 py=py({'test_lamp.py': LOG_PY}, cmd='DEBUG=pw:api pytest -s', replace=LOG_TRIM),
                 js=js({'lamp.spec.js': LOG_TS}, cmd='DEBUG=pw:api npx playwright test', replace=LOG_TRIM),
                 ts=ts({'lamp.spec.ts': LOG_TS}, cmd='DEBUG=pw:api npx playwright test', replace=LOG_TRIM),
                 result='With DEBUG=pw:api, Playwright writes a line for each step inside every call: the navigation, the element a locator found, the fill and the check. In JavaScript and TypeScript the client adds a line when each call ends, with the time since the line before, so you can see where the test spent its time. Python and Java run the same driver, so they print the same steps. The full log also has a line for every wait inside a call, which we cut here to keep it short.'),
}

DG = {
    'loop': {'t': 'From a red test to a fix', 'w': 900, 'h': 240,
             'n': [['fail', 20, 88, 130, 64, 'test fails', {'c': 5, 'sub': 'in CI or locally', 'i': 'A test fails, usually on a CI machine you cannot watch.'}],
                   ['err', 190, 88, 140, 64, 'read the error', {'c': 2, 'sub': 'expected, received', 'i': 'The error names the locator, the expected value, the received value and the call log.'}],
                   ['trace', 370, 16, 150, 64, 'open the trace', {'c': 1, 'sub': 'DOM, network, console', 'i': 'The trace shows the page before and after every action, with the network and the console.'}],
                   ['shot', 370, 160, 150, 64, 'screenshot, video', {'c': 1, 'sub': 'what the page showed', 'i': 'The screenshot and the video show what a user would have seen.'}],
                   ['debug', 560, 88, 150, 64, 'run it locally', {'c': 3, 'sub': 'Inspector or UI mode', 'i': 'Run the one test with the Inspector or UI mode and step through it.'}],
                   ['fix', 750, 88, 130, 64, 'fix and rerun', {'c': 0, 'sub': 'test or app', 'i': 'Fix the test or report the bug in the app, then run the test again.'}]],
             'e': [['fail', 'err'], ['err', 'trace'], ['err', 'shot'], ['trace', 'debug'], ['shot', 'debug'], ['debug', 'fix']],
             'st': [[['fail'], 'A test fails.'],
                    [['err', 'fail>err'], 'Read the error first. It often names the cause.'],
                    [['trace', 'shot', 'err>trace', 'err>shot'], 'Then look at the evidence: the trace, the screenshot and the video.'],
                    [['debug', 'trace>debug', 'shot>debug'], 'If it is still not clear, run the one test locally and step through it.'],
                    [['fix', 'debug>fix'], 'Fix the test or the app, and run it again.']]},
}

PARTS = [
    part('errors', '📜', 'Read the error first', f'''
<p>Most failures explain themselves. Before you open any tool, read what the runner printed. A Playwright error has four parts, and you will find them in every language.</p>
{table(['Part', 'What it tells you'], [
    ['the locator', 'which element the check or action looked for'],
    ['expected and received', 'what the test wanted and what the page had, side by side'],
    ['the timeout', 'how long Playwright kept trying before it gave up'],
    ['the call log', 'each try: did the locator find an element, was it visible, enabled and stable, what did it contain'],
])}
[[error]]
{table(['The error says', 'It usually means'], [
    ['received a different text or count', 'the page changed, or the expected value in the test is out of date'],
    ['element(s) not found, or waiting for locator', 'the locator is wrong, a step before it did not happen, or the page did not load'],
    ['strict mode violation, resolved to 2 elements', 'the locator is too loose, so narrow it with a role, a name or a parent'],
    ['element is not enabled, or is not visible', 'the app has not finished something, such as loading data or validating a form'],
    ['Test timeout of 30000ms exceeded', 'one call waited for something that never happened, and the call log names it'],
])}
{tip('Read the received value carefully. A missing full stop, an extra space or a different currency sign is the most common cause of a red check, and the error shows it to you directly.', 'tip')}
''', easy=True, kw=['error message', 'expected', 'received', 'call log', 'strict mode violation', 'timeout exceeded', 'failure']),

    part('evidence', '📸', 'Screenshots, videos and traces on failure', f'''
<p>A failure in CI happens on a machine you cannot watch. Turn on evidence so every failed test leaves behind what it saw. Keeping it only for failures saves disk space, because passing tests need none.</p>
[[evidence]]
{table(['Setting', 'Playwright Test', 'pytest-playwright', 'JUnit fixture'], [
    ['screenshot', "screenshot: 'only-on-failure'", '--screenshot only-on-failure', 'not built in, call page.screenshot() yourself'],
    ['video', "video: 'retain-on-failure'", '--video retain-on-failure', 'setRecordVideoDir(...), every test'],
    ['trace', "trace: 'retain-on-failure'", '--tracing retain-on-failure', 'setTrace(Options.Trace.RETAIN_ON_FAILURE)'],
    ['where', 'test-results/', 'test-results/', 'setOutputDir(...)'],
    ['other values', "'on', 'off', 'on-first-retry', 'retain-on-first-failure'", 'on, off', 'ON, OFF'],
])}
{tip("Teams often use trace: 'on-first-retry' in CI. A first run that fails is retried with tracing on, so the trace is recorded only for tests that failed at least once.", 'pro')}
''', kw=['screenshot only-on-failure', 'video retain-on-failure', 'trace retain-on-failure', 'on-first-retry', 'test-results', 'evidence']),

    part('trace', '🧭', 'The trace viewer', f'''
<p>A trace is a zip file with everything that happened in one test: each action, a copy of the page before and after it, the network calls, the console messages and the test source. The trace viewer plays it back. These screenshots come from the notebook test above.</p>
<div class="viz" data-viz="flow" data-k="loop"></div>
{figure('debug-trace-log.jpg', 'The trace viewer with the failed click selected, the page snapshot in the middle and the Log tab open below', 'The trace of the failed notebook test. The left side lists every action, with the failed click marked in red. The middle shows the page at that moment. The Log tab shows the click waiting 8.8 s for an Add to cart button in the Notebook card, while the snapshot shows that card has an Out of stock button instead.')}
{figure('debug-trace-network.jpg', 'The trace viewer with the Network tab open, listing the requests the page made', 'The Network tab lists every request the page made during the test, with its method, status, type and timing. Every request shown returned 200, so the page loaded fine and the button really was missing.')}
{table(['Open a trace', 'Command'], [
    ['JavaScript and TypeScript', 'npx playwright show-trace test-results/.../trace.zip'],
    ['Python', 'playwright show-trace test-results/.../trace.zip'],
    ['Java', 'mvn exec:java -e -D exec.mainClass=com.microsoft.playwright.CLI -D exec.args="show-trace trace.zip"'],
    ['any language, no install', 'drag the file onto trace.playwright.dev, which reads it in your browser'],
])}
[[steps]]
{tip('Inside the trace viewer, click an action and then use the Before and After tabs to compare the page. The Pick locator button lets you try a new locator on the saved page.', 'tip')}
''', kw=['trace viewer', 'trace.zip', 'show-trace', 'trace.playwright.dev', 'snapshots', 'test.step', 'tracing.group', 'tracing.start']),

    part('report', '📊', 'The HTML report and UI mode', f'''
<p>Playwright Test writes an HTML report with every test, its steps, its errors and its evidence. It opens by itself after a failed local run, and <code>npx playwright show-report</code> opens it any time.</p>
{figure('report-html-list.jpg', 'The Playwright HTML report listing two tests, one passed and one failed', 'The HTML report for the cart tests: one passed and one failed, with filters for each result at the top.')}
{figure('report-html-failed.jpg', 'The failed test in the HTML report, with the error, the screenshot and the trace link', 'Click the failed test to see its error with the source line, each step with its time, and a View Trace button. The screenshot taken at failure is further down the same page.')}
<p><b>UI mode</b> is a window for running and watching tests. You pick tests from a tree, run them, and step through each action with the same views as the trace viewer. It can also rerun tests when you save a file. Start it with <code>npx playwright test --ui</code>.</p>
{figure('debug-ui-mode.jpg', 'Playwright UI mode with the test tree on the left and the failed notebook test open on the right', 'UI mode after running both tests. The failed test is open, with its actions, the page snapshot and the error.')}
{tip('UI mode, the HTML report and the VS Code extension are part of Playwright Test, so they are there for JavaScript and TypeScript. Python teams usually add pytest-html, and Java teams add Allure or ExtentReports. The reporting chapter builds each of them.', 'warn')}
''', kw=['HTML report', 'show-report', 'UI mode', '--ui', 'watch mode', 'VS Code extension']),

    part('inspector', '🕵️', 'Step through a test with the Inspector', f'''
<p>When the evidence is not enough, run the test yourself and stop it at the line that fails. In debug mode Playwright opens a real browser and the <b>Inspector</b>, which shows the test source, highlights the current line and lets you step one action at a time. Debug mode also turns off timeouts, so you can take as long as you need.</p>
{figure('debug-inspector.jpg', 'A headed browser on the products page next to the Playwright Inspector paused at page.pause()', 'A test stopped at page.pause() on line 8. The Inspector on the right highlights that line and lists the finished steps in its Log tab. The browser on the left marks the five list items the last locator found.')}
{table(['', 'JavaScript and TypeScript', 'Python', 'Java'], [
    ['open the Inspector', 'npx playwright test --debug', 'PWDEBUG=1 pytest -s', 'PWDEBUG=1 mvn test'],
    ['one test only', 'npx playwright test cart.spec.ts:12 --debug', 'PWDEBUG=1 pytest -s -k notebook', 'PWDEBUG=1 mvn test -Dtest=CartTest#addTheNotebookToTheCart'],
    ['stop at a line', 'await page.pause()', 'page.pause()', 'page.pause()'],
    ['see the source', 'shown by itself', 'shown by itself', 'PLAYWRIGHT_JAVA_SRC=src/test/java'],
    ['watch slowly', 'launchOptions: { slowMo: 500 }', '--headed --slowmo 500', 'setLaunchOptions(...setSlowMo(500))'],
])}
<p>Next to the toolbar is the locator field. Type a locator there and the matching elements light up in the browser, which is the quickest way to fix a locator that finds nothing or finds too much.</p>
{tip('Remove page.pause() before you commit. It needs a headed browser and is only useful while you debug.', 'warn')}
''', kw=['Inspector', 'PWDEBUG', '--debug', 'page.pause', 'step over', 'slowMo', 'headed', 'PLAYWRIGHT_JAVA_SRC']),

    part('logs', '🧾', 'Verbose logs', f'''
<p>On a CI machine there is no window to open. The <code>DEBUG</code> environment variable makes Playwright print what every call does, in any language, so the CI log shows the last thing a stuck test was doing.</p>
[[logs]]
{table(['Variable', 'What it prints'], [
    ['DEBUG=pw:api', 'every Playwright call and the steps inside it'],
    ['DEBUG=pw:browser', 'what the browser process prints, useful when it will not start'],
    ['DEBUG=pw:protocol', 'every message between Playwright and the browser, very long'],
    ['PWDEBUG=console', 'a playwright object in the browser DevTools, to try locators in the console'],
])}
{tip('Browser console messages and page errors are a different stream. Collect them with page.on("console") and page.on("pageerror"), as the fixtures chapter does, or read them in the Console tab of the trace.', 'tip')}
''', kw=['DEBUG=pw:api', 'verbose logs', 'pw:browser', 'pw:protocol', 'PWDEBUG=console', 'CI logs']),
]

INFO = {'title': 'Find the cause, not a workaround', 'panels': [
    panel([['e', '📜'], ['t', 'error', {'b': 1}]], 'Error', 'Expected and received.', 'Read it first.'),
    panel([['e', '📸'], ['t', 'evidence', {'b': 1}]], 'Evidence', 'Screenshot, video, trace.', 'Kept on failure.'),
    panel([['e', '🧭'], ['t', 'trace', {'b': 1}]], 'Trace', 'Every action replayed.', 'DOM, network, console.'),
    panel([['e', '🕵️'], ['t', 'Inspector', {'b': 1}]], 'Inspector', 'Run it yourself.', 'One step at a time.')],
    'remember': 'Read the error, then the trace, and only then run the test by hand. Most failures are solved at the first step.'}

REAL = [
    ['🌙', 'The test that failed only at night', 'A nightly run fails on a test that always passes during the day. The trace shows a maintenance banner covering the button. The team adds a check for the banner and the mystery is gone.'],
    ['🧾', 'A trace attached to every bug', 'A QA team attaches the trace.zip of the failed test to each bug report. Developers open it on trace.playwright.dev and see the exact page, request and response without setting anything up.'],
    ['🐢', 'Where did the minute go', 'A checkout test takes over a minute. One run with DEBUG=pw:api shows a single navigation waiting 40 seconds for the load event because of a slow chat widget. Waiting for the page content instead fixes it.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter is about finding out why a test failed. You read the error, keep a screenshot, a video and a trace for every failure, replay the trace, look at the HTML report and UI mode, and step through a test in the Inspector.',
        'यह अध्याय यह जानने के बारे में है कि test क्यों fail हुआ। आप error पढ़ते हैं, हर failure के लिए screenshot, video और trace रखते हैं, trace को दोबारा चलाते हैं, HTML report और UI mode देखते हैं, और Inspector में test को कदम दर कदम चलाते हैं।',
        'ಈ ಅಧ್ಯಾಯ test ಏಕೆ fail ಆಯಿತು ಎಂದು ತಿಳಿಯುವುದರ ಬಗ್ಗೆ. ನೀವು error ಓದುತ್ತೀರಿ, ಪ್ರತಿ failure ಗೆ screenshot, video ಮತ್ತು trace ಇಡುತ್ತೀರಿ, trace ಅನ್ನು ಮತ್ತೆ ನೋಡುತ್ತೀರಿ, HTML report ಮತ್ತು UI mode ನೋಡುತ್ತೀರಿ, Inspector ನಲ್ಲಿ test ಅನ್ನು ಹೆಜ್ಜೆ ಹೆಜ್ಜೆಯಾಗಿ ನಡೆಸುತ್ತೀರಿ.',
        'ଏହି ଅଧ୍ୟାୟ test କାହିଁକି fail ହେଲା ଜାଣିବା ବିଷୟରେ। ଆପଣ error ପଢନ୍ତି, ପ୍ରତି failure ପାଇଁ screenshot, video ଓ trace ରଖନ୍ତି, trace କୁ ପୁଣି ଦେଖନ୍ତି, HTML report ଓ UI mode ଦେଖନ୍ତି, ଏବଂ Inspector ରେ test କୁ ପାଦେ ପାଦେ ଚଳାନ୍ତି।',
        'يدور هذا الفصل حول معرفة سبب فشل الاختبار. تقرأ رسالة الخطأ، وتحتفظ بلقطة شاشة وفيديو وأثر لكل فشل، وتعيد تشغيل الأثر، وتنظر في تقرير HTML ووضع UI، وتتقدم في الاختبار خطوة بخطوة داخل Inspector.',
        'In diesem Kapitel geht es darum, herauszufinden, warum ein Test fehlgeschlagen ist. Du liest die Fehlermeldung, behältst für jeden Fehler einen Screenshot, ein Video und einen Trace, spielst den Trace ab, schaust dir den HTML-Bericht und den UI-Modus an und gehst im Inspector Schritt für Schritt durch einen Test.'),
    say('errors', 'The error', 'A Playwright error names the locator, the expected value, the received value, the timeout and a call log of every try. Compare expected and received first, because the cause is often right there.',
        'Playwright error में locator, expected value, received value, timeout और हर कोशिश का call log होता है। पहले expected और received की तुलना करें, क्योंकि कारण अक्सर वहीं होता है।',
        'Playwright error ನಲ್ಲಿ locator, expected value, received value, timeout ಮತ್ತು ಪ್ರತಿ ಪ್ರಯತ್ನದ call log ಇರುತ್ತದೆ. ಮೊದಲು expected ಮತ್ತು received ಹೋಲಿಸಿ, ಏಕೆಂದರೆ ಕಾರಣ ಹೆಚ್ಚಾಗಿ ಅಲ್ಲೇ ಇರುತ್ತದೆ.',
        'Playwright error ରେ locator, expected value, received value, timeout ଓ ପ୍ରତି ଚେଷ୍ଟାର call log ଥାଏ। ପ୍ରଥମେ expected ଓ received ତୁଳନା କରନ୍ତୁ, କାରଣ କାରଣଟି ପ୍ରାୟତଃ ସେଠାରେ ଥାଏ।',
        'يذكر خطأ Playwright المحدد والقيمة المتوقعة والقيمة المستلمة والمهلة وسجل كل محاولة. قارن المتوقع بالمستلم أولًا، فالسبب غالبًا هناك.',
        'Ein Playwright-Fehler nennt den Locator, den erwarteten Wert, den erhaltenen Wert, das Timeout und ein Protokoll jedes Versuchs. Vergleiche zuerst erwartet und erhalten, denn dort liegt oft schon die Ursache.'),
    say('evidence', 'Evidence on failure', 'Turn on a screenshot, a video and a trace that are kept only when a test fails. Playwright Test and pytest-playwright have all three as settings. The JUnit fixture keeps traces and records videos.',
        'ऐसा screenshot, video और trace चालू करें जो केवल test fail होने पर रखा जाए। Playwright Test और pytest-playwright में तीनों settings हैं। JUnit fixture traces रखता है और videos record करता है।',
        'Test fail ಆದಾಗ ಮಾತ್ರ ಉಳಿಯುವ screenshot, video ಮತ್ತು trace ಆನ್ ಮಾಡಿ. Playwright Test ಮತ್ತು pytest-playwright ನಲ್ಲಿ ಮೂರೂ settings ಇವೆ. JUnit fixture traces ಇಡುತ್ತದೆ ಮತ್ತು videos record ಮಾಡುತ್ತದೆ.',
        'କେବଳ test fail ହେଲେ ରହୁଥିବା screenshot, video ଓ trace ଚାଲୁ କରନ୍ତୁ। Playwright Test ଓ pytest-playwright ରେ ତିନୋଟି settings ଅଛି। JUnit fixture traces ରଖେ ଓ videos record କରେ।',
        'فعّل لقطة شاشة وفيديو وأثرًا لا تُحفظ إلا عند فشل الاختبار. في Playwright Test وpytest-playwright الثلاثة إعدادات جاهزة. ويحفظ مثبّت JUnit الآثار ويسجل الفيديو.',
        'Schalte einen Screenshot, ein Video und einen Trace ein, die nur bei einem Fehlschlag behalten werden. Playwright Test und pytest-playwright haben alle drei als Einstellung. Die JUnit-Fixture behält Traces und nimmt Videos auf.'),
    say('trace', 'The trace viewer', 'A trace holds every action, the page before and after it, the network, the console and the source. Open it with show-trace or on trace.playwright.dev. Named steps make long traces easy to read.',
        'Trace में हर action, उसके पहले और बाद का page, network, console और source होता है। इसे show-trace से या trace.playwright.dev पर खोलें। नाम वाले steps लंबे traces को पढ़ना आसान बनाते हैं।',
        'Trace ನಲ್ಲಿ ಪ್ರತಿ action, ಅದರ ಮೊದಲು ಮತ್ತು ನಂತರದ page, network, console ಮತ್ತು source ಇರುತ್ತವೆ. show-trace ಅಥವಾ trace.playwright.dev ನಲ್ಲಿ ತೆರೆಯಿರಿ. ಹೆಸರಿರುವ steps ಉದ್ದ traces ಓದಲು ಸುಲಭ ಮಾಡುತ್ತವೆ.',
        'Trace ରେ ପ୍ରତି action, ତା ପୂର୍ବ ଓ ପରର page, network, console ଓ source ଥାଏ। ଏହାକୁ show-trace ରେ ବା trace.playwright.dev ରେ ଖୋଲନ୍ତୁ। ନାମ ଥିବା steps ଲମ୍ବା traces ପଢିବା ସହଜ କରେ।',
        'يحتوي الأثر على كل فعل، والصفحة قبله وبعده، والشبكة، والطرفية، والمصدر. افتحه بالأمر show-trace أو على trace.playwright.dev. الخطوات المسماة تجعل الآثار الطويلة سهلة القراءة.',
        'Ein Trace enthält jede Aktion, die Seite davor und danach, das Netzwerk, die Konsole und den Quelltext. Öffne ihn mit show-trace oder auf trace.playwright.dev. Benannte Schritte machen lange Traces leicht lesbar.'),
    say('report', 'Report and UI mode', 'Playwright Test writes an HTML report with errors, screenshots, videos and traces. UI mode runs tests in a window and lets you step through each action. Both come with Playwright Test for JavaScript and TypeScript.',
        'Playwright Test errors, screenshots, videos और traces के साथ HTML report लिखता है। UI mode tests को window में चलाता है और हर action से गुज़रने देता है। दोनों JavaScript और TypeScript के Playwright Test के साथ आते हैं।',
        'Playwright Test errors, screenshots, videos ಮತ್ತು traces ಇರುವ HTML report ಬರೆಯುತ್ತದೆ. UI mode tests ಅನ್ನು window ನಲ್ಲಿ ನಡೆಸಿ ಪ್ರತಿ action ನೋಡಲು ಬಿಡುತ್ತದೆ. ಎರಡೂ JavaScript ಮತ್ತು TypeScript ನ Playwright Test ಜೊತೆ ಬರುತ್ತವೆ.',
        'Playwright Test errors, screenshots, videos ଓ traces ସହ HTML report ଲେଖେ। UI mode tests କୁ window ରେ ଚଳାଏ ଓ ପ୍ରତି action ଦେଖିବାକୁ ଦିଏ। ଦୁହେଁ JavaScript ଓ TypeScript ର Playwright Test ସହ ଆସନ୍ତି।',
        'يكتب Playwright Test تقرير HTML فيه الأخطاء ولقطات الشاشة والفيديو والآثار. ويشغّل وضع UI الاختبارات في نافذة ويتيح لك التنقل بين الأفعال. ويأتي الاثنان مع Playwright Test للغتي JavaScript وTypeScript.',
        'Playwright Test schreibt einen HTML-Bericht mit Fehlern, Screenshots, Videos und Traces. Der UI-Modus führt Tests in einem Fenster aus und lässt dich jede Aktion durchgehen. Beides gehört zu Playwright Test für JavaScript und TypeScript.'),
    say('inspector', 'The Inspector', 'Run with --debug in Playwright Test or PWDEBUG=1 in Python and Java. A browser and the Inspector open, and you step through the test. page.pause() stops it at the line you choose.',
        'Playwright Test में --debug या Python और Java में PWDEBUG=1 के साथ चलाएँ। Browser और Inspector खुलते हैं, और आप test को कदम दर कदम चलाते हैं। page.pause() उसे आपकी चुनी line पर रोकता है।',
        'Playwright Test ನಲ್ಲಿ --debug ಅಥವಾ Python ಮತ್ತು Java ನಲ್ಲಿ PWDEBUG=1 ಜೊತೆ ನಡೆಸಿ. Browser ಮತ್ತು Inspector ತೆರೆಯುತ್ತವೆ, ನೀವು test ಅನ್ನು ಹೆಜ್ಜೆ ಹೆಜ್ಜೆಯಾಗಿ ನಡೆಸುತ್ತೀರಿ. page.pause() ನೀವು ಆರಿಸಿದ line ನಲ್ಲಿ ನಿಲ್ಲಿಸುತ್ತದೆ.',
        'Playwright Test ରେ --debug ବା Python ଓ Java ରେ PWDEBUG=1 ସହ ଚଳାନ୍ତୁ। Browser ଓ Inspector ଖୋଲେ, ଏବଂ ଆପଣ test କୁ ପାଦେ ପାଦେ ଚଳାନ୍ତି। page.pause() ଆପଣ ବାଛିଥିବା line ରେ ଅଟକାଏ।',
        'شغّل مع ‎--debug في Playwright Test أو PWDEBUG=1 في Python وJava. يفتح متصفح ومعه Inspector، وتتقدم في الاختبار خطوة بخطوة. ويوقفه page.pause()‎ عند السطر الذي تختاره.',
        'Starte mit --debug in Playwright Test oder mit PWDEBUG=1 in Python und Java. Ein Browser und der Inspector öffnen sich, und du gehst Schritt für Schritt durch den Test. page.pause() hält ihn an der Zeile an, die du wählst.'),
    say('logs', 'Verbose logs', 'DEBUG=pw:api prints a line for each step of every Playwright call. It works in every language and is the way to see what a test was doing on a CI machine.',
        'DEBUG=pw:api हर Playwright call के हर कदम के लिए एक line छापता है। यह हर भाषा में काम करता है और CI machine पर test क्या कर रहा था यह देखने का तरीका है।',
        'DEBUG=pw:api ಪ್ರತಿ Playwright call ನ ಪ್ರತಿ ಹಂತಕ್ಕೆ ಒಂದು line ಮುದ್ರಿಸುತ್ತದೆ. ಇದು ಎಲ್ಲಾ ಭಾಷೆಗಳಲ್ಲಿ ಕೆಲಸ ಮಾಡುತ್ತದೆ, CI machine ನಲ್ಲಿ test ಏನು ಮಾಡುತ್ತಿತ್ತು ಎಂದು ನೋಡುವ ದಾರಿ.',
        'DEBUG=pw:api ପ୍ରତି Playwright call ର ପ୍ରତି ପଦକ୍ଷେପ ପାଇଁ ଏକ line ଛାପେ। ଏହା ସବୁ ଭାଷାରେ କାମ କରେ ଏବଂ CI machine ରେ test କଣ କରୁଥିଲା ଦେଖିବାର ଉପାୟ।',
        'يطبع DEBUG=pw:api سطرًا لكل خطوة داخل كل استدعاء في Playwright. يعمل في كل اللغات، وهو طريقتك لمعرفة ما كان الاختبار يفعله على جهاز CI.',
        'DEBUG=pw:api schreibt eine Zeile für jeden Schritt in jedem Playwright-Aufruf. Das funktioniert in jeder Sprache und zeigt, was ein Test auf einer CI-Maschine gerade getan hat.'),
    say('practice', 'Playground labs', 'In the labs you fix a check whose expected text is wrong, using the received value from the error, and you rewrite a test for an out of stock product so it checks what the page really shows.',
        'Labs में आप error की received value से उस check को ठीक करते हैं जिसका expected text गलत है, और out of stock product वाले test को फिर से लिखते हैं ताकि वह वही जाँचे जो page सच में दिखाता है।',
        'Labs ನಲ್ಲಿ error ನ received value ಬಳಸಿ ತಪ್ಪು expected text ಇರುವ check ಸರಿಪಡಿಸುತ್ತೀರಿ, ಮತ್ತು out of stock product ನ test ಅನ್ನು page ನಿಜವಾಗಿ ತೋರಿಸುವುದನ್ನು ಪರಿಶೀಲಿಸುವಂತೆ ಮತ್ತೆ ಬರೆಯುತ್ತೀರಿ.',
        'Labs ରେ error ର received value ବ୍ୟବହାର କରି ଭୁଲ expected text ଥିବା check ଠିକ କରନ୍ତି, ଏବଂ out of stock product ର test କୁ page ପ୍ରକୃତରେ ଦେଖାଉଥିବା ଜିନିଷ ଯାଞ୍ଚ କରିବା ପାଇଁ ପୁଣି ଲେଖନ୍ତି।',
        'في المختبرات تصلح فحصًا نصه المتوقع خاطئ مستعينًا بالقيمة المستلمة في الخطأ، وتعيد كتابة اختبار لمنتج نفد من المخزون كي يفحص ما تعرضه الصفحة فعلًا.',
        'In den Labs reparierst du eine Prüfung mit falschem erwartetem Text anhand des erhaltenen Werts aus der Fehlermeldung, und du schreibst einen Test für ein ausverkauftes Produkt so um, dass er prüft, was die Seite wirklich zeigt.'),
]

QUIZ = [
    quiz(1, 'What should you look at first when a test fails?', ['the video', 'the error message', 'the HTML source of the app', 'the CI settings'], 1,
         'It is printed right where the test failed.', 'The error names the locator, the expected and the received values, which often show the cause.'),
    quiz(1, "What does screenshot: 'only-on-failure' do?", ['takes a screenshot after every action', 'saves a screenshot only when a test fails', 'compares screenshots', 'turns screenshots off'], 1,
         'Read the name.', 'A screenshot is taken at the end of each test and kept only if the test failed.'),
    quiz(1, 'Which command opens a trace file in JavaScript?', ['npx playwright open', 'npx playwright show-trace trace.zip', 'npx playwright trace', 'npx playwright report'], 1,
         'show-something.', 'npx playwright show-trace opens the trace viewer with the file.'),
    quiz(1, 'How do you open the Inspector for a Python test?', ['pytest --inspect', 'PWDEBUG=1 pytest -s', 'pytest --ui', 'DEBUG=1 pytest'], 1,
         'An environment variable.', 'PWDEBUG=1 runs headed, turns off timeouts and opens the Inspector.'),
    quiz(2, 'Which value records a trace only when a failed test is retried?', ["'on'", "'retain-on-failure'", "'on-first-retry'", "'off'"], 2,
         'It needs retries to be on.', "on-first-retry records the trace on the first retry of a failed test."),
    quiz(2, 'What does page.pause() do in debug mode?', ['ends the test', 'stops the test at that line until you resume', 'waits 1 second', 'takes a screenshot'], 1,
         'A breakpoint in the test.', 'The test stops and the Inspector waits for Resume or Step over.'),
    quiz(2, 'The error says "strict mode violation: resolved to 2 elements". What is the fix?', ['add a timeout', 'make the locator match only one element', 'use force: true', 'add a retry'], 1,
         'The locator found too much.', 'Narrow it with a role and name, a test id, or a parent locator.'),
    quiz(2, 'Which tool runs tests in a window and reruns them when you save a file?', ['the Inspector', 'UI mode', 'the trace viewer', 'codegen'], 1,
         'npx playwright test --ui', 'UI mode has a test tree, a watch option and the trace views.'),
    quiz(2, 'Where can you open a trace without installing anything?', ['playwright.dev/report', 'trace.playwright.dev', 'github.com/microsoft/playwright', 'localhost:9323'], 1,
         'A static site that reads the file in your browser.', 'trace.playwright.dev opens trace files locally in the browser.'),
    quiz(3, 'What does DEBUG=pw:api print?', ['browser console messages', 'every Playwright call with its timing', 'the HTML report', 'only errors'], 1,
         'It is about the API.', 'Each call is logged when it starts and when it ends.'),
    quiz(3, 'What does Java need so the Inspector can show the test source?', ['PWDEBUG=source', 'PLAYWRIGHT_JAVA_SRC set to the source folders', 'a special Maven plugin', 'nothing'], 1,
         'The JVM runs compiled classes.', 'PLAYWRIGHT_JAVA_SRC lists the folders with the .java files.'),
    quiz(3, 'How does Playwright Test name groups of actions in a trace and report?', ['tracing.group', 'test.step', 'test.describe', 'page.group'], 1,
         'tracing.group is the library way.', 'test.step groups actions in the trace and the HTML report. Python and Java use tracing.group.'),
]

CALC = [
    calc(1, 'A check retries every 100 ms for 5 s. About how many tries is that?', 50, '5000 / 100', ['5 s = 5000 ms', '5000 / 100 = 50 tries']),
    calc(1, '300 tests run, and 6 fail. With retain-on-failure, how many traces are kept?', 6, 'only failures keep a trace', ['passing tests delete their trace', '6 traces are kept']),
    calc(2, 'Each trace is 2 MB. With trace: on, how many MB do those 300 tests produce?', 600, '300 × 2', ['300 × 2 = 600 MB']),
    calc(2, 'And with retain-on-failure, for the 6 failures?', 12, '6 × 2', ['6 × 2 = 12 MB']),
    calc(2, 'A test has 20 actions and you step through each one in 15 s. How many minutes is that?', 5, '20 × 15 / 60', ['20 × 15 = 300 s', '300 / 60 = 5 minutes']),
    calc(3, 'With slowMo 500, a test of 12 actions gets how many seconds slower?', 6, '12 × 0.5', ['slowMo adds 500 ms to each action', '12 × 0.5 = 6 s']),
    calc(3, 'A run of 400 tests has 8 failures. What percent passed?', 98, '(400 - 8) / 400 × 100', ['400 - 8 = 392', '392 / 400 = 0.98', '× 100 = 98 %']),
    calc(3, 'On first retry, 10 tests fail once, and 4 of them fail again. How many traces are recorded?', 10, 'one per first retry', ['every test that is retried records a trace on its first retry', '10 traces']),
]

LABS = [
    {'id': 'greeting', 'title': 'Fix the check with the received value', 'name': 'greets Asha after sign in',
     'task': 'This test fails with <b>Expected: "Hello, Asha!"</b> and <b>Received: "Hello, Asha"</b>. Run it to see the error, then fix the expected text so the test passes.',
     'goal': 'Asha is signed in and the check passes.', 'start': '/login',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('greets Asha after sign in', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('s3cret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.locator('#hello')).toHaveText('Hello, Asha!');
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('greets Asha after sign in', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('s3cret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.locator('#hello')).toHaveText('Hello, Asha');
});'''},
     'hint': 'Compare the expected and the received values in the error. They differ by one character.',
     'why': 'The page and the test disagreed on one exclamation mark. When the page is right, the test changes. When the page is wrong, the test stays and a bug is reported.',
     'check': [['ctx.loggedIn', 'Asha is signed in'], ["/Hello, Asha['\"]/.test(ctx.code)", 'The check expects Hello, Asha']]},
    {'id': 'soldout', 'title': 'Test what the page really shows', 'name': 'the notebook is out of stock',
     'task': 'The notebook test failed because the Notebook (<code>product-4</code>) has no <b>Add to cart</b> button. It is out of stock. Rewrite the test so it checks that the Notebook button says <b>Out of stock</b> and is disabled.',
     'goal': 'The test checks the Out of stock button.', 'start': '/products',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('the notebook is out of stock', async ({ page }) => {
  await page.goto('/products');
  await page.getByTestId('product-4').getByRole('button', { name: 'Add to cart' }).click({ timeout: 3000 });
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('the notebook is out of stock', async ({ page }) => {
  await page.goto('/products');
  const button = page.getByTestId('product-4').getByRole('button');
  await expect(button).toHaveText('Out of stock');
  await expect(button).toBeDisabled();
});'''},
     'hint': "Find the button inside the card with <code>page.getByTestId('product-4').getByRole('button')</code>, then use <code>toHaveText</code> and <code>toBeDisabled</code>.",
     'why': 'The trace showed the card with a disabled Out of stock button, which is the right behaviour for a product with no stock. The old test was wrong, so the new test checks that behaviour instead.',
     'check': [["/Out of stock/.test(ctx.text)", 'The products are on the page'], ["/tobedisabled|to_be_disabled|isdisabled/i.test(ctx.code)", 'The test checks the button is disabled']]},
]

T = {
    'slug': 'pw-debug', 'title': 'Debugging failed tests: errors, traces, reports and the Inspector', 'short': 'Debugging', 'emoji': '🔍', 'module': MODULE, 'minutes': 22,
    'lead': 'Find out why a test failed, quickly and with proof. Read the error, keep a screenshot, a video and a trace for every failure, replay the trace, and step through the test in the Inspector when you need to.',
    'desc': 'Reading Playwright errors and call logs, screenshot, video and trace on failure, retain-on-failure and on-first-retry, the trace viewer, show-trace and trace.playwright.dev, test.step and tracing.group, the HTML report, UI mode, the Inspector with --debug, PWDEBUG and page.pause, and DEBUG=pw:api logs.',
    'summary': 'A failed check read line by line in four languages, a failed click that leaves a screenshot, a video and a trace, a trace with named steps, verbose logs, and real screenshots of the trace viewer, the HTML report, UI mode and the Inspector.',
    'keywords': ['debug', 'trace viewer', 'trace.zip', 'show-trace', 'screenshot', 'video', 'retain-on-failure', 'on-first-retry', 'HTML report', 'UI mode', 'Inspector', 'PWDEBUG', 'page.pause', 'DEBUG=pw:api', 'test.step', 'tracing.group'],
    'plain': 'When a test fails, Playwright can show you exactly what happened: what it looked for, what it found, and a recording of the page at every step. Debugging means reading that evidence before guessing.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
