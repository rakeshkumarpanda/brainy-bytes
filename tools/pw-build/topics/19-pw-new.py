import importlib.util
import os

from pkit import part, say, quiz, calc, panel, four, one, js, ts, py, jv, shown, table, tip

# the framework chapter reads the four real projects, the agents example sets them up in the TypeScript one
_spec = importlib.util.spec_from_file_location('fw16', os.path.join(os.path.dirname(os.path.abspath(__file__)), '16-pw-framework.py'))
fw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fw)

MODULE = fw.MODULE
run_files = fw.run_files

COLLECT_TS = '''import { test, expect } from '@playwright/test';

test('reads console messages and page errors after the fact', async ({ page }) => {
  await page.goto('/widgets');
  await page.getByRole('button', { name: 'Write to the console' }).click();
  await Promise.all([
    page.waitForEvent('pageerror'),
    page.getByRole('button', { name: 'Break the page' }).click(),
  ]);

  // New in 1.56: the page keeps its recent console messages, errors and requests, no listener needed
  for (const m of await page.consoleMessages()) console.log(`console.${m.type()}: ${m.text()}`);
  for (const e of await page.pageErrors()) console.log(`page error: ${e.message}`);
  console.log(`requests so far: ${(await page.requests()).length}`);
  expect(await page.pageErrors()).toHaveLength(1);
});'''

COLLECT_PY = '''from playwright.sync_api import Page


def test_reads_console_messages_and_page_errors_after_the_fact(page: Page):
    page.goto("/widgets")
    page.get_by_role("button", name="Write to the console").click()
    with page.expect_event("pageerror"):
        page.get_by_role("button", name="Break the page").click()

    # New in 1.56: the page keeps its recent console messages, errors and requests, no listener needed
    for m in page.console_messages():
        print(f"console.{m.type}: {m.text}")
    for e in page.page_errors():
        print(f"page error: {e.message}")
    print(f"requests so far: {len(page.requests())}")
    assert len(page.page_errors()) == 1'''

COLLECT_JAVA = '''package com.brainy;

import com.microsoft.playwright.ConsoleMessage;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.junit.UsePlaywright;
import com.microsoft.playwright.options.AriaRole;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

@UsePlaywright(ShopOptions.class)
public class CollectTest {
  @Test
  void readsConsoleMessagesAndPageErrorsAfterTheFact(Page page) {
    page.navigate("/widgets");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Write to the console")).click();
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Break the page")).click();
    page.waitForCondition(() -> !page.pageErrors().isEmpty());

    // New in 1.56: the page keeps its recent console messages, errors and requests, no listener needed
    for (ConsoleMessage m : page.consoleMessages()) System.out.println("console." + m.type() + ": " + m.text());
    for (String e : page.pageErrors()) System.out.println("page error: " + e);
    System.out.println("requests so far: " + page.requests().size());
    assertEquals(1, page.pageErrors().size());
  }
}'''

AGENTS_CMD = ('npx playwright init-agents --loop=claude && echo && find .claude specs tests/seed.spec.ts .mcp.json -type f | sort'
              ' && echo && cat tests/seed.spec.ts && echo && cat .mcp.json')

MCP_JSON = '''{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}'''

PLAN_MD = '''# Product search

## 1. Search finds one product
Steps:
1. Open /products
2. Type "mug" into the search box
Expected: only the Coffee mug card is shown, priced ₹199

## 2. Search finds nothing
Steps:
1. Open /products
2. Type "piano" into the search box
Expected: "No products match your search" is shown'''

