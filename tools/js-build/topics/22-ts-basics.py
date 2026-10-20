# Chapter 22: TypeScript fundamentals: setup, everyday types, functions, interfaces and type aliases, unions and narrowing, enums and their alternatives, and strict options.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg, ts

MODULE = ('🔷', 'TypeScript', 'ts', 'TypeScript from the first type to generics, advanced types, typed projects and test automation written in TypeScript.')

CODES = {
    'first': ts('''
// TypeScript is JavaScript plus types. The types are checked by tsc and then removed.
function lineTotal(price: number, qty: number): number {
  return price * qty;
}

const total = lineTotal(40, 3);
const wrong = lineTotal("40", 3);          // a string where a number is expected
const name: string = total;                // a number where a string is expected

console.log(total, wrong, name);
''', 'tsc finds the mistakes, Node.js runs the code anyway', errors=2),
    'tsconfig': show('''
{
  "compilerOptions": {
    "target": "es2024",            // which JavaScript features the output may use
    "module": "nodenext",          // how imports work: Node.js rules for ESM and CommonJS
    "strict": true,                // turn on every strict check, always do this
    "noUncheckedIndexedAccess": true,
    "noEmit": true,                // only type check, Node.js or a bundler runs the .ts files
    "allowImportingTsExtensions": true,
    "erasableSyntaxOnly": true,    // forbid syntax Node.js cannot simply strip, such as enum
    "types": ["node"]              // types for process, Buffer and friends from @types/node
  },
  "include": ["src", "tests"]
}
''', 'A modern tsconfig.json', lang='json', note='Explained below'),
    'everyday': ts('''
// Inference: no annotation needed when the value says it all
let retries = 3;                            // number
const browser = "chromium";                 // the literal type "chromium", because const never changes
const tags = ["smoke", "cart"];             // string[]

// Arrays, tuples, objects, optional and readonly
const timings: number[] = [840, 2310];
const pair: [string, number] = ["login", 840];
const user: { readonly id: number; name: string; email?: string } = { id: 7, name: "Asha" };

user.name = "Asha K";
user.id = 8;                                // readonly
retries = "three";                          // number only

// any switches checking off. unknown must be checked before use.
const fromApi: unknown = JSON.parse('{"status": 200}');
// fromApi.status;                          // error: 'fromApi' is of type 'unknown'
if (typeof fromApi === "object" && fromApi !== null && "status" in fromApi) console.log("status", fromApi.status);

console.log(browser, tags, timings, pair, user.email ?? "no email");
''', 'Everyday types, inference, readonly and unknown', errors=2),
    'functions': ts('''
// Parameters and returns, optional and default values, rest parameters
function greet(name: string, greeting = "Hello", punctuation?: string): string {
  return `${greeting}, ${name}${punctuation ?? "!"}`;
}
const sum = (...values: number[]): number => values.reduce((a, b) => a + b, 0);

// A function type, used for callbacks
type Matcher = (actual: string) => boolean;
const startsWith = (prefix: string): Matcher => actual => actual.startsWith(prefix);

// Overloads: one implementation, several typed call shapes
function find(id: number): { id: number };
function find(email: string): { email: string };
function find(key: number | string) {
  return typeof key === "number" ? { id: key } : { email: key };
}

// void for "returns nothing", never for "never returns"
function fail(message: string): never { throw new Error(message); }

console.log(greet("Asha"), greet("Ravi", "Hi", "."), sum(1, 2, 3), startsWith("ORD-")("ORD-7"));
console.log(find(7), find("asha@shop.test"));
greet();                                    // missing argument
sum(1, "2");                                // wrong type in the rest list
try { fail("stop"); } catch (e) { console.log((e as Error).message); }
''', 'Typing functions, callbacks and overloads', errors=2),
    'shapes': ts('''
// interface: a named object shape that can be extended and merged
interface TestResult {
  name: string;
  status: "passed" | "failed" | "skipped";
  durationMs: number;
}
interface RetriedResult extends TestResult {
  retries: number;
}

// type: a name for any type, including unions, tuples and intersections
type Browser = "chromium" | "firefox" | "webkit";
type WithBrowser = TestResult & { browser: Browser };
type ById = Record<string, TestResult>;            // an object with any string keys
type Timings = { [testName: string]: number };     // index signature, the same idea

const r: RetriedResult = { name: "checkout", status: "failed", durationMs: 2310, retries: 2 };
const w: WithBrowser = { name: "login", status: "passed", durationMs: 840, browser: "safari" };
const byId: ById = { t1: r };
const timings: Timings = { login: 840 };

console.log(r.retries, w.browser, Object.keys(byId), timings.login);
''', 'interface and type, extends and intersections', errors=1),
    'narrowing': ts('''
type ApiResult = { ok: true; data: string[] } | { ok: false; error: string; status: number };

function describe(r: ApiResult): string {
  if (r.ok) return `got ${r.data.length} items`;        // here TypeScript knows r has data
  return `failed with ${r.status}: ${r.error}`;          // and here that r has error and status
}

function formatId(id: string | number | null): string {
  if (id === null) return "none";                        // equality narrowing
  if (typeof id === "number") return `#${id.toFixed(0)}`; // typeof narrowing
  return id.toUpperCase();                               // only string is left
}

class TimeoutError extends Error {
  ms: number;
  constructor(ms: number) { super(`timeout after ${ms} ms`); this.ms = ms; }
}
function retryable(e: unknown): boolean {
  if (e instanceof TimeoutError) return e.ms < 30_000;  // instanceof narrowing
  if (e instanceof Error && "code" in e) return e.code === "ECONNRESET";   // in narrowing
  return false;
}

console.log(describe({ ok: true, data: ["a", "b"] }), "|", describe({ ok: false, error: "down", status: 503 }));
console.log(formatId(7), formatId("ord-7"), formatId(null), retryable(new TimeoutError(5000)));
''', 'Unions and narrowing'),
    'enums': ts('''
// enum creates real JavaScript, so Node.js cannot just strip it
enum Status { Passed = "passed", Failed = "failed" }

// The erasable alternative: a const object and a union type made from it
const Browser = { Chromium: "chromium", Firefox: "firefox", Webkit: "webkit" } as const;
type Browser = (typeof Browser)[keyof typeof Browser];   // "chromium" | "firefox" | "webkit"

function launch(b: Browser) { return `launching ${b}`; }
console.log(launch(Browser.Firefox), launch("webkit"), Status.Passed);
launch("edge");
''', 'enum against as const objects', errors=2, run=False, options={'erasableSyntaxOnly': True}),
    'strict': ts('''
const users = ["asha", "ravi"];
const third = users[2];                   // with noUncheckedIndexedAccess this is string | undefined
console.log(third.toUpperCase());          // could crash at run time, so tsc complains

function len(s) { return s.length; }       // noImplicitAny: s has no type

const config: { timeout?: number } = {};
const ms: number = config.timeout;         // strictNullChecks: it may be undefined
''', 'What strict mode catches', errors=3, run=False, options={'noUncheckedIndexedAccess': True}),
    'scenario': ts('''
import { readFileSync } from "node:fs";

interface Result { name: string; status: "passed" | "failed"; ms: number }

// JSON from a file or an API is unknown until it is checked
function isResult(x: unknown): x is Result {
  if (typeof x !== "object" || x === null) return false;
  const r = x as Record<string, unknown>;
  return typeof r.name === "string" && (r.status === "passed" || r.status === "failed") && typeof r.ms === "number";
}

const raw: unknown = JSON.parse(readFileSync("src/results.json", "utf8"));
if (!Array.isArray(raw)) throw new Error("expected a list of results");

const valid = raw.filter(isResult);                 // Result[] from here on
const rejected = raw.length - valid.length;
const failed = valid.filter(r => r.status === "failed").map(r => r.name);
const slowest = valid.toSorted((a, b) => b.ms - a.ms)[0];

console.log({ valid: valid.length, rejected, failed, slowest: slowest?.name });
''', 'Read untyped JSON safely', more={'src/results.json': '''
[
  { "name": "login", "status": "passed", "ms": 840 },
  { "name": "checkout", "status": "failed", "ms": 2310 },
  { "name": "search", "status": "pased", "ms": 120 },
  { "name": "profile", "status": "passed", "ms": "45" }
]
'''}),
}

