import re

from pkit import part, say, quiz, calc, panel, four, js, ts, py, jv, table, tip

MODULE = ('🏗️', 'Framework design', 'pw-framework', 'Page objects and components, a real framework built step by step in each language, CI pipelines and reports that teams read every day.')

POM_INI = '''[pytest]
addopts = --base-url http://localhost:4173
pythonpath = .'''


def to_js(src):
    """The JavaScript version of our TypeScript page objects: the same code without the types."""
    src = re.sub(r"(?m)^import type .*\n", '', src)
    src = re.sub(r"(?m)^type \w+ = .*\n", '', src)
    src = re.sub(r"(?m)^\s+(?:private |readonly )+\w+: [\w<>\[\]]+;\n", '', src)
    src = re.sub(r"(\w+): (?:string|number|Page|Locator)\b", r'\1', src)
    src = re.sub(r"(from '\.\.?/[\w/]+)'", r"\1.js'", src)
    src = src.replace('.extend<Pages>(', '.extend(')
    return re.sub(r'\{\n\n(\s+constructor)', r'{\n\1', src).replace('\n\n\n', '\n\n')


# ---------- step 1: one page object ----------
LOGIN_TS = '''import type { Page, Locator } from '@playwright/test';

// Everything a test needs to know about the sign in page, in one place
export class LoginPage {
  private readonly page: Page;
  readonly email: Locator;
  readonly password: Locator;
  readonly signInButton: Locator;
  readonly error: Locator;

  constructor(page: Page) {
    this.page = page;
    this.email = page.getByLabel('Email');
    this.password = page.getByLabel('Password');
    this.signInButton = page.getByRole('button', { name: 'Sign in' });
    this.error = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async signIn(email: string, password: string) {
    await this.email.fill(email);
    await this.password.fill(password);
    await this.signInButton.click();
  }
}'''

LOGIN_TEST_TS = '''import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

test('Asha can sign in', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.signIn('asha@shop.example', 's3cret');
  await expect(page.getByText('Hello, Asha')).toBeVisible();
});

test('a wrong password is refused', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.signIn('asha@shop.example', 'wrong');
  await expect(loginPage.error).toHaveText('Wrong email or password');
});'''

LOGIN_PY = '''from playwright.sync_api import Page


# Everything a test needs to know about the sign in page, in one place
class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.email = page.get_by_label("Email")
        self.password = page.get_by_label("Password")
        self.sign_in_button = page.get_by_role("button", name="Sign in")
        self.error = page.get_by_role("alert")

    def goto(self):
        self.page.goto("/login")

    def sign_in(self, email: str, password: str):
        self.email.fill(email)
        self.password.fill(password)
        self.sign_in_button.click()'''

LOGIN_TEST_PY = '''from playwright.sync_api import Page, expect

from pages.login_page import LoginPage


def test_asha_can_sign_in(page: Page):
    login_page = LoginPage(page)
    login_page.goto()
    login_page.sign_in("asha@shop.example", "s3cret")
    expect(page.get_by_text("Hello, Asha")).to_be_visible()


def test_a_wrong_password_is_refused(page: Page):
    login_page = LoginPage(page)
    login_page.goto()
    login_page.sign_in("asha@shop.example", "wrong")
    expect(login_page.error).to_have_text("Wrong email or password")'''

LOGIN_JAVA = '''package com.brainy.pages;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;

// Everything a test needs to know about the sign in page, in one place
public class LoginPage {
  private final Page page;
  public final Locator email;
  public final Locator password;
  public final Locator signInButton;
  public final Locator error;

  public LoginPage(Page page) {
    this.page = page;
    this.email = page.getByLabel("Email");
    this.password = page.getByLabel("Password");
    this.signInButton = page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in"));
    this.error = page.getByRole(AriaRole.ALERT);
  }

  public void navigate() {
    page.navigate("/login");
  }

  public void signIn(String email, String password) {
    this.email.fill(email);
    this.password.fill(password);
    signInButton.click();
  }
}'''

LOGIN_TEST_JAVA = '''package com.brainy;

import com.brainy.pages.LoginPage;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class LoginTest {
  @Test
  void ashaCanSignIn(Page page) {
    LoginPage loginPage = new LoginPage(page);
    loginPage.navigate();
    loginPage.signIn("asha@shop.example", "s3cret");
    assertThat(page.getByText("Hello, Asha")).isVisible();
  }

  @Test
  void aWrongPasswordIsRefused(Page page) {
    LoginPage loginPage = new LoginPage(page);
    loginPage.navigate();
    loginPage.signIn("asha@shop.example", "wrong");
    assertThat(loginPage.error).hasText("Wrong email or password");
  }
}'''

# ---------- step 2: components inside a page ----------
HEADER_TS = '''import type { Page, Locator } from '@playwright/test';

// The header is on every page, so it is a component, not a page
export class Header {
  readonly greeting: Locator;
  readonly cartCount: Locator;
  readonly signOut: Locator;

  constructor(page: Page) {
    const root = page.getByRole('banner');
    this.greeting = root.locator('#hello');
    this.cartCount = root.getByTestId('cart-count');
    this.signOut = root.getByRole('link', { name: 'Sign out' });
  }
}'''

CARD_TS = '''import type { Locator } from '@playwright/test';

// One product card. Every locator starts from the card, so it never finds another product's button.
export class ProductCard {
  readonly root: Locator;
  readonly price: Locator;
  readonly button: Locator;

  constructor(root: Locator) {
    this.root = root;
    this.price = root.locator('.price');
    this.button = root.getByRole('button');
  }

  async addToCart() {
    await this.root.getByRole('button', { name: 'Add to cart' }).click();
  }
}'''

