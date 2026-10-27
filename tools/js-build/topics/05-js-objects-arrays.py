# Chapter 5: objects, destructuring, spread and copies, arrays and every array method, grouping.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('📦', 'Working with data', 'js-data', 'Objects, arrays, text, numbers, dates, JSON and collections: the data every app and every test handles.')

CODES = {
    'objects': run('''
const product = {
  id: 101,
  name: "Wireless Mouse",
  "list-price": 899,            // a key with a dash needs quotes
  tags: ["electronics", "office"],
  seller: { name: "TechMart", rating: 4.6 },
  label() { return `${this.name} (#${this.id})`; },   // a method
};

console.log(product.name, product["list-price"], product.seller.rating);
const field = "id";
console.log(product[field]);       // brackets take any expression
console.log(product.label());

product.stock = 25;                // add
product.name = "Silent Mouse";     // change
delete product.tags;               // remove
console.log("stock" in product, Object.hasOwn(product, "tags"));
console.log(Object.keys(product));
''', 'Creating and changing objects'),
    'object-tools': run('''
const name = "Asha", role = "admin";
const key = "lastLogin";
const user = { name, role, [key]: "2026-10-20" };   // shorthand and a computed key
console.log(user);

console.log(Object.values(user));
for (const [k, v] of Object.entries(user)) console.log(`${k} -> ${v}`);

const prices = { pen: 20, book: 350, bag: 1200 };
const withTax = Object.fromEntries(
  Object.entries(prices).map(([item, p]) => [item, Math.round(p * 1.18)])
);
console.log(withTax);

const config = Object.freeze({ baseUrl: "https://shop.example", retries: 2 });
config.retries = 99;               // ignored (it would throw in strict code)
console.log(config.retries);
''', 'Shorthand, entries and freeze', file='objtools.cjs'),
    'destructure': run('''
const response = {
  status: 200,
  data: { user: { id: 7, name: "Asha", email: "asha@example.com" }, roles: ["admin", "editor"] },
};

const { status, data: { user: { name, email }, roles: [firstRole, ...otherRoles] } } = response;
console.log(status, name, email, firstRole, otherRoles);

const { timeout = 5000, retries: maxRetries = 1 } = { retries: 3 };   // defaults and renaming
console.log(timeout, maxRetries);

let a = 1, b = 2;
[a, b] = [b, a];                    // swap without a temporary variable
console.log(a, b);

const [, second, , fourth = "none"] = ["x", "y", "z"];
console.log(second, fourth);

const { id, ...withoutId } = response.data.user;   // take one field, keep the rest
console.log(id, withoutId);
''', 'Destructuring objects and arrays'),
    'fixture-shape': show('''
// Playwright: the test receives one object and destructures the fixtures it needs
test("search shows results", async ({ page, request, baseURL }) => {
  await page.goto(baseURL + "/search?q=phone");
});

// Jest and Vitest: test.each rows are destructured too
test.each([
  { input: "Secret12", valid: true },
  { input: "short", valid: false },
])("password $input is valid: $valid", ({ input, valid }) => {
  expect(isValidPassword(input)).toBe(valid);
});
''', 'Destructuring inside test runners', note='Snippets, full runs in chapters {{n:js-unit-testing}} to {{n:js-ui-automation}}'),
    'spread': run('''
const defaults = { browser: "chromium", headless: true, retries: 0 };
const ciConfig = { ...defaults, retries: 2 };           // later keys win
console.log(ciConfig);

const base = [1, 2, 3];
const more = [0, ...base, 4];
console.log(more);

const order = { id: 1, items: [{ sku: "A1", qty: 1 }] };
const shallow = { ...order };
shallow.items[0].qty = 99;                               // nested objects are still shared
console.log(order.items[0].qty);

const deep = structuredClone(order);
deep.items[0].qty = 1;
console.log(order.items[0].qty, deep.items[0].qty);
''', 'Spread, shallow copies and deep copies'),
    'arrays': run('''
const tests = ["login", "search"];
tests.push("checkout");          // add to the end
tests.unshift("setup");          // add to the start
console.log(tests, tests.length);
console.log(tests[0], tests.at(-1));   // at(-1) is the last item

const last = tests.pop();        // remove from the end
const first = tests.shift();     // remove from the start
console.log(first, last, tests);

const nums = [10, 20, 30, 40, 50];
console.log(nums.slice(1, 3));           // copy part, original unchanged
const removed = nums.splice(1, 2, 99);   // remove 2 items at index 1 and insert 99
console.log(removed, nums);

console.log(nums.includes(99), nums.indexOf(40), nums.join(" | "));
console.log(Array.from({ length: 4 }, (_, i) => i * i));
console.log([1, [2, [3, [4]]]].flat(Infinity));
''', 'Array basics'),
    'non-mutating': run('''
const scores = [72, 95, 61, 88];

const sortedCopy = scores.toSorted((a, b) => a - b);   // ES2023: a new sorted array
const reversedCopy = scores.toReversed();
const replaced = scores.with(0, 100);                 // copy with index 0 replaced
console.log(scores);
console.log(sortedCopy, reversedCopy, replaced);

scores.sort();                                        // sorts in place, and as TEXT by default
console.log(scores);
console.log([10, 9, 100, 1].sort());                  // the classic surprise
console.log([10, 9, 100, 1].sort((a, b) => a - b));   // numbers need a compare function
''', 'Sorting, and copies instead of changes'),
    'methods': run('''
const cart = [
  { sku: "A1", name: "Mouse", price: 899, qty: 2, inStock: true },
  { sku: "B2", name: "Keyboard", price: 2499, qty: 1, inStock: true },
  { sku: "C3", name: "Webcam", price: 3999, qty: 1, inStock: false },
  { sku: "D4", name: "Pad", price: 299, qty: 3, inStock: true },
];

const names = cart.map(item => item.name);
const available = cart.filter(item => item.inStock);
const total = available.reduce((sum, item) => sum + item.price * item.qty, 0);
const webcam = cart.find(item => item.sku === "C3");
const cheapIndex = cart.findIndex(item => item.price < 500);
const anyOut = cart.some(item => !item.inStock);
const allPriced = cart.every(item => item.price > 0);

console.log(names);
console.log(available.length, total);
console.log(webcam.name, cheapIndex, anyOut, allPriced);
console.log(cart.findLast(item => item.inStock).name);
console.log(cart.flatMap(item => Array(item.qty).fill(item.sku)));
''', 'map, filter, reduce, find, some and every'),
    'chain': run('''
const orders = [
  { id: 1, customer: "asha", total: 1200, status: "delivered" },
  { id: 2, customer: "ravi", total: 450, status: "cancelled" },
  { id: 3, customer: "asha", total: 3100, status: "delivered" },
  { id: 4, customer: "mei", total: 980, status: "delivered" },
];

const topDelivered = orders
  .filter(o => o.status === "delivered")
  .toSorted((a, b) => b.total - a.total)
  .slice(0, 2)
  .map(o => `#${o.id} ${o.customer} ₹${o.total}`);
console.log(topDelivered);
''', 'Chaining methods into a pipeline'),
    'group': run('''
const results = [
  { name: "login", suite: "auth", status: "passed" },
  { name: "logout", suite: "auth", status: "failed" },
  { name: "search", suite: "catalog", status: "passed" },
  { name: "filters", suite: "catalog", status: "passed" },
  { name: "pay", suite: "checkout", status: "failed" },
];

const bySuite = Object.groupBy(results, r => r.suite);       // ES2024
console.log(Object.keys(bySuite), bySuite.auth.length);

const counts = results.reduce((acc, r) => {
  acc[r.status] = (acc[r.status] ?? 0) + 1;
  return acc;
}, {});
console.log(counts);

const suites = [...new Set(results.map(r => r.suite))];      // unique values
console.log(suites);

const failedSuites = Object.entries(bySuite)
  .filter(([, list]) => list.some(r => r.status === "failed"))
  .map(([suite]) => suite);
console.log(failedSuites);
''', 'Grouping, counting and unique values'),
    'scenario': run('''
// Text read from the product cards of a listing sorted by "Price: low to high"
const cardTexts = [
  "Wireless Mouse ₹899",
  "USB Hub ₹1,299",
  "Keyboard ₹2,499",
  "USB Hub ₹1,299",
  "Webcam ₹2,199",
];

const products = cardTexts.map(text => {
  const [, name, price] = text.match(/^(.*) ₹([\\d,]+)$/);
  return { name, price: Number(price.replaceAll(",", "")) };
});
const prices = products.map(p => p.price);

const outOfOrder = prices.findIndex((p, i) => i > 0 && p < prices[i - 1]);
const isSorted = outOfOrder === -1;
const seen = new Set();
const duplicates = products.filter(p => seen.has(p.name) || !seen.add(p.name)).map(p => p.name);

console.log("prices:", prices);
console.log("sorted:", isSorted, isSorted ? "" : `(breaks at position ${outOfOrder}: ${prices[outOfOrder - 1]} then ${prices[outOfOrder]})`);
console.log("duplicates:", duplicates);
console.log("cheapest:", Math.min(...prices), "dearest:", Math.max(...prices));
''', 'Check a sorted product listing'),
    'vitest-arrays': test({
        'package.json': pkg('listing', 'module', {'test': 'vitest run'}),
        'listing.js': '''
export function parseCards(texts) {
  return texts.map(text => {
    const [, name, price] = text.match(/^(.*) ₹([\\d,]+)$/);
    return { name, price: Number(price.replaceAll(",", "")) };
  });
}

export const isSortedAsc = list => list.every((x, i) => i === 0 || list[i - 1] <= x);
''',
        'listing.test.js': '''
import { describe, test, expect } from "vitest";
import { parseCards, isSortedAsc } from "./listing.js";

const cards = ["Wireless Mouse ₹899", "USB Hub ₹1,299", "Keyboard ₹2,499"];

describe("product listing", () => {
  test("parses every card into name and price", () => {
    expect(parseCards(cards)).toEqual([
      { name: "Wireless Mouse", price: 899 },
      { name: "USB Hub", price: 1299 },
      { name: "Keyboard", price: 2499 },
    ]);
  });

  test("contains the hub, whatever else is there", () => {
    expect(parseCards(cards)).toContainEqual({ name: "USB Hub", price: 1299 });
    expect(parseCards(cards)).toEqual(expect.arrayContaining([expect.objectContaining({ name: "Keyboard" })]));
  });

  test.each([
    [[1, 2, 2, 5], true],
    [[3, 1], false],
    [[], true],
  ])("isSortedAsc(%j) is %s", (list, expected) => {
    expect(isSortedAsc(list)).toBe(expected);
  });
});
''',
    }, 'npx vitest run --reporter=verbose', 'Array and object matchers in Vitest', show=['listing.js', 'listing.test.js'],
        replace=[(r' \d+ms', ''), (r'Start at\s+[\d:]+', 'Start at  10:00:00'), (r'Duration\s+[^\n]+', 'Duration  310ms'), (r'(?m)^ RUN .*$', ' RUN  v5 /project')]),
}

