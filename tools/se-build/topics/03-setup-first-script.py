# Chapter 1.3: installing Selenium, Selenium Manager and the eight basic components of a script. Sources:
# selenium.dev documentation (Install a Selenium library, Write your first Selenium script, Selenium Manager, Service,
# Quitting sessions), the package metadata of Selenium 4.51.0 (Python requires >=3.10, selenium-webdriver engines
# node >=22, Java jars built for Java 11), and real runs of selenium-manager 0.4.51 recorded when the page was built.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, src, flow

K = Kit()

EIGHT = tri('eight', 'The eight basic components of a Selenium script', java=r'''
import java.time.Duration;  ## Duration describes a length of time, used for the wait below.
import org.openqa.selenium.By;  ## By holds the ways to locate an element: by name, by CSS selector and more.
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;  ## A WebElement is your handle on one element of the page.
import org.openqa.selenium.chrome.ChromeDriver;

public class FirstScript {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();  ## 1. Start the session. Chrome opens with a fresh profile.
        driver.get("https://www.selenium.dev/selenium/web/web-form.html");  ## 2. Take action on the browser: go to the practice form.
        String title = driver.getTitle();  ## 3. Request browser information: the page title.
        System.out.println("Title: " + title);
        driver.manage().timeouts().implicitlyWait(Duration.ofMillis(500));  ## 4. Establish a waiting strategy. Find calls will now retry for up to half a second.
        WebElement textBox = driver.findElement(By.name("my-text"));  ## 5. Find an element: the text box whose name attribute is my-text.
        WebElement submitButton = driver.findElement(By.cssSelector("button"));  ## 5. Find another: the first button on the page.
        textBox.sendKeys("Selenium");  ## 6. Take action on an element: type into the box.
        submitButton.click();  ## 6. Click Submit. The browser loads the next page.
        WebElement message = driver.findElement(By.id("message"));  ## Find the message on the new page. The implicit wait gives it time to appear.
        String value = message.getText();  ## 7. Request element information: its visible text.
        System.out.println("Message: " + value);
        driver.quit();  ## 8. End the session. The browser and the driver both close.
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.common.by import By  ## By holds the locator strategies: By.NAME, By.CSS_SELECTOR and more.

driver = webdriver.Chrome()  ## 1. Start the session. Chrome opens with a fresh profile.
driver.get("https://www.selenium.dev/selenium/web/web-form.html")  ## 2. Take action on the browser: go to the practice form.
title = driver.title  ## 3. Request browser information: the page title.
print("Title:", title)
driver.implicitly_wait(0.5)  ## 4. Establish a waiting strategy. Python takes seconds, so 0.5 means half a second.
text_box = driver.find_element(by=By.NAME, value="my-text")  ## 5. Find an element by its name attribute.
submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")  ## 5. Find the first button with a CSS selector.
text_box.send_keys("Selenium")  ## 6. Take action on an element: type into the box.
submit_button.click()  ## 6. Click Submit. The browser loads the next page.
message = driver.find_element(by=By.ID, value="message")  ## Find the message on the new page.
value = message.text  ## 7. Request element information: its visible text.
print("Message:", value)
driver.quit()  ## 8. End the session. The browser and the driver both close.
''', js=r'''
const { Builder, Browser, By } = require('selenium-webdriver');  ## Builder makes drivers, Browser names browsers, By builds locators.

(async function firstScript() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();  ## 1. Start the session. Chrome opens with a fresh profile.
  await driver.get('https://www.selenium.dev/selenium/web/web-form.html');  ## 2. Take action on the browser: go to the practice form.
  const title = await driver.getTitle();  ## 3. Request browser information: the page title.
  console.log('Title: ' + title);
  await driver.manage().setTimeouts({ implicit: 500 });  ## 4. Establish a waiting strategy. JavaScript takes milliseconds.
  const textBox = await driver.findElement(By.name('my-text'));  ## 5. Find an element by its name attribute.
  const submitButton = await driver.findElement(By.css('button'));  ## 5. Find the first button with a CSS selector.
  await textBox.sendKeys('Selenium');  ## 6. Take action on an element: type into the box.
  await submitButton.click();  ## 6. Click Submit. The browser loads the next page.
  const message = await driver.findElement(By.id('message'));  ## Find the message on the new page.
  const value = await message.getText();  ## 7. Request element information: its visible text.
  console.log('Message: ' + value);
  await driver.quit();  ## 8. End the session. The browser and the driver both close.
})();
''', expect='Message: Received!')

