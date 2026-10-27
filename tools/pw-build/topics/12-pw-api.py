from pkit import part, say, quiz, calc, panel, four, one, js, ts, py, jv, shown, table, tip, by

MODULE = ('🛰️', 'Network and APIs', 'pw-network', 'Watching, mocking and changing network traffic, testing APIs directly, and signing in once for the whole suite.')

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

# ---------- a plain API test ----------
CRUD_TS = '''import { test, expect } from '@playwright/test';

test('create, read, update and delete a person', async ({ request }) => {
  const created = await request.post('/api/people', { data: { name: 'Kiran', email: 'kiran@shop.example' } });
  expect(created.status()).toBe(201);
  const kiran = await created.json();
  expect(created.headers()['location']).toBe(`/api/people/${kiran.id}`);

  const read = await request.get(`/api/people/${kiran.id}`);
  await expect(read).toBeOK();
  expect(await read.json()).toEqual({ id: kiran.id, name: 'Kiran', email: 'kiran@shop.example', city: null });

  const updated = await request.patch(`/api/people/${kiran.id}`, { data: { city: 'Pune' } });
  expect((await updated.json()).city).toBe('Pune');

  expect((await request.delete(`/api/people/${kiran.id}`)).status()).toBe(204);
  expect((await request.get(`/api/people/${kiran.id}`)).status()).toBe(404);
});

test('a bad email is refused', async ({ request }) => {
  const response = await request.post('/api/people', { data: { name: 'Nobody', email: 'not-an-email' } });
  expect(response.status()).toBe(422);
  expect(await response.json()).toEqual({ error: 'name and a valid email are required' });
});'''

CRUD_CONFTEST = '''import pytest
from playwright.sync_api import APIRequestContext, Playwright


@pytest.fixture
def api(playwright: Playwright, base_url: str) -> APIRequestContext:
    context = playwright.request.new_context(base_url=base_url)
    yield context
    context.dispose()'''

CRUD_PY = '''from playwright.sync_api import APIRequestContext, expect


def test_create_read_update_and_delete_a_person(api: APIRequestContext):
    created = api.post("/api/people", data={"name": "Kiran", "email": "kiran@shop.example"})
    assert created.status == 201
    kiran = created.json()
    assert created.headers["location"] == f"/api/people/{kiran['id']}"

    read = api.get(f"/api/people/{kiran['id']}")
    expect(read).to_be_ok()
    assert read.json() == {"id": kiran["id"], "name": "Kiran", "email": "kiran@shop.example", "city": None}

    updated = api.patch(f"/api/people/{kiran['id']}", data={"city": "Pune"})
    assert updated.json()["city"] == "Pune"

    assert api.delete(f"/api/people/{kiran['id']}").status == 204
    assert api.get(f"/api/people/{kiran['id']}").status == 404


def test_a_bad_email_is_refused(api: APIRequestContext):
    response = api.post("/api/people", data={"name": "Nobody", "email": "not-an-email"})
    assert response.status == 422
    assert response.json() == {"error": "name and a valid email are required"}'''

CRUD_JAVA = '''package com.brainy;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.microsoft.playwright.APIRequestContext;
import com.microsoft.playwright.APIResponse;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.RequestOptions;
import org.junit.jupiter.api.Test;
import java.util.Map;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;

@UsePlaywright(ApiOptions.class)
public class PeopleApiTest {
  @Test
  void createReadUpdateAndDeleteAPerson(APIRequestContext request) {
    APIResponse created = request.post("/api/people",
        RequestOptions.create().setData(Map.of("name", "Kiran", "email", "kiran@shop.example")));
    assertEquals(201, created.status());
    int id = JsonParser.parseString(created.text()).getAsJsonObject().get("id").getAsInt();
    assertEquals("/api/people/" + id, created.headers().get("location"));

    APIResponse read = request.get("/api/people/" + id);
    assertThat(read).isOK();
    JsonObject kiran = JsonParser.parseString(read.text()).getAsJsonObject();
    assertEquals("Kiran", kiran.get("name").getAsString());
    assertEquals("kiran@shop.example", kiran.get("email").getAsString());

    APIResponse updated = request.patch("/api/people/" + id, RequestOptions.create().setData(Map.of("city", "Pune")));
    assertEquals("Pune", JsonParser.parseString(updated.text()).getAsJsonObject().get("city").getAsString());

    assertEquals(204, request.delete("/api/people/" + id).status());
    assertEquals(404, request.get("/api/people/" + id).status());
  }

  @Test
  void aBadEmailIsRefused(APIRequestContext request) {
    APIResponse response = request.post("/api/people",
        RequestOptions.create().setData(Map.of("name", "Nobody", "email", "not-an-email")));
    assertEquals(422, response.status());
    assertEquals("{\\"error\\":\\"name and a valid email are required\\"}", response.text());
  }
}'''

