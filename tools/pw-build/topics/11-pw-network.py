from pkit import part, say, quiz, calc, panel, four, one, js, ts, py, jv, shown, table, tip, by

MODULE = ('🛰️', 'Network and APIs', 'pw-network', 'Watching, mocking and changing network traffic, testing APIs directly, and signing in once for the whole suite.')

JAVA_TRIM = [(r'(?ms)^\tat .*?(?=^\[INFO\]|^\[ERROR\]|\Z)', ''), (r'(?m)^\[ERROR\] (Please refer|To see the full|Re-run Maven|For more information|-> \[Help|\s*$).*\n?', ''),
             (r'(?m)^\[ERROR\] Failed to execute goal.*\n', ''), (r'(?ms)^\[INFO\] \n\[INFO\] Results:.*?(?=^\[ERROR\] Tests run:)', '')]

# ---------- watch the traffic ----------
WATCH_TS = '''import { test, expect } from '@playwright/test';

test('the products come from the API', async ({ page }) => {
  page.on('request', request => {
    if (request.url().includes('/api/')) console.log('>>', request.method(), new URL(request.url()).pathname);
  });
  page.on('response', response => {
    if (response.url().includes('/api/')) console.log('<<', response.status(), new URL(response.url()).pathname);
  });

  const productsCall = page.waitForResponse('**/api/products');   // start waiting before the page asks
  await page.goto('/products');
  const response = await productsCall;

  expect(response.ok()).toBeTruthy();
  const products = await response.json();
  console.log(`the API sent ${products.length} products`);
  await expect(page.getByRole('listitem')).toHaveCount(products.length);
});'''

WATCH_PY = '''from urllib.parse import urlparse
from playwright.sync_api import Page, Request, Response, expect


def show_request(request: Request):
    if "/api/" in request.url:
        print(">>", request.method, urlparse(request.url).path)


def show_response(response: Response):
    if "/api/" in response.url:
        print("<<", response.status, urlparse(response.url).path)


def test_the_products_come_from_the_api(page: Page):
    page.on("request", show_request)
    page.on("response", show_response)

    with page.expect_response("**/api/products") as products_call:   # wait while the page loads
        page.goto("/products")
    response = products_call.value

    assert response.ok
    products = response.json()
    print(f"the API sent {len(products)} products")
    expect(page.get_by_role("listitem")).to_have_count(len(products))'''

WATCH_JAVA = '''package com.brainy;

import com.google.gson.JsonParser;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Response;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;
import java.net.URI;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertTrue;

@UsePlaywright(ShopOptions.class)
public class WatchTest {
  @Test
  void theProductsComeFromTheApi(Page page) {
    page.onRequest(request -> {
      if (request.url().contains("/api/")) System.out.println(">> " + request.method() + " " + URI.create(request.url()).getPath());
    });
    page.onResponse(response -> {
      if (response.url().contains("/api/")) System.out.println("<< " + response.status() + " " + URI.create(response.url()).getPath());
    });

    // run the navigation, and wait for the products call it causes
    Response response = page.waitForResponse("**/api/products", () -> page.navigate("/products"));

    assertTrue(response.ok());
    int count = JsonParser.parseString(response.text()).getAsJsonArray().size();
    System.out.println("the API sent " + count + " products");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(count);
  }
}'''

# ---------- mock a response ----------
MOCK_TS = '''import { test, expect } from '@playwright/test';

test('shows the products the API sends', async ({ page }) => {
  await page.route('**/api/products', route => route.fulfill({
    json: [
      { id: 7, name: 'Tea kettle', price: 899, stock: 4, category: 'Kitchen' },
      { id: 8, name: 'Pencil box', price: 150, stock: 0, category: 'Stationery' },
    ],
  }));

  await page.goto('/products');
  await expect(page.getByRole('listitem')).toHaveCount(2);
  await expect(page.getByTestId('product-7')).toContainText('₹899');
  await expect(page.getByTestId('product-8').getByRole('button')).toHaveText('Out of stock');
});'''

MOCK_PY = '''from playwright.sync_api import Page, Route, expect

PRODUCTS = [
    {"id": 7, "name": "Tea kettle", "price": 899, "stock": 4, "category": "Kitchen"},
    {"id": 8, "name": "Pencil box", "price": 150, "stock": 0, "category": "Stationery"},
]


def test_shows_the_products_the_api_sends(page: Page):
    page.route("**/api/products", lambda route: route.fulfill(json=PRODUCTS))

    page.goto("/products")
    expect(page.get_by_role("listitem")).to_have_count(2)
    expect(page.get_by_test_id("product-7")).to_contain_text("₹899")
    expect(page.get_by_test_id("product-8").get_by_role("button")).to_have_text("Out of stock")'''

MOCK_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.Route;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class MockTest {
  static final String PRODUCTS = """
      [
        { "id": 7, "name": "Tea kettle", "price": 899, "stock": 4, "category": "Kitchen" },
        { "id": 8, "name": "Pencil box", "price": 150, "stock": 0, "category": "Stationery" }
      ]""";

  @Test
  void showsTheProductsTheApiSends(Page page) {
    page.route("**/api/products", route -> route.fulfill(new Route.FulfillOptions()
        .setContentType("application/json")
        .setBody(PRODUCTS)));

    page.navigate("/products");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(2);
    assertThat(page.getByTestId("product-7")).containsText("₹899");
    assertThat(page.getByTestId("product-8").getByRole(AriaRole.BUTTON)).hasText("Out of stock");
  }
}'''

# ---------- errors and failures ----------
ERR_TS = '''import { test, expect } from '@playwright/test';

