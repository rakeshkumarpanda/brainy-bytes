# Chapter 23: advanced TypeScript: generics, keyof and indexed access, utility types, mapped and conditional types, template literal types, satisfies, exhaustive checks, assertion functions and branded types.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg, ts

MODULE = ('🔷', 'TypeScript', 'ts', 'TypeScript from the first type to generics, advanced types, typed projects and test automation written in TypeScript.')

CODES = {
    'generics': ts('''
// A generic function keeps the link between input and output types
function first<T>(items: readonly T[]): T | undefined {
  return items[0];
}
const id = first([101, 102]);            // number | undefined
const tag = first(["smoke", "cart"]);    // string | undefined

// Constraints: T must have at least these fields
function slowest<T extends { ms: number }>(results: T[]): T {
  return results.reduce((a, b) => (b.ms > a.ms ? b : a));
}
const top = slowest([{ name: "login", ms: 840 }, { name: "checkout", ms: 2310 }]);
console.log(id, tag, top.name);                 // top keeps its name field

// A generic type with a default
type ApiResponse<T, E = { message: string }> = { status: number; data?: T; error?: E };
const res: ApiResponse<{ id: number }> = { status: 201, data: { id: 7 } };
console.log(res.data?.id);

slowest([{ name: "x" }]);                       // missing ms
''', 'Generic functions, constraints and generic types', errors=1),
    'keyof': ts('''
const defaults = { baseURL: "http://localhost:3000", timeout: 5000, headless: true };

type Config = typeof defaults;                 // the type of a value
type ConfigKey = keyof Config;                 // "baseURL" | "timeout" | "headless"
type Timeout = Config["timeout"];              // indexed access: number

// K is one of the keys, and the return type follows it
function setting<K extends ConfigKey>(key: K, overrides: Partial<Config> = {}): Config[K] {
  return overrides[key] ?? defaults[key];
}
const t: Timeout = setting("timeout", { timeout: 10_000 });
const h = setting("headless");                 // boolean
console.log(t, h, setting("baseURL"));

setting("timout");                             // typo caught
const n: number = setting("baseURL");          // wrong type caught
''', 'typeof, keyof and indexed access types', errors=2),
    'utility': ts('''
interface User { id: number; email: string; name: string; role: "admin" | "customer"; password: string }

type NewUser = Omit<User, "id">;                      // what a create request sends
type PublicUser = Omit<User, "password">;             // what the API may return
type UserPatch = Partial<Pick<User, "name" | "email">>;
type Lookup = Record<User["role"], User[]>;
type Frozen = Readonly<User>;

async function fetchUser(): Promise<PublicUser> { return { id: 1, email: "a@shop.test", name: "Asha", role: "admin" }; }
type Fetched = Awaited<ReturnType<typeof fetchUser>>;
type Args = Parameters<typeof setting>;
function setting(name: string, fallback?: number) { return fallback ?? 0; }

const draft: NewUser = { email: "r@shop.test", name: "Ravi", role: "customer", password: "s3cret!" };
const patch: UserPatch = { name: "Ravi K" };
const leaked: PublicUser = { ...draft, id: 2 };      // extra password field in an object literal is allowed via spread
const byRole: Lookup = { admin: [], customer: [] };
const args: Args = ["timeout", 5000];
const u: Fetched = await fetchUser();
console.log(Object.keys(draft).length, patch, Object.keys(byRole), args, u.name, "password" in leaked);

const bad: PublicUser = { id: 3, email: "x", name: "X", role: "customer", password: "oops" };
const frozen: Frozen = u as User;
frozen.name = "changed";
''', 'Utility types: Partial, Pick, Omit, Record, ReturnType and Awaited', errors=2),
    'mapped': ts('''
// Mapped types build a new type from every key of another
type Flags<T> = { [K in keyof T]: boolean };
type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };
type Mutable<T> = { -readonly [K in keyof T]: T[K] };

interface Settings { readonly retries: number; readonly browser: string }
const changed: Flags<Settings> = { retries: true, browser: false };
const getters: Getters<Settings> = { getRetries: () => 2, getBrowser: () => "firefox" };
const m: Mutable<Settings> = { retries: 1, browser: "webkit" };
m.retries = 3;

// Conditional types choose a type, and infer pulls a type out of another
type ElementOf<T> = T extends readonly (infer E)[] ? E : never;
type Unwrap<T> = T extends Promise<infer V> ? V : T;
type NonEmpty<T> = T extends "" | null | undefined ? never : T;

const e: ElementOf<string[]> = "ok";
const v: Unwrap<Promise<number>> = 42;
type Clean = NonEmpty<"a" | "" | null | "b">;          // "a" | "b"
const c: Clean = "b";
console.log(changed, getters.getBrowser(), m.retries, e, v, c);

const wrong: Clean = "";
''', 'Mapped and conditional types with infer', errors=1),
    'template': ts('''
// Template literal types describe string patterns
type Method = "GET" | "POST" | "DELETE";
type Version = "v1" | "v2";
type Route = `/${Version}/${"users" | "orders"}`;
type Endpoint = `${Method} ${Route}`;                 // 3 × 2 × 2 = 12 strings

type TestId = `${"btn" | "input" | "link"}-${string}`;
type CssSize = `${number}px` | `${number}%`;

const call: Endpoint = "POST /v1/orders";
const loc: TestId = "btn-checkout";
const width: CssSize = "50%";

// Event names from a type, as typed event emitters do
type Events = { pass: { name: string }; fail: { name: string; error: string } };
type Handler = { [E in keyof Events as `on${Capitalize<E>}`]: (e: Events[E]) => void };
const reporter: Handler = { onPass: e => console.log("✔", e.name), onFail: e => console.log("✖", e.name, e.error) };
reporter.onFail({ name: "cart", error: "expected 2" });
console.log(call, loc, width);

const typo: Endpoint = "PUT /v1/orders";
const badId: TestId = "button-checkout";
''', 'Template literal types', errors=2),
    'satisfies': ts('''
type Browser = "chromium" | "firefox" | "webkit";
type Project = { browser: Browser; retries?: number; baseURL?: string };

// A type annotation widens: the exact keys and values are lost
const annotated: Record<string, Project> = { desktop: { browser: "chromium" }, mobile: { browser: "webkit", retries: 2 } };
annotated.tablet;                              // allowed, but undefined at run time

// satisfies checks the shape and keeps the precise type
const projects = {
  desktop: { browser: "chromium" },
  mobile: { browser: "webkit", retries: 2 },
} satisfies Record<string, Project>;

projects.mobile.retries.toFixed(0);            // known to exist, no undefined check needed
console.log(Object.keys(projects), projects.mobile.retries);
projects.tablet;                               // now a typo is caught

const broken = { desktop: { browser: "edge" } } satisfies Record<string, Project>;
''', 'satisfies: check without widening', errors=2),
    'exhaustive': ts('''
type Step =
  | { kind: "goto"; url: string }
  | { kind: "click"; selector: string }
  | { kind: "fill"; selector: string; value: string }
  | { kind: "expectText"; selector: string; text: string };

function assertNever(x: never): never { throw new Error(`unhandled step ${JSON.stringify(x)}`); }

function describe(step: Step): string {
  switch (step.kind) {
    case "goto": return `open ${step.url}`;
    case "click": return `click ${step.selector}`;
    case "fill": return `type "${step.value}" into ${step.selector}`;
    case "expectText": return `check ${step.selector} shows "${step.text}"`;
    default: return assertNever(step);           // a new kind of step without a case is a compile error
  }
}

const script: Step[] = [
  { kind: "goto", url: "/login" },
  { kind: "fill", selector: "#email", value: "asha@shop.test" },
  { kind: "click", selector: "button[type=submit]" },
  { kind: "expectText", selector: "h1", text: "Welcome" },
];
console.log(script.map(describe));

function describeOld(step: Step): string {
  switch (step.kind) {
    case "goto": return "open";
    case "click": return "click";
    default: return assertNever(step);           // fill and expectText are missing
  }
}
''', 'Discriminated unions with an exhaustive check', errors=1),
    'assertions': ts('''
// An assertion function narrows the type for the rest of the scope, or throws
function assertDefined<T>(value: T, label: string): asserts value is NonNullable<T> {
  if (value === undefined || value === null) throw new Error(`${label} is missing`);
}

// Branded types: same run time value, different compile time type
type OrderId = string & { readonly __brand: "OrderId" };
type UserId = string & { readonly __brand: "UserId" };
const asOrderId = (s: string): OrderId => {
  if (!/^ORD-\\d{6}$/.test(s)) throw new RangeError(`bad order id ${s}`);
  return s as OrderId;
};

function cancelOrder(id: OrderId) { return `cancelled ${id}`; }

const env = { BASE_URL: "http://localhost:3000" } as Record<string, string | undefined>;
const base = env.BASE_URL;
assertDefined(base, "BASE_URL");
console.log(base.toUpperCase());              // string from here on

const order = asOrderId("ORD-104233");
console.log(cancelOrder(order));
const user = "USR-7" as UserId;
cancelOrder(user);                            // a user id where an order id is needed
cancelOrder("ORD-000001");                    // a plain string is not an OrderId either
''', 'Assertion functions and branded types', errors=2),
    'scenario': ts('''
// Typed routes: the path decides the response type, so tests cannot misread a body
interface Routes {
  "GET /products": { id: string; price: number }[];
  "GET /products/:id": { id: string; price: number; stock: number };
  "POST /orders": { orderId: string; total: number };
}

type Params<P extends string> = P extends `${string}:${infer Name}/${infer Rest}`
  ? { [K in Name]: string } & Params<`/${Rest}`>
  : P extends `${string}:${infer Name}` ? { [K in Name]: string } : {};

async function call<R extends keyof Routes>(route: R, params: Params<R & string>): Promise<Routes[R]> {
  const [method, path] = (route as string).split(" ");
  const url = path.replace(/:(\\w+)/g, (_, k) => (params as Record<string, string>)[k]);
  console.log(method, url);
  const fake: Record<string, unknown> = {
    "/products": [{ id: "p1", price: 40 }], "/products/p1": { id: "p1", price: 40, stock: 3 }, "/orders": { orderId: "ORD-104233", total: 80 },
  };
  return fake[url] as Routes[R];
}

const list = await call("GET /products", {});
const one = await call("GET /products/:id", { id: "p1" });
const order = await call("POST /orders", {});
console.log(list.length, one.stock, order.orderId);

await call("GET /products/:id", {});           // the id parameter is required
console.log(one.stok);                         // typo in a response field
''', 'Typed API routes with inferred parameters', errors=2),
}

