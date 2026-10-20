# Chapter 2: variables, the seven primitive types, numbers, coercion, equality and every operator.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🌱', 'Foundations', 'js-foundations', 'From your first program to functions and closures. Developers and testers both start here.')

CODES = {
    'let-const': run('''
const baseUrl = "https://shop.example";   // never reassigned, so const
let attempts = 0;                          // changes, so let
attempts = attempts + 1;
attempts++;
console.log(baseUrl, attempts);

const user = { name: "Asha" };
user.name = "Ravi";        // allowed: the object changes, the binding does not
console.log(user);
user = {};                 // not allowed: const means this name always points at the same thing
''', 'let, const and what const really protects', expect='throw'),
    'var-scope': run('''
for (var i = 0; i < 3; i++) {}
console.log("var i after the loop:", i);    // var leaks out of the block

for (let j = 0; j < 3; j++) {}
console.log(typeof j);                        // let stays inside the block
''', 'var leaks out of blocks, let does not', file='var.cjs'),
    'typeof': run('''
const values = ["hello", 42, 3.14, 10n, true, undefined, null, Symbol("id"), { a: 1 }, [1, 2], function f() {}];
for (const v of values) {
  console.log(String(typeof v).padEnd(10), Array.isArray(v) ? "(an array)" : "");
}
''', 'typeof for every kind of value', replace=[(r' +\n', '\n')]),
    'copy': run('''
let a = 5;
let b = a;       // the number is copied
b = 10;
console.log(a, b);

const cart1 = { items: 1 };
const cart2 = cart1;   // both names point at ONE object
cart2.items = 99;
console.log(cart1.items, cart2.items);

const cart3 = { ...cart1 };  // a shallow copy is a second object
cart3.items = 0;
console.log(cart1.items, cart3.items);
''', 'Primitives are copied, objects are shared'),
    'numbers': run('''
console.log(0.1 + 0.2);
console.log(0.1 + 0.2 === 0.3);
console.log(Math.abs(0.1 + 0.2 - 0.3) < Number.EPSILON);
console.log((0.1 + 0.2).toFixed(2));

console.log(7 / 2, Math.floor(7 / 2), 7 % 2, 2 ** 10);
console.log(1 / 0, -1 / 0, 0 / 0);
console.log(Number.isNaN(NaN), NaN === NaN);
console.log(Number.MAX_SAFE_INTEGER);
console.log(9007199254740993);             // too big, silently rounded
console.log(9007199254740993n + 1n);       // BigInt keeps every digit
''', 'Numbers, NaN, Infinity and BigInt'),
    'money': run('''
// Work with money in the smallest unit (paise or cents) to avoid floating point errors
const pricePaise = 129950;      // ₹1299.50
const qty = 3;
const totalPaise = pricePaise * qty;
console.log(totalPaise / 100);

const fmt = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" });
console.log(fmt.format(totalPaise / 100));
''', 'Money without rounding errors'),
    'parse': run('''
console.log(Number("42"), Number(""), Number("42px"), Number(" 7 "));
console.log(parseInt("42px"), parseFloat("3.5kg"), parseInt("0x1F"), parseInt("101", 2));
console.log(String(42), (42).toString(2), `${42}`);
console.log(Boolean(""), Boolean("0"), Boolean(0), Boolean([]));
''', 'Converting on purpose'),
    'coercion': run('''
console.log("5" + 3);        // + with a string joins text
console.log("5" - 3);        // - only works on numbers, so "5" becomes 5
console.log("5" * "2");
console.log(true + 1);
console.log([] + []);
console.log([] + {});
console.log(null + 1, undefined + 1);
console.log("10" > "9", 10 > "9");
''', 'Conversions JavaScript does by itself'),
    'falsy': run('''
const values = [false, 0, -0, 0n, "", null, undefined, NaN, "0", "false", [], {}];
const labels = ["false", "0", "-0", "0n", '""', "null", "undefined", "NaN", '"0"', '"false"', "[]", "{}"];
values.forEach((v, i) => {
  console.log(labels[i].padEnd(10), v ? "truthy" : "falsy");
});
''', 'The eight falsy values', replace=[(r' +\n', '\n')]),
    'equality': run('''
console.log(5 == "5", 5 === "5");
console.log(0 == false, 0 === false);
console.log(null == undefined, null === undefined);
console.log(NaN === NaN, Object.is(NaN, NaN));
console.log(0 === -0, Object.is(0, -0));

const a = { id: 1 }, b = { id: 1 }, c = a;
console.log(a === b, a === c);
console.log(JSON.stringify(a) === JSON.stringify(b));
''', '==, === and Object.is'),
    'jest-eq': test({
        'package.json': pkg('eq', None, {'test': 'jest'}),
        'cart.test.js': '''
test("toBe compares with Object.is, so two equal looking objects fail", () => {
  expect({ id: 1 }).toBe({ id: 1 });
});

test("toEqual compares the contents", () => {
  expect({ id: 1, tags: ["new"] }).toEqual({ id: 1, tags: ["new"] });
});

test("toBeCloseTo is the right check for decimals", () => {
  expect(0.1 + 0.2).toBeCloseTo(0.3);
});
''',
    }, 'npx jest --verbose', 'The same idea inside a test runner', expect='fail',
        replace=[(r'Time:\s+[\d.]+ s.*', 'Time:        0.4 s'), (r'\(\d+ ms\)', '')]),
    'operators': run('''
let score = 10;
score += 5;      // 15
score *= 2;      // 30
score -= 4;      // 26
score %= 7;      // 5
console.log(score);

const age = 20;
console.log(age >= 18 ? "adult" : "minor");
console.log(age > 18 && age < 60, age < 18 || age > 60, !true);

console.log("" || "default", 0 || 10, "set" && "both true");
console.log(JSON.stringify("" ?? "default"), 0 ?? 10, null ?? "fallback");
''', 'Arithmetic, comparison, logic and ??'),
    'optional': run('''
const response = {
  user: { name: "Asha", address: null, orders: [{ id: 7, total: 1299 }] },
};

console.log(response.user?.address?.city);           // undefined, no crash
console.log(response.user?.address?.city ?? "Unknown");
console.log(response.user.orders?.[0]?.total);
console.log(response.user.orders?.[5]?.total ?? 0);
console.log(response.user.greet?.());                // call it only if it exists

const settings = { retries: 0, timeout: null };
settings.retries ||= 3;     // 0 is falsy, so it becomes 3
settings.timeout ??= 5000;  // only null or undefined is replaced
console.log(settings);
''', 'Optional chaining and logical assignment'),
    'scenario': run('''
// An API returned product data in an awkward shape. Normalise it before checking it.
const apiProducts = [
  { sku: "A1", price: "₹1,299.50", stock: "12", discount: null },
  { sku: "B2", price: "₹499", stock: "0", discount: { percent: 10 } },
  { sku: "C3", price: "", stock: undefined },
];

function toNumber(text) {
  const clean = String(text ?? "").replace(/[^0-9.]/g, "");
  return clean === "" ? null : Number(clean);
}

const products = apiProducts.map(p => ({
  sku: p.sku,
  price: toNumber(p.price),
  inStock: Number(p.stock ?? 0) > 0,
  discount: p.discount?.percent ?? 0,
}));
console.table(products);

const problems = products.filter(p => p.price === null || Number.isNaN(p.price));
console.log("Products with a missing price:", problems.map(p => p.sku));
''', 'Normalise messy test data'),
}