CODES = {
    'collect': four('New in 1.56: read console messages, errors and requests at any time',
                    java=jv({'CollectTest.java': COLLECT_JAVA}),
                    py=py({'test_collect.py': COLLECT_PY}, cmd='pytest -s -q'),
                    js=js({'collect.spec.js': COLLECT_TS}),
                    ts=ts({'collect.spec.ts': COLLECT_TS}),
                    result='The page kept the console messages and the error without any listener set up before. Earlier versions only offered page.on(\'console\') and page.on(\'pageerror\'), which miss anything that happened before the listener was added. The same three methods exist in every language: consoleMessages, pageErrors and requests. In Java a page error comes back as its message text.'),
    'agents': one('Set up the Playwright Test Agents in the framework',
                  ts(run_files('ts'), cmd=AGENTS_CMD, show=['playwright.config.ts'], typecheck=False),
                  result='This ran for real in the TypeScript framework. init-agents found the chromium project, wrote three agent definitions for Claude Code, a seed test, a specs folder for plans and an MCP configuration. The agents talk to Playwright through the test MCP server, started with npx playwright run-test-mcp-server. --loop also accepts vscode, copilot, codex and opencode. Run it again after every Playwright update, as the docs advise, so the agents get the new tools.'),
    'plan': one('A plan in specs/, the kind the planner writes',
                shown({'specs/product-search.md': PLAN_MD}, 'ts', note='A Markdown file, shown here'),
                result='A plan is plain Markdown that a person can review before any test exists. The generator turns each scenario into a test, and the labs below ask you to do the same by hand for the first scenario.'),
    'mcp': one('Playwright MCP for any assistant and any language', shown({'.mcp.json': MCP_JSON}, 'ts', note='A configuration file, shown here'),
               result='This is the configuration from the Playwright MCP README. Claude Code can also add it with <code>claude mcp add playwright npx @playwright/mcp@latest</code>. Since 1.62 the same server also ships inside Playwright as <code>npx playwright mcp</code>. The server works on the accessibility tree of the page, not on pixels, so the assistant sees roles and names, the same things good locators use.'),
}

DG = {
    'agents': {'t': 'Planner, generator and healer', 'w': 900, 'h': 230,
               'n': [['app', 20, 85, 110, 56, 'your app', {'c': 5, 'sub': 'running', 'i': 'The agents explore the real app in a browser.'}],
                     ['plan', 170, 20, 150, 56, 'planner', {'c': 3, 'sub': 'specs/*.md', 'i': 'Explores the app and writes a Markdown test plan.'}],
                     ['gen', 370, 20, 150, 56, 'generator', {'c': 1, 'sub': 'tests/*.spec.ts', 'i': 'Turns the plan into test files and checks each locator live.'}],
                     ['heal', 570, 20, 150, 56, 'healer', {'c': 0, 'sub': 'fix or skip', 'i': 'Runs failing tests, inspects the page and patches the test, or skips it when the app looks broken.'}],
                     ['you', 470, 150, 170, 56, 'you review', {'c': 2, 'sub': 'pull request', 'i': 'A person reads the plan and the tests before they are merged.'}],
                     ['ci', 740, 150, 140, 56, 'CI', {'c': 4, 'sub': 'every push', 'i': 'The reviewed tests run in the pipeline like any other test.'}]],
               'e': [['app', 'plan'], ['plan', 'gen'], ['gen', 'heal'], ['plan', 'you'], ['heal', 'you'], ['you', 'ci']],
               'st': [[['app'], 'The app runs, and the seed test opens it.'],
                      [['plan', 'app>plan'], 'The planner explores it and writes a plan in specs/.'],
                      [['gen', 'plan>gen'], 'The generator turns the plan into tests.'],
                      [['heal', 'gen>heal'], 'The healer runs them and repairs what fails.'],
                      [['you', 'plan>you', 'heal>you'], 'A person reviews the plan and the tests.'],
                      [['ci', 'you>ci'], 'Reviewed tests run in CI like every other test.']]},
}

