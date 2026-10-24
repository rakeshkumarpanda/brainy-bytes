# Chapter 14: errors in depth, async failures, debugging tools, structured logging and source maps.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🔬', 'JavaScript in depth', 'js-depth', 'How the engine really works, errors and debugging, regular expressions, functional style, metaprogramming and Node.js in depth.')

CODES = {
    'builtin': run('''
const cases = [
  () => null.length,                         // TypeError: wrong kind of value
  () => notDefinedAnywhere,                  // ReferenceError: unknown name
  () => new Array(-1),                       // RangeError: value out of range
  () => JSON.parse("{bad json}"),            // SyntaxError: at run time, from a parser
  () => decodeURIComponent("%"),             // URIError
  () => { throw new AggregateError([new Error("a"), new Error("b")], "2 checks failed"); },
];
for (const fn of cases) {
  try { fn(); }
  catch (e) { console.log(e.constructor.name.padEnd(15), e.message, e.errors ? `(${e.errors.length} inside)` : ""); }
}
''', 'The built in error types'),
    'custom': run('''
// A small hierarchy: catch the family, or one exact kind
class AppError extends Error {
  constructor(message, { code, cause, details } = {}) {
    super(message, { cause });
    this.name = new.target.name;             // "ValidationError", not "Error"
    this.code = code;
    this.details = details;
  }
}
class ValidationError extends AppError {}
class HttpError extends AppError {
  constructor(status, url) { super(`HTTP ${status} from ${url}`, { code: `HTTP_${status}` }); this.status = status; }
  get retryable() { return this.status >= 500 || this.status === 429; }
}

function placeOrder(qty) {
  if (!Number.isInteger(qty) || qty < 1) throw new ValidationError("qty must be a whole number from 1", { code: "BAD_QTY", details: { qty } });
  throw new HttpError(503, "/api/orders");
}

for (const qty of [0, 2]) {
  try { placeOrder(qty); }
  catch (e) {
    if (e instanceof ValidationError) console.log("fix the input:", e.code, e.details);
    else if (e instanceof HttpError) console.log(e.name, e.message, "| retry?", e.retryable);
    console.log("  still an Error:", e instanceof Error, "| an AppError:", e instanceof AppError);
  }
}

// Wrap low level errors with cause so no detail is lost
try {
  try { JSON.parse("<html>502 Bad Gateway</html>"); }
  catch (e) { throw new AppError("Could not read the orders response", { code: "BAD_BODY", cause: e }); }
} catch (e) {
  console.log(`${e.name}: ${e.message}\\n  caused by ${e.cause.name}: ${e.cause.message.split(",")[0]}`);
}
''', 'Custom errors with code and cause'),
    'async-errors': run('''
// 1. try and catch does not reach a callback that runs later
try {
  setTimeout(() => { try { throw new Error("inside the timer"); } catch (e) { console.log("caught inside the callback:", e.message); } }, 0);
} catch { console.log("this outer catch never runs"); }

// 2. With await, a rejected promise becomes a normal throw
async function loadUser() { throw new Error("401 Unauthorized"); }
try { await loadUser(); } catch (e) { console.log("await turns rejection into throw:", e.message); }

// 3. Without await, the rejection escapes the try block
try { loadUser().catch(e => console.log("only .catch sees it:", e.message)); }
catch { console.log("never reached"); }

// 4. finally runs whatever happens, which is where clean up belongs
async function withBrowser() {
  try { throw new Error("assertion failed"); }
  finally { console.log("finally: browser closed"); }
}
await withBrowser().catch(e => console.log("test failed:", e.message));
await new Promise(r => setTimeout(r, 5));
''', 'Errors in async code'),
    'unhandled': run('''
async function save() { throw new Error("DB down"); }
save();                                      // nobody awaits or catches this promise
setTimeout(() => console.log("this line never prints"), 10);
''', 'An unhandled rejection stops Node.js', expect='throw', play=False),
    'handlers': run('''
// Last line of defence: log, then exit with a failure code so CI notices
process.on("unhandledRejection", (reason) => {
  console.log("unhandledRejection:", reason.message);
  process.exitCode = 1;
});
process.on("uncaughtException", (err, origin) => {
  console.log(`${origin}:`, err.message);
  process.exitCode = 1;
});
process.on("exit", code => console.log("exit code", code));

Promise.reject(new Error("forgot to await the cleanup"));
setTimeout(() => { throw new Error("bug in a timer"); }, 0);
''', 'Global handlers for the errors nobody caught', play=False, expect='throw'),
    'result': run('''
// Expected failures as values, unexpected ones as exceptions
const ok = value => ({ ok: true, value });
const fail = (code, message) => ({ ok: false, code, message });

function parseCoupon(text) {
  const m = /^([A-Z]+)(\\d{1,2})$/.exec(text.trim());
  if (!m) return fail("FORMAT", `"${text}" is not like SAVE10`);
  const percent = Number(m[2]);
  if (percent > 50) return fail("TOO_BIG", `${percent}% is over the 50% limit`);
  return ok({ name: m[1], percent });
}

for (const input of ["SAVE10", "save10", "MEGA90"]) {
  const r = parseCoupon(input);
  console.log(input.padEnd(7), r.ok ? `valid ${r.value.percent}%` : `${r.code}: ${r.message}`);
}
''', 'Errors as values for expected failures'),
    'inspect': run('''
import util from "node:util";

const response = { status: 200, body: { order: { id: 7, items: [{ sku: "PEN", price: { amount: 10, currency: "INR" } }] } } };
console.log(response);                                          // nested objects are cut at depth 2
console.log(util.inspect(response, { depth: null, compact: true, breakLength: 120 }));
console.dir(response.body.order.items, { depth: 0 });

console.table([{ test: "login", ms: 840, ok: true }, { test: "checkout", ms: 2310, ok: false }]);
console.group("checkout");
console.count("retry");
console.count("retry");
console.assert(1 + 1 === 3, "maths is broken");               // prints only when false
console.groupEnd();
console.log(util.format("%s took %d ms (%o)", "login", 840, { slow: false }));
''', 'Inspect what you log'),
    'debugger': show('''
# Pause on the first line, then open chrome://inspect in Chrome or press F5 in VS Code
node --inspect-brk src/checkout.js

# Debug a single test file
node --inspect-brk --test test/cart.test.js
npx vitest --inspect-brk --no-file-parallelism cart.test.js

# Playwright: step through actions in the Inspector, or record a trace to replay later
PWDEBUG=1 npx playwright test checkout.spec.ts
npx playwright test --trace on && npx playwright show-trace test-results/**/trace.zip

# A debugger; statement in code pauses there when DevTools or the debugger is attached
''', 'Starting the debuggers', lang='bash', note='Interactive tools'),
    'als': run('''
import { AsyncLocalStorage } from "node:async_hooks";

// Structured JSON logs with a request id that follows the work through every await
const context = new AsyncLocalStorage();
const log = (level, msg, extra = {}) =>
  console.log(JSON.stringify({ level, msg, requestId: context.getStore()?.requestId, ...extra }));

async function fetchStock(sku) { await new Promise(r => setTimeout(r, sku === "PEN" ? 20 : 5)); log("debug", "stock checked", { sku }); return 3; }
async function handleOrder(requestId, sku) {
  return context.run({ requestId }, async () => {
    log("info", "order received", { sku });
    await fetchStock(sku);
    log("info", "order placed");
  });
}

// Two requests run at the same time, yet every line carries the right id
await Promise.all([handleOrder("req-1", "PEN"), handleOrder("req-2", "BOOK")]);
''', 'Structured logs with a request id across awaits'),
    'sourcemaps': test({
        'package.json': pkg('maps', 'module'),
        'tsconfig.json': '''
{
  "compilerOptions": { "target": "es2022", "module": "nodenext", "rootDir": "src", "outDir": "dist", "sourceMap": true, "strict": true },
  "include": ["src"]
}
''',
        'src/price.ts': '''
export function lineTotal(price: number, qty: number): number {
  if (qty > 10) {
    throw new RangeError(`qty ${qty} is over the limit of 10`);
  }
  return price * qty;
}

lineTotal(99, 12);
''',
        'run.sh': '''
npx tsc || exit 1
echo "$ node dist/price.js"
node dist/price.js 2>&1 | grep -E "RangeError|at lineTotal"
echo
echo "$ node --enable-source-maps dist/price.js"
node --enable-source-maps dist/price.js 2>&1 | grep -E "RangeError|at lineTotal"
true
''',
    }, 'sh run.sh', 'Source maps point the trace at the TypeScript line', show=['src/price.ts', 'run.sh'], shown_cmd='sh run.sh',
        replace=[(r'file://\S*/(dist|src)/', r'file:///project/\1/')]),
    'scenario': run('''
// Sort failed tests into buckets before anyone starts debugging
const failures = [
  { test: "checkout total", error: { name: "AssertionError", message: "expected 450 to equal 405" } },
  { test: "login", error: { name: "TimeoutError", message: "locator.click: Timeout 5000ms exceeded" } },
  { test: "search", error: { name: "Error", message: "connect ECONNREFUSED 127.0.0.1:3000" } },
  { test: "profile", error: { name: "TypeError", message: "Cannot read properties of undefined (reading 'name')" } },
  { test: "orders", error: { name: "Error", message: "HTTP 503 from /api/orders" } },
];

const rules = [
  [e => /ECONNREFUSED|ENOTFOUND|HTTP 50[234]/.test(e.message), "environment"],
  [e => e.name === "TimeoutError", "timing or locator"],
  [e => e.name === "AssertionError" || /expect/.test(e.message), "possible product bug"],
  [e => ["TypeError", "ReferenceError"].includes(e.name), "test code bug"],
];
const bucket = e => rules.find(([match]) => match(e))?.[1] ?? "unknown";

const report = Object.groupBy(failures, f => bucket(f.error));
for (const [kind, list] of Object.entries(report)) console.log(kind.padEnd(21), list.map(f => f.test).join(", "));
''', 'Triage failures by error type'),
}

