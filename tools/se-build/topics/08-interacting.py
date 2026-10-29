# Chapter 3.3: interacting with elements and reading element information. Sources: selenium.dev documentation
# (Interacting with web elements, Information about web elements, Working with select list elements, File Upload),
# the W3C WebDriver specification (Element Click, Element Send Keys, Element Clear, interactability, obscured
# elements, Get Element Attribute and Get Element Property) and real runs against Chrome 153 on the Selenium test
# pages web-form.html and formPage.html.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, src, flow

K = Kit()

FORM = tri('typeclick', 'Fill in a form: clear, type, tick and click', java=r'''
import java.time.Duration;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

public class FillForm {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(2));  ## As in chapter 1.3: let finds retry for up to 2 seconds, so the page after Submit has time to load.
        driver.get("https://www.selenium.dev/selenium/web/web-form.html");
        WebElement text = driver.findElement(By.name("my-text"));
        text.sendKeys("first try");  ## Element Send Keys: types into the box, adding to what is already there.
        text.clear();  ## Element Clear: empties the box.
        text.sendKeys("Selenium");  ## Type the real value.
        WebElement check2 = driver.findElement(By.id("my-check-2"));
        System.out.println("check 2 before: " + check2.isSelected());  ## isSelected reads whether a checkbox is ticked.
        check2.click();  ## Element Click: ticks it, as a mouse click would.
        System.out.println("check 2 after: " + check2.isSelected());
        driver.findElement(By.id("my-radio-2")).click();  ## Clicking the second radio button unselects the first one.
        System.out.println("radio 1 now: " + driver.findElement(By.id("my-radio-1")).isSelected());
        driver.findElement(By.cssSelector("button")).click();  ## Click Submit. The documentation prefers this to the submit() method.
        System.out.println(driver.findElement(By.id("message")).getText());
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.implicitly_wait(2)  ## As in chapter 1.3: let finds retry for up to 2 seconds, so the page after Submit has time to load.
driver.get("https://www.selenium.dev/selenium/web/web-form.html")
text = driver.find_element(By.NAME, "my-text")
text.send_keys("first try")  ## Element Send Keys: types into the box, adding to what is already there.
text.clear()  ## Element Clear: empties the box.
text.send_keys("Selenium")  ## Type the real value.
check2 = driver.find_element(By.ID, "my-check-2")
print("check 2 before:", check2.is_selected())  ## is_selected reads whether a checkbox is ticked.
check2.click()  ## Element Click: ticks it, as a mouse click would.
print("check 2 after:", check2.is_selected())
driver.find_element(By.ID, "my-radio-2").click()  ## Clicking the second radio button unselects the first one.
print("radio 1 now:", driver.find_element(By.ID, "my-radio-1").is_selected())
driver.find_element(By.CSS_SELECTOR, "button").click()  ## Click Submit. The documentation prefers this to the submit() method.
print(driver.find_element(By.ID, "message").text)
driver.quit()
''', js=r'''
const { Builder, Browser, By } = require('selenium-webdriver');

(async function fillForm() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.manage().setTimeouts({ implicit: 2000 });  ## As in chapter 1.3: let finds retry for up to 2 seconds, so the page after Submit has time to load.
  await driver.get('https://www.selenium.dev/selenium/web/web-form.html');
  const text = await driver.findElement(By.name('my-text'));
  await text.sendKeys('first try');  ## Element Send Keys: types into the box, adding to what is already there.
  await text.clear();  ## Element Clear: empties the box.
  await text.sendKeys('Selenium');  ## Type the real value.
  const check2 = await driver.findElement(By.id('my-check-2'));
  console.log('check 2 before: ' + await check2.isSelected());  ## isSelected reads whether a checkbox is ticked.
  await check2.click();  ## Element Click: ticks it, as a mouse click would.
  console.log('check 2 after: ' + await check2.isSelected());
  await driver.findElement(By.id('my-radio-2')).click();  ## Clicking the second radio button unselects the first one.
  console.log('radio 1 now: ' + await driver.findElement(By.id('my-radio-1')).isSelected());
  await driver.findElement(By.css('button')).click();  ## Click Submit. The documentation prefers this to the submit() method.
  console.log(await driver.findElement(By.id('message')).getText());
  await driver.quit();
})();
''', expect='Received!')

