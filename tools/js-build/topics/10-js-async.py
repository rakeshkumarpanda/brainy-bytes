# Chapter 10: the event loop, callbacks, promises, async and await, combinators, cancellation, retries and polling.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('⏳', 'Async and the platform', 'js-platform', 'Promises and the event loop, the browser DOM, and HTTP from both sides: everything a UI or API test waits for.')

TIMES = [(r'duration_ms [\d.]+', 'duration_ms 90'), (r' \(\d+(\.\d+)?ms\)', ''), (r'\n    generatedMessage[\s\S]*?\n  \}', '')]

CODES = {
    'order': run('''
console.log("1 start");
setTimeout(() => console.log("5 timeout"), 0);
Promise.resolve().then(() => console.log("3 promise"));
queueMicrotask(() => console.log("4 microtask"));
console.log("2 end");
''', 'Which line prints first'),
    'blocking': run('''
const started = Date.now();
setTimeout(() => console.log(`timer fired after ${Math.round((Date.now() - started) / 100) * 100} ms`), 100);

// A long loop keeps the only thread busy. Nothing else can run meanwhile.
const until = Date.now() + 500;
while (Date.now() < until) {}
console.log("busy loop done");
''', 'One thread: a busy loop delays everything'),
    'callbacks': run('''
import { readFile } from "node:fs";

// Node.js style: the callback receives (error, result)
readFile("missing.json", "utf8", (err, text) => {
  if (err) return console.log("callback got an error:", err.code);
  console.log(text);
});

// Callbacks inside callbacks get deep quickly
function step(name, done) { setTimeout(() => done(null, name), 10); }
step("login", (e1, a) => {
  step("search", (e2, b) => {
    step("checkout", (e3, c) => {
      console.log("finished:", a, b, c);
    });
  });
});
''', 'Callbacks and the pyramid they build', play=False),
    'promise': run('''
function wait(ms, value, fail = false) {
  return new Promise((resolve, reject) => {
    setTimeout(() => (fail ? reject(new Error(`${value} failed`)) : resolve(value)), ms);
  });
}

const p = wait(20, "token-123");
console.log(p);                              // still pending

p.then(token => {
  console.log("got", token);
  return wait(10, `profile for ${token}`);    // returning a promise chains it
})
  .then(profile => console.log(profile))
  .then(() => wait(10, "orders", true))
  .catch(err => console.log("caught:", err.message))   // one catch for the whole chain
  .finally(() => console.log("cleanup runs either way"));
''', 'Creating and chaining promises'),
    'with-resolvers': run('''
// ES2024: create a promise and get its resolve and reject functions outside it
const { promise, resolve } = Promise.withResolvers();

const events = [];
function onMessage(msg) {
  events.push(msg);
  if (msg === "order-confirmed") resolve(events.length);
}

setTimeout(() => onMessage("cart-updated"), 5);
setTimeout(() => onMessage("payment-ok"), 10);
setTimeout(() => onMessage("order-confirmed"), 15);

console.log("confirmed after", await promise, "events");
''', 'Promise.withResolvers for event driven code'),
    'async-await': run('''
const wait = (ms, v) => new Promise(r => setTimeout(() => r(v), ms));

async function login(user) {
  await wait(10);
  if (user === "blocked") throw new Error("account locked");
  return { user, token: "t-" + user };
}

async function main() {
  const session = await login("asha");      // reads like normal code
  console.log(session);
  try {
    await login("blocked");
  } catch (e) {
    console.log("caught:", e.message);
  }
  return "done";
}

const result = main();
console.log(result instanceof Promise);     // an async function always returns a promise
console.log(await result);
''', 'async and await'),
    'seq-par': run('''
const wait = (ms, v) => new Promise(r => setTimeout(() => r(v), ms));
const t = () => Math.round((performance.now() - start) / 100) * 100;
let start = performance.now();

const a = await wait(300, "users");
const b = await wait(300, "orders");
console.log("one after another:", t(), "ms", a, b);

start = performance.now();
const [c, d] = await Promise.all([wait(300, "users"), wait(300, "orders")]);
console.log("at the same time:", t(), "ms", c, d);
''', 'Sequential or parallel'),
    'forgot-await': test({
        'package.json': pkg('await-bug', 'module', {'test': 'node --test --test-reporter=spec'}),
        'status.test.js': '''
import { test } from "node:test";
import assert from "node:assert/strict";

async function getStatus() {
  await new Promise(r => setTimeout(r, 20));
  return 500;                                  // the server is broken
}

test("forgot await: passes by mistake", () => {
  getStatus().then(s => assert.equal(s, 200)); // the test ends before this runs
});

test("with await: fails as it should", async () => {
  assert.equal(await getStatus(), 200);
});
''',
    }, 'npm test', 'A missing await hides a real failure', expect='fail', replace=TIMES),
    'combinators': run('''
const ok = (ms, v) => new Promise(r => setTimeout(() => r(v), ms));
const bad = (ms, msg) => new Promise((_, j) => setTimeout(() => j(new Error(msg)), ms));

try {
  await Promise.all([ok(10, "a"), bad(20, "b broke"), ok(30, "c")]);
} catch (e) {
  console.log("all: rejects on the first failure ->", e.message);
}

const settled = await Promise.allSettled([ok(10, "a"), bad(20, "b broke")]);
console.log("allSettled:", settled.map(r => r.status === "fulfilled" ? r.value : r.reason.message));

console.log("race:", await Promise.race([ok(30, "slow"), ok(10, "fast")]));

console.log("any:", await Promise.any([bad(5, "mirror 1 down"), ok(20, "mirror 2"), ok(30, "mirror 3")]));
try {
  await Promise.any([bad(5, "x"), bad(10, "y")]);
} catch (e) {
  console.log("any, all failed:", e.constructor.name, e.errors.map(x => x.message));
}
''', 'all, allSettled, race and any'),
    'abort': run('''
async function slowRequest(signal) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => resolve("response"), 500);
    signal.addEventListener("abort", () => {
      clearTimeout(timer);
      reject(signal.reason);
    }, { once: true });
  });
}

// Cancel by hand
const controller = new AbortController();
setTimeout(() => controller.abort(new Error("user left the page")), 50);
await slowRequest(controller.signal).catch(e => console.log("aborted:", e.message));

// Cancel on a timeout
await slowRequest(AbortSignal.timeout(100)).catch(e => console.log("timed out:", e.name));

// Whichever comes first
const either = AbortSignal.any([AbortSignal.timeout(80), new AbortController().signal]);
await slowRequest(either).catch(e => console.log("any:", e.name));
''', 'Cancelling with AbortController'),
    'retry': run('''
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function retry(fn, { attempts = 4, baseMs = 20 } = {}) {
  for (let i = 1; ; i++) {
    try {
      return await fn(i);
    } catch (e) {
      if (i === attempts) throw e;
      const delay = baseMs * 2 ** (i - 1);            // 20, 40, 80 ...
      console.log(`attempt ${i} failed (${e.message}), waiting ${delay} ms`);
      await sleep(delay);
    }
  }
}

let calls = 0;
const flakyService = async () => {
  calls++;
  if (calls < 3) throw new Error("503 Service Unavailable");
  return { status: 200 };
};
console.log(await retry(flakyService));
''', 'Retry with exponential backoff'),
    'poll': run('''
const sleep = ms => new Promise(r => setTimeout(r, ms));

// Keep checking until the condition is true, or give up after timeout
async function waitFor(check, { timeout = 1000, interval = 50, message = "condition" } = {}) {
  const deadline = Date.now() + timeout;
  let lastError;
  while (Date.now() < deadline) {
    try {
      const value = await check();
      if (value) return value;
    } catch (e) {
      lastError = e;
    }
    await sleep(interval);
  }
  throw new Error(`Timed out after ${timeout} ms waiting for ${message}` + (lastError ? `: ${lastError.message}` : ""));
}

// A report that becomes ready after about 200 ms
const readyAt = Date.now() + 200;
const getReport = async () => (Date.now() >= readyAt ? { status: "ready", rows: 42 } : { status: "processing" });

const report = await waitFor(async () => {
  const r = await getReport();
  return r.status === "ready" && r;
}, { message: "the report" });
console.log(report);

await waitFor(() => false, { timeout: 150, message: "a button that never appears" }).catch(e => console.log(e.message));
''', 'Poll until a condition is true'),
    'pw-waits': show('''
// Playwright waits for you: actions wait for the element to be visible, enabled and stable
await page.getByRole("button", { name: "Pay" }).click();

// Web first assertions keep retrying until they pass or time out
await expect(page.getByText("Payment received")).toBeVisible({ timeout: 10_000 });

// Poll anything, such as an API, with expect.poll
await expect.poll(async () => {
  const res = await request.get("/api/orders/42");
  return (await res.json()).status;
}, { timeout: 30_000 }).toBe("shipped");

// Wait for a response the page makes
const [response] = await Promise.all([
  page.waitForResponse(r => r.url().includes("/api/cart") && r.ok()),
  page.getByRole("button", { name: "Add to cart" }).click(),
]);

// Avoid: a fixed sleep is either too long or too short
await page.waitForTimeout(3000);
''', 'Waiting the right way in Playwright', note='Runs for real in chapter 21'),
    'scenario': run('''
// Check 8 product URLs, at most 3 requests at a time, with a timeout on each.
const sleep = ms => new Promise(r => setTimeout(r, ms));
const latency = { "/p/1": 30, "/p/2": 50, "/p/3": 400, "/p/4": 20, "/p/5": 40, "/p/6": 30, "/p/7": 25, "/p/8": 35 };
let active = 0, peak = 0;

async function fakeFetch(url, { signal }) {
  active++; peak = Math.max(peak, active);
  try {
    await new Promise((resolve, reject) => {
      const t = setTimeout(resolve, latency[url]);
      signal.addEventListener("abort", () => { clearTimeout(t); reject(signal.reason); });
    });
    return { url, status: url === "/p/5" ? 404 : 200 };
  } finally {
    active--;
  }
}

async function mapLimit(items, limit, fn) {
  const results = new Array(items.length);
  let next = 0;
  async function worker() {
    while (next < items.length) {
      const i = next++;
      results[i] = await fn(items[i]);
    }
  }
  await Promise.all(Array.from({ length: limit }, worker));
  return results;
}

const urls = Object.keys(latency);
const results = await mapLimit(urls, 3, url =>
  fakeFetch(url, { signal: AbortSignal.timeout(200) })
    .then(r => ({ url, ok: r.status === 200, status: r.status }))
    .catch(e => ({ url, ok: false, status: e.name })));

console.table(results);
console.log("peak parallel requests:", peak);
console.log("broken:", results.filter(r => !r.ok).map(r => `${r.url} (${r.status})`).join(", "));
''', 'A link checker with a concurrency limit and timeouts'),
}

