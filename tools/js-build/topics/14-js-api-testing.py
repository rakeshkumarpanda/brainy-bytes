# Chapter 14: automated API testing in JavaScript: a live server, CRUD flows, schema checks, negative and data driven tests,
# auth, Playwright's request fixture, response times, and a full order flow.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('🧪', 'Testing with JavaScript', 'js-testing', 'Unit tests, API tests and browser automation with node:test, Jest, Vitest, Mocha, supertest, Playwright, Selenium and Cypress.')

NT = [(r'duration_ms [\d.]+', 'duration_ms 245.1'), (r' \(\d+(\.\d+)?ms\)', '')]
JEST = [(r'Time:\s+[\d.]+ m?s.*', 'Time:        0.92 s'), (r' \(\d+ ms\)', ''), (r'Ran all test suites.*', 'Ran all test suites.')]
PW = [(r' \(\d+(\.\d+)?m?s\)', ''), (r'\(([\d.]+)m?s\)$', '(1.2s)')]

# A small shop API used by every example on this page.
SHOP_API = '''
import express from "express";
import { randomUUID } from "node:crypto";

export function createShopApi() {
  const app = express();
  app.use(express.json());
  const users = new Map([["asha@shop.example", { id: 1, email: "asha@shop.example", password: "s3cret", role: "customer" }]]);
  const sessions = new Map();
  const products = new Map([
    [1, { id: 1, name: "Gel pen", price: 20, stock: 100 }],
    [2, { id: 2, name: "Coffee mug", price: 199, stock: 3 }],
  ]);
  const orders = new Map();
  let nextProduct = 3, nextOrder = 1001;

  const auth = (req, res, next) => {
    const user = sessions.get(req.get("authorization")?.replace(/^Bearer /, ""));
    if (!user) return res.status(401).json({ error: "Log in first" });
    req.user = user;
    next();
  };

  app.post("/api/login", (req, res) => {
    const user = users.get(req.body?.email);
    if (!user || user.password !== req.body.password) return res.status(401).json({ error: "Invalid credentials" });
    const token = randomUUID();
    sessions.set(token, user);
    res.json({ token, user: { id: user.id, email: user.email } });
  });

  app.get("/api/products", (req, res) => {
    let list = [...products.values()];
    if (req.query.q) list = list.filter(p => p.name.toLowerCase().includes(String(req.query.q).toLowerCase()));
    res.set("Cache-Control", "max-age=60").json({ items: list, total: list.length });
  });
  app.get("/api/products/:id", (req, res) => {
    const p = products.get(Number(req.params.id));
    p ? res.json(p) : res.status(404).json({ error: "Product not found" });
  });
  app.post("/api/products", (req, res) => {
    const { name, price, stock = 0 } = req.body ?? {};
    const problems = [];
    if (typeof name !== "string" || !name.trim()) problems.push("name is required");
    if (typeof price !== "number" || !(price > 0)) problems.push("price must be a positive number");
    if (!Number.isInteger(stock) || stock < 0) problems.push("stock must be a whole number, 0 or more");
    if (problems.length) return res.status(400).json({ error: "Validation failed", problems });
    const p = { id: nextProduct++, name: name.trim(), price, stock };
    products.set(p.id, p);
    res.status(201).location(`/api/products/${p.id}`).json(p);
  });
  app.patch("/api/products/:id", (req, res) => {
    const p = products.get(Number(req.params.id));
    if (!p) return res.status(404).json({ error: "Product not found" });
    if ("price" in req.body && !(req.body.price > 0)) return res.status(400).json({ error: "Validation failed", problems: ["price must be a positive number"] });
    Object.assign(p, req.body, { id: p.id });
    res.json(p);
  });
  app.delete("/api/products/:id", (req, res) => {
    products.delete(Number(req.params.id)) ? res.sendStatus(204) : res.status(404).json({ error: "Product not found" });
  });

  app.post("/api/orders", auth, (req, res) => {
    const lines = req.body?.items ?? [];
    for (const { productId, qty } of lines) {
      const p = products.get(productId);
      if (!p) return res.status(400).json({ error: `Unknown product ${productId}` });
      if (qty > p.stock) return res.status(409).json({ error: `Only ${p.stock} left of ${p.name}` });
    }
    for (const { productId, qty } of lines) products.get(productId).stock -= qty;
    const total = lines.reduce((s, l) => s + products.get(l.productId).price * l.qty, 0);
    const order = { id: nextOrder++, userId: req.user.id, items: lines, total, status: "placed" };
    orders.set(order.id, order);
    res.status(201).json(order);
  });
  app.get("/api/orders/:id", auth, (req, res) => {
    const o = orders.get(Number(req.params.id));
    if (!o) return res.status(404).json({ error: "Order not found" });
    if (o.userId !== req.user.id) return res.status(403).json({ error: "Not your order" });
    res.json(o);
  });
  return app;
}
'''

SERVER = '''
import { createShopApi } from "./shop-api.js";
const port = Number(process.env.PORT ?? 3000);
createShopApi().listen(port, () => console.log(`shop api on ${port}`));
'''

