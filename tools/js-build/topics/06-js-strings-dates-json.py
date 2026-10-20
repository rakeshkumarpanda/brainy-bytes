# Chapter 6: strings, regular expressions, Math and number formatting, dates and Temporal, JSON.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('📦', 'Working with data', 'js-data', 'Objects, arrays, text, numbers, dates, JSON and collections: the data every app and every test handles.')

CODES = {
    'strings': run('''
const title = "  Wireless Mouse, Silent Click  ";
const t = title.trim();
console.log(`[${t}]`, t.length);
console.log(t.toUpperCase(), "|", t.toLowerCase());
console.log(t.includes("Mouse"), t.startsWith("Wire"), t.endsWith("Click"));
console.log(t.indexOf("Silent"), t.slice(0, 8), t.slice(-5), t.at(0));
console.log(t.split(", "));
console.log(t.replace("Click", "Clicks"), "|", "a-b-c".replaceAll("-", "/"));
console.log("7".padStart(3, "0"), "ab".repeat(3), "Total".padEnd(8, ".") + "₹99");
''', 'The string methods you use daily'),
    'unicode': run('''
const word = "café";
const composed = "cafe\\u0301";            // e plus a combining accent looks the same
console.log(word === composed, word.length, composed.length);
console.log(word === composed.normalize("NFC"));

const thumbs = "👍🏽";
console.log(thumbs.length, [...thumbs].length);   // code units against characters

const names = ["Zoë", "zara", "Émile", "adam"];
console.log(names.toSorted());
console.log(names.toSorted((a, b) => a.localeCompare(b, "en", { sensitivity: "base" })));
''', 'Unicode, normalising and sorting text'),
    'compare-text': run('''
// Text read from a page often has extra spaces, line breaks and non breaking spaces
const fromPage = "  Order\\u00a0#4521\\n   confirmed  ";
const expected = "Order #4521 confirmed";

const clean = s => s.replace(/\\s+/g, " ").trim();
console.log(JSON.stringify(fromPage));
console.log(clean(fromPage) === expected);
console.log(clean(fromPage).toLowerCase().includes("confirmed"));
''', 'Comparing text read from a page'),
    'regex': run('''
const text = "Orders ORD-104233 and ORD-998120 shipped on 2026-10-18. Call +91 98450 12345.";

console.log(/ORD-\\d{6}/.test(text));                    // is there a match
console.log(text.match(/ORD-\\d{6}/)[0]);                 // the first match
console.log(text.match(/ORD-\\d{6}/g));                   // every match with the g flag

const date = text.match(/(?<year>\\d{4})-(?<month>\\d{2})-(?<day>\\d{2})/);
console.log(date.groups);                                  // named groups

for (const m of text.matchAll(/ORD-(\\d+)/g)) {
  console.log("order number", m[1], "at index", m.index);
}

const phone = "+91 98450 12345";
console.log(phone.replace(/\\d(?=(?:\\D*\\d){4})/g, "*"));   // mask every digit that has 4 more digits after it
console.log("2026-10-18".replace(/(\\d+)-(\\d+)-(\\d+)/, "$3/$2/$1"));
console.log(RegExp.escape("price (₹)?"));                 // ES2025: escape user text for a regex
''', 'Regular expressions in action'),
    'regex-qa': show('''
// Playwright: assert text with a pattern, find by a pattern
await expect(page.getByTestId("order-id")).toHaveText(/^ORD-\\d{6}$/);
await page.getByRole("button", { name: /add to (cart|basket)/i }).click();

// Cypress
cy.contains(/order ORD-\\d{6} confirmed/i).should("be.visible");
cy.url().should("match", /\\/orders\\/\\d+$/);

// Jest, Vitest
expect(response.body.id).toMatch(/^ORD-\\d{6}$/);
expect(response.body).toEqual({ id: expect.stringMatching(/^ORD-/), total: expect.any(Number) });
''', 'Patterns in assertions and locators', note='Snippets'),
    'math': run('''
console.log(Math.round(2.5), Math.round(-2.5), Math.floor(-2.5), Math.ceil(2.1), Math.trunc(-2.9));
console.log(Math.max(4, 9, 2), Math.min(...[4, 9, 2]), Math.abs(-7), Math.sqrt(81), Math.hypot(3, 4));
console.log((1.005).toFixed(2), Math.round(1.005 * 100) / 100);    // both show a decimal rounding trap

const randomInt = (min, max) => min + Math.floor(Math.random() * (max - min + 1));
const roll = randomInt(1, 6);
console.log(roll >= 1 && roll <= 6 && Number.isInteger(roll));

const inr = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" });
const usd = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });
const eur = new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" });
console.log(inr.format(1234567.5), usd.format(1234567.5), eur.format(1234567.5));
console.log(new Intl.NumberFormat("en", { style: "percent", maximumFractionDigits: 1 }).format(0.4567));
console.log(new Intl.NumberFormat("en", { notation: "compact" }).format(1520000));
''', 'Math, rounding and formatting numbers'),
    'dates': run('''
const d = new Date(Date.UTC(2026, 9, 20, 14, 30));   // months start at 0, so 9 is October
console.log(d.toISOString());
console.log(d.getUTCFullYear(), d.getUTCMonth() + 1, d.getUTCDate(), d.getUTCDay());   // day 2 is Tuesday
console.log(d.getTime());                             // milliseconds since 1 January 1970 UTC

const parsed = new Date("2026-10-20T14:30:00Z");
console.log(parsed.getTime() === d.getTime());

const inAWeek = new Date(d);
inAWeek.setUTCDate(inAWeek.getUTCDate() + 7);         // rolls over into the next month for you
console.log(inAWeek.toISOString().slice(0, 10));

const days = (new Date("2026-12-25") - new Date("2026-10-20")) / 86_400_000;
console.log(days, "days until 25 December");

const fmt = new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short", timeZone: "Asia/Kolkata" });
console.log(fmt.format(d));
console.log(d.toLocaleDateString("de-DE", { timeZone: "UTC" }), d.toLocaleDateString("en-US", { timeZone: "UTC" }));
console.log(new Date("2026-02-30").toString(), new Date("not a date").getTime());
''', 'The Date object', play=True),
    'temporal': run('''
// Temporal (ES2026): immutable, time zone aware, months start at 1.
const today = Temporal.PlainDate.from("2026-10-20");
console.log(today.toString(), today.dayOfWeek, today.month);

const due = today.add({ days: 30 });
console.log(due.toString());
console.log(today.until(Temporal.PlainDate.from("2026-12-25")).days, "days");

const meeting = Temporal.ZonedDateTime.from("2026-10-20T09:00[Asia/Kolkata]");
console.log(meeting.withTimeZone("Europe/Berlin").toString());

const d = Temporal.Duration.from({ hours: 1, minutes: 95 });
console.log(d.round({ largestUnit: "hours" }).toString());

console.log(Temporal.PlainDate.compare(today, due));   // -1, 0 or 1
try {
  Temporal.PlainDate.from("2026-02-30", { overflow: "reject" });
} catch (err) {
  console.log(err.name);
}
''', 'Temporal, the modern date API'),
    'json': run('''
const order = {
  id: "ORD-104233",
  total: 2695,
  items: [{ sku: "A1", qty: 2 }],
  placedAt: new Date("2026-10-20T14:30:00Z"),
  note: undefined,                 // dropped by JSON
  print() { return "..."; },       // dropped by JSON
};

const text = JSON.stringify(order);
console.log(text);
console.log(JSON.stringify(order, null, 2).split("\\n").length, "lines when pretty printed");
console.log(JSON.stringify(order, ["id", "total"]));   // keep only these keys

const back = JSON.parse(text);
console.log(typeof back.placedAt);                       // dates come back as strings

const revived = JSON.parse(text, (key, value) => key === "placedAt" ? new Date(value) : value);
console.log(revived.placedAt instanceof Date);

try {
  JSON.parse("{ id: 1 }");                               // keys must use double quotes
} catch (err) {
  console.log(err.name);
}
try {
  JSON.stringify({ big: 10n });
} catch (err) {
  console.log(err.message);
}
''', 'JSON.stringify and JSON.parse'),
    'fixtures-json': run('''
import { readFile, writeFile, mkdir } from "node:fs/promises";

await mkdir("fixtures", { recursive: true });
const users = [
  { email: "asha@example.com", role: "admin" },
  { email: "ravi@example.com", role: "customer" },
];
await writeFile("fixtures/users.json", JSON.stringify(users, null, 2));

const loaded = JSON.parse(await readFile("fixtures/users.json", "utf8"));
console.log(loaded.length, loaded[0].email);

// Node can also import JSON directly with an import attribute
const { default: again } = await import("./fixtures/users.json", { with: { type: "json" } });
console.log(again[1].role);
''', 'Reading and writing JSON test data files', play=False),
    'scenario': test({
        'package.json': pkg('order-api', None, {'test': 'jest'}),
        'order.test.js': '''
// The body an order API returned, as a test would receive it
const body = JSON.parse(`{
  "id": "ORD-104233",
  "status": "CONFIRMED",
  "total": { "amount": 2695, "currency": "INR", "display": "₹2,695.00" },
  "placedAt": "2026-10-20T14:30:00.000Z",
  "customer": { "email": "asha@example.com", "phone": "+91 98450 12345" },
  "items": [{ "sku": "A1", "qty": 2 }, { "sku": "D4", "qty": 3 }]
}`);

describe("order response", () => {
  test("has the right shape", () => {
    expect(body).toMatchObject({
      id: expect.stringMatching(/^ORD-\\d{6}$/),
      status: "CONFIRMED",
      total: { amount: expect.any(Number), currency: "INR" },
      items: expect.arrayContaining([expect.objectContaining({ sku: "A1" })]),
    });
  });

  test("shows the amount the way the page does", () => {
    const shown = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(body.total.amount);
    expect(body.total.display).toBe(shown);
  });

  test("placedAt is a valid ISO time within a day of the run", () => {
    const placed = new Date(body.placedAt);
    const now = new Date("2026-10-21T09:00:00Z");     // a fixed clock keeps the test stable
    expect(placed.toISOString()).toBe(body.placedAt);
    expect(now - placed).toBeLessThan(24 * 60 * 60 * 1000);
  });

  test("contact details look valid", () => {
    expect(body.customer.email).toMatch(/^[^@\\s]+@[^@\\s]+\\.[a-z]{2,}$/i);
    expect(body.customer.phone.replace(/\\D/g, "")).toHaveLength(12);
  });
});
''',
    }, 'npx jest --verbose', 'Validate an order API response', replace=[(r'Time:\s+[\d.]+ s.*', 'Time:        0.3 s'), (r' \(\d+ ms\)', '')]),
}

