# Web and APIs 2.1: calling web APIs with requests. Checked against the requests 2.34 documentation (quickstart,
# advanced usage: Session, timeouts, exceptions, authentication), RFC 9110 and the Python 3.14 documentation of json
# and datetime. Every requests program starts a tiny practice API on 127.0.0.1 first, so it needs no internet, and
# shows a real run made when the page was built. The page's Pyodide has no network sockets, so they use local().
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, lc, leet, files, grow, leet_items

chapter('py-requests')
K = Kit()

K.code('first_get', r'''
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import requests

# ---------- A tiny practice API on your own computer, so this file needs no internet ----------
BOOKS = [{"id": 1, "title": "Dune", "year": 1965}, {"id": 2, "title": "Emma", "year": 1815},
         {"id": 3, "title": "Dune Messiah", "year": 1969}]


class PracticeAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlsplit(self.path)
        words = parse_qs(url.query).get("q", [""])[0].lower()
        found = [book for book in BOOKS if words in book["title"].lower()]
        body = json.dumps(found).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), PracticeAPI)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_address[1]}"

# ---------- The part to learn: calling the API with requests ----------
r = requests.get(BASE + "/books", params={"q": "dune messiah", "page": 1}, timeout=5)
print("url:", r.url.replace(BASE, ""))           # params became a query string, the space became +
print("status:", r.status_code, r.reason, "ok:", r.ok)
print("content type:", r.headers["content-type"])  # header names ignore upper and lower case
print("text:", r.text)
books = r.json()                                   # JSON text to Python lists and dicts
print("python:", type(books).__name__, books[0]["title"], books[0]["year"])

r = requests.get(BASE + "/books", params={"q": "dune"}, timeout=5)
for book in r.json():
    print(book["id"], book["title"])
print("we sent the header User-Agent:", r.request.headers["User-Agent"].split("/")[0])
server.shutdown()
''', long=True)
K.code('sending', r'''
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

# ---------- A tiny practice API that answers with what it received ----------
class Echo(BaseHTTPRequestHandler):
    def answer(self):
        length = int(self.headers.get("Content-Length", 0))
        received = {"method": self.command, "path": self.path,
                    "content_type": self.headers.get("Content-Type"),
                    "body": self.rfile.read(length).decode()}
        body = json.dumps(received).encode()
        self.send_response(201 if self.command == "POST" else 200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = answer

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Echo)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_address[1]}"

# ---------- The part to learn: the methods and the three ways to send data ----------
book = {"title": "Emma", "year": 1815}

r = requests.post(BASE + "/books", json=book, timeout=5)        # JSON body
print(r.status_code, r.json())

r = requests.post(BASE + "/login", data={"user": "ann", "pw": "a b"}, timeout=5)    # web form body
print(r.status_code, r.json())

r = requests.get(BASE + "/books", params={"year": 1815}, timeout=5)    # no body, data in the URL
print(r.status_code, r.json())

r = requests.put(BASE + "/books/2", json={"title": "Emma", "year": 1816}, timeout=5)   # replace it all
print(r.json()["method"], r.json()["body"])
r = requests.patch(BASE + "/books/2", json={"year": 1816}, timeout=5)                  # change a part
print(r.json()["method"], r.json()["body"])
r = requests.delete(BASE + "/books/2", timeout=5)
print(r.json()["method"], r.json()["path"], "body:", repr(r.json()["body"]))
server.shutdown()
''', long=True)
K.code('errors', r'''
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

# ---------- A tiny practice API with a missing book, a slow page and a page that is not JSON ----------
class PracticeAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/slow":
            time.sleep(1)
        if self.path == "/html":
            status, kind, body = 200, "text/html", b"<h1>Hello</h1>"
        elif self.path == "/books/1":
            status, kind, body = 200, "application/json", b'{"id": 1, "title": "Dune"}'
        else:
            status, kind, body = 404, "application/json", b'{"error": "not found"}'
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), PracticeAPI)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_address[1]}"

# ---------- The part to learn: every way a call can fail ----------
r = requests.get(BASE + "/books/99", timeout=5)
print("404 is not an exception:", r.status_code, r.ok)
try:
    r.raise_for_status()
except requests.HTTPError as err:
    print("HTTPError:", err.response.status_code, err.response.json())

try:
    requests.get(BASE + "/slow", timeout=0.2)
except requests.Timeout as err:
    print("Timeout:", type(err).__name__)

try:
    requests.get("http://127.0.0.1:9", timeout=2)        # nothing listens on port 9
except requests.ConnectionError as err:
    print("ConnectionError:", type(err).__name__)

try:
    requests.get(BASE + "/html", timeout=5).json()
except requests.JSONDecodeError:
    print("JSONDecodeError: the body is not JSON")


def get_json(url):
    """Return (data, None) when it works, or (None, a short message) when it fails."""
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json(), None
    except requests.HTTPError as err:
        return None, f"server said {err.response.status_code}"
    except requests.JSONDecodeError:                  # must come before RequestException, its parent
        return None, "the answer was not JSON"
    except requests.RequestException as err:         # the parent of all requests errors
        return None, f"network problem: {type(err).__name__}"


for path in ["/books/1", "/books/7", "/html"]:
    print(path, get_json(BASE + path))
print(get_json("http://127.0.0.1:9/books"))
server.shutdown()
''', long=True)
K.code('session_auth', r'''
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

# ---------- A tiny practice API with a login cookie and a token ----------
TOKEN = "secret-token-123"


class PracticeAPI(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"                   # keep the connection open between requests

    def send_json(self, status, data, cookie=None):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):                               # POST /login
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        self.send_json(200, {"logged_in": True}, cookie="session=ann42; HttpOnly")

    def do_GET(self):
        if self.path == "/me" and "session=ann42" in self.headers.get("Cookie", ""):
            self.send_json(200, {"user": "ann", "via": "cookie"})
        elif self.path == "/orders" and self.headers.get("Authorization") == f"Bearer {TOKEN}":
            self.send_json(200, {"orders": [101, 102], "via": "token"})
        elif self.path == "/port":
            self.send_json(200, {"client_port": self.client_address[1]})
        else:
            self.send_json(401, {"error": "please log in"})

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), PracticeAPI)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_address[1]}"

# ---------- The part to learn: Session keeps cookies, headers and the connection ----------
print("without a session:", requests.get(BASE + "/me", timeout=5).status_code)

with requests.Session() as session:
    session.post(BASE + "/login", json={"user": "ann", "pw": "pw"}, timeout=5)
    print("cookies kept:", session.cookies.get_dict())
    print("with the session:", session.get(BASE + "/me", timeout=5).json())

    ports = {session.get(BASE + "/port", timeout=5).json()["client_port"] for _ in range(3)}
    print("3 requests used", len(ports), "connection")

with requests.Session() as api:
    api.headers.update({"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"})
    print("token:", api.get(BASE + "/orders", timeout=5).json())

ports = {requests.get(BASE + "/port", timeout=5).json()["client_port"] for _ in range(3)}
print("3 requests without a session used", len(ports), "connections")
server.shutdown()
''', long=True)
K.code('json_work', r'''
import json
from datetime import datetime

answer = """
{"city": "Pune", "updated": "2026-11-07T09:30:00+05:30",
 "days": [{"date": "2026-11-07", "max": 31.5, "min": 19.0, "rain": null},
          {"date": "2026-11-08", "max": 29.0, "min": 18.5, "rain": 2.4},
          {"date": "2026-11-09", "max": 27.5, "min": 17.0}]}
"""
data = json.loads(answer)                     # the same as response.json() in requests
print(type(data).__name__, list(data))
print(data["city"], "has", len(data["days"]), "days")

updated = datetime.fromisoformat(data["updated"])
print("updated", updated.strftime("%d %b %Y %H:%M"), "offset", updated.utcoffset())

for day in data["days"]:
    rain = day.get("rain") or 0.0            # a missing key and null both become 0.0
    print(day["date"], f"{day['min']} to {day['max']} C, rain {rain} mm")

hottest = max(data["days"], key=lambda day: day["max"])
print("hottest day:", hottest["date"])
print(json.dumps({"city": data["city"], "hottest": hottest["max"]}, indent=2))
print(json.dumps({"name": "café"}), json.dumps({"name": "café"}, ensure_ascii=False))
''')

