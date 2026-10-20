# Chapter 9: ES modules and CommonJS, npm and package.json, TypeScript, ESLint and Prettier, environment config, a test project layout.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🏗️', 'Structure and tooling', 'js-structure', 'Classes, modules, packages, TypeScript and the tools that keep a growing codebase and test suite in order.')

NODE_TEST_TIMES = [(r'duration_ms [\d.]+', 'duration_ms 0.5'), (r'\(\d+(\.\d+)?ms\)', '(0.5ms)')]

CODES = {
    'esm': run('''
import formatPrice, { TAX_RATE, addTax, Cart as ShoppingCart } from "./money.mjs";
import * as money from "./money.mjs";       // everything, as one object

console.log(TAX_RATE, addTax(100));
console.log(formatPrice(2695));
const cart = new ShoppingCart();
console.log(cart.add(500).add(250).total);
console.log(Object.keys(money));
''', 'Named and default exports', play=False, extra={'money.mjs': '''
export const TAX_RATE = 0.18;

export function addTax(amount) {
  return Math.round(amount * (1 + TAX_RATE));
}

export class Cart {
  total = 0;
  add(price) { this.total += price; return this; }
}

export default function formatPrice(amount) {
  return `₹${amount.toLocaleString("en-IN")}`;
}
'''}),
    'dynamic': run('''
// Top level await: modules may await without an async function
const lang = process.env.APP_LANG ?? "hi";

// Dynamic import loads a module only when it is needed
const { default: messages } = await import(`./messages/${lang}.mjs`);
console.log(messages.welcome);

// JSON can be imported with an import attribute
import settings from "./settings.json" with { type: "json" };
console.log(settings.retries, settings.baseURL);

console.log(import.meta.filename.split("/").at(-1));
''', 'Dynamic import, JSON modules and import.meta', play=False, extra={
        'messages/hi.mjs': 'export default { welcome: "नमस्ते" };',
        'settings.json': '{ "baseURL": "https://staging.shop.example", "retries": 2 }'}),
    'cjs': run('''
const { slugify } = require("./text.cjs");     // CommonJS: require and module.exports
const path = require("node:path");

console.log(slugify("Add to Cart Button"));
console.log(path.join("tests", "e2e", "login.spec.js"));
console.log(typeof module.exports, typeof __dirname);

// Since Node 22, require() can also load an ES module that has no top level await
const { addTax } = require("./money.mjs");
console.log(addTax(100));
''', 'CommonJS: require and module.exports', play=False, file='main.cjs', extra={
        'text.cjs': '''
function slugify(text) {
  return text.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-");
}
module.exports = { slugify };
''',
        'money.mjs': 'export const addTax = amount => Math.round(amount * 1.18);'}),
    'package-json': show('''
{
  "name": "shop-tests",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "engines": { "node": ">=22" },
  "scripts": {
    "test": "npm run test:unit && npm run test:api",
    "test:unit": "vitest run",
    "test:api": "node --test tests/api/",
    "test:e2e": "playwright test",
    "lint": "eslint .",
    "format": "prettier --write ."
  },
  "dependencies": {
    "ajv": "^8.17.1"
  },
  "devDependencies": {
    "@playwright/test": "~1.56.0",
    "vitest": "^5.0.0",
    "eslint": "10.13.0"
  }
}
''', 'A package.json for a test project', lang='json', note='Reference', result='"type": "module" makes .js files ES modules. Scripts run with npm run test:unit. devDependencies are tools only needed to build and test.'),
    'npm-cmds': show('''
npm init -y                      # create package.json
npm install ajv                  # add a dependency (writes package.json and package-lock.json)
npm install -D @playwright/test  # add a dev dependency
npm ci                           # clean install exactly what the lock file says (use this in CI)
npm run test:unit                # run a script from package.json
npm test -- --reporter=verbose   # pass extra options to the script after --
npx playwright test --headed     # run a tool from node_modules/.bin
npm outdated                     # what has newer versions
npm audit                        # known security problems in dependencies
''', 'The npm commands you use every week', lang='bash', note='Reference'),
    'semver': run('''
import semver from "semver";            // a package from node_modules

const checks = [
  ["^1.56.0", "1.58.2"], ["^1.56.0", "2.0.0"],
  ["~1.56.0", "1.56.9"], ["~1.56.0", "1.57.0"],
  ["1.56.1", "1.56.2"], ["^0.4.2", "0.5.0"],
];
for (const [range, version] of checks) {
  console.log(range.padEnd(8), version.padEnd(7), semver.satisfies(version, range) ? "allowed" : "not allowed");
}
console.log(semver.maxSatisfying(["1.55.0", "1.56.4", "1.60.1", "2.1.0"], "^1.56.0"));
''', 'What ^ and ~ allow', play=False),
    'ts-run': run('''
type Status = "passed" | "failed" | "skipped";

interface TestResult {
  name: string;
  status: Status;
  durationMs: number;
  retries?: number;              // optional
}

function slowest<T extends { durationMs: number }>(items: T[], count = 1): T[] {
  return items.toSorted((a, b) => b.durationMs - a.durationMs).slice(0, count);
}

const results: TestResult[] = [
  { name: "login", status: "passed", durationMs: 840 },
  { name: "checkout", status: "failed", durationMs: 2310, retries: 2 },
  { name: "search", status: "passed", durationMs: 120 },
];

const failed = results.filter(r => r.status === "failed").map(r => r.name);
console.log(failed, slowest(results)[0].name);
''', 'TypeScript runs directly in Node.js', file='report.ts', play=False),
    'tsc': test({
        'package.json': pkg('typed', 'module', {'typecheck': 'tsc'}),
        'tsconfig.json': '''
{
  "compilerOptions": {
    "target": "es2024",
    "module": "nodenext",
    "strict": true,
    "noEmit": true,
    "erasableSyntaxOnly": true
  },
  "include": ["src"]
}
''',
        'src/order.ts': '''
interface Order {
  id: number;
  total: number;
  coupon?: string;
}

export function discount(order: Order): number {
  return order.coupon.length > 0 ? order.total * 0.9 : order.total;
}

discount({ id: 7, total: "499" });
''',
    }, 'npx tsc', 'The type checker finds bugs before any test runs', show=['tsconfig.json', 'src/order.ts'], expect='fail', badge='🔎 Type check, finds 2 errors'),
    'eslint': test({
        'package.json': pkg('linted', 'module', {'lint': 'eslint .'}),
        'eslint.config.js': '''
import js from "@eslint/js";
import globals from "globals";

export default [
  js.configs.recommended,
  {
    languageOptions: { globals: { ...globals.node } },
    rules: {
      eqeqeq: "error",
      "no-unused-vars": "error",
      "require-await": "error",
    },
  },
];
''',
        'tests/cart.test.js': '''
import { test } from "node:test";
import assert from "node:assert/strict";

test("cart total", async () => {
  const items = [{ price: 100 }, { price: "50" }];
  const unused = 3;
  let total = 0;
  for (const i of items) total += Number(i.price);
  assert.ok(total == 150);
  assert.equal(totl, 150);
});
''',
    }, 'npx eslint .', 'ESLint reads the code and reports problems', expect='fail', badge='🔎 Lint, finds problems'),
    'prettier': test({
        'package.json': pkg('pretty', 'module'),
        'messy.js': '''
const user={name:"Asha",roles:[ 'admin','qa' ],active:true}
function greet( u ){return `Hello, ${u.name}`}
''',
    }, 'npx prettier messy.js', 'Prettier rewrites the layout, never the meaning', badge='✨ Formatter runs'),
    'env': run('''
// Values come from .env, which Node.js loads with --env-file
const config = {
  env: process.env.TEST_ENV,
  baseURL: process.env.BASE_URL,
  user: process.env.TEST_USER,
  headless: process.env.HEADLESS !== "false",
  workers: Number(process.env.WORKERS ?? 2),
};
console.log(config);
console.log("password loaded:", Boolean(process.env.TEST_PASSWORD), "| length:", process.env.TEST_PASSWORD.length);
''', 'Configuration from environment variables', play=False, flags=['--env-file=.env'], extra={'.env': '''
# Never commit real secrets. Keep .env in .gitignore and use CI secrets instead.
TEST_ENV=staging
BASE_URL=https://staging.shop.example
TEST_USER=qa.bot@shop.example
TEST_PASSWORD=not-a-real-password
HEADLESS=true
'''}),
    'project': test({
        'package.json': pkg('shop-tests', 'module', {'test:unit': 'node --test --test-reporter=spec tests/unit/', 'test:api': 'node --test --test-reporter=spec tests/api/'}),
        'src/price.js': '''
export function addTax(amount, rate = 0.18) {
  return Math.round(amount * (1 + rate) * 100) / 100;
}
''',
        'src/api.js': '''
export function buildQuery(params) {
  return new URLSearchParams(Object.entries(params).filter(([, v]) => v != null)).toString();
}
''',
        'tests/unit/price.test.js': '''
import { test } from "node:test";
import assert from "node:assert/strict";
import { addTax } from "../../src/price.js";

test("adds 18% by default", () => assert.equal(addTax(100), 118));
test("rounds to paise", () => assert.equal(addTax(9.99), 11.79));
''',
        'tests/api/query.test.js': '''
import { test } from "node:test";
import assert from "node:assert/strict";
import { buildQuery } from "../../src/api.js";

test("drops empty filters", () => {
  assert.equal(buildQuery({ q: "pen", page: 2, sort: null }), "q=pen&page=2");
});
''',
    }, 'npm run -s test:unit && npm run -s test:api', 'Separate scripts for each kind of test', replace=NODE_TEST_TIMES),
}