PARTS = [
    part('event-loop', '🔄', 'One thread and the event loop', '''
<p>JavaScript runs your code on <b>one thread</b>: one line at a time. Slow work such as a network request, a timer or reading a file is handed to the browser or Node.js, and your code keeps going. When the slow work finishes, a <b>callback</b> is queued. The <b>event loop</b> runs queued callbacks only when the call stack is empty.</p>
<div class="viz" data-viz="lanes" data-k="loop"></div>
[[order]]
<div class="tw"><table class="jt"><tr><th>Queue</th><th>What goes there</th><th>When it runs</th></tr>
<tr><td>Microtasks</td><td>promise callbacks (<code>then</code>, code after <code>await</code>), <code>queueMicrotask</code></td><td>right after the current code, all of them, before anything else</td></tr>
<tr><td>Tasks (macrotasks)</td><td><code>setTimeout</code>, <code>setInterval</code>, clicks, network and file events</td><td>one per turn of the loop, after the microtasks are empty</td></tr>
</table></div>
<p>Because there is only one thread, a long loop blocks everything: timers, clicks and screen updates all wait.</p>
[[blocking]]
''', kw=['event loop', 'single thread', 'call stack', 'microtask', 'macrotask', 'task queue', 'setTimeout', 'queueMicrotask', 'blocking', 'non-blocking']),
    part('callbacks', '📞', 'Callbacks', '''
<p>The first way to handle async work was to pass a function to call later. Node.js callbacks receive the error first and the result second. It works, but each step that depends on the previous one adds a level of nesting, known as callback hell, and error handling must be repeated at every level.</p>
[[callbacks]]
<div class="tip">Most Node.js APIs now have promise versions: <code>import { readFile } from "node:fs/promises"</code>. For an old callback API, <code>util.promisify(fn)</code> creates one.</div>
''', kw=['callback', 'error-first callback', 'callback hell', 'promisify', 'fs/promises']),
    part('promises', '🤝', 'Promises', '''
<p>A <b>promise</b> is an object that stands for a result that is not ready yet. It starts <b>pending</b>, then becomes <b>fulfilled</b> with a value or <b>rejected</b> with an error, and never changes again. <code>then</code> runs when it fulfils, <code>catch</code> when it rejects and <code>finally</code> either way. Returning a value or a promise from <code>then</code> passes it to the next step, so the steps form a flat chain.</p>
[[promise]]
[[with-resolvers]]
<div class="warn">A rejected promise that nobody catches is an <b>unhandled rejection</b>. In Node.js it crashes the process, and in test runners it often shows up as a confusing failure in a different test.</div>
''', qa=True, qa_why='Every Playwright, WebdriverIO and Selenium call returns a promise, so you need to know what one is.',
        kw=['Promise', 'pending', 'fulfilled', 'rejected', 'then', 'catch', 'finally', 'chaining', 'unhandled rejection', 'Promise.withResolvers', 'resolve', 'reject']),
    part('async-await', '⏸️', 'async and await', '''
<p><code>async</code> before a function makes it return a promise. Inside it, <code>await</code> pauses that function until a promise settles and gives you its value, while the rest of the program keeps running. Errors become normal exceptions you catch with <code>try</code> and <code>catch</code>.</p>
[[async-await]]
<h3>Sequential or parallel</h3>
<p>Two <code>await</code> lines one after another run one after another. When the steps do not depend on each other, start both and wait for both with <code>Promise.all</code>.</p>
[[seq-par]]
<h3>The most common bug in test code</h3>
<p>Forgetting <code>await</code> lets the test finish before the check runs. The test is reported as passed even though the server returned an error. The Node.js runner at least prints a warning about activity after the test ended. Many other runners print nothing at all.</p>
[[forgot-await]]
<div class="qa-box">Every Playwright action (<code>click</code>, <code>fill</code>, <code>goto</code>) and every <code>expect(locator)</code> assertion must be awaited. WebdriverIO and Selenium JavaScript are the same. Cypress is the exception: its commands are queued and you must not await them. Turn on the lint rule <code>no-floating-promises</code> to catch a missing await automatically.</div>
''', qa=['Playwright', 'Selenium', 'WebdriverIO', 'Jest', 'Cypress'], qa_why='A missing await is the number one cause of flaky and falsely passing automated tests.',
        kw=['async', 'await', 'try catch', 'Promise.all', 'sequential', 'parallel', 'forgot await', 'floating promise', 'false positive', 'flaky test', 'top level await']),
    part('combinators', '🧮', 'Running many promises: all, allSettled, race, any', '''
<p>Four helpers combine several promises into one. They differ in what counts as done and what happens on a failure.</p>
[[combinators]]
<div class="tw"><table class="jt"><tr><th>Helper</th><th>Fulfils when</th><th>Rejects when</th><th>Good for</th></tr>
<tr><td><code>Promise.all</code></td><td>all fulfil</td><td>the first one rejects</td><td>steps that must all succeed</td></tr>
<tr><td><code>Promise.allSettled</code></td><td>all have finished, either way</td><td>never</td><td>reports: check every link, list each result</td></tr>
<tr><td><code>Promise.race</code></td><td>the first one settles</td><td>the first one settles with an error</td><td>timeouts</td></tr>
<tr><td><code>Promise.any</code></td><td>the first one fulfils</td><td>all reject (<code>AggregateError</code>)</td><td>the fastest of several mirrors</td></tr>
</table></div>
<h3>Cancelling</h3>
<p>An <b>AbortController</b> gives you a <code>signal</code> to pass to <code>fetch</code> and other APIs, and an <code>abort()</code> method to stop them. <code>AbortSignal.timeout(ms)</code> aborts by itself, and <code>AbortSignal.any</code> combines signals.</p>
[[abort]]
''', qa=['Playwright', 'Jest'], qa_why='Clicking and waiting for a response together, checking many endpoints, and timeouts all use these helpers.',
        kw=['Promise.all', 'Promise.allSettled', 'Promise.race', 'Promise.any', 'AggregateError', 'AbortController', 'AbortSignal', 'AbortSignal.timeout', 'AbortSignal.any', 'cancel', 'timeout']),
    part('waiting', '⏱️', 'Retries, polling and waiting the right way', '''
<p>Tests and scripts often wait for something that happens at an unknown time: an element appears, a job finishes, a service recovers. A <b>fixed sleep</b> guesses the time. It wastes time when the guess is too long and fails when it is too short. <b>Polling</b> checks again and again until the condition is true or a timeout is reached.</p>
<div class="viz" data-viz="wait"></div>
[[poll]]
<p>A <b>retry with exponential backoff</b> repeats a failing call with longer and longer pauses, which gives a struggling server room to recover.</p>
[[retry]]
<p>Modern tools build this in, so you rarely write the loop yourself.</p>
[[pw-waits]]
<div class="qa-box">Retrying a whole test hides flakiness. Use retries for setup calls to unstable services and report retried tests as flaky, but fix the cause: a missing wait for a response, a fixed sleep, or shared test data.</div>
''', qa=['Playwright', 'Cypress', 'Selenium', 'WebdriverIO'], qa_why='Waiting correctly is the difference between a stable suite and a flaky one.',
        kw=['wait', 'polling', 'waitFor', 'sleep', 'fixed sleep', 'retry', 'exponential backoff', 'auto-waiting', 'expect.poll', 'waitForResponse', 'flaky']),
    part('scenario', '🎬', 'Real world scenario: a link checker', '''
<div class="scenario"><b>The situation</b>Before a release you must check that 8 product pages respond. The server must not get more than 3 requests at once, a page that takes longer than 200 ms counts as broken, and the report must list every page, not stop at the first problem.</div>
[[scenario]]
<p><code>mapLimit</code> starts 3 workers that take the next URL as soon as they are free. <code>AbortSignal.timeout</code> stops slow requests, and catching each error turns it into a row in the report instead of stopping the run.</p>
''', qa=True, kw=['link checker', 'concurrency limit', 'mapLimit', 'timeout', 'smoke test', 'AbortSignal.timeout', 'report']),
]

