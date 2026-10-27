# Chapter 25c: what is new in TypeScript from 5.0 to 7.0, each feature type checked by the real compiler and run on Node.js,
# with what it is good for at work: const type parameters, using, import attributes, NoInfer, inferred type predicates,
# regex checks, truthiness checks, iterator helpers, the ES2025 and esnext libraries in 6.0, and the native TypeScript 7.
import json
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg, ts

MODULE = ('🔷', 'TypeScript', 'ts', 'TypeScript from the first type to generics, advanced types, typed projects and test automation written in TypeScript.')

CODES = {
    'constparams': ts('''
// TypeScript 5.0: a const type parameter infers literal types without "as const" at every call
function roles<const T extends readonly string[]>(list: T): T { return list; }
function rolesOld<T extends readonly string[]>(list: T): T { return list; }

const exact = roles(["admin", "qa", "viewer"]);     // readonly ["admin", "qa", "viewer"]
const loose = rolesOld(["admin", "qa", "viewer"]);  // string[]

type Role = (typeof exact)[number];                 // "admin" | "qa" | "viewer"
const me: Role = "qa";
console.log(exact, loose, me);

const typo: Role = "qaa";                           // caught, because the literals were kept
''', 'const type parameters (5.0)', errors=1),
    'using': ts('''
// TypeScript 5.2 and Node.js: using calls [Symbol.dispose]() when the block ends, even after an error
function openDb(name: string) {
  console.log(`open ${name}`);
  return { name, query: (sql: string) => `${name}: ${sql}`, [Symbol.dispose]() { console.log(`close ${name}`); } };
}

async function startBrowser() {
  console.log("browser started");
  return { title: async () => "Shop", async [Symbol.asyncDispose]() { console.log("browser closed"); } };
}

function report() {
  using main = openDb("orders");
  using audit = openDb("audit");
  console.log(main.query("SELECT 1"));
  throw new Error("assertion failed");               // both connections still close, newest first
}

try { report(); } catch (e) { console.log("test failed:", (e as Error).message); }

{
  await using browser = await startBrowser();       // await using waits for an async cleanup
  console.log("title:", await browser.title());
}
console.log("done");
''', 'using and await using: cleanup that cannot be forgotten (5.2)'),
    'attributes': ts('''
// TypeScript 5.3: import attributes tell the runtime what kind of file it is loading
import users from "./users.json" with { type: "json" };

const admins = users.filter((u) => u.role === "admin");   // the JSON's shape is inferred
console.log(admins.map((u) => u.name));
console.log(users[0]?.email.toUpperCase());

console.log(users[0]?.phone);                             // no such field in the file
''', 'Import attributes for JSON test data (5.3)', errors=1, run=False,
        more={'src/users.json': json.dumps([{'name': 'Asha', 'email': 'asha@shop.test', 'role': 'admin'}, {'name': 'Ravi', 'email': 'ravi@shop.test', 'role': 'customer'}], indent=2)},
        options={'resolveJsonModule': True}),
    'noinfer': ts('''
// TypeScript 5.4: NoInfer<T> stops one argument from deciding what T is
function pickBrowser<T extends string>(supported: T[], fallback: NoInfer<T>): T {
  const wanted = process.env.BROWSER as T | undefined;
  return wanted && supported.includes(wanted) ? wanted : fallback;
}
console.log(pickBrowser(["chromium", "firefox", "webkit"], "chromium"));

// Narrowing now survives inside callbacks created after the last assignment
function label(id: string | number) {
  if (typeof id === "number") id = `#${id}`;
  return ["a", "b"].map((s) => `${s}-${id.toUpperCase()}`);   // id is known to be a string here
}
console.log(label(7));

pickBrowser(["chromium", "firefox"], "safari");     // without NoInfer, T would quietly widen to include "safari"
''', 'NoInfer and narrowing in closures (5.4)', errors=1),
    'predicates': ts('''
// TypeScript 5.5: filter with a simple check now narrows the array type by itself
const rows = [{ id: 1, total: 450 }, null, { id: 2, total: 99 }, undefined];

const present = rows.filter((r) => r != null);      // { id: number; total: number }[]
console.log(present.map((r) => r.total));           // no "possibly null" error any more

// The inferred function is a real type predicate you can reuse
const isBig = (r: { total: number } | null) => r !== null && r.total > 100;
const isRow = (r: { id: number; total: number } | null | undefined) => r != null;
const checked = rows.filter(isRow);
console.log(checked.length, isBig(rows[0] ?? null));
''', 'Inferred type predicates (5.5)'),
    'regex': ts('''
// TypeScript 5.5 checks the syntax of regular expression literals
const orderId = /^ORD-(?<num>\\d{6})$/;
const match = "ORD-104233".match(orderId);
console.log(match?.groups?.num);

const broken = /^ORD-(?<num>\\d{6})\\k<numb>$/;     // a back reference to a group that does not exist
const flags = /cart/gg;                              // a flag written twice
''', 'Regular expressions are checked too (5.5)', errors=2, run=False),
    'truthy': ts('''
// TypeScript 5.6: conditions that are always true or always false are errors
function isLoggedIn(): boolean { return true; }

if (isLoggedIn()) console.log("called: fine");
if (isLoggedIn) console.log("forgot the ()");        // a function is always truthy

const role = "customer";
if (/admin/) console.log("forgot .test(role), so this always runs for " + role);   // a regex literal is always truthy

// TypeScript 5.6 also types the iterator helper methods that Node.js supports
const fast = [120, 455, 80, 999, 300].values().filter((ms) => ms < 400).map((ms) => `${ms} ms`).toArray();
console.log(fast);
''', 'Always truthy checks and iterator helpers (5.6)', errors=2),
    'uninit': ts('''
// TypeScript 5.7: a variable that is never assigned anywhere is now reported inside functions too
let total: number;
function report() { return total.toFixed(2); }       // before 5.7 this compiled, because it is inside a function

let baseURL: string;
function url(path: string) { return baseURL + path; }   // fine: baseURL is assigned below before use
baseURL = "http://localhost:3000";
console.log(url("/health"));

try { console.log(report()); } catch (e) { console.log("crashed:", (e as Error).message); }
''', 'Variables that are never initialised (5.7)', errors=1),
    'defer': show('''
// TypeScript 5.9: import defer loads the module but runs it only on first use
import defer * as reports from "./heavy-reports.ts";

export function onExportClick() {
  return reports.buildPdf();        // heavy-reports.ts runs here, the first time, not at startup
}
''', 'import defer (5.9)', lang='ts', note='Needs a runtime that supports the import defer proposal, so it is not run here'),
    'ts60': ts('''
// TypeScript 6.0: types for ES2025 and newer runtime features that Node.js already has
const hits = new Map<string, number>();
for (const word of ["pass", "fail", "pass", "pass"]) {
  hits.set(word, hits.getOrInsert(word, 0) + 1);    // Map.getOrInsert (the "upsert" proposal)
}
console.log(hits);

const userInput = "price (in $)?";
const safe = new RegExp(RegExp.escape(userInput));  // escape text before putting it in a regex
console.log(safe.test("What is the price (in $)?"));

// The Temporal date and time API (esnext.temporal types)
const release = Temporal.PlainDate.from("2026-03-23");
const nextCheck = release.add({ months: 6 });
console.log(release.toString(), "->", nextCheck.toString(), release.until(nextCheck).total({ unit: "days" }), "days");
''', 'Map.getOrInsert, RegExp.escape and Temporal (6.0)'),
    'ts70': test({'package.json': pkg('ts7', 'module'),
                  'tsconfig.json': json.dumps({'compilerOptions': {'target': 'esnext', 'module': 'nodenext', 'strict': True, 'noEmit': True, 'allowImportingTsExtensions': True, 'types': ['node']}, 'include': ['src']}, indent=2),
                  'src/a.ts': 'export const a: number = 1;\n', 'src/b.ts': 'import { a } from "./a.ts";\nexport const b: string = a;\n'},
                 'npx tsc --version && echo "--- check with 2 parallel checkers ---" && npx tsc -p . --checkers 2 --pretty false; echo "--- target es5 is gone ---" && npx tsc -p . --target es5 --pretty false 2>&1 | head -1',
                 'TypeScript 7.0, the native compiler', show=['src/b.ts'],
                 shown_cmd='npx tsc --version\nnpx tsc -p . --checkers 2\nnpx tsc -p . --target es5'),
}

