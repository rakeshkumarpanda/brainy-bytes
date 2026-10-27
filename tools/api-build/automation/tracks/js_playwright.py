TRACK = {
    'id': 'js-playwright', 'lang': 'js', 'tool': 'playwright',
    'title': 'Playwright Test with JavaScript', 'emoji': '🎭',
    'tagline': 'API tests with the request fixture, custom fixtures, parallel workers, traces and UI plus API in one runner.',
    'intro': 'Playwright Test is a full test runner. Its built in <code>request</code> fixture is an HTTP client that already knows your <code>baseURL</code> and headers from the config. You get parallel workers, retries, HTML reports and traces for free, and you can mix API calls into UI tests to create data, sign in and mock the network.',
    'stack': [
        ('Node.js', '22 LTS or newer', 'runtime'),
        ('@playwright/test', '1.64.1', 'runner, request fixture, expect'),
        ('Ajv', '8.20.0', 'JSON Schema checks'),
        ('ajv-formats', '3', 'date and email formats'),
    ],
    'sections': [
        {
            'id': 'why', 'title': 'Why test APIs with Playwright Test', 'emoji': '🎯', 'level': 'Basic',
            'blocks': [
                ('p', 'An API test sends a request and checks the response, with no browser. Playwright Test does not start a browser unless a test asks for a <code>page</code>, so pure API tests run in milliseconds and in parallel across workers.'),
                ('table', ['Feature', 'Why testers like it'], [
                    ['<code>request</code> fixture', 'ready to use, with base URL and headers from the config'],
                    ['<code>expect(res).toBeOK()</code>', 'prints the response body when the status is not 2xx'],
                    ['Custom fixtures', 'tokens and test data created and cleaned up for you'],
                    ['Parallel workers', 'files run at the same time with no extra setup'],
                    ['Trace viewer and HTML report', 'every API call with headers and bodies, after the run'],
                    ['UI and API together', 'seed data, log in and mock the network inside UI tests'],
                ]),
                ('qa', 'If your UI tests already use Playwright, API tests can live in the same repo and CI job. Start by replacing slow UI setup steps with API calls.'),
            ],
        },
        {
            'id': 'setup', 'title': 'Project setup and config', 'emoji': '🧰', 'level': 'Basic',
            'blocks': [
                ('code', 'bash', 'Terminal', '''
npm init -y
npm install -D @playwright/test@1.64.1 ajv ajv-formats
npx playwright test                         # run everything
npx playwright test tests/crud.spec.js      # one file
npx playwright test --grep @smoke           # tagged tests only
npx playwright show-report                  # open the HTML report
BASE_URL=http://localhost:3001 npx playwright test
'''),
                ('code', 'json', 'package.json', '''
{
  "name": "booker-playwright-api",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "playwright test"
  },
  "devDependencies": {
    "@playwright/test": "1.64.1",
    "ajv": "^8.20.0",
    "ajv-formats": "^3.0.1"
  }
}
''', {'save': 'package.json'}),
                ('code', 'js', 'playwright.config.js', '''
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  retries: process.env.CI ? 1 : 0,
  reporter: [['list'], ['html', { open: 'never' }], ['junit', { outputFile: 'results/junit.xml' }]],
  use: {
    baseURL: process.env.BASE_URL ?? 'https://restful-booker.herokuapp.com',
    extraHTTPHeaders: { Accept: 'application/json' },
    trace: 'retain-on-failure',
  },
});
''', {'save': 'playwright.config.js'}),
                ('tip', 'API only projects never need browsers. Skip <code>npx playwright install</code> until you add UI tests.'),
            ],
        },
        {
            'id': 'first-test', 'title': 'Your first test: GET a booking', 'emoji': '👋', 'level': 'Basic',
            'blocks': [
                ('code', 'js', 'tests/first.spec.js', '''
import { test, expect } from '@playwright/test';

test('ping says the API is up @smoke', async ({ request }) => {
  const res = await request.get('/ping');
  expect(res.status()).toBe(201);          // Restful Booker answers 201 to a health check
});

test('get one booking', async ({ request }) => {
  const res = await request.get('/booking/1');

  await expect(res).toBeOK();              // any 2xx, shows the body if not
  expect(res.headers()['content-type']).toContain('application/json');

  const body = await res.json();
  expect(body).toEqual({
    firstname: expect.any(String),
    lastname: expect.any(String),
    totalprice: expect.any(Number),
    depositpaid: expect.any(Boolean),
    bookingdates: { checkin: expect.stringMatching(/^\\d{4}-\\d{2}-\\d{2}$/), checkout: expect.any(String) },
    additionalneeds: expect.any(String),
  });
});
''', {'save': 'tests/first.spec.js'}),
                ('ul', [
                    'The <code>request</code> fixture uses <code>baseURL</code>, so paths start with <code>/</code>.',
                    '<code>res.status()</code>, <code>res.headers()</code>, <code>await res.json()</code> and <code>await res.text()</code> read the response. Header names are lower case.',
                    '<code>expect.any(String)</code> and <code>expect.stringMatching</code> check the shape when exact values change.',
                    'The <code>@smoke</code> tag in the title lets you run a subset with <code>--grep @smoke</code>.',
                ]),
                ('try', {'method': 'GET', 'path': '/booking/1'}),
            ],
        },
        {
            'id': 'request', 'title': 'Request options', 'emoji': '🧱', 'level': 'Basic',
            'blocks': [
                ('code', 'js', 'Everything a call can take', '''
await request.get('/booking', { params: { firstname: 'Mary Ann', lastname: 'Brown' } });

await request.post('/booking', {
  data: booking,                                // objects become JSON with the right Content-Type
  headers: { 'X-Request-Id': crypto.randomUUID() },
  timeout: 10_000,                              // ms for this call
  failOnStatusCode: false,                      // the default, set true to throw on 4xx and 5xx
  maxRetries: 2,                                // retry network errors such as ECONNRESET
});

await request.post('/login', { form: { user: 'qa', password: 'secret' } });       // form fields
await request.post('/documents', { multipart: { file: fs.createReadStream('a.pdf'), note: 'March' } });
await request.fetch('/booking/1', { method: 'HEAD' });                            // any method
'''),
                ('table', ['Option', 'Sends'], [
                    ['<code>params</code>', 'query string, encoded for you'],
                    ['<code>data</code>', 'JSON for objects, raw for strings and buffers'],
                    ['<code>form</code>', 'application/x-www-form-urlencoded'],
                    ['<code>multipart</code>', 'multipart/form-data, for files'],
                    ['<code>headers</code>', 'extra headers for this call'],
                    ['<code>timeout</code>', 'time limit in ms'],
                    ['<code>maxRetries</code>', 'retries for network errors only'],
                ]),
            ],
        },
        {
            'id': 'crud', 'title': 'Create, update and delete (CRUD)', 'emoji': '✍️', 'level': 'Basic',
            'blocks': [
                ('code', 'js', 'tests/crud.spec.js', '''
import { test, expect } from '@playwright/test';

const basic = 'Basic ' + Buffer.from('admin:password123').toString('base64');

const newBooking = {
  firstname: 'Rakesh',
  lastname: 'Panda',
  totalprice: 250,
  depositpaid: true,
  bookingdates: { checkin: '2026-11-01', checkout: '2026-11-04' },
  additionalneeds: 'Breakfast',
};

test.describe.serial('booking CRUD', () => {
  let id;

  test('create', async ({ request }) => {
    const res = await request.post('/booking', { data: newBooking });
    await expect(res).toBeOK();
    const body = await res.json();
    expect(body.bookingid).toBeGreaterThan(0);
    expect(body.booking).toEqual(newBooking);
    id = body.bookingid;
  });

  test('replace with PUT', async ({ request }) => {
    const res = await request.put(`/booking/${id}`, {
      headers: { Authorization: basic },
      data: { ...newBooking, lastname: 'Kumar', totalprice: 300 },
    });
    expect(await res.json()).toMatchObject({ lastname: 'Kumar', totalprice: 300 });
  });

  test('change one field with PATCH', async ({ request }) => {
    const res = await request.patch(`/booking/${id}`, {
      headers: { Authorization: basic },
      data: { additionalneeds: 'Dinner' },
    });
    expect(await res.json()).toMatchObject({ additionalneeds: 'Dinner', lastname: 'Kumar' });
  });

  test('delete, then it is gone', async ({ request }) => {
    const del = await request.delete(`/booking/${id}`, { headers: { Authorization: basic } });
    expect(del.status()).toBe(201);              // this API answers 201 to DELETE
    expect((await request.get(`/booking/${id}`)).status()).toBe(404);
  });
});
''', {'save': 'tests/crud.spec.js'}),
                ('warn', '<code>test.describe.serial</code> runs the tests in order and stops after the first failure. Use it only for true step by step flows. Independent tests with fixtures, shown next, are better in most cases.'),
                ('try', {'method': 'POST', 'path': '/booking', 'body': {'firstname': 'Rakesh', 'lastname': 'Panda', 'totalprice': 250, 'depositpaid': True, 'bookingdates': {'checkin': '2026-11-01', 'checkout': '2026-11-04'}, 'additionalneeds': 'Breakfast'}}),
            ],
        },
        {
            'id': 'assertions', 'title': 'Assertions: matchers, soft checks and polling', 'emoji': '🔍', 'level': 'Intermediate',
            'blocks': [
                ('code', 'js', 'The matchers that matter for APIs', '''
const body = await res.json();

expect(body).toMatchObject({ firstname: 'Sally' });         // partial match, extra keys allowed
expect(body).toEqual({ ...expected, additionalneeds: expect.anything() });   // exact, with wildcards
expect(body).toHaveProperty('bookingdates.checkin');        // nested path
expect(body.totalprice).toBeGreaterThanOrEqual(0);
expect(body.firstname).toMatch(/^[A-Z]/);
expect(list).toContainEqual({ bookingid: 1 });              // an item in an array
expect(list).toEqual(expect.arrayContaining([{ bookingid: 1 }]));
expect(list.length).toBeGreaterThan(0);

// Soft checks: keep going and report every failure at the end of the test
expect.soft(res.status()).toBe(200);
expect.soft(body.firstname).toBeTruthy();
expect.soft(body.depositpaid).toBe(true);

// Poll until a background job finishes, with a time limit
await expect.poll(async () => (await (await request.get(`/jobs/${jobId}`)).json()).status, {
  timeout: 30_000,
  intervals: [500, 1000, 2000],
}).toBe('DONE');
'''),
                ('code', 'js', 'Group steps so the report reads like a test case', '''
await test.step('create a booking', async () => { /* ... */ });
await test.step('check it appears in search', async () => { /* ... */ });
'''),
                ('tip', 'Use <code>toMatchObject</code> when the API may add new fields, and <code>toEqual</code> when the exact shape is part of the contract.'),
            ],
        },
        {
            'id': 'fixtures', 'title': 'Custom fixtures for tokens and test data', 'emoji': '🧷', 'level': 'Intermediate',
            'blocks': [
                ('p', 'Fixtures prepare what a test needs and clean it up afterwards. Code after <code>await use(value)</code> is the cleanup, and it runs even when the test fails. A worker fixture runs once per worker process, which suits a login token.'),
                ('code', 'js', 'tests/fixtures.js', '''
import { test as base, expect } from '@playwright/test';

export const test = base.extend({
  // once per worker: log in and share the token
  token: [async ({ playwright }, use, workerInfo) => {
    const api = await playwright.request.newContext({ baseURL: workerInfo.project.use.baseURL });
    const res = await api.post('/auth', { data: { username: 'admin', password: 'password123' } });
    const { token } = await res.json();
    await use(token);
    await api.dispose();
  }, { scope: 'worker' }],

  // once per test: a fresh booking that is deleted afterwards
  booking: async ({ request, token }, use) => {
    const data = {
      firstname: `Guest${Date.now()}${Math.floor(Math.random() * 1000)}`,
      lastname: 'Fixture',
      totalprice: 150,
      depositpaid: true,
      bookingdates: { checkin: '2026-11-10', checkout: '2026-11-12' },
    };
    const res = await request.post('/booking', { data });
    await expect(res).toBeOK();
    const { bookingid } = await res.json();

    await use({ id: bookingid, ...data });

    await request.delete(`/booking/${bookingid}`, { headers: { Cookie: `token=${token}` } });
  },
});

export { expect };
''', {'save': 'tests/fixtures.js'}),
                ('code', 'js', 'tests/fixtures.spec.js', '''
import { test, expect } from './fixtures.js';

test('read a fresh booking', async ({ request, booking }) => {
  const res = await request.get(`/booking/${booking.id}`);
  expect(await res.json()).toMatchObject({ firstname: booking.firstname });
});

test('patch with the shared token', async ({ request, booking, token }) => {
  const res = await request.patch(`/booking/${booking.id}`, {
    headers: { Cookie: `token=${token}` },
    data: { additionalneeds: 'Late checkout' },
  });
  await expect(res).toBeOK();
  expect((await res.json()).additionalneeds).toBe('Late checkout');
});
''', {'save': 'tests/fixtures.spec.js'}),
                ('why', 'Every test has its own data and cleans up after itself. Tests can run in any order and in parallel without breaking each other.'),
            ],
        },
        {
            'id': 'auth', 'title': 'Authentication and negative tests', 'emoji': '🔐', 'level': 'Intermediate',
            'blocks': [
                ('code', 'js', 'Common styles', '''
// Per call
await request.patch(url, { headers: { Cookie: `token=${token}` }, data });
await request.get(url, { headers: { Authorization: `Bearer ${process.env.API_TOKEN}` } });

// For every call in the project, from the config
use: { extraHTTPHeaders: { Authorization: `Bearer ${process.env.API_TOKEN}` } }

// Basic auth sent up front, for a new context
const api = await playwright.request.newContext({
  baseURL,
  httpCredentials: { username: 'admin', password: 'password123', send: 'always' },
});
'''),
                ('code', 'js', 'tests/auth.spec.js', '''
import { test, expect } from './fixtures.js';

for (const [name, headers] of [
  ['no auth', {}],
  ['made up token', { Cookie: 'token=not-real' }],
  ['wrong password', { Authorization: 'Basic ' + Buffer.from('admin:wrong').toString('base64') }],
]) {
  test(`update refused with ${name}`, async ({ request, booking }) => {
    const res = await request.patch(`/booking/${booking.id}`, { headers, data: { firstname: 'Hacker' } });
    expect(res.status()).toBe(403);
    expect((await (await request.get(`/booking/${booking.id}`)).json()).firstname).not.toBe('Hacker');
  });
}
''', {'save': 'tests/auth.spec.js'}),
                ('warn', 'Without <code>send: \'always\'</code>, <code>httpCredentials</code> waits for a 401 challenge. Restful Booker answers 403, so the password would never be sent.'),
            ],
        },
        {
            'id': 'data-driven', 'title': 'Data driven tests', 'emoji': '📊', 'level': 'Intermediate',
            'blocks': [
                ('p', 'Playwright has no special data annotation. A normal loop that calls <code>test()</code> creates one named test per row, and each row can run in parallel.'),
                ('code', 'js', 'tests/data.spec.js', '''
import { test, expect } from '@playwright/test';

const valid = {
  firstname: 'Test', lastname: 'User', totalprice: 100, depositpaid: true,
  bookingdates: { checkin: '2026-12-01', checkout: '2026-12-03' },
};

const names = [
  { first: 'Ann', last: 'Lee' },
  { first: 'José', last: 'Núñez' },
  { first: "O'Brien", last: 'Smith-Jones' },
  { first: 'A', last: 'B' },
];

for (const { first, last } of names) {
  test(`stores the name ${first} ${last}`, async ({ request }) => {
    const res = await request.post('/booking', { data: { ...valid, firstname: first, lastname: last } });
    await expect(res).toBeOK();
    expect((await res.json()).booking.firstname).toBe(first);
  });
}

for (const field of ['firstname', 'lastname', 'totalprice', 'depositpaid', 'bookingdates']) {
  test(`missing ${field} is rejected`, async ({ request }) => {
    const { [field]: _, ...body } = valid;
    const res = await request.post('/booking', { data: body });
    expect(res.status(), 'Restful Booker answers 500, a good API answers 400').not.toBe(200);
  });
}

const statusCases = [['/ping', 201], ['/booking', 200], ['/booking/999999', 404], ['/booking/abc', 404]];
for (const [path, status] of statusCases) {
  test(`GET ${path} gives ${status}`, async ({ request }) => {
    expect((await request.get(path)).status()).toBe(status);
  });
}
''', {'save': 'tests/data.spec.js'}),
                ('tip', 'For larger sets, read a JSON or CSV file at the top of the spec with <code>fs.readFileSync</code> and loop over its rows in the same way.'),
            ],
        },
        {
            'id': 'schema', 'title': 'JSON Schema checks with Ajv', 'emoji': '📐', 'level': 'Advanced',
            'blocks': [
                ('code', 'js', 'tests/schema.spec.js', '''
import { test, expect } from '@playwright/test';
import Ajv from 'ajv';
import addFormats from 'ajv-formats';

const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

const validateBooking = ajv.compile({
  type: 'object',
  required: ['firstname', 'lastname', 'totalprice', 'depositpaid', 'bookingdates'],
  properties: {
    firstname: { type: 'string', minLength: 1 },
    lastname: { type: 'string', minLength: 1 },
    totalprice: { type: 'integer', minimum: 0 },
    depositpaid: { type: 'boolean' },
    bookingdates: {
      type: 'object',
      required: ['checkin', 'checkout'],
      properties: {
        checkin: { type: 'string', format: 'date' },
        checkout: { type: 'string', format: 'date' },
      },
    },
    additionalneeds: { type: 'string' },
  },
  additionalProperties: false,
});

test('booking matches the schema', async ({ request }) => {
  const body = await (await request.get('/booking/1')).json();
  const ok = validateBooking(body);
  expect(validateBooking.errors ?? [], JSON.stringify(validateBooking.errors)).toEqual([]);
  expect(ok).toBe(true);
});

test('schema catches a renamed field', () => {
  const ok = validateBooking({
    firstname: 'A', lastname: 'B', totalPrice: 1, depositpaid: true,
    bookingdates: { checkin: '2026-01-01', checkout: '2026-01-02' },
  });
  expect(ok).toBe(false);
  expect(validateBooking.errors.map(e => e.message)).toContain("must have required property 'totalprice'");
});
''', {'save': 'tests/schema.spec.js'}),
                ('tip', 'The second test checks the checker. A schema that never fails is as useless as no schema.'),
            ],
        },
        {
            'id': 'framework', 'title': 'Framework design: client class plus fixture', 'emoji': '🏗️', 'level': 'Advanced',
            'blocks': [
                ('code', 'js', 'tests/support/booking-client.js', '''
export class BookingClient {
  constructor(request) {
    this.request = request;
    this.headers = {};
  }

  async login(username = 'admin', password = 'password123') {
    const res = await this.request.post('/auth', { data: { username, password } });
    this.headers.Cookie = `token=${(await res.json()).token}`;
    return this;
  }

  create(data) { return this.request.post('/booking', { data }); }
  get(id) { return this.request.get(`/booking/${id}`); }
  async find(params) { return (await (await this.request.get('/booking', { params })).json()).map(b => b.bookingid); }
  patch(id, data) { return this.request.patch(`/booking/${id}`, { headers: this.headers, data }); }
  remove(id) { return this.request.delete(`/booking/${id}`, { headers: this.headers }); }
}
''', {'save': 'tests/support/booking-client.js'}),
                ('code', 'js', 'tests/framework.spec.js', '''
import { test as base, expect } from '@playwright/test';
import { BookingClient } from './support/booking-client.js';

const test = base.extend({
  bookings: async ({ request }, use) => use(await new BookingClient(request).login()),
});

test('patch through the client', async ({ bookings }) => {
  const created = await (await bookings.create({
    firstname: 'Frame', lastname: 'Work', totalprice: 120, depositpaid: true,
    bookingdates: { checkin: '2026-11-01', checkout: '2026-11-02' },
  })).json();

  expect(await bookings.find({ firstname: 'Frame' })).toContain(created.bookingid);
  expect(await (await bookings.patch(created.bookingid, { lastname: 'Updated' })).json()).toMatchObject({ lastname: 'Updated' });
  expect((await bookings.remove(created.bookingid)).status()).toBe(201);
  expect((await bookings.get(created.bookingid)).status()).toBe(404);
});
''', {'save': 'tests/framework.spec.js'}),
            ],
        },
        {
            'id': 'ui-api', 'title': 'UI and API together', 'emoji': '🖥️', 'level': 'Advanced',
            'blocks': [
                ('p', 'Inside a UI test, <code>page.request</code> shares cookies with the browser. Three patterns save QA teams the most time.'),
                ('code', 'js', 'Seed by API, check in the UI, and check what the UI sends', '''
test('new booking shows on the dashboard', async ({ page }) => {
  // 1. create data in milliseconds
  const res = await page.request.post('/api/bookings', { data: { guest: 'Rakesh Panda', nights: 3 } });
  const { id } = await res.json();

  // 2. check the UI
  await page.goto(`/bookings/${id}`);
  await expect(page.getByRole('heading')).toContainText('Rakesh Panda');

  // 3. check the API call the UI makes when the user saves
  const saved = page.waitForResponse(r => r.url().includes(`/api/bookings/${id}`) && r.request().method() === 'PATCH');
  await page.getByLabel('Nights').fill('4');
  await page.getByRole('button', { name: 'Save' }).click();
  const patch = await saved;
  expect(patch.status()).toBe(200);
  expect(patch.request().postDataJSON()).toMatchObject({ nights: 4 });
});
'''),
                ('code', 'js', 'Mock the API to test error handling in the UI', '''
test('dashboard shows a friendly error', async ({ page }) => {
  await page.route('**/api/bookings', route => route.fulfill({ status: 500, json: { error: 'down' } }));
  await page.goto('/bookings');
  await expect(page.getByText('Something went wrong')).toBeVisible();
});
'''),
                ('code', 'js', 'Log in once by API for every UI test (setup project)', '''
// tests/auth.setup.js
import { test as setup } from '@playwright/test';

setup('sign in', async ({ request }) => {
  await request.post('/api/login', { form: { user: 'qa', password: process.env.QA_PASSWORD } });
  await request.storageState({ path: '.auth/qa.json' });
});

// playwright.config.js
projects: [
  { name: 'setup', testMatch: /.*\\.setup\\.js/ },
  { name: 'ui', dependencies: ['setup'], use: { storageState: '.auth/qa.json' } },
]
'''),
                ('qa', '<code>waitForResponse</code> lets a UI test assert on the exact request the page sent. This catches bugs where the screen looks right but the wrong data reaches the server.'),
            ],
        },
        {
            'id': 'parallel-ci', 'title': 'Workers, sharding, traces and CI', 'emoji': '🚀', 'level': 'Expert',
            'blocks': [
                ('code', 'bash', 'Run options', '''
npx playwright test --workers 4               # parallel processes
npx playwright test --shard 1/3               # split across 3 CI machines
npx playwright test --repeat-each 5           # hunt for flaky tests
npx playwright test --last-failed             # rerun failures only
npx playwright show-trace test-results/**/trace.zip
'''),
                ('ul', [
                    'Every API call appears in the trace with method, URL, headers, body and timing, which makes CI failures easy to read.',
                    'Worker fixtures run once per worker. With 4 workers you log in 4 times.',
                    '<code>retries</code> in the config reruns failed tests and marks them as flaky in the report. Treat flaky tests as bugs to fix, not to hide.',
                ]),
                ('code', 'yaml', '.github/workflows/playwright-api.yml', '''
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
          cache: npm
      - run: npm ci
      - run: npx playwright test
        env:
          BASE_URL: ${{ vars.BASE_URL }}
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report
'''),
            ],
        },
        {
            'id': 'expert', 'title': 'Expert topics', 'emoji': '🧠', 'level': 'Expert',
            'blocks': [
                ('ul', [
                    '<b>Separate projects</b>: an <code>api</code> project with no browser and a <code>ui</code> project, each with its own <code>testDir</code> and settings, in one config.',
                    '<b>Global setup</b>: start a mock server or seed a database once before all workers with <code>globalSetup</code>.',
                    '<b>Contract checks</b>: compile Ajv validators from your OpenAPI components once and reuse them in every test.',
                    '<b>GraphQL</b>: <code>request.post(\'/graphql\', { data: { query, variables } })</code>, then assert that <code>errors</code> is undefined.',
                    '<b>Idempotency and concurrency</b>: fire several identical calls with <code>Promise.all</code> and check the final state.',
                    '<b>Annotations</b>: <code>test.info().annotations.push({ type: \'issue\', description: \'BUG-123\' })</code> links known bugs in the report.',
                ]),
                ('code', 'js', 'Concurrency check with Promise.all', '''
test('five creates in parallel get five different ids', async ({ request }) => {
  const make = i => request.post('/booking', { data: { firstname: `P${i}`, lastname: 'X', totalprice: i, depositpaid: false,
    bookingdates: { checkin: '2026-10-01', checkout: '2026-10-02' } } });
  const results = await Promise.all([0, 1, 2, 3, 4].map(make));
  const ids = await Promise.all(results.map(async r => (await r.json()).bookingid));
  expect(new Set(ids).size).toBe(5);
});
'''),
            ],
        },
        {
            'id': 'essentials', 'title': 'Real project essentials: environments, secrets, test data, logging and cleanup', 'emoji': '🧳', 'level': 'Intermediate',
            'blocks': [
                ('p', 'A company suite runs against several servers, keeps secrets out of Git, makes unique data so parallel workers never clash, attaches the exact exchange to the report when something fails, and leaves the shared QA database clean. Playwright Test has a built in answer for each of these.'),
                ('code', 'js', 'playwright.config.js: one config, many environments', '''
import { defineConfig } from '@playwright/test';

const ENVS = {
  local: 'http://localhost:3001',
  qa: 'https://qa.booker.example',
  prod: 'https://restful-booker.herokuapp.com',
};
const env = process.env.TEST_ENV ?? 'prod';
if (!(env in ENVS)) throw new Error(`TEST_ENV must be one of ${Object.keys(ENVS).join(', ')}`);

export default defineConfig({
  testDir: './tests',
  use: {
    baseURL: process.env.BASE_URL ?? ENVS[env],
    extraHTTPHeaders: { Accept: 'application/json', 'X-Test-Run': process.env.GITHUB_RUN_ID ?? 'local' },
    ignoreHTTPSErrors: process.env.QA_SELF_SIGNED === '1',      // QA only, never production
  },
});
'''),
                ('code', 'js', 'tests/essentials.spec.js', '''
import { test as base, expect } from '@playwright/test';
import { randomUUID } from 'node:crypto';

const test = base.extend({
  // Logs in once per test with the secret from the environment
  token: async ({ request }, use) => {
    const res = await request.post('/auth', { data: { username: process.env.API_USER ?? 'admin', password: process.env.API_PASSWORD ?? 'password123' } });
    await use((await res.json()).token);
  },
  // Collects ids and deletes them after the test, pass or fail
  created: async ({ request, token }, use) => {
    const ids = [];
    await use(ids);
    for (const id of ids) await request.delete(`/booking/${id}`, { headers: { Cookie: `token=${token}` } });
  },
});

async function attach(name, res) {
  await test.info().attach(name, { body: `${res.status()} ${res.url()}\\n${await res.text()}`, contentType: 'text/plain' });
}

test('a unique guest round trip, fully reported', async ({ request, created }) => {
  const guest = {
    firstname: `Guest-${randomUUID().slice(0, 8)}`,
    lastname: 'Essentials',
    totalprice: 500 + Math.floor(Math.random() * 24_500),
    depositpaid: true,
    bookingdates: { checkin: '2026-12-20', checkout: '2026-12-27' },
  };

  const res = await request.post('/booking', { data: guest });
  await attach('create booking', res);
  await expect(res).toBeOK();
  const { bookingid } = await res.json();
  created.push(bookingid);

  const read = await request.get(`/booking/${bookingid}`);
  await attach('read booking', read);
  expect(await read.json()).toEqual(guest);
});
''', {'save': 'tests/essentials.spec.js'}),
                ('code', 'bash', 'Run it', '''
TEST_ENV=local npx playwright test tests/essentials.spec.js
TEST_ENV=qa API_PASSWORD="$QA_PASSWORD" npx playwright test     # secret from your shell or CI
npx playwright show-report                                      # the attachments are under each test
'''),
                ('table', ['Need', 'Playwright answer'], [
                    ['Different servers', '<code>baseURL</code> chosen from <code>TEST_ENV</code> in the config'],
                    ['Secrets', '<code>process.env</code>, filled from CI secrets, or a local <code>.env</code> loaded with <code>node --env-file</code> or the dotenv package'],
                    ['Unique data', '<code>crypto.randomUUID()</code> in the names'],
                    ['Readable failures', '<code>test.info().attach()</code> and <code>trace: \'retain-on-failure\'</code>'],
                    ['Cleanup', 'code after <code>await use()</code> in a fixture'],
                ]),
                ('warn', 'Attachments and traces include request headers. If your API uses an <code>Authorization</code> header, avoid attaching raw headers, or replace the token with <code>***</code> before you attach.'),
            ],
        },
        {
            'id': 'latest', 'title': 'What is new in Playwright Test, and how it helps at work', 'emoji': '🆕', 'level': 'Expert',
            'blocks': [
                ('table', ['Feature', 'Available in', 'How it helps an API tester'], [
                    ['Tracing on API request contexts', 'Playwright 1.64', 'API calls appear in the trace viewer with headers and bodies. The runner traces them for you when <code>trace</code> is on'],
                    ['Cookie methods on API contexts', 'Playwright 1.64', '<code>addCookies()</code>, <code>cookies()</code> and <code>clearCookies()</code> set or inspect a session without a browser'],
                    ['<code>await using</code> on request contexts', 'Playwright 1.64 with Node 24 or TypeScript', 'A private context is disposed automatically at the end of the block'],
                    ['<code>maxRetries</code> per request', 'Playwright 1.46 and newer', 'Retries connection resets only, so real 5xx bugs still fail the test'],
                    ['Testing WebMCP tools and passkeys', 'Playwright 1.61 to 1.64', 'End to end tests for AI tool calls in the browser and passwordless login'],
                    ['Tags and annotations in test details', 'Playwright 1.42 and newer', '<code>test(\'...\', { tag: \'@smoke\' })</code> and linked issues in the report'],
                ]),
                ('code', 'js', 'tests/latest.spec.js', '''
import { test, expect } from '@playwright/test';

test('an API session with its own cookies', { tag: ['@smoke', '@api'] }, async ({ playwright }, testInfo) => {
  const baseURL = testInfo.project.use.baseURL;
  const api = await playwright.request.newContext({ baseURL });     // traced by the runner when trace is on
  try {
    const { token } = await (await api.post('/auth', { data: { username: 'admin', password: 'password123' } })).json();
    await api.addCookies([{ name: 'token', value: token, url: baseURL }]);
    expect((await api.cookies()).map(c => c.name)).toContain('token');

    // The cookie is sent automatically now, so PATCH works without a header
    const res = await api.patch('/booking/1', { data: { additionalneeds: 'Dinner' }, maxRetries: 2 });
    await expect(res).toBeOK();
  } finally {
    await api.dispose();
  }
});
''', {'save': 'tests/latest.spec.js'}),
                ('warn', 'Inside Playwright Test, do not call <code>api.tracing.start()</code> yourself when <code>trace</code> is set in the config. The runner already records every request context the test creates, and a second start fails with <code>Tracing has been already started</code>. Manual tracing is for scripts and other languages that do not use the runner.'),
                ('tip', 'Upgrade Playwright on a branch, run the suite with <code>--repeat-each 3</code> to spot new flakiness, and read the release notes for changed defaults before you merge.'),
            ],
        },
        {
            'id': 'scenario', 'title': 'Real world scenario: a hotel front desk day', 'emoji': '🏨', 'level': 'Scenario',
            'blocks': [
                ('p', 'The receptionist logs in, books a room, adds breakfast, and the guest later cancels. Someone without a login also tries to cancel. Each step is a <code>test.step</code>, so the report reads like the story.'),
                ('flow', [
                    ('Health check', '<code>GET /ping</code> answers 201.'),
                    ('Log in', 'The worker fixture provides a token.'),
                    ('Book', '<code>POST /booking</code> with a unique guest.'),
                    ('Search', 'The new id appears in <code>GET /booking?firstname=...</code>.'),
                    ('Add breakfast', '<code>PATCH</code> with the token.'),
                    ('Unauthorised cancel', '<code>DELETE</code> without a token gives 403.'),
                    ('Cancel', '<code>DELETE</code> with the token gives 201.'),
                    ('Gone', '<code>GET</code> gives 404.'),
                ]),
                ('code', 'js', 'tests/journey.spec.js', '''
import { test, expect } from './fixtures.js';

test('front desk day', async ({ request, token }) => {
  const guest = `Guest${Date.now()}`;
  let id;

  await test.step('API is up', async () => {
    expect((await request.get('/ping')).status()).toBe(201);
  });

  await test.step('book a room', async () => {
    const res = await request.post('/booking', { data: {
      firstname: guest, lastname: 'Panda', totalprice: 250, depositpaid: true,
      bookingdates: { checkin: '2026-11-01', checkout: '2026-11-04' },
    } });
    await expect(res).toBeOK();
    id = (await res.json()).bookingid;
  });

  await test.step('find it by name', async () => {
    expect(await (await request.get('/booking', { params: { firstname: guest } })).json()).toContainEqual({ bookingid: id });
  });

  await test.step('add breakfast', async () => {
    const res = await request.patch(`/booking/${id}`, { headers: { Cookie: `token=${token}` }, data: { additionalneeds: 'Breakfast' } });
    expect(await res.json()).toMatchObject({ additionalneeds: 'Breakfast', lastname: 'Panda' });
  });

  await test.step('cancel without a login is refused', async () => {
    expect((await request.delete(`/booking/${id}`)).status()).toBe(403);
    await expect(await request.get(`/booking/${id}`)).toBeOK();
  });

  await test.step('cancel and confirm', async () => {
    expect((await request.delete(`/booking/${id}`, { headers: { Cookie: `token=${token}` } })).status()).toBe(201);
    expect((await request.get(`/booking/${id}`)).status()).toBe(404);
  });
});
''', {'save': 'tests/journey.spec.js'}),
            ],
        },
    ],
    'quiz': [
        {'lv': 'e', 'q': 'Which fixture sends API requests in a Playwright test?', 'o': ['<code>page</code>', '<code>request</code>', '<code>browser</code>', '<code>context</code>'], 'a': 1, 'hint': 'Its name says what it does.', 'why': 'The <code>request</code> fixture is an <code>APIRequestContext</code> configured from the <code>use</code> settings.'},
        {'lv': 'e', 'q': 'What does <code>await expect(res).toBeOK()</code> check?', 'o': ['Status is exactly 200', 'Status is between 200 and 299', 'The body is JSON', 'The call took under 1 second'], 'a': 1, 'hint': 'OK is a family.', 'why': 'It passes for any 2xx and prints the response when it fails.'},
        {'lv': 'm', 'q': 'The API adds a new field to bookings. Which matcher keeps your test passing?', 'o': ['<code>toEqual</code>', '<code>toMatchObject</code>', '<code>toBe</code>', '<code>toStrictEqual</code>'], 'a': 1, 'hint': 'Partial match.', 'why': '<code>toMatchObject</code> only checks the keys you list. <code>toEqual</code> fails on extra keys.'},
        {'lv': 'm', 'q': 'Where does fixture cleanup code go?', 'o': ['Before <code>use()</code>', 'After <code>await use(value)</code>', 'In <code>afterAll</code> only', 'In the config'], 'a': 1, 'hint': 'use() hands the value to the test.', 'why': 'Code after <code>await use()</code> runs when the test is done, pass or fail.'},
        {'lv': 'h', 'q': 'How many times does a worker scoped login fixture run with <code>--workers 4</code>?', 'o': ['Once', 'Up to 4 times, once per worker', 'Once per test', 'Never'], 'a': 1, 'hint': 'Workers are separate processes.', 'why': 'Each worker process has its own worker fixtures.'},
        {'lv': 'h', 'q': 'How can a UI test check the JSON the page sent when the user clicked Save?', 'o': ['<code>page.route</code> only', '<code>page.waitForResponse</code> and then <code>response.request().postDataJSON()</code>', 'Read the DOM', 'It cannot'], 'a': 1, 'hint': 'Wait for the network.', 'why': 'Waiting for the response gives you both the response and the request, including its body.'},
        {'lv': 'x', 'q': 'Why avoid <code>test.describe.serial</code> for most API tests?', 'o': ['It is slower to write', 'Tests depend on each other, cannot run in parallel and stop at the first failure', 'It disables retries completely', 'It needs a browser'], 'a': 1, 'hint': 'Think independence.', 'why': 'Serial groups chain tests together. Fixtures that create their own data give independent tests that can run in parallel.'},
        {'lv': 'x', 'q': 'A GraphQL call returns 200. What else must the test check?', 'o': ['Nothing', 'That the body has no <code>errors</code> field', 'That it used GET', 'The trace file'], 'a': 1, 'hint': 'GraphQL reports errors in the body.', 'why': 'GraphQL often returns 200 with an <code>errors</code> array, so a status check alone misses failures.'},
    ],
}
