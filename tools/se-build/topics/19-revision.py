# Chapter 7.1: revision. One place to revise the whole Selenium path, organised by the kind of question rather than by
# chapter: predict the output, find the bug, design and sizing questions, and a cheat sheet in three languages.
# Every question is an original practice question written for this course. Every output quoted here was printed by a
# real run in an earlier chapter (Selenium 4.51.0, Chrome 153), and every number was checked with Python.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import src, flow

K = Kit()

K.lesson('map', 'How Selenium skills are tested', f'''
<p>This chapter is for the week before an interview, a certification style test or a code review of your own framework. It teaches nothing new. It shows the four shapes Selenium questions take, with worked answers, and points back to the chapter where each idea is taught. The questions are original practice questions written for this course.</p>
{table(['Question shape', 'What it looks like', 'What earns the marks', 'Lesson'], [
    ['Predict the output', 'A short program and the question: what does it print, or which error comes back', 'Knowing what the driver really does, not what the code seems to say', '2'],
    ['Find the bug', 'A test that is slow, flaky or fails, and the question: why, and how do you fix it', 'Naming the cause first, then a fix that removes it', '3'],
    ['Design and sizing', 'Plan a framework, size a Grid, triage a flaky suite', 'Clear layers, numbers from a formula, a reason for each choice', '4'],
    ['Write it in another language', 'The same step in Java, Python or JavaScript', 'The right method name and the right unit for time', '5']])}
<h3>The twenty ideas asked about most</h3>
<ol>
<li>Selenium is a family: WebDriver, IDE and Grid (chapter 1.1).</li>
<li>Every command is an HTTP request to a driver, which answers with JSON (chapter 1.2).</li>
<li>Selenium Manager finds or downloads the right driver (chapter 1.3).</li>
<li>Options and capabilities, page load strategies and the three timeouts (chapter 2.1).</li>
<li>get, back, forward, refresh and screenshots (chapter 2.2).</li>
<li>The eight locator strategies, CSS against XPath, relative locators (chapter 3.1).</li>
<li>find_element against find_elements, searching inside an element, shadow roots (chapter 3.2).</li>
<li>click, send keys, clear, select lists and what the driver checks before a click (chapter 3.3).</li>
<li>Why sleeps fail, implicit against explicit waits, and why the two must not be mixed (chapter 4.1).</li>
<li>Window handles, frames and alerts (chapter 4.2).</li>
<li>The Actions API: ticks, pointer, keys and wheel (chapter 4.3).</li>
<li>execute_script return types, async scripts and cookies (chapter 4.4).</li>
<li>JUnit, pytest and Mocha set up and tear down, a screenshot on failure (chapter 5.1).</li>
<li>Page objects and components (chapter 5.2).</li>
<li>A fresh browser per test, set up state through an API, small tests (chapter 5.3).</li>
<li>Stale elements, no such element and reading the logs (chapter 5.4).</li>
<li>Grid roles: Router, Session Queue, Distributor, Session Map, Node and Event Bus (chapter 6.1).</li>
<li>RemoteWebDriver and parallel runs, the sizing formula (chapter 6.1).</li>
<li>WebDriver BiDi events against classic request and response (chapter 6.2).</li>
<li>CDP for Chromium extras and GraphQL to look inside a Grid (chapter 6.2).</li>
</ol>
{note('Use the Revise lessons in order the first time, then use the Quiz and Worked problems tabs as a timed mock test. Each answer says which chapter to reread if you got it wrong.', 'tip')}
''', kw=['revision', 'exam', 'interview', 'practice', 'question types', 'selenium topics'])

