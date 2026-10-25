# Chapter 3: decisions, loops, errors and the retry and polling loops every test framework is built on.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🌱', 'Foundations', 'js-foundations', 'From your first program to functions and closures. Developers and testers both start here.')

CODES = {
    'if-else': run('''
function shippingFee(total, isMember) {
  if (total <= 0) {
    return "invalid";
  } else if (isMember || total >= 999) {
    return 0;
  } else if (total >= 500) {
    return 40;
  } else {
    return 80;
  }
}

console.log(shippingFee(1200, false));
console.log(shippingFee(600, false));
console.log(shippingFee(300, true));
console.log(shippingFee(300, false));
console.log(shippingFee(-5, false));
''', 'if, else if and else'),
    'guard': run('''
function applyCoupon(cart, code) {
  if (!cart) return "no cart";
  if (cart.items.length === 0) return "cart is empty";
  if (code !== "SAVE10") return "unknown coupon";

  // the happy path, no nesting needed
  return `saved ${cart.total * 0.1}`;
}

console.log(applyCoupon(null, "SAVE10"));
console.log(applyCoupon({ items: [], total: 0 }, "SAVE10"));
console.log(applyCoupon({ items: [1], total: 500 }, "OOPS"));
console.log(applyCoupon({ items: [1], total: 500 }, "SAVE10"));
''', 'Guard clauses keep code flat'),
    'switch': run('''
function statusIcon(status) {
  switch (status) {
    case "passed":
      return "✅";
    case "failed":
    case "broken":           // two cases share one result
      return "❌";
    case "skipped":
      return "⏭️";
    default:
      return "❓";
  }
}
["passed", "broken", "skipped", "flaky"].forEach(s => console.log(s, statusIcon(s)));

// forgetting break makes execution "fall through" into the next case
const level = 2;
switch (level) {
  case 1: console.log("one");
  case 2: console.log("two");
  case 3: console.log("three");
  default: console.log("default");
}
''', 'switch, shared cases and fall through'),
    'lookup': run('''
const ICONS = { passed: "✅", failed: "❌", broken: "❌", skipped: "⏭️" };
const icon = status => ICONS[status] ?? "❓";
console.log(icon("passed"), icon("broken"), icon("flaky"));
''', 'An object lookup instead of a switch'),
    'loops': run('''
for (let i = 1; i <= 3; i++) {
  console.log("for", i);
}

let tries = 0;
while (tries < 2) {
  tries++;
  console.log("while try", tries);
}

let n = 10;
do {
  console.log("do runs at least once, n =", n);
} while (n < 5);

for (const browser of ["chromium", "firefox", "webkit"]) {
  console.log("for...of", browser);
}

const user = { name: "Asha", role: "admin" };
for (const key in user) {
  console.log("for...in", key, "=", user[key]);
}
''', 'Every kind of loop'),
    'break-continue': run('''
const results = ["pass", "pass", "skip", "fail", "pass"];
for (const r of results) {
  if (r === "skip") continue;      // jump to the next item
  if (r === "fail") {
    console.log("stopping at the first failure");
    break;                         // leave the loop
  }
  console.log("checked", r);
}

outer: for (const row of [[1, 2], [3, 4], [5, 6]]) {
  for (const cell of row) {
    if (cell === 4) break outer;   // a label breaks out of both loops
    console.log(cell);
  }
}
''', 'break, continue and labels'),
    'entries': run('''
const scores = { asha: 82, ravi: 67, mei: 91 };
for (const [name, score] of Object.entries(scores)) {
  console.log(`${name}: ${score >= 70 ? "pass" : "fail"}`);
}

const tests = ["login", "search", "checkout"];
for (const [index, name] of tests.entries()) {
  console.log(index + 1, name);
}
''', 'Looping over objects and indexes'),
    'foreach-await': run('''
const sleep = ms => new Promise(r => setTimeout(r, ms));
const steps = ["open page", "fill form", "submit"];

console.log("forEach does not wait:");
steps.forEach(async step => {
  await sleep(10);
  console.log("  done:", step);
});
console.log("  forEach returned already");
await sleep(50);

console.log("for...of waits for each step:");
for (const step of steps) {
  await sleep(10);
  console.log("  done:", step);
}
console.log("  every step finished");
''', 'forEach does not wait for async steps'),
    'throw': run('''
function withdraw(balance, amount) {
  if (typeof amount !== "number" || Number.isNaN(amount)) {
    throw new TypeError("amount must be a number");
  }
  if (amount > balance) {
    throw new RangeError(`cannot withdraw ${amount}, balance is ${balance}`);
  }
  return balance - amount;
}

for (const amount of [30, "ten", 500]) {
  try {
    console.log("new balance:", withdraw(100, amount));
  } catch (err) {
    console.log(`${err.name}: ${err.message}`);
  } finally {
    console.log("finally always runs");
  }
}
''', 'throw, try, catch and finally'),
    'custom-error': run('''
class ValidationError extends Error {
  constructor(field, message, options) {
    super(message, options);
    this.name = "ValidationError";
    this.field = field;
  }
}

function parseAge(text) {
  const age = Number(text);
  if (!Number.isInteger(age)) {
    throw new ValidationError("age", `"${text}" is not a whole number`);
  }
  return age;
}

function signUp(form) {
  try {
    return { ok: true, age: parseAge(form.age) };
  } catch (err) {
    if (err instanceof ValidationError) {
      // wrap it with more context and keep the original as the cause
      throw new Error(`sign up failed for ${form.email}`, { cause: err });
    }
    throw err;   // anything else is unexpected, pass it on
  }
}

try {
  signUp({ email: "asha@example.com", age: "twenty" });
} catch (err) {
  console.log(err.message);
  console.log("cause:", err.cause.name, "on", err.cause.field, "-", err.cause.message);
}
''', 'A custom error with a cause'),
    'finally-cleanup': run('''
async function runTest(name, body) {
  const browser = { open: true };          // pretend we launched a browser
  console.log(`[${name}] browser launched`);
  try {
    await body();
    console.log(`[${name}] passed`);
  } catch (err) {
    console.log(`[${name}] failed: ${err.message}`);
  } finally {
    browser.open = false;                    // cleanup runs on pass and on fail
    console.log(`[${name}] browser closed`);
  }
}

await runTest("login", async () => {});
await runTest("checkout", async () => { throw new Error("button not found"); });
''', 'finally for cleanup'),
    'wait-for': run('''
const sleep = ms => new Promise(r => setTimeout(r, ms));

// The heart of every "wait until" helper: check, wait a little, check again, give up after a timeout.
async function waitFor(check, { timeout = 1000, interval = 100 } = {}) {
  const start = Date.now();
  let attempt = 0;
  while (true) {
    attempt++;
    const value = await check();
    if (value) return { value, attempt };
    if (Date.now() - start >= timeout) {
      throw new Error(`condition not met after ${attempt} attempts`);
    }
    await sleep(interval);
  }
}

// A fake "order status" that becomes ready on the 4th check
let calls = 0;
const orderStatus = async () => (++calls >= 4 ? "SHIPPED" : null);

const result = await waitFor(orderStatus, { timeout: 2000, interval: 50 });
console.log(result);

try {
  await waitFor(async () => false, { timeout: 200, interval: 50 });
} catch (err) {
  console.log(err.message);
}
''', 'A polling loop with a timeout', replace=[(r'after \d+ attempts', 'after 5 attempts')]),
    'retry': run('''
async function retry(action, { attempts = 3, delay = 50 } = {}) {
  let lastError;
  for (let i = 1; i <= attempts; i++) {
    try {
      return await action(i);
    } catch (err) {
      lastError = err;
      console.log(`attempt ${i} failed: ${err.message}`);
      if (i < attempts) await new Promise(r => setTimeout(r, delay * 2 ** (i - 1)));  // 50, 100, 200 ms
    }
  }
  throw new Error(`gave up after ${attempts} attempts`, { cause: lastError });
}

const flaky = async attempt => {
  if (attempt < 3) throw new Error("503 Service Unavailable");
  return "200 OK";
};
console.log(await retry(flaky));
''', 'Retry with exponential backoff'),
    'scenario': run('''
// Data driven checks: one validation rule, a table of inputs and the result each should give.
function isValidPassword(pw) {
  if (typeof pw !== "string") return false;
  if (pw.length < 8 || pw.length > 64) return false;
  if (!/[A-Z]/.test(pw)) return false;
  if (!/[0-9]/.test(pw)) return false;
  return true;
}

const cases = [
  { input: "Secret12", expected: true, why: "8 chars, upper, digit" },
  { input: "Secret1", expected: false, why: "7 chars, one too short" },
  { input: "secret12", expected: false, why: "no upper case" },
  { input: "SecretOK", expected: false, why: "no digit" },
  { input: "A1" + "x".repeat(62), expected: true, why: "64 chars, the maximum" },
  { input: "A1" + "x".repeat(63), expected: false, why: "65 chars, one too long" },
  { input: null, expected: false, why: "not a string" },
];

let failures = 0;
for (const c of cases) {
  const actual = isValidPassword(c.input);
  const ok = actual === c.expected;
  if (!ok) failures++;
  console.log(`${ok ? "PASS" : "FAIL"}  ${c.why.padEnd(24)} expected ${c.expected}, got ${actual}`);
}
console.log(failures === 0 ? "All cases pass" : `${failures} case(s) failed`);
''', 'A table of test cases'),
}

