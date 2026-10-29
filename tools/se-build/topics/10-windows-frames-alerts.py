# Chapter 4.2: windows and tabs, frames and iframes, and JavaScript alerts. Sources: selenium.dev documentation
# (Working with windows and tabs, Working with IFrames and frames, JavaScript alerts, prompts and confirmations,
# Browser options unhandledPromptBehavior), the W3C WebDriver specification (window handles, Switch To Frame,
# Switch To Parent Frame, user prompts) and real runs on the Selenium test pages xhtmlTest.html, iframes.html,
# iframeWithIframe.html and alerts.html.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, src, flow

K = Kit()

WIN = tri('windows', 'Follow a link into a new window, come back, open a new tab', java=r'''
import java.time.Duration;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WindowType;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class Windows {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/xhtmlTest.html");
        String original = driver.getWindowHandle();  ## The id of the current window. It stays the same for the whole session.
        System.out.println("windows at start: " + driver.getWindowHandles().size());
        driver.findElement(By.name("windowTwo")).click();  ## This link has target="_blank", so it opens a new window.
        new WebDriverWait(driver, Duration.ofSeconds(2)).until(ExpectedConditions.numberOfWindowsToBe(2));  ## Wait until the second window exists.
        for (String handle : driver.getWindowHandles()) {  ## Every open window, in the order they were opened.
            if (!handle.equals(original)) driver.switchTo().window(handle);  ## Switch to the one that is not the original.
        }
        System.out.println("new window: " + driver.getTitle());
        driver.close();  ## Close only this window.
        driver.switchTo().window(original);  ## Switch back, or the next command fails with no such window.
        System.out.println("back to: " + driver.getTitle());
        driver.switchTo().newWindow(WindowType.TAB);  ## Selenium 4: open a new tab and switch to it in one step.
        driver.get("https://www.selenium.dev/selenium/web/resultPage.html");
        System.out.println("new tab: " + driver.getTitle() + ", windows: " + driver.getWindowHandles().size());
        driver.quit();  ## Closes every window and tab at once.
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/xhtmlTest.html")
original = driver.current_window_handle  ## The id of the current window. It stays the same for the whole session.
print("windows at start:", len(driver.window_handles))
driver.find_element(By.NAME, "windowTwo").click()  ## This link has target="_blank", so it opens a new window.
WebDriverWait(driver, 2).until(EC.number_of_windows_to_be(2))  ## Wait until the second window exists.
for handle in driver.window_handles:  ## Every open window, in the order they were opened.
    if handle != original:
        driver.switch_to.window(handle)  ## Switch to the one that is not the original.
print("new window:", driver.title)
driver.close()  ## Close only this window.
driver.switch_to.window(original)  ## Switch back, or the next command fails with no such window.
print("back to:", driver.title)
driver.switch_to.new_window("tab")  ## Selenium 4: open a new tab and switch to it in one step.
driver.get("https://www.selenium.dev/selenium/web/resultPage.html")
print("new tab:", driver.title + ", windows:", len(driver.window_handles))
driver.quit()  ## Closes every window and tab at once.
''', js=r'''
const { Builder, Browser, By } = require('selenium-webdriver');

(async function windows() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/xhtmlTest.html');
  const original = await driver.getWindowHandle();  ## The id of the current window. It stays the same for the whole session.
  console.log('windows at start: ' + (await driver.getAllWindowHandles()).length);
  await driver.findElement(By.name('windowTwo')).click();  ## This link has target="_blank", so it opens a new window.
  await driver.wait(async () => (await driver.getAllWindowHandles()).length === 2, 2000);  ## Wait until the second window exists.
  for (const handle of await driver.getAllWindowHandles()) {  ## Every open window, in the order they were opened.
    if (handle !== original) await driver.switchTo().window(handle);  ## Switch to the one that is not the original.
  }
  console.log('new window: ' + await driver.getTitle());
  await driver.close();  ## Close only this window.
  await driver.switchTo().window(original);  ## Switch back, or the next command fails with no such window.
  console.log('back to: ' + await driver.getTitle());
  await driver.switchTo().newWindow('tab');  ## Selenium 4: open a new tab and switch to it in one step.
  await driver.get('https://www.selenium.dev/selenium/web/resultPage.html');
  console.log('new tab: ' + await driver.getTitle() + ', windows: ' + (await driver.getAllWindowHandles()).length);
  await driver.quit();  ## Closes every window and tab at once.
})();
''', expect='back to: XHTML Test Page')

