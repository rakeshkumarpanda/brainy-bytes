# Web and APIs 1.1: HTTP and REST. Checked against RFC 9110 (HTTP semantics: methods, safe and idempotent methods,
# status codes, headers, conditional requests), RFC 9111 (caching), RFC 3986 (URLs), RFC 6265 (cookies) and the
# Python 3.14 documentation of urllib.parse, http, http.server, http.client, http.cookies and urllib.request.
# Programs that open network sockets cannot run in the page's Pyodide, so they use local() and show a real run.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, lc, leet, files, grow, leet_items

chapter('py-http')
K = Kit()

K.code('url_parts', r'''
from urllib.parse import parse_qs, quote, unquote, urlencode, urljoin, urlsplit

url = "https://api.example.com:8443/v1/books/42?fields=title,year&lang=en#reviews"
parts = urlsplit(url)
print("scheme:", parts.scheme)
print("host:", parts.hostname, "port:", parts.port)
print("path:", parts.path)
print("query:", parts.query)
print("query as a dict:", parse_qs(parts.query))
print("fragment:", parts.fragment)          # never sent to the server, the browser keeps it

print(urlencode({"q": "python & web", "page": 2}))   # safe query text from a dict
print(quote("café menu/1"), unquote("caf%C3%A9"))
print(urljoin("https://example.com/docs/intro.html", "api.html"))
print(urljoin("https://example.com/docs/intro.html", "/api.html"))
''')
K.code('status_codes', r'''
from http import HTTPStatus

for code in (200, 201, 204, 301, 304, 400, 401, 403, 404, 409, 422, 429, 500, 503):
    print(code, HTTPStatus(code).phrase)

print(HTTPStatus.NOT_FOUND.value, "-", HTTPStatus.NOT_FOUND.description)


def kind(code):
    if 200 <= code < 300:
        return "success"
    if 300 <= code < 400:
        return "redirect"
    if 400 <= code < 500:
        return "client error: fix the request"
    if 500 <= code < 600:
        return "server error: maybe try again later"
    return "not an HTTP status"


for code in (204, 302, 422, 503, 99):
    print(code, kind(code))
''')
K.code('raw_http', r'''
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


class Hello(BaseHTTPRequestHandler):
    def do_GET(self):
        print("server got:", self.requestline)
        print("server saw the header Accept:", self.headers["Accept"])
        body = b"Hello from the server\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):            # keep the console quiet
        pass


server = HTTPServer(("127.0.0.1", 0), Hello)    # port 0: the system picks a free port
threading.Thread(target=server.serve_forever, daemon=True).start()
port = server.server_address[1]

request = (
    "GET /hello?name=ann HTTP/1.1\r\n"
    f"Host: 127.0.0.1:{port}\r\n"
    "Accept: text/plain\r\n"
    "Connection: close\r\n"
    "\r\n"                                      # the blank line ends the headers
)
with socket.create_connection(("127.0.0.1", port)) as sock:
    sock.sendall(request.encode())
    raw = b""
    while True:
        chunk = sock.recv(1024)
        if not chunk:
            break
        raw += chunk

print("--- the raw response ---")
for line in raw.decode().split("\r\n"):
    if not line.startswith(("Date:", "Server:")):   # these two change on every run
        print(repr(line))
server.shutdown()
''', long=True)
K.code('book_api', r'''
import json
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.error import HTTPError

BOOKS = {1: {"id": 1, "title": "Dune"}, 2: {"id": 2, "title": "Emma"}}


class BookAPI(BaseHTTPRequestHandler):
    def send_json(self, status, data, extra_headers=None):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/books":
            return self.send_json(200, list(BOOKS.values()))
        parts = self.path.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "books" and parts[1].isdigit():
            book = BOOKS.get(int(parts[1]))
            if book is None:
                return self.send_json(404, {"error": f"book {parts[1]} not found"})
            return self.send_json(200, book)
        self.send_json(404, {"error": "no such page"})

    def do_POST(self):
        if self.path != "/books":
            return self.send_json(404, {"error": "no such page"})
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length))
            title = data["title"].strip()
        except (ValueError, KeyError, AttributeError):
            return self.send_json(400, {"error": "send JSON with a title"})
        new_id = max(BOOKS) + 1
        BOOKS[new_id] = {"id": new_id, "title": title}
        self.send_json(201, BOOKS[new_id], {"Location": f"/books/{new_id}"})

    def log_message(self, *args):
        pass


server = HTTPServer(("127.0.0.1", 0), BookAPI)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_address[1]}"


def call(method, path, data=None):
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(BASE + path, data=body, method=method,
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, response.headers.get("Location"), json.loads(response.read())
    except HTTPError as err:                     # urllib raises for 4xx and 5xx
        return err.code, None, json.loads(err.read())


print(call("GET", "/books"))
print(call("GET", "/books/2"))
print(call("GET", "/books/99"))
print(call("POST", "/books", {"title": "Ulysses"}))
print(call("POST", "/books", {"name": "no title"}))
print(call("GET", "/books"))
server.shutdown()
''', long=True)
K.code('cookies_cache', r'''
from http.cookies import SimpleCookie

cookie = SimpleCookie()
cookie["session"] = "abc123"
cookie["session"]["httponly"] = True        # JavaScript in the page cannot read it
cookie["session"]["secure"] = True          # only sent over HTTPS
cookie["session"]["samesite"] = "Lax"       # not sent with most requests from other sites
cookie["session"]["max-age"] = 3600         # forget it after one hour
print(cookie.output())

incoming = SimpleCookie("session=abc123; theme=dark")    # the Cookie header a browser sends back
print({name: morsel.value for name, morsel in incoming.items()})


def answer(request_headers, current_etag):
    """What a server answers for a page whose version label (ETag) is current_etag."""
    if request_headers.get("If-None-Match") == current_etag:
        return 304, "Not Modified, no body"
    return 200, f"the full page, ETag {current_etag}"


print(answer({}, '"v7"'))
print(answer({"If-None-Match": '"v7"'}, '"v7"'))
print(answer({"If-None-Match": '"v6"'}, '"v7"'))
''')

