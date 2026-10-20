# Chapter 1: what JavaScript is, where it runs, the console, the page, strict mode and reading errors.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🌱', 'Foundations', 'js-foundations', 'From your first program to functions and closures. Developers and testers both start here.')

CODES = {
    'node-version': show('''
node -v          # which Node.js is installed
npm -v           # npm comes with Node.js
node             # opens the REPL, type .exit to leave
node hello.js    # runs a file
''', 'Check your setup in a terminal', lang='bash', note='Terminal commands',
        result='<code>node -v</code> prints a version such as <code>v26.12.0</code>. Every example on this page was run with that version.'),
    'nvm': show('''
# macOS and Linux: install nvm once, then any Node.js version you need
nvm install --lts       # the long term support release, the safe choice for projects
nvm install 26          # the newest release line, used on this page
nvm use 26
node -v

# Windows: use the installer from nodejs.org or "nvm-windows"
''', 'Several Node.js versions side by side', lang='bash', note='Terminal commands'),
    'hello': run('''
console.log("Hello, Brainy Bytes!");
console.log("2 + 3 =", 2 + 3);
console.log(`Today we learn ${"JavaScript"}`);
''', 'Your first program'),
    'comments': run('''
// A single line comment explains the next line
let price = 250; // a comment can also sit at the end of a line

/* A block comment
   can span many lines */
let qty = 3;

console.log(price * qty)   // no semicolon here, JavaScript adds one for us
console.log("done");
''', 'Statements, comments and semicolons'),
    'asi-trap': run('''
function getUser() {
  return
  {
    name: "Asha"
  };
}
console.log(getUser());
''', 'The one place automatic semicolons bite'),
    'console-tour': run('''
console.log("log is for normal messages");
console.info("info looks the same in Node");
console.warn("warn goes to the error stream");
console.error("error also goes to the error stream");

console.log("%s scored %d points", "Ravi", 42);

console.table([
  { test: "login", status: "passed", ms: 812 },
  { test: "checkout", status: "failed", ms: 2310 },
]);

console.group("Suite: cart");
console.log("adds an item");
console.log("removes an item");
console.groupEnd();

console.count("retry");
console.count("retry");
console.assert(1 + 1 === 3, "maths is broken");
''', 'The console toolbox'),
    'timing': run('''
console.time("build list");
const items = [];
for (let i = 0; i < 100000; i++) items.push(i * 2);
console.timeEnd("build list");
console.log("items:", items.length);
''', 'Measuring how long something takes', replace=[(r'build list: [\d.]+ms', 'build list: 2.481ms')]),
    'page-script': dom('''
<!doctype html>
<html>
<head><title>Shop</title></head>
<body>
  <h1 id="title">Welcome</h1>
  <button id="buy">Buy now</button>
  <p id="msg"></p>
</body>
</html>
''', '''
const title = document.querySelector("#title");
console.log("Before:", title.textContent);
title.textContent = "Welcome back, Asha";
console.log("After:", title.textContent);

document.querySelector("#buy").addEventListener("click", () => {
  document.querySelector("#msg").textContent = "Added to cart";
  console.log("Clicked!");
});
document.querySelector("#buy").click();
console.log("Message:", document.querySelector("#msg").textContent);
''', 'JavaScript changes the page'),
    'script-tags': show('''
<!-- Classic script: blocks the HTML parser while it downloads and runs -->
<script src="app.js"></script>

<!-- defer: downloads in parallel, runs in order after the HTML is parsed -->
<script defer src="app.js"></script>

<!-- async: downloads in parallel, runs as soon as it arrives, in any order -->
<script async src="analytics.js"></script>

<!-- module: deferred by default, strict mode, can use import and export -->
<script type="module" src="main.js"></script>
''', 'Four ways to load a script', lang='html', note='HTML'),
    'qa-execute': show('''
// Selenium WebDriver for JavaScript
const title = await driver.executeScript("return document.title");

// Playwright
const count = await page.evaluate(() => document.querySelectorAll(".product").length);

// Cypress
cy.window().then(win => win.localStorage.setItem("token", "abc"));
''', 'Test tools send JavaScript into the page', note='Snippets, full runs come in chapter 15'),
    'strict': run('''
"use strict";
let total = 0;
totl = 10;          // a typo creates a new global in sloppy mode, strict mode stops it
console.log(total);
''', 'Strict mode catches a typo', file='strict.cjs', expect='throw'),
    'sloppy': run('''
let total = 0;
totl = 10;          // sloppy mode silently creates a global variable
console.log(total, totl);
''', 'The same typo without strict mode', file='sloppy.cjs', play=False),
    'type-error': run('''
const user = { name: "Asha" };
console.log(user.name.toUpperCase());
console.log(user.address.city);
''', 'Reading an error message', expect='throw'),
    'try-it': run('''
const cart = [];
try {
  cart.push({ id: 1, price: 99 });
  console.log(cart[0].price.toFixed(2));
  console.log(cart[1].price);
} catch (err) {
  console.log("Caught:", err.name);
  console.log("Message:", err.message);
}
console.log("The program keeps going");
''', 'Catching the error instead of crashing'),
    'report': run('''
const results = [
  { name: "login works", status: "passed", ms: 812 },
  { name: "wrong password shows error", status: "passed", ms: 640 },
  { name: "checkout total", status: "failed", ms: 2310 },
  { name: "coupon applies", status: "skipped", ms: 0 },
  { name: "logout", status: "passed", ms: 301 },
];

const summary = { passed: 0, failed: 0, skipped: 0 };
let totalMs = 0;
for (const r of results) {
  summary[r.status]++;
  totalMs += r.ms;
}

console.table(summary);
console.log(`Total time: ${(totalMs / 1000).toFixed(2)} s`);
const failed = results.filter(r => r.status === "failed").map(r => r.name);
console.log("Failed:", failed);
''', 'Summarise a test run'),
    'report-test': test({
        'package.json': pkg('report', 'module', {'test': 'node --test'}),
        'summary.js': '''
export function summarize(results) {
  const summary = { passed: 0, failed: 0, skipped: 0 };
  for (const r of results) summary[r.status]++;
  return summary;
}
''',
        'summary.test.js': '''
import { test } from "node:test";
import assert from "node:assert/strict";
import { summarize } from "./summary.js";

test("counts each status", () => {
  const got = summarize([{ status: "passed" }, { status: "failed" }, { status: "passed" }]);
  assert.deepEqual(got, { passed: 2, failed: 1, skipped: 0 });
});

test("an empty run has zero of everything", () => {
  assert.deepEqual(summarize([]), { passed: 0, failed: 0, skipped: 0 });
});
''',
    }, 'npm test', 'A first automated check with the built in test runner', show=['summary.js', 'summary.test.js'],
        replace=[(r'duration_ms [\d.]+', 'duration_ms 0.5'), (r'\(\d+\.\d+ms\)', '(0.5ms)')]),
}

