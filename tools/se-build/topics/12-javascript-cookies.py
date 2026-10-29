# Chapter 4.4: executing JavaScript and working with cookies. Sources: selenium.dev documentation (Execute script in
# Browser interactions, Working with cookies, Timeouts script), the W3C WebDriver specification (Execute Script,
# Execute Async Script, cookie commands and the invalid cookie domain error) and real runs on the Selenium test pages
# javascriptPage.html and blank.html.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, src, flow

K = Kit()


JSRUN = tri('jsrun', 'Run JavaScript, pass an element in, and see what type comes back', java=r'''
import java.util.List;
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

public class RunScript {
    static String type(Object o) { return o == null ? "null" : o.getClass().getSimpleName(); }  ## The Java class of whatever came back.

    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        JavascriptExecutor js = (JavascriptExecutor) driver;  ## Every driver class implements JavascriptExecutor, so this cast is safe.
        driver.get("https://www.selenium.dev/selenium/web/javascriptPage.html");
        for (String script : List.of("return 42", "return 4.5", "return 'hi'", "return [1, 'a']", "return {a: 1}", "return undefined", "return document.getElementById('dynamo')", "1 + 1")) {
            System.out.println(script + " -> " + type(js.executeScript(script)));  ## Run the script as the body of a function and convert the result.
        }
        WebElement dinner = driver.findElement(By.id("dynamo"));
        System.out.println("arguments: " + js.executeScript("return arguments[0].innerText + ' / ' + arguments[1]", dinner, 7));  ## Extra arguments arrive in the script as arguments[0], arguments[1] and so on.
        js.executeScript("arguments[0].click();", driver.findElement(By.id("updatediv")));  ## A click done by JavaScript. It skips the checks a real click makes.
        System.out.println("after js click: " + dinner.getText());
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/javascriptPage.html")
for script in ["return 42", "return 4.5", "return 'hi'", "return [1, 'a']", "return {a: 1}", "return undefined", "return document.getElementById('dynamo')", "1 + 1"]:
    print(script, "->", type(driver.execute_script(script)).__name__)  ## Run the script as the body of a function and convert the result.
dinner = driver.find_element(By.ID, "dynamo")
print("arguments:", driver.execute_script("return arguments[0].innerText + ' / ' + arguments[1]", dinner, 7))  ## Extra arguments arrive in the script as arguments[0], arguments[1] and so on.
driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "updatediv"))  ## A click done by JavaScript. It skips the checks a real click makes.
print("after js click:", dinner.text)
driver.quit()
''', js=r'''
const { Builder, Browser, By } = require('selenium-webdriver');

const type = v => v === null ? 'null' : Array.isArray(v) ? 'Array' : typeof v === 'object' ? v.constructor.name : typeof v;  ## A readable name for whatever came back.
(async function runScript() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/javascriptPage.html');
  for (const script of ["return 42", "return 4.5", "return 'hi'", "return [1, 'a']", "return {a: 1}", "return undefined", "return document.getElementById('dynamo')", "1 + 1"]) {
    console.log(script + ' -> ' + type(await driver.executeScript(script)));  ## Run the script as the body of a function and convert the result.
  }
  const dinner = await driver.findElement(By.id('dynamo'));
  console.log('arguments: ' + await driver.executeScript("return arguments[0].innerText + ' / ' + arguments[1]", dinner, 7));  ## Extra arguments arrive in the script as arguments[0], arguments[1] and so on.
  await driver.executeScript('arguments[0].click();', await driver.findElement(By.id('updatediv')));  ## A click done by JavaScript. It skips the checks a real click makes.
  console.log('after js click: ' + await dinner.getText());
  await driver.quit();
})();
''', expect='after js click: Fish and chips!')