PARTS = [
    part('if-else', '🔀', 'Making decisions with if and else', '''
<p>An <code>if</code> statement runs a block only when a condition is truthy. <code>else if</code> adds more conditions, checked from the top, and the first one that matches wins.</p>
[[if-else]]
<div class="tip">Order matters. Put the most specific condition first. If <code>total >= 500</code> came before <code>total >= 999</code>, a ₹1200 order would wrongly pay ₹40.</div>
<h3>Guard clauses</h3>
<p>Deep nesting is hard to read. Handle the bad cases first and return early, so the main logic stays at the left edge.</p>
[[guard]]
<div class="qa-box">Every <code>if</code> and <code>else</code> is a path that needs a test. The shipping fee above has five paths, so it needs at least five test cases, plus the boundary values 499, 500, 998 and 999. Branch coverage reports count exactly these paths.</div>
''', qa=True, qa_why='Each branch is a test case, and coverage tools measure how many branches your tests reach.',
        kw=['if', 'else', 'else if', 'condition', 'guard clause', 'early return', 'branch coverage', 'boundary value']),
    part('switch', '🎛️', 'switch and lookup tables', '''
<p><code>switch</code> compares one value against many cases with <code>===</code>. Cases without a <code>break</code> or <code>return</code> fall through into the next one, which is useful for shared results and a classic bug otherwise.</p>
[[switch]]
<p>When each case only picks a value, an object used as a lookup table is shorter and easier to extend.</p>
[[lookup]]
''', kw=['switch', 'case', 'default', 'break', 'fall through', 'lookup table', 'object map']),
    part('loops', '🔁', 'Loops', '''
<p>Loops repeat work. Pick the loop by what you are repeating over.</p>
<div class="viz" data-viz="lanes" data-k="loop"></div>
[[loops]]
<div class="tw"><table class="jt"><tr><th>Loop</th><th>Use it when</th></tr>
<tr><td><code>for (let i = 0; i &lt; n; i++)</code></td><td>you need the counter, or a fixed number of repeats</td></tr>
<tr><td><code>for (const x of list)</code></td><td>you want each value of an array, string, Map or Set. The usual choice.</td></tr>
<tr><td><code>for (const key in obj)</code></td><td>you want the keys of a plain object. Avoid it on arrays.</td></tr>
<tr><td><code>while (condition)</code></td><td>you do not know how many times, such as polling until something is ready</td></tr>
<tr><td><code>do { } while (condition)</code></td><td>the body must run at least once</td></tr>
</table></div>
<h3>break, continue and labels</h3>
[[break-continue]]
[[entries]]
<div class="warn">A <code>while</code> loop whose condition never becomes false runs forever and freezes the page or the test. Every polling loop needs a timeout, as shown later in this chapter.</div>
''', kw=['for loop', 'while', 'do while', 'for...of', 'for...in', 'break', 'continue', 'label', 'Object.entries', 'infinite loop']),
    part('async-loops', '⏱️', 'Loops with async steps', '''
<p>Test code is full of steps that take time: open a page, click, wait for a response. These steps return promises and are written with <code>await</code> ({{ch:js-async}} explains how they work). Loops and <code>await</code> have one trap that breaks many first test suites.</p>
[[foreach-await]]
<ul>
<li><code>array.forEach</code> calls the function for every item and does not wait for any of them. The loop is "finished" while the steps are still running.</li>
<li><code>for...of</code> with <code>await</code> inside runs the steps one after another, in order. Use it for UI steps.</li>
<li>To start many independent requests at once and wait for all of them, use <code>await Promise.all(list.map(async x => ...))</code>.</li>
</ul>
<div class="qa-box">In Playwright and WebdriverIO, <code>items.forEach(async item => await page.click(item))</code> makes clicks race each other and the test may end before they finish. Write <code>for (const item of items) await page.click(item)</code>. Cypress queues its commands, so a plain <code>forEach</code> with <code>cy</code> commands inside works there, which is one of the main differences between the tools.</div>
''', qa=['Playwright', 'WebdriverIO', 'Selenium', 'Cypress'], qa_why='Awaiting inside forEach is one of the most common causes of flaky UI tests.',
        kw=['forEach await', 'async loop', 'for of await', 'Promise.all', 'sequential', 'parallel', 'flaky test']),
    part('errors', '🧯', 'Throwing and catching errors', '''
<p>Code signals a problem by <b>throwing</b> an error. The error travels up through the functions that called it until a <code>try</code> block catches it. If nothing catches it, the program stops.</p>
<div class="viz" data-viz="flow" data-k="trycatch"></div>
[[throw]]
<ul>
<li>Throw <code>Error</code> objects (or subclasses such as <code>TypeError</code>), never plain strings. Only <code>Error</code> objects carry a stack trace.</li>
<li><code>finally</code> runs whether the block passed, threw or returned. It is the place for cleanup.</li>
<li>Catch only what you can handle. Rethrow everything else with <code>throw err</code>.</li>
</ul>
<h3>Custom errors and causes</h3>
<p>A subclass of <code>Error</code> lets callers tell your error apart from others with <code>instanceof</code>. The <code>cause</code> option (ES2022) wraps a low level error in a clearer one without losing it.</p>
[[custom-error]]
<h3>finally for cleanup</h3>
[[finally-cleanup]]
<div class="qa-box">A test runner is a giant <code>try</code>, <code>catch</code> and <code>finally</code>. Each test body runs inside <code>try</code>, a failed assertion is a thrown error, and <code>afterEach</code> hooks run like <code>finally</code>. That is why a failed assertion stops the rest of that test but not the suite.</div>
''', qa=['Jest', 'Playwright', 'Mocha'], qa_why='An assertion failure is a thrown error. Knowing how errors travel explains how runners report and clean up.',
        kw=['throw', 'try', 'catch', 'finally', 'Error', 'TypeError', 'RangeError', 'custom error', 'instanceof', 'error cause', 'rethrow', 'cleanup']),
    part('polling', '⏳', 'Polling and retry loops', '''
<p>Two loops sit at the centre of every test framework. You will rarely write them yourself, but knowing how they work explains timeouts, flaky tests and the options every tool offers.</p>
<h3>Wait until something is true</h3>
[[wait-for]]
<div class="viz" data-viz="wait"></div>
<p>Playwright's auto-waiting, <code>expect.poll</code>, Cypress retry-ability, WebdriverIO's <code>waitUntil</code> and Selenium's <code>driver.wait</code> are all versions of this loop: check, wait a short interval, check again, fail with a clear message after the timeout.</p>
<h3>Retry an action that sometimes fails</h3>
[[retry]]
<div class="rule">Retry infrastructure problems (a 503 from a test server, a slow container). Never retry to hide a real bug. A test that only passes on the third try is reporting something.</div>
''', qa=['Playwright', 'Cypress', 'Selenium', 'WebdriverIO'], qa_why='Auto-waiting and retries are loops like these, and their timeout options are the loop limits.',
        kw=['polling', 'wait for', 'waitUntil', 'timeout', 'interval', 'retry', 'exponential backoff', 'expect.poll', 'auto waiting', 'flaky']),
    part('scenario', '🎬', 'Real world scenario: data driven password checks', '''
<div class="scenario"><b>The situation</b>A sign up form has a password rule: 8 to 64 characters, at least one capital letter and one digit. You need to check the rule on all the important inputs, including the boundaries, and show a readable report.</div>
[[scenario]]
<p>This is <b>data driven testing</b>: the logic of the check is written once and the cases live in a table. Adding a case means adding one row. Every test runner has a built in version: <code>test.each</code> in Jest and Vitest, a loop over <code>test()</code> in Playwright, and data providers in TestNG.</p>
<div class="qa-box">The rows were chosen with boundary value analysis: 7, 8, 64 and 65 characters, plus one row for each rule broken on its own. Each row has a short "why", which becomes the test name and tells the reader what failed.</div>
''', qa=['Jest', 'Vitest', 'Playwright'], kw=['data driven testing', 'test table', 'test.each', 'boundary values', 'password validation', 'test cases']),
]

