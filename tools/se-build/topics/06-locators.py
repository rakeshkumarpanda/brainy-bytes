# Chapter 3.1: locator strategies, CSS selectors, XPath and relative locators. Sources: selenium.dev documentation
# (Locator strategies with the Contact Selenium example page, Relative Locators, Encouraged practices: locators),
# the W3C WebDriver specification (the five location strategies), the Python binding source that turns id, name and
# class name into CSS selectors, and real runs on the Selenium test pages locators_tests/locators.html and login.html.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, src, flow

K = Kit()

ALL8 = tri('locators', 'All eight locator strategies on the documentation example page', java=r'''
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

public class EightLocators {
    static void show(String how, WebElement e) {  ## A helper that prints which element a locator found.
        System.out.println(how + " -> <" + e.getTagName() + "> " + e.getAttribute("value") + " " + e.getText());
    }

    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/locators_tests/locators.html");
        show("className", driver.findElement(By.className("information")));  ## The first element whose class list contains information.
        show("cssSelector", driver.findElement(By.cssSelector("#fname")));  ## CSS: # means id, so the input with id fname.
        show("id", driver.findElement(By.id("lname")));  ## The element whose id attribute is lname.
        show("name", driver.findElement(By.name("newsletter")));  ## The element whose name attribute is newsletter.
        show("linkText", driver.findElement(By.linkText("Selenium Official Page")));  ## A link whose whole visible text matches.
        show("partialLinkText", driver.findElement(By.partialLinkText("Official")));  ## A link whose visible text contains Official.
        show("tagName", driver.findElement(By.tagName("a")));  ## The first a element on the page.
        show("xpath", driver.findElement(By.xpath("//input[@value='f']")));  ## XPath: any input whose value attribute is f.
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.common.by import By

def show(how, e):  ## A helper that prints which element a locator found.
    print(how, "-> <" + e.tag_name + ">", e.get_attribute("value"), e.text)

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/locators_tests/locators.html")
show("CLASS_NAME", driver.find_element(By.CLASS_NAME, "information"))  ## The first element whose class list contains information.
show("CSS_SELECTOR", driver.find_element(By.CSS_SELECTOR, "#fname"))  ## CSS: # means id, so the input with id fname.
show("ID", driver.find_element(By.ID, "lname"))  ## The element whose id attribute is lname.
show("NAME", driver.find_element(By.NAME, "newsletter"))  ## The element whose name attribute is newsletter.
show("LINK_TEXT", driver.find_element(By.LINK_TEXT, "Selenium Official Page"))  ## A link whose whole visible text matches.
show("PARTIAL_LINK_TEXT", driver.find_element(By.PARTIAL_LINK_TEXT, "Official"))  ## A link whose visible text contains Official.
show("TAG_NAME", driver.find_element(By.TAG_NAME, "a"))  ## The first a element on the page.
show("XPATH", driver.find_element(By.XPATH, "//input[@value='f']"))  ## XPath: any input whose value attribute is f.
driver.quit()
''', js=r'''
const { Builder, Browser, By } = require('selenium-webdriver');

async function show(how, e) {  ## A helper that prints which element a locator found.
  console.log(how + ' -> <' + await e.getTagName() + '> ' + await e.getAttribute('value') + ' ' + await e.getText());
}

(async function eightLocators() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/locators_tests/locators.html');
  await show('className', await driver.findElement(By.className('information')));  ## The first element whose class list contains information.
  await show('css', await driver.findElement(By.css('#fname')));  ## CSS: # means id, so the input with id fname.
  await show('id', await driver.findElement(By.id('lname')));  ## The element whose id attribute is lname.
  await show('name', await driver.findElement(By.name('newsletter')));  ## The element whose name attribute is newsletter.
  await show('linkText', await driver.findElement(By.linkText('Selenium Official Page')));  ## A link whose whole visible text matches.
  await show('partialLinkText', await driver.findElement(By.partialLinkText('Official')));  ## A link whose visible text contains Official.
  await show('tagName', await driver.findElement(By.tagName('a')));  ## The first a element on the page.
  await show('xpath', await driver.findElement(By.xpath("//input[@value='f']")));  ## XPath: any input whose value attribute is f.
  await driver.quit();
})();
''', expect='Selenium Official Page')

