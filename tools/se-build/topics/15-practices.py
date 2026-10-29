# Chapter 5.3: good practices and things to avoid. Sources: selenium.dev documentation, Test practices: Overview,
# Testing types, Encouraged behaviours (Generating application state, Mock external services, Improved reporting,
# Avoid sharing state, Test independency, Fresh browser per test, Locators, Consider using a fluent API) and
# Discouraged behaviours (Captchas, File downloads, HTTP response codes, Gmail email and Facebook logins, Test
# dependency, Performance testing, Link spidering, Two factor authentication), with real runs of the two examples.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, src, flow

K = Kit()

FRESH = tri('fresh', 'A new driver starts with a clean profile', java=r'''
import org.openqa.selenium.Cookie;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class FreshBrowser {
    static final String PAGE = "https://www.selenium.dev/selenium/web/blank.html";

    public static void main(String[] args) {
        WebDriver first = new ChromeDriver();
        first.get(PAGE);
        first.manage().addCookie(new Cookie("cart", "3 items"));  ## State a first test leaves behind: a cookie
        ((JavascriptExecutor) first).executeScript("localStorage.setItem('theme', 'dark')");  ## and a value in local storage.
        System.out.println("first browser: " + first.manage().getCookies().size() + " cookie, storage " + ((JavascriptExecutor) first).executeScript("return localStorage.length"));
        first.quit();

        WebDriver second = new ChromeDriver();  ## A new driver gets a new, empty profile by default.
        second.get(PAGE);
        System.out.println("second browser: " + second.manage().getCookies().size() + " cookies, storage " + ((JavascriptExecutor) second).executeScript("return localStorage.length"));
        second.quit();
    }
}
''', py=r'''
from selenium import webdriver

PAGE = "https://www.selenium.dev/selenium/web/blank.html"

first = webdriver.Chrome()
first.get(PAGE)
first.add_cookie({"name": "cart", "value": "3 items"})  ## State a first test leaves behind: a cookie
first.execute_script("localStorage.setItem('theme', 'dark')")  ## and a value in local storage.
print("first browser:", len(first.get_cookies()), "cookie, storage", first.execute_script("return localStorage.length"))
first.quit()

second = webdriver.Chrome()  ## A new driver gets a new, empty profile by default.
second.get(PAGE)
print("second browser:", len(second.get_cookies()), "cookies, storage", second.execute_script("return localStorage.length"))
second.quit()
''', js=r'''
const { Builder, Browser } = require('selenium-webdriver');

const PAGE = 'https://www.selenium.dev/selenium/web/blank.html';
(async function freshBrowser() {
  const first = await new Builder().forBrowser(Browser.CHROME).build();
  await first.get(PAGE);
  await first.manage().addCookie({ name: 'cart', value: '3 items' });  ## State a first test leaves behind: a cookie
  await first.executeScript("localStorage.setItem('theme', 'dark')");  ## and a value in local storage.
  console.log('first browser: ' + (await first.manage().getCookies()).length + ' cookie, storage ' + await first.executeScript('return localStorage.length'));
  await first.quit();

  const second = await new Builder().forBrowser(Browser.CHROME).build();  ## A new driver gets a new, empty profile by default.
  await second.get(PAGE);
  console.log('second browser: ' + (await second.manage().getCookies()).length + ' cookies, storage ' + await second.executeScript('return localStorage.length'));
  await second.quit();
})();
''', expect='second browser: 0 cookies, storage 0')

