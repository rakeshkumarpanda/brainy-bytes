# Chapter 4.3: the Actions API. Sources: selenium.dev documentation (Actions API, Mouse actions, Keyboard actions,
# Scroll wheel actions), the W3C WebDriver specification (Actions, input sources, ticks, Perform Actions and Release
# Actions), the binding sources in box/ (default move durations, clear and reset methods) and real runs on the Selenium
# test pages mouse_interaction.html, single_text_input.html and scrolling_tests/.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, src, flow

K = Kit()

MOUSE = tri('mouse', 'Double click, right click, hover, drag and drop, and move to a point', java=r'''
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.interactions.Actions;

public class Mouse {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/mouse_interaction.html");
        WebElement box = driver.findElement(By.id("clickable"));
        new Actions(driver).doubleClick(box).perform();  ## Build a chain, then perform() sends it to the browser in one request.
        System.out.println("double: " + driver.findElement(By.id("click-status")).getText());
        new Actions(driver).contextClick(box).perform();  ## A right click.
        System.out.println("right: " + driver.findElement(By.id("click-status")).getText());
        new Actions(driver).moveToElement(driver.findElement(By.id("hover"))).perform();  ## Move to the centre of the element. Nothing is clicked.
        System.out.println("hover: " + driver.findElement(By.id("move-status")).getText());
        WebElement from = driver.findElement(By.id("draggable"));
        WebElement to = driver.findElement(By.id("droppable"));
        new Actions(driver).dragAndDrop(from, to).perform();  ## Move to from, press, move to to, release.
        System.out.println("drag: " + driver.findElement(By.id("drop-status")).getText());
        new Actions(driver).moveToLocation(8, 12).perform();  ## A point measured from the top left of the viewport.
        System.out.println("at: " + driver.findElement(By.id("absolute-location")).getText());
        new Actions(driver).moveByOffset(13, 15).perform();  ## From wherever the pointer is now. The driver remembered it between chains.
        System.out.println("moved by: " + driver.findElement(By.id("absolute-location")).getText());
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/mouse_interaction.html")
box = driver.find_element(By.ID, "clickable")
ActionChains(driver).double_click(box).perform()  ## Build a chain, then perform() sends it to the browser in one request.
print("double:", driver.find_element(By.ID, "click-status").text)
ActionChains(driver).context_click(box).perform()  ## A right click.
print("right:", driver.find_element(By.ID, "click-status").text)
ActionChains(driver).move_to_element(driver.find_element(By.ID, "hover")).perform()  ## Move to the centre of the element. Nothing is clicked.
print("hover:", driver.find_element(By.ID, "move-status").text)
source = driver.find_element(By.ID, "draggable")
target = driver.find_element(By.ID, "droppable")
ActionChains(driver).drag_and_drop(source, target).perform()  ## Move to source, press, move to target, release.
print("drag:", driver.find_element(By.ID, "drop-status").text)
builder = ActionBuilder(driver)  ## The lower level builder. Python has no move_to_location on ActionChains.
builder.pointer_action.move_to_location(8, 12)  ## A point measured from the top left of the viewport.
builder.perform()
print("at:", driver.find_element(By.ID, "absolute-location").text)
ActionChains(driver).move_by_offset(13, 15).perform()  ## From wherever the pointer is now. The driver remembered it between chains.
print("moved by:", driver.find_element(By.ID, "absolute-location").text)
driver.quit()
''', js=r'''
const { Builder, Browser, By, Origin } = require('selenium-webdriver');

(async function mouse() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/mouse_interaction.html');
  const box = await driver.findElement(By.id('clickable'));
  await driver.actions().doubleClick(box).perform();  ## Build a chain, then perform() sends it to the browser in one request.
  console.log('double: ' + await driver.findElement(By.id('click-status')).getText());
  await driver.actions().contextClick(box).perform();  ## A right click.
  console.log('right: ' + await driver.findElement(By.id('click-status')).getText());
  await driver.actions().move({ origin: await driver.findElement(By.id('hover')) }).perform();  ## Move to the centre of the element. Nothing is clicked.
  console.log('hover: ' + await driver.findElement(By.id('move-status')).getText());
  const from = await driver.findElement(By.id('draggable'));
  const to = await driver.findElement(By.id('droppable'));
  await driver.actions().dragAndDrop(from, to).perform();  ## Move to from, press, move to to, release.
  console.log('drag: ' + await driver.findElement(By.id('drop-status')).getText());
  await driver.actions().move({ x: 8, y: 12 }).perform();  ## With no origin, x and y are measured from the top left of the viewport.
  console.log('at: ' + await driver.findElement(By.id('absolute-location')).getText());
  await driver.actions().move({ x: 13, y: 15, origin: Origin.POINTER }).perform();  ## From wherever the pointer is now. The driver remembered it between chains.
  console.log('moved by: ' + await driver.findElement(By.id('absolute-location')).getText());
  await driver.quit();
})();
''', expect='drag: dropped')

