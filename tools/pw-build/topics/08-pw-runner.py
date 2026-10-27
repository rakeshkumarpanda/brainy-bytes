from pkit import part, say, quiz, calc, panel, four, one, js, ts, py, jv, shown, walk, step, table, tip, by, viz, figure, PW_CONFIG_JS

MODULE = ('🧪', 'The test runner', 'pw-runner', 'Organising, configuring and running tests: tags, parameters, config, fixtures and hooks, parallel runs, retries, timeouts and sharding.')

# ---------- organising tests ----------
ORG_TS = '''import { test, expect } from '@playwright/test';

test.describe('products page', () => {
  test('shows five products', { tag: '@smoke' }, async ({ page }) => {
    await page.goto('/products');
    await expect(page.getByRole('listitem')).toHaveCount(5);
  });

  test('sorts by price', { tag: '@regression' }, async ({ page }) => {
    await page.goto('/products');
    await page.getByLabel('Sort by').selectOption('low');
    await expect(page.getByRole('listitem').first()).toContainText('Gel pen');
  });

  test.skip('adds a product to the wish list', async ({ page }) => {
    // the wish list is not built yet
  });

  test('sells phones', {
    tag: '@regression',
    annotation: { type: 'issue', description: 'SHOP-42: phones arrive next month' },
  }, async ({ page }) => {
    test.fail();   // known to fail today, so a failure is the expected result
    await page.goto('/products');
    await page.getByPlaceholder('Search products').fill('phone');
    await expect(page.getByRole('button', { name: 'Add to cart' })).toHaveCount(1, { timeout: 1000 });
  });
});'''

ORG_PY = '''import pytest
from playwright.sync_api import Page, expect


class TestProductsPage:
    @pytest.mark.smoke
    def test_shows_five_products(self, page: Page):
        page.goto("/products")
        expect(page.get_by_role("listitem")).to_have_count(5)

    @pytest.mark.regression
    def test_sorts_by_price(self, page: Page):
        page.goto("/products")
        page.get_by_label("Sort by").select_option("low")
        expect(page.get_by_role("listitem").first).to_contain_text("Gel pen")

    @pytest.mark.skip(reason="the wish list is not built yet")
    def test_adds_a_product_to_the_wish_list(self, page: Page):
        pass

    @pytest.mark.regression
    @pytest.mark.xfail(reason="SHOP-42: phones arrive next month", strict=True)
    def test_sells_phones(self, page: Page):
        page.goto("/products")
        page.get_by_placeholder("Search products").fill("phone")
        expect(page.get_by_role("button", name="Add to cart")).to_have_count(1, timeout=1000)'''

ORG_INI = '''[pytest]
addopts = --base-url http://localhost:4173
markers =
    smoke: quick checks for every deploy
    regression: the full set of checks'''

ORG_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
@DisplayName("Products page")
public class ProductsPageTest {
  @Test
  @Tag("smoke")
  @DisplayName("shows five products")
  void showsFiveProducts(Page page) {
    page.navigate("/products");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(5);
  }

  @Test
  @Tag("regression")
  @DisplayName("sorts by price")
  void sortsByPrice(Page page) {
    page.navigate("/products");
    page.getByLabel("Sort by").selectOption("low");
    assertThat(page.getByRole(AriaRole.LISTITEM).first()).containsText("Gel pen");
  }

  @Test
  @Disabled("the wish list is not built yet")
  void addsAProductToTheWishList(Page page) {
  }

  // JUnit has no "expected to fail". Teams disable the test and name the ticket: SHOP-42.
}'''

# ---------- parameterised tests ----------
PAR_TS = '''import { test, expect } from '@playwright/test';

const searches = [
  { term: 'mug', count: 1, first: 'Coffee mug' },
  { term: 'o', count: 3, first: 'Coffee mug' },
  { term: 'pen', count: 1, first: 'Gel pen' },
  { term: 'BOTTLE', count: 1, first: 'Water bottle' },
];

for (const { term, count, first } of searches) {
  test(`search for "${term}" finds ${count}`, async ({ page }) => {
    await page.goto('/products');
    await page.getByPlaceholder('Search products').fill(term);
    const cards = page.getByRole('listitem');
    await expect(cards).toHaveCount(count);
    await expect(cards.first()).toContainText(first);
  });
}'''

PAR_PY = '''import pytest
from playwright.sync_api import Page, expect


@pytest.mark.parametrize("term, count, first", [
    ("mug", 1, "Coffee mug"),
    ("o", 3, "Coffee mug"),
    ("pen", 1, "Gel pen"),
    ("BOTTLE", 1, "Water bottle"),
])
def test_search(page: Page, term: str, count: int, first: str):
    page.goto("/products")
    page.get_by_placeholder("Search products").fill(term)
    cards = page.get_by_role("listitem")
    expect(cards).to_have_count(count)
    expect(cards.first).to_contain_text(first)'''

PAR_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class SearchTest {
  @ParameterizedTest(name = "search for \\"{0}\\" finds {1}")
  @CsvSource({
      "mug, 1, Coffee mug",
      "o, 3, Coffee mug",
      "pen, 1, Gel pen",
      "BOTTLE, 1, Water bottle",
  })
  void search(String term, int count, String first, Page page) {   // the data first, then Page
    page.navigate("/products");
    page.getByPlaceholder("Search products").fill(term);
    Locator cards = page.getByRole(AriaRole.LISTITEM);
    assertThat(cards).hasCount(count);
    assertThat(cards.first()).containsText(first);
  }
}'''

