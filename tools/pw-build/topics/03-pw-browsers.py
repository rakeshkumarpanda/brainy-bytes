from pkit import part, say, quiz, calc, panel, four, one, js, ts, py, jv, shown, walk, step, table, tip, by, viz, figure

MODULE = ('🌐', 'Browser handling', 'pw-browser', 'Browsers, contexts, pages, devices and tabs, then navigation, frames, dialogs, downloads, uploads and events.')

EXEC_POM = '''<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.brainy</groupId>
  <artifactId>scripts</artifactId>
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
        <configuration><mainClass>com.brainy.Main</mainClass></configuration>
      </plugin>
    </plugins>
  </build>
</project>'''

MAIN = 'src/main/java/com/brainy/Main.java'
NO_INFO = [(r'(?m)^\[INFO\].*\n', '')]


def script(java, py_code, js_code, ts_code, label, result):
    """A plain script, not a test, in all four languages."""
    return four(label,
                java=jv({MAIN: java}, cmd='mvn -q compile exec:java', pom_xml=EXEC_POM, options=False, replace=NO_INFO),
                py=py({'main.py': py_code}, ini=None, cmd='python main.py'),
                js=js({'main.mjs': js_code}, config=None, cmd='node main.mjs'),
                ts=ts({'main.ts': ts_code}, cmd='node main.ts', shown_cmd='npx tsc -p . && node main.ts'),
                result=result)


LAUNCH_JS = '''import { chromium } from 'playwright';

const browser = await chromium.launch({
  headless: true,      // no window. Use false to watch it work
  slowMo: 100,         // wait 100 ms before every action
  args: ['--lang=en-GB'],
});
console.log('Browser type:', browser.browserType().name());
console.log('Version:', browser.version());
console.log('Connected:', browser.isConnected());
console.log('Contexts so far:', browser.contexts().length);
await browser.close();
console.log('Connected after close:', browser.isConnected());'''

LAUNCH_TS = LAUNCH_JS.replace("import { chromium } from 'playwright';", "import { chromium, type Browser } from 'playwright';").replace('const browser = await', 'const browser: Browser = await')

LAUNCH_PY = '''from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,      # no window. Use False to watch it work
        slow_mo=100,        # wait 100 ms before every action
        args=["--lang=en-GB"],
    )
    print("Browser type:", browser.browser_type.name)
    print("Version:", browser.version)
    print("Connected:", browser.is_connected())
    print("Contexts so far:", len(browser.contexts))
    browser.close()
    print("Connected after close:", browser.is_connected())'''

LAUNCH_JAVA = '''package com.brainy;

import com.microsoft.playwright.*;
import java.util.List;

public class Main {
  public static void main(String[] args) {
    try (Playwright playwright = Playwright.create()) {
      Browser browser = playwright.chromium().launch(new BrowserType.LaunchOptions()
          .setHeadless(true)          // no window. Use false to watch it work
          .setSlowMo(100)             // wait 100 ms before every action
          .setArgs(List.of("--lang=en-GB")));
      System.out.println("Browser type: " + browser.browserType().name());
      System.out.println("Version: " + browser.version());
      System.out.println("Connected: " + browser.isConnected());
      System.out.println("Contexts so far: " + browser.contexts().size());
      browser.close();
      System.out.println("Connected after close: " + browser.isConnected());
    }
  }
}'''

ISO_TS = '''import { test, expect } from '@playwright/test';

test('two shoppers in one browser', async ({ browser }) => {
  // Each context is a separate, empty browser profile.
  const ashaContext = await browser.newContext();
  const guestContext = await browser.newContext();
  const asha = await ashaContext.newPage();
  const guest = await guestContext.newPage();

  await asha.goto('/login');
  await asha.getByLabel('Email').fill('asha@shop.example');
  await asha.getByLabel('Password').fill('s3cret');
  await asha.getByRole('button', { name: 'Sign in' }).click();
  await expect(asha.getByText('Hello, Asha')).toBeVisible();

  await guest.goto('/products');
  await expect(guest.getByRole('link', { name: 'Sign in' })).toBeVisible();
  console.log('Asha cookies:', (await ashaContext.cookies()).length);
  console.log('Guest cookies:', (await guestContext.cookies()).length);

  await ashaContext.close();
  await guestContext.close();
});'''

ISO_PY = '''from playwright.sync_api import expect


def test_two_shoppers_in_one_browser(new_context):
    # Each context is a separate, empty browser profile.
    asha_context = new_context()
    guest_context = new_context()
    asha = asha_context.new_page()
    guest = guest_context.new_page()

    asha.goto("/login")
    asha.get_by_label("Email").fill("asha@shop.example")
    asha.get_by_label("Password").fill("s3cret")
    asha.get_by_role("button", name="Sign in").click()
    expect(asha.get_by_text("Hello, Asha")).to_be_visible()

    guest.goto("/products")
    expect(guest.get_by_role("link", name="Sign in")).to_be_visible()
    print("Asha cookies:", len(asha_context.cookies()))
    print("Guest cookies:", len(guest_context.cookies()))'''

ISO_JAVA = '''package com.brainy;

import com.microsoft.playwright.*;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class ContextTest {
  @Test
  void twoShoppersInOneBrowser(Browser browser) {
    // Each context is a separate, empty browser profile.
    BrowserContext ashaContext = browser.newContext();
    BrowserContext guestContext = browser.newContext();
    Page asha = ashaContext.newPage();
    Page guest = guestContext.newPage();

    asha.navigate("http://localhost:4173/login");
    asha.getByLabel("Email").fill("asha@shop.example");
    asha.getByLabel("Password").fill("s3cret");
    asha.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in")).click();
    assertThat(asha.getByText("Hello, Asha")).isVisible();

    guest.navigate("http://localhost:4173/products");
    assertThat(guest.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Sign in"))).isVisible();
    System.out.println("Asha cookies: " + ashaContext.cookies().size());
    System.out.println("Guest cookies: " + guestContext.cookies().size());

    ashaContext.close();
    guestContext.close();
  }
}'''

EMU_TS = '''import { test, expect } from '@playwright/test';

test.use({
  viewport: { width: 390, height: 844 },
  locale: 'de-DE',
  timezoneId: 'Asia/Kolkata',
  colorScheme: 'dark',
  hasTouch: true,
});

test('the shop sees a German phone user in India', async ({ page }) => {
  await page.goto('/about-you');
  for (const id of ['width', 'lang', 'tz', 'price', 'touch']) {
    console.log(id.padEnd(6), await page.locator('#' + id).textContent());
  }
  const dark = await page.evaluate(() => matchMedia('(prefers-color-scheme: dark)').matches);
  console.log('dark  ', dark);
  await expect(page.locator('#lang')).toHaveText('de-DE');
});'''

EMU_PY = '''import pytest
from playwright.sync_api import Page, expect


@pytest.mark.browser_context_args(
    viewport={"width": 390, "height": 844},
    locale="de-DE",
    timezone_id="Asia/Kolkata",
    color_scheme="dark",
    has_touch=True,
)
def test_the_shop_sees_a_german_phone_user_in_india(page: Page):
    page.goto("/about-you")
    for id in ["width", "lang", "tz", "price", "touch"]:
        print(id.ljust(6), page.locator("#" + id).text_content())
    dark = page.evaluate("matchMedia('(prefers-color-scheme: dark)').matches")
    print("dark  ", dark)
    expect(page.locator("#lang")).to_have_text("de-DE")'''

