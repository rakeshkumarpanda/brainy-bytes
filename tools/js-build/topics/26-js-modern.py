# Chapter 26: what each yearly edition added, from ES2020 to the features arriving in 2026, with Temporal and resource management.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🧠', 'Expert and latest', 'js-expert', 'The newest language features, performance, patterns, security and the habits of expert JavaScript developers and testers.')

CODES = {
    'es2020': run('''
const order = { id: 7, customer: { name: "Asha", address: null }, discount: 0 };

// Optional chaining: stop at null or undefined instead of throwing
console.log(order.customer?.address?.city);          // undefined, no crash
console.log(order.items?.[0], order.notify?.());     // works for indexes and calls too

// Nullish coalescing: a default only for null and undefined, not for 0 or ""
console.log(order.discount || 10, order.discount ?? 10);

// BigInt for whole numbers beyond 2^53
console.log(2 ** 53 + 1, 2n ** 53n + 1n);

// Logical assignment (ES2021)
const settings = { retries: 0, browser: null };
settings.retries ||= 3;        // 0 is falsy, so it becomes 3
settings.browser ??= "chromium";
console.log(settings);

console.log(1_000_000 + 0.000_5, "a-b-c".replaceAll("-", "/"));
console.log(typeof globalThis);
''', 'ES2020 and ES2021: ?., ??, BigInt and friends'),
    'es2022': run('''
const runs = [{ id: 1, ok: true }, { id: 2, ok: false }, { id: 3, ok: true }, { id: 4, ok: false }];

console.log(runs.at(-1).id);                               // ES2022: count from the end
console.log(Object.hasOwn(runs[0], "ok"));                 // a safer hasOwnProperty

try {
  try { JSON.parse("{bad"); }
  catch (e) { throw new Error("Could not read the config", { cause: e }); }   // ES2022
} catch (e) {
  console.log(e.message, "<-", e.cause.name);
}

// ES2023: find from the end, and "change by copy" methods that never touch the original
console.log(runs.findLast(r => !r.ok).id, runs.findLastIndex(r => r.ok));
const byIdDesc = runs.toSorted((a, b) => b.id - a.id);
console.log(byIdDesc.map(r => r.id), runs.map(r => r.id));
console.log(runs.toReversed()[0].id, runs.with(0, { id: 99 })[0].id, runs.toSpliced(1, 2).length, runs.length);
''', 'ES2022 and ES2023: at, hasOwn, error cause, change by copy'),
    'es2024': run('''
const tests = [
  { name: "login", status: "passed", ms: 840 },
  { name: "search", status: "failed", ms: 120 },
  { name: "checkout", status: "failed", ms: 2310 },
  { name: "profile", status: "skipped", ms: 0 },
];

// Group a list into an object, or a Map, by any rule
const byStatus = Object.groupBy(tests, t => t.status);
console.log(Object.keys(byStatus), byStatus.failed.map(t => t.name));
const bySpeed = Map.groupBy(tests, t => (t.ms > 1000 ? "slow" : "fast"));
console.log(bySpeed.get("slow").map(t => t.name));

// A promise you can resolve from the outside
const { promise, resolve } = Promise.withResolvers();
setTimeout(() => resolve("done"), 10);
console.log(await promise);

// Well formed strings and the v flag for set operations in character classes
console.log("ok".isWellFormed(), "bad \\uD800".isWellFormed());
console.log("Héllo Wörld".match(/[\\p{L}--[a-z]]/gv));    // letters that are not plain a to z
''', 'ES2024: groupBy, withResolvers, the v flag'),
    'es2025': run('''
// Iterator helpers: lazy map, filter, take on any iterator ({{ch:js-collections-iterators}})
function* ids() { let n = 1; while (true) yield `TC-${n++}`; }
console.log(ids().filter(id => id.endsWith("7")).take(2).toArray());

// Set methods ({{ch:js-collections-iterators}})
console.log([...new Set(["a", "b", "c"]).difference(new Set(["b"]))]);

// RegExp.escape: put user text into a pattern safely
const userText = "Price (incl. tax) $5.00?";
console.log(RegExp.escape(userText));
console.log(new RegExp(RegExp.escape(userText)).test(`Total: ${userText}`));

// Promise.try: run a function that may throw or return a promise, and always get a promise
const readConfig = () => { throw new Error("missing file"); };
await Promise.try(readConfig).catch(e => console.log("caught:", e.message));

// Duplicate named groups and inline modifiers in regular expressions
const date = /(?<y>\\d{4})-(?<m>\\d\\d)|(?<m>\\d\\d)\\/(?<y>\\d{4})/;
console.log(date.exec("2026-10").groups.y, date.exec("10/2026").groups.y);
console.log(/^(?i:hello) World$/.test("HELLO World"), /^(?i:hello) World$/.test("hello WORLD"));

// Float16Array and Math.f16round for compact numbers (machine learning, graphics)
console.log(Math.f16round(1.337), new Float16Array([1.337])[0]);
''', 'ES2025: iterator helpers, Set methods, RegExp.escape, Promise.try'),
    'import-attrs': show('''
// ES2025: import attributes and JSON modules
import config from "./playwright.settings.json" with { type: "json" };
const { default: users } = await import("./users.json", { with: { type: "json" } });
''', 'Import attributes for JSON', note='Runs in {{ch:js-modules-tooling}}'),
    'es2026': run('''
// Explicit resource management: "using" calls Symbol.dispose when the block ends,
// even if an error is thrown. Great for browsers, servers, temp files and DB connections.
function openBrowser(name) {
  console.log(`open ${name}`);
  return { name, [Symbol.dispose]() { console.log(`close ${name}`); } };
}
function runTest() {
  using browser = openBrowser("chromium");
  using other = openBrowser("firefox");
  console.log(`testing with ${browser.name} and ${other.name}`);
  throw new Error("assertion failed");
}
try { runTest(); } catch (e) { console.log("test failed:", e.message); }

// Async version: await using with Symbol.asyncDispose
async function startServer() {
  return { url: "http://localhost:4173", async [Symbol.asyncDispose]() { console.log("server stopped"); } };
}
{
  await using server = await startServer();
  console.log("server at", server.url);
}

// Error.isError works across frames and realms, unlike instanceof
console.log(Error.isError(new TypeError("x")), Error.isError({ message: "fake" }));

// Array.fromAsync collects an async iterable
async function* pages() { yield [1, 2]; yield [3]; }
console.log((await Array.fromAsync(pages())).flat());

// Base64 and hex built into Uint8Array
const bytes = new TextEncoder().encode("QA rocks");
console.log(bytes.toBase64(), bytes.toHex().slice(0, 8), new TextDecoder().decode(Uint8Array.fromBase64("UUEgcm9ja3M=")));

// Map.getOrInsertComputed, Iterator.concat
const cache = new Map();
console.log(cache.getOrInsertComputed("token", () => "t-123"), cache.size);
console.log(Iterator.concat([1, 2], new Set([3])).toArray());

// JSON.parse can read the original text of a number, so big ids survive
console.log(JSON.parse('{"orderId": 90071992547409931}', (k, v, ctx) => (k === "orderId" ? BigInt(ctx.source) : v)));
''', 'ES2026 and using: Error.isError, fromAsync, base64, upsert and more', play=False),
    'disposable-stack': run('''
// DisposableStack: collect clean up steps as you go, run them all in reverse at the end
function setUpSuite() {
  using stack = new DisposableStack();
  const server = stack.adopt({ port: 4173 }, s => console.log("stop server on", s.port));
  stack.defer(() => console.log("delete temp folder"));
  const user = stack.adopt({ id: 42 }, u => console.log("delete test user", u.id));
  console.log("suite ready:", server.port, user.id);
  return stack.move();               // hand the clean up to the caller instead of running it now
}
const cleanup = setUpSuite();
console.log("tests run here");
cleanup.dispose();
console.log("disposed:", cleanup.disposed);

// Errors in clean up are not lost: they are wrapped in a SuppressedError
try {
  using a = { [Symbol.dispose]() { throw new Error("close failed"); } };
  throw new Error("test failed");
} catch (e) {
  console.log(e.name, "|", e.error.message, "| hid:", e.suppressed.message);
}
''', 'DisposableStack and SuppressedError for test set up', play=False),
    'support': run('''
// Feature detection: ask the runtime instead of guessing from a version number
const checks = {
  "using (ES2027)": () => { new Function("{ using x = null; }")(); return true; },
  "Temporal (ES2027)": () => typeof Temporal === "object",
  "Error.isError (ES2026)": () => typeof Error.isError === "function",
  "Map getOrInsert (ES2026)": () => typeof Map.prototype.getOrInsert === "function",
  "Math.sumPrecise (ES2026)": () => typeof Math.sumPrecise === "function",
  "iterator chunks (ES2027)": () => typeof Iterator.prototype.chunks === "function",
  "Iterator.zip (ES2027)": () => typeof Iterator.zip === "function",
  "iterator join (ES2027)": () => typeof Iterator.prototype.join === "function",
};
for (const [name, check] of Object.entries(checks)) {
  let ok;
  try { ok = check(); } catch { ok = false; }
  console.log((ok ? "yes " : "not yet ") + name);
}
console.log("loop sum:", [0.1, 0.2, 0.3].reduce((a, b) => a + b, 0));
''', 'Which of the newest features this Node.js has', play=False),
    'next': show('''
// Finished for ES2027 (iterator helpers) or ES2026 (sumPrecise), but not in Node.js 26 yet.
const ids = ["TC-1", "TC-2", "TC-3", "TC-4", "TC-5"];

ids.values().chunks(2).toArray();        // [["TC-1","TC-2"], ["TC-3","TC-4"], ["TC-5"]]  batches for workers
ids.values().windows(2).toArray();       // [["TC-1","TC-2"], ["TC-2","TC-3"], ...]     neighbours to compare

const names = ["login", "cart"], times = [812, 2310];
Iterator.zip([names, times]).toArray();               // [["login", 812], ["cart", 2310]]
Iterator.zipKeyed({ name: names, ms: times }).toArray(); // [{ name: "login", ms: 812 }, ...]

new Set(["chromium", "firefox"]).values().join(" | ");   // "chromium | firefox"
new Set(["chromium", "firefox"]).values().includes("webkit"); // false

Math.sumPrecise([0.1, 0.2, 0.3]);         // 0.6, a plain loop gives 0.6000000000000001
''', 'Coming next, shown with the results the proposals define', note='Not in Node.js 26 yet'),
    'temporal': run('''
const { PlainDate, PlainDateTime, ZonedDateTime, Duration, Instant } = Temporal;

// Dates without times or time zones: perfect for test data such as birthdays and due dates
const due = PlainDate.from("2026-01-31");
console.log(due.add({ months: 1 }).toString());            // clamps to the end of February
console.log(due.dayOfWeek, due.daysInMonth, due.inLeapYear);

// Exact age check, for an "18 or older" rule
const birthday = PlainDate.from("2008-10-21");
const today = PlainDate.from("2026-10-20");
console.log("age:", birthday.until(today, { largestUnit: "years" }).years);

// Time zones done right: the same meeting in Kolkata and Berlin
const meeting = ZonedDateTime.from("2026-03-29T10:00[Asia/Kolkata]");
console.log(meeting.withTimeZone("Europe/Berlin").toString());

// Durations you can add, compare and round
const timeout = Duration.from({ minutes: 1, seconds: 30 });
console.log(timeout.total("milliseconds"), Duration.compare(timeout, { seconds: 60 }));

// Objects are immutable and comparisons are explicit
const a = PlainDateTime.from("2026-10-20T09:00");
console.log(PlainDateTime.compare(a, a.add({ minutes: 5 })), a.toString());
console.log(Instant.from("2026-10-20T09:00:00Z").epochMilliseconds);
''', 'Temporal: dates and times that behave', play=False),
    'scenario': run('''
// Old style helper from a 2016 test suite
function oldSummary(results) {
  var copy = results.slice();
  copy.sort(function (a, b) { return b.ms - a.ms; });
  var groups = {};
  for (var i = 0; i < results.length; i++) {
    var s = results[i].status;
    if (!groups.hasOwnProperty(s)) groups[s] = [];
    groups[s].push(results[i].name);
  }
  var slowest = copy.length > 0 ? copy[0].name : "none";
  var owner = results.length && results[0].meta && results[0].meta.owner ? results[0].meta.owner : "unknown";
  return { failed: groups.failed || [], slowest: slowest, owner: owner };
}

// The same helper with modern features
const newSummary = results => ({
  failed: Object.groupBy(results, r => r.status).failed?.map(r => r.name) ?? [],
  slowest: results.toSorted((a, b) => b.ms - a.ms)[0]?.name ?? "none",
  owner: results[0]?.meta?.owner ?? "unknown",
});

const runs = [
  { name: "login", status: "passed", ms: 840, meta: { owner: "team-auth" } },
  { name: "checkout", status: "failed", ms: 2310 },
  { name: "search", status: "failed", ms: 120 },
];
for (const input of [runs, []]) {
  const before = oldSummary(input), after = newSummary(input);
  console.log(JSON.stringify(after), "| same as old:", JSON.stringify(before) === JSON.stringify(after));
}
''', 'Modernise an old helper and prove nothing changed'),
}

