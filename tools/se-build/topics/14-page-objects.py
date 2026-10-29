# Chapter 5.2: page objects and page component objects. Sources: selenium.dev documentation (Page object models,
# including Assertions in Page Objects, Page Component Objects and the Summary rules, and Domain specific language),
# Martin Fowler's PageObject note as cited by the documentation, and real runs of the page objects below against
# web-form.html, submitted-form.html and login.html.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, src, flow

K = Kit()

POM = tri('pom', 'Two page objects, one component and three tests', java=r'''
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import pages.Field;
import pages.ReceivedPage;
import pages.WebFormPage;

public class WebFormTest {
    WebDriver driver;

    @BeforeEach
    void start() { driver = new ChromeDriver(); }

    @Test
    void submittingTextShowsReceived() {
        WebFormPage form = WebFormPage.open(driver);  ## The test talks to pages, not to locators.
        form.field("Text input").fill("Selenium");
        ReceivedPage received = form.submit();  ## submit() moves to another page, so it returns that page object.
        assertEquals("Received!", received.message());  ## The assertion stays in the test.
    }

    @Test
    void onlyOneFieldIsDisabled() {
        List<Field> fields = WebFormPage.open(driver).fields();
        assertEquals(11, fields.size());  ## Eleven labelled controls on this page.
        assertEquals(List.of("Disabled input"), fields.stream().filter(f -> !f.isEnabled()).map(Field::name).toList());
    }

    @Test
    void refusesTheWrongPage() {
        driver.get("https://www.selenium.dev/selenium/web/login.html");
        assertThrows(IllegalStateException.class, () -> new WebFormPage(driver));  ## The constructor checks the page and fails loudly.
    }

    @AfterEach
    void stop() { driver.quit(); }
}
''', py=r'''
import pytest
from selenium import webdriver

from pages.web_form_page import WebFormPage


@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


def test_submitting_text_shows_received(driver):
    form = WebFormPage.open(driver)  ## The test talks to pages, not to locators.
    form.field("Text input").fill("Selenium")
    received = form.submit()  ## submit() moves to another page, so it returns that page object.
    assert received.message() == "Received!"  ## The assertion stays in the test.


def test_only_one_field_is_disabled(driver):
    fields = WebFormPage.open(driver).fields()
    assert len(fields) == 11  ## Eleven labelled controls on this page.
    assert [f.name() for f in fields if not f.is_enabled()] == ["Disabled input"]


def test_refuses_the_wrong_page(driver):
    driver.get("https://www.selenium.dev/selenium/web/login.html")
    with pytest.raises(ValueError):  ## The constructor checks the page and fails loudly.
        WebFormPage(driver)
''', js=r'''
const { Builder, Browser } = require('selenium-webdriver');
const assert = require('assert');
const { WebFormPage } = require('./pages/web_form_page');

describe('Web form with page objects', function () {
  let driver;
  beforeEach(async function () { driver = await new Builder().forBrowser(Browser.CHROME).build(); });

  it('shows Received! after submitting text', async function () {
    const form = await WebFormPage.open(driver);  ## The test talks to pages, not to locators.
    await (await form.field('Text input')).fill('Selenium');
    const received = await form.submit();  ## submit() moves to another page, so it returns that page object.
    assert.strictEqual(await received.message(), 'Received!');  ## The assertion stays in the test.
  });

  it('has only one disabled field', async function () {
    const fields = await (await WebFormPage.open(driver)).fields();
    assert.strictEqual(fields.length, 11);  ## Eleven labelled controls on this page.
    const disabled = [];
    for (const f of fields) if (!(await f.isEnabled())) disabled.push(await f.name());
    assert.deepStrictEqual(disabled, ['Disabled input']);
  });

  it('refuses the wrong page', async function () {
    await driver.get('https://www.selenium.dev/selenium/web/login.html');
    await assert.rejects(WebFormPage.at(driver), /This is not the web form/);  ## The check fails loudly.
  });

  afterEach(async function () { await driver.quit(); });
});
''', mode={'java': 'junit', 'py': 'pytest', 'js': 'mocha'}, extra={
    'java': {
        'pages/WebFormPage.java': r'''
package pages;

import java.util.List;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;

public class WebFormPage {
    static final String URL = "https://www.selenium.dev/selenium/web/web-form.html";
    private final By fieldsBy = By.cssSelector("label.form-label");  ## Locators live here and nowhere else.
    private final By submitBy = By.cssSelector("button[type=submit]");
    private final WebDriver driver;

    public WebFormPage(WebDriver driver) {
        this.driver = driver;
        if (!"Web form".equals(driver.getTitle())) {  ## The one check a page object should make: am I on the right page?
            throw new IllegalStateException("This is not the web form, it is: " + driver.getTitle());
        }
    }

    public static WebFormPage open(WebDriver driver) {
        driver.get(URL);
        return new WebFormPage(driver);
    }

    public List<Field> fields() {
        return driver.findElements(fieldsBy).stream().map(Field::new).toList();  ## Wrap every label element in a Field component.
    }

    public Field field(String name) {
        return fields().stream().filter(f -> f.name().equals(name)).findFirst()
            .orElseThrow(() -> new IllegalArgumentException("No field called " + name));
    }

    public ReceivedPage submit() {
        driver.findElement(submitBy).click();
        return new ReceivedPage(driver);
    }
}
''',
        'pages/Field.java': r'''
package pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;

public class Field {  ## A page component: one label and the control inside it.
    private final WebElement root;

    public Field(WebElement root) { this.root = root; }

    public String name() { return root.getText().split("\n")[0].trim(); }  ## The first line of the label is its name.

    private WebElement control() { return root.findElement(By.cssSelector("input, textarea, select")); }  ## Search inside this component only.

    public boolean isEnabled() { return control().isEnabled(); }

    public Field fill(String text) {
        control().clear();
        control().sendKeys(text);
        return this;  ## Returning itself allows field(...).fill(...).fill(...).
    }
}
''',
        'pages/ReceivedPage.java': r'''
package pages;

import java.time.Duration;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class ReceivedPage {
    private final WebDriver driver;

    public ReceivedPage(WebDriver driver) {
        this.driver = driver;
        new WebDriverWait(driver, Duration.ofSeconds(3)).until(ExpectedConditions.titleIs("Web form - target page"));  ## The page arrives after a navigation, so wait for it instead of checking once.
    }

    public String message() { return driver.findElement(By.id("message")).getText(); }
}
'''},
    'py': {
        'pages/web_form_page.py': r'''
from selenium.webdriver.common.by import By

from pages.field import Field
from pages.received_page import ReceivedPage


class WebFormPage:
    URL = "https://www.selenium.dev/selenium/web/web-form.html"
    FIELDS = (By.CSS_SELECTOR, "label.form-label")  ## Locators live here and nowhere else.
    SUBMIT = (By.CSS_SELECTOR, "button[type=submit]")

    def __init__(self, driver):
        self.driver = driver
        if driver.title != "Web form":  ## The one check a page object should make: am I on the right page?
            raise ValueError("This is not the web form, it is: " + driver.title)

    @classmethod
    def open(cls, driver):
        driver.get(cls.URL)
        return cls(driver)

    def fields(self):
        return [Field(e) for e in self.driver.find_elements(*self.FIELDS)]  ## Wrap every label element in a Field component.

    def field(self, name):
        for f in self.fields():
            if f.name() == name:
                return f
        raise LookupError("No field called " + name)

    def submit(self):
        self.driver.find_element(*self.SUBMIT).click()
        return ReceivedPage(self.driver)
''',
        'pages/field.py': r'''
from selenium.webdriver.common.by import By


class Field:  ## A page component: one label and the control inside it.
    def __init__(self, root):
        self.root = root

    def name(self):
        return self.root.text.split("\n")[0].strip()  ## The first line of the label is its name.

    def control(self):
        return self.root.find_element(By.CSS_SELECTOR, "input, textarea, select")  ## Search inside this component only.

    def is_enabled(self):
        return self.control().is_enabled()

    def fill(self, text):
        self.control().clear()
        self.control().send_keys(text)
        return self  ## Returning itself allows field(...).fill(...).fill(...).
''',
        'pages/received_page.py': r'''
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class ReceivedPage:
    def __init__(self, driver):
        self.driver = driver
        WebDriverWait(driver, 3).until(EC.title_is("Web form - target page"))  ## The page arrives after a navigation, so wait for it instead of checking once.

    def message(self):
        return self.driver.find_element(By.ID, "message").text
'''},
    'js': {
        'pages/web_form_page.js': r'''
const { By } = require('selenium-webdriver');
const { Field } = require('./field');
const { ReceivedPage } = require('./received_page');

const URL = 'https://www.selenium.dev/selenium/web/web-form.html';
const FIELDS = By.css('label.form-label');  ## Locators live here and nowhere else.
const SUBMIT = By.css('button[type=submit]');

class WebFormPage {
  constructor(driver) { this.driver = driver; }

  static async at(driver) {  ## A constructor cannot await, so an async factory does the page check.
    const title = await driver.getTitle();
    if (title !== 'Web form') throw new Error('This is not the web form, it is: ' + title);
    return new WebFormPage(driver);
  }

  static async open(driver) {
    await driver.get(URL);
    return WebFormPage.at(driver);
  }

  async fields() {
    return (await this.driver.findElements(FIELDS)).map(e => new Field(e));  ## Wrap every label element in a Field component.
  }

  async field(name) {
    for (const f of await this.fields()) if ((await f.name()) === name) return f;
    throw new Error('No field called ' + name);
  }

  async submit() {
    await this.driver.findElement(SUBMIT).click();
    return ReceivedPage.at(this.driver);
  }
}

module.exports = { WebFormPage };
''',
        'pages/field.js': r'''
const { By } = require('selenium-webdriver');

class Field {  ## A page component: one label and the control inside it.
  constructor(root) { this.root = root; }

  async name() { return (await this.root.getText()).split('\n')[0].trim(); }  ## The first line of the label is its name.

  control() { return this.root.findElement(By.css('input, textarea, select')); }  ## Search inside this component only.

  async isEnabled() { return (await this.control()).isEnabled(); }

  async fill(text) {
    const c = await this.control();
    await c.clear();
    await c.sendKeys(text);
    return this;
  }
}

module.exports = { Field };
''',
        'pages/received_page.js': r'''
const { By, until } = require('selenium-webdriver');

class ReceivedPage {
  constructor(driver) { this.driver = driver; }

  static async at(driver) {
    await driver.wait(until.titleIs('Web form - target page'), 3000);  ## The page arrives after a navigation, so wait for it instead of checking once.
    return new ReceivedPage(driver);
  }

  async message() { return this.driver.findElement(By.id('message')).getText(); }
}

module.exports = { ReceivedPage };
'''}})

