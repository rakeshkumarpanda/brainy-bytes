# Chapter 25a: how the TypeScript type system really decides: structural typing, excess property checks, literal widening,
# any, unknown and never, function compatibility and variance, index signatures, tuples, overloads and this, recursive types.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg, ts

MODULE = ('🔷', 'TypeScript', 'ts', 'TypeScript from the first type to generics, advanced types, typed projects and test automation written in TypeScript.')

CODES = {
    'structural': ts('''
interface Reporter {
  name: string;
  report(passed: number, failed: number): string;
}

// No "implements Reporter" anywhere: the shape is what counts
class ConsoleReporter {
  name = "console";
  colors = true;                                  // extra members are fine
  report(passed: number, failed: number) { return `${passed} passed, ${failed} failed`; }
}

const slackLike = { name: "slack", channel: "#qa", report: (p: number, f: number) => `:white_check_mark: ${p} :x: ${f}` };

function publish(r: Reporter) { console.log(`[${r.name}] ${r.report(41, 1)}`); }
publish(new ConsoleReporter());
publish(slackLike);                               // a variable with extra fields: allowed

publish({ name: "email", to: "qa@shop.test", report: () => "sent" });   // a fresh literal with an unknown field
try {
  publish({ name: "broken" });                                           // report is missing
} catch (e) {
  console.log("crashed:", (e as Error).message);
}
''', 'Structural typing: the shape decides, not the name', errors=2),
    'widening': ts('''
type Method = "GET" | "POST" | "PUT" | "DELETE";
function call(method: Method, path: string) { return `${method} ${path}`; }

const m1 = "GET";                 // const: the literal type "GET"
let m2 = "GET";                   // let: widened to string, because it may change later
const m3 = "POST" as Method;
const req = { method: "PUT", path: "/cart" };                 // method: string
const fixed = { method: "DELETE", path: "/cart/1" } as const; // method: "DELETE", and readonly

console.log(call(m1, "/products"));
console.log(call(m3, "/orders"));
console.log(call(fixed.method, fixed.path));

console.log(call(m2, "/products"));       // string is not assignable to Method
console.log(call(req.method, req.path));  // the same problem inside an object
fixed.path = "/other";                    // as const made it readonly
''', 'Literal types, widening and as const', errors=3),
    'unknown': ts('''
// any switches checking off. unknown means "we do not know yet, so check first".
const fromAny: any = JSON.parse('{"total": 42}');
const fromUnknown: unknown = JSON.parse('{"total": 42}');

if (typeof fromUnknown === "object" && fromUnknown !== null && "total" in fromUnknown && typeof fromUnknown.total === "number") {
  console.log("checked total:", fromUnknown.total.toFixed(2));
}

console.log(fromUnknown.total);         // not allowed before a check

// never is the empty type: a function that always throws returns never
function fail(message: string): never { throw new Error(message); }
const port: number = Number(process.env.PORT ?? "3000") || fail("PORT is not a number");
console.log(port);

console.log(fromAny.totl.toFixed(2));   // a typo that tsc cannot see through any: it crashes at run time
''', 'any, unknown and never', errors=1, expect='fail'),
    'functions': ts('''
type Listener = (event: string, at: number) => void;

const fewer: Listener = (event) => console.log("got", event);   // fewer parameters: fine
const returns: Listener = (event) => event.length;              // a value returned to a void callback: fine
fewer("click", Date.now());
returns("submit", Date.now());

class Animal { name = "any animal"; }
class Dog extends Animal { bark() { return "woof"; } }

let handleAnimal = (a: Animal) => console.log(a.name);
let handleDog = (d: Dog) => console.log(d.bark());

handleDog = handleAnimal;     // safe: something that handles any animal can handle a dog
handleDog(new Dog());

handleAnimal = handleDog;     // unsafe: it would call bark() on a cat (strictFunctionTypes)

// Variance annotations (TypeScript 4.7) document and check how T is used
interface Producer<out T> { next(): T }
interface Consumer<in T> { accept(value: T): void }
const dogs: Producer<Dog> = { next: () => new Dog() };
const animals: Producer<Animal> = dogs;              // out: Producer<Dog> is a Producer<Animal>
const anyAnimal: Consumer<Animal> = { accept: (a) => console.log("accepted", a.name) };
const forDogs: Consumer<Dog> = anyAnimal;            // in: works the other way round
console.log(animals.next().name);
forDogs.accept(new Dog());

interface Broken<in T> { get(): T }                  // T is used as output, so "in" is wrong
''', 'Function compatibility, variance and in/out', errors=2),
    'index': ts('''
// An index signature: any string key, number values
const timings: Record<string, number> = { login: 840, search: 312 };

const t1 = timings["checkout"];        // with noUncheckedIndexedAccess: number | undefined
console.log(t1 === undefined ? "no timing for checkout" : t1.toFixed(0));

const t2: number = timings["login"];   // might be undefined, so tsc refuses

const steps = ["open", "login", "pay"];
const last = steps[steps.length - 1];  // string | undefined too
console.log(last?.toUpperCase());

for (const [name, ms] of Object.entries(timings)) console.log(name, ms.toFixed(0));   // entries are safe

// exactOptionalPropertyTypes: "may be missing" is not the same as "may be undefined"
interface RunOptions { retries?: number }
const ok: RunOptions = {};
const notOk: RunOptions = { retries: undefined };
console.log(ok, notOk);
''', 'Index signatures and the two strictest options', errors=2, options={'noUncheckedIndexedAccess': True, 'exactOptionalPropertyTypes': True}),
    'tuples': ts('''
// Labeled, optional and rest elements
type Range = [start: number, end: number];
type Cell = [row: number, col: number, note?: string];
type Log = [level: "info" | "error", ...parts: string[]];

const r: Range = [10, 20];
const c: Cell = [1, 2];
const l: Log = ["error", "payment", "timeout"];
console.log(r, c, l);

// Variadic tuple types keep the exact shape when joining tuples
function concat<A extends unknown[], B extends unknown[]>(a: [...A], b: [...B]): [...A, ...B] {
  return [...a, ...b];
}
const joined = concat([1, "two"], [true]);     // [number, string, boolean]
const [n, s, b] = joined;
console.log(n.toFixed(1), s.toUpperCase(), b);

// Typing a function that forwards its arguments
function withRetry<Args extends unknown[], R>(fn: (...args: Args) => R, times: number) {
  return (...args: Args): R => { let last: unknown; for (let i = 0; i < times; i++) { try { return fn(...args); } catch (e) { last = e; } } throw last; };
}
const get = withRetry((path: string, timeout: number) => `GET ${path} in ${timeout} ms`, 3);
console.log(get("/health", 500));

get("/health");                               // the timeout argument is missing
const bad: Range = [1, 2, 3];                 // one too many
''', 'Labeled, optional, rest and variadic tuples', errors=2),
    'overloads': ts('''
// Overloads: several call signatures, one implementation
function parse(input: string): number;
function parse(input: string[]): number[];
function parse(input: string | string[]): number | number[] {
  return Array.isArray(input) ? input.map(Number) : Number(input);
}
const one = parse("42");              // number
const many = parse(["1", "2"]);       // number[]
console.log(one + 1, many.length);

// A "this" parameter says what this must be. It is erased from the JavaScript.
interface Button { label: string; clicks: number }
function onClick(this: Button) { this.clicks++; return `${this.label} clicked ${this.clicks} times`; }
const buy: Button & { click: typeof onClick } = { label: "Buy", clicks: 0, click: onClick };
console.log(buy.click());

// this as a return type gives fluent builders that keep the subclass type
class RequestBuilder {
  headers: Record<string, string> = {};
  header(k: string, v: string): this { this.headers[k] = v; return this; }
}
class AuthRequestBuilder extends RequestBuilder {
  token(t: string): this { return this.header("Authorization", `Bearer ${t}`); }
}
const built = new AuthRequestBuilder().header("Accept", "application/json").token("abc");
console.log(built.headers);

parse(42);                            // no overload takes a number
try {
  onClick();                          // called without a Button as this
} catch (e) {
  console.log("crashed:", (e as Error).message);
}
''', 'Overloads, this parameters and fluent this types', errors=2),
    'recursive': ts('''
// A type can refer to itself: this describes every value JSON.parse can return
type Json = string | number | boolean | null | Json[] | { [key: string]: Json };

const body: Json = { order: { id: 7, items: [{ sku: "PEN-1", qty: 2 }], paid: true, note: null } };

// Count every leaf value in a JSON tree, typed all the way down
function countLeaves(value: Json): number {
  if (value === null || typeof value !== "object") return 1;
  const children = Array.isArray(value) ? value : Object.values(value);
  return children.reduce<number>((sum, child) => sum + countLeaves(child), 0);
}
console.log("leaf values:", countLeaves(body));

// Recursive conditional type: all keys as dot paths, handy for typed config lookups
type Paths<T> = T extends object ? { [K in keyof T & string]: K | `${K}.${Paths<T[K]>}` }[keyof T & string] : never;
const config = { server: { port: 3000, tls: { enabled: false } }, retries: 2 };
type ConfigPath = Paths<typeof config>;
const p1: ConfigPath = "server.tls.enabled";
console.log(p1);

const date: Json = new Date();             // a Date is not JSON
const p2: ConfigPath = "server.host";      // no such path
''', 'Recursive types: JSON and dot paths', errors=2),
}

