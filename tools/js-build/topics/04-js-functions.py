# Chapter 4: functions, parameters, arrows, scope, hoisting, closures, this, higher order functions and recursion.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🌱', 'Foundations', 'js-foundations', 'From your first program to functions and closures. Developers and testers both start here.')

CODES = {
    'declare': run('''
function add(a, b) {
  return a + b;
}
console.log(add(2, 3));
console.log(add(2));          // missing arguments are undefined
console.log(add(2, 3, 99));   // extra arguments are ignored

function logIn(user, password = "Secret12", remember = false) {
  return `${user} / ${password} / remember=${remember}`;
}
console.log(logIn("asha"));
console.log(logIn("ravi", undefined, true));   // undefined uses the default
console.log(logIn("mei", null));               // null does not
''', 'Declaring and calling functions'),
    'rest-spread': run('''
function total(label, ...prices) {     // rest: gathers the remaining arguments into an array
  const sum = prices.reduce((s, p) => s + p, 0);
  return `${label}: ${sum}`;
}
console.log(total("cart", 100, 250, 75));

const prices = [10, 20, 30];
console.log(Math.max(...prices));       // spread: spreads an array into arguments
console.log(total("again", ...prices, 40));

function createUser({ name, role = "viewer", active = true } = {}) {   // destructured options
  return { name, role, active };
}
console.log(createUser({ name: "Asha", role: "admin" }));
console.log(createUser());
''', 'Rest parameters, spread and options objects'),
    'arrows': run('''
const square = function (n) { return n * n; };   // function expression
const cube = n => n * n * n;                       // arrow, one parameter, implicit return
const greet = (first, last) => `Hi ${first} ${last}`;
const makeUser = name => ({ name, createdAt: "today" });   // wrap an object in ( )
const log = () => { console.log("no parameters, a block body"); };

console.log(square(4), cube(3));
console.log(greet("Asha", "Rao"));
console.log(makeUser("Ravi"));
log();
''', 'Function expressions and arrow functions'),
    'scope': run('''
const appName = "Shop";                 // global scope

function checkout() {
  const total = 499;                    // function scope
  if (total > 100) {
    const message = "big order";        // block scope
    console.log(appName, total, message);
  }
  console.log(typeof message);          // not visible outside its block
}
checkout();
console.log(typeof total);              // not visible outside the function

let level = "global";
function shadow() {
  let level = "inside";                 // a new variable that hides the outer one
  console.log(level);
}
shadow();
console.log(level);
''', 'Global, function and block scope'),
    'hoisting': run('''
console.log(sayHi());               // function declarations are hoisted: this works
function sayHi() { return "hi"; }

console.log(typeof oldStyle);       // var is hoisted but undefined
var oldStyle = 1;

try {
  console.log(modern);             // let and const are in the "temporal dead zone"
} catch (err) {
  console.log(err.name + ": " + err.message);
}
let modern = 2;
''', 'Hoisting and the temporal dead zone', file='hoist.cjs'),
    'closure': run('''
function makeCounter(start = 0) {
  let count = start;               // private: only the inner functions can see it
  return {
    next: () => ++count,
    reset: () => { count = start; },
    get value() { return count; },
  };
}

const visits = makeCounter();
const retries = makeCounter(10);
visits.next(); visits.next();
retries.next();
console.log(visits.value, retries.value);
visits.reset();
console.log(visits.value);
console.log(visits.count);         // there is no way to reach the variable directly
''', 'A closure keeps its variables alive'),
    'loop-closure': run('''
const viaVar = [];
for (var i = 0; i < 3; i++) viaVar.push(() => i);
console.log(viaVar.map(f => f()));    // one shared i, already 3

const viaLet = [];
for (let j = 0; j < 3; j++) viaLet.push(() => j);
console.log(viaLet.map(f => f()));    // let makes a new j for every turn
''', 'The classic loop closure bug', file='loop.cjs'),
    'this': run('''
const cart = {
  owner: "Asha",
  items: ["pen", "book"],
  describe() {
    return `${this.owner} has ${this.items.length} items`;    // this is the object before the dot
  },
  describeLater() {
    return this.items.map(item => `${this.owner}: ${item}`);  // arrows use the outer this
  },
};
console.log(cart.describe());
console.log(cart.describeLater());

const loose = cart.describe;          // the method is taken off the object
try {
  console.log(loose());               // no object before the dot, so this is undefined
} catch (err) {
  console.log(err.message);
}

const bound = cart.describe.bind(cart);
console.log(bound());
console.log(cart.describe.call({ owner: "Ravi", items: [1, 2, 3] }));
''', 'How this is decided'),
    'mocha-this': test({
        'package.json': pkg('mocha-this', None, {'test': 'mocha'}),
        'slow.test.js': '''
const assert = require("node:assert");

describe("report export", () => {
  it("can raise its own timeout with a normal function", function () {
    this.timeout(5000);          // Mocha passes its context as this
    assert.ok(true);
  });

  it("cannot do the same in an arrow function", () => {
    this.timeout(5000);          // this comes from the arrow describe: the module, not Mocha
  });
});
''',
    }, 'npx mocha slow.test.js', 'Mocha needs function, not arrows, to use this', expect='fail',
        replace=[(r'\(\d+ms\)', ''), (r'\d+ms\)', ')')]),
    'hof': run('''
// Functions are values: store them, pass them, return them.
const rules = {
  required: v => v !== "" || "is required",
  email: v => /^[^@\\s]+@[^@\\s]+\\.\\w+$/.test(v) || "must be an email",
  min: n => v => v.length >= n || `must be at least ${n} characters`,   // returns a function
};

function validate(value, ...checks) {
  const errors = [];
  for (const check of checks) {
    const result = check(value);
    if (result !== true) errors.push(result);
  }
  return errors;
}

console.log(validate("asha@example.com", rules.required, rules.email));
console.log(validate("ab", rules.required, rules.email, rules.min(3)));
console.log(validate("", rules.required));
''', 'Higher order functions'),
    'memo': run('''
function memoize(fn) {
  const cache = new Map();
  return arg => {
    if (!cache.has(arg)) cache.set(arg, fn(arg));
    return cache.get(arg);
  };
}

let calls = 0;
const slowSquare = n => { calls++; return n * n; };
const fastSquare = memoize(slowSquare);
console.log(fastSquare(9), fastSquare(9), fastSquare(4), fastSquare(9));
console.log("real calls:", calls);

function debounce(fn, wait) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), wait);
  };
}
const search = debounce(text => console.log("searching for", text), 30);
search("p"); search("ph"); search("pho"); search("phone");   // typed quickly
''', 'Memoize and debounce, two closures you will meet'),
    'recursion': run('''
function factorial(n) {
  if (n <= 1) return 1;          // base case: stops the recursion
  return n * factorial(n - 1);   // recursive case: a smaller problem
}
console.log(factorial(5));

// Recursion fits nested data, such as a site menu
const menu = { label: "Home", children: [
  { label: "Shop", children: [{ label: "Phones" }, { label: "Laptops", children: [{ label: "Gaming" }] }] },
  { label: "Help" },
] };

function allLabels(node, depth = 0) {
  const lines = ["  ".repeat(depth) + node.label];
  for (const child of node.children ?? []) lines.push(...allLabels(child, depth + 1));
  return lines;
}
console.log(allLabels(menu).join("\\n"));

function forever(n) { return forever(n + 1); }   // no base case
try { forever(0); } catch (err) { console.log(err.name + ": " + err.message); }
''', 'Recursion and the call stack'),
    'scenario': run('''
// A test data builder: unique, valid data by default, overridable when a test needs something special.
function userFactory(prefix = "qa") {
  let seq = 0;                                  // private counter, kept by the closure
  return function build(overrides = {}) {
    seq++;
    return {
      id: seq,
      name: `Test User ${seq}`,
      email: `${prefix}.user${seq}@example.com`,
      role: "customer",
      verified: true,
      ...overrides,                             // the test's own values win
    };
  };
}

const buildUser = userFactory("checkout");
const normal = buildUser();
const admin = buildUser({ role: "admin" });
const unverified = buildUser({ verified: false, email: "not-an-email" });
console.table([normal, admin, unverified]);

const other = userFactory("search")();          // a separate counter for another suite
console.log(other.email);
''', 'A test data factory built on a closure'),
}