PARTS = [
    part('objects', '🗃️', 'Objects', '''
<p>An <b>object</b> groups related values under names called <b>keys</b> or <b>properties</b>. Almost everything you test is an object: a user, an API response, a configuration, a page element.</p>
[[objects]]
<ul>
<li>Use dot notation (<code>user.name</code>) for normal keys and brackets (<code>user["list-price"]</code>, <code>user[field]</code>) for unusual keys or keys held in a variable.</li>
<li>Reading a missing key gives <code>undefined</code>, not an error. Reading a key <i>of</i> a missing object is the error.</li>
<li><code>Object.hasOwn(obj, key)</code> checks whether the object itself has the key.</li>
</ul>
[[object-tools]]
<div class="tip"><code>Object.entries</code> and <code>Object.fromEntries</code> together let you use every array method on an object: turn it into pairs, transform them, turn them back.</div>
''', qa=True, kw=['object', 'property', 'key', 'dot notation', 'bracket notation', 'computed key', 'shorthand', 'Object.keys', 'Object.values', 'Object.entries', 'Object.fromEntries', 'Object.hasOwn', 'Object.freeze', 'delete']),
    part('destructuring', '✂️', 'Destructuring', '''
<p><b>Destructuring</b> pulls values out of objects and arrays into variables in one line. It can rename, give defaults, skip items and collect the rest.</p>
[[destructure]]
<p>Test runners use destructuring all the time, so it is worth being fluent in it.</p>
[[fixture-shape]]
<div class="qa-box">In Playwright, <code>async ({ page })</code> is destructuring: the runner passes one object of fixtures and you pick the ones you need. Only the fixtures you name are set up, which keeps tests fast.</div>
''', qa=['Playwright', 'Jest', 'Vitest'], qa_why='Playwright fixtures and test.each rows arrive as objects you destructure.',
        kw=['destructuring', 'object destructuring', 'array destructuring', 'default values', 'rename', 'rest in destructuring', 'swap', 'fixtures', 'test.each']),
    part('spread', '🧬', 'Spread, copies and immutability', '''
<p>The <b>spread</b> syntax <code>...</code> copies the items of an array or the keys of an object into a new one. When keys repeat, the later one wins, which makes it perfect for "defaults plus overrides".</p>
[[spread]]
<div class="viz" data-viz="lanes" data-k="copies"></div>
<div class="exam">Spread makes a <b>shallow</b> copy: the outer object is new, but nested objects and arrays are shared. Use <code>structuredClone</code> for a full deep copy.</div>
<div class="qa-box">Shared nested test data is a common cause of tests that pass alone and fail together. Give each test its own copy with <code>structuredClone(baseOrder)</code>, or build data with a factory function as in {{ch:js-functions}}.</div>
''', qa=True, kw=['spread', 'shallow copy', 'deep copy', 'structuredClone', 'immutability', 'defaults and overrides', 'object merge']),
    part('arrays', '📚', 'Arrays', '''
<p>An <b>array</b> is an ordered list. Indexes start at 0, <code>length</code> is the number of items and <code>at(-1)</code> reads from the end.</p>
[[arrays]]
<div class="tw"><table class="jt"><tr><th>Changes the array</th><th>Returns a new array or value</th></tr>
<tr><td><code>push pop shift unshift splice sort reverse fill</code></td><td><code>slice concat map filter flat flatMap toSorted toReversed toSpliced with</code></td></tr>
</table></div>
[[non-mutating]]
<div class="warn"><code>sort()</code> without a compare function sorts as <b>text</b>, so <code>100</code> comes before <code>9</code>. For numbers always pass <code>(a, b) =&gt; a - b</code>. It also changes the original array. ES2023 added <code>toSorted</code>, <code>toReversed</code>, <code>toSpliced</code> and <code>with</code>, which leave the original alone.</div>
''', kw=['array', 'index', 'length', 'at', 'push', 'pop', 'shift', 'unshift', 'splice', 'slice', 'includes', 'indexOf', 'join', 'Array.from', 'flat', 'sort', 'compare function', 'toSorted', 'toReversed', 'with']),
    part('array-methods', '⚙️', 'Array methods: map, filter, reduce and friends', '''
<p>These methods replace most hand written loops. Each one takes a function and calls it for every item.</p>
<div class="viz" data-viz="arr"></div>
[[methods]]
<div class="tw"><table class="jt"><tr><th>Method</th><th>Returns</th><th>Typical use</th></tr>
<tr><td><code>map</code></td><td>new array, same length</td><td>turn elements into their text, products into prices</td></tr>
<tr><td><code>filter</code></td><td>new array, only matching items</td><td>failed tests, items in stock</td></tr>
<tr><td><code>reduce</code></td><td>one value built up step by step</td><td>totals, counts, grouping</td></tr>
<tr><td><code>find</code>, <code>findLast</code></td><td>the first (or last) matching item, or undefined</td><td>the row for one SKU</td></tr>
<tr><td><code>findIndex</code></td><td>its index, or -1</td><td>where a sort order breaks</td></tr>
<tr><td><code>some</code>, <code>every</code></td><td>true or false, and they stop early</td><td>"any error shown", "all prices positive"</td></tr>
<tr><td><code>flatMap</code></td><td>map, then flatten one level</td><td>one row per quantity</td></tr>
</table></div>
[[chain]]
<div class="qa-box">Playwright's <code>locator.allTextContents()</code> and Cypress's <code>.then($els =&gt; [...$els].map(el =&gt; el.innerText))</code> hand you an array of strings. From there it is plain JavaScript: <code>map</code> to numbers, <code>every</code> to check sorting, <code>filter</code> to find bad rows.</div>
''', qa=['Playwright', 'Cypress', 'Selenium'], qa_why='Lists of element texts are arrays, and checking them is map, filter and every.',
        kw=['map', 'filter', 'reduce', 'find', 'findIndex', 'findLast', 'some', 'every', 'flatMap', 'method chaining', 'allTextContents', 'array of elements']),
    part('grouping', '🧺', 'Grouping, counting and unique values', '''
<p>Reports need data grouped and counted. ES2024 added <code>Object.groupBy</code> and <code>Map.groupBy</code>. <code>reduce</code> still handles any custom shape, and a <code>Set</code> removes duplicates.</p>
[[group]]
<div class="tip"><code>[...new Set(list)]</code> is the shortest way to remove duplicates from a list of strings or numbers. For objects, compare a key, as the scenario below does.</div>
''', qa=True, kw=['Object.groupBy', 'Map.groupBy', 'group by', 'count', 'reduce to object', 'unique values', 'Set', 'remove duplicates']),
    part('scenario', '🎬', 'Real world scenario: verify a sorted product listing', '''
<div class="scenario"><b>The situation</b>A shop's "Price: low to high" sort has had bugs before. You read the text of every product card on the page and must check three things: the prices really go up, no product is listed twice, and the cheapest and dearest prices are right.</div>
[[scenario]]
<p>The check found two real problems in this data: the second USB Hub at ₹1,299 comes after Keyboard at ₹2,499, so the order breaks at position 3, and USB Hub is listed twice. Both point to the same bug, a duplicated card, which is the kind of finding a good report makes obvious. In a real suite the parsing lives in a helper module with its own unit tests, and the matchers for arrays and objects make the assertions short.</p>
[[vitest-arrays]]
<div class="tw"><table class="jt"><tr><th>Matcher</th><th>Passes when</th></tr>
<tr><td><code>toEqual(list)</code></td><td>same items, same order, compared deeply</td></tr>
<tr><td><code>toContainEqual(item)</code></td><td>at least one item deeply equals <code>item</code></td></tr>
<tr><td><code>expect.arrayContaining([...])</code></td><td>the listed items appear, in any order, others allowed</td></tr>
<tr><td><code>expect.objectContaining({...})</code></td><td>the listed keys match, other keys allowed</td></tr>
<tr><td><code>toHaveLength(n)</code></td><td>the length is <code>n</code></td></tr>
</table></div>
''', qa=['Vitest', 'Jest', 'Playwright'], kw=['sorted listing', 'sort check', 'duplicates', 'toEqual', 'toContainEqual', 'arrayContaining', 'objectContaining', 'test.each', 'Vitest']),
]