PARTS = [
    part('what-is-js', '🌍', 'What JavaScript is and where it runs', '''
<p><b>JavaScript</b> is the programming language of the web. Every modern browser has a JavaScript <b>engine</b> built in, so the same code runs on a phone, a laptop and a smart TV. Outside the browser, <b>Node.js</b>, <b>Deno</b> and <b>Bun</b> run JavaScript on servers, laptops and CI machines.</p>
<div class="viz" data-viz="flow" data-k="where"></div>
<div class="tw"><table class="jt"><tr><th>Name</th><th>What it is</th></tr>
<tr><td>ECMAScript</td><td>The official standard. JavaScript is the language that follows it. A new edition comes out every June: ES2015 (also called ES6), ES2016 and so on up to ES2026.</td></tr>
<tr><td>TC39</td><td>The committee that decides new features. A proposal moves through stages 0 to 4 and joins the standard at stage 4.</td></tr>
<tr><td>Engine</td><td>The program that runs the code: V8 (Chrome, Edge, Node.js, Deno), SpiderMonkey (Firefox) and JavaScriptCore (Safari, Bun).</td></tr>
<tr><td>Runtime</td><td>An engine plus extra tools. A browser adds the page (DOM), fetch and storage. Node.js adds files, network servers and processes.</td></tr>
</table></div>
<div class="vs"><div><b>🛠️ Developers use it for</b>web pages, React or Angular apps, servers and APIs with Node.js, mobile apps with React Native and desktop apps with Electron.</div><div><b>🧪 QA engineers use it for</b>UI automation with Playwright, Cypress, WebdriverIO and Selenium WebDriver, API tests, unit tests with Jest or Vitest, and small scripts that create test data or read reports.</div></div>
<div class="fun">JavaScript has nothing to do with Java. The name was picked in 1995 for marketing, and the language was written in about ten days by Brendan Eich.</div>
''', qa=['Playwright', 'Cypress', 'Selenium', 'WebdriverIO'], qa_why='Most modern UI and API automation tools are written in JavaScript or TypeScript, and their tests are too.',
        kw=['ECMAScript', 'TC39', 'V8', 'SpiderMonkey', 'JavaScriptCore', 'Node.js', 'Deno', 'Bun', 'runtime', 'engine', 'ES6', 'ES2015']),
    part('setup', '🧰', 'Setting up Node.js and an editor', '''
<p>To follow along on your own machine you need two things: <b>Node.js</b> and a code editor. Every example on this page also runs inside your browser with the <b>✏️ Edit and run</b> button, so you can start right now.</p>
<ol class="steps">
<li>Install Node.js from <code>nodejs.org</code>. Pick the <b>LTS</b> (long term support) release for work projects. The <b>Current</b> release has the newest features.</li>
<li>Install <b>Visual Studio Code</b>, the editor most JavaScript teams use. Its built in terminal opens with <span class="kbd">Ctrl</span> + <span class="kbd">`</span>.</li>
<li>Open a terminal and check that both <code>node</code> and <code>npm</code> answer.</li>
</ol>
[[node-version]]
<p>Teams that work on several projects often need several Node.js versions. A version manager such as <b>nvm</b> switches between them.</p>
[[nvm]]
<div class="tip">A project can pin its Node.js version in a file called <code>.nvmrc</code> or in the <code>engines</code> field of <code>package.json</code>, so every developer and every CI machine uses the same one.</div>
<div class="qa-box">Playwright, Cypress and WebdriverIO all need Node.js. Before you install any of them, check <code>node -v</code> against the version the tool supports. A test that passes on your laptop and fails in CI is often just a different Node.js version.</div>
''', qa=True, kw=['install Node.js', 'LTS', 'nvm', 'VS Code', 'REPL', 'node -v', 'npm -v', '.nvmrc', 'engines']),
    part('first-program', '👋', 'Your first program', '''
<p>A JavaScript program is a list of <b>statements</b> that run from top to bottom. <code>console.log</code> prints whatever you give it. Several values are printed with a space between them.</p>
[[hello]]
<p>The text inside backticks is a <b>template literal</b>. Anything inside <code>${ }</code> is worked out and placed into the text. You will use it constantly for messages and test names.</p>
<h3>Comments and semicolons</h3>
[[comments]]
<p>Semicolons end statements. JavaScript has <b>automatic semicolon insertion</b> (ASI), so leaving them out usually works. Most teams pick one style and let a formatter such as Prettier enforce it.</p>
[[asi-trap]]
<div class="exam">A line break right after <code>return</code> makes JavaScript insert a semicolon there. The function returns <code>undefined</code> and the object below is never reached. Always start the returned value on the same line as <code>return</code>.</div>
''', kw=['console.log', 'hello world', 'statement', 'comment', 'semicolon', 'ASI', 'automatic semicolon insertion', 'template literal']),
    part('console', '🖨️', 'The console toolbox', '''
<p>The console is your first debugging tool and the place where test runners print what they find. It can do far more than <code>log</code>.</p>
[[console-tour]]
<div class="tw"><table class="jt"><tr><th>Method</th><th>Use it for</th></tr>
<tr><td><code>log</code>, <code>info</code></td><td>normal messages, written to standard output</td></tr>
<tr><td><code>warn</code>, <code>error</code></td><td>problems, written to the error stream, shown in yellow and red in the browser</td></tr>
<tr><td><code>table</code></td><td>arrays of objects shown as a table, perfect for test data</td></tr>
<tr><td><code>group</code>, <code>groupEnd</code></td><td>indenting related lines, like a suite and its tests</td></tr>
<tr><td><code>count</code></td><td>how many times a line ran, for example retries</td></tr>
<tr><td><code>assert</code></td><td>prints an error only when the condition is false</td></tr>
<tr><td><code>time</code>, <code>timeEnd</code></td><td>how long a piece of code took</td></tr>
</table></div>
[[timing]]
<div class="qa-box">When a Playwright or Cypress test fails, add a <code>console.log</code> of the value you expected and the value you got. Playwright shows test output in its report, and in Cypress the browser console shows it. For timings, prefer the runner's own reports over <code>console.time</code>.</div>
''', qa=['Playwright', 'Cypress', 'Jest'], kw=['console.table', 'console.group', 'console.count', 'console.assert', 'console.time', 'console.warn', 'console.error', 'debugging', 'format specifiers']),
    part('browser', '🌐', 'JavaScript in a web page', '''
<p>In a browser, JavaScript can read and change the page. The page is a tree of objects called the <b>DOM</b> (Document Object Model). <code>document.querySelector</code> finds an element with a CSS selector, the same kind of selector a test tool uses to find a button.</p>
[[page-script]]
<p>A page loads JavaScript with a <code>&lt;script&gt;</code> tag. Where and how the tag is written decides when the code runs.</p>
[[script-tags]]
<div class="viz" data-viz="flow" data-k="loading"></div>
<p>Every browser has <b>DevTools</b> (<span class="kbd">F12</span>). Its Console tab runs any JavaScript you type against the open page. Testers use it to try a selector before putting it in a test: <code>document.querySelectorAll("button.buy").length</code> tells you at once whether the selector is unique.</p>
[[qa-execute]]
<div class="qa-box">All three tools let you run your own JavaScript inside the page under test. That is how you read values the UI does not show, set up storage or check something a locator cannot reach. The code you send runs in the browser, so it can use <code>document</code> and <code>window</code>, but it cannot see the variables in your test file.</div>
''', qa=['Selenium', 'Playwright', 'Cypress'], qa_why='Locators are CSS or XPath selectors, and executeScript or evaluate send JavaScript into the page.',
        kw=['script tag', 'defer', 'async', 'type module', 'DOM', 'querySelector', 'DevTools', 'console', 'executeScript', 'page.evaluate', 'cy.window']),
    part('how-it-runs', '⚙️', 'How the engine runs your code', '''
<p>Running a script happens in a few steps, and knowing them explains several surprises you will meet later.</p>
<div class="viz" data-viz="flow" data-k="engine"></div>
<ul>
<li><b>Parse</b>: the engine reads the whole file first. A typo anywhere is a <code>SyntaxError</code> and nothing runs at all.</li>
<li><b>Compile</b>: V8 turns the code into bytecode, then a JIT (just in time) compiler turns busy functions into fast machine code while the program runs.</li>
<li><b>Execute</b>: one line at a time on a <b>single thread</b>. JavaScript does one thing at a time. Waiting for a server or a timer is handed to the runtime, which is how one thread stays responsive. Chapter 10 explains this event loop.</li>
</ul>
<h3>Strict mode</h3>
<p>Strict mode turns silent mistakes into errors. Modules (<code>type="module"</code> or <code>.mjs</code> files) and classes are always strict. Older scripts opt in with <code>"use strict"</code> on the first line.</p>
[[sloppy]]
[[strict]]
<div class="rule">Write new code as modules and you get strict mode for free. Every <code>.mjs</code> example on this page is strict.</div>
''', kw=['engine', 'parse', 'JIT', 'bytecode', 'single thread', 'strict mode', 'use strict', 'sloppy mode', 'SyntaxError']),
    part('errors', '🚨', 'Reading error messages', '''
<p>Errors are not a failure on your part. They are the fastest way to learn what the program really did. Every error has a <b>name</b>, a <b>message</b> and a <b>stack trace</b> that lists where it happened.</p>
[[type-error]]
<ol class="steps">
<li>Read the <b>name</b>: <code>TypeError</code> means a value was the wrong type for what you did with it. Here <code>user.address</code> is <code>undefined</code>, and you cannot read <code>city</code> from it.</li>
<li>Read the <b>first stack line</b> that points into your own file. <code>main.mjs:3</code> is file, line and column.</li>
<li>Look at that line and ask which value was missing. Then print it.</li>
</ol>
<div class="tw"><table class="jt"><tr><th>Error</th><th>Usual cause</th></tr>
<tr><td><code>SyntaxError</code></td><td>The code is not valid JavaScript: a missing bracket or quote. Nothing in the file runs.</td></tr>
<tr><td><code>ReferenceError</code></td><td>A name that does not exist, often a typo, or a variable used before <code>let</code> declared it.</td></tr>
<tr><td><code>TypeError</code></td><td>Reading a property of <code>undefined</code> or <code>null</code>, or calling something that is not a function.</td></tr>
<tr><td><code>RangeError</code></td><td>A number out of range, such as <code>new Array(-1)</code>, or endless recursion.</td></tr>
</table></div>
<p>A <code>try</code> and <code>catch</code> block lets the program handle the error and carry on. Chapter 3 goes much deeper.</p>
[[try-it]]
<div class="qa-box">A failing test prints exactly this kind of stack. "Cannot read properties of undefined" inside a test usually means a locator found nothing or an API response did not have the field you expected. Read the line number, then log the value.</div>
''', qa=['Jest', 'Playwright', 'Cypress'], qa_why='Every failed test hands you an error message and a stack trace to read.',
        kw=['TypeError', 'ReferenceError', 'SyntaxError', 'RangeError', 'stack trace', 'error message', 'Cannot read properties of undefined', 'try catch']),
    part('scenario', '🎬', 'Real world scenario: summarise a test run', '''
<div class="scenario"><b>The situation</b>Your team's nightly run produces a list of results. The lead wants a short summary in the chat every morning: how many passed, how many failed, the total time and the names of the failures.</div>
<p>The script below does exactly that with only what this chapter covered: an array of objects, a loop, a template literal and the console.</p>
[[report]]
<p>Real teams turn helpers like this into tested code. Node.js ships with a test runner, so a first automated check needs no extra installs. Run it with <code>npm test</code>.</p>
[[report-test]]
<div class="dev-box">Splitting the logic (<code>summarize</code>) from the printing makes it easy to test. The same idea, pure functions with the input and output kept separate, comes back in every chapter.</div>
''', qa=['node:test'], qa_why='Reading results and reporting them is daily QA work, and node:test is the simplest way to start testing.',
        kw=['test report', 'summary', 'node --test', 'node:test', 'assert', 'deepEqual', 'npm test']),
]