ERRS = tri('interacterr', 'The three errors interactions give, made on purpose', java=r'''
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebDriverException;
import org.openqa.selenium.chrome.ChromeDriver;

public class InteractErrors {
    static void attempt(String what, Runnable step) {  ## Run one step and report the error it raises, if any.
        try {
            step.run();
            System.out.println(what + ": ok");
        } catch (WebDriverException e) {
            System.out.println(what + ": " + e.getClass().getSimpleName() + ", " + e.getMessage().split("[:\n]")[0]);
        }
    }

    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/web-form.html");
        attempt("type into disabled", () -> driver.findElement(By.name("my-disabled")).sendKeys("x"));  ## A disabled input cannot take keyboard input.
        attempt("clear readonly", () -> driver.findElement(By.name("my-readonly")).clear());  ## A readonly input cannot be reset.
        ((JavascriptExecutor) driver).executeScript(  ## Add a cookie banner that covers the bottom of the page, as many real sites do.
            "const b = document.createElement('div'); b.textContent = 'We use cookies';"
            + "b.style.cssText = 'position:fixed;left:0;right:0;bottom:0;height:400px;background:orange';"
            + "document.body.appendChild(b);");
        attempt("click under banner", () -> driver.findElement(By.cssSelector("button")).click());  ## The banner sits over the centre of the button.
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

def attempt(what, step):  ## Run one step and report the error it raises, if any.
    try:
        step()
        print(what + ": ok")
    except WebDriverException as e:  ## Every Selenium error is a WebDriverException.
        print(what + ":", type(e).__name__ + ",", e.msg.split(":")[0].split("\n")[0])

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/web-form.html")
attempt("type into disabled", lambda: driver.find_element(By.NAME, "my-disabled").send_keys("x"))  ## A disabled input cannot take keyboard input.
attempt("clear readonly", lambda: driver.find_element(By.NAME, "my-readonly").clear())  ## A readonly input cannot be reset.
driver.execute_script(  ## Add a cookie banner that covers the bottom of the page, as many real sites do.
    "const b = document.createElement('div'); b.textContent = 'We use cookies';"
    "b.style.cssText = 'position:fixed;left:0;right:0;bottom:0;height:400px;background:orange';"
    "document.body.appendChild(b);")
attempt("click under banner", lambda: driver.find_element(By.CSS_SELECTOR, "button").click())  ## The banner sits over the centre of the button.
driver.quit()
''', js=r'''
const { Builder, Browser, By, error } = require('selenium-webdriver');

async function attempt(what, step) {  ## Run one step and report the error it raises, if any.
  try {
    await step();
    console.log(what + ': ok');
  } catch (e) {
    if (!(e instanceof error.WebDriverError)) throw e;  ## Every Selenium error extends WebDriverError.
    console.log(what + ': ' + e.name + ', ' + e.message.split(/[:\n]/)[0]);
  }
}

(async function interactErrors() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/web-form.html');
  await attempt('type into disabled', async () => (await driver.findElement(By.name('my-disabled'))).sendKeys('x'));  ## A disabled input cannot take keyboard input.
  await attempt('clear readonly', async () => (await driver.findElement(By.name('my-readonly'))).clear());  ## A readonly input cannot be reset.
  await driver.executeScript(  ## Add a cookie banner that covers the bottom of the page, as many real sites do.
    "const b = document.createElement('div'); b.textContent = 'We use cookies';" +
    "b.style.cssText = 'position:fixed;left:0;right:0;bottom:0;height:400px;background:orange';" +
    'document.body.appendChild(b);');
  await attempt('click under banner', async () => (await driver.findElement(By.css('button'))).click());  ## The banner sits over the centre of the button.
  await driver.quit();
})();
''', expect='click under banner')

