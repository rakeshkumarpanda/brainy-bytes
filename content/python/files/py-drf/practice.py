# 5.1 Django REST framework: JSON APIs on top of Django
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


# ================================================================== task 1: Write a serializer for shop orders
# Finish OrderSerializer. The fields are ready. Add validate_coupon: strip spaces, use upper case,
# and raise ValidationError("Unknown coupon.") when the coupon is not empty and not in COUPONS.
# Change validate: raise ValidationError("HALF needs at least 2 items.") when the coupon is HALF and
# the quantity is under 2, and set data["total"] to price times quantity minus the coupon percent.
# try_order(data) returns ["ok", validated data] or ["errors", {field: [messages]}].
# Hint: validate_<field> gets one value and returns the cleaned value. validate(data) gets all
# fields, and an error raised there appears under non_field_errors. The total is total × (100 −
# percent) / 100.

import django
from django.conf import settings

settings.configure(SECRET_KEY="dev-only", INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth", "rest_framework"])
django.setup()

from rest_framework import serializers

PRICES = {"tea": 3, "cake": 5, "sandwich": 7}
COUPONS = {"HALF": 50, "TEN": 10}


class OrderSerializer(serializers.Serializer):
    product = serializers.ChoiceField(choices=sorted(PRICES))
    quantity = serializers.IntegerField(min_value=1, max_value=10)
    coupon = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, data):
        data["total"] = PRICES[data["product"]] * data["quantity"]
        return data


def try_order(data):
    serializer = OrderSerializer(data=data)
    if serializer.is_valid():
        return ["ok", dict(serializer.validated_data)]
    return ["errors", {field: [str(e) for e in errors] for field, errors in serializer.errors.items()}]


# ================================================================== task 2: Write page number and cursor pagination
# Write paginate(items, page, page_size, base_url) that returns {"count", "next", "previous",
# "results"} like DRF's PageNumberPagination. Pages start at 1, next and previous are base_url +
# "?page=N" or None, an empty list still has a page 1, and a page that is not a whole number from 1
# to the last page raises ValueError("Invalid page."). Write cursor_page(rows, after_id, size): the
# ids of the next size rows with id greater than after_id, sorted by id, and next_cursor, the last
# id of the page, or None when nothing is left.
# Hint: The last page is the ceiling of len(items) / page_size, and at least 1. -(-a // b) is a
# ceiling division. For the cursor, sort the newer rows and check whether more rows exist after the
# page.

def page_url(base_url, page):
    return None if page is None else f"{base_url}?page={page}"


def paginate(items, page, page_size, base_url):
    """One page in the shape DRF's PageNumberPagination returns."""
    start = page * page_size
    return {"count": len(items), "next": None, "previous": None, "results": items[start:start + page_size]}


def cursor_page(rows, after_id, size):
    """Cursor pagination: the rows with id greater than after_id, sorted by id, and the cursor for the next page."""
    return {"results": [row["id"] for row in rows[:size]], "next_cursor": None}


def page_error(page):
    try:
        paginate(list(range(5)), page, 2, "/api/books/")
    except ValueError as error:
        return str(error)
    return "no error"


# ================================================================== task 3: Build a sliding window rate limiter
# Finish SlidingWindowLimiter, the idea behind DRF's throttles. parse_rate is ready: "3/minute"
# gives 3 requests per 60 seconds. allow(key, now) keeps the times of the accepted requests of each
# key. First forget the times that are window seconds old or older. When the key already has the
# allowed number of requests, return [False, seconds until the oldest one leaves the window] and do
# not store the request. Otherwise store it and return [True, 0]. Each key (an IP address or a user)
# has its own history.
# Hint: Remove times while times[0] <= now − window. The wait is times[0] + window − now. Rejected
# requests must not be added, or a client that keeps trying would never get in.

UNITS = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}


def parse_rate(rate):
    """ "3/minute" becomes (3, 60), as in DRF's SimpleRateThrottle."""
    count, unit = rate.split("/")
    if unit not in UNITS or not count.isdigit():
        raise ValueError(f"bad rate {rate!r}")
    return int(count), UNITS[unit]