KEYS = tri('keys', 'Hold Shift, select all with the right modifier, and type into an element', java=r'''
import org.openqa.selenium.By;
import org.openqa.selenium.Keys;
import org.openqa.selenium.Platform;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.interactions.Actions;

public class KeyboardActions {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/single_text_input.html");
        WebElement input = driver.findElement(By.id("textInput"));
        new Actions(driver)
            .keyDown(Keys.SHIFT)  ## Press Shift and keep holding it.
            .sendKeys("abc")  ## Goes to the element that has focus. The page focuses this box on load.
            .keyUp(Keys.SHIFT)  ## Let go of Shift.
            .sendKeys("def")
            .perform();
        System.out.println("typed: " + input.getAttribute("value"));
        Keys cmdCtrl = Platform.getCurrent().is(Platform.MAC) ? Keys.COMMAND : Keys.CONTROL;  ## Select all is Command A on a Mac and Control A elsewhere.
        new Actions(driver).keyDown(cmdCtrl).sendKeys("a").keyUp(cmdCtrl).sendKeys(Keys.BACK_SPACE).perform();
        System.out.println("after select all and delete: '" + input.getAttribute("value") + "'");
        new Actions(driver).sendKeys(input, "Selenium!").perform();  ## Clicks the element first, then types.
        System.out.println("typed into element: " + input.getAttribute("value"));
        driver.quit();
    }
}
''', py=r'''
import sys
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/single_text_input.html")
box = driver.find_element(By.ID, "textInput")
ActionChains(driver) \
    .key_down(Keys.SHIFT) \
    .send_keys("abc") \
    .key_up(Keys.SHIFT) \
    .send_keys("def") \
    .perform()  ## Shift is held for abc only. send_keys goes to the box that has focus.
print("typed:", box.get_attribute("value"))
cmd_ctrl = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL  ## Select all is Command A on a Mac and Control A elsewhere.
ActionChains(driver).key_down(cmd_ctrl).send_keys("a").key_up(cmd_ctrl).send_keys(Keys.BACKSPACE).perform()
print("after select all and delete: '" + box.get_attribute("value") + "'")
ActionChains(driver).send_keys_to_element(box, "Selenium!").perform()  ## Clicks the element first, then types.
print("typed into element:", box.get_attribute("value"))
driver.quit()
''', js=r'''
const { Builder, Browser, By, Key } = require('selenium-webdriver');

(async function keyboard() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/single_text_input.html');
  const input = await driver.findElement(By.id('textInput'));
  await driver.actions()
    .keyDown(Key.SHIFT)  ## Press Shift and keep holding it.
    .sendKeys('abc')  ## Goes to the element that has focus. The page focuses this box on load.
    .keyUp(Key.SHIFT)  ## Let go of Shift.
    .sendKeys('def')
    .perform();
  console.log('typed: ' + await input.getAttribute('value'));
  const cmdCtrl = process.platform === 'darwin' ? Key.COMMAND : Key.CONTROL;  ## Select all is Command A on a Mac and Control A elsewhere.
  await driver.actions().keyDown(cmdCtrl).sendKeys('a').keyUp(cmdCtrl).sendKeys(Key.BACK_SPACE).perform();
  console.log("after select all and delete: '" + await input.getAttribute('value') + "'");
  await driver.actions().click(input).sendKeys('Selenium!').perform();  ## JavaScript has no send keys to element in actions, so click first, then type.
  console.log('typed into element: ' + await input.getAttribute('value'));
  await driver.quit();
})();
''', expect='typed: ABCdef')