LANES = {
    'loop': {'t': 'The event loop runs the queues in order',
             'code': 'console.log("1 start");\nsetTimeout(() => console.log("5 timeout"), 0);\nPromise.resolve().then(() => console.log("3 promise"));\nqueueMicrotask(() => console.log("4 microtask"));\nconsole.log("2 end");',
             'lanes': ['Call stack', 'Microtasks', 'Tasks', 'Console'], 'tone': [2, 1, 3, 4],
             'steps': [{'l': 1, 'v': [['main code'], [], [], ['1 start']], 'm': 'The main code starts running on the call stack.'},
                       {'l': 2, 'v': [['main code'], [], ['timeout callback'], ['1 start']], 'm': 'setTimeout hands its callback to the timer. Even with 0 ms it waits in the task queue.'},
                       {'l': 3, 'v': [['main code'], ['promise callback'], ['timeout callback'], ['1 start']], 'm': 'The promise is already resolved, so its then callback goes to the microtask queue.'},
                       {'l': 4, 'v': [['main code'], ['promise callback', 'microtask callback'], ['timeout callback'], ['1 start']], 'm': 'queueMicrotask adds another microtask behind it.'},
                       {'l': 5, 'v': [[], ['promise callback', 'microtask callback'], ['timeout callback'], ['1 start', '2 end']], 'm': 'The main code ends. The call stack is empty, so the event loop takes over.'},
                       {'l': [3, 4], 'v': [[], [], ['timeout callback'], ['1 start', '2 end', '3 promise', '4 microtask']], 'm': 'All microtasks run first, in order, until that queue is empty.'},
                       {'l': 2, 'v': [[], [], [], ['1 start', '2 end', '3 promise', '4 microtask', '5 timeout']], 'm': 'Only then does the loop take one task: the timeout callback.'}]},
}