PARTS = [
    part('versions', '🆕', 'How Playwright changes, and how to keep up', f'''
<p>Playwright ships a new version roughly every month or two. Each version comes with its own browser builds, so updating Playwright also updates the browsers you test with. This course uses <b>1.63</b>.</p>
{table(['Version', 'Highlights for testers'], [
    ['1.56', 'Playwright Test Agents: planner, generator and healer. page.consoleMessages(), page.pageErrors() and page.requests()'],
    ['1.57', 'a Speedboard tab in the HTML report that shows the slowest tests, and Chrome for Testing builds instead of Chromium'],
    ['1.58', 'a timeline chart for merged reports, and old selectors such as _react removed'],
    ['1.59', 'page.screencast for videos with chapters and overlays, page.ariaSnapshot(), and npx playwright trace on the command line'],
    ['1.60', 'test.abort(), locator.drop() and HAR recording through tracing'],
    ['1.61', 'passkeys through browserContext.credentials, page.localStorage, and -G as a short form of --grep-invert'],
    ['1.62', 'retryStrategy, WebP screenshots, and npx playwright mcp bundled with Playwright'],
    ['1.63', 'test locks, locator.visible(), --add-reporter and a perfetto reporter'],
    ['1.64', 'page.webmcp, --shuffle, locator.within() and page.getByRef()'],
])}
{table(['Language', 'Update the package', 'Then'], [
    ['TypeScript and JavaScript', 'npm install -D @playwright/test@latest', 'npx playwright install --with-deps'],
    ['Python', 'pip install -U playwright pytest-playwright', 'playwright install --with-deps'],
    ['Java', 'change the version of com.microsoft.playwright in pom.xml', 'Playwright downloads the matching browsers on first run'],
])}
{tip('Read the release notes before updating, and update on a branch so CI shows what changed. Each release lists its breaking changes, such as page.accessibility removed in 1.57 and Node.js 16 support removed in 1.54.', 'pro')}
''', easy=True, kw=['release notes', 'new features', 'update', 'upgrade', 'version', '1.56', '1.63', '1.64']),

    part('collect', '🧾', 'A new feature in all four languages', f'''
<p>Many new features arrive in every language at once. Here is one from 1.56 that makes debugging easier: the page remembers its recent console messages, errors and network requests, so a test can read them after the fact.</p>
[[collect]]
{tip('Use pageErrors() at the end of a test to fail it when the page threw an error that the user never saw. It is a cheap check that catches broken scripts early.', 'pro')}
''', kw=['consoleMessages', 'pageErrors', 'requests', 'console', 'page errors', '1.56']),

    part('agents', '🤖', 'Playwright Test Agents', f'''
<p>Since 1.56, Playwright ships three <b>agent definitions</b>: instructions plus Playwright tools that an AI coding assistant follows to write and maintain tests. You bring the assistant, such as Claude Code, VS Code with Copilot, Codex or OpenCode. Playwright provides the agents.</p>
<div class="viz" data-viz="flow" data-k="agents"></div>
{table(['Agent', 'Reads', 'Writes'], [
    ['planner', 'your running app, starting from the seed test', 'a Markdown plan in specs/'],
    ['generator', 'a plan from specs/', 'test files in tests/, with each locator and check tried live'],
    ['healer', 'a failing test', 'a fixed test, or a skipped one when it believes the app itself is broken'],
])}
[[agents]]
[[plan]]
{tip('The agents write Playwright Test code in TypeScript or JavaScript. For Python and Java there are no ready made agents, but the Playwright MCP server below lets an assistant drive the browser while it writes pytest or Java tests.', 'warn')}
''', kw=['AI', 'agents', 'test agents', 'planner', 'generator', 'healer', 'init-agents', 'seed', 'specs', 'Claude Code', 'Copilot']),

    part('mcp', '🔌', 'Playwright MCP: a browser for AI assistants', f'''
<p><b>MCP</b>, the Model Context Protocol, is a standard way to give an AI assistant tools. The Playwright MCP server gives it a real browser: open a page, read its accessibility snapshot, click, type and take screenshots. The assistant can then write a test in whatever language your project uses.</p>
[[mcp]]
{table(['Tool', 'Use it for'], [
    ['Playwright MCP', 'any assistant that speaks MCP, exploring an app and writing tests in any language'],
    ['Playwright Test Agents', 'planning, generating and healing Playwright Test files in TypeScript or JavaScript'],
    ['Copy prompt in the HTML report, trace viewer and UI mode', 'pasting a failed test with its error and page snapshot into any assistant, since 1.51'],
    ['the Playwright CLI with skills', 'coding agents. The MCP README notes that the CLI uses fewer tokens'],
])}
''', kw=['MCP', 'Model Context Protocol', 'Playwright MCP', 'assistant', 'Copy prompt', 'accessibility snapshot']),

    part('review', '🧐', 'Using AI-written tests safely', f'''
<p>An assistant can write a test in seconds, but the team still owns it. Review AI-written tests with the same rules as tests written by people.</p>
{table(['Check', 'Why'], [
    ['the test uses the framework: page objects, fixtures, test data', 'otherwise every generated test adds locators that someone must maintain'],
    ['every check is meaningful', 'a test that only checks that a heading is visible passes even when the feature is broken'],
    ['no fixed waits and no force: true', 'they hide timing problems that real users meet'],
    ['the healer did not hide a bug', 'it may skip a test when the app looks broken. A skipped test needs a person to decide'],
    ['the test fails when the feature breaks', 'break the feature on purpose once, or change an expected value, and watch it go red'],
    ['secrets stay out of prompts and plans', 'plans and prompts are files and messages that other people and tools can read'],
])}
{tip('Give the agents a seed test that signs in through your own fixtures. Generated tests then start from the same state as the rest of your suite.', 'pro')}
''', kw=['review', 'AI tests', 'quality', 'healer', 'skip', 'safety', 'secrets']),
]

