import glob
import os
import subprocess

import pkit
from pkit import part, say, quiz, calc, panel, four, js, ts, py, jv, pom, table, tip, figure

MODULE = ('🔍', 'Debugging and quality', 'pw-quality', 'Finding out why a test failed with errors, traces, reports, UI mode and the Inspector, then checking how pages look, read and behave on every device.')

IMG = os.path.join(os.path.dirname(os.path.abspath(pkit.__file__)), '..', '..', 'content', 'playwright', 'img')

JAVA_TRIM = [(r'(?ms)^\tat .*?(?=^\[INFO\]|^\[ERROR\]|^\[WARNING\]|^Run \d|^[a-z]|\Z)', ''), (r'(?m)^\[ERROR\] (Please refer|To see the full|Re-run Maven|For more information|-> \[Help|\s*$).*\n?', ''),
             (r'(?m)^\[ERROR\] Failed to execute goal.*\n', ''), (r'(?ms)^\[INFO\] \n\[INFO\] Results:.*?(?=^\[ERROR\] Tests run:|^\[WARNING\] Tests run:)', '')]


def keep_diff(d, port, res):
    """Save the expected, actual and diff images of the failed comparison side by side, for the figure."""
    parts = []
    for kind in ('expected', 'actual', 'diff'):
        found = glob.glob(os.path.join(d, 'test-results', '**', f'lamp-card-{kind}.png'), recursive=True)
        if not found:
            return
        parts.append(found[0])
    subprocess.run(['convert', *parts, '-bordercolor', 'white', '-border', '12', '+append', '-quality', '88',
                    os.path.join(IMG, 'visual-lamp-diff.jpg')], check=True)


# ---------- 1. screenshots compared with a saved picture (Playwright Test only) ----------
SHOT_CONFIG = '''import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  reporter: 'list',
  expect: {
    toHaveScreenshot: { maxDiffPixels: 10 },   // allow up to 10 pixels to differ
  },
  use: { baseURL: 'http://localhost:4173' },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});'''

SHOT_TS = '''import { test, expect } from '@playwright/test';

test('the products page looks right', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByRole('listitem')).toHaveCount(5);
  await expect(page).toHaveScreenshot('products.png', { fullPage: true });
});

test('the lamp card looks right', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByTestId('product-3')).toHaveScreenshot('lamp-card.png');
});

test('a button colour changed by mistake', async ({ page }) => {
  await page.goto('/products');
  await page.addStyleTag({ content: '.card button { background: #b91c1c; }' });   // a style bug, on purpose
  await expect(page.getByTestId('product-3')).toHaveScreenshot('lamp-card.png');
});'''

SHOT_CMD = 'npx playwright test -g "looks right" --update-snapshots && npx playwright test ; s=$?; find tests test-results -name "*.png" | sort; exit $s'
SHOT_SHOWN = 'npx playwright test -g "looks right" --update-snapshots\n$ npx playwright test\n$ find tests test-results -name "*.png"'
SHOT_TRIM = [(r'(?ms)^\s+attachment #\d.*?─{20,}\n(?:.*\n)*?\s+─{20,}\n', ''), (r'(?m)^\s+Error Context: .*\n', '')]

# ---------- 2. aria snapshots: the structure, in every language ----------
ARIA_TS = '''import { test, expect } from '@playwright/test';

test('the main menu has four links', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByRole('navigation', { name: 'Main' })).toMatchAriaSnapshot(`
    - navigation "Main":
      - link "Products"
      - link "Feedback"
      - link "Widgets"
      - link "Orders"
  `);
});

test('the notebook card says it is out of stock', async ({ page }) => {
  await page.goto('/products');
  console.log(await page.getByTestId('product-4').ariaSnapshot());   // print it once, then paste it below
  await expect(page.getByTestId('product-4')).toMatchAriaSnapshot(`
    - listitem:
      - heading "Notebook" [level=3]
      - text: Stationery ₹60
      - button "Out of stock" [disabled]
  `);
});'''

ARIA_PY = '''from playwright.sync_api import Page, expect


def test_the_main_menu_has_four_links(page: Page):
    page.goto("/products")
    expect(page.get_by_role("navigation", name="Main")).to_match_aria_snapshot("""
        - navigation "Main":
          - link "Products"
          - link "Feedback"
          - link "Widgets"
          - link "Orders"
    """)


def test_the_notebook_card_says_it_is_out_of_stock(page: Page):
    page.goto("/products")
    print(page.get_by_test_id("product-4").aria_snapshot())   # print it once, then paste it below
    expect(page.get_by_test_id("product-4")).to_match_aria_snapshot("""
        - listitem:
          - heading "Notebook" [level=3]
          - text: Stationery ₹60
          - button "Out of stock" [disabled]
    """)'''

ARIA_JAVA = '''package com.brainy;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class StructureTest {
  @Test
  void theMainMenuHasFourLinks(Page page) {
    page.navigate("/products");
    assertThat(page.getByRole(AriaRole.NAVIGATION, new Page.GetByRoleOptions().setName("Main"))).matchesAriaSnapshot("""
        - navigation "Main":
          - link "Products"
          - link "Feedback"
          - link "Widgets"
          - link "Orders"
        """);
  }

  @Test
  void theNotebookCardSaysItIsOutOfStock(Page page) {
    page.navigate("/products");
    System.out.println(page.getByTestId("product-4").ariaSnapshot());   // print it once, then paste it below
    assertThat(page.getByTestId("product-4")).matchesAriaSnapshot("""
        - listitem:
          - heading "Notebook" [level=3]
          - text: Stationery ₹60
          - button "Out of stock" [disabled]
        """);
  }
}'''

