from pkit import part, say, quiz, calc, panel, four, one, js, ts, py, jv, shown, table, tip, by, pom

MODULE = ('🧪', 'The test runner', 'pw-runner', 'Organising, configuring and running tests: tags, parameters, config, fixtures and hooks, parallel runs, retries, timeouts and sharding.')

JAVA_TRIM = [(r'(?ms)^\tat .*?(?=^\[INFO\]|^\[ERROR\]|^\[WARNING\]|^Run \d|\Z)', ''), (r'(?m)^\[ERROR\] (Please refer|To see the full|Re-run Maven|For more information|-> \[Help|\s*$).*\n?', ''),
             (r'(?m)^\[ERROR\] Failed to execute goal.*\n', ''), (r'(?ms)^\[INFO\] \n\[INFO\] Results:.*?(?=^\[ERROR\] Tests run:|^\[WARNING\] Tests run:)', '')]

# ---------- the shop tests every example in this chapter runs ----------
PAR_CONFIG = '''import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  reporter: 'list',
  fullyParallel: true,              // every test can run at the same time as any other
  workers: 2,                       // two worker processes, each with its own browser
  use: { baseURL: 'http://localhost:4173' },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});'''

PAR_PRODUCTS_TS = '''import { test, expect } from '@playwright/test';

test('shows five products', async ({ page }, testInfo) => {
  console.log(`${testInfo.title} on worker ${testInfo.parallelIndex}`);
  await page.goto('/products');
  await expect(page.getByRole('listitem')).toHaveCount(5);
});

test('finds the lamp', async ({ page }, testInfo) => {
  console.log(`${testInfo.title} on worker ${testInfo.parallelIndex}`);
  await page.goto('/products');
  await page.getByPlaceholder('Search products').fill('lamp');
  await expect(page.getByRole('listitem')).toHaveCount(1);
});'''

PAR_ORDERS_TS = '''import { test, expect } from '@playwright/test';

test('page 1 shows five orders', async ({ page }, testInfo) => {
  console.log(`${testInfo.title} on worker ${testInfo.parallelIndex}`);
  await page.goto('/orders');
  await expect(page.getByRole('row')).toHaveCount(6);        // a header row and five orders
});

test('page 2 is the last page', async ({ page }, testInfo) => {
  console.log(`${testInfo.title} on worker ${testInfo.parallelIndex}`);
  await page.goto('/orders');
  await page.getByRole('button', { name: 'Next' }).click();
  await expect(page.getByText('Page 2 of 2')).toBeVisible();
});'''

PAR_PRODUCTS_PY = '''from playwright.sync_api import Page, expect


def test_shows_five_products(page: Page):
    page.goto("/products")
    expect(page.get_by_role("listitem")).to_have_count(5)


def test_finds_the_lamp(page: Page):
    page.goto("/products")
    page.get_by_placeholder("Search products").fill("lamp")
    expect(page.get_by_role("listitem")).to_have_count(1)'''

PAR_ORDERS_PY = '''from playwright.sync_api import Page, expect


def test_page_1_shows_five_orders(page: Page):
    page.goto("/orders")
    expect(page.get_by_role("row")).to_have_count(6)        # a header row and five orders


def test_page_2_is_the_last_page(page: Page):
    page.goto("/orders")
    page.get_by_role("button", name="Next").click()
    expect(page.get_by_text("Page 2 of 2")).to_be_visible()'''

JUNIT_PARALLEL = '''# Run test classes at the same time, on 2 threads. Tests inside one class stay in order.
junit.jupiter.execution.parallel.enabled = true
junit.jupiter.execution.parallel.mode.default = same_thread
junit.jupiter.execution.parallel.mode.classes.default = concurrent
junit.jupiter.execution.parallel.config.strategy = fixed
junit.jupiter.execution.parallel.config.fixed.parallelism = 2'''

PAR_PRODUCTS_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class ProductsTest {
  @Test
  void showsFiveProducts(Page page) {
    System.out.println("showsFiveProducts on " + Thread.currentThread().getName());
    page.navigate("/products");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(5);
  }

  @Test
  void findsTheLamp(Page page) {
    System.out.println("findsTheLamp on " + Thread.currentThread().getName());
    page.navigate("/products");
    page.getByPlaceholder("Search products").fill("lamp");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(1);
  }
}'''

PAR_ORDERS_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class OrdersTest {
  @Test
  void pageOneShowsFiveOrders(Page page) {
    System.out.println("pageOneShowsFiveOrders on " + Thread.currentThread().getName());
    page.navigate("/orders");
    assertThat(page.getByRole(AriaRole.ROW)).hasCount(6);        // a header row and five orders
  }

  @Test
  void pageTwoIsTheLastPage(Page page) {
    System.out.println("pageTwoIsTheLastPage on " + Thread.currentThread().getName());
    page.navigate("/orders");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Next")).click();
    assertThat(page.getByText("Page 2 of 2")).isVisible();
  }
}'''

# ---------- tests that share data: locks, xdist groups, @ResourceLock ----------
LOCK_TS = '''import { test, expect } from '@playwright/test';

// Both tests count the people in the shop, so they must not run at the same time.
test('add Meera', { lock: 'people' }, async ({ request }) => {
  console.log('add Meera: start');
  const before = (await (await request.get('/api/people')).json()).length;
  await request.post('/api/people', { data: { name: 'Meera', email: 'meera@shop.example' } });
  const after = (await (await request.get('/api/people')).json()).length;
  expect(after).toBe(before + 1);
  console.log('add Meera: done');
});

test('add Chen', { lock: 'people' }, async ({ request }) => {
  console.log('add Chen: start');
  const before = (await (await request.get('/api/people')).json()).length;
  await request.post('/api/people', { data: { name: 'Chen', email: 'chen@shop.example' } });
  const after = (await (await request.get('/api/people')).json()).length;
  expect(after).toBe(before + 1);
  console.log('add Chen: done');
});

test('shows five products', async ({ page }) => {        // no lock, runs alongside
  console.log('products: start');
  await page.goto('/products');
  await expect(page.getByRole('listitem')).toHaveCount(5);
  console.log('products: done');
});'''

LOCK_CONFIG = PAR_CONFIG.replace('workers: 2,                       // two worker processes, each with its own browser',
                                 'workers: 3,')

