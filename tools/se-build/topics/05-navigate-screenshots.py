# Chapter 2.2: navigation, browser information, window size and position, screenshots and printing to PDF.
# Sources: selenium.dev documentation (Browser interactions, Browser navigation, Working with windows and tabs:
# window management, TakeScreenshot, TakeElementScreenshot, Print Page), the W3C WebDriver specification
# (Navigate To, Back, Forward, Refresh, Get and Set Window Rect, Take Screenshot, Print Page) and real runs.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, src, flow

K = Kit()

NAV = tri('nav', 'Go somewhere, go back, go forward, reload', java=r'''
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class Navigate {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        driver.get("https://www.selenium.dev/selenium/web/web-form.html");  ## Navigate To. The short form of driver.navigate().to(...).
        System.out.println("1 " + driver.getTitle());
        driver.navigate().to("https://www.selenium.dev/selenium/web/xhtmlTest.html");  ## The long form does the same thing.
        System.out.println("2 " + driver.getTitle() + " at " + driver.getCurrentUrl());  ## Title and address of the page now showing.
        driver.navigate().back();  ## Press the Back button.
        System.out.println("3 " + driver.getTitle());
        driver.navigate().forward();  ## Press the Forward button.
        System.out.println("4 " + driver.getTitle());
        driver.navigate().refresh();  ## Reload the current page.
        System.out.println("5 " + driver.getTitle());
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/web-form.html")  ## Navigate To. Waits for the page load strategy.
print("1", driver.title)
driver.get("https://www.selenium.dev/selenium/web/xhtmlTest.html")  ## A second page. History now holds two entries.
print("2", driver.title, "at", driver.current_url)  ## Title and address of the page now showing.
driver.back()  ## Press the Back button.
print("3", driver.title)
driver.forward()  ## Press the Forward button.
print("4", driver.title)
driver.refresh()  ## Reload the current page.
print("5", driver.title)
driver.quit()
''', js=r'''
const { Builder, Browser } = require('selenium-webdriver');

(async function navigate() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.get('https://www.selenium.dev/selenium/web/web-form.html');  ## Navigate To. Waits for the page load strategy.
  console.log('1 ' + await driver.getTitle());
  await driver.navigate().to('https://www.selenium.dev/selenium/web/xhtmlTest.html');  ## The long form of get.
  console.log('2 ' + await driver.getTitle() + ' at ' + await driver.getCurrentUrl());
  await driver.navigate().back();  ## Press the Back button.
  console.log('3 ' + await driver.getTitle());
  await driver.navigate().forward();  ## Press the Forward button.
  console.log('4 ' + await driver.getTitle());
  await driver.navigate().refresh();  ## Reload the current page.
  console.log('5 ' + await driver.getTitle());
  await driver.quit();
})();
''', expect='5 XHTML Test Page')

WIN = tri('window', 'Set the window size and position, then read them back', java=r'''
import org.openqa.selenium.Dimension;
import org.openqa.selenium.Point;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class WindowRect {
    public static void main(String[] args) {
        WebDriver driver = new ChromeDriver();
        WebDriver.Window window = driver.manage().window();  ## Every window command lives under manage().window().
        window.setSize(new Dimension(1024, 768));  ## Restore the window and make it 1024 by 768 pixels.
        window.setPosition(new Point(40, 30));  ## Move its top left corner to x 40, y 30 on the screen.
        Dimension size = window.getSize();  ## Ask the browser for the size it really has.
        Point where = window.getPosition();
        System.out.println("size " + size.getWidth() + " x " + size.getHeight());
        System.out.println("position " + where.getX() + ", " + where.getY());
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver

driver = webdriver.Chrome()
driver.set_window_size(1024, 768)  ## Restore the window and make it 1024 by 768 pixels.
driver.set_window_position(40, 30)  ## Move its top left corner to x 40, y 30 on the screen.
size = driver.get_window_size()  ## A dict with width and height.
where = driver.get_window_position()  ## A dict with x and y.
print("size", size["width"], "x", size["height"])
print("position", str(where["x"]) + ",", where["y"])
print("rect", driver.get_window_rect())  ## One W3C command, Get Window Rect, returns all four numbers at once.
driver.quit()
''', js=r'''
const { Builder, Browser } = require('selenium-webdriver');

(async function windowRect() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  const window = driver.manage().window();  ## Window commands live under manage().window().
  await window.setRect({ width: 1024, height: 768, x: 40, y: 30 });  ## JavaScript sets size and position in one call to Set Window Rect.
  const { width, height, x, y } = await window.getRect();  ## Get Window Rect returns all four numbers.
  console.log('size ' + width + ' x ' + height);
  console.log('position ' + x + ', ' + y);
  await driver.quit();
})();
''', expect='size 1024 x 768')