# ---------- 3. an accessibility scan with axe ----------
AXE_TS = '''import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('the offers page has no accessibility problems', async ({ page }) => {
  await page.goto('/a11y');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])          // the WCAG 2 A and AA rules
    .analyze();
  for (const v of results.violations) {
    console.log(`${v.id} (${v.impact}): ${v.nodes.length} element(s). ${v.help}`);
  }
  expect(results.violations.map(v => v.id)).toEqual([]);
});'''

AXE_PY = '''from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page


def test_the_offers_page_has_no_accessibility_problems(page: Page):
    page.goto("/a11y")
    results = Axe().run(page, options={"runOnly": ["wcag2a", "wcag2aa"]})   # the WCAG 2 A and AA rules
    for v in results.response["violations"]:
        print(f"{v['id']} ({v['impact']}): {len(v['nodes'])} element(s). {v['help']}")
    assert [v["id"] for v in results.response["violations"]] == []'''

AXE_JAVA = '''package com.brainy;

import com.deque.html.axecore.playwright.AxeBuilder;
import com.deque.html.axecore.results.AxeResults;
import com.deque.html.axecore.results.Rule;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

@UsePlaywright(ShopOptions.class)
public class OffersAccessibilityTest {
  @Test
  void theOffersPageHasNoAccessibilityProblems(Page page) {
    page.navigate("/a11y");
    AxeResults results = new AxeBuilder(page)
        .withTags(List.of("wcag2a", "wcag2aa"))      // the WCAG 2 A and AA rules
        .analyze();
    for (Rule v : results.getViolations()) {
      System.out.println(v.getId() + " (" + v.getImpact() + "): " + v.getNodes().size() + " element(s). " + v.getHelp());
    }
    assertEquals(List.of(), results.getViolations().stream().map(Rule::getId).toList());
  }
}'''

AXE_DEP = '''
    <dependency>
      <groupId>com.deque.html.axe-core</groupId>
      <artifactId>playwright</artifactId>
      <version>4.14.0</version>
      <scope>test</scope>
    </dependency>'''

AXE_PY_TRIM = [(r'(?ms)^(tests/test_offers\.py:\d+: AssertionError)', r'\1')]

# ---------- 4. a fake clock: dates and timers on demand ----------
CLOCK_TS = '''import { test, expect } from '@playwright/test';

test('the sale is not live the day before', async ({ page }) => {
  await page.clock.setFixedTime(new Date('2026-12-24T12:00:00Z'));
  await page.goto('/clock');
  await expect(page.getByRole('status')).toHaveText('The Christmas sale is coming soon');
});

test('the sale goes live on Christmas Day', async ({ page }) => {
  await page.clock.setFixedTime(new Date('2026-12-25T12:00:00Z'));
  await page.goto('/clock');
  await expect(page.getByRole('status')).toHaveText('The Christmas sale is live');
});

test('an idle user is signed out after 5 minutes', async ({ page }) => {
  await page.clock.install({ time: new Date('2026-12-24T10:00:00Z') });
  await page.goto('/clock');
  await page.clock.runFor('05:00');                     // 5 minutes of timers, in a moment
  await expect(page.getByRole('alert')).toHaveText('You were signed out');
});'''

CLOCK_PY = '''from playwright.sync_api import Page, expect


def test_the_sale_is_not_live_the_day_before(page: Page):
    page.clock.set_fixed_time("2026-12-24T12:00:00Z")
    page.goto("/clock")
    expect(page.get_by_role("status")).to_have_text("The Christmas sale is coming soon")


def test_the_sale_goes_live_on_christmas_day(page: Page):
    page.clock.set_fixed_time("2026-12-25T12:00:00Z")
    page.goto("/clock")
    expect(page.get_by_role("status")).to_have_text("The Christmas sale is live")


def test_an_idle_user_is_signed_out_after_5_minutes(page: Page):
    page.clock.install(time="2026-12-24T10:00:00Z")
    page.goto("/clock")
    page.clock.run_for("05:00")                          # 5 minutes of timers, in a moment
    expect(page.get_by_role("alert")).to_have_text("You were signed out")'''

CLOCK_JAVA = '''package com.brainy;

import com.microsoft.playwright.Clock;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@UsePlaywright(ShopOptions.class)
public class SaleClockTest {
  @Test
  void theSaleIsNotLiveTheDayBefore(Page page) {
    page.clock().setFixedTime("2026-12-24T12:00:00Z");
    page.navigate("/clock");
    assertThat(page.getByRole(AriaRole.STATUS)).hasText("The Christmas sale is coming soon");
  }

  @Test
  void theSaleGoesLiveOnChristmasDay(Page page) {
    page.clock().setFixedTime("2026-12-25T12:00:00Z");
    page.navigate("/clock");
    assertThat(page.getByRole(AriaRole.STATUS)).hasText("The Christmas sale is live");
  }

  @Test
  void anIdleUserIsSignedOutAfterFiveMinutes(Page page) {
    page.clock().install(new Clock.InstallOptions().setTime("2026-12-24T10:00:00Z"));
    page.navigate("/clock");
    page.clock().runFor("05:00");                        // 5 minutes of timers, in a moment
    assertThat(page.getByRole(AriaRole.ALERT)).hasText("You were signed out");
  }
}'''

shot_ts = ts({'look.spec.ts': SHOT_TS}, config=SHOT_CONFIG, cmd=SHOT_CMD, shown_cmd=SHOT_SHOWN, expect='fail', replace=SHOT_TRIM)
shot_ts['after'] = keep_diff

