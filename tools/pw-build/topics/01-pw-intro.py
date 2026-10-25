from pkit import part, say, quiz, calc, panel, four, one, js, ts, py, jv, shown, walk, step, table, tip, by, viz

MODULE = ('🚀', 'Getting started', 'pw-start', 'What Playwright is, how one line of a test travels to the browser, and the tools you get in Java, Python, JavaScript and TypeScript.')

# ---------- code that runs for real when the page is built ----------
FIRST_JS = '''import { chromium } from 'playwright';

const browser = await chromium.launch();          // start a real Chromium, with no window
const page = await browser.newPage();             // open a new tab
await page.goto('http://localhost:4173/products');
console.log('Title:', await page.title());
await page.screenshot({ path: 'products.png' });  // save a picture of the page
await browser.close();'''

FIRST_TS = '''import { chromium, type Browser, type Page } from 'playwright';

const browser: Browser = await chromium.launch();
const page: Page = await browser.newPage();
await page.goto('http://localhost:4173/products');
const title: string = await page.title();
console.log('Title:', title);
await page.screenshot({ path: 'products.png' });
await browser.close();'''

FIRST_PY = '''from playwright.sync_api import sync_playwright

with sync_playwright() as p:                      # start the Playwright driver
    browser = p.chromium.launch()                 # start a real Chromium, with no window
    page = browser.new_page()                     # open a new tab
    page.goto("http://localhost:4173/products")
    print("Title:", page.title())
    page.screenshot(path="products.png")          # save a picture of the page
    browser.close()'''

FIRST_JAVA = '''package com.brainy;

import com.microsoft.playwright.*;

public class FirstScript {
  public static void main(String[] args) {
    try (Playwright playwright = Playwright.create()) {        // start the Playwright driver
      Browser browser = playwright.chromium().launch();         // start a real Chromium, with no window
      Page page = browser.newPage();                             // open a new tab
      page.navigate("http://localhost:4173/products");
      System.out.println("Title: " + page.title());
      page.screenshot(new Page.ScreenshotOptions()
          .setPath(java.nio.file.Paths.get("products.png")));  // save a picture of the page
    }                                                            // closing Playwright closes the browser too
  }
}'''

EXEC_POM = '''<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.brainy</groupId>
  <artifactId>first-script</artifactId>
  <version>1.0.0</version>
  <properties>
    <maven.compiler.release>21</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>
  <dependencies>
    <dependency>
      <groupId>com.microsoft.playwright</groupId>
      <artifactId>playwright</artifactId>
      <version>1.63.0</version>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.codehaus.mojo</groupId>
        <artifactId>exec-maven-plugin</artifactId>
        <version>3.5.1</version>
        <configuration><mainClass>com.brainy.FirstScript</mainClass></configuration>
      </plugin>
    </plugins>
  </build>
</project>'''

# The same sign in, with the debug log on. DEBUG=pw:api prints what Playwright does inside every call.
DBG_JS = '''import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('http://localhost:4173/login');
await page.getByLabel('Email').fill('asha@shop.example');
await page.getByRole('button', { name: 'Sign in' }).click();
await browser.close();'''

DBG_TS = '''import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('http://localhost:4173/login');
await page.getByLabel('Email').fill('asha@shop.example');
await page.getByRole('button', { name: 'Sign in' }).click();
await browser.close();'''

DBG_PY = '''from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:4173/login")
    page.get_by_label("Email").fill("asha@shop.example")
    page.get_by_role("button", name="Sign in").click()
    browser.close()'''

DBG_JAVA = '''package com.brainy;

import com.microsoft.playwright.*;
import com.microsoft.playwright.options.AriaRole;

public class FirstScript {
  public static void main(String[] args) {
    try (Playwright playwright = Playwright.create()) {
      Browser browser = playwright.chromium().launch();
      Page page = browser.newPage();
      page.navigate("http://localhost:4173/login");
      page.getByLabel("Email").fill("asha@shop.example");
      page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in")).click();
    }
  }
}'''

# Strip the timestamps of the debug log so the page shows what matters.
NO_TIME = [(r'(?m)^\S+Z pw:api ', ''), (r'(?m)^\s*$\n', '')]

CHANNEL_JS = DBG_JS

PROTO_JS = DBG_JS

FIRST_TEST_TS = '''import { test, expect } from '@playwright/test';

test('a customer can sign in', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('s3cret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByText('Hello, Asha')).toBeVisible();
});'''

FIRST_TEST_JS = FIRST_TEST_TS

FIRST_TEST_PY = '''from playwright.sync_api import Page, expect


def test_a_customer_can_sign_in(page: Page):
    page.goto("/login")
    page.get_by_label("Email").fill("asha@shop.example")
    page.get_by_label("Password").fill("s3cret")
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_text("Hello, Asha")).to_be_visible()'''

