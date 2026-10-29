# Chapter 1.2: architecture and the W3C WebDriver protocol. Sources: selenium.dev documentation (Components,
# WebDriver, Getting started, Drivers, BiDi, Upgrade to Selenium 4, Errors), the W3C WebDriver specification
# (local end, remote end, intermediary and endpoint nodes, endpoint table, error table with HTTP statuses), the
# Selenium Python binding source (locator_converter.py turns id and name into CSS selectors, the element key), and
# real logs and raw HTTP runs against chromedriver 153 recorded when the page was built.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from sekit import tri, solo, shell, flow

K = Kit()

RAW = tri('rawhttp', 'Drive Chrome with plain HTTP and no Selenium library at all', java=r'''
import java.net.URI;  ## URI turns a text address into an address object the HTTP client accepts.
import java.net.http.HttpClient;  ## The HTTP client built into Java 11 and later.
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class RawWebDriver {
    static HttpClient http = HttpClient.newHttpClient();  ## One HTTP client, reused for every command.

    static String call(String method, String path, String body) throws Exception {  ## Send one W3C command and return the JSON answer as text.
        HttpRequest.Builder req = HttpRequest.newBuilder(URI.create("http://localhost:9515" + path))  ## chromedriver listens on port 9515 unless told otherwise.
            .header("Content-Type", "application/json");  ## The protocol speaks JSON in both directions.
        req.method(method, body == null ? HttpRequest.BodyPublishers.noBody() : HttpRequest.BodyPublishers.ofString(body));  ## GET and DELETE carry no body. POST carries a JSON object.
        String reply = http.send(req.build(), HttpResponse.BodyHandlers.ofString()).body();  ## Send it and wait for the answer.
        System.out.println(method + " " + path + "  ->  " + (reply.length() > 70 ? reply.substring(0, 70) + "..." : reply));  ## Print the request and the start of the answer.
        return reply;
    }

    static String value(String json, String key) {  ## A tiny helper that pulls one string out of the JSON answer.
        return json.replaceAll("(?s).*\"" + key + "\":\"([^\"]+)\".*", "$1");
    }

    public static void main(String[] args) throws Exception {
        Process driver = new ProcessBuilder("chromedriver", "--port=9515").start();  ## Start the driver program yourself, the job Selenium usually does for you.
        Thread.sleep(1000);  ## Give chromedriver a moment to open its port.
        String created = call("POST", "/session", "{\"capabilities\":{\"alwaysMatch\":{\"browserName\":\"chrome\"}}}");  ## New Session. Chrome opens.
        String s = "/session/" + value(created, "sessionId");  ## Every later command names this session in its path.
        call("POST", s + "/timeouts", "{\"implicit\":2000}");  ## Set Timeouts: let Find Element keep looking for up to 2 seconds, so the next page has time to load.
        call("POST", s + "/url", "{\"url\":\"https://www.selenium.dev/selenium/web/web-form.html\"}");  ## Navigate To.
        call("GET", s + "/title", null);  ## Get Title.
        String box = value(call("POST", s + "/element", "{\"using\":\"css selector\",\"value\":\"[name='my-text']\"}"), "element-6066-11e4-a52e-4f735466cecf");  ## Find Element returns a reference under this fixed key.
        call("POST", s + "/element/" + box + "/value", "{\"text\":\"Selenium\"}");  ## Element Send Keys types into that element.
        String button = value(call("POST", s + "/element", "{\"using\":\"css selector\",\"value\":\"button\"}"), "element-6066-11e4-a52e-4f735466cecf");
        call("POST", s + "/element/" + button + "/click", "{}");  ## Element Click submits the form.
        String message = value(call("POST", s + "/element", "{\"using\":\"css selector\",\"value\":\"#message\"}"), "element-6066-11e4-a52e-4f735466cecf");
        call("GET", s + "/element/" + message + "/text", null);  ## Get Element Text on the next page.
        call("DELETE", s, null);  ## Delete Session closes Chrome.
        driver.destroy();  ## Stop chromedriver.
    }
}
''', py=r'''
import json  ## For turning Python dictionaries into JSON text and back.
import subprocess  ## For starting the chromedriver program.
import time
import urllib.request  ## Python's built in HTTP client. No Selenium library is imported anywhere.

driver = subprocess.Popen(["chromedriver", "--port=9515"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  ## Start the driver yourself, the job Selenium usually does for you. Its own messages are hidden.
time.sleep(1)  ## Give it a moment to open port 9515.

def call(method, path, body=None):  ## Send one W3C command and return the part of the answer under "value".
    data = json.dumps(body).encode() if body is not None else None  ## POST bodies are JSON objects. GET and DELETE have none.
    req = urllib.request.Request("http://localhost:9515" + path, data=data, method=method, headers={"Content-Type": "application/json"})
    reply = json.load(urllib.request.urlopen(req))  ## Send it and read the JSON answer.
    text = json.dumps(reply)
    print(method, path, " -> ", text[:70] + ("..." if len(text) > 70 else ""))  ## Print the request and the start of the answer.
    return reply["value"]  ## Every success answer keeps its result under "value".

KEY = "element-6066-11e4-a52e-4f735466cecf"  ## The fixed key the W3C spec uses for element references.
s = "/session/" + call("POST", "/session", {"capabilities": {"alwaysMatch": {"browserName": "chrome"}}})["sessionId"]  ## New Session. Chrome opens and we keep the session path.
call("POST", s + "/timeouts", {"implicit": 2000})  ## Set Timeouts: Find Element may keep looking for 2 seconds, so the next page has time to load.
call("POST", s + "/url", {"url": "https://www.selenium.dev/selenium/web/web-form.html"})  ## Navigate To.
call("GET", s + "/title")  ## Get Title.
box = call("POST", s + "/element", {"using": "css selector", "value": "[name='my-text']"})[KEY]  ## Find Element.
call("POST", s + "/element/" + box + "/value", {"text": "Selenium"})  ## Element Send Keys.
button = call("POST", s + "/element", {"using": "css selector", "value": "button"})[KEY]
call("POST", s + "/element/" + button + "/click", {})  ## Element Click submits the form.
message = call("POST", s + "/element", {"using": "css selector", "value": "#message"})[KEY]
call("GET", s + "/element/" + message + "/text")  ## Get Element Text on the next page.
call("DELETE", s)  ## Delete Session closes Chrome.
driver.terminate()  ## Stop chromedriver.
''', js=r'''
const { spawn } = require('child_process');  ## For starting the chromedriver program. No Selenium package is loaded.

async function call(method, path, body) {  ## Send one W3C command and return the part of the answer under "value".
  const res = await fetch('http://localhost:9515' + path, {  ## fetch is built into Node.js 18 and later.
    method, headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),  ## POST bodies are JSON objects. GET and DELETE have none.
  });
  const reply = await res.json();
  const text = JSON.stringify(reply);
  console.log(method, path, ' -> ', text.length > 70 ? text.slice(0, 70) + '...' : text);  ## Print the request and the start of the answer.
  return reply.value;
}

(async () => {
  const driver = spawn('chromedriver', ['--port=9515'], { stdio: 'ignore' });  ## Start the driver yourself and hide its own messages.
  await new Promise(r => setTimeout(r, 1000));  ## Give it a moment to open its port.
  const KEY = 'element-6066-11e4-a52e-4f735466cecf';  ## The fixed key for element references.
  const s = '/session/' + (await call('POST', '/session', { capabilities: { alwaysMatch: { browserName: 'chrome' } } })).sessionId;  ## New Session.
  await call('POST', s + '/timeouts', { implicit: 2000 });  ## Set Timeouts: Find Element may keep looking for 2 seconds while the next page loads.
  await call('POST', s + '/url', { url: 'https://www.selenium.dev/selenium/web/web-form.html' });  ## Navigate To.
  await call('GET', s + '/title');  ## Get Title.
  const box = (await call('POST', s + '/element', { using: 'css selector', value: "[name='my-text']" }))[KEY];  ## Find Element.
  await call('POST', s + '/element/' + box + '/value', { text: 'Selenium' });  ## Element Send Keys.
  const button = (await call('POST', s + '/element', { using: 'css selector', value: 'button' }))[KEY];
  await call('POST', s + '/element/' + button + '/click', {});  ## Element Click.
  const message = (await call('POST', s + '/element', { using: 'css selector', value: '#message' }))[KEY];
  await call('GET', s + '/element/' + message + '/text');  ## Get Element Text.
  await call('DELETE', s);  ## Delete Session.
  driver.kill();  ## Stop chromedriver.
})();
''', expect='"Received!"')

