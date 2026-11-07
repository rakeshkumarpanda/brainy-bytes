# Web and APIs 2.2: real API work. Checked against the requests 2.34 and urllib3 2.x documentation (HTTPAdapter,
# Retry with backoff_factor, status_forcelist, allowed_methods, respect_retry_after_header), RFC 9110 (Retry-After,
# 429 from RFC 6585, idempotent methods), the httpx 0.28 documentation (Client, AsyncClient, limits), the pydantic 2
# documentation (BaseModel, Field, TypeAdapter, ValidationError) and the AWS Architecture Blog article "Exponential
# Backoff And Jitter". Network programs start a tiny practice API on 127.0.0.1 and use local().
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, lc, leet, files, grow, leet_items

chapter('py-api-data')
K = Kit()

K.code('pagination', r'''
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import requests

# ---------- A tiny practice API with page numbers and with cursors ----------
ITEMS = [f"item{n}" for n in range(1, 8)]      # newest first: item1 is the newest


class PracticeAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlsplit(self.path)
        query = {name: values[0] for name, values in parse_qs(url.query).items()}
        size = int(query.get("size", 3))
        if url.path == "/pages":                 # ?page=1&size=3
            page = int(query.get("page", 1))
            start = (page - 1) * size
            data = {"items": ITEMS[start:start + size], "page": page,
                    "pages": (len(ITEMS) + size - 1) // size}
        else:                                    # /cursor?after=item3&size=3
            after = query.get("after")
            start = ITEMS.index(after) + 1 if after else 0
            chunk = ITEMS[start:start + size]
            more = start + size < len(ITEMS)
            data = {"items": chunk, "next": chunk[-1] if more else None}
        body = json.dumps(data).encode()
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

# ---------- The part to learn: generators that walk through every page ----------
def by_page(session, size=3):
    page = 1
    while True:
        data = session.get(BASE + "/pages", params={"page": page, "size": size}, timeout=5).json()
        yield from data["items"]
        if page >= data["pages"]:
            return
        page += 1


def by_cursor(session, size=3):
    after = None
    while True:
        params = {"size": size}
        if after:
            params["after"] = after
        data = session.get(BASE + "/cursor", params=params, timeout=5).json()
        yield from data["items"]
        after = data["next"]
        if after is None:
            return


with requests.Session() as session:
    print("pages: ", list(by_page(session)))
    print("cursor:", list(by_cursor(session)))

    # A new item arrives while we read. Page numbers shift, cursors do not.
    pages = by_page(session)
    first = [next(pages) for _ in range(3)]
    ITEMS.insert(0, "item0")
    print("pages while adding: ", first + list(pages))

    ITEMS.remove("item0")
    cursor = by_cursor(session)
    first = [next(cursor) for _ in range(3)]
    ITEMS.insert(0, "item0")
    print("cursor while adding:", first + list(cursor))
server.shutdown()
''', long=True)
K.code('retries', r'''
import json
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------- A tiny practice API that fails a few times before it works ----------
calls = {"/flaky": 0, "/limited": 0, "/auto": 0}


class PracticeAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        calls[self.path] += 1
        n = calls[self.path]
        if self.path in ("/flaky", "/auto") and n <= 2:
            status, extra = 503, {}
        elif self.path == "/limited" and n == 1:
            status, extra = 429, {"Retry-After": "1"}
        else:
            status, extra = 200, {}
        body = json.dumps({"try": n}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for name, value in extra.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), PracticeAPI)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_address[1]}"

# ---------- The part to learn: retries with backoff, jitter and Retry-After ----------
RETRY_STATUS = {429, 500, 502, 503, 504}


def get_with_retries(session, url, tries=4, base=0.1, cap=2.0):
    for attempt in range(tries):
        try:
            r = session.get(url, timeout=5)
            if r.status_code not in RETRY_STATUS:
                return r
            reason = r.status_code
            told = r.headers.get("Retry-After")
        except (requests.ConnectionError, requests.Timeout) as err:
            reason, told = type(err).__name__, None
        if attempt == tries - 1:
            break
        if told:
            wait = float(told)                                     # the server said how long
        else:
            wait = random.uniform(0, min(cap, base * 2 ** attempt))   # backoff with full jitter
        print(f"  try {attempt + 1} got {reason}, waiting {wait:.2f} s")
        time.sleep(wait)
    raise RuntimeError(f"gave up after {tries} tries")


random.seed(7)
with requests.Session() as session:
    print("flaky:", get_with_retries(session, BASE + "/flaky").json())
    start = time.perf_counter()
    print("limited:", get_with_retries(session, BASE + "/limited").json(),
          f"after {time.perf_counter() - start:.1f} s")

    # The same idea built into requests: mount an HTTPAdapter with a urllib3 Retry
    retry = Retry(total=3, backoff_factor=0.05, status_forcelist=sorted(RETRY_STATUS),
                  allowed_methods={"GET", "HEAD", "PUT", "DELETE"}, respect_retry_after_header=True)
    session.mount("http://", HTTPAdapter(max_retries=retry))
    r = session.get(BASE + "/auto", timeout=5)
    print("auto:", r.status_code, r.json(), "server saw", calls["/auto"], "requests")
server.shutdown()
''', long=True)
K.code('token_bucket', r'''
class TokenBucket:
    """Allows `rate` requests per second on average, with bursts of up to `capacity`."""

    def __init__(self, rate, capacity):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity          # start full
        self.last = 0.0

    def allow(self, now):
        passed = now - self.last
        self.tokens = min(self.capacity, self.tokens + passed * self.rate)    # refill
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


bucket = TokenBucket(rate=2, capacity=3)      # 2 requests a second, bursts of 3
for t in [0.0, 0.1, 0.2, 0.3, 0.4, 1.0, 1.1, 1.2, 3.0, 3.0, 3.0, 3.0]:
    answer = "200 allowed" if bucket.allow(t) else "429 Too Many Requests"
    print(f"t = {t:.1f} s  {answer:22}  tokens left {bucket.tokens:.1f}")


def wait_needed(tokens, rate):
    """How long a client should wait before the next token is ready."""
    return 0.0 if tokens >= 1 else (1 - tokens) / rate


print("wait for the next token:", wait_needed(bucket.tokens, bucket.rate), "s")
''')
K.code('validate', r'''
from pydantic import BaseModel, Field, TypeAdapter, ValidationError


class Author(BaseModel):
    name: str
    born: int | None = None


class Book(BaseModel):
    id: int
    title: str = Field(min_length=1)
    year: int = Field(ge=0, le=2100)
    tags: list[str] = []
    author: Author


good = {"id": "7", "title": "Dune", "year": 1965, "extra": "ignored",
        "author": {"name": "Frank Herbert", "born": 1920}}
book = Book.model_validate(good)
print(book.id, type(book.id).__name__, book.title, book.author.name, book.tags)
print(book.model_dump())

bad = {"id": "seven", "title": "", "year": 3000, "author": {}}
try:
    Book.model_validate(bad)
except ValidationError as err:
    print(err.error_count(), "problems:")
    for problem in err.errors():
        where = ".".join(str(part) for part in problem["loc"])
        print(" ", where, "-", problem["msg"])

text = '[{"id": 1, "title": "Emma", "year": 1815, "author": {"name": "Jane Austen"}}]'
books = TypeAdapter(list[Book]).validate_json(text)        # straight from the JSON text of a response
print(len(books), books[0].title, books[0].author.born)
print(Book.model_json_schema()["required"])
''')
K.code('httpx_async', r'''
import asyncio
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx

# ---------- A tiny practice API where every answer takes 0.2 seconds ----------
class SlowAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(0.2)
        number = int(self.path.rsplit("/", 1)[1])
        body = json.dumps({"id": number, "square": number * number}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), SlowAPI)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_address[1]}"

# ---------- The part to learn: the same 5 calls, one by one and at the same time ----------
NUMBERS = range(1, 6)

with httpx.Client(base_url=BASE, timeout=5) as client:          # works like requests.Session
    start = time.perf_counter()
    squares = [client.get(f"/numbers/{n}").json()["square"] for n in NUMBERS]
    print("one by one:     ", squares, f"{time.perf_counter() - start:.1f} s")


async def fetch_all(client, limit):
    gate = asyncio.Semaphore(limit)                # at most `limit` calls at the same time

    async def fetch(n):
        async with gate:
            r = await client.get(f"/numbers/{n}")
            r.raise_for_status()
            return r.json()["square"]

    return await asyncio.gather(*(fetch(n) for n in NUMBERS))


async def main():
    async with httpx.AsyncClient(base_url=BASE, timeout=5) as client:
        for limit in (5, 2):
            start = time.perf_counter()
            squares = await fetch_all(client, limit)
            print(f"async, {limit} at a time:", squares, f"{time.perf_counter() - start:.1f} s")


asyncio.run(main())
server.shutdown()
''', long=True)

