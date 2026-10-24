# Chapter 12: HTTP, fetch, URLs, auth, a Node.js and Express server, the Node.js core modules, and a mock API for tests.
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg

MODULE = ('⏳', 'Async and the platform', 'js-platform', 'Promises and the event loop, the browser DOM, and HTTP from both sides: everything a UI or API test waits for.')

PORT = [(r'127\.0\.0\.1:\d+', '127.0.0.1:41234'), (r'localhost:\d+', 'localhost:41234'), (r'port \d+', 'port 41234'),
        (r'[Dd]ate: .*', 'Date: Tue, 20 Oct 2026 09:00:00 GMT'), (r"'date' => '[^']*'", "'date' => 'Mon, 20 Oct 2026 09:00:00 GMT'"), (r'"date":"[^"]*"', '"date":"Mon, 20 Oct 2026 09:00:00 GMT"')]

CODES = {
    'raw': run('''
import http from "node:http";
import net from "node:net";

// A tiny server, so we can see a real request and response
const server = http.createServer((req, res) => {
  const body = JSON.stringify({ id: 7, name: "Gel pen" });
  res.writeHead(201, { "Content-Type": "application/json", "Content-Length": body.length, "X-Request-Id": "abc-123" });
  res.end(body);
});
await new Promise(r => server.listen(0, "127.0.0.1", r));
const { port } = server.address();

// Send a request by hand over a raw socket and print the exact text that comes back
const socket = net.connect(port, "127.0.0.1");
socket.write(
  "POST /api/products HTTP/1.1\\r\\n" +
  `Host: 127.0.0.1:${port}\\r\\n` +
  "Content-Type: application/json\\r\\n" +
  "Content-Length: 18\\r\\n" +
  "Connection: close\\r\\n\\r\\n" +
  '{"name":"Gel pen"}'
);
let text = "";
for await (const chunk of socket) text += chunk;
console.log(text.replaceAll("\\r\\n", "\\n"));
server.close();
''', 'What a request and a response really look like', play=False, replace=PORT),
    'fetch': run('''
import http from "node:http";

// A small fake API to talk to
const products = [{ id: 1, name: "Gel pen", price: 20 }];
const server = http.createServer(async (req, res) => {
  const send = (status, body) => {
    res.writeHead(status, { "Content-Type": "application/json" });
    res.end(JSON.stringify(body));
  };
  if (req.method === "GET" && req.url === "/api/products") return send(200, products);
  if (req.method === "POST" && req.url === "/api/products") {
    let raw = "";
    for await (const chunk of req) raw += chunk;
    const item = { id: products.length + 1, ...JSON.parse(raw) };
    products.push(item);
    return send(201, item);
  }
  send(404, { error: "Not found" });
});
await new Promise(r => server.listen(0, r));
const base = `http://localhost:${server.address().port}`;

// GET and read JSON
const res = await fetch(`${base}/api/products`);
console.log(res.status, res.ok, res.headers.get("content-type"));
console.log(await res.json());

// POST with a JSON body
const created = await fetch(`${base}/api/products`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "Coffee mug", price: 199 }),
});
console.log(created.status, await created.json());

// fetch does NOT reject on 404 or 500. Only network failures reject.
const missing = await fetch(`${base}/api/nothing`);
console.log(missing.status, missing.ok, await missing.json());

server.close();

// Only a missing response rejects, for example when nothing listens on the port
const gone = http.createServer();
await new Promise(r => gone.listen(0, r));
const deadUrl = `http://localhost:${gone.address().port}/`;
await new Promise(r => gone.close(r));
try {
  await fetch(deadUrl);
} catch (e) {
  console.log("rejected:", e.name, e.message, e.cause?.code);
}
''', 'fetch: GET, POST and errors', play=False, replace=PORT),
    'url': run('''
const url = new URL("https://shop.example:8443/api/products?q=gel+pen&page=2#reviews");
console.log(url.protocol, url.hostname, url.port, url.pathname);
console.log(url.searchParams.get("q"), url.searchParams.get("page"), url.hash);

const search = new URL("/api/search", "https://shop.example");
search.searchParams.set("q", "pens & pencils");
search.searchParams.append("tag", "office");
search.searchParams.append("tag", "school");
console.log(search.href);
console.log(search.searchParams.getAll("tag"));

console.log(encodeURIComponent("a/b c&d"), decodeURIComponent("a%2Fb%20c%26d"));
console.log(URL.canParse("not a url"), URL.parse("https://x.example/a")?.pathname);
''', 'Building and reading URLs'),
    'auth': run('''
import http from "node:http";

const USERS = { "asha@shop.example": { password: "s3cret", role: "customer" }, "admin@shop.example": { password: "adm1n", role: "admin" } };
const tokens = new Map();

const server = http.createServer(async (req, res) => {
  const send = (status, body) => { res.writeHead(status, { "Content-Type": "application/json" }); res.end(JSON.stringify(body)); };
  if (req.url === "/login" && req.method === "POST") {
    let raw = ""; for await (const c of req) raw += c;
    const { email, password } = JSON.parse(raw);
    if (USERS[email]?.password !== password) return send(401, { error: "Invalid credentials" });
    const token = "tok_" + tokens.size;
    tokens.set(token, { email, role: USERS[email].role });
    return send(200, { token });
  }
  const user = tokens.get(req.headers.authorization?.replace(/^Bearer /, ""));
  if (!user) return send(401, { error: "Log in first" });                 // who are you?
  if (req.url === "/admin/reports" && user.role !== "admin") return send(403, { error: "Admins only" });  // not allowed
  send(200, { ok: true, user: user.email });
});
await new Promise(r => server.listen(0, r));
const base = `http://localhost:${server.address().port}`;

async function login(email, password) {
  const res = await fetch(`${base}/login`, { method: "POST", body: JSON.stringify({ email, password }) });
  return (await res.json()).token;
}
const get = (path, token) => fetch(base + path, { headers: token ? { Authorization: `Bearer ${token}` } : {} }).then(r => r.status);

const customer = await login("asha@shop.example", "s3cret");
const admin = await login("admin@shop.example", "adm1n");
console.log("wrong password:", await fetch(`${base}/login`, { method: "POST", body: '{"email":"asha@shop.example","password":"x"}' }).then(r => r.status));
console.log("no token:      ", await get("/orders"));
console.log("customer:      ", await get("/orders", customer), await get("/admin/reports", customer));
console.log("admin:         ", await get("/orders", admin), await get("/admin/reports", admin));
server.close();
''', 'Logging in and sending a Bearer token', play=False),
    'express': run('''
import express from "express";

const app = express();
app.use(express.json());                         // parse JSON bodies

const db = new Map([[1, { id: 1, name: "Gel pen", price: 20 }]]);
let nextId = 2;

app.get("/api/products", (req, res) => {
  const max = Number(req.query.maxPrice ?? Infinity);
  res.json([...db.values()].filter(p => p.price <= max));
});
app.get("/api/products/:id", (req, res) => {
  const p = db.get(Number(req.params.id));
  p ? res.json(p) : res.status(404).json({ error: "Product not found" });
});
app.post("/api/products", (req, res) => {
  const { name, price } = req.body ?? {};
  if (!name || !(price > 0)) return res.status(400).json({ error: "name and a positive price are required" });
  const p = { id: nextId++, name, price };
  db.set(p.id, p);
  res.status(201).location(`/api/products/${p.id}`).json(p);
});
app.delete("/api/products/:id", (req, res) => {
  db.delete(Number(req.params.id)) ? res.status(204).end() : res.status(404).json({ error: "Product not found" });
});

const server = app.listen(0);
await new Promise(r => server.once("listening", r));
const base = `http://localhost:${server.address().port}/api/products`;
const call = async (method, path = "", body) => {
  const res = await fetch(base + path, { method, headers: { "Content-Type": "application/json" }, body: body && JSON.stringify(body) });
  const text = await res.text();
  console.log(method.padEnd(6), ("/api/products" + path).padEnd(28), res.status, text);
};

await call("GET");
await call("POST", "", { name: "Coffee mug", price: 199 });
await call("POST", "", { name: "Free thing", price: 0 });
await call("GET", "?maxPrice=100");
await call("GET", "/2");
await call("DELETE", "/2");
await call("GET", "/2");
server.close();
''', 'A REST API with Express', play=False),
    'node-core': run('''
import { readFile, writeFile, mkdir, readdir } from "node:fs/promises";
import path from "node:path";
import os from "node:os";

// Test data in a CSV file
await writeFile("users.csv", "email,role,active\\nasha@shop.example,admin,true\\nravi@shop.example,customer,false\\n");

const [header, ...lines] = (await readFile("users.csv", "utf8")).trim().split("\\n");
const keys = header.split(",");
const users = lines.map(l => Object.fromEntries(l.split(",").map((v, i) => [keys[i], v])));
console.log(users);

// Write a JSON report into a folder, creating it if needed
const outDir = path.join("reports", "2026-10-20");
await mkdir(outDir, { recursive: true });
const file = path.join(outDir, "summary.json");
await writeFile(file, JSON.stringify({ total: users.length, active: users.filter(u => u.active === "true").length }, null, 2));
console.log(file, "->", await readFile(file, "utf8"));
console.log(await readdir("reports", { recursive: true }));

console.log(path.extname(file), path.basename(file, ".json"), typeof os.cpus().length);
console.log(process.argv.length >= 2, process.platform.length > 0);
''', 'Files, folders and paths in Node.js', play=False),
    'child': run('''
import { execFile } from "node:child_process";
import { promisify } from "node:util";
const run = promisify(execFile);

// Run another program and read its output, like a CI script would
const { stdout } = await run(process.execPath, ["-e", "console.log(JSON.stringify({ node: process.versions.node.split('.')[0] }))"]);
console.log("child said:", JSON.parse(stdout));

try {
  await run(process.execPath, ["-e", "console.error('2 tests failed'); process.exit(1)"]);
} catch (e) {
  console.log("exit code:", e.code, "| stderr:", e.stderr.trim());
}
''', 'Running other programs', play=False),
    'scenario': run('''
import express from "express";

// A mock API that UI tests can start in a second, with data each test controls
export function createMockApi() {
  const app = express();
  app.use(express.json());
  let state = { products: [], failNext: null, delayMs: 0 };

  app.use(async (req, res, next) => {                       // slow network, on demand
    if (state.delayMs) await new Promise(r => setTimeout(r, state.delayMs));
    next();
  });
  app.post("/__test/reset", (req, res) => { state = { products: [], failNext: null, delayMs: 0, ...req.body }; res.sendStatus(204); });
  app.post("/__test/fail-next", (req, res) => { state.failNext = req.body.status; res.sendStatus(204); });
  app.get("/health", (req, res) => res.json({ status: "up" }));
  app.get("/api/products", (req, res) => {
    if (state.failNext) { const s = state.failNext; state.failNext = null; return res.status(s).json({ error: "Injected failure" }); }
    res.json(state.products);
  });
  return app;
}

const server = createMockApi().listen(0);
await new Promise(r => server.once("listening", r));
const base = `http://localhost:${server.address().port}`;
const post = (p, body) => fetch(base + p, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
const show = async label => { const r = await fetch(`${base}/api/products`); console.log(label.padEnd(24), r.status, await r.text()); };

console.log("health:", await (await fetch(`${base}/health`)).json());
await show("empty catalogue:");
await post("/__test/reset", { products: [{ id: 1, name: "Gel pen" }] });
await show("one product:");
await post("/__test/fail-next", { status: 503 });
await show("server error injected:");
await show("next call recovers:");

await post("/__test/reset", { delayMs: 300 });
const t = performance.now();
await show("slow network:");
console.log("took about", Math.round((performance.now() - t) / 100) * 100, "ms");
server.close();
''', 'A controllable mock API for UI tests', play=False),
}