LANES = {
    'lazy': {'t': 'Iterator helpers pull one value at a time',
             'code': 'function* ids() { let n = 1; while (true) yield `TC-${n++}`; }\nids().filter(id => id.endsWith("7"))\n     .take(2)\n     .toArray();',
             'lanes': ['toArray asks for', 'Generator makes', 'filter says', 'Result'], 'tone': [2, 0, 3, 1],
             'steps': [{'l': 4, 'v': [['next value please'], [], [], []], 'm': 'toArray asks take for a value, take asks filter, filter asks the generator. Nothing has been made yet.'},
                       {'l': 1, 'v': [['next value please'], ['TC-1'], ['TC-1: no, ask again'], []], 'm': 'The generator makes TC-1. It does not end with 7, so filter asks for another one.'},
                       {'l': 1, 'v': [['next value please'], ['TC-2 ... TC-6'], ['no, no, no, no, no'], []], 'm': 'TC-2 to TC-6 are made and rejected one by one. No array of rejected values is ever built.'},
                       {'l': 2, 'v': [['next value please'], ['TC-7'], ['TC-7: yes'], ['TC-7']], 'm': 'TC-7 passes the filter, goes through take (1 of 2) and lands in the result.'},
                       {'l': 2, 'v': [['next value please'], ['TC-8 ... TC-17'], ['TC-17: yes'], ['TC-7', 'TC-17']], 'm': 'The pulling goes on until TC-17 passes. take now has 2 values.'},
                       {'l': 3, 'v': [['done'], ['stopped at TC-17'], [], ['TC-7', 'TC-17']], 'm': 'take tells the chain it is done. The endless generator is closed and TC-18 is never made.'}]},
    'using': {'t': 'using: clean up in reverse order, even after an error',
              'code': '{\n  using db = openDb();\n  using browser = openBrowser();\n  runTest();            // throws\n}\n// the error arrives here',
              'lanes': ['Running', 'Open resources', 'Log'], 'tone': [2, 0, 4],
              'steps': [{'l': 2, 'v': [['openDb()'], ['db'], ['open db']], 'm': 'using db opens the database and remembers to dispose it when the block ends.'},
                        {'l': 3, 'v': [['openBrowser()'], ['db', 'browser'], ['open db', 'open browser']], 'm': 'using browser opens a browser on top of it, like a stack.'},
                        {'l': 4, 'v': [['runTest() throws'], ['db', 'browser'], ['open db', 'open browser', 'Error: assertion failed']], 'm': 'The test throws. Without using, both resources would stay open on the CI machine.'},
                        {'l': 5, 'v': [['browser[Symbol.dispose]()'], ['db'], ['open db', 'open browser', 'Error: assertion failed', 'close browser']], 'm': 'Leaving the block disposes the last resource first: the browser closes.'},
                        {'l': 5, 'v': [['db[Symbol.dispose]()'], [], ['open db', 'open browser', 'Error: assertion failed', 'close browser', 'close db']], 'm': 'Then the database closes. Reverse order matters because later resources often depend on earlier ones.'},
                        {'l': 6, 'v': [['catch (e)'], [], ['open db', 'open browser', 'Error: assertion failed', 'close browser', 'close db', 'test failed']], 'm': 'Only now does the original error reach the catch block. The test still fails, but nothing is left running.'}]},
}

