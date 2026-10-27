from pkit import part, say, quiz, calc, panel, four, one, js, ts, py, jv, shown, walk, step, table, tip, by, viz, figure

MODULE = ('🌐', 'Browser handling', 'pw-browser', 'Browsers, contexts, pages, devices and tabs, then navigation, frames, dialogs, downloads, uploads and events.')

# ---------- navigation ----------
NAV_TS = '''import { test, expect } from '@playwright/test';

test('moving around the shop', async ({ page }) => {
  await page.goto('/login', { waitUntil: 'domcontentloaded' });
  console.log('1.', page.url());

  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('s3cret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('**/products');            // the app moves on by itself
  console.log('2.', page.url());

  await page.goBack();
  await expect(page).toHaveURL(/\\/login$/);
  console.log('3.', page.url());

  await page.goForward();
  await page.reload();
  await expect(page).toHaveURL(/\\/products$/);
  console.log('4.', page.url(), '|', await page.title());
});'''

NAV_PY = '''import re
from playwright.sync_api import Page, expect


def test_moving_around_the_shop(page: Page):
    page.goto("/login", wait_until="domcontentloaded")
    print("1.", page.url)

    page.get_by_label("Email").fill("asha@shop.example")
    page.get_by_label("Password").fill("s3cret")
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_url("**/products")              # the app moves on by itself
    print("2.", page.url)

    page.go_back()
    expect(page).to_have_url(re.compile(r"/login$"))
    print("3.", page.url)

    page.go_forward()
    page.reload()
    expect(page).to_have_url(re.compile(r"/products$"))
    print("4.", page.url, "|", page.title())'''

NAV_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import com.microsoft.playwright.options.WaitUntilState;
import org.junit.jupiter.api.Test;
import java.util.regex.Pattern;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class NavigationTest {
  @Test
  void movingAroundTheShop(Page page) {
    page.navigate("/login", new Page.NavigateOptions().setWaitUntil(WaitUntilState.DOMCONTENTLOADED));
    System.out.println("1. " + page.url());

    page.getByLabel("Email").fill("asha@shop.example");
    page.getByLabel("Password").fill("s3cret");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in")).click();
    page.waitForURL("**/products");                 // the app moves on by itself
    System.out.println("2. " + page.url());

    page.goBack();
    assertThat(page).hasURL(Pattern.compile("/login$"));
    System.out.println("3. " + page.url());

    page.goForward();
    page.reload();
    assertThat(page).hasURL(Pattern.compile("/products$"));
    System.out.println("4. " + page.url() + " | " + page.title());
  }
}'''

# ---------- frames ----------
FRAME_TS = '''import { test, expect } from '@playwright/test';

test('pay inside the payment iframe', async ({ page }) => {
  await page.goto('/frames');
  const payment = page.frameLocator('iframe[title="Payment form"]');

  await payment.getByLabel('Card number').fill('4111 1111 1111 1111');
  await payment.getByLabel('Expiry').fill('12/29');
  await payment.getByRole('button', { name: 'Pay ₹219' }).click();

  // The message appears in the main page, outside the iframe.
  await expect(page.getByRole('status')).toHaveText('Paid with card ending 1111');
  console.log('Frames on the page:', page.frames().length);
});

test('a short card number is refused', async ({ page }) => {
  await page.goto('/frames');
  // Another way in: find the iframe element, then step into it.
  const payment = page.getByTitle('Payment form').contentFrame();
  await payment.getByLabel('Card number').fill('4111');
  await payment.getByRole('button', { name: 'Pay ₹219' }).click();
  await expect(payment.getByRole('alert')).toHaveText('Card number must have 16 digits');
});'''

FRAME_PY = '''from playwright.sync_api import Page, expect


def test_pay_inside_the_payment_iframe(page: Page):
    page.goto("/frames")
    payment = page.frame_locator('iframe[title="Payment form"]')

    payment.get_by_label("Card number").fill("4111 1111 1111 1111")
    payment.get_by_label("Expiry").fill("12/29")
    payment.get_by_role("button", name="Pay ₹219").click()

    # The message appears in the main page, outside the iframe.
    expect(page.get_by_role("status")).to_have_text("Paid with card ending 1111")
    print("Frames on the page:", len(page.frames))


def test_a_short_card_number_is_refused(page: Page):
    page.goto("/frames")
    # Another way in: find the iframe element, then step into it.
    payment = page.get_by_title("Payment form").content_frame
    payment.get_by_label("Card number").fill("4111")
    payment.get_by_role("button", name="Pay ₹219").click()
    expect(payment.get_by_role("alert")).to_have_text("Card number must have 16 digits")'''

FRAME_JAVA = '''package com.brainy;

import com.microsoft.playwright.FrameLocator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class FrameTest {
  @Test
  void payInsideThePaymentIframe(Page page) {
    page.navigate("/frames");
    FrameLocator payment = page.frameLocator("iframe[title=\\"Payment form\\"]");

    payment.getByLabel("Card number").fill("4111 1111 1111 1111");
    payment.getByLabel("Expiry").fill("12/29");
    payment.getByRole(AriaRole.BUTTON, new FrameLocator.GetByRoleOptions().setName("Pay ₹219")).click();

    // The message appears in the main page, outside the iframe.
    assertThat(page.getByRole(AriaRole.STATUS)).hasText("Paid with card ending 1111");
    System.out.println("Frames on the page: " + page.frames().size());
  }

  @Test
  void aShortCardNumberIsRefused(Page page) {
    page.navigate("/frames");
    // Another way in: find the iframe element, then step into it.
    FrameLocator payment = page.getByTitle("Payment form").contentFrame();
    payment.getByLabel("Card number").fill("4111");
    payment.getByRole(AriaRole.BUTTON, new FrameLocator.GetByRoleOptions().setName("Pay ₹219")).click();
    assertThat(payment.getByRole(AriaRole.ALERT)).hasText("Card number must have 16 digits");
  }
}'''

# ---------- dialogs ----------
DLG_TS = '''import { test, expect } from '@playwright/test';

test('with no handler, dialogs are dismissed', async ({ page }) => {
  await page.goto('/widgets');
  await page.getByRole('button', { name: 'Delete account' }).click();
  await expect(page.getByRole('status')).toHaveText('Kept your account');
});

test('accept a confirm and read its message', async ({ page }) => {
  await page.goto('/widgets');
  page.on('dialog', async dialog => {
    console.log(dialog.type(), '|', dialog.message());
    await dialog.accept();
  });
  await page.getByRole('button', { name: 'Delete account' }).click();
  await expect(page.getByRole('status')).toHaveText('Account deleted');
});

test('type an answer into a prompt', async ({ page }) => {
  await page.goto('/widgets');
  page.once('dialog', dialog => dialog.accept('Weekly shop'));
  await page.getByRole('button', { name: 'Rename list' }).click();
  await expect(page.getByRole('status')).toHaveText('List renamed to Weekly shop');
});'''

DLG_PY = '''from playwright.sync_api import Page, expect


def test_with_no_handler_dialogs_are_dismissed(page: Page):
    page.goto("/widgets")
    page.get_by_role("button", name="Delete account").click()
    expect(page.get_by_role("status")).to_have_text("Kept your account")


