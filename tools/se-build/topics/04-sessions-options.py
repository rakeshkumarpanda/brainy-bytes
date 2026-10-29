# Chapter 2.1: sessions, options, capabilities, page load strategy, timeouts and the driver service. Sources:
# selenium.dev documentation (Driver sessions, Browser options, Chrome specific functionality, Driver service,
# Remote WebDriver, Upgrade to Selenium 4), the W3C WebDriver specification (capabilities, timeouts, the Status
# endpoint) and real runs against Chrome 153 recorded when the page was built.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, src, flow

K = Kit()

CAPS = tri('caps', 'Ask for a session with options, then read what the browser agreed to', java=r'''
import org.openqa.selenium.Capabilities;
import org.openqa.selenium.PageLoadStrategy;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

public class SessionCaps {
    public static void main(String[] args) {
        ChromeOptions options = new ChromeOptions();  ## An Options object describes the session you want. browserName is already set to chrome.
        options.addArguments("--headless=new");  ## A Chrome command line switch: run without a visible window.
        options.addArguments("--window-size=1280,800");  ## Another switch: the size of the browser window.
        options.setPageLoadStrategy(PageLoadStrategy.EAGER);  ## A W3C capability: get() returns at DOMContentLoaded.
        ChromeDriver driver = new ChromeDriver(options);  ## New Session is sent with these capabilities.
        Capabilities caps = driver.getCapabilities();  ## The capabilities the driver actually granted.
        System.out.println("browserName: " + caps.getBrowserName());
        System.out.println("browserVersion: " + caps.getBrowserVersion());  ## The exact version of the browser that started.
        System.out.println("platformName: " + caps.getPlatformName());  ## The operating system at the remote end.
        System.out.println("pageLoadStrategy: " + caps.getCapability("pageLoadStrategy"));  ## Our request was honoured.
        System.out.println("unhandledPromptBehavior: " + caps.getCapability("unhandledPromptBehavior"));  ## A default we did not set.
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver

options = webdriver.ChromeOptions()  ## An Options object describes the session you want. browserName is already chrome.
options.add_argument("--headless=new")  ## A Chrome command line switch: run without a visible window.
options.add_argument("--window-size=1280,800")  ## Another switch: the size of the browser window.
options.page_load_strategy = "eager"  ## A W3C capability: get() returns at DOMContentLoaded.
driver = webdriver.Chrome(options=options)  ## New Session is sent with these capabilities.
caps = driver.capabilities  ## A plain dict of what the driver actually granted.
for key in ("browserName", "browserVersion", "platformName", "pageLoadStrategy", "unhandledPromptBehavior"):  ## Print a few of the standard keys.
    print(key + ":", caps[key])
driver.quit()
''', js=r'''
const { Builder, Browser } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');  ## The Chrome module holds chrome.Options.

(async function sessionCaps() {
  const options = new chrome.Options();  ## An Options object describes the session you want.
  options.addArguments('--headless=new', '--window-size=1280,800');  ## Chrome command line switches: no window, and a fixed size.
  options.setPageLoadStrategy('eager');  ## A W3C capability: get() returns at DOMContentLoaded.
  const driver = await new Builder().forBrowser(Browser.CHROME).setChromeOptions(options).build();  ## New Session is sent with these capabilities.
  const caps = await driver.getCapabilities();  ## The capabilities the driver actually granted.
  for (const key of ['browserName', 'browserVersion', 'platformName', 'pageLoadStrategy', 'unhandledPromptBehavior']) {
    console.log(key + ': ' + caps.get(key));  ## caps.get reads one capability by name.
  }
  await driver.quit();
})();
''', expect='pageLoadStrategy: eager')