PARTS = [
    part('why', '🔷', 'What TypeScript is and how it runs', '''
<p><b>TypeScript</b> is JavaScript with type annotations. The compiler <code>tsc</code> reads the types and reports mistakes before the code runs. The types are then <b>erased</b>: at run time it is plain JavaScript. Node.js 23.6 and later can run <code>.ts</code> files directly by stripping the types, without checking them, so you use both: <code>tsc</code> to check, Node.js to run.</p>
[[first]]
<p>Notice that Node.js ran the file even with two type errors. Types never change what code does. They are a safety net that only works if <code>tsc</code> runs in your editor and in CI.</p>
[[tsconfig]]
<div class="tip">Playwright, Vitest, Jest (with a transform), Cypress and WebdriverIO all accept TypeScript tests. Most new automation projects are written in TypeScript because locators, fixtures and API responses become typed and the editor completes them.</div>
''', qa=['Playwright', 'Cypress', 'WebdriverIO'], qa_why='Most modern automation frameworks are written and used in TypeScript.',
        kw=['TypeScript', 'tsc', 'type annotation', 'type erasure', 'type stripping', 'tsconfig.json', 'strict', 'noEmit', 'erasableSyntaxOnly', '@types/node', 'tsx']),
    part('everyday', '🧱', 'Everyday types', '''
<p>Most of the time TypeScript <b>infers</b> the type from the value, so you annotate function parameters, public APIs and empty containers, not every variable. Use <code>readonly</code> for data that must not change, <code>?</code> for optional properties, and tuples for fixed length lists.</p>
[[everyday]]
<div class="tw"><table class="jt"><tr><th>Type</th><th>Use it for</th></tr>
<tr><td><code>string number boolean bigint symbol</code></td><td>the primitive values</td></tr>
<tr><td><code>null undefined</code></td><td>"no value", checked strictly with <code>strict</code></td></tr>
<tr><td><code>string[]</code> or <code>Array&lt;string&gt;</code></td><td>lists of one type</td></tr>
<tr><td><code>[string, number]</code></td><td>tuples: fixed positions</td></tr>
<tr><td><code>"a" | "b"</code></td><td>literal unions: a fixed set of allowed values</td></tr>
<tr><td><code>unknown</code></td><td>outside data: you must check it before use</td></tr>
<tr><td><code>any</code></td><td>switches checking off, avoid it</td></tr>
<tr><td><code>never</code></td><td>a value that cannot exist, such as the return of a function that always throws</td></tr>
</table></div>
''', qa=True, qa_why='Typed test data and typed API responses catch typos in field names before a test even starts.',
        kw=['type inference', 'string', 'number', 'boolean', 'array type', 'tuple', 'object type', 'optional property', 'readonly', 'literal type', 'unknown', 'any', 'never', 'const inference']),
    part('functions', '🧩', 'Functions', '''
<p>Annotate parameters, and let the return type be inferred or write it for public functions. Optional parameters use <code>?</code>, defaults give both a type and a value, and rest parameters are typed as arrays. Function types describe callbacks, and <b>overloads</b> give one function several typed call shapes.</p>
[[functions]]
''', kw=['function types', 'parameter types', 'return type', 'optional parameter', 'default parameter', 'rest parameter', 'overloads', 'void', 'never', 'callback type', 'type assertion', 'as']),
    part('shapes', '📐', 'interface and type', '''
<p>Both <code>interface</code> and <code>type</code> name an object shape. Interfaces can be extended with <code>extends</code> and are merged when declared twice, which suits public object shapes. Type aliases can name anything: unions, tuples, functions and combinations with <code>&amp;</code>. Teams usually pick one style for objects and use <code>type</code> for everything else.</p>
[[shapes]]
''', qa=True, qa_why='Interfaces describe API responses, test data and page object options in typed test projects.',
        kw=['interface', 'type alias', 'extends', 'intersection', '&', 'Record', 'index signature', 'declaration merging', 'object shape']),
    part('narrowing', '🔍', 'Unions and narrowing', '''
<p>A <b>union</b> such as <code>string | number</code> means "one of these". Before you use a union, you <b>narrow</b> it with a check that TypeScript understands: <code>typeof</code>, <code>instanceof</code>, <code>in</code>, equality, or a shared literal field. Inside each branch, TypeScript knows the exact type.</p>
[[narrowing]]
<div class="note">A union of objects with a common literal field, such as <code>ok: true</code> or <code>ok: false</code>, is a <b>discriminated union</b>. It is the best way to type API results, test outcomes and state machines, and chapter 23 makes it exhaustive.</div>
''', qa=True, qa_why='API responses are usually "success or error", which discriminated unions model exactly.',
        kw=['union type', 'narrowing', 'typeof', 'instanceof', 'in operator', 'equality narrowing', 'discriminated union', 'control flow analysis', 'type guard']),
    part('enums', '🏷️', 'Enums and their modern alternative', '''
<p>An <code>enum</code> creates a real object at run time, so it is not erasable and fails with <code>erasableSyntaxOnly</code> and with Node.js type stripping. The modern alternative is a plain object marked <code>as const</code> plus a union type made from its values. It works everywhere and accepts both <code>Browser.Firefox</code> and the string <code>"firefox"</code>.</p>
[[enums]]
''', kw=['enum', 'const enum', 'as const', 'keyof typeof', 'erasableSyntaxOnly', 'literal union', 'string enum']),
    part('strict', '🛡️', 'Strict options', '''
<p><code>"strict": true</code> turns on a family of checks. The two that catch the most bugs are <b>strictNullChecks</b>, which makes you handle <code>undefined</code> and <code>null</code>, and <b>noImplicitAny</b>, which stops untyped parameters. <code>noUncheckedIndexedAccess</code> goes further: reading an array element or a record key may give <code>undefined</code>.</p>
[[strict]]
<div class="warn">A project without <code>strict</code> lets most of these bugs through, so TypeScript gives a false sense of safety. Turn it on from day one. When moving an old JavaScript project, turn on <code>checkJs</code> and fix files one folder at a time (chapter 24).</div>
''', qa=True, qa_why='Strict null checks catch the "cannot read properties of undefined" errors that make tests crash.',
        kw=['strict', 'strictNullChecks', 'noImplicitAny', 'noUncheckedIndexedAccess', 'exactOptionalPropertyTypes', 'tsconfig options', 'undefined', 'null']),
    part('scenario', '🎬', 'Real world scenario: typed results from untyped JSON', '''
<div class="scenario"><b>The situation</b>A dashboard script reads test results from a JSON file written by another tool. Some rows have typos such as "pased" or a duration stored as a string.</div>
[[scenario]]
<p><code>JSON.parse</code> really returns unknown data, whatever its declared type. A <b>type predicate</b> such as <code>x is Result</code> checks it at run time and tells TypeScript the result, so everything after the filter is fully typed and the bad rows are counted instead of breaking the report. Chapter 25 does the same with Zod.</p>
''', qa=True, kw=['unknown', 'JSON.parse', 'type predicate', 'is', 'runtime validation', 'type guard', 'filter', 'test results']),
]

