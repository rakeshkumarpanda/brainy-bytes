# Chapter 8: prototypes, classes, private fields, inheritance, composition, the Page Object Model and test data builders.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🏗️', 'Structure and tooling', 'js-structure', 'Classes, modules, packages, TypeScript and the tools that keep a growing codebase and test suite in order.')

LOGIN_HTML = '''
<!doctype html>
<html>
<body>
  <form id="login">
    <label>Email <input id="email" type="email"></label>
    <label>Password <input id="password" type="password"></label>
    <button type="submit" data-test="sign-in">Sign in</button>
    <p class="error" hidden></p>
  </form>
  <h1 id="welcome" hidden></h1>
  <script>
  </script>
</body>
</html>
'''

APP_JS = '''
// The app under test: a tiny login form.
document.querySelector("#login").addEventListener("submit", e => {
  e.preventDefault();
  const email = document.querySelector("#email").value;
  const pass = document.querySelector("#password").value;
  const error = document.querySelector(".error");
  if (pass !== "s3cret") {
    error.textContent = "Wrong email or password";
    error.hidden = false;
    return;
  }
  error.hidden = true;
  const welcome = document.querySelector("#welcome");
  welcome.textContent = `Hello, ${email.split("@")[0]}`;
  welcome.hidden = false;
});
'''