TIMEOUTS = tri('timeouts', 'Read the three session timeouts, then trip one on purpose', java=r'''
import java.time.Duration;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.ScriptTimeoutException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class SessionTimeouts {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        WebDriver.Timeouts t = driver.manage().timeouts();  ## The timeouts of this session.
        System.out.println("implicit: " + t.getImplicitWaitTimeout());  ## Java prints a Duration. PT0S means zero seconds.
        System.out.println("pageLoad: " + t.getPageLoadTimeout());  ## PT5M is five minutes, which is 300,000 ms.
        System.out.println("script: " + t.getScriptTimeout());  ## PT30S is thirty seconds.
        t.scriptTimeout(Duration.ofSeconds(1));  ## Allow scripts only one second from now on.
        driver.get("https://www.selenium.dev/selenium/web/blank.html");
        try {
            ((JavascriptExecutor) driver).executeAsyncScript("/* never calls its callback */");  ## An async script must call its callback. This one never does.
        } catch (ScriptTimeoutException e) {  ## After one second the driver gives up with the W3C error script timeout.
            System.out.println("Caught " + e.getClass().getSimpleName());
        } finally {
            driver.quit();
        }
    }
}
''', py=r'''
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

driver = webdriver.Chrome()
t = driver.timeouts  ## The timeouts of this session. Python reports them in seconds.
print("implicit:", t.implicit_wait)  ## 0: find_element does not wait at all unless you ask.
print("pageLoad:", t.page_load)  ## 300 seconds, which is 300,000 ms.
print("script:", t.script)  ## 30 seconds.
driver.set_script_timeout(1)  ## Allow scripts only one second from now on.
driver.get("https://www.selenium.dev/selenium/web/blank.html")
try:
    driver.execute_async_script("/* never calls its callback */")  ## An async script must call its callback. This one never does.
except TimeoutException as e:  ## Python raises TimeoutException for the W3C error script timeout.
    print("Caught", type(e).__name__)
finally:
    driver.quit()
''', js=r'''
const { Builder, Browser, error } = require('selenium-webdriver');

(async function sessionTimeouts() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  try {
    console.log(await driver.manage().getTimeouts());  ## One object with all three timeouts, in milliseconds.
    await driver.manage().setTimeouts({ script: 1000 });  ## Allow scripts only one second from now on.
    await driver.get('https://www.selenium.dev/selenium/web/blank.html');
    await driver.executeAsyncScript('/* never calls its callback */');  ## An async script must call its callback. This one never does.
  } catch (e) {
    if (!(e instanceof error.ScriptTimeoutError)) throw e;  ## The W3C error script timeout becomes ScriptTimeoutError.
    console.log('Caught ' + e.name);
  } finally {
    await driver.quit();
  }
})();
''', expect='Caught')

SERVICE = tri('service', 'Start the driver on a port you choose and ask if it is ready', java=r'''
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeDriverService;

public class DriverService {
    public static void main(String[] args) throws Exception {
        ChromeDriverService service = new ChromeDriverService.Builder().usingPort(9600).build();  ## A Service describes how to start chromedriver: here, on port 9600.
        ChromeDriver driver = new ChromeDriver(service);  ## Selenium starts chromedriver on that port, then opens a session.
        System.out.println("Driver URL: " + service.getUrl());  ## The address the binding sends its HTTP commands to.
        HttpRequest status = HttpRequest.newBuilder(URI.create("http://localhost:9600/status")).build();  ## GET /status is a W3C command that needs no session.
        String body = HttpClient.newHttpClient().send(status, HttpResponse.BodyHandlers.ofString()).body();
        System.out.println("ready: " + body.contains("\"ready\":true"));  ## The driver says whether it can start new sessions.
        driver.quit();  ## Ends the session and stops the service.
    }
}
''', py=r'''
import json
import urllib.request

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

service = Service(port=9600)  ## A Service describes how to start chromedriver: here, on port 9600.
driver = webdriver.Chrome(service=service)  ## Selenium starts chromedriver on that port, then opens a session.
print("Driver URL:", service.service_url)  ## The address the binding sends its HTTP commands to.
with urllib.request.urlopen("http://localhost:9600/status") as reply:  ## GET /status is a W3C command that needs no session.
    status = json.load(reply)["value"]
print("ready:", status["ready"])  ## The driver says whether it can start new sessions.
driver.quit()  ## Ends the session and stops the service.
''', js=r'''
const { Builder, Browser } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');

(async function driverService() {
  const service = new chrome.ServiceBuilder().setPort(9600);  ## A ServiceBuilder describes how to start chromedriver: here, on port 9600.
  const driver = await new Builder().forBrowser(Browser.CHROME).setChromeService(service).build();  ## Selenium starts chromedriver on that port, then opens a session.
  console.log('Driver URL: http://localhost:9600');
  const reply = await fetch('http://localhost:9600/status');  ## GET /status is a W3C command that needs no session. fetch is built into Node.
  const status = (await reply.json()).value;
  console.log('ready: ' + status.ready);  ## The driver says whether it can start new sessions.
  await driver.quit();  ## Ends the session and stops the service.
})();
''', expect='ready:')

