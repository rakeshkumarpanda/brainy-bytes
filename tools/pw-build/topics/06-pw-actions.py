from pkit import part, say, quiz, calc, panel, four, one, js, ts, py, jv, shown, walk, step, table, tip, by, viz, figure

MODULE = ('🎯', 'Finding and using elements', 'pw-elements', 'Locators, actions with auto-waiting, and assertions that retry by themselves.')

# ---------- auto-waiting ----------
AUTO_TS = '''import { test, expect } from '@playwright/test';

test('actions wait until the element is ready', async ({ page }) => {
  await page.goto('/widgets');
  // A loading cover hides the page for 0.8 s, and Pay now is disabled for 1 s.
  await page.getByRole('button', { name: 'Pay now' }).click();
  await expect(page.getByText('Payment done')).toBeVisible();

  // The offer appears 1.2 s after the click. The check waits for it.
  await page.getByRole('button', { name: 'Load offers' }).click();
  await expect(page.getByTestId('offer')).toHaveText('Buy 2 mugs, get 1 free');

  // This button slides in when the page opens. click waits until it stops moving.
  await page.getByRole('button', { name: 'Catch me' }).click();
  await expect(page.getByText('Caught it')).toBeVisible();
});'''

AUTO_PY = '''from playwright.sync_api import Page, expect


def test_actions_wait_until_the_element_is_ready(page: Page):
    page.goto("/widgets")
    # A loading cover hides the page for 0.8 s, and Pay now is disabled for 1 s.
    page.get_by_role("button", name="Pay now").click()
    expect(page.get_by_text("Payment done")).to_be_visible()

    # The offer appears 1.2 s after the click. The check waits for it.
    page.get_by_role("button", name="Load offers").click()
    expect(page.get_by_test_id("offer")).to_have_text("Buy 2 mugs, get 1 free")

    # This button slides in when the page opens. click waits until it stops moving.
    page.get_by_role("button", name="Catch me").click()
    expect(page.get_by_text("Caught it")).to_be_visible()'''

AUTO_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class AutoWaitTest {
  @Test
  void actionsWaitUntilTheElementIsReady(Page page) {
    page.navigate("/widgets");
    // A loading cover hides the page for 0.8 s, and Pay now is disabled for 1 s.
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Pay now")).click();
    assertThat(page.getByText("Payment done")).isVisible();

    // The offer appears 1.2 s after the click. The check waits for it.
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Load offers")).click();
    assertThat(page.getByTestId("offer")).hasText("Buy 2 mugs, get 1 free");

    // This button slides in when the page opens. click waits until it stops moving.
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Catch me")).click();
    assertThat(page.getByText("Caught it")).isVisible();
  }
}'''

# ---------- the call log of a timeout ----------
LOG_TS = '''import { test, expect } from '@playwright/test';

test('when it never gets ready, the error says why', async ({ page }) => {
  await page.goto('/products');
  const soldOut = page.getByRole('button', { name: 'Out of stock' });

  const error = await soldOut.click({ timeout: 2000 }).catch(e => e);
  console.log(error.name);
  console.log(error.message.split('\\n').slice(0, 7).join('\\n'));
});'''

LOG_PY = '''import pytest
from playwright.sync_api import Page, TimeoutError


def test_when_it_never_gets_ready_the_error_says_why(page: Page):
    page.goto("/products")
    sold_out = page.get_by_role("button", name="Out of stock")

    with pytest.raises(TimeoutError) as info:
        sold_out.click(timeout=2000)
    print(type(info.value).__name__)
    print("\\n".join(info.value.message.split("\\n")[:7]))'''

LOG_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.TimeoutError;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertThrows;

@UsePlaywright(ShopOptions.class)
public class CallLogTest {
  @Test
  void whenItNeverGetsReadyTheErrorSaysWhy(Page page) {
    page.navigate("/products");
    Locator soldOut = page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Out of stock"));

    TimeoutError error = assertThrows(TimeoutError.class, () -> soldOut.click(new Locator.ClickOptions().setTimeout(2000)));
    System.out.println(error.getClass().getSimpleName());
    String message = error.getMessage();
    // Java wraps the driver error and its stack, so print from the call log on.
    System.out.println(message.substring(message.indexOf("Call log:")).lines().limit(6).collect(Collectors.joining("\\n")));
  }
}'''

# ---------- hover and focus ----------
HOVER_TS = '''import { test, expect } from '@playwright/test';

test('hover and focus show the tooltip', async ({ page }) => {
  await page.goto('/forms');
  const help = page.getByText('❓ Help');
  const tooltip = page.getByRole('tooltip');
  await expect(tooltip).toBeHidden();

  await help.hover();                        // the mouse rests on it
  await expect(tooltip).toHaveText('We reply within two working days');

  await page.mouse.move(0, 0);               // move the mouse away
  await expect(tooltip).toBeHidden();

  await help.focus();                        // keyboard users reach it with Tab
  await expect(tooltip).toBeVisible();
  console.log('tooltip:', await tooltip.textContent());
});'''

HOVER_PY = '''from playwright.sync_api import Page, expect


def test_hover_and_focus_show_the_tooltip(page: Page):
    page.goto("/forms")
    help_icon = page.get_by_text("❓ Help")
    tooltip = page.get_by_role("tooltip")
    expect(tooltip).to_be_hidden()

    help_icon.hover()                        # the mouse rests on it
    expect(tooltip).to_have_text("We reply within two working days")

    page.mouse.move(0, 0)                    # move the mouse away
    expect(tooltip).to_be_hidden()

    help_icon.focus()                        # keyboard users reach it with Tab
    expect(tooltip).to_be_visible()
    print("tooltip:", tooltip.text_content())'''

HOVER_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class HoverTest {
  @Test
  void hoverAndFocusShowTheTooltip(Page page) {
    page.navigate("/forms");
    Locator help = page.getByText("❓ Help");
    Locator tooltip = page.getByRole(AriaRole.TOOLTIP);
    assertThat(tooltip).isHidden();

    help.hover();                            // the mouse rests on it
    assertThat(tooltip).hasText("We reply within two working days");

    page.mouse().move(0, 0);                 // move the mouse away
    assertThat(tooltip).isHidden();

    help.focus();                            // keyboard users reach it with Tab
    assertThat(tooltip).isVisible();
    System.out.println("tooltip: " + tooltip.textContent());
  }
}'''

# ---------- typing and keys ----------
KEYS_TS = '''import { test, expect } from '@playwright/test';

test('fill, type key by key, and press shortcuts', async ({ page }) => {
  await page.goto('/products');
  const search = page.getByPlaceholder('Search products');
  await expect(page.getByRole('listitem')).toHaveCount(5);

  await search.fill('desk');                              // sets the whole value at once
  console.log('after fill:', await search.inputValue(), '|', await page.getByRole('listitem').count(), 'card');

  await search.clear();
  await search.pressSequentially('mug', { delay: 50 });   // one key at a time, like a person
  console.log('after typing:', await search.inputValue());

  await search.press('Control+A');
  await search.press('Backspace');
  console.log('after select all and delete:', (await search.inputValue()).length, 'characters');

  await page.goto('/forms');
  await page.keyboard.press('Control+K');                 // a shortcut for the whole page
  await expect(page.getByText('Search opened')).toBeVisible();
});'''

KEYS_PY = '''from playwright.sync_api import Page, expect