CODES = {
    'proto': run('''
const animal = {
  breathe() { return `${this.name} breathes`; },
};
const dog = Object.create(animal);        // dog's prototype is animal
dog.name = "Rex";
dog.bark = function () { return "Woof"; };

console.log(dog.bark());                   // found on dog itself
console.log(dog.breathe());                // not on dog, found one step up
console.log(Object.getPrototypeOf(dog) === animal);
console.log(Object.hasOwn(dog, "breathe"), "breathe" in dog);

const arr = [1, 2];
console.log(Object.getPrototypeOf(arr) === Array.prototype);
console.log(Object.getPrototypeOf(Array.prototype) === Object.prototype);
console.log(Object.getPrototypeOf(Object.prototype));   // the end of every chain
''', 'Looking up the prototype chain'),
    'ctor-fn': run('''
// Before 2015 this is how "classes" were written. You still see it in older libraries.
function User(name) {
  this.name = name;
}
User.prototype.greet = function () {
  return `Hi, ${this.name}`;
};

const a = new User("Asha");
const b = new User("Ravi");
console.log(a.greet(), b.greet());
console.log(a.greet === b.greet);          // one shared copy on the prototype
console.log(a instanceof User, Object.getPrototypeOf(a) === User.prototype);
''', 'Constructor functions and new'),
    'class': run('''
class Cart {
  static currency = "INR";                 // belongs to the class, not each cart
  items = [];                              // a public field, set up for every new cart

  constructor(owner) {
    this.owner = owner;
  }

  add(name, price, qty = 1) {
    this.items.push({ name, price, qty });
    return this;                           // returning this allows chaining
  }

  get total() {                            // read like a property, computed each time
    return this.items.reduce((sum, i) => sum + i.price * i.qty, 0);
  }

  static fromJSON(json) {
    const data = JSON.parse(json);
    const cart = new Cart(data.owner);
    for (const i of data.items) cart.add(i.name, i.price, i.qty);
    return cart;
  }
}

const cart = new Cart("Asha").add("Pen", 20, 3).add("Book", 250);
console.log(cart.total, Cart.currency);
console.log(typeof Cart, Object.getOwnPropertyNames(Cart.prototype));

const copy = Cart.fromJSON('{"owner":"Ravi","items":[{"name":"Mug","price":199,"qty":2}]}');
console.log(copy.owner, copy.total);
''', 'A class with fields, a getter and a static method'),
    'class-traps': run('''
class Counter {
  count = 0;
  increment() { this.count++; }
  incrementArrow = () => { this.count++; };   // a field holding an arrow, bound per object
}

const c = new Counter();
const { increment, incrementArrow } = c;
incrementArrow();
console.log(c.count);
try {
  increment();                             // class bodies are strict, so this is undefined
} catch (e) {
  console.log(e.constructor.name + ":", e.message);
}

try {
  new Shape();                             // classes are not hoisted like functions
} catch (e) {
  console.log(e.constructor.name + ":", e.message);
}
class Shape {}
''', 'Two class traps: lost this and no hoisting', expect='ok'),
    'private': run('''
class BankAccount {
  #balance = 0;                            // private: only code inside the class can see it
  static #count = 0;

  constructor(owner) {
    this.owner = owner;
    BankAccount.#count++;
  }

  deposit(amount) {
    this.#check(amount);
    this.#balance += amount;
    return this.#balance;
  }

  #check(amount) {                         // a private method
    if (!(amount > 0)) throw new RangeError(`Invalid amount: ${amount}`);
  }

  get balance() { return this.#balance; }
  static get count() { return BankAccount.#count; }
  static isAccount(obj) { return #balance in obj; }   // a safe brand check
}

const acc = new BankAccount("Mei");
acc.deposit(500);
console.log(acc.balance, BankAccount.count);
console.log(Object.keys(acc), JSON.stringify(acc));
console.log(BankAccount.isAccount(acc), BankAccount.isAccount({ balance: 1 }));
for (const attempt of [() => { acc.balance = 1_000_000; }, () => acc.deposit(-5)]) {
  try {
    attempt();
  } catch (e) {
    console.log(e.name + ":", e.message);
  }
}
console.log(acc.balance);
''', 'Private fields and methods'),
    'static-block': run('''
class Config {
  static env;
  static baseURL;
  static {                                 // runs once when the class is defined
    Config.env = process.env.TEST_ENV ?? "staging";
    Config.baseURL = { staging: "https://staging.shop.example", prod: "https://shop.example" }[Config.env];
  }
}
console.log(Config.env, Config.baseURL);
''', 'Static initialisation blocks', play=False),
    'extends': run('''
class Animal {
  constructor(name) { this.name = name; }
  speak() { return `${this.name} makes a sound`; }
  toString() { return `[${this.constructor.name} ${this.name}]`; }
}

class Dog extends Animal {
  constructor(name, breed) {
    super(name);                           // must run before this is used
    this.breed = breed;
  }
  speak() {                                // overrides the parent method
    return `${super.speak()}, then barks`;  // and can still call it
  }
}

const d = new Dog("Rex", "beagle");
console.log(d.speak());
console.log(`${d}`);
console.log(d instanceof Dog, d instanceof Animal, d instanceof Object);
console.log(Object.getPrototypeOf(Dog.prototype) === Animal.prototype);
''', 'extends and super'),
    'errors': run('''
class HttpError extends Error {
  constructor(status, url, options) {
    super(`Request to ${url} failed with ${status}`, options);
    this.name = "HttpError";
    this.status = status;
  }
  get retryable() { return this.status >= 500 || this.status === 429; }
}

class NotFoundError extends HttpError {
  constructor(url) {
    super(404, url);
    this.name = "NotFoundError";
  }
}

function load(status) {
  try {
    throw new TypeError("network down");
  } catch (low) {
    if (status === 404) throw new NotFoundError("/api/users/9");
    throw new HttpError(status, "/api/users", { cause: low });   // keep the original error
  }
}

for (const status of [404, 503]) {
  try {
    load(status);
  } catch (e) {
    console.log(e.name, "|", e.message, "| retry:", e.retryable);
    console.log("  instanceof HttpError:", e instanceof HttpError, "| cause:", e.cause?.message);
  }
}
''', 'Custom error classes'),
    'composition': run('''
// Instead of a deep tree of subclasses, build objects from small abilities.
const canLog = base => class extends base {
  log(msg) { (this.logs ??= []).push(msg); return this; }
};
const canRetry = base => class extends base {
  async retry(fn, times = 3) {
    for (let i = 1; ; i++) {
      try { return await fn(i); } catch (e) {
        this.log?.(`attempt ${i} failed: ${e.message}`);
        if (i === times) throw e;
      }
    }
  }
};

class Client {}
class ApiClient extends canRetry(canLog(Client)) {}

const api = new ApiClient();
const result = await api.retry(n => {
  if (n < 3) throw new Error("timeout");
  return "200 OK";
});
console.log(result);
console.log(api.logs);

// Composition with plain objects: the client HAS a logger instead of BEING one
class Uploader {
  constructor(logger = console) { this.logger = logger; }
  upload(file) { this.logger.log(`uploading ${file}`); return true; }
}
const messages = [];
new Uploader({ log: m => messages.push(m) }).upload("report.pdf");
console.log(messages);
''', 'Mixins and composition'),
    'pom': dom(LOGIN_HTML.replace('<script>\n  </script>', '<script>' + APP_JS + '</script>'), '''
// A page object hides the selectors behind methods with business names.
class LoginPage {
  constructor(doc) { this.doc = doc; }

  get email() { return this.doc.querySelector("#email"); }
  get password() { return this.doc.querySelector("#password"); }
  get submit() { return this.doc.querySelector('[data-test="sign-in"]'); }
  get error() { return this.doc.querySelector(".error"); }
  get welcome() { return this.doc.querySelector("#welcome"); }

  loginAs(email, password) {
    this.email.value = email;
    this.password.value = password;
    this.submit.click();
    return this;
  }
}

const page = new LoginPage(document);
page.loginAs("asha@shop.example", "wrong");
console.log("error shown:", !page.error.hidden, "|", page.error.textContent);

page.loginAs("asha@shop.example", "s3cret");
console.log("error shown:", !page.error.hidden, "| welcome:", page.welcome.textContent);
''', 'A page object for a login form'),
    'pom-pw': show('''
// pages/login.page.js (Playwright)
export class LoginPage {
  constructor(page) {
    this.page = page;
    this.email = page.getByLabel("Email");
    this.password = page.getByLabel("Password");
    this.submit = page.getByRole("button", { name: "Sign in" });
    this.error = page.locator(".error");
  }
  async goto() {
    await this.page.goto("/login");
  }
  async loginAs(email, password) {
    await this.email.fill(email);
    await this.password.fill(password);
    await this.submit.click();
  }
}

// tests/login.spec.js
import { test, expect } from "@playwright/test";
import { LoginPage } from "../pages/login.page.js";

test("wrong password shows an error", async ({ page }) => {
  const login = new LoginPage(page);
  await login.goto();
  await login.loginAs("asha@shop.example", "wrong");
  await expect(login.error).toHaveText("Wrong email or password");
});
''', 'The same page object in Playwright', note='Runs for real in chapter 21', result='The test reads like the steps a manual tester writes. When the button text changes, only the page object changes.'),
    'pom-selenium': show('''
// pages/LoginPage.js (Selenium WebDriver)
const { By, until } = require("selenium-webdriver");

class LoginPage {
  static EMAIL = By.id("email");
  static PASSWORD = By.id("password");
  static SUBMIT = By.css('[data-test="sign-in"]');
  static ERROR = By.css(".error");

  constructor(driver) { this.driver = driver; }

  async open(baseUrl) {
    await this.driver.get(`${baseUrl}/login`);
  }
  async loginAs(email, password) {
    await this.driver.findElement(LoginPage.EMAIL).sendKeys(email);
    await this.driver.findElement(LoginPage.PASSWORD).sendKeys(password);
    await this.driver.findElement(LoginPage.SUBMIT).click();
  }
  async errorText() {
    const el = await this.driver.wait(until.elementLocated(LoginPage.ERROR), 5000);
    return el.getText();
  }
}
module.exports = { LoginPage };
''', 'The same page object in Selenium', note='Runs for real in chapter 21', result='Locators live in static fields, and every method is async because each WebDriver call talks to the browser.'),
    'builder': run('''
class UserBuilder {
  #data = { name: "Test User", email: "user@test.example", role: "customer", verified: true, address: { city: "Pune" } };
  static #seq = 0;

  withName(name) { this.#data.name = name; return this; }
  withRole(role) { this.#data.role = role; return this; }
  unverified() { this.#data.verified = false; return this; }
  inCity(city) { this.#data.address = { ...this.#data.address, city }; return this; }

  build() {
    const id = ++UserBuilder.#seq;
    return structuredClone({ id, ...this.#data, email: `user${id}@test.example` });
  }
}

const admin = new UserBuilder().withName("Asha").withRole("admin").build();
const newbie = new UserBuilder().unverified().inCity("Bhubaneswar").build();
console.log(admin);
console.log(newbie);
console.log(admin.email !== newbie.email);
''', 'A test data builder'),
    'api-client': run('''
// One base class knows HTTP. Each area of the API gets a small subclass.
class ApiClient {
  #log = [];
  constructor(baseURL, transport) {
    this.baseURL = baseURL;
    this.transport = transport;            // injected, so tests can pass a fake
  }
  async request(method, path, body) {
    const res = await this.transport({ method, url: this.baseURL + path, body });
    this.#log.push(`${method} ${path} -> ${res.status}`);
    if (res.status >= 400) throw new Error(`${method} ${path} failed with ${res.status}`);
    return res.body;
  }
  get history() { return [...this.#log]; }
}

class UsersApi extends ApiClient {
  get(id) { return this.request("GET", `/users/${id}`); }
  create(user) { return this.request("POST", "/users", user); }
}

// A fake transport stands in for the network
const db = new Map([[1, { id: 1, name: "Asha" }]]);
async function fakeTransport({ method, url, body }) {
  const id = Number(url.split("/").pop());
  if (method === "GET") return db.has(id) ? { status: 200, body: db.get(id) } : { status: 404 };
  const user = { id: db.size + 1, ...body };
  db.set(user.id, user);
  return { status: 201, body: user };
}

const users = new UsersApi("https://api.shop.example", fakeTransport);
console.log(await users.get(1));
console.log(await users.create({ name: "Ravi" }));
await users.get(42).catch(e => console.log("Error:", e.message));
console.log(users.history);
''', 'An API client with a base class and an injected transport'),
}