K.lesson('options', 'Options and capabilities', f'''
<p>When your code creates a driver, the binding sends New Session with a set of <b>capabilities</b>: the features you want the session to have. In Selenium 3 people wrote them into a DesiredCapabilities map. Since Selenium 4 you must use the browser <b>Options</b> classes: <code>ChromeOptions</code>, <code>FirefoxOptions</code>, <code>EdgeOptions</code> and <code>SafariOptions</code>. An Options object already knows its browserName, and it gives you named methods instead of string keys you could misspell.</p>
{scene('one test suite, two needs', '<p>On a laptop, a tester wants to watch Chrome click through the checkout. On the build server there is no screen, the window should be a fixed size so screenshots line up, and slow product images should not delay the tests. The test code is the same in both places. Only the Options object changes.</p>')}
<h3>The standard W3C capabilities</h3>
{table(['Capability', 'What it controls', 'Default'], [
    ['<code>browserName</code>', 'Which browser. Set for you by each Options class.', 'set by the class'],
    ['<code>browserVersion</code>', 'Which version. Selenium Manager can download it if missing.', 'whatever is installed'],
    ['<code>platformName</code>', 'The operating system at the remote end. Matters most on Grid and in the cloud.', 'the local OS'],
    ['<code>pageLoadStrategy</code>', 'When navigation commands return: normal, eager or none.', 'normal'],
    ['<code>acceptInsecureCerts</code>', 'Trust expired or self signed TLS certificates.', 'false'],
    ['<code>timeouts</code>', 'Script, page load and implicit wait.', '30 s, 300 s, 0'],
    ['<code>unhandledPromptBehavior</code>', 'What happens to an alert your code did not handle.', 'dismiss and notify'],
    ['<code>proxy</code>', 'Send browser traffic through a proxy server.', 'none'],
    ['<code>setWindowRect</code>', 'Whether the browser supports resizing and moving windows.', 'reported by the driver'],
    ['<code>strictFileInteractability</code>', 'Strict checks for hidden file inputs.', 'off']])}
<p>Anything browser specific carries a <b>vendor prefix</b>. Chrome options travel as <code>goog:chromeOptions</code>, Firefox as <code>moz:firefoxOptions</code>. That is how command line switches such as <code>--headless=new</code> reach the browser.</p>
{CAPS}
<p>The output shows the two sides of the agreement. You asked for eager, and the driver confirmed it. You did not mention prompts, and the driver filled in the W3C default <code>dismiss and notify</code>. Reading the granted capabilities is the quickest way to learn which browser version a test really ran on.</p>
{table(['Chrome switch', 'What it does'], [
    ['<code>--headless=new</code>', 'No visible window. Common on build servers.'],
    ['<code>--start-maximized</code>', 'Open the window maximised.'],
    ['<code>--window-size=1280,800</code>', 'A fixed window size, so pages lay out the same on every machine.'],
    ['<code>--user-data-dir=...</code>', 'Use a chosen profile folder instead of a fresh temporary one.']])}
{note('Each Options class can also take the binary path of a Chromium based browser, extensions, and excludeSwitches to turn off a default switch of chromedriver. The documentation lists them on the Chrome page. Use them only when you need them, because every extra setting is one more difference from what real users run.', 'tip')}
''', kw=['options', 'capabilities', 'ChromeOptions', 'DesiredCapabilities', 'browserName', 'browserVersion', 'platformName', 'acceptInsecureCerts', 'vendor prefix', 'goog:chromeOptions', 'headless', 'arguments'])

K.lesson('loading', 'Page load strategy', f'''
<p>When you call <code>get</code>, WebDriver does not return the moment the address is sent. It waits for the page to reach a <b>document.readyState</b>. Which state it waits for is the page load strategy.</p>
{table(['Strategy', 'Waits until readyState is', 'Browser event', 'Use it when'], [
    ['<b>normal</b> (default)', 'complete', 'load: every image, font and style sheet is in', 'You want the safest behaviour'],
    ['<b>eager</b>', 'interactive', 'DOMContentLoaded: the HTML is parsed, images may still load', 'Large images or ads slow the page and the test does not need them'],
    ['<b>none</b>', 'any', 'only the first download of the page', 'You control every wait yourself']])}
{viz('se-loadstrategy')}
<p>The documentation adds two warnings. First, complete does not mean the page is finished. A single page application can keep loading content with JavaScript long after the load event. Second, the strategy applies only to navigation by address. A click that leads to a new page is not covered, so your waits must handle that. The strategy applies to the whole session, so pick it once, in the Options.</p>
{note('Switching to eager or none to make tests faster is a trade. Every element that arrives later now needs an explicit wait, or the test becomes flaky. Chapter 4.1 shows how to write those waits.', 'warn')}
''', kw=['page load strategy', 'normal', 'eager', 'none', 'document.readyState', 'complete', 'interactive', 'DOMContentLoaded', 'load event', 'single page application'])