def test_fill_type_key_by_key_and_press_shortcuts(page: Page):
    page.goto("/products")
    search = page.get_by_placeholder("Search products")
    expect(page.get_by_role("listitem")).to_have_count(5)

    search.fill("desk")                                   # sets the whole value at once
    print("after fill:", search.input_value(), "|", page.get_by_role("listitem").count(), "card")

    search.clear()
    search.press_sequentially("mug", delay=50)            # one key at a time, like a person
    print("after typing:", search.input_value())

    search.press("Control+A")
    search.press("Backspace")
    print("after select all and delete:", len(search.input_value()), "characters")

    page.goto("/forms")
    page.keyboard.press("Control+K")                      # a shortcut for the whole page
    expect(page.get_by_text("Search opened")).to_be_visible()'''

KEYS_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class KeysTest {
  @Test
  void fillTypeKeyByKeyAndPressShortcuts(Page page) {
    page.navigate("/products");
    Locator search = page.getByPlaceholder("Search products");
    assertThat(page.getByRole(AriaRole.LISTITEM)).hasCount(5);

    search.fill("desk");                                   // sets the whole value at once
    System.out.println("after fill: " + search.inputValue() + " | " + page.getByRole(AriaRole.LISTITEM).count() + " card");

    search.clear();
    search.pressSequentially("mug", new Locator.PressSequentiallyOptions().setDelay(50));   // one key at a time
    System.out.println("after typing: " + search.inputValue());

    search.press("Control+A");
    search.press("Backspace");
    System.out.println("after select all and delete: " + search.inputValue().length() + " characters");

    page.navigate("/forms");
    page.keyboard().press("Control+K");                    // a shortcut for the whole page
    assertThat(page.getByText("Search opened")).isVisible();
  }
}'''

# ---------- form controls ----------
FORM_TS = '''import { test, expect } from '@playwright/test';

test('fill every kind of form control', async ({ page }) => {
  await page.goto('/forms');
  await page.getByLabel('Your name').fill('Asha');
  await page.getByLabel('Topic').selectOption('delivery');            // by value
  await page.getByLabel('Topic').selectOption({ label: 'Payment' });  // or by the text you see
  await page.getByLabel('Happy').check();                             // a radio button
  await page.getByLabel('Order date').fill('2026-10-01');             // dates use yyyy-mm-dd
  await page.getByLabel('Message').fill('The parcel came a day early.');
  await page.getByLabel('Send me the newsletter').setChecked(true);
  await page.getByLabel('Volume').fill('8');                          // a slider

  console.log('topic:', await page.getByLabel('Topic').inputValue());
  console.log('happy checked:', await page.getByLabel('Happy').isChecked());
  console.log('date:', await page.getByLabel('Order date').inputValue());
  console.log('volume:', await page.getByLabel('Volume').inputValue());

  await page.getByRole('button', { name: 'Send feedback' }).click();
  await expect(page.getByRole('status')).toHaveText(
    'Thanks Asha! Topic: payment, mood: happy, files: no files, newsletter: yes');
});'''

FORM_PY = '''from playwright.sync_api import Page, expect


def test_fill_every_kind_of_form_control(page: Page):
    page.goto("/forms")
    page.get_by_label("Your name").fill("Asha")
    page.get_by_label("Topic").select_option("delivery")            # by value
    page.get_by_label("Topic").select_option(label="Payment")       # or by the text you see
    page.get_by_label("Happy").check()                              # a radio button
    page.get_by_label("Order date").fill("2026-10-01")              # dates use yyyy-mm-dd
    page.get_by_label("Message").fill("The parcel came a day early.")
    page.get_by_label("Send me the newsletter").set_checked(True)
    page.get_by_label("Volume").fill("8")                           # a slider

    print("topic:", page.get_by_label("Topic").input_value())
    print("happy checked:", page.get_by_label("Happy").is_checked())
    print("date:", page.get_by_label("Order date").input_value())
    print("volume:", page.get_by_label("Volume").input_value())

    page.get_by_role("button", name="Send feedback").click()
    expect(page.get_by_role("status")).to_have_text(
        "Thanks Asha! Topic: payment, mood: happy, files: no files, newsletter: yes")'''

FORM_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import com.microsoft.playwright.options.SelectOption;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class FormTest {
  @Test
  void fillEveryKindOfFormControl(Page page) {
    page.navigate("/forms");
    page.getByLabel("Your name").fill("Asha");
    page.getByLabel("Topic").selectOption("delivery");                         // by value
    page.getByLabel("Topic").selectOption(new SelectOption().setLabel("Payment"));  // or by the text you see
    page.getByLabel("Happy").check();                                          // a radio button
    page.getByLabel("Order date").fill("2026-10-01");                          // dates use yyyy-mm-dd
    page.getByLabel("Message").fill("The parcel came a day early.");
    page.getByLabel("Send me the newsletter").setChecked(true);
    page.getByLabel("Volume").fill("8");                                       // a slider

    System.out.println("topic: " + page.getByLabel("Topic").inputValue());
    System.out.println("happy checked: " + page.getByLabel("Happy").isChecked());
    System.out.println("date: " + page.getByLabel("Order date").inputValue());
    System.out.println("volume: " + page.getByLabel("Volume").inputValue());

    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Send feedback")).click();
    assertThat(page.getByRole(AriaRole.STATUS)).hasText(
        "Thanks Asha! Topic: payment, mood: happy, files: no files, newsletter: yes");
  }
}'''

# ---------- drag and drop ----------
DRAG_TS = '''import { test, expect } from '@playwright/test';

test('drag tasks to the Done lane', async ({ page }) => {
  await page.goto('/forms');
  const todo = page.getByRole('list', { name: 'To do' });
  const done = page.getByRole('list', { name: 'Done' });

  await todo.getByText('Pack the order').dragTo(done);
  await expect(done.getByRole('listitem')).toHaveText(['Pack the order']);

  // The same by hand with the mouse, for widgets that need finer control.
  await todo.getByText('Print the label').hover();
  await page.mouse.down();
  await done.hover();
  await done.hover();            // a second move, so the page gets its dragover event
  await page.mouse.up();

  await expect(done.getByRole('listitem')).toHaveCount(2);
  console.log('Done lane:', await done.getByRole('listitem').allTextContents());
  console.log('To do lane:', await todo.getByRole('listitem').count(), 'tasks');
});'''

DRAG_PY = '''from playwright.sync_api import Page, expect


def test_drag_tasks_to_the_done_lane(page: Page):
    page.goto("/forms")
    todo = page.get_by_role("list", name="To do")
    done = page.get_by_role("list", name="Done")

    todo.get_by_text("Pack the order").drag_to(done)
    expect(done.get_by_role("listitem")).to_have_text(["Pack the order"])

    # The same by hand with the mouse, for widgets that need finer control.
    todo.get_by_text("Print the label").hover()
    page.mouse.down()
    done.hover()
    done.hover()            # a second move, so the page gets its dragover event
    page.mouse.up()

    expect(done.get_by_role("listitem")).to_have_count(2)
    print("Done lane:", done.get_by_role("listitem").all_text_contents())
    print("To do lane:", todo.get_by_role("listitem").count(), "tasks")'''

DRAG_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class DragTest {
  @Test
  void dragTasksToTheDoneLane(Page page) {
    page.navigate("/forms");
    Locator todo = page.getByRole(AriaRole.LIST, new Page.GetByRoleOptions().setName("To do"));
    Locator done = page.getByRole(AriaRole.LIST, new Page.GetByRoleOptions().setName("Done"));

    todo.getByText("Pack the order").dragTo(done);
    assertThat(done.getByRole(AriaRole.LISTITEM)).hasText(new String[] {"Pack the order"});

    // The same by hand with the mouse, for widgets that need finer control.
    todo.getByText("Print the label").hover();
    page.mouse().down();
    done.hover();
    done.hover();            // a second move, so the page gets its dragover event
    page.mouse().up();

    assertThat(done.getByRole(AriaRole.LISTITEM)).hasCount(2);
    System.out.println("Done lane: " + done.getByRole(AriaRole.LISTITEM).allTextContents());
    System.out.println("To do lane: " + todo.getByRole(AriaRole.LISTITEM).count() + " tasks");
  }
}'''