PARTS = [
    part('prototypes', '🧬', 'Objects and prototypes', '''
<p>Every object in JavaScript has a hidden link to another object called its <b>prototype</b>. When you read a property the object does not have, JavaScript follows that link and looks there, then on that object's prototype, and so on. This list of links is the <b>prototype chain</b>. It ends at <code>Object.prototype</code>, whose prototype is <code>null</code>.</p>
<div class="viz" data-viz="flow" data-k="chain"></div>
[[proto]]
<p>Before the <code>class</code> keyword existed, shared methods were put on a constructor function's <code>prototype</code> object and objects were made with <code>new</code>. Classes still work exactly this way underneath.</p>
[[ctor-fn]]
<div class="tip"><code>new User("Asha")</code> does four things: it creates an empty object, links it to <code>User.prototype</code>, runs <code>User</code> with <code>this</code> set to the new object, and returns it.</div>
''', kw=['prototype', 'prototype chain', '__proto__', 'Object.create', 'Object.getPrototypeOf', 'hasOwn', 'constructor function', 'new', 'Object.prototype']),
    part('classes', '🏛️', 'Classes', '''
<p>A <b>class</b> is a template for objects that share the same shape and methods. It has a <code>constructor</code> that sets up each new object, <b>methods</b> shared through the prototype, <b>fields</b> that every object gets, <b>getters and setters</b> that look like properties, and <b>static</b> members that belong to the class itself.</p>
[[class]]
<div class="tw"><table class="jt"><tr><th>Member</th><th>Lives on</th><th>Example</th></tr>
<tr><td>field</td><td>each object</td><td><code>items = []</code></td></tr>
<tr><td>method</td><td>the prototype, shared</td><td><code>add(name, price)</code></td></tr>
<tr><td>getter or setter</td><td>the prototype, used like a property</td><td><code>get total()</code></td></tr>
<tr><td>static</td><td>the class itself</td><td><code>Cart.fromJSON(json)</code></td></tr>
</table></div>
<h3>Two traps</h3>
<p>Class bodies are always in strict mode. A method pulled off its object and called on its own gets <code>this</code> as <code>undefined</code>. An arrow function stored in a field keeps its object. Classes are also not usable before the line that declares them.</p>
[[class-traps]]
''', qa=True, qa_why='Page objects, API clients, fixtures and custom reporters in every automation framework are classes.',
        kw=['class', 'constructor', 'method', 'field', 'getter', 'setter', 'get', 'static', 'this', 'chaining', 'strict mode', 'hoisting']),
    part('private', '🔒', 'Private fields and encapsulation', '''
<p>A field or method whose name starts with <code>#</code> is <b>private</b>. Only code inside the class body can read or change it. It does not show up in <code>Object.keys</code>, in JSON or in the console of other code, and any attempt to read it from outside is a syntax error. This is real privacy, not a naming habit like the old <code>_balance</code>.</p>
[[private]]
<p>A <b>static block</b> runs once when the class is defined. It is useful for set up that needs a few statements, such as picking a base URL from an environment variable.</p>
[[static-block]]
<div class="modern">Public and private fields, private methods, <code>#x in obj</code> and static blocks arrived in ES2022. Every current browser and Node.js support them.</div>
''', kw=['private', '#', 'private field', 'private method', 'encapsulation', 'static block', 'ergonomic brand check', 'in', 'ES2022']),
    part('inheritance', '🌳', 'Inheritance with extends and super', '''
<p><code>class Dog extends Animal</code> makes <code>Animal.prototype</code> the prototype of <code>Dog.prototype</code>. A <code>Dog</code> gets every <code>Animal</code> method and can <b>override</b> any of them. Inside the subclass, <code>super(...)</code> calls the parent constructor, and <code>super.method()</code> calls the parent version of a method.</p>
[[extends]]
<div class="warn">In a subclass constructor, <code>super()</code> must run before the first use of <code>this</code>. Forgetting it throws a <code>ReferenceError</code> as soon as the class is used.</div>
<h3>Custom errors</h3>
<p>Extending <code>Error</code> gives errors a clear type you can check with <code>instanceof</code>, extra data such as a status code, and a <code>cause</code> that keeps the original error. Test frameworks print the cause too, which makes failures much easier to read.</p>
[[errors]]
''', qa=True, qa_why='A BasePage that every page object extends, and custom errors with a status and a cause, are standard in test frameworks.',
        kw=['extends', 'super', 'inheritance', 'override', 'instanceof', 'subclass', 'custom error', 'Error cause', 'HttpError', 'BasePage']),
    part('composition', '🧩', 'Composition over inheritance', '''
<p>Deep class trees get hard to change: a fix in a parent class affects every child. Many teams prefer <b>composition</b>, where an object is built from small parts it holds or mixes in. A <b>mixin</b> is a function that takes a class and returns a new class with extra abilities. Passing a helper into the constructor, called <b>dependency injection</b>, lets tests replace it with a fake.</p>
[[composition]]
<div class="vs"><div><b>Inheritance: "is a"</b>A <code>CheckoutPage</code> is a <code>BasePage</code>. Good for one shallow level of shared behaviour.</div><div><b>Composition: "has a"</b>A <code>CheckoutPage</code> has a <code>Header</code> and a <code>CartSummary</code> component. Good for parts that appear on many pages.</div></div>
''', kw=['composition', 'mixin', 'dependency injection', 'has a', 'is a', 'component', 'logger', 'retry']),
    part('pom', '📄', 'The Page Object Model', '''
<p>The <b>Page Object Model</b> (POM) is the most common design pattern in UI automation. Each page or component of the app gets a class. The class holds the locators and offers methods with business names such as <code>loginAs</code> or <code>addToCart</code>. Tests then call those methods and never touch selectors directly.</p>
[[pom]]
<p>The idea is identical in every tool. Only the way you find and click elements changes.</p>
[[pom-pw]]
[[pom-selenium]]
<div class="qa-box">Rules that keep page objects healthy: one class per page or component, no assertions inside page objects (they belong in tests), methods return useful values or other page objects, and locators prefer roles, labels and <code>data-test</code> attributes over long CSS paths.</div>
''', qa=['Playwright', 'Selenium', 'Cypress', 'WebdriverIO'], qa_why='Almost every UI automation framework you join will be organised as page objects.',
        kw=['Page Object Model', 'POM', 'page object', 'locator', 'loginAs', 'BasePage', 'component', 'Playwright', 'Selenium', 'maintainable tests']),
    part('scenario', '🎬', 'Real world scenario: test data and an API client', '''
<div class="scenario"><b>The situation</b>Your API tests create many users with small differences, and every test repeats the same HTTP code. You want readable test data and one place that knows how to call the API.</div>
<p>A <b>builder</b> class starts from sensible defaults, and each test changes only what matters to it. Every built user gets a fresh email, so tests never clash.</p>
[[builder]]
<p>An <b>API client</b> base class owns the HTTP details and logging. Small subclasses add one method per endpoint. Because the transport is passed in, the same client works against a fake in unit tests and the real server in integration tests.</p>
[[api-client]]
''', qa=True, kw=['builder pattern', 'test data builder', 'API client', 'base class', 'dependency injection', 'fake transport', 'fluent interface']),
]

