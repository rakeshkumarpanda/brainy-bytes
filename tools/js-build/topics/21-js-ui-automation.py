# Chapter 21: browser automation with Playwright, Selenium WebDriver, Cypress and WebdriverIO, run against a small demo shop.
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg
from shop_app import SHOP_FILES

MODULE = ('🧪', 'Testing with JavaScript', 'js-testing', 'Unit tests, API tests and browser automation with node:test, Jest, Vitest, Mocha, supertest, Playwright, Selenium and Cypress.')

PW = [(r' \(\d+(\.\d+)?m?s\)', ''), (r'\((\d+(\.\d+)?)m?s\)\s*$', '(3.1s)'), (r'(passed|failed|flaky) \([\d.]+m?s\)', r'\1 (3.1s)'),
      (r'\n\s+at .*\n', '\n'), (r'Error Context: .*\n', ''), (r'\n\s+attachment #\d[\s\S]*?─+\n', '\n')]
MOCHA = [(r' \(\d+ms\)', ''), (r'passing \(\d+m?s\)', 'passing (4s)')]


def pw_config(port, use='', extra=''):
    """A Playwright config for the demo shop. Each example gets its own port so they can run side by side."""
    return f'''
import {{ defineConfig, devices }} from "@playwright/test";

export default defineConfig({{
  testDir: "tests",
  reporter: "list",
  workers: 1,                       // one worker keeps the output in the same order on this page
  use: {{ baseURL: "http://localhost:{port}"{use} }},
  projects: [{{ name: "chromium", use: {{ ...devices["Desktop Chrome"] }} }}],
  webServer: {{
    command: "node server.js",
    url: "http://localhost:{port}",
    env: {{ PORT: "{port}" }},
    reuseExistingServer: !process.env.CI,
  }},{extra}
}});
'''


def shop(port, tests, use='', extra='', more=None):
    files = {'package.json': pkg('shop-e2e', 'module', {'test': 'playwright test'}), **SHOP_FILES,
             'playwright.config.js': pw_config(port, use, extra)}
    files.update(tests)
    files.update(more or {})
    return files


LOGIN_STEPS = '''
  await page.getByLabel("Email").fill("asha@shop.example");
  await page.getByLabel("Password").fill("s3cret");
  await page.getByRole("button", { name: "Sign in" }).click();'''

SELENIUM_DRIVER_ESM = r'''
// One place that knows how to start Chrome for every Selenium test.
// Selenium Manager downloads a matching chromedriver by itself. CI machines
// can point CHROMEDRIVER and CHROME_BIN at fixed copies instead.
import { Builder } from "selenium-webdriver";
import chrome from "selenium-webdriver/chrome.js";

export async function buildDriver() {
  const options = new chrome.Options().addArguments("--headless=new", "--no-sandbox", "--window-size=1280,800");
  if (process.env.CHROME_BIN) options.setChromeBinaryPath(process.env.CHROME_BIN);
  const builder = new Builder().forBrowser("chrome").setChromeOptions(options);
  if (process.env.CHROMEDRIVER) builder.setChromeService(new chrome.ServiceBuilder(process.env.CHROMEDRIVER));
  return builder.build();
}
'''