WHY_NET = 'It uses the requests library and a small server on your own computer, and the Python inside this page has no network sockets. Install requests once with <code>pip install requests</code>.'

K.lesson('idea', 'What a web API is, and why requests', f'''
{src('The requests 2.34 documentation (quickstart and advanced usage), RFC 9110 (HTTP semantics) and the Python 3.14 documentation of json and urllib.request.')}
{wwh('A <b>web API</b> is a website made for programs instead of people. You send an HTTP request to a URL and get data back, usually as JSON. Weather services, payment companies, GitHub and maps all offer one. <b>requests</b> is the most used Python library for calling them.',
     'Python can already call APIs with urllib.request, but you must encode query strings, write JSON bodies and headers, and catch errors by hand. That is a lot of code for something every program does.',
     'requests does those jobs in one call: requests.get(url, params=..., timeout=...) builds the URL, sends the request, reuses connections and returns a <b>Response</b> object with status_code, headers, text and json(). You only write what is special about your call.')}
{viz('pyreq')}
{versus('Python libraries for calling APIs', ['', 'urllib.request', 'requests', 'httpx', 'aiohttp'], [
    ['Comes with Python', 'Yes', 'No, pip install requests', 'No, pip install httpx', 'No, pip install aiohttp'],
    ['A JSON call', 'Encode, build a Request, read, json.loads', 'requests.get(url).json()', 'httpx.get(url).json()', 'Inside async with blocks'],
    ['4xx and 5xx', 'Raises HTTPError', 'Returns the response, raise_for_status() raises', 'Returns, raise_for_status() raises', 'Returns, raise_for_status() raises'],
    ['async and HTTP/2', 'No', 'No', 'Both', 'async only'],
    ['Best for', 'Scripts that must not install anything', 'Most scripts and apps', 'The same as requests, plus async code', 'Many calls at once in async servers']],
    'Start with requests: its style is copied by httpx, so what you learn here moves over. Use httpx or aiohttp when you need many calls at the same time, which the next chapter shows.')}
''', kw=['web API', 'requests', 'HTTP client', 'JSON', 'Response', 'urllib.request', 'httpx', 'aiohttp', 'pip install'])

K.lesson('get', 'Your first GET request', f'''
{local('first_get', WHY_NET)}
{table(['On the Response', 'Gives', 'Example'], [
    ['r.status_code, r.reason', 'The status number and its words', '200 and OK'],
    ['r.ok', 'True when the status is below 400', 'False for 404'],
    ['r.headers', 'A dict of headers that ignores upper and lower case', 'r.headers["content-type"]'],
    ['r.text', 'The body as a str, decoded with r.encoding', '&#39;[&#123;"id": 3 ...&#39;'],
    ['r.content', 'The body as raw bytes, for images and files', 'b&#39;&#92;x89PNG...&#39;'],
    ['r.json()', 'The body parsed from JSON into Python', 'a list or a dict'],
    ['r.url, r.request', 'The final URL, and the request that was really sent', 'r.request.headers']])}
{note('Always pass <b>timeout=</b>. requests has no timeout by default, so a server that never answers keeps your program waiting for ever. A number such as timeout=5 is used for connecting and again for each wait while reading.', 'warn')}
''', kw=['requests.get', 'params', 'timeout', 'status_code', 'ok', 'headers', 'text', 'content', 'json()', 'url'])

K.lesson('send', 'Sending data: POST, PUT, PATCH and DELETE', f'''
{local('sending', WHY_NET)}
{table(['Argument', 'Sends', 'Content-Type it sets', 'Use it for'], [
    ['params=dict', 'The dict in the URL query string', 'None', 'Search words, filters, page numbers'],
    ['json=obj', 'The object as JSON text in the body', 'application/json', 'Almost every modern API'],
    ['data=dict', 'The dict as a web form in the body', 'application/x-www-form-urlencoded', 'HTML forms, OAuth token requests'],
    ['files=dict', 'Files as multipart form data', 'multipart/form-data', 'Uploading pictures and documents'],
    ['headers=dict', 'Extra headers', 'Whatever you set', 'API keys, Accept, a custom User-Agent']])}
{note('For a big download use <code>requests.get(url, stream=True, timeout=10)</code> and write <code>for chunk in r.iter_content(64_000)</code> into a file opened with "wb". Then the whole file never has to fit in memory.', 'tip')}
{scene('a shop sends an order to a delivery company', '<p>When a customer pays, the shop server calls the delivery company API with requests.post(url, json=order, headers=..., timeout=10). The delivery API answers 201 with a tracking number, which the shop stores. If the answer is 422, the address is wrong and the shop asks the customer. If it is 503, the shop tries again a little later.</p>')}
''', kw=['POST', 'PUT', 'PATCH', 'DELETE', 'json=', 'data=', 'files=', 'headers=', 'form data', 'multipart', 'stream', 'iter_content'])

