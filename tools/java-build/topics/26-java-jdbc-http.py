# Chapter 26: talking to the outside world: JDBC with a real H2 database (connections, PreparedStatement, SQL injection,
# transactions, batches, generated keys) and java.net.http.HttpClient against a local HTTP server (GET, POST, headers,
# timeouts, async calls, HTTP/3 in Java 26) with an API test as the scenario.
from kit import part, j, sh, show, say, quiz, calc, panel

MODULE = ('🚀', 'Modern Java', 'modern', 'Java 8 to Java 27: lambdas, streams, records, pattern matching, virtual threads, the JVM inside out, databases and HTTP, and every recent release explained with real work uses.')


def db(code, label, **kw):
    """A JDBC example that runs with the H2 database driver on the classpath."""
    spec = j(code, label, trace=False, **kw)
    spec['h2'] = True
    return spec


SERVER = '''
    // a tiny shop API on a free port, so the example needs no internet
    static HttpServer startServer() throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/products/1", ex -> reply(ex, 200, "{\\"id\\":1,\\"name\\":\\"pen\\",\\"price\\":49}"));
        server.createContext("/orders", ex -> {
            String body = new String(ex.getRequestBody().readAllBytes());
            if (!ex.getRequestMethod().equals("POST")) { reply(ex, 405, "{\\"error\\":\\"use POST\\"}"); return; }
            if (!"secret-token".equals(ex.getRequestHeaders().getFirst("Authorization"))) { reply(ex, 401, "{\\"error\\":\\"login first\\"}"); return; }
            ex.getResponseHeaders().add("Location", "/orders/77");
            reply(ex, 201, "{\\"id\\":77,\\"received\\":" + body + "}");
        });
        server.createContext("/slow", ex -> {
            try { Thread.sleep(2000); } catch (InterruptedException e) { }
            reply(ex, 200, "finally");
        });
        server.setExecutor(Executors.newVirtualThreadPerTaskExecutor());
        server.start();
        return server;
    }

    static void reply(HttpExchange ex, int status, String body) throws IOException {
        byte[] bytes = body.getBytes();
        ex.getResponseHeaders().add("Content-Type", "application/json");
        ex.sendResponseHeaders(status, bytes.length);
        try (OutputStream out = ex.getResponseBody()) { out.write(bytes); }
    }
'''

HTTP_IMPORTS = '''import com.sun.net.httpserver.*;
import java.io.*;
import java.net.*;
import java.net.http.*;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
'''