LANES = {
    'loop': {'t': 'A loop, one turn at a time', 's': 'Watch the counter, the condition and the running total.', 'code': 'let sum = 0;\nfor (let i = 1; i <= 3; i++) {\n  sum += i;\n}\nconsole.log(sum);',
             'lanes': ['Variables', 'Condition', 'Console'], 'tone': [2, 5, 1],
             'steps': [{'l': 1, 'v': [['sum = 0'], [], []], 'm': 'sum starts at 0.'},
                       {'l': 2, 'v': [['sum = 0', 'i = 1'], ['1 <= 3 → true'], []], 'm': 'The loop creates i = 1 and checks the condition. It is true, so the body runs.'},
                       {'l': 3, 'v': [['sum = 1', 'i = 1'], ['1 <= 3 → true'], []], 'm': 'sum += i adds 1.'},
                       {'l': 2, 'v': [['sum = 1', 'i = 2'], ['2 <= 3 → true'], []], 'm': 'i++ makes i 2. The condition is checked again.'},
                       {'l': 3, 'v': [['sum = 3', 'i = 2'], ['2 <= 3 → true'], []], 'm': 'sum becomes 3.'},
                       {'l': 2, 'v': [['sum = 3', 'i = 3'], ['3 <= 3 → true'], []], 'm': 'i is 3. Still true, because the condition uses <=.'},
                       {'l': 3, 'v': [['sum = 6', 'i = 3'], ['3 <= 3 → true'], []], 'm': 'sum becomes 6.'},
                       {'l': 2, 'v': [['sum = 6', 'i = 4'], ['4 <= 3 → false'], []], 'm': 'i is 4 and the condition is false, so the loop ends. i only lived inside the loop.'},
                       {'l': 5, 'v': [['sum = 6'], [], ['6']], 'm': 'The program continues after the loop and prints 6.'}]},
}

