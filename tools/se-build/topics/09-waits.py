# Chapter 4.1: waiting strategies. Sources: selenium.dev documentation (Waiting Strategies with the dynamic.html
# example, Expected Conditions, Browser options timeouts), the WebDriverWait sources of Selenium 4.51 (Python polls
# every 0.5 s and ignores NoSuchElementException by default, Java polls every 500 ms, JavaScript driver.wait polls
# every 200 ms and waits forever when no timeout is given) and real runs against Chrome 153 on dynamic.html, where
# "Add a box!" and "Reveal a new input" act after 1 second.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, src, flow

K = Kit()

RACE = tri('race', 'The race: look for the box straight after the click', java=r'''
import org.openqa.selenium.By;
import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class Race {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/dynamic.html");
        driver.findElement(By.id("adder")).click();  ## The page adds a red box, but only 1 second after the click.
        try {
            driver.findElement(By.id("box0"));  ## Our code asks at once. No wait is set, so the driver checks only once.
            System.out.println("found the box");
        } catch (NoSuchElementException e) {
            System.out.println("too early: no such element");  ## Selenium was faster than the page.
        }
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/dynamic.html")
driver.find_element(By.ID, "adder").click()  ## The page adds a red box, but only 1 second after the click.
try:
    driver.find_element(By.ID, "box0")  ## Our code asks at once. No wait is set, so the driver checks only once.
    print("found the box")
except NoSuchElementException:
    print("too early: no such element")  ## Selenium was faster than the page.
driver.quit()
''', js=r'''
const { Builder, Browser, By, error } = require('selenium-webdriver');

(async function race() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/dynamic.html');
  await driver.findElement(By.id('adder')).click();  ## The page adds a red box, but only 1 second after the click.
  try {
    await driver.findElement(By.id('box0'));  ## Our code asks at once. No wait is set, so the driver checks only once.
    console.log('found the box');
  } catch (e) {
    if (!(e instanceof error.NoSuchElementError)) throw e;
    console.log('too early: no such element');  ## Selenium was faster than the page.
  }
  await driver.quit();
})();
''', expect='too early')

IMPLICIT = tri('implicit', 'Implicit wait: every find keeps looking', java=r'''
import java.time.Duration;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

public class Implicit {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(2));  ## For the whole session: a find may keep looking for up to 2 seconds.
        driver.get("https://www.selenium.dev/selenium/web/dynamic.html");
        driver.findElement(By.id("adder")).click();
        long start = System.nanoTime();
        WebElement box = driver.findElement(By.id("box0"));  ## Not there yet, so the driver keeps checking until the box appears.
        double seconds = (System.nanoTime() - start) / 1e9;
        System.out.println("found " + box.getAttribute("class") + " after about " + Math.round(seconds) + " s");  ## Returns as soon as it is found, not after the full 2 seconds.
        driver.quit();
    }
}
''', py=r'''
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.implicitly_wait(2)  ## For the whole session: a find may keep looking for up to 2 seconds.
driver.get("https://www.selenium.dev/selenium/web/dynamic.html")
driver.find_element(By.ID, "adder").click()
start = time.monotonic()
box = driver.find_element(By.ID, "box0")  ## Not there yet, so the driver keeps checking until the box appears.
seconds = time.monotonic() - start
print("found", box.get_attribute("class"), "after about", round(seconds), "s")  ## Returns as soon as it is found, not after the full 2 seconds.
driver.quit()
''', js=r'''
const { Builder, Browser, By } = require('selenium-webdriver');

(async function implicit() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.manage().setTimeouts({ implicit: 2000 });  ## For the whole session: a find may keep looking for up to 2 seconds.
  await driver.get('https://www.selenium.dev/selenium/web/dynamic.html');
  await driver.findElement(By.id('adder')).click();
  const start = Date.now();
  const box = await driver.findElement(By.id('box0'));  ## Not there yet, so the driver keeps checking until the box appears.
  const seconds = (Date.now() - start) / 1000;
  console.log('found ' + await box.getAttribute('class') + ' after about ' + Math.round(seconds) + ' s');  ## Returns as soon as it is found, not after the full 2 seconds.
  await driver.quit();
})();
''', expect='found redbox')