CODES = {
    'connect': db('''
import java.sql.*;

class Main {
    public static void main(String[] args) throws SQLException {
        String url = "jdbc:h2:mem:shop";                     // an in-memory database, gone when the program ends
        try (Connection con = DriverManager.getConnection(url, "sa", "");
             Statement st = con.createStatement()) {

            st.execute("CREATE TABLE products (id INT PRIMARY KEY, name VARCHAR(40), price INT)");
            int rows = st.executeUpdate("INSERT INTO products VALUES (1, 'pen', 49), (2, 'notebook', 120), (3, 'bag', 899)");
            System.out.println(rows + " rows inserted");

            try (ResultSet rs = st.executeQuery("SELECT id, name, price FROM products WHERE price < 500 ORDER BY price")) {
                while (rs.next()) {                          // move to the next row, false when there are no more
                    System.out.println(rs.getInt("id") + " " + rs.getString("name") + " costs " + rs.getInt("price"));
                }
            }
            System.out.println("database: " + con.getMetaData().getDatabaseProductName());
        }
    }
}
''', 'Connect, create, insert and query'),
    'inject': db('''
import java.sql.*;

class Main {
    public static void main(String[] args) throws SQLException {
        try (Connection con = DriverManager.getConnection("jdbc:h2:mem:login", "sa", "")) {
            con.createStatement().execute("CREATE TABLE users (name VARCHAR(20), role VARCHAR(20))");
            con.createStatement().execute("INSERT INTO users VALUES ('asha', 'admin'), ('ravi', 'customer'), ('meera', 'customer')");

            String typed = "x' OR '1'='1";                   // what an attacker types into the login form

            // ❌ gluing the input into the SQL text
            String sql = "SELECT name FROM users WHERE name = '" + typed + "'";
            System.out.println("glued SQL: " + sql);
            try (ResultSet rs = con.createStatement().executeQuery(sql)) {
                while (rs.next()) System.out.println("  glued query returned " + rs.getString(1));
            }

            // ✅ a PreparedStatement sends the input as a value, never as SQL
            try (PreparedStatement ps = con.prepareStatement("SELECT name FROM users WHERE name = ?")) {
                ps.setString(1, typed);
                try (ResultSet rs = ps.executeQuery()) {
                    System.out.println("prepared query found a row? " + rs.next());
                }
            }
        }
    }
}
''', 'SQL injection, for real, and the fix'),
    'tx': db('''
import java.sql.*;

class Main {
    static void transfer(Connection con, String from, String to, int amount) throws SQLException {
        con.setAutoCommit(false);                            // start a transaction
        try (PreparedStatement take = con.prepareStatement("UPDATE accounts SET balance = balance - ? WHERE name = ?");
             PreparedStatement give = con.prepareStatement("UPDATE accounts SET balance = balance + ? WHERE name = ?")) {
            give.setInt(1, amount); give.setString(2, to); give.executeUpdate();
            take.setInt(1, amount); take.setString(2, from); take.executeUpdate();   // fails if balance goes below 0
            con.commit();
            System.out.println("transfer of " + amount + " committed");
        } catch (SQLException e) {
            con.rollback();                                  // undo every change in this transaction
            System.out.println("transfer of " + amount + " rolled back: balance would go below 0");
        } finally {
            con.setAutoCommit(true);
        }
    }

    static void show(Connection con) throws SQLException {
        try (ResultSet rs = con.createStatement().executeQuery("SELECT name, balance FROM accounts ORDER BY name")) {
            StringBuilder sb = new StringBuilder("  balances:");
            while (rs.next()) sb.append(" ").append(rs.getString(1)).append("=").append(rs.getInt(2));
            System.out.println(sb);
        }
    }

    public static void main(String[] args) throws SQLException {
        try (Connection con = DriverManager.getConnection("jdbc:h2:mem:bank", "sa", "")) {
            con.createStatement().execute("CREATE TABLE accounts (name VARCHAR(20), balance INT CHECK (balance >= 0))");
            con.createStatement().execute("INSERT INTO accounts VALUES ('asha', 500), ('ravi', 100)");
            show(con);
            transfer(con, "asha", "ravi", 200);
            show(con);
            transfer(con, "ravi", "asha", 1000);
            show(con);
        }
    }
}
''', 'A money transfer: commit or roll back together'),
    'batch': db('''
import java.sql.*;

class Main {
    record Order(long id, String customer, int amount) { }

    public static void main(String[] args) throws SQLException {
        try (Connection con = DriverManager.getConnection("jdbc:h2:mem:orders", "sa", "")) {
            con.createStatement().execute("CREATE TABLE orders (id BIGINT AUTO_INCREMENT PRIMARY KEY, customer VARCHAR(20), amount INT)");

            // one row, and ask for the id the database generated
            try (PreparedStatement ps = con.prepareStatement("INSERT INTO orders (customer, amount) VALUES (?, ?)", Statement.RETURN_GENERATED_KEYS)) {
                ps.setString(1, "asha"); ps.setInt(2, 450);
                ps.executeUpdate();
                try (ResultSet keys = ps.getGeneratedKeys()) {
                    keys.next();
                    System.out.println("new order id: " + keys.getLong(1));
                }
            }

            // a thousand rows in one round trip with a batch
            try (PreparedStatement ps = con.prepareStatement("INSERT INTO orders (customer, amount) VALUES (?, ?)")) {
                for (int i = 1; i <= 1000; i++) {
                    ps.setString(1, i % 2 == 0 ? "ravi" : "meera");
                    ps.setInt(2, i);
                    ps.addBatch();
                }
                System.out.println("batch inserted " + ps.executeBatch().length + " rows");
            }

            // map rows to records
            try (PreparedStatement ps = con.prepareStatement("SELECT id, customer, amount FROM orders WHERE amount > ? ORDER BY amount DESC LIMIT 3")) {
                ps.setInt(1, 990);
                try (ResultSet rs = ps.executeQuery()) {
                    while (rs.next()) System.out.println(new Order(rs.getLong("id"), rs.getString("customer"), rs.getInt("amount")));
                }
            }
            try (ResultSet rs = con.createStatement().executeQuery("SELECT customer, COUNT(*), SUM(amount) FROM orders GROUP BY customer ORDER BY customer")) {
                while (rs.next()) System.out.println(rs.getString(1) + ": " + rs.getInt(2) + " orders, total " + rs.getLong(3));
            }
        }
    }
}
''', 'Generated keys, batches and mapping rows to records'),
    'get': j(HTTP_IMPORTS + '''
class Main {
''' + SERVER + '''
    public static void main(String[] args) throws Exception {
        HttpServer server = startServer();
        String base = "http://127.0.0.1:" + server.getAddress().getPort();

        HttpClient client = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(2))
                .build();

        HttpRequest req = HttpRequest.newBuilder(URI.create(base + "/products/1"))
                .header("Accept", "application/json")
                .GET()
                .build();
        HttpResponse<String> res = client.send(req, HttpResponse.BodyHandlers.ofString());

        System.out.println("status: " + res.statusCode());
        System.out.println("content type: " + res.headers().firstValue("Content-Type").orElse("none"));
        System.out.println("body: " + res.body());
        System.out.println("protocol: " + res.version());
        server.stop(0);
    }
}
''', 'A GET request with HttpClient', trace=False),
    'post': j(HTTP_IMPORTS + '''
class Main {
''' + SERVER + '''
    public static void main(String[] args) throws Exception {
        HttpServer server = startServer();
        String base = "http://127.0.0.1:" + server.getAddress().getPort();
        HttpClient client = HttpClient.newHttpClient();
        String json = "{\\"product\\":1,\\"qty\\":2}";

        HttpRequest noToken = HttpRequest.newBuilder(URI.create(base + "/orders"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();
        HttpResponse<String> r1 = client.send(noToken, HttpResponse.BodyHandlers.ofString());
        System.out.println("without a token: " + r1.statusCode() + " " + r1.body());

        HttpRequest withToken = HttpRequest.newBuilder(URI.create(base + "/orders"))
                .header("Content-Type", "application/json")
                .header("Authorization", "secret-token")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();
        HttpResponse<String> r2 = client.send(withToken, HttpResponse.BodyHandlers.ofString());
        System.out.println("with a token:    " + r2.statusCode() + " " + r2.body());
        System.out.println("new order at:    " + r2.headers().firstValue("Location").orElseThrow());

        HttpResponse<String> r3 = client.send(HttpRequest.newBuilder(URI.create(base + "/orders")).GET().build(), HttpResponse.BodyHandlers.ofString());
        System.out.println("GET on /orders:  " + r3.statusCode() + " " + r3.body());
        server.stop(0);
    }
}
''', 'POST with a JSON body, headers and status codes', trace=False),
    'async': j(HTTP_IMPORTS + '''
class Main {
''' + SERVER + '''
    public static void main(String[] args) throws Exception {
        HttpServer server = startServer();
        String base = "http://127.0.0.1:" + server.getAddress().getPort();
        HttpClient client = HttpClient.newHttpClient();

        // a timeout on one request: the server takes 2 s, we wait at most 500 ms
        HttpRequest slow = HttpRequest.newBuilder(URI.create(base + "/slow")).timeout(Duration.ofMillis(500)).build();
        try {
            client.send(slow, HttpResponse.BodyHandlers.ofString());
        } catch (HttpTimeoutException e) {
            System.out.println("timed out: " + e.getMessage());
        }

        // three calls at once with sendAsync, which returns CompletableFutures
        long t0 = System.currentTimeMillis();
        List<CompletableFuture<Integer>> calls = new ArrayList<>();
        for (int i = 0; i < 3; i++) {
            calls.add(client.sendAsync(HttpRequest.newBuilder(URI.create(base + "/slow")).build(), HttpResponse.BodyHandlers.ofString())
                    .thenApply(HttpResponse::statusCode));
        }
        List<Integer> codes = calls.stream().map(CompletableFuture::join).toList();
        long secs = Math.round((System.currentTimeMillis() - t0) / 1000.0);
        System.out.println("3 slow calls together: " + codes + " in about " + secs + " s, not 6 s");
        server.stop(0);
    }
}
''', 'Timeouts and calls in parallel with sendAsync', trace=False),
    'http3': show('''
// Java 26 (JEP 517): ask for HTTP/3, which runs over QUIC (UDP) instead of TCP
HttpClient client = HttpClient.newBuilder()
        .version(HttpClient.Version.HTTP_3)     // the default stays HTTP/2
        .build();

HttpRequest req = HttpRequest.newBuilder(URI.create("https://openjdk.org/"))
        // try HTTP/3 only when the server advertises it, otherwise use HTTP/2 or 1.1
        .setOption(HttpOption.H3_DISCOVERY, HttpOption.Http3DiscoveryMode.ALT_SVC)
        .build();

HttpResponse<String> res = client.send(req, HttpResponse.BodyHandlers.ofString());
System.out.println(res.version());              // HTTP_3 once the server has offered it
''', 'Opting in to HTTP/3 (Java 26)', note='Needs a real HTTP/3 server on the internet, so it is not run here'),
    'apitest': j(HTTP_IMPORTS + '''
class Main {
''' + SERVER + '''
    static int passed = 0, failed = 0;

    static void check(String name, boolean ok, String detail) {
        if (ok) passed++; else failed++;
        System.out.println((ok ? "PASS " : "FAIL ") + name + (ok ? "" : "  -> " + detail));
    }

    public static void main(String[] args) throws Exception {
        HttpServer server = startServer();
        String base = "http://127.0.0.1:" + server.getAddress().getPort();
        HttpClient client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build();

        HttpResponse<String> p = client.send(HttpRequest.newBuilder(URI.create(base + "/products/1")).build(), HttpResponse.BodyHandlers.ofString());
        check("GET product returns 200", p.statusCode() == 200, "got " + p.statusCode());
        check("product is JSON", p.headers().firstValue("Content-Type").orElse("").contains("json"), p.headers().map().toString());
        check("product has a price", p.body().matches(".*\\"price\\":\\\\d+.*"), p.body());

        HttpRequest order = HttpRequest.newBuilder(URI.create(base + "/orders"))
                .header("Authorization", "secret-token")
                .POST(HttpRequest.BodyPublishers.ofString("{\\"product\\":1,\\"qty\\":2}")).build();
        HttpResponse<String> o = client.send(order, HttpResponse.BodyHandlers.ofString());
        check("POST order returns 201", o.statusCode() == 201, "got " + o.statusCode());
        check("Location header points to the order", o.headers().firstValue("Location").orElse("").startsWith("/orders/"), o.headers().map().toString());

        HttpResponse<String> anon = client.send(HttpRequest.newBuilder(URI.create(base + "/orders")).POST(HttpRequest.BodyPublishers.noBody()).build(), HttpResponse.BodyHandlers.ofString());
        check("POST without a token returns 401", anon.statusCode() == 401, "got " + anon.statusCode());
        check("unknown path returns 404", client.send(HttpRequest.newBuilder(URI.create(base + "/nope")).build(), HttpResponse.BodyHandlers.discarding()).statusCode() == 404, "");
        check("deliberately wrong: product costs 50", p.body().contains("\\"price\\":50"), "body was " + p.body());

        System.out.println(passed + " passed, " + failed + " failed");
        server.stop(0);
    }
}
''', 'An API test suite with nothing but the JDK', trace=False),
}

