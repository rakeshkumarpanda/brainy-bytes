# Chapter 5.4: errors, stale elements and logs. Sources: selenium.dev documentation (Troubleshooting: Understanding
# common errors with the W3C error to exception table, Logging), the W3C WebDriver specification (errors, web element
# reference and the element store of each browsing context, get a known element), the binding sources in box/ (logger
# names) and real runs: stale and no such element in Chrome 153, client logs in all three languages, ChromeDriver logs,
# and the session not created message for a ChromeDriver 147 recorded in chapter 1.3.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, src, flow

K = Kit()

STALE = tri('stale', 'Make an element reference fail three ways, and fix each one', java=r'''
import org.openqa.selenium.By;
import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.StaleElementReferenceException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

public class Stale {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/web-form.html");
        WebElement box = driver.findElement(By.name("my-text"));  ## The driver gives back a reference to this exact node.
        driver.navigate().refresh();  ## The page is rebuilt. The old node is gone, a new one with the same name takes its place.
        try {
            box.sendKeys("x");
        } catch (StaleElementReferenceException e) {
            System.out.println("1. after refresh: " + e.getClass().getSimpleName());
        }
        box = driver.findElement(By.name("my-text"));  ## The fix: find it again.
        box.sendKeys("found again");
        System.out.println("   fixed: " + box.getAttribute("value"));

        driver.get("https://www.selenium.dev/selenium/web/iframes.html");
        driver.switchTo().frame("iframe1");
        WebElement email = driver.findElement(By.id("email"));  ## Found inside the frame.
        driver.switchTo().defaultContent();
        try {
            email.getAttribute("type");
        } catch (NoSuchElementException e) {
            System.out.println("2. outside its frame: " + e.getClass().getSimpleName());  ## The reference is fine, but this context does not know it.
        }
        driver.switchTo().frame("iframe1");  ## The fix: switch back to the context where it was found.
        System.out.println("   fixed: " + email.getAttribute("type"));

        driver.get("https://www.selenium.dev/selenium/web/blank.html");  ## Leave the page completely.
        try {
            email.getAttribute("type");
        } catch (NoSuchElementException e) {
            System.out.println("3. after leaving the page: " + e.getClass().getSimpleName());  ## Go back to the page and find it again.
        }
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/web-form.html")
box = driver.find_element(By.NAME, "my-text")  ## The driver gives back a reference to this exact node.
driver.refresh()  ## The page is rebuilt. The old node is gone, a new one with the same name takes its place.
try:
    box.send_keys("x")
except StaleElementReferenceException as e:
    print("1. after refresh:", type(e).__name__)
box = driver.find_element(By.NAME, "my-text")  ## The fix: find it again.
box.send_keys("found again")
print("   fixed:", box.get_attribute("value"))

driver.get("https://www.selenium.dev/selenium/web/iframes.html")
driver.switch_to.frame("iframe1")
email = driver.find_element(By.ID, "email")  ## Found inside the frame.
driver.switch_to.default_content()
try:
    email.get_attribute("type")
except NoSuchElementException as e:
    print("2. outside its frame:", type(e).__name__)  ## The reference is fine, but this context does not know it.
driver.switch_to.frame("iframe1")  ## The fix: switch back to the context where it was found.
print("   fixed:", email.get_attribute("type"))

driver.get("https://www.selenium.dev/selenium/web/blank.html")  ## Leave the page completely.
try:
    email.get_attribute("type")
except NoSuchElementException as e:
    print("3. after leaving the page:", type(e).__name__)  ## Go back to the page and find it again.
driver.quit()
''', js=r'''
const { Builder, Browser, By, error } = require('selenium-webdriver');

(async function stale() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/web-form.html');
  let box = await driver.findElement(By.name('my-text'));  ## The driver gives back a reference to this exact node.
  await driver.navigate().refresh();  ## The page is rebuilt. The old node is gone, a new one with the same name takes its place.
  try {
    await box.sendKeys('x');
  } catch (e) {
    if (!(e instanceof error.StaleElementReferenceError)) throw e;
    console.log('1. after refresh: ' + e.name);
  }
  box = await driver.findElement(By.name('my-text'));  ## The fix: find it again.
  await box.sendKeys('found again');
  console.log('   fixed: ' + await box.getAttribute('value'));

  await driver.get('https://www.selenium.dev/selenium/web/iframes.html');
  const frame = await driver.findElement(By.id('iframe1'));
  await driver.switchTo().frame(frame);
  const email = await driver.findElement(By.id('email'));  ## Found inside the frame.
  await driver.switchTo().defaultContent();
  try {
    await email.getAttribute('type');
  } catch (e) {
    if (!(e instanceof error.NoSuchElementError)) throw e;
    console.log('2. outside its frame: ' + e.name);  ## The reference is fine, but this context does not know it.
  }
  await driver.switchTo().frame(frame);  ## The fix: switch back to the context where it was found.
  console.log('   fixed: ' + await email.getAttribute('type'));

  await driver.get('https://www.selenium.dev/selenium/web/blank.html');  ## Leave the page completely.
  try {
    await email.getAttribute('type');
  } catch (e) {
    if (!(e instanceof error.NoSuchElementError)) throw e;
    console.log('3. after leaving the page: ' + e.name);  ## Go back to the page and find it again.
  }
  await driver.quit();
})();
''', expect='   fixed: email')

