# Chapter 6.1: Selenium Grid 4. Sources: selenium.dev documentation (Grid: When to use Grid, Components, Getting
# started with Standalone, Hub and Node and Distributed roles and their default ports, Metadata in tests, Querying
# Selenium Grid, Grid sizes, Remote WebDriver and the file detector), and real runs against a Selenium Grid 4.51.0
# standalone server on http://localhost:4444 started by runner.py with --max-sessions 2.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, src, flow

K = Kit()

STATUS = tri('gridstatus', 'Ask the Grid if it is ready and what it offers', java=r'''
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.List;
import java.util.Map;
import org.openqa.selenium.json.Json;

public class GridStatus {
    @SuppressWarnings("unchecked")  ## JSON gives back plain objects, so the casts are unchecked.
    public static void main(String[] args) throws Exception {
        HttpResponse<String> res = HttpClient.newHttpClient().send(
            HttpRequest.newBuilder(URI.create("http://localhost:4444/status")).build(),  ## The same endpoint a driver has, now answered by the Grid.
            HttpResponse.BodyHandlers.ofString());
        Map<String, Object> body = new Json().toType(res.body(), Json.MAP_TYPE);  ## Selenium ships its own JSON reader.
        Map<String, Object> value = (Map<String, Object>) body.get("value");
        System.out.println("ready: " + value.get("ready") + ", " + value.get("message"));
        List<Map<String, Object>> nodes = (List<Map<String, Object>>) value.get("nodes");
        Map<String, Object> node = nodes.get(0);
        System.out.println("nodes: " + nodes.size() + ", max sessions: " + node.get("maxSessions"));
        for (Map<String, Object> slot : (List<Map<String, Object>>) node.get("slots")) {
            System.out.println("slot: " + ((Map<String, Object>) slot.get("stereotype")).get("browserName"));  ## Each slot can hold one session of this browser.
        }
    }
}
''', py=r'''
import json
import urllib.request

with urllib.request.urlopen("http://localhost:4444/status") as res:  ## The same endpoint a driver has, now answered by the Grid.
    value = json.load(res)["value"]
print(f"ready: {value['ready']}, {value['message']}")
node = value["nodes"][0]
print(f"nodes: {len(value['nodes'])}, max sessions: {node['maxSessions']}")
for slot in node["slots"]:
    print("slot:", slot["stereotype"]["browserName"])  ## Each slot can hold one session of this browser.
''', js=r'''
(async function gridStatus() {
  const res = await fetch('http://localhost:4444/status');  ## The same endpoint a driver has, now answered by the Grid.
  const value = (await res.json()).value;
  console.log('ready: ' + value.ready + ', ' + value.message);
  const node = value.nodes[0];
  console.log('nodes: ' + value.nodes.length + ', max sessions: ' + node.maxSessions);
  for (const slot of node.slots) {
    console.log('slot: ' + slot.stereotype.browserName);  ## Each slot can hold one session of this browser.
  }
})();
''', needs='grid', expect='max sessions: 2')

