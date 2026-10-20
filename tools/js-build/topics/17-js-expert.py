# Chapter 17: expert habits for developers and testers: performance, memory, patterns, workers, security and test quality.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🧠', 'Expert and latest', 'js-expert', 'The newest language features, performance, patterns, security and the habits of expert JavaScript developers and testers.')

TIMING = [(r'\d+\.\d+ ms', 'x.xx ms')]

CODES = {
    'bigo': run('''
// Count the work instead of the time: the count does not depend on the machine
function hasDuplicateNested(ids) {
  let steps = 0;
  for (let i = 0; i < ids.length; i++)
    for (let j = i + 1; j < ids.length; j++) {
      steps++;
      if (ids[i] === ids[j]) return { found: true, steps };
    }
  return { found: false, steps };
}

function hasDuplicateSet(ids) {
  let steps = 0;
  const seen = new Set();
  for (const id of ids) {
    steps++;
    if (seen.has(id)) return { found: true, steps };
    seen.add(id);
  }
  return { found: false, steps };
}

for (const n of [10, 100, 1000, 10000]) {
  const ids = Array.from({ length: n }, (_, i) => `ORD-${i}`);   // no duplicates: the worst case
  console.log(`n=${n}`.padEnd(8), "nested:", String(hasDuplicateNested(ids).steps).padStart(9), " set:", hasDuplicateSet(ids).steps);
}
''', 'O(n²) against O(n): count the steps'),
    'measure': run('''
const ids = Array.from({ length: 5000 }, (_, i) => `SKU-${i}`);
const wanted = Array.from({ length: 5000 }, (_, i) => `SKU-${i * 2}`);
const idSet = new Set(ids);

function bench(name, fn, rounds = 5) {
  fn();                                      // warm up so the JIT compiler can optimise
  const times = [];
  for (let r = 0; r < rounds; r++) {
    const start = performance.now();
    fn();
    times.push(performance.now() - start);
  }
  const median = times.toSorted((a, b) => a - b)[Math.floor(rounds / 2)];
  console.log(name.padEnd(14), `${median.toFixed(2)} ms`);   // times depend on the machine, so this page shows x.xx
  return median;
}

const slow = bench("array.includes", () => wanted.filter(id => ids.includes(id)).length);
const fast = bench("set.has", () => wanted.filter(id => idSet.has(id)).length);
console.log("Set is at least 10 times faster:", slow / fast > 10);
''', 'Measure with performance.now, a warm up and the median', replace=TIMING),
    'leak': run('''
// A page object that adds a listener every time it is created and never removes it
const bus = new EventTarget();
let count = 0;
const listeners = () => count;

class LeakyBanner {
  constructor() { bus.addEventListener("cart", () => { this.items = (this.items ?? 0) + 1; count++; }); }
}
for (let i = 0; i < 3; i++) new LeakyBanner();
bus.dispatchEvent(new Event("cart"));
console.log("leaky: one event ran", listeners(), "handlers");

// The fix: tie every listener to an AbortSignal and abort it when the object is done
class Banner {
  #controller = new AbortController();
  constructor() { bus.addEventListener("cart", () => { this.items = (this.items ?? 0) + 1; count++; }, { signal: this.#controller.signal }); }
  destroy() { this.#controller.abort(); }
}
count = 0;
const banner = new Banner();
banner.destroy();
bus.dispatchEvent(new Event("cart"));
console.log("fixed: after destroy, the event still reaches", listeners() - 3, "new handlers");
''', 'A listener leak and the AbortSignal fix'),
    'weak': run('''
// WeakMap keys do not keep objects alive, so extra data dies with the object
const meta = new WeakMap();
let element = { id: "checkout-button" };
meta.set(element, { clicks: 3 });
const ref = new WeakRef(element);

element = null;                                // drop the only strong reference
await new Promise(r => setTimeout(r, 0));      // let the current job finish
globalThis.gc();                               // force garbage collection (needs --expose-gc)
console.log("after gc:", ref.deref());

// A plain Map would keep the object alive for as long as the Map lives
const cache = new Map();
let page = { url: "/cart" };
cache.set(page, "rendered");
page = null;
await new Promise(r => setTimeout(r, 0));
globalThis.gc();
console.log("Map still holds:", [...cache.keys()]);
''', 'WeakMap and WeakRef: memory that cleans itself', play=False, flags=['--expose-gc']),
    'patterns': run('''
// Memoize: cache the result of a pure function
function memoize(fn) {
  const cache = new Map();
  return (...args) => cache.getOrInsertComputed(JSON.stringify(args), () => fn(...args));
}
let calls = 0;
const shippingCost = memoize((pin, kg) => { calls++; return kg * 40 + (pin.startsWith("56") ? 0 : 60); });
console.log(shippingCost("560001", 2), shippingCost("560001", 2), shippingCost("110001", 1), "calls:", calls);

// Pipe: build a function out of small steps
const pipe = (...steps) => input => steps.reduce((value, step) => step(value), input);
const slug = pipe(s => s.trim(), s => s.toLowerCase(), s => s.replace(/[^a-z0-9]+/g, "-"), s => s.replace(/^-|-$/g, ""));
console.log(slug("  Summer Sale: 50% OFF!  "));

// Strategy: swap behaviour without if and else chains
const discounts = {
  none: total => total,
  percent10: total => total * 0.9,
  flat100: total => Math.max(0, total - 100),
};
for (const name of Object.keys(discounts)) console.log(name.padEnd(9), discounts[name](800));

// Observer: subscribers are told about changes
function createStore(state) {
  const subscribers = new Set();
  return {
    get: () => state,
    set(patch) { state = { ...state, ...patch }; subscribers.forEach(fn => fn(state)); },
    subscribe(fn) { subscribers.add(fn); return () => subscribers.delete(fn); },
  };
}
const store = createStore({ items: 0 });
const stop = store.subscribe(s => console.log("badge shows", s.items));
store.set({ items: 1 });
stop();
store.set({ items: 2 });
console.log("final state", store.get());
''', 'Memoize, pipe, strategy and observer'),
    'builder': run('''
// Test data builder: sensible defaults, change only what the test is about
class UserBuilder {
  #user = { name: "Test User", email: "test.user@example.test", role: "customer", verified: true, country: "IN" };
  static aUser() { return new UserBuilder(); }
  withRole(role) { this.#user.role = role; return this; }
  unverified() { this.#user.verified = false; return this; }
  from(country) { this.#user.country = country; return this; }
  build() { return structuredClone(this.#user); }
}

const admin = UserBuilder.aUser().withRole("admin").build();
const newUser = UserBuilder.aUser().unverified().from("DE").build();
console.log(admin);
console.log(newUser);

// Factory with a counter so every record is unique, which keeps parallel tests apart
let seq = 0;
const makeOrder = (overrides = {}) => ({ id: `ORD-${++seq}`, items: [{ sku: "PEN", qty: 1 }], status: "new", ...overrides });
console.log(makeOrder(), makeOrder({ status: "paid" }).id);
''', 'Builder and factory for test data'),
    'workers': run('''
import { Worker } from "node:worker_threads";

// The worker counts primes in its own range on its own thread
const workerCode = `
  const { parentPort, workerData } = require("node:worker_threads");
  const { from, to } = workerData;
  let count = 0;
  for (let n = Math.max(2, from); n < to; n++) {
    let prime = true;
    for (let d = 2; d * d <= n; d++) if (n % d === 0) { prime = false; break; }
    if (prime) count++;
  }
  parentPort.postMessage({ from, to, count });
`;

const runWorker = range => new Promise((resolve, reject) => {
  const worker = new Worker(workerCode, { eval: true, workerData: range });
  worker.once("message", resolve);
  worker.once("error", reject);
});

const size = 500_000, parts = 4;
const ranges = Array.from({ length: parts }, (_, i) => ({ from: i * size / parts, to: (i + 1) * size / parts }));
const results = await Promise.all(ranges.map(runWorker));
for (const r of results) console.log(`${r.from}..${r.to}: ${r.count} primes`);
console.log("total:", results.reduce((sum, r) => sum + r.count, 0));
''', 'Split heavy work across worker threads', play=False),
    'web-worker': show('''
// main.js in the browser: keep the page responsive while a big CSV is parsed
const worker = new Worker(new URL("./parse-worker.js", import.meta.url), { type: "module" });
worker.postMessage(file);                          // file from an <input type="file">
worker.onmessage = ({ data }) => renderTable(data.rows);

// parse-worker.js
self.onmessage = async ({ data: file }) => {
  const text = await file.text();
  const rows = text.split("\\n").map(line => line.split(","));
  self.postMessage({ rows });
};
''', 'Web Workers in the browser', note='Runs in a browser'),
    'xss': dom('''
<h2>Reviews</h2>
<div id="unsafe"></div>
<div id="safe"></div>
''', '''
// A review typed by a user, coming back from the API
const review = 'Great pen <img src="x" onerror="alert(document.cookie)">';

// Unsafe: innerHTML turns the text into real elements, including the attacker's handler
document.querySelector("#unsafe").innerHTML = review;
console.log("unsafe has an onerror image:", document.querySelector("#unsafe img[onerror]") !== null);

// Safe: textContent shows the text exactly as typed
document.querySelector("#safe").textContent = review;
console.log("safe has an onerror image:", document.querySelector("#safe img") !== null);
console.log("safe shows:", document.querySelector("#safe").textContent);

// A QA check you can run on any page: no inline handlers in user content
const risky = [...document.querySelectorAll("[onerror], [onload], [onclick]")].map(el => el.closest("[id]").id);
console.log("risky containers:", risky);
''', 'Cross site scripting: innerHTML against textContent'),
    'pollution': run('''
// A naive deep merge, often written for config files and API bodies
function merge(target, source) {
  for (const key in source) {
    if (typeof source[key] === "object" && source[key] !== null) {
      target[key] ??= {};
      merge(target[key], source[key]);
    } else target[key] = source[key];
  }
  return target;
}

const body = JSON.parse('{"theme": "dark", "__proto__": {"isAdmin": true}}');   // sent by an attacker
merge({}, body);
console.log("every object is now admin:", ({}).isAdmin);
delete Object.prototype.isAdmin;                                                // undo for the rest of the demo

// The fix: skip dangerous keys, or use objects without a prototype
const BLOCKED = new Set(["__proto__", "constructor", "prototype"]);
function safeMerge(target, source) {
  for (const key of Object.keys(source)) {
    if (BLOCKED.has(key)) continue;
    const value = source[key];
    target[key] = typeof value === "object" && value !== null ? safeMerge(target[key] ?? Object.create(null), value) : value;
  }
  return target;
}
const settings = safeMerge({}, body);
console.log("after safeMerge:", ({}).isAdmin, settings.theme);
''', 'Prototype pollution and how to block it'),
    'property': run('''
// A tiny property based tester: random inputs from a fixed seed, so a failure can be replayed
function mulberry32(seed) {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function check(name, gen, property, { runs = 200, seed = 42 } = {}) {
  const rand = mulberry32(seed);
  for (let i = 0; i < runs; i++) {
    const input = gen(rand);
    if (!property(input)) return console.log(`✗ ${name} failed on run ${i + 1} with`, input);
  }
  console.log(`✓ ${name} held for ${runs} inputs`);
}

// The code under test: split a bill into n shares in paise, so no money is lost
const splitBuggy = (paise, n) => Array(n).fill(Math.round(paise / n));
const splitFixed = (paise, n) => Array.from({ length: n }, (_, i) => Math.floor(paise / n) + (i < paise % n ? 1 : 0));

const bill = rand => ({ paise: Math.floor(rand() * 100000), n: 1 + Math.floor(rand() * 6) });
const sumIsKept = split => ({ paise, n }) => split(paise, n).reduce((a, b) => a + b, 0) === paise;
const fair = ({ paise, n }) => { const s = splitFixed(paise, n); return Math.max(...s) - Math.min(...s) <= 1; };

check("buggy split keeps the total", bill, sumIsKept(splitBuggy));
check("fixed split keeps the total", bill, sumIsKept(splitFixed));
check("fixed split is fair", bill, fair);
''', 'Property based testing from scratch'),
    'mutation': run('''
// The code under test
const source = "total => total >= 499";

// Mutants: small changes a careless edit could make
const mutants = [
  ["original", source],
  [">= to >", source.replace(">=", ">")],
  [">= to <=", source.replace(">=", "<=")],
  ["499 to 500", source.replace("499", "500")],
  ["499 to 498", source.replace("499", "498")],
];

// Two test suites for freeShipping(total)
const weakSuite = [[1000, true], [10, false]];
const strongSuite = [[1000, true], [10, false], [499, true], [498.99, false]];

function score(suite) {
  let killed = 0;
  for (const [name, code] of mutants.slice(1)) {
    const fn = eval(code);
    const caught = suite.some(([input, want]) => fn(input) !== want);
    if (caught) killed++;
    else console.log("  survived:", name);
  }
  return `${killed} of ${mutants.length - 1} mutants killed`;
}

console.log("weak suite:", score(weakSuite));
console.log("strong suite:", score(strongSuite));
''', 'Mutation testing: do the tests notice a change'),
    'flaky': test({
        'package.json': pkg('flaky', 'module'),
        'src/cart.js': '''
export const cart = { items: [], coupon: null };
export const add = (sku, price) => cart.items.push({ sku, price });
export const total = () => {
  const sum = cart.items.reduce((s, i) => s + i.price, 0);
  return cart.coupon === "SAVE10" ? sum * 0.9 : sum;
};
''',
        'test/cart.test.js': '''
import { test } from "node:test";
import assert from "node:assert/strict";
import { cart, add, total } from "../src/cart.js";

test("adds items", () => {
  add("PEN", 100);
  add("BOOK", 400);
  assert.equal(total(), 500);
});

test("applies the coupon", () => {
  cart.coupon = "SAVE10";          // relies on the items left over by the first test
  assert.equal(total(), 450);
});
''',
        'check.sh': '''
say() { printf '\\n$ %s\\n' "$*"; }
say "node --test   # the whole file, in order"
node --test --no-warnings --test-reporter=spec | grep -E '^(✔|✖)'
say "node --test --test-name-pattern=coupon   # the same test on its own"
node --test --no-warnings --test-reporter=spec --test-name-pattern=coupon | grep -E '^(✔|✖)|actual:|expected:'
true
''',
    }, 'sh check.sh', 'A test that passes only in order', show=['test/cart.test.js', 'check.sh'], shown_cmd='sh check.sh',
        replace=[(r' \([\d.]+ms\)', '')]),
    'shards': run('''
// Timings from the last CI run, read from the JUnit report
const timings = {
  "checkout.spec": 310, "search.spec": 95, "login.spec": 60, "cart.spec": 120, "profile.spec": 45,
  "orders.spec": 180, "payments.spec": 240, "admin.spec": 70, "wishlist.spec": 40, "returns.spec": 150,
};
const files = Object.keys(timings).sort();

// Naive: spread files by position, which is what --shard style splitting does
function byPosition(n) {
  const shards = Array.from({ length: n }, () => []);
  files.forEach((f, i) => shards[i % n].push(f));
  return shards;
}

// Balanced: longest file first, always into the shard with the least work so far
function byDuration(n) {
  const shards = Array.from({ length: n }, () => ({ files: [], total: 0 }));
  for (const f of files.toSorted((a, b) => timings[b] - timings[a])) {
    const lightest = shards.reduce((min, s) => (s.total < min.total ? s : min));
    lightest.files.push(f);
    lightest.total += timings[f];
  }
  return shards.map(s => s.files);
}

const report = (name, shards) => {
  const totals = shards.map(s => s.reduce((sum, f) => sum + timings[f], 0));
  console.log(name.padEnd(12), "shard seconds:", totals.join(" / "), "| CI waits", Math.max(...totals), "s");
};
report("by position", byPosition(3));
report("by duration", byDuration(3));
console.log(byDuration(3).map((s, i) => `shard ${i + 1}: ${s.join(", ")}`).join("\\n"));
''', 'Balance CI shards with last run timings'),
}