CODES = {
    'shop-app': show(SHOP_FILES['site/index.html'], 'The demo shop page (site/index.html)', lang='html', note='The app under test',
                     result='A login form, a product list that loads after 600 ms, a cart and a Place order button. server.js serves it with Express and a small API.'),
    'pw-first': test(shop(4301, {'tests/shop.spec.js': '''
import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
});

test("wrong password shows an error", async ({ page }) => {
  await page.getByLabel("Email").fill("asha@shop.example");
  await page.getByLabel("Password").fill("wrong");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page.getByRole("alert")).toHaveText("Wrong email or password");
});

test("log in, add two products and place an order", async ({ page }) => {''' + LOGIN_STEPS + '''
  await expect(page.getByText("Hello, asha")).toBeVisible();

  // The list arrives 600 ms later. No sleep: the assertion keeps retrying.
  const products = page.getByTestId("product");
  await expect(products).toHaveCount(3);
  await products.filter({ hasText: "Coffee mug" }).getByRole("button", { name: "Add to cart" }).click();
  await products.filter({ hasText: "Gel pen" }).getByRole("button").click();

  await expect(page.getByTestId("cart-count")).toHaveText("2");
  await expect(page.locator("#total")).toHaveText("₹219");
  await page.getByRole("button", { name: "Place order" }).click();
  await expect(page.getByText(/^Order \\d+ placed$/)).toBeVisible();
});
'''}), 'npx playwright test', 'A first Playwright suite', show=['playwright.config.js', 'tests/shop.spec.js'], replace=PW),
    'pw-strict': test(shop(4302, {'tests/strict.spec.js': '''
import { test, expect } from "@playwright/test";

test("a locator that matches two elements", async ({ page }) => {
  await page.goto("/");''' + LOGIN_STEPS + '''
  await page.getByTestId("product").first().getByRole("button").click();
  await expect(page.getByRole("status")).toHaveText("");   // which status?
});
'''}), 'npx playwright test', 'Strict mode stops an ambiguous locator', show=['tests/strict.spec.js'], expect='fail',
        replace=PW + [(r'\n\s+Call log:[\s\S]*?(?=\n\s+\d+ \|)', '\n'), (r'\n\s+\d+ \|[\s\S]*?(?=\n\n)', ''), (r'\n  1 failed[\s\S]*', '\n  1 failed'), (r'\n    \n', '\n')]),
    'pw-network': test(shop(4303, {'tests/network.spec.js': '''
import { test, expect } from "@playwright/test";

async function logIn(page) {
  await page.goto("/");''' + LOGIN_STEPS + '''
}

test("shows a friendly message when the products API fails", async ({ page }) => {
  await page.route("**/api/products", route => route.fulfill({ status: 503, body: "down" }));
  await logIn(page);
  await expect(page.getByText("Could not load products. Try again later.")).toBeVisible();
});

test("renders whatever the API returns, even a huge price", async ({ page }) => {
  await page.route("**/api/products", route =>
    route.fulfill({ json: [{ id: 9, name: "Gold watch", price: 1234567 }] }));
  await logIn(page);
  await expect(page.getByTestId("product")).toHaveText(/Gold watch\\s*₹12,34,567/);
});

test("sends the right order to the server", async ({ page }) => {
  await logIn(page);
  await page.getByTestId("product").filter({ hasText: "Desk lamp" }).getByRole("button").click();
  const [request] = await Promise.all([
    page.waitForRequest("**/api/orders"),
    page.getByRole("button", { name: "Place order" }).click(),
  ]);
  expect(request.postDataJSON()).toEqual({ items: [3] });
  await expect(page.getByText("Order 1042 placed")).toBeVisible();
});
'''}), 'npx playwright test', 'Mock, break and spy on the network', show=['tests/network.spec.js'], replace=PW),
    'pw-pom': test(shop(4304, {
        'pages/shop.page.js': '''
import { expect } from "@playwright/test";

export class ShopPage {
  constructor(page) {
    this.page = page;
    this.products = page.getByTestId("product");
    this.cartCount = page.getByTestId("cart-count");
    this.total = page.locator("#total");
    this.placeOrder = page.getByRole("button", { name: "Place order" });
  }
  async open() {
    await this.page.goto("/");
  }
  async logIn(email, password) {
    await this.page.getByLabel("Email").fill(email);
    await this.page.getByLabel("Password").fill(password);
    await this.page.getByRole("button", { name: "Sign in" }).click();
    await expect(this.products.first()).toBeVisible();   // wait until the shop is ready
  }
  async add(name) {
    await this.products.filter({ hasText: name }).getByRole("button", { name: "Add to cart" }).click();
  }
}
''',
        'fixtures.js': '''
import { test as base } from "@playwright/test";
import { ShopPage } from "./pages/shop.page.js";

// A fixture builds what a test needs and hands it over as a parameter
export const test = base.extend({
  shop: async ({ page }, use) => {
    const shop = new ShopPage(page);
    await shop.open();
    await shop.logIn("asha@shop.example", "s3cret");
    await use(shop);                       // the test runs here
    // anything after use() is clean up
  },
});
export { expect } from "@playwright/test";
''',
        'tests/cart.spec.js': '''
import { test, expect } from "../fixtures.js";

test("one item", async ({ shop }) => {
  await shop.add("Gel pen");
  await expect(shop.total).toHaveText("₹20");
});

test("totals use Indian digit grouping", async ({ shop }) => {
  await shop.add("Desk lamp");
  await shop.add("Desk lamp");
  await expect(shop.cartCount).toHaveText("2");
  await expect(shop.total).toHaveText("₹2,598");
});

for (const [name, price] of [["Gel pen", "₹20"], ["Coffee mug", "₹199"], ["Desk lamp", "₹1,299"]]) {
  test(`price of ${name}`, async ({ shop }) => {
    await expect(shop.products.filter({ hasText: name }).locator(".price")).toHaveText(price);
  });
}
'''}), 'npx playwright test', 'Page objects and fixtures', show=['pages/shop.page.js', 'fixtures.js', 'tests/cart.spec.js'], replace=PW),
    'pw-flaky': test(shop(4305, {'tests/retry.spec.js': '''
import { test, expect } from "@playwright/test";

test("fails on the first try, passes on the retry", async ({ page }, testInfo) => {
  await page.goto("/");
  // Simulate a hiccup: the first attempt sees a different heading
  const expected = testInfo.retry === 0 ? "Demo Shop!" : "Demo Shop";
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(expected, { timeout: 1000 });
});
'''}, extra='\n  retries: 1,                       // try a failed test once more\n'), 'npx playwright test', 'Retries and flaky tests', show=['tests/retry.spec.js'],
        replace=PW + [(r'\n\s+Call log:[\s\S]*?(?=\n\s+\d+ \|)', '\n'), (r'\n\s+\d+ \|[\s\S]*?(?=\n\n)', ''), (r'\n\s+Retry #1[\s\S]*?(?=\n\n  1 flaky)', ''), (r'\n    \n', '\n')]),
    'pw-cli': show('''
npx playwright test                          # everything, headless
npx playwright test tests/cart.spec.js       # one file
npx playwright test -g "Indian digit"        # tests whose title matches
npx playwright test --grep @smoke            # tags in titles or { tag: "@smoke" }
npx playwright test --project=firefox        # one browser from the config
npx playwright test --headed --workers=1     # watch it in a real window
npx playwright test --debug                  # step through with the inspector
npx playwright test --ui                     # UI mode: time travel through each step
npx playwright test --last-failed            # only what failed last time
npx playwright test --repeat-each=20         # hunt for flakiness
npx playwright test --shard=2/4              # one quarter of the suite, for CI
npx playwright show-report                   # open the HTML report
npx playwright show-trace trace.zip          # open a recorded trace
npx playwright codegen http://localhost:4173 # record actions into code
''', 'Running Playwright in different ways', lang='bash', note='Reference'),
    'selenium': test({
        'package.json': pkg('shop-selenium', 'module', {'test': 'mocha --timeout 30000 "selenium/**/*.spec.js"'}),
        **SHOP_FILES,
        'selenium/driver.js': SELENIUM_DRIVER_ESM,
        'selenium/pages/ShopPage.js': '''
import { By, until } from "selenium-webdriver";

export class ShopPage {
  static EMAIL = By.name("email");
  static PASSWORD = By.name("password");
  static SIGN_IN = By.css("#login button");
  static ALERT = By.css("[role=alert]");
  static CART_COUNT = By.css("[data-testid=cart-count]");
  static TOTAL = By.id("total");
  static addButtonFor = name => By.xpath(`//li[h2='${name}']//button`);

  constructor(driver, baseUrl) {
    this.driver = driver;
    this.baseUrl = baseUrl;
  }
  async open() {
    await this.driver.get(this.baseUrl);
  }
  async logIn(email, password) {
    await this.driver.findElement(ShopPage.EMAIL).sendKeys(email);
    await this.driver.findElement(ShopPage.PASSWORD).sendKeys(password);
    await this.driver.findElement(ShopPage.SIGN_IN).click();
  }
  async add(name) {
    // Explicit wait: the products arrive after a delay
    const button = await this.driver.wait(until.elementLocated(ShopPage.addButtonFor(name)), 5000);
    await this.driver.wait(until.elementIsVisible(button), 5000);
    await button.click();
  }
  async cartCount(expected) {
    const el = await this.driver.findElement(ShopPage.CART_COUNT);
    await this.driver.wait(until.elementTextIs(el, expected), 5000);
    return el.getText();
  }
  async alertText() {
    const el = await this.driver.wait(until.elementLocated(ShopPage.ALERT), 5000);
    await this.driver.wait(until.elementIsVisible(el), 5000);
    return el.getText();
  }
}
''',
        'selenium/shop.spec.js': '''
import { expect } from "chai";
import { buildDriver } from "./driver.js";
import { ShopPage } from "./pages/ShopPage.js";
import { startShop } from "../server.js";

describe("demo shop with Selenium WebDriver", function () {
  let driver, server, shop;

  before(async () => {
    server = await startShop();                       // any free port
    driver = await buildDriver();
  });
  beforeEach(async () => {
    shop = new ShopPage(driver, `http://localhost:${server.address().port}`);
    await shop.open();
  });
  after(async () => {
    await driver?.quit();                             // always close the browser
    server?.close();
  });

  it("shows an error for a wrong password", async () => {
    await shop.logIn("asha@shop.example", "wrong");
    expect(await shop.alertText()).to.equal("Wrong email or password");
  });

  it("adds two products to the cart", async () => {
    await shop.logIn("asha@shop.example", "s3cret");
    await shop.add("Coffee mug");
    await shop.add("Desk lamp");
    expect(await shop.cartCount("2")).to.equal("2");
    expect(await driver.findElement(ShopPage.TOTAL).getText()).to.equal("₹1,498");
  });

  it("can read the page title and take a screenshot", async () => {
    expect(await driver.getTitle()).to.equal("Demo Shop");
    const png = await driver.takeScreenshot();         // base64 text of a PNG image
    expect(Buffer.from(png, "base64").subarray(1, 4).toString()).to.equal("PNG");
  });
});
''',
    }, 'npm test', 'Selenium WebDriver with Mocha, explicit waits and a page object', show=['selenium/driver.js', 'selenium/pages/ShopPage.js', 'selenium/shop.spec.js'], replace=MOCHA),
    'cypress': show('''
// cypress/e2e/shop.cy.js
describe("demo shop", () => {
  beforeEach(() => {
    cy.intercept("GET", "/api/products").as("products");   // watch the request
    cy.visit("/");
  });

  it("logs in and orders", () => {
    cy.get("input[name=email]").type("asha@shop.example");
    cy.get("input[name=password]").type("s3cret");
    cy.contains("button", "Sign in").click();
    cy.wait("@products").its("response.statusCode").should("eq", 200);

    cy.contains("[data-testid=product]", "Coffee mug").find("button").click();
    cy.get("[data-testid=cart-count]").should("have.text", "1");    // retries until true
    cy.contains("button", "Place order").click();
    cy.contains(/^Order \\d+ placed$/).should("be.visible");
  });

  it("shows a message when the API fails", () => {
    cy.intercept("GET", "/api/products", { statusCode: 503 });
    cy.login("asha@shop.example", "s3cret");                       // a custom command, see below
    cy.contains("Could not load products").should("be.visible");
  });
});

// cypress/support/commands.js
Cypress.Commands.add("login", (email, password) => {
  cy.get("input[name=email]").type(email);
  cy.get("input[name=password]").type(password);
  cy.contains("button", "Sign in").click();
});
''', 'The same tests in Cypress', note='Shown only: Cypress needs its own app download, which this page build cannot fetch',
        result='Run with npx cypress open (interactive) or npx cypress run (headless, for CI). Commands are queued and retried automatically, and are never awaited.'),
    'wdio': show('''
// test/specs/shop.e2e.js (WebdriverIO with Mocha)
import { browser, $, $$, expect } from "@wdio/globals";

describe("demo shop", () => {
  it("adds a product", async () => {
    await browser.url("/");
    await $("input[name=email]").setValue("asha@shop.example");
    await $("input[name=password]").setValue("s3cret");
    await $("button=Sign in").click();                          // button with this text
    await expect($$("[data-testid=product]")).toBeElementsArrayOfSize(3);
    await $("//li[h2='Gel pen']//button").click();
    await expect($("[data-testid=cart-count]")).toHaveText("1");
  });
});
// npx wdio run wdio.conf.js --spec test/specs/shop.e2e.js
''', 'The same test in WebdriverIO', note='Reference'),
    'ci': show('''
# .github/workflows/e2e.yml
name: e2e
on: [pull_request]
jobs:
  playwright:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with: { node-version: 24, cache: npm }
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test --shard=${{ matrix.shard }}/4
        env: { BASE_URL: "${{ vars.STAGING_URL }}" }
      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with: { name: "report-${{ matrix.shard }}", path: playwright-report/ }
''', 'Browser tests in CI', lang='yaml', note='Reference', result='Four machines each run a quarter of the suite. The HTML report, with traces of failed tests, is kept for every run.'),
}