INFO = {'title': 'What is new, in four ideas', 'panels': [
    panel([['e', '🆕'], ['t', 'monthly', {'b': 1}]], 'Releases', 'New browsers each time.', 'Read the notes first.'),
    panel([['e', '🧾'], ['t', 'pageErrors', {'b': 1}]], 'New APIs', 'In every language.', 'Like consoleMessages.'),
    panel([['e', '🤖'], ['t', 'agents', {'b': 1}]], 'Test Agents', 'Plan, generate, heal.', 'For Playwright Test.'),
    panel([['e', '🔌'], ['t', 'MCP', {'b': 1}]], 'Playwright MCP', 'A browser for assistants.', 'Any language.')],
    'remember': 'Update on a branch and read the release notes. Let AI write tests, but review them like any other code, and make sure each one can fail.'}

REAL = [
    ['🧭', 'A plan before the code', 'A team asks the planner to explore a new checkout page. The Markdown plan lists twelve scenarios, the product owner removes two and adds one, and only then does the generator write the tests.'],
    ['🩹', 'The healer that found a real bug', 'After a release the healer cannot repair a cart test and skips it, saying the Add to cart button no longer works. A person checks, and the button really is broken. The skip pointed straight at the bug.'],
    ['⬆️', 'An update that caught a crash', 'A team updates Playwright on a branch. A test with a pageErrors() check fails in the new Chromium, and the trace shows a script error in the app that had gone unseen for weeks.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter shows how Playwright keeps changing and how to keep up: recent releases, a new feature in all four languages, the Playwright Test Agents, Playwright MCP, and how to review tests that AI writes.',
        'यह अध्याय दिखाता है कि Playwright कैसे बदलता रहता है और साथ कैसे चलें: हाल के releases, चारों भाषाओं में एक नया feature, Playwright Test Agents, Playwright MCP, और AI के लिखे tests की समीक्षा कैसे करें।',
        'ಈ ಅಧ್ಯಾಯ Playwright ಹೇಗೆ ಬದಲಾಗುತ್ತದೆ ಮತ್ತು ಹೇಗೆ ಹಿಂದೆ ಬೀಳದಿರುವುದು ಎಂದು ತೋರಿಸುತ್ತದೆ: ಇತ್ತೀಚಿನ releases, ನಾಲ್ಕೂ ಭಾಷೆಗಳಲ್ಲಿ ಹೊಸ feature, Playwright Test Agents, Playwright MCP, ಮತ್ತು AI ಬರೆದ tests ಪರಿಶೀಲನೆ.',
        'ଏହି ଅଧ୍ୟାୟ ଦେଖାଏ Playwright କିପରି ବଦଳୁଛି ଏବଂ ସାଙ୍ଗରେ କିପରି ଚାଲିବେ: ନିକଟ releases, ଚାରି ଭାଷାରେ ଏକ ନୂଆ feature, Playwright Test Agents, Playwright MCP, ଏବଂ AI ଲେଖିଥିବା tests ର ସମୀକ୍ଷା।',
        'يعرض هذا الفصل كيف يتغير Playwright باستمرار وكيف تواكبه: الإصدارات الأخيرة، وميزة جديدة في اللغات الأربع، ووكلاء Playwright Test، وPlaywright MCP، وكيف تراجع الاختبارات التي يكتبها الذكاء الاصطناعي.',
        'Dieses Kapitel zeigt, wie sich Playwright laufend ändert und wie du Schritt hältst: neue Versionen, eine neue Funktion in allen vier Sprachen, die Playwright Test Agents, Playwright MCP und wie du von KI geschriebene Tests prüfst.'),
    say('versions', 'Keeping up', 'Playwright ships a new version every month or two, each with its own browsers. Read the release notes, update on a branch, and let CI show what changed.',
        'Playwright हर एक या दो महीने में नया version देता है, हर एक के अपने browsers के साथ। Release notes पढ़ें, branch पर update करें, और CI को दिखाने दें कि क्या बदला।',
        'Playwright ಪ್ರತಿ ಒಂದು ಅಥವಾ ಎರಡು ತಿಂಗಳಿಗೆ ಹೊಸ version ಕೊಡುತ್ತದೆ, ಪ್ರತಿಯೊಂದಕ್ಕೂ ತನ್ನ browsers. Release notes ಓದಿ, branch ನಲ್ಲಿ update ಮಾಡಿ, ಏನು ಬದಲಾಯಿತು ಎಂದು CI ತೋರಿಸಲಿ.',
        'Playwright ପ୍ରତି ଏକ ବା ଦୁଇ ମାସରେ ନୂଆ version ଦିଏ, ପ୍ରତ୍ୟେକର ନିଜ browsers ସହ। Release notes ପଢନ୍ତୁ, branch ରେ update କରନ୍ତୁ, ଏବଂ CI କୁ ଦେଖାଇବାକୁ ଦିଅନ୍ତୁ କଣ ବଦଳିଲା।',
        'يصدر Playwright نسخة جديدة كل شهر أو شهرين، لكل منها متصفحاتها. اقرأ ملاحظات الإصدار، وحدّث على فرع، ودع CI يُظهر ما تغيّر.',
        'Playwright bringt alle ein bis zwei Monate eine neue Version mit eigenen Browsern. Lies die Release Notes, aktualisiere auf einem Branch und lass CI zeigen, was sich geändert hat.'),
    say('collect', 'A new feature', 'Since 1.56 a page keeps its recent console messages, errors and requests. A test can read them at any time with consoleMessages, pageErrors and requests, in every language.',
        '1.56 से page अपने हाल के console messages, errors और requests याद रखता है। Test उन्हें कभी भी consoleMessages, pageErrors और requests से पढ़ सकता है, हर भाषा में।',
        '1.56 ರಿಂದ page ತನ್ನ ಇತ್ತೀಚಿನ console messages, errors ಮತ್ತು requests ಇಟ್ಟುಕೊಳ್ಳುತ್ತದೆ. Test ಅವನ್ನು ಯಾವಾಗ ಬೇಕಾದರೂ consoleMessages, pageErrors, requests ಮೂಲಕ ಓದಬಹುದು, ಎಲ್ಲಾ ಭಾಷೆಗಳಲ್ಲಿ.',
        '1.56 ରୁ page ନିଜର ନିକଟ console messages, errors ଓ requests ମନେ ରଖେ। Test ସେଗୁଡିକୁ ଯେକୌଣସି ସମୟରେ consoleMessages, pageErrors ଓ requests ରେ ପଢିପାରେ, ପ୍ରତି ଭାଷାରେ।',
        'منذ 1.56 تحتفظ الصفحة برسائل وحدة التحكم والأخطاء والطلبات الأخيرة. ويستطيع الاختبار قراءتها في أي وقت عبر consoleMessages وpageErrors وrequests، في كل لغة.',
        'Seit 1.56 merkt sich eine Seite ihre letzten Konsolenmeldungen, Fehler und Anfragen. Ein Test kann sie jederzeit mit consoleMessages, pageErrors und requests lesen, in jeder Sprache.'),
    say('agents', 'Test Agents', 'Three agent definitions help an AI assistant: the planner writes a plan, the generator turns it into tests, and the healer repairs failing tests or skips them when the app looks broken.',
        'तीन agent definitions AI assistant की मदद करती हैं: planner योजना लिखता है, generator उसे tests में बदलता है, और healer fail होते tests ठीक करता है या app टूटा लगे तो उन्हें skip करता है।',
        'ಮೂರು agent definitions AI assistant ಗೆ ಸಹಾಯ ಮಾಡುತ್ತವೆ: planner ಯೋಜನೆ ಬರೆಯುತ್ತದೆ, generator ಅದನ್ನು tests ಆಗಿ ಮಾಡುತ್ತದೆ, healer fail ಆಗುವ tests ಸರಿಪಡಿಸುತ್ತದೆ ಅಥವಾ app ಮುರಿದಂತೆ ಕಂಡರೆ skip ಮಾಡುತ್ತದೆ.',
        'ତିନୋଟି agent definitions AI assistant କୁ ସାହାଯ୍ୟ କରନ୍ତି: planner ଯୋଜନା ଲେଖେ, generator ତାକୁ tests କରେ, ଏବଂ healer fail ହେଉଥିବା tests ଠିକ୍ କରେ ବା app ଭଙ୍ଗା ଲାଗିଲେ skip କରେ।',
        'تساعد ثلاثة تعريفات وكلاء مساعد الذكاء الاصطناعي: المخطِّط يكتب خطة، والمولِّد يحوّلها إلى اختبارات، والمعالِج يصلح الاختبارات الفاشلة أو يتخطاها حين يبدو التطبيق معطوبًا.',
        'Drei Agentendefinitionen helfen einem KI-Assistenten: Der Planner schreibt einen Plan, der Generator macht daraus Tests, und der Healer repariert fehlschlagende Tests oder überspringt sie, wenn die App kaputt wirkt.'),
    say('mcp', 'Playwright MCP', 'The Playwright MCP server gives an AI assistant a real browser that it reads through the accessibility tree. The assistant can then write tests in any language.',
        'Playwright MCP server AI assistant को एक असली browser देता है जिसे वह accessibility tree से पढ़ता है। फिर assistant किसी भी भाषा में tests लिख सकता है।',
        'Playwright MCP server AI assistant ಗೆ ನಿಜವಾದ browser ಕೊಡುತ್ತದೆ, ಅದನ್ನು accessibility tree ಮೂಲಕ ಓದುತ್ತದೆ. ನಂತರ assistant ಯಾವುದೇ ಭಾಷೆಯಲ್ಲಿ tests ಬರೆಯಬಹುದು.',
        'Playwright MCP server AI assistant କୁ ଏକ ପ୍ରକୃତ browser ଦିଏ ଯାହାକୁ ସେ accessibility tree ରେ ପଢେ। ତାପରେ assistant ଯେକୌଣସି ଭାଷାରେ tests ଲେଖିପାରେ।',
        'يمنح خادم Playwright MCP مساعد الذكاء الاصطناعي متصفحًا حقيقيًا يقرؤه عبر شجرة إمكانية الوصول. ثم يستطيع المساعد كتابة الاختبارات بأي لغة.',
        'Der Playwright-MCP-Server gibt einem KI-Assistenten einen echten Browser, den er über den Barrierefreiheitsbaum liest. Danach kann der Assistent Tests in jeder Sprache schreiben.'),
    say('review', 'Reviewing AI tests', 'Review tests that AI writes like any other code: they must use the framework, check something meaningful, avoid fixed waits, and fail when the feature breaks.',
        'AI के लिखे tests की समीक्षा किसी भी दूसरे code की तरह करें: वे framework इस्तेमाल करें, कुछ सार्थक जाँचें, fixed waits से बचें, और feature टूटने पर fail हों।',
        'AI ಬರೆದ tests ಅನ್ನು ಬೇರೆ code ನಂತೆ ಪರಿಶೀಲಿಸಿ: framework ಬಳಸಬೇಕು, ಅರ್ಥಪೂರ್ಣವಾದದ್ದನ್ನು check ಮಾಡಬೇಕು, fixed waits ಬೇಡ, feature ಮುರಿದಾಗ fail ಆಗಬೇಕು.',
        'AI ଲେଖିଥିବା tests କୁ ଅନ୍ୟ code ପରି ସମୀକ୍ଷା କରନ୍ତୁ: ସେଗୁଡିକ framework ବ୍ୟବହାର କରିବେ, କିଛି ଅର୍ଥପୂର୍ଣ୍ଣ ଯାଞ୍ଚ କରିବେ, fixed waits ଏଡାଇବେ, ଏବଂ feature ଭାଙ୍ଗିଲେ fail ହେବେ।',
        'راجع الاختبارات التي يكتبها الذكاء الاصطناعي كأي كود آخر: يجب أن تستخدم الإطار، وتفحص شيئًا ذا معنى، وتتجنب الانتظار الثابت، وتفشل حين تتعطل الميزة.',
        'Prüfe von KI geschriebene Tests wie jeden anderen Code: Sie müssen das Framework nutzen, etwas Sinnvolles prüfen, feste Wartezeiten vermeiden und fehlschlagen, wenn die Funktion kaputt ist.'),
    say('practice', 'Playground labs', 'In the labs you write the seed test the agents start from, and turn the first scenario of a plan into a test yourself.',
        'Labs में आप वह seed test लिखते हैं जिससे agents शुरू करते हैं, और योजना के पहले scenario को खुद test में बदलते हैं।',
        'Labs ನಲ್ಲಿ agents ಆರಂಭಿಸುವ seed test ಬರೆಯುತ್ತೀರಿ, ಮತ್ತು ಯೋಜನೆಯ ಮೊದಲ scenario ಅನ್ನು ನೀವೇ test ಆಗಿ ಮಾಡುತ್ತೀರಿ.',
        'Labs ରେ ଆପଣ agents ଆରମ୍ଭ କରୁଥିବା seed test ଲେଖନ୍ତି, ଏବଂ ଯୋଜନାର ପ୍ରଥମ scenario କୁ ନିଜେ test କରନ୍ତି।',
        'في المختبرات تكتب اختبار البذرة الذي يبدأ منه الوكلاء، وتحوّل بنفسك السيناريو الأول من الخطة إلى اختبار.',
        'In den Labs schreibst du den Seed-Test, mit dem die Agenten starten, und machst selbst aus dem ersten Szenario eines Plans einen Test.'),
]