LANES = {
    'excess': {'t': 'How tsc checks one assignment',
               'code': 'interface Reporter { name: string; report(): string }\nconst slack = { name: "s", channel: "#qa", report: f };\nconst r1: Reporter = slack;\nconst r2: Reporter = { name: "e", to: "x", report: f };\nconst r3: Reporter = { name: "broken" };',
               'lanes': ['Value has', 'Reporter needs', 'Extra fields', 'tsc says'], 'tone': [1, 2, 3, 4],
               'steps': [{'l': 1, 'v': [[], ['name: string', 'report(): string'], [], []], 'm': 'The interface only lists what a Reporter must have. It says nothing about what it must not have.'},
                         {'l': 2, 'v': [['name', 'channel', 'report'], ['name: string', 'report(): string'], [], []], 'm': 'slack is an ordinary variable with three fields. Its type is inferred from the value.'},
                         {'l': 3, 'v': [['name', 'channel', 'report'], ['name: string', 'report(): string'], ['channel'], ['OK']], 'm': 'Every required member is there, so slack is a Reporter. The extra channel field is simply ignored. This is structural typing.'},
                         {'l': 4, 'v': [['name', 'to', 'report'], ['name: string', 'report(): string'], ['to'], ['error: unknown property to']], 'm': 'A fresh object literal written right where a Reporter is expected gets one extra check: unknown fields are probably typos, so tsc reports them.'},
                         {'l': 5, 'v': [['name'], ['name: string', 'report(): string'], [], ['error: report is missing']], 'm': 'A missing member is always an error, whether the value is fresh or not.'}]},
}