PARTS = [
    part('variables', '📦', 'Variables with let and const', '''
<p>A <b>variable</b> is a name for a value. Modern JavaScript has two keywords for creating one.</p>
<div class="vs"><div><b>const</b>The name always points at the same value. Use it by default, for URLs, selectors, test data and almost everything else.</div><div><b>let</b>The name can be pointed at a new value later. Use it for counters, totals and values that really change.</div></div>
[[let-const]]
<div class="exam"><code>const</code> does not freeze an object. It only stops the name from being reassigned. Use <code>Object.freeze(obj)</code> when the contents must not change either.</div>
<h3>And var</h3>
<p><code>var</code> is the original keyword from 1995. It ignores blocks and can be used before its line runs, which causes bugs. You will still see it in old code and old tutorials. Do not use it in new code.</p>
[[var-scope]]
<div class="tip">Names are case sensitive and use camelCase: <code>totalPrice</code>, <code>isLoggedIn</code>, <code>maxRetries</code>. Constants that never change across the whole project are often written as <code>MAX_RETRIES</code>.</div>
<div class="qa-box">Keep test configuration in <code>const</code> values at the top of a file or in a config module: <code>const BASE_URL = process.env.BASE_URL ?? "http://localhost:3000"</code>. Changing environments then means changing one line.</div>
''', qa=True, kw=['let', 'const', 'var', 'variable', 'reassign', 'Object.freeze', 'camelCase', 'block scope']),
    part('types', '🧬', 'The types of value', '''
<p>Every value in JavaScript is one of eight types. Seven are <b>primitives</b>, simple values that cannot be changed. Everything else is an <b>object</b>.</p>
<div class="tw"><table class="jt"><tr><th>Type</th><th>Examples</th><th>typeof</th></tr>
<tr><td>string</td><td><code>"Asha"</code>, <code>'ok'</code>, <code>`Hi ${name}`</code></td><td>"string"</td></tr>
<tr><td>number</td><td><code>42</code>, <code>3.14</code>, <code>NaN</code>, <code>Infinity</code></td><td>"number"</td></tr>
<tr><td>bigint</td><td><code>9007199254740993n</code></td><td>"bigint"</td></tr>
<tr><td>boolean</td><td><code>true</code>, <code>false</code></td><td>"boolean"</td></tr>
<tr><td>undefined</td><td>a variable with no value yet, a missing property</td><td>"undefined"</td></tr>
<tr><td>null</td><td>an empty value put there on purpose</td><td>"object" (a famous old bug)</td></tr>
<tr><td>symbol</td><td><code>Symbol("id")</code>, a unique key</td><td>"symbol"</td></tr>
<tr><td>object</td><td><code>{}</code>, <code>[]</code>, functions, dates, maps</td><td>"object" or "function"</td></tr>
</table></div>
[[typeof]]
<div class="warn"><code>typeof null</code> is <code>"object"</code> and <code>typeof []</code> is <code>"object"</code> too. Check for null with <code>value === null</code> and for arrays with <code>Array.isArray(value)</code>.</div>
<h3>Copied or shared</h3>
<div class="viz" data-viz="lanes" data-k="copy"></div>
[[copy]]
<div class="qa-box">This explains a common test bug. A shared object used as test data is changed by one test and the next test sees the change. Build fresh data in a <code>beforeEach</code> hook or copy it with <code>structuredClone(data)</code>.</div>
''', qa=['Jest', 'Playwright'], kw=['primitive', 'string', 'number', 'bigint', 'boolean', 'undefined', 'null', 'symbol', 'object', 'typeof', 'reference', 'copy by value', 'shared object']),
    part('numbers', '🔢', 'Numbers, NaN and BigInt', '''
<p>JavaScript has one number type for whole numbers and decimals. It stores them in binary, so some decimals cannot be stored exactly.</p>
[[numbers]]
<ul>
<li><code>0.1 + 0.2</code> is not exactly <code>0.3</code>. Compare decimals with a small tolerance, or round them first.</li>
<li><code>NaN</code> means "not a number", the result of a failed calculation. It is the only value not equal to itself, so test it with <code>Number.isNaN</code>.</li>
<li>Whole numbers are exact up to <code>Number.MAX_SAFE_INTEGER</code> (about 9 quadrillion). Larger IDs, such as some database keys, need <b>BigInt</b> or must stay strings.</li>
</ul>
[[money]]
<div class="rule">Store money in the smallest unit as a whole number and format it only for display. Never add up prices as decimals.</div>
<div class="qa-box">Checking a cart total such as <code>expect(total).toBe(0.3)</code> can fail for the wrong reason. Use <code>toBeCloseTo</code> in Jest or Vitest, or compare the formatted text the user sees, such as <code>"₹3,898.50"</code>.</div>
''', qa=['Jest', 'Vitest', 'Playwright'], kw=['floating point', '0.1 + 0.2', 'NaN', 'Infinity', 'Number.EPSILON', 'MAX_SAFE_INTEGER', 'BigInt', 'toFixed', 'Intl.NumberFormat', 'money', 'toBeCloseTo']),
    part('coercion', '🔄', 'Type conversion and coercion', '''
<p><b>Conversion</b> is when you change a type on purpose. <b>Coercion</b> is when JavaScript does it for you behind the scenes. Both follow fixed rules.</p>
[[parse]]
<p>When an operator gets the "wrong" type, JavaScript converts the value. The <code>+</code> operator prefers text: if either side is a string, it joins. The other maths operators convert to numbers.</p>
[[coercion]]
<h3>Truthy and falsy</h3>
<p>In an <code>if</code> or with <code>&amp;&amp;</code>, <code>||</code> and <code>!</code>, every value counts as true or false. Only eight values are <b>falsy</b>. Everything else, including <code>"0"</code>, <code>"false"</code>, <code>[]</code> and <code>{}</code>, is <b>truthy</b>.</p>
[[falsy]]
<div class="exam">Values read from an input field, a URL or an environment variable are always strings. <code>process.env.HEADLESS</code> set to <code>"false"</code> is truthy. Compare it with the text: <code>process.env.HEADLESS === "true"</code>.</div>
''', qa=True, qa_why='Every value read from the page with textContent, inputValue or getAttribute is a string.',
        kw=['coercion', 'type conversion', 'Number()', 'String()', 'Boolean()', 'parseInt', 'parseFloat', 'truthy', 'falsy', 'string concatenation', 'environment variable']),
    part('equality', '⚖️', 'Equality: ==, === and Object.is', '''
<p>JavaScript has three ways to ask "are these the same".</p>
<div class="viz" data-viz="coerce"></div>
[[equality]]
<ul>
<li><code>===</code> (strict equality) compares without converting. Use it everywhere.</li>
<li><code>==</code> (loose equality) converts first, which gives surprises such as <code>0 == ""</code>. The one useful case is <code>x == null</code>, which is true for both <code>null</code> and <code>undefined</code>.</li>
<li><code>Object.is</code> is like <code>===</code> except that <code>NaN</code> equals <code>NaN</code> and <code>0</code> differs from <code>-0</code>.</li>
<li>Objects and arrays are equal only when they are the <b>same object</b>. Two objects with the same contents are not <code>===</code>.</li>
</ul>
<p>Test runners have the same split. In Jest and Vitest, <code>toBe</code> uses <code>Object.is</code> and <code>toEqual</code> compares contents. The first test below fails on purpose so you can read the message.</p>
[[jest-eq]]
<div class="qa-box">Choose the matcher by what you compare: <code>toBe</code> for numbers, strings and booleans, <code>toEqual</code> or <code>toStrictEqual</code> for objects and arrays, <code>toBeCloseTo</code> for decimals. Chai uses <code>equal</code> and <code>deep.equal</code>, and Playwright's <code>expect</code> has the same <code>toBe</code> and <code>toEqual</code>.</div>
''', qa=['Jest', 'Vitest', 'Chai', 'Playwright'], qa_why='Picking the wrong equality is the most common reason a correct assertion fails.',
        kw=['==', '===', 'strict equality', 'loose equality', 'Object.is', 'NaN', 'toBe', 'toEqual', 'toStrictEqual', 'deep equal', 'reference equality']),
    part('operators', '➕', 'Operators', '''
<p>Operators combine values. Most of them you know from maths. A few are special to JavaScript and very handy.</p>
[[operators]]
<div class="tw"><table class="jt"><tr><th>Group</th><th>Operators</th></tr>
<tr><td>Arithmetic</td><td><code>+ - * / % **</code>, and <code>++</code> and <code>--</code> to add or take away one</td></tr>
<tr><td>Assignment</td><td><code>= += -= *= /= %= **=</code></td></tr>
<tr><td>Comparison</td><td><code>=== !== &lt; &gt; &lt;= &gt;=</code></td></tr>
<tr><td>Logical</td><td><code>&amp;&amp;</code> (and), <code>||</code> (or), <code>!</code> (not). They return one of their values, not just true or false.</td></tr>
<tr><td>Nullish</td><td><code>??</code> uses the right side only when the left is <code>null</code> or <code>undefined</code></td></tr>
<tr><td>Optional chaining</td><td><code>?.</code> stops and gives <code>undefined</code> instead of crashing on a missing value</td></tr>
<tr><td>Logical assignment</td><td><code>||= &amp;&amp;= ??=</code> assign only when needed</td></tr>
<tr><td>Conditional</td><td><code>condition ? a : b</code></td></tr>
</table></div>
<h3>?? against ||</h3>
<p><code>||</code> replaces every falsy value, so a real <code>0</code> or an empty string is lost. <code>??</code> replaces only <code>null</code> and <code>undefined</code>. For defaults such as a timeout or a retry count, <code>??</code> is almost always what you want.</p>
[[optional]]
<div class="qa-box">API responses are full of optional fields. <code>body.data?.items?.[0]?.id</code> reads deep values without a crash, so the assertion that follows fails with a clear message instead of a TypeError.</div>
''', qa=['Playwright', 'Cypress', 'Jest'], kw=['operators', 'modulo', 'exponent', 'ternary', 'logical AND', 'logical OR', 'nullish coalescing', '??', 'optional chaining', '?.', '||=', '??=', '&&=']),
    part('scenario', '🎬', 'Real world scenario: clean up data from an API', '''
<div class="scenario"><b>The situation</b>A product API returns prices as text with a currency sign, stock as text and a discount that is sometimes missing. Before you can check the numbers, you must turn them into real numbers without crashing on the gaps.</div>
[[scenario]]
<p>Every tool from this chapter is here: <code>??</code> for missing values, <code>?.</code> for the optional discount, explicit <code>Number</code> conversion, and a check with <code>Number.isNaN</code> for anything that went wrong.</p>
<div class="dev-box">The same <code>toNumber</code> helper is useful in the app itself. Parsing input once, at the edge, keeps the rest of the code working with clean types.</div>
''', qa=True, kw=['normalise data', 'API response', 'parse price', 'test data', 'console.table', 'map', 'filter']),
]