FIRST_TEST_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class SignInTest {
  @Test
  void aCustomerCanSignIn(Page page) {
    page.navigate("/login");
    page.getByLabel("Email").fill("asha@shop.example");
    page.getByLabel("Password").fill("s3cret");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in")).click();
    assertThat(page.getByText("Hello, Asha")).isVisible();
  }
}'''

CODES = {
    'first': four('Your first Playwright script',
                  java=jv({'src/main/java/com/brainy/FirstScript.java': FIRST_JAVA}, cmd='mvn -q compile exec:java', pom_xml=EXEC_POM, options=False,
                          replace=[(r'(?m)^\[INFO\].*\n', '')]),
                  py=py({'first.py': FIRST_PY}, ini=None, cmd='python first.py && ls *.png'),
                  js=js({'first.mjs': FIRST_JS}, config=None, cmd='node first.mjs && ls *.png'),
                  ts=ts({'first.ts': FIRST_TS}, cmd='node first.ts && ls *.png', shown_cmd='npx tsc -p . && node first.ts && ls *.png'),
                  result='Each version starts a real Chromium without a window, opens the products page, prints its title and saves <code>products.png</code>. Node.js 22.18 and later can run a <code>.ts</code> file directly, and the build checks the types with <code>tsc</code> first.'),
    'debug': four('Watch what Playwright does inside each call',
                  java=jv({'src/main/java/com/brainy/FirstScript.java': DBG_JAVA}, cmd='DEBUG=pw:api mvn -q compile exec:java 2>&1', pom_xml=EXEC_POM, options=False,
                          shown_cmd='DEBUG=pw:api mvn -q compile exec:java', replace=NO_TIME + [(r'(?m)^\[INFO\].*\n', '')]),
                  py=py({'first.py': DBG_PY}, ini=None, cmd='DEBUG=pw:api python first.py 2>&1', shown_cmd='DEBUG=pw:api python first.py', replace=NO_TIME),
                  js=js({'first.mjs': DBG_JS}, config=None, cmd='DEBUG=pw:api node first.mjs 2>&1', shown_cmd='DEBUG=pw:api node first.mjs', replace=NO_TIME),
                  ts=ts({'first.ts': DBG_TS}, cmd='DEBUG=pw:api node first.ts 2>&1', shown_cmd='DEBUG=pw:api node first.ts', replace=NO_TIME),
                  result='The log is written by the driver, which is the same program in every language. Look at how it names the locator in your own language, for example <code>get_by_label("Email")</code> in Python and <code>getByLabel(\'Email\')</code> in JavaScript. Before the click it waits until the button is visible, enabled and stable. You will meet these checks again in the chapter on auto waiting.'),
    'channel': one('The messages your code sends to the driver',
                   js({'first.mjs': CHANNEL_JS}, config=None, cmd='DEBUG=pw:channel node first.mjs 2>&1 | grep "SEND>"', shown_cmd='DEBUG=pw:channel node first.mjs',
                      replace=[(r'(?m)^\S+Z pw:channel ', ''), (r'@[0-9a-f]{32}', '@…')]),
                   result='Every line is one JSON message. <code>guid</code> names the object the call is for, such as one browser or one frame, and <code>method</code> is what to do. The locator <code>getByRole(\'button\', { name: \'Sign in\' })</code> has become the selector <code>internal:role=button[name="Sign in"i]</code>, and <code>strict: true</code> means the call fails if more than one element matches.'),
    'proto': one('The messages the driver sends to Chromium',
                 js({'first.mjs': PROTO_JS}, config=None, cmd='DEBUG=pw:protocol node first.mjs 2>&1 | grep "SEND ►" | grep -E "createBrowserContext|createTarget|Page.navigate|Input\\.(insertText|dispatchMouseEvent)"',
                    shown_cmd='DEBUG=pw:protocol node first.mjs',
                    replace=[(r'(?m)^\S+Z pw:protocol ', ''), (r'"(sessionId|frameId|browserContextId)":"[0-9A-F]+"', r'"\1":"…"')]),
                 result='These are Chrome DevTools Protocol messages. <code>Target.createBrowserContext</code> is the fresh context, <code>Page.navigate</code> is the <code>goto</code>, <code>Input.insertText</code> types the email in one go, and three <code>Input.dispatchMouseEvent</code> messages move the mouse to the middle of the button, press it and release it. The browser cannot tell these from a real person.'),
    'firsttest': four('Your first test, in four languages',
                      java=jv({'SignInTest.java': FIRST_TEST_JAVA}),
                      py=py({'test_sign_in.py': FIRST_TEST_PY}),
                      js=js({'sign-in.spec.js': FIRST_TEST_JS}),
                      ts=ts({'sign-in.spec.ts': FIRST_TEST_TS}),
                      result='All four are the same test. Each test runner gives the test a fresh page, opens the shop, signs in and checks the greeting. Java uses JUnit 5 with the <code>@UsePlaywright</code> annotation, Python uses pytest with the pytest-playwright plugin, and JavaScript and TypeScript use Playwright Test, the runner made by the Playwright team.'),
    'walk1': walk('A customer signs in', [
        step('Open the sign in page.', "await page.goto('http://localhost:4173/login');", 'page.goto("http://localhost:4173/login")', 'page.navigate("http://localhost:4173/login");'),
        step('Type the email into the box labelled Email.', "await page.getByLabel('Email').fill('asha@shop.example');", 'page.get_by_label("Email").fill("asha@shop.example")', 'page.getByLabel("Email").fill("asha@shop.example");'),
        step('Type the password.', "await page.getByLabel('Password').fill('s3cret');", 'page.get_by_label("Password").fill("s3cret")', 'page.getByLabel("Password").fill("s3cret");'),
        step('Click the button called Sign in. The shop signs Asha in and opens the products page.', "await page.getByRole('button', { name: 'Sign in' }).click();",
             'page.get_by_role("button", name="Sign in").click()', 'page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in")).click();'),
        step('Check that the greeting says Hello, Asha. The check waits until it appears.', "await expect(page.getByText('Hello, Asha')).toBeVisible();",
             'expect(page.get_by_text("Hello, Asha")).to_be_visible()', 'assertThat(page.getByText("Hello, Asha")).isVisible();'),
    ]),
}

DG = {
    'arch': {'t': 'The pieces of Playwright', 'w': 900, 'h': 330,
             'n': [['java', 20, 20, 170, 54, 'Java test', {'c': 1, 'sh': 'doc'}], ['py', 20, 95, 170, 54, 'Python test', {'c': 0, 'sh': 'doc'}],
                   ['js', 20, 170, 170, 54, 'JavaScript test', {'c': 5, 'sh': 'doc'}], ['ts', 20, 245, 170, 54, 'TypeScript test', {'c': 2, 'sh': 'doc'}],
                   ['cl', 250, 95, 170, 130, 'client library', {'c': 3, 'sub': 'jar, pip package or npm package', 'i': 'Turns each call such as click() into a JSON message.'}],
                   ['dr', 480, 95, 170, 130, 'Playwright driver', {'c': 4, 'sub': 'a Node.js program', 'i': 'Finds elements, waits for them and talks to the browser. It is the same program for every language.'}],
                   ['cr', 720, 20, 160, 70, 'Chromium', {'c': 2, 'sub': 'Chrome, Edge', 'i': 'Spoken to with the Chrome DevTools Protocol.'}],
                   ['ff', 720, 125, 160, 70, 'Firefox', {'c': 1, 'sub': 'patched build', 'i': 'Spoken to with Juggler, a protocol the Playwright team added to Firefox.'}],
                   ['wk', 720, 230, 160, 70, 'WebKit', {'c': 0, 'sub': 'engine of Safari', 'i': 'Spoken to with the WebKit inspector protocol, extended by Playwright.'}]],
             'e': [['java', 'cl'], ['py', 'cl'], ['js', 'cl'], ['ts', 'cl'], ['cl', 'dr', {'t': 'JSON messages'}], ['dr', 'cr', {'t': 'CDP'}], ['dr', 'ff'], ['dr', 'wk']],
             'st': [[['java', 'py', 'js', 'ts'], 'You write the test in the language your team already uses.'],
                    [['cl', 'java>cl', 'py>cl', 'js>cl', 'ts>cl'], 'The client library of that language turns every call into a small message.'],
                    [['dr', 'cl>dr'], 'The driver receives the message. In Java and Python it is a separate Node.js process. In JavaScript and TypeScript it runs inside the same process.'],
                    [['cr', 'ff', 'wk', 'dr>cr', 'dr>ff', 'dr>wk'], 'The driver speaks each browser\'s own debugging protocol. No browser plug in and no separate WebDriver server is needed.']]},
    'run': {'t': 'What happens when you run a test', 'w': 900, 'h': 250,
            'n': [['cmd', 20, 90, 130, 60, 'you run the tests', {'c': 5, 'sh': 'pill'}], ['cfg', 180, 90, 120, 60, 'read the config', {'c': 3, 'i': 'playwright.config.ts, pytest.ini or the options class in Java.'}],
                  ['br', 330, 20, 140, 60, 'launch browser', {'c': 2, 'sub': 'once per worker', 'i': 'Starting a browser takes about half a second, so it is shared by many tests.'}],
                  ['ctx', 330, 160, 140, 60, 'new context', {'c': 1, 'sub': 'for every test', 'i': 'A context is like a fresh incognito window. It takes a few milliseconds.'}],
                  ['body', 500, 90, 130, 60, 'run the test body', {'c': 4}], ['close', 660, 90, 110, 60, 'close context', {'c': 0}],
                  ['rep', 790, 90, 100, 60, 'report', {'c': 3, 'sh': 'doc'}]],
            'e': [['cmd', 'cfg'], ['cfg', 'br'], ['br', 'ctx'], ['ctx', 'body'], ['body', 'close'], ['close', 'rep'], ['close', 'ctx', {'t': 'next test', 'd': 1, 'cv': 40}]],
            'st': [[['cmd', 'cfg', 'cmd>cfg'], 'The runner reads the settings first: base address, browser, timeouts and reporters.'],
                   [['br', 'cfg>br'], 'It starts the browser once for each worker process.'],
                   [['ctx', 'br>ctx'], 'Every test gets a brand new browser context and page, so no cookie or login leaks from one test to the next.'],
                   [['body', 'ctx>body'], 'Your test body runs line by line.'],
                   [['close', 'body>close', 'close>ctx'], 'The context is thrown away and the next test gets a fresh one, while the browser keeps running.'],
                   [['rep', 'close>rep'], 'When all tests are done, the reporters write the results.']]},
}

PARTS = [
    part('what', '🎭', 'What Playwright is', f'''