def test_accept_a_confirm_and_read_its_message(page: Page):
    page.goto("/widgets")

    def handle(dialog):
        print(dialog.type, "|", dialog.message)
        dialog.accept()

    page.on("dialog", handle)
    page.get_by_role("button", name="Delete account").click()
    expect(page.get_by_role("status")).to_have_text("Account deleted")


def test_type_an_answer_into_a_prompt(page: Page):
    page.goto("/widgets")
    page.once("dialog", lambda dialog: dialog.accept("Weekly shop"))
    page.get_by_role("button", name="Rename list").click()
    expect(page.get_by_role("status")).to_have_text("List renamed to Weekly shop")'''

DLG_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class DialogTest {
  @Test
  void withNoHandlerDialogsAreDismissed(Page page) {
    page.navigate("/widgets");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Delete account")).click();
    assertThat(page.getByRole(AriaRole.STATUS)).hasText("Kept your account");
  }

  @Test
  void acceptAConfirmAndReadItsMessage(Page page) {
    page.navigate("/widgets");
    page.onDialog(dialog -> {
      System.out.println(dialog.type() + " | " + dialog.message());
      dialog.accept();
    });
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Delete account")).click();
    assertThat(page.getByRole(AriaRole.STATUS)).hasText("Account deleted");
  }

  @Test
  void typeAnAnswerIntoAPrompt(Page page) {
    page.navigate("/widgets");
    page.onceDialog(dialog -> dialog.accept("Weekly shop"));
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Rename list")).click();
    assertThat(page.getByRole(AriaRole.STATUS)).hasText("List renamed to Weekly shop");
  }
}'''

# ---------- downloads ----------
DL_TS = '''import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

test('download the orders report', async ({ page }) => {
  await page.goto('/widgets');
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('link', { name: 'Download report' }).click();
  const download = await downloadPromise;

  console.log('File name:', download.suggestedFilename());
  const text = readFileSync(await download.path(), 'utf8');
  console.log(text.trim());
  expect(text.split('\\n')[0]).toBe('order,total');
  await download.saveAs('reports/' + download.suggestedFilename());   // keep a copy
});'''

DL_PY = '''from playwright.sync_api import Page


def test_download_the_orders_report(page: Page):
    page.goto("/widgets")
    with page.expect_download() as download_info:
        page.get_by_role("link", name="Download report").click()
    download = download_info.value

    print("File name:", download.suggested_filename)
    text = download.path().read_text()
    print(text.strip())
    assert text.split("\\n")[0] == "order,total"
    download.save_as("reports/" + download.suggested_filename)   # keep a copy'''

DL_JAVA = '''package com.brainy;

import com.microsoft.playwright.Download;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;
import java.nio.file.Files;
import java.nio.file.Paths;

import static org.junit.jupiter.api.Assertions.assertEquals;

@UsePlaywright(ShopOptions.class)
public class DownloadTest {
  @Test
  void downloadTheOrdersReport(Page page) throws Exception {
    page.navigate("/widgets");
    Download download = page.waitForDownload(() ->
        page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Download report")).click());

    System.out.println("File name: " + download.suggestedFilename());
    String text = Files.readString(download.path());
    System.out.println(text.trim());
    assertEquals("order,total", text.split("\\n")[0]);
    download.saveAs(Paths.get("reports", download.suggestedFilename()));   // keep a copy
  }
}'''

# ---------- uploads ----------
UP_TS = '''import { test, expect } from '@playwright/test';

test('send feedback with two screenshots', async ({ page }) => {
  await page.goto('/forms');
  await page.getByPlaceholder('Full name').fill('Asha');
  await page.getByLabel('Screenshots').setInputFiles([
    { name: 'cart.png', mimeType: 'image/png', buffer: Buffer.from('fake picture 1') },
    { name: 'error.png', mimeType: 'image/png', buffer: Buffer.from('fake picture 2') },
  ]);
  await page.getByRole('button', { name: 'Send feedback' }).click();
  await expect(page.getByRole('status')).toContainText('files: cart.png, error.png');
});'''

UP_PY = '''from playwright.sync_api import Page, expect


def test_send_feedback_with_two_screenshots(page: Page):
    page.goto("/forms")
    page.get_by_placeholder("Full name").fill("Asha")
    page.get_by_label("Screenshots").set_input_files([
        {"name": "cart.png", "mimeType": "image/png", "buffer": b"fake picture 1"},
        {"name": "error.png", "mimeType": "image/png", "buffer": b"fake picture 2"},
    ])
    page.get_by_role("button", name="Send feedback").click()
    expect(page.get_by_role("status")).to_contain_text("files: cart.png, error.png")'''

UP_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import com.microsoft.playwright.options.FilePayload;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class UploadTest {
  @Test
  void sendFeedbackWithTwoScreenshots(Page page) {
    page.navigate("/forms");
    page.getByPlaceholder("Full name").fill("Asha");
    page.getByLabel("Screenshots").setInputFiles(new FilePayload[] {
        new FilePayload("cart.png", "image/png", "fake picture 1".getBytes()),
        new FilePayload("error.png", "image/png", "fake picture 2".getBytes())});
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Send feedback")).click();
    assertThat(page.getByRole(AriaRole.STATUS)).containsText("files: cart.png, error.png");
  }
}'''

# ---------- events ----------
EV_TS = '''import { test, expect } from '@playwright/test';

test('catch console messages and page errors', async ({ page }) => {
  const messages: string[] = [];
  page.on('console', msg => messages.push(`${msg.type()}: ${msg.text()}`));
  page.on('request', request => {
    if (request.url().includes('/api/')) console.log('request ->', request.method(), request.url());
  });
  await page.goto('/widgets');

  const warning = page.waitForEvent('console', msg => msg.type() === 'warning');
  await page.getByRole('button', { name: 'Write to the console' }).click();
  await warning;
  console.log(messages);

  const pageError = page.waitForEvent('pageerror');
  await page.getByRole('button', { name: 'Break the page' }).click();
  console.log('Page error:', (await pageError).message);
});'''

EV_JS = EV_TS.replace('const messages: string[] = [];', 'const messages = [];')

EV_PY = '''from playwright.sync_api import Page


def test_catch_console_messages_and_page_errors(page: Page):
    messages = []
    page.on("console", lambda msg: messages.append(f"{msg.type}: {msg.text}"))
    page.on("request", lambda request: print("request ->", request.method, request.url)
            if "/api/" in request.url else None)
    page.goto("/widgets")

    with page.expect_console_message(lambda msg: msg.type == "warning"):
        page.get_by_role("button", name="Write to the console").click()
    print(messages)

    with page.expect_event("pageerror") as error_info:
        page.get_by_role("button", name="Break the page").click()
    print("Page error:", error_info.value.message)'''

EV_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;
import java.util.ArrayList;
import java.util.List;

@UsePlaywright(ShopOptions.class)
public class EventsTest {
  @Test
  void catchConsoleMessagesAndPageErrors(Page page) {
    List<String> messages = new ArrayList<>();
    List<String> errors = new ArrayList<>();
    page.onConsoleMessage(msg -> messages.add(msg.type() + ": " + msg.text()));
    page.onPageError(errors::add);
    page.onRequest(request -> {
      if (request.url().contains("/api/")) System.out.println("request -> " + request.method() + " " + request.url());
    });
    page.navigate("/widgets");

    page.waitForConsoleMessage(new Page.WaitForConsoleMessageOptions().setPredicate(m -> m.type().equals("warning")),
        () -> page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Write to the console")).click());
    System.out.println(messages);

    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Break the page")).click();
    page.waitForCondition(() -> !errors.isEmpty());
    System.out.println("Page error: " + errors.get(0));
  }
}'''