K.lesson('trace', 'Predict the output', f'''
<p>These questions show a few lines of code and ask what happens. Every answer below is what a real run printed in an earlier chapter, so you can trust it more than intuition.</p>
{steps('Question 1. The pointer is moved to (8, 12) in the viewport, then moved by an offset of (13, 15). What does the page report?', [
    'move to location sets an absolute point, so the pointer is at (8, 12).',
    'move by offset adds to where the pointer already is.',
    '8 + 13 = 21 and 12 + 15 = 27, so the page printed 21, 27 (chapter 4.3).'])}
{src('py', '''
ActionChains(driver).key_down(Keys.SHIFT).send_keys("abc").key_up(Keys.SHIFT).send_keys("def").perform()
print(field.get_attribute("value"))
''', 'Question 2')}
{steps('Question 2. What is printed?', [
    'Shift is held while a, b and c are typed, so they arrive as capitals.',
    'Shift is released before d, e and f.',
    'The real run printed ABCdef (chapter 4.3).'])}
{src('py', '''
driver = webdriver.Chrome()
driver.add_cookie({"name": "k", "value": "v"})
''', 'Question 3')}
{steps('Question 3. What happens?', [
    'A new session sits on a blank page with no domain.',
    'A cookie belongs to a domain, so there is nothing to attach it to.',
    'The driver answers with the invalid cookie domain error. Navigate to the site first, then add the cookie (chapter 4.4).'])}
{steps('Question 4. execute_script("return 7") is called in each language. What type comes back?', [
    'The browser sends back a JSON number.',
    'Each binding maps it to its own type: Java gives a Long, Python an int and JavaScript a number.',
    'A decimal such as 7.5 comes back as a Double in Java and a float in Python (chapter 4.4).'])}
{src('py', '''
el = driver.find_element(By.ID, "my-text-id")
driver.refresh()
el.send_keys("hi")
''', 'Question 5')}
{steps('Question 5. What happens on the last line?', [
    'refresh builds a brand new document.',
    'The reference in el points to an element of the old document.',
    'The run raised StaleElementReferenceException. Find the element again after the refresh (chapter 5.4).'])}
{steps('Question 6. A test switches into an iframe, then looks for a heading that is in the main page. What happens?', [
    'After the switch, every find searches only inside the frame.',
    'The heading is not in the frame, so the search finds nothing.',
    'The real run raised NoSuchElementException. Switch back with default content first (chapters 4.2 and 5.4).'])}
{steps('Question 7. A test asks for a cookie that does not exist. What comes back?', [
    'Java returned null.',
    'Python returned None.',
    'JavaScript threw NoSuchCookieError. The same question has three answers, so know your binding (chapter 4.4).'])}
''', kw=['predict the output', 'trace', 'actions', 'shift', 'invalid cookie domain', 'stale element', 'no such element', 'return types'])

K.lesson('bugs', 'Find the bug', f'''
<p>Each test below runs, but it is slow, flaky or wrong. Say the cause first, then the fix. The cause is what earns the marks.</p>
<h3>Bug 1. A sleep before the click</h3>
{src('py', '''
driver.find_element(By.ID, "search").click()
time.sleep(5)
driver.find_element(By.CSS_SELECTOR, ".result").click()
''')}
{steps('Cause and fix', [
    'Cause: the sleep always waits 5 seconds. When results come in 1 second it wastes 4. When they need 6 seconds the test still fails.',
    'Fix: wait for the condition you need, for example WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".result"))).',
    'The explicit wait returns as soon as the condition holds, checking every 0.5 seconds in Python and Java (chapter 4.1).'])}
<h3>Bug 2. Implicit and explicit waits together</h3>
{src('java', '''
driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
new WebDriverWait(driver, Duration.ofSeconds(15)).until(ExpectedConditions.visibilityOfElementLocated(By.id("late")));
''')}
{steps('Cause and fix', [
    'Cause: every check inside the explicit wait is a find that itself blocks for up to 10 seconds.',
    'With the numbers from the documentation the wait gave up after about 20.5 seconds, not 15.',
    'Fix: keep the implicit wait at 0 and use explicit waits only. The documentation says do not mix them (chapter 4.1).'])}
<h3>Bug 3. A test that never closes its browser</h3>
{src('py', '''
driver = webdriver.Chrome()
driver.get(url)
assert driver.title == "Web form"
driver.quit()
''')}
{steps('Cause and fix', [
    'Cause: when the assert fails, the line with quit never runs, so Chrome and the driver stay open.',
    'On a long run these leftovers fill the memory of the machine.',
    'Fix: quit in a finally block, or in the tear down of the test framework (chapters 1.3 and 5.1).'])}
<h3>Bug 4. An absolute XPath</h3>
{src('py', '''
driver.find_element(By.XPATH, "/html/body/main/div[2]/form/div[1]/input")
''')}
{steps('Cause and fix', [
    'Cause: the locator depends on six levels of page structure. Any change to any level breaks it.',
    'Fix: use the id or name if there is one, otherwise a short CSS selector tied to a stable attribute.',
    'Keep the locator in a page object so a change is fixed in one place (chapters 3.1 and 5.2).'])}
<h3>Bug 5. Logging in through the form in every test</h3>
{steps('Cause and fix', [
    'Cause: each test spends seconds typing a user name and password that are not what the test checks.',
    'Fix: get a session through an API or set the session cookie, then open the page under test.',
    'Keep one test that logs in through the form, because that form is a feature too (chapter 5.3).'])}
{note('A good bug answer has three parts: what the code really does, why that breaks, and a fix that removes the cause. A retry that hides the failure is not a fix.', 'warn')}
''', kw=['find the bug', 'sleep', 'mix waits', 'quit', 'finally', 'absolute xpath', 'flaky', 'login through api'])

