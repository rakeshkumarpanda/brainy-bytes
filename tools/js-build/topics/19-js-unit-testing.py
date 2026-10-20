# Chapter 19: unit testing with node:test, Jest, Vitest and Mocha, mocks and fake timers, many ways to run a suite,
# unit tests for web (DOM) code and for API code, coverage and CI.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🧪', 'Testing with JavaScript', 'js-testing', 'Unit tests, API tests and browser automation with node:test, Jest, Vitest, Mocha, supertest, Playwright, Selenium and Cypress.')

# Timings change on every run, so the page shows fixed ones.
NT = [(r'duration_ms [\d.]+', 'duration_ms 92.5'), (r' \(\d+(\.\d+)?ms\)', ''), (r'\(node:\d+\)', '(node:4242)')]
JEST = [(r'Time:\s+[\d.]+ m?s.*', 'Time:        0.61 s'), (r' \(\d+ ms\)', ''), (r'Ran all test suites.*', 'Ran all test suites.')]
VT = [(r'Start at\s+[\d:]+', 'Start at  09:00:00'), (r'Duration\s+[\d.]+m?s.*', 'Duration  412ms'), (r'(✓|×) (.*?) \d+ms', r'\1 \2')]
MOCHA = [(r' \(\d+ms\)', ''), (r'passing \(\d+m?s\)', 'passing (12ms)')]

CART_ESM = '''
export function cartTotal(items, { coupon } = {}) {
  if (!Array.isArray(items)) throw new TypeError("items must be an array");
  const subtotal = items.reduce((sum, i) => sum + i.price * i.qty, 0);
  const discount = coupon === "SAVE10" ? subtotal * 0.1 : 0;
  return Math.round((subtotal - discount) * 100) / 100;
}

export function freeShipping(total) {
  return total >= 499;
}
'''

CART_CJS = CART_ESM.replace('export function', 'function') + '\nmodule.exports = { cartTotal, freeShipping };\n'