QUIZ = [
    quiz(1, 'Which version introduced the Playwright Test Agents?', ['1.40', '1.56', '1.62', '1.64'], 1,
         'Mid 1.5x.', 'The planner, generator and healer arrived in Playwright 1.56.'),
    quiz(1, 'What does the planner agent write?', ['test files', 'a Markdown test plan in specs/', 'a CI file', 'a bug report'], 1,
         'A plan first.', 'The planner explores the app and saves a Markdown plan in specs/.'),
    quiz(1, 'Which command adds the agent definitions to a project?', ['npx playwright agents', 'npx playwright init-agents --loop=claude', 'npm init agents', 'npx playwright codegen --agents'], 1,
         'init.', 'init-agents with a --loop for your assistant writes the definitions, a seed test and the MCP config.'),
    quiz(1, 'What does page.pageErrors() return?', ['console warnings', 'recent errors thrown in the page', 'failed network requests', 'test failures'], 1,
         'Errors in the page.', 'It returns the most recent uncaught errors from the page, up to 200.'),
    quiz(2, 'What does the healer do when it believes the app itself is broken?', ['deletes the test', 'marks the test as skipped', 'changes the app', 'retries forever'], 1,
         'It does not hide it silently.', 'It skips the test, so a person must look and decide.'),
    quiz(2, 'What does the Playwright MCP server use to understand a page?', ['screenshots and pixels', 'the accessibility tree', 'the page source only', 'OCR'], 1,
         'Roles and names.', 'The README says it uses the accessibility tree, not pixel input.'),
    quiz(2, 'Why update Playwright on a branch?', ['it is faster', 'so CI shows what the new version and browsers change before merging', 'branches get newer browsers', 'it is required'], 1,
         'See before merging.', 'New browsers and breaking changes show up as CI results on the branch.'),
    quiz(2, 'Which file did init-agents create for the agents\' tools?', ['package.json', '.mcp.json', 'tsconfig.json', 'pytest.ini'], 1,
         'MCP.', '.mcp.json starts the Playwright test MCP server that the agents use.'),
    quiz(3, 'What should you do with a test an assistant wrote that only checks a heading is visible?', ['merge it', 'make it check what the feature really does', 'add a sleep', 'delete the feature'], 1,
         'Meaningful checks.', 'A check that passes when the feature is broken gives false confidence.'),
    quiz(3, 'After updating Playwright, what should you do with the agent definitions?', ['nothing', 'regenerate them with init-agents', 'delete them', 'move them to specs/'], 1,
         'The docs say so.', 'The docs advise regenerating them so the agents get new tools and instructions.'),
    quiz(3, 'Which release added a Copy prompt button to the HTML report?', ['1.51', '1.40', '1.60', '1.64'], 0,
         'Early 1.5x.', 'Copy prompt arrived in 1.51 in the HTML report, the trace viewer and UI mode.'),
    quiz(3, 'Why might a team pick Playwright MCP over the Test Agents for a Java project?', ['MCP is newer', 'the agents write Playwright Test code, MCP lets an assistant write tests in any language', 'Java cannot run agents', 'MCP is faster'], 1,
         'Languages.', 'The agents generate TypeScript or JavaScript tests. MCP only drives the browser.'),
]