LOGS = tri('logs', 'Turn on the client log and see every command', java=r'''
import java.util.logging.Handler;
import java.util.logging.Level;
import java.util.logging.LogRecord;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class ClientLog {
    static final Logger HTTP = Logger.getLogger("org.openqa.selenium.remote.http.jdk.JdkHttpClient");  ## Keep a reference, or Java may forget the level you set.

    public static void main(String[] args) {
        HTTP.setLevel(Level.FINE);  ## Java logs at INFO by default. Request lines are written at FINE.
        HTTP.addHandler(new Handler() {  ## A tiny handler that prints one line per request.
            public void publish(LogRecord r) {
                String m = new SimpleFormatter().formatMessage(r);  ## The record holds a pattern plus values, so format it first.
                if (m.startsWith("Executing request: ")) {
                    String line = m.substring(19).replaceFirst("^\\((\\w+)\\)", "$1").replaceAll("/session/[0-9a-f]{32}", "/session/{id}");  ## Hide the session id, which changes every run.
                    System.out.println(line.split(" \\{")[0]);  ## Keep the method and path, drop the JSON body.
                }
            }
            public void flush() {}
            public void close() {}
        });
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/blank.html");
        driver.getTitle();
        driver.quit();
    }
}
''', py=r'''
import logging
import re

from selenium import webdriver


class Requests(logging.Handler):  ## A tiny handler that prints one line per request.
    def emit(self, record):
        m = re.match(r"(GET|POST|DELETE) http://[^/]+(\S*)", record.getMessage())  ## Request lines start with the method and the URL.
        if m:
            print(m.group(1), re.sub("/session/[0-9a-f]{32}", "/session/{id}", m.group(2)))  ## Hide the session id, which changes every run.


log = logging.getLogger("selenium")  ## The parent of every Selenium logger in Python.
log.setLevel(logging.DEBUG)  ## Python logs at WARNING by default. Requests are written at DEBUG.
log.addHandler(Requests())
driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/blank.html")
driver.title
driver.quit()
''', js=r'''
const { Builder, Browser, logging } = require('selenium-webdriver');

const http = logging.getLogger('driver.http.Executor');  ## In selenium-webdriver 4.51 the HTTP lines come from this logger.
http.setLevel(logging.Level.FINER);  ## Request lines are written at FINER.
http.addHandler(entry => {  ## A tiny handler that prints one line per request.
  const m = /^\[[\w.]+\] >>> (\w+) (\S+)$/.exec(entry.message);  ## Each message starts with the logger name in square brackets.
  if (m) console.log(m[1] + ' ' + m[2].replace(/\/session\/[0-9a-f]{32}/, '/session/{id}'));  ## Hide the session id, which changes every run.
});

(async function clientLog() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/blank.html');
  await driver.getTitle();
  await driver.quit();
})();
''', expect='/session/{id}/url')