PARTS = [
    part('yearly', '📅', 'How JavaScript grows every year', '''
<p>Every June, Ecma publishes a new edition of the standard: ES2020, ES2021 and so on. A feature joins only after it reaches <b>stage 4</b> at TC39, which needs two shipping browser engines and a full test suite. Engines often ship features months before the edition that lists them, so "can I use it" depends on your browsers and Node.js version, not the year on the label.</p>
<div class="tw"><table class="jt"><tr><th>Edition</th><th>Highlights you will meet in real code</th></tr>
<tr><td>ES2015 (ES6)</td><td>let and const, arrow functions, classes, modules, promises, template literals, destructuring, Map and Set</td></tr>
<tr><td>ES2017</td><td>async and await, Object.entries, padStart</td></tr>
<tr><td>ES2020</td><td><code>?.</code>, <code>??</code>, BigInt, Promise.allSettled, globalThis, dynamic import</td></tr>
<tr><td>ES2021</td><td><code>||=</code> <code>&amp;&amp;=</code> <code>??=</code>, replaceAll, Promise.any, numeric separators, WeakRef</td></tr>
<tr><td>ES2022</td><td>class fields and <code>#private</code>, top level await, <code>.at()</code>, Object.hasOwn, error cause</td></tr>
<tr><td>ES2023</td><td>findLast, toSorted, toReversed, toSpliced, with</td></tr>
<tr><td>ES2024</td><td>Object.groupBy, Map.groupBy, Promise.withResolvers, the <code>v</code> regex flag</td></tr>
<tr><td>ES2025</td><td>iterator helpers, Set methods, RegExp.escape, Promise.try, import attributes, Float16Array</td></tr>
<tr><td>ES2026 (June 2026)</td><td>Error.isError, Array.fromAsync, Uint8Array base64 and hex, Map and WeakMap <code>getOrInsert</code> (upsert), Iterator.concat, JSON.parse source text and JSON.rawJSON, Math.sumPrecise</td></tr>
<tr><td>Finished for ES2027</td><td><code>using</code> and <code>await using</code> with DisposableStack, Temporal, Atomics.pause, iterator <code>chunks</code> and <code>windows</code>, <code>Iterator.zip</code>, iterator <code>includes</code> and <code>join</code></td></tr>
</table></div>
<p>The "Finished for ES2027" row comes from TC39's list of finished proposals, checked in October 2026. Being finished means the design will not change, but a feature can still be missing from your Node.js or browser. The last part of this chapter shows how to check.</p>
<div class="tip">Check support on <b>caniuse.com</b> or MDN's compatibility tables, and set your TypeScript <code>target</code> and lint rules to match the oldest browser or Node.js you support.</div>
''', kw=['ECMAScript', 'ES2015', 'ES6', 'ES2020', 'ES2021', 'ES2022', 'ES2023', 'ES2024', 'ES2025', 'ES2026', 'TC39', 'stage 4', 'browser support']),
    part('es2020', '❓', 'ES2020 to ES2023: safer access and copies', '''
<p>Optional chaining and nullish coalescing removed most of the "cannot read properties of undefined" crashes from everyday code. The ES2023 <b>change by copy</b> methods return a new array and leave the original alone, which makes test data safe to reuse.</p>
[[es2020]]
[[es2022]]
<div class="qa-box"><code>??</code> against <code>||</code> matters in tests: a retry count of 0 or an empty search string are real values, and <code>||</code> silently replaces them with the default.</div>
''', qa=True, qa_why='These features appear in nearly every modern test file and page object.',
        kw=['optional chaining', '?.', 'nullish coalescing', '??', 'BigInt', 'logical assignment', '??=', 'replaceAll', 'at', 'Object.hasOwn', 'error cause', 'findLast', 'toSorted', 'toReversed', 'toSpliced', 'with', 'change by copy']),
    part('es2024', '🧰', 'ES2024 and ES2025: grouping, iterators, safer regexes', '''
<p>Grouping a list, a promise you resolve from outside, lazy iterator helpers, real set operations and a safe way to put user text into a regular expression all arrived in the last two editions.</p>
[[es2024]]
<p>Iterator helpers are <b>lazy</b>. Arrays do each step for every element before the next step starts. An iterator chain pulls one value at a time through all the steps, and stops the moment <code>take</code> has enough. That is why the example below can work on an endless list of test ids without running forever.</p>
<div class="viz" data-viz="lanes" data-k="lazy"></div>
[[es2025]]
[[import-attrs]]
<div class="warn"><code>new RegExp(userText)</code> breaks or misbehaves when the text contains <code>( ) . ? $</code>. <code>RegExp.escape</code> fixes that, which matters for tests that search a page for product names or prices.</div>
''', qa=True, qa_why='groupBy summarises test results in one line, and RegExp.escape makes text matching in tests safe.',
        kw=['Object.groupBy', 'Map.groupBy', 'Promise.withResolvers', 'v flag', 'isWellFormed', 'iterator helpers', 'Set methods', 'RegExp.escape', 'Promise.try', 'duplicate named groups', 'regex modifiers', 'Float16Array', 'import attributes']),
    part('es2026', '🆕', 'ES2026 and ES2027: using, Error.isError, upsert and more', '''
<p>The June 2026 edition, ES2026, is a collection of small tools that remove common helper functions from real projects:</p>
<ul>
<li><b>Error.isError</b> tells you whether a value is a real error, even one made in another frame or a <code>vm</code> context, where <code>instanceof Error</code> gives the wrong answer.</li>
<li><b>Array.fromAsync</b> collects an async iterable, such as pages of API results, into one array.</li>
<li><b>Uint8Array base64 and hex</b> methods replace the old <code>btoa</code> tricks and <code>Buffer</code> calls for tokens, file uploads and signatures.</li>
<li><b>Upsert</b>: <code>map.getOrInsert(key, value)</code> and <code>getOrInsertComputed(key, fn)</code> read a key or add it in one step, the classic cache pattern.</li>
<li><b>Iterator.concat</b> joins several iterables lazily, and <b>JSON.parse source text access</b> lets a reviver read the original text of a number, so long ids survive as BigInt.</li>
<li><b>Math.sumPrecise</b> adds a list of numbers without the rounding drift of a loop. It is in the standard but not yet in Node.js 26, so it appears in the last part.</li>
</ul>
<p>The headline feature for ES2027, already finished and already shipping in Node.js 24 and later, is <b>explicit resource management</b>. A variable declared with <code>using</code> is cleaned up automatically when its block ends, in reverse order, even when an error is thrown. It replaces long <code>try</code> and <code>finally</code> blocks around browsers, servers, files and connections.</p>
<div class="viz" data-viz="lanes" data-k="using"></div>
[[es2026]]
<p>When the clean up steps are only known at run time, collect them in a <b>DisposableStack</b>. Each <code>adopt</code> or <code>defer</code> adds a step, and they all run in reverse order. If both the test and a clean up step fail, nothing is lost: the two errors are joined in a <code>SuppressedError</code>.</p>
[[disposable-stack]]
<div class="modern">These features ship in Node.js 24 and later and in current browsers, with TypeScript support for <code>using</code>. The page you are reading ran them on Node.js 26. If your users run older browsers, check support or use a transpiler.</div>
''', qa=['Playwright', 'Node.js'], qa_why='using makes sure browsers, servers and temp data are always cleaned up, even when a test fails.',
        kw=['ES2026', 'ES2027', 'using', 'await using', 'Symbol.dispose', 'Symbol.asyncDispose', 'explicit resource management', 'DisposableStack', 'AsyncDisposableStack', 'SuppressedError', 'Error.isError', 'Array.fromAsync', 'toBase64', 'fromBase64', 'toHex', 'getOrInsert', 'getOrInsertComputed', 'upsert', 'Iterator.concat', 'JSON.parse source', 'JSON.rawJSON', 'Math.sumPrecise']),
    part('temporal', '🕰️', 'Temporal: dates done right', '''
<p>The old <code>Date</code> object mixes up time zones, months that start at 0 and objects that change in place. <b>Temporal</b> replaces it with clear types: <code>PlainDate</code> for a calendar date, <code>PlainDateTime</code> without a zone, <code>ZonedDateTime</code> with a zone, <code>Instant</code> for an exact moment and <code>Duration</code> for lengths of time. Every object is immutable.</p>
[[temporal]]
<div class="qa-box">Date bugs are some of the most common bugs testers find: month ends (31 January plus one month), leap years, daylight saving changes, and users in other time zones. Temporal makes the expected values in your tests easy to compute correctly.</div>
''', qa=True, qa_why='Date and time zone edge cases are a classic source of bugs and of wrong expected values in tests.',
        kw=['Temporal', 'PlainDate', 'PlainDateTime', 'ZonedDateTime', 'Instant', 'Duration', 'time zone', 'daylight saving', 'leap year', 'age check', 'immutable dates']),
    part('next', '🔭', 'What comes next, and how to check before you use it', '''
<p>A feature you read about may not exist where your code runs. Old phones, a company laptop with an old browser, or a CI image with an older Node.js all lag behind. Professionals do not guess from version numbers. They <b>detect the feature</b> at run time, or they let tools such as TypeScript's <code>lib</code> setting, ESLint and Babel check it at build time.</p>
[[support]]
<p>The "not yet" lines are features that TC39 has finished but V8 in Node.js 26 has not shipped. When they arrive, they will remove more small helpers from real projects: splitting test ids into batches for parallel workers, pairing names with timings in a report, and adding up money without floating point drift.</p>
[[next]]
<div class="tw"><table class="jt"><tr><th>Proposal</th><th>Stage in October 2026</th><th>What it would give you</th></tr>
<tr><td>Deferring module evaluation (<code>import defer</code>)</td><td>3</td><td>Load a module at start up but run its code only when you first use it, so apps start faster</td></tr>
<tr><td>Source phase imports, import text</td><td>3</td><td>Import a WebAssembly module or a text file directly</td></tr>
<tr><td>Decorators</td><td>2.7</td><td>Standard <code>@decorator</code> syntax. TypeScript already supports it ({{ch:js-metaprogramming}})</td></tr>
<tr><td>Math.clamp</td><td>2</td><td>Keep a number between a minimum and a maximum</td></tr></table></div>
<div class="tip">Follow new features on the TC39 proposals page on GitHub, MDN's browser compatibility tables and the V8 blog. A proposal at stage 3 is safe to learn, stage 4 is safe to plan for, and "ships in every browser you support" is safe to use without a fallback.</div>
''', qa=True, qa_why='Test code runs on CI images, old browsers and devices, so checking support prevents "works on my machine" failures.',
        kw=['feature detection', 'browser support', 'TC39 stages', 'stage 3', 'iterator chunks', 'windows', 'Iterator.zip', 'zipKeyed', 'iterator join', 'iterator includes', 'Math.sumPrecise', 'import defer', 'decorators stage 2.7', 'Math.clamp']),
    part('scenario', '🎬', 'Real world scenario: modernise safely', '''
<div class="scenario"><b>The situation</b>An old test helper written in 2016 is hard to read. You want to rewrite it with modern features without changing what it returns.</div>
[[scenario]]
<p>The rewrite is a third of the size. Running both versions on the same inputs, including an empty list, and comparing the results is a simple form of <b>characterisation testing</b>: it proves the behaviour stayed the same before you delete the old code.</p>
''', qa=True, kw=['refactoring', 'modernise', 'legacy code', 'characterisation test', 'optional chaining', 'groupBy', 'toSorted']),
]