LANES = {
    'dispose': {'t': 'What using does when a test fails',
                'code': 'function report() {\n  using main = openDb("orders");\n  using audit = openDb("audit");\n  console.log(main.query("SELECT 1"));\n  throw new Error("assertion failed");\n}',
                'lanes': ['Running', 'Open resources', 'Cleanup queue', 'Console'], 'tone': [2, 4, 3, 1],
                'steps': [{'l': 1, 'v': [['report()'], [], [], []], 'm': 'The function starts. Nothing is open yet.'},
                          {'l': 2, 'v': [['report()'], ['orders'], ['close orders'], ['open orders']], 'm': 'using opens the first connection and remembers to dispose of it when the block ends.'},
                          {'l': 3, 'v': [['report()'], ['orders', 'audit'], ['close audit', 'close orders'], ['open orders', 'open audit']], 'm': 'The second one goes on top of the cleanup queue. Cleanup runs newest first, like a stack.'},
                          {'l': 4, 'v': [['report()'], ['orders', 'audit'], ['close audit', 'close orders'], ['open orders', 'open audit', 'orders: SELECT 1']], 'm': 'The work runs normally.'},
                          {'l': 5, 'v': [['throwing'], [], [], ['open orders', 'open audit', 'orders: SELECT 1', 'close audit', 'close orders']], 'm': 'An error is thrown. Before it leaves the function, both resources are disposed, audit first. No try and finally was written, and none can be forgotten.'}]},
}

