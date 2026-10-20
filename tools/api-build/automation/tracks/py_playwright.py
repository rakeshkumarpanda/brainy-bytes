TRACK = {
    'id': 'py-playwright', 'lang': 'py', 'tool': 'playwright',
    'title': 'Playwright with Python', 'emoji': '🎭',
    'tagline': 'API tests with APIRequestContext and pytest, from a first GET to fixtures, schemas, async calls, traces and UI plus API in one suite.',
    'intro': 'Playwright for Python is best known for browser tests, but it also ships a full HTTP client called <b>APIRequestContext</b>. It knows your base URL and default headers, sends JSON for you and records every call in a trace. With the <b>pytest-playwright</b> plugin you get a ready <code>playwright</code> fixture, a <code>base_url</code> setting and tracing switches, so API tests and UI tests can share one project, one runner and one CI job.',
    'stack': [
        ('Python', '3.13', '3.9 or newer works'),
        ('playwright', '1.64.0', 'APIRequestContext and expect'),
        ('pytest', '9.1.1', 'runner, fixtures, parametrize'),
        ('pytest-playwright', '0.10.0', 'playwright fixture, base_url, tracing'),
        ('jsonschema', '4.26.0', 'schema checks'),
        ('pydantic', '2.14.1', 'typed models'),
        ('pytest-xdist', '3.8.0', 'parallel runs'),
    ],
    'sections': [
        {
            'id': 'why', 'title': 'Why test APIs with Playwright for Python', 'emoji': '🎯', 'level': 'Basic',
            'blocks': [
                ('p', 'An API test sends an HTTP request and checks the response, with no browser. Playwright only starts a browser when a test asks for a <code>page</code>, so pure API tests run as fast as tests written with requests. The difference is everything that comes with Playwright around those calls.'),
                ('table', ['Feature', 'Why testers like it'], [
                    ['<code>APIRequestContext</code>', 'base URL, default headers, cookies and timeouts set once for every call'],
                    ['<code>expect(res).to_be_ok()</code>', 'prints the status and the response body when the status is not 2xx'],
                    ['Traces', 'every call with its headers, body and timing, viewable after a CI failure'],
                    ['Shared cookies with the browser', '<code>page.request</code> calls the API as the signed in user'],
                    ['Network mocking', '<code>page.route</code> fakes API answers so the UI can be tested against errors'],
                    ['Sync and async APIs', 'plain functions for pytest, or <code>async</code> code for many calls at once'],
                ]),
                ('table', ['Question', 'requests with pytest', 'Playwright with Python'], [
                    ['Only API tests, no UI at all', 'Simplest choice', 'Works well too'],
                    ['UI tests already use Playwright', 'Second client to learn', 'Same project and fixtures'],
                    ['Trace of every call in CI', 'Write your own logging', 'Built in'],
                    ['Seed data before a UI test', 'Separate session, separate cookies', '<code>page.request</code> shares the login'],
                ]),
                ('qa', 'If your team already writes Playwright UI tests in Python, add API tests to the same repo. Start by replacing slow UI setup steps, such as creating a booking through five screens, with a single API call.'),
            ],
        },
        {
            'id': 'setup', 'title': 'Project setup: packages, pytest.ini and conftest.py', 'emoji': '🧰', 'level': 'Basic',
            'blocks': [
                ('code', 'bash', 'Terminal', '''
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pytest                                 # run everything
pytest -m smoke                        # only tests marked smoke
pytest --base-url http://localhost:3001     # point at another server
pytest --tracing retain-on-failure     # keep a trace for every failed test
'''),
                ('code', 'plain', 'requirements.txt', '''
playwright==1.64.0
pytest==9.1.1
pytest-playwright==0.10.0
jsonschema==4.26.0
pydantic==2.14.1
pytest-xdist==3.8.0
''', {'save': 'requirements.txt'}),
                ('code', 'ini', 'pytest.ini', '''
[pytest]
testpaths = tests
pythonpath = .
base_url = https://restful-booker.herokuapp.com
addopts = -ra --strict-markers
markers =
    smoke: quick checks that run on every commit
''', {'save': 'pytest.ini'}),
                ('code', 'py', 'tests/conftest.py', '''
import uuid
from typing import Generator

import pytest
from playwright.sync_api import APIRequestContext, Playwright


@pytest.fixture(scope="session")
def api(playwright: Playwright, base_url: str) -> Generator[APIRequestContext, None, None]:
    """One HTTP client for the whole run, with the base URL and JSON headers set once."""
    ctx = playwright.request.new_context(
        base_url=base_url,
        extra_http_headers={"Accept": "application/json"},
        timeout=10_000,                     # milliseconds for every call
    )
    yield ctx
    ctx.dispose()                           # closes connections and frees memory
''', {'save': 'tests/conftest.py'}),
                ('code', 'plain', 'Project layout', '''
booker-playwright-py/
├── requirements.txt
├── pytest.ini
├── api/
│   └── booking_client.py   one method per endpoint
└── tests/
    ├── conftest.py         shared fixtures: api, token, booking
    ├── test_first.py
    ├── test_crud.py
    └── ...
'''),
                ('ul', [
                    '<b>pytest-playwright</b> gives you the <code>playwright</code> fixture, which starts Playwright once per run.',
                    'The <code>base_url</code> fixture reads <code>--base-url</code> from the command line, or <code>base_url</code> from pytest.ini.',
                    '<code>playwright.request.new_context()</code> creates the HTTP client. Every path you call is joined to its <code>base_url</code>.',
                ]),
                ('tip', 'API only projects never need a browser. Skip <code>playwright install</code> until you add UI tests, which keeps CI images small.'),
            ],
        },
        {
            'id': 'first-test', 'title': 'Your first test: GET a booking', 'emoji': '👋', 'level': 'Basic',
            'blocks': [
                ('code', 'py', 'tests/test_first.py', '''
import re

import pytest
from playwright.sync_api import APIRequestContext, expect


@pytest.mark.smoke
def test_ping_says_the_api_is_up(api: APIRequestContext):
    res = api.get("/ping")
    assert res.status == 201                # Restful Booker answers 201 to a health check


def test_get_one_booking(api: APIRequestContext):
    res = api.get("/booking/1")

    expect(res).to_be_ok()                  # any 2xx, and shows the body if not
    assert "application/json" in res.headers["content-type"]

    body = res.json()
    assert isinstance(body["firstname"], str) and body["firstname"]
    assert isinstance(body["totalprice"], int)
    assert isinstance(body["depositpaid"], bool)
    assert re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}", body["bookingdates"]["checkin"])
''', {'save': 'tests/test_first.py'}),
                ('table', ['Read', 'Gives'], [
                    ['<code>res.status</code>', 'the status code as an int, for example 200'],
                    ['<code>res.ok</code>', '<code>True</code> for any 2xx status'],
                    ['<code>res.headers</code>', 'a dict with lower case header names'],
                    ['<code>res.json()</code>', 'the body parsed into dicts and lists'],
                    ['<code>res.text()</code>', 'the body as a string, useful for plain text answers such as 404 Not Found'],
                    ['<code>res.body()</code>', 'the raw bytes, for files and images'],
                ]),
                ('warn', 'In Python, <code>status</code>, <code>ok</code>, <code>headers</code> and <code>url</code> are properties, while <code>json()</code>, <code>text()</code> and <code>body()</code> are methods. Writing <code>res.status()</code> raises a TypeError.'),
                ('try', {'method': 'GET', 'path': '/booking/1'}),
            ],
        },
        {
            'id': 'request', 'title': 'Request options: params, data, form, headers and timeouts', 'emoji': '🧱', 'level': 'Basic',
            'blocks': [
                ('code', 'py', 'Everything a call can take', '''
# Query parameters are encoded for you: /booking?firstname=Mary+Ann
api.get("/booking", params={"firstname": "Mary Ann", "lastname": "Brown"})

# A dict in data= becomes JSON with Content-Type: application/json
api.post("/booking", data=booking, headers={"X-Request-Id": str(uuid.uuid4())})

# Form fields and file uploads
api.post("/login", form={"user": "qa", "password": "secret"})
api.post("/documents", multipart={
    "file": {"name": "invoice.pdf", "mimeType": "application/pdf", "buffer": pdf_bytes},
    "note": "March",
})

# Limits and behaviour for one call
api.get("/slow-report", timeout=30_000)         # milliseconds
api.get("/booking/1", fail_on_status_code=True) # raise an error on 4xx and 5xx
api.get("/booking/1", max_retries=2)            # retry network errors such as ECONNRESET

# Any method, including HEAD and OPTIONS
api.fetch("/booking/1", method="HEAD")
'''),
                ('table', ['Option', 'Sends'], [
                    ['<code>params=</code>', 'query string, encoded for you'],
                    ['<code>data=</code>', 'JSON for dicts and lists, raw text for strings, raw bytes for bytes'],
                    ['<code>form=</code>', 'application/x-www-form-urlencoded'],
                    ['<code>multipart=</code>', 'multipart/form-data, for files'],
                    ['<code>headers=</code>', 'extra headers for this call, added to the context headers'],
                    ['<code>timeout=</code>', 'time limit in milliseconds, 0 means no limit'],
                    ['<code>fail_on_status_code=</code>', 'raise instead of returning a 4xx or 5xx response'],
                    ['<code>max_retries=</code>', 'retries for network errors only, never for bad status codes'],
                ]),
                ('tip', 'Timeouts in Playwright are milliseconds. In requests and httpx they are seconds. Mixing them up gives a 10 millisecond timeout that fails every call.'),
            ],
        },
        {
            'id': 'crud', 'title': 'Create, update and delete (CRUD)', 'emoji': '✍️', 'level': 'Basic',
            'blocks': [
                ('code', 'py', 'tests/test_crud.py', '''
import base64

from playwright.sync_api import APIRequestContext, expect

BASIC = "Basic " + base64.b64encode(b"admin:password123").decode()

NEW_BOOKING = {
    "firstname": "Rakesh",
    "lastname": "Panda",
    "totalprice": 250,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-11-01", "checkout": "2026-11-04"},
    "additionalneeds": "Breakfast",
}


def test_full_booking_life_cycle(api: APIRequestContext):
    # Create
    res = api.post("/booking", data=NEW_BOOKING)
    expect(res).to_be_ok()
    created = res.json()
    booking_id = created["bookingid"]
    assert booking_id > 0
    assert created["booking"] == NEW_BOOKING

    # Read it back
    assert api.get(f"/booking/{booking_id}").json()["lastname"] == "Panda"

    # Replace with PUT
    res = api.put(f"/booking/{booking_id}", headers={"Authorization": BASIC},
                  data={**NEW_BOOKING, "lastname": "Kumar", "totalprice": 300})
    assert res.json()["lastname"] == "Kumar"
    assert res.json()["totalprice"] == 300

    # Change one field with PATCH
    res = api.patch(f"/booking/{booking_id}", headers={"Authorization": BASIC},
                    data={"additionalneeds": "Dinner"})
    assert res.json()["additionalneeds"] == "Dinner"
    assert res.json()["lastname"] == "Kumar"          # PATCH kept the other fields

    # Delete, then it is gone
    res = api.delete(f"/booking/{booking_id}", headers={"Authorization": BASIC})
    assert res.status == 201                           # this API answers 201 to DELETE
    gone = api.get(f"/booking/{booking_id}")
    assert gone.status == 404
    assert gone.text() == "Not Found"
''', {'save': 'tests/test_crud.py'}),
                ('ul', [
                    'Put the PUT body in <code>data=</code>. Playwright turns the dict into JSON and sets the Content-Type header.',
                    'PUT replaces the whole booking, so it needs every field. PATCH sends only the fields that change.',
                    'The 404 body is plain text, so <code>res.json()</code> would raise. Read it with <code>res.text()</code>.',
                ]),
                ('warn', 'One long test like this stops at the first failed step and leaves the booking behind. The fixtures lesson shows how to give every test its own booking that is always cleaned up.'),
                ('try', {'method': 'POST', 'path': '/booking', 'body': {'firstname': 'Rakesh', 'lastname': 'Panda', 'totalprice': 250, 'depositpaid': True, 'bookingdates': {'checkin': '2026-11-01', 'checkout': '2026-11-04'}, 'additionalneeds': 'Breakfast'}}),
            ],
        },
        {
            'id': 'assertions', 'title': 'Assertions, readable failures and polling', 'emoji': '🔍', 'level': 'Intermediate',
            'blocks': [
                ('p', 'Playwright for Python has one web first assertion for API responses, <code>expect(res).to_be_ok()</code>. Everything else is a plain pytest <code>assert</code>, which prints both sides when it fails.'),
                ('code', 'py', 'tests/test_assertions.py', '''
import time

from playwright.sync_api import APIRequestContext, expect


def test_status_family(api: APIRequestContext):
    expect(api.get("/booking/1")).to_be_ok()
    expect(api.get("/booking/999999")).not_to_be_ok()


def test_shape_and_values(api: APIRequestContext):
    body = api.get("/booking/1").json()

    # the keys that must be there, extra keys are allowed
    assert {"firstname", "lastname", "totalprice", "depositpaid", "bookingdates"} <= body.keys()
    # a partial match on a few values
    assert {"firstname": body["firstname"], "depositpaid": body["depositpaid"]}.items() <= body.items()
    # rules rather than exact values
    assert body["totalprice"] >= 0
    assert body["bookingdates"]["checkin"] <= body["bookingdates"]["checkout"]


def test_list_contains_booking_one(api: APIRequestContext):
    ids = [row["bookingid"] for row in api.get("/booking").json()]
    assert 1 in ids
    assert len(ids) == len(set(ids)), "booking ids must be unique"


def test_response_time(api: APIRequestContext):
    start = time.perf_counter()
    res = api.get("/booking/1")
    took_ms = (time.perf_counter() - start) * 1000
    expect(res).to_be_ok()
    assert took_ms < 2000, f"took {took_ms:.0f} ms"
''', {'save': 'tests/test_assertions.py'}),
                ('code', 'py', 'tests/helpers.py: poll until a condition is true', '''
import time
from typing import Callable, TypeVar

T = TypeVar("T")


def poll(read: Callable[[], T], until: Callable[[T], bool], timeout_s: float = 30, every_s: float = 0.5) -> T:
    """Call read() until until(value) is true, or fail with the last value seen."""
    deadline = time.monotonic() + timeout_s
    while True:
        value = read()
        if until(value):
            return value
        if time.monotonic() > deadline:
            raise AssertionError(f"gave up after {timeout_s} s, last value: {value!r}")
        time.sleep(every_s)
''', {'save': 'tests/helpers.py'}),
                ('code', 'py', 'Using poll for a background job', '''
job = poll(lambda: api.get(f"/jobs/{job_id}").json(), until=lambda j: j["status"] == "DONE", timeout_s=60)
assert job["result"]["rows"] > 0
'''),
                ('tip', 'Add a message to important asserts, for example <code>assert res.status == 200, res.text()</code>. When the test fails in CI, the message shows the error body the server sent.'),
            ],
        },
        {
            'id': 'fixtures', 'title': 'Fixtures for tokens and test data', 'emoji': '🧷', 'level': 'Intermediate',
            'blocks': [
                ('p', 'Fixtures prepare what a test needs and clean it up afterwards. The code after <code>yield</code> is the cleanup, and pytest runs it even when the test fails. A session scoped fixture runs once per run, which suits a login token.'),
                ('code', 'py', 'tests/conftest.py (add these below the api fixture)', '''
@pytest.fixture(scope="session")
def token(api: APIRequestContext) -> str:
    res = api.post("/auth", data={"username": "admin", "password": "password123"})
    assert res.ok, res.text()
    body = res.json()
    assert "token" in body, f"login failed: {body}"     # a wrong password still answers 200
    return body["token"]


@pytest.fixture
def booking(api: APIRequestContext, token: str):
    """A fresh booking for one test, deleted afterwards even if the test fails."""
    data = {
        "firstname": f"Guest{uuid.uuid4().hex[:8]}",
        "lastname": "Fixture",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-10", "checkout": "2026-11-12"},
    }
    res = api.post("/booking", data=data)
    assert res.ok, res.text()
    booking_id = res.json()["bookingid"]

    yield {"id": booking_id, **data}

    api.delete(f"/booking/{booking_id}", headers={"Cookie": f"token={token}"})
''', {'append': 'tests/conftest.py'}),
                ('code', 'py', 'tests/test_fixtures.py', '''
from playwright.sync_api import APIRequestContext, expect


def test_read_a_fresh_booking(api: APIRequestContext, booking: dict):
    res = api.get(f"/booking/{booking['id']}")
    assert res.json()["firstname"] == booking["firstname"]


def test_patch_with_the_shared_token(api: APIRequestContext, booking: dict, token: str):
    res = api.patch(
        f"/booking/{booking['id']}",
        headers={"Cookie": f"token={token}"},
        data={"additionalneeds": "Late checkout"},
    )
    expect(res).to_be_ok()
    assert res.json()["additionalneeds"] == "Late checkout"
''', {'save': 'tests/test_fixtures.py'}),
                ('table', ['Scope', 'Runs', 'Good for'], [
                    ['<code>function</code> (default)', 'once per test', 'test data that a test changes'],
                    ['<code>module</code>', 'once per file', 'read only data shared by a file'],
                    ['<code>session</code>', 'once per run, or once per xdist worker', 'the API client and the login token'],
                ]),
                ('why', 'Every test gets its own booking and removes it afterwards. Tests can run in any order and in parallel without breaking each other.'),
            ],
        },
        {
            'id': 'auth', 'title': 'Authentication and negative tests', 'emoji': '🔐', 'level': 'Intermediate',
            'blocks': [
                ('code', 'py', 'Common styles', '''
# Per call
api.patch(url, headers={"Cookie": f"token={token}"}, data=changes)
api.get(url, headers={"Authorization": f"Bearer {os.environ['API_TOKEN']}"})

# For every call made by one context
admin = playwright.request.new_context(
    base_url=base_url,
    extra_http_headers={"Authorization": f"Bearer {os.environ['API_TOKEN']}"},
)

# Basic auth sent with the first request
admin = playwright.request.new_context(
    base_url=base_url,
    http_credentials={"username": "admin", "password": "password123", "send": "always"},
)
'''),
                ('code', 'py', 'tests/test_auth.py', '''
import base64

import pytest
from playwright.sync_api import APIRequestContext, Playwright, expect


def basic(user: str, password: str) -> dict:
    return {"Authorization": "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()}


@pytest.mark.parametrize("headers", [
    pytest.param({}, id="no auth"),
    pytest.param({"Cookie": "token=not-real"}, id="made up token"),
    pytest.param(basic("admin", "wrong"), id="wrong password"),
])
def test_update_is_refused(api: APIRequestContext, booking: dict, headers: dict):
    res = api.patch(f"/booking/{booking['id']}", headers=headers, data={"firstname": "Hacker"})
    assert res.status == 403
    assert api.get(f"/booking/{booking['id']}").json()["firstname"] != "Hacker"


def test_wrong_password_is_reported_in_the_body(api: APIRequestContext):
    res = api.post("/auth", data={"username": "admin", "password": "nope"})
    assert res.status == 200                       # a quirk of this API
    assert res.json() == {"reason": "Bad credentials"}


def test_http_credentials_with_send_always(playwright: Playwright, base_url: str, booking: dict):
    admin = playwright.request.new_context(
        base_url=base_url,
        http_credentials={"username": "admin", "password": "password123", "send": "always"},
    )
    try:
        res = admin.patch(f"/booking/{booking['id']}", data={"additionalneeds": "Spa"})
        expect(res).to_be_ok()
    finally:
        admin.dispose()
''', {'save': 'tests/test_auth.py'}),
                ('warn', 'Without <code>"send": "always"</code>, <code>http_credentials</code> waits for a 401 challenge before sending the password. Restful Booker answers 403, so the password would never be sent and the test would fail.'),
                ('qa', 'For every protected endpoint, test at least three cases: no credentials, wrong credentials and a valid token that lacks the right role. Then read the data again to prove nothing changed.'),
            ],
        },
        {
            'id': 'data-driven', 'title': 'Data driven tests with parametrize', 'emoji': '📊', 'level': 'Intermediate',
            'blocks': [
                ('code', 'py', 'tests/test_data.py', '''
import pytest
from playwright.sync_api import APIRequestContext, expect

VALID = {
    "firstname": "Test", "lastname": "User", "totalprice": 100, "depositpaid": True,
    "bookingdates": {"checkin": "2026-12-01", "checkout": "2026-12-03"},
}


@pytest.mark.parametrize("first, last", [
    ("Ann", "Lee"),
    ("José", "Núñez"),
    ("O'Brien", "Smith-Jones"),
    ("A", "B"),
])
def test_stores_the_name(api: APIRequestContext, first: str, last: str):
    res = api.post("/booking", data={**VALID, "firstname": first, "lastname": last})
    expect(res).to_be_ok()
    assert res.json()["booking"]["firstname"] == first


@pytest.mark.parametrize("field", ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"])
def test_missing_field_is_rejected(api: APIRequestContext, field: str):
    body = {k: v for k, v in VALID.items() if k != field}
    res = api.post("/booking", data=body)
    assert res.status != 200, "Restful Booker answers 500, a well built API answers 400"


@pytest.mark.parametrize("path, status", [
    ("/ping", 201),
    ("/booking", 200),
    ("/booking/999999", 404),
    ("/booking/abc", 404),
])
def test_status_codes(api: APIRequestContext, path: str, status: int):
    assert api.get(path).status == status
''', {'save': 'tests/test_data.py'}),
                ('code', 'py', 'Rows from a CSV file', '''
import csv
from pathlib import Path

ROWS = list(csv.DictReader(Path(__file__).with_name("guests.csv").open(encoding="utf-8")))


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r["firstname"])
def test_guest_from_csv(api, row):
    res = api.post("/booking", data={**VALID, "firstname": row["firstname"], "totalprice": int(row["price"])})
    expect(res).to_be_ok()
'''),
                ('tip', 'Give each case a readable id with <code>pytest.param(..., id="...")</code> or <code>ids=</code>. The report then says <code>test_update_is_refused[wrong password]</code> instead of a list of numbers.'),
            ],
        },
        {
            'id': 'schema', 'title': 'Schema checks with jsonschema and pydantic', 'emoji': '📐', 'level': 'Advanced',
            'blocks': [
                ('code', 'py', 'tests/test_schema.py', '''
import pytest
from jsonschema import Draft7Validator, FormatChecker
from playwright.sync_api import APIRequestContext
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, ValidationError
from datetime import date

BOOKING_SCHEMA = {
    "type": "object",
    "required": ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"],
    "properties": {
        "firstname": {"type": "string", "minLength": 1},
        "lastname": {"type": "string", "minLength": 1},
        "totalprice": {"type": "integer", "minimum": 0},
        "depositpaid": {"type": "boolean"},
        "bookingdates": {
            "type": "object",
            "required": ["checkin", "checkout"],
            "properties": {
                "checkin": {"type": "string", "format": "date"},
                "checkout": {"type": "string", "format": "date"},
            },
        },
        "additionalneeds": {"type": "string"},
    },
    "additionalProperties": False,
}
validator = Draft7Validator(BOOKING_SCHEMA, format_checker=FormatChecker())


def test_booking_matches_the_schema(api: APIRequestContext):
    errors = [f"{list(e.path)}: {e.message}" for e in validator.iter_errors(api.get("/booking/1").json())]
    assert errors == []


def test_schema_catches_a_renamed_field():
    bad = {"firstname": "A", "lastname": "B", "totalPrice": 1, "depositpaid": True,
           "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-02"}}
    messages = [e.message for e in validator.iter_errors(bad)]
    assert "'totalprice' is a required property" in messages


class Dates(BaseModel):
    checkin: date
    checkout: date


class Booking(BaseModel):
    model_config = ConfigDict(extra="forbid")
    firstname: StrictStr = Field(min_length=1)
    lastname: StrictStr = Field(min_length=1)
    totalprice: StrictInt = Field(ge=0)
    depositpaid: StrictBool
    bookingdates: Dates
    additionalneeds: StrictStr | None = None


def test_booking_parses_into_a_typed_model(api: APIRequestContext):
    booking = Booking.model_validate(api.get("/booking/1").json())
    assert booking.bookingdates.checkin <= booking.bookingdates.checkout


def test_model_rejects_a_price_sent_as_text():
    with pytest.raises(ValidationError):
        Booking.model_validate({"firstname": "A", "lastname": "B", "totalprice": "100", "depositpaid": True,
                                "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-02"}})
''', {'save': 'tests/test_schema.py'}),
                ('ul', [
                    '<b>jsonschema</b> checks the response against the same schema your OpenAPI file uses. <code>iter_errors</code> lists every problem at once.',
                    '<b>pydantic</b> turns the JSON into a typed object. <code>StrictInt</code> refuses <code>"100"</code> where a number is expected, which catches APIs that send numbers as text.',
                    'The dates stay in normal mode on purpose, so pydantic turns <code>"2026-01-01"</code> into a real <code>date</code> you can compare.',
                ]),
                ('tip', 'The second test in each pair checks the checker. A schema that never fails protects nothing.'),
            ],
        },
        {
            'id': 'framework', 'title': 'Framework design: a client class and fixtures', 'emoji': '🏗️', 'level': 'Advanced',
            'blocks': [
                ('p', 'As a suite grows, keep URLs and headers in one class with one method per endpoint. Tests then read like business steps, and a changed endpoint is fixed in one place.'),
                ('code', 'py', 'api/booking_client.py', '''
from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse


class BookingClient:
    def __init__(self, request: APIRequestContext):
        self.request = request
        self.headers: dict[str, str] = {}

    def login(self, username: str = "admin", password: str = "password123") -> "BookingClient":
        res = self.request.post("/auth", data={"username": username, "password": password})
        self.headers["Cookie"] = f"token={res.json()['token']}"
        return self

    def create(self, data: dict[str, Any]) -> APIResponse:
        return self.request.post("/booking", data=data)

    def get(self, booking_id: int) -> APIResponse:
        return self.request.get(f"/booking/{booking_id}")

    def find(self, **filters: str) -> list[int]:
        return [row["bookingid"] for row in self.request.get("/booking", params=filters).json()]

    def patch(self, booking_id: int, changes: dict[str, Any]) -> APIResponse:
        return self.request.patch(f"/booking/{booking_id}", headers=self.headers, data=changes)

    def remove(self, booking_id: int) -> APIResponse:
        return self.request.delete(f"/booking/{booking_id}", headers=self.headers)
''', {'save': 'api/booking_client.py'}),
                ('code', 'py', 'api/__init__.py', '''
from api.booking_client import BookingClient

__all__ = ["BookingClient"]
''', {'save': 'api/__init__.py'}),
                ('code', 'py', 'tests/test_framework.py', '''
import pytest
from playwright.sync_api import APIRequestContext

from api import BookingClient


@pytest.fixture
def bookings(api: APIRequestContext) -> BookingClient:
    return BookingClient(api).login()


def test_patch_through_the_client(bookings: BookingClient):
    created = bookings.create({
        "firstname": "Frame", "lastname": "Work", "totalprice": 120, "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-01", "checkout": "2026-11-02"},
    }).json()
    booking_id = created["bookingid"]

    assert booking_id in bookings.find(firstname="Frame")
    assert bookings.patch(booking_id, {"lastname": "Updated"}).json()["lastname"] == "Updated"
    assert bookings.remove(booking_id).status == 201
    assert bookings.get(booking_id).status == 404
''', {'save': 'tests/test_framework.py'}),
                ('table', ['Layer', 'Holds', 'Never holds'], [
                    ['<code>api/</code> client', 'paths, headers, auth, request building', 'assertions'],
                    ['<code>conftest.py</code>', 'clients, tokens, test data, cleanup', 'business checks'],
                    ['<code>tests/</code>', 'steps and assertions', 'URLs or raw headers'],
                ]),
            ],
        },
        {
            'id': 'ui-api', 'title': 'UI and API together', 'emoji': '🖥️', 'level': 'Advanced',
            'blocks': [
                ('p', 'This is where Playwright beats every other Python HTTP client. Inside a UI test, <code>page.request</code> shares cookies with the browser, <code>page.expect_response</code> captures what the page sends, and <code>page.route</code> fakes API answers. These examples need a web app and <code>playwright install chromium</code>.'),
                ('code', 'py', 'Seed by API, check in the UI, then check what the UI sent', '''
from playwright.sync_api import Page, expect


def test_new_booking_shows_on_the_dashboard(page: Page):
    # 1. create data in milliseconds, with the same cookies as the browser
    res = page.request.post("/api/bookings", data={"guest": "Rakesh Panda", "nights": 3})
    booking_id = res.json()["id"]

    # 2. check the UI
    page.goto(f"/bookings/{booking_id}")
    expect(page.get_by_role("heading")).to_contain_text("Rakesh Panda")

    # 3. check the API call the page makes when the user saves
    with page.expect_response(lambda r: f"/api/bookings/{booking_id}" in r.url and r.request.method == "PATCH") as info:
        page.get_by_label("Nights").fill("4")
        page.get_by_role("button", name="Save").click()
    saved = info.value
    assert saved.status == 200
    assert saved.request.post_data_json == {"nights": 4}
'''),
                ('code', 'py', 'Mock the API to test error handling in the UI', '''
def test_dashboard_shows_a_friendly_error(page: Page):
    page.route("**/api/bookings", lambda route: route.fulfill(status=500, json={"error": "down"}))
    page.goto("/bookings")
    expect(page.get_by_text("Something went wrong")).to_be_visible()
'''),
                ('code', 'py', 'Log in once by API and reuse the session in every UI test', '''
@pytest.fixture(scope="session")
def storage_state(playwright, base_url, tmp_path_factory):
    path = tmp_path_factory.mktemp("auth") / "qa.json"
    ctx = playwright.request.new_context(base_url=base_url)
    ctx.post("/api/login", form={"user": "qa", "password": os.environ["QA_PASSWORD"]})
    ctx.storage_state(path=path)              # saves the cookies the login set
    ctx.dispose()
    return path


@pytest.fixture
def browser_context_args(browser_context_args, storage_state):
    return {**browser_context_args, "storage_state": storage_state}
'''),
                ('qa', '<code>expect_response</code> lets a UI test assert on the exact request the page sent. It catches bugs where the screen looks right but the wrong data reaches the server.'),
            ],
        },
        {
            'id': 'async', 'title': 'Async API calls for speed', 'emoji': '⚡', 'level': 'Advanced',
            'blocks': [
                ('p', 'The sync API sends one call at a time. The async API in <code>playwright.async_api</code> can keep many calls in flight with <code>asyncio.gather</code>. Use it for seeding lots of data, quick load checks and concurrency tests.'),
                ('code', 'py', 'scripts/parallel_calls.py', '''
import asyncio
import os
import time

from playwright.async_api import async_playwright

BASE = os.getenv("BASE_URL", "https://restful-booker.herokuapp.com")


def new_booking(i: int) -> dict:
    return {"firstname": f"Async{i}", "lastname": "Guest", "totalprice": 100 + i, "depositpaid": True,
            "bookingdates": {"checkin": "2026-10-01", "checkout": "2026-10-02"}}


async def main() -> None:
    async with async_playwright() as p:
        api = await p.request.new_context(base_url=BASE)
        try:
            start = time.perf_counter()
            responses = await asyncio.gather(*(api.post("/booking", data=new_booking(i)) for i in range(5)))
            took = time.perf_counter() - start

            ids = [(await r.json())["bookingid"] for r in responses]
            assert all(r.ok for r in responses)
            assert len(set(ids)) == 5, f"ids must be unique, got {ids}"
            print(f"created {ids} in {took:.2f} s")
        finally:
            await api.dispose()


if __name__ == "__main__":
    asyncio.run(main())
''', {'save': 'scripts/parallel_calls.py'}),
                ('warn', 'Do not share one sync Playwright object between threads. For parallel work use the async API, or run tests in separate processes with pytest-xdist.'),
            ],
        },
        {
            'id': 'parallel-ci', 'title': 'Markers, parallel runs, traces and CI', 'emoji': '🚀', 'level': 'Expert',
            'blocks': [
                ('code', 'bash', 'Run options', '''
pytest -n 4                                  # 4 worker processes with pytest-xdist
pytest -m "smoke and not slow"               # pick tests by marker
pytest --lf                                  # rerun only last failures
pytest --tracing retain-on-failure           # trace.zip for each failed test
playwright show-trace test-results/<test-name>/trace.zip
pytest --junitxml=results/junit.xml          # report for CI dashboards
'''),
                ('ul', [
                    'With <code>--tracing</code>, pytest-playwright 0.10 also records the API request contexts you create, so each call appears in the trace with method, URL, headers, body and timing.',
                    'Session fixtures run once per xdist worker. With <code>-n 4</code> you log in four times, which is fine for most APIs.',
                    'Give every test its own data, as in the fixtures lesson. Shared bookings are the main cause of flaky parallel runs.',
                ]),
                ('code', 'yaml', '.github/workflows/api-tests.yml', '''
name: API tests
on: [push, pull_request]
jobs:
  api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
          cache: pip
      - run: pip install -r requirements.txt
      - run: pytest -n 4 --tracing retain-on-failure --junitxml=results/junit.xml --base-url "${{ vars.BASE_URL }}"
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: api-test-results
          path: |
            results
            test-results
'''),
                ('tip', 'No <code>playwright install</code> step is needed for API tests. Add <code>playwright install --with-deps chromium</code> only when the suite gains UI tests.'),
            ],
        },
        {
            'id': 'expert', 'title': 'Expert topics: contracts, GraphQL, idempotency and flaky networks', 'emoji': '🧠', 'level': 'Expert',
            'blocks': [
                ('ul', [
                    '<b>Contract checks</b>: load the component schemas from your OpenAPI file once in a session fixture and validate every response against them.',
                    '<b>GraphQL</b>: <code>api.post("/graphql", data={"query": q, "variables": v})</code>, then assert that the body has no <code>errors</code> key, because GraphQL often answers 200 for failures.',
                    '<b>Idempotency</b>: send the same PUT twice and check that the second call changes nothing. Send the same POST twice with an Idempotency-Key header and check you get one record.',
                    '<b>Network errors</b>: <code>max_retries=2</code> retries resets and refused connections only. It never hides a 500.',
                    '<b>Clean contexts</b>: create a new context for each user role with its own <code>extra_http_headers</code> and dispose it in the fixture teardown.',
                    '<b>Storage state</b>: <code>ctx.storage_state(path=...)</code> saves cookies from an API login, and a browser context can start already signed in.',
                ]),
                ('code', 'py', 'tests/test_expert.py', '''
from playwright.sync_api import APIRequestContext, expect


def test_put_twice_gives_the_same_result(api: APIRequestContext, booking: dict, token: str):
    auth = {"Cookie": f"token={token}"}
    body = {k: v for k, v in booking.items() if k != "id"} | {"lastname": "Same"}
    first = api.put(f"/booking/{booking['id']}", headers=auth, data=body).json()
    second = api.put(f"/booking/{booking['id']}", headers=auth, data=body).json()
    assert first == second


def test_every_listed_booking_can_be_read(api: APIRequestContext):
    for row in api.get("/booking").json()[:5]:
        expect(api.get(f"/booking/{row['bookingid']}")).to_be_ok()


def test_dispose_frees_the_context(playwright, base_url):
    ctx = playwright.request.new_context(base_url=base_url)
    assert ctx.get("/ping").status == 201
    ctx.dispose()
''', {'save': 'tests/test_expert.py'}),
            ],
        },
        {
            'id': 'scenario', 'title': 'Real world scenario: a hotel front desk day', 'emoji': '🏨', 'level': 'Scenario',
            'blocks': [
                ('p', 'The receptionist logs in, books a room, adds breakfast, and the guest later cancels. Someone without a login also tries to cancel. Each step is a small function, so a failure names the exact step that broke.'),
                ('flow', [
                    ('Health check', '<code>GET /ping</code> answers 201.'),
                    ('Log in', 'The session fixture provides a token.'),
                    ('Book', '<code>POST /booking</code> with a unique guest.'),
                    ('Search', 'The new id appears in <code>GET /booking?firstname=...</code>.'),
                    ('Add breakfast', '<code>PATCH</code> with the token.'),
                    ('Unauthorised cancel', '<code>DELETE</code> without a token gives 403.'),
                    ('Cancel', '<code>DELETE</code> with the token gives 201.'),
                    ('Gone', '<code>GET</code> gives 404.'),
                ]),
                ('code', 'py', 'tests/test_journey.py', '''
import uuid

from playwright.sync_api import APIRequestContext, expect


def test_front_desk_day(api: APIRequestContext, token: str):
    auth = {"Cookie": f"token={token}"}
    guest = f"Guest{uuid.uuid4().hex[:8]}"

    # the API is up
    assert api.get("/ping").status == 201

    # book a room
    res = api.post("/booking", data={
        "firstname": guest, "lastname": "Panda", "totalprice": 250, "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-01", "checkout": "2026-11-04"},
    })
    expect(res).to_be_ok()
    booking_id = res.json()["bookingid"]

    # find it by name
    assert {"bookingid": booking_id} in api.get("/booking", params={"firstname": guest}).json()

    # add breakfast
    res = api.patch(f"/booking/{booking_id}", headers=auth, data={"additionalneeds": "Breakfast"})
    assert res.json()["additionalneeds"] == "Breakfast"
    assert res.json()["lastname"] == "Panda"

    # cancelling without a login is refused, and the booking is still there
    assert api.delete(f"/booking/{booking_id}").status == 403
    expect(api.get(f"/booking/{booking_id}")).to_be_ok()

    # cancel and confirm
    assert api.delete(f"/booking/{booking_id}", headers=auth).status == 201
    assert api.get(f"/booking/{booking_id}").status == 404
''', {'save': 'tests/test_journey.py'}),
                ('qa', 'Real front desk systems add more steps, such as payment and email. The pattern stays the same: create your own data, act through the API, check the state after every step, and clean up.'),
            ],
        },
    ],
    'quiz': [
        {'lv': 'e', 'q': 'Which Playwright object sends API requests without a browser?', 'o': ['<code>Page</code>', '<code>APIRequestContext</code>', '<code>BrowserContext</code>', '<code>Locator</code>'], 'a': 1, 'hint': 'You create it with playwright.request.new_context().', 'why': '<code>APIRequestContext</code> is the HTTP client. It holds the base URL, headers, cookies and timeouts for its calls.'},
        {'lv': 'e', 'q': 'How do you read the status code of a Python <code>APIResponse</code>?', 'o': ['<code>res.status()</code>', '<code>res.status</code>', '<code>res.status_code</code>', '<code>res.code</code>'], 'a': 1, 'hint': 'In Python it is a property.', 'why': '<code>status</code> is a property in Python. <code>status_code</code> belongs to requests, and <code>status()</code> is the JavaScript style.'},
        {'lv': 'm', 'q': 'Which argument sends a dict as a JSON body?', 'o': ['<code>json=</code>', '<code>data=</code>', '<code>body=</code>', '<code>form=</code>'], 'a': 1, 'hint': 'requests uses a different name for this.', 'why': 'In Playwright, <code>data=</code> serializes dicts as JSON and sets the Content-Type. <code>form=</code> sends form fields.'},
        {'lv': 'm', 'q': 'You pass <code>timeout=10</code> to a call. What happens?', 'o': ['It waits 10 seconds', 'It waits 10 milliseconds and almost always fails', 'It retries 10 times', 'Nothing, timeouts are ignored'], 'a': 1, 'hint': 'Check the unit.', 'why': 'Playwright timeouts are in milliseconds, so 10 means 10 ms. Use <code>10_000</code> for 10 seconds.'},
        {'lv': 'h', 'q': 'Why must <code>http_credentials</code> use <code>"send": "always"</code> for Restful Booker?', 'o': ['It is faster', 'Without it the password waits for a 401 challenge, and this API answers 403', 'It encrypts the password', 'It is needed for cookies'], 'a': 1, 'hint': 'Which status code triggers the default behaviour.', 'why': 'By default the credentials are only sent after a 401 with a WWW-Authenticate header. Restful Booker answers 403, so they would never be sent.'},
        {'lv': 'h', 'q': 'A UI test must check the JSON the page sent when the user clicked Save. What do you use?', 'o': ['<code>page.route</code> only', '<code>page.expect_response</code>, then <code>response.request.post_data_json</code>', 'Read the DOM', 'It is not possible'], 'a': 1, 'hint': 'Wait for the network event.', 'why': '<code>expect_response</code> captures the response, and its <code>request</code> gives the method, headers and body the page sent.'},
        {'lv': 'x', 'q': 'With <code>pytest -n 4</code>, how often does a session scoped login fixture run?', 'o': ['Once', 'Once per worker, so up to 4 times', 'Once per test', 'Never'], 'a': 1, 'hint': 'xdist workers are separate processes.', 'why': 'Each xdist worker is its own Python process with its own session, so session fixtures run once in each worker.'},
        {'lv': 'x', 'q': 'What does <code>max_retries=2</code> retry?', 'o': ['Any status from 500 to 599', 'Network errors such as a reset connection', 'Failed assertions', 'Every call twice'], 'a': 1, 'hint': 'It never hides a server error.', 'why': 'It retries only network level failures. A 500 is a real answer from the server and is returned to the test as is.'},
    ],
}