LOCK_PY = '''import pytest
from playwright.sync_api import Page, expect


# Both tests count the people in the shop. The same group keeps them on one worker, one after the other.
@pytest.mark.xdist_group("people")
def test_add_meera(page: Page):
    before = len(page.request.get("/api/people").json())
    page.request.post("/api/people", data={"name": "Meera", "email": "meera@shop.example"})
    assert len(page.request.get("/api/people").json()) == before + 1


@pytest.mark.xdist_group("people")
def test_add_chen(page: Page):
    before = len(page.request.get("/api/people").json())
    page.request.post("/api/people", data={"name": "Chen", "email": "chen@shop.example"})
    assert len(page.request.get("/api/people").json()) == before + 1


def test_shows_five_products(page: Page):          # no group, runs on any worker
    page.goto("/products")
    expect(page.get_by_role("listitem")).to_have_count(5)'''

JUNIT_LOCK = '''junit.jupiter.execution.parallel.enabled = true
junit.jupiter.execution.parallel.mode.default = same_thread
junit.jupiter.execution.parallel.mode.classes.default = concurrent
junit.jupiter.execution.parallel.config.strategy = fixed
junit.jupiter.execution.parallel.config.fixed.parallelism = 3'''

LOCK_JAVA_MEERA = '''package com.brainy;

import com.google.gson.JsonParser;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.RequestOptions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.parallel.ResourceLock;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

@UsePlaywright(ShopOptions.class)
public class AddMeeraTest {
  @Test
  @ResourceLock("people")              // never at the same time as another test holding "people"
  void addMeera(Page page) {
    System.out.println("add Meera: start");
    int before = JsonParser.parseString(page.request().get("/api/people").text()).getAsJsonArray().size();
    page.request().post("/api/people", RequestOptions.create().setData(Map.of("name", "Meera", "email", "meera@shop.example")));
    int after = JsonParser.parseString(page.request().get("/api/people").text()).getAsJsonArray().size();
    assertEquals(before + 1, after);
    System.out.println("add Meera: done");
  }
}'''

LOCK_JAVA_CHEN = (LOCK_JAVA_MEERA.replace('AddMeeraTest', 'AddChenTest').replace('addMeera', 'addChen')
                  .replace('Meera', 'Chen').replace('meera@', 'chen@'))

LOCK_JAVA_PRODUCTS = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class ProductsTest {
  @Test                                // no lock, runs alongside
  void showsFiveProducts(Page page) {
    System.out.println("products: start");
    page.navigate("/products");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(5);
    System.out.println("products: done");
  }
}'''

# ---------- retries ----------
RETRY_CONFIG = '''import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  reporter: 'list',
  retries: 2,                       // a failed test gets up to 2 more tries
  use: { baseURL: 'http://localhost:4173' },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});'''

RETRY_TS = '''import { test, expect } from '@playwright/test';

test('the offer shows up', async ({ page }, testInfo) => {
  console.log(`attempt ${testInfo.retry + 1}`);
  await page.goto('/widgets');
  await page.getByRole('button', { name: 'Load offers' }).click();
  // Flaky on purpose: the first try waits only 0.5 s, but the offer needs 1.2 s.
  const wait = testInfo.retry === 0 ? 500 : 5_000;
  await expect(page.getByTestId('offer')).toBeVisible({ timeout: wait });
});'''

RETRY_PY = '''from playwright.sync_api import Page, expect


def test_the_offer_shows_up(page: Page, request):
    attempt = request.node.execution_count          # set by pytest-rerunfailures
    print(f"\\nattempt {attempt}")
    page.goto("/widgets")
    page.get_by_role("button", name="Load offers").click()
    # Flaky on purpose: the first try waits only 0.5 s, but the offer needs 1.2 s.
    wait = 500 if attempt == 1 else 5_000
    expect(page.get_by_test_id("offer")).to_be_visible(timeout=wait)'''

RETRY_JAVA = '''package com.brainy;

import com.microsoft.playwright.*;
import com.microsoft.playwright.assertions.LocatorAssertions;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.*;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

// Surefire reruns this class from the start, so it opens and closes Playwright itself.
public class OfferTest {
  private static int attempt = 0;      // the rerun happens in the same JVM
  static Playwright playwright;
  static Browser browser;
  BrowserContext context;
  Page page;

  @BeforeAll
  static void launch() {
    playwright = Playwright.create();
    browser = playwright.chromium().launch();
  }

  @BeforeEach
  void newPage() {
    context = browser.newContext(new Browser.NewContextOptions().setBaseURL("http://localhost:4173"));
    page = context.newPage();
  }

  @Test
  void theOfferShowsUp() {
    attempt++;
    System.out.println("attempt " + attempt);
    page.navigate("/widgets");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Load offers")).click();
    // Flaky on purpose: the first try waits only 0.5 s, but the offer needs 1.2 s.
    double wait = attempt == 1 ? 500 : 5_000;
    assertThat(page.getByTestId("offer")).isVisible(new LocatorAssertions.IsVisibleOptions().setTimeout(wait));
  }

  @AfterEach
  void closeContext() {
    context.close();
  }

  @AfterAll
  static void close() {
    playwright.close();
  }
}'''

# ---------- timeouts ----------
TIME_CONFIG = '''import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  reporter: 'list',
  timeout: 30_000,                  // each test, with its hooks and fixtures
  expect: { timeout: 5_000 },       // each expect check
  use: {
    baseURL: 'http://localhost:4173',
    actionTimeout: 10_000,          // each click, fill, check and so on
    navigationTimeout: 15_000,      // each goto
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});'''

TIME_TS = '''import { test, expect } from '@playwright/test';

test('waits long enough for the offer', async ({ page }) => {
  await page.goto('/widgets');
  await page.getByRole('button', { name: 'Load offers' }).click();
  await expect(page.getByTestId('offer')).toHaveText('Buy 2 mugs, get 1 free');   // the 5 s default is enough
});

test('gives up too early', async ({ page }) => {
  await page.goto('/widgets');
  await page.getByRole('button', { name: 'Load offers' }).click();
  await expect(page.getByTestId('offer')).toBeVisible({ timeout: 1_000 });        // 1 s, but the offer needs 1.2 s
});

test('a slow test gets more time', async ({ page }) => {
  test.slow();                                  // three times the test timeout: 90 s
  await page.goto('/widgets');
  await page.getByRole('button', { name: 'Pay now' }).click({ timeout: 3_000 });  // this click only
  await expect(page.getByText('Payment done')).toBeVisible();
});'''

TIME_CONFTEST = '''import pytest
from playwright.sync_api import Page, expect

expect.set_options(timeout=5_000)                   # each expect check


@pytest.fixture(autouse=True)
def timeouts(page: Page):
    page.set_default_timeout(10_000)                # each click, fill, check and so on
    page.set_default_navigation_timeout(15_000)     # each goto'''