WHY_NET = 'It opens a real network socket, and the Python inside this page has no network sockets.'

K.lesson('idea', 'How the web works: one request, one response', f'''
{src('RFC 9110 (HTTP semantics), RFC 9111 (caching), RFC 3986 (URLs) and the Python 3.14 documentation of urllib, http.server and http.client.')}
{wwh('<b>HTTP</b> (HyperText Transfer Protocol) is the language that browsers, apps and servers use to talk. A client sends a <b>request</b> (a method such as GET, a path and some headers) and the server sends back a <b>response</b> (a status code, headers and usually a body). <b>HTTPS</b> is the same thing inside an encrypted TLS connection.',
     'Programs written in different languages on different computers need one shared, simple set of rules to ask for data and send it. Without a standard every website and app would need its own protocol.',
     'HTTP messages are plain text lines sent over a TCP connection: a first line, headers, a blank line, then the body. Because the format is so simple, any language can read and write it, and Python has it in the standard library.')}
{viz('pyhttp')}
{versus('Ways for programs to talk over the network', ['', 'REST over HTTP', 'GraphQL', 'gRPC', 'WebSocket'], [
    ['Idea', 'URLs name resources, methods say what to do', 'One URL, the client writes a query for exactly the fields it wants', 'Call functions on a server, messages in Protocol Buffers', 'One connection that stays open, both sides send at any time'],
    ['Data', 'Usually JSON', 'JSON', 'Binary, typed', 'Text or binary frames'],
    ['Good for', 'Public APIs, most web apps', 'Apps that need flexible queries', 'Fast calls between internal services', 'Chat, live prices, games'],
    ['Caching', 'Built into HTTP', 'Harder', 'Do it yourself', 'Not for messages'],
    ['In Python', 'requests, Flask, Django, FastAPI', 'graphene, strawberry', 'grpcio', 'websockets']],
    'Learn REST over HTTP first: almost every API you will call uses it, and the others build on the same ideas.')}
''', kw=['HTTP', 'HTTPS', 'request', 'response', 'client', 'server', 'TCP', 'TLS', 'DNS', 'REST', 'GraphQL', 'gRPC', 'WebSocket'])

K.lesson('urls', 'URLs: the address of a resource', f'''
{run('url_parts')}
{table(['Part', 'Example', 'Meaning'], [
    ['scheme', 'https', 'How to talk: http, https, ftp, mailto ...'],
    ['host', 'api.example.com', 'Which computer. DNS turns it into an IP address'],
    ['port', '8443', 'Which program on that computer. Default 80 for http, 443 for https'],
    ['path', '/v1/books/42', 'Which resource on the server'],
    ['query', 'fields=title,year&amp;lang=en', 'Extra options as name=value pairs joined with &amp;'],
    ['fragment', 'reviews', 'A place inside the page. The browser keeps it and never sends it']])}
{note('URLs may only contain a small set of characters. Others, like spaces, é or &amp; inside a value, must be <b>percent encoded</b>: each byte becomes % and two hex digits, so a space is %20 and é (2 bytes in UTF-8) is %C3%A9. Use urlencode or let requests do it with params=, never glue query text together by hand.', 'exam')}
''', kw=['URL', 'scheme', 'host', 'port', 'path', 'query string', 'fragment', 'urlsplit', 'parse_qs', 'urlencode', 'percent encoding', 'urljoin'])

K.lesson('message', 'Inside an HTTP message', f'''
{local('raw_http', WHY_NET)}
{note('BaseHTTPRequestHandler answers with HTTP/1.0 unless you set protocol_version = "HTTP/1.1" in the class. Every line ends with &#92;r&#92;n (carriage return and new line), and an empty line separates the headers from the body.', 'tip')}
{table(['Method', 'Means', 'Safe (changes nothing)', 'Idempotent (same result if repeated)', 'Has a body'], [
    ['GET', 'Read a resource', 'Yes', 'Yes', 'No'],
    ['HEAD', 'Like GET, but only the headers', 'Yes', 'Yes', 'No'],
    ['POST', 'Create something, or run an action', 'No', 'No', 'Yes'],
    ['PUT', 'Replace the whole resource', 'No', 'Yes', 'Yes'],
    ['PATCH', 'Change part of a resource', 'No', 'Not always', 'Yes'],
    ['DELETE', 'Remove a resource', 'No', 'Yes', 'Usually no'],
    ['OPTIONS', 'Ask what is allowed (used by CORS)', 'Yes', 'Yes', 'No']])}
{run('status_codes')}
{table(['Range', 'Meaning', 'Common codes'], [
    ['1xx', 'Wait, more is coming', '101 Switching Protocols (WebSocket)'],
    ['2xx', 'Success', '200 OK, 201 Created, 204 No Content'],
    ['3xx', 'Look somewhere else', '301 Moved Permanently, 302 Found, 304 Not Modified'],
    ['4xx', 'The client made a mistake', '400 Bad Request, 401 Unauthorized (not logged in), 403 Forbidden (not allowed), 404 Not Found, 409 Conflict, 422 invalid data, 429 Too Many Requests'],
    ['5xx', 'The server failed', '500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout']])}
''', kw=['request line', 'status line', 'headers', 'body', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'safe', 'idempotent', 'status codes', 'HTTPStatus'])