INFO = {'title': 'Types that catch bugs early', 'panels': [
    panel([['e', '🔷'], ['t', 'price: number', {'b': 1}]], 'Annotate', 'Say what a value must be.', 'tsc checks, Node.js runs.'),
    panel([['e', '🧠'], ['t', 'let n = 3 // number', {'b': 1}]], 'Infer', 'Most types come for free.', 'Annotate inputs and APIs.'),
    panel([['e', '🔍'], ['t', 'if (r.ok) …', {'b': 1}]], 'Narrow', 'Check, then use.', 'Each branch knows the type.'),
    panel([['e', '🛡️'], ['t', '"strict": true', {'b': 1}]], 'Be strict', 'Handle undefined and null.', 'No silent any.')],
    'remember': 'Turn on strict, annotate inputs, let the rest be inferred, treat outside data as unknown and narrow before you use it.'}

REAL = [
    ['🎭', 'A Playwright team', 'Moved its tests to TypeScript and found 14 typos in locator option names and fixture names on the first tsc run, all of them silent bugs.'],
    ['🧾', 'A billing API', 'Typed its response as a discriminated union of success and error. The client code could no longer read data from an error by mistake.'],
    ['🧪', 'A test data tool', 'Treats every CSV and JSON input as unknown and checks it with type predicates, so a typo in a data file is reported with its row number.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter starts TypeScript: how it runs, everyday types, functions, interfaces and types, unions and narrowing, enums and strict options.',
        'यह अध्याय TypeScript शुरू करता है: यह कैसे चलता है, रोज़ के types, functions, interfaces और types, unions और narrowing, enums और strict options।',
        'ಈ ಅಧ್ಯಾಯ TypeScript ಆರಂಭಿಸುತ್ತದೆ: types, functions, interfaces, unions, narrowing, enums ಮತ್ತು strict options.',
        'ଏହି ଅଧ୍ୟାୟ TypeScript ଆରମ୍ଭ କରେ: types, functions, interfaces, unions, narrowing, enums ଓ strict options।',
        'يبدأ هذا الفصل TypeScript: كيف يعمل والأنواع اليومية والدوال والواجهات والاتحادات والتضييق والتعدادات والخيارات الصارمة.',
        'Dieses Kapitel startet TypeScript: wie es läuft, Alltagstypen, Funktionen, Interfaces, Unions, Narrowing, Enums und strikte Optionen.'),
    say('why', 'What TypeScript is', 'TypeScript adds types to JavaScript. tsc checks them and then they are erased. Node runs ts files by stripping types, without checking them.',
        'TypeScript JavaScript में types जोड़ता है। tsc उन्हें जांचता है फिर वे हट जाते हैं। Node बिना जांचे types हटाकर ts files चलाता है।',
        'TypeScript JavaScript ಗೆ types ಸೇರಿಸುತ್ತದೆ. tsc ಪರಿಶೀಲಿಸುತ್ತದೆ, ನಂತರ ತೆಗೆಯಲಾಗುತ್ತದೆ.',
        'TypeScript JavaScript ରେ types ଯୋଡ଼େ। tsc ଯାଞ୍ଚ କରେ, ତାପରେ ହଟିଯାଏ।',
        'تضيف TypeScript الأنواع إلى JavaScript، ويتحقق منها tsc ثم تُزال. يشغل Node ملفات ts بإزالة الأنواع دون فحصها.',
        'TypeScript ergänzt JavaScript um Typen. tsc prüft sie, dann werden sie entfernt. Node führt ts-Dateien ohne Prüfung aus.'),
    say('everyday', 'Everyday types', 'TypeScript infers most types. Use readonly, optional properties and tuples, treat outside data as unknown and avoid any.',
        'TypeScript ज़्यादातर types खुद समझ लेता है। readonly, optional properties और tuples इस्तेमाल करें, बाहर का data unknown मानें।',
        'TypeScript ಹೆಚ್ಚಿನ types ಊಹಿಸುತ್ತದೆ. readonly, optional, tuples ಬಳಸಿ, ಹೊರಗಿನ data unknown.',
        'TypeScript ଅଧିକାଂଶ types ଅନୁମାନ କରେ। readonly, optional, tuples ବ୍ୟବହାର କରନ୍ତୁ, ବାହାର data unknown।',
        'تستنتج TypeScript أغلب الأنواع. استخدم readonly والخصائص الاختيارية والصفوف، واعتبر البيانات الخارجية unknown وتجنب any.',
        'TypeScript leitet die meisten Typen ab. Nutze readonly, optionale Felder und Tupel, behandle externe Daten als unknown.'),
    say('functions', 'Functions', 'Type the parameters, use optional and default values, describe callbacks with function types, and use overloads for several call shapes.',
        'Parameters को type दें, optional और default values इस्तेमाल करें, callbacks के लिए function types और कई रूपों के लिए overloads।',
        'Parameters ಗೆ type ಕೊಡಿ, callbacks ಗೆ function types, ಅನೇಕ ರೂಪಗಳಿಗೆ overloads.',
        'Parameters କୁ type ଦିଅନ୍ତୁ, callbacks ପାଇଁ function types, ଅନେକ ରୂପ ପାଇଁ overloads।',
        'حدد أنواع المعاملات واستخدم القيم الاختيارية والافتراضية، وصف الاستدعاءات الراجعة بأنواع الدوال، واستخدم التحميل الزائد لأشكال متعددة.',
        'Typisiere Parameter, nutze optionale und Standardwerte, beschreibe Callbacks mit Funktionstypen und Overloads.'),
    say('shapes', 'interface and type', 'interface names an object shape and can be extended. type can name anything, including unions and intersections.',
        'interface object का आकार बताता है और extend हो सकता है। type कुछ भी नाम दे सकता है, unions और intersections भी।',
        'interface object ಆಕಾರ ಹೆಸರಿಸುತ್ತದೆ, extend ಆಗುತ್ತದೆ. type ಯಾವುದನ್ನೂ ಹೆಸರಿಸಬಹುದು.',
        'interface object ଆକାର ନାମ ଦିଏ, extend ହୁଏ। type ଯାହା ବି ନାମ ଦେଇପାରେ।',
        'تسمي interface شكل كائن ويمكن توسيعها، ويمكن لـ type تسمية أي شيء بما فيه الاتحادات والتقاطعات.',
        'interface benennt eine Objektform und lässt sich erweitern. type kann alles benennen, auch Unions.'),
    say('narrowing', 'Narrowing', 'A union means one of several types. Narrow it with typeof, instanceof, in, equality or a shared literal field, and each branch knows the exact type.',
        'Union का मतलब कई में से एक type। typeof, instanceof, in, equality या literal field से narrow करें।',
        'Union ಎಂದರೆ ಹಲವು types ನಲ್ಲಿ ಒಂದು. typeof, instanceof, in ಮೂಲಕ narrow ಮಾಡಿ.',
        'Union ମାନେ ଅନେକ types ମଧ୍ୟରୁ ଗୋଟିଏ। typeof, instanceof, in ରେ narrow କରନ୍ତୁ।',
        'الاتحاد يعني نوعًا من عدة أنواع. ضيّقه بـ typeof أو instanceof أو in أو المساواة أو حقل حرفي مشترك.',
        'Eine Union ist einer von mehreren Typen. Grenze sie mit typeof, instanceof, in oder einem Literalfeld ein.'),
    say('enums', 'Enums', 'An enum creates real code, so Node cannot strip it. Use a const object with as const and a union type made from its values.',
        'Enum असली code बनाता है, इसलिए Node उसे हटा नहीं सकता। as const object और उसके values से बना union type इस्तेमाल करें।',
        'Enum ನಿಜವಾದ code ಮಾಡುತ್ತದೆ. as const object ಮತ್ತು union type ಬಳಸಿ.',
        'Enum ପ୍ରକୃତ code କରେ। as const object ଓ union type ବ୍ୟବହାର କରନ୍ତୁ।',
        'ينشئ enum شيفرة حقيقية فلا يستطيع Node إزالته. استخدم كائنًا ثابتًا بـ as const ونوع اتحاد من قيمه.',
        'Ein enum erzeugt echten Code, Node kann es nicht entfernen. Nutze ein Objekt mit as const und eine Union.'),
    say('strict', 'Strict mode', 'strict turns on null checks and no implicit any. noUncheckedIndexedAccess also treats array reads as possibly undefined.',
        'strict null checks और no implicit any चालू करता है। noUncheckedIndexedAccess array reads को भी undefined मान सकता है।',
        'strict null checks ಮತ್ತು no implicit any ಆನ್ ಮಾಡುತ್ತದೆ.',
        'strict null checks ଓ no implicit any ଚାଲୁ କରେ।',
        'يشغل strict فحوص null ومنع any الضمني، ويجعل noUncheckedIndexedAccess قراءة المصفوفة قد تكون undefined.',
        'strict aktiviert Null-Prüfungen und verbietet implizites any. noUncheckedIndexedAccess macht Array-Zugriffe vorsichtig.'),
    say('scenario', 'Scenario', 'JSON is unknown until it is checked. A type predicate checks each row at run time and gives TypeScript the type, so bad rows are counted.',
        'JSON जांचने तक unknown है। Type predicate हर row को run time पर जांचता है और TypeScript को type देता है।',
        'JSON ಪರಿಶೀಲಿಸುವವರೆಗೆ unknown. Type predicate ಪ್ರತಿ row ಪರಿಶೀಲಿಸುತ್ತದೆ.',
        'JSON ଯାଞ୍ଚ ପର୍ଯ୍ୟନ୍ତ unknown। Type predicate ପ୍ରତି row ଯାଞ୍ଚ କରେ।',
        'يبقى JSON مجهولًا حتى يُفحص. يفحص مسند النوع كل صف وقت التشغيل ويخبر TypeScript بالنوع، فتُعد الصفوف السيئة.',
        'JSON ist unknown, bis es geprüft ist. Ein Typprädikat prüft jede Zeile und gibt TypeScript den Typ.'),
    say('practice', 'Hands-on', 'Practise a type guard, a function that handles a union, an as const lookup and safe reads with defaults.',
        'Type guard, union संभालने वाला function, as const lookup और defaults के साथ safe reads का अभ्यास करें।',
        'Type guard, union function, as const lookup ಮತ್ತು safe reads ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Type guard, union function, as const lookup ଓ safe reads ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على حارس نوع ودالة تعالج اتحادًا وجدول بحث بـ as const وقراءات آمنة بقيم افتراضية.',
        'Übe einen Type Guard, eine Funktion für Unions, ein as-const-Lookup und sichere Zugriffe mit Standardwerten.'),
]

