# Chapter 11: the DOM, selectors and XPath, changing the page, events, forms, shadow DOM, iframes, observers, storage and cookies.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('⏳', 'Async and the platform', 'js-platform', 'Promises and the event loop, the browser DOM, and HTTP from both sides: everything a UI or API test waits for.')

SHOP = '''
<!doctype html>
<html>
<body>
  <header><nav aria-label="Main"><a href="/">Home</a> <a href="/deals" class="hot">Deals</a></nav></header>
  <main id="products">
    <article class="card" data-test="product" data-sku="PEN-01">
      <h2>Gel pen</h2><span class="price">₹20</span>
      <button type="button" class="add">Add to cart</button>
    </article>
    <article class="card sold-out" data-test="product" data-sku="BOOK-07">
      <h2>Notebook</h2><span class="price">₹250</span>
      <button type="button" class="add" disabled>Sold out</button>
    </article>
    <article class="card" data-test="product" data-sku="MUG-03">
      <h2>Coffee mug</h2><span class="price">₹199</span>
      <button type="button" class="add">Add to cart</button>
    </article>
  </main>
  <p id="cart-count">0</p>
</body>
</html>
'''

FORM = '''
<!doctype html>
<html>
<body>
  <form id="signup" novalidate>
    <label for="email">Email</label>
    <input id="email" name="email" type="email" required>
    <label for="age">Age</label>
    <input id="age" name="age" type="number" min="18" max="120">
    <label><input type="checkbox" name="terms" id="terms" required> I accept the terms</label>
    <select id="plan" name="plan">
      <option value="free">Free</option>
      <option value="pro" selected>Pro</option>
    </select>
    <button>Create account</button>
  </form>
</body>
</html>
'''