CODES = {
    'live': test({
        'package.json': pkg('api-live', 'module', {'test': 'node --test --test-reporter=spec'}),
        'src/shop-api.js': SHOP_API,
        'test/products.test.js': '''
import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import { createShopApi } from "../src/shop-api.js";

let server, base;
before(async () => {
  server = createShopApi().listen(0);              // port 0: any free port, so parallel runs never clash
  await new Promise(r => server.once("listening", r));
  base = `http://127.0.0.1:${server.address().port}/api`;
});
after(() => server.close());

const json = (method, body) => ({ method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

describe("products CRUD", () => {
  let created;

  it("POST creates a product (201, Location, body)", async () => {
    const res = await fetch(`${base}/products`, json("POST", { name: "  Desk lamp ", price: 1299, stock: 5 }));
    assert.equal(res.status, 201);
    created = await res.json();
    assert.equal(res.headers.get("location"), `/api/products/${created.id}`);
    assert.deepEqual(created, { id: created.id, name: "Desk lamp", price: 1299, stock: 5 });
  });

  it("GET returns what was created", async () => {
    const res = await fetch(`${base}/products/${created.id}`);
    assert.equal(res.status, 200);
    assert.match(res.headers.get("content-type"), /application\\/json/);
    assert.equal((await res.json()).name, "Desk lamp");
  });

  it("PATCH changes one field and keeps the rest", async () => {
    const res = await fetch(`${base}/products/${created.id}`, json("PATCH", { price: 999 }));
    assert.deepEqual(await res.json(), { ...created, price: 999 });
  });

  it("search finds it, case insensitive", async () => {
    const body = await (await fetch(`${base}/products?q=LAMP`)).json();
    assert.equal(body.total, 1);
    assert.equal(body.items[0].id, created.id);
  });

  it("DELETE removes it, then GET is 404", async () => {
    assert.equal((await fetch(`${base}/products/${created.id}`, { method: "DELETE" })).status, 204);
    const res = await fetch(`${base}/products/${created.id}`);
    assert.equal(res.status, 404);
    assert.deepEqual(await res.json(), { error: "Product not found" });
  });
});
''',
    }, 'npm test', 'A CRUD flow against a running server', show=['test/products.test.js'], replace=NT),
    'schema': run('''
import Ajv from "ajv";

const productSchema = {
  type: "object",
  required: ["id", "name", "price", "stock"],
  additionalProperties: false,
  properties: {
    id: { type: "integer", minimum: 1 },
    name: { type: "string", minLength: 1, maxLength: 120 },
    price: { type: "number", exclusiveMinimum: 0 },
    stock: { type: "integer", minimum: 0 },
  },
};
const listSchema = {
  type: "object",
  required: ["items", "total"],
  properties: { items: { type: "array", items: productSchema }, total: { type: "integer" } },
};

const ajv = new Ajv({ allErrors: true });
const validateList = ajv.compile(listSchema);

const today = { items: [{ id: 1, name: "Gel pen", price: 20, stock: 100 }], total: 1 };
console.log("today:", validateList(today));

// A backend change: price became a string, stock was renamed, and a field was added
const afterRelease = { items: [{ id: 1, name: "Gel pen", price: "20.00", qty: 100, internalCost: 7 }], total: 1 };
console.log("after release:", validateList(afterRelease));
for (const e of validateList.errors) console.log(" ", e.instancePath || "(root)", e.message, e.params.additionalProperty ?? e.params.missingProperty ?? "");
''', 'Validate a response with JSON Schema', play=False),
    'negative': test({
        'package.json': pkg('api-negative', 'module', {'test': 'vitest run'}),
        'src/shop-api.js': SHOP_API,
        'test/validation.test.js': '''
import { describe, it, expect } from "vitest";
import request from "supertest";
import { createShopApi } from "../src/shop-api.js";

const app = createShopApi();

describe("POST /api/products rejects bad input with 400", () => {
  it.each([
    ["no body", undefined, "name is required"],
    ["empty name", { name: " ", price: 10 }, "name is required"],
    ["price as text", { name: "Pen", price: "10" }, "price must be a positive number"],
    ["zero price", { name: "Pen", price: 0 }, "price must be a positive number"],
    ["negative stock", { name: "Pen", price: 10, stock: -1 }, "stock must be a whole number, 0 or more"],
    ["decimal stock", { name: "Pen", price: 10, stock: 1.5 }, "stock must be a whole number, 0 or more"],
  ])("%s", async (_, body, problem) => {
    const res = await request(app).post("/api/products").send(body);
    expect(res.status).toBe(400);
    expect(res.body.problems).toContain(problem);
  });

  it("lists every problem at once", async () => {
    const res = await request(app).post("/api/products").send({ price: -1, stock: "a" });
    expect(res.body.problems).toHaveLength(3);
  });
});

describe("boundaries and odd input", () => {
  it("accepts the smallest positive price", async () => {
    await request(app).post("/api/products").send({ name: "Sticker", price: 0.01 }).expect(201);
  });

  it("ignores an id sent by the client", async () => {
    const res = await request(app).post("/api/products").send({ id: 1, name: "Clip", price: 2 }).expect(201);
    expect(res.body.id).not.toBe(1);
  });

  it("handles broken JSON with a 400, not a crash", async () => {
    await request(app).post("/api/products").set("Content-Type", "application/json").send("{ name: ").expect(400);
  });

  it("returns 404 JSON for an id that is not a number", async () => {
    await request(app).get("/api/products/abc").expect(404).expect("Content-Type", /json/);
  });
});
''',
    }, 'npx vitest run --reporter=verbose', 'Negative and boundary tests, data driven', show=['test/validation.test.js'],
        replace=[(r'Start at\s+[\d:]+', 'Start at  09:00:00'), (r'Duration\s+[\d.]+m?s.*', 'Duration  540ms'), (r'(✓|×) (.*?) \d+ms', r'\1 \2')]),
    'auth': test({
        'package.json': pkg('api-auth', 'module', {'test': 'NODE_OPTIONS=--experimental-vm-modules jest'}),
        'jest.config.js': 'export default { transform: {} };   // run ES modules as they are, no Babel',
        'src/shop-api.js': SHOP_API,
        'test/orders.test.js': '''
import { describe, test, expect, beforeAll } from "@jest/globals";
import request from "supertest";
import { createShopApi } from "../src/shop-api.js";

const app = createShopApi();
let token;

beforeAll(async () => {
  const res = await request(app).post("/api/login").send({ email: "asha@shop.example", password: "s3cret" }).expect(200);
  token = res.body.token;
});

describe("authentication", () => {
  test("wrong password is 401", () =>
    request(app).post("/api/login").send({ email: "asha@shop.example", password: "nope" }).expect(401));

  test("no token is 401", () => request(app).post("/api/orders").send({ items: [] }).expect(401));

  test("a made up token is 401", () =>
    request(app).post("/api/orders").set("Authorization", "Bearer not-a-real-token").send({ items: [] }).expect(401));
});

describe("orders", () => {
  test("placing an order lowers the stock", async () => {
    const order = await request(app).post("/api/orders").auth(token, { type: "bearer" })
      .send({ items: [{ productId: 2, qty: 2 }] }).expect(201);
    expect(order.body).toMatchObject({ total: 398, status: "placed" });
    const mug = await request(app).get("/api/products/2");
    expect(mug.body.stock).toBe(1);
  });

  test("ordering more than the stock is 409", async () => {
    const res = await request(app).post("/api/orders").auth(token, { type: "bearer" })
      .send({ items: [{ productId: 2, qty: 5 }] }).expect(409);
    expect(res.body.error).toBe("Only 1 left of Coffee mug");
  });
});
''',
    }, 'NODE_OPTIONS=--experimental-vm-modules npx jest --verbose', 'Auth, state changes and conflicts with Jest and supertest',
        show=['jest.config.js', 'test/orders.test.js'], replace=JEST + [(r'\(node:\d+\) ExperimentalWarning.*\n(\(Use .*\n)?', '')]),
    'playwright-api': test({
        'package.json': pkg('pw-api', 'module', {'test': 'playwright test'}),
        'src/shop-api.js': SHOP_API,
        'src/server.js': SERVER,
        'playwright.config.js': '''
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "tests",
  reporter: "list",
  workers: 1,
  use: { baseURL: "http://127.0.0.1:3917", extraHTTPHeaders: { Accept: "application/json" } },
  webServer: {                                   // Playwright starts the API and waits for it
    command: "node src/server.js",
    url: "http://127.0.0.1:3917/api/products",
    env: { PORT: "3917" },
    reuseExistingServer: !process.env.CI,
  },
});
''',
        'tests/shop.api.spec.js': '''
import { test, expect } from "@playwright/test";

test.describe("shop API", () => {
  let token;

  test.beforeAll(async ({ request }) => {
    const res = await request.post("/api/login", { data: { email: "asha@shop.example", password: "s3cret" } });
    expect(res.ok()).toBeTruthy();
    token = (await res.json()).token;
  });

  test("lists products with a cache header", async ({ request }) => {
    const res = await request.get("/api/products");
    expect(res.status()).toBe(200);
    expect(res.headers()["cache-control"]).toBe("max-age=60");
    const body = await res.json();
    expect(body.total).toBe(body.items.length);
    expect(body.items).toContainEqual(expect.objectContaining({ name: "Gel pen" }));
  });

  test("a customer cannot read another customer's order", async ({ request }) => {
    const res = await request.get("/api/orders/9999", { headers: { Authorization: `Bearer ${token}` } });
    expect(res.status()).toBe(404);
  });

  test("place an order and read it back", async ({ request }) => {
    const headers = { Authorization: `Bearer ${token}` };
    const created = await request.post("/api/orders", { headers, data: { items: [{ productId: 1, qty: 3 }] } });
    expect(created.status()).toBe(201);
    const order = await created.json();
    const again = await request.get(`/api/orders/${order.id}`, { headers });
    await expect(again).toBeOK();
    expect(await again.json()).toEqual(order);
  });
});
''',
    }, 'npx playwright test', 'API tests with Playwright, which starts the server itself', show=['playwright.config.js', 'tests/shop.api.spec.js'], replace=PW),
    'timing': run('''
import { createShopApi } from "./shop-api.mjs";

const server = createShopApi().listen(0);
await new Promise(r => server.once("listening", r));
const url = `http://127.0.0.1:${server.address().port}/api/products?q=pen`;

async function timed() {
  const t = performance.now();
  const res = await fetch(url);
  await res.arrayBuffer();
  return { ms: performance.now() - t, status: res.status };
}

// 200 requests, 20 at a time
const results = [];
for (let batch = 0; batch < 10; batch++) {
  results.push(...await Promise.all(Array.from({ length: 20 }, timed)));
}
const times = results.map(r => r.ms).sort((a, b) => a - b);
const pct = p => times[Math.ceil((p / 100) * times.length) - 1];

console.log("requests:", results.length, "| errors:", results.filter(r => r.status !== 200).length);
console.log("p50 under 50 ms:", pct(50) < 50, "| p95 under 200 ms:", pct(95) < 200);
console.log("slowest is the max:", Math.max(...times) === times.at(-1));
server.close();
''', 'Response times and percentiles', play=False, extra={'shop-api.mjs': SHOP_API}),
    'other-tools': show('''
// Cypress: cy.request in a spec file
it("creates a product", () => {
  cy.request("POST", "/api/products", { name: "Pen", price: 10 }).then(res => {
    expect(res.status).to.eq(201);
    expect(res.body).to.have.property("id");
  });
});

// Postman collections from the command line, for example in CI
// npx newman run shop.postman_collection.json -e staging.postman_environment.json --reporters cli,junit

// k6 load tests are also written in JavaScript
// import http from "k6/http";
// export const options = { vus: 50, duration: "1m", thresholds: { http_req_duration: ["p(95)<300"] } };
// export default () => http.get("https://staging.shop.example/api/products");
''', 'The same ideas in Cypress, Newman and k6', note='Reference'),
    'scenario': test({
        'package.json': pkg('order-flow', 'module', {'test': 'node --test --test-reporter=spec'}),
        'src/shop-api.js': SHOP_API,
        'test/order-flow.test.js': '''
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createShopApi } from "../src/shop-api.js";

let server, api;
before(async () => {
  server = createShopApi().listen(0);
  await new Promise(r => server.once("listening", r));
  const base = `http://127.0.0.1:${server.address().port}/api`;
  // A tiny client: JSON in, JSON out, the token added when we have one
  let token;
  api = async (method, path, body) => {
    const res = await fetch(base + path, {
      method,
      headers: { "Content-Type": "application/json", ...(token && { Authorization: `Bearer ${token}` }) },
      body: body && JSON.stringify(body),
    });
    const data = res.status === 204 ? null : await res.json();
    if (path === "/login" && res.ok) token = data.token;
    return { status: res.status, data };
  };
});
after(() => server.close());

test("a customer buys the last two mugs", async t => {
  let productId, orderId;

  await t.test("admin adds stock: a new mug with 2 left", async () => {
    const r = await api("POST", "/products", { name: "Blue mug", price: 249, stock: 2 });
    assert.equal(r.status, 201);
    productId = r.data.id;
  });

  await t.test("customer logs in", async () => {
    assert.equal((await api("POST", "/login", { email: "asha@shop.example", password: "s3cret" })).status, 200);
  });

  await t.test("orders both mugs", async () => {
    const r = await api("POST", "/orders", { items: [{ productId, qty: 2 }] });
    assert.equal(r.status, 201);
    assert.equal(r.data.total, 498);
    orderId = r.data.id;
  });

  await t.test("stock is now 0", async () => {
    assert.equal((await api("GET", `/products/${productId}`)).data.stock, 0);
  });

  await t.test("a second order for the same mug is refused with 409", async () => {
    const r = await api("POST", "/orders", { items: [{ productId, qty: 1 }] });
    assert.equal(r.status, 409);
    assert.equal(r.data.error, "Only 0 left of Blue mug");
  });

  await t.test("the order can be read back", async () => {
    const r = await api("GET", `/orders/${orderId}`);
    assert.deepEqual([r.status, r.data.status, r.data.items], [200, "placed", [{ productId, qty: 2 }]]);
  });

  await t.test("clean up the test product", async () => {
    assert.equal((await api("DELETE", `/products/${productId}`)).status, 204);
  });
});
''',
    }, 'npm test', 'An end to end API flow with steps', show=['test/order-flow.test.js'], replace=NT),
}