PARTS = [
    part('http', '📨', 'How HTTP works', '''
<p>Browsers, apps and test tools talk to servers with <b>HTTP</b>. The client sends a <b>request</b>: a method, a path, headers and sometimes a body. The server sends back a <b>response</b>: a status code, headers and usually a body. Both are plain text you can read.</p>
[[raw]]
<div class="tw"><table class="jt"><tr><th>Method</th><th>Meaning</th><th>Safe to repeat</th></tr>
<tr><td>GET</td><td>read</td><td>yes</td></tr>
<tr><td>POST</td><td>create, or run an action</td><td>no</td></tr>
<tr><td>PUT</td><td>replace completely</td><td>yes</td></tr>
<tr><td>PATCH</td><td>change some fields</td><td>usually not</td></tr>
<tr><td>DELETE</td><td>remove</td><td>yes</td></tr>
</table></div>
<div class="tw"><table class="jt"><tr><th>Status</th><th>Group</th><th>Ones you see every day</th></tr>
<tr><td>1xx</td><td>information</td><td>101 Switching Protocols (WebSockets)</td></tr>
<tr><td>2xx</td><td>success</td><td>200 OK, 201 Created, 204 No Content</td></tr>
<tr><td>3xx</td><td>redirect</td><td>301 Moved Permanently, 302 Found, 304 Not Modified</td></tr>
<tr><td>4xx</td><td>the client got it wrong</td><td>400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict, 422 Unprocessable, 429 Too Many Requests</td></tr>
<tr><td>5xx</td><td>the server failed</td><td>500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout</td></tr>
</table></div>
''', qa=True, qa_why='Every API test checks a method, a status code, headers and a body.',
        kw=['HTTP', 'request', 'response', 'method', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'status code', 'headers', 'body', 'idempotent', '200', '201', '404', '500']),
    part('fetch', '📡', 'fetch and URLs', '''
<p><code>fetch(url, options)</code> sends a request and returns a promise for the response. It is built into browsers and Node.js. Read the body once with <code>res.json()</code>, <code>res.text()</code> or <code>res.blob()</code>.</p>
[[fetch]]
<div class="warn"><code>fetch</code> only rejects when there is no response at all: a refused connection, a DNS error or an abort. A 404 or 500 still fulfils, so always check <code>res.ok</code> or <code>res.status</code>.</div>
<p>Build URLs with the <code>URL</code> class instead of joining strings. It encodes spaces and symbols correctly, which hand built URLs often get wrong.</p>
[[url]]
''', qa=['Playwright', 'Jest', 'Cypress'], qa_why='API tests send requests and read responses with fetch or a wrapper around it, such as Playwright request or Cypress cy.request.',
        kw=['fetch', 'Response', 'res.ok', 'res.status', 'res.json', 'headers', 'POST body', 'Content-Type', 'URL', 'URLSearchParams', 'encodeURIComponent', 'query string']),
    part('auth', '🔑', 'Authentication: 401 against 403', '''
<p>Most APIs need you to prove who you are. A common pattern: log in once, receive a <b>token</b>, then send it on every request in the <code>Authorization: Bearer ...</code> header. Browsers usually keep the session in a cookie instead.</p>
[[auth]]
<div class="vs"><div><b>401 Unauthorized</b>The server does not know who you are: no token, a wrong one or an expired one. Log in again.</div><div><b>403 Forbidden</b>The server knows exactly who you are, and you are not allowed to do this. Logging in again will not help.</div></div>
<div class="qa-box">Every protected endpoint deserves at least four tests: no token (401), a broken or expired token (401), a valid token without permission (403) and a valid token with permission (2xx). Checking that a customer cannot read another customer's order by changing an id is one of the most valuable security tests you can write.</div>
''', qa=True, qa_why='Authorisation bugs are among the most serious and the easiest to test at the API level.',
        kw=['authentication', 'authorization', 'token', 'Bearer', 'Authorization header', '401', '403', 'JWT', 'session', 'roles', 'access control']),
    part('server', '🖥️', 'Writing a server with Express', '''
<p>On the server side, Node.js answers requests. <b>Express</b> is the most used library for it: you declare <b>routes</b> (a method plus a path) and a handler that receives the request and builds the response. <b>Middleware</b> runs before the routes, for example to parse JSON or check a token.</p>
[[express]]
<div class="dev-box">Return the right status code and a helpful error body. Clients and tests rely on 201 with a <code>Location</code> header for created items, 204 with no body for deletes, 400 for bad input and 404 for missing items.</div>
<div class="qa-box">Knowing how routes and status codes are written makes API bugs easier to explain: "POST with price 0 returns 400, as it should, but PUT with price 0 returns 200 and saves it" points straight at the missing check.</div>
''', qa=['supertest'], qa_why='API test suites start a server like this one, and {{ch:js-api-testing}} tests this exact app with supertest.',
        kw=['Express', 'server', 'route', 'middleware', 'req.params', 'req.query', 'req.body', 'res.status', 'res.json', 'REST', 'CRUD', '201', '204', '400']),
    part('node', '🧰', 'Node.js core modules', '''
<p>Node.js comes with modules for files, paths, processes and more. Test suites use them to read test data, write reports and run other tools.</p>
[[node-core]]
[[child]]
<div class="tw"><table class="jt"><tr><th>Module</th><th>Used for</th></tr>
<tr><td><code>node:fs/promises</code></td><td>read and write files and folders</td></tr>
<tr><td><code>node:path</code></td><td>join and split file paths the same way on Windows, macOS and Linux</td></tr>
<tr><td><code>node:child_process</code></td><td>run other programs</td></tr>
<tr><td><code>node:crypto</code></td><td>random ids (<code>randomUUID</code>) and hashes</td></tr>
<tr><td><code>node:test</code>, <code>node:assert</code></td><td>the built in test runner ({{ch:js-unit-testing}})</td></tr>
</table></div>
''', qa=True, qa_why='Data driven tests read CSV and JSON files, and custom reports are written with fs and path.',
        kw=['fs', 'fs/promises', 'readFile', 'writeFile', 'mkdir', 'path', 'path.join', 'os', 'process.argv', 'child_process', 'execFile', 'CSV', 'test data']),
    part('scenario', '🎬', 'Real world scenario: a mock API for UI tests', '''
<div class="scenario"><b>The situation</b>The real backend is shared, slow and its data changes all the time, so UI tests fail for reasons that have nothing to do with the UI. You need an API that each test can reset, fill with data, slow down and make fail on purpose.</div>
[[scenario]]
<p>The <code>/__test</code> routes exist only in the mock. A test resets the state, sets up exactly the products it needs and can inject a 503 to check that the page shows a friendly error and a retry button. A delay shows whether loading spinners appear.</p>
<div class="tip">Playwright can do the same without a server by intercepting requests with <code>page.route()</code>, and Cypress with <code>cy.intercept()</code>. A mock server is still useful when mobile apps or several services need the same fake.</div>
''', qa=['Playwright', 'Cypress'], kw=['mock API', 'mock server', 'test double', 'fault injection', 'reset state', 'health check', 'page.route', 'cy.intercept', 'Express']),
]