# ---------- configuration ----------
CFG_TS = '''import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,                   // one test may take 30 s
  expect: { timeout: 5_000 },        // one assertion may keep trying for 5 s
  fullyParallel: true,
  forbidOnly: !!process.env.CI,      // a forgotten test.only fails the CI run
  retries: process.env.CI ? 2 : 0,
  workers: 2,
  reporter: 'list',
  use: {
    baseURL: 'http://localhost:4173',
    locale: 'en-IN',
    timezoneId: 'Asia/Kolkata',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'phone', use: { ...devices['Pixel 7'] } },
  ],
});'''

CFG_TEST_TS = '''import { test } from '@playwright/test';

test('the config reaches every test', async ({ page }, testInfo) => {
  await page.goto('/about-you');
  console.log(testInfo.project.name.padEnd(8),
    '| viewport', page.viewportSize()?.width,
    '| language', await page.locator('#lang').textContent(),
    '| time zone', await page.locator('#tz').textContent());
});'''

CFG_INI = '''[pytest]
addopts =
    --base-url http://localhost:4173
    --browser chromium
    --screenshot only-on-failure
    --tracing retain-on-failure'''

CFG_CONFTEST = '''import pytest


# Options for every browser context that the page fixture opens.
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "locale": "en-IN", "timezone_id": "Asia/Kolkata"}'''

CFG_TEST_PY = '''from playwright.sync_api import Page


def test_the_config_reaches_every_test(page: Page):
    page.goto("/about-you")
    print("| viewport", page.viewport_size["width"],
          "| language", page.locator("#lang").text_content(),
          "| time zone", page.locator("#tz").text_content())'''

CFG_OPTIONS_JAVA = '''package com.brainy;

import com.microsoft.playwright.Browser;
import com.microsoft.playwright.junit.Options;
import com.microsoft.playwright.junit.OptionsFactory;

// Shared settings for every test class that says @UsePlaywright(ShopOptions.class)
public class ShopOptions implements OptionsFactory {
  @Override
  public Options getOptions() {
    return new Options()
        .setHeadless(true)
        .setBrowserName("chromium")
        .setBaseUrl("http://localhost:4173")
        .setContextOptions(new Browser.NewContextOptions()
            .setLocale("en-IN")
            .setTimezoneId("Asia/Kolkata"));
  }
}'''

CFG_PHONE_JAVA = '''package com.brainy;

import com.microsoft.playwright.Browser;
import com.microsoft.playwright.junit.Options;
import com.microsoft.playwright.junit.OptionsFactory;

// The same shop, as a phone. setDeviceName uses Playwright's device list.
public class PhoneOptions implements OptionsFactory {
  @Override
  public Options getOptions() {
    return new Options()
        .setHeadless(true)
        .setBaseUrl("http://localhost:4173")
        .setDeviceName("Pixel 7")
        .setContextOptions(new Browser.NewContextOptions()
            .setLocale("en-IN")
            .setTimezoneId("Asia/Kolkata"));
  }
}'''

CFG_SHOW_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;

// A helper both test classes share.
public class AboutYou {
  static void show(String name, Page page) {
    page.navigate("/about-you");
    System.out.println(String.format("%-8s", name)
        + "| viewport " + page.viewportSize().width
        + " | language " + page.locator("#lang").textContent()
        + " | time zone " + page.locator("#tz").textContent());
  }
}'''

CFG_DESKTOP_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import org.junit.jupiter.api.Test;

@UsePlaywright(ShopOptions.class)
public class DesktopTest {
  @Test
  void theConfigReachesEveryTest(Page page) { AboutYou.show("desktop", page); }
}'''

CFG_PHONE_TEST_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import org.junit.jupiter.api.Test;