PRODUCTS_TS = '''import type { Page, Locator } from '@playwright/test';
import { Header } from '../components/Header';
import { ProductCard } from '../components/ProductCard';

export class ProductsPage {
  private readonly page: Page;
  readonly header: Header;
  readonly search: Locator;
  readonly cards: Locator;

  constructor(page: Page) {
    this.page = page;
    this.header = new Header(page);
    this.search = page.getByPlaceholder('Search products');
    this.cards = page.getByRole('listitem');
  }

  async goto() {
    await this.page.goto('/products');
  }

  card(name: string) {
    return new ProductCard(this.cards.filter({ has: this.page.getByRole('heading', { name }) }));
  }
}'''

CART_TEST_TS = '''import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { ProductsPage } from '../pages/ProductsPage';

test('Asha adds the lamp and the mug', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.signIn('asha@shop.example', 's3cret');

  const products = new ProductsPage(page);
  await expect(products.header.greeting).toHaveText('Hello, Asha');
  await products.card('Desk lamp').addToCart();
  await expect(products.header.cartCount).toHaveText('1');
  await products.card('Coffee mug').addToCart();
  await expect(products.header.cartCount).toHaveText('2');
});

test('the notebook is out of stock', async ({ page }) => {
  const products = new ProductsPage(page);
  await products.goto();
  const notebook = products.card('Notebook');
  await expect(notebook.price).toHaveText('₹60');
  await expect(notebook.button).toHaveText('Out of stock');
  await expect(notebook.button).toBeDisabled();
});'''

HEADER_PY = '''from playwright.sync_api import Page


# The header is on every page, so it is a component, not a page
class Header:
    def __init__(self, page: Page):
        root = page.get_by_role("banner")
        self.greeting = root.locator("#hello")
        self.cart_count = root.get_by_test_id("cart-count")
        self.sign_out = root.get_by_role("link", name="Sign out")'''

CARD_PY = '''from playwright.sync_api import Locator


# One product card. Every locator starts from the card, so it never finds another product's button.
class ProductCard:
    def __init__(self, root: Locator):
        self.root = root
        self.price = root.locator(".price")
        self.button = root.get_by_role("button")

    def add_to_cart(self):
        self.root.get_by_role("button", name="Add to cart").click()'''

PRODUCTS_PY = '''from playwright.sync_api import Page

from components.header import Header
from components.product_card import ProductCard


class ProductsPage:
    def __init__(self, page: Page):
        self.page = page
        self.header = Header(page)
        self.search = page.get_by_placeholder("Search products")
        self.cards = page.get_by_role("listitem")

    def goto(self):
        self.page.goto("/products")

    def card(self, name: str) -> ProductCard:
        return ProductCard(self.cards.filter(has=self.page.get_by_role("heading", name=name)))'''

CART_TEST_PY = '''from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from pages.products_page import ProductsPage


def test_asha_adds_the_lamp_and_the_mug(page: Page):
    login_page = LoginPage(page)
    login_page.goto()
    login_page.sign_in("asha@shop.example", "s3cret")

    products = ProductsPage(page)
    expect(products.header.greeting).to_have_text("Hello, Asha")
    products.card("Desk lamp").add_to_cart()
    expect(products.header.cart_count).to_have_text("1")
    products.card("Coffee mug").add_to_cart()
    expect(products.header.cart_count).to_have_text("2")


def test_the_notebook_is_out_of_stock(page: Page):
    products = ProductsPage(page)
    products.goto()
    notebook = products.card("Notebook")
    expect(notebook.price).to_have_text("₹60")
    expect(notebook.button).to_have_text("Out of stock")
    expect(notebook.button).to_be_disabled()'''

HEADER_JAVA = '''package com.brainy.components;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;

// The header is on every page, so it is a component, not a page
public class Header {
  public final Locator greeting;
  public final Locator cartCount;
  public final Locator signOut;

  public Header(Page page) {
    Locator root = page.getByRole(AriaRole.BANNER);
    this.greeting = root.locator("#hello");
    this.cartCount = root.getByTestId("cart-count");
    this.signOut = root.getByRole(AriaRole.LINK, new Locator.GetByRoleOptions().setName("Sign out"));
  }
}'''

CARD_JAVA = '''package com.brainy.components;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.options.AriaRole;

// One product card. Every locator starts from the card, so it never finds another product's button.
public class ProductCard {
  public final Locator root;
  public final Locator price;
  public final Locator button;

  public ProductCard(Locator root) {
    this.root = root;
    this.price = root.locator(".price");
    this.button = root.getByRole(AriaRole.BUTTON);
  }

  public void addToCart() {
    root.getByRole(AriaRole.BUTTON, new Locator.GetByRoleOptions().setName("Add to cart")).click();
  }
}'''

PRODUCTS_JAVA = '''package com.brainy.pages;

import com.brainy.components.Header;
import com.brainy.components.ProductCard;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;

public class ProductsPage {
  private final Page page;
  public final Header header;
  public final Locator search;
  public final Locator cards;

  public ProductsPage(Page page) {
    this.page = page;
    this.header = new Header(page);
    this.search = page.getByPlaceholder("Search products");
    this.cards = page.getByRole(AriaRole.LISTITEM);
  }

  public void navigate() {
    page.navigate("/products");
  }

  public ProductCard card(String name) {
    return new ProductCard(cards.filter(new Locator.FilterOptions()
        .setHas(page.getByRole(AriaRole.HEADING, new Page.GetByRoleOptions().setName(name)))));
  }
}'''

