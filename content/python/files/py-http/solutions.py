# 1.1 HTTP and REST: how the web talks
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


# ================================================================== task 1: Read a query string correctly
# Write parse_query(query) that turns a query string such as "q=hello%20world&page=2" into a dict of
# names and values. Decode percent encoding and + as a space, keep names without a value as "" and,
# when a name appears twice, keep the last value. Use urllib.parse.parse_qsl with
# keep_blank_values=True.
# Why it works: Frameworks such as Flask (request.args) and Django (request.GET) do this parsing for
# you, with the same rules.

from urllib.parse import parse_qsl


def parse_query(query):
    result = {}
    for name, value in parse_qsl(query, keep_blank_values=True):
        result[name] = value
    return result


# ================================================================== task 2: Describe status codes and decide when to retry
# Write describe(code) that returns text like "404 Not Found (client error)" with the kinds success,
# redirect, client error and server error, and raises ValueError for a number that is not a known
# HTTP status. Also write should_retry(code): True only for 408, 429, 500, 502, 503 and 504, because
# other errors will fail again in the same way. Use http.HTTPStatus.
# Why it works: Retrying a 400 or 404 only repeats the same mistake, and retrying 501 Not
# Implemented never helps. Real clients also wait longer between each retry.

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


# ================================================================== task 3: Parse a raw HTTP request
# Write parse_request(raw) for the text of a request. Lines end with \r\n and a blank line separates
# the headers from the body. Return a dict with method, path (without the query), query (a dict,
# like in the first task), version, headers (a dict with lower case names) and body (the first
# Content-Length characters after the blank line, or "" when there is no Content-Length). Raise
# ValueError when the request line does not have exactly three parts or the version does not start
# with "HTTP/".
# Why it works: This is roughly what http.server, Flask and Django do with every request before your
# code sees it. Real servers also limit sizes, so that a huge Content-Length cannot fill the memory.

from urllib.parse import parse_qsl


def parse_request(raw):
    head, _, rest = raw.partition("\r\n\r\n")
    lines = head.split("\r\n")
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


GET = "GET /books?page=2&q=sci%20fi HTTP/1.1\r\nHost: shop.com\r\nAccept: application/json\r\n\r\n"
POST = "POST /books HTTP/1.1\r\nHost: shop.com\r\nContent-Type: application/json\r\nContent-Length: 17\r\n\r\n{\"title\": \"Emma\"}"


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Read a query string correctly", [('parse_query("page=2&size=10")', {'page': '2', 'size': '10'}), ('parse_query("q=hello%20world")', {'q': 'hello world'}), ('parse_query("q=fish+%26+chips")', {'q': 'fish & chips'}), ('parse_query("debug&page=3")', {'debug': '', 'page': '3'}), ('parse_query("")', {})]))
    results.append(check("Task 2: Describe status codes and decide when to retry", [('describe(404)', '404 Not Found (client error)'), ('describe(201)', '201 Created (success)'), ('describe(503)', '503 Service Unavailable (server error)'), ('describe(301)', '301 Moved Permanently (redirect)'), ('unknown_code(299)', 'ValueError'), ('[c for c in (400, 404, 408, 429, 500, 501, 503) if should_retry(c)]', [408, 429, 500, 503])]))
    results.append(check("Task 3: Parse a raw HTTP request", [('parse_request(GET)', {'method': 'GET', 'path': '/books', 'query': {'page': '2', 'q': 'sci fi'}, 'version': 'HTTP/1.1', 'headers': {'host': 'shop.com', 'accept': 'application/json'}, 'body': ''}), ('parse_request(POST)["body"]', '{"title": "Emma"}'), ('parse_request(POST)["headers"]["content-length"]', '17'), ('error_of("GET /books\\r\\n\\r\\n")', 'ValueError'), ('error_of("GET /books FTP/1.0\\r\\n\\r\\n")', 'ValueError')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