@UsePlaywright(PhoneOptions.class)
public class PhoneTest {
  @Test
  void theConfigReachesEveryTest(Page page) { AboutYou.show("phone", page); }
}'''

NO_MVN_NOISE = [(r'(?m)^\[INFO\] (-+|\s*|T E S T S|Results:|BUILD SUCCESS|Total time.*|Finished at.*)\n', '')]

CODES = {
    'organize': four('Group, tag, skip and mark known failures',
                     java=jv({'ProductsPageTest.java': ORG_JAVA}),
                     py=py({'test_products_page.py': ORG_PY}, ini=ORG_INI),
                     js=js({'products-page.spec.js': ORG_TS}),
                     ts=ts({'products-page.spec.ts': ORG_TS}),
                     result='Four tests, one result each: two passed, one skipped, and one failed as expected. The test that is known to fail keeps the run green: Playwright Test shows its cross but counts it as passed, and pytest calls it xfailed. The day phones arrive it turns red, which reminds the team to remove the mark. JUnit has no such mark, so the Java class skips that case.'),
    'select': four('Run only the tests with one tag',
                   java=jv({'ProductsPageTest.java': ORG_JAVA}, cmd='mvn test -Dgroups=smoke', replace=NO_MVN_NOISE),
                   py=py({'test_products_page.py': ORG_PY}, ini=ORG_INI, cmd='pytest -v -m smoke'),
                   js=js({'products-page.spec.js': ORG_TS}, cmd='npx playwright test --grep @smoke'),
                   ts=ts({'products-page.spec.ts': ORG_TS}, cmd='npx playwright test --grep @smoke'),
                   result='The same file, but only the smoke test ran. Playwright Test matches the tag in the title and tag list with <code>--grep</code>, pytest selects markers with <code>-m</code>, and Maven Surefire passes JUnit tags with <code>-Dgroups</code>. All three accept expressions, such as <code>--grep-invert @slow</code>, <code>-m "smoke and not slow"</code> or <code>-Dgroups="smoke &amp; !slow"</code>.'),
    'param': four('One test, many rows of data',
                  java=jv({'SearchTest.java': PAR_JAVA}, pom_xml=None, replace=NO_MVN_NOISE),
                  py=py({'test_search.py': PAR_PY}),
                  js=js({'search.spec.js': PAR_TS}),
                  ts=ts({'search.spec.ts': PAR_TS}),
                  result='Four rows of data became four separate tests, each with its own name and its own fresh page. A failure names the row that failed. The search ignores case, so BOTTLE finds the Water bottle.'),
    'config': four('Configuration that every test receives',
                   java=jv({'ShopOptions.java': CFG_OPTIONS_JAVA, 'PhoneOptions.java': CFG_PHONE_JAVA, 'AboutYou.java': CFG_SHOW_JAVA, 'DesktopTest.java': CFG_DESKTOP_JAVA, 'PhoneTest.java': CFG_PHONE_TEST_JAVA},
                           cmd='mvn test', replace=NO_MVN_NOISE),
                   py=py({'test_config.py': CFG_TEST_PY, 'conftest.py': CFG_CONFTEST}, ini=CFG_INI,
                         cmd='pytest -s -q && pytest -s -q --device "Pixel 7"', shown_cmd='pytest -s -q\npytest -s -q --device "Pixel 7"',
                         show=['pytest.ini', 'conftest.py', 'tests/test_config.py']),
                   js=js({'config.spec.js': CFG_TEST_TS}, config=CFG_TS, show=['playwright.config.js', 'tests/config.spec.js']),
                   ts=ts({'config.spec.ts': CFG_TEST_TS}, config=CFG_TS, show=['playwright.config.ts', 'tests/config.spec.ts']),
                   result='One test ran as a desktop browser and as a phone, and both got the language and time zone from the configuration, not from the test. Chromium reports the time zone Asia/Kolkata by its older name Asia/Calcutta, which is the same zone. In Playwright Test, projects run the same tests with different settings. pytest-playwright takes the device from the command line, and Java uses one options class per setup.'),
}

DG = {
    'run': {'t': 'What happens when you start a test run', 'w': 900, 'h': 210,
            'n': [['find', 20, 75, 150, 64, 'find tests', {'c': 5, 'sub': 'files and names', 'i': 'The runner collects test files and test names, and applies filters such as tags.'}],
                  ['cfg', 190, 75, 150, 64, 'read config', {'c': 3, 'sub': 'one place', 'i': 'Base URL, browser, timeouts, retries, reporters and projects come from the configuration.'}],
                  ['work', 360, 75, 160, 64, 'start workers', {'c': 2, 'sub': 'in parallel', 'i': 'Worker processes start, each with its own browser.'}],
                  ['each', 540, 75, 170, 64, 'each test', {'c': 1, 'sub': 'a fresh context', 'i': 'Every test gets a new browser context and page, so tests do not share cookies or storage.'}],
                  ['rep', 730, 75, 150, 64, 'report', {'c': 0, 'sub': 'pass, fail, skip', 'i': 'Reporters print results and write files such as HTML or JUnit XML.'}]],
            'e': [['find', 'cfg'], ['cfg', 'work'], ['work', 'each'], ['each', 'rep']],
            'st': [[['find'], 'The runner finds your test files and test names and applies filters, such as a tag.'],
                   [['cfg', 'find>cfg'], 'It reads the configuration once: base URL, browser, timeouts, retries and reporters.'],
                   [['work', 'cfg>work'], 'It starts worker processes so several tests can run at the same time.'],
                   [['each', 'work>each'], 'Every test gets a fresh browser context and page.'],
                   [['rep', 'each>rep'], 'Results go to reporters: the terminal, an HTML report, JUnit XML for CI and more.']]},
}

RUNNERS = table(['Language', 'Test runner', 'How Playwright plugs in'], [
    ['JavaScript, TypeScript', 'Playwright Test (@playwright/test)', 'built in: fixtures, config, projects, retries, sharding, reporters, UI mode'],
    ['Python', 'pytest', 'the pytest-playwright plugin gives page, context and browser fixtures and CLI options'],
    ['Java', 'JUnit 5 or TestNG', 'JUnit 5: @UsePlaywright injects Page and friends (since 1.42). TestNG: you create them in hooks'],
    ['C#', 'NUnit, MSTest or xUnit', 'base classes such as PageTest give you Page'],
])

PARTS = [
    part('runners', '🏃', 'One library, a runner per language', f'''