EMU_JAVA = '''package com.brainy;

import com.microsoft.playwright.*;
import com.microsoft.playwright.junit.Options;
import com.microsoft.playwright.junit.OptionsFactory;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.ColorScheme;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(EmulationTest.GermanPhone.class)
public class EmulationTest {
  public static class GermanPhone implements OptionsFactory {
    @Override
    public Options getOptions() {
      return new Options().setHeadless(true).setBaseUrl("http://localhost:4173")
          .setContextOptions(new Browser.NewContextOptions()
              .setViewportSize(390, 844)
              .setLocale("de-DE")
              .setTimezoneId("Asia/Kolkata")
              .setColorScheme(ColorScheme.DARK)
              .setHasTouch(true));
    }
  }

  @Test
  void theShopSeesAGermanPhoneUserInIndia(Page page) {
    page.navigate("/about-you");
    for (String id : new String[] {"width", "lang", "tz", "price", "touch"}) {
      System.out.println(String.format("%-6s ", id) + page.locator("#" + id).textContent());
    }
    Object dark = page.evaluate("matchMedia('(prefers-color-scheme: dark)').matches");
    System.out.println("dark   " + dark);
    assertThat(page.locator("#lang")).hasText("de-DE");
  }
}'''

GEO_TS = '''import { test, expect } from '@playwright/test';

test.describe('with the location shared', () => {
  test.use({
    geolocation: { latitude: 28.6139, longitude: 77.209 },   // New Delhi
    permissions: ['geolocation'],
  });

  test('finds stores near New Delhi', async ({ page }) => {
    await page.goto('/about-you');
    await page.getByRole('button', { name: 'Find stores near me' }).click();
    await expect(page.locator('#where')).toHaveText('28.6139, 77.2090');
  });
});

test('location blocked when permission is not granted', async ({ page }) => {
  await page.goto('/about-you');
  await page.getByRole('button', { name: 'Find stores near me' }).click();
  await expect(page.locator('#where')).toContainText('blocked');
});'''

GEO_PY = '''import pytest
from playwright.sync_api import Page, expect


@pytest.mark.browser_context_args(
    geolocation={"latitude": 28.6139, "longitude": 77.209},   # New Delhi
    permissions=["geolocation"],
)
def test_finds_stores_near_new_delhi(page: Page):
    page.goto("/about-you")
    page.get_by_role("button", name="Find stores near me").click()
    expect(page.locator("#where")).to_have_text("28.6139, 77.2090")


def test_location_blocked_when_permission_is_not_granted(page: Page):
    page.goto("/about-you")
    page.get_by_role("button", name="Find stores near me").click()
    expect(page.locator("#where")).to_contain_text("blocked")'''

GEO_JAVA = '''package com.brainy;

import com.microsoft.playwright.*;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class LocationTest {
  @Test
  void findsStoresNearNewDelhi(Browser browser) {
    BrowserContext context = browser.newContext(new Browser.NewContextOptions()
        .setGeolocation(28.6139, 77.209)                 // New Delhi
        .setPermissions(java.util.List.of("geolocation")));
    Page page = context.newPage();
    page.navigate("http://localhost:4173/about-you");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Find stores near me")).click();
    assertThat(page.locator("#where")).hasText("28.6139, 77.2090");
    context.close();
  }

  @Test
  void locationBlockedWhenPermissionIsNotGranted(Page page) {
    page.navigate("/about-you");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Find stores near me")).click();
    assertThat(page.locator("#where")).containsText("blocked");
  }
}'''

DEV_TS = '''import { test, expect, devices } from '@playwright/test';

test.use({ ...devices['Pixel 7'] });

test('the shop on a Pixel 7', async ({ page }) => {
  await page.goto('/about-you');
  console.log('width ', await page.locator('#width').textContent());
  console.log('touch ', await page.locator('#touch').textContent());
  console.log('mobile', await page.evaluate(() => /Mobile/.test(navigator.userAgent)));
  await expect(page.locator('#touch')).toHaveText('yes');
});'''

DEV_PY = '''from playwright.sync_api import Page, expect


def test_the_shop_on_a_pixel_7(page: Page):
    page.goto("/about-you")
    print("width ", page.locator("#width").text_content())
    print("touch ", page.locator("#touch").text_content())
    print("mobile", page.evaluate("/Mobile/.test(navigator.userAgent)"))
    expect(page.locator("#touch")).to_have_text("yes")'''

DEV_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.Options;
import com.microsoft.playwright.junit.OptionsFactory;
import com.microsoft.playwright.junit.UsePlaywright;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(DeviceTest.Pixel.class)
public class DeviceTest {
  public static class Pixel implements OptionsFactory {
    @Override
    public Options getOptions() {
      return new Options().setHeadless(true).setBaseUrl("http://localhost:4173").setDeviceName("Pixel 7");
    }
  }

  @Test
  void theShopOnAPixel7(Page page) {
    page.navigate("/about-you");
    System.out.println("width  " + page.locator("#width").textContent());
    System.out.println("touch  " + page.locator("#touch").textContent());
    System.out.println("mobile " + page.evaluate("/Mobile/.test(navigator.userAgent)"));
    assertThat(page.locator("#touch")).hasText("yes");
  }
}'''

TABS_TS = '''import { test, expect } from '@playwright/test';

test('help opens in a new tab', async ({ page }) => {
  await page.goto('/widgets');
  // Start waiting for the new tab before the click that opens it.
  const popupPromise = page.waitForEvent('popup');
  await page.getByRole('link', { name: 'Open help in a new tab' }).click();
  const help = await popupPromise;

  await expect(help).toHaveTitle('Help · Brainy Shop');
  console.log('Tabs open:', page.context().pages().length);
  await help.close();
  console.log('Tabs open:', page.context().pages().length);
});

test('the chat window is a popup', async ({ page }) => {
  await page.goto('/widgets');
  const popupPromise = page.waitForEvent('popup');
  await page.getByRole('button', { name: 'Open chat window' }).click();
  const chat = await popupPromise;
  await expect(chat.getByRole('heading')).toHaveText('Chat with us');
});'''

TABS_PY = '''from playwright.sync_api import Page, expect


def test_help_opens_in_a_new_tab(page: Page):
    page.goto("/widgets")
    # Start waiting for the new tab before the click that opens it.
    with page.expect_popup() as popup_info:
        page.get_by_role("link", name="Open help in a new tab").click()
    help = popup_info.value

    expect(help).to_have_title("Help · Brainy Shop")
    print("Tabs open:", len(page.context.pages))
    help.close()
    print("Tabs open:", len(page.context.pages))