CART_TEST_JAVA = '''package com.brainy;

import com.brainy.components.ProductCard;
import com.brainy.pages.LoginPage;
import com.brainy.pages.ProductsPage;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class CartTest {
  @Test
  void ashaAddsTheLampAndTheMug(Page page) {
    LoginPage loginPage = new LoginPage(page);
    loginPage.navigate();
    loginPage.signIn("asha@shop.example", "s3cret");

    ProductsPage products = new ProductsPage(page);
    assertThat(products.header.greeting).hasText("Hello, Asha");
    products.card("Desk lamp").addToCart();
    assertThat(products.header.cartCount).hasText("1");
    products.card("Coffee mug").addToCart();
    assertThat(products.header.cartCount).hasText("2");
  }

  @Test
  void theNotebookIsOutOfStock(Page page) {
    ProductsPage products = new ProductsPage(page);
    products.navigate();
    ProductCard notebook = products.card("Notebook");
    assertThat(notebook.price).hasText("₹60");
    assertThat(notebook.button).hasText("Out of stock");
    assertThat(notebook.button).isDisabled();
  }
}'''

# ---------- step 3: hand the page objects to tests as fixtures ----------
FIX_TS = '''import { test as base } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { ProductsPage } from '../pages/ProductsPage';

type Pages = { loginPage: LoginPage; productsPage: ProductsPage };

// Tests ask for loginPage or productsPage by name, like they ask for page
export const test = base.extend<Pages>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  productsPage: async ({ page, loginPage }, use) => {
    await loginPage.goto();
    await loginPage.signIn('asha@shop.example', 's3cret');   // productsPage always starts signed in
    await use(new ProductsPage(page));
  },
});

export { expect } from '@playwright/test';'''

FIX_TEST_TS = '''import { test, expect } from '../fixtures/pages';

test('the mug costs 199 rupees and can be added', async ({ productsPage }) => {
  const mug = productsPage.card('Coffee mug');
  await expect(mug.price).toHaveText('₹199');
  await mug.addToCart();
  await expect(productsPage.header.cartCount).toHaveText('1');
});

test('the search finds one lamp', async ({ productsPage }) => {
  await productsPage.search.fill('lamp');
  await expect(productsPage.cards).toHaveCount(1);
});'''

FIX_CONFTEST = '''import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage
from pages.products_page import ProductsPage


# Tests ask for login_page or products_page by name, like they ask for page
@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def products_page(page: Page, login_page: LoginPage) -> ProductsPage:
    login_page.goto()
    login_page.sign_in("asha@shop.example", "s3cret")   # products_page always starts signed in
    return ProductsPage(page)'''

FIX_TEST_PY = '''from playwright.sync_api import expect

from pages.products_page import ProductsPage


def test_the_mug_costs_199_rupees_and_can_be_added(products_page: ProductsPage):
    mug = products_page.card("Coffee mug")
    expect(mug.price).to_have_text("₹199")
    mug.add_to_cart()
    expect(products_page.header.cart_count).to_have_text("1")


def test_the_search_finds_one_lamp(products_page: ProductsPage):
    products_page.search.fill("lamp")
    expect(products_page.cards).to_have_count(1)'''

FIX_BASE_JAVA = '''package com.brainy;

import com.brainy.pages.LoginPage;
import com.brainy.pages.ProductsPage;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import org.junit.jupiter.api.BeforeEach;

// Every test class that extends ShopTest gets signed in page objects
@UsePlaywright(ShopOptions.class)
public abstract class ShopTest {
  protected LoginPage loginPage;
  protected ProductsPage productsPage;

  @BeforeEach
  void createPages(Page page) {
    loginPage = new LoginPage(page);
    productsPage = new ProductsPage(page);
    loginPage.navigate();
    loginPage.signIn("asha@shop.example", "s3cret");
  }
}'''

FIX_TEST_JAVA = '''package com.brainy;

import com.brainy.components.ProductCard;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

public class MugTest extends ShopTest {
  @Test
  void theMugCosts199RupeesAndCanBeAdded() {
    ProductCard mug = productsPage.card("Coffee mug");
    assertThat(mug.price).hasText("₹199");
    mug.addToCart();
    assertThat(productsPage.header.cartCount).hasText("1");
  }

  @Test
  void theSearchFindsOneLamp() {
    productsPage.search.fill("lamp");
    assertThat(productsPage.cards).hasCount(1);
  }
}'''

JS_PAGES1 = {'pages/LoginPage.js': to_js(LOGIN_TS)}
TS_PAGES1 = {'pages/LoginPage.ts': LOGIN_TS}
JS_PAGES2 = {**JS_PAGES1, 'components/Header.js': to_js(HEADER_TS), 'components/ProductCard.js': to_js(CARD_TS), 'pages/ProductsPage.js': to_js(PRODUCTS_TS)}
TS_PAGES2 = {**TS_PAGES1, 'components/Header.ts': HEADER_TS, 'components/ProductCard.ts': CARD_TS, 'pages/ProductsPage.ts': PRODUCTS_TS}
PY_PAGES1 = {'pages/login_page.py': LOGIN_PY}
PY_PAGES2 = {**PY_PAGES1, 'components/header.py': HEADER_PY, 'components/product_card.py': CARD_PY, 'pages/products_page.py': PRODUCTS_PY}
J = 'src/test/java/com/brainy/'
JAVA_PAGES1 = {J + 'pages/LoginPage.java': LOGIN_JAVA}
JAVA_PAGES2 = {**JAVA_PAGES1, J + 'components/Header.java': HEADER_JAVA, J + 'components/ProductCard.java': CARD_JAVA, J + 'pages/ProductsPage.java': PRODUCTS_JAVA}

