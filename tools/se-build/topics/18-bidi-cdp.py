# Chapter 6.2: WebDriver BiDi, the Chrome DevTools Protocol and advanced Grid features. Sources: selenium.dev
# documentation (BiDirectional functionality, WebDriver BiDi: Logging, Network, Chrome DevTools Protocol, Grid advanced
# features: GraphQL support and Grid endpoints), the official docs examples (LogTest.java, test_bidi_logging.py,
# logInspector.spec.js, test_network_commands.py), the W3C WebDriver BiDi specification, and real runs with Chrome 153
# and a Selenium Grid 4.51.0 standalone server.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, src, flow

K = Kit()

BIDILOG = tri('bidilog', 'Hear console messages and page errors as they happen', java=r'''
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.bidi.module.LogInspector;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

public class BidiLog {
    public static void main(String[] args) throws Exception {
        ChromeOptions options = new ChromeOptions();
        options.setCapability("webSocketUrl", true);  ## Ask for a BiDi WebSocket next to the normal HTTP connection.
        WebDriver driver = new ChromeDriver(options);
        List<String> heard = new CopyOnWriteArrayList<>();  ## Events arrive on another thread, so use a thread safe list.
        try (LogInspector inspector = new LogInspector(driver)) {  ## Subscribes to log events. Closing it unsubscribes.
            inspector.onConsoleEntry(e -> heard.add("console " + e.getLevel() + ": " + e.getText()));  ## Called for every console.log, console.error and so on.
            inspector.onJavaScriptException(e -> heard.add("page error: " + e.getText()));  ## Called for every uncaught error in the page.
            driver.get("https://www.selenium.dev/selenium/web/bidi/logEntryAdded.html");
            for (String id : new String[] {"consoleLog", "consoleError", "jsException"}) {
                driver.findElement(By.id(id)).click();
            }
            long end = System.currentTimeMillis() + 5000;
            while (heard.size() < 3 && System.currentTimeMillis() < end) Thread.sleep(50);  ## Events are pushed, not returned, so wait until all three arrived.
        }
        heard.forEach(System.out::println);
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

options = webdriver.ChromeOptions()
options.enable_bidi = True  ## Ask for a BiDi WebSocket next to the normal HTTP connection.
driver = webdriver.Chrome(options=options)
heard = []
driver.script.add_console_message_handler(lambda e: heard.append(f"console {e.level}: {e.text}"))  ## Called for every console.log, console.error and so on.
driver.script.add_javascript_error_handler(lambda e: heard.append(f"page error: {e.text}"))  ## Called for every uncaught error in the page.
driver.get("https://www.selenium.dev/selenium/web/bidi/logEntryAdded.html")
for button in ["consoleLog", "consoleError", "jsException"]:
    driver.find_element(By.ID, button).click()
WebDriverWait(driver, 5).until(lambda _: len(heard) == 3)  ## Events are pushed, not returned, so wait until all three arrived.
print("\n".join(heard))
driver.quit()
''', js=r'''
const { Builder, Browser, By } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const LogInspector = require('selenium-webdriver/bidi/logInspector');

(async function bidiLog() {
  const driver = await new Builder().forBrowser(Browser.CHROME).setChromeOptions(new chrome.Options().enableBidi()).build();  ## Ask for a BiDi WebSocket next to the normal HTTP connection.
  const heard = [];
  const inspector = await LogInspector(driver);  ## Subscribes to log events.
  await inspector.onConsoleEntry(e => heard.push(`console ${e.level}: ${e.text}`));  ## Called for every console.log, console.error and so on.
  await inspector.onJavascriptException(e => heard.push(`page error: ${e.text}`));  ## Called for every uncaught error in the page.
  await driver.get('https://www.selenium.dev/selenium/web/bidi/logEntryAdded.html');
  for (const id of ['consoleLog', 'consoleError', 'jsException']) {
    await driver.findElement(By.id(id)).click();
  }
  await driver.wait(() => heard.length === 3, 5000);  ## Events are pushed, not returned, so wait until all three arrived.
  console.log(heard.join('\n'));
  await inspector.close();
  await driver.quit();
})();
''', expect='page error: Error: Not working')