RELATIVE = tri('relative', 'Relative locators: find an element by where it sits', java=r'''
import static org.openqa.selenium.support.locators.RelativeLocator.with;  ## with() starts a relative locator.

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

public class Relative {
    static void show(String how, WebElement e) {
        System.out.println(how + " -> " + e.getAttribute("outerHTML"));  ## outerHTML shows the whole tag that was found.
    }

    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/locators_tests/locators.html");
        show("below last name label", driver.findElement(with(By.tagName("input")).below(By.cssSelector("label[for='lname']"))));  ## An input below the Last name label. The closest one wins.
        show("above lname", driver.findElement(with(By.tagName("input")).above(By.id("lname"))));  ## An input above the lname box.
        show("right of Male", driver.findElement(with(By.tagName("input")).toRightOf(By.cssSelector("input[value='m']"))));  ## An input to the right of the Male radio.
        show("below fname and above the checkbox", driver.findElement(with(By.tagName("input")).below(By.id("fname")).above(By.name("newsletter"))));  ## Chained: both conditions must hold.
        show("near Newsletter label", driver.findElement(with(By.tagName("input")).near(By.cssSelector("label[for='newsletter']"))));  ## near means at most 50 pixels away. Look at what it really returned.
        driver.get("https://www.selenium.dev/selenium/web/login.html");
        show("left of password", driver.findElement(with(By.tagName("input")).toLeftOf(By.id("password-field"))));  ## On the login page the three inputs sit in one row.
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.relative_locator import locate_with  ## locate_with() starts a relative locator.

def show(how, e):
    print(how, "->", e.get_attribute("outerHTML"))  ## outerHTML shows the whole tag that was found.

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/locators_tests/locators.html")
show("below last name label", driver.find_element(locate_with(By.TAG_NAME, "input").below({By.CSS_SELECTOR: "label[for='lname']"})))  ## Python writes the anchor locator as a small dict.
show("above lname", driver.find_element(locate_with(By.TAG_NAME, "input").above({By.ID: "lname"})))  ## An input above the lname box.
show("right of Male", driver.find_element(locate_with(By.TAG_NAME, "input").to_right_of({By.CSS_SELECTOR: "input[value='m']"})))  ## An input to the right of the Male radio.
show("below fname and above the checkbox", driver.find_element(locate_with(By.TAG_NAME, "input").below({By.ID: "fname"}).above({By.NAME: "newsletter"})))  ## Chained: both conditions must hold.
show("near Newsletter label", driver.find_element(locate_with(By.TAG_NAME, "input").near({By.CSS_SELECTOR: "label[for='newsletter']"})))  ## near means at most 50 pixels away. Look at what it really returned.
driver.get("https://www.selenium.dev/selenium/web/login.html")
show("left of password", driver.find_element(locate_with(By.TAG_NAME, "input").to_left_of({By.ID: "password-field"})))  ## On the login page the three inputs sit in one row.
driver.quit()
''', js=r'''
const { Builder, Browser, By, locateWith } = require('selenium-webdriver');  ## locateWith() starts a relative locator.

async function show(how, e) {
  console.log(how + ' -> ' + await e.getAttribute('outerHTML'));  ## outerHTML shows the whole tag that was found.
}

(async function relative() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/locators_tests/locators.html');
  await show('below last name label', await driver.findElement(locateWith(By.tagName('input')).below(By.css("label[for='lname']"))));  ## An input below the Last name label. The closest one wins.
  await show('above lname', await driver.findElement(locateWith(By.tagName('input')).above(By.id('lname'))));  ## An input above the lname box.
  await show('right of Male', await driver.findElement(locateWith(By.tagName('input')).toRightOf(By.css("input[value='m']"))));  ## An input to the right of the Male radio.
  await show('below fname and above the checkbox', await driver.findElement(locateWith(By.tagName('input')).below(By.id('fname')).above(By.name('newsletter'))));  ## Chained: both conditions must hold.
  await show('near Newsletter label', await driver.findElement(locateWith(By.tagName('input')).near(By.css("label[for='newsletter']"))));  ## near means at most 50 pixels away. Look at what it really returned.
  await driver.get('https://www.selenium.dev/selenium/web/login.html');
  await show('left of password', await driver.findElement(locateWith(By.tagName('input')).toLeftOf(By.id('password-field'))));  ## On the login page the three inputs sit in one row.
  await driver.quit();
})();
''', expect='left of password')

