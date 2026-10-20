TRACK = {
    'id': 'js-native', 'lang': 'js', 'tool': 'native',
    'title': 'Native JavaScript with fetch and node:test', 'emoji': '🟨',
    'tagline': 'Zero dependency API tests with the fetch, test runner, assert and mock modules built into Node.js.',
    'intro': 'Modern Node.js ships everything an API test needs. <b>fetch</b> sends HTTP requests, <b>node:test</b> finds and runs tests with hooks, filters, reporters and coverage, <b>node:assert</b> compares values, and <b>mock</b> replaces functions such as fetch itself. Nothing to install except Node. It is the best way to understand what every JavaScript test tool does under the hood.',
    'stack': [
        ('Node.js', '22 LTS or newer', 'fetch, node:test, --env-file'),
        ('fetch', 'built in', 'HTTP client, same as in browsers'),
        ('node:test', 'built in', 'runner, hooks, mocks, reporters'),
        ('node:assert/strict', 'built in', 'assertions'),
        ('dependencies', 'none', 'nothing to npm install'),
    ],
    'sections': [
        {
            'id': 'why', 'title': 'Why go native', 'emoji': '🎯', 'level': 'Basic',
            'blocks': [
                ('p', 'An API test sends a request and checks the response. With Node 22 or newer you can do this with no packages at all, which means no supply chain risk, no version upgrades and instant installs in CI.'),
                ('table', ['Need', 'Built in answer'], [
                    ['Send HTTP requests', '<code>fetch</code>, <code>Request</code>, <code>Response</code>, <code>Headers</code>'],
                    ['Time limits', '<code>AbortSignal.timeout(ms)</code>'],
                    ['Run tests', '<code>node --test</code>, <code>test</code>, <code>describe</code>, <code>it</code>'],
                    ['Setup and cleanup', '<code>before</code>, <code>after</code>, <code>beforeEach</code>, <code>afterEach</code>'],
                    ['Assertions', '<code>node:assert/strict</code>'],
                    ['Mocks', '<code>mock.method</code>, <code>mock.fn</code>, <code>mock.timers</code>'],
                    ['Reports and coverage', '<code>--test-reporter</code>, <code>--experimental-test-coverage</code>'],
                    ['Secrets from a file', '<code>node --env-file=.env</code>'],
                ]),
                ('qa', 'fetch works the same in Node and in the browser console. Testers can try a request in DevTools, then paste the same lines into a test file.'),
            ],
        },
        {
            'id': 'setup', 'title': 'Setup and running tests', 'emoji': '🧰', 'level': 'Basic',
            'blocks': [
                ('code', 'json', 'package.json', '''
{
  "name": "booker-native-api",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "node --test",
    "test:smoke": "node --test --test-name-pattern=smoke",
    "test:ci": "node --test --test-reporter=spec --test-reporter-destination=stdout --test-reporter=junit --test-reporter-destination=results/junit.xml"
  }
}
''', {'save': 'package.json'}),
                ('code', 'bash', 'Terminal', '''
node --version                         # 22 or newer
npm test                               # runs every *.test.js file
node --test tests/crud.test.js         # one file
node --test --watch                    # rerun on save
BASE_URL=http://localhost:3001 npm test
node --env-file=.env --test            # load variables from .env
'''),
                ('code', 'plain', 'Project layout', '''
booker-native-api/
├── package.json
├── src/
│   ├── config.js       BASE_URL and defaults
│   └── client.js       a small wrapper around fetch
└── tests/
    ├── first.test.js
    ├── crud.test.js
    └── ...
'''),
                ('code', 'js', 'src/config.js', '''
export const BASE = process.env.BASE_URL ?? 'https://restful-booker.herokuapp.com';
export const TIMEOUT_MS = Number(process.env.TIMEOUT_MS ?? 10_000);
''', {'save': 'src/config.js'}),
            ],
        },
        {
            'id': 'first-test', 'title': 'Your first test: GET a booking', 'emoji': '👋', 'level': 'Basic',
            'blocks': [
                ('code', 'js', 'tests/first.test.js', '''
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { BASE } from '../src/config.js';

test('smoke: ping says the API is up', async () => {
  const res = await fetch(`${BASE}/ping`, { signal: AbortSignal.timeout(10_000) });
  assert.equal(res.status, 201);              // Restful Booker answers 201 to a health check
});

test('get one booking', async () => {
  const res = await fetch(`${BASE}/booking/1`, {
    headers: { Accept: 'application/json' },
    signal: AbortSignal.timeout(10_000),
  });

  assert.equal(res.status, 200);
  assert.ok(res.ok);
  assert.match(res.headers.get('content-type'), /application\\/json/);

  const body = await res.json();
  assert.equal(typeof body.firstname, 'string');
  assert.deepEqual(Object.keys(body.bookingdates).sort(), ['checkin', 'checkout']);
});
''', {'save': 'tests/first.test.js'}),
                ('ul', [
                    '<code>fetch</code> resolves when the headers arrive. Read the body once with <code>await res.json()</code> or <code>await res.text()</code>.',
                    'fetch does <b>not</b> throw on 404 or 500. Check <code>res.status</code> or <code>res.ok</code> yourself.',
                    'fetch has no default time limit. <code>AbortSignal.timeout(ms)</code> cancels a call that hangs.',
                    '<code>assert/strict</code> uses strict equality, so <code>assert.equal(1, "1")</code> fails as it should.',
                ]),
                ('try', {'method': 'GET', 'path': '/booking/1'}),
            ],
        },
        {
            'id': 'request', 'title': 'Building requests: URL, headers and bodies', 'emoji': '🧱', 'level': 'Basic',
            'blocks': [
                ('code', 'js', 'URL, query params and headers', '''
// Query strings: URL and URLSearchParams handle encoding
const url = new URL('/booking', BASE);
url.searchParams.set('firstname', 'Mary Ann');          // ?firstname=Mary+Ann
await fetch(url);

// Headers
const headers = new Headers({ Accept: 'application/json' });
headers.set('X-Request-Id', crypto.randomUUID());

// JSON body: stringify it and set Content-Type yourself
await fetch(`${BASE}/booking`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
  body: JSON.stringify(booking),
});

// Form fields and file uploads
await fetch(`${BASE}/login`, { method: 'POST', body: new URLSearchParams({ user: 'qa', password: 'x' }) });
const form = new FormData();
form.append('file', new Blob([await readFile('invoice.pdf')], { type: 'application/pdf' }), 'invoice.pdf');
await fetch(`${BASE}/documents`, { method: 'POST', body: form });
'''),
                ('table', ['Body type', 'Content-Type set automatically'], [
                    ['<code>JSON.stringify(obj)</code> (a string)', 'text/plain, so set application/json yourself'],
                    ['<code>URLSearchParams</code>', 'application/x-www-form-urlencoded'],
                    ['<code>FormData</code>', 'multipart/form-data with a boundary'],
                    ['<code>Blob</code> or <code>Buffer</code>', 'the Blob type, or none'],
                ]),
                ('warn', 'Forgetting <code>Content-Type: application/json</code> is the most common fetch mistake. Many servers then ignore the body or answer 400 or 500.'),
            ],
        },
        {
            'id': 'crud', 'title': 'Create, update and delete (CRUD)', 'emoji': '✍️', 'level': 'Basic',
            'blocks': [
                ('code', 'js', 'tests/crud.test.js', '''
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { BASE } from '../src/config.js';

const BASIC = 'Basic ' + btoa('admin:password123');
const JSON_HEADERS = { 'Content-Type': 'application/json', Accept: 'application/json' };

const newBooking = {
  firstname: 'Rakesh',
  lastname: 'Panda',
  totalprice: 250,
  depositpaid: true,
  bookingdates: { checkin: '2026-11-01', checkout: '2026-11-04' },
  additionalneeds: 'Breakfast',
};

describe('booking CRUD', () => {
  let id;

  it('creates', async () => {
    const res = await fetch(`${BASE}/booking`, { method: 'POST', headers: JSON_HEADERS, body: JSON.stringify(newBooking) });
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.ok(body.bookingid > 0);
    assert.deepEqual(body.booking, newBooking);
    id = body.bookingid;
  });

  it('replaces with PUT', async () => {
    const res = await fetch(`${BASE}/booking/${id}`, {
      method: 'PUT',
      headers: { ...JSON_HEADERS, Authorization: BASIC },
      body: JSON.stringify({ ...newBooking, lastname: 'Kumar' }),
    });
    assert.equal((await res.json()).lastname, 'Kumar');
  });

  it('changes one field with PATCH', async () => {
    const res = await fetch(`${BASE}/booking/${id}`, {
      method: 'PATCH',
      headers: { ...JSON_HEADERS, Authorization: BASIC },
      body: JSON.stringify({ additionalneeds: 'Dinner' }),
    });
    const body = await res.json();
    assert.equal(body.additionalneeds, 'Dinner');
    assert.equal(body.lastname, 'Kumar');
  });

  it('deletes, then it is gone', async () => {
    const del = await fetch(`${BASE}/booking/${id}`, { method: 'DELETE', headers: { Authorization: BASIC } });
    assert.equal(del.status, 201);                         // this API answers 201
    const get = await fetch(`${BASE}/booking/${id}`);
    assert.equal(get.status, 404);
    assert.equal(await get.text(), 'Not Found');
  });
});
''', {'save': 'tests/crud.test.js'}),
                ('tip', 'Inside one <code>describe</code>, tests run one after another by default, so the shared <code>id</code> is safe here. Different files run in parallel in separate processes.'),
                ('try', {'method': 'POST', 'path': '/booking', 'body': {'firstname': 'Rakesh', 'lastname': 'Panda', 'totalprice': 250, 'depositpaid': True, 'bookingdates': {'checkin': '2026-11-01', 'checkout': '2026-11-04'}, 'additionalneeds': 'Breakfast'}}),
            ],
        },
        {
            'id': 'assertions', 'title': 'Assertions with node:assert', 'emoji': '🔍', 'level': 'Intermediate',
            'blocks': [
                ('code', 'js', 'The assertions you need', '''
import assert from 'node:assert/strict';

assert.equal(res.status, 200, 'status');                      // ===
assert.notEqual(body.firstname, '');
assert.ok(body.totalprice >= 0, `price was ${body.totalprice}`);
assert.deepEqual(body.bookingdates, { checkin: '2026-11-01', checkout: '2026-11-04' });
assert.partialDeepStrictEqual(body, { firstname: 'Rakesh' });  // Node 22.13 or newer, still experimental
assert.match(body.bookingdates.checkin, /^\\d{4}-\\d{2}-\\d{2}$/);
await assert.rejects(fetch('http://localhost:1'), TypeError);  // connection refused
assert.throws(() => JSON.parse('Not Found'), SyntaxError);
'''),
                ('p', 'For older Node versions, a tiny helper gives the same partial match.'),
                ('code', 'js', 'src/expect-shape.js', '''
// Checks that every key in `shape` exists in `actual`.
// A function in `shape` is used as a test, any other value must match exactly.
export function expectShape(actual, shape, path = '$') {
  for (const [key, want] of Object.entries(shape)) {
    const here = `${path}.${key}`;
    if (!(key in Object(actual))) throw new Error(`${here} is missing`);
    const got = actual[key];
    if (typeof want === 'function') {
      if (!want(got)) throw new Error(`${here} failed ${want.name || 'check'}: ${JSON.stringify(got)}`);
    } else if (want && typeof want === 'object') {
      expectShape(got, want, here);
    } else if (got !== want) {
      throw new Error(`${here} is ${JSON.stringify(got)}, expected ${JSON.stringify(want)}`);
    }
  }
}

export const isString = v => typeof v === 'string';
export const isNonEmptyString = v => typeof v === 'string' && v.length > 0;
export const isNumber = v => typeof v === 'number' && Number.isFinite(v);
export const isBoolean = v => typeof v === 'boolean';
export const isDate = v => /^\\d{4}-\\d{2}-\\d{2}$/.test(v);
''', {'save': 'src/expect-shape.js'}),
                ('code', 'js', 'tests/shape.test.js', '''
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { BASE } from '../src/config.js';
import { expectShape, isNonEmptyString, isNumber, isBoolean, isDate } from '../src/expect-shape.js';

const bookingShape = {
  firstname: isNonEmptyString,
  lastname: isNonEmptyString,
  totalprice: isNumber,
  depositpaid: isBoolean,
  bookingdates: { checkin: isDate, checkout: isDate },
};

test('booking 1 has the right shape', async () => {
  const body = await (await fetch(`${BASE}/booking/1`)).json();
  expectShape(body, bookingShape);
});

test('the shape check catches a renamed field', () => {
  assert.throws(
    () => expectShape({ firstname: 'A', lastname: 'B', totalPrice: 1, depositpaid: true,
      bookingdates: { checkin: '2026-01-01', checkout: '2026-01-02' } }, bookingShape),
    /\\$\\.totalprice is missing/);
});
''', {'save': 'tests/shape.test.js'}),
                ('tip', 'For full JSON Schema support add Ajv, the one package most native suites accept. The Playwright track shows how.'),
            ],
        },
        {
            'id': 'hooks-auth', 'title': 'Hooks, shared login and auth checks', 'emoji': '🔐', 'level': 'Intermediate',
            'blocks': [
                ('p', '<code>before</code> runs once before the tests in its block, <code>beforeEach</code> before every test, and the <code>after</code> versions clean up. Use them to log in once and to create and delete test data.'),
                ('code', 'js', 'tests/auth.test.js', '''
import { describe, it, before, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { BASE } from '../src/config.js';

const JSON_HEADERS = { 'Content-Type': 'application/json', Accept: 'application/json' };
let token;
let booking;

before(async () => {
  const res = await fetch(`${BASE}/auth`, {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify({ username: 'admin', password: 'password123' }),
  });
  ({ token } = await res.json());
});

beforeEach(async () => {
  const res = await fetch(`${BASE}/booking`, {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify({ firstname: `Guest${Date.now()}`, lastname: 'Hook', totalprice: 10, depositpaid: false,
      bookingdates: { checkin: '2026-09-01', checkout: '2026-09-02' } }),
  });
  booking = await res.json();
});

afterEach(async () => {
  await fetch(`${BASE}/booking/${booking.bookingid}`, { method: 'DELETE', headers: { Cookie: `token=${token}` } });
});

describe('protected updates', () => {
  for (const [name, headers] of [
    ['no auth', {}],
    ['made up token', { Cookie: 'token=not-real' }],
    ['wrong password', { Authorization: 'Basic ' + btoa('admin:wrong') }],
  ]) {
    it(`refuses an update with ${name}`, async () => {
      const res = await fetch(`${BASE}/booking/${booking.bookingid}`, {
        method: 'PATCH', headers: { ...JSON_HEADERS, ...headers }, body: JSON.stringify({ firstname: 'Hacker' }),
      });
      assert.equal(res.status, 403);
      const after = await (await fetch(`${BASE}/booking/${booking.bookingid}`)).json();
      assert.notEqual(after.firstname, 'Hacker');
    });
  }

  it('accepts the token cookie', async () => {
    const res = await fetch(`${BASE}/booking/${booking.bookingid}`, {
      method: 'PATCH', headers: { ...JSON_HEADERS, Cookie: `token=${token}` }, body: JSON.stringify({ additionalneeds: 'Spa' }),
    });
    assert.equal(res.status, 200);
    assert.equal((await res.json()).additionalneeds, 'Spa');
  });
});
''', {'save': 'tests/auth.test.js'}),
                ('code', 'js', 'Other auth styles', '''
headers: { Authorization: `Bearer ${process.env.API_TOKEN}` }
headers: { 'x-api-key': process.env.API_KEY }
headers: { Authorization: 'Basic ' + btoa(`${user}:${password}`) }
'''),
                ('warn', 'Node\'s fetch does not keep cookies between calls like a browser does. Send the <code>Cookie</code> header yourself, or read <code>res.headers.getSetCookie()</code> and store the values.'),
            ],
        },
        {
            'id': 'data-driven', 'title': 'Data driven tests', 'emoji': '📊', 'level': 'Intermediate',
            'blocks': [
                ('code', 'js', 'tests/data.test.js', '''
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { BASE } from '../src/config.js';

const cases = [
  { path: '/ping', status: 201 },
  { path: '/booking', status: 200 },
  { path: '/booking/1', status: 200 },
  { path: '/booking/999999', status: 404 },
  { path: '/booking/abc', status: 404 },
];

describe('status per path', { concurrency: true }, () => {
  for (const { path, status } of cases) {
    it(`GET ${path} gives ${status}`, async () => {
      const res = await fetch(`${BASE}${path}`);
      await res.body?.cancel();                 // free the connection, we only need the status
      assert.equal(res.status, status);
    });
  }
});

const valid = { firstname: 'T', lastname: 'U', totalprice: 1, depositpaid: true,
  bookingdates: { checkin: '2026-12-01', checkout: '2026-12-03' } };

describe('required fields', () => {
  for (const field of Object.keys(valid)) {
    it(`missing ${field} is rejected`, async () => {
      const { [field]: _, ...body } = valid;
      const res = await fetch(`${BASE}/booking`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
      });
      await res.body?.cancel();
      assert.notEqual(res.status, 200, 'Restful Booker answers 500 here, a good API answers 400');
    });
  }
});
''', {'save': 'tests/data.test.js'}),
                ('tip', '<code>{ concurrency: true }</code> runs the tests inside that <code>describe</code> at the same time. Use it only for tests that do not share state.'),
            ],
        },
        {
            'id': 'mocking', 'title': 'Mocking fetch and time', 'emoji': '🎭', 'level': 'Advanced',
            'blocks': [
                ('p', 'When you test your own code that calls an API, replace <code>fetch</code> with a mock. The test controls every answer and checks every call, with no network.'),
                ('code', 'js', 'src/client.js', '''
import { BASE, TIMEOUT_MS } from './config.js';

export class BookingClient {
  constructor(base = BASE) {
    this.base = base;
    this.headers = { Accept: 'application/json' };
  }

  async call(method, path, body) {
    const res = await fetch(`${this.base}${path}`, {
      method,
      headers: body ? { ...this.headers, 'Content-Type': 'application/json' } : this.headers,
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
    const type = res.headers.get('content-type') ?? '';
    return { status: res.status, body: type.includes('json') ? await res.json() : await res.text() };
  }

  async login(username = 'admin', password = 'password123') {
    const { body } = await this.call('POST', '/auth', { username, password });
    if (!body.token) throw new Error(`Login failed: ${JSON.stringify(body)}`);
    this.headers = { ...this.headers, Cookie: `token=${body.token}` };
    return this;
  }

  create(b) { return this.call('POST', '/booking', b); }
  get(id) { return this.call('GET', `/booking/${id}`); }
  patch(id, f) { return this.call('PATCH', `/booking/${id}`, f); }
  remove(id) { return this.call('DELETE', `/booking/${id}`); }

  async getWithRetry(id, tries = 3, waitMs = 200) {
    for (let i = 1; ; i++) {
      const res = await this.get(id);
      if (res.status < 500 || i === tries) return res;
      await new Promise(r => setTimeout(r, waitMs * i));
    }
  }
}
''', {'save': 'src/client.js'}),
                ('code', 'js', 'tests/mocking.test.js', '''
import { test, mock, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { BookingClient } from '../src/client.js';

afterEach(() => mock.restoreAll());

const json = (status, body) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

test('login stores the token as a cookie header', async () => {
  const fake = mock.method(globalThis, 'fetch', async () => json(200, { token: 'abc' }));

  const client = await new BookingClient('https://api.test').login();

  assert.equal(fake.mock.callCount(), 1);
  const [url, init] = fake.mock.calls[0].arguments;
  assert.equal(url, 'https://api.test/auth');
  assert.equal(init.method, 'POST');
  assert.deepEqual(JSON.parse(init.body), { username: 'admin', password: 'password123' });
  assert.equal(client.headers.Cookie, 'token=abc');
});

test('login fails loudly on bad credentials', async () => {
  mock.method(globalThis, 'fetch', async () => json(200, { reason: 'Bad credentials' }));
  await assert.rejects(new BookingClient('https://api.test').login('admin', 'nope'), /Login failed/);
});

test('getWithRetry retries a 503, then succeeds', async () => {
  const answers = [new Response('down', { status: 503 }), json(200, { firstname: 'Sally' })];
  const fake = mock.method(globalThis, 'fetch', async () => answers.shift());

  const res = await new BookingClient('https://api.test').getWithRetry(1, 3, 1);

  assert.equal(fake.mock.callCount(), 2);
  assert.deepEqual(res, { status: 200, body: { firstname: 'Sally' } });
});
''', {'save': 'tests/mocking.test.js'}),
                ('tip', '<code>mock.timers.enable({ apis: [\'setTimeout\'] })</code> fakes the clock, so retry and polling code with long waits can be tested instantly with <code>mock.timers.tick(ms)</code>.'),
            ],
        },
        {
            'id': 'concurrency', 'title': 'Concurrency and a quick latency check', 'emoji': '⚡', 'level': 'Advanced',
            'blocks': [
                ('code', 'js', 'tests/concurrency.test.js', '''
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { BASE } from '../src/config.js';

test('twenty reads at once agree and stay fast', async () => {
  const times = [];
  const bodies = await Promise.all(Array.from({ length: 20 }, async () => {
    const start = performance.now();
    const res = await fetch(`${BASE}/booking/1`);
    const text = await res.text();
    times.push(performance.now() - start);
    assert.equal(res.status, 200);
    return text;
  }));

  assert.equal(new Set(bodies).size, 1, 'every caller should see the same booking');

  times.sort((a, b) => a - b);
  const p95 = times[Math.ceil(times.length * 0.95) - 1];
  assert.ok(p95 < 3000, `p95 was ${p95.toFixed(0)} ms`);
});

test('parallel creates get unique ids', async () => {
  const make = i => fetch(`${BASE}/booking`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ firstname: `C${i}`, lastname: 'X', totalprice: i, depositpaid: false,
      bookingdates: { checkin: '2026-10-01', checkout: '2026-10-02' } }),
  }).then(r => r.json());

  const ids = (await Promise.all([0, 1, 2, 3, 4].map(make))).map(b => b.bookingid);
  assert.equal(new Set(ids).size, 5);
});
''', {'save': 'tests/concurrency.test.js'}),
                ('h', 'The percentile formula'),
                ('p', 'Sort n times from fastest to slowest. The p95 sits at'),
                ('p', '<span class="eqn">index = ⌈ 0.95 × n ⌉ − 1</span>'),
                ('p', 'With 20 calls that is ⌈ 19 ⌉ − 1 = 18, the 19th fastest call.'),
            ],
        },
        {
            'id': 'framework', 'title': 'Framework design with the client', 'emoji': '🏗️', 'level': 'Advanced',
            'blocks': [
                ('p', 'The <code>BookingClient</code> from the mocking lesson keeps tests short. The same class is tested with mocks and then used for real calls.'),
                ('code', 'js', 'tests/framework.test.js', '''
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { BookingClient } from '../src/client.js';

test('full flow through the client', async () => {
  const api = await new BookingClient().login();

  const created = await api.create({ firstname: 'Frame', lastname: 'Work', totalprice: 120, depositpaid: true,
    bookingdates: { checkin: '2026-11-01', checkout: '2026-11-02' } });
  assert.equal(created.status, 200);
  const id = created.body.bookingid;

  assert.equal((await api.patch(id, { lastname: 'Updated' })).body.lastname, 'Updated');
  assert.equal((await api.remove(id)).status, 201);
  assert.deepEqual(await api.get(id), { status: 404, body: 'Not Found' });
});
''', {'save': 'tests/framework.test.js'}),
            ],
        },
        {
            'id': 'ci', 'title': 'Reporters, coverage, filters and CI', 'emoji': '🚀', 'level': 'Expert',
            'blocks': [
                ('code', 'bash', 'Runner options worth knowing', '''
node --test --test-name-pattern="smoke"          # only tests whose name matches
node --test --test-skip-pattern="slow"           # skip by name
node --test --test-concurrency=4                 # files in parallel
node --test --test-reporter=tap                  # tap, spec, dot, junit, lcov
node --test --experimental-test-coverage         # coverage of src/ used by tests
node --test --test-timeout=30000                 # fail any test over 30 s
'''),
                ('code', 'yaml', '.github/workflows/native-api.yml', '''
name: API tests
on: [push, pull_request]
jobs:
  api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: mkdir -p results && npm run test:ci
        env:
          BASE_URL: ${{ vars.BASE_URL }}
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: junit
          path: results
'''),
                ('tip', 'There is no <code>npm install</code> step at all. That is the main benefit of the native approach.'),
            ],
        },
        {
            'id': 'expert', 'title': 'Expert topics', 'emoji': '🧠', 'level': 'Expert',
            'blocks': [
                ('ul', [
                    '<b>Streaming</b>: <code>res.body</code> is a web <code>ReadableStream</code>. Read large downloads or server sent events chunk by chunk with <code>for await (const chunk of res.body)</code>.',
                    '<b>Redirects</b>: <code>redirect: \'manual\'</code> lets a test assert on a 301 or 302 and its <code>Location</code> header instead of following it.',
                    '<b>Proxies and certificates</b>: recent Node releases read <code>HTTP_PROXY</code> and <code>HTTPS_PROXY</code> for fetch when started with <code>NODE_USE_ENV_PROXY=1</code>. For a private test certificate authority use <code>NODE_EXTRA_CA_CERTS</code>.',
                    '<b>Browser side</b>: the same fetch works in the DevTools console, but the browser applies CORS. A call that works in Node may be blocked in a page, which is itself worth testing.',
                    '<b>GraphQL</b>: POST <code>{ query, variables }</code> and assert <code>body.errors</code> is undefined.',
                    '<b>Contract tests</b>: keep shape definitions next to the OpenAPI spec and check every response against them.',
                ]),
                ('code', 'js', 'Check a redirect without following it', '''
const res = await fetch(`${BASE}/old-path`, { redirect: 'manual' });
assert.equal(res.status, 301);
assert.equal(res.headers.get('location'), '/new-path');
'''),
            ],
        },
        {
            'id': 'scenario', 'title': 'Real world scenario: a hotel front desk day', 'emoji': '🏨', 'level': 'Scenario',
            'blocks': [
                ('p', 'The receptionist logs in, books a room, adds breakfast, and the guest cancels. Someone without a login also tries to cancel. Using <code>t.test</code> subtests, each step appears as its own line in the report.'),
                ('flow', [
                    ('Health check', '<code>GET /ping</code> answers 201.'),
                    ('Log in', 'The client stores the token cookie.'),
                    ('Book', '<code>POST /booking</code> with a unique guest.'),
                    ('Search', '<code>GET /booking?firstname=...</code> includes the id.'),
                    ('Add breakfast', '<code>PATCH</code> with the token.'),
                    ('Unauthorised cancel', '<code>DELETE</code> with no token gives 403.'),
                    ('Cancel', '<code>DELETE</code> with the token gives 201.'),
                    ('Gone', '<code>GET</code> gives 404.'),
                ]),
                ('code', 'js', 'tests/journey.test.js', '''
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { BASE } from '../src/config.js';
import { BookingClient } from '../src/client.js';

test('front desk day', async (t) => {
  const desk = new BookingClient();
  const anonymous = new BookingClient();
  const guest = `Guest${Date.now()}`;
  let id;

  await t.test('API is up', async () => {
    assert.equal((await fetch(`${BASE}/ping`)).status, 201);
  });

  await t.test('receptionist logs in', async () => {
    await desk.login();
    assert.match(desk.headers.Cookie, /^token=.+/);
  });

  await t.test('book a room', async () => {
    const res = await desk.create({ firstname: guest, lastname: 'Panda', totalprice: 250, depositpaid: true,
      bookingdates: { checkin: '2026-11-01', checkout: '2026-11-04' } });
    assert.equal(res.status, 200);
    id = res.body.bookingid;
  });

  await t.test('find it by name', async () => {
    const url = new URL('/booking', BASE);
    url.searchParams.set('firstname', guest);
    const found = await (await fetch(url)).json();
    assert.ok(found.some(b => b.bookingid === id));
  });

  await t.test('add breakfast', async () => {
    const res = await desk.patch(id, { additionalneeds: 'Breakfast' });
    assert.equal(res.body.additionalneeds, 'Breakfast');
    assert.equal(res.body.lastname, 'Panda');
  });

  await t.test('cancel without login is refused', async () => {
    assert.equal((await anonymous.remove(id)).status, 403);
    assert.equal((await anonymous.get(id)).status, 200);
  });

  await t.test('cancel and confirm', async () => {
    assert.equal((await desk.remove(id)).status, 201);
    assert.equal((await desk.get(id)).status, 404);
  });
});
''', {'save': 'tests/journey.test.js'}),
            ],
        },
    ],
    'quiz': [
        {'lv': 'e', 'q': 'Does <code>fetch</code> throw when the server answers 404?', 'o': ['Yes, always', 'No, it resolves and you check <code>res.status</code> or <code>res.ok</code>', 'Only in Node', 'Only for POST'], 'a': 1, 'hint': 'fetch only rejects on network failures.', 'why': 'A 404 is still a valid HTTP response. fetch rejects only when no response arrives, for example a refused connection or a timeout.'},
        {'lv': 'e', 'q': 'Which command runs every test file with the built in runner?', 'o': ['<code>node test</code>', '<code>node --test</code>', '<code>npm jest</code>', '<code>node run tests</code>'], 'a': 1, 'hint': 'It is a flag.', 'why': '<code>node --test</code> finds files such as <code>*.test.js</code> and runs them.'},
        {'lv': 'm', 'q': 'You POST <code>JSON.stringify(booking)</code> and the server answers 500. What is the most likely cause?', 'o': ['fetch cannot POST', 'Missing <code>Content-Type: application/json</code>', 'You must use FormData', 'The URL needs a trailing slash'], 'a': 1, 'hint': 'What type does a plain string body get?', 'why': 'A string body is labelled text/plain. The server does not parse it as JSON, so required fields look missing.'},
        {'lv': 'm', 'q': 'How do you give a fetch call a 5 second limit?', 'o': ['<code>{ timeout: 5000 }</code>', '<code>{ signal: AbortSignal.timeout(5000) }</code>', '<code>fetch.setTimeout(5000)</code>', 'It always has one'], 'a': 1, 'hint': 'fetch has no timeout option.', 'why': 'fetch is cancelled through an AbortSignal. <code>AbortSignal.timeout(ms)</code> creates one that fires after the time limit.'},
        {'lv': 'h', 'q': 'Which call replaces the global fetch with a mock in node:test?', 'o': ['<code>mock.fn(fetch)</code>', '<code>mock.method(globalThis, \'fetch\', impl)</code>', '<code>jest.spyOn(fetch)</code>', '<code>globalThis.fetch.mock()</code>'], 'a': 1, 'hint': 'fetch is a method of the global object.', 'why': '<code>mock.method</code> swaps a method on an object and records every call. <code>mock.restoreAll()</code> puts the real one back.'},
        {'lv': 'h', 'q': 'Why call <code>await res.body?.cancel()</code> when you only need the status?', 'o': ['It is required by the spec', 'It frees the connection instead of leaving the unread body pending', 'It makes the status available', 'It retries the call'], 'a': 1, 'hint': 'Unread bodies hold resources.', 'why': 'An unread body keeps the connection busy until it is garbage collected. Cancelling releases it at once, which matters in large suites.'},
        {'lv': 'x', 'q': 'Tests that pass alone fail when a <code>describe</code> has <code>{ concurrency: true }</code>. Likely cause?', 'o': ['Node is too old', 'They share a variable such as an id that another test changes', 'fetch is not thread safe', 'Assertions are async'], 'a': 1, 'hint': 'Concurrency and shared state.', 'why': 'With concurrency on, tests interleave. Shared mutable variables must be removed, or the tests must run in order.'},
        {'lv': 'x', 'q': 'With 40 sorted response times, which index (from 0) is the p95?', 'o': ['37', '38', '39', '36'], 'a': 0, 'hint': 'index = ceil(0.95 × n) − 1', 'why': '⌈0.95 × 40⌉ − 1 = 38 − 1 = 37.'},
    ],
}