TIDY = tri('tidy', 'Quit even when something fails', java=r'''
import org.openqa.selenium.By;
import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class AlwaysQuit {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();  ## Start the session outside the try, so driver is known in finally.
        try {  ## Everything that might fail goes inside try.
            driver.get("https://www.selenium.dev/selenium/web/web-form.html");
            driver.findElement(By.id("no-such-id"));  ## This element does not exist, so this line throws.
            System.out.println("never printed");  ## Java jumps straight to catch and never reaches this line.
        } catch (NoSuchElementException e) {  ## Catch the error so we can report it.
            System.out.println("Failed: " + e.getMessage().split("\n")[0]);  ## Print only the first line of the message.
        } finally {  ## finally runs whether the try worked or failed.
            driver.quit();  ## So the browser always closes.
            System.out.println("Browser closed");
        }
    }
}
''', py=r'''
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

with webdriver.Chrome() as driver:  ## A with block calls driver.quit() for you when the block ends, even after an error.
    driver.get("https://www.selenium.dev/selenium/web/web-form.html")
    try:
        driver.find_element(By.ID, "no-such-id")  ## This element does not exist, so this line raises.
        print("never printed")
    except NoSuchElementException as e:  ## Catch the error so we can report it.
        print("Failed:", e.msg.split("\n")[0])  ## e.msg is the message from the driver. Keep its first line.
print("Browser closed")  ## We are outside the with block, so quit has already run.
''', js=r'''
const { Builder, Browser, By, error } = require('selenium-webdriver');  ## error holds the exception classes.

(async function alwaysQuit() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  try {  ## Everything that might fail goes inside try.
    await driver.get('https://www.selenium.dev/selenium/web/web-form.html');
    await driver.findElement(By.id('no-such-id'));  ## This element does not exist, so the promise rejects.
    console.log('never printed');
  } catch (e) {
    if (!(e instanceof error.NoSuchElementError)) throw e;  ## Only swallow the error we expected. Anything else is a real bug.
    console.log('Failed: ' + e.message.split('\n')[0]);
  } finally {  ## finally runs whether the try worked or failed.
    await driver.quit();  ## So the browser always closes.
    console.log('Browser closed');
  }
})();
''', expect='Browser closed')

MISMATCH = solo('mismatch', 'What an old driver on a new browser looks like', 'py', r'''
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.chrome.service import Service  ## Service describes how to start the driver program.

service = Service(executable_path="/opt/drivers/chromedriver-147")  ## Point Selenium at an old chromedriver 147 on purpose. Selenium Manager is now skipped.
try:
    driver = webdriver.Chrome(service=service)  ## Chrome on this machine is version 153, so New Session fails.
    driver.quit()
except SessionNotCreatedException as e:  ## The driver answered with the W3C error code session not created.
    print(e.msg.split("\n")[0])  ## Print the first line of the driver's message.
''', expect='only supports Chrome version 147', why='Python only, because the error comes from chromedriver and reads the same in every language. The driver path is given by hand, so Selenium Manager never gets the chance to fix it.')