# ---------- a token in a header ----------
TOKEN_TS = '''import { test, expect } from '@playwright/test';

test('the token opens the cart', async ({ request, playwright }) => {
  expect((await request.get('/api/cart')).status()).toBe(401);      // nobody is signed in yet

  const login = await request.post('/api/login', { data: { email: 'asha@shop.example', password: 's3cret' } });
  const { token, name } = await login.json();
  console.log(`signed in as ${name}`);

  // A fresh client that sends the token with every call, and has no cookies.
  const asha = await playwright.request.newContext({
    baseURL: 'http://localhost:4173',
    extraHTTPHeaders: { Authorization: `Bearer ${token}` },
  });
  await asha.post('/api/cart', { data: { productId: 2, qty: 2 } });
  const cart = await (await asha.get('/api/cart')).json();
  console.log(cart);
  expect(cart.count).toBe(2);
  expect(cart.total).toBe(398);
  await asha.dispose();
});'''

TOKEN_PY = '''from playwright.sync_api import APIRequestContext, Playwright


def test_the_token_opens_the_cart(api: APIRequestContext, playwright: Playwright, base_url: str):
    assert api.get("/api/cart").status == 401          # nobody is signed in yet

    login = api.post("/api/login", data={"email": "asha@shop.example", "password": "s3cret"})
    token, name = login.json()["token"], login.json()["name"]
    print(f"\\nsigned in as {name}")

    # A fresh client that sends the token with every call, and has no cookies.
    asha = playwright.request.new_context(base_url=base_url, extra_http_headers={"Authorization": f"Bearer {token}"})
    asha.post("/api/cart", data={"productId": 2, "qty": 2})
    cart = asha.get("/api/cart").json()
    print(cart)
    assert cart["count"] == 2
    assert cart["total"] == 398
    asha.dispose()'''

TOKEN_JAVA = '''package com.brainy;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.microsoft.playwright.APIRequest;
import com.microsoft.playwright.APIRequestContext;
import com.microsoft.playwright.Playwright;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.RequestOptions;
import org.junit.jupiter.api.Test;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

@UsePlaywright(ApiOptions.class)
public class TokenTest {
  @Test
  void theTokenOpensTheCart(APIRequestContext request, Playwright playwright) {
    assertEquals(401, request.get("/api/cart").status());      // nobody is signed in yet

    JsonObject login = JsonParser.parseString(request.post("/api/login",
        RequestOptions.create().setData(Map.of("email", "asha@shop.example", "password", "s3cret"))).text()).getAsJsonObject();
    System.out.println("signed in as " + login.get("name").getAsString());

    // A fresh client that sends the token with every call, and has no cookies.
    APIRequestContext asha = playwright.request().newContext(new APIRequest.NewContextOptions()
        .setBaseURL("http://localhost:4173")
        .setExtraHTTPHeaders(Map.of("Authorization", "Bearer " + login.get("token").getAsString())));
    asha.post("/api/cart", RequestOptions.create().setData(Map.of("productId", 2, "qty", 2)));
    JsonObject cart = JsonParser.parseString(asha.get("/api/cart").text()).getAsJsonObject();
    System.out.println(cart);
    assertEquals(2, cart.get("count").getAsInt());
    assertEquals(398, cart.get("total").getAsInt());
    asha.dispose();
  }
}'''

# ---------- set up through the API, check in the UI ----------
MIX_TS = '''import { test, expect } from '@playwright/test';

test('a lamp added through the API shows in the cart page', async ({ page }) => {
  // Sign in through the API. page.request shares cookies with the page.
  const login = await page.request.post('/api/login', { data: { email: 'asha@shop.example', password: 's3cret' } });
  const { token } = await login.json();
  await page.addInitScript(t => localStorage.setItem('token', t), token);   // the shop keeps its token here

  await page.request.post('/api/cart', { data: { productId: 3 } });         // arrange the cart without clicking

  await page.goto('/cart');
  await expect(page.getByText('Hello, Asha')).toBeVisible();
  await expect(page.getByRole('row', { name: /Desk lamp/ })).toContainText('₹1,299');
  await expect(page.getByTestId('cart-count')).toHaveText('1');
});'''

MIX_PY = '''from playwright.sync_api import Page, expect


def test_a_lamp_added_through_the_api_shows_in_the_cart_page(page: Page):
    # Sign in through the API. page.request shares cookies with the page.
    login = page.request.post("/api/login", data={"email": "asha@shop.example", "password": "s3cret"})
    token = login.json()["token"]
    page.add_init_script(f"localStorage.setItem('token', '{token}')")     # the shop keeps its token here

    page.request.post("/api/cart", data={"productId": 3})                  # arrange the cart without clicking

    page.goto("/cart")
    expect(page.get_by_text("Hello, Asha")).to_be_visible()
    expect(page.get_by_role("row", name="Desk lamp")).to_contain_text("₹1,299")
    expect(page.get_by_test_id("cart-count")).to_have_text("1")'''

MIX_JAVA = '''package com.brainy;

import com.google.gson.JsonParser;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import com.microsoft.playwright.options.RequestOptions;
import org.junit.jupiter.api.Test;
import java.util.Map;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class CartSetupTest {
  @Test
  void aLampAddedThroughTheApiShowsInTheCartPage(Page page) {
    // Sign in through the API. page.request() shares cookies with the page.
    String token = JsonParser.parseString(page.request().post("/api/login",
        RequestOptions.create().setData(Map.of("email", "asha@shop.example", "password", "s3cret"))).text())
        .getAsJsonObject().get("token").getAsString();
    page.addInitScript("localStorage.setItem('token', '" + token + "')");    // the shop keeps its token here

    page.request().post("/api/cart", RequestOptions.create().setData(Map.of("productId", 3)));   // arrange the cart without clicking

    page.navigate("/cart");
    assertThat(page.getByText("Hello, Asha")).isVisible();
    assertThat(page.getByRole(AriaRole.ROW, new Page.GetByRoleOptions().setName("Desk lamp"))).containsText("₹1,299");
    assertThat(page.getByTestId("cart-count")).hasText("1");
  }
}'''