CDP = tri('cdp', 'Send Chrome DevTools commands: read the version and change the time zone', java=r'''
import java.util.Map;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.chrome.ChromeDriver;

public class Cdp {
    public static void main(String[] args) {
        ChromeDriver driver = new ChromeDriver();  ## executeCdpCommand exists on Chrome and Edge drivers only.
        driver.get("https://www.selenium.dev/selenium/web/blank.html");
        Map<String, Object> version = driver.executeCdpCommand("Browser.getVersion", Map.of());  ## Any CDP method by name, with a map of parameters.
        System.out.println("protocol " + version.get("protocolVersion") + ", " + version.get("product"));
        String zone = "return Intl.DateTimeFormat().resolvedOptions().timeZone";
        System.out.println("time zone before: " + ((JavascriptExecutor) driver).executeScript(zone));
        driver.executeCdpCommand("Emulation.setTimezoneOverride", Map.of("timezoneId", "Asia/Kolkata"));  ## Something WebDriver Classic has no command for.
        System.out.println("time zone after: " + ((JavascriptExecutor) driver).executeScript(zone));
        driver.quit();
    }
}
''', py=r'''
from selenium import webdriver

driver = webdriver.Chrome()  ## execute_cdp_cmd exists on Chrome and Edge drivers only.
driver.get("https://www.selenium.dev/selenium/web/blank.html")
version = driver.execute_cdp_cmd("Browser.getVersion", {})  ## Any CDP method by name, with a dict of parameters.
print(f"protocol {version['protocolVersion']}, {version['product']}")
zone = "return Intl.DateTimeFormat().resolvedOptions().timeZone"
print("time zone before:", driver.execute_script(zone))
driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": "Asia/Kolkata"})  ## Something WebDriver Classic has no command for.
print("time zone after:", driver.execute_script(zone))
driver.quit()
''', js=r'''
const { Builder, Browser } = require('selenium-webdriver');

(async function cdp() {
  const driver = await new Builder().forBrowser(Browser.CHROME).build();  ## sendAndGetDevToolsCommand exists on Chrome and Edge drivers only.
  await driver.get('https://www.selenium.dev/selenium/web/blank.html');
  const version = await driver.sendAndGetDevToolsCommand('Browser.getVersion', {});  ## Any CDP method by name, with an object of parameters.
  console.log(`protocol ${version.protocolVersion}, ${version.product}`);
  const zone = 'return Intl.DateTimeFormat().resolvedOptions().timeZone';
  console.log('time zone before: ' + await driver.executeScript(zone));
  await driver.sendAndGetDevToolsCommand('Emulation.setTimezoneOverride', { timezoneId: 'Asia/Kolkata' });  ## Something WebDriver Classic has no command for.
  console.log('time zone after: ' + await driver.executeScript(zone));
  await driver.quit();
})();
''', expect='time zone after: Asia/Calcutta')