PARTS = [
    part('what', '🗺️', 'What an API test checks', '''
<p>An <b>API test</b> sends real HTTP requests to a running service and checks the answers. It sits in the middle of the test pyramid: much faster and steadier than a browser test, and it checks the real routes, validation, database and auth together, which unit tests cannot.</p>
<div class="tw"><table class="jt"><tr><th>Check</th><th>Example</th></tr>
<tr><td>Status code</td><td>201 after create, 404 for a missing id, 400 for bad input</td></tr>
<tr><td>Headers</td><td><code>Content-Type: application/json</code>, <code>Location</code>, <code>Cache-Control</code></td></tr>
<tr><td>Body values</td><td>the created product has the name that was sent, trimmed</td></tr>
<tr><td>Body shape</td><td>every product has an integer id and a positive price (JSON Schema)</td></tr>
<tr><td>Side effects</td><td>the stock really went down, the deleted item is really gone</td></tr>
<tr><td>Negative cases</td><td>missing fields, wrong types, boundaries, broken JSON</td></tr>
<tr><td>Security</td><td>401 without a token, 403 or 404 for someone else's data</td></tr>
<tr><td>Speed</td><td>95% of requests under 200 ms</td></tr>
</table></div>
<div class="tip">This chapter tests one small shop API, written with Express in <code>shop-api.js</code>, with four different tools. It is the same app as in chapter 12, with login and orders added.</div>
''', qa=True, qa_why='API tests give the most coverage per minute of any automated test.',
        kw=['API testing', 'what to test', 'status code', 'headers', 'body', 'schema', 'side effects', 'negative testing', 'security', 'response time', 'test pyramid']),
    part('live', '🔁', 'Testing a running server: a CRUD flow', '''
<p>The most direct API test starts the server, sends requests with <code>fetch</code> and checks each answer. Listening on port <code>0</code> lets the system pick a free port, so many suites can run side by side.</p>
[[live]]
<p>The tests run in order and share <code>created</code>, so together they cover the whole life of one product: Create, Read, Update and Delete, also called <b>CRUD</b>. Checking the GET after the DELETE proves the delete really happened, which the 204 alone does not.</p>
<div class="warn">Tests that depend on each other stop at the first failure and cannot run alone. Use this style for one flow on purpose. For everything else, each test creates its own data.</div>
''', qa=['node:test', 'fetch'], qa_why='A CRUD flow against a real server is the first suite most API testers write.',
        kw=['CRUD', 'running server', 'fetch', 'port 0', 'before', 'after', 'POST', 'GET', 'PATCH', 'DELETE', 'Location header', 'node:test']),
    part('schema', '📐', 'Checking the shape with JSON Schema', '''
<p>Checking every field by hand gets long, and it misses fields you did not think of. A <b>JSON Schema</b> describes the allowed shape once: required fields, types, ranges and whether extra fields are allowed. <b>Ajv</b> checks a response against it in one call and lists every problem.</p>
[[schema]]
<p>This kind of check, the response still matches what clients expect, is a simple <b>contract test</b>. It catches a renamed field or a number turned into a string before the mobile app crashes on it. OpenAPI files already contain these schemas, so many teams generate them instead of writing them by hand.</p>
''', qa=['Ajv', 'Jest', 'Playwright'], qa_why='Schema checks catch breaking API changes that value checks miss.',
        kw=['JSON Schema', 'Ajv', 'schema validation', 'contract test', 'additionalProperties', 'required', 'OpenAPI', 'breaking change', 'response shape']),
    part('negative', '🚫', 'Negative, boundary and data driven tests', '''
<p>Most API bugs hide in input the developer did not expect. <b>Negative tests</b> send wrong data on purpose and check that it is refused with a clear 400, not saved and not answered with a 500. A table of cases with <code>it.each</code> keeps dozens of them readable.</p>
[[negative]]
<div class="qa-box">Ideas for every field: missing, null, empty, only spaces, wrong type ("10" for 10), zero, negative, decimals where whole numbers are expected, very long text, unicode and emoji, and the exact limits plus one each side. For the whole request: no body, broken JSON, an extra id the client should not control, and the wrong Content-Type.</div>
''', qa=['Vitest', 'supertest'], qa_why='Input validation is where APIs most often fail, and these tests are cheap to write as tables.',
        kw=['negative testing', 'boundary values', 'data driven', 'it.each', 'test.each', 'validation', '400', 'malformed JSON', 'supertest', 'equivalence classes']),
    part('auth', '🔐', 'Authentication, state and conflicts', '''
<p>Real APIs need a login and change data as they go. Log in once in <code>beforeAll</code>, keep the token, and send it with each request. Then check not only the answer but also its effect, such as the stock that went down, and the conflicts that follow, such as ordering more than is left.</p>
[[auth]]
<div class="tip">supertest's <code>.auth(token, { type: "bearer" })</code> sets the Authorization header for you. The same suite can point at a deployed server by passing a URL string instead of the app: <code>request("https://staging.shop.example")</code>.</div>
''', qa=['Jest', 'supertest'], qa_why='Auth checks and state changes are where API bugs are most costly.',
        kw=['authentication', 'Bearer token', 'beforeAll', 'supertest auth', '401', '409 Conflict', 'stock', 'state change', 'side effect', 'Jest ESM']),
    part('playwright', '🎭', 'API testing with Playwright', '''
<p>Playwright is known for browsers, but its <code>request</code> fixture is also a complete API client. It shares the base URL and config with UI tests, and its <b>webServer</b> option starts the app before the tests and stops it afterwards. UI tests often use it to create data through the API before opening the page.</p>
[[playwright-api]]
<p>The second test checks access to another customer's order. This API answers 404 rather than 403, so it does not even admit the order exists, which is a common and good choice.</p>
[[other-tools]]
''', qa=['Playwright', 'Cypress', 'Postman'], qa_why='Most Playwright suites mix API calls into UI tests for setup and checks, and some teams run their whole API suite in it.',
        kw=['Playwright', 'request fixture', 'APIRequestContext', 'webServer', 'baseURL', 'toBeOK', 'cy.request', 'Newman', 'Postman', 'k6']),
    part('performance', '⏱️', 'Response times', '''
<p>A correct answer that takes five seconds is still a bug. Measure each request and look at <b>percentiles</b>, not the average: p95 is the time under which 95% of requests finish. One very slow request barely moves the average but is exactly what a user notices.</p>
[[timing]]
<div class="tw"><table class="jt"><tr><th>Number</th><th>Meaning</th></tr>
<tr><td>p50 (median)</td><td>a typical request</td></tr>
<tr><td>p95, p99</td><td>the slow tail that real users hit every day</td></tr>
<tr><td>error rate</td><td>failed requests divided by all requests</td></tr>
<tr><td>throughput</td><td>requests handled per second</td></tr>
</table></div>
<div class="warn">Times measured on a laptop or a shared CI machine vary a lot. Use generous limits in functional suites to catch big slowdowns, and leave real load testing to tools such as k6 against a production like environment.</div>
''', qa=['k6'], qa_why='Response time checks catch slow endpoints before users do.',
        kw=['response time', 'latency', 'percentile', 'p95', 'p99', 'median', 'throughput', 'error rate', 'load test', 'performance']),
    part('scenario', '🎬', 'Real world scenario: buying the last two mugs', '''
<div class="scenario"><b>The situation</b>Customers complain that sold out items can still be ordered. You must test the whole flow: add a product with two in stock, log in, order both, confirm the stock is 0, confirm a second order is refused, read the order back, and leave no test data behind.</div>
[[scenario]]
<p>Subtests with <code>t.test</code> name each step, so a failure says exactly where the flow broke. The last step deletes the product the test created, so the shared environment stays clean for everyone else.</p>
''', qa=True, kw=['end to end API flow', 'subtests', 't.test', 'stock', 'sold out', '409', 'test data cleanup', 'API client']),
]