const SORRY = 'Sorry, we could not load the products. Please try again.';

test('a server error shows a friendly message', async ({ page }) => {
  await page.route('**/api/products', route => route.fulfill({ status: 500, json: { error: 'Database is down' } }));
  await page.goto('/products');
  await expect(page.getByRole('alert')).toHaveText(SORRY);
});

test('a broken connection shows the same message', async ({ page }) => {
  await page.route('**/api/products', route => route.abort());
  await page.goto('/products');
  await expect(page.getByRole('alert')).toHaveText(SORRY);
});'''

ERR_PY = '''from playwright.sync_api import Page, expect

SORRY = "Sorry, we could not load the products. Please try again."


def test_a_server_error_shows_a_friendly_message(page: Page):
    page.route("**/api/products", lambda route: route.fulfill(status=500, json={"error": "Database is down"}))
    page.goto("/products")
    expect(page.get_by_role("alert")).to_have_text(SORRY)


def test_a_broken_connection_shows_the_same_message(page: Page):
    page.route("**/api/products", lambda route: route.abort())
    page.goto("/products")
    expect(page.get_by_role("alert")).to_have_text(SORRY)'''

ERR_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.Route;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class ErrorsTest {
  static final String SORRY = "Sorry, we could not load the products. Please try again.";

  @Test
  void aServerErrorShowsAFriendlyMessage(Page page) {
    page.route("**/api/products", route -> route.fulfill(new Route.FulfillOptions()
        .setStatus(500).setContentType("application/json").setBody("{\\"error\\": \\"Database is down\\"}")));
    page.navigate("/products");
    assertThat(page.getByRole(AriaRole.ALERT)).hasText(SORRY);
  }

  @Test
  void aBrokenConnectionShowsTheSameMessage(Page page) {
    page.route("**/api/products", route -> route.abort());
    page.navigate("/products");
    assertThat(page.getByRole(AriaRole.ALERT)).hasText(SORRY);
  }
}'''

# ---------- change a real response ----------
EDIT_TS = '''import { test, expect } from '@playwright/test';

test('the lamp shows as sold out', async ({ page }) => {
  await page.route('**/api/products', async route => {
    const response = await route.fetch();                  // ask the real server
    const products = await response.json();
    products.find(p => p.name === 'Desk lamp').stock = 0;  // then change one field
    await route.fulfill({ response, json: products });
  });

  await page.goto('/products');
  await expect(page.getByRole('listitem')).toHaveCount(5);   // the other products are real
  await expect(page.getByTestId('product-3').getByRole('button')).toHaveText('Out of stock');
});'''

EDIT_TS_TYPED = EDIT_TS.replace("products.find(p => p.name === 'Desk lamp').stock = 0;  // then change one field",
                                "products.find((p: { name: string }) => p.name === 'Desk lamp').stock = 0;  // then change one field")

EDIT_PY = '''from playwright.sync_api import Page, Route, expect


def sell_out_the_lamp(route: Route):
    response = route.fetch()                       # ask the real server
    products = response.json()
    for product in products:                       # then change one field
        if product["name"] == "Desk lamp":
            product["stock"] = 0
    route.fulfill(response=response, json=products)


def test_the_lamp_shows_as_sold_out(page: Page):
    page.route("**/api/products", sell_out_the_lamp)

    page.goto("/products")
    expect(page.get_by_role("listitem")).to_have_count(5)   # the other products are real
    expect(page.get_by_test_id("product-3").get_by_role("button")).to_have_text("Out of stock")'''

EDIT_JAVA = '''package com.brainy;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.microsoft.playwright.APIResponse;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Route;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class SoldOutTest {
  @Test
  void theLampShowsAsSoldOut(Page page) {
    page.route("**/api/products", route -> {
      APIResponse response = route.fetch();                    // ask the real server
      JsonArray products = JsonParser.parseString(response.text()).getAsJsonArray();
      for (JsonElement product : products) {                   // then change one field
        if (product.getAsJsonObject().get("name").getAsString().equals("Desk lamp"))
          product.getAsJsonObject().addProperty("stock", 0);
      }
      route.fulfill(new Route.FulfillOptions().setResponse(response).setBody(products.toString()));
    });

    page.navigate("/products");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(5);   // the other products are real
    assertThat(page.getByTestId("product-3").getByRole(AriaRole.BUTTON)).hasText("Out of stock");
  }
}'''

# ---------- HAR: record once, replay later ----------
HAR_TS = '''import { test, expect } from '@playwright/test';

test('record the products API', async ({ page }) => {
  await page.routeFromHAR('hars/products.har', { url: '**/api/products', update: true });
  await page.goto('/products');
  await expect(page.getByRole('listitem')).toHaveCount(5);
});

test('replay it from the file', async ({ page }) => {
  await page.routeFromHAR('hars/products.har', { url: '**/api/products' });   // no update: answers come from the file
  await page.goto('/products');
  await expect(page.getByRole('listitem')).toHaveCount(5);
});'''