GQL = tri('graphql', 'Ask the Grid exactly what you need with GraphQL', java=r'''
import java.net.URI;
import java.net.URL;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.json.Json;
import org.openqa.selenium.remote.RemoteWebDriver;

@SuppressWarnings("unchecked")
public class GridQuery {
    static final Json JSON = new Json();  ## Selenium ships its own JSON reader.

    static Map<String, Object> ask(String query) throws Exception {
        String body = "{\"query\": \"" + query + "\"}";  ## GraphQL over HTTP: one POST with the query as a string.
        String text = HttpClient.newHttpClient().send(
            HttpRequest.newBuilder(URI.create("http://localhost:4444/graphql")).POST(HttpRequest.BodyPublishers.ofString(body)).build(),
            HttpResponse.BodyHandlers.ofString()).body();
        Map<String, Object> reply = JSON.toType(text, Json.MAP_TYPE);
        return (Map<String, Object>) reply.get("data");  ## The answer sits under data.
    }

    public static void main(String[] args) throws Exception {
        String q = "{ grid { nodeCount, totalSlots, maxSession, sessionCount, sessionQueueSize } }";  ## Ask only for these fields.
        System.out.println("idle: " + ask(q).get("grid"));
        ChromeOptions options = new ChromeOptions();
        options.setCapability("se:name", "graphql demo");
        RemoteWebDriver driver = new RemoteWebDriver(new URL("http://localhost:4444"), options);
        System.out.println("busy: " + ask(q).get("grid"));  ## One session is running now.
        Map<String, Object> info = (Map<String, Object>) ask("{ sessionsInfo { sessions { capabilities } } }").get("sessionsInfo");
        List<Map<String, Object>> sessions = (List<Map<String, Object>>) info.get("sessions");
        System.out.println("names: " + sessions.stream()
            .map(x -> JSON.<Map<String, Object>>toType((String) x.get("capabilities"), Json.MAP_TYPE).get("se:name"))  ## The se:name metadata is in the session capabilities.
            .collect(Collectors.toList()));
        driver.quit();
    }
}
''', py=r'''
import json
import urllib.request

from selenium import webdriver


def ask(query):
    req = urllib.request.Request("http://localhost:4444/graphql", data=json.dumps({"query": query}).encode(), method="POST")  ## GraphQL over HTTP: one POST with the query as a string.
    with urllib.request.urlopen(req) as res:
        return json.load(res)["data"]


q = "{ grid { nodeCount, totalSlots, maxSession, sessionCount, sessionQueueSize } }"  ## Ask only for these fields.
print("idle:", ask(q)["grid"])
options = webdriver.ChromeOptions()
options.set_capability("se:name", "graphql demo")
driver = webdriver.Remote("http://localhost:4444", options=options)
print("busy:", ask(q)["grid"])  ## One session is running now.
sessions = ask("{ sessionsInfo { sessions { capabilities } } }")["sessionsInfo"]["sessions"]
print("names:", [json.loads(s["capabilities"]).get("se:name") for s in sessions])  ## The se:name metadata is in the session capabilities.
driver.quit()
''', js=r'''
const { Builder, Browser } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');

async function ask(query) {
  const res = await fetch('http://localhost:4444/graphql', { method: 'POST', body: JSON.stringify({ query }) });  ## GraphQL over HTTP: one POST with the query as a string.
  return (await res.json()).data;
}

(async function gridQuery() {
  const q = '{ grid { nodeCount, totalSlots, maxSession, sessionCount, sessionQueueSize } }';  ## Ask only for these fields.
  console.log('idle: ' + JSON.stringify((await ask(q)).grid));
  const options = new chrome.Options();
  options.set('se:name', 'graphql demo');
  const driver = await new Builder().forBrowser(Browser.CHROME).setChromeOptions(options).usingServer('http://localhost:4444').build();
  console.log('busy: ' + JSON.stringify((await ask(q)).grid));  ## One session is running now.
  const sessions = (await ask('{ sessionsInfo { sessions { capabilities } } }')).sessionsInfo.sessions;
  console.log('names: ' + JSON.stringify(sessions.map(s => JSON.parse(s.capabilities)['se:name'])));  ## The se:name metadata is in the session capabilities.
  await driver.quit();
})();
''', needs='grid', expect='busy')

K.lesson('bidi', 'WebDriver BiDi: the browser talks back', f'''
<p>Everything so far followed one pattern: the test asks, the driver answers. The documentation calls this strict request and response, and it is exactly what you want for clicks and reads. It cannot tell you about something you did not ask for, such as a message the page logged or an error it threw a second ago.</p>
<p><b>WebDriver BiDi</b> is a newer W3C protocol that adds a WebSocket next to the HTTP connection. Over it the browser can push <b>events</b> to the test the moment they happen. The Selenium team and the browser vendors build it together as a stable, cross browser replacement for the Chrome DevTools Protocol.</p>
{viz('se-bidi')}
{BIDILOG}
<p>The test never asked for a log. It subscribed once, and each click made the browser push an event. Three different events arrived: a console message at level info, one at level error, and an uncaught JavaScript error. A test can now fail on any page error, even when the page still looks fine.</p>
{table(['How to switch it on', 'Java', 'Python', 'JavaScript'], [
    ['Capability', '<code>options.setCapability("webSocketUrl", true)</code>', '<code>options.enable_bidi = True</code>', '<code>new chrome.Options().enableBidi()</code>'],
    ['Console and page errors', '<code>new LogInspector(driver)</code>', '<code>driver.script.add_console_message_handler</code>', '<code>await LogInspector(driver)</code>']])}
{note('BiDi is still growing. The documentation lists log, network, script and browsing context features, and some network APIs are marked as not yet stable in some bindings, for example the Python docs example uses an underscore method for intercepts. Check the documentation page for your binding before you build on a feature.', 'warn')}
''', kw=['bidi', 'webdriver bidi', 'websocket', 'events', 'console log', 'javascript error', 'log inspector', 'bidirectional'])