REMOTE = tri('remote', 'Run a test on the Grid with a name and a file upload', java=r'''
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.remote.LocalFileDetector;
import org.openqa.selenium.remote.RemoteWebDriver;

public class OnTheGrid {
    public static void main(String[] args) throws Exception {
        ChromeOptions options = new ChromeOptions();  ## Options say which browser you want. The Grid picks a node that has it.
        options.setCapability("se:name", "upload on the grid");  ## se: capabilities are Grid metadata. se:name shows in the Grid UI.
        RemoteWebDriver driver = new RemoteWebDriver(new URL("http://localhost:4444"), options);  ## The only change from a local test: a URL instead of a local driver.
        for (String k : new String[] {"browserName", "platformName", "se:name", "se:cdp"}) {
            Object v = driver.getCapabilities().getCapability(k);
            System.out.println(k + ": " + (k.equals("se:cdp") ? String.valueOf(v).replaceAll("[0-9a-f]{32}", "{id}") : v));  ## se:cdp is a DevTools address that goes through the Grid.
        }
        Path file = Files.writeString(Files.createTempDirectory("up").resolve("report.txt"), "hello grid");
        driver.setFileDetector(new LocalFileDetector());  ## Sends the local file to the node, which may be another machine.
        driver.get("https://www.selenium.dev/selenium/web/upload.html");
        WebElement input = driver.findElement(By.id("upload"));
        input.sendKeys(file.toAbsolutePath().toString());
        System.out.println("attached: " + driver.executeScript("return arguments[0].files[0].name", input));  ## The browser on the node has the file.
        driver.quit();
    }
}
''', py=r'''
import os
import tempfile

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.file_detector import LocalFileDetector

options = webdriver.ChromeOptions()  ## Options say which browser you want. The Grid picks a node that has it.
options.set_capability("se:name", "upload on the grid")  ## se: capabilities are Grid metadata. se:name shows in the Grid UI.
driver = webdriver.Remote("http://localhost:4444", options=options)  ## The only change from a local test: a URL instead of a local driver.
for k in ["browserName", "platformName", "se:name", "se:cdp"]:
    v = driver.capabilities.get(k)
    print(k + ":", v if k != "se:cdp" else v.replace(driver.session_id, "{id}"))  ## se:cdp is a DevTools address that goes through the Grid.
path = os.path.join(tempfile.mkdtemp(), "report.txt")
with open(path, "w") as f:
    f.write("hello grid")
driver.file_detector = LocalFileDetector()  ## Sends the local file to the node, which may be another machine.
driver.get("https://www.selenium.dev/selenium/web/upload.html")
upload = driver.find_element(By.ID, "upload")
upload.send_keys(path)
print("attached:", driver.execute_script("return arguments[0].files[0].name", upload))  ## The browser on the node has the file.
driver.quit()
''', js=r'''
const fs = require('fs');
const os = require('os');
const path = require('path');
const { Builder, Browser, By } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const remote = require('selenium-webdriver/remote');

(async function onTheGrid() {
  const options = new chrome.Options();  ## Options say which browser you want. The Grid picks a node that has it.
  options.set('se:name', 'upload on the grid');  ## se: capabilities are Grid metadata. se:name shows in the Grid UI.
  const driver = await new Builder().forBrowser(Browser.CHROME).setChromeOptions(options).usingServer('http://localhost:4444').build();  ## The only change from a local test: a server URL.
  const caps = await driver.getCapabilities();
  const id = (await driver.getSession()).getId();
  for (const k of ['browserName', 'platformName', 'se:name', 'se:cdp']) {
    const v = caps.get(k);
    console.log(k + ': ' + (k === 'se:cdp' ? v.replace(id, '{id}') : v));  ## se:cdp is a DevTools address that goes through the Grid.
  }
  const file = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'up-')), 'report.txt');
  fs.writeFileSync(file, 'hello grid');
  driver.setFileDetector(new remote.FileDetector());  ## Sends the local file to the node, which may be another machine.
  await driver.get('https://www.selenium.dev/selenium/web/upload.html');
  const upload = await driver.findElement(By.id('upload'));
  await upload.sendKeys(file);
  console.log('attached: ' + await driver.executeScript('return arguments[0].files[0].name', upload));  ## The browser on the node has the file.
  await driver.quit();
})();
''', needs='grid', expect='se:name: upload on the grid')