PARTS = [
    part('strings', '🔤', 'Working with strings', '''
<p>A <b>string</b> is text. Strings are <b>immutable</b>: every method returns a new string and the original never changes. Indexes start at 0.</p>
[[strings]]
<div class="tw"><table class="jt"><tr><th>Need</th><th>Method</th></tr>
<tr><td>remove spaces at the ends</td><td><code>trim</code>, <code>trimStart</code>, <code>trimEnd</code></td></tr>
<tr><td>search</td><td><code>includes</code>, <code>startsWith</code>, <code>endsWith</code>, <code>indexOf</code>, <code>search</code></td></tr>
<tr><td>cut out a part</td><td><code>slice(start, end)</code> (negative counts from the end), <code>at</code></td></tr>
<tr><td>change</td><td><code>replace</code>, <code>replaceAll</code>, <code>toUpperCase</code>, <code>toLowerCase</code></td></tr>
<tr><td>split and join</td><td><code>split(separator)</code> and the array's <code>join</code></td></tr>
<tr><td>pad and repeat</td><td><code>padStart</code>, <code>padEnd</code>, <code>repeat</code></td></tr>
</table></div>
<h3>Unicode</h3>
[[unicode]]
<div class="warn"><code>length</code> counts UTF-16 code units, not visible characters. Emoji and some accents count as 2 or more. Use <code>[...str].length</code> for characters, <code>normalize("NFC")</code> before comparing and <code>localeCompare</code> for human sorting.</div>
<h3>Comparing text from the UI</h3>
[[compare-text]]
<div class="qa-box">Page text often contains non breaking spaces, line breaks from wrapped layout and extra spaces from templates. Normalise both sides before comparing, or use an assertion that already does: Playwright's <code>toHaveText</code> collapses whitespace, and <code>toContainText</code> matches a part.</div>
''', qa=['Playwright', 'Cypress', 'Selenium'], qa_why='Most UI assertions compare text, and whitespace or case differences cause false failures.',
        kw=['string', 'trim', 'includes', 'startsWith', 'slice', 'split', 'replace', 'replaceAll', 'padStart', 'toUpperCase', 'unicode', 'normalize', 'localeCompare', 'whitespace', 'non breaking space']),
    part('regex', '🧷', 'Regular expressions', '''
<p>A <b>regular expression</b> describes a pattern of text. It is written between slashes, followed by optional <b>flags</b>.</p>
<div class="viz" data-viz="regex"></div>
[[regex]]
<div class="tw"><table class="jt"><tr><th>Piece</th><th>Means</th></tr>
<tr><td><code>\\d \\w \\s</code></td><td>a digit, a word character, whitespace (capitals mean "not": <code>\\D</code>)</td></tr>
<tr><td><code>[abc] [^abc] [a-z]</code></td><td>one of, none of, a range</td></tr>
<tr><td><code>* + ? {6} {2,4}</code></td><td>repeat: 0 or more, 1 or more, optional, exactly 6, 2 to 4</td></tr>
<tr><td><code>^ $ \\b</code></td><td>start, end, word boundary</td></tr>
<tr><td><code>( ) (?&lt;name&gt; ) (?: )</code></td><td>capture group, named group, group without capturing</td></tr>
<tr><td><code>a|b</code></td><td>a or b</td></tr>
<tr><td><code>(?=x) (?!x)</code></td><td>followed by x, not followed by x (lookahead)</td></tr>
<tr><td>flags <code>g i m s u v y</code></td><td>all matches, ignore case, multi line, dot matches new lines, unicode, unicode sets, sticky</td></tr>
</table></div>
<p>Test tools accept regular expressions almost everywhere text is expected.</p>
[[regex-qa]]
<div class="qa-box">Anchor patterns with <code>^</code> and <code>$</code> when the whole value must match. <code>/ORD-\\d{6}/</code> also passes for <code>XORD-1234567</code>, while <code>/^ORD-\\d{6}$/</code> does not.</div>
''', qa=['Playwright', 'Cypress', 'Jest'], qa_why='Text assertions, locator names, URL checks and API field checks all accept regular expressions.',
        kw=['regular expression', 'regex', 'RegExp', 'test', 'match', 'matchAll', 'replace', 'capture group', 'named group', 'lookahead', 'flags', 'toMatch', 'toHaveText regex', 'stringMatching', 'RegExp.escape']),
    part('math', '🧮', 'Math and number formatting', '''
<p>The <code>Math</code> object holds rounding, min and max, powers and random numbers. <code>Intl.NumberFormat</code> turns numbers into the exact text a user in each country expects.</p>
[[math]]
<ul>
<li><code>Math.round</code> rounds .5 up towards positive infinity, so <code>-2.5</code> becomes <code>-2</code>.</li>
<li><code>(1.005).toFixed(2)</code> gives <code>"1.00"</code> because 1.005 is really stored as 1.00499999. For money, work in whole paise or cents.</li>
<li><code>Math.random()</code> is fine for test data, never for passwords or tokens. Use <code>crypto.randomUUID()</code> or <code>crypto.getRandomValues()</code> for those.</li>
</ul>
<div class="qa-box">To check a price on screen, format the expected number with the same <code>Intl.NumberFormat</code> settings the app uses and compare text with text. This catches the wrong currency sign, the wrong grouping (₹12,34,567 in India against $1,234,567 in the US) and wrong rounding.</div>
''', qa=True, kw=['Math', 'Math.round', 'Math.floor', 'Math.ceil', 'Math.random', 'random integer', 'toFixed', 'Intl.NumberFormat', 'currency format', 'percent', 'compact notation']),
    part('dates', '📅', 'Dates, time zones and Temporal', '''
<p>The <code>Date</code> object stores one moment as milliseconds since 1 January 1970 UTC. It has well known traps, which is why the new <b>Temporal</b> API was added in ES2026.</p>
[[dates]]
<div class="warn"><code>Date</code> months start at 0 (January is 0, December is 11), invalid dates such as 30 February roll over silently, and methods without "UTC" use the computer's time zone, so the same test can pass in Bengaluru and fail on a CI server in Frankfurt.</div>
<h3>Temporal</h3>
<p>Temporal separates the different ideas a date can mean: a calendar date (<code>PlainDate</code>), a time on a wall clock (<code>PlainTime</code>), an exact moment (<code>Instant</code>) and a moment in a place (<code>ZonedDateTime</code>). Values are immutable, months start at 1 and invalid input can be rejected.</p>
[[temporal]]
<div class="modern">Temporal ships in Node.js 26, Firefox and Chrome. Where it is missing, the <code>@js-temporal/polyfill</code> package adds it. If "Edit and run" shows a ReferenceError for Temporal, your browser does not have it yet.</div>
<div class="qa-box">Date logic is a top source of flaky tests: "today" changes, month ends differ and time zones shift dates. Fix the clock (Jest and Vitest fake timers with <code>setSystemTime</code>, Playwright's <code>page.clock</code>, Cypress's <code>cy.clock</code>), run CI in UTC and test the edges: 31 January plus one month, leap days and daylight saving changes.</div>
''', qa=['Playwright', 'Cypress', 'Jest'], qa_why='Date pickers, expiry rules and "today" logic need a fixed clock and edge case dates.',
        kw=['Date', 'Date.UTC', 'toISOString', 'getTime', 'timestamp', 'time zone', 'UTC', 'Intl.DateTimeFormat', 'Temporal', 'PlainDate', 'ZonedDateTime', 'Duration', 'fake timers', 'page.clock', 'cy.clock']),
    part('json', '📄', 'JSON', '''
<p><b>JSON</b> (JavaScript Object Notation) is the text format of almost every API. <code>JSON.stringify</code> turns a value into JSON text and <code>JSON.parse</code> turns text back into a value.</p>
[[json]]
<div class="tw"><table class="jt"><tr><th>JavaScript value</th><th>What JSON does with it</th></tr>
<tr><td>objects, arrays, strings, numbers, booleans, null</td><td>kept</td></tr>
<tr><td><code>undefined</code>, functions, symbols</td><td>dropped from objects, turned into <code>null</code> in arrays</td></tr>
<tr><td><code>Date</code></td><td>becomes an ISO string and comes back as a string</td></tr>
<tr><td><code>NaN</code>, <code>Infinity</code></td><td>become <code>null</code></td></tr>
<tr><td><code>BigInt</code></td><td>throws a TypeError</td></tr>
<tr><td><code>Map</code>, <code>Set</code></td><td>become <code>{}</code></td></tr>
</table></div>
<h3>JSON files as test data</h3>
[[fixtures-json]]
<div class="qa-box">Keep test data in <code>.json</code> fixture files: Cypress loads them with <code>cy.fixture("users")</code>, Playwright and Jest tests can <code>import</code> them. Pretty print with <code>JSON.stringify(data, null, 2)</code> when writing files so reviews show clean diffs.</div>
''', qa=['Cypress', 'Playwright', 'Jest'], qa_why='Every API test sends and reads JSON, and fixture files hold the test data.',
        kw=['JSON', 'JSON.stringify', 'JSON.parse', 'replacer', 'reviver', 'pretty print', 'fixtures', 'cy.fixture', 'import JSON', 'import attributes']),
    part('scenario', '🎬', 'Real world scenario: validate an order API response', '''
<div class="scenario"><b>The situation</b>The order API returns JSON. You must check that the order id has the right format, the status is confirmed, the display amount matches the number, the timestamp is a valid ISO time from the last day and the contact details look sane.</div>
[[scenario]]
<ul>
<li><code>toMatchObject</code> checks only the keys you list, so new fields in the API do not break the test.</li>
<li>Asymmetric matchers (<code>expect.stringMatching</code>, <code>expect.any</code>) check the <b>kind</b> of value when the exact value changes every run.</li>
<li>The clock is fixed (<code>now</code> is a constant), so the time check passes on any day it runs.</li>
</ul>
<div class="dev-box">Chapter 20 turns this into a real API suite: starting a server, sending requests with fetch and supertest, and validating whole responses against a JSON Schema.</div>
''', qa=['Jest', 'Vitest'], kw=['API response validation', 'toMatchObject', 'expect.stringMatching', 'expect.any', 'JSON body', 'ISO date check', 'currency check']),
]