DG = {
    'variance': {'t': 'Which way can a type be swapped?', 'w': 900, 'h': 300, 'mw': 640,
        'n': [['dog', 40, 40, 200, 60, 'Dog', {'c': 1, 'sub': 'a special Animal'}], ['animal', 40, 190, 200, 60, 'Animal', {'c': 2, 'sub': 'the general type'}],
              ['pd', 340, 40, 220, 60, 'Producer<Dog>', {'c': 4, 'sub': 'gives dogs'}], ['pa', 340, 190, 220, 60, 'Producer<Animal>', {'c': 4, 'sub': 'gives animals'}],
              ['ca', 650, 40, 220, 60, 'Consumer<Animal>', {'c': 3, 'sub': 'takes any animal'}], ['cd', 650, 190, 220, 60, 'Consumer<Dog>', {'c': 3, 'sub': 'takes only dogs'}]],
        'e': [['dog', 'animal', {'t': 'is an', 'id': 'v1'}], ['pd', 'pa', {'t': 'usable as (out)', 'id': 'v2'}], ['ca', 'cd', {'t': 'usable as (in)', 'id': 'v3'}]],
        'st': [[['dog', 'animal', 'v1'], 'Every Dog is an Animal, so a Dog can go wherever an Animal is expected.'],
               [['pd', 'pa', 'v2'], 'Something that produces dogs can stand in for something that produces animals. The arrow points the same way. This is called covariance, marked out T.'],
               [['ca', 'cd', 'v3'], 'Something that accepts any animal can stand in for something that accepts dogs. The arrow flips. This is contravariance, marked in T.'],
               [['cd', 'ca'], 'The reverse is unsafe: a dog only handler given a cat would call bark() on it. strictFunctionTypes makes tsc catch this for function types.']]},
}