CODES = {
    'first': test({
        'package.json': pkg('cart', 'module', {'test': 'node --test --test-reporter=spec'}),
        'src/cart.js': CART_ESM,
        'test/cart.test.js': '''
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { cartTotal, freeShipping } from "../src/cart.js";

describe("cartTotal", () => {
  it("adds price times quantity", () => {
    // Arrange
    const items = [{ price: 20, qty: 3 }, { price: 250, qty: 1 }];
    // Act
    const total = cartTotal(items);
    // Assert
    assert.equal(total, 310);
  });

  it("is 0 for an empty cart", () => {
    assert.equal(cartTotal([]), 0);
  });

  it("takes 10% off with SAVE10", () => {
    assert.equal(cartTotal([{ price: 199, qty: 1 }], { coupon: "SAVE10" }), 179.1);
  });

  it("rejects input that is not an array", () => {
    assert.throws(() => cartTotal("pen"), { name: "TypeError", message: /must be an array/ });
  });
});

describe("freeShipping", () => {
  for (const [total, expected] of [[498.99, false], [499, true], [500, true]]) {
    it(`${total} -> ${expected}`, () => assert.equal(freeShipping(total), expected));
  }
});
''',
    }, 'npm test', 'A first unit test suite with node:test', show=['src/cart.js', 'test/cart.test.js'], replace=NT),
    'node-mocks': test({
        'package.json': pkg('signup', 'module'),
        'src/signup.js': '''
export function createSignup({ mailer, clock }) {
  const pending = new Map();
  return {
    async register(email) {
      const code = String(clock.now() % 1_000_000).padStart(6, "0");
      pending.set(email, { code, expires: clock.now() + 10 * 60_000 });
      await mailer.send(email, `Your code is ${code}`);
      return { status: "pending" };
    },
    verify(email, code) {
      const entry = pending.get(email);
      if (!entry || clock.now() > entry.expires) return "expired";
      return entry.code === code ? "verified" : "wrong code";
    },
  };
}
''',
        'test/signup.test.js': '''
import { describe, it, beforeEach, afterEach, mock } from "node:test";
import assert from "node:assert/strict";
import { createSignup } from "../src/signup.js";

describe("signup", () => {
  let mailer, signup;

  beforeEach(() => {
    mock.timers.enable({ apis: ["Date"], now: 1_700_000_123_456 });   // a fixed, fake clock
    mailer = { send: mock.fn(async () => {}) };                        // a fake mailer that records calls
    signup = createSignup({ mailer, clock: Date });
  });

  afterEach(() => mock.timers.reset());                                  // real time again

  it("emails a 6 digit code", async () => {
    await signup.register("asha@shop.example");
    assert.equal(mailer.send.mock.callCount(), 1);
    assert.deepEqual(mailer.send.mock.calls[0].arguments, ["asha@shop.example", "Your code is 123456"]);
  });

  it("accepts the right code within 10 minutes", async () => {
    await signup.register("asha@shop.example");
    mock.timers.tick(9 * 60_000);                                       // jump 9 minutes ahead instantly
    assert.equal(signup.verify("asha@shop.example", "123456"), "verified");
  });

  it("expires the code after 10 minutes", async () => {
    await signup.register("asha@shop.example");
    mock.timers.tick(10 * 60_000 + 1);
    assert.equal(signup.verify("asha@shop.example", "123456"), "expired");
  });
});
''',
    }, 'node --test --test-reporter=spec', 'Fake functions and a fake clock in node:test', show=['src/signup.js', 'test/signup.test.js'], replace=NT),
    'ways-node': test({
        'package.json': pkg('ways', 'module'),
        'src/cart.js': CART_ESM,
        'test/cart.test.js': '''
import { test } from "node:test";
import assert from "node:assert/strict";
import { cartTotal } from "../src/cart.js";

test("checkout total with coupon", { tags: ["smoke"] }, () => {
  assert.equal(cartTotal([{ price: 100, qty: 2 }], { coupon: "SAVE10" }), 180);
});
test("checkout total without coupon", () => {
  assert.equal(cartTotal([{ price: 100, qty: 2 }]), 200);
});
test("empty cart", { tags: ["smoke"] }, () => assert.equal(cartTotal([]), 0));
test.skip("multi currency carts", () => {});
test.todo("gift cards");
''',
        'test/shipping.test.js': '''
import { test } from "node:test";
import assert from "node:assert/strict";
import { freeShipping } from "../src/cart.js";

test("free shipping from 499", () => assert.equal(freeShipping(499), true));
''',
        'ways.sh': '''
say() { printf '\\n$ %s\\n' "$*"; }
say "node --test --test-reporter=dot"
node --test --no-warnings --test-reporter=dot
say "node --test --test-name-pattern=checkout --test-reporter=spec"
node --test --no-warnings --test-name-pattern=checkout --test-reporter=spec | grep -v '^ℹ \\(suites\\|cancelled\\|todo\\|duration\\)\\|^✔ test/'
say "node --test --test-reporter=spec test/shipping.test.js"
node --test --no-warnings --test-reporter=spec test/shipping.test.js | sed -n '1p'
say "node --test --experimental-test-tag-filter=smoke --test-reporter=spec"
node --test --no-warnings --experimental-test-tag-filter=smoke --test-reporter=spec | sed -n '1,2p'
say "node --test --test-shard=1/2 --test-reporter=spec"
node --test --no-warnings --test-shard=1/2 --test-reporter=spec | grep -c '^✔' | sed 's/$/ tests ran in shard 1 of 2/'
say "node --test --test-reporter=junit --test-reporter-destination=junit.xml"
node --test --no-warnings --test-reporter=junit --test-reporter-destination=junit.xml
sed -n '1,4p' junit.xml
say "node --test --experimental-test-coverage --test-coverage-include=src/** --test-reporter=spec"
node --test --no-warnings --experimental-test-coverage --test-coverage-include='src/**' --test-reporter=spec | sed -n '/start of coverage/,/end of coverage/p'
''',
    }, 'sh ways.sh', 'Seven ways to run the same node:test suite', show=['test/cart.test.js'], shown_cmd='sh ways.sh   # runs each command below',
        replace=NT + [(r'time="[\d.]+"', 'time="0.0005"'), (r'timestamp="[^"]*"', 'timestamp="2026-10-20T09:00:00Z"'), (r'hostname="[^"]*"', 'hostname="ci-runner"')]),
    'jest-basics': test({
        'package.json': pkg('cart-jest', None, {'test': 'jest'}),
        'src/cart.js': CART_CJS,
        'src/cart.test.js': '''
const { cartTotal, freeShipping } = require("./cart");

describe("cartTotal", () => {
  test("adds price times quantity", () => {
    expect(cartTotal([{ price: 20, qty: 3 }, { price: 250, qty: 1 }])).toBe(310);
  });

  test.each([
    [[], 0],
    [[{ price: 99.99, qty: 3 }], 299.97],
    [[{ price: 0.1, qty: 3 }], 0.3],
  ])("cartTotal(%j) is %d", (items, expected) => {
    expect(cartTotal(items)).toBeCloseTo(expected, 2);
  });

  test("throws a TypeError for bad input", () => {
    expect(() => cartTotal(null)).toThrow(TypeError);
    expect(() => cartTotal(null)).toThrow(/must be an array/);
  });
});

describe("freeShipping", () => {
  test.each`
    total     | free
    ${498.99} | ${false}
    ${499}    | ${true}
  `("$total gives $free", ({ total, free }) => {
    expect(freeShipping(total)).toBe(free);
  });
});

test("matchers for objects and arrays", () => {
  const order = { id: 7, items: ["pen", "mug"], meta: { source: "web", at: Date.now() } };
  expect(order).toEqual(expect.objectContaining({ id: 7 }));
  expect(order.items).toContain("mug");
  expect(order.items).toHaveLength(2);
  expect(order).toMatchObject({ meta: { source: "web" } });
  expect(order.meta.at).toEqual(expect.any(Number));
});
''',
    }, 'npx jest --verbose', 'Jest: matchers and table driven tests', show=['src/cart.test.js'], replace=JEST),
    'jest-mocks': test({
        'package.json': pkg('order-jest', None, {'test': 'jest'}),
        'src/mailer.js': '''
module.exports = {
  async send(to, subject) {
    throw new Error("real emails must never be sent from unit tests");
  },
};
''',
        'src/order.js': '''
const mailer = require("./mailer");

async function placeOrder(order, { now = Date.now } = {}) {
  if (!order.items.length) throw new Error("Cart is empty");
  const id = `ORD-${now()}`;
  await mailer.send(order.email, `Order ${id} confirmed`);
  return { id, status: "confirmed" };
}

function remindLater(fn, ms = 24 * 60 * 60 * 1000) {
  return setTimeout(fn, ms);
}

module.exports = { placeOrder, remindLater };
''',
        'src/order.test.js': '''
jest.mock("./mailer");                         // replace every export with a fake
const mailer = require("./mailer");
const { placeOrder, remindLater } = require("./order");

beforeEach(() => jest.clearAllMocks());

test("sends one confirmation email", async () => {
  mailer.send.mockResolvedValue(undefined);
  const result = await placeOrder({ email: "asha@shop.example", items: ["pen"] }, { now: () => 42 });
  expect(result).toEqual({ id: "ORD-42", status: "confirmed" });
  expect(mailer.send).toHaveBeenCalledTimes(1);
  expect(mailer.send).toHaveBeenCalledWith("asha@shop.example", "Order ORD-42 confirmed");
});

test("an empty cart sends nothing", async () => {
  await expect(placeOrder({ email: "a@b.c", items: [] })).rejects.toThrow("Cart is empty");
  expect(mailer.send).not.toHaveBeenCalled();
});

test("a mail failure fails the order", async () => {
  mailer.send.mockRejectedValueOnce(new Error("SMTP down"));
  await expect(placeOrder({ email: "a@b.c", items: ["pen"] })).rejects.toThrow("SMTP down");
});

test("spyOn watches a real method without replacing it", () => {
  const spy = jest.spyOn(Math, "round");
  Math.round(2.6);
  expect(spy).toHaveBeenCalledWith(2.6);
  expect(spy).toHaveReturnedWith(3);
  spy.mockRestore();
});

test("fake timers skip a whole day instantly", () => {
  jest.useFakeTimers();
  const remind = jest.fn();
  remindLater(remind);
  jest.advanceTimersByTime(23 * 60 * 60 * 1000);
  expect(remind).not.toHaveBeenCalled();
  jest.advanceTimersByTime(60 * 60 * 1000);
  expect(remind).toHaveBeenCalledTimes(1);
  jest.useRealTimers();
});
''',
    }, 'npx jest --verbose', 'Jest: mock a module, spy, and fake timers', show=['src/order.js', 'src/order.test.js'], replace=JEST),
    'ways-jest': test({
        'package.json': pkg('ways-jest', None, {'test': 'jest'}),
        'src/cart.js': CART_CJS,
        'src/cart.test.js': '''
const { cartTotal } = require("./cart");
test("@smoke checkout total", () => expect(cartTotal([{ price: 10, qty: 2 }])).toBe(20));
test("discount with SAVE10", () => expect(cartTotal([{ price: 10, qty: 2 }], { coupon: "SAVE10" })).toBe(18));
''',
        'src/shipping.test.js': '''
const { freeShipping } = require("./cart");
test("@smoke free shipping from 499", () => expect(freeShipping(499)).toBe(true));
''',
        'ways.sh': '''
say() { printf '\\n$ %s\\n' "$*"; }
say 'npx jest --listTests'
npx jest --listTests | sed 's|.*/src/|src/|' | sort
say 'npx jest -t "@smoke" --verbose'
npx jest -t "@smoke" --verbose 2>&1 | grep -E '✓|○|Tests:'
say 'npx jest shipping'
npx jest shipping 2>&1 | grep -E 'PASS|FAIL|Tests:'
say 'npx jest --shard=2/2'
npx jest --shard=2/2 2>&1 | grep -E 'PASS|Tests:'
say 'npx jest --coverage --coverageThreshold={"global":{"branches":100}}'
npx jest --coverage --coverageThreshold='{"global":{"branches":100}}' > out.txt 2>&1
code=$?
grep -E '^(File|All files|.*cart\\.js|Jest:)' out.txt
echo "exit code: $code"
''',
    }, 'sh ways.sh', 'Filter, shard and measure coverage with Jest', show=['src/cart.test.js'], shown_cmd='sh ways.sh   # runs each command below', replace=JEST),
    'vitest': test({
        'package.json': pkg('cart-vitest', 'module', {'test': 'vitest run'}),
        'src/price.js': '''
export async function convert(amount, to, { getRate }) {
  if (to === "INR") return amount;
  const rate = await getRate("INR", to);
  return Math.round(amount * rate * 100) / 100;
}

export function debounce(fn, ms) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
}
''',
        'src/price.test.js': '''
import { describe, it, expect, vi } from "vitest";
import { convert, debounce } from "./price.js";

describe("convert", () => {
  it("does not call the rate service for INR", async () => {
    const getRate = vi.fn();
    expect(await convert(500, "INR", { getRate })).toBe(500);
    expect(getRate).not.toHaveBeenCalled();
  });

  it("uses the rate from the service", async () => {
    const getRate = vi.fn().mockResolvedValue(0.012);
    await expect(convert(1000, "USD", { getRate })).resolves.toBe(12);
    expect(getRate).toHaveBeenCalledWith("INR", "USD");
  });
});

describe("debounce", () => {
  it("runs once after the user stops typing", () => {
    vi.useFakeTimers();
    const search = vi.fn();
    const onType = debounce(search, 300);
    onType("p"); onType("pe"); onType("pen");
    vi.advanceTimersByTime(299);
    expect(search).not.toHaveBeenCalled();
    vi.advanceTimersByTime(1);
    expect(search).toHaveBeenCalledExactlyOnceWith("pen");
    vi.useRealTimers();
  });
});

it.concurrent.each([1, 2, 3])("concurrent case %i", async n => {
  expect(n).toBeGreaterThan(0);
});
''',
    }, 'npx vitest run --reporter=verbose', 'Vitest: the same ideas, ES modules first', show=['src/price.test.js'], replace=VT),
    'mocha': test({
        'package.json': pkg('cart-mocha', 'module', {'test': 'mocha'}),
        '.mocharc.json': '{ "spec": "test/**/*.spec.js", "timeout": 2000 }',
        'src/cart.js': CART_ESM,
        'test/cart.spec.js': '''
import { expect } from "chai";
import sinon from "sinon";
import { cartTotal } from "../src/cart.js";

describe("cartTotal @smoke", function () {
  it("adds price times quantity", function () {
    expect(cartTotal([{ price: 20, qty: 3 }])).to.equal(60);
  });

  it("rejects bad input", function () {
    expect(() => cartTotal({})).to.throw(TypeError, /must be an array/);
  });
});

describe("analytics", function () {
  afterEach(() => sinon.restore());

  it("tracks the checkout once", function () {
    const analytics = { track() {} };
    const spy = sinon.spy(analytics, "track");
    analytics.track("checkout", { total: 60 });
    expect(spy.calledOnceWith("checkout", { total: 60 })).to.be.true;
  });

  it("stubs a slow call", async function () {
    const api = { getStock: async () => { throw new Error("network"); } };
    sinon.stub(api, "getStock").resolves(7);
    expect(await api.getStock("PEN-01")).to.equal(7);
  });
});
''',
    }, 'npx mocha && npx mocha --grep @smoke --reporter dot', 'Mocha with Chai and Sinon', show=['.mocharc.json', 'test/cart.spec.js'], replace=MOCHA),
    'web-unit': test({
        'package.json': pkg('web-unit', 'module', {'test': 'vitest run'}),
        'vitest.config.js': '''
import { defineConfig } from "vitest/config";
export default defineConfig({ test: { environment: "jsdom" } });   // a fake browser for every test
''',
        'src/coupon-form.js': '''
// A small UI component: a coupon box that validates and shows a message
export function mountCouponForm(root, { applyCoupon }) {
  root.innerHTML = `
    <form aria-label="Coupon">
      <label for="code">Coupon code</label>
      <input id="code" name="code">
      <button>Apply</button>
      <p role="status"></p>
    </form>`;
  const form = root.querySelector("form");
  const status = root.querySelector('[role="status"]');
  form.addEventListener("submit", async e => {
    e.preventDefault();
    const code = form.elements.code.value.trim().toUpperCase();
    if (!/^[A-Z0-9]{4,10}$/.test(code)) {
      status.textContent = "Enter 4 to 10 letters or digits";
      return;
    }
    form.querySelector("button").disabled = true;
    const result = await applyCoupon(code);
    status.textContent = result.ok ? `Saved ₹${result.saved}` : "This coupon has expired";
    form.querySelector("button").disabled = false;
  });
}
''',
        'src/coupon-form.test.js': '''
import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/dom";
import userEvent from "@testing-library/user-event";
import { mountCouponForm } from "./coupon-form.js";

describe("coupon form", () => {
  let applyCoupon;
  beforeEach(() => {
    document.body.innerHTML = "<div id=app></div>";
    applyCoupon = vi.fn();
    mountCouponForm(document.querySelector("#app"), { applyCoupon });
  });

  it("rejects a code that is too short without calling the server", async () => {
    await userEvent.type(screen.getByLabelText("Coupon code"), "ab");
    await userEvent.click(screen.getByRole("button", { name: "Apply" }));
    expect(screen.getByRole("status")).toHaveProperty("textContent", "Enter 4 to 10 letters or digits");
    expect(applyCoupon).not.toHaveBeenCalled();
  });

  it("trims and upper cases the code, then shows the saving", async () => {
    applyCoupon.mockResolvedValue({ ok: true, saved: 50 });
    await userEvent.type(screen.getByLabelText("Coupon code"), "  save10 {Enter}");
    await waitFor(() => expect(screen.getByRole("status").textContent).toBe("Saved ₹50"));
    expect(applyCoupon).toHaveBeenCalledWith("SAVE10");
  });

  it("shows an expiry message", async () => {
    applyCoupon.mockResolvedValue({ ok: false });
    await userEvent.type(screen.getByLabelText("Coupon code"), "OLD2020");
    await userEvent.click(screen.getByRole("button", { name: "Apply" }));
    expect(await screen.findByText("This coupon has expired")).toBeTruthy();
  });
});
''',
    }, 'npx vitest run --reporter=verbose', 'Unit testing UI code with jsdom and Testing Library', show=['vitest.config.js', 'src/coupon-form.js', 'src/coupon-form.test.js'], replace=VT),
    'web-jest': test({
        'package.json': pkg('web-jest', None, {'test': 'jest'}),
        'src/badge.js': '''
function renderCartBadge(el, count) {
  el.textContent = count > 99 ? "99+" : String(count);
  el.hidden = count === 0;
  el.setAttribute("aria-label", `${count} items in cart`);
}
module.exports = { renderCartBadge };
''',
        'src/badge.test.js': '''
/**
 * @jest-environment jsdom
 */
const { renderCartBadge } = require("./badge");

test.each([
  [0, "0", true],
  [3, "3", false],
  [120, "99+", false],
])("count %i shows %j, hidden: %s", (count, text, hidden) => {
  const el = document.createElement("span");
  renderCartBadge(el, count);
  expect(el.textContent).toBe(text);
  expect(el.hidden).toBe(hidden);
  expect(el.getAttribute("aria-label")).toBe(`${count} items in cart`);
});
''',
    }, 'npx jest --verbose', 'The same idea in Jest with a docblock', show=['src/badge.test.js'], replace=JEST),
    'api-unit': test({
        'package.json': pkg('api-unit', 'module', {'test': 'vitest run'}),
        'src/app.js': '''
import express from "express";

// The app receives its dependencies, so tests can hand it fakes
export function createApp({ stockService }) {
  const app = express();
  app.use(express.json());

  app.get("/api/products/:sku/stock", async (req, res) => {
    try {
      const qty = await stockService.get(req.params.sku);
      if (qty == null) return res.status(404).json({ error: "Unknown product" });
      res.json({ sku: req.params.sku, qty, inStock: qty > 0 });
    } catch {
      res.status(503).json({ error: "Stock service unavailable" });
    }
  });
  return app;
}
''',
        'src/stock-client.js': '''
// Talks to another team's HTTP service
export function stockClient(baseUrl) {
  return {
    async get(sku) {
      const res = await fetch(`${baseUrl}/stock/${encodeURIComponent(sku)}`);
      if (res.status === 404) return null;
      if (!res.ok) throw new Error(`stock service answered ${res.status}`);
      return (await res.json()).available;
    },
  };
}
''',
        'test/app.test.js': '''
import { describe, it, expect, vi } from "vitest";
import request from "supertest";
import { createApp } from "../src/app.js";

describe("GET /api/products/:sku/stock (route, fake service)", () => {
  const stockService = { get: vi.fn() };
  const app = createApp({ stockService });       // no port, supertest calls the app directly

  it("200 with the quantity", async () => {
    stockService.get.mockResolvedValue(4);
    const res = await request(app).get("/api/products/PEN-01/stock").expect(200).expect("Content-Type", /json/);
    expect(res.body).toEqual({ sku: "PEN-01", qty: 4, inStock: true });
  });

  it("404 for an unknown product", async () => {
    stockService.get.mockResolvedValue(null);
    await request(app).get("/api/products/NOPE/stock").expect(404, { error: "Unknown product" });
  });

  it("503 when the stock service fails", async () => {
    stockService.get.mockRejectedValue(new Error("timeout"));
    await request(app).get("/api/products/PEN-01/stock").expect(503);
  });
});
''',
        'test/stock-client.test.js': '''
import { describe, it, expect, afterEach } from "vitest";
import nock from "nock";
import { stockClient } from "../src/stock-client.js";

describe("stockClient (outgoing HTTP, faked with nock)", () => {
  const client = stockClient("https://stock.internal.example");
  afterEach(() => nock.cleanAll());

  it("reads the available quantity", async () => {
    const scope = nock("https://stock.internal.example").get("/stock/PEN-01").reply(200, { available: 12 });
    expect(await client.get("PEN-01")).toBe(12);
    expect(scope.isDone()).toBe(true);           // the request really happened
  });

  it("returns null on 404", async () => {
    nock("https://stock.internal.example").get("/stock/GONE").reply(404);
    expect(await client.get("GONE")).toBeNull();
  });

  it("throws on 500 so the route can answer 503", async () => {
    nock("https://stock.internal.example").get("/stock/PEN-01").reply(500);
    await expect(client.get("PEN-01")).rejects.toThrow("stock service answered 500");
  });
});
''',
    }, 'npx vitest run --reporter=verbose', 'Unit testing API code: routes with supertest, outgoing calls with nock',
        show=['src/app.js', 'test/app.test.js', 'src/stock-client.js', 'test/stock-client.test.js'], replace=VT),
    'ci': show('''
# .github/workflows/tests.yml
name: tests
on: [push, pull_request]
jobs:
  unit:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node: [22, 24, 26]          # the same tests on three Node.js versions
        shard: [1, 2]               # each version split over two machines
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with: { node-version: "${{ matrix.node }}", cache: npm }
      - run: npm ci
      - run: npx vitest run --shard=${{ matrix.shard }}/2 --coverage --reporter=junit --outputFile=junit.xml
      - uses: actions/upload-artifact@v4
        if: always()                # keep the report even when tests fail
        with: { name: "junit-${{ matrix.node }}-${{ matrix.shard }}", path: junit.xml }
''', 'Running unit tests in CI', lang='yaml', note='Reference', result='Six jobs run in parallel: three Node.js versions times two shards. The JUnit files feed the test report in the pull request.'),
    'regression-red': test({
        'package.json': pkg('bug-4711', 'module', {'test': 'node --test --test-reporter=spec'}),
        'src/split.js': '''
// Bug 4711: "Splitting ₹100 between 3 friends loses a rupee"
export function splitBill(total, people) {
  const share = Math.floor((total / people) * 100) / 100;
  return Array(people).fill(share);
}
''',
        'test/split.test.js': '''
import { test } from "node:test";
import assert from "node:assert/strict";
import { splitBill } from "../src/split.js";

test("bug 4711: shares always add up to the total", () => {
  const shares = splitBill(100, 3);
  const sum = Math.round(shares.reduce((a, b) => a + b) * 100) / 100;
  assert.equal(sum, 100);
});

test("shares differ by at most one paisa", () => {
  const shares = splitBill(100, 3);
  assert.ok(Math.max(...shares) - Math.min(...shares) <= 0.011);
});
''',
    }, 'npm test', 'Step 1: a test that reproduces the bug fails', expect='fail', badge='🔴 Red: the test fails, as it should', replace=NT + [(r'\n\s+at [\s\S]*?(?=\n\S|\n\n|$)', ''), (r'\n  \{\n[\s\S]*?\n  \}', '')]),
    'regression-green': test({
        'package.json': pkg('bug-4711', 'module', {'test': 'node --test --test-reporter=spec'}),
        'src/split.js': '''
// Work in paise (whole numbers), then hand the leftover paise out one by one
export function splitBill(total, people) {
  const paise = Math.round(total * 100);
  const base = Math.floor(paise / people);
  const extra = paise - base * people;
  return Array.from({ length: people }, (_, i) => (base + (i < extra ? 1 : 0)) / 100);
}
''',
        'test/split.test.js': '''
import { test } from "node:test";
import assert from "node:assert/strict";
import { splitBill } from "../src/split.js";

test("bug 4711: shares always add up to the total", () => {
  const shares = splitBill(100, 3);
  const sum = Math.round(shares.reduce((a, b) => a + b) * 100) / 100;
  assert.equal(sum, 100);
});

test("shares differ by at most one paisa", () => {
  const shares = splitBill(100, 3);
  assert.ok(Math.max(...shares) - Math.min(...shares) <= 0.011);
});

test("examples", () => {
  assert.deepEqual(splitBill(100, 3), [33.34, 33.33, 33.33]);
  assert.deepEqual(splitBill(10, 4), [2.5, 2.5, 2.5, 2.5]);
});
''',
    }, 'npm test', 'Step 2: fix the code and the same tests pass', show=['src/split.js'], badge='🟢 Green: fixed', replace=NT),
}