TIME_PY = '''from playwright.sync_api import Page, expect


def test_waits_long_enough_for_the_offer(page: Page):
    page.goto("/widgets")
    page.get_by_role("button", name="Load offers").click()
    expect(page.get_by_test_id("offer")).to_have_text("Buy 2 mugs, get 1 free")   # the 5 s default is enough


def test_gives_up_too_early(page: Page):
    page.goto("/widgets")
    page.get_by_role("button", name="Load offers").click()
    expect(page.get_by_test_id("offer")).to_be_visible(timeout=1_000)            # 1 s, but the offer needs 1.2 s


def test_a_click_with_its_own_timeout(page: Page):
    page.goto("/widgets")
    page.get_by_role("button", name="Pay now").click(timeout=3_000)              # this click only
    expect(page.get_by_text("Payment done")).to_be_visible()'''

TIME_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.LocatorAssertions;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.*;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
@Timeout(30)                                          // each test, in seconds
public class TimeoutsTest {
  @BeforeAll
  static void expectTimeout() {
    PlaywrightAssertions.setDefaultAssertionTimeout(5_000);   // each assertThat check
  }

  @BeforeEach
  void timeouts(Page page) {
    page.setDefaultTimeout(10_000);                   // each click, fill, check and so on
    page.setDefaultNavigationTimeout(15_000);         // each navigate
  }

  @Test
  @Order(1)
  void waitsLongEnoughForTheOffer(Page page) {
    page.navigate("/widgets");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Load offers")).click();
    assertThat(page.getByTestId("offer")).hasText("Buy 2 mugs, get 1 free");   // the 5 s default is enough
  }

  @Test
  @Order(2)
  void givesUpTooEarly(Page page) {
    page.navigate("/widgets");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Load offers")).click();
    assertThat(page.getByTestId("offer")).isVisible(new LocatorAssertions.IsVisibleOptions().setTimeout(1_000));
  }

  @Test
  @Order(3)
  void aClickWithItsOwnTimeout(Page page) {
    page.navigate("/widgets");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Pay now")).click(new Locator.ClickOptions().setTimeout(3_000));
    assertThat(page.getByText("Payment done")).isVisible();
  }
}'''

# ---------- sharding ----------
SHARD_CONFIG = PAR_CONFIG.replace("reporter: 'list',", "reporter: 'list',").replace('workers: 2,                       // two worker processes, each with its own browser',
                                                                                  'workers: 1,')

CODES = {
    'workers': four('Four tests, two at a time',
                    java=jv({'ProductsTest.java': PAR_PRODUCTS_JAVA, 'OrdersTest.java': PAR_ORDERS_JAVA,
                             'src/test/resources/junit-platform.properties': JUNIT_PARALLEL},
                            show=['src/test/resources/junit-platform.properties', 'src/test/java/com/brainy/ProductsTest.java', 'src/test/java/com/brainy/OrdersTest.java']),
                    py=py({'test_products.py': PAR_PRODUCTS_PY, 'test_orders.py': PAR_ORDERS_PY}, cmd='pytest -n 2 -v'),
                    js=js({'products.spec.js': PAR_PRODUCTS_TS, 'orders.spec.js': PAR_ORDERS_TS}, config=PAR_CONFIG,
                          show=['playwright.config.js', 'tests/products.spec.js', 'tests/orders.spec.js']),
                    ts=ts({'products.spec.ts': PAR_PRODUCTS_TS, 'orders.spec.ts': PAR_ORDERS_TS}, config=PAR_CONFIG,
                          show=['playwright.config.ts', 'tests/products.spec.ts', 'tests/orders.spec.ts']),
                    result='Four tests ran on two workers at once, and the output shows which worker took which test. Each worker has its own browser, and each test still gets its own fresh page, so the tests cannot see each other. In Playwright Test the workers are separate processes. pytest-xdist also starts processes, named gw0 and gw1. JUnit uses threads inside one JVM, so each class gets its own Playwright on its own thread.'),
    'lock': four('Two tests that must not run at the same time',
                 java=jv({'AddMeeraTest.java': LOCK_JAVA_MEERA, 'AddChenTest.java': LOCK_JAVA_CHEN, 'ProductsTest.java': LOCK_JAVA_PRODUCTS,
                          'src/test/resources/junit-platform.properties': JUNIT_LOCK},
                         show=['src/test/java/com/brainy/AddMeeraTest.java', 'src/test/java/com/brainy/ProductsTest.java']),
                 py=py({'test_people.py': LOCK_PY}, cmd='pytest -n 3 --dist loadgroup -v'),
                 js=js({'people.spec.js': LOCK_TS}, config=LOCK_CONFIG),
                 ts=ts({'people.spec.ts': LOCK_TS}, config=LOCK_CONFIG),
                 result='The two tests that count people never overlapped: one finished before the other started, while the products test ran next to them. Playwright Test calls this a test lock (new in version 1.63). JUnit has the same idea in @ResourceLock. pytest-xdist has no lock, but a group sends tests to one worker, which runs them one after the other.'),
    'retry': four('A flaky test that passes on the second try',
                  java=jv({'OfferTest.java': RETRY_JAVA}, cmd='mvn test -Dsurefire.rerunFailingTestsCount=2', replace=JAVA_TRIM),
                  py=py({'test_offer.py': RETRY_PY}, cmd='pytest -v -s --reruns 2'),
                  js=js({'offer.spec.js': RETRY_TS}, config=RETRY_CONFIG),
                  ts=ts({'offer.spec.ts': RETRY_TS}, config=RETRY_CONFIG),
                  result='The first try failed, the retry passed, and the run still passed. Each runner marks the test so you notice: Playwright Test says <b>1 flaky</b>, pytest says <b>1 rerun</b> and Surefire says <b>Flakes: 1</b>. A flaky test is a bug in the test or the app, and the retry only hides it until someone fixes it. In our run, a Surefire rerun of a class that uses @UsePlaywright failed with <b>Playwright connection closed</b>, so the Java version opens and closes Playwright in its own @BeforeAll and @AfterAll.'),
    'timeouts': four('Timeouts that are long enough, and one that is too short',
                     java=jv({'TimeoutsTest.java': TIME_JAVA}, expect='fail', replace=JAVA_TRIM),
                     py=py({'conftest.py': TIME_CONFTEST, 'test_timeouts.py': TIME_PY}, expect='fail', show=['conftest.py', 'tests/test_timeouts.py']),
                     js=js({'timeouts.spec.js': TIME_TS}, config=TIME_CONFIG, expect='fail'),
                     ts=ts({'timeouts.spec.ts': TIME_TS}, config=TIME_CONFIG, expect='fail'),
                     result='The offer appears 1.2 s after the click. The default check waits up to 5 s, so the first test passed. The second test allowed only 1 s and failed, and the error names the timeout it used. The Pay now button is disabled for 1 s, and the click waited for it inside its own 3 s limit.'),
    'shard': four('Split the suite in two, as two CI machines would',
                  java=jv({'ProductsTest.java': PAR_PRODUCTS_JAVA, 'OrdersTest.java': PAR_ORDERS_JAVA}, cmd='mvn test -Dtest=ProductsTest',
                          show=['src/test/java/com/brainy/ProductsTest.java', 'src/test/java/com/brainy/OrdersTest.java']),
                  py=py({'test_products.py': PAR_PRODUCTS_PY, 'test_orders.py': PAR_ORDERS_PY}, cmd='pytest --splits 2 --group 1 -v && pytest --splits 2 --group 2 -v'),
                  js=js({'products.spec.js': PAR_PRODUCTS_TS, 'orders.spec.js': PAR_ORDERS_TS}, config=SHARD_CONFIG,
                        cmd='npx playwright test --shard=1/2 && npx playwright test --shard=2/2'),
                  ts=ts({'products.spec.ts': PAR_PRODUCTS_TS, 'orders.spec.ts': PAR_ORDERS_TS}, config=SHARD_CONFIG,
                        cmd='npx playwright test --shard=1/2 && npx playwright test --shard=2/2'),
                  result='Each command ran half of the suite, the way two CI machines would, one command each. Playwright Test splits with --shard. pytest needs a plugin, and pytest-split is shown here. Maven has no shard option, so teams give each machine its own classes with -Dtest, or its own tags with -Dgroups. The other machine would run mvn test -Dtest=OrdersTest.'),
}

DG = {
    'split': {'t': 'Shards on machines, workers inside each machine', 'w': 900, 'h': 250,
              'n': [['suite', 20, 93, 130, 64, '400 tests', {'c': 5, 'sub': 'the whole suite', 'i': 'The full suite, too slow to run on one machine.'}],
                    ['s1', 190, 20, 150, 64, 'shard 1/2', {'c': 2, 'sub': 'machine A', 'i': 'One CI machine runs --shard=1/2, about half of the tests.'}],
                    ['s2', 190, 166, 150, 64, 'shard 2/2', {'c': 2, 'sub': 'machine B', 'i': 'A second CI machine runs --shard=2/2 at the same time.'}],
                    ['w1', 380, 20, 160, 64, '4 workers', {'c': 1, 'sub': 'on machine A', 'i': 'Inside the machine, workers run tests in parallel, each with its own browser.'}],
                    ['w2', 380, 166, 160, 64, '4 workers', {'c': 1, 'sub': 'on machine B', 'i': 'The second machine has its own workers.'}],
                    ['blob', 580, 93, 140, 64, 'blob reports', {'c': 3, 'sub': 'one per shard', 'i': 'Each shard saves its results as a blob report.'}],
                    ['one', 760, 93, 120, 64, 'one report', {'c': 0, 'sub': 'merge-reports', 'i': 'A last job merges the blob reports into one HTML report.'}]],
              'e': [['suite', 's1'], ['suite', 's2'], ['s1', 'w1'], ['s2', 'w2'], ['w1', 'blob'], ['w2', 'blob'], ['blob', 'one']],
              'st': [[['suite'], 'The suite has 400 tests.'],
                     [['s1', 's2', 'suite>s1', 'suite>s2'], 'Sharding splits it between two machines.'],
                     [['w1', 'w2', 's1>w1', 's2>w2'], 'Each machine runs its half on several workers at once.'],
                     [['blob', 'w1>blob', 'w2>blob'], 'Each shard writes a blob report.'],
                     [['one', 'blob>one'], 'merge-reports joins them into one report for the whole run.']]},
}

PARTS = [
    part('workers', '👷', 'Workers: tests at the same time', f'''