PARTS = [
    part('generics', '🧬', 'Generics', '''
<p>A <b>generic</b> is a type parameter, written <code>&lt;T&gt;</code>, that is filled in when the function or type is used. It keeps the connection between inputs and outputs: <code>first</code> of a number list is a number. A <b>constraint</b> with <code>extends</code> says what <code>T</code> must at least have.</p>
[[generics]]
<div class="tip">Generics are why Playwright's <code>test.extend&lt;{ cart: CartPage }&gt;()</code> knows the type of every fixture, and why <code>response.json()</code> in a typed client can return your response type (chapter 25).</div>
''', qa=['Playwright'], qa_why='Typed fixtures, typed API clients and test data builders are all built with generics.',
        kw=['generics', 'type parameter', '<T>', 'generic constraint', 'extends', 'default type parameter', 'generic type', 'inference']),
    part('keyof', '🔑', 'typeof, keyof and indexed access', '''
<p><code>typeof value</code> turns a value into a type, <code>keyof T</code> gives the union of its keys, and <code>T[K]</code> reads the type of one property. Together they let a function accept only real keys and return the right type for each one.</p>
[[keyof]]
''', kw=['typeof type', 'keyof', 'indexed access type', 'T[K]', 'lookup type', 'K extends keyof T', 'Partial']),
    part('utility', '🧰', 'Utility types', '''
<p>TypeScript ships with type helpers that change existing types instead of writing new ones by hand.</p>
<div class="tw"><table class="jt"><tr><th>Helper</th><th>Gives</th></tr>
<tr><td><code>Partial&lt;T&gt;</code> <code>Required&lt;T&gt;</code></td><td>every property optional, or every property required</td></tr>
<tr><td><code>Pick&lt;T, K&gt;</code> <code>Omit&lt;T, K&gt;</code></td><td>only some keys, or all but some keys</td></tr>
<tr><td><code>Record&lt;K, V&gt;</code></td><td>an object with keys K and values V</td></tr>
<tr><td><code>Readonly&lt;T&gt;</code></td><td>every property readonly</td></tr>
<tr><td><code>ReturnType</code> <code>Parameters</code> <code>Awaited</code></td><td>the return, the arguments, the value inside a promise</td></tr>
<tr><td><code>NonNullable</code> <code>Exclude</code> <code>Extract</code></td><td>remove null and undefined, remove or keep union members</td></tr>
</table></div>
[[utility]]
<div class="warn">Look at the <code>leaked</code> line: spreading an object with extra fields into a typed variable is allowed, so a password can slip into a "public" object. Types describe what must be there, not what must be absent. API tests must still check that secret fields are not in the response.</div>
''', qa=True, qa_why='Omit and Pick model create requests and public responses, and the leaked password shows what types alone cannot prove.',
        kw=['utility types', 'Partial', 'Required', 'Pick', 'Omit', 'Record', 'Readonly', 'ReturnType', 'Parameters', 'Awaited', 'NonNullable', 'Exclude', 'Extract', 'excess property check']),
    part('mapped', '🗺️', 'Mapped and conditional types', '''
<p>A <b>mapped type</b> loops over keys: <code>{ [K in keyof T]: … }</code>. It can rename keys with <code>as</code> and add or remove <code>readonly</code> and <code>?</code>. A <b>conditional type</b>, <code>T extends U ? X : Y</code>, chooses a type, and <code>infer</code> captures part of a type, such as the element of an array or the value inside a promise.</p>
[[mapped]]
<div class="note">Conditional types are <b>distributive</b> over unions: <code>NonEmpty&lt;"a" | ""&gt;</code> is checked one member at a time, which is how <code>Exclude</code> and <code>NonNullable</code> are written.</div>
''', kw=['mapped types', 'key remapping', 'as', 'Capitalize', '-readonly', 'conditional types', 'infer', 'distributive conditional types', 'never']),
    part('template', '🧵', 'Template literal types', '''
<p>Template literal types describe patterns of strings, built from other string types. They type routes, CSS values, event names and test ids, and the compiler checks every literal you write.</p>
[[template]]
''', qa=True, qa_why='Typed routes and test id patterns stop typos in endpoints and locators.',
        kw=['template literal types', 'string patterns', 'Capitalize', 'Uppercase', 'route types', 'event names', 'data-testid']),
    part('satisfies', '✔️', 'satisfies', '''
<p>An annotation such as <code>const x: Record&lt;string, Project&gt;</code> replaces the type of the value with the wider annotation, so the exact keys are lost. <code>satisfies</code> checks the value against the type but keeps the precise type that was inferred. It is ideal for configuration objects.</p>
[[satisfies]]
<div class="tip"><code>playwright.config.ts</code> uses <code>defineConfig</code> for the same reason. With your own config objects, <code>satisfies</code> gives typo checking and auto complete at the same time.</div>
''', qa=['Playwright'], qa_why='Test configuration objects get both type checking and precise auto complete.',
        kw=['satisfies', 'type annotation', 'widening', 'config object', 'as const satisfies', 'precise types']),
    part('exhaustive', '🧱', 'Exhaustive checks with never', '''
<p>With a discriminated union, a <code>switch</code> on the shared field narrows each case. Passing the leftover value to a function that takes <code>never</code> makes the check <b>exhaustive</b>: add a new kind to the union and every switch that forgot it becomes a compile error.</p>
[[exhaustive]]
''', qa=True, qa_why='Keyword driven and data driven frameworks model their steps as unions, and exhaustive checks keep every runner up to date.',
        kw=['discriminated union', 'exhaustive check', 'never', 'assertNever', 'switch', 'keyword driven', 'state machine']),
    part('assertions', '🛂', 'Assertion functions and branded types', '''
<p>An <b>assertion function</b> with <code>asserts value is T</code> narrows the type after the call, or throws. Test helpers such as <code>expect(x).toBeDefined()</code> cannot narrow types, but your own assertion functions can. A <b>branded type</b> adds an invisible tag to a primitive so two kinds of string id cannot be mixed up.</p>
[[assertions]]
''', qa=True, qa_why='Required environment variables and typed ids are checked once, and the rest of the test can rely on them.',
        kw=['assertion function', 'asserts', 'asserts value is', 'branded type', 'nominal typing', 'opaque type', 'type safety', 'environment variables']),
    part('scenario', '🎬', 'Real world scenario: typed API routes', '''
<div class="scenario"><b>The situation</b>API tests often read the wrong field or forget a path parameter. The team wants the route string itself to decide the parameters and the response type.</div>
[[scenario]]
<p>A conditional type with <code>infer</code> pulls <code>:id</code> out of the route string, and the <code>Routes</code> map gives the response type. A missing parameter or a typo such as <code>stok</code> is now a compile error. Tools such as openapi-typescript generate a map like <code>Routes</code> from the API's OpenAPI file, so the types follow the real API.</p>
''', qa=True, kw=['typed API client', 'route types', 'path parameters', 'infer', 'OpenAPI', 'openapi-typescript', 'response types']),
]