EXPLICIT = tri('explicit', 'Explicit wait: wait for exactly the condition you need', java=r'''
import java.time.Duration;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.WebDriverWait;

public class Explicit {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/dynamic.html");
        WebElement revealed = driver.findElement(By.id("revealed"));  ## The input is in the page already, just hidden.
        driver.findElement(By.id("reveal")).click();  ## The page shows it 1 second later.
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(2));  ## Wait at most 2 seconds. Java checks every 500 ms.
        wait.until(d -> revealed.isDisplayed());  ## A lambda: keep calling it until it returns true.
        revealed.sendKeys("Displayed");  ## Safe now: the input is displayed, so it can take keys.
        System.out.println("typed: " + revealed.getDomProperty("value"));
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/dynamic.html")
revealed = driver.find_element(By.ID, "revealed")  ## The input is in the page already, just hidden.
driver.find_element(By.ID, "reveal").click()  ## The page shows it 1 second later.
wait = WebDriverWait(driver, timeout=2)  ## Wait at most 2 seconds. Python checks every 0.5 s.
wait.until(lambda d: revealed.is_displayed())  ## A lambda: keep calling it until it returns something true.
revealed.send_keys("Displayed")  ## Safe now: the input is displayed, so it can take keys.
print("typed:", revealed.get_property("value"))
driver.quit()
''', js=r'''
const { Builder, Browser, By } = require('selenium-webdriver');

(async function explicit() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/dynamic.html');
  const revealed = await driver.findElement(By.id('revealed'));  ## The input is in the page already, just hidden.
  await driver.findElement(By.id('reveal')).click();  ## The page shows it 1 second later.
  await driver.wait(() => revealed.isDisplayed(), 2000);  ## Keep calling the function until it is true, for at most 2000 ms. JavaScript checks every 200 ms.
  await revealed.sendKeys('Displayed');  ## Safe now: the input is displayed, so it can take keys.
  console.log('typed: ' + await revealed.getProperty('value'));
  await driver.quit();
})();
''', expect='typed: Displayed')

EC = tri('conditions', 'Ready made conditions, and what a timeout looks like', java=r'''
import java.time.Duration;
import org.openqa.selenium.By;
import org.openqa.selenium.TimeoutException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class Conditions {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/dynamic.html");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(2));
        driver.findElement(By.id("adder")).click();
        WebElement box = wait.until(ExpectedConditions.presenceOfElementLocated(By.id("box0")));  ## A ready made condition. It returns the element it waited for.
        System.out.println("present: " + box.getAttribute("id"));
        driver.findElement(By.id("reveal")).click();
        WebElement input = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("revealed")));  ## Present is not enough for typing. Wait until it is visible.
        System.out.println("visible: " + input.isDisplayed());
        try {
            new WebDriverWait(driver, Duration.ofSeconds(1)).withMessage("the second box never came")  ## Our own message makes the failure readable.
                .until(ExpectedConditions.presenceOfElementLocated(By.id("box1")));  ## Nobody clicked again, so box1 never appears.
        } catch (TimeoutException e) {
            System.out.println("TimeoutException: " + e.getMessage().split("\n")[0]);
        }
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  ## The usual short name for the expected conditions module.
from selenium.webdriver.support.wait import WebDriverWait

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/dynamic.html")
wait = WebDriverWait(driver, 2)
driver.find_element(By.ID, "adder").click()
box = wait.until(EC.presence_of_element_located((By.ID, "box0")))  ## A ready made condition. Note the locator is one tuple. It returns the element.
print("present:", box.get_attribute("id"))
driver.find_element(By.ID, "reveal").click()
field = wait.until(EC.visibility_of_element_located((By.ID, "revealed")))  ## Present is not enough for typing. Wait until it is visible.
print("visible:", field.is_displayed())
try:
    WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, "box1")), "the second box never came")  ## Nobody clicked again, so box1 never appears. The second argument is our message.
except TimeoutException as e:
    print("TimeoutException:", e.msg)
driver.quit()
''', js=r'''
const { Builder, Browser, By, until, error } = require('selenium-webdriver');  ## until holds the ready made conditions in JavaScript.

(async function conditions() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/dynamic.html');
  await driver.findElement(By.id('adder')).click();
  const box = await driver.wait(until.elementLocated(By.id('box0')), 2000);  ## A ready made condition. It resolves to the element.
  console.log('present: ' + await box.getAttribute('id'));
  await driver.findElement(By.id('reveal')).click();
  const field = await driver.findElement(By.id('revealed'));
  await driver.wait(until.elementIsVisible(field), 2000);  ## Present is not enough for typing. Wait until it is visible.
  console.log('visible: ' + await field.isDisplayed());
  try {
    await driver.wait(until.elementLocated(By.id('box1')), 1000, 'the second box never came');  ## Nobody clicked again, so box1 never appears. The third argument is our message.
  } catch (e) {
    if (!(e instanceof error.TimeoutError)) throw e;
    console.log('TimeoutError: ' + e.message.split('\n')[0]);
  }
  await driver.quit();
})();
''', expect='the second box never came')

