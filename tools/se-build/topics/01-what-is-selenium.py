# Chapter 1.1: what Selenium is. Sources: selenium.dev documentation (Overview, Components, Details, WebDriver,
# Getting started, Using Selenium), selenium.dev/history, the release posts for Selenium 2.0 (2011-07-08), 3.0
# (2016-10-13) and 4.0 (2021-10-13), and the W3C WebDriver Recommendation of 5 June 2018.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, shell, flow

K = Kit()

HELLO = tri('hello', 'A first look: open a page, read its title, close the browser', java=r'''
import org.openqa.selenium.WebDriver;  ## Bring in the WebDriver interface. Every browser driver in Java speaks through it.
import org.openqa.selenium.chrome.ChromeDriver;  ## ChromeDriver is the class that starts and talks to Chrome.

public class FirstLook {  ## A plain Java class. Java runs the main method below.
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();  ## Start Chrome. Selenium Manager finds a matching chromedriver for you, then a new browser session begins.
        driver.get("https://www.selenium.dev/selenium/web/web-form.html");  ## Ask the browser to open the page and wait until it has loaded.
        System.out.println("Title: " + driver.getTitle());  ## Ask the browser for the page title and print it.
        System.out.println("URL: " + driver.getCurrentUrl());  ## Ask which address the browser is showing now.
        driver.quit();  ## End the session. This closes every window and stops the driver process.
    }
}
''', py=r'''
from selenium import webdriver  ## Import the webdriver package, which holds one class per browser.

driver = webdriver.Chrome()  ## Start Chrome. Selenium Manager finds a matching chromedriver, then a new session begins.
driver.get("https://www.selenium.dev/selenium/web/web-form.html")  ## Open the page and wait until it has loaded.
print("Title:", driver.title)  ## driver.title asks the browser for the page title.
print("URL:", driver.current_url)  ## current_url asks which address the browser is showing.
driver.quit()  ## End the session, close every window and stop chromedriver.
''', js=r'''
const { Builder, Browser } = require('selenium-webdriver');  ## Load the two pieces we need from the selenium-webdriver package.

(async function firstLook() {  ## Every Selenium call in JavaScript returns a promise, so we work inside an async function.
  const driver = await new Builder().forBrowser(Browser.CHROME).build();  ## Build a driver for Chrome. Selenium Manager finds chromedriver and a session starts.
  await driver.get('https://www.selenium.dev/selenium/web/web-form.html');  ## Open the page and wait for it to load.
  console.log('Title: ' + await driver.getTitle());  ## Ask for the title. await waits for the browser to answer.
  console.log('URL: ' + await driver.getCurrentUrl());  ## Ask which address the browser shows.
  await driver.quit();  ## End the session and close the browser.
})();
''', expect='Title: Web form')

K.lesson('what', 'What Selenium is', f'''
<p>Think about the last time you bought a train ticket online. You opened a website, typed two station names, picked a date, clicked Search, chose a seat and paid. Every one of those steps is something a person does with a browser. Selenium is a set of free, open source tools that lets a program do the same steps in a real browser, as fast and as often as you like.</p>
<p>The official documentation puts it this way: Selenium is an umbrella project for a range of tools and libraries that enable and support the automation of web browsers. At its core it is a <b>browser user agent library</b>: a library your code calls to control a browser the way a user would. It can type into fields, choose from drop downs, tick boxes, click links, move the mouse and run JavaScript.</p>
{table(['What people use Selenium for', 'An everyday example'], [
    ['Testing web applications', 'Before a bank releases a new version of its login page, a test opens the page in Chrome, Firefox and Edge, logs in with a test account and checks the balance appears.'],
    ['Repetitive tasks', 'A script logs into a supplier portal every morning at 6 and downloads the order report for the day.'],
    ['Collecting data from pages', 'A researcher reads prices from a site that has no API. The docs ask you to check the terms of service of the site first, because some sites forbid it and some block Selenium.']])}
<p>Most people use it for the first one: automated testing. That is why most of this subject is about testing, but every command you learn works for any browser job.</p>
{scene('a shopping site on sale day', '<p>A shop changes its checkout page on Friday. On Saturday thousands of people buy during a sale. If the Pay button stopped working in Firefox, the shop loses money every minute. A Selenium test that runs on every change opens the checkout in each browser, fills the form and presses Pay, so the broken button is caught on Friday afternoon instead of by customers on Saturday.</p>')}
<h3>One interface for every browser</h3>
<p>Chrome, Firefox, Edge and Safari are built very differently inside, even when the pages look the same. A guiding principle of the project is one common interface for all major browsers. Selenium hides the differences, so the same few lines of your code run on each browser. You learn the commands once.</p>
{note('Selenium only controls the browser. It does not decide whether a test passed, it does not write reports and it does not give you Given, When, Then syntax. Those come from a test framework such as JUnit, pytest or Mocha. Chapter 5.1 joins the two.', 'warn')}
''', kw=['what is selenium', 'browser automation', 'user agent library', 'umbrella project', 'open source', 'testing', 'web scraping', 'repetitive tasks', 'cross browser'])