FRAMES = tri('frames', 'Switch into an iframe three ways and back out', java=r'''
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

public class Frames {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/iframes.html");
        System.out.println("email boxes seen from the top: " + driver.findElements(By.id("email")).size());  ## The form lives inside the iframe, so the top document sees none.
        WebElement frame = driver.findElement(By.id("iframe1"));
        driver.switchTo().frame(frame);  ## 1. Switch with a WebElement: the most flexible way.
        System.out.println("by element: " + driver.findElement(By.id("email")).getAttribute("type"));
        driver.switchTo().defaultContent();  ## Leave the frame: back to the top document.
        driver.switchTo().frame("iframe1-name");  ## 2. Switch with the frame name or id.
        System.out.println("by name: " + driver.findElements(By.id("email")).size() + " email box");
        driver.switchTo().defaultContent();
        driver.switchTo().frame(0);  ## 3. Switch with an index: the first frame of the page.
        System.out.println("title inside the frame: " + driver.getTitle());  ## Get Title always reports the top level page, even from inside a frame.
        driver.switchTo().defaultContent();
        System.out.println("heading: " + driver.findElement(By.id("iframe_page_heading")).getText());  ## Outside elements are reachable again.
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/iframes.html")
print("email boxes seen from the top:", len(driver.find_elements(By.ID, "email")))  ## The form lives inside the iframe, so the top document sees none.
frame = driver.find_element(By.ID, "iframe1")
driver.switch_to.frame(frame)  ## 1. Switch with a WebElement: the most flexible way.
print("by element:", driver.find_element(By.ID, "email").get_attribute("type"))
driver.switch_to.default_content()  ## Leave the frame: back to the top document.
driver.switch_to.frame("iframe1-name")  ## 2. Switch with the frame name or id.
print("by name:", len(driver.find_elements(By.ID, "email")), "email box")
driver.switch_to.default_content()
driver.switch_to.frame(0)  ## 3. Switch with an index: the first frame of the page.
print("title inside the frame:", driver.title)  ## Get Title always reports the top level page, even from inside a frame.
driver.switch_to.default_content()
print("heading:", driver.find_element(By.ID, "iframe_page_heading").text)  ## Outside elements are reachable again.
driver.quit()
''', js=r'''
const { Builder, Browser, By } = require('selenium-webdriver');

(async function frames() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/iframes.html');
  console.log('email boxes seen from the top: ' + (await driver.findElements(By.id('email'))).length);  ## The form lives inside the iframe, so the top document sees none.
  const frame = await driver.findElement(By.id('iframe1'));
  await driver.switchTo().frame(frame);  ## 1. Switch with a WebElement: the most flexible way.
  console.log('by element: ' + await driver.findElement(By.id('email')).getAttribute('type'));
  await driver.switchTo().defaultContent();  ## Leave the frame: back to the top document.
  await driver.switchTo().frame(await driver.findElement(By.name('iframe1-name')));  ## 2. JavaScript has no switch by name string, so find the frame by its name first.
  console.log('by name: ' + (await driver.findElements(By.id('email'))).length + ' email box');
  await driver.switchTo().defaultContent();
  await driver.switchTo().frame(0);  ## 3. Switch with an index: the first frame of the page.
  console.log('title inside the frame: ' + await driver.getTitle());  ## Get Title always reports the top level page, even from inside a frame.
  await driver.switchTo().defaultContent();
  console.log('heading: ' + await driver.findElement(By.id('iframe_page_heading')).getText());  ## Outside elements are reachable again.
  await driver.quit();
})();
''', expect='heading: This is the heading')