DG = {
    'chain': {'t': 'Where dog.breathe() is found', 'w': 900, 'h': 230,
              'n': [['dog', 20, 80, 180, 70, 'dog', {'c': 2, 'sub': 'name, bark', 'i': 'The object itself. Own properties are checked first.'}],
                    ['animal', 250, 80, 180, 70, 'animal', {'c': 1, 'sub': 'breathe', 'i': 'The prototype of dog, set by Object.create(animal).'}],
                    ['op', 480, 80, 190, 70, 'Object.prototype', {'c': 0, 'sub': 'toString, hasOwnProperty', 'i': 'Every plain object ends up here.'}],
                    ['nul', 730, 80, 140, 70, 'null', {'c': 5, 'sh': 'pill', 'i': 'The chain stops. A missing property gives undefined.'}]],
              'e': [['dog', 'animal', {'t': 'prototype'}], ['animal', 'op', {'t': 'prototype'}], ['op', 'nul', {'t': 'prototype'}]],
              'st': [[['dog'], 'JavaScript looks for breathe on dog first. dog only has name and bark.'],
                     [['animal', 'dog>animal'], 'It follows the prototype link to animal, finds breathe there and calls it with this set to dog.'],
                     [['op', 'animal>op'], 'A name that is not on animal either, such as toString, is looked up on Object.prototype.'],
                     [['nul', 'op>nul'], 'If nothing on the chain has it, the lookup reaches null and the result is undefined.']]},
}