DG = {
    'where': {'t': 'One language, many places to run', 'w': 900, 'h': 300,
              'n': [['code', 20, 120, 160, 60, 'your .js code', {'c': 5, 'sh': 'doc'}],
                    ['br', 270, 20, 180, 70, 'Browser', {'c': 2, 'sub': 'V8, SpiderMonkey, JSC', 'i': 'Adds the DOM, events, fetch, storage and timers.'}],
                    ['nd', 270, 115, 180, 70, 'Node.js', {'c': 1, 'sub': 'V8', 'i': 'Adds files, servers, processes and npm packages.'}],
                    ['dn', 270, 210, 180, 70, 'Deno and Bun', {'c': 3, 'sub': 'V8 and JSC', 'i': 'Newer runtimes with TypeScript and testing built in.'}],
                    ['ui', 560, 20, 300, 70, 'web pages and apps', {'c': 0, 'sub': 'React, Angular, Vue'}],
                    ['qa', 560, 115, 300, 70, 'servers, APIs, CLIs and test tools', {'c': 4, 'sub': 'Express, Playwright, Jest, Cypress'}],
                    ['sc', 560, 210, 300, 70, 'scripts and edge functions', {'c': 0, 'sub': 'build tools, CI tasks'}]],
              'e': [['code', 'br'], ['code', 'nd'], ['code', 'dn'], ['br', 'ui'], ['nd', 'qa'], ['dn', 'sc']]},
    'loading': {'t': 'When each kind of script runs', 'w': 900, 'h': 260,
                'n': [['p1', 20, 30, 230, 44, 'HTML parsing', {'c': 2}], ['n1', 270, 30, 130, 44, 'download', {'c': 0}], ['x1', 410, 30, 110, 44, 'run', {'c': 4}], ['p1b', 530, 30, 300, 44, 'parsing continues', {'c': 2}],
                      ['p2', 20, 110, 560, 44, 'HTML parsing never stops', {'c': 2}], ['n2', 270, 165, 160, 40, 'download in parallel', {'c': 0}], ['x2', 600, 110, 120, 44, 'run (defer)', {'c': 1}]],
                'tx': [[110, 16, 'classic <script>', {'b': 1}], [110, 98, '<script defer> and type="module"', {'b': 1}]],
                'e': [['p1', 'n1', {'t': 'pause'}], ['n1', 'x1'], ['x1', 'p1b'], ['n2', 'x2', {'t': 'after parsing'}]],
                'st': [[['p1', 'n1', 'x1', 'p1>n1', 'n1>x1', 'x1>p1b', 'p1b'], 'A classic script stops the parser, downloads, runs, and only then does the page keep loading. Users see a blank page meanwhile.'],
                       [['p2', 'n2', 'x2', 'n2>x2'], 'defer and module scripts download while the HTML is parsed and run once parsing is done, in the order they appear.']]},
    'engine': {'t': 'From source text to running program', 'w': 900, 'h': 230,
               'n': [['src', 20, 80, 130, 60, 'source code', {'c': 5, 'sh': 'doc'}], ['parse', 190, 80, 130, 60, 'parser', {'c': 2, 'i': 'Reads the whole file. Any syntax error stops everything here.'}],
                     ['ast', 360, 80, 120, 60, 'syntax tree', {'c': 3, 'sh': 'pill'}], ['bc', 520, 20, 160, 60, 'bytecode', {'c': 0, 'sub': 'interpreter runs it', 'i': 'V8 calls this interpreter Ignition. It starts quickly.'}],
                     ['jit', 520, 140, 160, 60, 'optimised machine code', {'c': 1, 'sub': 'JIT compiler', 'i': 'Hot functions are compiled again into fast code. V8 calls this TurboFan.'}],
                     ['out', 740, 80, 140, 60, 'output', {'c': 4, 'sh': 'screen'}]],
               'e': [['src', 'parse'], ['parse', 'ast'], ['ast', 'bc'], ['bc', 'jit', {'t': 'hot code'}], ['jit', 'bc', {'t': 'deoptimise', 'd': 1, 'cv': 30}], ['bc', 'out'], ['jit', 'out']],
               'st': [[['src', 'parse', 'src>parse'], 'The engine reads all the text first.'], [['ast', 'parse>ast'], 'It builds a tree that describes the program.'],
                      [['bc', 'ast>bc'], 'The interpreter turns the tree into bytecode and starts running at once.'], [['jit', 'bc>jit'], 'Functions that run many times are compiled into fast machine code.'],
                      [['jit>bc'], 'If an assumption breaks, for example a number suddenly becomes a string, the fast code is thrown away.'], [['out', 'bc>out', 'jit>out'], 'Either way, the result is the same output. Only the speed changes.']]},
}

