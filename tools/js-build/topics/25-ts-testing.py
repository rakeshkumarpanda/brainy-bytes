# Chapter 25: test automation written in TypeScript: unit tests with node:test and Vitest, type tests, typed Playwright page objects and fixtures, a typed API client checked with zod, and the type check in CI.
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg, ts
from shop_app import SHOP_FILES

MODULE = ('🔷', 'TypeScript', 'ts', 'TypeScript from the first type to generics, advanced types, typed projects and test automation written in TypeScript.')

NT = [(r'duration_ms [\d.]+', 'duration_ms 88.4'), (r' \(\d+(\.\d+)?ms\)', '')]
VT = [(r'Start at\s+[\d:]+', 'Start at  09:00:00'), (r'Duration\s+[\d.]+m?s.*', 'Duration  398ms'), (r'(✓|×) (.*?) \d+ms', r'\1 \2')]
PW = [(r' \(\d+(\.\d+)?m?s\)', ''), (r'\((\d+(\.\d+)?)m?s\)\s*$', '(2.4s)'), (r'(passed|failed|flaky) \([\d.]+m?s\)', r'\1 (2.4s)')]

TS_TEST_CONFIG = {'compilerOptions': {'target': 'esnext', 'module': 'nodenext', 'strict': True, 'noEmit': True,
                                      'allowImportingTsExtensions': True, 'lib': ['esnext', 'dom'], 'types': ['node'], 'skipLibCheck': True}}


def tsconfig(include):
    cfg = json.loads(json.dumps(TS_TEST_CONFIG))
    cfg['include'] = include
    return json.dumps(cfg, indent=2)


CHECK = 'npx tsc -p . --pretty false && echo "tsc: no type errors" && echo'

CART_TS = '''
export interface Line { sku: string; price: number; qty: number }
export type Coupon = "SAVE10" | "SAVE20";

const RATES: Record<Coupon, number> = { SAVE10: 0.1, SAVE20: 0.2 };

export function cartTotal(lines: Line[], coupon?: Coupon): number {
  const sum = lines.reduce((total, l) => total + l.price * l.qty, 0);
  return Math.round(sum * (1 - (coupon ? RATES[coupon] : 0)));
}
'''