CODES = {
    'tree': dom(SHOP, '''
console.log(document.title === "", document.body.children.length);

const main = document.getElementById("products");
const firstCard = main.querySelector(".card");               // the first match
const allCards = main.querySelectorAll(".card");              // a static NodeList
console.log(firstCard.querySelector("h2").textContent, allCards.length);

// Walk around the tree
const price = firstCard.querySelector(".price");
console.log(price.parentElement.dataset.sku);                 // up
console.log(price.previousElementSibling.textContent);        // sideways
console.log(price.closest("main").id);                        // nearest ancestor that matches
console.log([...allCards].map(c => c.dataset.sku));
''', 'Finding elements and walking the tree'),
    'selectors': dom(SHOP, '''
const q = s => document.querySelectorAll(s).length;

console.log("by tag:            ", q("article"));
console.log("by class:          ", q(".card"));
console.log("two classes:       ", q(".card.sold-out"));
console.log("attribute:         ", q('[data-test="product"]'));
console.log("attribute prefix:  ", q('[data-sku^="PEN"]'));
console.log("child of:          ", q("main > article"));
console.log("not:               ", q(".card:not(.sold-out)"));
console.log("nth:               ", document.querySelector(".card:nth-of-type(3) h2").textContent);
console.log("has (parent by child):", q("article:has(button:disabled)"));
console.log("enabled buttons:   ", q("button.add:enabled"));
''', 'CSS selectors for finding elements'),
    'xpath': dom(SHOP, '''
function xpath(expr, context = document) {
  const r = document.evaluate(expr, context, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
  return Array.from({ length: r.snapshotLength }, (_, i) => r.snapshotItem(i));
}

// Find by visible text, which CSS cannot do
console.log(xpath("//h2[text()='Coffee mug']").length);
// Go up to the card that contains that heading, then down to its button
console.log(xpath("//h2[text()='Coffee mug']/ancestor::article//button")[0].textContent);
// Contains, and an index
console.log(xpath("//button[contains(., 'Sold')]").map(b => b.disabled));
console.log(xpath("(//span[@class='price'])[last()]")[0].textContent);
''', 'XPath, used by Selenium and others'),
    'change': dom(SHOP, '''
const card = document.querySelector('[data-sku="PEN-01"]');

card.querySelector("h2").textContent = "Gel pen (blue)";   // safe: plain text only
card.classList.add("in-cart");
card.classList.toggle("highlight");
card.setAttribute("aria-label", "Gel pen, in cart");
card.dataset.qty = "2";                                    // becomes data-qty="2"
console.log(card.className, card.getAttribute("data-qty"));

const badge = document.createElement("span");
badge.className = "badge";
badge.textContent = "New";
card.prepend(badge);
console.log(card.firstElementChild.outerHTML);

const userInput = '<img src=x onerror="alert(1)">';
const safe = document.createElement("p");
safe.textContent = userInput;                              // shown as text, never run
console.log(safe.innerHTML);

document.querySelector(".sold-out").remove();
console.log(document.querySelectorAll(".card").length);
''', 'Changing text, classes, attributes and elements'),
    'events': dom(SHOP, '''
const count = document.querySelector("#cart-count");

// One listener on the parent handles every button, even ones added later
document.querySelector("#products").addEventListener("click", event => {
  const button = event.target.closest("button.add");
  if (!button || button.disabled) return;
  const sku = button.closest("[data-sku]").dataset.sku;
  count.textContent = Number(count.textContent) + 1;
  console.log(`added ${sku}, target was <${event.target.tagName.toLowerCase()}>, listener on #${event.currentTarget.id}`);
});

document.querySelector('[data-sku="PEN-01"] button').click();
document.querySelector('[data-sku="MUG-03"] button').click();
document.querySelector('[data-sku="BOOK-07"] button').click();   // disabled: click() does nothing
console.log("cart count:", count.textContent);

// A link whose default action is stopped
const deals = document.querySelector("a.hot");
deals.addEventListener("click", e => { e.preventDefault(); console.log("navigation prevented"); });
deals.click();

// Custom events let parts of a page talk to each other
document.addEventListener("cart:changed", e => console.log("custom event:", e.detail));
document.dispatchEvent(new CustomEvent("cart:changed", { detail: { items: 2 } }));
console.log("isTrusted for script events:", new MouseEvent("click").isTrusted);
''', 'Listening for events and event delegation'),
    'forms': dom(FORM, '''
const form = document.querySelector("#signup");
const email = form.elements.email;

email.value = "not-an-email";
form.elements.age.value = "15";
console.log("valid form:", form.checkValidity());
for (const field of form.elements) {
  if (!field.name || field.validity.valid) continue;
  const problem = ["valueMissing", "typeMismatch", "rangeUnderflow", "rangeOverflow"].find(k => field.validity[k]);
  console.log(`  ${field.name}: ${problem}`);
}

email.value = "asha@shop.example";
form.elements.age.value = "29";
form.elements.terms.checked = true;
form.elements.plan.value = "free";
console.log("valid form:", form.checkValidity());

form.addEventListener("submit", e => {
  e.preventDefault();
  console.log("submitted:", Object.fromEntries(new FormData(form)));
});
form.requestSubmit();
''', 'Form values and built in validation'),
    'shadow': dom('''
<!doctype html>
<html><body>
  <user-card name="Asha"></user-card>
  <iframe id="pay"></iframe>
</body></html>
''', '''
class UserCard extends HTMLElement {
  connectedCallback() {
    const root = this.attachShadow({ mode: "open" });
    root.innerHTML = `<p class="name">${this.getAttribute("name")}</p><button>Follow</button>`;
  }
}
customElements.define("user-card", UserCard);

console.log("normal query finds:", document.querySelector("user-card .name"));
const host = document.querySelector("user-card");
console.log("through shadowRoot:", host.shadowRoot.querySelector(".name").textContent);

// An iframe has its own document. You must step into it first.
const frame = document.querySelector("#pay");
frame.contentDocument.body.innerHTML = "<button id='pay-now'>Pay ₹499</button>";   // the provider's page
console.log("button in main page:", document.querySelector("#pay-now"));
console.log("button in iframe:", frame.contentDocument.querySelector("#pay-now").textContent);
''', 'Shadow DOM and iframes', play=False),
    'observer': dom('''
<!doctype html>
<html><body><div id="results"></div></body></html>
''', '''
// Resolve when an element matching the selector exists, or reject after a timeout
function waitForElement(selector, timeout = 1000) {
  return new Promise((resolve, reject) => {
    const found = document.querySelector(selector);
    if (found) return resolve(found);
    const observer = new MutationObserver(() => {
      const el = document.querySelector(selector);
      if (el) { observer.disconnect(); clearTimeout(timer); resolve(el); }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    const timer = setTimeout(() => { observer.disconnect(); reject(new Error(`${selector} not found in ${timeout} ms`)); }, timeout);
  });
}

// The "app" renders results after a fake network delay
setTimeout(() => {
  document.querySelector("#results").innerHTML = '<ul class="list"><li>Gel pen</li><li>Fountain pen</li></ul>';
}, 200);

const list = await waitForElement(".list");
console.log("appeared with", list.children.length, "items");
await waitForElement(".no-such-thing", 300).catch(e => console.log(e.message));
''', 'Waiting for an element with MutationObserver'),
    'storage': dom('<!doctype html><html><body></body></html>', '''
localStorage.setItem("theme", "dark");
localStorage.setItem("cart", JSON.stringify([{ sku: "PEN-01", qty: 2 }]));   // only strings are stored
console.log(localStorage.getItem("theme"), localStorage.length);
console.log(JSON.parse(localStorage.getItem("cart"))[0].qty);
console.log(localStorage.getItem("missing"));

sessionStorage.setItem("step", "3");          // cleared when the tab closes
console.log(sessionStorage.getItem("step"));

localStorage.removeItem("theme");
localStorage.clear();
console.log(localStorage.length);
''', 'localStorage and sessionStorage'),
    'cookies': dom('<!doctype html><html><body></body></html>', '''
document.cookie = "consent=yes; path=/; max-age=31536000; SameSite=Lax";
document.cookie = "lang=hi; path=/";
document.cookie = `recent=${encodeURIComponent("pen, mug")}; path=/`;
console.log(document.cookie);

const cookies = Object.fromEntries(document.cookie.split("; ").map(c => {
  const i = c.indexOf("=");
  return [c.slice(0, i), decodeURIComponent(c.slice(i + 1))];
}));
console.log(cookies.recent);

document.cookie = "lang=; path=/; max-age=0";    // delete by expiring it
console.log(document.cookie.includes("lang"));
''', 'Reading and writing cookies', play=False),
    'pw-state': show('''
// Log in once, save cookies and localStorage, reuse them in every test
// auth.setup.js
import { test as setup } from "@playwright/test";
setup("log in", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill(process.env.TEST_USER);
  await page.getByLabel("Password").fill(process.env.TEST_PASSWORD);
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.context().storageState({ path: ".auth/user.json" });
});

// in a test: read and change browser state directly
await page.evaluate(() => localStorage.setItem("onboarding-done", "true"));
const cookies = await page.context().cookies();
await page.context().addCookies([{ name: "consent", value: "yes", url: "https://shop.example" }]);
''', 'Browser state in Playwright', note='Runs for real in {{ch:js-ui-automation}}', result='Tests start already logged in, which saves the login steps in every test and keeps them independent.'),
    'scenario': dom('''
<!doctype html>
<html><body>
<table id="orders">
  <thead><tr><th>Order</th><th>Item</th><th>Qty</th><th>Price</th><th>Line total</th></tr></thead>
  <tbody>
    <tr><td>#1042</td><td>Gel pen</td><td>3</td><td>₹20.00</td><td>₹60.00</td></tr>
    <tr><td>#1043</td><td>Coffee mug</td><td>2</td><td>₹199.00</td><td>₹398.00</td></tr>
    <tr><td>#1044</td><td>Notebook</td><td>1</td><td>₹250.00</td><td>₹250.00</td></tr>
    <tr><td>#1045</td><td>Desk lamp</td><td>2</td><td>₹1,299.00</td><td>₹2,589.00</td></tr>
  </tbody>
  <tfoot><tr><td colspan="4">Total</td><td>₹3,297.00</td></tr></tfoot>
</table>
</body></html>
''', '''
const money = text => Number(text.replace(/[^\\d.]/g, ""));
const headers = [...document.querySelectorAll("#orders thead th")].map(th => th.textContent);
const rows = [...document.querySelectorAll("#orders tbody tr")].map(tr =>
  Object.fromEntries([...tr.cells].map((td, i) => [headers[i], td.textContent])));

const problems = [];
for (const r of rows) {
  const expected = Number(r.Qty) * money(r.Price);
  if (expected !== money(r["Line total"])) {
    problems.push(`${r.Order}: ${r.Qty} x ${r.Price} should be ${expected}, page shows ${r["Line total"]}`);
  }
}
const sum = rows.reduce((s, r) => s + money(r["Line total"]), 0);
const shownTotal = money(document.querySelector("#orders tfoot td:last-child").textContent);
if (sum !== shownTotal) problems.push(`total: rows add up to ${sum}, footer shows ${shownTotal}`);

console.log(rows.length, "rows checked");
console.log(problems.length ? problems : "all good");
''', 'Check every row of an order table'),
}