# ---------- waiting without sleeping ----------
WAIT_TS = '''import { test, expect } from '@playwright/test';

test('wait for what you need, never for a fixed time', async ({ page }) => {
  // Start waiting for the API answer before the page asks for it.
  const answer = page.waitForResponse(r => r.url().includes('/api/products'));
  await page.goto('/products');
  console.log('API answered with status', (await answer).status());

  await page.getByText('Loading products…').waitFor({ state: 'detached' });
  console.log('cards now:', await page.getByRole('listitem').count());

  await page.goto('/widgets');
  await page.waitForFunction(() => !document.querySelector('#cover'));
  console.log('loading cover left:', await page.locator('#cover').count());
  await expect(page.getByRole('button', { name: 'Pay now' })).toBeEnabled();
});'''

WAIT_PY = '''from playwright.sync_api import Page, expect


def test_wait_for_what_you_need_never_for_a_fixed_time(page: Page):
    # Start waiting for the API answer before the page asks for it.
    with page.expect_response(lambda r: "/api/products" in r.url) as answer:
        page.goto("/products")
    print("API answered with status", answer.value.status)

    page.get_by_text("Loading products…").wait_for(state="detached")
    print("cards now:", page.get_by_role("listitem").count())

    page.goto("/widgets")
    page.wait_for_function("() => !document.querySelector('#cover')")
    print("loading cover left:", page.locator("#cover").count())
    expect(page.get_by_role("button", name="Pay now")).to_be_enabled()'''

WAIT_JAVA = '''package com.brainy;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Response;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import com.microsoft.playwright.options.WaitForSelectorState;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class WaitTest {
  @Test
  void waitForWhatYouNeedNeverForAFixedTime(Page page) {
    // Start waiting for the API answer before the page asks for it.
    Response answer = page.waitForResponse(r -> r.url().contains("/api/products"), () -> page.navigate("/products"));
    System.out.println("API answered with status " + answer.status());

    page.getByText("Loading products…").waitFor(new Locator.WaitForOptions().setState(WaitForSelectorState.DETACHED));
    System.out.println("cards now: " + page.getByRole(AriaRole.LISTITEM).count());

    page.navigate("/widgets");
    page.waitForFunction("() => !document.querySelector('#cover')");
    System.out.println("loading cover left: " + page.locator("#cover").count());
    assertThat(page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Pay now"))).isEnabled();
  }
}'''

CODES = {
    'auto': four('Click a button that is covered, disabled and moving',
                 java=jv({'AutoWaitTest.java': AUTO_JAVA}),
                 py=py({'test_auto_wait.py': AUTO_PY}),
                 js=js({'auto-wait.spec.js': AUTO_TS}),
                 ts=ts({'auto-wait.spec.ts': AUTO_TS}),
                 result='The test has no sleep anywhere. Each click waited exactly as long as the page needed: until the cover was gone, the button was enabled, and the moving button stood still. A fixed wait would either be too short and fail, or too long and waste time on every run.'),
    'calllog': four('A click that can never happen, and its call log',
                    java=jv({'CallLogTest.java': LOG_JAVA}),
                    py=py({'test_call_log.py': LOG_PY}, cmd='pytest -v -s'),
                    js=js({'call-log.spec.js': LOG_TS}),
                    ts=ts({'call-log.spec.ts': LOG_TS}),
                    result='The button stays disabled, so the click gave up after the 2 second timeout. The call log under the message tells you which check kept failing: here, element is not enabled. When a test times out in your project, this log is the first thing to read. In Java the message also carries the stack of the driver, so the Java example prints from the call log on.'),
    'hover': four('Hover and focus',
                  java=jv({'HoverTest.java': HOVER_JAVA}),
                  py=py({'test_hover.py': HOVER_PY}, cmd='pytest -v -s'),
                  js=js({'hover.spec.js': HOVER_TS}),
                  ts=ts({'hover.spec.ts': HOVER_TS}),
                  result='Hover moves the real mouse over the element, so CSS hover effects and menus react. Focus is what the Tab key does. Checking both makes sure the tooltip works for mouse users and keyboard users.'),
    'keys': four('fill, pressSequentially and keyboard shortcuts',
                 java=jv({'KeysTest.java': KEYS_JAVA}),
                 py=py({'test_keys.py': KEYS_PY}, cmd='pytest -v -s'),
                 js=js({'keys.spec.js': KEYS_TS}),
                 ts=ts({'keys.spec.ts': KEYS_TS}),
                 result='<code>fill</code> sets the value in one go and fires the input event, which is enough for almost every box. <code>pressSequentially</code> sends one key at a time for boxes that react to each key, such as an auto complete list. <code>press</code> takes a key name or a combination such as Control+A.'),
    'form': four('Text boxes, drop downs, radio buttons, checkboxes, dates and sliders',
                 java=jv({'FormTest.java': FORM_JAVA}),
                 py=py({'test_form.py': FORM_PY}, cmd='pytest -v -s'),
                 js=js({'form.spec.js': FORM_TS}),
                 ts=ts({'form.spec.ts': FORM_TS}),
                 result='Every control on the form is found by its label. <code>selectOption</code> takes the value or the visible label, and the last call wins, so the topic is payment. Dates are filled in the yyyy-mm-dd format whatever the browser shows. The status line proves the page received every value.'),
    'drag': four('Drag and drop with dragTo, and by hand with the mouse',
                 java=jv({'DragTest.java': DRAG_JAVA}),
                 py=py({'test_drag.py': DRAG_PY}, cmd='pytest -v -s'),
                 js=js({'drag.spec.js': DRAG_TS}),
                 ts=ts({'drag.spec.ts': DRAG_TS}),
                 result='<code>dragTo</code> hovers the task, presses the mouse button, moves to the lane and releases it. The manual version does the same steps one by one. The Playwright docs advise moving twice over the target when the page listens for dragover, which this page does.'),
    'wait': four('Wait for a response, an element or a condition',
                 java=jv({'WaitTest.java': WAIT_JAVA}),
                 py=py({'test_wait.py': WAIT_PY}, cmd='pytest -v -s'),
                 js=js({'wait.spec.js': WAIT_TS}),
                 ts=ts({'wait.spec.ts': WAIT_TS}),
                 result='Each wait names the thing the test needs: the API answer, the loading message going away, the cover being removed. Each one returns the moment that happens. In Python and Java the wait wraps the action that causes it, so the answer cannot be missed.'),
    'walkform': walk('Filling the feedback form', [
        step('Open the feedback form.', "await page.goto('http://localhost:4173/forms');", 'page.goto("http://localhost:4173/forms")', 'page.navigate("http://localhost:4173/forms");'),
        step('Type the name into the box labelled Your name.', "await page.getByLabel('Your name').fill('Asha');",
             'page.get_by_label("Your name").fill("Asha")', 'page.getByLabel("Your name").fill("Asha");'),
        step('Choose Delivery in the Topic drop down.', "await page.getByLabel('Topic').selectOption('delivery');",
             'page.get_by_label("Topic").select_option("delivery")', 'page.getByLabel("Topic").selectOption("delivery");'),
        step('Pick the Happy radio button.', "await page.getByLabel('Happy').check();",
             'page.get_by_label("Happy").check()', 'page.getByLabel("Happy").check();'),
        step('Write a short message.', "await page.getByLabel('Message').fill('The parcel came a day early.');",
             'page.get_by_label("Message").fill("The parcel came a day early.")', 'page.getByLabel("Message").fill("The parcel came a day early.");'),
        step('Tick the newsletter box.', "await page.getByLabel('Send me the newsletter').check();",
             'page.get_by_label("Send me the newsletter").check()', 'page.getByLabel("Send me the newsletter").check();'),
        step('Send the form. Playwright scrolls the button into view by itself.', "await page.getByRole('button', { name: 'Send feedback' }).click();",
             'page.get_by_role("button", name="Send feedback").click()', 'page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Send feedback")).click();'),
        step('The thank you line shows every value the page received.', "await expect(page.getByRole('status')).toContainText('Topic: delivery, mood: happy');",
             'expect(page.get_by_role("status")).to_contain_text("Topic: delivery, mood: happy")', 'assertThat(page.getByRole(AriaRole.STATUS)).containsText("Topic: delivery, mood: happy");'),
    ], size=(900, 620)),
}