DG = {
    'jdbc': {'t': 'What happens during one JDBC query', 'w': 900, 'h': 280, 'mw': 640,
        'n': [['app', 30, 50, 200, 60, 'Your code', {'c': 1, 'sub': 'prepareStatement'}],
              ['drv', 350, 50, 200, 60, 'JDBC driver', {'c': 3, 'sub': 'H2, PostgreSQL, MySQL'}],
              ['dbs', 670, 50, 200, 60, 'Database', {'c': 2, 'sub': 'plans and runs SQL'}],
              ['rs', 670, 180, 200, 60, 'ResultSet', {'c': 4, 'sub': 'rows, one at a time'}],
              ['pool', 350, 180, 200, 60, 'Connection pool', {'c': 5, 'sub': 'reuses connections'}]],
        'e': [['app', 'drv', {'t': 'SQL + values', 'id': 'q1'}], ['drv', 'dbs', {'t': 'network', 'id': 'q2'}], ['dbs', 'rs', {'t': 'rows', 'id': 'q3'}],
              ['pool', 'drv', {'id': 'q4', 'd': 1}]],
        'st': [[['app'], 'Your code only talks to the java.sql interfaces: Connection, PreparedStatement and ResultSet.'],
               [['drv', 'q1'], 'The driver, a JAR from the database vendor, implements those interfaces. Switching databases mostly means switching the driver and the URL.'],
               [['dbs', 'q2'], 'The driver sends the SQL with ? placeholders and the values separately. The database plans the query once and fills in the values.'],
               [['rs', 'q3'], 'Rows come back in a ResultSet. rs.next() moves to the next row and returns false at the end.'],
               [['pool', 'q4'], 'Opening a connection is slow, so real services borrow connections from a pool such as HikariCP and give them back when the try block ends.']]},
    'http': {'t': 'The life of one HTTP request', 'w': 900, 'h': 280, 'mw': 640,
        'n': [['b', 30, 40, 220, 60, 'HttpRequest.newBuilder', {'c': 1, 'sub': 'URI, method, headers, body'}],
              ['c', 30, 170, 220, 60, 'HttpClient.send', {'c': 3, 'sub': 'or sendAsync'}],
              ['n', 340, 105, 200, 60, 'Network', {'c': 5, 'sub': 'HTTP/1.1, 2 or 3'}],
              ['s', 630, 40, 240, 60, 'Server', {'c': 2, 'sub': 'routes and replies'}],
              ['r', 630, 170, 240, 60, 'HttpResponse', {'c': 4, 'sub': 'status, headers, body'}]],
        'e': [['b', 'c', {'t': 'build()', 'id': 'h1'}], ['c', 'n', {'id': 'h2'}], ['n', 's', {'t': 'request', 'id': 'h3'}], ['s', 'r', {'t': 'response', 'id': 'h4'}]],
        'st': [[['b'], 'A request is an immutable value built step by step: where to go, which method, which headers, and an optional body.'],
               [['c', 'h1'], 'One HttpClient is reused for many requests. It keeps connections open and handles redirects, timeouts and HTTP versions.'],
               [['n', 'h2', 'h3'], 'The request travels over the network. The client uses HTTP/2 when the server supports it, and HTTP/3 if you opt in on Java 26 or later.'],
               [['s', 'r', 'h4'], 'The server answers with a status code, headers and a body. A body handler decides how to read it: as a String, a file, a stream, or not at all.']]},
}