INFO = tri('info', 'Ask an element about itself', java=r'''
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

public class ElementInfo {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/web-form.html");
        WebElement text = driver.findElement(By.name("my-text"));
        text.sendKeys("hello");  ## Type, so the live value differs from the HTML.
        System.out.println("displayed: " + text.isDisplayed() + ", enabled: " + text.isEnabled());
        System.out.println("disabled box enabled: " + driver.findElement(By.name("my-disabled")).isEnabled());  ## The disabled input reports false.
        System.out.println("tag: " + text.getTagName() + ", rect: " + text.getRect().getWidth() + " x " + text.getRect().getHeight());  ## Get Element Rect: position and size in pixels.
        System.out.println("getAttribute(value): " + text.getAttribute("value"));  ## The classic method: property first, then attribute.
        System.out.println("getDomAttribute(value): " + text.getDomAttribute("value"));  ## Only what the HTML says. The HTML has no value attribute.
        System.out.println("getDomProperty(value): " + text.getDomProperty("value"));  ## The live JavaScript property: what is typed now.
        System.out.println("getDomAttribute(myprop): " + text.getDomAttribute("myprop"));  ## A made up attribute in the HTML.
        System.out.println("button colour: " + driver.findElement(By.cssSelector("button")).getCssValue("color"));  ## The computed CSS value.
        System.out.println("heading text: " + driver.findElement(By.tagName("h1")).getText());  ## The rendered, visible text.
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/web-form.html")
text = driver.find_element(By.NAME, "my-text")
text.send_keys("hello")  ## Type, so the live value differs from the HTML.
print("displayed:", text.is_displayed(), ", enabled:", text.is_enabled())
print("disabled box enabled:", driver.find_element(By.NAME, "my-disabled").is_enabled())  ## The disabled input reports False.
print("tag:", text.tag_name, ", rect:", text.rect["width"], "x", text.rect["height"])  ## Get Element Rect: position and size in pixels.
print("get_attribute(value):", text.get_attribute("value"))  ## The classic method: property first, then attribute.
print("get_dom_attribute(value):", text.get_dom_attribute("value"))  ## Only what the HTML says. The HTML has no value attribute.
print("get_property(value):", text.get_property("value"))  ## The live JavaScript property: what is typed now.
print("get_dom_attribute(myprop):", text.get_dom_attribute("myprop"))  ## A made up attribute in the HTML.
print("button colour:", driver.find_element(By.CSS_SELECTOR, "button").value_of_css_property("color"))  ## The computed CSS value.
print("heading text:", driver.find_element(By.TAG_NAME, "h1").text)  ## The rendered, visible text.
driver.quit()
''', js=r'''
const { Builder, Browser, By } = require('selenium-webdriver');

(async function elementInfo() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/web-form.html');
  const text = await driver.findElement(By.name('my-text'));
  await text.sendKeys('hello');  ## Type, so the live value differs from the HTML.
  console.log('displayed: ' + await text.isDisplayed() + ', enabled: ' + await text.isEnabled());
  console.log('disabled box enabled: ' + await driver.findElement(By.name('my-disabled')).isEnabled());  ## The disabled input reports false.
  const rect = await text.getRect();  ## Get Element Rect: position and size in pixels.
  console.log('tag: ' + await text.getTagName() + ', rect: ' + rect.width + ' x ' + rect.height);
  console.log('getAttribute(value): ' + await text.getAttribute('value'));  ## The classic method: property first, then attribute.
  console.log('getDomAttribute(value): ' + await text.getDomAttribute('value'));  ## Only what the HTML says. The HTML has no value attribute.
  console.log('getProperty(value): ' + await text.getProperty('value'));  ## The live JavaScript property: what is typed now.
  console.log('getDomAttribute(myprop): ' + await text.getDomAttribute('myprop'));  ## A made up attribute in the HTML.
  console.log('button colour: ' + await driver.findElement(By.css('button')).getCssValue('color'));  ## The computed CSS value.
  console.log('heading text: ' + await driver.findElement(By.css('h1')).getText());  ## The rendered, visible text.
  await driver.quit();
})();
''', expect='hello')

