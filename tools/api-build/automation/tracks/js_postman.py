import json

# Scripts are written once here, shown on the page, and also placed into the collection file
# that the last lesson exports, so what learners read is exactly what Newman runs.

PING_TEST = '''
pm.test("API is up", () => {
    pm.response.to.have.status(201);
});
'''

AUTH_TEST = '''
pm.test("Login gives a token", () => {
    pm.response.to.have.status(200);
    const body = pm.response.json();
    pm.expect(body.token, "token").to.be.a("string").and.not.be.empty;
    pm.collectionVariables.set("token", body.token);
});
'''

CREATE_PRE = '''
// Build fresh, unique test data before the request is sent
const guest = "Guest" + Date.now();
pm.collectionVariables.set("guest", guest);
pm.collectionVariables.set("checkin", "2026-11-01");
pm.collectionVariables.set("checkout", "2026-11-04");
'''

CREATE_BODY = '''{
  "firstname": "{{guest}}",
  "lastname": "Panda",
  "totalprice": 250,
  "depositpaid": true,
  "bookingdates": { "checkin": "{{checkin}}", "checkout": "{{checkout}}" },
  "additionalneeds": "Breakfast"
}'''

CREATE_TEST = '''
const body = pm.response.json();

pm.test("Status is 200", () => pm.response.to.have.status(200));
pm.test("Has a booking id", () => pm.expect(body.bookingid).to.be.a("number").above(0));
pm.test("Stored what we sent", () => {
    pm.expect(body.booking.firstname).to.eql(pm.collectionVariables.get("guest"));
    pm.expect(body.booking.bookingdates).to.eql({
        checkin: pm.collectionVariables.get("checkin"),
        checkout: pm.collectionVariables.get("checkout")
    });
});

pm.collectionVariables.set("bookingId", body.bookingid);
'''

SCHEMA_TEST = '''
const schema = {
    type: "object",
    required: ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"],
    properties: {
        firstname: { type: "string", minLength: 1 },
        lastname: { type: "string" },
        totalprice: { type: "integer", minimum: 0 },
        depositpaid: { type: "boolean" },
        bookingdates: {
            type: "object",
            required: ["checkin", "checkout"],
            properties: {
                checkin: { type: "string", pattern: "^\\\\d{4}-\\\\d{2}-\\\\d{2}$" },
                checkout: { type: "string", pattern: "^\\\\d{4}-\\\\d{2}-\\\\d{2}$" }
            }
        },
        additionalneeds: { type: "string" }
    }
};

pm.test("Status is 200", () => pm.response.to.have.status(200));
pm.test("Matches the booking schema", () => pm.response.to.have.jsonSchema(schema));
pm.test("Answered in under 2 seconds", () => pm.expect(pm.response.responseTime).to.be.below(2000));
pm.test("JSON content type", () => pm.response.to.have.header("Content-Type"));
pm.test("Content type is JSON", () => pm.expect(pm.response.headers.get("Content-Type")).to.include("application/json"));
'''

SEARCH_TEST = '''
pm.test("Search finds the new booking", () => {
    const ids = pm.response.json().map(b => b.bookingid);
    pm.expect(ids).to.include(pm.collectionVariables.get("bookingId"));
});
'''

PATCH_TEST = '''
const body = pm.response.json();
pm.test("Breakfast added", () => pm.expect(body.additionalneeds).to.eql("Breakfast and dinner"));
pm.test("Other fields unchanged", () => pm.expect(body.lastname).to.eql("Panda"));
'''

FORBIDDEN_TEST = '''
pm.test("Delete without a token is refused", () => pm.response.to.have.status(403));
'''

DELETE_TEST = '''
pm.test("Deleted (this API answers 201)", () => pm.response.to.have.status(201));
'''

GONE_TEST = '''
pm.test("Booking is gone", () => pm.response.to.have.status(404));
pm.test("Body is plain text", () => pm.expect(pm.response.text()).to.eql("Not Found"));
'''