INFO = {'title': 'Ask the API, check every part of the answer', 'panels': [
    panel([['e', '📨'], ['t', 'POST /api/products', {'b': 1}]], 'Send', 'A real request to a running service.', 'fetch, supertest or Playwright request.'),
    panel([['e', '🔍'], ['t', '201 + Location + body', {'b': 1}]], 'Check', 'Status, headers, body and shape.', 'JSON Schema checks the shape in one go.'),
    panel([['e', '🚫'], ['t', 'price: "10" → 400', {'b': 1}]], 'Break it', 'Wrong input must be refused clearly.', 'Tables of bad cases find most bugs.'),
    panel([['e', '🧹'], ['t', 'DELETE what you made', {'b': 1}]], 'Clean up', 'Leave the environment as you found it.', 'Other people and tests share it.')],
    'remember': 'Status, headers, body, shape, side effects, the bad cases, and clean up after yourself.'}

REAL = [
    ['📱', 'A mobile release saved', 'A schema check failed when price turned into a string. The Android app would have crashed for every user on the old version.'],
    ['🛍️', 'Overselling', 'An order flow test found that two quick orders could both buy the last item. The team added a database lock and the test now guards it.'],
    ['⚡', 'Fast feedback', 'A team runs 900 API tests in 2 minutes on every pull request and keeps only 40 browser journeys.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter tests one shop API with fetch, supertest, Jest, Vitest and Playwright, from CRUD flows to schemas, bad input, auth and response times.',
        'यह अध्याय एक shop API को fetch, supertest, Jest, Vitest और Playwright से test करता है, CRUD से लेकर schema, गलत input, auth और response time तक।',
        'ಈ ಅಧ್ಯಾಯ ಒಂದು shop API ಅನ್ನು fetch, supertest, Jest, Vitest ಮತ್ತು Playwright ಮೂಲಕ test ಮಾಡುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ ଗୋଟିଏ shop API କୁ fetch, supertest, Jest, Vitest ଓ Playwright ରେ test କରେ।',
        'يختبر هذا الفصل واجهة متجر واحدة باستخدام fetch وsupertest وJest وVitest وPlaywright، من عمليات CRUD إلى المخططات والمدخلات الخاطئة والمصادقة وزمن الاستجابة.',
        'Dieses Kapitel testet eine Shop-API mit fetch, supertest, Jest, Vitest und Playwright, von CRUD über Schemas bis zu Auth und Antwortzeiten.'),
    say('what', 'What to check', 'Check the status, headers, body values, body shape, side effects, bad input, security and speed.',
        'Status, headers, body values, body shape, side effects, गलत input, security और speed जांचें।',
        'Status, headers, body values, body shape, side effects, ತಪ್ಪು input, security ಮತ್ತು speed ಪರಿಶೀಲಿಸಿ.',
        'Status, headers, body values, body shape, side effects, ଭୁଲ input, security ଓ speed ଯାଞ୍ଚ କରନ୍ତୁ।',
        'افحص الحالة والترويسات وقيم الجسم وشكله والآثار الجانبية والمدخلات الخاطئة والأمان والسرعة.',
        'Prüfe Status, Header, Werte, Struktur, Nebenwirkungen, falsche Eingaben, Sicherheit und Tempo.'),
    say('live', 'CRUD flow', 'Start the server on a free port, then create, read, update and delete one product, checking the effect of each step.',
        'Server को खाली port पर शुरू करें, फिर एक product create, read, update और delete करें।',
        'Server ಅನ್ನು ಖಾಲಿ port ನಲ್ಲಿ ಆರಂಭಿಸಿ, ನಂತರ ಒಂದು product create, read, update, delete ಮಾಡಿ.',
        'Server କୁ ଖାଲି port ରେ ଆରମ୍ଭ କରନ୍ତୁ, ତାପରେ ଗୋଟିଏ product create, read, update ଓ delete କରନ୍ତୁ।',
        'شغّل الخادم على منفذ حر، ثم أنشئ منتجًا واقرأه وعدّله واحذفه، مع فحص أثر كل خطوة.',
        'Starte den Server auf einem freien Port, dann ein Produkt anlegen, lesen, ändern und löschen.'),
    say('schema', 'JSON Schema', 'A JSON Schema describes the allowed shape once. Ajv lists every field that breaks it, which catches breaking changes early.',
        'JSON Schema allowed shape को एक बार बताता है। Ajv हर टूटे field को बताता है।',
        'JSON Schema ಅನುಮತಿಸಿದ shape ಅನ್ನು ಒಮ್ಮೆ ವಿವರಿಸುತ್ತದೆ. Ajv ಮುರಿದ ಪ್ರತಿ field ಪಟ್ಟಿ ಮಾಡುತ್ತದೆ.',
        'JSON Schema ଅନୁମତି ପ୍ରାପ୍ତ shape କୁ ଥରେ ବର୍ଣ୍ଣନା କରେ। Ajv ପ୍ରତ୍ୟେକ ଭଙ୍ଗା field ତାଲିକା କରେ।',
        'يصف مخطط JSON الشكل المسموح مرة واحدة. ويعدد Ajv كل حقل يخالفه، فيكشف التغييرات الكاسرة مبكرًا.',
        'Ein JSON Schema beschreibt die erlaubte Struktur einmal. Ajv listet jedes Feld, das sie verletzt.'),
    say('negative', 'Negative tests', 'Send wrong input on purpose and expect a clear 400. A table of cases keeps dozens of them short.',
        'जानबूझकर गलत input भेजें और साफ 400 की उम्मीद करें। Cases की table उन्हें छोटा रखती है।',
        'ಉದ್ದೇಶಪೂರ್ವಕವಾಗಿ ತಪ್ಪು input ಕಳುಹಿಸಿ, ಸ್ಪಷ್ಟ 400 ನಿರೀಕ್ಷಿಸಿ. Cases table ಅವನ್ನು ಚಿಕ್ಕದಾಗಿಡುತ್ತದೆ.',
        'ଜାଣିଶୁଣି ଭୁଲ input ପଠାନ୍ତୁ ଏବଂ ସ୍ପଷ୍ଟ 400 ଆଶା କରନ୍ତୁ। Cases ର table ସେଗୁଡ଼ିକୁ ଛୋଟ ରଖେ।',
        'أرسل مدخلات خاطئة عمدًا وتوقع 400 واضحة. يبقي جدول الحالات العشرات منها قصيرة.',
        'Sende absichtlich falsche Eingaben und erwarte ein klares 400. Eine Tabelle hält Dutzende Fälle kurz.'),
    say('auth', 'Auth and state', 'Log in once, send the token, and check the effect of each change, such as stock going down and a 409 when it runs out.',
        'एक बार login करें, token भेजें, और हर बदलाव का असर जांचें, जैसे stock कम होना और खत्म होने पर 409।',
        'ಒಮ್ಮೆ login ಮಾಡಿ, token ಕಳುಹಿಸಿ, ಪ್ರತಿ ಬದಲಾವಣೆಯ ಪರಿಣಾಮ ಪರಿಶೀಲಿಸಿ.',
        'ଥରେ login କରନ୍ତୁ, token ପଠାନ୍ତୁ, ଏବଂ ପ୍ରତ୍ୟେକ ବଦଳର ପ୍ରଭାବ ଯାଞ୍ଚ କରନ୍ତୁ।',
        'سجّل الدخول مرة وأرسل الرمز، وافحص أثر كل تغيير مثل نقص المخزون و409 عند نفاده.',
        'Einmal einloggen, das Token senden und die Wirkung jeder Änderung prüfen, etwa sinkenden Bestand.'),
    say('playwright', 'Playwright API', 'Playwright request is a full API client, and its web server option starts the app before the tests run.',
        'Playwright request एक पूरा API client है, और web server option tests से पहले app शुरू करता है।',
        'Playwright request ಪೂರ್ಣ API client, web server option tests ಮೊದಲು app ಆರಂಭಿಸುತ್ತದೆ.',
        'Playwright request ଏକ ପୂର୍ଣ୍ଣ API client, ଏବଂ web server option tests ପୂର୍ବରୁ app ଆରମ୍ଭ କରେ।',
        'طلبات Playwright عميل API كامل، وخيار خادم الويب يشغّل التطبيق قبل الاختبارات.',
        'Playwright request ist ein voller API-Client, und webServer startet die App vor den Tests.'),
    say('performance', 'Response times', 'Look at percentiles such as p95, not the average. Use generous limits in functional tests and real load tools for load.',
        'Average नहीं, p95 जैसे percentiles देखें। Functional tests में ढीली limits और load के लिए असली load tools इस्तेमाल करें।',
        'Average ಅಲ್ಲ, p95 ನಂತಹ percentiles ನೋಡಿ. Load ಗೆ ನಿಜವಾದ load tools ಬಳಸಿ.',
        'Average ନୁହେଁ, p95 ପରି percentiles ଦେଖନ୍ତୁ। Load ପାଇଁ ଅସଲ load tools ବ୍ୟବହାର କରନ୍ତୁ।',
        'انظر إلى المئينات مثل p95 لا إلى المتوسط. استخدم حدودًا مرنة في الاختبارات الوظيفية وأدوات حمل حقيقية للحمل.',
        'Achte auf Perzentile wie p95, nicht auf den Durchschnitt. Für Last echte Lastwerkzeuge nutzen.'),
    say('scenario', 'Scenario', 'Walk the whole flow in named steps: add stock, log in, order, check stock, refuse a second order, read back and clean up.',
        'पूरे flow को नाम वाले steps में चलाएं: stock जोड़ें, login, order, stock जांचें, दूसरा order मना, वापस पढ़ें और साफ करें।',
        'ಸಂಪೂರ್ಣ flow ಅನ್ನು ಹೆಸರಿನ steps ನಲ್ಲಿ ನಡೆಸಿ: stock, login, order, ಪರಿಶೀಲನೆ, ನಿರಾಕರಣೆ, clean up.',
        'ସମ୍ପୂର୍ଣ୍ଣ flow କୁ ନାମିତ steps ରେ ଚଲାନ୍ତୁ: stock, login, order, ଯାଞ୍ଚ, ମନା, clean up।',
        'نفذ المسار كاملًا بخطوات مسماة: أضف مخزونًا، سجّل الدخول، اطلب، افحص، ارفض طلبًا ثانيًا، اقرأ ونظّف.',
        'Den ganzen Ablauf in benannten Schritten: Bestand, Login, Bestellung, Prüfung, Ablehnung, Aufräumen.'),
    say('practice', 'Hands-on', 'Practise a status and body check, a tiny schema validator, percentiles and finding fields that changed between two responses.',
        'Status और body check, छोटा schema validator, percentiles और दो responses के बीच बदले fields ढूंढने का अभ्यास करें।',
        'Status ಮತ್ತು body check, ಚಿಕ್ಕ schema validator, percentiles ಮತ್ತು ಬದಲಾದ fields ಹುಡುಕುವುದನ್ನು ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Status ଓ body check, ଛୋଟ schema validator, percentiles ଓ ବଦଳିଥିବା fields ଖୋଜିବା ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على فحص الحالة والجسم ومدقق مخطط صغير والمئينات وإيجاد الحقول التي تغيرت بين استجابتين.',
        'Übe Status- und Body-Prüfung, einen kleinen Schema-Validator, Perzentile und geänderte Felder finden.'),
]