SELECT = tri('select', 'Work with single and multiple select lists', java=r'''
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.Select;  ## Select lives in the support package.

public class Selects {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/formPage.html");
        Select single = new Select(driver.findElement(By.name("selectomatic")));  ## Wrap a select element in a Select object.
        System.out.println("options: " + single.getOptions().size());  ## getOptions lists every option element.
        single.selectByVisibleText("Four");  ## Pick by the text the user sees.
        System.out.println("now: " + single.getFirstSelectedOption().getText());
        single.selectByValue("two");  ## Pick by the value attribute.
        System.out.println("now: " + single.getFirstSelectedOption().getText());
        single.selectByIndex(0);  ## Pick by position, counting from 0.
        System.out.println("now: " + single.getFirstSelectedOption().getText());
        Select multi = new Select(driver.findElement(By.id("multi")));  ## A select with the multiple attribute.
        System.out.println("multi starts with: " + multi.getAllSelectedOptions().size() + " selected");  ## Eggs and Sausages are selected in the HTML.
        multi.deselectByValue("eggs");  ## Only multiple lists can deselect.
        multi.selectByVisibleText("Ham");
        for (WebElement o : multi.getAllSelectedOptions()) System.out.println("  selected: " + o.getText());
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select  ## Select lives in the support package.

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/formPage.html")
single = Select(driver.find_element(By.NAME, "selectomatic"))  ## Wrap a select element in a Select object.
print("options:", len(single.options))  ## options lists every option element.
single.select_by_visible_text("Four")  ## Pick by the text the user sees.
print("now:", single.first_selected_option.text)
single.select_by_value("two")  ## Pick by the value attribute.
print("now:", single.first_selected_option.text)
single.select_by_index(0)  ## Pick by position, counting from 0.
print("now:", single.first_selected_option.text)
multi = Select(driver.find_element(By.ID, "multi"))  ## A select with the multiple attribute.
print("multi starts with:", len(multi.all_selected_options), "selected")  ## Eggs and Sausages are selected in the HTML.
multi.deselect_by_value("eggs")  ## Only multiple lists can deselect.
multi.select_by_visible_text("Ham")
for o in multi.all_selected_options:
    print("  selected:", o.text)
driver.quit()
''', js=r'''
const { Builder, Browser, By, Select } = require('selenium-webdriver');

(async function selects() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/formPage.html');
  const single = new Select(await driver.findElement(By.name('selectomatic')));  ## Wrap a select element in a Select object.
  console.log('options: ' + (await single.getOptions()).length);  ## getOptions lists every option element.
  await single.selectByVisibleText('Four');  ## Pick by the text the user sees.
  console.log('now: ' + await (await single.getFirstSelectedOption()).getText());
  await single.selectByValue('two');  ## Pick by the value attribute.
  console.log('now: ' + await (await single.getFirstSelectedOption()).getText());
  await single.selectByIndex(0);  ## Pick by position, counting from 0.
  console.log('now: ' + await (await single.getFirstSelectedOption()).getText());
  const multi = new Select(await driver.findElement(By.id('multi')));  ## A select with the multiple attribute.
  console.log('multi starts with: ' + (await multi.getAllSelectedOptions()).length + ' selected');  ## Eggs and Sausages are selected in the HTML.
  await multi.deselectByValue('eggs');  ## Only multiple lists can deselect.
  await multi.selectByVisibleText('Ham');
  for (const o of await multi.getAllSelectedOptions()) console.log('  selected: ' + await o.getText());
  await driver.quit();
})();
''', expect='selected: Ham')

UPLOAD = tri('upload', 'Upload a file without the file dialog', java=r'''
import java.nio.file.Files;
import java.nio.file.Path;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

public class Upload {
    public static void main(String[] args) throws Exception {
        Path file = Files.writeString(Path.of("report.txt"), "quarterly numbers");  ## Make a small file to upload.
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/web-form.html");
        WebElement input = driver.findElement(By.name("my-file"));  ## The input with type="file".
        input.sendKeys(file.toAbsolutePath().toString());  ## Send the full path. No dialog opens, the file is simply attached.
        System.out.println("browser shows: " + input.getDomProperty("value"));  ## Browsers hide the real folder and show a made up folder called fakepath.
        driver.quit();
    }
}
''', py=r'''
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By

file = Path("report.txt")
file.write_text("quarterly numbers")  ## Make a small file to upload.
driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/web-form.html")
upload = driver.find_element(By.NAME, "my-file")  ## The input with type="file".
upload.send_keys(str(file.resolve()))  ## Send the full path. No dialog opens, the file is simply attached.
print("browser shows:", upload.get_property("value"))  ## Browsers hide the real folder and show a made up folder called fakepath.
driver.quit()
''', js=r'''
const fs = require('fs');
const path = require('path');
const { Builder, Browser, By } = require('selenium-webdriver');

(async function upload() {
  fs.writeFileSync('report.txt', 'quarterly numbers');  ## Make a small file to upload.
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/web-form.html');
  const input = await driver.findElement(By.name('my-file'));  ## The input with type="file".
  await input.sendKeys(path.resolve('report.txt'));  ## Send the full path. No dialog opens, the file is simply attached.
  console.log('browser shows: ' + await input.getProperty('value'));  ## Browsers hide the real folder and show a made up folder called fakepath.
  await driver.quit();
})();
''', expect='fakepath')