K.lesson('install', 'Install Selenium for your language', f'''
<p>Before any code runs you need two things on your machine: the Selenium library for your language and a browser. The third piece, the driver, is handled for you, as the next lesson shows.</p>
{table(['Language', 'Minimum version for Selenium 4.51', 'How you add Selenium'], [
    ['Java', 'Java 11 (the jars are built for Java 11)', 'A build tool. Add <code>org.seleniumhq.selenium:selenium-java</code> to Maven or Gradle.'],
    ['Python', 'Python 3.10', '<code>pip install selenium</code>, or a line <code>selenium==4.51.0</code> in requirements.txt'],
    ['JavaScript', 'Node.js 22', '<code>npm install selenium-webdriver</code>']])}
<p>The Selenium documentation points to the package pages for the current minimum, so check them when you upgrade. The versions above are what the 4.51.0 packages declare.</p>
<h3>Java with Maven</h3>
<p>The documentation shows the dependency for a Maven <code>pom.xml</code>. Maven downloads selenium-java and everything it needs when you build.</p>
{src('java', """<dependency>
  <groupId>org.seleniumhq.selenium</groupId>
  <artifactId>selenium-java</artifactId>
  <version>4.51.0</version>
</dependency>""", 'pom.xml')}
<p>With Gradle the same coordinates go in <code>build.gradle</code> as <code>testImplementation 'org.seleniumhq.selenium:selenium-java:4.51.0'</code>.</p>
<h3>Python and JavaScript</h3>
{shell('Install in a fresh project', """python3 -m venv .venv
source .venv/bin/activate
pip install selenium
npm init -y
npm install selenium-webdriver""")}
{note('Use a virtual environment in Python and a package.json in JavaScript. Each project then pins its own Selenium version, so upgrading one project never breaks another.', 'tip')}
{scene('a new tester joins the team', '<p>Priya clones the test project on her first day. She runs <code>mvn test</code>, Maven reads the version from pom.xml and fetches selenium-java 4.51.0. She already has Chrome. She does not download chromedriver at all: the first test run asks Selenium Manager for it. Her setup takes minutes, and her machine runs the same Selenium version as everyone else.</p>')}
''', kw=['install', 'maven', 'gradle', 'pip install selenium', 'npm install selenium-webdriver', 'requirements', 'java 11', 'python 3.10', 'node 22', 'virtual environment'])