CALC = [
    calc(1, 'Playwright went from 1.56 to 1.64. How many minor versions is that?', 8, '64 - 56', ['64 - 56 = 8']),
    calc(1, 'init-agents wrote 3 agent definitions, 1 seed test, 1 specs README and 1 MCP config. How many files?', 6, '3 + 1 + 1 + 1', ['3 + 1 + 1 + 1 = 6']),
    calc(2, 'page.consoleMessages() keeps up to 200 messages. A page logged 230. How many of the oldest are dropped?', 30, '230 - 200', ['230 - 200 = 30']),
    calc(2, 'A plan has 12 scenarios and the product owner removes 2 and adds 1. How many does the generator turn into tests?', 11, '12 - 2 + 1', ['12 - 2 = 10', '10 + 1 = 11']),
    calc(2, 'The healer fixes 7 of 9 failing tests and skips the rest. How many need a person to look?', 2, '9 - 7', ['9 - 7 = 2']),
    calc(3, 'A team updates every second release. With 8 releases a year, how many updates is that?', 4, '8 / 2', ['8 / 2 = 4']),
    calc(3, 'Reviewing a generated test takes 6 minutes and writing it by hand takes 20. How many minutes do 10 tests save?', 140, '10 × (20 - 6)', ['20 - 6 = 14 minutes per test', '10 × 14 = 140']),
    calc(3, 'A suite has 150 tests and 3 fail after an update. What percentage still pass?', 98, '(150 - 3) / 150 × 100', ['150 - 3 = 147', '147 / 150 = 0.98', '0.98 × 100 = 98']),
]