def test_the_chat_window_is_a_popup(page: Page):
    page.goto("/widgets")
    with page.expect_popup() as popup_info:
        page.get_by_role("button", name="Open chat window").click()
    expect(popup_info.value.get_by_role("heading")).to_have_text("Chat with us")'''

TABS_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class TabsTest {
  @Test
  void helpOpensInANewTab(Page page) {
    page.navigate("/widgets");
    // waitForPopup runs the click and waits for the new tab it opens.
    Page help = page.waitForPopup(() ->
        page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Open help in a new tab")).click());

    assertThat(help).hasTitle("Help · Brainy Shop");
    System.out.println("Tabs open: " + page.context().pages().size());
    help.close();
    System.out.println("Tabs open: " + page.context().pages().size());
  }

  @Test
  void theChatWindowIsAPopup(Page page) {
    page.navigate("/widgets");
    Page chat = page.waitForPopup(() ->
        page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Open chat window")).click());
    assertThat(chat.getByRole(AriaRole.HEADING)).hasText("Chat with us");
  }
}'''

PERSIST_JS = '''import { chromium } from 'playwright';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const profile = mkdtempSync(join(tmpdir(), 'shop-profile-'));

// First visit: a real profile folder on disk, like a person's Chrome profile.
let context = await chromium.launchPersistentContext(profile);
let page = context.pages()[0];
await page.goto('http://localhost:4173/');
await page.evaluate(() => localStorage.setItem('theme', 'dark'));
await context.close();

// Second visit with the same folder: the data is still there.
context = await chromium.launchPersistentContext(profile);
page = context.pages()[0];
await page.goto('http://localhost:4173/');
console.log('theme =', await page.evaluate(() => localStorage.getItem('theme')));
await context.close();'''

PERSIST_TS = PERSIST_JS.replace('let context = await', 'let context: BrowserContext = await').replace("import { chromium } from 'playwright';", "import { chromium, type BrowserContext } from 'playwright';")

PERSIST_PY = '''import tempfile
from playwright.sync_api import sync_playwright

profile = tempfile.mkdtemp(prefix="shop-profile-")

with sync_playwright() as p:
    # First visit: a real profile folder on disk, like a person's Chrome profile.
    context = p.chromium.launch_persistent_context(profile)
    page = context.pages[0]
    page.goto("http://localhost:4173/")
    page.evaluate("localStorage.setItem('theme', 'dark')")
    context.close()

    # Second visit with the same folder: the data is still there.
    context = p.chromium.launch_persistent_context(profile)
    page = context.pages[0]
    page.goto("http://localhost:4173/")
    print("theme =", page.evaluate("localStorage.getItem('theme')"))
    context.close()'''

PERSIST_JAVA = '''package com.brainy;

import com.microsoft.playwright.*;
import java.nio.file.Files;
import java.nio.file.Path;

public class Main {
  public static void main(String[] args) throws Exception {
    Path profile = Files.createTempDirectory("shop-profile-");
    try (Playwright playwright = Playwright.create()) {
      // First visit: a real profile folder on disk, like a person's Chrome profile.
      BrowserContext context = playwright.chromium().launchPersistentContext(profile, new BrowserType.LaunchPersistentContextOptions());
      Page page = context.pages().get(0);
      page.navigate("http://localhost:4173/");
      page.evaluate("localStorage.setItem('theme', 'dark')");
      context.close();

      // Second visit with the same folder: the data is still there.
      context = playwright.chromium().launchPersistentContext(profile, new BrowserType.LaunchPersistentContextOptions());
      page = context.pages().get(0);
      page.navigate("http://localhost:4173/");
      System.out.println("theme = " + page.evaluate("localStorage.getItem('theme')"));
      context.close();
    }
  }
}'''

MULTI_CFG = '''import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  use: { baseURL: 'http://localhost:4173' },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'mobile', use: { ...devices['iPhone 15'] } },
    { name: 'edge', use: { ...devices['Desktop Edge'], channel: 'msedge' } },
  ],
});'''

CODES = {
    'launch': script(LAUNCH_JAVA, LAUNCH_PY, LAUNCH_JS, LAUNCH_TS, 'Launch a browser with options',
                     'The browser reports its type and its real version, here Chrome for Testing 153. After <code>close()</code> the connection is gone, and every page and context inside it is closed too.'),
    'iso': four('Two shoppers in one browser, kept apart',
                java=jv({'ContextTest.java': ISO_JAVA}),
                py=py({'test_contexts.py': ISO_PY}, cmd='pytest -v -s'),
                js=js({'contexts.spec.js': ISO_TS}),
                ts=ts({'contexts.spec.ts': ISO_TS}),
                result='Asha signed in inside her own context and got a session cookie. The guest context, in the same browser, has no cookie and still sees the Sign in link. In Playwright Test, a context you create from the <code>browser</code> fixture gets the same <code>use</code> options as the built in one, such as <code>baseURL</code>. The Python <code>new_context</code> fixture does the same and closes the contexts for you. In Java, a context you create yourself starts with default options, so the Java version uses full addresses.'),
    'emu': four('Pretend to be a German phone user in India',
                java=jv({'EmulationTest.java': EMU_JAVA}),
                py=py({'test_emulation.py': EMU_PY}, cmd='pytest -v -s'),
                js=js({'emulation.spec.js': EMU_TS}),
                ts=ts({'emulation.spec.ts': EMU_TS}),
                result='The page read 390 px, de-DE, a touch screen and dark mode, and the time zone as Asia/Calcutta, which is the older name Chromium still reports for Asia/Kolkata. It also formatted the euro price the German way, with a comma for decimals. All of it came from the context options. Nothing on the computer changed.'),
    'geo': four('Location and permissions',
                java=jv({'LocationTest.java': GEO_JAVA}),
                py=py({'test_location.py': GEO_PY}),
                js=js({'location.spec.js': GEO_TS}),
                ts=ts({'location.spec.ts': GEO_TS}),
                result='With the <code>geolocation</code> permission granted, the browser answers with the fake position at once. Without it, the request is refused, so the same page also lets you test the unhappy path.'),
    'device': four('Emulate a phone from the device list',
                   java=jv({'DeviceTest.java': DEV_JAVA}),
                   py=py({'test_device.py': DEV_PY}, cmd='pytest -v -s --device "Pixel 7"', ini='[pytest]\naddopts = --base-url http://localhost:4173'),
                   js=js({'device.spec.js': DEV_TS}),
                   ts=ts({'device.spec.ts': DEV_TS}),
                   result='One name sets the screen size, the pixel ratio, the user agent, touch and the mobile flag. Look at the width: 981 px, not 412. The About you page has no <code>&lt;meta name="viewport"&gt;</code> tag, so the phone lays it out at desktop width and zooms out, exactly like a real phone does. Emulation found a real mobile bug in the practice shop. Python takes the device on the command line with <code>--device</code>, Java takes it with <code>setDeviceName</code> in the options, and JavaScript spreads it into <code>test.use</code>.'),
    'tabs': four('New tabs and pop up windows',
                 java=jv({'TabsTest.java': TABS_JAVA}),
                 py=py({'test_tabs.py': TABS_PY}, cmd='pytest -v -s'),
                 js=js({'tabs.spec.js': TABS_TS}),
                 ts=ts({'tabs.spec.ts': TABS_TS}),
                 result='A link with <code>target="_blank"</code> and a <code>window.open</code> call both create a popup page. You start waiting before the click, then use the new page like any other. Both tabs live in the same context, so they share the login.'),
    'persist': script(PERSIST_JAVA, PERSIST_PY, PERSIST_JS, PERSIST_TS, 'A persistent profile that survives a restart',
                      'A persistent context keeps cookies and storage in a folder on disk, like a real Chrome profile. Tests normally avoid this, because a fresh context per test is what keeps tests independent. It is useful for browser extensions and for scripts that must stay signed in.'),
    'multi': one('One suite, many browsers and devices',
                 shown({'playwright.config.ts': MULTI_CFG}, 'ts', 'npx playwright test --project=firefox',
                       'Every test runs once per project, so this config runs each test five times. <code>--project</code> picks one. This file is shown and not run here, because only Chromium is installed on the build machine of this page.')),
}

