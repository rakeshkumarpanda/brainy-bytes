from pkit import part, say, quiz, calc, panel, four, one, js, ts, py, jv, shown, walk, step, table, tip, by, viz, figure, PW_CONFIG_JS

MODULE = ('🧪', 'The test runner', 'pw-runner', 'Organising, configuring and running tests: tags, parameters, config, fixtures and hooks, parallel runs, retries, timeouts and sharding.')

JAVA_TRIM = [(r'(?ms)^\tat .*?(?=^\[INFO\]|^\[ERROR\]|\Z)', ''), (r'(?m)^\[ERROR\] (Please refer|To see the full|Re-run Maven|For more information|-> \[Help|\s*$).*\n?', ''),
             (r'(?m)^\[ERROR\] Failed to execute goal.*\n', ''), (r'(?ms)^\[INFO\] \n\[INFO\] Results:.*?(?=^\[ERROR\] Tests run:)', '')]

# ---------- hooks ----------
HOOKS_TS = '''import { test, expect } from '@playwright/test';

test.beforeAll(async () => {
  console.log('beforeAll: once for this file');
});

test.beforeEach(async ({ page }, testInfo) => {
  console.log(`beforeEach: open the products page for "${testInfo.title}"`);
  await page.goto('/products');
});

test.afterEach(async ({}, testInfo) => {
  console.log(`afterEach: "${testInfo.title}" ${testInfo.status}`);
});

test.afterAll(async () => {
  console.log('afterAll: once at the end');
});

test('shows five products', async ({ page }) => {
  await expect(page.getByRole('listitem')).toHaveCount(5);
});

test('finds the lamp', async ({ page }) => {
  await page.getByPlaceholder('Search products').fill('lamp');
  await expect(page.getByRole('listitem')).toHaveCount(1);
});'''

HOOKS_PY = '''import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="module", autouse=True)
def once_for_this_file():
    print("\\nbefore all: once for this file")
    yield
    print("\\nafter all: once at the end")


@pytest.fixture(autouse=True)
def open_products(page: Page, request):
    print(f"\\nbefore each: open the products page for {request.node.originalname}")
    page.goto("/products")
    yield
    print(f"\\nafter each: {request.node.originalname} done")


def test_shows_five_products(page: Page):
    expect(page.get_by_role("listitem")).to_have_count(5)


def test_finds_the_lamp(page: Page):
    page.get_by_placeholder("Search products").fill("lamp")
    expect(page.get_by_role("listitem")).to_have_count(1)'''

HOOKS_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.*;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class HooksTest {
  @BeforeAll
  static void onceForThisClass() {
    System.out.println("@BeforeAll: once for this class");
  }

  @BeforeEach
  void openProducts(Page page, TestInfo info) {
    System.out.println("@BeforeEach: open the products page for " + info.getDisplayName());
    page.navigate("/products");
  }

  @AfterEach
  void done(TestInfo info) {
    System.out.println("@AfterEach: " + info.getDisplayName() + " done");
  }

  @AfterAll
  static void atTheEnd() {
    System.out.println("@AfterAll: once at the end");
  }

  @Test
  @Order(1)
  void showsFiveProducts(Page page) {
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(5);
  }

  @Test
  @Order(2)
  void findsTheLamp(Page page) {
    page.getByPlaceholder("Search products").fill("lamp");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(1);
  }
}'''

# ---------- a custom fixture ----------
FIX_DEF_TS = '''import { test as base, expect, type Page } from '@playwright/test';

type ShopFixtures = { signedInPage: Page };

export const test = base.extend<ShopFixtures>({
  signedInPage: async ({ page }, use) => {
    // Set up: sign in as Asha.
    await page.goto('/login');
    await page.getByLabel('Email').fill('asha@shop.example');
    await page.getByLabel('Password').fill('s3cret');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page.getByText('Hello, Asha')).toBeVisible();
    console.log('fixture set up: signed in');

    await use(page);                          // the test runs here

    // Tear down: leave the cart empty for the next test.
    await page.request.delete('/api/cart');
    console.log('fixture tear down: cart emptied');
  },
});

export { expect };'''

FIX_DEF_JS = FIX_DEF_TS.replace("import { test as base, expect, type Page } from '@playwright/test';\n\ntype ShopFixtures = { signedInPage: Page };\n\nexport const test = base.extend<ShopFixtures>({",
                                "import { test as base, expect } from '@playwright/test';\n\nexport const test = base.extend({")

FIX_TEST_TS = '''import { test, expect } from './fixtures';

test('add a mug to the cart', async ({ signedInPage: page }) => {
  await page.getByTestId('product-2').getByRole('button', { name: 'Add to cart' }).click();
  await expect(page.getByRole('status')).toHaveText('Coffee mug added to your cart');
  await expect(page.getByTestId('cart-count')).toHaveText('1');
  console.log('test: the mug is in the cart');
});'''

FIX_TEST_JS = FIX_TEST_TS.replace("'./fixtures'", "'./fixtures.js'")

FIX_CONFTEST = '''import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def signed_in_page(page: Page):
    # Set up: sign in as Asha.
    page.goto("/login")
    page.get_by_label("Email").fill("asha@shop.example")
    page.get_by_label("Password").fill("s3cret")
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_text("Hello, Asha")).to_be_visible()
    print("\\nfixture set up: signed in")

    yield page                                # the test runs here

    # Tear down: leave the cart empty for the next test.
    page.request.delete("/api/cart")
    print("\\nfixture tear down: cart emptied")'''

FIX_TEST_PY = '''from playwright.sync_api import Page, expect