DG = {
    'path': {'t': 'From TypeScript 5 to the native TypeScript 7', 'w': 900, 'h': 300, 'mw': 640,
        'n': [['t5', 30, 110, 200, 70, 'TypeScript 5.x', {'c': 1, 'sub': '2023 to 2025'}],
              ['t6', 340, 110, 220, 70, 'TypeScript 6.0', {'c': 3, 'sub': 'March 2026, last JavaScript based'}],
              ['t7', 670, 110, 200, 70, 'TypeScript 7.0', {'c': 4, 'sub': 'native, written in Go'}],
              ['dep', 340, 220, 220, 56, 'Deprecation warnings', {'c': 5, 'sub': 'ignoreDeprecations: "6.0"'}],
              ['api', 670, 220, 200, 56, '@typescript/typescript6', {'c': 2, 'sub': 'old API until 7.1'}],
              ['speed', 670, 20, 200, 56, '8 to 12 times faster', {'c': 4, 'sub': 'VS Code: 125.7 s to 10.6 s'}]],
        'e': [['t5', 't6', {'t': 'upgrade', 'id': 'p1'}], ['t6', 't7', {'t': 'then', 'id': 'p2'}], ['t6', 'dep', {'id': 'p3'}], ['t7', 'api', {'id': 'p4', 'd': 1}], ['t7', 'speed', {'id': 'p5'}]],
        'st': [[['t5'], 'TypeScript 5 added most of the features in this chapter, one release every few months.'],
               [['t6', 'p1'], 'TypeScript 6.0 is the bridge. It changes the defaults to strict, esnext modules and target es2025, and it is the last version written in JavaScript.'],
               [['dep', 'p3'], 'It deprecates old options such as target es5, baseUrl, moduleResolution node10 and outFile. They can be silenced for a while with ignoreDeprecations set to "6.0".'],
               [['t7', 'p2'], 'TypeScript 7.0 is the same language, rewritten in Go. Everything deprecated in 6.0 is now a hard error.'],
               [['speed', 'p5'], 'Native code and parallel checking make builds typically 8 to 12 times faster. New flags --checkers, --builders and --singleThreaded control the parallelism.'],
               [['api', 'p4'], 'Tools that call the compiler from JavaScript can keep using the 6.0 compiler through the @typescript/typescript6 package until a stable API arrives in 7.1.']]},
}

