# Chapter 5.1: Selenium inside a test framework. Sources: selenium.dev documentation (Test runners, Design strategies,
# Encouraged behaviours: Test independency, Fresh browser per test), the JUnit 5 user guide (lifecycle, extensions,
# AfterTestExecutionCallback, parameterized tests), the pytest documentation (fixtures with yield, parametrize,
# making test result information available in fixtures) and the Mocha documentation (hooks, this.currentTest), with real
# runs of every example below.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, src, flow

K = Kit()

SUITE = tri('suite', 'A first test class: a fresh browser for every test', java=r'''
import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class WebFormTest {
    WebDriver driver;  ## A field, so every method of this test can reach the driver.

    @BeforeEach  ## Runs before every test method.
    void startBrowser() {
        driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/web-form.html");
    }

    @Test  ## One test: one behaviour, one reason to fail.
    void pageHasTheRightTitle() {
        assertEquals("Web form", driver.getTitle());  ## Expected value first in JUnit, then the actual one.
    }

    @Test
    void submittingShowsReceived() {
        driver.findElement(By.name("my-text")).sendKeys("Selenium");
        driver.findElement(By.cssSelector("button")).click();
        assertEquals("Received!", driver.findElement(By.id("message")).getText());
    }

    @AfterEach  ## Runs after every test, also when the test failed.
    void quitBrowser() {
        driver.quit();
    }
}
''', py=r'''
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By


@pytest.fixture  ## A fixture is pytest's setup and teardown in one function.
def driver():
    driver = webdriver.Chrome()
    driver.get("https://www.selenium.dev/selenium/web/web-form.html")
    yield driver  ## Everything before yield is setup. The test runs here.
    driver.quit()  ## Everything after yield is teardown, and runs also when the test failed.


def test_page_has_the_right_title(driver):  ## Asking for a parameter called driver makes pytest run the fixture.
    assert driver.title == "Web form"  ## A plain assert. pytest shows both sides when it fails.


def test_submitting_shows_received(driver):
    driver.find_element(By.NAME, "my-text").send_keys("Selenium")
    driver.find_element(By.CSS_SELECTOR, "button").click()
    assert driver.find_element(By.ID, "message").text == "Received!"
''', js=r'''
const { Builder, Browser, By } = require('selenium-webdriver');
const assert = require('assert');

describe('Web form', function () {  ## describe groups tests. Mocha gives every test a name.
  let driver;

  beforeEach(async function () {  ## Runs before every test.
    driver = await new Builder().forBrowser(Browser.CHROME).build();
    await driver.get('https://www.selenium.dev/selenium/web/web-form.html');
  });

  it('has the right title', async function () {  ## One test.
    assert.strictEqual(await driver.getTitle(), 'Web form');  ## Node's own assert module. Actual first, then expected.
  });

  it('shows Received! after submit', async function () {
    await driver.findElement(By.name('my-text')).sendKeys('Selenium');
    await driver.findElement(By.css('button')).click();
    assert.strictEqual(await driver.findElement(By.id('message')).getText(), 'Received!');
  });

  afterEach(async function () {  ## Runs after every test, also when the test failed.
    await driver.quit();
  });
});
''', mode={'java': 'junit', 'py': 'pytest', 'js': 'mocha'})

