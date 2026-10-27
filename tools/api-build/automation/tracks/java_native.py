TRACK = {
    'id': 'java-native', 'lang': 'java', 'tool': 'native',
    'title': 'Native Java with HttpClient', 'emoji': '🧩',
    'tagline': 'Test APIs with the HTTP client built into the JDK. No API library, full control, deep understanding.',
    'intro': 'Since Java 11 the JDK has a modern HTTP client in <code>java.net.http</code>. It supports HTTP/2, async calls, timeouts, cookies and authentication with no extra library. Learning it shows you exactly what tools like Rest Assured do for you. It is also the right choice for small health checks, CLI tools and teams that keep dependencies to a minimum. The JDK has no JSON parser, so this track adds Jackson for JSON and JUnit as the runner.',
    'stack': [
        ('Java', '21 LTS', 'HttpClient, virtual threads, text blocks'),
        ('java.net.http', 'built in', 'HttpClient, HttpRequest, HttpResponse'),
        ('JUnit Jupiter', '6.1.3', 'runner and assertions'),
        ('Jackson', '2.22.4', 'JSON, since the JDK has none'),
        ('json-schema-validator', '3.0.8', 'networknt, optional'),
    ],
    'sections': [
        {
            'id': 'why', 'title': 'Why learn the native way', 'emoji': '🎯', 'level': 'Basic',
            'blocks': [
                ('p', 'An API test sends an HTTP request and checks the response. Libraries make this shorter, but each one sits on top of an HTTP client like this one. When a library hides a problem, such as a missing header or a redirect, knowing the raw client tells you where to look.'),
                ('table', ['Class', 'Job'], [
                    ['<code>HttpClient</code>', 'Sends requests. Holds settings such as timeouts, redirects, cookies and HTTP version. Create one and reuse it.'],
                    ['<code>HttpRequest</code>', 'One request: URI, method, headers, body. Immutable, built with a builder.'],
                    ['<code>HttpRequest.BodyPublishers</code>', 'Turns a String, bytes or file into a request body.'],
                    ['<code>HttpResponse</code>', 'Status code, headers, body and the request that produced it.'],
                    ['<code>HttpResponse.BodyHandlers</code>', 'Reads the body as a String, bytes, file, stream or nothing.'],
                ]),
                ('qa', 'Many companies have internal tools that check service health before a release. A single Java file using HttpClient can do that with nothing to install except the JDK.'),
            ],
        },
        {
            'id': 'setup', 'title': 'Setup: from one file to a Maven project', 'emoji': '🧰', 'level': 'Basic',
            'blocks': [
                ('p', 'Java can run a single source file directly, with no build tool. This is the fastest way to try the client. The script below calls the API and exits with code 1 if a check fails, so CI treats it as a failure.'),
                ('code', 'java', 'BookerSmoke.java (run with: java BookerSmoke.java)', '''
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

public class BookerSmoke {

    public static void main(String[] args) throws Exception {
        String base = System.getProperty("baseUrl", "https://restful-booker.herokuapp.com");
        try (HttpClient client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build()) {

            HttpResponse<String> ping = client.send(
                HttpRequest.newBuilder(URI.create(base + "/ping")).GET().build(),
                HttpResponse.BodyHandlers.ofString());
            check(ping.statusCode() == 201, "ping should answer 201 but was " + ping.statusCode());

            HttpResponse<String> one = client.send(
                HttpRequest.newBuilder(URI.create(base + "/booking/1"))
                    .header("Accept", "application/json").build(),
                HttpResponse.BodyHandlers.ofString());
            check(one.statusCode() == 200, "booking 1 should exist");
            check(one.body().contains("\\"firstname\\""), "booking should have a firstname");
        }
        System.out.println("All smoke checks passed");
    }

    static void check(boolean ok, String message) {
        if (!ok) {
            System.err.println("FAILED: " + message);
            System.exit(1);
        }
    }
}
''', {'save': 'BookerSmoke.java'}),
                ('p', 'For a real suite, use Maven with JUnit for structure and reports, and Jackson for JSON.'),
                ('code', 'xml', 'pom.xml', '''
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.brainybytes</groupId>
  <artifactId>booker-native-api</artifactId>
  <version>1.0</version>

  <properties>
    <maven.compiler.release>21</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>

  <dependencies>
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
            ],
        },
        {
            'id': 'first-test', 'title': 'Your first JUnit test with HttpClient', 'emoji': '👋', 'level': 'Basic',
            'blocks': [
                ('code', 'java', 'src/test/java/tests/FirstTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import org.junit.jupiter.api.Test;

class FirstTest {

    static final String BASE = System.getProperty("baseUrl", "https://restful-booker.herokuapp.com");
    static final HttpClient CLIENT = HttpClient.newBuilder()
        .connectTimeout(Duration.ofSeconds(10))
        .build();

    @Test
    void getOneBooking() throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(BASE + "/booking/1"))
            .header("Accept", "application/json")
            .timeout(Duration.ofSeconds(10))
            .GET()
            .build();

        HttpResponse<String> response = CLIENT.send(request, HttpResponse.BodyHandlers.ofString());

        assertEquals(200, response.statusCode());
        assertTrue(response.headers().firstValue("Content-Type").orElse("").contains("application/json"));
        assertTrue(response.body().startsWith("{"));
    }
}
''', {'save': 'src/test/java/tests/FirstTest.java'}),
                ('ul', [
                    'One <code>HttpClient</code> is shared by all tests. It keeps connections open and is thread safe.',
                    '<code>connectTimeout</code> limits how long it waits to connect. <code>request.timeout</code> limits the whole call.',
                    '<code>send</code> blocks until the response arrives. <code>sendAsync</code> returns a <code>CompletableFuture</code>.',
                    '<code>headers().firstValue(name)</code> ignores the case of the header name.',
                ]),
                ('try', {'method': 'GET', 'path': '/booking/1'}),
            ],
        },
        {
            'id': 'request', 'title': 'Building requests: query strings, headers, methods', 'emoji': '🧱', 'level': 'Basic',
            'blocks': [
                ('p', 'HttpClient does not build query strings for you. Encode each value with <code>URLEncoder</code>, or names with spaces and symbols will break the URL.'),
                ('code', 'java', 'A small query helper', '''
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.stream.Collectors;

static String query(Map<String, String> params) {
    return params.entrySet().stream()
        .map(e -> URLEncoder.encode(e.getKey(), StandardCharsets.UTF_8) + "="
                + URLEncoder.encode(e.getValue(), StandardCharsets.UTF_8))
        .collect(Collectors.joining("&", "?", ""));
}

URI uri = URI.create(BASE + "/booking" + query(Map.of("firstname", "Mary Ann")));
// https://restful-booker.herokuapp.com/booking?firstname=Mary+Ann
'''),
                ('table', ['HTTP method', 'Builder call'], [
                    ['GET', '<code>.GET()</code>, the default'],
                    ['POST', '<code>.POST(BodyPublishers.ofString(json))</code>'],
                    ['PUT', '<code>.PUT(BodyPublishers.ofString(json))</code>'],
                    ['PATCH', '<code>.method("PATCH", BodyPublishers.ofString(json))</code>'],
                    ['DELETE', '<code>.DELETE()</code>'],
                    ['HEAD', '<code>.HEAD()</code>'],
                ]),
                ('code', 'java', 'Client wide settings', '''
HttpClient client = HttpClient.newBuilder()
    .version(HttpClient.Version.HTTP_2)            // falls back to HTTP/1.1 when needed
    .followRedirects(HttpClient.Redirect.NORMAL)   // follow 3xx except https to http
    .connectTimeout(Duration.ofSeconds(5))
    .cookieHandler(new java.net.CookieManager())   // keeps cookies between calls
    .build();
'''),
                ('warn', 'Some header names are restricted and cannot be set, such as <code>Host</code>, <code>Connection</code> and <code>Content-Length</code>. The client sets them itself.'),
            ],
        },
        {
            'id': 'crud', 'title': 'Create, update and delete (CRUD)', 'emoji': '✍️', 'level': 'Basic',
            'blocks': [
                ('p', 'Bodies are sent with a <code>BodyPublisher</code>. Text blocks keep JSON readable. Remember to set <code>Content-Type</code>, because the client does not guess it.'),
                ('code', 'java', 'src/test/java/tests/CrudTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpRequest.BodyPublishers;
import java.net.http.HttpResponse;
import java.net.http.HttpResponse.BodyHandlers;
import java.util.Base64;
import org.junit.jupiter.api.*;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class CrudTest {

    static final String BASE = System.getProperty("baseUrl", "https://restful-booker.herokuapp.com");
    static final HttpClient CLIENT = HttpClient.newHttpClient();
    static final ObjectMapper JSON = new ObjectMapper();
    static final String BASIC = "Basic " + Base64.getEncoder().encodeToString("admin:password123".getBytes());
    static int bookingId;

    static HttpRequest.Builder to(String path) {
        return HttpRequest.newBuilder(URI.create(BASE + path))
            .header("Accept", "application/json")
            .header("Content-Type", "application/json");
    }

    @Test @Order(1)
    void create() throws Exception {
        String body = """
            {
              "firstname": "Rakesh",
              "lastname": "Panda",
              "totalprice": 250,
              "depositpaid": true,
              "bookingdates": { "checkin": "2026-11-01", "checkout": "2026-11-04" },
              "additionalneeds": "Breakfast"
            }
            """;
        HttpResponse<String> res = CLIENT.send(to("/booking").POST(BodyPublishers.ofString(body)).build(), BodyHandlers.ofString());

        assertEquals(200, res.statusCode());
        JsonNode json = JSON.readTree(res.body());
        bookingId = json.get("bookingid").asInt();
        assertEquals("Rakesh", json.at("/booking/firstname").asText());
    }

    @Test @Order(2)
    void patchOneField() throws Exception {
        HttpRequest req = to("/booking/" + bookingId)
            .header("Authorization", BASIC)
            .method("PATCH", BodyPublishers.ofString("{\\"additionalneeds\\":\\"Dinner\\"}"))
            .build();
        HttpResponse<String> res = CLIENT.send(req, BodyHandlers.ofString());

        assertEquals(200, res.statusCode());
        assertEquals("Dinner", JSON.readTree(res.body()).get("additionalneeds").asText());
    }

    @Test @Order(3)
    void deleteThenGone() throws Exception {
        HttpResponse<Void> del = CLIENT.send(to("/booking/" + bookingId).header("Authorization", BASIC).DELETE().build(), BodyHandlers.discarding());
        assertEquals(201, del.statusCode());   // this API answers 201 to DELETE

        HttpResponse<String> get = CLIENT.send(to("/booking/" + bookingId).GET().build(), BodyHandlers.ofString());
        assertEquals(404, get.statusCode());
        assertEquals("Not Found", get.body());
    }
}
''', {'save': 'src/test/java/tests/CrudTest.java'}),
                ('tip', '<code>BodyHandlers.discarding()</code> skips reading the body when you only need the status, which saves memory on large responses.'),
                ('try', {'method': 'POST', 'path': '/booking', 'body': {'firstname': 'Rakesh', 'lastname': 'Panda', 'totalprice': 250, 'depositpaid': True, 'bookingdates': {'checkin': '2026-11-01', 'checkout': '2026-11-04'}, 'additionalneeds': 'Breakfast'}}),
            ],
        },
        {
            'id': 'json', 'title': 'Reading JSON and asserting well', 'emoji': '🔍', 'level': 'Intermediate',
            'blocks': [
                ('p', 'Parse the body once into a <code>JsonNode</code> with Jackson. Read nested values with JSON Pointer paths. Turn the body into a record when you want to compare whole objects.'),
                ('code', 'java', 'JsonNode and records', '''
JsonNode b = JSON.readTree(res.body());

assertAll(
    () -> assertTrue(b.get("firstname").isTextual()),
    () -> assertTrue(b.get("totalprice").canConvertToInt()),
    () -> assertTrue(b.get("depositpaid").isBoolean()),
    () -> assertTrue(b.at("/bookingdates/checkin").asText().matches("\\\\d{4}-\\\\d{2}-\\\\d{2}")),
    () -> assertTrue(b.path("additionalneeds").isMissingNode() || b.get("additionalneeds").isTextual()));

// Typed: map straight to records
record Dates(String checkin, String checkout) {}
@JsonIgnoreProperties(ignoreUnknown = true)
record Booking(String firstname, String lastname, int totalprice, boolean depositpaid, Dates bookingdates) {}

Booking booking = JSON.readValue(res.body(), Booking.class);
assertEquals("2026-11-01", booking.bookingdates().checkin());
'''),
                ('p', 'For the response as a whole, write a small reusable assertion helper. When it fails, it prints the status and the body, which saves a lot of debugging time.'),
                ('code', 'java', 'A helpful status assertion', '''
static void assertStatus(int expected, HttpResponse<String> res) {
    assertEquals(expected, res.statusCode(),
        () -> res.request().method() + " " + res.uri() + " gave " + res.statusCode() + "\\n" + res.body());
}
'''),
                ('tip', '<code>path("x")</code> returns a missing node when the field is absent, while <code>get("x")</code> returns null. Use <code>path</code> when a field is optional to avoid a <code>NullPointerException</code>.'),
            ],
        },
        {
            'id': 'auth', 'title': 'Authentication and cookies', 'emoji': '🔐', 'level': 'Intermediate',
            'blocks': [
                ('code', 'java', 'Token cookie, Basic and Bearer', '''
// 1. Get the token
HttpResponse<String> login = CLIENT.send(
    to("/auth").POST(BodyPublishers.ofString("""
        {"username":"admin","password":"password123"}""")).build(),
    BodyHandlers.ofString());
String token = JSON.readTree(login.body()).get("token").asText();

// 2a. Send it as a cookie header (Restful Booker)
to("/booking/" + id).header("Cookie", "token=" + token);

// 2b. Basic auth, built by hand so it is sent on the first request
String basic = Base64.getEncoder().encodeToString("admin:password123".getBytes(StandardCharsets.UTF_8));
to("/booking/" + id).header("Authorization", "Basic " + basic);

// 2c. Bearer token
to("/orders").header("Authorization", "Bearer " + System.getenv("API_TOKEN"));
'''),
                ('p', 'A <code>CookieManager</code> on the client stores cookies the server sets with <code>Set-Cookie</code> and sends them back on later calls, like a browser. You can also add one yourself.'),
                ('code', 'java', 'Cookie manager', '''
CookieManager cookies = new CookieManager();
HttpClient client = HttpClient.newBuilder().cookieHandler(cookies).build();

HttpCookie c = new HttpCookie("token", token);
c.setPath("/");
cookies.getCookieStore().add(URI.create(BASE), c);   // now sent with every call to BASE
'''),
                ('warn', 'The JDK <code>Authenticator</code> only answers a 401 challenge. Restful Booker answers 403, so build the <code>Authorization</code> header yourself as shown.'),
                ('h', 'Negative checks to always include'),
                ('ul', [
                    'No auth gives 401 or 403.',
                    'A made up token is refused.',
                    'The booking is unchanged after a refused update.',
                ]),
            ],
        },
        {
            'id': 'async', 'title': 'Async calls and parallel requests', 'emoji': '⚡', 'level': 'Intermediate',
            'blocks': [
                ('p', '<code>sendAsync</code> returns at once with a <code>CompletableFuture</code>. Start many calls together and wait for all of them. This is how you check that an API behaves under a little concurrency.'),
                ('code', 'java', 'src/test/java/tests/AsyncTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.stream.IntStream;
import org.junit.jupiter.api.Test;

class AsyncTest {

    static final String BASE = System.getProperty("baseUrl", "https://restful-booker.herokuapp.com");
    static final HttpClient CLIENT = HttpClient.newHttpClient();

    @Test
    void tenReadsAtOnce() {
        List<CompletableFuture<HttpResponse<String>>> calls = IntStream.rangeClosed(1, 10)
            .mapToObj(i -> HttpRequest.newBuilder(URI.create(BASE + "/booking")).build())
            .map(req -> CLIENT.sendAsync(req, HttpResponse.BodyHandlers.ofString()))
            .toList();

        CompletableFuture.allOf(calls.toArray(CompletableFuture[]::new)).join();

        calls.forEach(c -> assertEquals(200, c.join().statusCode()));
    }
}
''', {'save': 'src/test/java/tests/AsyncTest.java'}),
                ('tip', 'In Java 21 you can also start one virtual thread per call with <code>Executors.newVirtualThreadPerTaskExecutor()</code> and use the simple blocking <code>send</code> inside each. The code reads top to bottom and still runs in parallel.'),
            ],
        },
        {
            'id': 'data-driven', 'title': 'Data driven tests', 'emoji': '📊', 'level': 'Intermediate',
            'blocks': [
                ('code', 'java', 'src/test/java/tests/DataDrivenTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class DataDrivenTest {

    static final String BASE = System.getProperty("baseUrl", "https://restful-booker.herokuapp.com");
    static final HttpClient CLIENT = HttpClient.newHttpClient();

    @ParameterizedTest(name = "{0} gives {1}")
    @CsvSource({
        "/ping,           201",
        "/booking,        200",
        "/booking/1,      200",
        "/booking/abc,    404",
        "/booking/999999, 404",
        "/nothing-here,   404"
    })
    void statusPerPath(String path, int expected) throws Exception {
        HttpResponse<Void> res = CLIENT.send(
            HttpRequest.newBuilder(URI.create(BASE + path)).build(),
            HttpResponse.BodyHandlers.discarding());
        assertEquals(expected, res.statusCode());
    }
}
''', {'save': 'src/test/java/tests/DataDrivenTest.java'}),
                ('qa', 'A table of path and expected status is a quick way to cover routing, missing ids and wrong id types in one place. Add rows whenever a bug is found so it never returns.'),
            ],
        },
        {
            'id': 'mocking', 'title': 'A stub server with the JDK alone', 'emoji': '🎭', 'level': 'Advanced',
            'blocks': [
                ('p', 'The JDK includes a small HTTP server in <code>com.sun.net.httpserver</code>. Use it as a stub for a service your code depends on, or to test your own client code against answers you control, including errors and slow responses.'),
                ('code', 'java', 'src/test/java/tests/StubServerTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;

import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpTimeoutException;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import org.junit.jupiter.api.*;

class StubServerTest {

    static HttpServer server;
    static String base;
    static final HttpClient CLIENT = HttpClient.newHttpClient();

    @BeforeAll
    static void start() throws Exception {
        server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);   // port 0 picks a free port
        server.createContext("/payments", ex -> {
            byte[] body = "{\\"status\\":\\"APPROVED\\"}".getBytes(StandardCharsets.UTF_8);
            ex.getResponseHeaders().add("Content-Type", "application/json");
            ex.sendResponseHeaders(200, body.length);
            ex.getResponseBody().write(body);
            ex.close();
        });
        server.createContext("/slow", ex -> {
            try { Thread.sleep(2_000); } catch (InterruptedException ignored) { }
            ex.sendResponseHeaders(204, -1);
            ex.close();
        });
        server.start();
        base = "http://127.0.0.1:" + server.getAddress().getPort();
    }

    @Test
    void stubbedPayment() throws Exception {
        HttpResponse<String> res = CLIENT.send(
            HttpRequest.newBuilder(URI.create(base + "/payments")).POST(HttpRequest.BodyPublishers.ofString("{}")).build(),
            HttpResponse.BodyHandlers.ofString());
        assertEquals(200, res.statusCode());
        assertTrue(res.body().contains("APPROVED"));
    }

    @Test
    void slowAnswerHitsTheTimeout() {
        HttpRequest req = HttpRequest.newBuilder(URI.create(base + "/slow")).timeout(Duration.ofMillis(300)).build();
        assertThrows(HttpTimeoutException.class, () -> CLIENT.send(req, HttpResponse.BodyHandlers.discarding()));
    }

    @AfterAll
    static void stop() { server.stop(0); }
}
''', {'save': 'src/test/java/tests/StubServerTest.java'}),
                ('tip', 'The timeout test proves your code gives up on a slow service instead of hanging forever. Production outages often start with a missing timeout.'),
            ],
        },
        {
            'id': 'schema-framework', 'title': 'Schema checks and a small framework', 'emoji': '🏗️', 'level': 'Advanced',
            'blocks': [
                ('p', 'Wrap the raw client in a small class so tests stay short. Add schema validation with networknt, which reads the schema and the body as plain strings.'),
                ('code', 'java', 'src/test/java/tests/support/Api.java', '''
package tests.support;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

public final class Api {

    public static final String BASE = System.getProperty("baseUrl", "https://restful-booker.herokuapp.com");
    private static final HttpClient CLIENT = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build();
    private static final ObjectMapper JSON = new ObjectMapper();

    public record Result(int status, String body, HttpResponse<String> raw) {
        public JsonNode json() {
            try { return JSON.readTree(body); }
            catch (IOException e) { throw new AssertionError("Body is not JSON: " + body, e); }
        }
    }

    public static Result call(String method, String path, Object body, String... headers) {
        try {
            HttpRequest.Builder b = HttpRequest.newBuilder(URI.create(BASE + path))
                .timeout(Duration.ofSeconds(15))
                .header("Accept", "application/json");
            if (headers.length > 0) b.headers(headers);
            HttpRequest.BodyPublisher pub = HttpRequest.BodyPublishers.noBody();
            if (body != null) {
                b.header("Content-Type", "application/json");
                pub = HttpRequest.BodyPublishers.ofString(body instanceof String s ? s : JSON.writeValueAsString(body));
            }
            HttpResponse<String> res = CLIENT.send(b.method(method, pub).build(), HttpResponse.BodyHandlers.ofString());
            return new Result(res.statusCode(), res.body(), res);
        } catch (IOException | InterruptedException e) {
            throw new RuntimeException(method + " " + path + " failed", e);
        }
    }

    public static Result get(String path, String... headers)                { return call("GET", path, null, headers); }
    public static Result post(String path, Object body, String... headers)  { return call("POST", path, body, headers); }
    public static Result patch(String path, Object body, String... headers) { return call("PATCH", path, body, headers); }
    public static Result delete(String path, String... headers)             { return call("DELETE", path, null, headers); }

    private Api() { }
}
''', {'save': 'src/test/java/tests/support/Api.java'}),
                ('code', 'java', 'src/test/java/tests/SchemaTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;

import com.networknt.schema.InputFormat;
import com.networknt.schema.Schema;
import com.networknt.schema.SchemaRegistry;
import com.networknt.schema.SpecificationVersion;
import org.junit.jupiter.api.Test;
import tests.support.Api;

class SchemaTest {

    static final Schema BOOKING = SchemaRegistry.withDefaultDialect(SpecificationVersion.DRAFT_7).getSchema("""
        {
          "type": "object",
          "required": ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"],
          "properties": {
            "firstname":   { "type": "string" },
            "lastname":    { "type": "string" },
            "totalprice":  { "type": "integer", "minimum": 0 },
            "depositpaid": { "type": "boolean" },
            "bookingdates": {
              "type": "object",
              "required": ["checkin", "checkout"]
            }
          }
        }
        """);

    @Test
    void bookingMatchesSchema() {
        Api.Result res = Api.get("/booking/1");
        assertEquals(200, res.status());
        var errors = BOOKING.validate(res.body(), InputFormat.JSON);
        assertTrue(errors.isEmpty(), () -> errors.toString());
    }
}
''', {'save': 'src/test/java/tests/SchemaTest.java'}),
            ],
        },
        {
            'id': 'performance', 'title': 'A quick load smoke with virtual threads', 'emoji': '📈', 'level': 'Expert',
            'blocks': [
                ('p', 'This is not a replacement for a load testing tool, but a quick check that an endpoint stays fast under a small burst. Send 50 calls at once, collect the times, and check the 95th percentile. That is the time 95 out of 100 calls finish within.'),
                ('code', 'java', 'src/test/java/tests/LoadSmokeTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.junit.jupiter.api.Test;

class LoadSmokeTest {

    static final String BASE = System.getProperty("baseUrl", "https://restful-booker.herokuapp.com");

    @Test
    void fiftyCallsStayFast() throws Exception {
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest req = HttpRequest.newBuilder(URI.create(BASE + "/booking/1")).build();
        List<Long> times = Collections.synchronizedList(new ArrayList<>());

        try (var pool = Executors.newVirtualThreadPerTaskExecutor()) {
            List<Future<Integer>> results = new ArrayList<>();
            for (int i = 0; i < 50; i++) {
                results.add(pool.submit(() -> {
                    long start = System.nanoTime();
                    int status = client.send(req, HttpResponse.BodyHandlers.discarding()).statusCode();
                    times.add((System.nanoTime() - start) / 1_000_000);
                    return status;
                }));
            }
            for (Future<Integer> f : results) assertEquals(200, f.get());
        }

        List<Long> sorted = times.stream().sorted().toList();
        long p95 = sorted.get((int) Math.ceil(sorted.size() * 0.95) - 1);
        System.out.println("p95 = " + p95 + " ms");
        assertTrue(p95 < 3_000, "95% of calls should finish within 3 seconds, p95 was " + p95);
    }
}
''', {'save': 'src/test/java/tests/LoadSmokeTest.java'}),
                ('h', 'The percentile formula'),
                ('p', 'Sort the n times from fastest to slowest. The p95 is the value at position'),
                ('p', '<span class="eqn">index = ⌈ 0.95 × n ⌉ − 1</span>'),
                ('p', 'counting from 0. With 50 calls that is ⌈ 47.5 ⌉ − 1 = 47, the 48th fastest call.'),
                ('warn', 'Never run load against a shared public API such as Restful Booker beyond a small burst. Use your own test environment for real load testing with tools such as Gatling, k6 or JMeter.'),
            ],
        },
        {
            'id': 'expert', 'title': 'Expert topics: retries, TLS, HTTP/2 and CI', 'emoji': '🧠', 'level': 'Expert',
            'blocks': [
                ('code', 'java', 'Retry with backoff, only where it is safe', '''
static HttpResponse<String> sendWithRetry(HttpClient c, HttpRequest r, int attempts) throws Exception {
    long wait = 200;
    for (int i = 1; ; i++) {
        try {
            HttpResponse<String> res = c.send(r, HttpResponse.BodyHandlers.ofString());
            if (res.statusCode() < 500 || i == attempts) return res;   // retry 5xx only
        } catch (java.io.IOException e) {
            if (i == attempts) throw e;                                 // retry network errors
        }
        Thread.sleep(wait);
        wait *= 2;                                                      // 200, 400, 800 ms
    }
}
'''),
                ('ul', [
                    'Only retry calls that are safe to repeat: GET, PUT and DELETE. Retrying a POST can create two bookings.',
                    'Custom certificates: pass an <code>SSLContext</code> to <code>HttpClient.newBuilder().sslContext(...)</code> to trust a test environment\'s certificate. Never turn off certificate checks in shared code.',
                    'HTTP/2: <code>response.version()</code> tells you which version was used. Check it when the API claims HTTP/2 support.',
                    'Proxies: <code>.proxy(ProxySelector.of(new InetSocketAddress("proxy", 8080)))</code> routes calls through a corporate proxy or a tool such as Burp for security testing.',
                    'CI: the same GitHub Actions workflow as any Maven project. Run <code>mvn -B test -DbaseUrl=...</code> and upload <code>target/surefire-reports</code>.',
                ]),
            ],
        },
        {
            'id': 'essentials', 'title': 'Real project essentials: environments, secrets, logging with redaction and cleanup', 'emoji': '🧳', 'level': 'Intermediate',
            'blocks': [
                ('p', 'Even with no libraries, a native suite can behave like a professional one. The JDK already has everything needed: system properties and environment variables for config, <code>System.Logger</code> for logs, <code>UUID</code> for unique data, and JUnit hooks for cleanup. The one rule that matters most is to hide secrets before anything is logged.'),
                ('code', 'java', 'src/test/java/tests/support/HttpLog.java', '''
package tests.support;

import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Set;
import java.util.stream.Collectors;

public final class HttpLog {

    private static final System.Logger LOG = System.getLogger("api");
    private static final Set<String> SECRET = Set.of("authorization", "cookie", "x-api-key");

    private HttpLog() { }

    /** Headers as text, with secret values replaced, so logs are safe to share. */
    public static String headers(HttpRequest req) {
        return req.headers().map().entrySet().stream()
            .map(e -> e.getKey() + ": " + (SECRET.contains(e.getKey().toLowerCase()) ? "***" : String.join(",", e.getValue())))
            .collect(Collectors.joining(", "));
    }

    public static void log(HttpResponse<String> res, long ms) {
        HttpRequest req = res.request();
        LOG.log(System.Logger.Level.INFO, "{0} {1} -> {2} in {3} ms [{4}]", req.method(), req.uri(), res.statusCode(), ms, headers(req));
        if (res.statusCode() >= 400) LOG.log(System.Logger.Level.WARNING, "body: {0}", res.body());
    }
}
''', {'save': 'src/test/java/tests/support/HttpLog.java'}),
                ('code', 'java', 'src/test/java/tests/EssentialsTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import tests.support.HttpLog;

class EssentialsTest {

    static final String BASE = System.getProperty("baseUrl", System.getenv().getOrDefault("BASE_URL", "https://restful-booker.herokuapp.com"));
    static final String USER = System.getenv().getOrDefault("API_USER", "admin");
    static final String PASSWORD = System.getenv().getOrDefault("API_PASSWORD", "password123");   // practice API only
    static final HttpClient CLIENT = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build();

    private final List<String> created = new ArrayList<>();

    static HttpResponse<String> send(String method, String path, String json, String... headers) throws Exception {
        HttpRequest.Builder b = HttpRequest.newBuilder(URI.create(BASE + path)).timeout(Duration.ofSeconds(15))
            .header("Accept", "application/json");
        if (headers.length > 0) b.headers(headers);
        if (json != null) b.header("Content-Type", "application/json");
        HttpRequest req = b.method(method, json == null ? HttpRequest.BodyPublishers.noBody() : HttpRequest.BodyPublishers.ofString(json)).build();
        long start = System.nanoTime();
        HttpResponse<String> res = CLIENT.send(req, HttpResponse.BodyHandlers.ofString());
        HttpLog.log(res, (System.nanoTime() - start) / 1_000_000);
        return res;
    }

    static String token() throws Exception {
        String body = send("POST", "/auth", "{\\"username\\":\\"%s\\",\\"password\\":\\"%s\\"}".formatted(USER, PASSWORD)).body();
        return body.replaceAll(".*\\"token\\"\\\\s*:\\\\s*\\"([^\\"]+)\\".*", "$1");
    }

    @AfterEach
    void cleanUp() throws Exception {
        if (created.isEmpty()) return;
        String cookie = "token=" + token();
        for (String id : created) send("DELETE", "/booking/" + id, null, "Cookie", cookie);
        created.clear();
    }

    @Test
    void uniqueGuestIsStoredAndCleanedUp() throws Exception {
        String guest = "Guest-" + UUID.randomUUID().toString().substring(0, 8);
        String json = """
            {"firstname":"%s","lastname":"Native","totalprice":420,"depositpaid":true,
             "bookingdates":{"checkin":"2026-12-20","checkout":"2026-12-22"}}""".formatted(guest);

        HttpResponse<String> res = send("POST", "/booking", json);
        assertEquals(200, res.statusCode(), res.body());
        String id = res.body().replaceAll(".*\\"bookingid\\"\\\\s*:\\\\s*(\\\\d+).*", "$1");
        created.add(id);

        HttpResponse<String> read = send("GET", "/booking/" + id, null);
        assertTrue(read.body().contains(guest), read.body());
        assertEquals("Cookie: ***", HttpLog.headers(HttpRequest.newBuilder(URI.create(BASE)).header("Cookie", "token=abc").build()));
    }
}
''', {'save': 'src/test/java/tests/EssentialsTest.java'}),
                ('code', 'bash', 'Run it', '''
mvn test -Dtest=EssentialsTest -DbaseUrl=http://localhost:3001
API_PASSWORD="$QA_PASSWORD" BASE_URL=https://qa.booker.example mvn test
'''),
                ('ul', [
                    '<code>System.Logger</code> is part of the JDK and is routed to whatever logging framework the project already uses, so there is nothing extra to set up.',
                    'Redact secrets in one place, <code>HttpLog.headers</code>, and test the redaction itself, as the last line of the test does.',
                    'Unique names from <code>UUID</code> keep parallel CI jobs from reading each other\'s bookings.',
                ]),
                ('warn', 'The regular expressions here keep the example free of libraries. In a real suite, parse JSON with Jackson as the schema lesson does. Regex parsing breaks as soon as the response format changes.'),
            ],
        },
        {
            'id': 'latest', 'title': 'What is new in Java for HTTP testing, and how it helps at work', 'emoji': '🆕', 'level': 'Expert',
            'blocks': [
                ('table', ['Feature', 'Since', 'How it helps an API tester'], [
                    ['Java 25 LTS', 'September 2025', 'The current long term support release, a good target for new CI images'],
                    ['Compact source files and instance <code>main</code>', 'Java 25 (JEP 512)', 'A health check or data seeding script in a few lines, run with <code>java Seed.java</code>'],
                    ['Module import declarations', 'Java 25 (JEP 511)', '<code>import module java.net.http;</code> brings in the whole HTTP client in one line'],
                    ['Scoped values', 'Java 25 (JEP 506)', 'Pass a request id or test run id safely through virtual threads without thread locals'],
                    ['Virtual threads', 'Java 21', 'Thousands of concurrent requests for a quick load smoke, as in the earlier lesson'],
                    ['HTTP/3 in <code>HttpClient</code>', 'Java 26 (JEP 517, March 2026)', 'Opt in with <code>HttpClient.Version.HTTP_3</code> to test gateways that speak HTTP/3 over QUIC. HTTP/2 has been there since Java 11'],
                ]),
                ('code', 'java', 'Seed.java on Java 25 (run with: java Seed.java)', '''
import module java.net.http;

void main() throws Exception {
    var client = HttpClient.newHttpClient();
    for (var name : List.of("Asha", "Ben", "Chen")) {
        var body = """
            {"firstname":"%s","lastname":"Seed","totalprice":100,"depositpaid":true,
             "bookingdates":{"checkin":"2026-12-01","checkout":"2026-12-02"}}""".formatted(name);
        var req = HttpRequest.newBuilder(URI.create("http://localhost:3001/booking"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(body)).build();
        IO.println(name + " -> " + client.send(req, HttpResponse.BodyHandlers.ofString()).body());
    }
}
'''),
                ('code', 'java', 'src/test/java/tests/ProtocolTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import org.junit.jupiter.api.Test;

class ProtocolTest {

    static final String BASE = System.getProperty("baseUrl", "https://restful-booker.herokuapp.com");

    @Test
    void reportsWhichHttpVersionWasUsed() throws Exception {
        HttpClient client = HttpClient.newBuilder().version(HttpClient.Version.HTTP_2).build();
        HttpResponse<String> res = client.send(HttpRequest.newBuilder(URI.create(BASE + "/booking/1")).build(),
            HttpResponse.BodyHandlers.ofString());
        assertEquals(200, res.statusCode());
        // HTTP_2 is a preference. Over plain http, or when the server cannot, the client falls back to HTTP/1.1
        assertTrue(res.version() == HttpClient.Version.HTTP_2 || res.version() == HttpClient.Version.HTTP_1_1, res.version().toString());
        System.out.println("negotiated " + res.version());
    }
}
''', {'save': 'src/test/java/tests/ProtocolTest.java'}),
                ('tip', 'Before you move a suite to a new Java release at work, run it on the new JDK in a separate CI job for a week. Compile warnings about deprecated APIs are your to do list.'),
            ],
        },
        {
            'id': 'scenario', 'title': 'Real world scenario: a release gate health check', 'emoji': '🚦', 'level': 'Scenario',
            'blocks': [
                ('p', 'Before a release goes live, the team wants a quick yes or no: is the booking service healthy and does a full booking journey still work? The check must run anywhere a JDK exists, finish in seconds, and print a clear result.'),
                ('flow', [
                    ('Ping', '<code>GET /ping</code> must answer 201 within 2 seconds.'),
                    ('Log in', '<code>POST /auth</code> returns a token.'),
                    ('Create', '<code>POST /booking</code> with a unique name returns an id.'),
                    ('Read', '<code>GET /booking/{id}</code> returns the same data.'),
                    ('Protected', '<code>DELETE</code> without a token gives 403.'),
                    ('Clean up', '<code>DELETE</code> with the token gives 201, then <code>GET</code> gives 404.'),
                    ('Verdict', 'Exit code 0 releases, anything else blocks the pipeline.'),
                ]),
                ('code', 'java', 'src/test/java/tests/ReleaseGateTest.java', '''
package tests;

import static org.junit.jupiter.api.Assertions.*;

import java.util.Map;
import org.junit.jupiter.api.Test;
import tests.support.Api;

class ReleaseGateTest {

    @Test
    void bookingJourneyIsHealthy() {
        long start = System.nanoTime();
        assertEquals(201, Api.get("/ping").status());
        assertTrue((System.nanoTime() - start) / 1_000_000 < 2_000, "ping too slow");

        String token = Api.post("/auth", Map.of("username", "admin", "password", "password123"))
            .json().get("token").asText();

        String guest = "Gate" + System.currentTimeMillis();
        Api.Result created = Api.post("/booking", Map.of(
            "firstname", guest, "lastname", "Check", "totalprice", 99, "depositpaid", false,
            "bookingdates", Map.of("checkin", "2026-12-24", "checkout", "2026-12-26")));
        assertEquals(200, created.status());
        int id = created.json().get("bookingid").asInt();

        assertEquals(guest, Api.get("/booking/" + id).json().get("firstname").asText());
        assertEquals(403, Api.delete("/booking/" + id).status());
        assertEquals(201, Api.delete("/booking/" + id, "Cookie", "token=" + token).status());
        assertEquals(404, Api.get("/booking/" + id).status());
    }
}
''', {'save': 'src/test/java/tests/ReleaseGateTest.java'}),
            ],
        },
    ],
    'quiz': [
        {'lv': 'e', 'q': 'Which package holds the JDK\'s modern HTTP client?', 'o': ['<code>java.net.http</code>', '<code>java.io.http</code>', '<code>javax.servlet</code>', '<code>java.util.http</code>'], 'a': 0, 'hint': 'Added in Java 11.', 'why': '<code>java.net.http</code> holds <code>HttpClient</code>, <code>HttpRequest</code> and <code>HttpResponse</code>.'},
        {'lv': 'e', 'q': 'How do you send a PATCH request?', 'o': ['<code>.PATCH(body)</code>', '<code>.method("PATCH", body)</code>', '<code>.patch(body)</code>', 'PATCH is not supported'], 'a': 1, 'hint': 'Only the common methods have their own builder call.', 'why': 'The builder has <code>GET</code>, <code>POST</code>, <code>PUT</code>, <code>DELETE</code> and <code>HEAD</code>. Every other method uses <code>method(name, publisher)</code>.'},
        {'lv': 'm', 'q': 'Your POST gets an error because the server thinks the body is not JSON. What is missing?', 'o': ['<code>Accept</code> header', '<code>Content-Type: application/json</code>', 'A timeout', 'HTTP/2'], 'a': 1, 'hint': 'The client never guesses the body type.', 'why': 'HttpClient sends bytes. The server reads the <code>Content-Type</code> header to know they are JSON.'},
        {'lv': 'm', 'q': 'You search for <code>Mary Ann</code> by building <code>"?firstname=" + name</code>. What goes wrong?', 'o': ['Nothing', 'The space makes the URI invalid, so encode it with URLEncoder', 'Query strings are not allowed', 'It becomes a POST'], 'a': 1, 'hint': 'Spaces are not allowed in a URI.', 'why': '<code>URI.create</code> throws on the space. <code>URLEncoder.encode</code> turns it into <code>Mary+Ann</code>.'},
        {'lv': 'h', 'q': 'Why share one <code>HttpClient</code> across tests instead of creating one per request?', 'o': ['It is required by JUnit', 'It reuses connections and threads, so calls are faster', 'Clients expire after one call', 'To share cookies with the browser'], 'a': 1, 'hint': 'Think about connection pools.', 'why': 'A client keeps a connection pool and is thread safe. Creating one per call wastes time on new connections.'},
        {'lv': 'h', 'q': 'With 20 sorted response times, which position is the p95 (counting from 0)?', 'o': ['17', '18', '19', '20'], 'a': 1, 'hint': 'index = ceil(0.95 × n) − 1', 'why': '⌈0.95 × 20⌉ − 1 = 19 − 1 = 18, the 19th fastest time.'},
        {'lv': 'x', 'q': 'Which calls are safe to retry automatically after a network error?', 'o': ['Any call', 'GET, PUT and DELETE, because repeating them gives the same result', 'Only POST', 'None'], 'a': 1, 'hint': 'Look up idempotent methods.', 'why': 'Idempotent methods leave the same state when repeated. A repeated POST may create a duplicate booking.'},
        {'lv': 'x', 'q': 'A test against a stub server waits forever when the stub hangs. What fixes it?', 'o': ['<code>request.timeout(Duration)</code>', 'A bigger heap', '<code>BodyHandlers.discarding()</code>', 'HTTP/2'], 'a': 0, 'hint': 'HttpClient has no total timeout by default.', 'why': 'Without <code>timeout</code> on the request, <code>send</code> can wait indefinitely. With it, the call fails with <code>HttpTimeoutException</code>.'},
    ],
}