INFO = {'title': 'From a text file to a working page', 'panels': [
    panel([['e', '📝'], ['t', 'console.log("Hi")', {'b': 1}]], 'You write text', 'JavaScript starts as plain text in a .js file.', 'Any editor works. VS Code adds colours, hints and a terminal.'),
    panel([['e', '⚙️'], ['t', 'parse, compile, run', {'b': 1}]], 'The engine runs it', 'V8 or another engine reads the text and runs it.', 'A syntax error stops everything before the first line runs.'),
    panel([['e', '🖥️'], ['t', 'Hi', {'b': 1}]], 'Something happens', 'A line is printed, a page changes, or a server answers.', 'Where it runs decides what it can do: pages in a browser, files and servers in Node.js.'),
    panel([['e', '🧪'], ['t', '✓ 5 passed', {'b': 1}]], 'Tests check it', 'Testers use the same language to check that it all works.', 'Playwright, Cypress, Jest and node:test are written in JavaScript too.')],
    'remember': 'Same language in the page, on the server and in the tests.'}

REAL = [
    ['🛒', 'An online shop', 'When you change the quantity in a cart, JavaScript in the page recalculates the total without reloading.'],
    ['🔧', 'A build pipeline', 'Node.js scripts run linters, bundle the code and start the test suite on every pull request.'],
    ['🤖', 'Nightly regression', 'A Playwright suite written in TypeScript logs in, buys a product and checks the receipt in three browsers.'],
]

