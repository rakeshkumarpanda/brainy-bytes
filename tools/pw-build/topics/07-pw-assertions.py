from pkit import part, say, quiz, calc, panel, four, one, js, ts, py, jv, shown, walk, step, table, tip, by, viz, figure

MODULE = ('🎯', 'Finding and using elements', 'pw-elements', 'Locators, actions with auto-waiting, and assertions that retry by themselves.')

JAVA_TRIM = [(r'(?ms)^\tat .*?(?=^\[INFO\]|^\[ERROR\]|\Z)', ''), (r'(?m)^\[ERROR\] (Please refer|To see the full|Re-run Maven|For more information|-> \[Help|\s*$).*\n?', ''),
             (r'(?m)^\[ERROR\] Failed to execute goal.*\n', ''), (r'(?ms)^\[INFO\] \n\[INFO\] Results:.*?(?=^\[ERROR\] Tests run:)', '')]
PY_TRIM = [(r'/\S*/box/\.venv/', '.venv/')]

# ---------- web-first assertions retry ----------
RETRY_TS = '''import { test, expect } from '@playwright/test';

test('a web-first check waits, a plain read does not', async ({ page }) => {
  await page.goto('/widgets');
  await page.getByRole('button', { name: 'Load offers' }).click();
  const offer = page.getByTestId('offer');      // shows up 1.2 s after the click

  console.log('isVisible() right now:', await offer.isVisible());   // a snapshot, no waiting
  await expect(offer).toBeVisible();                                 // retries until it shows
  console.log('isVisible() after the check:', await offer.isVisible());
});'''

RETRY_PY = '''from playwright.sync_api import Page, expect


def test_a_web_first_check_waits_a_plain_read_does_not(page: Page):
    page.goto("/widgets")
    page.get_by_role("button", name="Load offers").click()
    offer = page.get_by_test_id("offer")      # shows up 1.2 s after the click

    print("is_visible() right now:", offer.is_visible())   # a snapshot, no waiting
    expect(offer).to_be_visible()                          # retries until it shows
    print("is_visible() after the check:", offer.is_visible())'''

RETRY_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class RetryTest {
  @Test
  void aWebFirstCheckWaitsAPlainReadDoesNot(Page page) {
    page.navigate("/widgets");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Load offers")).click();
    Locator offer = page.getByTestId("offer");      // shows up 1.2 s after the click

    System.out.println("isVisible() right now: " + offer.isVisible());   // a snapshot, no waiting
    assertThat(offer).isVisible();                                       // retries until it shows
    System.out.println("isVisible() after the check: " + offer.isVisible());
  }
}'''

# ---------- one check for each thing a user notices ----------
MANY_TS = '''import { test, expect } from '@playwright/test';

test('one check for each thing a user can notice', async ({ page }) => {
  await page.goto('/login');
  await expect(page).toHaveTitle('Sign in · Brainy Shop');
  await expect(page).toHaveURL(/\\/login$/);

  const email = page.getByLabel('Email');
  await expect(email).toBeEmpty();
  await expect(email).toBeEditable();
  await expect(email).toHaveAttribute('type', 'email');
  await expect(email).toHaveRole('textbox');
  await email.fill('asha@shop.example');
  await expect(email).toHaveValue('asha@shop.example');
  await expect(email).toBeFocused();

  await expect(page.getByRole('checkbox', { name: 'Remember me' })).not.toBeChecked();
  await expect(page.getByRole('alert')).toBeHidden();
  const signIn = page.getByRole('button', { name: 'Sign in' });
  await expect(signIn).toBeEnabled();
  await expect(signIn).toHaveCSS('background-color', 'rgb(22, 163, 74)');
  await expect(signIn).toBeInViewport();
  await expect(page.getByRole('form')).toHaveAccessibleName('Sign in');
  console.log('all 15 checks passed');
});'''

MANY_PY = '''import re
from playwright.sync_api import Page, expect


def test_one_check_for_each_thing_a_user_can_notice(page: Page):
    page.goto("/login")
    expect(page).to_have_title("Sign in · Brainy Shop")
    expect(page).to_have_url(re.compile(r"/login$"))

    email = page.get_by_label("Email")
    expect(email).to_be_empty()
    expect(email).to_be_editable()
    expect(email).to_have_attribute("type", "email")
    expect(email).to_have_role("textbox")
    email.fill("asha@shop.example")
    expect(email).to_have_value("asha@shop.example")
    expect(email).to_be_focused()

    expect(page.get_by_role("checkbox", name="Remember me")).not_to_be_checked()
    expect(page.get_by_role("alert")).to_be_hidden()
    sign_in = page.get_by_role("button", name="Sign in")
    expect(sign_in).to_be_enabled()
    expect(sign_in).to_have_css("background-color", "rgb(22, 163, 74)")
    expect(sign_in).to_be_in_viewport()
    expect(page.get_by_role("form")).to_have_accessible_name("Sign in")
    print("all 15 checks passed")'''

MANY_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;
import java.util.regex.Pattern;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class ManyChecksTest {
  @Test
  void oneCheckForEachThingAUserCanNotice(Page page) {
    page.navigate("/login");
    assertThat(page).hasTitle("Sign in · Brainy Shop");
    assertThat(page).hasURL(Pattern.compile("/login$"));

    Locator email = page.getByLabel("Email");
    assertThat(email).isEmpty();
    assertThat(email).isEditable();
    assertThat(email).hasAttribute("type", "email");
    assertThat(email).hasRole(AriaRole.TEXTBOX);
    email.fill("asha@shop.example");
    assertThat(email).hasValue("asha@shop.example");
    assertThat(email).isFocused();

    assertThat(page.getByRole(AriaRole.CHECKBOX, new Page.GetByRoleOptions().setName("Remember me"))).not().isChecked();
    assertThat(page.getByRole(AriaRole.ALERT)).isHidden();
    Locator signIn = page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in"));
    assertThat(signIn).isEnabled();
    assertThat(signIn).hasCSS("background-color", "rgb(22, 163, 74)");
    assertThat(signIn).isInViewport();
    assertThat(page.getByRole(AriaRole.FORM)).hasAccessibleName("Sign in");
    System.out.println("all 15 checks passed");
  }
}'''

# ---------- text checks ----------
TEXT_TS = '''import { test, expect } from '@playwright/test';

test('text checks for one element and for a list', async ({ page }) => {
  await page.goto('/products');
  const names = page.getByRole('listitem').getByRole('heading');

  // A list: every element, in this order.
  await expect(names).toHaveText(['Coffee mug', 'Desk lamp', 'Gel pen', 'Notebook', 'Water bottle']);
  // A list: some elements contain these texts, in this order.
  await expect(names).toContainText(['mug', 'pen']);

  await expect(page.getByRole('heading', { level: 1 })).toHaveText('products', { ignoreCase: true });
  await expect(page.getByTestId('product-3')).toContainText('₹1,299');
  await expect(page.getByTestId('product-3')).toHaveText(/Desk lamp.*Home/);

  await page.getByRole('combobox', { name: 'Sort by' }).selectOption('low');
  await expect(names).toHaveText(['Gel pen', 'Notebook', 'Coffee mug', 'Water bottle', 'Desk lamp']);
  console.log('sorted:', await names.allTextContents());
});'''