PARTS = [
    part('performance', '⚡', 'Performance: count first, then measure', '''
<p>Most slow JavaScript is slow because of the algorithm, not the engine. A loop inside a loop over the same list does about <span class="eq">n²</span> ÷ 2 steps, while a <code>Set</code> lookup does about <span class="eq">n</span>. Count steps to compare ideas, and measure time only to confirm.</p>
[[bigo]]
<p>When you do measure, warm the code up first so the JIT compiler can optimise it, run it several times and take the median. One run on a laptop with a browser open is noise.</p>
[[measure]]
<div class="tip">In the browser, the Performance panel of DevTools shows long tasks, layout work and memory over time. Lighthouse and the Core Web Vitals (LCP, INP and CLS) are what users actually feel, and Playwright can read them with <code>page.evaluate</code> during a test.</div>
''', qa=['Playwright', 'Lighthouse'], qa_why='Performance checks in CI catch slow pages and slow APIs before users do.',
        kw=['performance', 'Big O', 'O(n)', 'O(n²)', 'performance.now', 'benchmark', 'median', 'warm up', 'JIT', 'Core Web Vitals', 'LCP', 'INP', 'CLS', 'Lighthouse']),
    part('memory', '🧠', 'Memory: leaks and weak references', '''
<p>JavaScript frees memory that nothing can reach any more. A leak happens when something you forgot still points at old data: a listener that was never removed, a cache that only grows, or a timer that keeps running. In a long test run or a single page app that stays open all day, small leaks add up.</p>
[[leak]]
<p><code>WeakMap</code>, <code>WeakSet</code> and <code>WeakRef</code> hold objects without keeping them alive. Use them to attach extra data to objects you do not own, such as DOM nodes.</p>
[[weak]]
<div class="qa-box">To test for a leak, repeat an action many times (open and close a dialog 50 times), force garbage collection and compare heap snapshots. Playwright can open a CDP session in Chromium and call <code>HeapProfiler.collectGarbage</code> and <code>Performance.getMetrics</code>.</div>
''', qa=['Playwright'], qa_why='Leaks show up in long test runs and soak tests, and testers are often the first to see them.',
        kw=['memory leak', 'garbage collection', 'event listener leak', 'AbortController', 'AbortSignal', 'WeakMap', 'WeakRef', 'WeakSet', 'FinalizationRegistry', 'heap snapshot', 'CDP']),
    part('patterns', '🧩', 'Patterns experts reach for', '''
<p>A pattern is a known shape for a common problem. These four appear in application code and in test frameworks alike.</p>
[[patterns]]
<p>For tests, the two most useful patterns are the <b>page object</b> from chapter 8 and the <b>test data builder</b>. A builder gives every field a valid default, so each test states only what it is about.</p>
[[builder]]
<div class="tip">Unique values from a counter or <code>crypto.randomUUID()</code> keep tests that run in parallel from clashing over the same email or order id.</div>
''', qa=True, qa_why='Builders, factories and page objects make large test suites readable and safe to run in parallel.',
        kw=['design patterns', 'memoize', 'pipe', 'compose', 'strategy pattern', 'observer pattern', 'pub sub', 'builder pattern', 'test data builder', 'factory', 'page object']),
    part('workers', '🧵', 'Workers: real parallel work', '''
<p>JavaScript runs your code on one thread, so a long calculation blocks everything else. <b>Worker threads</b> in Node.js and <b>Web Workers</b> in the browser run code on separate threads and talk to the main thread with messages.</p>
[[workers]]
[[web-worker]]
<div class="note">Use workers for heavy CPU work such as parsing, hashing, image work or big calculations. For waiting on the network or disk, plain <code>async</code> code is already enough. Test runners use the same idea: Jest, Vitest and Playwright run test files in parallel workers.</div>
''', qa=['Playwright', 'Jest', 'Vitest'], qa_why='Test runners use workers to run files in parallel, which is why tests must not share state.',
        kw=['worker_threads', 'Web Worker', 'Worker', 'postMessage', 'workerData', 'parallel', 'CPU bound', 'main thread', 'test workers']),
    part('security', '🔐', 'Security every JavaScript developer should test', '''
<p><b>Cross site scripting</b> (XSS) happens when user text is turned into HTML. The safe defaults are <code>textContent</code>, framework templates that escape by default, and a Content Security Policy header that blocks inline scripts.</p>
[[xss]]
<p><b>Prototype pollution</b> happens when code copies keys from untrusted JSON into objects. The key <code>__proto__</code> reaches the shared prototype and changes every object in the program.</p>
[[pollution]]
<div class="tw"><table class="jt"><tr><th>Risk</th><th>What to check</th></tr>
<tr><td>XSS</td><td>Type <code>&lt;img src=x onerror=alert(1)&gt;</code> into every field and check it shows as text</td></tr>
<tr><td>Secrets</td><td>No API keys in the browser bundle or in git. Read them from environment variables</td></tr>
<tr><td>eval</td><td>No <code>eval</code> or <code>new Function</code> on user input</td></tr>
<tr><td>Dependencies</td><td>Run <code>npm audit</code>, keep a lock file and use <code>npm ci</code> in CI</td></tr>
<tr><td>Auth</td><td>Every API checks the token and the role, not just the UI (chapter 14)</td></tr>
<tr><td>Cookies</td><td>Session cookies use HttpOnly, Secure and SameSite</td></tr>
</table></div>
''', qa=True, qa_why='Security checks such as XSS payloads and auth rules belong in every regression suite.',
        kw=['security', 'XSS', 'cross site scripting', 'innerHTML', 'textContent', 'Content Security Policy', 'CSP', 'prototype pollution', '__proto__', 'eval', 'npm audit', 'secrets', 'OWASP']),
    part('quality', '🎯', 'Test quality: properties, mutants and flaky tests', '''
<p>Example based tests check the inputs you thought of. <b>Property based testing</b> generates hundreds of inputs and checks a rule that must always hold. Libraries such as fast-check also shrink a failure to the smallest input. The seed makes every failure repeatable.</p>
[[property]]
<p>Coverage tells you which lines ran, not whether a test would notice a bug. <b>Mutation testing</b> changes the code on purpose and checks that some test fails. Stryker does this for JavaScript and TypeScript projects.</p>
[[mutation]]
<p>A <b>flaky test</b> passes and fails without any change to the code. The common causes are shared state between tests, fixed sleeps instead of waiting for a condition, test order, time and time zones, and real network calls. Running a test on its own is the quickest way to find an order problem.</p>
[[flaky]]
<div class="tip">The fix for the test above is to reset the cart in a <code>beforeEach</code> and let each test add its own items. Track flaky tests in a list, fix them quickly, and never leave retries on to hide them.</div>
''', qa=True, qa_why='These techniques measure how good a test suite really is, which is the core skill of a senior tester.',
        kw=['property based testing', 'fast-check', 'seed', 'shrinking', 'mutation testing', 'Stryker', 'mutation score', 'flaky test', 'test isolation', 'beforeEach', 'test order']),
    part('scenario', '🎬', 'Real world scenario: a faster CI pipeline', '''
<div class="scenario"><b>The situation</b>The end to end suite runs on three CI machines, but one machine always finishes long after the others. You have the timings from the last run.</div>
[[shards]]
<p>Splitting by position put the slow checkout and payments files on the same machine. Sorting by duration and filling the lightest shard first cuts the wait by more than three minutes with the same three machines. This greedy method is called <b>longest processing time first</b>, and it is what tools such as Knapsack Pro and CircleCI test splitting do.</p>
''', qa=['Playwright', 'CI'], kw=['CI', 'sharding', 'test splitting', 'parallel', 'JUnit timings', 'longest processing time', 'pipeline speed']),
]