FLUENT = tri('fluent', 'A customised wait: poll faster and retry on an error', java=r'''
import java.time.Duration;
import org.openqa.selenium.By;
import org.openqa.selenium.ElementNotInteractableException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.openqa.selenium.support.ui.Wait;

public class Fluent {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/dynamic.html");
        WebElement revealed = driver.findElement(By.id("revealed"));
        driver.findElement(By.id("reveal")).click();
        Wait<WebDriver> wait = new FluentWait<WebDriver>(driver)  ## FluentWait lets you set every part of the loop.
            .withTimeout(Duration.ofSeconds(2))  ## Give up after 2 seconds.
            .pollingEvery(Duration.ofMillis(300))  ## Check every 300 ms instead of 500.
            .ignoring(ElementNotInteractableException.class);  ## Treat this error as not yet and try again.
        wait.until(d -> {  ## The condition does the action itself and returns true when it worked.
            revealed.sendKeys("Displayed");
            return true;
        });
        System.out.println("typed: " + revealed.getDomProperty("value"));
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/dynamic.html")
revealed = driver.find_element(By.ID, "revealed")
driver.find_element(By.ID, "reveal").click()
errors = [ElementNotInteractableException]  ## The errors that mean not yet, try again.
wait = WebDriverWait(driver, timeout=2, poll_frequency=0.3, ignored_exceptions=errors)  ## Give up after 2 s, check every 0.3 s.
wait.until(lambda d: revealed.send_keys("Displayed") or True)  ## Do the action inside the condition. send_keys returns None, so "or True" reports success.
print("typed:", revealed.get_property("value"))
driver.quit()
''', js=r'''
const { Builder, Browser, By, error } = require('selenium-webdriver');

(async function fluent() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/dynamic.html');
  const revealed = await driver.findElement(By.id('revealed'));
  await driver.findElement(By.id('reveal')).click();
  await driver.wait(async () => {  ## JavaScript has no ignore list, so the condition catches the error itself.
    try {
      await revealed.sendKeys('Displayed');
      return true;  ## Worked: the wait ends.
    } catch (e) {
      if (e instanceof error.ElementNotInteractableError) return false;  ## Not yet: the wait tries again.
      throw e;  ## Any other error is a real problem.
    }
  }, 2000, 'the input never became usable', 300);  ## Timeout 2000 ms, our message, and poll every 300 ms.
  console.log('typed: ' + await revealed.getProperty('value'));
  await driver.quit();
})();
''', expect='typed: Displayed')

MIX = solo('mixwait', 'Proof: mixing implicit and explicit waits stretches the timeout', 'py', r'''
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/dynamic.html")
driver.implicitly_wait(2)  ## Implicit wait: each find may block for 2 seconds.
start = time.monotonic()
try:
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "box9")))  ## Explicit wait of 3 seconds for an element that never comes.
except TimeoutException:
    print(f"gave up after {time.monotonic() - start:.1f} s, not 3 s")  ## Each check inside the explicit wait blocked 2 seconds on the implicit wait.
driver.quit()
''', expect='gave up after', why='Python only, because the timing rule is the same in every binding. The documentation warns that 10 s implicit plus 15 s explicit can time out after 20 s. Here smaller numbers make the run short.')