PARTS = [
    part('overview', '🗓️', 'Three years of TypeScript in one page', '''
<p>TypeScript ships a new version every few months, and each brings small features that save real time. This chapter goes release by release from 5.0 (2023) to 7.0 (2026). Every example is checked by the TypeScript 7 compiler and run on Node.js 26.</p>
<div class="viz" data-viz="flow" data-k="path"></div>
<div class="tw"><table class="jt"><tr><th>Version</th><th>Headline features</th></tr>
<tr><td>5.0</td><td>standard decorators, const type parameters, extends with several configs, moduleResolution bundler, verbatimModuleSyntax</td></tr>
<tr><td>5.1 to 5.3</td><td>unrelated getter and setter types, <code>using</code> declarations, decorator metadata, import attributes</td></tr>
<tr><td>5.4 and 5.5</td><td>NoInfer, narrowing in closures, inferred type predicates, regex checking, isolatedDeclarations</td></tr>
<tr><td>5.6 and 5.7</td><td>always truthy checks, iterator helper types, never initialised variables, rewriteRelativeImportExtensions</td></tr>
<tr><td>5.8 and 5.9</td><td>erasableSyntaxOnly, require of ES modules under nodenext, import defer, module node20, a short tsc --init</td></tr>
<tr><td>6.0</td><td>new defaults, target es2025, Temporal and upsert types, #/ subpath imports, many deprecations</td></tr>
<tr><td>7.0</td><td>native compiler in Go, parallel checking, deprecated options removed</td></tr></table></div>
''', kw=['TypeScript releases', 'TypeScript 5', 'TypeScript 6', 'TypeScript 7', 'release history', 'what is new', 'upgrade']),
    part('ts50', '🔒', 'TypeScript 5.0: const type parameters', '''
<p>Before 5.0, a generic function that should keep exact strings needed callers to write <code>as const</code>. A <code>const</code> type parameter does it for every caller. 5.0 also introduced standard decorators, covered in the projects chapter.</p>
[[constparams]]
''', kw=['const type parameters', 'TypeScript 5.0', 'literal inference', 'as const', 'standard decorators']),
    part('ts52', '🧹', 'TypeScript 5.2 and 5.3: using and import attributes', '''
<p><code>using</code> is explicit resource management from a JavaScript proposal that TypeScript supports since 5.2 and Node.js runs natively. When the block ends, normally or by an error, the object's <code>[Symbol.dispose]()</code> runs. For test code that opens browsers, database connections or temp folders, this replaces fragile try and finally blocks.</p>
[[using]]
<div class="viz" data-viz="lanes" data-k="dispose"></div>
<p>TypeScript 5.3 added <b>import attributes</b>. <code>with { type: "json" }</code> tells the runtime the file is JSON, which Node requires for JSON imports, and TypeScript infers the type of the data from the file.</p>
[[attributes]]
''', qa=True, qa_why='Browsers, pages and connections that are always closed, even when an assertion fails, stop leaks that slow down whole test runs.',
        kw=['using', 'await using', 'Symbol.dispose', 'Symbol.asyncDispose', 'explicit resource management', 'TypeScript 5.2', 'import attributes', 'with type json', 'TypeScript 5.3']),
    part('ts54', '🎯', 'TypeScript 5.4 and 5.5: smarter inference', '''
<p><code>NoInfer&lt;T&gt;</code> marks an argument that must match T but must not help decide what T is. Without it, a wrong default such as "safari" would simply widen T to include it. 5.4 also keeps narrowing inside callbacks created after the last change to a variable.</p>
[[noinfer]]
<p>TypeScript 5.5 infers <b>type predicates</b>: <code>rows.filter(r =&gt; r != null)</code> finally gives an array without null. It also checks regular expression literals, so typos in patterns are found before a test runs.</p>
[[predicates]]
[[regex]]
''', qa=True, qa_why='Filtering test data and writing locator or log patterns are daily work. These checks catch the mistakes early.',
        kw=['NoInfer', 'TypeScript 5.4', 'closure narrowing', 'inferred type predicates', 'filter', 'TypeScript 5.5', 'regular expression checking', 'named groups']),
    part('ts56', '🚨', 'TypeScript 5.6 to 5.9: fewer silent mistakes', '''
<p>5.6 reports conditions that can never be false, such as a function used without calling it. This is a classic bug in test helpers: <code>if (isLoggedIn)</code> is always true. 5.6 also typed the <b>iterator helper</b> methods such as <code>filter</code>, <code>map</code> and <code>toArray</code> on iterators.</p>
[[truthy]]
<p>5.7 reports variables that are never assigned anywhere, even when they are used inside a function, where older versions stayed quiet. 5.8 added <code>erasableSyntaxOnly</code> for running .ts files directly, and 5.9 added <code>import defer</code>, which loads a module but runs it only when first used.</p>
[[uninit]]
[[defer]]
''', kw=['always truthy', 'TypeScript 5.6', 'iterator helpers', 'never initialized', 'TypeScript 5.7', 'erasableSyntaxOnly', 'TypeScript 5.8', 'import defer', 'TypeScript 5.9']),
    part('ts60', '🌉', 'TypeScript 6.0: the bridge release', '''
<p>TypeScript 6.0 (March 2026) is the last version of the compiler written in JavaScript. It changes the defaults of a new project to <code>strict: true</code>, <code>module: "esnext"</code> and <code>target: "es2025"</code>, and adds types for runtime features that Node.js and browsers already ship.</p>
[[ts60]]
<p>6.0 also deprecates options that TypeScript 7 removes: <code>target: "es5"</code>, <code>downlevelIteration</code>, <code>moduleResolution</code> node10 and classic, the amd, umd and systemjs module formats, <code>baseUrl</code>, <code>outFile</code>, and the old <code>module Foo {}</code> namespace syntax. <code>"ignoreDeprecations": "6.0"</code> silences the warnings while a project migrates.</p>
''', qa=True, qa_why='Temporal ends date bugs in test data, and RegExp.escape makes locators built from user text safe.',
        kw=['TypeScript 6.0', 'es2025', 'Temporal', 'Map.getOrInsert', 'upsert', 'RegExp.escape', 'deprecations', 'ignoreDeprecations', 'new defaults']),
    part('ts70', '🚀', 'TypeScript 7.0: the native compiler', '''
<p>TypeScript 7.0 is the compiler ported to Go. The language is the same, but builds are typically 8 to 12 times faster, and the VS Code code base went from 125.7 seconds to 10.6 seconds. Checking can run on several CPU cores.</p>
[[ts70]]
<div class="tw"><table class="jt"><tr><th>New in 7.0</th><th>Use</th></tr>
<tr><td><code>--checkers N</code></td><td>split type checking across N workers</td></tr>
<tr><td><code>--builders N</code></td><td>build N referenced projects at the same time</td></tr>
<tr><td><code>--singleThreaded</code></td><td>turn parallelism off, for debugging or small CI machines</td></tr></table></div>
<div class="note">Tools that call the compiler from JavaScript, such as some lint rules and code generators, have no stable API in 7.0 yet. The <code>@typescript/typescript6</code> package keeps the 6.0 compiler available as <code>tsc6</code> until 7.1.</div>
''', kw=['TypeScript 7', 'native compiler', 'Go port', 'Project Corsa', '--checkers', '--builders', '--singleThreaded', 'faster builds', '@typescript/typescript6']),
]