INFO = {'title': 'Types that think', 'panels': [
    panel([['e', '🧬'], ['t', 'first<T>(xs: T[]): T', {'b': 1, 'size': 11}]], 'Generics', 'Keep input and output linked.', 'Constrain with extends.'),
    panel([['e', '🧰'], ['t', 'Omit<User, "password">', {'b': 1, 'size': 11}]], 'Utility types', 'Reshape what you have.', 'Pick, Omit, Partial, Record.'),
    panel([['e', '🧵'], ['t', '`${Method} /${string}`', {'b': 1, 'size': 11}]], 'Patterns', 'Strings with structure.', 'Typos become errors.'),
    panel([['e', '🧱'], ['t', 'assertNever(step)', {'b': 1}]], 'Exhaustive', 'Every case handled.', 'New cases cannot be forgotten.')],
    'remember': 'Use generics to keep types connected, utility and mapped types to reshape them, satisfies for configs, and never to make switches exhaustive.'}

REAL = [
    ['🧭', 'An API test suite', 'Generates its route types from the OpenAPI file in CI. When the backend renamed a field, 37 tests failed to compile before a single request was sent.'],
    ['🎹', 'A keyword driven framework', 'Models every step as a union member. Adding a "hover" step showed the three runners that still needed to support it.'],
    ['🆔', 'A marketplace', 'Branded its UserId and OrderId types after a bug sent a refund to an order id that happened to look like a user id.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers advanced TypeScript: generics, keyof, utility types, mapped and conditional types, template literal types, satisfies, exhaustive checks and branded types.',
        'यह अध्याय advanced TypeScript सिखाता है: generics, keyof, utility types, mapped और conditional types, template literal types, satisfies और branded types।',
        'ಈ ಅಧ್ಯಾಯ advanced TypeScript: generics, keyof, utility types, mapped, conditional, template literal types ಮತ್ತು satisfies.',
        'ଏହି ଅଧ୍ୟାୟ advanced TypeScript: generics, keyof, utility types, mapped, conditional, template literal types ଓ satisfies।',
        'يتناول هذا الفصل TypeScript المتقدمة: الأنواع العامة وkeyof والأنواع المساعدة والمحولة والشرطية وأنواع القوالب وsatisfies والفحوص الشاملة.',
        'Dieses Kapitel behandelt fortgeschrittenes TypeScript: Generics, keyof, Utility-, Mapped- und Conditional Types, satisfies und Brands.'),
    say('generics', 'Generics', 'A generic is a type parameter filled in at use. It keeps input and output types linked, and extends sets what the type must have.',
        'Generic एक type parameter है जो इस्तेमाल पर भरता है। यह input और output types को जोड़े रखता है।',
        'Generic ಎಂಬುದು ಬಳಕೆಯಲ್ಲಿ ತುಂಬುವ type parameter. Input ಮತ್ತು output ಜೋಡಿಸುತ್ತದೆ.',
        'Generic ବ୍ୟବହାରରେ ଭରାଯାଉଥିବା type parameter। Input ଓ output ଯୋଡ଼େ।',
        'النوع العام معامل نوع يُملأ عند الاستخدام، ويربط نوع المدخل بنوع المخرج، وتحدد extends ما يجب أن يحتويه.',
        'Ein Generic ist ein Typparameter, der beim Aufruf gefüllt wird. Er verbindet Ein- und Ausgabetypen.'),
    say('keyof', 'keyof', 'typeof makes a type from a value, keyof lists its keys, and T of K reads the type of one property.',
        'typeof value से type बनाता है, keyof उसकी keys देता है, और T of K एक property का type पढ़ता है।',
        'typeof value ನಿಂದ type, keyof keys, T of K ಒಂದು property type.',
        'typeof value ରୁ type, keyof keys, T of K ଗୋଟିଏ property type।',
        'يصنع typeof نوعًا من قيمة، ويسرد keyof مفاتيحه، ويقرأ T[K] نوع خاصية واحدة.',
        'typeof macht aus einem Wert einen Typ, keyof liefert die Schlüssel, T[K] den Typ einer Eigenschaft.'),
    say('utility', 'Utility types', 'Partial, Pick, Omit, Record, ReturnType and Awaited reshape existing types. Types say what must be there, not what must be absent.',
        'Partial, Pick, Omit, Record, ReturnType और Awaited मौजूद types को बदलते हैं। Types बताते हैं क्या होना चाहिए, क्या नहीं होना चाहिए यह नहीं।',
        'Partial, Pick, Omit, Record ಮುಂತಾದವು types ಮರುರೂಪಿಸುತ್ತವೆ.',
        'Partial, Pick, Omit, Record ଆଦି types ପୁନଃ ଆକାର ଦିଅନ୍ତି।',
        'تعيد Partial وPick وOmit وRecord وReturnType وAwaited تشكيل الأنواع. الأنواع تقول ما يجب وجوده لا ما يجب غيابه.',
        'Partial, Pick, Omit, Record und Awaited formen Typen um. Typen sagen, was da sein muss, nicht was fehlen muss.'),
    say('mapped', 'Mapped and conditional', 'Mapped types loop over keys. Conditional types choose a type, and infer captures part of another type.',
        'Mapped types keys पर चलते हैं। Conditional types type चुनते हैं, और infer दूसरे type का हिस्सा पकड़ता है।',
        'Mapped types keys ಮೇಲೆ, conditional types ಆಯ್ಕೆ, infer ಭಾಗ ಹಿಡಿಯುತ್ತದೆ.',
        'Mapped types keys ଉପରେ, conditional types ବାଛେ, infer ଅଂଶ ଧରେ।',
        'تمر الأنواع المحولة على المفاتيح، وتختار الأنواع الشرطية نوعًا، ويلتقط infer جزءًا من نوع آخر.',
        'Mapped Types laufen über Schlüssel, Conditional Types wählen einen Typ, infer fängt einen Teil ein.'),
    say('template', 'Template literal types', 'Template literal types describe string patterns, such as routes and test ids, and every literal is checked.',
        'Template literal types string patterns जैसे routes और test ids बताते हैं, और हर literal जांचा जाता है।',
        'Template literal types routes ಮತ್ತು test ids ನಂತಹ patterns ವಿವರಿಸುತ್ತವೆ.',
        'Template literal types routes ଓ test ids ପରି patterns ବର୍ଣ୍ଣନା କରନ୍ତି।',
        'تصف أنواع القوالب أنماط النصوص مثل المسارات ومعرفات الاختبار، ويُفحص كل نص حرفي.',
        'Template-Literal-Typen beschreiben Muster wie Routen und Test-IDs, jedes Literal wird geprüft.'),
    say('satisfies', 'satisfies', 'satisfies checks a value against a type but keeps the precise inferred type, which suits configuration objects.',
        'satisfies value को type से जांचता है पर सटीक inferred type रखता है, config objects के लिए अच्छा।',
        'satisfies type ಪರಿಶೀಲಿಸಿ ನಿಖರ type ಇಡುತ್ತದೆ.',
        'satisfies type ଯାଞ୍ଚ କରି ସଠିକ type ରଖେ।',
        'يتحقق satisfies من القيمة مقابل النوع لكنه يحتفظ بالنوع الدقيق المستنتج، وهذا يناسب كائنات الإعداد.',
        'satisfies prüft gegen einen Typ und behält den genauen Typ, ideal für Konfigurationen.'),
    say('exhaustive', 'Exhaustive checks', 'Pass the leftover case of a switch to a function that takes never. A new union member without a case becomes a compile error.',
        'Switch का बचा case never लेने वाले function को दें। बिना case वाला नया union member compile error बनता है।',
        'Switch ನ ಉಳಿದ case never function ಗೆ ಕೊಡಿ.',
        'Switch ର ବାକି case never function କୁ ଦିଅନ୍ତୁ।',
        'مرر الحالة المتبقية من switch إلى دالة تأخذ never، فيصبح عضو الاتحاد الجديد بلا حالة خطأ ترجمة.',
        'Gib den Restfall eines switch an eine Funktion mit never. Ein neuer Fall ohne case wird zum Fehler.'),
    say('assertions', 'Assertions and brands', 'Assertion functions narrow a type or throw. Branded types stop two kinds of string id from being mixed up.',
        'Assertion functions type को narrow करते हैं या throw करते हैं। Branded types दो तरह के string id मिलने से रोकते हैं।',
        'Assertion functions narrow ಅಥವಾ throw. Branded types ids ಬೆರೆಯದಂತೆ ತಡೆಯುತ್ತವೆ.',
        'Assertion functions narrow କିମ୍ବା throw। Branded types ids ମିଶିବାକୁ ଅଟକାନ୍ତି।',
        'تضيق دوال التأكيد النوع أو ترمي خطأ، وتمنع الأنواع الموسومة خلط نوعين من معرفات النصوص.',
        'Assertion-Funktionen grenzen ein oder werfen. Branded Types verhindern das Vertauschen von IDs.'),
    say('scenario', 'Scenario', 'The route string decides the parameters and the response type, so a missing id or a typo in a field is a compile error.',
        'Route string parameters और response type तय करता है, इसलिए missing id या field typo compile error है।',
        'Route string parameters ಮತ್ತು response type ನಿರ್ಧರಿಸುತ್ತದೆ.',
        'Route string parameters ଓ response type ସ୍ଥିର କରେ।',
        'يحدد نص المسار المعاملات ونوع الاستجابة، فيصبح المعرف المفقود أو الخطأ الإملائي في حقل خطأ ترجمة.',
        'Der Routen-String bestimmt Parameter und Antworttyp, ein fehlender Parameter wird zum Fehler.'),
    say('practice', 'Hands-on', 'Practise a pick helper, grouping with a typed key, an exhaustive step runner and a branded id parser.',
        'Pick helper, typed key से grouping, exhaustive step runner और branded id parser का अभ्यास करें।',
        'Pick helper, grouping, step runner ಮತ್ತು branded id parser ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Pick helper, grouping, step runner ଓ branded id parser ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على دالة pick والتجميع بمفتاح محدد النوع ومشغل خطوات شامل ومحلل معرفات موسومة.',
        'Übe einen pick-Helfer, Gruppieren mit typisiertem Schlüssel, einen Schritt-Runner und einen ID-Parser.'),
]