K.lesson('why', 'Why page objects', f'''
<p>A test that finds elements directly works fine on its own. The trouble starts at test number forty. The same <code>By.cssSelector("button[type=submit]")</code> is now copied into forty tests, and when the developers rename the button, forty tests break and forty places need the same fix.</p>
<p>The documentation describes a <b>page object</b> as an object oriented class that serves as an interface to a page of the application under test. Tests call its methods whenever they need the page. When the page changes, only the page object changes. The tests stay the same.</p>
{viz('se-pom')}
{table(['Without page objects', 'With page objects'], [
    ['Locators are copied into every test that uses the page', 'Each locator is written once, inside the page object'],
    ['A test reads as a list of clicks and CSS selectors', 'A test reads as what the user does: open the form, fill a field, submit'],
    ['A UI change breaks many tests in many files', 'A UI change is fixed in one class'],
    ['Waiting and page checks are repeated', 'The page object waits for its page once, in its constructor']])}
{scene('the renamed button', '<p>A shop has 60 checkout tests. The design team changes the Pay button from an id to a data attribute. Without page objects the change touches 60 files and two of them are missed, so the nightly run is red for a day. With a CheckoutPage class, one line changes in one file and all 60 tests pass again on the next run.</p>')}
''', kw=['page object', 'page object model', 'pom', 'design pattern', 'maintenance', 'duplication', 'locators in one place'])