LANES = {
    'copy': {'t': 'What a variable really holds', 's': 'Step through to see a number copied and an object shared.', 'code': 'let a = 5;\nlet b = a;\nb = 10;\nconst cart1 = { items: 1 };\nconst cart2 = cart1;\ncart2.items = 99;',
             'lanes': ['Variables', 'Objects in memory'], 'tone': [2, 0],
             'steps': [{'l': 1, 'v': [['a = 5'], []], 'm': 'a holds the number 5 itself.'},
                       {'l': 2, 'v': [['a = 5', 'b = 5'], []], 'm': 'b gets its own copy of 5.'},
                       {'l': 3, 'v': [['a = 5', 'b = 10'], []], 'm': 'Changing b does not touch a.'},
                       {'l': 4, 'v': [['a = 5', 'b = 10', 'cart1 → #1'], ['#1 { items: 1 }']], 'm': 'The object lives in memory. cart1 holds only an arrow to it.'},
                       {'l': 5, 'v': [['a = 5', 'b = 10', 'cart1 → #1', 'cart2 → #1'], ['#1 { items: 1 }']], 'm': 'cart2 copies the arrow, not the object. Both point at #1.'},
                       {'l': 6, 'v': [['a = 5', 'b = 10', 'cart1 → #1', 'cart2 → #1'], ['#1 { items: 99 }']], 'm': 'Changing the object through cart2 is visible through cart1 too.'}]},
}