<p>Playwright is a free tool, made by Microsoft, that controls a real web browser from code. Your code can open a page, click buttons, type into boxes, wait for things to appear and check that the page shows the right result. It does this in Chromium (the engine of Google Chrome and Microsoft Edge), Firefox and WebKit (the engine of Apple Safari).</p>
{tip('Think of a shop that hires a careful helper. Every morning the helper opens the shop website, signs in, adds a pen to the cart and checks that the total is right. Playwright is that helper, written in code. It never gets bored, it checks the same steps in three browsers, and it finishes in seconds.', 'kid')}
<p>Teams use Playwright for three jobs:</p>
<ul>
<li><b>End to end tests.</b> A test acts like a user, from opening the site to placing an order, and checks every important step.</li>
<li><b>API tests.</b> Playwright can also send HTTP requests without a browser, so the same project can test the server directly.</li>
<li><b>Automation.</b> Filling forms, taking screenshots, making PDFs and collecting data from pages.</li>
</ul>
<p>Playwright has official versions for four language families, all made and released together by the Playwright team:</p>
{table(['Language', 'Package', 'Usual test runner', 'Version used on this page'], [
    ['☕ Java', '<code>com.microsoft.playwright:playwright</code> on Maven Central', 'JUnit 5 or TestNG', '1.63.0'],
    ['🐍 Python', '<code>playwright</code> and <code>pytest-playwright</code> on PyPI', 'pytest', '1.63.0'],
    ['🟨 JavaScript and 🔷 TypeScript', '<code>@playwright/test</code> on npm', 'Playwright Test (built in)', '1.63.0'],
    ['🟪 C# and .NET', '<code>Microsoft.Playwright</code> on NuGet', 'NUnit, MSTest or xUnit', 'shown in the playground only'],
])}
<p>Pick your language at the top of the page. Every example and every explanation then shows that language first, and you can switch tabs at any time to compare.</p>
{tip('People often ask for Playwright in C, C++ or Go. There is no official Playwright for C or C++. For Go there is a community project, playwright-go, which is not made by the Playwright team. This subject sticks to the official languages so that every example is supported and up to date.', 'warn')}
''', easy=True, kw=['playwright', 'what is playwright', 'browser automation', 'end to end testing']),

    part('why', '⚖️', 'Why teams pick Playwright', f'''
<p>Before Playwright, most teams used Selenium, and many front end teams used Cypress. All three are good tools. This table shows the facts that differ, so you can explain the choice in an interview or a team meeting.</p>
{table(['', 'Playwright', 'Selenium WebDriver', 'Cypress'], [
    ['Languages', 'Java, Python, JavaScript, TypeScript, C#', 'Java, Python, JavaScript, C#, Ruby', 'JavaScript and TypeScript'],
    ['Browsers', 'Chromium, Firefox, WebKit', 'Chrome, Firefox, Edge, Safari through their drivers', 'Chromium family, Firefox, WebKit (experimental)'],
    ['How it talks to the browser', 'Browser debugging protocols, through one driver process', 'The W3C WebDriver protocol, through a driver per browser', 'Runs inside the browser next to your app'],
    ['Waiting', 'Automatic before every action and in every check', 'You add waits yourself', 'Automatic retries for commands and checks'],
    ['Several tabs, windows and domains in one test', 'Yes', 'Yes', 'Limited'],
    ['Parallel runs', 'Built in, free', 'With Selenium Grid or a test runner', 'Paid cloud service, or plugins'],
    ['Debugging', 'Trace viewer, UI mode, inspector, codegen', 'Logs and screenshots you add', 'Time travel in the runner'],
])}
<p>The biggest daily difference is waiting. In Selenium, a click on a button that is still loading fails, so people add waits. Playwright checks that the element is visible, stable and enabled before it acts, and every <code>expect</code> check keeps trying until it passes or times out. This removes most flaky tests, the ones that pass and fail at random.</p>
{tip('In many companies you will join a project that already uses Selenium. Knowing both is useful. Many teams move to Playwright one test suite at a time, because the ideas are close: find an element, act on it, check the result.', 'pro')}
''', easy=True, kw=['selenium', 'cypress', 'comparison', 'webdriver']),

    part('first-look', '👀', 'Your first script', f'''
<p>A script is the simplest way to use Playwright. It starts a browser, opens a page, does something and closes the browser. Read it line by line in your language.</p>
[[first]]
<p>Three objects appear in every language:</p>
<ul>
<li><b>Browser</b>: one running browser program. Starting it takes about half a second.</li>
<li><b>Page</b>: one tab inside the browser. Almost everything you do, such as <code>goto</code>, <code>click</code> and <code>fill</code>, is done on a page.</li>
<li>{by(java='<b>Playwright</b>: the object you create with <code>Playwright.create()</code>. It starts the driver. Closing it with try with resources closes everything.',
          py='<b>sync_playwright()</b>: starts the driver. The <code>with</code> block stops it at the end, even after an error.',
          js='<b>chromium</b>: the browser type you import. <code>firefox</code> and <code>webkit</code> are imported the same way.')}</li>
</ul>
<p>{by(java='Java calls the method <code>navigate</code>, while the other languages call it <code>goto</code>, because <code>goto</code> is a reserved word in Java.',
      py='Python uses snake case names, such as <code>new_page</code> and <code>get_by_role</code>, where JavaScript writes <code>newPage</code> and <code>getByRole</code>. The meaning is the same.',
      js='JavaScript and TypeScript need <code>await</code> before every Playwright call, because each call sends a message and waits for the answer. Forgetting <code>await</code> is the most common beginner mistake.')}</p>