# ---------- sign in once, save the state, reuse it ----------
STATE_CONFIG = '''import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  reporter: 'list',
  use: { baseURL: 'http://localhost:4173' },
  projects: [
    { name: 'setup', testMatch: /auth\\.setup\\.[jt]s/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: 'playwright/.auth/asha.json' },   // every test starts signed in
      dependencies: ['setup'],
    },
  ],
});'''

STATE_SETUP_TS = '''import { test as setup, expect } from '@playwright/test';

setup('sign in as Asha', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('s3cret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByText('Hello, Asha')).toBeVisible();          // wait until signing in has finished
  await page.context().storageState({ path: 'playwright/.auth/asha.json' });
});'''

STATE_TEST_TS = '''import { test, expect } from '@playwright/test';

test('the products page greets Asha', async ({ page }) => {
  await page.goto('/products');                      // no sign in steps here
  await expect(page.getByText('Hello, Asha')).toBeVisible();
});

test('the cart is open to her', async ({ page }) => {
  await page.goto('/cart');
  await expect(page.getByRole('heading', { name: 'Your cart' })).toBeVisible();
  await expect(page).toHaveURL(/\\/cart$/);           // not sent to /login
});'''

STATE_CONFTEST = '''from pathlib import Path
import pytest
from playwright.sync_api import Browser, expect

STATE = Path("playwright/.auth/asha.json")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, browser: Browser, base_url: str):
    # Sign in once for the whole run, and save cookies and local storage.
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    page.goto("/login")
    page.get_by_label("Email").fill("asha@shop.example")
    page.get_by_label("Password").fill("s3cret")
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_text("Hello, Asha")).to_be_visible()     # wait until signing in has finished
    STATE.parent.mkdir(parents=True, exist_ok=True)            # Python does not create the folder for you
    context.storage_state(path=STATE)
    context.close()
    return {**browser_context_args, "storage_state": STATE}    # every test starts signed in'''

STATE_PY = '''import re
from playwright.sync_api import Page, expect


def test_the_products_page_greets_asha(page: Page):
    page.goto("/products")                            # no sign in steps here
    expect(page.get_by_text("Hello, Asha")).to_be_visible()


def test_the_cart_is_open_to_her(page: Page):
    page.goto("/cart")
    expect(page.get_by_role("heading", name="Your cart")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/cart$"))  # not sent to /login'''

STATE_OPTIONS_JAVA = '''package com.brainy;

import com.microsoft.playwright.Browser;
import com.microsoft.playwright.junit.Options;
import com.microsoft.playwright.junit.OptionsFactory;
import java.nio.file.Paths;

// Every test that uses these options starts signed in as Asha.
public class SignedInOptions implements OptionsFactory {
  @Override
  public Options getOptions() {
    return new Options()
        .setHeadless(true)
        .setBaseUrl("http://localhost:4173")
        .setContextOptions(new Browser.NewContextOptions().setStorageStatePath(Paths.get("playwright/.auth/asha.json")));
  }
}'''

STATE_JAVA = '''package com.brainy;

import com.microsoft.playwright.*;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import java.nio.file.Paths;
import java.util.regex.Pattern;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(SignedInOptions.class)
public class SignedInTest {
  @BeforeAll
  static void signInOnce() {
    // Sign in once, and save cookies and local storage for every test in the class.
    try (Playwright playwright = Playwright.create()) {
      BrowserContext context = playwright.chromium().launch()
          .newContext(new Browser.NewContextOptions().setBaseURL("http://localhost:4173"));
      Page page = context.newPage();
      page.navigate("/login");
      page.getByLabel("Email").fill("asha@shop.example");
      page.getByLabel("Password").fill("s3cret");
      page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in")).click();
      assertThat(page.getByText("Hello, Asha")).isVisible();     // wait until signing in has finished
      context.storageState(new BrowserContext.StorageStateOptions().setPath(Paths.get("playwright/.auth/asha.json")));
    }
  }

  @Test
  void theProductsPageGreetsAsha(Page page) {
    page.navigate("/products");                        // no sign in steps here
    assertThat(page.getByText("Hello, Asha")).isVisible();
  }

  @Test
  void theCartIsOpenToHer(Page page) {
    page.navigate("/cart");
    assertThat(page.getByRole(AriaRole.HEADING, new Page.GetByRoleOptions().setName("Your cart"))).isVisible();
    assertThat(page).hasURL(Pattern.compile("/cart$"));  // not sent to /login
  }
}'''