QUEUE = tri('queue', 'Three tests, two slots: watch the queue', java=r'''
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.remote.RemoteWebDriver;

public class Queue {
    public static void main(String[] args) throws Exception {
        long t0 = System.currentTimeMillis();
        ExecutorService pool = Executors.newFixedThreadPool(3);  ## Three threads, so three tests start at the same moment.
        List<Future<String>> results = new ArrayList<>();
        for (int i = 1; i <= 3; i++) {
            int n = i;
            results.add(pool.submit(() -> {
                RemoteWebDriver driver = new RemoteWebDriver(new URL("http://localhost:4444"), new ChromeOptions());  ## Returns when the Grid has given this test a slot.
                long got = Math.round((System.currentTimeMillis() - t0) / 1000.0);
                Thread.sleep(3000);  ## Pretend the test takes 3 seconds.
                driver.quit();  ## Frees the slot for the next request in the queue.
                return got + " s";
            }));
        }
        List<String> times = new ArrayList<>();
        for (Future<String> f : results) times.add(f.get());
        pool.shutdown();
        times.sort(null);
        System.out.println("got a browser after: " + times);  ## Two at once, the third only after a slot was free.
    }
}
''', py=r'''
import time
from concurrent.futures import ThreadPoolExecutor

from selenium import webdriver

t0 = time.time()


def one_test(n):
    driver = webdriver.Remote("http://localhost:4444", options=webdriver.ChromeOptions())  ## Returns when the Grid has given this test a slot.
    got = round(time.time() - t0)
    time.sleep(3)  ## Pretend the test takes 3 seconds.
    driver.quit()  ## Frees the slot for the next request in the queue.
    return got


with ThreadPoolExecutor(max_workers=3) as pool:  ## Three threads, so three tests start at the same moment.
    times = sorted(pool.map(one_test, [1, 2, 3]))
print("got a browser after:", [f"{t} s" for t in times])  ## Two at once, the third only after a slot was free.
''', js=r'''
const { Builder, Browser } = require('selenium-webdriver');

const t0 = Date.now();
async function oneTest() {
  const driver = await new Builder().forBrowser(Browser.CHROME).usingServer('http://localhost:4444').build();  ## Resolves when the Grid has given this test a slot.
  const got = Math.round((Date.now() - t0) / 1000);
  await new Promise(r => setTimeout(r, 3000));  ## Pretend the test takes 3 seconds.
  await driver.quit();  ## Frees the slot for the next request in the queue.
  return got;
}

(async function queue() {
  const times = (await Promise.all([oneTest(), oneTest(), oneTest()])).sort((a, b) => a - b);  ## Three tests start at the same moment.
  console.log('got a browser after: ' + JSON.stringify(times.map(t => t + ' s')));  ## Two at once, the third only after a slot was free.
})();
''', needs='grid', expect='got a browser after')

K.lesson('why', 'When and why to use a Grid', f'''
<p>So far every test started a browser on the same machine. <b>Selenium Grid</b> lets the same tests run on other machines, called <b>nodes</b>, many at the same time. The documentation names two reasons to use it: run tests in parallel against different browsers, versions and operating systems, and cut the time a suite takes.</p>
{fx('Suite time on a Grid', 'total time = ' + frac('number of tests × average test time', 'number of nodes'), 'From the documentation: 15 tests of 45 s take 11 min 15 s on one node, 2 min 15 s on 5 nodes and 45 s on 15 nodes.', key=True)}
{viz('se-grid')}
<p>For a test, the Grid looks like one big remote driver. The test sends the same W3C requests as before, only to <code>http://localhost:4444</code> or wherever the Grid runs. The Grid finds a node with a free slot for the requested browser, starts the session there, and passes every later command to that node.</p>
{STATUS}
<p>This Grid runs in <b>standalone</b> mode with <code>--max-sessions 2</code>. Its single node offered two slots each for Chrome, Firefox and Edge, but at most two sessions can run at the same time.</p>
{scene('Black Friday regression', '<p>A shop has 600 browser tests of about 40 seconds. On one machine the run takes 6 hours 40 minutes, too long to run before every release. On a Grid of 20 small nodes it takes about 20 minutes, so the team runs it on every merge, in Chrome, Firefox and Edge.</p>')}
''', kw=['selenium grid', 'grid 4', 'node', 'parallel', 'remote', 'status', 'slots', 'standalone', 'execution time'])