INFO = {'title': 'Text, patterns, numbers, dates and JSON', 'panels': [
    panel([['e', '🔤'], ['t', '"  Hi  ".trim() → "Hi"', {'b': 1}]], 'Strings', 'Immutable text with many helper methods.', 'Normalise spaces and case before you compare page text.'),
    panel([['e', '🧷'], ['t', '/^ORD-\\d{6}$/', {'b': 1}]], 'Patterns', 'Regular expressions describe the shape of text.', 'Anchor with ^ and $ when the whole value must match.'),
    panel([['e', '📅'], ['t', 'month 9 = October', {'b': 1}]], 'Dates', 'Date counts months from 0, Temporal from 1.', 'Fix the clock in tests and run CI in UTC.'),
    panel([['e', '📄'], ['t', 'JSON.parse(text)', {'b': 1}]], 'JSON', 'The text format of APIs and fixture files.', 'Dates come back as strings and undefined disappears.')],
    'remember': 'Compare normalised text, anchor your patterns and freeze the clock.'}

REAL = [
    ['🧾', 'Invoice numbers', 'A billing service generates INV-2026-000123 style ids and a regex in the tests checks every one.'],
    ['🌍', 'Prices around the world', 'A shop shows ₹12,34,567.50 in India and $1,234,567.50 in the US from the same number with Intl.NumberFormat.'],
    ['⏰', 'A coupon that expires', 'A coupon valid "until the end of the month" is tested with a fixed clock on 31 January, 28 February and 29 February.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers strings, regular expressions, number formatting, dates with Temporal, and JSON.',
        'यह अध्याय strings, regular expressions, number formatting, Temporal के साथ dates और JSON सिखाता है।',
        'ಈ ಅಧ್ಯಾಯ strings, regular expressions, number formatting, Temporal ಜೊತೆ dates ಮತ್ತು JSON ಕಲಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ strings, regular expressions, number formatting, Temporal ସହ dates ଓ JSON ଶିଖାଏ।',
        'يتناول هذا الفصل النصوص والتعابير النمطية وتنسيق الأرقام والتواريخ مع Temporal وJSON.',
        'Dieses Kapitel behandelt Strings, reguläre Ausdrücke, Zahlenformatierung, Datumswerte mit Temporal und JSON.'),
    say('strings', 'Strings', 'Strings never change, every method returns a new one. Trim, normalise and compare carefully, because page text has hidden spaces.',
        'Strings कभी नहीं बदलते, हर method नया string लौटाता है। Page text में छिपे spaces होते हैं, इसलिए trim और normalise करके compare करें।',
        'Strings ಬದಲಾಗುವುದಿಲ್ಲ, ಪ್ರತಿ method ಹೊಸ string ಕೊಡುತ್ತದೆ. Page text ನಲ್ಲಿ ಅಡಗಿದ spaces ಇರುತ್ತವೆ, trim ಮಾಡಿ compare ಮಾಡಿ.',
        'Strings କେବେ ବଦଳେ ନାହିଁ, ପ୍ରତ୍ୟେକ method ନୂଆ string ଫେରାଏ। Page text ରେ ଲୁଚିଥିବା spaces ଥାଏ, trim କରି compare କରନ୍ତୁ।',
        'النصوص لا تتغير، وكل دالة تعيد نصًا جديدًا. نص الصفحة فيه مسافات مخفية، لذا قص وطبّع قبل المقارنة.',
        'Strings ändern sich nie, jede Methode liefert einen neuen. Seitentext hat versteckte Leerzeichen, also trimmen und normalisieren vor dem Vergleich.'),
    say('regex', 'Regular expressions', 'A regular expression describes a pattern of text. Test tools accept them for text checks, locator names and URLs. Anchor them when the whole value must match.',
        'Regular expression text के pattern को बताता है। Test tools इन्हें text checks, locator names और URLs में लेते हैं। पूरी value मिलानी हो तो anchor करें।',
        'Regular expression text ನ pattern ವಿವರಿಸುತ್ತದೆ. Test tools ಇವನ್ನು text checks, locator names ಮತ್ತು URLs ಗೆ ಸ್ವೀಕರಿಸುತ್ತವೆ.',
        'Regular expression text ର pattern ବର୍ଣ୍ଣନା କରେ। Test tools ଏଗୁଡ଼ିକୁ text checks, locator names ଓ URLs ରେ ଗ୍ରହଣ କରନ୍ତି।',
        'التعبير النمطي يصف نمطًا من النص. تقبله أدوات الاختبار في فحص النصوص وأسماء المحددات والروابط. ثبته بالبداية والنهاية عند مطابقة القيمة كاملة.',
        'Ein regulärer Ausdruck beschreibt ein Textmuster. Testwerkzeuge akzeptieren ihn für Textprüfungen, Locator-Namen und URLs. Verankere ihn, wenn der ganze Wert passen muss.'),
    say('math', 'Math and formatting', 'Math handles rounding and random numbers. Intl number format produces the exact text a user sees, which is the best way to check prices.',
        'Math rounding और random numbers संभालता है। Intl.NumberFormat वही text बनाता है जो user देखता है, prices जाँचने का सबसे अच्छा तरीका।',
        'Math rounding ಮತ್ತು random numbers ನಿಭಾಯಿಸುತ್ತದೆ. Intl.NumberFormat user ನೋಡುವ text ರಚಿಸುತ್ತದೆ, prices ಪರಿಶೀಲನೆಗೆ ಉತ್ತಮ.',
        'Math rounding ଓ random numbers ସମ୍ଭାଳେ। Intl.NumberFormat user ଦେଖୁଥିବା text ତିଆରି କରେ, prices ଯାଞ୍ଚ ପାଇଁ ସର୍ବୋତ୍ତମ।',
        'يتولى Math التقريب والأرقام العشوائية. Intl.NumberFormat ينتج النص الذي يراه المستخدم، وهو أفضل طريقة لفحص الأسعار.',
        'Math erledigt Runden und Zufallszahlen. Intl.NumberFormat erzeugt genau den Text, den Nutzer sehen, ideal zum Prüfen von Preisen.'),
    say('dates', 'Dates', 'Date months start at zero and use the local time zone. Temporal fixes these problems. In tests, fix the clock and test edge dates.',
        'Date के months zero से शुरू होते हैं और local time zone इस्तेमाल करते हैं। Temporal ये problems ठीक करता है। Tests में clock fix करें।',
        'Date months zero ಇಂದ ಶುರು, local time zone ಬಳಸುತ್ತದೆ. Temporal ಈ problems ಸರಿಪಡಿಸುತ್ತದೆ. Tests ನಲ್ಲಿ clock fix ಮಾಡಿ.',
        'Date months zero ରୁ ଆରମ୍ଭ ଏବଂ local time zone ବ୍ୟବହାର କରେ। Temporal ଏହି problems ଠିକ୍ କରେ। Tests ରେ clock fix କରନ୍ତୁ।',
        'أشهر Date تبدأ من صفر وتستخدم المنطقة الزمنية المحلية. يصلح Temporal هذه المشكلات. في الاختبارات ثبت الساعة واختبر التواريخ الحدية.',
        'Date-Monate beginnen bei null und nutzen die lokale Zeitzone. Temporal behebt das. In Tests die Uhr festsetzen und Randdaten prüfen.'),
    say('json', 'JSON', 'JSON stringify turns values into text and JSON parse turns text back. Dates come back as strings, and undefined and functions are dropped.',
        'JSON.stringify values को text बनाता है और JSON.parse वापस। Dates strings बनकर लौटती हैं, undefined और functions हट जाते हैं।',
        'JSON.stringify values ಅನ್ನು text ಆಗಿಸುತ್ತದೆ, JSON.parse ಹಿಂದಕ್ಕೆ. Dates strings ಆಗಿ ಬರುತ್ತವೆ, undefined ಮತ್ತು functions ಬಿಡಲಾಗುತ್ತವೆ.',
        'JSON.stringify values କୁ text କରେ ଏବଂ JSON.parse ଫେରାଏ। Dates strings ହୋଇ ଫେରେ, undefined ଓ functions ବାଦ ପଡ଼େ।',
        'يحول JSON.stringify القيم إلى نص ويعيدها JSON.parse. تعود التواريخ نصوصًا وتُحذف undefined والدوال.',
        'JSON.stringify macht Werte zu Text, JSON.parse zurück. Datumswerte kommen als Strings zurück, undefined und Funktionen fallen weg.'),
    say('scenario', 'Scenario', 'A Jest test checks an order response with toMatchObject, regex and type matchers, a formatted amount and a fixed clock.',
        'एक Jest test order response को toMatchObject, regex और type matchers, formatted amount और fixed clock से जाँचता है।',
        'ಒಂದು Jest test order response ಅನ್ನು toMatchObject, regex, type matchers, formatted amount ಮತ್ತು fixed clock ಮೂಲಕ ಪರಿಶೀಲಿಸುತ್ತದೆ.',
        'ଏକ Jest test order response କୁ toMatchObject, regex, type matchers, formatted amount ଓ fixed clock ରେ ଯାଞ୍ଚ କରେ।',
        'اختبار Jest يفحص استجابة طلب باستخدام toMatchObject والتعابير النمطية ومطابقات النوع ومبلغ منسق وساعة ثابتة.',
        'Ein Jest-Test prüft eine Bestellantwort mit toMatchObject, Regex- und Typ-Matchern, einem formatierten Betrag und fester Uhr.'),
    say('practice', 'Hands-on', 'Practise text clean up, masking, pattern extraction and date arithmetic.',
        'Text clean up, masking, pattern extraction और date arithmetic का अभ्यास करें।',
        'Text clean up, masking, pattern extraction ಮತ್ತು date arithmetic ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Text clean up, masking, pattern extraction ଓ date arithmetic ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على تنظيف النص والإخفاء واستخراج الأنماط وحساب التواريخ.',
        'Übe Textbereinigung, Maskieren, Musterextraktion und Datumsrechnung.'),
]