INFO = {'title': 'Small releases, big savings', 'panels': [
    panel([['e', '🧹'], ['t', 'using db = openDb()', {'b': 1, 'size': 11}]], '5.2', 'Cleanup that runs by itself.', 'Even when a test throws.'),
    panel([['e', '🎯'], ['t', 'filter(r => r != null)', {'b': 1, 'size': 11}]], '5.5', 'Filters narrow types.', 'Regexes are checked too.'),
    panel([['e', '🌉'], ['t', 'Temporal.PlainDate', {'b': 1, 'size': 11}]], '6.0', 'New defaults and new APIs.', 'Old options deprecated.'),
    panel([['e', '🚀'], ['t', 'tsc --checkers 4', {'b': 1}]], '7.0', 'Native and parallel.', 'Up to 10 times faster.')],
    'remember': 'Use using for cleanup, const type parameters and NoInfer for precise generics, let filters narrow by themselves, fix 6.0 deprecation warnings, then enjoy the speed of TypeScript 7.'}

REAL = [
    ['🎭', 'A Playwright team', 'Wraps every extra browser context in await using, so contexts close even when an expect fails, and the suite stopped running out of memory.'],
    ['📅', 'A booking test suite', 'Replaced hand written date maths with Temporal, and the tests stopped failing on the last day of each month.'],
    ['⚡', 'A large monorepo', 'Moved to TypeScript 7 after fixing 6.0 deprecations, and its CI type check dropped from minutes to seconds.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers what is new in TypeScript from 5.0 to 7.0, each feature checked by the real compiler and run on Node.',
        'यह अध्याय TypeScript 5.0 से 7.0 तक क्या नया है बताता है, हर feature असली compiler से जांचा और Node पर चलाया गया।',
        'TypeScript 5.0 ರಿಂದ 7.0 ವರೆಗೆ ಹೊಸದು ಈ ಅಧ್ಯಾಯದಲ್ಲಿ.',
        'TypeScript 5.0 ରୁ 7.0 ପର୍ଯ୍ୟନ୍ତ ନୂଆ ଏହି ଅଧ୍ୟାୟରେ।',
        'يغطي هذا الفصل الجديد في TypeScript من 5.0 إلى 7.0، وكل ميزة يفحصها المترجم الحقيقي وتعمل على Node.',
        'Dieses Kapitel zeigt die Neuerungen von TypeScript 5.0 bis 7.0, jede vom echten Compiler geprüft und auf Node ausgeführt.'),
    say('overview', 'Overview', 'TypeScript 5 added many small features, 6.0 is the bridge with new defaults and deprecations, and 7.0 is the fast native compiler.',
        'TypeScript 5 ने कई छोटे features जोड़े, 6.0 नए defaults और deprecations वाला पुल है, और 7.0 तेज़ native compiler है।',
        'TypeScript 5 ಸಣ್ಣ features, 6.0 ಸೇತುವೆ, 7.0 ವೇಗದ native compiler.',
        'TypeScript 5 ଛୋଟ features, 6.0 ସେତୁ, 7.0 ଦ୍ରୁତ native compiler।',
        'أضاف TypeScript 5 ميزات صغيرة كثيرة، و6.0 جسر بقيم افتراضية جديدة وإهمالات، و7.0 هو المترجم الأصلي السريع.',
        'TypeScript 5 brachte viele kleine Features, 6.0 ist die Brücke mit neuen Standards, 7.0 der schnelle native Compiler.'),
    say('ts50', 'TypeScript 5.0', 'A const type parameter keeps exact literal types for every caller, without as const.',
        'const type parameter हर caller के लिए सटीक literal types रखता है, बिना as const के।',
        'const type parameter literal types ಉಳಿಸುತ್ತದೆ.',
        'const type parameter literal types ରଖେ।',
        'يحفظ معامل النوع الثابت الأنواع الحرفية الدقيقة لكل مستدعٍ دون as const.',
        'Ein const-Typparameter behält für jeden Aufrufer genaue Literaltypen, ohne as const.'),
    say('ts52', 'using', 'using disposes of a resource when the block ends, even after an error, newest first. Import attributes load JSON with its type.',
        'using block खत्म होने पर resource बंद करता है, error के बाद भी, नया पहले। Import attributes JSON को उसके type के साथ लाते हैं।',
        'using block ಮುಗಿದಾಗ resource ಮುಚ್ಚುತ್ತದೆ.',
        'using block ଶେଷ ହେଲେ resource ବନ୍ଦ କରେ।',
        'يتخلص using من المورد عند انتهاء الكتلة حتى بعد خطأ، الأحدث أولًا، وتحمّل سمات الاستيراد ملفات JSON بنوعها.',
        'using gibt eine Ressource am Blockende frei, auch nach einem Fehler, die neueste zuerst. Import-Attribute laden JSON mit Typ.'),
    say('ts54', 'Inference', 'NoInfer stops an argument from widening a type parameter. Filters with a null check now narrow the array type by themselves.',
        'NoInfer किसी argument को type parameter चौड़ा करने से रोकता है। Null check वाले filters अब खुद array type narrow करते हैं।',
        'NoInfer type widening ತಡೆಯುತ್ತದೆ. filter ಈಗ narrow ಮಾಡುತ್ತದೆ.',
        'NoInfer type widening ରୋକେ। filter ବର୍ତ୍ତମାନ narrow କରେ।',
        'يمنع NoInfer وسيطًا من توسيع معامل النوع، وتضيّق المرشحات ذات فحص null نوع المصفوفة بنفسها الآن.',
        'NoInfer verhindert, dass ein Argument den Typparameter erweitert. Filter mit Null-Prüfung engen den Array-Typ jetzt selbst ein.'),
    say('ts56', 'Fewer mistakes', 'Conditions that are always true, such as a function used without calling it, and variables never assigned are now errors.',
        'हमेशा true रहने वाली conditions, जैसे बिना call किया function, और कभी assign न हुए variables अब errors हैं।',
        'ಯಾವಾಗಲೂ true condition ಈಗ error.',
        'ସର୍ବଦା true condition ବର୍ତ୍ତମାନ error।',
        'أصبحت الشروط الصحيحة دائمًا، مثل دالة بلا استدعاء، والمتغيرات التي لا تُسند أبدًا أخطاء الآن.',
        'Immer wahre Bedingungen, etwa eine nicht aufgerufene Funktion, und nie zugewiesene Variablen sind jetzt Fehler.'),
    say('ts60', 'TypeScript 6.0', 'TypeScript 6 sets strict and modern defaults, adds types for Temporal, getOrInsert and RegExp escape, and deprecates old options.',
        'TypeScript 6 strict और आधुनिक defaults रखता है, Temporal, getOrInsert और RegExp escape के types जोड़ता है, और पुराने options deprecate करता है।',
        'TypeScript 6 ಹೊಸ defaults, Temporal types, ಹಳೆಯ options deprecate.',
        'TypeScript 6 ନୂଆ defaults, Temporal types, ପୁରୁଣା options deprecate।',
        'يضبط TypeScript 6 قيمًا افتراضية صارمة وحديثة، ويضيف أنواع Temporal وgetOrInsert وRegExp.escape، ويهمل الخيارات القديمة.',
        'TypeScript 6 setzt strenge, moderne Standards, bringt Typen für Temporal, getOrInsert und RegExp.escape und markiert alte Optionen als veraltet.'),
    say('ts70', 'TypeScript 7.0', 'TypeScript 7 is the native compiler. Builds are about ten times faster, checking can run in parallel, and deprecated options are now errors.',
        'TypeScript 7 native compiler है। Builds लगभग दस गुना तेज़, checking parallel, और deprecated options अब errors हैं।',
        'TypeScript 7 native, ಹತ್ತು ಪಟ್ಟು ವೇಗ.',
        'TypeScript 7 native, ଦଶ ଗୁଣ ଦ୍ରୁତ।',
        'TypeScript 7 هو المترجم الأصلي، والبناء أسرع بنحو عشر مرات، والفحص متوازٍ، والخيارات المهملة أخطاء الآن.',
        'TypeScript 7 ist der native Compiler. Builds sind etwa zehnmal schneller, Prüfung läuft parallel, veraltete Optionen sind jetzt Fehler.'),
    say('practice', 'Hands-on', 'Practise a disposable stack, an upsert counter, safe regex escaping and finding deprecated options in a config.',
        'Disposable stack, upsert counter, सुरक्षित regex escaping और config में deprecated options खोजने का अभ्यास करें।',
        'Disposable stack, upsert counter, regex escape ಅಭ್ಯಾಸ.',
        'Disposable stack, upsert counter, regex escape ଅଭ୍ୟାସ।',
        'تدرّب على مكدس قابل للتخلص وعداد upsert وتهريب التعابير النمطية وإيجاد الخيارات المهملة.',
        'Übe einen Disposable-Stack, einen Upsert-Zähler, sicheres Regex-Escaping und das Finden veralteter Optionen.'),
]