QUIZ = [
    quiz('e', 'What does <T> in function first<T>(xs: T[]): T mean?', ['A type parameter filled in when the function is called', 'A JSX tag', 'A comparison', 'A tuple'], 0, 'Generic.', 'first([1, 2]) makes T number.'),
    quiz('e', 'Which utility type makes every property optional?', ['Partial', 'Required', 'Readonly', 'Pick'], 0, 'Partly filled.', 'Great for PATCH request bodies and overrides.'),
    quiz('e', 'What is keyof { a: 1, b: 2 }?', ['"a" | "b"', '1 | 2', 'string', 'number'], 0, 'The keys.', 'Indexed access T["a"] gives the value type.'),
    quiz('m', 'Omit<User, "password"> gives?', ['User without the password property', 'Only the password', 'A string', 'User with password optional'], 0, 'Leave out.', 'Pick is the opposite.'),
    quiz('m', 'What does satisfies keep that a type annotation loses?', ['The precise inferred type of the value', 'Run time checks', 'Comments', 'Default values'], 0, 'No widening.', 'Exact keys and literal values stay known.'),
    quiz('m', 'What does T extends Promise<infer V> ? V : T give for Promise<number>?', ['number', 'Promise<number>', 'never', 'unknown'], 0, 'infer captures.', 'This is how Awaited works.'),
    quiz('m', 'How many strings does `${"GET" | "POST"} /${"a" | "b" | "c"}` allow?', ['6', '5', '2', 'Any string'], 0, 'Every combination.', '2 × 3.'),
    quiz('h', 'Why pass the default case of a switch to a function taking never?', ['So forgetting a case becomes a compile error', 'To speed up the switch', 'To silence errors', 'It is required syntax'], 0, 'Exhaustiveness.', 'If a case is missing, the value is not never and tsc complains.'),
    quiz('h', 'What does asserts value is NonNullable<T> do after the call?', ['TypeScript treats value as not null or undefined', 'It converts the value', 'It logs the value', 'It returns a boolean'], 0, 'Narrowing by assertion.', 'If the check fails, the function throws instead.'),
    quiz('h', 'Why can a password still end up in a PublicUser object?', ['Spreading an object with extra fields is allowed, types do not forbid extra properties', 'TypeScript is broken', 'Omit does not work', 'Passwords are strings'], 0, 'Structural typing.', 'Only fresh object literals get the excess property check.'),
    quiz('x', 'What is the point of a branded type such as string & { __brand: "OrderId" }?', ['Two kinds of id stay apart at compile time with no run time cost', 'It encrypts the id', 'It validates the format at run time', 'It makes ids unique'], 0, 'Nominal typing.', 'Combine it with a parse function that checks the format once.'),
    quiz('x', 'Conditional types distribute over unions. What is Exclude<"a" | "b" | "c", "b">?', ['"a" | "c"', '"b"', 'never', '"a" | "b" | "c"'], 0, 'One member at a time.', 'Exclude<T, U> is T extends U ? never : T.'),
]

