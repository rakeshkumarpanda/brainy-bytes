TRACK = {
    'id': 'java-playwright', 'lang': 'java', 'tool': 'playwright',
    'title': 'Playwright for Java', 'emoji': '🎭',
    'tagline': 'One library for UI and API tests. Use APIRequestContext for fast API checks and test data setup.',
    'intro': 'Playwright is best known for browser automation, but it ships a full HTTP client called <b>APIRequestContext</b>. Teams that already use Playwright for UI tests can write API tests in the same project, share login state between API and browser, and mock API answers inside UI tests. This track uses JUnit 5 style tests, which run on JUnit 6.',
    'stack': [
        ('Java', '21 LTS', 'Playwright needs Java 8 or newer, we use 21'),
        ('Playwright', '1.63.0', 'APIRequestContext and assertions'),
        ('JUnit Jupiter', '6.1.3', 'runner and parameterized tests'),
        ('Jackson', '2.22.4', 'JSON to Java objects'),
        ('json-schema-validator', '3.0.8', 'networknt, schema checks'),
    ],
    'sections': [
        {
            'id': 'why', 'title': 'Why test APIs with Playwright', 'emoji': '🎯', 'level': 'Basic',
            'blocks': [
                ('p', 'An API test sends an HTTP request and checks the answer, without a browser. Playwright makes this possible with <code>playwright.request().newContext()</code>, which opens no browser at all. It starts in a fraction of a second and needs no browser download for pure API work.'),
                ('table', ['Reason', 'What it gives you'], [
                    ['One tool for UI and API', 'One dependency, one set of reports and one CI job'],
                    ['Shared login state', 'Log in with an API call, then open the browser already signed in'],
                    ['Fast test data', 'Create bookings with POST before a UI test instead of clicking forms'],
                    ['Network mocking in UI tests', '<code>page.route()</code> can answer API calls made by the web page'],
                    ['Built in assertions', '<code>assertThat(response).isOK()</code> prints the response on failure'],
                ]),
                ('qa', 'If your team runs Playwright for UI, this is the natural first step into API testing. Every UI test can start with API calls that create exactly the data it needs.'),
                ('p', 'Every test follows <b>Arrange, Act, Assert</b>. Arrange builds the request, Act sends it, Assert checks the response.'),
            ],
        },
        {
            'id': 'setup', 'title': 'Project setup with Maven and JUnit', 'emoji': '🧰', 'level': 'Basic',
            'blocks': [
                ('code', 'xml', 'pom.xml', '''
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.brainybytes</groupId>
  <artifactId>booker-playwright-api</artifactId>
  <version>1.0</version>

  <properties>
    <maven.compiler.release>21</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>

  <dependencies>
    <dependency>
      <groupId>com.microsoft.playwright</groupId>
      <artifactId>playwright</artifactId>
      <version>1.63.0</version>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.junit.jupiter</groupId>
      <artifactId>junit-jupiter</artifactId>
      <version>6.1.3</version>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-databind</artifactId>
      <version>2.22.4</version>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>com.networknt</groupId>
      <artifactId>json-schema-validator</artifactId>
      <version>3.0.8</version>
      <scope>test</scope>
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>
        <version>3.5.4</version>
      </plugin>
    </plugins>
  </build>
</project>
''', {'save': 'pom.xml'}),
                ('tip', 'API tests do not need browsers. Set the environment variable <code>PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1</code> on CI machines that only run API tests, so the first run does not download Chromium, Firefox and WebKit.'),
                ('p', 'Run the suite with <code>mvn test</code>, one class with <code>mvn test -Dtest=FirstTest</code>, and point it at another server with <code>mvn test -DbaseUrl=http://localhost:3001</code>.'),
            ],
        },
        {
            'id': 'first-test', 'title': 'Your first test: GET a booking', 'emoji': '👋', 'level': 'Basic',
            'blocks': [
                ('p', 'Create one <code>Playwright</code> and one <code>APIRequestContext</code> for the test class, use it in every test, and close both at the end. The context keeps the base URL, default headers and cookies.'),
                ('code', 'java', 'src/test/java/tests/FirstTest.java', '''
package tests;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;
import static org.junit.jupiter.api.Assertions.*;

import com.microsoft.playwright.APIRequest;
import com.microsoft.playwright.APIRequestContext;
import com.microsoft.playwright.APIResponse;
import com.microsoft.playwright.Playwright;
import java.util.Map;
import org.junit.jupiter.api.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class FirstTest {

    Playwright playwright;
    APIRequestContext request;

    @BeforeAll
    void setUp() {
        playwright = Playwright.create();
        request = playwright.request().newContext(new APIRequest.NewContextOptions()
            .setBaseURL(System.getProperty("baseUrl", "https://restful-booker.herokuapp.com"))
            .setExtraHTTPHeaders(Map.of("Accept", "application/json")));
    }

    @Test
    void pingSaysTheApiIsUp() {
        APIResponse res = request.get("/ping");
        assertEquals(201, res.status());
    }

    @Test
    void getOneBooking() {
        APIResponse res = request.get("/booking/1");

        assertThat(res).isOK();                                   // any 2xx, prints the body if not
        assertEquals(200, res.status());
        assertTrue(res.headers().get("content-type").contains("application/json"));
        assertTrue(res.text().contains("\\"firstname\\""));
    }

    @AfterAll
    void tearDown() {
        request.dispose();
        playwright.close();
    }
}
''', {'save': 'src/test/java/tests/FirstTest.java'}),
                ('ul', [
                    '<code>@TestInstance(PER_CLASS)</code> lets <code>@BeforeAll</code> be a normal method, so fields can hold the context.',
                    '<code>res.status()</code> is the code, <code>res.text()</code> is the body as text, <code>res.body()</code> is raw bytes.',
                    '<code>res.headers()</code> is a map with lower case names, so ask for <code>content-type</code>.',
                    '<code>assertThat(res).isOK()</code> passes for any status from 200 to 299.',
                ]),
                ('try', {'method': 'GET', 'path': '/booking/1'}),
            ],
        },
        {
            'id': 'request', 'title': 'Building requests with RequestOptions', 'emoji': '🧱', 'level': 'Basic',
            'blocks': [
                ('p', 'Every call takes an optional <code>RequestOptions</code>. It holds query parameters, headers, the body, timeouts and more.'),
                ('code', 'java', 'Query params, headers, timeouts', '''
import com.microsoft.playwright.options.RequestOptions;

// /booking?firstname=Sally&lastname=Brown
APIResponse list = request.get("/booking", RequestOptions.create()
    .setQueryParam("firstname", "Sally")
    .setQueryParam("lastname", "Brown"));

// Extra headers and a timeout for one call
APIResponse one = request.get("/booking/1", RequestOptions.create()
    .setHeader("X-Request-Id", java.util.UUID.randomUUID().toString())
    .setTimeout(5_000));                       // milliseconds

// Do not throw on 4xx or 5xx (the default). Set true to fail fast instead.
APIResponse strict = request.get("/booking/1", RequestOptions.create().setFailOnStatusCode(true));

// Any method, including PATCH and HEAD
APIResponse head = request.fetch("/booking/1", RequestOptions.create().setMethod("HEAD"));
'''),
                ('table', ['Need', 'Option'], [
                    ['Query string', '<code>setQueryParam(name, value)</code>'],
                    ['Header', '<code>setHeader(name, value)</code>'],
                    ['JSON body', '<code>setData(object or String)</code>'],
                    ['Form body', '<code>setForm(FormData.create().set("a", "1"))</code>'],
                    ['File upload', '<code>setMultipart(FormData.create().set("file", path))</code>'],
                    ['Time limit', '<code>setTimeout(ms)</code>'],
                    ['Retry on network errors', '<code>setMaxRetries(3)</code>'],
                    ['Throw on 4xx and 5xx', '<code>setFailOnStatusCode(true)</code>'],
                ]),
            ],
        },
        {
            'id': 'crud', 'title': 'Create, update and delete (CRUD)', 'emoji': '✍️', 'level': 'Basic',
            'blocks': [
                ('p', '<code>setData</code> accepts a <code>Map</code>, which Playwright turns into JSON and labels with <code>Content-Type: application/json</code>. A <code>String</code> is sent as it is, so add the header yourself.'),
                ('code', 'java', 'src/test/java/tests/CrudTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.microsoft.playwright.*;
import com.microsoft.playwright.options.RequestOptions;
import java.util.Base64;
import java.util.Map;
import org.junit.jupiter.api.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class CrudTest {

    static final ObjectMapper JSON = new ObjectMapper();
    Playwright playwright;
    APIRequestContext request;
    int bookingId;

    @BeforeAll
    void setUp() {
        playwright = Playwright.create();
        String basic = Base64.getEncoder().encodeToString("admin:password123".getBytes());
        request = playwright.request().newContext(new APIRequest.NewContextOptions()
            .setBaseURL(System.getProperty("baseUrl", "https://restful-booker.herokuapp.com"))
            .setExtraHTTPHeaders(Map.of(
                "Accept", "application/json",
                "Authorization", "Basic " + basic)));   // sent with every call
    }

    @Test @Order(1)
    void create() throws Exception {
        APIResponse res = request.post("/booking", RequestOptions.create().setData(Map.of(
            "firstname", "Rakesh",
            "lastname", "Panda",
            "totalprice", 250,
            "depositpaid", true,
            "bookingdates", Map.of("checkin", "2026-11-01", "checkout", "2026-11-04"),
            "additionalneeds", "Breakfast")));

        assertEquals(200, res.status());
        JsonNode body = JSON.readTree(res.body());
        bookingId = body.get("bookingid").asInt();
        assertTrue(bookingId > 0);
        assertEquals("Rakesh", body.at("/booking/firstname").asText());
    }

    @Test @Order(2)
    void replaceWithPut() throws Exception {
        APIResponse res = request.put("/booking/" + bookingId, RequestOptions.create()
            .setHeader("Content-Type", "application/json")
            .setData("""
                {"firstname":"Rakesh","lastname":"Kumar","totalprice":300,"depositpaid":false,
                 "bookingdates":{"checkin":"2026-11-02","checkout":"2026-11-05"}}
                """));

        assertEquals(200, res.status());
        assertEquals("Kumar", JSON.readTree(res.body()).get("lastname").asText());
    }

    @Test @Order(3)
    void changeOneFieldWithPatch() throws Exception {
        APIResponse res = request.patch("/booking/" + bookingId,
            RequestOptions.create().setData(Map.of("additionalneeds", "Dinner")));

        JsonNode body = JSON.readTree(res.body());
        assertEquals("Dinner", body.get("additionalneeds").asText());
        assertEquals("Kumar", body.get("lastname").asText());   // other fields stay
    }

    @Test @Order(4)
    void deleteThenConfirmGone() {
        assertEquals(201, request.delete("/booking/" + bookingId).status());   // this API answers 201
        assertEquals(404, request.get("/booking/" + bookingId).status());
    }

    @AfterAll
    void tearDown() {
        request.dispose();
        playwright.close();
    }
}
''', {'save': 'src/test/java/tests/CrudTest.java'}),
                ('warn', 'Restful Booker answers 403 instead of 401 when auth is missing. Playwright\'s <code>setHttpCredentials</code> waits for a 401 before sending the password, unless you add <code>.setSend(HttpCredentialsSend.ALWAYS)</code>. Sending the <code>Authorization</code> header yourself, as above, always works.'),
                ('try', {'method': 'PATCH', 'path': '/booking/1', 'auth': 'basic', 'body': {'additionalneeds': 'Dinner'}}),
            ],
        },
        {
            'id': 'assertions', 'title': 'Assertions and reading JSON', 'emoji': '🔍', 'level': 'Intermediate',
            'blocks': [
                ('p', 'Playwright gives the body as text or bytes. Parse it with Jackson into a <code>JsonNode</code> and walk it with JSON Pointer paths like <code>/bookingdates/checkin</code>. JUnit <code>assertAll</code> runs every check and reports all failures together.'),
                ('code', 'java', 'Checking a booking thoroughly', '''
APIResponse res = request.get("/booking/1");
JsonNode b = JSON.readTree(res.body());

assertAll("booking 1",
    () -> assertEquals(200, res.status()),
    () -> assertTrue(res.headers().get("content-type").startsWith("application/json")),
    () -> assertTrue(b.get("firstname").isTextual()),
    () -> assertTrue(b.get("totalprice").isInt()),
    () -> assertTrue(b.get("totalprice").asInt() >= 0),
    () -> assertTrue(b.get("depositpaid").isBoolean()),
    () -> assertTrue(b.at("/bookingdates/checkin").asText().matches("\\\\d{4}-\\\\d{2}-\\\\d{2}")),
    () -> assertFalse(b.at("/bookingdates/checkout").isMissingNode()));

// Lists: check every item
JsonNode list = JSON.readTree(request.get("/booking").body());
assertTrue(list.isArray() && list.size() > 0);
list.forEach(item -> assertTrue(item.get("bookingid").asInt() > 0));
'''),
                ('h', 'Playwright\'s own response assertions'),
                ('code', 'java', 'assertThat on APIResponse', '''
import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

assertThat(request.get("/booking/1")).isOK();
assertThat(request.get("/booking/999999")).not().isOK();
'''),
                ('tip', 'When <code>isOK()</code> fails, Playwright prints the method, URL, status and the response body. That message is usually enough to understand a failure in CI without rerunning.'),
            ],
        },
        {
            'id': 'chain-auth', 'title': 'Chaining calls and authentication', 'emoji': '🔐', 'level': 'Intermediate',
            'blocks': [
                ('p', 'Log in, keep the token, and send it with later calls. Restful Booker wants the token in a cookie. Most other APIs want a Bearer token in the <code>Authorization</code> header.'),
                ('code', 'java', 'Token flow', '''
// 1. log in
APIResponse login = request.post("/auth", RequestOptions.create()
    .setData(Map.of("username", "admin", "password", "password123")));
String token = JSON.readTree(login.body()).get("token").asText();

// 2. use it for one call
APIResponse patched = request.patch("/booking/" + id, RequestOptions.create()
    .setHeader("Cookie", "token=" + token)
    .setData(Map.of("firstname", "Updated")));

// 3. or build a context that always sends it
APIRequestContext admin = playwright.request().newContext(new APIRequest.NewContextOptions()
    .setBaseURL(baseUrl)
    .setExtraHTTPHeaders(Map.of("Cookie", "token=" + token)));

// Bearer token APIs
APIRequestContext api = playwright.request().newContext(new APIRequest.NewContextOptions()
    .setBaseURL("https://api.example.com")
    .setExtraHTTPHeaders(Map.of("Authorization", "Bearer " + System.getenv("API_TOKEN"))));

// Basic auth sent on the first request
APIRequestContext basic = playwright.request().newContext(new APIRequest.NewContextOptions()
    .setBaseURL(baseUrl)
    .setHttpCredentials(new HttpCredentials("admin", "password123").setSend(HttpCredentialsSend.ALWAYS)));
'''),
                ('h', 'Security checks to include'),
                ('ul', [
                    'No token, a wrong token, and an expired token must all be refused.',
                    'Changing the id in the path must not expose another user\'s booking.',
                    'Error answers must not include stack traces or internal details.',
                ]),
                ('code', 'java', 'A negative test', '''
@Test
void updateWithoutTokenIsForbidden() {
    APIResponse res = anonymous.patch("/booking/1",
        RequestOptions.create().setData(Map.of("firstname", "Hacker")));
    assertEquals(403, res.status());
    assertFalse(anonymous.get("/booking/1").text().contains("Hacker"));
}
'''),
            ],
        },
        {
            'id': 'data-driven', 'title': 'Data driven tests with @ParameterizedTest', 'emoji': '📊', 'level': 'Intermediate',
            'blocks': [
                ('p', 'JUnit runs one method once per row of data. Use <code>@CsvSource</code> for small tables, <code>@MethodSource</code> for objects, and <code>@CsvFileSource</code> for a file.'),
                ('code', 'java', 'src/test/java/tests/DataDrivenTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.microsoft.playwright.*;
import com.microsoft.playwright.options.RequestOptions;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class DataDrivenTest {

    static final ObjectMapper JSON = new ObjectMapper();
    Playwright playwright;
    APIRequestContext request;

    @BeforeAll
    void setUp() {
        playwright = Playwright.create();
        request = playwright.request().newContext(new APIRequest.NewContextOptions()
            .setBaseURL(System.getProperty("baseUrl", "https://restful-booker.herokuapp.com")));
    }

    @ParameterizedTest(name = "{0} {1} is stored exactly")
    @CsvSource({
        "Ann, Lee",
        "José, Núñez",
        "O'Brien, Smith-Jones",
        "A, B"
    })
    void namesAreKept(String first, String last) throws Exception {
        Map<String, Object> body = validBooking();
        body.put("firstname", first);
        body.put("lastname", last);

        APIResponse res = request.post("/booking", RequestOptions.create().setData(body));

        assertEquals(200, res.status());
        assertEquals(first, JSON.readTree(res.body()).at("/booking/firstname").asText());
    }

    @ParameterizedTest(name = "missing {0} is rejected")
    @ValueSource(strings = {"firstname", "lastname", "totalprice", "depositpaid", "bookingdates"})
    void requiredFields(String field) {
        Map<String, Object> body = validBooking();
        body.remove(field);

        APIResponse res = request.post("/booking", RequestOptions.create().setData(body));

        assertNotEquals(200, res.status(), "Restful Booker answers 500 here, a good API answers 400");
    }

    static Map<String, Object> validBooking() {
        Map<String, Object> b = new HashMap<>();
        b.put("firstname", "Test");
        b.put("lastname", "User");
        b.put("totalprice", 100);
        b.put("depositpaid", true);
        b.put("bookingdates", Map.of("checkin", "2026-12-01", "checkout", "2026-12-03"));
        return b;
    }

    @AfterAll
    void tearDown() {
        request.dispose();
        playwright.close();
    }
}
''', {'save': 'src/test/java/tests/DataDrivenTest.java'}),
                ('qa', 'Boundary and invalid data rows are where most API bugs hide: empty strings, very long strings, negative prices, a checkout before the checkin, and dates in the wrong format.'),
            ],
        },
        {
            'id': 'schema', 'title': 'JSON Schema validation', 'emoji': '📐', 'level': 'Advanced',
            'blocks': [
                ('p', 'A schema describes the shape of a response. The networknt validator checks a response against it and lists every problem it finds.'),
                ('code', 'json', 'src/test/resources/schemas/booking-schema.json', '''
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"],
  "properties": {
    "firstname":   { "type": "string", "minLength": 1 },
    "lastname":    { "type": "string", "minLength": 1 },
    "totalprice":  { "type": "integer", "minimum": 0 },
    "depositpaid": { "type": "boolean" },
    "bookingdates": {
      "type": "object",
      "required": ["checkin", "checkout"],
      "properties": {
        "checkin":  { "type": "string", "pattern": "^\\\\d{4}-\\\\d{2}-\\\\d{2}$" },
        "checkout": { "type": "string", "pattern": "^\\\\d{4}-\\\\d{2}-\\\\d{2}$" }
      }
    },
    "additionalneeds": { "type": "string" }
  }
}
''', {'save': 'src/test/resources/schemas/booking-schema.json'}),
                ('code', 'java', 'src/test/java/tests/SchemaTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;

import com.microsoft.playwright.*;
import com.networknt.schema.InputFormat;
import com.networknt.schema.Schema;
import com.networknt.schema.SchemaRegistry;
import com.networknt.schema.SpecificationVersion;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class SchemaTest {

    Playwright playwright;
    APIRequestContext request;
    Schema bookingSchema;

    @BeforeAll
    void setUp() throws Exception {
        playwright = Playwright.create();
        request = playwright.request().newContext(new APIRequest.NewContextOptions()
            .setBaseURL(System.getProperty("baseUrl", "https://restful-booker.herokuapp.com")));
        String text = Files.readString(Path.of("src/test/resources/schemas/booking-schema.json"));
        bookingSchema = SchemaRegistry.withDefaultDialect(SpecificationVersion.DRAFT_7).getSchema(text);
    }

    @Test
    void bookingMatchesSchema() {
        APIResponse res = request.get("/booking/1");
        var errors = bookingSchema.validate(res.text(), InputFormat.JSON);
        assertTrue(errors.isEmpty(), () -> "Schema problems: " + errors);
    }

    @Test
    void schemaCatchesARenamedField() {
        var errors = bookingSchema.validate("""
            {"firstname":"A","lastname":"B","totalPrice":1,"depositpaid":true,
             "bookingdates":{"checkin":"2026-01-01","checkout":"2026-01-02"}}
            """, InputFormat.JSON);
        assertFalse(errors.isEmpty());   // totalprice is required, totalPrice does not count
    }

    @AfterAll
    void tearDown() {
        request.dispose();
        playwright.close();
    }
}
''', {'save': 'src/test/java/tests/SchemaTest.java'}),
                ('tip', 'The second test proves the schema itself works. Testing your checks against bad data is a good habit, because a check that can never fail is worth nothing.'),
            ],
        },
        {
            'id': 'framework', 'title': 'Framework design: a client class and a base test', 'emoji': '🏗️', 'level': 'Advanced',
            'blocks': [
                ('p', 'Move HTTP details into a client class with one method per endpoint, and move setup into a base class. Tests then only describe behaviour.'),
                ('code', 'java', 'src/test/java/tests/support/BookingClient.java', '''
package tests.support;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.microsoft.playwright.APIRequestContext;
import com.microsoft.playwright.APIResponse;
import com.microsoft.playwright.options.RequestOptions;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.Map;

public class BookingClient {

    private static final ObjectMapper JSON = new ObjectMapper();
    private final APIRequestContext request;
    private String token;

    public BookingClient(APIRequestContext request) { this.request = request; }

    public BookingClient login(String user, String password) {
        token = json(request.post("/auth", RequestOptions.create()
            .setData(Map.of("username", user, "password", password)))).get("token").asText();
        return this;
    }

    public APIResponse create(Map<String, ?> booking) { return request.post("/booking", RequestOptions.create().setData(booking)); }
    public APIResponse get(int id)                    { return request.get("/booking/" + id); }
    public APIResponse patch(int id, Map<String, ?> f){ return request.patch("/booking/" + id, authed().setData(f)); }
    public APIResponse delete(int id)                 { return request.delete("/booking/" + id, authed()); }

    public int createAndGetId(Map<String, ?> booking) { return json(create(booking)).get("bookingid").asInt(); }

    private RequestOptions authed() {
        RequestOptions o = RequestOptions.create();
        return token == null ? o : o.setHeader("Cookie", "token=" + token);
    }

    public static JsonNode json(APIResponse res) {
        try { return JSON.readTree(res.body()); }
        catch (IOException e) { throw new UncheckedIOException("Not JSON: " + res.text(), e); }
    }
}
''', {'save': 'src/test/java/tests/support/BookingClient.java'}),
                ('code', 'java', 'src/test/java/tests/support/ApiTest.java', '''
package tests.support;

import com.microsoft.playwright.APIRequest;
import com.microsoft.playwright.APIRequestContext;
import com.microsoft.playwright.Playwright;
import java.util.Map;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.TestInstance;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public abstract class ApiTest {

    protected Playwright playwright;
    protected APIRequestContext request;
    protected BookingClient bookings;

    @BeforeAll
    void startApi() {
        playwright = Playwright.create();
        request = playwright.request().newContext(new APIRequest.NewContextOptions()
            .setBaseURL(System.getProperty("baseUrl", "https://restful-booker.herokuapp.com"))
            .setExtraHTTPHeaders(Map.of("Accept", "application/json")));
        bookings = new BookingClient(request);
    }

    @AfterAll
    void stopApi() {
        request.dispose();
        playwright.close();
    }
}
''', {'save': 'src/test/java/tests/support/ApiTest.java'}),
                ('code', 'java', 'src/test/java/tests/FrameworkTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;
import static tests.support.BookingClient.json;

import java.util.Map;
import org.junit.jupiter.api.Test;
import tests.support.ApiTest;

class FrameworkTest extends ApiTest {

    static final Map<String, Object> SAMPLE = Map.of(
        "firstname", "Frame", "lastname", "Work", "totalprice", 120, "depositpaid", true,
        "bookingdates", Map.of("checkin", "2026-11-01", "checkout", "2026-11-02"));

    @Test
    void patchThroughTheClient() {
        bookings.login("admin", "password123");
        int id = bookings.createAndGetId(SAMPLE);

        assertEquals("Late", json(bookings.patch(id, Map.of("additionalneeds", "Late"))).get("additionalneeds").asText());
        assertEquals(201, bookings.delete(id).status());
        assertEquals(404, bookings.get(id).status());
    }
}
''', {'save': 'src/test/java/tests/FrameworkTest.java'}),
            ],
        },
        {
            'id': 'ui-api', 'title': 'Mixing UI and API in one test', 'emoji': '🖥️', 'level': 'Advanced',
            'blocks': [
                ('p', 'This is where Playwright shines for QA. Each browser context has its own <code>request()</code> that shares cookies with the pages in it. Three patterns save the most time.'),
                ('code', 'java', 'Seed data by API, check it in the UI', '''
BrowserContext context = browser.newContext(new Browser.NewContextOptions().setBaseURL(appUrl));
Page page = context.newPage();

// 1. Create test data through the API, which takes milliseconds
APIResponse created = context.request().post("/api/bookings",
    RequestOptions.create().setData(Map.of("guest", "Rakesh Panda", "nights", 3)));
int id = BookingClient.json(created).get("id").asInt();

// 2. Check the UI shows it
page.navigate("/bookings/" + id);
assertThat(page.getByRole(AriaRole.HEADING)).containsText("Rakesh Panda");
'''),
                ('code', 'java', 'Log in once by API and reuse the session', '''
APIRequestContext api = playwright.request().newContext(
    new APIRequest.NewContextOptions().setBaseURL(appUrl));
api.post("/api/login", RequestOptions.create()
    .setData(Map.of("user", "qa", "password", System.getenv("QA_PASSWORD"))));
api.storageState(new APIRequestContext.StorageStateOptions().setPath(Path.of("auth.json")));

// every browser test starts signed in
BrowserContext signedIn = browser.newContext(
    new Browser.NewContextOptions().setStorageStatePath(Path.of("auth.json")));
'''),
                ('code', 'java', 'Mock what the page receives from the API', '''
page.route("**/api/bookings", route -> route.fulfill(new Route.FulfillOptions()
    .setStatus(500)
    .setContentType("application/json")
    .setBody("{\\"error\\":\\"Server down\\"}")));

page.navigate("/bookings");
assertThat(page.getByText("Something went wrong")).isVisible();
'''),
                ('qa', 'Mocking with <code>page.route</code> lets you test how the UI handles slow answers, empty lists and server errors, which are hard to produce on a real server.'),
            ],
        },
        {
            'id': 'parallel-ci', 'title': 'Parallel runs, thread safety and CI', 'emoji': '🚀', 'level': 'Expert',
            'blocks': [
                ('p', 'JUnit can run test classes in parallel. Playwright objects are <b>not thread safe</b>, so every thread needs its own <code>Playwright</code> and context. Creating them per class, as the base class above does, is safe when classes run in parallel and methods inside a class run one at a time.'),
                ('code', 'properties', 'src/test/resources/junit-platform.properties', '''
junit.jupiter.execution.parallel.enabled = true
junit.jupiter.execution.parallel.mode.default = same_thread
junit.jupiter.execution.parallel.mode.classes.default = concurrent
junit.jupiter.execution.parallel.config.strategy = fixed
junit.jupiter.execution.parallel.config.fixed.parallelism = 4
'''),
                ('code', 'yaml', '.github/workflows/api-tests.yml', '''
name: API tests
on: [push, pull_request]
jobs:
  api:
    runs-on: ubuntu-latest
    env:
      PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD: 1
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 21
          cache: maven
      - run: mvn -B test -DbaseUrl=${{ vars.BASE_URL }}
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-reports
          path: target/surefire-reports
'''),
                ('tip', 'Tag tests with <code>@Tag("smoke")</code> and run a quick subset with <code>mvn test -Dgroups=smoke</code> on every commit. Run the full suite nightly.'),
            ],
        },
        {
            'id': 'expert', 'title': 'Expert topics: retries, polling, uploads and GraphQL', 'emoji': '🧠', 'level': 'Expert',
            'blocks': [
                ('code', 'java', 'Retries, polling and uploads', '''
// Retry network failures such as a reset connection (not 4xx or 5xx answers)
request.get("/booking/1", RequestOptions.create().setMaxRetries(3));

// Poll until a background job finishes, with a hard limit
long deadline = System.currentTimeMillis() + 30_000;
String status;
do {
    status = BookingClient.json(request.get("/jobs/" + jobId)).get("status").asText();
    if (!status.equals("DONE")) Thread.sleep(1_000);
} while (!status.equals("DONE") && System.currentTimeMillis() < deadline);
assertEquals("DONE", status);

// Multipart file upload
request.post("/documents", RequestOptions.create().setMultipart(FormData.create()
    .set("file", Path.of("src/test/resources/invoice.pdf"))
    .set("note", "March invoice")));

// GraphQL is one POST. Always check the errors array.
JsonNode gql = BookingClient.json(request.post("/graphql", RequestOptions.create().setData(Map.of(
    "query", "query($id: ID!) { booking(id: $id) { firstname } }",
    "variables", Map.of("id", 1)))));
assertTrue(gql.path("errors").isMissingNode());
'''),
                ('ul', [
                    '<b>Contract tests</b>: check responses against the OpenAPI or JSON Schema contract on every build.',
                    '<b>Idempotency</b>: send the same PUT twice and expect the same result.',
                    '<b>Rate limits</b>: many fast calls should give 429 with <code>Retry-After</code>.',
                    '<b>Pagination</b>: walk every page and check nothing is missing or repeated.',
                    '<b>Fuzzing</b>: odd inputs such as emoji, 10,000 character strings and wrong types should give 400, never 500.',
                ]),
            ],
        },
        {
            'id': 'essentials', 'title': 'Real project essentials: environments, secrets, test data, logging and cleanup', 'emoji': '🧳', 'level': 'Intermediate',
            'blocks': [
                ('p', 'A real Playwright for Java suite runs in several places, must not print secrets, creates unique data so parallel CI jobs never clash, says exactly what went wrong when it fails, and removes what it created. Playwright\'s context options also handle the awkward parts of real environments, such as self signed certificates and corporate proxies.'),
                ('code', 'java', 'src/test/java/tests/EssentialsTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.microsoft.playwright.APIRequest;
import com.microsoft.playwright.APIRequestContext;
import com.microsoft.playwright.APIResponse;
import com.microsoft.playwright.Playwright;
import com.microsoft.playwright.options.RequestOptions;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ThreadLocalRandom;
import java.util.logging.Logger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class EssentialsTest {

    private static final Logger LOG = Logger.getLogger("api");
    private static final ObjectMapper JSON = new ObjectMapper();

    private Playwright playwright;
    private APIRequestContext api;
    private String token;
    private final List<Integer> created = new ArrayList<>();

    static String setting(String property, String envVar, String fallback) {
        return Optional.ofNullable(System.getProperty(property))
            .or(() -> Optional.ofNullable(System.getenv(envVar)))
            .filter(v -> !v.isBlank())
            .orElse(fallback);
    }

    @BeforeAll
    void start() throws Exception {
        playwright = Playwright.create();
        api = playwright.request().newContext(new APIRequest.NewContextOptions()
            .setBaseURL(setting("baseUrl", "BASE_URL", "https://restful-booker.herokuapp.com"))
            .setExtraHTTPHeaders(Map.of("Accept", "application/json",
                                        "X-Test-Run", setting("runId", "GITHUB_RUN_ID", "local")))
            .setIgnoreHTTPSErrors("1".equals(System.getenv("QA_SELF_SIGNED")))   // QA only, never production
            .setTimeout(10_000));
        APIResponse login = api.post("/auth", RequestOptions.create().setData(Map.of(
            "username", setting("apiUser", "API_USER", "admin"),
            "password", setting("apiPassword", "API_PASSWORD", "password123"))));   // practice API default only
        token = JSON.readTree(login.text()).get("token").asText();
    }

    @AfterEach
    void cleanUp() {
        created.forEach(id -> api.delete("/booking/" + id, RequestOptions.create().setHeader("Cookie", "token=" + token)));
        created.clear();
    }

    @AfterAll
    void stop() {
        api.dispose();
        playwright.close();
    }

    /** Logs every call, and puts the whole response into the failure message when the status is wrong. */
    private JsonNode expectStatus(APIResponse res, int status) throws Exception {
        LOG.info(() -> res.url() + " -> " + res.status());
        assertEquals(status, res.status(), () -> "Unexpected status from " + res.url() + "\\n" + res.text());
        return JSON.readTree(res.text());
    }

    @Test
    void uniqueGuestRoundTrip() throws Exception {
        String guest = "Guest-" + UUID.randomUUID().toString().substring(0, 8);
        int price = ThreadLocalRandom.current().nextInt(500, 25_000);
        Map<String, Object> data = Map.of(
            "firstname", guest, "lastname", "Essentials", "totalprice", price, "depositpaid", true,
            "bookingdates", Map.of("checkin", "2026-12-20", "checkout", "2026-12-27"));

        int id = expectStatus(api.post("/booking", RequestOptions.create().setData(data)), 200).get("bookingid").asInt();
        created.add(id);

        JsonNode stored = expectStatus(api.get("/booking/" + id), 200);
        assertEquals(guest, stored.get("firstname").asText());
        assertEquals(price, stored.get("totalprice").asInt());
    }
}
''', {'save': 'src/test/java/tests/EssentialsTest.java'}),
                ('code', 'bash', 'Run it', '''
mvn test -Dtest=EssentialsTest -DbaseUrl=http://localhost:3001
BASE_URL=https://qa.booker.example API_PASSWORD="$QA_PASSWORD" mvn test
'''),
                ('table', ['Context option', 'Real situation'], [
                    ['<code>setBaseURL</code>', 'local, QA and staging from one suite'],
                    ['<code>setExtraHTTPHeaders</code>', 'a run id so backend logs can be filtered by CI run'],
                    ['<code>setIgnoreHTTPSErrors</code>', 'QA servers with self signed certificates'],
                    ['<code>setHttpCredentials</code>', 'staging behind Basic auth'],
                    ['<code>setProxy</code>', 'corporate networks that force a proxy'],
                    ['<code>setClientCertificates</code>', 'partner and banking APIs with mutual TLS'],
                    ['<code>setStorageStatePath</code>', 'reuse cookies from a login step instead of logging in for every class'],
                ]),
                ('tip', 'The lambda form <code>assertEquals(expected, actual, () -&gt; message)</code> builds the message only when the check fails, so reading the body costs nothing on passing tests.'),
            ],
        },
        {
            'id': 'latest', 'title': 'What is new in Java, JUnit 6 and Playwright, and how it helps at work', 'emoji': '🆕', 'level': 'Expert',
            'blocks': [
                ('table', ['Feature', 'Since', 'How it helps an API tester'], [
                    ['Java 25 LTS', 'September 2025', 'The new long term support release. Compact source files and instance <code>main</code> methods make small API scripts much shorter'],
                    ['Records and pattern matching for <code>switch</code>', 'Java 21', 'Model responses as records and branch on status codes cleanly'],
                    ['JUnit 6', 'September 2025', 'One version number for all JUnit modules, Java 17 as the minimum, and nullness annotations on the API'],
                    ['<code>@ParameterizedClass</code>', 'JUnit 5.13 and 6', 'Run a whole test class once per environment or per user role'],
                    ['Playwright for Java 1.64', '2026', 'Keep the Java bindings in step with the Node, Python and .NET releases your UI team uses'],
                ]),
                ('code', 'java', 'src/test/java/tests/RoleMatrixTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;

import com.microsoft.playwright.APIRequest;
import com.microsoft.playwright.APIRequestContext;
import com.microsoft.playwright.APIResponse;
import com.microsoft.playwright.Playwright;
import com.microsoft.playwright.options.RequestOptions;
import java.util.Base64;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.params.Parameter;
import org.junit.jupiter.params.ParameterizedClass;
import org.junit.jupiter.params.provider.EnumSource;

@ParameterizedClass(name = "as {0}")
@EnumSource(RoleMatrixTest.Role.class)
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class RoleMatrixTest {

    enum Role { ADMIN, WRONG_PASSWORD, ANONYMOUS }

    sealed interface Outcome permits Allowed, Refused { }
    record Allowed(int status) implements Outcome { }
    record Refused(int status) implements Outcome { }

    @Parameter
    Role role;

    private Playwright playwright;
    private APIRequestContext api;

    @BeforeAll
    void start() {
        playwright = Playwright.create();
        api = playwright.request().newContext(new APIRequest.NewContextOptions()
            .setBaseURL(System.getProperty("baseUrl", "https://restful-booker.herokuapp.com")));
    }

    @AfterAll
    void stop() { api.dispose(); playwright.close(); }

    private RequestOptions asRole() {
        RequestOptions o = RequestOptions.create().setData(java.util.Map.of("additionalneeds", "Dinner"));
        return switch (role) {
            case ADMIN -> o.setHeader("Authorization", "Basic " + Base64.getEncoder().encodeToString("admin:password123".getBytes()));
            case WRONG_PASSWORD -> o.setHeader("Authorization", "Basic " + Base64.getEncoder().encodeToString("admin:nope".getBytes()));
            case ANONYMOUS -> o;
        };
    }

    @Test
    void patchIsOnlyAllowedForAdmin() {
        APIResponse res = api.patch("/booking/1", asRole());
        Outcome outcome = res.ok() ? new Allowed(res.status()) : new Refused(res.status());

        String verdict = switch (outcome) {
            case Allowed a when role == Role.ADMIN -> "ok";
            case Refused r when role != Role.ADMIN && r.status() == 403 -> "ok";
            case Allowed a -> "BUG: " + role + " was allowed with " + a.status();
            case Refused r -> "unexpected " + r.status() + " for " + role;
        };
        assertEquals("ok", verdict);
    }
}
''', {'save': 'src/test/java/tests/RoleMatrixTest.java'}),
                ('code', 'java', 'Java 25: a whole health check script in one small file (run with: java Health.java)', '''
import java.net.URI;
import java.net.http.*;

void main() throws Exception {
    var res = HttpClient.newHttpClient().send(
        HttpRequest.newBuilder(URI.create("https://restful-booker.herokuapp.com/ping")).build(),
        HttpResponse.BodyHandlers.discarding());
    IO.println("ping -> " + res.statusCode());
}
'''),
                ('ul', [
                    'The role matrix class runs three times, once per role, and the report shows <code>as ADMIN</code>, <code>as WRONG_PASSWORD</code> and <code>as ANONYMOUS</code>. Add a role and every test in the class runs for it.',
                    'The sealed interface and record patterns make the compiler check that every outcome is handled.',
                    'Compact source files need Java 25. On Java 21 keep the normal <code>class</code> with <code>public static void main</code>.',
                ]),
            ],
        },
        {
            'id': 'scenario', 'title': 'Real world scenario: a hotel front desk day', 'emoji': '🏨', 'level': 'Scenario',
            'blocks': [
                ('p', 'The receptionist logs in, books a room, adds breakfast, and later cancels. The test follows the same steps and includes the check a hacker would try.'),
                ('flow', [
                    ('Health check', '<code>GET /ping</code> answers 201.'),
                    ('Log in', '<code>POST /auth</code> returns a token.'),
                    ('Book', '<code>POST /booking</code> returns a new id.'),
                    ('Search', '<code>GET /booking?firstname=...</code> includes the id.'),
                    ('Add breakfast', '<code>PATCH</code> with the token changes one field.'),
                    ('Unauthorised cancel', '<code>DELETE</code> without a token gives 403.'),
                    ('Cancel', '<code>DELETE</code> with the token gives 201.'),
                    ('Gone', '<code>GET</code> gives 404.'),
                ]),
                ('code', 'java', 'src/test/java/tests/FrontDeskJourneyTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;
import static tests.support.BookingClient.json;

import com.microsoft.playwright.APIResponse;
import com.microsoft.playwright.options.RequestOptions;
import java.util.Map;
import org.junit.jupiter.api.Test;
import tests.support.ApiTest;

class FrontDeskJourneyTest extends ApiTest {

    @Test
    void bookChangeAndCancel() {
        assertEquals(201, request.get("/ping").status());

        String token = json(request.post("/auth", RequestOptions.create()
            .setData(Map.of("username", "admin", "password", "password123")))).get("token").asText();
        assertFalse(token.isBlank());

        String guest = "Guest" + System.currentTimeMillis();
        int id = json(request.post("/booking", RequestOptions.create().setData(Map.of(
            "firstname", guest, "lastname", "Panda", "totalprice", 250, "depositpaid", true,
            "bookingdates", Map.of("checkin", "2026-11-01", "checkout", "2026-11-04"))))).get("bookingid").asInt();

        APIResponse found = request.get("/booking", RequestOptions.create().setQueryParam("firstname", guest));
        assertTrue(json(found).findValues("bookingid").stream().anyMatch(n -> n.asInt() == id));

        APIResponse patched = request.patch("/booking/" + id, RequestOptions.create()
            .setHeader("Cookie", "token=" + token)
            .setData(Map.of("additionalneeds", "Breakfast")));
        assertEquals("Breakfast", json(patched).get("additionalneeds").asText());
        assertEquals("Panda", json(patched).get("lastname").asText());

        assertEquals(403, request.delete("/booking/" + id).status());
        assertEquals(200, request.get("/booking/" + id).status());

        assertEquals(201, request.delete("/booking/" + id,
            RequestOptions.create().setHeader("Cookie", "token=" + token)).status());
        assertEquals(404, request.get("/booking/" + id).status());
    }
}
''', {'save': 'src/test/java/tests/FrontDeskJourneyTest.java'}),
            ],
        },
    ],
    'quiz': [
        {'lv': 'e', 'q': 'Which Playwright object sends API requests without opening a browser?', 'o': ['<code>Page</code>', '<code>APIRequestContext</code>', '<code>Locator</code>', '<code>BrowserType</code>'], 'a': 1, 'hint': 'You get it from playwright.request().', 'why': '<code>playwright.request().newContext()</code> returns an <code>APIRequestContext</code>, a full HTTP client with no browser.'},
        {'lv': 'e', 'q': 'What does <code>assertThat(res).isOK()</code> accept?', 'o': ['Only 200', 'Any status from 200 to 299', 'Any status below 500', 'Only 201'], 'a': 1, 'hint': 'OK means the 2xx family.', 'why': '<code>isOK()</code> passes for every 2xx status. Check the exact code with <code>assertEquals</code> when it matters.'},
        {'lv': 'm', 'q': 'You call <code>res.headers().get("Content-Type")</code> and get null. Why?', 'o': ['The API sent no headers', 'Playwright stores header names in lower case', 'Headers are only in <code>res.body()</code>', 'You need <code>setFailOnStatusCode</code>'], 'a': 1, 'hint': 'Look at the key spelling.', 'why': 'The map uses lower case names, so ask for <code>content-type</code>.'},
        {'lv': 'm', 'q': 'What happens when <code>setData</code> gets a <code>Map</code>?', 'o': ['It is sent as a form', 'It is turned into JSON and Content-Type is set to application/json', 'It throws an error', 'It is sent as a query string'], 'a': 1, 'hint': 'Compare with passing a String.', 'why': 'Objects and maps become JSON with the right header. A String is sent as it is, so you add the header yourself.'},
        {'lv': 'h', 'q': 'Basic auth with <code>setHttpCredentials</code> gets 403 from Restful Booker. What fixes it?', 'o': ['<code>.setSend(HttpCredentialsSend.ALWAYS)</code> or an Authorization header', 'Using GET', 'Restarting Playwright', '<code>setMaxRetries(3)</code>'], 'a': 0, 'hint': 'By default credentials wait for a 401 challenge.', 'why': 'Without a 401 challenge Playwright never sends the password. Sending it always, or adding the header yourself, works.'},
        {'lv': 'h', 'q': 'Why do UI tests often create data with <code>context.request()</code> first?', 'o': ['It is the only way', 'API calls are far faster and more reliable than filling forms', 'Browsers cannot send POST', 'It hides bugs'], 'a': 1, 'hint': 'Milliseconds versus seconds.', 'why': 'Seeding by API keeps UI tests short and focused on what the UI shows, not on the setup steps.'},
        {'lv': 'x', 'q': 'Tests share one static <code>APIRequestContext</code> and fail randomly when run in parallel. Why?', 'o': ['The API is down', 'Playwright objects are not thread safe', 'JUnit forbids static fields', 'JSON parsing is slow'], 'a': 1, 'hint': 'Check the Playwright threading rules.', 'why': 'Playwright objects must stay on one thread. Create a Playwright and context per class or per thread.'},
        {'lv': 'x', 'q': '<code>setMaxRetries(3)</code> is set and the API answers 503. How many times is the call sent?', 'o': ['Once, retries only cover network errors', 'Four times', 'Three times', 'Until it succeeds'], 'a': 0, 'hint': 'A 503 is still an answer.', 'why': 'Playwright retries network failures such as reset connections. An HTTP status, even 503, is a response and is not retried.'},
    ],
}