CODES = {
    'crud': four('Create, read, update and delete through the API',
                 java=jv({'ApiOptions.java': API_OPTIONS_JAVA, 'PeopleApiTest.java': CRUD_JAVA}, show=['src/test/java/com/brainy/PeopleApiTest.java']),
                 py=py({'conftest.py': CRUD_CONFTEST, 'test_people_api.py': CRUD_PY}, show=['conftest.py', 'tests/test_people_api.py']),
                 js=js({'people-api.spec.js': CRUD_TS}),
                 ts=ts({'people-api.spec.ts': CRUD_TS}),
                 result='No browser page was opened. The test talked to the API directly: it created Kiran, read him back, moved him to Pune, deleted him, and checked that he was gone. The second test checked that the API refuses a bad email with 422 and a clear message.'),
    'token': four('Sign in through the API and send the token',
                  java=jv({'ApiOptions.java': API_OPTIONS_JAVA, 'TokenTest.java': TOKEN_JAVA}, show=['src/test/java/com/brainy/TokenTest.java']),
                  py=py({'conftest.py': CRUD_CONFTEST, 'test_token.py': TOKEN_PY}, cmd='pytest -s -q', show=['tests/test_token.py']),
                  js=js({'token.spec.js': TOKEN_TS}),
                  ts=ts({'token.spec.ts': TOKEN_TS}),
                  result='Without signing in, the cart answered 401. After the login call, a new client sent the token in an Authorization header with every request, and two mugs went into Asha\'s cart for ₹398. The new client had no cookies, so the token alone was enough.'),
    'mix': four('Arrange through the API, check through the page',
                java=jv({'CartSetupTest.java': MIX_JAVA}),
                py=py({'test_cart_setup.py': MIX_PY}),
                js=js({'cart-setup.spec.js': MIX_TS}),
                ts=ts({'cart-setup.spec.ts': MIX_TS.replace('t => localStorage', '(t: string) => localStorage')}),
                result='The test signed in and filled the cart with two API calls, then opened the cart page once and checked what a customer would see. The UI part is short and fast, and it tests only what the UI must show. Because the shop keeps its token in local storage, addInitScript puts it there before any shop script runs.'),
    'state': four('Sign in once, save the state, start every test signed in',
                  java=jv({'SignedInOptions.java': STATE_OPTIONS_JAVA, 'SignedInTest.java': STATE_JAVA}),
                  py=py({'conftest.py': STATE_CONFTEST, 'test_signed_in.py': STATE_PY}, show=['conftest.py', 'tests/test_signed_in.py']),
                  js=js({'auth.setup.js': STATE_SETUP_TS, 'signed-in.spec.js': STATE_TEST_TS}, config=STATE_CONFIG,
                        show=['playwright.config.js', 'tests/auth.setup.js', 'tests/signed-in.spec.js']),
                  ts=ts({'auth.setup.ts': STATE_SETUP_TS, 'signed-in.spec.ts': STATE_TEST_TS}, config=STATE_CONFIG,
                        show=['playwright.config.ts', 'tests/auth.setup.ts', 'tests/signed-in.spec.ts']),
                  result='Signing in ran once and saved its cookies and local storage to playwright/.auth/asha.json. Both tests then started already signed in, with no sign in steps of their own. In a suite of hundreds of tests, this saves one sign in per test. One difference showed up in our run: Python\'s storage_state does not create a missing folder, so the conftest creates playwright/.auth first, while JavaScript and Java create it themselves.'),
}

DG = {
    'state': {'t': 'Sign in once, reuse everywhere', 'w': 900, 'h': 230,
              'n': [['setup', 20, 83, 150, 64, 'setup step', {'c': 2, 'sub': 'signs in once', 'i': 'A setup project, a session fixture or a @BeforeAll method signs in through the real login page.'}],
                    ['file', 230, 83, 190, 64, 'asha.json', {'c': 5, 'sub': 'cookies and local storage', 'i': 'storageState writes the cookies and the local storage of the signed in context to a file.'}],
                    ['t1', 490, 10, 170, 64, 'test 1', {'c': 1, 'sub': 'starts signed in', 'i': 'Each new context is created from the file, so the test starts signed in.'}],
                    ['t2', 490, 83, 170, 64, 'test 2', {'c': 1, 'sub': 'starts signed in', 'i': 'The same file serves every test.'}],
                    ['t3', 490, 156, 170, 64, 'test 300', {'c': 1, 'sub': 'starts signed in', 'i': 'However many tests there are, the sign in ran once.'}],
                    ['git', 720, 83, 160, 64, '.gitignore', {'c': 3, 'sub': 'never commit it', 'i': 'The file holds a live session. Keep it out of the repository.'}]],
              'e': [['setup', 'file'], ['file', 't1'], ['file', 't2'], ['file', 't3'], ['t2', 'git']],
              'st': [[['setup'], 'A setup step signs in once, through the real page.'],
                     [['file', 'setup>file'], 'storageState saves cookies and local storage to a file.'],
                     [['t1', 't2', 't3', 'file>t1', 'file>t2', 'file>t3'], 'Every test creates its context from that file and starts signed in.'],
                     [['git', 't2>git'], 'The file is a live session, so it goes in .gitignore.']]},
}