WIRELOG = solo('wirelog', 'Watch the real requests a normal Selenium script sends', 'py', r'''
import logging  ## Python's standard logging module.
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.DEBUG, format="%(message)s", stream=sys.stdout)  ## Print DEBUG messages, which include every HTTP request the binding sends.
for name in ("urllib3", "selenium.webdriver.common"):  ## Hide two noisy loggers so only the protocol messages remain.
    logging.getLogger(name).setLevel(logging.WARNING)

driver = webdriver.Chrome()  ## POST /session
driver.get("https://www.selenium.dev/selenium/web/web-form.html")  ## POST /session/{id}/url
box = driver.find_element(By.NAME, "my-text")  ## POST /session/{id}/element. Watch how By.NAME becomes a CSS selector.
box.send_keys("Hi")  ## POST /session/{id}/element/{element id}/value
print("title is", driver.title)  ## GET /session/{id}/title
driver.quit()  ## DELETE /session/{id}
''', why='Python is used here because its logging prints each request on one line. Java (java.util.logging at FINE for org.openqa.selenium.remote) and JavaScript (the webdriver.http logger) can show the same traffic.', expect='title is Web form')

K.lesson('pieces', 'The pieces between your code and the browser', f'''
<p>When you call <code>click()</code>, your code does not reach into Chrome and press the button. A message travels through three separate programs. Knowing them makes every error message later in this subject easy to read.</p>
{flow(('Your test', 'Java, Python or JavaScript code that calls the Selenium API.'), ('Language binding', 'The Selenium library. The W3C spec calls it the local end.'), ('Driver', 'chromedriver, geckodriver, msedgedriver or safaridriver. The remote end.'), ('Browser', 'Does the real work and reports back.'))}
<p>The Selenium documentation describes the driver as the component responsible for delegating down to the browser, and handling communication to and from Selenium and the browser. That split is deliberate: browser vendors take responsibility for driving their own browser, and Selenium ties all the drivers together behind one interface.</p>
{viz('se-wire')}
{table(['Spec word', 'In practice', 'Example'], [
    ['Local end', 'The client side, usually a language library on top of the protocol', 'selenium for Python, selenium-java, selenium-webdriver for npm'],
    ['Remote end', 'The server side that carries out the commands', 'chromedriver, or Selenium Grid'],
    ['Intermediary node', 'A remote end that passes commands on to another remote end', 'Selenium Grid, which forwards to a node'],
    ['Endpoint node', 'The last remote end in the chain, built into or next to the browser', 'chromedriver driving Chrome']])}
{scene('ordering in a restaurant', '<p>You tell the waiter "one masala dosa". The waiter writes it on a slip in a fixed format the kitchen understands, the kitchen cooks, and the waiter brings the plate back. You never enter the kitchen. Your code is the customer, the binding writes the slip, the driver is the kitchen pass that hands orders to the cook, and the browser is the cook. Whatever language you speak to the waiter, the slip looks the same.</p>')}
''', kw=['architecture', 'local end', 'remote end', 'language binding', 'driver', 'chromedriver', 'geckodriver', 'intermediary node', 'endpoint node', 'client server'])