INFO = {'title': 'A request goes out, a response comes back', 'panels': [
    panel([['e', '📨'], ['t', 'POST /api/products', {'b': 1}]], 'Request', 'A method, a path, headers and a body.', 'GET reads, POST creates, PUT and PATCH change, DELETE removes.'),
    panel([['e', '🔢'], ['t', '201 Created', {'b': 1}]], 'Status', 'Three digits that say how it went.', '2xx good, 4xx your mistake, 5xx the server failed.'),
    panel([['e', '🔑'], ['t', 'Authorization: Bearer …', {'b': 1, 'size': 11}]], 'Auth', 'Prove who you are on every call.', '401: who are you. 403: not allowed.'),
    panel([['e', '🖥️'], ['t', 'app.get("/api/…")', {'b': 1}]], 'Server', 'Routes turn requests into responses.', 'Mock servers give tests full control.')],
    'remember': 'Check the status, the headers and the body. fetch does not throw on a 404.'}

REAL = [
    ['📱', 'One API, many clients', 'The same REST API serves the website, the Android app and the iPhone app, so one API test suite protects all three.'],
    ['🔐', 'A broken access check', 'An API test changed the order id in /orders/1042 to another customer\'s order and got 200. The bug was fixed before release.'],
    ['🧪', 'A mock payment provider', 'The checkout tests point at a small Express server that pretends to be the bank, including declined cards and timeouts.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers HTTP, fetch, URLs, logging in with tokens, an Express server, the Node core modules and a mock API for tests.',
        'यह अध्याय HTTP, fetch, URLs, tokens से login, Express server, Node core modules और tests के लिए mock API सिखाता है।',
        'ಈ ಅಧ್ಯಾಯ HTTP, fetch, URLs, tokens ಮೂಲಕ login, Express server, Node core modules ಮತ್ತು tests ಗಾಗಿ mock API ಕಲಿಸುತ್ತದೆ.',
        'ଏହି ଅଧ୍ୟାୟ HTTP, fetch, URLs, tokens ରେ login, Express server, Node core modules ଓ tests ପାଇଁ mock API ଶିଖାଏ।',
        'يتناول هذا الفصل HTTP وfetch والروابط وتسجيل الدخول بالرموز وخادم Express ووحدات Node الأساسية وواجهة وهمية للاختبارات.',
        'Dieses Kapitel behandelt HTTP, fetch, URLs, Login mit Tokens, einen Express-Server, Node-Kernmodule und eine Mock-API für Tests.'),
    say('http', 'HTTP', 'A request has a method, a path, headers and a body. A response has a status code, headers and a body. The first digit of the status tells you the group.',
        'Request में method, path, headers और body होते हैं। Response में status code, headers और body। Status का पहला अंक group बताता है।',
        'Request ನಲ್ಲಿ method, path, headers ಮತ್ತು body. Response ನಲ್ಲಿ status code, headers ಮತ್ತು body. Status ನ ಮೊದಲ ಅಂಕಿ group ಹೇಳುತ್ತದೆ.',
        'Request ରେ method, path, headers ଓ body। Response ରେ status code, headers ଓ body। Status ର ପ୍ରଥମ ଅଙ୍କ group କହେ।',
        'للطلب طريقة ومسار وترويسات وجسم. وللاستجابة رمز حالة وترويسات وجسم. يخبرك الرقم الأول من الحالة بالمجموعة.',
        'Eine Anfrage hat Methode, Pfad, Header und Body. Eine Antwort hat Statuscode, Header und Body. Die erste Ziffer nennt die Gruppe.'),
    say('fetch', 'fetch', 'fetch returns a promise for the response. It does not reject on 404 or 500, so always check res ok. Build URLs with the URL class.',
        'fetch response का promise लौटाता है। यह 404 या 500 पर reject नहीं करता, इसलिए हमेशा res.ok जांचें।',
        'fetch response ನ promise ಕೊಡುತ್ತದೆ. 404 ಅಥವಾ 500 ಗೆ reject ಆಗುವುದಿಲ್ಲ, ಆದ್ದರಿಂದ ಯಾವಾಗಲೂ res.ok ನೋಡಿ.',
        'fetch response ର promise ଫେରାଏ। 404 କିମ୍ବା 500 ରେ reject କରେ ନାହିଁ, ତେଣୁ ସର୍ବଦା res.ok ଯାଞ୍ଚ କରନ୍ତୁ।',
        'تعيد fetch وعدًا بالاستجابة. لا ترفض عند 404 أو 500، لذا افحص res.ok دائمًا. وابن الروابط بصنف URL.',
        'fetch liefert ein Promise für die Antwort. Bei 404 oder 500 wird nicht abgelehnt, prüfe also immer res.ok.'),
    say('auth', 'Auth', 'Send the token in the Authorization header. 401 means the server does not know you. 403 means it knows you and says no.',
        'Token को Authorization header में भेजें। 401 का मतलब server आपको नहीं जानता। 403 का मतलब वह जानता है और मना करता है।',
        'Token ಅನ್ನು Authorization header ನಲ್ಲಿ ಕಳುಹಿಸಿ. 401 ಎಂದರೆ server ನಿಮ್ಮನ್ನು ಅರಿಯದು. 403 ಎಂದರೆ ಅರಿತು ನಿರಾಕರಿಸುತ್ತದೆ.',
        'Token କୁ Authorization header ରେ ପଠାନ୍ତୁ। 401 ମାନେ server ଆପଣଙ୍କୁ ଜାଣେ ନାହିଁ। 403 ମାନେ ଜାଣେ ଏବଂ ମନା କରେ।',
        'أرسل الرمز في ترويسة Authorization. يعني 401 أن الخادم لا يعرفك، ويعني 403 أنه يعرفك ويرفض.',
        'Sende das Token im Authorization-Header. 401 heißt, der Server kennt dich nicht. 403 heißt, er kennt dich und sagt nein.'),
    say('server', 'Express', 'Express maps a method and a path to a handler. Middleware runs first. Good APIs return precise status codes and clear error bodies.',
        'Express method और path को handler से जोड़ता है। Middleware पहले चलता है। अच्छी APIs सही status codes और साफ error देती हैं।',
        'Express method ಮತ್ತು path ಅನ್ನು handler ಗೆ ಜೋಡಿಸುತ್ತದೆ. Middleware ಮೊದಲು ಓಡುತ್ತದೆ. ಒಳ್ಳೆಯ APIs ಸರಿಯಾದ status codes ಕೊಡುತ್ತವೆ.',
        'Express method ଓ path କୁ handler ସହ ଯୋଡ଼େ। Middleware ପ୍ରଥମେ ଚାଲେ। ଭଲ APIs ଠିକ୍ status codes ଦିଅନ୍ତି।',
        'يربط Express الطريقة والمسار بمعالج. تعمل الوسائط أولًا. وتعيد الواجهات الجيدة رموز حالة دقيقة ورسائل خطأ واضحة.',
        'Express ordnet Methode und Pfad einem Handler zu. Middleware läuft zuerst. Gute APIs liefern genaue Statuscodes und klare Fehler.'),
    say('node', 'Node core', 'fs reads and writes files, path joins paths safely, and child process runs other programs. Tests use them for data and reports.',
        'fs files पढ़ता और लिखता है, path paths सुरक्षित जोड़ता है, और child_process दूसरे programs चलाता है।',
        'fs files ಓದಿ ಬರೆಯುತ್ತದೆ, path paths ಸುರಕ್ಷಿತವಾಗಿ ಜೋಡಿಸುತ್ತದೆ, child_process ಬೇರೆ programs ಓಡಿಸುತ್ತದೆ.',
        'fs files ପଢ଼େ ଓ ଲେଖେ, path paths ସୁରକ୍ଷିତ ଭାବେ ଯୋଡ଼େ, ଏବଂ child_process ଅନ୍ୟ programs ଚଲାଏ।',
        'تقرأ fs الملفات وتكتبها، وتجمع path المسارات بأمان، وتشغل child_process برامج أخرى.',
        'fs liest und schreibt Dateien, path verbindet Pfade sicher, child_process startet andere Programme.'),
    say('scenario', 'Scenario', 'A mock API lets each test reset data, slow the network down and inject failures, so UI tests stop failing for backend reasons.',
        'Mock API हर test को data reset करने, network धीमा करने और failures डालने देता है।',
        'Mock API ಪ್ರತಿ test ಗೆ data reset, network ನಿಧಾನ ಮತ್ತು failures ಸೇರಿಸಲು ಅವಕಾಶ ಕೊಡುತ್ತದೆ.',
        'Mock API ପ୍ରତ୍ୟେକ test କୁ data reset, network ଧୀର ଓ failures ଯୋଡ଼ିବାକୁ ଦିଏ।',
        'تتيح الواجهة الوهمية لكل اختبار إعادة البيانات وإبطاء الشبكة وحقن الأعطال، فتتوقف اختبارات الواجهة عن الفشل لأسباب خلفية.',
        'Eine Mock-API lässt jeden Test Daten zurücksetzen, das Netz bremsen und Fehler einspielen.'),
    say('practice', 'Hands-on', 'Practise grouping status codes, building URLs, reading a Link header and matching routes with parameters.',
        'Status codes को group करना, URLs बनाना, Link header पढ़ना और parameters वाले routes match करने का अभ्यास करें।',
        'Status codes group, URLs ರಚನೆ, Link header ಓದುವುದು ಮತ್ತು parameters ಇರುವ routes match ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Status codes group, URLs ତିଆରି, Link header ପଢ଼ିବା ଓ parameters ଥିବା routes match ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على تصنيف رموز الحالة وبناء الروابط وقراءة ترويسة Link ومطابقة المسارات ذات المعاملات.',
        'Übe Statuscodes gruppieren, URLs bauen, einen Link-Header lesen und Routen mit Parametern abgleichen.'),
]