HAR_PY = '''from playwright.sync_api import Page, expect


def test_record_the_products_api(page: Page):
    page.route_from_har("hars/products.har", url="**/api/products", update=True)
    page.goto("/products")
    expect(page.get_by_role("listitem")).to_have_count(5)


def test_replay_it_from_the_file(page: Page):
    page.route_from_har("hars/products.har", url="**/api/products")   # no update: answers come from the file
    page.goto("/products")
    expect(page.get_by_role("listitem")).to_have_count(5)'''

HAR_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.*;
import java.nio.file.Paths;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class HarTest {
  @Test
  @Order(1)
  void recordTheProductsApi(Page page) {
    page.routeFromHAR(Paths.get("hars/products.har"), new Page.RouteFromHAROptions().setUrl("**/api/products").setUpdate(true));
    page.navigate("/products");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(5);
  }

  @Test
  @Order(2)
  void replayItFromTheFile(Page page) {
    // no update: answers come from the file
    page.routeFromHAR(Paths.get("hars/products.har"), new Page.RouteFromHAROptions().setUrl("**/api/products"));
    page.navigate("/products");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(5);
  }
}'''

# ---------- WebSockets ----------
WS_TS = '''import { test, expect } from '@playwright/test';

test('shows the live stock from the server', async ({ page }) => {
  await page.goto('/widgets');
  await expect(page.getByTestId('live-stock')).toHaveText('Desk lamp: 8 left');
});

test('a mocked feed says the lamp sold out', async ({ page }) => {
  await page.routeWebSocket('**/ws/stock', ws => {          // no real server is contacted
    ws.onMessage(message => {
      if (message === 'subscribe')
        ws.send(JSON.stringify({ product: 'Desk lamp', left: 0 }));
    });
  });
  await page.goto('/widgets');
  await expect(page.getByTestId('live-stock')).toHaveText('Desk lamp: sold out');
});'''

WS_PY = '''import json
from playwright.sync_api import Page, WebSocketRoute, expect


def test_shows_the_live_stock_from_the_server(page: Page):
    page.goto("/widgets")
    expect(page.get_by_test_id("live-stock")).to_have_text("Desk lamp: 8 left")


def answer(ws: WebSocketRoute, message):
    if message == "subscribe":
        ws.send(json.dumps({"product": "Desk lamp", "left": 0}))


def test_a_mocked_feed_says_the_lamp_sold_out(page: Page):
    # no real server is contacted
    page.route_web_socket("**/ws/stock", lambda ws: ws.on_message(lambda message: answer(ws, message)))
    page.goto("/widgets")
    expect(page.get_by_test_id("live-stock")).to_have_text("Desk lamp: sold out")'''

WS_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class LiveStockTest {
  @Test
  void showsTheLiveStockFromTheServer(Page page) {
    page.navigate("/widgets");
    assertThat(page.getByTestId("live-stock")).hasText("Desk lamp: 8 left");
  }

  @Test
  void aMockedFeedSaysTheLampSoldOut(Page page) {
    page.routeWebSocket("**/ws/stock", ws -> {               // no real server is contacted
      ws.onMessage(frame -> {
        if ("subscribe".equals(frame.text()))
          ws.send("{\\"product\\": \\"Desk lamp\\", \\"left\\": 0}");
      });
    });
    page.navigate("/widgets");
    assertThat(page.getByTestId("live-stock")).hasText("Desk lamp: sold out");
  }
}'''

CODES = {
    'watch': four('Listen to the traffic and wait for one response',
                  java=jv({'WatchTest.java': WATCH_JAVA}),
                  py=py({'test_watch.py': WATCH_PY}, cmd='pytest -s -q'),
                  js=js({'watch.spec.js': WATCH_TS}),
                  ts=ts({'watch.spec.ts': WATCH_TS}),
                  result='Every API call of the page was printed as it went out and came back. The test also waited for the one response it cared about, read its JSON, and checked that the page shows as many products as the API sent. Start waiting before the action that causes the request, or the response may arrive before you listen.'),
    'mock': four('Answer the products API with your own data',
                 java=jv({'MockTest.java': MOCK_JAVA}),
                 py=py({'test_mock.py': MOCK_PY}),
                 js=js({'mock.spec.js': MOCK_TS}),
                 ts=ts({'mock.spec.ts': MOCK_TS}),
                 result='The page showed two products that do not exist on the server. The request never left the browser: route.fulfill answered it. Java has no json option on fulfill, so it sets the body and the content type itself.'),
    'errors': four('Make the API fail, and check the page copes',
                   java=jv({'ErrorsTest.java': ERR_JAVA}),
                   py=py({'test_errors.py': ERR_PY}),
                   js=js({'errors.spec.js': ERR_TS}),
                   ts=ts({'errors.spec.ts': ERR_TS}),
                   result='A 500 answer and a broken connection both led to the same friendly message. These cases are hard to produce with a real server, and with route they take one line each.'),
    'edit': four('Keep the real answer, change one field',
                 java=jv({'SoldOutTest.java': EDIT_JAVA}),
                 py=py({'test_sold_out.py': EDIT_PY}),
                 js=js({'sold-out.spec.js': EDIT_TS}),
                 ts=ts({'sold-out.spec.ts': EDIT_TS_TYPED}),
                 result='route.fetch sent the request to the real server, the handler changed the stock of the lamp to 0, and route.fulfill passed the changed answer on. Four products are exactly as the server sent them, and only the lamp is sold out.'),
    'har': four('Record the API into a HAR file, then replay it',
                java=jv({'HarTest.java': HAR_JAVA}, cmd='mvn test && ls -1 hars'),
                py=py({'test_har.py': HAR_PY}, cmd='pytest -v && ls hars'),
                js=js({'har.spec.js': HAR_TS}, cmd='npx playwright test && ls hars'),
                ts=ts({'har.spec.ts': HAR_TS}, cmd='npx playwright test && ls hars'),
                result='The first test called the real API and saved the answer into hars/products.har. The ls at the end shows the HAR file and a second file with the response body, named by a hash, which you can edit by hand. The second test was answered from those files, and it was faster, because the file answers at once while the real API waits 600 ms. Commit the folder, and the tests no longer depend on the live API.'),
    'ws': four('Mock a WebSocket feed',
               java=jv({'LiveStockTest.java': WS_JAVA}),
               py=py({'test_live_stock.py': WS_PY}),
               js=js({'live-stock.spec.js': WS_TS}),
               ts=ts({'live-stock.spec.ts': WS_TS}),
               result='The first test read the real feed: 8 lamps left. In the second, routeWebSocket took the place of the server. When the page sent subscribe, the handler answered with 0, and the page said sold out. To keep the real server and only change some messages, call connectToServer in the handler.'),
}