PARTS = [
    part('esm', '📦', 'ES modules: import and export', '''
<p>A <b>module</b> is a file with its own scope. Nothing inside it is visible to other files unless it is <b>exported</b>, and nothing from outside is available unless it is <b>imported</b>. This keeps large codebases and test suites tidy: page objects, helpers and test data each live in their own file.</p>
[[esm]]
<div class="tw"><table class="jt"><tr><th>Syntax</th><th>Meaning</th></tr>
<tr><td><code>export const x</code>, <code>export function f</code></td><td>named export, imported with the same name in braces</td></tr>
<tr><td><code>export default ...</code></td><td>one main value per file, imported with any name</td></tr>
<tr><td><code>import { a as b }</code></td><td>rename while importing</td></tr>
<tr><td><code>import * as ns</code></td><td>every export as one object</td></tr>
<tr><td><code>await import("./x.js")</code></td><td>load later, only when needed</td></tr>
</table></div>
<p>Modules are always strict, run once however many files import them, and may use <code>await</code> at the top level.</p>
[[dynamic]]
<div class="tip">Many teams avoid default exports: named exports keep the same name in every file, which makes search and automatic refactoring reliable.</div>
''', qa=True, qa_why='Every test file imports a runner, page objects and helpers. Playwright, Vitest and WebdriverIO projects are ES modules by default.',
        kw=['module', 'ES modules', 'ESM', 'import', 'export', 'default export', 'named export', 'dynamic import', 'top level await', 'import attributes', 'JSON modules', 'import.meta']),
    part('cjs', '🧱', 'CommonJS and how the two mix', '''
<p>Before ES modules, Node.js used <b>CommonJS</b>: <code>require()</code> to load and <code>module.exports</code> to share. Older packages, Jest setups, Mocha and many Selenium projects still use it, so you will read both styles.</p>
[[cjs]]
<div class="tw"><table class="jt"><tr><th></th><th>ES modules</th><th>CommonJS</th></tr>
<tr><td>Load</td><td><code>import</code>, loaded before the code runs</td><td><code>require()</code>, a normal function call</td></tr>
<tr><td>Share</td><td><code>export</code></td><td><code>module.exports</code></td></tr>
<tr><td>Chosen by</td><td><code>.mjs</code>, or <code>.js</code> with <code>"type": "module"</code></td><td><code>.cjs</code>, or <code>.js</code> without it</td></tr>
<tr><td>Top level await</td><td>yes</td><td>no</td></tr>
<tr><td>Where you see it</td><td>Playwright, Vitest, browsers, new code</td><td>older Node.js code, Jest by default, Mocha</td></tr>
</table></div>
<div class="warn">The error <code>Cannot use import statement outside a module</code> means a file with <code>import</code> is being treated as CommonJS. Add <code>"type": "module"</code> to package.json or rename the file to <code>.mjs</code>.</div>
''', qa=['Jest', 'Mocha', 'Selenium'], qa_why='Jest, Mocha and many Selenium projects are CommonJS, and mixing the two styles causes the most common set up errors.',
        kw=['CommonJS', 'require', 'module.exports', '.cjs', '.mjs', 'type module', 'Cannot use import statement outside a module', '__dirname', 'require esm']),
    part('npm', '📥', 'npm and package.json', '''
<p><b>npm</b> installs packages from the npm registry into <code>node_modules</code> and records them in <b>package.json</b>. The <b>lock file</b> (<code>package-lock.json</code>) pins the exact version of every package, so every laptop and CI machine installs the same thing.</p>
[[package-json]]
<h3>Version ranges</h3>
<p>Versions follow <b>semantic versioning</b>: <code>MAJOR.MINOR.PATCH</code>. A major bump may break your code. A caret <code>^</code> allows new minor and patch versions. A tilde <code>~</code> allows only new patches. No symbol means that exact version. Below 1.0.0 the caret is stricter: <code>^0.4.2</code> allows only <code>0.4.x</code>, because in a 0.x package every minor release may break things.</p>
[[semver]]
[[npm-cmds]]
<div class="qa-box">Use <code>npm ci</code> in pipelines, not <code>npm install</code>. It fails if package.json and the lock file disagree, and it never changes the lock file. Pin browser automation tools such as Playwright exactly or with <code>~</code>, because a new version also brings new browser builds.</div>
''', qa=True, qa_why='Installing, pinning and updating test tools, and running them through npm scripts, is part of every automation project.',
        kw=['npm', 'package.json', 'package-lock.json', 'node_modules', 'dependencies', 'devDependencies', 'scripts', 'npm ci', 'npx', 'semver', 'caret', 'tilde', 'npm audit']),
    part('typescript', '🔷', 'TypeScript', '''
<p><b>TypeScript</b> is JavaScript with types added. You describe the shape of your data once, and the type checker warns you about wrong property names, missing fields and wrong value types while you type, long before a test runs. Playwright, Angular and most new projects use it, and its tests are usually written in it too.</p>
[[ts-run]]
<p>Node.js 23.6 and later run <code>.ts</code> files directly by removing the type annotations. It does not check them. Checking is the job of <code>tsc</code>, the TypeScript compiler, usually run as its own step in CI.</p>
[[tsc]]
<div class="tw"><table class="jt"><tr><th>Syntax</th><th>Meaning</th></tr>
<tr><td><code>let n: number</code></td><td>a type annotation</td></tr>
<tr><td><code>interface User { name: string; age?: number }</code></td><td>the shape of an object, <code>?</code> marks optional</td></tr>
<tr><td><code>type Status = "passed" | "failed"</code></td><td>a union: one of these values</td></tr>
<tr><td><code>function first&lt;T&gt;(list: T[]): T</code></td><td>a generic: works for any type T</td></tr>
<tr><td><code>value as string</code></td><td>tell the checker you know better (use rarely)</td></tr>
</table></div>
<div class="modern">The <code>erasableSyntaxOnly</code> option (TypeScript 5.8) keeps you to type syntax that Node.js can simply remove, which is what makes running .ts files without a build step work.</div>
''', qa=['Playwright', 'Cypress', 'WebdriverIO'], qa_why='Playwright and most modern frameworks generate TypeScript projects, and typed page objects catch broken locators and data at edit time.',
        kw=['TypeScript', 'types', 'interface', 'type alias', 'union', 'generics', 'tsc', 'tsconfig', 'type stripping', 'strict', 'erasableSyntaxOnly', 'optional property']),
    part('lint', '🧹', 'ESLint and Prettier', '''
<p><b>ESLint</b> reads your code without running it and reports likely bugs and risky habits: unused variables, typos in names, <code>==</code> where <code>===</code> was meant, an <code>async</code> function that never awaits. Rules live in <code>eslint.config.js</code>.</p>
[[eslint]]
<p><b>Prettier</b> only formats: spaces, quotes, line breaks and commas. It ends style discussions in code review because everyone's code comes out the same.</p>
[[prettier]]
<div class="qa-box">Lint test code too. Plugins such as <code>eslint-plugin-playwright</code>, <code>eslint-plugin-jest</code> and <code>eslint-plugin-cypress</code> catch a missing <code>await</code> before an action, a forgotten <code>test.only</code> and conditionals inside tests. With TypeScript, the <code>@typescript-eslint/no-floating-promises</code> rule finds the missing <code>await</code> that causes most flaky Playwright tests.</div>
''', qa=['Playwright', 'Jest', 'Cypress'], qa_why='A missing await or a forgotten test.only is caught by the linter before it reaches CI.',
        kw=['ESLint', 'lint', 'eslint.config.js', 'flat config', 'rules', 'Prettier', 'format', 'no-unused-vars', 'eqeqeq', 'no-floating-promises', 'eslint-plugin-playwright']),
    part('env', '🔐', 'Environment variables and config', '''
<p>The same tests must run against a laptop, a staging server and sometimes production. The parts that change, such as the base URL, user names and secrets, come from <b>environment variables</b> in <code>process.env</code>. Node.js can load them from a <code>.env</code> file with <code>--env-file</code>, with no extra package.</p>
[[env]]
<div class="warn">Everything in <code>process.env</code> is a string. <code>"false"</code> is truthy, so compare with <code>=== "true"</code> or <code>!== "false"</code>, and turn numbers into numbers. Never commit passwords or tokens: add <code>.env</code> to <code>.gitignore</code> and use your CI tool's secret store.</div>
''', qa=True, qa_why='Choosing the target environment, test users and secrets through variables is how one suite runs against every environment.',
        kw=['environment variables', 'process.env', '.env', '--env-file', 'dotenv', 'secrets', 'config', 'baseURL', 'staging']),
    part('scenario', '🎬', 'Real world scenario: lay out a test project', '''
<div class="scenario"><b>The situation</b>You are starting the automation project for a shop. Unit tests, API tests and end to end tests must be runnable on their own, and CI must be able to run each of them as a separate job.</div>
<p>Source code lives in <code>src</code>. Tests are split by kind under <code>tests</code>. Each kind gets its own npm script, so a developer runs <code>npm run test:unit</code> in seconds while CI runs every script.</p>
[[project]]
<div class="tip"><b>A typical layout</b><pre class="tree">shop-tests/
  package.json, package-lock.json, tsconfig.json, eslint.config.js
  .env.example        names of the variables, no real values
  src/                helpers, API clients, test data builders
  pages/              page objects
  tests/unit/         fast checks of pure functions
  tests/api/          HTTP requests against a running server
  tests/e2e/          browser tests with Playwright or Cypress
  playwright.config.ts</pre></div>
''', qa=True, kw=['project structure', 'folder layout', 'npm scripts', 'test:unit', 'test:api', 'test:e2e', 'node --test', 'CI jobs']),
]