WHY_NET = 'It talks to a small server on your own computer, and the Python inside this page has no network sockets. Install the libraries once with <code>pip install requests httpx</code>.'

K.lesson('idea', 'What changes when an API is real', f'''
{src('requests, urllib3 Retry, httpx and pydantic 2 documentation, RFC 9110 and RFC 6585 (429 and Retry-After), and the AWS Architecture Blog article on exponential backoff and jitter.')}
{wwh('Real APIs are bigger and less polite than examples. Answers come in <b>pages</b>, servers sometimes fail for a moment, they <b>limit</b> how many calls you may make, and the data does not always have the shape the documentation promises. Real API work means handling all four.',
     'A script that reads only the first page misses data. A script that gives up after one 503 fails for no good reason. One that retries too fast makes the outage worse or gets blocked. One that trusts every field crashes deep inside the program on the first odd record.',
     'Loop over pages with a generator, retry only temporary errors with exponential backoff and random jitter, respect 429 and Retry-After, check the data at the door with pydantic, and use an async client such as httpx when you need many calls at once.')}
{viz('pyretry')}
{versus('Ways to retry a failed call', ['', 'No retry', 'Fixed wait', 'Exponential backoff', 'Backoff with jitter'], [
    ['Waits', 'None', '1, 1, 1 s', '1, 2, 4, 8 s', 'random(0, 1), random(0, 2), random(0, 4) s'],
    ['A short outage', 'Fails', 'Recovers', 'Recovers', 'Recovers'],
    ['Many clients at once', 'Fail together', 'Retry together, keep the server down', 'Less load, still together', 'Spread out, the server recovers'],
    ['Use it for', 'Requests that must not repeat', 'Rarely a good choice', 'A single client', 'Almost everything']],
    'Use exponential backoff with jitter, a maximum wait, a maximum number of tries, and only for errors that may go away.')}
''', kw=['pagination', 'retries', 'backoff', 'jitter', 'rate limit', '429', 'validation', 'pydantic', 'httpx', 'async'])

K.lesson('paging', 'Pagination: getting every page', f'''
{local('pagination', WHY_NET)}
{table(['Style', 'The request', 'Good', 'Weak'], [
    ['Page number', '?page=3&amp;size=50', 'Simple, can jump to any page', 'Items shift when data changes, so you can see one twice or miss one'],
    ['Offset and limit', '?offset=100&amp;limit=50', 'The same as pages, in rows', 'Slow for big offsets, the database still skips every row'],
    ['Cursor', '?after=item3 or ?cursor=eyJpZCI6...', 'Stable while data changes, fast', 'Cannot jump to page 40'],
    ['Link header', '<code>Link: &lt;...?page=4&gt;; rel="next"</code>', 'The server gives the next URL', 'You must read the header (requests: r.links["next"]["url"])']])}
{note('Write the loop as a <b>generator</b> with yield from. The caller sees one long stream of items and can stop early, and pages are only fetched when they are needed.', 'tip')}
''', kw=['pagination', 'page', 'offset', 'limit', 'cursor', 'Link header', 'generator', 'yield from', 'r.links'])