QUIZ = [
    quiz('e', 'After a successful DELETE, which status do you usually expect?', ['204', '200 with the deleted item', '201', '404'], 0, 'Nothing to return.', '204 No Content. Then a GET should be 404.'),
    quiz('e', 'Why listen on port 0 in tests?', ['The system picks a free port, so suites never clash', 'Port 0 is faster', 'It disables the network', 'It is required by Express'], 0, 'Parallel runs.', 'A fixed port fails when another test or app already uses it.'),
    quiz('e', 'Which tool validates a response against a JSON Schema?', ['Ajv', 'nock', 'Prettier', 'jsdom'], 0, 'Another JSON validator.', 'Ajv compiles a schema into a fast validate function.'),
    quiz('m', 'POST with price "10" (a string) should return?', ['400 with a clear message', '201', '500', '200'], 0, 'Wrong type.', 'The API must refuse it clearly rather than save or crash.'),
    quiz('m', 'Why GET after DELETE?', ['To prove the item is really gone', 'To warm the cache', 'Because DELETE has no status', 'To get a new token'], 0, 'Check the side effect.', 'A 204 only says the server claims success. The GET checks it.'),
    quiz('m', 'In Playwright, what does the webServer option do?', ['Starts the app before tests and stops it after', 'Mocks every request', 'Opens a browser', 'Deploys the app'], 0, 'Set up for you.', 'It runs the command and waits for the URL to answer.'),
    quiz('h', 'What does additionalProperties: false catch?', ['New fields that are not in the schema, such as leaked internal data', 'Missing required fields', 'Wrong types', 'Slow responses'], 0, 'Extra keys.', 'It flags anything not listed, for example an internalCost field that should never reach clients.'),
    quiz('h', 'Ordering 5 when 1 is left should return?', ['409 Conflict', '400', '404', '201'], 0, 'The request is valid but clashes with the current state.', '409 says the request conflicts with the state of the resource.'),
    quiz('h', '100 requests: 99 take 20 ms and one takes 3,000 ms. Which number shows the problem best?', ['p99 or the max', 'the average', 'p50', 'the minimum'], 0, 'The tail.', 'The average is about 50 ms and hides it. The slow tail is what p99 and the max reveal.'),
    quiz('x', 'Why might an API answer 404 instead of 403 for someone else\'s order?', ['So it does not reveal that the order exists', 'Because 403 is deprecated', 'Because the order really does not exist', 'It is a bug'], 0, 'Information leaks.', 'Hiding existence stops attackers from guessing valid ids.'),
    quiz('x', 'Which is the best way to make API tests independent?', ['Each test creates and removes its own data', 'Run them in a fixed order', 'Share one product between all tests', 'Never delete anything'], 0, 'No hidden coupling.', 'Own data means a test can run alone, in parallel and in any order.'),
    quiz('x', 'supertest is given a URL string instead of the app. What changes?', ['It sends real HTTP to that deployed server', 'Nothing', 'It mocks the server', 'It starts the app'], 0, 'Same tests, other target.', 'request("https://staging...") runs the suite against a deployed environment.'),
]