CALC = [
    calc('e', 'The Endpoint type combines 3 methods, 2 versions and 2 resources. How many strings does it allow?', '12', 'Multiply.', ['<span class="eq">3 × 2 × 2 = 12</span>']),
    calc('e', 'User has 5 properties. How many does Omit<User, "id" | "password"> keep?', '3', 'Remove two.', ['<span class="eq">5 − 2 = 3</span>']),
    calc('m', 'Pick<User, "name" | "email"> then Partial. How many properties are required?', '0', 'Partial makes all optional.', ['Both picked properties become optional.']),
    calc('m', 'The step union has 4 kinds and describeOld handles 2. How many kinds reach assertNever?', '2', 'The rest.', ['fill and expectText are left, which is why tsc reports an error.']),
    calc('m', 'keyof of an object with 3 keys combined with Capitalize in a mapped type gives how many getter names?', '3', 'One per key.', ['getRetries, getBrowser and one more for a third key.']),
    calc('h', 'Exclude<"a" | "b" | "c" | "d", "b" | "d"> has how many members?', '2', 'Remove two.', ['"a" | "c" remain.']),
    calc('h', 'A Record<"admin" | "customer" | "guest", User[]> needs how many keys?', '3', 'One per role.', ['Every key in the union is required.']),
    calc('x', 'A route "GET /users/:userId/orders/:orderId" needs how many parameters?', '2', 'Count the colon parts.', ['userId and orderId.']),
]