QUIZ = [
    quiz('e', 'What does "  hi  ".trim() return?', ['"hi"', '"  hi"', '"hi  "', '"  hi  "'], 0, 'trim removes both ends.', '<code>trim</code> removes whitespace from both ends.'),
    quiz('e', 'Which flag makes a regex find every match instead of only the first?', ['g', 'i', 'm', 's'], 0, 'g for global.', 'The <code>g</code> flag finds all matches. <code>i</code> ignores case.'),
    quiz('e', 'What month is new Date(2026, 0, 15)?', ['January', 'December', 'February', 'An invalid date'], 0, 'Date months start at 0.', 'Month 0 is January. Temporal uses 1 for January.'),
    quiz('m', 'What does JSON.stringify({ a: 1, b: undefined }) give?', ['\'{"a":1}\'', '\'{"a":1,"b":undefined}\'', '\'{"a":1,"b":null}\'', 'An error'], 0, 'undefined is not a JSON value.', 'Keys with <code>undefined</code> are dropped from objects.'),
    quiz('m', 'Which pattern matches the whole value ORD-123456 and nothing longer?', ['/^ORD-\\d{6}$/', '/ORD-\\d{6}/', '/ORD-\\d+/', '/^ORD/'], 0, 'Anchors.', '<code>^</code> and <code>$</code> make the pattern cover the whole string.'),
    quiz('m', 'What does "👍🏽".length return?', ['4', '1', '2', '8'], 0, 'length counts UTF-16 code units.', 'The thumbs up and the skin tone are each two code units.'),
    quiz('h', 'After JSON.parse, what type is a value that was a Date before JSON.stringify?', ['string', 'Date', 'number', 'object'], 0, 'JSON has no date type.', 'It becomes an ISO string. Use a reviver to turn it back into a Date.'),
    quiz('h', 'A test checks "Expires 31 Oct" and passes in India but fails in CI in the US. What is the most likely cause?', ['The Date code uses the machine\'s local time zone', 'Regex flags differ by country', 'JSON parsing is locale specific', 'CI is slower'], 0, 'Which part of Date depends on the machine?', 'Local time methods use the machine\'s time zone. Use UTC methods, Temporal with a zone, or set TZ in CI.'),
    quiz('h', 'Which Jest matcher checks only the keys you list and ignores extra keys?', ['toMatchObject', 'toEqual', 'toStrictEqual', 'toBe'], 0, 'It matches a subset.', '<code>toMatchObject</code> passes when the listed keys match, whatever else is present.'),
    quiz('x', 'What does (1.005).toFixed(2) return?', ['"1.00"', '"1.01"', '1.01', '"1.005"'], 0, 'How is 1.005 really stored?', 'It is stored as 1.00499999..., so it rounds down.'),
    quiz('x', 'What does "2026-10-18".replace(/(\\d+)-(\\d+)-(\\d+)/, "$3/$2/$1") return?', ['"18/10/2026"', '"2026/10/18"', '"$3/$2/$1"', '"10/18/2026"'], 0, '$1 is the first group.', 'The groups are 2026, 10 and 18, placed in reverse.'),
    quiz('x', 'Which is true about Temporal.PlainDate?', ['It is immutable and add() returns a new date', 'Months start at 0', 'It always uses the machine time zone', 'It is mutable like Date'], 0, 'Temporal was designed to fix Date.', 'Temporal values never change. Methods such as <code>add</code> return new values.'),
]