CALC = [
    calc('e', 'Two mugs at ₹199 each. What total should the order show?', '398', 'Multiply.', ['<span class="eq">2 × 199 = 398</span>']),
    calc('e', 'Stock is 3 and an order takes 2. What should GET show for stock?', '1', 'Subtract.', ['<span class="eq">3 − 2 = 1</span>']),
    calc('m', 'A field needs tests for missing, null, empty, wrong type and two boundaries each side of one limit. How many cases?', '6', 'Count them.', ['missing, null, empty, wrong type: 4.', 'just below and on the limit: 2.', '<span class="eq">4 + 2 = 6</span>']),
    calc('m', '200 requests, 3 failed. What is the error rate in percent?', '1.5', 'Failed over total.', ['<span class="eq">3 ÷ 200 × 100 = 1.5</span>']),
    calc('h', '20 sorted response times. Which position (from 1) is p95?', '19', 'Ceiling of 0.95 times the count.', ['<span class="eq">⌈0.95 × 20⌉ = ⌈19⌉ = 19</span>']),
    calc('h', '900 API tests of 120 ms each, run with 4 parallel workers. About how many seconds?', '27', 'Total time, then divide by workers.', ['<span class="eq">900 × 0.12 = 108</span> s', '<span class="eq">108 ÷ 4 = 27</span> s']),
    calc('x', 'The schema check after the release found how many errors?', '4', 'Read the output.', ['price is a string, stock is missing.', 'qty and internalCost are extra fields.', 'That is 4.']),
    calc('x', 'An endpoint allows 100 requests per minute per user. A test suite makes 450 calls as one user. At least how many minutes does it need?', '5', 'Round up.', ['<span class="eq">450 ÷ 100 = 4.5</span>', 'You cannot use half a minute window, so 5.']),
]