INFO = {'title': 'Classes put data and behaviour together', 'panels': [
    panel([['e', '🧬'], ['t', 'dog → animal → Object.prototype', {'b': 1, 'size': 11}]], 'Prototypes', 'Objects borrow from the object behind them.', 'Classes are a neater way to set these links up.'),
    panel([['e', '🏛️'], ['t', 'class Cart { add() {} }', {'b': 1}]], 'Classes', 'One template, many objects.', 'Fields, methods, getters and static members.'),
    panel([['e', '🔒'], ['t', '#balance', {'b': 1}]], 'Private', 'Hidden from everything outside the class.', 'Change state only through methods you control.'),
    panel([['e', '📄'], ['t', 'login.loginAs(user)', {'b': 1}]], 'Page objects', 'Selectors in one place, tests in plain words.', 'The pattern behind most UI automation frameworks.')],
    'remember': 'A class bundles data and the methods that work on it. Page objects bundle a page and the actions you take on it.'}

REAL = [
    ['🛒', 'A shopping cart', 'An e-commerce site models carts, products and orders as classes with getters for totals and private fields for prices that only the server may set.'],
    ['🧪', 'A UI test framework', 'A team of five keeps 300 Playwright tests stable because a button rename touches one page object instead of 40 tests.'],
    ['🚨', 'Clear failures', 'An API test suite throws HttpError with the status and the URL, so the CI report says "GET /orders failed with 503" instead of "undefined is not a function".'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers prototypes, classes, private fields, inheritance, composition and the Page Object Model used in UI automation.',
        'यह अध्याय prototypes, classes, private fields, inheritance, composition और UI automation में इस्तेमाल होने वाला Page Object Model सिखाता है।',
        'ಈ ಅಧ್ಯಾಯ prototypes, classes, private fields, inheritance, composition ಮತ್ತು UI automation ನ Page Object Model ಕಲಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ prototypes, classes, private fields, inheritance, composition ଓ UI automation ର Page Object Model ଶିଖାଏ।',
        'يتناول هذا الفصل النماذج الأولية والأصناف والحقول الخاصة والوراثة والتركيب ونموذج كائن الصفحة في أتمتة الواجهات.',
        'Dieses Kapitel behandelt Prototypen, Klassen, private Felder, Vererbung, Komposition und das Page Object Model der UI-Automatisierung.'),
    say('prototypes', 'Prototypes', 'Every object links to a prototype. A missing property is looked up along this chain until it reaches null.',
        'हर object एक prototype से जुड़ा होता है। जो property नहीं मिलती, वह इस chain में null तक खोजी जाती है।',
        'ಪ್ರತಿ object ಒಂದು prototype ಗೆ ಜೋಡಣೆಯಾಗಿದೆ. ಸಿಗದ property ಈ chain ನಲ್ಲಿ null ವರೆಗೆ ಹುಡುಕಲಾಗುತ್ತದೆ.',
        'ପ୍ରତ୍ୟେକ object ଏକ prototype ସହ ଯୋଡ଼ା। ନଥିବା property ଏହି chain ରେ null ପର୍ଯ୍ୟନ୍ତ ଖୋଜାଯାଏ।',
        'كل كائن مرتبط بنموذج أولي. يبحث عن الخاصية المفقودة على طول هذه السلسلة حتى تصل إلى null.',
        'Jedes Objekt ist mit einem Prototyp verknüpft. Eine fehlende Eigenschaft wird entlang dieser Kette bis null gesucht.'),
    say('classes', 'Classes', 'A class has a constructor, fields, shared methods, getters and static members. Methods pulled off an object lose this.',
        'Class में constructor, fields, shared methods, getters और static members होते हैं। Object से अलग की गई method का this खो जाता है।',
        'Class ನಲ್ಲಿ constructor, fields, shared methods, getters ಮತ್ತು static members ಇರುತ್ತವೆ. ಬೇರ್ಪಡಿಸಿದ method ತನ್ನ this ಕಳೆದುಕೊಳ್ಳುತ್ತದೆ.',
        'Class ରେ constructor, fields, shared methods, getters ଓ static members ଥାଏ। ଅଲଗା କରାଯାଇଥିବା method ର this ହଜିଯାଏ।',
        'يحتوي الصنف على منشئ وحقول ودوال مشتركة ودوال جلب وأعضاء ثابتة. الدالة المفصولة عن كائنها تفقد this.',
        'Eine Klasse hat einen Konstruktor, Felder, gemeinsame Methoden, Getter und statische Mitglieder. Abgelöste Methoden verlieren this.'),
    say('private', 'Private fields', 'Names that start with a hash are private. Only code inside the class can use them, so outside code cannot break the state.',
        '# से शुरू होने वाले नाम private होते हैं। सिर्फ class के अंदर का code उन्हें इस्तेमाल कर सकता है।',
        '# ನಿಂದ ಆರಂಭವಾಗುವ ಹೆಸರುಗಳು private. Class ಒಳಗಿನ code ಮಾತ್ರ ಅವುಗಳನ್ನು ಬಳಸಬಹುದು.',
        '# ରୁ ଆରମ୍ଭ ହେଉଥିବା ନାମ private। କେବଳ class ଭିତରର code ସେଗୁଡ଼ିକ ବ୍ୟବହାର କରିପାରେ।',
        'الأسماء التي تبدأ بعلامة # خاصة. لا يستخدمها إلا الكود داخل الصنف، فلا يستطيع الكود الخارجي إفساد الحالة.',
        'Namen mit Raute sind privat. Nur Code in der Klasse kann sie nutzen, also kann fremder Code den Zustand nicht zerstören.'),
    say('inheritance', 'Inheritance', 'extends builds a subclass, super calls the parent, and custom errors carry a status and a cause.',
        'extends subclass बनाता है, super parent को call करता है, और custom errors status और cause रखते हैं।',
        'extends subclass ಮಾಡುತ್ತದೆ, super parent ಅನ್ನು call ಮಾಡುತ್ತದೆ, custom errors status ಮತ್ತು cause ಹೊಂದಿರುತ್ತವೆ.',
        'extends subclass ତିଆରି କରେ, super parent କୁ call କରେ, ଏବଂ custom errors status ଓ cause ରଖନ୍ତି।',
        'تنشئ extends صنفًا فرعيًا، وتستدعي super الأب، وتحمل الأخطاء المخصصة حالة وسببًا.',
        'extends erzeugt eine Unterklasse, super ruft die Elternklasse auf, eigene Fehler tragen Status und Ursache.'),
    say('composition', 'Composition', 'Build objects from small parts. Mixins add abilities, and passing helpers into the constructor lets tests use fakes.',
        'Objects को छोटे हिस्सों से बनाएं। Mixins abilities जोड़ते हैं, और constructor में helpers देने से tests fakes इस्तेमाल कर सकते हैं।',
        'Objects ಅನ್ನು ಚಿಕ್ಕ ಭಾಗಗಳಿಂದ ಕಟ್ಟಿ. Mixins abilities ಸೇರಿಸುತ್ತವೆ, constructor ಗೆ helpers ಕೊಟ್ಟರೆ tests fakes ಬಳಸಬಹುದು.',
        'Objects କୁ ଛୋଟ ଅଂଶରୁ ଗଢ଼ନ୍ତୁ। Mixins abilities ଯୋଡ଼ନ୍ତି, constructor ରେ helpers ଦେଲେ tests fakes ବ୍ୟବହାର କରିପାରେ।',
        'ابن الكائنات من أجزاء صغيرة. تضيف الخلطات قدرات، وتمرير المساعدات إلى المنشئ يسمح للاختبارات باستخدام بدائل.',
        'Baue Objekte aus kleinen Teilen. Mixins fügen Fähigkeiten hinzu, und Helfer im Konstruktor erlauben Tests mit Attrappen.'),
    say('pom', 'Page objects', 'A page object keeps the locators of one page and offers methods with business names. Tests call the methods, never the selectors.',
        'Page object एक page के locators रखता है और business नामों वाली methods देता है। Tests methods call करते हैं, selectors नहीं।',
        'Page object ಒಂದು page ನ locators ಇಡುತ್ತದೆ ಮತ್ತು business ಹೆಸರಿನ methods ಕೊಡುತ್ತದೆ. Tests methods ಅನ್ನು ಕರೆಯುತ್ತವೆ.',
        'Page object ଗୋଟିଏ page ର locators ରଖେ ଏବଂ business ନାମର methods ଦିଏ। Tests methods କୁ call କରନ୍ତି, selectors ନୁହେଁ।',
        'يحفظ كائن الصفحة محددات صفحة واحدة ويقدم دوال بأسماء من لغة العمل. تستدعي الاختبارات الدوال لا المحددات.',
        'Ein Page Object hält die Locators einer Seite und bietet Methoden mit fachlichen Namen. Tests rufen Methoden auf, keine Selektoren.'),
    say('scenario', 'Scenario', 'A builder makes test users from defaults, and an API client base class keeps the HTTP code in one place.',
        'Builder defaults से test users बनाता है, और API client base class HTTP code को एक जगह रखता है।',
        'Builder defaults ನಿಂದ test users ಮಾಡುತ್ತದೆ, API client base class HTTP code ಅನ್ನು ಒಂದೇ ಕಡೆ ಇಡುತ್ತದೆ.',
        'Builder defaults ରୁ test users ତିଆରି କରେ, ଏବଂ API client base class HTTP code କୁ ଗୋଟିଏ ସ୍ଥାନରେ ରଖେ।',
        'ينشئ الباني مستخدمي اختبار من القيم الافتراضية، ويحفظ صنف عميل الواجهة الأساسي كود HTTP في مكان واحد.',
        'Ein Builder erzeugt Testnutzer aus Standardwerten, und eine API-Client-Basisklasse hält den HTTP-Code an einer Stelle.'),
    say('practice', 'Hands-on', 'Practise a class with a getter, private state, a subclass and a small page object.',
        'Getter वाली class, private state, subclass और एक छोटे page object का अभ्यास करें।',
        'Getter ಇರುವ class, private state, subclass ಮತ್ತು ಚಿಕ್ಕ page object ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Getter ଥିବା class, private state, subclass ଓ ଛୋଟ page object ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على صنف بدالة جلب وحالة خاصة وصنف فرعي وكائن صفحة صغير.',
        'Übe eine Klasse mit Getter, privatem Zustand, einer Unterklasse und einem kleinen Page Object.'),
]