DG = {
    'trycatch': {'t': 'Where an error goes', 'w': 900, 'h': 260,
                 'n': [['try', 30, 100, 160, 60, 'try { ... }', {'c': 2}], ['ok', 260, 20, 170, 56, 'no error', {'c': 1, 'sub': 'catch is skipped'}],
                       ['bad', 260, 180, 170, 56, 'throw new Error()', {'c': 6, 'sub': 'rest of try is skipped'}], ['catch', 490, 180, 160, 56, 'catch (err)', {'c': 0}],
                       ['fin', 710, 100, 160, 60, 'finally', {'c': 3, 'sub': 'always runs'}], ['up', 490, 20, 160, 56, 'not caught here?', {'c': 4, 'sub': 'travels to the caller'}]],
                 'e': [['try', 'ok'], ['try', 'bad'], ['bad', 'catch'], ['ok', 'fin', {'via': [[790, 48]]}], ['catch', 'fin'], ['catch', 'up', {'t': 'rethrow', 'd': 1}]],
                 'st': [[['try', 'ok', 'try>ok', 'fin', 'ok>fin'], 'When nothing goes wrong, the try block finishes, catch is skipped and finally runs.'],
                        [['try', 'bad', 'try>bad'], 'A throw stops the try block on that line.'],
                        [['catch', 'bad>catch'], 'Control jumps to catch with the error object.'],
                        [['fin', 'catch>fin'], 'finally runs next, so cleanup always happens.'],
                        [['up', 'catch>up'], 'If catch throws again, or there is no catch, the error travels up to whoever called this code.']]},
}

INFO = {'title': 'Deciding, repeating and recovering', 'panels': [
    panel([['e', '🔀'], ['t', 'if (total >= 999) free', {'b': 1}]], 'Decide', 'if, else and switch pick a path.', 'Each path is a test case. Boundaries such as 998 and 999 deserve their own.'),
    panel([['e', '🔁'], ['c', [1, 2, 3], {'hl': {0: 'ok', 1: 'ok', 2: 'hl'}}]], 'Repeat', 'Loops run a block again and again.', 'for...of for values, a counter for fixed repeats, while for "until it is ready".'),
    panel([['e', '🧯'], ['t', 'try { } catch (e) { }', {'b': 1}]], 'Recover', 'try and catch handle errors.', 'finally always runs, which makes it the home of cleanup.'),
    panel([['e', '⏳'], ['t', 'check, wait, check again', {'b': 1}]], 'Wait', 'A polling loop waits for a condition.', 'This loop is inside every auto-wait. Its timeout is the limit you configure.')],
    'remember': 'Every branch is a test case, and every waiting loop needs a timeout.'}