K.lesson('family', 'WebDriver, IDE and Grid', f'''
<p>Selenium is not one tool. The documentation names three parts, and each one answers a different need.</p>
{table(['Part', 'What it is', 'Use it when'], [
    ['<b>WebDriver</b>', 'A library for your programming language plus a driver for each browser. Your code sends commands, the driver makes the browser carry them out.', 'You write automated tests or scripts in Java, Python, JavaScript, C# or Ruby. This is what most of this subject teaches.'],
    ['<b>IDE</b>', 'A Chrome and Firefox extension that records what you do in the browser and plays it back as Selenium commands.', 'You want a quick recording, or you are learning which command matches which action.'],
    ['<b>Grid</b>', 'A server that spreads WebDriver sessions over many machines, browsers and operating systems.', 'One machine is too slow, or you must test on browser and operating system pairs you do not have.']])}
<h3>Four words you will hear every day</h3>
{table(['Word', 'Meaning in the Selenium documentation'], [
    ['API', 'The set of commands you use to control WebDriver, such as get, findElement and click.'],
    ['Library', 'The code module that holds those commands for one language: a .jar file for Java, a pip package for Python, an npm package for JavaScript.'],
    ['Driver', 'The program that controls one browser, such as chromedriver for Chrome and geckodriver for Firefox. Browser vendors write most of them. It usually runs on the same machine as the browser.'],
    ['Framework', 'An extra library that supports a test suite: test runners such as JUnit, pytest or Mocha, or tools such as Cucumber.']])}
{flow(('Your code', 'Calls the WebDriver API in your language.'), ('Language binding', 'The Selenium library turns each call into a command.'), ('Driver', 'chromedriver receives the command.'), ('Browser', 'Chrome does the work and the answer travels back.'))}
<p>Chapter 1.2 opens up that chain and shows the real messages that travel along it.</p>
{ladder(
    '<p>Selenium is a remote control for a web browser. Your program presses the buttons, the browser does what a person would do.</p>',
    '<p>WebDriver is a library plus a browser specific driver. The library sends commands, the driver executes them in the browser, and results come back. IDE records and replays, and Grid runs many sessions on many machines.</p>',
    '<p>WebDriver is a client and server design: the language binding is the local end and the driver is the remote end of the W3C WebDriver protocol. Because the browser is driven through vendor automation APIs and not through code compiled into the app, the build you test is the build you ship.</p>',
    '<p>The W3C protocol separates intent from mechanism. Ongoing work in WebDriver BiDi adds a two way event channel over WebSocket, so a client can listen to console logs, network traffic and DOM changes as they happen, which the request and response design of classic WebDriver cannot do.</p>')}
''', kw=['WebDriver', 'Selenium IDE', 'Selenium Grid', 'API', 'library', 'driver', 'framework', 'chromedriver', 'geckodriver', 'components'])