<p>A suite of 400 tests that takes 2 seconds each needs over 13 minutes in a row. Run 4 at a time and it needs about 3. Each runner does this with <b>workers</b>: separate processes or threads, each with its own browser.</p>
[[workers]]
{table(['', 'Playwright Test', 'pytest', 'JUnit 5'], [
    ['how', 'built in, worker processes', 'the pytest-xdist plugin, worker processes', 'built in, threads in one JVM'],
    ['turn it on', 'on by default, per file', 'pytest -n 4, or -n auto', 'junit-platform.properties'],
    ['how many', 'workers: 4, or --workers=4', '-n 4', 'config.fixed.parallelism = 4'],
    ['tests inside one file', 'in order, unless fullyParallel: true', 'spread over workers', 'in order, unless mode.default = concurrent'],
    ['turn it off', '--workers=1', 'leave out -n', 'parallel.enabled = false'],
])}
{tip('Playwright Test runs files in parallel and the tests inside a file in order. fullyParallel: true lets every test run on any worker, which balances the load better.', 'tip')}
''', easy=True, kw=['parallel', 'workers', 'fullyParallel', 'pytest-xdist', '-n', 'junit-platform.properties', 'threads']),

    part('isolation', '🧱', 'Parallel tests must not share data', f'''
<p>Each test gets its own page and its own cookies, so the browser side is already separate. The danger is data outside the browser: the same user account, the same database row, the same file. Two tests that change it at the same time can break each other in ways that fail only sometimes.</p>
<p>The best fix is to give each test its own data: a new person with a unique name, a fresh account, a test id in the file name. When a few tests really must share something, tell the runner they must not overlap.</p>
[[lock]]
{tip("Playwright Test also has a serial mode, test.describe.configure({ mode: 'serial' }), where the tests in a file run in order and the rest are skipped after a failure. The Playwright docs advise against it: isolated tests are faster and easier to retry.", 'warn')}
''', kw=['isolation', 'shared state', 'lock', 'ResourceLock', 'xdist_group', 'loadgroup', 'serial']),

    part('retries', '🔁', 'Retries and flaky tests', f'''
<p>A <b>flaky</b> test passes and fails on the same code. A retry runs a failed test again. If it passes the second time, the runner reports it as flaky, so the run stays green but the problem stays visible.</p>
[[retry]]
{table(['', 'Playwright Test', 'pytest', 'JUnit 5 with Maven'], [
    ['set retries', 'retries: 2, or --retries=2', 'the pytest-rerunfailures plugin, --reruns 2', 'mvn test -Dsurefire.rerunFailingTestsCount=2'],
    ['which try is this', 'testInfo.retry, starts at 0', 'request.node.execution_count, starts at 1', 'not given, count it yourself'],
    ['how it is reported', 'flaky', 'rerun', 'Flakes'],
    ['fail the run on flaky tests', '--fail-on-flaky-tests', 'not built in', 'not built in'],
])}
{tip('Most teams turn retries on only in CI, for example retries: process.env.CI ? 2 : 0, and keep a list of flaky tests to fix. A retry also records a trace in Playwright Test when trace is on-first-retry, which is often the fastest way to find the cause.', 'pro')}
''', kw=['retries', 'flaky', 'rerun', 'reruns', 'rerunFailingTestsCount', 'testInfo.retry']),

    part('timeouts', '⏱️', 'Timeouts', f'''