K.lesson('protocol', 'The W3C WebDriver protocol', f'''
<p>The messages between the binding and the driver follow the W3C WebDriver specification. It is a plain HTTP protocol: each command is one HTTP request, and each answer is one HTTP response with a JSON body.</p>
{table(['Command', 'Method', 'Path', 'What you write in Python'], [
    ['New Session', 'POST', '/session', '<code>webdriver.Chrome()</code>'],
    ['Delete Session', 'DELETE', '/session/{session id}', '<code>driver.quit()</code>'],
    ['Navigate To', 'POST', '/session/{id}/url', '<code>driver.get(url)</code>'],
    ['Get Title', 'GET', '/session/{id}/title', '<code>driver.title</code>'],
    ['Find Element', 'POST', '/session/{id}/element', '<code>driver.find_element(...)</code>'],
    ['Find Elements', 'POST', '/session/{id}/elements', '<code>driver.find_elements(...)</code>'],
    ['Element Click', 'POST', '/session/{id}/element/{element id}/click', '<code>element.click()</code>'],
    ['Element Send Keys', 'POST', '/session/{id}/element/{element id}/value', '<code>element.send_keys(...)</code>'],
    ['Get Element Text', 'GET', '/session/{id}/element/{element id}/text', '<code>element.text</code>'],
    ['Set Timeouts', 'POST', '/session/{id}/timeouts', '<code>driver.implicitly_wait(2)</code>'],
    ['Execute Script', 'POST', '/session/{id}/execute/sync', '<code>driver.execute_script(...)</code>'],
    ['Take Screenshot', 'GET', '/session/{id}/screenshot', '<code>driver.get_screenshot_as_png()</code>']])}
<h3>The shape of every answer</h3>
{fxs(
    fx('Success', 'HTTP 200 and {"value": result}', 'The result is null for commands that only act, a string for text and titles, a list for Find Elements.', key=True),
    fx('Error', 'HTTP 4xx or 5xx and {"value": {"error", "message", "stacktrace"}}', 'error is a fixed code such as no such element. The binding turns it into an exception.', key=True),
    fx('Element reference', '{"element-6066-11e4-a52e-4f735466cecf": "f.C6…e.6"}', 'A web element travels as an object with this one fixed key. The value is an opaque id made by the driver.'))}
{table(['Error code', 'HTTP status', 'Python exception you see'], [
    ['no such element', '404', 'NoSuchElementException'],
    ['stale element reference', '404', 'StaleElementReferenceException'],
    ['invalid session id', '404', 'InvalidSessionIdException'],
    ['element not interactable', '400', 'ElementNotInteractableException'],
    ['element click intercepted', '400', 'ElementClickInterceptedException'],
    ['invalid selector', '400', 'InvalidSelectorException'],
    ['timeout', '500', 'TimeoutException'],
    ['unexpected alert open', '500', 'UnexpectedAlertPresentException'],
    ['session not created', '500', 'SessionNotCreatedException']])}
{note('The binding changes some locators before they leave your machine. The Python binding sends By.ID "x" as the CSS selector [id="x"], By.NAME as [name="x"] and By.CLASS_NAME as .x. Look for it in the log in the next lesson. That is why the W3C spec only needs five strategies: css selector, link text, partial link text, tag name and xpath.', 'tip')}
{steps('Read one real request from the log', [
    'The binding sent <code>POST http://localhost:PORT/session/a443…/element</code>.',
    'Its body was <code>{"using": "css selector", "value": "[name="my-text"]"}</code>, made from <code>By.NAME, "my-text"</code>.',
    'chromedriver answered 200 with <code>{"value": {"element-6066-11e4-a52e-4f735466cecf": "f.C6C4…e.6"}}</code>.',
    'The binding wrapped that id in a WebElement object, so later calls such as send_keys know which element to name in their path.'])}
''', kw=['W3C WebDriver', 'protocol', 'HTTP', 'JSON', 'endpoint', 'session id', 'element reference', 'element-6066-11e4-a52e-4f735466cecf', 'error codes', 'HTTP status'])