JSASYNC = tri('jsasync', 'Asynchronous scripts, promises, the script timeout and a JavaScript error', java=r'''
import java.time.Duration;
import org.openqa.selenium.JavascriptException;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.ScriptTimeoutException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class AsyncScript {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        JavascriptExecutor js = (JavascriptExecutor) driver;
        driver.get("https://www.selenium.dev/selenium/web/blank.html");
        Object waited = js.executeAsyncScript("const done = arguments[arguments.length - 1]; setTimeout(() => done('waited'), 300);");  ## Selenium adds a callback as the last argument. The command returns when the script calls it.
        System.out.println("async: " + waited);
        System.out.println("promise: " + js.executeScript("return new Promise(r => setTimeout(() => r('from promise'), 200));"));  ## A returned promise is awaited by the browser before it answers.
        driver.manage().timeouts().scriptTimeout(Duration.ofMillis(200));  ## How long a script may run. The default is 30 seconds.
        try {
            js.executeAsyncScript("const done = arguments[arguments.length - 1]; setTimeout(() => done('late'), 500);");
        } catch (ScriptTimeoutException e) {
            System.out.println("too slow: " + e.getMessage().split("\n")[0]);  ## The callback came after 500 ms, the limit was 200 ms.
        }
        try {
            js.executeScript("return nosuch.thing;");
        } catch (JavascriptException e) {
            System.out.println("broken script: " + e.getMessage().split("\n")[0]);  ## A JavaScript error in the page becomes javascript error.
        }
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.common.exceptions import JavascriptException, TimeoutException

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/blank.html")
waited = driver.execute_async_script("const done = arguments[arguments.length - 1]; setTimeout(() => done('waited'), 300);")  ## Selenium adds a callback as the last argument. The command returns when the script calls it.
print("async:", waited)
print("promise:", driver.execute_script("return new Promise(r => setTimeout(() => r('from promise'), 200));"))  ## A returned promise is awaited by the browser before it answers.
driver.set_script_timeout(0.2)  ## How long a script may run, in seconds. The default is 30.
try:
    driver.execute_async_script("const done = arguments[arguments.length - 1]; setTimeout(() => done('late'), 500);")
except TimeoutException as e:
    print("too slow:", e.msg.split("\n")[0])  ## The callback came after 500 ms, the limit was 200 ms.
try:
    driver.execute_script("return nosuch.thing;")
except JavascriptException as e:
    print("broken script:", e.msg.split("\n")[0])  ## A JavaScript error in the page becomes javascript error.
driver.quit()
''', js=r'''
const { Builder, Browser, error } = require('selenium-webdriver');

(async function asyncScript() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/blank.html');
  const waited = await driver.executeAsyncScript("const done = arguments[arguments.length - 1]; setTimeout(() => done('waited'), 300);");  ## Selenium adds a callback as the last argument. The command returns when the script calls it.
  console.log('async: ' + waited);
  console.log('promise: ' + await driver.executeScript("return new Promise(r => setTimeout(() => r('from promise'), 200));"));  ## A returned promise is awaited by the browser before it answers.
  await driver.manage().setTimeouts({ script: 200 });  ## How long a script may run, in ms. The default is 30000.
  try {
    await driver.executeAsyncScript("const done = arguments[arguments.length - 1]; setTimeout(() => done('late'), 500);");
  } catch (e) {
    if (!(e instanceof error.ScriptTimeoutError)) throw e;
    console.log('too slow: ' + e.message.split('\n')[0]);  ## The callback came after 500 ms, the limit was 200 ms.
  }
  try {
    await driver.executeScript('return nosuch.thing;');
  } catch (e) {
    if (!(e instanceof error.JavascriptError)) throw e;
    console.log('broken script: ' + e.message.split('\n')[0]);  ## A JavaScript error in the page becomes javascript error.
  }
  await driver.quit();
})();
''', expect='promise: from promise')