SAY = [
    say('top', 'Welcome', 'Welcome to JavaScript. This chapter shows where it runs, how to set it up, how to print and how to read errors.',
        'JavaScript में आपका स्वागत है। यह अध्याय बताता है कि यह कहाँ चलता है, इसे कैसे set up करें, कैसे print करें और errors कैसे पढ़ें।',
        'JavaScript ಗೆ ಸ್ವಾಗತ. ಇದು ಎಲ್ಲಿ ಓಡುತ್ತದೆ, ಹೇಗೆ set up ಮಾಡುವುದು, ಹೇಗೆ print ಮಾಡುವುದು ಮತ್ತು errors ಹೇಗೆ ಓದುವುದು ಎಂದು ಈ ಅಧ್ಯಾಯ ತೋರಿಸುತ್ತದೆ.',
        'JavaScript କୁ ସ୍ୱାଗତ। ଏହା କେଉଁଠି ଚାଲେ, କିପରି set up କରିବେ, କିପରି print କରିବେ ଏବଂ errors କିପରି ପଢ଼ିବେ, ଏହି ଅଧ୍ୟାୟ ଦେଖାଏ।',
        'مرحبًا بك في JavaScript. يوضح هذا الفصل أين تعمل، وكيف تجهزها، وكيف تطبع النتائج، وكيف تقرأ الأخطاء.',
        'Willkommen bei JavaScript. Dieses Kapitel zeigt, wo es läuft, wie man es einrichtet, wie man ausgibt und wie man Fehler liest.'),
    say('what-is-js', 'What JavaScript is', 'JavaScript is the language of the web. Engines such as V8 run it in browsers, and Node.js runs it on servers and in test tools.',
        'JavaScript web की भाषा है। V8 जैसे engines इसे browser में चलाते हैं, और Node.js इसे servers और test tools में चलाता है।',
        'JavaScript ವೆಬ್‌ನ ಭಾಷೆ. V8 ನಂತಹ engines ಇದನ್ನು browser ನಲ್ಲಿ ಓಡಿಸುತ್ತವೆ, Node.js ಇದನ್ನು servers ಮತ್ತು test tools ನಲ್ಲಿ ಓಡಿಸುತ್ತದೆ.',
        'JavaScript ହେଉଛି web ର ଭାଷା। V8 ପରି engines ଏହାକୁ browser ରେ ଚଲାନ୍ତି, ଏବଂ Node.js ଏହାକୁ servers ଓ test tools ରେ ଚଲାଏ।',
        'JavaScript هي لغة الويب. محركات مثل V8 تشغلها في المتصفح، وNode.js يشغلها على الخوادم وفي أدوات الاختبار.',
        'JavaScript ist die Sprache des Webs. Engines wie V8 führen es im Browser aus, und Node.js führt es auf Servern und in Testwerkzeugen aus.'),
    say('setup', 'Setting up', 'Install Node.js, pick the LTS release for projects, and check it with node minus v. A version manager such as nvm switches versions.',
        'Node.js install करें, projects के लिए LTS release चुनें, और node -v से जाँचें। nvm जैसा version manager versions बदलता है।',
        'Node.js install ಮಾಡಿ, projects ಗಾಗಿ LTS release ಆಯ್ಕೆ ಮಾಡಿ, node -v ಮೂಲಕ ಪರಿಶೀಲಿಸಿ. nvm ನಂತಹ version manager versions ಬದಲಾಯಿಸುತ್ತದೆ.',
        'Node.js install କରନ୍ତୁ, projects ପାଇଁ LTS release ବାଛନ୍ତୁ, ଏବଂ node -v ରେ ଯାଞ୍ଚ କରନ୍ତୁ। nvm ପରି version manager versions ବଦଳାଏ।',
        'ثبّت Node.js، واختر إصدار LTS للمشاريع، وتحقق منه بالأمر node -v. مدير الإصدارات مثل nvm ينقلك بين الإصدارات.',
        'Installiere Node.js, nimm für Projekte die LTS-Version und prüfe sie mit node -v. Ein Versionsmanager wie nvm wechselt zwischen Versionen.'),
    say('first-program', 'First program', 'A program is a list of statements that run from top to bottom. console dot log prints values, and a return value must start on the same line as return.',
        'Program statements की list है जो ऊपर से नीचे चलती है। console.log values print करता है, और return value return वाली line पर ही शुरू होनी चाहिए।',
        'Program ಮೇಲಿನಿಂದ ಕೆಳಗೆ ಓಡುವ statements ಪಟ್ಟಿ. console.log values print ಮಾಡುತ್ತದೆ, return value return ಇರುವ ಸಾಲಿನಲ್ಲೇ ಶುರುವಾಗಬೇಕು.',
        'Program ହେଉଛି ଉପରୁ ତଳକୁ ଚାଲୁଥିବା statements ର ତାଲିକା। console.log values print କରେ, ଏବଂ return value return ଥିବା ଧାଡ଼ିରେ ହିଁ ଆରମ୍ଭ ହେବା ଉଚିତ।',
        'البرنامج قائمة من التعليمات تعمل من الأعلى إلى الأسفل. console.log يطبع القيم، ويجب أن تبدأ القيمة المرجعة على نفس سطر return.',
        'Ein Programm ist eine Liste von Anweisungen, die von oben nach unten laufen. console.log gibt Werte aus, und ein Rückgabewert muss in der Zeile von return beginnen.'),
    say('console', 'The console', 'The console can log, warn, show tables, group lines, count and time code. Test runners print their findings there too.',
        'Console log, warn, tables, groups, count और time कर सकता है। Test runners भी अपने नतीजे वहीं print करते हैं।',
        'Console log, warn, tables, groups, count ಮತ್ತು time ಮಾಡಬಹುದು. Test runners ಕೂಡ ತಮ್ಮ ಫಲಿತಾಂಶಗಳನ್ನು ಅಲ್ಲಿ print ಮಾಡುತ್ತವೆ.',
        'Console log, warn, tables, groups, count ଏବଂ time କରିପାରେ। Test runners ମଧ୍ୟ ସେଠାରେ ଫଳାଫଳ print କରନ୍ତି।',
        'يمكن لـ console أن يسجل ويحذر ويعرض جداول ويجمع الأسطر ويعد ويقيس الوقت. وأدوات الاختبار تطبع نتائجها هناك أيضًا.',
        'Die Konsole kann loggen, warnen, Tabellen zeigen, Zeilen gruppieren, zählen und Zeit messen. Testrunner geben dort auch ihre Ergebnisse aus.'),
    say('browser', 'In the page', 'In a browser, JavaScript reads and changes the page through the DOM. Test tools use the same selectors and can send JavaScript into the page.',
        'Browser में JavaScript DOM के ज़रिए page पढ़ता और बदलता है। Test tools वही selectors इस्तेमाल करते हैं और page में JavaScript भेज सकते हैं।',
        'Browser ನಲ್ಲಿ JavaScript DOM ಮೂಲಕ page ಓದುತ್ತದೆ ಮತ್ತು ಬದಲಾಯಿಸುತ್ತದೆ. Test tools ಅದೇ selectors ಬಳಸುತ್ತವೆ ಮತ್ತು page ಗೆ JavaScript ಕಳುಹಿಸಬಹುದು.',
        'Browser ରେ JavaScript DOM ମାଧ୍ୟମରେ page ପଢ଼େ ଓ ବଦଳାଏ। Test tools ସେହି selectors ବ୍ୟବହାର କରନ୍ତି ଏବଂ page କୁ JavaScript ପଠାଇପାରନ୍ତି।',
        'في المتصفح، تقرأ JavaScript الصفحة وتغيرها عبر DOM. أدوات الاختبار تستخدم نفس المحددات ويمكنها إرسال JavaScript إلى الصفحة.',
        'Im Browser liest und ändert JavaScript die Seite über das DOM. Testwerkzeuge nutzen dieselben Selektoren und können JavaScript in die Seite schicken.'),
    say('how-it-runs', 'How it runs', 'The engine parses the whole file, compiles it and runs it on one thread. Strict mode turns silent mistakes into errors.',
        'Engine पूरी file parse करता है, compile करता है और एक thread पर चलाता है। Strict mode चुपचाप होने वाली गलतियों को errors बना देता है।',
        'Engine ಸಂಪೂರ್ಣ file parse ಮಾಡಿ, compile ಮಾಡಿ ಒಂದೇ thread ನಲ್ಲಿ ಓಡಿಸುತ್ತದೆ. Strict mode ಮೌನ ತಪ್ಪುಗಳನ್ನು errors ಆಗಿ ಮಾಡುತ್ತದೆ.',
        'Engine ପୂରା file parse କରେ, compile କରେ ଏବଂ ଗୋଟିଏ thread ରେ ଚଲାଏ। Strict mode ନୀରବ ଭୁଲକୁ errors କରିଦିଏ।',
        'يحلل المحرك الملف كله ويترجمه ويشغله على خيط واحد. الوضع الصارم يحول الأخطاء الصامتة إلى أخطاء ظاهرة.',
        'Die Engine parst die ganze Datei, kompiliert sie und führt sie auf einem Thread aus. Der Strict Mode macht stille Fehler sichtbar.'),
    say('errors', 'Reading errors', 'Every error has a name, a message and a stack trace. Read the name, find the first line in your own file, then print the value that was missing.',
        'हर error का name, message और stack trace होता है। Name पढ़ें, अपनी file की पहली line ढूँढें, फिर जो value नहीं थी उसे print करें।',
        'ಪ್ರತಿ error ಗೆ name, message ಮತ್ತು stack trace ಇರುತ್ತದೆ. Name ಓದಿ, ನಿಮ್ಮ file ನ ಮೊದಲ ಸಾಲು ಹುಡುಕಿ, ಇಲ್ಲದ value ಯನ್ನು print ಮಾಡಿ.',
        'ପ୍ରତ୍ୟେକ error ର name, message ଓ stack trace ଥାଏ। Name ପଢ଼ନ୍ତୁ, ନିଜ file ର ପ୍ରଥମ ଧାଡ଼ି ଖୋଜନ୍ତୁ, ତାପରେ ନଥିବା value print କରନ୍ତୁ।',
        'لكل خطأ اسم ورسالة وتتبع للمكدس. اقرأ الاسم، وابحث عن أول سطر في ملفك، ثم اطبع القيمة التي كانت مفقودة.',
        'Jeder Fehler hat einen Namen, eine Nachricht und einen Stacktrace. Lies den Namen, finde die erste Zeile in deiner Datei und gib den fehlenden Wert aus.'),
    say('scenario', 'Scenario', 'A short script turns a list of test results into a morning summary, and the built in node test runner checks that the summary is right.',
        'एक छोटा script test results की list को सुबह की summary में बदलता है, और built in node test runner जाँचता है कि summary सही है।',
        'ಒಂದು ಚಿಕ್ಕ script test results ಪಟ್ಟಿಯನ್ನು ಬೆಳಗಿನ summary ಆಗಿ ಮಾಡುತ್ತದೆ, built in node test runner summary ಸರಿಯೇ ಎಂದು ಪರಿಶೀಲಿಸುತ್ತದೆ.',
        'ଏକ ଛୋଟ script test results ତାଲିକାକୁ ସକାଳର summary କରେ, ଏବଂ built in node test runner summary ଠିକ୍ କି ନାହିଁ ଯାଞ୍ଚ କରେ।',
        'سكربت قصير يحول قائمة نتائج الاختبارات إلى ملخص صباحي، ومشغل الاختبارات المدمج في Node يتحقق من صحة الملخص.',
        'Ein kurzes Skript macht aus einer Liste von Testergebnissen eine Morgenübersicht, und der eingebaute Node-Testrunner prüft, ob sie stimmt.'),
    say('practice', 'Hands-on', 'Now write code yourself. Each exercise runs real tests in your browser and tells you which cases pass.',
        'अब खुद code लिखें। हर exercise आपके browser में असली tests चलाती है और बताती है कि कौन से cases pass हुए।',
        'ಈಗ ನೀವೇ code ಬರೆಯಿರಿ. ಪ್ರತಿ exercise ನಿಮ್ಮ browser ನಲ್ಲಿ ನಿಜವಾದ tests ಓಡಿಸಿ ಯಾವ cases pass ಆಗಿವೆ ಎಂದು ಹೇಳುತ್ತದೆ.',
        'ଏବେ ନିଜେ code ଲେଖନ୍ତୁ। ପ୍ରତ୍ୟେକ exercise ଆପଣଙ୍କ browser ରେ ପ୍ରକୃତ tests ଚଲାଏ ଏବଂ କେଉଁ cases pass ହେଲା କହେ।',
        'الآن اكتب الكود بنفسك. كل تمرين يشغل اختبارات حقيقية في متصفحك ويخبرك بالحالات التي نجحت.',
        'Jetzt schreibst du selbst Code. Jede Übung führt echte Tests in deinem Browser aus und zeigt, welche Fälle bestehen.'),
]