INFO = {'title': 'One small release every year', 'panels': [
    panel([['e', '❓'], ['t', 'a?.b ?? "default"', {'b': 1}]], 'Safer access', 'No more crashes on missing fields.', 'And defaults that respect 0 and empty strings.'),
    panel([['e', '📋'], ['t', 'toSorted(), groupBy()', {'b': 1}]], 'Better data tools', 'Copies instead of changes, groups in one line.', 'Test data stays the same between tests.'),
    panel([['e', '🧹'], ['t', 'using browser = …', {'b': 1}]], 'Automatic clean up', 'Resources close themselves.', 'Even when the test throws.'),
    panel([['e', '🕰️'], ['t', 'Temporal.PlainDate', {'b': 1}]], 'Real dates', 'Clear types for dates, times and zones.', 'Month ends and time zones without surprises.')],
    'remember': 'Know which edition a feature came from, check that your browsers and Node.js support it, and prefer the safer modern form.'}

REAL = [
    ['🌍', 'A travel site', 'Moved its booking calendar to Temporal and fixed a long standing bug where flights shown in the user\'s time zone jumped a day around daylight saving changes.'],
    ['🧪', 'A test framework', 'Wraps its browser, server and database fixtures with Symbol.asyncDispose so a failing test can never leave a browser running on a CI machine.'],
    ['🧾', 'A billing service', 'Uses JSON.parse with source text access so 18 digit invoice ids no longer lose their last digits.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter walks through what each edition from ES2020 to ES2026 added, the features finished for ES2027 such as using and Temporal, and how to check what your runtime supports.',
        'यह अध्याय ES2020 से हर edition में जोड़े गए features, अभी आ रहे features जैसे using, और dates के लिए Temporal दिखाता है।',
        'ಈ ಅಧ್ಯಾಯ ES2020 ರಿಂದ ಪ್ರತಿ edition ಸೇರಿಸಿದ features, ಈಗ ಬರುತ್ತಿರುವ using ಮತ್ತು dates ಗಾಗಿ Temporal ತೋರಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ ES2020 ରୁ ପ୍ରତ୍ୟେକ edition ର features, ଏବେ ଆସୁଥିବା using ଓ dates ପାଇଁ Temporal ଦେଖାଏ।',
        'يستعرض هذا الفصل ما أضافته كل نسخة منذ ES2020، والميزات الجديدة مثل using، وTemporal للتواريخ.',
        'Dieses Kapitel zeigt, was jede Ausgabe seit ES2020 brachte, neue Funktionen wie using und Temporal für Datumswerte.'),
    say('yearly', 'Yearly editions', 'A new edition comes every June. Features need stage 4 and two shipping engines, so check support in your browsers and Node.',
        'हर June नया edition आता है। Features को stage 4 और दो engines चाहिए, इसलिए अपने browsers और Node में support जांचें।',
        'ಪ್ರತಿ June ಹೊಸ edition ಬರುತ್ತದೆ. Features ಗೆ stage 4 ಮತ್ತು ಎರಡು engines ಬೇಕು, support ಪರಿಶೀಲಿಸಿ.',
        'ପ୍ରତ୍ୟେକ June ନୂଆ edition ଆସେ। Features ପାଇଁ stage 4 ଓ ଦୁଇଟି engines ଦରକାର, support ଯାଞ୍ଚ କରନ୍ତୁ।',
        'تصدر نسخة جديدة كل يونيو. تحتاج الميزات المرحلة الرابعة ومحركين يدعمانها، فافحص الدعم في متصفحاتك وNode.',
        'Jeden Juni erscheint eine Ausgabe. Funktionen brauchen Stufe 4 und zwei Engines, prüfe die Unterstützung.'),
    say('es2020', 'Safer access', 'Optional chaining stops at missing values, nullish coalescing keeps zero and empty strings, and the copy methods leave the original array alone.',
        'Optional chaining missing values पर रुकता है, nullish coalescing शून्य और खाली strings रखता है, और copy methods original array नहीं बदलते।',
        'Optional chaining ಕಾಣೆಯಾದ values ನಲ್ಲಿ ನಿಲ್ಲುತ್ತದೆ, nullish coalescing ಶೂನ್ಯ ಮತ್ತು ಖಾಲಿ strings ಇಡುತ್ತದೆ.',
        'Optional chaining ନଥିବା values ରେ ଅଟକେ, nullish coalescing ଶୂନ୍ୟ ଓ ଖାଲି strings ରଖେ।',
        'يتوقف التسلسل الاختياري عند القيم المفقودة، ويحتفظ دمج القيم الفارغة بالصفر والنص الفارغ، ولا تغير دوال النسخ المصفوفة الأصلية.',
        'Optional Chaining stoppt bei fehlenden Werten, ?? behält null und leere Texte, Kopiermethoden lassen das Original unberührt.'),
    say('es2024', 'Grouping and iterators', 'groupBy sorts a list into groups in one line, iterator helpers work lazily, and RegExp escape makes user text safe in patterns.',
        'groupBy एक line में list को groups में बांटता है, iterator helpers lazily काम करते हैं, और RegExp.escape user text को सुरक्षित बनाता है।',
        'groupBy ಒಂದು ಸಾಲಿನಲ್ಲಿ list ಅನ್ನು groups ಮಾಡುತ್ತದೆ, iterator helpers lazily ಕೆಲಸ ಮಾಡುತ್ತವೆ, RegExp.escape ಸುರಕ್ಷಿತಗೊಳಿಸುತ್ತದೆ.',
        'groupBy ଗୋଟିଏ ଧାଡ଼ିରେ list କୁ groups କରେ, iterator helpers lazily କାମ କରନ୍ତି, RegExp.escape ସୁରକ୍ଷିତ କରେ।',
        'تقسم groupBy القائمة إلى مجموعات في سطر واحد، وتعمل مساعدات المكررات بكسل، وتجعل RegExp.escape نص المستخدم آمنًا.',
        'groupBy teilt eine Liste in einer Zeile in Gruppen, Iterator-Helfer arbeiten verzögert, RegExp.escape macht Nutzertext sicher.'),
    say('es2026', 'ES2026 and using', 'ES2026 added Error.isError, Array.fromAsync, base64, getOrInsert and more. A variable declared with using is cleaned up when its block ends, in reverse order, even when an error is thrown.',
        'ES2026 ने Error.isError, Array.fromAsync, base64, getOrInsert और बहुत कुछ जोड़ा। using से बना variable block खत्म होने पर उल्टे क्रम में साफ होता है, error आने पर भी।',
        'ES2026 Error.isError, Array.fromAsync, base64, getOrInsert ಸೇರಿಸಿತು. using ನಿಂದ ಘೋಷಿಸಿದ variable block ಮುಗಿದಾಗ ಹಿಮ್ಮುಖ ಕ್ರಮದಲ್ಲಿ ಸ್ವಚ್ಛವಾಗುತ್ತದೆ, error ಬಂದರೂ.',
        'ES2026 Error.isError, Array.fromAsync, base64, getOrInsert ଯୋଡ଼ିଲା। using ରେ ଘୋଷିତ variable block ଶେଷରେ ଓଲଟା କ୍ରମରେ ସଫା ହୁଏ, error ହେଲେ ମଧ୍ୟ।',
        'أضافت ES2026 الدالة Error.isError وArray.fromAsync وbase64 وgetOrInsert وغيرها. ويُنظَّف المتغير المعرّف بـ using عند انتهاء كتلته بترتيب عكسي حتى لو وقع خطأ.',
        'ES2026 brachte Error.isError, Array.fromAsync, base64, getOrInsert und mehr. Eine mit using deklarierte Variable wird am Blockende rückwärts aufgeräumt, auch bei Fehlern.'),
    say('next', 'What comes next', 'Check a feature at run time before you rely on it. Iterator chunks, zip, join and Math.sumPrecise are finished but not in Node 26 yet.',
        'किसी feature पर भरोसा करने से पहले run time पर जांचें। Iterator chunks, zip, join और Math.sumPrecise तैयार हैं पर Node 26 में अभी नहीं हैं।',
        'Feature ಬಳಸುವ ಮೊದಲು run time ನಲ್ಲಿ ಪರಿಶೀಲಿಸಿ. Iterator chunks, zip, join ಮತ್ತು Math.sumPrecise ಸಿದ್ಧ, ಆದರೆ Node 26 ನಲ್ಲಿ ಇನ್ನೂ ಇಲ್ಲ.',
        'Feature ବ୍ୟବହାର ପୂର୍ବରୁ run time ରେ ଯାଞ୍ଚ କରନ୍ତୁ। Iterator chunks, zip, join ଓ Math.sumPrecise ପ୍ରସ୍ତୁତ, କିନ୍ତୁ Node 26 ରେ ଏଯାଏଁ ନାହିଁ।',
        'افحص الميزة وقت التشغيل قبل الاعتماد عليها. التقسيم إلى دفعات وzip وjoin وMath.sumPrecise مكتملة لكنها ليست في Node 26 بعد.',
        'Prüfe eine Funktion zur Laufzeit, bevor du dich darauf verlässt. chunks, zip, join und Math.sumPrecise sind fertig, aber noch nicht in Node 26.'),
    say('temporal', 'Temporal', 'Temporal has separate types for dates, date times, zoned times, instants and durations, and every object is immutable.',
        'Temporal में dates, date times, zoned times, instants और durations के अलग types हैं, और हर object immutable है।',
        'Temporal ನಲ್ಲಿ dates, date times, zoned times, instants ಮತ್ತು durations ಗೆ ಬೇರೆ types ಇವೆ, ಎಲ್ಲವೂ immutable.',
        'Temporal ରେ dates, date times, zoned times, instants ଓ durations ପାଇଁ ଅଲଗା types ଅଛି, ସବୁ immutable।',
        'لدى Temporal أنواع منفصلة للتواريخ والأوقات والمناطق الزمنية واللحظات والمدد، وكل كائن غير قابل للتغيير.',
        'Temporal hat eigene Typen für Datum, Datum mit Zeit, Zeitzonen, Zeitpunkte und Dauern, alle unveränderlich.'),
    say('scenario', 'Scenario', 'Rewrite an old helper with modern features and run both versions on the same inputs to prove nothing changed.',
        'पुराने helper को modern features से फिर लिखें और दोनों versions को एक ही inputs पर चलाकर साबित करें कि कुछ नहीं बदला।',
        'ಹಳೆಯ helper ಅನ್ನು modern features ನಿಂದ ಮರುಬರೆಯಿರಿ, ಎರಡೂ versions ಒಂದೇ inputs ನಲ್ಲಿ ಓಡಿಸಿ.',
        'ପୁରୁଣା helper କୁ modern features ରେ ପୁଣି ଲେଖନ୍ତୁ ଏବଂ ଦୁଇ versions କୁ ସମାନ inputs ରେ ଚଲାନ୍ତୁ।',
        'أعد كتابة دالة قديمة بميزات حديثة وشغّل النسختين على المدخلات نفسها لتثبت أن شيئًا لم يتغير.',
        'Schreibe einen alten Helfer modern neu und lass beide Versionen mit denselben Eingaben laufen.'),
    say('practice', 'Hands-on', 'Practise safe access with defaults, sorting without changing the input, writing groupBy, and a clean up helper like using.',
        'Defaults के साथ safe access, input बदले बिना sort, groupBy लिखना और using जैसा clean up helper का अभ्यास करें।',
        'Defaults ಜೊತೆ safe access, input ಬದಲಿಸದೆ sort, groupBy ಮತ್ತು using ನಂತಹ clean up helper ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Defaults ସହ safe access, input ନ ବଦଳାଇ sort, groupBy ଓ using ପରି clean up helper ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على الوصول الآمن بقيم افتراضية، والفرز دون تغيير المدخلات، وكتابة groupBy، ودالة تنظيف مثل using.',
        'Übe sicheren Zugriff mit Standardwerten, Sortieren ohne Änderung, groupBy und einen Aufräum-Helfer wie using.'),
]