DRIVERLOG = tri('driverlog', 'Ask ChromeDriver for its own log', java=r'''
import java.io.File;
import java.nio.file.Files;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeDriverService;
import org.openqa.selenium.chromium.ChromiumDriverLogLevel;

public class DriverLog {
    public static void main(String[] args) throws Exception {
        File log = new File("chromedriver.log");
        ChromeDriverService service = new ChromeDriverService.Builder()
            .withLogFile(log)  ## Where ChromeDriver writes its log.
            .withLogLevel(ChromiumDriverLogLevel.DEBUG)  ## More detail than the default.
            .build();
        WebDriver driver = new ChromeDriver(service);
        driver.get("https://www.selenium.dev/selenium/web/blank.html");
        driver.quit();
        for (String line : Files.readAllLines(log.toPath())) {
            if (line.contains("] COMMAND ")) System.out.println(line.split("] COMMAND ")[1].split(" ")[0]);  ## Print the name of each command the driver received.
        }
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

service = Service(log_output="chromedriver.log", service_args=["--log-level=DEBUG"])  ## Where ChromeDriver writes its log, and how much.
driver = webdriver.Chrome(service=service)
driver.get("https://www.selenium.dev/selenium/web/blank.html")
driver.quit()
for line in open("chromedriver.log"):
    if "] COMMAND " in line:
        print(line.split("] COMMAND ")[1].split(" ")[0])  ## Print the name of each command the driver received.
''', js=r'''
const fs = require('fs');
const { Builder, Browser } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');

(async function driverLog() {
  const service = new chrome.ServiceBuilder().loggingTo('chromedriver.log').enableVerboseLogging();  ## Where ChromeDriver writes its log, with full detail.
  const driver = await new Builder().forBrowser(Browser.CHROME).setChromeService(service).build();
  await driver.get('https://www.selenium.dev/selenium/web/blank.html');
  await driver.quit();
  for (const line of fs.readFileSync('chromedriver.log', 'utf8').split('\n')) {
    if (line.includes('] COMMAND ')) console.log(line.split('] COMMAND ')[1].split(' ')[0]);  ## Print the name of each command the driver received.
  }
})();
''', expect='Navigate')

ERRORS = [
    ('no such element', 'NoSuchElementException', 'NoSuchElementException', 'NoSuchElementError', 'Wrong place, wrong time or a changed locator. Check the page, add an explicit wait, update the locator.'),
    ('stale element reference', 'StaleElementReferenceException', 'StaleElementReferenceException', 'StaleElementReferenceError', 'The node was replaced, for example by a refresh or a re render. Find it again.'),
    ('element click intercepted', 'ElementClickInterceptedException', 'ElementClickInterceptedException', 'ElementClickInterceptedError', 'Something covers the element: a sticky bar, a modal, an animation. Wait for it to go, or scroll.'),
    ('element not interactable', 'ElementNotInteractableException', 'ElementNotInteractableException', 'ElementNotInteractableError', 'Hidden, zero size or not ready. Wait until visible and enabled.'),
    ('invalid selector', 'InvalidSelectorException', 'InvalidSelectorException', 'InvalidSelectorError', 'The CSS or XPath is broken, or an XPath was passed to a CSS locator.'),
    ('timeout', 'TimeoutException', 'TimeoutException', 'TimeoutError', 'An explicit wait ran out. The message says which condition.'),
    ('script timeout', 'ScriptTimeoutException', 'TimeoutException', 'ScriptTimeoutError', 'A script took longer than the script timeout.'),
    ('unexpected alert open', 'UnhandledAlertException', 'UnexpectedAlertPresentException', 'UnexpectedAlertOpenError', 'An alert was left open. Handle it where it opens.'),
    ('no such window', 'NoSuchWindowException', 'NoSuchWindowException', 'NoSuchWindowError', 'The window was closed and the test did not switch back.'),
    ('invalid session id', 'NoSuchSessionException', 'InvalidSessionIdException', 'NoSuchSessionError', 'The session was quit or crashed. Look for a quit earlier in the test.'),
    ('session not created', 'SessionNotCreatedException', 'SessionNotCreatedException', 'SessionNotCreatedError', 'Driver and browser versions do not match, or the browser could not start.'),
]

