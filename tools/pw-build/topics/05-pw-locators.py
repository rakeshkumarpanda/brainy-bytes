from pkit import part, say, quiz, calc, panel, four, one, js, ts, py, jv, shown, walk, step, table, tip, by, viz, figure

MODULE = ('🎯', 'Finding and using elements', 'pw-elements', 'Locators, actions with auto-waiting, and assertions that retry by themselves.')

# ---------- getByRole ----------
ROLE_TS = '''import { test, expect } from '@playwright/test';

test('find things the way a user sees them', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByRole('listitem')).toHaveCount(5);   // waits for the list

  console.log('headings:', await page.getByRole('heading').allTextContents());
  console.log('level 1 heading:', await page.getByRole('heading', { level: 1 }).textContent());

  // The name is matched ignoring case, and part of the name is enough.
  console.log('"add to cart":', await page.getByRole('button', { name: 'add to cart' }).count());
  // exact: true wants the whole name with the same case.
  console.log('"add to cart" exact:', await page.getByRole('button', { name: 'add to cart', exact: true }).count());
  console.log('disabled buttons:', await page.getByRole('button', { disabled: true }).count());

  await page.getByRole('searchbox', { name: 'Search' }).fill('lamp');
  await page.getByRole('combobox', { name: 'Sort by' }).selectOption('high');
  await expect(page.getByRole('listitem')).toHaveCount(1);
  console.log('left after search:', await page.getByRole('listitem').getByRole('heading').textContent());
});'''

ROLE_PY = '''from playwright.sync_api import Page, expect


def test_find_things_the_way_a_user_sees_them(page: Page):
    page.goto("/products")
    expect(page.get_by_role("listitem")).to_have_count(5)   # waits for the list

    print("headings:", page.get_by_role("heading").all_text_contents())
    print("level 1 heading:", page.get_by_role("heading", level=1).text_content())

    # The name is matched ignoring case, and part of the name is enough.
    print('"add to cart":', page.get_by_role("button", name="add to cart").count())
    # exact=True wants the whole name with the same case.
    print('"add to cart" exact:', page.get_by_role("button", name="add to cart", exact=True).count())
    print("disabled buttons:", page.get_by_role("button", disabled=True).count())

    page.get_by_role("searchbox", name="Search").fill("lamp")
    page.get_by_role("combobox", name="Sort by").select_option("high")
    expect(page.get_by_role("listitem")).to_have_count(1)
    print("left after search:", page.get_by_role("listitem").get_by_role("heading").text_content())'''

ROLE_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class RoleTest {
  @Test
  void findThingsTheWayAUserSeesThem(Page page) {
    page.navigate("/products");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(5);   // waits for the list

    System.out.println("headings: " + page.getByRole(AriaRole.HEADING).allTextContents());
    System.out.println("level 1 heading: " + page.getByRole(AriaRole.HEADING, new Page.GetByRoleOptions().setLevel(1)).textContent());

    // The name is matched ignoring case, and part of the name is enough.
    System.out.println("\\"add to cart\\": " + page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("add to cart")).count());
    // setExact(true) wants the whole name with the same case.
    System.out.println("\\"add to cart\\" exact: " + page.getByRole(AriaRole.BUTTON,
        new Page.GetByRoleOptions().setName("add to cart").setExact(true)).count());
    System.out.println("disabled buttons: " + page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setDisabled(true)).count());

    page.getByRole(AriaRole.SEARCHBOX, new Page.GetByRoleOptions().setName("Search")).fill("lamp");
    page.getByRole(AriaRole.COMBOBOX, new Page.GetByRoleOptions().setName("Sort by")).selectOption("high");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(1);
    System.out.println("left after search: " + page.getByRole(AriaRole.LISTITEM).getByRole(AriaRole.HEADING).textContent());
  }
}'''

# ---------- the other getBy methods ----------
GETBY_TS = '''import { test, expect } from '@playwright/test';

test('labels, placeholders, text, titles and test ids', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('s3cret');
  await page.getByText('Remember me').click();          // clicking a label ticks its box
  await expect(page.getByLabel('Remember me')).toBeChecked();
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page.getByText('Hello, Asha')).toBeVisible();
  await expect(page.getByTestId('cart-count')).toHaveText('0');
  await expect(page.getByPlaceholder('Search products')).toBeEditable();
  await expect(page.getByTestId(/^product-/)).toHaveCount(5);   // all product cards

  await page.goto('/frames');
  console.log('iframes by title:', await page.getByTitle('Payment form').count());
});'''

GETBY_PY = '''import re
from playwright.sync_api import Page, expect


def test_labels_placeholders_text_titles_and_test_ids(page: Page):
    page.goto("/login")
    page.get_by_label("Email").fill("asha@shop.example")
    page.get_by_label("Password").fill("s3cret")
    page.get_by_text("Remember me").click()          # clicking a label ticks its box
    expect(page.get_by_label("Remember me")).to_be_checked()
    page.get_by_role("button", name="Sign in").click()

    expect(page.get_by_text("Hello, Asha")).to_be_visible()
    expect(page.get_by_test_id("cart-count")).to_have_text("0")
    expect(page.get_by_placeholder("Search products")).to_be_editable()
    expect(page.get_by_test_id(re.compile(r"^product-"))).to_have_count(5)   # all product cards

    page.goto("/frames")
    print("iframes by title:", page.get_by_title("Payment form").count())'''

GETBY_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;
import java.util.regex.Pattern;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class GetByTest {
  @Test
  void labelsPlaceholdersTextTitlesAndTestIds(Page page) {
    page.navigate("/login");
    page.getByLabel("Email").fill("asha@shop.example");
    page.getByLabel("Password").fill("s3cret");
    page.getByText("Remember me").click();          // clicking a label ticks its box
    assertThat(page.getByLabel("Remember me")).isChecked();
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in")).click();

    assertThat(page.getByText("Hello, Asha")).isVisible();
    assertThat(page.getByTestId("cart-count")).hasText("0");
    assertThat(page.getByPlaceholder("Search products")).isEditable();
    assertThat(page.getByTestId(Pattern.compile("^product-"))).hasCount(5);   // all product cards

    page.navigate("/frames");
    System.out.println("iframes by title: " + page.getByTitle("Payment form").count());
  }
}'''

# ---------- CSS and XPath ----------
CSS_TS = '''import { test, expect } from '@playwright/test';

test('CSS and XPath when nothing better fits', async ({ page }) => {
  await page.goto('/products');
  await expect(page.locator('li.card')).toHaveCount(5);

  console.log('CSS prices:', await page.locator('li.card .price').allTextContents());
  console.log('CSS attribute:', await page.locator('[data-testid="product-3"] h3').textContent());
  console.log('CSS :has-text():', await page.locator('li.card:has-text("mug") h3').textContent());
  console.log('XPath:', await page.locator('//li[h3="Desk lamp"]//span[@class="price"]').textContent());
  console.log('id:', await page.locator('#sort').inputValue());
});'''

CSS_PY = '''from playwright.sync_api import Page, expect


def test_css_and_xpath_when_nothing_better_fits(page: Page):
    page.goto("/products")
    expect(page.locator("li.card")).to_have_count(5)

    print("CSS prices:", page.locator("li.card .price").all_text_contents())
    print("CSS attribute:", page.locator('[data-testid="product-3"] h3').text_content())
    print("CSS :has-text():", page.locator('li.card:has-text("mug") h3').text_content())
    print("XPath:", page.locator('//li[h3="Desk lamp"]//span[@class="price"]').text_content())
    print("id:", page.locator("#sort").input_value())'''