QUIZ = [
    quiz('e', 'What happens to TypeScript types when the code runs?', ['They are erased, it runs as JavaScript', 'They are checked again', 'They make it faster', 'They are sent to the browser'], 0, 'Erasure.', 'Types exist only for tsc and your editor.'),
    quiz('e', 'Which type must be checked before you can use its properties?', ['unknown', 'any', 'string', 'object'], 0, 'Safe outside data.', 'any lets you do anything, which hides bugs.'),
    quiz('e', 'What does email?: string mean in an object type?', ['email may be missing', 'email is a string or a number', 'email is readonly', 'email is required'], 0, 'Optional.', 'Its type when read is string | undefined.'),
    quiz('m', 'Node.js runs a .ts file that has type errors. What happens?', ['It runs, Node.js strips types without checking them', 'It refuses to run', 'It fixes the errors', 'It prints the errors and stops'], 0, 'Strip only.', 'Run tsc in the editor and in CI to catch errors.'),
    quiz('m', 'What is the type of const browser = "chromium"?', ['The literal type "chromium"', 'string', 'any', 'unknown'], 0, 'const never changes.', 'let browser = "chromium" would be string.'),
    quiz('m', 'Which can type a union like "a" | "b"?', ['type', 'interface', 'Both', 'Neither'], 0, 'Type aliases name anything.', 'Interfaces describe object shapes only.'),
    quiz('m', 'After if (typeof id === "number") return …, what is id below it if it was string | number?', ['string', 'number', 'never', 'unknown'], 0, 'Control flow narrowing.', 'The number case has already returned.'),
    quiz('h', 'Why does erasableSyntaxOnly reject enum?', ['enum creates run time code, so stripping types would break it', 'enum is deprecated', 'enum is slow', 'enum needs classes'], 0, 'Not just a type.', 'Namespaces and parameter properties are rejected for the same reason.'),
    quiz('h', 'With noUncheckedIndexedAccess, what is the type of names[0] for names: string[]?', ['string | undefined', 'string', 'never', 'any'], 0, 'The list may be empty.', 'You must check it before calling string methods.'),
    quiz('h', 'What does a return type of x is Result do?', ['Tells TypeScript that x is a Result when the function returns true', 'Converts x to Result', 'Throws if x is not a Result', 'Nothing at run time or compile time'], 0, 'Type predicate.', 'Used with filter, it narrows the whole array.'),
    quiz('x', 'Which statement about overloads is true?', ['Callers see only the overload signatures, not the implementation signature', 'Each overload has its own body', 'Overloads run in order', 'They are erased at compile time and then fail'], 0, 'One body.', 'The implementation must handle every overload.'),
    quiz('x', 'What does the never return type say about fail(message)?', ['It never returns normally, it always throws or loops', 'It returns undefined', 'It returns nothing useful', 'It is unused'], 0, 'Unreachable end.', 'Code after a call to it is unreachable.'),
]