# ---------- running code in the page ----------
EVAL_TS = '''import { test, expect } from '@playwright/test';

test('run code inside the page', async ({ page }) => {
  // Runs in the page before any of its own scripts, on every navigation.
  await page.addInitScript(() => { (window as any).testMode = true; });
  await page.goto('/products');
  await expect(page.getByRole('listitem')).toHaveCount(5);   // wait for the list

  const info = await page.evaluate(() => ({
    title: document.title,
    cards: document.querySelectorAll('li.card').length,
    testMode: (window as any).testMode,
  }));
  console.log(info);

  const sum = await page.evaluate(([a, b]) => a + b, [20, 199]);   // pass values in
  console.log('sum =', sum);

  const tag = await page.getByPlaceholder('Search products').evaluate(el => el.tagName);
  console.log('tag =', tag);
});'''

EVAL_JS = EVAL_TS.replace('(window as any)', 'window')

EVAL_PY = '''from playwright.sync_api import Page, expect


def test_run_code_inside_the_page(page: Page):
    # Runs in the page before any of its own scripts, on every navigation.
    page.add_init_script("window.testMode = true")
    page.goto("/products")
    expect(page.get_by_role("listitem")).to_have_count(5)   # wait for the list

    info = page.evaluate("""() => ({
        title: document.title,
        cards: document.querySelectorAll('li.card').length,
        testMode: window.testMode,
    })""")
    print(info)

    total = page.evaluate("([a, b]) => a + b", [20, 199])   # pass values in
    print("sum =", total)

    tag = page.get_by_placeholder("Search products").evaluate("el => el.tagName")
    print("tag =", tag)'''

EVAL_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;
import java.util.List;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class EvaluateTest {
  @Test
  void runCodeInsideThePage(Page page) {
    // Runs in the page before any of its own scripts, on every navigation.
    page.addInitScript("window.testMode = true");
    page.navigate("/products");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(5);   // wait for the list

    Object info = page.evaluate("() => ({" +
        " title: document.title," +
        " cards: document.querySelectorAll('li.card').length," +
        " testMode: window.testMode })");
    System.out.println(info);

    Object sum = page.evaluate("([a, b]) => a + b", List.of(20, 199));   // pass values in
    System.out.println("sum = " + sum);

    Object tag = page.getByPlaceholder("Search products").evaluate("el => el.tagName");
    System.out.println("tag = " + tag);
  }
}'''

# ---------- shadow DOM ----------
SH_TS = '''import { test, expect } from '@playwright/test';

test('vote inside a shadow DOM component', async ({ page }) => {
  await page.goto('/shadow');
  const ashaReview = page.locator('review-card').filter({ hasText: 'Asha' });

  // getByRole and CSS look inside open shadow roots by themselves.
  await ashaReview.getByRole('button', { name: 'Helpful' }).click();
  await expect(ashaReview.getByText('found this helpful')).toHaveText('1 person found this helpful');

  console.log('CSS sees the buttons:', await page.locator('review-card button').count());
  console.log('XPath sees the buttons:', await page.locator('//review-card//button').count());
});'''

SH_PY = '''from playwright.sync_api import Page, expect


def test_vote_inside_a_shadow_dom_component(page: Page):
    page.goto("/shadow")
    asha_review = page.locator("review-card").filter(has_text="Asha")

    # get_by_role and CSS look inside open shadow roots by themselves.
    asha_review.get_by_role("button", name="Helpful").click()
    expect(asha_review.get_by_text("found this helpful")).to_have_text("1 person found this helpful")

    print("CSS sees the buttons:", page.locator("review-card button").count())
    print("XPath sees the buttons:", page.locator("//review-card//button").count())'''

SH_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class ShadowTest {
  @Test
  void voteInsideAShadowDomComponent(Page page) {
    page.navigate("/shadow");
    Locator ashaReview = page.locator("review-card").filter(new Locator.FilterOptions().setHasText("Asha"));

    // getByRole and CSS look inside open shadow roots by themselves.
    ashaReview.getByRole(AriaRole.BUTTON, new Locator.GetByRoleOptions().setName("Helpful")).click();
    assertThat(ashaReview.getByText("found this helpful")).hasText("1 person found this helpful");

    System.out.println("CSS sees the buttons: " + page.locator("review-card button").count());
    System.out.println("XPath sees the buttons: " + page.locator("//review-card//button").count());
  }
}'''