QUIZ = [
    quiz('e', 'Which program runs JavaScript outside the browser on servers and CI machines?', ['Node.js', 'Java Virtual Machine', 'Python', 'The DOM'], 0,
         'It is built on the V8 engine.', 'Node.js puts the V8 engine outside the browser and adds files, servers and processes. Deno and Bun do the same job.'),
    quiz('e', 'What does this print?', ['5 1', '"5" "1"', '51', 'An error'], 0, 'console.log separates its values with a space.',
         'console.log prints each value with one space between them, so you see <code>5 1</code>.', code='console.log(2 + 3, 1);'),
    quiz('e', 'Which console method shows an array of objects as rows and columns?', ['console.table', 'console.group', 'console.dir', 'console.count'], 0,
         'Think of a spreadsheet.', '<code>console.table</code> draws a table with one row per item and one column per property.'),
    quiz('m', 'What does this function return?', ['{ name: "Asha" }', 'undefined', 'null', 'A SyntaxError'], 1,
         'Look at what follows return on the same line.', 'Automatic semicolon insertion puts a semicolon right after <code>return</code>, so the function returns <code>undefined</code>.',
         code='function f() {\n  return\n  { name: "Asha" };\n}\nconsole.log(f());'),
    quiz('m', 'Which script tag downloads in parallel and runs after the HTML is parsed, in document order?', ['&lt;script defer&gt;', '&lt;script async&gt;', 'A classic &lt;script&gt;', '&lt;script nomodule&gt;'], 0,
         'async runs in whatever order the files arrive.', '<code>defer</code> keeps the order and waits for parsing. Module scripts behave the same way by default.'),
    quiz('m', 'A test fails with "TypeError: Cannot read properties of undefined (reading \'total\')". What is the most likely cause?', ['The object you read total from is undefined', 'total is spelled wrong in the HTML', 'The test runner is broken', 'The number is too large'], 0,
         'Read the error name and the word after "of".', 'The value before <code>.total</code> was <code>undefined</code>, for example an API response without the field you expected.'),
    quiz('h', 'In which kind of file is strict mode switched on without writing "use strict"?', ['An ES module such as a .mjs file', 'Any .js file', 'Only files in node_modules', 'Only files run by npm'], 0,
         'Modules were added in ES2015 with stricter rules.', 'ES modules and class bodies are always strict. Classic scripts and CommonJS files need the directive.'),
    quiz('h', 'A file has a missing closing bracket on line 40. What happens to the console.log on line 1?', ['It never runs', 'It runs, then the error appears', 'It runs twice', 'It depends on the browser'], 0,
         'When is the whole file read?', 'The engine parses the entire file before running anything. A <code>SyntaxError</code> stops the file before line 1 runs.'),
    quiz('h', 'Inside page.evaluate in Playwright, which of these can the code use?', ['document and window of the page', 'Variables declared in the test file around it', 'The Node.js fs module', 'The test runner\'s expect function'], 0,
         'The function is sent to the browser and run there.', 'The callback is serialised and run inside the page, so it sees the page\'s globals. Values from the test must be passed as an argument.'),
    quiz('x', 'Which engine runs JavaScript in Node.js, Chrome and Deno?', ['V8', 'SpiderMonkey', 'JavaScriptCore', 'Chakra'], 0,
         'Google started it in 2008.', 'V8 powers Chrome, Edge, Node.js and Deno. Firefox uses SpiderMonkey and Safari and Bun use JavaScriptCore.'),
    quiz('x', 'A proposal is at TC39 stage 3. What does that usually mean?', ['The design is done and engines are implementing it', 'It is already in every browser', 'It was rejected', 'Only Node.js supports it'], 0,
         'Stage 4 means it is in the standard.', 'Stage 3 means the design is final and implementations are under way. Stage 4 needs two shipping implementations and joins the next edition.'),
    quiz('x', 'Why do teams pin the Node.js version in .nvmrc or engines?', ['So every laptop and CI machine runs the same version', 'To make npm install faster', 'Because Node.js only allows one version per computer', 'To turn on strict mode'], 0,
         'Think about "passes locally, fails in CI".', 'Different Node.js versions can behave differently or lack features. Pinning removes one source of tests that pass on one machine and fail on another.'),
]