DG = {
    'route': {'t': 'Where page.route sits', 'w': 900, 'h': 230,
              'n': [['pg', 20, 83, 140, 64, 'the page', {'c': 5, 'sub': "fetch('/api/products')", 'i': 'The shop page asks for the products, as it always does.'}],
                    ['rt', 220, 83, 150, 64, 'page.route', {'c': 2, 'sub': 'your handler', 'i': 'Playwright catches every request that matches the pattern and calls your handler.'}],
                    ['ff', 440, 10, 170, 64, 'route.fulfill', {'c': 1, 'sub': 'answer it yourself', 'i': 'The handler answers with your data. The server never sees the request.'}],
                    ['ab', 440, 156, 170, 64, 'route.abort', {'c': 3, 'sub': 'fail the request', 'i': 'The request fails as if the network were down.'}],
                    ['ct', 440, 83, 170, 64, 'route.continue', {'c': 0, 'sub': 'let it through', 'i': 'The request goes on to the server, changed or not.'}],
                    ['sv', 680, 83, 200, 64, 'the server', {'c': 4, 'sub': 'or route.fetch first', 'i': 'With continue or fetch, the real server answers. fetch lets you change the answer before the page sees it.'}]],
              'e': [['pg', 'rt'], ['rt', 'ff'], ['rt', 'ab'], ['rt', 'ct'], ['ct', 'sv']],
              'st': [[['pg'], 'The page makes a request.'],
                     [['rt', 'pg>rt'], 'A matching route catches it before it leaves the browser.'],
                     [['ff', 'rt>ff'], 'Fulfill answers with your own data.'],
                     [['ab', 'rt>ab'], 'Abort makes it fail.'],
                     [['ct', 'sv', 'rt>ct', 'ct>sv'], 'Continue, or fetch, lets the real server answer.']]},
}

PARTS = [
    part('watch', '👀', 'Watch the traffic', f'''
<p>A page talks to its server all the time. Playwright lets a test listen to every request and response, or wait for one in particular. This is how you check that the right call was made, or read the data the page received.</p>
[[watch]]
{table(['To', 'Playwright Test', 'Python', 'Java'], [
    ['log every request', "page.on('request', ...)", 'page.on("request", ...)', 'page.onRequest(...)'],
    ['log every response', "page.on('response', ...)", 'page.on("response", ...)', 'page.onResponse(...)'],
    ['wait for one response', "page.waitForResponse('**/api/products')", 'with page.expect_response(...)', 'page.waitForResponse(..., () -> action)'],
    ['wait for one request', 'page.waitForRequest(...)', 'with page.expect_request(...)', 'page.waitForRequest(..., () -> action)'],
    ['see failed requests', "page.on('requestfailed', ...)", 'page.on("requestfailed", ...)', 'page.onRequestFailed(...)'],
])}
''', easy=True, kw=['network', 'request', 'response', 'waitForResponse', 'expect_response', 'onRequest', 'events']),

    part('mock', '🎭', 'Mock an API', f'''
<p><b>Mocking</b> means answering a request with data you choose, instead of the real server. It lets you test pages whose data you cannot control: an empty list, a product that costs ₹0, a name with 200 letters.</p>
<div class="viz" data-viz="flow" data-k="route"></div>
[[mock]]
{tip('The pattern in page.route is a glob: ** matches any part of the address, including slashes, and * matches any part between two slashes. A regular expression works too. Routes added with context.route catch requests from every page of the context, including new tabs.', 'tip')}
''', easy=True, kw=['mock', 'route', 'fulfill', 'json', 'glob', 'context.route']),

    part('errors', '💥', 'Errors that are hard to cause', f'''
<p>What does the shop do when the server answers 500, or the network drops? With a real server, that is hard to arrange. With route it is one line.</p>
[[errors]]
{tip("Routes can also make tests faster. page.route('**/*.{png,jpg,jpeg}', route => route.abort()) stops images from loading in tests that do not need them.", 'pro')}
''', kw=['error', '500', 'abort', 'offline', 'friendly message']),

    part('edit', '✏️', 'Change a real response', f'''
<p>Sometimes you want almost everything real, with one field changed. route.fetch sends the request to the real server and gives you its answer, which you change before the page sees it.</p>
[[edit]]
{tip('route.continue can change the request on its way out instead: a different header, method or body. For example, route.continue({ headers: { ...route.request().headers(), "x-test": "yes" } }).', 'tip')}
''', kw=['route.fetch', 'modify response', 'continue', 'headers']),

    part('har', '📼', 'Record and replay with HAR', f'''
<p>A <b>HAR</b> file (HTTP Archive) is a recording of network traffic. Playwright can record the answers of an API into a HAR file once, and replay them in later runs. Tests then get the same data every time, even when the real API changes or is down.</p>
[[har]]
{table(['Step', 'What you write'], [
    ['record', 'routeFromHAR(file, { url, update: true }) and run the test once'],
    ['edit', 'change the JSON in the body file next to the HAR, if you want different data'],
    ['replay', 'routeFromHAR(file, { url }) without update'],
    ['refresh', 'run once more with update: true when the API changes'],
])}
{tip('Replay matches the address and the method exactly, and for POST also the body. A request that matches nothing in the file is aborted, unless you pass notFound: fallback.', 'warn')}
''', kw=['HAR', 'routeFromHAR', 'record', 'replay', 'update', 'notFound']),

    part('websocket', '🔌', 'WebSockets', f'''
<p>A <b>WebSocket</b> is a connection that stays open, so the server can send messages at any time, like the live stock on the widgets page. routeWebSocket lets a test act as the server.</p>
[[ws]]
''', kw=['WebSocket', 'routeWebSocket', 'onMessage', 'connectToServer', 'live']),
]