K.lesson('commands', 'Click, type and clear', f'''
<p>The documentation says there are only five basic commands for an element: <b>click</b>, <b>send keys</b>, <b>clear</b>, <b>submit</b> and <b>select</b>. Almost every form you will ever test needs nothing more.</p>
{table(['Command', 'Works on', 'Watch out for'], [
    ['click', 'Any element', 'It clicks the centre of the element. If something else is on top there, you get element click intercepted.'],
    ['send keys', 'Text fields and other keyboard interactable elements', 'It adds to the existing text. Clear first if you want to replace it.'],
    ['clear', 'Editable, resettable elements: text inputs and content editable', 'Readonly and disabled inputs give invalid element state.'],
    ['submit', 'Form elements', 'In Selenium 4 it runs a script, so the documentation recommends clicking the submit button instead.'],
    ['select', 'select and option elements', 'Use the Select class, covered below.']])}
{FORM}
<h3>Two checks before every action</h3>
<p>These commands copy what a user can do, so the driver does two things first. It <b>scrolls the element into view</b> if it is outside the viewport, lining up its bottom with the bottom of the viewport. Then it checks that the element is <b>interactable</b>: displayed, with a size, and able to receive the pointer or the keyboard. If not, you get <code>element not interactable</code>.</p>
{viz('se-click')}
{ERRS}
<p>Each error tells you something different. <b>element not interactable</b>: the element cannot take this action at all, here because it is disabled. <b>invalid element state</b>: the element exists and is visible, but its state forbids the action, here readonly. <b>element click intercepted</b>: the element is fine, but something else lies on top of it.</p>
{scene('the cookie banner that broke every test', '<p>A shop adds a cookie consent banner on Monday. On Tuesday half the checkout tests fail with element click intercepted. Nothing was wrong with the checkout: the banner covered the bottom of every page. The fix was one step at the start of each test that clicks Accept on the banner, or sets the consent cookie before the first page loads. Reading the "Other element would receive the click" part of the message points straight at the cause.</p>')}
''', kw=['click', 'send keys', 'clear', 'submit', 'element not interactable', 'element click intercepted', 'invalid element state', 'scroll into view', 'interactable', 'checkbox', 'radio button'])

K.lesson('info', 'Read information about an element', f'''
<p>Tests do two things: act, then check. Checking means asking the element questions.</p>
{table(['Question', 'Java', 'Python', 'JavaScript'], [
    ['Is it displayed?', '<code>isDisplayed()</code>', '<code>is_displayed()</code>', '<code>isDisplayed()</code>'],
    ['Is it enabled?', '<code>isEnabled()</code>', '<code>is_enabled()</code>', '<code>isEnabled()</code>'],
    ['Is it selected?', '<code>isSelected()</code>', '<code>is_selected()</code>', '<code>isSelected()</code>'],
    ['Tag name', '<code>getTagName()</code>', '<code>tag_name</code>', '<code>getTagName()</code>'],
    ['Position and size', '<code>getRect()</code>', '<code>rect</code>', '<code>getRect()</code>'],
    ['Computed CSS', '<code>getCssValue(name)</code>', '<code>value_of_css_property(name)</code>', '<code>getCssValue(name)</code>'],
    ['Visible text', '<code>getText()</code>', '<code>text</code>', '<code>getText()</code>']])}
{INFO}
<h3>Attribute or property</h3>
<p>The three value lines show the difference that confuses many testers. An <b>attribute</b> is what the HTML says. A <b>property</b> is the live JavaScript value of the element right now. The text box has no value attribute in its HTML, so the DOM attribute is empty, but after typing, the value property is hello.</p>
{table(['Method', 'Reads', 'Use it for'], [
    ['get DOM attribute', 'Only the attribute in the HTML', 'Checking what the server sent, such as a data-test value'],
    ['get DOM property', 'Only the live JavaScript property', 'What is in a field now, whether a box is checked now'],
    ['get attribute (classic)', 'The property if there is one, otherwise the attribute. Selenium does this with a JavaScript atom', 'Old code. Prefer the two precise methods.']])}
{note('isDisplayed is not defined by the W3C spec, because deciding what a person can see covers too many cases. The documentation explains that Selenium runs a large JavaScript function that makes approximations. Treat it as a good guide, not a perfect one.', 'exam')}
''', kw=['is displayed', 'is enabled', 'is selected', 'tag name', 'rect', 'css value', 'text', 'attribute', 'property', 'getDomAttribute', 'getDomProperty', 'get_property'])