CODES = {
    'page': four('Step 1: one page object for the sign in page',
                 java=jv({**JAVA_PAGES1, 'LoginTest.java': LOGIN_TEST_JAVA}, show=[J + 'pages/LoginPage.java', J + 'LoginTest.java']),
                 py=py({**PY_PAGES1, 'test_login.py': LOGIN_TEST_PY}, ini=POM_INI, show=['pages/login_page.py', 'tests/test_login.py', 'pytest.ini']),
                 js=js({**JS_PAGES1, 'login.spec.js': to_js(LOGIN_TEST_TS)}, show=['pages/LoginPage.js', 'tests/login.spec.js']),
                 ts=ts({**TS_PAGES1, 'login.spec.ts': LOGIN_TEST_TS}, show=['pages/LoginPage.ts', 'tests/login.spec.ts']),
                 result='Both tests passed. The tests now say what happens, sign in with these details, and the page object knows how: which fields, which button. If the Sign in button is renamed tomorrow, one line in LoginPage changes and every test keeps working. The check stays in the test, so a reader sees what is being proved. Python needs pythonpath = . in pytest.ini so the tests can import the pages folder.'),
    'component': four('Step 2: components for parts that repeat',
                      java=jv({**JAVA_PAGES2, 'CartTest.java': CART_TEST_JAVA},
                              show=[J + 'components/ProductCard.java', J + 'components/Header.java', J + 'pages/ProductsPage.java', J + 'CartTest.java']),
                      py=py({**PY_PAGES2, 'test_cart.py': CART_TEST_PY}, ini=POM_INI,
                            show=['components/product_card.py', 'components/header.py', 'pages/products_page.py', 'tests/test_cart.py']),
                      js=js({**JS_PAGES2, 'cart.spec.js': to_js(CART_TEST_TS)},
                            show=['components/ProductCard.js', 'components/Header.js', 'pages/ProductsPage.js', 'tests/cart.spec.js']),
                      ts=ts({**TS_PAGES2, 'cart.spec.ts': CART_TEST_TS},
                            show=['components/ProductCard.ts', 'components/Header.ts', 'pages/ProductsPage.ts', 'tests/cart.spec.ts']),
                      result='Both tests passed. The header appears on every page and a product card appears five times, so each is a component that pages reuse. products.card("Desk lamp") returns a card whose locators all start inside that card, so its Add to cart button can never be confused with the button of another product. The test reads almost like the steps a person would write down.'),
    'fixture': four('Step 3: page objects as fixtures',
                    java=jv({**JAVA_PAGES2, 'ShopTest.java': FIX_BASE_JAVA, 'MugTest.java': FIX_TEST_JAVA}, show=[J + 'ShopTest.java', J + 'MugTest.java']),
                    py=py({**PY_PAGES2, 'conftest.py': FIX_CONFTEST, 'test_mug.py': FIX_TEST_PY}, ini=POM_INI, show=['conftest.py', 'tests/test_mug.py']),
                    js=js({**JS_PAGES2, 'fixtures/pages.js': to_js(FIX_TS), 'mug.spec.js': to_js(FIX_TEST_TS)}, show=['fixtures/pages.js', 'tests/mug.spec.js']),
                    ts=ts({**TS_PAGES2, 'fixtures/pages.ts': FIX_TS, 'mug.spec.ts': FIX_TEST_TS}, show=['fixtures/pages.ts', 'tests/mug.spec.ts']),
                    result='All tests passed, and none of them creates a page object or signs in. Playwright Test builds productsPage on demand with test.extend, pytest does the same with fixtures in conftest.py, and JUnit uses a base class with a @BeforeEach method. @UsePlaywright is inherited, so the subclass needs no annotation of its own.'),
}

DG = {
    'layers': {'t': 'The layers of a page object test', 'w': 900, 'h': 220,
               'n': [['test', 20, 78, 140, 64, 'test', {'c': 2, 'sub': 'what to prove', 'i': 'The test says what happens and what must be true. It holds the checks.'}],
                     ['fix', 200, 78, 140, 64, 'fixtures', {'c': 5, 'sub': 'hand out objects', 'i': 'Fixtures or a base class create page objects and sign in, so tests do not repeat it.'}],
                     ['pages', 380, 78, 150, 64, 'page objects', {'c': 1, 'sub': 'one per screen', 'i': 'LoginPage and ProductsPage know the locators and steps of one screen each.'}],
                     ['comp', 570, 78, 150, 64, 'components', {'c': 3, 'sub': 'parts that repeat', 'i': 'Header and ProductCard are reused by many pages.'}],
                     ['loc', 760, 78, 120, 64, 'locators', {'c': 0, 'sub': 'Playwright', 'i': 'In the end every action runs on a Playwright locator, with auto waiting.'}]],
               'e': [['test', 'fix'], ['fix', 'pages'], ['pages', 'comp'], ['comp', 'loc']],
               'st': [[['test'], 'The test describes the behaviour and holds the checks.'],
                      [['fix', 'test>fix'], 'Fixtures hand it ready page objects.'],
                      [['pages', 'fix>pages'], 'Page objects know one screen each.'],
                      [['comp', 'pages>comp'], 'Components cover the parts that appear on many screens.'],
                      [['loc', 'comp>loc'], 'Underneath, Playwright locators do the work.']]},
}