<p>Playwright itself drives the browser. A <b>test runner</b> finds your tests, runs them, and reports the results. Each language uses the runner its developers already know.</p>
{RUNNERS}
<div class="viz" data-viz="flow" data-k="run"></div>
{tip('Playwright Test was built by the Playwright team, so it has the most features out of the box. pytest, JUnit and TestNG need a plugin or a little code for the same things, which the next chapters show side by side.', 'tip')}
''', easy=True, kw=['test runner', 'Playwright Test', 'pytest', 'JUnit', 'TestNG', 'UsePlaywright']),

    part('organize', '🗂️', 'Grouping, tags and annotations', f'''
<p>A real suite has hundreds of tests. Groups keep related tests together, tags let you run a slice such as the smoke tests, and annotations say why a test is skipped or expected to fail.</p>
[[organize]]
{table(['You want', 'JavaScript and TypeScript', 'Python (pytest)', 'Java (JUnit 5)'], [
    ['a group', 'test.describe()', 'a class TestSomething', 'a test class with @DisplayName'],
    ['a tag', "{ tag: '@smoke' }", '@pytest.mark.smoke', '@Tag("smoke")'],
    ['skip', 'test.skip()', '@pytest.mark.skip(reason=...)', '@Disabled("why")'],
    ['skip on a condition', 'test.skip(condition, reason)', '@pytest.mark.skipif(condition, reason=...)', '@EnabledOnOs, @DisabledIf...'],
    ['known to fail', 'test.fail()', '@pytest.mark.xfail(strict=True)', 'not built in, @Disabled with the ticket'],
    ['broken, fix later', 'test.fixme()', '@pytest.mark.skip with a reason', '@Disabled'],
    ['give it more time', 'test.slow()', 'a timeout marker from a plugin', '@Timeout'],
    ['run only this one', 'test.only()', '-k name on the command line', '-Dtest=Class#method'],
])}
{tip('A test.only left in the code silently skips every other test. Set forbidOnly in the CI config so such a run fails instead.', 'warn')}
''', easy=True, kw=['describe', 'tag', 'grep', 'skip', 'fixme', 'fail', 'xfail', 'marker', 'Disabled', 'Tag', 'annotation']),

    part('select', '🎯', 'Running a slice of the suite', f'''
<p>Tags pay off when you run only some tests: smoke tests on every deploy, the full regression at night.</p>
[[select]]
''', kw=['grep', 'markers', '-m', 'groups', 'smoke', 'regression']),

    part('param', '🔁', 'Parameterised tests', f'''
<p>When the same steps should run with different data, write the steps once and feed them rows of data. Each row becomes its own test in the report.</p>
[[param]]
{tip('In real projects the rows often come from a CSV or JSON file, for example 50 postcodes for a delivery check. Read the file at the top of the test file and loop over it, or use @CsvFileSource in JUnit and a list built from the file in pytest.', 'pro')}
''', easy=True, kw=['parameterize', 'parametrize', 'ParameterizedTest', 'CsvSource', 'data driven']),

    part('config', '⚙️', 'Configuration in one place', f'''