PARTS = [
    part('jdbc', '🗃️', 'JDBC: talking to a database', '''
<p>Almost every real application stores data in a database. <b>JDBC</b> (Java Database Connectivity) is the standard API in <code>java.sql</code> for that. Your code uses the same interfaces whatever the database, and a <b>driver</b> JAR does the database specific work. The examples here use H2, a small database written in Java that can live entirely in memory, so they really run.</p>
<div class="viz" data-viz="flow" data-k="jdbc"></div>
[[connect]]
<div class="tip">Every Connection, Statement and ResultSet holds resources in the database. Always open them in try-with-resources so they close even when an exception is thrown. Leaked connections are a classic cause of "the app froze after a few hours".</div>
''', kw=['JDBC', 'java.sql', 'DriverManager', 'Connection', 'Statement', 'ResultSet', 'executeQuery', 'executeUpdate', 'H2', 'JDBC URL', 'driver']),
    part('prepared', '🛡️', 'PreparedStatement and SQL injection', '''
<p>The most famous database bug is <b>SQL injection</b>. When user input is glued into SQL text, a quote in the input can end the string early and change the meaning of the query. Try it in the widget first, then see the real database do it.</p>
<div class="viz" data-viz="jsql"></div>
[[inject]]
<p>A <b>PreparedStatement</b> sends the SQL with <code>?</code> placeholders, and the values separately. The database never reads a value as SQL, whatever it contains. As a bonus, the database can reuse the query plan, so repeated queries run faster.</p>
<div class="note">Testers check for this by typing <code>'</code>, <code>' OR '1'='1</code> and <code>'; DROP TABLE users; --</code> into every input field and API parameter. A 500 error or extra rows is a serious bug.</div>
''', kw=['PreparedStatement', 'SQL injection', 'placeholder', 'setString', 'bind parameters', 'OWASP', 'security testing', 'query plan']),
    part('transactions', '🏦', 'Transactions: all or nothing', '''
<p>A bank transfer is two updates: take money from one account and add it to another. If the program crashes between them, money appears or disappears. A <b>transaction</b> groups statements so they all succeed together (<b>commit</b>) or all are undone (<b>rollback</b>).</p>
[[tx]]
<p>In the failed transfer the first update had already added 1000 to asha. The rollback undid it, so the balances are exactly as before. By default JDBC commits every statement on its own (auto commit). Turn that off for a group of statements that belong together.</p>
<div class="tw"><table class="jt"><tr><th>ACID</th><th>Means</th></tr>
<tr><td>Atomic</td><td>all statements or none</td></tr>
<tr><td>Consistent</td><td>rules such as CHECK constraints always hold</td></tr>
<tr><td>Isolated</td><td>other users do not see half finished work</td></tr>
<tr><td>Durable</td><td>after commit, the data survives a crash</td></tr></table></div>
''', kw=['transaction', 'commit', 'rollback', 'setAutoCommit', 'ACID', 'atomic', 'isolation', 'CHECK constraint', 'money transfer']),
    part('batch', '📦', 'Generated keys, batches and records', '''
<p>Three everyday needs: getting the id the database generated for a new row, inserting many rows quickly, and turning rows into Java objects. Records are a natural fit for rows.</p>
[[batch]]
<div class="tip">In real projects, libraries such as Spring's JdbcClient, jOOQ or JPA with Hibernate remove most of this code. They all use JDBC underneath, so knowing it helps when you need to read their logs or fix a slow query.</div>
''', kw=['getGeneratedKeys', 'RETURN_GENERATED_KEYS', 'addBatch', 'executeBatch', 'batch insert', 'row mapping', 'records', 'DAO', 'JPA', 'Hibernate', 'jOOQ', 'HikariCP']),
    part('httpclient', '🌐', 'HttpClient: calling web APIs (Java 11)', '''
<p>Since Java 11, the JDK has a modern HTTP client in <code>java.net.http</code>. It supports HTTP/1.1 and HTTP/2, synchronous and asynchronous calls, and timeouts. Each example below starts a tiny local server first with <code>com.sun.net.httpserver</code>, so the calls really happen.</p>
<div class="viz" data-viz="flow" data-k="http"></div>
[[get]]
<p>The protocol says HTTP_1_1 even though the client prefers HTTP/2. The little test server only speaks HTTP/1.1, so the client quietly falls back. Against a real HTTPS API that supports it, the same code would print HTTP_2.</p>
[[post]]
<div class="tw"><table class="jt"><tr><th>Status</th><th>Meaning</th></tr>
<tr><td>200 OK, 201 Created, 204 No Content</td><td>it worked</td></tr>
<tr><td>301, 302, 304</td><td>look elsewhere, or use your cached copy</td></tr>
<tr><td>400, 401, 403, 404, 405, 409, 429</td><td>the client did something wrong</td></tr>
<tr><td>500, 502, 503, 504</td><td>the server failed</td></tr></table></div>
''', kw=['HttpClient', 'HttpRequest', 'HttpResponse', 'BodyHandlers', 'BodyPublishers', 'GET', 'POST', 'headers', 'status code', 'JSON', 'REST API', 'com.sun.net.httpserver']),
    part('async', '⏱️', 'Timeouts, async calls and HTTP/3', '''
<p>A call to another service can hang. Always set a <b>connect timeout</b> on the client and a <b>request timeout</b> on each request. Since Java 26 the request timeout also covers reading the response body, not only waiting for the headers. <code>sendAsync</code> returns a CompletableFuture, so many calls can run at the same time.</p>
[[async]]
<p>Java 26 added <b>HTTP/3</b> to the client (JEP 517). HTTP/3 runs over QUIC on UDP and handles lossy mobile networks better. It is opt in, and the default stays HTTP/2.</p>
[[http3]]
''', kw=['timeout', 'HttpTimeoutException', 'connectTimeout', 'sendAsync', 'CompletableFuture', 'HTTP/2', 'HTTP/3', 'QUIC', 'JEP 517', 'Java 26', 'H3_DISCOVERY']),
    part('scenario', '🎬', 'Real world scenario: an API test suite with only the JDK', '''
<div class="scenario"><b>The situation</b>A team wants a smoke test that runs right after deployment, with no extra libraries to install on the build agent.</div>
[[apitest]]
<p>The one failing check is there on purpose, to show what a failure report looks like. In bigger projects the same checks are written with REST Assured or JUnit, but they still send these requests and compare these status codes, headers and bodies. Read the API testing subject for the full story.</p>
''', kw=['API testing', 'smoke test', 'status code assertion', 'REST Assured', 'contract checks', 'HttpClient test', 'post deployment check']),
]

