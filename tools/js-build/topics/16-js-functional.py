# Chapter 16: functional programming in JavaScript: pure functions, immutability, currying and composition, lazy pipelines, recursion and composable validators.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🔬', 'JavaScript in depth', 'js-depth', 'How the engine really works, errors and debugging, regular expressions, functional style, metaprogramming and Node.js in depth.')

CODES = {
    'pure': run('''
// Impure: reads the clock and changes something outside itself
let lastDiscount;
function discountImpure(total) {
  const isSale = new Date().getUTCDay() === 5;          // depends on when you run it
  lastDiscount = isSale ? total * 0.2 : 0;              // side effect
  return total - lastDiscount;
}

// Pure: the same inputs always give the same output, and nothing else changes
const discount = (total, day) => (day === 5 ? total * 0.8 : total);

console.log(discount(500, 5), discount(500, 5), discount(500, 2));

// Push the impure part to the edge and pass it in, then tests can choose the day
const todayFrom = clock => clock().getUTCDay();
const fakeFriday = () => new Date("2026-10-23T10:00:00Z");
console.log("on a Friday:", discount(500, todayFrom(fakeFriday)));
''', 'Pure functions and pushing side effects to the edge'),
    'immutable': run('''
"use strict";
const config = Object.freeze({ baseURL: "https://staging.example.test", retries: 2, users: { admin: "asha" } });

try { config.retries = 5; } catch (e) { console.log(e.constructor.name + ":", e.message.split(" of ")[0]); }
config.users.admin = "mallory";                          // freeze is shallow: nested objects still change
console.log(config.users.admin);

function deepFreeze(obj) {
  for (const value of Object.values(obj)) if (typeof value === "object" && value !== null) deepFreeze(value);
  return Object.freeze(obj);
}
const safe = deepFreeze({ users: { admin: "asha" }, tags: ["smoke"] });
try { safe.tags.push("slow"); } catch (e) { console.log("deep frozen:", e.constructor.name); }

// Immutable updates: copy the path you change, share the rest
const state = { cart: { items: [{ sku: "PEN", qty: 1 }], coupon: null }, user: { name: "Asha" } };
const next = { ...state, cart: { ...state.cart, items: state.cart.items.map(i => (i.sku === "PEN" ? { ...i, qty: i.qty + 1 } : i)) } };
console.log(state.cart.items[0].qty, next.cart.items[0].qty, "| user shared:", state.user === next.user);

const copy = structuredClone(state);                     // a full deep copy, including Dates and Maps
console.log("deep copy is separate:", copy.cart !== state.cart);
''', 'Immutability: freeze, deep freeze and copy on change'),
    'curry': run('''
// Curry: a function of many arguments becomes a chain of one argument functions
const curry = fn => function curried(...args) {
  return args.length >= fn.length ? fn.apply(this, args) : (...more) => curried.apply(this, [...args, ...more]);
};

const withinTolerance = curry((tolerance, expected, actual) => Math.abs(actual - expected) <= tolerance);
const aboutRight = withinTolerance(0.01);                // partial application: fix the tolerance
const isTotal = aboutRight(179.1);
console.log(isTotal(179.1), isTotal(179.104), isTotal(179.2), withinTolerance(1, 10, 10.5));

// Compose and pipe: build bigger functions from small ones
const compose = (...fns) => x => fns.reduceRight((v, f) => f(v), x);
const pipe = (...fns) => x => fns.reduce((v, f) => f(v), x);
const trim = s => s.trim(), lower = s => s.toLowerCase(), squash = s => s.replace(/\\s+/g, " ");
const normalise = pipe(trim, squash, lower);
console.log(JSON.stringify(normalise("   Add   TO  Cart ")), compose(lower, trim)("  OK ") === pipe(trim, lower)("  OK "));

// Point free style: pass functions without naming their arguments
const labels = ["  Login ", "CHECKOUT", " search"].map(normalise);
console.log(labels);
''', 'Currying, partial application and composition'),
    'lazy': run('''
// Eager arrays build a full new array at every step
let calls = 0;
const big = Array.from({ length: 100_000 }, (_, i) => i);
const eager = big.map(n => (calls++, n * 2)).filter(n => n % 3 === 0).slice(0, 3);
console.log(eager, "eager calls:", calls);

// Lazy iterators pull one item through all steps, and stop when they have enough
calls = 0;
const lazy = big.values().map(n => (calls++, n * 2)).filter(n => n % 3 === 0).take(3).toArray();
console.log(lazy, "lazy calls:", calls);

// reduce builds any shape: here an index by id in one pass
const products = [{ id: "p1", price: 40 }, { id: "p2", price: 250 }];
const byId = products.reduce((acc, p) => ({ ...acc, [p.id]: p }), {});
console.log(Object.keys(byId), byId.p2.price);

// flatMap maps and flattens one level, often replacing a filter then map
const orders = [{ id: 1, items: ["PEN", "INK"] }, { id: 2, items: [] }, { id: 3, items: ["BAG"] }];
console.log(orders.flatMap(o => o.items.map(sku => `${o.id}:${sku}`)));
''', 'Lazy pipelines with iterator helpers'),
    'recursion': run('''
// Walk any JSON response and collect every value under a given key, at any depth
function collect(node, key, out = []) {
  if (Array.isArray(node)) node.forEach(child => collect(child, key, out));
  else if (node && typeof node === "object")
    for (const [k, v] of Object.entries(node)) { if (k === key) out.push(v); collect(v, key, out); }
  return out;
}
const response = { id: 1, order: { id: 7, lines: [{ id: 70, sku: "PEN" }, { id: 71, sku: "INK", bundle: { id: 710 } }] } };
console.log(collect(response, "id"));

// Deep recursion can overflow the stack. A trampoline runs it in a loop instead.
const trampoline = fn => (...args) => { let r = fn(...args); while (typeof r === "function") r = r(); return r; };
const sumTo = trampoline(function sum(n, acc = 0) { return n === 0 ? acc : () => sum(n - 1, acc + n); });
console.log(sumTo(1_000_000));

// Structural equality, the core of every deepEqual assertion
const equal = (a, b) =>
  a === b || (typeof a === "object" && typeof b === "object" && a && b &&
    Object.keys(a).length === Object.keys(b).length && Object.keys(a).every(k => equal(a[k], b[k])));
console.log(equal({ a: [1, { b: 2 }] }, { a: [1, { b: 2 }] }), equal({ a: 1 }, { a: "1" }));
''', 'Recursion on trees, trampolines and deep equality'),
    'scenario': run('''
// Small checks that combine into a full API response validator
const check = (name, test) => (value, path = "$") => (test(value) ? [] : [`${path}: expected ${name}, got ${JSON.stringify(value)}`]);
const isString = check("a string", v => typeof v === "string");
const isPositive = check("a number above 0", v => typeof v === "number" && v > 0);
const matches = re => check(`text matching ${re}`, v => typeof v === "string" && re.test(v));
const oneOf = (...vals) => check(`one of ${vals.join("|")}`, v => vals.includes(v));

const shape = spec => (value, path = "$") =>
  value === null || typeof value !== "object"
    ? [`${path}: expected an object`]
    : Object.entries(spec).flatMap(([key, rule]) => rule(value[key], `${path}.${key}`));
const listOf = rule => (value, path = "$") =>
  Array.isArray(value) ? value.flatMap((item, i) => rule(item, `${path}[${i}]`)) : [`${path}: expected an array`];

const orderSchema = shape({
  id: matches(/^ORD-\\d{6}$/),
  status: oneOf("new", "paid", "shipped"),
  lines: listOf(shape({ sku: isString, qty: isPositive, price: isPositive })),
});

const good = { id: "ORD-104233", status: "paid", lines: [{ sku: "PEN", qty: 2, price: 40 }] };
const bad = { id: "104233", status: "lost", lines: [{ sku: "PEN", qty: 0, price: 40 }, { qty: 1, price: "9" }] };
console.log(orderSchema(good));
console.log(orderSchema(bad));
''', 'Composable validators for API responses'),
}