QUIZ = [
    quiz('e', 'What does <code>using conn = openDb()</code> guarantee?', ['conn is disposed when the block ends, even after an error', 'conn is cached', 'conn is opened lazily', 'conn is shared between files'], 0, 'Explicit resource management.', 'It calls conn[Symbol.dispose]().'),
    quiz('e', 'Which TypeScript version is the native compiler written in Go?', ['7.0', '6.0', '5.9', '5.0'], 0, 'The newest.', '6.0 is the last JavaScript based compiler.'),
    quiz('e', 'What does <code>with { type: "json" }</code> on an import do?', ['Tells the runtime the file is JSON', 'Validates the JSON against a schema', 'Converts JSON to YAML', 'Makes the import lazy'], 0, 'Import attributes.', 'Node requires it for JSON imports in ES modules.'),
    quiz('m', 'What is the type of <code>[1, null, 2].filter(x =&gt; x !== null)</code> since TypeScript 5.5?', ['number[]', '(number | null)[]', 'unknown[]', 'never[]'], 0, 'Inferred type predicate.', 'The arrow function is inferred as x is number.'),
    quiz('m', 'Why is <code>if (isLoggedIn)</code> an error in TypeScript 5.6?', ['A function is always truthy, so the call was probably forgotten', 'Functions cannot be in if', 'isLoggedIn is undefined', 'if needs a boolean variable'], 0, 'Always true.', 'The fix is isLoggedIn().'),
    quiz('m', 'What does <code>NoInfer&lt;T&gt;</code> on the fallback parameter prevent?', ['The fallback widening T to accept a wrong value', 'T from being used', 'The function from being generic', 'Default values'], 0, 'Inference source.', 'T is decided only by the supported list.'),
    quiz('m', 'In what order are two <code>using</code> resources disposed?', ['Newest first, like a stack', 'Oldest first', 'In parallel', 'In random order'], 0, 'Last in, first out.', 'audit closed before orders in the example.'),
    quiz('h', 'What does <code>"ignoreDeprecations": "6.0"</code> do?', ['Silences 6.0 deprecation warnings during a migration', 'Turns on TypeScript 6 features', 'Downgrades to 6.0', 'Removes deprecated code'], 0, 'Temporary.', 'In 7.0 the deprecated options are errors and cannot be silenced.'),
    quiz('h', 'What does <code>--checkers 4</code> do in TypeScript 7?', ['Runs type checking in 4 parallel workers', 'Checks 4 files only', 'Runs 4 linters', 'Retries 4 times'], 0, 'Parallel checking.', '--builders does the same for referenced projects.'),
    quiz('h', 'What does <code>RegExp.escape(text)</code> return?', ['The text with regex special characters escaped', 'A RegExp object', 'The text in upper case', 'The number of matches'], 0, 'Safe patterns.', 'Use it before putting user text into new RegExp().'),
    quiz('x', 'Which option was deprecated in 6.0 and removed in 7.0?', ['target es5', 'strict', 'noEmit', 'lib'], 0, 'Old output targets.', 'Also baseUrl, outFile and moduleResolution node10.'),
    quiz('x', 'Why might a tool still need <code>@typescript/typescript6</code>?', ['TypeScript 7.0 has no stable JavaScript API until 7.1', 'TypeScript 7 cannot check files', 'It is faster', 'It supports Go'], 0, 'Programmatic API.', 'Language services and code generators may call the compiler from JavaScript.'),
]