DG = {
    'click': {'t': 'What happens inside one click()', 'w': 900, 'h': 220,
              'n': [['find', 20, 80, 130, 64, 'find', {'c': 5, 'sub': 'exactly one', 'i': 'The locator must match exactly one element, or the click fails with strict mode.'}],
                    ['checks', 170, 80, 160, 64, 'checks', {'c': 2, 'sub': 'retry until ready', 'i': 'Visible, stable, receives events, enabled, not inert. Each failed check is retried.'}],
                    ['scroll', 350, 80, 140, 64, 'scroll', {'c': 3, 'sub': 'into view', 'i': 'The element is scrolled into view if it is not on screen.'}],
                    ['mouse', 510, 80, 160, 64, 'mouse', {'c': 1, 'sub': 'move, down, up', 'i': 'The mouse moves to the middle of the element, presses and releases.'}],
                    ['nav', 690, 80, 190, 64, 'after the click', {'c': 0, 'sub': 'navigation started', 'i': 'If the click starts a navigation, Playwright waits for it to start before returning.'}]],
              'e': [['find', 'checks'], ['checks', 'scroll'], ['scroll', 'mouse'], ['mouse', 'nav']],
              'st': [[['find'], 'First the locator is resolved. It must find exactly one element.'],
                     [['checks', 'find>checks'], 'Then the actionability checks run, and any that fail are retried until they pass or the timeout ends.'],
                     [['scroll', 'checks>scroll'], 'The element is scrolled into view, so you never need to scroll by hand.'],
                     [['mouse', 'scroll>mouse'], 'A real mouse moves to the middle of the element and clicks, so the page sees the same events as with a person.'],
                     [['nav', 'mouse>nav'], 'If the click started a navigation, click waits for it to start. Then your next line runs.']]},
}

CHECKS = table(['Action', 'Visible', 'Stable', 'Receives events', 'Enabled', 'Editable'], [
    ['click, dblclick, check, uncheck, setChecked, tap', '✓', '✓', '✓', '✓', ''],
    ['hover, dragTo', '✓', '✓', '✓', '', ''],
    ['screenshot', '✓', '✓', '', '', ''],
    ['fill, clear', '✓', '', '', '✓', '✓'],
    ['selectOption', '✓', '', '', '✓', ''],
    ['selectText', '✓', '', '', '', ''],
    ['scrollIntoViewIfNeeded', '', '✓', '', '', ''],
    ['focus, blur, press, pressSequentially, setInputFiles, dispatchEvent', '', '', '', '', ''],
])