K.lesson('cdp', 'The Chrome DevTools Protocol', f'''
<p>Before BiDi existed, Selenium gave access to the <b>Chrome DevTools Protocol</b>, the protocol Chrome DevTools uses to debug pages. The documentation is careful about it: CDP was not designed for testing and has no stable API, so features depend on the browser version. Selenium supports the three most recent Chrome versions for its generated CDP classes. The Java jars in this course carry v153, v154 and v155.</p>
{CDP}
<p>Two lines show the point. <code>Browser.getVersion</code> returns information no W3C command gives. <code>Emulation.setTimezoneOverride</code> changed what the page believes its time zone is, without touching the machine. The page then reports Asia/Calcutta, because Chrome uses the older canonical name for the zone you set as Asia/Kolkata. This is how a test can check how a page shows times in India from a server in another country.</p>
{table(['', 'WebDriver Classic', 'CDP', 'WebDriver BiDi'], [
    ['Standard', 'W3C Recommendation', 'Chrome only, no stability promise', 'W3C, in progress'],
    ['Browsers', 'All', 'Chrome and Edge', 'Chrome, Edge and Firefox, growing'],
    ['Style', 'Request and response over HTTP', 'Commands and events over WebSocket', 'Commands and events over WebSocket'],
    ['Use it for', 'Every normal test step', 'Chromium features with no other API', 'Events, logs, network, and the future of Selenium']])}
{note('The documentation calls out two popular CDP examples with limited value: emulated geolocation, because most sites use the IP address, and overriding device metrics, because Chrome mobile emulation in the options is the better tool.', 'tip')}
''', kw=['cdp', 'chrome devtools protocol', 'devtools', 'execute cdp command', 'emulation', 'time zone', 'browser version', 'chromium'])