CODES = {
    'catch': ts('''
import { test, expect } from "@playwright/test";

test("add a pen to the cart", async ({ page, shopp }) => {     // a typo in a fixture name
  await page.goto("/");
  await page.getByRol("button", { name: "Add to cart" }).click(); // a typo in a method name
  await expect(page.getByTestId("cart-count")).toHaveText(1);  // a number where text is expected
});
''', 'Three test mistakes caught before the browser starts', errors=3, run=False, name='cart.spec.ts', options={'skipLibCheck': True}),
    'node-test': test({
        'package.json': pkg('ts-unit', 'module'),
        'tsconfig.json': tsconfig(['src']),
        'src/cart.ts': CART_TS,
        'src/cart.test.ts': '''
import { test } from "node:test";
import assert from "node:assert/strict";
import { cartTotal, type Line } from "./cart.ts";

const lines: Line[] = [{ sku: "pen", price: 20, qty: 3 }, { sku: "mug", price: 199, qty: 1 }];

test("total without a coupon", () => assert.equal(cartTotal(lines), 259));
test("SAVE10 takes 10 percent off", () => assert.equal(cartTotal(lines, "SAVE10"), 233));
test("an empty cart costs nothing", () => assert.equal(cartTotal([]), 0));
''',
    }, f'{CHECK} && node --test', 'node:test runs .ts files directly', show=['src/cart.ts', 'src/cart.test.ts'],
        shown_cmd='npx tsc && node --test', badge='🔷 tsc passes, then node:test runs', replace=NT),
    'vitest': test({
        'package.json': pkg('ts-vitest', 'module'),
        'tsconfig.json': tsconfig(['src']),
        'src/cart.ts': CART_TS,
        'src/cart.test.ts': '''
import { describe, it, expect, expectTypeOf } from "vitest";
import { cartTotal, type Coupon, type Line } from "./cart.ts";

describe("cartTotal", () => {
  const pen: Line = { sku: "pen", price: 20, qty: 5 };

  it.each<[Coupon | undefined, number]>([
    [undefined, 100],
    ["SAVE10", 90],
    ["SAVE20", 80],
  ])("coupon %s gives %i", (coupon, want) => {
    expect(cartTotal([pen], coupon)).toBe(want);
  });

  it("has the types the rest of the suite relies on", () => {
    expectTypeOf(cartTotal).returns.toEqualTypeOf<number>();
    expectTypeOf(cartTotal).parameter(1).toEqualTypeOf<Coupon | undefined>();
  });
});
''',
    }, f'{CHECK} && npx vitest run --reporter=verbose', 'Vitest with TypeScript and no extra set up', show=['src/cart.test.ts'],
        shown_cmd='npx tsc && npx vitest run', badge='🔷 tsc passes, then Vitest runs', replace=VT),
    'jest': show('''
// Jest does not read TypeScript by itself. Pick one transformer:
//   ts-jest      type checks while it runs (slower, catches more)
//   @swc/jest    or babel-jest: removes the types only (fast, run tsc separately)

// jest.config.ts
import type { Config } from "jest";

const config: Config = {
  preset: "ts-jest",                 // or: transform: { "^.+\\\\.tsx?$": "@swc/jest" }
  testEnvironment: "node",
  testMatch: ["**/*.test.ts"],
};
export default config;

// tsconfig.json for the tests: "types": ["jest", "node"] gives describe, it and expect their types
''', 'Jest with TypeScript', note='Set up only. The test code itself is the same as above.'),
    'typetests': ts('''
import { expectTypeOf } from "vitest";

type Role = "admin" | "customer";
interface User { id: number; email: string; role: Role }

// A helper the whole suite uses. Its type is part of its contract.
function makeUser(overrides: Partial<User> = {}): User {
  return { id: 1, email: "asha@shop.test", role: "customer", ...overrides };
}

expectTypeOf(makeUser).returns.toEqualTypeOf<User>();
expectTypeOf(makeUser).parameter(0).toEqualTypeOf<Partial<User> | undefined>();
expectTypeOf<User["role"]>().toEqualTypeOf<"admin" | "customer" | "guest">();   // somebody expects a guest role
''', 'Type tests: tests for the types themselves', errors=1, run=False, name='user.test-d.ts', options={'skipLibCheck': True}),
    'pw-ts': test({
        'package.json': pkg('shop-e2e-ts', 'module', {'test': 'playwright test'}), **SHOP_FILES,
        'tsconfig.json': tsconfig(['tests', 'pages', 'fixtures.ts', 'playwright.config.ts']),
        'playwright.config.ts': '''
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "tests",
  reporter: "list",
  workers: 1,
  use: { baseURL: "http://localhost:4331" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: { command: "node server.js", url: "http://localhost:4331", env: { PORT: "4331" }, reuseExistingServer: !process.env.CI },
});
''',
        'pages/shop.page.ts': '''
import { expect, type Locator, type Page } from "@playwright/test";

export type Product = "Gel pen" | "Coffee mug" | "Desk lamp";

export class ShopPage {
  readonly products: Locator;
  readonly cartCount: Locator;
  readonly total: Locator;

  constructor(readonly page: Page) {
    this.products = page.getByTestId("product");
    this.cartCount = page.getByTestId("cart-count");
    this.total = page.locator("#total");
  }
  async open(): Promise<this> {
    await this.page.goto("/");
    return this;
  }
  async logIn(email: string, password: string): Promise<void> {
    await this.page.getByLabel("Email").fill(email);
    await this.page.getByLabel("Password").fill(password);
    await this.page.getByRole("button", { name: "Sign in" }).click();
    await expect(this.products.first()).toBeVisible();
  }
  async add(name: Product): Promise<void> {     // only real product names compile
    await this.products.filter({ hasText: name }).getByRole("button", { name: "Add to cart" }).click();
  }
}
''',
        'fixtures.ts': '''
import { test as base } from "@playwright/test";
import { ShopPage } from "./pages/shop.page.ts";

interface TestUser { email: string; password: string }

// The type argument tells every test which fixtures exist and what they hold
export const test = base.extend<{ user: TestUser; shop: ShopPage }>({
  user: [{ email: "asha@shop.example", password: "s3cret" }, { option: true }],
  shop: async ({ page, user }, use) => {
    const shop = await new ShopPage(page).open();
    await shop.logIn(user.email, user.password);
    await use(shop);
  },
});
export { expect } from "@playwright/test";
''',
        'tests/cart.spec.ts': '''
import { test, expect } from "../fixtures.ts";

test("one gel pen", async ({ shop }) => {
  await shop.add("Gel pen");
  await expect(shop.total).toHaveText("₹20");
});

test("two lamps use Indian digit grouping", async ({ shop }) => {
  await shop.add("Desk lamp");
  await shop.add("Desk lamp");
  await expect(shop.cartCount).toHaveText("2");
  await expect(shop.total).toHaveText("₹2,598");
});
''',
    }, f'{CHECK} && npx playwright test', 'Typed page objects and typed fixtures in Playwright',
        show=['pages/shop.page.ts', 'fixtures.ts', 'tests/cart.spec.ts'], shown_cmd='npx tsc && npx playwright test',
        badge='🔷 tsc passes, then Playwright runs in Chromium', replace=PW),
    'api': test({
        'package.json': pkg('typed-api', 'module'),
        'tsconfig.json': tsconfig(['src', 'test']),
        'src/server.ts': '''
import { createServer, type Server } from "node:http";

// A tiny products API. ?v=2 sends a price as text, the kind of change that breaks clients.
export function startApi(): Promise<Server> {
  const server = createServer((req, res) => {
    const v2 = req.url?.includes("v=2");
    const body = [{ id: 1, name: "Gel pen", price: v2 ? "20" : 20 }, { id: 2, name: "Coffee mug", price: 199 }];
    res.writeHead(200, { "content-type": "application/json" }).end(JSON.stringify(body));
  });
  return new Promise(resolve => server.listen(0, () => resolve(server)));
}
''',
        'src/client.ts': '''
import { z } from "zod";

// One schema gives both the run time check and the TypeScript type
export const Product = z.object({ id: z.number().int(), name: z.string().min(1), price: z.number().nonnegative() });
export type Product = z.infer<typeof Product>;

export class ProductsClient {
  private readonly baseURL: string;
  constructor(baseURL: string) { this.baseURL = baseURL; }

  async list(query = ""): Promise<Product[]> {
    const res = await fetch(`${this.baseURL}/products${query}`);
    if (!res.ok) throw new Error(`GET /products answered ${res.status}`);
    return z.array(Product).parse(await res.json());   // unknown JSON in, typed data out
  }
}
''',
        'test/products.test.ts': '''
import { test, after } from "node:test";
import assert from "node:assert/strict";
import type { AddressInfo } from "node:net";
import { z } from "zod";
import { startApi } from "../src/server.ts";
import { ProductsClient } from "../src/client.ts";

const server = await startApi();
const api = new ProductsClient(`http://localhost:${(server.address() as AddressInfo).port}`);
after(() => server.close());

test("products match the contract", async () => {
  const products = await api.list();
  assert.equal(products.length, 2);
  assert.equal(products[0].price + products[1].price, 219);   // price is a number here, the type says so
});

test("a changed field type is caught at the edge", async () => {
  await assert.rejects(api.list("?v=2"), (e: unknown) => {
    assert.ok(e instanceof z.ZodError);
    console.log(z.prettifyError(e));
    return true;
  });
});
''',
    }, f'{CHECK} && node --test', 'A typed API client that checks every response with zod',
        show=['src/client.ts', 'test/products.test.ts'], shown_cmd='npx tsc && node --test', badge='🔷 tsc passes, then node:test runs', replace=NT),
    'ci': show('''
# .github/workflows/tests.yml
name: tests
on: [push, pull_request]

jobs:
  types:                                # fast gate: fails in about 30 seconds
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with: { node-version: 24, cache: npm }
      - run: npm ci
      - run: npx tsc --noEmit           # type errors in tests or helpers stop here
      - run: npx eslint .               # with typescript-eslint: no floating promises, no any

  e2e:
    needs: types                        # browsers start only when the types are clean
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with: { node-version: 24, cache: npm }
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test
''', 'Type check first, browsers second', lang='yaml', note='A CI pipeline, not run on this page'),
    'lint': show('''
// eslint.config.js: rules that only work with type information
import tseslint from "typescript-eslint";

export default tseslint.config(
  ...tseslint.configs.recommendedTypeChecked,
  {
    languageOptions: { parserOptions: { projectService: true } },
    rules: {
      "@typescript-eslint/no-floating-promises": "error",   // a missing await before expect or click
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/await-thenable": "error",          // await on something that is not a promise
    },
  },
);
''', 'typescript-eslint rules that catch flaky tests', note='Lint set up, not run on this page'),
    'scenario': ts('''
// Typed test data builders: sensible defaults, typed overrides, unique ids
type Role = "admin" | "customer";
interface Address { city: string; pin: string }
interface User { id: number; email: string; role: Role; address: Address }
interface Order { id: number; user: User; items: { sku: string; qty: number }[]; status: "new" | "paid" | "shipped" }

let next = 1000;
const id = () => ++next;

function builder<T>(defaults: () => T) {
  return (overrides: Partial<T> = {}): T => ({ ...defaults(), ...overrides });
}

const aUser = builder<User>(() => ({ id: id(), email: `user${next}@shop.test`, role: "customer", address: { city: "Pune", pin: "411001" } }));
const anOrder = builder<Order>(() => ({ id: id(), user: aUser(), items: [{ sku: "pen", qty: 1 }], status: "new" }));

const admin = aUser({ role: "admin" });
const paid = anOrder({ user: admin, status: "paid" });
const big = anOrder({ items: [{ sku: "lamp", qty: 2 }, { sku: "mug", qty: 4 }] });

console.log(admin.email, admin.role, paid.status, paid.user.id === admin.id);
console.log(big.items.length, big.user.role, big.id > paid.id);
''', 'Typed test data builders', options={'skipLibCheck': True}),
}