INFO = {'title': 'Waiting without stopping', 'panels': [
    panel([['e', '🧵'], ['t', 'one thread', {'b': 1}]], 'One thread', 'JavaScript runs one thing at a time.', 'Slow work is handed off so the page stays responsive.'),
    panel([['e', '🤝'], ['t', 'pending → fulfilled', {'b': 1}]], 'Promises', 'A placeholder for a value that comes later.', 'then, catch and finally react to the result.'),
    panel([['e', '⏸️'], ['t', 'await page.click()', {'b': 1}]], 'await', 'Pause this function until the promise settles.', 'Forget it and the test ends before the check runs.'),
    panel([['e', '⏱️'], ['t', 'poll, do not sleep', {'b': 1}]], 'Waiting', 'Check until true, with a timeout.', 'Fixed sleeps are the classic source of flaky tests.')],
    'remember': 'Await every promise you care about, run independent work in parallel, and poll instead of sleeping.'}

REAL = [
    ['🛍️', 'A product page', 'The page asks for details, reviews and stock at the same time with Promise.all, so it loads in the time of the slowest call, not the sum of all three.'],
    ['🔁', 'A flaky payment sandbox', 'A test setup call to a third party sandbox retries with backoff, while the tests themselves never retry silently.'],
    ['🔗', 'Release smoke check', 'A CI job checks 500 URLs with 10 requests at a time and allSettled, then posts the broken ones to the team.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers the event loop, callbacks, promises, async and await, combining promises, cancelling, retries and polling.',
        'यह अध्याय event loop, callbacks, promises, async और await, promises को जोड़ना, cancel करना, retries और polling सिखाता है।',
        'ಈ ಅಧ್ಯಾಯ event loop, callbacks, promises, async ಮತ್ತು await, promises ಜೋಡಣೆ, cancel, retries ಮತ್ತು polling ಕಲಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ event loop, callbacks, promises, async ଓ await, promises ଯୋଡ଼ିବା, cancel, retries ଓ polling ଶିଖାଏ।',
        'يتناول هذا الفصل حلقة الأحداث والاستدعاءات الراجعة والوعود وasync وawait ودمج الوعود والإلغاء وإعادة المحاولة والاستطلاع.',
        'Dieses Kapitel behandelt die Event Loop, Callbacks, Promises, async und await, kombinierte Promises, Abbruch, Wiederholungen und Polling.'),
    say('event-loop', 'Event loop', 'JavaScript runs on one thread. When the stack is empty, the event loop runs all microtasks first, then one task such as a timer.',
        'JavaScript एक thread पर चलता है। Stack खाली होने पर event loop पहले सारे microtasks, फिर एक task जैसे timer चलाता है।',
        'JavaScript ಒಂದು thread ನಲ್ಲಿ ಓಡುತ್ತದೆ. Stack ಖಾಲಿಯಾದಾಗ event loop ಮೊದಲು ಎಲ್ಲ microtasks, ನಂತರ timer ನಂತಹ ಒಂದು task ಓಡಿಸುತ್ತದೆ.',
        'JavaScript ଗୋଟିଏ thread ରେ ଚାଲେ। Stack ଖାଲି ହେଲେ event loop ପ୍ରଥମେ ସବୁ microtasks, ତାପରେ timer ପରି ଗୋଟିଏ task ଚଲାଏ।',
        'تعمل JavaScript على خيط واحد. عندما يفرغ المكدس تنفذ حلقة الأحداث كل المهام الدقيقة أولًا ثم مهمة واحدة مثل المؤقت.',
        'JavaScript läuft auf einem Thread. Ist der Stack leer, führt die Event Loop erst alle Microtasks aus, dann eine Task wie einen Timer.'),
    say('callbacks', 'Callbacks', 'Callbacks are functions called later. Nested callbacks get deep, so modern code uses promise based versions.',
        'Callbacks बाद में call होने वाले functions हैं। Nested callbacks गहरे हो जाते हैं, इसलिए आधुनिक code promise वाले versions इस्तेमाल करता है।',
        'Callbacks ನಂತರ ಕರೆಯುವ functions. Nested callbacks ಆಳವಾಗುತ್ತವೆ, ಆದ್ದರಿಂದ ಆಧುನಿಕ code promise versions ಬಳಸುತ್ತದೆ.',
        'Callbacks ପରେ call ହେଉଥିବା functions। Nested callbacks ଗଭୀର ହୁଏ, ତେଣୁ ଆଧୁନିକ code promise versions ବ୍ୟବହାର କରେ।',
        'الاستدعاءات الراجعة دوال تستدعى لاحقًا. تتعمق المتداخلة منها، لذا يستخدم الكود الحديث نسخًا تعتمد على الوعود.',
        'Callbacks sind Funktionen, die später aufgerufen werden. Verschachtelt werden sie tief, daher nutzt moderner Code Promise-Versionen.'),
    say('promises', 'Promises', 'A promise is pending, then fulfilled or rejected. Then, catch and finally react to it, and a chain stays flat.',
        'Promise पहले pending होता है, फिर fulfilled या rejected। then, catch और finally उस पर react करते हैं।',
        'Promise ಮೊದಲು pending, ನಂತರ fulfilled ಅಥವಾ rejected. then, catch ಮತ್ತು finally ಅದಕ್ಕೆ ಪ್ರತಿಕ್ರಿಯಿಸುತ್ತವೆ.',
        'Promise ପ୍ରଥମେ pending, ତାପରେ fulfilled କିମ୍ବା rejected। then, catch ଓ finally ତାହା ଉପରେ react କରନ୍ତି।',
        'يكون الوعد معلقًا ثم يتحقق أو يرفض. تستجيب له then وcatch وfinally وتبقى السلسلة مسطحة.',
        'Ein Promise ist erst ausstehend, dann erfüllt oder abgelehnt. then, catch und finally reagieren darauf.'),
    say('async-await', 'async and await', 'await pauses a function until a promise settles. Forgetting await in a test lets it pass while the real check fails later.',
        'await function को promise पूरा होने तक रोकता है। Test में await भूलने से test pass हो जाता है जबकि असली check बाद में fail होता है।',
        'await promise ಮುಗಿಯುವವರೆಗೆ function ನಿಲ್ಲಿಸುತ್ತದೆ. Test ನಲ್ಲಿ await ಮರೆತರೆ test pass ಆಗುತ್ತದೆ, ನಿಜವಾದ check ನಂತರ fail ಆಗುತ್ತದೆ.',
        'await promise ଶେଷ ହେବା ପର୍ଯ୍ୟନ୍ତ function କୁ ଅଟକାଏ। Test ରେ await ଭୁଲିଲେ test pass ହୁଏ, ଅସଲ check ପରେ fail ହୁଏ।',
        'توقف await الدالة حتى يستقر الوعد. نسيانها في الاختبار يجعله ينجح بينما يفشل الفحص الحقيقي لاحقًا.',
        'await pausiert eine Funktion, bis das Promise fertig ist. Fehlt await im Test, besteht er, obwohl die Prüfung später scheitert.'),
    say('combinators', 'Combinators', 'all needs every promise, allSettled reports each one, race takes the first to finish and any takes the first success. AbortController cancels work.',
        'all को हर promise चाहिए, allSettled हर एक बताता है, race पहला खत्म होने वाला और any पहली सफलता लेता है। AbortController काम cancel करता है।',
        'all ಗೆ ಎಲ್ಲ promise ಬೇಕು, allSettled ಪ್ರತಿಯೊಂದನ್ನು ತಿಳಿಸುತ್ತದೆ, race ಮೊದಲು ಮುಗಿದದ್ದು, any ಮೊದಲ ಯಶಸ್ಸು. AbortController ಕೆಲಸ cancel ಮಾಡುತ್ತದೆ.',
        'all କୁ ସବୁ promise ଦରକାର, allSettled ପ୍ରତ୍ୟେକକୁ ଜଣାଏ, race ପ୍ରଥମ ଶେଷ ହେଉଥିବା ଓ any ପ୍ରଥମ ସଫଳତା ନିଏ। AbortController କାମ cancel କରେ।',
        'تحتاج all كل الوعود، وتبلغ allSettled عن كل واحد، وتأخذ race أول من ينتهي وany أول نجاح. ويلغي AbortController العمل.',
        'all braucht jedes Promise, allSettled meldet jedes, race nimmt das erste fertige, any den ersten Erfolg. AbortController bricht Arbeit ab.'),
    say('waiting', 'Waiting', 'Poll until a condition is true instead of sleeping for a fixed time. Retry with backoff for unstable services.',
        'Fixed समय sleep करने की जगह condition true होने तक poll करें। अस्थिर services के लिए backoff के साथ retry करें।',
        'Fixed ಸಮಯ sleep ಬದಲು condition true ಆಗುವವರೆಗೆ poll ಮಾಡಿ. ಅಸ್ಥಿರ services ಗೆ backoff ಜೊತೆ retry ಮಾಡಿ.',
        'Fixed ସମୟ sleep ବଦଳରେ condition true ହେବା ପର୍ଯ୍ୟନ୍ତ poll କରନ୍ତୁ। ଅସ୍ଥିର services ପାଇଁ backoff ସହ retry କରନ୍ତୁ।',
        'استطلع حتى يتحقق الشرط بدل الانتظار لوقت ثابت. أعد المحاولة مع تراجع تدريجي للخدمات غير المستقرة.',
        'Prüfe wiederholt, bis eine Bedingung stimmt, statt fest zu warten. Wiederhole mit Backoff bei instabilen Diensten.'),
    say('scenario', 'Scenario', 'A link checker runs three requests at a time, stops slow ones with a timeout and reports every page.',
        'Link checker एक साथ तीन requests चलाता है, धीमी requests timeout से रोकता है और हर page की report देता है।',
        'Link checker ಒಮ್ಮೆಗೆ ಮೂರು requests ಓಡಿಸುತ್ತದೆ, ನಿಧಾನವಾದವನ್ನು timeout ನಿಂದ ನಿಲ್ಲಿಸುತ್ತದೆ, ಪ್ರತಿ page ವರದಿ ಮಾಡುತ್ತದೆ.',
        'Link checker ଏକାସାଙ୍ଗରେ ତିନୋଟି requests ଚଲାଏ, ଧୀର ଗୁଡ଼ିକୁ timeout ରେ ଅଟକାଏ ଏବଂ ପ୍ରତ୍ୟେକ page ର report ଦିଏ।',
        'يشغل مدقق الروابط ثلاثة طلبات في وقت واحد، ويوقف البطيء منها بمهلة، ويبلغ عن كل صفحة.',
        'Ein Linkprüfer führt drei Anfragen gleichzeitig aus, stoppt langsame per Timeout und meldet jede Seite.'),
    say('practice', 'Hands-on', 'Practise a sleep helper, a timeout wrapper, a retry helper and a concurrency limit.',
        'Sleep helper, timeout wrapper, retry helper और concurrency limit का अभ्यास करें।',
        'Sleep helper, timeout wrapper, retry helper ಮತ್ತು concurrency limit ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Sleep helper, timeout wrapper, retry helper ଓ concurrency limit ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على دالة انتظار وغلاف مهلة ودالة إعادة محاولة وحد للتوازي.',
        'Übe einen Sleep-Helfer, einen Timeout-Wrapper, einen Retry-Helfer und ein Parallelitätslimit.'),
]