CODES = {
    'nav': four('Go, wait for the address, go back and reload',
                java=jv({'NavigationTest.java': NAV_JAVA}),
                py=py({'test_navigation.py': NAV_PY}, cmd='pytest -v -s'),
                js=js({'navigation.spec.js': NAV_TS}),
                ts=ts({'navigation.spec.ts': NAV_TS}),
                result='After the click, the shop changes the address with its own script, so the test waits for the new URL with <code>waitForURL</code>. Back, forward and reload work like the browser buttons. The checks on the URL use a regular expression so they do not depend on the port.'),
    'frame': four('Fill a card form that lives inside an iframe',
                  java=jv({'FrameTest.java': FRAME_JAVA}),
                  py=py({'test_frames.py': FRAME_PY}, cmd='pytest -v -s'),
                  js=js({'frames.spec.js': FRAME_TS}),
                  ts=ts({'frames.spec.ts': FRAME_TS}),
                  result='<code>frameLocator</code> and <code>contentFrame()</code> both give you a way into the iframe, and every locator after it searches only inside. The page has two frames: the main page and the payment iframe.'),
    'dialog': four('Alerts, confirms and prompts',
                   java=jv({'DialogTest.java': DLG_JAVA}),
                   py=py({'test_dialogs.py': DLG_PY}, cmd='pytest -v -s'),
                   js=js({'dialogs.spec.js': DLG_TS}),
                   ts=ts({'dialogs.spec.ts': DLG_TS}),
                   result='With no handler, Playwright dismisses every dialog so the test never hangs, which is why the first test sees <b>Kept your account</b>. A handler can read the type and the message, then accept, dismiss, or type an answer into a prompt.'),
    'download': four('Catch a download and read the file',
                     java=jv({'DownloadTest.java': DL_JAVA}),
                     py=py({'test_download.py': DL_PY}, cmd='pytest -v -s'),
                     js=js({'download.spec.js': DL_TS}),
                     ts=ts({'download.spec.ts': DL_TS}),
                     result='The browser saved the file in a temporary folder that Playwright deletes when the context closes. <code>suggestedFilename</code> is the name the server asked for, and <code>saveAs</code> keeps a copy where you want it.'),
    'upload': four('Upload files without touching the disk',
                   java=jv({'UploadTest.java': UP_JAVA}),
                   py=py({'test_upload.py': UP_PY}),
                   js=js({'upload.spec.js': UP_TS}),
                   ts=ts({'upload.spec.ts': UP_TS}),
                   result='<code>setInputFiles</code> fills a file input directly. Here the files are made in memory, so the test needs no sample files. You can also pass real file paths, and an empty list clears the input.'),
    'events': four('Listen to console messages, page errors and requests',
                   java=jv({'EventsTest.java': EV_JAVA}),
                   py=py({'test_events.py': EV_PY}, cmd='pytest -v -s'),
                   js=js({'events.spec.js': EV_JS}),
                   ts=ts({'events.spec.ts': EV_TS}),
                   result='The page wrote one log and one warning, then threw an error that nothing caught. A test can fail on any page error, which catches broken JavaScript that the screen does not show. The widgets page makes no API calls, so the request listener printed nothing. In Java the error arrives as text that includes the stack trace, while JavaScript and Python give an error object with a <code>message</code>.'),
    'eval': four('Run JavaScript inside the page',
                 java=jv({'EvaluateTest.java': EVAL_JAVA}),
                 py=py({'test_evaluate.py': EVAL_PY}, cmd='pytest -v -s'),
                 js=js({'evaluate.spec.js': EVAL_JS}),
                 ts=ts({'evaluate.spec.ts': EVAL_TS}),
                 result='The function runs in the browser and its result comes back to your language: a JavaScript object becomes a dictionary in Python and a Map in Java. Values travel in as an argument, because the function cannot see the variables of your test.'),
    'shadow': four('Click a button inside a shadow DOM component',
                   java=jv({'ShadowTest.java': SH_JAVA}),
                   py=py({'test_shadow.py': SH_PY}, cmd='pytest -v -s'),
                   js=js({'shadow.spec.js': SH_TS}),
                   ts=ts({'shadow.spec.ts': SH_TS}),
                   result='Playwright locators go into open shadow roots with no extra work. XPath does not, which is one more reason to prefer role, text and CSS locators.'),
    'walkframe': walk('Paying inside an iframe', [
        step('Open the checkout page. The card form is an iframe from the payment company.', "await page.goto('http://localhost:4173/frames');", 'page.goto("http://localhost:4173/frames")', 'page.navigate("http://localhost:4173/frames");'),
        step('Step into the iframe and type the card number.', "await page.frameLocator('iframe[title=\"Payment form\"]').getByLabel('Card number').fill('4111 1111 1111 1111');",
             'page.frame_locator(\'iframe[title="Payment form"]\').get_by_label("Card number").fill("4111 1111 1111 1111")',
             'page.frameLocator("iframe[title=\\"Payment form\\"]").getByLabel("Card number").fill("4111 1111 1111 1111");'),
        step('Type the expiry date.', "await page.frameLocator('iframe[title=\"Payment form\"]').getByLabel('Expiry').fill('12/29');",
             'page.frame_locator(\'iframe[title="Payment form"]\').get_by_label("Expiry").fill("12/29")',
             'page.frameLocator("iframe[title=\\"Payment form\\"]").getByLabel("Expiry").fill("12/29");'),
        step('Click Pay inside the iframe.', "await page.frameLocator('iframe[title=\"Payment form\"]').getByRole('button', { name: 'Pay ₹219' }).click();",
             'page.frame_locator(\'iframe[title="Payment form"]\').get_by_role("button", name="Pay ₹219").click()',
             'page.frameLocator("iframe[title=\\"Payment form\\"]").getByRole(AriaRole.BUTTON, new FrameLocator.GetByRoleOptions().setName("Pay ₹219")).click();'),
        step('Back in the main page, the shop shows the result.', "await expect(page.getByRole('status')).toHaveText('Paid with card ending 1111');",
             'expect(page.get_by_role("status")).to_have_text("Paid with card ending 1111")', 'assertThat(page.getByRole(AriaRole.STATUS)).hasText("Paid with card ending 1111");'),
    ], size=(900, 560)),
}

DG = {
    'load': {'t': 'What goto waits for', 'w': 900, 'h': 200,
             'n': [['go', 20, 70, 120, 60, 'goto(url)', {'c': 5, 'sh': 'pill'}], ['commit', 170, 70, 150, 60, 'commit', {'c': 3, 'sub': 'the answer starts', 'i': 'The server started sending the page.'}],
                   ['dcl', 350, 70, 170, 60, 'domcontentloaded', {'c': 2, 'sub': 'HTML is read', 'i': 'The HTML is parsed and deferred scripts ran. Images may still load.'}],
                   ['load', 550, 70, 140, 60, 'load', {'c': 1, 'sub': 'the default', 'i': 'Images, styles and scripts of the page have loaded.'}],
                   ['idle', 720, 70, 160, 60, 'networkidle', {'c': 0, 'sub': 'not recommended', 'i': 'No network traffic for 500 ms. Pages with polling never reach it, so prefer a check on what you need.'}]],
             'e': [['go', 'commit'], ['commit', 'dcl'], ['dcl', 'load'], ['load', 'idle']],
             'st': [[['go', 'commit', 'go>commit'], 'goto sends the request and can return as soon as the answer starts, with waitUntil commit.'],
                    [['dcl', 'commit>dcl'], 'domcontentloaded: the HTML is ready. Good for slow pages with many images.'],
                    [['load', 'dcl>load'], 'load is the default. Everything the page needs has loaded.'],
                    [['idle', 'load>idle'], 'networkidle waits for 500 ms of silence. It is slow and unreliable, so check the element you need instead.']]},
}