K.lesson('selectlists', 'Select lists', f'''
<p>A <code>&lt;select&gt;</code> drop down needs a helper: the <b>Select</b> class in the support package. Wrap the element, then choose options by visible text, by value or by index.</p>
{src('py', """<select name="selectomatic">
    <option selected="selected" id="non_multi_option" value="one">One</option>
    <option value="two">Two</option>
    <option value="four">Four</option>
    <option value="still learning how to count, apparently">Still learning how to count, apparently</option>
</select>
<select name="multi" id="multi" multiple="multiple">
    <option selected="selected" value="eggs">Eggs</option>
    <option value="ham">Ham</option>
    <option selected="selected" value="sausages">Sausages</option>
    <option value="onion gravy">Onion gravy</option>
</select>""", 'formPage.html (the two lists used here)')}
{SELECT}
{table(['Rule from the documentation', 'What it means for you'], [
    ['Select only works on select and option elements', 'Drop downs built from div or li with JavaScript need normal clicks instead'],
    ['Since Selenium 4.5 a Select cannot be created on a disabled select', 'Check isEnabled first if the list may be disabled'],
    ['Disabled options cannot be selected', 'Trying raises an error'],
    ['Only multiple lists can deselect', 'deselect on a single list raises an error']])}
''', kw=['select', 'drop down', 'select by visible text', 'select by value', 'select by index', 'multiple select', 'deselect', 'options', 'support package'])