PARTS = [
    part('auto', '⏳', 'Auto-waiting: no more sleeps', f'''
<p>Pages are slow in many small ways. A button is disabled until a price loads, a cover hides the page while it gets ready, a panel slides in. Before every action, Playwright checks that the element is ready and waits until it is. You do not write any waiting code for this.</p>
{viz('pwact')}
[[auto]]
<p>The checks depend on the action. This table comes from the Playwright documentation. Click, check and fill also make sure the element is not inert, which means not blocked by an open modal dialog.</p>
{CHECKS}
<div class="viz" data-viz="flow" data-k="click"></div>
{tip('Think of a lift. You press the button and wait until the doors open. You do not stand there counting to ten first. Playwright waits for the doors, not for the clock.', 'life')}
''', easy=True, kw=['auto-waiting', 'actionability', 'visible', 'stable', 'enabled', 'editable', 'flaky', 'sleep']),

    part('calllog', '🧾', 'When waiting is not enough', f'''
<p>Sometimes the element never becomes ready, because of a real bug or a wrong locator. Then the action fails with a <b>TimeoutError</b> after its timeout, and the message includes a call log of every check it tried.</p>
[[calllog]]
<p>Two options change the checks, and both are worth knowing even if you rarely use them.</p>
{table(['Option', 'What it does', 'When to use it'], [
    [by(java='setForce(true)', py='force=True', js='force: true'), 'skips the checks that are not essential, such as receives events', 'a custom widget that hides its real input under a styled label'],
    [by(java='setTrial(true)', py='trial=True', js='trial: true'), 'runs every check but does not click', 'to wait until something could be clicked, without clicking it'],
    [by(java='setTimeout(5000)', py='timeout=5000', js='timeout: 5000'), 'a different timeout for this one action', 'one action that is known to be slow'],
])}
{tip('Reaching for force is often a sign the test found the wrong element, or that a real user could not click it either. Read the call log first.', 'warn')}
''', kw=['TimeoutError', 'call log', 'force', 'trial', 'timeout']),

    part('mouse', '🖱️', 'Clicking, hovering and focusing', f'''
<p>A click can be more than a plain left click. All of these are options of the same <code>click</code> method.</p>
{table(['You want', 'Code'], [
    ['a double click', by(java='dblclick()', py='dblclick()', js='dblclick()')],
    ['a right click', by(java='click(new Locator.ClickOptions().setButton(MouseButton.RIGHT))', py='click(button="right")', js="click({ button: 'right' })")],
    ['Shift and click', by(java='setModifiers(Arrays.asList(KeyboardModifier.SHIFT))', py='click(modifiers=["Shift"])', js="click({ modifiers: ['Shift'] })")],
    ['Control on Windows and Linux, Command on macOS', by(java='KeyboardModifier.CONTROL_OR_META', py='modifiers=["ControlOrMeta"]', js="modifiers: ['ControlOrMeta']")],
    ['a click at the top left corner', by(java='setPosition(0, 0)', py='position={"x": 0, "y": 0}', js='position: { x: 0, y: 0 }')],
    ['the mouse resting on it', by(java='hover()', py='hover()', js='hover()')],
    ['a tap on a touch screen', by(java='tap() with setHasTouch(true) on the context', py='tap() with has_touch=True on the context', js='tap() with hasTouch: true in use')],
])}
[[hover]]
''', easy=True, kw=['click', 'dblclick', 'right click', 'hover', 'focus', 'modifiers', 'tap', 'ControlOrMeta']),

    part('keys', '⌨️', 'Typing and keys', f'''
<p>Most of the time you only need <code>fill</code>. It clears the box and puts the new text in, like pasting. Use the slower ways only when the page reacts to single key presses.</p>
[[keys]]
{table(['Method', 'Sends', 'Use for'], [
    ['fill(text)', 'the whole value at once', 'almost every text box'],
    ['pressSequentially(text)', 'one key event per character', 'auto complete, masks that format as you type'],
    ['press(key)', 'one key or a combination', 'Enter, Tab, Escape, ArrowDown, Control+A'],
    ['keyboard.press(key)', 'a key to whatever has focus', 'page shortcuts such as Control+K'],
    ['clear()', 'an empty value', 'emptying a box'],
])}
{tip('Old tutorials use type(). It was renamed pressSequentially in Playwright 1.38 and the old name is deprecated. If you see it in a code base, it does the same thing.', 'new')}
''', kw=['fill', 'pressSequentially', 'type', 'press', 'keyboard', 'shortcut', 'clear']),

    part('forms', '📝', 'Checkboxes, radio buttons, drop downs and dates', f'''
<p>A form is a mix of controls. Each has its own method, and they all wait and check like click does.</p>
[[walkform]]
[[form]]
{table(['Control', 'Method', 'Read it back'], [
    ['text box, text area', 'fill', 'inputValue'],
    ['checkbox, radio button', 'check, uncheck, setChecked', 'isChecked or toBeChecked'],
    ['drop down (select)', 'selectOption by value, label or index, or a list for multi select', 'inputValue or toHaveValue'],
    ['date, time, color, range', 'fill with the standard format, such as 2026-10-01', 'inputValue'],
    ['file input', 'setInputFiles', 'the files list'],
])}
''', easy=True, kw=['check', 'uncheck', 'setChecked', 'selectOption', 'radio', 'checkbox', 'select', 'date', 'range', 'form']),

    part('drag', '🧲', 'Drag and drop and the mouse', f'''
<p>Kanban boards, sliders, sortable lists and file drop zones all need dragging. <code>dragTo</code> does it in one line. The mouse object gives you every step for widgets that need more control.</p>
[[drag]]
''', kw=['dragTo', 'drag and drop', 'mouse', 'mouse.down', 'mouse.up', 'mouse.move', 'kanban']),

    part('wait', '🚫', 'Waiting without sleeping', f'''
<p>Fixed waits such as {by(java='<code>page.waitForTimeout(3000)</code> or <code>Thread.sleep(3000)</code>', py='<code>page.wait_for_timeout(3000)</code> or <code>time.sleep(3)</code>', js='<code>page.waitForTimeout(3000)</code>')} are the most common reason for slow and flaky tests. When an action or a check is not enough, wait for the exact thing you need.</p>
[[wait]]
{table(['Wait for', 'Method'], [
    ['an element to appear, hide or go away', by(java='locator.waitFor(new Locator.WaitForOptions().setState(...))', py='locator.wait_for(state=...)', js='locator.waitFor({ state })')],
    ['a new URL', by(java='page.waitForURL', py='page.wait_for_url', js='page.waitForURL')],
    ['a network response', by(java='page.waitForResponse(predicate, action)', py='with page.expect_response(...)', js='page.waitForResponse(...)')],
    ['anything the page can compute', by(java='page.waitForFunction', py='page.wait_for_function', js='page.waitForFunction')],
    ['a popup, download or dialog', by(java='page.waitForPopup and friends', py='with page.expect_popup() and friends', js="page.waitForEvent('popup')")],
])}
{tip('Many teams add a lint rule or a code review check that rejects waitForTimeout. A suite with 200 tests and a 2 second sleep in each spends almost 7 minutes doing nothing on every run.', 'pro')}
''', kw=['waitForTimeout', 'sleep', 'waitFor', 'waitForResponse', 'waitForFunction', 'flaky']),
]

INFO = {'title': 'Act like a person, wait like a machine', 'panels': [
    panel([['e', '⏳'], ['t', 'auto-wait', {'b': 1}]], 'Auto-waiting', 'Checks before every action.', 'No sleeps needed.'),
    panel([['e', '🧾'], ['t', 'call log', {'b': 1}]], 'Timeouts', 'The error says which check failed.', 'Read it before using force.'),
    panel([['e', '⌨️'], ['t', 'fill', {'b': 1}]], 'Typing', 'fill for most boxes.', 'pressSequentially for key by key.'),
    panel([['e', '📝'], ['t', 'selectOption', {'b': 1}]], 'Forms', 'check, selectOption, dragTo.', 'Found by their labels.')],
    'remember': 'Never sleep. Every action waits until the element is ready, and when you need more, wait for the exact thing you need.'}