PARTS = [
    part('basics', '🧱', 'What a unit test is', '''
<p>A <b>unit test</b> checks one small piece of code, usually one function or one class, on its own. It runs in milliseconds, needs no browser, server or database, and tells you exactly which piece broke. A good suite has many unit tests, fewer API or integration tests, and a small number of slow end to end tests. This shape is called the <b>test pyramid</b>.</p>
<div class="viz" data-viz="flow" data-k="pyramid"></div>
<p>Every test follows the same three steps: <b>Arrange</b> the input, <b>Act</b> by calling the code, <b>Assert</b> that the result is right. Node.js has a test runner built in, so the first suite needs nothing installed.</p>
[[first]]
<div class="tip">Good unit tests are fast, independent of each other and of the order they run in, repeatable on any machine, and named so that a failure explains itself: "takes 10% off with SAVE10" beats "test 3".</div>
''', qa=['node:test'], qa_why="Testers who read and write unit tests can review developers' tests and spot missing cases early.",
        kw=['unit test', 'test pyramid', 'Arrange Act Assert', 'AAA', 'node:test', 'describe', 'it', 'assert', 'assert.equal', 'assert.throws', 'deepEqual']),
    part('doubles', '🎭', 'Mocks, spies, stubs and fake timers', '''
<p>Real code calls other things: an email service, the clock, the network. A unit test swaps them for <b>test doubles</b> so the test is fast and predictable and never sends a real email.</p>
<div class="tw"><table class="jt"><tr><th>Double</th><th>What it does</th><th>Example</th></tr>
<tr><td>Stub</td><td>returns a fixed answer</td><td>the stock service always says 7</td></tr>
<tr><td>Spy</td><td>records how it was called</td><td>was <code>send</code> called once, with which arguments</td></tr>
<tr><td>Mock</td><td>a stub and a spy together, often replacing a whole module</td><td><code>jest.mock("./mailer")</code></td></tr>
<tr><td>Fake</td><td>a small working version</td><td>an in memory database, a fake clock</td></tr>
</table></div>
[[node-mocks]]
<div class="warn">Mock what is slow or outside your control, not the code under test itself. A test where everything is mocked only proves that the mocks work.</div>
''', qa=True, qa_why='Mocks and fake timers are how tests cover error paths and time based rules without waiting or breaking real systems.',
        kw=['mock', 'spy', 'stub', 'fake', 'test double', 'mock.fn', 'mock.timers', 'fake timers', 'dependency injection', 'beforeEach', 'callCount']),
    part('jest', '🃏', 'Jest', '''
<p><b>Jest</b> is the most used JavaScript test runner. It has matchers built in (<code>expect(x).toBe(y)</code>), table driven tests with <code>test.each</code>, mocks for whole modules, fake timers, snapshots and coverage. By default it uses CommonJS.</p>
[[jest-basics]]
[[jest-mocks]]
<div class="tw"><table class="jt"><tr><th>Matcher</th><th>Passes when</th></tr>
<tr><td><code>toBe(x)</code></td><td>same value, or same object (<code>Object.is</code>)</td></tr>
<tr><td><code>toEqual(x)</code></td><td>same contents, deeply</td></tr>
<tr><td><code>toMatchObject(x)</code></td><td>contains at least these properties</td></tr>
<tr><td><code>toBeCloseTo(x, digits)</code></td><td>decimals are close enough</td></tr>
<tr><td><code>toThrow(x)</code></td><td>the function throws a matching error</td></tr>
<tr><td><code>resolves</code>, <code>rejects</code></td><td>for promises, always with <code>await</code></td></tr>
<tr><td><code>toHaveBeenCalledWith(...)</code></td><td>a mock was called with these arguments</td></tr>
</table></div>
''', qa=['Jest'], qa_why='Jest is the default runner in many company projects, and its expect API is reused by Playwright and Vitest.',
        kw=['Jest', 'expect', 'toBe', 'toEqual', 'toMatchObject', 'toThrow', 'test.each', 'jest.fn', 'jest.mock', 'jest.spyOn', 'mockResolvedValue', 'useFakeTimers', 'advanceTimersByTime']),
    part('vitest-mocha', '⚡', 'Vitest and Mocha', '''
<p><b>Vitest</b> has almost the same API as Jest (<code>vi.fn</code> instead of <code>jest.fn</code>) but runs ES modules and TypeScript with no set up and is very fast. It is the natural choice for Vite, Vue and modern React projects.</p>
[[vitest]]
<p><b>Mocha</b> is older and smaller: it only runs tests. You add an assertion library such as <b>Chai</b> and a mocking library such as <b>Sinon</b>. WebdriverIO and many Selenium suites use Mocha style <code>describe</code> and <code>it</code>.</p>
[[mocha]]
<div class="tw"><table class="jt"><tr><th></th><th>node:test</th><th>Jest</th><th>Vitest</th><th>Mocha</th></tr>
<tr><td>Install</td><td>nothing</td><td>one package</td><td>one package</td><td>plus Chai and Sinon</td></tr>
<tr><td>Assertions</td><td><code>node:assert</code></td><td><code>expect</code></td><td><code>expect</code></td><td>Chai</td></tr>
<tr><td>Mocks</td><td><code>mock.fn</code></td><td><code>jest.fn</code></td><td><code>vi.fn</code></td><td>Sinon</td></tr>
<tr><td>ES modules and TS</td><td>yes</td><td>needs set up</td><td>yes</td><td>yes</td></tr>
<tr><td>Seen in</td><td>libraries, small tools</td><td>React, Node.js APIs</td><td>Vite, Vue, new projects</td><td>WebdriverIO, Selenium suites</td></tr>
</table></div>
''', qa=['Vitest', 'Mocha', 'WebdriverIO'], qa_why='You will meet all of these in real projects, and WebdriverIO tests use the Mocha style by default.',
        kw=['Vitest', 'vi.fn', 'vi.useFakeTimers', 'Mocha', 'Chai', 'Sinon', 'expect', 'spy', 'stub', 'mocharc', 'debounce', 'concurrent']),
    part('running', '🏃', 'Running tests in different ways', '''
<p>The same suite is run differently depending on the moment: everything before a merge, one file while you fix it, only smoke tests after a deploy, split across machines in CI. Every runner has options for this.</p>
[[ways-node]]
[[ways-jest]]
<p>The last command failed on purpose. No Jest test passes something that is not an array, so the error branch on line 2 of cart.js never ran. A coverage threshold turns that gap into a failing build, which is how teams stop coverage from slowly dropping.</p>
<div class="tw"><table class="jt"><tr><th>Goal</th><th>node:test</th><th>Jest</th><th>Vitest</th><th>Mocha</th></tr>
<tr><td>one file</td><td><code>node --test file</code></td><td><code>jest path</code></td><td><code>vitest run path</code></td><td><code>mocha file</code></td></tr>
<tr><td>by name or tag</td><td><code>--test-name-pattern</code>, tags</td><td><code>-t "name"</code></td><td><code>-t "name"</code></td><td><code>--grep</code></td></tr>
<tr><td>only this one</td><td><code>test.only</code> with <code>--test-only</code></td><td><code>test.only</code></td><td><code>test.only</code></td><td><code>it.only</code></td></tr>
<tr><td>skip or todo</td><td><code>test.skip</code>, <code>test.todo</code></td><td><code>test.skip</code>, <code>test.todo</code></td><td>same</td><td><code>it.skip</code></td></tr>
<tr><td>rerun on save</td><td><code>--watch</code></td><td><code>--watch</code></td><td><code>vitest</code> (default)</td><td><code>--watch</code></td></tr>
<tr><td>split over machines</td><td><code>--test-shard=1/3</code></td><td><code>--shard=1/3</code></td><td><code>--shard=1/3</code></td><td>by file lists</td></tr>
<tr><td>stop at first failure</td><td>no flag yet</td><td><code>--bail</code></td><td><code>--bail=1</code></td><td><code>--bail</code></td></tr>
<tr><td>report for CI</td><td><code>--test-reporter=junit</code></td><td><code>jest-junit</code> reporter</td><td><code>--reporter=junit</code></td><td><code>--reporter xunit</code></td></tr>
<tr><td>coverage</td><td><code>--experimental-test-coverage</code></td><td><code>--coverage</code></td><td><code>--coverage</code></td><td>with <code>c8</code></td></tr>
</table></div>
[[ci]]
<div class="warn">A <code>test.only</code> committed by mistake silently skips the rest of the suite in some runners. Add a lint rule or run CI with <code>--forbid-only</code> (Mocha, Playwright) to block it.</div>
''', qa=True, qa_why='Choosing which tests run where, and reading coverage and JUnit reports, is daily work for test automation engineers.',
        kw=['run tests', 'filter', 'grep', 'test-name-pattern', '-t', 'tags', 'only', 'skip', 'todo', 'watch', 'shard', 'bail', 'reporter', 'junit', 'coverage', 'coverage threshold', 'CI', 'GitHub Actions', 'matrix']),
    part('web', '🖼️', 'Unit testing web (UI) code', '''
<p>UI components can be unit tested without a real browser. <b>jsdom</b> is a browser written in JavaScript that runs inside Node.js: it has <code>document</code>, events and forms, but draws nothing. <b>Testing Library</b> adds queries that find elements the way a user does, by role, label and text, and <b>user-event</b> types and clicks like a person.</p>
[[web-unit]]
[[web-jest]]
<div class="vs"><div><b>Unit test with jsdom</b>Milliseconds per test. Great for logic, validation messages, states such as disabled buttons. Cannot see layout, CSS, real scrolling or browser differences.</div><div><b>Browser test with Playwright</b>Seconds per test. Real rendering, real network, every browser. Keep these for the journeys that matter most.</div></div>
<div class="qa-box">The query priority of Testing Library, role first, then label, then text, then test id, is the same advice Playwright gives for locators. Learn it once and use it in both kinds of test.</div>
''', qa=['Jest', 'Vitest', 'Testing Library'], qa_why='Component tests cover UI rules at unit speed and use the same locator thinking as Playwright.',
        kw=['jsdom', 'Testing Library', 'user-event', 'screen', 'getByRole', 'getByLabelText', 'findByText', 'waitFor', 'component test', 'testEnvironment', 'jest-environment-jsdom', 'environment jsdom']),
    part('api', '🔌', 'Unit testing API code', '''
<p>API code has two sides to test. <b>Incoming</b>: your routes. <b>supertest</b> sends requests straight into an Express app, without opening a port, and checks the status, headers and body. <b>Outgoing</b>: calls your code makes to other services. <b>nock</b> intercepts them and answers with whatever the test needs, including errors that are hard to produce for real.</p>
[[api-unit]]
<div class="tip">Passing <code>stockService</code> into <code>createApp</code> is what makes the route easy to test. Code that creates its own clients inside every function is much harder to test, so testable design starts with how dependencies are passed in.</div>
<div class="dev-box">Chapter 20 goes further: tests against a running server, JSON Schema validation, contract checks and Playwright's API testing.</div>
''', qa=['supertest', 'nock', 'Jest', 'Vitest'], qa_why='Most API test frameworks start from supertest and nock, and their ideas carry over to every other tool.',
        kw=['API unit test', 'supertest', 'nock', 'Express', 'route test', 'status code', 'mock HTTP', 'outgoing request', 'dependency injection', '503', '404']),
    part('scenario', '🎬', 'Real world scenario: turn a bug report into a test', '''
<div class="scenario"><b>The situation</b>A customer reports that splitting ₹100 between 3 friends shows ₹33.33 each, so ₹0.01 vanishes. You must fix it and make sure it never comes back.</div>
<p>First write a test that reproduces the bug and watch it fail. A failing test proves the test can see the bug.</p>
[[regression-red]]
<p>Then fix the code. The cure is to work in whole paise and give the leftover paise to the first people.</p>
[[regression-green]]
<p>This red then green cycle is the heart of <b>test driven development</b> (TDD). The test now stays in the suite as a <b>regression test</b>, named after the bug, so anyone who breaks it again sees the history.</p>
''', qa=True, kw=['regression test', 'bug report', 'TDD', 'test driven development', 'red green refactor', 'rounding', 'money', 'paise']),
]