LANES = {
    'copies': {'t': 'Shallow copy against deep copy', 'code': 'const order = { id: 1, items: [{ qty: 1 }] };\nconst shallow = { ...order };\nshallow.id = 2;\nshallow.items[0].qty = 99;\nconst deep = structuredClone(order);\ndeep.items[0].qty = 5;',
               'lanes': ['Names', 'Outer objects', 'Nested items'], 'tone': [2, 0, 3],
               'steps': [{'l': 1, 'v': [['order → #1'], ['#1 { id: 1, items → #A }'], ['#A [{ qty: 1 }]']], 'm': 'order points at object #1, whose items property points at array #A.'},
                         {'l': 2, 'v': [['order → #1', 'shallow → #2'], ['#1 { id: 1, items → #A }', '#2 { id: 1, items → #A }'], ['#A [{ qty: 1 }]']], 'm': 'Spread creates a new outer object #2, but copies the arrow to #A. The array is shared.'},
                         {'l': 3, 'v': [['order → #1', 'shallow → #2'], ['#1 { id: 1, items → #A }', '#2 { id: 2, items → #A }'], ['#A [{ qty: 1 }]']], 'm': 'Changing a top level key only changes #2.'},
                         {'l': 4, 'v': [['order → #1', 'shallow → #2'], ['#1 { id: 1, items → #A }', '#2 { id: 2, items → #A }'], ['#A [{ qty: 99 }]']], 'm': 'Changing a nested value changes #A, which order also uses. This is the shallow copy trap.'},
                         {'l': 5, 'v': [['order → #1', 'shallow → #2', 'deep → #3'], ['#1 { id: 1, items → #A }', '#2 { id: 2, items → #A }', '#3 { id: 1, items → #B }'], ['#A [{ qty: 99 }]', '#B [{ qty: 99 }]']], 'm': 'structuredClone copies every level, so deep gets its own array #B.'},
                         {'l': 6, 'v': [['order → #1', 'shallow → #2', 'deep → #3'], ['#1 { id: 1, items → #A }', '#2 { id: 2, items → #A }', '#3 { id: 1, items → #B }'], ['#A [{ qty: 99 }]', '#B [{ qty: 5 }]']], 'm': 'Changes to deep never reach order.'}]},
}