PARTS = [
    part('why', '🛡️', 'Why write tests in TypeScript', '''
<p>Test code is code. It has typos, wrong arguments and missing <code>await</code>s, and in JavaScript you only find them when the test runs, often in CI, often after a slow browser start. TypeScript finds them while you type. Every Playwright, Vitest and Jest API ships its own types, so the editor knows every fixture, locator method and matcher.</p>
[[catch]]
<p>All three would have failed the run in JavaScript, one at a time, each with a stack trace. Here tsc lists them together in under a second, and the editor underlines them before you save.</p>
''', qa=True, qa_why='Typed tests fail fast on mistakes in the test itself, so red builds point at real product bugs more often.',
        kw=['TypeScript tests', 'typed tests', 'compile time errors', 'test typos', 'Playwright types', 'fixture types', 'editor auto complete']),
    part('unit', '🧪', 'Unit tests in TypeScript', '''
<p>Node.js 24 and later remove the types and run <code>.ts</code> files directly, so <code>node --test</code> needs no build step. Vitest reads TypeScript too, without any set up. In both cases the runner only strips the types and does not check them, so run <code>tsc</code> as its own step.</p>
[[node-test]]
[[vitest]]
[[jest]]
<div class="warn">Removing types is not checking types. A test file full of type errors still runs green under <code>node --test</code>, Vitest or <code>@swc/jest</code>. Only <code>tsc</code> (or ts-jest) reports them. That is why every example on this page runs <code>tsc</code> first.</div>
''', qa=True, qa_why='Knowing which runners strip types and which check them avoids a green suite full of type errors.',
        kw=['node --test', 'type stripping', 'Vitest TypeScript', 'it.each', 'ts-jest', '@swc/jest', 'babel-jest', 'jest.config.ts', 'tsc --noEmit']),
    part('typetests', '🔬', 'Type tests', '''
<p>Shared helpers, builders and API clients are used by hundreds of tests, so their types are part of their contract. <code>expectTypeOf</code> from Vitest (and the <code>expect-type</code> package it is built on) asserts on types instead of values. Nothing runs. The check happens when tsc reads the file.</p>
[[typetests]]
<p>Type test messages are long because the library builds them out of types. Read the line number first. It points at the assertion that no longer holds, here the role union that has no guest.</p>
<p>Vitest can also collect these files with <code>vitest --typecheck</code>, which runs tsc for you on every <code>*.test-d.ts</code> file and shows type failures next to normal test failures.</p>
''', qa=True, qa_why='Type tests stop a helper change from quietly breaking the types that the rest of the suite depends on.',
        kw=['expectTypeOf', 'expect-type', 'type tests', 'test-d.ts', 'vitest --typecheck', 'toEqualTypeOf', 'tsd']),
    part('pw', '🎭', 'Playwright in TypeScript', '''
<p>Playwright runs TypeScript without any set up, and most Playwright documentation is written in it. Two things become much better with types. Page objects can limit their inputs, for example to real product names. Fixtures declared with <code>test.extend&lt;{ shop: ShopPage }&gt;</code> are typed in every test, so <code>({ shop })</code> auto completes and a typo does not compile.</p>
[[pw-ts]]
<div class="tip"><code>user</code> is an <b>option fixture</b>. A project in <code>playwright.config.ts</code> can set <code>use: { user: adminUser }</code> and every test in that project logs in as the admin. TypeScript checks that the value has the right shape.</div>
''', qa=['Playwright'], qa_why='Typed page objects and typed fixtures are the standard way to write Playwright suites in teams.',
        kw=['Playwright TypeScript', 'typed page object', 'test.extend', 'typed fixtures', 'option fixture', 'Locator type', 'Page type', 'playwright.config.ts']),
    part('api', '🔌', 'A typed API client with run time checks', '''
<p>TypeScript types disappear at run time, so they cannot check JSON from a server. A schema library such as <b>zod</b> does both jobs at once. The schema checks the data at run time, and <code>z.infer</code> turns the same schema into a TypeScript type, so the two can never drift apart.</p>
[[api]]
<p>Without the schema, the second test would have passed and a later assertion would have compared <code>"20" + 199</code>, which in JavaScript is the text <code>"20199"</code>. The schema stops the bad data at the edge, with a message that names the field and its position.</p>
''', qa=True, qa_why='API tests that parse every response with a schema catch contract changes on the first call.',
        kw=['zod', 'z.infer', 'schema validation', 'runtime validation', 'API client', 'contract testing', 'ZodError', 'unknown JSON']),
    part('ci', '🚦', 'TypeScript in CI', '''
<p>Put the type check in front of everything slow. It needs no browser and no server, and it fails in seconds. Type aware lint rules from typescript-eslint add checks that tsc does not do, such as a missing <code>await</code>, which is one of the most common causes of flaky tests.</p>
[[ci]]
[[lint]]
''', qa=True, qa_why='A fast type gate keeps broken test code out of the expensive browser jobs.',
        kw=['CI', 'GitHub Actions', 'tsc --noEmit', 'typescript-eslint', 'no-floating-promises', 'await-thenable', 'projectService', 'quality gate']),
    part('scenario', '🎬', 'Real world scenario: typed test data builders', '''
<div class="scenario"><b>The situation</b>Test data is copied between tests as large object literals. When the User type gained an address field, 140 tests broke at run time.</div>
[[scenario]]
<p>Each builder holds the defaults in one place and gives every object a fresh id, so tests stay independent. Overrides are <code>Partial&lt;T&gt;</code>, so a test only writes the fields it cares about, and a misspelt field or a wrong role does not compile. When <code>User</code> gains a field, only the builder needs to change.</p>
''', qa=True, kw=['test data builder', 'factory', 'Partial', 'generics', 'test data', 'unique ids', 'fixtures', 'object mother']),
]