K.lesson('errors', 'When a call fails', f'''
{local('errors', WHY_NET)}
{table(['Exception', 'Means', 'Parent'], [
    ['requests.HTTPError', 'raise_for_status() found a 4xx or 5xx status', 'RequestException'],
    ['requests.ConnectionError', 'No connection: the server is down, the name is wrong, no network', 'RequestException'],
    ['requests.Timeout (ConnectTimeout, ReadTimeout)', 'The connect or a read took longer than timeout', 'RequestException'],
    ['requests.TooManyRedirects', 'Redirects went round in a circle', 'RequestException'],
    ['requests.JSONDecodeError', 'r.json() on a body that is not JSON', 'RequestException and ValueError'],
    ['requests.RequestException', 'The parent of all of them', 'OSError']])}
{steps('A safe way to call an API', [
    'Pass a timeout to every call.',
    'Call r.raise_for_status() right away, or check r.status_code yourself when some errors are normal (a 404 can mean "no such user").',
    'Catch the exact exceptions first and RequestException last, because except blocks are checked from top to bottom.',
    'Log the URL, the status and the error message from the body, so you can find the problem later.',
    'Retry only errors that may go away (timeouts, 429, 502, 503, 504), and only for requests that are safe to repeat.'])}
''', kw=['raise_for_status', 'HTTPError', 'ConnectionError', 'Timeout', 'ReadTimeout', 'JSONDecodeError', 'RequestException', 'error handling'])

K.lesson('session', 'Sessions, cookies and authentication', f'''
{local('session_auth', WHY_NET)}
{table(['Way to log in', 'How requests sends it', 'Notes'], [
    ['API key in a header', 'headers=&#123;"X-API-Key": key&#125;', 'Simple. Keep the key out of your code, read it from an environment variable'],
    ['Bearer token', 'headers=&#123;"Authorization": f"Bearer &#123;token&#125;"&#125;', 'Most modern APIs, often an OAuth 2 access token'],
    ['Basic auth', 'auth=("user", "password")', 'Name and password in base64, only safe over HTTPS'],
    ['Session cookie', 'A Session keeps Set-Cookie and sends it back', 'Websites that have a login form'],
    ['OAuth 2', 'Get a token first, then send it as Bearer', 'Libraries such as requests-oauthlib do the steps for you']])}
{note('A <b>Session</b> keeps cookies and default headers, and it reuses the TCP (and TLS) connection for every request to the same host. The example shows 3 requests over 1 connection. That saves one or two round trips each time, so use a Session whenever you make more than a couple of calls.', 'exam')}
{note('Never put a real token or password in code that you share or commit to git. Read it with os.environ["API_TOKEN"] and keep it in a .env file that git ignores.', 'warn')}
''', kw=['Session', 'cookies', 'connection reuse', 'keep alive', 'authentication', 'API key', 'Bearer token', 'Basic auth', 'OAuth 2', 'environment variable'])

K.lesson('json', 'Working with JSON answers', f'''
{run('json_work')}
{table(['JSON', 'Python after json.loads', 'Watch out'], [
    ['object &#123;...&#125;', 'dict', 'Keys are always str'],
    ['array [...]', 'list', ''],
    ['string', 'str', 'Dates stay strings, parse them with datetime.fromisoformat'],
    ['number', 'int or float', '1 becomes int, 1.0 becomes float'],
    ['true, false', 'True, False', ''],
    ['null', 'None', 'A missing key and a null value are different. dict.get covers both']])}
{note('Use data["key"] when the key must be there (a missing key is a bug you want to see), and data.get("key", default) when it is optional. The next chapter shows pydantic, which checks the whole shape of an answer at once.', 'tip')}
''', kw=['JSON', 'json.loads', 'json.dumps', 'indent', 'ensure_ascii', 'dict.get', 'nested data', 'datetime.fromisoformat', 'null'])

K.lesson('maths', 'The maths: round trips, timeouts and limits', f'''
{fxs(fx('Pages to fetch', 'pages = &lceil;items / page size&rceil;', '95 items, 20 per page: &lceil;4.75&rceil; = 5 requests.', key=True),
     fx('Time without a Session', 'n &times; (handshake RTTs + 1) &times; RTT', '10 calls, 2 handshake RTTs, RTT 50 ms: 10 &times; 3 &times; 50 = 1,500 ms.'),
     fx('Time with a Session', '(handshake RTTs + n) &times; RTT', '(2 + 10) &times; 50 = 600 ms, so 900 ms saved.', key=True),
     fx('Longest wait with timeout=(c, r)', 'up to c + r for each silent stretch', 'timeout=(3, 2): up to 3 s to connect, then 2 s with no data before ReadTimeout.'),
     fx('Rate limit', 'minimum time = requests / allowed rate', '300 calls at 60 per minute: 5 minutes.'),
     fx('Chance one of k tries works', 'P = 1 &minus; (1 &minus; p)<sup>k</sup>', 'p = 0.9, k = 3: 1 &minus; 0.001 = 0.999.', key=True))}
{steps('Worked example: download 2,000 records', [
    'The API gives 100 records per page, so &lceil;2000 / 100&rceil; = 20 requests.',
    'RTT is 60 ms and the server needs 40 ms per page. With a Session each request costs about 100 ms.',
    'One after another that is 20 &times; 100 = 2,000 ms, plus 120 ms for the first handshake.',
    'Without a Session each call adds 2 handshake round trips: 20 &times; (100 + 120) = 4,400 ms.',
    eq('Session: about 2.1 s, no Session: about 4.4 s')])}
''', kw=['pagination maths', 'RTT', 'connection reuse', 'timeout', 'rate limit', 'probability', 'retries'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Call requests.get with params and a timeout, read status_code and r.json(), and send JSON with requests.post.</p>',
    '<p>Handle every kind of error, use a Session with auth headers, send forms and files, and read nested JSON safely.</p>',
    '<p>Write a small client class for an API, test it with a fake server, and reason about round trips and limits.</p>',
    '<p>Add retries with backoff, pagination, rate limits, validation and async clients (next chapter), and keep secrets out of code.</p>')}
{grow('Make calls and read JSON.', 'Handle errors, sessions and auth.', 'Build reliable, testable API clients.')}
{deep('What requests is made of', '<p>requests sits on top of <b>urllib3</b>, which keeps a pool of open connections for each host and does the TLS work with Python&#39;s ssl module. Certificates are checked against the certifi bundle by default. That is why verify=False is dangerous: it turns off the check that you really talk to the right server.</p>')}
''', kw=['beginner', 'expert', 'urllib3', 'connection pool', 'certifi', 'verify', 'TLS'])

PLAY = '''