def test_add_a_mug_to_the_cart(signed_in_page: Page):
    page = signed_in_page
    page.get_by_test_id("product-2").get_by_role("button", name="Add to cart").click()
    expect(page.get_by_role("status")).to_have_text("Coffee mug added to your cart")
    expect(page.get_by_test_id("cart-count")).to_have_text("1")
    print("test: the mug is in the cart")'''

FIX_BASE_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

// Every test class that extends this one starts signed in as Asha.
@UsePlaywright(ShopOptions.class)
public abstract class SignedInTest {
  @BeforeEach
  void signIn(Page page) {
    page.navigate("/login");
    page.getByLabel("Email").fill("asha@shop.example");
    page.getByLabel("Password").fill("s3cret");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in")).click();
    assertThat(page.getByText("Hello, Asha")).isVisible();
    System.out.println("set up: signed in");
  }

  @AfterEach
  void emptyCart(Page page) {
    page.request().delete("/api/cart");
    System.out.println("tear down: cart emptied");
  }
}'''

FIX_TEST_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

public class CartTest extends SignedInTest {
  @Test
  void addAMugToTheCart(Page page) {
    page.getByTestId("product-2").getByRole(AriaRole.BUTTON, new Locator.GetByRoleOptions().setName("Add to cart")).click();
    assertThat(page.getByRole(AriaRole.STATUS)).hasText("Coffee mug added to your cart");
    assertThat(page.getByTestId("cart-count")).hasText("1");
    System.out.println("test: the mug is in the cart");
  }
}'''

# ---------- an automatic fixture that fails on page errors ----------
AUTO_DEF_TS = '''import { test as base, expect } from '@playwright/test';

export const test = base.extend<{ failOnPageErrors: void }>({
  failOnPageErrors: [async ({ page }, use) => {
    const errors: string[] = [];
    page.on('pageerror', error => errors.push(error.message));
    await use();
    expect(errors, 'the page threw errors').toEqual([]);
  }, { auto: true }],       // every test gets it, without asking for it
});

export { expect };'''

AUTO_DEF_JS = AUTO_DEF_TS.replace('base.extend<{ failOnPageErrors: void }>(', 'base.extend(').replace('const errors: string[] = [];', 'const errors = [];')

AUTO_TEST_TS = '''import { test, expect } from './fixtures';

test('the products page has no errors', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByRole('listitem')).toHaveCount(5);
});

test('the widgets page breaks', async ({ page }) => {
  await page.goto('/widgets');
  await page.getByRole('button', { name: 'Break the page' }).click();
  await expect(page.getByRole('heading', { name: 'Console and errors' })).toBeVisible();
  // the test itself passes, the fixture finds the error afterwards
});'''

AUTO_TEST_JS = AUTO_TEST_TS.replace("'./fixtures'", "'./fixtures.js'")

AUTO_CONFTEST = '''import pytest
from playwright.sync_api import Page


@pytest.fixture(autouse=True)       # every test gets it, without asking for it
def fail_on_page_errors(page: Page):
    errors = []
    page.on("pageerror", lambda error: errors.append(error.message))
    yield
    assert errors == [], f"the page threw errors: {errors}"'''

AUTO_TEST_PY = '''from playwright.sync_api import Page, expect


def test_the_products_page_has_no_errors(page: Page):
    page.goto("/products")
    expect(page.get_by_role("listitem")).to_have_count(5)


def test_the_widgets_page_breaks(page: Page):
    page.goto("/widgets")
    page.get_by_role("button", name="Break the page").click()
    expect(page.get_by_role("heading", name="Console and errors")).to_be_visible()
    # the test itself passes, the fixture finds the error afterwards'''

AUTO_BASE_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

// Every test class that extends this one fails when its page throws an error.
@UsePlaywright(ShopOptions.class)
public abstract class NoPageErrorsTest {
  private final List<String> errors = new ArrayList<>();

  @BeforeEach
  void listen(Page page) {
    page.onPageError(error -> errors.add(error.split("\\n")[0]));
  }

  @AfterEach
  void noErrors(Page page) {
    page.waitForTimeout(100);   // Java hands over browser events only while a Playwright call runs
    assertEquals(List.of(), errors, "the page threw errors");
  }
}'''

AUTO_TEST_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

public class PagesTest extends NoPageErrorsTest {
  @Test
  void theProductsPageHasNoErrors(Page page) {
    page.navigate("/products");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(5);
  }

  @Test
  void theWidgetsPageBreaks(Page page) {
    page.navigate("/widgets");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Break the page")).click();
    assertThat(page.getByRole(AriaRole.HEADING, new Page.GetByRoleOptions().setName("Console and errors"))).isVisible();
    // the test itself passes, the check after it finds the error
  }
}'''

# ---------- once per run: setup project, session fixture, @BeforeAll ----------
SETUP_CONFIG_TS = '''import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  reporter: 'list',
  use: { baseURL: 'http://localhost:4173' },
  projects: [
    { name: 'setup', testMatch: /global\\.setup\\.[jt]s/ },                // runs first
    { name: 'chromium', use: { ...devices['Desktop Chrome'] }, dependencies: ['setup'] },
  ],
});'''