CALC = [
    calc('e', 'The first example has two wrong lines. How many type errors does tsc report?', '2', 'One per mistake.', ['A string passed as a number, and a number stored in a string.']),
    calc('e', 'How many values does the type "chromium" | "firefox" | "webkit" allow?', '3', 'Count the literals.', ['Three browsers.']),
    calc('m', 'A tuple [string, number, boolean] has what length?', '3', 'Fixed positions.', ['Exactly three elements.']),
    calc('m', 'In the scenario, 4 rows were read. One has the status "pased" and one has ms "45". How many rows are valid?', '2', 'Both broken rows fail.', ['<span class="eq">4 − 2 = 2</span>']),
    calc('m', 'A type has 5 properties and 2 are optional. How many must every object provide?', '3', 'Required ones.', ['<span class="eq">5 − 2 = 3</span>']),
    calc('h', 'type A = "a" | "b" and type B = "x" | "y" | "z". How many combinations does the template type `${A}-${B}` allow?', '6', 'Every pairing.', ['<span class="eq">2 × 3 = 6</span>']),
    calc('h', 'A project turns on strict and tsc reports 120 errors. A team fixes 15 a day. How many days?', '8', 'Divide.', ['<span class="eq">120 ÷ 15 = 8</span>']),
    calc('x', 'How many of string, number, boolean, null, undefined remain after if (x == null) return, starting from all five?', '3', '== null removes both.', ['null and undefined are removed by == null.', 'string, number and boolean remain.']),
]