QUIZ = [
    quiz('e', 'What does a getter like get total() let you write?', ['cart.total, without brackets', 'cart.total()', 'cart.getTotal()', 'Cart.total'], 0, 'It is read like a property.', 'A getter runs a function each time the property is read.'),
    quiz('e', 'Where does a static method live?', ['On the class itself', 'On every object', 'On Object.prototype', 'Only inside the constructor'], 0, 'Cart.fromJSON(json).', 'Static members are called on the class, not on objects made from it.'),
    quiz('e', 'In the Page Object Model, where do selectors belong?', ['In the page object class', 'In every test', 'In the CI file', 'In the HTML report'], 0, 'One place to change.', 'Tests call page object methods. Only the page object knows the selectors.'),
    quiz('m', 'What happens when code outside the class reads acc.#balance?', ['A SyntaxError before anything runs', 'It returns undefined', 'It returns the balance', 'A warning is printed'], 0, 'Private names are checked when the code is parsed.', 'Referring to a private name outside its class is a syntax error.'),
    quiz('m', 'What must a subclass constructor do before using this?', ['Call super()', 'Call new', 'Return this', 'Nothing special'], 0, 'The parent sets up the object first.', 'Until <code>super()</code> runs, <code>this</code> does not exist and using it throws a ReferenceError.'),
    quiz('m', 'Which assertion belongs in a test, not in a page object?', ['expect(login.error).toHaveText("Wrong email or password")', 'this.submit = page.getByRole("button")', 'await this.email.fill(email)', 'async goto() { await this.page.goto("/login") }'], 0, 'Page objects act, tests judge.', 'Keeping assertions in tests lets page objects be reused by tests that expect different outcomes.'),
    quiz('h', 'increment is a normal class method that uses this. What happens here?', ['TypeError, because this is undefined', 'It increments counter', 'It increments a global', 'Nothing'], 0, 'Class bodies are strict.', 'Detached methods lose their object, and strict mode leaves <code>this</code> undefined.', code='const { increment } = counter;\nincrement();'),
    quiz('h', 'What does #balance in obj check?', ['Whether obj was created by the class that declares #balance', 'Whether obj has a public balance', 'Whether balance is zero', 'Whether obj is frozen'], 0, 'A brand check.', 'It returns true only for objects that have the private field, without throwing for others.'),
    quiz('h', 'Why pass a transport into an ApiClient constructor instead of calling fetch inside?', ['Tests can pass a fake transport', 'fetch does not work in classes', 'It makes the code faster', 'It is required by JavaScript'], 0, 'Dependency injection.', 'Injected helpers can be swapped for fakes, so the client can be tested without a network.'),
    quiz('x', 'Object.getPrototypeOf(Dog.prototype) === Animal.prototype when Dog extends Animal. What else is true?', ['Object.getPrototypeOf(Dog) === Animal', 'Dog.prototype === Animal.prototype', 'Animal instanceof Dog', 'Dog has no prototype'], 0, 'Static members are inherited too.', 'extends links both the prototypes and the classes themselves, so static methods are inherited.'),
    quiz('x', 'Why are class methods placed on the prototype instead of on each object?', ['One shared copy saves memory and can be changed in one place', 'Objects cannot hold functions', 'It makes them private', 'It is needed for JSON'], 0, 'a.greet === b.greet.', 'Every object finds the same function through the prototype chain.'),
    quiz('x', 'What does new Error("x", { cause: low }) add?', ['A cause property holding the original error', 'A stack of every error ever thrown', 'An automatic retry', 'A status code'], 0, 'ES2022 error cause.', 'The <code>cause</code> option keeps the lower level error, so reports show the full story.'),
]