QUIZ = [
    quiz('e', 'What is 0 ?? 5?', ['0', '5', 'null', 'undefined'], 0, 'Only null and undefined trigger the default.', '0 is a real value, so ?? keeps it. 0 || 5 would give 5.'),
    quiz('e', 'What does user?.address?.city give when address is null?', ['undefined', 'null', 'It throws', '""'], 0, 'It stops early.', 'Optional chaining returns undefined as soon as it meets null or undefined.'),
    quiz('e', 'Which method sorts without changing the original array?', ['toSorted', 'sort', 'reverse', 'splice'], 0, 'Change by copy.', 'toSorted returns a new sorted array.'),
    quiz('m', 'What does [10, 20, 30].at(-1) return?', ['30', '10', 'undefined', '-1'], 0, 'Negative counts from the end.', '.at(-1) is the last element.'),
    quiz('m', 'What does Object.groupBy(list, fn) return?', ['An object whose keys are fn results and values are arrays', 'A Map', 'A sorted array', 'A Set'], 0, 'Map.groupBy returns a Map.', 'Each key holds the items that produced it.'),
    quiz('m', 'Why use RegExp.escape(text) before new RegExp(text)?', ['So characters like ( . ? $ are matched literally', 'To make it faster', 'To ignore case', 'To match emoji'], 0, 'Special characters.', 'Without escaping, user text can change the meaning of the pattern.'),
    quiz('h', 'Two resources are declared with using in the same block. In which order are they disposed?', ['Reverse order: the last declared is closed first', 'Declaration order', 'Random', 'Only the first one'], 0, 'Like a stack.', 'Later resources may depend on earlier ones, so they close first.'),
    quiz('h', 'PlainDate.from("2026-01-31").add({ months: 1 }) gives?', ['2026-02-28', '2026-03-03', '2026-02-31', 'An error'], 0, 'February is short.', 'Temporal clamps to the last valid day by default.'),
    quiz('h', 'Which is true about Temporal objects?', ['They are immutable: methods return new objects', 'They change in place like Date', 'They have no time zone support', 'Months start at 0'], 0, 'No surprise changes.', 'Every Temporal method returns a new value.'),
    quiz('x', 'Why can JSON.parse lose digits of a large id like 90071992547409931?', ['Numbers beyond 2^53 cannot be stored exactly as doubles', 'JSON does not allow numbers', 'The id is too short', 'It is a bug in V8'], 0, 'Number.MAX_SAFE_INTEGER.', 'A reviver with the source text can turn it into a BigInt instead.'),
    quiz('x', 'Why is Error.isError(x) better than x instanceof Error in some cases?', ['It works for errors created in other frames or realms', 'It is faster', 'It catches the error', 'It creates an error'], 0, 'iframes and vm contexts.', 'Each realm has its own Error constructor, which breaks instanceof.'),
    quiz('m', 'Which edition added Error.isError, Array.fromAsync and Map getOrInsert?', ['ES2026', 'ES2020', 'ES2015', 'ES2023'], 0, 'The June 2026 edition.', 'They reached stage 4 in time for ES2026. using and Temporal finished later and are listed for ES2027.'),
    quiz('h', 'What does new Map().getOrInsertComputed("token", () => "t-1") return the first time?', ['"t-1", and the map now holds it', 'undefined', 'The map itself', 'It throws because the key is missing'], 0, 'Read or add in one step.', 'The callback runs only when the key is missing, which makes it the standard cache pattern.'),
    quiz('h', 'Both the test and a dispose step throw inside a using block. What does the catch block receive?', ['A SuppressedError holding both errors', 'Only the test error', 'Only the dispose error', 'Nothing, errors are ignored'], 0, 'Neither error is lost.', 'e.error is the newer error from clean up and e.suppressed is the one it hid.'),
    quiz('x', 'Why prefer feature detection over checking the Node.js or browser version?', ['It asks the runtime directly, so it stays right on every engine and version', 'It is required by TC39', 'Version numbers are secret', 'It makes code faster'], 0, 'Ask, do not guess.', 'Engines ship features at different times, and flags or polyfills can add or remove them.'),
    quiz('x', 'What does settings.retries ||= 3 do when retries is 0?', ['Sets it to 3, because 0 is falsy', 'Keeps 0', 'Throws', 'Sets it to undefined'], 0, 'Logical OR assignment.', 'Use ??= if 0 is a valid value you want to keep.'),
]