EX = [
    ex('isorder', 'e', 'A type guard', '<p>TypeScript guards are plain functions at run time. Write <code>isOrder(x)</code> that returns true only for objects with a string <code>id</code> and a number <code>total</code>. In TypeScript its signature would be <code>(x: unknown): x is Order</code>.</p>',
       'function isOrder(x) {\n  \n}\n',
       [('isOrder({ id: "ORD-1", total: 40 })', True), ('isOrder({ id: 1, total: 40 })', False), ('isOrder({ id: "ORD-1" })', False), ('isOrder(null)', False), ('isOrder("ORD-1")', False)],
       'function isOrder(x) {\n  return typeof x === "object" && x !== null && typeof x.id === "string" && typeof x.total === "number";\n}', hint='Check for null separately, because <code>typeof null</code> is "object".', why='The same checks narrow an unknown value in TypeScript.'),
    ex('describe', 'm', 'Handle a union', '<p>Write <code>describe(r)</code> for results shaped like <code>{ ok: true, data }</code> or <code>{ ok: false, status, error }</code>. Return "N items" for success, where N is the length of data, and "STATUS: ERROR" for failure.</p>',
       'function describe(r) {\n  \n}\n',
       [('describe({ ok: true, data: [1, 2, 3] })', '3 items'), ('describe({ ok: false, status: 503, error: "down" })', '503: down'), ('describe({ ok: true, data: [] })', '0 items')],
       'function describe(r) {\n  return r.ok ? `${r.data.length} items` : `${r.status}: ${r.error}`;\n}', hint='Check <code>r.ok</code> first, the same way TypeScript narrows a discriminated union.', why='In TypeScript, reading r.data in the failure branch would be a compile error.'),
    ex('browsers', 'h', 'An as const lookup', '<p>Write <code>BROWSERS</code> as a frozen object <code>{ Chromium: "chromium", Firefox: "firefox", Webkit: "webkit" }</code> and <code>isBrowser(name)</code> that returns true only for one of its values.</p>',
       'const BROWSERS = {};\nfunction isBrowser(name) {\n  \n}\n',
       [('isBrowser("firefox")', True), ('isBrowser("edge")', False), ('isBrowser("Chromium")', False), ('Object.isFrozen(BROWSERS) && BROWSERS.Webkit', 'webkit')],
       'const BROWSERS = Object.freeze({ Chromium: "chromium", Firefox: "firefox", Webkit: "webkit" });\nfunction isBrowser(name) {\n  return Object.values(BROWSERS).includes(name);\n}', hint='<code>Object.values</code> gives the list of allowed strings.', why='In TypeScript, as const plus this check gives a value of type Browser after the if.'),
    ex('safeget', 'x', 'Safe reads with defaults', '<p>With <code>noUncheckedIndexedAccess</code>, every read may be undefined. Write <code>at(list, index, fallback)</code> that returns the element, counting from the end for negative indexes, or <code>fallback</code> when it is missing. Keep real values such as 0 and "".</p>',
       'function at(list, index, fallback) {\n  \n}\n',
       [('at([10, 20, 30], 1, -1)', 20), ('at([10, 20, 30], -1, -1)', 30), ('at([10, 20], 5, -1)', -1), ('at([0, ""], 1, "x")', ''), ('at([0], 0, 9)', 0), ('at([], -1, "none")', 'none')],
       'function at(list, index, fallback) {\n  return list.at(index) ?? fallback;\n}', hint='<code>Array.prototype.at</code> handles negative indexes, and <code>??</code> only replaces undefined and null.', why='With || instead of ??, the 0 and "" cases would wrongly return the fallback.'),
]