K.lesson('retries', 'Retries with backoff, jitter and Retry-After', f'''
{local('retries', WHY_NET)}
{table(['Retry?', 'Status or error', 'Why'], [
    ['Yes', 'ConnectionError, Timeout', 'The network or the server had a short problem'],
    ['Yes', '429 Too Many Requests', 'Wait as long as Retry-After says, then try again'],
    ['Yes', '502, 503, 504, sometimes 500', 'A server or a gateway is busy or restarting'],
    ['No', '400, 401, 403, 404, 422', 'The request itself is wrong, it will fail the same way again'],
    ['Careful', 'POST and PATCH', 'Not idempotent: the first try may have worked. Retry only with an idempotency key']])}
{steps('Rules for good retries', [
    'Retry only temporary errors, and only for safe or idempotent requests.',
    'Wait base &times; 2<sup>attempt</sup>, pick a random wait between 0 and that number (full jitter), and never more than a cap such as 30 s.',
    'If the server sends Retry-After, wait exactly that long.',
    'Stop after a fixed number of tries and raise a clear error, so the caller knows.',
    'With requests you can mount <code>HTTPAdapter(max_retries=Retry(...))</code> on a Session, and urllib3 does all of this for you.'])}
''', kw=['retry', 'exponential backoff', 'jitter', 'Retry-After', '429', '503', 'idempotent', 'urllib3 Retry', 'HTTPAdapter', 'backoff_factor'])

K.lesson('limits', 'Rate limits: the token bucket', f'''
{run('token_bucket')}
{table(['Header', 'Meaning'], [
    ['Retry-After: 30', 'Wait 30 seconds before the next call (it can also be a date)'],
    ['X-RateLimit-Limit: 5000', 'How many calls you may make in the current window'],
    ['X-RateLimit-Remaining: 12', 'How many are left'],
    ['X-RateLimit-Reset: 1793000000', 'When the window starts again, often as a Unix time'],
    ['RateLimit-Policy, RateLimit', 'Newer standard names for the same ideas (an IETF draft)']])}
{scene('a script that syncs orders every night', '<p>A shop syncs 20,000 orders from a partner API that allows 10 calls per second. The script keeps its own token bucket with rate 10, so it never sends faster than allowed. When the partner is busy and sends 429 with Retry-After: 5, the script waits 5 seconds and goes on. The sync takes about 35 minutes and never gets the API key blocked.</p>')}
{note('A token bucket holds up to capacity tokens and refills rate tokens every second. Each call takes one token, and with no token the call must wait or gets 429. So it allows short bursts but keeps the average at the rate. Servers use it to protect themselves, and clients can use it to stay polite.', 'exam')}
''', kw=['rate limit', 'token bucket', 'burst', 'X-RateLimit-Remaining', 'Retry-After', 'throttling', '429'])

K.lesson('validate', 'Checking the data with pydantic', f'''
{run('validate')}
{versus('Ways to check an API answer', ['', 'Trust it', 'Checks by hand', 'dataclass', 'pydantic'], [
    ['Wrong type, such as "seven" for an int', 'Crashes later, far away', 'Found if you wrote the check', 'Not found', 'Found at once with a clear message'],
    ['"7" for an int', 'Stays a str', 'Your choice', 'Stays a str', 'Turned into 7 (lax mode)'],
    ['Missing field', 'KeyError somewhere', 'Found if you wrote the check', 'TypeError when you build it', 'Listed with its path, such as author.name'],
    ['Nested objects and lists', 'Plain dicts', 'Much code', 'By hand', 'Built in'],
    ['Cost', 'None', 'Many lines', 'Few lines', 'One class, a fast core written in Rust']],
    'Check data where it enters your program. pydantic is the usual choice, and FastAPI uses it for every request (step 5).')}
{note('By default pydantic ignores fields it does not know (like "extra" above). Set model_config = ConfigDict(extra="forbid") to reject them, or strict=True to refuse "7" for an int.', 'tip')}
''', kw=['validation', 'pydantic', 'BaseModel', 'Field', 'ValidationError', 'model_validate', 'model_dump', 'TypeAdapter', 'JSON schema', 'type hints'])

K.lesson('async', 'Many calls at once with httpx', f'''
{local('httpx_async', WHY_NET)}
{steps('What happened', [
    'One by one, 5 calls of 0.2 s take 5 &times; 0.2 = 1.0 s, because each call waits for the one before.',
    'With httpx.AsyncClient and asyncio.gather, all 5 wait at the same time, so the total is about one call: 0.2 s.',
    'An asyncio.Semaphore(2) lets only 2 run at once: &lceil;5 / 2&rceil; = 3 rounds of 0.2 s = 0.6 s.',
    'Always limit how many calls run at once. Without a limit, 10,000 tasks would open 10,000 connections and hit every rate limit.'])}
{table(['Need', 'Tool'], [
    ['A few calls in a script', 'requests or httpx.Client'],
    ['Many calls at once in a script', 'httpx.AsyncClient with asyncio.gather and a Semaphore, or a ThreadPoolExecutor with requests'],
    ['Calls inside an async web app (FastAPI)', 'httpx.AsyncClient, never requests, which would block the event loop'],
    ['HTTP/2', 'httpx.Client(http2=True) after pip install httpx[http2]']])}
''', kw=['httpx', 'AsyncClient', 'asyncio.gather', 'Semaphore', 'concurrency', 'HTTP/2', 'ThreadPoolExecutor', 'blocking'])