SETUP_TS = '''import { test as setup, expect } from '@playwright/test';

setup('the shop is up and has test data', async ({ request }) => {
  await expect(await request.get('/api/health')).toBeOK();
  const response = await request.post('/api/people', {
    data: { name: 'Test Customer', email: 'test@shop.example' },
  });
  expect(response.status()).toBe(201);
  console.log('setup: created person', (await response.json()).id);
});'''

SETUP_USE_TS = '''import { test, expect } from '@playwright/test';

test('the test data is there', async ({ request }) => {
  const people = await (await request.get('/api/people')).json();
  console.log('test: people in the shop:', people.map((p: { name: string }) => p.name));
  expect(people).toHaveLength(1);
});'''

SETUP_USE_JS = SETUP_USE_TS.replace('(p: { name: string })', 'p')

SETUP_CONFTEST = '''import pytest
from playwright.sync_api import Playwright, expect


@pytest.fixture(scope="session", autouse=True)      # once for the whole run
def shop_data(playwright: Playwright, base_url: str):
    api = playwright.request.new_context(base_url=base_url)
    expect(api.get("/api/health")).to_be_ok()
    response = api.post("/api/people", data={"name": "Test Customer", "email": "test@shop.example"})
    assert response.status == 201
    print("\\nsetup: created person", response.json()["id"])
    yield
    api.dispose()'''

SETUP_TEST_PY = '''from playwright.sync_api import Page


def test_the_test_data_is_there(page: Page):
    people = page.request.get("/api/people").json()
    print("test: people in the shop:", [p["name"] for p in people])
    assert len(people) == 1'''

API_OPTIONS_JAVA = '''package com.brainy;

import com.microsoft.playwright.APIRequest;
import com.microsoft.playwright.junit.Options;
import com.microsoft.playwright.junit.OptionsFactory;

// setBaseUrl is for pages. The request fixture reads its own options.
public class ApiOptions implements OptionsFactory {
  @Override
  public Options getOptions() {
    return new Options()
        .setHeadless(true)
        .setBaseUrl("http://localhost:4173")
        .setApiRequestOptions(new APIRequest.NewContextOptions().setBaseURL("http://localhost:4173"));
  }
}'''

SETUP_JAVA = '''package com.brainy;

import com.google.gson.JsonParser;
import com.microsoft.playwright.APIRequest;
import com.microsoft.playwright.APIRequestContext;
import com.microsoft.playwright.APIResponse;
import com.microsoft.playwright.Playwright;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.RequestOptions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import java.util.Map;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;

@UsePlaywright(ApiOptions.class)
public class PeopleTest {
  @BeforeAll                                          // once for this class
  static void shopData() {
    try (Playwright playwright = Playwright.create()) {
      APIRequestContext api = playwright.request().newContext(
          new APIRequest.NewContextOptions().setBaseURL("http://localhost:4173"));
      assertThat(api.get("/api/health")).isOK();
      APIResponse response = api.post("/api/people",
          RequestOptions.create().setData(Map.of("name", "Test Customer", "email", "test@shop.example")));
      assertEquals(201, response.status());
      System.out.println("setup: created person " + JsonParser.parseString(response.text()).getAsJsonObject().get("id"));
    }
  }

  @Test
  void theTestDataIsThere(APIRequestContext request) {
    var people = JsonParser.parseString(request.get("/api/people").text()).getAsJsonArray();
    System.out.println("test: people in the shop: " + people);
    assertEquals(1, people.size());
  }
}'''