ALERTS = tri('alerts', 'Alert, confirm, prompt, a slow alert and one left open', java=r'''
import java.time.Duration;
import org.openqa.selenium.Alert;
import org.openqa.selenium.By;
import org.openqa.selenium.UnhandledAlertException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class Alerts {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(2));
        driver.get("https://www.selenium.dev/selenium/web/alerts.html");
        driver.findElement(By.id("alert")).click();  ## The page calls alert('cheese').
        Alert alert = wait.until(ExpectedConditions.alertIsPresent());  ## Wait for the alert, then get a handle on it.
        System.out.println("alert: " + alert.getText());
        alert.accept();  ## Press OK.
        driver.findElement(By.id("confirm")).click();  ## A confirm box: OK or Cancel.
        Alert confirm = driver.switchTo().alert();  ## Switch to it without waiting, because it opens at once.
        System.out.println("confirm: " + confirm.getText());
        confirm.dismiss();  ## Press Cancel.
        driver.findElement(By.id("prompt")).click();  ## A prompt asks for text.
        Alert prompt = wait.until(ExpectedConditions.alertIsPresent());
        prompt.sendKeys("Selenium");  ## Type the answer into the prompt.
        prompt.accept();
        System.out.println("page shows: " + driver.findElement(By.id("text")).getText());  ## The page wrote our answer into a paragraph.
        driver.findElement(By.id("slow-alert")).click();  ## This one opens 200 ms later.
        System.out.println("slow: " + wait.until(ExpectedConditions.alertIsPresent()).getText());  ## switchTo().alert() now would fail, so wait.
        driver.switchTo().alert().accept();
        driver.findElement(By.id("alert")).click();  ## Open one more alert and forget about it.
        try {
            driver.getTitle();  ## Any command while an alert is open.
        } catch (UnhandledAlertException e) {
            System.out.println("left open: " + e.getMessage().split("\n")[0]);  ## The default behaviour dismisses it and reports an error.
        }
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 2)
driver.get("https://www.selenium.dev/selenium/web/alerts.html")
driver.find_element(By.ID, "alert").click()  ## The page calls alert('cheese').
alert = wait.until(EC.alert_is_present())  ## Wait for the alert, then get a handle on it.
print("alert:", alert.text)
alert.accept()  ## Press OK.
driver.find_element(By.ID, "confirm").click()  ## A confirm box: OK or Cancel.
confirm = driver.switch_to.alert  ## Switch to it without waiting, because it opens at once.
print("confirm:", confirm.text)
confirm.dismiss()  ## Press Cancel.
driver.find_element(By.ID, "prompt").click()  ## A prompt asks for text.
prompt = wait.until(EC.alert_is_present())
prompt.send_keys("Selenium")  ## Type the answer into the prompt.
prompt.accept()
print("page shows:", driver.find_element(By.ID, "text").text)  ## The page wrote our answer into a paragraph.
driver.find_element(By.ID, "slow-alert").click()  ## This one opens 200 ms later.
print("slow:", wait.until(EC.alert_is_present()).text)  ## switch_to.alert now would fail, so wait.
driver.switch_to.alert.accept()
driver.find_element(By.ID, "alert").click()  ## Open one more alert and forget about it.
try:
    driver.title  ## Any command while an alert is open.
except UnexpectedAlertPresentException as e:
    print("left open:", e.msg.split("\n")[0])  ## The default behaviour dismisses it and reports an error.
driver.quit()
''', js=r'''
const { Builder, Browser, By, until, error } = require('selenium-webdriver');

(async function alerts() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/alerts.html');
  await driver.findElement(By.id('alert')).click();  ## The page calls alert('cheese').
  const alert = await driver.wait(until.alertIsPresent(), 2000);  ## Wait for the alert, then get a handle on it.
  console.log('alert: ' + await alert.getText());
  await alert.accept();  ## Press OK.
  await driver.findElement(By.id('confirm')).click();  ## A confirm box: OK or Cancel.
  const confirm = await driver.switchTo().alert();  ## Switch to it without waiting, because it opens at once.
  console.log('confirm: ' + await confirm.getText());
  await confirm.dismiss();  ## Press Cancel.
  await driver.findElement(By.id('prompt')).click();  ## A prompt asks for text.
  const prompt = await driver.wait(until.alertIsPresent(), 2000);
  await prompt.sendKeys('Selenium');  ## Type the answer into the prompt.
  await prompt.accept();
  console.log('page shows: ' + await driver.findElement(By.id('text')).getText());  ## The page wrote our answer into a paragraph.
  await driver.findElement(By.id('slow-alert')).click();  ## This one opens 200 ms later.
  const slow = await driver.wait(until.alertIsPresent(), 2000);  ## switchTo().alert() now would fail, so wait.
  console.log('slow: ' + await slow.getText());
  await slow.accept();
  await driver.findElement(By.id('alert')).click();  ## Open one more alert and forget about it.
  try {
    await driver.getTitle();  ## Any command while an alert is open.
  } catch (e) {
    if (!(e instanceof error.UnexpectedAlertOpenError)) throw e;
    console.log('left open: ' + e.message.split('\n')[0]);  ## The default behaviour dismisses it and reports an error.
  }
  await driver.quit();
})();
''', expect='page shows: Selenium')