WHEEL = tri('wheel', 'Scroll to an element, by an amount, and inside a frame', java=r'''
import java.time.Duration;
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.interactions.Actions;
import org.openqa.selenium.interactions.WheelInput;
import org.openqa.selenium.support.ui.WebDriverWait;

public class Wheel {
    static final String IN_VIEW = "const r = arguments[0].getBoundingClientRect(); return r.top >= 0 && r.bottom <= window.innerHeight;";

    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        JavascriptExecutor js = (JavascriptExecutor) driver;
        driver.get("https://www.selenium.dev/selenium/web/scrolling_tests/frame_with_nested_scrolling_frame_out_of_view.html");
        WebElement frame = driver.findElement(By.tagName("iframe"));  ## The page starts with a 5000 px tall block, so the iframe is far below.
        System.out.println("frame in view before: " + js.executeScript(IN_VIEW, frame));
        new Actions(driver).scrollToElement(frame).perform();  ## Scroll until the bottom of the element is in view.
        System.out.println("frame in view after: " + js.executeScript(IN_VIEW, frame));
        driver.get("https://www.selenium.dev/selenium/web/scrolling_tests/frame_with_nested_scrolling_frame_out_of_view.html");  ## Load it again. A refresh would keep the scroll position.
        new Actions(driver).scrollByAmount(0, 300).perform();  ## Like turning the wheel: 300 px down from the top left of the viewport.
        System.out.println("scrollY right after perform: " + js.executeScript("return window.scrollY"));
        new WebDriverWait(driver, Duration.ofSeconds(2)).until(d -> ((Number) js.executeScript("return window.scrollY")).intValue() >= 300);  ## The scroll can land after perform returns, so wait for it.
        System.out.println("scrollY after waiting: " + js.executeScript("return window.scrollY"));
        driver.get("https://www.selenium.dev/selenium/web/scrolling_tests/frame_with_nested_scrolling_frame.html");
        WebElement inner = driver.findElement(By.tagName("iframe"));
        new Actions(driver).scrollFromOrigin(WheelInput.ScrollOrigin.fromElement(inner), 0, 200).perform();  ## Turn the wheel with the pointer over the frame, so the frame scrolls.
        driver.switchTo().frame(inner);
        new WebDriverWait(driver, Duration.ofSeconds(2)).until(d -> ((Number) js.executeScript("return window.scrollY")).intValue() > 0);
        System.out.println("frame scrollY: " + js.executeScript("return window.scrollY") + " of at most " + js.executeScript("return document.documentElement.scrollHeight - window.innerHeight"));
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

IN_VIEW = "const r = arguments[0].getBoundingClientRect(); return r.top >= 0 && r.bottom <= window.innerHeight;"
driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/scrolling_tests/frame_with_nested_scrolling_frame_out_of_view.html")
frame = driver.find_element(By.TAG_NAME, "iframe")  ## The page starts with a 5000 px tall block, so the iframe is far below.
print("frame in view before:", driver.execute_script(IN_VIEW, frame))
ActionChains(driver).scroll_to_element(frame).perform()  ## Scroll until the bottom of the element is in view.
print("frame in view after:", driver.execute_script(IN_VIEW, frame))
driver.get("https://www.selenium.dev/selenium/web/scrolling_tests/frame_with_nested_scrolling_frame_out_of_view.html")  ## Load it again. A refresh would keep the scroll position.
ActionChains(driver).scroll_by_amount(0, 300).perform()  ## Like turning the wheel: 300 px down from the top left of the viewport.
print("scrollY right after perform:", driver.execute_script("return window.scrollY"))
WebDriverWait(driver, 2).until(lambda d: d.execute_script("return window.scrollY") >= 300)  ## The scroll can land after perform returns, so wait for it.
print("scrollY after waiting:", driver.execute_script("return window.scrollY"))
driver.get("https://www.selenium.dev/selenium/web/scrolling_tests/frame_with_nested_scrolling_frame.html")
inner = driver.find_element(By.TAG_NAME, "iframe")
ActionChains(driver).scroll_from_origin(ScrollOrigin.from_element(inner), 0, 200).perform()  ## Turn the wheel with the pointer over the frame, so the frame scrolls.
driver.switch_to.frame(inner)
WebDriverWait(driver, 2).until(lambda d: d.execute_script("return window.scrollY") > 0)
print("frame scrollY:", driver.execute_script("return window.scrollY"), "of at most", driver.execute_script("return document.documentElement.scrollHeight - window.innerHeight"))
driver.quit()
''', js=r'''
const { Builder, Browser, By } = require('selenium-webdriver');

const IN_VIEW = 'const r = arguments[0].getBoundingClientRect(); return r.top >= 0 && r.bottom <= window.innerHeight;';
(async function wheel() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/scrolling_tests/frame_with_nested_scrolling_frame_out_of_view.html');
  const frame = await driver.findElement(By.tagName('iframe'));  ## The page starts with a 5000 px tall block, so the iframe is far below.
  console.log('frame in view before: ' + await driver.executeScript(IN_VIEW, frame));
  await driver.actions().scroll(0, 0, 0, 0, frame).perform();  ## scroll(x, y, deltaX, deltaY, origin). With an element as origin and no delta, it scrolls the element into view.
  console.log('frame in view after: ' + await driver.executeScript(IN_VIEW, frame));
  await driver.get('https://www.selenium.dev/selenium/web/scrolling_tests/frame_with_nested_scrolling_frame_out_of_view.html');  ## Load it again. A refresh would keep the scroll position.
  await driver.actions().scroll(0, 0, 0, 300).perform();  ## Like turning the wheel: 300 px down from the top left of the viewport.
  console.log('scrollY right after perform: ' + await driver.executeScript('return window.scrollY'));
  await driver.wait(async () => (await driver.executeScript('return window.scrollY')) >= 300, 2000);  ## The scroll can land after perform returns, so wait for it.
  console.log('scrollY after waiting: ' + await driver.executeScript('return window.scrollY'));
  await driver.get('https://www.selenium.dev/selenium/web/scrolling_tests/frame_with_nested_scrolling_frame.html');
  const inner = await driver.findElement(By.tagName('iframe'));
  await driver.actions().scroll(0, 0, 0, 200, inner).perform();  ## Turn the wheel with the pointer over the frame, so the frame scrolls.
  await driver.switchTo().frame(inner);
  await driver.wait(async () => (await driver.executeScript('return window.scrollY')) > 0, 2000);
  console.log('frame scrollY: ' + await driver.executeScript('return window.scrollY') + ' of at most ' + await driver.executeScript('return document.documentElement.scrollHeight - window.innerHeight'));
  await driver.quit();
})();
''', expect='frame in view after: ')