EX = [
    ex('pick', 'e', 'A typed pick at run time', '<p>Write <code>pick(obj, keys)</code> that returns a new object with only the listed keys that exist on <code>obj</code>. In TypeScript its type is <code>&lt;T, K extends keyof T&gt;(obj: T, keys: K[]) =&gt; Pick&lt;T, K&gt;</code>.</p>',
       'function pick(obj, keys) {\n  \n}\n',
       [('pick({ id: 1, email: "a@x", password: "s" }, ["id", "email"])', {'id': 1, 'email': 'a@x'}), ('pick({ a: 1 }, [])', {}), ('pick({ a: 0, b: null }, ["a", "b"])', {'a': 0, 'b': None})],
       'function pick(obj, keys) {\n  return Object.fromEntries(keys.filter(k => k in obj).map(k => [k, obj[k]]));\n}', hint='<code>Object.fromEntries</code> over the filtered keys.', why='Real values such as 0 and null must be kept, so check with in, not truthiness.'),
    ex('groupkey', 'm', 'Group by a key name', '<p>Write <code>groupByKey(list, key)</code> that groups objects by the value of the named property. In TypeScript, <code>key</code> would be <code>keyof T</code>, so only real fields are allowed.</p>',
       'function groupByKey(list, key) {\n  \n}\n',
       [('groupByKey([{ s: "pass", n: 1 }, { s: "fail", n: 2 }, { s: "pass", n: 3 }], "s")', {'pass': [{'s': 'pass', 'n': 1}, {'s': 'pass', 'n': 3}], 'fail': [{'s': 'fail', 'n': 2}]}), ('groupByKey([], "s")', {})],
       'function groupByKey(list, key) {\n  const out = {};\n  for (const item of list) (out[item[key]] ??= []).push(item);\n  return out;\n}', hint='Read <code>item[key]</code> and push into an array for that value.', why='With keyof T, a typo such as "staus" is caught by tsc before the test runs.'),
    ex('steps', 'h', 'An exhaustive step runner', '<p>Write <code>runSteps(steps)</code> for steps of kind <code>goto</code> (url), <code>click</code> (selector) and <code>fill</code> (selector, value). Return lines such as <code>"open /login"</code>, <code>"click #go"</code>, <code>"fill #email with asha"</code>. Throw an Error with the message <code>"unknown step: KIND"</code> for any other kind, like assertNever does.</p>',
       'function runSteps(steps) {\n  \n}\n',
       [('runSteps([{ kind: "goto", url: "/login" }, { kind: "fill", selector: "#email", value: "asha" }, { kind: "click", selector: "#go" }])', ['open /login', 'fill #email with asha', 'click #go']),
        ('(() => { try { runSteps([{ kind: "hover", selector: "x" }]); } catch (e) { return e.message; } })()', 'unknown step: hover')],
       'function runSteps(steps) {\n  return steps.map(step => {\n    switch (step.kind) {\n      case "goto": return `open ${step.url}`;\n      case "click": return `click ${step.selector}`;\n      case "fill": return `fill ${step.selector} with ${step.value}`;\n      default: throw new Error(`unknown step: ${step.kind}`);\n    }\n  });\n}',
       hint='A switch on <code>step.kind</code> with a default that throws.', why='At run time the default catches bad data from files. At compile time the never check catches missing cases in code.'),
    ex('orderid', 'x', 'Parse a branded id', '<p>Write <code>parseOrderId(text)</code> that trims the text, upper cases it, and returns it if it looks like <code>ORD-</code> followed by exactly 6 digits. Otherwise throw a <code>RangeError</code> with the message <code>bad order id: TEXT</code> using the original text. In TypeScript the return type would be <code>OrderId</code>.</p>',
       'function parseOrderId(text) {\n  \n}\n',
       [('parseOrderId(" ord-104233 ")', 'ORD-104233'), ('(() => { try { parseOrderId("ORD-12"); } catch (e) { return [e.name, e.message]; } })()', ['RangeError', 'bad order id: ORD-12']), ('parseOrderId("ORD-000001")', 'ORD-000001')],
       'function parseOrderId(text) {\n  const id = text.trim().toUpperCase();\n  if (!/^ORD-\\d{6}$/.test(id)) throw new RangeError(`bad order id: ${text}`);\n  return id;\n}', hint='Normalise first, then test with <code>/^ORD-\\d{6}$/</code>.', why='Parse once at the edge and the brand guarantees every OrderId inside the code is valid.'),
]