TEXT_PY = '''import re
from playwright.sync_api import Page, expect


def test_text_checks_for_one_element_and_for_a_list(page: Page):
    page.goto("/products")
    names = page.get_by_role("listitem").get_by_role("heading")

    # A list: every element, in this order.
    expect(names).to_have_text(["Coffee mug", "Desk lamp", "Gel pen", "Notebook", "Water bottle"])
    # A list: some elements contain these texts, in this order.
    expect(names).to_contain_text(["mug", "pen"])

    expect(page.get_by_role("heading", level=1)).to_have_text("products", ignore_case=True)
    expect(page.get_by_test_id("product-3")).to_contain_text("₹1,299")
    expect(page.get_by_test_id("product-3")).to_have_text(re.compile(r"Desk lamp.*Home"))

    page.get_by_role("combobox", name="Sort by").select_option("low")
    expect(names).to_have_text(["Gel pen", "Notebook", "Coffee mug", "Water bottle", "Desk lamp"])
    print("sorted:", names.all_text_contents())'''

TEXT_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.LocatorAssertions;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;
import java.util.regex.Pattern;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class TextTest {
  @Test
  void textChecksForOneElementAndForAList(Page page) {
    page.navigate("/products");
    Locator names = page.getByRole(AriaRole.LISTITEM).getByRole(AriaRole.HEADING);

    // A list: every element, in this order.
    assertThat(names).hasText(new String[] {"Coffee mug", "Desk lamp", "Gel pen", "Notebook", "Water bottle"});
    // A list: some elements contain these texts, in this order.
    assertThat(names).containsText(new String[] {"mug", "pen"});

    assertThat(page.getByRole(AriaRole.HEADING, new Page.GetByRoleOptions().setLevel(1)))
        .hasText("products", new LocatorAssertions.HasTextOptions().setIgnoreCase(true));
    assertThat(page.getByTestId("product-3")).containsText("₹1,299");
    assertThat(page.getByTestId("product-3")).hasText(Pattern.compile("Desk lamp.*Home"));

    page.getByRole(AriaRole.COMBOBOX, new Page.GetByRoleOptions().setName("Sort by")).selectOption("low");
    assertThat(names).hasText(new String[] {"Gel pen", "Notebook", "Coffee mug", "Water bottle", "Desk lamp"});
    System.out.println("sorted: " + names.allTextContents());
  }
}'''

# ---------- negative checks ----------
NOT_TS = '''import { test, expect } from '@playwright/test';

test('negative checks wait too', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByText('Loading products…')).not.toBeVisible();   // waits until it goes away
  await expect(page.getByText('No products match your search')).toHaveCount(0);

  await page.getByPlaceholder('Search products').fill('phone');
  await expect(page.getByRole('listitem')).toHaveText('No products match your search');
  await expect(page.getByRole('button', { name: 'Add to cart' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Add to cart' })).not.toBeAttached();
  console.log('nothing to buy when searching for phone');
});'''

NOT_PY = '''from playwright.sync_api import Page, expect


def test_negative_checks_wait_too(page: Page):
    page.goto("/products")
    expect(page.get_by_text("Loading products…")).not_to_be_visible()   # waits until it goes away
    expect(page.get_by_text("No products match your search")).to_have_count(0)

    page.get_by_placeholder("Search products").fill("phone")
    expect(page.get_by_role("listitem")).to_have_text("No products match your search")
    expect(page.get_by_role("button", name="Add to cart")).to_have_count(0)
    expect(page.get_by_role("button", name="Add to cart")).not_to_be_attached()
    print("nothing to buy when searching for phone")'''

NOT_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class NegativeTest {
  @Test
  void negativeChecksWaitToo(Page page) {
    page.navigate("/products");
    assertThat(page.getByText("Loading products…")).not().isVisible();   // waits until it goes away
    assertThat(page.getByText("No products match your search")).hasCount(0);

    page.getByPlaceholder("Search products").fill("phone");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasText("No products match your search");
    assertThat(page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Add to cart"))).hasCount(0);
    assertThat(page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Add to cart"))).not().isAttached();
    System.out.println("nothing to buy when searching for phone");
  }
}'''

# ---------- a failing check ----------
FAIL_TS = '''import { test, expect } from '@playwright/test';

test('a failing check explains itself', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByRole('listitem')).toHaveCount(5);
  await expect(page.getByTestId('product-2'), 'the mug should cost 149 in the sale')
    .toContainText('₹149', { timeout: 2000 });
});'''

FAIL_PY = '''from playwright.sync_api import Page, expect


def test_a_failing_check_explains_itself(page: Page):
    page.goto("/products")
    expect(page.get_by_role("listitem")).to_have_count(5)
    expect(page.get_by_test_id("product-2"), "the mug should cost 149 in the sale") \\
        .to_contain_text("₹149", timeout=2000)'''

FAIL_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.LocatorAssertions;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class FailingTest {
  @Test
  void aFailingCheckExplainsItself(Page page) {
    page.navigate("/products");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(5);
    // Java has no message argument. The test name and a comment carry the intent.
    assertThat(page.getByTestId("product-2"))
        .containsText("₹149", new LocatorAssertions.ContainsTextOptions().setTimeout(2000));
  }
}'''

# ---------- soft assertions ----------
SOFT_TS = '''import { test, expect } from '@playwright/test';

test('soft checks report every problem at once', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByRole('listitem')).toHaveCount(5);

  await expect.soft(page.getByTestId('product-1')).toContainText('₹25', { timeout: 1000 });          // wrong on purpose
  await expect.soft(page.getByTestId('product-4')).toContainText('Add to cart', { timeout: 1000 });  // wrong on purpose
  await expect.soft(page.getByTestId('product-5')).toContainText('₹349');                           // right
  console.log('the test kept going after', test.info().errors.length, 'failed checks');
});'''

SOFT_PY = '''from playwright.sync_api import Page, expect


def test_soft_checks_report_every_problem_at_once(page: Page):
    page.goto("/products")
    expect(page.get_by_role("listitem")).to_have_count(5)

    expect.soft(page.get_by_test_id("product-1")).to_contain_text("₹25", timeout=1000)          # wrong on purpose
    expect.soft(page.get_by_test_id("product-4")).to_contain_text("Add to cart", timeout=1000)  # wrong on purpose
    expect.soft(page.get_by_test_id("product-5")).to_contain_text("₹349")                       # right
    print("the test kept going after the failed checks")'''

SOFT_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.LocatorAssertions;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertAll;

@UsePlaywright(ShopOptions.class)
public class SoftTest {
  @Test
  void softChecksReportEveryProblemAtOnce(Page page) {
    page.navigate("/products");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(5);
    LocatorAssertions.ContainsTextOptions quick = new LocatorAssertions.ContainsTextOptions().setTimeout(1000);

    // JUnit 5 runs every check in the group and reports all failures together.
    assertAll("product cards",
        () -> assertThat(page.getByTestId("product-1")).containsText("₹25", quick),          // wrong on purpose
        () -> assertThat(page.getByTestId("product-4")).containsText("Add to cart", quick),  // wrong on purpose
        () -> assertThat(page.getByTestId("product-5")).containsText("₹349"));               // right
  }
}'''