K.lesson('race', 'The race between your code and the page', f'''
<p>The documentation calls synchronisation perhaps the most common challenge in browser automation. Your code and the page run at the same time. Sometimes the page is ready first and the test passes. Sometimes Selenium is first and the test fails. A test that passes and fails on the same code is a <b>flaky test</b>, and this race is one of their main causes.</p>
<p>Navigation commands already wait for the page load strategy. But that only covers the HTML and its assets. Content that JavaScript adds or shows later, such as search results, a spinner that goes away or a dialog that slides in, is not covered. The documentation example is the dynamic.html page: <b>Add a box!</b> creates a red box and <b>Reveal a new input</b> shows a hidden input, each about a second after the click.</p>
{RACE}
<p>The first idea most people have is to sleep for a few seconds. The documentation explains why that is poor: too short and it still fails on a slow day, too long and every test pays the full sleep every time. Selenium gives two better tools: implicit waits and explicit waits.</p>
{viz('se-waits')}
''', kw=['race condition', 'flaky test', 'synchronisation', 'sleep', 'dynamic content', 'single page application', 'dynamic.html'])

K.lesson('implicit', 'Implicit waits', f'''
<p>An <b>implicit wait</b> is a session setting. Once set, every find element call keeps looking for up to that long before it raises no such element. It is set with the timeouts capability or a driver method, and its default is 0.</p>
{IMPLICIT}
<p>The box appeared after about one second and find returned straight away. A larger implicit wait does not slow down finds that succeed. It only changes how long a failing find takes to fail.</p>
{table(['Strength', 'Weakness'], [
    ['One line covers every find in the session', 'It only waits for presence. A present element can still be hidden, covered or disabled'],
    ['Finds return as soon as the element appears', 'Every check that something is absent now takes the full wait'],
    ['Easy to show in a first script', 'It cannot wait for text, a title, a count or anything that is not a find']])}
<div class="sp" data-sp="waits"></div>
''', kw=['implicit wait', 'implicitly wait', 'session timeout', 'presence', 'global setting'])

K.lesson('explicit', 'Explicit waits and expected conditions', f'''
<p>An <b>explicit wait</b> is a loop in your code. It checks a condition, sleeps for a polling interval, and checks again, until the condition is true or the timeout passes. Because you choose the condition, you can wait for exactly what the next step needs. The documentation adds that the wait class handles no such element for you while it loops.</p>
{steps('One explicit wait, step by step', [
    'Create the wait with a timeout, for example 2 seconds.',
    'Call until with a condition: a lambda, a function, or a ready made expected condition.',
    'The wait calls the condition. If the result is true, or an element, it returns it to you.',
    'If the result is false, or an ignored error was raised, it looks at the clock. Past the timeout, it raises a timeout error with your message.',
    'Otherwise it sleeps for the polling interval and tries again.'])}
{EXPLICIT}
{table(['Default', 'Java WebDriverWait', 'Python WebDriverWait', 'JavaScript driver.wait'], [
    ['Polling interval', '500 ms', '0.5 s', '200 ms'],
    ['Errors ignored while looping', 'NotFoundException (such as no such element)', 'NoSuchElementException', 'none, catch them yourself'],
    ['Timeout', 'you must give one', 'you must give one', '0, which means wait forever. Always pass one'],
    ['Error at the end', 'TimeoutException', 'TimeoutException', 'TimeoutError']])}
<h3>Expected conditions</h3>
<p>Expected conditions are ready made conditions for the common cases: an element exists, is visible, is clickable or has gone stale, some text is present, or the title contains a value. Java has <code>ExpectedConditions</code>, Python has <code>expected_conditions</code> (usually imported as EC) and JavaScript has <code>until</code>.</p>
{EC}
{table(['Wait for', 'Java', 'Python', 'JavaScript'], [
    ['Element exists', '<code>presenceOfElementLocated</code>', '<code>presence_of_element_located</code>', '<code>until.elementLocated</code>'],
    ['Element visible', '<code>visibilityOfElementLocated</code>', '<code>visibility_of_element_located</code>', '<code>until.elementIsVisible</code>'],
    ['Element clickable', '<code>elementToBeClickable</code>', '<code>element_to_be_clickable</code>', '<code>until.elementIsEnabled</code> plus visible'],
    ['Text present', '<code>textToBePresentInElement</code>', '<code>text_to_be_present_in_element</code>', '<code>until.elementTextContains</code>'],
    ['Title contains', '<code>titleContains</code>', '<code>title_contains</code>', '<code>until.titleContains</code>'],
    ['Element gone stale', '<code>stalenessOf</code>', '<code>staleness_of</code>', '<code>until.stalenessOf</code>']])}
<div class="sp" data-sp="reveal"></div>
''', kw=['explicit wait', 'WebDriverWait', 'expected conditions', 'until', 'polling interval', 'timeout exception', 'visibility', 'presence', 'clickable', 'driver.wait'])