CALC = [
    calc('e', 'How many lines does this program print?', '3', 'Count the console.log calls that run.', ['Each <code>console.log</code> call prints one line.', 'There are three calls, so three lines.'],
         code='console.log("a");\nconsole.log("b", "c");\nconsole.log(`d ${1 + 1}`);'),
    calc('e', 'What is the last line printed?', 'retry: 3', 'console.count prints the label and how many times it has been called.', ['Calls one, two and three print <code>retry: 1</code>, <code>retry: 2</code> and <code>retry: 3</code>.'],
         code='for (let i = 0; i < 3; i++) {\n  console.count("retry");\n}', alt=['3']),
    calc('m', 'ES2015 is the 6th edition of ECMAScript (ES6). Which edition number is ES2026?', '17', 'One edition per year.', ['<span class="eq">2026 - 2015 = 11</span>', '<span class="eq">6 + 11 = 17</span>']),
    calc('m', 'What does this print?', 'Total: 6 items', 'Work out the template literal.', ['<code>a.length</code> is 3 and <code>a.length * 2</code> is 6.', 'The text becomes <code>Total: 6 items</code>.'],
         code='const a = [1, 2, 3];\nconsole.log(`Total: ${a.length * 2} items`);'),
    calc('h', 'A test suite has 40 tests that take 1.5 s each. They run one after another. How many seconds does the run take?', '60', 'Multiply.', ['<span class="eq">40 × 1.5 = 60</span>'], alt=['60 s', '60s']),
    calc('h', 'The same 40 tests are split over 4 parallel workers evenly. How many seconds now?', '15', 'Each worker gets a quarter of the tests.', ['<span class="eq">40 ÷ 4 = 10 tests per worker</span>', '<span class="eq">10 × 1.5 = 15 s</span>'], alt=['15 s', '15s']),
    calc('x', 'A suite replaces 25 fixed waits of 2000 ms with auto-waits that take 300 ms on average. How many seconds does one run save?', '42.5', 'Work out the saving per wait first.',
         ['<span class="eq">2000 - 300 = 1700 ms saved per wait</span>', '<span class="eq">25 × 1700 = 42500 ms</span>', '<span class="eq">42500 ms = 42.5 s</span>'], alt=['42.5 s']),
    calc('x', 'What does this print?', '3', 'Only one line prints. Which value does it print?', ['<code>console.assert</code> prints only when its condition is false. <code>2 > 1</code> is true, so nothing prints.', 'The last line prints <code>x.length</code>, which is 3.'],
         code='const x = ["a", "b", "c"];\nconsole.assert(2 > 1, "never shown");\nconsole.log(x.length);'),
]