SHOT = tri('shots', 'Save a screenshot of the page and of one element', java=r'''
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import org.openqa.selenium.By;
import org.openqa.selenium.Dimension;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

public class Screenshots {
    public static void main(String[] args) throws Exception {
        WebDriver driver = new ChromeDriver();
        driver.manage().window().setSize(new Dimension(1024, 768));
        driver.get("https://www.selenium.dev/selenium/web/web-form.html");
        File page = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);  ## Take Screenshot of the viewport. Selenium writes a temporary PNG file.
        Files.copy(page.toPath(), Path.of("page.png"));  ## Copy it somewhere you will find it.
        WebElement button = driver.findElement(By.cssSelector("button"));
        File only = button.getScreenshotAs(OutputType.FILE);  ## Take Element Screenshot: just the area of the button.
        Files.copy(only.toPath(), Path.of("button.png"));
        for (String name : new String[] {"page.png", "button.png"}) {
            BufferedImage img = ImageIO.read(new File(name));  ## Open the PNG to read its size in pixels.
            System.out.println(name + ": " + img.getWidth() + " x " + img.getHeight());
        }
        driver.quit();
    }
}
''', py=r'''
import struct

from selenium import webdriver
from selenium.webdriver.common.by import By

def png_size(path):  ## A PNG keeps its width and height at bytes 16 to 24 of the file.
    with open(path, "rb") as f:
        return struct.unpack(">II", f.read(24)[16:24])

driver = webdriver.Chrome()
driver.set_window_size(1024, 768)
driver.get("https://www.selenium.dev/selenium/web/web-form.html")
driver.save_screenshot("page.png")  ## Take Screenshot of the viewport and save it as a PNG.
button = driver.find_element(By.CSS_SELECTOR, "button")
button.screenshot("button.png")  ## Take Element Screenshot: just the area of the button.
for name in ("page.png", "button.png"):
    w, h = png_size(name)
    print(f"{name}: {w} x {h}")
driver.quit()
''', js=r'''
const fs = require('fs');
const { Builder, Browser, By } = require('selenium-webdriver');

const pngSize = file => { const b = fs.readFileSync(file); return [b.readUInt32BE(16), b.readUInt32BE(20)]; };  ## A PNG keeps width and height at bytes 16 and 20.

(async function screenshots() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();
  await driver.manage().window().setRect({ width: 1024, height: 768 });
  await driver.get('https://www.selenium.dev/selenium/web/web-form.html');
  const page = await driver.takeScreenshot();  ## Take Screenshot answers with the PNG as base64 text.
  fs.writeFileSync('page.png', page, 'base64');  ## Decode the base64 and write the bytes to a file.
  const button = await driver.findElement(By.css('button'));
  fs.writeFileSync('button.png', await button.takeScreenshot(), 'base64');  ## Take Element Screenshot: just the area of the button.
  for (const name of ['page.png', 'button.png']) {
    const [w, h] = pngSize(name);
    console.log(`${name}: ${w} x ${h}`);
  }
  await driver.quit();
})();
''', expect='button.png:')