K.lesson('rest', 'REST: designing an API with resources', f'''
{local('book_api', WHY_NET)}
{table(['Action', 'Method and path', 'Success', 'Typical errors'], [
    ['List books', 'GET /books', '200 with a JSON list', ''],
    ['Read one book', 'GET /books/2', '200 with the book', '404 if it does not exist'],
    ['Create a book', 'POST /books with JSON', '201 Created and a Location header', '400 or 422 for bad data'],
    ['Replace a book', 'PUT /books/2 with JSON', '200 or 204', '404, 400'],
    ['Change a book', 'PATCH /books/2 with some fields', '200', '404, 400'],
    ['Delete a book', 'DELETE /books/2', '204 No Content', '404']])}
{steps('Rules of a good REST API', [
    'Paths name <b>things</b> (nouns): /books, /books/2/reviews. The method says the <b>action</b>, so there is no /getBook or /deleteBook.',
    'Use the status code that fits: 201 after creating, 404 for missing, 400 or 422 for bad input, never 200 with an error inside.',
    'Send and accept JSON with Content-Type: application/json, and give errors a JSON body such as {"error": "..."}.',
    'Keep every request <b>stateless</b>: it carries everything the server needs, such as an auth token, so any server in a group can answer it.',
    'Add a version (/v1/books) and paging (?page=2&amp;size=50) before many clients depend on the API.'])}
{note('urllib.request.urlopen raises HTTPError for 4xx and 5xx answers. The requests library in the next chapters does not: it returns the response, and you call raise_for_status() when you want an exception.', 'exam')}
''', kw=['REST', 'resource', 'endpoint', 'JSON API', 'Location header', 'stateless', 'versioning', 'pagination', 'urllib.request', 'HTTPError', 'http.server'])

K.lesson('headers', 'Headers, cookies and caching', f'''
{run('cookies_cache')}
{table(['Header', 'Sent by', 'Does'], [
    ['Host', 'Client', 'Which site on a server with many sites'],
    ['Accept, Content-Type', 'Both', 'Which format is wanted, which format is sent'],
    ['Authorization', 'Client', 'Proves who you are, for example Bearer and a token'],
    ['User-Agent', 'Client', 'Names the program that sends the request'],
    ['Set-Cookie, Cookie', 'Server, then client', 'The server stores a small value in the browser, which sends it back on every request'],
    ['Cache-Control, ETag, If-None-Match', 'Both', 'How long a copy may be kept, its version, and "is my version still right?"'],
    ['Location', 'Server', 'Where a new resource is, or where to go for a redirect'],
    ['Access-Control-Allow-Origin', 'Server', 'Which other websites may call this API from a browser (CORS)']])}
{note('HTTP itself has no memory between requests. Logins work because the server gives the browser a session cookie or a token, and the client sends it back every time. Mark session cookies HttpOnly, Secure and SameSite, as in the example.', 'warn')}
''', kw=['headers', 'Content-Type', 'Accept', 'Authorization', 'User-Agent', 'cookies', 'Set-Cookie', 'session', 'Cache-Control', 'ETag', 'If-None-Match', '304', 'CORS'])