PARTS = [
    part('navigate', '🧭', 'Going to pages and waiting for them', f'''
<p><code>{by(java='page.navigate(url)', py='page.goto(url)', js='page.goto(url)')}</code> opens an address and waits until the page has loaded. You can say how far it should wait with the <code>waitUntil</code> option.</p>
<div class="viz" data-viz="flow" data-k="load"></div>
<p>A relative address such as <code>/login</code> is joined to the base URL from the config. Many pages also move on by themselves after a click, for example after signing in. Then you wait for the new address.</p>
[[nav]]
{tip('Do not wait for the network to go quiet. A chat widget or analytics script can keep it busy forever. Wait for what the user is waiting for: a URL, a heading or a message. Every check with expect already waits.', 'warn')}
''', easy=True, kw=['goto', 'navigate', 'waitUntil', 'waitForURL', 'goBack', 'reload', 'toHaveURL']),

    part('frames', '🖼️', 'Iframes', f'''
<p>An iframe is a web page inside a web page. Payment forms, maps, videos and chat windows often live in iframes, because another company serves them. A locator on the main page does not see inside an iframe, so you step into it first.</p>
[[walkframe]]
[[frame]]
{tip('Most real payment iframes come from another domain. Playwright handles that the same way, which older tools could not do easily. In tests, many teams use the payment company test card numbers, such as 4111 1111 1111 1111, in their sandbox.', 'life')}
''', easy=True, kw=['iframe', 'frameLocator', 'contentFrame', 'frames', 'payment form']),

    part('dialogs', '💬', 'Alerts, confirms and prompts', f'''
<p>Browser dialogs stop the page until someone answers. Playwright answers for you: with no handler, it dismisses them. To accept or to type an answer, register a handler <b>before</b> the click that opens the dialog.</p>
[[dialog]]
{table(['Dialog', 'Opened by', 'accept()', 'dismiss()'], [
    ['alert', '<code>alert(msg)</code>', 'closes it', 'closes it'],
    ['confirm', '<code>confirm(msg)</code>', 'the page gets true', 'the page gets false'],
    ['prompt', '<code>prompt(msg, default)</code>', 'the page gets your text', 'the page gets null'],
    ['beforeunload', 'leaving a page with unsaved changes', 'leave the page', 'stay on the page'],
])}
''', kw=['dialog', 'alert', 'confirm', 'prompt', 'accept', 'dismiss', 'onDialog']),

    part('files', '📁', 'Downloads and uploads', f'''
<p>A download is an event, like a popup. Start waiting first, then click, then use the download object.</p>
[[download]]
<p>For uploads, put the files straight into the file input. You never deal with the operating system file window.</p>
[[upload]]
{tip('Some pages hide the real file input and open the file window from a pretty button. Then wait for the file chooser event: <code>page.waitForEvent(\'filechooser\')</code> in JavaScript, <code>page.expect_file_chooser()</code> in Python or <code>page.waitForFileChooser(...)</code> in Java, and call <code>setFiles</code> on it.', 'tip')}
''', kw=['download', 'upload', 'setInputFiles', 'suggestedFilename', 'saveAs', 'file chooser']),

    part('events', '📡', 'Listening to what the page does', f'''
<p>A page fires events while you test it: console messages, uncaught errors, network requests and responses, new popups, dialogs and downloads. Listening to them lets a test notice problems the screen does not show.</p>
[[events]]
{table(['Event', 'Tells you', 'Typical use'], [
    ['console', 'a message the page logged', 'fail on <code>console.error</code>, debug a test'],
    ['pageerror', 'an error nothing caught', 'fail the test on broken JavaScript'],
    ['request and response', 'every network call', 'check an API was called, count calls'],
    ['popup, download, dialog', 'a new tab, a file, a dialog', 'handle it in the test'],
    ['close, crash', 'the page closed or crashed', 'clean up, report a crash'],
])}
{tip('Many companies add one shared fixture that collects page errors and fails any test that had one. It finds JavaScript bugs on pages nobody wrote a check for.', 'pro')}
''', kw=['events', 'console', 'pageerror', 'request', 'response', 'listener']),

    part('evaluate', '🧪', 'Running code inside the page', f'''
<p>Sometimes you need something the page knows but does not show: a value in storage, a count, a computed style. <code>evaluate</code> runs a JavaScript function inside the page and brings the result back to your language. <code>addInitScript</code> runs code before the page's own scripts, which is useful to set a flag or fake something before the app starts.</p>
[[eval]]
{tip('Use evaluate to read and to prepare, not to click. A click done with JavaScript skips the waiting and the visibility checks that make Playwright tests reliable, and it can pass on a button a real user could never press.', 'warn')}
''', kw=['evaluate', 'addInitScript', 'javascript', 'evaluateHandle']),

    part('shadow', '🌑', 'Shadow DOM and web components', f'''
<p>Web components hide their insides in a shadow root, so <code>document.querySelector</code> cannot find them. Design systems such as Salesforce Lightning and many company component libraries use them. Playwright locators look inside open shadow roots automatically.</p>
[[shadow]]
''', kw=['shadow dom', 'web components', 'custom element', 'xpath']),
]

INFO = {'title': 'Everything a page can throw at you', 'panels': [
    panel([['e', '🧭'], ['t', 'waitForURL', {'b': 1}]], 'Navigation', 'goto waits for load.', 'After a click, wait for the new URL.'),
    panel([['e', '🖼️'], ['t', 'frameLocator', {'b': 1}]], 'Iframes', 'Step in first.', 'Then locate as usual.'),
    panel([['e', '💬'], ['t', 'dialog.accept()', {'b': 1}]], 'Dialogs', 'Dismissed by default.', 'Handle them before the click.'),
    panel([['e', '📁'], ['t', 'setInputFiles', {'b': 1}]], 'Files', 'Wait for downloads.', 'Fill file inputs directly.')],
    'remember': 'Start waiting before the click for anything the click creates: a new URL, a popup, a dialog or a download.'}