INFO = {'title': 'Data in, data checked', 'panels': [
    panel([['e', '🗃️'], ['t', '{ name: "Asha", role: "admin" }', {'b': 1, 'size': 11}]], 'Objects', 'Named values grouped together.', 'Dot for normal keys, brackets for keys in variables or with dashes.'),
    panel([['e', '✂️'], ['t', 'const { name } = user', {'b': 1}]], 'Destructure', 'Pull values out in one line.', 'Playwright fixtures and test.each rows use exactly this.'),
    panel([['e', '📚'], ['c', [899, 1299, 2499], {'hl': {0: 'ok', 1: 'ok', 2: 'ok'}}]], 'Arrays', 'Ordered lists with powerful methods.', 'map, filter and reduce replace most loops.'),
    panel([['e', '🧪'], ['t', 'prices.every(sorted)', {'b': 1}]], 'Check them', 'Element texts become arrays you can verify.', 'Parse once, then every, some and filter answer the test questions.')],
    'remember': 'Copy before you change, and pass numbers a compare function when sorting.'}

REAL = [
    ['🛍️', 'A shopping cart', 'The cart total is a reduce over the items: price times quantity, summed, for items still in stock.'],
    ['📊', 'A test dashboard', 'Results are grouped by suite with Object.groupBy, and each suite card shows its pass and fail counts.'],
    ['⚙️', 'Tool configuration', 'playwright.config.js spreads shared settings into each project and overrides only the browser and viewport.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers objects, destructuring, copies, arrays, the array methods and grouping data for reports.',
        'यह अध्याय objects, destructuring, copies, arrays, array methods और reports के लिए data grouping सिखाता है।',
        'ಈ ಅಧ್ಯಾಯ objects, destructuring, copies, arrays, array methods ಮತ್ತು reports ಗಾಗಿ data grouping ಕಲಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ objects, destructuring, copies, arrays, array methods ଓ reports ପାଇଁ data grouping ଶିଖାଏ।',
        'يتناول هذا الفصل الكائنات والتفكيك والنسخ والمصفوفات ودوالها وتجميع البيانات للتقارير.',
        'Dieses Kapitel behandelt Objekte, Destrukturierung, Kopien, Arrays, Array-Methoden und das Gruppieren von Daten für Berichte.'),
    say('objects', 'Objects', 'Objects group values under keys. Use dots for normal keys and brackets for keys in variables. entries and fromEntries let you transform an object.',
        'Objects values को keys के नीचे रखते हैं। Normal keys के लिए dot और variables वाली keys के लिए brackets इस्तेमाल करें।',
        'Objects values ಅನ್ನು keys ಅಡಿಯಲ್ಲಿ ಗುಂಪು ಮಾಡುತ್ತವೆ. ಸಾಮಾನ್ಯ keys ಗೆ dot, variable keys ಗೆ brackets ಬಳಸಿ.',
        'Objects values କୁ keys ତଳେ ରଖନ୍ତି। ସାଧାରଣ keys ପାଇଁ dot ଏବଂ variable keys ପାଇଁ brackets ବ୍ୟବହାର କରନ୍ତୁ।',
        'تجمع الكائنات القيم تحت مفاتيح. استخدم النقطة للمفاتيح العادية والأقواس للمفاتيح المخزنة في متغيرات.',
        'Objekte bündeln Werte unter Schlüsseln. Punkt für normale Schlüssel, eckige Klammern für Schlüssel in Variablen.'),
    say('destructuring', 'Destructuring', 'Destructuring pulls values out into variables with renaming, defaults and rest. Playwright fixtures arrive this way.',
        'Destructuring values को renaming, defaults और rest के साथ variables में निकालता है। Playwright fixtures ऐसे ही आते हैं।',
        'Destructuring values ಅನ್ನು renaming, defaults ಮತ್ತು rest ಜೊತೆ variables ಗೆ ತೆಗೆಯುತ್ತದೆ. Playwright fixtures ಹೀಗೆ ಬರುತ್ತವೆ.',
        'Destructuring values କୁ renaming, defaults ଓ rest ସହ variables ରେ ବାହାର କରେ। Playwright fixtures ଏହିପରି ଆସେ।',
        'يستخرج التفكيك القيم إلى متغيرات مع إعادة التسمية والقيم الافتراضية والباقي. هكذا تصل fixtures في Playwright.',
        'Destrukturierung holt Werte mit Umbenennen, Standardwerten und Rest in Variablen. So kommen Playwright-Fixtures an.'),
    say('spread', 'Spread and copies', 'Spread copies only the outer level, so nested objects stay shared. Use structuredClone when you need a full copy.',
        'Spread सिर्फ बाहरी level copy करता है, nested objects shared रहते हैं। पूरी copy के लिए structuredClone इस्तेमाल करें।',
        'Spread ಹೊರಗಿನ level ಮಾತ್ರ copy ಮಾಡುತ್ತದೆ, nested objects shared ಆಗಿರುತ್ತವೆ. ಸಂಪೂರ್ಣ copy ಗೆ structuredClone ಬಳಸಿ.',
        'Spread କେବଳ ବାହାର level copy କରେ, nested objects shared ରହେ। ପୂର୍ଣ୍ଣ copy ପାଇଁ structuredClone ବ୍ୟବହାର କରନ୍ତୁ।',
        'ينسخ الانتشار المستوى الخارجي فقط، فتبقى الكائنات المتداخلة مشتركة. استخدم structuredClone للنسخ الكامل.',
        'Spread kopiert nur die äußere Ebene, verschachtelte Objekte bleiben geteilt. Für eine vollständige Kopie nimm structuredClone.'),
    say('arrays', 'Arrays', 'Arrays are ordered lists starting at index zero. sort without a compare function sorts as text, and toSorted returns a copy.',
        'Arrays zero index से शुरू होने वाली ordered lists हैं। Compare function के बिना sort text की तरह sort करता है, और toSorted copy लौटाता है।',
        'Arrays zero index ನಿಂದ ಶುರುವಾಗುವ ordered lists. Compare function ಇಲ್ಲದೆ sort text ಆಗಿ sort ಮಾಡುತ್ತದೆ, toSorted copy ಹಿಂದಿರುಗಿಸುತ್ತದೆ.',
        'Arrays zero index ରୁ ଆରମ୍ଭ ହେଉଥିବା ordered lists। Compare function ବିନା sort text ଭାବେ sort କରେ, toSorted copy ଫେରାଏ।',
        'المصفوفات قوائم مرتبة تبدأ من الفهرس صفر. الترتيب بدون دالة مقارنة يرتب كنص، وtoSorted تعيد نسخة.',
        'Arrays sind geordnete Listen ab Index null. sort ohne Vergleichsfunktion sortiert als Text, toSorted gibt eine Kopie zurück.'),
    say('array-methods', 'Array methods', 'map transforms, filter keeps matches, reduce builds one value, find returns the first match, and some and every answer yes or no questions.',
        'map बदलता है, filter matches रखता है, reduce एक value बनाता है, find पहला match देता है, और some और every हाँ या ना बताते हैं।',
        'map ಬದಲಿಸುತ್ತದೆ, filter matches ಇಡುತ್ತದೆ, reduce ಒಂದು value ಕಟ್ಟುತ್ತದೆ, find ಮೊದಲ match ಕೊಡುತ್ತದೆ, some ಮತ್ತು every ಹೌದು ಅಥವಾ ಇಲ್ಲ ಹೇಳುತ್ತವೆ.',
        'map ବଦଳାଏ, filter matches ରଖେ, reduce ଗୋଟିଏ value ତିଆରି କରେ, find ପ୍ରଥମ match ଦିଏ, some ଓ every ହଁ ବା ନା କହନ୍ତି।',
        'map تحول، وfilter تحتفظ بالمطابقات، وreduce تبني قيمة واحدة، وfind تعيد أول تطابق، وsome وevery تجيبان بنعم أو لا.',
        'map wandelt um, filter behält Treffer, reduce baut einen Wert, find liefert den ersten Treffer, some und every beantworten Ja-Nein-Fragen.'),
    say('grouping', 'Grouping', 'Object groupBy groups items by a key, reduce counts them, and a Set removes duplicates.',
        'Object.groupBy items को key से group करता है, reduce गिनता है, और Set duplicates हटाता है।',
        'Object.groupBy items ಅನ್ನು key ಮೂಲಕ group ಮಾಡುತ್ತದೆ, reduce ಎಣಿಸುತ್ತದೆ, Set duplicates ತೆಗೆಯುತ್ತದೆ.',
        'Object.groupBy items କୁ key ଅନୁସାରେ group କରେ, reduce ଗଣେ, ଏବଂ Set duplicates ହଟାଏ।',
        'يجمع Object.groupBy العناصر حسب مفتاح، وreduce تعدها، وSet تزيل التكرار.',
        'Object.groupBy gruppiert nach einem Schlüssel, reduce zählt, und ein Set entfernt Duplikate.'),
    say('scenario', 'Scenario', 'Card texts from a sorted listing are parsed into numbers, then checked for order and duplicates, with unit tests for the helper.',
        'Sorted listing के card texts को numbers में parse करके order और duplicates जाँचे जाते हैं, और helper के unit tests भी हैं।',
        'Sorted listing ನ card texts ಅನ್ನು numbers ಆಗಿ parse ಮಾಡಿ order ಮತ್ತು duplicates ಪರಿಶೀಲಿಸಲಾಗುತ್ತದೆ.',
        'Sorted listing ର card texts କୁ numbers ରେ parse କରି order ଓ duplicates ଯାଞ୍ଚ ହୁଏ।',
        'تُحلل نصوص البطاقات من قائمة مرتبة إلى أرقام ثم تُفحص من حيث الترتيب والتكرار، مع اختبارات وحدة للمساعد.',
        'Kartentexte einer sortierten Liste werden in Zahlen zerlegt und auf Reihenfolge und Duplikate geprüft, mit Unit-Tests für den Helfer.'),
    say('practice', 'Hands-on', 'Practise array and object methods, from plucking a field to a deep comparison.',
        'Array और object methods का अभ्यास करें, एक field निकालने से लेकर deep comparison तक।',
        'Array ಮತ್ತು object methods ಅಭ್ಯಾಸ ಮಾಡಿ, ಒಂದು field ತೆಗೆಯುವುದರಿಂದ deep comparison ವರೆಗೆ.',
        'Array ଓ object methods ଅଭ୍ୟାସ କରନ୍ତୁ, ଗୋଟିଏ field ବାହାର କରିବାଠାରୁ deep comparison ପର୍ଯ୍ୟନ୍ତ।',
        'تدرب على دوال المصفوفات والكائنات، من استخراج حقل إلى المقارنة العميقة.',
        'Übe Array- und Objektmethoden, vom Herausziehen eines Feldes bis zum tiefen Vergleich.'),
]