LABS = [
    {'id': 'seed', 'title': 'Write the seed test', 'name': 'seed',
     'task': 'The agents start every exploration from a seed test. Write one that opens <code>/products</code> and checks that the heading <b>Products</b> is visible, so the planner knows the shop is up.',
     'goal': 'The products page is open and its heading is checked.', 'start': '',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('seed', async ({ page }) => {
  // open the products page and check its heading
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('seed', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByRole('heading', { name: 'Products' })).toBeVisible();
});'''},
     'hint': "Use <code>page.getByRole('heading', { name: 'Products' })</code> with <code>toBeVisible()</code>.",
     'why': 'A seed test that reaches a known page in a known state lets the planner and the generator start from the same place as your suite.',
     'check': [["ctx.url.includes('/products')", 'The products page is open'], ["/heading/i.test(ctx.code)", 'The test checks the heading']]},
    {'id': 'planstep', 'title': 'Turn a plan scenario into a test', 'name': 'search finds one product',
     'task': 'Scenario 1 of the plan: open <code>/products</code>, type <code>mug</code> into the search box, and expect only the <b>Coffee mug</b> card, priced <b>₹199</b>. Check the card with the test id <code>product-2</code>.',
     'goal': 'The search shows the mug with its price.', 'start': '/products',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('search finds one product', async ({ page }) => {
  await page.goto('/products');
  // follow the steps of scenario 1 and check the expected result
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('search finds one product', async ({ page }) => {
  await page.goto('/products');
  await page.getByPlaceholder('Search products').fill('mug');
  await expect(page.getByRole('list', { name: 'Products' }).getByRole('listitem')).toHaveCount(1);
  await expect(page.getByTestId('product-2')).toContainText('₹199');
});'''},
     'hint': "Fill <code>page.getByPlaceholder('Search products')</code>, then check the count of list items and the text of <code>product-2</code>.",
     'why': 'This is what the generator does with each scenario: one step becomes one action, and each expected result becomes a check.',
     'check': [["/mug/.test(ctx.code)", 'The test searches for mug'], ["/product-2/.test(ctx.code) && /199/.test(ctx.code)", 'The test checks the mug and its price'],
               ["/Coffee mug/.test(ctx.text)", 'The mug is on the page']]},
]

T = {
    'slug': 'pw-new', 'title': "What's new, and AI test agents", 'short': "What's new", 'emoji': '🤖', 'module': MODULE, 'minutes': 25,
    'lead': 'Keep up with Playwright: recent releases, a new feature in all four languages, the Playwright Test Agents set up for real in the framework, Playwright MCP for any assistant, and how to review tests that AI writes.',
    'desc': 'Playwright release highlights from 1.56 to 1.64, updating Playwright in each language, page.consoleMessages, page.pageErrors and page.requests, the planner, generator and healer agents with npx playwright init-agents, the seed test and specs folder, Playwright MCP and its configuration, Copy prompt, and a checklist for reviewing AI-written tests.',
    'summary': 'A 1.56 feature ran in all four languages, the agent definitions were created for real in the TypeScript framework, and a checklist shows how to keep AI-written tests honest.',
    'keywords': ["what's new", 'release notes', 'AI', 'agents', 'test agents', 'planner', 'generator', 'healer', 'MCP', 'Playwright MCP', 'init-agents', 'consoleMessages', 'pageErrors', 'upgrade'],
    'plain': 'Playwright keeps adding features, such as pages that remember their console messages and errors, and AI agents that plan, write and repair tests. They help, but a person still reviews every test.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
