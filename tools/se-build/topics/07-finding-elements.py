# Chapter 3.2: finding elements. Sources: selenium.dev documentation (Finding web elements: first matching
# element, subset of the DOM, Shadow DOM, optimized locator, all matching elements, find elements from element,
# active element), the W3C WebDriver specification (Find Element, Find Elements, Find Element From Element, Get
# Element Shadow Root, Find Element From Shadow Root, Get Active Element) and real runs against Chrome 153.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, src, flow

K = Kit()

MANY = tri('findall', 'One element, all elements, and what happens when nothing matches', java=r'''
import java.util.List;
import org.openqa.selenium.By;
import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

public class FindAll {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/locators_tests/locators.html");
        List<WebElement> inputs = driver.findElements(By.tagName("input"));  ## Plural: a List of every input, in page order.
        System.out.println("inputs: " + inputs.size());
        for (WebElement e : inputs) {  ## Walk the list like any Java list.
            System.out.println("  " + e.getAttribute("type") + " " + e.getAttribute("name"));
        }
        List<WebElement> none = driver.findElements(By.id("email"));  ## No match: an empty list, never an error.
        System.out.println("email boxes: " + none.size());
        try {
            driver.findElement(By.id("email"));  ## Singular with no match: an exception.
        } catch (NoSuchElementException e) {
            System.out.println("findElement: NoSuchElementException");
        }
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/locators_tests/locators.html")
inputs = driver.find_elements(By.TAG_NAME, "input")  ## Plural: a list of every input, in page order.
print("inputs:", len(inputs))
for e in inputs:  ## Walk the list like any Python list.
    print(" ", e.get_attribute("type"), e.get_attribute("name"))
none = driver.find_elements(By.ID, "email")  ## No match: an empty list, never an error.
print("email boxes:", len(none))
try:
    driver.find_element(By.ID, "email")  ## Singular with no match: an exception.
except NoSuchElementException:
    print("find_element: NoSuchElementException")
driver.quit()
''', js=r'''
const { Builder, Browser, By, error } = require('selenium-webdriver');

(async function findAll() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/locators_tests/locators.html');
  const inputs = await driver.findElements(By.tagName('input'));  ## Plural: an array of every input, in page order.
  console.log('inputs: ' + inputs.length);
  for (const e of inputs) {  ## for...of with await inside, so the questions are asked one by one.
    console.log('  ' + await e.getAttribute('type') + ' ' + await e.getAttribute('name'));
  }
  const none = await driver.findElements(By.id('email'));  ## No match: an empty array, never an error.
  console.log('email boxes: ' + none.length);
  try {
    await driver.findElement(By.id('email'));  ## Singular with no match: the promise rejects.
  } catch (e) {
    if (!(e instanceof error.NoSuchElementError)) throw e;
    console.log('findElement: NoSuchElementError');
  }
  await driver.quit();
})();
''', expect='email boxes: 0')