QUIZ = [
    quiz('e', 'Which method returns a new array with every item transformed?', ['map', 'filter', 'forEach', 'find'], 0, 'Same length, new values.', '<code>map</code> returns a new array of the same length.'),
    quiz('e', 'What does [10, 20, 30].at(-1) return?', ['30', '10', 'undefined', '-1'], 0, 'Negative counts from the end.', '<code>at(-1)</code> is the last item.'),
    quiz('e', 'How do you read a key called list-price?', ['product["list-price"]', 'product.list-price', 'product.listPrice', 'product->list-price'], 0, 'The dash is a minus sign in code.', 'Keys with dashes or spaces need bracket notation.'),
    quiz('m', 'What does this print?', ['[ 1, 10, 100, 9 ]', '[ 1, 9, 10, 100 ]', '[ 100, 10, 9, 1 ]', 'An error'], 0, 'Default sort compares text.', 'As text, "10" and "100" come before "9".', code='console.log([10, 9, 100, 1].sort());'),
    quiz('m', 'What does this print?', ['99', '1', 'undefined', 'An error'], 0, 'Is the nested array copied?', 'Spread is shallow, so <code>items</code> is shared.', code='const a = { items: [{ qty: 1 }] };\nconst b = { ...a };\nb.items[0].qty = 99;\nconsole.log(a.items[0].qty);'),
    quiz('m', 'Which method stops at the first item that matches and returns that item?', ['find', 'filter', 'some', 'map'], 0, 'filter returns all matches.', '<code>find</code> returns the first match, or undefined.'),
    quiz('h', 'What are timeout and maxRetries?', ['5000 and 3', 'undefined and 3', '5000 and undefined', 'undefined and undefined'], 0, 'Defaults apply to missing keys.', '<code>timeout</code> is missing so it takes 5000. <code>retries</code> is 3 and is renamed.', code='const { timeout = 5000, retries: maxRetries = 1 } = { retries: 3 };'),
    quiz('h', 'Which matcher passes when an array contains an object with name "Keyboard", whatever its other keys and the other items?', ['expect(list).toEqual(expect.arrayContaining([expect.objectContaining({ name: "Keyboard" })]))', 'expect(list).toEqual([{ name: "Keyboard" }])', 'expect(list).toBe({ name: "Keyboard" })', 'expect(list).toContain("Keyboard")'], 0, 'Combine two asymmetric matchers.',
         'arrayContaining allows other items and objectContaining allows other keys.'),
    quiz('h', 'What does reduce return here?', ['{ passed: 2, failed: 1 }', '3', '[2, 1]', 'undefined'], 0, 'The start value is an object.', 'The accumulator starts as <code>{}</code> and counts each status.', code='["passed", "failed", "passed"].reduce((acc, s) => {\n  acc[s] = (acc[s] ?? 0) + 1;\n  return acc;\n}, {});'),
    quiz('x', 'Which ES2023 method returns a sorted copy and leaves the original unchanged?', ['toSorted', 'sort', 'sorted', 'Array.sort'], 0, 'The "to" methods copy.', '<code>toSorted</code>, <code>toReversed</code>, <code>toSpliced</code> and <code>with</code> never change the original.'),
    quiz('x', 'What does [1, 2, 3].some(x => x > 1) do after checking 2?', ['Stops and returns true', 'Checks 3 and returns true', 'Returns [2, 3]', 'Returns 2'], 0, 'One match is enough.', '<code>some</code> stops at the first match, <code>every</code> stops at the first failure.'),
    quiz('x', 'Why do two tests that pass alone fail together when they share a const testOrder object?', ['One test changes the shared object and the other sees the change', 'const objects cannot be shared', 'Test runners reset const values', 'Objects are copied between tests'], 0, 'const does not freeze.', 'Both tests use the same object. Build a fresh copy per test.'),
]