# ---------- plain value checks ----------
VAL_TS = '''import { test, expect } from '@playwright/test';

test('plain value checks for data you already have', async ({ page }) => {
  const response = await page.request.get('/api/products?delay=0');
  await expect(response).toBeOK();                  // a web-first check for API answers
  const products = await response.json();

  expect(products).toHaveLength(5);                 // plain checks: no waiting, no await
  expect(products.map((p: { name: string }) => p.name)).toContain('Desk lamp');
  expect(products[0]).toEqual({ id: 1, name: 'Gel pen', price: 20, stock: 120, category: 'Stationery' });
  expect(products[2].price).toBeGreaterThan(1000);
  console.log('cheapest:', Math.min(...products.map((p: { price: number }) => p.price)));
});'''

VAL_JS = VAL_TS.replace('(p: { name: string })', 'p').replace('(p: { price: number })', 'p')

VAL_PY = '''from playwright.sync_api import Page, expect


def test_plain_value_checks_for_data_you_already_have(page: Page):
    response = page.request.get("/api/products?delay=0")
    expect(response).to_be_ok()                       # a Playwright check for API answers
    products = response.json()

    assert len(products) == 5                         # plain Python checks
    assert "Desk lamp" in [p["name"] for p in products]
    assert products[0] == {"id": 1, "name": "Gel pen", "price": 20, "stock": 120, "category": "Stationery"}
    assert products[2]["price"] > 1000
    print("cheapest:", min(p["price"] for p in products))'''

VAL_JAVA = '''package com.brainy;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.microsoft.playwright.APIResponse;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import org.junit.jupiter.api.Test;
import java.util.ArrayList;
import java.util.List;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;
import static org.junit.jupiter.api.Assertions.*;

@UsePlaywright(ShopOptions.class)
public class ValueTest {
  @Test
  void plainValueChecksForDataYouAlreadyHave(Page page) {
    APIResponse response = page.request().get("/api/products?delay=0");
    assertThat(response).isOK();                    // a Playwright check for API answers
    JsonArray products = new Gson().fromJson(response.text(), JsonArray.class);   // Gson comes with Playwright

    assertEquals(5, products.size());               // plain JUnit checks
    List<String> names = new ArrayList<>();
    for (JsonElement p : products) names.add(p.getAsJsonObject().get("name").getAsString());
    assertTrue(names.contains("Desk lamp"));
    assertEquals("Gel pen", products.get(0).getAsJsonObject().get("name").getAsString());
    assertTrue(products.get(2).getAsJsonObject().get("price").getAsInt() > 1000);
    int cheapest = Integer.MAX_VALUE;
    for (JsonElement p : products) cheapest = Math.min(cheapest, p.getAsJsonObject().get("price").getAsInt());
    System.out.println("cheapest: " + cheapest);
  }
}'''

# ---------- poll and toPass (Playwright Test only) ----------
POLL_TS = '''import { test, expect } from '@playwright/test';

test('expect.poll and toPass retry your own code', async ({ page }) => {
  await page.goto('/products');
  // Poll any value until it matches: here a count read with a plain call.
  await expect.poll(() => page.locator('li.card').count(), { timeout: 5000 }).toBe(5);

  // Retry a whole block until every check inside it passes.
  let tries = 0;
  await expect(async () => {
    tries++;
    const response = await page.request.get('/api/products?delay=0');
    expect(response.status()).toBe(200);
    expect(tries).toBeGreaterThanOrEqual(3);     // the first two tries fail on purpose
  }).toPass({ intervals: [100, 200, 500] });
  console.log('the block passed on try', tries);

  const slowExpect = expect.configure({ timeout: 10_000 });   // a copy of expect with other defaults
  await slowExpect(page.getByRole('heading', { level: 1 })).toHaveText('Products');
});'''

POLL_JS = POLL_TS

CODES = {
    'retry': four('A web-first check against a plain read',
                  java=jv({'RetryTest.java': RETRY_JAVA}),
                  py=py({'test_retry.py': RETRY_PY}, cmd='pytest -v -s'),
                  js=js({'retry.spec.js': RETRY_TS}),
                  ts=ts({'retry.spec.ts': RETRY_TS}),
                  result='Right after the click the offer is not there yet, so <code>isVisible()</code> says false. It reads the page once and returns. <code>expect(...).toBeVisible()</code> kept checking until the offer appeared. A test written as <code>expect(await offer.isVisible()).toBe(true)</code> would have failed here for no good reason.'),
    'many': four('Fifteen checks on the sign in page',
                 java=jv({'ManyChecksTest.java': MANY_JAVA}),
                 py=py({'test_many_checks.py': MANY_PY}, cmd='pytest -v -s'),
                 js=js({'many-checks.spec.js': MANY_TS}),
                 ts=ts({'many-checks.spec.ts': MANY_TS}),
                 result='Each check reads one thing a user or a screen reader can notice: the title, the address, an empty box, its type, a ticked box, a hidden error, the colour of a button. The colour comes back in the rgb form the browser computes, even though the style sheet says #16a34a.'),
    'text': four('toHaveText and toContainText for one element and for lists',
                 java=jv({'TextTest.java': TEXT_JAVA}),
                 py=py({'test_text.py': TEXT_PY}, cmd='pytest -v -s'),
                 js=js({'text.spec.js': TEXT_TS}),
                 ts=ts({'text.spec.ts': TEXT_TS}),
                 result='With a list, <code>toHaveText</code> wants exactly these elements in exactly this order, which makes it a good check for sorting. <code>toContainText</code> with a list is looser: some elements, in this order, each containing a part of the text. A regular expression gives full control, and ignoreCase relaxes the case.'),
    'not': four('Checks that something is gone',
                java=jv({'NegativeTest.java': NOT_JAVA}),
                py=py({'test_negative.py': NOT_PY}, cmd='pytest -v -s'),
                js=js({'negative.spec.js': NOT_TS}),
                ts=ts({'negative.spec.ts': NOT_TS}),
                result='A negative check also retries. <code>not.toBeVisible()</code> waited for the loading message to go away, and the count checks waited for the cards to be replaced by the empty message.'),
    'fail': four('What a failing check looks like',
                 java=jv({'FailingTest.java': FAIL_JAVA}, expect='fail', replace=JAVA_TRIM),
                 py=py({'test_failing.py': FAIL_PY}, expect='fail'),
                 js=js({'failing.spec.js': FAIL_TS}, expect='fail'),
                 ts=ts({'failing.spec.ts': FAIL_TS}, expect='fail'),
                 result='This test fails on purpose, because the mug costs ₹199. The report shows what was expected, what the page really had, how long it waited, and the call log. In JavaScript and Python the custom message comes first, so a reader knows the intent before the details. Python also prints an aria snapshot, a short outline of the element as a screen reader sees it, and Playwright Test points to an error-context.md file it saved with the results.'),
    'soft': four('Soft checks: keep going, then fail with every problem',
                 java=jv({'SoftTest.java': SOFT_JAVA}, expect='fail', replace=JAVA_TRIM),
                 py=py({'test_soft.py': SOFT_PY}, cmd='pytest -v -s', expect='fail', replace=PY_TRIM),
                 js=js({'soft.spec.js': SOFT_TS}, expect='fail'),
                 ts=ts({'soft.spec.ts': SOFT_TS}, expect='fail'),
                 result='Two of the three checks are wrong on purpose. With soft checks the test still ran to the end, and the report lists both problems instead of only the first. Java has no soft assertions in Playwright, so the Java version uses <code>assertAll</code> from JUnit 5, which gives the same result.'),
    'values': four('Plain checks on data you already have',
                   java=jv({'ValueTest.java': VAL_JAVA}),
                   py=py({'test_values.py': VAL_PY}, cmd='pytest -v -s'),
                   js=js({'values.spec.js': VAL_JS}),
                   ts=ts({'values.spec.ts': VAL_TS}),
                   result='The products came from the API, so they are plain data in your language and there is nothing to wait for. Each language uses its usual checks: <code>expect(value)</code> in Playwright Test, <code>assert</code> in Python and JUnit assertions in Java. Only the response check is a Playwright assertion.'),
    'poll': four('expect.poll, toPass and expect.configure',
                 js=js({'poll.spec.js': POLL_JS}),
                 ts=ts({'poll.spec.ts': POLL_TS}),
                 result='These three are part of Playwright Test, so they exist in JavaScript and TypeScript only. <code>expect.poll</code> keeps calling your function until the value matches, and <code>toPass</code> retries a whole block. In Python and Java, reach for a locator assertion or <code>wait_for_function</code> / <code>waitForFunction</code> instead.'),
    'walkcheck': walk('Checking a search, one assertion at a time', [
        step('Open the products page.', "await page.goto('http://localhost:4173/products');", 'page.goto("http://localhost:4173/products")', 'page.navigate("http://localhost:4173/products");'),
        step('The check waits until the slow product list has loaded.', "await expect(page.getByRole('listitem')).toHaveCount(5);",
             'expect(page.get_by_role("listitem")).to_have_count(5)', 'assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(5);'),
        step('Search for bottle.', "await page.getByPlaceholder('Search products').fill('bottle');",
             'page.get_by_placeholder("Search products").fill("bottle")', 'page.getByPlaceholder("Search products").fill("bottle");'),
        step('One card is left, and it is the right one.', "await expect(page.getByRole('listitem')).toContainText('Water bottle');",
             'expect(page.get_by_role("listitem")).to_contain_text("Water bottle")', 'assertThat(page.getByRole(AriaRole.LISTITEM)).containsText("Water bottle");'),
        step('The search box keeps what was typed.', "await expect(page.getByPlaceholder('Search products')).toHaveValue('bottle');",
             'expect(page.get_by_placeholder("Search products")).to_have_value("bottle")', 'assertThat(page.getByPlaceholder("Search products")).hasValue("bottle");'),
        step('Search for something the shop does not sell.', "await page.getByPlaceholder('Search products').fill('phone');",
             'page.get_by_placeholder("Search products").fill("phone")', 'page.getByPlaceholder("Search products").fill("phone");'),
        step('No Add to cart buttons are left. A negative check also waits.', "await expect(page.getByRole('button', { name: 'Add to cart' })).toHaveCount(0);",
             'expect(page.get_by_role("button", name="Add to cart")).to_have_count(0)', 'assertThat(page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Add to cart"))).hasCount(0);'),
    ], start="", size=(900, 520)),
}