LANES = {
    'unwind': {'t': 'A thrown error travels down the call stack', 'code': 'function readConfig() { throw new ConfigError("missing url"); }\nfunction startSuite() {\n  try { readConfig(); }\n  finally { console.log("cleanup"); }\n}\ntry { startSuite(); }\ncatch (e) { console.log("caught", e.code); }', 'lanes': ['Call stack', 'Error in flight', 'Console'], 'tone': [2, 6, 4], 'steps': [{'l': 6, 'v': [['global', 'startSuite()'], [], []], 'm': 'The script calls startSuite inside a try block.'}, {'l': 3, 'v': [['global', 'startSuite()', 'readConfig()'], [], []], 'm': 'startSuite calls readConfig inside its own try block.'}, {'l': 1, 'v': [['global', 'startSuite()', 'readConfig()'], ['ConfigError: missing url'], []], 'm': 'throw creates the error and stops readConfig at once. No line after it runs.'}, {'l': 3, 'v': [['global', 'startSuite()'], ['ConfigError: missing url'], []], 'm': 'readConfig has no try, so its frame is removed and the error moves down to startSuite.'}, {'l': 4, 'v': [['global', 'startSuite()'], ['ConfigError: missing url'], ['cleanup']], 'm': 'startSuite has a try with only a finally. finally always runs, then the error keeps travelling.'}, {'l': 7, 'v': [['global'], [], ['cleanup', 'caught CONFIG']], 'm': 'The outer catch stops the error. The program carries on normally after it. With no catch at all, the error would reach the top and end the program.'}]},
}