CALC = [
    calc('e', 'What does [3, 8, 1].map(n => n * 2) give? Write it like [a, b, c].', '[6, 16, 2]', 'Double each.', ['3 × 2 = 6, 8 × 2 = 16, 1 × 2 = 2'], alt=['[6,16,2]', '6, 16, 2', '6,16,2']),
    calc('e', 'What is the length of the array after these lines?', '4', 'Track each change.', ['Start 2, push makes 3, unshift makes 4, pop makes 3, push makes 4.'], code='const a = [1, 2];\na.push(3);\na.unshift(0);\na.pop();\na.push(9);'),
    calc('m', 'What does this reduce return?', '2695', 'Only items in stock count, price times quantity.', ['In stock: the 899 item and the 299 item.', '<span class="eq">899 × 2 = 1798</span>', '<span class="eq">299 × 3 = 897</span>', '<span class="eq">1798 + 897 = 2695</span>'],
         code='const cart = [\n  { price: 899, qty: 2, inStock: true },\n  { price: 2499, qty: 1, inStock: false },\n  { price: 299, qty: 3, inStock: true },\n  { price: 3999, qty: 1, inStock: false },\n];\ncart.filter(i => i.inStock).reduce((s, i) => s + i.price * i.qty, 0);'),
    calc('m', 'How many unique values are in [2, 3, 2, 5, 3, 2]?', '3', 'A Set keeps one of each.', ['The unique values are 2, 3 and 5.']),
    calc('h', 'What does [5, 1, 4].findIndex(x => x > 4) return?', '0', 'Is any item greater than 4, and where is the first?', ['5 > 4 is true at index 0, so the search stops there.']),
    calc('h', 'prices = [899, 1299, 2499, 2199]. What does prices.findIndex((p, i) => i > 0 && p < prices[i - 1]) return?', '3', 'Find where a price is lower than the one before.', ['Index 1: 1299 is not lower than 899.', 'Index 2: 2499 is not lower than 1299.', 'Index 3: 2199 is lower than 2499. The answer is 3.']),
    calc('x', 'What does [[1, 2], [3, [4, 5]]].flat().length give?', '4', 'flat() goes one level deep by default.', ['One level: [1, 2, 3, [4, 5]].', 'That has 4 items.']),
    calc('x', 'What is Object.keys(Object.groupBy([1, 2, 3, 4, 5, 6], n => n % 3)).length?', '3', 'n % 3 can be 0, 1 or 2.', ['Groups: 1 and 4 under "1", 2 and 5 under "2", 3 and 6 under "0".', 'Three keys.']),
]