K.lesson('errors', 'Read an error the right way', f'''
<p>Every failure from a driver is one of the errors named in the W3C specification, such as <code>no such element</code>. Each language turns it into its own class, and the names are not always the same. The documentation keeps a table of them. These are the ones you will meet most:</p>
{table(['W3C error', 'Java', 'Python', 'JavaScript', 'Usual cause and fix'], [list(r) for r in ERRORS])}
<p>Read a failure in this order: the error name, then the message, then the line of your code in the stack trace. The error name narrows the cause to one row above. The message often names the locator or the condition. The line tells you which step of the test failed, which can be one step after the real cause, as the forgotten alert in chapter 4.2 showed.</p>
{shell('A driver that is too old for the browser (recorded in chapter 1.3)', 'python main.py', out="""session not created: This version of ChromeDriver only supports Chrome version 147""", cap='What the Python example printed from the exception message')}
{note('Search the error name together with the first line of the message. Ignore the long list of numbers under Stacktrace in Chrome messages. Those are addresses inside ChromeDriver, not your code.', 'tip')}
''', kw=['errors', 'exceptions', 'no such element', 'stale element', 'click intercepted', 'not interactable', 'invalid selector', 'timeout', 'session not created', 'stack trace'])

K.lesson('stale', 'Stale elements and the element store', f'''
<p>When you find an element, the driver does not send the element to your code. It stores the node in a table that belongs to the current browsing context, the window or frame you are in, and sends back an id for it. Every later command with that element sends the id back, and the driver looks it up in the table of the <b>current</b> context.</p>
{viz('se-stale')}
{STALE}
<p>The run shows three different failures. After a refresh the id is still known, but its node has been removed from the page, so the driver reports <b>stale element reference</b>. Outside its frame, and after leaving the page, Chrome 153 reported <b>no such element</b>, because the id is looked up in a context that never stored it. The documentation groups all three under stale elements and gives the same fixes: find it again, or switch back to the right context first.</p>
{table(['What happened', 'Error in this run', 'Fix'], [
    ['Refresh, re render, list re sorted', 'stale element reference', 'Find the element again just before you use it'],
    ['Switched to another frame or window', 'no such element', 'Switch back to the context where it was found'],
    ['Navigated to another page', 'no such element', 'Go back to the page and find it again']])}
{note('Page objects that find elements inside their methods, as in chapter 5.2, rarely meet stale elements, because they look the element up fresh each time.', 'tip')}
''', kw=['stale element', 'stale element reference', 'element reference', 'element store', 'refresh', 'relocate', 'browsing context', 'no such element'])