PARTS = [
    part('api', '🔌', 'API tests without a browser', f'''
<p>Playwright can call an HTTP API directly, with no page at all. These tests are fast, and they check the rules of the server: status codes, data and error messages. Each language has a request client that remembers the base URL and the cookies.</p>
{table(['', 'Playwright Test', 'Python', 'Java'], [
    ['the client', 'the request fixture', 'playwright.request.new_context()', 'the APIRequestContext fixture, or playwright.request().newContext()'],
    ['send JSON', "request.post(url, { data })", 'api.post(url, data=...)', 'request.post(url, RequestOptions.create().setData(...))'],
    ['check status 200 to 299', 'await expect(response).toBeOK()', 'expect(response).to_be_ok()', 'assertThat(response).isOK()'],
    ['read JSON', 'await response.json()', 'response.json()', 'response.text() and a JSON library'],
])}
[[crud]]
''', easy=True, kw=['API testing', 'request', 'APIRequestContext', 'get', 'post', 'patch', 'delete', 'status', 'toBeOK']),

    part('token', '🔑', 'Tokens and headers', f'''
<p>Most APIs want proof of who is calling. The shop gives a token when you sign in, and accepts it in an <code>Authorization: Bearer</code> header. A request client can send that header with every call.</p>
[[token]]
{tip('Keep real passwords and tokens out of test code. Read them from environment variables, such as process.env.SHOP_PASSWORD, os.environ["SHOP_PASSWORD"] or System.getenv("SHOP_PASSWORD"), and set them as secrets in CI. The framework chapter shows a .env file for local runs.', 'warn')}
''', kw=['token', 'Bearer', 'Authorization', 'extraHTTPHeaders', '401', 'secrets']),

    part('mix', '🧩', 'API for set up, page for checks', f'''
<p>A UI test that clicks through sign in and three product pages to fill a cart is slow, and it fails when any of those pages has a problem. A common pattern is to set up through the API and use the page only for what the test is about.</p>
[[mix]]
{tip('page.request (and context.request) share cookies with the browser context. A sign in through page.request signs in the page too, for apps that use cookies. The shop also keeps a token in local storage, which is why the example adds it with addInitScript.', 'tip')}
''', kw=['arrange', 'page.request', 'addInitScript', 'set up through API', 'cookies']),

    part('state', '💾', 'Sign in once for the whole suite', f'''
<p>Signing in through the page in every test costs time, often seconds per test. Playwright can save the signed in state, the cookies and local storage of a context, to a file with <b>storageState</b>. New contexts created from that file start signed in.</p>
<div class="viz" data-viz="flow" data-k="state"></div>
[[state]]
{table(['Need', 'Approach'], [
    ['all tests can share one account', 'one setup step and one state file, as above'],
    ['tests change data of the account', 'one account per worker, named with the worker index'],
    ['two roles, such as customer and admin', 'two state files, asha.json and ravi.json, and a project or fixture for each'],
    ['the app keeps its session in sessionStorage', 'storageState does not save sessionStorage, so save it yourself and restore it with addInitScript'],
])}
{tip('The state file holds a live session that anyone could use. Add playwright/.auth to .gitignore, and let each run create it fresh.', 'warn')}
''', kw=['storageState', 'auth', 'setup project', 'signed in', 'roles', '.auth', 'sessionStorage']),
]

INFO = {'title': 'Fast tests through the API', 'panels': [
    panel([['e', '🔌'], ['t', 'request', {'b': 1}]], 'API tests', 'No browser at all.', 'Status, data, errors.'),
    panel([['e', '🔑'], ['t', 'Bearer', {'b': 1}]], 'Tokens', 'Proof of who calls.', 'Keep them in secrets.'),
    panel([['e', '🧩'], ['t', 'arrange', {'b': 1}]], 'Mix', 'API for set up.', 'Page for the check.'),
    panel([['e', '💾'], ['t', 'storageState', {'b': 1}]], 'Sign in once', 'Save the state.', 'Every test starts signed in.')],
    'remember': 'Use the page for what the user sees. Use the API for everything you only need to get ready.'}