CALC = [
    calc('e', 'What does "Brainy Bytes".slice(0, 6) return?', 'Brainy', 'Characters 0 to 5.', ['Indexes 0 to 5 are B, r, a, i, n, y.']),
    calc('e', 'What does "7".padStart(3, "0") return?', '007', 'Pad the start until the length is 3.', ['Two zeros are added in front.']),
    calc('m', 'How many matches does "a1b22c333".match(/\\d+/g) return?', '3', '+ means one or more, so neighbours join.', ['The matches are "1", "22" and "333".']),
    calc('m', 'How many days are there from 20 October 2026 to 25 December 2026?', '66', 'Count the rest of October, November and December.', ['October: 31 - 20 = 11 days.', 'November: 30 days.', 'December: 25 days.', '<span class="eq">11 + 30 + 25 = 66</span>']),
    calc('h', 'What does Math.round(-2.5) return?', '-2', 'Math.round goes towards positive infinity at .5.', ['-2.5 is halfway, so it rounds up to -2.']),
    calc('h', 'How many lines does JSON.stringify({ a: 1, b: [1, 2] }, null, 2) produce?', '7', 'Each array item gets its own line.', ['Lines: {, "a": 1,, "b": [, 1,, 2, ], }', 'That is 7 lines.']),
    calc('x', 'In milliseconds, how long is one day?', '86400000', '24 hours of 60 minutes of 60 seconds of 1000 ms.', ['<span class="eq">24 × 60 × 60 × 1000 = 86,400,000</span>'], alt=['86,400,000', '86_400_000']),
    calc('x', 'Temporal.PlainDate.from("2026-01-31").add({ months: 1 }) gives which date (YYYY-MM-DD)?', '2026-02-28', 'February 2026 has 28 days and the default overflow is "constrain".', ['31 February does not exist.', 'With the default overflow it is constrained to the last day: 2026-02-28.']),
]