CSS_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class CssTest {
  @Test
  void cssAndXpathWhenNothingBetterFits(Page page) {
    page.navigate("/products");
    assertThat(page.locator("li.card")).hasCount(5);

    System.out.println("CSS prices: " + page.locator("li.card .price").allTextContents());
    System.out.println("CSS attribute: " + page.locator("[data-testid=\\"product-3\\"] h3").textContent());
    System.out.println("CSS :has-text(): " + page.locator("li.card:has-text(\\"mug\\") h3").textContent());
    System.out.println("XPath: " + page.locator("//li[h3=\\"Desk lamp\\"]//span[@class=\\"price\\"]").textContent());
    System.out.println("id: " + page.locator("#sort").inputValue());
  }
}'''

# ---------- filter, chain, and, or ----------
FILTER_TS = '''import { test, expect } from '@playwright/test';

test('narrow down with filter, chaining, and and or', async ({ page }) => {
  await page.goto('/products');
  const cards = page.getByRole('listitem');
  await expect(cards).toHaveCount(5);

  const mug = cards.filter({ hasText: 'Coffee mug' });
  console.log('mug price:', await mug.locator('.price').textContent());

  const kitchen = cards.filter({ hasText: 'Kitchen' });
  console.log('kitchen:', await kitchen.getByRole('heading').allTextContents());

  const soldOut = cards.filter({ has: page.getByRole('button', { name: 'Out of stock' }) });
  console.log('sold out:', await soldOut.getByRole('heading').textContent());

  const inStock = cards.filter({ hasNot: page.getByRole('button', { disabled: true }) });
  console.log('in stock:', await inStock.count());

  console.log('first:', await cards.first().getByRole('heading').textContent());
  console.log('nth(2):', await cards.nth(2).getByRole('heading').textContent());
  console.log('last:', await cards.last().getByRole('heading').textContent());

  const anyButton = page.getByRole('button', { name: 'Add to cart' }).or(page.getByRole('button', { name: 'Out of stock' }));
  console.log('or:', await anyButton.count());
  const disabledButton = page.getByRole('button').and(page.locator('[disabled]'));
  console.log('and:', await disabledButton.textContent());
});'''

FILTER_PY = '''from playwright.sync_api import Page, expect


def test_narrow_down_with_filter_chaining_and_and_or(page: Page):
    page.goto("/products")
    cards = page.get_by_role("listitem")
    expect(cards).to_have_count(5)

    mug = cards.filter(has_text="Coffee mug")
    print("mug price:", mug.locator(".price").text_content())

    kitchen = cards.filter(has_text="Kitchen")
    print("kitchen:", kitchen.get_by_role("heading").all_text_contents())

    sold_out = cards.filter(has=page.get_by_role("button", name="Out of stock"))
    print("sold out:", sold_out.get_by_role("heading").text_content())

    in_stock = cards.filter(has_not=page.get_by_role("button", disabled=True))
    print("in stock:", in_stock.count())

    print("first:", cards.first.get_by_role("heading").text_content())
    print("nth(2):", cards.nth(2).get_by_role("heading").text_content())
    print("last:", cards.last.get_by_role("heading").text_content())

    any_button = page.get_by_role("button", name="Add to cart").or_(page.get_by_role("button", name="Out of stock"))
    print("or:", any_button.count())
    disabled_button = page.get_by_role("button").and_(page.locator("[disabled]"))
    print("and:", disabled_button.text_content())'''

FILTER_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class FilterTest {
  @Test
  void narrowDownWithFilterChainingAndAndOr(Page page) {
    page.navigate("/products");
    Locator cards = page.getByRole(AriaRole.LISTITEM);
    assertThat(cards).hasCount(5);

    Locator mug = cards.filter(new Locator.FilterOptions().setHasText("Coffee mug"));
    System.out.println("mug price: " + mug.locator(".price").textContent());

    Locator kitchen = cards.filter(new Locator.FilterOptions().setHasText("Kitchen"));
    System.out.println("kitchen: " + kitchen.getByRole(AriaRole.HEADING).allTextContents());

    Locator soldOut = cards.filter(new Locator.FilterOptions()
        .setHas(page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Out of stock"))));
    System.out.println("sold out: " + soldOut.getByRole(AriaRole.HEADING).textContent());

    Locator inStock = cards.filter(new Locator.FilterOptions()
        .setHasNot(page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setDisabled(true))));
    System.out.println("in stock: " + inStock.count());

    System.out.println("first: " + cards.first().getByRole(AriaRole.HEADING).textContent());
    System.out.println("nth(2): " + cards.nth(2).getByRole(AriaRole.HEADING).textContent());
    System.out.println("last: " + cards.last().getByRole(AriaRole.HEADING).textContent());

    Locator anyButton = page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Add to cart"))
        .or(page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Out of stock")));
    System.out.println("or: " + anyButton.count());
    Locator disabledButton = page.getByRole(AriaRole.BUTTON).and(page.locator("[disabled]"));
    System.out.println("and: " + disabledButton.textContent());
  }
}'''

# ---------- strictness ----------
STRICT_TS = '''import { test, expect } from '@playwright/test';

test('strict mode refuses to guess', async ({ page }) => {
  await page.goto('/products');
  const add = page.getByRole('button', { name: 'Add to cart' });
  await expect(add).toHaveCount(4);              // counting many is fine

  const error = await add.click().catch(e => e);  // acting on many is not
  console.log(error.message.split('\\n').slice(0, 4).join('\\n'));
});'''

STRICT_JS = STRICT_TS

STRICT_PY = '''import pytest
from playwright.sync_api import Page, Error, expect


def test_strict_mode_refuses_to_guess(page: Page):
    page.goto("/products")
    add = page.get_by_role("button", name="Add to cart")
    expect(add).to_have_count(4)              # counting many is fine

    with pytest.raises(Error) as info:        # acting on many is not
        add.click()
    print("\\n".join(info.value.message.split("\\n")[:4]))'''

STRICT_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.PlaywrightException;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;

@UsePlaywright(ShopOptions.class)
public class StrictTest {
  @Test
  void strictModeRefusesToGuess(Page page) {
    page.navigate("/products");
    Locator add = page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Add to cart"));
    assertThat(add).hasCount(4);              // counting many is fine

    PlaywrightException error = assertThrows(PlaywrightException.class, () -> add.click());   // acting on many is not
    System.out.println(String.join("\\n", java.util.Arrays.asList(error.getMessage().split("\\n")).subList(0, 5)));
  }
}'''

# ---------- lists and tables ----------
TABLE_TS = '''import { test, expect } from '@playwright/test';

test('read a table and act on one row', async ({ page }) => {
  await page.goto('/orders');
  const rows = page.getByRole('row').filter({ has: page.getByRole('cell') });   // skip the header row
  await expect(rows).toHaveCount(5);

  for (const row of await rows.all()) {
    console.log(await row.getByRole('cell').allTextContents());
  }

  const meera = rows.filter({ hasText: 'Meera' });
  await meera.getByRole('button', { name: 'Delete' }).click();
  await expect(page.getByRole('status')).toHaveText('Order #1003 deleted');
  await expect(rows.filter({ hasText: 'Meera' })).toHaveCount(0);
});'''

TABLE_PY = '''from playwright.sync_api import Page, expect