<p>Settings that are the same for every test belong in one place, not in each test: the base URL, the browser, timeouts, retries, what to record on failure, and the devices to test.</p>
[[config]]
{table(['Setting', 'Playwright Test', 'pytest-playwright', 'Java JUnit'], [
    ['base URL', "use: { baseURL }", '--base-url', 'setBaseUrl'],
    ['browser', "projects with devices['Desktop Firefox']", '--browser firefox', 'setBrowserName("firefox")'],
    ['headed', '--headed or use: { headless: false }', '--headed', 'setHeadless(false)'],
    ['device', "use: { ...devices['Pixel 7'] }", '--device "Pixel 7"', 'setDeviceName("Pixel 7")'],
    ['locale and other context options', "use: { locale }", 'browser_context_args fixture', 'setContextOptions(...)'],
    ['test timeout', 'timeout', 'a plugin such as pytest-timeout', '@Timeout or junit.jupiter.execution.timeout'],
    ['screenshots, video, trace', "use: { screenshot, video, trace }", '--screenshot, --video, --tracing', 'setTrace(...) and your own hooks'],
])}
''', kw=['playwright.config', 'pytest.ini', 'conftest', 'OptionsFactory', 'projects', 'devices', 'baseURL', 'use']),
]

INFO = {'title': 'Let the runner do the work', 'panels': [
    panel([['e', '🏃'], ['t', 'runner', {'b': 1}]], 'Runner', 'Finds and runs tests.', 'One per language.'),
    panel([['e', '🏷️'], ['t', '@smoke', {'b': 1}]], 'Tags', 'Run a slice.', 'Smoke now, regression tonight.'),
    panel([['e', '🔁'], ['t', 'parametrize', {'b': 1}]], 'Data', 'One test, many rows.', 'Each row is its own result.'),
    panel([['e', '⚙️'], ['t', 'config', {'b': 1}]], 'Config', 'Settings in one place.', 'Projects for each device.')],
    'remember': 'Tests say what to check. The runner and its configuration decide where, how and with what settings they run.'}

REAL = [
    ['🚀', 'Smoke tests on every deploy', 'A food delivery app runs 20 tests tagged @smoke after every deploy in 3 minutes, and the full 1000 test regression every night.'],
    ['🏷️', 'Known bugs stay visible', 'A bank marks tests for known bugs as expected to fail with the ticket number. The day a fix ships, the test turns red and the team removes the mark.'],
    ['📮', 'Fifty postcodes, one test', 'A courier company checks delivery prices for 50 postcodes with one parameterised test that reads a CSV file.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter is about the test runner: which runner each language uses, how to group, tag and skip tests, how to run a slice of the suite, parameterised tests, and configuration.',
        'यह अध्याय test runner के बारे में है: हर भाषा कौन सा runner इस्तेमाल करती है, tests को group, tag और skip कैसे करें, suite का हिस्सा कैसे चलाएँ, parameterised tests और configuration।',
        'ಈ ಅಧ್ಯಾಯ test runner ಬಗ್ಗೆ: ಪ್ರತಿ ಭಾಷೆ ಯಾವ runner ಬಳಸುತ್ತದೆ, tests ಅನ್ನು group, tag ಮತ್ತು skip ಮಾಡುವುದು, suite ನ ಭಾಗ ನಡೆಸುವುದು, parameterised tests ಮತ್ತು configuration.',
        'ଏହି ଅଧ୍ୟାୟ test runner ବିଷୟରେ: ପ୍ରତି ଭାଷା କେଉଁ runner ବ୍ୟବହାର କରେ, tests କୁ group, tag ଓ skip କିପରି କରିବେ, suite ର ଅଂଶ କିପରି ଚଳାଇବେ, parameterised tests ଓ configuration।',
        'يتناول هذا الفصل مشغل الاختبارات: أي مشغل تستخدمه كل لغة، وكيف تجمع الاختبارات وتوسمها وتتخطاها، وكيف تشغل جزءًا من المجموعة، والاختبارات ذات المعاملات، والإعدادات.',
        'Dieses Kapitel behandelt den Test Runner: welchen Runner jede Sprache nutzt, wie man Tests gruppiert, taggt und überspringt, wie man einen Teil der Suite ausführt, parametrisierte Tests und Konfiguration.'),
    say('runners', 'Runners', 'Playwright drives the browser and a test runner runs the tests. JavaScript and TypeScript use Playwright Test, Python uses pytest with a plugin, and Java uses JUnit or TestNG.',
        'Playwright browser चलाता है और test runner tests चलाता है। JavaScript और TypeScript Playwright Test, Python plugin के साथ pytest, और Java JUnit या TestNG इस्तेमाल करते हैं।',
        'Playwright browser ನಡೆಸುತ್ತದೆ, test runner tests ನಡೆಸುತ್ತದೆ. JavaScript ಮತ್ತು TypeScript Playwright Test, Python plugin ಜೊತೆ pytest, Java JUnit ಅಥವಾ TestNG ಬಳಸುತ್ತವೆ.',
        'Playwright browser ଚଳାଏ ଏବଂ test runner tests ଚଳାଏ। JavaScript ଓ TypeScript Playwright Test, Python plugin ସହ pytest, ଏବଂ Java JUnit ବା TestNG ବ୍ୟବହାର କରନ୍ତି।',
        'يقود Playwright المتصفح ويشغّل مشغل الاختبارات الاختبارات. تستخدم JavaScript وTypeScript أداة Playwright Test، وتستخدم Python أداة pytest مع إضافة، وتستخدم Java أداة JUnit أو TestNG.',
        'Playwright steuert den Browser, ein Test Runner führt die Tests aus. JavaScript und TypeScript nutzen Playwright Test, Python pytest mit einem Plugin und Java JUnit oder TestNG.'),
    say('organize', 'Organising tests', 'Group related tests, tag them as smoke or regression, skip what is not built yet, and mark known failures with the ticket number so they turn red when the bug is fixed.',
        'मिलते जुलते tests को group करें, उन्हें smoke या regression tag दें, जो अभी बना नहीं उसे skip करें, और जानी हुई failures को ticket number के साथ mark करें ताकि bug ठीक होने पर वे लाल हो जाएँ।',
        'ಸಂಬಂಧಿತ tests ಅನ್ನು group ಮಾಡಿ, smoke ಅಥವಾ regression tag ನೀಡಿ, ಇನ್ನೂ ಮಾಡದದ್ದನ್ನು skip ಮಾಡಿ, ತಿಳಿದ failures ಅನ್ನು ticket number ಜೊತೆ mark ಮಾಡಿ, bug ಸರಿಯಾದಾಗ ಅವು ಕೆಂಪಾಗುತ್ತವೆ.',
        'ସମ୍ପର୍କିତ tests କୁ group କରନ୍ତୁ, smoke ବା regression tag ଦିଅନ୍ତୁ, ଯାହା ଏପର୍ଯ୍ୟନ୍ତ ତିଆରି ହୋଇନି ତାକୁ skip କରନ୍ତୁ, ଜଣା failures କୁ ticket number ସହ mark କରନ୍ତୁ ଯାହାଫଳରେ bug ଠିକ୍ ହେଲେ ସେମାନେ ଲାଲ ହୁଅନ୍ତି।',
        'اجمع الاختبارات المترابطة ووسمها كاختبارات smoke أو regression، وتخطَّ ما لم يُبنَ بعد، وعلّم الإخفاقات المعروفة برقم التذكرة لتتحول إلى الأحمر عند إصلاح الخلل.',
        'Gruppiere zusammengehörige Tests, tagge sie als Smoke oder Regression, überspringe Unfertiges und markiere bekannte Fehler mit der Ticketnummer, damit sie rot werden, sobald der Fehler behoben ist.'),
    say('select', 'Running a slice', 'Run only some tests by tag: grep in Playwright Test, dash m in pytest, and dash D groups in Maven. Smoke tests on every deploy, the full set at night.',
        'Tag से कुछ ही tests चलाएँ: Playwright Test में grep, pytest में dash m, और Maven में dash D groups। हर deploy पर smoke tests, रात को पूरा set।',
        'Tag ಮೂಲಕ ಕೆಲವು tests ಮಾತ್ರ ನಡೆಸಿ: Playwright Test ನಲ್ಲಿ grep, pytest ನಲ್ಲಿ dash m, Maven ನಲ್ಲಿ dash D groups. ಪ್ರತಿ deploy ಗೆ smoke tests, ರಾತ್ರಿ ಸಂಪೂರ್ಣ set.',
        'Tag ଦ୍ୱାରା କିଛି tests ଚଳାନ୍ତୁ: Playwright Test ରେ grep, pytest ରେ dash m, Maven ରେ dash D groups। ପ୍ରତି deploy ରେ smoke tests, ରାତିରେ ପୂରା set।',
        'شغّل بعض الاختبارات فقط حسب الوسم: grep في Playwright Test وdash m في pytest وdash D groups في Maven. اختبارات smoke مع كل نشر والمجموعة الكاملة ليلًا.',
        'Führe nur einige Tests per Tag aus: grep in Playwright Test, Minus m in pytest und Minus D groups in Maven. Smoke-Tests bei jedem Deploy, das volle Set nachts.'),
    say('param', 'Parameterised tests', 'Write the steps once and give them rows of data. Each row becomes its own test with its own name, so a failure tells you which row broke.',
        'Steps एक बार लिखें और उन्हें data की rows दें। हर row अपने नाम के साथ अलग test बनती है, इसलिए failure बताता है कि कौन सी row टूटी।',
        'Steps ಒಮ್ಮೆ ಬರೆದು ಅವುಗಳಿಗೆ data rows ನೀಡಿ. ಪ್ರತಿ row ತನ್ನದೇ ಹೆಸರಿನ ಪ್ರತ್ಯೇಕ test ಆಗುತ್ತದೆ, failure ಯಾವ row ಮುರಿಯಿತು ಎಂದು ಹೇಳುತ್ತದೆ.',
        'Steps ଥରେ ଲେଖନ୍ତୁ ଏବଂ ସେଗୁଡ଼ିକୁ data ର rows ଦିଅନ୍ତୁ। ପ୍ରତି row ନିଜ ନାମ ସହ ଅଲଗା test ହୁଏ, ତେଣୁ failure କହେ କେଉଁ row ଭାଙ୍ଗିଲା।',
        'اكتب الخطوات مرة واحدة وأعطها صفوفًا من البيانات. يصبح كل صف اختبارًا مستقلًا باسمه، فيخبرك الفشل بالصف الذي تعطل.',
        'Schreibe die Schritte einmal und gib ihnen Datenzeilen. Jede Zeile wird ein eigener Test mit eigenem Namen, sodass ein Fehler die kaputte Zeile nennt.'),
    say('config', 'Configuration', 'Put shared settings in one place: base URL, browser, timeouts, retries, recordings on failure and devices. Projects in Playwright Test run the same tests with different settings.',
        'साझा settings एक जगह रखें: base URL, browser, timeouts, retries, failure पर recordings और devices। Playwright Test में projects वही tests अलग settings के साथ चलाते हैं।',
        'ಹಂಚಿಕೊಂಡ settings ಒಂದೇ ಸ್ಥಳದಲ್ಲಿ ಇರಿಸಿ: base URL, browser, timeouts, retries, failure ಸಮಯದ recordings ಮತ್ತು devices. Playwright Test ನ projects ಅದೇ tests ಅನ್ನು ಬೇರೆ settings ಜೊತೆ ನಡೆಸುತ್ತವೆ.',
        'ସାଝା settings ଗୋଟିଏ ଜାଗାରେ ରଖନ୍ତୁ: base URL, browser, timeouts, retries, failure ରେ recordings ଓ devices। Playwright Test ର projects ସେହି tests କୁ ଅଲଗା settings ସହ ଚଳାନ୍ତି।',
        'ضع الإعدادات المشتركة في مكان واحد: عنوان URL الأساسي والمتصفح والمهل وإعادة المحاولة والتسجيلات عند الفشل والأجهزة. تشغّل المشاريع في Playwright Test الاختبارات نفسها بإعدادات مختلفة.',
        'Lege gemeinsame Einstellungen an einem Ort ab: Basis-URL, Browser, Timeouts, Wiederholungen, Aufnahmen bei Fehlern und Geräte. Projekte in Playwright Test führen dieselben Tests mit anderen Einstellungen aus.'),
    say('practice', 'Playground labs', 'In the labs you write a quick smoke test for the home page, and a test that uses the header to reach the orders page.',
        'Labs में आप home page का छोटा smoke test लिखते हैं, और header से orders page तक पहुँचने वाला test।',
        'Labs ನಲ್ಲಿ home page ಗೆ ಸಣ್ಣ smoke test ಬರೆಯುತ್ತೀರಿ, ಮತ್ತು header ಮೂಲಕ orders page ತಲುಪುವ test.',
        'Labs ରେ ଆପଣ home page ପାଇଁ ଛୋଟ smoke test ଲେଖନ୍ତି, ଏବଂ header ଦ୍ୱାରା orders page ପର୍ଯ୍ୟନ୍ତ ପହଞ୍ଚୁଥିବା test।',
        'في المختبرات تكتب اختبار smoke سريعًا للصفحة الرئيسية، واختبارًا يستخدم الترويسة للوصول إلى صفحة الطلبات.',
        'In den Labs schreibst du einen schnellen Smoke-Test für die Startseite und einen Test, der über die Kopfzeile zur Bestellseite geht.'),
]

QUIZ = [
    quiz(1, 'Which runner do Python Playwright tests usually use?', ['unittest only', 'pytest with pytest-playwright', 'Playwright Test', 'JUnit'], 1,
         'Look at the runner table.', 'pytest with the pytest-playwright plugin gives the page fixture and the CLI options.'),
    quiz(1, 'How do you tag a test as smoke in Playwright Test?', ["test('x', { tag: '@smoke' }, ...)", 'test.smoke()', '@smoke above the test', 'test.only()'], 0,
         'Tags are an option of the test.', 'Pass a tag in the details object, or put @smoke in the title.'),
    quiz(1, 'How do you run only tests tagged smoke in pytest?', ['pytest --tag smoke', 'pytest -m smoke', 'pytest -k @smoke', 'pytest smoke'], 1,
         'm for marker.', 'pytest selects markers with -m.'),
    quiz(1, 'Where should the base URL live?', ['in every test', 'in the configuration', 'in an environment variable only', 'in the page object'], 1,
         'One place for shared settings.', 'The base URL goes in the config, so tests can use relative addresses.'),
    quiz(2, 'What does test.fail() (or xfail) mean?', ['skip the test', 'the test is expected to fail, and a failure keeps the run green', 'retry the test', 'fail the whole run'], 1,
         'Look at the organize result.', 'The test runs and is expected to fail. If it passes unexpectedly, the run reports it.'),
    quiz(2, 'In JUnit 5, how do you run only tests tagged smoke with Maven?', ['mvn test -m smoke', 'mvn test -Dgroups=smoke', 'mvn test --grep smoke', 'mvn smoke'], 1,
         'Surefire passes JUnit tags as groups.', '-Dgroups=smoke tells Surefire which JUnit tags to include.'),
    quiz(2, 'A parameterised test has 4 rows of data. How many results does the report show?', ['1', '4', '0', 'depends on the browser'], 1,
         'Each row is a test.', 'Each row runs as its own test with its own result.'),
    quiz(2, 'In a JUnit @ParameterizedTest with @UsePlaywright, where does the Page parameter go?', ['first', 'after the data parameters', 'it cannot be used', 'in a field'], 1,
         'Look at the Java parameter example.', 'JUnit fills the source arguments first, then resolves the remaining parameters such as Page.'),
    quiz(2, 'Why set forbidOnly on CI?', ['To speed up', 'A forgotten test.only would silently skip all other tests', 'To allow retries', 'For reports'], 1,
         'What does test.only do?', 'test.only runs just that test. forbidOnly makes such a run fail instead of passing quietly.'),
    quiz(3, 'How does one Playwright Test run cover a desktop and a phone?', ['two config files', 'two projects with different use settings', 'a loop in each test', 'it cannot'], 1,
         'Look at the config example.', 'Each project runs every test with its own settings, such as a device.'),
    quiz(3, 'Where do you set the locale for every page in pytest-playwright?', ['pytest.ini locale=', 'a browser_context_args fixture in conftest.py', 'page.set_locale()', '--locale'], 1,
         'Context options come from a fixture.', 'Override the browser_context_args fixture and add locale.'),
    quiz(3, 'Why did the time zone print as Asia/Calcutta when the config said Asia/Kolkata?', ['A bug', 'Chromium reports the older name of the same zone', 'Java changed it', 'The server is in Calcutta'], 1,
         'Both names exist in the time zone database.', 'Asia/Kolkata and Asia/Calcutta are the same zone, and Chromium reports the older name.'),
]

CALC = [
    calc(1, 'A file has 4 tests: 2 pass, 1 is skipped and 1 is expected to fail and does. How many tests ran in the browser?', 3, '4 - 1 skipped', ['The skipped test does not run', '4 - 1 = 3']),
    calc(1, 'A parameterised test has 4 rows and runs in 2 projects. How many results?', 8, '4 × 2', ['4 rows × 2 projects = 8']),
    calc(2, 'The full suite has 1000 tests and 20 are tagged smoke. What percent is smoke?', 2, '20 / 1000 × 100', ['20 / 1000 = 0.02', '0.02 × 100 = 2 %']),
    calc(2, '50 postcodes in a CSV and 3 browsers. How many test results?', 150, '50 × 3', ['50 × 3 = 150']),
    calc(2, 'Smoke tests take 3 minutes and run on 12 deploys a day. How many minutes a day?', 36, '3 × 12', ['3 × 12 = 36 minutes']),
    calc(3, 'retries is 2 on CI. A test fails every time. How many times does it run in total?', 3, '1 + 2 retries', ['the first run', '+ 2 retries', '= 3 runs']),
    calc(3, 'The Pixel 7 viewport is 412 px wide and the desktop one is 1280 px. How many px wider is the desktop?', 868, '1280 - 412', ['1280 - 412 = 868']),
    calc(3, 'Each test may take 30 s. In the worst case, how many minutes can 10 tests take on 1 worker?', 5, '10 × 30 / 60', ['10 × 30 = 300 s', '300 / 60 = 5 minutes']),
]

LABS = [
    {'id': 'smoke', 'title': 'A smoke test for the home page', 'name': 'the home page works',
     'task': 'Open <code>/</code>. Check the heading <b>Welcome to Brainy Shop</b> is visible, click the <b>Browse products</b> link, and check that the address ends with <code>/products</code>.',
     'goal': 'The home page shows its heading and leads to the products.', 'start': '/',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('the home page works', { tag: '@smoke' }, async ({ page }) => {
  await page.goto('/');
  // check the heading, follow the Browse products link, check the address
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('the home page works', { tag: '@smoke' }, async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Welcome to Brainy Shop' })).toBeVisible();
  await page.getByRole('link', { name: 'Browse products' }).click();
  await expect(page).toHaveURL(/\\/products$/);
});'''},
     'hint': "<code>page.getByRole('link', { name: 'Browse products' }).click()</code>, then <code>expect(page).toHaveURL(/\\/products$/)</code>.",
     'why': 'A smoke test checks the few things that must work after every deploy: the page loads and the main way in works. Keep it short so it can run often.',
     'check': [["ctx.url.includes('/products')", 'The test reached the products page'], ["/Welcome to Brainy Shop/.test(ctx.code)", 'The test checks the heading']]},
    {'id': 'headerorders', 'title': 'Reach the orders page from the header', 'name': 'the header leads to orders',
     'task': 'Open <code>/</code>. Click <b>Orders</b> in the header navigation, check the heading <b>Past orders</b>, and check the table shows <b>6</b> rows (5 orders and the header row).',
     'goal': 'The header link opens the orders table.', 'start': '/',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('the header leads to orders', async ({ page }) => {
  await page.goto('/');
  // click Orders in the navigation, then check the heading and the rows
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('the header leads to orders', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('navigation', { name: 'Main' }).getByRole('link', { name: 'Orders' }).click();
  await expect(page.getByRole('heading', { name: 'Past orders' })).toBeVisible();
  await expect(page.getByRole('row')).toHaveCount(6);
});'''},
     'hint': "The header has <code>&lt;nav aria-label=\"Main\"&gt;</code>, so <code>page.getByRole('navigation', { name: 'Main' })</code> finds it.",
     'why': 'Starting from the navigation keeps the test from clicking another Orders link somewhere else on the page.',
     'check': [["ctx.url.includes('/orders')", 'The test opened the orders page'], ["/6/.test(ctx.code)", 'The test counts the rows']]},
]

T = {
    'slug': 'pw-runner', 'title': 'The test runner: organise, tag, parameterise and configure', 'short': 'Test runner', 'emoji': '🏃', 'module': MODULE, 'minutes': 22,
    'lead': 'Let the runner do the heavy lifting. Group and tag tests, skip and mark known failures, run a slice of the suite, feed one test many rows of data, and keep every setting in one configuration.',
    'desc': 'Playwright Test, pytest with pytest-playwright and JUnit 5 with @UsePlaywright side by side: describe and classes, tags and markers, skip, fail and xfail, grep, -m and -Dgroups, parameterised tests, playwright.config projects, pytest.ini and conftest, and OptionsFactory.',
    'summary': 'Which runner each language uses, what happens in a test run, groups, tags, skip and expected failures in all four languages, running only smoke tests, parameterised search tests, and one test run as a desktop and as a phone from configuration.',
    'keywords': ['test runner', 'Playwright Test', 'pytest', 'JUnit', 'describe', 'tag', 'grep', 'marker', 'skip', 'xfail', 'parametrize', 'ParameterizedTest', 'config', 'projects', 'OptionsFactory', 'conftest'],
    'plain': 'Playwright moves the browser. The test runner decides which tests run, with which settings, and how the results are reported. This chapter shows the runner of each language doing the same jobs.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
