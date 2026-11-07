# 1.1 HTTP and REST: how the web talks
# Practice tasks. Fill in each function, then run this file.
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
# Hint: Splitting by hand misses %20, + and names without "=". parse_qsl does all of that, and
# keep_blank_values=True keeps "debug".

def parse_query(query):
    result = {}
    for pair in query.split("&"):
        name, value = pair.split("=")
        result[name] = value
    return result


# ================================================================== task 2: Describe status codes and decide when to retry
# Write describe(code) that returns text like "404 Not Found (client error)" with the kinds success,
# redirect, client error and server error, and raises ValueError for a number that is not a known
# HTTP status. Also write should_retry(code): True only for 408, 429, 500, 502, 503 and 504, because
# other errors will fail again in the same way. Use http.HTTPStatus.
# Hint: HTTPStatus(code) already raises ValueError for unknown numbers. Add the kind from the first
# digit. Retry only temporary problems: timeouts (408), rate limits (429) and some server errors.

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


# ================================================================== task 3: Parse a raw HTTP request
# Write parse_request(raw) for the text of a request. Lines end with \r\n and a blank line separates
# the headers from the body. Return a dict with method, path (without the query), query (a dict,
# like in the first task), version, headers (a dict with lower case names) and body (the first
# Content-Length characters after the blank line, or "" when there is no Content-Length). Raise
# ValueError when the request line does not have exactly three parts or the version does not start
# with "HTTP/".
# Hint: partition("\r\n\r\n") splits the head from the body. Check the request line before unpacking
# it, lower case the header names (HTTP header names ignore case), and use Content-Length to cut the
# body.

def parse_request(raw):
    lines = raw.split("\n")
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