INFO = {'title': 'From one file to a real project', 'panels': [
    panel([['e', '📦'], ['t', 'import { addTax } from "./money.js"', {'b': 1, 'size': 11}]], 'Modules', 'Each file shares only what it exports.', 'ES modules in new code, CommonJS in older code.'),
    panel([['e', '📥'], ['t', 'npm ci', {'b': 1}]], 'Packages', 'npm installs tools and records exact versions.', 'The lock file makes every machine install the same thing.'),
    panel([['e', '🔷'], ['t', 'total: number', {'b': 1}]], 'Types', 'TypeScript catches wrong data while you type.', 'Node.js runs .ts files, tsc checks them.'),
    panel([['e', '🧹'], ['t', 'eslint . && prettier --check .', {'b': 1, 'size': 11}]], 'Quality gates', 'Lint finds risky code, Prettier fixes layout.', 'Both run in CI before the tests.')],
    'remember': 'Modules split the code, npm brings the tools, TypeScript and ESLint catch mistakes before tests run.'}

REAL = [
    ['🏭', 'A monorepo', 'A company keeps its web app, its API and its Playwright suite in one repository with npm workspaces, so a change and its tests land in one pull request.'],
    ['🔒', 'A supply chain alert', 'npm audit flags a vulnerable package in the test tools. The team updates it in the lock file and CI confirms nothing broke.'],
    ['🌍', 'One suite, three environments', 'The same Playwright tests run against dev, staging and pre-production by changing BASE_URL and the test user in the CI job.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers modules, npm and package.json, TypeScript, ESLint and Prettier, environment variables and the layout of a test project.',
        'यह अध्याय modules, npm और package.json, TypeScript, ESLint और Prettier, environment variables और test project का ढांचा सिखाता है।',
        'ಈ ಅಧ್ಯಾಯ modules, npm ಮತ್ತು package.json, TypeScript, ESLint ಮತ್ತು Prettier, environment variables ಮತ್ತು test project ರಚನೆ ಕಲಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ modules, npm ଓ package.json, TypeScript, ESLint ଓ Prettier, environment variables ଓ test project ର ଗଠନ ଶିଖାଏ।',
        'يتناول هذا الفصل الوحدات وnpm وملف package.json وTypeScript وESLint وPrettier ومتغيرات البيئة وتنظيم مشروع الاختبار.',
        'Dieses Kapitel behandelt Module, npm und package.json, TypeScript, ESLint und Prettier, Umgebungsvariablen und den Aufbau eines Testprojekts.'),
    say('esm', 'ES modules', 'Each module shares only what it exports. Import named values in braces, a default value with any name, or load a module later with dynamic import.',
        'हर module सिर्फ वही share करता है जो वह export करता है। Named values braces में import करें, default किसी भी नाम से।',
        'ಪ್ರತಿ module ತಾನು export ಮಾಡಿದ್ದನ್ನು ಮಾತ್ರ ಹಂಚುತ್ತದೆ. Named values braces ನಲ್ಲಿ, default ಯಾವುದೇ ಹೆಸರಿನಲ್ಲಿ import ಮಾಡಿ.',
        'ପ୍ରତ୍ୟେକ module କେବଳ ଯାହା export କରେ ତାହା share କରେ। Named values braces ରେ, default ଯେକୌଣସି ନାମରେ import କରନ୍ତୁ।',
        'تشارك كل وحدة ما تصدره فقط. استورد القيم المسماة بين أقواس، والقيمة الافتراضية بأي اسم، أو حمّل وحدة لاحقًا بالاستيراد الديناميكي.',
        'Jedes Modul teilt nur, was es exportiert. Benannte Werte in Klammern importieren, den Standardwert unter beliebigem Namen.'),
    say('cjs', 'CommonJS', 'Older code uses require and module exports. The file extension or the type field in package json decides which style a file uses.',
        'पुराना code require और module.exports इस्तेमाल करता है। File extension या package.json का type तय करता है कि कौन सा style है।',
        'ಹಳೆಯ code require ಮತ್ತು module.exports ಬಳಸುತ್ತದೆ. File extension ಅಥವಾ package.json ನ type style ನಿರ್ಧರಿಸುತ್ತದೆ.',
        'ପୁରୁଣା code require ଓ module.exports ବ୍ୟବହାର କରେ। File extension କିମ୍ବା package.json ର type style ସ୍ଥିର କରେ।',
        'يستخدم الكود القديم require وmodule.exports. يحدد امتداد الملف أو حقل type في package.json النمط المستخدم.',
        'Älterer Code nutzt require und module.exports. Die Dateiendung oder das type-Feld in package.json entscheidet den Stil.'),
    say('npm', 'npm', 'npm installs packages and records them in package json. The lock file pins exact versions, and npm ci installs exactly those in CI.',
        'npm packages install करता है और package.json में लिखता है। Lock file exact versions तय करती है, और CI में npm ci वही install करता है।',
        'npm packages install ಮಾಡಿ package.json ನಲ್ಲಿ ಬರೆಯುತ್ತದೆ. Lock file exact versions ಸ್ಥಿರಗೊಳಿಸುತ್ತದೆ, CI ನಲ್ಲಿ npm ci ಅವನ್ನೇ install ಮಾಡುತ್ತದೆ.',
        'npm packages install କରି package.json ରେ ଲେଖେ। Lock file exact versions ସ୍ଥିର କରେ, CI ରେ npm ci ସେଗୁଡ଼ିକୁ install କରେ।',
        'يثبت npm الحزم ويسجلها في package.json. يثبت ملف القفل الإصدارات بدقة، ويثبتها npm ci كما هي في CI.',
        'npm installiert Pakete und trägt sie in package.json ein. Die Lock-Datei fixiert Versionen, npm ci installiert genau diese im CI.'),
    say('typescript', 'TypeScript', 'TypeScript adds types to JavaScript. Node runs ts files by removing the types, and tsc checks them for mistakes.',
        'TypeScript JavaScript में types जोड़ता है। Node types हटाकर ts files चलाता है, और tsc गलतियां जांचता है।',
        'TypeScript JavaScript ಗೆ types ಸೇರಿಸುತ್ತದೆ. Node types ತೆಗೆದು ts files ಓಡಿಸುತ್ತದೆ, tsc ತಪ್ಪುಗಳನ್ನು ಪರಿಶೀಲಿಸುತ್ತದೆ.',
        'TypeScript JavaScript ରେ types ଯୋଡ଼େ। Node types ହଟାଇ ts files ଚଲାଏ, ଏବଂ tsc ଭୁଲ ଯାଞ୍ଚ କରେ।',
        'يضيف TypeScript الأنواع إلى JavaScript. يشغل Node ملفات ts بإزالة الأنواع، ويتحقق tsc من الأخطاء.',
        'TypeScript ergänzt JavaScript um Typen. Node führt ts-Dateien ohne Typen aus, tsc prüft sie auf Fehler.'),
    say('lint', 'Lint and format', 'ESLint finds risky code without running it. Prettier formats code the same way for everyone. Lint your tests too.',
        'ESLint code चलाए बिना जोखिम भरा code ढूंढता है। Prettier सबका code एक जैसा format करता है। Tests को भी lint करें।',
        'ESLint code ಓಡಿಸದೆ ಅಪಾಯಕಾರಿ code ಹುಡುಕುತ್ತದೆ. Prettier ಎಲ್ಲರ code ಒಂದೇ ರೀತಿ format ಮಾಡುತ್ತದೆ. Tests ಅನ್ನೂ lint ಮಾಡಿ.',
        'ESLint code ନ ଚଲାଇ ବିପଦଜନକ code ଖୋଜେ। Prettier ସମସ୍ତଙ୍କ code ଏକା ପରି format କରେ। Tests କୁ ମଧ୍ୟ lint କରନ୍ତୁ।',
        'يجد ESLint الكود الخطر دون تشغيله. ينسق Prettier الكود بالطريقة نفسها للجميع. افحص اختباراتك أيضًا.',
        'ESLint findet riskanten Code, ohne ihn auszuführen. Prettier formatiert für alle gleich. Prüfe auch deine Tests.'),
    say('env', 'Environment', 'Settings that change between environments come from process env. Everything there is a string, and secrets never go into git.',
        'Environments के बीच बदलने वाली settings process.env से आती हैं। वहां सब string है, और secrets कभी git में न डालें।',
        'Environments ನಡುವೆ ಬದಲಾಗುವ settings process.env ನಿಂದ ಬರುತ್ತವೆ. ಅಲ್ಲಿ ಎಲ್ಲವೂ string, secrets git ಗೆ ಹಾಕಬೇಡಿ.',
        'Environments ମଧ୍ୟରେ ବଦଳୁଥିବା settings process.env ରୁ ଆସେ। ସେଠାରେ ସବୁ string, ଏବଂ secrets git ରେ ରଖନ୍ତୁ ନାହିଁ।',
        'تأتي الإعدادات التي تتغير بين البيئات من process.env. كل ما فيها نص، ولا تضع الأسرار في git أبدًا.',
        'Einstellungen, die sich je Umgebung ändern, kommen aus process.env. Alles dort ist Text, Geheimnisse gehören nie ins Git.'),
    say('scenario', 'Scenario', 'A test project keeps source, page objects and each kind of test in its own folder, with one npm script per kind.',
        'Test project source, page objects और हर तरह के test को अलग folder में रखता है, हर तरह के लिए एक npm script के साथ।',
        'Test project source, page objects ಮತ್ತು ಪ್ರತಿ ರೀತಿಯ test ಅನ್ನು ಬೇರೆ folder ನಲ್ಲಿ ಇಡುತ್ತದೆ, ಪ್ರತಿಯೊಂದಕ್ಕೂ ಒಂದು npm script.',
        'Test project source, page objects ଓ ପ୍ରତ୍ୟେକ ପ୍ରକାର test କୁ ଅଲଗା folder ରେ ରଖେ, ପ୍ରତ୍ୟେକ ପାଇଁ ଗୋଟିଏ npm script।',
        'يحفظ مشروع الاختبار الكود وكائنات الصفحات وكل نوع من الاختبارات في مجلد خاص، مع سكربت npm لكل نوع.',
        'Ein Testprojekt hält Quellcode, Page Objects und jede Testart in eigenen Ordnern, mit einem npm-Skript pro Art.'),
    say('practice', 'Hands-on', 'Practise reading configuration, checking version ranges, parsing an env file and resolving import paths.',
        'Configuration पढ़ना, version ranges जांचना, env file parse करना और import paths निकालने का अभ्यास करें।',
        'Configuration ಓದುವುದು, version ranges ಪರಿಶೀಲಿಸುವುದು, env file parse ಮಾಡುವುದು ಮತ್ತು import paths ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Configuration ପଢ଼ିବା, version ranges ଯାଞ୍ଚ, env file parse ଓ import paths ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على قراءة الإعدادات وفحص نطاقات الإصدارات وتحليل ملف env وحل مسارات الاستيراد.',
        'Übe das Lesen von Konfiguration, Versionsbereiche, das Parsen einer env-Datei und das Auflösen von Importpfaden.'),
]