INFO = {'title': 'Habits of an expert', 'panels': [
    panel([['e', '⚡'], ['t', 'O(n²) → O(n)', {'b': 1}]], 'Count, then measure', 'Pick the right algorithm first.', 'Measure with a warm up and a median.'),
    panel([['e', '🧹'], ['t', '{ signal }', {'b': 1}]], 'Clean up', 'Remove listeners and timers.', 'Leaks add up in long runs.'),
    panel([['e', '🔐'], ['t', 'textContent', {'b': 1}]], 'Treat input as text', 'Never as HTML or code.', 'Block __proto__ keys.'),
    panel([['e', '🎯'], ['t', 'mutants killed', {'b': 1}]], 'Test the tests', 'Properties, mutants, isolation.', 'Coverage alone is not enough.')],
    'remember': 'Good code is fast because of its design, cleans up after itself, treats user input as data, and comes with tests that would fail if it broke.'}

REAL = [
    ['🛒', 'An online shop', 'Replaced a nested loop that matched cart items to offers with a Map and cut checkout time from 2 seconds to 40 ms on large carts.'],
    ['📊', 'A dashboard team', 'Found a listener leak after QA kept the app open for a full day and memory grew past 2 GB. AbortController fixed it.'],
    ['🏦', 'A payments company', 'Added property based tests to its rounding code and found a split that lost one paisa, before it reached real customers.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers expert topics: performance, memory, design patterns, workers, security, and how to judge the quality of your tests.',
        'यह अध्याय expert topics सिखाता है: performance, memory, design patterns, workers, security, और tests की quality कैसे परखें।',
        'ಈ ಅಧ್ಯಾಯ expert topics ಒಳಗೊಂಡಿದೆ: performance, memory, design patterns, workers, security ಮತ್ತು tests ನ quality.',
        'ଏହି ଅଧ୍ୟାୟ expert topics ଶିଖାଏ: performance, memory, design patterns, workers, security ଓ tests ର quality।',
        'يغطي هذا الفصل موضوعات متقدمة: الأداء والذاكرة وأنماط التصميم والعمال والأمان وكيفية الحكم على جودة الاختبارات.',
        'Dieses Kapitel behandelt Expertenthemen: Leistung, Speicher, Entwurfsmuster, Worker, Sicherheit und die Qualität von Tests.'),
    say('performance', 'Performance', 'Count the steps to compare algorithms. A Set lookup grows with n, a nested loop with n squared. Measure with a warm up and a median.',
        'Algorithms की तुलना के लिए steps गिनें। Set lookup n के साथ बढ़ता है, nested loop n squared के साथ। Warm up और median से मापें।',
        'Algorithms ಹೋಲಿಸಲು steps ಎಣಿಸಿ. Set lookup n ಜೊತೆ, nested loop n squared ಜೊತೆ ಬೆಳೆಯುತ್ತದೆ.',
        'Algorithms ତୁଳନା ପାଇଁ steps ଗଣନ୍ତୁ। Set lookup n ସହ, nested loop n squared ସହ ବଢ଼େ।',
        'عُدّ الخطوات لتقارن الخوارزميات. يزداد البحث في Set مع n والحلقة المتداخلة مع مربع n. قِس بعد إحماء وخذ الوسيط.',
        'Zähle Schritte, um Algorithmen zu vergleichen. Ein Set wächst mit n, eine verschachtelte Schleife mit n zum Quadrat.'),
    say('memory', 'Memory', 'A leak is something you forgot that still points at old data. Remove listeners with an AbortSignal and use WeakMap for extra data.',
        'Leak वह चीज़ है जो भूली हुई है पर पुराने data को पकड़े है। AbortSignal से listeners हटाएं और WeakMap इस्तेमाल करें।',
        'Leak ಎಂದರೆ ಮರೆತ ವಸ್ತು ಹಳೆಯ data ಹಿಡಿದಿರುವುದು. AbortSignal ನಿಂದ listeners ತೆಗೆದು WeakMap ಬಳಸಿ.',
        'Leak ହେଉଛି ଭୁଲିଯାଇଥିବା ଜିନିଷ ଯାହା ପୁରୁଣା data ଧରିଥାଏ। AbortSignal ରେ listeners ହଟାନ୍ତୁ।',
        'التسرب شيء نسيته ما زال يشير إلى بيانات قديمة. أزل المستمعين بـ AbortSignal واستخدم WeakMap للبيانات الإضافية.',
        'Ein Leck ist etwas Vergessenes, das alte Daten festhält. Entferne Listener mit AbortSignal und nutze WeakMap.'),
    say('patterns', 'Patterns', 'Memoize caches results, pipe joins small steps, strategy swaps behaviour, observer tells subscribers about changes, and a builder makes test data.',
        'Memoize results cache करता है, pipe छोटे steps जोड़ता है, strategy behaviour बदलता है, observer बदलाव बताता है, builder test data बनाता है।',
        'Memoize results cache ಮಾಡುತ್ತದೆ, pipe steps ಜೋಡಿಸುತ್ತದೆ, observer ಬದಲಾವಣೆ ತಿಳಿಸುತ್ತದೆ, builder test data ಮಾಡುತ್ತದೆ.',
        'Memoize results cache କରେ, pipe steps ଯୋଡ଼େ, observer ପରିବର୍ତ୍ତନ ଜଣାଏ, builder test data ତିଆରି କରେ।',
        'يخزن memoize النتائج، ويربط pipe خطوات صغيرة، ويبدل strategy السلوك، ويبلغ observer المشتركين، ويصنع builder بيانات الاختبار.',
        'Memoize speichert Ergebnisse, pipe verbindet Schritte, Observer meldet Änderungen, ein Builder erzeugt Testdaten.'),
    say('workers', 'Workers', 'Workers run code on separate threads and talk with messages. Use them for heavy CPU work, not for waiting on the network.',
        'Workers अलग threads पर code चलाते हैं और messages से बात करते हैं। इन्हें भारी CPU काम के लिए इस्तेमाल करें।',
        'Workers ಬೇರೆ threads ನಲ್ಲಿ code ಓಡಿಸಿ messages ಮೂಲಕ ಮಾತನಾಡುತ್ತವೆ. ಭಾರೀ CPU ಕೆಲಸಕ್ಕೆ ಬಳಸಿ.',
        'Workers ଅଲଗା threads ରେ code ଚଲାନ୍ତି ଓ messages ରେ କଥା ହୁଅନ୍ତି। ଭାରୀ CPU କାମ ପାଇଁ ବ୍ୟବହାର କରନ୍ତୁ।',
        'تشغّل العمال الشيفرة في خيوط منفصلة وتتواصل بالرسائل. استخدمها للعمل الحسابي الثقيل لا لانتظار الشبكة.',
        'Worker führen Code in eigenen Threads aus und sprechen über Nachrichten. Nutze sie für schwere Rechenarbeit.'),
    say('security', 'Security', 'Show user text with textContent, never innerHTML. Block keys such as proto when you merge objects, and keep secrets out of the browser.',
        'User text को textContent से दिखाएं, innerHTML से नहीं। Objects merge करते समय proto जैसी keys रोकें और secrets browser से दूर रखें।',
        'User text ಅನ್ನು textContent ನಿಂದ ತೋರಿಸಿ, innerHTML ಬೇಡ. Merge ಮಾಡುವಾಗ proto keys ತಡೆಯಿರಿ.',
        'User text କୁ textContent ରେ ଦେଖାନ୍ତୁ, innerHTML ନୁହେଁ। Merge ବେଳେ proto keys ଅଟକାନ୍ତୁ।',
        'اعرض نص المستخدم بـ textContent لا بـ innerHTML، وامنع مفاتيح مثل proto عند الدمج، وأبعد الأسرار عن المتصفح.',
        'Zeige Nutzertext mit textContent, nie mit innerHTML. Blockiere Schlüssel wie proto beim Zusammenführen.'),
    say('quality', 'Test quality', 'Property based tests check a rule on many inputs, mutation testing checks that tests notice changes, and running a test alone exposes order problems.',
        'Property based tests कई inputs पर नियम जांचते हैं, mutation testing देखता है कि tests बदलाव पकड़ें, और अकेले test चलाने से order की समस्या दिखती है।',
        'Property based tests ಅನೇಕ inputs ನಲ್ಲಿ ನಿಯಮ ಪರಿಶೀಲಿಸುತ್ತವೆ, mutation testing ಬದಲಾವಣೆ ಹಿಡಿಯುತ್ತದೆಯೇ ನೋಡುತ್ತದೆ.',
        'Property based tests ଅନେକ inputs ରେ ନିୟମ ଯାଞ୍ଚ କରେ, mutation testing ପରିବର୍ତ୍ତନ ଧରେ କି ନାହିଁ ଦେଖେ।',
        'تفحص اختبارات الخصائص قاعدة على مدخلات كثيرة، ويتأكد اختبار الطفرات أن الاختبارات تلاحظ التغيير، ويكشف تشغيل الاختبار وحده مشاكل الترتيب.',
        'Eigenschaftstests prüfen eine Regel mit vielen Eingaben, Mutationstests prüfen, ob Tests Änderungen bemerken.'),
    say('scenario', 'Scenario', 'Use last run timings, sort files longest first, and always add the next file to the lightest shard. The pipeline finishes much sooner.',
        'पिछले run की timings लें, files को सबसे लंबी पहले sort करें और अगली file सबसे हल्के shard में डालें।',
        'ಹಿಂದಿನ run timings ಬಳಸಿ, ಉದ್ದದ files ಮೊದಲು sort ಮಾಡಿ, ಹಗುರ shard ಗೆ ಸೇರಿಸಿ.',
        'ପୂର୍ବ run timings ନିଅନ୍ତୁ, ଲମ୍ବା files ପ୍ରଥମେ sort କରି ହାଲୁକା shard ରେ ଯୋଡ଼ନ୍ତୁ।',
        'استخدم توقيتات التشغيل السابق، ورتب الملفات من الأطول، وأضف كل ملف إلى أخف جزء. ينتهي خط التكامل أسرع بكثير.',
        'Nutze die Zeiten des letzten Laufs, sortiere die längsten Dateien zuerst und fülle immer den leichtesten Shard.'),
    say('practice', 'Hands-on', 'Practise a memoize helper, a debounce helper, escaping HTML safely, and balancing test files across CI shards.',
        'Memoize helper, debounce helper, HTML को सुरक्षित escape करना और CI shards में test files बांटने का अभ्यास करें।',
        'Memoize, debounce, HTML ಸುರಕ್ಷಿತ escape ಮತ್ತು CI shards ನಲ್ಲಿ test files ಹಂಚುವ ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Memoize, debounce, HTML ସୁରକ୍ଷିତ escape ଓ CI shards ରେ test files ବାଣ୍ଟିବା ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على دالة memoize ودالة debounce وتهريب HTML بأمان وتوزيع ملفات الاختبار على أجزاء CI.',
        'Übe memoize, debounce, sicheres HTML-Escaping und das Verteilen von Testdateien auf CI-Shards.'),
]