T = {
    'slug': 'ts-basics', 'title': 'TypeScript fundamentals', 'short': 'TypeScript basics', 'emoji': '🔷', 'module': MODULE, 'minutes': 18,
    'lead': 'Start TypeScript the modern way: tsc to check and Node.js to run, a strict tsconfig, everyday types and inference, typed functions and overloads, interface and type, unions and narrowing, enums against as const objects, the strict options, and typed results from untyped JSON.',
    'desc': 'TypeScript fundamentals: tsc, tsconfig, type stripping, types, inference, unknown, any, never, functions, overloads, interface, type alias, union, narrowing, discriminated unions, enum, as const and strict mode.',
    'summary': 'What TypeScript is and how Node.js runs it, a modern tsconfig, everyday types, inference, readonly and unknown, typed functions, callbacks and overloads, interface against type, unions and narrowing, enum against as const, what strict mode catches, and reading untyped JSON safely with a type predicate.',
    'keywords': ['TypeScript', 'tsc', 'tsconfig', 'types', 'inference', 'unknown', 'any', 'interface', 'type alias', 'union', 'narrowing', 'enum', 'as const', 'strict', 'type predicate', 'interview'],
    'qa_intro': 'Most new automation projects use TypeScript. Typed locators, fixtures and API responses catch mistakes in test code before the suite even starts.',
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
