# 6.2 Web revision exam: HTTP, Flask, Django, FastAPI and security
# Model solutions. Try practice.py first.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: Pick the right status code
# Finish pick_status(method, logged_in, allowed, found, valid). Check in this order: not logged in
# gives 401, not allowed 403, not found 404, invalid input 422. When everything is fine, POST gives
# 201, DELETE gives 204 and every other method 200. status_table() collects six cases.
# Why it works: This order is what DRF and FastAPI do too: authentication runs first, then
# permissions, then the object lookup, then validation. That is why a logged out caller gets 401
# even for an id that does not exist, and learns nothing about the data.

def pick_status(method, logged_in=True, allowed=True, found=True, valid=True):
    """Return the HTTP status a REST API should send. Check in this order: who, may, exists, valid, success."""
    if not logged_in:
        return 401
    if not allowed:
        return 403
    if not found:
        return 404
    if not valid:
        return 422
    if method == "POST":
        return 201
    if method == "DELETE":
        return 204
    return 200


def status_table():
    return [pick_status("GET"), pick_status("POST"), pick_status("DELETE"), pick_status("PUT", valid=False),
            pick_status("GET", logged_in=False, found=False), pick_status("PATCH", allowed=False, found=False)]


# ================================================================== task 2: Build a Flask style URL router
# Finish UrlRouter.bind and match. A rule such as /books/<int:book_id> has fixed pieces, <name> for
# any one piece, <int:name> for digits only (given as an int) and <path:name> for the rest of the
# URL with its slashes. match(method, url) returns [200, name, params] for the first rule that fits
# the URL and the method, [405, None, {}] when some rule fits the URL but not the method, and [404,
# None, {}] when nothing fits.
# Why it works: Werkzeug, the router inside Flask, works the same way with compiled regular
# expressions, and it also answers 405 with an Allow header listing the methods that would work.
# Django's path() converters (int, str, slug, uuid, path) follow the same idea.

class UrlRouter:
    """A tiny Flask style router with the converters <name>, <int:name> and <path:name>."""

    def __init__(self):
        self.rules = []

    def add(self, methods, rule, name):
        self.rules.append((set(methods), rule.strip("/").split("/"), name))

    def bind(self, pattern, parts):
        params = {}
        for i, piece in enumerate(pattern):
            if piece.startswith("<path:"):
                if i >= len(parts):
                    return None
                params[piece[6:-1]] = "/".join(parts[i:])
                return params
            if i >= len(parts):
                return None
            if piece.startswith("<int:"):
                if not parts[i].isdigit():
                    return None
                params[piece[5:-1]] = int(parts[i])
            elif piece.startswith("<"):
                params[piece[1:-1]] = parts[i]
            elif piece != parts[i]:
                return None
        return params if len(pattern) == len(parts) else None

    def match(self, method, url):
        parts = url.strip("/").split("/")
        wrong_method = False
        for methods, pattern, name in self.rules:
            params = self.bind(pattern, parts)
            if params is None:
                continue
            if method in methods:
                return [200, name, params]
            wrong_method = True
        return [405, None, {}] if wrong_method else [404, None, {}]


def shop_router():
    r = UrlRouter()
    r.add(["GET"], "/books", "list_books")
    r.add(["POST"], "/books", "add_book")
    r.add(["GET", "PUT"], "/books/<int:book_id>", "book")
    r.add(["GET"], "/authors/<name>/books", "author_books")
    r.add(["GET"], "/files/<path:rest>", "file")
    return r


# ================================================================== task 3: Add ETags for caching and safe updates
# make_etag is ready. Finish handle(store, method, key, headers, body). A missing key gives [404,
# None, None]. GET answers [200, tag, doc], or [304, tag, None] when If-None-Match equals the
# current tag. PUT without If-Match answers [428, None, None], with a tag that is not current [412,
# tag, None], and otherwise saves the body and answers [200, new tag, body]. lost_update_story shows
# two users who both read the same version.
# Why it works: 304 saves bandwidth because the client keeps its copy. 412 is optimistic
# concurrency: nobody locks the record, but the second writer is told that it changed and must
# reload. 428 Precondition Required (RFC 6585) forces clients to send If-Match at all.

import hashlib
import json


def make_etag(doc):
    """A strong ETag: the first 16 hex digits of sha256 of the JSON with sorted keys, in double quotes."""
    text = json.dumps(doc, sort_keys=True, separators=(",", ":"))
    return '"' + hashlib.sha256(text.encode()).hexdigest()[:16] + '"'


def handle(store, method, key, headers=None, body=None):
    """GET with If-None-Match gives 304 when nothing changed. PUT with If-Match gives 412 when someone
    else changed the document first, and 428 when If-Match is missing. Returns [status, etag or None, body]."""
    headers = headers or {}
    doc = store.get(key)
    if doc is None:
        return [404, None, None]
    tag = make_etag(doc)
    if method == "GET":
        if headers.get("If-None-Match") == tag:
            return [304, tag, None]
        return [200, tag, doc]
    if method == "PUT":
        if "If-Match" not in headers:
            return [428, None, None]
        if headers["If-Match"] != tag:
            return [412, tag, None]
        store[key] = body
        return [200, make_etag(body), body]
    return [405, None, None]


def lost_update_story():
    store = {"book-1": {"title": "Emma", "stock": 3}}
    _, tag, _ = handle(store, "GET", "book-1")
    ann = handle(store, "PUT", "book-1", {"If-Match": tag}, {"title": "Emma", "stock": 2})
    ben = handle(store, "PUT", "book-1", {"If-Match": tag}, {"title": "Emma", "stock": 9})
    again = handle(store, "GET", "book-1", {"If-None-Match": ann[1]})
    return [ann[0], ben[0], again[0], store["book-1"]["stock"]]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Pick the right status code", [('status_table()', [200, 201, 204, 422, 401, 403]), ('pick_status("DELETE", valid=False)', 422), ('pick_status("POST", logged_in=False, allowed=False)', 401), ('pick_status("HEAD")', 200)]))
    results.append(check("Task 2: Build a Flask style URL router", [('shop_router().match("GET", "/books")', [200, 'list_books', {}]), ('shop_router().match("POST", "/books/")', [200, 'add_book', {}]), ('shop_router().match("PUT", "/books/42")', [200, 'book', {'book_id': 42}]), ('shop_router().match("GET", "/books/abc")', [404, None, {}]), ('shop_router().match("DELETE", "/books/42")', [405, None, {}]), ('shop_router().match("GET", "/authors/ann/books")', [200, 'author_books', {'name': 'ann'}]), ('shop_router().match("GET", "/files/img/2026/cat.png")', [200, 'file', {'rest': 'img/2026/cat.png'}]), ('shop_router().match("GET", "/files")', [404, None, {}])]))
    results.append(check("Task 3: Add ETags for caching and safe updates", [('make_etag({"b": 1, "a": 2}) == make_etag({"a": 2, "b": 1})', True), ('lost_update_story()', [200, 412, 304, 2]), ('handle({"k": {"x": 1}}, "PUT", "k", {}, {"x": 2})', [428, None, None]), ('handle({}, "GET", "k")', [404, None, None]), ('handle({"k": {"x": 1}}, "GET", "k", {"If-None-Match": "stale"})[0]', 200)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