PARTS = [
    part('dom', '🌳', 'The DOM tree', '''
<p>When a browser loads HTML, it builds the <b>DOM</b> (Document Object Model): a tree of objects, one for each element, piece of text and comment. JavaScript reads and changes the page only through this tree, and so does every UI automation tool.</p>
[[tree]]
<div class="tw"><table class="jt"><tr><th>Method</th><th>Returns</th></tr>
<tr><td><code>getElementById("x")</code></td><td>one element or <code>null</code></td></tr>
<tr><td><code>querySelector(css)</code></td><td>the first match or <code>null</code></td></tr>
<tr><td><code>querySelectorAll(css)</code></td><td>a NodeList of every match, possibly empty</td></tr>
<tr><td><code>el.closest(css)</code></td><td>the element itself or its nearest ancestor that matches</td></tr>
<tr><td><code>parentElement</code>, <code>children</code>, <code>nextElementSibling</code></td><td>neighbours in the tree</td></tr>
</table></div>
''', qa=True, qa_why='Every locator in Selenium, Playwright and Cypress finds nodes in this tree.',
        kw=['DOM', 'document', 'element', 'node', 'tree', 'getElementById', 'querySelector', 'querySelectorAll', 'closest', 'NodeList', 'parentElement']),
    part('selectors', '🎯', 'Selectors and locators', '''
<p>A <b>CSS selector</b> describes elements by tag, id, class, attribute and position. The same selector works in <code>document.querySelector</code>, in your stylesheet and in every test tool.</p>
[[selectors]]
<p><b>XPath</b> is an older query language for the same tree. It can find elements by their text and step up to ancestors, which CSS cannot. Selenium supports it fully and many older suites use it.</p>
[[xpath]]
<h3>Which locator to choose</h3>
<div class="tw"><table class="jt"><tr><th>Locator</th><th>Example</th><th>Stability</th></tr>
<tr><td>Role and name (what a user sees)</td><td><code>getByRole("button", { name: "Add to cart" })</code></td><td>best: survives layout and styling changes</td></tr>
<tr><td>Label or text</td><td><code>getByLabel("Email")</code>, <code>getByText("Deals")</code></td><td>good, changes with the wording</td></tr>
<tr><td>Test id</td><td><code>[data-test="product"]</code>, <code>getByTestId</code></td><td>good, made for tests</td></tr>
<tr><td>Short CSS</td><td><code>.card .price</code></td><td>fair, breaks when classes change</td></tr>
<tr><td>Long CSS or XPath by position</td><td><code>/html/body/main/article[3]/button</code></td><td>poor, breaks with any layout change</td></tr>
</table></div>
''', qa=['Playwright', 'Selenium', 'Cypress', 'WebdriverIO'], qa_why='Choosing stable locators decides how often your UI tests break.',
        kw=['CSS selector', 'locator', 'XPath', 'attribute selector', ':has', ':not', 'nth-of-type', 'data-test', 'data-testid', 'getByRole', 'getByText', 'stable locators', 'ancestor']),
    part('change', '✏️', 'Changing the page', '''
<p>Elements can be changed in place: their text, classes, attributes and children. <code>textContent</code> sets plain text and is always safe. <code>innerHTML</code> parses HTML, so putting user input into it can run an attacker's code, a bug called <b>cross site scripting</b> (XSS).</p>
[[change]]
<div class="tw"><table class="jt"><tr><th>Property</th><th>Reads or writes</th></tr>
<tr><td><code>textContent</code></td><td>all text, including hidden elements, fast</td></tr>
<tr><td><code>innerText</code></td><td>only the text a user can see, with layout applied (what Selenium's <code>getText()</code> returns)</td></tr>
<tr><td><code>innerHTML</code></td><td>the HTML inside the element</td></tr>
<tr><td><code>value</code></td><td>what is typed in an input, select or textarea</td></tr>
</table></div>
<div class="qa-box">Testers deliberately type <code>&lt;script&gt;</code> and <code>&lt;img onerror&gt;</code> payloads into forms to check that the page shows them as text. If an alert pops up, you found an XSS bug.</div>
''', kw=['textContent', 'innerText', 'innerHTML', 'classList', 'setAttribute', 'dataset', 'createElement', 'append', 'remove', 'XSS', 'cross site scripting']),
    part('events', '🖱️', 'Events', '''
<p>Clicks, key presses, input changes and form submits are <b>events</b>. <code>addEventListener(type, handler)</code> runs your function each time one happens. An event travels down from the window to the target (<b>capture</b>), then back up (<b>bubble</b>), so a listener on a parent hears clicks on its children.</p>
<div class="viz" data-viz="bubble"></div>
[[events]]
<p><b>Event delegation</b> uses this: one listener on a list handles every item, including items added later. <code>event.target</code> is what was clicked and <code>event.currentTarget</code> is where the listener sits. <code>preventDefault()</code> stops the browser's own action, such as following a link.</p>
<div class="warn">Events created by scripts have <code>isTrusted</code> set to false, and <code>element.click()</code> skips the checks a real user goes through: it works on hidden or covered buttons. That is why Playwright and Selenium move a real mouse and check that the element is visible and not covered before clicking, and why <code>{ force: true }</code> clicks can hide real bugs.</div>
''', qa=['Playwright', 'Selenium', 'Cypress'], qa_why='Understanding bubbling and trusted events explains "element click intercepted" errors and why forced clicks hide bugs.',
        kw=['event', 'addEventListener', 'click', 'capture', 'bubble', 'event delegation', 'target', 'currentTarget', 'preventDefault', 'stopPropagation', 'CustomEvent', 'dispatchEvent', 'isTrusted', 'force click']),
    part('forms', '📝', 'Forms and validation', '''
<p>Form fields hold their current value in <code>value</code> (or <code>checked</code> for checkboxes). HTML attributes such as <code>required</code>, <code>type="email"</code> and <code>min</code> give free validation, which JavaScript reads through <code>checkValidity()</code> and each field's <code>validity</code>. <code>FormData</code> collects every named field in one go.</p>
[[forms]]
<div class="qa-box">Form testing checklist: required fields, wrong formats, boundary values (17, 18, 120, 121 for an age between 18 and 120), very long text, leading and trailing spaces, pasted text, the Enter key, double submit, and the error message text. Always check the server rejects bad data too, because client side checks are easy to skip.</div>
''', qa=True, qa_why='Forms are the most tested part of any web app, and their validation rules are the source of many test cases.',
        kw=['form', 'input', 'value', 'checked', 'select', 'validation', 'checkValidity', 'validity', 'required', 'FormData', 'submit', 'requestSubmit', 'boundary values']),
    part('advanced', '🧱', 'Shadow DOM, iframes and observers', '''
<p><b>Web components</b> hide their inner elements inside a <b>shadow root</b>. A normal <code>querySelector</code> from the document cannot see inside it. An <b>iframe</b> holds a whole separate document, often for payment forms, maps or embedded editors.</p>
[[shadow]]
<div class="tw"><table class="jt"><tr><th>Tool</th><th>Shadow DOM</th><th>Iframes</th></tr>
<tr><td>Playwright</td><td>pierced automatically by most locators</td><td><code>page.frameLocator("#pay").getByRole(...)</code></td></tr>
<tr><td>Selenium</td><td><code>element.getShadowRoot()</code></td><td><code>driver.switchTo().frame(...)</code>, then back with <code>defaultContent()</code></td></tr>
<tr><td>Cypress</td><td><code>.shadow()</code> or <code>includeShadowDom</code></td><td>needs a helper or plugin, same origin only</td></tr>
</table></div>
<p>A <b>MutationObserver</b> calls you back whenever the DOM changes. It is how "wait until the element appears" is built without polling.</p>
[[observer]]
''', qa=['Playwright', 'Selenium', 'Cypress'], qa_why='Elements inside shadow roots and iframes are the most common reason a correct looking locator finds nothing.',
        kw=['shadow DOM', 'shadowRoot', 'web components', 'custom elements', 'iframe', 'contentDocument', 'frameLocator', 'switchTo frame', 'MutationObserver', 'wait for element']),
    part('storage', '🍪', 'Storage and cookies', '''
<p>Browsers keep data for a site in three main places. <b>localStorage</b> keeps strings until they are deleted. <b>sessionStorage</b> keeps them until the tab closes. <b>Cookies</b> are small strings that are also sent to the server with every request, which is why logins usually live in them.</p>
[[storage]]
[[cookies]]
<div class="warn">Cookies marked <code>HttpOnly</code> cannot be read from JavaScript at all, which protects session tokens from XSS. Test tools read them through the browser instead, for example <code>context.cookies()</code> in Playwright.</div>
[[pw-state]]
''', qa=['Playwright', 'Cypress', 'Selenium'], qa_why='Seeding storage and cookies skips slow login screens and sets up feature flags and consent banners.',
        kw=['localStorage', 'sessionStorage', 'cookie', 'document.cookie', 'HttpOnly', 'SameSite', 'storageState', 'session', 'login state']),
    part('scenario', '🎬', 'Real world scenario: check an order table', '''
<div class="scenario"><b>The situation</b>A customer says the order history shows wrong amounts. You must check every row: quantity times price must equal the line total, and the lines must add up to the footer total.</div>
[[scenario]]
<p>Reading the header cells first turns each row into an object keyed by column name, so the check keeps working if a column is added or moved. The footer does match the rows as shown, so a check of the total alone would have missed this bug. Only the line by line check catches it.</p>
''', qa=True, kw=['table', 'rows', 'cells', 'scrape', 'data validation', 'totals', 'price parsing', 'UI data check']),
]