INFO = {'title': 'Two doors to the outside world', 'panels': [
    panel([['e', '🗃️'], ['t', 'rs.next()', {'b': 1}]], 'JDBC', 'Same API for every database.', 'Always close with try-with-resources.'),
    panel([['e', '🛡️'], ['t', 'WHERE name = ?', {'b': 1}]], 'PreparedStatement', 'Values are never read as SQL.', 'That stops SQL injection.'),
    panel([['e', '🏦'], ['t', 'commit() / rollback()', {'b': 1, 'size': 11}]], 'Transactions', 'All or nothing.', 'Turn off auto commit for a group.'),
    panel([['e', '🌐'], ['t', 'client.send(req, ofString())', {'b': 1, 'size': 10}]], 'HttpClient', 'Status, headers, body.', 'Set timeouts and use sendAsync for many calls.')],
    'remember': 'Use PreparedStatement for every query with input, transactions for changes that belong together, and try-with-resources for every JDBC object. Reuse one HttpClient, set timeouts, and check status codes before trusting a body.'}

REAL = [
    ['🛒', 'An online shop', 'Places an order in one transaction: the order row, its items and the stock updates are committed together or not at all.'],
    ['🔐', 'A security test team', 'Found a login form that glued input into SQL. Switching to PreparedStatement fixed it in one line per query.'],
    ['🚦', 'A release pipeline', 'Runs a JDK only HttpClient smoke test after each deploy and rolls back automatically when any check fails.'],
]