CALC = [
    calc('e', 'What is [4, 8, 15, 16, 23, 42].at(-2)?', '23', 'Second from the end.', ['The last is 42, the one before is 23.']),
    calc('e', 'How many groups does Object.groupBy([1, 2, 3, 4, 5], n => n % 3) create?', '3', 'Remainders.', ['1 and 4 give 1, 2 and 5 give 2, 3 gives 0.', 'Three keys: 0, 1 and 2.']),
    calc('m', 'What is Number.MAX_SAFE_INTEGER, written as a power of 2 minus 1? Give the exponent.', '53', 'Doubles have 53 bits of precision.', ['<span class="eq">2<sup>53</sup> − 1 = 9,007,199,254,740,991</span>']),
    calc('m', 'Someone born on 2008-10-21. How old are they on 2026-10-20, in whole years?', '17', 'One day short of the birthday.', ['On 2026-10-21 they turn 18.', 'One day earlier they are still 17.']),
    calc('h', 'A Duration of 1 minute 30 seconds is how many milliseconds?', '90000', 'Seconds times 1000.', ['<span class="eq">90 × 1000 = 90000</span>']),
    calc('h', '10:00 in Kolkata (UTC+5:30) on 29 March 2026 is what hour in Berlin, which moves to UTC+2 that day?', '6:30', 'Go through UTC.', ['10:00 minus 5:30 is 04:30 UTC.', '04:30 plus 2:00 is 06:30 in Berlin.'], alt=['06:30', '6.30']),
    calc('x', 'How many editions from ES2015 to ES2025, counting both?', '11', 'One per year.', ['<span class="eq">2025 − 2015 + 1 = 11</span>']),
    calc('x', 'The modern summary helper has 5 lines of body, the old one 13. By what percent is it shorter, rounded?', '62', '(old minus new) over old.', ['<span class="eq">(13 − 5) ÷ 13 × 100 ≈ 61.5</span>', 'Rounded: 62.']),
]