PARTS = [
    part('levels', '🏢', 'Browser, context and page', f'''
<p>Playwright gives you three levels of objects, and it helps to picture them as real things:</p>
<ul>
<li><b>Browser</b>: the browser program that is running, such as Chromium. Starting it is slow, about half a second, so you start one and reuse it.</li>
<li><b>Browser context</b>: a brand new, empty browser profile inside that browser. It has its own cookies, storage, cache and permissions, like a fresh incognito window. Creating one takes a few milliseconds.</li>
<li><b>Page</b>: one tab inside a context. A context can have many pages, and they share the context's login.</li>
</ul>
{tip('Picture a shop with one building and many changing rooms. The building is the browser. Each changing room is a context: what one customer leaves in their room never appears in another room. The pages are the hangers in the room, all belonging to the same customer.', 'kid')}
<p>Build them yourself below. Add contexts and pages, sign a context in, and watch what is shared and what is not.</p>
{viz('pwctx')}
<p>This is why test runners create a new context for every test. Two tests can never see each other's cookies, so they pass in any order and can run in parallel.</p>
''', easy=True, kw=['browser', 'context', 'page', 'isolation', 'incognito']),

    part('launch', '🚀', 'Launching a browser', f'''
<p>In a script you launch the browser yourself. In a test runner the runner launches it for you, and you only set the options.</p>
[[launch]]
{table(['Option', 'What it does', 'When you use it'], [
    ['headless', 'run without a window (the default)', 'always on CI, turn off to watch a test locally'],
    ['slowMo', 'pause before each action', 'to follow a test with your eyes or record a demo'],
    ['channel', 'use an installed branded browser: <code>chrome</code>, <code>msedge</code>, <code>chrome-beta</code>', 'when the team must test the exact browser users have'],
    ['args', 'extra command line switches for the browser', 'rare cases, such as a language or a fake camera'],
    ['executablePath', 'start a browser from a path you give', 'company images with their own browser build'],
    ['timeout', 'how long to wait for the browser to start', 'slow CI machines'],
])}
<p>{by(java='In JUnit with <code>@UsePlaywright</code>, set these in your options class with <code>setHeadless</code>, <code>setChannel</code>, <code>setBrowserName</code> and <code>setLaunchOptions</code>.',
      py='With pytest-playwright, use <code>--headed</code>, <code>--slowmo</code>, <code>--browser</code> and <code>--browser-channel</code>, or override the <code>browser_type_launch_args</code> fixture in conftest.py.',
      js='In Playwright Test, put them in <code>use</code> in the config: <code>headless</code>, <code>channel</code>, and <code>launchOptions: { slowMo, args }</code>.')}</p>
''', easy=True, kw=['launch', 'headless', 'slowMo', 'channel', 'chrome', 'msedge']),

    part('contexts', '🧳', 'Contexts keep tests apart', f'''
<p>One browser can hold many contexts at the same time. This test signs Asha in inside one context and checks that a second context, in the same browser, is still a guest.</p>
[[iso]]
{tip('Real projects use two contexts in one test for features with two people: a chat between a customer and a support agent, an admin approving an order while the customer waits, or two players in a game. Each person gets their own context.', 'pro')}
''', kw=['newContext', 'cookies', 'isolation', 'multiple users']),

    part('emulate', '🎭', 'Pretend to be another user', f'''
<p>Context options change what the website sees about the browser. You can test a German user in India on a small screen in dark mode, without leaving your desk. The shop's <b>About you</b> page prints what it sees.</p>
[[emu]]
{table(['Option', 'Example', 'What the page sees'], [
    ['viewport', '390 × 844', '<code>innerWidth</code>, media queries'],
    ['locale', 'de-DE', '<code>navigator.language</code>, number and date formats'],
    ['timezoneId', 'Asia/Kolkata', 'dates and times'],
    ['colorScheme', 'dark', '<code>prefers-color-scheme</code>'],
    ['hasTouch, isMobile', 'true', 'touch events, mobile layout'],
    ['geolocation, permissions', 'New Delhi', 'the location API'],
    ['userAgent', 'any string', '<code>navigator.userAgent</code>'],
    ['offline', 'true', 'no network at all'],
])}
[[geo]]
''', kw=['emulation', 'locale', 'timezone', 'viewport', 'dark mode', 'geolocation', 'permissions']),

    part('devices', '📱', 'Phones and tablets', f'''
<p>Playwright ships a list of more than 200 device profiles, such as <b>iPhone 15</b>, <b>Pixel 7</b> and <b>Galaxy S24</b>. Each profile is a set of context options. This is emulation inside a desktop browser engine: it gets the size, the touch input and the user agent right, but it is not a real phone.</p>
[[device]]
{tip('Emulation catches most layout and touch bugs and costs nothing. Some bugs only show on real hardware, such as a keyboard covering a field or a slow phone. Many teams run emulated phones on every commit and real devices in a cloud service before a release.', 'warn')}
''', kw=['devices', 'mobile', 'iPhone', 'Pixel', 'emulation']),

    part('tabs', '🗂️', 'New tabs and pop ups', f'''
<p>When a click opens a new tab or window, Playwright gives you a new page object for it. The trick is to start waiting <b>before</b> the click, so the event cannot be missed.</p>
[[tabs]]
<p>{by(java='Java wraps the action in a lambda: <code>page.waitForPopup(() -&gt; ...click())</code> runs the click and returns the new page.',
      py='Python uses a <code>with page.expect_popup() as info:</code> block around the click, then <code>info.value</code> is the new page.',
      js='JavaScript stores the promise first, <code>const p = page.waitForEvent(\'popup\')</code>, then clicks, then awaits the promise.')}</p>
<p>To catch any new page in the context, not only popups of one page, wait for the context's <code>page</code> event instead.</p>
''', kw=['popup', 'new tab', 'waitForPopup', 'expect_popup', 'window.open']),

    part('browsers', '🦊', 'Chromium, Firefox and WebKit', f'''
<p>Each Playwright release is tested with its own builds of Chromium, Firefox and WebKit. Running the same tests in all three catches bugs that only one engine shows, such as a date picker that breaks in Safari.</p>
[[multi]]
{table(['', '☕ Java', '🐍 Python', '🟨🔷 Playwright Test'], [
    ['pick the engine', '<code>playwright.firefox()</code> or <code>setBrowserName("firefox")</code>', '<code>--browser firefox</code>', 'a project with <code>devices[\'Desktop Firefox\']</code>'],
    ['all three in one run', 'a parameterized test or three Maven runs', '<code>--browser chromium --browser firefox --browser webkit</code>', 'three projects in the config'],
    ['branded Chrome or Edge', '<code>setChannel("chrome")</code>', '<code>--browser-channel chrome</code>', '<code>channel: \'chrome\'</code>'],
])}
{tip('WebKit on Windows and Linux is the engine of Safari, not Safari itself. It catches most Safari bugs. For the last few percent, teams run a small smoke suite on real Safari on a Mac.', 'tip')}
''', kw=['firefox', 'webkit', 'safari', 'projects', 'cross browser']),

    part('lifecycle', '♻️', 'Profiles, closing and remote browsers', f'''
<p>Most of the time a fresh context per test is right. Two other ways to get a browser are worth knowing.</p>
[[persist]]
<ul>
<li><b>Connect to a browser that is already running.</b> <code>chromium.connectOverCDP(url)</code> attaches to a Chrome started with a remote debugging port, for example to automate a browser that a person already signed into.</li>
<li><b>Run browsers on another machine.</b> <code>launchServer()</code> starts a browser that others connect to with <code>browserType.connect(wsEndpoint)</code>. Cloud grids and the Playwright Docker image use this.</li>
</ul>
{tip('Close what you open. In a test runner the fixtures close contexts and pages for you. In a script, close the browser at the end, or use try with resources in Java and a with block in Python, so a crash does not leave browser processes running on the machine.', 'tip')}
''', kw=['launchPersistentContext', 'profile', 'connectOverCDP', 'launchServer', 'close']),
]

