# 2.2 Real API work: pages, retries, limits and validation
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


# ================================================================== task 1: Collect every page from a cursor API
# fetch_page(cursor) returns a dict with "items" (a list) and "next" (the cursor for the next page,
# or None at the end). The first call uses cursor None. Write collect(fetch_page) that returns all
# items of all pages in order. A broken API might send a cursor it already sent, which would loop
# for ever, so raise RuntimeError when a cursor comes back a second time.
# Hint: Loop until next is None. Keep a set of cursors you have used, and stop with an error when
# one repeats.

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


# ================================================================== task 2: Backoff waits and Retry-After
# Write backoff_waits(tries, base, cap): the list of waits between tries, base × 2n for n = 0, 1,
# ... but never more than cap (there is one wait fewer than tries). Write parse_retry_after(value,
# now): Retry-After is either a number of seconds such as "120" or an HTTP date such as "Wed, 21 Oct
# 2026 07:28:00 GMT". Return the seconds to wait as an int, 0 for a date in the past, and None when
# the value cannot be read. Write should_retry(method, status): True only for GET, HEAD, PUT, DELETE
# and OPTIONS with status 408, 429, 500, 502, 503 or 504.
# Hint: min(cap, base * 2 ** n) for n in range(tries - 1). email.utils.parsedate_to_datetime reads
# HTTP dates and raises ValueError for text it cannot read. Two sets make should_retry one line.

from datetime import datetime, timezone


def backoff_waits(tries, base, cap):
    return [base * 2 for n in range(tries)]


def parse_retry_after(value, now):
    return int(value)


def should_retry(method, status):
    return status >= 500


NOW = datetime(2026, 10, 21, 7, 27, 0, tzinfo=timezone.utc)


# ================================================================== task 3: Validate a user record by hand
# Without pydantic, write validate_user(data) that returns [clean, errors]. Rules: "id" is required
# and must be a whole number above 0 (a string of digits such as "12" is fine, but True is not).
# "email" is required and must have exactly one "@" with a dot somewhere after it. "age" is optional
# (default None) and must be a whole number from 0 to 150 (digit strings are fine). "tags" is
# optional (default []) and must be a list of strings. When everything is fine return the clean dict
# with exactly these four keys and no errors. Otherwise return None and the list of messages "field:
# problem", sorted. Use the messages from the tests.
# Hint: Check one field at a time and collect every problem before you return, so the caller sees
# all of them at once. isinstance(True, int) is True in Python, so test for bool first.

def validate_user(data):
    return [data, []]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Collect every page from a cursor API", [('collect(THREE)', ['a', 'b', 'c', 'd', 'e']), ('collect(ONE)', ['only']), ('collect(EMPTY)', []), ('loop_error()', 'RuntimeError')]))
    results.append(check("Task 2: Backoff waits and Retry-After", [('backoff_waits(4, 0.5, 30)', [0.5, 1.0, 2.0]), ('backoff_waits(6, 1, 10)', [1, 2, 4, 8, 10]), ('backoff_waits(1, 1, 10)', []), ('parse_retry_after("120", NOW)', 120), ('parse_retry_after("Wed, 21 Oct 2026 07:28:00 GMT", NOW)', 60), ('parse_retry_after("Wed, 21 Oct 2026 07:00:00 GMT", NOW)', 0), ('parse_retry_after("soon", NOW)', None), ('[should_retry("GET", 503), should_retry("POST", 503), should_retry("GET", 404), should_retry("PUT", 429), should_retry("DELETE", 501)]', [True, False, False, True, False])]))
    results.append(check("Task 3: Validate a user record by hand", [('validate_user({"id": "12", "email": "ann@site.com"})', [{'id': 12, 'email': 'ann@site.com', 'age': None, 'tags': []}, []]), ('validate_user({"id": 5, "email": "a@b.co", "age": "30", "tags": ["x"], "extra": 1})', [{'id': 5, 'email': 'a@b.co', 'age': 30, 'tags': ['x']}, []]), ('validate_user({"id": 0, "email": "bad", "age": 200})', [None, ['age: must be a whole number from 0 to 150', 'email: not a valid email', 'id: must be a whole number above 0']]), ('validate_user({"email": "a@b.co", "tags": ["x", 3]})', [None, ['id: required', 'tags: must be a list of strings']]), ('validate_user({"id": True, "email": "a@@b.co"})', [None, ['email: not a valid email', 'id: must be a whole number above 0']])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
