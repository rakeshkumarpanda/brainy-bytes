TRACK = {
    'id': 'ts-playwright', 'lang': 'ts', 'tool': 'playwright',
    'title': 'Playwright Test with TypeScript', 'emoji': '🔷',
    'tagline': 'Typed API tests: models, a typed client, Zod checks at run time, types generated from OpenAPI, and a type check gate in CI.',
    'intro': 'TypeScript is JavaScript with types. In API testing that means your editor knows every field of a booking, a typo such as <code>totalPrice</code> is caught before the test even runs, and a change in the API contract shows up as a red line in every test it breaks. Playwright Test runs <code>.ts</code> files directly, so there is no build step. This track builds the same skills as the JavaScript track, then adds the parts that only types can give you.',
    'stack': [
        ('Node.js', '22 LTS or newer', 'runtime'),
        ('TypeScript', '7.0.2', 'type checker (tsc), the native Go compiler'),
        ('@playwright/test', '1.64.1', 'runner, request fixture, expect'),
        ('Zod', '4.6.7', 'schemas checked at run time, types inferred from them'),
        ('openapi-typescript', '7.13.0', 'types generated from an OpenAPI file (run with npx)'),
    ],
    'sections': [
        {
            'id': 'why', 'title': 'Why write API tests in TypeScript', 'emoji': '🎯', 'level': 'Basic',
            'blocks': [
                ('p', 'Imagine a team of ten testers sharing one test suite for a payments API. The backend renames <code>amount</code> to <code>amountPaise</code>. In plain JavaScript, every test that reads <code>amount</code> quietly gets <code>undefined</code>, and some assertions even pass by accident. In TypeScript, you update the <code>Payment</code> type once and the type checker lists every line that must change, before a single test runs.'),
                ('table', ['What TypeScript adds', 'What it means in daily work'], [
                    ['Types for requests and responses', 'Autocomplete for every field, no more guessing names from the docs'],
                    ['Errors before run time', '<code>tsc --noEmit</code> catches typos, missing fields and wrong types in seconds'],
                    ['Safe refactoring', 'Rename a field in one type and the editor updates or flags every use'],
                    ['Typed fixtures and clients', 'A test cannot ask for a fixture that does not exist, or pass a booking where an id is expected'],
                    ['Types from the contract', 'Generate types from the OpenAPI file so tests and API docs never drift apart'],
                ]),
                ('warn', 'Types exist only while you write and check code. They are removed before the code runs, so they cannot check what the server really sent. That is why this track also uses <b>Zod</b>, which checks response bodies at run time.'),
                ('qa', 'Most new Playwright projects in companies are started in TypeScript. If you can read and write typed tests, you can join those teams on day one.'),
            ],
        },
        {
            'id': 'setup', 'title': 'Project setup: packages, tsconfig and config', 'emoji': '🧰', 'level': 'Basic',
            'blocks': [
                ('code', 'bash', 'Terminal', '''
npm init -y
npm install -D @playwright/test@1.64.1 typescript@7.0.2 zod@4.6.7 @types/node@24
npx playwright test                         # run every test
npx tsc --noEmit                            # type check only, writes no files
npx playwright test --grep @smoke           # tagged tests only
BASE_URL=http://localhost:3001 npx playwright test
'''),
                ('code', 'json', 'package.json', '''
{
  "name": "booker-playwright-ts",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "playwright test",
    "typecheck": "tsc --noEmit",
    "ci": "tsc --noEmit && playwright test"
  },
  "devDependencies": {
    "@playwright/test": "1.64.1",
    "@types/node": "^24.0.0",
    "typescript": "7.0.2",
    "zod": "^4.6.7"
  }
}
''', {'save': 'package.json'}),
                ('code', 'json', 'tsconfig.json', '''
{
  "compilerOptions": {
    "target": "es2023",
    "module": "esnext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noEmit": true,
    "allowImportingTsExtensions": true,
    "skipLibCheck": true,
    "types": ["node"]
  },
  "include": ["playwright.config.ts", "src", "tests"]
}
''', {'save': 'tsconfig.json'}),
                ('code', 'ts', 'playwright.config.ts', '''
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
''', {'save': 'playwright.config.ts'}),
                ('code', 'text', 'Folder layout used in this track', '''
booker-playwright-ts/
├── package.json
├── tsconfig.json
├── playwright.config.ts
├── openapi.yaml               the API contract
├── src/
│   ├── models.ts              hand written types
│   ├── schemas.ts             Zod schemas (run time checks)
│   ├── booking-client.ts      typed client class
│   ├── fixtures.ts            typed fixtures
│   └── generated/booker.ts    types generated from openapi.yaml
└── tests/
    ├── first.spec.ts
    ├── crud.spec.ts
    └── ...
'''),
                ('ul', [
                    '<code>"strict": true</code> turns on all the safety checks. TypeScript 7 turns it on by default, but writing it keeps the intent clear for older tools.',
                    '<code>noUncheckedIndexedAccess</code> makes <code>list[0]</code> possibly <code>undefined</code>, which matches reality when an API returns an empty array.',
                    '<code>noEmit</code> means <code>tsc</code> only checks. Playwright runs the <code>.ts</code> files itself.',
                ]),
                ('tip', 'API only projects never need browsers. Skip <code>npx playwright install</code> until you add UI tests.'),
            ],
        },
        {
            'id': 'first-test', 'title': 'Your first typed test: GET a booking', 'emoji': '👋', 'level': 'Basic',
            'blocks': [
                ('code', 'ts', 'tests/first.spec.ts', '''
import { test, expect } from '@playwright/test';

interface Booking {
  firstname: string;
  lastname: string;
  totalprice: number;
  depositpaid: boolean;
  bookingdates: { checkin: string; checkout: string };
  additionalneeds?: string;
}

test('ping says the API is up @smoke', async ({ request }) => {
  const res = await request.get('/ping');
  expect(res.status()).toBe(201);          // Restful Booker answers 201 to a health check
});

test('get one booking', async ({ request }) => {
  const res = await request.get('/booking/1');
  await expect(res).toBeOK();

  const body: Booking = await res.json(); // res.json() returns any, so we state the type we expect
  expect(body.firstname.length).toBeGreaterThan(0);
  expect(body.bookingdates.checkin).toMatch(/^\\d{4}-\\d{2}-\\d{2}$/);
  expect(typeof body.totalprice).toBe('number');
});
''', {'save': 'tests/first.spec.ts'}),
                ('ul', [
                    'Fixtures such as <code>request</code> are fully typed, so the editor shows every method and option.',
                    '<code>res.json()</code> returns <code>any</code>. Writing <code>const body: Booking</code> gives you autocomplete, but it is a promise you make, not a check. The Zod lesson fixes that.',
                    'Mistype <code>body.firstName</code> and <code>npx tsc --noEmit</code> fails with <code>Property \'firstName\' does not exist on type \'Booking\'. Did you mean \'firstname\'?</code>',
                ]),
                ('try', {'method': 'GET', 'path': '/booking/1'}),
            ],
        },
        {
            'id': 'models', 'title': 'Typed models: interfaces, utility types and satisfies', 'emoji': '🧬', 'level': 'Basic',
            'blocks': [
                ('p', 'Put the shapes of your API in one file. Every test imports them, so a change to the API is a change in one place.'),
                ('code', 'ts', 'src/models.ts', '''
export interface BookingDates {
  checkin: string;   // YYYY-MM-DD
  checkout: string;
}

export interface Booking {
  firstname: string;
  lastname: string;
  totalprice: number;
  depositpaid: boolean;
  bookingdates: BookingDates;
  additionalneeds?: string;
}

export interface CreatedBooking {
  bookingid: number;
  booking: Booking;
}

export type BookingPatch = Partial<Booking>;               // every field optional, for PATCH
export type BookingSummary = Pick<Booking, 'firstname' | 'lastname'>;
export type BookingId = { bookingid: number };

export const sampleBooking = {
  firstname: 'Rakesh',
  lastname: 'Panda',
  totalprice: 250,
  depositpaid: true,
  bookingdates: { checkin: '2026-11-01', checkout: '2026-11-04' },
  additionalneeds: 'Breakfast',
} satisfies Booking;
''', {'save': 'src/models.ts'}),
                ('table', ['Utility', 'Gives you', 'Used for'], [
                    ['<code>Partial&lt;T&gt;</code>', 'every field optional', 'PATCH bodies'],
                    ['<code>Pick&lt;T, K&gt;</code>', 'only the listed fields', 'summaries and list items'],
                    ['<code>Omit&lt;T, K&gt;</code>', 'every field except the listed ones', 'a create body without the server made <code>id</code>'],
                    ['<code>Readonly&lt;T&gt;</code>', 'fields that cannot be reassigned', 'shared test data nobody should change by accident'],
                    ['<code>Record&lt;K, V&gt;</code>', 'an object with known keys', 'lookup tables such as status code to message'],
                ]),
                ('why', '<code>satisfies Booking</code> checks the object matches the type but keeps its exact literal types. A misspelt field or a string price is flagged at once, and <code>sampleBooking.firstname</code> is still known to be exactly <code>"Rakesh"</code>.'),
            ],
        },
        {
            'id': 'crud', 'title': 'Create, update and delete (CRUD) with types', 'emoji': '✍️', 'level': 'Basic',
            'blocks': [
                ('code', 'ts', 'tests/crud.spec.ts', '''
import { test, expect } from '@playwright/test';
import { sampleBooking, type Booking, type BookingPatch, type CreatedBooking } from '../src/models';

const basic = 'Basic ' + Buffer.from('admin:password123').toString('base64');

test('create, replace, patch and delete a booking', async ({ request }) => {
  const created: CreatedBooking = await (await request.post('/booking', { data: sampleBooking })).json();
  expect(created.booking).toEqual(sampleBooking);
  const id = created.bookingid;

  const replacement: Booking = { ...sampleBooking, lastname: 'Kumar', totalprice: 300 };
  const put = await request.put(`/booking/${id}`, { headers: { Authorization: basic }, data: replacement });
  expect(await put.json()).toEqual(replacement);

  const change: BookingPatch = { additionalneeds: 'Dinner' };
  const patched: Booking = await (await request.patch(`/booking/${id}`, { headers: { Authorization: basic }, data: change })).json();
  expect(patched).toMatchObject({ ...replacement, ...change });

  expect((await request.delete(`/booking/${id}`, { headers: { Authorization: basic } })).status()).toBe(201);
  expect((await request.get(`/booking/${id}`)).status()).toBe(404);
});
''', {'save': 'tests/crud.spec.ts'}),
                ('tip', '<code>import { type Booking }</code> marks an import as type only. It is removed when the file runs, which keeps run time imports clean and is required by some fast TypeScript runners.'),
                ('try', {'method': 'POST', 'path': '/booking', 'body': {'firstname': 'Rakesh', 'lastname': 'Panda', 'totalprice': 250, 'depositpaid': True, 'bookingdates': {'checkin': '2026-11-01', 'checkout': '2026-11-04'}, 'additionalneeds': 'Breakfast'}}),
            ],
        },
        {
            'id': 'zod', 'title': 'Run time checks with Zod: one schema, one type', 'emoji': '🛡️', 'level': 'Intermediate',
            'blocks': [
                ('p', 'A type tells the editor what you expect. A Zod schema checks what actually arrived. Better still, Zod can produce the type from the schema, so you write the shape once and get both.'),
                ('code', 'ts', 'src/schemas.ts', '''
import { z } from 'zod';

const isoDate = z.string().regex(/^\\d{4}-\\d{2}-\\d{2}$/, 'expected YYYY-MM-DD');

export const BookingSchema = z.object({
  firstname: z.string().min(1),
  lastname: z.string().min(1),
  totalprice: z.number().int().nonnegative(),
  depositpaid: z.boolean(),
  bookingdates: z.object({ checkin: isoDate, checkout: isoDate }),
  additionalneeds: z.string().optional(),
}).strict();                                  // unknown extra fields are an error

export const CreatedSchema = z.object({ bookingid: z.number().int().positive(), booking: BookingSchema });
export const IdListSchema = z.array(z.object({ bookingid: z.number().int() }));
export const TokenSchema = z.object({ token: z.string().min(10) });

export type BookingFromSchema = z.infer<typeof BookingSchema>;   // the type, for free
''', {'save': 'src/schemas.ts'}),
                ('code', 'ts', 'tests/zod.spec.ts', '''
import { test, expect } from '@playwright/test';
import { BookingSchema, IdListSchema, type BookingFromSchema } from '../src/schemas';

test('booking 1 matches the schema', async ({ request }) => {
  const result = BookingSchema.safeParse(await (await request.get('/booking/1')).json());
  expect(result.success, result.error ? JSON.stringify(result.error.issues, null, 2) : '').toBe(true);

  const booking: BookingFromSchema = result.data!;   // fully typed from here on
  expect(booking.bookingdates.checkout >= booking.bookingdates.checkin).toBe(true);
});

test('the list endpoint returns ids only', async ({ request }) => {
  const ids = IdListSchema.parse(await (await request.get('/booking')).json());   // throws on mismatch
  expect(ids.length).toBeGreaterThan(0);
});

test('the schema catches a renamed field', () => {
  const result = BookingSchema.safeParse({
    firstname: 'A', lastname: 'B', totalPrice: 1, depositpaid: true,
    bookingdates: { checkin: '2026-01-01', checkout: '2026-01-02' },
  });
  expect(result.success).toBe(false);
  expect(result.error!.issues.map(i => i.path.join('.'))).toEqual(expect.arrayContaining(['totalprice']));
});
''', {'save': 'tests/zod.spec.ts'}),
                ('ul', [
                    '<code>safeParse</code> returns <code>{ success, data, error }</code> and never throws, so the test can print every issue. <code>parse</code> throws on the first bad body.',
                    '<code>.strict()</code> fails on unknown fields. Use it for contracts you own. Leave it out for third party APIs that may add fields.',
                    'Zod 4 is much faster than Zod 3 and can export a JSON Schema with <code>z.toJSONSchema(BookingSchema)</code>, useful for sharing the contract with Java or Python teams.',
                ]),
                ('tip', 'The third test checks the checker. A schema that never fails is as useless as no schema.'),
            ],
        },
        {
            'id': 'client', 'title': 'A typed client class with generics', 'emoji': '🧱', 'level': 'Intermediate',
            'blocks': [
                ('p', 'A client class hides URLs and headers, so tests read like the business story. With types and Zod, every method returns data that is both checked and typed.'),
                ('code', 'ts', 'src/booking-client.ts', '''
import type { APIRequestContext, APIResponse } from '@playwright/test';
import type { z } from 'zod';
import { BookingSchema, CreatedSchema, IdListSchema, TokenSchema } from './schemas';
import type { Booking, BookingPatch } from './models';

export class ApiError extends Error {
  constructor(readonly status: number, readonly body: string, readonly url: string) {
    super(`${status} from ${url}: ${body.slice(0, 200)}`);
  }
}

async function checked<S extends z.ZodType>(res: APIResponse, schema: S): Promise<z.infer<S>> {
  if (!res.ok()) throw new ApiError(res.status(), await res.text(), res.url());
  return schema.parse(await res.json());
}

export class BookingClient {
  private headers: Record<string, string> = {};

  constructor(private readonly request: APIRequestContext) {}

  async login(username = 'admin', password = 'password123'): Promise<this> {
    const { token } = await checked(await this.request.post('/auth', { data: { username, password } }), TokenSchema);
    this.headers.Cookie = `token=${token}`;
    return this;
  }

  create(data: Booking) { return this.request.post('/booking', { data }).then(r => checked(r, CreatedSchema)); }
  get(id: number) { return this.request.get(`/booking/${id}`).then(r => checked(r, BookingSchema)); }
  find(params: Partial<Record<'firstname' | 'lastname' | 'checkin' | 'checkout', string>>) {
    return this.request.get('/booking', { params }).then(r => checked(r, IdListSchema)).then(list => list.map(b => b.bookingid));
  }
  patch(id: number, data: BookingPatch) {
    return this.request.patch(`/booking/${id}`, { headers: this.headers, data }).then(r => checked(r, BookingSchema));
  }
  remove(id: number): Promise<APIResponse> { return this.request.delete(`/booking/${id}`, { headers: this.headers }); }
  raw(): APIRequestContext { return this.request; }
}
''', {'save': 'src/booking-client.ts'}),
                ('code', 'ts', 'tests/client.spec.ts', '''
import { test, expect } from '@playwright/test';
import { BookingClient, ApiError } from '../src/booking-client';
import { sampleBooking } from '../src/models';

test('create, find, patch and delete through the client', async ({ request }) => {
  const api = await new BookingClient(request).login();
  const { bookingid } = await api.create({ ...sampleBooking, firstname: 'Typed' });

  expect(await api.find({ firstname: 'Typed' })).toContain(bookingid);
  expect((await api.patch(bookingid, { lastname: 'Client' })).lastname).toBe('Client');
  expect((await api.remove(bookingid)).status()).toBe(201);
  await expect(api.get(bookingid)).rejects.toThrow(ApiError);
});
''', {'save': 'tests/client.spec.ts'}),
                ('why', '<code>checked()</code> is generic: give it <code>BookingSchema</code> and the return type is a booking, give it <code>TokenSchema</code> and it is <code>{ token: string }</code>. One helper, every endpoint, no casts.'),
            ],
        },
        {
            'id': 'fixtures', 'title': 'Typed fixtures for clients and test data', 'emoji': '🧷', 'level': 'Intermediate',
            'blocks': [
                ('p', '<code>test.extend</code> takes two type parameters: fixtures created for each test, and fixtures created once per worker. The editor then knows exactly what each test can ask for.'),
                ('code', 'ts', 'src/fixtures.ts', '''
import { test as base, expect } from '@playwright/test';
import { BookingClient } from './booking-client';
import { sampleBooking, type Booking } from './models';

type TestFixtures = {
  api: BookingClient;
  booking: { id: number; data: Booking };
};
type WorkerFixtures = {
  token: string;
};

export const test = base.extend<TestFixtures, WorkerFixtures>({
  token: [async ({ playwright }, use, workerInfo) => {
    const ctx = await playwright.request.newContext({ baseURL: workerInfo.project.use.baseURL });
    const res = await ctx.post('/auth', { data: { username: 'admin', password: 'password123' } });
    const { token } = (await res.json()) as { token: string };
    await use(token);
    await ctx.dispose();
  }, { scope: 'worker' }],

  api: async ({ request }, use) => {
    await use(await new BookingClient(request).login());
  },

  booking: async ({ api }, use) => {
    const data: Booking = { ...sampleBooking, firstname: `Guest${Date.now()}${Math.floor(Math.random() * 1000)}` };
    const { bookingid } = await api.create(data);
    await use({ id: bookingid, data });
    await api.remove(bookingid);           // cleanup runs even when the test fails
  },
});

export { expect };
''', {'save': 'src/fixtures.ts'}),
                ('code', 'ts', 'tests/fixtures.spec.ts', '''
import { test, expect } from '../src/fixtures';

test('read a fresh booking', async ({ api, booking }) => {
  expect((await api.get(booking.id)).firstname).toBe(booking.data.firstname);
});

test('patch with the shared worker token', async ({ request, booking, token }) => {
  const res = await request.patch(`/booking/${booking.id}`, {
    headers: { Cookie: `token=${token}` },
    data: { additionalneeds: 'Late checkout' },
  });
  await expect(res).toBeOK();
});
''', {'save': 'tests/fixtures.spec.ts'}),
                ('tip', 'Ask for a fixture that does not exist, such as <code>async ({ bookng })</code>, and the type checker flags it at once. In JavaScript you would only find out when the test runs and the value is <code>undefined</code>.'),
            ],
        },
        {
            'id': 'data-driven', 'title': 'Data driven tests with typed case tables', 'emoji': '📊', 'level': 'Intermediate',
            'blocks': [
                ('code', 'ts', 'tests/data.spec.ts', '''
import { test, expect } from '../src/fixtures';
import { sampleBooking, type Booking } from '../src/models';

type NameCase = { first: string; last: string; why: string };

const names: NameCase[] = [
  { first: 'Ann', last: 'Lee', why: 'short and plain' },
  { first: 'José', last: 'Núñez', why: 'accents' },
  { first: "O'Brien", last: 'Smith-Jones', why: 'apostrophe and hyphen' },
  { first: 'प्रिया', last: 'शर्मा', why: 'Devanagari script' },
];

for (const { first, last, why } of names) {
  test(`stores the name ${first} ${last} (${why})`, async ({ api }) => {
    const { bookingid, booking } = await api.create({ ...sampleBooking, firstname: first, lastname: last });
    expect(booking.firstname).toBe(first);
    await api.remove(bookingid);
  });
}

const required = ['firstname', 'lastname', 'totalprice', 'depositpaid', 'bookingdates'] as const satisfies readonly (keyof Booking)[];

for (const field of required) {
  test(`missing ${field} is rejected`, async ({ request }) => {
    const { [field]: _removed, ...body } = sampleBooking;
    const res = await request.post('/booking', { data: body });
    expect(res.status(), 'Restful Booker answers 500, a good API answers 400').not.toBe(200);
  });
}
''', {'save': 'tests/data.spec.ts'}),
                ('why', '<code>as const satisfies readonly (keyof Booking)[]</code> means the list can only hold real field names. If the API renames <code>totalprice</code>, this line turns red instead of silently testing a field that no longer exists.'),
            ],
        },
        {
            'id': 'auth', 'title': 'Authentication and negative tests', 'emoji': '🔐', 'level': 'Intermediate',
            'blocks': [
                ('code', 'ts', 'tests/auth.spec.ts', '''
import { test, expect } from '../src/fixtures';

const cases: Array<[name: string, headers: Record<string, string>]> = [
  ['no auth', {}],
  ['made up token', { Cookie: 'token=not-real' }],
  ['wrong password', { Authorization: 'Basic ' + Buffer.from('admin:wrong').toString('base64') }],
];

for (const [name, headers] of cases) {
  test(`update refused with ${name}`, async ({ request, api, booking }) => {
    const res = await request.patch(`/booking/${booking.id}`, { headers, data: { firstname: 'Hacker' } });
    expect(res.status()).toBe(403);
    expect((await api.get(booking.id)).firstname).not.toBe('Hacker');
  });
}

test('bad credentials give no token', async ({ request }) => {
  const body = (await (await request.post('/auth', { data: { username: 'admin', password: 'nope' } })).json()) as { token?: string; reason?: string };
  expect(body.token).toBeUndefined();
  expect(body.reason).toBe('Bad credentials');
});
''', {'save': 'tests/auth.spec.ts'}),
                ('tip', 'Labelled tuple types such as <code>[name: string, headers: Record&lt;string, string&gt;]</code> document each column of a case table and show the labels in editor hints.'),
            ],
        },
        {
            'id': 'openapi', 'title': 'Types generated from the OpenAPI contract', 'emoji': '📜', 'level': 'Advanced',
            'blocks': [
                ('p', 'Hand written types can drift away from the real API. In most companies the backend publishes an OpenAPI file, and the test project generates its types from it. When the contract changes, you regenerate, run <code>tsc</code>, and every affected test is listed.'),
                ('code', 'yaml', 'openapi.yaml (part of the Restful Booker contract)', '''
openapi: 3.1.0
info: { title: Restful Booker, version: 1.0.0 }
paths:
  /booking/{id}:
    get:
      parameters:
        - { name: id, in: path, required: true, schema: { type: integer } }
      responses:
        '200':
          description: One booking
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Booking' }
        '404': { description: Not found }
  /booking:
    post:
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/Booking' }
      responses:
        '200':
          description: Created
          content:
            application/json:
              schema:
                type: object
                required: [bookingid, booking]
                properties:
                  bookingid: { type: integer }
                  booking: { $ref: '#/components/schemas/Booking' }
components:
  schemas:
    Booking:
      type: object
      required: [firstname, lastname, totalprice, depositpaid, bookingdates]
      properties:
        firstname: { type: string }
        lastname: { type: string }
        totalprice: { type: integer }
        depositpaid: { type: boolean }
        bookingdates:
          type: object
          required: [checkin, checkout]
          properties:
            checkin: { type: string, format: date }
            checkout: { type: string, format: date }
        additionalneeds: { type: string }
''', {'save': 'openapi.yaml'}),
                ('code', 'bash', 'Generate the types', '''
npx openapi-typescript@7.13.0 openapi.yaml -o src/generated/booker.ts
'''),
                ('code', 'ts', 'tests/contract-types.spec.ts', '''
import { test, expect } from '@playwright/test';
import type { components, paths } from '../src/generated/booker';

type Booking = components['schemas']['Booking'];
type GetBookingOk = paths['/booking/{id}']['get']['responses']['200']['content']['application/json'];
type CreateBody = NonNullable<paths['/booking']['post']['requestBody']>['content']['application/json'];
type CreateOk = paths['/booking']['post']['responses']['200']['content']['application/json'];

test('create and read back using the generated contract types', async ({ request }) => {
  const body: CreateBody = {
    firstname: 'Spec', lastname: 'First', totalprice: 99, depositpaid: false,
    bookingdates: { checkin: '2026-12-24', checkout: '2026-12-26' },
  };
  const created: CreateOk = await (await request.post('/booking', { data: body })).json();
  const read: GetBookingOk = await (await request.get(`/booking/${created.bookingid}`)).json();

  const same: Booking = read;            // the same component type on both endpoints
  expect(same).toMatchObject(body);
});
''', {'save': 'tests/contract-types.spec.ts'}),
                ('warn', 'openapi-typescript 7.13 still lists TypeScript 5 as its peer dependency, so installing it next to TypeScript 7 fails with a peer dependency error. Running it with <code>npx openapi-typescript@7.13.0</code> keeps it out of your project and avoids the clash. Checking peer dependencies like this is normal work when a big new compiler version arrives.'),
                ('qa', 'Add the generate step to CI and fail the build if <code>src/generated/booker.ts</code> changed but was not committed. That way nobody can change the API contract without the tests noticing.'),
            ],
        },
        {
            'id': 'framework', 'title': 'Framework design: environments, logging and a type gate', 'emoji': '🏗️', 'level': 'Advanced',
            'blocks': [
                ('p', 'Real projects run the same tests against local, QA and staging, keep secrets out of the code, and print useful details when something fails. A small typed config file covers all three.'),
                ('code', 'ts', 'src/config.ts', '''
const ENVS = {
  local: 'http://localhost:3001',
  qa: 'https://qa.booker.example',
  prod: 'https://restful-booker.herokuapp.com',
} as const;

export type EnvName = keyof typeof ENVS;

function pickEnv(value: string | undefined): EnvName {
  if (value && value in ENVS) return value as EnvName;
  if (value) throw new Error(`TEST_ENV must be one of ${Object.keys(ENVS).join(', ')}, got "${value}"`);
  return 'prod';
}

export const env: EnvName = pickEnv(process.env.TEST_ENV);
export const baseURL: string = process.env.BASE_URL ?? ENVS[env];
export const adminPassword: string = process.env.ADMIN_PASSWORD ?? 'password123';   // practice API only
''', {'save': 'src/config.ts'}),
                ('code', 'ts', 'tests/logging.spec.ts', '''
import { test, expect } from '@playwright/test';
import type { APIResponse } from '@playwright/test';

async function attachExchange(name: string, res: APIResponse) {
  const text = await res.text();
  await test.info().attach(name, {
    body: `${res.status()} ${res.url()}\\n${JSON.stringify(res.headers(), null, 2)}\\n\\n${text}`,
    contentType: 'text/plain',
  });
}

test('every response is attached to the report', async ({ request }) => {
  const res = await request.get('/booking/1');
  await attachExchange('GET booking 1', res);        // visible in the HTML report and trace
  await expect(res).toBeOK();
});
''', {'save': 'tests/logging.spec.ts'}),
                ('ul', [
                    'Import <code>baseURL</code> from <code>src/config.ts</code> in <code>playwright.config.ts</code>, then run <code>TEST_ENV=qa npx playwright test</code>.',
                    'Secrets such as <code>ADMIN_PASSWORD</code> come from environment variables locally and from the CI secret store in pipelines. Never commit them.',
                    '<code>test.info().attach</code> adds the status, headers and body to the HTML report, which saves a rerun when a CI test fails.',
                    'Run <code>tsc --noEmit</code> before the tests. A type error should stop the pipeline before any request is sent.',
                ]),
            ],
        },
        {
            'id': 'parallel-ci', 'title': 'Type check, parallel runs and CI', 'emoji': '🚀', 'level': 'Expert',
            'blocks': [
                ('code', 'yaml', '.github/workflows/api-ts.yml', '''
name: API tests (TypeScript)
on: [push, pull_request]
jobs:
  api:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        shard: [1, 2, 3]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 24
          cache: npm
      - run: npm ci
      - run: npx tsc --noEmit                       # stop early on type errors
      - run: npx playwright test --shard ${{ matrix.shard }}/3
        env:
          BASE_URL: ${{ vars.BASE_URL }}
          ADMIN_PASSWORD: ${{ secrets.ADMIN_PASSWORD }}
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: report-${{ matrix.shard }}
          path: playwright-report
'''),
                ('ul', [
                    'TypeScript 7 checks with four parallel workers by default, so <code>tsc --noEmit</code> on a large test repo takes seconds instead of minutes. Use <code>--checkers</code> to change the number.',
                    '<code>--shard 1/3</code> splits the suite across three machines. Worker fixtures still run once per worker on each machine.',
                    'Keep <code>retries</code> low and treat a test that passes only on retry as a bug to fix.',
                ]),
            ],
        },
        {
            'id': 'latest', 'title': 'Latest TypeScript and tool features in real work', 'emoji': '🆕', 'level': 'Expert',
            'blocks': [
                ('table', ['Feature', 'Since', 'How it helps an API tester'], [
                    ['Native compiler written in Go', 'TypeScript 7.0, July 2026', 'Type checks are up to about ten times faster on big projects, so the type gate in CI no longer slows the pipeline. <code>strict</code> is on by default.'],
                    ['<code>satisfies</code>', 'TypeScript 4.9', 'Check test data against a type and keep exact literal values, as in <code>sampleBooking</code>.'],
                    ['<code>using</code> and <code>await using</code>', 'TypeScript 5.2', 'Dispose a request context automatically at the end of a block, even when an assertion throws.'],
                    ['<code>erasableSyntaxOnly</code>', 'TypeScript 5.8', 'Keeps you to syntax that can simply be stripped, which is what lets Node.js run <code>.ts</code> files directly.'],
                    ['Type stripping in Node.js', 'Node.js 22.18 and 24, on by default', '<code>node scripts/seed.ts</code> runs a typed data seeding script with no build step.'],
                    ['Zod 4', '2025', 'Faster parsing, smaller bundles, <code>z.toJSONSchema()</code> to share schemas with other teams.'],
                ]),
                ('code', 'ts', 'tests/dispose.spec.ts', '''
import { test, expect, request as pwRequest } from '@playwright/test';

test('a private request context is disposed automatically', async ({}, testInfo) => {
  await using admin = await pwRequest.newContext({ baseURL: testInfo.project.use.baseURL });
  const res = await admin.post('/auth', { data: { username: 'admin', password: 'password123' } });
  expect((await res.json()).token).toBeTruthy();
  // no admin.dispose() needed: it runs when the block ends, pass or fail
});
''', {'save': 'tests/dispose.spec.ts'}),
                ('code', 'ts', 'src/export-schema.ts (run with: node src/export-schema.ts)', '''
import { z } from 'zod';
import { BookingSchema } from './schemas.ts';

console.log(JSON.stringify(z.toJSONSchema(BookingSchema), null, 2));
''', {'save': 'src/export-schema.ts'}),
                ('tip', 'When you upgrade TypeScript, Playwright or Zod at work, do it on a branch, run <code>tsc --noEmit</code> and the full suite, and read the release notes for removed options. TypeScript 7 turns some old, deprecated settings into hard errors.'),
            ],
        },
        {
            'id': 'scenario', 'title': 'Real world scenario: a hotel front desk day', 'emoji': '🏨', 'level': 'Scenario',
            'blocks': [
                ('p', 'The receptionist logs in, books a room, adds breakfast, and the guest later cancels. Someone without a login also tries to cancel. Every step uses the typed client, so the test reads like the story and every value is checked against the schema.'),
                ('flow', [
                    ('Health check', '<code>GET /ping</code> answers 201.'),
                    ('Log in', 'The <code>api</code> fixture logs in and keeps the token.'),
                    ('Book', '<code>api.create()</code> returns a typed, schema checked booking.'),
                    ('Search', 'The new id appears in <code>api.find({ firstname })</code>.'),
                    ('Add breakfast', '<code>api.patch()</code> with a <code>BookingPatch</code>.'),
                    ('Unauthorised cancel', '<code>DELETE</code> without a token gives 403.'),
                    ('Cancel', '<code>api.remove()</code> gives 201.'),
                    ('Gone', '<code>api.get()</code> rejects with an <code>ApiError</code> of status 404.'),
                ]),
                ('code', 'ts', 'tests/journey.spec.ts', '''
import { test, expect } from '../src/fixtures';
import { ApiError } from '../src/booking-client';
import { sampleBooking } from '../src/models';

test('front desk day', async ({ request, api }) => {
  const guest = `Guest${Date.now()}`;
  let id = 0;

  await test.step('API is up', async () => {
    expect((await request.get('/ping')).status()).toBe(201);
  });

  await test.step('book a room', async () => {
    id = (await api.create({ ...sampleBooking, firstname: guest, additionalneeds: undefined })).bookingid;
  });

  await test.step('find it by name', async () => {
    expect(await api.find({ firstname: guest })).toContain(id);
  });

  await test.step('add breakfast', async () => {
    expect(await api.patch(id, { additionalneeds: 'Breakfast' })).toMatchObject({ firstname: guest, additionalneeds: 'Breakfast' });
  });

  await test.step('cancel without a login is refused', async () => {
    expect((await request.delete(`/booking/${id}`)).status()).toBe(403);
  });

  await test.step('cancel and confirm', async () => {
    expect((await api.remove(id)).status()).toBe(201);
    const err = await api.get(id).catch((e: unknown) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect((err as ApiError).status).toBe(404);
  });
});
''', {'save': 'tests/journey.spec.ts'}),
            ],
        },
    ],
    'quiz': [
        {'lv': 'e', 'q': 'What does <code>npx tsc --noEmit</code> do in this project?', 'o': ['Runs the tests', 'Checks the types without writing any files', 'Deletes compiled files', 'Installs TypeScript'], 'a': 1, 'hint': 'No emit means no output files.', 'why': 'Playwright runs the .ts files itself, so tsc is used only as a fast checker.'},
        {'lv': 'e', 'q': 'Why do we still need Zod when we already have TypeScript types?', 'o': ['Zod makes tests faster', 'Types are removed before the code runs, so only a run time check can see what the server really sent', 'TypeScript cannot describe objects', 'Playwright requires Zod'], 'a': 1, 'hint': 'When do types exist?', 'why': 'Types help while writing code. Zod validates the real response body at run time and gives you the type as well.'},
        {'lv': 'm', 'q': 'Which utility type fits a PATCH body where any field may be sent?', 'o': ['<code>Required&lt;Booking&gt;</code>', '<code>Partial&lt;Booking&gt;</code>', '<code>Readonly&lt;Booking&gt;</code>', '<code>Record&lt;string, Booking&gt;</code>'], 'a': 1, 'hint': 'Every field becomes optional.', 'why': '<code>Partial</code> makes every property optional, which matches a partial update.'},
        {'lv': 'm', 'q': 'What does <code>z.infer&lt;typeof BookingSchema&gt;</code> give you?', 'o': ['A JSON file', 'The TypeScript type described by the schema', 'A random booking', 'A Playwright fixture'], 'a': 1, 'hint': 'One schema, one type.', 'why': 'You write the shape once as a Zod schema and get the matching type for free.'},
        {'lv': 'h', 'q': 'In <code>base.extend&lt;A, B&gt;()</code>, what is <code>B</code>?', 'o': ['Fixtures for each test', 'Fixtures created once per worker', 'Config options', 'Reporter types'], 'a': 1, 'hint': 'The second type parameter.', 'why': 'The first type lists test scoped fixtures and the second lists worker scoped fixtures such as a shared token.'},
        {'lv': 'h', 'q': 'Why install openapi-typescript 7.13 with npx instead of as a dev dependency next to TypeScript 7?', 'o': ['npx is faster', 'Its peer dependency still asks for TypeScript 5, so installing it beside TypeScript 7 fails', 'It only works on Windows', 'It is not on npm'], 'a': 1, 'hint': 'Look at peer dependencies.', 'why': 'Running the generator with npx keeps its own TypeScript out of your project and avoids the peer clash.'},
        {'lv': 'x', 'q': 'What does <code>as const satisfies readonly (keyof Booking)[]</code> guarantee for a list of field names?', 'o': ['Nothing at run time or compile time', 'Every entry must be a real Booking field, and the exact names are kept', 'The fields are sent in that order', 'The list is sorted'], 'a': 1, 'hint': 'Two keywords, two jobs.', 'why': '<code>as const</code> keeps the literal names and <code>satisfies</code> checks each one is a key of Booking, so a renamed field turns red.'},
        {'lv': 'x', 'q': 'What does <code>await using admin = await request.newContext()</code> add?', 'o': ['Parallel requests', 'The context is disposed automatically when the block ends, even if an assertion fails', 'Retries', 'A trace file'], 'a': 1, 'hint': 'Explicit resource management.', 'why': '<code>await using</code> calls the async dispose method at the end of the scope, so no context leaks between tests.'},
    ],
}