QUIZ = [
    quiz('e', 'What does an async function always return?', ['A promise', 'undefined', 'The value directly', 'A callback'], 0, 'Even return 5 is wrapped.', 'The returned value becomes the fulfilled value of a promise.'),
    quiz('e', 'Which helper rejects as soon as one promise rejects?', ['Promise.all', 'Promise.allSettled', 'Promise.any', 'None of them'], 0, 'All or nothing.', 'Promise.all fails fast on the first rejection.'),
    quiz('e', 'In Playwright, what is missing in page.getByRole("button").click() inside an async test?', ['await', 'then', 'async', 'Nothing'], 0, 'Actions return promises.', 'Without await the test moves on before the click finishes.'),
    quiz('m', 'Which runs first: a setTimeout(fn, 0) callback or a Promise.resolve().then(fn) callback?', ['The promise callback', 'The timeout callback', 'They run together', 'It is random'], 0, 'Microtasks before tasks.', 'Promise callbacks are microtasks and run before the next task.'),
    quiz('m', 'Two independent awaits of 300 ms each, one after the other, take about how long?', ['600 ms', '300 ms', '0 ms', '900 ms'], 0, 'One waits for the other.', 'Sequential awaits add up. Promise.all would take about 300 ms.'),
    quiz('m', 'What does Promise.allSettled never do?', ['Reject', 'Fulfil', 'Wait for every promise', 'Return statuses'], 0, 'It always reports.', 'It waits for all and fulfils with a status for each.'),
    quiz('h', 'A test calls getStatus().then(s => assert.equal(s, 200)) without returning or awaiting it. Why does it pass?', ['The test ends before the assertion runs', 'assert.equal never fails', 'then swallows errors', 'Status is 200'], 0, 'Who waits for the promise?', 'Nothing waits for the promise, so the runner sees a test that finished without errors.'),
    quiz('h', 'Promise.any rejects with which error when every promise rejects?', ['AggregateError', 'TypeError', 'RangeError', 'AbortError'], 0, 'It collects all the errors.', 'An AggregateError has an errors array with each reason.'),
    quiz('h', 'Why is page.waitForTimeout(3000) considered a bad wait?', ['It is too long when the app is fast and too short when it is slow', 'It is not supported', 'It clicks the page', 'It never ends'], 0, 'A guess.', 'A fixed sleep wastes time or fails. Waiting for a condition does neither.'),
    quiz('x', 'In Cypress, why should you not write await cy.get("button")?', ['Cypress commands are queued, not promises you await', 'Cypress has no buttons', 'await is not allowed in tests', 'It is faster without'], 0, 'Cypress has its own command queue.', 'Cypress runs its queued commands in order by itself. Mixing await with them breaks that.'),
    quiz('x', 'What is the delay before the 3rd retry when the base is 20 ms and it doubles each time?', ['80 ms', '60 ms', '40 ms', '20 ms'], 0, '20, 40, 80.', 'The waits are base × 2 to the power of (attempt minus 1).'),
    quiz('x', 'What does AbortSignal.any([a, b]) return?', ['A signal that aborts when either a or b aborts', 'The first signal', 'A promise', 'A boolean'], 0, 'Combine reasons to stop.', 'Useful to stop on a timeout or when the user cancels, whichever comes first.'),
]