CODES = {
    'hooks': four('Before and after hooks, and the order they run in',
                  java=jv({'HooksTest.java': HOOKS_JAVA}),
                  py=py({'test_hooks.py': HOOKS_PY}, cmd='pytest -s -q'),
                  js=js({'hooks.spec.js': HOOKS_TS}),
                  ts=ts({'hooks.spec.ts': HOOKS_TS}),
                  result='The once per file hook ran before the first test and after the last one. The each hooks wrapped every test, so both tests started on the products page without a goto of their own. In pytest the same thing is written as fixtures that yield: the code before yield is the set up, the code after it is the tear down.'),
    'fixture': four('A signed in page for every test that asks for it',
                    java=jv({'SignedInTest.java': FIX_BASE_JAVA, 'CartTest.java': FIX_TEST_JAVA}),
                    py=py({'conftest.py': FIX_CONFTEST, 'test_cart.py': FIX_TEST_PY}, cmd='pytest -s -q', show=['conftest.py', 'tests/test_cart.py']),
                    js=js({'fixtures.js': FIX_DEF_JS, 'cart.spec.js': FIX_TEST_JS}),
                    ts=ts({'fixtures.ts': FIX_DEF_TS, 'cart.spec.ts': FIX_TEST_TS}),
                    result='The test only says what it checks. Signing in happened in the fixture before it, and emptying the cart happened after it, even though the test never mentioned either. Any test that asks for the signed in page gets the same set up, and a test that does not ask for it pays nothing. Java has no custom fixtures in the same sense, so the common pattern is a base class with @BeforeEach and @AfterEach.'),
    'auto': four('An automatic fixture that fails a test when the page throws an error',
                 java=jv({'NoPageErrorsTest.java': AUTO_BASE_JAVA, 'PagesTest.java': AUTO_TEST_JAVA}, expect='fail', replace=JAVA_TRIM),
                 py=py({'conftest.py': AUTO_CONFTEST, 'test_pages.py': AUTO_TEST_PY}, expect='fail', show=['conftest.py', 'tests/test_pages.py']),
                 js=js({'fixtures.js': AUTO_DEF_JS, 'pages.spec.js': AUTO_TEST_JS}, expect='fail'),
                 ts=ts({'fixtures.ts': AUTO_DEF_TS, 'pages.spec.ts': AUTO_TEST_TS}, expect='fail'),
                 result='Neither test asked for the fixture, yet both got it. The products page had no errors and passed. The widgets test did everything right, but the page threw <b>Price service is down</b>, so the fixture failed it after the test body finished. pytest reports this as an error in the tear down, which still fails the run. The Java check calls page.waitForTimeout first, because the synchronous Java API delivers browser events only while a Playwright method is running.'),
    'global': four('Set up once: check the shop and create test data',
                   java=jv({'ApiOptions.java': API_OPTIONS_JAVA, 'PeopleTest.java': SETUP_JAVA}),
                   py=py({'conftest.py': SETUP_CONFTEST, 'test_people.py': SETUP_TEST_PY}, cmd='pytest -s -q', show=['conftest.py', 'tests/test_people.py']),
                   js=js({'global.setup.js': SETUP_TS, 'people.spec.js': SETUP_USE_JS}, config=SETUP_CONFIG_TS.replace('[jt]s', '[jt]s'),
                         show=['playwright.config.js', 'tests/global.setup.js', 'tests/people.spec.js']),
                   ts=ts({'global.setup.ts': SETUP_TS, 'people.spec.ts': SETUP_USE_TS}, config=SETUP_CONFIG_TS,
                         show=['playwright.config.ts', 'tests/global.setup.ts', 'tests/people.spec.ts']),
                   result='The set up ran once, before the tests, and created one person through the API. In Playwright Test it is a project that the other projects depend on, so it shows up in the report and the trace like any test. pytest uses a session fixture, and JUnit a static @BeforeAll method. For a whole Maven run, JUnit also offers a LauncherSessionListener. Note ApiOptions in the Java version: setBaseUrl only covers pages, so the request fixture gets its own base URL through setApiRequestOptions.'),
}

DG = {
    'life': {'t': 'The life of one fixture', 'w': 900, 'h': 200,
             'n': [['ask', 20, 70, 150, 64, 'test asks', {'c': 5, 'sub': '({ signedInPage })', 'i': 'The test names the fixture in its parameters. Only fixtures that are asked for run.'}],
                   ['up', 200, 70, 160, 64, 'set up', {'c': 2, 'sub': 'code before use', 'i': 'The fixture prepares what the test needs, such as signing in.'}],
                   ['run', 390, 70, 150, 64, 'the test', {'c': 1, 'sub': 'use(value)', 'i': 'The test body runs with the value the fixture handed over.'}],
                   ['down', 570, 70, 160, 64, 'tear down', {'c': 3, 'sub': 'code after use', 'i': 'The fixture cleans up, even when the test failed.'}],
                   ['next', 760, 70, 120, 64, 'next test', {'c': 0, 'sub': 'fresh again', 'i': 'The next test gets its own fresh fixture.'}]],
             'e': [['ask', 'up'], ['up', 'run'], ['run', 'down'], ['down', 'next']],
             'st': [[['ask'], 'A test asks for a fixture by naming it.'],
                    [['up', 'ask>up'], 'The fixture runs its set up code.'],
                    [['run', 'up>run'], 'It hands its value to the test, and the test runs.'],
                    [['down', 'run>down'], 'After the test, passed or failed, the fixture runs its tear down code.'],
                    [['next', 'down>next'], 'The next test starts from a clean state with its own fixture.']]},
}

BUILTIN = table(['Fixture', 'Playwright Test', 'pytest-playwright', 'Java @UsePlaywright'], [
    ['a fresh page', 'page', 'page', 'Page page'],
    ['its browser context', 'context', 'context', 'BrowserContext browserContext'],
    ['the shared browser', 'browser', 'browser', 'Browser browser'],
    ['an API client', 'request', 'page.request, or playwright.request.new_context()', 'APIRequestContext request'],
    ['which browser', 'browserName', 'browser_name', 'browser.browserType().name()'],
    ['Playwright itself', 'playwright', 'playwright', 'Playwright playwright'],
])