INFO = {'title': 'You control the network', 'panels': [
    panel([['e', '👀'], ['t', 'waitForResponse', {'b': 1}]], 'Watch', 'See every call.', 'Wait for the one you need.'),
    panel([['e', '🎭'], ['t', 'fulfill', {'b': 1}]], 'Mock', 'Answer with your data.', 'No server needed.'),
    panel([['e', '✏️'], ['t', 'fetch', {'b': 1}]], 'Change', 'Real answer, one field changed.', 'The rest stays real.'),
    panel([['e', '📼'], ['t', 'HAR', {'b': 1}]], 'Replay', 'Record once.', 'Same data every run.')],
    'remember': 'Mock what you do not own or cannot control. Keep a few tests against the real API, so the mocks do not drift away from it.'}

REAL = [
    ['💳', 'The payment provider that is never down in tests', 'A shop mocks the answers of its payment provider: approved, declined and timed out. Each case takes one route, and no test charges a real card.'],
    ['📉', 'The empty state nobody had seen', 'A dashboard team mocks an empty list and finds that the page shows a spinner forever instead of a message. Real data had always been there, so the bug had stayed hidden.'],
    ['📼', 'A demo that never changes', 'A team records the answers of a slow partner API into HAR files. Their tests run in seconds and stay green on days when the partner is down.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter is about the network: listening to requests, answering them with your own data, making them fail, changing real answers, recording them into HAR files, and mocking WebSockets.',
        'यह अध्याय network के बारे में है: requests सुनना, उन्हें अपने data से जवाब देना, उन्हें fail करना, असली जवाब बदलना, उन्हें HAR files में record करना, और WebSockets को mock करना।',
        'ಈ ಅಧ್ಯಾಯ network ಬಗ್ಗೆ: requests ಕೇಳುವುದು, ನಿಮ್ಮ data ದಿಂದ ಉತ್ತರಿಸುವುದು, fail ಮಾಡುವುದು, ನಿಜವಾದ ಉತ್ತರ ಬದಲಿಸುವುದು, HAR files ಗೆ record ಮಾಡುವುದು ಮತ್ತು WebSockets mock ಮಾಡುವುದು.',
        'ଏହି ଅଧ୍ୟାୟ network ବିଷୟରେ: requests ଶୁଣିବା, ନିଜ data ରେ ଉତ୍ତର ଦେବା, fail କରିବା, ପ୍ରକୃତ ଉତ୍ତର ବଦଳାଇବା, HAR files ରେ record କରିବା ଏବଂ WebSockets mock କରିବା।',
        'يتناول هذا الفصل الشبكة: الاستماع إلى الطلبات، والرد عليها ببياناتك، وجعلها تفشل، وتعديل الردود الحقيقية، وتسجيلها في ملفات HAR، ومحاكاة WebSockets.',
        'In diesem Kapitel geht es um das Netzwerk: Anfragen mithören, sie mit eigenen Daten beantworten, sie scheitern lassen, echte Antworten ändern, sie in HAR-Dateien aufnehmen und WebSockets simulieren.'),
    say('watch', 'Watch the traffic', 'page.on request and response let you see every call. waitForResponse waits for one call. Start waiting before the action that causes it.',
        'page.on request और response से आप हर call देख सकते हैं। waitForResponse एक call का इंतज़ार करता है। उसे पैदा करने वाले action से पहले इंतज़ार शुरू करें।',
        'page.on request ಮತ್ತು response ಮೂಲಕ ಪ್ರತಿ call ನೋಡಬಹುದು. waitForResponse ಒಂದು call ಗಾಗಿ ಕಾಯುತ್ತದೆ. ಅದನ್ನು ಉಂಟುಮಾಡುವ action ಗಿಂತ ಮೊದಲು ಕಾಯಲು ಶುರುಮಾಡಿ.',
        'page.on request ଓ response ରେ ପ୍ରତି call ଦେଖିହେବ। waitForResponse ଗୋଟିଏ call ପାଇଁ ଅପେକ୍ଷା କରେ। ତାକୁ ସୃଷ୍ଟି କରୁଥିବା action ପୂର୍ବରୁ ଅପେକ୍ଷା ଆରମ୍ଭ କରନ୍ତୁ।',
        'يتيح page.on للطلبات والردود رؤية كل اتصال. ينتظر waitForResponse اتصالًا واحدًا. ابدأ الانتظار قبل الفعل الذي يسببه.',
        'Mit page.on für request und response siehst du jeden Aufruf. waitForResponse wartet auf einen bestimmten. Beginne zu warten, bevor die Aktion ihn auslöst.'),
    say('mock', 'Mock an API', 'page.route catches requests that match a pattern. route.fulfill answers them with your own data, so the server never sees them.',
        'page.route pattern से मिलती requests पकड़ता है। route.fulfill उन्हें आपके data से जवाब देता है, इसलिए server उन्हें कभी नहीं देखता।',
        'page.route pattern ಗೆ ಹೊಂದುವ requests ಹಿಡಿಯುತ್ತದೆ. route.fulfill ನಿಮ್ಮ data ದಿಂದ ಉತ್ತರಿಸುತ್ತದೆ, ಹಾಗಾಗಿ server ಅವುಗಳನ್ನು ನೋಡುವುದೇ ಇಲ್ಲ.',
        'page.route pattern ସହ ମେଳ ଖାଉଥିବା requests ଧରେ। route.fulfill ନିଜ data ରେ ଉତ୍ତର ଦିଏ, ତେଣୁ server ସେଗୁଡିକୁ କେବେ ଦେଖେ ନାହିଁ।',
        'يلتقط page.route الطلبات المطابقة لنمط. ويرد عليها route.fulfill ببياناتك، فلا يراها الخادم أبدًا.',
        'page.route fängt Anfragen ab, die zu einem Muster passen. route.fulfill beantwortet sie mit eigenen Daten, sodass der Server sie nie sieht.'),
    say('errors', 'Errors', 'A status of 500 or route.abort makes a request fail on purpose, so you can check the friendly message the page shows.',
        'Status 500 या route.abort request को जानबूझकर fail करता है, ताकि आप page का friendly message जाँच सकें।',
        'Status 500 ಅಥವಾ route.abort request ಅನ್ನು ಉದ್ದೇಶಪೂರ್ವಕ fail ಮಾಡುತ್ತದೆ, ಆಗ page ತೋರಿಸುವ friendly message ಪರಿಶೀಲಿಸಬಹುದು.',
        'Status 500 ବା route.abort request କୁ ଜାଣିଶୁଣି fail କରେ, ଯାହାଦ୍ୱାରା page ର friendly message ଯାଞ୍ଚ କରିହେବ।',
        'تجعل الحالة 500 أو route.abort الطلب يفشل عمدًا، فتتحقق من الرسالة الودية التي تعرضها الصفحة.',
        'Ein Status 500 oder route.abort lässt eine Anfrage absichtlich scheitern, damit du die freundliche Meldung der Seite prüfen kannst.'),
    say('edit', 'Change a real response', 'route.fetch gets the real answer. Change what you need, then pass it on with route.fulfill.',
        'route.fetch असली जवाब लाता है। जो चाहिए वह बदलें, फिर route.fulfill से आगे भेजें।',
        'route.fetch ನಿಜವಾದ ಉತ್ತರ ತರುತ್ತದೆ. ಬೇಕಾದ್ದನ್ನು ಬದಲಿಸಿ, ನಂತರ route.fulfill ಮೂಲಕ ಮುಂದೆ ಕಳುಹಿಸಿ.',
        'route.fetch ପ୍ରକୃତ ଉତ୍ତର ଆଣେ। ଦରକାରୀ ବଦଳାନ୍ତୁ, ତାପରେ route.fulfill ରେ ଆଗକୁ ପଠାନ୍ତୁ।',
        'يجلب route.fetch الرد الحقيقي. غيّر ما تحتاجه ثم مرّره عبر route.fulfill.',
        'route.fetch holt die echte Antwort. Ändere, was du brauchst, und gib sie mit route.fulfill weiter.'),
    say('har', 'HAR files', 'routeFromHAR with update records the API into a file. Without update it replays the file, so tests get the same data every run.',
        'update के साथ routeFromHAR API को file में record करता है। update के बिना वह file replay करता है, जिससे tests को हर run में वही data मिलता है।',
        'update ಜೊತೆ routeFromHAR API ಅನ್ನು file ಗೆ record ಮಾಡುತ್ತದೆ. update ಇಲ್ಲದೆ file replay ಮಾಡುತ್ತದೆ, ಆಗ tests ಪ್ರತಿ run ನಲ್ಲಿ ಅದೇ data ಪಡೆಯುತ್ತವೆ.',
        'update ସହ routeFromHAR API କୁ file ରେ record କରେ। update ବିନା ଏହା file replay କରେ, ତେଣୁ tests ପ୍ରତି run ରେ ସେହି data ପାଆନ୍ତି।',
        'يسجّل routeFromHAR مع update واجهة API في ملف. وبدون update يعيد تشغيل الملف، فتحصل الاختبارات على البيانات نفسها في كل تشغيل.',
        'routeFromHAR mit update nimmt die API in eine Datei auf. Ohne update spielt es die Datei ab, sodass Tests bei jedem Lauf dieselben Daten bekommen.'),
    say('websocket', 'WebSockets', 'routeWebSocket lets the test act as the WebSocket server. The handler reads what the page sends and answers with its own messages.',
        'routeWebSocket से test WebSocket server की तरह काम करता है। handler page का भेजा पढ़ता है और अपने messages से जवाब देता है।',
        'routeWebSocket ಮೂಲಕ test WebSocket server ಆಗಿ ಕೆಲಸ ಮಾಡುತ್ತದೆ. handler page ಕಳುಹಿಸಿದ್ದನ್ನು ಓದಿ ತನ್ನ messages ನಿಂದ ಉತ್ತರಿಸುತ್ತದೆ.',
        'routeWebSocket ରେ test WebSocket server ଭାବେ କାମ କରେ। handler page ପଠାଇଥିବା ପଢେ ଏବଂ ନିଜ messages ରେ ଉତ୍ତର ଦିଏ।',
        'يتيح routeWebSocket للاختبار أن يعمل كخادم WebSocket. يقرأ المعالج ما ترسله الصفحة ويرد برسائله.',
        'Mit routeWebSocket spielt der Test den WebSocket-Server. Der Handler liest, was die Seite sendet, und antwortet mit eigenen Nachrichten.'),
    say('practice', 'Playground labs', 'In the labs you mock an empty product list, and then make the products API fail with status 503.',
        'Labs में आप खाली product list mock करते हैं, फिर products API को status 503 से fail करते हैं।',
        'Labs ನಲ್ಲಿ ಖಾಲಿ product list mock ಮಾಡುತ್ತೀರಿ, ನಂತರ products API ಅನ್ನು status 503 ಮೂಲಕ fail ಮಾಡುತ್ತೀರಿ.',
        'Labs ରେ ଆପଣ ଖାଲି product list mock କରନ୍ତି, ତାପରେ products API କୁ status 503 ରେ fail କରନ୍ତି।',
        'في المختبرات تحاكي قائمة منتجات فارغة، ثم تجعل واجهة المنتجات تفشل بالحالة 503.',
        'In den Labs simulierst du eine leere Produktliste und lässt dann die Produkt-API mit Status 503 scheitern.'),
]