K.lesson('history', 'How Selenium grew', f'''
<p>Selenium is more than twenty years old, and its history explains its design. The early versions ran JavaScript inside the page. That broke on many browser rules, so the project moved to driving the browser from outside, and in the end the browser makers agreed on a standard.</p>
{viz('se-timeline')}
{table(['Version', 'Released', 'What changed'], [
    ['Selenium 2.0', '8 July 2011', 'The WebDriver APIs became the heart of Selenium. Selenium 1 code still ran.'],
    ['Selenium 3.0', '13 October 2016', 'The original Selenium Core implementation was removed. Every major browser vendor now ships its own driver.'],
    ['W3C WebDriver', '5 June 2018', 'WebDriver became a W3C Recommendation, a standard every browser can implement the same way.'],
    ['Selenium 4.0', '13 October 2021', 'Support for the old JSON Wire Protocol was removed. Only the W3C protocol is used. Relative locators and a rebuilt Grid arrived.']])}
{note('Interviewers like to ask what changed in Selenium 4. The short answer: W3C protocol only, so capabilities must follow the W3C names (browserVersion, platformName) or carry a vendor prefix such as goog:chromeOptions. Options classes replaced DesiredCapabilities, Java lost the findElementById style helpers, and relative locators and Grid 4 arrived. Selenium Manager came later, in 4.6.', 'exam')}
{deep('Why driving from outside the page matters', '<p>A script running inside the page follows the same rules as the page. The browser same origin policy stops a page from one site touching another, so Selenium Core needed a proxy server to pretend every page came from the same place. Events made by JavaScript are also not the same as real ones: the Selenium 2 release notes describe how native events, sent at the operating system level, avoid browser quirks of JavaScript made events. WebDriver lets the browser vendor build the automation into the browser itself, which is why the vendors write the drivers today.</p>')}
''', kw=['history', 'Jason Huggins', 'Selenium RC', 'Selenium Core', 'Simon Stewart', 'Selenium 2', 'Selenium 3', 'Selenium 4', 'W3C Recommendation', 'JSON Wire Protocol'])