K.lesson('logs', 'Logs: what the client sent and what the driver did', f'''
<p>When an error makes no sense, look at the conversation itself. Two logs show it from both ends: the <b>client log</b> from your Selenium library, and the <b>driver log</b> from ChromeDriver.</p>
{LOGS}
<p>All three logs show the same W3C conversation as chapter 1.2: New Session, then one request per command, then Delete Session. Two differences are visible. JavaScript first asked the driver <code>GET /status</code> to check it was ready. Java asked the browser DevTools endpoint for <code>GET /json/version</code> right after New Session, which the Java binding does for Chrome sessions. Each language uses its own logging system:</p>
{table(['Language', 'Logger', 'Default level', 'Level that shows requests'], [
    ['Java', 'java.util.logging, for example org.openqa.selenium.remote.http.jdk.JdkHttpClient', 'INFO', 'FINE'],
    ['Python', 'logging, under the name selenium', 'WARNING', 'DEBUG'],
    ['JavaScript', 'selenium-webdriver logging, driver.http.Executor in 4.51', 'OFF until set', 'FINER']])}
{note('The documentation shows the JavaScript logger as getLogger("webdriver"). In selenium-webdriver 4.51 that name printed nothing in our run, while driver.http and driver.http.Executor printed every request. In pytest, the documentation adds that logs of passing tests are hidden unless you run pytest -s -p no:logging.', 'warn')}
{DRIVERLOG}
{ladder(
    '<p>An error name tells you what kind of problem it is. Most failures are a locator, a missing wait, something covering the element, or a page that changed.</p>',
    '<p>Match the error to its cause: no such element, stale, intercepted, not interactable, timeout. Find elements again after the page changes and switch back to the right context. Turn on logs when the cause is unclear.</p>',
    '<p>The driver keeps an element store per browsing context. An id from another context is unknown there, and an id whose node left the document is stale. The client log shows each W3C request, the driver log shows each command the driver received.</p>',
    '<p>The Grid adds its own logs per component, and BiDi can stream console messages and JavaScript errors from the page into the test, as chapter 6.2 shows.</p>')}
''', kw=['logging', 'logs', 'debug', 'client log', 'driver log', 'chromedriver log', 'log level', 'java util logging', 'pytest logs'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'An element is found, the page refreshes, and the test clicks it. Which error is likely?', ['no such window', 'stale element reference', 'invalid selector', 'timeout'], 1,
       'The node was replaced.', 'After a refresh the old node is gone, so the reference is stale.')
K.quiz('e', 'What is the usual fix for a stale element?', ['Restart the browser', 'Find the element again', 'Increase the timeout', 'Use XPath'], 1,
       'Get a fresh reference.', 'Find it again just before using it.')
K.quiz('e', 'Which error names the W3C error invalid session id in Java?', ['InvalidSessionIdException', 'NoSuchSessionException', 'SessionNotCreatedException', 'WebDriverException'], 1,
       'Java differs here.', 'The documentation table maps invalid session id to NoSuchSessionException in Java.')
K.quiz('m', 'An element found inside an iframe is used after defaultContent(). What did Chrome 153 report in the run?', ['stale element reference', 'no such element', 'no such frame', 'It worked'], 1,
       'Look at line 2 of the output.', 'The id is looked up in the top document store, which never held it.')
K.quiz('m', 'A click fails with element click intercepted. What is a likely cause?', ['The locator is wrong', 'Another element such as a sticky bar or modal covers it', 'The session ended', 'The page has no title'], 1,
       'Something is on top.', 'The click would land on a different element.')
K.quiz('m', 'Which Python logger name covers every Selenium logger?', ['root', 'selenium', 'webdriver', 'urllib3'], 1,
       'The package name.', 'Python loggers follow module names, so selenium is the parent of all.')
K.quiz('m', 'session not created: This version of ChromeDriver only supports Chrome version 147. What should you do?', ['Add a wait', 'Use a driver that matches the browser, for example let Selenium Manager pick it', 'Change the locator', 'Use JavaScript'], 1,
       'Versions.', 'The driver and the browser must match. Removing the old driver from PATH lets Selenium Manager choose.')
K.quiz('h', 'Which log shows the commands from the driver side, such as COMMAND Navigate?', ['The client log', 'The ChromeDriver log', 'The browser console', 'The test report'], 1,
       'Driver side.', 'ChromeDriver writes COMMAND and RESPONSE lines to its own log.')
K.quiz('h', 'A test fails at line 40, but the real cause is an alert opened at line 38. Why does the trace point at 40?', ['A bug in Selenium', 'The error is raised by the next command after the cause', 'Line numbers are wrong', 'Alerts are slow'], 1,
       'The next command meets the problem.', 'The error appears at the first command that runs into the state left behind.')
K.quiz('x', 'In JavaScript with selenium-webdriver 4.51, which logger printed the HTTP requests in the run?', ['webdriver', 'driver.http.Executor', 'selenium', 'console'], 1,
       'Look at the example.', 'The HTTP request lines come from driver.http.Executor at level FINER.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A client log shows New Session, 5 commands and Delete Session. How many HTTP requests is that?', '7', 'Count all.',
       ['New Session: 1.', 'Commands: 5. Delete: 1.', eq('1 + 5 + 1 = 7 requests')], check=7)
K.calc('e', 'A suite of 300 tests has 12 failures, 9 of them no such element. What percent of failures is that?', '75', 'Part of the failures.',
       ['9 out of 12.', '9 ÷ 12 = 0.75.', eq('75 %')], check=75, unit='%')
K.calc('m', 'Finding an element again costs one request of 15 ms. A test uses an element 8 times and finds it again each time. How many ms of extra requests is that?', '105', 'The first find is needed anyway.',
       ['8 uses need 8 finds if each use finds again.', 'One find was needed anyway, so 7 are extra.', eq('7 × 15 = 105 ms')], check=105, unit='ms')
K.calc('m', 'A driver log has a COMMAND and a RESPONSE line per command. A run sent 3 commands. How many such lines are there?', '6', 'Two per command.',
       ['3 commands.', '2 lines each.', eq('3 × 2 = 6 lines')], check=6)
K.calc('h', 'A test is 3 frames deep and uses an element found at the top. How many switches does it need before the element works again, at least?', '1', 'One command.',
       ['parentFrame three times would work.', 'defaultContent goes to the top in one command.', eq('1 switch')], check=1)
K.calc('x', 'A flaky suite fails 4 % of 500 tests. Fixing stale elements removes 60 % of those failures. How many failures remain?', '8', 'First the count, then the rest.',
       ['4 % of 500 = 20 failures.', '60 % of 20 = 12 fixed.', eq('20 − 12 = 8 remain')], check=8)

# ---------------------------------------------------------------- assignments
K.assign('errfix', 'e', 'Suggest a fix from the error name',
         '<p>Write <code>first_fix(error)</code> for a W3C error name. Return "wait" for "no such element", "timeout" and "element not interactable", "find again" for "stale element reference", "switch back" for "no such window", "check versions" for "session not created" and "look" for anything else.</p>',
         '''
def first_fix(error):
    # your code here
    pass
''', [('first_fix("no such element")', 'wait'), ('first_fix("stale element reference")', 'find again'), ('first_fix("session not created")', 'check versions'), ('first_fix("javascript error")', 'look')],
         '''
def first_fix(error):
    if error in ("no such element", "timeout", "element not interactable"):
        return "wait"
    fixes = {
        "stale element reference": "find again",
        "no such window": "switch back",
        "session not created": "check versions",
    }
    return fixes.get(error, "look")
''', 'A tuple for the wait group and a dict for the rest.', '<p>A first guess, not a diagnosis: a no such element can also be a wrong locator, which waiting will not fix.</p>')
K.assign('countcmd', 'm', 'Count commands in a driver log',
         '<p>Write <code>count_commands(lines)</code>. Each line of a ChromeDriver log that contains "] COMMAND " has the command name right after it, followed by a space. Return a dict from command name to how many times it appears.</p>',
         '''
def count_commands(lines):
    # your code here
    pass
''', [('count_commands(["[1][INFO]: [s] COMMAND Navigate {", "[2][INFO]: [s] RESPONSE Navigate", "[3][INFO]: [s] COMMAND Navigate {"])', {'Navigate': 2}),
      ('count_commands(["[1][INFO]: [s] COMMAND InitSession {", "[2][INFO]: [s] COMMAND Quit {"])', {'InitSession': 1, 'Quit': 1}), ('count_commands([])', {})],
         '''
def count_commands(lines):
    counts = {}
    for line in lines:
        if "] COMMAND " in line:
            name = line.split("] COMMAND ")[1].split(" ")[0]
            counts[name] = counts.get(name, 0) + 1
    return counts
''', 'Split on the marker, then on the first space.', '<p>The same split is used in the driver log example on this page.</p>')

K.must('Error names', 'Each W3C error has a class per language. Read the name, then the message, then your line in the trace.')
K.must('Stale element', 'The node behind a reference was replaced, for example by a refresh. Find the element again.')
K.must('Context', 'An element found in one frame or window is unknown in another. Switch back before using it.')
K.must('Client log', 'Java: java.util.logging at FINE. Python: logger selenium at DEBUG. JavaScript 4.51: driver.http.Executor at FINER.')
K.must('Driver log', 'ChromeDriver writes COMMAND and RESPONSE lines when its service is given a log file and a verbose level.')

T = K.topic(
    slug='troubleshooting', topic='troubleshooting',
    step=(5, 'Build a test suite', 'se-suite', 'Test frameworks, page objects, good practices and the errors you will meet.', 'Intermediate'),
    title='Troubleshooting: errors, stale elements and logs', short='Troubleshooting', badge='5.4', minutes=50, added='2026-10-29',
    lead='Read an error the right way, understand why element references go stale or unknown, and turn on the client and driver logs to see exactly what was sent.',
    desc='The W3C errors and their Java, Python and JavaScript classes from the documentation table, a real session not created message, an animation of the element store, real stale element and no such element runs with fixes, client logs in all three languages, the ChromeDriver log, and a note where the documentation and selenium-webdriver 4.51 differ.',
    summary='Common errors, stale elements and logging in Java, Python and JavaScript.',
    keywords=['troubleshooting', 'errors', 'exceptions', 'stale element', 'no such element', 'logging', 'debug', 'chromedriver log', 'session not created'],
    recap='<p>Read the error name, the message and your line in the trace. Stale means the node was replaced, so find it again. An element from another frame or page is unknown, so switch back or find it again. Turn on the client log or the ChromeDriver log to see every request and command.</p>')