DG = {
    'pyramid': {'t': 'The test pyramid', 'w': 900, 'h': 300,
                'n': [['e2e', 330, 20, 240, 60, 'End to end (UI)', {'c': 4, 'sub': 'few, slow, most realistic', 'i': 'Playwright, Cypress, Selenium. Seconds to minutes each.'}],
                      ['api', 230, 110, 440, 60, 'API and integration', {'c': 1, 'sub': 'some, fast enough', 'i': 'supertest, fetch, Playwright request. Tens to hundreds of milliseconds each.'}],
                      ['unit', 110, 200, 680, 60, 'Unit', {'c': 2, 'sub': 'many, milliseconds each', 'i': 'node:test, Jest, Vitest, Mocha. Thousands can run in seconds.'}]],
                'e': [['unit', 'api', {'t': 'more confidence per test'}], ['api', 'e2e', {'t': 'more confidence per test'}]],
                'st': [[['unit'], 'The base: many small, fast unit tests for logic and edge cases.'],
                       [['api', 'unit>api'], 'The middle: API and integration tests that check parts working together.'],
                       [['e2e', 'api>e2e'], 'The top: a few end to end tests for the most important user journeys. They are slow and the most likely to flake.']]},
}

INFO = {'title': 'Small checks, run often', 'panels': [
    panel([['e', '🧱'], ['t', 'Arrange, Act, Assert', {'b': 1}]], 'One unit', 'Check one function with known input.', 'Milliseconds per test, so you can run thousands.'),
    panel([['e', '🎭'], ['t', 'vi.fn(), mock.timers', {'b': 1}]], 'Doubles', 'Replace email, clock and network with fakes.', 'Fast, predictable, and no real side effects.'),
    panel([['e', '🏃'], ['t', '-t "@smoke" --shard=1/3', {'b': 1, 'size': 11}]], 'Run it your way', 'Filter, tag, shard, watch, report.', 'The right subset at the right moment.'),
    panel([['e', '🔴🟢'], ['t', 'red → green', {'b': 1}]], 'Regression', 'Every bug becomes a test.', 'Fail first, then fix, then keep the test forever.')],
    'remember': 'Many fast unit tests, doubles for what is slow or outside, and a failing test before every fix.'}