CALC = [
    calc('e', 'Three resources are opened with using in one block. How many dispose calls run when the block ends?', '3', 'One per resource.', ['Each using declaration registers one cleanup.']),
    calc('e', 'Map.getOrInsert counts ["pass", "fail", "pass", "pass"]. What is the count for pass?', '3', 'Count the passes.', ['pass appears 3 times.']),
    calc('m', 'A build took 125.7 s and now takes 10.6 s. How many seconds are saved per build?', '115.1', 'Subtract.', ['<span class="eq">125.7 − 10.6 = 115.1 s</span>']),
    calc('m', 'CI runs 40 type checks a day, each saving 115.1 s. About how many minutes a day is that, to the nearest whole number?', '77', 'Multiply, then divide by 60.', ['<span class="eq">40 × 115.1 = 4604 s</span>', '<span class="eq"><span class="fr"><i>4604</i><i>60</i></span> ≈ 77 min</span>']),
    calc('h', 'How many days are there from 2026-03-23 to 2026-09-23?', '184', 'Count month by month: 31 + 30 + 31 + 30 + 31 + 31.', ['<span class="eq">8 + 30 + 31 + 30 + 31 + 31 + 23 = 184</span>', 'Days left in March, then April to August, then 23 days of September.']),
    calc('h', 'A const type parameter keeps ["admin", "qa", "viewer"]. How many members does the Role union have?', '3', 'One per literal.', ['"admin" | "qa" | "viewer".']),
    calc('x', 'A 4 core CI machine checks a project in 24 s single threaded. With --checkers 4 and 75 percent efficiency, about how many seconds does it take?', '8', 'Ideal time divided by efficiency.', ['<span class="eq"><span class="fr"><i>24</i><i>4</i></span> = 6 s ideal</span>', '<span class="eq"><span class="fr"><i>6</i><i>0.75</i></span> = 8 s</span>']),
]