INFO = {'title': 'The page is a tree you can query', 'panels': [
    panel([['e', '🌳'], ['t', 'document → body → main → article', {'b': 1, 'size': 11}]], 'The DOM', 'HTML becomes a tree of objects.', 'Scripts and test tools both work on this tree.'),
    panel([['e', '🎯'], ['t', 'getByRole("button")', {'b': 1}]], 'Locators', 'Find elements the way a user would.', 'Roles and test ids survive redesigns. Long paths do not.'),
    panel([['e', '🖱️'], ['t', 'capture ↓ target ↑ bubble', {'b': 1}]], 'Events', 'Clicks travel down and back up.', 'One listener on a parent can handle all its children.'),
    panel([['e', '🍪'], ['t', 'cookies, localStorage', {'b': 1}]], 'State', 'The browser remembers things for each site.', 'Tests seed it to skip logins and banners.')],
    'remember': 'Find with stable locators, act like a user, and check what the user would see.'}

REAL = [
    ['🛒', 'Add to cart', 'A product grid with 200 items uses one delegated click listener instead of 200, and its buttons carry data-test attributes for the test suite.'],
    ['💳', 'A payment iframe', 'The card form comes from the payment provider inside an iframe, so the checkout test switches into the frame to fill it.'],
    ['🧾', 'Report checks', 'A nightly script opens the admin dashboard and checks that every table row adds up, catching a rounding bug before customers do.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers the DOM, selectors and XPath, changing the page, events, forms, shadow DOM, iframes, storage and cookies.',
        'यह अध्याय DOM, selectors और XPath, page बदलना, events, forms, shadow DOM, iframes, storage और cookies सिखाता है।',
        'ಈ ಅಧ್ಯಾಯ DOM, selectors ಮತ್ತು XPath, page ಬದಲಾವಣೆ, events, forms, shadow DOM, iframes, storage ಮತ್ತು cookies ಕಲಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ DOM, selectors ଓ XPath, page ବଦଳାଇବା, events, forms, shadow DOM, iframes, storage ଓ cookies ଶିଖାଏ।',
        'يتناول هذا الفصل DOM والمحددات وXPath وتغيير الصفحة والأحداث والنماذج وShadow DOM والإطارات والتخزين وملفات تعريف الارتباط.',
        'Dieses Kapitel behandelt das DOM, Selektoren und XPath, Seitenänderungen, Events, Formulare, Shadow DOM, iframes, Speicher und Cookies.'),
    say('dom', 'The DOM', 'The browser turns HTML into a tree of objects. querySelector, closest and the parent and child properties move around it.',
        'Browser HTML को objects के tree में बदलता है। querySelector, closest और parent, child properties उसमें घूमते हैं।',
        'Browser HTML ಅನ್ನು objects tree ಆಗಿ ಮಾಡುತ್ತದೆ. querySelector, closest ಮತ್ತು parent, child properties ಅದರಲ್ಲಿ ಚಲಿಸುತ್ತವೆ.',
        'Browser HTML କୁ objects ର tree କରେ। querySelector, closest ଓ parent, child properties ସେଥିରେ ଘୁରନ୍ତି।',
        'يحول المتصفح HTML إلى شجرة كائنات. تتنقل فيها querySelector وclosest وخصائص الأب والأبناء.',
        'Der Browser macht aus HTML einen Objektbaum. querySelector, closest und Eltern- und Kind-Eigenschaften bewegen sich darin.'),
    say('selectors', 'Selectors', 'CSS selectors and XPath find elements. Prefer roles, labels and test ids, because long paths break with every layout change.',
        'CSS selectors और XPath elements ढूंढते हैं। Roles, labels और test ids चुनें, क्योंकि लंबे paths हर layout बदलाव पर टूटते हैं।',
        'CSS selectors ಮತ್ತು XPath elements ಹುಡುಕುತ್ತವೆ. Roles, labels ಮತ್ತು test ids ಆಯ್ಕೆ ಮಾಡಿ, ಉದ್ದ paths layout ಬದಲಾದಾಗ ಮುರಿಯುತ್ತವೆ.',
        'CSS selectors ଓ XPath elements ଖୋଜନ୍ତି। Roles, labels ଓ test ids ବାଛନ୍ତୁ, ଲମ୍ବା paths layout ବଦଳିଲେ ଭାଙ୍ଗେ।',
        'تجد محددات CSS وXPath العناصر. فضّل الأدوار والتسميات ومعرفات الاختبار، لأن المسارات الطويلة تنكسر مع كل تغيير في التخطيط.',
        'CSS-Selektoren und XPath finden Elemente. Bevorzuge Rollen, Labels und Test-IDs, lange Pfade brechen bei jeder Layoutänderung.'),
    say('change', 'Changing the page', 'textContent writes safe plain text. innerHTML parses HTML, so user input there can cause cross site scripting.',
        'textContent सुरक्षित plain text लिखता है। innerHTML HTML parse करता है, इसलिए वहां user input से XSS हो सकता है।',
        'textContent ಸುರಕ್ಷಿತ plain text ಬರೆಯುತ್ತದೆ. innerHTML HTML parse ಮಾಡುತ್ತದೆ, ಅಲ್ಲಿ user input XSS ಉಂಟುಮಾಡಬಹುದು.',
        'textContent ସୁରକ୍ଷିତ plain text ଲେଖେ। innerHTML HTML parse କରେ, ତେଣୁ ସେଠାରେ user input XSS ଘଟାଇପାରେ।',
        'تكتب textContent نصًا آمنًا. أما innerHTML فتحلل HTML، لذا قد يسبب إدخال المستخدم فيها ثغرة XSS.',
        'textContent schreibt sicheren Text. innerHTML parst HTML, Nutzereingaben dort können Cross-Site-Scripting auslösen.'),
    say('events', 'Events', 'Events travel down to the target and bubble back up. One listener on a parent can handle all children. Script clicks skip real user checks.',
        'Events target तक नीचे जाते हैं और फिर ऊपर bubble होते हैं। Parent पर एक listener सभी children संभाल सकता है।',
        'Events target ವರೆಗೆ ಕೆಳಗೆ ಹೋಗಿ ಮತ್ತೆ ಮೇಲೆ bubble ಆಗುತ್ತವೆ. Parent ಮೇಲಿನ ಒಂದು listener ಎಲ್ಲ children ನೋಡಿಕೊಳ್ಳಬಹುದು.',
        'Events target ପର୍ଯ୍ୟନ୍ତ ତଳକୁ ଯାଇ ପୁଣି ଉପରକୁ bubble ହୁଅନ୍ତି। Parent ରେ ଗୋଟିଏ listener ସବୁ children ସମ୍ଭାଳିପାରେ।',
        'تنتقل الأحداث نزولًا إلى الهدف ثم تصعد. يمكن لمستمع واحد على الأب معالجة كل الأبناء. نقرات السكربت تتجاوز فحوص المستخدم الحقيقي.',
        'Events laufen zum Ziel hinab und steigen wieder auf. Ein Listener am Elternelement kann alle Kinder bedienen.'),
    say('forms', 'Forms', 'Fields hold their value, HTML attributes give free validation, and FormData collects every field. Test boundaries and the server too.',
        'Fields अपनी value रखते हैं, HTML attributes मुफ्त validation देते हैं, और FormData सब fields इकट्ठा करता है।',
        'Fields ತಮ್ಮ value ಇಡುತ್ತವೆ, HTML attributes ಉಚಿತ validation ಕೊಡುತ್ತವೆ, FormData ಎಲ್ಲ fields ಸಂಗ್ರಹಿಸುತ್ತದೆ.',
        'Fields ନିଜ value ରଖନ୍ତି, HTML attributes ମାଗଣା validation ଦିଅନ୍ତି, ଏବଂ FormData ସବୁ fields ସଂଗ୍ରହ କରେ।',
        'تحفظ الحقول قيمها، وتعطي سمات HTML تحققًا مجانيًا، وتجمع FormData كل الحقول. اختبر الحدود والخادم أيضًا.',
        'Felder halten ihren Wert, HTML-Attribute validieren kostenlos, FormData sammelt alle Felder. Teste Grenzwerte und den Server.'),
    say('advanced', 'Shadow DOM and iframes', 'Shadow roots and iframes hide elements from normal queries. Test tools have special ways to reach inside them.',
        'Shadow roots और iframes elements को सामान्य queries से छिपाते हैं। Test tools के पास अंदर पहुंचने के खास तरीके हैं।',
        'Shadow roots ಮತ್ತು iframes elements ಅನ್ನು ಸಾಮಾನ್ಯ queries ನಿಂದ ಮರೆಮಾಡುತ್ತವೆ. Test tools ಒಳಗೆ ತಲುಪಲು ವಿಶೇಷ ದಾರಿ ಹೊಂದಿವೆ.',
        'Shadow roots ଓ iframes elements କୁ ସାଧାରଣ queries ରୁ ଲୁଚାନ୍ତି। Test tools ଭିତରେ ପହଞ୍ଚିବାର ବିଶେଷ ଉପାୟ ଅଛି।',
        'تخفي جذور الظل والإطارات العناصر عن الاستعلامات العادية. لأدوات الاختبار طرق خاصة للوصول إليها.',
        'Shadow Roots und iframes verbergen Elemente vor normalen Abfragen. Testwerkzeuge haben eigene Wege hinein.'),
    say('storage', 'Storage', 'localStorage keeps strings, sessionStorage lasts for one tab, and cookies are sent with every request. Tests seed them to skip logins.',
        'localStorage strings रखता है, sessionStorage एक tab तक रहता है, और cookies हर request के साथ जाती हैं।',
        'localStorage strings ಇಡುತ್ತದೆ, sessionStorage ಒಂದು tab ವರೆಗೆ ಇರುತ್ತದೆ, cookies ಪ್ರತಿ request ಜೊತೆ ಹೋಗುತ್ತವೆ.',
        'localStorage strings ରଖେ, sessionStorage ଗୋଟିଏ tab ପର୍ଯ୍ୟନ୍ତ ରହେ, ଏବଂ cookies ପ୍ରତ୍ୟେକ request ସହ ଯାଏ।',
        'يحفظ localStorage النصوص، ويبقى sessionStorage لعلامة تبويب واحدة، وترسل ملفات الارتباط مع كل طلب.',
        'localStorage hält Texte, sessionStorage gilt für einen Tab, Cookies gehen mit jeder Anfrage mit. Tests setzen sie, um Logins zu sparen.'),
    say('scenario', 'Scenario', 'Read the table header, turn each row into an object, and check every line total and the footer total.',
        'Table header पढ़ें, हर row को object बनाएं, और हर line total और footer total जांचें।',
        'Table header ಓದಿ, ಪ್ರತಿ row ಅನ್ನು object ಮಾಡಿ, ಪ್ರತಿ line total ಮತ್ತು footer total ಪರಿಶೀಲಿಸಿ.',
        'Table header ପଢ଼ନ୍ତୁ, ପ୍ରତ୍ୟେକ row କୁ object କରନ୍ତୁ, ଏବଂ ପ୍ରତ୍ୟେକ line total ଓ footer total ଯାଞ୍ଚ କରନ୍ତୁ।',
        'اقرأ رأس الجدول وحوّل كل صف إلى كائن وتحقق من كل مجموع سطر ومن المجموع النهائي.',
        'Lies die Tabellenköpfe, mach aus jeder Zeile ein Objekt und prüfe jede Zeilensumme und die Gesamtsumme.'),
    say('practice', 'Hands-on', 'Practise building selectors, parsing cookies, working out an event path and checking a sorted price list.',
        'Selectors बनाना, cookies parse करना, event path निकालना और sorted price list जांचने का अभ्यास करें।',
        'Selectors ರಚನೆ, cookies parse, event path ಮತ್ತು sorted price list ಪರಿಶೀಲನೆ ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Selectors ତିଆରି, cookies parse, event path ଓ sorted price list ଯାଞ୍ଚ ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على بناء المحددات وتحليل ملفات الارتباط وتتبع مسار الحدث وفحص قائمة أسعار مرتبة.',
        'Übe Selektoren bauen, Cookies parsen, einen Event-Pfad bestimmen und eine sortierte Preisliste prüfen.'),
]