REAL = [
    ['💳', 'Payment testing', 'A shop checks every release that a test card pays inside the payment iframe and that a short card number is refused with the right message.'],
    ['📊', 'Monthly reports', 'An admin portal test downloads the monthly CSV report, reads it, and checks that the totals match the numbers on the screen.'],
    ['🐞', 'A hidden JavaScript error', 'A shared fixture fails any test that had a page error. It found a broken coupon script on a page that no test checked directly.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers navigation and waiting for pages, iframes, dialogs, downloads and uploads, page events, running code in the page, and shadow DOM.',
        'यह अध्याय navigation और pages का इंतज़ार, iframes, dialogs, downloads और uploads, page events, page में code चलाना और shadow DOM समझाता है।',
        'ಈ ಅಧ್ಯಾಯ navigation ಮತ್ತು pages ಗಾಗಿ ಕಾಯುವುದು, iframes, dialogs, downloads ಮತ್ತು uploads, page events, page ನಲ್ಲಿ code ನಡೆಸುವುದು ಮತ್ತು shadow DOM ವಿವರಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ navigation ଓ pages ପାଇଁ ଅପେକ୍ଷା, iframes, dialogs, downloads ଓ uploads, page events, page ରେ code ଚଳାଇବା ଏବଂ shadow DOM ବୁଝାଏ।',
        'يغطي هذا الفصل التنقل وانتظار الصفحات والإطارات المضمنة ومربعات الحوار والتنزيلات والرفع وأحداث الصفحة وتشغيل الشيفرة داخل الصفحة وshadow DOM.',
        'Dieses Kapitel behandelt Navigation und das Warten auf Seiten, Iframes, Dialoge, Downloads und Uploads, Seitenereignisse, Code in der Seite ausführen und Shadow DOM.'),
    say('navigate', 'Navigation', 'goto opens an address and waits for the load event by default. When the app moves to a new page after a click, wait for the new URL. Avoid waiting for the network to go quiet.',
        'goto एक address खोलता है और default रूप से load event का इंतज़ार करता है। Click के बाद app नए page पर जाए तो नए URL का इंतज़ार करें। Network के शांत होने का इंतज़ार न करें।',
        'goto ಒಂದು address ತೆರೆಯುತ್ತದೆ ಮತ್ತು default ಆಗಿ load event ಗಾಗಿ ಕಾಯುತ್ತದೆ. Click ನಂತರ app ಹೊಸ page ಗೆ ಹೋದರೆ ಹೊಸ URL ಗಾಗಿ ಕಾಯಿರಿ. Network ಶಾಂತವಾಗುವುದಕ್ಕೆ ಕಾಯಬೇಡಿ.',
        'goto ଏକ address ଖୋଲେ ଏବଂ default ଭାବେ load event ପାଇଁ ଅପେକ୍ଷା କରେ। Click ପରେ app ନୂଆ page କୁ ଗଲେ ନୂଆ URL ପାଇଁ ଅପେକ୍ଷା କରନ୍ତୁ। Network ଶାନ୍ତ ହେବା ପାଇଁ ଅପେକ୍ଷା କରନ୍ତୁ ନାହିଁ।',
        'يفتح goto عنوانًا وينتظر حدث التحميل افتراضيًا. عندما ينتقل التطبيق إلى صفحة جديدة بعد نقرة، انتظر العنوان الجديد. تجنب انتظار هدوء الشبكة.',
        'goto öffnet eine Adresse und wartet standardmäßig auf das Load-Ereignis. Wenn die App nach einem Klick zu einer neuen Seite wechselt, warte auf die neue URL. Warte nicht darauf, dass das Netzwerk ruhig wird.'),
    say('frames', 'Iframes', 'An iframe is a page inside a page, such as a payment form. Step into it with frame locator or content frame, then use locators as usual. The result may appear in the main page.',
        'Iframe एक page के अंदर दूसरा page है, जैसे payment form। frame locator या content frame से उसमें जाएँ, फिर सामान्य locators इस्तेमाल करें। नतीजा main page में दिख सकता है।',
        'Iframe ಎಂದರೆ page ಒಳಗಿನ page, ಉದಾಹರಣೆಗೆ payment form. frame locator ಅಥವಾ content frame ಮೂಲಕ ಒಳಗೆ ಹೋಗಿ ನಂತರ ಸಾಮಾನ್ಯ locators ಬಳಸಿ. ಫಲಿತಾಂಶ main page ನಲ್ಲಿ ಕಾಣಬಹುದು.',
        'Iframe ହେଉଛି page ଭିତରେ page, ଯେପରି payment form। frame locator ବା content frame ଦ୍ୱାରା ଭିତରକୁ ଯାଆନ୍ତୁ, ତାପରେ ସାଧାରଣ locators ବ୍ୟବହାର କରନ୍ତୁ। ଫଳାଫଳ main page ରେ ଦେଖାଯାଇପାରେ।',
        'الإطار المضمن صفحة داخل صفحة مثل نموذج الدفع. ادخل إليه باستخدام frame locator أو content frame ثم استخدم المحددات كالمعتاد. قد تظهر النتيجة في الصفحة الرئيسية.',
        'Ein Iframe ist eine Seite in einer Seite, etwa ein Zahlungsformular. Gehe mit frame locator oder content frame hinein und nutze dann Locators wie gewohnt. Das Ergebnis kann in der Hauptseite erscheinen.'),
    say('dialogs', 'Dialogs', 'Without a handler Playwright dismisses alerts, confirms and prompts. Register a dialog handler before the click to read the message, accept, dismiss or type an answer.',
        'Handler के बिना Playwright alerts, confirms और prompts को dismiss करता है। संदेश पढ़ने, accept, dismiss या जवाब लिखने के लिए click से पहले dialog handler लगाएँ।',
        'Handler ಇಲ್ಲದಿದ್ದರೆ Playwright alerts, confirms ಮತ್ತು prompts ಅನ್ನು dismiss ಮಾಡುತ್ತದೆ. ಸಂದೇಶ ಓದಲು, accept, dismiss ಅಥವಾ ಉತ್ತರ ಬರೆಯಲು click ಗಿಂತ ಮೊದಲು dialog handler ಸೇರಿಸಿ.',
        'Handler ବିନା Playwright alerts, confirms ଓ prompts କୁ dismiss କରେ। ସନ୍ଦେଶ ପଢ଼ିବା, accept, dismiss ବା ଉତ୍ତର ଲେଖିବା ପାଇଁ click ପୂର୍ବରୁ dialog handler ଯୋଡନ୍ତୁ।',
        'بدون معالج يرفض Playwright التنبيهات والتأكيدات والمطالبات. سجّل معالج الحوار قبل النقر لقراءة الرسالة أو القبول أو الرفض أو كتابة إجابة.',
        'Ohne Handler schließt Playwright Alerts, Bestätigungen und Eingabeaufforderungen ab. Registriere vor dem Klick einen Dialog-Handler, um die Nachricht zu lesen, anzunehmen, abzulehnen oder eine Antwort einzugeben.'),
    say('files', 'Downloads and uploads', 'Wait for the download event before the click, then read the file or save a copy. For uploads, fill the file input directly with real paths or files made in memory.',
        'Click से पहले download event का इंतज़ार शुरू करें, फिर file पढ़ें या copy सेव करें। Uploads के लिए file input में सीधे असली paths या memory में बनी files भरें।',
        'Click ಗಿಂತ ಮೊದಲು download event ಗಾಗಿ ಕಾಯಿರಿ, ನಂತರ file ಓದಿ ಅಥವಾ copy ಉಳಿಸಿ. Uploads ಗೆ file input ನಲ್ಲಿ ನೇರವಾಗಿ ನಿಜವಾದ paths ಅಥವಾ memory ಯಲ್ಲಿ ಮಾಡಿದ files ತುಂಬಿ.',
        'Click ପୂର୍ବରୁ download event ପାଇଁ ଅପେକ୍ଷା କରନ୍ତୁ, ତାପରେ file ପଢ଼ନ୍ତୁ ବା copy ସେଭ୍ କରନ୍ତୁ। Uploads ପାଇଁ file input ରେ ସିଧାସଳଖ ପ୍ରକୃତ paths ବା memory ରେ ତିଆରି files ଭରନ୍ତୁ।',
        'انتظر حدث التنزيل قبل النقر ثم اقرأ الملف أو احفظ نسخة. للرفع املأ حقل الملف مباشرة بمسارات حقيقية أو بملفات منشأة في الذاكرة.',
        'Warte vor dem Klick auf das Download-Ereignis, lies dann die Datei oder speichere eine Kopie. Für Uploads füllst du das Dateifeld direkt mit echten Pfaden oder im Speicher erzeugten Dateien.'),
    say('events', 'Page events', 'Pages fire console, page error, request, response, popup, download and dialog events. Listening to them lets a test catch JavaScript errors that the screen does not show.',
        'Pages console, page error, request, response, popup, download और dialog events भेजते हैं। इन्हें सुनकर टेस्ट वे JavaScript errors पकड़ सकता है जो screen पर नहीं दिखते।',
        'Pages console, page error, request, response, popup, download ಮತ್ತು dialog events ಕಳುಹಿಸುತ್ತವೆ. ಇವುಗಳನ್ನು ಕೇಳುವುದರಿಂದ screen ನಲ್ಲಿ ಕಾಣದ JavaScript errors ಅನ್ನು ಟೆಸ್ಟ್ ಹಿಡಿಯಬಹುದು.',
        'Pages console, page error, request, response, popup, download ଓ dialog events ପଠାନ୍ତି। ଏଗୁଡ଼ିକୁ ଶୁଣି ଟେଷ୍ଟ screen ରେ ନ ଦେଖାଯାଉଥିବା JavaScript errors ଧରିପାରେ।',
        'تطلق الصفحات أحداث console وpage error وrequest وresponse وpopup وdownload وdialog. الاستماع إليها يتيح للاختبار التقاط أخطاء JavaScript التي لا تظهر على الشاشة.',
        'Seiten feuern Ereignisse für Konsole, Seitenfehler, Anfragen, Antworten, Pop-ups, Downloads und Dialoge. Wer zuhört, findet JavaScript-Fehler, die der Bildschirm nicht zeigt.'),
    say('evaluate', 'Running code in the page', 'evaluate runs a JavaScript function inside the page and returns the result to your language. add init script runs before the page scripts. Use them to read and prepare, not to click.',
        'evaluate page के अंदर JavaScript function चलाकर नतीजा आपकी भाषा में लौटाता है। add init script page scripts से पहले चलता है। इन्हें पढ़ने और तैयारी के लिए इस्तेमाल करें, click के लिए नहीं।',
        'evaluate page ಒಳಗೆ JavaScript function ನಡೆಸಿ ಫಲಿತಾಂಶವನ್ನು ನಿಮ್ಮ ಭಾಷೆಗೆ ಹಿಂದಿರುಗಿಸುತ್ತದೆ. add init script page scripts ಗಿಂತ ಮೊದಲು ನಡೆಯುತ್ತದೆ. ಓದಲು ಮತ್ತು ತಯಾರಿಗೆ ಬಳಸಿ, click ಗೆ ಅಲ್ಲ.',
        'evaluate page ଭିତରେ JavaScript function ଚଳାଇ ଫଳାଫଳ ଆପଣଙ୍କ ଭାଷାକୁ ଫେରାଏ। add init script page scripts ପୂର୍ବରୁ ଚାଲେ। ପଢ଼ିବା ଓ ପ୍ରସ୍ତୁତି ପାଇଁ ବ୍ୟବହାର କରନ୍ତୁ, click ପାଇଁ ନୁହେଁ।',
        'يشغّل evaluate دالة JavaScript داخل الصفحة ويعيد النتيجة إلى لغتك. يعمل add init script قبل سكربتات الصفحة. استخدمهما للقراءة والتحضير وليس للنقر.',
        'evaluate führt eine JavaScript-Funktion in der Seite aus und gibt das Ergebnis an deine Sprache zurück. add init script läuft vor den Skripten der Seite. Nutze beides zum Lesen und Vorbereiten, nicht zum Klicken.'),
    say('shadow', 'Shadow DOM', 'Web components hide their insides in a shadow root. Playwright role, text and CSS locators look inside open shadow roots automatically. XPath does not.',
        'Web components अपने अंदर का हिस्सा shadow root में छिपाते हैं। Playwright के role, text और CSS locators open shadow roots के अंदर अपने आप देखते हैं। XPath नहीं देखता।',
        'Web components ತಮ್ಮ ಒಳಭಾಗವನ್ನು shadow root ನಲ್ಲಿ ಮರೆಮಾಡುತ್ತವೆ. Playwright role, text ಮತ್ತು CSS locators open shadow roots ಒಳಗೆ ತಾನಾಗಿಯೇ ನೋಡುತ್ತವೆ. XPath ನೋಡುವುದಿಲ್ಲ.',
        'Web components ନିଜ ଭିତର ଭାଗକୁ shadow root ରେ ଲୁଚାନ୍ତି। Playwright role, text ଓ CSS locators open shadow roots ଭିତରେ ନିଜେ ଦେଖନ୍ତି। XPath ଦେଖେ ନାହିଁ।',
        'تخفي مكونات الويب أجزاءها الداخلية في shadow root. محددات Playwright للدور والنص وCSS تبحث داخل جذور الظل المفتوحة تلقائيًا، أما XPath فلا.',
        'Web Components verstecken ihr Inneres in einem Shadow Root. Rollen-, Text- und CSS-Locators von Playwright schauen automatisch in offene Shadow Roots. XPath nicht.'),
    say('practice', 'Playground labs', 'In the labs you pay inside the payment iframe and you accept a confirm dialog to delete an account.',
        'Labs में आप payment iframe के अंदर भुगतान करते हैं और account हटाने के लिए confirm dialog accept करते हैं।',
        'Labs ನಲ್ಲಿ ನೀವು payment iframe ಒಳಗೆ ಪಾವತಿಸುತ್ತೀರಿ ಮತ್ತು account ಅಳಿಸಲು confirm dialog accept ಮಾಡುತ್ತೀರಿ.',
        'Labs ରେ ଆପଣ payment iframe ଭିତରେ ପେମେଣ୍ଟ କରନ୍ତି ଏବଂ account ହଟାଇବା ପାଇଁ confirm dialog accept କରନ୍ତି।',
        'في المختبرات تدفع داخل إطار الدفع المضمن وتقبل مربع تأكيد لحذف حساب.',
        'In den Labs bezahlst du im Zahlungs-Iframe und bestätigst einen Dialog, um ein Konto zu löschen.'),
]