INFO = {'title': 'One browser, many clean rooms', 'panels': [
    panel([['e', '🌐'], ['t', 'browser', {'b': 1}]], 'Browser', 'Start once, about 0.5 s.', 'Shared by many tests.'),
    panel([['e', '🧳'], ['t', 'context', {'b': 1}]], 'Context', 'A fresh, empty profile.', 'Its own cookies, storage and permissions.'),
    panel([['e', '📄'], ['t', 'page', {'b': 1}]], 'Page', 'One tab.', 'Tabs in a context share the login.'),
    panel([['e', '📱'], ['t', 'devices[...]', {'b': 1}]], 'Emulation', 'Size, locale, time zone, location.', 'Set on the context, nothing on your computer changes.')],
    'remember': 'Start one browser, give every test a new context, and set what the site should see, such as a phone or a German user, with context options.'}

REAL = [
    ['💬', 'Support chat', 'A test opens two contexts, one signed in as a customer and one as a support agent, and checks that a message typed by one appears for the other.'],
    ['🌍', 'A shop in five countries', 'The same checkout test runs with five locales and time zones, and checks the currency format and the delivery date shown to each country.'],
    ['📱', 'Mobile first launch', 'Before a mobile redesign goes live, the team adds Pixel 7 and iPhone 15 projects to the config, and the whole suite runs on both every night.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers browsers, contexts and pages, launch options, emulating users and devices, new tabs and pop ups, the three browser engines, and persistent profiles.',
        'यह अध्याय browsers, contexts और pages, launch options, users और devices की नकल, नए tabs और pop ups, तीन browser engines और persistent profiles समझाता है।',
        'ಈ ಅಧ್ಯಾಯ browsers, contexts ಮತ್ತು pages, launch options, users ಮತ್ತು devices ಅನುಕರಣೆ, ಹೊಸ tabs ಮತ್ತು pop ups, ಮೂರು browser engines ಮತ್ತು persistent profiles ವಿವರಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ browsers, contexts ଓ pages, launch options, users ଓ devices ର ନକଲ, ନୂଆ tabs ଓ pop ups, ତିନୋଟି browser engines ଏବଂ persistent profiles ବୁଝାଏ।',
        'يغطي هذا الفصل المتصفحات والسياقات والصفحات وخيارات التشغيل ومحاكاة المستخدمين والأجهزة والتبويبات والنوافذ المنبثقة ومحركات المتصفح الثلاثة والملفات الشخصية الدائمة.',
        'Dieses Kapitel behandelt Browser, Kontexte und Seiten, Startoptionen, die Emulation von Nutzern und Geräten, neue Tabs und Pop-ups, die drei Browser-Engines und dauerhafte Profile.'),
    say('levels', 'Browser, context, page', 'A browser is the running program. A context is a fresh, empty profile with its own cookies and storage. A page is one tab. Test runners give every test a new context.',
        'Browser चलता हुआ program है। Context एक नया, खाली profile है जिसकी अपनी cookies और storage होती है। Page एक tab है। Test runners हर टेस्ट को नया context देते हैं।',
        'Browser ಚಲಿಸುತ್ತಿರುವ program. Context ತನ್ನದೇ cookies ಮತ್ತು storage ಇರುವ ಹೊಸ ಖಾಲಿ profile. Page ಒಂದು tab. Test runners ಪ್ರತಿ ಟೆಸ್ಟ್‌ಗೆ ಹೊಸ context ನೀಡುತ್ತವೆ.',
        'Browser ଚାଲୁଥିବା program। Context ନିଜର cookies ଓ storage ଥିବା ଏକ ନୂଆ ଖାଲି profile। Page ଗୋଟିଏ tab। Test runners ପ୍ରତ୍ୟେକ ଟେଷ୍ଟକୁ ନୂଆ context ଦିଅନ୍ତି।',
        'المتصفح هو البرنامج العامل. السياق ملف شخصي جديد فارغ له ملفات تعريف الارتباط والتخزين الخاصة به. الصفحة تبويب واحد. تعطي مشغّلات الاختبار كل اختبار سياقًا جديدًا.',
        'Der Browser ist das laufende Programm. Ein Kontext ist ein frisches, leeres Profil mit eigenen Cookies und eigenem Speicher. Eine Seite ist ein Tab. Test Runner geben jedem Test einen neuen Kontext.'),
    say('launch', 'Launching', 'Launch options control the browser: headless, slow motion, a branded channel such as Chrome or Edge, extra arguments and the start timeout. In test runners you set them in the config or options.',
        'Launch options browser को नियंत्रित करते हैं: headless, slow motion, Chrome या Edge जैसा channel, extra arguments और start timeout। Test runners में इन्हें config या options में रखते हैं।',
        'Launch options browser ನಿಯಂತ್ರಿಸುತ್ತವೆ: headless, slow motion, Chrome ಅಥವಾ Edge ನಂತಹ channel, extra arguments ಮತ್ತು start timeout. Test runners ನಲ್ಲಿ ಇವುಗಳನ್ನು config ಅಥವಾ options ನಲ್ಲಿ ಇಡುತ್ತೇವೆ.',
        'Launch options browser କୁ ନିୟନ୍ତ୍ରଣ କରନ୍ତି: headless, slow motion, Chrome ବା Edge ଭଳି channel, extra arguments ଓ start timeout। Test runners ରେ ଏଗୁଡ଼ିକ config ବା options ରେ ରଖାଯାଏ।',
        'تتحكم خيارات التشغيل بالمتصفح: الوضع بدون واجهة والحركة البطيئة والقناة مثل Chrome أو Edge والوسائط الإضافية ومهلة البدء. في مشغّلات الاختبار تضعها في الإعدادات أو الخيارات.',
        'Startoptionen steuern den Browser: headless, Zeitlupe, ein Kanal wie Chrome oder Edge, zusätzliche Argumente und das Start-Timeout. In Test Runnern setzt du sie in der Konfiguration oder den Optionen.'),
    say('contexts', 'Contexts keep tests apart', 'Two contexts in one browser share nothing. Asha signs in inside one context while the other stays a guest. Use this for features with two people, such as a chat.',
        'एक browser के दो contexts कुछ साझा नहीं करते। Asha एक context में sign in करती है जबकि दूसरा guest रहता है। दो लोगों वाली सुविधाओं जैसे chat के लिए इसका उपयोग करें।',
        'ಒಂದೇ browser ನ ಎರಡು contexts ಏನನ್ನೂ ಹಂಚಿಕೊಳ್ಳುವುದಿಲ್ಲ. Asha ಒಂದು context ನಲ್ಲಿ sign in ಮಾಡಿದರೆ ಇನ್ನೊಂದು guest ಆಗಿಯೇ ಇರುತ್ತದೆ. chat ನಂತಹ ಇಬ್ಬರ ಸೌಲಭ್ಯಗಳಿಗೆ ಇದನ್ನು ಬಳಸಿ.',
        'ଗୋଟିଏ browser ର ଦୁଇଟି contexts କିଛି ବାଣ୍ଟନ୍ତି ନାହିଁ। Asha ଗୋଟିଏ context ରେ sign in କଲେ ଅନ୍ୟଟି guest ରହେ। chat ଭଳି ଦୁଇଜଣଙ୍କ ସୁବିଧା ପାଇଁ ଏହା ବ୍ୟବହାର କରନ୍ତୁ।',
        'سياقان في متصفح واحد لا يتشاركان شيئًا. تسجّل Asha الدخول في سياق بينما يبقى الآخر ضيفًا. استخدم ذلك للميزات التي تحتاج شخصين مثل الدردشة.',
        'Zwei Kontexte in einem Browser teilen nichts. Asha meldet sich in einem Kontext an, während der andere Gast bleibt. Nutze das für Funktionen mit zwei Personen, zum Beispiel einen Chat.'),
    say('emulate', 'Emulation', 'Context options change what the site sees: screen size, language, time zone, dark mode, touch, location and permissions. Nothing on your computer changes.',
        'Context options बदलते हैं कि site क्या देखती है: screen size, भाषा, time zone, dark mode, touch, location और permissions। आपके computer पर कुछ नहीं बदलता।',
        'Context options site ನೋಡುವುದನ್ನು ಬದಲಾಯಿಸುತ್ತವೆ: screen size, ಭಾಷೆ, time zone, dark mode, touch, location ಮತ್ತು permissions. ನಿಮ್ಮ computer ನಲ್ಲಿ ಏನೂ ಬದಲಾಗುವುದಿಲ್ಲ.',
        'Context options site କଣ ଦେଖେ ତାହା ବଦଳାନ୍ତି: screen size, ଭାଷା, time zone, dark mode, touch, location ଓ permissions। ଆପଣଙ୍କ computer ରେ କିଛି ବଦଳେ ନାହିଁ।',
        'تغيّر خيارات السياق ما يراه الموقع: حجم الشاشة واللغة والمنطقة الزمنية والوضع الداكن واللمس والموقع والأذونات. لا يتغير شيء على حاسوبك.',
        'Kontextoptionen ändern, was die Seite sieht: Bildschirmgröße, Sprache, Zeitzone, Dunkelmodus, Touch, Standort und Berechtigungen. Auf deinem Computer ändert sich nichts.'),
    say('devices', 'Phones and tablets', 'Playwright has more than 200 device profiles such as iPhone 15 and Pixel 7. One name sets size, pixel ratio, user agent and touch. It is emulation, not a real phone.',
        'Playwright में 200 से ज़्यादा device profiles हैं जैसे iPhone 15 और Pixel 7। एक नाम size, pixel ratio, user agent और touch तय करता है। यह नकल है, असली phone नहीं।',
        'Playwright ನಲ್ಲಿ iPhone 15 ಮತ್ತು Pixel 7 ನಂತಹ 200 ಕ್ಕೂ ಹೆಚ್ಚು device profiles ಇವೆ. ಒಂದು ಹೆಸರು size, pixel ratio, user agent ಮತ್ತು touch ಹೊಂದಿಸುತ್ತದೆ. ಇದು ಅನುಕರಣೆ, ನಿಜವಾದ phone ಅಲ್ಲ.',
        'Playwright ରେ iPhone 15 ଓ Pixel 7 ଭଳି 200 ରୁ ଅଧିକ device profiles ଅଛି। ଗୋଟିଏ ନାମ size, pixel ratio, user agent ଓ touch ସେଟ କରେ। ଏହା ନକଲ, ପ୍ରକୃତ phone ନୁହେଁ।',
        'يملك Playwright أكثر من 200 ملف جهاز مثل iPhone 15 وPixel 7. اسم واحد يضبط الحجم ونسبة البكسل ووكيل المستخدم واللمس. إنها محاكاة وليست هاتفًا حقيقيًا.',
        'Playwright hat über 200 Geräteprofile wie iPhone 15 und Pixel 7. Ein Name setzt Größe, Pixeldichte, User Agent und Touch. Das ist Emulation, kein echtes Telefon.'),
    say('tabs', 'New tabs and pop ups', 'When a click opens a new tab, start waiting for the popup before the click, then use the new page like any other. Tabs in one context share the login.',
        'जब click से नया tab खुले, तो click से पहले popup का इंतज़ार शुरू करें, फिर नए page को सामान्य page की तरह इस्तेमाल करें। एक context के tabs login साझा करते हैं।',
        'Click ನಿಂದ ಹೊಸ tab ತೆರೆದಾಗ, click ಗಿಂತ ಮೊದಲೇ popup ಗಾಗಿ ಕಾಯಲು ಆರಂಭಿಸಿ, ನಂತರ ಹೊಸ page ಅನ್ನು ಇತರ page ನಂತೆ ಬಳಸಿ. ಒಂದು context ನ tabs login ಹಂಚಿಕೊಳ್ಳುತ್ತವೆ.',
        'Click ରେ ନୂଆ tab ଖୋଲିଲେ, click ପୂର୍ବରୁ popup ପାଇଁ ଅପେକ୍ଷା ଆରମ୍ଭ କରନ୍ତୁ, ତାପରେ ନୂଆ page କୁ ଅନ୍ୟ page ଭଳି ବ୍ୟବହାର କରନ୍ତୁ। ଗୋଟିଏ context ର tabs login ବାଣ୍ଟନ୍ତି।',
        'عندما تفتح نقرة تبويبًا جديدًا، ابدأ انتظار النافذة المنبثقة قبل النقر، ثم استخدم الصفحة الجديدة كأي صفحة. تتشارك تبويبات السياق الواحد تسجيل الدخول.',
        'Wenn ein Klick einen neuen Tab öffnet, beginne vor dem Klick auf das Pop-up zu warten und nutze die neue Seite dann wie jede andere. Tabs in einem Kontext teilen die Anmeldung.'),
    say('browsers', 'Three engines', 'Playwright tests Chromium, Firefox and WebKit. In Playwright Test each engine is a project in the config. Python uses minus minus browser and Java uses the browser name option.',
        'Playwright Chromium, Firefox और WebKit टेस्ट करता है। Playwright Test में हर engine config का एक project है। Python minus minus browser और Java browser name option इस्तेमाल करता है।',
        'Playwright Chromium, Firefox ಮತ್ತು WebKit ಪರೀಕ್ಷಿಸುತ್ತದೆ. Playwright Test ನಲ್ಲಿ ಪ್ರತಿ engine config ನ ಒಂದು project. Python minus minus browser ಮತ್ತು Java browser name option ಬಳಸುತ್ತದೆ.',
        'Playwright Chromium, Firefox ଓ WebKit ପରୀକ୍ଷା କରେ। Playwright Test ରେ ପ୍ରତ୍ୟେକ engine config ର ଏକ project। Python minus minus browser ଓ Java browser name option ବ୍ୟବହାର କରେ।',
        'يختبر Playwright محركات Chromium وFirefox وWebKit. في Playwright Test كل محرك مشروع في الإعدادات. يستخدم Python الخيار ناقص ناقص browser وتستخدم Java خيار اسم المتصفح.',
        'Playwright testet Chromium, Firefox und WebKit. In Playwright Test ist jede Engine ein Projekt in der Konfiguration. Python nutzt minus minus browser und Java die Option für den Browsernamen.'),
    say('lifecycle', 'Profiles and remote browsers', 'A persistent context keeps data in a folder like a real profile. You can also connect to a running Chrome over CDP, or to a browser server on another machine. Always close what you open.',
        'Persistent context data को असली profile की तरह folder में रखता है। आप CDP से चल रहे Chrome से या दूसरी machine के browser server से भी जुड़ सकते हैं। जो खोलें उसे हमेशा बंद करें।',
        'Persistent context ನಿಜವಾದ profile ನಂತೆ data ಅನ್ನು folder ನಲ್ಲಿ ಇಡುತ್ತದೆ. CDP ಮೂಲಕ ಚಲಿಸುತ್ತಿರುವ Chrome ಗೆ ಅಥವಾ ಬೇರೆ machine ನ browser server ಗೆ ಸಂಪರ್ಕಿಸಬಹುದು. ತೆರೆದದ್ದನ್ನು ಯಾವಾಗಲೂ ಮುಚ್ಚಿ.',
        'Persistent context ପ୍ରକୃତ profile ଭଳି data କୁ folder ରେ ରଖେ। CDP ଦ୍ୱାରା ଚାଲୁଥିବା Chrome କିମ୍ବା ଅନ୍ୟ machine ର browser server ସହ ମଧ୍ୟ ଯୋଡ଼ିହେବ। ଯାହା ଖୋଲନ୍ତି ସବୁବେଳେ ବନ୍ଦ କରନ୍ତୁ।',
        'يحفظ السياق الدائم البيانات في مجلد مثل ملف شخصي حقيقي. يمكنك أيضًا الاتصال بمتصفح Chrome يعمل عبر CDP أو بخادم متصفح على جهاز آخر. أغلق دائمًا ما تفتحه.',
        'Ein dauerhafter Kontext speichert Daten in einem Ordner wie ein echtes Profil. Du kannst dich auch per CDP mit einem laufenden Chrome oder mit einem Browserserver auf einem anderen Rechner verbinden. Schließe immer, was du öffnest.'),
    say('practice', 'Playground labs', 'In the labs you make the page phone sized and check what the shop sees, and you sign in and check that the login reaches a second page in the same context.',
        'Labs में आप page को phone के आकार का बनाकर देखते हैं कि shop क्या देखती है, और sign in करके जाँचते हैं कि login उसी context के दूसरे page तक पहुँचता है।',
        'Labs ನಲ್ಲಿ ನೀವು page ಅನ್ನು phone ಗಾತ್ರಕ್ಕೆ ಮಾಡಿ shop ಏನು ನೋಡುತ್ತದೆ ಎಂದು ಪರಿಶೀಲಿಸುತ್ತೀರಿ, ಮತ್ತು sign in ಮಾಡಿ ಅದೇ context ನ ಇನ್ನೊಂದು page ಗೆ login ತಲುಪುತ್ತದೆಯೇ ಎಂದು ನೋಡುತ್ತೀರಿ.',
        'Labs ରେ ଆପଣ page କୁ phone ଆକାରର କରି shop କଣ ଦେଖେ ଯାଞ୍ଚ କରନ୍ତି, ଏବଂ sign in କରି ଦେଖନ୍ତି ଯେ login ସେହି context ର ଅନ୍ୟ page କୁ ପହଞ୍ଚେ।',
        'في المختبرات تجعل الصفحة بحجم الهاتف وتتحقق مما يراه المتجر، وتسجّل الدخول وتتحقق من أن تسجيل الدخول يصل إلى صفحة ثانية في السياق نفسه.',
        'In den Labs machst du die Seite so groß wie ein Telefon und prüfst, was der Shop sieht, und du meldest dich an und prüfst, dass die Anmeldung eine zweite Seite im selben Kontext erreicht.'),
]