INFO = {'title': 'Tests that check themselves', 'panels': [
    panel([['e', '🛡️'], ['t', 'tsc before the browser', {'b': 1}]], 'Fail fast', 'Typos in tests fail in a second.', 'Not after a slow browser start.'),
    panel([['e', '🎭'], ['t', 'test.extend<{ shop }>', {'b': 1}]], 'Typed fixtures', 'Every test knows its fixtures.', 'Page objects limit their inputs.'),
    panel([['e', '🔌'], ['t', 'z.infer<typeof Product>', {'b': 1}]], 'Checked data', 'One schema, two jobs.', 'Run time check and type.'),
    panel([['e', '🚦'], ['t', 'tsc --noEmit then e2e', {'b': 1}]], 'CI gate', 'Types first, browsers second.', 'Lint for missing awaits.')],
    'remember': 'Runners strip types and tsc checks them. Type your fixtures and page objects, check API responses with a schema, and run tsc first in CI.'}

REAL = [
    ['🎭', 'An e-commerce UI suite', 'Moved its 400 Playwright tests to TypeScript. Failures caused by mistakes in the test code itself fell from about one a week to almost none.'],
    ['🔌', 'A payments API team', 'Parsed every response with zod schemas. A field that silently changed from number to string was caught on the first CI run after the backend deploy.'],
    ['🚦', 'A QA platform team', 'Added a 40 second tsc and lint job in front of the 25 minute browser job, and stopped spending browser minutes on test code that could not work.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter shows test automation written in TypeScript: unit tests, type tests, Playwright with typed page objects and fixtures, a typed API client and the type check in CI.',
        'यह अध्याय TypeScript में test automation दिखाता है: unit tests, type tests, typed page objects वाला Playwright, typed API client और CI में type check।',
        'ಈ ಅಧ್ಯಾಯ TypeScript ನಲ್ಲಿ test automation ತೋರಿಸುತ್ತದೆ: unit tests, type tests, Playwright, typed API client ಮತ್ತು CI.',
        'ଏହି ଅଧ୍ୟାୟ TypeScript ରେ test automation ଦେଖାଏ: unit tests, type tests, Playwright, typed API client ଓ CI।',
        'يعرض هذا الفصل أتمتة الاختبارات بلغة TypeScript: اختبارات الوحدات واختبارات الأنواع وPlaywright مع كائنات صفحات مكتوبة الأنواع وعميل API وفحص الأنواع في CI.',
        'Dieses Kapitel zeigt Testautomatisierung in TypeScript: Unit-Tests, Typtests, Playwright mit typisierten Page Objects, einen typisierten API-Client und die Typprüfung in CI.'),
    say('why', 'Why TypeScript', 'TypeScript finds typos, wrong arguments and wrong fixture names in test code before the test runs, all at once and in under a second.',
        'TypeScript test code की typos, गलत arguments और गलत fixture names test चलने से पहले, एक साथ, एक second में पकड़ लेता है।',
        'TypeScript test ಓಡುವ ಮೊದಲೇ typos ಮತ್ತು ತಪ್ಪು fixture ಹೆಸರುಗಳನ್ನು ಹಿಡಿಯುತ್ತದೆ.',
        'TypeScript test ଚାଲିବା ପୂର୍ବରୁ typos ଓ ଭୁଲ fixture ନାମ ଧରେ।',
        'تكتشف TypeScript الأخطاء الإملائية والوسائط الخاطئة وأسماء التجهيزات الخاطئة قبل تشغيل الاختبار، كلها معًا وفي أقل من ثانية.',
        'TypeScript findet Tippfehler, falsche Argumente und falsche Fixture-Namen vor dem Testlauf, alle auf einmal in unter einer Sekunde.'),
    say('unit', 'Unit tests', 'Node test and Vitest run TypeScript files directly. They only remove the types, so run tsc as a separate step to check them.',
        'Node test और Vitest TypeScript files सीधे चलाते हैं। वे केवल types हटाते हैं, इसलिए जांच के लिए tsc अलग से चलाएं।',
        'Node test ಮತ್ತು Vitest TypeScript ನೇರವಾಗಿ ಓಡಿಸುತ್ತವೆ. Types ಪರಿಶೀಲನೆಗೆ tsc ಬೇರೆ ಓಡಿಸಿ.',
        'Node test ଓ Vitest TypeScript ସିଧା ଚଲାନ୍ତି। Types ଯାଞ୍ଚ ପାଇଁ tsc ଅଲଗା ଚଲାନ୍ତୁ।',
        'يشغل Node test وVitest ملفات TypeScript مباشرة، لكنهما يحذفان الأنواع فقط، لذا شغل tsc خطوة مستقلة للفحص.',
        'Node test und Vitest führen TypeScript direkt aus. Sie entfernen nur die Typen, also prüft tsc in einem eigenen Schritt.'),
    say('typetests', 'Type tests', 'expectTypeOf asserts on types instead of values. Nothing runs, and tsc reports a failure when a helper type changes.',
        'expectTypeOf values की जगह types पर assert करता है। कुछ नहीं चलता, और helper type बदलने पर tsc failure बताता है।',
        'expectTypeOf values ಬದಲು types ಮೇಲೆ assert ಮಾಡುತ್ತದೆ.',
        'expectTypeOf values ବଦଳରେ types ଉପରେ assert କରେ।',
        'تتحقق expectTypeOf من الأنواع بدل القيم، فلا يعمل شيء، وتبلغ tsc عن فشل عندما يتغير نوع دالة مساعدة.',
        'expectTypeOf prüft Typen statt Werte. Nichts läuft, und tsc meldet einen Fehler, wenn sich ein Hilfstyp ändert.'),
    say('pw', 'Playwright', 'Typed fixtures from test extend are known in every test, and page objects can limit inputs to real values such as product names.',
        'test extend से बने typed fixtures हर test में ज्ञात होते हैं, और page objects inputs को असली values तक सीमित कर सकते हैं।',
        'test extend ನ typed fixtures ಪ್ರತಿ test ನಲ್ಲಿ ತಿಳಿದಿರುತ್ತವೆ.',
        'test extend ର typed fixtures ପ୍ରତି test ରେ ଜଣା।',
        'التجهيزات المكتوبة الأنواع من test.extend معروفة في كل اختبار، ويمكن لكائنات الصفحات حصر المدخلات في قيم حقيقية مثل أسماء المنتجات.',
        'Typisierte Fixtures aus test.extend sind in jedem Test bekannt, und Page Objects erlauben nur echte Werte wie Produktnamen.'),
    say('api', 'API client', 'Types vanish at run time, so a zod schema checks the JSON, and z infer turns the same schema into the TypeScript type.',
        'Types run time पर गायब हो जाते हैं, इसलिए zod schema JSON जांचता है, और z infer उसी schema से TypeScript type बनाता है।',
        'Run time ನಲ್ಲಿ types ಇರುವುದಿಲ್ಲ, zod schema JSON ಪರಿಶೀಲಿಸುತ್ತದೆ.',
        'Run time ରେ types ନଥାଏ, zod schema JSON ଯାଞ୍ଚ କରେ।',
        'تختفي الأنواع وقت التشغيل، لذا يفحص مخطط zod بيانات JSON، ويحول z.infer المخطط نفسه إلى نوع TypeScript.',
        'Typen verschwinden zur Laufzeit, also prüft ein zod-Schema das JSON, und z.infer macht daraus den TypeScript-Typ.'),
    say('ci', 'CI', 'Run tsc and type aware lint before any browser job. They fail in seconds and catch missing awaits that cause flaky tests.',
        'किसी browser job से पहले tsc और type aware lint चलाएं। वे seconds में fail होते हैं और missing await पकड़ते हैं।',
        'Browser job ಮೊದಲು tsc ಮತ್ತು lint ಓಡಿಸಿ.',
        'Browser job ପୂର୍ବରୁ tsc ଓ lint ଚଲାନ୍ତୁ।',
        'شغل tsc والفحص المدرك للأنواع قبل أي مهمة متصفح، فهي تفشل في ثوان وتكتشف await المفقودة التي تسبب اختبارات متقلبة.',
        'tsc und typbewusstes Linting laufen vor jedem Browser-Job. Sie scheitern in Sekunden und finden fehlende awaits.'),
    say('scenario', 'Scenario', 'Typed builders keep test data defaults in one place, give fresh ids, and accept only valid partial overrides.',
        'Typed builders test data के defaults एक जगह रखते हैं, नए ids देते हैं और केवल सही partial overrides लेते हैं।',
        'Typed builders defaults ಒಂದೇ ಕಡೆ ಇಡುತ್ತವೆ ಮತ್ತು ಹೊಸ ids ಕೊಡುತ್ತವೆ.',
        'Typed builders defaults ଏକ ଜାଗାରେ ରଖନ୍ତି ଓ ନୂଆ ids ଦିଅନ୍ତି।',
        'تحفظ المنشئات المكتوبة الأنواع القيم الافتراضية في مكان واحد وتعطي معرفات جديدة وتقبل تعديلات جزئية صحيحة فقط.',
        'Typisierte Builder halten Standardwerte an einem Ort, vergeben neue IDs und erlauben nur gültige Teilwerte.'),
    say('practice', 'Hands-on', 'Practise a test data builder, a response parser, a fixture runner with set up and clean up, and a polling assertion.',
        'Test data builder, response parser, set up और clean up वाला fixture runner और polling assertion का अभ्यास करें।',
        'Builder, parser, fixture runner ಮತ್ತು polling assertion ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Builder, parser, fixture runner ଓ polling assertion ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على منشئ بيانات اختبار ومحلل استجابات ومشغل تجهيزات مع الإعداد والتنظيف وتأكيد يعيد المحاولة.',
        'Übe einen Testdaten-Builder, einen Antwort-Parser, einen Fixture-Runner mit Auf- und Abbau und eine wiederholende Prüfung.'),
]