QUIZ = [
    quiz(1, 'What does goto wait for by default?', ['commit', 'domcontentloaded', 'load', 'networkidle'], 2,
         'It is the classic page load event.', 'By default <code>goto</code> waits for the <code>load</code> event.'),
    quiz(1, 'A payment form lives in an iframe. How do you reach its Card number box?', ['page.getByLabel directly', 'Step in with frameLocator or contentFrame, then getByLabel', 'Use evaluate', 'It cannot be reached'], 1,
         'Locators on the main page do not see inside iframes.', 'Step into the iframe first, then locate inside it.'),
    quiz(1, 'What does Playwright do with a confirm dialog if the test has no handler?', ['Accepts it', 'Dismisses it', 'Waits forever', 'Fails the test'], 1,
         'Look at the first dialog test.', 'Dialogs are dismissed by default so a test never hangs. The page got false and showed Kept your account.'),
    quiz(1, 'Which call puts files into a file input?', ['fill', 'setInputFiles', 'upload', 'type'], 1,
         'It sets the files of an input.', '<code>setInputFiles</code> (or <code>set_input_files</code>) fills the input with paths or in memory files.'),
    quiz(2, 'Why start waiting for a download before the click?', ['It is required by Java', 'So the event cannot fire before you listen', 'Downloads are slow', 'To rename the file'], 1,
         'The click can be very fast.', 'If the download starts before you listen, you miss the event and the test times out.'),
    quiz(2, 'After signing in, the app moves to /products by itself. What should the test do?', ['Sleep 2 seconds', 'waitForURL(\'**/products\') or check toHaveURL', 'Call goto again', 'Nothing'], 1,
         'Wait for what the user waits for.', 'Wait for the URL. A check such as <code>toHaveURL</code> also waits.'),
    quiz(2, 'Why is waitUntil networkidle not recommended?', ['It is too fast', 'Pages with polling or analytics may never go quiet, and it is slow', 'It only works in Java', 'It skips scripts'], 1,
         'Think of a chat widget.', 'Networkidle waits for 500 ms of no traffic, which some pages never reach. Check the element you need instead.'),
    quiz(2, 'How does a test notice an uncaught JavaScript error on the page?', ['It cannot', 'Listen to the pageerror event', 'Read the title', 'Use goBack'], 1,
         'The event is named after it.', 'The <code>pageerror</code> event fires for every error that nothing in the page caught.'),
    quiz(2, 'In Python, how do you catch a download?', ['page.on_download()', 'with page.expect_download() as info:', 'page.download()', 'page.wait_download()'], 1,
         'Python uses a with block.', 'The <code>expect_download</code> block waits around the click, and <code>info.value</code> is the download.'),
    quiz(3, 'Why should you not click buttons with evaluate?', ['It is slower', 'It skips the actionability checks, so a button a user cannot press can still be clicked', 'It does not work in Java', 'It opens dialogs'], 1,
         'What does a real click check first?', 'Playwright clicks check visibility, stability and that nothing covers the element. A JavaScript click checks none of that.'),
    quiz(3, 'Which locator does NOT go into a shadow root?', ['getByRole', 'CSS', 'XPath', 'getByText'], 2,
         'Look at the shadow DOM output.', 'Role, text and CSS locators pierce open shadow roots. XPath does not.'),
    quiz(3, 'A function passed to evaluate cannot see the variables of your test. How do you give it a value?', ['Use a global variable', 'Pass it as the argument of evaluate', 'Write it to a file', 'It is not possible'], 1,
         'The function runs in another process.', 'Pass values as the argument. They are serialized and sent into the page.'),
]