K.lesson('maths', 'The maths: backoff, limits and pages', f'''
{fxs(fx('Backoff wait', 'wait<sub>n</sub> = min(cap, base &times; 2<sup>n</sup>)', 'base 0.5 s: 0.5, 1, 2, 4, 8 s for n = 0 to 4.', key=True),
     fx('Total backoff time', 'base &times; (2<sup>k</sup> &minus; 1) for k waits', 'base 1 s, 4 waits: 1 + 2 + 4 + 8 = 15 s.'),
     fx('Full jitter', 'wait = random(0, base &times; 2<sup>n</sup>), mean = base &times; 2<sup>n</sup> / 2', 'n = 3, base 1 s: random between 0 and 8 s, 4 s on average.'),
     fx('Token bucket in time T', 'at most capacity + rate &times; T calls', 'rate 5/s, capacity 20, 10 s: 20 + 50 = 70 calls.', key=True),
     fx('Rows skipped by an offset', 'skipped = (page &minus; 1) &times; size', 'page 50, size 20: 980 rows read and thrown away.'),
     fx('Calls in flight (Little&#39;s law)', 'L = rate &times; time per call', '100 calls/s at 0.25 s each: 25 at the same moment.', key=True))}
{steps('Worked example: how many tries are enough?', [
    'A call fails for a short time with probability 0.2, and each try is independent.',
    'With 1 try the call fails with probability 0.2.',
    'With 4 tries all must fail: 0.2<sup>4</sup> = 0.0016, that is 16 in 10,000.',
    'With backoff base 0.5 s the 3 waits add up to 0.5 + 1 + 2 = 3.5 s at most, which is fine for a nightly job but too long for a web page.',
    eq('P(all k tries fail) = p<sup>k</sup>')])}
''', kw=['backoff formula', 'jitter', 'token bucket', 'offset cost', 'Little law', 'probability of failure'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Loop over pages until there are no more, and know which errors are worth a retry.</p>',
    '<p>Write page generators, retries with backoff and jitter, respect 429 and Retry-After, and check answers with pydantic.</p>',
    '<p>Run many calls at once with httpx and a Semaphore, keep a client side token bucket, and use cursors for data that changes.</p>',
    '<p>Design clients with idempotency keys, circuit breakers and timeouts on every layer, and measure them with logs and metrics.</p>')}
{grow('Read every page safely.', 'Retry, limit and validate.', 'Build clients that stay up when the API does not.')}
{deep('Circuit breaker', '<p>If an API keeps failing, every caller still waits for timeouts and retries. A circuit breaker counts failures, and after too many it "opens": calls fail at once for a while without touching the network. After a pause it lets one test call through and closes again if that works. Libraries such as pybreaker do this, and service meshes do it for whole systems.</p>')}
''', kw=['beginner', 'expert', 'circuit breaker', 'idempotency key', 'observability'])

PLAY = '''

def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results
'''

lc(21, 'Merge Two Sorted Lists', 'merge-two-sorted-lists', 'e', 'Walk both lists, always take the smaller head', 'Like merging two sorted pages of results from two APIs. A dummy first node keeps the code short.', r'''
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def merge_two_lists(list1, list2):
    dummy = ListNode()
    tail = dummy
    while list1 and list2:
        if list1.val <= list2.val:
            tail.next = list1
            list1 = list1.next
        else:
            tail.next = list2
            list2 = list2.next
        tail = tail.next
    tail.next = list1 or list2
    return dummy.next


def build(values):
    head = None
    for value in reversed(values):
        head = ListNode(value, head)
    return head


def to_list(node):
    values = []
    while node:
        values.append(node.val)
        node = node.next
    return values


def merge_lists(a, b):
    return to_list(merge_two_lists(build(a), build(b)))
''', [('merge_lists([1, 2, 4], [1, 3, 4])', [1, 1, 2, 3, 4, 4]), ('merge_lists([], [])', []), ('merge_lists([], [0])', [0])])
lc(350, 'Intersection of Two Arrays II', 'intersection-of-two-arrays-ii', 'e', 'Counter and the & operator', 'Which ids do two API answers share, counting repeats? Counter(a) &amp; Counter(b) keeps the smaller count of each value.', r'''
from collections import Counter


def intersect(nums1, nums2):
    common = Counter(nums1) & Counter(nums2)
    return sorted(common.elements())
''', [('intersect([1, 2, 2, 1], [2, 2])', [2, 2]), ('intersect([4, 9, 5], [9, 4, 9, 8, 4])', [4, 9])])
lc(1450, 'Number of Students Doing Homework at a Given Time', 'number-of-students-doing-homework-at-a-given-time', 'e', 'Check each time range', 'Like counting the sessions that were active at a given moment in API logs. A range counts when start &lt;= time &lt;= end.', r'''
def busy_student(start_time, end_time, query_time):
    return sum(1 for start, end in zip(start_time, end_time) if start <= query_time <= end)
''', [('busy_student([1, 2, 3], [3, 2, 7], 4)', 1), ('busy_student([4], [4], 4)', 1)])
lc(703, 'Kth Largest Element in a Stream', 'kth-largest-element-in-a-stream', 'e', 'A min heap of size k', 'Keep only the k largest values seen so far in a heap. Its smallest value is the k-th largest, like the slowest of the top k response times.', r'''
import heapq


class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.heap = []
        for number in nums:
            self.add(number)

    def add(self, val):
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        return self.heap[0]
''' + PLAY, [('play(KthLargest, ["KthLargest", "add", "add", "add", "add", "add"], [[3, [4, 5, 8, 2]], [3], [5], [10], [9], [4]])', [None, 4, 5, 5, 8, 8])])
lc(57, 'Insert Interval', 'insert-interval', 'm', 'Before, overlapping, after', 'Add a time range to a sorted list of ranges. Copy the ranges that end before it, merge the ones that overlap, then copy the rest.', r'''
def insert(intervals, new_interval):
    start, end = new_interval
    result = []
    i = 0
    while i < len(intervals) and intervals[i][1] < start:
        result.append(intervals[i])
        i += 1
    while i < len(intervals) and intervals[i][0] <= end:
        start = min(start, intervals[i][0])
        end = max(end, intervals[i][1])
        i += 1
    result.append([start, end])
    result.extend(intervals[i:])
    return result