COLLECTION_TEST = '''
// Runs after every request in the collection
pm.test("No server errors", () => pm.expect(pm.response.code).to.be.below(500));
'''


def _script(listen, src):
    return {'listen': listen, 'script': {'type': 'text/javascript', 'exec': src.strip('\n').split('\n')}}


def _req(name, method, path, test, pre=None, body=None, auth=False):
    item = {'name': name, 'event': [], 'request': {'method': method, 'header': [{'key': 'Accept', 'value': 'application/json'}], 'url': '{{baseUrl}}' + path}}
    if pre:
        item['event'].append(_script('prerequest', pre))
    item['event'].append(_script('test', test))
    if body:
        item['request']['header'].append({'key': 'Content-Type', 'value': 'application/json'})
        item['request']['body'] = {'mode': 'raw', 'raw': body, 'options': {'raw': {'language': 'json'}}}
    if auth:
        item['request']['header'].append({'key': 'Cookie', 'value': 'token={{token}}'})
    return item


COLLECTION = json.dumps({
    'info': {'name': 'Restful Booker: front desk journey', 'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'},
    'variable': [{'key': 'baseUrl', 'value': 'https://restful-booker.herokuapp.com'}],
    'event': [_script('test', COLLECTION_TEST)],
    'item': [
        _req('Ping', 'GET', '/ping', PING_TEST),
        _req('Log in', 'POST', '/auth', AUTH_TEST, body='{\n  "username": "admin",\n  "password": "password123"\n}'),
        _req('Create booking', 'POST', '/booking', CREATE_TEST, pre=CREATE_PRE, body=CREATE_BODY),
        _req('Get booking', 'GET', '/booking/{{bookingId}}', SCHEMA_TEST),
        _req('Search by name', 'GET', '/booking?firstname={{guest}}', SEARCH_TEST),
        _req('Add breakfast', 'PATCH', '/booking/{{bookingId}}', PATCH_TEST, body='{\n  "additionalneeds": "Breakfast and dinner"\n}', auth=True),
        _req('Delete without token', 'DELETE', '/booking/{{bookingId}}', FORBIDDEN_TEST),
        _req('Delete booking', 'DELETE', '/booking/{{bookingId}}', DELETE_TEST, auth=True),
        _req('Confirm gone', 'GET', '/booking/{{bookingId}}', GONE_TEST),
    ],
}, indent=2, ensure_ascii=False)

ENVIRONMENT = json.dumps({
    'name': 'local',
    'values': [{'key': 'baseUrl', 'value': 'http://localhost:3001', 'enabled': True}],
}, indent=2)

DATA_CSV = '''firstname,lastname,totalprice,expected
Ann,Lee,100,200
José,Núñez,250,200
O'Brien,Smith-Jones,0,200
'''

DATA_TEST = '''
const row = pm.iterationData;           // the current row of the data file

pm.test(`Row ${pm.info.iteration + 1}: status ${row.get("expected")}`, () => {
    pm.response.to.have.status(Number(row.get("expected")));
});

pm.test("Name stored exactly", () => {
    pm.expect(pm.response.json().booking.firstname).to.eql(row.get("firstname"));
});
'''

DATA_BODY = '''{
  "firstname": "{{firstname}}",
  "lastname": "{{lastname}}",
  "totalprice": {{totalprice}},
  "depositpaid": true,
  "bookingdates": { "checkin": "2026-12-01", "checkout": "2026-12-03" }
}'''

DATA_COLLECTION = json.dumps({
    'info': {'name': 'Restful Booker: data driven create', 'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'},
    'variable': [{'key': 'baseUrl', 'value': 'https://restful-booker.herokuapp.com'}],
    'item': [_req('Create from data row', 'POST', '/booking', DATA_TEST, body=DATA_BODY)],
}, indent=2, ensure_ascii=False)