CODES = {
    'screenshot': four('Compare the page with a saved picture',
                       js=js({'look.spec.js': SHOT_TS}, config=SHOT_CONFIG, cmd=SHOT_CMD, shown_cmd=SHOT_SHOWN, expect='fail', replace=SHOT_TRIM),
                       ts=shot_ts,
                       result='The first command saved two pictures, products-chromium-linux.png and lamp-card-chromium-linux.png, next to the test file. The second run compared the page with them. The two tests that changed nothing passed. The third test made the buttons red, the way a bad style change would, and failed with the number of pixels that differ. Playwright saved the expected picture, the actual picture and a diff for the report.'),
    'aria': four('Check the structure of the page with an aria snapshot',
                 java=jv({'StructureTest.java': ARIA_JAVA}),
                 py=py({'test_structure.py': ARIA_PY}, cmd='pytest -v -s'),
                 js=js({'structure.spec.js': ARIA_TS}),
                 ts=ts({'structure.spec.ts': ARIA_TS}),
                 result='Both checks passed in every language. An aria snapshot is the page as a screen reader sees it: roles, names and states, written as YAML. The printed snapshot of the notebook card is the one pasted into the check, which is how most snapshots are written. Leaving out a part, such as the /url of each link, still matches, so a check only states what matters.'),
    'axe': four('Scan a page for accessibility problems with axe',
                java=jv({'OffersAccessibilityTest.java': AXE_JAVA}, pom_xml=pom('junit', AXE_DEP), expect='fail', replace=JAVA_TRIM),
                py=py({'test_offers.py': AXE_PY}, cmd='pytest -v -s', expect='fail'),
                js=js({'offers.spec.js': AXE_TS}, expect='fail'),
                ts=ts({'offers.spec.ts': AXE_TS}, expect='fail'),
                result='The scan failed on purpose, because the offers page was built with common mistakes. axe found the same two rule breaks in every language and listed each with how serious it is, how many elements break it and a one line help text. The JavaScript and Java libraries come from Deque, the makers of axe. The Python one, axe-playwright-python, is a community package with its own copy of axe, so its rule versions can lag a little behind.'),
    'clock': four('Control dates and timers with a fake clock',
                  java=jv({'SaleClockTest.java': CLOCK_JAVA}),
                  py=py({'test_clock.py': CLOCK_PY}),
                  js=js({'clock.spec.js': CLOCK_TS}),
                  ts=ts({'clock.spec.ts': CLOCK_TS}),
                  result='All three tests passed in well under a second each. setFixedTime made the page think it was 24 or 25 December 2026, so both sides of the sale date were tested without waiting for Christmas. install replaced the page timers, and runFor ran five minutes of them at once, so the idle sign out happened straight away.'),
}

DG = {
    'layers': {'t': 'Four checks, four kinds of mistake', 'w': 900, 'h': 230,
               'n': [['page', 20, 83, 140, 64, 'one page', {'c': 5, 'sub': 'the shop', 'i': 'The same page can break in ways that functional checks do not notice.'}],
                     ['look', 250, 10, 170, 56, 'screenshot', {'c': 1, 'sub': 'how it looks', 'i': 'toHaveScreenshot catches colours, layout and fonts that changed.'}],
                     ['tree', 250, 86, 170, 56, 'aria snapshot', {'c': 2, 'sub': 'how it reads', 'i': 'toMatchAriaSnapshot catches a missing heading, a renamed button or a lost label.'}],
                     ['axe', 250, 162, 170, 56, 'axe scan', {'c': 3, 'sub': 'who can use it', 'i': 'axe catches images without text, low contrast and fields without labels.'}],
                     ['time', 500, 83, 170, 64, 'fake clock', {'c': 0, 'sub': 'when it changes', 'i': 'The clock tests what the page does on a given date or after a given time.'}],
                     ['ok', 750, 83, 130, 64, 'release', {'c': 4, 'sub': 'with confidence', 'i': 'A page that passes all four looks right, reads right, works for everyone and on every date.'}]],
               'e': [['page', 'look'], ['page', 'tree'], ['page', 'axe'], ['look', 'time'], ['tree', 'time'], ['axe', 'time'], ['time', 'ok']],
               'st': [[['page'], 'A page can pass every click test and still be broken.'],
                      [['look', 'page>look'], 'A screenshot comparison sees how it looks.'],
                      [['tree', 'page>tree'], 'An aria snapshot sees how it reads to a screen reader.'],
                      [['axe', 'page>axe'], 'An axe scan finds barriers for disabled users.'],
                      [['time', 'look>time', 'tree>time', 'axe>time'], 'A fake clock tests dates and timers without waiting.'],
                      [['ok', 'time>ok'], 'Together they cover what plain checks miss.']]},
}