K.lesson('wire', 'See the wire for yourself', f'''
<p>The best way to believe the protocol is simple is to drive Chrome without Selenium. The programs below start chromedriver, then send it the same requests a binding would, with nothing but the HTTP client of each language. They fill the web form and read the message on the next page. The output is what chromedriver really answered.</p>
{RAW}
<p>Every request gets an answer that starts with <code>{{"value":</code>. Without the Set Timeouts line, Find Element can run before the next page has loaded and answer no such element, which is the first taste of the waiting problem in chapter 4.1. The session id and element ids are random, so your run will show different ones.</p>
<h3>The same traffic from a normal script</h3>
<p>A real Selenium script sends exactly these requests for you. Turning on debug logging shows them. Note how <code>By.NAME</code> leaves your machine as a CSS selector.</p>
{WIRELOG}
{note('You will never write raw HTTP in real tests. The point is to see that nothing magic happens: Selenium is a polite HTTP client with good manners about waiting, errors and types. When a test fails with a strange message, picture the request that was sent and the error code that came back.', 'tip')}
{deep('How chromedriver controls Chrome', '<p>The W3C spec only defines the HTTP side. How a driver controls its browser is up to the vendor. In the logged answer to New Session you can see <code>goog:chromeOptions</code> with a <code>debuggerAddress</code>: chromedriver connects to Chrome through its DevTools port. geckodriver uses the remote protocol built into Firefox, and safaridriver is built into macOS. This is why a driver version must match its browser: the inner protocol changes with each browser release.</p>')}
''', kw=['raw HTTP', 'chromedriver port 9515', 'curl', 'fetch', 'urllib', 'HttpClient', 'logging', 'debug log', 'wire log', 'debuggerAddress'])