K.lesson('timeouts', 'The three session timeouts', f'''
<p>Every session has three timeouts. They are W3C capabilities, so every browser has the same ones with the same defaults.</p>
{fxs(fx('Implicit wait', '0', 'How long Find Element keeps looking before it gives up with no such element. Zero means it checks once.'),
     fx('Page load', '300,000 ms', 'Five minutes. How long a navigation may take before a timeout error.', key=True),
     fx('Script', '30,000 ms', 'Thirty seconds. How long an injected script may run before the script timeout error.'))}
{TIMEOUTS}
<p>Look at how each language shows the same three numbers. Java prints ISO durations: PT0S, PT5M and PT30S. Python gives seconds. JavaScript gives milliseconds. The browser underneath stored exactly the same values.</p>
{table(['Language', 'Set the page load timeout to 30 s'], [
    ['Java', '<code>driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30))</code>'],
    ['Python', '<code>driver.set_page_load_timeout(30)</code>'],
    ['JavaScript', '<code>await driver.manage().setTimeouts({{ pageLoad: 30000 }})</code>']])}
{note('These timeouts belong to the browser session. Explicit waits such as WebDriverWait are different: they run in your code and poll the browser. Mixing an implicit wait with explicit waits can give surprising wait times, which chapter 4.1 explains.', 'exam')}
''', kw=['timeouts', 'implicit wait', 'page load timeout', 'script timeout', '300000', '30000', 'ScriptTimeoutException', 'TimeoutException', 'Duration'])