PARTS = [
    part('pure', '💧', 'Pure functions and side effects', '''
<p>A <b>pure function</b> returns the same output for the same input and changes nothing outside itself: no global variables, no network, no clock, no random numbers. Pure functions are the easiest code in the world to test, because a test is just input and expected output.</p>
[[pure]]
<p>Real programs need side effects, so the functional style keeps them at the edges. Pass the clock, the random generator or the HTTP client in as arguments, and the core logic stays pure.</p>
<div class="qa-box">If a function is hard to test, look for a hidden side effect: <code>Date.now()</code>, <code>Math.random()</code>, a global config or a direct <code>fetch</code>. Ask the developers to inject it, and the flaky test becomes a simple one.</div>
''', qa=True, qa_why='Hidden clocks and random numbers inside functions are a top cause of flaky unit tests.',
        kw=['pure function', 'side effect', 'referential transparency', 'dependency injection', 'deterministic', 'testability', 'functional programming']),
    part('immutable', '🧊', 'Immutability', '''
<p>Data that never changes cannot be broken by another part of the program. <code>const</code> only stops a variable from being reassigned. <code>Object.freeze</code> stops an object from changing, but only one level deep. For updates, build a new object that copies the path you change and shares everything else.</p>
[[immutable]]
<div class="tip">This copy on change style is how React, Redux and many state libraries know something changed: a new object means new data, so a simple <code>===</code> check is enough.</div>
''', qa=True, qa_why='Shared test data that one test changes is a classic cause of tests that pass alone and fail together.',
        kw=['immutability', 'Object.freeze', 'deep freeze', 'shallow', 'structuredClone', 'spread', 'immutable update', 'const', 'shared state']),
    part('compose', '🧩', 'Currying, partial application and composition', '''
<p><b>Currying</b> turns <code>f(a, b, c)</code> into <code>f(a)(b)(c)</code>. Fixing the first few arguments, called <b>partial application</b>, creates specialised functions from a general one. <b>Composition</b> builds a function out of smaller ones: <code>pipe</code> runs them left to right, <code>compose</code> right to left.</p>
[[curry]]
''', kw=['currying', 'curry', 'partial application', 'compose', 'pipe', 'point free', 'function arity', 'fn.length', 'higher order function']),
    part('lazy', '🦥', 'Eager and lazy collections', '''
<p>Array methods are <b>eager</b>: each step creates a full new array. Iterator helpers from ES2025 are <b>lazy</b>: they pass one item at a time through all steps and stop as soon as <code>take</code> has enough. On large data that can be thousands of times less work.</p>
[[lazy]]
''', kw=['lazy evaluation', 'eager', 'iterator helpers', 'take', 'reduce', 'flatMap', 'index by id', 'data pipeline']),
    part('recursion', '🌳', 'Recursion on real data', '''
<p>JSON responses, the DOM and file systems are trees, and recursion is the natural way to walk a tree. Very deep recursion can overflow the stack, and a <b>trampoline</b> avoids that by returning a function instead of calling it, so a loop does the calls one at a time.</p>
[[recursion]]
<div class="note">The <code>equal</code> function above is a tiny version of what <code>assert.deepStrictEqual</code>, Jest's <code>toEqual</code> and Chai's <code>deep.equal</code> do, with extra care for Dates, Maps, Sets, cycles and prototypes.</div>
''', qa=True, qa_why='Searching a nested API response for every id or every price is a frequent API test task.',
        kw=['recursion', 'tree walk', 'nested JSON', 'trampoline', 'stack overflow', 'deep equality', 'deepStrictEqual', 'toEqual']),
    part('scenario', '🎬', 'Real world scenario: a validator built from tiny functions', '''
<div class="scenario"><b>The situation</b>The API test suite needs to check the shape of order responses, and every failure must say exactly which field is wrong, such as <code>$.lines[1].sku</code>.</div>
[[scenario]]
<p>Each rule is a small pure function that returns a list of problems, and <code>shape</code> and <code>listOf</code> combine them. This is the same design that Zod, Yup, Joi and Superstruct use, and it shows why functional style suits test code: small parts, easy to combine, easy to test.</p>
''', qa=True, kw=['validator', 'schema validation', 'combinator', 'Zod', 'Joi', 'API response check', 'JSON path', 'composition']),
]