REAL = [
    ['⚛️', 'A React team', 'Runs 4,000 Vitest tests in 40 seconds on every save and only 60 Playwright journeys before each deploy.'],
    ['🏦', 'A payments API', 'Uses nock to simulate bank timeouts and declines that would be impossible to trigger with the real bank sandbox.'],
    ['🐞', 'The bug that came back', 'A rounding bug in invoices returned twice until the team added a regression test named after the ticket.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers unit testing with node test, Jest, Vitest and Mocha, test doubles, many ways to run tests, and unit tests for web and API code.',
        'यह अध्याय node:test, Jest, Vitest और Mocha से unit testing, test doubles, tests चलाने के कई तरीके, और web व API code के unit tests सिखाता है।',
        'ಈ ಅಧ್ಯಾಯ node:test, Jest, Vitest ಮತ್ತು Mocha ಮೂಲಕ unit testing, test doubles, tests ಓಡಿಸುವ ಹಲವು ವಿಧಗಳು ಮತ್ತು web, API code ನ unit tests ಕಲಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ node:test, Jest, Vitest ଓ Mocha ରେ unit testing, test doubles, tests ଚଲାଇବାର ଅନେକ ଉପାୟ ଓ web, API code ର unit tests ଶିଖାଏ।',
        'يتناول هذا الفصل اختبار الوحدات باستخدام node:test وJest وVitest وMocha، وبدائل الاختبار، وطرق تشغيل الاختبارات، واختبار كود الويب وواجهات API.',
        'Dieses Kapitel behandelt Unit-Tests mit node:test, Jest, Vitest und Mocha, Test-Doubles, viele Wege, Tests auszuführen, und Unit-Tests für Web- und API-Code.'),
    say('basics', 'Unit tests', 'A unit test checks one small piece of code in milliseconds. Arrange the input, act, then assert the result. Have many unit tests and few slow ones.',
        'Unit test code के एक छोटे हिस्से को milliseconds में जांचता है। Input तैयार करें, चलाएं, फिर result assert करें।',
        'Unit test code ನ ಒಂದು ಚಿಕ್ಕ ಭಾಗವನ್ನು milliseconds ನಲ್ಲಿ ಪರಿಶೀಲಿಸುತ್ತದೆ. Input ತಯಾರಿಸಿ, ಓಡಿಸಿ, result assert ಮಾಡಿ.',
        'Unit test code ର ଛୋଟ ଅଂଶକୁ milliseconds ରେ ଯାଞ୍ଚ କରେ। Input ପ୍ରସ୍ତୁତ କରନ୍ତୁ, ଚଲାନ୍ତୁ, ତାପରେ result assert କରନ୍ତୁ।',
        'يفحص اختبار الوحدة جزءًا صغيرًا من الكود في أجزاء من الثانية. جهز المدخلات ونفذ ثم تحقق من النتيجة.',
        'Ein Unit-Test prüft ein kleines Stück Code in Millisekunden. Eingabe vorbereiten, ausführen, Ergebnis prüfen.'),
    say('doubles', 'Test doubles', 'Stubs answer, spies record, mocks do both and fakes are small working versions. Use them for the slow and the outside, never for the code under test.',
        'Stubs जवाब देते हैं, spies रिकॉर्ड करते हैं, mocks दोनों करते हैं और fakes छोटे काम करने वाले versions हैं।',
        'Stubs ಉತ್ತರಿಸುತ್ತವೆ, spies ದಾಖಲಿಸುತ್ತವೆ, mocks ಎರಡೂ ಮಾಡುತ್ತವೆ, fakes ಚಿಕ್ಕ ಕೆಲಸ ಮಾಡುವ versions.',
        'Stubs ଉତ୍ତର ଦିଅନ୍ତି, spies ରେକର୍ଡ କରନ୍ତି, mocks ଦୁହେଁ କରନ୍ତି ଏବଂ fakes ଛୋଟ କାମ କରୁଥିବା versions।',
        'البدائل الثابتة تجيب، والجواسيس تسجل، والمحاكيات تفعل الأمرين، والمزيفات نسخ عاملة صغيرة. استخدمها للبطيء والخارجي فقط.',
        'Stubs antworten, Spies zeichnen auf, Mocks tun beides, Fakes sind kleine funktionierende Versionen.'),
    say('jest', 'Jest', 'Jest has matchers, table driven tests, module mocks and fake timers built in. Always await resolves and rejects.',
        'Jest में matchers, table driven tests, module mocks और fake timers पहले से हैं। resolves और rejects को हमेशा await करें।',
        'Jest ನಲ್ಲಿ matchers, table driven tests, module mocks ಮತ್ತು fake timers ಇವೆ. resolves ಮತ್ತು rejects ಅನ್ನು ಯಾವಾಗಲೂ await ಮಾಡಿ.',
        'Jest ରେ matchers, table driven tests, module mocks ଓ fake timers ଅଛି। resolves ଓ rejects କୁ ସର୍ବଦା await କରନ୍ତୁ।',
        'يحتوي Jest على المطابقات والاختبارات الجدولية ومحاكاة الوحدات والمؤقتات المزيفة. انتظر resolves وrejects دائمًا.',
        'Jest bringt Matcher, tabellengetriebene Tests, Modul-Mocks und Fake-Timer mit. resolves und rejects immer mit await.'),
    say('vitest-mocha', 'Vitest and Mocha', 'Vitest is Jest compatible and ES module first. Mocha only runs tests and pairs with Chai for assertions and Sinon for mocks.',
        'Vitest Jest जैसा है और ES modules के लिए बना है। Mocha सिर्फ tests चलाता है और Chai व Sinon के साथ आता है।',
        'Vitest Jest ಹೊಂದಾಣಿಕೆಯದು, ES modules ಗೆ ಮೊದಲ ಆದ್ಯತೆ. Mocha tests ಮಾತ್ರ ಓಡಿಸುತ್ತದೆ, Chai ಮತ್ತು Sinon ಜೊತೆ ಬಳಸಲಾಗುತ್ತದೆ.',
        'Vitest Jest ପରି ଏବଂ ES modules ପାଇଁ ତିଆରି। Mocha କେବଳ tests ଚଲାଏ ଏବଂ Chai ଓ Sinon ସହ ବ୍ୟବହୃତ ହୁଏ।',
        'Vitest متوافق مع Jest ويدعم وحدات ES أولًا. أما Mocha فيشغل الاختبارات فقط ويقترن بـ Chai للتحقق وSinon للمحاكاة.',
        'Vitest ist Jest-kompatibel und setzt auf ES-Module. Mocha führt nur Tests aus und nutzt Chai und Sinon.'),
    say('running', 'Running tests', 'Run one file, filter by name or tag, skip, watch, shard across machines, write JUnit reports and measure coverage. Block a forgotten only in CI.',
        'एक file चलाएं, नाम या tag से filter करें, skip, watch, machines में shard करें, JUnit reports लिखें और coverage मापें।',
        'ಒಂದು file ಓಡಿಸಿ, ಹೆಸರು ಅಥವಾ tag ನಿಂದ filter, skip, watch, machines ನಲ್ಲಿ shard, JUnit reports ಮತ್ತು coverage.',
        'ଗୋଟିଏ file ଚଲାନ୍ତୁ, ନାମ କିମ୍ବା tag ରେ filter, skip, watch, machines ରେ shard, JUnit reports ଓ coverage।',
        'شغّل ملفًا واحدًا، أو رشّح بالاسم أو الوسم، أو تخطَّ، أو راقب، أو وزّع على الأجهزة، واكتب تقارير JUnit وقس التغطية.',
        'Eine Datei ausführen, nach Name oder Tag filtern, überspringen, beobachten, auf Maschinen aufteilen, JUnit-Berichte und Abdeckung.'),
    say('web', 'Web unit tests', 'jsdom gives Node a fake browser. Testing Library finds elements by role and label, and user event types and clicks like a person.',
        'jsdom Node को एक नकली browser देता है। Testing Library role और label से elements ढूंढती है, और user-event इंसान की तरह type और click करता है।',
        'jsdom Node ಗೆ ನಕಲಿ browser ಕೊಡುತ್ತದೆ. Testing Library role ಮತ್ತು label ನಿಂದ elements ಹುಡುಕುತ್ತದೆ, user-event ಮನುಷ್ಯರಂತೆ type, click ಮಾಡುತ್ತದೆ.',
        'jsdom Node କୁ ନକଲି browser ଦିଏ। Testing Library role ଓ label ରେ elements ଖୋଜେ, user-event ମଣିଷ ପରି type ଓ click କରେ।',
        'يعطي jsdom لـ Node متصفحًا مزيفًا. تجد Testing Library العناصر بالدور والتسمية، وتكتب user-event وتنقر مثل الإنسان.',
        'jsdom gibt Node einen Schein-Browser. Testing Library findet Elemente nach Rolle und Label, user-event tippt und klickt wie ein Mensch.'),
    say('api', 'API unit tests', 'supertest sends requests straight into an Express app. nock fakes the services your code calls, including failures.',
        'supertest requests सीधे Express app में भेजता है। nock उन services को नकली बनाता है जिन्हें आपका code call करता है।',
        'supertest requests ಅನ್ನು ನೇರವಾಗಿ Express app ಗೆ ಕಳುಹಿಸುತ್ತದೆ. nock ನಿಮ್ಮ code ಕರೆಯುವ services ಅನ್ನು ನಕಲಿ ಮಾಡುತ್ತದೆ.',
        'supertest requests ସିଧା Express app କୁ ପଠାଏ। nock ଆପଣଙ୍କ code call କରୁଥିବା services କୁ ନକଲି କରେ।',
        'يرسل supertest الطلبات مباشرة إلى تطبيق Express. ويزيف nock الخدمات التي يستدعيها كودك، بما فيها الأعطال.',
        'supertest schickt Anfragen direkt in eine Express-App. nock fälscht die Dienste, die dein Code aufruft, auch Fehler.'),
    say('scenario', 'Scenario', 'Write a test that reproduces the bug and see it fail, fix the code, see it pass, and keep the test as a regression test.',
        'Bug दोहराने वाला test लिखें और उसे fail होते देखें, code ठीक करें, pass होते देखें, और test को regression test के रूप में रखें।',
        'Bug ಪುನರಾವರ್ತಿಸುವ test ಬರೆದು fail ಆಗುವುದನ್ನು ನೋಡಿ, code ಸರಿಪಡಿಸಿ, pass ಆಗುವುದನ್ನು ನೋಡಿ, regression test ಆಗಿ ಇಡಿ.',
        'Bug ପୁନରାବୃତ୍ତି କରୁଥିବା test ଲେଖି fail ହେବା ଦେଖନ୍ତୁ, code ଠିକ୍ କରନ୍ତୁ, pass ଦେଖନ୍ତୁ, ଏବଂ regression test ଭାବେ ରଖନ୍ତୁ।',
        'اكتب اختبارًا يعيد إنتاج الخطأ وشاهده يفشل، ثم أصلح الكود وشاهده ينجح، واحتفظ به اختبارًا للتراجع.',
        'Schreibe einen Test, der den Fehler zeigt, sieh ihn scheitern, repariere den Code, sieh ihn bestehen und behalte ihn.'),
    say('practice', 'Hands-on', 'Practise a deep equality check, a spy, a tiny test runner with only and skip, and splitting tests into shards.',
        'Deep equality check, spy, only और skip वाला छोटा test runner, और tests को shards में बांटने का अभ्यास करें।',
        'Deep equality check, spy, only ಮತ್ತು skip ಇರುವ ಚಿಕ್ಕ test runner ಮತ್ತು tests ಅನ್ನು shards ಆಗಿ ವಿಭಜಿಸುವುದನ್ನು ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Deep equality check, spy, only ଓ skip ଥିବା ଛୋଟ test runner ଓ tests କୁ shards ରେ ବାଣ୍ଟିବା ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على فحص التساوي العميق ودالة تجسس ومشغل اختبارات صغير يدعم only وskip وتقسيم الاختبارات إلى أجزاء.',
        'Übe einen tiefen Gleichheitsvergleich, einen Spy, einen kleinen Testrunner mit only und skip und das Aufteilen in Shards.'),
]