QUIZ = [
    quiz('e', 'What does document.querySelector(".card") return when nothing matches?', ['null', 'an empty array', 'undefined', 'It throws'], 0, 'One element or nothing.', 'querySelector returns null, querySelectorAll returns an empty NodeList.'),
    quiz('e', 'Which selector matches <button data-test="buy">?', ['[data-test="buy"]', '#buy', '.buy', 'button:buy'], 0, 'Attribute selectors use square brackets.', 'The attribute and its value go inside brackets.'),
    quiz('e', 'Which property is safe for showing user input as text?', ['textContent', 'innerHTML', 'outerHTML', 'insertAdjacentHTML'], 0, 'No HTML parsing.', 'textContent never turns the text into elements, so scripts cannot sneak in.'),
    quiz('m', 'A click on a button inside a list fires a listener on the list. Which property points to the button?', ['event.target', 'event.currentTarget', 'this', 'event.list'], 0, 'Where the click started.', 'currentTarget is the list, where the listener sits. target is the clicked element.'),
    quiz('m', 'Which locator is most stable across a redesign?', ['getByRole("button", { name: "Checkout" })', '/html/body/div[2]/div/button[3]', '.btn.btn-primary.mt-2', 'div > div > button'], 0, 'What does the user see?', 'Role and accessible name stay the same when markup and styling change.'),
    quiz('m', 'An age field allows 18 to 120. Which values are classic boundary tests?', ['17, 18, 120, 121', '0 and 1000 only', '50 only', '18 and 120 only'], 0, 'Just inside and just outside each edge.', 'Boundary value analysis tests both sides of every limit.'),
    quiz('h', 'Why can document.querySelector not find a button inside a web component?', ['It is inside a shadow root', 'Buttons cannot be queried', 'Web components are iframes', 'It has no id'], 0, 'Encapsulation.', 'Shadow DOM hides its inner tree from document level queries.'),
    quiz('h', 'Why does Selenium need driver.switchTo().frame() for a payment form?', ['The form is in an iframe with its own document', 'The form is hidden', 'Payments need HTTPS', 'Selenium cannot type numbers'], 0, 'A separate document.', 'Commands run in one document at a time, so the driver must switch into the frame.'),
    quiz('h', 'What is true of a cookie marked HttpOnly?', ['document.cookie cannot read it', 'It is never sent to the server', 'It expires immediately', 'It only works on HTTP, not HTTPS'], 0, 'Protection against XSS.', 'The browser sends it with requests but hides it from page scripts.'),
    quiz('x', 'Why is a { force: true } click risky in a test?', ['It clicks even if the element is hidden or covered, so it can pass when users would fail', 'It is slower', 'It clicks twice', 'It only works in Chrome'], 0, 'Actionability checks.', 'Forcing skips the visibility and overlay checks that represent a real user.'),
    quiz('x', 'What does this print?', ['"string"', '"number"', '"object"', '"undefined"'], 0, 'Storage only keeps text.', 'Values are converted to strings, so use JSON for anything else.', code='localStorage.setItem("n", 5);\nconsole.log(typeof localStorage.getItem("n"));'),
    quiz('x', 'Which XPath finds the card article that contains the heading "Coffee mug"?', ["//h2[text()='Coffee mug']/ancestor::article", "//article[text()='Coffee mug']", "//h2/../..[@mug]", "article > h2:Coffee mug"], 0, 'Find the heading, then go up.', 'The ancestor axis walks up the tree, which CSS cannot do.'),
]