INFO = {'title': 'Values, types and the comparisons between them', 'panels': [
    panel([['e', '📦'], ['t', 'const url = "..."', {'b': 1}]], 'Name a value', 'const and let give a value a name.', 'Use const unless the name really must point somewhere new.'),
    panel([['e', '🧬'], ['t', 'typeof 42 → "number"', {'b': 1}]], 'Every value has a type', 'Seven primitive types plus objects.', 'typeof null says "object", an old mistake kept for compatibility.'),
    panel([['e', '🔄'], ['t', '"5" + 3 → "53"', {'b': 1}]], 'Types get converted', 'Operators convert values that do not match.', 'Plus joins text when one side is a string. The others turn text into numbers.'),
    panel([['e', '⚖️'], ['t', '5 === "5" → false', {'b': 1}]], 'Compare strictly', 'Use === so nothing is converted behind your back.', 'Objects are equal only when they are the very same object.')],
    'remember': 'const by default, === always, ?? for defaults.'}

REAL = [
    ['🧾', 'An invoice total', 'Billing code keeps amounts in paise or cents as whole numbers and formats them with Intl.NumberFormat only on screen.'],
    ['🔐', 'A feature flag', 'A script reads FEATURE_NEW_CHECKOUT from the environment. It arrives as the string "false", which is truthy, so the code compares it with "true".'],
    ['📮', 'An API response', 'An order may have no delivery address yet. order.address?.city ?? "Not set" shows a label instead of crashing the page.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers variables, the types of value, numbers, conversions, equality and every operator you will use.',
        'यह अध्याय variables, values के types, numbers, conversions, equality और सभी operators सिखाता है।',
        'ಈ ಅಧ್ಯಾಯ variables, values ನ types, numbers, conversions, equality ಮತ್ತು ಎಲ್ಲ operators ಕಲಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ variables, values ର types, numbers, conversions, equality ଏବଂ ସମସ୍ତ operators ଶିଖାଏ।',
        'يتناول هذا الفصل المتغيرات وأنواع القيم والأرقام والتحويلات والمساواة وكل العوامل التي ستستخدمها.',
        'Dieses Kapitel behandelt Variablen, Werttypen, Zahlen, Umwandlungen, Gleichheit und alle Operatoren.'),
    say('variables', 'Variables', 'Use const by default and let when the value really changes. Avoid var in new code because it leaks out of blocks.',
        'Default रूप से const और जब value सच में बदले तब let इस्तेमाल करें। नए code में var से बचें, यह blocks से बाहर निकल जाता है।',
        'ಸಾಮಾನ್ಯವಾಗಿ const ಬಳಸಿ, value ನಿಜವಾಗಿ ಬದಲಾದರೆ let ಬಳಸಿ. ಹೊಸ code ನಲ್ಲಿ var ಬೇಡ, ಅದು blocks ಹೊರಗೆ ಹೋಗುತ್ತದೆ.',
        'Default ଭାବେ const ଏବଂ value ପ୍ରକୃତରେ ବଦଳିଲେ let ବ୍ୟବହାର କରନ୍ତୁ। ନୂଆ code ରେ var ଏଡ଼ାନ୍ତୁ, ଏହା blocks ବାହାରକୁ ଯାଏ।',
        'استخدم const افتراضيًا وlet عندما تتغير القيمة فعلًا. تجنب var في الكود الجديد لأنها تخرج من الكتل.',
        'Nimm standardmäßig const und let, wenn sich der Wert wirklich ändert. Vermeide var, weil es aus Blöcken heraussickert.'),
    say('types', 'Types', 'There are seven primitive types and objects. Primitives are copied, while objects are shared between every name that points at them.',
        'सात primitive types और objects होते हैं। Primitives copy होते हैं, जबकि objects उन सभी names में shared रहते हैं जो उनकी ओर point करते हैं।',
        'ಏಳು primitive types ಮತ್ತು objects ಇವೆ. Primitives copy ಆಗುತ್ತವೆ, objects ಅವುಗಳನ್ನು ತೋರಿಸುವ ಎಲ್ಲ names ನಡುವೆ shared ಆಗಿರುತ್ತವೆ.',
        'ସାତଟି primitive types ଏବଂ objects ଅଛି। Primitives copy ହୁଏ, objects ସେମାନଙ୍କୁ ଦେଖାଉଥିବା ସବୁ names ମଧ୍ୟରେ shared ରହେ।',
        'هناك سبعة أنواع أولية بالإضافة إلى الكائنات. الأنواع الأولية تُنسخ، أما الكائنات فتُشارك بين كل الأسماء التي تشير إليها.',
        'Es gibt sieben primitive Typen und Objekte. Primitive werden kopiert, Objekte werden zwischen allen Namen geteilt, die auf sie zeigen.'),
    say('numbers', 'Numbers', 'Decimals are stored in binary, so zero point one plus zero point two is not exactly zero point three. Keep money in whole cents and use BigInt for huge numbers.',
        'Decimals binary में store होते हैं, इसलिए 0.1 + 0.2 ठीक 0.3 नहीं होता। पैसे पूरे paise में रखें और बहुत बड़ी संख्याओं के लिए BigInt इस्तेमाल करें।',
        'Decimals binary ಯಲ್ಲಿ store ಆಗುತ್ತವೆ, ಆದ್ದರಿಂದ 0.1 + 0.2 ನಿಖರವಾಗಿ 0.3 ಅಲ್ಲ. ಹಣವನ್ನು ಪೂರ್ಣ paise ನಲ್ಲಿ ಇಡಿ, ದೊಡ್ಡ ಸಂಖ್ಯೆಗೆ BigInt ಬಳಸಿ.',
        'Decimals binary ରେ store ହୁଏ, ତେଣୁ 0.1 + 0.2 ଠିକ୍ 0.3 ନୁହେଁ। ଟଙ୍କାକୁ ପୂର୍ଣ୍ଣ paise ରେ ରଖନ୍ତୁ ଏବଂ ବହୁତ ବଡ଼ ସଂଖ୍ୟା ପାଇଁ BigInt ବ୍ୟବହାର କରନ୍ତୁ।',
        'تُخزن الكسور بالنظام الثنائي، لذا فإن 0.1 زائد 0.2 لا يساوي 0.3 بالضبط. احفظ المال بالوحدة الصغرى واستخدم BigInt للأعداد الضخمة.',
        'Dezimalzahlen werden binär gespeichert, deshalb ist 0,1 plus 0,2 nicht genau 0,3. Speichere Geld in ganzen Cent und nutze BigInt für riesige Zahlen.'),
    say('coercion', 'Coercion', 'Plus joins text when one side is a string, other operators turn text into numbers. Only eight values are falsy, and the string false is truthy.',
        'एक side string हो तो plus text जोड़ता है, बाकी operators text को numbers में बदलते हैं। सिर्फ आठ values falsy हैं, और string "false" truthy है।',
        'ಒಂದು ಬದಿ string ಆಗಿದ್ದರೆ plus text ಜೋಡಿಸುತ್ತದೆ, ಇತರ operators text ಅನ್ನು numbers ಆಗಿಸುತ್ತವೆ. ಎಂಟು values ಮಾತ್ರ falsy, string "false" truthy.',
        'ଗୋଟିଏ ପାଖ string ହେଲେ plus text ଯୋଡ଼େ, ଅନ୍ୟ operators text କୁ numbers କରନ୍ତି। କେବଳ ଆଠଟି values falsy, ଏବଂ string "false" truthy।',
        'يجمع الزائد النصوص إذا كان أحد الطرفين نصًا، والعوامل الأخرى تحول النص إلى أرقام. ثماني قيم فقط زائفة، والنص false قيمته صحيحة.',
        'Plus verbindet Text, wenn eine Seite ein String ist, andere Operatoren machen Text zu Zahlen. Nur acht Werte sind falsy, der String false ist truthy.'),
    say('equality', 'Equality', 'Use triple equals everywhere. Objects are equal only when they are the same object, which is why tests use toEqual for contents.',
        'हर जगह === इस्तेमाल करें। Objects तभी बराबर हैं जब वे एक ही object हों, इसलिए tests contents के लिए toEqual इस्तेमाल करते हैं।',
        'ಎಲ್ಲೆಡೆ === ಬಳಸಿ. Objects ಒಂದೇ object ಆಗಿದ್ದರೆ ಮಾತ್ರ ಸಮಾನ, ಆದ್ದರಿಂದ tests contents ಗಾಗಿ toEqual ಬಳಸುತ್ತವೆ.',
        'ସବୁଠି === ବ୍ୟବହାର କରନ୍ତୁ। Objects ସମାନ ହୁଏ କେବଳ ଯେତେବେଳେ ସେଗୁଡ଼ିକ ସେହି ଗୋଟିଏ object, ତେଣୁ tests contents ପାଇଁ toEqual ବ୍ୟବହାର କରନ୍ତି।',
        'استخدم المساواة الثلاثية في كل مكان. الكائنات متساوية فقط إذا كانت نفس الكائن، ولهذا تستخدم الاختبارات toEqual للمحتوى.',
        'Nutze überall dreifaches Gleich. Objekte sind nur gleich, wenn es dasselbe Objekt ist, deshalb nutzen Tests toEqual für Inhalte.'),
    say('operators', 'Operators', 'Logical operators return one of their values. Nullish coalescing replaces only null and undefined, and optional chaining stops safely at a missing value.',
        'Logical operators अपनी values में से एक लौटाते हैं। ?? सिर्फ null और undefined को बदलता है, और ?. missing value पर सुरक्षित रूप से रुक जाता है।',
        'Logical operators ತಮ್ಮ values ನಲ್ಲಿ ಒಂದನ್ನು ಹಿಂದಿರುಗಿಸುತ್ತವೆ. ?? null ಮತ್ತು undefined ಅನ್ನು ಮಾತ್ರ ಬದಲಿಸುತ್ತದೆ, ?. missing value ನಲ್ಲಿ ಸುರಕ್ಷಿತವಾಗಿ ನಿಲ್ಲುತ್ತದೆ.',
        'Logical operators ନିଜ values ମଧ୍ୟରୁ ଗୋଟିଏ ଫେରାନ୍ତି। ?? କେବଳ null ଓ undefined ବଦଳାଏ, ଏବଂ ?. missing value ରେ ସୁରକ୍ଷିତ ଭାବେ ଅଟକେ।',
        'تعيد العوامل المنطقية إحدى قيمها. عامل ?? يستبدل null وundefined فقط، والتسلسل الاختياري يتوقف بأمان عند القيمة المفقودة.',
        'Logische Operatoren geben einen ihrer Werte zurück. ?? ersetzt nur null und undefined, und optionales Verketten stoppt sicher bei einem fehlenden Wert.'),
    say('scenario', 'Scenario', 'Messy API data is turned into clean numbers with explicit conversion, nullish defaults and optional chaining, then checked for gaps.',
        'गंदा API data explicit conversion, ?? defaults और ?. से साफ numbers में बदला जाता है, फिर gaps के लिए जाँचा जाता है।',
        'ಗೊಂದಲದ API data explicit conversion, ?? defaults ಮತ್ತು ?. ಮೂಲಕ ಸ್ವಚ್ಛ numbers ಆಗುತ್ತದೆ, ನಂತರ gaps ಗಾಗಿ ಪರಿಶೀಲಿಸಲಾಗುತ್ತದೆ.',
        'ଅସଜଡ଼ା API data explicit conversion, ?? defaults ଓ ?. ଦ୍ୱାରା ସଫା numbers ହୁଏ, ତାପରେ gaps ପାଇଁ ଯାଞ୍ଚ ହୁଏ।',
        'تتحول بيانات API الفوضوية إلى أرقام نظيفة بالتحويل الصريح والقيم الافتراضية والتسلسل الاختياري، ثم تُفحص بحثًا عن الفجوات.',
        'Unordentliche API-Daten werden mit expliziter Umwandlung, Standardwerten und optionalem Verketten zu sauberen Zahlen und dann auf Lücken geprüft.'),
    say('practice', 'Hands-on', 'Practise conversions, safe reads and comparisons. Each exercise runs its tests in your browser.',
        'Conversions, safe reads और comparisons का अभ्यास करें। हर exercise अपने tests आपके browser में चलाती है।',
        'Conversions, safe reads ಮತ್ತು comparisons ಅಭ್ಯಾಸ ಮಾಡಿ. ಪ್ರತಿ exercise ನಿಮ್ಮ browser ನಲ್ಲಿ tests ಓಡಿಸುತ್ತದೆ.',
        'Conversions, safe reads ଓ comparisons ଅଭ୍ୟାସ କରନ୍ତୁ। ପ୍ରତ୍ୟେକ exercise ଆପଣଙ୍କ browser ରେ tests ଚଲାଏ।',
        'تدرب على التحويلات والقراءة الآمنة والمقارنات. كل تمرين يشغل اختباراته في متصفحك.',
        'Übe Umwandlungen, sicheres Lesen und Vergleiche. Jede Übung führt ihre Tests in deinem Browser aus.'),
]