PDF = tri('printpdf', 'Print the page to a PDF file', java=r'''
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Base64;
import org.openqa.selenium.Pdf;
import org.openqa.selenium.PrintsPage;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.print.PrintOptions;

public class PrintPdf {
    public static void main(String[] args) throws Exception {
        ChromeOptions options = new ChromeOptions().addArguments("--headless=new");  ## Chromium prints to PDF only in headless mode.
        ChromeDriver driver = new ChromeDriver(options);
        driver.get("https://www.selenium.dev/selenium/web/web-form.html");
        PrintOptions print = new PrintOptions();  ## Paper settings: orientation, page ranges, size, margins, scale, background.
        print.setOrientation(PrintOptions.Orientation.LANDSCAPE);
        Pdf pdf = ((PrintsPage) driver).print(print);  ## The W3C Print Page command. The PDF comes back as base64 text.
        byte[] bytes = Base64.getDecoder().decode(pdf.getContent());  ## Decode it to the real bytes.
        Files.write(Path.of("page.pdf"), bytes);
        System.out.println("page.pdf starts with " + new String(bytes, 0, 5));  ## Every PDF file starts with %PDF-.
        driver.quit();
    }
}
''', py=r'''
import base64

from selenium import webdriver
from selenium.webdriver.common.print_page_options import PrintOptions

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  ## Chromium prints to PDF only in headless mode.
driver = webdriver.Chrome(options=options)
driver.get("https://www.selenium.dev/selenium/web/web-form.html")
print_options = PrintOptions()  ## Paper settings: orientation, page ranges, size, margins, scale, background.
print_options.orientation = "landscape"
pdf = base64.b64decode(driver.print_page(print_options))  ## The W3C Print Page command answers with base64, so decode it.
with open("page.pdf", "wb") as f:
    f.write(pdf)
print("page.pdf starts with", pdf[:5].decode())  ## Every PDF file starts with %PDF-.
driver.quit()
''', js=r'''
const fs = require('fs');
const { Builder, Browser } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');

(async function printPdf() {
  const options = new chrome.Options().addArguments('--headless=new');  ## Chromium prints to PDF only in headless mode.
  const driver = await new Builder().forBrowser(Browser.CHROME).setChromeOptions(options).build();
  await driver.get('https://www.selenium.dev/selenium/web/web-form.html');
  const base64 = await driver.printPage({ orientation: 'landscape' });  ## The W3C Print Page command answers with base64 text.
  const pdf = Buffer.from(base64, 'base64');  ## Decode it to the real bytes.
  fs.writeFileSync('page.pdf', pdf);
  console.log('page.pdf starts with ' + pdf.subarray(0, 5).toString());  ## Every PDF file starts with %PDF-.
  await driver.quit();
})();
''', expect='%PDF-')

K.lesson('navigate', 'Navigate and ask where you are', f'''
<p>Four commands move a tab around, and they match the buttons a person uses: the address bar, Back, Forward and Reload. Two more questions tell you where you ended up: the title and the current URL.</p>
{table(['What you want', 'Java', 'Python', 'JavaScript'], [
    ['Open an address', '<code>driver.get(url)</code> or <code>navigate().to(url)</code>', '<code>driver.get(url)</code>', '<code>driver.get(url)</code> or <code>navigate().to(url)</code>'],
    ['Back', '<code>navigate().back()</code>', '<code>driver.back()</code>', '<code>navigate().back()</code>'],
    ['Forward', '<code>navigate().forward()</code>', '<code>driver.forward()</code>', '<code>navigate().forward()</code>'],
    ['Reload', '<code>navigate().refresh()</code>', '<code>driver.refresh()</code>', '<code>navigate().refresh()</code>'],
    ['Page title', '<code>getTitle()</code>', '<code>driver.title</code>', '<code>getTitle()</code>'],
    ['Current address', '<code>getCurrentUrl()</code>', '<code>driver.current_url</code>', '<code>getCurrentUrl()</code>']])}
{NAV}
{viz('se-history')}
<p>History works the way it does for a person. A new <code>get</code> after going back throws away the pages that were ahead. Back on the first page does nothing at all, and raises no error, so a test that needs to know where it is should check the title or the URL.</p>
{scene('a login redirect', '<p>A test opens the account page of a shop. The shop is not logged in, so it redirects to the login page. The test checks <code>current_url</code> and sees <code>/login?next=/account</code>. After logging in it expects to land back on <code>/account</code>. Reading the address after each step is how the test proves the redirect works.</p>')}
{note('After refresh or any navigation, the elements you found before belong to the old page. Using them raises stale element reference. Find them again on the new page. Chapter 5.4 covers this error in depth.', 'warn')}
''', kw=['navigate', 'get', 'navigate to', 'back', 'forward', 'refresh', 'title', 'current url', 'history', 'redirect'])