QUIZ = [
    quiz('e', 'Which status code means a new item was created?', ['201', '200', '204', '301'], 0, 'Created.', '201 Created, usually with a Location header pointing at the new item.'),
    quiz('e', 'Which method should only read data?', ['GET', 'POST', 'DELETE', 'PATCH'], 0, 'Safe and repeatable.', 'GET must not change anything on the server.'),
    quiz('e', 'What group is status 503 in?', ['Server error', 'Client error', 'Success', 'Redirect'], 0, 'First digit 5.', '5xx means the server failed. 503 says it is unavailable right now.'),
    quiz('m', 'fetch gets a 404 response. What happens?', ['The promise fulfils with res.ok false', 'The promise rejects', 'It retries', 'It throws a TypeError'], 0, 'fetch only rejects without a response.', 'Any HTTP response fulfils. Check res.ok or res.status yourself.'),
    quiz('m', 'A logged in customer calls an admin only endpoint. Which status is right?', ['403', '401', '404', '500'], 0, 'The server knows who it is.', '403 Forbidden: authenticated, but not allowed.'),
    quiz('m', 'Which builds a correctly encoded query string for q = "pens & pencils"?', ['url.searchParams.set("q", "pens & pencils")', '"?q=" + "pens & pencils"', 'url.query = "pens & pencils"', 'JSON.stringify'], 0, 'Let the URL class encode.', 'searchParams encodes the & and spaces, which plain joining would break.'),
    quiz('h', 'Which status should DELETE return when it succeeds with nothing to send back?', ['204 No Content', '200 with an empty object', '201', '202'], 0, 'No body.', '204 says it worked and there is no body to read.'),
    quiz('h', 'What does express.json() middleware do?', ['Parses JSON request bodies into req.body', 'Sends JSON responses', 'Validates JSON Schema', 'Logs requests'], 0, 'It runs before the routes.', 'Without it, req.body would be undefined for JSON posts.'),
    quiz('h', 'Why join paths with path.join instead of "+"?', ['It uses the right separator and removes doubled slashes on every system', 'It is faster', 'It checks the file exists', 'It encodes spaces'], 0, 'Windows uses backslashes.', 'path.join builds correct paths on Windows, macOS and Linux.'),
    quiz('x', 'Which test is most likely to find an access control bug?', ['Request another user\'s order id with your own token', 'Request your own order twice', 'Send a GET without a body', 'Check the Content-Type header'], 0, 'Change the id, keep the token.', 'This is the classic insecure direct object reference check.'),
    quiz('x', 'Which method is not idempotent, so repeating it can create duplicates?', ['POST', 'PUT', 'DELETE', 'GET'], 0, 'Think of a double click on Pay.', 'Two identical POSTs can create two orders. That is why payment APIs use idempotency keys.'),
    quiz('x', 'In the mock API, why are the /__test routes useful?', ['Each test can set the exact data and failures it needs', 'They make the API faster', 'They replace HTTPS', 'Browsers need them'], 0, 'Control.', 'Tests become independent of shared, changing backend data.'),
]