REAL = [
    ['🚚', 'Delivery charges', 'An if, else if chain decides free, reduced or full shipping. The tests check each band and the values on each edge.'],
    ['📦', 'Order tracking', 'A tracking page polls the server every few seconds until the status says delivered, then stops.'],
    ['🔁', 'Flaky test server', 'A CI job retries a request that fails with 503 three times with growing delays before reporting the server as down.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers decisions, loops and errors, and ends with the polling and retry loops every test framework is built on.',
        'यह अध्याय decisions, loops और errors सिखाता है, और उन polling और retry loops पर खत्म होता है जिन पर हर test framework बना है।',
        'ಈ ಅಧ್ಯಾಯ decisions, loops ಮತ್ತು errors ಕಲಿಸುತ್ತದೆ, ಪ್ರತಿ test framework ಆಧರಿಸಿದ polling ಮತ್ತು retry loops ನೊಂದಿಗೆ ಮುಗಿಯುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ decisions, loops ଓ errors ଶିଖାଏ, ଏବଂ ପ୍ରତ୍ୟେକ test framework ର ମୂଳ polling ଓ retry loops ରେ ଶେଷ ହୁଏ।',
        'يتناول هذا الفصل القرارات والحلقات والأخطاء، وينتهي بحلقات الانتظار وإعادة المحاولة التي تقوم عليها كل أدوات الاختبار.',
        'Dieses Kapitel behandelt Entscheidungen, Schleifen und Fehler und endet mit den Warte- und Wiederholungsschleifen, auf denen jedes Testframework aufbaut.'),
    say('if-else', 'Decisions', 'if and else pick a path, and the first matching condition wins. Guard clauses return early so the main logic stays flat. Each path needs a test.',
        'if और else रास्ता चुनते हैं, और पहली matching condition जीतती है। Guard clauses जल्दी return करते हैं। हर रास्ते को एक test चाहिए।',
        'if ಮತ್ತು else ದಾರಿ ಆಯ್ಕೆ ಮಾಡುತ್ತವೆ, ಮೊದಲ matching condition ಗೆಲ್ಲುತ್ತದೆ. Guard clauses ಬೇಗ return ಮಾಡುತ್ತವೆ. ಪ್ರತಿ ದಾರಿಗೆ ಒಂದು test ಬೇಕು.',
        'if ଓ else ରାସ୍ତା ବାଛନ୍ତି, ପ୍ରଥମ matching condition ଜିତେ। Guard clauses ଶୀଘ୍ର return କରନ୍ତି। ପ୍ରତ୍ୟେକ ରାସ୍ତା ପାଇଁ ଏକ test ଦରକାର।',
        'تختار if وelse المسار، والشرط الأول المطابق هو الذي يُنفذ. تعيد عبارات الحماية مبكرًا. كل مسار يحتاج إلى اختبار.',
        'if und else wählen einen Weg, die erste passende Bedingung gewinnt. Guard Clauses kehren früh zurück. Jeder Weg braucht einen Test.'),
    say('switch', 'switch', 'switch compares one value against many cases. Without break, execution falls through. An object lookup is often shorter.',
        'switch एक value को कई cases से मिलाता है। break के बिना execution आगे गिर जाता है। Object lookup अक्सर छोटा होता है।',
        'switch ಒಂದು value ಅನ್ನು ಹಲವು cases ಜೊತೆ ಹೋಲಿಸುತ್ತದೆ. break ಇಲ್ಲದಿದ್ದರೆ ಮುಂದಿನ case ಗೆ ಹೋಗುತ್ತದೆ. Object lookup ಹೆಚ್ಚಾಗಿ ಚಿಕ್ಕದು.',
        'switch ଗୋଟିଏ value କୁ ଅନେକ cases ସହ ତୁଳନା କରେ। break ବିନା ପରବର୍ତ୍ତୀ case କୁ ଯାଏ। Object lookup ପ୍ରାୟ ଛୋଟ।',
        'تقارن switch قيمة واحدة بحالات كثيرة. بدون break يستمر التنفيذ إلى الحالة التالية. جدول البحث بكائن غالبًا أقصر.',
        'switch vergleicht einen Wert mit vielen Fällen. Ohne break läuft die Ausführung weiter. Eine Objekttabelle ist oft kürzer.'),
    say('loops', 'Loops', 'Use for of for values, a counter loop for fixed repeats, for in for object keys and while when you do not know how many times.',
        'Values के लिए for of, तय repeats के लिए counter loop, object keys के लिए for in और अनजानी गिनती के लिए while इस्तेमाल करें।',
        'Values ಗೆ for of, ನಿಗದಿತ repeats ಗೆ counter loop, object keys ಗೆ for in, ಎಷ್ಟು ಬಾರಿ ಎಂದು ಗೊತ್ತಿಲ್ಲದಾಗ while ಬಳಸಿ.',
        'Values ପାଇଁ for of, ନିର୍ଦ୍ଦିଷ୍ଟ repeats ପାଇଁ counter loop, object keys ପାଇଁ for in ଏବଂ ଅଜଣା ସଂଖ୍ୟା ପାଇଁ while ବ୍ୟବହାର କରନ୍ତୁ।',
        'استخدم for of للقيم، وحلقة العداد للتكرار المحدد، وfor in لمفاتيح الكائن، وwhile عندما لا تعرف عدد المرات.',
        'Nimm for of für Werte, eine Zählschleife für feste Wiederholungen, for in für Objektschlüssel und while, wenn die Anzahl unbekannt ist.'),
    say('async-loops', 'Async loops', 'forEach does not wait for async steps. Use for of with await to run steps in order, and Promise all to run independent ones together.',
        'forEach async steps का इंतज़ार नहीं करता। Steps क्रम से चलाने के लिए await के साथ for of, और अलग steps साथ चलाने के लिए Promise.all इस्तेमाल करें।',
        'forEach async steps ಗಾಗಿ ಕಾಯುವುದಿಲ್ಲ. ಕ್ರಮವಾಗಿ ಓಡಿಸಲು await ಜೊತೆ for of, ಒಟ್ಟಿಗೆ ಓಡಿಸಲು Promise.all ಬಳಸಿ.',
        'forEach async steps ପାଇଁ ଅପେକ୍ଷା କରେ ନାହିଁ। କ୍ରମରେ ଚଲାଇବାକୁ await ସହ for of, ଏକାଠି ଚଲାଇବାକୁ Promise.all ବ୍ୟବହାର କରନ୍ତୁ।',
        'لا تنتظر forEach الخطوات غير المتزامنة. استخدم for of مع await لتنفيذ الخطوات بالترتيب، وPromise.all لتنفيذ المستقلة معًا.',
        'forEach wartet nicht auf asynchrone Schritte. Nutze for of mit await für die Reihenfolge und Promise.all für unabhängige Schritte.'),
    say('errors', 'Errors', 'Throw Error objects, catch only what you can handle, and use finally for cleanup. A failed assertion is just a thrown error.',
        'Error objects throw करें, सिर्फ वही catch करें जो संभाल सकें, और cleanup के लिए finally इस्तेमाल करें। Failed assertion बस एक thrown error है।',
        'Error objects throw ಮಾಡಿ, ನಿಭಾಯಿಸಬಹುದಾದ್ದನ್ನು ಮಾತ್ರ catch ಮಾಡಿ, cleanup ಗೆ finally ಬಳಸಿ. Failed assertion ಒಂದು thrown error ಮಾತ್ರ.',
        'Error objects throw କରନ୍ତୁ, ସମ୍ଭାଳିପାରୁଥିବା କେବଳ catch କରନ୍ତୁ, cleanup ପାଇଁ finally ବ୍ୟବହାର କରନ୍ତୁ। Failed assertion କେବଳ ଏକ thrown error।',
        'ارمِ كائنات Error، والتقط فقط ما تستطيع معالجته، واستخدم finally للتنظيف. التحقق الفاشل مجرد خطأ مرمي.',
        'Wirf Error-Objekte, fange nur, was du behandeln kannst, und räume in finally auf. Eine fehlgeschlagene Assertion ist nur ein geworfener Fehler.'),
    say('polling', 'Polling and retries', 'A polling loop checks, waits and checks again until a timeout. A retry loop repeats a failing action with growing delays. Auto waiting in test tools works the same way.',
        'Polling loop जाँचता है, रुकता है और timeout तक फिर जाँचता है। Retry loop असफल action को बढ़ती देरी के साथ दोहराता है। Test tools का auto waiting ऐसे ही काम करता है।',
        'Polling loop ಪರಿಶೀಲಿಸಿ, ಕಾಯ್ದು, timeout ವರೆಗೆ ಮತ್ತೆ ಪರಿಶೀಲಿಸುತ್ತದೆ. Retry loop ವಿಫಲ action ಅನ್ನು ಹೆಚ್ಚುವ ವಿಳಂಬದೊಂದಿಗೆ ಮರುಮಾಡುತ್ತದೆ.',
        'Polling loop ଯାଞ୍ଚ କରେ, ଅପେକ୍ଷା କରେ ଏବଂ timeout ପର୍ଯ୍ୟନ୍ତ ପୁଣି ଯାଞ୍ଚ କରେ। Retry loop ବିଫଳ action କୁ ବଢ଼ୁଥିବା ବିଳମ୍ବ ସହ ଦୋହରାଏ।',
        'حلقة الانتظار تفحص وتنتظر وتفحص مجددًا حتى انتهاء المهلة. حلقة إعادة المحاولة تكرر الإجراء الفاشل مع تأخير متزايد.',
        'Eine Warteschleife prüft, wartet und prüft erneut bis zum Timeout. Eine Wiederholungsschleife wiederholt eine fehlgeschlagene Aktion mit wachsenden Pausen.'),
    say('scenario', 'Scenario', 'One password rule is checked against a table of cases chosen with boundary values. Adding a case means adding one row.',
        'एक password rule को boundary values से चुने cases की table पर जाँचा जाता है। नया case मतलब एक नई row।',
        'ಒಂದು password rule ಅನ್ನು boundary values ಮೂಲಕ ಆಯ್ದ cases table ವಿರುದ್ಧ ಪರಿಶೀಲಿಸಲಾಗುತ್ತದೆ. ಹೊಸ case ಎಂದರೆ ಒಂದು row.',
        'ଗୋଟିଏ password rule କୁ boundary values ରୁ ବଛା cases table ରେ ଯାଞ୍ଚ କରାଯାଏ। ନୂଆ case ମାନେ ଗୋଟିଏ row।',
        'تُفحص قاعدة كلمة مرور واحدة مقابل جدول حالات مختارة بقيم الحدود. إضافة حالة تعني إضافة صف واحد.',
        'Eine Passwortregel wird gegen eine Tabelle von Fällen mit Grenzwerten geprüft. Ein neuer Fall ist eine neue Zeile.'),
    say('practice', 'Hands-on', 'Write decisions, loops and a real polling helper, then run the tests in your browser.',
        'Decisions, loops और एक असली polling helper लिखें, फिर tests अपने browser में चलाएँ।',
        'Decisions, loops ಮತ್ತು ನಿಜವಾದ polling helper ಬರೆಯಿರಿ, ನಂತರ tests ನಿಮ್ಮ browser ನಲ್ಲಿ ಓಡಿಸಿ.',
        'Decisions, loops ଓ ଏକ ପ୍ରକୃତ polling helper ଲେଖନ୍ତୁ, ତାପରେ tests ଆପଣଙ୍କ browser ରେ ଚଲାନ୍ତୁ।',
        'اكتب قرارات وحلقات ومساعد انتظار حقيقي، ثم شغل الاختبارات في متصفحك.',
        'Schreibe Entscheidungen, Schleifen und eine echte Wartehilfe und führe die Tests im Browser aus.'),
]