PARTS = [
    part('tools', '🧭', 'The tools and how they drive a browser', '''
<p>A UI automation tool starts a real browser and acts like a user: it opens pages, types, clicks and reads what is shown. The four big JavaScript tools differ in how they talk to the browser, and that explains most of their strengths and limits.</p>
<div class="viz" data-viz="flow" data-k="drivers"></div>
<div class="tw"><table class="jt"><tr><th></th><th>Playwright</th><th>Selenium WebDriver</th><th>Cypress</th><th>WebdriverIO</th></tr>
<tr><td>Talks to the browser</td><td>its own protocol (CDP for Chromium, patched Firefox and WebKit)</td><td>W3C WebDriver through a driver program, BiDi coming</td><td>runs inside the browser next to your app</td><td>WebDriver or BiDi</td></tr>
<tr><td>Browsers</td><td>Chromium, Firefox, WebKit</td><td>every major browser, also real Safari and mobile through Appium</td><td>Chromium family, Firefox, WebKit (experimental)</td><td>all, plus mobile through Appium</td></tr>
<tr><td>Waiting</td><td>auto-waits for every action and assertion</td><td>explicit waits you write</td><td>retries commands and assertions</td><td>auto-waits on actions</td></tr>
<tr><td>Languages</td><td>JS, TS, Python, Java, .NET</td><td>JS, Java, Python, C#, Ruby</td><td>JS, TS</td><td>JS, TS</td></tr>
<tr><td>Async style</td><td><code>await</code> everything</td><td><code>await</code> everything</td><td>chained commands, no await</td><td><code>await</code> everything</td></tr>
<tr><td>Extras</td><td>API testing, traces, network mocking, parallel by default</td><td>Grid for many machines, the longest history</td><td>time travel debugger, network stubs</td><td>huge plugin set, mobile and desktop apps</td></tr>
</table></div>
<p>Every example below runs against the same small shop: a login form, a product list that arrives after 600 ms, a cart and an order button.</p>
[[shop-app]]
''', qa=['Playwright', 'Selenium', 'Cypress', 'WebdriverIO'], qa_why='Picking a tool and understanding how it reaches the browser is the first decision in every UI automation project.',
        kw=['UI automation', 'end to end', 'Playwright', 'Selenium', 'WebDriver', 'Cypress', 'WebdriverIO', 'CDP', 'BiDi', 'Appium', 'browser driver', 'tool comparison']),
    part('playwright', '🎭', 'Playwright: locators and web first assertions', '''
<p>A Playwright test receives a <code>page</code>, finds elements with <b>locators</b> and checks them with <b>web first assertions</b>. A locator is a recipe, not an element: it is looked up again on every use, so it never goes stale. Every action waits until the element is visible, enabled and not moving, and every <code>expect(locator)</code> retries until it passes or times out.</p>
[[pw-first]]
<p>The product list arrives after 600 ms, yet there is no sleep anywhere. <code>toHaveCount(3)</code> simply keeps checking. <code>filter({ hasText })</code> narrows a list to one card, and the button is found inside that card, which is far steadier than "the second button on the page".</p>
<div class="viz" data-viz="wait"></div>
<h3>Strict mode</h3>
<p>If a locator matches more than one element, an action or assertion fails instead of guessing. Here an <code>&lt;output&gt;</code> element also has the role <code>status</code>, which is easy to miss.</p>
[[pw-strict]]
<div class="tip">The error lists both matches and suggests a precise locator. Fix it by narrowing: <code>getByText(/^Order \\d+ placed$/)</code>, <code>getByRole("status").filter({ hasText: "Order" })</code> or a test id.</div>
''', qa=['Playwright'], qa_why='Locators and auto-waiting assertions are the core of every Playwright test.',
        kw=['Playwright', 'page', 'locator', 'getByRole', 'getByLabel', 'getByText', 'getByTestId', 'filter', 'hasText', 'expect', 'toHaveText', 'toHaveCount', 'toBeVisible', 'auto-waiting', 'strict mode', 'web first assertions']),
    part('network', '🛰️', 'Controlling the network', '''
<p>Playwright sees every request the page makes. <code>page.route</code> can answer a request with fake data or an error, so you can test states that are hard to produce for real: a broken API, an empty list, a very long name. <code>waitForRequest</code> and <code>waitForResponse</code> check what the page sends.</p>
[[pw-network]]
<div class="qa-box">Mocked tests check how the UI behaves, not whether the backend works. Keep a few tests that use the real API end to end, and use mocks for the error and edge cases. Cypress does the same with <code>cy.intercept</code>.</div>
''', qa=['Playwright', 'Cypress'], qa_why='Network mocking makes error states testable and UI tests independent of backend data.',
        kw=['page.route', 'route.fulfill', 'network mocking', 'waitForRequest', 'waitForResponse', 'postDataJSON', 'error state', 'cy.intercept', 'stub API']),
    part('framework', '🏗️', 'Page objects, fixtures and retries', '''
<p>As a suite grows, repeated steps move into <b>page objects</b> (chapter 8) and <b>fixtures</b>. A Playwright fixture prepares something a test needs, here a logged in shop, and passes it in as a parameter. Tests become short and read like a test case.</p>
[[pw-pom]]
<h3>Flaky tests and retries</h3>
<p>A <b>flaky</b> test passes and fails without any code change. Playwright can retry a failed test, and a test that fails and then passes is reported as <b>flaky</b>, not hidden as passed.</p>
[[pw-flaky]]
<div class="warn">Retries keep a pipeline green while you investigate, they are not a fix. With <code>trace: "on-first-retry"</code>, Playwright records a trace of the retry: every action, DOM snapshot, network call and console message, which usually shows the cause in minutes.</div>
[[pw-cli]]
''', qa=['Playwright'], qa_why='Fixtures, page objects and honest flaky reporting are what keep large UI suites maintainable.',
        kw=['page object', 'fixture', 'test.extend', 'use', 'retries', 'flaky', 'trace', 'testInfo.retry', 'grep', 'headed', 'debug', 'UI mode', 'codegen', 'shard', 'repeat-each']),
    part('selenium', '🚗', 'Selenium WebDriver', '''
<p><b>Selenium WebDriver</b> sends each command to a driver program (chromedriver, geckodriver, safaridriver), which controls the browser. Every call is a network round trip and returns a promise, so every line is awaited. Selenium does not wait for you: use <b>explicit waits</b> with <code>driver.wait(until...)</code> for anything that appears later.</p>
[[selenium]]
<div class="tw"><table class="jt"><tr><th>Need</th><th>Selenium</th></tr>
<tr><td>Find</td><td><code>By.id</code>, <code>By.css</code>, <code>By.xpath</code>, <code>By.name</code>, <code>By.linkText</code></td></tr>
<tr><td>Wait</td><td><code>until.elementLocated</code>, <code>elementIsVisible</code>, <code>elementTextIs</code>, <code>titleIs</code>, <code>urlContains</code></td></tr>
<tr><td>Act</td><td><code>click()</code>, <code>sendKeys()</code>, <code>clear()</code>, <code>driver.actions()</code> for hover and drag</td></tr>
<tr><td>Frames and windows</td><td><code>switchTo().frame()</code>, <code>switchTo().window()</code>, <code>switchTo().alert()</code></td></tr>
<tr><td>Many machines</td><td>Selenium Grid: <code>new Builder().usingServer(gridUrl)</code></td></tr>
</table></div>
<div class="warn">Avoid <code>driver.manage().setTimeouts({ implicit })</code> together with explicit waits. Mixing the two makes waits add up in surprising ways. Pick explicit waits.</div>
''', qa=['Selenium'], qa_why='Many enterprise suites are Selenium, and its explicit waits and locators are the base of every WebDriver tool.',
        kw=['Selenium', 'WebDriver', 'selenium-webdriver', 'chromedriver', 'By', 'xpath', 'css', 'driver.wait', 'until', 'explicit wait', 'implicit wait', 'sendKeys', 'Grid', 'Mocha', 'screenshot']),
    part('cypress', '🌲', 'Cypress and WebdriverIO', '''
<p><b>Cypress</b> runs inside the browser, in the same loop as your app. Commands such as <code>cy.get</code> are not promises: Cypress queues them and runs them in order, retrying each query and assertion until it passes. That is why you never write <code>await</code> in Cypress, and why plain variables do not hold element values (use <code>.then</code> or aliases).</p>
[[cypress]]
<p><b>WebdriverIO</b> is a WebDriver based framework with a friendlier API than raw Selenium, built in waiting, and support for mobile apps through Appium.</p>
[[wdio]]
''', qa=['Cypress', 'WebdriverIO'], qa_why='Cypress is widely used by front end teams and its command queue works differently from every other tool.',
        kw=['Cypress', 'cy.get', 'cy.contains', 'cy.intercept', 'cy.wait', 'alias', 'custom command', 'should', 'command queue', 'WebdriverIO', 'wdio', '$', '$$', 'Appium']),
    part('scenario', '🎬', 'Real world scenario: a UI suite in CI', '''
<div class="scenario"><b>The situation</b>The team wants every pull request checked by the browser suite in under ten minutes, with a report anyone can open when something fails.</div>
[[ci]]
<p>Sharding splits the tests across four machines. <code>fail-fast: false</code> lets every shard finish, so one failure does not hide others. The report is uploaded even when tests fail, and the traces inside it show exactly what the browser saw.</p>
<div class="qa-box">A healthy UI suite: tests independent of each other, data created through the API rather than the UI, stable locators, no fixed sleeps, network mocks only for edge cases, flaky tests tracked and fixed within days, and the slowest tests reviewed every sprint.</div>
''', qa=True, kw=['CI', 'GitHub Actions', 'shard', 'matrix', 'HTML report', 'trace', 'artifact', 'playwright install', 'pipeline', 'flaky tests', 'test strategy']),
]