K.lesson('strategies', 'The eight locator strategies', f'''
<p>Before Selenium can click or type, it must find the element. A <b>locator</b> is the description you give it: "the input whose id is lname", "the first link that says Official". The documentation lists eight traditional strategies, all shown on its Contact Selenium example page, which this chapter uses too.</p>
{src('py', """<h2>Contact Selenium</h2>
<form>
  <input type="radio" name="gender" value="m" />Male
  <input type="radio" name="gender" value="f" />Female
  <label for="fname">First name:</label>
  <input class="information" type="text" id="fname" name="fname" value="Jane">
  <label for="lname">Last name:</label>
  <input class="information" type="text" id="lname" name="lname" value="Doe">
  <label for="newsletter">Newsletter:</label>
  <input type="checkbox" name="newsletter" value="1" />
  <input type="submit" value="Submit">
</form>
<p>... <a href="https://www.selenium.dev/">Selenium Official Page</a></p>""", 'locators.html (shortened)')}
{table(['Strategy', 'Finds', 'Example'], [
    ['id', 'The element whose id attribute matches', '<code>lname</code>'],
    ['name', 'Elements whose name attribute matches', '<code>newsletter</code>'],
    ['class name', 'Elements whose class list contains the value. Compound names such as "a b" are not allowed.', '<code>information</code>'],
    ['css selector', 'Elements matching a CSS selector', '<code>#fname</code>'],
    ['xpath', 'Elements matching an XPath expression', '<code>//input[@value=\'f\']</code>'],
    ['tag name', 'Elements with that tag', '<code>a</code>'],
    ['link text', 'Links whose visible text is exactly the value', '<code>Selenium Official Page</code>'],
    ['partial link text', 'Links whose visible text contains the value', '<code>Official</code>']])}
{ALL8}
<p>Each line asked for one element and got the first match. class name <code>information</code> matches two inputs, Jane and Doe, and returned Jane because it comes first in the page.</p>
{viz('se-locate')}
<h3>Only five reach the browser</h3>
<p>The W3C protocol knows five strategies: css selector, link text, partial link text, tag name and xpath. So where do id, name and class name go? The binding turns them into CSS before sending. You saw it in chapter 1.2: Python sent <code>[name="my-text"]</code> for By.NAME. Python turns id into <code>[id="lname"]</code> and class name into <code>.information</code>.</p>
{note('find element (singular) returns the first match or raises no such element. find elements (plural) returns every match in page order, or an empty list. Chapter 3.2 covers the difference in detail.', 'tip')}
''', kw=['locator', 'By', 'id', 'name', 'class name', 'css selector', 'xpath', 'tag name', 'link text', 'partial link text', 'locator strategies'])