K.lesson('manager', 'Selenium Manager finds the driver', f'''
<p>Every browser needs its driver: chromedriver for Chrome, geckodriver for Firefox, msedgedriver for Edge. For years people downloaded the driver by hand and put it on the PATH. The documentation describes why that broke. Chrome is <b>evergreen</b>: it updates itself quietly. Your chromedriver 113 worked on Monday, Chrome updated to 115 on Tuesday, and every test failed with <code>session not created: This version of ChromeDriver only supports Chrome version 113</code>.</p>
<p>Since Selenium 4.6, every release ships <b>Selenium Manager</b>, the official driver manager. It is a small command line program written in Rust, built for Windows, Linux and macOS, and stored inside the library you installed. Your binding calls it only as a fallback, when you have not given a driver yourself.</p>
{viz('se-manager')}
{steps('Automated driver management, as the documentation lists it', [
    '<b>Browser version discovery.</b> It runs a shell command such as <code>google-chrome --version</code> to learn which browser version is installed.',
    '<b>Driver version discovery.</b> It asks the browser vendor which driver version fits that browser.',
    '<b>Driver download.</b> It downloads the driver archive, unpacks it and stores it.',
    '<b>Driver cache.</b> Drivers live in <code>~/.cache/selenium</code>. Next time the same driver is taken from there.'])}
<p>Since Selenium 4.11 it also manages <b>browsers</b>. If Chrome is missing, or you ask for a version you do not have through the <code>browserVersion</code> option, it downloads Chrome for Testing into the cache. Firefox followed in 4.12 and Edge in 4.14. Labels such as <code>stable</code>, <code>beta</code>, <code>dev</code> and <code>canary</code> work as versions too.</p>
<h3>Watch it work</h3>
<p>You can run Selenium Manager yourself. This log was recorded on the Linux machine that built this page, with the network switched off and a chromedriver already on PATH. Read it from the top: driver found on PATH, browser found, browser version read, then the two paths the binding will use.</p>
{shell('Ask Selenium Manager what it would use', 'selenium-manager --browser chrome --offline --debug', out="""
[DEBUG] Offline flag set, but also asked not to avoid browser downloads. Honouring offline flag
[DEBUG] Using Selenium Manager in offline mode
[DEBUG] Found chromedriver 153.0.8010.12 in PATH: /usr/local/bin/chromedriver
[DEBUG] chrome detected at /opt/google/chrome/chrome
[DEBUG] Running command: /opt/google/chrome/chrome --version
[DEBUG] Output: "Google Chrome for Testing 153.0.8010.12 "
[DEBUG] Detected browser: chrome 153.0.8010.12
[DEBUG] Exception managing chrome: Unable to discover proper chromedriver version in offline mode
[INFO ] Driver path: /usr/local/bin/chromedriver
[INFO ] Browser path: /opt/google/chrome/chrome""", cap='Recorded with selenium-manager 0.4.51 on Linux (timestamps removed, folder names shortened)')}
<p>The same machine with an old chromedriver 147 on PATH gave a warning that is worth knowing by heart, because it explains many broken builds:</p>
{shell('An old driver on PATH', 'selenium-manager --browser chrome --offline --debug', out="""
[DEBUG] Found chromedriver 147.0.7727.24 in PATH: /opt/drivers/chromedriver
[DEBUG] Detected browser: chrome 153.0.8010.12
[WARN ] The chromedriver version (147.0.7727.24) detected in PATH at /opt/drivers/chromedriver might not be compatible with the detected chrome version (153.0.8010.12) ... so it is advised to delete the driver in PATH and retry
[INFO ] Driver path: /opt/drivers/chromedriver""", cap='Recorded with selenium-manager 0.4.51 on Linux (timestamps removed, folder names and one line shortened)')}
{MISMATCH}
{note('If you pass a driver path yourself, Selenium trusts you and never calls Selenium Manager. The documentation says that with Selenium 4.6 or newer you should not need to set a driver location at all. Delete old drivers from PATH and let Selenium Manager do the job.', 'warn')}
<h3>Configuring it</h3>
<p>Most people never configure Selenium Manager. When you must, for example behind a company proxy, there are three places, and the first one found wins:</p>
{flow(('Command line arguments', 'What the binding passes, built from your browser options, such as --browser-version.'), ('se-config.toml', 'A file in the cache folder, for example proxy = "myproxy:8080".'), ('Environment variables', 'The same key in capitals with SE_ in front, for example SE_PROXY or SE_OFFLINE.'))}
{table(['Setting', 'Default', 'What it does'], [
    ['<code>cache-path</code>', '<code>~/.cache/selenium</code>', 'Where drivers, browsers and metadata are stored'],
    ['<code>ttl</code>', '3600 seconds', 'How long resolved versions are trusted before asking the vendor again'],
    ['<code>offline</code>', 'false', 'No network requests or downloads at all'],
    ['<code>avoid-stats</code>', 'false', 'Selenium Manager sends anonymous usage numbers to Plausible once a day. Set SE_AVOID_STATS=true to stop it.'],
    ['<code>proxy</code>', 'none', 'An HTTP proxy for the downloads']])}
{deep('Why Rust and why a separate program', '<p>The same driver logic is needed by five bindings. Writing it once as a separate program, compiled for each operating system, means Java, Python, JavaScript, C# and Ruby all behave the same way, and a fix lands in every language at once. Selenium Manager versions mirror Selenium: Selenium 4.51.0 ships Selenium Manager 0.4.51.</p>')}
''', kw=['selenium manager', 'driver management', 'chromedriver', 'evergreen', 'session not created', 'cache', 'se-config.toml', 'SE_OFFLINE', 'chrome for testing', 'browserVersion', 'PATH'])