QUIZ = [
    quiz(1, 'What is a browser context?', ['A new browser program', 'A fresh, empty profile with its own cookies and storage', 'One HTML element', 'A test file'], 1,
         'Think of an incognito window.', 'A context is an isolated profile inside a running browser. Creating one is fast.'),
    quiz(1, 'Why do test runners give each test a new context?', ['It is faster than a new page', 'So tests never share cookies or logins and can run in any order', 'Browsers need it', 'To use less memory'], 1,
         'Independence.', 'A fresh context per test keeps tests independent and safe to run in parallel.'),
    quiz(1, 'Which option shows the browser window?', ['slowMo', 'headless: false', 'channel', 'devtools'], 1,
         'Headless means no window.', 'Set <code>headless</code> to false (or pass <code>--headed</code>) to see the window.'),
    quiz(1, 'Two pages in the same context: what do they share?', ['Nothing', 'Cookies and storage, so the login', 'Only the URL', 'Only the title'], 1,
         'They are tabs of the same profile.', 'Pages in one context share cookies and storage, like tabs of one browser window.'),
    quiz(2, 'How does a test check a German user without changing the computer?', ['Install a German Windows', 'Set locale to de-DE in the context options', 'Use a VPN', 'Change the server'], 1,
         'The context controls what the page sees.', 'The <code>locale</code> option changes <code>navigator.language</code> and number and date formatting for that context.'),
    quiz(2, 'When must you start waiting for a popup?', ['After the click', 'Before the click that opens it', 'Any time', 'After the page loads'], 1,
         'Events can fire very fast.', 'Start waiting first, then click, so the popup event cannot happen before you are listening.'),
    quiz(2, 'In Python, which fixture creates extra contexts that keep the base URL?', ['context', 'browser', 'new_context', 'make_context'], 2,
         'It is a function you call.', '<code>new_context()</code> uses the browser context args, including the base URL, and closes the contexts after the test.'),
    quiz(2, 'Without the geolocation permission, what did the About you page show after clicking Find stores near me?', ['New Delhi', 'blocked', 'Nothing happens', 'An error in the test'], 1,
         'The browser refuses to share the position.', 'The location request is refused and the page shows that it was blocked.'),
    quiz(2, 'Which Java option emulates a Pixel 7 with @UsePlaywright?', ['setDevice("Pixel 7")', 'setDeviceName("Pixel 7")', 'setMobile(true)', 'devices.get("Pixel 7")'], 1,
         'It takes a device name.', 'The JUnit Options class has <code>setDeviceName</code>.'),
    quiz(3, 'What is a persistent context good for?', ['Every normal test', 'Browser extensions and scripts that must keep a real profile', 'Faster tests', 'Parallel runs'], 1,
         'It keeps data on disk between runs.', 'Persistent contexts are for profiles that must survive, such as extension testing. Normal tests want a fresh context.'),
    quiz(3, 'In Playwright Test, a test creates its own context with <code>browser.newContext()</code>. Which settings does it get?', ['None, always the defaults', 'The use options from the config, such as baseURL and locale', 'Only the viewport', 'The settings of the last test'], 1,
         'The build of this page checked this with a real run.', 'Playwright Test applies the <code>use</code> options to contexts created from the <code>browser</code> fixture too. In Java, a context you create yourself starts with default options.'),
    quiz(3, 'Which call attaches to a Chrome that is already running with a debugging port?', ['chromium.launch()', 'chromium.connectOverCDP(url)', 'chromium.attach()', 'browser.newContext()'], 1,
         'CDP is the Chrome DevTools Protocol.', '<code>connectOverCDP</code> connects to an existing Chromium based browser.'),
]