QUIZ = [
    quiz('e', 'What are the three steps of a typical unit test?', ['Arrange, Act, Assert', 'Build, Deploy, Monitor', 'Click, Wait, Check', 'Plan, Code, Ship'], 0, 'AAA.', 'Prepare the input, call the code, check the result.'),
    quiz('e', 'Which Jest matcher compares the contents of two objects?', ['toEqual', 'toBe', 'toBeTruthy', 'toContain'], 0, 'toBe compares identity.', 'toEqual compares deeply. toBe uses Object.is.'),
    quiz('e', 'Which runner is built into Node.js?', ['node:test', 'Jest', 'Mocha', 'Vitest'], 0, 'No install needed.', 'node --test runs it, with node:assert for checks.'),
    quiz('m', 'A test must not send real emails. What do you use?', ['A mock or stub for the mailer', 'A slower test', 'A try catch', 'A longer timeout'], 0, 'Replace the outside service.', 'A test double records the call without any real side effect.'),
    quiz('m', 'Which command runs only Jest tests whose name contains "@smoke"?', ['npx jest -t "@smoke"', 'npx jest --smoke', 'npx jest @smoke.test.js', 'npx jest --only smoke'], 0, 't for test name.', '-t filters by test name, which is how tags in names work in Jest.'),
    quiz('m', 'What does --shard=2/3 do?', ['Runs the second of three equal parts of the suite', 'Runs tests 2 and 3', 'Runs the suite three times', 'Retries twice'], 0, 'Split across machines.', 'Three CI machines each take one shard, so the suite finishes about three times faster.'),
    quiz('h', 'expect(promise).rejects.toThrow("x") without await. What can happen?', ['The test passes even if the promise fulfils', 'It always fails', 'It throws a syntax error', 'Jest waits automatically'], 0, 'Chapter 10.', 'Without await, the test ends before the assertion is checked.'),
    quiz('h', 'Why does supertest not need app.listen()?', ['It passes requests straight to the app function', 'It uses a fixed port', 'It mocks Express', 'It only checks headers'], 0, 'In process.', 'supertest starts a temporary server internally or calls the handler directly, so tests never fight over ports.'),
    quiz('h', 'What can jsdom not test?', ['Real layout and CSS, such as an element hidden behind another', 'Click handlers', 'Form validation messages', 'Text content'], 0, 'It draws nothing.', 'jsdom has no rendering, so overlap and visual bugs need a real browser.'),
    quiz('x', 'A suite has a test.only left in by mistake. What is the safest CI protection?', ['Fail the run with --forbid-only or a lint rule', 'Run the suite twice', 'Use --bail', 'Use coverage'], 0, 'Make it impossible to merge.', 'Blocking .only stops one test from silently replacing the whole suite.'),
    quiz('x', 'Which statement about 100% line coverage is true?', ['It shows every line ran, not that every result was checked', 'It proves there are no bugs', 'It means every branch was tested', 'It is required by Jest'], 0, 'Running is not checking.', 'A test with no assertions still counts as coverage. Coverage finds untested code, not correct code.'),
    quiz('x', 'Why write the failing test before fixing a bug?', ['It proves the test can detect the bug', 'It is faster', 'Fixes do not need tests', 'It raises coverage'], 0, 'Red first.', 'If the test passed before the fix, it would not protect you from the bug coming back.'),
]