QUIZ = [
    quiz('e', 'Which line imports a named export called addTax?', ['import { addTax } from "./money.js"', 'import addTax from "./money.js"', 'require addTax from "./money.js"', 'import "./money.js" as addTax'], 0, 'Named exports go in braces.', 'Without braces you would get the default export instead.'),
    quiz('e', 'Which command should CI use to install dependencies?', ['npm ci', 'npm install', 'npm update', 'npx install'], 0, 'Clean and exact.', '<code>npm ci</code> installs exactly what the lock file says and fails if it is out of date.'),
    quiz('e', 'Where do test tools such as Playwright and Jest usually go?', ['devDependencies', 'dependencies', 'scripts', 'engines'], 0, 'Needed only to build and test.', 'devDependencies are not installed when the app itself is deployed.'),
    quiz('m', 'What does "^1.56.0" allow?', ['1.56.0 up to, but not including, 2.0.0', 'Only 1.56.x', 'Only 1.56.0', 'Any version'], 0, 'Caret: same major.', 'A caret allows new minor and patch versions within major version 1.'),
    quiz('m', 'You see "Cannot use import statement outside a module". What is the usual fix?', ['Add "type": "module" to package.json or use .mjs', 'Install the import package', 'Use var instead of const', 'Restart the computer'], 0, 'The file is being treated as CommonJS.', 'Node.js decides the module system from the extension and the type field.'),
    quiz('m', 'process.env.HEADLESS is "false". What is Boolean(process.env.HEADLESS)?', ['true', 'false', 'undefined', 'It throws'], 0, 'Every non empty string is truthy.', 'Environment values are strings, so compare them as text.'),
    quiz('h', 'What does Node.js do with type annotations in a .ts file?', ['Removes them and runs the code without checking them', 'Checks them and refuses to run', 'Converts them to JSDoc', 'Ignores the whole file'], 0, 'Type stripping.', 'Checking is done separately by <code>tsc</code>.'),
    quiz('h', 'Which tool would report total == 150 when the rule eqeqeq is on?', ['ESLint', 'Prettier', 'npm', 'tsc'], 0, 'A rule about code quality.', 'Prettier only changes layout. ESLint enforces rules like using ===.'),
    quiz('h', 'A module is imported by five test files. How many times does its top level code run?', ['Once', 'Five times', 'Never', 'Once per test'], 0, 'Modules are cached.', 'A module is evaluated once, and every importer shares the same exports.'),
    quiz('x', 'Why might a team avoid export default?', ['Named exports keep one name everywhere, which helps search and refactoring', 'Default exports are slower', 'Default exports are not standard', 'Default exports cannot be functions'], 0, 'import Foo vs import Bar of the same thing.', 'Each importer can call a default export by a different name, which makes code harder to search.'),
    quiz('x', 'What does a lock file protect you from?', ['A dependency getting a new version between two installs and changing behaviour', 'Viruses', 'Running out of disk', 'Syntax errors'], 0, 'Reproducible installs.', 'Without a lock file, a range like ^1.2.0 can resolve to a different version tomorrow.'),
    quiz('x', 'Which TypeScript error did tsc report first for discount({ id: 7, total: "499" })?', ['order.coupon is possibly undefined', 'id must be a string', 'discount is not exported', 'interface is a reserved word'], 0, 'coupon has a question mark.', 'An optional property may be undefined, so calling <code>.length</code> on it is flagged. The string total is the second error.'),
]