CALC = [
    calc('e', 'A response has status 404. What is the first digit that tells you its group?', '4', 'Look at the first digit.', ['4xx is a client error.']),
    calc('e', 'An API allows 100 requests per minute. How many requests per second is that on average? Give one decimal.', '1.7', 'Divide by 60.', ['<span class="eq">100 ÷ 60 ≈ 1.67</span>', 'Rounded to one decimal: 1.7.'], alt=['1.67']),
    calc('m', 'A protected endpoint gets 4 auth tests per role, and there are 3 roles. How many tests?', '12', 'Multiply.', ['<span class="eq">4 × 3 = 12</span>']),
    calc('m', 'An endpoint takes 120 ms. A test makes 25 calls one after another. How many seconds is that?', '3', 'Total ms, then divide by 1000.', ['<span class="eq">25 × 120 = 3000</span> ms', '<span class="eq">3000 ÷ 1000 = 3</span> s']),
    calc('h', 'Content-Length for the body {"name":"Gel pen"} is how many bytes?', '18', 'Count every character.', ['{"name":"Gel pen"} has 18 characters, all of them one byte.']),
    calc('h', 'The products list has 230 items, 25 per page. How many pages?', '10', 'Round up.', ['<span class="eq">230 ÷ 25 = 9.2</span>', 'The last page holds 5 items, so 10 pages.']),
    calc('x', 'An API returns 429 with Retry-After: 30. A test retries 3 times, waiting as told. At least how many seconds pass?', '90', 'Three waits.', ['<span class="eq">3 × 30 = 90</span>']),
    calc('x', 'Out of 400 API calls in a run, 6 return 5xx. What percentage is that?', '1.5', 'Part over total, times 100.', ['<span class="eq">6 ÷ 400 × 100 = 1.5</span>']),
]