K.lesson('upload', 'File upload', f'''
<p>Selenium cannot touch the operating system file dialog. The documentation gives the way round it: send the <b>full path</b> of the file to the <code>input type="file"</code> element with send keys. No dialog appears, and the browser attaches the file as if the user had picked it.</p>
{UPLOAD}
<p>The value the page sees starts with <code>C:\\fakepath\\</code> on every operating system. Browsers hide the real folder from web pages for privacy, so this is expected, not a bug.</p>
{note('When the test runs on a Grid, the file must reach the remote machine. The Java, Python and JavaScript bindings handle this with a file detector that uploads the file to the node first. Chapter 6.1 shows it.', 'tip')}
{ladder(
    '<p>Click, type, clear and pick from a list. Then ask the element whether it is shown, enabled, ticked and what it says.</p>',
    '<p>Before acting, the driver scrolls the element into view and checks it can be used. Errors say what was wrong: not interactable, invalid state or click intercepted. Attributes are the HTML, properties are the live value.</p>',
    '<p>Element Click aims at the in view centre point and checks the topmost element there. Element Send Keys focuses the element and dispatches key events, so page JavaScript sees real typing. File inputs are a special case where send keys sets the file list.</p>',
    '<p>Because Element Click needs the centre to be unobscured, sticky headers, overlays and animations cause most click failures. When you truly need pointer moves at exact offsets, the Actions API in chapter 4.3 skips these user like checks.</p>')}
''', kw=['file upload', 'input type file', 'send keys path', 'fakepath', 'file dialog', 'file detector'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'How many basic commands does the documentation list for an element?', ['3', '5', '8', '12'], 1,
       'click, send keys, clear, submit and...', 'Five: click, send keys, clear, submit and select.')
K.quiz('e', 'What does send keys do with text already in a field?', ['Replaces it', 'Adds to it', 'Raises an error', 'Clears it first'], 1,
       'Clear exists for a reason.', 'send keys types at the end. Call clear first to replace the content.')
K.quiz('e', 'How do you upload a file with Selenium?', ['Click the input and type in the dialog', 'send keys the full file path to the input type="file"', 'Use the Actions API', 'It is not possible'], 1,
       'No dialog.', 'Sending the full path to the file input attaches the file without the dialog.')
K.quiz('m', 'Which error do you get when a cookie banner covers the centre of a button you click?', ['no such element', 'element not interactable', 'element click intercepted', 'stale element reference'], 2,
       'Another element would receive the click.', 'The centre is obscured, so the driver answers element click intercepted.')
K.quiz('m', 'You call clear() on a readonly input. What happens?', ['It clears it', 'invalid element state', 'element click intercepted', 'Nothing'], 1,
       'The state forbids it.', 'clear needs an editable, resettable element. A readonly input gives invalid element state, as the real run shows.')
K.quiz('m', 'Why does the documentation advise clicking the submit button instead of calling submit()?', ['submit() is faster', 'In Selenium 4 submit() runs a script instead of a separate endpoint', 'submit() is removed', 'Buttons cannot be clicked'], 1,
       'How is it implemented?', 'In Selenium 4 submit is implemented by executing a script, so clicking the real button is closer to the user.')
K.quiz('m', 'A text box has no value attribute in its HTML and you typed "hello". What does get DOM attribute "value" return?', ['hello', 'An empty value (null or None)', 'value', 'An error'], 1,
       'Attribute means HTML.', 'The DOM attribute only reflects the HTML, which has no value. The property holds hello.')
K.quiz('h', 'Which of these can the Select class NOT handle?', ['A single select', 'A multiple select', 'A drop down built from div and li with JavaScript', 'Selecting by value'], 2,
       'It needs real select elements.', 'The documentation says Select only works for select and option elements.')
K.quiz('h', 'Which method can deselect an option?', ['Any Select', 'Only a Select on a list with the multiple attribute', 'Only selectByIndex', 'None'], 1,
       'Single lists always have one choice.', 'Only multiple select lists can have options deselected.')
K.quiz('x', 'Why is isDisplayed implemented with a JavaScript atom instead of a W3C command?', ['W3C forgot it', 'Displayedness could not be fully defined in the spec, so Selenium uses a large approximating function', 'It is faster', 'Browsers forbid it'], 1,
       'Too many cases.', 'The documentation says it is mentioned but not defined by the W3C spec, so Selenium executes a large JavaScript function.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A select list has 4 options. What is the highest index you can pass to selectByIndex?', '3', 'Counting starts at 0.',
       ['Indexes are 0, 1, 2 and 3.', 'The highest is one less than the count.', eq('4 − 1 = 3')], check=3)
K.calc('e', 'A field holds "Jane". You call send keys " Doe" without clear. How many characters does it hold now?', '8', 'send keys appends.',
       ['"Jane" has 4 characters.', '" Doe" has 4 characters, counting the space.', eq('4 + 4 = 8 characters: "Jane Doe"')], check=8)
K.calc('m', 'A multiple list starts with Eggs and Sausages selected. You deselect eggs and select Ham. How many options are selected?', '2', 'Track the set.',
       ['Start: Eggs, Sausages.', 'Deselect eggs: Sausages.', eq('Select Ham: Sausages, Ham = 2')], check=2)
K.calc('m', 'A button is 120 px wide and 40 px tall, with its top left at (300, 500). Where does Element Click aim? Give the x value.', '360', 'The centre.',
       ['Centre x = left + width ÷ 2.', '300 + 120 ÷ 2 = 300 + 60.', eq('x = 360 (and y = 500 + 20 = 520)')], check=360)
K.calc('h', 'The viewport is 625 px tall and a button with its top at 900 px and height 40 px is below it. The driver lines up the bottom of the element with the bottom of the viewport. By how many px does it scroll?', '315', 'Bottom of element minus viewport height.',
       ['Bottom of the button: 900 + 40 = 940 px.', 'After scrolling, that must sit at 625 px.', eq('940 − 625 = 315 px')], check=315, unit='px')
K.calc('x', 'A checkout test clicks 12 buttons. A banner covers 3 of them. If each failure stops the test, how many clicks run before the first failure if the covered ones are buttons 5, 8 and 11?', '4', 'Stop at the first problem.',
       ['Buttons 1 to 4 click fine.', 'Button 5 raises element click intercepted.', eq('4 successful clicks, then the test stops')], check=4)

# ---------------------------------------------------------------- assignments
K.assign('which_error', 'm', 'Predict the interaction error',
         '<p>Write <code>result(action, state)</code>. <code>action</code> is "click", "type" or "clear". <code>state</code> is one of "ok", "hidden", "disabled", "readonly" or "covered". Return "ok" or the W3C error name, following the real runs on this page: hidden or disabled with type gives "element not interactable", hidden with click or clear also gives "element not interactable", readonly with clear gives "invalid element state", covered with click gives "element click intercepted". Every other pair returns "ok".</p>',
         '''
def result(action, state):
    # your code here
    pass
''', [('result("type", "disabled")', 'element not interactable'), ('result("clear", "readonly")', 'invalid element state'), ('result("click", "covered")', 'element click intercepted'), ('result("click", "hidden")', 'element not interactable'), ('result("type", "ok")', 'ok'), ('result("type", "readonly")', 'ok')],
         '''
def result(action, state):
    if state == "hidden":
        return "element not interactable"
    if action == "type" and state == "disabled":
        return "element not interactable"
    if action == "clear" and state == "readonly":
        return "invalid element state"
    if action == "click" and state == "covered":
        return "element click intercepted"
    return "ok"
''', 'Check hidden first, because it fails for every action.', '<p>Typing into a readonly field raised no error in the real run, but nothing is typed either. That is why a good test reads the value back afterwards.</p>')
K.assign('centre', 'e', 'Where does a click land?',
         '<p>Write <code>centre(rect)</code>. <code>rect</code> is a dict with x, y, width and height. Return the point <code>(cx, cy)</code> that Element Click aims at.</p>',
         '''
def centre(rect):
    # your code here
    pass
''', [('centre({"x": 300, "y": 500, "width": 120, "height": 40})', (360.0, 520.0)), ('centre({"x": 8, "y": 110, "width": 201, "height": 39})', (108.5, 129.5))],
         '''
def centre(rect):
    return (rect["x"] + rect["width"] / 2, rect["y"] + rect["height"] / 2)
''', 'Half the width and half the height.', '<p>The second rect is the real First name box from chapter 3.1, so its centre has halves.</p>')

K.must('Five commands', 'click, send keys, clear, submit and select. Prefer clicking the submit button over submit(). send keys appends, so clear first.')
K.must('Built in checks', 'Before acting the driver scrolls the element into view and checks it is interactable. Errors: element not interactable, invalid element state, element click intercepted.')
K.must('Element information', 'isDisplayed, isEnabled, isSelected, tag name, rect, CSS value and text. isDisplayed is a JavaScript approximation.')
K.must('Attribute vs property', 'DOM attribute is the HTML, DOM property is the live value. The classic getAttribute mixes both.')
K.must('Select and upload', 'Select works only on select elements: by visible text, value or index. Upload by sending the full path to input type="file".')

T = K.topic(
    slug='interacting', topic='interacting',
    step=(3, 'Find and use elements', 'se-elements', 'Locators, finding elements, interacting with inputs, reading element information, select lists and file upload.', 'Beginner'),
    title='Interacting with elements and reading them', short='Interact and inspect', badge='3.3', minutes=55, added='2026-10-29',
    lead='Fill in forms with click, type and clear, understand the checks the driver makes before each action and the errors they give, read what an element knows about itself, and handle select lists and file uploads.',
    desc='The five element commands, scrolling into view and interactability, real element not interactable, invalid element state and element click intercepted errors, an animation of Element Click, displayed, enabled, selected, rect, CSS and text, DOM attribute versus property with a real run, the Select class for single and multiple lists, and file upload without the dialog.',
    summary='Click, type, clear, the checks before every action and their errors, element information, select lists and uploads.',
    keywords=['click', 'send keys', 'clear', 'select', 'upload', 'is displayed', 'attribute', 'property', 'interactable', 'intercepted'],
    recap='<p>Elements take five commands. The driver scrolls them into view and checks they are interactable first, and each failure has its own error. Read state with isDisplayed, isEnabled, isSelected, text and rect, and prefer DOM attribute or DOM property over the classic getAttribute. Use Select for select lists and send keys with a full path for uploads.</p>')