QUIZ = [
    quiz('e', 'Which loop is the usual choice to visit every value of an array?', ['for...of', 'for...in', 'do...while', 'switch'], 0, 'It gives values, not keys.', '<code>for...of</code> gives each value. <code>for...in</code> gives keys and is meant for plain objects.'),
    quiz('e', 'When does a finally block run?', ['Always, after try and any catch', 'Only when there was an error', 'Only when there was no error', 'Only if catch rethrows'], 0, 'Think of cleanup.', 'finally runs whether the try block passed, threw or returned.'),
    quiz('e', 'What does continue do inside a loop?', ['Skips to the next turn', 'Leaves the loop', 'Restarts the loop from the start', 'Throws an error'], 0, 'break leaves, continue skips.', '<code>continue</code> ends the current turn and moves to the next item.'),
    quiz('m', 'What does this print?', ['two three', 'two', 'one two three', 'three'], 0, 'There are no break statements.', 'Execution starts at case 2 and falls through into case 3.', code='switch (2) {\n  case 1: console.log("one");\n  case 2: console.log("two");\n  case 3: console.log("three");\n}'),
    quiz('m', 'Why should you throw new Error("x") instead of throw "x"?', ['Only Error objects carry a stack trace and a name', 'Strings cannot be thrown', 'It is faster', 'catch only accepts objects'], 0, 'What helps you find where it happened?', 'A string can be thrown, but it has no stack, so the report cannot say where the problem started.'),
    quiz('m', 'A Playwright test does items.forEach(async i => await page.click(i)). What usually happens?', ['The clicks race each other and the test can end before they finish', 'Each click waits for the previous one', 'It throws a SyntaxError', 'forEach becomes synchronous'], 0, 'Does forEach look at the promises?',
         'forEach ignores the returned promises. Use <code>for...of</code> with <code>await</code> for steps that must happen in order.'),
    quiz('h', 'What is err.cause here?', ['The original ValidationError', 'undefined', 'The string "bad age"', 'A new TypeError'], 0, 'The second argument of Error is an options object.', 'The <code>cause</code> option stores the original error on the new one.', code='try { parseAge("x"); }\ncatch (e) { throw new Error("bad age", { cause: e }); }'),
    quiz('h', 'Which loop body runs at least once even when the condition starts false?', ['do...while', 'while', 'for', 'for...of'], 0, 'The check is at the end.', '<code>do...while</code> checks its condition after the body.'),
    quiz('h', 'A retry waits 100 ms, then doubles the wait each time. How long is the wait before the 4th attempt?', ['400 ms', '800 ms', '300 ms', '100 ms'], 0, '100, 200, then...', 'Waits before attempts 2, 3 and 4 are 100, 200 and 400 ms.'),
    quiz('x', 'Which tool runs a plain forEach over cy commands correctly, and why?', ['Cypress, because commands are queued and run later in order', 'Playwright, because it awaits forEach', 'Selenium, because it is synchronous', 'None of them'], 0, 'One of them does not use await at all.', 'Cypress commands do not run when called. They are added to a queue that Cypress runs in order, so forEach only fills the queue.'),
    quiz('x', 'What does this print?', ['1 2 3', '1 2 3 5 6', '1 2', '1 2 3 5'], 0, 'The label belongs to the outer loop.', '<code>break outer</code> leaves both loops when the cell is 4, so only 1, 2 and 3 are printed.', code='outer: for (const row of [[1,2],[3,4],[5,6]]) {\n  for (const c of row) {\n    if (c === 4) break outer;\n    console.log(c);\n  }\n}'),
    quiz('x', 'What does the function return?', ['"finally"', '"try"', 'undefined', 'It throws'], 0, 'A return in finally wins.', 'A <code>return</code> inside <code>finally</code> replaces the value from <code>try</code>. This is why linters warn about it.', code='function f() {\n  try { return "try"; }\n  finally { return "finally"; }\n}'),
]