CALC = [
    calc('e', 'A project has 3 dependencies and 5 devDependencies. How many packages does package.json list?', '8', 'Add both lists.', ['<span class="eq">3 + 5 = 8</span>']),
    calc('e', 'What is the MAJOR number in version 4.12.7?', '4', 'MAJOR.MINOR.PATCH.', ['The first number is the major version.']),
    calc('m', 'Which of 1.56.9, 1.57.0, 2.0.0 does "~1.56.0" allow? Answer with how many.', '1', 'Tilde: same minor.', ['Only 1.56.9 keeps minor version 56.']),
    calc('m', 'Unit tests take 20 s, API tests 90 s, e2e tests 6 minutes. In seconds, how long is the whole run one after another?', '470', 'Turn minutes into seconds.', ['<span class="eq">6 × 60 = 360</span>', '<span class="eq">20 + 90 + 360 = 470</span>']),
    calc('h', 'The same three jobs run in parallel CI jobs. In seconds, how long until all are done?', '360', 'The slowest job decides.', ['Parallel jobs finish when the longest one ends: 360 s.']),
    calc('h', 'WORKERS is "4" in .env. What is process.env.WORKERS + 1?', '41', 'A string plus a number.', ['Environment values are strings.', '<span class="eq">"4" + 1 = "41"</span>'], alt=['"41"']),
    calc('x', 'How many errors did tsc report for src/order.ts?', '2', 'Read the output.', ['coupon is possibly undefined.', 'The string "499" is not a number.']),
    calc('x', 'semver.maxSatisfying(["1.55.0", "1.56.4", "1.60.1", "2.1.0"], "^1.56.0") returned what?', '1.60.1', 'The highest version inside the range.', ['1.55.0 is too low and 2.1.0 is a new major.', 'Of 1.56.4 and 1.60.1, the higher is 1.60.1.']),
]