EX = [
    ex('slugify', 'e', 'Make a URL slug', '<p>Write <code>slugify(title)</code>: lower case, trim, replace every run of characters that are not letters or digits with one dash, and remove dashes at the ends. <code>"  Hello, World!  "</code> becomes <code>"hello-world"</code>.</p>',
       'function slugify(title) {\n  \n}\n',
       [('slugify("  Hello, World!  ")', 'hello-world'), ('slugify("JavaScript for QA & Dev")', 'javascript-for-qa-dev'), ('slugify("2026 -- Plans")', '2026-plans')],
       'function slugify(title) {\n  return title.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");\n}',
       hint='Two <code>replace</code> calls: one for the runs of other characters, one for dashes at the start and end.', why='The <code>+</code> turns a run of spaces and punctuation into a single dash.'),
    ex('mask', 'm', 'Mask an email', '<p>Write <code>maskEmail(email)</code> that keeps the first character of the name and the whole domain and replaces the rest of the name with three stars: <code>"asha.rao@example.com"</code> becomes <code>"a***@example.com"</code>. Return <code>"invalid"</code> when there is no single @.</p>',
       'function maskEmail(email) {\n  \n}\n',
       [('maskEmail("asha.rao@example.com")', 'a***@example.com'), ('maskEmail("r@x.io")', 'r***@x.io'), ('maskEmail("no-at-sign")', 'invalid'), ('maskEmail("a@b@c")', 'invalid')],
       'function maskEmail(email) {\n  const parts = email.split("@");\n  if (parts.length !== 2 || !parts[0]) return "invalid";\n  return `${parts[0][0]}***@${parts[1]}`;\n}', hint='<code>split("@")</code> must give exactly two parts.', why='Checking the number of parts handles both a missing @ and too many.'),
    ex('order-ids', 'h', 'Extract order numbers', '<p>Write <code>orderNumbers(text)</code> that returns every order number (the digits only, as numbers) from ids like <code>ORD-104233</code>. Only ids with exactly six digits count, and <code>XORD-</code> is not an id.</p>',
       'function orderNumbers(text) {\n  \n}\n',
       [('orderNumbers("ORD-104233 and ORD-998120 shipped")', [104233, 998120]), ('orderNumbers("ORD-12 and ORD-1234567")', []), ('orderNumbers("XORD-111111, ORD-222222.")', [222222]), ('orderNumbers("")', [])],
       'function orderNumbers(text) {\n  return [...text.matchAll(/\\bORD-(\\d{6})\\b/g)].map(m => Number(m[1]));\n}',
       hint='Use <code>matchAll</code> with a capture group and word boundaries <code>\\b</code> on both sides.', why='The boundaries stop <code>XORD-</code> and seven digit numbers from matching, and the group gives just the digits.'),
    ex('business-days', 'x', 'Add business days', '<p>Write <code>addBusinessDays(isoDate, n)</code>. It gets a date like <code>"2026-10-23"</code> and returns the date <code>n</code> working days later (skipping Saturdays and Sundays) in the same format. Work in UTC.</p>',
       'function addBusinessDays(isoDate, n) {\n  \n}\n',
       [('addBusinessDays("2026-10-23", 1)', '2026-10-26'), ('addBusinessDays("2026-10-20", 3)', '2026-10-23'), ('addBusinessDays("2026-10-30", 5)', '2026-11-06'), ('addBusinessDays("2026-10-24", 1)', '2026-10-26')],
       'function addBusinessDays(isoDate, n) {\n  const d = new Date(isoDate + "T00:00:00Z");\n  let added = 0;\n  while (added < n) {\n    d.setUTCDate(d.getUTCDate() + 1);\n    const day = d.getUTCDay();\n    if (day !== 0 && day !== 6) added++;\n  }\n  return d.toISOString().slice(0, 10);\n}',
       hint='Step one day at a time with <code>setUTCDate</code> and count only days where <code>getUTCDay()</code> is 1 to 5.', why='Stepping day by day handles month ends and weekends without special cases. Using UTC keeps it independent of the machine\'s time zone.'),
]