K.lesson('pom', 'Write page objects and components', f'''
<p>Below are two page objects, <code>WebFormPage</code> and <code>ReceivedPage</code>, one <b>page component</b>, <code>Field</code>, and three tests. Open each file in the example and walk it line by line. The tests never mention a locator.</p>
{POM}
<p>Read the three tests against the rules from the documentation. The first test only calls methods that describe what a user does, and the assertion is in the test, not in the page object. The second test uses <code>Field</code> objects, each built around one label element, which is what the documentation calls a page component object. The third test opens the login page and asks for a web form page object, and the constructor refuses with an error.</p>
{table(['Rule from the documentation', 'Where it shows in the example'], [
    ['The public methods represent the services the page offers', '<code>field</code>, <code>fields</code>, <code>submit</code>, <code>message</code>'],
    ['Try not to expose the internals of the page', 'Locators are private. <code>Field.control()</code> is private in Java'],
    ['Generally do not make assertions', 'Every <code>assert</code> is in the test file'],
    ['The one allowed check: the right page is loaded', 'The constructors check the title, or wait for it after a navigation'],
    ['Methods return other page objects, components or themselves', '<code>submit()</code> returns ReceivedPage, <code>fill()</code> returns the Field'],
    ['A page object need not represent an entire page', '<code>Field</code> represents one labelled control']])}
{note('ReceivedPage waits for its title, while WebFormPage checks the title once. The web form is opened with get(), which returns after the page loads. The received page appears after a click, and chapter 3.3 showed that the next command can run before the new page is there.', 'tip')}
''', kw=['page object', 'page component', 'component object', 'constructor check', 'return page object', 'fluent', 'no assertions in page objects', 'encapsulation'])