K.lesson('maths', 'The maths: latency, bandwidth and caching', f'''
{fxs(fx('Time to first byte', 'about (TCP 1 + TLS 1 + request 1) round trips &times; RTT', 'RTT 50 ms: 3 &times; 50 = 150 ms before the first byte of the answer, however small it is.', key=True),
     fx('Transfer time', 'time = size &times; 8 / bandwidth', '2 MB at 40 Mbit/s: 16 Mbit / 40 = 0.4 s.'),
     fx('Average time with a cache', 'average = hit rate &times; hit time + (1 &minus; hit rate) &times; miss time', '80 % hits at 5 ms, misses at 200 ms: 0.8 &times; 5 + 0.2 &times; 200 = 44 ms.', key=True),
     fx('Little\'s law', 'requests in progress = arrival rate &times; time per request', '200 requests a second, 50 ms each: 10 requests at the same moment.'),
     fx('Bandwidth delay product', 'bits in flight = bandwidth &times; RTT', '100 Mbit/s and 80 ms: 8 Mbit (1 MB) on the wire at once.'),
     fx('Percent encoding size', 'a byte outside the allowed set becomes 3 characters', '"é" is 2 bytes in UTF-8, so it becomes 6 characters: %C3%A9.'))}
{steps('Worked example: why do small requests feel slow far away?', [
    'A server in another continent has an RTT of 150 ms. A new HTTPS connection needs about 3 round trips: 450 ms.',
    'The answer is only 5 KB. At 50 Mbit/s that takes 40,000 / 50,000,000 s, less than 1 ms.',
    'So almost all the time is waiting for round trips, not sending data.',
    'Keeping the connection open (requests.Session, HTTP keep alive) saves the 2 handshake round trips on later requests: 150 ms instead of 450 ms.',
    eq('Latency, not bandwidth, decides the speed of small requests')])}
''', kw=['latency', 'RTT', 'round trip', 'bandwidth', 'transfer time', 'cache hit rate', 'Little law', 'keep alive'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Read a URL, know GET and POST, the main status codes and what JSON in a body looks like.</p>',
    '<p>Design REST paths and status codes, use headers for content type, auth and caching, and run a small server with http.server.</p>',
    '<p>Understand safe and idempotent methods, conditional requests, cookies and CORS, and measure latency in round trips.</p>',
    '<p>Know HTTP/2 multiplexing and HTTP/3 over QUIC, TLS 1.3, CDNs, caching rules from RFC 9111, and how to design APIs that evolve for years.</p>')}
{grow('Read and send simple requests.', 'Design REST endpoints and use headers well.', 'Tune latency, caching and protocol versions.')}
''', kw=['beginner', 'expert', 'HTTP/2', 'HTTP/3', 'QUIC', 'CDN', 'API design'])

lc(1961, 'Check If String Is a Prefix of Array', 'check-if-string-is-a-prefix-of-array', 'e', 'Join pieces until the text is long enough', 'Like building a URL path from its parts. Add the words one by one and stop as soon as the joined text is as long as s.', r'''
def is_prefix_string(s, words):
    joined = ""
    for word in words:
        joined += word
        if len(joined) >= len(s):
            return joined == s
    return False
''', [('is_prefix_string("iloveleetcode", ["i", "love", "leetcode", "apples"])', True), ('is_prefix_string("iloveleetcode", ["apples", "i", "love", "leetcode"])', False), ('is_prefix_string("/api/books", ["/api", "/books", "/1"])', True)])
lc(1309, 'Decrypt String from Alphabet to Integer Mapping', 'decrypt-string-from-alphabet-to-integer-mapping', 'e', 'Look two places ahead for #', 'This is decoding, like reading %20 in a URL. If the character two places ahead is #, read two digits, otherwise one.', r'''
def freq_alphabets(s):
    result = []
    i = 0
    while i < len(s):
        if i + 2 < len(s) and s[i + 2] == "#":
            number = int(s[i:i + 2])
            i += 3
        else:
            number = int(s[i])
            i += 1
        result.append(chr(ord("a") + number - 1))
    return "".join(result)
''', [('freq_alphabets("10#11#12")', 'jkab'), ('freq_alphabets("1326#")', 'acz')])
lc(1773, 'Count Items Matching a Rule', 'count-items-matching-a-rule', 'e', 'Pick the column by its name', 'Like a query string such as ?color=silver filtering records. Map the rule key to a column index with a dict.', r'''
def count_matches(items, rule_key, rule_value):
    column = {"type": 0, "color": 1, "name": 2}[rule_key]
    return sum(1 for item in items if item[column] == rule_value)
''', [('count_matches([["phone", "blue", "pixel"], ["computer", "silver", "lenovo"], ["phone", "gold", "iphone"]], "color", "silver")', 1), ('count_matches([["phone", "blue", "pixel"], ["computer", "silver", "phone"], ["phone", "gold", "iphone"]], "type", "phone")', 2)])
lc(2185, 'Counting Words With a Given Prefix', 'counting-words-with-a-given-prefix', 'e', 'str.startswith', 'Routers match URL paths by prefix in the same way. Count the words that start with the prefix.', r'''
def prefix_count(words, pref):
    return sum(1 for word in words if word.startswith(pref))
''', [('prefix_count(["pay", "attention", "practice", "attend"], "at")', 2), ('prefix_count(["leetcode", "win", "loops", "success"], "code")', 0)])
lc(811, 'Subdomain Visit Count', 'subdomain-visit-count', 'm', 'Every suffix of a host name', 'A visit to discuss.leetcode.com also counts for leetcode.com and com. Split on dots and add the count to every ending with a Counter.', r'''
from collections import Counter


def subdomain_visits(cpdomains):
    counts = Counter()
    for entry in cpdomains:
        number, domain = entry.split()
        parts = domain.split(".")
        for i in range(len(parts)):
            counts[".".join(parts[i:])] += int(number)
    return sorted(f"{count} {name}" for name, count in counts.items())