K.lesson('design', 'Design and sizing questions', f'''
<p>Senior interviews and code reviews ask you to plan, not to recite. Answer with layers, numbers and reasons.</p>
<h3>Question 1. Design a test framework for a shop</h3>
{flow(('Tests', 'Read like a story: open the product, add to cart, check the total.'),
      ('Page objects and components', 'One class per page and per repeated part, holding the locators and the actions.'),
      ('Driver factory', 'Builds a local or remote driver from configuration, with the options for each browser.'),
      ('Support', 'API helpers for set up, test data, a screenshot on failure, logs.'))}
<p>Say why each layer exists. Tests change when the behaviour changes. Page objects change when the page changes. The driver factory changes when the place you run changes, for example from a laptop to a Grid. Each change then touches one layer only.</p>
<h3>Question 2. Size a Grid</h3>
{fx('Suite time on a Grid', 'total time = ' + frac('number of tests × average test time', 'number of nodes'), 'From the Grid documentation. Each node here runs one test at a time.', key=True)}
{steps('900 tests of 30 s must finish in 10 minutes. How many one slot nodes are needed?', [
    'Rearrange the formula: nodes = tests × average time ÷ allowed time.',
    'The allowed time is 10 × 60 = 600 s.',
    eq('nodes = 900 × 30 ÷ 600 = 45'),
    'The documentation suggests about one CPU and 1 GB of RAM per browser, so plan about 45 CPUs and 45 GB across the nodes (chapter 6.1).'])}
<h3>Question 3. Triage a flaky suite</h3>
{steps('A suite fails a few different tests on each run. What do you do?', [
    'Group the failures by error. no such element and stale element usually mean timing or a page that changed under the test.',
    'Read the screenshot and the logs of one failure from each group before changing code.',
    'Replace sleeps with explicit waits for the exact condition, and find elements again after the page changes.',
    'Make each test start from a fresh browser and its own data, so tests cannot affect each other.',
    'Track the failure rate after the fix. A retry may keep a release moving, but it does not count as the fix (chapters 5.3 and 5.4).'])}
{ladder(
    '<p>Selenium tests are small programs. Revise by predicting what they do, finding what is wrong, and planning how many machines they need.</p>',
    '<p>Know the layers of a framework, the waits and the errors well enough to explain a failure from its message alone.</p>',
    '<p>Size a Grid from the formula and the resources per browser, and read the queue size to scale it.</p>',
    '<p>Compare WebDriver Classic, CDP and BiDi as protocols, and explain why events need a two way connection.</p>')}
''', kw=['framework design', 'layers', 'driver factory', 'grid sizing', 'formula', 'flaky tests', 'triage'])