PARTS = [
    part('hooks', '🪝', 'Before and after hooks', f'''
<p>Hooks run code around your tests: before and after each test, or once before and after all the tests in a file or class. They are the simplest way to share set up.</p>
[[hooks]]
{table(['When', 'Playwright Test', 'pytest', 'JUnit 5'], [
    ['before each test', 'test.beforeEach', 'a fixture, code before yield', '@BeforeEach'],
    ['after each test', 'test.afterEach', 'a fixture, code after yield', '@AfterEach'],
    ['once before all', 'test.beforeAll', 'a fixture with scope="module" or "session"', '@BeforeAll (static)'],
    ['once after all', 'test.afterAll', 'the same fixture, after yield', '@AfterAll (static)'],
])}
''', easy=True, kw=['beforeEach', 'afterEach', 'beforeAll', 'afterAll', 'BeforeEach', 'AfterEach', 'hooks', 'yield']),

    part('fixtures', '🧩', 'Fixtures: set up on demand', f'''
<p>A fixture gives a test something it needs, sets it up before the test and cleans it up after. You have used fixtures since the first chapter: <code>page</code> is one.</p>
{BUILTIN}
<div class="viz" data-viz="flow" data-k="life"></div>
<p>You can write your own. A signed in page is the classic first one.</p>
[[fixture]]
{tip('Hooks run for every test in the file. Fixtures run only for tests that ask for them, and they can depend on other fixtures. As a suite grows, teams move set up from hooks into fixtures.', 'pro')}
''', easy=True, kw=['fixture', 'test.extend', 'use', 'conftest', 'yield', 'base class', 'signed in']),

    part('auto', '🛡️', 'Automatic fixtures', f'''
<p>An automatic fixture runs for every test without being asked. It is the right place for checks and recordings that every test should have, such as failing on JavaScript errors.</p>
[[auto]]
''', kw=['auto fixture', 'autouse', 'pageerror', 'guard']),

    part('global', '🌍', 'Set up once for the whole run', f'''
<p>Some work should happen once, not once per test: checking the application is up, creating test data, or signing in and saving the session (the API testing chapter shows that one).</p>
[[global]]
{table(['Scope', 'Playwright Test', 'pytest', 'JUnit 5'], [
    ['each test', 'test fixture (the default)', 'scope="function" (the default)', '@BeforeEach'],
    ['each worker process', "{ scope: 'worker' }", 'not built in (pytest-xdist workers use session)', 'not built in'],
    ['the file or class', 'test.beforeAll', 'scope="module" or "class"', '@BeforeAll'],
    ['the whole run', 'a setup project with dependencies, or globalSetup', 'scope="session"', 'LauncherSessionListener, or @BeforeAll in a base class'],
])}
''', kw=['global setup', 'setup project', 'dependencies', 'session fixture', 'worker fixture', 'BeforeAll', 'scope']),
]

INFO = {'title': 'Set up once, use everywhere', 'panels': [
    panel([['e', '🪝'], ['t', 'beforeEach', {'b': 1}]], 'Hooks', 'Around every test.', 'Simple and visible.'),
    panel([['e', '🧩'], ['t', 'fixture', {'b': 1}]], 'Fixtures', 'Only when asked for.', 'Set up, use, tear down.'),
    panel([['e', '🛡️'], ['t', 'auto', {'b': 1}]], 'Automatic', 'Every test gets it.', 'Guards and recordings.'),
    panel([['e', '🌍'], ['t', 'setup', {'b': 1}]], 'Once per run', 'Health check, data.', 'Before any test.')],
    'remember': 'Put set up where it belongs: in the test if one test needs it, in a fixture if several do, and in a setup step if the whole run does.'}