REAL = [
    ['🏦', 'Sign in once instead of 800 times', 'A banking suite signs in once per run in a setup project and saves the state. Each test skips the sign in page and starts on the screen it is about.'],
    ['🛒', 'Carts filled by the API', 'An online grocer fills carts with 30 items through one API call before each checkout test. Clicking 30 product pages would take most of a minute and add 30 chances to fail.'],
    ['🔐', 'Two roles, two files', 'A support tool saves agent.json and admin.json in two setup steps. Tests for the admin screens use one file, and tests for the agent screens use the other.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter tests the API directly, sends tokens in headers, sets up data through the API before a UI check, and signs in once so every test starts signed in.',
        'यह अध्याय API को सीधे test करता है, headers में tokens भेजता है, UI check से पहले API से data तैयार करता है, और एक बार sign in करता है ताकि हर test signed in शुरू हो।',
        'ಈ ಅಧ್ಯಾಯ API ಅನ್ನು ನೇರವಾಗಿ test ಮಾಡುತ್ತದೆ, headers ನಲ್ಲಿ tokens ಕಳುಹಿಸುತ್ತದೆ, UI check ಗೆ ಮೊದಲು API ಮೂಲಕ data ಸಿದ್ಧಪಡಿಸುತ್ತದೆ, ಮತ್ತು ಒಮ್ಮೆ sign in ಮಾಡಿ ಪ್ರತಿ test signed in ಆಗಿ ಶುರುವಾಗುವಂತೆ ಮಾಡುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ API କୁ ସିଧାସଳଖ test କରେ, headers ରେ tokens ପଠାଏ, UI check ପୂର୍ବରୁ API ରେ data ପ୍ରସ୍ତୁତ କରେ, ଏବଂ ଥରେ sign in କରେ ଯାହାଦ୍ୱାରା ପ୍ରତି test signed in ଆରମ୍ଭ ହୁଏ।',
        'يختبر هذا الفصل واجهة API مباشرة، ويرسل الرموز في الترويسات، ويجهّز البيانات عبر API قبل فحص الواجهة، ويسجّل الدخول مرة واحدة ليبدأ كل اختبار مسجّلًا.',
        'Dieses Kapitel testet die API direkt, sendet Tokens in Headern, bereitet Daten über die API vor einer UI-Prüfung vor und meldet sich einmal an, damit jeder Test angemeldet startet.'),
    say('api', 'API tests', 'The request client calls the API with no page. A test checks status codes, the data that comes back, and the error for bad input.',
        'Request client बिना page के API को call करता है। Test status codes, लौटे data और गलत input की error जाँचता है।',
        'Request client page ಇಲ್ಲದೆ API ಅನ್ನು call ಮಾಡುತ್ತದೆ. Test status codes, ಬಂದ data ಮತ್ತು ತಪ್ಪು input ನ error ಪರಿಶೀಲಿಸುತ್ತದೆ.',
        'Request client page ବିନା API କୁ call କରେ। Test status codes, ଫେରିଥିବା data ଓ ଭୁଲ input ର error ଯାଞ୍ଚ କରେ।',
        'يستدعي عميل الطلبات واجهة API دون صفحة. ويتحقق الاختبار من رموز الحالة والبيانات العائدة والخطأ عند الإدخال الخاطئ.',
        'Der Request-Client ruft die API ohne Seite auf. Ein Test prüft Statuscodes, die zurückgegebenen Daten und den Fehler bei falscher Eingabe.'),
    say('token', 'Tokens', 'After signing in, the API gives a token. A client with extra HTTP headers sends it with every call, in an Authorization header.',
        'Sign in के बाद API एक token देता है। Extra HTTP headers वाला client उसे हर call के साथ Authorization header में भेजता है।',
        'Sign in ನಂತರ API ಒಂದು token ಕೊಡುತ್ತದೆ. Extra HTTP headers ಇರುವ client ಅದನ್ನು ಪ್ರತಿ call ಜೊತೆ Authorization header ನಲ್ಲಿ ಕಳುಹಿಸುತ್ತದೆ.',
        'Sign in ପରେ API ଏକ token ଦିଏ। Extra HTTP headers ଥିବା client ଏହାକୁ ପ୍ରତି call ସହ Authorization header ରେ ପଠାଏ।',
        'بعد تسجيل الدخول تعطي واجهة API رمزًا. ويرسله عميل له ترويسات إضافية مع كل اتصال في ترويسة Authorization.',
        'Nach der Anmeldung gibt die API ein Token. Ein Client mit zusätzlichen HTTP-Headern sendet es bei jedem Aufruf im Authorization-Header.'),
    say('mix', 'API for set up', 'Fill the cart through the API, then open the cart page and check it. The page part stays short and only tests what the page must show.',
        'API से cart भरें, फिर cart page खोलकर जाँचें। Page वाला हिस्सा छोटा रहता है और सिर्फ़ वही test करता है जो page को दिखाना है।',
        'API ಮೂಲಕ cart ತುಂಬಿಸಿ, ನಂತರ cart page ತೆರೆದು ಪರಿಶೀಲಿಸಿ. Page ಭಾಗ ಚಿಕ್ಕದಾಗಿರುತ್ತದೆ ಮತ್ತು page ತೋರಿಸಬೇಕಾದ್ದನ್ನು ಮಾತ್ರ test ಮಾಡುತ್ತದೆ.',
        'API ରେ cart ଭରନ୍ତୁ, ତାପରେ cart page ଖୋଲି ଯାଞ୍ଚ କରନ୍ତୁ। Page ଅଂଶ ଛୋଟ ରହେ ଏବଂ page ଦେଖାଇବା ଉଚିତ ଜିନିଷ କେବଳ test କରେ।',
        'املأ السلة عبر API، ثم افتح صفحة السلة وتحقق منها. يبقى جزء الصفحة قصيرًا ولا يختبر إلا ما يجب أن تعرضه الصفحة.',
        'Fülle den Warenkorb über die API, öffne dann die Warenkorbseite und prüfe sie. Der Seitenteil bleibt kurz und testet nur, was die Seite zeigen muss.'),
    say('state', 'Sign in once', 'storageState saves cookies and local storage to a file. New contexts created from that file start signed in, so the sign in runs once for the whole suite.',
        'storageState cookies और local storage को file में save करता है। उस file से बने नए contexts signed in शुरू होते हैं, इसलिए sign in पूरे suite के लिए एक बार चलता है।',
        'storageState cookies ಮತ್ತು local storage ಅನ್ನು file ಗೆ save ಮಾಡುತ್ತದೆ. ಆ file ನಿಂದ ಮಾಡಿದ ಹೊಸ contexts signed in ಆಗಿ ಶುರುವಾಗುತ್ತವೆ, ಹಾಗಾಗಿ sign in ಸಂಪೂರ್ಣ suite ಗೆ ಒಮ್ಮೆ ನಡೆಯುತ್ತದೆ.',
        'storageState cookies ଓ local storage କୁ file ରେ save କରେ। ସେହି file ରୁ ତିଆରି ନୂଆ contexts signed in ଆରମ୍ଭ ହୁଏ, ତେଣୁ sign in ପୂରା suite ପାଇଁ ଥରେ ଚାଲେ।',
        'يحفظ storageState ملفات تعريف الارتباط والتخزين المحلي في ملف. تبدأ السياقات الجديدة المنشأة منه مسجّلة الدخول، فيعمل تسجيل الدخول مرة واحدة للمجموعة كلها.',
        'storageState speichert Cookies und Local Storage in einer Datei. Neue Kontexte aus dieser Datei starten angemeldet, sodass die Anmeldung einmal für die ganze Suite läuft.'),
    say('practice', 'Playground labs', 'In the labs you sign in as Ravi, the admin, and then place a real order as Asha from the cart page.',
        'Labs में आप admin Ravi के रूप में sign in करते हैं, फिर cart page से Asha के रूप में असली order देते हैं।',
        'Labs ನಲ್ಲಿ admin Ravi ಆಗಿ sign in ಮಾಡುತ್ತೀರಿ, ನಂತರ cart page ನಿಂದ Asha ಆಗಿ ನಿಜವಾದ order ಮಾಡುತ್ತೀರಿ.',
        'Labs ରେ ଆପଣ admin Ravi ଭାବେ sign in କରନ୍ତି, ତାପରେ cart page ରୁ Asha ଭାବେ ପ୍ରକୃତ order ଦିଅନ୍ତି।',
        'في المختبرات تسجّل الدخول باسم Ravi المسؤول، ثم تقدّم طلبًا حقيقيًا باسم Asha من صفحة السلة.',
        'In den Labs meldest du dich als Admin Ravi an und gibst dann als Asha eine echte Bestellung auf der Warenkorbseite auf.'),
]