K.lesson('sheet', 'Cheat sheet in three languages', f'''
<p>The same common steps in each binding. Time is a Duration in Java, seconds in Python and milliseconds in JavaScript.</p>
{table(['Step', 'Java', 'Python', 'JavaScript'], [
    ['Start Chrome', '<code>new ChromeDriver()</code>', '<code>webdriver.Chrome()</code>', '<code>await new Builder().forBrowser(Browser.CHROME).build()</code>'],
    ['Open a page', '<code>driver.get(url)</code>', '<code>driver.get(url)</code>', '<code>await driver.get(url)</code>'],
    ['Find one element', '<code>driver.findElement(By.id("q"))</code>', '<code>driver.find_element(By.ID, "q")</code>', '<code>await driver.findElement(By.id("q"))</code>'],
    ['Type', '<code>el.sendKeys("text")</code>', '<code>el.send_keys("text")</code>', '<code>await el.sendKeys("text")</code>'],
    ['Wait for an element', '<code>new WebDriverWait(driver, Duration.ofSeconds(5)).until(ExpectedConditions.visibilityOfElementLocated(By.id("q")))</code>', '<code>WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "q")))</code>', '<code>await driver.wait(until.elementLocated(By.id("q")), 5000)</code>'],
    ['Into a frame', '<code>driver.switchTo().frame(el)</code>', '<code>driver.switch_to.frame(el)</code>', '<code>await driver.switchTo().frame(el)</code>'],
    ['Back to the page', '<code>driver.switchTo().defaultContent()</code>', '<code>driver.switch_to.default_content()</code>', '<code>await driver.switchTo().defaultContent()</code>'],
    ['Run a script', '<code>((JavascriptExecutor) driver).executeScript("return 1")</code>', '<code>driver.execute_script("return 1")</code>', '<code>await driver.executeScript("return 1")</code>'],
    ['Add a cookie', '<code>driver.manage().addCookie(new Cookie("k", "v"))</code>', '<code>driver.add_cookie({{"name": "k", "value": "v"}})</code>', '<code>await driver.manage().addCookie({{name: "k", value: "v"}})</code>'],
    ['Use a Grid', '<code>new RemoteWebDriver(new URL("http://localhost:4444"), new ChromeOptions())</code>', '<code>webdriver.Remote(command_executor="http://localhost:4444", options=webdriver.ChromeOptions())</code>', '<code>await new Builder().usingServer("http://localhost:4444").forBrowser(Browser.CHROME).build()</code>'],
    ['End the session', '<code>driver.quit()</code>', '<code>driver.quit()</code>', '<code>await driver.quit()</code>']])}
{fxs(fx('Explicit wait poll', '500 ms', 'The default check interval in Java and Python.', key=True),
     fx('Page load timeout', '300,000 ms', 'Five minutes by default.'),
     fx('Script timeout', '30,000 ms', 'Thirty seconds by default.'),
     fx('Implicit wait', '0', 'The default. Keep it there when you use explicit waits.', key=True))}
''', kw=['cheat sheet', 'java', 'python', 'javascript', 'commands', 'defaults', 'timeouts'])

# ---------------------------------------------------------------- mock quiz
K.quiz('e', 'Which part of Selenium runs tests on many machines at once?', ['Selenium IDE', 'Selenium Grid', 'Selenium Manager', 'ChromeDriver'], 1,
       'Think of scale.', 'Grid routes sessions to many nodes. Chapter 6.1.')
K.quiz('e', 'How does a binding send a command to the driver?', ['Over a shared file', 'As an HTTP request with a JSON body', 'By keyboard events', 'Through the browser address bar'], 1,
       'The W3C protocol.', 'Every WebDriver Classic command is an HTTP request. Chapter 1.2.')
K.quiz('e', 'What does find_elements return when nothing matches?', ['An error', 'None', 'An empty list', 'The first element'], 2,
       'Plural.', 'Only find_element raises no such element. Chapter 3.2.')
K.quiz('e', 'Which call ends the session and closes every window?', ['close', 'quit', 'refresh', 'back'], 1,
       'The whole session.', 'close closes one window. quit ends the session. Chapters 1.3 and 4.2.')
K.quiz('m', 'What is the default implicit wait?', ['0', '500 ms', '10 s', '30 s'], 0,
       'Off by default.', 'Find Element checks once unless you set it. Chapter 2.1.')