DG = {
    'drivers': {'t': 'How each tool reaches the browser', 'w': 900, 'h': 320,
                'n': [['pw', 20, 20, 190, 56, 'Playwright test', {'c': 2}], ['se', 20, 130, 190, 56, 'Selenium test', {'c': 1}], ['cy', 20, 240, 190, 56, 'Cypress test', {'c': 3}],
                      ['cdp', 300, 20, 220, 56, 'CDP or Playwright protocol', {'c': 0, 'sh': 'pill', 'i': 'One fast, two way connection. Events such as network calls flow back to the test.'}],
                      ['drv', 300, 130, 220, 56, 'chromedriver', {'c': 0, 'sub': 'W3C WebDriver over HTTP', 'i': 'Each command is an HTTP request to the driver, which then controls the browser.'}],
                      ['inb', 300, 240, 220, 56, 'runs inside the page', {'c': 0, 'sh': 'pill', 'i': 'The test code is loaded into the browser next to the app.'}],
                      ['br', 640, 110, 230, 100, 'Browser', {'c': 4, 'sh': 'screen', 'sub': 'your web app'}]],
                'e': [['pw', 'cdp'], ['cdp', 'br'], ['se', 'drv'], ['drv', 'br'], ['cy', 'inb'], ['inb', 'br']],
                'st': [[['pw', 'cdp', 'br', 'pw>cdp', 'cdp>br'], 'Playwright keeps one connection open and hears every event, which makes auto-waiting and network control cheap.'],
                       [['se', 'drv', 'br', 'se>drv', 'drv>br'], 'Selenium sends standard WebDriver commands to a driver program. It works with every browser vendor, and each command is a round trip.'],
                       [['cy', 'inb', 'br', 'cy>inb', 'inb>br'], 'Cypress runs inside the browser itself, so it sees the app directly but lives within the browser\'s rules, for example one tab at a time.']]},
}