REAL = [
    ['🛡️', 'JavaScript errors found for free', 'A travel site adds one automatic fixture that fails on page errors. From then on, a broken script fails a test even on pages nobody wrote checks for.'],
    ['🔐', 'One sign in fixture for 400 tests', 'A banking team moves copy pasted sign in steps from hundreds of tests into one fixture. When the sign in page changes, they fix one file.'],
    ['🧹', 'Tests that clean up after themselves', 'A shop test suite empties the cart in a fixture tear down, so a failed test never leaves items that break the next one.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter is about sharing set up: hooks around tests, fixtures that set up only what a test asks for, automatic fixtures for every test, and set up that runs once for the whole run.',
        'यह अध्याय set up साझा करने के बारे में है: tests के चारों ओर hooks, fixtures जो सिर्फ़ वही तैयार करते हैं जो test माँगता है, हर test के लिए automatic fixtures, और पूरे run के लिए एक बार चलने वाला set up।',
        'ಈ ಅಧ್ಯಾಯ set up ಹಂಚಿಕೊಳ್ಳುವುದರ ಬಗ್ಗೆ: tests ಸುತ್ತಲಿನ hooks, test ಕೇಳಿದ್ದನ್ನು ಮಾತ್ರ ಸಿದ್ಧಪಡಿಸುವ fixtures, ಪ್ರತಿ test ಗೆ automatic fixtures, ಮತ್ತು ಸಂಪೂರ್ಣ run ಗೆ ಒಮ್ಮೆ ನಡೆಯುವ set up.',
        'ଏହି ଅଧ୍ୟାୟ set up ବାଣ୍ଟିବା ବିଷୟରେ: tests ଚାରିପାଖରେ hooks, test ମାଗୁଥିବା ଜିନିଷ କେବଳ ପ୍ରସ୍ତୁତ କରୁଥିବା fixtures, ପ୍ରତି test ପାଇଁ automatic fixtures, ଏବଂ ପୂରା run ପାଇଁ ଥରେ ଚାଲୁଥିବା set up।',
        'يتناول هذا الفصل مشاركة التهيئة: خطافات حول الاختبارات، وتجهيزات تعدّ فقط ما يطلبه الاختبار، وتجهيزات تلقائية لكل اختبار، وتهيئة تعمل مرة واحدة للتشغيل كله.',
        'Dieses Kapitel behandelt gemeinsames Setup: Hooks rund um Tests, Fixtures, die nur vorbereiten, was ein Test verlangt, automatische Fixtures für jeden Test und Setup, das einmal pro Lauf läuft.'),
    say('hooks', 'Hooks', 'Before each and after each run around every test, before all and after all run once. In pytest the same idea is a fixture with code before and after yield.',
        'Before each और after each हर test के चारों ओर चलते हैं, before all और after all एक बार। pytest में यही विचार yield से पहले और बाद के code वाला fixture है।',
        'Before each ಮತ್ತು after each ಪ್ರತಿ test ಸುತ್ತ ನಡೆಯುತ್ತವೆ, before all ಮತ್ತು after all ಒಮ್ಮೆ. pytest ನಲ್ಲಿ ಇದೇ ಆಲೋಚನೆ yield ಮುಂಚೆ ಮತ್ತು ನಂತರದ code ಇರುವ fixture.',
        'Before each ଓ after each ପ୍ରତି test ଚାରିପାଖରେ ଚାଲେ, before all ଓ after all ଥରେ। pytest ରେ ସେହି ଧାରଣା yield ପୂର୍ବ ଓ ପର code ଥିବା fixture।',
        'يعمل before each وafter each حول كل اختبار، ويعمل before all وafter all مرة واحدة. في pytest الفكرة نفسها هي تجهيز فيه شيفرة قبل yield وبعده.',
        'Before each und after each laufen um jeden Test, before all und after all einmal. In pytest ist dieselbe Idee eine Fixture mit Code vor und nach yield.'),
    say('fixtures', 'Fixtures', 'A fixture sets up what a test needs, hands it over, and cleans up afterwards. Only tests that ask for a fixture run it. A signed in page is a classic custom fixture.',
        'Fixture वह तैयार करता है जो test को चाहिए, उसे सौंपता है, और बाद में साफ़ करता है। सिर्फ़ fixture माँगने वाले tests उसे चलाते हैं। Signed in page एक जाना माना custom fixture है।',
        'Fixture test ಗೆ ಬೇಕಾದದ್ದನ್ನು ಸಿದ್ಧಪಡಿಸಿ, ಹಸ್ತಾಂತರಿಸಿ, ನಂತರ ಸ್ವಚ್ಛಗೊಳಿಸುತ್ತದೆ. Fixture ಕೇಳಿದ tests ಮಾತ್ರ ಅದನ್ನು ನಡೆಸುತ್ತವೆ. Signed in page ಒಂದು ಪ್ರಸಿದ್ಧ custom fixture.',
        'Fixture test ପାଇଁ ଦରକାରୀ ଜିନିଷ ପ୍ରସ୍ତୁତ କରେ, ହସ୍ତାନ୍ତର କରେ ଏବଂ ପରେ ସଫା କରେ। କେବଳ fixture ମାଗୁଥିବା tests ଏହାକୁ ଚଳାନ୍ତି। Signed in page ଏକ ଜଣାଶୁଣା custom fixture।',
        'التجهيز يعدّ ما يحتاجه الاختبار ويسلّمه ثم ينظف بعده. لا يشغله إلا الاختبار الذي يطلبه. الصفحة المسجّل دخولها مثال شائع لتجهيز مخصص.',
        'Eine Fixture bereitet vor, was ein Test braucht, übergibt es und räumt danach auf. Nur Tests, die sie verlangen, führen sie aus. Eine angemeldete Seite ist die klassische eigene Fixture.'),
    say('auto', 'Automatic fixtures', 'An automatic fixture runs for every test without being asked. A common one fails any test whose page threw a JavaScript error.',
        'Automatic fixture बिना माँगे हर test के लिए चलता है। एक आम उदाहरण वह है जो हर उस test को fail करता है जिसके page ने JavaScript error दिया।',
        'Automatic fixture ಕೇಳದೆಯೇ ಪ್ರತಿ test ಗೆ ನಡೆಯುತ್ತದೆ. ಸಾಮಾನ್ಯ ಉದಾಹರಣೆ: page JavaScript error ನೀಡಿದ test ಅನ್ನು fail ಮಾಡುವುದು.',
        'Automatic fixture ନ ମାଗିଲେ ବି ପ୍ରତି test ପାଇଁ ଚାଲେ। ସାଧାରଣ ଉଦାହରଣ: page JavaScript error ଦେଲେ test କୁ fail କରିବା।',
        'يعمل التجهيز التلقائي لكل اختبار دون أن يُطلب. ومن أشهرها تجهيز يُفشل أي اختبار رمت صفحته خطأ JavaScript.',
        'Eine automatische Fixture läuft für jeden Test, ohne angefordert zu werden. Eine verbreitete lässt jeden Test scheitern, dessen Seite einen JavaScript-Fehler warf.'),
    say('global', 'Once per run', 'Work that should happen once goes in a setup step: a setup project in Playwright Test, a session fixture in pytest, or a static before all method in JUnit.',
        'जो काम एक बार होना चाहिए वह setup step में जाता है: Playwright Test में setup project, pytest में session fixture, या JUnit में static before all method।',
        'ಒಮ್ಮೆ ಆಗಬೇಕಾದ ಕೆಲಸ setup step ಗೆ ಹೋಗುತ್ತದೆ: Playwright Test ನಲ್ಲಿ setup project, pytest ನಲ್ಲಿ session fixture, ಅಥವಾ JUnit ನಲ್ಲಿ static before all method.',
        'ଥରେ ହେବା ଉଚିତ କାମ setup step ରେ ଯାଏ: Playwright Test ରେ setup project, pytest ରେ session fixture, ବା JUnit ରେ static before all method।',
        'العمل الذي يجب أن يحدث مرة واحدة يوضع في خطوة تهيئة: مشروع setup في Playwright Test، أو تجهيز session في pytest، أو دالة before all ثابتة في JUnit.',
        'Arbeit, die einmal passieren soll, gehört in einen Setup-Schritt: ein Setup-Projekt in Playwright Test, eine Session-Fixture in pytest oder eine statische before-all-Methode in JUnit.'),
    say('practice', 'Playground labs', 'In the labs you write the steps a signed in fixture would do and add a lamp to the cart, then you empty the cart the way a tear down would.',
        'Labs में आप वे steps लिखते हैं जो signed in fixture करता और cart में lamp जोड़ते हैं, फिर tear down की तरह cart खाली करते हैं।',
        'Labs ನಲ್ಲಿ signed in fixture ಮಾಡುವ steps ಬರೆದು cart ಗೆ lamp ಸೇರಿಸುತ್ತೀರಿ, ನಂತರ tear down ರೀತಿ cart ಖಾಲಿ ಮಾಡುತ್ತೀರಿ.',
        'Labs ରେ ଆପଣ signed in fixture କରୁଥିବା steps ଲେଖି cart ରେ lamp ଯୋଡନ୍ତି, ତାପରେ tear down ପରି cart ଖାଲି କରନ୍ତି।',
        'في المختبرات تكتب الخطوات التي يقوم بها تجهيز تسجيل الدخول وتضيف مصباحًا إلى السلة، ثم تفرغ السلة كما يفعل التنظيف.',
        'In den Labs schreibst du die Schritte einer Anmelde-Fixture und legst eine Lampe in den Warenkorb, danach leerst du den Warenkorb wie ein Teardown.'),
]