PAYLOAD = '''{"actions": [
  {"type": "pointer", "id": "mouse", "parameters": {"pointerType": "mouse"},
   "actions": [
     {"type": "pointerMove", "duration": 250, "x": 0, "y": 0, "origin": {"element-6066-...": "...e.3"}},
     {"type": "pointerDown", "duration": 0, "button": 0},
     {"type": "pointerMove", "duration": 250, "x": 0, "y": 0, "origin": {"element-6066-...": "...e.4"}},
     {"type": "pointerUp", "duration": 0, "button": 0}]},
  {"type": "key", "id": "key",
   "actions": [
     {"type": "pause", "duration": 0}, {"type": "pause", "duration": 0},
     {"type": "pause", "duration": 0}, {"type": "pause", "duration": 0}]}
]}'''

K.lesson('mouse', 'How actions work, and the mouse', f'''
<p>Most tests only need <code>click()</code> and <code>sendKeys()</code> on an element. Some things a real user does cannot be said with those: a double click, a right click, hovering to open a menu, dragging a card to another column, holding Shift while typing, or turning the mouse wheel. The <b>Actions API</b> is the low level way to describe exactly what the input devices do.</p>
<p>You build a chain of steps and then call <code>perform()</code>. Only then is a request sent. The binding turns the chain into one <code>POST /session/{{id}}/actions</code> request. This is the body Python really sent for <code>drag_and_drop</code> in the run below, with the element ids shortened:</p>
{src('js', PAYLOAD, 'POST /session/{id}/actions')}
<p>There is one list per <b>input source</b>: a pointer (mouse, pen or touch), a key source and a wheel. The W3C spec runs the lists together, one column at a time. Each column is called a <b>tick</b>. A tick lasts as long as the slowest action in it. Python filled the key list with pauses so that both lists have four ticks.</p>
{viz('se-ticks')}
{MOUSE}
<p>The pointer position is kept by the driver between chains. That is why <code>move by offset (13, 15)</code> after <code>move to location (8, 12)</code> printed 21, 27. The driver keeps pressed keys and buttons too, until the chain releases them or the test calls <b>release actions</b>.</p>
{table(['Mouse action', 'Java', 'Python', 'JavaScript'], [
    ['Double click', '<code>doubleClick(el)</code>', '<code>double_click(el)</code>', '<code>doubleClick(el)</code>'],
    ['Right click', '<code>contextClick(el)</code>', '<code>context_click(el)</code>', '<code>contextClick(el)</code>'],
    ['Hover', '<code>moveToElement(el)</code>', '<code>move_to_element(el)</code>', '<code>move({{origin: el}})</code>'],
    ['Press and hold', '<code>clickAndHold(el)</code>', '<code>click_and_hold(el)</code>', '<code>press()</code>'],
    ['Drag and drop', '<code>dragAndDrop(a, b)</code>', '<code>drag_and_drop(a, b)</code>', '<code>dragAndDrop(a, b)</code>'],
    ['Point in the viewport', '<code>moveToLocation(x, y)</code>', '<code>ActionBuilder</code> then <code>move_to_location(x, y)</code>', '<code>move({{x, y}})</code>'],
    ['From the current point', '<code>moveByOffset(x, y)</code>', '<code>move_by_offset(x, y)</code>', '<code>move({{x, y, origin: Origin.POINTER}})</code>'],
    ['Release everything', '<code>((RemoteWebDriver) driver).resetInputState()</code>', '<code>ActionBuilder(driver).clear_actions()</code>', '<code>actions().clear()</code>']])}
{note('A pointer move has a duration. In the bindings used here, Python uses 250 ms by default and JavaScript 100 ms. Some drag libraries ignore a move that takes 0 ms, so if a drag does nothing, try a chain with a longer move.', 'tip')}
{scene('a Kanban board', '<p>A task board lets a user drag a card from To do to Done. element.click() cannot express that. The test finds the card and the Done column, calls drag and drop, then checks that the card is now inside the Done column. When the board is built with a library that needs several mouse moves, the test builds the chain by hand: click and hold the card, move by an offset, move to the column, release.</p>')}
''', kw=['actions api', 'action chains', 'perform', 'ticks', 'input source', 'double click', 'context click', 'right click', 'hover', 'drag and drop', 'move to element', 'move by offset', 'release actions'])

