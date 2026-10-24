# Chapter 17: objects in depth and metaprogramming: property descriptors, getters and setters, well known symbols, Proxy, Reflect, tagged templates and decorators.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🔬', 'JavaScript in depth', 'js-depth', 'How the engine really works, errors and debugging, regular expressions, functional style, metaprogramming and Node.js in depth.')

CODES = {
    'descriptors': run('''
"use strict";
const user = { name: "Asha" };
Object.defineProperty(user, "id", { value: 7, writable: false, enumerable: false, configurable: false });

console.log(Object.getOwnPropertyDescriptor(user, "name"));
console.log(Object.getOwnPropertyDescriptor(user, "id"));
console.log(Object.keys(user), JSON.stringify(user), user.id);      // not enumerable: hidden from keys and JSON
try { user.id = 8; } catch (e) { console.log(e.constructor.name, "on write") }
try { delete user.id; } catch (e) { console.log(e.constructor.name, "on delete") }

// Getters and setters: computed and validated properties
const cart = {
  items: [{ price: 40, qty: 2 }, { price: 250, qty: 1 }],
  get total() { return this.items.reduce((s, i) => s + i.price * i.qty, 0); },
  set coupon(code) {
    if (!/^[A-Z]+\\d+$/.test(code)) throw new RangeError(`bad coupon ${code}`);
    this._coupon = code;
  },
};
console.log("total", cart.total);
cart.coupon = "SAVE10";
try { cart.coupon = "nope"; } catch (e) { console.log(e.message); }

// The three levels of locking
const levels = { preventExtensions: Object.preventExtensions, seal: Object.seal, freeze: Object.freeze };
for (const [name, lock] of Object.entries(levels)) {
  const o = lock({ a: 1 });
  const can = op => { try { op(o); return "yes"; } catch { return "no"; } };
  console.log(name.padEnd(17), "add:", can(o => (o.b = 2)), " change:", can(o => (o.a = 9)), " delete:", can(o => delete o.a));
}
''', 'Property descriptors, getters, setters and locking'),
    'symbols': run('''
import util from "node:util";

class Money {
  constructor(amount, currency) { this.amount = amount; this.currency = currency; }
  // Decide what the object becomes in maths, in strings and by default
  [Symbol.toPrimitive](hint) { return hint === "number" ? this.amount : `${this.currency} ${this.amount.toFixed(2)}`; }
  get [Symbol.toStringTag]() { return "Money"; }
}
const price = new Money(49.5, "INR");
console.log(+price * 2, `${price}`, Object.prototype.toString.call(price));

// Control instanceof for duck typing
class Thenable { static [Symbol.hasInstance](x) { return typeof x?.then === "function"; } }
console.log(Promise.resolve() instanceof Thenable, {} instanceof Thenable);

// Hide secrets when objects are logged in Node.js
class Credentials {
  constructor(user, password) { this.user = user; this.password = password; }
  [util.inspect.custom]() { return `Credentials { user: '${this.user}', password: '***' }`; }
  toJSON() { return { user: this.user }; }
}
const login = new Credentials("asha", "s3cret");
console.log(login, JSON.stringify(login));
''', 'Well known symbols change built in behaviour'),
    'proxy': run('''
// A Proxy wraps an object and intercepts operations through "traps"
const strictConfig = target => new Proxy(target, {
  get(obj, key, receiver) {
    if (typeof key === "string" && !(key in obj)) throw new ReferenceError(`unknown config key "${key}"`);
    return Reflect.get(obj, key, receiver);
  },
  set(obj, key, value) {
    if (key === "timeout" && !(Number.isInteger(value) && value > 0)) throw new TypeError("timeout must be a positive integer");
    return Reflect.set(obj, key, value);
  },
});

const config = strictConfig({ baseURL: "http://localhost:3000", timeout: 5000 });
console.log(config.timeout);
try { config.timout; } catch (e) { console.log(e.message); }              // typo caught at once
try { config.timeout = "5s"; } catch (e) { console.log(e.message); }

// Negative indexes for arrays
const last = arr => new Proxy(arr, { get: (a, k, r) => Reflect.get(a, typeof k === "string" && /^-\\d+$/.test(k) ? a.length + Number(k) : k, r) });
console.log(last(["login", "search", "checkout"])[-1]);

// Count reads to find which settings are really used
const reads = new Map();
const watched = new Proxy({ a: 1, b: 2 }, { get(o, k) { reads.set(k, (reads.get(k) ?? 0) + 1); return o[k]; } });
watched.a; watched.a; watched.b;
console.log(Object.fromEntries(reads));
''', 'Proxy and Reflect: intercept property access'),
    'pom-proxy': run('''
// Wrap every page object method: log the step and its time, and retry once on a known flaky error
function instrument(page, { log = console.log } = {}) {
  return new Proxy(page, {
    get(target, key, receiver) {
      const value = Reflect.get(target, key, receiver);
      if (typeof value !== "function") return value;
      return async (...args) => {
        const label = `${target.constructor.name}.${String(key)}(${args.map(a => JSON.stringify(a)).join(", ")})`;
        for (let attempt = 1; ; attempt++) {
          try {
            const result = await value.apply(receiver, args);
            log(`✔ ${label}${attempt > 1 ? ` after ${attempt} tries` : ""}`);
            return result;
          } catch (e) {
            if (attempt === 2 || !/detached|stale/i.test(e.message)) { log(`✖ ${label}: ${e.message}`); throw e; }
          }
        }
      };
    },
  });
}

class SearchPage {
  clicks = 0;
  async search(term) { if (++this.clicks === 1) throw new Error("element is detached from the DOM"); return `${term}: 3 results`; }
  async openResult(n) { if (n > 3) throw new Error(`result ${n} not found`); return `opened ${n}`; }
}
const page = instrument(new SearchPage());
console.log(await page.search("pen"));
await page.openResult(9).catch(() => {});
''', 'A Proxy that logs and retries page object steps'),
    'tagged': run('''
// A tag function receives the fixed strings and the values separately
function html(strings, ...values) {
  const escape = v => String(v).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  return strings.reduce((out, s, i) => out + s + (i < values.length ? escape(values[i]) : ""), "");
}
const review = '<img src=x onerror="alert(1)">';
console.log(html`<p class="review">${review}</p>`);

// A SQL tag that never builds text from values, which prevents SQL injection
function sql(strings, ...values) {
  return { text: strings.reduce((q, s, i) => q + `$${i}` + s), values };
}
const email = "x' OR '1'='1";
console.log(sql`SELECT * FROM users WHERE email = ${email} AND active = ${true}`);

// String.raw keeps backslashes, handy for regexes and Windows paths
console.log(String.raw`C:\\tests\\new`, "|", `C:\\tests\\new`.length, String.raw`C:\\tests\\new`.length);

// A dedent tag for readable multi line test data
const dedent = (s, ...v) => String.raw(s, ...v).replace(/^\\n/, "").replace(new RegExp(`^${String.raw(s, ...v).match(/^\\n?( *)/)[1]}`, "gm"), "");
console.log(dedent`
    Feature: Login
      Scenario: wrong password
        Then I see "Try again"`);
''', 'Tagged templates: safe HTML and SQL'),
    'decorators': show('''
// Decorators are a stage 3 proposal. TypeScript 5 and later supports them today ({{ch:ts-projects}}),
// and Babel can compile them for JavaScript.
class CheckoutPage {
  @step("Pay with card")          // log the step in the report
  @retry(2)                       // retry the method on a flaky error
  async pay(card) { /* ... */ }
}

function step(title) {
  return function (method, context) {
    return async function (...args) {
      console.log(`step: ${title}`);
      return method.apply(this, args);
    };
  };
}
''', 'Decorators wrap methods and classes', note='Runs in {{ch:ts-projects}} with TypeScript'),
    'scenario': run('''
// A fluent API client built from a Proxy: api.users[7].orders.get() calls GET /users/7/orders
function client(baseURL, fetchFn) {
  const make = path => new Proxy(() => {}, {
    get(_, key) {
      if (["get", "post", "put", "delete"].includes(key))
        return (body) => fetchFn(key.toUpperCase(), `${baseURL}${path}`, body);
      return make(`${path}/${String(key)}`);
    },
  });
  return make("");
}

// A fake fetch so the example runs anywhere
const calls = [];
const fakeFetch = async (method, url, body) => { calls.push(`${method} ${url}${body ? " " + JSON.stringify(body) : ""}`); return { status: method === "POST" ? 201 : 200 }; };

const api = client("https://api.shop.test/v1", fakeFetch);
await api.users[7].orders.get();
await api.products.post({ name: "Pen", price: 40 });
await api.carts["c-19"].items.PEN.delete();
console.log(calls);
''', 'A dynamic API client with a Proxy'),
}