K.lesson('eight', 'The eight steps of a first script', f'''
<p>The documentation says that almost everything Selenium does is one of two things: send the browser a command, or ask it for information. A first script uses eight basic components, and you will recognise them in every test you ever read.</p>
{table(['Step', 'What it means', 'In this example'], [
    ['1. Start the session', 'Create a driver. A browser opens.', 'Chrome'],
    ['2. Take action on the browser', 'Navigate, go back, resize and so on.', 'Open the web form'],
    ['3. Request browser information', 'Title, address, window handles, cookies.', 'Read the title'],
    ['4. Establish a waiting strategy', 'Make sure an element is present before you look for it.', 'Implicit wait of 500 ms'],
    ['5. Find an element', 'Most commands are about elements.', 'The text box and the button'],
    ['6. Take action on an element', 'Type, click, clear.', 'Type Selenium, click Submit'],
    ['7. Request element information', 'Text, attributes, size, state.', 'Read the message'],
    ['8. End the session', 'Quit the driver and close the browser.', 'quit']])}
{EIGHT}
<p>Press <b>Explain line by line</b> and step through it. Notice that the code for steps 5 and 6 is the same idea in all three languages, only the spelling changes: <code>findElement</code> in Java and JavaScript, <code>find_element</code> in Python. Python measures waits in seconds, Java uses a Duration, and JavaScript uses milliseconds.</p>
{note('The documentation itself warns that an implicit wait is rarely the best solution. It is used here because it is the easiest to show. Chapter 4.1 replaces it with explicit waits.', 'warn')}
<h3>Try it yourself</h3>
<p>The box below is a practice browser that runs inside this page. It does not use real Selenium, but it understands the same lines in all three languages and shows the W3C request that each line would send. Run it one line at a time, then change <code>"Selenium"</code> to your own name and run it again.</p>
<div class="sp" data-sp="first"></div>
''', kw=['first script', 'eight components', 'start session', 'navigate', 'title', 'implicit wait', 'find element', 'send keys', 'click', 'get text', 'quit', 'playground'])