PARTS = [
    part('functions', '🧩', 'Declaring functions', '''
<p>A <b>function</b> is a named, reusable piece of code. It takes <b>parameters</b>, does some work and <b>returns</b> a value. A function without a <code>return</code> returns <code>undefined</code>.</p>
[[declare]]
<ul>
<li>JavaScript does not check how many arguments you pass. Missing ones are <code>undefined</code> and extra ones are ignored.</li>
<li><b>Default values</b> replace <code>undefined</code> only. Passing <code>null</code> keeps <code>null</code>.</li>
</ul>
<h3>Rest, spread and options objects</h3>
[[rest-spread]]
<div class="tip">When a function has more than two or three parameters, take one <b>options object</b> and destructure it. Calls read like labels (<code>launch({ headless: true, slowMo: 50 })</code>) and the order stops mattering. Playwright, Cypress and Jest all configure this way.</div>
''', kw=['function', 'parameter', 'argument', 'return', 'default parameter', 'rest parameter', 'spread', 'options object', 'destructuring parameters']),
    part('arrows', '🏹', 'Function expressions and arrow functions', '''
<p>A function can also be written as an <b>expression</b> and stored in a variable. The shorter <b>arrow function</b> syntax is the most common form in modern code and in test files.</p>
[[arrows]]
<div class="tw"><table class="jt"><tr><th>Form</th><th>Notes</th></tr>
<tr><td><code>function name() {}</code></td><td>Hoisted, so it can be called before its line. Has its own <code>this</code>.</td></tr>
<tr><td><code>const f = function () {}</code></td><td>Not hoisted. Has its own <code>this</code>.</td></tr>
<tr><td><code>const f = () =&gt; {}</code></td><td>Not hoisted. No own <code>this</code> or <code>arguments</code>: it uses the ones around it. Cannot be called with <code>new</code>.</td></tr>
</table></div>
<div class="qa-box">Test files are mostly arrow functions: <code>test("adds to cart", async ({ page }) =&gt; { ... })</code>. The exceptions are Mocha and Cypress code that uses <code>this</code>, covered below.</div>
''', qa=['Playwright', 'Jest', 'Cypress'], kw=['function expression', 'arrow function', 'implicit return', 'anonymous function', 'callback']),
    part('scope', '🔭', 'Scope, hoisting and the temporal dead zone', '''
<p><b>Scope</b> decides where a name can be seen. JavaScript looks for a name in the current block, then in each enclosing block and function, out to the global scope. This chain is fixed by where the code is <b>written</b>, which is called lexical scope.</p>
<div class="viz" data-viz="lanes" data-k="scope"></div>
[[scope]]
<h3>Hoisting</h3>
<p>Before running a scope, the engine registers its declarations. Function declarations are ready at once. <code>var</code> exists but is <code>undefined</code>. <code>let</code> and <code>const</code> exist but cannot be touched until their line runs. That gap is the <b>temporal dead zone</b>.</p>
[[hoisting]]
<div class="rule">Declare variables at the top of the block where you need them, with <code>const</code> or <code>let</code>. Then hoisting never surprises you.</div>
''', kw=['scope', 'lexical scope', 'block scope', 'function scope', 'global scope', 'shadowing', 'hoisting', 'temporal dead zone', 'TDZ', 'scope chain']),
    part('closures', '🎒', 'Closures', '''
<p>A <b>closure</b> is a function together with the variables it could see when it was created. Those variables stay alive as long as the function does, even after the outer function has returned. Closures give you private state without classes.</p>
<div class="viz" data-viz="lanes" data-k="closure"></div>
[[closure]]
<p>Each call to <code>makeCounter</code> creates a fresh <code>count</code>, so <code>visits</code> and <code>retries</code> never interfere.</p>
[[loop-closure]]
<div class="exam">With <code>var</code>, every function created in the loop shares one variable, which has its final value by the time they run. <code>let</code> creates a new binding for each turn. This was a famous interview question before <code>let</code> existed.</div>
<div class="qa-box">Closures are everywhere in test code: a <code>let page</code> declared in a <code>describe</code> block and set in <code>beforeEach</code> is captured by every test inside. Test data factories, custom wait helpers and Page Object methods all rely on them.</div>
''', qa=['Jest', 'Mocha', 'Playwright'], kw=['closure', 'private state', 'factory function', 'counter', 'loop closure', 'var in loop', 'encapsulation']),
    part('this', '👉', 'this, call, apply and bind', '''
<p><code>this</code> is decided by <b>how</b> a function is called, not where it is written. Arrow functions are the exception: they never get their own <code>this</code> and use the one from the surrounding code.</p>
<div class="tw"><table class="jt"><tr><th>Call</th><th>this is</th></tr>
<tr><td><code>obj.method()</code></td><td><code>obj</code>, the object before the dot</td></tr>
<tr><td><code>fn()</code></td><td><code>undefined</code> in strict code (the global object in old sloppy code)</td></tr>
<tr><td><code>fn.call(x, a, b)</code>, <code>fn.apply(x, [a, b])</code></td><td><code>x</code>, chosen by you for this one call</td></tr>
<tr><td><code>fn.bind(x)</code></td><td>a new function where this is always <code>x</code></td></tr>
<tr><td><code>new Fn()</code></td><td>the new object being created</td></tr>
<tr><td>arrow function</td><td>whatever this was where the arrow was written</td></tr>
</table></div>
[[this]]
<h3>Why test runners care</h3>
<p>Mocha puts helpers such as <code>this.timeout()</code> and <code>this.retries()</code> on the test's <code>this</code>. Cypress stores aliases on it too (<code>this.user</code> after <code>cy.wrap(user).as("user")</code>). Both only work when the test is a normal <code>function</code>. An arrow test borrows <code>this</code> from the code around it, and below, where <code>describe</code> is an arrow too, that is the module and not Mocha.</p>
[[mocha-this]]
<div class="rule">If a Mocha or Cypress test uses <code>this</code>, write both the <code>describe</code> and the test with <code>function</code>. Everywhere else, arrows are fine.</div>
''', qa=['Mocha', 'Cypress'], qa_why='Mocha this.timeout and Cypress aliases on this only work inside function, not arrow functions.',
        kw=['this', 'call', 'apply', 'bind', 'method', 'arrow function this', 'lost this', 'Mocha this.timeout', 'Cypress alias this']),
    part('higher-order', '🧠', 'Higher order functions', '''
<p>A <b>higher order function</b> takes a function as an argument or returns one. You already used one: <code>array.map(fn)</code>. They let you write the shape of a task once and plug in the details.</p>
[[hof]]
<p><code>rules.min(3)</code> returns a new function that remembers <code>3</code>. Returning configured functions like this is the basis of matchers, middleware and plugins.</p>
[[memo]]
<ul>
<li><b>memoize</b> remembers results so a slow, pure function runs once per input.</li>
<li><b>debounce</b> waits until calls stop for a while, then runs once. Search boxes use it so the server gets one request instead of one per key press.</li>
</ul>
<div class="qa-box">Debounced inputs explain a classic test failure: the test types "phone" and checks the results at once, before the debounce timer fires. Assert on the results with an auto-waiting check (<code>await expect(list).toHaveCount(3)</code>) instead of reading them immediately.</div>
''', qa=['Playwright', 'Cypress'], kw=['higher order function', 'callback', 'function returning function', 'currying', 'memoize', 'debounce', 'throttle', 'validation rules']),
    part('recursion', '🪆', 'Recursion and the call stack', '''
<p>A <b>recursive</b> function calls itself on a smaller piece of the problem. It needs a <b>base case</b> that stops the calls. Every call waits on the <b>call stack</b> until the one it made returns.</p>
<div class="viz" data-viz="lanes" data-k="stack"></div>
[[recursion]]
<p>Recursion is natural for nested data: menus, folder trees, JSON with nested objects, the DOM itself. Without a base case, the stack fills up and you get <code>RangeError: Maximum call stack size exceeded</code>.</p>
''', kw=['recursion', 'base case', 'call stack', 'stack overflow', 'Maximum call stack size exceeded', 'factorial', 'tree walk', 'nested data']),
    part('scenario', '🎬', 'Real world scenario: a test data factory', '''
<div class="scenario"><b>The situation</b>Your sign up tests keep failing with "email already registered" because every test uses <code>test@example.com</code>. You need valid, unique users by default, and an easy way for one test to ask for an admin or an unverified user.</div>
[[scenario]]
<ul>
<li>The closure keeps a private <code>seq</code> counter per factory, so emails never repeat within a run.</li>
<li>The object spread <code>...overrides</code> lets each test change only what it cares about. The test reads as "a user, but unverified".</li>
<li>Separate factories have separate counters, so suites do not depend on each other.</li>
</ul>
<div class="dev-box">The same pattern builds fixtures for unit tests of the app code itself. Libraries such as Fishery and @faker-js/faker grow it further with realistic random values.</div>
''', qa=True, kw=['test data factory', 'builder pattern', 'unique email', 'overrides', 'fixtures', 'faker']),
]