STATE = tri('appstate', 'Prepare the state without clicking through the user interface', java=r'''
import org.openqa.selenium.By;
import org.openqa.selenium.Cookie;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class AppState {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        String session = "abc123";  ## In a real suite this value comes from a login API call, not from the login form.
        driver.get("https://www.selenium.dev/selenium/web/blank.html");  ## A small page on the domain, only to be allowed to set the cookie.
        driver.manage().addCookie(new Cookie("session", session));
        driver.get("https://www.selenium.dev/selenium/web/cookies.html");  ## Now open the page under test. It reads its cookies on load.
        System.out.println("page shows: " + driver.findElement(By.id("result")).getText());
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
session = "abc123"  ## In a real suite this value comes from a login API call, not from the login form.
driver.get("https://www.selenium.dev/selenium/web/blank.html")  ## A small page on the domain, only to be allowed to set the cookie.
driver.add_cookie({"name": "session", "value": session})
driver.get("https://www.selenium.dev/selenium/web/cookies.html")  ## Now open the page under test. It reads its cookies on load.
print("page shows:", driver.find_element(By.ID, "result").text)
driver.quit()
''', js=r'''
const { Builder, Browser, By } = require('selenium-webdriver');

(async function appState() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  const session = 'abc123';  ## In a real suite this value comes from a login API call, not from the login form.
  await driver.get('https://www.selenium.dev/selenium/web/blank.html');  ## A small page on the domain, only to be allowed to set the cookie.
  await driver.manage().addCookie({ name: 'session', value: session });
  await driver.get('https://www.selenium.dev/selenium/web/cookies.html');  ## Now open the page under test. It reads its cookies on load.
  console.log('page shows: ' + await driver.findElement(By.id('result')).getText());
  await driver.quit();
})();
''', expect='page shows: session=abc123')

K.lesson('shape', 'The shape of a good browser test', f'''
<p>The documentation starts its advice with a question: do you really need a browser for this? Browser tests are the most expensive tests you have. They need browsers, drivers and often a Grid, and they take seconds where a unit test takes milliseconds. Their strength is that they test the whole application, from the database to the screen, as a user sees it.</p>
<p>When a browser test is the right tool, the documentation says it should do three things, and keep each short: <b>set up the data</b>, <b>perform a discrete set of actions</b>, and <b>evaluate the results</b>. One or two operations are enough most of the time.</p>
{viz('se-split')}
<p>The documentation tells the story of Larry's unicorn shop: create an account, configure a unicorn, add it to the cart, check out and pay, give feedback. The temptation is one grand script for the whole journey. The documentation says to resist it, because such a test is slow, more exposed to timing problems, and when it fails it does not tell you at a glance what broke. Break it into small independent tests, each with one reason to exist.</p>
{table(['Testing type', 'Question it answers', 'Selenium fits?'], [
    ['Acceptance', 'Are we building the right product?', 'Yes, by simulating what the user expects'],
    ['Functional', 'Are we building the product right?', 'Yes'],
    ['Integration', 'Do the modules work together, for example order plus payment?', 'Yes, for flows through the UI'],
    ['System', 'Does the whole product work end to end, in an environment like production?', 'Yes, a few journeys'],
    ['Performance (load and stress)', 'How fast is it, and does it survive a peak?', 'Not as the measuring tool. The documentation points to tools such as JMeter'],
    ['Regression', 'Did a change break what worked?', 'Yes, by running the existing tests again']])}
''', kw=['test design', 'set up act evaluate', 'small tests', 'happy path', 'testing types', 'acceptance', 'functional', 'regression', 'unicorn'])