QUIZ = [
    quiz('e', 'Does node --test check the types in a .ts test file?', ['No, it only removes them', 'Yes, always', 'Only with strict', 'Only in CI'], 0, 'Stripping is not checking.', 'Run tsc as its own step to check types.'),
    quiz('e', 'Which Playwright call adds your own typed fixtures?', ['test.extend<{ shop: ShopPage }>()', 'test.use()', 'test.fixture()', 'expect.extend()'], 0, 'Extend the base test.', 'The type argument lists each fixture and its type.'),
    quiz('e', 'What does z.infer<typeof Product> give you?', ['The TypeScript type described by the schema', 'A parsed object', 'A JSON schema', 'A test'], 0, 'Infer the type.', 'One schema then serves as both run time check and type.'),
    quiz('m', 'Why must API responses be checked at run time even in TypeScript?', ['Types are erased, so JSON from a server is never checked by them', 'TypeScript is slow', 'fetch has no types', 'It is required by Node.js'], 0, 'Erased at run time.', 'res.json() is effectively unknown data. A schema turns it into checked data.'),
    quiz('m', 'Which Jest set up type checks while the tests run?', ['ts-jest', '@swc/jest', 'babel-jest', 'jest-environment-jsdom'], 0, 'The ts one.', 'SWC and Babel only remove types, which is faster but checks nothing.'),
    quiz('m', 'What does expectTypeOf(fn).returns.toEqualTypeOf<number>() do at run time?', ['Nothing useful, the check happens in tsc', 'Calls fn', 'Throws if fn returns a string', 'Logs the type'], 0, 'Types only.', 'Type tests fail at compile time, never at run time.'),
    quiz('m', 'In the Playwright example, what happens with shop.add("Pencil")?', ['tsc reports an error because Pencil is not a Product', 'The test fails at run time', 'It adds nothing', 'It adds a gel pen'], 0, 'A union of names.', 'The Product type allows only the three real names.'),
    quiz('h', 'Which typescript-eslint rule catches a missing await before expect(...).toHaveText()?', ['no-floating-promises', 'no-explicit-any', 'no-unused-vars', 'prefer-const'], 0, 'A promise left floating.', 'A missing await is a common cause of flaky and falsely green tests.'),
    quiz('h', 'Why put the tsc job before the browser job in CI?', ['It fails in seconds and saves the slow job from running broken code', 'Browsers need compiled code', 'Playwright requires it', 'It makes tests faster'], 0, 'Fail fast.', 'needs: types makes the e2e job wait for a clean type check.'),
    quiz('h', 'What is an option fixture in Playwright?', ['A fixture with a default value that projects or test.use can override', 'An optional test', 'A skipped fixture', 'A fixture that runs once'], 0, 'option: true.', 'For example a user that one project sets to an admin.'),
    quiz('x', 'Why does the builder take a function that returns defaults instead of a defaults object?', ['So each call gets fresh objects and a new id', 'It is faster', 'TypeScript requires it', 'To allow async'], 0, 'Shared objects leak between tests.', 'A shared nested object would be changed by one test and seen by the next.'),
    quiz('x', 'What does "20" + 199 give in JavaScript, the bug the zod schema prevents?', ['"20199"', '219', 'NaN', 'A TypeError'], 0, 'Plus with a string.', 'Plus joins text when either side is a string.'),
]