K.lesson('service', 'The driver service', f'''
<p>A local session has two programs: the browser and the driver. The <b>Service</b> classes manage the driver program: where its file is, which port it listens on, which arguments it gets and where its logs go. The documentation notes that a Service is only for local drivers. A remote session on a Grid has no local driver to manage.</p>
{SERVICE}
<p>The example also uses <code>GET /status</code>, a W3C command that needs no session. It tells you whether the driver can start a new session. Grid uses the same idea to check its nodes, as chapter 6.1 shows.</p>
{table(['Service setting', 'Why you would change it'], [
    ['Driver location', 'Only with Selenium older than 4.6 or a special setup. Otherwise let Selenium Manager find it.'],
    ['Port', 'A firewall allows only certain ports, or you want to talk to the driver yourself.'],
    ['Log output and level', 'Driver logs are thrown away unless you send them somewhere. Levels are ALL, DEBUG, INFO, WARNING, SEVERE and OFF.'],
    ['Arguments', 'Pass chromedriver switches, such as appending to a log file.']])}
{flow(('Options', 'What session you want: browser, version, strategy, timeouts, switches.'), ('Service', 'How to start the local driver: file, port, logs.'), ('Driver class', 'new ChromeDriver(service, options) puts both together and sends New Session.'))}
{ladder(
    '<p>Options say what kind of browser you want. Service says how to start the little driver program. The driver class uses both.</p>',
    '<p>Options become the capabilities of New Session. Service starts chromedriver on a port and the binding sends HTTP there. For a remote session you pass a URL instead of a Service.</p>',
    '<p>Capability matching happens in two passes in W3C: alwaysMatch must hold, and one of the firstMatch entries is chosen. The Python binding, for example, sends your Options as alwaysMatch next to an empty firstMatch, as the real log in chapter 1.2 shows. The granted capabilities are the truth about the session, which is why logging them helps when a test passes locally and fails in CI.</p>',
    '<p>The intermediary design means a Grid Router accepts New Session, picks a node whose stereotype matches the capabilities, and forwards the request. Chapter 6.1 follows that path, including the se: prefixed capabilities Grid adds.</p>')}
''', kw=['service', 'driver service', 'port', 'status endpoint', 'log output', 'ChromeDriverService', 'ServiceBuilder', 'local driver', 'remote driver'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Since Selenium 4, how should you describe the session you want?', ['DesiredCapabilities only', 'Browser Options classes such as ChromeOptions', 'A properties file', 'Environment variables'], 1,
       'Selenium 4 changed this.', 'As of Selenium 4 you must use the browser Options classes.')
K.quiz('e', 'What is the default page load strategy?', ['eager', 'none', 'normal', 'lazy'], 2,
       'The safest one.', 'normal is the default and waits for readyState complete.')
K.quiz('e', 'What is the default implicit wait of a new session?', ['0', '500 ms', '30 s', '5 minutes'], 0,
       'It does not wait unless asked.', 'The implicit wait timeout starts at 0.')
K.quiz('m', 'With eager, what readyState does get() wait for?', ['loading', 'interactive', 'complete', 'none'], 1,
       'DOMContentLoaded.', 'eager waits for interactive, which is when DOMContentLoaded fires.')
K.quiz('m', 'Chrome specific settings such as switches travel in which capability?', ['chrome', 'goog:chromeOptions', 'moz:chromeOptions', 'se:options'], 1,
       'A vendor prefix.', 'Browser specific options use a vendor prefix: goog for Chrome, moz for Firefox.')
K.quiz('m', 'What is the default page load timeout?', ['30 seconds', '60 seconds', '300 seconds', 'No limit'], 2,
       'Five minutes.', 'The default page load timeout is 300,000 ms.')
K.quiz('m', 'Which object is NOT used for a Remote WebDriver session?', ['Options', 'Service', 'The remote URL', 'Capabilities'], 1,
       'It starts a local program.', 'Service classes manage local drivers and cannot be used with a Remote WebDriver session.')
K.quiz('h', 'A click opens a new page. Does pageLoadStrategy normal make WebDriver wait for it to load?', ['Yes, always', 'No, the strategy applies to navigation by address, not to clicks', 'Only in Firefox', 'Only with eager'], 1,
       'Read the documentation note.', 'The documentation says the behaviour does not apply to navigation that results from clicking an element or submitting a form.')
K.quiz('h', 'You did not set unhandledPromptBehavior. What does the session report?', ['accept', 'ignore', 'dismiss and notify', 'nothing'], 2,
       'A W3C default.', 'The default user prompt handler is dismiss and notify, as the real run on this page shows.')
K.quiz('x', 'The tests pass locally and fail in CI. Which quick step tells you whether CI ran a different browser version?', ['Add sleeps', 'Print the granted capabilities, such as browserVersion', 'Switch to eager', 'Use DesiredCapabilities'], 1,
       'The session tells you the truth.', 'The capabilities returned by New Session record the browser version and platform that really ran.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'The default page load timeout is 300,000 ms. How many minutes is that?', '5', 'ms to seconds to minutes.',
       ['300,000 ms ÷ 1000 = 300 seconds.', '300 seconds ÷ 60 = 5 minutes.', eq('5 minutes')], check=5)
K.calc('e', 'Java printed the script timeout as PT30S. How many milliseconds is that?', '30000', 'PT30S means 30 seconds.',
       ['PT starts an ISO time duration, 30S is 30 seconds.', '1 second = 1000 ms.', eq('30 × 1000 = 30,000 ms')], check=30000)
K.calc('m', 'A page needs 400 ms for HTML, 300 ms to parse and 2,500 ms for images. When does get() return with eager?', '700', 'eager waits for DOMContentLoaded.',
       ['HTML arrives at 400 ms.', 'DOMContentLoaded at 400 + 300 = 700 ms.', eq('eager returns at 700 ms')], check=700, unit='ms')
K.calc('m', 'Same page. How many ms does eager save on each get() compared with normal?', '2500', 'normal also waits for the images.',
       ['normal returns at 400 + 300 + 2,500 = 3,200 ms.', 'eager returns at 700 ms.', eq('3,200 − 700 = 2,500 ms')], check=2500, unit='ms')
K.calc('h', 'A suite calls get() 600 times on that page. How many minutes does eager save in total?', '25', 'Multiply, then convert.',
       ['Each call saves 2,500 ms.', '600 × 2,500 = 1,500,000 ms = 1,500 s.', eq('1,500 ÷ 60 = 25 minutes')], check=25)
K.calc('x', 'A navigation hangs. With the default page load timeout, how long until the error, and how many hung navigations fit into a 1 hour CI limit?', '12', 'Five minutes each.',
       ['Each hung navigation waits 300 s = 5 minutes.', 'One hour is 60 minutes.', eq('60 ÷ 5 = 12 hung navigations, which is why many teams lower the page load timeout')], check=12)

# ---------------------------------------------------------------- assignments
K.assign('strategy', 'e', 'When does get() return?',
         '<p>Write <code>returns_at(strategy, html, dom, images)</code>. The page needs <code>html</code> ms to download, then <code>dom</code> ms to parse, then <code>images</code> ms for its resources. Return the time in ms when get() returns for <code>"normal"</code>, <code>"eager"</code> or <code>"none"</code>.</p>',
         '''
def returns_at(strategy, html, dom, images):
    # your code here
    pass
''', [('returns_at("normal", 400, 300, 2500)', 3200), ('returns_at("eager", 400, 300, 2500)', 700), ('returns_at("none", 400, 300, 2500)', 400)],
         '''
def returns_at(strategy, html, dom, images):
    if strategy == "none":
        return html
    if strategy == "eager":
        return html + dom
    return html + dom + images
''', 'none stops after the HTML, eager after parsing, normal after everything.', '<p>The three strategies are three points on the same timeline, which is why the stages simply add up.</p>')
K.assign('isodur', 'm', 'Read a Java duration',
         '<p>Java prints timeouts as ISO durations such as <code>PT0S</code>, <code>PT30S</code>, <code>PT5M</code> or <code>PT1M30S</code>. Write <code>to_ms(text)</code> that returns the number of milliseconds. Only minutes (M) and whole seconds (S) appear.</p>',
         '''
def to_ms(text):
    # your code here
    pass
''', [('to_ms("PT0S")', 0), ('to_ms("PT30S")', 30000), ('to_ms("PT5M")', 300000), ('to_ms("PT1M30S")', 90000)],
         '''
def to_ms(text):
    body = text[2:]
    total, number = 0, ""
    for ch in body:
        if ch.isdigit():
            number += ch
        elif ch == "M":
            total += int(number) * 60
            number = ""
        elif ch == "S":
            total += int(number)
            number = ""
    return total * 1000
''', 'Skip PT, collect digits, and add them up when you meet M or S.', '<p>Reading one character at a time and remembering the digits seen so far handles every combination of minutes and seconds.</p>')

K.must('Options', 'Since Selenium 4, describe sessions with Options classes. They become W3C capabilities, and browser specific ones carry a prefix such as goog:chromeOptions.')
K.must('Page load strategy', 'normal waits for complete (load), eager for interactive (DOMContentLoaded), none for the first download. It covers navigation by address, not clicks.')
K.must('Default timeouts', 'Implicit 0, page load 300,000 ms, script 30,000 ms. Java prints PT0S, PT5M and PT30S.')
K.must('Service', 'Starts and stops a local driver: file, port, arguments and logs. Not used for remote sessions.')
K.must('Granted capabilities', 'Read them after New Session to learn the real browser version, platform and defaults such as dismiss and notify.')

T = K.topic(
    slug='sessions-options', topic='sessions-options',
    step=(2, 'Control the browser', 'se-browser', 'Options, capabilities, page load strategy, timeouts, the driver service, navigation, windows and screenshots.', 'Beginner'),
    title='Sessions, options and timeouts', short='Sessions and options', badge='2.1', minutes=45, added='2026-10-29',
    lead='Describe the session you want with Options, see what the browser agrees to, choose when navigation returns, and know the three timeouts every session has.',
    desc='Options classes and W3C capabilities, vendor prefixes, Chrome switches, the granted capabilities, page load strategies normal, eager and none, the implicit, page load and script timeouts with their defaults, and the driver Service with port, logs and the Status endpoint, run in Java, Python and JavaScript.',
    summary='Options and capabilities, page load strategy, the three session timeouts and the driver service, shown with real runs.',
    keywords=['session', 'options', 'capabilities', 'page load strategy', 'timeouts', 'service', 'headless', 'chromeoptions'],
    recap='<p>Options describe the session and become W3C capabilities. The page load strategy decides when navigation returns. Each session has implicit, page load and script timeouts with fixed defaults. A Service starts the local driver, and the granted capabilities tell you what really ran.</p>')