TRACK = {
    'id': 'js-postman', 'lang': 'js', 'tool': 'postman',
    'title': 'Postman with JavaScript', 'emoji': '📮',
    'tagline': 'From manual requests to automated collections with JavaScript tests, run anywhere with Newman.',
    'intro': 'Postman is where most testers send their first API request. It becomes an automation tool once you add <b>JavaScript test scripts</b> to each request, connect requests with <b>variables</b>, and run the whole <b>collection</b> from the command line with <b>Newman</b> or the Postman CLI. Scripts use the <code>pm</code> object and Chai style <code>pm.expect</code> assertions.',
    'stack': [
        ('Postman app', 'v11 or newer', 'Scripts tab with Pre-request and Post-response'),
        ('Newman', '6.2.3', 'free CLI runner for collections'),
        ('Node.js', '22 LTS or newer', 'needed by Newman'),
        ('Chai', 'built in', '<code>pm.expect</code> assertions'),
        ('Ajv', 'built in', '<code>jsonSchema</code> checks'),
    ],
    'sections': [
        {
            'id': 'why', 'title': 'From manual requests to automated tests', 'emoji': '🎯', 'level': 'Basic',
            'blocks': [
                ('p', 'An API test sends a request and checks the response. In Postman you already send requests by hand. Automation adds three things: a <b>script</b> that checks each response, <b>variables</b> that pass values between requests, and a <b>runner</b> that plays the whole collection in order without clicks.'),
                ('table', ['Postman part', 'What it is'], [
                    ['Collection', 'A folder of saved requests that run in order. This is your test suite.'],
                    ['Environment', 'A set of variables such as <code>baseUrl</code> for dev, QA or staging.'],
                    ['Pre-request script', 'JavaScript that runs before the request, for example to build test data.'],
                    ['Post-response script', 'JavaScript that runs after, with <code>pm.test</code> checks. Older versions call this the Tests tab.'],
                    ['Collection Runner', 'Runs a collection inside the app, optionally with a data file.'],
                    ['Newman and Postman CLI', 'Run a collection from the terminal or CI.'],
                ]),
                ('qa', 'This is the friendliest path from manual to automated API testing. You keep the requests you already trust and add checks one at a time.'),
            ],
        },
        {
            'id': 'setup', 'title': 'Setup: workspace, environment and Newman', 'emoji': '🧰', 'level': 'Basic',
            'blocks': [
                ('ol', [
                    'Install the Postman app and create a workspace.',
                    'Create a collection called <b>Restful Booker</b>.',
                    'Open the collection, go to <b>Variables</b>, and add <code>baseUrl</code> with the value <code>https://restful-booker.herokuapp.com</code>.',
                    'Create an environment called <b>local</b> with <code>baseUrl</code> set to another server when you need one. An environment value wins over a collection value.',
                    'Install Node.js, then Newman, so collections can run from the terminal.',
                ]),
                ('code', 'bash', 'Terminal', '''
npm install -g newman
newman --version

# export the collection from Postman (... > Export > v2.1), then:
newman run booker.postman_collection.json
newman run booker.postman_collection.json -e local.postman_environment.json
newman run booker.postman_collection.json --env-var baseUrl=http://localhost:3001
'''),
                ('code', 'json', 'local.postman_environment.json', ENVIRONMENT, {'save': 'local.postman_environment.json'}),
            ],
        },
        {
            'id': 'first-test', 'title': 'Your first request with a test', 'emoji': '👋', 'level': 'Basic',
            'blocks': [
                ('p', 'Create a request <code>GET {{baseUrl}}/ping</code>. Open <b>Scripts</b>, then <b>Post-response</b>, and add the script below. Press Send, then open <b>Test Results</b> under the response.'),
                ('code', 'js', 'Ping: Post-response script', PING_TEST),
                ('p', 'Now add <code>GET {{baseUrl}}/booking/1</code> with this script. Each <code>pm.test</code> becomes one line in the results with a pass or fail mark.'),
                ('code', 'js', 'Get booking: Post-response script', '''
pm.test("Status is 200", () => {
    pm.response.to.have.status(200);
});

pm.test("Body is JSON with a first name", () => {
    pm.response.to.be.json;
    const body = pm.response.json();
    pm.expect(body.firstname).to.be.a("string").and.not.be.empty;
});

pm.test("Fast enough", () => {
    pm.expect(pm.response.responseTime).to.be.below(2000);
});
'''),
                ('tip', 'The snippets list on the right of the script editor inserts common checks with one click, such as status code and response time. They are a good way to learn the <code>pm</code> API.'),
                ('try', {'method': 'GET', 'path': '/booking/1'}),
            ],
        },
        {
            'id': 'variables', 'title': 'Variables and their scopes', 'emoji': '🧮', 'level': 'Basic',
            'blocks': [
                ('p', 'Write <code>{{name}}</code> anywhere in a URL, header or body and Postman replaces it before sending. In scripts you read and write variables with <code>pm</code>.'),
                ('table', ['Scope', 'Lives in', 'Read and write in scripts', 'Use for'], [
                    ['Global', 'the workspace', '<code>pm.globals</code>', 'rarely, values for every collection'],
                    ['Collection', 'one collection', '<code>pm.collectionVariables</code>', 'ids and tokens passed between requests'],
                    ['Environment', 'the selected environment', '<code>pm.environment</code>', 'base URL and users per server'],
                    ['Data', 'the current data file row', '<code>pm.iterationData</code>', 'data driven runs'],
                    ['Local', 'one request run', '<code>pm.variables</code>', 'temporary values'],
                ]),
                ('p', 'When the same name exists in several scopes, the narrowest wins: local, then data, then environment, then collection, then global. <code>pm.variables.get(name)</code> follows this order for you.'),
                ('warn', 'Mark secrets such as passwords as <b>secret</b> type in the environment, and do not commit exported environments that contain real secrets.'),
            ],
        },
        {
            'id': 'crud', 'title': 'CRUD requests and chaining with variables', 'emoji': '🔗', 'level': 'Basic',
            'blocks': [
                ('p', 'Each request saves what the next one needs. The login stores <code>token</code>, the create stores <code>bookingId</code>, and later requests use <code>{{token}}</code> and <code>{{bookingId}}</code>.'),
                ('code', 'js', 'POST {{baseUrl}}/auth: Post-response', AUTH_TEST),
                ('code', 'js', 'POST {{baseUrl}}/booking: Pre-request', CREATE_PRE),
                ('code', 'json', 'POST {{baseUrl}}/booking: Body (raw, JSON)', CREATE_BODY),
                ('code', 'js', 'POST {{baseUrl}}/booking: Post-response', CREATE_TEST),
                ('p', 'For the update and delete requests, add a header <code>Cookie</code> with the value <code>token={{token}}</code>, and use the path <code>/booking/{{bookingId}}</code>.'),
                ('table', ['Request', 'Expected'], [
                    ['<code>PATCH /booking/{{bookingId}}</code> with the token', '200 and the changed field'],
                    ['<code>DELETE /booking/{{bookingId}}</code> without the token', '403'],
                    ['<code>DELETE /booking/{{bookingId}}</code> with the token', '201, a quirk of this API'],
                    ['<code>GET /booking/{{bookingId}}</code>', '404'],
                ]),
                ('try', {'method': 'POST', 'path': '/auth', 'body': {'username': 'admin', 'password': 'password123'}}),
            ],
        },
        {
            'id': 'assertions', 'title': 'Assertions cookbook', 'emoji': '🔍', 'level': 'Intermediate',
            'blocks': [
                ('p', '<code>pm.expect</code> is the Chai assertion library. Chains read like sentences and give clear failure messages.'),
                ('code', 'js', 'Checks you will use every day', '''
const res = pm.response;
const body = res.json();

pm.test("Status family", () => pm.expect(res.code).to.be.within(200, 299));
pm.test("Exact status", () => res.to.have.status(200));
pm.test("Status text", () => res.to.have.status("OK"));
pm.test("Header present", () => res.to.have.header("Content-Type"));
pm.test("Header value", () => pm.expect(res.headers.get("Content-Type")).to.include("application/json"));
pm.test("Time", () => pm.expect(res.responseTime).to.be.below(1000));
pm.test("Size", () => pm.expect(res.responseSize).to.be.below(5000));

pm.test("Types", () => {
    pm.expect(body.firstname).to.be.a("string");
    pm.expect(body.totalprice).to.be.a("number").and.to.be.at.least(0);
    pm.expect(body.depositpaid).to.be.a("boolean");
});
pm.test("Keys", () => pm.expect(body).to.have.all.keys("firstname", "lastname", "totalprice", "depositpaid", "bookingdates", "additionalneeds"));
pm.test("Nested", () => pm.expect(body).to.have.nested.property("bookingdates.checkin").that.matches(/^\\d{4}-\\d{2}-\\d{2}$/));
pm.test("Deep equal", () => pm.expect(body.bookingdates).to.deep.include({ checkin: "2026-01-01" }));
pm.test("One of", () => pm.expect(body.additionalneeds).to.be.oneOf(["Breakfast", "Lunch", "Dinner", undefined]));

// Arrays
const list = [{ bookingid: 1 }, { bookingid: 2 }];
pm.test("Every id positive", () => list.forEach(b => pm.expect(b.bookingid).to.be.above(0)));
pm.test("Contains id 2", () => pm.expect(list.map(b => b.bookingid)).to.include(2));
'''),
                ('tip', 'A failed <code>pm.expect</code> inside one <code>pm.test</code> does not stop the other tests in the script, so one run shows every problem.'),
            ],
        },
        {
            'id': 'auth', 'title': 'Authorization tab and auth scripts', 'emoji': '🔐', 'level': 'Intermediate',
            'blocks': [
                ('p', 'Set auth once on the collection or a folder, then choose <b>Inherit auth from parent</b> on each request. Postman supports the common types directly.'),
                ('table', ['Auth type', 'Fill in', 'Sends'], [
                    ['Basic Auth', '<code>admin</code> and <code>{{password}}</code>', '<code>Authorization: Basic ...</code> on every request'],
                    ['Bearer Token', '<code>{{accessToken}}</code>', '<code>Authorization: Bearer ...</code>'],
                    ['API Key', 'key name, value, header or query', 'for example <code>x-api-key</code>'],
                    ['OAuth 2.0', 'token URL, client id and secret, scope', 'gets and refreshes tokens for you'],
                ]),
                ('p', 'For a token that must be fetched first, a collection level <b>Pre-request</b> script can log in automatically when no token is stored yet, using <code>pm.sendRequest</code>.'),
                ('code', 'js', 'Collection Pre-request: log in once', '''
if (!pm.collectionVariables.get("token")) {
    pm.sendRequest({
        url: pm.variables.get("baseUrl") + "/auth",
        method: "POST",
        header: { "Content-Type": "application/json" },
        body: { mode: "raw", raw: JSON.stringify({ username: "admin", password: pm.environment.get("password") }) }
    }, (err, res) => {
        if (err) { console.error(err); return; }
        pm.collectionVariables.set("token", res.json().token);
    });
}
'''),
                ('h', 'Negative checks for every protected request'),
                ('ul', [
                    'Duplicate the request, remove the token, and expect 403 or 401.',
                    'Set the token to a made up value and expect a refusal.',
                    'After a refused update, GET the record and check nothing changed.',
                ]),
            ],
        },
        {
            'id': 'data-driven', 'title': 'Data driven runs with CSV or JSON', 'emoji': '📊', 'level': 'Intermediate',
            'blocks': [
                ('p', 'Run the same requests once per row of a data file. Column names become variables, so <code>{{firstname}}</code> in the body is filled from the row. In scripts, read the row with <code>pm.iterationData</code>.'),
                ('code', 'plain', 'bookings.csv', DATA_CSV, {'save': 'bookings.csv'}),
                ('code', 'json', 'POST {{baseUrl}}/booking: Body', DATA_BODY),
                ('code', 'js', 'Post-response', DATA_TEST),
                ('code', 'bash', 'Run it', '''
# In the app: Runner > choose the collection > Select File > bookings.csv > Run
newman run data.postman_collection.json -d bookings.csv
'''),
                ('code', 'json', 'data.postman_collection.json', DATA_COLLECTION, {'save': 'data.postman_collection.json'}),
                ('qa', 'Data files are a simple way to hand test design to the whole team. Testers add rows for boundary values and special characters without touching any script.'),
            ],
        },
        {
            'id': 'schema', 'title': 'JSON Schema checks', 'emoji': '📐', 'level': 'Advanced',
            'blocks': [
                ('p', '<code>pm.response.to.have.jsonSchema(schema)</code> validates the body with Ajv, which is built into the Postman sandbox. One schema check replaces many field checks and catches renamed or retyped fields.'),
                ('code', 'js', 'GET {{baseUrl}}/booking/{{bookingId}}: Post-response', SCHEMA_TEST),
                ('tip', 'Store large schemas in a collection variable or a Postman package and load them with <code>JSON.parse(pm.collectionVariables.get("bookingSchema"))</code>, so many requests share one schema.'),
            ],
        },
        {
            'id': 'flow-control', 'title': 'Controlling the run: setNextRequest, skips and loops', 'emoji': '🔀', 'level': 'Advanced',
            'blocks': [
                ('p', 'By default the runner plays requests from top to bottom. Scripts can change that.'),
                ('code', 'js', 'Jump, stop, skip and poll', '''
// After this request, jump to a request by name
pm.execution.setNextRequest("Delete booking");

// Stop the run after this request
pm.execution.setNextRequest(null);

// In a Pre-request script: skip this request entirely
if (!pm.collectionVariables.get("bookingId")) {
    pm.execution.skipRequest();
}

// Poll: repeat this request until the job is done, at most 10 times
const tries = Number(pm.collectionVariables.get("tries") || 0) + 1;
pm.collectionVariables.set("tries", tries);
if (pm.response.json().status !== "DONE" && tries < 10) {
    pm.execution.setNextRequest(pm.info.requestName);
} else {
    pm.collectionVariables.unset("tries");
}
'''),
                ('warn', 'Jumps only work in the Collection Runner, Newman and the Postman CLI, not when you press Send on a single request. Always add a limit to loops.'),
            ],
        },
        {
            'id': 'newman', 'title': 'Newman: reporters, options and running from Node', 'emoji': '🖥️', 'level': 'Advanced',
            'blocks': [
                ('code', 'bash', 'Useful options', '''
newman run booker.postman_collection.json \\
  -e qa.postman_environment.json \\
  --folder "Smoke" \\
  --iteration-count 3 \\
  --delay-request 100 \\
  --timeout-request 10000 \\
  --bail \\
  --reporters cli,junit \\
  --reporter-junit-export reports/newman.xml

# Prettier HTML report
npm install -g newman-reporter-htmlextra
newman run booker.postman_collection.json -r cli,htmlextra --reporter-htmlextra-export reports/report.html
'''),
                ('p', 'Newman is also a Node library, so you can run collections from a script and decide what to do with the results.'),
                ('code', 'js', 'run-collection.mjs', '''
import newman from "newman";

newman.run({
    collection: "./booker.postman_collection.json",
    envVar: [{ key: "baseUrl", value: process.env.BASE_URL ?? "https://restful-booker.herokuapp.com" }],
    reporters: ["cli"]
}, (err, summary) => {
    if (err) throw err;
    const failed = summary.run.failures.length;
    console.log(`${summary.run.stats.assertions.total} assertions, ${failed} failed`);
    process.exitCode = failed ? 1 : 0;
});
''', {'save': 'run-collection.mjs'}),
                ('tip', 'The official <b>Postman CLI</b> (<code>postman collection run</code>) can run collections stored in your Postman workspace and send results back to Postman. Newman runs exported files and needs no account.'),
            ],
        },
        {
            'id': 'ci', 'title': 'CI, monitors and mock servers', 'emoji': '🚀', 'level': 'Expert',
            'blocks': [
                ('code', 'yaml', '.github/workflows/postman.yml', '''
name: Postman API tests
on: [push, pull_request]
jobs:
  api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm install -g newman
      - run: >
          newman run postman/booker.postman_collection.json
          --env-var baseUrl=${{ vars.BASE_URL }}
          --env-var password=${{ secrets.BOOKER_PASSWORD }}
          --reporters cli,junit --reporter-junit-export reports/newman.xml
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: newman-report
          path: reports
'''),
                ('ul', [
                    'Keep exported collections in Git so changes are reviewed like code.',
                    '<b>Monitors</b> run a collection on a schedule from Postman\'s cloud and alert you when checks fail. Good for production health checks.',
                    '<b>Mock servers</b> answer requests with saved examples. Front end developers and testers can work before the real API exists.',
                    'Import an <b>OpenAPI</b> spec to generate a collection with every endpoint, then add tests to it.',
                ]),
            ],
        },
        {
            'id': 'expert', 'title': 'Expert habits for large collections', 'emoji': '🧠', 'level': 'Expert',
            'blocks': [
                ('ul', [
                    '<b>Reuse code</b>: put shared helpers in the collection Pre-request or Post-response script, or in a <b>package</b> from the Package Library loaded with <code>pm.require</code>.',
                    '<b>One folder per feature</b>, each with its own setup and cleanup requests, so folders can run alone with <code>--folder</code>.',
                    '<b>Self cleaning</b>: every collection deletes what it creates, even when checks fail, by putting cleanup requests last and never stopping early with <code>--bail</code> in nightly runs.',
                    '<b>Unique data</b>: use <code>Date.now()</code> or dynamic variables such as <code>{{$randomFirstName}}</code> and <code>{{$guid}}</code> so parallel runs never collide.',
                    '<b>Contract first</b>: validate every response against the OpenAPI schema so the collection fails when the API drifts from its documentation.',
                    '<b>Know the limits</b>: Postman is great for functional checks and smoke suites. For thousands of tests, complex logic or load testing, a code based framework or a load tool fits better.',
                ]),
                ('code', 'js', 'Collection level Post-response: shared checks for every request', COLLECTION_TEST),
            ],
        },
        {
            'id': 'scenario', 'title': 'Real world scenario: the front desk collection', 'emoji': '🏨', 'level': 'Scenario',
            'blocks': [
                ('p', 'A receptionist logs in, books a room, the guest adds breakfast, someone without a login tries to cancel, and finally the booking is cancelled. Here is the full collection, built from the scripts in the earlier lessons. Save it as a file and run it with Newman.'),
                ('flow', [
                    ('Ping', 'Checks the API answers 201.'),
                    ('Log in', 'Saves <code>token</code>.'),
                    ('Create booking', 'Pre-request makes a unique guest name. Saves <code>bookingId</code>.'),
                    ('Get booking', 'Schema, time and header checks.'),
                    ('Search by name', 'The new id is in the results.'),
                    ('Add breakfast', 'PATCH with the token cookie.'),
                    ('Delete without token', 'Must give 403.'),
                    ('Delete booking', 'With the token, gives 201.'),
                    ('Confirm gone', 'GET gives 404.'),
                ]),
                ('code', 'json', 'booker.postman_collection.json', COLLECTION, {'save': 'booker.postman_collection.json'}),
                ('code', 'bash', 'Run it', 'newman run booker.postman_collection.json'),
                ('qa', 'Import this file into Postman with <b>Import</b>, then run it in the Collection Runner to see every test result in the app.'),
            ],
        },
    ],
    'quiz': [
        {'lv': 'e', 'q': 'Where do you write checks that run after the response arrives?', 'o': ['Pre-request script', 'Post-response script', 'Headers tab', 'Body tab'], 'a': 1, 'hint': 'Older versions called it the Tests tab.', 'why': 'The Post-response script runs after the response, so it can read <code>pm.response</code> and run <code>pm.test</code> checks.'},
        {'lv': 'e', 'q': 'Which line checks for status 200?', 'o': ['<code>pm.status(200)</code>', '<code>pm.response.to.have.status(200)</code>', '<code>pm.expect(200)</code>', '<code>response.code = 200</code>'], 'a': 1, 'hint': 'It reads like a sentence.', 'why': '<code>pm.response.to.have.status(200)</code> is the built in status assertion.'},
        {'lv': 'm', 'q': 'A variable <code>baseUrl</code> exists in both the collection and the selected environment. Which value is used?', 'o': ['Collection', 'Environment', 'Global', 'Neither, it errors'], 'a': 1, 'hint': 'The narrower scope wins.', 'why': 'Order from narrow to wide: local, data, environment, collection, global. The environment value wins.'},
        {'lv': 'm', 'q': 'How do you pass a new booking id to later requests?', 'o': ['Copy it by hand', '<code>pm.collectionVariables.set("bookingId", body.bookingid)</code> then use <code>{{bookingId}}</code>', 'Put it in the Headers tab', 'Newman does it automatically'], 'a': 1, 'hint': 'Save it in a variable.', 'why': 'Saving to a variable in the Post-response script makes it available as <code>{{bookingId}}</code> everywhere.'},
        {'lv': 'h', 'q': 'Which command runs a collection once per row of <code>bookings.csv</code>?', 'o': ['<code>newman run c.json -e bookings.csv</code>', '<code>newman run c.json -d bookings.csv</code>', '<code>newman run c.json --folder bookings.csv</code>', '<code>newman data bookings.csv</code>'], 'a': 1, 'hint': 'd for data.', 'why': '<code>-d</code> (or <code>--iteration-data</code>) runs one iteration per row. <code>-e</code> is for environments.'},
        {'lv': 'h', 'q': 'Why might <code>pm.execution.setNextRequest("Delete booking")</code> seem to do nothing?', 'o': ['The name is case insensitive', 'You pressed Send on one request instead of running the collection', 'It only works in Pre-request', 'It needs a data file'], 'a': 1, 'hint': 'Who decides the next request?', 'why': 'Only a runner (Collection Runner, Newman, Postman CLI) moves between requests. A single Send has no next request.'},
        {'lv': 'x', 'q': 'Your nightly Newman job uses <code>--bail</code>. What risk does it add?', 'o': ['Slower runs', 'A failure stops the run before cleanup requests, leaving test data behind', 'Reports are lost', 'Variables are reset'], 'a': 1, 'hint': 'Where are the cleanup requests?', 'why': '<code>--bail</code> stops at the first failure, so delete requests at the end never run. Keep it for quick smoke runs only.'},
        {'lv': 'x', 'q': 'What makes a collection safe to run in parallel on CI from several branches?', 'o': ['Using global variables', 'Unique test data per run, such as names with Date.now()', 'Turning off tests', 'Running with --bail'], 'a': 1, 'hint': 'Think about collisions.', 'why': 'Unique data means two runs never search, change or delete each other\'s bookings.'},
    ],
}