REAL = [
    ['🧾', 'Insurance quote forms', 'An insurance company tests a 40 field quote form with drop downs, dates and radio buttons. The tests fill every control by its label and check the price summary at the end.'],
    ['⏱️', 'A suite that got 5 times faster', 'A team removed every fixed sleep from 300 tests and let auto-waiting do the work. The run went from 50 minutes to 10, and the random failures went away with the sleeps.'],
    ['🗂️', 'A project board', 'A task tracking product tests that cards can be dragged between columns, using dragTo for the normal case and the mouse steps for a custom sortable list.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter is about actions: how Playwright waits before every click, what to read when it times out, clicking, hovering, typing, filling forms, dragging, and waiting without sleeps.',
        'यह अध्याय actions के बारे में है: Playwright हर click से पहले कैसे इंतज़ार करता है, timeout होने पर क्या पढ़ें, click, hover, typing, forms भरना, drag करना और sleep के बिना इंतज़ार।',
        'ಈ ಅಧ್ಯಾಯ actions ಬಗ್ಗೆ: Playwright ಪ್ರತಿ click ಗೆ ಮೊದಲು ಹೇಗೆ ಕಾಯುತ್ತದೆ, timeout ಆದಾಗ ಏನು ಓದಬೇಕು, click, hover, typing, forms ತುಂಬುವುದು, drag ಮತ್ತು sleep ಇಲ್ಲದೆ ಕಾಯುವುದು.',
        'ଏହି ଅଧ୍ୟାୟ actions ବିଷୟରେ: Playwright ପ୍ରତି click ପୂର୍ବରୁ କିପରି ଅପେକ୍ଷା କରେ, timeout ହେଲେ କଣ ପଢ଼ିବେ, click, hover, typing, forms ଭରିବା, drag ଏବଂ sleep ବିନା ଅପେକ୍ଷା।',
        'يتناول هذا الفصل الإجراءات: كيف ينتظر Playwright قبل كل نقرة، وماذا تقرأ عند انتهاء المهلة، والنقر والتمرير والكتابة وملء النماذج والسحب والانتظار دون توقف ثابت.',
        'Dieses Kapitel behandelt Aktionen: wie Playwright vor jedem Klick wartet, was du bei einem Timeout liest, Klicken, Hovern, Tippen, Formulare ausfüllen, Ziehen und Warten ohne Sleep.'),
    say('auto', 'Auto-waiting', 'Before every action Playwright checks that the element is visible, stable, receives events and is enabled, and it retries until all pass. You never need a fixed sleep.',
        'हर action से पहले Playwright जाँचता है कि element दिख रहा है, स्थिर है, events लेता है और enabled है, और सब पास होने तक दोबारा कोशिश करता है। Fixed sleep की कभी ज़रूरत नहीं।',
        'ಪ್ರತಿ action ಗೆ ಮೊದಲು Playwright element ಕಾಣುತ್ತಿದೆಯೇ, ಸ್ಥಿರವಾಗಿದೆಯೇ, events ಪಡೆಯುತ್ತದೆಯೇ ಮತ್ತು enabled ಆಗಿದೆಯೇ ಎಂದು ಪರಿಶೀಲಿಸಿ, ಎಲ್ಲವೂ ಪಾಸ್ ಆಗುವವರೆಗೆ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸುತ್ತದೆ. Fixed sleep ಬೇಕಿಲ್ಲ.',
        'ପ୍ରତି action ପୂର୍ବରୁ Playwright ଯାଞ୍ଚ କରେ element ଦେଖାଯାଉଛି, ସ୍ଥିର ଅଛି, events ପାଉଛି ଓ enabled ଅଛି, ଏବଂ ସବୁ ପାସ୍ ହେବା ପର୍ଯ୍ୟନ୍ତ ପୁଣି ଚେଷ୍ଟା କରେ। Fixed sleep ଦରକାର ନାହିଁ।',
        'قبل كل إجراء يتحقق Playwright من أن العنصر ظاهر ومستقر ويستقبل الأحداث ومفعّل، ويعيد المحاولة حتى تنجح كل الفحوص. لا تحتاج أبدًا إلى انتظار ثابت.',
        'Vor jeder Aktion prüft Playwright, ob das Element sichtbar, stabil, für Ereignisse erreichbar und aktiviert ist, und wiederholt das, bis alles passt. Ein festes Sleep brauchst du nie.'),
    say('calllog', 'Timeouts', 'If an element never becomes ready, the action fails with a timeout error. The call log in the message names the check that kept failing. Read it before you reach for force.',
        'अगर element कभी तैयार न हो तो action timeout error के साथ fail होता है। संदेश का call log बताता है कि कौन सी जाँच बार बार fail हुई। force से पहले इसे पढ़ें।',
        'Element ಎಂದಿಗೂ ಸಿದ್ಧವಾಗದಿದ್ದರೆ action timeout error ನೊಂದಿಗೆ fail ಆಗುತ್ತದೆ. ಸಂದೇಶದ call log ಯಾವ ಪರಿಶೀಲನೆ ವಿಫಲವಾಯಿತು ಎಂದು ಹೇಳುತ್ತದೆ. force ಗೆ ಮೊದಲು ಅದನ್ನು ಓದಿ.',
        'Element କେବେ ପ୍ରସ୍ତୁତ ନ ହେଲେ action timeout error ସହ fail ହୁଏ। ସନ୍ଦେଶର call log କହେ କେଉଁ ଯାଞ୍ଚ ବାରମ୍ବାର fail ହେଲା। force ପୂର୍ବରୁ ଏହାକୁ ପଢ଼ନ୍ତୁ।',
        'إذا لم يصبح العنصر جاهزًا أبدًا، يفشل الإجراء بخطأ انتهاء المهلة. يذكر سجل الاستدعاء في الرسالة الفحص الذي ظل يفشل. اقرأه قبل استخدام force.',
        'Wird ein Element nie bereit, scheitert die Aktion mit einem Timeout-Fehler. Das Call Log in der Meldung nennt die Prüfung, die immer wieder fehlschlug. Lies es, bevor du zu force greifst.'),
    say('mouse', 'Mouse', 'Click has options for double click, right click, modifier keys and position. Hover rests the mouse on an element and focus does what the Tab key does.',
        'Click में double click, right click, modifier keys और position के options हैं। Hover माउस को element पर रखता है और focus वही करता है जो Tab key करती है।',
        'Click ನಲ್ಲಿ double click, right click, modifier keys ಮತ್ತು position options ಇವೆ. Hover mouse ಅನ್ನು element ಮೇಲೆ ಇರಿಸುತ್ತದೆ, focus Tab key ಮಾಡುವುದನ್ನೇ ಮಾಡುತ್ತದೆ.',
        'Click ରେ double click, right click, modifier keys ଓ position options ଅଛି। Hover mouse କୁ element ଉପରେ ରଖେ ଏବଂ focus Tab key ଯାହା କରେ ତାହା କରେ।',
        'للنقر خيارات للنقر المزدوج والنقر الأيمن ومفاتيح التعديل والموضع. يضع hover الفأرة فوق العنصر ويفعل focus ما يفعله مفتاح Tab.',
        'Click hat Optionen für Doppelklick, Rechtsklick, Zusatztasten und Position. Hover lässt die Maus auf einem Element ruhen, und focus macht, was die Tab-Taste tut.'),
    say('keys', 'Typing', 'fill puts the whole text in at once and is right for almost every box. pressSequentially sends one key at a time, and press sends a key or a shortcut such as Control A.',
        'fill पूरा text एक बार में डालता है और लगभग हर box के लिए सही है। pressSequentially एक एक key भेजता है, और press एक key या Control A जैसा shortcut भेजता है।',
        'fill ಸಂಪೂರ್ಣ text ಅನ್ನು ಒಮ್ಮೆಗೇ ಹಾಕುತ್ತದೆ ಮತ್ತು ಬಹುತೇಕ ಎಲ್ಲಾ box ಗಳಿಗೆ ಸರಿ. pressSequentially ಒಂದೊಂದೇ key ಕಳುಹಿಸುತ್ತದೆ, press ಒಂದು key ಅಥವಾ Control A ನಂತಹ shortcut ಕಳುಹಿಸುತ್ತದೆ.',
        'fill ପୂରା text ଥରେ ଦିଏ ଏବଂ ପ୍ରାୟ ସବୁ box ପାଇଁ ଠିକ୍। pressSequentially ଗୋଟିଏ ଗୋଟିଏ key ପଠାଏ, ଏବଂ press ଗୋଟିଏ key ବା Control A ପରି shortcut ପଠାଏ।',
        'يضع fill النص كاملًا دفعة واحدة وهو مناسب لكل الحقول تقريبًا. يرسل pressSequentially مفتاحًا واحدًا في كل مرة، ويرسل press مفتاحًا أو اختصارًا مثل Control A.',
        'fill setzt den ganzen Text auf einmal und passt für fast jedes Feld. pressSequentially sendet eine Taste nach der anderen, und press sendet eine Taste oder ein Kürzel wie Control A.'),
    say('forms', 'Forms', 'check and uncheck tick boxes and radio buttons, selectOption picks from a drop down by value or label, and dates are filled in the year month day format.',
        'check और uncheck boxes और radio buttons को tick करते हैं, selectOption drop down से value या label से चुनता है, और dates साल महीना दिन format में भरी जाती हैं।',
        'check ಮತ್ತು uncheck boxes ಮತ್ತು radio buttons ಅನ್ನು tick ಮಾಡುತ್ತವೆ, selectOption drop down ನಿಂದ value ಅಥವಾ label ಮೂಲಕ ಆರಿಸುತ್ತದೆ, dates ವರ್ಷ ತಿಂಗಳು ದಿನ format ನಲ್ಲಿ ತುಂಬಲಾಗುತ್ತದೆ.',
        'check ଓ uncheck boxes ଓ radio buttons tick କରନ୍ତି, selectOption drop down ରୁ value ବା label ଦ୍ୱାରା ବାଛେ, ଏବଂ dates ବର୍ଷ ମାସ ଦିନ format ରେ ଭରାଯାଏ।',
        'يضع check وuncheck علامة في المربعات وأزرار الاختيار، ويختار selectOption من قائمة منسدلة بالقيمة أو التسمية، وتُملأ التواريخ بصيغة السنة ثم الشهر ثم اليوم.',
        'check und uncheck setzen Häkchen bei Kästchen und Optionsfeldern, selectOption wählt aus einer Liste nach Wert oder Beschriftung, und Daten werden im Format Jahr Monat Tag eingetragen.'),
    say('drag', 'Drag and drop', 'dragTo drags one element onto another in one line. For finer control, hover, press the mouse, move over the target twice and release.',
        'dragTo एक element को दूसरे पर एक line में खींचता है। ज़्यादा नियंत्रण के लिए hover करें, mouse दबाएँ, target पर दो बार ले जाएँ और छोड़ें।',
        'dragTo ಒಂದು element ಅನ್ನು ಇನ್ನೊಂದರ ಮೇಲೆ ಒಂದೇ line ನಲ್ಲಿ ಎಳೆಯುತ್ತದೆ. ಹೆಚ್ಚು ನಿಯಂತ್ರಣಕ್ಕೆ hover ಮಾಡಿ, mouse ಒತ್ತಿ, target ಮೇಲೆ ಎರಡು ಬಾರಿ ಸರಿಸಿ ಮತ್ತು ಬಿಡಿ.',
        'dragTo ଗୋଟିଏ element କୁ ଅନ୍ୟ ଉପରକୁ ଗୋଟିଏ line ରେ ଟାଣେ। ଅଧିକ ନିୟନ୍ତ୍ରଣ ପାଇଁ hover କରନ୍ତୁ, mouse ଦବାନ୍ତୁ, target ଉପରେ ଦୁଇଥର ନିଅନ୍ତୁ ଏବଂ ଛାଡନ୍ତୁ।',
        'يسحب dragTo عنصرًا فوق آخر في سطر واحد. للتحكم الأدق مرّر الفأرة واضغط زرها وحرّكها فوق الهدف مرتين ثم أفلتها.',
        'dragTo zieht ein Element in einer Zeile auf ein anderes. Für mehr Kontrolle: hovern, Maustaste drücken, zweimal über das Ziel bewegen und loslassen.'),
    say('wait', 'Waiting', 'Do not use fixed sleeps. Wait for the exact thing you need: an element state, a URL, a network response, or a condition in the page.',
        'Fixed sleep इस्तेमाल न करें। ठीक उसी चीज़ का इंतज़ार करें जो चाहिए: element की स्थिति, URL, network response, या page में कोई शर्त।',
        'Fixed sleep ಬಳಸಬೇಡಿ. ನಿಮಗೆ ಬೇಕಾದದ್ದಕ್ಕೇ ಕಾಯಿರಿ: element ಸ್ಥಿತಿ, URL, network response ಅಥವಾ page ನಲ್ಲಿ ಒಂದು ಷರತ್ತು.',
        'Fixed sleep ବ୍ୟବହାର କରନ୍ତୁ ନାହିଁ। ଯାହା ଦରକାର ଠିକ୍ ତାହା ପାଇଁ ଅପେକ୍ଷା କରନ୍ତୁ: element ସ୍ଥିତି, URL, network response ବା page ରେ ଏକ ସର୍ତ୍ତ।',
        'لا تستخدم الانتظار الثابت. انتظر الشيء الذي تحتاجه بالضبط: حالة عنصر أو عنوان URL أو استجابة شبكة أو شرطًا داخل الصفحة.',
        'Nutze keine festen Sleeps. Warte auf genau das, was du brauchst: einen Elementzustand, eine URL, eine Netzwerkantwort oder eine Bedingung in der Seite.'),
    say('practice', 'Playground labs', 'In the labs you send the feedback form as Ravi with a topic and a mood, and you drag a task into the Done lane.',
        'Labs में आप Ravi के रूप में topic और mood के साथ feedback form भेजते हैं, और एक task को Done lane में खींचते हैं।',
        'Labs ನಲ್ಲಿ ನೀವು Ravi ಆಗಿ topic ಮತ್ತು mood ಜೊತೆ feedback form ಕಳುಹಿಸುತ್ತೀರಿ, ಮತ್ತು ಒಂದು task ಅನ್ನು Done lane ಗೆ ಎಳೆಯುತ್ತೀರಿ.',
        'Labs ରେ ଆପଣ Ravi ଭାବେ topic ଓ mood ସହ feedback form ପଠାନ୍ତି, ଏବଂ ଗୋଟିଏ task କୁ Done lane କୁ ଟାଣନ୍ତି।',
        'في المختبرات ترسل نموذج الملاحظات باسم Ravi مع موضوع ومزاج، وتسحب مهمة إلى عمود Done.',
        'In den Labs sendest du das Feedback-Formular als Ravi mit Thema und Stimmung und ziehst eine Aufgabe in die Spalte Done.'),
]