PARTS = [
    part('visual', '🖼️', 'Visual comparisons', f'''
<p>A test can click every button and still miss that the buttons turned red. A <b>visual comparison</b> takes a screenshot and compares it, pixel by pixel, with a picture saved earlier, called the <b>baseline</b>. Playwright Test has this built in as <code>toHaveScreenshot</code>.</p>
<div class="viz" data-viz="flow" data-k="layers"></div>
[[screenshot]]
{figure('visual-lamp-diff.jpg', 'Three images of the Desk lamp card: the expected one with a green button, the actual one with a red button, and the diff with the changed pixels in red', 'The pictures from the failed comparison above: expected, actual and the diff, where every changed pixel is marked in red. The HTML report shows them with a slider to compare.')}
{table(['Option', 'What it does'], [
    ['--update-snapshots', 'saves new baselines instead of comparing, after a change you meant to make'],
    ['maxDiffPixels, maxDiffPixelRatio', 'how many pixels, or what share of them, may differ'],
    ['threshold', 'how different one pixel may be before it counts, from 0 to 1, default 0.2'],
    ['mask: [locator]', 'covers parts that change every run, such as a date or an advert, with a box'],
    ['animations: "disabled"', 'stops CSS animations so the picture is the same every time (the default)'],
    ['stylePath', 'adds a style sheet only while taking the picture, for example to hide a clock'],
])}
{tip('Baselines depend on the operating system and the browser, which is why the file name ends in chromium-linux. Make them on the same system that runs the tests, usually the CI image or the Playwright Docker image, and commit them to the repository.', 'pro')}
{tip('toHaveScreenshot is part of Playwright Test. Python and Java have page.screenshot() to save a picture, but no comparison built in. Teams add a library for it or use a visual testing service. The aria snapshot below works in every language.', 'warn')}
''', kw=['visual comparison', 'toHaveScreenshot', 'baseline', 'update-snapshots', 'maxDiffPixels', 'mask', 'pixel diff']),

    part('aria', '🌳', 'Aria snapshots', f'''
<p>An <b>aria snapshot</b> describes a part of the page the way assistive technology sees it: each element's role, its name and its state, nested in YAML. Compare it with a saved version and you check the structure, not the pixels, so a new font or colour does not break it.</p>
[[aria]]
{table(['', 'Playwright Test', 'Python', 'Java'], [
    ['print a snapshot', "await locator.ariaSnapshot()", 'locator.aria_snapshot()', 'locator.ariaSnapshot()'],
    ['check a snapshot', 'toMatchAriaSnapshot(`...`)', 'to_match_aria_snapshot("""...""")', 'matchesAriaSnapshot("""...""")'],
    ['keep it in a file', 'toMatchAriaSnapshot({ name: "menu.aria.yml" })', 'not built in', 'not built in'],
])}
{tip('Codegen can record aria snapshots too: use the Assert snapshot button in the toolbar while recording, and the snapshot of the element you click is added to the test.', 'tip')}
''', easy=True, kw=['aria snapshot', 'toMatchAriaSnapshot', 'ariaSnapshot', 'accessibility tree', 'YAML', 'structure']),

    part('a11y', '♿', 'Accessibility scans with axe', f'''
<p>Many people use a screen reader, a keyboard only or high contrast. <b>axe</b> is an open source engine from Deque that checks a page against rules from WCAG, the web accessibility guidelines. Playwright runs it inside the page and gives you the list of problems.</p>
[[axe]]
{table(['What axe found', 'Why it matters', 'The fix'], [
    ['image-alt: the lamp image has no alt text', 'a screen reader cannot say what the picture shows', 'add alt="Desk lamp"'],
    ['color-contrast: light blue text on a light background', 'people with low vision cannot read it', 'use a darker colour, with a contrast ratio of at least 4.5 to 1'],
])}
<p>The scan passed two things on the same page that a person would still question. The bell button has the text 🔔, so it has a name, but a screen reader may read it as just "bell". The email field has only a placeholder, which axe accepts as a name, but the hint disappears as soon as someone starts typing. A scan finds rule breaks. It cannot judge whether a name is helpful.</p>
{table(['Package', 'Language', 'Made by'], [
    ['@axe-core/playwright', 'JavaScript and TypeScript', 'Deque'],
    ['com.deque.html.axe-core:playwright', 'Java', 'Deque'],
    ['axe-playwright-python', 'Python', 'community'],
])}
{tip('An automatic scan finds only part of the problems. It cannot tell whether alt text is useful or whether the tab order makes sense. Keep a few manual checks with a keyboard and a screen reader, and use the scan to stop the easy mistakes from coming back.', 'warn')}
{tip('An old page may have many known problems. Scan with .exclude() for the parts you will fix later, or compare the list of violations with a saved list, so new problems still fail the test.', 'pro')}
''', kw=['accessibility', 'axe', 'axe-core', 'WCAG', 'AxeBuilder', 'violations', 'a11y', 'screen reader']),

    part('clock', '⏰', 'Fake time with page.clock', f'''
<p>Some pages change with the date or after a delay: a sale that starts at midnight, a session that ends after 5 minutes, a countdown. Waiting for the real time is slow or impossible. <b>page.clock</b> replaces the page's Date and timers with a fake clock that you control.</p>
[[clock]]
{table(['Method', 'What it does'], [
    ['setFixedTime(time)', 'Date.now() always returns this time. Timers still run normally.'],
    ['install({ time })', 'replaces Date and every timer. Call it before the page loads.'],
    ['runFor("05:00")', 'moves forward, firing every timer that falls due on the way'],
    ['fastForward("05:00")', 'jumps forward and fires due timers at most once, like a laptop waking from sleep'],
    ['pauseAt(time), resume()', 'stops time at a moment to check the page, then lets it run again'],
    ['setSystemTime(time)', 'changes the date without firing timers, like a user changing the system clock'],
])}
{tip('Use setFixedTime when the page only reads the date, and install with runFor when it uses setTimeout or setInterval. Either way the test runs in milliseconds and gives the same result on every day of the year.', 'tip')}
''', kw=['clock', 'page.clock', 'setFixedTime', 'install', 'runFor', 'fastForward', 'fake timers', 'date']),
]