K.lesson('custom', 'Customising waits, and never mixing them', f'''
<p>The wait class takes extra settings: how often to poll, which errors mean "not yet", the total timeout and the message on failure. The documentation example retries an action that raises element not interactable until it works.</p>
{FLUENT}
<h3>Do not mix implicit and explicit waits</h3>
<p>The documentation is direct: do not mix them, because the wait times become unpredictable. Its example is an implicit wait of 10 seconds with an explicit wait of 15 seconds, which can time out after 20 seconds. The reason is that each check of the explicit wait calls find element, and find element now blocks for the implicit wait every time the element is missing.</p>
{MIX}
<p>Three seconds were asked for, and the run gave up after more than four. With the documentation numbers the effect grows to many seconds per failing test. Pick one strategy for a project. Most teams keep the implicit wait at 0 and use explicit waits where they are needed.</p>
{scene('the suite that took an hour longer', '<p>A team set a 10 second implicit wait "to be safe", and their page objects also used 15 second explicit waits. Most tests passed, so nobody noticed. On a day when the login service was down, every one of 300 tests waited about 20 seconds per failed check instead of 15. The run that normally took 20 minutes ran past the CI limit. Removing the implicit wait made failures fast again.</p>')}
{ladder(
    '<p>Do not guess with sleep. Tell Selenium what you are waiting for and let it check again and again until it happens.</p>',
    '<p>An implicit wait makes every find patient. An explicit wait loops over a condition you choose, with a timeout and a polling interval. Use one or the other, not both.</p>',
    '<p>Explicit waits run in the client and send a command per poll. Implicit waits run in the driver inside one Find Element command. Combining them nests one loop inside the other, so the worst case is roughly the explicit timeout plus one whole implicit wait.</p>',
    '<p>Polling trades speed of reaction against commands sent. WebDriver BiDi lets a client subscribe to DOM mutations and network events instead, so future waits can react to the page instead of asking it repeatedly.</p>')}
''', kw=['FluentWait', 'polling', 'ignored exceptions', 'custom wait', 'mixing waits', 'implicit and explicit', 'unpredictable wait times', 'timeout message'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What is the default implicit wait?', ['0', '0.5 s', '10 s', '30 s'], 0,
       'It does not wait unless you ask.', 'The default implicit wait is 0, so a missing element fails at once.')
K.quiz('e', 'Why is time.sleep(5) a poor way to wait?', ['It is not allowed', 'Too short fails, too long wastes time on every run', 'It stops the browser', 'It clears the page'], 1,
       'The code cannot know the right length.', 'A fixed sleep is either too short and flaky, or too long and slow.')
K.quiz('e', 'What does an explicit wait return when its condition gives an element?', ['True', 'The element', 'Nothing', 'The driver'], 1,
       'Used with presence or visibility.', 'until returns the truthy result of the condition, such as the element it found.')
K.quiz('m', 'An implicit wait is 10 s and the element appears after 2 s. How long does find element take?', ['10 s', 'About 2 s', '0 s', '12 s'], 1,
       'It returns as soon as it finds.', 'The driver returns the element as soon as it is located.')
K.quiz('m', 'Which default polling interval does Python WebDriverWait use?', ['100 ms', '200 ms', '0.5 s', '1 s'], 2,
       'Look at the table.', 'POLL_FREQUENCY is 0.5 s in the Python binding. Java uses 500 ms and JavaScript 200 ms.')
K.quiz('m', 'An element is present but hidden. Which condition should you wait for before typing?', ['presence', 'visibility', 'staleness', 'title contains'], 1,
       'An element must be present and displayed.', 'Typing needs a displayed element. Wait for visibility.')
K.quiz('m', 'What does JavaScript driver.wait do when you pass no timeout?', ['Waits 30 s', 'Waits forever', 'Fails at once', 'Waits 2 s'], 1,
       'The default is 0.', 'A timeout of 0 means wait indefinitely in the JavaScript binding.')
K.quiz('h', 'According to the documentation, what can happen with an implicit wait of 10 s and an explicit wait of 15 s?', ['Timeout after 10 s', 'Timeout after 15 s exactly', 'Timeout after about 20 s', 'No timeout'], 2,
       'The waits nest.', 'Mixing them can cause a timeout to occur after 20 seconds.')
K.quiz('h', 'Which error does Python WebDriverWait ignore by default while looping?', ['TimeoutException', 'NoSuchElementException', 'StaleElementReferenceException', 'None'], 1,
       'The one that means not there yet.', 'IGNORED_EXCEPTIONS defaults to NoSuchElementException.')
K.quiz('x', 'Why is the mixed wait longer than the explicit timeout?', ['Selenium adds a bonus', 'Each check calls find element, which blocks for the implicit wait when the element is missing', 'The browser slows down', 'Polling is disabled'], 1,
       'Look inside one check.', 'The explicit loop only checks the clock between checks, and each check can block for the whole implicit wait.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'An explicit wait polls every 0.5 s starting at 0 s. The element appears at 1.2 s. At which check time does the wait return?', '1.5', 'The first check at or after 1.2 s.',
       ['Checks happen at 0, 0.5, 1.0, 1.5 s.', 'At 1.0 s the element is not there yet.', eq('It returns at the 1.5 s check')], check=1.5, unit='s')
K.calc('e', 'A suite has 200 tests, each with one sleep(3). The pages are ready after 1 s on average. How many minutes are wasted per run?', '6.67', 'Wasted seconds per test, then total.',
       ['Each sleep wastes 3 − 1 = 2 s.', '200 × 2 = 400 s.', eq('400 ÷ 60 ≈ 6.67 minutes')], check=6.67, tol=0.01)
K.calc('m', 'With polling every 0.2 s (JavaScript default), the element appears at 1.25 s. When does the wait return?', '1.4', 'Next multiple of 0.2 after 1.25.',
       ['Checks: 1.0, 1.2, 1.4 s.', 'At 1.2 s it is not there yet.', eq('The 1.4 s check succeeds')], check=1.4, unit='s')
K.calc('m', 'An implicit wait of 5 s is set. A test checks that an error banner is absent using find elements, 4 times. How many seconds does that add?', '20', 'Absence takes the full wait.',
       ['An absent element makes find elements wait the full implicit time.', 'Each check costs 5 s.', eq('4 × 5 = 20 s')], check=20, unit='s')
K.calc('h', 'Implicit 2 s, explicit 3 s, poll 0.5 s, element never comes. The Python loop checks, gives up if the time is past the timeout, otherwise sleeps and checks again. When does it give up?', '4.5', 'Each check blocks 2 s.',
       ['Check 1 runs 0 to 2 s and fails. 2 s is not past 3 s, so it sleeps to 2.5 s.', 'Check 2 runs 2.5 to 4.5 s and fails. 4.5 s is past 3 s.', eq('It gives up at about 4.5 s instead of 3 s. The real run on this page took 4.6 s')], check=4.5, unit='s')
K.calc('x', 'The documentation numbers: implicit 10 s, explicit 15 s, poll 0.5 s, element never comes. When does the loop give up?', '20.5', 'Same method.',
       ['Check 1: 0 to 10 s. 10 s is not past 15 s, so sleep to 10.5 s.', 'Check 2: 10.5 to 20.5 s. 20.5 s is past 15 s.', eq('About 20.5 s, matching the documentation warning of a timeout after 20 seconds')], check=20.5, unit='s')

# ---------------------------------------------------------------- assignments
K.assign('pollret', 'm', 'When does an explicit wait return?',
         '<p>Write <code>returns_at(appear, timeout, poll)</code>. Checks happen at 0, poll, 2 × poll and so on. Return the time of the first check at or after <code>appear</code>, rounded to 2 decimals. If that check would be later than <code>timeout</code>, return the string <code>"timeout"</code>.</p>',
         '''
def returns_at(appear, timeout, poll):
    # your code here
    pass
''', [('returns_at(1.2, 2, 0.5)', 1.5), ('returns_at(0, 2, 0.5)', 0), ('returns_at(1.25, 2, 0.2)', 1.4), ('returns_at(3, 2, 0.5)', 'timeout')],
         '''
def returns_at(appear, timeout, poll):
    t = 0
    while round(t, 6) < appear:
        t += poll
    t = round(t, 2)
    return t if t <= timeout else "timeout"
''', 'Step a time variable by poll until it reaches appear.', '<p>Rounding protects against floating point steps such as 0.2 + 0.2 + 0.2 giving 0.6000000000000001.</p>')
K.assign('mixed', 'h', 'How long does a mixed wait really take?',
         '<p>Write <code>gives_up(implicit, timeout, poll)</code> for an element that never appears, following the Python loop. Start at t = 0. Each check takes <code>implicit</code> seconds and fails. If t is then past <code>timeout</code>, return t rounded to 2 decimals. Otherwise sleep <code>poll</code> seconds and check again.</p>',
         '''
def gives_up(implicit, timeout, poll):
    # your code here
    pass
''', [('gives_up(2, 3, 0.5)', 4.5), ('gives_up(10, 15, 0.5)', 20.5), ('gives_up(0, 2, 0.5)', 2.5)],
         '''
def gives_up(implicit, timeout, poll):
    t = 0
    while True:
        t += implicit
        if t > timeout:
            return round(t, 2)
        t += poll
''', 'Add the implicit time, compare, then add the poll.', '<p>With no implicit wait the loop ends one poll after the timeout at most. With one, the last check can start just before the timeout and still block for a whole implicit wait.</p>')

K.must('The race', 'Content added or shown by JavaScript after load is not covered by navigation waits. Finding it too early fails. Do not use fixed sleeps.')
K.must('Implicit wait', 'A session setting, default 0. Every find keeps looking up to that long and returns as soon as the element appears. It only waits for presence.')
K.must('Explicit wait', 'A loop with a condition, timeout and polling interval. Defaults: Java 500 ms, Python 0.5 s, JavaScript 200 ms. JavaScript waits forever without a timeout.')
K.must('Expected conditions', 'presence, visibility, clickable, text present, title contains, staleness. Wait for visibility before typing.')
K.must('Never mix', 'Implicit plus explicit makes waits unpredictable: 10 s with 15 s can time out after about 20 s. Keep implicit at 0 and use explicit waits.')

T = K.topic(
    slug='waits', topic='waits',
    step=(4, 'Synchronise and control', 'se-control', 'Waits, windows, tabs, frames and alerts, the Actions API, JavaScript, cookies and print.', 'Intermediate'),
    title='Waiting strategies: implicit, explicit and fluent', short='Waits', badge='4.1', minutes=55, added='2026-10-29',
    lead='Beat the race between your code and the page. See why sleeps fail, how implicit and explicit waits work, which conditions to wait for, and prove with a real run why the two must never be mixed.',
    desc='The race condition behind flaky tests on dynamic.html, a timeline animation of five strategies, implicit waits, explicit waits with lambdas and expected conditions, polling and ignored errors per language, custom messages, FluentWait, and a real run showing how mixing implicit and explicit waits stretches the timeout.',
    summary='Why tests race the page, implicit and explicit waits, expected conditions, custom waits and why not to mix them.',
    keywords=['waits', 'implicit wait', 'explicit wait', 'webdriverwait', 'expected conditions', 'fluentwait', 'flaky tests', 'synchronization'],
    recap='<p>Pages change after load, so tests must wait. Sleeps are too short or too long. An implicit wait makes every find patient but only for presence. An explicit wait loops over the exact condition you need, with a timeout and polling interval. Never mix the two.</p>')