PARTS = [
    part('descriptors', '🧾', 'Property descriptors, getters and setters', '''
<p>Every property has a <b>descriptor</b> with flags. <code>writable</code> allows changes, <code>enumerable</code> shows it in <code>Object.keys</code>, loops and JSON, and <code>configurable</code> allows deleting it or changing its flags. Accessor properties use <code>get</code> and <code>set</code> functions instead of a value.</p>
[[descriptors]]
<div class="tip">This is why a hidden property can be on an object you are testing but missing from <code>JSON.stringify</code> and <code>toEqual</code> comparisons. Use <code>Object.getOwnPropertyDescriptors</code> when an object behaves strangely.</div>
''', kw=['property descriptor', 'defineProperty', 'writable', 'enumerable', 'configurable', 'getter', 'setter', 'accessor', 'Object.freeze', 'Object.seal', 'preventExtensions']),
    part('symbols', '🔣', 'Well known symbols', '''
<p>Built in operations look for special symbol keys on your objects. <code>Symbol.toPrimitive</code> controls conversion to numbers and strings, <code>Symbol.hasInstance</code> controls <code>instanceof</code>, <code>Symbol.toStringTag</code> the type label, and <code>Symbol.iterator</code> ({{ch:js-collections-iterators}}) makes an object loopable. Node.js adds <code>util.inspect.custom</code> for how an object is logged.</p>
[[symbols]]
<div class="qa-box">Give credential and token objects a custom inspect and a <code>toJSON</code> that leave the secret out. Test reports, CI logs and screenshots of the console then never leak a password.</div>
''', qa=True, qa_why='Hiding secrets from logs and reports is a must for test frameworks that log every object.',
        kw=['Symbol.toPrimitive', 'Symbol.hasInstance', 'Symbol.toStringTag', 'Symbol.iterator', 'util.inspect.custom', 'toJSON', 'well known symbols', 'secrets in logs']),
    part('proxy', '🪞', 'Proxy and Reflect', '''
<p>A <b>Proxy</b> sits in front of an object and can intercept almost anything done to it: reading, writing, deleting, <code>in</code>, listing keys, calling and <code>new</code>. Each handler function is a <b>trap</b>. <b>Reflect</b> has a method for every trap that does the normal behaviour, so a trap can add checks and then hand over.</p>
[[proxy]]
<p>Test frameworks use proxies for auto mocking, for fluent APIs and for wrapping page objects. Here a Proxy adds step logging and one retry on a known flaky error to every method, without touching the page class.</p>
[[pom-proxy]]
<div class="warn">Proxies add a cost to every operation and can surprise people reading the code. Use them in tools and test frameworks, not in hot paths of application code.</div>
''', qa=['Playwright', 'Selenium'], qa_why='Proxies power auto mocks and step logging, and let you add retries or reporting to every page object at once.',
        kw=['Proxy', 'Reflect', 'trap', 'get trap', 'set trap', 'has', 'deleteProperty', 'apply', 'construct', 'validation proxy', 'negative index', 'auto mock', 'step logging']),
    part('tagged', '🏷️', 'Tagged template literals', '''
<p>A <b>tag</b> is a function placed before a template literal. It receives the fixed text pieces and the values separately, so it can escape values, build safe queries or change the text. Libraries such as lit-html, styled-components and the <code>gql</code> tag for GraphQL are built on this.</p>
[[tagged]]
''', qa=True, qa_why='Knowing how query tags keep values apart from SQL text explains why injection tests pass or fail.',
        kw=['tagged template', 'template literal', 'String.raw', 'escape HTML', 'SQL injection', 'parameterised query', 'dedent', 'gql']),
    part('decorators', '🎀', 'Decorators', '''
<p>A <b>decorator</b> is a function written as <code>@name</code> before a class, method, field or accessor. It receives the original and can replace or wrap it. Test frameworks use decorators for steps, retries, timeouts and dependency injection.</p>
[[decorators]]
''', kw=['decorators', 'stage 3', '@decorator', 'method decorator', 'TypeScript decorators', 'Babel']),
    part('scenario', '🎬', 'Real world scenario: a fluent API client', '''
<div class="scenario"><b>The situation</b>The API test suite calls dozens of endpoints. Writing a function for each one is slow, and URL strings built by hand are full of typos.</div>
[[scenario]]
<p>Each property read adds a part to the path, and the verb at the end sends the request. The same trick is used by real clients for large APIs. Pair it with TypeScript types ({{ch:ts-advanced}}) so the editor suggests only valid paths.</p>
''', qa=True, kw=['API client', 'fluent API', 'Proxy', 'REST', 'URL builder', 'fake fetch']),
]