''', [('insert([[1, 3], [6, 9]], [2, 5])', [[1, 5], [6, 9]]), ('insert([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8])', [[1, 2], [3, 10], [12, 16]])])
lc(729, 'My Calendar I', 'my-calendar-i', 'm', 'Two ranges overlap when each starts before the other ends', 'A booking API must refuse a slot that overlaps an existing one. [s1, e1) and [s2, e2) overlap when s1 &lt; e2 and s2 &lt; e1.', r'''
class MyCalendar:
    def __init__(self):
        self.booked = []

    def book(self, start, end):
        for s, e in self.booked:
            if start < e and s < end:
                return False
        self.booked.append((start, end))
        return True
''' + PLAY, [('play(MyCalendar, ["MyCalendar", "book", "book", "book"], [[], [10, 20], [15, 25], [20, 30]])', [None, True, False, True])])
lc(731, 'My Calendar II', 'my-calendar-ii', 'm', 'Keep the bookings and the double booked parts', 'Now two bookings may overlap but never three. Keep a list of the parts that are already double booked. A new booking that touches one of them must be refused.', r'''
class MyCalendarTwo:
    def __init__(self):
        self.booked = []
        self.double = []

    def book(self, start, end):
        for s, e in self.double:
            if start < e and s < end:
                return False
        for s, e in self.booked:
            if start < e and s < end:
                self.double.append((max(start, s), min(end, e)))
        self.booked.append((start, end))
        return True
''' + PLAY, [('play(MyCalendarTwo, ["MyCalendarTwo", "book", "book", "book", "book", "book", "book"], [[], [10, 20], [50, 60], [10, 40], [5, 15], [5, 10], [25, 55]])', [None, True, True, True, False, True, True])])
lc(435, 'Non-overlapping Intervals', 'non-overlapping-intervals', 'm', 'Greedy: keep the range that ends first', 'Sort by end time. Keep a range when it starts after the last kept one ends, otherwise remove it. Ending early leaves the most room.', r'''
def erase_overlap_intervals(intervals):
    removed = 0
    last_end = float("-inf")
    for start, end in sorted(intervals, key=lambda pair: pair[1]):
        if start >= last_end:
            last_end = end
        else:
            removed += 1
    return removed
''', [('erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]])', 1), ('erase_overlap_intervals([[1, 2], [1, 2], [1, 2]])', 2), ('erase_overlap_intervals([[1, 2], [2, 3]])', 0)])
lc(480, 'Sliding Window Median', 'sliding-window-median', 'h', 'Keep the window sorted with bisect', 'Monitoring shows the median response time of the last k calls. Keep the window sorted: insort the new value, remove the old one, and read the middle.', r'''
from bisect import bisect_left, insort