QUIZ = [
    quiz('e', 'Which keyword should you use for a base URL that never changes?', ['const', 'let', 'var', 'static'], 0, 'It is never reassigned.', '<code>const</code> says the name will always point at this value.'),
    quiz('e', 'What does this print?', ['"53"', '8', '53', 'An error'], 2, '+ with a string joins text.', 'One side is a string, so <code>+</code> joins: <code>53</code>. console.log prints a string without quotes.', code='console.log("5" + 3);'),
    quiz('e', 'Which of these is falsy?', ['0', '"0"', '[]', '"false"'], 0, 'Only eight values are falsy.', 'The number <code>0</code> is falsy. Any non empty string and every array are truthy.'),
    quiz('m', 'What does this print?', ['0', '"Unknown"', 'Unknown', 'undefined'], 0, '?? only replaces null and undefined.', '<code>0</code> is neither null nor undefined, so <code>??</code> keeps it.', code='const qty = 0;\nconsole.log(qty ?? "Unknown");'),
    quiz('m', 'What does this print?', ['1', '99', 'undefined', 'An error'], 1, 'How many objects exist?', 'Both names point at one object, so the change made through <code>b</code> shows through <code>a</code>.', code='const a = { n: 1 };\nconst b = a;\nb.n = 99;\nconsole.log(a.n);'),
    quiz('m', 'Which Jest matcher should check that an API returned { id: 1, name: "Asha" }?', ['toEqual', 'toBe', 'toBeTruthy', 'toBeCloseTo'], 0, 'You care about the contents.', '<code>toEqual</code> compares contents recursively. <code>toBe</code> would need the very same object.'),
    quiz('h', 'What does typeof null return?', ['"object"', '"null"', '"undefined"', '"empty"'], 0, 'It is a famous bug.', 'A mistake from the first version of the language, kept so old pages keep working.'),
    quiz('h', 'process.env.HEADLESS is set to the text false. Which check correctly turns headless mode off?', ['process.env.HEADLESS === "true"', 'Boolean(process.env.HEADLESS)', '!!process.env.HEADLESS', 'process.env.HEADLESS == true'], 0, 'Environment values are always strings.',
         'The string "false" is truthy, so the Boolean based checks say true. Compare the text instead.'),
    quiz('h', 'What does this print?', ['false true', 'true true', 'false false', 'true false'], 0, '=== never converts. Object.is has two special cases.', '<code>NaN === NaN</code> is false. <code>Object.is(NaN, NaN)</code> is true.', code='console.log(NaN === NaN, Object.is(NaN, NaN));'),
    quiz('x', 'What does this print?', ['9007199254740992', '9007199254740993', 'Infinity', 'A RangeError'], 0, 'It is above MAX_SAFE_INTEGER.', 'The number cannot be stored exactly, so it is rounded to the nearest number a double can hold.', code='console.log(9007199254740993);'),
    quiz('x', 'What does [] + {} give?', ['"[object Object]"', '0', 'NaN', 'An error'], 0, 'Both sides are turned into strings first.', 'An empty array becomes "" and a plain object becomes "[object Object]". Joining them gives "[object Object]".'),
    quiz('x', 'Which expression is true only when value is null or undefined?', ['value == null', 'value === null', '!value', 'typeof value === "undefined"'], 0, 'This is the one good use of loose equality.',
         '<code>== null</code> matches null and undefined and nothing else. <code>!value</code> is also true for 0 and "".'),
]