K.lesson('cssxpath', 'CSS selectors and XPath', f'''
<p>id and name only work when the page has them. For everything else you write a CSS selector or an XPath. Both describe a path through the page, in two different languages.</p>
{table(['To find', 'CSS selector', 'XPath'], [
    ['By id', '<code>#fname</code>', '<code>//*[@id="fname"]</code>'],
    ['By class', '<code>.information</code>', '<code>//*[contains(@class,"information")]</code>'],
    ['Tag with attribute', '<code>input[name="fname"]</code>', '<code>//input[@name="fname"]</code>'],
    ['Attribute starts with', '<code>a[href^="https"]</code>', '<code>//a[starts-with(@href,"https")]</code>'],
    ['Attribute contains', '<code>a[href*="selenium"]</code>', '<code>//a[contains(@href,"selenium")]</code>'],
    ['Direct child', '<code>form > input</code>', '<code>//form/input</code>'],
    ['Any descendant', '<code>form input</code>', '<code>//form//input</code>'],
    ['Second matching input', '<code>input:nth-of-type(2)</code>', '<code>(//input)[2]</code>'],
    ['By visible text', 'not possible', '<code>//label[text()="Last name:"]</code>'],
    ['The parent', 'not possible', '<code>//input[@id="lname"]/..</code>'],
    ['Next sibling', '<code>label + input</code>', '<code>//label[@for="lname"]/following-sibling::input[1]</code>']])}
{steps('Read a CSS selector from left to right', [
    '<code>form</code>: start at a form element.',
    '<code>></code>: go to its direct children only.',
    '<code>input</code>: keep the children that are inputs.',
    '<code>[type="text"]</code>: keep the ones whose type attribute is text.',
    'So <code>form > input[type="text"]</code> finds the First name and Last name boxes.'])}
<p>XPath has two forms. An <b>absolute</b> path starts at the root, such as <code>/html/body/form/input[1]</code>. It breaks as soon as anyone adds a div. A <b>relative</b> path starts with <code>//</code> and searches anywhere, such as <code>//input[@name="fname"]</code>. Use relative paths.</p>
<p>Open the playground, change any locator and run it. The element found is outlined on the page, and the log shows exactly what was sent to the driver.</p>
<div class="sp" data-sp="locators"></div>
{deep('How to test a selector before you use it', '<p>Open the page in Chrome, press F12 and go to the Console. <code>document.querySelectorAll("form > input")</code> lists what a CSS selector matches. <code>$x("//label[text()=\'Last name:\']")</code> does the same for XPath. In the Elements panel, Ctrl+F also accepts both. If the browser finds it, Selenium will too, because the driver asks the same browser.</p>')}
''', kw=['css selector', 'xpath', 'absolute xpath', 'relative xpath', 'contains', 'starts-with', 'text()', 'nth-of-type', 'following-sibling', 'parent', 'devtools'])

K.lesson('relative', 'Relative locators', f'''
<p>Selenium 4 added <b>relative locators</b>, first called friendly locators. They help when an element is hard to describe but easy to place: "the input below the Last name label". The documentation explains that Selenium uses the JavaScript function getBoundingClientRect() to learn the size and position of elements, then picks neighbours.</p>
{table(['Method', 'Finds an element that is', 'Note'], [
    ['above', 'higher on the page than the anchor', ''],
    ['below', 'lower on the page than the anchor', ''],
    ['toLeftOf / to_left_of', 'left of the anchor', ''],
    ['toRightOf / to_right_of', 'right of the anchor', ''],
    ['near', 'at most 50 pixels from the anchor', 'Useful for an input next to its label']])}
{RELATIVE}
<p>Look closely at the near line. You might expect the Newsletter checkbox, which sits right next to its label. The real run returned the Submit button. The relative locator code in the bindings explains why. near keeps every candidate whose box overlaps the anchor box grown by 50 pixels on each side, and both the checkbox and the button qualify. The candidates are then sorted by the distance between their centre and the centre of the anchor. The label text is wide, so its centre is closer to the Submit button underneath than to the checkbox at its right end. That is the honest lesson about relative locators: they depend on layout, so a different window size or a CSS change can change the answer. Use them when nothing better exists, and check what they return.</p>
{note('Each relative locator sends the page a script to run, so it is slower than a plain CSS selector. Prefer an id or a short CSS selector, and keep relative locators for elements with no good attributes.', 'warn')}
''', kw=['relative locators', 'friendly locators', 'above', 'below', 'toLeftOf', 'toRightOf', 'near', '50 pixels', 'getBoundingClientRect', 'locate_with', 'locateWith', 'chaining'])