CALC = [
    calc('e', 'How many elements does document.querySelectorAll(".card") find on the shop page?', '3', 'Count the articles.', ['There are three article elements with class card.']),
    calc('e', 'How many of them match ".card:not(.sold-out)"?', '2', 'One card is sold out.', ['3 cards minus 1 sold out.']),
    calc('m', 'A click on the button in window > document > body > div.card > button with listeners in both phases on every level. How many listener calls happen?', '9', 'Down, target, up.', ['Capture: window, document, body, div.card is 4.', 'Target: 1.', 'Bubble: div.card, body, document, window is 4.', '<span class="eq">4 + 1 + 4 = 9</span>']),
    calc('m', 'Same click, but div.card calls stopPropagation in its bubble phase listener. How many listener calls happen now?', '6', 'Body, document and window miss the bubble.', ['Capture: 4 calls, target: 1 call.', 'Bubble: only div.card runs, 1 call.', '<span class="eq">4 + 1 + 1 = 6</span>']),
    calc('h', 'Row #1045 shows 2 × ₹1,299.00. What should the line total be?', '2598', 'Multiply.', ['<span class="eq">2 × 1299 = 2598</span>']),
    calc('h', 'The rows as shown add up to what amount?', '3297', 'Add the line totals.', ['<span class="eq">60 + 398 + 250 + 2589 = 3297</span>']),
    calc('x', 'If row #1045 were fixed, what would the correct order total be?', '3306', 'Replace 2589 with 2598.', ['<span class="eq">60 + 398 + 250 + 2598 = 3306</span>']),
    calc('x', 'An age field accepts 18 to 120. With boundary value analysis you test one below, on and one above each edge. How many values is that?', '6', 'Three per edge.', ['Lower edge: 17, 18, 19.', 'Upper edge: 119, 120, 121.']),
]