INFO = {'title': 'A robot user with a checklist', 'panels': [
    panel([['e', '🎯'], ['t', 'getByRole("button", { name })', {'b': 1, 'size': 11}]], 'Find', 'Locate elements like a user would.', 'Roles, labels and test ids, filtered to one card.'),
    panel([['e', '⏳'], ['t', 'await expect(...).toHaveText()', {'b': 1, 'size': 11}]], 'Wait', 'Retry until true, never sleep.', 'Selenium needs explicit waits, Playwright and Cypress retry for you.'),
    panel([['e', '🛰️'], ['t', 'page.route(...)', {'b': 1}]], 'Control', 'Mock the network for edge cases.', 'Errors, empty lists and huge values on demand.'),
    panel([['e', '📊'], ['t', 'trace + report', {'b': 1}]], 'Explain', 'Failures come with evidence.', 'Traces, screenshots and flaky reports in CI.')],
    'remember': 'Stable locators, assertions that wait, independent tests and evidence for every failure.'}

REAL = [
    ['🛒', 'Checkout guard', 'An online store runs 30 Playwright journeys on every pull request. A broken coupon field was caught before it cost a weekend of sales.'],
    ['🏦', 'A bank on Selenium', 'A bank keeps 2,000 Selenium tests on a Grid of Chrome, Firefox, Edge and Safari machines because its customers use all four.'],
    ['⚛️', 'A front end team', 'A React team writes Cypress tests next to its components and stubs every API with cy.intercept to test each state of the UI.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter automates a small shop with Playwright and Selenium, shows the same tests in Cypress and WebdriverIO, and covers locators, waits, network control, fixtures, retries and CI.',
        'यह अध्याय एक छोटी shop को Playwright और Selenium से automate करता है, वही tests Cypress और WebdriverIO में दिखाता है।',
        'ಈ ಅಧ್ಯಾಯ ಒಂದು ಚಿಕ್ಕ shop ಅನ್ನು Playwright ಮತ್ತು Selenium ಮೂಲಕ automate ಮಾಡುತ್ತದೆ, ಅದೇ tests Cypress ಮತ್ತು WebdriverIO ನಲ್ಲಿ ತೋರಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ ଏକ ଛୋଟ shop କୁ Playwright ଓ Selenium ରେ automate କରେ, ସେହି tests Cypress ଓ WebdriverIO ରେ ଦେଖାଏ।',
        'يؤتمت هذا الفصل متجرًا صغيرًا باستخدام Playwright وSelenium، ويعرض الاختبارات نفسها في Cypress وWebdriverIO.',
        'Dieses Kapitel automatisiert einen kleinen Shop mit Playwright und Selenium und zeigt dieselben Tests in Cypress und WebdriverIO.'),
    say('tools', 'The tools', 'Playwright talks to the browser over one fast connection, Selenium through a driver program, and Cypress runs inside the browser.',
        'Playwright एक तेज connection से browser से बात करता है, Selenium driver program से, और Cypress browser के अंदर चलता है।',
        'Playwright ಒಂದು ವೇಗದ connection ಮೂಲಕ, Selenium driver program ಮೂಲಕ browser ಜೊತೆ ಮಾತನಾಡುತ್ತವೆ, Cypress browser ಒಳಗೆ ಓಡುತ್ತದೆ.',
        'Playwright ଏକ ଦ୍ରୁତ connection ରେ, Selenium driver program ରେ browser ସହ କଥା ହୁଏ, ଏବଂ Cypress browser ଭିତରେ ଚାଲେ।',
        'يتصل Playwright بالمتصفح عبر اتصال سريع واحد، وSelenium عبر برنامج تشغيل، ويعمل Cypress داخل المتصفح.',
        'Playwright spricht über eine schnelle Verbindung mit dem Browser, Selenium über ein Treiberprogramm, Cypress läuft im Browser.'),
    say('playwright', 'Playwright', 'Locators are looked up again on every use, actions wait for the element, and assertions retry until they pass. Strict mode refuses ambiguous locators.',
        'Locators हर बार फिर से खोजे जाते हैं, actions element का इंतज़ार करते हैं, और assertions pass होने तक retry करते हैं।',
        'Locators ಪ್ರತಿ ಬಾರಿ ಮತ್ತೆ ಹುಡುಕಲ್ಪಡುತ್ತವೆ, actions element ಗಾಗಿ ಕಾಯುತ್ತವೆ, assertions pass ಆಗುವವರೆಗೆ retry ಮಾಡುತ್ತವೆ.',
        'Locators ପ୍ରତ୍ୟେକ ଥର ପୁଣି ଖୋଜାଯାଏ, actions element ପାଇଁ ଅପେକ୍ଷା କରନ୍ତି, assertions pass ପର୍ଯ୍ୟନ୍ତ retry କରନ୍ତି।',
        'يبحث عن المحددات من جديد في كل استخدام، وتنتظر الأفعال العنصر، وتعيد التأكيدات المحاولة حتى تنجح.',
        'Locators werden bei jeder Nutzung neu gesucht, Aktionen warten auf das Element, Assertions wiederholen bis zum Erfolg.'),
    say('network', 'Network', 'page route answers requests with fake data or errors, and wait for request checks what the page sends.',
        'page.route requests का जवाब नकली data या errors से देता है, और waitForRequest जांचता है कि page क्या भेजता है।',
        'page.route requests ಗೆ ನಕಲಿ data ಅಥವಾ errors ಉತ್ತರಿಸುತ್ತದೆ, waitForRequest page ಕಳುಹಿಸುವುದನ್ನು ಪರಿಶೀಲಿಸುತ್ತದೆ.',
        'page.route requests କୁ ନକଲି data କିମ୍ବା errors ରେ ଉତ୍ତର ଦିଏ, waitForRequest page ଯାହା ପଠାଏ ତାହା ଯାଞ୍ଚ କରେ।',
        'يجيب page.route الطلبات ببيانات مزيفة أو أخطاء، ويفحص waitForRequest ما ترسله الصفحة.',
        'page.route beantwortet Anfragen mit Schein-Daten oder Fehlern, waitForRequest prüft, was die Seite sendet.'),
    say('framework', 'Framework', 'Page objects hold the steps, fixtures prepare what a test needs, and retries report flaky tests honestly. Traces show the cause.',
        'Page objects steps रखते हैं, fixtures test की ज़रूरत तैयार करते हैं, और retries flaky tests को ईमानदारी से बताते हैं।',
        'Page objects steps ಇಡುತ್ತವೆ, fixtures test ಗೆ ಬೇಕಾದದ್ದನ್ನು ಸಿದ್ಧಪಡಿಸುತ್ತವೆ, retries flaky tests ಅನ್ನು ಪ್ರಾಮಾಣಿಕವಾಗಿ ತಿಳಿಸುತ್ತವೆ.',
        'Page objects steps ରଖନ୍ତି, fixtures test ର ଆବଶ୍ୟକତା ପ୍ରସ୍ତୁତ କରନ୍ତି, retries flaky tests କୁ ସଚ୍ଚୋଟ ଭାବେ ଜଣାନ୍ତି।',
        'تحفظ كائنات الصفحات الخطوات، وتجهز التجهيزات ما يحتاجه الاختبار، وتبلغ إعادة المحاولة عن الاختبارات المتقلبة بصدق.',
        'Page Objects halten die Schritte, Fixtures bereiten vor, Wiederholungen melden wackelige Tests ehrlich.'),
    say('selenium', 'Selenium', 'Selenium sends each command to a driver program. Await every call and use explicit waits for anything that appears later.',
        'Selenium हर command driver program को भेजता है। हर call को await करें और बाद में आने वाली चीज़ों के लिए explicit waits इस्तेमाल करें।',
        'Selenium ಪ್ರತಿ command ಅನ್ನು driver program ಗೆ ಕಳುಹಿಸುತ್ತದೆ. ಪ್ರತಿ call await ಮಾಡಿ, explicit waits ಬಳಸಿ.',
        'Selenium ପ୍ରତ୍ୟେକ command driver program କୁ ପଠାଏ। ପ୍ରତ୍ୟେକ call await କରନ୍ତୁ ଏବଂ explicit waits ବ୍ୟବହାର କରନ୍ତୁ।',
        'يرسل Selenium كل أمر إلى برنامج تشغيل. انتظر كل استدعاء واستخدم الانتظار الصريح لكل ما يظهر لاحقًا.',
        'Selenium schickt jeden Befehl an ein Treiberprogramm. Jeden Aufruf awaiten und explizite Wartezeiten nutzen.'),
    say('cypress', 'Cypress', 'Cypress queues commands and retries them inside the browser, so you never await them. WebdriverIO wraps WebDriver with built in waiting.',
        'Cypress commands को queue करता है और browser के अंदर retry करता है, इसलिए उन्हें कभी await न करें।',
        'Cypress commands ಅನ್ನು queue ಮಾಡಿ browser ಒಳಗೆ retry ಮಾಡುತ್ತದೆ, ಆದ್ದರಿಂದ ಅವನ್ನು await ಮಾಡಬೇಡಿ.',
        'Cypress commands କୁ queue କରି browser ଭିତରେ retry କରେ, ତେଣୁ ସେଗୁଡ଼ିକୁ await କରନ୍ତୁ ନାହିଁ।',
        'يضع Cypress الأوامر في طابور ويعيد محاولتها داخل المتصفح، فلا تنتظرها أبدًا. ويغلف WebdriverIO بروتوكول WebDriver مع انتظار مدمج.',
        'Cypress reiht Befehle ein und wiederholt sie im Browser, daher nie await. WebdriverIO umhüllt WebDriver mit eingebautem Warten.'),
    say('scenario', 'Scenario', 'Split the suite into shards across machines, let every shard finish, and keep the report and traces for every run.',
        'Suite को machines में shards में बांटें, हर shard पूरा होने दें, और हर run की report और traces रखें।',
        'Suite ಅನ್ನು machines ನಲ್ಲಿ shards ಆಗಿ ವಿಭಜಿಸಿ, ಪ್ರತಿ shard ಮುಗಿಯಲಿ, report ಮತ್ತು traces ಇಡಿ.',
        'Suite କୁ machines ରେ shards ରେ ବାଣ୍ଟନ୍ତୁ, ପ୍ରତ୍ୟେକ shard ଶେଷ ହେବାକୁ ଦିଅନ୍ତୁ, report ଓ traces ରଖନ୍ତୁ।',
        'قسّم المجموعة على الأجهزة، ودع كل جزء ينتهي، واحتفظ بالتقرير والآثار لكل تشغيل.',
        'Teile die Suite auf Maschinen auf, lass jeden Teil fertig laufen und behalte Bericht und Traces.'),
    say('practice', 'Hands-on', 'Practise choosing a locator, writing a wait helper, a locator filter and a flaky test detector.',
        'Locator चुनना, wait helper लिखना, locator filter और flaky test detector का अभ्यास करें।',
        'Locator ಆಯ್ಕೆ, wait helper, locator filter ಮತ್ತು flaky test detector ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Locator ବାଛିବା, wait helper, locator filter ଓ flaky test detector ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على اختيار المحدد وكتابة دالة انتظار ومرشح محددات وكاشف للاختبارات المتقلبة.',
        'Übe Locator-Wahl, einen Warte-Helfer, einen Locator-Filter und einen Erkenner für wackelige Tests.'),
]