QUIZ = [
    quiz(1, 'What does Playwright do before it clicks a button?', ['Nothing, it clicks at once', 'Waits a fixed 1 second', 'Checks the button is ready and retries until it is', 'Reloads the page'], 2,
         'Look at the auto-waiting table.', 'It checks visible, stable, receives events and enabled, and retries until they pass or the timeout ends.'),
    quiz(1, 'Which method fills a text box in one go?', ['type', 'fill', 'pressSequentially', 'press'], 1,
         'It is the one you use most.', '<code>fill</code> sets the whole value at once.'),
    quiz(1, 'How do you pick the Happy radio button labelled Happy?', ['click the label text twice', 'getByLabel(\'Happy\').check()', 'selectOption(\'Happy\')', 'fill(\'Happy\')'], 1,
         'Radio buttons are checked.', '<code>check()</code> works for checkboxes and radio buttons.'),
    quiz(1, 'Which line is a bad idea in a test?', ['await expect(x).toBeVisible()', 'await page.waitForTimeout(3000)', 'await x.click()', 'await x.fill(\'a\')'], 1,
         'It waits for the clock.', 'A fixed sleep is either too short or wastes time. Wait for the thing you need.'),
    quiz(2, 'A click times out. What tells you why?', ['The test name', 'The call log in the error message', 'The browser version', 'Nothing'], 1,
         'Look at the call log output.', 'The call log lists each check it tried, such as element is not enabled.'),
    quiz(2, 'Which check does fill do that click does not?', ['visible', 'editable', 'stable', 'receives events'], 1,
         'A read only box can be clicked but not typed into.', 'fill checks the element is editable. Click checks stable and receives events instead.'),
    quiz(2, 'When should you use pressSequentially instead of fill?', ['Always', 'When the box reacts to each key, like an auto complete', 'For passwords', 'Never'], 1,
         'What is different about key by key?', 'It sends one key event per character, which some boxes need to react.'),
    quiz(2, 'In which format do you fill a date input?', ['01/10/2026', '1 Oct 2026', '2026-10-01', 'any format'], 2,
         'Look at the form example.', 'Date inputs take the standard yyyy-mm-dd format, whatever the browser shows.'),
    quiz(2, 'What does trial: true do on a click?', ['Clicks twice', 'Runs the checks but does not click', 'Skips the checks', 'Retries the test'], 1,
         'It is a rehearsal.', 'Trial runs every actionability check without performing the click.'),
    quiz(3, 'Why do the docs suggest hovering the drop target twice when dragging by hand?', ['To be safe', 'Some pages need a dragover event, which needs at least two mouse moves', 'Java needs it', 'To scroll'], 1,
         'Read the drag example comment.', 'The dragover event needs at least two mouse moves in all browsers.'),
    quiz(3, 'In Python, how do you wait for the products API answer around a goto?', ['page.wait_for_response() after goto', 'with page.expect_response(...) as answer: page.goto(...)', 'time.sleep(1)', 'page.on("response")'], 1,
         'Python waits around the action.', 'The with block starts waiting before goto, so the answer cannot be missed.'),
    quiz(3, 'Which actions do no actionability checks at all?', ['click and fill', 'focus, press and setInputFiles', 'hover and dragTo', 'check and uncheck'], 1,
         'Look at the last row of the table.', 'focus, blur, press, pressSequentially, setInputFiles and dispatchEvent do no checks.'),
]