CALC = [
    calc(1, 'A config has 3 browser projects and 2 phone projects. A suite has 10 tests. How many test runs?', 50, 'projects times tests', ['3 + 2 = 5 projects', '5 × 10 = 50 runs']),
    calc(1, 'A context holds 3 pages. You close 1. How many pages are left?', 2, '3 minus 1', ['3 - 1 = 2 pages']),
    calc(2, 'slowMo is 100 ms and a test has 12 actions. How many seconds of extra waiting does slowMo add?', 1.2, '12 × 100 ms', ['12 × 100 = 1200 ms', '1200 ms = 1.2 s']),
    calc(2, 'A new context takes 8 ms and a new browser takes 600 ms. How many contexts can you create in the time of one browser start?', 75, '600 ÷ 8', ['600 ÷ 8 = 75 contexts']),
    calc(2, 'A shop supports 4 locales and 3 screen sizes. A checkout test must run once for each pair. How many runs?', 12, '4 × 3', ['4 locales × 3 sizes = 12 runs']),
    calc(3, 'The iPhone 15 profile has a viewport 393 px wide and a device scale factor of 3. How many real pixels wide is a screenshot?', 1179, '393 × 3', ['393 × 3 = 1179 pixels']),
    calc(3, 'A chat test needs a customer and an agent. 6 chat tests each use 2 contexts. How many contexts are created?', 12, '6 × 2', ['6 tests × 2 contexts = 12 contexts']),
    calc(3, 'Running 200 tests in 3 engines takes 30 minutes. Running only Chromium on each commit and all three at night: how many minutes does one commit run take?', 10,
         'one third of the time', ['3 engines take 30 minutes', '1 engine takes 30 ÷ 3 = 10 minutes']),
]