CALC = [
    calc('e', 'How many times does the body run?', '5', 'Count i from 0 up to 4.', ['i takes the values 0, 1, 2, 3 and 4.', 'That is 5 turns.'], code='for (let i = 0; i < 5; i++) {\n  console.log(i);\n}'),
    calc('e', 'What is the shipping fee for a total of 600 for a non member, with the rules from Part 1?', '40', 'Check the conditions from the top.', ['600 is not ≤ 0 and not ≥ 999, but it is ≥ 500.', 'So the fee is 40.']),
    calc('m', 'What is sum at the end?', '9', 'Odd numbers only.', ['continue skips 2 and 4.', '<span class="eq">1 + 3 + 5 = 9</span>'], code='let sum = 0;\nfor (let i = 1; i <= 5; i++) {\n  if (i % 2 === 0) continue;\n  sum += i;\n}'),
    calc('m', 'A polling loop has a timeout of 1000 ms and an interval of 200 ms. Each check is instant. At most how many checks run?', '6', 'Checks at 0, 200, 400...', ['Checks happen at 0, 200, 400, 600, 800 and 1000 ms.', 'The check at 1000 ms is the last one, so 6 checks.']),
    calc('h', 'A retry starts at 50 ms and doubles: 50, 100, 200... What is the total waiting time for 5 attempts?', '750', 'There is no wait after the last attempt.', ['4 waits come between 5 attempts.', '<span class="eq">50 + 100 + 200 + 400 = 750 ms</span>'], alt=['750 ms']),
    calc('h', 'The password rule allows 8 to 64 characters. Using boundary value analysis with the values just below, on and just above each edge, how many length values do you test?', '6', 'Three values around each edge.', ['Lower edge: 7, 8, 9.', 'Upper edge: 63, 64, 65.', 'That is 6 values.']),
    calc('x', 'What does this print?', '6', 'The do body runs once before the check.', ['The body runs with n = 5 and makes n 6.', 'Then <code>6 &lt; 5</code> is false, so the loop stops and prints 6.'], code='let n = 5;\ndo {\n  n++;\n} while (n < 5);\nconsole.log(n);'),
    calc('x', 'How many lines does this print?', '4', 'Follow the case where it starts.', ['"start" prints first.', 'The switch jumps to case "b" and prints b, falls through into case "c" and prints c, then break leaves the switch.', '"end" prints last. That is 4 lines.'],
         code='console.log("start");\nswitch ("b") {\n  case "a": console.log("a");\n  case "b": console.log("b");\n  case "c": console.log("c"); break;\n  default: console.log("default");\n}\nconsole.log("end");'),
]