DG = {
    'retry': {'t': 'How a web-first assertion decides', 'w': 900, 'h': 230,
              'n': [['read', 30, 80, 150, 64, 'read the page', {'c': 5, 'sub': 'find the element', 'i': 'The locator is resolved and the value is read, such as the text.'}],
                    ['cmp', 230, 80, 150, 64, 'compare', {'c': 3, 'sub': 'expected or not', 'i': 'The value is compared with what you expect.'}],
                    ['pass', 440, 20, 150, 60, 'pass', {'c': 1, 'sub': 'go on', 'i': 'The value matches. The next line of the test runs at once.'}],
                    ['wait', 440, 140, 150, 60, 'wait a little', {'c': 2, 'sub': 'then read again', 'i': 'Not yet. Wait a short moment and read the page again.'}],
                    ['fail', 680, 140, 190, 60, 'timeout reached', {'c': 0, 'sub': 'fail with details', 'i': 'After 5 seconds by default, fail with the expected value, the real value and the call log.'}]],
              'e': [['read', 'cmp'], ['cmp', 'pass'], ['cmp', 'wait'], ['wait', 'fail']],
              'st': [[['read'], 'The check finds the element and reads the value it needs.'],
                     [['cmp', 'read>cmp'], 'It compares the value with what you expect.'],
                     [['pass', 'cmp>pass'], 'If it matches, the check passes at once. No time is wasted.'],
                     [['wait', 'cmp>wait'], 'If it does not match yet, it waits a little and reads again, over and over.'],
                     [['fail', 'wait>fail'], 'Only when the timeout runs out does it fail, with a message that shows both values.']]},
}