INFO = {'title': 'Beyond clicks and text', 'panels': [
    panel([['e', '🖼️'], ['t', 'pixels', {'b': 1}]], 'Screenshot', 'How it looks.', 'Baseline and diff.'),
    panel([['e', '🌳'], ['t', 'tree', {'b': 1}]], 'Aria snapshot', 'How it reads.', 'Every language.'),
    panel([['e', '♿'], ['t', 'axe', {'b': 1}]], 'axe scan', 'Who can use it.', 'WCAG rules.'),
    panel([['e', '⏰'], ['t', 'clock', {'b': 1}]], 'Fake clock', 'Any date, any delay.', 'No waiting.')],
    'remember': 'Screenshots check pixels, aria snapshots check structure, axe checks access, and the clock checks time. Use each for the mistakes it is good at.'}

REAL = [
    ['🎨', 'The style change that broke checkout', 'A designer changes a shared button style. Every functional test passes, but the screenshot test of the checkout page fails: the Pay button is now white on white. The change is fixed before release.'],
    ['♿', 'A scan on every pull request', 'A public service runs an axe scan on its 20 most used pages in CI. A new form field without a label fails the build the same day, instead of reaching users who rely on screen readers.'],
    ['🎄', 'Testing Christmas in July', 'An online shop tests its holiday banner, its midnight price change and its New Year sale with page.clock, so the tests pass on any day of the year and every rule is checked before the date arrives.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter checks what plain tests miss: how a page looks with screenshot comparisons, how it reads with aria snapshots, who can use it with an axe scan, and how it behaves on a date or after a delay with a fake clock.',
        'यह अध्याय वह जाँचता है जो साधारण tests छोड़ देते हैं: screenshot comparison से page कैसा दिखता है, aria snapshot से वह कैसा पढ़ा जाता है, axe scan से कौन उसे इस्तेमाल कर सकता है, और fake clock से किसी तारीख या देरी के बाद वह कैसा व्यवहार करता है।',
        'ಈ ಅಧ್ಯಾಯ ಸಾಮಾನ್ಯ tests ಬಿಟ್ಟುಬಿಡುವುದನ್ನು ಪರಿಶೀಲಿಸುತ್ತದೆ: screenshot comparison ನಿಂದ page ಹೇಗೆ ಕಾಣುತ್ತದೆ, aria snapshot ನಿಂದ ಹೇಗೆ ಓದಲ್ಪಡುತ್ತದೆ, axe scan ನಿಂದ ಯಾರು ಬಳಸಬಹುದು, fake clock ನಿಂದ ಒಂದು ದಿನಾಂಕ ಅಥವಾ ವಿಳಂಬದ ನಂತರ ಹೇಗೆ ವರ್ತಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ ସାଧାରଣ tests ଛାଡିଦେଉଥିବା ଜିନିଷ ଯାଞ୍ଚ କରେ: screenshot comparison ରେ page କେମିତି ଦେଖାଯାଏ, aria snapshot ରେ କେମିତି ପଢାଯାଏ, axe scan ରେ କିଏ ବ୍ୟବହାର କରିପାରିବ, ଏବଂ fake clock ରେ ଏକ ତାରିଖ ବା ବିଳମ୍ବ ପରେ କେମିତି ବ୍ୟବହାର କରେ।',
        'يفحص هذا الفصل ما تفوته الاختبارات العادية: كيف تبدو الصفحة بمقارنة لقطات الشاشة، وكيف تُقرأ بلقطة aria، ومن يستطيع استخدامها بفحص axe، وكيف تتصرف في تاريخ معين أو بعد مهلة بساعة مزيفة.',
        'Dieses Kapitel prüft, was normale Tests übersehen: wie eine Seite aussieht, mit Screenshot-Vergleichen, wie sie gelesen wird, mit Aria-Snapshots, wer sie benutzen kann, mit einem axe-Scan, und wie sie sich an einem Datum oder nach einer Wartezeit verhält, mit einer falschen Uhr.'),
    say('visual', 'Visual comparisons', 'toHaveScreenshot compares a screenshot with a saved baseline and fails when too many pixels differ. Update the baseline with --update-snapshots after a change you meant to make. It is part of Playwright Test.',
        'toHaveScreenshot एक screenshot की तुलना saved baseline से करता है और बहुत ज़्यादा pixels अलग हों तो fail होता है। जानबूझकर किए बदलाव के बाद --update-snapshots से baseline बदलें। यह Playwright Test का हिस्सा है।',
        'toHaveScreenshot screenshot ಅನ್ನು saved baseline ಜೊತೆ ಹೋಲಿಸುತ್ತದೆ, ತುಂಬಾ pixels ಬೇರೆಯಾದರೆ fail ಆಗುತ್ತದೆ. ಉದ್ದೇಶಪೂರ್ವಕ ಬದಲಾವಣೆಯ ನಂತರ --update-snapshots ನಿಂದ baseline ಬದಲಿಸಿ. ಇದು Playwright Test ನ ಭಾಗ.',
        'toHaveScreenshot ଏକ screenshot କୁ saved baseline ସହ ତୁଳନା କରେ ଏବଂ ଅଧିକ pixels ଭିନ୍ନ ହେଲେ fail ହୁଏ। ଜାଣିଶୁଣି କରିଥିବା ପରିବର୍ତ୍ତନ ପରେ --update-snapshots ରେ baseline ବଦଳାନ୍ତୁ। ଏହା Playwright Test ର ଅଂଶ।',
        'يقارن toHaveScreenshot لقطة الشاشة بصورة أساس محفوظة ويفشل إذا اختلف عدد كبير من البكسلات. حدّث الصورة الأساس بالخيار ‎--update-snapshots بعد تغيير مقصود. وهو جزء من Playwright Test.',
        'toHaveScreenshot vergleicht einen Screenshot mit einer gespeicherten Basis und schlägt fehl, wenn zu viele Pixel abweichen. Nach einer gewollten Änderung aktualisierst du die Basis mit --update-snapshots. Es gehört zu Playwright Test.'),
    say('aria', 'Aria snapshots', 'An aria snapshot is the page as a screen reader sees it: roles, names and states in YAML. toMatchAriaSnapshot compares it with a saved version and works in every language.',
        'Aria snapshot page को वैसे दिखाता है जैसे screen reader देखता है: roles, names और states YAML में। toMatchAriaSnapshot इसे saved version से मिलाता है और हर भाषा में काम करता है।',
        'Aria snapshot ಎಂದರೆ screen reader ನೋಡುವಂತೆ page: roles, names ಮತ್ತು states YAML ನಲ್ಲಿ. toMatchAriaSnapshot ಅದನ್ನು saved version ಜೊತೆ ಹೋಲಿಸುತ್ತದೆ ಮತ್ತು ಎಲ್ಲಾ ಭಾಷೆಗಳಲ್ಲಿ ಕೆಲಸ ಮಾಡುತ್ತದೆ.',
        'Aria snapshot ହେଉଛି screen reader ଦେଖୁଥିବା ପରି page: roles, names ଓ states YAML ରେ। toMatchAriaSnapshot ଏହାକୁ saved version ସହ ତୁଳନା କରେ ଏବଂ ସବୁ ଭାଷାରେ କାମ କରେ।',
        'لقطة aria هي الصفحة كما يراها قارئ الشاشة: الأدوار والأسماء والحالات بصيغة YAML. يقارنها toMatchAriaSnapshot بنسخة محفوظة ويعمل في كل اللغات.',
        'Ein Aria-Snapshot ist die Seite so, wie ein Screenreader sie sieht: Rollen, Namen und Zustände in YAML. toMatchAriaSnapshot vergleicht ihn mit einer gespeicherten Fassung und funktioniert in jeder Sprache.'),
    say('a11y', 'Accessibility scans', 'axe checks a page against WCAG rules and lists each problem with its impact and the elements involved. Deque makes the JavaScript and Java packages, and a community package covers Python. A scan finds only part of the problems, so keep some manual checks.',
        'axe page को WCAG नियमों से जाँचता है और हर समस्या को उसके असर और elements के साथ बताता है। Deque JavaScript और Java packages बनाता है, और Python के लिए community package है। Scan केवल कुछ समस्याएँ ढूँढता है, इसलिए कुछ manual checks रखें।',
        'axe page ಅನ್ನು WCAG ನಿಯಮಗಳ ಜೊತೆ ಪರಿಶೀಲಿಸಿ ಪ್ರತಿ ಸಮಸ್ಯೆಯನ್ನು ಅದರ ಪರಿಣಾಮ ಮತ್ತು elements ಜೊತೆ ಪಟ್ಟಿ ಮಾಡುತ್ತದೆ. Deque JavaScript ಮತ್ತು Java packages ಮಾಡುತ್ತದೆ, Python ಗೆ community package ಇದೆ. Scan ಕೆಲವು ಸಮಸ್ಯೆಗಳನ್ನು ಮಾತ್ರ ಕಂಡುಹಿಡಿಯುತ್ತದೆ, ಆದ್ದರಿಂದ manual checks ಇಡಿ.',
        'axe page କୁ WCAG ନିୟମ ସହ ଯାଞ୍ଚ କରେ ଏବଂ ପ୍ରତି ସମସ୍ୟାକୁ ତାର ପ୍ରଭାବ ଓ elements ସହ ତାଲିକା କରେ। Deque JavaScript ଓ Java packages ତିଆରି କରେ, ଏବଂ Python ପାଇଁ community package ଅଛି। Scan କେବଳ କିଛି ସମସ୍ୟା ଖୋଜେ, ତେଣୁ କିଛି manual checks ରଖନ୍ତୁ।',
        'يفحص axe الصفحة وفق قواعد WCAG ويعرض كل مشكلة مع أثرها والعناصر المعنية. تصنع Deque حزمتي JavaScript وJava، وتغطي حزمة مجتمعية لغة Python. ولا يجد الفحص إلا جزءًا من المشكلات، لذا أبقِ بعض الفحوص اليدوية.',
        'axe prüft eine Seite nach den WCAG-Regeln und listet jedes Problem mit seiner Schwere und den betroffenen Elementen. Deque baut die Pakete für JavaScript und Java, für Python gibt es ein Community-Paket. Ein Scan findet nur einen Teil der Probleme, also behalte einige manuelle Prüfungen.'),
    say('clock', 'Fake time', 'page.clock controls Date and timers in the page. setFixedTime sets the date, install with runFor runs timers forward, so a sale date or a 5 minute sign out is tested in milliseconds.',
        'page.clock page में Date और timers को नियंत्रित करता है। setFixedTime तारीख तय करता है, install और runFor timers को आगे चलाते हैं, इसलिए sale की तारीख या 5 minute का sign out milliseconds में test होता है।',
        'page.clock page ನಲ್ಲಿ Date ಮತ್ತು timers ನಿಯಂತ್ರಿಸುತ್ತದೆ. setFixedTime ದಿನಾಂಕ ಹೊಂದಿಸುತ್ತದೆ, install ಮತ್ತು runFor timers ಮುಂದೆ ಓಡಿಸುತ್ತವೆ, ಆದ್ದರಿಂದ sale ದಿನಾಂಕ ಅಥವಾ 5 minute sign out milliseconds ನಲ್ಲಿ test ಆಗುತ್ತದೆ.',
        'page.clock page ରେ Date ଓ timers ନିୟନ୍ତ୍ରଣ କରେ। setFixedTime ତାରିଖ ସ୍ଥିର କରେ, install ଓ runFor timers ଆଗକୁ ଚଳାନ୍ତି, ତେଣୁ sale ତାରିଖ ବା 5 minute sign out milliseconds ରେ test ହୁଏ।',
        'يتحكم page.clock في Date والمؤقتات داخل الصفحة. يضبط setFixedTime التاريخ، ويدفع install مع runFor المؤقتات إلى الأمام، فيُختبر موعد التخفيضات أو تسجيل الخروج بعد 5 دقائق في أجزاء من الثانية.',
        'page.clock steuert Date und Timer in der Seite. setFixedTime setzt das Datum, install mit runFor lässt Timer vorlaufen, sodass ein Verkaufsdatum oder eine Abmeldung nach 5 Minuten in Millisekunden getestet wird.'),
    say('practice', 'Playground labs', 'In the labs you check the shop the way a screen reader would: find the cart link by its accessible name, and check that the products list is named and holds five products.',
        'Labs में आप shop को वैसे जाँचते हैं जैसे screen reader करेगा: cart link को उसके accessible name से ढूँढते हैं, और जाँचते हैं कि products list का नाम है और उसमें पाँच products हैं।',
        'Labs ನಲ್ಲಿ screen reader ಮಾಡುವಂತೆ shop ಪರಿಶೀಲಿಸುತ್ತೀರಿ: cart link ಅನ್ನು ಅದರ accessible name ನಿಂದ ಹುಡುಕುತ್ತೀರಿ, products list ಗೆ ಹೆಸರಿದೆ ಮತ್ತು ಐದು products ಇವೆ ಎಂದು ಪರಿಶೀಲಿಸುತ್ತೀರಿ.',
        'Labs ରେ screen reader କରିବା ପରି shop ଯାଞ୍ଚ କରନ୍ତି: cart link କୁ ତାର accessible name ରୁ ଖୋଜନ୍ତି, ଏବଂ products list ର ନାମ ଅଛି ଓ ସେଥିରେ ପାଞ୍ଚଟି products ଅଛି ବୋଲି ଯାଞ୍ଚ କରନ୍ତି।',
        'في المختبرات تفحص المتجر كما يفعل قارئ الشاشة: تجد رابط السلة باسمه المتاح، وتتحقق من أن قائمة المنتجات لها اسم وتحتوي على خمسة منتجات.',
        'In den Labs prüfst du den Shop so, wie ein Screenreader es täte: Du findest den Warenkorb-Link über seinen zugänglichen Namen und prüfst, dass die Produktliste einen Namen hat und fünf Produkte enthält.'),
]