CALC = [
    calc('e', 'Three API calls take 200, 350 and 150 ms. How many ms does Promise.all take?', '350', 'The slowest decides.', ['They run together, so the time is the longest one.']),
    calc('e', 'The same three calls awaited one after another take how many ms?', '700', 'Add them.', ['<span class="eq">200 + 350 + 150 = 700</span>']),
    calc('m', 'Retry with base 100 ms doubling, 4 attempts. How many ms of waiting in total if all 4 fail?', '700', 'Waits happen between attempts.', ['Three waits: 100, 200 and 400.', '<span class="eq">100 + 200 + 400 = 700</span>']),
    calc('m', 'Polling every 50 ms with a 1000 ms timeout checks at most how many times?', '20', 'Divide.', ['<span class="eq">1000 ÷ 50 = 20</span>']),
    calc('h', 'In the order example, which number is printed last?', '5', 'Tasks come after all microtasks.', ['1 and 2 are the main code.', '3 and 4 are microtasks.', '5 is the timeout task.']),
    calc('h', '12 requests of 100 ms each run with a limit of 3 at a time. About how many ms in total?', '400', 'Batches of 3.', ['<span class="eq">12 ÷ 3 = 4</span> rounds.', '<span class="eq">4 × 100 = 400</span> ms.']),
    calc('x', 'A test suite has 200 fixed sleeps of 2 s. The real waits average 0.4 s. How many seconds are wasted per run?', '320', 'Wasted time per sleep times count.', ['<span class="eq">2 − 0.4 = 1.6</span> s per sleep.', '<span class="eq">1.6 × 200 = 320</span> s.']),
    calc('x', 'The exponential backoff delay is base × 2<sup>n−1</sup>. With base 250 ms, what is the delay before attempt 5, that is after 4 failures?', '2000', 'n is 4 here.', ['<span class="eq">250 × 2<sup>3</sup> = 250 × 8 = 2000</span> ms.']),
]