''', [('subdomain_visits(["9001 discuss.leetcode.com"])', ['9001 com', '9001 discuss.leetcode.com', '9001 leetcode.com']), ('subdomain_visits(["900 google.mail.com", "50 yahoo.com", "1 intel.mail.com", "5 wiki.org"])', ['1 intel.mail.com', '5 org', '5 wiki.org', '50 yahoo.com', '900 google.mail.com', '901 mail.com', '951 com'])])
lc(93, 'Restore IP Addresses', 'restore-ip-addresses', 'm', 'Try every split into four parts', 'Each part is 0 to 255 with no leading zero, like a real IPv4 address. Try lengths 1, 2 and 3 for each of the four parts.', r'''
def restore_ip_addresses(s):
    found = []

    def valid(part):
        return part == "0" or (part[0] != "0" and int(part) <= 255)

    def build(start, parts):
        if len(parts) == 4:
            if start == len(s):
                found.append(".".join(parts))
            return
        for length in (1, 2, 3):
            part = s[start:start + length]
            if len(part) == length and valid(part):
                build(start + length, parts + [part])

    build(0, [])
    return found
''', [('restore_ip_addresses("25525511135")', ['255.255.11.135', '255.255.111.35']), ('restore_ip_addresses("0000")', ['0.0.0.0']), ('restore_ip_addresses("101023")', ['1.0.10.23', '1.0.102.3', '10.1.0.23', '10.10.2.3', '101.0.2.3'])])
lc(1268, 'Search Suggestions System', 'search-suggestions-system', 'm', 'Sort once, then filter by the growing prefix', 'This is what a search box API returns while you type. Sort the products, and for each typed prefix keep the first three that start with it.', r'''
def suggested_products(products, search_word):
    products = sorted(products)
    result = []
    prefix = ""
    for ch in search_word:
        prefix += ch
        matches = [p for p in products if p.startswith(prefix)]
        result.append(matches[:3])
    return result
''', [('suggested_products(["mobile", "mouse", "moneypot", "monitor", "mousepad"], "mouse")', [['mobile', 'moneypot', 'monitor'], ['mobile', 'moneypot', 'monitor'], ['mouse', 'mousepad'], ['mouse', 'mousepad'], ['mouse', 'mousepad']])])
lc(2284, 'Sender With Largest Word Count', 'sender-with-largest-word-count', 'm', 'A Counter, then max with a tuple key', 'Count the words each sender wrote. Pick the largest count, and on a tie the name that is largest in alphabetical order: max by (count, name).', r'''
from collections import Counter


def largest_word_count(messages, senders):
    words = Counter()
    for message, sender in zip(messages, senders):
        words[sender] += len(message.split())
    return max(words, key=lambda name: (words[name], name))
''', [('largest_word_count(["Hello userTwooo", "Hi userThree", "Wonderful day Alice", "Nice day userThree"], ["Alice", "userTwo", "userThree", "Alice"])', 'Alice'), ('largest_word_count(["How is leetcode for everyone", "Leetcode is useful for practice"], ["Bob", "Charlie"])', 'Charlie')])
lc(140, 'Word Break II', 'word-break-ii', 'h', 'Recursion with a cache of endings', 'All the ways to cut a string into dictionary words. sentences(start) returns every sentence for s[start:], and functools.cache remembers each answer.', r'''
from functools import cache


def word_break(s, word_dict):
    words = set(word_dict)

    @cache
    def sentences(start):
        if start == len(s):
            return [""]
        found = []
        for end in range(start + 1, len(s) + 1):
            word = s[start:end]
            if word in words:
                for rest in sentences(end):
                    found.append(word + (" " + rest if rest else ""))
        return found

    return sorted(sentences(0))
''', [('word_break("catsanddog", ["cat", "cats", "and", "sand", "dog"])', ['cat sand dog', 'cats and dog']), ('word_break("pineapplepenapple", ["apple", "pen", "applepen", "pine", "pineapple"])', ['pine apple pen apple', 'pine applepen apple', 'pineapple pen apple']), ('word_break("catsandog", ["cats", "dog", "sand", "and", "cat"])', [])])
lc(301, 'Remove Invalid Parentheses', 'remove-invalid-parentheses', 'h', 'Breadth first search by number of removals', 'Check all strings with one character removed, then two, and so on. The first level that has valid strings gives the answer with the fewest removals.', r'''
def remove_invalid_parentheses(s):
    def valid(text):
        depth = 0
        for ch in text:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth < 0:
                    return False
        return depth == 0

    level = {s}
    while True:
        good = [text for text in level if valid(text)]
        if good:
            return sorted(good)
        next_level = set()
        for text in level:
            for i in range(len(text)):
                if text[i] in "()":
                    next_level.add(text[:i] + text[i + 1:])
        level = next_level