PARTS = [
    part('types', '🧯', 'The error types and building your own', '''
<p>Every error has a <code>name</code>, a <code>message</code> and a <code>stack</code>. The built in types tell you what kind of mistake happened, which narrows the search before you read a single line of code.</p>
[[builtin]]
<p>For your own code, a small hierarchy of error classes lets callers catch a whole family or one exact kind. Give each error a stable <code>code</code> for programs to check, a human <code>message</code>, and a <code>cause</code> when you wrap a lower level error.</p>
[[custom]]
<p>When an error is thrown, the engine stops the current function and looks for a <code>catch</code> in it. If there is none, it removes that function from the call stack and looks in the caller, and so on. This is called <b>unwinding</b> the stack. Every <code>finally</code> on the way still runs, which is why clean up code belongs there.</p>
<div class="viz" data-viz="lanes" data-k="unwind"></div>
<div class="tip">Check the <code>code</code> or the class, never the message text. Messages change with translations and wording fixes, codes do not.</div>
''', qa=True, qa_why='Test frameworks, HTTP clients and drivers all throw typed errors, and good helpers in a test framework do the same.',
        kw=['Error', 'TypeError', 'ReferenceError', 'RangeError', 'SyntaxError', 'URIError', 'AggregateError', 'custom error', 'extends Error', 'error code', 'cause', 'instanceof', 'new.target']),
    part('async', '⏳', 'Errors in async code', '''
<p>A <code>try</code> block only sees errors thrown while it is on the call stack. A callback that runs later has left it already. With <code>await</code>, a rejected promise turns into an ordinary throw at that line, which is the main reason async and await made error handling simple.</p>
[[async-errors]]
<p>A rejected promise that nobody handles is an <b>unhandled rejection</b>. Since Node.js 15 it stops the process with exit code 1, which is good: the bug cannot hide.</p>
[[unhandled]]
[[handlers]]
<div class="qa-box">The most common cause of an unhandled rejection in tests is a missing <code>await</code> before a Playwright action or an API call. The test may even pass, then a later test fails with a strange error. Turn on the <code>no-floating-promises</code> lint rule.</div>
''', qa=['Playwright', 'Node.js'], qa_why='Missing awaits and unhandled rejections cause failures that appear in the wrong test, the hardest kind to debug.',
        kw=['async error', 'try catch', 'await', 'rejected promise', 'unhandledRejection', 'uncaughtException', 'finally', 'exit code', 'floating promise', 'process.on']),
    part('values', '📬', 'Throw or return: errors as values', '''
<p>Throwing is right for things that should never happen. For failures you expect, such as a user typing a bad coupon, returning a result object keeps the flow simple and forces the caller to look at both cases.</p>
[[result]]
<div class="note">A good rule: validation and parsing of outside input return results, while broken assumptions inside your own code throw. Never use an empty <code>catch {}</code>, which hides the very information you will need later.</div>
''', kw=['result object', 'errors as values', 'throw vs return', 'validation', 'expected failure', 'empty catch']),
    part('debugging', '🔎', 'Debugging tools', '''
<p><code>console.log</code> is fine for a quick look, but it hides deep objects and its output is easy to misread. Node.js gives you precise tools for inspecting values.</p>
[[inspect]]
<p>For anything harder, use a real debugger. You can pause on any line, look at every variable, step into functions and set <b>conditional breakpoints</b> that stop only when, for example, <code>order.total &lt; 0</code>. <b>Logpoints</b> print a message without changing the code.</p>
[[debugger]]
<div class="qa-box">The Playwright <b>trace viewer</b> is the best debugger for a failed UI test: it shows every action, a DOM snapshot before and after, the network calls and the console, all from a CI run you cannot reproduce on your laptop.</div>
''', qa=['Playwright', 'Vitest'], qa_why='The Inspector and trace viewer turn a red CI run into a step by step replay of what the browser saw.',
        kw=['debugging', 'console.table', 'console.dir', 'util.inspect', 'console.count', 'console.assert', '--inspect', '--inspect-brk', 'breakpoint', 'conditional breakpoint', 'logpoint', 'debugger statement', 'PWDEBUG', 'trace viewer', 'VS Code debugger']),
    part('logging', '🪵', 'Structured logging', '''
<p>Plain text logs are hard to search across many servers or parallel tests. <b>Structured logs</b> write one JSON object per line with a level, a message and fields. Tools such as pino in Node.js, and log platforms such as Grafana Loki, Datadog or ELK, filter them by any field.</p>
[[als]]
<p><code>AsyncLocalStorage</code> keeps a value, such as a request id or the current test name, attached to all async work started inside <code>context.run</code>. That is how a log line deep in a helper still knows which request or test it belongs to.</p>
''', qa=True, qa_why='Attaching a test id or request id to every log line is how you find the server logs that match one failed test.',
        kw=['structured logging', 'JSON logs', 'log levels', 'pino', 'request id', 'correlation id', 'AsyncLocalStorage', 'context', 'observability']),
    part('sourcemaps', '🗺️', 'Source maps', '''
<p>TypeScript, bundlers and minifiers change your code before it runs, so stack traces point at generated files. A <b>source map</b> is a file that maps each generated position back to the original line. Browsers use them automatically in DevTools. Node.js uses them with <code>--enable-source-maps</code>.</p>
[[sourcemaps]]
<div class="tip">Upload source maps to your error tracker, such as Sentry, so production errors show the real file and line. Keep them off the public web server if your source code is private.</div>
''', kw=['source map', 'sourceMap', '--enable-source-maps', 'minified code', 'stack trace', 'TypeScript', 'Sentry']),
    part('scenario', '🎬', 'Real world scenario: triage a red pipeline', '''
<div class="scenario"><b>The situation</b>The nightly run has five failures. Before anyone opens a debugger, the team wants to know which failures are the product, which are the tests and which are the environment.</div>
[[scenario]]
<p>Error names and messages carry enough signal to sort most failures automatically. Connection errors and 5xx responses point at the environment, timeouts at timing or locators, assertion errors at the product, and TypeErrors in test code at the tests themselves. Posting this summary to the team chat saves the first half hour of every morning.</p>
''', qa=True, kw=['triage', 'test failure analysis', 'AssertionError', 'TimeoutError', 'ECONNREFUSED', 'environment issue', 'product bug', 'test bug', 'nightly run']),
]

