TRACK = {
    'id': 'java-rest-assured', 'lang': 'java', 'tool': 'rest-assured',
    'title': 'Rest Assured with Java', 'emoji': '☕',
    'tagline': 'The most used Java library for API tests. Readable given, when, then tests with TestNG.',
    'intro': 'Rest Assured wraps HTTP calls in a small language that reads like a test case: <b>given</b> this request, <b>when</b> I call this endpoint, <b>then</b> the response should look like this. It handles JSON, XML, cookies, auth, logging and schema checks, and it fits any Java project, including Selenium frameworks that need fast API setup steps.',
    'stack': [
        ('Java', '21 LTS', 'Rest Assured 6 needs Java 17 or newer'),
        ('Rest Assured', '6.2.0', 'requests and checks'),
        ('TestNG', '7.12.0', 'runner, groups, data providers'),
        ('Jackson', '2.22.4', 'turns JSON into Java objects'),
        ('json-schema-validator', '6.2.0', 'contract checks'),
        ('Maven', '3.9', 'build and dependencies'),
    ],
    'sections': [
        {
            'id': 'why', 'title': 'What API automation is and what to check', 'emoji': '🎯', 'level': 'Basic',
            'blocks': [
                ('p', 'An API test sends a real HTTP request to a service and checks the response, with no browser involved. Because there is no page to load, a single API test runs in milliseconds, so a suite of a thousand checks can finish in a minute. This is why most teams keep many API tests in the middle of their test pyramid, with fewer slow UI tests on top.'),
                ('table', ['Check', 'Example on Restful Booker', 'Why'], [
                    ['Status code', '<code>GET /booking/1</code> gives 200', 'The first sign that the call worked'],
                    ['Body values', '<code>firstname</code> is <code>Sally</code>', 'Proves the right data came back'],
                    ['Body shape', 'Every booking has <code>bookingdates.checkin</code>', 'Catches renamed or missing fields'],
                    ['Headers', '<code>Content-Type</code> contains <code>application/json</code>', 'Clients parse based on it'],
                    ['Negative cases', '<code>PUT</code> without a token gives 403', 'Security and validation rules hold'],
                    ['Time', 'Answer in under 2 seconds', 'Catches slow endpoints early'],
                ]),
                ('qa', 'In a Selenium or Playwright UI framework, API calls are the fastest way to create test data. Create a booking with one POST, then open the UI and check it shows up. This cuts minutes from every UI test.'),
                ('p', 'Each test follows <b>Arrange, Act, Assert</b>. Arrange builds the request, Act sends it, Assert checks the response. Rest Assured maps these to <code>given()</code>, <code>when()</code> and <code>then()</code>.'),
            ],
        },
        {
            'id': 'setup', 'title': 'Project setup with Maven', 'emoji': '🧰', 'level': 'Basic',
            'blocks': [
                ('p', 'Create a Maven project and add the dependencies below. Test code lives in <code>src/test/java</code>, and files such as JSON schemas live in <code>src/test/resources</code>.'),
                ('code', 'xml', 'pom.xml', '''
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.brainybytes</groupId>
  <artifactId>booker-api-tests</artifactId>
  <version>1.0</version>

  <properties>
    <maven.compiler.release>21</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>

  <dependencies>
    <dependency>
      <groupId>io.rest-assured</groupId>
      <artifactId>rest-assured</artifactId>
      <version>6.2.0</version>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>io.rest-assured</groupId>
      <artifactId>json-schema-validator</artifactId>
      <version>6.2.0</version>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.testng</groupId>
      <artifactId>testng</artifactId>
      <version>7.12.0</version>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-databind</artifactId>
      <version>2.22.4</version>
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
                ('code', 'plain', 'Project layout', '''
booker-api-tests/
├── pom.xml
└── src/test/
    ├── java/tests/
    │   ├── FirstTest.java
    │   ├── CrudTest.java
    │   └── ...
    └── resources/schemas/
        └── booking-schema.json
'''),
                ('p', 'Rest Assured is used through static imports, so the code reads like plain English. Add these at the top of every test class.'),
                ('code', 'java', 'The imports you will use most', '''
import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
'''),
                ('tip', 'Run everything with <code>mvn test</code>. Run one class with <code>mvn test -Dtest=FirstTest</code>. Point the suite at another server with <code>mvn test -DbaseUrl=http://localhost:3001</code>, which the examples below read with <code>System.getProperty</code>.'),
            ],
        },
        {
            'id': 'first-test', 'title': 'Your first test: GET a booking', 'emoji': '👋', 'level': 'Basic',
            'blocks': [
                ('p', 'This test asks for booking 1 and checks three things: the status, the content type, and that the first name is a non empty string. Restful Booker resets its data, so the exact name can change, which is why the check is about the shape rather than one value.'),
                ('code', 'java', 'src/test/java/tests/FirstTest.java', '''
package tests;

import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;

public class FirstTest {

    @BeforeClass
    public void setUp() {
        RestAssured.baseURI = System.getProperty("baseUrl", "https://restful-booker.herokuapp.com");
    }

    @Test
    public void pingSaysTheApiIsUp() {
        when()
            .get("/ping")
        .then()
            .statusCode(201);   // Restful Booker answers 201 to a health check
    }

    @Test
    public void getOneBooking() {
        given()
            .accept(ContentType.JSON)
        .when()
            .get("/booking/1")
        .then()
            .log().ifValidationFails()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("firstname", not(emptyOrNullString()))
            .body("bookingdates.checkin", matchesPattern("\\\\d{4}-\\\\d{2}-\\\\d{2}"));
    }
}
''', {'save': 'src/test/java/tests/FirstTest.java'}),
                ('ul', [
                    '<code>given()</code> holds everything about the request: headers, params, body, auth.',
                    '<code>when()</code> sends it with an HTTP method such as <code>get</code> or <code>post</code>.',
                    '<code>then()</code> starts the checks. Each <code>body(path, matcher)</code> reads a value with a GPath expression and compares it with a Hamcrest matcher.',
                    '<code>log().ifValidationFails()</code> prints the full request and response only when a check fails, which keeps passing runs quiet.',
                ]),
                ('try', {'method': 'GET', 'path': '/booking/1'}),
            ],
        },
        {
            'id': 'request', 'title': 'Building requests: params, headers and cookies', 'emoji': '🧱', 'level': 'Basic',
            'blocks': [
                ('p', 'Real requests carry more than a path. Rest Assured gives a method for each part of the request.'),
                ('code', 'java', 'Path params, query params, headers and cookies', '''
// Path parameter: fills {id} in the path
given().pathParam("id", 1)
.when().get("/booking/{id}")
.then().statusCode(200);

// Query parameters: /booking?firstname=Sally&lastname=Brown
given()
    .queryParam("firstname", "Sally")
    .queryParam("lastname", "Brown")
.when().get("/booking")
.then().statusCode(200).body("bookingid", everyItem(greaterThan(0)));

// Headers and cookies
given()
    .header("Accept", "application/json")
    .header("X-Request-Id", java.util.UUID.randomUUID().toString())
    .cookie("token", "abc123")
.when().get("/booking/1");
'''),
                ('table', ['Part of the request', 'Rest Assured method', 'Example'], [
                    ['Path parameter', '<code>pathParam("id", 1)</code>', '<code>/booking/{id}</code>'],
                    ['Query parameter', '<code>queryParam("firstname", "Sally")</code>', '<code>?firstname=Sally</code>'],
                    ['Header', '<code>header("Accept", "application/json")</code>', 'Any header'],
                    ['Cookie', '<code>cookie("token", token)</code>', 'Session or token cookie'],
                    ['Form field', '<code>formParam("user", "admin")</code>', 'HTML style forms'],
                    ['Content type', '<code>contentType(ContentType.JSON)</code>', 'Sets the Content-Type header'],
                ]),
                ('tip', 'The list endpoint returns <code>[{"bookingid":1},{"bookingid":2}]</code>. On a JSON array, the GPath <code>bookingid</code> collects the field from every item, so <code>everyItem(greaterThan(0))</code> checks them all at once.'),
            ],
        },
        {
            'id': 'crud', 'title': 'Create, update and delete (CRUD)', 'emoji': '✍️', 'level': 'Basic',
            'blocks': [
                ('p', 'There are three common ways to send a JSON body: a text block, a <code>Map</code>, or a Java object that Jackson turns into JSON. All three produce the same request.'),
                ('code', 'java', 'src/test/java/tests/CrudTest.java', '''
package tests;

import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import java.util.Map;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;

public class CrudTest {

    private int bookingId;

    @BeforeClass
    public void setUp() {
        RestAssured.baseURI = System.getProperty("baseUrl", "https://restful-booker.herokuapp.com");
    }

    @Test
    public void createWithTextBlock() {
        bookingId =
            given()
                .contentType(ContentType.JSON)
                .accept(ContentType.JSON)
                .body("""
                    {
                      "firstname": "Rakesh",
                      "lastname": "Panda",
                      "totalprice": 250,
                      "depositpaid": true,
                      "bookingdates": { "checkin": "2026-11-01", "checkout": "2026-11-04" },
                      "additionalneeds": "Breakfast"
                    }
                    """)
            .when()
                .post("/booking")
            .then()
                .statusCode(200)
                .body("bookingid", greaterThan(0))
                .body("booking.firstname", equalTo("Rakesh"))
                .body("booking.bookingdates.checkout", equalTo("2026-11-04"))
                .extract().path("bookingid");
    }

    @Test(dependsOnMethods = "createWithTextBlock")
    public void partialUpdateWithMap() {
        given()
            .contentType(ContentType.JSON)
            .accept(ContentType.JSON)
            .auth().preemptive().basic("admin", "password123")
            .body(Map.of("additionalneeds", "Dinner", "totalprice", 300))
        .when()
            .patch("/booking/{id}", bookingId)
        .then()
            .statusCode(200)
            .body("additionalneeds", equalTo("Dinner"))
            .body("totalprice", equalTo(300))
            .body("firstname", equalTo("Rakesh"));   // untouched fields stay
    }

    @Test(dependsOnMethods = "partialUpdateWithMap")
    public void deleteThenConfirmGone() {
        given()
            .auth().preemptive().basic("admin", "password123")
        .when()
            .delete("/booking/{id}", bookingId)
        .then()
            .statusCode(201);   // this API answers 201 to a delete

        when().get("/booking/{id}", bookingId)
        .then().statusCode(404);
    }
}
''', {'save': 'src/test/java/tests/CrudTest.java'}),
                ('table', ['Method', 'Meaning', 'Restful Booker answer'], [
                    ['<code>POST</code>', 'Create something new', '200 with <code>bookingid</code>'],
                    ['<code>GET</code>', 'Read', '200, or 404 when missing'],
                    ['<code>PUT</code>', 'Replace every field', '200, needs auth'],
                    ['<code>PATCH</code>', 'Change only the fields you send', '200, needs auth'],
                    ['<code>DELETE</code>', 'Remove', '201, needs auth'],
                ]),
                ('warn', '<code>.auth().basic()</code> waits for the server to ask for a password with a 401 before it sends one. Restful Booker answers 403 instead, so the password is never sent. Use <code>.auth().preemptive().basic()</code>, which sends it on the first request.'),
                ('try', {'method': 'POST', 'path': '/booking', 'body': {'firstname': 'Rakesh', 'lastname': 'Panda', 'totalprice': 250, 'depositpaid': True, 'bookingdates': {'checkin': '2026-11-01', 'checkout': '2026-11-04'}, 'additionalneeds': 'Breakfast'}}),
            ],
        },
        {
            'id': 'assertions', 'title': 'Assertions with Hamcrest and GPath', 'emoji': '🔍', 'level': 'Intermediate',
            'blocks': [
                ('p', 'Rest Assured reads values with <b>GPath</b>, the path language from Groovy, and compares them with <b>Hamcrest</b> matchers. A few patterns cover almost every check.'),
                ('table', ['GPath', 'Reads', 'On this JSON'], [
                    ['<code>firstname</code>', 'A top level field', 'a booking'],
                    ['<code>bookingdates.checkin</code>', 'A nested field', 'a booking'],
                    ['<code>[0].bookingid</code> or <code>bookingid[0]</code>', 'An item in a top level array', 'the booking list'],
                    ['<code>bookingid</code>', 'One field from every item', 'the booking list'],
                    ['<code>size()</code>', 'How many items', 'the booking list'],
                    ['<code>findAll { it.bookingid &gt; 5 }.bookingid</code>', 'A filter', 'the booking list'],
                    ['<code>max { it.bookingid }.bookingid</code>', 'The largest', 'the booking list'],
                ]),
                ('code', 'java', 'Matchers you will use every day', '''
when().get("/booking/1")
.then()
    .statusCode(anyOf(is(200), is(304)))
    .header("Content-Type", containsString("application/json"))
    .time(lessThan(2000L))                                 // milliseconds
    .body("firstname", instanceOf(String.class))
    .body("totalprice", greaterThanOrEqualTo(0))
    .body("depositpaid", anyOf(is(true), is(false)))
    .body("$", hasKey("bookingdates"))                     // $ is the root object
    .body("bookingdates", hasKey("checkin"))
    .body("additionalneeds", anyOf(nullValue(), instanceOf(String.class)));

when().get("/booking")
.then()
    .body("size()", greaterThan(0))
    .body("bookingid", hasItem(1))
    .body("bookingid", everyItem(greaterThan(0)))
    .body("findAll { it.bookingid > 0 }.size()", greaterThan(0));
'''),
                ('p', 'When several <code>body</code> checks fail in one <code>then()</code>, Rest Assured reports all of them together, so one run shows every problem. For a Java side check after extraction, use TestNG <code>SoftAssert</code> for the same effect.'),
                ('warn', 'JSON numbers arrive as <code>Integer</code>, <code>Long</code>, <code>Float</code> or <code>Double</code> depending on their size. <code>equalTo(300)</code> passes for 300 but <code>equalTo(300L)</code> fails. For money, check with <code>closeTo</code> or extract as <code>BigDecimal</code> through a POJO.'),
            ],
        },
        {
            'id': 'extract', 'title': 'Extracting values and chaining calls', 'emoji': '🔗', 'level': 'Intermediate',
            'blocks': [
                ('p', 'Most real flows need a value from one response in the next request: a token, a new id, a link. Rest Assured gives three ways to pull values out.'),
                ('code', 'java', 'Three ways to extract', '''
// 1. One value straight from then()
String token =
    given().contentType(ContentType.JSON)
        .body(Map.of("username", "admin", "password", "password123"))
    .when().post("/auth")
    .then().statusCode(200).extract().path("token");

// 2. Keep the whole Response and read many values
Response res = when().get("/booking/1").then().statusCode(200).extract().response();
String first = res.path("firstname");
int price = res.jsonPath().getInt("totalprice");
String checkin = res.jsonPath().getString("bookingdates.checkin");
long millis = res.time();

// 3. Map the body to a Java object (see the POJO lesson)
Booking booking = when().get("/booking/1").as(Booking.class);
'''),
                ('code', 'java', 'Chaining: log in, create, then update with the token', '''
String token = given().contentType(ContentType.JSON)
        .body(Map.of("username", "admin", "password", "password123"))
    .post("/auth").then().extract().path("token");

int id = given().contentType(ContentType.JSON).body(newBooking())
    .post("/booking").then().statusCode(200).extract().path("bookingid");

given()
    .contentType(ContentType.JSON)
    .cookie("token", token)
    .body(Map.of("firstname", "Updated"))
.when()
    .patch("/booking/{id}", id)
.then()
    .statusCode(200)
    .body("firstname", equalTo("Updated"));
'''),
                ('qa', 'Chained tests should create their own data. Do not depend on booking 1 existing on a shared server, because someone else may delete it. Create, use, then clean up in an <code>@AfterMethod</code>.'),
            ],
        },
        {
            'id': 'auth', 'title': 'Authentication: token cookie, Basic, Bearer, OAuth 2 and API keys', 'emoji': '🔐', 'level': 'Intermediate',
            'blocks': [
                ('p', 'APIs protect data in a few standard ways. Restful Booker accepts a token cookie or Basic auth. Most other APIs you test will use a Bearer token, an API key or OAuth 2.'),
                ('code', 'java', 'Every common style', '''
// Token in a cookie (Restful Booker)
given().cookie("token", token);

// Basic auth, sent on the first request
given().auth().preemptive().basic("admin", "password123");

// Bearer token, used by most modern APIs
given().header("Authorization", "Bearer " + accessToken);
given().auth().oauth2(accessToken);            // same header, shorter

// API key in a header or the query string
given().header("x-api-key", System.getenv("API_KEY"));
given().queryParam("api_key", System.getenv("API_KEY"));

// OAuth 2 client credentials: get a token, then use it
String accessToken =
    given()
        .formParam("grant_type", "client_credentials")
        .formParam("client_id", System.getenv("CLIENT_ID"))
        .formParam("client_secret", System.getenv("CLIENT_SECRET"))
        .formParam("scope", "bookings.read")
    .when().post("https://auth.example.com/oauth2/token")
    .then().statusCode(200).extract().path("access_token");
'''),
                ('h', 'Security tests every QA should write'),
                ('ul', [
                    'No credentials at all gives 401 or 403, never 200.',
                    'A wrong or expired token is refused.',
                    'A user cannot read or change another user\'s data by changing the id in the path. This is called broken object level authorization and it is the top risk in the OWASP API Security Top 10.',
                    'Error messages do not leak stack traces, SQL or internal hostnames.',
                ]),
                ('code', 'java', 'A negative auth test', '''
@Test
public void updateWithoutTokenIsForbidden() {
    given()
        .contentType(ContentType.JSON)
        .body(Map.of("firstname", "Hacker"))
    .when()
        .patch("/booking/1")
    .then()
        .statusCode(403);

    when().get("/booking/1").then().body("firstname", not(equalTo("Hacker")));
}
'''),
                ('warn', 'Never put real passwords or tokens in code. Read them from environment variables or a secrets store, and keep them out of logs. The blacklist filter in the framework lesson hides them in Rest Assured logs.'),
                ('try', {'method': 'PUT', 'path': '/booking/1', 'body': {'firstname': 'Hacker', 'lastname': 'X', 'totalprice': 1, 'depositpaid': False, 'bookingdates': {'checkin': '2026-01-01', 'checkout': '2026-01-02'}}}),
            ],
        },
        {
            'id': 'specs', 'title': 'Reusable specifications and filters', 'emoji': '♻️', 'level': 'Intermediate',
            'blocks': [
                ('p', 'Copying the same base URI, headers and checks into every test makes a suite hard to change. A <b>RequestSpecification</b> holds shared request settings and a <b>ResponseSpecification</b> holds shared checks.'),
                ('code', 'java', 'src/test/java/tests/BaseTest.java', '''
package tests;

import static org.hamcrest.Matchers.*;

import io.restassured.builder.RequestSpecBuilder;
import io.restassured.builder.ResponseSpecBuilder;
import io.restassured.filter.log.LogDetail;
import io.restassured.http.ContentType;
import io.restassured.specification.RequestSpecification;
import io.restassured.specification.ResponseSpecification;
import org.testng.annotations.BeforeClass;

public abstract class BaseTest {

    protected RequestSpecification spec;
    protected ResponseSpecification okJson;

    @BeforeClass
    public void buildSpecs() {
        spec = new RequestSpecBuilder()
            .setBaseUri(System.getProperty("baseUrl", "https://restful-booker.herokuapp.com"))
            .setContentType(ContentType.JSON)
            .setAccept(ContentType.JSON)
            .addHeader("X-Test-Suite", "booker-api")
            .log(LogDetail.URI)
            .build();

        okJson = new ResponseSpecBuilder()
            .expectStatusCode(200)
            .expectContentType(ContentType.JSON)
            .expectResponseTime(lessThan(5000L))
            .build();
    }
}
''', {'save': 'src/test/java/tests/BaseTest.java'}),
                ('code', 'java', 'src/test/java/tests/SpecTest.java', '''
package tests;

import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

import org.testng.annotations.Test;

public class SpecTest extends BaseTest {

    @Test
    public void listUsesSharedSpecs() {
        given().spec(spec)
        .when().get("/booking")
        .then().spec(okJson).body("size()", greaterThan(0));
    }
}
''', {'save': 'src/test/java/tests/SpecTest.java'}),
                ('p', '<b>Filters</b> run around every request. Use them for logging, timing, adding headers, or attaching calls to a report. Write your own by implementing <code>Filter</code>.'),
                ('code', 'java', 'A custom filter that times every call', '''
import io.restassured.filter.Filter;
import io.restassured.filter.FilterContext;
import io.restassured.response.Response;
import io.restassured.specification.FilterableRequestSpecification;
import io.restassured.specification.FilterableResponseSpecification;

public class TimingFilter implements Filter {
    @Override
    public Response filter(FilterableRequestSpecification req,
                           FilterableResponseSpecification res,
                           FilterContext ctx) {
        long start = System.nanoTime();
        Response response = ctx.next(req, res);
        long ms = (System.nanoTime() - start) / 1_000_000;
        System.out.printf("%s %s -> %d in %d ms%n",
            req.getMethod(), req.getURI(), response.statusCode(), ms);
        return response;
    }
}

// use it for one call, or for every call
given().filter(new TimingFilter()).get("/ping");
RestAssured.filters(new TimingFilter());
'''),
                ('warn', 'Setting <code>RestAssured.baseURI</code> or <code>RestAssured.requestSpecification</code> changes a global value. That is fine for a single thread, but in parallel runs each test should pass its own spec with <code>given().spec(spec)</code>.'),
            ],
        },
        {
            'id': 'data-driven', 'title': 'Data driven tests with DataProvider', 'emoji': '📊', 'level': 'Intermediate',
            'blocks': [
                ('p', 'One test method can run with many rows of data. TestNG feeds each row from a <code>@DataProvider</code>. This is how you cover boundary values and invalid inputs without copying tests.'),
                ('code', 'java', 'src/test/java/tests/DataDrivenTest.java', '''
package tests;

import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

import io.restassured.http.ContentType;
import java.util.HashMap;
import java.util.Map;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

public class DataDrivenTest extends BaseTest {

    @DataProvider(name = "names")
    public Object[][] names() {
        return new Object[][] {
            {"Ann", "Lee"},
            {"José", "Núñez"},             // accents
            {"O'Brien", "Smith-Jones"},    // quote and dash
            {"A", "B"},                    // shortest
        };
    }

    @Test(dataProvider = "names")
    public void createKeepsNamesExactly(String first, String last) {
        Map<String, Object> body = validBooking();
        body.put("firstname", first);
        body.put("lastname", last);

        given().spec(spec).body(body)
        .when().post("/booking")
        .then().spec(okJson)
            .body("booking.firstname", equalTo(first))
            .body("booking.lastname", equalTo(last));
    }

    @DataProvider(name = "missingField")
    public Object[][] missingField() {
        return new Object[][] {{"firstname"}, {"lastname"}, {"totalprice"}, {"depositpaid"}, {"bookingdates"}};
    }

    @Test(dataProvider = "missingField")
    public void requiredFieldMissingIsRejected(String field) {
        Map<String, Object> body = validBooking();
        body.remove(field);

        given().spec(spec).body(body)
        .when().post("/booking")
        .then().statusCode(not(200));   // Restful Booker answers 500. A well built API answers 400.
    }

    static Map<String, Object> validBooking() {
        Map<String, Object> b = new HashMap<>();
        b.put("firstname", "Test");
        b.put("lastname", "User");
        b.put("totalprice", 100);
        b.put("depositpaid", true);
        b.put("bookingdates", Map.of("checkin", "2026-12-01", "checkout", "2026-12-03"));
        b.put("additionalneeds", "None");
        return b;
    }
}
''', {'save': 'src/test/java/tests/DataDrivenTest.java'}),
                ('qa', 'Restful Booker answers <b>500</b> when a required field is missing. A good API should answer <b>400 Bad Request</b> with a message. Finding gaps like this is exactly the kind of bug API testers report.'),
                ('tip', 'Data can also come from a CSV, JSON or Excel file. Read the file inside the <code>@DataProvider</code> method and return the rows. Add <code>parallel = true</code> to the annotation to run rows at the same time.'),
            ],
        },
        {
            'id': 'schema', 'title': 'JSON Schema validation', 'emoji': '📐', 'level': 'Advanced',
            'blocks': [
                ('p', 'A JSON Schema describes the shape of a response: which fields exist, their types, which are required, and allowed patterns. One schema check replaces dozens of single field checks and catches a renamed or retyped field at once.'),
                ('code', 'json', 'src/test/resources/schemas/booking-schema.json', '''
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Booking",
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
  },
  "additionalProperties": false
}
''', {'save': 'src/test/resources/schemas/booking-schema.json'}),
                ('code', 'java', 'src/test/java/tests/SchemaTest.java', '''
package tests;

import static io.restassured.RestAssured.*;
import static io.restassured.module.jsv.JsonSchemaValidator.matchesJsonSchemaInClasspath;

import org.testng.annotations.Test;

public class SchemaTest extends BaseTest {

    @Test
    public void bookingMatchesSchema() {
        given().spec(spec)
        .when().get("/booking/1")
        .then().spec(okJson)
            .body(matchesJsonSchemaInClasspath("schemas/booking-schema.json"));
    }
}
''', {'save': 'src/test/java/tests/SchemaTest.java'}),
                ('tip', '<code>"additionalProperties": false</code> makes the test fail when the API adds an unexpected field. Turn it on for strict contracts, and leave it off when the API is allowed to grow.'),
                ('why', 'If the developers rename <code>totalprice</code> to <code>totalPrice</code>, a value check on another field still passes. The schema check fails straight away and names the missing field.'),
            ],
        },
        {
            'id': 'pojo', 'title': 'POJOs, records and serialization', 'emoji': '🧬', 'level': 'Advanced',
            'blocks': [
                ('p', 'Turning a Java object into JSON is <b>serialization</b>. Turning JSON back into an object is <b>deserialization</b>. Rest Assured does both with Jackson whenever it is on the classpath. Java records make the model classes short.'),
                ('code', 'java', 'src/test/java/tests/model/Booking.java', '''
package tests.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;

@JsonIgnoreProperties(ignoreUnknown = true)       // new API fields will not break tests
@JsonInclude(JsonInclude.Include.NON_NULL)        // do not send nulls
public record Booking(
        String firstname,
        String lastname,
        Integer totalprice,
        Boolean depositpaid,
        BookingDates bookingdates,
        String additionalneeds) {

    public record BookingDates(String checkin, String checkout) {}

    public static Booking sample() {
        return new Booking("Rakesh", "Panda", 250, true,
            new BookingDates("2026-11-01", "2026-11-04"), "Breakfast");
    }

    public Booking withFirstname(String name) {
        return new Booking(name, lastname, totalprice, depositpaid, bookingdates, additionalneeds);
    }
}
''', {'save': 'src/test/java/tests/model/Booking.java'}),
                ('code', 'java', 'src/test/java/tests/model/CreatedBooking.java', '''
package tests.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public record CreatedBooking(int bookingid, Booking booking) {}
''', {'save': 'src/test/java/tests/model/CreatedBooking.java'}),
                ('code', 'java', 'src/test/java/tests/PojoTest.java', '''
package tests;

import static io.restassured.RestAssured.*;
import static org.testng.Assert.*;

import org.testng.annotations.Test;
import tests.model.Booking;
import tests.model.CreatedBooking;

public class PojoTest extends BaseTest {

    @Test
    public void roundTripAsObjects() {
        Booking sent = Booking.sample().withFirstname("Pojo");

        CreatedBooking created =
            given().spec(spec).body(sent)
            .when().post("/booking")
            .then().spec(okJson)
            .extract().as(CreatedBooking.class);

        assertTrue(created.bookingid() > 0);
        assertEquals(created.booking(), sent);   // records compare every field

        Booking read = given().spec(spec).get("/booking/{id}", created.bookingid()).as(Booking.class);
        assertEquals(read, sent);
    }
}
''', {'save': 'src/test/java/tests/PojoTest.java'}),
                ('tip', 'Records give you <code>equals</code> for free, so <code>assertEquals(read, sent)</code> compares every field in one line. For lists use <code>extract().as(new TypeRef&lt;List&lt;Booking&gt;&gt;() {})</code>.'),
            ],
        },
        {
            'id': 'framework', 'title': 'Designing a real framework', 'emoji': '🏗️', 'level': 'Advanced',
            'blocks': [
                ('p', 'Tests that call <code>given()</code> directly are fine for twenty tests. For hundreds, split the code into layers so that a change to an endpoint is fixed in one place. This is the API version of the Page Object pattern.'),
                ('code', 'plain', 'A layered layout', '''
src/test/java/
├── config/      Config.java          base URL, users, timeouts from env or a properties file
├── client/      BookingApi.java      one method per endpoint, returns Response
│                AuthApi.java
├── model/       Booking.java         records for request and response bodies
├── data/        BookingFactory.java  builds valid and invalid test data
├── support/     Specs.java           shared request and response specs, filters
└── tests/       BookingCrudTest.java only test logic and assertions
'''),
                ('code', 'java', 'src/test/java/tests/client/BookingApi.java', '''
package tests.client;

import static io.restassured.RestAssured.given;

import io.restassured.response.Response;
import io.restassured.specification.RequestSpecification;
import java.util.Map;
import tests.model.Booking;

public class BookingApi {

    private final RequestSpecification spec;
    private String token;

    public BookingApi(RequestSpecification spec) {
        this.spec = spec;
    }

    public BookingApi login(String user, String password) {
        token = given().spec(spec)
            .body(Map.of("username", user, "password", password))
            .post("/auth").then().statusCode(200).extract().path("token");
        return this;
    }

    public Response create(Booking b)              { return given().spec(spec).body(b).post("/booking"); }
    public Response get(int id)                    { return given().spec(spec).get("/booking/{id}", id); }
    public Response list(Map<String, ?> filters)   { return given().spec(spec).queryParams(filters).get("/booking"); }
    public Response update(int id, Booking b)      { return authed().body(b).put("/booking/{id}", id); }
    public Response patch(int id, Map<String, ?> f){ return authed().body(f).patch("/booking/{id}", id); }
    public Response delete(int id)                 { return authed().delete("/booking/{id}", id); }

    private RequestSpecification authed() {
        RequestSpecification r = given().spec(spec);
        return token == null ? r : r.cookie("token", token);
    }
}
''', {'save': 'src/test/java/tests/client/BookingApi.java'}),
                ('code', 'java', 'src/test/java/tests/FrameworkTest.java', '''
package tests;

import static org.hamcrest.Matchers.*;

import java.util.Map;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;
import tests.client.BookingApi;
import tests.model.Booking;

public class FrameworkTest extends BaseTest {

    private BookingApi api;

    @BeforeClass(dependsOnMethods = "buildSpecs")
    public void login() {
        api = new BookingApi(spec).login("admin", "password123");
    }

    @Test
    public void updateThroughTheClient() {
        int id = api.create(Booking.sample()).then().statusCode(200).extract().path("bookingid");

        api.patch(id, Map.of("lastname", "Updated"))
            .then().statusCode(200).body("lastname", equalTo("Updated"));

        api.delete(id).then().statusCode(201);
        api.get(id).then().statusCode(404);
    }
}
''', {'save': 'src/test/java/tests/FrameworkTest.java'}),
                ('ul', [
                    'Tests read like a story because the HTTP details live in the client.',
                    'When <code>/booking</code> moves to <code>/v2/bookings</code>, you change one line.',
                    'The same client is reused by UI tests to create data quickly.',
                    'Config comes from <code>System.getProperty</code> or <code>System.getenv</code>, so the same suite runs on dev, QA and staging.',
                ]),
            ],
        },
        {
            'id': 'mocking', 'title': 'Mocking other services with WireMock', 'emoji': '🎭', 'level': 'Advanced',
            'blocks': [
                ('p', 'Sometimes the API you test calls another service that is slow, costly or not built yet, such as a payment gateway. <b>WireMock</b> starts a fake HTTP server that returns answers you define. Point the service, or your own client code, at it.'),
                ('code', 'xml', 'Extra dependency', '''
<dependency>
  <groupId>org.wiremock</groupId>
  <artifactId>wiremock-standalone</artifactId>
  <version>3.13.2</version>
  <scope>test</scope>
</dependency>
'''),
                ('code', 'java', 'Stub a payment service and test against it', '''
import static com.github.tomakehurst.wiremock.client.WireMock.*;
import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.equalTo;

import com.github.tomakehurst.wiremock.WireMockServer;
import com.github.tomakehurst.wiremock.core.WireMockConfiguration;
import org.testng.annotations.*;

public class PaymentStubTest {

    private WireMockServer server;

    @BeforeClass
    public void start() {
        server = new WireMockServer(WireMockConfiguration.options().dynamicPort());
        server.start();

        server.stubFor(post(urlEqualTo("/payments"))
            .withRequestBody(matchingJsonPath("$.amount", equalTo("250")))
            .willReturn(okJson("{\\"status\\":\\"APPROVED\\",\\"id\\":\\"pay_1\\"}")));

        server.stubFor(post(urlEqualTo("/payments"))
            .withRequestBody(matchingJsonPath("$.amount", equalTo("0")))
            .willReturn(aResponse().withStatus(422).withBody("Amount must be positive")));

        server.stubFor(get("/slow").willReturn(ok().withFixedDelay(3000)));
    }

    @Test
    public void approvedPayment() {
        given().baseUri(server.baseUrl()).contentType("application/json")
            .body("{\\"amount\\":250}")
        .when().post("/payments")
        .then().statusCode(200).body("status", equalTo("APPROVED"));

        server.verify(1, postRequestedFor(urlEqualTo("/payments")));
    }

    @AfterClass
    public void stop() { server.stop(); }
}
'''),
                ('tip', 'Stubs make error paths easy to test: timeouts with <code>withFixedDelay</code>, 500 errors, broken JSON, or a dropped connection with <code>withFault(Fault.CONNECTION_RESET_BY_PEER)</code>.'),
            ],
        },
        {
            'id': 'parallel-ci', 'title': 'Parallel runs, reports and CI', 'emoji': '🚀', 'level': 'Expert',
            'blocks': [
                ('p', 'A mature suite runs on every pull request, in parallel, and publishes a report. TestNG handles parallel runs through <code>testng.xml</code>.'),
                ('code', 'xml', 'src/test/resources/testng.xml', '''
<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="Booker API" parallel="classes" thread-count="4">
  <test name="smoke">
    <groups><run><include name="smoke"/></run></groups>
    <packages><package name="tests"/></packages>
  </test>
</suite>
'''),
                ('ul', [
                    'Keep each test independent. It creates its own booking and never relies on order, unless you use <code>dependsOnMethods</code> on purpose.',
                    'Do not share mutable static fields between threads. Pass specs and ids as local variables.',
                    'Tag tests with <code>@Test(groups = "smoke")</code> so a quick subset can run on every commit and the full set nightly.',
                ]),
                ('code', 'yaml', '.github/workflows/api-tests.yml', '''
name: API tests
on: [push, pull_request]
jobs:
  api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 21
          cache: maven
      - name: Run tests
        run: mvn -B test -DbaseUrl=${{ vars.BASE_URL }}
        env:
          API_PASSWORD: ${{ secrets.API_PASSWORD }}
      - name: Keep the reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: surefire-reports
          path: target/surefire-reports
'''),
                ('p', 'For a richer report, add <b>Allure</b> (<code>io.qameta.allure:allure-rest-assured</code>) and register <code>new AllureRestAssured()</code> as a filter. Every request and response is then attached to the test in the report, which makes failures easy to read.'),
            ],
        },
        {
            'id': 'expert', 'title': 'Expert topics: polling, uploads, GraphQL, contracts and more', 'emoji': '🧠', 'level': 'Expert',
            'blocks': [
                ('h', 'Waiting for eventually consistent APIs'),
                ('p', 'Some APIs process work in the background, so the result appears a few seconds later. Never use <code>Thread.sleep</code>. Poll with a time limit using Awaitility.'),
                ('code', 'java', 'Poll until a job is done', '''
import static org.awaitility.Awaitility.await;
import java.time.Duration;

await().atMost(Duration.ofSeconds(30))
       .pollInterval(Duration.ofSeconds(1))
       .until(() -> get("/jobs/{id}", jobId).path("status").equals("DONE"));
'''),
                ('h', 'File uploads and downloads'),
                ('code', 'java', 'Multipart upload and binary download', '''
given().multiPart("file", new File("src/test/resources/invoice.pdf"), "application/pdf")
       .multiPart("note", "March invoice")
.when().post("/documents")
.then().statusCode(201);

byte[] pdf = get("/documents/7/download").then().statusCode(200).extract().asByteArray();
assertTrue(pdf.length > 0);
'''),
                ('h', 'GraphQL'),
                ('p', 'GraphQL is still HTTP: one POST to <code>/graphql</code> with a <code>query</code> and <code>variables</code>. Always check for an <code>errors</code> array, because GraphQL often answers 200 even when something failed.'),
                ('code', 'java', 'A GraphQL query', '''
given().contentType(ContentType.JSON)
    .body(Map.of(
        "query", "query($id: ID!) { booking(id: $id) { firstname totalprice } }",
        "variables", Map.of("id", 1)))
.when().post("/graphql")
.then().statusCode(200)
    .body("errors", nullValue())
    .body("data.booking.firstname", notNullValue());
'''),
                ('h', 'Contract testing'),
                ('p', 'In a microservice system, a <b>consumer driven contract</b> test with Pact records what a client expects from a provider. The provider then replays those expectations in its own build. Breaking changes are caught before deployment, without a shared test environment. Schema checks are the lighter version of the same idea.'),
                ('h', 'Other expert checks'),
                ('ul', [
                    '<b>Idempotency</b>: sending the same PUT or DELETE twice must leave the same state. Payment APIs often accept an <code>Idempotency-Key</code> header for POST.',
                    '<b>Pagination</b>: walk every page with <code>page</code> and <code>size</code> and check no item is missing or repeated.',
                    '<b>Rate limits</b>: many fast calls should give 429 with a <code>Retry-After</code> header.',
                    '<b>Caching</b>: <code>ETag</code> and <code>If-None-Match</code> should give 304 Not Modified.',
                    '<b>Fuzzing</b>: very long strings, emoji, SQL characters and wrong types should give 400, never 500.',
                    '<b>OpenAPI</b>: generate the client and the schema checks from the API spec so tests follow the contract.',
                ]),
            ],
        },
        {
            'id': 'scenario', 'title': 'Real world scenario: a hotel front desk day', 'emoji': '🏨', 'level': 'Scenario',
            'blocks': [
                ('p', 'A guest calls the front desk. The receptionist books a room, the guest asks for breakfast to be added, then the trip is cancelled. Your end to end API test follows the same journey and checks each step, including the one a hacker would try.'),
                ('flow', [
                    ('Health check', '<code>GET /ping</code> must answer 201 before anything else runs.'),
                    ('Receptionist logs in', '<code>POST /auth</code> returns a token. Save it.'),
                    ('Create the booking', '<code>POST /booking</code> returns a new <code>bookingid</code>. Save it.'),
                    ('Read it back', '<code>GET /booking/{id}</code> must match what was sent, field by field.'),
                    ('Find it by name', '<code>GET /booking?firstname=...</code> must include the new id.'),
                    ('Guest adds breakfast', '<code>PATCH</code> with the token changes only <code>additionalneeds</code>.'),
                    ('Someone tries without logging in', '<code>DELETE</code> with no token must give 403, and the booking must still exist.'),
                    ('Trip cancelled', '<code>DELETE</code> with the token gives 201.'),
                    ('Confirm it is gone', '<code>GET /booking/{id}</code> gives 404.'),
                ]),
                ('code', 'java', 'src/test/java/tests/FrontDeskJourneyTest.java', '''
package tests;

import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

import java.util.Map;
import org.testng.annotations.Test;
import tests.model.Booking;

public class FrontDeskJourneyTest extends BaseTest {

    @Test
    public void bookChangeAndCancel() {
        given().spec(spec).get("/ping").then().statusCode(201);

        String token = given().spec(spec)
            .body(Map.of("username", "admin", "password", "password123"))
            .post("/auth").then().statusCode(200).body("token", not(emptyOrNullString()))
            .extract().path("token");

        String guest = "Guest" + System.currentTimeMillis();
        Booking booking = Booking.sample().withFirstname(guest);

        int id = given().spec(spec).body(booking).post("/booking")
            .then().spec(okJson).extract().path("bookingid");

        given().spec(spec).get("/booking/{id}", id)
            .then().spec(okJson)
            .body("firstname", equalTo(guest))
            .body("bookingdates.checkin", equalTo("2026-11-01"));

        given().spec(spec).queryParam("firstname", guest).get("/booking")
            .then().spec(okJson).body("bookingid", hasItem(id));

        given().spec(spec).cookie("token", token)
            .body(Map.of("additionalneeds", "Breakfast and dinner"))
            .patch("/booking/{id}", id)
            .then().spec(okJson)
            .body("additionalneeds", equalTo("Breakfast and dinner"))
            .body("lastname", equalTo("Panda"));

        given().spec(spec).delete("/booking/{id}", id).then().statusCode(403);
        given().spec(spec).get("/booking/{id}", id).then().statusCode(200);

        given().spec(spec).cookie("token", token).delete("/booking/{id}", id).then().statusCode(201);
        given().spec(spec).get("/booking/{id}", id).then().statusCode(404);
    }
}
''', {'save': 'src/test/java/tests/FrontDeskJourneyTest.java'}),
                ('qa', 'The unique guest name makes the search step reliable on a shared server where other people create bookings at the same time.'),
            ],
        },
    ],
    'quiz': [
        {'lv': 'e', 'q': 'Which part of a Rest Assured test sends the request?', 'o': ['<code>given()</code>', '<code>when()</code> with a method like <code>get</code>', '<code>then()</code>', '<code>extract()</code>'], 'a': 1, 'hint': 'Arrange, Act, Assert.', 'why': '<code>given()</code> arranges, <code>when().get()</code> acts by sending, <code>then()</code> asserts.'},
        {'lv': 'e', 'q': 'What status does Restful Booker return for a successful DELETE?', 'o': ['200', '204', '201', '202'], 'a': 2, 'hint': 'It is one of its known quirks.', 'why': 'Restful Booker answers 201 Created to DELETE. Always check what the real API does, not what you expect.'},
        {'lv': 'm', 'q': 'Your PATCH with <code>.auth().basic("admin", "password123")</code> gets 403. What is the fix?', 'o': ['Use <code>.auth().preemptive().basic(...)</code>', 'Use PUT instead', 'Add <code>accept(ContentType.JSON)</code>', 'Use <code>.auth().digest(...)</code>'], 'a': 0, 'hint': 'Basic auth waits for a 401 challenge.', 'why': 'Plain <code>basic()</code> only sends the password after a 401 challenge. This API never sends one, so the password must be sent up front with <code>preemptive()</code>.'},
        {'lv': 'm', 'q': 'On the list response <code>[{"bookingid":1},{"bookingid":2}]</code>, what does the GPath <code>bookingid</code> return?', 'o': ['1', 'An error', 'The list [1, 2]', 'null'], 'a': 2, 'hint': 'GPath collects across arrays.', 'why': 'On an array, a field name collects that field from every item, so you can check it with <code>hasItem</code> or <code>everyItem</code>.'},
        {'lv': 'h', 'q': 'Why should parallel tests avoid setting <code>RestAssured.baseURI</code> inside each test?', 'o': ['It is slower', 'It is a static global, so threads overwrite each other', 'It is deprecated', 'It only works with JUnit'], 'a': 1, 'hint': 'Think about shared state.', 'why': 'Static settings are shared by every thread. Pass a <code>RequestSpecification</code> per test with <code>given().spec(spec)</code> instead.'},
        {'lv': 'h', 'q': 'A developer renames <code>totalprice</code> to <code>totalPrice</code>. Which check catches it with the least code?', 'o': ['<code>statusCode(200)</code>', 'A JSON Schema check with <code>totalprice</code> required', '<code>time(lessThan(2000L))</code>', '<code>contentType(JSON)</code>'], 'a': 1, 'hint': 'Shape, not value.', 'why': 'The schema lists required fields, so the missing <code>totalprice</code> fails the check immediately.'},
        {'lv': 'x', 'q': 'A booking id from <code>extract().path("bookingid")</code> is used in later tests. They pass alone but fail in parallel. Most likely cause?', 'o': ['The JSON is wrong', 'The id is stored in a shared field and overwritten by another thread', 'TestNG does not support parallel runs', 'The server is slow'], 'a': 1, 'hint': 'Who else writes that field?', 'why': 'A shared instance or static field is written by several threads. Keep ids local to the test, or use a <code>ThreadLocal</code>.'},
        {'lv': 'x', 'q': 'A GraphQL call returns HTTP 200. What must you still check?', 'o': ['Nothing, 200 means success', 'That the body has no <code>errors</code> array', 'That the method was GET', 'That the Content-Length is 0'], 'a': 1, 'hint': 'GraphQL reports errors in the body.', 'why': 'GraphQL commonly returns 200 with an <code>errors</code> list. A test that only checks the status will miss real failures.'},
    ],
}