PARTS = [
    part('webfirst', '✅', 'Web-first assertions retry', f'''
<p>An assertion checks that the page is the way it should be. Playwright assertions are <b>web-first</b>: they know the page is still changing, so they keep checking until the condition is true or the timeout ends. The default timeout is 5 seconds.</p>
<div class="viz" data-viz="flow" data-k="retry"></div>
[[retry]]
{tip('A rule that catches many flaky tests: never put await inside expect. Write ' + by(java='<code>assertThat(locator).isVisible()</code>, not <code>assertTrue(locator.isVisible())</code>', py='<code>expect(locator).to_be_visible()</code>, not <code>assert locator.is_visible()</code>', js='<code>await expect(locator).toBeVisible()</code>, not <code>expect(await locator.isVisible()).toBe(true)</code>') + '.', 'warn')}
''', easy=True, kw=['assertion', 'expect', 'assertThat', 'web-first', 'retry', 'isVisible']),

    part('kinds', '📚', 'The assertions you will use every day', f'''
<p>There is one assertion for each thing a user can notice. In JavaScript and TypeScript they start with <code>to</code>, in Python with <code>to_</code>, and in Java with <code>is</code> or <code>has</code> after <code>assertThat</code>.</p>
[[many]]
{table(['Checks', 'JavaScript and TypeScript', 'Python', 'Java'], [
    ['visible or hidden', 'toBeVisible, toBeHidden', 'to_be_visible, to_be_hidden', 'isVisible, isHidden'],
    ['text', 'toHaveText, toContainText', 'to_have_text, to_contain_text', 'hasText, containsText'],
    ['how many', 'toHaveCount', 'to_have_count', 'hasCount'],
    ['box value', 'toHaveValue, toHaveValues, toBeEmpty', 'to_have_value, to_have_values, to_be_empty', 'hasValue, hasValues, isEmpty'],
    ['state', 'toBeChecked, toBeEnabled, toBeDisabled, toBeEditable, toBeFocused', 'to_be_checked, to_be_enabled, ...', 'isChecked, isEnabled, ...'],
    ['attributes and style', 'toHaveAttribute, toHaveClass, toContainClass, toHaveCSS, toHaveId', 'to_have_attribute, to_have_class, ...', 'hasAttribute, hasClass, ...'],
    ['accessibility', 'toHaveRole, toHaveAccessibleName, toHaveAccessibleDescription', 'to_have_role, ...', 'hasRole, ...'],
    ['the page', 'toHaveTitle, toHaveURL', 'to_have_title, to_have_url', 'hasTitle, hasURL'],
    ['an API answer', 'toBeOK', 'to_be_ok', 'isOK'],
    ['pictures and structure', 'toHaveScreenshot, toMatchAriaSnapshot', 'to_match_aria_snapshot', 'matchesAriaSnapshot'],
])}
''', easy=True, kw=['toHaveText', 'toBeVisible', 'toHaveCount', 'toHaveValue', 'toHaveAttribute', 'toHaveCSS', 'toHaveURL', 'toHaveTitle', 'toHaveRole']),

    part('text', '🔤', 'Checking text and lists', f'''
<p>Text checks are the most common checks of all. Both kinds ignore extra spaces and line breaks, so the layout of the HTML does not matter.</p>
[[text]]
{table(['Assertion', 'With a string', 'With a list of strings'], [
    ['toHaveText', 'the whole text must match', 'exactly these elements, in this order'],
    ['toContainText', 'the text must contain it', 'some elements, in this order, containing these parts'],
])}
''', easy=True, kw=['toHaveText', 'toContainText', 'ignoreCase', 'regex', 'list', 'order']),

    part('negative', '🙅', 'Checking that something is not there', f'''
<p>Put <code>not</code> in front of any assertion: {by(java='<code>assertThat(x).not().isVisible()</code>', py='<code>expect(x).not_to_be_visible()</code>', js='<code>expect(x).not.toBeVisible()</code>')}. Negative checks retry too, so they wait for a spinner or an error message to go away.</p>
[[walkcheck]]
[[not]]
''', kw=['not', 'toBeHidden', 'toHaveCount(0)', 'toBeAttached', 'negative']),

    part('failing', '💥', 'Reading a failure', f'''
<p>A good failure tells you what went wrong without opening the browser. Playwright prints the expected value, the value it really saw, the timeout and the call log.</p>
[[fail]]
{tip('Change the timeout of one check with its timeout option, or of all checks: ' + by(java='<code>PlaywrightAssertions.setDefaultAssertionTimeout(10_000)</code>', py='<code>expect.set_options(timeout=10_000)</code> in conftest.py', js='<code>expect: { timeout: 10_000 }</code> in playwright.config') + '. Raise it for a slow test environment, not to hide a slow page.', 'tip')}
''', kw=['failure', 'error message', 'custom message', 'timeout', 'call log', 'diff']),

    part('soft', '🧽', 'Soft assertions', f'''
<p>A normal assertion stops the test at the first failure. A soft assertion records the failure and lets the test carry on, so one run tells you about every problem on the page. The test still fails at the end.</p>
[[soft]]
{tip('Soft checks are handy for a page with many independent fields, such as an invoice or a profile. Do not use them for steps the rest of the test depends on, such as signing in.', 'pro')}
''', kw=['soft assertion', 'expect.soft', 'assertAll', 'multiple failures']),

    part('values', '🔢', 'Plain values, polling and blocks', f'''
<p>Not everything is on the screen. For values you already hold, such as API data, use the normal checks of your language. They do not wait, because the value cannot change.</p>
[[values]]
<p>Playwright Test also has ways to retry your own code.</p>
[[poll]]
''', kw=['toEqual', 'toBe', 'assert', 'assertEquals', 'expect.poll', 'toPass', 'expect.configure']),
]

INFO = {'title': 'Checks that wait for the page', 'panels': [
    panel([['e', '✅'], ['t', 'expect(x)', {'b': 1}]], 'Web-first', 'Retries until true.', '5 seconds by default.'),
    panel([['e', '🔤'], ['t', 'toHaveText', {'b': 1}]], 'Text', 'Exact or contains.', 'Lists check order too.'),
    panel([['e', '🙅'], ['t', 'not', {'b': 1}]], 'Negative', 'Waits for things to go.', 'toHaveCount(0) for none.'),
    panel([['e', '🧽'], ['t', 'expect.soft', {'b': 1}]], 'Soft', 'Keep going.', 'Report every problem.')],
    'remember': 'Check the page with assertions that retry, and never read a value first and check it later.'}