EX = [
    ex('safe', 'e', 'Safe access with defaults', '<p>Write <code>shippingCity(order)</code> that returns <code>order.customer.address.city</code>, or <code>"unknown"</code> if any part is missing. An empty string city should be kept as it is.</p>',
       'function shippingCity(order) {\n  \n}\n',
       [('shippingCity({ customer: { address: { city: "Pune" } } })', 'Pune'), ('shippingCity({ customer: { address: null } })', 'unknown'), ('shippingCity({})', 'unknown'), ('shippingCity(null)', 'unknown'),
        ('shippingCity({ customer: { address: { city: "" } } })', '')],
       'function shippingCity(order) {\n  return order?.customer?.address?.city ?? "unknown";\n}', hint='<code>?.</code> at every step and <code>??</code> for the default.', why='With <code>||</code>, the empty string would wrongly become "unknown".'),
    ex('copy', 'm', 'Sort without side effects', '<p>Write <code>topSlow(results, n)</code> that returns the names of the <code>n</code> slowest results (largest <code>ms</code> first) without changing the <code>results</code> array.</p>',
       'function topSlow(results, n) {\n  \n}\n',
       [('(() => { const r = [{ name: "a", ms: 5 }, { name: "b", ms: 50 }, { name: "c", ms: 20 }]; const top = topSlow(r, 2); return [top, r.map(x => x.name)]; })()', [['b', 'c'], ['a', 'b', 'c']])],
       'function topSlow(results, n) {\n  return results.toSorted((a, b) => b.ms - a.ms).slice(0, n).map(r => r.name);\n}', hint='<code>toSorted</code> instead of <code>sort</code>.', why='The second half of the test checks the original order, which <code>sort</code> would have broken.'),
    ex('group', 'h', 'Write groupBy yourself', '<p>Write <code>groupBy(list, keyFn)</code> that works like <code>Object.groupBy</code>: return an object whose keys are the results of <code>keyFn(item, index)</code> and whose values are arrays of items in their original order.</p>',
       'function groupBy(list, keyFn) {\n  \n}\n',
       [('groupBy([1, 2, 3, 4], n => (n % 2 ? "odd" : "even"))', {'odd': [1, 3], 'even': [2, 4]}), ('groupBy(["a", "b"], (x, i) => i)', {'0': ['a'], '1': ['b']}), ('groupBy([], x => x)', {})],
       'function groupBy(list, keyFn) {\n  const out = {};\n  list.forEach((item, i) => {\n    (out[keyFn(item, i)] ??= []).push(item);\n  });\n  return out;\n}',
       hint='<code>(out[key] ??= []).push(item)</code> creates the array the first time.', why='The built in version returns an object with no prototype, so keys like "constructor" are safe too.'),
    ex('dispose', 'x', 'Clean up like using', '<p>Write <code>async withResources(openers, fn)</code>. <code>openers</code> is a list of async functions, each returning a resource with an async <code>close()</code>. Open them in order, call <code>fn(resources)</code>, and always close every opened resource in reverse order, even when <code>fn</code> or a later opener throws. Return what <code>fn</code> returns, or rethrow its error.</p>',
       'async function withResources(openers, fn) {\n  \n}\n',
       [('(async () => { const log = []; const make = n => async () => ({ n, close: async () => log.push("close " + n) }); const r = await withResources([make("db"), make("browser")], async ([a, b]) => a.n + "+" + b.n); return [r, log]; })()', ['db+browser', ['close browser', 'close db']]),
        ('(async () => { const log = []; const make = n => async () => ({ close: async () => log.push("close " + n) }); try { await withResources([make("db"), async () => { throw new Error("no browser"); }], async () => "never"); } catch (e) { return [e.message, log]; } })()', ['no browser', ['close db']])],
       'async function withResources(openers, fn) {\n  const opened = [];\n  try {\n    for (const open of openers) opened.push(await open());\n    return await fn(opened);\n  } finally {\n    for (const r of opened.toReversed()) await r.close();\n  }\n}',
       hint='Keep a list of what actually opened, and close it in a <code>finally</code> block.', why='This is exactly what <code>await using</code> does for you, and why it closes only resources that were successfully opened.'),
]

