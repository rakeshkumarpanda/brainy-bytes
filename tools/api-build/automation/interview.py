"""Interview questions for API Automation Testing, shown with assets/interview.js at the end of the page.

Every question has a hint, a short model answer, key points and a detailed explanation. The learner
writes an answer first, can open the hint, and then opens the full answer.
"""


def Q(id, topic, lv, q, hint, answer, explain, **more):
    """One question. Optional: kind, points, code, acode, lang, follow."""
    item = dict(id=id, topic=topic, lv=lv, q=q, hint=hint, answer=answer, explain=explain)
    item.update({k: v for k, v in more.items() if v})
    return item


MUST = [
    ['🔁', 'Status codes and methods', 'Know what 200, 201, 204, 400, 401, 403, 404, 409, 422, 429 and 500 mean, and which methods are safe and idempotent.'],
    ['🔐', 'Authentication', 'Tokens, cookies, Basic auth, OAuth 2 and how you test that a protected endpoint really refuses bad credentials.'],
    ['🔗', 'Chaining and test data', 'Extracting an id or token from one response and using it in the next call, with data each test owns and cleans up.'],
    ['📐', 'Schema and contract testing', 'JSON Schema, OpenAPI and consumer driven contracts catch breaking changes that value checks miss.'],
    ['🏗️', 'Framework design', 'Client classes, fixtures, config per environment, reporting and how you keep a large suite readable.'],
    ['🧪', 'Positive, negative and edge cases', 'Missing fields, wrong types, boundaries, duplicates and bad auth find most real API bugs.'],
    ['🚀', 'CI, parallel runs and flaky tests', 'How the suite runs on every commit, why tests must be independent, and how you find and fix flakiness.'],
    ['🧰', 'Your chosen tool in depth', 'Rest Assured, Playwright, requests with pytest, Postman with Newman or fetch. Expect detailed questions on the one on your CV.'],
]