K.lesson('windows', 'Windows and tabs', f'''
<p>WebDriver does not tell windows and tabs apart. Each one has a <b>window handle</b>, a unique id that stays the same for the whole session. Commands always go to one window, the current one. When a link opens a new window, the browser shows it on screen, but the documentation points out that WebDriver does not follow. You must switch.</p>
{viz('se-context')}
{WIN}
{table(['What you want', 'Java', 'Python', 'JavaScript'], [
    ['Current handle', '<code>getWindowHandle()</code>', '<code>current_window_handle</code>', '<code>getWindowHandle()</code>'],
    ['All handles', '<code>getWindowHandles()</code>', '<code>window_handles</code>', '<code>getAllWindowHandles()</code>'],
    ['Switch', '<code>switchTo().window(h)</code>', '<code>switch_to.window(h)</code>', '<code>switchTo().window(h)</code>'],
    ['New tab or window', '<code>switchTo().newWindow(WindowType.TAB)</code>', '<code>switch_to.new_window("tab")</code>', '<code>switchTo().newWindow("tab")</code>'],
    ['Close current', '<code>close()</code>', '<code>close()</code>', '<code>close()</code>']])}
{note('After close() you are still pointing at the closed window. The documentation warns that the next command raises no such window. Always switch back to a handle you saved before.', 'warn')}
{scene('the payment pop up', '<p>A shop opens the card payment page of its bank in a new window. The test saves the shop window handle, clicks Pay, waits for two windows, switches to the bank window, fills in the test card and confirms. The bank window closes itself, so the test switches back to the saved shop handle and checks the order confirmation.</p>')}
''', kw=['window handle', 'tabs', 'switch to window', 'new window', 'new tab', 'close', 'no such window', 'getWindowHandles', 'target blank'])