K.lesson('choose', 'Choosing a good locator', f'''
<p>A test is only as stable as its locators. The encouraged practices page of the documentation gives an order of preference.</p>
{steps('From best to last resort', [
    '<b>A unique, stable id.</b> Fast, short and clear. Preferred whenever the id is unique and predictable.',
    '<b>A well written CSS selector.</b> The preferred choice when there is no good id.',
    '<b>XPath.</b> Works as well as CSS and can match text, but the syntax is harder to debug and browsers do not tune it for speed.',
    '<b>Link text and partial link text.</b> Only work on links.',
    '<b>Tag name.</b> Dangerous for a single element, because pages have many of each tag. Useful with find elements.'])}
{table(['Fragile locator', 'Why it breaks', 'Better'], [
    ['<code>/html/body/div[2]/form/input[3]</code>', 'Any new div or input shifts the path', '<code>#lname</code>'],
    ['<code>.btn.btn-primary.mt-3</code>', 'Styling classes change when the design changes', '<code>[data-test="submit"]</code>'],
    ['<code>//button[text()="Submit"]</code>', 'Breaks when the text is translated or reworded', 'An id or a data attribute'],
    ['<code>#ember1234</code>', 'Generated ids change on every page load', 'A stable attribute near it']])}
{scene('a test id agreement', '<p>A team keeps breaking tests whenever designers restyle buttons. They agree with the developers that every element a test touches gets a <code>data-test</code> attribute, such as <code>data-test="checkout-pay"</code>. Tests use <code>[data-test="checkout-pay"]</code>. Designers can now change classes and text freely, and the tests keep passing.</p>')}
{note('Keep locators in one place, apart from the steps that use them. The documentation recommends declaring them separately, which is exactly what a page object does. Chapter 5.2 shows the pattern.', 'exam')}
{ladder(
    '<p>A locator is directions to an element. Short, unique directions that do not depend on looks are the best.</p>',
    '<p>id first, then CSS, then XPath. Avoid long absolute paths and styling classes. Relative locators help when an element has no good attribute.</p>',
    '<p>id, name and class name compile to CSS in the bindings, so all of them run on the browser selector engine. Narrowing the scope, for example finding inside one form, cuts the work the browser does and the chance of a wrong match.</p>',
    '<p>Locator stability is a contract between test and product code. Dedicated test attributes make that contract explicit and survive redesigns, translation and framework changes that rename generated ids.</p>')}
''', kw=['best locator', 'stable locator', 'data-test', 'id first', 'fragile locators', 'generated ids', 'encouraged practices', 'page object'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'How many traditional locator strategies does the Selenium documentation list?', ['5', '6', '8', '10'], 2,
       'Count id, name, class name and the rest.', 'Eight: class name, css selector, id, name, link text, partial link text, tag name and xpath.')
K.quiz('e', 'What does By.id("lname") find?', ['Elements whose name is lname', 'The element whose id attribute is lname', 'Links with text lname', 'Any element containing lname'], 1,
       'The id attribute.', 'id finds the element whose ID attribute matches.')
K.quiz('e', 'Which locator only works on links?', ['tag name', 'link text', 'css selector', 'name'], 1,
       'Its name says it.', 'link text and partial link text only work on anchor elements.')
K.quiz('m', 'class name "information" matches two inputs. What does find element return?', ['Both', 'The first in page order', 'The last', 'An error'], 1,
       'Singular.', 'find element returns the first match. find elements returns both.')
K.quiz('m', 'Which locator strategies does the W3C protocol itself define?', ['All eight', 'id, name and class name only', 'css selector, link text, partial link text, tag name and xpath', 'Only xpath'], 2,
       'id is not one of them.', 'The W3C spec has five. Bindings turn id, name and class name into CSS.')
K.quiz('m', 'What is the main risk of /html/body/div[2]/form/input[3]?', ['It is too short', 'It breaks when the page structure changes', 'Browsers do not support XPath', 'It is case sensitive'], 1,
       'Absolute paths.', 'An absolute path depends on every level of the page, so any added element breaks it.')
K.quiz('m', 'What does near() mean for a relative locator?', ['Inside the anchor', 'At most 50 pixels away', 'The next sibling in HTML', 'Same parent'], 1,
       'A distance in pixels.', 'The documentation says near finds an element at most 50px from the anchor.')
K.quiz('h', 'Which can XPath do that CSS selectors cannot?', ['Match by attribute', 'Match direct children', 'Match by visible text and move to a parent', 'Match by id'], 2,
       'Think text() and ..', 'XPath can test text() and walk up with .. or the parent axis. CSS cannot.')
K.quiz('h', 'According to the documentation, which locator is preferred when ids are not available?', ['XPath', 'A well written CSS selector', 'Tag name', 'Partial link text'], 1,
       'The encouraged practices page.', 'If unique IDs are unavailable, a well written CSS selector is the preferred method.')
K.quiz('x', 'Relative locators use which browser function to compare positions?', ['offsetTop', 'getBoundingClientRect()', 'scrollIntoView()', 'elementFromPoint()'], 1,
       'It returns a rectangle.', 'The documentation names getBoundingClientRect() as the source of sizes and positions.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A page has 7 input elements. How many elements does find elements with tag name input return?', '7', 'Plural returns every match.',
       ['tag name matches every element with that tag.', 'find elements returns all of them in page order.', eq('7 elements')], check=7)
K.calc('e', 'near() allows at most 50 pixels. A checkbox is 42 pixels from a label and a button is 48 pixels away. How many qualify?', '2', 'Compare each with 50.',
       ['42 ≤ 50, so the checkbox qualifies.', '48 ≤ 50, so the button qualifies too.', eq('2 elements qualify, which is why near can surprise you')], check=2)
K.calc('m', 'An absolute XPath has 6 levels. Each release, each level has a 5 % chance of changing. What is the chance it survives one release, in percent?', '73.51', 'Every level must survive.',
       ['One level survives with 0.95.', 'Six levels must all survive: 0.95⁶.', eq('0.95⁶ ≈ 0.7351 = 73.51 %')], check=73.51, tol=0.05, unit='%')
K.calc('m', 'Same release model, but a short CSS selector depends on only 1 level. How many percentage points more likely is it to survive?', '21.49', 'Compare 95 % with 73.51 %.',
       ['One level survives with 95 %.', 'Six levels survive with 73.51 %.', eq('95 − 73.51 = 21.49 points')], check=21.49, tol=0.05)
K.calc('h', 'An input sits 120 px below a label. The next input sits 195 px below it. Which distance does below() pick first, in px?', '120', 'The closest one wins.',
       ['Both inputs are below the label.', 'Relative locators sort the candidates by the distance between centres.', eq('120 px, the nearer input')], check=120, unit='px')
K.calc('x', 'A suite uses 400 locators. 30 % are XPath, and moving to CSS saves 4 ms per lookup. Each locator is used 25 times per run. How many seconds per run would switching save?', '12', 'Count XPath lookups.',
       ['XPath locators: 30 % of 400 = 120.', 'Lookups: 120 × 25 = 3,000.', eq('3,000 × 4 ms = 12,000 ms = 12 seconds')], check=12)

# ---------------------------------------------------------------- assignments
K.assign('tocss', 'm', 'Turn a locator into what the Python binding sends',
         '<p>Write <code>to_w3c(by, value)</code> that returns <code>(using, value)</code> as the Python binding sends it. id becomes css selector <code>[id="value"]</code>, name becomes <code>[name="value"]</code>, class name becomes <code>.value</code>. css selector, xpath, tag name, link text and partial link text pass through unchanged.</p>',
         '''
def to_w3c(by, value):
    # your code here
    pass
''', [('to_w3c("id", "lname")', ('css selector', '[id="lname"]')), ('to_w3c("name", "newsletter")', ('css selector', '[name="newsletter"]')), ('to_w3c("class name", "information")', ('css selector', '.information')), ('to_w3c("xpath", "//a")', ('xpath', '//a')), ('to_w3c("link text", "Home")', ('link text', 'Home'))],
         '''
def to_w3c(by, value):
    if by == "id":
        return ("css selector", '[id="' + value + '"]')
    if by == "name":
        return ("css selector", '[name="' + value + '"]')
    if by == "class name":
        return ("css selector", "." + value)
    return (by, value)
''', 'Handle the three converted strategies, then return the rest unchanged.', '<p>The real binding also escapes special characters in the value. This version keeps the idea and leaves that out.</p>')
K.assign('fragile', 'e', 'Spot a fragile XPath',
         '<p>Write <code>is_absolute(xpath)</code> that returns True when an XPath is absolute, which means it starts with a single <code>/</code> and not with <code>//</code>.</p>',
         '''
def is_absolute(xpath):
    # your code here
    pass
''', [('is_absolute("/html/body/form/input[1]")', True), ('is_absolute("//input[@name=\'fname\']")', False), ('is_absolute("(//input)[2]")', False)],
         '''
def is_absolute(xpath):
    return xpath.startswith("/") and not xpath.startswith("//")
''', 'Check the first two characters.', '<p>A path in brackets such as <code>(//input)[2]</code> starts with a bracket, so it is relative too.</p>')

K.must('Eight strategies', 'id, name, class name, css selector, xpath, tag name, link text, partial link text. find element returns the first match.')
K.must('Five on the wire', 'W3C defines css selector, link text, partial link text, tag name and xpath. Bindings turn id, name and class name into CSS.')
K.must('CSS and XPath', 'CSS: #id, .class, tag[attr="v"], parent > child. XPath adds text matching and moving up to a parent. Prefer relative XPath (//).')
K.must('Relative locators', 'above, below, toLeftOf, toRightOf and near (50 px), built on getBoundingClientRect. They depend on layout, so check what they return.')
K.must('Preference', 'Unique stable id, then a short CSS selector, then XPath. Avoid absolute paths, styling classes and generated ids. Consider data-test attributes.')

T = K.topic(
    slug='locators', topic='locators',
    step=(3, 'Find and use elements', 'se-elements', 'Locators, finding elements, interacting with inputs, reading element information, select lists and file upload.', 'Beginner'),
    title='Locators: how Selenium finds an element', short='Locators', badge='3.1', minutes=50, added='2026-10-29',
    lead='Learn all eight locator strategies on one page, read and write CSS selectors and XPath, place elements with relative locators, and pick locators that survive the next redesign.',
    desc='The eight traditional locators run in Java, Python and JavaScript, the five W3C strategies and how bindings convert id, name and class name, CSS selector and XPath side by side, relative locators above, below, left, right and near with a real surprise, and the documentation advice on choosing locators.',
    summary='All eight locator strategies, CSS and XPath, relative locators and how to choose a locator that lasts.',
    keywords=['locators', 'by', 'css selector', 'xpath', 'id', 'name', 'class name', 'relative locators', 'link text', 'tag name'],
    recap='<p>A locator describes an element. Selenium has eight strategies, and the binding turns id, name and class name into CSS for the five W3C ones. CSS is short and fast, XPath can match text and parents, and relative locators place elements by position. Prefer stable ids, then short CSS.</p>')