K.lesson('components', 'Components, roles and ports', f'''
<p>Grid 4 is built from six components. In a small Grid they all run in one process. In a large one each runs on its own machine. The documentation describes them like this:</p>
{table(['Component', 'Job', 'Default port'], [
    ['Router', 'Entry point for every request. New sessions go to the queue. Commands for existing sessions go straight to the right node, found through the Session Map', '4444'],
    ['New Session Queue', 'Holds new session requests in first in, first out order, with a timeout', '5559'],
    ['Distributor', 'Knows every node and its slots. Takes requests from the queue, finds a matching free slot and creates the session', '5553'],
    ['Session Map', 'Remembers which node runs which session id', '5556'],
    ['Node', 'Runs the browsers. By default one slot per CPU for Chromium browsers and Firefox, one for Safari', '5555'],
    ['Event Bus', 'Messages between the other components, cheaper than HTTP. Started first in a distributed Grid', '4442, 4443 and 5557']])}
{table(['Role', 'Command', 'Use it for'], [
    ['Standalone', '<code>java -jar selenium-server-&lt;version&gt;.jar standalone</code>', 'All components in one process on one machine. Local debugging, quick suites, CI'],
    ['Hub and Node', '<code>... hub</code> and <code>... node --hub http://&lt;hub-ip&gt;:4444</code>', 'The most used role. Combine machines with different systems and browsers behind one address'],
    ['Distributed', '<code>... event-bus</code>, <code>sessionqueue</code>, <code>sessions</code>, <code>distributor</code>, <code>router</code>, <code>node</code>', 'Large Grids with more than 100 nodes, each component scaled on its own']])}
{note('A node registers by sending a message on the Event Bus, and the Distributor then calls it over HTTP to confirm. When hub and node are on different machines, the Event Bus ports 4442 and 4443 and the node port must be reachable.', 'tip')}
{QUEUE}
<p>The Grid only had two free slots for three tests. Two got a browser straight away. The third waited in the New Session Queue until a test called quit and freed a slot. This is why every test must quit its session, pass or fail: a session left open keeps its slot until the session timeout, 300 seconds on this node.</p>
''', kw=['router', 'distributor', 'session map', 'new session queue', 'event bus', 'node', 'hub', 'standalone', 'distributed', 'ports', '4444', 'queue'])