DATA = tri('datadriven', 'One test, three rows of data', java=r'''
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.time.Duration;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.openqa.selenium.Alert;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class LoginTest {
    WebDriver driver;

    @BeforeEach
    void open() {
        driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/login.html");
    }

    @ParameterizedTest(name = "{0} / {1}")  ## The name shows the data of each run in the report.
    @CsvSource({  ## Each line is one run of the test: username, password, expected message.
        "username, password, You have successfully logged in.",
        "username, wrong, Please enter valid credentials",
        "admin, password, Please enter valid credentials"
    })
    void login(String user, String password, String expected) {  ## JUnit passes the columns in as parameters.
        driver.findElement(By.id("username-field")).sendKeys(user);
        driver.findElement(By.id("password-field")).sendKeys(password);
        driver.findElement(By.id("login-form-submit")).click();
        Alert alert = new WebDriverWait(driver, Duration.ofSeconds(2)).until(ExpectedConditions.alertIsPresent());  ## The page answers with an alert.
        assertEquals(expected, alert.getText());
        alert.accept();
    }

    @AfterEach
    void close() {
        driver.quit();
    }
}
''', py=r'''
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.get("https://www.selenium.dev/selenium/web/login.html")
    yield driver
    driver.quit()


@pytest.mark.parametrize("user, password, expected", [  ## Each tuple is one run of the test.
    ("username", "password", "You have successfully logged in."),
    ("username", "wrong", "Please enter valid credentials"),
    ("admin", "password", "Please enter valid credentials"),
])
def test_login(driver, user, password, expected):  ## pytest passes the columns in as parameters, next to the fixture.
    driver.find_element(By.ID, "username-field").send_keys(user)
    driver.find_element(By.ID, "password-field").send_keys(password)
    driver.find_element(By.ID, "login-form-submit").click()
    alert = WebDriverWait(driver, 2).until(EC.alert_is_present())  ## The page answers with an alert.
    assert alert.text == expected
    alert.accept()
''', js=r'''
const { Builder, Browser, By, until } = require('selenium-webdriver');
const assert = require('assert');

const rows = [  ## Each row is one run of the test.
  ['username', 'password', 'You have successfully logged in.'],
  ['username', 'wrong', 'Please enter valid credentials'],
  ['admin', 'password', 'Please enter valid credentials'],
];

describe('Login', function () {
  let driver;
  beforeEach(async function () {
    driver = await new Builder().forBrowser(Browser.CHROME).build();
    await driver.get('https://www.selenium.dev/selenium/web/login.html');
  });

  for (const [user, password, expected] of rows) {  ## Mocha has no data annotation. A loop that calls it() once per row does the same job.
    it(`${user} / ${password}`, async function () {
      await driver.findElement(By.id('username-field')).sendKeys(user);
      await driver.findElement(By.id('password-field')).sendKeys(password);
      await driver.findElement(By.id('login-form-submit')).click();
      const alert = await driver.wait(until.alertIsPresent(), 2000);  ## The page answers with an alert.
      assert.strictEqual(await alert.getText(), expected);
      await alert.accept();
    });
  }

  afterEach(async function () {
    await driver.quit();
  });
});
''', mode={'java': 'junit', 'py': 'pytest', 'js': 'mocha'})