INFO = {'title': 'Code that shapes code', 'panels': [
    panel([['e', '🧾'], ['t', '{ writable, enumerable }', {'b': 1, 'size': 11}]], 'Descriptors', 'Flags on every property.', 'Hidden keys skip JSON.'),
    panel([['e', '🔣'], ['t', '[Symbol.toPrimitive]', {'b': 1, 'size': 11}]], 'Symbols', 'Hooks into built in behaviour.', 'Hide secrets from logs.'),
    panel([['e', '🪞'], ['t', 'new Proxy(obj, traps)', {'b': 1, 'size': 11}]], 'Proxy', 'Intercept any operation.', 'Reflect does the default.'),
    panel([['e', '🏷️'], ['t', 'sql`… ${email}`', {'b': 1}]], 'Tags', 'Values arrive separately.', 'Safe HTML and SQL.')],
    'remember': 'Descriptors and symbols change how objects behave, Proxy intercepts operations, and tags keep values apart from text.'}

REAL = [
    ['🧪', 'Vitest and Jest', 'Build automatic mocks of whole modules with proxies, so every function exists and records its calls.'],
    ['🔐', 'A banking test suite', 'Logged request objects in every failure until a password appeared in a CI log. A custom inspect on the credentials class fixed it for good.'],
    ['🐙', 'A popular GitHub client', 'Builds its methods for hundreds of endpoints from a description file, the same idea as the proxy client on this page.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers objects in depth and metaprogramming: descriptors, getters and setters, well known symbols, Proxy and Reflect, tagged templates and decorators.',
        'यह अध्याय objects और metaprogramming सिखाता है: descriptors, getters और setters, symbols, Proxy और Reflect, tagged templates और decorators।',
        'ಈ ಅಧ್ಯಾಯ objects ಮತ್ತು metaprogramming: descriptors, getters, symbols, Proxy, Reflect, tagged templates ಮತ್ತು decorators.',
        'ଏହି ଅଧ୍ୟାୟ objects ଓ metaprogramming: descriptors, getters, symbols, Proxy, Reflect, tagged templates ଓ decorators।',
        'يتناول هذا الفصل الكائنات بعمق والبرمجة الوصفية: الواصفات والمحصلات والرموز المعروفة وProxy وReflect والقوالب الموسومة والمزخرفات.',
        'Dieses Kapitel behandelt Objekte im Detail und Metaprogrammierung: Deskriptoren, Getter, Symbole, Proxy, Reflect, Tags und Dekoratoren.'),
    say('descriptors', 'Descriptors', 'Each property has flags: writable, enumerable and configurable. Getters and setters compute or check values. freeze, seal and preventExtensions lock objects.',
        'हर property के flags होते हैं: writable, enumerable और configurable। Getters और setters values गिनते या जांचते हैं।',
        'ಪ್ರತಿ property ಗೆ flags: writable, enumerable, configurable. Getters setters values ಲೆಕ್ಕಿಸುತ್ತವೆ.',
        'ପ୍ରତି property ର flags: writable, enumerable, configurable। Getters setters values ହିସାବ କରନ୍ତି।',
        'لكل خاصية أعلام: قابلة للكتابة وقابلة للعد وقابلة للتهيئة. تحسب المحصلات والمعينات القيم أو تتحقق منها.',
        'Jede Eigenschaft hat Flags: writable, enumerable, configurable. Getter und Setter berechnen oder prüfen Werte.'),
    say('symbols', 'Symbols', 'Well known symbols let your objects control conversion, instanceof and logging. Use a custom inspect to hide passwords.',
        'Well known symbols से objects conversion, instanceof और logging नियंत्रित करते हैं। Passwords छिपाने के लिए custom inspect लगाएं।',
        'Well known symbols conversion, instanceof ಮತ್ತು logging ನಿಯಂತ್ರಿಸುತ್ತವೆ. Passwords ಮರೆಮಾಡಿ.',
        'Well known symbols conversion, instanceof ଓ logging ନିୟନ୍ତ୍ରଣ କରନ୍ତି। Passwords ଲୁଚାନ୍ତୁ।',
        'تتيح الرموز المعروفة لكائناتك التحكم في التحويل وinstanceof والطباعة. استخدم inspect مخصصًا لإخفاء كلمات المرور.',
        'Bekannte Symbole steuern Umwandlung, instanceof und Logging. Ein eigenes inspect versteckt Passwörter.'),
    say('proxy', 'Proxy', 'A Proxy intercepts operations on an object with traps, and Reflect performs the normal behaviour. Test tools use it for mocks and step logging.',
        'Proxy traps से object के operations पकड़ता है, और Reflect सामान्य व्यवहार करता है। Test tools इसे mocks के लिए इस्तेमाल करते हैं।',
        'Proxy traps ಮೂಲಕ operations ತಡೆಯುತ್ತದೆ, Reflect ಸಾಮಾನ್ಯ ವರ್ತನೆ ಮಾಡುತ್ತದೆ.',
        'Proxy traps ରେ operations ଧରେ, Reflect ସାଧାରଣ ବ୍ୟବହାର କରେ।',
        'يعترض Proxy العمليات على الكائن بالمصائد، وينفذ Reflect السلوك العادي. تستخدمه أدوات الاختبار للمحاكاة وتسجيل الخطوات.',
        'Ein Proxy fängt Operationen mit Traps ab, Reflect führt das normale Verhalten aus. Testwerkzeuge nutzen das für Mocks.'),
    say('tagged', 'Tagged templates', 'A tag function gets the text pieces and the values apart, so it can escape HTML or build a safe SQL query.',
        'Tag function को text pieces और values अलग मिलते हैं, इसलिए वह HTML escape या सुरक्षित SQL बना सकता है।',
        'Tag function text ಮತ್ತು values ಬೇರೆಯಾಗಿ ಪಡೆಯುತ್ತದೆ, HTML escape ಅಥವಾ safe SQL ಮಾಡುತ್ತದೆ.',
        'Tag function text ଓ values ଅଲଗା ପାଏ, HTML escape କିମ୍ବା safe SQL କରେ।',
        'تستقبل دالة الوسم أجزاء النص والقيم منفصلة، فتستطيع تهريب HTML أو بناء استعلام SQL آمن.',
        'Eine Tag-Funktion erhält Text und Werte getrennt und kann HTML escapen oder sicheres SQL bauen.'),
    say('decorators', 'Decorators', 'A decorator is a function written with an at sign before a class or method. It can wrap the method with logging or retries.',
        'Decorator class या method से पहले at चिह्न के साथ लिखा function है। यह method को logging या retries से लपेट सकता है।',
        'Decorator ಎಂಬುದು class ಅಥವಾ method ಮುಂದೆ at ಚಿಹ್ನೆಯಿಂದ ಬರೆದ function.',
        'Decorator ହେଉଛି class କିମ୍ବା method ପୂର୍ବରୁ at ଚିହ୍ନ ସହ ଲେଖା function।',
        'المزخرف دالة تكتب بعلامة at قبل صنف أو دالة، ويمكنها تغليف الدالة بالتسجيل أو إعادة المحاولة.',
        'Ein Dekorator ist eine Funktion mit at-Zeichen vor Klasse oder Methode und kann sie mit Logging oder Retries umhüllen.'),
    say('scenario', 'Scenario', 'Every property read adds a path segment and the verb sends the request, so one Proxy gives a client for every endpoint.',
        'हर property read path में एक हिस्सा जोड़ता है और verb request भेजता है, इसलिए एक Proxy हर endpoint का client बनता है।',
        'ಪ್ರತಿ property read path ಸೇರಿಸುತ್ತದೆ, verb request ಕಳುಹಿಸುತ್ತದೆ.',
        'ପ୍ରତି property read path ଯୋଡ଼େ, verb request ପଠାଏ।',
        'كل قراءة خاصية تضيف جزءًا إلى المسار والفعل يرسل الطلب، فيعطي Proxy واحد عميلًا لكل نقطة نهاية.',
        'Jedes Lesen fügt ein Pfadstück hinzu, das Verb sendet die Anfrage, so entsteht ein Client für jeden Endpunkt.'),
    say('practice', 'Hands-on', 'Practise a read only view, a default value proxy, an HTML tag that escapes values, and a proxy that records method calls.',
        'Read only view, default value proxy, values escape करने वाला HTML tag और method calls record करने वाले proxy का अभ्यास करें।',
        'Read only view, default proxy, HTML tag ಮತ್ತು method calls record ಮಾಡುವ proxy ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Read only view, default proxy, HTML tag ଓ method calls record କରୁଥିବା proxy ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على عرض للقراءة فقط وProxy بقيم افتراضية ووسم HTML يهرب القيم وProxy يسجل استدعاءات الدوال.',
        'Übe eine Nur-Lese-Ansicht, einen Proxy mit Standardwerten, einen HTML-Tag und einen Proxy, der Aufrufe aufzeichnet.'),
]