EX = [
    ex('sleep', 'e', 'A sleep helper', '<p>Write <code>sleep(ms, value)</code> that returns a promise which fulfils with <code>value</code> after <code>ms</code> milliseconds.</p>',
       'function sleep(ms, value) {\n  \n}\n',
       [('sleep(10, "done")', 'done'), ('(async () => { const t = Date.now(); await sleep(50); return Date.now() - t >= 45; })()', True)],
       'function sleep(ms, value) {\n  return new Promise(resolve => setTimeout(() => resolve(value), ms));\n}', hint='<code>new Promise(resolve =&gt; setTimeout(...))</code>.', why='Wrapping a callback API in a promise is how almost every async helper is built.'),
    ex('timeout', 'm', 'Give up after a timeout', '<p>Write <code>withTimeout(promise, ms)</code>. It fulfils with the promise value if it settles in time, otherwise it rejects with an Error whose message is <code>"Timed out after ms ms"</code> (with the number).</p>',
       'function withTimeout(promise, ms) {\n  \n}\n',
       [('withTimeout(new Promise(r => setTimeout(() => r("ok"), 10)), 100)', 'ok'),
        ('withTimeout(new Promise(r => setTimeout(() => r("late"), 200)), 30).catch(e => e.message)', 'Timed out after 30 ms')],
       'function withTimeout(promise, ms) {\n  const timer = new Promise((_, reject) =>\n    setTimeout(() => reject(new Error(`Timed out after ${ms} ms`)), ms));\n  return Promise.race([promise, timer]);\n}',
       hint='<code>Promise.race</code> with a promise that rejects after <code>ms</code>.', why='race settles with whichever finishes first. A production version also clears the timer, which AbortSignal.timeout does for you.'),
    ex('retry', 'h', 'Retry a flaky call', '<p>Write <code>retry(fn, attempts)</code> that calls the async function <code>fn</code> and returns its result. If it throws, call it again, up to <code>attempts</code> times in total. If the last attempt also throws, reject with that last error.</p>',
       'async function retry(fn, attempts) {\n  \n}\n',
       [('(async () => { let n = 0; return await retry(async () => { n++; if (n < 3) throw new Error("x"); return n; }, 5); })()', 3),
        ('(async () => { let n = 0; try { await retry(async () => { n++; throw new Error("down " + n); }, 2); } catch (e) { return [n, e.message]; } })()', [2, 'down 2'])],
       'async function retry(fn, attempts) {\n  let lastError;\n  for (let i = 0; i < attempts; i++) {\n    try {\n      return await fn();\n    } catch (e) {\n      lastError = e;\n    }\n  }\n  throw lastError;\n}',
       hint='A loop with <code>try</code> and <code>return await fn()</code> inside.', why='<code>return await</code> inside <code>try</code> matters: without await, a rejection would escape the try block and skip the retry.'),
    ex('limit', 'x', 'Run with a concurrency limit', '<p>Write <code>mapLimit(items, limit, fn)</code> that calls the async <code>fn(item)</code> for every item, with at most <code>limit</code> calls running at the same time, and returns the results in the original order.</p>',
       'async function mapLimit(items, limit, fn) {\n  \n}\n',
       [('(async () => { let active = 0, peak = 0; const out = await mapLimit([30, 10, 20, 5, 15], 2, async ms => { active++; peak = Math.max(peak, active); await new Promise(r => setTimeout(r, ms)); active--; return ms * 2; }); return [out, peak]; })()', [[60, 20, 40, 10, 30], 2]),
        ('mapLimit([], 3, async x => x)', [])],
       'async function mapLimit(items, limit, fn) {\n  const results = new Array(items.length);\n  let next = 0;\n  async function worker() {\n    while (next < items.length) {\n      const i = next++;\n      results[i] = await fn(items[i]);\n    }\n  }\n  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, worker));\n  return results;\n}',
       hint='Start <code>limit</code> workers. Each one takes the next index in a loop until none are left.', why='Saving each result at its own index keeps the order, even though calls finish in a different order.'),
]