<p>Every wait in Playwright has a limit, so a broken test fails instead of hanging forever. There are several limits, and each one has its own default.</p>
{table(['Limit', 'Default', 'Playwright Test', 'Python', 'Java'], [
    ['one test', '30 s', 'timeout: 30_000, test.setTimeout(), test.slow()', 'not built in (the pytest-timeout plugin adds it)', 'JUnit @Timeout(30)'],
    ['one expect check', '5 s', 'expect: { timeout: 5_000 }', 'expect.set_options(timeout=5_000)', 'PlaywrightAssertions.setDefaultAssertionTimeout(5_000)'],
    ['one action', 'no limit in Playwright Test, 30 s in the libraries', 'use: { actionTimeout }', 'page.set_default_timeout()', 'page.setDefaultTimeout()'],
    ['one navigation', 'no limit in Playwright Test, 30 s in the libraries', 'use: { navigationTimeout }', 'page.set_default_navigation_timeout()', 'page.setDefaultNavigationTimeout()'],
    ['the whole run', 'no limit', 'globalTimeout', 'not built in', 'not built in'],
])}
[[timeouts]]
{tip('When a check times out, the fix is almost never a bigger number. Ask what the page was waiting for. A longer timeout is right only when the app really is that slow, such as a report that takes 20 s to build.', 'tip')}
''', kw=['timeout', 'expect timeout', 'actionTimeout', 'navigationTimeout', 'test.slow', 'setTimeout', 'globalTimeout', '@Timeout']),

    part('sharding', '🍕', 'Sharding across machines', f'''