CALC = [
    calc(1, 'Pay now is disabled for 1000 ms and the cover is gone after 800 ms. After about how many ms can the click happen?', 1000,
         'Both must be true', ['The cover goes at 800 ms', 'The button is enabled at 1000 ms', 'The later of the two: 1000 ms']),
    calc(1, 'The To do lane has 2 tasks. You drag 1 to Done. How many are left in To do?', 1, '2 - 1', ['2 - 1 = 1']),
    calc(2, '200 tests each have a 3 second sleep. How many minutes are spent sleeping?', 10, '200 × 3 / 60', ['200 × 3 = 600 s', '600 / 60 = 10 minutes']),
    calc(2, 'pressSequentially types "mug" with a delay of 50 ms between keys. About how many ms does it take at least?', 150, '3 keys × 50 ms', ['3 characters', '3 × 50 = 150 ms']),
    calc(2, 'A click with a 2000 ms timeout retries a check about every 100 ms. About how many tries fit in?', 20, '2000 / 100', ['2000 / 100 = 20']),
    calc(3, 'A suite of 300 tests took 50 minutes. Removing sleeps saved 40 minutes. How many seconds did each test save on average?', 8,
         '40 × 60 / 300', ['40 minutes = 2400 s', '2400 / 300 = 8 s per test']),
    calc(3, 'The slider goes from 0 to 10 and you fill 8. What percent of the way is that?', 80, '8 / 10 × 100', ['8 / 10 = 0.8', '0.8 × 100 = 80 %']),
    calc(3, 'The offer appears 1200 ms after the click, and the default expect timeout is 5000 ms. How many ms of the timeout are left when it appears?', 3800, '5000 - 1200', ['5000 - 1200 = 3800 ms']),
]

LABS = [
    {'id': 'feedback', 'title': 'Send the feedback form', 'name': 'send feedback as Ravi',
     'task': 'On <code>/forms</code>, type <b>Ravi</b> as the name, choose the topic <b>Payment</b>, pick the mood <b>Okay</b>, click <b>Send feedback</b>, and check that the status contains <b>Topic: payment, mood: okay</b>.',
     'goal': 'The thank you line shows Ravi, payment and okay.', 'start': '/forms',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('send feedback as Ravi', async ({ page }) => {
  await page.goto('/forms');
  // fill the name, choose the topic, pick the mood, then send
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('send feedback as Ravi', async ({ page }) => {
  await page.goto('/forms');
  await page.getByLabel('Your name').fill('Ravi');
  await page.getByLabel('Topic').selectOption('payment');
  await page.getByLabel('Okay').check();
  await page.getByRole('button', { name: 'Send feedback' }).click();
  await expect(page.getByRole('status')).toContainText('Topic: payment, mood: okay');
});'''},
     'hint': "Use <code>getByLabel('Topic').selectOption('payment')</code> for the drop down and <code>getByLabel('Okay').check()</code> for the radio button.",
     'why': 'Every control is found by its label, and each has its own method: fill for text, selectOption for the drop down and check for the radio button.',
     'check': [["/Thanks Ravi/.test(ctx.text)", 'The form was sent as Ravi'], ["/Topic: payment, mood: okay/.test(ctx.text)", 'The topic and mood are right']]},
    {'id': 'dragdone', 'title': 'Drag a task to Done', 'name': 'move a task to done',
     'task': 'On <code>/forms</code>, drag <b>Print the label</b> from the To do lane into the <b>Done</b> lane, then check that the Done lane contains it.',
     'goal': 'Print the label sits in the Done lane.', 'start': '/forms',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('move a task to done', async ({ page }) => {
  await page.goto('/forms');
  const done = page.getByRole('list', { name: 'Done' });
  // drag the task onto the Done lane, then check it is there
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('move a task to done', async ({ page }) => {
  await page.goto('/forms');
  const done = page.getByRole('list', { name: 'Done' });
  await page.getByText('Print the label').dragTo(done);
  await expect(done).toContainText('Print the label');
});'''},
     'hint': "<code>page.getByText('Print the label').dragTo(done)</code>, then <code>expect(done).toContainText(...)</code>.",
     'why': 'dragTo presses the mouse on the task, moves it over the lane and releases it, so the page receives the same drag events as with a person.',
     'check': [["/dragTo|drag_to|DragTo|mouse/.test(ctx.code)", 'The test drags the task'], ["/Done/.test(ctx.code)", 'The test checks the Done lane']]},
]

T = {
    'slug': 'pw-actions', 'title': 'Actions and auto-waiting', 'short': 'Actions', 'emoji': '🖱️', 'module': MODULE, 'minutes': 24,
    'lead': 'Click, type, pick, drag and hover like a person, while Playwright waits for every element to be ready. Learn to read a timeout, fill every kind of form control, and replace every sleep with a wait for the real thing.',
    'desc': 'Auto-waiting and actionability checks, TimeoutError and the call log, force and trial, click options, hover, focus, fill, pressSequentially, press and keyboard shortcuts, check, selectOption, dates, dragTo, mouse, waitFor, waitForResponse and waitForFunction in Java, Python, JavaScript and TypeScript.',
    'summary': 'An interactive auto-waiting lab, a real click on a covered, disabled and moving button, the actionability table from the docs, the call log of a timeout, force and trial, click options and hover, fill versus pressSequentially, a recorded walk through a feedback form, every form control, drag and drop by dragTo and by hand, and waits that replace sleeps.',
    'keywords': ['auto-waiting', 'actionability', 'click', 'fill', 'pressSequentially', 'press', 'keyboard', 'hover', 'check', 'selectOption', 'dragTo', 'mouse', 'waitFor', 'waitForResponse', 'TimeoutError', 'force', 'sleep'],
    'plain': 'Tell Playwright what a person would do: click this, type that, pick this option. It waits for each element to be ready on its own, so a test needs no sleeps and does not break on a slow day.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