K.lesson('frames', 'Frames and iframes', f'''
<p>An <b>iframe</b> puts a whole second document inside a page, often from another site: a payment form, a video player, a chat box or an editor. Selenium only sees the elements of the document it is pointing at, so the documentation explains that an element inside an iframe gives no such element until you switch into the frame.</p>
{FRAMES}
{table(['Switch by', 'Example', 'When to use'], [
    ['WebElement', '<code>switchTo().frame(element)</code>', 'Most flexible. Find the frame with any locator.'],
    ['Name or id', '<code>switchTo().frame("iframe1-name")</code>', 'The frame has a stable name or id. If several match, the first one is used. Java and Python accept the string. JavaScript needs the element.'],
    ['Index', '<code>switchTo().frame(0)</code>', 'Position in window.frames. Breaks if frames are added.'],
    ['Leave all frames', '<code>switchTo().defaultContent()</code>', 'Back to the top document.'],
    ['Up one level', '<code>switchTo().parentFrame()</code>', 'For frames inside frames.']])}
<p>One detail in the output surprises people: inside the frame, Get Title still returned the title of the top page. Title belongs to the top level browsing context. Element commands, on the other hand, go to the frame you switched to.</p>
<div class="sp" data-sp="frames"></div>
''', kw=['iframe', 'frame', 'switch to frame', 'default content', 'parent frame', 'frame index', 'frame name', 'nested frames'])