K.lesson('encouraged', 'Encouraged practices', f'''
<p>These practices come from the encouraged behaviours section of the documentation. The first two are shown with real runs.</p>
<p><b>Fresh browser per test.</b> Start each test from a clean, known state. The documentation notes that drivers such as ChromeDriver and GeckoDriver start with a new user profile by default. The run below proves it: the second browser sees none of the cookie or storage the first one left.</p>
{FRESH}
<p><b>Generate application state.</b> Selenium should not be used to prepare a test case. Logging in through the form before every test is slow and adds a place to fail. The documentation suggests creating a method that logs in through an API and sets a cookie. Here the session cookie is set directly and the page under test reads it on load.</p>
{STATE}
{table(['Practice', 'What the documentation says'], [
    ['Avoid sharing state', 'Do not share test data, clean up stale data, and create a new WebDriver per test'],
    ['Test independency', 'Write each test as its own unit, not relying on another test to complete'],
    ['Mock external services', 'Removing dependencies on external services improves speed and stability'],
    ['Improved reporting', 'Selenium does not report. Use the reports of your test framework, such as xUnit XML or HTML'],
    ['Locators', 'Unique ids first, then a well written CSS selector. XPath is flexible but harder to debug and often slower'],
    ['Page objects and a fluent API', 'Chapter 5.2. Methods can return the page for chained calls'],
    ['Domain specific language', 'Business level methods on top of page objects']])}
{scene('one order, two tests', '<p>Two tests each query the database for a valid order and act on the first one they find. On a busy night both pick order 1042, one cancels it, and the other fails because the order is gone. The fix from the documentation: each test creates its own order through the API and cleans it up afterwards.</p>')}
''', kw=['fresh browser', 'clean state', 'application state', 'api login', 'cookie', 'independent tests', 'shared state', 'mock services', 'reporting'])