CALC = [
    calc('e', 'A suite has 4,000 unit tests at 2 ms each. How many seconds does it take run one after another?', '8', 'Multiply, then divide by 1000.', ['<span class="eq">4000 × 2 = 8000</span> ms', '<span class="eq">8000 ÷ 1000 = 8</span> s']),
    calc('e', 'What does cartTotal([{ price: 20, qty: 3 }, { price: 250, qty: 1 }]) return?', '310', 'Price times quantity, added.', ['<span class="eq">20 × 3 + 250 × 1 = 310</span>']),
    calc('m', 'A coupon takes 10% off a ₹199 cart. What is the total?', '179.1', '10% of 199 is 19.9.', ['<span class="eq">199 − 19.9 = 179.1</span>']),
    calc('m', 'A CI matrix has 3 Node.js versions and 2 shards. How many jobs run?', '6', 'Multiply the lists.', ['<span class="eq">3 × 2 = 6</span>']),
    calc('h', 'The suite takes 12 minutes on one machine. Split into 4 even shards, how many minutes until all are done?', '3', 'Each shard gets a quarter.', ['<span class="eq">12 ÷ 4 = 3</span>']),
    calc('h', 'A file has 40 lines and the tests run 34 of them. What is the line coverage in percent?', '85', 'Covered over total.', ['<span class="eq">34 ÷ 40 × 100 = 85</span>']),
    calc('x', '₹100 split between 3 people in whole paise. How many people get the extra paisa?', '1', 'Work in paise.', ['<span class="eq">10000 ÷ 3 = 3333</span> remainder 1.', 'One person gets 3334 paise, the others 3333.']),
    calc('x', 'Debounce of 300 ms. The user types at 0, 100 and 250 ms. At what time in ms does the search run?', '550', 'The timer restarts on every key.', ['The last key is at 250 ms.', '<span class="eq">250 + 300 = 550</span>']),
]