EX = [
    ex('pluck', 'e', 'Pluck one field', '<p>Write <code>pluck(list, key)</code> that returns an array with the value of <code>key</code> from every object.</p>',
       'function pluck(list, key) {\n  \n}\n',
       [('pluck([{ id: 1 }, { id: 2 }], "id")', [1, 2]), ('pluck([{ name: "a" }, {}], "name")', ['a', None]), ('pluck([], "x")', [])],
       'function pluck(list, key) {\n  return list.map(item => item[key] ?? null);\n}', hint='<code>map</code> with bracket notation.', why='Brackets read a key held in a variable. <code>?? null</code> keeps missing values visible in JSON.'),
    ex('sorted', 'm', 'Is it sorted', '<p>Write <code>isSorted(list, order = "asc")</code> that returns true when the numbers are in ascending (or <code>"desc"</code>) order. Equal neighbours are allowed. An empty list is sorted.</p>',
       'function isSorted(list, order = "asc") {\n  \n}\n',
       [('isSorted([1, 2, 2, 5])', True), ('isSorted([3, 1])', False), ('isSorted([9, 4, 4, 1], "desc")', True), ('isSorted([1, 2], "desc")', False), ('isSorted([])', True)],
       'function isSorted(list, order = "asc") {\n  return list.every((x, i) => i === 0 || (order === "asc" ? list[i - 1] <= x : list[i - 1] >= x));\n}',
       hint='<code>every</code> gives you the index as its second argument, so you can look at <code>list[i - 1]</code>.', why='Skipping index 0 and comparing each item with the one before covers every pair exactly once.'),
    ex('count-by', 'h', 'Count by a key', '<p>Write <code>countBy(list, key)</code> that returns an object counting how many items have each value of <code>key</code>, such as <code>{ passed: 3, failed: 1 }</code>.</p>',
       'function countBy(list, key) {\n  \n}\n',
       [('countBy([{ s: "p" }, { s: "f" }, { s: "p" }], "s")', {'p': 2, 'f': 1}), ('countBy([], "s")', {}), ('countBy([{ b: "x" }, { b: "x" }], "b")', {'x': 2})],
       'function countBy(list, key) {\n  return list.reduce((acc, item) => {\n    acc[item[key]] = (acc[item[key]] ?? 0) + 1;\n    return acc;\n  }, {});\n}',
       hint='<code>reduce</code> with <code>{}</code> as the start value.', why='The accumulator object grows one key at a time. <code>?? 0</code> handles the first time a value is seen.'),
    ex('deep-equal', 'x', 'Deep equality', '<p>Write <code>deepEqual(a, b)</code> the way <code>toEqual</code> works for plain data: primitives with <code>Object.is</code>, arrays by length and items in order, plain objects by the same keys with deeply equal values.</p>',
       'function deepEqual(a, b) {\n  return a === b;\n}\n',
       [('deepEqual({ a: [1, { b: 2 }] }, { a: [1, { b: 2 }] })', True), ('deepEqual([1, 2], [2, 1])', False), ('deepEqual({ a: 1 }, { a: 1, b: 2 })', False),
        ('deepEqual(NaN, NaN)', True), ('deepEqual({ a: undefined }, { b: undefined })', False), ('deepEqual([], {})', False), ('deepEqual(null, {})', False)],
       'function deepEqual(a, b) {\n  if (Object.is(a, b)) return true;\n  if (typeof a !== "object" || typeof b !== "object" || a === null || b === null) return false;\n  if (Array.isArray(a) !== Array.isArray(b)) return false;\n  const ka = Object.keys(a), kb = Object.keys(b);\n  if (ka.length !== kb.length) return false;\n  return ka.every(k => Object.hasOwn(b, k) && deepEqual(a[k], b[k]));\n}',
       hint='Handle primitives first, then make sure both are objects of the same kind, then compare keys and recurse.',
       why='Arrays are objects whose keys are indexes, so the same key comparison works for both once you check they are the same kind.'),
]

T = {
    'slug': 'js-objects-arrays', 'title': 'Objects and Arrays', 'short': 'Objects and arrays', 'emoji': '📦', 'module': MODULE, 'minutes': 20,
    'lead': 'Objects and their tools, destructuring, spread with shallow and deep copies, arrays, sorting without surprises, map, filter, reduce and friends, and grouping data for reports.',
    'desc': 'Objects, destructuring, spread, structuredClone, arrays, sort, toSorted, map, filter, reduce, find, some, every, Object.groupBy and array matchers.',
    'summary': 'Object literals, keys, entries and freeze, destructuring with defaults and renames, spread and the shallow copy trap, structuredClone, array basics, sorting with compare functions and the ES2023 copying methods, map, filter, reduce, find, some, every and flatMap, Object.groupBy and Sets, and checking a sorted product listing with Vitest matchers.',
    'keywords': ['object', 'array', 'destructuring', 'spread', 'structuredClone', 'deep copy', 'map', 'filter', 'reduce', 'find', 'some', 'every', 'sort', 'toSorted', 'groupBy', 'Set', 'toEqual', 'arrayContaining'],
    'qa_intro': 'UI tests read lists of element texts and API tests read nested JSON. This chapter is the toolkit for turning both into clear checks.',
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