SAY = [
    say('top', 'Welcome', 'Welcome to JDBC and HttpClient: talking to a database and calling web APIs from Java, with real runs.',
        'JDBC और HttpClient में स्वागत है: Java से database और web APIs से बात करना, असली runs के साथ।',
        'JDBC ಮತ್ತು HttpClient ಗೆ ಸ್ವಾಗತ: database ಮತ್ತು web APIs ಜೊತೆ ಮಾತನಾಡುವುದು.',
        'JDBC ଏବଂ HttpClient କୁ ସ୍ୱାଗତ: database ଏବଂ web APIs ସହ କଥା ହେବା।',
        'مرحبًا بك في JDBC وHttpClient: التحدث إلى قاعدة بيانات واستدعاء واجهات الويب من Java بتشغيل حقيقي.',
        'Willkommen zu JDBC und HttpClient: mit einer Datenbank sprechen und Web-APIs aus Java aufrufen, mit echten Läufen.'),
    say('jdbc', 'JDBC', 'Get a Connection, run SQL with a Statement, and read rows from a ResultSet with next. Close everything with try with resources.',
        'Connection लें, Statement से SQL चलाएँ, और ResultSet से next के साथ rows पढ़ें। try with resources से सब बंद करें।',
        'Connection ಪಡೆದು Statement ನಿಂದ SQL ಓಡಿಸಿ, ResultSet ನಿಂದ rows ಓದಿ.',
        'Connection ନେଇ Statement ଦ୍ୱାରା SQL ଚଲାନ୍ତୁ, ResultSet ରୁ rows ପଢ଼ନ୍ତୁ।',
        'احصل على اتصال، ونفذ SQL بعبارة، واقرأ الصفوف من ResultSet باستخدام next، وأغلق كل شيء بـ try مع الموارد.',
        'Hole eine Connection, führe SQL mit einem Statement aus und lies Zeilen aus dem ResultSet mit next. Schließe alles mit try-with-resources.'),
    say('prepared', 'PreparedStatement', 'Gluing input into SQL allows SQL injection. A PreparedStatement sends values separately, so they are never read as SQL.',
        'Input को SQL में जोड़ने से SQL injection होता है। PreparedStatement values अलग भेजता है, इसलिए वे कभी SQL नहीं बनते।',
        'Input ಅನ್ನು SQL ಗೆ ಅಂಟಿಸಿದರೆ injection. PreparedStatement values ಪ್ರತ್ಯೇಕವಾಗಿ ಕಳುಹಿಸುತ್ತದೆ.',
        'Input କୁ SQL ରେ ଯୋଡ଼ିଲେ injection। PreparedStatement values ଅଲଗା ପଠାଏ।',
        'لصق المدخلات في SQL يسمح بحقن SQL، أما PreparedStatement فيرسل القيم منفصلة فلا تُقرأ أبدًا على أنها SQL.',
        'Eingaben in SQL einzukleben erlaubt SQL-Injection. Ein PreparedStatement sendet Werte getrennt, sie werden nie als SQL gelesen.'),
    say('transactions', 'Transactions', 'Turn off auto commit, run the statements, then commit. If anything fails, roll back and every change is undone.',
        'Auto commit बंद करें, statements चलाएँ, फिर commit करें। कुछ गलत हो तो rollback करें और हर बदलाव वापस हो जाता है।',
        'Auto commit ಆಫ್ ಮಾಡಿ, commit ಮಾಡಿ. ವಿಫಲವಾದರೆ rollback.',
        'Auto commit ବନ୍ଦ କରି commit କରନ୍ତୁ। ବିଫଳ ହେଲେ rollback।',
        'أوقف الالتزام التلقائي، ونفذ العبارات، ثم التزم، وإذا فشل شيء فتراجع فتُلغى كل التغييرات.',
        'Schalte Auto-Commit aus, führe die Anweisungen aus und committe. Schlägt etwas fehl, mache ein Rollback und alles wird rückgängig.'),
    say('batch', 'Batches', 'Ask for generated keys to learn a new row id, use addBatch for many rows in one trip, and map each row to a record.',
        'नई row की id के लिए generated keys माँगें, कई rows के लिए addBatch इस्तेमाल करें, और हर row को record में बदलें।',
        'Generated keys, addBatch ಮತ್ತು rows ಅನ್ನು records ಗೆ ಬದಲಿಸಿ.',
        'Generated keys, addBatch ଏବଂ rows କୁ records ରେ ବଦଳାନ୍ତୁ।',
        'اطلب المفاتيح المولدة لمعرفة رقم الصف الجديد، واستخدم addBatch لصفوف كثيرة دفعة واحدة، وحوّل كل صف إلى سجل.',
        'Frage generierte Schlüssel ab, nutze addBatch für viele Zeilen auf einmal und bilde jede Zeile auf einen Record ab.'),
    say('httpclient', 'HttpClient', 'Build an HttpRequest, send it with one shared HttpClient, then check the status code, headers and body of the HttpResponse.',
        'HttpRequest बनाएँ, एक shared HttpClient से भेजें, फिर HttpResponse का status code, headers और body जाँचें।',
        'HttpRequest ರಚಿಸಿ, HttpClient ನಿಂದ ಕಳುಹಿಸಿ, status, headers, body ಪರಿಶೀಲಿಸಿ.',
        'HttpRequest ତିଆରି କରି HttpClient ଦ୍ୱାରା ପଠାନ୍ତୁ, status, headers, body ଯାଞ୍ଚ କରନ୍ତୁ।',
        'ابنِ HttpRequest وأرسله عبر HttpClient مشترك، ثم افحص رمز الحالة والترويسات والجسم في HttpResponse.',
        'Baue einen HttpRequest, sende ihn mit einem gemeinsamen HttpClient und prüfe Statuscode, Header und Body der Antwort.'),
    say('async', 'Timeouts and async', 'Set timeouts so a slow server cannot hang your program. sendAsync runs many calls at once. Java 26 adds HTTP 3 as an option.',
        'Timeouts लगाएँ ताकि धीमा server program को न रोके। sendAsync कई calls एक साथ चलाता है। Java 26 में HTTP 3 विकल्प है।',
        'Timeouts ಹೊಂದಿಸಿ. sendAsync ಹಲವು calls ಒಟ್ಟಿಗೆ. Java 26 ನಲ್ಲಿ HTTP 3.',
        'Timeouts ସେଟ୍ କରନ୍ତୁ। sendAsync ଅନେକ calls ଏକାଥରେ। Java 26 ରେ HTTP 3।',
        'اضبط المهلات حتى لا يعلّق خادم بطيء برنامجك، ويشغل sendAsync استدعاءات كثيرة معًا، وتضيف Java 26 خيار HTTP 3.',
        'Setze Timeouts, damit ein langsamer Server nichts blockiert. sendAsync führt viele Aufrufe parallel aus. Java 26 bietet HTTP 3 als Option.'),
    say('scenario', 'Scenario', 'A smoke test checks status codes, headers and bodies of a real API, with nothing but the JDK.',
        'एक smoke test केवल JDK के साथ असली API के status codes, headers और bodies जाँचता है।',
        'Smoke test JDK ಮಾತ್ರದಿಂದ API status, headers, body ಪರಿಶೀಲಿಸುತ್ತದೆ.',
        'Smoke test କେବଳ JDK ଦ୍ୱାରା API status, headers, body ଯାଞ୍ଚ କରେ।',
        'يفحص اختبار دخان رموز الحالة والترويسات والأجسام لواجهة حقيقية باستخدام JDK وحدها.',
        'Ein Smoke-Test prüft Statuscodes, Header und Bodys einer echten API, nur mit dem JDK.'),
]