QUIZ = [
    quiz('e', 'Which is the safe way to show text a user typed?', ['element.textContent = text', 'element.innerHTML = text', 'document.write(text)', 'eval(text)'], 0, 'Text, not HTML.', 'textContent never turns the text into elements or scripts.'),
    quiz('e', 'Why take the median of several runs in a benchmark?', ['One slow run caused by the machine does not skew the result', 'It is always the fastest', 'It removes the need for a warm up', 'It counts steps'], 0, 'Noise.', 'The median ignores outliers such as a garbage collection pause.'),
    quiz('e', 'What is a flaky test?', ['A test that passes and fails without any code change', 'A test that always fails', 'A skipped test', 'A slow test'], 0, 'Unreliable.', 'Flaky tests teach people to ignore red builds, so fix them quickly.'),
    quiz('m', 'Searching an array of n items for each of n other items is roughly?', ['O(n²)', 'O(n)', 'O(log n)', 'O(1)'], 0, 'A loop in a loop.', 'Using a Set makes each lookup O(1) on average, so the total becomes O(n).'),
    quiz('m', 'What does passing { signal } to addEventListener let you do?', ['Remove the listener by aborting the controller', 'Make the listener run once', 'Make it passive', 'Run it in a worker'], 0, 'AbortController.', 'One abort() call can remove many listeners at once.'),
    quiz('m', 'What is a test data builder for?', ['Creating valid objects with defaults so each test changes only what it needs', 'Building the app', 'Running tests in parallel', 'Writing reports'], 0, 'Defaults.', 'Tests become shorter and stay valid when new required fields are added.'),
    quiz('m', 'When are worker threads the right tool?', ['Heavy CPU work such as parsing or hashing', 'Waiting for an HTTP response', 'Reading one small file', 'Adding two numbers'], 0, 'CPU bound.', 'Waiting on I/O is already non blocking with async code.'),
    quiz('h', 'How does JSON with a "__proto__" key pollute every object?', ['A naive merge assigns into the shared Object.prototype', 'JSON.parse runs code', 'It deletes properties', 'It changes Array.prototype only'], 0, 'target["__proto__"] is the prototype.', 'Skip that key or use Object.create(null) objects.'),
    quiz('h', 'Your tests have 100% line coverage but a mutant survives. What does that mean?', ['Some line ran but no test checked its result closely enough', 'Coverage is broken', 'The mutant is invalid', 'Tests are too slow'], 0, 'Ran is not checked.', 'Add a test at the boundary that the mutant changed.'),
    quiz('h', 'Why should a property based test use a fixed or printed seed?', ['So a failing input can be replayed exactly', 'To make it faster', 'To avoid shrinking', 'Seeds are required by JavaScript'], 0, 'Repeatable.', 'fast-check prints the seed and path of every failure for this reason.'),
    quiz('x', 'A test passes in the full file but fails when run alone. The most likely cause?', ['It depends on state left by an earlier test', 'The runner is broken', 'The machine is slow', 'A typo in the name'], 0, 'Order dependency.', 'Reset state in beforeEach so each test sets up what it needs.'),
    quiz('x', 'Why does a WeakMap keyed by a DOM node not leak when the node is removed?', ['Weak keys do not keep the node alive, so the entry goes when the node is collected', 'WeakMap clears itself every second', 'DOM nodes cannot be keys', 'It copies the node'], 0, 'Weak reference.', 'A plain Map would keep the node and its data in memory forever.'),
]