COOKIES = tri('cookies', 'Add, read, protect and delete cookies', java=r'''
import org.openqa.selenium.Cookie;
import org.openqa.selenium.InvalidCookieDomainException;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class Cookies {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        try {
            driver.manage().addCookie(new Cookie("key", "value"));  ## The browser is still on an empty start page with no domain.
        } catch (InvalidCookieDomainException e) {
            System.out.println("before visiting: " + e.getMessage().split("\n")[0]);
        }
        driver.get("https://www.selenium.dev/selenium/web/blank.html");  ## Visit the domain first. A small page is enough.
        driver.manage().addCookie(new Cookie("key", "value"));
        Cookie c = driver.manage().getCookieNamed("key");  ## Read one cookie by name.
        System.out.println("key: " + c.getValue() + ", domain " + c.getDomain() + ", sameSite " + c.getSameSite() + ", secure " + c.isSecure() + ", httpOnly " + c.isHttpOnly());
        driver.manage().addCookie(new Cookie.Builder("foo", "bar").sameSite("Strict").build());  ## The builder sets the other fields.
        driver.manage().addCookie(new Cookie.Builder("secret", "s").isHttpOnly(true).build());  ## httpOnly hides the cookie from page JavaScript.
        System.out.println("cookies: " + driver.manage().getCookies().size());
        System.out.println("page script sees: " + ((JavascriptExecutor) driver).executeScript("return document.cookie"));
        driver.manage().deleteCookieNamed("foo");
        System.out.println("missing cookie: " + driver.manage().getCookieNamed("foo"));  ## Asking for a cookie that is not there gives null, not an error.
        driver.manage().deleteAllCookies();  ## A clean start, for example before logging in as another user.
        System.out.println("after delete all: " + driver.manage().getCookies().size());
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.common.exceptions import InvalidCookieDomainException

driver = webdriver.Chrome()
try:
    driver.add_cookie({"name": "key", "value": "value"})  ## The browser is still on an empty start page with no domain.
except InvalidCookieDomainException as e:
    print("before visiting:", e.msg.split("\n")[0])
driver.get("https://www.selenium.dev/selenium/web/blank.html")  ## Visit the domain first. A small page is enough.
driver.add_cookie({"name": "key", "value": "value"})
c = driver.get_cookie("key")  ## Read one cookie by name. It comes back as a dict.
print(f"key: {c['value']}, domain {c['domain']}, sameSite {c['sameSite']}, secure {c['secure']}, httpOnly {c['httpOnly']}")
driver.add_cookie({"name": "foo", "value": "bar", "sameSite": "Strict"})  ## Any other field goes in the same dict.
driver.add_cookie({"name": "secret", "value": "s", "httpOnly": True})  ## httpOnly hides the cookie from page JavaScript.
print("cookies:", len(driver.get_cookies()))
print("page script sees:", driver.execute_script("return document.cookie"))
driver.delete_cookie("foo")
print("missing cookie:", driver.get_cookie("foo"))  ## Asking for a cookie that is not there gives None, not an error.
driver.delete_all_cookies()  ## A clean start, for example before logging in as another user.
print("after delete all:", len(driver.get_cookies()))
driver.quit()
''', js=r'''
const { Builder, Browser, error } = require('selenium-webdriver');

(async function cookies() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  try {
    await driver.manage().addCookie({ name: 'key', value: 'value' });  ## The browser is still on an empty start page with no domain.
  } catch (e) {
    if (!(e instanceof error.InvalidCookieDomainError)) throw e;
    console.log('before visiting: ' + e.message.split('\n')[0]);
  }
  await driver.get('https://www.selenium.dev/selenium/web/blank.html');  ## Visit the domain first. A small page is enough.
  await driver.manage().addCookie({ name: 'key', value: 'value' });
  const c = await driver.manage().getCookie('key');  ## Read one cookie by name. It comes back as an object.
  console.log(`key: ${c.value}, domain ${c.domain}, sameSite ${c.sameSite}, secure ${c.secure}, httpOnly ${c.httpOnly}`);
  await driver.manage().addCookie({ name: 'foo', value: 'bar', sameSite: 'Strict' });  ## Any other field goes in the same object.
  await driver.manage().addCookie({ name: 'secret', value: 's', httpOnly: true });  ## httpOnly hides the cookie from page JavaScript.
  console.log('cookies: ' + (await driver.manage().getCookies()).length);
  console.log('page script sees: ' + await driver.executeScript('return document.cookie'));
  await driver.manage().deleteCookie('foo');
  try {
    console.log('missing cookie: ' + await driver.manage().getCookie('foo'));
  } catch (e) {
    console.log('missing cookie: ' + e.name);  ## JavaScript raises NoSuchCookieError here, where Java and Python return null or None.
  }
  await driver.manage().deleteAllCookies();  ## A clean start, for example before logging in as another user.
  console.log('after delete all: ' + (await driver.manage().getCookies()).length);
  await driver.quit();
})();
''', expect='page script sees: key=value; foo=bar')