K.lesson('look', 'A first look at real code', f'''
<p>Here is the smallest useful Selenium program, written three times. Pick your language with the buttons, then press <b>Explain line by line</b> to read what each line does. The output under the code is real: this page was built by running each program in Chrome.</p>
{HELLO}
<p>All three programs do the same four things: start a session, send the browser somewhere, ask it a question, and end the session. Every Selenium program you will ever write follows that shape. Chapter 1.3 grows it into the eight standard steps.</p>
{note('Always end with quit. If a program stops without it, the driver process and the browser keep running in the background and hold memory and ports. On a busy test machine those leftovers pile up quickly.', 'tip')}
{steps('What happened when the Python version ran', [
    '<code>webdriver.Chrome()</code> asked Selenium Manager for a chromedriver that matches the installed Chrome, started it, and sent it a New Session request.',
    'chromedriver launched Chrome with a fresh, empty profile and replied with a session id.',
    '<code>get</code> sent the address. The driver waited until the page reported it had finished loading, then answered.',
    '<code>title</code> and <code>current_url</code> were two more small questions, each with an answer.',
    '<code>quit</code> sent Delete Session. Chrome and chromedriver both closed.'])}
''', kw=['first program', 'quit', 'session', 'get', 'title', 'current url', 'Java', 'Python', 'JavaScript'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What is Selenium at its core, according to its documentation?', ['A test framework with assertions', 'A browser user agent library that automates browsers', 'A load testing tool', 'A programming language'], 1,
       'It controls something. What?', 'Selenium is a library that drives a real browser the way a user would. Assertions and reports come from a test framework.')
K.quiz('e', 'Which Selenium part records your clicks in the browser and plays them back?', ['WebDriver', 'Grid', 'IDE', 'Selenium Manager'], 2,
       'It is a browser extension.', 'Selenium IDE is a Chrome and Firefox extension that records and replays actions.')
K.quiz('e', 'Which part runs many sessions across many machines?', ['IDE', 'Grid', 'chromedriver', 'pytest'], 1,
       'Think of scale.', 'Selenium Grid routes sessions to nodes on other machines so tests run in parallel and on more browser and OS pairs.')
K.quiz('e', 'Who writes most browser drivers such as chromedriver and geckodriver today?', ['The Selenium project only', 'The browser vendors', 'Test framework authors', 'Cloud providers'], 1,
       'Who knows the browser best?', 'Since Selenium 3, every major browser vendor ships its own driver, built close to the browser.')
K.quiz('m', 'Which of these does Selenium itself NOT do?', ['Click a button', 'Type into a field', 'Decide whether a test passed and write a report', 'Run JavaScript in the page'], 2,
       'Where do assertions come from?', 'Pass or fail, assertions and reports come from the test framework, such as JUnit, pytest or Mocha.')
K.quiz('m', 'Which protocol does Selenium 4 use to talk to drivers?', ['The JSON Wire Protocol only', 'Both JSON Wire and W3C, chosen at random', 'The W3C WebDriver protocol only', 'SOAP'], 2,
       'Selenium 4 removed something.', 'Selenium 4 removed support for the legacy JSON Wire Protocol and uses the W3C standard.')
K.quiz('m', 'When did WebDriver become a W3C Recommendation?', ['July 2011', 'October 2016', 'June 2018', 'October 2021'], 2,
       'Between Selenium 3 and 4.', 'The W3C published WebDriver as a Recommendation on 5 June 2018.')
K.quiz('m', 'What did Selenium 3.0 remove?', ['WebDriver', 'The original Selenium Core implementation', 'Python support', 'Grid'], 1,
       'The oldest piece.', 'The Selenium 3.0 post says the original Selenium Core implementation was removed and replaced by one backed by WebDriver.')
K.quiz('h', 'A tester says: we test the same build we ship, because WebDriver does not need to be compiled into the application. Why is that true?', ['WebDriver patches the app at run time', 'WebDriver drives the browser through vendor automation APIs, outside the app', 'The app must import Selenium', 'It is not true'], 1,
       'Where does the automation live?', 'WebDriver uses browser automation APIs from the vendors, so nothing is added to your app. The docs call this non intrusive.')
K.quiz('x', 'Why did early Selenium need a proxy server to test sites on other domains?', ['To speed pages up', 'Because JavaScript inside a page is bound by the same origin policy', 'Because browsers had no JavaScript', 'To record videos'], 1,
       'Selenium Core ran inside the page.', 'Code inside a page cannot touch pages of other origins. Selenium RC worked around the policy, and WebDriver later removed the need by driving from outside.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Selenium Manager versions use major version 0 and follow Selenium, so Selenium 4.12.0 ships Selenium Manager 0.4.12. Which Selenium Manager version ships with Selenium 4.51.0?', '0.4.51', 'Keep the 0, then the Selenium minor numbers.',
       ['The rule from the docs: Selenium 4.12.0 ships 0.4.12.', 'So the pattern is 0, then the major 4, then the minor.', eq('Selenium 4.51.0 ships Selenium Manager 0.4.51')], check='0.4.51')
K.calc('e', 'How many years passed between Selenium 2.0 (2011) and Selenium 3.0 (2016)?', '5', 'Subtract the years.',
       ['Selenium 2.0: 8 July 2011.', 'Selenium 3.0: 13 October 2016.', eq('2016 − 2011 = 5 years, as the Selenium 3 post itself says')], check=5)
K.calc('m', 'A manual regression check has 40 steps per browser and takes 3 minutes per step. You check 3 browsers. How many minutes is that by hand?', '360', 'Steps × minutes × browsers.',
       ['Per browser: 40 × 3 = 120 minutes.', 'Three browsers: 120 × 3.', eq('360 minutes, which is 6 hours')], check=360)
K.calc('m', 'The same 40 steps run in Selenium at 20 seconds each, one browser after another. How many minutes do the 3 browsers take?', '40', 'Convert seconds to minutes at the end.',
       ['Per browser: 40 × 20 = 800 seconds.', 'Three browsers: 2,400 seconds.', eq('2,400 ÷ 60 = 40 minutes')], check=40)
K.calc('h', 'A suite has 200 tests. Each test opens a fresh browser (2 seconds) and then runs its steps (6 seconds). What percentage of the total time is spent starting browsers?', '25', 'Start time divided by start plus steps.',
       ['Each test takes 2 + 6 = 8 seconds.', 'The share of starting is 2 ÷ 8 for every test, so the number of tests does not change it.', eq('2 ÷ 8 = 0.25 = 25 %')], check=25, unit='%')
K.calc('x', 'The Grid documentation gives total time = tests × average test time ÷ nodes. How many seconds do 15 tests of 45 seconds take on 15 nodes?', '45', 'Every node runs one test at the same time.',
       ['On one machine: 15 × 45 = 675 seconds, which is 11 minutes 15 seconds.', 'Divide by 15 nodes.', eq('675 ÷ 15 = 45 seconds')], check=45)

# ---------------------------------------------------------------- assignments
K.assign('smver', 'e', 'Which Selenium Manager comes with this Selenium?',
         '<p>Write <code>manager_version(selenium)</code>. It takes a Selenium version such as <code>"4.12.0"</code> and returns the Selenium Manager version that ships with it, such as <code>"0.4.12"</code>. The rule from the docs: major version 0, then the Selenium major and minor numbers.</p>',
         '''
def manager_version(selenium):
    # your code here
    pass
''', [('manager_version("4.12.0")', '0.4.12'), ('manager_version("4.51.0")', '0.4.51'), ('manager_version("4.6.0")', '0.4.6')],
         '''
def manager_version(selenium):
    major, minor = selenium.split(".")[:2]
    return "0." + major + "." + minor
''', 'Split the string on dots and keep the first two parts.', '<p>Splitting on dots gives the parts as strings, so no number conversion is needed. The patch number is not used.</p>')
K.assign('era', 'm', 'Which Selenium was current on a date?',
         '<p>Write <code>selenium_major(date)</code>. date is a string <code>"YYYY-MM-DD"</code>. Return the major version of the newest Selenium released on or before that date: 1 before 2011-07-08, 2 from 2011-07-08, 3 from 2016-10-13 and 4 from 2021-10-13.</p>',
         '''
def selenium_major(date):
    # your code here
    pass
''', [('selenium_major("2010-01-01")', 1), ('selenium_major("2011-07-08")', 2), ('selenium_major("2018-06-05")', 3), ('selenium_major("2026-10-29")', 4)],
         '''
def selenium_major(date):
    releases = [("2011-07-08", 2), ("2016-10-13", 3), ("2021-10-13", 4)]
    major = 1
    for day, version in releases:
        if date >= day:
            major = version
    return major
''', 'Dates written as YYYY-MM-DD sort correctly as plain strings.', '<p>Because the year comes first and every part has a fixed width, comparing the strings compares the dates. The W3C Recommendation date falls in the Selenium 3 era.</p>')

K.must('What Selenium is', 'An umbrella project of tools and libraries that automate real browsers the way a user would. At its core, a browser user agent library.')
K.must('Three parts', 'WebDriver (library plus browser driver, for code), IDE (record and play back extension), Grid (many sessions on many machines).')
K.must('Not a test framework', 'Selenium drives the browser. Assertions, test structure and reports come from JUnit, pytest, Mocha and similar tools.')
K.must('Key dates', 'Selenium 2.0 on 8 July 2011, 3.0 on 13 October 2016, W3C Recommendation on 5 June 2018, Selenium 4.0 on 13 October 2021.')
K.must('Program shape', 'Start a session, send the browser somewhere, ask or act, and always quit at the end.')

T = K.topic(
    slug='what-is-selenium', topic='what-is-selenium',
    step=(1, 'Meet Selenium', 'se-meet', 'What Selenium is, how it talks to a browser through the W3C WebDriver protocol, and your first script in Java, Python and JavaScript.', 'Beginner'),
    title='What Selenium is and where it came from', short='What Selenium is', badge='1.1', minutes=30, added='2026-10-29',
    lead='Meet the tools that let a program use a real browser the way you do, see the three parts of the project, and follow twenty years of history to the W3C standard.',
    desc='What Selenium is, its uses, WebDriver, IDE and Grid, the words API, library, driver and framework, the history from JavaScriptTestRunner to Selenium 4 and the W3C Recommendation, and a first program in Java, Python and JavaScript run for real.',
    summary='What Selenium does, its three parts, the key words, its history to the W3C standard and a first real program.',
    keywords=['selenium', 'what is selenium', 'webdriver', 'selenium ide', 'selenium grid', 'history', 'selenium 4', 'w3c'],
    recap='<p>Selenium automates real browsers. WebDriver is the library you call plus a driver per browser, IDE records and replays, and Grid scales out. It started as JavaScript inside the page, moved outside the page with WebDriver, and became a W3C standard in 2018. Selenium 4 speaks only that standard.</p>')