''', [('remove_invalid_parentheses("()())()")', ['(())()', '()()()']), ('remove_invalid_parentheses("(a)())()")', ['(a())()', '(a)()()']), ('remove_invalid_parentheses(")(")', [''])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Web code reads and checks a lot of text: URL paths, host names, IP addresses, query filters, search box suggestions and messages. These problems practise exactly that kind of parsing.</p>'), kw=['LeetCode', 'parsing', 'prefix', 'IP address', 'domain', 'autocomplete', 'Counter', 'backtracking', 'BFS'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'HTTP is a request (method, path, headers, optional body) and a response (status, headers, body) as text lines over TCP. HTTPS adds TLS encryption.',
    'A URL has a scheme, host, port, path, query and fragment. Build query strings with urlencode, never by hand.',
    'GET reads, POST creates, PUT replaces, PATCH changes, DELETE removes. GET, PUT and DELETE are idempotent, POST is not.',
    'Status codes: 2xx success, 3xx redirect, 4xx client mistake, 5xx server failure. REST paths are nouns, methods are verbs.',
    'Headers carry the content type, auth tokens, cookies and caching rules. ETag with If-None-Match gives a cheap 304.'],
    'Next: what is under HTTP, with sockets, TCP and UDP.')}
{files('Three tasks: read a query string correctly, describe status codes and decide when to retry, and parse a raw HTTP request into its parts.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which HTTP method is used to read a resource without changing it?', ['POST', 'GET', 'DELETE', 'PATCH'], 1, 'Read.', 'GET is safe: it should never change data on the server.')
K.quiz('e', 'What does status code 404 mean?', ['Server error', 'Not Found', 'Created', 'Redirect'], 1, '4xx is the client side.', 'The URL points to nothing on that server.')
K.quiz('e', 'Which part of https://shop.com/cart?id=5#top is never sent to the server?', ['/cart', 'id=5', '#top', 'shop.com'], 2, 'The browser keeps it.', 'The fragment only moves the view inside the page.')
K.quiz('m', 'Which status code fits best after a POST created a new order?', ['200 OK', '201 Created', '204 No Content', '302 Found'], 1, 'Something new exists.', 'Also send a Location header with the address of the new order.')
K.quiz('m', 'Which of these methods is NOT idempotent?', ['GET', 'PUT', 'DELETE', 'POST'], 3, 'Repeat it twice.', 'Two identical POSTs usually create two resources.')
K.quiz('m', 'What separates the headers from the body in an HTTP message?', ['A comma', 'An empty line', 'The word BODY', 'A semicolon'], 1, '&#92;r&#92;n twice in a row.', 'That is why HTTP needs Content-Length (or chunked encoding) to know where the body ends.')
K.quiz('m', 'urllib.request.urlopen gets a 404 answer. What happens?', ['It returns the response', 'It raises urllib.error.HTTPError', 'It returns None', 'It retries'], 1, 'urllib raises for 4xx and 5xx.', 'The requests library returns the response instead, and you call raise_for_status().')
K.quiz('m', 'What does a 304 Not Modified answer contain?', ['The full page', 'No body: the client uses its cached copy', 'An error message', 'A redirect URL'], 1, 'Conditional request.', 'It answers a request with If-None-Match or If-Modified-Since.')
K.quiz('m', 'Which header says the format of the body you send?', ['Accept', 'Content-Type', 'Host', 'Location'], 1, 'Type of the content.', 'Accept says which format you want back.')
K.quiz('h', 'What is the difference between 401 and 403?', ['None', '401: not logged in or the credentials are wrong, 403: logged in but not allowed', '401 is for servers, 403 for clients', '403 means the page moved'], 1, 'Who are you, and may you.', '401 is about authentication, 403 about authorisation.')
K.quiz('h', 'Why should a REST API be stateless?', ['To use less memory', 'Each request carries all it needs, so any server can answer it and servers can be added freely', 'Because HTTP forbids sessions', 'To avoid JSON'], 1, 'Scaling.', 'State such as the user goes in a token or in the database, not in the memory of one server.')
K.quiz('x', 'In the style of a Stanford CS 144 exam: with HTTP/1.1 a browser opens 6 connections, each fetching one file per round trip. How long do 30 small files take at RTT 100 ms, compared with one HTTP/2 connection that sends all requests at once?', ['Both 100 ms', 'About 500 ms with HTTP/1.1, about 100 ms with HTTP/2', '3 s and 100 ms', 'HTTP/2 is slower'], 1, '30 / 6 = 5 rounds.', 'HTTP/2 multiplexes many requests on one connection, so the files share the same round trip.')
K.quiz('x', 'In the style of an MIT 6.033 exam: a client retries a POST /payments after a timeout, but the first request did reach the server. How do good APIs stop a double payment?', ['They cannot', 'The client sends an idempotency key, and the server ignores a second request with the same key', 'Use GET instead', 'Use a shorter timeout'], 1, 'Make POST safe to retry.', 'Payment APIs keep each key and its first result for some time.')

K.calc('e', 'How many characters is the body {"id": 1} as written by json.dumps?', '9', 'Count every character.', ['{"id": 1}', 'Braces, quotes, colon, space, digit.', eq('9')], check=len('{"id": 1}'))
K.calc('e', 'A new HTTPS connection needs 3 round trips before the first byte. The RTT is 50 ms. How many ms is that?', '150', '3 &times; 50.', ['TCP, TLS, request.', '3 &times; 50.', eq('150 ms')], check=3 * 50)
K.calc('e', 'How many characters does percent encoding make of the 2 byte letter é?', '6', 'Each byte becomes 3 characters.', ['%C3 and %A9.', '2 &times; 3.', eq('6')], check=len('%C3%A9'))
K.calc('m', 'How many seconds does a 2 MB file take at 40 Mbit/s (1 MB = 8 Mbit)?', '0.4', 'size &times; 8 / bandwidth.', ['2 MB = 16 Mbit.', '16 / 40.', eq('0.4 s')], check=16 / 40)
K.calc('m', 'A cache answers 80 % of requests in 5 ms, the rest take 200 ms. What is the average in ms?', '44', 'Weighted average.', ['0.8 &times; 5 = 4.', '0.2 &times; 200 = 40.', eq('44 ms')], check=0.8 * 5 + 0.2 * 200)
K.calc('m', '200 requests arrive each second and each takes 0.05 s. How many are in progress on average?', '10', 'Little\'s law.', ['L = &lambda; &times; W.', '200 &times; 0.05.', eq('10')], check=200 * 0.05)
K.calc('m', 'A request fails with probability 0.1 and is tried at most 3 times. What is the expected number of tries?', '1.11', '1 + p + p².', ['Always 1 try.', 'A 2nd with 0.1, a 3rd with 0.01.', eq('1.11')], check=round(1 + 0.1 + 0.01, 2))
K.calc('h', 'How many megabytes are in flight at 100 Mbit/s with an RTT of 80 ms?', '1', 'bandwidth &times; RTT.', ['100 Mbit/s &times; 0.08 s = 8 Mbit.', '8 Mbit / 8.', eq('1 MB')], check=100 * 0.08 / 8)
K.calc('h', 'Base64 for HTTP Basic auth: how many characters is the encoding of the 6 bytes "ann:pw"?', '8', '4 &times; &lceil;n / 3&rceil;.', ['6 / 3 = 2 groups.', '4 characters each.', eq('8')], check=len(__import__('base64').b64encode(b'ann:pw')))
K.calc('x', 'In the style of a Stanford CS 144 exam: 30 small files, 6 HTTP/1.1 connections, one file per connection per round trip, RTT 100 ms. How many ms are saved by one HTTP/2 connection that needs a single round trip?', '400', '5 rounds against 1.', ['30 / 6 = 5 rounds = 500 ms.', 'HTTP/2: 100 ms.', eq('400 ms saved')], check=(30 // 6) * 100 - 100)

K.assign('querystring', 'e', 'Read a query string correctly',
         '<p>Write <code>parse_query(query)</code> that turns a query string such as "q=hello%20world&amp;page=2" into a dict of names and values. Decode percent encoding and + as a space, keep names without a value as "" and, when a name appears twice, keep the last value. Use urllib.parse.parse_qsl with keep_blank_values=True.</p>',
         '''