QUIZ = [
    quiz(1, 'What does toHaveScreenshot compare the page with?', ['the live site', 'a saved baseline picture', 'the HTML source', 'the trace'], 1,
         'It is saved the first time.', 'It compares a new screenshot with the baseline saved earlier.'),
    quiz(1, 'Which flag saves new baselines after a change you meant to make?', ['--headed', '--update-snapshots', '--reset', '--save'], 1,
         'It updates them.', '--update-snapshots writes the current screenshots as the new baselines.'),
    quiz(1, 'What does an aria snapshot describe?', ['pixels', 'roles, names and states, as assistive technology sees them', 'network calls', 'CSS rules'], 1,
         'Think of a screen reader.', 'It is the accessibility tree of a part of the page, written in YAML.'),
    quiz(1, 'What is axe?', ['a browser', 'an engine that checks pages against accessibility rules', 'a reporter', 'a CI tool'], 1,
         'Made by Deque.', 'axe-core checks pages against WCAG rules and lists the violations.'),
    quiz(2, 'Why does a baseline file name end in chromium-linux?', ['it is a convention only', 'screenshots differ between browsers and operating systems', 'Linux is required', 'it is the project name'], 1,
         'Fonts render differently.', 'Each browser and operating system draws text slightly differently, so each has its own baseline.'),
    quiz(2, 'A date on the page changes every run and breaks the screenshot. What do you use?', ['a bigger threshold', 'mask: [locator]', '--update-snapshots every run', 'delete the test'], 1,
         'Cover it.', 'mask paints a box over the given elements before comparing.'),
    quiz(2, 'Which method makes Date.now() return a set time while timers keep running?', ['install', 'setFixedTime', 'runFor', 'pauseAt'], 1,
         'Fixed.', 'setFixedTime fixes the date. Timers keep running normally.'),
    quiz(2, 'Which check works in Python and Java without extra packages?', ['toHaveScreenshot', 'an aria snapshot', 'an axe scan', 'a visual diff'], 1,
         'It is in the core assertions.', 'to_match_aria_snapshot and matchesAriaSnapshot are part of Playwright for every language.'),
    quiz(2, 'What does runFor("05:00") do after clock.install?', ['waits 5 real minutes', 'runs 5 minutes of timers at once', 'sets the time to 5:00', 'pauses for 5 seconds'], 1,
         'Fake time.', 'It moves the fake clock forward 5 minutes and fires every timer that falls due.'),
    quiz(3, 'What share of accessibility problems can an automatic scan find?', ['all of them', 'only part of them', 'none', 'only colour problems'], 1,
         'Some need a human.', 'A scan cannot judge whether alt text is useful or the tab order makes sense, so manual checks are still needed.'),
    quiz(3, 'How is fastForward different from runFor?', ['it is slower', 'it fires due timers at most once, like waking from sleep', 'it only works in Java', 'there is no difference'], 1,
         'Think of a closed laptop.', 'fastForward jumps ahead and fires due timers once. runFor fires every timer on the way.'),
    quiz(3, 'Which axe package is a community project, not from Deque?', ['@axe-core/playwright', 'com.deque.html.axe-core:playwright', 'axe-playwright-python', 'axe-core'], 2,
         'The Python one.', 'axe-playwright-python is a community package with its own copy of axe-core.'),
]