K.lesson('discouraged', 'Things to avoid', f'''
<p>The documentation also lists jobs that Selenium can technically do but should not, with what to do instead.</p>
{table(['Avoid', 'Why', 'Do instead'], [
    ['CAPTCHAs', 'They are built to stop automation', 'Disable them in the test environment, or add a hook that lets tests bypass them'],
    ['File downloads', 'The API does not expose download progress', 'Find the link with Selenium and fetch it with an HTTP library such as curl, using any cookies it needs'],
    ['HTTP status codes', 'WebDriver acts like a user, and a status code is rarely the useful detail of a failure', 'Check what the user sees, such as an error page. Chapter 6.2 shows BiDi network events if you really need codes'],
    ['Logging in to Gmail or Facebook', 'Against their terms, slow and unreliable', 'Use the APIs or test account tools they provide'],
    ['Test dependency', 'Tests must run in any order', 'Make each test set up its own state'],
    ['Performance testing', 'Browser start, servers and third parties add noise to every number', 'Use performance tools, and keep Selenium for function'],
    ['Link spidering', 'A browser takes seconds per page', 'Use curl or a library such as BeautifulSoup'],
    ['Two factor authentication', 'Automating it is hard and less secure', 'A test only token, or 2FA turned off for test users, test IPs or the test environment']])}
{note('Every row has the same shape: Selenium is a tool for what a user does in a browser. When the job is not that, a lighter tool is faster and more reliable.', 'tip')}
{ladder(
    '<p>Use a browser test only when you need one, keep it short, start it clean, and do not make Selenium do jobs other tools do better.</p>',
    '<p>Each test sets up its data, performs a few actions and checks the result. Fresh browser per test, no shared data, state prepared through APIs and cookies, reports from the framework.</p>',
    '<p>The encouraged and discouraged lists in the documentation all serve two goals: tests that are independent, so they can run in any order and in parallel, and tests that fail for one clear reason.</p>',
    '<p>Large suites add test data factories, service mocks at the network edge, contract tests for APIs and a small set of end to end browser journeys on top of many fast lower level tests.</p>')}
''', kw=['captcha', 'file download', 'status code', 'gmail', 'facebook login', 'test dependency', 'performance testing', 'link spidering', 'two factor authentication', '2fa'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What does the documentation ask first, before writing a Selenium test?', ['Which browser to use', 'Whether you really need a browser for it', 'How many locators you need', 'Which Grid to use'], 1,
       'Browser tests are expensive.', 'Always ask whether a lighter test, such as a unit test, can do the job.')
K.quiz('e', 'What are the three steps of a browser test?', ['Open, wait, close', 'Set up the data, perform the actions, evaluate the results', 'Find, click, type', 'Build, run, report'], 1,
       'Arrange, act, assert.', 'The documentation names set up, perform and evaluate, each kept short.')
K.quiz('e', 'How should a test deal with a CAPTCHA?', ['Solve it with OCR', 'Disable it in the test environment or add a bypass hook', 'Click it many times', 'Wait for it to disappear'], 1,
       'It is built to stop automation.', 'The documentation says do not try. Disable it or bypass it in test.')
K.quiz('m', 'Why prefer several small tests over one grand journey?', ['Fewer files', 'They are faster, less exposed to timing issues, and a failure points to one cause', 'Grid requires it', 'Reports are shorter'], 1,
       'Larry and the unicorns.', 'Small independent tests fail for one clear reason.')
K.quiz('m', 'A new ChromeDriver session starts. What does it know about cookies from an earlier session?', ['Everything', 'Nothing, it starts with a new profile', 'Only secure cookies', 'Only localStorage'], 1,
       'Look at the second browser line.', 'A new driver gets a new, empty user profile by default.')
K.quiz('m', 'How does the documentation suggest preparing a logged in state?', ['Click through the login form each time', 'Log in through an API and set a cookie', 'Share one browser', 'Use the Remember me box'], 1,
       'Generating application state.', 'Selenium should not prepare a test. Use an API and a cookie.')
K.quiz('m', 'How should a test check a file download?', ['Watch the progress bar', 'Read the link with Selenium and fetch it with an HTTP library', 'Take a screenshot', 'It cannot be tested'], 1,
       'The API has no progress.', 'Get the URL and cookies, then download outside the browser.')
K.quiz('h', 'Why is Selenium a poor tool for performance numbers?', ['It cannot measure time', 'Browser start, servers, third party files and the driver itself add variation', 'It is too fast', 'It blocks images'], 1,
       'Noise.', 'Many points of fragility outside your control change the results.')
K.quiz('h', 'Two tests pick the same order from the database. What does the documentation advise?', ['Run them one after the other', 'Do not share test data, each test creates its own', 'Retry on failure', 'Use a longer wait'], 1,
       'Avoid sharing state.', 'Shared data makes tests interfere, so each creates its own.')
K.quiz('x', 'Each of 5 steps in a journey fails randomly 2 % of the time. Roughly how often does the whole journey pass?', ['98 %', 'About 90 %', '50 %', '10 %'], 1,
       'Multiply the pass chances.', '0.98 to the power 5 is about 0.904, so about 90 %.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A unit test takes 5 ms and a browser test 4 s. How many unit tests run in the time of one browser test?', '800', 'Same units first.',
       ['4 s is 4,000 ms.', 'Divide by 5 ms.', eq('4,000 ÷ 5 = 800 unit tests')], check=800)
K.calc('e', 'A login through the form takes 3 s and through an API 0.3 s. How many seconds does a test save?', '2.7', 'Subtract.',
       ['Form: 3 s.', 'API: 0.3 s.', eq('3 − 0.3 = 2.7 s')], check=2.7, unit='s')
K.calc('m', 'A journey has 5 steps and each passes 98 % of the time. What is the chance, in percent to one decimal, that the whole journey passes?', '90.4', 'Multiply.',
       ['Pass chance per step: 0.98.', '0.98<sup>5</sup> ≈ 0.904.', eq('About 90.4 %')], check=90.4, unit='%')
K.calc('m', 'With the same steps as 5 separate tests, how many tests fail on average per 100 runs of the set?', '10', 'Each test fails 2 %.',
       ['Each test fails 2 times per 100 runs.', 'There are 5 tests.', eq('5 × 2 = 10 failures per 100 runs of the set, each naming its step')], check=10)
K.calc('h', 'A suite of 400 tests logs in through the form at 3 s each. Switching to API login at 0.3 s, how many minutes does a run save?', '18', 'Saving per test times tests.',
       ['Saving per test: 2.7 s.', '400 × 2.7 = 1,080 s.', eq('1,080 ÷ 60 = 18 minutes')], check=18, unit='min')
K.calc('x', 'A spider must visit 600 pages. A browser needs 2.5 s per page, curl needs 0.1 s. How many minutes does curl save?', '24', 'Time each, then subtract.',
       ['Browser: 600 × 2.5 = 1,500 s.', 'curl: 600 × 0.1 = 60 s.', eq('1,440 s saved, which is 24 minutes')], check=24, unit='min')

# ---------------------------------------------------------------- assignments
K.assign('journey', 'e', 'Chance that a journey passes',
         '<p>Write <code>pass_chance(steps, flake)</code>. Each of <code>steps</code> steps fails at random with probability <code>flake</code> (for example 0.02). Return the chance that all steps pass, rounded to 3 decimals.</p>',
         '''
def pass_chance(steps, flake):
    # your code here
    pass
''', [('pass_chance(5, 0.02)', 0.904), ('pass_chance(1, 0.1)', 0.9), ('pass_chance(10, 0.0)', 1.0)],
         '''
def pass_chance(steps, flake):
    return round((1 - flake) ** steps, 3)
''', 'Multiply the pass chance of each step.', '<p>This is why the documentation warns about one grand test: the chances multiply, so a long journey fails more often than any of its steps.</p>')
K.assign('ordercheck', 'm', 'Do the tests depend on their order?',
         '<p>Write <code>order_independent(results_a, results_b)</code>. Each argument maps test names to "pass" or "fail" from one run, the two runs used different orders. Return True if every test has the same result in both runs.</p>',
         '''
def order_independent(results_a, results_b):
    # your code here
    pass
''', [('order_independent({"a": "pass", "b": "pass"}, {"b": "pass", "a": "pass"})', True), ('order_independent({"a": "pass", "b": "pass"}, {"b": "fail", "a": "pass"})', False), ('order_independent({}, {})', True)],
         '''
def order_independent(results_a, results_b):
    if results_a.keys() != results_b.keys():
        return False
    for name in results_a:
        if results_a[name] != results_b[name]:
            return False
    return True
''', 'Compare result by result.', '<p>Plugins such as pytest-randomly run tests in a random order on purpose, to find this kind of hidden dependency early.</p>')

K.must('Need a browser?', 'Ask first whether a lighter test can do the job. Browser tests are the most expensive kind.')
K.must('Short and focused', 'Set up the data, perform a few actions, evaluate the result. Many small independent tests beat one grand journey.')
K.must('Clean start', 'A new driver starts with a new profile. Use a fresh browser per test and never share test data.')
K.must('Prepare state outside the UI', 'Log in and create data through APIs, then set cookies, instead of clicking through forms.')
K.must('Avoid', 'CAPTCHAs, download progress, status codes, third party logins, test order, performance numbers, spidering and 2FA are jobs for other tools or test hooks.')

T = K.topic(
    slug='practices', topic='practices',
    step=(5, 'Build a test suite', 'se-suite', 'Test frameworks, page objects, good practices and the errors you will meet.', 'Intermediate'),
    title='Good practices and things to avoid', short='Good practices', badge='5.3', minutes=40, added='2026-10-29',
    lead='Design browser tests the way the Selenium documentation recommends: short, independent and starting clean, with state prepared through APIs, and without the jobs Selenium is not made for.',
    desc='When to use a browser test, set up, perform and evaluate, an animation of one grand test against small tests, testing types, a real run proving a new driver starts clean, application state through cookies, and the encouraged and discouraged practices from the documentation.',
    summary='Test design, encouraged practices and the things the documentation says to avoid.',
    keywords=['best practices', 'test design', 'fresh browser', 'application state', 'shared state', 'test independence', 'captcha', 'file download', 'performance testing', '2fa'],
    recap='<p>Use a browser only when you need one. Keep each test to set up, a few actions and a check. Start every test with a fresh browser, never share data, prepare state through APIs and cookies, and leave CAPTCHAs, downloads, status codes, performance numbers and 2FA to other tools or test hooks.</p>')