T = {
    'slug': 'ts-advanced', 'title': 'Advanced TypeScript types', 'short': 'Advanced types', 'emoji': '🧬', 'module': MODULE, 'minutes': 20,
    'lead': 'The type tools experts use: generics and constraints, typeof, keyof and indexed access, the utility types, mapped and conditional types with infer, template literal types, satisfies, exhaustive checks with never, assertion functions, branded types, and API routes whose types follow the path.',
    'desc': 'Advanced TypeScript: generics, constraints, keyof, typeof, indexed access, Partial, Pick, Omit, Record, ReturnType, Awaited, mapped types, conditional types, infer, template literal types, satisfies, never, assertion functions and branded types.',
    'summary': 'Generic functions and types, typeof, keyof and indexed access, the utility types and what they cannot prove, mapped and conditional types with infer, template literal types for routes and test ids, satisfies for config objects, exhaustive switches with never, assertion functions and branded ids, and typed API routes with inferred path parameters.',
    'keywords': ['generics', 'keyof', 'indexed access', 'utility types', 'Partial', 'Omit', 'Record', 'mapped types', 'conditional types', 'infer', 'template literal types', 'satisfies', 'never', 'exhaustive', 'assertion functions', 'branded types', 'interview'],
    'qa_intro': 'Advanced types turn whole classes of test bugs into compile errors: wrong routes, missing parameters, typos in response fields and forgotten step types.',
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