K.quiz('m', 'A test adds a cookie right after starting the browser. Which error comes back?', ['no such element', 'invalid cookie domain', 'stale element reference', 'timeout'], 1,
       'There is no site yet.', 'Navigate to the domain first. Chapter 4.4.')
K.quiz('m', 'Why should implicit and explicit waits not be mixed?', ['It is not allowed by the API', 'The wait times become unpredictable', 'Explicit waits stop working', 'It disables screenshots'], 1,
       'Each check blocks.', 'Each check of the explicit wait can block for the implicit time. Chapter 4.1.')
K.quiz('m', 'An element was found, then the page was refreshed. Using the old reference raises', ['NoSuchElementException', 'StaleElementReferenceException', 'TimeoutException', 'Nothing'], 1,
       'The document is new.', 'The reference belongs to the old document. Chapter 5.4.')
K.quiz('m', 'Which layer should hold the locators in a well built framework?', ['The tests', 'The page objects', 'The driver factory', 'The CI pipeline'], 1,
       'One home for each locator.', 'Tests stay readable and a change is fixed once. Chapter 5.2.')
K.quiz('h', 'In a Grid, which component keeps the link from a session id to its node?', ['Distributor', 'Session Map', 'Session Queue', 'Event Bus'], 1,
       'A map.', 'The Router asks the Session Map where to send each command. Chapter 6.1.')
K.quiz('h', 'A command for a running session reaches the Router. Where does it go next?', ['The New Session Queue', 'The Distributor', 'Straight to the node, found through the Session Map', 'Back to the client'], 2,
       'Only new sessions queue.', 'Commands skip the queue and the Distributor. Chapter 6.1.')
K.quiz('h', 'What type does Java return for execute script with "return 7"?', ['Integer', 'Long', 'Double', 'String'], 1,
       'Java maps JSON numbers widely.', 'The real run printed Long. Chapter 4.4.')
K.quiz('h', 'Which protocol lets the browser push console messages to a test as they happen?', ['WebDriver Classic', 'WebDriver BiDi', 'GraphQL', 'SMTP'], 1,
       'Two way.', 'BiDi adds a WebSocket for events. Chapter 6.2.')
K.quiz('x', '15 tests of 45 s run on 5 one slot nodes. How long does the suite take by the Grid formula?', ['45 s', '135 s', '225 s', '675 s'], 1,
       'tests × time ÷ nodes.', '15 × 45 ÷ 5 = 135 s. Chapter 6.1.')
K.quiz('x', 'Why does the documentation call CDP a poor base for long lived tests?', ['It is slow', 'It has no stable API and depends on the browser version', 'It needs a Grid', 'It only works in Firefox'], 1,
       'Compatibility.', 'Selenium supports only the three newest Chrome versions for its CDP classes. Chapter 6.2.')
K.quiz('x', 'A journey has 5 steps that each pass 98 % of the time. Roughly how often does the whole journey pass?', ['98 %', '95 %', '90 %', '80 %'], 2,
       'Multiply.', '0.98<sup>5</sup> ≈ 0.904. Long tests fail more. Chapter 5.3.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'An explicit wait checks every 0.5 s starting at 0 s. The element appears at 2.1 s. At which check, in seconds, does the wait return?', '2.5', 'The first check at or after 2.1 s.',
       ['Checks run at 0, 0.5, 1.0, 1.5, 2.0, 2.5 seconds.', 'At 2.0 s the element is not there yet.', eq('the check at 2.5 s finds it')], check=2.5, tol=0.001, unit='s')
K.calc('e', 'The pointer is at (8, 12). A move by offset of (13, 15) follows. What is the new x?', '21', 'Offsets add.',
       ['Start x is 8.', 'The offset in x is 13.', eq('8 + 13 = 21')], check=21, tol=0.01)
K.calc('m', 'Implicit wait 4 s, explicit wait 6 s, poll 0.5 s, and the element never comes. When does the explicit wait give up, in seconds?', '8.5', 'Each check blocks for the implicit time.',
       ['The check at 0 s blocks until 4 s. 4 s is not past 6 s, so it sleeps 0.5 s.', 'The next check starts at 4.5 s and blocks until 8.5 s.', eq('8.5 s is past 6 s, so it gives up at 8.5 s')], check=8.5, tol=0.001, unit='s')