def test_read_a_table_and_act_on_one_row(page: Page):
    page.goto("/orders")
    rows = page.get_by_role("row").filter(has=page.get_by_role("cell"))   # skip the header row
    expect(rows).to_have_count(5)

    for row in rows.all():
        print(row.get_by_role("cell").all_text_contents())

    meera = rows.filter(has_text="Meera")
    meera.get_by_role("button", name="Delete").click()
    expect(page.get_by_role("status")).to_have_text("Order #1003 deleted")
    expect(rows.filter(has_text="Meera")).to_have_count(0)'''

TABLE_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class TableTest {
  @Test
  void readATableAndActOnOneRow(Page page) {
    page.navigate("/orders");
    Locator rows = page.getByRole(AriaRole.ROW)
        .filter(new Locator.FilterOptions().setHas(page.getByRole(AriaRole.CELL)));   // skip the header row
    assertThat(rows).hasCount(5);

    for (Locator row : rows.all()) {
      System.out.println(row.getByRole(AriaRole.CELL).allTextContents());
    }

    Locator meera = rows.filter(new Locator.FilterOptions().setHasText("Meera"));
    meera.getByRole(AriaRole.BUTTON, new Locator.GetByRoleOptions().setName("Delete")).click();
    assertThat(page.getByRole(AriaRole.STATUS)).hasText("Order #1003 deleted");
    assertThat(rows.filter(new Locator.FilterOptions().setHasText("Meera"))).hasCount(0);
  }
}'''

# ---------- a locator is lazy ----------
LAZY_TS = '''import { test, expect } from '@playwright/test';

test('a locator is a recipe, not an element', async ({ page }) => {
  await page.goto('/products');
  const cards = page.getByRole('listitem');          // nothing is searched yet
  await expect(cards).toHaveCount(5);
  console.log('before search:', await cards.count());

  await page.getByPlaceholder('Search products').fill('o');
  console.log('after "o":', await cards.count());    // the same locator, found again

  await page.getByPlaceholder('Search products').fill('bottle');
  await expect(cards).toHaveCount(1);
  console.log('after "bottle":', await cards.count());
  console.log(cards.describe('product cards').toString());
});'''

LAZY_PY = '''from playwright.sync_api import Page, expect


def test_a_locator_is_a_recipe_not_an_element(page: Page):
    page.goto("/products")
    cards = page.get_by_role("listitem")          # nothing is searched yet
    expect(cards).to_have_count(5)
    print("before search:", cards.count())

    page.get_by_placeholder("Search products").fill("o")
    print('after "o":', cards.count())            # the same locator, found again

    page.get_by_placeholder("Search products").fill("bottle")
    expect(cards).to_have_count(1)
    print('after "bottle":', cards.count())
    print(cards.describe("product cards"))'''

LAZY_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class LazyTest {
  @Test
  void aLocatorIsARecipeNotAnElement(Page page) {
    page.navigate("/products");
    Locator cards = page.getByRole(AriaRole.LISTITEM);          // nothing is searched yet
    assertThat(cards).hasCount(5);
    System.out.println("before search: " + cards.count());

    page.getByPlaceholder("Search products").fill("o");
    System.out.println("after \\"o\\": " + cards.count());       // the same locator, found again

    page.getByPlaceholder("Search products").fill("bottle");
    assertThat(cards).hasCount(1);
    System.out.println("after \\"bottle\\": " + cards.count());
    System.out.println(cards.describe("product cards"));
  }
}'''

ROW = "page.getByRole('row').filter({ hasText: 'John' })"

CODES = {
    'lazy': four('A locator is found again every time you use it',
                 java=jv({'LazyTest.java': LAZY_JAVA}),
                 py=py({'test_lazy.py': LAZY_PY}, cmd='pytest -v -s'),
                 js=js({'lazy.spec.js': LAZY_TS}),
                 ts=ts({'lazy.spec.ts': LAZY_TS}),
                 result='One locator gave three different counts, because it searches the page again at the moment it is used. A search for the letter o keeps the three products whose names contain it. <code>describe</code> gives the locator a readable name that shows up in reports and in the trace viewer. Python prints the whole locator, with the name inside the selector.'),
    'role': four('getByRole with names, levels and states',
                 java=jv({'RoleTest.java': ROLE_JAVA}),
                 py=py({'test_roles.py': ROLE_PY}, cmd='pytest -v -s'),
                 js=js({'roles.spec.js': ROLE_TS}),
                 ts=ts({'roles.spec.ts': ROLE_TS}),
                 result='The list is sorted by name, so Coffee mug comes first. A search box has the role searchbox, a drop down list has the role combobox, and a heading knows its level. By default the name matches ignoring case and part of it is enough, so <b>add to cart</b> finds all four buttons. With exact it finds none, because the real name starts with a capital A.'),
    'getby': four('Labels, placeholders, text, titles and test ids',
                  java=jv({'GetByTest.java': GETBY_JAVA}),
                  py=py({'test_getby.py': GETBY_PY}, cmd='pytest -v -s'),
                  js=js({'getby.spec.js': GETBY_TS}),
                  ts=ts({'getby.spec.ts': GETBY_TS}),
                  result='The form boxes are found by the words of their labels. Clicking the text <b>Remember me</b> clicks its label, and the browser ticks the box, just as it would for a person. The cart counter has a <code>data-testid</code>, and a regular expression finds all five product cards by theirs.'),
    'css': four('CSS and XPath',
                java=jv({'CssTest.java': CSS_JAVA}),
                py=py({'test_css.py': CSS_PY}, cmd='pytest -v -s'),
                js=js({'css.spec.js': CSS_TS}),
                ts=ts({'css.spec.ts': CSS_TS}),
                result='Playwright decides by the first characters: a string that starts with <code>//</code> or <code>..</code> is XPath, everything else is CSS. CSS also gets extras such as <code>:has-text()</code>. These locators work, but they break when a developer renames a class or moves a tag, which a user never notices.'),
    'filter': four('filter, first, nth, last, and, or',
                   java=jv({'FilterTest.java': FILTER_JAVA}),
                   py=py({'test_filter.py': FILTER_PY}, cmd='pytest -v -s'),
                   js=js({'filter.spec.js': FILTER_TS}),
                   ts=ts({'filter.spec.ts': FILTER_TS}),
                   result='<code>filter</code> keeps the cards that contain some text, or that contain (or do not contain) another locator. Chaining, such as <code>soldOut.getByRole(\'heading\')</code>, searches only inside the cards that are left. <code>nth</code> counts from 0, so <code>nth(2)</code> is the third card. <code>or</code> matches either locator, and <code>and</code> keeps only elements both locators match.'),
    'strict': four('Strict mode: one action, one element',
                   java=jv({'StrictTest.java': STRICT_JAVA}),
                   py=py({'test_strict.py': STRICT_PY}, cmd='pytest -v -s'),
                   js=js({'strict.spec.js': STRICT_JS}),
                   ts=ts({'strict.spec.ts': STRICT_TS}),
                   result='The click failed at once instead of picking a button at random. The message lists the elements it found, and for each one it suggests a locator that finds only that one, written in your language. Counting and checking a count are fine with many elements, actions are not.'),
    'table': four('Read every row of a table, then act on one row',
                  java=jv({'TableTest.java': TABLE_JAVA}),
                  py=py({'test_table.py': TABLE_PY}, cmd='pytest -v -s'),
                  js=js({'table.spec.js': TABLE_TS}),
                  ts=ts({'table.spec.ts': TABLE_TS}),
                  result='Table cells have the role <code>cell</code> and header cells have the role <code>columnheader</code>, so filtering rows that have a cell skips the header. <code>all()</code> turns the locator into a list you can loop over. It does not wait, so the count check comes first. The Delete button of Meera\'s row is found inside that row only.'),
    'walkloc': walk('Working on one row of the orders table', [
        step('Open the orders page. It shows 5 of 7 orders per page.', "await page.goto('http://localhost:4173/orders');", 'page.goto("http://localhost:4173/orders")', 'page.navigate("http://localhost:4173/orders");'),
        step('Click the Total column header to sort by total, smallest first.', "await page.getByRole('button', { name: 'Total' }).click();",
             'page.get_by_role("button", name="Total").click()', 'page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Total")).click();'),
        step('Find the row that mentions John, then the Delete button inside that row only.', f"await {ROW}.getByRole('button', {{ name: 'Delete' }}).click();",
             'page.get_by_role("row").filter(has_text="John").get_by_role("button", name="Delete").click()',
             'page.getByRole(AriaRole.ROW).filter(new Locator.FilterOptions().setHasText("John"))\n    .getByRole(AriaRole.BUTTON, new Locator.GetByRoleOptions().setName("Delete")).click();'),
        step('The status message confirms which order went away.', "await expect(page.getByRole('status')).toHaveText('Order #1004 deleted');",
             'expect(page.get_by_role("status")).to_have_text("Order #1004 deleted")', 'assertThat(page.getByRole(AriaRole.STATUS)).hasText("Order #1004 deleted");'),
        step('Go to the next page of the table.', "await page.getByRole('button', { name: 'Next' }).click();",
             'page.get_by_role("button", name="Next").click()', 'page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Next")).click();'),
        step('Check the page counter by its text.', "await expect(page.getByText('Page 2 of 2')).toBeVisible();",
             'expect(page.get_by_text("Page 2 of 2")).to_be_visible()', 'assertThat(page.getByText("Page 2 of 2")).isVisible();'),
    ], size=(900, 560)),
}

DG = {
    'prio': {'t': 'Which locator to try first', 'w': 900, 'h': 210,
             'n': [['role', 20, 70, 140, 64, 'getByRole', {'c': 1, 'sub': 'first choice', 'i': 'Buttons, links, headings, boxes, rows. What a user and a screen reader see.'}],
                   ['label', 180, 70, 130, 64, 'getByLabel', {'c': 1, 'sub': 'form boxes', 'i': 'A form box found by the words of its label.'}],
                   ['ph', 330, 70, 150, 64, 'getByPlaceholder', {'c': 2, 'sub': 'no label', 'i': 'For a box that only has hint text inside.'}],
                   ['text', 500, 70, 120, 64, 'getByText', {'c': 2, 'sub': 'plain text', 'i': 'For text that is not a button or link, such as a message.'}],
                   ['tid', 640, 70, 120, 64, 'getByTestId', {'c': 3, 'sub': 'agreed id', 'i': 'A data-testid the developers promise to keep.'}],
                   ['css', 780, 70, 100, 64, 'CSS, XPath', {'c': 0, 'sub': 'last resort', 'i': 'Tied to how the page is built, so it breaks when the code changes.'}]],
             'e': [['role', 'label'], ['label', 'ph'], ['ph', 'text'], ['text', 'tid'], ['tid', 'css']],
             'st': [[['role'], 'Start with the role and the visible name. It is how people find things, so it rarely breaks and it checks accessibility for free.'],
                    [['label', 'role>label'], 'Form boxes are best found by their label, the words a user reads next to the box.'],
                    [['ph', 'text', 'label>ph', 'ph>text'], 'Placeholder and text cover boxes without labels and plain messages.'],
                    [['tid', 'text>tid'], 'When the visible text changes often, for example in many languages, agree on a test id with the developers.'],
                    [['css', 'tid>css'], 'CSS and XPath are the last resort, because they depend on how the page is built.']]},
}

PARTS = [
    part('what', '🎯', 'What a locator is', f'''