EX = [
    ex('greet', 'e', 'Say hello', '<p>Write <code>greet(name)</code> that returns the text <code>Hello, NAME!</code> using a template literal.</p>',
       'function greet(name) {\n  // return the greeting\n}\n',
       [('greet("Asha")', 'Hello, Asha!'), ('greet("QA team")', 'Hello, QA team!'), ('greet("")', 'Hello, !')],
       'function greet(name) {\n  return `Hello, ${name}!`;\n}', hint='Backticks and <code>${name}</code>.',
       why='A template literal places the value of <code>name</code> straight into the text.'),
    ex('seconds', 'm', 'Milliseconds to seconds', '<p>Test runners report time in milliseconds. Write <code>toSeconds(ms)</code> that returns a string with two decimals and an <code>s</code>, such as <code>"2.31 s"</code>.</p>',
       'function toSeconds(ms) {\n  \n}\n',
       [('toSeconds(2310)', '2.31 s'), ('toSeconds(0)', '0.00 s'), ('toSeconds(1005)', '1.00 s'), ('toSeconds(61500)', '61.50 s')],
       'function toSeconds(ms) {\n  return `${(ms / 1000).toFixed(2)} s`;\n}', hint='<code>toFixed(2)</code> gives exactly two decimals.',
       why='Divide by 1000 to get seconds, then <code>toFixed(2)</code> rounds and pads to two decimals.'),
    ex('summary', 'h', 'Count the results', '<p>Write <code>summarize(results)</code>. Each result has a <code>status</code> of <code>"passed"</code>, <code>"failed"</code> or <code>"skipped"</code>. Return an object with all three counts, even when a count is zero.</p>',
       'function summarize(results) {\n  \n}\n',
       [('summarize([{status:"passed"},{status:"failed"},{status:"passed"}])', {'passed': 2, 'failed': 1, 'skipped': 0}),
        ('summarize([])', {'passed': 0, 'failed': 0, 'skipped': 0}), ('summarize([{status:"skipped"}])', {'passed': 0, 'failed': 0, 'skipped': 1})],
       'function summarize(results) {\n  const out = { passed: 0, failed: 0, skipped: 0 };\n  for (const r of results) out[r.status]++;\n  return out;\n}',
       hint='Start with an object that already has all three keys set to 0.', why='Starting with every key at zero means an empty run still reports all three counts.'),
    ex('stack-line', 'x', 'Find the line in a stack trace', '<p>Write <code>firstLine(stack, file)</code>. It gets the text of a stack trace and a file name, and returns the line number (a number) of the first frame in that file, or <code>null</code> when the file is not in the trace.</p><p>A frame looks like <code>    at login (tests/login.spec.js:12:5)</code>.</p>',
       'function firstLine(stack, file) {\n  \n}\n',
       [('firstLine("Error: x\\n    at a (node:internal/x:1:1)\\n    at login (tests/login.spec.js:12:5)\\n    at run (tests/login.spec.js:40:3)", "login.spec.js")', 12),
        ('firstLine("TypeError: y\\n    at file:///app/cart.js:7:19", "cart.js")', 7), ('firstLine("Error\\n    at x (a.js:1:1)", "b.js")', None)],
       'function firstLine(stack, file) {\n  for (const line of stack.split("\\n")) {\n    const at = line.indexOf(file + ":");\n    if (at !== -1) {\n      return Number(line.slice(at + file.length + 1).split(":")[0]);\n    }\n  }\n  return null;\n}',
       hint='Split the text on <code>"\\n"</code>, find the line that contains <code>file + ":"</code>, then take the number after it.',
       why='Each stack frame ends with file, line and column separated by colons. The first match is the frame closest to where the error was thrown.'),
]

T = {
    'slug': 'js-getting-started', 'title': 'Getting Started with JavaScript', 'short': 'Getting started', 'emoji': '🚀', 'module': MODULE, 'minutes': 14,
    'lead': 'What JavaScript is, where it runs, how to set up Node.js, how to print with the console, how a page loads scripts and how to read the errors you will meet every day.',
    'desc': 'What JavaScript is, engines and runtimes, installing Node.js, the console, scripts in a page, strict mode and reading error messages.',
    'summary': 'What JavaScript is and where it runs, ECMAScript and TC39, engines and runtimes, installing Node.js and VS Code, your first program, the console toolbox, script loading with defer and async, strict mode and how to read errors and stack traces.',
    'keywords': ['JavaScript', 'introduction', 'ECMAScript', 'Node.js', 'console', 'DevTools', 'strict mode', 'error messages', 'stack trace', 'script tag', 'first program'],
    'qa_intro': 'Parts marked 🧪 QA essential are what you need before writing Playwright, Cypress, WebdriverIO or Selenium tests in JavaScript. Press "Show the QA path only" to hide the rest.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