EX = [
    ex('status', 'e', 'Group a status code', '<p>Write <code>statusGroup(code)</code> that returns <code>"info"</code>, <code>"success"</code>, <code>"redirect"</code>, <code>"client error"</code> or <code>"server error"</code> for codes from 100 to 599, and <code>"unknown"</code> for anything else.</p>',
       'function statusGroup(code) {\n  \n}\n',
       [('statusGroup(201)', 'success'), ('statusGroup(404)', 'client error'), ('statusGroup(503)', 'server error'), ('statusGroup(302)', 'redirect'), ('statusGroup(101)', 'info'), ('statusGroup(700)', 'unknown')],
       'function statusGroup(code) {\n  const groups = ["info", "success", "redirect", "client error", "server error"];\n  const first = Math.floor(code / 100);\n  return groups[first - 1] ?? "unknown";\n}',
       hint='<code>Math.floor(code / 100)</code> gives the first digit.', why='Grouping by the first digit is how API dashboards count errors.'),
    ex('build-url', 'm', 'Build a request URL', '<p>Write <code>buildUrl(base, path, query)</code> using the <code>URL</code> class. Skip query values that are <code>null</code> or <code>undefined</code>. Arrays become repeated keys.</p>',
       'function buildUrl(base, path, query = {}) {\n  \n}\n',
       [('buildUrl("https://shop.example", "/api/search", { q: "pens & pencils", page: 2, sort: null })', 'https://shop.example/api/search?q=pens+%26+pencils&page=2'),
        ('buildUrl("https://shop.example", "/api/items", { tag: ["a", "b"] })', 'https://shop.example/api/items?tag=a&tag=b'),
        ('buildUrl("https://shop.example/v2/", "orders")', 'https://shop.example/v2/orders')],
       'function buildUrl(base, path, query = {}) {\n  const url = new URL(path, base);\n  for (const [key, value] of Object.entries(query)) {\n    if (value == null) continue;\n    for (const v of [value].flat()) url.searchParams.append(key, v);\n  }\n  return url.href;\n}',
       hint='<code>new URL(path, base)</code>, then <code>searchParams.append</code> for each value.', why='Note the last test: a relative path is resolved against the base folder, the same rule as links in HTML.'),
    ex('link', 'h', 'Read a Link header', '<p>Paginated APIs often send <code>Link: &lt;url&gt;; rel="next", &lt;url&gt;; rel="last"</code>. Write <code>parseLink(header)</code> that returns an object from each rel to its URL. An empty header gives <code>{}</code>.</p>',
       'function parseLink(header) {\n  \n}\n',
       [('parseLink(\'<https://api.example/items?page=2>; rel="next", <https://api.example/items?page=9>; rel="last"\')', {'next': 'https://api.example/items?page=2', 'last': 'https://api.example/items?page=9'}),
        ('parseLink("")', {})],
       'function parseLink(header) {\n  const out = {};\n  for (const m of header.matchAll(/<([^>]+)>;\\s*rel="([^"]+)"/g)) {\n    out[m[2]] = m[1];\n  }\n  return out;\n}',
       hint='A regular expression with two groups and <code>matchAll</code>.', why='The GitHub API paginates this way, and a test that walks every page follows <code>next</code> until it is missing.'),
    ex('route', 'x', 'Match a route with parameters', '<p>Write <code>matchRoute(pattern, path)</code>. Patterns look like <code>"/users/:id/orders/:orderId"</code>. Return an object of the parameters when the path matches, or <code>null</code> when it does not. Both must have the same number of segments.</p>',
       'function matchRoute(pattern, path) {\n  \n}\n',
       [('matchRoute("/users/:id/orders/:orderId", "/users/7/orders/1042")', {'id': '7', 'orderId': '1042'}), ('matchRoute("/users/:id", "/products/7")', None),
        ('matchRoute("/users/:id", "/users/7/extra")', None), ('matchRoute("/health", "/health")', {})],
       'function matchRoute(pattern, path) {\n  const a = pattern.split("/"), b = path.split("/");\n  if (a.length !== b.length) return null;\n  const params = {};\n  for (let i = 0; i < a.length; i++) {\n    if (a[i].startsWith(":")) params[a[i].slice(1)] = b[i];\n    else if (a[i] !== b[i]) return null;\n  }\n  return params;\n}',
       hint='Split both on <code>/</code> and compare piece by piece.', why='This is what Express does for <code>req.params</code>, and what Playwright and Cypress do when you intercept <code>/api/users/*</code>.'),
]

T = {
    'slug': 'js-http-node', 'title': 'HTTP, fetch and Node.js Servers', 'short': 'HTTP and Node.js', 'emoji': '📡', 'module': MODULE, 'minutes': 18,
    'lead': 'What a request and a response look like, fetch and URLs, logging in with tokens and the difference between 401 and 403, writing a REST API with Express, the Node.js core modules, and a mock API that UI tests can control.',
    'desc': 'HTTP methods and status codes, fetch, URL and URLSearchParams, Bearer tokens, 401 against 403, Express routes and middleware, fs, path, child_process and a mock API server.',
    'summary': 'A raw HTTP exchange, methods and status codes, fetch with GET and POST and why it does not reject on 404, building URLs with the URL class, token login and access checks, an Express REST API with proper status codes, reading CSV test data and writing reports, running other programs, and a mock API with reset, fault injection and delays.',
    'keywords': ['HTTP', 'status code', 'fetch', 'URL', 'URLSearchParams', 'Bearer token', '401', '403', 'Express', 'REST', 'middleware', 'fs', 'path', 'child_process', 'mock server', 'fault injection'],
    'qa_intro': 'API testing is HTTP. Methods, status codes, headers, auth and a server you control are the foundations for {{ch:js-api-testing}}.',
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