EX = [
    ex('selector', 'e', 'Build a CSS selector', '<p>Write <code>toSelector({ tag, id, classes, attrs })</code> that builds a CSS selector. Every key is optional. <code>attrs</code> is an object turned into <code>[name="value"]</code> parts. Order: tag, id, classes, attributes.</p>',
       'function toSelector({ tag = "", id, classes = [], attrs = {} }) {\n  \n}\n',
       [('toSelector({ tag: "button", classes: ["add", "primary"] })', 'button.add.primary'), ('toSelector({ id: "cart" })', '#cart'),
        ('toSelector({ tag: "article", attrs: { "data-test": "product", "data-sku": "PEN-01" } })', 'article[data-test="product"][data-sku="PEN-01"]')],
       'function toSelector({ tag = "", id, classes = [], attrs = {} }) {\n  let s = tag;\n  if (id) s += "#" + id;\n  for (const c of classes) s += "." + c;\n  for (const [k, v] of Object.entries(attrs)) s += `[${k}="${v}"]`;\n  return s;\n}',
       hint='Start with the tag and keep adding with <code>+=</code>.', why='Selector builders are common in page objects that take a product id and need its card.'),
    ex('cookies', 'm', 'Parse document.cookie', '<p>Write <code>parseCookies(text)</code> that turns <code>"a=1; recent=pen%2C%20mug"</code> into <code>{ a: "1", recent: "pen, mug" }</code>. Decode values with <code>decodeURIComponent</code>. An empty string gives an empty object.</p>',
       'function parseCookies(text) {\n  \n}\n',
       [('parseCookies("a=1; recent=pen%2C%20mug")', {'a': '1', 'recent': 'pen, mug'}), ('parseCookies("")', {}), ('parseCookies("token=abc==")', {'token': 'abc=='})],
       'function parseCookies(text) {\n  const out = {};\n  if (!text) return out;\n  for (const part of text.split("; ")) {\n    const i = part.indexOf("=");\n    out[part.slice(0, i)] = decodeURIComponent(part.slice(i + 1));\n  }\n  return out;\n}',
       hint='Split on <code>"; "</code>, then cut each part at the first <code>=</code>.', why='Tokens often end in <code>=</code>, so splitting at every <code>=</code> would break them.'),
    ex('path', 'h', 'The path of an event', '<p>Write <code>eventPath(parents, target)</code>. <code>parents</code> maps each node name to its parent name, and the top node has no entry. Return the list of <code>"capture:x"</code>, <code>"target:x"</code> and <code>"bubble:x"</code> steps in the order a click on <code>target</code> visits them.</p>',
       'function eventPath(parents, target) {\n  \n}\n',
       [('eventPath({ document: "window", body: "document", button: "body" }, "button")', ['capture:window', 'capture:document', 'capture:body', 'target:button', 'bubble:body', 'bubble:document', 'bubble:window']),
        ('eventPath({}, "window")', ['target:window'])],
       'function eventPath(parents, target) {\n  const up = [];\n  for (let n = parents[target]; n; n = parents[n]) up.push(n);\n  return [\n    ...up.toReversed().map(n => "capture:" + n),\n    "target:" + target,\n    ...up.map(n => "bubble:" + n),\n  ];\n}',
       hint='Collect the ancestors from the target upwards. Capture uses them reversed, bubble uses them as they are.', why='This is exactly the order the bubble animation shows, and the order your listeners run in.'),
    ex('sorted', 'x', 'Is the price list sorted?', '<p>A test reads price texts from a product grid after choosing "Price: low to high". Write <code>firstUnsorted(prices)</code> that returns the index of the first price that is lower than the one before it, or <code>-1</code> if the list is sorted. Prices look like <code>"₹1,299.00"</code>.</p>',
       'function firstUnsorted(prices) {\n  \n}\n',
       [('firstUnsorted(["₹20", "₹199.00", "₹1,299.00"])', -1), ('firstUnsorted(["₹99", "₹1,000", "₹250", "₹300"])', 2), ('firstUnsorted([])', -1), ('firstUnsorted(["₹5", "₹5"])', -1)],
       'function firstUnsorted(prices) {\n  const nums = prices.map(p => Number(p.replace(/[^\\d.]/g, "")));\n  for (let i = 1; i < nums.length; i++) {\n    if (nums[i] < nums[i - 1]) return i;\n  }\n  return -1;\n}',
       hint='Turn each text into a number first by removing everything except digits and the dot.', why='Compared as text, "₹1,000" sorts before "₹250", which is the classic bug in sort tests.'),
]