INFO = {'title': 'When things go wrong', 'panels': [
    panel([['e', '🧯'], ['t', 'class HttpError extends AppError', {'b': 1, 'size': 11}]], 'Typed errors', 'A class and a code for each kind.', 'Wrap with cause, keep every detail.'),
    panel([['e', '⏳'], ['t', 'await or .catch', {'b': 1}]], 'Async errors', 'try only sees what it awaits.', 'Unhandled rejections stop Node.js.'),
    panel([['e', '🔎'], ['t', 'debugger;', {'b': 1}]], 'Real debuggers', 'Pause, look, step.', 'Trace viewer for UI tests.'),
    panel([['e', '🪵'], ['t', '{"level":"info","requestId":…}', {'b': 1, 'size': 11}]], 'Structured logs', 'JSON lines with ids.', 'Find every line of one request.')],
    'remember': 'Throw typed errors with a code and cause, await everything, and log JSON with an id you can search.'}

REAL = [
    ['🧾', 'A payments API', 'Gave every error a stable code such as CARD_DECLINED. Its client apps and the API tests check codes, so rewording messages never breaks anything.'],
    ['🌙', 'A nightly suite', 'Bucketed failures by error type and posted the summary to chat. Environment failures went to the platform team, product bugs to developers.'],
    ['🔗', 'A microservice team', 'Added a request id with AsyncLocalStorage and found a slow checkout by searching one id across five services.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers errors in depth, async errors and unhandled rejections, errors as values, debugging tools, structured logging and source maps.',
        'यह अध्याय errors, async errors और unhandled rejections, errors as values, debugging tools, structured logging और source maps सिखाता है।',
        'ಈ ಅಧ್ಯಾಯ errors, async errors, unhandled rejections, debugging tools, structured logging ಮತ್ತು source maps ಕಲಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ errors, async errors, unhandled rejections, debugging tools, structured logging ଓ source maps ଶିଖାଏ।',
        'يتناول هذا الفصل الأخطاء بعمق وأخطاء الشيفرة غير المتزامنة وأدوات التصحيح والسجلات المنظمة وخرائط المصدر.',
        'Dieses Kapitel behandelt Fehler im Detail, asynchrone Fehler, Debugging-Werkzeuge, strukturiertes Logging und Source Maps.'),
    say('types', 'Error types', 'Each built in error type points at a kind of mistake. Your own errors should have a class, a stable code and a cause when they wrap another error.',
        'हर built in error type एक तरह की गलती बताता है। अपने errors में class, stable code और cause रखें।',
        'ಪ್ರತಿ built in error type ಒಂದು ರೀತಿಯ ತಪ್ಪು ತೋರಿಸುತ್ತದೆ. ನಿಮ್ಮ errors ಗೆ class, code ಮತ್ತು cause ಇರಲಿ.',
        'ପ୍ରତ୍ୟେକ built in error type ଗୋଟିଏ ପ୍ରକାର ଭୁଲ ଦେଖାଏ। ନିଜ errors ରେ class, code ଓ cause ରଖନ୍ତୁ।',
        'كل نوع خطأ مدمج يشير إلى نوع من الأخطاء. اجعل لأخطائك صنفًا ورمزًا ثابتًا وسببًا عند تغليف خطأ آخر.',
        'Jeder eingebaute Fehlertyp zeigt eine Art von Fehler. Eigene Fehler brauchen eine Klasse, einen Code und eine Ursache.'),
    say('async', 'Async errors', 'try only catches what it awaits. A promise nobody handles is an unhandled rejection, and Node stops with exit code one.',
        'try केवल वही पकड़ता है जिसे वह await करता है। कोई promise handle न हो तो Node exit code एक के साथ रुकता है।',
        'try ತಾನು await ಮಾಡಿದ್ದನ್ನು ಮಾತ್ರ ಹಿಡಿಯುತ್ತದೆ. Handle ಆಗದ promise ಇದ್ದರೆ Node ನಿಲ್ಲುತ್ತದೆ.',
        'try କେବଳ await କରିଥିବା ଧରେ। Handle ହୋଇନଥିବା promise ଥିଲେ Node ବନ୍ଦ ହୁଏ।',
        'لا يلتقط try إلا ما ينتظره بـ await. الوعد المرفوض بلا معالجة يوقف Node برمز خروج واحد.',
        'try fängt nur, was es mit await abwartet. Eine unbehandelte Ablehnung beendet Node mit Exit-Code eins.'),
    say('values', 'Errors as values', 'Return a result object for failures you expect, such as bad input, and throw only for things that should never happen.',
        'अपेक्षित failures जैसे गलत input के लिए result object लौटाएं, और केवल असंभव चीज़ों पर throw करें।',
        'ನಿರೀಕ್ಷಿತ failures ಗೆ result object ಹಿಂದಿರುಗಿಸಿ, ಅಸಾಧ್ಯ ವಿಷಯಗಳಿಗೆ ಮಾತ್ರ throw ಮಾಡಿ.',
        'ଆଶା କରାଯାଉଥିବା failures ପାଇଁ result object ଫେରାନ୍ତୁ, କେବଳ ଅସମ୍ଭବ କଥାରେ throw କରନ୍ତୁ।',
        'أعد كائن نتيجة للأخطاء المتوقعة مثل المدخلات الخاطئة، وارمِ الاستثناء فقط لما لا يجب أن يحدث.',
        'Gib für erwartete Fehler wie falsche Eingaben ein Ergebnisobjekt zurück und wirf nur bei Unmöglichem.'),
    say('debugging', 'Debugging', 'Use util inspect, console table and console dir to see values clearly, and a real debugger with breakpoints for harder problems.',
        'Values साफ देखने के लिए util inspect, console table और console dir, और कठिन समस्याओं के लिए breakpoints वाला debugger इस्तेमाल करें।',
        'Values ನೋಡಲು util inspect, console table ಬಳಸಿ, ಕಠಿಣ ಸಮಸ್ಯೆಗೆ breakpoints ಇರುವ debugger.',
        'Values ଦେଖିବାକୁ util inspect, console table ବ୍ୟବହାର କରନ୍ତୁ, କଠିନ ସମସ୍ୟାରେ debugger।',
        'استخدم util.inspect وconsole.table وconsole.dir لرؤية القيم بوضوح، ومصححًا حقيقيًا بنقاط توقف للمشكلات الأصعب.',
        'Nutze util.inspect, console.table und console.dir für klare Werte und einen echten Debugger mit Haltepunkten.'),
    say('logging', 'Logging', 'Structured logs write one JSON object per line. AsyncLocalStorage keeps a request id attached to every await, so each line is easy to find.',
        'Structured logs हर line में एक JSON object लिखते हैं। AsyncLocalStorage हर await में request id साथ रखता है।',
        'Structured logs ಪ್ರತಿ ಸಾಲಿಗೆ ಒಂದು JSON object. AsyncLocalStorage request id ಅನ್ನು ಪ್ರತಿ await ಗೆ ಜೋಡಿಸುತ್ತದೆ.',
        'Structured logs ପ୍ରତି ଧାଡ଼ିରେ ଗୋଟିଏ JSON object। AsyncLocalStorage request id ପ୍ରତି await ରେ ରଖେ।',
        'السجلات المنظمة تكتب كائن JSON في كل سطر، وتحفظ AsyncLocalStorage معرف الطلب عبر كل await.',
        'Strukturierte Logs schreiben ein JSON-Objekt pro Zeile. AsyncLocalStorage hält die Request-ID über jedes await.'),
    say('sourcemaps', 'Source maps', 'Source maps map generated code back to your original lines. Node uses them with the enable source maps flag.',
        'Source maps बने हुए code को आपकी असली lines से जोड़ते हैं। Node इन्हें enable source maps flag से इस्तेमाल करता है।',
        'Source maps generated code ಅನ್ನು ಮೂಲ ಸಾಲುಗಳಿಗೆ ಜೋಡಿಸುತ್ತವೆ. Node flag ಮೂಲಕ ಬಳಸುತ್ತದೆ.',
        'Source maps generated code କୁ ମୂଳ ଧାଡ଼ି ସହ ଯୋଡ଼େ। Node flag ରେ ବ୍ୟବହାର କରେ।',
        'تربط خرائط المصدر الشيفرة المولدة بأسطرك الأصلية، ويستخدمها Node مع خيار enable source maps.',
        'Source Maps führen erzeugten Code auf deine Originalzeilen zurück. Node nutzt sie mit einem Schalter.'),
    say('scenario', 'Scenario', 'Sort failures by error type: connection errors are the environment, timeouts are timing, assertions are the product, TypeErrors are the tests.',
        'Failures को error type से बांटें: connection errors environment, timeouts timing, assertions product, TypeErrors tests।',
        'Failures ಅನ್ನು error type ನಿಂದ ವಿಂಗಡಿಸಿ: connection errors environment, timeouts timing, assertions product.',
        'Failures କୁ error type ରେ ଭାଗ କରନ୍ତୁ: connection errors environment, timeouts timing, assertions product।',
        'صنف الإخفاقات حسب نوع الخطأ: أخطاء الاتصال للبيئة، والمهلات للتوقيت، والتأكيدات للمنتج، وTypeError للاختبارات.',
        'Sortiere Fehler nach Typ: Verbindungsfehler sind die Umgebung, Timeouts das Timing, Assertions das Produkt.'),
    say('practice', 'Hands-on', 'Practise a custom error class, a safe JSON parser that returns a result, a retry that only retries the right errors, and a failure triage function.',
        'Custom error class, result लौटाने वाला safe JSON parser, सही errors पर retry और failure triage function का अभ्यास करें।',
        'Custom error class, safe JSON parser, ಸರಿಯಾದ errors ಗೆ retry ಮತ್ತು triage function ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Custom error class, safe JSON parser, ଠିକ୍ errors ରେ retry ଓ triage function ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على صنف خطأ مخصص ومحلل JSON آمن يعيد نتيجة وإعادة محاولة للأخطاء المناسبة فقط ودالة فرز للإخفاقات.',
        'Übe eine eigene Fehlerklasse, einen sicheren JSON-Parser, gezielte Wiederholungen und eine Triage-Funktion.'),
]