K.lesson('tidy', 'Always end the session', f'''
<p>Step 8 is the one beginners forget. The documentation explains that quit ends the driver process, which by default closes the browser too, and that no more commands can be sent to that driver afterwards. If a test fails before it reaches quit, the browser and the driver keep running. Run a thousand failing tests and you have a thousand Chrome windows eating the memory of the build machine.</p>
<p>The fix is to put quit where it always runs: in a <code>finally</code> block, or in Python inside a <code>with</code> block, which quits for you.</p>
{TIDY}
{table(['', 'quit', 'close'], [
    ['Closes', 'Every window and tab of the session', 'Only the current window or tab'],
    ['Driver process', 'Stopped', 'Keeps running while other windows are open'],
    ['After it', 'The driver object cannot be used again', 'Switch to another window to carry on']])}
{note('In a test framework the setup and teardown hooks do this job: start the driver before each test and quit it after each test, pass or fail. Chapter 5.1 shows the hooks in JUnit 5, pytest and Mocha.', 'tip')}
{ladder(
    '<p>Open the browser, do your steps, close the browser. Close it even if something goes wrong.</p>',
    '<p>Wrap your steps in try and finally, or use Python with. quit sends Delete Session, the driver closes the browser, and the binding stops the driver process.</p>',
    '<p>Driver processes and browser profiles are operating system resources. A suite that leaks them slows down and then fails with port or memory errors far from the real cause. One driver per test with guaranteed teardown keeps every test independent.</p>',
    '<p>The binding owns the driver process through a Service object. quit both ends the W3C session and stops the service. A remote session on a Grid has no local service, so there quit only ends the session and the Grid frees the slot. Chapter 6.1 covers session timeouts that clean up after clients that never quit.</p>')}
''', kw=['quit', 'close', 'finally', 'with statement', 'context manager', 'teardown', 'resource leak', 'service'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Which command installs Selenium for JavaScript?', ['npm install selenium', 'npm install selenium-webdriver', 'pip install selenium-webdriver', 'npm install webdriver-manager'], 1,
       'The package name has two words.', 'The JavaScript package is selenium-webdriver.')
K.quiz('e', 'Since which Selenium version does Selenium Manager ship with every release?', ['4.0', '4.6', '4.11', '3.141'], 1,
       'It came after Selenium 4.0.', 'The documentation says Selenium Manager is shipped out of the box with each release as of version 4.6.')
K.quiz('e', 'Where does Selenium Manager cache drivers by default?', ['/tmp', 'The project folder', '~/.cache/selenium', 'The Windows folder'], 2,
       'A hidden folder in your home directory.', 'The default cache path is ~/.cache/selenium.')
K.quiz('e', 'Which step of a first script is most often forgotten and leaves browsers running?', ['Start the session', 'Find an element', 'End the session with quit', 'Request the title'], 2,
       'The last one.', 'Without quit the driver and browser keep running. Put it in finally or a with block.')
K.quiz('m', 'Chrome updates itself from 113 to 115 while chromedriver 113 is on PATH, and you passed nothing else. What error do you get?', ['no such element', 'session not created: This version of ChromeDriver only supports Chrome version 113', 'timeout', 'stale element reference'], 1,
       'The browser and driver do not match.', 'The driver refuses to start a session for a browser version it does not support. This is the example in the Selenium Manager documentation.')
K.quiz('m', 'You pass the path of a chromedriver yourself through a Service. When does Selenium Manager run?', ['Always first', 'Never, because a driver was given', 'Only on Windows', 'After the session starts'], 1,
       'It is only a fallback.', 'Selenium Manager only operates as a fallback, when no driver is provided.')
K.quiz('m', 'In Python, driver.implicitly_wait(0.5) waits up to how long?', ['0.5 milliseconds', '0.5 seconds', '5 seconds', '500 seconds'], 1,
       'Python times are in seconds.', 'Python takes seconds, so 0.5 is half a second. Java uses Duration.ofMillis(500) and JavaScript uses implicit: 500.')
K.quiz('m', 'Which order of preference does Selenium Manager use for its configuration?', ['Environment, file, command line', 'Command line, se-config.toml, environment variables', 'File, command line, environment', 'Only environment variables'], 1,
       'The most specific wins.', 'Command line arguments first, then the configuration file, then SE_ environment variables.')
K.quiz('h', 'What is the difference between quit and close?', ['None', 'close ends the session and quit closes one tab', 'quit closes every window and ends the session, close only closes the current window', 'quit only works on Grid'], 2,
       'One of them stops the driver.', 'close closes the current window. quit closes them all, ends the session and stops the driver process.')
K.quiz('x', 'Since 4.11, what does Selenium Manager do when browserVersion is set to 114 and Chrome 114 is not installed?', ['It fails', 'It uses the installed Chrome anyway', 'It downloads Chrome for Testing 114 into the cache and a matching chromedriver', 'It installs Chrome system wide'], 2,
       'Automated browser management.', 'It discovers, downloads and caches Chrome for Testing 114, and manages the matching driver too.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Selenium Manager trusts resolved versions for its TTL of 3600 seconds. How many hours is that?', '1', 'Divide by 3600 seconds per hour.',
       ['The TTL is given in seconds: 3600.', 'There are 60 × 60 = 3,600 seconds in an hour.', eq('3600 ÷ 3600 = 1 hour')], check=1)
K.calc('e', 'An implicit wait is set to 500 ms. The element appears after 300 ms. About how long does find_element take?', '300', 'It returns as soon as the element is there.',
       ['The implicit wait is the most it will wait, not a fixed delay.', 'The driver keeps looking and finds the element at 300 ms.', eq('About 300 ms')], check=300, unit='ms')
K.calc('m', 'Downloading chromedriver takes 4 seconds the first time. A suite starts 50 sessions. With the cache, how many seconds of download time does the suite spend in total?', '4', 'Only the first one downloads.',
       ['Session 1: not cached, download 4 s.', 'Sessions 2 to 50: the driver is in ~/.cache/selenium.', eq('4 + 49 × 0 = 4 seconds')], check=4)
K.calc('m', 'A failing test leaves its browser open. Each leftover Chrome uses 300 MB. After 40 failing tests, how many GB are wasted? (1 GB = 1000 MB)', '12', 'Multiply, then convert.',
       ['Each failing test leaves one Chrome of 300 MB.', '40 × 300 = 12,000 MB.', eq('12,000 ÷ 1000 = 12 GB')], check=12, unit='GB')
K.calc('h', 'Python waits in seconds, Java in Duration and JavaScript in milliseconds. A Python test uses implicitly_wait(2.5). What number goes in JavaScript setTimeouts({implicit: ?})', '2500', 'Seconds to milliseconds.',
       ['Python reads 2.5 as seconds.', 'JavaScript wants milliseconds, and 1 second = 1000 ms.', eq('2.5 × 1000 = 2500 ms')], check=2500)
K.calc('x', 'A team has 3 browsers and drivers to keep in step. Chrome updates every 4 weeks. Over a 52 week year, how many manual chromedriver updates does Selenium Manager save, if each Chrome update needed one?', '13', 'Updates per year.',
       ['A year has 52 weeks.', 'One Chrome update every 4 weeks means 52 ÷ 4 updates.', eq('52 ÷ 4 = 13 updates a year, each a chance of a broken suite')], check=13)

# ---------------------------------------------------------------- assignments
K.assign('envkey', 'e', 'Turn a configuration key into its environment variable',
         '<p>Write <code>env_name(key)</code>. The documentation says each Selenium Manager key becomes an environment variable by turning it to capitals, replacing every dash with an underscore and adding the prefix <code>SE_</code>. So <code>browser-version</code> becomes <code>SE_BROWSER_VERSION</code>.</p>',
         '''
def env_name(key):
    # your code here
    pass
''', [('env_name("browser-version")', 'SE_BROWSER_VERSION'), ('env_name("offline")', 'SE_OFFLINE'), ('env_name("avoid-stats")', 'SE_AVOID_STATS'), ('env_name("skip-driver-in-path")', 'SE_SKIP_DRIVER_IN_PATH')],
         '''
def env_name(key):
    return "SE_" + key.upper().replace("-", "_")
''', 'upper() and replace() do all the work.', '<p>The order of upper and replace does not matter here because a dash has no capital form.</p>')
K.assign('pick', 'm', 'Which setting wins?',
         '<p>Write <code>setting(cli, toml, env)</code>. Each argument is the value from that place, or <code>None</code> if it was not set there. Return the value Selenium Manager uses: command line first, then the configuration file, then the environment variable. If none is set, return <code>None</code>.</p>',
         '''
def setting(cli, toml, env):
    # your code here
    pass
''', [('setting("120", "118", "117")', '120'), ('setting(None, "118", "117")', '118'), ('setting(None, None, "117")', '117'), ('setting(None, None, None)', None)],
         '''
def setting(cli, toml, env):
    for value in (cli, toml, env):
        if value is not None:
            return value
    return None
''', 'Check the three places in order and return the first one that is set.', '<p>Testing <code>is not None</code> matters: a value such as an empty string or 0 counts as set.</p>')

K.must('Install', 'Java: selenium-java with Maven or Gradle (Java 11+). Python: pip install selenium (3.10+). JavaScript: npm install selenium-webdriver (Node 22+).')
K.must('Selenium Manager', 'Ships with Selenium since 4.6. A fallback that discovers the browser version, resolves, downloads and caches the driver in ~/.cache/selenium, and since 4.11 can download browsers.')
K.must('Driver mismatch', 'An old driver on PATH or given by hand gives session not created. Delete it and let Selenium Manager match the driver.')
K.must('Eight components', 'Start session, act on browser, ask the browser, wait strategy, find element, act on element, ask the element, end session.')
K.must('Always quit', 'Put quit in finally, or use a Python with block. quit closes every window and stops the driver, close only closes one window.')

T = K.topic(
    slug='setup-first-script', topic='setup-first-script',
    step=(1, 'Meet Selenium', 'se-meet', 'What Selenium is, how it talks to a browser through the W3C WebDriver protocol, and your first script in Java, Python and JavaScript.', 'Beginner'),
    title='Setup, Selenium Manager and your first script', short='Setup and first script', badge='1.3', minutes=45, added='2026-10-29',
    lead='Install Selenium in Java, Python or JavaScript, watch Selenium Manager find the right driver, and write the eight steps every Selenium script is made of.',
    desc='Installing Selenium with Maven, pip and npm, minimum versions, Selenium Manager and its four steps, browser management, the cache, configuration order, a real driver mismatch error, the eight basic components of a script in three languages, a practice browser, and quit versus close.',
    summary='Install Selenium, let Selenium Manager match the driver, and write and tidy up your first real script.',
    keywords=['setup', 'install', 'selenium manager', 'first script', 'eight components', 'quit', 'close', 'chromedriver'],
    recap='<p>Add the Selenium library with your build tool, keep a browser installed and let Selenium Manager find, download and cache the matching driver. Every script follows eight steps from starting a session to quitting it, and quit belongs in a finally or with block so it always runs.</p>')