FAILSHOT = tri('failshot', 'A failing test that saves a screenshot before the browser closes', java=r'''
import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

@ExtendWith(ScreenshotOnFailure.class)  ## Plug the extension into this test class.
public class TitleTest {
    WebDriver driver;  ## The extension reads this field.

    @BeforeEach
    void open() {
        driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/web-form.html");
    }

    @Test
    void titleIsWrongOnPurpose() {
        assertEquals("Web form!", driver.getTitle());  ## Wrong on purpose, so the test fails.
    }

    @AfterEach  ## Runs after the extension, so the browser is still open when the screenshot is taken.
    void close() {
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver


def test_title_is_wrong_on_purpose(driver):  ## The driver fixture comes from conftest.py.
    driver.get("https://www.selenium.dev/selenium/web/web-form.html")
    assert driver.title == "Web form!"  ## Wrong on purpose, so the test fails.
''', js=r'''
const { Builder, Browser } = require('selenium-webdriver');
const assert = require('assert');
const fs = require('fs');

describe('Title', function () {
  let driver;
  beforeEach(async function () {
    driver = await new Builder().forBrowser(Browser.CHROME).build();
    await driver.get('https://www.selenium.dev/selenium/web/web-form.html');
  });

  it('is wrong on purpose', async function () {
    assert.strictEqual(await driver.getTitle(), 'Web form!');  ## Wrong on purpose, so the test fails.
  });

  afterEach(async function () {
    if (this.currentTest.state === 'failed') {  ## Mocha tells the hook how the test ended.
      const name = 'failure-' + this.currentTest.title.replace(/ /g, '-') + '.png';
      fs.writeFileSync(name, await driver.takeScreenshot(), 'base64');  ## Take the picture before quit.
      console.log('saved ' + name + ' ' + (fs.statSync(name).size > 0));
    }
    await driver.quit();
  });
});
''', mode={'java': 'junit', 'py': 'pytest', 'js': 'mocha'}, fail=True, extra={
    'java': {'ScreenshotOnFailure.java': r'''
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import org.junit.jupiter.api.extension.AfterTestExecutionCallback;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;

public class ScreenshotOnFailure implements AfterTestExecutionCallback {  ## Called right after the test method, before any AfterEach method.
    @Override
    public void afterTestExecution(ExtensionContext context) throws Exception {
        if (context.getExecutionException().isPresent()) {  ## Present only when the test threw, so only when it failed.
            WebDriver driver = ((TitleTest) context.getRequiredTestInstance()).driver;
            Path shot = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE).toPath();
            Path target = Path.of("failure-" + context.getRequiredTestMethod().getName() + ".png");  ## Name the file after the test.
            Files.copy(shot, target, StandardCopyOption.REPLACE_EXISTING);
            System.out.println("saved " + target + " " + (Files.size(target) > 0));
        }
    }
}
'''},
    'py': {'conftest.py': r'''
import os

import pytest
from selenium import webdriver


@pytest.hookimpl(wrapper=True, tryfirst=True)  ## A hook that sees every test report as pytest builds it.
def pytest_runtest_makereport(item, call):
    report = yield
    setattr(item, "rep_" + report.when, report)  ## Keep the report on the test item: rep_setup, rep_call and rep_teardown.
    return report


@pytest.fixture
def driver(request):
    driver = webdriver.Chrome()
    yield driver
    if request.node.rep_call.failed:  ## Did the test body fail?
        name = f"failure-{request.node.name}.png"  ## Name the file after the test.
        driver.save_screenshot(name)  ## Take the picture before quit.
        print("saved", name, os.path.getsize(name) > 0)
    driver.quit()
'''}})

K.lesson('runners', 'Selenium inside a test framework', f'''
<p>Selenium drives the browser. It does not decide whether a test passed, it does not group tests, and it does not write a report. A <b>test framework</b> does that: JUnit 5 for Java, pytest for Python and Mocha for JavaScript are the ones the Selenium documentation uses in its own examples. The framework finds your tests, runs setup before each one and teardown after it, compares values with assertions and reports what passed and failed.</p>
{viz('se-lifecycle')}
{SUITE}
{table(['Job', 'JUnit 5', 'pytest', 'Mocha'], [
    ['Before every test', '<code>@BeforeEach</code>', 'fixture code before <code>yield</code>', '<code>beforeEach</code>'],
    ['After every test', '<code>@AfterEach</code>', 'fixture code after <code>yield</code>', '<code>afterEach</code>'],
    ['Once for the class or file', '<code>@BeforeAll</code>, <code>@AfterAll</code>', '<code>scope="module"</code> or <code>"session"</code>', '<code>before</code>, <code>after</code>'],
    ['Check a value', '<code>assertEquals(expected, actual)</code>', '<code>assert actual == expected</code>', '<code>assert.strictEqual(actual, expected)</code>'],
    ['Run it', 'build tool or console launcher', '<code>pytest</code>', '<code>mocha</code> or <code>npx mocha</code>']])}
{note('The Selenium documentation recommends a fresh browser for every test. Then no cookie, login or open dialog can leak from one test into the next, and the tests can run in any order or in parallel. It costs a browser start per test, a price that is almost always worth paying.', 'tip')}
{scene('the flaky Friday test', '<p>A team shares one browser across a whole test class to save time. One test logs out at the end, and on Friday the runner orders the tests differently: the logout test runs before the cart test, and the cart test fails with a login page. Nothing in the cart test is wrong. Moving the driver into a before each and after each pair makes the failure disappear for good.</p>')}
''', kw=['test framework', 'junit 5', 'pytest', 'mocha', 'before each', 'after each', 'fixture', 'yield', 'assert', 'assertion', 'test runner', 'fresh browser per test'])