CALC = [
    calc('e', 'What does this print?', '2', '- converts the text to a number.', ['<span class="eq">"5" - 3 = 5 - 3 = 2</span>'], code='console.log("5" - 3);'),
    calc('e', 'What is the value of score at the end?', '26', 'Work line by line.', ['10 + 5 = 15', '15 × 2 = 30', '30 - 4 = 26'], code='let score = 10;\nscore += 5;\nscore *= 2;\nscore -= 4;'),
    calc('m', 'What does 17 % 5 give?', '2', '% is the remainder after dividing.', ['<span class="eq">17 = 5 × 3 + 2</span>', 'The remainder is 2.']),
    calc('m', 'What does this print?', '3', 'The empty retries value is falsy.', ['<code>0</code> is falsy, so <code>||=</code> assigns 3.'], code='const s = { retries: 0 };\ns.retries ||= 3;\nconsole.log(s.retries);'),
    calc('h', 'A shirt costs ₹1299.50. Stored in paise, what is the total for 3 shirts in paise?', '389850', 'Turn rupees into paise first.', ['<span class="eq">1299.50 × 100 = 129950 paise</span>', '<span class="eq">129950 × 3 = 389850</span>']),
    calc('h', 'How many of these are truthy: 0, "0", "", [], null, "false", NaN, {}?', '4', 'Check each one against the falsy list.', ['Falsy: 0, "", null, NaN.', 'Truthy: "0", [], "false", {}. That is 4.']),
    calc('x', 'What does this print?', '1', 'true becomes 1 and null becomes 0.', ['<span class="eq">true + null = 1 + 0 = 1</span>'], code='console.log(true + null);'),
    calc('x', 'What is 2 ** 3 ** 2?', '512', '** groups from the right.', ['<span class="eq">3 ** 2 = 9</span>', '<span class="eq">2 ** 9 = 512</span>']),
]