CALC = [
    calc('e', 'A nested duplicate check on 1000 ids with no duplicates. How many comparisons? Use n × (n − 1) ÷ 2.', '499500', 'Each pair once.', ['<span class="eq">1000 × 999 ÷ 2 = 499,500</span>']),
    calc('e', 'Benchmark runs took 12, 9, 30, 10 and 11 ms. What is the median?', '11', 'Sort them first.', ['Sorted: 9, 10, 11, 12, 30.', 'The middle value is 11.']),
    calc('m', 'With a Set, the same 1000 ids need how many lookups?', '1000', 'One per id.', ['<span class="eq">n = 1000</span>']),
    calc('m', 'A suite kills 18 of 24 mutants. What is the mutation score in percent?', '75', 'Killed over total.', ['<span class="eq">18 ÷ 24 × 100 = 75</span>']),
    calc('m', 'A test fails 3 times in 200 CI runs. What is its flake rate in percent?', '1.5', 'Failures over runs.', ['<span class="eq">3 ÷ 200 × 100 = 1.5</span>']),
    calc('h', '₹1000.00 is split between 3 people in paise so nothing is lost. What is the largest share, in paise?', '33334', 'Floor, then hand out the remainder.', ['<span class="eq">100000 ÷ 3 = 33333 remainder 1</span>', 'One person gets one extra paisa: 33334.']),
    calc('h', 'Test files take 310, 240, 180, 150 and 120 seconds. Longest first into 2 shards, always into the lighter one. How long does CI wait, in seconds?', '540', 'Track both totals.', ['310 goes to A, 240 to B.', '180 goes to B (420), 150 to A (460), 120 to B (540).', 'Totals 460 and 540. CI waits for the larger.']),
    calc('x', 'The scenario pipeline waits 645 s by position and 445 s by duration. How many seconds does balancing save on every run?', '200', 'Difference.', ['<span class="eq">645 − 445 = 200</span>']),
]