EX = [
    ex('grade', 'e', 'Grade a score', '<p>Write <code>grade(score)</code>: 90 and above is <code>"A"</code>, 75 to 89 is <code>"B"</code>, 50 to 74 is <code>"C"</code>, below 50 is <code>"F"</code>. Anything that is not a number from 0 to 100 returns <code>"invalid"</code>.</p>',
       'function grade(score) {\n  \n}\n',
       [('grade(95)', 'A'), ('grade(90)', 'A'), ('grade(89)', 'B'), ('grade(75)', 'B'), ('grade(50)', 'C'), ('grade(49)', 'F'), ('grade(0)', 'F'), ('grade(101)', 'invalid'), ('grade("80")', 'invalid')],
       'function grade(score) {\n  if (typeof score !== "number" || score < 0 || score > 100) return "invalid";\n  if (score >= 90) return "A";\n  if (score >= 75) return "B";\n  if (score >= 50) return "C";\n  return "F";\n}',
       hint='Start with a guard clause for invalid input, then check from the highest grade down.', why='Checking from the top band down means each condition only needs one comparison.'),
    ex('first-fail', 'm', 'Stop at the first failure', '<p>Write <code>firstFailure(results)</code>. It gets an array like <code>["pass", "pass", "fail"]</code> and returns the <b>index</b> of the first <code>"fail"</code>, or <code>-1</code> when there is none. Use a loop with <code>break</code> or <code>return</code>.</p>',
       'function firstFailure(results) {\n  \n}\n',
       [('firstFailure(["pass", "pass", "fail", "fail"])', 2), ('firstFailure(["fail"])', 0), ('firstFailure(["pass", "skip"])', -1), ('firstFailure([])', -1)],
       'function firstFailure(results) {\n  for (let i = 0; i < results.length; i++) {\n    if (results[i] === "fail") return i;\n  }\n  return -1;\n}', hint='A counter loop gives you the index.',
       why='Returning inside the loop stops it at once. The built in <code>results.indexOf("fail")</code> does the same thing.'),
    ex('retry-sync', 'h', 'Retry a flaky function', '<p>Write <code>retry(fn, attempts)</code>. Call <code>fn()</code>. If it throws, call it again, up to <code>attempts</code> calls in total. Return the first value it returns. If every call throws, throw the <b>last</b> error.</p>',
       'function retry(fn, attempts) {\n  return fn();\n}\n',
       [('(() => { let n = 0; return retry(() => { n++; if (n < 3) throw new Error("no"); return "ok on " + n; }, 5); })()', 'ok on 3'),
        ('(() => { let n = 0; try { retry(() => { n++; throw new Error("fail " + n); }, 3); } catch (e) { return e.message; } })()', 'fail 3'),
        ('(() => { let n = 0; retry(() => ++n, 4); return n; })()', 1)],
       'function retry(fn, attempts) {\n  let last;\n  for (let i = 0; i < attempts; i++) {\n    try {\n      return fn();\n    } catch (err) {\n      last = err;\n    }\n  }\n  throw last;\n}',
       hint='Put <code>try</code> and <code>catch</code> inside a loop. Remember the error in a variable outside the loop.', why='A successful call returns straight out of the loop. Only when the loop runs out does the saved error get thrown.'),
    ex('wait-until', 'x', 'Write waitUntil', '<p>Write an <code>async</code> function <code>waitUntil(check, timeout, interval)</code>. It calls <code>check()</code> (which may return a promise) until the result is truthy and returns that result. If <code>timeout</code> milliseconds pass first, it throws an error with the message <code>"timed out"</code>.</p>',
       'async function waitUntil(check, timeout, interval) {\n  return check();\n}\n',
       [('(async () => { let n = 0; return await waitUntil(() => (++n >= 3 ? "ready" : false), 1000, 10); })()', 'ready'),
        ('(async () => { try { await waitUntil(() => false, 60, 10); return "no error"; } catch (e) { return e.message; } })()', 'timed out'),
        ('(async () => await waitUntil(async () => 42, 100, 10))()', 42)],
       'async function waitUntil(check, timeout, interval) {\n  const start = Date.now();\n  while (true) {\n    const value = await check();\n    if (value) return value;\n    if (Date.now() - start >= timeout) throw new Error("timed out");\n    await new Promise(r => setTimeout(r, interval));\n  }\n}',
       hint='Remember the start time with <code>Date.now()</code>. Wait with <code>await new Promise(r => setTimeout(r, interval))</code>.',
       why='This is the core of every auto-waiting helper. Awaiting <code>check()</code> lets it work with both normal and async checks.'),
]

T = {
    'slug': 'js-control-flow', 'title': 'Control Flow, Loops and Errors', 'short': 'Control flow and errors', 'emoji': '🔀', 'module': MODULE, 'minutes': 18,
    'lead': 'if and switch, every kind of loop, the forEach and await trap, throwing and catching errors with causes and cleanup, and the polling and retry loops that power auto-waiting in every test tool.',
    'desc': 'if, else and switch, for, while, for...of and for...in loops, async loops, try, catch and finally, custom errors, polling, retries and data driven checks.',
    'summary': 'Decisions with if, else and switch, guard clauses, every loop with break, continue and labels, why forEach does not wait for await, throwing and catching errors with finally, custom errors and error causes, polling loops with timeouts, retries with backoff and data driven test tables.',
    'keywords': ['if else', 'switch', 'loops', 'for of', 'for in', 'while', 'break', 'continue', 'try catch', 'finally', 'throw', 'custom error', 'error cause', 'polling', 'retry', 'forEach await', 'data driven'],
    'qa_intro': 'The parts on async loops, errors and polling explain the three things behind most flaky UI tests: steps that are not awaited, cleanup that does not run, and fixed waits instead of polling.',
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