EX = [
    ex('price', 'e', 'Read a price', '<p>Write <code>toPaise(text)</code>. It gets a price as shown on a page, such as <code>"₹1,299.50"</code>, and returns the amount in paise as a whole number (<code>129950</code>).</p>',
       'function toPaise(text) {\n  \n}\n', [('toPaise("₹1,299.50")', 129950), ('toPaise("₹499")', 49900), ('toPaise("₹0.99")', 99)],
       'function toPaise(text) {\n  const rupees = Number(text.replace(/[^0-9.]/g, ""));\n  return Math.round(rupees * 100);\n}',
       hint='Remove everything that is not a digit or a dot, convert with <code>Number</code>, then multiply by 100 and round.',
       why='<code>Math.round</code> removes tiny floating point errors such as 129949.99999.'),
    ex('city', 'm', 'Read a value that may be missing', '<p>Write <code>cityOf(user)</code> that returns <code>user.address.city</code>, or <code>"Unknown"</code> when the user, the address or the city is missing. An empty string city should stay an empty string.</p>',
       'function cityOf(user) {\n  return user.address.city;\n}\n',
       [('cityOf({ address: { city: "Pune" } })', 'Pune'), ('cityOf({ address: null })', 'Unknown'), ('cityOf(undefined)', 'Unknown'), ('cityOf({ address: { city: "" } })', '')],
       'function cityOf(user) {\n  return user?.address?.city ?? "Unknown";\n}', hint='Combine <code>?.</code> and <code>??</code>.',
       why='<code>??</code> keeps the empty string because it only replaces null and undefined. <code>||</code> would have turned it into "Unknown".'),
    ex('close', 'h', 'Compare decimals', '<p>Write <code>closeTo(a, b, places = 2)</code> that returns true when <code>a</code> and <code>b</code> are equal to that many decimal places, the way Jest\'s <code>toBeCloseTo</code> works: the difference must be less than <code>10 ** -places / 2</code>.</p>',
       'function closeTo(a, b, places = 2) {\n  return a === b;\n}\n',
       [('closeTo(0.1 + 0.2, 0.3)', True), ('closeTo(1.005, 1.0)', True), ('closeTo(1.01, 1.0)', False), ('closeTo(3.14159, 3.1416, 4)', True), ('closeTo(3.14159, 3.15, 2)', False)],
       'function closeTo(a, b, places = 2) {\n  return Math.abs(a - b) < 10 ** -places / 2;\n}', hint='Compare <code>Math.abs(a - b)</code> with the allowed difference.',
       why='This is exactly the rule Jest uses, which is why <code>toBeCloseTo(0.3)</code> passes for <code>0.1 + 0.2</code>.'),
    ex('same', 'x', 'Write your own Object.is', '<p>Write <code>same(a, b)</code> that behaves like <code>Object.is</code> without calling it: like <code>===</code>, except that <code>NaN</code> equals <code>NaN</code> and <code>0</code> and <code>-0</code> are different.</p>',
       'function same(a, b) {\n  return a === b;\n}\n',
       [('same(1, 1)', True), ('same(NaN, NaN)', True), ('same(0, -0)', False), ('same(-0, -0)', True), ('same("a", "a")', True), ('same({}, {})', False)],
       'function same(a, b) {\n  if (a === b) {\n    return a !== 0 || 1 / a === 1 / b;\n  }\n  return a !== a && b !== b;\n}',
       hint='Only NaN is not equal to itself. And <code>1 / 0</code> is Infinity while <code>1 / -0</code> is -Infinity.',
       why='When <code>a === b</code> and both are zero, dividing 1 by each tells +0 from -0. When they are not equal, both must be NaN to count as the same.'),
]

T = {
    'slug': 'js-values-types', 'title': 'Variables, Types and Operators', 'short': 'Variables and types', 'emoji': '🔢', 'module': MODULE, 'minutes': 18,
    'lead': 'let and const, the seven primitive types, why 0.1 + 0.2 is not 0.3, how JavaScript converts values by itself, the three kinds of equality and every operator, including ?. and ??.',
    'desc': 'Variables with let and const, primitive types, numbers and BigInt, type coercion, truthy and falsy, ==, === and Object.is, and all JavaScript operators.',
    'summary': 'let, const and var, the seven primitive types and objects, copy by value against shared objects, floating point numbers, NaN and BigInt, conversion and coercion, truthy and falsy values, ==, === and Object.is with Jest matchers, and every operator including optional chaining and nullish coalescing.',
    'keywords': ['variables', 'let', 'const', 'var', 'data types', 'typeof', 'number', 'BigInt', 'NaN', 'coercion', 'truthy', 'falsy', 'equality', '===', 'operators', 'optional chaining', 'nullish coalescing'],
    'qa_intro': 'Testers need this chapter for assertions: which equality a matcher uses, why text read from a page must be converted, and how to read optional fields from an API without crashes.',
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