LANES = {
    'scope': {'t': 'Looking up a name through the scope chain', 'code': 'const app = "Shop";\nfunction checkout() {\n  const total = 499;\n  if (total > 100) {\n    const msg = "big";\n    console.log(app, total, msg);\n  }\n}\ncheckout();',
              'lanes': ['Global scope', 'checkout() scope', 'if block scope', 'Lookup'], 'tone': [2, 1, 0, 5],
              'steps': [{'l': 1, 'v': [['app = "Shop"', 'checkout = fn'], [], [], []], 'm': 'The global scope holds app and the checkout function.'},
                        {'l': 9, 'v': [['app = "Shop"', 'checkout = fn'], ['(new scope)'], [], []], 'm': 'Calling checkout creates a new scope for that call.'},
                        {'l': 3, 'v': [['app = "Shop"', 'checkout = fn'], ['total = 499'], [], []], 'm': 'total belongs to the function scope.'},
                        {'l': 5, 'v': [['app = "Shop"', 'checkout = fn'], ['total = 499'], ['msg = "big"'], []], 'm': 'msg is declared with const inside the if block, so it gets an even smaller scope.'},
                        {'l': 6, 'v': [['app = "Shop"', 'checkout = fn'], ['total = 499'], ['msg = "big"'], ['msg: found in the block']], 'm': 'Looking up msg: found at once in the block.'},
                        {'l': 6, 'v': [['app = "Shop"', 'checkout = fn'], ['total = 499'], ['msg = "big"'], ['msg: found in the block', 'total: not in block, found in function']], 'm': 'total is not in the block, so the search moves one scope out.'},
                        {'l': 6, 'v': [['app = "Shop"', 'checkout = fn'], ['total = 499'], ['msg = "big"'], ['msg: found in the block', 'total: not in block, found in function', 'app: found in global']], 'm': 'app is found two scopes out, in the global scope. The search only goes outwards, never inwards.'},
                        {'l': 8, 'v': [['app = "Shop"', 'checkout = fn'], [], [], []], 'm': 'When the call ends, its scopes are gone, unless a closure still needs them.'}]},
    'closure': {'t': 'A closure keeps its variables alive', 'code': 'function makeCounter() {\n  let count = 0;\n  return () => ++count;\n}\nconst next = makeCounter();\nnext();\nnext();',
                'lanes': ['Global', 'Kept alive by the closure', 'Returned values'], 'tone': [2, 3, 1],
                'steps': [{'l': 5, 'v': [['makeCounter = fn'], ['count = 0'], []], 'm': 'Calling makeCounter creates count inside its scope.'},
                          {'l': 3, 'v': [['makeCounter = fn', 'next = arrow fn'], ['count = 0'], []], 'm': 'The arrow function is returned. makeCounter has finished, yet count is kept because the arrow still refers to it.'},
                          {'l': 6, 'v': [['makeCounter = fn', 'next = arrow fn'], ['count = 1'], ['1']], 'm': 'next() reaches into the kept scope and adds one.'},
                          {'l': 7, 'v': [['makeCounter = fn', 'next = arrow fn'], ['count = 2'], ['1', '2']], 'm': 'The value survives between calls. Nothing outside can touch count directly.'}]},
    'stack': {'t': 'factorial(3) on the call stack', 'code': 'function factorial(n) {\n  if (n <= 1) return 1;\n  return n * factorial(n - 1);\n}\nfactorial(3);',
              'lanes': ['Call stack (top is running)', 'Returned'], 'tone': [0, 1],
              'steps': [{'l': 5, 'v': [['factorial(3)'], []], 'm': 'factorial(3) starts and is placed on the stack.'},
                        {'l': 3, 'v': [['factorial(2)', 'factorial(3) waits'], []], 'm': 'It needs factorial(2), which goes on top. factorial(3) waits.'},
                        {'l': 3, 'v': [['factorial(1)', 'factorial(2) waits', 'factorial(3) waits'], []], 'm': 'factorial(2) needs factorial(1).'},
                        {'l': 2, 'v': [['factorial(2) waits', 'factorial(3) waits'], ['factorial(1) = 1']], 'm': 'The base case returns 1 without another call. Its frame leaves the stack.'},
                        {'l': 3, 'v': [['factorial(3) waits'], ['factorial(1) = 1', 'factorial(2) = 2']], 'm': 'factorial(2) can finish: 2 × 1 = 2.'},
                        {'l': 3, 'v': [[], ['factorial(1) = 1', 'factorial(2) = 2', 'factorial(3) = 6']], 'm': 'factorial(3) finishes: 3 × 2 = 6. The stack is empty again.'}]},
}