SCOPE = tri('scope', 'Search inside one element, and the XPath trap', java=r'''
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

public class Scope {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/locators_tests/locators.html");
        WebElement form = driver.findElement(By.tagName("form"));  ## First find the parent element.
        System.out.println("inputs in form: " + form.findElements(By.cssSelector("input")).size());  ## Called on the form, CSS only looks inside it.
        System.out.println("links via //a: " + form.findElements(By.xpath("//a")).size());  ## The trap: // starts at the top of the document, so the link outside the form is found.
        System.out.println("links via .//a: " + form.findElements(By.xpath(".//a")).size());  ## The dot means start here. Now nothing outside the form counts.
        WebElement last = form.findElement(By.id("lname"));  ## Two commands: find the form, then find inside it.
        WebElement same = driver.findElement(By.cssSelector("form #lname"));  ## The optimised version: one CSS selector, one command.
        System.out.println("same element: " + last.equals(same));  ## Both references point at the same element.
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/locators_tests/locators.html")
form = driver.find_element(By.TAG_NAME, "form")  ## First find the parent element.
print("inputs in form:", len(form.find_elements(By.CSS_SELECTOR, "input")))  ## Called on the form, CSS only looks inside it.
print("links via //a:", len(form.find_elements(By.XPATH, "//a")))  ## The trap: // starts at the top of the document, so the link outside the form is found.
print("links via .//a:", len(form.find_elements(By.XPATH, ".//a")))  ## The dot means start here. Now nothing outside the form counts.
last = form.find_element(By.ID, "lname")  ## Two commands: find the form, then find inside it.
same = driver.find_element(By.CSS_SELECTOR, "form #lname")  ## The optimised version: one CSS selector, one command.
print("same element:", last == same)  ## Both references point at the same element.
driver.quit()
''', js=r'''
const { Builder, Browser, By, WebElement } = require('selenium-webdriver');

(async function scope() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/locators_tests/locators.html');
  const form = await driver.findElement(By.css('form'));  ## First find the parent element.
  console.log('inputs in form: ' + (await form.findElements(By.css('input'))).length);  ## Called on the form, CSS only looks inside it.
  console.log('links via //a: ' + (await form.findElements(By.xpath('//a'))).length);  ## The trap: // starts at the top of the document, so the link outside the form is found.
  console.log('links via .//a: ' + (await form.findElements(By.xpath('.//a'))).length);  ## The dot means start here. Now nothing outside the form counts.
  const last = await form.findElement(By.id('lname'));  ## Two commands: find the form, then find inside it.
  const same = await driver.findElement(By.css('form #lname'));  ## The optimised version: one CSS selector, one command.
  console.log('same element: ' + await WebElement.equals(last, same));  ## Both references point at the same element.
  await driver.quit();
})();
''', expect='links via .//a: 0')

SHADOW = tri('shadow', 'Reach into a shadow root', java=r'''
import org.openqa.selenium.By;
import org.openqa.selenium.InvalidArgumentException;
import org.openqa.selenium.SearchContext;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

public class Shadow {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/shadowRootPage.html");
        String box = "input[type='checkbox']";
        System.out.println("from the page: " + driver.findElements(By.cssSelector(box)).size());  ## The checkbox lives in a shadow tree, so a normal search finds nothing.
        WebElement host = driver.findElement(By.cssSelector("custom-checkbox-element"));  ## The shadow host: the element the hidden tree is attached to.
        SearchContext shadowRoot = host.getShadowRoot();  ## Get Element Shadow Root. A SearchContext, like the driver and an element.
        WebElement checkbox = shadowRoot.findElement(By.cssSelector(box));  ## Search inside the shadow tree.
        System.out.println("from the shadow root: " + checkbox.getAttribute("type"));
        try {
            shadowRoot.findElement(By.xpath(".//input"));  ## XPath inside a shadow root.
        } catch (InvalidArgumentException e) {
            System.out.println("xpath in shadow root: " + e.getMessage().split("\n")[0]);  ## Chrome refuses it.
        }
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/shadowRootPage.html")
box = "input[type='checkbox']"
print("from the page:", len(driver.find_elements(By.CSS_SELECTOR, box)))  ## The checkbox lives in a shadow tree, so a normal search finds nothing.
host = driver.find_element(By.CSS_SELECTOR, "custom-checkbox-element")  ## The shadow host: the element the hidden tree is attached to.
shadow_root = host.shadow_root  ## Get Element Shadow Root. A ShadowRoot object with find_element and find_elements.
checkbox = shadow_root.find_element(By.CSS_SELECTOR, box)  ## Search inside the shadow tree.
print("from the shadow root:", checkbox.get_attribute("type"))
try:
    shadow_root.find_element(By.XPATH, ".//input")  ## XPath inside a shadow root.
except InvalidArgumentException as e:
    print("xpath in shadow root:", e.msg.split("\n")[0])  ## Chrome refuses it.
driver.quit()
''', js=r'''
const { Builder, Browser, By, error } = require('selenium-webdriver');

(async function shadow() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/shadowRootPage.html');
  const box = "input[type='checkbox']";
  console.log('from the page: ' + (await driver.findElements(By.css(box))).length);  ## The checkbox lives in a shadow tree, so a normal search finds nothing.
  const host = await driver.findElement(By.css('custom-checkbox-element'));  ## The shadow host: the element the hidden tree is attached to.
  const shadowRoot = await host.getShadowRoot();  ## Get Element Shadow Root.
  const checkbox = await shadowRoot.findElement(By.css(box));  ## Search inside the shadow tree.
  console.log('from the shadow root: ' + await checkbox.getAttribute('type'));
  try {
    await shadowRoot.findElement(By.xpath('.//input'));  ## XPath inside a shadow root.
  } catch (e) {
    if (!(e instanceof error.InvalidArgumentError)) throw e;
    console.log('xpath in shadow root: ' + e.message.split('\n')[0]);  ## Chrome refuses it.
  }
  await driver.quit();
})();
''', expect='from the shadow root: checkbox')