INFO = {'title': 'Small functions, combined', 'panels': [
    panel([['e', '💧'], ['t', 'f(x) is always the same', {'b': 1}]], 'Pure', 'No hidden inputs or outputs.', 'Tests are input and output.'),
    panel([['e', '🧊'], ['t', '{ ...state, cart }', {'b': 1}]], 'Immutable', 'Copy the path you change.', 'Share the rest.'),
    panel([['e', '🧩'], ['t', 'pipe(trim, lower)', {'b': 1}]], 'Composed', 'Big functions from small ones.', 'Curry to specialise.'),
    panel([['e', '🦥'], ['t', '.values().map().take(3)', {'b': 1, 'size': 11}]], 'Lazy', 'Only do the work you need.', 'Stop early.')],
    'remember': 'Keep the core pure, push effects to the edges, never change shared data, and build big checks from small functions.'}

REAL = [
    ['🧾', 'An invoicing service', 'Moved tax rules into pure functions with the date passed in. Its 600 unit tests went from flaky around midnight to stable.'],
    ['🧪', 'An API test framework', 'Builds every response check from tiny validators like those on this page, and prints the JSON path of each wrong field.'],
    ['🛒', 'A shopping cart', 'Uses copy on change updates for its state, so the UI tests can compare snapshots before and after an action with ===.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers functional programming: pure functions, immutability, currying and composition, lazy pipelines, recursion and composable validators.',
        'यह अध्याय functional programming सिखाता है: pure functions, immutability, currying और composition, lazy pipelines, recursion और validators।',
        'ಈ ಅಧ್ಯಾಯ functional programming: pure functions, immutability, currying, composition, lazy pipelines ಮತ್ತು recursion.',
        'ଏହି ଅଧ୍ୟାୟ functional programming: pure functions, immutability, currying, composition, lazy pipelines ଓ recursion।',
        'يتناول هذا الفصل البرمجة الوظيفية: الدوال النقية وعدم التغير والتجزئة والتركيب والمعالجة الكسولة والتكرار والمدققات المركبة.',
        'Dieses Kapitel behandelt funktionale Programmierung: reine Funktionen, Unveränderlichkeit, Currying, Komposition, Laziness und Rekursion.'),
    say('pure', 'Pure functions', 'A pure function gives the same output for the same input and changes nothing else. Pass the clock and random numbers in, so tests can control them.',
        'Pure function एक ही input पर एक ही output देता है और कुछ नहीं बदलता। Clock और random numbers बाहर से दें।',
        'Pure function ಒಂದೇ input ಗೆ ಒಂದೇ output ಕೊಡುತ್ತದೆ. Clock ಮತ್ತು random ಹೊರಗಿನಿಂದ ಕೊಡಿ.',
        'Pure function ସମାନ input ରେ ସମାନ output ଦିଏ। Clock ଓ random ବାହାରୁ ଦିଅନ୍ତୁ।',
        'الدالة النقية تعطي النتيجة نفسها للمدخلات نفسها ولا تغير شيئًا آخر. مرر الساعة والأرقام العشوائية من الخارج.',
        'Eine reine Funktion liefert für gleiche Eingaben gleiche Ausgaben und ändert nichts sonst. Gib Uhr und Zufall von außen hinein.'),
    say('immutable', 'Immutability', 'freeze stops changes one level deep. For updates, copy the path you change and share the rest.',
        'freeze एक level तक बदलाव रोकता है। Update के लिए बदलने वाला रास्ता copy करें और बाकी साझा करें।',
        'freeze ಒಂದು ಹಂತ ಮಾತ್ರ ತಡೆಯುತ್ತದೆ. Update ಗೆ ಬದಲಾಗುವ ಭಾಗ copy ಮಾಡಿ.',
        'freeze ଗୋଟିଏ ସ୍ତର ପର୍ଯ୍ୟନ୍ତ ଅଟକାଏ। Update ପାଇଁ ବଦଳୁଥିବା ଅଂଶ copy କରନ୍ତୁ।',
        'يمنع freeze التغيير في مستوى واحد فقط. عند التحديث انسخ المسار الذي تغيره وشارك الباقي.',
        'freeze verhindert Änderungen nur eine Ebene tief. Kopiere bei Updates nur den geänderten Pfad.'),
    say('compose', 'Composition', 'Currying turns a function of many arguments into a chain. pipe joins small functions left to right into a bigger one.',
        'Currying कई arguments वाले function को chain बनाता है। pipe छोटे functions को बाएं से दाएं जोड़ता है।',
        'Currying ಅನೇಕ arguments function ಅನ್ನು chain ಮಾಡುತ್ತದೆ. pipe ಸಣ್ಣ functions ಜೋಡಿಸುತ್ತದೆ.',
        'Currying ଅନେକ arguments function କୁ chain କରେ। pipe ଛୋଟ functions ଯୋଡ଼େ।',
        'التجزئة تحول دالة متعددة المعاملات إلى سلسلة، وتربط pipe دوال صغيرة من اليسار إلى اليمين.',
        'Currying macht aus vielen Argumenten eine Kette. pipe verbindet kleine Funktionen von links nach rechts.'),
    say('lazy', 'Lazy pipelines', 'Array methods do every step for every item. Iterator helpers pass one item at a time and stop early, which saves work on large data.',
        'Array methods हर item पर हर step करते हैं। Iterator helpers एक item पास करते हैं और जल्दी रुकते हैं।',
        'Array methods ಪ್ರತಿ item ಗೆ ಪ್ರತಿ step ಮಾಡುತ್ತವೆ. Iterator helpers ಬೇಗ ನಿಲ್ಲುತ್ತವೆ.',
        'Array methods ପ୍ରତି item ରେ ପ୍ରତି step କରେ। Iterator helpers ଶୀଘ୍ର ଅଟକେ।',
        'تنفذ دوال المصفوفات كل خطوة لكل عنصر، أما مساعدات المكررات فتمرر عنصرًا واحدًا وتتوقف مبكرًا.',
        'Array-Methoden machen jeden Schritt für jedes Element. Iterator-Helfer reichen einzeln weiter und hören früh auf.'),
    say('recursion', 'Recursion', 'JSON and the DOM are trees, so recursion walks them naturally. A trampoline avoids stack overflow for very deep recursion.',
        'JSON और DOM पेड़ हैं, इसलिए recursion उन्हें आसानी से चलता है। Trampoline गहरी recursion में stack overflow रोकता है।',
        'JSON ಮತ್ತು DOM ಮರಗಳು, recursion ಸಹಜ. Trampoline stack overflow ತಡೆಯುತ್ತದೆ.',
        'JSON ଓ DOM ଗଛ, recursion ସ୍ୱାଭାବିକ। Trampoline stack overflow ଅଟକାଏ।',
        'JSON وDOM أشجار، فالتكرار يمشي فيها بطبيعية، ويمنع الترامبولين فيض المكدس عند التكرار العميق.',
        'JSON und DOM sind Bäume, Rekursion läuft sie natürlich ab. Ein Trampolin verhindert Stack-Überläufe.'),
    say('scenario', 'Scenario', 'Tiny checks combine into a validator that reports the exact JSON path of every wrong field.',
        'छोटे checks मिलकर एक validator बनाते हैं जो हर गलत field का JSON path बताता है।',
        'ಸಣ್ಣ checks ಸೇರಿ validator ಆಗುತ್ತವೆ, ಪ್ರತಿ ತಪ್ಪು field ನ JSON path ತೋರಿಸುತ್ತದೆ.',
        'ଛୋଟ checks ମିଶି validator ହୁଏ, ପ୍ରତି ଭୁଲ field ର JSON path ଦେଖାଏ।',
        'تجتمع فحوص صغيرة في مدقق يذكر مسار JSON الدقيق لكل حقل خاطئ.',
        'Kleine Prüfungen ergeben einen Validator, der den JSON-Pfad jedes falschen Feldes nennt.'),
    say('practice', 'Hands-on', 'Practise a pipe helper, a deep freeze, an immutable cart update and a recursive key finder.',
        'pipe helper, deep freeze, immutable cart update और recursive key finder का अभ्यास करें।',
        'pipe, deep freeze, immutable cart update ಮತ್ತು recursive key finder ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'pipe, deep freeze, immutable cart update ଓ recursive key finder ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على دالة pipe والتجميد العميق وتحديث سلة دون تغيير وباحث متكرر عن المفاتيح.',
        'Übe pipe, tiefes Einfrieren, ein unveränderliches Warenkorb-Update und eine rekursive Schlüsselsuche.'),
]