QUIZ = [
    quiz('e', 'A property with enumerable: false is hidden from which of these?', ['Object.keys and JSON.stringify', 'Direct reads like obj.x', 'The in operator', 'Object.getOwnPropertyDescriptor'], 0, 'Enumeration.', 'You can still read it directly.'),
    quiz('e', 'What does a getter do?', ['Runs a function when the property is read', 'Runs when the object is created', 'Deletes the property', 'Copies the object'], 0, 'Computed property.', 'cart.total is computed from the items every time.'),
    quiz('e', 'What does a tag function receive first?', ['An array of the fixed text pieces', 'The whole string', 'Only the values', 'A regex'], 0, 'strings, then ...values.', 'There is always one more string than values.'),
    quiz('m', 'Which lock still allows changing existing values?', ['Object.seal', 'Object.freeze', 'Both', 'Neither'], 0, 'Seal stops adding and deleting.', 'Freeze also stops changes.'),
    quiz('m', 'Which symbol decides what +obj gives?', ['Symbol.toPrimitive', 'Symbol.iterator', 'Symbol.hasInstance', 'Symbol.toStringTag'], 0, 'Conversion.', 'It receives a hint of "number", "string" or "default".'),
    quiz('m', 'Why call Reflect.get inside a get trap?', ['To do the normal read after your own checks', 'It is faster than nothing', 'Traps must return undefined', 'To create a new proxy'], 0, 'Default behaviour.', 'Passing the receiver keeps getters working correctly.'),
    quiz('m', 'How does util.inspect.custom help in test frameworks?', ['It controls how an object is logged, so secrets can be hidden', 'It speeds up tests', 'It mocks modules', 'It prints stack traces'], 0, 'Logging.', 'Add toJSON as well for reports that serialise objects.'),
    quiz('h', 'Why does the sql tag on this page prevent SQL injection?', ['Values are sent separately as parameters, never pasted into the text', 'It deletes quotes', 'It uses a regex', 'It encrypts the query'], 0, 'Parameterised query.', 'The database never treats a value as SQL.'),
    quiz('h', 'Which trap runs for "key" in proxy?', ['has', 'get', 'ownKeys', 'apply'], 0, 'The in operator.', 'ownKeys runs for Object.keys and for loops over keys.'),
    quiz('h', 'A Proxy wraps every page object method with a retry. What does the page class need to change?', ['Nothing, the Proxy adds it from outside', 'Every method', 'Its constructor', 'Its tests'], 0, 'Wrapping.', 'That is the main benefit: one place adds behaviour to all methods.'),
    quiz('x', 'Why does the fluent client proxy wrap a function () => {} instead of {}?', ['So the proxy can also be called, which needs an apply trap on a function target', 'Functions are faster', 'Objects cannot be proxied', 'To hide it from JSON'], 0, 'Callable proxies.', 'A Proxy is only callable if its target is a function.'),
    quiz('x', 'String.raw`a\\nb`.length is?', ['4', '3', '2', '1'], 0, 'Backslash and n stay as two characters.', 'Without raw, \\n is one new line character, giving 3.'),
]