K.lesson('keyboard', 'Keyboard actions', f'''
<p>A key source sends <b>keyDown</b> and <b>keyUp</b>. <code>sendKeys("abc")</code> inside a chain becomes a key down and key up for every character. Special keys such as Shift, Control, Enter and Backspace are characters from a private Unicode range. Shift is U+E008, Control is U+E009 and Enter is U+E007, which you can see in the payload of the Shift plan in the animation above.</p>
{KEYS}
<p>Look at the first line of output. Shift was held for <code>abc</code> and released before <code>def</code>, so the box shows capitals only for the first three letters. The second line shows an empty value: Control A selected everything and Backspace deleted it. On a Mac that shortcut uses Command, which is why the code picks the key from the platform.</p>
{table(['Key method', 'What it does'], [
    ['keyDown(key)', 'Press a key and keep it down. Meant for modifier keys.'],
    ['keyUp(key)', 'Release it. Forget this and the key stays down for the next chain.'],
    ['sendKeys(text)', 'Type into whatever has focus, one key down and key up per character.'],
    ['sendKeys(element, text)', 'Click the element first, then type. Java and Python only.']])}
{note('Actions type into the focused element. If nothing has focus, the keys go to the page body and the test seems to type into nothing. Element sendKeys focuses the element itself, which is why it is the better choice for plain typing.', 'warn')}
''', kw=['keyboard actions', 'key down', 'key up', 'shift', 'control', 'command', 'select all', 'send keys', 'special keys', 'unicode keys'])