INFO = {'title': 'Functions in four pictures', 'panels': [
    panel([['e', '🧩'], ['t', 'add(2, 3) → 5', {'b': 1}]], 'Input to output', 'A function takes arguments and returns a value.', 'Defaults fill in missing arguments. Rest collects extra ones into an array.'),
    panel([['e', '🔭'], ['t', 'block → function → global', {'b': 1}]], 'Scope', 'Names are looked up from the inside out.', 'Where the code is written decides what it can see.'),
    panel([['e', '🎒'], ['t', 'count stays alive', {'b': 1}]], 'Closures', 'An inner function keeps the variables it saw.', 'This gives private state and fresh counters per call.'),
    panel([['e', '👉'], ['t', 'obj.method() → this = obj', {'b': 1}]], 'this', 'this depends on how the function is called.', 'Arrows borrow this from outside. Mocha needs function to use this.timeout.')],
    'remember': 'Small pure functions are the easiest code in the world to test.'}

REAL = [
    ['🔎', 'Search as you type', 'An online shop debounces the search box, so typing "phone" sends one request instead of five.'],
    ['🧾', 'Form validation', 'A sign up page builds its rules from small functions such as required, email and min(8), and runs them as a list.'],
    ['🗂️', 'Nested categories', 'A recursive function renders a category tree of any depth in an e-commerce menu.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers functions, arrows, scope, closures, this, higher order functions and recursion.',
        'यह अध्याय functions, arrows, scope, closures, this, higher order functions और recursion सिखाता है।',
        'ಈ ಅಧ್ಯಾಯ functions, arrows, scope, closures, this, higher order functions ಮತ್ತು recursion ಕಲಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ functions, arrows, scope, closures, this, higher order functions ଓ recursion ଶିଖାଏ।',
        'يتناول هذا الفصل الدوال والدوال السهمية والنطاق والإغلاقات وthis والدوال عالية الرتبة والاستدعاء الذاتي.',
        'Dieses Kapitel behandelt Funktionen, Pfeilfunktionen, Gültigkeitsbereiche, Closures, this, Funktionen höherer Ordnung und Rekursion.'),
    say('functions', 'Functions', 'A function takes parameters and returns a value. Defaults fill in undefined arguments, rest gathers extra ones, and an options object keeps calls readable.',
        'Function parameters लेता है और value लौटाता है। Defaults undefined arguments भरते हैं, rest बाकी इकट्ठा करता है, और options object calls को पढ़ने लायक रखता है।',
        'Function parameters ತೆಗೆದು value ಹಿಂದಿರುಗಿಸುತ್ತದೆ. Defaults undefined arguments ತುಂಬುತ್ತವೆ, rest ಹೆಚ್ಚುವರಿಗಳನ್ನು ಸಂಗ್ರಹಿಸುತ್ತದೆ.',
        'Function parameters ନେଇ value ଫେରାଏ। Defaults undefined arguments ପୂରଣ କରେ, rest ଅତିରିକ୍ତ ଗୁଡ଼ିକ ସଂଗ୍ରହ କରେ।',
        'تأخذ الدالة معاملات وتعيد قيمة. القيم الافتراضية تملأ الوسائط غير المعرفة، وrest يجمع الزائد، وكائن الخيارات يجعل الاستدعاء واضحًا.',
        'Eine Funktion nimmt Parameter und gibt einen Wert zurück. Standardwerte füllen fehlende Argumente, Rest sammelt zusätzliche, ein Optionsobjekt hält Aufrufe lesbar.'),
    say('arrows', 'Arrows', 'Arrow functions are short and use the this of the code around them. They are the usual form in test files.',
        'Arrow functions छोटे होते हैं और आसपास के code का this इस्तेमाल करते हैं। Test files में यही आम रूप है।',
        'Arrow functions ಚಿಕ್ಕವು ಮತ್ತು ಸುತ್ತಲಿನ code ನ this ಬಳಸುತ್ತವೆ. Test files ನಲ್ಲಿ ಇದೇ ಸಾಮಾನ್ಯ ರೂಪ.',
        'Arrow functions ଛୋଟ ଏବଂ ଚାରିପାଖ code ର this ବ୍ୟବହାର କରନ୍ତି। Test files ରେ ଏହା ସାଧାରଣ ରୂପ।',
        'الدوال السهمية قصيرة وتستخدم this الخاص بالكود المحيط. وهي الشكل المعتاد في ملفات الاختبار.',
        'Pfeilfunktionen sind kurz und nutzen das this des umgebenden Codes. In Testdateien sind sie die übliche Form.'),
    say('scope', 'Scope', 'Names are looked up from the current block outwards to the global scope. let and const cannot be used before their line, which is the temporal dead zone.',
        'Names current block से बाहर global scope तक खोजे जाते हैं। let और const अपनी line से पहले इस्तेमाल नहीं हो सकते, यही temporal dead zone है।',
        'Names ಈಗಿನ block ನಿಂದ ಹೊರಗೆ global scope ವರೆಗೆ ಹುಡುಕಲಾಗುತ್ತದೆ. let ಮತ್ತು const ತಮ್ಮ ಸಾಲಿಗೆ ಮೊದಲು ಬಳಸಲಾಗದು.',
        'Names ବର୍ତ୍ତମାନ block ରୁ ବାହାରକୁ global scope ପର୍ଯ୍ୟନ୍ତ ଖୋଜାଯାଏ। let ଓ const ନିଜ ଧାଡ଼ି ପୂର୍ବରୁ ବ୍ୟବହାର ହୋଇପାରେ ନାହିଁ।',
        'يُبحث عن الأسماء من الكتلة الحالية إلى الخارج حتى النطاق العام. لا يمكن استخدام let وconst قبل سطرها، وهذه هي المنطقة الميتة المؤقتة.',
        'Namen werden vom aktuellen Block nach außen bis zum globalen Bereich gesucht. let und const sind vor ihrer Zeile nicht nutzbar, das ist die Temporal Dead Zone.'),
    say('closures', 'Closures', 'A closure is a function that keeps the variables it saw when it was created. Each call to a factory gets its own fresh copy.',
        'Closure वह function है जो बनते समय दिखे variables को साथ रखता है। Factory की हर call को अपनी नई copy मिलती है।',
        'Closure ಎಂದರೆ ತಾನು ರಚನೆಯಾದಾಗ ನೋಡಿದ variables ಅನ್ನು ಇಟ್ಟುಕೊಳ್ಳುವ function. Factory ಯ ಪ್ರತಿ call ಗೆ ಹೊಸ copy.',
        'Closure ହେଉଛି ସେହି function ଯାହା ତିଆରି ବେଳେ ଦେଖିଥିବା variables ରଖେ। Factory ର ପ୍ରତ୍ୟେକ call ନୂଆ copy ପାଏ।',
        'الإغلاق دالة تحتفظ بالمتغيرات التي رأتها عند إنشائها. كل استدعاء للمصنع يحصل على نسخته الجديدة.',
        'Eine Closure ist eine Funktion, die die Variablen behält, die sie bei ihrer Erstellung sah. Jeder Aufruf einer Fabrik bekommt eine frische Kopie.'),
    say('this', 'this', 'this is decided by how a function is called. Arrow functions borrow it from outside, so Mocha this timeout only works in a normal function.',
        'this इस बात से तय होता है कि function कैसे call हुआ। Arrow functions इसे बाहर से लेते हैं, इसलिए Mocha का this.timeout सिर्फ normal function में चलता है।',
        'Function ಹೇಗೆ call ಆಯಿತು ಎಂಬುದರಿಂದ this ನಿರ್ಧಾರವಾಗುತ್ತದೆ. Arrow functions ಹೊರಗಿನಿಂದ ಪಡೆಯುತ್ತವೆ, ಹಾಗಾಗಿ Mocha this.timeout normal function ನಲ್ಲಿ ಮಾತ್ರ.',
        'Function କିପରି call ହେଲା ତାହା this ସ୍ଥିର କରେ। Arrow functions ବାହାରୁ ନିଅନ୍ତି, ତେଣୁ Mocha this.timeout କେବଳ normal function ରେ ଚାଲେ।',
        'تحدد طريقة استدعاء الدالة قيمة this. الدوال السهمية تستعيرها من الخارج، لذلك يعمل this.timeout في Mocha فقط داخل دالة عادية.',
        'this hängt davon ab, wie eine Funktion aufgerufen wird. Pfeilfunktionen leihen es von außen, daher funktioniert this.timeout in Mocha nur in normalen Funktionen.'),
    say('higher-order', 'Higher order functions', 'Functions can take and return functions. Memoize remembers results and debounce waits until calls stop, which tests must wait for too.',
        'Functions दूसरे functions ले और लौटा सकते हैं। Memoize नतीजे याद रखता है और debounce calls रुकने तक रुकता है, जिसका tests को भी इंतज़ार करना होता है।',
        'Functions ಇತರ functions ತೆಗೆದು ಹಿಂದಿರುಗಿಸಬಹುದು. Memoize ಫಲಿತಾಂಶ ನೆನಪಿಡುತ್ತದೆ, debounce calls ನಿಲ್ಲುವವರೆಗೆ ಕಾಯುತ್ತದೆ.',
        'Functions ଅନ୍ୟ functions ନେଇ ଫେରାଇପାରନ୍ତି। Memoize ଫଳାଫଳ ମନେ ରଖେ, debounce calls ବନ୍ଦ ହେବା ପର୍ଯ୍ୟନ୍ତ ଅପେକ୍ଷା କରେ।',
        'يمكن للدوال أن تأخذ دوالًا وتعيدها. memoize يتذكر النتائج وdebounce ينتظر حتى تتوقف الاستدعاءات، وعلى الاختبارات أن تنتظر أيضًا.',
        'Funktionen können Funktionen annehmen und zurückgeben. Memoize merkt sich Ergebnisse, Debounce wartet, bis Aufrufe aufhören, und Tests müssen ebenfalls warten.'),
    say('recursion', 'Recursion', 'A recursive function calls itself on a smaller problem and needs a base case. Each call waits on the call stack.',
        'Recursive function छोटे problem पर खुद को call करता है और उसे base case चाहिए। हर call call stack पर इंतज़ार करती है।',
        'Recursive function ಚಿಕ್ಕ problem ಮೇಲೆ ತನ್ನನ್ನೇ call ಮಾಡುತ್ತದೆ, base case ಬೇಕು. ಪ್ರತಿ call call stack ಮೇಲೆ ಕಾಯುತ್ತದೆ.',
        'Recursive function ଛୋଟ problem ଉପରେ ନିଜକୁ call କରେ ଏବଂ base case ଦରକାର। ପ୍ରତ୍ୟେକ call call stack ରେ ଅପେକ୍ଷା କରେ।',
        'الدالة الذاتية تستدعي نفسها على مشكلة أصغر وتحتاج إلى حالة أساس. كل استدعاء ينتظر على مكدس الاستدعاءات.',
        'Eine rekursive Funktion ruft sich mit einem kleineren Problem selbst auf und braucht einen Basisfall. Jeder Aufruf wartet auf dem Aufrufstapel.'),
    say('scenario', 'Scenario', 'A closure based factory builds unique, valid test users by default and lets each test override only what it needs.',
        'Closure पर बनी factory default रूप से unique, valid test users बनाती है और हर test को सिर्फ ज़रूरी चीज़ बदलने देती है।',
        'Closure ಆಧಾರಿತ factory default ಆಗಿ unique, valid test users ರಚಿಸುತ್ತದೆ, ಪ್ರತಿ test ಬೇಕಾದದ್ದನ್ನು ಮಾತ್ರ ಬದಲಿಸಬಹುದು.',
        'Closure ଆଧାରିତ factory default ଭାବେ unique, valid test users ତିଆରି କରେ ଏବଂ ପ୍ରତ୍ୟେକ test କେବଳ ଦରକାରୀ ବଦଳାଏ।',
        'مصنع مبني على الإغلاق ينشئ مستخدمي اختبار فريدين وصالحين افتراضيًا، ويسمح لكل اختبار بتغيير ما يحتاجه فقط.',
        'Eine Fabrik auf Basis einer Closure baut standardmäßig eindeutige, gültige Testnutzer, und jeder Test ändert nur, was er braucht.'),
    say('practice', 'Hands-on', 'Write functions with defaults, closures and wrappers, then run the tests in your browser.',
        'Defaults, closures और wrappers वाले functions लिखें, फिर tests अपने browser में चलाएँ।',
        'Defaults, closures ಮತ್ತು wrappers ಇರುವ functions ಬರೆಯಿರಿ, ನಂತರ tests ನಿಮ್ಮ browser ನಲ್ಲಿ ಓಡಿಸಿ.',
        'Defaults, closures ଓ wrappers ଥିବା functions ଲେଖନ୍ତୁ, ତାପରେ tests ଆପଣଙ୍କ browser ରେ ଚଲାନ୍ତୁ।',
        'اكتب دوالًا بقيم افتراضية وإغلاقات وأغلفة، ثم شغل الاختبارات في متصفحك.',
        'Schreibe Funktionen mit Standardwerten, Closures und Hüllen und führe die Tests im Browser aus.'),
]