QUIZ = [
    quiz(1, 'Which method answers a caught request with your own data?', ['route.continue', 'route.fulfill', 'route.abort', 'route.fetch'], 1,
         'Fulfil means to complete.', 'route.fulfill sends your status, headers and body back to the page.'),
    quiz(1, 'What does route.abort do?', ['skips the test', 'makes the request fail', 'closes the page', 'waits longer'], 1,
         'As if the network broke.', 'The request fails, as if the connection were lost.'),
    quiz(1, 'What is a HAR file?', ['a test report', 'a recording of network traffic', 'a browser binary', 'a config file'], 1,
         'HTTP Archive.', 'A HAR file records requests and responses so they can be replayed.'),
    quiz(1, "Which pattern matches http://localhost:4173/api/products?", ["'/products'", "'**/api/products'", "'*api'", "'api/*/products'"], 1,
         '** matches any part, slashes too.', "'**/api/products' matches that address on any host."),
    quiz(2, 'Why start waitForResponse before page.goto?', ['it is faster', 'the response might arrive before you start listening', 'goto needs it', 'it is required in TypeScript'], 1,
         'Think about timing.', 'If you start listening after the action, the response may already be gone.'),
    quiz(2, 'How do you change one field of the real answer?', ['route.continue with a body', 'route.fetch, change it, route.fulfill', 'route.abort', 'edit the server'], 1,
         'Get it first, then pass it on.', 'fetch gets the real answer, you change it, and fulfill passes it to the page.'),
    quiz(2, 'Which option does the Java fulfill lack, compared with JavaScript and Python?', ['status', 'json', 'body', 'contentType'], 1,
         'Look at the Java mock example.', 'Java sets the body and the content type itself.'),
    quiz(2, 'Which route catches requests from every tab of a context?', ['page.route', 'context.route', 'browser.route', 'test.route'], 1,
         'Context means all its pages.', 'context.route applies to every page in the context, including new tabs.'),
    quiz(2, 'What does update: true do in routeFromHAR?', ['replays the file', 'records real answers into the file', 'deletes the file', 'updates Playwright'], 1,
         'It writes the file.', 'With update the real API is called and the file is written. Without it the file is replayed.'),
    quiz(3, 'During HAR replay, a request matches nothing in the file. What happens by default?', ['it goes to the server', 'it is aborted', 'the test is skipped', 'it waits forever'], 1,
         'Read the HAR tip.', 'It is aborted, unless notFound is set to fallback.'),
    quiz(3, 'In routeWebSocket, how do you keep the real server and only change some messages?', ['ws.continue()', 'ws.connectToServer()', 'ws.fetch()', 'you cannot'], 1,
         'Connect, then forward.', 'connectToServer opens the real connection, and the handler forwards or changes messages.'),
    quiz(3, 'Which is a good reason to keep some tests against the real API?', ['mocks are slow', 'so the mocks do not drift away from the real API', 'routes are not allowed in CI', 'HAR files expire'], 1,
         'Mocks can go stale.', 'If the API changes and only mocks are tested, the tests keep passing while the real page breaks.'),
]