EX = [
    ex('env-parse', 'e', 'Parse an env file', '<p>Write <code>parseEnv(text)</code> that turns lines like <code>KEY=value</code> into an object. Skip empty lines and lines starting with <code>#</code>. Values may contain <code>=</code>, so split only at the first one.</p>',
       'function parseEnv(text) {\n  \n}\n',
       [('parseEnv("A=1\\nB=two")', {'A': '1', 'B': 'two'}), ('parseEnv("# comment\\n\\nURL=https://x.example/?a=b")', {'URL': 'https://x.example/?a=b'}), ('parseEnv("")', {})],
       'function parseEnv(text) {\n  const out = {};\n  for (const line of text.split("\\n")) {\n    const t = line.trim();\n    if (!t || t.startsWith("#")) continue;\n    const i = t.indexOf("=");\n    out[t.slice(0, i)] = t.slice(i + 1);\n  }\n  return out;\n}',
       hint='Use <code>indexOf("=")</code> and <code>slice</code>, not <code>split("=")</code>.', why='URLs and tokens often contain <code>=</code>, so splitting at every one would cut them apart.'),
    ex('config', 'm', 'Typed config from strings', '<p>Write <code>loadConfig(env)</code> that reads a plain object of strings and returns <code>{ baseURL, headless, workers }</code>. <code>baseURL</code> defaults to <code>"http://localhost:3000"</code>. <code>headless</code> is false only when the value is exactly <code>"false"</code>. <code>workers</code> is a number, default 2.</p>',
       'function loadConfig(env) {\n  \n}\n',
       [('loadConfig({})', {'baseURL': 'http://localhost:3000', 'headless': True, 'workers': 2}),
        ('loadConfig({ BASE_URL: "https://staging.example", HEADLESS: "false", WORKERS: "4" })', {'baseURL': 'https://staging.example', 'headless': False, 'workers': 4})],
       'function loadConfig(env) {\n  return {\n    baseURL: env.BASE_URL ?? "http://localhost:3000",\n    headless: env.HEADLESS !== "false",\n    workers: Number(env.WORKERS ?? 2),\n  };\n}',
       hint='<code>??</code> gives defaults, <code>Number()</code> converts the text.', why='Turning strings into real types in one place means the rest of the suite never has to remember that env values are text.'),
    ex('caret', 'h', 'Does ^ allow it?', '<p>Write <code>caretAllows(range, version)</code> for ranges like <code>"^1.4.2"</code> and versions like <code>"1.9.0"</code>. Return true when the major numbers match and the version is not lower than the range. To keep it short, ignore the stricter rule for major version 0.</p>',
       'function caretAllows(range, version) {\n  \n}\n',
       [('caretAllows("^1.4.2", "1.9.0")', True), ('caretAllows("^1.4.2", "1.4.1")', False), ('caretAllows("^1.4.2", "2.0.0")', False), ('caretAllows("^1.4.2", "1.4.10")', True)],
       'function caretAllows(range, version) {\n  const [a1, a2, a3] = range.slice(1).split(".").map(Number);\n  const [b1, b2, b3] = version.split(".").map(Number);\n  if (a1 !== b1) return false;\n  if (b2 !== a2) return b2 > a2;\n  return b3 >= a3;\n}',
       hint='Turn both into three numbers. Compare minor first, then patch.', why='Comparing as numbers matters: as text, "1.4.10" would sort before "1.4.2".'),
    ex('resolve', 'x', 'Resolve an import path', '<p>Write <code>resolveImport(fromFile, spec)</code>. For a relative <code>spec</code> starting with <code>./</code> or <code>../</code>, return the path of the imported file relative to the project root, as Node.js would. For anything else (a package name), return <code>"node_modules/" + spec</code>.</p>',
       'function resolveImport(fromFile, spec) {\n  \n}\n',
       [('resolveImport("tests/unit/price.test.js", "../../src/price.js")', 'src/price.js'), ('resolveImport("tests/e2e/login.spec.js", "./helpers.js")', 'tests/e2e/helpers.js'),
        ('resolveImport("tests/a.js", "vitest")', 'node_modules/vitest')],
       'function resolveImport(fromFile, spec) {\n  if (!spec.startsWith("./") && !spec.startsWith("../")) return "node_modules/" + spec;\n  const parts = fromFile.split("/").slice(0, -1);\n  for (const piece of spec.split("/")) {\n    if (piece === "..") parts.pop();\n    else if (piece !== ".") parts.push(piece);\n  }\n  return parts.join("/");\n}',
       hint='Start from the folder of <code>fromFile</code>. <code>..</code> removes a folder, <code>.</code> does nothing, any other piece is added.', why='This is what happens every time a test imports a page object, and getting it wrong is the cause of most "Cannot find module" errors.'),
]