CALC = [
    calc('e', 'The first example has three mistakes. How many type errors does tsc report?', '3', 'One per mistake.', ['A wrong fixture name, a wrong method name and a number where text is expected.']),
    calc('e', 'In the node:test example, the cart has 3 pens at ₹20 and 1 mug at ₹199. What is the total?', '259', 'Price times quantity.', ['<span class="eq">3 × 20 + 1 × 199 = 60 + 199 = 259</span>']),
    calc('m', 'With SAVE10 the same cart costs what, rounded?', '233', 'Take off 10 percent.', ['<span class="eq">259 × 0.9 = 233.1</span>', 'Math.round gives 233.']),
    calc('m', 'Two desk lamps cost ₹1,299 each. What does the total show, as a plain number?', '2598', 'Double it.', ['<span class="eq">2 × 1299 = 2598</span>', 'The page shows it as ₹2,598.'], alt=['2,598', '₹2,598']),
    calc('m', 'A tsc and lint job takes 40 seconds and a browser job 25 minutes. A broken commit is caught by tsc. How many seconds of browser time are saved?', '1500', 'Minutes to seconds.', ['<span class="eq">25 × 60 = 1500</span>']),
    calc('h', 'The products API returns a gel pen at 20 and a mug at 199. What does the passing test add up to?', '219', 'Two numbers.', ['<span class="eq">20 + 199 = 219</span>']),
    calc('h', 'In the scenario the id counter starts at 1000. aUser() is called for admin first. What is admin.id?', '1001', 'Pre increment.', ['++next raises 1000 to 1001 and returns it.']),
    calc('x', 'In the scenario, how many ids are taken after admin, paid and big are built?', '4', 'Count every builder call, including nested ones.', ['admin takes 1. paid takes 1 for the order (its user is given).', 'big takes 1 for the order and 1 for its default user.', '<span class="eq">1 + 1 + 2 = 4</span>']),
]