ACTIVE = tri('active', 'Which element has the focus?', java=r'''
import org.openqa.selenium.By;
import org.openqa.selenium.Keys;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class Active {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/web-form.html");
        System.out.println("at start: " + driver.switchTo().activeElement().getTagName());  ## Nothing is focused yet, so the active element is the body.
        driver.findElement(By.name("my-text")).click();  ## Clicking a text box gives it the focus.
        System.out.println("after click: " + driver.switchTo().activeElement().getAttribute("name"));
        driver.switchTo().activeElement().sendKeys(Keys.TAB);  ## Press Tab on whatever has the focus, as a user would.
        System.out.println("after Tab: " + driver.switchTo().activeElement().getAttribute("name"));  ## The focus moved to the next field.
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/web-form.html")
print("at start:", driver.switch_to.active_element.tag_name)  ## Nothing is focused yet, so the active element is the body.
driver.find_element(By.NAME, "my-text").click()  ## Clicking a text box gives it the focus.
print("after click:", driver.switch_to.active_element.get_attribute("name"))
driver.switch_to.active_element.send_keys(Keys.TAB)  ## Press Tab on whatever has the focus, as a user would.
print("after Tab:", driver.switch_to.active_element.get_attribute("name"))  ## The focus moved to the next field.
driver.quit()
''', js=r'''
const { Builder, Browser, By, Key } = require('selenium-webdriver');

(async function active() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/web-form.html');
  console.log('at start: ' + await (await driver.switchTo().activeElement()).getTagName());  ## Nothing is focused yet, so the active element is the body.
  await driver.findElement(By.name('my-text')).click();  ## Clicking a text box gives it the focus.
  console.log('after click: ' + await (await driver.switchTo().activeElement()).getAttribute('name'));
  await (await driver.switchTo().activeElement()).sendKeys(Key.TAB);  ## Press Tab on whatever has the focus, as a user would.
  console.log('after Tab: ' + await (await driver.switchTo().activeElement()).getAttribute('name'));  ## The focus moved to the next field.
  await driver.quit();
})();
''', expect='after click: my-text')

K.lesson('oneormany', 'Find one or find many', f'''
<p>Every Selenium binding has two find methods, and their only difference is how many results they return and what they do when nothing matches.</p>
{table(['', 'find element (singular)', 'find elements (plural)'], [
    ['Returns', 'One element: the first match in page order', 'A list of every match, in page order'],
    ['No match', 'Raises no such element', 'Returns an empty list'],
    ['W3C command', 'Find Element', 'Find Elements'],
    ['Use it for', 'An element that must be there', 'Counting, looping, or checking that something is absent']])}
{MANY}
{scene('checking the search results', '<p>A test types "laptop" into a shop search and must check that exactly 20 results appear and that none says "Out of stock". It uses find elements on the result cards, checks the list has 20 entries, then loops over them reading each status. To check that an error banner is gone, it asks find elements for the banner and expects an empty list, which never raises.</p>')}
{note('find elements never waits for the first element to appear unless an implicit wait is set, and then it returns as soon as at least one matches. An empty list can mean the page is not ready yet. Chapter 4.1 shows how to wait properly.', 'warn')}
''', kw=['find element', 'find elements', 'first match', 'empty list', 'NoSuchElementException', 'list', 'loop', 'count elements'])