CALC = [
    calc('e', 'A cart holds 3 pens at 20 and 1 book at 250. What does cart.total return?', '310', 'Price times quantity, added up.', ['<span class="eq">3 × 20 = 60</span>', '<span class="eq">60 + 250 = 310</span>']),
    calc('e', 'How many steps up the prototype chain is breathe from dog, if breathe is on animal and dog = Object.create(animal)?', '1', 'Count the links.', ['dog has no breathe.', 'Its prototype animal does, one step up.']),
    calc('m', 'Three BankAccount objects are created. What is BankAccount.count?', '3', 'The static counter grows in the constructor.', ['Each constructor call adds 1 to the static #count.']),
    calc('m', 'A suite has 40 tests that click the Sign in button. The button label changes. How many files change with a page object?', '1', 'Where does the locator live?', ['Only the page object holds the locator, so one file changes.']),
    calc('h', 'The builder created 2 users. What number is in the email of the next user it builds?', '3', 'The static sequence goes up on every build.', ['Each build adds 1 to #seq.', 'After 2 builds, the next build gives id 3 and user3@test.example.']),
    calc('h', 'What does this log?', '2', 'The arrow keeps its object.', ['incrementArrow runs twice on c.', 'The detached normal method is never called.'], code='class Counter {\n  count = 0;\n  incrementArrow = () => { this.count++; };\n}\nconst c = new Counter();\nconst { incrementArrow } = c;\nincrementArrow();\nincrementArrow();\nconsole.log(c.count);'),
    calc('x', 'Which status codes make HttpError.retryable true among 404, 429, 500 and 503? Answer with how many.', '3', 'status >= 500 or status === 429.', ['429 is true.', '500 and 503 are true.', '404 is false.']),
    calc('x', 'Dog extends Animal. How many prototype objects are checked to find hasOwnProperty on a Dog object, counting the one where it is found?', '3', 'Dog.prototype, Animal.prototype, then Object.prototype.', ['The dog object itself does not have it.', 'Dog.prototype and Animal.prototype do not have it either.', 'Object.prototype does, so 3 prototype objects are checked.']),
]