T = {
    'slug': 'js-modules-tooling', 'title': 'Modules, npm, TypeScript and Tooling', 'short': 'Modules and tooling', 'emoji': '📦', 'module': MODULE, 'minutes': 16,
    'lead': 'ES modules and CommonJS, npm with package.json and version ranges, TypeScript run straight in Node.js and checked with tsc, ESLint and Prettier, configuration from environment variables, and how a real test project is laid out.',
    'desc': 'import and export, CommonJS, npm, package.json, semver, lock files, TypeScript, tsc, ESLint, Prettier, .env files and test project structure.',
    'summary': 'Named and default exports, dynamic import, JSON modules, CommonJS and how it mixes with ES modules, package.json scripts and dependencies, semantic version ranges, npm ci and the lock file, TypeScript types and the type checker, ESLint and Prettier on real code, environment variables with --env-file, and a test project with separate unit and API scripts.',
    'keywords': ['import', 'export', 'ES modules', 'CommonJS', 'require', 'npm', 'package.json', 'semver', 'package-lock.json', 'npm ci', 'TypeScript', 'tsc', 'ESLint', 'Prettier', 'process.env', '.env', 'project structure'],
    'qa_intro': 'Every automation framework is a Node.js project: modules, npm scripts, TypeScript, lint rules and environment config are what you touch on day one.',
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