T = {
    'slug': 'js-dom-browser', 'title': 'The DOM and the Browser', 'short': 'DOM and browser', 'emoji': '🌐', 'module': MODULE, 'minutes': 19,
    'lead': 'How the page becomes a tree of objects, finding elements with CSS selectors and XPath, choosing stable locators, changing the page safely, events and delegation, forms and validation, shadow DOM, iframes, observers, storage and cookies.',
    'desc': 'DOM tree, querySelector, CSS selectors, XPath, locator strategy, textContent and innerHTML, XSS, events, bubbling, delegation, forms, validation, shadow DOM, iframes, MutationObserver, localStorage and cookies.',
    'summary': 'The DOM tree and how to move around it, CSS selectors including :has and attribute selectors, XPath by text and ancestor, which locators stay stable, textContent against innerHTML and XSS, events with capture and bubble, delegation and trusted events, form values and validation, shadow DOM and iframes in each test tool, waiting with MutationObserver, localStorage, sessionStorage and cookies, and checking every row of an order table.',
    'keywords': ['DOM', 'querySelector', 'CSS selector', 'XPath', 'locator', 'getByRole', 'data-test', 'textContent', 'innerHTML', 'XSS', 'event', 'bubbling', 'delegation', 'form validation', 'shadow DOM', 'iframe', 'MutationObserver', 'localStorage', 'cookie'],
    'qa_intro': 'UI automation is the DOM driven from outside. Locators, events, frames, shadow roots and browser storage explain most of what makes UI tests pass, fail or flake.',
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