def parse_query(query):
    result = {}
    for pair in query.split("&"):
        name, value = pair.split("=")
        result[name] = value
    return result
''', [('parse_query("page=2&size=10")', {'page': '2', 'size': '10'}), ('parse_query("q=hello%20world")', {'q': 'hello world'}), ('parse_query("q=fish+%26+chips")', {'q': 'fish & chips'}), ('parse_query("debug&page=3")', {'debug': '', 'page': '3'}), ('parse_query("")', {})],
         '''
from urllib.parse import parse_qsl


def parse_query(query):
    result = {}
    for name, value in parse_qsl(query, keep_blank_values=True):
        result[name] = value
    return result
''', 'Splitting by hand misses %20, + and names without "=". parse_qsl does all of that, and keep_blank_values=True keeps "debug".', '<p>Frameworks such as Flask (request.args) and Django (request.GET) do this parsing for you, with the same rules.</p>')
K.assign('statuses', 'm', 'Describe status codes and decide when to retry',
         '<p>Write <code>describe(code)</code> that returns text like "404 Not Found (client error)" with the kinds success, redirect, client error and server error, and raises ValueError for a number that is not a known HTTP status. Also write <code>should_retry(code)</code>: True only for 408, 429, 500, 502, 503 and 504, because other errors will fail again in the same way. Use http.HTTPStatus.</p>',
         '''
from http import HTTPStatus


def describe(code):
    return f"{code} {HTTPStatus(code).phrase}"


def should_retry(code):
    return code >= 400


def unknown_code(code):
    try:
        describe(code)
    except ValueError:
        return "ValueError"
    return "no error"
''', [('describe(404)', '404 Not Found (client error)'), ('describe(201)', '201 Created (success)'), ('describe(503)', '503 Service Unavailable (server error)'), ('describe(301)', '301 Moved Permanently (redirect)'), ("unknown_code(299)", 'ValueError'), ('[c for c in (400, 404, 408, 429, 500, 501, 503) if should_retry(c)]', [408, 429, 500, 503])],
         '''
from http import HTTPStatus

RETRY = {408, 429, 500, 502, 503, 504}


def describe(code):
    status = HTTPStatus(code)            # raises ValueError for unknown codes
    if 200 <= code < 300:
        kind = "success"
    elif 300 <= code < 400:
        kind = "redirect"
    elif 400 <= code < 500:
        kind = "client error"
    else:
        kind = "server error"
    return f"{code} {status.phrase} ({kind})"


def should_retry(code):
    return code in RETRY


def unknown_code(code):
    try:
        describe(code)
    except ValueError:
        return "ValueError"
    return "no error"
''', 'HTTPStatus(code) already raises ValueError for unknown numbers. Add the kind from the first digit. Retry only temporary problems: timeouts (408), rate limits (429) and some server errors.', '<p>Retrying a 400 or 404 only repeats the same mistake, and retrying 501 Not Implemented never helps. Real clients also wait longer between each retry.</p>')
K.assign('rawrequest', 'h', 'Parse a raw HTTP request',
         '<p>Write <code>parse_request(raw)</code> for the text of a request. Lines end with &#92;r&#92;n and a blank line separates the headers from the body. Return a dict with method, path (without the query), query (a dict, like in the first task), version, headers (a dict with lower case names) and body (the first Content-Length characters after the blank line, or "" when there is no Content-Length). Raise ValueError when the request line does not have exactly three parts or the version does not start with "HTTP/".</p>',
         '''