CALC = [
    calc(1, 'The products API waits 600 ms. A mocked answer takes about 0 ms. 50 tests load the products once each. How many seconds does mocking save?', 30, '50 × 0.6', ['50 × 600 ms = 30000 ms', '30000 ms = 30 s']),
    calc(1, 'A mock sends 2 products. How many list items does the page show?', 2, 'one item per product', ['2 products → 2 items']),
    calc(2, 'The real API sends 5 products, and the handler sets the stock of 2 of them to 0. How many Add to cart buttons are left?', 2, 'the Notebook is already out of stock', ['5 products, 1 already sold out: 4 buttons', '4 - 2 = 2']),
    calc(2, 'A page makes 6 API calls, and 2 are caught by routes and fulfilled. How many reach the server?', 4, '6 - 2', ['6 - 2 = 4']),
    calc(2, 'A HAR replay file has 3 recorded answers. The page makes 4 different calls, and no fallback is set. How many are aborted?', 1, 'what is not in the file', ['4 - 3 = 1']),
    calc(3, 'Images are 70 % of the bytes of a page of 2000 KB. How many KB load when images are aborted?', 600, '2000 × 0.3', ['100 - 70 = 30 %', '2000 × 0.3 = 600 KB']),
    calc(3, 'A mocked WebSocket sends a stock message every 500 ms. How many messages in 3 seconds?', 6, '3000 / 500', ['3000 ms / 500 ms = 6']),
    calc(3, 'A team has 120 tests and mocks the payment API in 30 of them. What percent use the real payment API?', 75, '90 / 120 × 100', ['120 - 30 = 90', '90 / 120 = 0.75', '× 100 = 75 %']),
]