CALC = [
    calc('e', 'cart has items of 40 × 2 and 250 × 1. What does the total getter return?', '330', 'Price times quantity.', ['<span class="eq">40 × 2 + 250 × 1 = 330</span>']),
    calc('e', 'A template literal has 2 values. How many text pieces does the tag function receive?', '3', 'One more than values.', ['Text, value, text, value, text.']),
    calc('m', 'How many of add, change and delete does Object.seal allow on a sealed object?', '1', 'Only change.', ['Adding and deleting fail, changing works.']),
    calc('m', 'last(["a", "b", "c", "d"])[-2] reads which index of the array?', '2', 'length + (−2).', ['<span class="eq">4 + (−2) = 2</span>', 'Index 2 is "c".']),
    calc('m', 'A watched proxy sees a read twice and b once. What is the total count of reads?', '3', 'Add them.', ['2 + 1 = 3.']),
    calc('h', 'The instrumented search fails once with a detached error and then works. How many times did the real method run?', '2', 'One retry.', ['First call threw, the retry returned results.']),
    calc('h', 'sql`… ${a} … ${b} … ${c}` produces placeholders $1 to $n. What is n?', '3', 'One per value.', ['Three values give $1, $2 and $3.']),
    calc('x', 'api.carts["c-19"].items.PEN.delete(). How many path segments are in the URL after the base?', '4', 'carts, c-19, items, PEN.', ['/carts/c-19/items/PEN has 4 segments.']),
]