QUIZ = [
    quiz('e', 'Which method moves a ResultSet to the next row?', ['next()', 'moveNext()', 'fetch()', 'read()'], 0, 'It returns false at the end.', 'A ResultSet starts before the first row, so call next() before reading.'),
    quiz('e', 'Which HTTP status means "created"?', ['201', '200', '204', '302'], 0, 'Usually after a POST.', 'A Location header often points to the new resource.'),
    quiz('e', 'Why use try-with-resources for a Connection?', ['It always closes the connection, even when an exception is thrown', 'It makes queries faster', 'It is required to compile', 'It commits automatically'], 0, 'Resource leaks.', 'Leaked connections eventually exhaust the pool.'),
    quiz('m', 'What does a PreparedStatement do with the input <code>x\' OR \'1\'=\'1</code>?', ['Treats it as one plain text value, so no user matches', 'Returns every user', 'Throws a syntax error', 'Removes the quotes'], 0, 'Values are not SQL.', 'The SQL text and the values travel separately.'),
    quiz('m', 'A transaction updates two rows, and the second update fails. What should the code call?', ['rollback()', 'commit()', 'close() only', 'nothing, JDBC undoes it by itself'], 0, 'All or nothing.', 'rollback undoes the first update too.'),
    quiz('m', 'What does <code>client.sendAsync(...)</code> return?', ['A CompletableFuture of the response', 'The response directly', 'A Thread', 'void'], 0, 'Async.', 'Use thenApply, join or allOf to work with the results.'),
    quiz('m', 'Which status code family means the server failed?', ['5xx', '4xx', '3xx', '2xx'], 0, 'Not the client\'s fault.', '4xx means the client sent something wrong.'),
    quiz('h', 'What is the default HTTP version of HttpClient in Java 26?', ['HTTP/2, and HTTP/3 is opt in', 'HTTP/3', 'HTTP/1.1', 'HTTP/1.0'], 0, 'JEP 517.', 'Choose HTTP_3 on the client or request to try it.'),
    quiz('h', 'What changed about HttpRequest timeouts in Java 26?', ['They also cover reading the response body', 'They were removed', 'They now default to 30 seconds', 'They only apply to HTTP/3'], 0, 'Body reading.', 'Before Java 26 the timeout ended once the headers arrived.'),
    quiz('h', 'Why is executeBatch faster than 1000 separate executeUpdate calls?', ['The rows go to the database in fewer round trips', 'It skips constraints', 'It does not write to disk', 'It runs in parallel threads'], 0, 'Network trips.', 'Each round trip has a fixed delay, so fewer trips save time.'),
    quiz('x', 'What does this print?', ['2', '3', '1', '0'], 0, 'Count rows in the result.', 'Two of the three prices are under 500.', code='try (var con = java.sql.DriverManager.getConnection("jdbc:h2:mem:q", "sa", "")) {\n    con.createStatement().execute("CREATE TABLE p (price INT)");\n    con.createStatement().execute("INSERT INTO p VALUES (49), (120), (899)");\n    var rs = con.createStatement().executeQuery("SELECT COUNT(*) FROM p WHERE price < 500");\n    rs.next();\n    System.out.println(rs.getInt(1));\n}', run=True),
    quiz('x', 'What does this print?', ['HTTP_2', 'HTTP_1_1', 'HTTP_3', 'null'], 0, 'The default version of a new client.', 'HttpClient prefers HTTP/2 unless told otherwise.', code='System.out.println(java.net.http.HttpClient.newHttpClient().version());', run=True),
]