K.lesson('javascript', 'Run JavaScript in the page', f'''
<p>Sometimes a test needs something that no WebDriver command offers: read a value from the page state, scroll a box by a few pixels, or check how many items a list has without finding them all. <code>executeScript</code> sends a piece of JavaScript to the browser and returns the result to your code.</p>
<p>The browser runs your text as the <b>body of a function</b>. That is why every script that gives back a value starts with <code>return</code>, and why <code>1 + 1</code> on its own gives back nothing. The values you pass after the script arrive as <code>arguments[0]</code>, <code>arguments[1]</code> and so on. A WebElement you pass in becomes the real DOM node inside the script.</p>
{viz('se-script')}
{JSRUN}
<p>The same JavaScript value lands as a different type in each language. Look at the three outputs side by side: a whole number is a <code>Long</code> in Java, an <code>int</code> in Python and a <code>number</code> in JavaScript. A DOM node comes back as a WebElement you can click. <code>undefined</code> and a missing return both become null or None.</p>
{note('A click done with JavaScript always works, even on a covered or disabled element, because it skips every check a user faces. A test that passes with a JavaScript click may be hiding a real bug. Use it only when you know why the real click cannot work.', 'warn')}
{scene('reading the cart total', '<p>A shop keeps the cart in a JavaScript object called window.cart. The test adds three items through the user interface, then reads <code>return window.cart.items.length</code> and <code>return window.cart.total</code> with one script each, and compares them with what the page shows. If the numbers match the state but not the screen, the bug is in the rendering.</p>')}
''', kw=['execute script', 'javascript executor', 'arguments', 'return value', 'javascript click', 'types', 'executeScript'])

K.lesson('async', 'Asynchronous scripts and the script timeout', f'''
<p>Some answers only exist later: a timer, a network call, an animation that ends. <code>executeAsyncScript</code> adds a callback function as the <b>last argument</b> of your script. The command waits until your script calls it, and returns the value you pass to it. A script that returns a <b>promise</b> through plain executeScript is also waited for, because the W3C spec awaits a returned promise.</p>
{JSASYNC}
{table(['Error', 'Java', 'Python', 'JavaScript'], [
    ['The script took longer than the script timeout', 'ScriptTimeoutException', 'TimeoutException', 'ScriptTimeoutError'],
    ['The script threw an error', 'JavascriptException', 'JavascriptException', 'JavascriptError']])}
{note('The script timeout is 30 seconds by default, as chapter 2.1 showed. It covers both sync and async scripts. A short timeout makes a broken async script fail fast.', 'tip')}
''', kw=['execute async script', 'callback', 'promise', 'script timeout', 'javascript error', 'asynchronous'])