CALC = [
    calc(1, 'A screenshot is 1280 by 720 pixels. How many pixels is that?', 921600, '1280 × 720', ['1280 × 720 = 921600']),
    calc(2, 'maxDiffPixelRatio is 0.01 on that screenshot. How many pixels may differ?', 9216, '921600 × 0.01', ['921600 × 0.01 = 9216']),
    calc(1, 'The idle timer counts down from 5 minutes. How many seconds is that?', 300, '5 × 60', ['5 × 60 = 300 s']),
    calc(2, 'runFor("05:00") fires a 1 second interval how many times?', 300, '300 s / 1 s', ['5 minutes = 300 s', '300 / 1 = 300 times']),
    calc(2, '12 pages, each with 3 projects (browsers). How many baseline pictures?', 36, '12 × 3', ['one baseline per page and project', '12 × 3 = 36']),
    calc(3, 'An axe scan finds 3 rules broken by 1, 2 and 4 elements. How many elements need a fix?', 7, '1 + 2 + 4', ['1 + 2 + 4 = 7']),
    calc(3, 'A sale starts on 25 December. A test sets the clock to 24 December at 12:00. How many hours until midnight?', 12, '24 - 12', ['from 12:00 to 24:00 is 12 hours']),
    calc(3, '20 pages are scanned with axe in CI, 2 seconds each, on 4 workers. About how many seconds does the scan take?', 10, '20 × 2 / 4', ['20 × 2 = 40 s of scanning', '40 / 4 workers = 10 s']),
]