K.lesson('design', 'Design choices and the limits of page objects', f'''
<p>Page objects are a pattern, not a library, so a team still makes choices. These are the ones that come up most often.</p>
{table(['Choice', 'What the documentation or practice suggests'], [
    ['Same action, different result', 'Write two methods, for example loginAsValidUser and loginExpectingError, each returning the page that really follows'],
    ['A part that appears on many pages', 'A component object such as a header, a menu or a product card, used inside page objects'],
    ['Where waits go', 'Inside the page object, so tests do not repeat them'],
    ['Base class', 'Shared code such as the driver field and a wait helper. Keep it small'],
    ['PageFactory in Java', 'An older helper that fills fields annotated with @FindBy. Plain By fields, as in the example, work in every language']])}
<p>A layer above page objects is a <b>domain specific language</b>: methods such as <code>shop.buy("backpack")</code> that hide whole user journeys. The documentation describes this as giving tests a language that business people can read. It sits on top of page objects and does not replace them.</p>
{ladder(
    '<p>A page object is a class for one page. Tests call its methods, so a change to the page is fixed in one place.</p>',
    '<p>Locators and waits live in the page object, assertions live in the test. Methods that move to another page return that page object. Repeated parts become component objects.</p>',
    '<p>The constructor checks that the right page is loaded, or waits for it after a navigation. Different results for the same action are modelled as different methods, as the documentation summary says.</p>',
    '<p>On top of page objects, a domain layer gives business level steps. Components scope their searches to a root element, which also makes them reusable in lists, tables and repeated cards.</p>')}
''', kw=['page factory', 'findby', 'base page', 'domain specific language', 'component', 'design', 'loadable component'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What is the main benefit of page objects?', ['Faster browsers', 'A UI change is fixed in one place', 'No need for waits', 'Shorter test names'], 1,
       'Maintenance.', 'Locators and page code live in one class, so a change is fixed once.')
K.quiz('e', 'Where should assertions go?', ['In the page object', 'In the test', 'In the driver', 'In the locator'], 1,
       'The documentation is clear.', 'Page objects should never make verifications. Assertions belong to the test.')
K.quiz('e', 'What should submit() return when it moves the browser to a new page?', ['Nothing', 'The page object of the new page', 'A boolean', 'The WebDriver'], 1,
       'Return the next page.', 'Methods that navigate return the page object of where you land.')
K.quiz('m', 'Which single check may a page object make?', ['That a test passed', 'That the right page is loaded', 'That the database is up', 'That the button is green'], 1,
       'In the constructor.', 'The documentation allows one verification: the page, and possibly critical elements, loaded correctly.')
K.quiz('m', 'What is a page component object?', ['A whole page', 'An object for a repeated part of a page, such as a card or a field', 'A Grid node', 'A JUnit extension'], 1,
       'Smaller than a page.', 'A component object represents a discrete chunk of a page and can be used inside page objects.')
K.quiz('m', 'Why does the Field component search with root.findElement and not driver.findElement?', ['It is faster to type', 'So it only looks inside its own label', 'driver.findElement does not work', 'To avoid waits'], 1,
       'Scope.', 'Searching from the root keeps the component to its own part of the page, chapter 3.2 style.')
K.quiz('m', 'A login can succeed or show an error. How does the documentation suggest modelling that?', ['One method returning Object', 'Two methods, one per result', 'An if in the test', 'A global flag'], 1,
       'Different results, different methods.', 'Different results for the same action are modelled as different methods.')
K.quiz('h', 'Why does ReceivedPage wait for its title instead of checking it once?', ['Titles are slow', 'It appears after a click, and the next command can run before it loads', 'Waits are required in constructors', 'To avoid a stale element'], 1,
       'After a navigation.', 'The page appears after a click, so a single check could run too early.')
K.quiz('h', 'The JavaScript page object uses a static async at() method. Why not the constructor?', ['Style only', 'A constructor cannot await', 'Mocha needs it', 'To save memory'], 1,
       'await in a constructor.', 'Checking the title needs an await, which a JavaScript constructor cannot do.')
K.quiz('x', '60 tests each use the submit locator twice. Without page objects, how many places change when it is renamed?', ['1', '60', '120', '2'], 2,
       'Count every copy.', '60 × 2 = 120 copies. With a page object it is 1.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A locator is copied into 25 tests. With a page object, how many copies are there?', '1', 'One home.',
       ['Without: 25 copies.', 'With a page object the tests call a method.', eq('1 copy, inside the page object')], check=1)
K.calc('e', 'The web form page in this chapter has how many labelled fields, and how many of them are disabled? Give the number of enabled fields.', '10', 'Use the real run.',
       ['The test found 11 fields.', 'One is disabled.', eq('11 − 1 = 10 enabled fields')], check=10)
K.calc('m', 'Fixing one copy of a locator takes 2 minutes. A rename touches 60 tests with 2 copies each. How many minutes does the fix take without page objects?', '240', 'Count copies.',
       ['60 × 2 = 120 copies.', 'Each takes 2 minutes.', eq('120 × 2 = 240 minutes, 4 hours')], check=240, unit='min')
K.calc('m', 'With a page object the same rename takes one fix of 2 minutes plus one run of 15 minutes to check. How many minutes are saved compared with 240?', '223', 'Subtract.',
       ['With a page object: 2 + 15 = 17 minutes.', 'Without: 240 minutes.', eq('240 − 17 = 223 minutes saved')], check=223, unit='min')
K.calc('h', 'A shop page shows 6 product cards. A test reads the price of each through a component, with 1 find for the card list and 1 find per card for the price. How many find commands?', '7', 'One list plus one per card.',
       ['1 findElements for the cards.', '6 findElement calls inside the cards.', eq('1 + 6 = 7 commands')], check=7)
K.calc('x', 'A suite has 8 page objects with 6 locators each and 3 components with 2 locators each. A redesign changes 25 % of all locators. How many locators change?', '13.5', 'Count, then take a quarter.',
       ['Page objects: 8 × 6 = 48.', 'Components: 3 × 2 = 6, so 54 in total.', eq('0.25 × 54 = 13.5, so about 14 locators')], check=13.5)

# ---------------------------------------------------------------- assignments
K.assign('fieldname', 'e', 'Read a field name from label text',
         '<p>Write <code>field_name(label_text)</code>. A label wraps its control, so its text can have several lines, for example a select lists its options. Return the first line without spaces at either end.</p>',
         '''
def field_name(label_text):
    # your code here
    pass
''', [('field_name("Text input")', 'Text input'), ('field_name("Dropdown (select)\\nOpen this select menu\\nOne")', 'Dropdown (select)'), ('field_name("  Password  ")', 'Password')],
         '''
def field_name(label_text):
    return label_text.split("\\n")[0].strip()
''', 'split on the line break, then strip.', '<p>This is exactly what the Field component does with the label text in all three languages.</p>')
K.assign('pagecheck', 'm', 'A page object check',
         '<p>Write a class <code>Page</code> with a constructor <code>Page(title, expected)</code>. If <code>title</code> differs from <code>expected</code>, raise <code>ValueError</code> with the text "Expected X but was Y". Otherwise store the title. Then write <code>open_page(title, expected)</code> that returns "ok" when a Page can be built and the error text when it cannot.</p>',
         '''
class Page:
    def __init__(self, title, expected):
        # your code here
        pass


def open_page(title, expected):
    # your code here
    pass
''', [('open_page("Web form", "Web form")', 'ok'), ('open_page("Login", "Web form")', 'Expected Web form but was Login')],
         '''
class Page:
    def __init__(self, title, expected):
        if title != expected:
            raise ValueError("Expected " + expected + " but was " + title)
        self.title = title


def open_page(title, expected):
    try:
        Page(title, expected)
        return "ok"
    except ValueError as e:
        return str(e)
''', 'raise in the constructor, catch in open_page.', '<p>A page object that refuses the wrong page turns a confusing failure several steps later into a clear one at the start.</p>')

K.must('Page object', 'A class that is the interface to one page. Tests call its methods, so a change to the page is fixed in one place.')
K.must('No assertions inside', 'Assertions belong to the test. The only check in a page object is that the right page is loaded.')
K.must('Return the next page', 'A method that moves to another page returns that page object. A method that stays may return itself.')
K.must('Components', 'A page component object models a repeated part, such as a field or a product card, and searches only inside its root element.')
K.must('Waits inside', 'Put waits in the page object, for example a constructor that waits for its title after a navigation.')

T = K.topic(
    slug='page-objects', topic='page-objects',
    step=(5, 'Build a test suite', 'se-suite', 'Test frameworks, page objects, good practices and the errors you will meet.', 'Intermediate'),
    title='Page objects and page components', short='Page objects', badge='5.2', minutes=50, added='2026-10-29',
    lead='Keep locators, waits and page checks in one class per page, so tests read like user steps and a UI change is fixed in one place.',
    desc='Why page objects, with an animation of a locator change with and without them, two page objects and a page component in Java, Python and JavaScript run as real JUnit 5, pytest and Mocha tests, the rules from the Selenium documentation, and design choices such as two methods for two results, base classes, PageFactory and a domain layer.',
    summary='Page objects, page component objects and the rules for writing them.',
    keywords=['page object', 'page object model', 'pom', 'page component', 'design pattern', 'maintainability', 'page factory'],
    recap='<p>A page object is the interface to one page: locators, waits and the page check live inside, assertions live in the test. Methods that navigate return the next page object. Component objects model repeated parts and search only inside their root. When the page changes, one class changes.</p>')