K.lesson('scope', 'Search inside an element', f'''
<p>Instead of searching the whole page, you can first find a container and then search inside it. The documentation calls this evaluating a subset of the DOM. In Java and C# the driver, an element and a shadow root all implement the same <code>SearchContext</code> interface, which is why they share the find methods.</p>
{SCOPE}
{viz('se-scope')}
<p>The second line of output is the most common XPath mistake in Selenium. An XPath that begins with <code>//</code> always starts at the top of the document, even when you call it on an element. Start with <code>.//</code> to search below the element. CSS selectors called on an element never have this problem.</p>
<p>The documentation also points out that a nested search costs two commands. When a single CSS selector such as <code>form #lname</code> can say the same thing, it is one command and slightly faster.</p>
{note('Searching inside a container is still very useful when the page repeats a pattern: the Delete button inside the third row of a table, or the price inside one product card. Find the row or card first, then the button inside it.', 'tip')}
''', kw=['search context', 'find from element', 'scope', 'subset of the DOM', 'xpath dot', 'relative xpath', 'optimized locator', 'nested find'])

K.lesson('shadow', 'The shadow DOM', f'''
<p>Modern components often hide their insides in a <b>shadow DOM</b>: a separate tree attached to an element, called the shadow host. The page can see the host but a normal search does not go inside it. That keeps the component styles and ids apart from the rest of the page, and it also hides them from Selenium.</p>
{flow(('Find the host', 'A normal locator finds the element the shadow tree hangs from.'), ('Get its shadow root', 'Get Element Shadow Root. Selenium 4 and Chromium 96 or later.'), ('Search inside', 'Find Element From Shadow Root with a CSS selector.'))}
{SHADOW}
<p>Three facts show in this run. A search from the page cannot see the checkbox. A search from the shadow root can. And Chrome refused an XPath inside the shadow root with <code>invalid argument</code>. When this page was built, tag name was refused too, while id, name and class name worked because the binding sends them as CSS. Use CSS selectors inside shadow roots.</p>
{note('A shadow root can contain another shadow host. Then you repeat the two steps: get that host, get its shadow root, search again. Each level is one more pair of commands.', 'tip')}
''', kw=['shadow dom', 'shadow root', 'shadow host', 'getShadowRoot', 'shadow_root', 'web components', 'custom element', 'invalid locator'])