QUIZ = [
    quiz('e', 'What does a function without a return statement return?', ['undefined', 'null', '0', 'The last value it computed'], 0, 'Nothing was given back.', 'Without <code>return</code>, a call gives <code>undefined</code>.'),
    quiz('e', 'What does this arrow return?', ['{ id: 1 }', 'undefined', 'A SyntaxError', '1'], 0, 'The object is wrapped in parentheses.', 'Parentheses make the braces an object, so it is returned.', code='const make = () => ({ id: 1 });\nconsole.log(make());'),
    quiz('e', 'What does ...nums do in function sum(...nums)?', ['Collects all arguments into an array', 'Spreads an array into arguments', 'Makes nums optional', 'Copies nums'], 0, 'In a parameter list it gathers.', 'In a parameter list, <code>...</code> is a rest parameter and gathers the arguments into a real array.'),
    quiz('m', 'What does this print?', ['3 3 3', '0 1 2', 'undefined undefined undefined', 'An error'], 0, 'How many i variables are there with var?', 'With <code>var</code> there is one shared <code>i</code>, which is 3 when the functions run.', code='const fs = [];\nfor (var i = 0; i < 3; i++) fs.push(() => i);\nconsole.log(...fs.map(f => f()));'),
    quiz('m', 'What does logIn("asha", null) use for the password?', ['null', 'The default "Secret12"', 'undefined', '""'], 0, 'Defaults only replace one value.', 'Default values apply only when the argument is <code>undefined</code>.', code='function logIn(user, password = "Secret12") { return password; }'),
    quiz('m', 'Why does this.timeout(5000) fail inside it("...", () => {...}) in Mocha?', ['Arrow functions do not get Mocha\'s context as this', 'Mocha has no timeout method', 'Timeouts must be set in the config', 'this.timeout only works in beforeEach'], 0, 'Who decides this for an arrow?', 'An arrow uses the outer <code>this</code>, so Mocha cannot hand it the test context.'),
    quiz('h', 'What happens here?', ['ReferenceError: cannot access before initialization', 'It prints undefined', 'It prints 2', 'It prints null'], 0, 'let is hoisted differently from var.', 'The name exists but is in the temporal dead zone until its line runs.', code='console.log(x);\nlet x = 2;'),
    quiz('h', 'In a module, what is this inside method when it is called like this?', ['undefined', 'obj', 'The global object', 'f'], 0, 'There is nothing before the dot.', 'Modules are strict, and a plain call gives <code>this</code> as <code>undefined</code>.', code='const f = obj.method;\nf();'),
    quiz('h', 'What does fn.bind(x) return?', ['A new function whose this is always x', 'The result of calling fn with this as x', 'fn itself, changed', 'undefined'], 0, 'bind does not call.', '<code>call</code> and <code>apply</code> call immediately. <code>bind</code> returns a new function for later.'),
    quiz('x', 'A search box is debounced by 300 ms. A test types and reads the result count straight away. What is the most likely outcome?', ['It sees the old results because the request has not been sent yet', 'It sees the new results', 'The typing fails', 'The debounce is skipped in tests'], 0, 'When does the debounced function run?', 'The request only fires 300 ms after the last key press. Use an auto-waiting assertion.'),
    quiz('x', 'Which function keeps state between calls without a global variable?', ['One created inside another function that returns it', 'Any arrow function', 'A function declaration', 'A function using var'], 0, 'Think closures.', 'A closure keeps the variables of the function that created it.'),
    quiz('x', 'What does this print?', ['1 1', '1 2', '2 2', '0 1'], 0, 'Each factory call makes its own count.', '<code>a</code> and <code>b</code> each have their own <code>count</code>, so both print 1.', code='const make = () => { let count = 0; return () => ++count; };\nconst a = make(), b = make();\nconsole.log(a(), b());'),
]