PARTS = [
    part('structural', '🧩', 'Structural typing: shapes, not names', '''
<p>In Java or C#, a class is a Reporter only if it says <code>implements Reporter</code>. TypeScript is <b>structural</b>: any value with the right members fits, whatever it is called. This matches how JavaScript code is really written, with plain objects passed around.</p>
[[structural]]
<div class="viz" data-viz="lanes" data-k="excess"></div>
<div class="tip">The excess property check is a typo detector, not a security feature. As the advanced chapter showed with the leaked password, a value from a variable may carry extra fields. API tests must still check that secret fields are absent.</div>
''', qa=True, qa_why='Mocks and test doubles work because any object with the right shape fits, without extending real classes.',
        kw=['structural typing', 'duck typing', 'assignability', 'excess property check', 'fresh object literal', 'implements', 'nominal typing']),
    part('widening', '📏', 'Literal types and widening', '''
<p>A value can have a very exact type. <code>const m = "GET"</code> has the type <code>"GET"</code>, a <b>literal type</b>. A <code>let</code> may change later, so TypeScript <b>widens</b> it to <code>string</code>. Object properties are widened too. <code>as const</code> stops widening and makes everything readonly.</p>
[[widening]]
<div class="note">This is the most common surprise for beginners: a value that looks exactly right is "string" to TypeScript. Use <code>as const</code>, a type annotation, or <code>satisfies</code> to keep the literal.</div>
''', kw=['literal types', 'widening', 'as const', 'const vs let', 'readonly', 'union of literals', 'string is not assignable']),
    part('unknown', '❓', 'any, unknown and never', '''
<p><code>any</code> turns checking off for a value and everything you reach through it, so mistakes spread silently. <code>unknown</code> accepts any value too, but you must check it before use. <code>never</code> is the type with no values, used for functions that never return and for impossible cases.</p>
[[unknown]]
<p>The program compiled with <code>any</code> but crashed on the typo <code>totl</code>. With <code>unknown</code> the same mistake is impossible, because nothing can be read before a check.</p>
<div class="tw"><table class="jt"><tr><th>Type</th><th>Accepts</th><th>You can use it as</th></tr>
<tr><td><code>any</code></td><td>everything</td><td>anything, with no checks</td></tr>
<tr><td><code>unknown</code></td><td>everything</td><td>nothing, until you narrow it</td></tr>
<tr><td><code>never</code></td><td>nothing</td><td>anything, since it cannot happen</td></tr></table></div>
''', qa=True, qa_why='Response bodies and test data files are unknown until checked. Using any there hides wrong field names until a test crashes.',
        kw=['any', 'unknown', 'never', 'top type', 'bottom type', 'type narrowing', 'JSON.parse', 'noImplicitAny']),
    part('functions', '🔁', 'Function compatibility and variance', '''
<p>When is one function type usable as another? Fewer parameters is fine, because JavaScript ignores extra arguments. A callback that returns a value is fine where <code>void</code> is expected. Parameter types are where it gets subtle.</p>
<div class="viz" data-viz="flow" data-k="variance"></div>
[[functions]]
<div class="tip">Methods written as <code>method(x: T): void</code> in an interface are still checked loosely (bivariantly) for compatibility with old code. Writing them as properties, <code>method: (x: T) =&gt; void</code>, gets the strict check.</div>
''', kw=['function compatibility', 'variance', 'covariance', 'contravariance', 'bivariance', 'strictFunctionTypes', 'in T', 'out T', 'variance annotations', 'callback types']),
    part('index', '🗂️', 'Index signatures and the strictest options', '''
<p>An <b>index signature</b>, <code>{ [key: string]: number }</code> or <code>Record&lt;string, number&gt;</code>, describes objects used as dictionaries. By default TypeScript pretends every key exists. Two options, not included in <code>strict</code>, make it honest.</p>
[[index]]
<div class="tw"><table class="jt"><tr><th>Option</th><th>Effect</th></tr>
<tr><td><code>noUncheckedIndexedAccess</code></td><td><code>obj[key]</code> and <code>arr[i]</code> may be undefined</td></tr>
<tr><td><code>exactOptionalPropertyTypes</code></td><td><code>retries?: number</code> may be missing, but not set to undefined</td></tr></table></div>
<div class="note">Many teams turn on noUncheckedIndexedAccess in test code, where lookups by name ("the row for asha") are common and a missing row should be handled, not crash.</div>
''', qa=True, qa_why='Lookups in test data maps and table rows by index are exactly where undefined sneaks in.',
        kw=['index signature', 'Record<string, T>', 'noUncheckedIndexedAccess', 'exactOptionalPropertyTypes', 'dictionary', 'undefined', 'optional property']),
    part('tuples', '📦', 'Tuples: fixed length arrays with names', '''
<p>A <b>tuple</b> is an array with a fixed length and a type per position. Elements can have labels, be optional, or be a rest of many. <b>Variadic tuple types</b>, <code>[...A, ...B]</code>, keep exact shapes when functions combine or forward argument lists, which is how wrappers such as retry helpers stay fully typed.</p>
[[tuples]]
''', kw=['tuple', 'labeled tuple', 'optional element', 'rest element', 'variadic tuple types', '...args', 'Parameters', 'higher order function']),
    part('overloads', '🔀', 'Overloads and this', '''
<p><b>Overloads</b> give one function several typed call signatures, so the return type follows the argument type. A <b>this parameter</b> says what <code>this</code> must be when the function runs, and a <code>this</code> return type lets builder methods keep the subclass type, so chained calls do not lose methods.</p>
[[overloads]]
<div class="tip">Prefer a union parameter or a generic when they are enough. Overloads are best when different inputs give clearly different outputs, as in <code>parse</code> above or <code>document.createElement</code>.</div>
''', qa=['Playwright'], qa_why='Page object and request builder chains keep their subclass methods thanks to this return types.',
        kw=['overloads', 'call signatures', 'this parameter', 'this type', 'fluent interface', 'builder pattern', 'method chaining']),
    part('recursive', '🌳', 'Recursive types', '''
<p>A type may refer to itself. That is how trees are described: JSON, file systems, menus, nested config. Recursive conditional types go further and compute types such as every dot path in an object.</p>
[[recursive]]
<div class="note">Very deep recursive types make tsc slow and give long error messages. Keep them for shared building blocks, such as a typed config reader, not for every object.</div>
''', kw=['recursive types', 'Json type', 'tree', 'recursive conditional types', 'dot paths', 'template literal types', 'typed config']),
]

INFO = {'title': 'How the checker thinks', 'panels': [
    panel([['e', '🧩'], ['t', 'shape, not name', {'b': 1}]], 'Structural', 'Right members, right type.', 'Fresh literals also get a typo check.'),
    panel([['e', '📏'], ['t', 'let m = "GET"  // string', {'b': 1, 'size': 11}]], 'Widening', 'let and objects widen.', 'as const keeps the literal.'),
    panel([['e', '❓'], ['t', 'unknown, not any', {'b': 1}]], 'Unknown', 'Check before you use.', 'any hides mistakes.'),
    panel([['e', '🔁'], ['t', 'Producer<out T>', {'b': 1}]], 'Variance', 'Producers follow, consumers flip.', 'strictFunctionTypes keeps callbacks safe.')],
    'remember': 'TypeScript compares shapes, widens let and object values, wants unknown checked before use, and compares function parameters in the opposite direction to return values.'}