K.lesson('wheel', 'Scroll wheel actions', f'''
<p>The wheel source turns the mouse wheel. The documentation offers three cases: scroll an element into view, scroll by an amount, and scroll by an amount starting from a point or an element. The last one matters when only part of the page scrolls, such as a frame or a list with its own scroll bar.</p>
{WHEEL}
<p>The output has two lessons. First, the frame was out of view and became visible after scroll to element. Second, scroll by amount is a real wheel event. In the Python and JavaScript runs the page had not moved yet when perform() returned and read 0. In the Java run it had already moved. The timing varies from run to run, and every language read 300 after the wait. Treat a scroll like any other change on the page and wait for its result. The last line shows that asking the frame to scroll 200 px moved it only as far as its content allows.</p>
{table(['Wheel action', 'Java', 'Python', 'JavaScript'], [
    ['Into view', '<code>scrollToElement(el)</code>', '<code>scroll_to_element(el)</code>', '<code>scroll(0, 0, 0, 0, el)</code>'],
    ['By an amount', '<code>scrollByAmount(0, 300)</code>', '<code>scroll_by_amount(0, 300)</code>', '<code>scroll(0, 0, 0, 300)</code>'],
    ['From an element', '<code>scrollFromOrigin(ScrollOrigin.fromElement(el), 0, 200)</code>', '<code>scroll_from_origin(ScrollOrigin.from_element(el), 0, 200)</code>', '<code>scroll(0, 0, 0, 200, el)</code>']])}
{scene('an endless product feed', '<p>A shop loads 20 more products each time the user reaches the bottom of the list. The test counts the products, scrolls the last one into view with the wheel, waits until the count grows, and repeats until it finds the product it needs. Scrolling with JavaScript would move the page without firing the wheel events some feeds listen for, so the wheel action is closer to a real user.</p>')}
{ladder(
    '<p>Actions let a test do what a person does with a mouse and keyboard: double click, right click, hover, drag, hold Shift and scroll.</p>',
    '<p>Build a chain, then call perform(). Each device is an input source. The browser runs the steps tick by tick, and waits for the slowest step in each tick.</p>',
    '<p>Perform Actions takes a list of input sources, each with a list of actions. Pointer moves have durations and origins: the viewport, the current pointer or an element centre. The driver keeps the input state between calls until Release Actions resets it.</p>',
    '<p>Because a whole chain is one request, timing inside it is exact and does not suffer from network delay between steps. Moves with a duration are broken into several pointer events, which is what some drag and drop and drawing libraries need.</p>')}
''', kw=['scroll', 'wheel', 'scroll to element', 'scroll by amount', 'scroll from origin', 'infinite scroll', 'scroll origin'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'When does an action chain reach the browser?', ['When each step is added', 'When perform() is called', 'When the test ends', 'When the page loads'], 1,
       'Building is local.', 'The chain is built in your code and sent in one request when perform() is called.')
K.quiz('e', 'Which action opens a right click menu?', ['doubleClick', 'contextClick', 'clickAndHold', 'moveToElement'], 1,
       'Context menu.', 'contextClick, or context_click in Python, is a right click.')
K.quiz('e', 'Which action hovers over an element without clicking it?', ['click', 'moveToElement', 'dragAndDrop', 'sendKeys'], 1,
       'Only move.', 'moveToElement moves the pointer to the centre of the element and presses nothing.')
K.quiz('m', 'In the payload for drag and drop, why does the key source have four pauses?', ['To slow the drag down', 'So every input source has the same number of ticks', 'Because Shift is pressed', 'It is a bug'], 1,
       'Ticks line up by column.', 'The binding pads every input source so that each has one action per tick.')
K.quiz('m', 'A tick has a pointer move of 250 ms and a key pause of 0 ms. How long does the tick last?', ['0 ms', '125 ms', '250 ms', '250 ms plus network time'], 2,
       'The slowest one.', 'A tick lasts as long as its longest action.')
K.quiz('m', 'You call key down Shift and never key up. What happens to the next chain?', ['Shift is released automatically', 'Shift is still held', 'An error is raised', 'The page reloads'], 1,
       'The driver keeps input state.', 'Pressed keys stay down until released or until Release Actions resets the state.')
K.quiz('m', 'In the run, move to location (8, 12) and then move by offset (13, 15). Where is the pointer?', ['13, 15', '8, 12', '21, 27', '0, 0'], 2,
       'Add them.', 'Move by offset starts from the current position: 8 + 13 and 12 + 15.')
K.quiz('h', 'scroll by amount returned, but window.scrollY was still 0. What should the test do?', ['Fail', 'Wait until scrollY reaches the target', 'Scroll again', 'Use a bigger number'], 1,
       'It is a change on the page.', 'The scroll can land just after perform() returns, so wait for the result like any other change.')
K.quiz('h', 'Which actions method types into the element that already has focus?', ['sendKeys(text)', 'sendKeys(element, text)', 'keyDown(text)', 'click(text)'], 0,
       'No element given.', 'Without an element, keys go to whatever has focus.')
K.quiz('x', 'A list scrolls inside its own box. Which wheel action scrolls the list and not the page?', ['scroll by amount', 'scroll from origin with the list as origin', 'scroll to element on the page body', 'move by offset'], 1,
       'Where is the pointer?', 'The wheel scrolls whatever is under the pointer, so start from the list element.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A drag and drop chain has ticks of 250, 0, 250 and 0 ms. How long does the chain take at least, in ms?', '500', 'Add the ticks.',
       ['Tick 1 moves to the source: 250 ms.', 'Tick 2 presses, tick 4 releases: 0 ms each.', eq('250 + 0 + 250 + 0 = 500 ms')], check=500, unit='ms')
K.calc('e', 'How many key actions does send_keys("abc") add to the key source?', '6', 'Down and up.',
       ['Each character is one key down and one key up.', 'There are 3 characters.', eq('3 × 2 = 6 actions')], check=6)
K.calc('m', 'A chain holds Shift, types "ab" and releases Shift. How many ticks does it have?', '6', 'Count the key actions.',
       ['Shift down: 1.', 'a and b: 2 actions each, so 4.', eq('1 + 4 + 1 = 6 ticks')], check=6)
K.calc('m', 'The pointer is at (8, 12). You move by offset (13, 15) and then by (−5, 10). Where is the pointer x?', '16', 'Add offsets.',
       ['After the first move x is 8 + 13 = 21.', 'Then 21 − 5.', eq('x = 16')], check=16)
K.calc('h', 'An element is 202 px wide and its left edge is at x = 18. Move to element puts the pointer at the centre. What is the x of the pointer?', '119', 'Half the width.',
       ['Half of 202 is 101.', 'The centre is the left edge plus half the width.', eq('18 + 101 = 119')], check=119)
K.calc('x', 'A feed loads 20 products each time you reach the bottom. A test needs product number 95 and starts with 20 loaded. How many wheel scrolls to the bottom does it need, at least?', '4', 'Loads of 20.',
       ['After n loads there are 20 + 20n products.', 'Need 20 + 20n ≥ 95, so 20n ≥ 75.', eq('n ≥ 3.75, so n = 4')], check=4)

# ---------------------------------------------------------------- assignments
K.assign('ticklen', 'e', 'How long does a chain take?',
         '<p>Write <code>chain_ms(sources)</code>. <code>sources</code> is a list of input sources, and each source is a list of durations in ms, one per tick. All sources have the same length. Return the total time: the sum, over ticks, of the longest duration in that tick.</p>',
         '''
def chain_ms(sources):
    # your code here
    pass
''', [('chain_ms([[250, 0, 250, 0], [0, 0, 0, 0]])', 500), ('chain_ms([[100], [300]])', 300), ('chain_ms([[0, 0, 0]])', 0)],
         '''
def chain_ms(sources):
    total = 0
    for tick in zip(*sources):
        total += max(tick)
    return total
''', 'zip(*sources) gives one tuple per tick.', '<p>This is the rule from the W3C spec: all actions in a tick run together, and the tick ends when the slowest is done.</p>')
K.assign('keyseq', 'm', 'Turn text into key actions',
         '<p>Write <code>key_actions(text, shift)</code>. Return the list of key actions a binding sends for typing <code>text</code>. Each character becomes <code>("keyDown", ch)</code> then <code>("keyUp", ch)</code>. If <code>shift</code> is True, the list starts with <code>("keyDown", "SHIFT")</code> and ends with <code>("keyUp", "SHIFT")</code>.</p>',
         '''
def key_actions(text, shift):
    # your code here
    pass
''', [('key_actions("ab", False)', [('keyDown', 'a'), ('keyUp', 'a'), ('keyDown', 'b'), ('keyUp', 'b')]),
      ('key_actions("a", True)', [('keyDown', 'SHIFT'), ('keyDown', 'a'), ('keyUp', 'a'), ('keyUp', 'SHIFT')]),
      ('key_actions("", False)', [])],
         '''
def key_actions(text, shift):
    out = []
    if shift:
        out.append(("keyDown", "SHIFT"))
    for ch in text:
        out.append(("keyDown", ch))
        out.append(("keyUp", ch))
    if shift:
        out.append(("keyUp", "SHIFT"))
    return out
''', 'Add Shift down first and Shift up last.', '<p>The real payload uses the code point U+E008 in place of the word SHIFT, as the run on this page showed.</p>')

K.must('Build then perform', 'An action chain is sent in one request when perform() is called. Nothing happens before that.')
K.must('Ticks', 'Each input source has one action per tick. A tick lasts as long as its slowest action.')
K.must('Mouse', 'doubleClick, contextClick, moveToElement, clickAndHold, dragAndDrop, moveByOffset. The driver remembers the pointer position between chains.')
K.must('Keyboard', 'keyDown and keyUp for modifiers, sendKeys for text. Use Command on a Mac and Control elsewhere. Release every key you press.')
K.must('Wheel', 'scrollToElement, scrollByAmount, scrollFromOrigin. Wait for the scroll result, because it can land after perform() returns.')

T = K.topic(
    slug='actions', topic='actions',
    step=(4, 'Synchronise and control', 'se-control', 'Waits, windows, tabs, frames and alerts, the Actions API, JavaScript, cookies and print.', 'Intermediate'),
    title='The Actions API: mouse, keyboard and wheel', short='Actions API', badge='4.3', minutes=55, added='2026-10-29',
    lead='Do what a person does with a mouse, a keyboard and a scroll wheel: double click, right click, hover, drag and drop, hold Shift, and scroll inside a page or a frame.',
    desc='How action chains become one Perform Actions request with input sources and ticks, an animation of real payloads, mouse actions with real runs in Java, Python and JavaScript, keyboard actions with modifiers and select all, scroll wheel actions, and release actions.',
    summary='Mouse, keyboard and wheel actions, and how a chain becomes ticks.',
    keywords=['actions', 'action chains', 'mouse', 'keyboard', 'drag and drop', 'hover', 'double click', 'right click', 'scroll', 'wheel', 'ticks'],
    recap='<p>Build a chain of actions and call perform() to send it in one request. Each input source has one action per tick, and a tick lasts as long as its slowest action. Use mouse actions for hover, double click, right click and drag, key down and key up for modifiers, and wheel actions for scrolling. Wait for the result of a scroll, and release every key you press.</p>')