K.calc('m', '300 tests of 60 s run on 20 one slot nodes. How many minutes does the suite take?', '15', 'Use the Grid formula, then convert.',
       ['300 × 60 = 18,000 s of testing.', '18,000 ÷ 20 = 900 s.', eq('900 ÷ 60 = 15 minutes')], check=15, tol=0.01, unit='min')
K.calc('m', 'A journey has 4 steps that each pass 99 % of the time. What is the chance in percent that it passes, to two decimals?', '96.06', 'Multiply the chances.',
       ['0.99 × 0.99 = 0.9801.', '0.9801 × 0.99 × 0.99 = 0.96059601.', eq('≈ 96.06 %')], check=96.0596, tol=0.006, unit='%')
K.calc('h', '250 tests each log in through a form in 3.5 s. Logging in through an API takes 0.5 s. How many minutes does a run save?', '12.5', 'Saving per test, then total.',
       ['Each test saves 3.5 − 0.5 = 3 s.', '250 × 3 = 750 s.', eq('750 ÷ 60 = 12.5 minutes')], check=12.5, tol=0.01, unit='min')
K.calc('h', 'A screenshot comes back as a base64 string of 8,000 characters. About how many bytes is the PNG?', '6000', 'Base64 turns 3 bytes into 4 characters.',
       ['Each 4 characters carry 3 bytes.', '8,000 ÷ 4 = 2,000 groups.', eq('2,000 × 3 = 6,000 bytes')], check=6000, tol=0.5, unit='bytes')
K.calc('x', '900 tests of 30 s must finish in 10 minutes. How many one slot nodes are needed?', '45', 'Rearrange the formula.',
       ['Allowed time is 600 s.', 'Total test time is 900 × 30 = 27,000 s.', eq('27,000 ÷ 600 = 45 nodes')], check=45, tol=0.01)
K.calc('x', 'An implicit wait of 3 s is set. A test checks that 5 different banners are absent using find_elements. How many seconds does that add?', '15', 'Absence takes the full wait.',
       ['find_elements keeps looking for the whole implicit wait when nothing matches.', 'Each check costs 3 s.', eq('5 × 3 = 15 s')], check=15, tol=0.01, unit='s')

K.must('Predict, then run', 'The driver does what the protocol says, not what the code seems to say. Offsets add, Shift changes case, a refresh makes references stale.')
K.must('Cause before fix', 'Name why a test is slow or flaky before changing it. Sleeps, mixed waits and missing quit calls are the usual causes.')
K.must('Layers', 'Tests, page objects and components, a driver factory and support code. Each change should touch one layer.')
K.must('Size with the formula', 'Suite time = tests × average time ÷ nodes, with about one CPU and 1 GB of RAM per browser.')
K.must('Know your binding', 'Time is a Duration in Java, seconds in Python and milliseconds in JavaScript, and a missing cookie gives null, None or an error.')

T = K.topic(
    slug='revision', topic='revision', kind='revision',
    step=(7, 'Revise and practise', 'se-revision', 'Revise the whole path with output tracing, bug hunts, design and sizing questions, a cheat sheet in three languages and a mock quiz.', 'All levels'),
    title='Revision: predict, debug and design', short='Revision', badge='7.1', minutes=60, added='2026-10-29',
    lead='Practise the question shapes you will meet in interviews and reviews: predict what a test prints, find why a test fails, design a framework and size a Grid, all with worked answers.',
    desc='The twenty most asked Selenium ideas with chapter links, predict the output questions from real runs, five bug hunts with causes and fixes, framework design, Grid sizing and flaky test triage, a cheat sheet in Java, Python and JavaScript, a mock quiz and worked problems.',
    summary='Predict the output, find the bug, design and sizing questions, a cheat sheet in three languages and a mock quiz.',
    keywords=['revision', 'exam', 'interview', 'mock quiz', 'cheat sheet', 'predict output', 'find the bug', 'framework design', 'grid sizing'],
    recap='')