T = {
    'slug': 'js-strings-dates-json', 'title': 'Strings, Regex, Numbers, Dates and JSON', 'short': 'Strings, dates and JSON', 'emoji': '🔤', 'module': MODULE, 'minutes': 22,
    'lead': 'String methods and Unicode, comparing text read from a page, regular expressions in code and in assertions, Math and Intl number formatting, Date traps and the new Temporal API, and JSON for APIs and fixture files.',
    'desc': 'String methods, Unicode, regular expressions, Math, Intl.NumberFormat, Date, time zones, Temporal, JSON.stringify, JSON.parse and validating an API response.',
    'summary': 'String methods and Unicode, normalising page text for comparisons, regular expressions with groups, lookahead and flags, regex in Playwright, Cypress and Jest, Math and rounding traps, Intl.NumberFormat for currencies, Date and time zone traps, Temporal, JSON with replacers and revivers, JSON fixture files and validating an order API response.',
    'keywords': ['string', 'regex', 'regular expression', 'Math', 'Intl.NumberFormat', 'currency', 'Date', 'time zone', 'Temporal', 'JSON', 'JSON.parse', 'JSON.stringify', 'fixtures', 'toMatch', 'toMatchObject'],
    'qa_intro': 'Text, pattern, price and date checks make up most assertions. This chapter shows how to make them strict where it matters and stable everywhere else.',
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