class SlidingWindowLimiter:
    def __init__(self, rate):
        self.allowed, self.window = parse_rate(rate)
        self.history = {}                         # key -> times of the accepted requests, oldest first

    def allow(self, key, now):
        times = self.history.setdefault(key, [])
        times.append(now)
        return [len(times) <= self.allowed, 0]


def limiter_story(rate, events):
    """events: a list of (key, time). Returns [allowed, retry_after] for each."""
    limiter = SlidingWindowLimiter(rate)
    return [limiter.allow(key, now) for key, now in events]


def rate_error(rate):
    try:
        parse_rate(rate)
    except ValueError:
        return "ValueError"
    return "no error"


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Write a serializer for shop orders", [('try_order({"product": "cake", "quantity": 2})', ['ok', {'product': 'cake', 'quantity': 2, 'coupon': '', 'total': 10.0}]), ('try_order({"product": "tea", "quantity": 4, "coupon": " half "})', ['ok', {'product': 'tea', 'quantity': 4, 'coupon': 'HALF', 'total': 6.0}]), ('try_order({"product": "pizza", "quantity": 0})', ['errors', {'product': ['"pizza" is not a valid choice.'], 'quantity': ['Ensure this value is greater than or equal to 1.']}]), ('try_order({"product": "tea", "quantity": 1, "coupon": "FREE"})', ['errors', {'coupon': ['Unknown coupon.']}]), ('try_order({"product": "sandwich", "quantity": 1, "coupon": "HALF"})', ['errors', {'non_field_errors': ['HALF needs at least 2 items.']}]), ('try_order({"quantity": 3})', ['errors', {'product': ['This field is required.']}])]))
    results.append(check("Task 2: Write page number and cursor pagination", [('paginate(list(range(1, 6)), 1, 2, "/api/books/")', {'count': 5, 'next': '/api/books/?page=2', 'previous': None, 'results': [1, 2]}), ('paginate(list(range(1, 6)), 2, 2, "/api/books/")', {'count': 5, 'next': '/api/books/?page=3', 'previous': '/api/books/?page=1', 'results': [3, 4]}), ('paginate(list(range(1, 6)), 3, 2, "/api/books/")', {'count': 5, 'next': None, 'previous': '/api/books/?page=2', 'results': [5]}), ('paginate([], 1, 2, "/api/books/")', {'count': 0, 'next': None, 'previous': None, 'results': []}), ('[page_error(0), page_error(4), page_error(3)]', ['Invalid page.', 'Invalid page.', 'no error']), ('cursor_page([{"id": 5}, {"id": 2}, {"id": 9}, {"id": 7}], 0, 2)', {'results': [2, 5], 'next_cursor': 5}), ('cursor_page([{"id": 5}, {"id": 2}, {"id": 9}, {"id": 7}], 5, 2)', {'results': [7, 9], 'next_cursor': None})]))
    results.append(check("Task 3: Build a sliding window rate limiter", [('limiter_story("3/minute", [("ip1", 0), ("ip1", 10), ("ip1", 20), ("ip1", 30)])', [[True, 0], [True, 0], [True, 0], [False, 30]]), ('limiter_story("3/minute", [("ip1", 0), ("ip1", 10), ("ip1", 20), ("ip1", 60), ("ip1", 61)])', [[True, 0], [True, 0], [True, 0], [True, 0], [False, 9]]), ('limiter_story("1/second", [("a", 0), ("b", 0), ("a", 0.5), ("a", 1)])', [[True, 0], [True, 0], [False, 0.5], [True, 0]]), ('limiter_story("2/hour", [("u", 0), ("u", 100), ("u", 200), ("u", 3600), ("u", 3601)])', [[True, 0], [True, 0], [False, 3400], [True, 0], [False, 99]]), ('[rate_error("3/minute"), rate_error("3/week"), rate_error("many/day")]', ['no error', 'ValueError', 'ValueError'])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