PARTS = [
    part('why', '🤔', 'Why page objects', f'''
<p>Picture 200 tests that all sign in by filling the Email field. One day the label changes to Email address, and 200 tests fail. A <b>page object</b> is a class that holds the locators and steps for one screen. Tests call its methods, so a change to the screen means a change in one file.</p>
<div class="viz" data-viz="flow" data-k="layers"></div>
{table(['Without page objects', 'With page objects'], [
    ['locators copied into every test', 'each locator written once'],
    ['a UI change breaks many files', 'a UI change is fixed in one class'],
    ['tests read as clicks and fills', 'tests read as steps: signIn, addToCart'],
    ['new team members copy old tests', 'new tests reuse a small, named set of methods'],
])}
[[page]]
''', easy=True, kw=['page object model', 'POM', 'page object', 'LoginPage', 'maintenance', 'reuse']),

    part('components', '🧩', 'Components for repeated parts', f'''
<p>Some parts are not a page: the header on every screen, a product card shown five times, a date picker used in three forms. Give each one its own class, a <b>component</b>, and let page objects create them. A component takes a root locator and finds everything inside it.</p>
[[component]]
{tip('Return locators, or small components, and leave the checks in the test. A test that says expect(notebook.button).toBeDisabled() shows what it proves. A page object method called checkNotebook() hides it.', 'tip')}
''', kw=['component', 'ProductCard', 'Header', 'filter has', 'root locator', 'reuse']),

    part('fixtures', '🔧', 'Handing out page objects', f'''
<p>Creating page objects and signing in at the top of every test is repetition again. Move it to the place each runner provides for set up.</p>
[[fixture]]
{table(['', 'Playwright Test', 'pytest', 'JUnit 5'], [
    ['where page objects are created', 'test.extend in a fixtures file', '@pytest.fixture in conftest.py', 'a base class with @BeforeEach'],
    ['how a test gets one', 'by name: { productsPage }', 'by name: products_page', 'a field of the base class'],
    ['only built when used', 'yes', 'yes', 'no, for every test in the class'],
])}
''', kw=['fixtures', 'test.extend', 'conftest', 'base class', 'BeforeEach', 'dependency injection']),

    part('rules', '📏', 'Rules teams follow', f'''
<p>Page objects can grow into a second, harder copy of the app. These rules keep them small and useful.</p>
{table(['Rule', 'Why'], [
    ['one class per screen or component', 'easy to find, small enough to read'],
    ['locators by role, label or test id', 'they survive style changes, as the locators chapter showed'],
    ['methods are user actions: signIn, addToCart', 'tests read like steps, not clicks'],
    ['checks live in tests', 'the test shows what it proves'],
    ['no sleeps and no waits for timeouts', 'Playwright actions and checks already wait'],
    ['no test data inside the class', 'pass it in, so one page object serves many tests'],
    ['a method returns the next page object when the screen changes', 'signIn() can return ProductsPage, so the flow is clear'],
])}
{tip('Large suites sometimes add one more layer of business steps, such as checkout(user, items), built from page objects. Add it when you notice the same five page object calls in many tests, not before.', 'pro')}
''', kw=['best practices', 'rules', 'no assertions in page objects', 'fluent', 'business layer']),
]

INFO = {'title': 'Tests that survive change', 'panels': [
    panel([['e', '📄'], ['t', 'page', {'b': 1}]], 'Page object', 'One class per screen.', 'Locators in one place.'),
    panel([['e', '🧩'], ['t', 'component', {'b': 1}]], 'Component', 'Parts that repeat.', 'Root locator first.'),
    panel([['e', '🔧'], ['t', 'fixture', {'b': 1}]], 'Fixtures', 'Hand them out.', 'No set up in tests.'),
    panel([['e', '✅'], ['t', 'expect', {'b': 1}]], 'Checks', 'Stay in the test.', 'Easy to read.')],
    'remember': 'The test says what, the page object says how. A change to the screen is fixed in one class.'}