CALC = [
    calc('e', 'What does add(2) return?', 'NaN', 'b is undefined.', ['<code>b</code> is <code>undefined</code>.', '<span class="eq">2 + undefined = NaN</span>'], code='function add(a, b) { return a + b; }'),
    calc('e', 'What does total(1, 2, 3, 4) return?', '10', 'Rest gathers all four numbers.', ['<span class="eq">1 + 2 + 3 + 4 = 10</span>'], code='const total = (...n) => n.reduce((s, x) => s + x, 0);'),
    calc('m', 'What does the last line print?', '3', 'Each call adds one.', ['The counter goes 1, 2, 3.'], code='function makeCounter() { let c = 0; return () => ++c; }\nconst next = makeCounter();\nnext(); next();\nconsole.log(next());'),
    calc('m', 'What is factorial(5)?', '120', 'Multiply 5 down to 1.', ['<span class="eq">5 × 4 × 3 × 2 × 1 = 120</span>']),
    calc('h', 'How many times does slowSquare really run?', '2', 'The cache remembers each input once.', ['Inputs: 9, 9, 4, 9.', 'Only 9 and 4 are new. That is 2 real calls.'], code='const fast = memoize(slowSquare);\nfast(9); fast(9); fast(4); fast(9);'),
    calc('h', 'factorial(4) is called. How many frames are on the call stack at its deepest point?', '4', 'factorial(4), (3), (2), (1).', ['Each call waits for the next one until n is 1.', 'Frames: factorial(4), factorial(3), factorial(2), factorial(1). That is 4.']),
    calc('x', 'A debounced search waits 300 ms. A user types 5 letters 100 ms apart. How many ms after the first key press is the request sent?', '700', 'The timer restarts on each key.', ['The last key is pressed at 400 ms.', '<span class="eq">400 + 300 = 700 ms</span>'], alt=['700 ms']),
    calc('x', 'What does this print?', '6', 'bind fixes this but call cannot change it again.', ['<code>bound</code> always uses <code>{ n: 6 }</code>.', 'Calling it with <code>call</code> on another object does not change a bound function.'],
         code='function getN() { return this.n; }\nconst bound = getN.bind({ n: 6 });\nconsole.log(bound.call({ n: 9 }));'),
]