LABS = [
    {'id': 'cartname', 'title': 'Find the cart link by its accessible name', 'name': 'the cart link has a name',
     'task': 'The cart link in the header shows only an icon and a number, but it has the accessible name <b>Cart</b>. Find it with <code>getByRole</code> and check its accessible name is <b>Cart</b>.',
     'goal': 'The cart link is found by its role and name.', 'start': '/products',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('the cart link has a name', async ({ page }) => {
  await page.goto('/products');
  // find the link named Cart and check its accessible name
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('the cart link has a name', async ({ page }) => {
  await page.goto('/products');
  const cart = page.getByRole('link', { name: 'Cart' });
  await expect(cart).toBeVisible();
  await expect(cart).toHaveAccessibleName('Cart');
});'''},
     'hint': "Use <code>page.getByRole('link', { name: 'Cart' })</code>, then <code>toHaveAccessibleName('Cart')</code>.",
     'why': 'A link with only an icon is silent for a screen reader unless it has a name. Here aria-label gives it one, and the test makes sure it stays.',
     'check': [["/toHaveAccessibleName|to_have_accessible_name|hasAccessibleName/i.test(ctx.code)", 'The test checks the accessible name'], ["/Cart/.test(ctx.code)", 'It uses the name Cart']]},
    {'id': 'namedlist', 'title': 'Check the named products list', 'name': 'the products list is named',
     'task': 'On <code>/products</code> the list of products has the accessible name <b>Products</b>. Find the list by its role and name, and check that it holds <b>5</b> list items.',
     'goal': 'The named list holds five products.', 'start': '/products',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('the products list is named', async ({ page }) => {
  await page.goto('/products');
  // find the list named Products and count its items
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('the products list is named', async ({ page }) => {
  await page.goto('/products');
  const list = page.getByRole('list', { name: 'Products' });
  await expect(list.getByRole('listitem')).toHaveCount(5);
});'''},
     'hint': "Chain locators: <code>page.getByRole('list', { name: 'Products' }).getByRole('listitem')</code>.",
     'why': 'A named list lets a screen reader user jump straight to it and hear how many items it has. The test checks both the name and the content.',
     'check': [["/list/i.test(ctx.code) && /Products/.test(ctx.code)", 'The list is found by its name'], ["/5/.test(ctx.code)", 'The test counts 5 items']]},
]

T = {
    'slug': 'pw-visual', 'title': 'Visual, accessibility and time checks', 'short': 'Visual and a11y', 'emoji': '🖼️', 'module': MODULE, 'minutes': 22,
    'lead': 'Catch the bugs that click tests miss. Compare screenshots with a baseline, check the structure with aria snapshots, scan for accessibility problems with axe, and test dates and timers with a fake clock.',
    'desc': 'toHaveScreenshot, baselines, --update-snapshots, maxDiffPixels and mask, aria snapshots with toMatchAriaSnapshot and ariaSnapshot, accessibility scans with axe in every language, WCAG rules, page.clock with setFixedTime, install, runFor and fastForward.',
    'summary': 'A screenshot comparison that catches a style bug with a real diff picture, aria snapshots of the menu and a product card, an axe scan that finds a missing alt text and low contrast, and a sale date and an idle sign out tested with a fake clock.',
    'keywords': ['visual testing', 'toHaveScreenshot', 'baseline', 'update-snapshots', 'aria snapshot', 'toMatchAriaSnapshot', 'accessibility', 'axe', 'WCAG', 'clock', 'setFixedTime', 'runFor', 'fake timers'],
    'plain': 'Some bugs are about how a page looks, who can use it, or what it does on a certain day. Playwright has a check for each: a picture comparison, an accessibility tree check, an accessibility scan and a fake clock.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