<p>Workers split tests inside one machine. <b>Sharding</b> splits the suite between several machines, usually CI jobs that run at the same time. Each shard runs its own part, and the reports are joined at the end.</p>
<div class="viz" data-viz="flow" data-k="split"></div>
[[shard]]
{tip('Shards are balanced by test count, not by time. With fullyParallel: true, Playwright Test splits single tests, so the shards come out even. Without it, whole files are split, so keep files a similar size. pytest-split can balance by recorded durations.', 'pro')}
<p>The reporting chapter shows how the blob reports of each shard are merged into one HTML report, and the CI chapter shows the GitHub Actions matrix that starts the shards.</p>
''', kw=['shard', 'sharding', '--shard', 'pytest-split', 'merge-reports', 'blob', 'CI machines']),
]

INFO = {'title': 'Faster runs that stay honest', 'panels': [
    panel([['e', '👷'], ['t', 'workers', {'b': 1}]], 'Workers', 'Tests at the same time.', 'Each with its own browser.'),
    panel([['e', '🔒'], ['t', 'lock', {'b': 1}]], 'Isolation', 'No shared data.', 'Lock what must be shared.'),
    panel([['e', '🔁'], ['t', 'retries', {'b': 1}]], 'Retries', 'Try again on failure.', 'Flaky is still a bug.'),
    panel([['e', '🍕'], ['t', 'shard', {'b': 1}]], 'Shards', 'Split across machines.', 'Merge the reports.')],
    'remember': 'Parallel runs only work when every test can run alone, in any order, next to any other test.'}

REAL = [
    ['⏩', 'Minutes instead of an hour', 'A retail team turns on fullyParallel with 4 workers on each CI machine and splits the run into 2 shards. A suite that took most of an hour now finishes in a few minutes.'],
    ['🎲', 'The test that failed now and then', 'Two tests edit the same customer account. In order they pass, in parallel they fail now and then. Giving each test its own new customer removes the flake for good.'],
    ['📋', 'A flaky list, not a silent retry', 'A payments team keeps retries at 2 in CI, but any test reported as flaky gets a ticket the same day, with the trace from the retry attached.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter makes a suite fast without making it fragile: workers run tests at the same time, locks and groups protect shared data, retries catch flaky tests, timeouts stop hanging tests, and shards split the run across machines.',
        'यह अध्याय suite को तेज़ बनाता है बिना उसे कमज़ोर किए: workers tests को एक साथ चलाते हैं, locks और groups साझा data बचाते हैं, retries flaky tests पकड़ते हैं, timeouts अटके tests रोकते हैं, और shards run को कई machines में बाँटते हैं।',
        'ಈ ಅಧ್ಯಾಯ suite ಅನ್ನು ದುರ್ಬಲಗೊಳಿಸದೆ ವೇಗಗೊಳಿಸುತ್ತದೆ: workers tests ಅನ್ನು ಒಟ್ಟಿಗೆ ನಡೆಸುತ್ತವೆ, locks ಮತ್ತು groups ಹಂಚಿದ data ರಕ್ಷಿಸುತ್ತವೆ, retries flaky tests ಹಿಡಿಯುತ್ತವೆ, timeouts ಸಿಲುಕಿದ tests ನಿಲ್ಲಿಸುತ್ತವೆ, shards run ಅನ್ನು machines ನಡುವೆ ಹಂಚುತ್ತವೆ.',
        'ଏହି ଅଧ୍ୟାୟ suite କୁ ଦୁର୍ବଳ ନକରି ଦ୍ରୁତ କରେ: workers tests କୁ ଏକାସାଙ୍ଗରେ ଚଳାନ୍ତି, locks ଓ groups ବାଣ୍ଟିଥିବା data ରକ୍ଷା କରନ୍ତି, retries flaky tests ଧରନ୍ତି, timeouts ଅଟକିଥିବା tests ବନ୍ଦ କରନ୍ତି, ଏବଂ shards run କୁ machines ମଧ୍ୟରେ ବାଣ୍ଟନ୍ତି।',
        'يجعل هذا الفصل مجموعة الاختبارات سريعة دون أن تصبح هشة: العمال يشغلون الاختبارات معًا، والأقفال والمجموعات تحمي البيانات المشتركة، وإعادة المحاولة تكشف الاختبارات المتقلبة، والمهل توقف الاختبارات العالقة، والتقسيم يوزع التشغيل على عدة أجهزة.',
        'Dieses Kapitel macht eine Testsuite schnell, ohne sie anfällig zu machen: Worker führen Tests gleichzeitig aus, Locks und Gruppen schützen geteilte Daten, Wiederholungen entdecken wackelige Tests, Timeouts stoppen hängende Tests und Shards verteilen den Lauf auf mehrere Maschinen.'),
    say('workers', 'Workers', 'A worker is a process or thread with its own browser. Playwright Test has workers built in, pytest uses pytest-xdist with -n, and JUnit turns on parallel threads in junit-platform.properties.',
        'Worker एक process या thread है जिसका अपना browser होता है। Playwright Test में workers पहले से हैं, pytest में -n के साथ pytest-xdist, और JUnit में junit-platform.properties से parallel threads चालू होते हैं।',
        'Worker ಎಂದರೆ ತನ್ನದೇ browser ಇರುವ process ಅಥವಾ thread. Playwright Test ನಲ್ಲಿ workers ಮೊದಲೇ ಇವೆ, pytest ನಲ್ಲಿ -n ಜೊತೆ pytest-xdist, JUnit ನಲ್ಲಿ junit-platform.properties ಮೂಲಕ parallel threads.',
        'Worker ହେଉଛି ନିଜ browser ଥିବା ଏକ process ବା thread। Playwright Test ରେ workers ପୂର୍ବରୁ ଅଛି, pytest ରେ -n ସହ pytest-xdist, ଏବଂ JUnit ରେ junit-platform.properties ରୁ parallel threads।',
        'العامل عملية أو خيط له متصفحه الخاص. العمال مدمجون في Playwright Test، ويستخدم pytest الإضافة pytest-xdist مع -n، ويشغّل JUnit الخيوط المتوازية من junit-platform.properties.',
        'Ein Worker ist ein Prozess oder Thread mit eigenem Browser. Playwright Test hat Worker eingebaut, pytest nutzt pytest-xdist mit -n, und JUnit schaltet parallele Threads in junit-platform.properties ein.'),
    say('isolation', 'Isolation', 'Tests in parallel must not share data. Give each test its own data. When two tests must share something, a lock in Playwright Test, a ResourceLock in JUnit or an xdist group in pytest keeps them apart.',
        'Parallel tests को data साझा नहीं करना चाहिए। हर test को उसका अपना data दें। जब दो tests को कुछ साझा करना ही हो, तो Playwright Test में lock, JUnit में ResourceLock या pytest में xdist group उन्हें अलग रखता है।',
        'Parallel tests data ಹಂಚಿಕೊಳ್ಳಬಾರದು. ಪ್ರತಿ test ಗೆ ಅದರದೇ data ಕೊಡಿ. ಎರಡು tests ಏನನ್ನಾದರೂ ಹಂಚಿಕೊಳ್ಳಲೇಬೇಕಾದರೆ, Playwright Test ನ lock, JUnit ನ ResourceLock ಅಥವಾ pytest ನ xdist group ಅವುಗಳನ್ನು ಬೇರೆ ಇಡುತ್ತದೆ.',
        'Parallel tests data ବାଣ୍ଟିବା ଉଚିତ ନୁହେଁ। ପ୍ରତି test କୁ ତାର ନିଜ data ଦିଅନ୍ତୁ। ଦୁଇଟି tests କିଛି ବାଣ୍ଟିବାକୁ ପଡିଲେ, Playwright Test ର lock, JUnit ର ResourceLock ବା pytest ର xdist group ସେମାନଙ୍କୁ ଅଲଗା ରଖେ।',
        'يجب ألا تتشارك الاختبارات المتوازية البيانات. أعطِ كل اختبار بياناته الخاصة. وإذا اضطر اختباران إلى مشاركة شيء، فإن القفل في Playwright Test أو ResourceLock في JUnit أو مجموعة xdist في pytest يفصل بينهما.',
        'Parallele Tests dürfen keine Daten teilen. Gib jedem Test eigene Daten. Wenn zwei Tests etwas teilen müssen, hält ein Lock in Playwright Test, ein ResourceLock in JUnit oder eine xdist-Gruppe in pytest sie auseinander.'),
    say('retries', 'Retries', 'A retry runs a failed test again. If it passes, the runner calls it flaky. Retries keep the run green, but a flaky test is still a bug to fix.',
        'Retry fail हुए test को फिर चलाता है। अगर वह pass हो जाए, तो runner उसे flaky कहता है। Retries run को green रखते हैं, पर flaky test फिर भी ठीक करने वाला bug है।',
        'Retry fail ಆದ test ಅನ್ನು ಮತ್ತೆ ನಡೆಸುತ್ತದೆ. ಅದು pass ಆದರೆ runner ಅದನ್ನು flaky ಎನ್ನುತ್ತದೆ. Retries run ಅನ್ನು green ಆಗಿ ಇಡುತ್ತವೆ, ಆದರೆ flaky test ಇನ್ನೂ ಸರಿಪಡಿಸಬೇಕಾದ bug.',
        'Retry fail ହୋଇଥିବା test କୁ ପୁଣି ଚଳାଏ। ଯଦି ଏହା pass ହୁଏ, runner ଏହାକୁ flaky କହେ। Retries run କୁ green ରଖେ, କିନ୍ତୁ flaky test ତଥାପି ଠିକ କରିବାକୁ ଥିବା bug।',
        'إعادة المحاولة تشغّل الاختبار الفاشل مرة أخرى. إذا نجح، يسميه المشغّل متقلبًا. تبقي إعادة المحاولة التشغيل ناجحًا، لكن الاختبار المتقلب يظل خطأ يجب إصلاحه.',
        'Eine Wiederholung führt einen fehlgeschlagenen Test erneut aus. Besteht er dann, nennt der Runner ihn flaky. Wiederholungen halten den Lauf grün, aber ein wackeliger Test bleibt ein Fehler, den man beheben muss.'),
    say('timeouts', 'Timeouts', 'Every wait has a limit: 30 seconds for a test in Playwright Test, 5 seconds for an expect check, and limits for actions and navigation. When a check times out, first ask what the page was waiting for.',
        'हर wait की एक सीमा है: Playwright Test में test के लिए 30 seconds, expect check के लिए 5 seconds, और actions व navigation की सीमाएँ। जब check का समय खत्म हो, पहले पूछें कि page किसका इंतज़ार कर रहा था।',
        'ಪ್ರತಿ wait ಗೆ ಮಿತಿ ಇದೆ: Playwright Test ನಲ್ಲಿ test ಗೆ 30 seconds, expect check ಗೆ 5 seconds, actions ಮತ್ತು navigation ಗೆ ಮಿತಿಗಳು. Check ಸಮಯ ಮೀರಿದಾಗ, page ಯಾವುದಕ್ಕಾಗಿ ಕಾಯುತ್ತಿತ್ತು ಎಂದು ಮೊದಲು ಕೇಳಿ.',
        'ପ୍ରତି wait ର ଏକ ସୀମା ଅଛି: Playwright Test ରେ test ପାଇଁ 30 seconds, expect check ପାଇଁ 5 seconds, ଏବଂ actions ଓ navigation ପାଇଁ ସୀମା। Check ର ସମୟ ସରିଲେ, ପ୍ରଥମେ ପଚାରନ୍ତୁ page କାହା ପାଇଁ ଅପେକ୍ଷା କରୁଥିଲା।',
        'لكل انتظار حد: 30 ثانية للاختبار في Playwright Test، و5 ثوانٍ لفحص expect، وحدود للأفعال والتنقل. عندما تنتهي مهلة فحص، اسأل أولًا عمّا كانت الصفحة تنتظره.',
        'Jedes Warten hat ein Limit: 30 Sekunden für einen Test in Playwright Test, 5 Sekunden für eine expect-Prüfung und Limits für Aktionen und Navigation. Läuft eine Prüfung ab, frag zuerst, worauf die Seite gewartet hat.'),
    say('sharding', 'Sharding', 'Sharding splits the suite between machines. Playwright Test has --shard, pytest uses a plugin such as pytest-split, and Maven runs different classes or tags on each machine. The reports are merged at the end.',
        'Sharding suite को machines में बाँटता है। Playwright Test में --shard है, pytest में pytest-split जैसा plugin, और Maven हर machine पर अलग classes या tags चलाता है। आख़िर में reports जोड़े जाते हैं।',
        'Sharding suite ಅನ್ನು machines ನಡುವೆ ಹಂಚುತ್ತದೆ. Playwright Test ನಲ್ಲಿ --shard ಇದೆ, pytest ನಲ್ಲಿ pytest-split ನಂತಹ plugin, Maven ಪ್ರತಿ machine ನಲ್ಲಿ ಬೇರೆ classes ಅಥವಾ tags ನಡೆಸುತ್ತದೆ. ಕೊನೆಯಲ್ಲಿ reports ಸೇರಿಸಲಾಗುತ್ತದೆ.',
        'Sharding suite କୁ machines ମଧ୍ୟରେ ବାଣ୍ଟେ। Playwright Test ରେ --shard ଅଛି, pytest ରେ pytest-split ପରି plugin, ଏବଂ Maven ପ୍ରତି machine ରେ ଅଲଗା classes ବା tags ଚଳାଏ। ଶେଷରେ reports ଯୋଡାଯାଏ।',
        'التقسيم يوزع مجموعة الاختبارات على الأجهزة. في Playwright Test يوجد ‎--shard، ويستخدم pytest إضافة مثل pytest-split، ويشغّل Maven فئات أو وسومًا مختلفة على كل جهاز. وتُدمج التقارير في النهاية.',
        'Sharding verteilt die Suite auf mehrere Maschinen. Playwright Test hat --shard, pytest nutzt ein Plugin wie pytest-split, und Maven führt auf jeder Maschine andere Klassen oder Tags aus. Am Ende werden die Berichte zusammengeführt.'),
    say('practice', 'Playground labs', 'In the labs you fix a check whose timeout is too short, and give a click its own timeout while the Pay now button is still disabled.',
        'Labs में आप उस check को ठीक करते हैं जिसका timeout बहुत छोटा है, और Pay now button के disabled रहते click को उसका अपना timeout देते हैं।',
        'Labs ನಲ್ಲಿ ತುಂಬಾ ಚಿಕ್ಕ timeout ಇರುವ check ಅನ್ನು ಸರಿಪಡಿಸುತ್ತೀರಿ, ಮತ್ತು Pay now button disabled ಇರುವಾಗ click ಗೆ ಅದರದೇ timeout ಕೊಡುತ್ತೀರಿ.',
        'Labs ରେ ଆପଣ ବହୁତ ଛୋଟ timeout ଥିବା check ଠିକ କରନ୍ତି, ଏବଂ Pay now button disabled ଥିବାବେଳେ click କୁ ତାର ନିଜ timeout ଦିଅନ୍ତି।',
        'في المختبرات تصلح فحصًا مهلته قصيرة جدًا، وتعطي نقرة مهلتها الخاصة بينما زر Pay now ما زال معطلًا.',
        'In den Labs reparierst du eine Prüfung mit zu kurzem Timeout und gibst einem Klick einen eigenen Timeout, solange der Pay-now-Knopf noch deaktiviert ist.'),
]

QUIZ = [
    quiz(1, 'What runs tests at the same time in Playwright Test?', ['hooks', 'workers', 'fixtures', 'shards only'], 1,
         'Each has its own browser.', 'Workers are separate processes that run tests in parallel.'),
    quiz(1, 'How do you run pytest on 4 workers?', ['pytest --workers 4', 'pytest -n 4 with pytest-xdist', 'pytest --parallel', 'pytest -p 4'], 1,
         'The plugin is pytest-xdist.', 'pytest-xdist adds -n, for example -n 4 or -n auto.'),
    quiz(1, 'What is a flaky test?', ['a slow test', 'a test that passes and fails on the same code', 'a skipped test', 'a test without checks'], 1,
         'Same code, different result.', 'Flaky means the result changes between runs without any code change.'),
    quiz(1, 'What is the default expect timeout?', ['1 s', '5 s', '30 s', 'no limit'], 1,
         'Look at the timeouts table.', 'Each expect check retries for up to 5 seconds by default.'),
    quiz(2, 'In Playwright Test, how do tests inside one file run by default?', ['all at once', 'in order, in one worker', 'randomly', 'one per machine'], 1,
         'Files run in parallel, tests inside a file do not.', 'Without fullyParallel, a file runs its tests in order in one worker.'),
    quiz(2, 'Where does JUnit 5 turn on parallel runs?', ['pom.xml only', 'junit-platform.properties', 'playwright.config', '@Parallel on each test'], 1,
         'A properties file in src/test/resources.', 'junit.jupiter.execution.parallel.enabled = true in junit-platform.properties.'),
    quiz(2, 'How does Playwright Test report a test that failed and then passed on retry?', ['passed', 'failed', 'flaky', 'skipped'], 2,
         'Read the retry example.', 'It is counted as flaky, and the run still passes.'),
    quiz(2, 'Two tests change the same customer and fail only in parallel. What is the best fix?', ['more retries', 'a longer timeout', 'give each test its own customer', 'run with one worker'], 2,
         'Remove the shared data.', 'Isolated data removes the cause. Locks or one worker only hide it and slow the run.'),
    quiz(2, 'Which JUnit annotation stops two tests from running at the same time?', ['@Order', '@ResourceLock', '@Timeout', '@Disabled'], 1,
         'It names a shared resource.', '@ResourceLock("people") lets only one test at a time hold that resource.'),
    quiz(3, 'What does --shard=2/3 do?', ['runs 2 of 3 retries', 'runs the second third of the suite', 'uses 2 workers out of 3', 'runs every test twice'], 1,
         'Index over total.', 'It runs shard 2 of 3, the second part of the suite.'),
    quiz(3, 'Which reporter do shards use so their results can be merged?', ['list', 'dot', 'blob', 'line'], 2,
         'Then run merge-reports.', 'Each shard writes a blob report, and npx playwright merge-reports joins them.'),
    quiz(3, 'A check timed out waiting for a button. What should you do first?', ['double every timeout', 'find out why the button did not appear in time', 'add retries', 'add a sleep'], 1,
         'A bigger number usually hides the cause.', 'Find the cause: a wrong locator, a missing step or a real slow page.'),
]

CALC = [
    calc(1, '400 tests take 3 s each, one at a time. How many minutes is that?', 20, '400 × 3 / 60', ['400 × 3 = 1200 s', '1200 / 60 = 20 minutes']),
    calc(1, 'The same 400 tests on 4 workers. About how many minutes now?', 5, '20 / 4', ['20 minutes / 4 workers = 5 minutes']),
    calc(2, 'Split those 400 tests into 2 shards, each with 4 workers. About how many seconds?', 150, '400 × 3 / 8', ['2 × 4 = 8 workers in total', '1200 s / 8 = 150 s']),
    calc(2, 'A test fails twice and passes on the third try. How many retries did it use?', 2, 'tries minus the first', ['3 tries in total', 'the first is not a retry: 3 - 1 = 2']),
    calc(2, 'test.slow() triples the default test timeout of 30 s. How many seconds does the test get?', 90, '30 × 3', ['30 × 3 = 90 s']),
    calc(3, '200 tests, and 6 were flaky last week. What percent is that?', 3, '6 / 200 × 100', ['6 / 200 = 0.03', '× 100 = 3 %']),
    calc(3, 'With --shard=3/4 and 100 tests split evenly, how many tests does shard 3 run?', 25, '100 / 4', ['100 / 4 = 25']),
    calc(3, 'A check waits for an offer that appears after 1.2 s. What is the smallest whole number of seconds that works as its timeout?', 2, 'more than 1.2', ['1 s is too short', '2 s is the smallest whole number above 1.2']),
]

LABS = [
    {'id': 'offerwait', 'title': 'Fix a timeout that is too short', 'name': 'shows the offer',
     'task': 'On <code>/widgets</code> the test clicks <b>Load offers</b>, but the check gives up after 1 second and the offer needs 1.2 seconds. Change the check so it waits long enough, and check the offer says <b>Buy 2 mugs, get 1 free</b>.',
     'goal': 'The offer is on the page and the check passes.', 'start': '/widgets',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('shows the offer', async ({ page }) => {
  await page.goto('/widgets');
  await page.getByRole('button', { name: 'Load offers' }).click();
  await expect(page.getByTestId('offer')).toBeVisible({ timeout: 1000 });
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('shows the offer', async ({ page }) => {
  await page.goto('/widgets');
  await page.getByRole('button', { name: 'Load offers' }).click();
  await expect(page.getByTestId('offer')).toHaveText('Buy 2 mugs, get 1 free', { timeout: 3000 });
});'''},
     'hint': 'Remove the timeout to use the 5 s default, or give a value above 1200, such as <code>{ timeout: 3000 }</code>. Then check the text with <code>toHaveText</code>.',
     'why': 'The check retries until the offer appears or the time runs out. Any limit above 1.2 s passes. The default 5 s is the usual choice, and a custom value is for pages known to be slow.',
     'check': [["/Buy 2 mugs, get 1 free/.test(ctx.text)", 'The offer is on the page'], ["/Buy 2 mugs, get 1 free/.test(ctx.code)", 'The test checks the offer text']]},
    {'id': 'paytimeout', 'title': 'Give one click its own timeout', 'name': 'pays when the button is ready',
     'task': 'On <code>/widgets</code>, <b>Pay now</b> is disabled for the first second. Click it with its own timeout of 3 seconds, then check that <b>Payment done</b> appears.',
     'goal': 'The payment is done.', 'start': '/widgets',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('pays when the button is ready', async ({ page }) => {
  await page.goto('/widgets');
  // click Pay now with a 3 s timeout, then check the message
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('pays when the button is ready', async ({ page }) => {
  await page.goto('/widgets');
  await page.getByRole('button', { name: 'Pay now' }).click({ timeout: 3000 });
  await expect(page.getByText('Payment done')).toBeVisible();
});'''},
     'hint': "Actions take options too: <code>page.getByRole('button', { name: 'Pay now' }).click({ timeout: 3000 })</code>.",
     'why': 'The click waits until the button is enabled, which takes 1 s, well inside its 3 s limit. No sleep is needed, because waiting for an enabled button is part of every click.',
     'check': [["/Payment done/.test(ctx.text)", 'The payment is done'], ["/3000|3_000/.test(ctx.code)", 'The click has a 3 s timeout']]},
]

T = {
    'slug': 'pw-parallel', 'title': 'Parallel runs, retries, timeouts and sharding', 'short': 'Parallel and retries', 'emoji': '⚡', 'module': MODULE, 'minutes': 24,
    'lead': 'Run hundreds of tests in minutes without making them fragile. Workers run tests side by side, locks protect shared data, retries expose flaky tests, timeouts stop hanging ones, and shards split the run across machines.',
    'desc': 'Workers, fullyParallel, pytest-xdist and JUnit parallel threads, test locks, @ResourceLock and xdist groups, retries with pytest-rerunfailures and Surefire, flaky tests, test, expect, action and navigation timeouts, test.slow, sharding with --shard and pytest-split.',
    'summary': 'Four tests on two workers in each language, two tests kept apart with a lock, a flaky test that passes on retry, the five kinds of timeout with one that is too short, and a suite split into two shards.',
    'keywords': ['parallel', 'workers', 'fullyParallel', 'pytest-xdist', 'ResourceLock', 'lock', 'retries', 'flaky', 'reruns', 'timeout', 'expect timeout', 'actionTimeout', 'shard', 'pytest-split', 'merge-reports'],
    'plain': 'A big suite is slow when tests run one by one. Running them side by side, on one machine or many, makes it fast, as long as the tests do not get in each other\'s way.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