EX = [
    ex('memo', 'e', 'Memoize a pure function', '<p>Write <code>memoize(fn)</code> that returns a function which calls <code>fn</code> only once for each set of arguments and returns the cached result after that. Treat arguments as equal when <code>JSON.stringify</code> of them is equal.</p>',
       'function memoize(fn) {\n  \n}\n',
       [('(() => { let calls = 0; const sq = memoize(n => { calls++; return n * n; }); return [sq(4), sq(4), sq(5), calls]; })()', [16, 16, 25, 2]),
        ('(() => { let calls = 0; const add = memoize((a, b) => { calls++; return a + b; }); add(1, 2); add(2, 1); add(1, 2); return calls; })()', 2)],
       'function memoize(fn) {\n  const cache = new Map();\n  return (...args) => {\n    const key = JSON.stringify(args);\n    if (!cache.has(key)) cache.set(key, fn(...args));\n    return cache.get(key);\n  };\n}',
       hint='Use <code>JSON.stringify(args)</code> as the key of a <code>Map</code>.', why='Memoize only pure functions. A function that reads the clock or the network would return stale results.'),
    ex('debounce', 'm', 'Debounce a search box', '<p>Write <code>debounce(fn, ms)</code>. The returned function waits <code>ms</code> milliseconds after the last call and then calls <code>fn</code> once with the latest arguments. Earlier calls inside the wait are dropped.</p>',
       'function debounce(fn, ms) {\n  \n}\n',
       [('(async () => { const seen = []; const search = debounce(q => seen.push(q), 30); search("p"); search("pe"); search("pen"); await new Promise(r => setTimeout(r, 80)); search("book"); await new Promise(r => setTimeout(r, 80)); return seen; })()', ['pen', 'book'])],
       'function debounce(fn, ms) {\n  let timer;\n  return (...args) => {\n    clearTimeout(timer);\n    timer = setTimeout(() => fn(...args), ms);\n  };\n}',
       hint='Clear the previous timer on every call, then start a new one.', why='Testers meet debounce often: a search box that waits before calling the API needs a wait in the test, never a fixed sleep shorter than the debounce.'),
    ex('escape', 'h', 'Escape HTML', '<p>Write <code>escapeHtml(text)</code> that replaces <code>&amp;</code>, <code>&lt;</code>, <code>&gt;</code>, <code>"</code> and <code>\'</code> with <code>&amp;amp;</code>, <code>&amp;lt;</code>, <code>&amp;gt;</code>, <code>&amp;quot;</code> and <code>&amp;#39;</code>, so the text is safe inside HTML and attributes.</p>',
       'function escapeHtml(text) {\n  \n}\n',
       [('escapeHtml("<img src=x onerror=alert(1)>")', '&lt;img src=x onerror=alert(1)&gt;'), ('escapeHtml(\'Tom & "Jerry" \\\'s\')', 'Tom &amp; &quot;Jerry&quot; &#39;s'), ('escapeHtml("&lt;")', '&amp;lt;'), ('escapeHtml("plain")', 'plain')],
       'function escapeHtml(text) {\n  const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", \'"\': "&quot;", "\'": "&#39;" };\n  return text.replace(/[&<>"\']/g, ch => map[ch]);\n}',
       hint='One regular expression with a lookup object. Replace every character in a single pass so <code>&amp;</code> is not escaped twice.', why='Replacing one character at a time in separate passes can escape the ampersands you just added.'),
    ex('shards', 'x', 'Balance test shards', '<p>Write <code>balance(timings, n)</code>. <code>timings</code> maps file names to seconds. Sort files by time, longest first (ties by name A to Z), and put each one into the shard with the smallest total so far (the lowest index on a tie). Return an array of <code>n</code> arrays of file names.</p>',
       'function balance(timings, n) {\n  \n}\n',
       [('balance({ a: 5, b: 4, c: 3, d: 3, e: 1 }, 2)', [['a', 'd'], ['b', 'c', 'e']]), ('balance({ x: 10 }, 3)', [['x'], [], []]), ('balance({ p: 2, q: 2 }, 2)', [['p'], ['q']])],
       'function balance(timings, n) {\n  const shards = Array.from({ length: n }, () => ({ files: [], total: 0 }));\n  const files = Object.keys(timings).sort((a, b) => timings[b] - timings[a] || a.localeCompare(b));\n  for (const f of files) {\n    let best = shards[0];\n    for (const s of shards) if (s.total < best.total) best = s;\n    best.files.push(f);\n    best.total += timings[f];\n  }\n  return shards.map(s => s.files);\n}',
       hint='Keep a running total for each shard and pick the smallest with a strict less than, so ties go to the lowest index.', why='This is the longest processing time rule. It is simple and usually lands within a few percent of the best possible split.'),
]