QUIZ = [
    quiz('e', 'Which function is pure?', ['(a, b) => a + b', '() => Date.now()', 'x => { log.push(x) }', '() => Math.random()'], 0, 'Same input, same output.', 'The others read the clock, change outside data or are random.'),
    quiz('e', 'What does Object.freeze do to nested objects?', ['Nothing, it is shallow', 'Freezes them too', 'Deletes them', 'Copies them'], 0, 'One level.', 'Write a deepFreeze or use structuredClone for deep safety.'),
    quiz('e', 'What does pipe(f, g)(x) compute?', ['g(f(x))', 'f(g(x))', 'f(x) + g(x)', 'x'], 0, 'Left to right.', 'compose(f, g)(x) is f(g(x)).'),
    quiz('m', 'What is partial application?', ['Fixing some arguments to create a more specific function', 'Calling half a function', 'A function with no arguments', 'Skipping errors'], 0, 'Specialise.', 'withinTolerance(0.01) gives a tolerance specific check.'),
    quiz('m', 'Why are pure functions easy to test?', ['A test is just input and expected output', 'They are always fast', 'They never return', 'They have no code'], 0, 'No setup.', 'No mocks, no clocks, no network.'),
    quiz('m', 'An immutable update to state.cart.items creates new copies of which objects?', ['state, state.cart and the items array', 'Only the items array', 'Everything in state', 'Nothing'], 0, 'The changed path.', 'Unchanged branches such as state.user are shared.'),
    quiz('m', 'What does fn.length return?', ['The number of declared parameters', 'The length of the source', 'The number of calls', 'Always 0'], 0, 'Arity.', 'curry uses it to know when enough arguments have arrived.'),
    quiz('h', 'Why are iterator helpers faster than map then filter then slice on a large array with take(3)?', ['They stop once three items pass', 'They use workers', 'They skip filter', 'They are not faster'], 0, 'Lazy.', 'Eager arrays process every item at every step.'),
    quiz('h', 'What problem does a trampoline solve?', ['Stack overflow in very deep recursion', 'Slow loops', 'Async errors', 'Memory leaks'], 0, 'Return a function, loop it.', 'The stack never grows beyond one frame.'),
    quiz('h', 'Why is shared mutable test data dangerous?', ['One test can change it and break the next test', 'It uses more memory', 'It is slower', 'Tests cannot read it'], 0, 'Order dependency.', 'Give each test its own copy or freeze the shared data.'),
    quiz('x', 'In the validator scenario, why does each rule return an array instead of throwing?', ['So all problems are collected and reported together', 'Arrays are faster', 'Throwing is not allowed', 'To save memory'], 0, 'Report everything.', 'flatMap combines the lists of problems from every rule.'),
    quiz('x', 'Which pair is equal under the equal() function on this page?', ['{ a: [1, { b: 2 }] } and { a: [1, { b: 2 }] }', '{ a: 1 } and { a: "1" }', '{ a: 1 } and { a: 1, b: 2 }', '[1, 2] and [2, 1]'], 0, 'Same structure and values.', 'Strict equality is used on leaves, so 1 and "1" differ.'),
]