''', easy=True, kw=['first script', 'launch', 'newPage', 'goto', 'screenshot']),

    part('inside', '🔍', 'How one line travels to the browser', f'''
<p>When your test says <code>click</code>, a lot happens in a few milliseconds. Knowing these layers helps you understand error messages, timeouts and why the same features exist in every language.</p>
<div class="viz" data-viz="flow" data-k="arch"></div>
<p>Now follow one click through every layer. Pick your language and a browser, then press Play.</p>
{viz('pwarch')}
<p>You do not have to imagine any of this. Playwright can print its own log. Set the <code>DEBUG</code> environment variable to <code>pw:api</code> and run the same sign in script. This is real output from the build of this page.</p>
[[debug]]
<p>Two more logs show the layers below. <code>pw:channel</code> prints the messages from the client to the driver, and <code>pw:protocol</code> prints the messages from the driver to the browser.</p>
[[channel]]
[[proto]]
{tip('The driver is the same Node.js program for every language. The Java jar and the Python package carry a copy of it and start it for you. This is why a new feature arrives in Java, Python, JavaScript and C# in the same release.', 'tip')}
''', kw=['architecture', 'driver', 'cdp', 'protocol', 'debug', 'pw:api', 'internals']),

    part('first-test', '✅', 'From a script to a test', f'''
<p>A script does things. A test does things and then <b>checks</b> the result, and a test runner runs many tests, gives each one a fresh page and reports which passed. Here is the same sign in, as a real test, in four languages.</p>
[[firsttest]]
<p>Step through the same test below. Each picture was taken from a real Chromium run when this page was built.</p>
[[walk1]]
<p>Notice what the test does <b>not</b> do. It never waits for a number of seconds and never looks for an element by its position on the screen. It finds things the way a person does, by their label and their role, and it lets Playwright wait.</p>
{tip(by(java='The test method receives a <code>Page</code> because of <code>@UsePlaywright(ShopOptions.class)</code>. JUnit creates a fresh context and page for each test. ShopOptions sets the base address, so <code>navigate("/login")</code> means http://localhost:4173/login.',
        py='The test asks for a <code>page</code> argument. pytest-playwright sees the name and gives the test a fresh page. The <code>--base-url</code> option in pytest.ini makes <code>/login</code> mean http://localhost:4173/login.',
        js='The test asks for <code>{ page }</code>. Playwright Test sees the name, makes a fresh context and page for this test and closes them afterwards. The <code>baseURL</code> in playwright.config makes <code>/login</code> mean http://localhost:4173/login.'), 'tip')}
''', easy=True, kw=['first test', 'test runner', 'expect', 'pytest', 'junit', 'playwright test']),

    part('runner', '🏃', 'What the test runner does for you', f'''
<p>When you type the run command, the runner does the same steps in every language. Press Play to see them in order.</p>
<div class="viz" data-viz="flow" data-k="run"></div>
{table(['Job', '☕ Java', '🐍 Python', '🟨 JavaScript and 🔷 TypeScript'], [
    ['Run the tests', '<code>mvn test</code>', '<code>pytest</code>', '<code>npx playwright test</code>'],
    ['Where settings live', 'an options class, or your own base class', '<code>pytest.ini</code> and <code>conftest.py</code>', '<code>playwright.config.ts</code>'],
    ['A fresh page for each test', '<code>@UsePlaywright</code>, or your own setup methods', 'the <code>page</code> fixture', 'the <code>page</code> fixture'],
    ['Checks that wait', '<code>assertThat(...)</code>', '<code>expect(...)</code>', '<code>expect(...)</code>'],
    ['Run in parallel', 'JUnit or TestNG parallel settings', '<code>pytest -n 4</code> with pytest-xdist', 'built in, one worker per CPU core by default'],
    ['HTML report', 'Allure or ExtentReports', 'pytest-html or Allure', 'built in, plus Allure'],
])}
<p>JavaScript and TypeScript get the most out of the box, because Playwright Test is made by the Playwright team. Java and Python use the test runners those communities already know, and the Playwright library works the same inside them. The rest of this subject shows every feature in all four languages, and tells you clearly when one language has a feature that the others do not.</p>
''', kw=['test runner', 'mvn test', 'pytest', 'npx playwright test', 'context per test']),

    part('roadmap', '🗺️', 'What this subject covers', f'''