T = {
    'slug': 'js-expert', 'title': 'Expert JavaScript: performance, security and test quality', 'short': 'Expert JavaScript', 'emoji': '🏆', 'module': MODULE, 'minutes': 20,
    'lead': 'The habits that separate experts: choosing the right algorithm and measuring it fairly, finding memory leaks, design patterns for apps and tests, worker threads, XSS and prototype pollution, property based and mutation testing, flaky tests, and a faster CI pipeline.',
    'desc': 'Expert JavaScript: Big O and benchmarks, memory leaks and WeakMap, memoize, observer, builder, worker threads, XSS, prototype pollution, property based testing, mutation testing, flaky tests and CI sharding.',
    'summary': 'Counting steps and benchmarking with a warm up and median, listener leaks and weak references, memoize, pipe, strategy, observer, builder and factory patterns, worker threads and Web Workers, XSS and prototype pollution with a security checklist, property based testing, mutation testing and order dependent flaky tests, and balancing CI shards by duration.',
    'keywords': ['performance', 'Big O', 'benchmark', 'memory leak', 'WeakMap', 'design patterns', 'test data builder', 'worker threads', 'Web Workers', 'XSS', 'prototype pollution', 'security testing', 'property based testing', 'mutation testing', 'flaky tests', 'CI sharding', 'expert JavaScript'],
    'qa_intro': 'Senior testers judge the tests as well as the product: they check performance and memory, try security payloads, measure test quality with mutants, hunt flaky tests and keep the pipeline fast.',
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