QUIZ = [
    quiz('e', 'Which error do you get from null.length?', ['TypeError', 'ReferenceError', 'RangeError', 'SyntaxError'], 0, 'Wrong kind of value.', 'Reading a property of null or undefined is a TypeError.'),
    quiz('e', 'What does finally do?', ['Runs after try and catch whether or not an error happened', 'Runs only on errors', 'Stops the error', 'Retries the try block'], 0, 'Always.', 'That makes it the place for clean up such as closing a browser.'),
    quiz('e', 'Which console method shows an array of objects as a grid?', ['console.table', 'console.dir', 'console.group', 'console.count'], 0, 'A table.', 'Handy for test results and API rows.'),
    quiz('m', 'Why set this.name = new.target.name in a base error class?', ['So every subclass reports its own class name', 'To make it faster', 'It is required by JavaScript', 'To hide the stack'], 0, 'Subclasses.', 'Otherwise every custom error prints as plain "Error".'),
    quiz('m', 'A function calls loadUser() inside try without await, and it rejects. What happens?', ['The catch block does not see it', 'catch handles it', 'It retries', 'Nothing ever'], 0, 'The promise is not awaited.', 'The rejection happens after the try block has finished.'),
    quiz('m', 'What does { cause } in new Error(msg, { cause }) give you?', ['The original error kept inside the new one', 'A retry count', 'A stack trace only', 'A status code'], 0, 'Wrapping.', 'Logs and inspect show both errors, so no detail is lost.'),
    quiz('m', 'Why check err.code instead of err.message?', ['Codes are stable while messages change', 'Messages are always empty', 'Codes are faster', 'Messages cannot be compared'], 0, 'Stability.', 'Rewording a message must never break a caller or a test.'),
    quiz('h', 'What does Node.js do by default with an unhandled rejection?', ['Prints it and exits with code 1', 'Ignores it', 'Retries it', 'Writes a warning only'], 0, 'Since Node.js 15.', 'Earlier versions only warned, which let bugs hide.'),
    quiz('h', 'What does AsyncLocalStorage give you?', ['A value that follows async work started inside run()', 'Browser local storage in Node', 'A database', 'A faster event loop'], 0, 'Context across awaits.', 'Used for request ids, user ids and test names in logs.'),
    quiz('h', 'What is a source map for?', ['Mapping generated code positions back to original source lines', 'Mapping URLs to routes', 'Drawing a site map', 'Compressing code'], 0, 'Stack traces.', 'It makes errors in compiled TypeScript point at the .ts line.'),
    quiz('x', 'A failure says "connect ECONNREFUSED 127.0.0.1:3000". Most likely cause?', ['The server under test is not running', 'An assertion is wrong', 'A locator is wrong', 'A TypeScript error'], 0, 'Connection refused.', 'Nothing is listening on that port, which is an environment problem.'),
    quiz('x', 'Which is the best use of AggregateError?', ['Reporting several failures together, as Promise.any does', 'Replacing all errors', 'Adding a stack', 'Catching syntax errors'], 0, 'Many at once.', 'Its errors property holds every inner error.'),
]