T = {
    'slug': 'js-async', 'title': 'Asynchronous JavaScript: Promises, async and await', 'short': 'Async JavaScript', 'emoji': '⏳', 'module': MODULE, 'minutes': 18,
    'lead': 'How one thread handles slow work with the event loop, callbacks, promises, async and await, running promises together, cancelling with AbortController, and waiting with retries and polling instead of fixed sleeps.',
    'desc': 'Event loop, microtasks, callbacks, promises, async, await, Promise.all, allSettled, race, any, AbortController, retries with backoff and polling.',
    'summary': 'The single thread and the event loop with microtasks and tasks, error first callbacks, promises and chaining, Promise.withResolvers, async and await, sequential against parallel awaits, the missing await that makes a test pass by mistake, all, allSettled, race and any, AbortController and AbortSignal.timeout, polling and retry with exponential backoff, waiting in Playwright, and a link checker with a concurrency limit.',
    'keywords': ['event loop', 'microtask', 'callback', 'Promise', 'then', 'catch', 'async', 'await', 'Promise.all', 'Promise.allSettled', 'Promise.race', 'Promise.any', 'AbortController', 'timeout', 'retry', 'backoff', 'polling', 'flaky tests'],
    'qa_intro': 'Every browser and API action in a test is asynchronous. Missing awaits and fixed sleeps cause most flaky tests, and this chapter shows both.',
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