REAL = [
    ['🧪', 'A test team', 'Replaced a heavy mocking library with plain objects that match the interface. Structural typing made them valid test doubles with no casts.'],
    ['🐛', 'An API client', 'Typed every response as unknown and checked it once. A renamed field in the backend became a clear error instead of an undefined value deep in a report.'],
    ['🔁', 'A retry helper', 'Used variadic tuple types, so wrapping any function with retries kept its exact arguments and return type.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter explains how the TypeScript checker decides: structural typing, widening, unknown, variance, index signatures, tuples, overloads and recursive types.',
        'यह अध्याय बताता है कि TypeScript checker कैसे तय करता है: structural typing, widening, unknown, variance, index signatures, tuples, overloads और recursive types।',
        'TypeScript checker ಹೇಗೆ ನಿರ್ಧರಿಸುತ್ತದೆ ಎಂದು ಈ ಅಧ್ಯಾಯ ವಿವರಿಸುತ್ತದೆ.',
        'TypeScript checker କିପରି ନିଷ୍ପତ୍ତି ନିଏ ଏହି ଅଧ୍ୟାୟ ବୁଝାଏ।',
        'يشرح هذا الفصل كيف يقرر مدقق TypeScript: الأنواع البنيوية والتوسيع وunknown والتباين والفهارس والصفوف والتحميل الزائد والأنواع العودية.',
        'Dieses Kapitel erklärt, wie der TypeScript-Checker entscheidet: strukturelle Typen, Widening, unknown, Varianz, Index-Signaturen, Tupel, Überladungen und rekursive Typen.'),
    say('structural', 'Structural typing', 'Any value with the right members fits a type, whatever its name. Only fresh object literals are checked for unknown extra fields.',
        'सही members वाली कोई भी value type में फिट होती है, नाम कुछ भी हो। केवल नए object literals में अनजान extra fields जांचे जाते हैं।',
        'ಸರಿಯಾದ members ಇರುವ ಯಾವುದೇ value type ಗೆ ಹೊಂದುತ್ತದೆ.',
        'ଠିକ୍ members ଥିବା ଯେକୌଣସି value type ରେ ଫିଟ୍ ହୁଏ।',
        'أي قيمة تملك الأعضاء الصحيحة تناسب النوع مهما كان اسمها، ولا تُفحص الحقول الزائدة إلا في الكائنات الحرفية الجديدة.',
        'Jeder Wert mit den richtigen Mitgliedern passt zu einem Typ, egal wie er heißt. Nur frische Objektliterale werden auf unbekannte Felder geprüft.'),
    say('widening', 'Widening', 'const keeps a literal type, but let and object properties widen to string. as const keeps the exact values and makes them readonly.',
        'const literal type रखता है, लेकिन let और object properties string बन जाते हैं। as const सटीक values रखता है और readonly बनाता है।',
        'const literal type ಉಳಿಸುತ್ತದೆ, let string ಆಗುತ್ತದೆ. as const readonly.',
        'const literal type ରଖେ, let string ହୁଏ। as const readonly।',
        'يحتفظ const بالنوع الحرفي، أما let وخصائص الكائنات فتتوسع إلى string، ويحفظ as const القيم الدقيقة ويجعلها للقراءة فقط.',
        'const behält den Literaltyp, let und Objekteigenschaften werden zu string. as const behält die genauen Werte und macht sie readonly.'),
    say('unknown', 'Unknown', 'any turns checking off. unknown accepts everything but must be checked before use. never has no values at all.',
        'any checking बंद कर देता है। unknown सब स्वीकार करता है पर इस्तेमाल से पहले जांचना पड़ता है। never की कोई value नहीं होती।',
        'any checking ನಿಲ್ಲಿಸುತ್ತದೆ. unknown ಬಳಸುವ ಮೊದಲು ಪರಿಶೀಲಿಸಬೇಕು.',
        'any checking ବନ୍ଦ କରେ। unknown ବ୍ୟବହାର ପୂର୍ବରୁ ଯାଞ୍ଚ କରିବାକୁ ପଡ଼େ।',
        'يوقف any الفحص، ويقبل unknown كل شيء لكن يجب فحصه قبل الاستخدام، وليس لـ never أي قيم.',
        'any schaltet die Prüfung ab. unknown nimmt alles an, muss aber vor Gebrauch geprüft werden. never hat gar keine Werte.'),
    say('functions', 'Variance', 'A function with fewer parameters fits. A handler for any animal can replace a handler for dogs, but not the other way round.',
        'कम parameters वाला function फिट होता है। हर animal का handler dog handler की जगह ले सकता है, उल्टा नहीं।',
        'ಕಡಿಮೆ parameters ಇರುವ function ಹೊಂದುತ್ತದೆ. Animal handler dog handler ಬದಲು ಬರಬಹುದು.',
        'କମ୍ parameters ଥିବା function ଫିଟ୍ ହୁଏ। Animal handler dog handler ବଦଳରେ ଆସିପାରେ।',
        'الدالة ذات المعاملات الأقل تناسب، ومعالج أي حيوان يمكن أن يحل محل معالج الكلاب، لا العكس.',
        'Eine Funktion mit weniger Parametern passt. Ein Handler für jedes Tier kann einen Hunde-Handler ersetzen, aber nicht umgekehrt.'),
    say('index', 'Index signatures', 'With noUncheckedIndexedAccess, reading a dictionary key or an array index may give undefined, so you must handle the missing case.',
        'noUncheckedIndexedAccess के साथ dictionary key या array index पढ़ने पर undefined मिल सकता है, इसलिए missing case संभालना पड़ता है।',
        'noUncheckedIndexedAccess ಜೊತೆ undefined ಸಿಗಬಹುದು.',
        'noUncheckedIndexedAccess ସହ undefined ମିଳିପାରେ।',
        'مع noUncheckedIndexedAccess قد تعطي قراءة مفتاح أو فهرس القيمة undefined، فيجب التعامل مع الحالة المفقودة.',
        'Mit noUncheckedIndexedAccess kann ein Schlüssel oder Index undefined liefern, also muss der fehlende Fall behandelt werden.'),
    say('tuples', 'Tuples', 'A tuple has a fixed length and a type per position. Variadic tuples keep exact argument lists when wrapping functions.',
        'Tuple की लंबाई तय होती है और हर position का type। Variadic tuples functions लपेटते समय सटीक arguments रखते हैं।',
        'Tuple ನಿಗದಿತ ಉದ್ದ, ಪ್ರತಿ ಸ್ಥಾನಕ್ಕೆ type.',
        'Tuple ନିର୍ଦ୍ଦିଷ୍ଟ ଲମ୍ବ, ପ୍ରତି ସ୍ଥାନ ପାଇଁ type।',
        'للصف طول ثابت ونوع لكل موضع، وتحفظ الصفوف المتغيرة قوائم الوسائط الدقيقة عند تغليف الدوال.',
        'Ein Tupel hat feste Länge und einen Typ je Position. Variadische Tupel behalten genaue Argumentlisten beim Umhüllen von Funktionen.'),
    say('overloads', 'Overloads', 'Overloads give one function several call signatures. A this return type keeps builder chains typed.',
        'Overloads एक function को कई call signatures देते हैं। this return type builder chains को typed रखता है।',
        'Overloads ಒಂದು function ಗೆ ಹಲವು signatures. this return type chains ಉಳಿಸುತ್ತದೆ.',
        'Overloads ଗୋଟିଏ function କୁ ଅନେକ signatures। this return type chains ରଖେ।',
        'يعطي التحميل الزائد الدالة عدة تواقيع، ويحفظ نوع الإرجاع this سلاسل البناء مكتوبة الأنواع.',
        'Überladungen geben einer Funktion mehrere Signaturen. Ein this-Rückgabetyp hält Builder-Ketten typisiert.'),
    say('recursive', 'Recursive types', 'A type can refer to itself, which describes trees such as JSON. Recursive conditional types can list every dot path of an object.',
        'Type खुद को refer कर सकता है, जिससे JSON जैसे trees बनते हैं। Recursive conditional types object के सभी dot paths बता सकते हैं।',
        'Type ತನ್ನನ್ನೇ ಸೂಚಿಸಬಹುದು, JSON ನಂತಹ trees.',
        'Type ନିଜକୁ refer କରିପାରେ, JSON ପରି trees।',
        'يمكن للنوع أن يشير إلى نفسه فيصف أشجارًا مثل JSON، ويمكن للأنواع الشرطية العودية سرد كل مسارات الكائن.',
        'Ein Typ kann sich selbst referenzieren und so Bäume wie JSON beschreiben. Rekursive bedingte Typen listen alle Punkt-Pfade eines Objekts.'),
    say('practice', 'Hands-on', 'Practise a structural check, a JSON leaf counter, a dot path reader and a safe dictionary lookup.',
        'Structural check, JSON leaf counter, dot path reader और सुरक्षित dictionary lookup का अभ्यास करें।',
        'Structural check, JSON leaf counter, dot path reader ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Structural check, JSON leaf counter, dot path reader ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرّب على فحص بنيوي وعداد أوراق JSON وقارئ مسارات وبحث آمن في القاموس.',
        'Übe eine Strukturprüfung, einen JSON-Blattzähler, einen Pfadleser und einen sicheren Wörterbuchzugriff.'),
]