CALC = [
    calc(1, 'A page has 1 main frame and 2 iframes. How many frames does page.frames() return?', 3, '1 + 2', ['1 main frame + 2 iframes = 3 frames']),
    calc(1, 'The feedback form got 2 screenshots and then 1 more in a second call that replaced them. How many files does the input hold?', 1,
         'setInputFiles replaces the files', ['The second call replaces the first list', '1 file']),
    calc(2, 'networkidle waits for 500 ms of silence. A page polls the server every 400 ms. How many times will networkidle be reached?', 0,
         'Is there ever 500 ms of silence?', ['A request every 400 ms', 'The longest quiet gap is under 400 ms', 'networkidle is never reached: 0']),
    calc(2, 'A suite has 30 tests and each one used a fixed wait of 2 s instead of waiting for the URL, which takes 0.3 s. How many seconds are wasted?', 51,
         '30 × (2 - 0.3)', ['2 - 0.3 = 1.7 s per test', '30 × 1.7 = 51 s']),
    calc(2, 'The CSV report has a header line and 2 order lines. How many lines does it have?', 3, '1 + 2', ['1 header + 2 orders = 3 lines']),
    calc(3, 'The report shows totals 219 and 1299. What is the sum of all orders?', 1518, '219 + 1299', ['219 + 1299 = 1518']),
    calc(3, 'A test counts page errors. The page throws 1 error each time Break the page is clicked. The test clicks it 3 times. How many pageerror events?', 3, '1 per click', ['3 clicks × 1 error = 3 events']),
    calc(3, 'The card number 4111 1111 1111 1111 has spaces. After the page removes them, how many digits are left?', 16, 'four groups of four', ['4 × 4 = 16 digits']),
]

LABS = [
    {'id': 'pay', 'title': 'Pay inside the iframe', 'name': 'pay inside the payment iframe',
     'task': 'On <code>/frames</code>, step into the iframe with the title <b>Payment form</b>, type the card <code>4111 1111 1111 1111</code> and expiry <code>12/29</code>, click <b>Pay ₹219</b>, and check that the main page says <b>Paid with card ending 1111</b>.',
     'goal': 'The payment goes through and the main page shows it.', 'start': '/frames',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('pay inside the payment iframe', async ({ page }) => {
  await page.goto('/frames');
  const payment = page.frameLocator('iframe[title="Payment form"]');
  // fill the card number and expiry inside the iframe, then pay
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('pay inside the payment iframe', async ({ page }) => {
  await page.goto('/frames');
  const payment = page.frameLocator('iframe[title="Payment form"]');
  await payment.getByLabel('Card number').fill('4111 1111 1111 1111');
  await payment.getByLabel('Expiry').fill('12/29');
  await payment.getByRole('button', { name: 'Pay ₹219' }).click();
  await expect(page.getByRole('status')).toHaveText('Paid with card ending 1111');
});'''},
     'hint': 'Use <code>payment.getByLabel(...)</code> for the boxes inside the iframe, and <code>page.getByRole(\'status\')</code> for the message outside it.',
     'why': 'Locators that start from the frame search inside the iframe only. The result message is in the main page, so that check starts from page again.',
     'check': [["/Paid with card ending 1111/.test(ctx.text)", 'The main page shows the payment'], ["/frameLocator|frame_locator|FrameLocator|contentFrame|content_frame|ContentFrame/.test(ctx.code)", 'The test steps into the iframe']]},
    {'id': 'confirm', 'title': 'Accept a confirm dialog', 'name': 'delete the account',
     'task': 'On <code>/widgets</code>, the <b>Delete account</b> button asks for confirmation. Accept the dialog and check that the status says <b>Account deleted</b>. Try it first without a handler to see what happens.',
     'goal': 'The dialog is accepted and the account is deleted.', 'start': '/widgets',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('delete the account', async ({ page }) => {
  await page.goto('/widgets');
  // add a dialog handler here, before the click
  await page.getByRole('button', { name: 'Delete account' }).click();
  await expect(page.getByRole('status')).toHaveText('Account deleted');
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('delete the account', async ({ page }) => {
  await page.goto('/widgets');
  page.on('dialog', dialog => dialog.accept());
  await page.getByRole('button', { name: 'Delete account' }).click();
  await expect(page.getByRole('status')).toHaveText('Account deleted');
});'''},
     'hint': 'Before the click: <code>page.on(\'dialog\', dialog =&gt; dialog.accept())</code>. In Java: <code>page.onDialog(dialog -&gt; dialog.accept())</code>.',
     'why': 'Without a handler the dialog is dismissed, so the page shows Kept your account and the check fails. The handler must exist before the click that opens the dialog.',
     'check': [["/Account deleted/.test(ctx.text)", 'The account was deleted'], ["/dialog|Dialog/.test(ctx.code)", 'The test handles the dialog']]},
]

T = {
    'slug': 'pw-pages', 'title': 'Navigation, frames, dialogs, files and events', 'short': 'Frames, dialogs and files', 'emoji': '🧭', 'module': MODULE, 'minutes': 22,
    'lead': 'Handle everything a real page throws at a test: navigation and redirects, payment iframes, alerts and prompts, downloads and uploads, console errors, code that runs inside the page, and shadow DOM.',
    'desc': 'goto and waitUntil, waitForURL, back and reload, frameLocator and contentFrame, dialogs, downloads, setInputFiles, console and pageerror events, evaluate and addInitScript, and shadow DOM in Java, Python, JavaScript and TypeScript.',
    'summary': 'What goto waits for, waiting for the URL after a click, back, forward and reload, a recorded walk through a payment iframe, frameLocator and contentFrame, alert, confirm and prompt with the default dismiss, downloads with suggestedFilename and saveAs, uploads from memory, console, pageerror and request events, evaluate and addInitScript, and locating inside shadow DOM.',
    'keywords': ['goto', 'waitUntil', 'waitForURL', 'iframe', 'frameLocator', 'contentFrame', 'dialog', 'alert', 'confirm', 'prompt', 'download', 'upload', 'setInputFiles', 'console', 'pageerror', 'evaluate', 'addInitScript', 'shadow dom'],
    'plain': 'Real pages open new addresses, hide forms inside other pages, pop up questions and give you files. Playwright has a simple tool for each, and the rule is the same: start waiting before the click that causes it.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