EX = [
    ex('check', 'e', 'Check a response', '<p>Write <code>checkResponse(res, expected)</code>. <code>res</code> is <code>{ status, headers, body }</code>. <code>expected</code> may have <code>status</code>, <code>contentType</code> (a substring of the content-type header) and <code>body</code> (fields that must be equal). Return a list of problem strings, empty when all is well.</p>',
       'function checkResponse(res, expected) {\n  \n}\n',
       [('checkResponse({ status: 201, headers: { "content-type": "application/json" }, body: { id: 3, name: "Pen" } }, { status: 201, contentType: "json", body: { name: "Pen" } })', []),
        ('checkResponse({ status: 500, headers: { "content-type": "text/html" }, body: {} }, { status: 201, contentType: "json", body: { name: "Pen" } })',
         ['status 500, expected 201', 'content-type text/html, expected json', 'body.name is undefined, expected "Pen"'])],
       'function checkResponse(res, expected) {\n  const problems = [];\n  if (expected.status && res.status !== expected.status) problems.push(`status ${res.status}, expected ${expected.status}`);\n  const type = res.headers["content-type"] ?? "";\n  if (expected.contentType && !type.includes(expected.contentType)) problems.push(`content-type ${type}, expected ${expected.contentType}`);\n  for (const [k, v] of Object.entries(expected.body ?? {})) {\n    if (res.body[k] !== v) problems.push(`body.${k} is ${JSON.stringify(res.body[k])}, expected ${JSON.stringify(v)}`);\n  }\n  return problems;\n}',
       hint='Collect messages in an array instead of stopping at the first problem.', why='Reporting every problem at once saves a fix, rerun, fix cycle when an API changes.'),
    ex('schema-mini', 'm', 'A tiny schema validator', '<p>Write <code>validate(schema, value)</code> for schemas like <code>{ id: "integer", name: "string", price: "number", tags: "array" }</code>. Every key is required. Return a list of errors such as <code>"price should be number"</code> or <code>"name is missing"</code>, in the order of the schema.</p>',
       'function validate(schema, value) {\n  \n}\n',
       [('validate({ id: "integer", name: "string", price: "number" }, { id: 1, name: "Pen", price: 20 })', []),
        ('validate({ id: "integer", name: "string", price: "number", tags: "array" }, { id: 1.5, price: "20", tags: {} })', ['id should be integer', 'name is missing', 'price should be number', 'tags should be array'])],
       'function validate(schema, value) {\n  const errors = [];\n  const is = {\n    integer: v => Number.isInteger(v),\n    number: v => typeof v === "number",\n    string: v => typeof v === "string",\n    array: v => Array.isArray(v),\n  };\n  for (const [key, type] of Object.entries(schema)) {\n    if (!(key in value)) errors.push(`${key} is missing`);\n    else if (!is[type](value[key])) errors.push(`${key} should be ${type}`);\n  }\n  return errors;\n}',
       hint='A small object of type checking functions, one per type name, keeps it short.', why='Ajv does the same thing, with many more keywords and much faster compiled checks.'),
    ex('pct', 'h', 'Percentiles', '<p>Write <code>percentile(times, p)</code> using the nearest rank method: sort a copy of the times, then take the value at position <code>⌈p ÷ 100 × n⌉</code> counted from 1. An empty list gives <code>null</code>.</p>',
       'function percentile(times, p) {\n  \n}\n',
       [('percentile([30, 10, 20, 40, 50], 50)', 30), ('percentile([5, 1, 9, 3, 7, 2, 8, 4, 6, 3000], 95)', 3000), ('percentile([5, 1, 9, 3, 7, 2, 8, 4, 6, 3000], 90)', 9), ('percentile([], 95)', None)],
       'function percentile(times, p) {\n  if (!times.length) return null;\n  const sorted = times.toSorted((a, b) => a - b);\n  return sorted[Math.ceil((p / 100) * sorted.length) - 1];\n}',
       hint='Sort numbers with <code>(a, b) =&gt; a - b</code>, and subtract 1 to turn the rank into an index.', why='Note how p90 is 9 ms but p95 is 3,000 ms: one slow request decides the tail.'),
    ex('diff', 'x', 'What changed in the response?', '<p>Write <code>diffKeys(before, after)</code> comparing two flat objects. Return <code>{ added, removed, typeChanged }</code>, each a sorted list of key names. A key is in <code>typeChanged</code> when it exists in both but <code>typeof</code> differs.</p>',
       'function diffKeys(before, after) {\n  \n}\n',
       [('diffKeys({ id: 1, name: "Pen", price: 20, stock: 100 }, { id: 1, name: "Pen", price: "20.00", qty: 100, internalCost: 7 })', {'added': ['internalCost', 'qty'], 'removed': ['stock'], 'typeChanged': ['price']}),
        ('diffKeys({ a: 1 }, { a: 2 })', {'added': [], 'removed': [], 'typeChanged': []})],
       'function diffKeys(before, after) {\n  const a = Object.keys(before), b = Object.keys(after);\n  return {\n    added: b.filter(k => !(k in before)).sort(),\n    removed: a.filter(k => !(k in after)).sort(),\n    typeChanged: a.filter(k => k in after && typeof before[k] !== typeof after[k]).sort(),\n  };\n}',
       hint='Three filters over the key lists.', why='Comparing a saved response from the last release with today\'s is a quick way to spot breaking changes, the same idea as the schema check.'),
]