QUIZ = [
    quiz('e', 'A class has every member of an interface but does not say implements. Can it be used as that interface?', ['Yes, TypeScript compares shapes', 'No, implements is required', 'Only with a cast', 'Only at run time'], 0, 'Structural typing.', 'The name and the implements clause do not matter, the members do.'),
    quiz('e', 'What is the type of <code>let m = "GET"</code>?', ['string', '"GET"', 'any', 'unknown'], 0, 'let may change.', 'let widens literals. const m = "GET" would keep "GET".'),
    quiz('e', 'Which type must be checked before you can use the value?', ['unknown', 'any', 'never', 'object'], 0, 'The safe top type.', 'any allows everything without checks, which hides mistakes.'),
    quiz('m', 'Why does <code>{ name: "x", to: "y", report }</code> passed directly to a Reporter parameter fail, when the same object in a variable passes?', ['Fresh object literals get an excess property check for typos', 'Variables are not type checked', 'Literals are always any', 'to is a reserved word'], 0, 'Freshness.', 'Only a literal written in place is checked for unknown fields.'),
    quiz('m', 'What does <code>as const</code> do to <code>{ method: "GET" }</code>?', ['Keeps method as the literal "GET" and makes it readonly', 'Converts it to a string', 'Freezes it at run time', 'Removes the property'], 0, 'No widening.', 'It is compile time only, Object.freeze would be needed at run time.'),
    quiz('m', 'With noUncheckedIndexedAccess, what is the type of <code>arr[0]</code> for <code>arr: string[]</code>?', ['string | undefined', 'string', 'never', 'unknown'], 0, 'The index may not exist.', 'You must check it or use optional chaining.'),
    quiz('m', 'Can <code>(a: Animal) =&gt; void</code> be assigned to a variable of type <code>(d: Dog) =&gt; void</code>?', ['Yes, a handler for any animal can handle a dog', 'No, never', 'Only with any', 'Only for classes'], 0, 'Parameters flip.', 'That is contravariance of parameter types.'),
    quiz('h', 'What does <code>out T</code> in <code>interface Producer&lt;out T&gt;</code> declare?', ['T is only produced, so Producer<Dog> is assignable to Producer<Animal>', 'T is optional', 'T is exported', 'T is a return type of void'], 0, 'Covariance.', 'tsc reports an error if T is used as an input inside the interface.'),
    quiz('h', 'What does a return type of <code>this</code> in a builder method give?', ['Chained calls keep the subclass type and its extra methods', 'The method becomes static', 'It returns a copy', 'It prevents subclassing'], 0, 'Fluent subclasses.', 'header() on AuthRequestBuilder still returns AuthRequestBuilder.'),
    quiz('h', 'With exactOptionalPropertyTypes, is <code>{ retries: undefined }</code> a valid <code>{ retries?: number }</code>?', ['No, the property may be missing but not undefined', 'Yes, always', 'Only in strict mode', 'Only for numbers'], 0, 'Missing is not undefined.', 'This matters for APIs where sending a field as undefined differs from leaving it out.'),
    quiz('x', 'What is the type of <code>concat([1], ["a", true])</code> with <code>[...A, ...B]</code> as the return type?', ['[number, string, boolean]', '(string | number | boolean)[]', 'unknown[]', 'never'], 0, 'Variadic tuples keep positions.', 'Each position keeps its own type.'),
    quiz('x', 'Which value is not a valid Json in the recursive Json type?', ['new Date()', 'null', '[1, "a"]', '{ "a": { "b": [] } }'], 0, 'Only JSON values.', 'A Date is an object with methods, not a plain JSON object of Json values.'),
]