def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results
'''

lc(2418, 'Sort the People', 'sort-the-people', 'e', 'Sort pairs by one field', 'Like sorting API records by a field. Zip names with heights and sort by height, largest first.', r'''
def sort_people(names, heights):
    pairs = sorted(zip(heights, names), reverse=True)
    return [name for height, name in pairs]
''', [('sort_people(["Mary", "John", "Emma"], [180, 165, 170])', ['Mary', 'Emma', 'John']), ('sort_people(["Alice", "Bob", "Bob"], [155, 185, 150])', ['Bob', 'Alice', 'Bob'])])
lc(1854, 'Maximum Population Year', 'maximum-population-year', 'e', 'Count people alive in each year', 'Records with a start and an end, like user sessions in logs. Years are only 1950 to 2050, so count each year directly.', r'''
def maximum_population(logs):
    alive = [0] * 101
    for birth, death in logs:
        for year in range(birth, death):
            alive[year - 1950] += 1
    best = max(alive)
    return alive.index(best) + 1950
''', [('maximum_population([[1993, 1999], [2000, 2010]])', 1993), ('maximum_population([[1950, 1961], [1960, 1971], [1970, 1981]])', 1960)])
lc(1700, 'Number of Students Unable to Eat Lunch', 'number-of-students-unable-to-eat-lunch', 'e', 'Only the counts matter', 'A queue of requests waiting for a matching resource. Count how many want each kind, then serve the stack until no one wants the top item.', r'''
def count_students(students, sandwiches):
    wants = [students.count(0), students.count(1)]
    for sandwich in sandwiches:
        if wants[sandwich] == 0:
            break
        wants[sandwich] -= 1
    return wants[0] + wants[1]
''', [('count_students([1, 1, 0, 0], [0, 1, 0, 1])', 0), ('count_students([1, 1, 1, 0, 0, 1], [1, 0, 0, 0, 1, 1])', 3)])
lc(2456, 'Most Popular Video Creator', 'most-popular-video-creator', 'm', 'Group records by creator', 'Typical API analytics: total views per creator, and each creator&#39;s best video (most views, then the smallest id).', r'''
def most_popular_creator(creators, ids, views):
    total = {}
    best = {}
    for creator, video, count in zip(creators, ids, views):
        total[creator] = total.get(creator, 0) + count
        if creator not in best or (-count, video) < (-best[creator][1], best[creator][0]):
            best[creator] = (video, count)
    top = max(total.values())
    return sorted([creator, best[creator][0]] for creator in total if total[creator] == top)
''', [('most_popular_creator(["alice", "bob", "alice", "chris"], ["one", "two", "three", "four"], [5, 10, 5, 4])', [['alice', 'one'], ['bob', 'two']]), ('most_popular_creator(["alice", "alice", "alice"], ["a", "b", "c"], [1, 2, 2])', [['alice', 'b']])])
lc(1366, 'Rank Teams by Votes', 'rank-teams-by-votes', 'm', 'Sort by a tuple of vote counts', 'Count how often each team gets each place. Sort by the counts, most first, and by the letter on a tie.', r'''
def rank_teams(votes):
    places = len(votes[0])
    counts = {team: [0] * places for team in votes[0]}
    for vote in votes:
        for place, team in enumerate(vote):
            counts[team][place] += 1
    ranked = sorted(counts, key=lambda team: ([-c for c in counts[team]], team))
    return "".join(ranked)
''', [('rank_teams(["ABC", "ACB", "ABC", "ACB", "ACB"])', 'ACB'), ('rank_teams(["WXYZ", "XYZW"])', 'XWYZ'), ('rank_teams(["ZMNAGUEDSJYLBOPHRQICWFXTVK"])', 'ZMNAGUEDSJYLBOPHRQICWFXTVK')])
lc(355, 'Design Twitter', 'design-twitter', 'm', 'Dicts of lists and sets, heapq.nlargest', 'A small social API. Store each user&#39;s tweets with a counter as the time. The feed is the 10 newest tweets of the user and the people they follow.', r'''
import heapq
from itertools import count


class Twitter:
    def __init__(self):
        self.clock = count()
        self.tweets = {}
        self.follows = {}

    def postTweet(self, userId, tweetId):
        self.tweets.setdefault(userId, []).append((next(self.clock), tweetId))

    def getNewsFeed(self, userId):
        people = self.follows.get(userId, set()) | {userId}
        candidates = []
        for person in people:
            candidates.extend(self.tweets.get(person, [])[-10:])
        newest = heapq.nlargest(10, candidates)
        return [tweet_id for time, tweet_id in newest]

    def follow(self, followerId, followeeId):
        self.follows.setdefault(followerId, set()).add(followeeId)

    def unfollow(self, followerId, followeeId):
        self.follows.get(followerId, set()).discard(followeeId)