EX = [
    ex('readonly', 'e', 'A read only view', '<p>Write <code>readOnly(obj)</code> that returns a Proxy where reading works normally but any attempt to set or delete a property throws a <code>TypeError</code>. The original object stays writable.</p>',
       'function readOnly(obj) {\n  \n}\n',
       [('(() => { const o = { a: 1 }; const r = readOnly(o); let threw = 0; try { r.a = 2; } catch (e) { threw += e instanceof TypeError; } try { delete r.a; } catch (e) { threw += e instanceof TypeError; } o.b = 3; return [r.a, r.b, threw]; })()', [1, 3, 2])],
       'function readOnly(obj) {\n  const deny = () => { throw new TypeError("read only"); };\n  return new Proxy(obj, { set: deny, deleteProperty: deny });\n}', hint='Traps for <code>set</code> and <code>deleteProperty</code> that throw.', why='Unlike freeze, the owner can still change the data while callers only get a view.'),
    ex('defaults', 'm', 'Defaults for missing keys', '<p>Write <code>withDefaults(obj, fallback)</code> that returns a Proxy. Reading a key that is not in the object returns <code>fallback</code>, and reading an existing key returns its value, even when that value is 0 or an empty string.</p>',
       'function withDefaults(obj, fallback) {\n  \n}\n',
       [('(() => { const p = withDefaults({ retries: 0, name: "" }, "n/a"); return [p.retries, p.name, p.missing]; })()', [0, '', 'n/a'])],
       'function withDefaults(obj, fallback) {\n  return new Proxy(obj, {\n    get: (target, key, receiver) => (key in target ? Reflect.get(target, key, receiver) : fallback),\n  });\n}', hint='Use <code>key in target</code>, not a truthy check.', why='A truthy check would replace real values of 0 and "" with the fallback.'),
    ex('htmltag', 'h', 'An escaping HTML tag', '<p>Write a tag function <code>html</code> so that <code>html`&lt;b&gt;${x}&lt;/b&gt;`</code> escapes <code>&amp; &lt; &gt; " \'</code> in every value but leaves the fixed text alone.</p>',
       'function html(strings, ...values) {\n  \n}\n',
       [('html`<b>${"<i>"}</b>`', '<b>&lt;i&gt;</b>'), ('html`${"Tom & \\"J\\""} and ${5}`', 'Tom &amp; &quot;J&quot; and 5'), ('html`plain`', 'plain')],
       'function html(strings, ...values) {\n  const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", \'"\': "&quot;", "\'": "&#39;" };\n  const esc = v => String(v).replace(/[&<>"\']/g, c => map[c]);\n  return strings.reduce((out, s, i) => out + s + (i < values.length ? esc(values[i]) : ""), "");\n}',
       hint='Join the strings with the escaped values between them. There is one more string than values.', why='Template engines in every framework do exactly this, which is why they are safe from XSS by default.'),
    ex('recorder', 'x', 'Record every method call', '<p>Write <code>recorder(obj)</code> that returns <code>{ proxy, calls }</code>. Calling any method through <code>proxy</code> runs the real method with the right <code>this</code> and pushes <code>[name, args]</code> to <code>calls</code>. Reading non function properties works normally.</p>',
       'function recorder(obj) {\n  \n}\n',
       [('(() => { const o = { n: 1, add(x) { this.n += x; return this.n; } }; const { proxy, calls } = recorder(o); return [proxy.add(2), proxy.add(3), proxy.n, calls]; })()', [3, 6, 6, [['add', [2]], ['add', [3]]]])],
       'function recorder(obj) {\n  const calls = [];\n  const proxy = new Proxy(obj, {\n    get(target, key, receiver) {\n      const value = Reflect.get(target, key, receiver);\n      if (typeof value !== "function") return value;\n      return (...args) => {\n        calls.push([key, args]);\n        return value.apply(target, args);\n      };\n    },\n  });\n  return { proxy, calls };\n}',
       hint='In the get trap, wrap functions in an arrow that records and then calls <code>value.apply(target, args)</code>.', why='This is a spy. jest.spyOn and sinon.spy record calls the same way.'),
]