def median_sliding_window(nums, k):
    window = sorted(nums[:k])
    medians = []
    for i in range(k, len(nums) + 1):
        if k % 2 == 1:
            medians.append(float(window[k // 2]))
        else:
            medians.append((window[k // 2 - 1] + window[k // 2]) / 2)
        if i == len(nums):
            break
        window.pop(bisect_left(window, nums[i - k]))
        insort(window, nums[i])
    return medians
''', [('median_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)', [1.0, -1.0, -1.0, 3.0, 5.0, 6.0]), ('median_sliding_window([1, 2, 3, 4, 2, 3, 1, 4, 2], 3)', [2.0, 3.0, 3.0, 3.0, 2.0, 3.0, 2.0]), ('median_sliding_window([1, 4, 2, 3], 4)', [2.5])])
lc(732, 'My Calendar III', 'my-calendar-iii', 'h', 'Sweep line: +1 at a start, &minus;1 at an end', 'How many bookings overlap at the busiest moment? Add +1 at each start and &minus;1 at each end, then walk the times in order and keep a running sum.', r'''
class MyCalendarThree:
    def __init__(self):
        self.change = {}

    def book(self, startTime, endTime):
        self.change[startTime] = self.change.get(startTime, 0) + 1
        self.change[endTime] = self.change.get(endTime, 0) - 1
        running = 0
        most = 0
        for time in sorted(self.change):
            running += self.change[time]
            most = max(most, running)
        return most
''' + PLAY, [('play(MyCalendarThree, ["MyCalendarThree", "book", "book", "book", "book", "book", "book"], [[], [10, 20], [50, 60], [10, 40], [5, 15], [5, 10], [25, 55]])', [None, 1, 1, 2, 3, 3, 3])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>API work is full of time ranges and streams: merging sorted pages, finding records that two sources share, booking time slots without overlap, keeping the k largest or the median of recent values, and refusing a third overlapping booking. These problems practise those patterns.</p>'), kw=['LeetCode', 'merge', 'intervals', 'heap', 'calendar booking', 'sliding window median', 'stream'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'APIs answer in pages. Walk them with a generator. Cursors stay correct while data changes, page numbers do not.',
    'Retry only temporary errors (timeouts, 429, 502, 503, 504) and only safe requests, with exponential backoff, jitter and a cap.',
    'Respect 429 and Retry-After. A token bucket allows bursts but keeps the average rate.',
    'Check answers at the door with pydantic: types, required fields and nested data, with clear errors.',
    'httpx.AsyncClient with asyncio.gather runs many calls at once. Always limit them with a Semaphore.'],
    'Next: build your own web apps and APIs with Flask.')}
{files('Three tasks: collect every page from a cursor API safely, compute backoff waits and read Retry-After, and validate a user record by hand.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'An API returns 50 items per page and you need all 120. How many requests?', ['2', '3', '120', '1'], 1, 'Round up.', '&lceil;120 / 50&rceil; = 3.')
K.quiz('e', 'Which status means you sent too many requests?', ['404', '429', '500', '301'], 1, 'Too Many Requests.', 'It often comes with a Retry-After header.')
K.quiz('e', 'Which error is worth a retry?', ['404 Not Found', '503 Service Unavailable', '401 Unauthorized', '422 invalid data'], 1, 'Temporary or not.', 'The others will fail the same way again.')
K.quiz('m', 'What does exponential backoff with base 1 s wait before tries 2, 3 and 4?', ['1, 1, 1 s', '1, 2, 4 s', '1, 2, 3 s', '0, 0, 0 s'], 1, 'Doubling.', 'With jitter each wait becomes a random number up to that value.')
K.quiz('m', 'Why add random jitter to retries?', ['To make them faster', 'So many clients that failed together do not retry together', 'To confuse attackers', 'Because the server asks for it'], 1, 'Thundering herd.', 'Random waits spread the load over time.')
K.quiz('m', 'A server sends 429 with Retry-After: 10. What should the client do?', ['Retry at once', 'Wait 10 seconds, then retry', 'Give up for ever', 'Send the request to another URL'], 1, 'The server told you.', 'Retrying earlier only adds more 429 answers.')
K.quiz('m', 'Why can page numbers show the same item twice?', ['A bug in requests', 'A new item added at the start shifts all later items by one', 'Pages are cached', 'JSON is unordered'], 1, 'Data changed between requests.', 'Cursor pagination does not have this problem.')
K.quiz('m', 'What does pydantic do with {"id": "7"} for a field id: int?', ['Raises an error', 'Turns it into 7', 'Keeps "7"', 'Sets it to None'], 1, 'Lax mode.', 'With strict=True it would raise a ValidationError.')
K.quiz('m', 'Five calls of 0.2 s each with asyncio.gather and Semaphore(2). About how long?', ['0.2 s', '0.6 s', '1.0 s', '0.4 s'], 1, 'Rounds of 2.', '&lceil;5 / 2&rceil; = 3 rounds of 0.2 s.')
K.quiz('h', 'Why should a FastAPI endpoint call other APIs with httpx.AsyncClient and not requests?', ['requests cannot send JSON', 'requests blocks the event loop, so all other requests wait', 'httpx is always faster', 'requests has no timeout'], 1, 'async code must not block.', 'One blocking call stops every coroutine on that event loop.')
K.quiz('h', 'A token bucket has capacity 10 and refills 2 tokens per second. It is full. How many calls can go through in the first 5 seconds?', ['10', '20', '12', '5'], 1, 'capacity + rate &times; time.', '10 + 2 &times; 5 = 20.')
K.quiz('x', 'In the style of an MIT 6.824 exam: why is "retry until it works" with a POST /transfer dangerous, and what fixes it?', ['Nothing, POST is safe', 'The first try may have worked, so money moves twice. An idempotency key lets the server ignore a repeat', 'It is too slow. Use UDP', 'Use GET for transfers'], 1, 'At least once delivery.', 'Idempotency keys turn "at least once" into "exactly once" for the effect.')
K.quiz('x', 'In the style of a Stanford CS 244 exam: 1,000 clients fail at the same moment and retry with fixed 1 s waits. The server handles 200 per second. What happens, and what helps most?', ['They are served in 5 s', 'Every second 1,000 arrive and all fail again. Random jitter spreads them so about 200 a second get in', 'A longer fixed wait solves it', 'Nothing helps'], 1, 'They stay in step.', 'Spreading the retries over 5 s or more lets the server catch up.')

K.calc('e', 'Backoff base 0.5 s. What is the wait for n = 3 (the 4th wait, n starts at 0)?', '4', 'base &times; 2<sup>n</sup>.', ['2<sup>3</sup> = 8.', '0.5 &times; 8.', eq('4 s')], check=0.5 * 2 ** 3)
K.calc('e', 'How many pages of 100 are needed for 1,000 items?', '10', 'items / size, rounded up.', ['1000 / 100 = 10.', 'It is a whole number, so no extra page.', eq('10')], check=-(-1000 // 100))
K.calc('e', 'A token bucket allows 5 calls a second with a burst of 20 and starts full. How many calls at most in 10 s?', '70', 'capacity + rate &times; T.', ['Burst: 20.', 'Refill: 5 &times; 10 = 50.', eq('70')], check=20 + 5 * 10)
K.calc('m', 'Backoff waits 1, 2, 4 and 8 s. What is the total wait in seconds?', '15', 'Add them, or 2<sup>4</sup> &minus; 1.', ['1 + 2 + 4 + 8.', 'Check: 2<sup>4</sup> &minus; 1 = 15.', eq('15 s')], check=1 + 2 + 4 + 8)
K.calc('m', 'Full jitter with base 1 s at n = 3. What is the average wait in seconds?', '4', 'The mean of random(0, m) is m / 2.', ['m = 1 &times; 2<sup>3</sup> = 8.', 'Mean = 8 / 2.', eq('4 s')], check=2 ** 3 / 2)
K.calc('m', 'Offset paging with size 20: how many rows does the database skip to show page 50?', '980', '(page &minus; 1) &times; size.', ['49 earlier pages.', '49 &times; 20.', eq('980')], check=49 * 20)
K.calc('m', '50 calls of 0.3 s each, at most 10 at once. How many seconds in total?', '1.5', 'Rounds of 10.', ['50 / 10 = 5 rounds.', 'Each round 0.3 s.', eq('5 &times; 0.3 = 1.5 s')], check=5 * 0.3, tol=0.01)
K.calc('m', 'Retry-After says a date 90 s after the answer. You already spent 30 s. How many more seconds to wait?', '60', 'What is left.', ['The server wants 90 s in total.', '90 &minus; 30.', eq('60 s')], check=90 - 30)
K.calc('h', 'Each try fails with probability 0.2, independently. What is the chance all 4 tries fail (4 decimals)?', '0.0016', 'p<sup>k</sup>.', ['0.2<sup>2</sup> = 0.04.', '0.04<sup>2</sup> = 0.0016.', eq('0.0016')], check=0.2 ** 4, tol=0.00005)
K.calc('x', 'In the style of a CMU 15-440 exam: an API allows 100 calls per second and each call takes 0.25 s. How many calls must be in flight to use the full limit?', '25', 'Little&#39;s law.', ['L = &lambda; &times; W.', '100 &times; 0.25.', eq('25')], check=100 * 0.25)

K.assign('paging', 'e', 'Collect every page from a cursor API',
         '<p><code>fetch_page(cursor)</code> returns a dict with "items" (a list) and "next" (the cursor for the next page, or None at the end). The first call uses cursor None. Write <code>collect(fetch_page)</code> that returns all items of all pages in order. A broken API might send a cursor it already sent, which would loop for ever, so raise RuntimeError when a cursor comes back a second time.</p>',
         '''
def collect(fetch_page):
    page = fetch_page(None)
    return page["items"]


def fake_api(pages):
    """Makes a fetch_page function from a dict: cursor -> (items, next cursor)."""
    def fetch_page(cursor):
        items, next_cursor = pages[cursor]
        return {"items": items, "next": next_cursor}
    return fetch_page


THREE = fake_api({None: (["a", "b"], "c2"), "c2": (["c", "d"], "c3"), "c3": (["e"], None)})
ONE = fake_api({None: (["only"], None)})
EMPTY = fake_api({None: ([], None)})
LOOP = fake_api({None: (["a"], "c2"), "c2": (["b"], "c3"), "c3": (["c"], "c2")})


def loop_error():
    try:
        collect(LOOP)
    except RuntimeError:
        return "RuntimeError"
    return "no error"
''', [('collect(THREE)', ['a', 'b', 'c', 'd', 'e']), ('collect(ONE)', ['only']), ('collect(EMPTY)', []), ('loop_error()', 'RuntimeError')],
         '''
def collect(fetch_page):
    items = []
    seen = set()
    cursor = None
    while True:
        page = fetch_page(cursor)
        items.extend(page["items"])
        cursor = page["next"]
        if cursor is None:
            return items
        if cursor in seen:
            raise RuntimeError(f"the API sent the cursor {cursor!r} twice")
        seen.add(cursor)


def fake_api(pages):
    """Makes a fetch_page function from a dict: cursor -> (items, next cursor)."""
    def fetch_page(cursor):
        items, next_cursor = pages[cursor]
        return {"items": items, "next": next_cursor}
    return fetch_page


THREE = fake_api({None: (["a", "b"], "c2"), "c2": (["c", "d"], "c3"), "c3": (["e"], None)})
ONE = fake_api({None: (["only"], None)})
EMPTY = fake_api({None: ([], None)})
LOOP = fake_api({None: (["a"], "c2"), "c2": (["b"], "c3"), "c3": (["c"], "c2")})


def loop_error():
    try:
        collect(LOOP)
    except RuntimeError:
        return "RuntimeError"
    return "no error"
''', 'Loop until next is None. Keep a set of cursors you have used, and stop with an error when one repeats.', '<p>Production code also stops after a maximum number of pages and logs how many it read. Never trust an outside API to end a loop for you.</p>')
K.assign('backoff', 'm', 'Backoff waits and Retry-After',
         '<p>Write <code>backoff_waits(tries, base, cap)</code>: the list of waits between tries, base &times; 2<sup>n</sup> for n = 0, 1, ... but never more than cap (there is one wait fewer than tries). Write <code>parse_retry_after(value, now)</code>: Retry-After is either a number of seconds such as "120" or an HTTP date such as "Wed, 21 Oct 2026 07:28:00 GMT". Return the seconds to wait as an int, 0 for a date in the past, and None when the value cannot be read. Write <code>should_retry(method, status)</code>: True only for GET, HEAD, PUT, DELETE and OPTIONS with status 408, 429, 500, 502, 503 or 504.</p>',
         '''
from datetime import datetime, timezone


def backoff_waits(tries, base, cap):
    return [base * 2 for n in range(tries)]


def parse_retry_after(value, now):
    return int(value)


def should_retry(method, status):
    return status >= 500


NOW = datetime(2026, 10, 21, 7, 27, 0, tzinfo=timezone.utc)
''', [('backoff_waits(4, 0.5, 30)', [0.5, 1.0, 2.0]), ('backoff_waits(6, 1, 10)', [1, 2, 4, 8, 10]), ('backoff_waits(1, 1, 10)', []), ('parse_retry_after("120", NOW)', 120), ('parse_retry_after("Wed, 21 Oct 2026 07:28:00 GMT", NOW)', 60), ('parse_retry_after("Wed, 21 Oct 2026 07:00:00 GMT", NOW)', 0), ('parse_retry_after("soon", NOW)', None), ('[should_retry("GET", 503), should_retry("POST", 503), should_retry("GET", 404), should_retry("PUT", 429), should_retry("DELETE", 501)]', [True, False, False, True, False])],
         '''
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

RETRY_METHODS = {"GET", "HEAD", "PUT", "DELETE", "OPTIONS"}
RETRY_STATUS = {408, 429, 500, 502, 503, 504}


def backoff_waits(tries, base, cap):
    return [min(cap, base * 2 ** n) for n in range(tries - 1)]


def parse_retry_after(value, now):
    value = value.strip()
    if value.isdigit():
        return int(value)
    try:
        moment = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    return max(0, int((moment - now).total_seconds()))


def should_retry(method, status):
    return method.upper() in RETRY_METHODS and status in RETRY_STATUS


NOW = datetime(2026, 10, 21, 7, 27, 0, tzinfo=timezone.utc)
''', 'min(cap, base * 2 ** n) for n in range(tries - 1). email.utils.parsedate_to_datetime reads HTTP dates and raises ValueError for text it cannot read. Two sets make should_retry one line.', '<p>urllib3 Retry does the same three jobs: backoff_factor gives the waits, respect_retry_after_header reads Retry-After, and allowed_methods with status_forcelist decide what is retried.</p>')
K.assign('validate', 'h', 'Validate a user record by hand',
         '<p>Without pydantic, write <code>validate_user(data)</code> that returns [clean, errors]. Rules: "id" is required and must be a whole number above 0 (a string of digits such as "12" is fine, but True is not). "email" is required and must have exactly one "@" with a dot somewhere after it. "age" is optional (default None) and must be a whole number from 0 to 150 (digit strings are fine). "tags" is optional (default []) and must be a list of strings. When everything is fine return the clean dict with exactly these four keys and no errors. Otherwise return None and the list of messages "field: problem", sorted. Use the messages from the tests.</p>',
         '''
def validate_user(data):
    return [data, []]
''', [('validate_user({"id": "12", "email": "ann@site.com"})', [{'id': 12, 'email': 'ann@site.com', 'age': None, 'tags': []}, []]), ('validate_user({"id": 5, "email": "a@b.co", "age": "30", "tags": ["x"], "extra": 1})', [{'id': 5, 'email': 'a@b.co', 'age': 30, 'tags': ['x']}, []]), ('validate_user({"id": 0, "email": "bad", "age": 200})', [None, ['age: must be a whole number from 0 to 150', 'email: not a valid email', 'id: must be a whole number above 0']]), ('validate_user({"email": "a@b.co", "tags": ["x", 3]})', [None, ['id: required', 'tags: must be a list of strings']]), ('validate_user({"id": True, "email": "a@@b.co"})', [None, ['email: not a valid email', 'id: must be a whole number above 0']])],
         '''
def whole_number(value):
    """Return value as an int, or None when it is not a whole number. True and False do not count."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def good_email(value):
    if not isinstance(value, str) or value.count("@") != 1:
        return False
    name, domain = value.split("@")
    return name != "" and "." in domain


def validate_user(data):
    errors = []
    clean = {}

    if "id" not in data:
        errors.append("id: required")
    else:
        number = whole_number(data["id"])
        if number is None or number <= 0:
            errors.append("id: must be a whole number above 0")
        clean["id"] = number

    if "email" not in data:
        errors.append("email: required")
    elif not good_email(data["email"]):
        errors.append("email: not a valid email")
    else:
        clean["email"] = data["email"]

    clean["age"] = None
    if data.get("age") is not None:
        age = whole_number(data["age"])
        if age is None or not 0 <= age <= 150:
            errors.append("age: must be a whole number from 0 to 150")
        clean["age"] = age

    tags = data.get("tags", [])
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        errors.append("tags: must be a list of strings")
    clean["tags"] = tags

    if errors:
        return [None, sorted(errors)]
    return [clean, []]
''', 'Check one field at a time and collect every problem before you return, so the caller sees all of them at once. isinstance(True, int) is True in Python, so test for bool first.', '<p>This is exactly what pydantic does for you, with the same idea: one place that checks everything and reports every problem with the field name. Compare the length of this code with the Book model in the lesson.</p>')

K.must('Pages', 'Loop with a generator until no next page or cursor. Cursors stay correct when data changes. pages = &lceil;items / size&rceil;.')
K.must('Retries', 'Only timeouts, connection errors, 429, 502, 503, 504, and only idempotent requests. wait = random(0, min(cap, base &times; 2<sup>n</sup>)). Stop after k tries.')
K.must('Limits', '429 plus Retry-After (seconds or a date). Token bucket: capacity for bursts, rate for the average. X-RateLimit-Remaining.')
K.must('pydantic', 'class M(BaseModel), Field(min_length=, ge=, le=), M.model_validate(dict), model_dump(), TypeAdapter(list[M]).validate_json(text), ValidationError.errors().')
K.must('httpx', 'httpx.Client like a Session, httpx.AsyncClient with await, asyncio.gather for many, asyncio.Semaphore(n) to limit them.')

T = K.topic(
    slug='py-api-data', topic='py-api-data', step=(2, 'Calling web APIs', 'py-w2', 'Use real web APIs from Python: requests, errors and timeouts, sessions and auth, JSON, then pagination, retries, rate limits, validation and async clients.', 'Intermediate'),
    title='Real API work: pages, retries, limits and validation', short='API data', badge='2.2', minutes=90,
    lead='Make API code that survives the real world. Read every page, retry the right errors with backoff and jitter, stay inside rate limits, check the data with pydantic, and run many calls at once with httpx.',
    desc='Pagination with page numbers, offsets, cursors and Link headers, page generators, which errors to retry, exponential backoff with full jitter, Retry-After, urllib3 Retry on a requests Session, idempotency keys, rate limits and the token bucket, validation with pydantic models, httpx Client and AsyncClient with asyncio.gather and a Semaphore, and the maths of backoff, limits and pages.',
    summary='Pagination, retries with backoff and jitter, rate limits, pydantic validation and async calls with httpx.',
    keywords=['pagination', 'cursor', 'retry', 'backoff', 'jitter', 'rate limit', 'token bucket', 'pydantic', 'httpx', 'asyncio'],
    recap='<p>Real APIs page their data, fail for a moment, limit you and send odd records. Loop, retry with jitter, slow down when asked, and check what comes in.</p>',
    added='2026-11-07', leet=leet_items())