CALC = [
    calc('e', 'An interface needs 2 members and an object has those plus 3 extra. How many extra members does tsc ignore when the object comes from a variable?', '3', 'Extra members are ignored for variables.', ['Only fresh literals are checked for extras.']),
    calc('e', 'How many values does <code>"GET" | "POST" | "PUT" | "DELETE"</code> allow?', '4', 'Count the literals.', ['One per member.']),
    calc('m', 'A tuple type <code>[row: number, col: number, note?: string]</code>. What is the largest allowed length?', '3', 'The optional element counts when present.', ['Allowed lengths are 2 and 3.']),
    calc('m', 'A Log tuple is <code>[level, ...parts: string[]]</code>. How many parts does <code>["error", "payment", "timeout"]</code> have?', '2', 'Everything after the level.', ['<span class="eq">3 − 1 = 2</span>']),
    calc('h', 'How many leaf values does <code>{ a: 1, b: [true, null], c: { d: "x" } }</code> have?', '4', 'Count values that are not arrays or objects.', ['1, true, null and "x".']),
    calc('h', 'How many dot paths does Paths give for <code>{ server: { port: 3000 }, retries: 2 }</code>?', '3', 'Each key, plus nested paths.', ['"server", "server.port" and "retries".']),
    calc('x', 'A function has 2 overload signatures and 1 implementation signature. How many signatures can callers see?', '2', 'The implementation signature is hidden.', ['Only the overloads are visible from outside.']),
]