T = {
    'slug': 'js-modern', 'title': 'Modern JavaScript: ES2020 to ES2027', 'short': 'Modern JavaScript', 'emoji': '🆕', 'module': MODULE, 'minutes': 22,
    'lead': 'What every yearly edition added and why it matters: optional chaining and nullish coalescing, change by copy arrays, groupBy, iterator helpers and Set methods, RegExp.escape and Promise.try, the new using declarations for automatic clean up, Temporal for dates and time zones, the ES2026 edition with upsert and base64, DisposableStack, and how to check for the features that are finished but not shipped yet.',
    'desc': 'ES2020 to ES2027: ?., ??, BigInt, at, toSorted, groupBy, withResolvers, iterator helpers, Set methods, RegExp.escape, Promise.try, using, Error.isError, Array.fromAsync, base64, getOrInsert, DisposableStack, Temporal, iterator chunks and zip, and feature detection.',
    'summary': 'The yearly release process and a table of editions, ES2020 to ES2023 features for safer access and copies, ES2024 and ES2025 grouping, iterator helpers, Set methods and safer regular expressions, the newest features such as using and await using, Error.isError and base64, Temporal for dates, ages, time zones and durations, feature detection and the proposals coming next, and modernising an old helper with a check that its results did not change.',
    'keywords': ['ES2020', 'ES2021', 'ES2022', 'ES2023', 'ES2024', 'ES2025', 'ES2026', 'ES2027', 'DisposableStack', 'getOrInsert', 'feature detection', 'optional chaining', 'nullish coalescing', 'toSorted', 'groupBy', 'iterator helpers', 'RegExp.escape', 'Promise.try', 'using', 'Symbol.dispose', 'Temporal', 'latest JavaScript'],
    'qa_intro': 'Modern features make test code shorter and safer: defaults that respect 0, test data that is never changed by accident, and browsers and servers that always get closed.',
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