QUIZ = [
    quiz('e', 'Which Playwright locator is preferred for a button labelled "Sign in"?', ['page.getByRole("button", { name: "Sign in" })', 'page.locator("form > button:nth-child(3)")', 'page.locator("//html/body/form/button")', 'page.locator(".btn")'], 0, 'What does a user see?', 'Role and accessible name survive layout and style changes.'),
    quiz('e', 'Which tool runs its test code inside the browser?', ['Cypress', 'Selenium', 'Playwright', 'WebdriverIO'], 0, 'Same loop as the app.', 'Cypress loads the test into the browser next to the application.'),
    quiz('e', 'What does await expect(locator).toHaveText("2") do when the text is still "1"?', ['Keeps retrying until it becomes "2" or times out', 'Fails at once', 'Waits a fixed 5 seconds', 'Throws a syntax error'], 0, 'Web first assertions.', 'It polls the page until the condition is met, up to the timeout.'),
    quiz('m', 'In Selenium, the product list appears after 600 ms. What should you use?', ['driver.wait(until.elementLocated(...))', 'A fixed sleep of 1 second', 'Nothing, Selenium waits by itself', 'driver.refresh()'], 0, 'Explicit waits.', 'Selenium does not auto-wait, so wait for the exact condition you need.'),
    quiz('m', 'What does strict mode in Playwright do?', ['Fails when a locator matches more than one element', 'Makes tests run slower', 'Turns on JavaScript strict mode', 'Blocks network calls'], 0, 'Ambiguity.', 'It refuses to guess which element you meant.'),
    quiz('m', 'Why use page.route in a UI test?', ['To return fake data or errors for edge cases', 'To change the page URL', 'To speed up the browser', 'To log in'], 0, 'Control the network.', 'It lets you test error and empty states without breaking the real backend.'),
    quiz('h', 'A Playwright test failed once, then passed on retry. How is it reported?', ['As flaky', 'As passed, with no trace', 'As failed', 'It is hidden'], 0, 'Honest reporting.', 'Playwright marks it flaky so the team can investigate.'),
    quiz('h', 'Why do you never write await before cy.get in Cypress?', ['Commands are queued, not promises', 'Cypress has no async code', 'await is slower', 'It is not allowed in JavaScript'], 0, 'Command queue.', 'Cypress schedules commands and runs them in order itself.'),
    quiz('h', 'What does a Playwright fixture defined with test.extend give a test?', ['A ready made object, such as a logged in page object, with clean up after', 'A faster browser', 'A mock server', 'Retries'], 0, 'Set up and tear down.', 'Code before use() prepares, code after use() cleans up.'),
    quiz('x', 'Why mix implicit and explicit waits in Selenium carefully?', ['Their timeouts can stack and make waits unpredictable', 'Implicit waits are deprecated', 'Explicit waits only work in Chrome', 'They cannot be mixed in JavaScript'], 0, 'Two waiting mechanisms.', 'The Selenium docs advise not to mix them because of unpredictable wait times.'),
    quiz('x', 'Which statement about locators in Playwright is true?', ['A locator is resolved again on every use, so it never goes stale', 'A locator holds one element forever', 'Locators only work with CSS', 'A locator throws if the element is not there yet'], 0, 'Recipe, not element.', 'This is why Playwright avoids the stale element errors common in Selenium.'),
    quiz('x', 'fail-fast: false in a CI matrix means?', ['Every shard runs to the end even if one fails', 'Tests never fail', 'The job retries forever', 'Shards share one machine'], 0, 'See all failures.', 'Otherwise one failing shard cancels the others and hides their results.'),
]