K.lesson('gridplus', 'Grid features: GraphQL and endpoints', f'''
<p>A Grid with many nodes needs a way to see what is going on. Besides the <code>/status</code> endpoint from chapter 6.1, the Grid answers <b>GraphQL</b> queries at <code>/graphql</code>. GraphQL lets you ask for exactly the fields you need, nothing more.</p>
{GQL}
<p>The run shows the Grid idle, then with one session, and the <code>se:name</code> metadata travelling in the session capabilities. The queue size field is how a CI system can notice that tests are waiting for slots and start more nodes.</p>
{table(['Endpoint', 'What it does'], [
    ['GET /status', 'Current state of the Grid and every node, with slots and sessions'],
    ['POST /graphql', 'Ask for exactly the fields you need: grid, nodesInfo, sessionsInfo, session(id)'],
    ['DELETE /session/&lt;id&gt;', 'End a session and free its slot'],
    ['POST /se/grid/distributor/node/&lt;node-id&gt;/drain', 'Stop a node after its running sessions end, with no new sessions. Needs the registration secret header'],
    ['DELETE /se/grid/distributor/node/&lt;node-id&gt;', 'Remove a node from the Distributor. Its running sessions continue']])}
{ladder(
    '<p>BiDi lets the browser tell the test about events, such as console messages and page errors, the moment they happen. CDP gives Chrome only extras. GraphQL tells you what the Grid is doing.</p>',
    '<p>Turn on BiDi with the webSocketUrl capability, then subscribe to log events. Use CDP commands by name for Chromium features with no W3C command. Query the Grid at /graphql for counts, sessions and the queue.</p>',
    '<p>BiDi and CDP both use a WebSocket with commands and events, but BiDi is a W3C standard across browsers while CDP has no stability promise. On a Grid, se:cdp in the capabilities is the DevTools address routed through the Grid.</p>',
    '<p>Selenium is moving its own implementation from Classic to BiDi while keeping compatibility. Network interception, authentication handlers and preload scripts are the next layer, and the Grid adds observability with tracing for each component.</p>')}
''', kw=['graphql', 'grid endpoints', 'drain node', 'remove node', 'status', 'session queue size', 'observability'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What does BiDi add to WebDriver?', ['Faster clicks', 'Events pushed from the browser over a WebSocket', 'New locators', 'Grid support'], 1,
       'Two directions.', 'The browser can push events to the test as they happen.')
K.quiz('e', 'Which capability turns on BiDi?', ['enableCdp', 'webSocketUrl', 'bidi:true', 'se:bidi'], 1,
       'A WebSocket address.', 'Setting webSocketUrl to true asks for the BiDi WebSocket.')
K.quiz('e', 'Which browsers support CDP commands in Selenium?', ['All', 'Chrome and Edge', 'Firefox only', 'Safari'], 1,
       'Chrome DevTools.', 'CDP is a Chromium protocol, so Chrome and Edge.')
K.quiz('m', 'Why does the documentation warn about CDP?', ['It is slow', 'It is not designed for testing and has no stable API', 'It needs a Grid', 'It cannot run JavaScript'], 1,
       'Stability.', 'CDP changes with browser versions and was not built for testing.')
K.quiz('m', 'In the BiDi run, how did the test learn about the page error?', ['It polled the console', 'The browser pushed an event to a handler', 'It read a log file', 'It took a screenshot'], 1,
       'Subscribe once.', 'The handler was called when the event arrived.')
K.quiz('m', 'How many Chrome versions does Selenium support with generated CDP classes at a time?', ['1', '3', '5', 'All'], 1,
       'The jars show v153 to v155.', 'The three most recent versions.')
K.quiz('m', 'What is the advantage of GraphQL on the Grid?', ['It is faster than HTTP', 'You ask for exactly the fields you need', 'It starts nodes', 'It replaces /status entirely'], 1,
       'Exactly what you need.', 'GraphQL returns only the fields in the query.')
K.quiz('h', 'Why might an emulated geolocation not change what a site shows?', ['CDP is broken', 'Most sites use the IP address for location', 'Chrome ignores it', 'It needs BiDi'], 1,
       'From the documentation.', 'Most sites use the IP address, so the emulated position rarely matters.')
K.quiz('h', 'What does draining a Grid node do?', ['Kills its sessions', 'Lets running sessions finish and accepts no new ones', 'Restarts the node', 'Clears the queue'], 1,
       'Graceful.', 'A drained node stops after its sessions end and takes no new ones.')
K.quiz('x', 'A CI system wants to add nodes when tests wait for slots. Which GraphQL field fits?', ['nodeCount', 'sessionQueueSize', 'version', 'uri'], 1,
       'Waiting tests.', 'sessionQueueSize counts requests waiting for a slot.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A page logs 3 console messages and throws 2 errors. With console and error handlers, how many events arrive?', '5', 'Count both.',
       ['3 console events.', '2 error events.', eq('3 + 2 = 5 events')], check=5)
K.calc('e', 'Selenium supports the 3 newest Chrome versions for CDP. The newest is 155. What is the oldest supported?', '153', 'Count back.',
       ['155, 154, 153.', 'Three versions.', eq('153')], check=153)
K.calc('m', 'A Grid has 4 nodes with 4 slots each and 10 running sessions. How many free slots are there?', '6', 'Total minus used.',
       ['Total: 4 × 4 = 16.', 'Used: 10.', eq('16 − 10 = 6 free')], check=6)
K.calc('m', 'Polling a page log every 500 ms, an error is seen on average after half the interval. How many ms faster is a pushed BiDi event, ignoring network time?', '250', 'Half the poll interval.',
       ['Polling finds it on average 250 ms late.', 'A pushed event arrives at once.', eq('About 250 ms faster')], check=250, unit='ms')
K.calc('h', 'sessionQueueSize is 12 and each new node has 4 slots. How many nodes clear the queue at once?', '3', 'Divide and round up.',
       ['12 ÷ 4 = 3.', 'No remainder.', eq('3 nodes')], check=3)
K.calc('x', 'Kolkata is UTC+5:30. A page shows 09:00 UTC in local time. What does it show after the time zone override, in hours with decimals?', '14.5', 'Add the offset.',
       ['UTC+5:30 is 5.5 hours ahead.', '9 + 5.5.', eq('14.5, which is 14:30')], check=14.5, unit='h')

# ---------------------------------------------------------------- assignments
K.assign('pageerrors', 'e', 'Fail on page errors',
         '<p>Write <code>page_ok(events)</code>. Each event is a dict with <code>type</code> ("console" or "javascript") and <code>level</code> ("info", "warn" or "error"). Return False if any event is of type "javascript" or has level "error", otherwise True.</p>',
         '''
def page_ok(events):
    # your code here
    pass
''', [('page_ok([{"type": "console", "level": "info"}])', True), ('page_ok([{"type": "console", "level": "error"}])', False), ('page_ok([{"type": "javascript", "level": "error"}])', False), ('page_ok([])', True)],
         '''
def page_ok(events):
    for e in events:
        if e["type"] == "javascript" or e["level"] == "error":
            return False
    return True
''', 'One loop, two conditions.', '<p>Collect events with BiDi handlers during a test and check them in the after each step, so every test also fails on page errors.</p>')
K.assign('freeslots', 'm', 'Read a GraphQL answer',
         '<p>Write <code>free_slots(answer)</code>. <code>answer</code> is the <code>grid</code> part of a GraphQL reply, a dict with <code>maxSession</code>, <code>sessionCount</code> and <code>sessionQueueSize</code>. Return how many more sessions can start now: max sessions minus running sessions, never below 0. If requests are waiting, return 0.</p>',
         '''
def free_slots(answer):
    # your code here
    pass
''', [('free_slots({"maxSession": 2, "sessionCount": 1, "sessionQueueSize": 0})', 1), ('free_slots({"maxSession": 2, "sessionCount": 2, "sessionQueueSize": 3})', 0), ('free_slots({"maxSession": 4, "sessionCount": 0, "sessionQueueSize": 0})', 4)],
         '''
def free_slots(answer):
    if answer["sessionQueueSize"] > 0:
        return 0
    return max(0, answer["maxSession"] - answer["sessionCount"])
''', 'Check the queue first.', '<p>maxSession is the limit of concurrent sessions, which on the Grid in this course is 2 even though it offers 6 slots.</p>')

K.must('BiDi', 'A W3C protocol with a WebSocket, so the browser can push events. Turn it on with webSocketUrl, then subscribe to console and page errors.')
K.must('Events, not polling', 'Handlers are called when events arrive. Wait for them, because they come after the action that caused them.')
K.must('CDP', 'Chrome and Edge only, no stability promise, the three newest Chrome versions. Use it for Chromium features with no other API.')
K.must('GraphQL', 'POST a query to /graphql on the Grid for nodes, slots, sessions and the queue size.')
K.must('Grid endpoints', '/status, DELETE /session, and drain or remove a node through the Distributor endpoints.')

T = K.topic(
    slug='bidi-cdp', topic='bidi-cdp',
    step=(6, 'Scale out with Grid', 'se-scale', 'Selenium Grid 4: components, roles, remote sessions and parallel runs, then BiDi, CDP and Grid features.', 'Advanced'),
    title='WebDriver BiDi, CDP and Grid features', short='BiDi, CDP, GraphQL', badge='6.2', minutes=50, added='2026-10-29',
    lead='Let the browser talk back with WebDriver BiDi events, reach Chromium extras through the Chrome DevTools Protocol, and look inside a running Grid with GraphQL.',
    desc='Classic request and response against BiDi events with an animation, real console and page error events in Java, Python and JavaScript, CDP commands for the browser version and a time zone override, a comparison of Classic, CDP and BiDi, and Grid GraphQL queries and endpoints from real runs.',
    summary='WebDriver BiDi events, Chrome DevTools Protocol commands and Grid GraphQL.',
    keywords=['bidi', 'webdriver bidi', 'cdp', 'devtools', 'websocket', 'events', 'log inspector', 'graphql', 'grid endpoints', 'drain'],
    recap='<p>BiDi adds a WebSocket so the browser pushes events such as console messages and page errors. CDP gives Chrome and Edge extras with no stability promise. The Grid answers GraphQL queries for exactly the counts and sessions you need, and has endpoints to end sessions and drain or remove nodes.</p>')