EX = [
    ex('discount', 'e', 'A discount with a default', '<p>Write <code>discount(price, percent = 10)</code> that returns the price after the discount, rounded to two decimals as a number.</p>',
       'function discount(price, percent) {\n  \n}\n',
       [('discount(200)', 180), ('discount(200, 25)', 150), ('discount(99.99, 15)', 84.99), ('discount(50, 0)', 50)],
       'function discount(price, percent = 10) {\n  return Math.round(price * (100 - percent)) / 100;\n}', hint='Give <code>percent</code> a default. Round with <code>Math.round(x * 100) / 100</code>.',
       why='Multiplying by <code>(100 - percent)</code> and dividing by 100 once keeps rounding errors small.'),
    ex('counter', 'm', 'A counter with a closure', '<p>Write <code>makeCounter(start = 0)</code> that returns an object with <code>next()</code> (adds one and returns the new value), <code>reset()</code> (back to start) and <code>peek()</code> (returns the value without changing it).</p>',
       'function makeCounter(start = 0) {\n  \n}\n',
       [('(() => { const c = makeCounter(); c.next(); c.next(); return c.peek(); })()', 2),
        ('(() => { const c = makeCounter(5); c.next(); c.reset(); return c.peek(); })()', 5),
        ('(() => { const a = makeCounter(), b = makeCounter(); a.next(); return [a.peek(), b.peek()]; })()', [1, 0]),
        ('makeCounter(1).next()', 2)],
       'function makeCounter(start = 0) {\n  let count = start;\n  return {\n    next: () => ++count,\n    reset: () => { count = start; },\n    peek: () => count,\n  };\n}',
       hint='Keep <code>let count = start</code> inside makeCounter and return three arrow functions that use it.', why='Each call to makeCounter gets its own <code>count</code>, so counters never share state.'),
    ex('once', 'h', 'Run only once', '<p>Write <code>once(fn)</code>. It returns a function that calls <code>fn</code> with its arguments the first time and returns the result. Every later call returns that first result without calling <code>fn</code> again. This is how "log in only once per suite" helpers work.</p>',
       'function once(fn) {\n  return fn;\n}\n',
       [('(() => { let n = 0; const f = once(() => ++n); f(); f(); return n; })()', 1),
        ('(() => { const f = once((a, b) => a + b); return [f(2, 3), f(10, 10)]; })()', [5, 5]),
        ('(() => { const f = once(() => undefined); let calls = 0; const g = once(() => { calls++; }); g(); g(); return calls; })()', 1)],
       'function once(fn) {\n  let done = false;\n  let result;\n  return (...args) => {\n    if (!done) {\n      done = true;\n      result = fn(...args);\n    }\n    return result;\n  };\n}',
       hint='Keep two variables in the closure: whether it has run, and the result.', why='Using a separate <code>done</code> flag works even when the first result is <code>undefined</code>.'),
    ex('debounce', 'x', 'Write debounce', '<p>Write <code>debounce(fn, wait)</code>. The returned function restarts a timer on every call and calls <code>fn</code> with the <b>latest</b> arguments once no call has happened for <code>wait</code> milliseconds.</p>',
       'function debounce(fn, wait) {\n  return fn;\n}\n',
       [('(async () => { const seen = []; const d = debounce(x => seen.push(x), 30); d(1); d(2); d(3); await new Promise(r => setTimeout(r, 80)); return seen; })()', [3]),
        ('(async () => { const seen = []; const d = debounce(x => seen.push(x), 20); d("a"); await new Promise(r => setTimeout(r, 60)); d("b"); await new Promise(r => setTimeout(r, 60)); return seen; })()', ['a', 'b']),
        ('(async () => { const seen = []; const d = debounce((a, b) => seen.push(a + b), 10); d(1, 2); return seen.length; })()', 0)],
       'function debounce(fn, wait) {\n  let timer;\n  return (...args) => {\n    clearTimeout(timer);\n    timer = setTimeout(() => fn(...args), wait);\n  };\n}',
       hint='Keep the timer id in the closure. <code>clearTimeout</code> the old one before starting a new one.', why='Each call cancels the pending timer, so only the last call in a burst survives long enough to run.'),
]

T = {
    'slug': 'js-functions', 'title': 'Functions, Scope and Closures', 'short': 'Functions and closures', 'emoji': '🧩', 'module': MODULE, 'minutes': 20,
    'lead': 'Declarations and arrows, defaults, rest and options objects, scope and hoisting, closures, how this is decided, higher order functions such as memoize and debounce, and recursion on the call stack.',
    'desc': 'Functions, arrow functions, parameters, scope, hoisting, closures, this with call, apply and bind, higher order functions, memoize, debounce and recursion.',
    'summary': 'Function declarations and expressions, arrow functions, default and rest parameters, options objects, lexical scope, hoisting and the temporal dead zone, closures and private state, the loop closure bug, this with call, apply and bind and why Mocha needs function, higher order functions, memoize, debounce, recursion and a closure based test data factory.',
    'keywords': ['function', 'arrow function', 'parameters', 'scope', 'hoisting', 'closure', 'this', 'bind', 'call', 'apply', 'higher order function', 'callback', 'memoize', 'debounce', 'recursion', 'test data factory'],
    'qa_intro': 'Closures and this explain how describe, beforeEach and test share variables, why Mocha and Cypress sometimes need function instead of arrows, and how to build clean test data factories.',
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