CALC = [
    calc('e', 'A suite has 240 UI tests of 30 seconds each. How many minutes does it take on one worker?', '120', 'Seconds to minutes.', ['<span class="eq">240 × 30 = 7200</span> s', '<span class="eq">7200 ÷ 60 = 120</span> min']),
    calc('e', 'The same suite split over 4 shards. How many minutes?', '30', 'Divide.', ['<span class="eq">120 ÷ 4 = 30</span>']),
    calc('m', 'Two Desk lamps at ₹1,299. What total should the cart show, without the symbol and commas?', '2598', 'Multiply.', ['<span class="eq">2 × 1299 = 2598</span>, shown as ₹2,598.']),
    calc('m', 'A fixed sleep of 3 s is used 50 times, but the page is ready after 0.8 s on average. How many seconds are wasted per run?', '110', 'Waste per sleep times count.', ['<span class="eq">3 − 0.8 = 2.2</span>', '<span class="eq">2.2 × 50 = 110</span>']),
    calc('h', 'A test passes 47 times out of 50 runs with --repeat-each=50. What is its failure rate in percent?', '6', '3 failures out of 50.', ['<span class="eq">3 ÷ 50 × 100 = 6</span>']),
    calc('h', 'With a failure rate of 6% per test and retries: 1, what is the chance a run still fails? Give the percent with one decimal.', '0.4', 'Both attempts must fail.', ['<span class="eq">0.06 × 0.06 = 0.0036</span>', 'That is 0.36%, about 0.4%.'], alt=['0.36']),
    calc('x', 'A suite has 200 tests, each with a 1% chance of a random failure. What is the chance, in percent rounded to a whole number, that at least one fails?', '87', 'One minus the chance that all pass.', ['<span class="eq">0.99<sup>200</sup> ≈ 0.134</span>', '<span class="eq">1 − 0.134 = 0.866</span>, about 87%.']),
    calc('x', 'Three projects (chromium, firefox, webkit) times 4 shards. How many CI jobs?', '12', 'Multiply.', ['<span class="eq">3 × 4 = 12</span>']),
]