REAL = [
    ['🏦', 'A renamed button, one line changed', 'A bank renames Sign in to Log in across its site. Its 600 tests use a LoginPage, so one locator changes and the whole suite is green again in minutes.'],
    ['🛍️', 'One card component, three pages', 'A shop shows the same product card on search, category and wish list pages. One ProductCard component serves all three, and its tests did not change when the card got a new layout.'],
    ['👥', 'New testers write tests on day two', 'A team keeps a small set of page objects with clear method names. New testers write their first tests by combining signIn, search and addToCart, without learning every locator first.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter starts the framework module. You build a page object for the sign in page, components for the header and the product card, and fixtures that hand page objects to every test, in all four languages.',
        'यह अध्याय framework module शुरू करता है। आप sign in page के लिए page object, header और product card के लिए components, और हर test को page objects देने वाले fixtures बनाते हैं, चारों भाषाओं में।',
        'ಈ ಅಧ್ಯಾಯ framework module ಆರಂಭಿಸುತ್ತದೆ. ನೀವು sign in page ಗೆ page object, header ಮತ್ತು product card ಗೆ components, ಪ್ರತಿ test ಗೆ page objects ಕೊಡುವ fixtures ನಾಲ್ಕೂ ಭಾಷೆಗಳಲ್ಲಿ ಮಾಡುತ್ತೀರಿ.',
        'ଏହି ଅଧ୍ୟାୟ framework module ଆରମ୍ଭ କରେ। ଆପଣ sign in page ପାଇଁ page object, header ଓ product card ପାଇଁ components, ଏବଂ ପ୍ରତି test କୁ page objects ଦେଉଥିବା fixtures ଚାରି ଭାଷାରେ ତିଆରି କରନ୍ତି।',
        'يبدأ هذا الفصل وحدة بناء إطار العمل. تبني كائن صفحة لصفحة تسجيل الدخول، ومكونات للترويسة وبطاقة المنتج، ومثبتات تسلّم كائنات الصفحات لكل اختبار، باللغات الأربع.',
        'Dieses Kapitel beginnt das Framework-Modul. Du baust ein Page Object für die Anmeldeseite, Komponenten für die Kopfzeile und die Produktkarte und Fixtures, die jedem Test Page Objects geben, in allen vier Sprachen.'),
    say('why', 'Page objects', 'A page object is a class with the locators and steps of one screen. Tests call its methods, so a change to the screen is fixed in one place, and tests read like steps.',
        'Page object एक class है जिसमें एक screen के locators और steps होते हैं। Tests उसके methods बुलाते हैं, इसलिए screen का बदलाव एक जगह ठीक होता है, और tests steps जैसे पढ़े जाते हैं।',
        'Page object ಎಂದರೆ ಒಂದು screen ನ locators ಮತ್ತು steps ಇರುವ class. Tests ಅದರ methods ಕರೆಯುತ್ತವೆ, ಆದ್ದರಿಂದ screen ಬದಲಾವಣೆ ಒಂದೇ ಕಡೆ ಸರಿಯಾಗುತ್ತದೆ, tests steps ನಂತೆ ಓದುತ್ತವೆ.',
        'Page object ହେଉଛି ଏକ screen ର locators ଓ steps ଥିବା class। Tests ତାର methods ଡାକନ୍ତି, ତେଣୁ screen ର ପରିବର୍ତ୍ତନ ଗୋଟିଏ ଜାଗାରେ ଠିକ ହୁଏ, ଏବଂ tests steps ପରି ପଢାଯାଏ।',
        'كائن الصفحة صنف يحمل محددات شاشة واحدة وخطواتها. تستدعي الاختبارات توابعه، فيُصلح أي تغيير في الشاشة في مكان واحد، وتُقرأ الاختبارات كخطوات.',
        'Ein Page Object ist eine Klasse mit den Locatoren und Schritten eines Bildschirms. Tests rufen seine Methoden auf, also wird eine Änderung am Bildschirm an einer Stelle behoben, und Tests lesen sich wie Schritte.'),
    say('components', 'Components', 'A component is a class for a part that repeats, such as the header or a product card. It starts from a root locator, so it never finds a button that belongs to another card.',
        'Component दोहराए जाने वाले हिस्से की class है, जैसे header या product card। यह root locator से शुरू होता है, इसलिए किसी दूसरे card का button कभी नहीं पकड़ता।',
        'Component ಎಂದರೆ header ಅಥವಾ product card ನಂತೆ ಮತ್ತೆ ಬರುವ ಭಾಗದ class. ಅದು root locator ನಿಂದ ಆರಂಭವಾಗುತ್ತದೆ, ಆದ್ದರಿಂದ ಬೇರೆ card ನ button ಎಂದೂ ಹಿಡಿಯುವುದಿಲ್ಲ.',
        'Component ହେଉଛି header ବା product card ପରି ପୁନରାବୃତ୍ତି ହେଉଥିବା ଅଂଶର class। ଏହା root locator ରୁ ଆରମ୍ଭ ହୁଏ, ତେଣୁ ଅନ୍ୟ card ର button କେବେ ଧରେ ନାହିଁ।',
        'المكوّن صنف لجزء يتكرر، مثل الترويسة أو بطاقة المنتج. يبدأ من محدد جذر، فلا يجد أبدًا زرًا يخص بطاقة أخرى.',
        'Eine Komponente ist eine Klasse für einen Teil, der sich wiederholt, etwa die Kopfzeile oder eine Produktkarte. Sie beginnt bei einem Wurzel-Locator und findet daher nie den Knopf einer anderen Karte.'),
    say('fixtures', 'Fixtures', 'Fixtures create page objects and sign in before the test. Playwright Test uses test.extend, pytest uses conftest.py, and JUnit uses a base class with @BeforeEach.',
        'Fixtures test से पहले page objects बनाते हैं और sign in करते हैं। Playwright Test test.extend, pytest conftest.py, और JUnit @BeforeEach वाली base class इस्तेमाल करता है।',
        'Fixtures test ಮೊದಲು page objects ಮಾಡಿ sign in ಮಾಡುತ್ತವೆ. Playwright Test test.extend, pytest conftest.py, JUnit @BeforeEach ಇರುವ base class ಬಳಸುತ್ತದೆ.',
        'Fixtures test ପୂର୍ବରୁ page objects ତିଆରି କରନ୍ତି ଓ sign in କରନ୍ତି। Playwright Test test.extend, pytest conftest.py, ଏବଂ JUnit @BeforeEach ଥିବା base class ବ୍ୟବହାର କରେ।',
        'تنشئ المثبتات كائنات الصفحات وتسجل الدخول قبل الاختبار. يستخدم Playwright Test الدالة test.extend، ويستخدم pytest الملف conftest.py، ويستخدم JUnit صنفًا أساسيًا مع ‎@BeforeEach.',
        'Fixtures erstellen Page Objects und melden sich vor dem Test an. Playwright Test nutzt test.extend, pytest nutzt conftest.py und JUnit eine Basisklasse mit @BeforeEach.'),
    say('rules', 'Rules', 'Keep one class per screen, use role and label locators, name methods after user actions, keep checks in tests, and pass test data in instead of storing it in the class.',
        'हर screen के लिए एक class रखें, role और label locators इस्तेमाल करें, methods के नाम user actions पर रखें, checks tests में रखें, और test data class में रखने के बजाय भेजें।',
        'ಪ್ರತಿ screen ಗೆ ಒಂದು class ಇಡಿ, role ಮತ್ತು label locators ಬಳಸಿ, methods ಗೆ user actions ಹೆಸರು ಕೊಡಿ, checks tests ನಲ್ಲಿ ಇಡಿ, test data class ನಲ್ಲಿ ಇಡದೆ ಕಳುಹಿಸಿ.',
        'ପ୍ରତି screen ପାଇଁ ଗୋଟିଏ class ରଖନ୍ତୁ, role ଓ label locators ବ୍ୟବହାର କରନ୍ତୁ, methods ର ନାମ user actions ଅନୁସାରେ ଦିଅନ୍ତୁ, checks tests ରେ ରଖନ୍ତୁ, ଏବଂ test data class ରେ ନରଖି ପଠାନ୍ତୁ।',
        'أبقِ صنفًا واحدًا لكل شاشة، واستخدم محددات الدور والتسمية، وسمِّ التوابع بأفعال المستخدم، وأبقِ الفحوص في الاختبارات، ومرّر بيانات الاختبار بدل تخزينها في الصنف.',
        'Halte eine Klasse pro Bildschirm, nutze Rollen- und Label-Locatoren, benenne Methoden nach Nutzeraktionen, lass Prüfungen in den Tests und übergib Testdaten, statt sie in der Klasse zu speichern.'),
    say('practice', 'Playground labs', 'In the labs you work the way a component does: find one product card by its heading, then use only locators inside that card.',
        'Labs में आप component की तरह काम करते हैं: heading से एक product card ढूँढते हैं, फिर केवल उस card के अंदर के locators इस्तेमाल करते हैं।',
        'Labs ನಲ್ಲಿ component ನಂತೆ ಕೆಲಸ ಮಾಡುತ್ತೀರಿ: heading ನಿಂದ ಒಂದು product card ಹುಡುಕಿ, ನಂತರ ಆ card ಒಳಗಿನ locators ಮಾತ್ರ ಬಳಸುತ್ತೀರಿ.',
        'Labs ରେ ଆପଣ component ପରି କାମ କରନ୍ତି: heading ରୁ ଗୋଟିଏ product card ଖୋଜନ୍ତି, ତାପରେ କେବଳ ସେହି card ଭିତରର locators ବ୍ୟବହାର କରନ୍ତି।',
        'في المختبرات تعمل كما يعمل المكوّن: تجد بطاقة منتج واحدة بعنوانها، ثم تستخدم المحددات داخل تلك البطاقة فقط.',
        'In den Labs arbeitest du wie eine Komponente: Du findest eine Produktkarte über ihre Überschrift und nutzt dann nur Locatoren innerhalb dieser Karte.'),
]