<p>A locator is a way to find an element on the page, written as a short description such as <i>the button called Sign in</i>. It does not hold the element. Every time you use it, Playwright searches the page again, at that moment. This is why a locator never goes stale when the page changes, which was a common problem in older tools.</p>
[[lazy]]
<p>Playwright gives you locators that describe what a person sees: a role and a name, a label, a placeholder, some text. Try them in the locator lab. Type your own in any of the four languages.</p>
{viz('pwloc')}
<div class="viz" data-viz="flow" data-k="prio"></div>
{tip('A real life example: you tell a friend <i>press the green Pay button</i>, not <i>press the third button in the second box</i>. The first instruction still works when the page is redesigned. Good locators work the same way.', 'life')}
''', easy=True, kw=['locator', 'lazy', 'stale element', 'describe', 'priority']),

    part('role', '🧑‍🦯', 'getByRole: the first choice', f'''
<p>Every element has a role that tells assistive technology what it is: <code>button</code>, <code>link</code>, <code>heading</code>, <code>textbox</code>, <code>checkbox</code>, <code>row</code> and many more. Most of them come from the HTML tag itself, so developers get them for free. The name is what a person reads: the button text, the label of a box, or an <code>aria-label</code>.</p>
[[role]]
{table(['HTML', 'Role', 'Example locator'], [
    ['&lt;button&gt;, &lt;input type=submit&gt;', 'button', "getByRole('button', { name: 'Sign in' })"],
    ['&lt;a href&gt;', 'link', "getByRole('link', { name: 'Orders' })"],
    ['&lt;h1&gt; to &lt;h6&gt;', 'heading', "getByRole('heading', { level: 1 })"],
    ['&lt;input type=text&gt;, &lt;textarea&gt;', 'textbox', "getByRole('textbox', { name: 'Email' })"],
    ['&lt;input type=search&gt;', 'searchbox', "getByRole('searchbox')"],
    ['&lt;select&gt;', 'combobox', "getByRole('combobox', { name: 'Sort by' })"],
    ['&lt;input type=checkbox&gt; and radio', 'checkbox, radio', "getByRole('checkbox', { checked: true })"],
    ['&lt;li&gt;, &lt;tr&gt;, &lt;td&gt;', 'listitem, row, cell', "getByRole('row').filter(...)"],
])}
<p>Options narrow it further: {by(java='<code>setName</code>, <code>setExact</code>, <code>setLevel</code>, <code>setChecked</code>, <code>setDisabled</code>, <code>setExpanded</code>, <code>setPressed</code>, <code>setSelected</code> and <code>setIncludeHidden</code> on <code>GetByRoleOptions</code>', py='<code>name</code>, <code>exact</code>, <code>level</code>, <code>checked</code>, <code>disabled</code>, <code>expanded</code>, <code>pressed</code>, <code>selected</code> and <code>include_hidden</code>', js='<code>name</code>, <code>exact</code>, <code>level</code>, <code>checked</code>, <code>disabled</code>, <code>expanded</code>, <code>pressed</code>, <code>selected</code> and <code>includeHidden</code>')}. The name can also be a regular expression.</p>
{tip('If getByRole cannot find a button that you can see, the page is probably missing a role or a name, and a screen reader user cannot use it either. That is a real accessibility bug worth reporting.', 'pro')}
''', easy=True, kw=['getByRole', 'role', 'name', 'exact', 'aria', 'accessibility', 'AriaRole']),

    part('getby', '🏷️', 'Labels, placeholders, text, alt text, titles and test ids', f'''