CALC = [
    calc('e', 'A suite has 5 failures: 2 environment, 1 timeout, 1 assertion, 1 TypeError. How many point at the product?', '1', 'Assertions.', ['Only the assertion failure is a possible product bug.']),
    calc('e', 'console.count("retry") is called 3 times. What number does the third call print?', '3', 'It counts calls with that label.', ['retry: 1, retry: 2, retry: 3.']),
    calc('m', 'util.inspect default depth is 2. An object nests 4 levels deep. How many levels are hidden behind [Object]?', '2', 'Shown levels are 0, 1 and 2.', ['Levels 3 and 4 are replaced by [Object].'], alt=['1']),
    calc('m', 'A retry helper tries 3 times. Each failing call takes 2 s and there is a 1 s wait between tries. How long until the final failure, in seconds?', '8', 'Calls plus waits.', ['<span class="eq">3 × 2 + 2 × 1 = 8</span>']),
    calc('m', 'Out of 200 nightly failures, 120 were environment problems. What percent is that?', '60', 'Part over whole.', ['<span class="eq">120 ÷ 200 × 100 = 60</span>']),
    calc('h', 'A 5xx retry policy retries 503 and 429 but not 400 or 404. Of the statuses 400, 404, 429, 500, 503, how many are retried if 5xx also includes 500?', '3', '429 plus the 5xx ones.', ['429, 500 and 503 are retried.', '400 and 404 are not.']),
    calc('h', 'Exponential backoff waits 100 ms, then doubles each time. What is the total wait over 4 retries, in ms?', '1500', '100 + 200 + 400 + 800.', ['<span class="eq">100 + 200 + 400 + 800 = 1500</span>']),
    calc('x', 'Two requests log 3 lines each, interleaved. With a request id on every line, how many lines does a search for one id return?', '3', 'Only its own lines.', ['The id filters exactly that request out of the 6 lines.']),
]