EX = [
    ex('fits', 'e', 'Does it fit the shape?', '<p>Write <code>fits(obj, keys)</code> that returns true when <code>obj</code> is a non null object that has every key in <code>keys</code>, like a structural type check at run time. Extra keys are fine.</p>',
       'function fits(obj, keys) {\n  \n}\n',
       [('fits({ name: "x", report() {}, channel: "#qa" }, ["name", "report"])', True), ('fits({ name: "x" }, ["name", "report"])', False), ('fits(null, ["name"])', False), ('fits({}, [])', True)],
       'function fits(obj, keys) {\n  return typeof obj === "object" && obj !== null && keys.every(k => k in obj);\n}', hint='Check for an object first, then use <code>every</code> with <code>in</code>.', why='This is what structural typing means: required members must be present, extras are allowed.'),
    ex('leaves', 'm', 'Count JSON leaves', '<p>Write <code>countLeaves(value)</code> that counts every value in a JSON tree that is not an array or an object. null counts as a leaf.</p>',
       'function countLeaves(value) {\n  \n}\n',
       [('countLeaves({ a: 1, b: [true, null], c: { d: "x" } })', 4), ('countLeaves([])', 0), ('countLeaves(5)', 1), ('countLeaves({ order: { items: [{ qty: 2 }, { qty: 3 }] } })', 2)],
       'function countLeaves(value) {\n  if (value === null || typeof value !== "object") return 1;\n  const children = Array.isArray(value) ? value : Object.values(value);\n  return children.reduce((sum, child) => sum + countLeaves(child), 0);\n}', hint='Recursion: a leaf is 1, a container is the sum of its children.', why='The recursive Json type and the recursive function have the same shape.'),
    ex('getpath', 'h', 'Read a dot path', '<p>Write <code>getPath(obj, path)</code> that follows a dot path such as <code>"server.tls.enabled"</code> and returns the value, or <code>undefined</code> if any step is missing.</p>',
       'function getPath(obj, path) {\n  \n}\n',
       [('getPath({ server: { tls: { enabled: false } } }, "server.tls.enabled")', False), ('getPath({ server: { port: 3000 } }, "server.host") === undefined', True), ('getPath({ a: { b: 0 } }, "a.b")', 0), ('getPath({}, "x.y.z") === undefined', True)],
       'function getPath(obj, path) {\n  return path.split(".").reduce((cur, key) => (cur == null ? undefined : cur[key]), obj);\n}', hint='Split on dots and walk with <code>reduce</code>, stopping at null or undefined.', why='With the Paths type, a wrong path is a compile error. At run time the function still handles missing steps safely.'),
    ex('lookup', 'x', 'A safe dictionary lookup', '<p>Write <code>lookup(map, key, fallback)</code> that returns <code>map[key]</code> only if the key is the object\'s own property, otherwise the fallback. Keys such as <code>"toString"</code> that come from the prototype must give the fallback.</p>',
       'function lookup(map, key, fallback) {\n  \n}\n',
       [('lookup({ login: 840 }, "login", 0)', 840), ('lookup({ login: 840 }, "pay", -1)', -1), ('lookup({}, "toString", "none")', 'none'), ('lookup({ zero: 0 }, "zero", 5)', 0)],
       'function lookup(map, key, fallback) {\n  return Object.hasOwn(map, key) ? map[key] : fallback;\n}', hint='<code>Object.hasOwn</code> checks only the object\'s own keys.', why='This is the run time version of what noUncheckedIndexedAccess forces you to think about: a key may be missing.'),
]

T = {
    'slug': 'ts-type-system', 'title': 'How the TypeScript type system decides', 'short': 'The type system', 'emoji': '🧠', 'module': MODULE, 'minutes': 22,
    'lead': 'Why does one object fit and an almost identical one fail? This chapter explains the rules the checker follows: structural typing and the excess property check, literal types and widening, any, unknown and never, function compatibility and variance, index signatures with the strictest options, tuples, overloads and this, and recursive types.',
    'desc': 'The TypeScript type system in depth: structural typing, excess property checks, literal types, widening, as const, any vs unknown vs never, function compatibility, covariance and contravariance, in and out variance annotations, index signatures, noUncheckedIndexedAccess, exactOptionalPropertyTypes, variadic tuples, overloads, this types and recursive types.',
    'summary': 'Structural typing with an animated assignment check, literal widening and as const, any versus unknown versus never, function compatibility and variance with in and out, safe dictionary lookups, labeled and variadic tuples, overloads and fluent this types, and recursive Json and dot path types.',
    'keywords': ['structural typing', 'excess property check', 'widening', 'as const', 'unknown', 'never', 'variance', 'strictFunctionTypes', 'noUncheckedIndexedAccess', 'exactOptionalPropertyTypes', 'tuples', 'overloads', 'this type', 'recursive types', 'interview'],
    'qa_intro': 'Most confusing type errors in test code come from three rules in this chapter: excess property checks, widening of literals, and values that are any instead of unknown.',
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