QUIZ = [
    quiz(1, 'Which Playwright Test fixture calls an API without a page?', ['page', 'request', 'api', 'fetch'], 1,
         'It sends requests.', 'The request fixture is an APIRequestContext that uses the baseURL from the config.'),
    quiz(1, 'Which status code means created?', ['200', '201', '204', '404'], 1,
         'Look at the POST in the CRUD example.', '201 Created is the usual answer to a successful POST that makes something new.'),
    quiz(1, 'What does toBeOK check?', ['the status is 200 only', 'the status is from 200 to 299', 'the body is not empty', 'the page loaded'], 1,
         'OK covers a range.', 'toBeOK, to_be_ok and isOK pass for any status from 200 to 299.'),
    quiz(1, 'What does storageState save?', ['screenshots', 'cookies and local storage', 'the whole browser', 'passwords'], 1,
         'It is about being signed in.', 'It saves the cookies and local storage of the context, which is what keeps a user signed in.'),
    quiz(2, 'Why add playwright/.auth to .gitignore?', ['it is large', 'it holds a live session someone could use', 'git cannot store JSON', 'Playwright requires it'], 1,
         'Think of what is inside.', 'The file holds session cookies and tokens that work like a signed in user.'),
    quiz(2, 'In Java with @UsePlaywright, why did the example need ApiOptions?', ['to use Firefox', 'setBaseUrl does not apply to the request fixture', 'to run in parallel', 'for headless mode'], 1,
         'The request fixture has its own options.', 'setApiRequestOptions gives the APIRequestContext fixture its own base URL.'),
    quiz(2, 'Which header carries a token in the shop API?', ['Cookie', 'Authorization: Bearer ...', 'X-Token', 'Accept'], 1,
         'Look at the token example.', 'The shop accepts Authorization: Bearer followed by the token.'),
    quiz(2, 'Why fill the cart through the API before a cart page test?', ['APIs are prettier', 'it is faster and the test fails only for cart page problems', 'pages cannot add to cart', 'it is required'], 1,
         'Fewer steps, fewer reasons to fail.', 'Set up through the API is fast and keeps unrelated pages from failing the test.'),
    quiz(2, 'Do page.request calls share cookies with the page?', ['no', 'yes, they use the same context', 'only in Java', 'only with a flag'], 1,
         'Read the tip in the mix part.', 'page.request and context.request share the cookie storage of the browser context.'),
    quiz(3, 'Your tests change account settings and run in parallel. What is the safer approach?', ['one shared account', 'one account per worker', 'no sign in', 'retries'], 1,
         'Parallel tests must not share changing data.', 'One account per worker keeps parallel tests from changing each other\'s data.'),
    quiz(3, 'What does storageState not save?', ['cookies', 'local storage', 'session storage', 'the origin'], 2,
         'Read the table in the last part.', 'sessionStorage is not saved. Save and restore it yourself when an app needs it.'),
    quiz(3, 'In pytest-playwright, how do all tests start signed in?', ['a pytest.ini option', 'browser_context_args returns storage_state', 'a --signed-in flag', 'conftest.py is not needed'], 1,
         'Look at the conftest in the state example.', 'Overriding browser_context_args with storage_state makes every context start from the saved file.'),
]