LABS = [
    {'id': 'mockempty', 'title': 'Show an empty shop', 'name': 'shows a message when there are no products',
     'task': 'Answer <code>**/api/products</code> with an empty list <code>[]</code> before opening <code>/products</code>. Then check that the page says <b>No products match your search</b>.',
     'goal': 'The shop shows its empty message.', 'start': '/products',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('shows a message when there are no products', async ({ page }) => {
  // mock the products API with an empty list, then open /products
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('shows a message when there are no products', async ({ page }) => {
  await page.route('**/api/products', route => route.fulfill({ json: [] }));
  await page.goto('/products');
  await expect(page.getByText('No products match your search')).toBeVisible();
});'''},
     'hint': "Add the route before goto: <code>await page.route('**/api/products', route => route.fulfill({ json: [] }));</code>",
     'why': 'The route must exist before the page asks for the products, so it comes before goto. An empty list is a real case, for a new shop or a search with no hits, and the page should show a message, not an empty space.',
     'check': [["/No products match your search/.test(ctx.text)", 'The empty message is on the page'], ["/fulfill|Fulfill/.test(ctx.code)", 'The test answers the request itself']]},
    {'id': 'mock503', 'title': 'Make the products API fail', 'name': 'shows a friendly error',
     'task': 'Answer <code>**/api/products</code> with status <b>503</b>, open <code>/products</code>, and check that the alert says <b>Sorry, we could not load the products. Please try again.</b>',
     'goal': 'The friendly error is on the page.', 'start': '/products',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('shows a friendly error', async ({ page }) => {
  // make the products API answer with status 503, then open /products
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('shows a friendly error', async ({ page }) => {
  await page.route('**/api/products', route => route.fulfill({ status: 503 }));
  await page.goto('/products');
  await expect(page.getByRole('alert')).toHaveText('Sorry, we could not load the products. Please try again.');
});'''},
     'hint': "Use <code>route.fulfill({ status: 503 })</code>, and find the message with <code>getByRole('alert')</code>.",
     'why': '503 means the service is not available right now. The page treats every answer that is not ok the same way, so 500, 503 and an aborted request all lead to the same message.',
     'check': [["/could not load the products/.test(ctx.text)", 'The friendly error is on the page'], ["/503/.test(ctx.code)", 'The API answered with 503']]},
]

T = {
    'slug': 'pw-network', 'title': 'Network: watch, mock and change requests', 'short': 'Network mocking', 'emoji': '🛰️', 'module': MODULE, 'minutes': 26,
    'lead': 'Take control of what the page receives. Listen to every request, answer them with your own data, make them fail, change one field of a real answer, record an API into a HAR file and replay it, and mock a WebSocket feed.',
    'desc': "page.on('request') and response, waitForResponse and expect_response, page.route with fulfill, abort, continue and fetch, glob patterns, context.route, error states, HAR recording and replay with routeFromHAR, and routeWebSocket.",
    'summary': 'Logging API traffic and reading one response, mocking the products API, a 500 and a broken connection, selling out the lamp in a real answer, recording and replaying a HAR file, and mocking the live stock WebSocket.',
    'keywords': ['network', 'mock', 'route', 'fulfill', 'abort', 'continue', 'fetch', 'waitForResponse', 'expect_response', 'HAR', 'routeFromHAR', 'WebSocket', 'routeWebSocket', 'glob'],
    'plain': 'A page is only as good as the data it gets. Controlling the network lets you test the cases that are hard to create for real: empty lists, server errors, sold out products and a feed that says something new.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