T = {
    'slug': 'js-api-testing', 'title': 'Automated API Testing with JavaScript', 'short': 'API testing', 'emoji': '🔌', 'module': MODULE, 'minutes': 22,
    'lead': 'Test one real shop API with four tools: fetch and node:test for a CRUD flow, Ajv for JSON Schema checks, Vitest and supertest for negative and boundary tables, Jest for auth and stock, Playwright request with a web server, response time percentiles, and a full order flow that cleans up after itself.',
    'desc': 'API testing with fetch, node:test, supertest, Jest, Vitest, Playwright request, Ajv JSON Schema, negative and boundary tests, auth, 409 conflicts, response times and cleanup.',
    'summary': 'What an API test checks, a CRUD flow against a running server, JSON Schema validation with Ajv that catches breaking changes, data driven negative and boundary tests, login with tokens and checking side effects and conflicts, Playwright request with webServer, Cypress, Newman and k6 in brief, percentiles for response times, and an order flow written as named subtests.',
    'keywords': ['API testing', 'REST', 'CRUD', 'fetch', 'supertest', 'Playwright request', 'Ajv', 'JSON Schema', 'contract test', 'negative testing', 'boundary', 'auth', '401', '409', 'p95', 'response time', 'cleanup', 'Newman', 'k6'],
    'qa_intro': 'Every test on this page ran against a real Express server when the page was built. Pick the tool your team uses, the ideas are the same in all of them.',
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