K.lesson('windowsize', 'Window size and position', f'''
<p>A page can look different at different sizes. A menu turns into a hamburger button on a narrow screen, and a table hides columns. The documentation reminds us that screen resolution can change how your application renders, so WebDriver lets you set the size and position of the window.</p>
{WIN}
{table(['Command', 'What it does'], [
    ['Set window size', 'Restores the window if it was maximised, then sets width and height in pixels'],
    ['Set window position', 'Moves the top left corner to x and y on the screen'],
    ['Get window rect', 'Width, height, x and y in one answer'],
    ['Maximize', 'Makes the window fill the screen, without covering the system menus'],
    ['Minimize', 'Hides the window, usually to the taskbar. The exact result depends on the window manager. Selenium 4 and later.'],
    ['Fullscreen', 'Fills the whole screen, like pressing F11']])}
{note('Maximize and minimize need a desktop window manager. On a bare Linux build server they can fail with an unknown error, which is what happened when this page was built. Setting an exact size with Set Window Rect or the --window-size switch works everywhere and gives the same layout on every machine.', 'warn')}
{scene('testing the mobile menu', '<p>A news site shows a full menu above 768 pixels and a hamburger button below. One test sets the window to 1280 by 800 and checks the full menu. Another sets it to 375 by 800 and checks that the hamburger opens the menu. Same page, two layouts, two sizes.</p>')}
''', kw=['window size', 'window position', 'window rect', 'maximize', 'minimize', 'fullscreen', 'responsive', 'Dimension', 'Point'])

K.lesson('screenshots', 'Screenshots', f'''
<p>A screenshot is the most useful thing a failed test can leave behind. WebDriver has two commands: <b>Take Screenshot</b> for the visible part of the page and <b>Take Element Screenshot</b> for one element. Both return a PNG encoded as base64 text, and each binding gives you helpers to save it.</p>
{SHOT}
<p>The page screenshot is the size of the viewport, the part of the window that shows the page. Here it is 1024 by 625, smaller than the 1024 by 768 window, because the window also holds the tab strip and toolbar. The button screenshot is cut to the button.</p>
{table(['Language', 'Page screenshot to file', 'Element screenshot to file'], [
    ['Java', '<code>((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE)</code>', '<code>element.getScreenshotAs(OutputType.FILE)</code>'],
    ['Python', '<code>driver.save_screenshot("page.png")</code>', '<code>element.screenshot("el.png")</code>'],
    ['JavaScript', '<code>driver.takeScreenshot()</code> gives base64', '<code>element.takeScreenshot()</code> gives base64']])}
{note('Take a screenshot in the teardown of a failing test, before quit. Name the file after the test, so the report can link to it. Chapter 5.1 wires this into JUnit, pytest and Mocha.', 'tip')}
''', kw=['screenshot', 'take screenshot', 'element screenshot', 'png', 'base64', 'TakesScreenshot', 'save_screenshot', 'viewport'])