K.lesson('cookies', 'Cookies', f'''
<p>A <b>cookie</b> is a small named value that a site stores in the browser and gets back with every request. Logins, language choices, consent banners and shopping carts usually live in cookies. Selenium can add, read and delete them, which lets a test skip a slow login screen or start with the banner already accepted.</p>
{COOKIES}
<p>Four things in this run are worth remembering. A cookie can only be added for the <b>domain the browser is on</b>, so the first call failed with invalid cookie domain on the empty start page. A new cookie on this https page came back with <code>secure</code> true and <code>sameSite</code> Lax, which Chrome chose because the test did not say. The httpOnly cookie <code>secret</code> was stored but not shown to <code>document.cookie</code>. And a missing cookie is not an error in Java and Python, which return null and None, while JavaScript raises NoSuchCookieError.</p>
{table(['Field', 'Meaning'], [
    ['name, value', 'Required. The data.'],
    ['domain, path', 'Where the cookie is sent. They must match the current page.'],
    ['secure', 'Only sent over https.'],
    ['httpOnly', 'Hidden from page JavaScript.'],
    ['sameSite', 'Strict, Lax or None. Whether the cookie goes with requests started by other sites.'],
    ['expiry', 'Seconds since 1970. With no expiry the cookie lasts for the session.']])}
{scene('skip the login screen', '<p>Every test in a suite of 300 needs a logged in user. Logging in through the form takes 4 seconds. The suite logs in once through the API, gets the session cookie, and each test opens a small page on the domain, adds that cookie and goes straight to the page it tests. The form login is still tested once, in its own test.</p>')}
{ladder(
    '<p>Selenium can run JavaScript in the page and give you the answer, and it can read and set the cookies a site stores.</p>',
    '<p>executeScript runs your text as a function body, passes arguments in and converts the return value. executeAsyncScript waits for a callback. Cookies need the browser to be on their domain first.</p>',
    '<p>Execute Script and Execute Async Script are W3C commands that serialise arguments and results as JSON, with element references for DOM nodes. A returned promise is awaited. Cookie commands work on the cookies of the current browsing context domain.</p>',
    '<p>BiDi adds script.evaluate and script.callFunction with realms and preload scripts, and storage.getCookies and storage.setCookie with partitions, which can set cookies without visiting the site first.</p>')}
''', kw=['cookies', 'add cookie', 'get cookie', 'delete cookie', 'httpOnly', 'sameSite', 'secure', 'invalid cookie domain', 'session cookie', 'login'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Why does a script that should give a value start with return?', ['It is optional style', 'The script runs as the body of a function', 'return makes it faster', 'Only Java needs it'], 1,
       'A function body.', 'The browser wraps the script in a function, so only a return statement hands back a value.')
K.quiz('e', 'How does a script read the second value passed after it?', ['args[2]', 'arguments[1]', 'this.second', 'params[1]'], 1,
       'Counting from 0.', 'Extra values arrive as arguments[0], arguments[1] and so on.')
K.quiz('e', 'Before adding a cookie, what must the test do?', ['Nothing', 'Open a page on the cookie domain', 'Restart the browser', 'Clear the cache'], 1,
       'Look at the first line of the cookie run.', 'Cookies can only be added for the domain the browser is currently on.')
K.quiz('m', 'A script returns 42. What type does Java give you?', ['Integer', 'Long', 'Double', 'String'], 1,
       'Check the Java output.', 'Whole numbers come back as Long in Java.')
K.quiz('m', 'In executeAsyncScript, where is the callback?', ['arguments[0]', 'The last argument', 'window.done', 'this.callback'], 1,
       'arguments.length minus 1.', 'Selenium adds the callback as the last argument.')
K.quiz('m', 'A cookie has httpOnly true. What does document.cookie in the page show?', ['The cookie', 'Not this cookie', 'An error', 'Only its name'], 1,
       'Look at the run.', 'httpOnly cookies are hidden from page JavaScript, though Selenium can still read them.')
K.quiz('m', 'Why is a JavaScript click risky in a test?', ['It is slow', 'It skips the checks a real click makes', 'It cannot click links', 'It needs a callback'], 1,
       'Covered or disabled.', 'A JavaScript click works even when a user could not click, so it can hide bugs.')
K.quiz('h', 'A script returns a promise through plain executeScript. What comes back?', ['A promise object', 'The value the promise resolves to', 'null', 'An error'], 1,
       'The run printed from promise.', 'The W3C spec awaits a returned promise and sends back its value.')
K.quiz('h', 'An async script calls its callback after 500 ms and the script timeout is 200 ms. What happens in Python?', ['It returns after 500 ms', 'TimeoutException', 'JavascriptException', 'It returns None'], 1,
       'Python name.', 'Python raises TimeoutException with the message script timeout.')
K.quiz('x', 'A suite logs in by adding a session cookie. What else must it still test?', ['Nothing', 'The real login form, once', 'Cookie expiry only', 'Every page twice'], 1,
       'Do not lose coverage.', 'Skipping the form in every test is fine only if the form itself is tested on its own.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A script is called with 3 extra arguments and run with executeAsyncScript. What is arguments.length inside it?', '4', 'Add the callback.',
       ['3 values you passed.', 'Selenium adds 1 callback at the end.', eq('3 + 1 = 4')], check=4)
K.calc('e', 'The script timeout is 30 s. How many ms is that?', '30000', 'Times 1000.',
       ['1 s is 1,000 ms.', '30 × 1,000.', eq('30,000 ms')], check=30000, unit='ms')
K.calc('m', 'Logging in through the form takes 4 s and adding a cookie takes 0.2 s. How many seconds does a suite of 300 tests save?', '1140', 'Saving per test.',
       ['Each test saves 4 − 0.2 = 3.8 s.', 'There are 300 tests.', eq('300 × 3.8 = 1,140 s, 19 minutes')], check=1140, unit='s')
K.calc('m', 'A cookie expiry is 86,400 s after now. How many hours does it last?', '24', '3,600 s per hour.',
       ['1 hour is 3,600 s.', '86,400 ÷ 3,600.', eq('24 hours')], check=24, unit='h')
K.calc('h', 'An async script resolves after 300 ms. The script timeout is 200 ms. How many ms over the limit is it?', '100', 'Subtract.',
       ['The script needs 300 ms.', 'The limit is 200 ms.', eq('300 − 200 = 100 ms too late, so it fails')], check=100, unit='ms')
K.calc('x', 'A page has 5 cookies. The test adds 2, deletes 1 of its own and 1 of the page, then adds 1 httpOnly cookie. How many cookies does getCookies return?', '6', 'Count step by step.',
       ['5 + 2 = 7.', 'Delete 2: 7 − 2 = 5.', eq('Add 1: 5 + 1 = 6, the httpOnly one included')], check=6)

# ---------------------------------------------------------------- assignments
K.assign('jstype', 'e', 'Which Python type comes back?',
         '<p>Write <code>py_type(js_value)</code>. It gets a description of a JavaScript value: "whole number", "decimal", "text", "true or false", "array", "object", "undefined" or "element". Return the name of the Python type Selenium gives back, as the run on this page printed it.</p>',
         '''
def py_type(js_value):
    # your code here
    pass
''', [('py_type("whole number")', 'int'), ('py_type("array")', 'list'), ('py_type("undefined")', 'NoneType'), ('py_type("element")', 'WebElement')],
         '''
def py_type(js_value):
    table = {
        "whole number": "int",
        "decimal": "float",
        "text": "str",
        "true or false": "bool",
        "array": "list",
        "object": "dict",
        "undefined": "NoneType",
        "element": "WebElement",
    }
    return table[js_value]
''', 'A dictionary from description to type name.', '<p>Java gives Long, Double, String, Boolean, a List, a Map and a WebElement for the same values.</p>')
K.assign('cookiesent', 'm', 'Is the cookie sent?',
         '<p>Write <code>is_sent(cookie, https, path)</code>. <code>cookie</code> is a dict with <code>secure</code> (True or False) and <code>path</code>. Return True when the browser would send it on a request: if the cookie is secure the request must be https, and the request path must start with the cookie path.</p>',
         '''
def is_sent(cookie, https, path):
    # your code here
    pass
''', [('is_sent({"secure": True, "path": "/"}, True, "/shop")', True), ('is_sent({"secure": True, "path": "/"}, False, "/shop")', False), ('is_sent({"secure": False, "path": "/admin"}, True, "/shop")', False)],
         '''
def is_sent(cookie, https, path):
    if cookie["secure"] and not https:
        return False
    return path.startswith(cookie["path"])
''', 'Two checks, secure first.', '<p>Real browsers also check the domain, sameSite and expiry. This exercise keeps two of the rules.</p>')

K.must('executeScript', 'The script runs as a function body. Use return to get a value and arguments[n] to read what you pass in. Elements go in and come back as WebElements.')
K.must('Return types', 'Whole numbers are Long in Java and int in Python, objects are Map and dict, undefined is null or None.')
K.must('Async scripts', 'executeAsyncScript adds a callback as the last argument. A returned promise is also awaited. The script timeout, 30 s by default, limits both.')
K.must('JavaScript click', 'It skips the checks a real click makes, so use it only when you know why the real click cannot work.')
K.must('Cookies', 'Visit the domain first, then add. httpOnly hides a cookie from page scripts. deleteAllCookies gives a clean start.')

T = K.topic(
    slug='javascript-cookies', topic='javascript-cookies',
    step=(4, 'Synchronise and control', 'se-control', 'Waits, windows, tabs, frames and alerts, the Actions API, JavaScript, cookies and print.', 'Intermediate'),
    title='JavaScript execution and cookies', short='JavaScript and cookies', badge='4.4', minutes=45, added='2026-10-29',
    lead='Run your own JavaScript in the page and read the result in Java, Python or JavaScript, wait for asynchronous scripts, and add, read and delete cookies.',
    desc='executeScript as a function body with arguments and an animation of the request, the real return types in each language, JavaScript clicks and their risk, executeAsyncScript, promises, the script timeout and javascript error, and cookies with domain rules, httpOnly, sameSite and secure, from real runs.',
    summary='Running JavaScript in the page, async scripts, and working with cookies.',
    keywords=['execute script', 'javascript executor', 'async script', 'promise', 'script timeout', 'cookies', 'httponly', 'samesite', 'invalid cookie domain'],
    recap='<p>executeScript runs your text as a function body, with arguments in and a converted result out. executeAsyncScript waits for its callback, a returned promise is awaited, and the script timeout limits both. Cookies can be added only for the current domain, httpOnly hides them from page scripts, and deleteAllCookies gives a clean start.</p>')