EX = [
    ex('deep', 'e', 'Deep equality', '<p>Write <code>deepEqual(a, b)</code> that returns true when two values have the same contents: numbers, strings, booleans, null, arrays and plain objects, nested to any depth. Key order in objects does not matter.</p>',
       'function deepEqual(a, b) {\n  \n}\n',
       [('deepEqual({ a: [1, { b: 2 }] }, { a: [1, { b: 2 }] })', True), ('deepEqual({ a: 1, b: 2 }, { b: 2, a: 1 })', True), ('deepEqual([1, 2], [1, 2, 3])', False),
        ('deepEqual({ a: 1 }, { a: "1" })', False), ('deepEqual(null, {})', False)],
       'function deepEqual(a, b) {\n  if (Object.is(a, b)) return true;\n  if (typeof a !== "object" || typeof b !== "object" || a === null || b === null) return false;\n  if (Array.isArray(a) !== Array.isArray(b)) return false;\n  const ka = Object.keys(a), kb = Object.keys(b);\n  if (ka.length !== kb.length) return false;\n  return ka.every(k => Object.hasOwn(b, k) && deepEqual(a[k], b[k]));\n}',
       hint='Handle the simple case with <code>Object.is</code>, then compare keys and call yourself for each value.', why='This is the heart of <code>toEqual</code> and <code>assert.deepEqual</code>.'),
    ex('spy', 'm', 'A spy function', '<p>Write <code>createSpy(impl)</code> that returns a function. Calling it runs <code>impl</code> (if given) with the same arguments and returns its result. The function has a <code>calls</code> array of argument lists and a <code>calledWith(...args)</code> method.</p>',
       'function createSpy(impl) {\n  \n}\n',
       [('(() => { const s = createSpy((a, b) => a + b); const r = s(2, 3); s(1, 1); return [r, s.calls]; })()', [5, [[2, 3], [1, 1]]]),
        ('(() => { const s = createSpy(); s("pen", 2); return [s.calledWith("pen", 2), s.calledWith("pen")]; })()', [True, False])],
       'function createSpy(impl) {\n  const spy = (...args) => {\n    spy.calls.push(args);\n    return impl ? impl(...args) : undefined;\n  };\n  spy.calls = [];\n  spy.calledWith = (...want) => spy.calls.some(c => JSON.stringify(c) === JSON.stringify(want));\n  return spy;\n}',
       hint='Functions are objects, so you can attach <code>calls</code> and <code>calledWith</code> to the function itself.', why='jest.fn, vi.fn and mock.fn all work this way underneath.'),
    ex('runner', 'h', 'A tiny test runner', '<p>Write <code>async runTests(tests)</code>. Each test is <code>{ name, fn, only, skip }</code>. If any test has <code>only</code>, run only those. Skip tests with <code>skip</code>. A test fails when <code>fn</code> throws or its promise rejects. Return <code>{ passed, failed, skipped }</code> as counts.</p>',
       'async function runTests(tests) {\n  \n}\n',
       [('runTests([{ name: "a", fn: () => {} }, { name: "b", fn: () => { throw new Error("x"); } }, { name: "c", fn: () => {}, skip: true }])', {'passed': 1, 'failed': 1, 'skipped': 1}),
        ('runTests([{ name: "a", fn: async () => { throw new Error("late"); } }, { name: "b", fn: () => {}, only: true }])', {'passed': 1, 'failed': 0, 'skipped': 1}),
        ('runTests([])', {'passed': 0, 'failed': 0, 'skipped': 0})],
       'async function runTests(tests) {\n  const focus = tests.some(t => t.only);\n  const result = { passed: 0, failed: 0, skipped: 0 };\n  for (const t of tests) {\n    if (t.skip || (focus && !t.only)) {\n      result.skipped++;\n      continue;\n    }\n    try {\n      await t.fn();\n      result.passed++;\n    } catch {\n      result.failed++;\n    }\n  }\n  return result;\n}',
       hint='Check for <code>only</code> first. Use <code>await t.fn()</code> inside <code>try</code> so async failures are caught too.', why='The <code>await</code> matters: without it, the async failure in the second test would escape and count as a pass.'),
    ex('shard', 'x', 'Split tests into shards', '<p>Write <code>shard(files, spec)</code> where <code>spec</code> is like <code>"2/3"</code>. Sort the files by name, then give them out in turn: file 1 to shard 1, file 2 to shard 2, and so on, starting again after the last shard. Return the files of the requested shard, sorted.</p>',
       'function shard(files, spec) {\n  \n}\n',
       [('shard(["c.test.js", "a.test.js", "d.test.js", "b.test.js", "e.test.js"], "1/2")', ['a.test.js', 'c.test.js', 'e.test.js']),
        ('shard(["c.test.js", "a.test.js", "d.test.js", "b.test.js", "e.test.js"], "2/2")', ['b.test.js', 'd.test.js']),
        ('shard(["x.test.js"], "3/3")', [])],
       'function shard(files, spec) {\n  const [index, total] = spec.split("/").map(Number);\n  return files.toSorted().filter((_, i) => i % total === index - 1);\n}',
       hint='After sorting, file number <code>i</code> (from 0) goes to shard <code>i % total + 1</code>.', why='Sorting first makes every machine agree on the split, so no file runs twice and none is missed.'),
]

T = {
    'slug': 'js-unit-testing', 'title': 'Unit Testing: node:test, Jest, Vitest and Mocha', 'short': 'Unit testing', 'emoji': '🧪', 'module': MODULE, 'minutes': 25,
    'lead': 'Write, run and organise unit tests with the four most used JavaScript runners. Mocks, spies and fake timers, many ways to run a suite (filters, tags, shards, reporters, coverage, CI), unit tests for web UI code with jsdom and Testing Library, and for API code with supertest and nock.',
    'desc': 'Unit tests with node:test, Jest, Vitest and Mocha, mocks, spies, stubs, fake timers, filters, tags, shards, JUnit reports, coverage, CI, jsdom, Testing Library, supertest and nock.',
    'summary': 'The test pyramid and Arrange Act Assert, node:test with mocks and a fake clock, Jest matchers, test.each, module mocks, spies and fake timers, Vitest and Mocha with Chai and Sinon, seven ways to run a node:test suite and five with Jest, a CI matrix with shards, UI component tests with jsdom, Testing Library and user-event, API route tests with supertest, outgoing HTTP faked with nock, and a bug turned into a regression test.',
    'keywords': ['unit testing', 'node:test', 'Jest', 'Vitest', 'Mocha', 'Chai', 'Sinon', 'mock', 'spy', 'stub', 'fake timers', 'test.each', 'filter', 'tags', 'shard', 'coverage', 'JUnit', 'CI', 'jsdom', 'Testing Library', 'supertest', 'nock', 'TDD', 'regression test'],
    'qa_intro': 'Every example on this page ran with the real runner when the page was built. You will see the same test written for web code and for API code, and the same suite run in many different ways.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