def parse_request(raw):
    lines = raw.split("\\n")
    method, path, version = lines[0].split()
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            name, value = line.split(":", 1)
            headers[name] = value.strip()
    return {"method": method, "path": path, "query": {}, "version": version, "headers": headers, "body": ""}


def error_of(raw):
    try:
        parse_request(raw)
    except ValueError:
        return "ValueError"
    return "no error"


GET = "GET /books?page=2&q=sci%20fi HTTP/1.1\\r\\nHost: shop.com\\r\\nAccept: application/json\\r\\n\\r\\n"
POST = "POST /books HTTP/1.1\\r\\nHost: shop.com\\r\\nContent-Type: application/json\\r\\nContent-Length: 17\\r\\n\\r\\n{\\"title\\": \\"Emma\\"}"
''', [('parse_request(GET)', {'method': 'GET', 'path': '/books', 'query': {'page': '2', 'q': 'sci fi'}, 'version': 'HTTP/1.1', 'headers': {'host': 'shop.com', 'accept': 'application/json'}, 'body': ''}), ('parse_request(POST)["body"]', '{"title": "Emma"}'), ('parse_request(POST)["headers"]["content-length"]', '17'), ('error_of("GET /books\\r\\n\\r\\n")', 'ValueError'), ('error_of("GET /books FTP/1.0\\r\\n\\r\\n")', 'ValueError')],
         '''
from urllib.parse import parse_qsl


def parse_request(raw):
    head, _, rest = raw.partition("\\r\\n\\r\\n")
    lines = head.split("\\r\\n")
    parts = lines[0].split()
    if len(parts) != 3 or not parts[2].startswith("HTTP/"):
        raise ValueError(f"bad request line: {lines[0]!r}")
    method, target, version = parts
    path, _, query_text = target.partition("?")
    query = {}
    for name, value in parse_qsl(query_text, keep_blank_values=True):
        query[name] = value
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()
    length = int(headers.get("content-length", 0))
    return {"method": method, "path": path, "query": query, "version": version, "headers": headers, "body": rest[:length]}


def error_of(raw):
    try:
        parse_request(raw)
    except ValueError:
        return "ValueError"
    return "no error"


GET = "GET /books?page=2&q=sci%20fi HTTP/1.1\\r\\nHost: shop.com\\r\\nAccept: application/json\\r\\n\\r\\n"
POST = "POST /books HTTP/1.1\\r\\nHost: shop.com\\r\\nContent-Type: application/json\\r\\nContent-Length: 17\\r\\n\\r\\n{\\"title\\": \\"Emma\\"}"
''', 'partition("&#92;r&#92;n&#92;r&#92;n") splits the head from the body. Check the request line before unpacking it, lower case the header names (HTTP header names ignore case), and use Content-Length to cut the body.', '<p>This is roughly what http.server, Flask and Django do with every request before your code sees it. Real servers also limit sizes, so that a huge Content-Length cannot fill the memory.</p>')

K.must('Messages', 'Request line (method, path, version), headers, blank line, body. Status line, headers, blank line, body. &#92;r&#92;n line ends.')
K.must('Methods and codes', 'GET read, POST create (201 + Location), PUT replace, PATCH change, DELETE (204). 2xx ok, 3xx redirect, 4xx client, 5xx server.')
K.must('URLs', 'urlsplit, parse_qs, parse_qsl, urlencode, quote, urljoin. Percent encoding: one byte becomes %XX.')
K.must('Headers', 'Content-Type, Accept, Authorization, Set-Cookie (HttpOnly, Secure, SameSite), Cache-Control, ETag and If-None-Match for 304.')
K.must('Python', 'http.server.BaseHTTPRequestHandler (do_GET, send_response, send_header, end_headers, wfile), urllib.request, HTTPError for 4xx and 5xx.')

T = K.topic(
    slug='py-http', topic='py-http', step=(1, 'How the web works: HTTP, REST and sockets', 'py-w1', 'See what really travels between a program and a server: HTTP requests and responses, REST design, and the sockets underneath.', 'Intermediate'),
    title='HTTP and REST: how the web talks', short='HTTP and REST', badge='1.1', minutes=90,
    lead='See exactly what a program and a server send each other. Learn URLs, methods, status codes and headers, build a small JSON API with http.server, and learn the rules of REST design and caching.',
    desc='URLs and urllib.parse, percent encoding, the HTTP request and response format, methods, safe and idempotent methods, status codes and HTTPStatus, headers, cookies, caching with ETag and 304, REST resources and status codes, a JSON API with http.server and urllib.request, latency, bandwidth and cache maths.',
    summary='HTTP messages, URLs, methods, status codes, headers, cookies, caching and REST design.',
    keywords=['HTTP', 'REST', 'URL', 'status codes', 'headers', 'cookies', 'caching', 'http.server', 'urllib', 'JSON API'],
    recap='<p>A request names a resource and an action, a response gives a status and the data. Everything else, cookies, caching and auth, travels in headers.</p>',
    added='2026-11-07', leet=leet_items())