EX = [
    ex('httperror', 'e', 'A custom error class', '<p>Write a class <code>HttpError</code> that extends <code>Error</code>. <code>new HttpError(404, "/cart")</code> must have <code>name</code> "HttpError", <code>status</code> 404 and <code>message</code> "HTTP 404 from /cart".</p>',
       'class HttpError extends Error {\n  \n}\n',
       [('(() => { const e = new HttpError(404, "/cart"); return [e.name, e.status, e.message, e instanceof Error]; })()', ['HttpError', 404, 'HTTP 404 from /cart', True])],
       'class HttpError extends Error {\n  constructor(status, url) {\n    super(`HTTP ${status} from ${url}`);\n    this.name = "HttpError";\n    this.status = status;\n  }\n}', hint='Call <code>super(message)</code> first, then set the extra fields.', why='Subclasses of Error keep the stack trace and work with instanceof.'),
    ex('safejson', 'm', 'Parse JSON without throwing', '<p>Write <code>safeJson(text)</code> that returns <code>{ ok: true, value }</code> for valid JSON and <code>{ ok: false, error }</code> with the error message for invalid JSON.</p>',
       'function safeJson(text) {\n  \n}\n',
       [('safeJson(\'{"a":1}\')', {'ok': True, 'value': {'a': 1}}), ('safeJson("<html>").ok', False), ('typeof safeJson("{bad").error', 'string')],
       'function safeJson(text) {\n  try {\n    return { ok: true, value: JSON.parse(text) };\n  } catch (e) {\n    return { ok: false, error: e.message };\n  }\n}', hint='Wrap <code>JSON.parse</code> in try and catch and return an object from both branches.', why='An API test can now report "the body was HTML, not JSON" instead of crashing.'),
    ex('retryif', 'h', 'Retry only the right errors', '<p>Write <code>async retryIf(fn, shouldRetry, times)</code>. Call <code>fn()</code> up to <code>times</code> times. If it throws and <code>shouldRetry(error)</code> is true and tries are left, try again, otherwise rethrow at once. Return the first successful result.</p>',
       'async function retryIf(fn, shouldRetry, times) {\n  \n}\n',
       [('(async () => { let n = 0; const r = await retryIf(async () => { if (++n < 3) throw { status: 503 }; return "ok"; }, e => e.status >= 500, 5); return [r, n]; })()', ['ok', 3]),
        ('(async () => { let n = 0; try { await retryIf(async () => { n++; throw { status: 400 }; }, e => e.status >= 500, 5); } catch (e) { return [e.status, n]; } })()', [400, 1]),
        ('(async () => { let n = 0; try { await retryIf(async () => { n++; throw { status: 503 }; }, () => true, 2); } catch (e) { return [e.status, n]; } })()', [503, 2])],
       'async function retryIf(fn, shouldRetry, times) {\n  for (let i = 1; ; i++) {\n    try {\n      return await fn();\n    } catch (e) {\n      if (i >= times || !shouldRetry(e)) throw e;\n    }\n  }\n}', hint='A loop with try and catch. Rethrow when you are out of tries or the error is not retryable.', why='Retrying a 400 can never help and hides real bugs. Only retry errors that can go away by themselves.'),
    ex('triage', 'x', 'Triage a failure', '<p>Write <code>triage(error)</code> that returns <code>"environment"</code> when the message contains ECONNREFUSED or ENOTFOUND or "HTTP 5", <code>"timing"</code> when the name is TimeoutError, <code>"product"</code> when the name is AssertionError, <code>"test"</code> for TypeError or ReferenceError, and <code>"unknown"</code> otherwise. Check the rules in that order.</p>',
       'function triage(error) {\n  \n}\n',
       [('triage({ name: "Error", message: "connect ECONNREFUSED 127.0.0.1:3000" })', 'environment'), ('triage({ name: "TimeoutError", message: "Timeout 5000ms" })', 'timing'),
        ('triage({ name: "AssertionError", message: "HTTP 500 expected 200" })', 'environment'), ('triage({ name: "AssertionError", message: "1 !== 2" })', 'product'),
        ('triage({ name: "TypeError", message: "x is undefined" })', 'test'), ('triage({ name: "Error", message: "?" })', 'unknown')],
       'function triage(error) {\n  const { name, message } = error;\n  if (/ECONNREFUSED|ENOTFOUND|HTTP 5/.test(message)) return "environment";\n  if (name === "TimeoutError") return "timing";\n  if (name === "AssertionError") return "product";\n  if (name === "TypeError" || name === "ReferenceError") return "test";\n  return "unknown";\n}',
       hint='Use a regular expression for the message test and simple comparisons for the names.', why='The third test shows why order matters: an assertion that failed because of a 500 is still an environment problem.'),
]