EX = [
    ex('stack', 'e', 'A disposable stack', '<p>Write <code>runWith(names)</code> that "opens" each name in order by pushing <code>"open NAME"</code> to a log, then closes them in reverse order by pushing <code>"close NAME"</code>, and returns the log. This is what several <code>using</code> lines do.</p>',
       'function runWith(names) {\n  \n}\n',
       [('runWith(["orders", "audit"])', ['open orders', 'open audit', 'close audit', 'close orders']), ('runWith([])', []), ('runWith(["a"])', ['open a', 'close a'])],
       'function runWith(names) {\n  const log = names.map(n => `open ${n}`);\n  for (const n of [...names].reverse()) log.push(`close ${n}`);\n  return log;\n}', hint='Map to open lines, then loop over a reversed copy.', why='Cleanup in reverse order means later resources, which may depend on earlier ones, close first.'),
    ex('upsert', 'm', 'Count with getOrInsert', '<p>Write <code>countAll(words)</code> that returns a plain object of counts. Use a Map with <code>getOrInsert</code> if you like, then convert it with <code>Object.fromEntries</code>.</p>',
       'function countAll(words) {\n  \n}\n',
       [('countAll(["pass", "fail", "pass"])', {'pass': 2, 'fail': 1}), ('countAll([])', {}), ('countAll(["skip"])', {'skip': 1})],
       'function countAll(words) {\n  const m = new Map();\n  for (const w of words) m.set(w, m.getOrInsert(w, 0) + 1);\n  return Object.fromEntries(m);\n}', hint='<code>m.getOrInsert(w, 0)</code> returns the old count or inserts 0.', why='Upsert removes the "check, then set a default" dance that often hides off by one bugs.'),
    ex('escape', 'h', 'Find text safely', '<p>Write <code>countMatches(haystack, needle)</code> that counts how many times <code>needle</code> appears in <code>haystack</code>, treating it as plain text even if it contains characters such as <code>(</code>, <code>$</code> or <code>.</code>. Use <code>RegExp.escape</code>.</p>',
       'function countMatches(haystack, needle) {\n  \n}\n',
       [('countMatches("price (in $) and price (in $)", "price (in $)")', 2), ('countMatches("a.b.c", ".")', 2), ('countMatches("none here", "x+")', 0)],
       'function countMatches(haystack, needle) {\n  return (haystack.match(new RegExp(RegExp.escape(needle), "g")) || []).length;\n}', hint='Build the regex from the escaped needle with the g flag.', why='Without escaping, "." matches every character and "(in $)" is not even valid.'),
    ex('deprecated', 'x', 'Find options TypeScript 7 removed', '<p>Write <code>removedOptions(compilerOptions)</code> that returns the names of problems, in this order of checks: <code>"baseUrl"</code> if set, <code>"outFile"</code> if set, <code>"target es5"</code> if target is <code>"es5"</code> (any case), <code>"moduleResolution node10"</code> if it is <code>"node10"</code> or <code>"node"</code>, and <code>"moduleResolution classic"</code> if it is <code>"classic"</code>.</p>',
       'function removedOptions(compilerOptions) {\n  \n}\n',
       [('removedOptions({ baseUrl: ".", target: "ES5", moduleResolution: "node" })', ['baseUrl', 'target es5', 'moduleResolution node10']), ('removedOptions({ strict: true })', []), ('removedOptions({ outFile: "a.js", moduleResolution: "classic" })', ['outFile', 'moduleResolution classic'])],
       'function removedOptions(o) {\n  const out = [];\n  if (o.baseUrl !== undefined) out.push("baseUrl");\n  if (o.outFile !== undefined) out.push("outFile");\n  if (String(o.target).toLowerCase() === "es5") out.push("target es5");\n  const mr = String(o.moduleResolution).toLowerCase();\n  if (mr === "node10" || mr === "node") out.push("moduleResolution node10");\n  if (mr === "classic") out.push("moduleResolution classic");\n  return out;\n}', hint='One if per rule, in the given order. Lower case strings before comparing.', why='A small script like this can scan every tsconfig in a monorepo before the TypeScript 7 upgrade.'),
]

T = {
    'slug': 'ts-whats-new', 'title': 'What is new in TypeScript: 5.0 to 7.0', 'short': 'What is new up to TS 7', 'emoji': '🆕', 'module': MODULE, 'minutes': 22,
    'lead': 'TypeScript changes quickly, and each release removes a little more friction. This chapter walks from TypeScript 5.0 to 7.0: const type parameters, using for automatic cleanup, import attributes, NoInfer, filters that narrow by themselves, regex and truthiness checks, the ES2025 and Temporal types of 6.0, and the native, parallel TypeScript 7 compiler, each checked by the real compiler and run on Node.js.',
    'desc': 'What is new in TypeScript 5.0 to 7.0: const type parameters, using and await using, import attributes, NoInfer, inferred type predicates, regex checking, always truthy checks, iterator helpers, never initialised variables, import defer, TypeScript 6.0 defaults, Temporal, Map.getOrInsert, RegExp.escape and deprecations, and the native TypeScript 7 compiler with --checkers and --builders.',
    'summary': 'A release table from 5.0 to 7.0, const type parameters, using with an animated cleanup order, JSON import attributes, NoInfer and closure narrowing, inferred type predicates and regex checks, truthiness and never initialised checks, iterator helpers, import defer, 6.0 runtime types and deprecations, and the TypeScript 7 compiler with parallel checking.',
    'keywords': ['TypeScript 5.0', 'TypeScript 5.5', 'TypeScript 6.0', 'TypeScript 7.0', 'using', 'Symbol.dispose', 'import attributes', 'NoInfer', 'inferred type predicates', 'Temporal', 'getOrInsert', 'RegExp.escape', 'native compiler', '--checkers', 'what is new'],
    'qa_intro': 'Several of these features exist mainly to prevent the bugs test code is full of: leaked browsers, forgotten function calls in conditions, wrong regex patterns and null rows in filtered data.',
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