K.lesson('alerts', 'Alerts, confirms and prompts', f'''
<p>JavaScript has three native pop ups, drawn by the browser and not by the page, so they cannot be found with locators. WebDriver has its own commands for them.</p>
{table(['Pop up', 'Buttons', 'What you can do'], [
    ['alert', 'OK', 'Read the text, accept'],
    ['confirm', 'OK and Cancel', 'Read the text, accept or dismiss'],
    ['prompt', 'OK and Cancel, plus a text box', 'Read the text, send keys, accept or dismiss. Sending keys replaces the placeholder text']])}
{ALERTS}
<p>Two lessons come out of this run. A <b>slow alert</b> needs a wait, exactly like a slow element: <code>alertIsPresent</code> in Java, <code>alert_is_present</code> in Python, <code>until.alertIsPresent</code> in JavaScript. And an alert you <b>forget</b> breaks the next command. The unhandledPromptBehavior capability decides what happens. Its default, dismiss and notify, closes the pop up and raises unexpected alert open, so the test fails at the line after the real cause.</p>
{table(['unhandledPromptBehavior', 'What happens to a forgotten pop up'], [
    ['dismiss and notify (default)', 'Dismissed, and the command raises unexpected alert open'],
    ['accept and notify', 'Accepted, and the command raises unexpected alert open'],
    ['dismiss', 'Dismissed silently'],
    ['accept', 'Accepted silently'],
    ['ignore', 'Left open, and the command raises unexpected alert open']])}
<div class="sp" data-sp="alerts"></div>
{note('Recent drivers dismiss beforeunload prompts, the "Leave site?" box, by default. Chapter 2.1 showed where unhandledPromptBehavior is set.', 'tip')}
{ladder(
    '<p>Selenium works in one window and one document at a time. To use a new tab, a frame or a pop up, you tell it to switch there first.</p>',
    '<p>Windows have handles, frames are switched into by element, name or index, and alerts have their own accept, dismiss, text and send keys commands. Save the original handle and always switch back.</p>',
    '<p>The W3C spec keeps a current top level browsing context and a current browsing context. Window commands change the first, frame commands the second. Title and window rect read the top level context, element commands use the current one.</p>',
    '<p>BiDi models every window, tab and frame as a browsingContext with events for creation, navigation and user prompts. A test can then react to a pop up or a new tab the moment it opens, instead of polling for it.</p>')}
''', kw=['alert', 'confirm', 'prompt', 'accept', 'dismiss', 'switch to alert', 'alert is present', 'unexpected alert open', 'unhandledPromptBehavior', 'beforeunload'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Does WebDriver treat a tab differently from a window?', ['Yes, tabs need special commands', 'No, both are windows with a handle', 'Tabs cannot be automated', 'Only in Firefox'], 1,
       'One kind of handle.', 'WebDriver does not make a distinction between windows and tabs.')
K.quiz('e', 'Which command leaves every frame and returns to the top document?', ['parentFrame', 'defaultContent', 'frame(0)', 'window(original)'], 1,
       'Default means top.', 'switchTo().defaultContent() returns to the top level document.')
K.quiz('e', 'How do you press OK on an alert?', ['alert.dismiss()', 'alert.accept()', 'click the OK button by xpath', 'alert.close()'], 1,
       'Accept means OK.', 'accept presses OK. dismiss presses Cancel or closes it.')
K.quiz('m', 'A link opens a new window. Where do your next commands go if you do nothing?', ['The new window', 'The original window', 'Both', 'Nowhere, the session ends'], 1,
       'WebDriver does not follow the screen.', 'WebDriver keeps its current window until you switch, even if the new one is focused on screen.')
K.quiz('m', 'You close a window and then call getTitle() without switching. What happens?', ['The title of the other window', 'no such window error', 'An empty title', 'The browser quits'], 1,
       'The current window is gone.', 'The documentation warns that forgetting to switch back triggers a No Such Window Exception.')
K.quiz('m', 'An element is inside an iframe. find element from the top document gives which error?', ['stale element reference', 'no such element', 'no such frame', 'invalid selector'], 1,
       'The top document cannot see into the frame.', 'Selenium only sees the current document, so it raises no such element until you switch.')
K.quiz('m', 'An alert appears 200 ms after a click. What should the test do before switching to it?', ['Sleep 1 s', 'Wait for alert is present', 'Refresh', 'Nothing'], 1,
       'Same as a slow element.', 'Use an explicit wait with the alert present condition, which also returns the alert.')
K.quiz('h', 'From inside an iframe you call Get Title. Which title do you get?', ['The iframe document title', 'The top level page title', 'An error', 'An empty string'], 1,
       'Look at the real output.', 'Get Title reads the top level browsing context, as the run on this page showed.')
K.quiz('h', 'With the default unhandledPromptBehavior, what happens to a forgotten alert at the next command?', ['It stays open silently', 'It is accepted silently', 'It is dismissed and the command raises unexpected alert open', 'The session ends'], 2,
       'dismiss and notify.', 'The default dismiss and notify closes it and reports an error.')
K.quiz('x', 'Which is the most fragile way to switch to a frame?', ['By WebElement', 'By a unique id', 'By index', 'By name'], 2,
       'Positions change.', 'An index depends on the order of frames, so adding a frame anywhere earlier breaks it.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A test opens 3 extra tabs with newWindow and closes 1 of them. How many window handles does the session have?', '3', 'Start with one.',
       ['Start: 1 window.', 'Open 3: 4 windows.', eq('Close 1: 4 − 1 = 3 handles')], check=3)
K.calc('e', 'A page has 4 iframes. What is the highest index you can pass to switchTo().frame()?', '3', 'Indexes start at 0.',
       ['The frames are 0, 1, 2 and 3.', 'The highest is the count minus one.', eq('4 − 1 = 3')], check=3)
K.calc('m', 'You are 3 frames deep. How many parentFrame() calls bring you to the top document?', '3', 'One level each.',
       ['parentFrame goes up one level.', 'Three levels of frames.', eq('3 calls, or one defaultContent()')], check=3)
K.calc('m', 'An alert opens 200 ms after the click and an explicit wait polls every 500 ms from 0. When does the wait return, in ms?', '500', 'First poll after 200 ms.',
       ['Poll at 0 ms: no alert yet.', 'The alert opens at 200 ms.', eq('Poll at 500 ms finds it')], check=500, unit='ms')
K.calc('h', 'A suite of 400 tests leaves one alert open in 5 % of tests, which fails the next command. How many tests fail for this reason?', '20', 'Percent of tests.',
       ['5 % of 400.', '0.05 × 400.', eq('20 tests fail at the line after the real cause')], check=20)
K.calc('x', 'A test switches window 6 times, each switch is one command of 12 ms, and it also needs 2 waits for a new window that poll every 500 ms and succeed on the second poll. Roughly how many ms does window handling add?', '1072', 'Commands plus waiting.',
       ['Switches: 6 × 12 = 72 ms.', 'Each wait succeeds on the second poll, at 500 ms: 2 × 500 = 1,000 ms.', eq('72 + 1,000 = 1,072 ms')], check=1072, unit='ms')

# ---------------------------------------------------------------- assignments
K.assign('newhandle', 'e', 'Find the new window handle',
         '<p>Write <code>new_handle(before, after)</code>. <code>before</code> is the list of handles before a click, <code>after</code> the list after it. Return the one handle that is new, or <code>None</code> if nothing new opened.</p>',
         '''
def new_handle(before, after):
    # your code here
    pass
''', [('new_handle(["A"], ["A", "B"])', 'B'), ('new_handle(["A", "B"], ["A", "B", "C"])', 'C'), ('new_handle(["A"], ["A"])', None)],
         '''
def new_handle(before, after):
    for handle in after:
        if handle not in before:
            return handle
    return None
''', 'Loop over after and return the first handle that is not in before.', '<p>Comparing with the handles you had before is safer than taking the last handle, because the order of handles is not guaranteed by every driver.</p>')
K.assign('promptres', 'm', 'What does the page get from a prompt?',
         '<p>Write <code>prompt_result(action, typed)</code> for a JavaScript prompt. <code>action</code> is "accept" or "dismiss", <code>typed</code> is the text sent with send keys or <code>None</code>. Accept returns the typed text, or an empty string if nothing was typed. Dismiss always returns <code>None</code>, because pressing Cancel submits nothing.</p>',
         '''
def prompt_result(action, typed):
    # your code here
    pass
''', [('prompt_result("accept", "Selenium")', 'Selenium'), ('prompt_result("accept", None)', ''), ('prompt_result("dismiss", "Selenium")', None)],
         '''
def prompt_result(action, typed):
    if action == "dismiss":
        return None
    return typed if typed is not None else ""
''', 'Handle dismiss first.', '<p>In a real browser, accept with nothing typed returns whatever default text the prompt had. The prompt on alerts.html has no default, so it is an empty string.</p>')

K.must('Windows', 'Each window or tab has a handle. Save the original, switch to the new one, and switch back after close(). newWindow("tab") opens and switches in one step.')
K.must('Frames', 'Switch into an iframe by element, name or id, or index before finding inside it. defaultContent goes to the top, parentFrame up one level.')
K.must('Title in frames', 'Get Title always reports the top level page, even from inside a frame.')
K.must('Alerts', 'alert, confirm and prompt: getText, accept, dismiss, sendKeys. Wait with alert is present when it appears late.')
K.must('Forgotten pop ups', 'unhandledPromptBehavior defaults to dismiss and notify: the pop up is closed and the next command raises unexpected alert open.')

T = K.topic(
    slug='windows-frames-alerts', topic='windows-frames-alerts',
    step=(4, 'Synchronise and control', 'se-control', 'Waits, windows, tabs, frames and alerts, the Actions API, JavaScript, cookies and print.', 'Intermediate'),
    title='Windows, tabs, frames and alerts', short='Windows, frames, alerts', badge='4.2', minutes=50, added='2026-10-29',
    lead='Point WebDriver at the right place: switch between windows and tabs, step into iframes and out again, and handle alerts, confirms and prompts, including the ones that appear late or are forgotten.',
    desc='Window handles, switching, new tabs and closing with real runs in Java, Python and JavaScript, an animation of the current browsing context, iframes by element, name and index, defaultContent and parentFrame, the top level title, alert, confirm and prompt, waiting for slow alerts, and unhandledPromptBehavior.',
    summary='Switching windows and tabs, working inside iframes, and handling alerts, confirms and prompts.',
    keywords=['windows', 'tabs', 'window handle', 'iframe', 'frames', 'alerts', 'confirm', 'prompt', 'switch to', 'unhandledpromptbehavior'],
    recap='<p>WebDriver works in one window and one document at a time. Switch windows by handle and switch back after closing. Switch into iframes before finding inside them and leave with defaultContent. Handle alerts with accept, dismiss, getText and sendKeys, wait for slow ones, and never leave one open.</p>')