T = {
    'slug': 'js-metaprogramming', 'title': 'Objects in depth and metaprogramming', 'short': 'Metaprogramming', 'emoji': '🪞', 'module': MODULE, 'minutes': 17,
    'lead': 'Change how objects behave: property descriptors, getters and setters, freeze, seal and preventExtensions, well known symbols such as toPrimitive and util.inspect.custom, Proxy and Reflect for validation, logging and retries, tagged templates for safe HTML and SQL, and decorators.',
    'desc': 'JavaScript metaprogramming: property descriptors, defineProperty, getters, setters, freeze, seal, Symbol.toPrimitive, Symbol.hasInstance, util.inspect.custom, Proxy, Reflect, traps, tagged template literals, String.raw and decorators.',
    'summary': 'Descriptor flags, getters, setters and the three levels of locking, well known symbols and hiding secrets from logs, Proxy and Reflect for strict config, negative indexes and usage tracking, a proxy that logs and retries page object steps, tagged templates for HTML and SQL, decorators, and a fluent API client.',
    'keywords': ['property descriptor', 'defineProperty', 'getter', 'setter', 'Object.seal', 'Symbol.toPrimitive', 'util.inspect.custom', 'Proxy', 'Reflect', 'trap', 'tagged template', 'String.raw', 'decorators', 'spy', 'interview'],
    'qa_intro': 'Mocks, spies, fluent clients and step reporters are all metaprogramming. This chapter shows how they work so you can build and debug them.',
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