QUIZ = [
    quiz(1, 'Which hook runs before every test in Playwright Test?', ['test.beforeAll', 'test.beforeEach', 'test.setup', 'test.first'], 1,
         'Each means every test.', 'test.beforeEach runs before every test in its scope.'),
    quiz(1, 'In pytest, where does the tear down code of a fixture go?', ['before yield', 'after yield', 'in a separate file', 'in teardown()'], 1,
         'yield hands over the value.', 'Code after yield runs after the test, even when it failed.'),
    quiz(1, 'What is page in async ({ page }) => ...?', ['a global variable', 'a built in fixture', 'a hook', 'a config option'], 1,
         'It is passed in by the runner.', 'page is a built in fixture: a fresh page for each test.'),
    quiz(1, 'Which JUnit 5 annotation runs once before all tests in a class?', ['@BeforeEach', '@BeforeAll', '@Before', '@Setup'], 1,
         'All means once.', '@BeforeAll runs once, and the method is static.'),
    quiz(2, 'When does a custom fixture run?', ['for every test', 'only for tests that ask for it', 'once per file', 'never'], 1,
         'Look at how the test names it.', 'A normal fixture runs only for tests that list it, unless it is automatic.'),
    quiz(2, 'How do you make a Playwright Test fixture run for every test without being asked?', ['scope: worker', 'auto: true', 'global: true', 'always: true'], 1,
         'Look at the automatic fixture.', 'Pass { auto: true } in the fixture tuple.'),
    quiz(2, 'In pytest, how do you make a fixture run for every test without being asked?', ['scope="session"', 'autouse=True', 'auto=True', 'always=True'], 1,
         'Use it automatically.', 'autouse=True makes pytest use the fixture in every test in its scope.'),
    quiz(2, 'Why empty the cart in the fixture tear down, not at the end of the test?', ['It is faster', 'Tear down runs even when the test failed', 'Tests cannot call APIs', 'It is required'], 1,
         'What if the test fails halfway?', 'A failed test stops early, but the tear down still runs, so the next test starts clean.'),
    quiz(2, 'The widgets test passed its own checks but failed. Why?', ['a timeout', 'the automatic fixture found a page error after the test', 'a strict mode violation', 'it was skipped'], 1,
         'Read the auto example result.', 'The page threw an error, and the automatic fixture failed the test after its body finished.'),
    quiz(3, 'What is the recommended way to run set up once before all tests in Playwright Test?', ['a beforeAll in every file', 'a setup project that other projects depend on', 'a sleep', 'a shell script'], 1,
         'It shows up in the report too.', 'A setup project with dependencies runs first and appears in reports and traces.'),
    quiz(3, 'Which pytest fixture scope runs once for the whole run?', ['function', 'module', 'class', 'session'], 3,
         'The widest scope.', 'scope="session" means once per test session.'),
    quiz(3, 'Java has no custom fixtures like test.extend. What do teams usually use?', ['static variables only', 'a base class with @BeforeEach and @AfterEach', 'nothing', 'Python'], 1,
         'Look at SignedInTest.', 'A base class with hooks that test classes extend is the common Java pattern.'),
]