<p>The other built in locators cover the cases where a role is not enough.</p>
{table(['Locator', 'Finds', 'Good for'], [
    ['getByLabel', 'a form box by its &lt;label&gt; or aria-label', 'every form'],
    ['getByPlaceholder', 'a box by its hint text', 'boxes with no label'],
    ['getByText', 'the smallest element that contains the text', 'messages, paragraphs, labels'],
    ['getByAltText', 'an image by its alt text', 'logos, product pictures'],
    ['getByTitle', 'an element by its title attribute', 'icons, iframes'],
    ['getByTestId', 'an element by data-testid', 'text that changes or is translated'],
])}
[[getby]]
<p>Text matching works like names: ignoring case, part of the text is enough, and runs of spaces count as one. Use exact for a full, case sensitive match, or a regular expression.</p>
{tip('Many companies use another attribute for test ids, such as data-qa or data-test. Tell Playwright once: ' + by(java='<code>playwright.selectors().setTestIdAttribute("data-qa")</code>', py='<code>playwright.selectors.set_test_id_attribute("data-qa")</code>, or in pytest a fixture that calls it', js="<code>use: { testIdAttribute: 'data-qa' }</code> in playwright.config") + '. After that, getByTestId reads the new attribute.', 'pro')}
''', easy=True, kw=['getByLabel', 'getByPlaceholder', 'getByText', 'getByAltText', 'getByTitle', 'getByTestId', 'testIdAttribute', 'data-testid']),

    part('css', '🧩', 'CSS and XPath', f'''
<p><code>locator()</code> takes a CSS selector or an XPath. They are useful for old pages without good labels, but they describe how the page is built, not what the user sees.</p>
[[css]]
{table(['You want', 'Better choice', 'Fragile choice'], [
    ['the Sign in button', "getByRole('button', { name: 'Sign in' })", "locator('#login > button.btn-primary')"],
    ['the email box', "getByLabel('Email')", "locator('//form/div[1]/input')"],
    ['the price of the mug', "getByRole('listitem').filter({ hasText: 'Coffee mug' }).getByText(/₹/)", "locator('li:nth-child(1) span:nth-child(3)')"],
])}
{tip('Long XPaths copied from the browser tools, such as /html/body/div[2]/div/form/input, break as soon as one box is added to the page. Recorded tests from older tools are full of them, and they are the first thing to replace when a team moves to Playwright.', 'warn')}
''', kw=['css', 'xpath', 'locator', 'has-text', 'selector']),

    part('filter', '🔎', 'Filtering and chaining', f'''
<p>Real pages repeat things: five product cards, each with an Add to cart button. Find the right card first, then the button inside it. That is how you would describe it to a person: <i>the Add to cart button of the Coffee mug card</i>.</p>
[[filter]]
{table(['Method', 'Keeps'], [
    [by(java='filter(new FilterOptions().setHasText("x"))', py='filter(has_text="x")', js="filter({ hasText: 'x' })"), 'elements that contain the text somewhere inside'],
    [by(java='setHasNotText("x")', py='has_not_text="x"', js="hasNotText: 'x'"), 'elements that do not contain the text'],
    [by(java='setHas(locator)', py='has=locator', js='has: locator'), 'elements that contain an element the locator finds'],
    [by(java='setHasNot(locator)', py='has_not=locator', js='hasNot: locator'), 'elements that do not contain it'],
    [by(java='setVisible(true)', py='visible=True', js='visible: true'), 'only visible elements'],
    [by(java='first(), last(), nth(i)', py='first, last, nth(i)', js='first(), last(), nth(i)'), 'one element by position, nth counts from 0'],
    [by(java='a.and(b), a.or(b)', py='a.and_(b), a.or_(b)', js='a.and(b), a.or(b)'), 'elements both match, or either matches'],
])}
{tip('first(), last() and nth() depend on the order of the page. When the order changes, they quietly pick another element. Prefer a filter by text when you can.', 'warn')}
''', kw=['filter', 'hasText', 'has', 'hasNot', 'nth', 'first', 'last', 'and', 'or', 'chaining']),

    part('strict', '🚦', 'Strict mode', f'''
<p>When a locator finds more than one element, an action such as click or fill does not pick one for you. It fails with a <b>strict mode violation</b>. This protects you from a test that clicks the wrong button and still passes.</p>
[[strict]]
<p>The message is also a helper. It shows each element it found and a locator for each that finds only that one. Pick the one you meant, or better, add a name or a filter.</p>
''', kw=['strict mode', 'strict mode violation', 'count', 'multiple elements']),

    part('lists', '📋', 'Lists and tables', f'''