REAL = [
    ['🧾', 'An invoice page', 'An accounting product checks 20 fields of an invoice with soft assertions, so one failed run shows every wrong total at once.'],
    ['🔍', 'Search results', 'An online shop checks that sorting by price gives the exact order of product names with one toHaveText list check.'],
    ['⏳', 'A flaky test fixed in one line', 'A team replaced expect(await banner.isVisible()).toBe(true) with await expect(banner).toBeVisible(). The test stopped failing on slow CI machines.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter is about assertions: checks that retry until the page is right, the everyday assertions, text and list checks, negative checks, reading a failure, soft assertions and plain value checks.',
        'यह अध्याय assertions के बारे में है: ऐसी जाँचें जो page सही होने तक दोबारा कोशिश करती हैं, रोज़ की assertions, text और list की जाँच, negative जाँच, failure पढ़ना, soft assertions और साधारण value की जाँच।',
        'ಈ ಅಧ್ಯಾಯ assertions ಬಗ್ಗೆ: page ಸರಿಯಾಗುವವರೆಗೆ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸುವ ಪರಿಶೀಲನೆಗಳು, ದಿನನಿತ್ಯದ assertions, text ಮತ್ತು list ಪರಿಶೀಲನೆ, negative ಪರಿಶೀಲನೆ, failure ಓದುವುದು, soft assertions ಮತ್ತು ಸಾಮಾನ್ಯ value ಪರಿಶೀಲನೆ.',
        'ଏହି ଅଧ୍ୟାୟ assertions ବିଷୟରେ: page ଠିକ୍ ହେବା ପର୍ଯ୍ୟନ୍ତ ପୁଣି ଚେଷ୍ଟା କରୁଥିବା ଯାଞ୍ଚ, ଦୈନନ୍ଦିନ assertions, text ଓ list ଯାଞ୍ଚ, negative ଯାଞ୍ଚ, failure ପଢ଼ିବା, soft assertions ଓ ସାଧାରଣ value ଯାଞ୍ଚ।',
        'يتناول هذا الفصل التأكيدات: فحوص تعيد المحاولة حتى تصبح الصفحة صحيحة، والتأكيدات اليومية، وفحص النصوص والقوائم، والفحوص السلبية، وقراءة الفشل، والتأكيدات المرنة، وفحص القيم العادية.',
        'Dieses Kapitel behandelt Assertions: Prüfungen, die wiederholen, bis die Seite stimmt, die alltäglichen Assertions, Text- und Listenprüfungen, negative Prüfungen, das Lesen eines Fehlers, Soft Assertions und einfache Wertprüfungen.'),
    say('webfirst', 'Web-first assertions', 'Playwright assertions keep checking the page until the condition is true or five seconds pass. A plain read such as is visible looks once and does not wait.',
        'Playwright assertions शर्त सही होने या पाँच सेकंड बीतने तक page जाँचती रहती हैं। is visible जैसा साधारण read एक बार देखता है और इंतज़ार नहीं करता।',
        'Playwright assertions ಷರತ್ತು ಸರಿಯಾಗುವವರೆಗೆ ಅಥವಾ ಐದು ಸೆಕೆಂಡು ಕಳೆಯುವವರೆಗೆ page ಪರಿಶೀಲಿಸುತ್ತಲೇ ಇರುತ್ತವೆ. is visible ನಂತಹ ಸಾಮಾನ್ಯ read ಒಮ್ಮೆ ನೋಡುತ್ತದೆ ಮತ್ತು ಕಾಯುವುದಿಲ್ಲ.',
        'Playwright assertions ସର୍ତ୍ତ ଠିକ୍ ହେବା ବା ପାଞ୍ଚ ସେକେଣ୍ଡ ବିତିବା ପର୍ଯ୍ୟନ୍ତ page ଯାଞ୍ଚ କରନ୍ତି। is visible ପରି ସାଧାରଣ read ଥରେ ଦେଖେ ଏବଂ ଅପେକ୍ଷା କରେ ନାହିଁ।',
        'تستمر تأكيدات Playwright في فحص الصفحة حتى يتحقق الشرط أو تمر خمس ثوان. أما القراءة العادية مثل is visible فتنظر مرة واحدة ولا تنتظر.',
        'Playwright-Assertions prüfen die Seite so lange, bis die Bedingung stimmt oder fünf Sekunden vergehen. Ein einfaches Lesen wie is visible schaut einmal und wartet nicht.'),
    say('kinds', 'Everyday assertions', 'There is an assertion for each thing a user notices: visibility, text, count, value, state, attributes, style, accessible name, the title and the URL.',
        'हर उस चीज़ के लिए assertion है जो user देखता है: दिखना, text, गिनती, value, स्थिति, attributes, style, accessible name, title और URL।',
        'User ಗಮನಿಸುವ ಪ್ರತಿಯೊಂದಕ್ಕೂ assertion ಇದೆ: ಕಾಣುವುದು, text, ಎಣಿಕೆ, value, ಸ್ಥಿತಿ, attributes, style, accessible name, title ಮತ್ತು URL.',
        'User ଲକ୍ଷ୍ୟ କରୁଥିବା ପ୍ରତିଟି ଜିନିଷ ପାଇଁ assertion ଅଛି: ଦେଖାଯିବା, text, ଗଣନା, value, ସ୍ଥିତି, attributes, style, accessible name, title ଓ URL।',
        'هناك تأكيد لكل شيء يلاحظه المستخدم: الظهور والنص والعدد والقيمة والحالة والسمات والنمط والاسم الميسر والعنوان وعنوان URL.',
        'Für alles, was ein Nutzer bemerkt, gibt es eine Assertion: Sichtbarkeit, Text, Anzahl, Wert, Zustand, Attribute, Stil, zugänglicher Name, Titel und URL.'),
    say('text', 'Text checks', 'to have text wants the whole text, to contain text wants a part. With a list, to have text checks every element in order, which is ideal for sorting.',
        'to have text पूरा text चाहता है, to contain text एक हिस्सा। List के साथ to have text हर element को क्रम में जाँचता है, जो sorting के लिए सबसे अच्छा है।',
        'to have text ಸಂಪೂರ್ಣ text ಬಯಸುತ್ತದೆ, to contain text ಒಂದು ಭಾಗ. List ಜೊತೆ to have text ಪ್ರತಿ element ಅನ್ನು ಕ್ರಮದಲ್ಲಿ ಪರಿಶೀಲಿಸುತ್ತದೆ, sorting ಗೆ ಉತ್ತಮ.',
        'to have text ପୂରା text ଚାହେଁ, to contain text ଏକ ଅଂଶ। List ସହ to have text ପ୍ରତି element କୁ କ୍ରମରେ ଯାଞ୍ଚ କରେ, ଯାହା sorting ପାଇଁ ଉତ୍ତମ।',
        'يريد to have text النص كاملًا ويريد to contain text جزءًا منه. مع قائمة يفحص to have text كل عنصر بالترتيب، وهذا مثالي لاختبار الفرز.',
        'to have text verlangt den ganzen Text, to contain text einen Teil. Mit einer Liste prüft to have text jedes Element in Reihenfolge, ideal für Sortierungen.'),
    say('negative', 'Negative checks', 'Put not in front of any assertion. Negative checks retry too, so they wait for a spinner or a message to go away. Use a count of zero to check that nothing matches.',
        'किसी भी assertion के आगे not लगाएँ। Negative जाँचें भी दोबारा कोशिश करती हैं, इसलिए spinner या message के जाने का इंतज़ार करती हैं। कुछ भी match न हो, यह जाँचने के लिए count शून्य रखें।',
        'ಯಾವುದೇ assertion ಮುಂದೆ not ಸೇರಿಸಿ. Negative ಪರಿಶೀಲನೆಗಳೂ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸುತ್ತವೆ, ಆದ್ದರಿಂದ spinner ಅಥವಾ message ಹೋಗುವವರೆಗೆ ಕಾಯುತ್ತವೆ. ಏನೂ match ಆಗದಿರುವುದನ್ನು ಪರಿಶೀಲಿಸಲು count ಸೊನ್ನೆ ಬಳಸಿ.',
        'ଯେକୌଣସି assertion ଆଗରେ not ଲଗାନ୍ତୁ। Negative ଯାଞ୍ଚ ମଧ୍ୟ ପୁଣି ଚେଷ୍ଟା କରେ, ତେଣୁ spinner ବା message ଚାଲିଯିବା ପାଇଁ ଅପେକ୍ଷା କରେ। କିଛି match ନ ହେବା ଯାଞ୍ଚ ପାଇଁ count ଶୂନ ବ୍ୟବହାର କରନ୍ତୁ।',
        'ضع not أمام أي تأكيد. الفحوص السلبية تعيد المحاولة أيضًا، فتنتظر اختفاء مؤشر التحميل أو الرسالة. استخدم عددًا يساوي صفرًا للتحقق من عدم وجود أي تطابق.',
        'Setze not vor jede Assertion. Auch negative Prüfungen wiederholen und warten, bis ein Spinner oder eine Meldung verschwindet. Prüfe mit einer Anzahl von null, dass nichts passt.'),
    say('failing', 'Failures', 'A failing check prints the expected value, the real value, the timeout and the call log. In JavaScript and Python you can add a message that explains the intent.',
        'Fail होने वाली जाँच अपेक्षित value, असली value, timeout और call log दिखाती है। JavaScript और Python में आप उद्देश्य बताने वाला message जोड़ सकते हैं।',
        'Fail ಆಗುವ ಪರಿಶೀಲನೆ ನಿರೀಕ್ಷಿತ value, ನಿಜವಾದ value, timeout ಮತ್ತು call log ತೋರಿಸುತ್ತದೆ. JavaScript ಮತ್ತು Python ನಲ್ಲಿ ಉದ್ದೇಶ ವಿವರಿಸುವ message ಸೇರಿಸಬಹುದು.',
        'Fail ହେଉଥିବା ଯାଞ୍ଚ ଆଶା କରାଯାଇଥିବା value, ପ୍ରକୃତ value, timeout ଓ call log ଦେଖାଏ। JavaScript ଓ Python ରେ ଉଦ୍ଦେଶ୍ୟ ବୁଝାଉଥିବା message ଯୋଡିପାରିବେ।',
        'يطبع الفحص الفاشل القيمة المتوقعة والقيمة الفعلية والمهلة وسجل الاستدعاء. في JavaScript وPython يمكنك إضافة رسالة تشرح الغرض.',
        'Eine fehlschlagende Prüfung zeigt den erwarteten Wert, den echten Wert, das Timeout und das Call Log. In JavaScript und Python kannst du eine Nachricht hinzufügen, die die Absicht erklärt.'),
    say('soft', 'Soft assertions', 'A soft assertion records a failure and lets the test continue, so one run shows every problem. Python and JavaScript have expect soft. In Java, JUnit assert all does the same.',
        'Soft assertion failure दर्ज करता है और टेस्ट को चलने देता है, ताकि एक run में हर समस्या दिखे। Python और JavaScript में expect soft है। Java में JUnit का assert all यही करता है।',
        'Soft assertion failure ದಾಖಲಿಸಿ ಟೆಸ್ಟ್ ಮುಂದುವರಿಯಲು ಬಿಡುತ್ತದೆ, ಒಂದೇ run ನಲ್ಲಿ ಎಲ್ಲಾ ಸಮಸ್ಯೆಗಳು ಕಾಣುತ್ತವೆ. Python ಮತ್ತು JavaScript ನಲ್ಲಿ expect soft ಇದೆ. Java ದಲ್ಲಿ JUnit assert all ಅದೇ ಮಾಡುತ್ತದೆ.',
        'Soft assertion failure ଲେଖି ରଖେ ଏବଂ ଟେଷ୍ଟକୁ ଚାଲିବାକୁ ଦିଏ, ଯାହାଫଳରେ ଗୋଟିଏ run ରେ ସବୁ ସମସ୍ୟା ଦେଖାଯାଏ। Python ଓ JavaScript ରେ expect soft ଅଛି। Java ରେ JUnit assert all ସେହି କାମ କରେ।',
        'يسجل التأكيد المرن الفشل ويترك الاختبار يكمل، فيظهر كل خلل في تشغيل واحد. في Python وJavaScript يوجد expect soft، وفي Java يقوم JUnit assert all بالشيء نفسه.',
        'Eine Soft Assertion notiert den Fehler und lässt den Test weiterlaufen, sodass ein Lauf alle Probleme zeigt. Python und JavaScript haben expect soft, in Java macht JUnit assert all dasselbe.'),
    say('values', 'Plain values', 'For data you already hold, use the normal checks of your language, which do not wait. Playwright Test also has expect poll and to pass to retry your own code.',
        'जो data आपके पास पहले से है उसके लिए अपनी भाषा की सामान्य जाँचें इस्तेमाल करें, जो इंतज़ार नहीं करतीं। Playwright Test में अपने code को दोहराने के लिए expect poll और to pass भी हैं।',
        'ನಿಮ್ಮಲ್ಲಿ ಈಗಾಗಲೇ ಇರುವ data ಗೆ ನಿಮ್ಮ ಭಾಷೆಯ ಸಾಮಾನ್ಯ ಪರಿಶೀಲನೆಗಳನ್ನು ಬಳಸಿ, ಅವು ಕಾಯುವುದಿಲ್ಲ. Playwright Test ನಲ್ಲಿ ನಿಮ್ಮ code ಮರುಪ್ರಯತ್ನಿಸಲು expect poll ಮತ್ತು to pass ಇವೆ.',
        'ଆପଣଙ୍କ ପାଖରେ ଥିବା data ପାଇଁ ଆପଣଙ୍କ ଭାଷାର ସାଧାରଣ ଯାଞ୍ଚ ବ୍ୟବହାର କରନ୍ତୁ, ଯାହା ଅପେକ୍ଷା କରେ ନାହିଁ। Playwright Test ରେ ନିଜ code ପୁଣି ଚଳାଇବାକୁ expect poll ଓ to pass ଅଛି।',
        'للبيانات التي لديك مسبقًا استخدم الفحوص العادية في لغتك وهي لا تنتظر. ولدى Playwright Test أيضًا expect poll وto pass لإعادة تشغيل شيفرتك.',
        'Für Daten, die du schon hast, nutze die normalen Prüfungen deiner Sprache, die nicht warten. Playwright Test hat außerdem expect poll und to pass, um eigenen Code zu wiederholen.'),
    say('practice', 'Playground labs', 'In the labs you check the error after a wrong password, and you check the exact order of products after sorting by price.',
        'Labs में आप गलत password के बाद error जाँचते हैं, और price से sort करने के बाद products का सही क्रम जाँचते हैं।',
        'Labs ನಲ್ಲಿ ತಪ್ಪು password ನಂತರದ error ಪರಿಶೀಲಿಸುತ್ತೀರಿ, ಮತ್ತು price ಮೂಲಕ sort ಮಾಡಿದ ನಂತರ products ಕ್ರಮ ಪರಿಶೀಲಿಸುತ್ತೀರಿ.',
        'Labs ରେ ଭୁଲ password ପରେ error ଯାଞ୍ଚ କରନ୍ତି, ଏବଂ price ଅନୁସାରେ sort ପରେ products ର କ୍ରମ ଯାଞ୍ଚ କରନ୍ତି।',
        'في المختبرات تتحقق من الخطأ بعد كلمة مرور خاطئة، ومن الترتيب الدقيق للمنتجات بعد الفرز حسب السعر.',
        'In den Labs prüfst du die Fehlermeldung nach einem falschen Passwort und die genaue Reihenfolge der Produkte nach Sortierung nach Preis.'),
]