LABS = [
    {'id': 'phone', 'title': 'A phone sized screen', 'name': 'the shop on a narrow screen',
     'task': 'Make the page 390 pixels wide and 844 high with <code>setViewportSize</code>, open <code>/about-you</code>, and check that the shop reports a screen width of <b>390 px</b>.',
     'goal': 'The shop sees a 390 px wide screen.', 'start': '/about-you',
     'code': {'ts': """import { test, expect } from '@playwright/test';

test('the shop on a narrow screen', async ({ page }) => {
  // 1. set the viewport size
  // 2. open /about-you
  // 3. check the text of #width
});"""},
     'answer': {'ts': """import { test, expect } from '@playwright/test';

test('the shop on a narrow screen', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/about-you');
  await expect(page.locator('#width')).toHaveText('390 px');
});"""},
     'hint': '<code>page.setViewportSize({ width: 390, height: 844 })</code> in JavaScript, <code>page.set_viewport_size({"width": 390, "height": 844})</code> in Python and <code>page.setViewportSize(390, 844)</code> in Java.',
     'why': 'Changing the size of one page is quick for a single check. For a whole suite on phones, set the viewport or a device in the context options instead.',
     'check': [["ctx.url.includes('/about-you')", 'The test opened the About you page'], ["/390/.test(ctx.code)", 'The test sets a 390 px wide viewport']]},
    {'id': 'sharedlogin', 'title': 'The login follows you to another page', 'name': 'login is shared by the pages of a context',
     'task': 'Sign in as Asha, then open <code>/cart</code> in the same page and check that the header still says <b>Hello, Asha</b>. The cookie lives in the context, so every page of it is signed in.',
     'goal': 'Asha is still signed in on the cart page.', 'start': '/login',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('login is shared by the pages of a context', async ({ page }) => {
  await page.goto('/login');
  // sign in, then go to /cart and check the greeting
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('login is shared by the pages of a context', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('s3cret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByText('Hello, Asha')).toBeVisible();
  await page.goto('/cart');
  await expect(page.getByText('Hello, Asha')).toBeVisible();
});'''},
     'hint': 'Sign in exactly like in chapter 1, then <code>page.goto(\'/cart\')</code> and check the same greeting again.',
     'why': 'The login is stored in the context, not in the page. This is also why a fresh context per test means every test starts signed out.',
     'check': [['ctx.loggedIn', 'Asha is signed in'], ["ctx.url.includes('/cart')", 'The test went to the cart']]},
]

T = {
    'slug': 'pw-browsers', 'title': 'Browsers, contexts, pages and devices', 'short': 'Browsers and contexts', 'emoji': '🌐', 'module': MODULE, 'minutes': 20,
    'lead': 'Start browsers with the right options, keep tests apart with contexts, pretend to be a German phone user in India, handle new tabs and pop ups, and run in Chromium, Firefox and WebKit.',
    'desc': 'Browser, BrowserContext and Page, launch options, isolation with contexts, emulating locale, time zone, dark mode, location and devices, popups and tabs, cross browser projects and persistent profiles in four languages.',
    'summary': 'The browser, context and page levels with an interactive builder, launch options such as headless, slowMo and channel, two signed in users in one browser, context options for viewport, locale, time zone, colour scheme, touch, geolocation and permissions, device profiles, new tabs and popups, Chromium, Firefox and WebKit projects, persistent profiles, connectOverCDP and browser servers.',
    'keywords': ['browser', 'browser context', 'page', 'launch options', 'headless', 'emulation', 'devices', 'locale', 'timezone', 'geolocation', 'permissions', 'popup', 'new tab', 'firefox', 'webkit', 'persistent context'],
    'plain': 'A browser is the program, a context is a clean profile inside it, and a page is one tab. Each test gets its own clean profile, and you can make that profile look like any phone, country or language.',
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