T = {
    'slug': 'js-errors-debugging', 'title': 'Errors, debugging and logging', 'short': 'Errors and debugging', 'emoji': '🧯', 'module': MODULE, 'minutes': 18,
    'lead': 'Handle failure like an expert: the built in error types, custom errors with codes and causes, errors in async code and unhandled rejections, when to return a result instead of throwing, real debuggers and the Playwright trace viewer, structured logs with request ids, and source maps.',
    'desc': 'JavaScript errors and debugging: error types, custom errors, error cause, AggregateError, async errors, unhandled rejections, result objects, util.inspect, debugger, Playwright trace viewer, structured logging, AsyncLocalStorage and source maps.',
    'summary': 'Built in error types and custom error classes with codes and causes, errors in callbacks and promises, unhandled rejections and global handlers, errors as values, inspecting values and starting the debuggers, JSON logs with a request id through AsyncLocalStorage, source maps for TypeScript stack traces, and sorting test failures by error type.',
    'keywords': ['errors', 'custom error', 'error cause', 'AggregateError', 'unhandled rejection', 'uncaughtException', 'debugging', 'debugger', 'trace viewer', 'util.inspect', 'structured logging', 'AsyncLocalStorage', 'source maps', 'triage', 'interview'],
    'qa_intro': 'A tester spends much of the day reading failures. This chapter shows how errors are built, how to debug them fast, and how to sort a red pipeline into product, test and environment problems.',
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