<p>Tables are where locators earn their keep. Find the row by something unique in it, such as a name or an order number, then act inside that row.</p>
[[walkloc]]
[[table]]
{tip('A bank or an admin portal often has tables with paging and sorting. A test that finds a row by position breaks the day someone adds an order. A test that finds the row by its order number keeps working.', 'life')}
''', kw=['table', 'row', 'cell', 'all', 'allTextContents', 'loop', 'list']),
]

INFO = {'title': 'Find it like a person would', 'panels': [
    panel([['e', '🧑‍🦯'], ['t', 'getByRole', {'b': 1}]], 'Role and name', 'What the user sees.', 'The first choice.'),
    panel([['e', '🏷️'], ['t', 'getByLabel', {'b': 1}]], 'Forms', 'Boxes by their label.', 'Placeholder when there is none.'),
    panel([['e', '🔎'], ['t', 'filter', {'b': 1}]], 'Narrow down', 'Card first, then button.', 'hasText, has, hasNot.'),
    panel([['e', '🚦'], ['t', 'strict', {'b': 1}]], 'One element', 'Actions need exactly one.', 'The error lists them all.')],
    'remember': 'A locator is searched again every time you use it, and an action needs exactly one match.'}

REAL = [
    ['🏦', 'A redesign that broke nothing', 'A bank moved its login form into a new layout. Tests that used getByLabel and getByRole kept passing, while old XPath tests in another team failed by the hundred.'],
    ['🌍', 'A site in twelve languages', 'A travel site runs the same tests in every language. Buttons are found by test id, because their text changes with the language.'],
    ['🛒', 'The wrong Add to cart', 'A test clicked the first Add to cart button on the page. When the product order changed, it bought the wrong item and still passed. A filter by product name fixed it.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter is about locators: how Playwright finds elements by role, label, text and test id, how to filter and chain them, strict mode, and working with lists and tables.',
        'यह अध्याय locators के बारे में है: Playwright role, label, text और test id से elements कैसे ढूँढता है, उन्हें filter और chain कैसे करें, strict mode, और lists व tables के साथ काम।',
        'ಈ ಅಧ್ಯಾಯ locators ಬಗ್ಗೆ: Playwright role, label, text ಮತ್ತು test id ಮೂಲಕ elements ಹೇಗೆ ಹುಡುಕುತ್ತದೆ, filter ಮತ್ತು chain ಹೇಗೆ ಮಾಡುವುದು, strict mode, ಮತ್ತು lists ಹಾಗೂ tables ಜೊತೆ ಕೆಲಸ.',
        'ଏହି ଅଧ୍ୟାୟ locators ବିଷୟରେ: Playwright role, label, text ଓ test id ଦ୍ୱାରା elements କିପରି ଖୋଜେ, filter ଓ chain କିପରି କରିବେ, strict mode, ଏବଂ lists ଓ tables ସହ କାମ।',
        'يتناول هذا الفصل المحددات: كيف يجد Playwright العناصر بالدور والتسمية والنص ومعرّف الاختبار، وكيف تصفّيها وتسلسلها، والوضع الصارم، والعمل مع القوائم والجداول.',
        'Dieses Kapitel behandelt Locators: wie Playwright Elemente über Rolle, Label, Text und Test-ID findet, wie man sie filtert und verkettet, den Strict Mode und die Arbeit mit Listen und Tabellen.'),
    say('what', 'What a locator is', 'A locator describes how to find an element. It does not hold the element. Playwright searches the page again every time you use it, so it never goes stale.',
        'Locator बताता है कि element कैसे ढूँढें। वह element को पकड़कर नहीं रखता। हर इस्तेमाल पर Playwright page को फिर से खोजता है, इसलिए वह कभी पुराना नहीं होता।',
        'Locator ಒಂದು element ಅನ್ನು ಹೇಗೆ ಹುಡುಕಬೇಕು ಎಂದು ವಿವರಿಸುತ್ತದೆ. ಅದು element ಅನ್ನು ಹಿಡಿದಿಡುವುದಿಲ್ಲ. ಪ್ರತಿ ಬಳಕೆಯಲ್ಲೂ Playwright page ಅನ್ನು ಮತ್ತೆ ಹುಡುಕುತ್ತದೆ, ಆದ್ದರಿಂದ ಅದು ಹಳೆಯದಾಗುವುದಿಲ್ಲ.',
        'Locator element କିପରି ଖୋଜିବେ ତାହା ବର୍ଣ୍ଣନା କରେ। ଏହା element କୁ ଧରି ରଖେ ନାହିଁ। ପ୍ରତି ବ୍ୟବହାରରେ Playwright page କୁ ପୁଣି ଖୋଜେ, ତେଣୁ ଏହା କେବେ ପୁରୁଣା ହୁଏ ନାହିଁ।',
        'المحدد يصف كيفية العثور على عنصر ولا يحتفظ بالعنصر نفسه. يبحث Playwright في الصفحة من جديد في كل استخدام، لذلك لا يصبح قديمًا أبدًا.',
        'Ein Locator beschreibt, wie ein Element gefunden wird. Er hält das Element nicht fest. Playwright durchsucht die Seite bei jeder Verwendung neu, deshalb veraltet er nie.'),
    say('role', 'getByRole', 'getByRole finds elements by their role, such as button, link or heading, and their name, the words a person reads. The name matches ignoring case unless you ask for exact.',
        'getByRole elements को उनके role, जैसे button, link या heading, और उनके name से ढूँढता है, यानी वे शब्द जो व्यक्ति पढ़ता है। exact न कहें तो name बिना case देखे मिलाया जाता है।',
        'getByRole elements ಅನ್ನು ಅವುಗಳ role, ಉದಾಹರಣೆಗೆ button, link ಅಥವಾ heading, ಮತ್ತು name ಮೂಲಕ ಹುಡುಕುತ್ತದೆ, ಅಂದರೆ ವ್ಯಕ್ತಿ ಓದುವ ಪದಗಳು. exact ಕೇಳದಿದ್ದರೆ name ಅನ್ನು case ನೋಡದೆ ಹೋಲಿಸಲಾಗುತ್ತದೆ.',
        'getByRole elements କୁ ସେମାନଙ୍କ role, ଯେପରି button, link ବା heading, ଏବଂ name ଦ୍ୱାରା ଖୋଜେ, ଅର୍ଥାତ୍ ବ୍ୟକ୍ତି ପଢ଼ୁଥିବା ଶବ୍ଦ। exact ନ କହିଲେ name case ନ ଦେଖି ମେଳ ହୁଏ।',
        'يجد getByRole العناصر حسب دورها مثل زر أو رابط أو عنوان، وحسب اسمها وهو الكلمات التي يقرؤها الشخص. تتم مطابقة الاسم دون مراعاة حالة الأحرف ما لم تطلب المطابقة التامة.',
        'getByRole findet Elemente über ihre Rolle, etwa Button, Link oder Überschrift, und ihren Namen, also die Wörter, die ein Mensch liest. Der Name wird ohne Beachtung der Groß- und Kleinschreibung verglichen, außer du verlangst exact.'),
    say('getby', 'Other locators', 'getByLabel finds form boxes by their label, getByPlaceholder by hint text, getByText by visible text, getByAltText and getByTitle by attributes, and getByTestId by an id agreed with developers.',
        'getByLabel form boxes को label से, getByPlaceholder hint text से, getByText दिखने वाले text से, getByAltText और getByTitle attributes से, और getByTestId developers के साथ तय id से ढूँढता है।',
        'getByLabel form boxes ಅನ್ನು label ಮೂಲಕ, getByPlaceholder hint text ಮೂಲಕ, getByText ಕಾಣುವ text ಮೂಲಕ, getByAltText ಮತ್ತು getByTitle attributes ಮೂಲಕ, ಮತ್ತು getByTestId developers ಜೊತೆ ಒಪ್ಪಿದ id ಮೂಲಕ ಹುಡುಕುತ್ತದೆ.',
        'getByLabel form boxes କୁ label ଦ୍ୱାରା, getByPlaceholder hint text ଦ୍ୱାରା, getByText ଦେଖାଯାଉଥିବା text ଦ୍ୱାରା, getByAltText ଓ getByTitle attributes ଦ୍ୱାରା, ଏବଂ getByTestId developers ସହ ସ୍ଥିର id ଦ୍ୱାରା ଖୋଜେ।',
        'يجد getByLabel حقول النماذج بتسميتها، وgetByPlaceholder بنص التلميح، وgetByText بالنص الظاهر، وgetByAltText وgetByTitle بالسمات، وgetByTestId بمعرّف متفق عليه مع المطورين.',
        'getByLabel findet Formularfelder über ihr Label, getByPlaceholder über den Hinweistext, getByText über sichtbaren Text, getByAltText und getByTitle über Attribute und getByTestId über eine mit den Entwicklern vereinbarte ID.'),
    say('css', 'CSS and XPath', 'locator takes CSS or XPath. They work, but they describe how the page is built, so they break when the code changes. Use them as the last resort.',
        'locator CSS या XPath लेता है। ये काम करते हैं, पर page की बनावट बताते हैं, इसलिए code बदलने पर टूट जाते हैं। इन्हें आख़िरी विकल्प रखें।',
        'locator CSS ಅಥವಾ XPath ತೆಗೆದುಕೊಳ್ಳುತ್ತದೆ. ಅವು ಕೆಲಸ ಮಾಡುತ್ತವೆ, ಆದರೆ page ರಚನೆಯನ್ನು ವಿವರಿಸುತ್ತವೆ, ಆದ್ದರಿಂದ code ಬದಲಾದಾಗ ಮುರಿಯುತ್ತವೆ. ಕೊನೆಯ ಆಯ್ಕೆಯಾಗಿ ಬಳಸಿ.',
        'locator CSS ବା XPath ନିଏ। ଏଗୁଡ଼ିକ କାମ କରେ, କିନ୍ତୁ page ର ଗଠନ ବର୍ଣ୍ଣନା କରେ, ତେଣୁ code ବଦଳିଲେ ଭାଙ୍ଗିଯାଏ। ଶେଷ ବିକଳ୍ପ ଭାବେ ବ୍ୟବହାର କରନ୍ତୁ।',
        'تقبل locator محددات CSS أو XPath. إنها تعمل لكنها تصف بنية الصفحة، لذلك تنكسر عندما تتغير الشيفرة. استخدمها كخيار أخير.',
        'locator nimmt CSS oder XPath. Das funktioniert, beschreibt aber den Aufbau der Seite und bricht, wenn sich der Code ändert. Nutze es als letzten Ausweg.'),
    say('filter', 'Filtering', 'filter keeps elements that contain some text or another locator. Chain locators to search inside the elements that are left. first, last and nth pick by position, and and or combine two locators.',
        'filter उन elements को रखता है जिनमें कुछ text या दूसरा locator हो। बचे elements के अंदर खोजने के लिए locators को chain करें। first, last और nth स्थिति से चुनते हैं, और and व or दो locators जोड़ते हैं।',
        'filter ಕೆಲವು text ಅಥವಾ ಇನ್ನೊಂದು locator ಇರುವ elements ಅನ್ನು ಉಳಿಸುತ್ತದೆ. ಉಳಿದ elements ಒಳಗೆ ಹುಡುಕಲು locators ಅನ್ನು chain ಮಾಡಿ. first, last ಮತ್ತು nth ಸ್ಥಾನದಿಂದ ಆರಿಸುತ್ತವೆ, and ಮತ್ತು or ಎರಡು locators ಸೇರಿಸುತ್ತವೆ.',
        'filter ସେହି elements ରଖେ ଯେଉଁଥିରେ କିଛି text ବା ଅନ୍ୟ locator ଅଛି। ବାକି elements ଭିତରେ ଖୋଜିବାକୁ locators chain କରନ୍ତୁ। first, last ଓ nth ସ୍ଥାନ ଅନୁସାରେ ବାଛନ୍ତି, and ଓ or ଦୁଇ locators ଯୋଡନ୍ତି।',
        'يحتفظ filter بالعناصر التي تحتوي على نص معين أو على محدد آخر. سلسل المحددات للبحث داخل العناصر المتبقية. تختار first وlast وnth حسب الموضع، وتجمع and وor بين محددين.',
        'filter behält Elemente, die einen Text oder einen anderen Locator enthalten. Verkette Locators, um in den verbleibenden Elementen zu suchen. first, last und nth wählen nach Position, and und or verbinden zwei Locators.'),
    say('strict', 'Strict mode', 'An action needs exactly one element. If a locator finds several, click and fill fail with a strict mode violation that lists every match and suggests a locator for each.',
        'Action को ठीक एक element चाहिए। अगर locator कई ढूँढे तो click और fill strict mode violation के साथ fail होते हैं, जो हर match दिखाता है और हर एक के लिए locator सुझाता है।',
        'Action ಗೆ ನಿಖರವಾಗಿ ಒಂದು element ಬೇಕು. Locator ಹಲವು ಕಂಡರೆ click ಮತ್ತು fill strict mode violation ನೊಂದಿಗೆ fail ಆಗುತ್ತವೆ, ಅದು ಪ್ರತಿ match ತೋರಿಸಿ ಪ್ರತಿಯೊಂದಕ್ಕೂ locator ಸೂಚಿಸುತ್ತದೆ.',
        'Action ପାଇଁ ଠିକ୍ ଗୋଟିଏ element ଦରକାର। Locator ଅନେକ ପାଇଲେ click ଓ fill strict mode violation ସହ fail ହୁଏ, ଯାହା ପ୍ରତି match ଦେଖାଏ ଓ ପ୍ରତିଟି ପାଇଁ locator ପରାମର୍ଶ ଦିଏ।',
        'يحتاج الإجراء إلى عنصر واحد بالضبط. إذا وجد المحدد عدة عناصر، يفشل click وfill بخطأ strict mode violation الذي يسرد كل تطابق ويقترح محددًا لكل منها.',
        'Eine Aktion braucht genau ein Element. Findet ein Locator mehrere, scheitern click und fill mit einer Strict-Mode-Verletzung, die jeden Treffer auflistet und für jeden einen Locator vorschlägt.'),
    say('lists', 'Lists and tables', 'Find the row by something unique in it, such as a name or an order number, then act inside that row. all turns a locator into a list you can loop over, but it does not wait.',
        'Row को उसमें मौजूद किसी अनोखी चीज़, जैसे नाम या order number, से ढूँढें, फिर उसी row के अंदर काम करें। all locator को loop करने लायक list बनाता है, पर इंतज़ार नहीं करता।',
        'Row ಅನ್ನು ಅದರಲ್ಲಿರುವ ವಿಶಿಷ್ಟ ವಿಷಯ, ಉದಾಹರಣೆಗೆ ಹೆಸರು ಅಥವಾ order number, ಮೂಲಕ ಹುಡುಕಿ, ನಂತರ ಆ row ಒಳಗೆ ಕೆಲಸ ಮಾಡಿ. all locator ಅನ್ನು loop ಮಾಡಬಹುದಾದ list ಆಗಿ ಮಾಡುತ್ತದೆ, ಆದರೆ ಕಾಯುವುದಿಲ್ಲ.',
        'Row କୁ ସେଥିରେ ଥିବା ଅନନ୍ୟ କିଛି, ଯେପରି ନାମ ବା order number, ଦ୍ୱାରା ଖୋଜନ୍ତୁ, ତାପରେ ସେହି row ଭିତରେ କାମ କରନ୍ତୁ। all locator କୁ loop କରିହେବା list କରେ, କିନ୍ତୁ ଅପେକ୍ଷା କରେ ନାହିଁ।',
        'ابحث عن الصف بشيء فريد فيه مثل اسم أو رقم طلب، ثم نفّذ الإجراء داخل ذلك الصف. يحوّل all المحدد إلى قائمة يمكنك المرور عليها، لكنه لا ينتظر.',
        'Finde die Zeile über etwas Eindeutiges darin, etwa einen Namen oder eine Bestellnummer, und handle dann innerhalb dieser Zeile. all macht aus einem Locator eine Liste zum Durchlaufen, wartet aber nicht.'),
    say('practice', 'Playground labs', 'In the labs you find the price of the coffee mug inside its card, and you delete one order from the orders table by its customer name.',
        'Labs में आप coffee mug के card के अंदर उसकी कीमत ढूँढते हैं, और orders table से एक order को customer के नाम से हटाते हैं।',
        'Labs ನಲ್ಲಿ ನೀವು coffee mug card ಒಳಗೆ ಅದರ ಬೆಲೆ ಹುಡುಕುತ್ತೀರಿ, ಮತ್ತು orders table ನಿಂದ customer ಹೆಸರಿನ ಮೂಲಕ ಒಂದು order ಅಳಿಸುತ್ತೀರಿ.',
        'Labs ରେ ଆପଣ coffee mug card ଭିତରେ ତାର ଦାମ ଖୋଜନ୍ତି, ଏବଂ orders table ରୁ customer ନାମ ଦ୍ୱାରା ଗୋଟିଏ order ହଟାନ୍ତି।',
        'في المختبرات تجد سعر كوب القهوة داخل بطاقته، وتحذف طلبًا واحدًا من جدول الطلبات باسم العميل.',
        'In den Labs findest du den Preis der Kaffeetasse in ihrer Karte und löschst eine Bestellung aus der Tabelle über den Kundennamen.'),
]

QUIZ = [
    quiz(1, 'Which locator does Playwright recommend trying first?', ['locator(css)', 'getByRole', 'getByTestId', 'XPath'], 1,
         'It is about what the user sees.', 'getByRole with a name matches how people and assistive technology find things, so it rarely breaks.'),
    quiz(1, 'When does a locator search the page?', ['When it is created', 'Every time it is used', 'Only once per test', 'When the page loads'], 1,
         'Look at the three counts from one locator.', 'A locator is searched again at the moment you use it, so it never goes stale.'),
    quiz(1, 'How do you find the Email box of a form with a label Email?', ['getByText(\'Email\')', 'getByLabel(\'Email\')', 'getByTitle(\'Email\')', 'locator(\'Email\')'], 1,
         'Form boxes have labels.', 'getByLabel finds the input that the label belongs to.'),
    quiz(1, 'What role does a &lt;select&gt; drop down have?', ['select', 'listbox', 'combobox', 'menu'], 2,
         'Look at the role table.', 'A single choice &lt;select&gt; has the role combobox.'),
    quiz(2, 'getByRole(\'button\', { name: \'add to cart\' }) on a page with four "Add to cart" buttons finds how many?', ['0', '1', '4', 'an error'], 2,
         'Name matching ignores case by default.', 'By default the name is matched ignoring case and as a part, so all four match.'),
    quiz(2, 'A locator finds 4 buttons and you call click(). What happens?', ['It clicks the first', 'It clicks all four', 'It fails with a strict mode violation', 'It waits forever'], 2,
         'Actions need one element.', 'Strict mode makes an action fail when the locator finds more than one element.'),
    quiz(2, 'Which keeps only the product cards that contain a disabled button?', ['filter({ hasText: \'disabled\' })', 'filter({ has: page.getByRole(\'button\', { disabled: true }) })', 'nth(3)', 'and(\'disabled\')'], 1,
         'has takes another locator.', 'filter with has keeps elements that contain an element the inner locator finds.'),
    quiz(2, 'nth(2) gives which element?', ['the second', 'the third', 'the last', 'two elements'], 1,
         'Counting starts at 0.', 'nth counts from 0, so nth(2) is the third.'),
    quiz(2, 'Why can locator.all() give a wrong result when the list is still loading?', ['It is slow', 'It does not wait for elements', 'It only works in Java', 'It returns strings'], 1,
         'Compare it with toHaveCount.', 'all() returns what is there right now. Check the count first, then loop.'),
    quiz(3, 'In Python, how do you combine two locators so that either one matches?', ['a.or(b)', 'a | b', 'a.or_(b)', 'a.either(b)'], 2,
         'or is a keyword in Python.', 'Python uses or_ and and_ because or and and are reserved words.'),
    quiz(3, 'How does locator() decide between CSS and XPath?', ['It tries both', 'A string starting with // or .. is XPath, otherwise CSS', 'XPath needs xpath= always', 'It asks the browser'], 1,
         'Look at the CSS example result.', 'Playwright treats a selector starting with // or .. as XPath. You can also write xpath= or css= in front.'),
    quiz(3, 'Your site is translated into many languages. Which locator keeps one test working in all of them?', ['getByText', 'getByRole with a name', 'getByTestId', 'getByPlaceholder'], 2,
         'Which one does not depend on the words?', 'A test id stays the same in every language, while names and text change.'),
]

CALC = [
    calc(1, 'The products page shows 5 cards. 1 is out of stock. How many Add to cart buttons are there?', 4, '5 - 1', ['5 cards - 1 out of stock = 4 buttons']),
    calc(1, 'cards.nth(i) is the fourth card. What is i?', 3, 'nth counts from 0', ['first is 0, second 1, third 2, fourth 3']),
    calc(1, 'The shop has Gel pen, Coffee mug, Desk lamp, Notebook and Water bottle. You search for the letter o. How many cards are left?', 3,
         'Count the names that contain the letter o', ['Gel pen: no', 'Coffee mug: yes', 'Desk lamp: no', 'Notebook: yes', 'Water bottle: yes', '3 cards']),
    calc(2, 'The orders table shows 5 rows per page and has 7 orders. How many pages?', 2, '7 / 5, rounded up', ['7 / 5 = 1.4', 'rounded up: 2 pages']),
    calc(2, 'getByRole(\'row\') on a page of 5 orders. The header row counts too. How many rows?', 6, '5 + 1', ['5 data rows + 1 header row = 6']),
    calc(2, 'Kitchen has Coffee mug (₹199) and Water bottle (₹349). What do they cost together?', 548, '199 + 349', ['199 + 349 = 548']),
    calc(3, 'After deleting 1 order from 7, the table shows 5 per page. How many rows are on page 2?', 1, '7 - 1 = 6', ['6 orders', 'page 1 shows 5', 'page 2 shows 1']),
    calc(3, 'An old suite has 120 tests with copied XPaths. A redesign breaks 3 of every 4 of them. How many fail?', 90, '120 × 3 / 4', ['120 / 4 = 30', '30 × 3 = 90 tests fail']),
]

LABS = [
    {'id': 'mug', 'title': 'Find the price inside one card', 'name': 'the coffee mug costs 199',
     'task': 'On <code>/products</code>, find the list item that contains <b>Coffee mug</b> with a filter, then check that the price <b>₹199</b> is visible inside that card.',
     'goal': 'The check passes on the price inside the Coffee mug card.', 'start': '/products',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('the coffee mug costs 199', async ({ page }) => {
  await page.goto('/products');
  // find the Coffee mug card, then the price inside it
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('the coffee mug costs 199', async ({ page }) => {
  await page.goto('/products');
  const mug = page.getByRole('listitem').filter({ hasText: 'Coffee mug' });
  await expect(mug.getByText('₹199')).toBeVisible();
});'''},
     'hint': "<code>page.getByRole('listitem').filter({ hasText: 'Coffee mug' })</code> is the card. Chain <code>.getByText('₹199')</code> on it.",
     'why': 'The filter picks one card out of five, and the chained getByText searches only inside it. The same price on another card would not count.',
     'check': [["/filter|Filter/.test(ctx.code)", 'The test filters the cards'], ["/199/.test(ctx.code)", 'The test checks the price']]},
    {'id': 'delrow', 'title': 'Delete one order by its customer', 'name': 'delete the order of Meera',
     'task': 'On <code>/orders</code>, find the row that contains <b>Meera</b>, click the <b>Delete</b> button in that row, and check that the status says <b>Order #1003 deleted</b>.',
     'goal': 'Meera\'s order is deleted, and only hers.', 'start': '/orders',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('delete the order of Meera', async ({ page }) => {
  await page.goto('/orders');
  // find Meera's row, then the Delete button inside it
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('delete the order of Meera', async ({ page }) => {
  await page.goto('/orders');
  const row = page.getByRole('row').filter({ hasText: 'Meera' });
  await row.getByRole('button', { name: 'Delete' }).click();
  await expect(page.getByRole('status')).toHaveText('Order #1003 deleted');
});'''},
     'hint': "Try <code>page.getByRole('button', { name: 'Delete' }).click()</code> first and read the strict mode error. Then start from <code>page.getByRole('row').filter({ hasText: 'Meera' })</code>.",
     'why': 'There are five Delete buttons. The row filter narrows the search to Meera\'s row, so exactly one button is left and the click is allowed.',
     'check': [["/Order #1003 deleted/.test(ctx.text)", 'Order 1003 was deleted'], ["/filter|Filter/.test(ctx.code)", 'The test finds the row with a filter']]},
]

T = {
    'slug': 'pw-locators', 'title': 'Locators: finding elements', 'short': 'Locators', 'emoji': '🎯', 'module': MODULE, 'minutes': 24,
    'lead': 'Find any element the way a person would: by its role and name, its label, its text or a test id. Then narrow down with filters, keep strict mode on your side, and work through lists and tables.',
    'desc': 'getByRole, getByLabel, getByPlaceholder, getByText, getByAltText, getByTitle, getByTestId, CSS and XPath, filter with hasText, has and hasNot, nth, first, last, and, or, strict mode and tables in Java, Python, JavaScript and TypeScript.',
    'summary': 'Why a locator is searched again every time, a live locator lab, which locator to try first, getByRole with names, levels and states, labels, placeholders, text, titles and test ids, custom test id attributes, CSS and XPath and why they break, filter, chaining, nth, and, or, strict mode violations, and a recorded walk through a sortable, paged table.',
    'keywords': ['locator', 'getByRole', 'getByLabel', 'getByText', 'getByPlaceholder', 'getByTestId', 'getByAltText', 'getByTitle', 'css', 'xpath', 'filter', 'hasText', 'nth', 'strict mode', 'table', 'and', 'or'],
    'plain': 'A locator is how a test says which element it means. The best ones read like an instruction to a person: the Sign in button, the Email box, the Delete button in Meera\'s row.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