EX = [
    ex('pick', 'e', 'Pick the best locator', '<p>Write <code>bestLocator(el)</code> for an element description like <code>{ role, name, testId, id, css }</code> (any may be missing). Return a Playwright locator string in this order of preference: <code>getByRole("role", { name: "name" })</code> when both role and name exist, then <code>getByTestId("x")</code>, then <code>locator("#id")</code>, then <code>locator("css")</code>.</p>',
       'function bestLocator(el) {\n  \n}\n',
       [('bestLocator({ role: "button", name: "Sign in", id: "go" })', 'getByRole("button", { name: "Sign in" })'), ('bestLocator({ role: "button", testId: "buy" })', 'getByTestId("buy")'),
        ('bestLocator({ id: "total", css: "output" })', 'locator("#total")'), ('bestLocator({ css: ".card .price" })', 'locator(".card .price")')],
       'function bestLocator(el) {\n  if (el.role && el.name) return `getByRole("${el.role}", { name: "${el.name}" })`;\n  if (el.testId) return `getByTestId("${el.testId}")`;\n  if (el.id) return `locator("#${el.id}")`;\n  return `locator("${el.css}")`;\n}',
       hint='A chain of <code>if</code> checks with early returns, most preferred first.', why='This is the order Playwright and Testing Library recommend, because it follows what users see.'),
    ex('wait', 'm', 'A waitFor helper', '<p>Write <code>async waitFor(check, { timeout = 1000, interval = 20 } = {})</code>. Call <code>check()</code> (it may be async) until it returns a truthy value, and return that value. If the timeout passes first, throw an Error with the message <code>"Timed out after 1000 ms"</code> (with the real timeout).</p>',
       'async function waitFor(check, { timeout = 1000, interval = 20 } = {}) {\n  \n}\n',
       [('(async () => { const start = Date.now(); return await waitFor(() => Date.now() - start > 100 && "ready"); })()', 'ready'),
        ('waitFor(() => false, { timeout: 100 }).catch(e => e.message)', 'Timed out after 100 ms')],
       'async function waitFor(check, { timeout = 1000, interval = 20 } = {}) {\n  const deadline = Date.now() + timeout;\n  while (Date.now() < deadline) {\n    const value = await check();\n    if (value) return value;\n    await new Promise(r => setTimeout(r, interval));\n  }\n  throw new Error(`Timed out after ${timeout} ms`);\n}',
       hint='A loop with a deadline, an <code>await</code> on the check and a short sleep between tries.', why='This is what <code>expect.poll</code>, Selenium waits and Cypress retries all do inside.'),
    ex('filter', 'h', 'filter({ hasText }) for cards', '<p>A page has product cards as objects <code>{ text, buttons }</code>. Write <code>filterCards(cards, hasText)</code> returning the cards whose text contains <code>hasText</code> (a string, case sensitive, or a RegExp). Then write <code>strictOne(list)</code> that returns the only item, or throws <code>"strict mode violation: N elements"</code> when the list does not have exactly one.</p>',
       'function filterCards(cards, hasText) {\n  \n}\n\nfunction strictOne(list) {\n  \n}\n',
       [('filterCards([{ text: "Gel pen ₹20" }, { text: "Coffee mug ₹199" }], "mug").length', 1), ('filterCards([{ text: "Gel pen" }, { text: "Fountain pen" }], /pen$/).length', 2),
        ('strictOne([{ text: "a" }]).text', 'a'), ('(() => { try { strictOne([1, 2]); } catch (e) { return e.message; } })()', 'strict mode violation: 2 elements')],
       'function filterCards(cards, hasText) {\n  return cards.filter(c => (hasText instanceof RegExp ? hasText.test(c.text) : c.text.includes(hasText)));\n}\n\nfunction strictOne(list) {\n  if (list.length !== 1) throw new Error(`strict mode violation: ${list.length} elements`);\n  return list[0];\n}',
       hint='<code>instanceof RegExp</code> tells the two kinds of filter apart.', why='Filtering, then insisting on exactly one match, is how Playwright keeps a test from clicking the wrong card.'),
    ex('flaky', 'x', 'Find the flaky tests', '<p>Write <code>flakyReport(runs)</code>. <code>runs</code> is a list of runs, each an object from test name to <code>"passed"</code> or <code>"failed"</code>. Return the names of tests that both passed and failed at least once, sorted, each with its failure rate in percent rounded to a whole number, like <code>"checkout (33%)"</code>.</p>',
       'function flakyReport(runs) {\n  \n}\n',
       [('flakyReport([{ login: "passed", checkout: "failed", search: "failed" }, { login: "passed", checkout: "passed", search: "failed" }, { login: "passed", checkout: "passed", search: "failed" }])', ['checkout (33%)']),
        ('flakyReport([{ a: "failed", b: "passed" }, { a: "passed", b: "failed" }])', ['a (50%)', 'b (50%)']), ('flakyReport([])', [])],
       'function flakyReport(runs) {\n  const stats = {};\n  for (const run of runs) {\n    for (const [name, status] of Object.entries(run)) {\n      stats[name] ??= { passed: 0, failed: 0 };\n      stats[name][status]++;\n    }\n  }\n  return Object.entries(stats)\n    .filter(([, s]) => s.passed > 0 && s.failed > 0)\n    .map(([name, s]) => `${name} (${Math.round((s.failed / (s.passed + s.failed)) * 100)}%)`)\n    .sort();\n}',
       hint='Count passes and failures per test first, then keep the ones with some of each.', why='A test that always fails is broken, not flaky. Only mixed results point at timing, data or environment problems.'),
]

T = {
    'slug': 'js-ui-automation', 'title': 'UI Automation: Playwright, Selenium, Cypress and WebdriverIO', 'short': 'UI automation', 'emoji': '🎭', 'module': MODULE, 'minutes': 26,
    'lead': 'Drive a real browser against a small demo shop. Playwright locators, auto-waiting assertions, strict mode, network mocking, page objects, fixtures and retries, all run for real, Selenium WebDriver with explicit waits and a page object, run for real in Chrome, plus the same tests in Cypress and WebdriverIO and a sharded CI set up.',
    'desc': 'Playwright, Selenium WebDriver, Cypress and WebdriverIO: locators, waits, strict mode, network mocking, page objects, fixtures, retries, flaky tests, traces and CI.',
    'summary': 'How each tool reaches the browser, a Playwright suite with role based locators and web first assertions, a strict mode failure, page.route for errors and fake data, waitForRequest, a page object with a fixture, retries that report flaky tests, the Playwright command line, Selenium WebDriver with Mocha, explicit waits, XPath and screenshots, the same tests in Cypress and WebdriverIO, and a sharded GitHub Actions workflow.',
    'keywords': ['UI automation', 'end to end', 'Playwright', 'Selenium', 'WebDriver', 'Cypress', 'WebdriverIO', 'locator', 'getByRole', 'auto-waiting', 'explicit wait', 'strict mode', 'page.route', 'cy.intercept', 'page object', 'fixture', 'retries', 'flaky', 'trace', 'shard', 'CI'],
    'qa_intro': 'The Playwright and Selenium tests on this page ran in a real Chromium against the demo shop when the page was built. Cypress is shown with the same tests so you can compare.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