QUIZ = [
    quiz(1, 'What is a page object?', ['a browser tab', 'a class with the locators and steps of one screen', 'a test file', 'a fixture'], 1,
         'One class per screen.', 'It keeps the knowledge about one screen in one place.'),
    quiz(1, 'The Sign in button is renamed. With page objects, how many files change?', ['every test', 'one page object', 'the config', 'none'], 1,
         'The locator lives in one place.', 'Only LoginPage changes, and every test keeps working.'),
    quiz(1, 'Where should the checks (expect, assertThat) usually be?', ['in page objects', 'in the tests', 'in the config', 'in fixtures'], 1,
         'A reader should see what is proved.', 'Keeping checks in tests shows what each test proves.'),
    quiz(1, 'What is a component?', ['a test runner', 'a class for a part that repeats, such as a header', 'a browser', 'a report'], 1,
         'Header, product card, date picker.', 'A component covers a part that many pages share.'),
    quiz(2, 'Why does ProductCard start every locator from its root?', ['it is faster', 'so it only finds elements inside its own card', 'Playwright requires it', 'for the report'], 1,
         'There are five Add to cart buttons.', 'Scoping to the root means card("Desk lamp") finds only the lamp\'s button.'),
    quiz(2, 'How does a Playwright Test test receive a page object as a fixture?', ['new LoginPage() in each test', 'test.extend, then by name in the test arguments', 'a global variable', 'an environment variable'], 1,
         'Like page itself.', 'test.extend defines it, and the test asks for it by name.'),
    quiz(2, 'What does Python need so tests in tests/ can import pages/login_page.py?', ['nothing', 'pythonpath = . in pytest.ini, or an installed package', 'a JSON file', 'a symlink'], 1,
         'Python looks up imports on a path.', 'pythonpath = . adds the project folder to the import path.'),
    quiz(2, 'Why can a JUnit subclass of ShopTest skip @UsePlaywright?', ['it is optional everywhere', 'the annotation is inherited', 'JUnit ignores it', 'Maven adds it'], 1,
         'Look at how it is declared.', '@UsePlaywright is marked @Inherited, so subclasses get it.'),
    quiz(2, 'Which method name follows the rules?', ['clickButton2', 'signIn', 'fillField', 'doStuff'], 1,
         'Name the user action.', 'signIn describes what the user does, not how.'),
    quiz(3, 'What should a page object do instead of waitForTimeout(2000)?', ['a longer sleep', 'rely on actions and checks that already wait', 'retry the test', 'add a loop'], 1,
         'Auto waiting.', 'Playwright actions and web-first checks wait for the right state.'),
    quiz(3, 'signIn() takes the user to the products page. What can it return?', ['nothing ever', 'a ProductsPage', 'a string', 'the browser'], 1,
         'The next screen.', 'Returning the next page object makes the flow clear.'),
    quiz(3, 'When is a business layer, such as checkout(user, items), worth adding?', ['always, from day one', 'when the same page object calls repeat in many tests', 'never', 'only in Java'], 1,
         'Add it when you see repetition.', 'A layer earns its place when it removes real repetition.'),
]