K.lesson('remote', 'Remote sessions, metadata and files', f'''
<p>Moving a test to the Grid changes one line: the driver is created with the Grid address instead of a local browser. Options still choose the browser and its settings. Capabilities that start with <code>se:</code> are Grid metadata. <code>se:name</code> shows the test name in the Grid UI instead of the session id.</p>
{REMOTE}
<p>Two capabilities came back from the Grid that a local driver does not return. <code>se:name</code> echoes the metadata. <code>se:cdp</code> is a DevTools address that runs through the Grid itself, so tools that need DevTools work even when the browser is on another machine. Chapter 6.2 uses it.</p>
<p>The <b>file detector</b> matters as soon as the node is another machine. sendKeys with a path on your laptop means nothing to a node in a data centre. With a local file detector the binding zips the file, sends it to the node, and types the path of the copy. On this Grid the node was the same machine, so it would also have worked without it. On a real Grid it would not.</p>
{table(['Language', 'Remote driver', 'File detector'], [
    ['Java', '<code>new RemoteWebDriver(new URL(gridUrl), options)</code>', '<code>setFileDetector(new LocalFileDetector())</code>'],
    ['Python', '<code>webdriver.Remote(gridUrl, options=options)</code>', '<code>driver.file_detector = LocalFileDetector()</code>'],
    ['JavaScript', '<code>new Builder().usingServer(gridUrl)</code>', '<code>setFileDetector(new remote.FileDetector())</code>']])}
{ladder(
    '<p>A Grid runs your tests on other machines, many at once. Your test only changes the address it connects to.</p>',
    '<p>The Router takes requests, the queue holds new ones, the Distributor finds a free slot on a node and the Session Map remembers where each session runs. Standalone, hub and node, or distributed decide how the components are deployed.</p>',
    '<p>Slots are matched by capabilities. A request waits in the queue until a slot is free or the queue timeout passes. se: capabilities carry metadata, and se:cdp exposes DevTools through the Router.</p>',
    '<p>The documentation recommends many small nodes over one large one, about one CPU and 1 GB of RAM per browser, and Docker for isolation. Large Grids use the distributed role, with GraphQL and observability from chapter 6.2.</p>')}
''', kw=['remote webdriver', 'remote', 'se:name', 'metadata', 'se:cdp', 'file detector', 'local file detector', 'upload', 'capabilities'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What are the two reasons the documentation gives for using a Grid?', ['Prettier reports and fewer locators', 'Parallel runs on different browsers and systems, and shorter suite time', 'Faster page loads and fewer waits', 'Recording tests'], 1,
       'When would you use a Grid.', 'Run in parallel across browsers, versions and systems, and reduce suite time.')
K.quiz('e', 'Which component is the entry point of the Grid?', ['Node', 'Router', 'Event Bus', 'Session Map'], 1,
       'It routes.', 'The Router receives every external request.')
K.quiz('e', 'What changes in a test that moves to the Grid?', ['Every locator', 'The driver is created with the Grid URL', 'The assertions', 'Nothing at all'], 1,
       'One line.', 'Only the driver creation changes, from local to remote.')
K.quiz('m', 'A command for an existing session reaches the Router. Where does it go?', ['To the New Session Queue', 'Straight to the node, found through the Session Map', 'To every node', 'To the Event Bus'], 1,
       'Existing session.', 'The Router asks the Session Map for the node and forwards the command there.')
K.quiz('m', 'Three tests ask for a browser and two slots are free. What happens to the third?', ['It fails at once', 'It waits in the New Session Queue until a slot frees or it times out', 'It runs on the hub', 'It shares a browser'], 1,
       'Look at the queue run.', 'It waited until a test quit and freed a slot.')
K.quiz('m', 'What does se:name do?', ['Renames the browser', 'Shows the test name in the Grid UI', 'Sets the window title', 'Chooses a node'], 1,
       'Metadata.', 'se: capabilities are metadata, and se:name shows in the Grid UI.')
K.quiz('m', 'Why set a local file detector on a remote driver?', ['To find files faster', 'So the file is sent to the node, which may be another machine', 'To check file types', 'Uploads need it locally too'], 1,
       'Your laptop path means nothing on the node.', 'The binding sends the file to the node and types the path of the copy.')
K.quiz('h', 'Which Event Bus ports must be reachable when hub and nodes are on different machines?', ['4444 and 5555', '4442 and 4443', '5556 and 5559', '80 and 443'], 1,
       'Publish and subscribe.', 'The Event Bus uses 4442 and 4443 by default.')
K.quiz('h', 'A test forgets to quit on a busy Grid. What does it cost?', ['Nothing', 'Its slot stays busy until the session timeout, so others queue', 'The node restarts', 'The Router stops'], 1,
       'Slots are shared.', 'The slot stays taken until the session timeout, 300 s on this node.')
K.quiz('x', 'The documentation compares one 32 CPU node with 32 small nodes. Which does it prefer, and why?', ['One big node, it is faster', '32 small nodes, so a failure is isolated', 'Either, it does not matter', 'One big node, Docker needs it'], 1,
       'Isolation.', 'Many small nodes isolate failures, and Docker helps achieve that.')

# ---------------------------------------------------------------- worked problems
K.calc('e', '15 tests of 45 s run on 5 nodes. How long does the suite take, in seconds?', '135', 'Use the formula.',
       ['15 × 45 = 675 s of tests.', 'Divide by 5 nodes.', eq('675 ÷ 5 = 135 s, which is 2 min 15 s')], check=135, unit='s')
K.calc('e', '100 tests of 120 s run on 15 nodes. How many minutes does the suite take?', '13.33', 'Seconds first.',
       ['100 × 120 = 12,000 s.', '12,000 ÷ 15 = 800 s.', eq('800 ÷ 60 ≈ 13.33 min, 13 min 20 s')], check=13.33, unit='min')
K.calc('m', 'A node machine has 8 CPUs. How many Chrome sessions can it run at once by default?', '8', 'One per CPU.',
       ['The node creates one slot per CPU for Chromium browsers.', '8 CPUs.', eq('8 sessions')], check=8)
K.calc('m', 'Each browser session needs about 1 GB of RAM. How many GB does a node with 8 busy Chrome slots need, at least?', '8', 'Per browser.',
       ['About 1 GB per session.', '8 sessions.', eq('8 GB, plus the system itself')], check=8, unit='GB')
K.calc('h', 'A Grid has 2 slots. 3 tests of 3 s start together. When does the last one finish, in seconds?', '6', 'Two rounds.',
       ['Tests 1 and 2 run from 0 to 3 s.', 'Test 3 waits for a slot and runs from 3 to 6 s.', eq('6 s, plus session start times')], check=6, unit='s')
K.calc('x', '600 tests of 40 s must finish in 20 minutes. How many nodes with one slot each are needed, at least?', '20', 'Rearrange the formula.',
       ['Total test time: 600 × 40 = 24,000 s.', '20 minutes is 1,200 s.', eq('24,000 ÷ 1,200 = 20 nodes')], check=20)

# ---------------------------------------------------------------- assignments
K.assign('suitetime', 'e', 'Suite time on a Grid',
         '<p>Write <code>suite_seconds(tests, avg_seconds, nodes)</code> with the formula from the documentation: tests times average time divided by nodes. Return a whole number of seconds, rounded up, because a half finished test still takes its time.</p>',
         '''
import math


def suite_seconds(tests, avg_seconds, nodes):
    # your code here
    pass
''', [('suite_seconds(15, 45, 1)', 675), ('suite_seconds(15, 45, 5)', 135), ('suite_seconds(100, 120, 15)', 800), ('suite_seconds(10, 7, 3)', 24)],
         '''
import math


def suite_seconds(tests, avg_seconds, nodes):
    return math.ceil(tests * avg_seconds / nodes)
''', 'math.ceil rounds up.', '<p>Real suites add session start time and queue waiting, so the formula is a lower bound.</p>')
K.assign('slots', 'm', 'Who gets a slot?',
         '<p>Write <code>start_times(requests, slots, duration)</code>. <code>requests</code> tests ask for a browser at time 0, the Grid has <code>slots</code> slots, and every test takes <code>duration</code> seconds. Return the sorted list of times at which each test gets a browser, ignoring start up time.</p>',
         '''
def start_times(requests, slots, duration):
    # your code here
    pass
''', [('start_times(3, 2, 3)', [0, 0, 3]), ('start_times(4, 2, 5)', [0, 0, 5, 5]), ('start_times(2, 4, 10)', [0, 0])],
         '''
def start_times(requests, slots, duration):
    return sorted((i // slots) * duration for i in range(requests))
''', 'Test number i starts in round i // slots.', '<p>The queue run on this page printed 1, 1 and 4 seconds in Python and JavaScript, and 2, 2 and 5 in Java, because a real session takes time to start. The third test still got its browser one test length after the first two.</p>')

K.must('Why a Grid', 'Parallel runs on many browsers, versions and systems, and shorter suites: tests × average time ÷ nodes.')
K.must('Components', 'Router (4444), New Session Queue, Distributor, Session Map, Node (5555) and Event Bus (4442, 4443).')
K.must('Roles', 'Standalone for one machine, Hub and Node for most Grids, Distributed for very large ones.')
K.must('Remote driver', 'Only the driver creation changes. se:name adds metadata, se:cdp gives DevTools through the Grid, and a local file detector sends upload files to the node.')
K.must('Queue and quit', 'New sessions wait in the queue for a free slot. Always quit, or the slot stays busy until the session timeout.')

T = K.topic(
    slug='grid', topic='grid',
    step=(6, 'Scale out with Grid', 'se-scale', 'Selenium Grid 4: components, roles, remote sessions and parallel runs, then BiDi, CDP and Grid features.', 'Advanced'),
    title='Selenium Grid 4', short='Selenium Grid', badge='6.1', minutes=55, added='2026-10-29',
    lead='Run the same tests on other machines and many at once: the six Grid components, the standalone, hub and node and distributed roles, remote sessions with metadata and file uploads, and the session queue, all from real runs against a Grid.',
    desc='When to use a Grid with the suite time formula, an animation of a request travelling through Router, queue, Distributor, Session Map and node, a real /status reply, components and default ports, roles and their commands, a remote session with se:name, se:cdp and a file detector, and three tests competing for two slots, in Java, Python and JavaScript.',
    summary='Selenium Grid 4 components, roles, remote sessions and parallel runs.',
    keywords=['selenium grid', 'grid 4', 'remote webdriver', 'router', 'distributor', 'node', 'hub', 'standalone', 'parallel', 'se:name', 'file detector'],
    recap='<p>A Grid runs tests on nodes, many at once. The Router takes every request, new sessions wait in the queue until the Distributor finds a free slot, and the Session Map remembers which node runs which session. A test only changes its driver creation. Use se:name for metadata, a file detector for uploads, and always quit to free the slot.</p>')