CALC = [
    calc(1, 'A file has 2 tests. How many times does beforeEach run?', 2, 'once per test', ['2 tests × 1 = 2']),
    calc(1, 'A file has 2 tests. How many times does beforeAll run?', 1, 'once per file in one worker', ['beforeAll runs once: 1']),
    calc(2, 'Signing in takes 3 s. 400 tests sign in through the UI. How many minutes does signing in cost?', 20, '400 × 3 / 60', ['400 × 3 = 1200 s', '1200 / 60 = 20 minutes']),
    calc(2, 'A fixture is used by 30 of 100 tests. How many times does it set up?', 30, 'only tests that ask', ['30 tests ask for it', '30 set ups']),
    calc(2, 'An automatic fixture in a suite of 100 tests. How many times does it set up?', 100, 'every test', ['auto: every test gets it', '100']),
    calc(3, 'A session fixture creates 1 person and 3 tests each create 2 more. How many people at the end?', 7, '1 + 3 × 2', ['3 × 2 = 6', '1 + 6 = 7']),
    calc(3, 'The automatic fixture found errors on 4 of 50 pages. What percent had errors?', 8, '4 / 50 × 100', ['4 / 50 = 0.08', '× 100 = 8 %']),
    calc(3, 'A worker fixture takes 3 s and there are 4 workers running 200 tests. How many seconds go to that fixture in total?', 12, 'once per worker', ['4 workers × 3 s = 12 s', 'not 200 × 3, because it is per worker']),
]

LABS = [
    {'id': 'signinadd', 'title': 'Sign in, then add the lamp', 'name': 'add the desk lamp as Asha',
     'task': 'Do what a signed in fixture does: on <code>/login</code> sign in as <code>asha@shop.example</code> with <code>s3cret</code> and wait for <b>Hello, Asha</b>. Then add the <b>Desk lamp</b> to the cart and check the cart counter shows <b>1</b>.',
     'goal': 'Asha is signed in and has the lamp in her cart.', 'start': '/login',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('add the desk lamp as Asha', async ({ page }) => {
  await page.goto('/login');
  // sign in, wait for the greeting, then add the Desk lamp
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('add the desk lamp as Asha', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('s3cret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByText('Hello, Asha')).toBeVisible();
  await page.getByTestId('product-3').getByRole('button', { name: 'Add to cart' }).click();
  await expect(page.getByTestId('cart-count')).toHaveText('1');
});'''},
     'hint': "The Desk lamp card has the test id <code>product-3</code>. Its button: <code>page.getByTestId('product-3').getByRole('button', { name: 'Add to cart' })</code>.",
     'why': 'The first five lines are exactly what the signedInPage fixture does. In a real suite they move into the fixture, and the test keeps only the last two lines.',
     'check': [['ctx.loggedIn', 'Asha is signed in'], ['ctx.cartCount === 1', 'One item is in the cart']]},
    {'id': 'emptycart', 'title': 'Empty the cart like a tear down', 'name': 'empty the cart',
     'task': 'Sign in as Asha, add the <b>Coffee mug</b>, then go to <code>/cart</code>, click <b>Empty cart</b> and check the table says <b>Your cart is empty</b>.',
     'goal': 'The cart is empty again, ready for the next test.', 'start': '/login',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('empty the cart', async ({ page }) => {
  await page.goto('/login');
  // sign in, add the mug, then empty the cart on /cart
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('empty the cart', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('s3cret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByText('Hello, Asha')).toBeVisible();
  await page.getByTestId('product-2').getByRole('button', { name: 'Add to cart' }).click();
  await expect(page.getByTestId('cart-count')).toHaveText('1');
  await page.goto('/cart');
  await page.getByRole('button', { name: 'Empty cart' }).click();
  await expect(page.getByRole('cell', { name: 'Your cart is empty' })).toBeVisible();
});'''},
     'hint': "On <code>/cart</code>, the button is <code>getByRole('button', { name: 'Empty cart' })</code>, and the message is a table cell.",
     'why': 'Wait for the counter to show 1 before leaving the page, or the cart page may load before the item is saved. A tear down that empties the cart keeps one test from changing the next.',
     'check': [["ctx.url.includes('/cart')", 'The test is on the cart page'], ['ctx.loggedIn && ctx.cartCount === 0', 'The cart is empty']]},
]

T = {
    'slug': 'pw-fixtures', 'title': 'Fixtures, hooks and set up once', 'short': 'Fixtures and hooks', 'emoji': '🧩', 'module': MODULE, 'minutes': 22,
    'lead': 'Share set up without copy and paste. Hooks run around tests, fixtures prepare exactly what a test asks for and clean up after it, automatic fixtures guard every test, and set up steps run once for the whole run.',
    'desc': 'beforeEach, afterEach, beforeAll and afterAll, pytest fixtures with yield, JUnit @BeforeEach and @AfterAll, built in fixtures, test.extend, conftest.py, base classes, auto and autouse fixtures, setup projects with dependencies, session fixtures and fixture scopes.',
    'summary': 'The order hooks run in, the built in fixtures of each language, the life of a fixture, a signed in page fixture with a clean up, an automatic fixture that fails tests on JavaScript errors, and set up that checks the shop and creates data once per run.',
    'keywords': ['fixture', 'hooks', 'beforeEach', 'afterEach', 'beforeAll', 'test.extend', 'conftest', 'yield', 'autouse', 'auto', 'setup project', 'dependencies', 'session', 'BeforeEach', 'base class'],
    'plain': 'Most tests need something ready before they start: a signed in user, some data, a page. Fixtures and hooks prepare it in one place and clean up after, so each test only says what it checks.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