QUIZ = [
    quiz(1, 'How long does a Playwright assertion keep trying by default?', ['1 second', '5 seconds', '30 seconds', 'forever'], 1,
         'It is the expect timeout.', 'The default assertion timeout is 5 seconds.'),
    quiz(1, 'Which line waits for the banner to appear?', ['expect(await banner.isVisible()).toBe(true)', 'await expect(banner).toBeVisible()', 'banner.isVisible()', 'expect(banner.count()).toBe(1)'], 1,
         'Which one is web-first?', 'Only the assertion on the locator retries. The others read the page once.'),
    quiz(1, 'In Java, how do you check a locator has the text Products?', ['assertEquals("Products", x)', 'assertThat(x).hasText("Products")', 'x.hasText("Products")', 'expect(x).toHaveText("Products")'], 1,
         'Java uses assertThat.', 'Java assertions start with assertThat and use has or is.'),
    quiz(1, 'How do you check that no Add to cart button is left?', ['toBeVisible()', 'toHaveCount(0)', 'toHaveText(\'\')', 'toBeEmpty()'], 1,
         'Count them.', 'toHaveCount(0) passes when nothing matches, and it waits for that.'),
    quiz(2, 'toHaveText([\'a\', \'b\']) on a list of three elements. What happens?', ['passes', 'fails, it wants exactly these elements', 'checks only the first two', 'error'], 1,
         'With a list, toHaveText is strict.', 'toHaveText with a list wants exactly those elements in that order.'),
    quiz(2, 'A soft assertion fails. What happens to the test?', ['It stops at once', 'It keeps running and fails at the end', 'It passes', 'It is skipped'], 1,
         'Soft means keep going.', 'The failure is recorded, the test continues, and it is marked failed at the end.'),
    quiz(2, 'Java has no Playwright soft assertions. What gives the same effect?', ['try and catch everything', 'JUnit 5 assertAll', 'Thread.sleep', 'a second test'], 1,
         'Look at the Java soft example.', 'assertAll runs every check in the group and reports all failures together.'),
    quiz(2, 'Why does the colour check use rgb(22, 163, 74) and not #16a34a?', ['A typo', 'toHaveCSS compares the computed style, which the browser gives in rgb', 'Java needs it', 'It is a different colour'], 1,
         'Computed values.', 'The browser computes colours to rgb form, and toHaveCSS reads the computed value.'),
    quiz(2, 'Which is a plain, non-waiting check in Playwright Test?', ['await expect(locator).toHaveText(\'x\')', 'expect(products).toHaveLength(5)', 'await expect(page).toHaveURL(/x/)', 'await expect(response).toBeOK()'], 1,
         'It checks a value you already have.', 'Checks on plain values such as an array do not wait and need no await.'),
    quiz(3, 'Which of these exists only in Playwright Test for JavaScript and TypeScript?', ['toHaveText', 'expect.poll and toPass', 'toBeVisible', 'not'], 1,
         'Look at the poll example.', 'expect.poll, toPass and expect.configure are part of Playwright Test.'),
    quiz(3, 'How do you set the assertion timeout for all checks in Python?', ['expect.timeout = 10', 'expect.set_options(timeout=10_000)', 'pytest --timeout', 'page.set_default_timeout'], 1,
         'It goes in conftest.py.', 'expect.set_options(timeout=...) changes the default for every expect.'),
    quiz(3, 'toContainText([\'mug\', \'pen\']) on Coffee mug, Desk lamp, Gel pen. What happens?', ['fails, lamp is in between', 'passes, a subset in this order contains them', 'fails, mug is not the full text', 'error'], 1,
         'Contain with a list allows gaps.', 'It looks for some elements, in order, each containing one of the parts.'),
]