CALC = [
    calc('e', 'pipe(x => x + 1, x => x * 2)(3) gives?', '8', 'Left to right.', ['<span class="eq">(3 + 1) × 2 = 8</span>']),
    calc('e', 'compose(x => x + 1, x => x * 2)(3) gives?', '7', 'Right to left.', ['<span class="eq">3 × 2 + 1 = 7</span>']),
    calc('m', 'A curried function of 3 arguments is called as f(1)(2)(3). How many calls happen in total?', '3', 'One per argument.', ['f(1), then (2), then (3).']),
    calc('m', 'map then filter then slice(0, 3) on 1000 items. How many times does the map callback run?', '1000', 'Eager.', ['map runs on every item before filter starts.']),
    calc('m', 'Lazy: n => n * 2, keep multiples of 3, take 3, starting from 0. How many map calls?', '7', 'Track which pass.', ['0, 6 and 12 come from n = 0, 3 and 6.', 'n runs from 0 to 6, which is 7 calls.']),
    calc('h', 'sumTo(1000) with the trampoline returns?', '500500', 'n(n + 1) ÷ 2.', ['<span class="eq">1000 × 1001 ÷ 2 = 500,500</span>']),
    calc('h', 'How many id values does collect(response, "id") find in the recursion example?', '5', 'Count every level.', ['1, 7, 70, 71 and 710.']),
    calc('x', 'The bad order in the scenario has 2 lines. How many problems does the validator report in total?', '5', 'id, status, then each line.', ['id and status give 2.', 'Line 0 has qty 0, line 1 misses sku and has a string price.', '<span class="eq">2 + 1 + 2 = 5</span>']),
]