''' + PLAY, [('play(Twitter, ["Twitter", "postTweet", "getNewsFeed", "follow", "postTweet", "getNewsFeed", "unfollow", "getNewsFeed"], [[], [1, 5], [1], [1, 2], [2, 6], [1], [1, 2], [1]])', [None, None, [5], None, None, [6, 5], None, [5]])])
lc(1348, 'Tweet Counts Per Frequency', 'tweet-counts-per-frequency', 'm', 'Put each time into a bucket', 'API dashboards count events per minute, hour or day. The bucket of a time t is (t &minus; start) // size.', r'''
class TweetCounts:
    SIZE = {"minute": 60, "hour": 3600, "day": 86400}

    def __init__(self):
        self.times = {}

    def recordTweet(self, tweetName, time):
        self.times.setdefault(tweetName, []).append(time)

    def getTweetCountsPerFrequency(self, freq, tweetName, startTime, endTime):
        size = self.SIZE[freq]
        counts = [0] * ((endTime - startTime) // size + 1)
        for t in self.times.get(tweetName, []):
            if startTime <= t <= endTime:
                counts[(t - startTime) // size] += 1
        return counts
''' + PLAY, [('play(TweetCounts, ["TweetCounts", "recordTweet", "recordTweet", "recordTweet", "getTweetCountsPerFrequency", "getTweetCountsPerFrequency", "recordTweet", "getTweetCountsPerFrequency"], [[], ["tweet3", 0], ["tweet3", 60], ["tweet3", 10], ["minute", "tweet3", 0, 59], ["minute", "tweet3", 0, 60], ["tweet3", 120], ["hour", "tweet3", 0, 210]])', [None, None, None, None, [2], [2, 1], None, [4]])])
lc(1606, 'Find Servers That Handled Most Number of Requests', 'find-servers-that-handled-most-number-of-requests', 'h', 'Two heaps: busy servers and free servers', 'A load balancer. Request i prefers server i % k, or the next free one after it. Store a free server j as i + (j &minus; i) % k so the smallest number in the heap is the right server.', r'''
import heapq


def busiest_servers(k, arrival, load):
    handled = [0] * k
    busy = []
    free = list(range(k))
    for i, (start, length) in enumerate(zip(arrival, load)):
        while busy and busy[0][0] <= start:
            finish, server = heapq.heappop(busy)
            heapq.heappush(free, i + (server - i) % k)
        if free:
            server = heapq.heappop(free) % k
            handled[server] += 1
            heapq.heappush(busy, (start + length, server))
    most = max(handled)
    return [server for server in range(k) if handled[server] == most]
''', [('busiest_servers(3, [1, 2, 3, 4, 5], [5, 2, 3, 3, 3])', [1]), ('busiest_servers(3, [1, 2, 3, 4], [1, 2, 1, 2])', [0]), ('busiest_servers(3, [1, 2, 3], [10, 12, 11])', [0, 1, 2])])
lc(2102, 'Sequentially Ordinal Rank Tracker', 'sequentially-ordinal-rank-tracker', 'h', 'Two heaps split at the i-th best', 'Keep the places already returned in one heap with the worst on top, and the rest in another with the best on top. get() moves one place across.', r'''
import heapq


class Worst:
    """Orders places so the WORST comes first: a lower score, then the later name."""

    def __init__(self, score, name):
        self.score = score
        self.name = name

    def __lt__(self, other):
        if self.score != other.score:
            return self.score < other.score
        return self.name > other.name


class SORTracker:
    def __init__(self):
        self.best = []
        self.rest = []

    def add(self, name, score):
        heapq.heappush(self.best, Worst(score, name))
        worst = heapq.heappop(self.best)
        heapq.heappush(self.rest, (-worst.score, worst.name))

    def get(self):
        score, name = heapq.heappop(self.rest)
        heapq.heappush(self.best, Worst(-score, name))
        return name
''' + PLAY, [('play(SORTracker, ["SORTracker", "add", "add", "get", "add", "get", "add", "get", "add", "get", "add", "get", "get"], [[], ["bradford", 2], ["branford", 3], [], ["alps", 2], [], ["orland", 2], [], ["orangered", 10], [], ["alpine", 2], [], []])', [None, None, None, 'branford', None, 'alps', None, 'bradford', None, 'bradford', None, 'bradford', 'orland'])])
lc(352, 'Data Stream as Disjoint Intervals', 'data-stream-as-disjoint-intervals', 'h', 'A set of numbers, joined into runs when asked', 'Like tracking which parts of a file have arrived. Keep the numbers in a set, and on getIntervals walk them in order and join neighbours into ranges.', r'''
class SummaryRanges:
    def __init__(self):
        self.numbers = set()

    def addNum(self, value):
        self.numbers.add(value)

    def getIntervals(self):
        result = []
        for number in sorted(self.numbers):
            if result and number == result[-1][1] + 1:
                result[-1][1] = number
            else:
                result.append([number, number])
        return result
''' + PLAY, [('play(SummaryRanges, ["SummaryRanges", "addNum", "getIntervals", "addNum", "getIntervals", "addNum", "getIntervals", "addNum", "getIntervals", "addNum", "getIntervals"], [[], [1], [], [3], [], [7], [], [2], [], [6], []])', [None, None, [[1, 1]], None, [[1, 1], [3, 3]], None, [[1, 1], [3, 3], [7, 7]], None, [[1, 3], [7, 7]], None, [[1, 3], [6, 7]]])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>API code spends most of its time on the data that comes back: sorting records, counting by a key, grouping by time, ranking, building feeds and spreading requests over servers. These problems practise exactly those jobs.</p>'), kw=['LeetCode', 'sorting', 'counting', 'heap', 'design', 'time buckets', 'ranking', 'load balancing'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A web API is HTTP for programs. requests.get, post, put, patch and delete call it and return a Response.',
    'params= goes into the URL, json= sends a JSON body, data= a form, files= uploads. Always pass timeout=.',
    'A 4xx or 5xx is not an exception until raise_for_status(). Catch HTTPError, Timeout and ConnectionError, and RequestException last.',
    'A Session keeps cookies and headers and reuses connections. Send tokens in the Authorization header and keep them out of code.',
    'r.json() gives dicts and lists. Use [] for required keys and .get() for optional ones, and parse dates with datetime.'],
    'Next: real API work with pagination, retries, rate limits, validation and async clients.')}
{files('Three tasks: pick data out of a list of repositories, read a value from nested JSON by a path, and write a small API client that you can test with a fake server.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does r.json() return for the body [{"id": 1}]?', ['A str', 'A list with one dict', 'A dict', 'bytes'], 1, 'JSON array becomes a list.', 'r.text would give the same thing as a string.')
K.quiz('e', 'requests.get gets a 404 answer. What happens?', ['It raises an exception', 'It returns a Response with status_code 404', 'It returns None', 'It tries again'], 1, 'requests does not raise on its own.', 'Call r.raise_for_status() when you want an exception.')
K.quiz('e', 'Which argument sends a dict as a JSON body?', ['params=', 'data=', 'json=', 'body='], 2, 'The name says it.', 'json= also sets Content-Type: application/json.')
K.quiz('m', 'What is the default timeout in requests?', ['5 seconds', '30 seconds', 'None, it can wait for ever', '60 seconds'], 2, 'Always pass one.', 'Linters such as bandit warn about calls with no timeout.')
K.quiz('m', 'When is r.ok True?', ['Only for 200', 'When the status is below 400', 'When the body is JSON', 'When there was no redirect'], 1, '1xx, 2xx and 3xx.', '3xx are rare to see because requests follows redirects for you.')
K.quiz('m', 'params={"q": "dune messiah"} becomes which query string?', ['q=dune messiah', 'q=dune+messiah', 'q="dune messiah"', 'q=dune,messiah'], 1, 'Spaces in a query.', 'requests encodes a space as + and other special letters as %XX.')
K.quiz('m', 'What does data={"user": "ann"} send?', ['JSON', 'A web form: user=ann with Content-Type application/x-www-form-urlencoded', 'A query string', 'A file'], 1, 'Like an HTML form.', 'Use json= for JSON APIs.')
K.quiz('m', 'Why use a requests.Session for many calls?', ['It is required for POST', 'It reuses connections and keeps cookies and headers', 'It makes calls run in parallel', 'It caches every answer'], 1, 'One connection, many requests.', 'Fewer handshakes means less waiting.')
K.quiz('m', 'Which except block must come first?', ['except requests.RequestException', 'except requests.Timeout', 'They can be in any order', 'except Exception'], 1, 'Child before parent.', 'If RequestException came first, it would catch the Timeout and the second block would never run.')
K.quiz('h', 'Why is verify=False a bad idea?', ['It is slower', 'It turns off the TLS certificate check, so another server could pretend to be the API', 'It disables cookies', 'It only works for GET'], 1, 'Who are you talking to.', 'Fix certificate problems with the right CA bundle instead.')
K.quiz('h', 'A POST /payments timed out. Is it safe to just send it again?', ['Yes, always', 'Not without an idempotency key, because the first one may have worked', 'Only with a longer timeout', 'Only on Mondays'], 1, 'POST is not idempotent.', 'Payment APIs accept an Idempotency-Key header so a repeat is ignored.')
K.quiz('x', 'In the style of a Stanford CS 142 exam: 10 API calls, RTT 50 ms, a new HTTPS connection needs 2 extra round trips. How much time does reusing one connection save?', ['None', '900 ms', '500 ms', '100 ms'], 1, 'n &times; 3 RTT against (2 + n) RTT.', '1,500 ms without, 600 ms with a Session.')
K.quiz('x', 'In the style of a CMU 15-213 exam question on robustness: a client retries a failing GET up to 3 times in total. Each try works with probability 0.9, independently. What is the chance it fails in the end?', ['0.1', '0.01', '0.001', '0.3'], 2, 'All 3 tries must fail.', '0.1<sup>3</sup> = 0.001, so retries turn 90 % into 99.9 %.')

K.calc('e', 'An API returns 20 items per page. How many requests are needed for 95 items?', '5', 'Round up.', ['95 / 20 = 4.75.', 'A part page still needs a request.', eq('&lceil;4.75&rceil; = 5')], check=-(-95 // 20))
K.calc('e', 'How many characters does json.dumps({"q": "dune"}) make?', '13', 'Count every character, the space too.', ['The text is &#123;"q": "dune"&#125;.', 'Braces 2, "q" 3, colon and space 2, "dune" 6.', eq('13')], check=len('{"q": "dune"}'))
K.calc('e', 'Three calls run one after another, each takes 120 ms. How many ms in total?', '360', 'Add them.', ['One after another means no overlap.', '3 &times; 120.', eq('360 ms')], check=3 * 120)
K.calc('m', '10 calls, RTT 50 ms, each new connection costs 2 extra round trips. How many ms does a Session save?', '900', 'Without: 10 &times; 3 RTT. With: (2 + 10) RTT.', ['Without: 10 &times; 3 &times; 50 = 1,500 ms.', 'With: 12 &times; 50 = 600 ms.', eq('900 ms')], check=10 * 3 * 50 - (2 + 10) * 50)
K.calc('m', 'timeout=(3, 2). Connecting takes 2.9 s, then the server sends nothing. After how many seconds does ReadTimeout come?', '4.9', 'Connect time plus the read timeout.', ['Connect works after 2.9 s, inside the 3 s limit.', 'Then 2 s with no data.', eq('2.9 + 2 = 4.9 s')], check=2.9 + 2, tol=0.01)
K.calc('m', 'An API allows 60 requests per minute. How many seconds do 300 requests need at least?', '300', 'requests / rate.', ['300 / 60 = 5 minutes.', '5 &times; 60 s.', eq('300 s')], check=300 / 60 * 60)
K.calc('m', 'Each try works with probability 0.9. What is the chance that at least one of 3 tries works (3 decimals)?', '0.999', '1 &minus; (1 &minus; p)<sup>k</sup>.', ['One try fails with 0.1.', 'All 3 fail with 0.1<sup>3</sup> = 0.001.', eq('1 &minus; 0.001 = 0.999')], check=1 - 0.1 ** 3, tol=0.0005)
K.calc('m', '100 calls of 200 ms each, 10 at the same time. How many seconds in total?', '2', 'Rounds of 10.', ['100 / 10 = 10 rounds.', 'Each round takes 0.2 s.', eq('10 &times; 0.2 = 2 s')], check=100 / 10 * 0.2)
K.calc('h', 'A call works with probability 0.8 and you retry until it works. How many tries on average?', '1.25', 'The mean of a geometric distribution is 1 / p.', ['Each try is independent.', 'Mean tries = 1 / p.', eq('1 / 0.8 = 1.25')], check=1 / 0.8)
K.calc('x', 'In the style of a Stanford CS 142 exam: a page needs 12 API answers, each 1 RTT of 80 ms, over 6 open connections at once. What is the least time in ms?', '160', 'Rounds of 6.', ['12 / 6 = 2 rounds.', 'Each round is one RTT.', eq('2 &times; 80 = 160 ms')], check=12 // 6 * 80)

K.assign('repos', 'e', 'Pick data out of an API answer',
         '<p>REPOS is a list of repositories as an API like GitHub returns it. Write <code>top_repos(repos, n)</code>: the names of the n repositories with the most stars ("stars"), and on a tie the name that comes first A to Z. Write <code>language_counts(repos)</code>: a dict from language to how many repositories use it, where a language that is null or missing counts as "unknown".</p>',
         '''
def top_repos(repos, n):
    ranked = sorted(repos, key=lambda repo: repo["stars"])
    return [repo["name"] for repo in ranked[:n]]


def language_counts(repos):
    counts = {}
    for repo in repos:
        language = repo["language"]
        counts[language] = counts.get(language, 0) + 1
    return counts


REPOS = [
    {"name": "flask", "stars": 68000, "language": "Python"},
    {"name": "requests", "stars": 52000, "language": "Python"},
    {"name": "httpx", "stars": 13000, "language": "Python"},
    {"name": "express", "stars": 65000, "language": "JavaScript"},
    {"name": "awesome-list", "stars": 52000, "language": None},
    {"name": "notes", "stars": 3},
]
''', [('top_repos(REPOS, 3)', ['flask', 'express', 'awesome-list']), ('top_repos(REPOS, 1)', ['flask']), ('top_repos([], 2)', []), ('language_counts(REPOS)', {'Python': 3, 'JavaScript': 1, 'unknown': 2}), ('language_counts([])', {})],
         '''
def top_repos(repos, n):
    ranked = sorted(repos, key=lambda repo: (-repo["stars"], repo["name"]))
    return [repo["name"] for repo in ranked[:n]]


def language_counts(repos):
    counts = {}
    for repo in repos:
        language = repo.get("language") or "unknown"
        counts[language] = counts.get(language, 0) + 1
    return counts


REPOS = [
    {"name": "flask", "stars": 68000, "language": "Python"},
    {"name": "requests", "stars": 52000, "language": "Python"},
    {"name": "httpx", "stars": 13000, "language": "Python"},
    {"name": "express", "stars": 65000, "language": "JavaScript"},
    {"name": "awesome-list", "stars": 52000, "language": None},
    {"name": "notes", "stars": 3},
]
''', 'Sort by (minus stars, name) so more stars come first and ties go A to Z. repo.get("language") or "unknown" covers both a missing key and None.', '<p>Real answers often leave out empty fields or send null. Code that only works for the full example answer breaks on the first unusual record.</p>')
K.assign('getpath', 'm', 'Read a value from nested JSON by a path',
         '<p>Write <code>get_path(data, path, default=None)</code>. The path is keys and list positions joined by dots, such as "user.address.city" or "orders.1.total". When the current value is a list, the part must be a number and is used as a position. Return default when a key is missing, a position is out of range, or the value is not a dict or a list.</p>',
         '''
def get_path(data, path, default=None):
    value = data
    for part in path.split("."):
        value = value[part]
    return value


DATA = {
    "user": {"name": "Ann", "address": {"city": "Pune", "zip": None}},
    "orders": [{"id": 7, "total": 250}, {"id": 9, "total": 99}],
}
''', [('get_path(DATA, "user.address.city")', 'Pune'), ('get_path(DATA, "orders.1.total")', 99), ('get_path(DATA, "orders.5.total", "none")', 'none'), ('get_path(DATA, "user.phone", "?")', '?'), ('get_path(DATA, "user.name.first", "?")', '?'), ('get_path(DATA, "orders.x", 0)', 0), ('get_path(DATA, "user.address.zip", "empty")', None)],
         '''
def get_path(data, path, default=None):
    value = data
    for part in path.split("."):
        if isinstance(value, dict):
            if part not in value:
                return default
            value = value[part]
        elif isinstance(value, list):
            if not part.isdigit() or int(part) >= len(value):
                return default
            value = value[int(part)]
        else:
            return default
    return value


DATA = {
    "user": {"name": "Ann", "address": {"city": "Pune", "zip": None}},
    "orders": [{"id": 7, "total": 250}, {"id": 9, "total": 99}],
}
''', 'Look at the type of the current value at each step: a dict needs the key, a list needs a number in range, anything else means the path is wrong. A key that is there with the value null gives None, not the default.', '<p>Tools such as jq, JMESPath and glom do this for real projects. Writing it once shows how to walk any JSON safely.</p>')
K.assign('client', 'h', 'Write a small API client you can test',
         '<p>BookClient gets a <code>send(method, path, body=None)</code> function that returns (status, data). In real code send would use requests, and in the tests it is FakeServer.send. Write <code>get_book(book_id)</code>: the book dict, None for 404, and for a 5xx status try again, 3 tries in total, then raise RuntimeError. Write <code>create_book(title)</code>: POST /books with &#123;"title": title&#125;, return the new book for 201, raise ValueError with the message from the server for 422. Never retry the POST, and raise RuntimeError for any other status.</p>',
         '''
class FakeServer:
    """Pretends to be the book API. send(method, path, body) returns (status, data)."""

    def __init__(self):
        self.books = {1: {"id": 1, "title": "Dune"}}
        self.calls = 0
        self.fail_next = 0

    def send(self, method, path, body=None):
        self.calls += 1
        if self.fail_next > 0:
            self.fail_next -= 1
            return 503, {"error": "busy, try later"}
        if method == "GET" and path.startswith("/books/"):
            book_id = int(path.split("/")[2])
            if book_id in self.books:
                return 200, self.books[book_id]
            return 404, {"error": "not found"}
        if method == "POST" and path == "/books":
            title = str((body or {}).get("title", "")).strip()
            if not title:
                return 422, {"error": "title is required"}
            new_id = max(self.books) + 1
            self.books[new_id] = {"id": new_id, "title": title}
            return 201, self.books[new_id]
        return 405, {"error": "method not allowed"}


class BookClient:
    def __init__(self, send):
        self.send = send

    def get_book(self, book_id):
        status, data = self.send("GET", f"/books/{book_id}")
        return data

    def create_book(self, title):
        status, data = self.send("POST", "/books", {"title": title})
        return data


def try_get(book_id):
    return BookClient(FakeServer().send).get_book(book_id)


def create(title):
    return BookClient(FakeServer().send).create_book(title)


def create_error(title):
    try:
        create(title)
    except ValueError as err:
        return f"ValueError: {err}"
    return "no error"


def flaky(failures):
    server = FakeServer()
    server.fail_next = failures
    try:
        book = BookClient(server.send).get_book(1)
    except RuntimeError:
        return ["RuntimeError", server.calls]
    return [book, server.calls]


def flaky_post():
    server = FakeServer()
    server.fail_next = 1
    try:
        BookClient(server.send).create_book("Emma")
    except RuntimeError:
        return ["RuntimeError", server.calls]
    return ["no error", server.calls]
''', [('try_get(1)', {'id': 1, 'title': 'Dune'}), ('try_get(5)', None), ('create("  Emma ")', {'id': 2, 'title': 'Emma'}), ('create_error("")', 'ValueError: title is required'), ('flaky(2)', [{'id': 1, 'title': 'Dune'}, 3]), ('flaky(3)', ['RuntimeError', 3]), ('flaky_post()', ['RuntimeError', 1])],
         '''
class FakeServer:
    """Pretends to be the book API. send(method, path, body) returns (status, data)."""

    def __init__(self):
        self.books = {1: {"id": 1, "title": "Dune"}}
        self.calls = 0
        self.fail_next = 0

    def send(self, method, path, body=None):
        self.calls += 1
        if self.fail_next > 0:
            self.fail_next -= 1
            return 503, {"error": "busy, try later"}
        if method == "GET" and path.startswith("/books/"):
            book_id = int(path.split("/")[2])
            if book_id in self.books:
                return 200, self.books[book_id]
            return 404, {"error": "not found"}
        if method == "POST" and path == "/books":
            title = str((body or {}).get("title", "")).strip()
            if not title:
                return 422, {"error": "title is required"}
            new_id = max(self.books) + 1
            self.books[new_id] = {"id": new_id, "title": title}
            return 201, self.books[new_id]
        return 405, {"error": "method not allowed"}


class BookClient:
    TRIES = 3

    def __init__(self, send):
        self.send = send

    def get_book(self, book_id):
        for attempt in range(self.TRIES):
            status, data = self.send("GET", f"/books/{book_id}")
            if status < 500:
                break
        else:
            raise RuntimeError(f"server error {status} after {self.TRIES} tries")
        if status == 404:
            return None
        if status != 200:
            raise RuntimeError(f"unexpected status {status}")
        return data

    def create_book(self, title):
        status, data = self.send("POST", "/books", {"title": title})
        if status == 422:
            raise ValueError(data["error"])
        if status != 201:
            raise RuntimeError(f"unexpected status {status}")
        return data


def try_get(book_id):
    return BookClient(FakeServer().send).get_book(book_id)


def create(title):
    return BookClient(FakeServer().send).create_book(title)


def create_error(title):
    try:
        create(title)
    except ValueError as err:
        return f"ValueError: {err}"
    return "no error"


def flaky(failures):
    server = FakeServer()
    server.fail_next = failures
    try:
        book = BookClient(server.send).get_book(1)
    except RuntimeError:
        return ["RuntimeError", server.calls]
    return [book, server.calls]


def flaky_post():
    server = FakeServer()
    server.fail_next = 1
    try:
        BookClient(server.send).create_book("Emma")
    except RuntimeError:
        return ["RuntimeError", server.calls]
    return ["no error", server.calls]
''', 'A for loop with an else block fits the retry: break when the status is below 500, and the else part runs only when every try failed. Map each status to a return value or an exception.', '<p>Passing send in, instead of calling requests inside the class, is called dependency injection. It lets you test the client without a network. In real code send would be a small function around session.request(method, BASE + path, json=body, timeout=5).</p>')

K.must('Calls', 'requests.get, post, put, patch, delete(url, params=, json=, data=, headers=, timeout=). Response: status_code, ok, headers, text, content, json().')
K.must('Errors', 'raise_for_status() for 4xx and 5xx. HTTPError, ConnectionError, Timeout, JSONDecodeError, all under RequestException (catch it last).')
K.must('Timeouts', 'No default timeout. timeout=5 or timeout=(connect, read). Always pass one.')
K.must('Session', 'Reuses connections, keeps cookies and headers. Auth: Authorization: Bearer token, auth=(user, pw), API key header. Secrets come from environment variables.')
K.must('JSON', 'object to dict, array to list, null to None. [] for required keys, .get() for optional. datetime.fromisoformat for dates.')

T = K.topic(
    slug='py-requests', topic='py-requests', step=(2, 'Calling web APIs', 'py-w2', 'Use real web APIs from Python: requests, errors and timeouts, sessions and auth, JSON, then pagination, retries, rate limits, validation and async clients.', 'Intermediate'),
    title='Calling web APIs with requests', short='requests', badge='2.1', minutes=90,
    lead='Call web APIs the way real Python programs do. Send GET and POST requests with requests, handle every kind of error and timeout, log in with sessions and tokens, and read JSON answers safely.',
    desc='What a web API is, requests compared with urllib, httpx and aiohttp, GET with params and timeout, the Response object, POST, PUT, PATCH and DELETE with json=, data= and files=, streaming downloads, raise_for_status and the requests exceptions, Session, cookies and connection reuse, API keys, Bearer tokens and Basic auth, JSON to Python types, and the maths of round trips, timeouts and rate limits.',
    summary='requests: GET and POST, params and json, timeouts, errors, sessions, auth and JSON answers.',
    keywords=['requests', 'web API', 'GET', 'POST', 'JSON', 'timeout', 'raise_for_status', 'Session', 'Bearer token', 'cookies'],
    recap='<p>One requests call builds the HTTP request, sends it and wraps the answer in a Response. Your job is to pass a timeout, check the status and handle the errors.</p>',
    added='2026-11-07', leet=leet_items())