<p>The chapters follow the order a new tester meets things at work, from the first install to running a full framework in a pipeline.</p>
{table(['Module', 'You will learn'], [
    ['🚀 Getting started', 'what Playwright is, how it works inside, installing it in four languages, codegen and VS Code'],
    ['🌐 Browser handling', 'browsers, contexts, pages, devices, tabs, pop ups, frames, dialogs, downloads and uploads'],
    ['🎯 Finding and using elements', 'locators, actions and auto waiting, and checks that wait'],
    ['🏃 The test runner', 'configuration, tags, data driven tests, fixtures, hooks, parallel runs, retries and timeouts'],
    ['🔌 Network and API', 'mocking the server, recording traffic, API tests and signing in once'],
    ['🐞 Debugging and quality', 'trace viewer, UI mode, screenshots, videos, visual and accessibility tests, the clock'],
    ['🏗️ Framework design', 'page objects, a real company framework built step by step in each language, CI and Docker'],
    ['📊 Reporting labs', 'the built in reporters, HTML report, Allure, pytest-html, ExtentReports and your own reporter'],
    ['🆕 New and AI features', 'what changed from version 1.45 to 1.64, the Playwright MCP server and test agents'],
])}
<p>Every chapter has a playground at the end. You write a real test in your language and run it against a copy of the practice shop inside this page, one line at a time if you like.</p>
''', easy=True, kw=['roadmap', 'syllabus', 'modules']),
]

INFO = {'title': 'A helper that uses the website for you', 'panels': [
    panel([['e', '🧑‍💻'], ['t', 'your test', {'b': 1}]], 'You write steps', 'Open, type, click, check.', 'In Java, Python, JavaScript or TypeScript.'),
    panel([['e', '📨'], ['t', 'JSON message', {'b': 1}]], 'Messages', 'Each call becomes a small message.', 'The driver is the same for every language.'),
    panel([['e', '🌐'], ['t', 'Chromium · Firefox · WebKit', {'b': 1}]], 'Real browsers', 'Real clicks and real typing.', 'The page cannot tell it apart from a person.'),
    panel([['e', '⏳'], ['t', 'wait until ready', {'b': 1}]], 'It waits', 'Visible, stable, enabled.', 'No fixed sleeps, so far fewer flaky tests.')],
    'remember': 'Playwright drives real browsers through one driver, waits for elements before it acts, and works the same way in Java, Python, JavaScript and TypeScript.'}

REAL = [
    ['🛒', 'An online store before a sale', 'Before a big sale, a test suite places orders in Chromium, Firefox and WebKit every hour, so a broken checkout is found by a test and not by a customer.'],
    ['🏦', 'A bank moving from Selenium', 'A bank team rewrites its slowest Selenium suite in Playwright Java. The suite keeps its JUnit structure, and the waits they used to write by hand disappear.'],
    ['📰', 'A news site with daily screenshots', 'A small Python script opens the home page on a phone size screen every morning and saves a screenshot, so the editors can see the layout without a phone.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter explains what Playwright is, why teams choose it, how one line of a test reaches the browser, and how a test runner runs your tests.',
        'यह अध्याय बताता है कि Playwright क्या है, टीमें इसे क्यों चुनती हैं, टेस्ट की एक लाइन ब्राउज़र तक कैसे पहुँचती है, और test runner टेस्ट कैसे चलाता है।',
        'ಈ ಅಧ್ಯಾಯ Playwright ಎಂದರೇನು, ತಂಡಗಳು ಅದನ್ನು ಏಕೆ ಆಯ್ಕೆ ಮಾಡುತ್ತವೆ, ಟೆಸ್ಟ್‌ನ ಒಂದು ಸಾಲು ಬ್ರೌಸರ್‌ಗೆ ಹೇಗೆ ತಲುಪುತ್ತದೆ ಮತ್ತು test runner ಟೆಸ್ಟ್‌ಗಳನ್ನು ಹೇಗೆ ನಡೆಸುತ್ತದೆ ಎಂದು ವಿವರಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ Playwright କଣ, ଦଳମାନେ ଏହାକୁ କାହିଁକି ବାଛନ୍ତି, ଟେଷ୍ଟର ଗୋଟିଏ ଧାଡ଼ି ବ୍ରାଉଜର ପାଖରେ କିପରି ପହଞ୍ଚେ ଏବଂ test runner ଟେଷ୍ଟ କିପରି ଚଳାଏ ତାହା ବୁଝାଏ।',
        'يشرح هذا الفصل ما هو Playwright ولماذا تختاره الفرق وكيف يصل سطر واحد من الاختبار إلى المتصفح وكيف يشغّل مشغّل الاختبارات اختباراتك.',
        'Dieses Kapitel erklärt, was Playwright ist, warum Teams es wählen, wie eine Zeile eines Tests den Browser erreicht und wie ein Test Runner deine Tests ausführt.'),
    say('what', 'What Playwright is', 'Playwright is a free tool from Microsoft that controls real Chromium, Firefox and WebKit browsers from code. It has official versions for Java, Python, JavaScript, TypeScript and C sharp.',
        'Playwright Microsoft का एक मुफ़्त टूल है जो कोड से असली Chromium, Firefox और WebKit ब्राउज़र चलाता है। इसके आधिकारिक संस्करण Java, Python, JavaScript, TypeScript और C sharp के लिए हैं।',
        'Playwright ಎಂಬುದು Microsoft ನ ಉಚಿತ ಸಾಧನ. ಇದು ಕೋಡ್‌ನಿಂದ ನಿಜವಾದ Chromium, Firefox ಮತ್ತು WebKit ಬ್ರೌಸರ್‌ಗಳನ್ನು ನಿಯಂತ್ರಿಸುತ್ತದೆ. Java, Python, JavaScript, TypeScript ಮತ್ತು C sharp ಗೆ ಅಧಿಕೃತ ಆವೃತ್ತಿಗಳಿವೆ.',
        'Playwright ହେଉଛି Microsoft ର ଏକ ମାଗଣା ଟୁଲ୍, ଯାହା କୋଡ୍ ଦ୍ୱାରା ପ୍ରକୃତ Chromium, Firefox ଓ WebKit ବ୍ରାଉଜର ଚଳାଏ। Java, Python, JavaScript, TypeScript ଓ C sharp ପାଇଁ ଏହାର ସରକାରୀ ସଂସ୍କରଣ ଅଛି।',
        'Playwright أداة مجانية من Microsoft تتحكم بمتصفحات Chromium وFirefox وWebKit الحقيقية من خلال الشيفرة. لها إصدارات رسمية للغات Java وPython وJavaScript وTypeScript وC sharp.',
        'Playwright ist ein kostenloses Werkzeug von Microsoft, das echte Chromium-, Firefox- und WebKit-Browser per Code steuert. Es gibt offizielle Versionen für Java, Python, JavaScript, TypeScript und C sharp.'),
    say('why', 'Why teams pick it', 'Compared with Selenium and Cypress, Playwright waits automatically before every action and check, supports many tabs and domains in one test, and runs tests in parallel for free.',
        'Selenium और Cypress की तुलना में Playwright हर action और check से पहले अपने आप इंतज़ार करता है, एक टेस्ट में कई tabs और domains संभालता है, और मुफ़्त में parallel टेस्ट चलाता है।',
        'Selenium ಮತ್ತು Cypress ಗೆ ಹೋಲಿಸಿದರೆ Playwright ಪ್ರತಿಯೊಂದು action ಮತ್ತು check ಗೆ ಮೊದಲು ತಾನಾಗಿಯೇ ಕಾಯುತ್ತದೆ, ಒಂದೇ ಟೆಸ್ಟ್‌ನಲ್ಲಿ ಹಲವು tabs ಮತ್ತು domains ಬೆಂಬಲಿಸುತ್ತದೆ ಮತ್ತು ಉಚಿತವಾಗಿ parallel ಆಗಿ ನಡೆಸುತ್ತದೆ.',
        'Selenium ଓ Cypress ତୁଳନାରେ Playwright ପ୍ରତ୍ୟେକ action ଓ check ପୂର୍ବରୁ ନିଜେ ଅପେକ୍ଷା କରେ, ଗୋଟିଏ ଟେଷ୍ଟରେ ଅନେକ tabs ଓ domains ସମ୍ଭାଳେ ଏବଂ ମାଗଣାରେ parallel ଟେଷ୍ଟ ଚଳାଏ।',
        'مقارنة بـ Selenium وCypress ينتظر Playwright تلقائيًا قبل كل إجراء وكل تحقق، ويدعم عدة تبويبات ونطاقات في اختبار واحد، ويشغّل الاختبارات بالتوازي مجانًا.',
        'Im Vergleich zu Selenium und Cypress wartet Playwright vor jeder Aktion und jeder Prüfung automatisch, unterstützt mehrere Tabs und Domains in einem Test und führt Tests kostenlos parallel aus.'),
    say('first-look', 'Your first script', 'A script starts a browser, opens a page, prints its title, saves a screenshot and closes the browser. The three main objects are the browser, the page and the Playwright object that starts the driver.',
        'एक script ब्राउज़र शुरू करती है, पेज खोलती है, उसका title छापती है, screenshot सेव करती है और ब्राउज़र बंद करती है। तीन मुख्य objects हैं browser, page और driver शुरू करने वाला Playwright object।',
        'ಒಂದು script ಬ್ರೌಸರ್ ಆರಂಭಿಸಿ, ಪುಟ ತೆರೆದು, ಅದರ title ಮುದ್ರಿಸಿ, screenshot ಉಳಿಸಿ, ಬ್ರೌಸರ್ ಮುಚ್ಚುತ್ತದೆ. ಮೂರು ಮುಖ್ಯ objects ಎಂದರೆ browser, page ಮತ್ತು driver ಆರಂಭಿಸುವ Playwright object.',
        'ଗୋଟିଏ script ବ୍ରାଉଜର ଆରମ୍ଭ କରେ, ପେଜ୍ ଖୋଲେ, ତାହାର title ଛାପେ, screenshot ସେଭ୍ କରେ ଏବଂ ବ୍ରାଉଜର ବନ୍ଦ କରେ। ତିନୋଟି ମୁଖ୍ୟ objects ହେଲା browser, page ଓ driver ଆରମ୍ଭ କରୁଥିବା Playwright object।',
        'يبدأ السكربت متصفحًا ويفتح صفحة ويطبع عنوانها ويحفظ لقطة شاشة ثم يغلق المتصفح. الكائنات الثلاثة الأساسية هي المتصفح والصفحة وكائن Playwright الذي يشغّل المشغّل.',
        'Ein Skript startet einen Browser, öffnet eine Seite, gibt ihren Titel aus, speichert einen Screenshot und schließt den Browser. Die drei wichtigsten Objekte sind Browser, Page und das Playwright-Objekt, das den Treiber startet.'),
    say('inside', 'How one line travels', 'Your call goes to the client library, which sends a JSON message to the Playwright driver. The driver finds the element, waits until it is ready, and sends real input events to the browser through its debugging protocol.',
        'आपकी call client library तक जाती है, जो Playwright driver को एक JSON संदेश भेजती है। Driver element ढूँढता है, उसके तैयार होने तक रुकता है, और debugging protocol से ब्राउज़र को असली input events भेजता है।',
        'ನಿಮ್ಮ call client library ಗೆ ಹೋಗುತ್ತದೆ, ಅದು Playwright driver ಗೆ JSON ಸಂದೇಶ ಕಳುಹಿಸುತ್ತದೆ. Driver element ಹುಡುಕಿ, ಅದು ಸಿದ್ಧವಾಗುವವರೆಗೆ ಕಾಯುತ್ತದೆ ಮತ್ತು debugging protocol ಮೂಲಕ ಬ್ರೌಸರ್‌ಗೆ ನಿಜವಾದ input events ಕಳುಹಿಸುತ್ತದೆ.',
        'ଆପଣଙ୍କ call client library କୁ ଯାଏ, ଯାହା Playwright driver କୁ ଏକ JSON ସନ୍ଦେଶ ପଠାଏ। Driver element ଖୋଜେ, ତାହା ପ୍ରସ୍ତୁତ ହେବା ପର୍ଯ୍ୟନ୍ତ ଅପେକ୍ଷା କରେ ଏବଂ debugging protocol ଦ୍ୱାରା ବ୍ରାଉଜରକୁ ପ୍ରକୃତ input events ପଠାଏ।',
        'يذهب استدعاؤك إلى مكتبة العميل التي ترسل رسالة JSON إلى مشغّل Playwright. يجد المشغّل العنصر وينتظر حتى يصبح جاهزًا ثم يرسل أحداث إدخال حقيقية إلى المتصفح عبر بروتوكول التصحيح.',
        'Dein Aufruf geht an die Client-Bibliothek, die eine JSON-Nachricht an den Playwright-Treiber schickt. Der Treiber findet das Element, wartet, bis es bereit ist, und sendet über das Debugging-Protokoll echte Eingabeereignisse an den Browser.'),
    say('first-test', 'From a script to a test', 'A test does the steps and then checks the result. The test runner gives every test a fresh page. The same sign in test is shown in Java with JUnit, Python with pytest, and JavaScript and TypeScript with Playwright Test.',
        'टेस्ट steps करता है और फिर नतीजा जाँचता है। Test runner हर टेस्ट को नया page देता है। यही sign in टेस्ट Java में JUnit, Python में pytest और JavaScript व TypeScript में Playwright Test के साथ दिखाया गया है।',
        'ಟೆಸ್ಟ್ steps ಮಾಡಿ ನಂತರ ಫಲಿತಾಂಶ ಪರಿಶೀಲಿಸುತ್ತದೆ. Test runner ಪ್ರತಿ ಟೆಸ್ಟ್‌ಗೆ ಹೊಸ page ನೀಡುತ್ತದೆ. ಅದೇ sign in ಟೆಸ್ಟ್ Java ದಲ್ಲಿ JUnit, Python ನಲ್ಲಿ pytest ಮತ್ತು JavaScript, TypeScript ನಲ್ಲಿ Playwright Test ಜೊತೆ ತೋರಿಸಲಾಗಿದೆ.',
        'ଟେଷ୍ଟ steps କରେ ଏବଂ ପରେ ଫଳାଫଳ ଯାଞ୍ଚ କରେ। Test runner ପ୍ରତ୍ୟେକ ଟେଷ୍ଟକୁ ନୂଆ page ଦିଏ। ସେହି sign in ଟେଷ୍ଟ Java ରେ JUnit, Python ରେ pytest ଏବଂ JavaScript ଓ TypeScript ରେ Playwright Test ସହ ଦେଖାଯାଇଛି।',
        'ينفّذ الاختبار الخطوات ثم يتحقق من النتيجة. يعطي مشغّل الاختبارات كل اختبار صفحة جديدة. يظهر اختبار تسجيل الدخول نفسه في Java مع JUnit وفي Python مع pytest وفي JavaScript وTypeScript مع Playwright Test.',
        'Ein Test führt die Schritte aus und prüft dann das Ergebnis. Der Test Runner gibt jedem Test eine frische Seite. Derselbe Anmeldetest wird in Java mit JUnit, in Python mit pytest und in JavaScript und TypeScript mit Playwright Test gezeigt.'),
    say('runner', 'What the runner does', 'The runner reads the settings, starts the browser once per worker, gives every test a new context and page, runs the test, throws the context away and finally writes the report.',
        'Runner settings पढ़ता है, हर worker के लिए एक बार ब्राउज़र शुरू करता है, हर टेस्ट को नया context और page देता है, टेस्ट चलाता है, context हटाता है और अंत में report लिखता है।',
        'Runner settings ಓದಿ, ಪ್ರತಿ worker ಗೆ ಒಮ್ಮೆ ಬ್ರೌಸರ್ ಆರಂಭಿಸಿ, ಪ್ರತಿ ಟೆಸ್ಟ್‌ಗೆ ಹೊಸ context ಮತ್ತು page ನೀಡಿ, ಟೆಸ್ಟ್ ನಡೆಸಿ, context ತೆಗೆದು, ಕೊನೆಗೆ report ಬರೆಯುತ್ತದೆ.',
        'Runner settings ପଢ଼େ, ପ୍ରତ୍ୟେକ worker ପାଇଁ ଥରେ ବ୍ରାଉଜର ଆରମ୍ଭ କରେ, ପ୍ରତ୍ୟେକ ଟେଷ୍ଟକୁ ନୂଆ context ଓ page ଦିଏ, ଟେଷ୍ଟ ଚଳାଏ, context ହଟାଏ ଏବଂ ଶେଷରେ report ଲେଖେ।',
        'يقرأ المشغّل الإعدادات ويشغّل المتصفح مرة لكل عامل ويعطي كل اختبار سياقًا وصفحة جديدين ويشغّل الاختبار ثم يتخلص من السياق ويكتب التقرير في النهاية.',
        'Der Runner liest die Einstellungen, startet den Browser einmal pro Worker, gibt jedem Test einen neuen Kontext und eine neue Seite, führt den Test aus, verwirft den Kontext und schreibt am Ende den Bericht.'),
    say('roadmap', 'What this subject covers', 'The subject goes from installing Playwright and handling browsers, through locators, checks, the test runner, network and API tests and debugging, to framework design, CI, reporting labs and the newest features.',
        'यह विषय Playwright install करने और ब्राउज़र संभालने से शुरू होकर locators, checks, test runner, network और API टेस्ट, debugging से होते हुए framework design, CI, reporting labs और नई सुविधाओं तक जाता है।',
        'ಈ ವಿಷಯ Playwright install ಮತ್ತು ಬ್ರೌಸರ್ ನಿರ್ವಹಣೆಯಿಂದ ಆರಂಭಿಸಿ locators, checks, test runner, network ಮತ್ತು API ಟೆಸ್ಟ್, debugging ಮೂಲಕ framework design, CI, reporting labs ಮತ್ತು ಹೊಸ ವೈಶಿಷ್ಟ್ಯಗಳವರೆಗೆ ಹೋಗುತ್ತದೆ.',
        'ଏହି ବିଷୟ Playwright install ଓ ବ୍ରାଉଜର ସମ୍ଭାଳିବାରୁ ଆରମ୍ଭ କରି locators, checks, test runner, network ଓ API ଟେଷ୍ଟ, debugging ଦେଇ framework design, CI, reporting labs ଓ ନୂଆ ସୁବିଧା ପର୍ଯ୍ୟନ୍ତ ଯାଏ।',
        'يبدأ هذا الموضوع بتثبيت Playwright والتعامل مع المتصفحات، ثم المحددات والتحققات ومشغّل الاختبارات واختبارات الشبكة وAPI والتصحيح، وصولًا إلى تصميم إطار العمل وCI ومختبرات التقارير وأحدث الميزات.',
        'Das Fach führt von der Installation und dem Umgang mit Browsern über Locators, Prüfungen, den Test Runner, Netzwerk- und API-Tests und Debugging bis zu Framework-Design, CI, Reporting-Labs und den neuesten Funktionen.'),
    say('practice', 'Playground labs', 'In the labs you write a real Playwright test in your language and run it against the practice shop inside this page, all at once or one line at a time.',
        'Labs में आप अपनी भाषा में असली Playwright टेस्ट लिखते हैं और इसे इस पेज के अंदर की practice shop पर एक साथ या एक-एक लाइन करके चलाते हैं।',
        'Labs ನಲ್ಲಿ ನೀವು ನಿಮ್ಮ ಭಾಷೆಯಲ್ಲಿ ನಿಜವಾದ Playwright ಟೆಸ್ಟ್ ಬರೆದು ಈ ಪುಟದೊಳಗಿನ practice shop ಮೇಲೆ ಒಮ್ಮೆಗೇ ಅಥವಾ ಒಂದೊಂದು ಸಾಲಾಗಿ ನಡೆಸುತ್ತೀರಿ.',
        'Labs ରେ ଆପଣ ନିଜ ଭାଷାରେ ପ୍ରକୃତ Playwright ଟେଷ୍ଟ ଲେଖନ୍ତି ଏବଂ ଏହି ପେଜ୍ ଭିତରର practice shop ଉପରେ ଏକାଥରେ କିମ୍ବା ଗୋଟିଏ ଗୋଟିଏ ଧାଡ଼ି କରି ଚଳାନ୍ତି।',
        'في المختبرات تكتب اختبار Playwright حقيقيًا بلغتك وتشغّله على متجر التدريب داخل هذه الصفحة دفعة واحدة أو سطرًا بعد سطر.',
        'In den Labs schreibst du einen echten Playwright-Test in deiner Sprache und führst ihn gegen den Übungsshop auf dieser Seite aus, auf einmal oder Zeile für Zeile.'),
]

QUIZ = [
    quiz(1, 'Which browser engines can Playwright drive?', ['Only Chrome', 'Chromium, Firefox and WebKit', 'Only browsers with a WebDriver server', 'Internet Explorer and Edge'], 1,
         'Think of the three engines behind most browsers today.', 'Playwright drives Chromium (Chrome and Edge), Firefox and WebKit (the engine of Safari).'),
    quiz(1, 'Which of these languages has an official Playwright from the Playwright team?', ['Go', 'C++', 'Python', 'Ruby'], 2,
         'The official list is Java, Python, JavaScript, TypeScript and C#.', 'Python is official. Go has only a community project, and C++ and Ruby have no official version.'),
    quiz(1, 'In Java, which method opens a web address?', ['page.goto()', 'page.open()', 'page.navigate()', 'page.get()'], 2,
         'goto is a reserved word in Java.', 'Java uses <code>page.navigate(url)</code>. The other languages use <code>goto</code>.'),
    quiz(1, 'What is the difference between a script and a test?', ['A test is longer', 'A test checks the result, and a runner reports pass or fail', 'A script cannot click', 'There is none'], 1,
         'What does expect add?', 'A test does the steps and then checks the result. A test runner runs many tests and reports which ones passed.'),
    quiz(2, 'In JavaScript, what goes wrong if you forget await before page.click()?', ['Nothing', 'The click runs twice', 'The next line may run before the click finishes, and the test can end early', 'TypeScript adds it for you'], 2,
         'Every Playwright call returns a promise.', 'Without await the test does not wait for the click. Lines run too early and errors can go unnoticed.'),
    quiz(2, 'What does the Playwright driver do?', ['It stores test results', 'It finds elements, waits for them and speaks the browser protocol', 'It compiles Java code', 'It is a browser plug in'], 1,
         'It sits between the client library and the browser.', 'The driver receives messages from your language, finds elements, runs the waiting checks and sends protocol messages to the browser.'),
    quiz(2, 'Why does a new Playwright feature arrive in Java and Python at the same time as in JavaScript?', ['Different teams copy each other', 'All languages share the same driver program', 'Java and Python run JavaScript code directly', 'They do not'], 1,
         'Which part does the real work?', 'The jar and the Python package carry the same Node.js driver. Each language only needs a thin client to call it.'),
    quiz(2, 'What does <code>strict: true</code> in the click message mean?', ['Click only once', 'Fail if the locator matches more than one element', 'Click with the left button', 'Wait for the network'], 1,
         'Look at the channel log.', 'Strict mode makes an action fail when the locator matches several elements, so you never click the wrong one by accident.'),
    quiz(2, 'A test runner gives each test a new browser context. Why?', ['To save memory', 'So cookies, storage and logins never leak from one test to the next', 'Because browsers crash', 'To make tests slower'], 1,
         'A context is like a fresh incognito window.', 'A fresh context keeps tests independent. Any order of tests gives the same results.'),
    quiz(3, 'With DEBUG=pw:protocol in Chromium, which message types the email address into the box?', ['Page.navigate', 'Input.insertText', 'Runtime.evaluate', 'Target.createTarget'], 1,
         'Look at the protocol log.', '<code>fill</code> focuses the box and sends <code>Input.insertText</code> with the whole value at once.'),
    quiz(3, 'In Java and Python, how does the client talk to the driver?', ['Over HTTP to a WebDriver server', 'Over a pipe to a separate Node.js process', 'Through a browser plug in', 'Through a database'], 1,
         'In JavaScript it is the same process.', 'Java and Python start the driver as a child process and send JSON messages over a pipe.'),
    quiz(3, 'Which runner do JavaScript and TypeScript tests usually use with Playwright?', ['Jest', 'Mocha', 'Playwright Test, from @playwright/test', 'Karma'], 2,
         'It is made by the same team.', 'Playwright Test comes in the <code>@playwright/test</code> package and has fixtures, parallel runs, retries, reporters and the trace viewer built in.'),
]

CALC = [
    calc(1, 'A suite has 3 tests and each one runs in Chromium, Firefox and WebKit. How many test runs is that?', 9, 'tests times browsers',
         ['3 tests × 3 browsers', '= 9 runs']),
    calc(1, 'Starting a browser takes about 500 ms and a new context about 10 ms. How many milliseconds do 20 tests spend on setup if they share one browser and each gets its own context?', 700,
         'one browser start plus one context per test', ['500 ms for the browser', '20 × 10 ms = 200 ms for contexts', '500 + 200 = 700 ms']),
    calc(2, 'The same 20 tests start a fresh browser each time, at 500 ms each. How many milliseconds of setup is that?', 10000, '20 × 500',
         ['20 × 500 ms = 10000 ms', 'That is 10 seconds, against 0.7 seconds when the browser is shared']),
    calc(2, 'A manual tester needs 6 minutes to check the checkout in one browser. The team checks 3 browsers every day for 5 working days. How many minutes a week is that?', 90,
         '6 × 3 × 5', ['6 minutes × 3 browsers = 18 minutes a day', '18 × 5 days = 90 minutes a week']),
    calc(2, 'A test has 4 actions. Each one sends 1 message to the driver and gets 1 answer. How many messages travel between the client and the driver?', 8,
         'one message out and one answer back for each action', ['4 actions × 2 messages', '= 8 messages']),
    calc(3, 'A click sent three mouse events in the protocol log: move, press and release. A test clicks 15 times. How many mouse events reach the browser?', 45,
         '3 events per click', ['15 clicks × 3 events', '= 45 mouse events']),
    calc(3, 'A flaky Selenium suite fails at random 1 time in 20 runs. The team runs it 200 times a month. How many random failures is that each month?', 10,
         '200 ÷ 20', ['200 runs ÷ 20', '= 10 random failures to look at, which is why automatic waiting matters']),
    calc(3, 'Playwright Test uses half the CPU cores as workers by default. A laptop has 8 cores. How many workers run at once?', 4, '8 ÷ 2',
         ['8 cores ÷ 2', '= 4 workers']),
]

LABS = [
    {'id': 'title', 'title': 'Open a page and check its title', 'name': 'products page has a title',
     'task': 'Open the products page at <code>/products</code> and check that the page title is <b>Products · Brainy Shop</b>.',
     'goal': 'The test opens the products page and checks the title.', 'start': '',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('products page has a title', async ({ page }) => {
  // 1. go to /products
  // 2. check the title
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('products page has a title', async ({ page }) => {
  await page.goto('/products');
  await expect(page).toHaveTitle('Products · Brainy Shop');
});'''},
     'hint': 'Use <code>page.goto</code> with the path, then <code>expect(page).toHaveTitle(...)</code>. In Java the check is <code>assertThat(page).hasTitle(...)</code>.',
     'why': 'A title check is the smallest useful test. It proves that the page loaded and that it is the right page.',
     'check': [["ctx.url.includes('/products')", 'The test opened the products page'], ["/toHaveTitle|hasTitle|to_have_title|ToHaveTitleAsync/.test(ctx.code)", 'The test checks the title']]},
    {'id': 'signin', 'title': 'Sign in and check the greeting', 'name': 'a customer can sign in',
     'task': 'Sign in as <code>asha@shop.example</code> with the password <code>s3cret</code>, then check that <b>Hello, Asha</b> is visible. Run it one line at a time and watch the shop.',
     'goal': 'Asha is signed in and the test checks the greeting.', 'start': '/login',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('a customer can sign in', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  // fill the password, click Sign in, then check the greeting
});'''},
     'answer': {'ts': FIRST_TEST_TS.replace('a customer can sign in', 'a customer can sign in')},
     'hint': 'The password box has the label <b>Password</b>. The button has the role <b>button</b> and the name <b>Sign in</b>.',
     'why': 'Labels and roles are what a person sees, so the test keeps working when the page layout or CSS classes change.',
     'check': [['ctx.loggedIn', 'Asha is signed in'], ["/Hello, Asha/.test(ctx.code)", 'The test checks the greeting']]},
]

T = {
    'slug': 'pw-intro', 'title': 'What Playwright is and how it works', 'short': 'What Playwright is', 'emoji': '🎭', 'module': MODULE, 'minutes': 16,
    'lead': 'Meet Playwright, the free tool that drives real Chromium, Firefox and WebKit browsers from Java, Python, JavaScript and TypeScript. See how one line of a test travels to the browser, with real logs from a real run.',
    'desc': 'What Playwright is, how it compares with Selenium and Cypress, its architecture with the client, driver and browser protocols, a first script and a first test in Java, Python, JavaScript and TypeScript.',
    'summary': 'What Playwright is and the jobs teams use it for, the official languages, a fact based comparison with Selenium and Cypress, a first script in four languages, how one call travels through the client library, the driver and the browser protocol with real DEBUG=pw:api, pw:channel and pw:protocol logs, a first test with JUnit, pytest and Playwright Test, a recorded sign in walk, and what a test runner does for every test.',
    'keywords': ['playwright', 'introduction', 'architecture', 'driver', 'cdp', 'selenium', 'cypress', 'first test', 'junit', 'pytest', 'playwright test', 'debug log'],
    'plain': 'Playwright is code that uses a website the way a person does. It opens real browsers, clicks and types, waits until things are ready and checks that the page shows the right result.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
