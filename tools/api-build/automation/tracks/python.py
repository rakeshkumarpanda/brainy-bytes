TRACK = {
    'id': 'python', 'lang': 'py', 'tool': 'requests',
    'title': 'API testing with Python', 'emoji': '🐍',
    'tagline': 'requests and pytest for everyday tests, httpx for async, plus schemas, mocks, parallel runs and CI.',
    'intro': 'Python is one of the quickest languages for API testing. <b>requests</b> sends HTTP calls in one line, <b>pytest</b> finds and runs tests with plain <code>assert</code> statements, and <b>fixtures</b> handle setup such as tokens and test data. This track goes from a first GET to async tests with <b>httpx</b>, schema checks with <b>jsonschema</b> and <b>pydantic</b>, mocking with <b>responses</b> and <b>respx</b>, property based testing with <b>Schemathesis</b>, and parallel runs in CI.',
    'stack': [
        ('Python', '3.13', '3.10 or newer works'),
        ('requests', '2.34.2', 'simple HTTP calls'),
        ('pytest', '9.1.1', 'runner, fixtures, parametrize'),
        ('httpx', '0.28.1', 'sync and async HTTP'),
        ('jsonschema', '4.26.0', 'schema checks'),
        ('pydantic', '2.14.1', 'typed models'),
        ('responses and respx', '0.26 and 0.23', 'mocking'),
        ('pytest-xdist', '3.8.0', 'parallel runs'),
    ],
    'sections': [
        {
            'id': 'why', 'title': 'What API automation is and what to check', 'emoji': '🎯', 'level': 'Basic',
            'blocks': [
                ('p', 'An API test sends a real HTTP request and checks the response, with no browser. API tests are fast and stable, so teams keep many of them in the middle of the test pyramid. Python is popular here because the code is short and easy to read, even for testers who are new to programming.'),
                ('table', ['Check', 'Example', 'Python'], [
                    ['Status', '<code>GET /booking/1</code> gives 200', '<code>assert res.status_code == 200</code>'],
                    ['Body value', 'firstname is a string', '<code>assert isinstance(res.json()["firstname"], str)</code>'],
                    ['Header', 'JSON content type', '<code>assert "application/json" in res.headers["Content-Type"]</code>'],
                    ['Time', 'under 2 seconds', '<code>assert res.elapsed.total_seconds() &lt; 2</code>'],
                    ['Negative', 'update without token gives 403', '<code>assert res.status_code == 403</code>'],
                    ['Shape', 'matches the schema', '<code>validate(res.json(), schema)</code>'],
                ]),
                ('qa', 'pytest prints the actual values when an <code>assert</code> fails, for example <code>assert 404 == 200</code>. You do not need special assertion methods, which keeps tests easy to read for the whole team.'),
            ],
        },
        {
            'id': 'setup', 'title': 'Project setup: venv, packages and layout', 'emoji': '🧰', 'level': 'Basic',
            'blocks': [
                ('code', 'bash', 'Terminal', '''
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pytest                             # run everything
pytest -k crud -v                  # run tests whose name contains "crud"
BASE_URL=http://localhost:3001 pytest   # point at another server
'''),
                ('code', 'plain', 'requirements.txt', '''
requests==2.34.2
pytest==9.1.1
httpx==0.28.1
jsonschema==4.26.0
pydantic==2.14.1
responses==0.26.3
respx==0.23.1
pytest-asyncio==1.4.0
pytest-xdist==3.8.0
tenacity==9.2.1
''', {'save': 'requirements.txt'}),
                ('code', 'ini', 'pytest.ini', '''
[pytest]
testpaths = tests
pythonpath = .
addopts = -ra --strict-markers
markers =
    smoke: quick checks that run on every commit
asyncio_default_fixture_loop_scope = function
''', {'save': 'pytest.ini'}),
                ('code', 'plain', 'Project layout', '''
booker-api-tests/
├── requirements.txt
├── pytest.ini
├── api/
│   └── client.py          one method per endpoint
├── schemas/
│   └── booking.json
└── tests/
    ├── conftest.py        shared fixtures: base_url, session, token, booking
    ├── test_first.py
    ├── test_crud.py
    └── ...
'''),
                ('tip', 'pytest finds files named <code>test_*.py</code> and functions named <code>test_*</code>. No classes or main method are needed.'),
            ],
        },
        {
            'id': 'first-test', 'title': 'Your first test: GET a booking', 'emoji': '👋', 'level': 'Basic',
            'blocks': [
                ('code', 'py', 'tests/test_first.py', '''
import os

import pytest
import requests

BASE = os.getenv("BASE_URL", "https://restful-booker.herokuapp.com")


@pytest.mark.smoke
def test_ping_says_the_api_is_up():
    res = requests.get(f"{BASE}/ping", timeout=10)
    assert res.status_code == 201          # Restful Booker answers 201 to a health check


def test_get_one_booking():
    res = requests.get(f"{BASE}/booking/1", headers={"Accept": "application/json"}, timeout=10)

    assert res.status_code == 200
    assert "application/json" in res.headers["Content-Type"]

    body = res.json()
    assert isinstance(body["firstname"], str) and body["firstname"]
    assert set(body["bookingdates"]) == {"checkin", "checkout"}
    assert res.elapsed.total_seconds() < 5
''', {'save': 'tests/test_first.py'}),
                ('ul', [
                    '<code>requests.get(url)</code> sends the call and waits for the answer.',
                    '<code>timeout=10</code> stops a call that hangs. requests has no timeout by default, so always pass one.',
                    '<code>res.json()</code> turns the body into Python dicts and lists.',
                    '<code>res.headers</code> ignores case, so <code>content-type</code> works too.',
                ]),
                ('try', {'method': 'GET', 'path': '/booking/1'}),
            ],
        },
        {
            'id': 'request', 'title': 'Building requests: params, headers, cookies and sessions', 'emoji': '🧱', 'level': 'Basic',
            'blocks': [
                ('code', 'py', 'Every part of a request', '''
# Query parameters are encoded for you: /booking?firstname=Mary+Ann
requests.get(f"{BASE}/booking", params={"firstname": "Mary Ann"}, timeout=10)

# Headers and cookies
requests.get(
    f"{BASE}/booking/1",
    headers={"Accept": "application/json", "X-Request-Id": "test-42"},
    cookies={"token": "abc123"},
    timeout=(3, 10),          # 3 s to connect, 10 s to read
)

# A Session keeps headers, cookies and open connections between calls
session = requests.Session()
session.headers.update({"Accept": "application/json"})
session.get(f"{BASE}/booking/1", timeout=10)
'''),
                ('table', ['Argument', 'Sends'], [
                    ['<code>params=</code>', 'query string'],
                    ['<code>json=</code>', 'a JSON body and the <code>Content-Type: application/json</code> header'],
                    ['<code>data=</code>', 'form fields or raw text'],
                    ['<code>files=</code>', 'multipart file upload'],
                    ['<code>headers=</code>', 'extra headers'],
                    ['<code>cookies=</code>', 'cookies'],
                    ['<code>auth=</code>', 'Basic auth as a tuple'],
                    ['<code>timeout=</code>', 'seconds, or a (connect, read) tuple'],
                ]),
                ('tip', 'Use a <code>Session</code> in test suites. It reuses connections, so a suite of hundreds of calls runs noticeably faster.'),
            ],
        },
        {
            'id': 'crud', 'title': 'Create, update and delete (CRUD)', 'emoji': '✍️', 'level': 'Basic',
            'blocks': [
                ('code', 'py', 'tests/test_crud.py', '''
import os

import requests

BASE = os.getenv("BASE_URL", "https://restful-booker.herokuapp.com")
ADMIN = ("admin", "password123")

NEW_BOOKING = {
    "firstname": "Rakesh",
    "lastname": "Panda",
    "totalprice": 250,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-11-01", "checkout": "2026-11-04"},
    "additionalneeds": "Breakfast",
}


def test_full_crud_cycle():
    # Create
    res = requests.post(f"{BASE}/booking", json=NEW_BOOKING, timeout=10)
    assert res.status_code == 200
    booking_id = res.json()["bookingid"]
    assert res.json()["booking"] == NEW_BOOKING          # the whole object in one check

    # Read
    res = requests.get(f"{BASE}/booking/{booking_id}", timeout=10)
    assert res.json() == NEW_BOOKING

    # Replace with PUT (every field)
    changed = {**NEW_BOOKING, "lastname": "Kumar", "totalprice": 300}
    res = requests.put(f"{BASE}/booking/{booking_id}", json=changed, auth=ADMIN, timeout=10)
    assert res.status_code == 200
    assert res.json()["lastname"] == "Kumar"

    # Change one field with PATCH
    res = requests.patch(f"{BASE}/booking/{booking_id}", json={"additionalneeds": "Dinner"}, auth=ADMIN, timeout=10)
    assert res.json()["additionalneeds"] == "Dinner"
    assert res.json()["lastname"] == "Kumar"              # untouched fields stay

    # Delete, then confirm it is gone
    res = requests.delete(f"{BASE}/booking/{booking_id}", auth=ADMIN, timeout=10)
    assert res.status_code == 201                         # this API answers 201
    assert requests.get(f"{BASE}/booking/{booking_id}", timeout=10).status_code == 404
''', {'save': 'tests/test_crud.py'}),
                ('tip', 'Comparing whole dicts with <code>==</code> is one of Python\'s best features for API tests. When they differ, pytest shows exactly which keys changed.'),
                ('try', {'method': 'POST', 'path': '/booking', 'body': {'firstname': 'Rakesh', 'lastname': 'Panda', 'totalprice': 250, 'depositpaid': True, 'bookingdates': {'checkin': '2026-11-01', 'checkout': '2026-11-04'}, 'additionalneeds': 'Breakfast'}}),
            ],
        },
        {
            'id': 'fixtures', 'title': 'Fixtures and conftest.py', 'emoji': '🧷', 'level': 'Intermediate',
            'blocks': [
                ('p', 'A <b>fixture</b> is a function that prepares something a test needs. A test asks for it by naming it as an argument. Code after <code>yield</code> runs after the test, which makes cleanup automatic. Fixtures in <code>conftest.py</code> are shared by every test in the folder.'),
                ('code', 'py', 'tests/conftest.py', '''
import os
import time

import pytest
import requests


@pytest.fixture(scope="session")
def base_url():
    return os.getenv("BASE_URL", "https://restful-booker.herokuapp.com")


@pytest.fixture(scope="session")
def api(base_url):
    """One shared session for the whole run."""
    s = requests.Session()
    s.headers.update({"Accept": "application/json"})
    yield s
    s.close()


@pytest.fixture(scope="session")
def token(api, base_url):
    res = api.post(f"{base_url}/auth", json={"username": "admin", "password": "password123"}, timeout=10)
    assert res.status_code == 200, res.text
    return res.json()["token"]


@pytest.fixture
def booking(api, base_url, token):
    """Create a fresh booking for one test, then delete it afterwards."""
    data = {
        "firstname": f"Guest{time.time_ns()}",
        "lastname": "Fixture",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-10", "checkout": "2026-11-12"},
        "additionalneeds": "None",
    }
    res = api.post(f"{base_url}/booking", json=data, timeout=10)
    assert res.status_code == 200, res.text
    booking_id = res.json()["bookingid"]

    yield {"id": booking_id, **data}

    api.delete(f"{base_url}/booking/{booking_id}", cookies={"token": token}, timeout=10)
''', {'save': 'tests/conftest.py'}),
                ('code', 'py', 'tests/test_fixtures.py', '''
def test_read_uses_a_fresh_booking(api, base_url, booking):
    res = api.get(f"{base_url}/booking/{booking['id']}", timeout=10)
    assert res.status_code == 200
    assert res.json()["firstname"] == booking["firstname"]


def test_patch_with_the_session_token(api, base_url, booking, token):
    res = api.patch(
        f"{base_url}/booking/{booking['id']}",
        json={"additionalneeds": "Late checkout"},
        cookies={"token": token},
        timeout=10,
    )
    assert res.status_code == 200
    assert res.json()["additionalneeds"] == "Late checkout"
''', {'save': 'tests/test_fixtures.py'}),
                ('table', ['Scope', 'Created', 'Good for'], [
                    ['<code>function</code> (default)', 'once per test', 'test data that a test changes'],
                    ['<code>module</code>', 'once per file', 'data shared by a file of read only tests'],
                    ['<code>session</code>', 'once per run', 'the HTTP session, config, auth token'],
                ]),
                ('why', 'Every test gets its own booking and cleans it up, even when the test fails. Tests never depend on each other or on data someone else created.'),
            ],
        },
        {
            'id': 'auth', 'title': 'Authentication styles', 'emoji': '🔐', 'level': 'Intermediate',
            'blocks': [
                ('code', 'py', 'Basic, cookie, Bearer, API key and OAuth 2', '''
# Basic auth, sent on the first request
requests.put(url, json=data, auth=("admin", "password123"), timeout=10)

# Token cookie (Restful Booker)
requests.put(url, json=data, cookies={"token": token}, timeout=10)

# Bearer token for one session
session.headers["Authorization"] = f"Bearer {os.environ['API_TOKEN']}"

# API key
requests.get(url, headers={"x-api-key": os.environ["API_KEY"]}, timeout=10)

# OAuth 2 client credentials
res = requests.post(
    "https://auth.example.com/oauth2/token",
    data={"grant_type": "client_credentials", "scope": "bookings.read"},
    auth=(os.environ["CLIENT_ID"], os.environ["CLIENT_SECRET"]),
    timeout=10,
)
access_token = res.json()["access_token"]
'''),
                ('code', 'py', 'tests/test_auth.py', '''
import pytest


@pytest.mark.parametrize("how", ["no auth", "bad token", "bad password"])
def test_update_is_refused(api, base_url, booking, how):
    kwargs = {
        "no auth": {},
        "bad token": {"cookies": {"token": "not-a-real-token"}},
        "bad password": {"auth": ("admin", "wrong")},
    }[how]

    res = api.patch(f"{base_url}/booking/{booking['id']}", json={"firstname": "Hacker"}, timeout=10, **kwargs)

    assert res.status_code == 403
    assert api.get(f"{base_url}/booking/{booking['id']}", timeout=10).json()["firstname"] != "Hacker"


def test_login_with_wrong_password_gives_no_token(api, base_url):
    res = api.post(f"{base_url}/auth", json={"username": "admin", "password": "nope"}, timeout=10)
    assert res.status_code == 200                    # a quirk: still 200
    assert res.json() == {"reason": "Bad credentials"}
''', {'save': 'tests/test_auth.py'}),
                ('qa', 'Restful Booker returns 200 with <code>{"reason": "Bad credentials"}</code> for a wrong password. Many teams would log this as a bug, because 401 is the correct status. Your test documents the real behaviour and makes it visible.'),
                ('warn', 'Keep secrets in environment variables or a CI secret store. Never print tokens in test output.'),
            ],
        },
        {
            'id': 'parametrize', 'title': 'Data driven tests with parametrize', 'emoji': '📊', 'level': 'Intermediate',
            'blocks': [
                ('code', 'py', 'tests/test_params.py', '''
import json
from pathlib import Path

import pytest

VALID = {
    "firstname": "Test",
    "lastname": "User",
    "totalprice": 100,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-12-01", "checkout": "2026-12-03"},
}


@pytest.mark.parametrize(
    "first,last",
    [
        ("Ann", "Lee"),
        ("José", "Núñez"),
        ("O'Brien", "Smith-Jones"),
        ("A", "B"),
    ],
    ids=["plain", "accents", "symbols", "shortest"],
)
def test_names_are_kept(api, base_url, first, last):
    res = api.post(f"{base_url}/booking", json={**VALID, "firstname": first, "lastname": last}, timeout=10)
    assert res.status_code == 200
    assert res.json()["booking"]["firstname"] == first


@pytest.mark.parametrize("field", ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"])
def test_missing_required_field_is_rejected(api, base_url, field):
    body = {k: v for k, v in VALID.items() if k != field}
    res = api.post(f"{base_url}/booking", json=body, timeout=10)
    assert res.status_code != 200, "Restful Booker answers 500 here. A good API answers 400."


CASES = json.loads((Path(__file__).parent / "status_cases.json").read_text())


@pytest.mark.parametrize("case", CASES, ids=[c["path"] for c in CASES])
def test_status_from_a_file(api, base_url, case):
    assert api.get(f"{base_url}{case['path']}", timeout=10).status_code == case["status"]
''', {'save': 'tests/test_params.py'}),
                ('code', 'json', 'tests/status_cases.json', '''
[
  { "path": "/ping",           "status": 201 },
  { "path": "/booking",        "status": 200 },
  { "path": "/booking/1",      "status": 200 },
  { "path": "/booking/999999", "status": 404 },
  { "path": "/booking/abc",    "status": 404 }
]
''', {'save': 'tests/status_cases.json'}),
                ('tip', 'The <code>ids</code> list gives each row a readable name in the report, such as <code>test_names_are_kept[accents]</code>.'),
            ],
        },
        {
            'id': 'schema', 'title': 'Schema checks with jsonschema and pydantic', 'emoji': '📐', 'level': 'Advanced',
            'blocks': [
                ('p', 'Two good options. <b>jsonschema</b> checks a response against a JSON Schema file, which can be shared with other teams and tools. <b>pydantic</b> describes the shape as Python classes and gives you typed objects to use in the rest of the test.'),
                ('code', 'json', 'schemas/booking.json', '''
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"],
  "properties": {
    "firstname":   { "type": "string", "minLength": 1 },
    "lastname":    { "type": "string", "minLength": 1 },
    "totalprice":  { "type": "integer", "minimum": 0 },
    "depositpaid": { "type": "boolean" },
    "bookingdates": {
      "type": "object",
      "required": ["checkin", "checkout"],
      "properties": {
        "checkin":  { "type": "string", "format": "date" },
        "checkout": { "type": "string", "format": "date" }
      }
    },
    "additionalneeds": { "type": "string" }
  }
}
''', {'save': 'schemas/booking.json'}),
                ('code', 'py', 'tests/test_schema.py', '''
import json
from datetime import date
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from pydantic import BaseModel, Field, ValidationError, model_validator

SCHEMA = json.loads((Path(__file__).parents[1] / "schemas" / "booking.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def test_booking_matches_json_schema(api, base_url, booking):
    body = api.get(f"{base_url}/booking/{booking['id']}", timeout=10).json()
    errors = [f"{list(e.path)}: {e.message}" for e in VALIDATOR.iter_errors(body)]
    assert not errors, errors


class Dates(BaseModel):
    checkin: date
    checkout: date

    @model_validator(mode="after")
    def checkout_after_checkin(self):
        if self.checkout <= self.checkin:
            raise ValueError("checkout must be after checkin")
        return self


class Booking(BaseModel, extra="forbid"):
    firstname: str = Field(min_length=1)
    lastname: str = Field(min_length=1)
    totalprice: int = Field(ge=0)
    depositpaid: bool
    bookingdates: Dates
    additionalneeds: str | None = None


def test_booking_matches_pydantic_model(api, base_url, booking):
    model = Booking.model_validate(api.get(f"{base_url}/booking/{booking['id']}", timeout=10).json())
    assert model.bookingdates.checkout > model.bookingdates.checkin
    assert (model.bookingdates.checkout - model.bookingdates.checkin).days == 2


def test_model_catches_bad_data():
    with pytest.raises(ValidationError):
        Booking.model_validate({"firstname": "", "lastname": "B", "totalprice": -5, "depositpaid": "maybe",
                                "bookingdates": {"checkin": "2026-01-05", "checkout": "2026-01-01"}})
''', {'save': 'tests/test_schema.py'}),
                ('tip', 'pydantic can check business rules too, such as checkout after checkin, which a plain schema cannot express. Use <code>extra="forbid"</code> to fail when the API adds fields you did not expect.'),
            ],
        },
        {
            'id': 'framework', 'title': 'Framework design: a client class', 'emoji': '🏗️', 'level': 'Advanced',
            'blocks': [
                ('p', 'Keep URLs and HTTP details in one client class. Tests call methods with clear names and only contain checks. When an endpoint changes, you fix it in one place.'),
                ('code', 'py', 'api/client.py', '''
from __future__ import annotations

import logging

import requests

log = logging.getLogger("api")


class BookingClient:
    def __init__(self, base_url: str, timeout: float = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.session.hooks["response"].append(self._log)

    @staticmethod
    def _log(res: requests.Response, *args, **kwargs):
        log.info("%s %s -> %s in %d ms", res.request.method, res.url, res.status_code,
                 res.elapsed.total_seconds() * 1000)

    def _call(self, method: str, path: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, f"{self.base_url}{path}", **kwargs)

    def login(self, user: str = "admin", password: str = "password123") -> BookingClient:
        token = self._call("POST", "/auth", json={"username": user, "password": password}).json()["token"]
        self.session.cookies.set("token", token)
        return self

    def create(self, booking: dict) -> requests.Response:
        return self._call("POST", "/booking", json=booking)

    def get(self, booking_id: int) -> requests.Response:
        return self._call("GET", f"/booking/{booking_id}")

    def find(self, **filters) -> list[int]:
        return [b["bookingid"] for b in self._call("GET", "/booking", params=filters).json()]

    def patch(self, booking_id: int, **fields) -> requests.Response:
        return self._call("PATCH", f"/booking/{booking_id}", json=fields)

    def delete(self, booking_id: int) -> requests.Response:
        return self._call("DELETE", f"/booking/{booking_id}")
''', {'save': 'api/client.py'}),
                ('code', 'py', 'tests/test_framework.py', '''
import pytest

from api.client import BookingClient


@pytest.fixture(scope="module")
def client(base_url):
    return BookingClient(base_url).login()


def test_patch_through_the_client(client):
    created = client.create({
        "firstname": "Frame", "lastname": "Work", "totalprice": 120, "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-01", "checkout": "2026-11-02"},
    })
    booking_id = created.json()["bookingid"]

    assert booking_id in client.find(firstname="Frame")
    assert client.patch(booking_id, lastname="Updated").json()["lastname"] == "Updated"
    assert client.delete(booking_id).status_code == 201
    assert client.get(booking_id).status_code == 404
''', {'save': 'tests/test_framework.py'}),
                ('tip', 'Run with <code>pytest --log-cli-level=INFO</code> to see the line logged for every call by the response hook.'),
            ],
        },
        {
            'id': 'mocking', 'title': 'Mocking HTTP with responses and respx', 'emoji': '🎭', 'level': 'Advanced',
            'blocks': [
                ('p', 'When you test code that calls an API, such as your own client class, you often want to control the answers. <b>responses</b> intercepts calls made with requests. <b>respx</b> does the same for httpx. No network is used, so tests are fast and can simulate errors on demand.'),
                ('code', 'py', 'tests/test_mocking.py', '''
import httpx
import pytest
import requests
import responses
import respx

from api.client import BookingClient


@responses.activate
def test_client_handles_a_server_error():
    responses.get("https://api.test/booking/1", status=503, body="Service Unavailable")

    res = BookingClient("https://api.test").get(1)

    assert res.status_code == 503
    assert responses.calls[0].request.headers["Accept"] == "application/json"


@responses.activate
def test_client_raises_on_timeout():
    responses.get("https://api.test/booking/1", body=requests.exceptions.ConnectTimeout())

    with pytest.raises(requests.exceptions.ConnectTimeout):
        BookingClient("https://api.test").get(1)


@respx.mock
def test_httpx_call_is_mocked():
    route = respx.get("https://api.test/booking/7").mock(
        return_value=httpx.Response(200, json={"firstname": "Mock"}))

    res = httpx.get("https://api.test/booking/7")

    assert route.called
    assert res.json() == {"firstname": "Mock"}
''', {'save': 'tests/test_mocking.py'}),
                ('qa', 'Mocks test your code, not the real API. Use them for unit tests of helpers and clients, and keep separate tests that call the real service.'),
            ],
        },
        {
            'id': 'async', 'title': 'Async tests with httpx', 'emoji': '⚡', 'level': 'Advanced',
            'blocks': [
                ('p', '<b>httpx</b> has the same style as requests, plus an async client. With <code>asyncio.gather</code> you can send many calls at once. This is useful for quick concurrency checks and for testing async services.'),
                ('code', 'py', 'tests/test_async.py', '''
import asyncio
import time

import httpx
import pytest


@pytest.mark.asyncio
async def test_twenty_reads_at_once(base_url):
    async with httpx.AsyncClient(base_url=base_url, timeout=10) as client:
        start = time.perf_counter()
        responses = await asyncio.gather(*(client.get("/booking/1") for _ in range(20)))
        took = time.perf_counter() - start

    assert all(r.status_code == 200 for r in responses)
    assert len({r.text for r in responses}) == 1          # everyone saw the same data
    assert took < 10


@pytest.mark.asyncio
async def test_create_many_in_parallel(base_url):
    def booking(i):
        return {"firstname": f"Async{i}", "lastname": "Test", "totalprice": i, "depositpaid": False,
                "bookingdates": {"checkin": "2026-10-01", "checkout": "2026-10-02"}}

    async with httpx.AsyncClient(base_url=base_url, timeout=10) as client:
        results = await asyncio.gather(*(client.post("/booking", json=booking(i)) for i in range(5)))

    ids = [r.json()["bookingid"] for r in results]
    assert len(set(ids)) == 5                              # no duplicate ids under concurrency
''', {'save': 'tests/test_async.py'}),
                ('why', 'Bugs such as duplicate ids or lost updates only appear when calls overlap. A few parallel calls in a test can expose them early.'),
            ],
        },
        {
            'id': 'parallel-ci', 'title': 'Markers, parallel runs, reports and CI', 'emoji': '🚀', 'level': 'Expert',
            'blocks': [
                ('code', 'bash', 'Common commands', '''
pytest -m smoke                       # only tests marked smoke
pytest -n auto                        # parallel on every CPU core (pytest-xdist)
pytest -n 4 --dist loadfile           # 4 workers, tests from one file stay together
pytest --junitxml=reports/junit.xml   # report CI systems understand
pytest --lf                           # rerun only the last failures
'''),
                ('ul', [
                    'Session fixtures run once per <b>worker</b> with xdist, so each worker gets its own token. That is fine for most APIs.',
                    'Tests must not depend on each other or on order. The function scoped <code>booking</code> fixture makes this easy.',
                    'For an HTML report add <code>pytest-html</code>. For a rich report with every request attached, add <code>allure-pytest</code>.',
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
      - run: pytest -n auto --junitxml=reports/junit.xml
        env:
          BASE_URL: ${{ vars.BASE_URL }}
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: reports
          path: reports
'''),
            ],
        },
        {
            'id': 'resilience', 'title': 'Retries, polling and flaky networks', 'emoji': '🔁', 'level': 'Expert',
            'blocks': [
                ('p', 'Real networks drop calls now and then. Retry the safe calls at the HTTP layer so a single blip does not fail the build, and poll properly when an API finishes work in the background.'),
                ('code', 'py', 'Automatic retries on a session', '''
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

retry = Retry(
    total=3,
    backoff_factor=0.5,                       # waits 0.5 s, 1 s, 2 s
    status_forcelist=[502, 503, 504],
    allowed_methods=["GET", "PUT", "DELETE"], # never retry POST automatically
)
session.mount("https://", HTTPAdapter(max_retries=retry))
'''),
                ('code', 'py', 'Poll until ready with tenacity', '''
from tenacity import retry, retry_if_result, stop_after_delay, wait_fixed


@retry(retry=retry_if_result(lambda status: status != "DONE"),
       wait=wait_fixed(1), stop=stop_after_delay(30))
def wait_for_job(session, job_url):
    return session.get(job_url, timeout=10).json()["status"]
'''),
                ('warn', 'Retries hide real problems if overused. Log every retry, keep the count low, and never retry a 4xx, since the request itself is wrong.'),
            ],
        },
        {
            'id': 'expert', 'title': 'Expert topics: property based testing, contracts and load', 'emoji': '🧠', 'level': 'Expert',
            'blocks': [
                ('h', 'Property based testing with Schemathesis'),
                ('p', 'Schemathesis reads an OpenAPI spec and generates thousands of requests, including odd values you would not think of. It checks that the API never answers 500 and that every response matches the spec.'),
                ('code', 'bash', 'One command against an OpenAPI spec', '''
pip install schemathesis
st run https://api.example.com/openapi.json --checks all
'''),
                ('h', 'Contract tests'),
                ('p', 'With <b>pact-python</b>, the consumer team records the requests and responses it relies on. The provider replays that contract in its own pipeline, so breaking changes fail before they are deployed.'),
                ('h', 'Load testing'),
                ('p', '<b>Locust</b> describes user behaviour in plain Python classes and ramps up to thousands of users. Use it on your own environment, never on shared public APIs.'),
                ('code', 'py', 'locustfile.py', '''
from locust import HttpUser, between, task


class Guest(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def browse(self):
        self.client.get("/booking")

    @task(1)
    def view_one(self):
        self.client.get("/booking/1", name="/booking/[id]")
'''),
                ('h', 'More expert checks'),
                ('ul', [
                    '<b>Idempotency</b>: repeat a PUT and expect the same state.',
                    '<b>Pagination</b>: walk all pages and check no id repeats.',
                    '<b>Rate limits</b>: 429 with a <code>Retry-After</code> header after many fast calls.',
                    '<b>Security</b>: OWASP API Top 10 checks such as broken object level authorization, mass assignment and excessive data exposure.',
                ]),
            ],
        },
        {
            'id': 'essentials', 'title': 'Real project essentials: environments, secrets, fake data, logging and cleanup', 'emoji': '🧳', 'level': 'Intermediate',
            'blocks': [
                ('p', 'Tutorials talk to one server with one password. Real teams run the same suite against local, QA and staging, keep passwords out of Git, need fresh realistic data for every run, and want to see the exact request and response when a test fails at 2 am in CI. These five habits are what separate a demo from a suite a company trusts.'),
                ('code', 'py', 'api/settings.py', '''
import os
from dataclasses import dataclass

ENVIRONMENTS = {
    "local": "http://localhost:3001",
    "qa": "https://qa.booker.example",
    "prod": "https://restful-booker.herokuapp.com",
}


@dataclass(frozen=True)
class Settings:
    env: str
    base_url: str
    username: str
    password: str
    timeout: float


def load_settings() -> Settings:
    env = os.environ.get("TEST_ENV", "prod")
    if env not in ENVIRONMENTS:
        raise ValueError(f"TEST_ENV must be one of {sorted(ENVIRONMENTS)}, got {env!r}")
    return Settings(
        env=env,
        base_url=os.environ.get("BASE_URL", ENVIRONMENTS[env]),
        username=os.environ.get("API_USER", "admin"),
        password=os.environ.get("API_PASSWORD", "password123"),   # practice API only, real secrets come from CI
        timeout=float(os.environ.get("API_TIMEOUT", "10")),
    )
''', {'save': 'api/settings.py'}),
                ('code', 'py', 'tests/test_essentials.py', '''
import logging

import pytest
import requests
from faker import Faker

from api.settings import load_settings

log = logging.getLogger("api")
fake = Faker("en_IN")          # Indian names, cities and phone numbers
settings = load_settings()


def log_exchange(res, *args, **kwargs):
    """A requests hook: runs after every response and logs the full exchange."""
    req = res.request
    log.info("%s %s -> %s in %.0f ms", req.method, req.url, res.status_code, res.elapsed.total_seconds() * 1000)
    log.debug("request body: %s", req.body)
    log.debug("response body: %s", res.text[:500])


@pytest.fixture
def session():
    s = requests.Session()
    s.headers["Accept"] = "application/json"
    s.hooks["response"].append(log_exchange)
    yield s
    s.close()


@pytest.fixture
def cleanup(session):
    """Collects ids a test creates and deletes them afterwards, even when the test fails."""
    created = []
    yield created
    token = session.post(f"{settings.base_url}/auth",
                         json={"username": settings.username, "password": settings.password},
                         timeout=settings.timeout).json()["token"]
    for booking_id in created:
        session.delete(f"{settings.base_url}/booking/{booking_id}", cookies={"token": token}, timeout=settings.timeout)


def fake_booking():
    checkin = fake.date_between(start_date="+1d", end_date="+60d")
    return {
        "firstname": fake.first_name(),
        "lastname": fake.last_name(),
        "totalprice": fake.random_int(min=500, max=25000),
        "depositpaid": fake.boolean(),
        "bookingdates": {"checkin": checkin.isoformat(),
                         "checkout": fake.date_between(start_date=checkin, end_date="+90d").isoformat()},
        "additionalneeds": fake.random_element(["Breakfast", "Airport pickup", "Late checkout"]),
    }


def test_realistic_booking_round_trip(session, cleanup, caplog):
    caplog.set_level(logging.INFO, logger="api")
    data = fake_booking()

    res = session.post(f"{settings.base_url}/booking", json=data, timeout=settings.timeout)
    assert res.status_code == 200, res.text
    booking_id = res.json()["bookingid"]
    cleanup.append(booking_id)

    stored = session.get(f"{settings.base_url}/booking/{booking_id}", timeout=settings.timeout).json()
    assert stored == data
    assert any("POST" in m and "-> 200" in m for m in caplog.messages)
''', {'save': 'tests/test_essentials.py'}),
                ('code', 'bash', 'Running it in different places', '''
TEST_ENV=local pytest tests/test_essentials.py -o log_cli=true --log-cli-level=INFO
TEST_ENV=qa API_PASSWORD="$QA_PASSWORD" pytest            # the password comes from your shell or CI
pytest --log-level=DEBUG                                   # full bodies in the failure report
'''),
                ('table', ['Habit', 'Why', 'Here'], [
                    ['Config from the environment', 'One suite, many servers, no code changes', '<code>TEST_ENV</code> and <code>BASE_URL</code>'],
                    ['Secrets never in Git', 'Leaked passwords are a security incident', 'Defaults only for the public practice API'],
                    ['Fake but realistic data', 'Unique names avoid clashes between parallel runs and catch encoding bugs', '<code>Faker("en_IN")</code>'],
                    ['Log every exchange', 'A failing CI test explains itself', 'a <code>requests</code> response hook'],
                    ['Clean up what you create', 'Shared QA databases stay usable', 'a fixture with code after <code>yield</code>'],
                ]),
                ('tip', 'pytest shows captured log lines only for failing tests, so passing runs stay quiet and failing runs show the full request and response. That is exactly what you want in CI.'),
            ],
        },
        {
            'id': 'latest', 'title': 'What is new in pytest 9 and Python, and how it helps at work', 'emoji': '🆕', 'level': 'Expert',
            'blocks': [
                ('table', ['Feature', 'Since', 'How it helps an API tester'], [
                    ['Built in <code>subtests</code> fixture', 'pytest 9.0', 'Check many fields of one response and see every failure, not only the first'],
                    ['Native TOML config in <code>[tool.pytest]</code>', 'pytest 9.0', 'Real lists, numbers and booleans in <code>pyproject.toml</code> instead of strings'],
                    ['<code>strict = true</code>', 'pytest 9.0', 'One switch for strict markers, strict config and strict xfail, so typos in marker names fail the run'],
                    ['Python 3.14', 'October 2025', 'Template strings (t-strings, PEP 750) and the officially supported free threaded build for heavier parallel scripts'],
                    ['requests 2.34 and httpx 0.28', '2025 and 2026', 'Current TLS defaults and security fixes. Keep them pinned and upgrade on purpose'],
                ]),
                ('code', 'toml', 'pyproject.toml (pytest 9 native TOML mode)', '''
[tool.pytest]
testpaths = ["tests"]
pythonpath = ["."]
addopts = ["-ra"]
strict = true
markers = [
    "smoke: quick checks that run on every commit",
]
'''),
                ('code', 'py', 'tests/test_subtests.py', '''
import requests

from api.settings import load_settings

settings = load_settings()

EXPECTED_TYPES = {
    "firstname": str,
    "lastname": str,
    "totalprice": int,
    "depositpaid": bool,
    "bookingdates": dict,
}


def test_every_field_has_the_right_type(subtests):
    body = requests.get(f"{settings.base_url}/booking/1", timeout=settings.timeout).json()

    for field, expected in EXPECTED_TYPES.items():
        with subtests.test(msg=field):
            assert field in body, f"{field} is missing"
            assert isinstance(body[field], expected), f"{field} is {type(body[field]).__name__}"
''', {'save': 'tests/test_subtests.py'}),
                ('ul', [
                    'Each <code>subtests.test()</code> block is reported on its own. If two fields are wrong you see both in one run, which saves a fix, rerun, fix, rerun cycle.',
                    'The <code>[tool.pytest]</code> table uses real TOML types. The older <code>[tool.pytest.ini_options]</code> table still works, so you can move over gradually.',
                    'Before upgrading at work, run the suite with <code>-W error::DeprecationWarning</code> on the old version. Anything it flags is what the new version will remove.',
                ]),
            ],
        },
        {
            'id': 'scenario', 'title': 'Real world scenario: a hotel front desk day', 'emoji': '🏨', 'level': 'Scenario',
            'blocks': [
                ('p', 'A receptionist books a room for a guest, adds breakfast later, and then the guest cancels. Someone without a login also tries to cancel the booking. The test proves each step, using fixtures for login.'),
                ('flow', [
                    ('Health check', '<code>GET /ping</code> answers 201.'),
                    ('Log in', 'The <code>token</code> fixture calls <code>POST /auth</code> once for the run.'),
                    ('Book', '<code>POST /booking</code> with a unique guest name.'),
                    ('Search', '<code>GET /booking?firstname=...</code> includes the new id.'),
                    ('Add breakfast', '<code>PATCH</code> with the token changes one field only.'),
                    ('Unauthorised cancel', '<code>DELETE</code> without a token gives 403 and nothing changes.'),
                    ('Cancel', '<code>DELETE</code> with the token gives 201.'),
                    ('Gone', '<code>GET</code> gives 404.'),
                ]),
                ('code', 'py', 'tests/test_journey.py', '''
import time


def test_front_desk_day(api, base_url, token):
    assert api.get(f"{base_url}/ping", timeout=10).status_code == 201

    guest = f"Guest{time.time_ns()}"
    booking = {
        "firstname": guest,
        "lastname": "Panda",
        "totalprice": 250,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-01", "checkout": "2026-11-04"},
    }
    booking_id = api.post(f"{base_url}/booking", json=booking, timeout=10).json()["bookingid"]

    found = api.get(f"{base_url}/booking", params={"firstname": guest}, timeout=10).json()
    assert {"bookingid": booking_id} in found

    res = api.patch(f"{base_url}/booking/{booking_id}", json={"additionalneeds": "Breakfast"},
                    cookies={"token": token}, timeout=10)
    assert res.json() == {**booking, "additionalneeds": "Breakfast"}

    assert api.delete(f"{base_url}/booking/{booking_id}", timeout=10).status_code == 403
    assert api.get(f"{base_url}/booking/{booking_id}", timeout=10).status_code == 200

    assert api.delete(f"{base_url}/booking/{booking_id}", cookies={"token": token}, timeout=10).status_code == 201
    assert api.get(f"{base_url}/booking/{booking_id}", timeout=10).status_code == 404
''', {'save': 'tests/test_journey.py'}),
            ],
        },
    ],
    'quiz': [
        {'lv': 'e', 'q': 'Which requests argument sends a Python dict as a JSON body?', 'o': ['<code>data=</code>', '<code>json=</code>', '<code>params=</code>', '<code>body=</code>'], 'a': 1, 'hint': 'It also sets the Content-Type header.', 'why': '<code>json=</code> serializes the dict and sets <code>Content-Type: application/json</code>. <code>data=</code> sends form fields.'},
        {'lv': 'e', 'q': 'What is the default timeout in requests?', 'o': ['10 seconds', '30 seconds', 'None, it can wait forever', '1 minute'], 'a': 2, 'hint': 'That is why every example passes one.', 'why': 'requests waits indefinitely unless you pass <code>timeout=</code>. A hung server would hang your whole suite.'},
        {'lv': 'm', 'q': 'What runs the code after <code>yield</code> in a fixture?', 'o': ['Nothing, it is ignored', 'pytest, after the test finishes, even if it failed', 'Only when the test passes', 'Before the test'], 'a': 1, 'hint': 'Think cleanup.', 'why': 'The part after <code>yield</code> is teardown. pytest runs it after the test, pass or fail, so cleanup always happens.'},
        {'lv': 'm', 'q': 'Which fixture scope suits an auth token shared by the whole run?', 'o': ['<code>function</code>', '<code>class</code>', '<code>module</code>', '<code>session</code>'], 'a': 3, 'hint': 'Created once per run.', 'why': 'A <code>session</code> fixture runs once, so you log in once instead of before every test.'},
        {'lv': 'h', 'q': '<code>Retry(allowed_methods=["GET", "PUT", "DELETE"])</code> leaves out POST. Why?', 'o': ['POST is slow', 'POST is not idempotent, so a retry may create a duplicate', 'urllib3 cannot retry POST', 'POST never fails'], 'a': 1, 'hint': 'What happens if the first POST did succeed?', 'why': 'If the first POST reached the server but the answer was lost, a retry creates a second booking.'},
        {'lv': 'h', 'q': 'Which tool mocks calls made with httpx?', 'o': ['responses', 'respx', 'requests-mock', 'unittest only'], 'a': 1, 'hint': 'The name sounds like responses plus x.', 'why': '<code>respx</code> intercepts httpx. <code>responses</code> intercepts requests.'},
        {'lv': 'x', 'q': 'With <code>pytest -n 4</code>, how often does a <code>session</code> scoped fixture run?', 'o': ['Once in total', 'Once per worker, so up to 4 times', 'Once per test', 'Never'], 'a': 1, 'hint': 'Each xdist worker is a separate process.', 'why': 'xdist starts separate processes, and each one has its own session. Shared state across workers needs a file lock or an external store.'},
        {'lv': 'x', 'q': 'What does Schemathesis mainly check?', 'o': ['UI layout', 'That generated requests never cause 500 errors and responses match the OpenAPI spec', 'Database indexes', 'Code coverage'], 'a': 1, 'hint': 'It is property based.', 'why': 'It generates many inputs from the spec and checks properties that must always hold, such as no server errors and schema conformance.'},
    ],
}