K.lesson('print', 'Print a page to PDF', f'''
<p>The W3C <b>Print Page</b> command turns the current page into a PDF. You describe the paper with PrintOptions and get the PDF back as base64. The documentation notes that Chromium browsers need headless mode for this.</p>
{PDF}
{table(['PrintOptions setting', 'Example'], [
    ['Orientation', 'portrait or landscape'],
    ['Page ranges', '"2-4"'],
    ['Page size', 'A4, Legal and others'],
    ['Margins', 'top, bottom, left, right'],
    ['Scale', '1.0 is 100 %, 0.25 is 25 %'],
    ['Background', 'whether background colours and images print'],
    ['Shrink to fit', 'whether wide content is shrunk to the page']])}
{scene('archiving invoices', '<p>An accounts team must keep a copy of every invoice page the system shows on the last day of each month. A scheduled Selenium job logs in, opens each invoice and prints it to PDF in landscape with backgrounds on. No person clicks Print a hundred times.</p>')}
{ladder(
    '<p>You can tell the browser where to go, ask where it is, change its size, take a picture and print the page, all from code.</p>',
    '<p>Each of these is one W3C command: Navigate To, Back, Forward, Refresh, Get Title, Get Current URL, Set Window Rect, Take Screenshot and Print Page. Images and PDFs travel as base64 text inside the JSON answer.</p>',
    '<p>Navigation commands wait according to the page load strategy, but history and refresh can change the page under any element references you hold. Screenshots show the viewport only, so full page captures need a browser specific feature, such as Firefox full page screenshots.</p>',
    '<p>WebDriver BiDi adds a browsingContext module with navigate, print and captureScreenshot commands that can also report navigation events as they happen. Chapter 6.2 introduces BiDi.</p>')}
''', kw=['print page', 'pdf', 'PrintOptions', 'headless', 'orientation', 'landscape', 'base64', 'archive'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Which Python call presses the browser Back button?', ['driver.navigate().back()', 'driver.back()', 'driver.history(-1)', 'driver.go_back()'], 1,
       'Python keeps it short.', 'Python has driver.back(). Java and JavaScript use navigate().back().')
K.quiz('e', 'What does driver.current_url (getCurrentUrl) return?', ['The first URL of the session', 'The address the browser shows now', 'The URL of the driver', 'The page title'], 1,
       'Like reading the address bar.', 'It returns the address of the current page.')
K.quiz('e', 'In which format does Take Screenshot return the image inside the JSON answer?', ['A file path', 'Base64 encoded PNG', 'JPEG bytes', 'SVG'], 1,
       'JSON carries text.', 'The endpoint returns the screenshot encoded in base64.')
K.quiz('m', 'You go back from page B to A and then call get(C). What is ahead of C in history?', ['B', 'Nothing', 'A', 'B and A'], 1,
       'A new navigation cuts the forward pages.', 'A new navigation drops the pages that were ahead, just like in a normal browser.')
K.quiz('m', 'You call back() on the first page of the session. What happens?', ['NoSuchWindowException', 'The browser closes', 'Nothing, no error', 'The session ends'], 2,
       'Like clicking a greyed out Back button.', 'With nothing behind, Back has no effect and no error is raised.')
K.quiz('m', 'What does Set Window Size do to a maximised window?', ['Nothing', 'Restores it, then sets the size', 'Raises an error', 'Makes it fullscreen'], 1,
       'The documentation says it in the heading.', 'Set window size restores the window and sets the size.')
K.quiz('m', 'Which mode do Chromium browsers need for Print Page?', ['Incognito', 'Headless', 'Kiosk', 'Any'], 1,
       'See the note in the documentation.', 'The documentation says Print Page requires Chromium browsers to be in headless mode.')
K.quiz('h', 'You found a button, then called refresh(), then clicked the old button object. What happens?', ['The click works', 'stale element reference error', 'no such window', 'The page refreshes again'], 1,
       'The old page is gone.', 'Refresh builds a new document, so references to elements of the old one are stale.')
K.quiz('h', 'Why is a page screenshot smaller than the window size you set?', ['Compression', 'It only covers the viewport, not the browser toolbar and borders', 'Selenium crops 10 %', 'It is not smaller'], 1,
       'What part of the window shows the page?', 'Take Screenshot captures the viewport. The window also contains the toolbar and frame.')
K.quiz('x', 'A CI server has no window manager and maximize fails. What is the most portable way to get a fixed layout?', ['Retry maximize', 'Set an exact window size with Set Window Rect or --window-size', 'Use fullscreen', 'Zoom the page with CSS'], 1,
       'Exact numbers are reproducible.', 'An exact size works without a window manager and gives every machine the same layout.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A base64 string of a screenshot has 4,000 characters. Base64 turns every 3 bytes into 4 characters. About how many bytes is the PNG?', '3000', 'Multiply by 3/4.',
       ['Every 4 characters hold 3 bytes.', '4,000 ÷ 4 = 1,000 groups.', eq('1,000 × 3 = 3,000 bytes')], check=3000)
K.calc('e', 'A window is 1024 by 768 and the browser toolbar and frame take 143 pixels of height, as in the real run on this page. How tall is the screenshot?', '625', 'Subtract the toolbar.',
       ['The window height includes the browser chrome.', 'The viewport is what remains.', eq('768 − 143 = 625 pixels, the height the real screenshot had')], check=625)
K.calc('m', 'You visit A, B, C, go back twice, then get D. How many pages are in the history now?', '2', 'Back twice lands on A, then D cuts the rest.',
       ['After A, B, C the pointer is on C.', 'Back twice: the pointer is on A, with B and C ahead.', eq('get D drops B and C, so history is A, D: 2 pages')], check=2)
K.calc('m', 'A test takes a 300 KB screenshot only when it fails. 2,000 tests run and 3 % fail. How many MB of screenshots? (1 MB = 1000 KB)', '18', 'Failures times size.',
       ['3 % of 2,000 = 60 failures.', '60 × 300 KB = 18,000 KB.', eq('18,000 ÷ 1000 = 18 MB')], check=18)
K.calc('h', 'The same suite takes a screenshot after every test instead. How many times more storage than in the previous problem?', '33.33', 'Compare 2,000 with 60.',
       ['Every test: 2,000 screenshots.', 'Failures only: 60 screenshots.', eq('2,000 ÷ 60 ≈ 33.3 times more')], check=33.33, tol=0.1)
K.calc('x', 'You test 4 window widths on 3 browsers, and each check takes 5 seconds including the resize. How many seconds for one page?', '60', 'Every width on every browser.',
       ['Combinations: 4 widths × 3 browsers = 12.', 'Each takes 5 seconds.', eq('12 × 5 = 60 seconds')], check=60)

# ---------------------------------------------------------------- assignments
K.assign('history', 'm', 'Simulate the history of a tab',
         '<p>Write <code>showing(actions)</code>. <code>actions</code> is a list such as <code>["get A", "get B", "back"]</code>. get opens a page and drops any pages ahead. back and forward move one page if they can and do nothing otherwise. refresh changes nothing. Return the page showing at the end.</p>',
         '''
def showing(actions):
    # your code here
    pass
''', [('showing(["get A", "get B", "back"])', 'A'), ('showing(["get A", "back", "back"])', 'A'), ('showing(["get A", "get B", "back", "get C", "forward"])', 'C'), ('showing(["get A", "get B", "back", "forward", "refresh"])', 'B')],
         '''
def showing(actions):
    history, at = [], -1
    for action in actions:
        parts = action.split()
        if parts[0] == "get":
            history = history[:at + 1] + [parts[1]]
            at = len(history) - 1
        elif parts[0] == "back" and at > 0:
            at -= 1
        elif parts[0] == "forward" and at < len(history) - 1:
            at += 1
    return history[at]
''', 'Keep a list and an index. get cuts the list after the index before adding.', '<p>The slice <code>history[:at + 1]</code> is the step people forget. It is what makes forward do nothing after a new get.</p>')
K.assign('pngsize', 'e', 'Read the size of a PNG',
         '<p>Write <code>png_size(data)</code>. <code>data</code> is the bytes of a PNG file. Width is the 4 byte big endian number at bytes 16 to 19 and height is at bytes 20 to 23. Return <code>(width, height)</code>.</p>',
         '''
def png_size(data):
    # your code here
    pass
''', [('png_size(bytes(16) + (1024).to_bytes(4, "big") + (625).to_bytes(4, "big"))', (1024, 625)), ('png_size(bytes(16) + (79).to_bytes(4, "big") + (38).to_bytes(4, "big"))', (79, 38))],
         '''
def png_size(data):
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    return (width, height)
''', 'int.from_bytes with "big" reads a big endian number.', '<p>The PNG format stores width and height in its first chunk, IHDR, right after the 8 byte signature and the chunk length and type. That is why the same offsets work for every PNG.</p>')

K.must('Navigation', 'get or navigate().to, back, forward, refresh. Python spells them driver.back(), driver.forward(), driver.refresh().')
K.must('Where am I', 'Title and current URL. Check them when a test depends on a redirect or on history, because back on the first page raises no error.')
K.must('Window rect', 'Set and get size and position. An exact size is more portable than maximize, which needs a window manager.')
K.must('Screenshots', 'Take Screenshot (viewport) and Take Element Screenshot return base64 PNG. Save one when a test fails, before quit.')
K.must('Print Page', 'Returns a base64 PDF. Use PrintOptions for orientation, ranges, size, margins and scale. Chromium needs headless.')

T = K.topic(
    slug='navigate-screenshots', topic='navigate-screenshots',
    step=(2, 'Control the browser', 'se-browser', 'Options, capabilities, page load strategy, timeouts, the driver service, navigation, windows and screenshots.', 'Beginner'),
    title='Navigation, window size, screenshots and PDF', short='Navigate and capture', badge='2.2', minutes=40, added='2026-10-29',
    lead='Move around like a person with the toolbar buttons, read where you are, size the window for each layout, and capture what the browser shows as PNG or PDF.',
    desc='Navigate To, Back, Forward and Refresh, title and current URL, how history works, window size and position with Set Window Rect, maximize and fullscreen, page and element screenshots, and printing to PDF with PrintOptions, run in Java, Python and JavaScript.',
    summary='Navigation and history, title and URL, window size and position, screenshots and printing pages to PDF.',
    keywords=['navigation', 'back', 'forward', 'refresh', 'title', 'current url', 'window size', 'screenshot', 'print', 'pdf'],
    recap='<p>get, back, forward and refresh move a tab the way the toolbar does, and title and current URL tell you where you are. Set Window Rect fixes the layout. Take Screenshot and Take Element Screenshot give base64 PNGs, and Print Page gives a base64 PDF.</p>')