CALC = [
    calc('e', 'asha has 500 and ravi 100. asha sends ravi 200. What is ravi\'s balance?', '300', 'Add to ravi.', ['<span class="eq">100 + 200 = 300</span>']),
    calc('e', 'A batch has 1000 rows. How many rows does executeBatch report in total?', '1000', 'One count per row.', ['The returned int array has one entry per batched statement.']),
    calc('m', 'Each database round trip takes 2 ms. How many ms do 1000 separate inserts spend on round trips?', '2000', '1000 trips.', ['<span class="eq">1000 × 2 ms = 2000 ms</span>', 'A single batch needs roughly one trip, which is why batches are so much faster.']),
    calc('m', 'Three API calls take 2 s each. How many seconds do they take with sendAsync at the same time?', '2', 'Wait for the slowest.', ['<span class="eq">max(2, 2, 2) = 2 s</span>']),
    calc('h', 'An API test suite has 8 checks and 1 fails. What percent pass?', '87.5', 'Passed over total.', ['<span class="eq"><span class="fr"><i>7</i><i>8</i></span> × 100 = 87.5</span>']),
    calc('h', 'What does this print?', '3', 'Rows inserted by one statement.', ['executeUpdate returns how many rows changed.'], code='try (var con = java.sql.DriverManager.getConnection("jdbc:h2:mem:c", "sa", "")) {\n    con.createStatement().execute("CREATE TABLE t (n INT)");\n    System.out.println(con.createStatement().executeUpdate("INSERT INTO t VALUES (1), (2), (3)"));\n}', run=True),
    calc('x', 'What does this print?', '0', 'An update with no matching rows.', ['No row has the name zed, so 0 rows change and no exception is thrown.'], code='try (var con = java.sql.DriverManager.getConnection("jdbc:h2:mem:z", "sa", "")) {\n    con.createStatement().execute("CREATE TABLE u (name VARCHAR(9))");\n    var ps = con.prepareStatement("UPDATE u SET name = ? WHERE name = ?");\n    ps.setString(1, "amy"); ps.setString(2, "zed");\n    System.out.println(ps.executeUpdate());\n}', run=True),
]

for q in QUIZ + CALC:
    if q.get('run') and 'h2:mem' in q.get('code', ''):
        q['_h2'] = True
        q['code'] = 'void main() throws Exception {\n' + '\n'.join('    ' + line for line in q['code'].split('\n')) + '\n}'

T = {
    'slug': 'java-jdbc-http', 'title': 'Databases and web APIs: JDBC and HttpClient', 'short': 'JDBC and HTTP', 'emoji': '🔌', 'module': MODULE, 'minutes': 26,
    'lead': 'Programs become useful when they talk to the outside world. This chapter connects Java to a real database with JDBC, shows SQL injection and how PreparedStatement stops it, groups changes into transactions, and then calls web APIs with HttpClient, including timeouts, async calls, HTTP/3 from Java 26 and a small API test suite.',
    'desc': 'JDBC with a real H2 database: Connection, Statement, ResultSet, PreparedStatement, SQL injection, transactions with commit and rollback, batches and generated keys. HttpClient: GET and POST, headers, status codes, timeouts, sendAsync, HTTP/3 in Java 26, and an API smoke test.',
    'summary': 'Connecting to H2, SQL injection on a real database and the PreparedStatement fix, a money transfer with rollback, generated keys, batches and records, HttpClient GET and POST against a local server, status codes, timeouts and sendAsync, HTTP/3 opt in, and a JDK only API test suite.',
    'keywords': ['JDBC', 'PreparedStatement', 'SQL injection', 'transaction', 'commit', 'rollback', 'batch', 'H2', 'HttpClient', 'REST API', 'status codes', 'sendAsync', 'HTTP/3', 'API testing', 'Java 26'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC,
}