EX = [
    ex('pipe', 'e', 'Write pipe', '<p>Write <code>pipe(...fns)</code> that returns a function which passes its input through every function from left to right. With no functions it returns the input unchanged.</p>',
       'function pipe(...fns) {\n  \n}\n',
       [('pipe(x => x + 1, x => x * 2)(3)', 8), ('pipe()(5)', 5), ('pipe(s => s.trim(), s => s.toUpperCase())("  ok ")', 'OK')],
       'function pipe(...fns) {\n  return x => fns.reduce((value, fn) => fn(value), x);\n}', hint='<code>reduce</code> over the functions, starting with the input.', why='compose is the same with reduceRight.'),
    ex('deepfreeze', 'm', 'Deep freeze', '<p>Write <code>deepFreeze(obj)</code> that freezes the object and every nested object and array, then returns it.</p>',
       'function deepFreeze(obj) {\n  \n}\n',
       [('(() => { const o = deepFreeze({ a: { b: [1, { c: 2 }] } }); return [Object.isFrozen(o), Object.isFrozen(o.a), Object.isFrozen(o.a.b), Object.isFrozen(o.a.b[1])]; })()', [True, True, True, True]),
        ('deepFreeze({ x: null, y: 1 }).y', 1)],
       'function deepFreeze(obj) {\n  for (const value of Object.values(obj)) {\n    if (typeof value === "object" && value !== null) deepFreeze(value);\n  }\n  return Object.freeze(obj);\n}', hint='Recurse into every value that is an object, and remember <code>typeof null</code> is "object".', why='Shared fixtures frozen this way throw in strict mode the moment a test tries to change them.'),
    ex('addqty', 'h', 'An immutable cart update', '<p>Write <code>addQty(state, sku, n)</code> that returns a new state where the item with that sku has <code>qty + n</code>. Do not change the original state, and keep <code>state.user</code> as the same object.</p>',
       'function addQty(state, sku, n) {\n  \n}\n',
       [('(() => { const s = { user: { id: 1 }, cart: { items: [{ sku: "PEN", qty: 1 }, { sku: "INK", qty: 2 }] } }; const t = addQty(s, "PEN", 2); return [s.cart.items[0].qty, t.cart.items[0].qty, t.cart.items[1] === s.cart.items[1], t.user === s.user, t !== s]; })()', [1, 3, True, True, True])],
       'function addQty(state, sku, n) {\n  return {\n    ...state,\n    cart: {\n      ...state.cart,\n      items: state.cart.items.map(i => (i.sku === sku ? { ...i, qty: i.qty + n } : i)),\n    },\n  };\n}', hint='Spread each level on the path: state, cart, the items array, the one item.', why='Unchanged items stay the same objects, so a UI can skip re-rendering them.'),
    ex('findkey', 'x', 'Find every value of a key', '<p>Write <code>findAll(node, key)</code> that returns every value stored under <code>key</code> anywhere inside nested objects and arrays, in the order a depth first walk meets them.</p>',
       'function findAll(node, key) {\n  \n}\n',
       [('findAll({ id: 1, a: [{ id: 2 }, { b: { id: 3 } }] }, "id")', [1, 2, 3]), ('findAll([{ price: 5 }, [{ price: 7 }]], "price")', [5, 7]), ('findAll("text", "id")', [])],
       'function findAll(node, key) {\n  const out = [];\n  const walk = n => {\n    if (Array.isArray(n)) n.forEach(walk);\n    else if (n && typeof n === "object") {\n      for (const [k, v] of Object.entries(n)) {\n        if (k === key) out.push(v);\n        walk(v);\n      }\n    }\n  };\n  walk(node);\n  return out;\n}',
       hint='An inner <code>walk</code> function that handles arrays, objects and everything else.', why='API tests use this to check that every price in a response is positive, wherever it appears.'),
]

T = {
    'slug': 'js-functional', 'title': 'Functional programming in JavaScript', 'short': 'Functional style', 'emoji': '🧩', 'module': MODULE, 'minutes': 16,
    'lead': 'Write code that is simple to test: pure functions with side effects pushed to the edges, immutability and copy on change updates, currying, partial application and composition, lazy pipelines, recursion on real JSON trees, and an API validator built from tiny functions.',
    'desc': 'Functional JavaScript: pure functions, side effects, immutability, Object.freeze, structuredClone, currying, partial application, compose and pipe, lazy iterator helpers, reduce, recursion, trampolines and composable validators.',
    'summary': 'Pure functions and injecting the clock, freeze, deep freeze and immutable updates, curry, partial application, pipe and compose, eager arrays against lazy iterator helpers, recursion over JSON, trampolines and deep equality, and a composable validator that reports the JSON path of each wrong field.',
    'keywords': ['functional programming', 'pure function', 'side effects', 'immutability', 'Object.freeze', 'currying', 'partial application', 'compose', 'pipe', 'lazy evaluation', 'recursion', 'trampoline', 'validator', 'interview'],
    'qa_intro': 'Functional habits make code testable and test code reliable: inject the clock, never change shared fixtures, and build checks from small reusable functions.',
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