EX = [
    ex('rect', 'e', 'A rectangle class', '<p>Write a class <code>Rectangle</code> with a constructor <code>(width, height)</code>, a getter <code>area</code> and a method <code>scale(factor)</code> that multiplies both sides and returns <code>this</code>.</p>',
       'class Rectangle {\n  constructor(width, height) {\n    \n  }\n}\n',
       [('new Rectangle(3, 4).area', 12), ('new Rectangle(2, 5).scale(2).area', 40), ('(() => { const r = new Rectangle(1, 1); return r.scale(3) === r; })()', True)],
       'class Rectangle {\n  constructor(width, height) {\n    this.width = width;\n    this.height = height;\n  }\n  get area() {\n    return this.width * this.height;\n  }\n  scale(factor) {\n    this.width *= factor;\n    this.height *= factor;\n    return this;\n  }\n}',
       hint='Store the sides on <code>this</code>. A getter is <code>get area() { ... }</code>.', why='Returning <code>this</code> from <code>scale</code> lets callers chain calls, the same trick builders use.'),
    ex('stack', 'm', 'A stack with private storage', '<p>Write a class <code>Stack</code> with a private array, methods <code>push(x)</code> and <code>pop()</code>, and a getter <code>size</code>. <code>pop()</code> on an empty stack returns <code>undefined</code>. The array must not be visible from outside, so <code>Object.keys(stack)</code> is empty.</p>',
       'class Stack {\n  \n}\n',
       [('(() => { const s = new Stack(); s.push(1); s.push(2); return [s.pop(), s.size]; })()', [2, 1]),
        ('(() => { const s = new Stack(); return s.pop() === undefined && s.size === 0; })()', True),
        ('(() => { const s = new Stack(); s.push(5); return Object.keys(s); })()', [])],
       'class Stack {\n  #items = [];\n  push(x) {\n    this.#items.push(x);\n  }\n  pop() {\n    return this.#items.pop();\n  }\n  get size() {\n    return this.#items.length;\n  }\n}',
       hint='Declare <code>#items = [];</code> as a field.', why='Private fields never show up in <code>Object.keys</code>, so no outside code can reach in and break the stack.'),
    ex('errors', 'h', 'A custom error class', '<p>Write <code>class ValidationError extends Error</code> with a constructor <code>(field, message)</code>. It sets <code>name</code> to <code>"ValidationError"</code>, stores <code>field</code>, and its message is <code>"field: message"</code>. Then write <code>check(user)</code> that throws a ValidationError for field <code>"email"</code> with message <code>"is required"</code> when <code>user.email</code> is missing, and returns <code>true</code> otherwise.</p>',
       'class ValidationError extends Error {\n  \n}\n\nfunction check(user) {\n  \n}\n',
       [('(() => { try { check({}); } catch (e) { return [e instanceof ValidationError, e instanceof Error, e.name, e.field, e.message]; } })()', [True, True, 'ValidationError', 'email', 'email: is required']),
        ('check({ email: "a@b.c" })', True)],
       'class ValidationError extends Error {\n  constructor(field, message) {\n    super(`${field}: ${message}`);\n    this.name = "ValidationError";\n    this.field = field;\n  }\n}\n\nfunction check(user) {\n  if (!user.email) throw new ValidationError("email", "is required");\n  return true;\n}',
       hint='Call <code>super(...)</code> with the full message first, then set the extra properties.', why='Tests can now check <code>instanceof ValidationError</code> and the field, which is much clearer than matching message text.'),
    ex('page-object', 'x', 'A page object for a search box', '<p>Write a class <code>SearchPage</code> whose constructor takes a <code>driver</code> object with two async methods: <code>fill(selector, text)</code> and <code>textOf(selector)</code>, plus <code>click(selector)</code>. Add <code>async search(term)</code> that fills <code>"#q"</code> with the term and clicks <code>"#go"</code>, and <code>async resultCount()</code> that reads <code>".count"</code> such as <code>"12 results"</code> and returns the number <code>12</code>.</p>',
       'class SearchPage {\n  constructor(driver) {\n    \n  }\n}\n',
       [('(async () => { const calls = []; const driver = { fill: async (s, t) => calls.push(["fill", s, t]), click: async s => calls.push(["click", s]), textOf: async s => "12 results" }; const p = new SearchPage(driver); await p.search("pens"); return [calls, await p.resultCount()]; })()',
         [[['fill', '#q', 'pens'], ['click', '#go']], 12]),
        ('(async () => { const p = new SearchPage({ textOf: async () => "0 results" }); return await p.resultCount(); })()', 0)],
       'class SearchPage {\n  constructor(driver) {\n    this.driver = driver;\n  }\n  async search(term) {\n    await this.driver.fill("#q", term);\n    await this.driver.click("#go");\n  }\n  async resultCount() {\n    const text = await this.driver.textOf(".count");\n    return parseInt(text, 10);\n  }\n}',
       hint='Store the driver on <code>this</code>, and <code>await</code> each driver call in order. <code>parseInt("12 results", 10)</code> gives 12.',
       why='The test passed a fake driver, which is exactly how page objects are unit tested. The same class would work with a real Playwright or Selenium wrapper.'),
]

T = {
    'slug': 'js-oop', 'title': 'Prototypes, Classes and the Page Object Model', 'short': 'Classes and OOP', 'emoji': '🏛️', 'module': MODULE, 'minutes': 17,
    'lead': 'How objects borrow from prototypes, classes with fields, getters, static and private members, inheritance with extends and super, custom errors, composition, and the Page Object Model that most UI test frameworks are built on.',
    'desc': 'Prototypes, constructor functions, classes, getters, static members, private fields, extends, super, custom errors, mixins, composition and the Page Object Model.',
    'summary': 'The prototype chain, constructor functions and new, classes with fields, getters and static methods, lost this and other class traps, private fields and static blocks, inheritance with extends and super, custom error classes with cause, mixins and dependency injection, the Page Object Model in plain DOM, Playwright and Selenium, a test data builder and an API client class.',
    'keywords': ['prototype', 'class', 'constructor', 'getter', 'static', 'private field', 'extends', 'super', 'custom error', 'mixin', 'composition', 'dependency injection', 'Page Object Model', 'POM', 'builder pattern'],
    'qa_intro': 'Page objects, API clients, test data builders and custom errors are all classes. This chapter is the base for the framework design in chapter 21.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