CALC = [
    calc(1, 'The offer appears 1200 ms after the click. With the default 5000 ms timeout, how many ms of the timeout are left?', 3800, '5000 - 1200', ['5000 - 1200 = 3800 ms']),
    calc(1, 'The page shows 5 products and you search for phone. How many listitems are there with the empty message?', 1,
         'The message is also a list item', ['No product matches', 'the list shows one item: the message', '1']),
    calc(2, 'Sorted from low to high: Gel pen ₹20, Notebook ₹60, Coffee mug ₹199, Water bottle ₹349, Desk lamp ₹1299. What is the price of the middle one?', 199,
         'The third of five', ['The middle of 5 is the 3rd', 'Coffee mug: 199']),
    calc(2, 'A soft check suite has 20 fields and 3 are wrong. How many failures does one run report?', 3, 'All of them', ['Soft checks keep going', 'All 3 are reported']),
    calc(2, 'With normal checks, the same 20 fields with 3 wrong need how many runs to find all 3, if you fix one per run?', 3, 'A normal check stops at the first failure', ['Run 1 finds the 1st', 'Run 2 finds the 2nd', 'Run 3 finds the 3rd']),
    calc(3, 'Two soft checks each wait 1000 ms before failing, and the rest of the test takes 500 ms. About how many ms does the test take?', 2500,
         '1000 + 1000 + 500', ['2 × 1000 = 2000 ms', '2000 + 500 = 2500 ms']),
    calc(3, 'toPass retries with intervals 100, 200 and 500 ms and passes on the third try. How many ms were spent waiting between tries?', 300,
         'Two waits before the third try', ['wait 100 ms before try 2', 'wait 200 ms before try 3', '100 + 200 = 300 ms']),
    calc(3, 'The sum of all product prices is 20 + 199 + 1299 + 60 + 349. What is it?', 1927, 'Add them', ['20 + 199 = 219', '219 + 1299 = 1518', '1518 + 60 = 1578', '1578 + 349 = 1927']),
]

LABS = [
    {'id': 'wrongpw', 'title': 'Check the error for a wrong password', 'name': 'a wrong password shows an error',
     'task': 'On <code>/login</code>, sign in as <code>asha@shop.example</code> with the password <code>nope</code>. Check that the alert says <b>Wrong email or password</b> and that the page is still on <code>/login</code>.',
     'goal': 'The error is shown and the user stays on the sign in page.', 'start': '/login',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('a wrong password shows an error', async ({ page }) => {
  await page.goto('/login');
  // fill the form with a wrong password, click Sign in, then check the alert and the URL
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('a wrong password shows an error', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('nope');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('alert')).toHaveText('Wrong email or password');
  await expect(page).toHaveURL(/\\/login$/);
});'''},
     'hint': "The error line has the role alert: <code>expect(page.getByRole('alert')).toHaveText(...)</code>. For the address: <code>expect(page).toHaveURL(/\\/login$/)</code>.",
     'why': 'The alert is hidden until the server answers, so the check has to wait, and a web-first assertion does. The URL check proves the shop did not let the user in.',
     'check': [["/Wrong email or password/.test(ctx.text)", 'The error is on the page'], ["/toHaveURL|to_have_url|hasURL|HaveURL/.test(ctx.code)", 'The test checks the address']]},
    {'id': 'sorthigh', 'title': 'Check the order after sorting', 'name': 'sort by price, highest first',
     'task': 'On <code>/products</code>, choose <b>Price: high to low</b> in the Sort by list. Check with one assertion that the product names are, in order: Desk lamp, Water bottle, Coffee mug, Notebook, Gel pen.',
     'goal': 'One list check proves the sort order.', 'start': '/products',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('sort by price, highest first', async ({ page }) => {
  await page.goto('/products');
  // choose the sort, then check all names in one toHaveText with a list
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('sort by price, highest first', async ({ page }) => {
  await page.goto('/products');
  await page.getByLabel('Sort by').selectOption('high');
  await expect(page.getByRole('listitem').getByRole('heading'))
    .toHaveText(['Desk lamp', 'Water bottle', 'Coffee mug', 'Notebook', 'Gel pen']);
});'''},
     'hint': "Select the option with value <code>high</code>, then pass a list to <code>toHaveText</code> on <code>page.getByRole('listitem').getByRole('heading')</code>.",
     'why': 'toHaveText with a list checks every element and the order, so a wrong sort fails even when the right products are on the page.',
     'check': [["/Desk lamp[\\s\\S]*Water bottle[\\s\\S]*Coffee mug[\\s\\S]*Notebook[\\s\\S]*Gel pen/.test(ctx.code)", 'The test checks all five names in order'], ["/high/.test(ctx.code)", 'The test sorts by price, highest first']]},
]

T = {
    'slug': 'pw-assertions', 'title': 'Assertions that wait for the page', 'short': 'Assertions', 'emoji': '✅', 'module': MODULE, 'minutes': 22,
    'lead': 'Check what a user can see with assertions that retry until the page is right. Learn the everyday checks, text and list checks, negative checks, how to read a failure, soft assertions, and plain checks for data.',
    'desc': 'Web-first assertions, toBeVisible, toHaveText, toContainText, toHaveCount, toHaveValue, toHaveAttribute, toHaveCSS, toHaveURL, not, custom messages, timeouts, expect.soft and JUnit assertAll, expect.poll and toPass in Java, Python, JavaScript and TypeScript.',
    'summary': 'How a web-first assertion retries, a plain read against a retrying check, fifteen checks on one page, text and list checks for sorting, negative checks, a real failure report, soft assertions in all four languages, plain value checks on API data, expect.poll and toPass, and a recorded walk through a search.',
    'keywords': ['assertion', 'expect', 'assertThat', 'web-first', 'toHaveText', 'toContainText', 'toBeVisible', 'toHaveCount', 'not', 'soft assertion', 'assertAll', 'expect.poll', 'toPass', 'timeout'],
    'plain': 'An assertion is the part of a test that says what should be true. Playwright assertions look again and again for a few seconds, so a slow page does not make a correct test fail.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