CALC = [
    calc(1, '200 tests each sign in with 3 locators. Without page objects, how many locator lines is that?', 600, '200 × 3', ['200 × 3 = 600']),
    calc(1, 'With a LoginPage, how many locator lines for the same 3 locators?', 3, 'written once', ['each locator is written once in LoginPage']),
    calc(2, 'A label change touches 1 locator used by 200 tests. Without page objects, how many lines change?', 200, 'one per test', ['200 tests × 1 line = 200 lines']),
    calc(2, 'A shop has 12 screens and 4 shared parts. One class each: how many classes?', 16, '12 + 4', ['12 page objects + 4 components = 16']),
    calc(2, 'The products page shows 5 cards with 1 button each. How many Add to cart or Out of stock buttons?', 5, '5 × 1', ['5 × 1 = 5']),
    calc(3, 'Signing in takes 2 s. A products_page fixture serves 30 tests. How many seconds of signing in is that?', 60, '30 × 2', ['the fixture runs once per test', '30 × 2 = 60 s']),
    calc(3, 'Saving the sign in with storage state cuts that to one 2 s sign in. How many seconds are saved?', 58, '60 - 2', ['60 - 2 = 58 s']),
    calc(3, 'A page object has 8 methods and 5 are used by fewer than 2 tests. What percent are used by 2 or more?', 37, '3 / 8 × 100, rounded down', ['8 - 5 = 3', '3 / 8 = 0.375', '37.5 %, so 37 rounded down']),
]

LABS = [
    {'id': 'gelpen', 'title': 'Add the gel pen from its own card', 'name': 'Asha adds the gel pen',
     'task': 'Sign in as Asha (<code>asha@shop.example</code>, <code>s3cret</code>). Then find the card whose heading is <b>Gel pen</b>, click the <b>Add to cart</b> button inside that card, and check the cart count is <b>1</b>.',
     'goal': 'The gel pen is in the cart.', 'start': '/login',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('Asha adds the gel pen', async ({ page }) => {
  await page.goto('/login');
  // sign in, find the Gel pen card, add it, check the cart count
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('Asha adds the gel pen', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('s3cret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  const card = page.getByRole('listitem').filter({ has: page.getByRole('heading', { name: 'Gel pen' }) });
  await card.getByRole('button', { name: 'Add to cart' }).click();
  await expect(page.getByTestId('cart-count')).toHaveText('1');
});'''},
     'hint': "Find the card with <code>page.getByRole('listitem').filter({ has: page.getByRole('heading', { name: 'Gel pen' }) })</code>, then look for the button inside it.",
     'why': 'This is what the ProductCard component does inside: a root locator for one card, and every other locator starting from it.',
     'check': [['ctx.loggedIn', 'Asha is signed in'], ['ctx.cartCount === 1', 'One item is in the cart'], ["/filter/i.test(ctx.code)", 'The card is found with filter']]},
    {'id': 'bottleprice', 'title': 'Read a price from one card', 'name': 'the water bottle costs 349 rupees',
     'task': 'On <code>/products</code>, find the card whose heading is <b>Water bottle</b> and check that the price inside it is <b>₹349</b>.',
     'goal': 'The price of the water bottle is checked.', 'start': '/products',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('the water bottle costs 349 rupees', async ({ page }) => {
  await page.goto('/products');
  // find the Water bottle card and check its price
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('the water bottle costs 349 rupees', async ({ page }) => {
  await page.goto('/products');
  const card = page.getByRole('listitem').filter({ has: page.getByRole('heading', { name: 'Water bottle' }) });
  await expect(card.locator('.price')).toHaveText('₹349');
});'''},
     'hint': "Use the same filter as before with the heading <b>Water bottle</b>, then <code>card.locator('.price')</code>.",
     'why': 'Scoping to the card means the check reads the bottle price and never the price of another product.',
     'check': [["/Water bottle/.test(ctx.code)", 'The card is found by its heading'], ["/349/.test(ctx.code)", 'The test checks ₹349']]},
]

T = {
    'slug': 'pw-pom', 'title': 'Page objects and components', 'short': 'Page objects', 'emoji': '🧱', 'module': MODULE, 'minutes': 22,
    'lead': 'Keep tests readable and cheap to change. Put the locators and steps of each screen in a page object, the parts that repeat in components, and hand them to tests through fixtures.',
    'desc': 'The page object model in Java, Python, JavaScript and TypeScript: LoginPage and ProductsPage, Header and ProductCard components scoped with a root locator and filter, page objects as fixtures with test.extend, conftest.py and a JUnit base class, and the rules teams follow.',
    'summary': 'A LoginPage, a ProductsPage built from Header and ProductCard components, and fixtures that hand out signed in page objects, each run for real in four languages.',
    'keywords': ['page object model', 'POM', 'page object', 'component', 'LoginPage', 'ProductCard', 'test.extend', 'conftest', 'base class', 'best practices'],
    'plain': 'A page object is a class that knows one screen of the app. Tests ask it to sign in or add to cart, so when the screen changes, only the class changes.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