CALC = [
    calc(1, 'Signing in through the page takes 3 s. How many seconds do 200 tests spend signing in when each signs in itself?', 600, '200 × 3', ['200 × 3 = 600 s']),
    calc(1, 'With storageState, the same suite signs in once. How many seconds does it save?', 597, '600 - 3', ['600 s before, 3 s now', '600 - 3 = 597 s']),
    calc(2, 'Two mugs cost ₹199 each. What total should the cart API report?', 398, '2 × 199', ['2 × 199 = 398']),
    calc(2, 'A test creates 3 people and deletes 1. The list was empty. How many people are left?', 2, '3 - 1', ['3 - 1 = 2']),
    calc(2, 'Clicking through 5 pages to set up a cart takes 2 s per page. One API call takes 1 s. How many seconds does the API save?', 9, '5 × 2 - 1', ['5 × 2 = 10 s', '10 - 1 = 9 s']),
    calc(3, '4 workers each need their own account, and 2 roles are tested. How many state files?', 8, '4 × 2', ['4 accounts per role', '4 × 2 = 8']),
    calc(3, 'An API test takes 50 ms and the same check in the UI takes 2 s. How many API tests fit in the time of one UI test?', 40, '2000 / 50', ['2 s = 2000 ms', '2000 / 50 = 40']),
    calc(3, 'The lamp costs ₹1,299 and a pen ₹20. The cart has 1 lamp and 3 pens. What is the total in rupees?', 1359, '1299 + 3 × 20', ['3 × 20 = 60', '1299 + 60 = 1359']),
]

LABS = [
    {'id': 'ravi', 'title': 'Sign in as the admin', 'name': 'Ravi can sign in',
     'task': 'Sign in on <code>/login</code> as <code>ravi@shop.example</code> with the password <code>admin123</code>, and check that the header says <b>Hello, Ravi</b>.',
     'goal': 'Ravi is signed in.', 'start': '/login',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('Ravi can sign in', async ({ page }) => {
  await page.goto('/login');
  // fill in Ravi's email and password, sign in, and check the greeting
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('Ravi can sign in', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('ravi@shop.example');
  await page.getByLabel('Password').fill('admin123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByText('Hello, Ravi')).toBeVisible();
});'''},
     'hint': 'The same steps as for Asha, with Ravi\'s email and <code>admin123</code>.',
     'why': 'In a real suite these steps run once in a setup step for each role, and save ravi.json next to asha.json. Admin tests then start from ravi.json.',
     'check': [['ctx.loggedIn', 'Someone is signed in'], ["/Hello, Ravi/.test(ctx.text)", 'The header greets Ravi']]},
    {'id': 'order', 'title': 'Place a real order', 'name': 'Asha places an order',
     'task': 'Sign in as Asha (<code>asha@shop.example</code>, <code>s3cret</code>), add the <b>Coffee mug</b>, open <code>/cart</code>, accept the confirmation dialog and click <b>Place order</b>. Check that the status says the order was <b>placed</b>.',
     'goal': 'One order is placed.', 'start': '/login',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('Asha places an order', async ({ page }) => {
  await page.goto('/login');
  // sign in, add the mug, open the cart, accept the dialog and place the order
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('Asha places an order', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('s3cret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByText('Hello, Asha')).toBeVisible();
  await page.getByTestId('product-2').getByRole('button', { name: 'Add to cart' }).click();
  await expect(page.getByTestId('cart-count')).toHaveText('1');
  await page.goto('/cart');
  page.on('dialog', dialog => dialog.accept());
  await page.getByRole('button', { name: 'Place order' }).click();
  await expect(page.getByRole('status')).toContainText('placed');
});'''},
     'hint': "Register the dialog handler before the click: <code>page.on('dialog', dialog => dialog.accept());</code>",
     'why': 'Everything before page.goto(\'/cart\') is set up. In a real suite it would be one API call and a saved state, and the test would start on the cart page.',
     'check': [['ctx.orders === 1', 'One order was placed'], ["/placed/.test(ctx.text)", 'The page says the order was placed']]},
]

T = {
    'slug': 'pw-api', 'title': 'API testing and signing in once', 'short': 'API and auth', 'emoji': '🔑', 'module': MODULE, 'minutes': 24,
    'lead': 'Test the server directly with the request client, send tokens in headers, set up data through the API before a short UI check, and sign in once so every test starts signed in.',
    'desc': 'The request fixture, APIRequestContext and playwright.request, GET, POST, PATCH and DELETE, status codes and toBeOK, extraHTTPHeaders and Bearer tokens, page.request with shared cookies, addInitScript, storageState, setup projects, browser_context_args and multiple roles.',
    'summary': 'A full create, read, update and delete test of the people API with a validation error, a token sent in a header, a cart filled through the API and checked in the page, and a saved sign in reused by every test.',
    'keywords': ['API testing', 'request', 'APIRequestContext', 'post', 'patch', 'delete', 'toBeOK', 'token', 'Bearer', 'extraHTTPHeaders', 'storageState', 'auth', 'setup project', 'browser_context_args', 'roles'],
    'plain': 'Many checks do not need a browser at all, and many tests only need a browser for the last step. Calling the API directly makes those tests fast, and saving the sign in once makes every other test faster.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