K.lesson('remote', 'Local, remote and Grid, plus BiDi', f'''
<p>The documentation shows three ways the pieces can be arranged. The protocol is the same in all of them, which is why moving a test from your laptop to a Grid changes one line.</p>
{table(['Layout', 'Where things run', 'Code difference'], [
    ['Direct', 'Your code, the driver and the browser on one machine.', '<code>new ChromeDriver()</code>, <code>webdriver.Chrome()</code>'],
    ['Remote', 'Your code on one machine, driver and browser on another, reached through Selenium Server or RemoteWebDriver.', '<code>new RemoteWebDriver(url, options)</code>, <code>webdriver.Remote(url, options=...)</code>'],
    ['Grid', 'Selenium Grid receives the commands and relays them to the driver on a node machine.', 'Same as remote, the URL points at the Grid']])}
<h3>Why a second protocol, WebDriver BiDi?</h3>
<p>Classic WebDriver is request and response: your code asks, the browser answers. The browser cannot start a conversation. That is fine for clicking and reading, but not for "tell me every time the page logs an error" or "tell me about every network request". WebDriver BiDi, a W3C standard made by the Selenium project and the browser vendors, adds a WebSocket connection so the browser can send events as they happen. Before BiDi, Selenium offered these features through the Chrome DevTools Protocol, which the docs call temporary until BiDi is implemented. Chapter 6.2 uses BiDi.</p>
{ladder(
    '<p>Your program sends small written orders to a helper program, and the helper makes the browser do them.</p>',
    '<p>The binding sends HTTP requests with JSON bodies to a driver. Each command has a fixed method and path, and every answer has a value or an error code.</p>',
    '<p>The W3C protocol is stateless HTTP with a session id in the path. Intermediary nodes such as Grid can route by that id without understanding the command. Capabilities in New Session negotiate the browser, version, platform and vendor extensions such as goog:chromeOptions.</p>',
    '<p>BiDi moves automation to an event driven model over WebSocket, with modules such as browsingContext, script, network and log. It lets one client subscribe to browser events across tabs, which classic WebDriver could only approximate by polling.</p>')}
''', kw=['RemoteWebDriver', 'remote', 'Selenium Server', 'Grid', 'WebDriver BiDi', 'WebSocket', 'CDP', 'Chrome DevTools Protocol', 'events'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What does the W3C spec call the language library side of WebDriver?', ['The remote end', 'The local end', 'The endpoint node', 'The browser'], 1,
       'Local means on your side.', 'The binding is the local end. The driver is the remote end.')
K.quiz('e', 'Which HTTP method and path start a new session?', ['GET /session', 'POST /session', 'PUT /browser', 'POST /start'], 1,
       'Creating something new.', 'New Session is POST /session with the capabilities in the JSON body.')
K.quiz('e', 'Where does a success answer keep its result?', ['Under "result"', 'Under "value"', 'In an HTTP header', 'In the status text'], 1,
       'Look at any line of the raw output.', 'Every answer is a JSON object with the key value.')
K.quiz('m', 'What HTTP status does "no such element" use?', ['200', '400', '404', '500'], 2,
       'Something was not found.', 'The spec maps no such element to 404, like stale element reference and invalid session id.')
K.quiz('m', 'The Python binding sends By.ID "lname" as which locator?', ['id "lname"', 'css selector [id="lname"]', 'xpath //*[@id="lname"]', 'name "lname"'], 1,
       'The spec has no id strategy.', 'locator_converter.py turns By.ID into the CSS selector [id="lname"].')
K.quiz('m', 'Which key holds an element reference in the JSON?', ['"element"', '"ELEMENT"', '"element-6066-11e4-a52e-4f735466cecf"', '"id"'], 2,
       'It looks like a fixed id.', 'The W3C spec uses the constant element-6066-11e4-a52e-4f735466cecf.')
K.quiz('m', 'Which command path types into an element?', ['/element/{id}/type', '/element/{id}/value', '/element/{id}/keys', '/keys'], 1,
       'A field holds a value.', 'Element Send Keys is POST /session/{id}/element/{element id}/value.')
K.quiz('h', 'Why can Selenium Grid route commands without understanding them?', ['It reads the page', 'The session id is in every path, so it can look up which node owns the session', 'It asks the test', 'It cannot'], 1,
       'Look at the paths.', 'Every command after New Session names the session in its path. The Grid router maps that id to a node.')
K.quiz('h', 'Why does a chromedriver have to match the Chrome version?', ['License rules', 'The driver controls Chrome through an inner protocol that changes with Chrome releases', 'Speed', 'It does not need to'], 1,
       'The W3C part is stable. What is not?', 'The W3C side is stable, but how chromedriver drives Chrome changes with releases. A mismatch gives session not created.')
K.quiz('x', 'Classic WebDriver cannot push a console error to your test the moment it happens. Why, and what fixes it?', ['HTTP is too slow, use HTTP/2', 'It is request and response only, WebDriver BiDi adds a WebSocket channel for events', 'Browsers hide console errors', 'Use implicit waits'], 1,
       'Who starts each conversation?', 'In classic WebDriver only the client starts a request. BiDi adds a two way WebSocket so the browser can send events.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'The first script fills a field and clicks submit: New Session, Navigate To, Find Element twice, Send Keys, Click, Find Element, Get Element Text, Delete Session. How many HTTP requests is that?', '9', 'Count each command once.',
       ['Session: New Session and Delete Session make 2.', 'Navigation: 1. Three Find Element calls: 3.', 'Send Keys, Click and Get Element Text: 3.', eq('2 + 1 + 3 + 3 = 9 requests')], check=9)
K.calc('e', 'What HTTP status code comes back for "element click intercepted"?', '400', 'It is a client error in the spec table.',
       ['The click could not land on the element because something covered it.', 'The spec lists it with the other bad request style errors.', eq('element click intercepted is HTTP 400')], check=400)
K.calc('m', 'A command reaches chromedriver in 2 ms each way and Chrome needs 6 ms to act. If a test sends 150 commands one after another, how many milliseconds go just on the HTTP trips?', '600', 'Two trips per command.',
       ['Each command makes a request and a response: 2 + 2 = 4 ms on the wire.', 'Chrome time is not part of the question.', eq('150 × 4 = 600 ms')], check=600, unit='ms')
K.calc('m', 'Find Element with By.NAME "q" in Python. What is the exact value string in the JSON body?', '[name="q"]', 'locator_converter.py writes [name="..."].',
       ['By.NAME is not a W3C strategy.', 'The binding switches to css selector.', eq('value = [name="q"]')], check='[name="q"]')
K.calc('h', 'A Grid adds 30 ms each way between the client and the node. A test of 150 commands that took 9 seconds locally now runs through the Grid. How many seconds does it take, if nothing else changes?', '18', 'Extra time = commands × 2 × 30 ms.',
       ['Extra per command: 2 × 30 = 60 ms.', 'For 150 commands: 150 × 60 = 9,000 ms = 9 seconds.', eq('9 + 9 = 18 seconds'), 'This is why a remote Grid should sit close to the test machines on the network.'], check=18, unit='s')
K.calc('x', 'Out of the 9 error codes in the lesson table, how many use HTTP 404?', '3', 'Look for the not found style errors.',
       ['404: no such element, stale element reference, invalid session id.', '400: element not interactable, element click intercepted, invalid selector.', '500: timeout, unexpected alert open, session not created.', eq('3 of the 9 are 404')], check=3)

# ---------------------------------------------------------------- assignments
K.assign('w3cloc', 'm', 'Convert a locator the way the bindings do',
         '<p>Write <code>to_w3c(by, value)</code> that returns the dictionary the Python binding sends for Find Element. Rules from locator_converter.py: <code>"id"</code> becomes css selector <code>[id="value"]</code>, <code>"name"</code> becomes <code>[name="value"]</code>, <code>"class name"</code> becomes <code>.value</code>. Every other strategy is sent unchanged.</p>',
         '''
def to_w3c(by, value):
    # return {"using": ..., "value": ...}
    pass
''', [('to_w3c("id", "lname")', {'using': 'css selector', 'value': '[id="lname"]'}), ('to_w3c("name", "q")', {'using': 'css selector', 'value': '[name="q"]'}),
      ('to_w3c("class name", "information")', {'using': 'css selector', 'value': '.information'}), ('to_w3c("xpath", "//a")', {'using': 'xpath', 'value': '//a'})],
         '''
def to_w3c(by, value):
    if by == "id":
        return {"using": "css selector", "value": '[id="' + value + '"]'}
    if by == "name":
        return {"using": "css selector", "value": '[name="' + value + '"]'}
    if by == "class name":
        return {"using": "css selector", "value": "." + value}
    return {"using": by, "value": value}
''', 'Three special cases, then return the pair as it is.', '<p>The W3C spec defines only five strategies, so the bindings rewrite the three older ones into CSS before sending.</p>')
K.assign('w3cerr', 'h', 'Turn an error answer into an exception name',
         '<p>Write <code>exception_for(status, body)</code>. body is the parsed JSON answer. If status is 200 return <code>"ok"</code>. Otherwise read <code>body["value"]["error"]</code> and return the Python exception name: no such element gives NoSuchElementException, stale element reference gives StaleElementReferenceException, timeout gives TimeoutException, and anything else gives WebDriverException.</p>',
         '''
def exception_for(status, body):
    # your code here
    pass
''', [('exception_for(200, {"value": None})', 'ok'), ('exception_for(404, {"value": {"error": "no such element", "message": "x"}})', 'NoSuchElementException'),
      ('exception_for(404, {"value": {"error": "stale element reference", "message": "x"}})', 'StaleElementReferenceException'),
      ('exception_for(500, {"value": {"error": "timeout", "message": "x"}})', 'TimeoutException'), ('exception_for(500, {"value": {"error": "unknown error", "message": "x"}})', 'WebDriverException')],
         '''
def exception_for(status, body):
    if status == 200:
        return "ok"
    names = {"no such element": "NoSuchElementException",
             "stale element reference": "StaleElementReferenceException",
             "timeout": "TimeoutException"}
    return names.get(body["value"]["error"], "WebDriverException")
''', 'A dictionary from error code to name, with a default.', '<p>This is a tiny version of the error handler inside every binding. The real one maps every code in the spec table.</p>')

K.must('Three programs', 'Your code and the binding (local end), the driver (remote end), the browser. The driver is written by the browser vendor.')
K.must('HTTP and JSON', 'Every command is one HTTP request with a fixed method and path. Answers are {"value": ...} on success or {"value": {"error", "message", "stacktrace"}} on failure.')
K.must('Session id', 'POST /session returns a session id. Every later path contains it. DELETE /session/{id} ends it.')
K.must('Element reference', 'Elements travel as {"element-6066-11e4-a52e-4f735466cecf": "id"}. Bindings turn id, name and class name into CSS selectors.')
K.must('BiDi', 'Classic WebDriver is request and response. WebDriver BiDi adds a WebSocket so the browser can send events. CDP access is temporary until BiDi covers it.')

T = K.topic(
    slug='architecture', topic='architecture',
    step=(1, 'Meet Selenium', 'se-meet', 'What Selenium is, how it talks to a browser through the W3C WebDriver protocol, and your first script in Java, Python and JavaScript.', 'Beginner'),
    title='Architecture and the W3C WebDriver protocol', short='Architecture', badge='1.2', minutes=45, added='2026-10-29',
    lead='Follow one click from your code through the language binding and the driver to the browser and back, then drive Chrome with plain HTTP to see that the protocol is simple.',
    desc='Local end, remote end, intermediary and endpoint nodes, the HTTP and JSON W3C protocol, the endpoint table, success and error answers, the element key, error codes with HTTP status, raw HTTP runs in Java, Python and JavaScript, a real debug log, direct, remote and Grid layouts, and WebDriver BiDi.',
    summary='How a command travels from your code to the browser over the W3C WebDriver protocol, shown with real HTTP traffic.',
    keywords=['architecture', 'w3c webdriver protocol', 'json wire', 'http', 'endpoint', 'session', 'driver', 'chromedriver', 'bidi', 'error codes'],
    recap='<p>Your code calls a binding, the binding sends HTTP requests with JSON bodies to a driver, and the driver controls the browser. Paths name the session and element, answers carry value or an error code, and the binding turns error codes into exceptions. Grid sits in the middle as an intermediary node, and BiDi adds two way events.</p>')