EX = [
    ex('builder', 'e', 'A test data builder', '<p>Write <code>makeBuilder(defaults)</code>. <code>defaults</code> is a function that returns a fresh object. <code>makeBuilder</code> returns a function that takes optional overrides and returns the defaults merged with the overrides.</p>',
       'function makeBuilder(defaults) {\n  \n}\n',
       [('(() => { const aUser = makeBuilder(() => ({ role: "customer", city: "Pune" })); return [aUser(), aUser({ role: "admin" })]; })()', [{'role': 'customer', 'city': 'Pune'}, {'role': 'admin', 'city': 'Pune'}]),
        ('(() => { const a = makeBuilder(() => ({ tags: [] })); const x = a(); x.tags.push("t"); return a().tags.length; })()', 0)],
       'function makeBuilder(defaults) {\n  return (overrides = {}) => ({ ...defaults(), ...overrides });\n}', hint='Call <code>defaults()</code> inside the returned function, then spread the overrides after it.', why='Calling defaults on every build keeps tests from sharing the same nested objects.'),
    ex('parse', 'm', 'Check a response by hand', '<p>Write <code>parseProduct(x)</code> that returns <code>x</code> when it has an integer <code>id</code>, a non-empty string <code>name</code> and a number <code>price</code> of 0 or more. Otherwise throw a <code>TypeError</code> whose message is the first bad field name followed by <code>": invalid"</code>, checking in the order id, name, price.</p>',
       'function parseProduct(x) {\n  \n}\n',
       [('parseProduct({ id: 1, name: "Gel pen", price: 20 })', {'id': 1, 'name': 'Gel pen', 'price': 20}),
        ('(() => { try { parseProduct({ id: 1, name: "Gel pen", price: "20" }); } catch (e) { return [e.name, e.message]; } })()', ['TypeError', 'price: invalid']),
        ('(() => { try { parseProduct({ id: 1.5, name: "", price: -1 }); } catch (e) { return e.message; } })()', 'id: invalid')],
       'function parseProduct(x) {\n  const rules = {\n    id: v => Number.isInteger(v),\n    name: v => typeof v === "string" && v.length > 0,\n    price: v => typeof v === "number" && v >= 0,\n  };\n  for (const [field, ok] of Object.entries(rules)) {\n    if (!ok(x?.[field])) throw new TypeError(`${field}: invalid`);\n  }\n  return x;\n}',
       hint='Keep one small check function per field and loop over them in order.', why='This is what a zod object schema does for you, plus it gives you the type.'),
    ex('fixtures', 'h', 'A fixture runner', '<p>Write <code>runWithFixtures(fixtures, testFn)</code>. Each fixture is <code>async (use) =&gt; { …set up…; await use(value); …clean up… }</code>, like in Playwright. Set fixtures up in object order, call <code>testFn</code> with an object of all values, then let them clean up in reverse order. Return what <code>testFn</code> returns.</p>',
       'async function runWithFixtures(fixtures, testFn) {\n  \n}\n',
       [('(async () => { const log = []; const r = await runWithFixtures({ db: async use => { log.push("db up"); await use("DB"); log.push("db down"); }, page: async use => { log.push("page up"); await use("PAGE"); log.push("page down"); } }, async f => { log.push("test " + f.db + " " + f.page); return 7; }); return [r, log]; })()',
         [7, ['db up', 'page up', 'test DB PAGE', 'page down', 'db down']])],
       'async function runWithFixtures(fixtures, testFn) {\n  const names = Object.keys(fixtures);\n  const values = {};\n  async function setUp(i) {\n    if (i === names.length) return testFn(values);\n    let result;\n    await fixtures[names[i]](async value => {\n      values[names[i]] = value;\n      result = await setUp(i + 1);\n    });\n    return result;\n  }\n  return setUp(0);\n}',
       hint='Set up one fixture at a time. Inside its <code>use</code> callback, set up the next one, and run the test when none are left.', why='Nesting each fixture inside the previous one gives the reverse clean up order for free.'),
    ex('poll', 'x', 'A polling assertion', '<p>Write <code>expectPoll(fn, expected, { interval, timeout })</code>. It calls <code>fn</code> until the result equals <code>expected</code> and then resolves to the number of calls. If <code>timeout</code> milliseconds pass first, it rejects with an Error whose message starts with <code>"expected 2, last value 1"</code> for those values.</p>',
       'async function expectPoll(fn, expected, { interval = 10, timeout = 1000 } = {}) {\n  \n}\n',
       [('(async () => { let n = 0; return await expectPoll(() => ++n, 3, { interval: 5, timeout: 500 }); })()', 3),
        ('(async () => { try { await expectPoll(() => 1, 2, { interval: 5, timeout: 40 }); } catch (e) { return e.message.startsWith("expected 2, last value 1"); } })()', True)],
       'async function expectPoll(fn, expected, { interval = 10, timeout = 1000 } = {}) {\n  const end = Date.now() + timeout;\n  let calls = 0;\n  let last;\n  while (true) {\n    last = await fn();\n    calls++;\n    if (last === expected) return calls;\n    if (Date.now() >= end) throw new Error(`expected ${expected}, last value ${last} after ${calls} calls`);\n    await new Promise(r => setTimeout(r, interval));\n  }\n}',
       hint='Loop: call, compare, check the clock, then wait for the interval.', why='Playwright expect.poll and web first assertions retry like this instead of sleeping.'),
]