K.lesson('datadriven', 'Data-driven tests', f'''
<p>The login page has one form and many cases: right user and password, wrong password, unknown user. Copying the test three times means three places to fix when the form changes. A <b>parameterized test</b> writes the steps once and feeds them a table of data. The report shows one result per row.</p>
{DATA}
<p>Look at each report. JUnit used the name pattern for every row and Mocha used the title built by the loop. pytest ran in quiet mode, so it printed one dot per row, three dots for three runs. Run it with <code>-v</code> and it lists each row with its data in the test id. When the second row fails one day, the report says which row, without opening the code.</p>
{note('Keep the data close to the test while it is small. When it grows, move it to a CSV or JSON file: JUnit has @CsvFileSource, and pytest and Mocha can read any file into the same list.', 'tip')}
''', kw=['data driven', 'parameterized test', 'parametrize', 'csv source', 'test data', 'rows'])

K.lesson('failshot', 'A screenshot when a test fails', f'''
<p>A red test in a report from the night run says what was expected, not what the page looked like. A screenshot taken at the moment of failure answers that. The trick is the order: the picture must be taken <b>after</b> the test failed but <b>before</b> the browser is closed. Each framework has its own place for that.</p>
{FAILSHOT}
{table(['Framework', 'Where the screenshot code goes', 'How it knows the test failed'], [
    ['JUnit 5', 'An extension with <code>AfterTestExecutionCallback</code>, which runs before <code>@AfterEach</code>', '<code>context.getExecutionException()</code> is present'],
    ['pytest', 'The fixture, after <code>yield</code> and before <code>quit()</code>', 'A <code>pytest_runtest_makereport</code> hook in conftest.py stores the report on the test'],
    ['Mocha', 'The <code>afterEach</code> hook, before <code>quit()</code>', '<code>this.currentTest.state</code> is "failed"']])}
<p>The run on this page failed on purpose, and each language printed "saved" followed by true, which means the file was written and is not empty. The failure message itself shows the expected title "Web form!" and the real one, "Web form".</p>
{ladder(
    '<p>A test framework runs your Selenium code as tests: setup before, the test, teardown after, and a pass or fail for each.</p>',
    '<p>Start a fresh browser in the before each step and quit it in the after each step. Use parameterized tests for many rows of data and take a screenshot in the after step when the test failed.</p>',
    '<p>Each framework has hooks at different points: JUnit extensions, pytest fixtures and hook functions, Mocha hooks with this.currentTest. Teardown runs whatever happened in the test, which is why quit belongs there.</p>',
    '<p>Fixtures with a wider scope, such as one browser per worker, trade isolation for speed. Combine them with deleteAllCookies and a fresh page in a function scoped fixture, and with parallel runners such as pytest-xdist or JUnit parallel execution.</p>')}
''', kw=['screenshot on failure', 'test watcher', 'extension', 'conftest', 'makereport', 'current test state', 'failure', 'report'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Which part decides whether a Selenium test passed?', ['The driver', 'The browser', 'The test framework and its assertions', 'Selenium Manager'], 2,
       'Selenium only drives.', 'Assertions and pass or fail come from the test framework.')
K.quiz('e', 'In a pytest fixture, where does the teardown code go?', ['Before yield', 'After yield', 'In the test', 'In conftest only'], 1,
       'yield hands over the driver.', 'Code after yield runs when the test is finished.')
K.quiz('e', 'Which JUnit 5 annotation runs before every test method?', ['@BeforeAll', '@BeforeEach', '@Test', '@Setup'], 1,
       'Each.', '@BeforeEach runs before every test method.')
K.quiz('m', 'Why does the documentation recommend a fresh browser per test?', ['It is faster', 'No state leaks between tests, so they run in any order', 'Browsers crash otherwise', 'Grid requires it'], 1,
       'Think of cookies and logins.', 'Fresh browsers keep tests independent of each other and of their order.')
K.quiz('m', 'A test fails at its assertion. Does @AfterEach, the fixture teardown or afterEach still run?', ['No', 'Yes', 'Only in pytest', 'Only if the browser is open'], 1,
       'That is what teardown is for.', 'Teardown runs whether the test passed or failed, so quit is never skipped.')
K.quiz('m', 'A parameterized test has 3 rows. How many test results does the report show?', ['1', '3', '6', 'It depends on the browser'], 1,
       'One per row.', 'Each row is a separate run with its own result.')
K.quiz('m', 'Mocha has no parameter annotation. How did the example run one test per row?', ['With describe.each', 'A loop that calls it() for each row', 'A CSV plugin', 'It cannot'], 1,
       'Plain JavaScript.', 'A for loop around it() creates one test per row.')
K.quiz('h', 'Why does the JUnit example use AfterTestExecutionCallback and not a TestWatcher?', ['It is newer', 'It runs before @AfterEach, while the browser is still open', 'TestWatcher cannot read fields', 'It runs faster'], 1,
       'Order matters.', 'The screenshot needs the browser, and @AfterEach quits it.')
K.quiz('h', 'In the pytest example, what does request.node.rep_call.failed tell the fixture?', ['That setup failed', 'That the test body failed', 'That teardown failed', 'That the browser crashed'], 1,
       'call is the test body.', 'The hook stores one report per phase: setup, call and teardown. call is the test body.')
K.quiz('x', 'A suite shares one browser for a whole class to save time. What is the main risk?', ['Slower tests', 'State from one test changes the result of another', 'More memory', 'No screenshots'], 1,
       'Order dependence.', 'Shared state makes results depend on test order, the classic flaky test.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A class has 4 tests with a fresh browser per test. How many browsers start?', '4', 'One per test.',
       ['@BeforeEach runs once per test.', 'There are 4 tests.', eq('4 browsers')], check=4)
K.calc('e', 'A parameterized test has 5 rows and the class has 2 other tests. How many results are in the report?', '7', 'Rows count as tests.',
       ['The parameterized test gives 5 results.', 'The other tests give 2.', eq('5 + 2 = 7')], check=7)
K.calc('m', 'A browser starts in 1.5 s. A suite of 120 tests uses a fresh browser per test. How many minutes are spent starting browsers?', '3', 'Total seconds, then minutes.',
       ['120 × 1.5 = 180 s.', 'There are 60 s in a minute.', eq('180 ÷ 60 = 3 minutes')], check=3, unit='min')
K.calc('m', 'The same suite runs on 4 parallel workers. Roughly how long do browser starts take now, in seconds?', '45', 'Shared across workers.',
       ['180 s of starts in total.', 'Each worker does a quarter.', eq('180 ÷ 4 = 45 s')], check=45, unit='s')
K.calc('h', 'A nightly run of 400 tests fails 6 tests. Each screenshot is 60 KB. How many KB of screenshots does it store?', '360', 'Only failures.',
       ['Screenshots are taken only for failed tests.', '6 failures.', eq('6 × 60 = 360 KB')], check=360, unit='KB')
K.calc('x', 'A test has 3 rows of data and runs in 3 browsers. Each run takes 4 s. With 3 parallel workers, how many seconds does it take at least?', '12', 'Count runs, then share.',
       ['Runs: 3 rows × 3 browsers = 9.', 'Total time: 9 × 4 = 36 s.', eq('36 ÷ 3 workers = 12 s')], check=12, unit='s')

# ---------------------------------------------------------------- assignments
K.assign('hookorder', 'e', 'Write down the hook order',
         '<p>Write <code>hook_order(tests)</code>. <code>tests</code> is a list of test names. Return the list of steps a framework runs, with "before" and "after" around each test, like this: before, test name, after, before, next test, after.</p>',
         '''
def hook_order(tests):
    # your code here
    pass
''', [('hook_order(["a"])', ['before', 'a', 'after']), ('hook_order(["a", "b"])', ['before', 'a', 'after', 'before', 'b', 'after']), ('hook_order([])', [])],
         '''
def hook_order(tests):
    steps = []
    for name in tests:
        steps += ["before", name, "after"]
    return steps
''', 'Three entries per test.', '<p>This is the order of @BeforeEach and @AfterEach in JUnit, a function scoped fixture in pytest and beforeEach and afterEach in Mocha.</p>')
K.assign('shotname', 'm', 'Name the failure screenshot',
         '<p>Write <code>shot_name(test, row)</code>. Return a file name for the screenshot of a failed test: "failure-", then the test name with spaces replaced by dashes, then "-" and the row number when <code>row</code> is not None, then ".png".</p>',
         '''
def shot_name(test, row):
    # your code here
    pass
''', [('shot_name("is wrong on purpose", None)', 'failure-is-wrong-on-purpose.png'), ('shot_name("login", 2)', 'failure-login-2.png'), ('shot_name("a b", 0)', 'failure-a-b-0.png')],
         '''
def shot_name(test, row):
    name = "failure-" + test.replace(" ", "-")
    if row is not None:
        name += "-" + str(row)
    return name + ".png"
''', 'Check row against None, because row 0 is a real row.', '<p>A name with the row number tells you which data row failed. Testing <code>if row:</code> would drop row 0.</p>')

K.must('Framework jobs', 'Selenium drives the browser. JUnit 5, pytest or Mocha find the tests, run setup and teardown, assert and report.')
K.must('Fresh browser', 'Start the driver in the before each step and quit it in the after each step, so tests stay independent and can run in any order.')
K.must('Teardown always runs', '@AfterEach, code after yield and afterEach run also when the test failed, so quit belongs there.')
K.must('Data-driven', '@ParameterizedTest with @CsvSource, @pytest.mark.parametrize, or a loop around it() in Mocha. One result per row.')
K.must('Screenshot on failure', 'Take it after the test failed and before quit: a JUnit AfterTestExecutionCallback, a pytest makereport hook plus fixture, or Mocha this.currentTest.state.')

T = K.topic(
    slug='test-frameworks', topic='test-frameworks',
    step=(5, 'Build a test suite', 'se-suite', 'Test frameworks, page objects, good practices and the errors you will meet.', 'Intermediate'),
    title='Test frameworks: JUnit 5, pytest and Mocha', short='Test frameworks', badge='5.1', minutes=55, added='2026-10-29',
    lead='Turn Selenium scripts into real tests: setup and teardown with a fresh browser for each test, assertions, data-driven tests, and a screenshot whenever a test fails.',
    desc='JUnit 5, pytest and Mocha with real runs, an animation of the test lifecycle, before each and after each, fixtures with yield, assertions, parameterized tests with CsvSource, parametrize and a loop, and a screenshot on failure through a JUnit extension, a pytest hook and a Mocha hook.',
    summary='Running Selenium inside JUnit 5, pytest and Mocha, with data-driven tests and screenshots on failure.',
    keywords=['junit', 'pytest', 'mocha', 'test framework', 'fixture', 'before each', 'after each', 'parameterized', 'data driven', 'screenshot on failure'],
    recap='<p>A test framework runs Selenium code as tests. Start a fresh browser before each test and quit it after, because teardown runs whether the test passed or failed. Use parameterized tests for many rows of data, and take a screenshot after a failure and before quit.</p>')