ITEMS = [
    # ---------- Fundamentals ----------
    Q('what-is-api-testing', 'Fundamentals', 'e',
      'What is API testing, and why do teams automate it?',
      'Think about the layer between the UI and the database, and about speed.',
      'API testing sends requests straight to an application programming interface and checks the responses, without a user interface. Teams automate it because API tests are fast, stable and can run on every commit.',
      'The UI calls the same APIs that mobile apps and partner systems call, so testing at this layer checks the business logic once for every client. API tests usually take milliseconds, do not break when a button moves, and can reach edge cases that are hard to reach through screens. That is why they form the large middle layer of the test pyramid. Automation lets the team run hundreds of these checks in CI on every pull request, so a broken contract is caught before it reaches other teams.',
      kind='Concept',
      points=['No UI, only HTTP requests and responses', 'Faster and more stable than UI tests', 'Checks business rules for every client at once', 'Runs in CI on every change'],
      follow=['Where do API tests sit in the test pyramid?', 'What can an API test find that a UI test cannot?']),
    Q('what-to-check', 'Fundamentals', 'e',
      'What do you check in the response of an API call?',
      'There are more parts to a response than the body.',
      'The status code, the body values and structure, the important headers, the response time, and the side effects such as the data really being saved.',
      'A good API test checks several layers. The status code tells you the outcome. The body must have the right values, types and shape, which a JSON Schema check covers well. Headers such as Content-Type, Cache-Control, Location and security headers matter to clients. Response time catches performance regressions. Finally, a test should confirm side effects, for example reading a booking back after creating it, because an API can answer 200 and still fail to store the data.',
      kind='Concept',
      points=['Status code', 'Body values, types and schema', 'Headers such as Content-Type and Location', 'Response time', 'Side effects, by reading the data back']),
    Q('positive-negative', 'Fundamentals', 'e',
      'What are positive and negative API tests? Give an example of each for a create booking endpoint.',
      'One proves it works with good input, the other proves it fails safely with bad input.',
      'A positive test sends valid data and expects success, for example a full booking that returns 200 with a new id. A negative test sends invalid data or bad credentials and expects a clean failure, for example a booking without a lastname that returns 400.',
      'Positive tests prove the happy path works. Negative tests prove the API protects itself and its data. For a create endpoint, negative cases include missing required fields, wrong types such as a price sent as text, values out of range, an empty body, a malformed JSON body, an unsupported Content-Type and missing or wrong auth. The expected result is a 4xx code with a helpful error message and no record created. A 500 for bad input is a bug, because the server should validate input instead of crashing.',
      kind='Concept',
      points=['Positive: valid input, expect success', 'Negative: invalid input or auth, expect a clean 4xx', 'A 500 for bad input is a bug', 'Confirm nothing was saved after a rejected request']),
    Q('status-codes', 'Fundamentals', 'm',
      'Explain the difference between 401 and 403, and between 400 and 422.',
      'One pair is about who you are versus what you may do. The other pair is about syntax versus meaning.',
      '401 Unauthorized means the server does not know who you are, so credentials are missing or invalid. 403 Forbidden means it knows who you are but you are not allowed. 400 Bad Request means the request itself is malformed, while 422 Unprocessable Content means the syntax is fine but the data breaks a rule.',
      'A 401 should come with a WWW-Authenticate header that tells the client how to log in. A 403 says logging in again will not help, for example a normal user trying to delete another user\'s order. For input errors, 400 suits broken JSON or a missing required parameter, and 422 suits valid JSON that fails validation, such as a checkout date before the checkin date. Many APIs use 400 for both, so the team\'s API guidelines decide. In tests, assert the exact code the contract promises, not just any 4xx.',
      kind='Concept',
      points=['401: who are you', '403: I know you, but no', '400: malformed request', '422: well formed but breaks a rule'],
      follow=['What status would you expect for a duplicate email on sign up?', 'When should an API answer 429?']),
    Q('idempotent', 'Fundamentals', 'm',
      'Which HTTP methods are idempotent, and how would you test idempotency?',
      'Idempotent means sending the same request twice leaves the server in the same state as sending it once.',
      'GET, HEAD, OPTIONS, PUT and DELETE are idempotent. POST is not, and PATCH is not guaranteed to be. To test it, send the same request twice and check that the final state and the stored data are the same as after one call.',
      'Idempotency matters because clients retry when the network fails. If a retried PUT changed data twice, or a retried payment POST charged twice, users would see real harm. A test sends the same PUT twice and compares the stored record after each call. For DELETE, the second call may return 404, which is fine, because the state is still the same. For POST endpoints that must be safe to retry, many APIs accept an Idempotency-Key header, and the test sends two POSTs with the same key and checks that only one record exists.',
      kind='Concept',
      points=['Idempotent: GET, HEAD, OPTIONS, PUT, DELETE', 'Not idempotent: POST, and PATCH is not guaranteed', 'Test: send twice, compare state', 'Idempotency-Key makes a POST safe to retry']),
    Q('put-patch', 'Fundamentals', 'e',
      'What is the difference between PUT and PATCH?',
      'One sends the whole resource.',
      'PUT replaces the whole resource with the body you send. PATCH changes only the fields you send and keeps the rest.',
      'With PUT, a missing field usually means the field is removed or the request is rejected, so tests send the complete object. With PATCH, a body with one field changes only that field. A good PATCH test checks both the changed field and that the untouched fields kept their old values. In Restful Booker, PUT needs every booking field while PATCH accepts just additionalneeds.',
      kind='Concept',
      points=['PUT: full replacement', 'PATCH: partial update', 'Test that PATCH keeps the other fields']),
    Q('chaining', 'Fundamentals', 'm',
      'What is request chaining? Show how you would chain a login and an update.',
      'The output of one call becomes the input of the next.',
      'Chaining means taking a value from one response, such as a token or an id, and using it in a later request. For example, call POST /auth, read the token from the body, then send it as a cookie in PUT /booking/{id}.',
      'Real workflows are chains, so tests must be too. The important habits are to assert each step before using its output, so a failure points at the right step, and to keep the extracted value in a local variable or fixture rather than a global, so parallel tests do not overwrite each other\'s values. In Postman this is a collection variable set in a post response script. In code it is a normal variable, a fixture or a field on a client object.',
      kind='Coding', lang='py',
      acode='''token = api.post("/auth", data={"username": "admin", "password": "password123"}).json()["token"]
res = api.put(f"/booking/{booking_id}", headers={"Cookie": f"token={token}"}, data=updated)
assert res.status == 200''',
      points=['Extract, store, reuse', 'Assert every step before using its output', 'Keep values local to the test for parallel safety']),

    # ---------- HTTP and REST in tests ----------
    Q('rest-principles', 'HTTP and REST', 'm',
      'What makes an API RESTful, and what would you check to confirm it follows REST?',
      'Resources, methods, statelessness and status codes.',
      'A RESTful API exposes resources at URLs, uses HTTP methods for actions, is stateless so each request carries everything it needs, and uses standard status codes and media types.',
      'In practice you check that nouns are in the path and verbs are the methods, for example GET /bookings/42 rather than GET /getBooking?id=42. Creating returns 201 with a Location header pointing at the new resource. Each request is independent, so the same call with the same token gives the same answer on any server. Collections support filtering and paging through query parameters. Errors use proper 4xx and 5xx codes with a consistent error body. Responses that can be cached say so through headers such as ETag and Cache-Control.',
      kind='Concept',
      points=['Resources as nouns in URLs', 'Methods as verbs', 'Stateless requests', 'Correct status codes, 201 plus Location on create', 'Consistent error format']),
    Q('headers-matter', 'HTTP and REST', 'm',
      'Which request and response headers do you check in API tests, and why?',
      'Think about content, auth, caching, tracing and security.',
      'Content-Type and Accept for the format, Authorization or Cookie for auth, Location after a create, Cache-Control and ETag for caching, a correlation or request id for tracing, and security headers such as Strict-Transport-Security.',
      'A response with the right body but Content-Type text/html will break clients that parse JSON. A create that returns no Location header forces clients to guess where the new resource lives. Wrong caching headers can serve one user\'s data to another through a proxy. Request ids let you find the failing call in server logs. Security headers and the absence of Server version banners are often part of a security checklist. Header names are case insensitive, so assert in a way that ignores case.',
      kind='Concept'),
    Q('pagination', 'HTTP and REST', 'h',
      'How would you test pagination on GET /orders?',
      'Boundaries, totals, overlap and stable ordering.',
      'Check the first, middle and last pages, page size limits, an empty page past the end, invalid values such as page=-1 or size=0, that no item appears twice or goes missing across pages, and that the total count matches.',
      'Create a known number of records first, for example 25 orders, so the expected numbers are certain. With size 10 you expect pages of 10, 10 and 5, and an empty list on page 4. Collect the ids from every page and check there are 25 unique ids, which catches overlap and gaps. Check the maximum size the API allows and what happens above it. Test sorting together with paging, because an unstable sort makes items jump between pages. For cursor based paging, follow the next cursor until it ends and check the same rules.',
      kind='Scenario',
      points=['Known data first', 'First, middle, last and beyond the last page', 'No duplicates or gaps across pages', 'Invalid and maximum page sizes', 'Stable sort order']),
    Q('graphql', 'HTTP and REST', 'h',
      'How is testing a GraphQL API different from testing a REST API?',
      'Look at the status code GraphQL returns when a query fails.',
      'GraphQL usually has one endpoint and returns 200 even when a query fails, with the problems listed in an errors array. So tests must check the body for errors, not only the status. Tests also cover query depth and cost limits, field level authorization and schema changes.',
      'In REST each resource has its own URL and status codes carry meaning. In GraphQL every call is a POST to /graphql with a query and variables. A test that only asserts 200 will pass for a broken query. Other areas to test include partial data with errors, nullability rules, introspection being disabled in production, deeply nested queries that could overload the server, and a user who can read a type but not one sensitive field on it. Schema diff tools in CI catch removed fields that would break clients.',
      kind='Concept',
      acode='''res = api.post("/graphql", data={"query": "query($id: ID!) { booking(id: $id) { firstname } }", "variables": {"id": 1}})
body = res.json()
assert res.status == 200
assert "errors" not in body, body.get("errors")
assert body["data"]["booking"]["firstname"]''', lang='py'),
    Q('rate-limit', 'HTTP and REST', 'h',
      'How would you test rate limiting?',
      'Send more requests than allowed and look at the code and the headers.',
      'Send requests above the limit inside the window and expect 429 Too Many Requests, usually with a Retry-After header. Then wait for the window to pass and check that requests succeed again. Also check that the limit is per user or per key as designed.',
      'Read the documented limit first, for example 100 requests per minute per API key. Send 100 requests and expect success, then the 101st should get 429. Check headers such as Retry-After and any X-RateLimit-Remaining counters. Use two different keys to prove one user cannot use up another user\'s quota. Run these tests against a dedicated environment or with a low test limit, because hitting a shared limit can break other teams\' tests.',
      kind='Scenario'),

    # ---------- Framework design ----------
    Q('framework-layers', 'Framework design', 'm',
      'Describe how you would structure an API automation framework from scratch.',
      'Think in layers: config, client, data, tests, reporting.',
      'Config per environment, a client layer with one method per endpoint, models or schemas for request and response bodies, test data builders and fixtures that clean up, the tests themselves with only steps and assertions, and reporting plus CI.',
      'Config holds base URLs, credentials from environment variables and timeouts, so the same tests run on dev, staging and production like environments. The client layer hides paths, headers and auth, so a renamed endpoint is fixed in one place. Models or schemas define the contract. Builders make valid data with sensible defaults and let a test change one field. Fixtures or hooks create and delete data so tests are independent. Tests read like business steps. Reporting such as Allure or the Playwright HTML report, plus a CI pipeline with parallel runs and artifacts, finish the picture.',
      kind='Design',
      points=['Environment config and secrets from env vars', 'Client or service layer per API', 'Models and schemas', 'Data builders and fixtures with cleanup', 'Readable tests', 'Reports and CI'],
      follow=['How do you share a token across tests without making them depend on each other?', 'Where do assertions belong, in the client or in the test?']),
    Q('test-data', 'Framework design', 'm',
      'How do you manage test data in API automation?',
      'Who creates the data, who owns it, and who deletes it.',
      'Each test creates the data it needs through the API, uses unique values, and deletes it afterwards in a teardown or fixture. Shared reference data is read only. Secrets come from environment variables.',
      'Hard coded ids such as booking 1 break when someone else changes or deletes that record, especially in shared environments that reset. Creating data in a fixture gives every test a clean known state and lets tests run in parallel. Unique values, for example a UUID in the name, stop collisions. Cleanup runs in a finally block, an @AfterEach method, or after yield in pytest, so it runs even when the test fails. For large data sets, a seed script or database snapshot before the run is faster than API calls.',
      kind='Design'),
    Q('flaky', 'Framework design', 'h',
      'Your API suite fails randomly in CI about once in ten runs. How do you find and fix the cause?',
      'Most flakiness comes from shared state, timing or the environment.',
      'Rerun the failing test many times alone and in parallel to reproduce it, read the logs or traces of the failed runs, then look for shared data, order dependence, timing assumptions about asynchronous work, and unstable environments. Fix the root cause instead of adding retries.',
      'Run with repeat options such as pytest-repeat, Playwright --repeat-each or a loop in CI to make the failure show up. Run the test alone. If it then passes, it depends on another test. Typical causes are tests sharing one record, a static token or variable overwritten by a parallel thread, asserting immediately on data that is processed in the background, relying on list order, and a shared environment that other teams reset. Fixes are unique data per test, thread safe or per test state, polling with a timeout instead of sleep, sorting before comparing, and a dedicated environment or mocks for unstable dependencies. Retries can hide real race conditions in the product, so treat them only as a short term measure and track every flaky test as a bug.',
      kind='Scenario',
      points=['Reproduce with repeated and isolated runs', 'Check shared data and test order', 'Poll instead of sleep for async work', 'Fix the cause, keep retries temporary']),
    Q('environments', 'Framework design', 'e',
      'How do you run the same API tests against dev, QA and staging?',
      'Nothing environment specific should be inside the test code.',
      'Keep the base URL, credentials and other settings outside the tests, in environment variables or one config file per environment, and select the environment with a variable or command line option at run time.',
      'Examples are BASE_URL=https://qa.example.com pytest, pytest --base-url, a Maven profile with -Denv=qa, a Playwright project per environment, or a Postman environment file passed to Newman with -e. Secrets such as passwords and API keys come from the CI secret store and are never committed. Tests that must not run in a given environment, for example destructive tests in production, are tagged and excluded there.',
      kind='Concept'),
    Q('mock-vs-real', 'Framework design', 'h',
      'When would you mock an API in your tests, and when would you test the real one?',
      'Think about what each kind of test is trying to prove.',
      'Mock a dependency when you test your own service or client and need fast, repeatable control over its answers, including errors and timeouts. Test the real API when the goal is to prove the integration and the contract actually work.',
      'Mocks with tools such as WireMock, responses, respx, MSW or Playwright route handlers let you simulate a 500, a slow reply or malformed JSON on demand, which is hard with a real system. But mocks can drift from reality, so a test suite that only mocks gives false confidence. A healthy strategy has unit and component tests with mocks, contract tests that keep the mocks honest, and a smaller set of end to end API tests against a real deployed environment.',
      kind='Design'),

    # ---------- Rest Assured ----------
    Q('ra-given-when-then', 'Rest Assured', 'e',
      'Explain the given, when, then structure in Rest Assured with an example.',
      'Arrange, act, assert.',
      'given() sets up the request with base URI, headers, auth and body. when() sends it with a method and path. then() checks the response with status, body and header matchers.',
      'This BDD style makes tests read like a specification. Hamcrest matchers such as equalTo, hasItem and notNullValue check values at JSON paths. Adding log().ifValidationFails() prints the request and response only when the test fails, which keeps CI logs short but useful.',
      kind='Coding', lang='java',
      acode='''given()
    .baseUri("https://restful-booker.herokuapp.com")
    .accept(ContentType.JSON)
.when()
    .get("/booking/1")
.then()
    .log().ifValidationFails()
    .statusCode(200)
    .body("firstname", notNullValue())
    .body("bookingdates.checkin", matchesPattern("\\\\d{4}-\\\\d{2}-\\\\d{2}"));''',
      points=['given: request setup', 'when: method and path', 'then: assertions', 'log().ifValidationFails() for readable failures']),
    Q('ra-spec', 'Rest Assured', 'm',
      'What are RequestSpecification and ResponseSpecification, and why use them?',
      'Think about repeated setup across many tests.',
      'They are reusable bundles of request settings and response checks. A RequestSpecBuilder holds the base URI, content type, filters and auth once, and a ResponseSpecBuilder holds common checks such as content type and response time.',
      'Without specs every test repeats the same given() lines, and changing the base URI means editing hundreds of tests. With specs, tests call given().spec(requestSpec) and then(). spec(responseSpec). You can have one spec per role or per service. Filters added to the request spec, such as logging or Allure filters, then apply to every test.',
      kind='Coding', lang='java',
      acode='''RequestSpecification requestSpec = new RequestSpecBuilder()
    .setBaseUri(System.getenv().getOrDefault("BASE_URL", "https://restful-booker.herokuapp.com"))
    .setContentType(ContentType.JSON)
    .addFilter(new AllureRestAssured())
    .build();

ResponseSpecification ok = new ResponseSpecBuilder()
    .expectStatusCode(200)
    .expectContentType(ContentType.JSON)
    .expectResponseTime(lessThan(2000L))
    .build();

given().spec(requestSpec).when().get("/booking/1").then().spec(ok);'''),
    Q('ra-extract', 'Rest Assured', 'm',
      'How do you extract a value from a response in Rest Assured and use it in the next request?',
      'There is a method called extract().',
      'Call extract() after then(), and read the value with path(), jsonPath() or as() for a POJO. Store it in a variable and pass it to the next request.',
      'extract().path("bookingid") is quick for one value. extract().jsonPath() gives typed getters like getInt and getList. extract().as(BookingResponse.class) maps the whole body to a Java object with Jackson, which is cleaner for many fields. Assert the status in then() before extract(), so a failed create does not hand a null id to the next step.',
      kind='Coding', lang='java',
      acode='''int id = given().spec(requestSpec).body(booking)
    .when().post("/booking")
    .then().statusCode(200)
    .extract().path("bookingid");

given().spec(requestSpec).cookie("token", token)
    .when().delete("/booking/" + id)
    .then().statusCode(201);'''),
    Q('ra-pojo', 'Rest Assured', 'm',
      'How do you send and read Java objects instead of JSON strings in Rest Assured?',
      'Serialization and deserialization with a JSON library on the classpath.',
      'Pass a POJO or record to body(), and Rest Assured serializes it with Jackson or Gson. Read a response with extract().as(MyClass.class) to deserialize it.',
      'This gives compile time checks on field names and keeps tests readable. Builders or factory methods create valid objects with defaults. For negative tests that need invalid JSON, such as a wrong type or a missing field, use a Map or a raw string instead, because the POJO cannot express broken data. Configure Jackson to fail on unknown properties in contract tests if new fields should be noticed.',
      kind='Concept'),
    Q('ra-schema', 'Rest Assured', 'h',
      'How do you validate a JSON schema in Rest Assured?',
      'There is a separate module for it.',
      'Add the json-schema-validator module, put the schema file on the classpath, and assert with body(matchesJsonSchemaInClasspath("schemas/booking.json")).',
      'The schema checks types, required fields, formats and extra properties in one assertion, which value checks alone miss. Keep schemas in sync with the OpenAPI file, ideally generated from it. Include a test that proves the schema fails on bad data, otherwise a schema that is too loose passes everything.',
      kind='Coding', lang='java',
      acode='''given().spec(requestSpec)
.when().get("/booking/1")
.then().statusCode(200)
    .body(matchesJsonSchemaInClasspath("schemas/booking.json"));'''),
    Q('ra-auth', 'Rest Assured', 'm',
      'What is the difference between auth().basic() and auth().preemptive().basic() in Rest Assured?',
      'When is the password sent?',
      'auth().basic() waits for the server to answer 401 with a challenge and then sends the credentials. preemptive().basic() sends the Authorization header with the first request.',
      'Many APIs never send a 401 challenge. Restful Booker answers 403, for example, so the non preemptive form never sends the password and the test fails with 403. Preemptive auth avoids the extra round trip as well. Other options are auth().oauth2(token) for a bearer token and a plain header("Authorization", ...) when you need full control.',
      kind='Concept'),
    Q('ra-parallel', 'Rest Assured', 'x',
      'Your Rest Assured tests pass alone but fail when TestNG runs them in parallel. What could be wrong?',
      'Look for anything static.',
      'Shared mutable state, usually static fields such as RestAssured.baseURI, a static token or a static booking id that parallel threads overwrite, or tests that share the same data.',
      'RestAssured static configuration is global, so one test changing RestAssured.basePath affects every running thread. Use RequestSpecification objects per test or per class instead. Keep tokens and ids in local variables, in ThreadLocal, or in data providers. Make each test create its own data. Check that listeners and reporting filters are thread safe. Then run with parallel="methods" and a thread count, and repeat the run several times to confirm the fix.',
      kind='Scenario',
      points=['Avoid static RestAssured settings in tests', 'Use RequestSpecification per test', 'Local or ThreadLocal state', 'Own data per test']),

    # ---------- Playwright ----------
    Q('pw-request-context', 'Playwright', 'e',
      'How do you test an API with Playwright without opening a browser?',
      'There is a request object that is not a page.',
      'Use an APIRequestContext, either the built in request fixture in Playwright Test for JavaScript, playwright.request.new_context() in Python, or playwright.request().newContext() in Java. It sends HTTP calls with a base URL and default headers, and no browser starts.',
      'The context holds the base URL, extra headers, cookies, timeouts and HTTP credentials. In JavaScript, configure baseURL and extraHTTPHeaders in playwright.config.js and use the request fixture. In Python, create one context in a session fixture and dispose it at the end. In Java, create it in @BeforeAll and dispose it in @AfterAll. Because no browser is launched, playwright install is not needed for API only projects.',
      kind='Concept',
      acode='''@pytest.fixture(scope="session")
def api(playwright, base_url):
    ctx = playwright.request.new_context(base_url=base_url, extra_http_headers={"Accept": "application/json"})
    yield ctx
    ctx.dispose()''', lang='py'),
    Q('pw-ui-api', 'Playwright', 'm',
      'Give three ways Playwright lets you combine API calls with UI tests.',
      'Setup, verification and mocking.',
      'Create test data through the API before the UI steps, wait for and assert on the API calls the page makes, and mock API responses with route handlers to test UI error states. A fourth is logging in once through the API and reusing the storage state.',
      'page.request shares cookies with the browser, so seeding data or calling protected endpoints works as the signed in user. waitForResponse in JavaScript or expect_response in Python captures a response and its request, so you can check the JSON the page sent. page.route can fulfill a call with a 500 or slow it down to test spinners and error messages. Storage state saved after an API login makes every UI test start signed in, which removes the slowest steps of a UI suite.',
      kind='Concept'),
    Q('pw-tobeok', 'Playwright', 'e',
      'What does expect(response).toBeOK() check in Playwright, and why is it better than checking status equals 200?',
      'It accepts a range, and it helps you on failure.',
      'It passes for any status from 200 to 299, and when it fails it prints the response, which shows the error body the server sent.',
      'A plain status assertion only says expected 200 but got 400. toBeOK shows the message from the server, such as which field failed validation, so failures in CI are quicker to diagnose. In Python the same check is expect(res).to_be_ok(). When the exact code matters, such as 201 for a create, assert the exact status as well.',
      kind='Concept'),
    Q('pw-timeouts-units', 'Playwright', 'm',
      'A Python tester moves from requests to Playwright and writes timeout=10. Their tests now fail with timeouts. Why?',
      'Compare the units of the two libraries.',
      'requests measures timeouts in seconds, while Playwright measures them in milliseconds. timeout=10 in Playwright means 10 milliseconds.',
      'The fix is timeout=10_000. The same trap applies to Java, where setTimeout takes milliseconds. It is worth setting a default timeout on the context with new_context(timeout=10_000) so individual calls do not need it. Also note that in Python the response status is a property, res.status, not a method.',
      kind='Scenario', lang='py',
      code='''res = api.get("/reports/monthly", timeout=10)''',
      acode='''res = api.get("/reports/monthly", timeout=10_000)   # 10 seconds''',),
    Q('pw-workers', 'Playwright', 'h',
      'How many times does a worker scoped login fixture run in Playwright Test with four workers, and why does that matter?',
      'Workers are separate processes.',
      'It runs once per worker, so up to four times. Each worker process keeps its own token. That is fine for most APIs, but it matters when logins are rate limited or a token is single use.',
      'Worker fixtures are the right place for expensive setup that tests can share without changing it, such as a login token or an API client. Test data that a test changes should be test scoped instead. If the identity provider allows only one active session per user, give each worker its own test user, using workerInfo.workerIndex in JavaScript or the xdist worker id in Python.',
      kind='Concept'),

    # ---------- Python ----------
    Q('py-fixture-yield', 'Python', 'e',
      'What does the code after yield in a pytest fixture do?',
      'Think about cleanup.',
      'It is the teardown. pytest runs it after the test that used the fixture finishes, whether the test passed or failed.',
      'Everything before yield is setup, and the yielded value is what the test receives. This is the cleanest place to delete test data, close sessions and dispose Playwright contexts. Fixture scope decides when teardown runs: after each test for function scope, after the file for module scope, and at the end of the run for session scope.',
      kind='Concept', lang='py',
      acode='''@pytest.fixture
def booking(api, token):
    res = api.post("/booking", data=new_booking())
    booking_id = res.json()["bookingid"]
    yield booking_id
    api.delete(f"/booking/{booking_id}", headers={"Cookie": f"token={token}"})'''),
    Q('py-json-data', 'Python', 'e',
      'In requests, what is the difference between json= and data=?',
      'One sets the Content-Type to application/json.',
      'json= serializes a dict to JSON and sets Content-Type: application/json. data= sends form encoded fields for a dict, or the raw body for a string or bytes.',
      'Sending a dict with data= to a JSON API is a classic bug. The server receives firstname=Sally&lastname=Brown and usually answers 400 or 500. Note that Playwright for Python is the opposite, where data= sends a dict as JSON and form= sends form fields, so check which library you are in.',
      kind='Concept'),
    Q('py-timeout', 'Python', 'm',
      'Why should every requests call in a test pass a timeout?',
      'What is the default?',
      'requests has no default timeout, so a call to a server that never answers can hang forever and block the whole CI job.',
      'Pass timeout=(connect, read) such as (3, 10), or wrap requests in a Session subclass or client class that adds a default. pytest-timeout can add a safety net per test as well. Hanging jobs are worse than failing ones, because they hide every other result until CI kills them.',
      kind='Concept'),
    Q('py-parametrize', 'Python', 'm',
      'How do you run the same API test with many data sets in pytest?',
      'There is a decorator for it.',
      'Use @pytest.mark.parametrize with the argument names and a list of values. pytest creates one test per row, and ids or pytest.param make the names readable.',
      'Each row is a separate test, so one bad row does not hide the others, and pytest-xdist can run rows in parallel. For larger data, load a CSV or JSON file at import time and pass its rows to parametrize. Parametrized fixtures with params= suit cases where the setup itself changes, such as running every test for two user roles.',
      kind='Coding', lang='py',
      acode='''@pytest.mark.parametrize("path, status", [
    pytest.param("/ping", 201, id="health"),
    pytest.param("/booking/999999", 404, id="missing"),
])
def test_status(api, path, status):
    assert api.get(path).status == status'''),
    Q('py-session', 'Python', 'm',
      'Why use requests.Session instead of calling requests.get directly in a framework?',
      'Connections and shared settings.',
      'A Session reuses TCP and TLS connections, which is faster, and keeps headers, cookies and auth for every call made through it.',
      'Setting the base headers and auth once on a session removes repetition and mistakes. Connection pooling can cut response times noticeably when a suite makes thousands of calls. Cookies set by a login are sent automatically on later calls, which matches how a browser behaves. A Session is not guaranteed to be thread safe, so give each thread or xdist worker its own.',
      kind='Concept'),
    Q('py-async', 'Python', 'x',
      'When would you use httpx or the async Playwright API instead of requests in API tests?',
      'Many calls at once.',
      'When you need many calls in flight at the same time, for example seeding hundreds of records, testing concurrent updates, or quick load checks. Async clients with asyncio.gather send them concurrently in one thread.',
      'requests is synchronous, so 100 calls take 100 round trips one after another. With httpx.AsyncClient or playwright.async_api, the calls overlap and finish in roughly the time of the slowest ones. This also makes race conditions testable, such as two clients booking the last room at once. httpx is also useful when the application under test is a Python ASGI app, because it can call the app in process without a network.',
      kind='Concept'),

    # ---------- Postman and Newman ----------
    Q('pm-variables', 'Postman', 'e',
      'Explain the variable scopes in Postman and which one wins.',
      'From global down to the closest scope.',
      'Postman has global, collection, environment, data and local variables. When names clash, the narrowest scope wins: local beats data, data beats environment, environment beats collection, and collection beats global.',
      'Use environment variables for things that change between dev, QA and staging, such as baseUrl. Use collection variables for values shared by the requests in one collection, such as a token set in a post response script. Data variables come from a CSV or JSON file in the Collection Runner or Newman. Avoid globals in shared work, because they leak between collections.',
      kind='Concept'),
    Q('pm-tests', 'Postman', 'e',
      'Write a Postman test that checks the status is 200 and saves the token from the body.',
      'pm.test, pm.response and pm.collectionVariables.',
      'Use pm.test with pm.response.to.have.status(200), read the body with pm.response.json(), and save the token with pm.collectionVariables.set.',
      'Each pm.test appears as a named check in the runner and in Newman reports. Asserting before saving prevents an empty token from breaking later requests silently.',
      kind='Coding', lang='js',
      acode='''pm.test("Status is 200", () => pm.response.to.have.status(200));

const body = pm.response.json();
pm.test("Token is present", () => pm.expect(body.token).to.be.a("string").and.not.empty);
pm.collectionVariables.set("token", body.token);'''),
    Q('pm-newman', 'Postman', 'm',
      'How do you run a Postman collection in a CI pipeline?',
      'Postman has a command line runner.',
      'Export the collection and environment, or reference them from the Postman API, and run them with Newman, for example newman run collection.json -e qa.json --reporters cli,junit. The pipeline fails when any test fails.',
      'Newman exits with a non zero code when tests fail, which fails the CI step. The JUnit reporter feeds CI dashboards, and htmlextra makes a readable HTML report. Data driven runs use -d data.csv with -n for iterations. Secrets should come from CI variables passed with --env-var instead of being saved in the exported environment file. The Postman CLI is the newer official alternative with similar options.',
      kind='Concept',
      acode='''newman run booker.postman_collection.json \\
  -e qa.postman_environment.json \\
  --env-var "password=$BOOKER_PASSWORD" \\
  -d guests.csv \\
  --reporters cli,junit --reporter-junit-export results/newman.xml''', lang='js'),
    Q('pm-limits', 'Postman', 'h',
      'What are the limits of Postman for a large automation suite, and when would you move to code?',
      'Think about reuse, review and version control.',
      'Postman is great for exploring and for small to medium suites, but large suites suffer from copy pasted scripts, hard code review of JSON exports, limited reuse and harder debugging. A code based framework fits better when the suite grows, needs complex data and logic, or must share code with other tests.',
      'Collection level scripts and package libraries help, but logic still lives in many small script tabs. Diffs of exported JSON are hard to review in pull requests. Complex setup, database checks, retries and custom reporting are easier in a real language with an IDE, debugger and unit tests. Many teams keep Postman for exploration, contract examples and quick smoke checks with Newman, and use Rest Assured, Playwright or pytest for the main regression suite.',
      kind='Design'),

    # ---------- JavaScript native ----------
    Q('js-fetch-errors', 'JavaScript', 'm',
      'Does fetch throw an error when the server answers 404 or 500?',
      'What does res.ok tell you?',
      'No. fetch only rejects on network failures such as a refused connection or a timeout. For 404 or 500 it resolves normally, and you must check res.status or res.ok yourself.',
      'This surprises many testers moving from Axios, which throws on 4xx and 5xx by default. In tests that is useful, because you can assert any status directly. In helper code that expects success, add a check such as if (!res.ok) throw new Error(...) with the status and body text. Use AbortSignal.timeout(10_000) for a time limit, because fetch has no default timeout either.',
      kind='Concept', lang='js',
      acode='''const res = await fetch(`${BASE}/booking/999999`, { signal: AbortSignal.timeout(10_000) });
assert.equal(res.ok, false);
assert.equal(res.status, 404);'''),
    Q('js-node-test', 'JavaScript', 'm',
      'How do you write and run API tests with only Node.js and no extra packages?',
      'Node ships its own test runner and assertion module.',
      'Use the built in node:test module for describe, test and hooks, node:assert/strict for assertions, and the global fetch for HTTP. Run them with node --test.',
      'Since Node 18, fetch is global, and node:test has become stable with before and after hooks, subtests, test filtering, concurrency options, watch mode and reporters such as spec and junit. This is ideal for small services and teams that want zero dependencies to maintain. For schema checks you would still add Ajv, and for larger suites Playwright Test or Jest give richer reporting.',
      kind='Coding', lang='js',
      acode='''import { test } from 'node:test';
import assert from 'node:assert/strict';

test('ping', async () => {
  const res = await fetch(`${process.env.BASE_URL}/ping`);
  assert.equal(res.status, 201);
});'''),
    Q('js-async-mistake', 'JavaScript', 'h',
      'This test always passes, even when the API is down. What is wrong?',
      'Look at what the test function returns.',
      'The promise is not awaited, so the test finishes before the request completes and any failure happens after the test has already passed.',
      'Without await, fetch starts, the function returns, and the runner sees no error. The assertion runs later, if at all, and its error may show as an unhandled rejection or nowhere. Always make the test function async and await every request and json() call. Linters such as the no-floating-promises rule catch this automatically.',
      kind='Output', lang='js',
      code='''test('booking exists', () => {
  fetch(`${BASE}/booking/1`).then(res => assert.equal(res.status, 200));
});''',
      acode='''test('booking exists', async () => {
  const res = await fetch(`${BASE}/booking/1`);
  assert.equal(res.status, 200);
});'''),

    # ---------- Schema and contracts ----------
    Q('schema-why', 'Schema and contracts', 'm',
      'Why add JSON Schema validation when you already assert on values?',
      'Values change, shapes should not.',
      'A schema checks the whole structure in one place: required fields, types, formats, enums and unexpected extra fields. Value assertions usually cover only the few fields a test cares about, so a renamed or retyped field elsewhere slips through.',
      'For example, totalprice changing from a number to a string breaks mobile clients but passes a test that only checks firstname. A schema catches it instantly. Generate schemas from the OpenAPI specification where possible, so tests and docs share one source of truth. Decide deliberately whether additionalProperties is false, which catches unexpected new fields, or allowed, which avoids failures when the API adds fields on purpose.',
      kind='Concept'),
    Q('contract-testing', 'Schema and contracts', 'x',
      'What is consumer driven contract testing, and how is it different from schema validation?',
      'Who writes the expectations, and who runs them?',
      'In consumer driven contract testing, each consumer records the requests it makes and the parts of the responses it relies on as a contract, for example with Pact. The provider then runs those contracts in its own pipeline before releasing. Schema validation checks one response against one schema, but does not know which fields each consumer actually uses.',
      'Contract tests answer the question whether this provider change will break any real consumer, without a shared end to end environment. A broker stores contracts and verification results, and a can-i-deploy check blocks a release that would break a consumer. Schema tests remain useful for general shape checks and for APIs with unknown or public consumers. The two approaches complement each other.',
      kind='Concept'),
    Q('openapi', 'Schema and contracts', 'h',
      'How can an OpenAPI specification help your API automation?',
      'It is a machine readable contract.',
      'You can validate responses against its schemas, generate client code and test data, run property based tools such as Schemathesis that create many requests from it, detect breaking changes by diffing versions, and find endpoints that have no tests.',
      'The specification lists every path, method, parameter, request body, response code and schema. Tools turn that into value: schema validators in tests, generated typed clients, fuzzing that finds 500 errors from unexpected input, coverage reports that compare the spec to what tests actually call, and CI checks such as oasdiff that flag removed fields or new required parameters before release.',
      kind='Concept'),

    # ---------- CI and reporting ----------
    Q('ci-pipeline', 'CI and reporting', 'm',
      'Describe how your API tests run in CI.',
      'Trigger, environment, run, report, notify.',
      'On every pull request the pipeline installs dependencies, runs a fast smoke set against a test environment or a containerised service, runs the full regression in parallel on merge or nightly, publishes JUnit and HTML reports as artifacts, and fails the build on any failed test.',
      'Secrets such as API keys come from the CI secret store. The base URL is a variable per environment. A smoke tag gives quick feedback in a few minutes, while the full suite can be sharded across machines. Reports such as Allure, the Playwright HTML report or Newman htmlextra are kept as artifacts with traces and logs for failed tests. Results go to the team chat, and failures block the merge.',
      kind='Design'),
    Q('ci-parallel', 'CI and reporting', 'h',
      'What must be true about your tests before you run them in parallel?',
      'Independence.',
      'Each test must be independent: it creates its own data, does not rely on other tests or on order, does not share mutable state such as static variables, and cleans up after itself.',
      'Parallel runners such as TestNG with parallel methods, JUnit 5 parallel execution, pytest-xdist and Playwright workers run tests at the same time in any order. Shared bookings, a static token that one test refreshes while another uses it, or a test that expects a list to contain exactly three items will fail randomly. Unique data, per test fixtures, thread safe clients and assertions that tolerate other tests\' data make parallel runs reliable.',
      kind='Concept'),
    Q('reporting', 'CI and reporting', 'e',
      'What should a good API test report show when a test fails?',
      'What would you need to raise a bug without rerunning anything?',
      'The test name and steps, the full request with method, URL, headers and body, the full response with status, headers and body, the timing, the environment, and the assertion that failed with expected and actual values.',
      'With this information a developer can reproduce the bug immediately. Rest Assured filters with Allure, Playwright traces, pytest with logging or pytest-html, and Newman reporters can all attach requests and responses. Mask secrets such as tokens and passwords in the logs before publishing reports.',
      kind='Concept'),

    # ---------- Real world scenarios ----------
    Q('sc-200-wrong', 'Real world scenarios', 'm',
      'An endpoint returns 200, but users report that their data is not saved. How would you write a test that catches this?',
      'Do not trust the response alone.',
      'After the write call, read the data back through a separate GET, or check the database or downstream system, and assert that the stored values match what was sent.',
      'A response can echo the request body even when the save failed or was rolled back later. A test that only checks the response would pass. Reading back with a fresh GET, ideally with a new connection or client so no cache is involved, proves persistence. For asynchronous systems, poll the GET with a timeout until the data appears, rather than sleeping a fixed time.',
      kind='Scenario'),
    Q('sc-security', 'Real world scenarios', 'h',
      'Which security checks would you add to your API automation suite?',
      'Think of the OWASP API Security Top 10.',
      'Broken object level authorization, where user A reads or changes user B\'s data by changing an id. Missing or weak authentication. Excessive data exposure in responses. Mass assignment, where extra fields such as role=admin are accepted. Rate limiting. Injection in parameters. Security headers and HTTPS only.',
      'Broken object level authorization is the most common serious API bug, and it is easy to automate: create a resource as user A, then request it with user B\'s token and expect 403 or 404. For mass assignment, send fields the client should not control and check they are ignored. Check that error messages do not leak stack traces and that responses do not include fields such as password hashes. These tests are cheap to run on every build and catch issues long before a penetration test.',
      kind='Scenario',
      points=['Object level authorization with two users', 'Auth missing, wrong and expired', 'No sensitive fields in responses', 'Mass assignment ignored', 'Rate limits and safe error messages']),
    Q('sc-async-job', 'Real world scenarios', 'h',
      'POST /reports starts a job that takes up to a minute. How do you test it without Thread.sleep or time.sleep?',
      'Ask repeatedly, with a deadline.',
      'Read the job id from the 202 response, then poll GET /reports/{id} every second or so until the status is DONE or FAILED, with an overall timeout. Then assert on the final result.',
      'Fixed sleeps are either too short, which makes the test flaky, or too long, which wastes time on every run. Polling returns as soon as the job finishes. Tools help: Awaitility in Java, expect.poll in Playwright Test, a small poll helper or tenacity in Python. Make the timeout message include the last status, so a stuck job is easy to diagnose.',
      kind='Coding', lang='java',
      acode='''String id = given().spec(spec).post("/reports").then().statusCode(202).extract().path("id");

await().atMost(Duration.ofSeconds(60)).pollInterval(Duration.ofSeconds(1))
    .until(() -> given().spec(spec).get("/reports/" + id).path("status"), equalTo("DONE"));'''),
    Q('sc-breaking-change', 'Real world scenarios', 'm',
      'A developer renames a field from total_price to totalPrice. Which of your tests should fail, and how do you prevent it reaching production?',
      'Value checks, schema checks and contracts.',
      'Schema tests and contract tests should fail at once, as well as any value assertion on that field. Running them in the provider\'s pull request pipeline stops the change before it merges.',
      'If only some tests check that field, a schema check on every response is the safety net. Consumer driven contracts tell the developer which consumers depend on the old name. The fix is usually to support both names for a deprecation period, version the API, or coordinate the change with consumers. This question tests whether you think about API changes as contract changes, not just code changes.',
      kind='Scenario'),
    Q('ts-why-zod', 'Framework design', 'm',
      'Your Playwright tests are written in TypeScript with a Booking interface. Why would you still add Zod or JSON Schema checks?',
      'When do TypeScript types exist?',
      'Types are removed before the code runs, so they only describe what you expect. A run time check such as Zod or JSON Schema looks at the body the server really sent and fails when it does not match.',
      'Writing <code>const body: Booking = await res.json()</code> gives autocomplete but proves nothing about the response. With Zod you write the schema once, validate with <code>safeParse</code>, and get the type for free with <code>z.infer</code>. Generating types from the OpenAPI file with openapi-typescript keeps the compile time side in step with the contract.',
      kind='Concept',
      points=['Types vanish at run time', 'Zod or JSON Schema checks the real body', 'z.infer gives the type from the schema', 'Generate types from OpenAPI to avoid drift']),
    Q('secrets-logs', 'Framework design', 'm',
      'How do you keep passwords and tokens out of your API test code, logs and reports?',
      'Think of where secrets live and where they could leak.',
      'Read secrets from environment variables filled by the CI secret store, never commit them, and redact Authorization, Cookie and API key headers before anything is logged or attached to a report.',
      'Locally use an ignored .env file. In Rest Assured use <code>blacklistHeader</code> in the log config, in Postman keep secrets in the current value or Vault, and in custom loggers replace secret header values with stars. Test the redaction itself, because CI logs and HTML reports are read by many people.',
      kind='Concept',
      points=['Environment variables and CI secrets', 'Ignored .env files locally', 'Redact headers before logging', 'Check reports and traces too']),
    Q('test-data-cleanup', 'Framework design', 'h',
      'Several CI jobs run your API suite in parallel against one shared QA server, and tests fail randomly. What would you change?',
      'Shared data is the usual cause.',
      'Give every test its own data with unique values such as a UUID or Faker names, never depend on records another test made, and delete what each test created in a fixture or after hook that runs even when the test fails.',
      'Random failures in parallel runs usually come from two tests reading or changing the same record. Unique data removes the collisions. Cleanup keeps the shared database usable. Add a run id header so backend logs can be filtered by CI run, and seed Faker when a failure must be reproduced.',
      kind='Scenario'),
    Q('latest-tools-2026', 'Real world scenarios', 'x',
      'Name recent changes in API automation tools that you would use at work, and why.',
      'Pick one per tool you know.',
      'Examples: Rest Assured 6.1 added the QUERY method and JSON Schema 2020-12, 6.2 added mutual TLS client certificates, pytest 9 added built in subtests and TOML config, TypeScript 7 made type checks much faster, Playwright 1.64 added tracing and cookie methods on API request contexts, and Postman 12 moved to Git native YAML collections.',
      'Interviewers want to see that you follow your tools and connect each change to a benefit, such as validating OpenAPI 3.1 schemas, seeing every failing field in one run, or reviewing collection changes in the same pull request as the code. Mention that you upgrade on a branch and read release notes first.',
      kind='Concept'),
    Q('sc-what-first', 'Real world scenarios', 'e',
      'You join a team with no API automation. What would you automate first?',
      'Value and risk.',
      'Start with a smoke set: a health check, login, and the main happy path of the most important business flows. Then add negative and auth tests for the riskiest endpoints, and run all of it in CI on every change.',
      'Early value comes from catching the failures that hurt most, such as login broken or orders not created. Choose a tool that fits the team\'s language so developers can contribute. Build the client layer, config and data fixtures from the start, because adding them later is more work. Measure progress by business flows covered rather than by number of tests.',
      kind='Scenario'),
]