K.lesson('activeel', 'The active element', f'''
<p>The <b>active element</b> is the element that has the keyboard focus right now: what would receive your typing. The W3C command Get Active Element returns it, and the bindings put it under <code>switchTo()</code>.</p>
{ACTIVE}
<p>This is how you test keyboard behaviour: that Tab moves through a form in a sensible order, that a dialog puts the focus on its first button, or that pressing Enter in a search box submits it. Keyboard users and screen reader users depend on that order.</p>
{ladder(
    '<p>Ask for one element or for all of them. Look inside a part of the page, inside a hidden component, or at the element that has the focus.</p>',
    '<p>find element raises when nothing matches, find elements returns an empty list. Searches from an element stay inside it, except XPath that starts with //. Shadow roots need host, shadow root, then CSS.</p>',
    '<p>Each search is a W3C command with its own endpoint: Find Element, Find Elements, Find Element From Element, Find Elements From Element, Get Element Shadow Root, Find Element From Shadow Root and Get Active Element. Fewer, more precise commands make suites faster.</p>',
    '<p>The shadow root reference is its own web object with the key shadow-6066-11e4-a52e-4f735466cecf, like the element key in chapter 1.2. The W3C spec allows any strategy inside a shadow root, but browsers do not have to support XPath there, which is why portable tests use CSS.</p>')}
''', kw=['active element', 'focus', 'switchTo activeElement', 'keyboard', 'tab order', 'accessibility', 'Keys.TAB'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What does find elements return when nothing matches?', ['null', 'An empty list', 'NoSuchElementException', 'The body element'], 1,
       'Plural is forgiving.', 'The plural methods return an empty collection when nothing matches.')
K.quiz('e', 'What does find element return when three elements match?', ['All three', 'The first in page order', 'The last', 'An error'], 1,
       'Singular.', 'It returns the first element found within the context.')
K.quiz('e', 'Which command gives you the element that has the keyboard focus?', ['Get Focus', 'Get Active Element', 'Find Focused', 'Get Selected'], 1,
       'switchTo().activeElement().', 'The W3C command Get Active Element returns the focused element.')
K.quiz('m', 'You call form.find_elements(By.XPATH, "//a"). The only link is outside the form. How many are returned?', ['0', '1', 'An error', 'All elements of the form'], 1,
       'Where does // start?', 'An XPath starting with // starts at the document root, so the link outside the form is found. Use .//a.')
K.quiz('m', 'Why can a normal find not reach an element inside a web component?', ['It is invisible', 'It is inside a shadow DOM tree attached to the host', 'It is in an iframe', 'Selenium does not support custom elements'], 1,
       'An encapsulated tree.', 'The shadow DOM is an encapsulated tree hidden inside an element, so you search from its shadow root.')
K.quiz('m', 'Which minimum versions does the documentation give for the shadow root methods?', ['Selenium 3 and Chrome 80', 'Selenium 4.0 and Chromium 96', 'Selenium 4.11 only', 'Any version'], 1,
       'Read the shadow DOM section.', 'The documentation says these methods need Selenium 4.0 or greater and Chromium v96.')
K.quiz('m', 'Which locator kind should you use inside a shadow root for Chrome?', ['XPath', 'CSS selector', 'Link text only', 'Any, all work'], 1,
       'One was refused in the real run.', 'Chrome refused XPath and tag name inside the shadow root. CSS selectors work.')
K.quiz('h', 'Why can driver.find_element(By.CSS_SELECTOR, "form #lname") be better than finding the form and then lname?', ['It finds more elements', 'It is one command instead of two', 'It waits longer', 'It works in shadow roots'], 1,
       'Count the round trips.', 'The documentation notes a nested lookup needs two commands. One selector does it in one.')
K.quiz('h', 'In Java, what do WebDriver, WebElement and the shadow root have in common?', ['They extend WebElement', 'They implement SearchContext', 'They are all JavascriptExecutor', 'Nothing'], 1,
       'A role based interface.', 'All three implement SearchContext, which declares findElement and findElements.')
K.quiz('x', 'A page is still loading and find elements returns an empty list for the result cards. What does that list prove?', ['There are no results', 'Only that none were present at that moment', 'The locator is invalid', 'The session ended'], 1,
       'Timing.', 'An empty list says nothing matched at that instant. Wait for the right condition before you decide.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A page has 6 inputs in a form and 1 search box outside it. How many does form.find_elements(css "input") return?', '6', 'CSS from an element stays inside it.',
       ['The search starts at the form.', 'The search box outside is not looked at.', eq('6 inputs')], check=6)
K.calc('e', 'Same page. How many does form.find_elements(xpath "//input") return?', '7', '// starts at the document.',
       ['// ignores the form and starts at the top.', 'It sees the 6 form inputs and the search box.', eq('6 + 1 = 7 inputs')], check=7)
K.calc('m', 'Each command takes 15 ms. A test finds a row, then a button inside it, in 40 rows. How many ms does using one combined CSS selector per row save?', '600', 'One command saved per row.',
       ['Nested: 2 commands per row.', 'Combined: 1 command per row, so 1 saved.', eq('40 × 15 ms = 600 ms saved')], check=600, unit='ms')
K.calc('m', 'A component is nested 3 shadow roots deep. Each level needs a find for the host and a Get Shadow Root. How many commands before the final find?', '6', 'Two per level.',
       ['Per level: find host, get shadow root.', 'Three levels.', eq('3 × 2 = 6 commands, then one more to find the element')], check=6)
K.calc('h', 'Tab moves focus through fields in order. Focus is on field 3 of 9. After pressing Tab 4 times, which field has focus?', '7', 'Add the presses.',
       ['Each Tab moves one field forward.', 'Start at 3, press 4 times.', eq('3 + 4 = 7')], check=7)
K.calc('x', 'A results list should have 20 cards. find_elements runs 300 ms after the search, but cards arrive at 50 ms each starting at 100 ms. How many cards will it count?', '5', 'Count those that arrived by 300 ms.',
       ['Card k arrives at 100 + 50 × (k − 1) ms.', 'By 300 ms: cards arriving at 100, 150, 200, 250 and 300 ms.', eq('5 cards, not 20, so the test must wait for the full list')], check=5)

# ---------------------------------------------------------------- assignments
K.assign('firstmatch', 'e', 'Model find element and find elements',
         '<p>Write <code>find(elements, wanted, plural)</code>. <code>elements</code> is a list of tag names in page order. Return the list of positions that equal <code>wanted</code> when <code>plural</code> is True. When it is False return the first position, or the string <code>"no such element"</code>.</p>',
         '''
def find(elements, wanted, plural):
    # your code here
    pass
''', [('find(["h2", "input", "input", "a"], "input", True)', [1, 2]), ('find(["h2", "input", "input", "a"], "input", False)', 1), ('find(["h2", "a"], "input", True)', []), ('find(["h2", "a"], "input", False)', 'no such element')],
         '''
def find(elements, wanted, plural):
    hits = [i for i, tag in enumerate(elements) if tag == wanted]
    if plural:
        return hits
    return hits[0] if hits else "no such element"
''', 'Collect every matching position first, then decide what to return.', '<p>Both methods do the same search. They only differ in what they hand back, which is why a missing element is an error for one and an empty list for the other.</p>')
K.assign('xpscope', 'm', 'Fix the XPath trap',
         '<p>Write <code>scoped(xpath)</code>. When an XPath is used on an element it should search below that element. If it starts with <code>//</code>, return it with a dot in front. Leave every other XPath unchanged.</p>',
         '''
def scoped(xpath):
    # your code here
    pass
''', [('scoped("//a")', './/a'), ('scoped(".//a")', './/a'), ('scoped("input")', 'input'), ('scoped("//div[@id=\'x\']//span")', ".//div[@id='x']//span")],
         '''
def scoped(xpath):
    if xpath.startswith("//"):
        return "." + xpath
    return xpath
''', 'Only the very start matters.', '<p>The later <code>//</code> in the last example means any descendant of the div, which is fine. Only a leading <code>//</code> jumps to the document root.</p>')

K.must('One or many', 'find element returns the first match or raises no such element. find elements returns all matches or an empty list.')
K.must('Search context', 'You can search from the driver, from an element or from a shadow root. CSS from an element stays inside it.')
K.must('XPath trap', 'An XPath starting with // always starts at the document, even when called on an element. Use .// to search below the element.')
K.must('Shadow DOM', 'Find the host, get its shadow root, then search with a CSS selector. Chrome refuses XPath there.')
K.must('Active element', 'switchTo().activeElement() returns the focused element. Use it to test keyboard flow such as Tab order.')

T = K.topic(
    slug='finding-elements', topic='finding-elements',
    step=(3, 'Find and use elements', 'se-elements', 'Locators, finding elements, interacting with inputs, reading element information, select lists and file upload.', 'Beginner'),
    title='Finding elements: one, many, scoped and in shadow DOM', short='Finding elements', badge='3.2', minutes=40, added='2026-10-29',
    lead='Know exactly what find element and find elements return, search inside one part of a page without falling into the XPath trap, reach into shadow DOM components and find the focused element.',
    desc='find element and find elements with real runs in Java, Python and JavaScript, empty lists and NoSuchElementException, searching from an element, the // XPath trap, optimised single selectors, an animation of search scope, shadow roots with a real refused XPath, and the active element for keyboard tests.',
    summary='Singular and plural finds, scoped searches and the XPath trap, shadow DOM and the active element.',
    keywords=['find element', 'find elements', 'search context', 'shadow dom', 'shadow root', 'active element', 'xpath scope', 'nosuchelement'],
    recap='<p>find element returns the first match or raises, find elements returns all or an empty list. Searching from an element keeps CSS inside it, but an XPath starting with // still starts at the document. Shadow DOM needs host, shadow root and a CSS selector. The active element is the one with the focus.</p>')