T = {
    'slug': 'ts-testing', 'title': 'Test automation in TypeScript', 'short': 'Testing in TypeScript', 'emoji': '🧪', 'module': MODULE, 'minutes': 20,
    'lead': 'Test automation written in TypeScript: why typed tests fail faster, unit tests with node:test, Vitest and Jest, type tests with expectTypeOf, Playwright with typed page objects and fixtures, a typed API client that checks responses with zod, the type check in CI, and typed test data builders.',
    'desc': 'TypeScript test automation: node --test with .ts, Vitest, ts-jest, expectTypeOf type tests, Playwright test.extend typed fixtures, typed page objects, zod schemas and z.infer, tsc --noEmit and typescript-eslint in CI, test data builders.',
    'summary': 'How TypeScript catches mistakes in test code, running unit tests in TypeScript with node:test, Vitest and Jest, testing types with expectTypeOf, typed Playwright page objects and fixtures, an API client that checks every response with zod, a CI pipeline that type checks first, and typed test data builders.',
    'keywords': ['TypeScript testing', 'Playwright TypeScript', 'Vitest', 'node:test', 'ts-jest', 'expectTypeOf', 'typed fixtures', 'page object', 'zod', 'z.infer', 'API client', 'tsc --noEmit', 'typescript-eslint', 'test data builder', 'interview'],
    'qa_intro': 'Most new automation frameworks are written in TypeScript. This chapter puts the earlier TypeScript chapters to work on unit, API and browser tests.',
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
