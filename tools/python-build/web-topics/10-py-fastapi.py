# Web and APIs 5.2: FastAPI. Checked against the FastAPI 0.162 documentation (tutorial: first steps, path and query
# parameters, request body, query and path validations, response model, handling errors, dependencies including
# yield, security with OAuth2 and Bearer tokens, background tasks, testing, async and concurrency, lifespan events,
# deployment) and Pydantic 2.14 (models, fields, validators, JSON Schema), with real runs of FastAPI 0.162.0,
# Starlette 1.10.0, Pydantic 2.14.3 and httpx 0.28.1 on Python 3.14. The FastAPI programs use the test client,
# which needs threads, so they are shown with local(). The Pydantic program runs in the page.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, lc, leet, files, grow, leet_items

chapter('py-fastapi')
K = Kit()

K.code('pydantic_models', r'''
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator


class Address(BaseModel):
    city: str
    zip_code: str = Field(pattern=r"^[0-9]{6}$")          # exactly 6 digits


class Order(BaseModel):
    customer: str = Field(min_length=2, max_length=50)
    quantity: int = Field(gt=0, le=10)                      # 1 to 10
    size: Literal["S", "M", "L"] = "M"                      # only these values, M by default
    delivery: date
    address: Address                                        # a model inside a model
    tags: list[str] = []

    @field_validator("customer")
    @classmethod
    def tidy_name(cls, value):
        return value.strip().title()

    @model_validator(mode="after")
    def not_in_the_past(self):
        if self.delivery < date(2026, 11, 8):
            raise ValueError("delivery must not be in the past")
        return self


# 1. Good data: strings are converted to the declared types
order = Order(customer="  ann lee ", quantity="3", delivery="2026-12-01",
              address={"city": "Pune", "zip_code": "411001"})
print(order)
print("quantity is", type(order.quantity).__name__, "| delivery is", type(order.delivery).__name__)
print(order.model_dump_json())

# 2. Bad data: every problem is listed with where it is and why
try:
    Order(customer="A", quantity=0, size="XL", delivery="2026-13-01", address={"city": "Pune", "zip_code": "41"})
except ValidationError as error:
    print(error.error_count(), "errors:")
    for problem in error.errors():
        print("  ", ".".join(str(part) for part in problem["loc"]), "->", problem["msg"])

# 3. A rule across fields, from the model validator
try:
    Order(customer="Bob", quantity=1, delivery="2020-01-01", address={"city": "Goa", "zip_code": "403001"})
except ValidationError as error:
    print("model rule:", error.errors()[0]["msg"])

# 4. The JSON Schema that FastAPI puts into the API docs
schema = Order.model_json_schema()
print("required:", schema["required"])
print("quantity schema:", schema["properties"]["quantity"])''', long=True)
K.code('first_api', r'''
import warnings

warnings.filterwarnings("ignore", message="Using `httpx` with")   # a notice from Starlette 1.10 about its test client

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI(title="Book shop API", version="1.0")


class BookIn(BaseModel):                                   # what a client sends
    title: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=0, le=2026)
    price: float = Field(gt=0)


class BookOut(BookIn):                                     # what the API sends back
    id: int


BOOKS: dict[int, BookOut] = {1: BookOut(id=1, title="Dune", year=1965, price=9.99)}


@app.get("/books", response_model=list[BookOut])
def list_books(min_year: int = 0, limit: int = Query(10, ge=1, le=100)):     # query parameters with types
    found = [book for book in BOOKS.values() if book.year >= min_year]
    return found[:limit]


@app.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: int):                                # a path parameter, checked as int
    if book_id not in BOOKS:
        raise HTTPException(status_code=404, detail="Book not found")
    return BOOKS[book_id]


@app.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def add_book(book: BookIn):                                # the JSON body, checked by Pydantic
    new = BookOut(id=max(BOOKS) + 1, **book.model_dump())
    BOOKS[new.id] = new
    return new


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    if BOOKS.pop(book_id, None) is None:
        raise HTTPException(status_code=404, detail="Book not found")


client = TestClient(app)
for method, url, body in [
    ("get", "/books", None),
    ("post", "/books", {"title": "Emma", "year": 1815, "price": 5}),
    ("get", "/books?min_year=1900&limit=5", None),
    ("get", "/books/2", None),
    ("get", "/books/abc", None),
    ("post", "/books", {"title": "", "year": 3000}),
    ("get", "/books?limit=500", None),
    ("delete", "/books/2", None),
    ("delete", "/books/2", None),
]:
    response = client.request(method.upper(), url, json=body)
    data = response.json() if response.content else None
    if response.status_code == 422:                        # show only where and why for validation errors
        data = [(".".join(map(str, e["loc"])), e["msg"]) for e in data["detail"]]
    print(f"{method.upper():6} {url:28} {response.status_code} {data}")

schema = client.get("/openapi.json").json()               # the docs FastAPI wrote by itself
print("OpenAPI paths:", {path: sorted(ops) for path, ops in schema["paths"].items()})
print("Swagger UI at /docs:", client.get("/docs").status_code, "| ReDoc at /redoc:", client.get("/redoc").status_code)''', long=True)
K.code('dependencies', r'''
import warnings

warnings.filterwarnings("ignore", message="Using `httpx` with")   # a notice from Starlette 1.10 about its test client

import sqlite3
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()
TOKENS = {"secret-ann": "ann", "secret-bob": "bob"}


# ---------- Dependencies: small functions FastAPI calls for you before the endpoint ----------
def get_db():
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.execute("CREATE TABLE note (id INTEGER PRIMARY KEY, owner TEXT, text TEXT)")
    db.executemany("INSERT INTO note (owner, text) VALUES (?, ?)",
                   [("ann", "buy milk"), ("ann", "call mum"), ("bob", "fix bike"), ("ann", "read Dune")])
    print("   [get_db] connection opened")
    try:
        yield db                                           # the endpoint runs here
    finally:
        db.close()                                         # runs after the answer, even after an error
        print("   [get_db] connection closed")


def current_user(authorization: Annotated[str | None, Header()] = None):
    token = (authorization or "").removeprefix("Bearer ")
    if token not in TOKENS:
        raise HTTPException(status_code=401, detail="Not logged in", headers={"WWW-Authenticate": "Bearer"})
    return TOKENS[token]


def paging(skip: int = 0, limit: int = 2):                # shared query parameters
    return {"skip": skip, "limit": min(limit, 50)}


DB = Annotated[sqlite3.Connection, Depends(get_db)]
User = Annotated[str, Depends(current_user)]
Page = Annotated[dict, Depends(paging)]


@app.get("/notes")
def my_notes(db: DB, user: User, page: Page):
    rows = db.execute("SELECT id, text FROM note WHERE owner = ? ORDER BY id LIMIT ? OFFSET ?",
                      (user, page["limit"], page["skip"])).fetchall()
    return {"user": user, "notes": [{"id": i, "text": t} for i, t in rows]}


client = TestClient(app)
response = client.get("/notes")
print("no token:", response.status_code, response.json())          # get_db still ran: it comes first in my_notes
headers = {"Authorization": "Bearer secret-ann"}
print("ann page 1:", client.get("/notes", headers=headers).json())
print("ann page 2:", client.get("/notes?skip=2", headers=headers).json())

# ---------- In tests, swap a dependency for a fake one ----------
app.dependency_overrides[current_user] = lambda: "bob"
print("override, no token needed:", client.get("/notes").json())
app.dependency_overrides.clear()''', long=True)
K.code('async_background', r'''
import asyncio
import time
from contextlib import asynccontextmanager

import httpx
from fastapi import BackgroundTasks, FastAPI

EVENTS = []


@asynccontextmanager
async def lifespan(app):                                   # runs once at start up and once at shut down
    EVENTS.append("start: open the database pool")
    yield
    EVENTS.append("stop: close the pool")


app = FastAPI(lifespan=lifespan)


@app.get("/slow-async")
async def slow_async():
    await asyncio.sleep(0.2)                               # waiting on the network or a database, the right way
    return {"done": True}


@app.get("/slow-sync")
def slow_sync():
    time.sleep(0.2)                                        # a blocking call: FastAPI runs plain def endpoints in a thread pool
    return {"done": True}


@app.get("/blocking-async")
async def blocking_async():
    time.sleep(0.2)                                        # THE MISTAKE: a blocking call inside async def stops the event loop
    return {"done": True}


def send_email(address):
    EVENTS.append(f"email sent to {address}")


@app.post("/signup")
async def signup(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_email, email)                      # runs after the answer has been sent
    EVENTS.append("answer sent")
    return {"ok": True}


async def timed(client, path, n):
    start = time.perf_counter()
    await asyncio.gather(*[client.get(path) for _ in range(n)])
    return time.perf_counter() - start


async def main():
    transport = httpx.ASGITransport(app=app)               # call the app directly, no network
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            for path in ["/slow-async", "/slow-sync", "/blocking-async"]:
                seconds = await timed(client, path, 10)
                print(f"10 requests at once to {path:15}: {seconds:.1f} s (one alone takes 0.2 s)")
            await client.post("/signup", params={"email": "ann@example.com"})
    print(EVENTS)


asyncio.run(main())''', long=True)
K.code('pytest_api', r'''
import os
import subprocess
import sys
import tempfile

# Two real files, main.py (the app) and test_main.py (the tests), then a real pytest run
APP = """
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


def get_store():
    return {}                                   # in a real app: a database session


@app.post("/items", status_code=201)
def add_item(item: Item, store: dict = Depends(get_store)):
    if item.name in store:
        raise HTTPException(409, "Item exists")
    store[item.name] = item.price
    return {"name": item.name, "price": item.price, "count": len(store)}
"""

TESTS = """
import pytest
import warnings
warnings.filterwarnings("ignore", message="Using `httpx` with")
from fastapi.testclient import TestClient

from main import app, get_store


@pytest.fixture
def client():
    store = {}
    app.dependency_overrides[get_store] = lambda: store     # every test gets its own empty store
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_add_item(client):
    r = client.post("/items", json={"name": "tea", "price": 3})
    assert r.status_code == 201
    assert r.json() == {"name": "tea", "price": 3.0, "count": 1}


def test_same_item_twice_is_409(client):
    client.post("/items", json={"name": "tea", "price": 3})
    r = client.post("/items", json={"name": "tea", "price": 4})
    assert r.status_code == 409
    assert r.json()["detail"] == "Item exists"


@pytest.mark.parametrize("body", [{}, {"name": "tea"}, {"name": "tea", "price": "free"}])
def test_bad_bodies_are_422(client, body):
    assert client.post("/items", json=body).status_code == 422
"""

folder = tempfile.mkdtemp()
for name, text in [("main.py", APP), ("test_main.py", TESTS)]:
    with open(os.path.join(folder, name), "w") as f:
        f.write(text)
result = subprocess.run([sys.executable, "-m", "pytest", "-v", "-p", "no:cacheprovider"], cwd=folder,
                        capture_output=True, text=True)
for line in result.stdout.splitlines():
    if "::" in line or "passed" in line or "failed" in line:
        print(line.split(" [")[0].replace(folder + os.sep, "").rstrip())      # the test lines and the summary''', long=True)

PLAY = '''

def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results
'''

WHY = 'FastAPI&#39;s test client runs the app in a helper thread, and threads do not work in the browser&#39;s Python. Install everything with <code>pip install fastapi httpx</code>.'

K.lesson('idea', 'What FastAPI is and why type hints matter', f'''
{src('FastAPI 0.162 documentation (tutorial, dependencies, security, background tasks, testing, async, lifespan, deployment) and Pydantic 2.14 documentation (models, fields, validators, JSON Schema).')}
{wwh('<b>FastAPI</b> is a Python framework for building APIs. You write normal functions with <b>type hints</b>, such as book_id: int or book: BookIn, and FastAPI uses them to read the request, check it with <b>Pydantic</b>, write the JSON answer and produce live API docs.',
     'In most frameworks the input rules live in one place (a serializer or form), the function signature in another and the docs in a third. They drift apart, and every endpoint repeats the same checking code. Many APIs also spend most of their time waiting for databases and other services.',
     'The type hints are the single source: they check the input (422 when wrong), convert text to numbers and dates, filter the output with response_model and feed the OpenAPI docs at /docs. Depends gives shared parts such as the database and the user. async def endpoints let one process serve many waiting requests at once.')}
{viz('pyfastapi')}
{versus('FastAPI, Flask and Django REST framework', ['', 'FastAPI', 'Flask', 'Django REST framework'], [
    ['Input checks', 'Pydantic from type hints', 'By hand or with an extension', 'Serializers'],
    ['Docs', 'OpenAPI, Swagger UI and ReDoc built in', 'Extensions', 'Browsable API, OpenAPI with an add on'],
    ['Async', 'Built on ASGI, async def everywhere', 'Mainly sync (WSGI)', 'Mainly sync, async views possible'],
    ['Database and admin', 'Your choice (SQLAlchemy, SQLModel)', 'Your choice', 'Django ORM and admin'],
    ['Good for', 'New API services, many waiting calls', 'Small apps and services', 'APIs next to a Django site']],
    'Choose FastAPI for a new JSON API, especially one that calls other services. Choose DRF when the data already lives in Django.')}
''', kw=['FastAPI', 'type hints', 'Pydantic', 'ASGI', 'OpenAPI', 'Swagger UI', 'async', 'Flask', 'Django REST framework'])

K.lesson('pydantic', 'Pydantic: data that checks itself', f'''
{run('pydantic_models')}
{table(['Tool', 'Example', 'Effect'], [
    ['Type hint', 'quantity: int', '"3" becomes 3, "abc" is an error'],
    ['Field limits', 'Field(gt=0, le=10), Field(min_length=2), Field(pattern=...)', 'Ranges, lengths, patterns'],
    ['Literal', 'size: Literal["S", "M", "L"] = "M"', 'Only these values, with a default'],
    ['Nested model', 'address: Address', 'A dict is checked as an Address'],
    ['field_validator', '@field_validator("customer")', 'Your own rule or clean up for one field'],
    ['model_validator', '@model_validator(mode="after")', 'A rule across several fields'],
    ['Output', 'model_dump(), model_dump_json()', 'A dict or JSON text'],
    ['Schema', 'model_json_schema()', 'The JSON Schema that FastAPI puts in the docs']])}
{note('Pydantic converts when it is safe: "3" becomes 3, but "3.5" for an int is an error, and so is the 13th month. Every problem is listed with its location, such as address.zip_code, which is exactly what FastAPI sends back in a 422 answer.', 'tip')}
''', kw=['Pydantic', 'BaseModel', 'Field', 'Literal', 'field_validator', 'model_validator', 'ValidationError', 'model_dump', 'JSON Schema'])

K.lesson('first', 'Your first API: parameters, bodies and errors', f'''
{local('first_api', WHY)}
{table(['Where the value comes from', 'How you write it', 'Example'], [
    ['Path', 'A name in &#123;&#125; in the route and a parameter', '@app.get("/books/&#123;book_id&#125;") def get_book(book_id: int)'],
    ['Query string', 'A simple parameter that is not in the path', 'min_year: int = 0, limit: int = Query(10, le=100)'],
    ['JSON body', 'A parameter with a Pydantic model type', 'def add_book(book: BookIn)'],
    ['Header or cookie', 'Header() or Cookie()', 'authorization: Annotated[str, Header()]'],
    ['Answer shape', 'response_model and status_code', '@app.post(..., response_model=BookOut, status_code=201)'],
    ['Errors', 'raise HTTPException', 'HTTPException(404, "Book not found")']])}
{steps('What the example shows', [
    'book_id: int made /books/abc a 422 with the location path.book_id, before the function ran.',
    'The body model BookIn listed three problems at once: an empty title, a year after 2026 and a missing price.',
    'limit: int = Query(10, ge=1, le=100) refused limit=500.',
    'HTTPException(404) gave &#123;"detail": "Book not found"&#125;, and status_code=204 gave an empty answer to DELETE.',
    '/openapi.json, /docs and /redoc existed without one extra line of code.'])}
{note('Run the real server with <code>fastapi dev main.py</code> while you develop (it reloads on every save) and <code>fastapi run main.py</code> or <code>uvicorn main:app --workers 4</code> in production. Then open http://127.0.0.1:8000/docs.', 'exam')}
''', kw=['path parameters', 'query parameters', 'request body', 'response_model', 'status_code', 'HTTPException', '422', 'Query', 'OpenAPI', 'uvicorn'])

K.lesson('depends', 'Dependencies', f'''
{local('dependencies', WHY)}
{table(['Use of Depends', 'Example'], [
    ['A database session per request, closed after', 'def get_db(): db = ... yield db ... close'],
    ['The current user from a token', 'def current_user(authorization: str = Header()) ...'],
    ['Shared query parameters', 'def paging(skip: int = 0, limit: int = 20)'],
    ['A permission check', 'def admin_only(user = Depends(current_user)): if not user.is_admin: raise HTTPException(403)'],
    ['Settings loaded once', 'def get_settings(): return Settings() with lru_cache'],
    ['Fakes in tests', 'app.dependency_overrides[get_db] = fake_db']])}
{steps('What the example shows', [
    'my_notes only names what it needs: db, user and page. FastAPI found and called the three dependency functions.',
    'get_db uses yield: the code after yield ran after every answer, even the 401.',
    'get_db ran before the token check, because it is the first parameter. Put cheap checks first when the order matters.',
    'Annotated[str, Depends(current_user)] gives a short name (User) that many endpoints can reuse.',
    'dependency_overrides swapped the login for a fake user without touching the endpoint.'])}
{note('For real logins FastAPI has OAuth2PasswordBearer, which reads "Authorization: Bearer ..." and also adds an Authorize button to /docs. The token is usually a JWT signed with a secret key (chapter 6.1).', 'tip')}
''', kw=['Depends', 'dependency injection', 'yield', 'Annotated', 'Header', 'dependency_overrides', 'OAuth2PasswordBearer', 'Bearer token'])

K.lesson('async', 'async def, background tasks and start up', f'''
{local('async_background', 'It uses asyncio.run and a thread pool, which do not work in the browser&#39;s Python. Install everything with <code>pip install fastapi httpx</code>.')}
{versus('Three ways to write a slow endpoint', ['', 'async def with await', 'def (plain)', 'async def with a blocking call'], [
    ['Example', 'await asyncio.sleep(0.2), await client.get(...)', 'time.sleep(0.2), requests.get(...)', 'time.sleep(0.2) inside async def'],
    ['Runs on', 'The event loop', 'A thread pool', 'The event loop, which it blocks'],
    ['10 requests at once', '0.2 s', '0.2 s', '2.0 s'],
    ['Verdict', 'Best with async libraries', 'Fine with normal libraries', 'Never do this']],
    'Write async def only when everything slow inside it uses await. When you use a normal library such as requests or a sync database driver, write a plain def.')}
{table(['Tool', 'Use it for'], [
    ['BackgroundTasks', 'Small work after the answer, such as an email'],
    ['A task queue (Celery, RQ, arq)', 'Heavy or important work that must survive a restart'],
    ['lifespan', 'Open pools and load models once at start up, close them at shut down'],
    ['httpx.AsyncClient with ASGITransport', 'Calling the app directly from async tests'],
    ['WebSocket routes (@app.websocket)', 'Two way messages such as chat or live prices']])}
''', kw=['async', 'await', 'event loop', 'thread pool', 'blocking call', 'BackgroundTasks', 'lifespan', 'ASGITransport', 'WebSocket', 'Celery'])

K.lesson('testing', 'Testing a FastAPI app with pytest', f'''
{local('pytest_api', 'It writes two files and runs the real pytest. Install everything with <code>pip install fastapi httpx pytest</code>.')}
{steps('The pattern', [
    'Keep the app in main.py and the tests in test_main.py.',
    'A fixture makes TestClient(app) and swaps the real store or database with dependency_overrides, so each test starts empty.',
    'Each test sends a request and checks the status code and the JSON with plain assert.',
    'pytest.mark.parametrize runs one test with many bodies, here three bad ones that must all give 422.',
    'Clear dependency_overrides after the test so it never leaks into the next one.'])}
{scene('a team that ships an API every day', '<p>A team runs a price API. Every pull request runs pytest in CI: about 300 tests with TestClient finish in a few seconds because no server or network is involved. The OpenAPI JSON is saved as a CI artifact, and the mobile team generates its client code from it, so a renamed field breaks the build at once instead of the app in production.</p>')}
''', kw=['pytest', 'TestClient', 'fixture', 'dependency_overrides', 'parametrize', 'CI'])

K.lesson('maths', 'The maths: concurrency, workers and timeouts', f'''
{fxs(fx('Time with await', 'total &asymp; the longest single wait', '10 requests that each wait 0.2 s: about 0.2 s.', key=True),
     fx('Time with a blocked loop', 'total &asymp; n &times; wait', '10 &times; 0.2 = 2.0 s.', key=True),
     fx('Requests one process can hold (Little&#39;s law)', 'in flight = rate &times; time per request', '500 requests a second at 0.2 s each: 100 in flight at once.', key=True),
     fx('Thread pool limit', 'requests per second &le; threads / time per request', '40 threads at 0.2 s: at most 200 plain def requests a second per process.'),
     fx('Workers', 'workers &asymp; 2 &times; CPU cores + 1 (a common start for sync servers)', '4 cores: 9 workers. Async servers often use one worker per core.'),
     fx('Timeout budget', 'total &le; sum of the calls in a row', 'Three calls of 0.3 s in a row: 0.9 s. In parallel with gather: about 0.3 s.'))}
{steps('Worked example: one async worker or many threads?', [
    'An endpoint calls a slow partner API that answers in 0.2 s, and the traffic is 500 requests a second.',
    'By Little&#39;s law 500 &times; 0.2 = 100 requests wait at the same time.',
    'A plain def endpoint has 40 threads per process, so one process manages at most 40 / 0.2 = 200 requests a second, and 3 processes are needed.',
    'An async def endpoint with httpx.AsyncClient keeps all 100 waiting requests on one event loop, so one process is enough, if the CPU work per request is small.',
    eq('waiting is cheap with await, and CPU work still needs more processes')])}
''', kw=["Little's law", 'concurrency', 'event loop', 'thread pool', 'workers', 'timeouts', 'asyncio.gather'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Write endpoints with path and query parameters, Pydantic body models, response_model and HTTPException.</p>',
    '<p>Share code with Depends, close resources with yield, test with TestClient and dependency_overrides.</p>',
    '<p>Use async def correctly, background tasks, lifespan, Bearer token logins and a real database with SQLAlchemy.</p>',
    '<p>Design versioned APIs from the OpenAPI schema, measure the event loop under load, and deploy with several workers behind a proxy.</p>')}
{grow('Typed endpoints.', 'Shared, testable parts.', 'Fast under real load.')}
{deep('ASGI, Starlette and Uvicorn', '<p>FastAPI is built on <b>Starlette</b>, a small ASGI toolkit that does the routing, requests, responses and WebSockets. <b>ASGI</b> is the async successor of WSGI: the server calls an async function with the request and awaits messages. <b>Uvicorn</b> is the ASGI server that speaks HTTP. FastAPI adds the type hint magic, Pydantic, dependencies and the docs on top.</p>')}
''', kw=['beginner', 'expert', 'Starlette', 'ASGI', 'Uvicorn', 'SQLAlchemy', 'deployment'])

lc(1122, 'Relative Sort Array', 'relative-sort-array', 'e', 'Sort with a key: (position in the order, value)', 'Like an API that lists fields in a fixed order and the rest A to Z after them. A dict gives each wanted value its position, and the sort key puts the others at the end.', r'''
def relative_sort_array(arr1, arr2):
    rank = {value: i for i, value in enumerate(arr2)}
    return sorted(arr1, key=lambda value: (rank.get(value, len(arr2)), value))
''', [('relative_sort_array([2, 3, 1, 3, 2, 4, 6, 7, 9, 2, 19], [2, 1, 4, 3, 9, 6])', [2, 2, 2, 1, 4, 3, 3, 9, 6, 7, 19]), ('relative_sort_array([28, 6, 22, 8, 44, 17], [22, 28, 8, 6])', [22, 28, 8, 6, 17, 44])])
lc(1200, 'Minimum Absolute Difference', 'minimum-absolute-difference', 'e', 'Sort, then only neighbours matter', 'After sorting, the closest pair is always next to each other, so one pass finds the smallest gap and the pairs that have it.', r'''
def minimum_abs_difference(arr):
    arr = sorted(arr)
    best = min(b - a for a, b in zip(arr, arr[1:]))
    return [[a, b] for a, b in zip(arr, arr[1:]) if b - a == best]
''', [('minimum_abs_difference([4, 2, 1, 3])', [[1, 2], [2, 3], [3, 4]]), ('minimum_abs_difference([1, 3, 6, 10, 15])', [[1, 3]]), ('minimum_abs_difference([3, 8, -10, 23, 19, -4, -14, 27])', [[-14, -10], [19, 23], [23, 27]])])
lc(1287, 'Element Appearing More Than 25% In Sorted Array', 'element-appearing-more-than-25-in-sorted-array', 'e', 'Compare with the item a quarter further on', 'In a sorted list a value that fills more than a quarter must still be there a quarter of the length later. One loop, no counting.', r'''
def find_special_integer(arr):
    step = len(arr) // 4
    for i in range(len(arr) - step):
        if arr[i] == arr[i + step]:
            return arr[i]
    return arr[0]
''', [('find_special_integer([1, 2, 2, 6, 6, 6, 6, 7, 10])', 6), ('find_special_integer([1, 1])', 1)])
lc(1013, 'Partition Array Into Three Parts With Equal Sum', 'partition-array-into-three-parts-with-equal-sum', 'e', 'Walk once and count parts that reach a third', 'The total must split into three equal parts. Add numbers from the left and count each time the running sum reaches one third, then start again.', r'''
def can_three_parts_equal_sum(arr):
    total = sum(arr)
    if total % 3 != 0:
        return False
    target = total // 3
    parts = 0
    running = 0
    for value in arr:
        running += value
        if running == target:
            parts += 1
            running = 0
    return parts >= 3
''', [('can_three_parts_equal_sum([0, 2, 1, -6, 6, -7, 9, 1, 2, 0, 1])', True), ('can_three_parts_equal_sum([0, 2, 1, -6, 6, 7, 9, -1, 2, 0, 1])', False), ('can_three_parts_equal_sum([3, 3, 6, 5, -2, 2, 5, 1, -9, 4])', True)])
lc(1237, 'Find Positive Integer Solution for a Given Equation', 'find-positive-integer-solution-for-a-given-equation', 'm', 'Two pointers on a function you can only call', 'You can only call the hidden function f(x, y), like a remote API that you want to call as few times as possible. f grows with x and with y, so start at x = 1 and y = 1000 and move one of them each call.', r'''
class CustomFunction:
    """Stands in for LeetCode's hidden function. Each id is one increasing formula."""
    FORMULAS = {1: lambda x, y: x + y, 2: lambda x, y: x * y}

    def __init__(self, function_id):
        self.f = self.FORMULAS[function_id]
        self.calls = 0

    def f_call(self, x, y):
        self.calls += 1
        return self.f(x, y)


def find_solution(custom, z):
    result = []
    x, y = 1, 1000
    while x <= 1000 and y >= 1:
        value = custom.f_call(x, y)
        if value == z:
            result.append([x, y])
            x += 1
            y -= 1
        elif value < z:
            x += 1
        else:
            y -= 1
    return result
''', [('find_solution(CustomFunction(1), 5)', [[1, 4], [2, 3], [3, 2], [4, 1]]), ('find_solution(CustomFunction(2), 5)', [[1, 5], [5, 1]]), ('(lambda c: [len(find_solution(c, 5)) > 0, c.calls <= 2000])(CustomFunction(1))', [True, True])])
lc(2069, 'Walking Robot Simulation II', 'walking-robot-simulation-ii', 'm', 'Moves wrap around the border, so use the remainder', 'The robot only walks around the edge of the grid. One full lap is a fixed number of steps, so a huge step count shrinks to steps % lap, like a cursor that wraps around.', r'''
class Robot:
    MOVES = {"East": (1, 0, "North"), "North": (0, 1, "West"), "West": (-1, 0, "South"), "South": (0, -1, "East")}

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.facing = "East"
        self.lap = 2 * (width + height) - 4

    def step(self, num):
        num %= self.lap
        if num == 0:
            num = self.lap                  # a full lap ends facing a new way at the start corner
        while num > 0:
            dx, dy, turn = self.MOVES[self.facing]
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                self.x, self.y = nx, ny
                num -= 1
            else:
                self.facing = turn

    def getPos(self):
        return [self.x, self.y]

    def getDir(self):
        return self.facing
''' + PLAY, [('play(Robot, ["Robot", "step", "step", "getPos", "getDir", "step", "step", "step", "getPos", "getDir"], [[6, 3], [2], [2], [], [], [2], [1], [4], [], []])', [None, None, None, [4, 0], 'East', None, None, None, [1, 2], 'West'])])
lc(1801, 'Number of Orders in the Backlog', 'number-of-orders-in-the-backlog', 'm', 'Two heaps: highest buy and lowest sell', 'An order book API: a buy matches the cheapest sell, a sell matches the highest buy. A min heap of sells and a max heap of buys (negated prices) give the best match at once.', r'''
import heapq


def get_number_of_backlog_orders(orders):
    buys = []                                # (-price, amount), so the highest price is on top
    sells = []                               # (price, amount)
    for price, amount, kind in orders:
        if kind == 0:                        # a buy order
            while amount and sells and sells[0][0] <= price:
                sell_price, sell_amount = heapq.heappop(sells)
                used = min(amount, sell_amount)
                amount -= used
                if sell_amount > used:
                    heapq.heappush(sells, (sell_price, sell_amount - used))
            if amount:
                heapq.heappush(buys, (-price, amount))
        else:                                # a sell order
            while amount and buys and -buys[0][0] >= price:
                buy_price, buy_amount = heapq.heappop(buys)
                used = min(amount, buy_amount)
                amount -= used
                if buy_amount > used:
                    heapq.heappush(buys, (buy_price, buy_amount - used))
            if amount:
                heapq.heappush(sells, (price, amount))
    return sum(amount for _, amount in buys + sells) % (10 ** 9 + 7)
''', [('get_number_of_backlog_orders([[10, 5, 0], [15, 2, 1], [25, 1, 1], [30, 4, 0]])', 6), ('get_number_of_backlog_orders([[7, 1000000000, 1], [15, 3, 0], [5, 999999995, 0], [5, 1, 1]])', 999999984)])
lc(1032, 'Stream of Characters', 'stream-of-characters', 'h', 'A trie of reversed words, checked from the newest letter', 'Like a WebSocket that gets one letter at a time and must say at once if the latest letters end a banned word. Store the words backwards in a trie and walk it from the newest letter back.', r'''
class StreamChecker:
    def __init__(self, words):
        self.trie = {}
        self.longest = 0
        for word in words:
            node = self.trie
            for ch in reversed(word):
                node = node.setdefault(ch, {})
            node["$"] = True
            self.longest = max(self.longest, len(word))
        self.recent = []

    def query(self, letter):
        self.recent.append(letter)
        if len(self.recent) > self.longest:
            self.recent.pop(0)
        node = self.trie
        for ch in reversed(self.recent):
            if ch not in node:
                return False
            node = node[ch]
            if "$" in node:
                return True
        return False
''' + PLAY, [('play(StreamChecker, ["StreamChecker"] + ["query"] * 12, [[["cd", "f", "kl"]]] + [[c] for c in "abcdefghijkl"])', [None, False, False, False, True, False, True, False, False, False, False, False, True])])
lc(2642, 'Design Graph With Shortest Path Calculator', 'design-graph-with-shortest-path-calculator', 'h', 'Dijkstra with a heap on every query', 'Like a gateway that finds the cheapest chain of services. Keep the edges in a dict of lists, let addEdge append, and run Dijkstra with a heap for each shortestPath question.', r'''
import heapq


class Graph:
    def __init__(self, n, edges):
        self.out = {node: [] for node in range(n)}
        for edge in edges:
            self.addEdge(edge)

    def addEdge(self, edge):
        start, end, cost = edge
        self.out[start].append((end, cost))

    def shortestPath(self, node1, node2):
        best = {node1: 0}
        heap = [(0, node1)]
        while heap:
            dist, node = heapq.heappop(heap)
            if node == node2:
                return dist
            if dist > best[node]:
                continue
            for nxt, cost in self.out[node]:
                if dist + cost < best.get(nxt, float("inf")):
                    best[nxt] = dist + cost
                    heapq.heappush(heap, (dist + cost, nxt))
        return -1
''' + PLAY, [('play(Graph, ["Graph", "shortestPath", "shortestPath", "addEdge", "shortestPath"], [[4, [[0, 2, 5], [0, 1, 2], [1, 2, 1], [3, 0, 3]]], [3, 2], [0, 3], [[1, 3, 4]], [0, 3]])', [None, 6, -1, None, 6])])
lc(2286, 'Booking Concert Tickets in Groups', 'booking-concert-tickets-in-groups', 'h', 'A segment tree with the max and the sum of free seats per range', 'A booking API must answer "first row with k free seats together" and "book k scattered seats" fast. A segment tree keeps the most free seats in a row and the total free seats for every range of rows.', r'''
class BookMyShow:
    def __init__(self, n, m):
        self.n = n
        self.m = m
        size = 1
        while size < n:
            size *= 2
        self.size = size
        self.most = [0] * (2 * size)          # the most free seats in one row of the range
        self.total = [0] * (2 * size)         # all free seats of the range
        for row in range(n):
            self.most[size + row] = m
            self.total[size + row] = m
        for i in range(size - 1, 0, -1):
            self.pull(i)
        self.first_free = 0                   # rows before this one are full

    def pull(self, i):
        self.most[i] = max(self.most[2 * i], self.most[2 * i + 1])
        self.total[i] = self.total[2 * i] + self.total[2 * i + 1]

    def set_free(self, row, free):
        i = self.size + row
        self.most[i] = free
        self.total[i] = free
        i //= 2
        while i:
            self.pull(i)
            i //= 2

    def first_row_with(self, k, max_row):
        """The first row up to max_row with at least k free seats, or -1."""
        if self.most[1] < k:
            return -1
        i = 1
        while i < self.size:
            i = 2 * i if self.most[2 * i] >= k else 2 * i + 1
        row = i - self.size
        return row if row <= max_row else -1

    def free_up_to(self, max_row, i=1, low=0, high=None):
        if high is None:
            high = self.size - 1
        if low > max_row:
            return 0
        if high <= max_row:
            return self.total[i]
        middle = (low + high) // 2
        return self.free_up_to(max_row, 2 * i, low, middle) + self.free_up_to(max_row, 2 * i + 1, middle + 1, high)

    def gather(self, k, maxRow):
        row = self.first_row_with(k, maxRow)
        if row == -1:
            return []
        used = self.m - self.most[self.size + row]
        self.set_free(row, self.most[self.size + row] - k)
        return [row, used]

    def scatter(self, k, maxRow):
        if self.free_up_to(maxRow) < k:
            return False
        row = self.first_free
        while k > 0:
            free = self.total[self.size + row]
            take = min(free, k)
            self.set_free(row, free - take)
            k -= take
            if self.total[self.size + row] == 0:
                row += 1
        self.first_free = row
        return True
''' + PLAY, [('play(BookMyShow, ["BookMyShow", "gather", "gather", "scatter", "scatter"], [[2, 5], [4, 0], [2, 0], [5, 1], [5, 1]])', [None, [0, 0], [], True, False])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Problems that match the work of an API service: ordering fields, close values, a quick check in sorted data, splitting a total, calling a hidden function as few times as possible, a state machine that wraps around, an order book with two heaps, a stream checked letter by letter, the cheapest path between services and a seat booking system with a segment tree.</p>'), kw=['LeetCode', 'sorting', 'two pointers', 'heaps', 'trie', 'Dijkstra', 'segment tree', 'design'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'FastAPI reads type hints: path, query, body and header values are converted and checked by Pydantic, and bad input gets 422 with locations.',
    'Pydantic models use Field limits, Literal, nested models and validators, and give model_dump and a JSON Schema for the docs.',
    'response_model shapes the answer, HTTPException sends errors, and /openapi.json, /docs and /redoc come for free.',
    'Depends shares the database, the user and paging. yield closes resources, and dependency_overrides swaps them in tests.',
    'Use async def only with awaitable libraries, plain def otherwise. A blocking call in async def stalls every request.'],
    'Next: API security, then the web revision exam.')}
{files('Three tasks: write a Pydantic model for products, build dependency injection like Depends, and build a router that reads type hints.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does FastAPI use to know that book_id must be a whole number?', ['A comment', 'The type hint book_id: int', 'A serializer', 'The URL name'], 1, 'Type hints are the rules.', 'abc in that place gives 422.')
K.quiz('e', 'Where are FastAPI&#39;s interactive docs by default?', ['/admin', '/docs (Swagger UI) and /redoc', '/api', '/help'], 1, 'Built in.', 'They are made from /openapi.json.')
K.quiz('e', 'What status code does FastAPI send when the body does not match the Pydantic model?', ['400', '422', '500', '404'], 1, 'Unprocessable.', 'The detail lists each problem with its location.')
K.quiz('m', 'In def list_books(min_year: int = 0), where does min_year come from?', ['The JSON body', 'The query string, such as ?min_year=1900', 'The path', 'A header'], 1, 'Simple types not in the path are query parameters.', 'A Pydantic model type would be the body.')
K.quiz('m', 'What does response_model=BookOut do?', ['Nothing', 'Checks the returned data and keeps only the fields of BookOut, and shows the shape in the docs', 'Changes the status code', 'Saves to the database'], 1, 'It filters the output.', 'Secrets such as password hashes never leak.')
K.quiz('m', 'Why does get_db use yield instead of return?', ['It is faster', 'The code after yield runs after the answer, so the connection is always closed', 'FastAPI needs generators', 'To return two values'], 1, 'Clean up.', 'It runs even when the endpoint raises an error.')
K.quiz('m', 'How do you replace the real database with a fake one in a test?', ['Edit main.py', 'app.dependency_overrides[get_db] = fake_db', 'Monkeypatch sqlite3', 'Use a second app'], 1, 'Overrides.', 'Clear them after the test.')
K.quiz('m', 'Which Pydantic tool checks a rule that needs two fields?', ['Field(gt=0)', 'A model_validator', 'Literal', 'A type hint'], 1, 'Across fields.', 'field_validator sees one field only.')
K.quiz('m', 'An endpoint uses requests.get (a blocking library). How should it be written?', ['async def', 'A plain def, so FastAPI runs it in its thread pool', 'With yield', 'As a background task'], 1, 'Blocking calls need threads.', 'Or switch to httpx.AsyncClient with await.')
K.quiz('h', 'Ten requests hit async def slow(): time.sleep(0.2) at once on one worker. How long do they take?', ['0.2 s', 'About 2 s, because the blocking sleep stops the event loop', '0.02 s', 'They fail'], 1, 'The loop is stuck.', 'The program measured 2.0 s.')
K.quiz('h', 'What is the difference between BackgroundTasks and a task queue such as Celery?', ['None', 'BackgroundTasks run in the same process after the answer and are lost on a crash, a queue stores the job and retries it in separate workers', 'Celery is only for Django', 'BackgroundTasks are slower'], 1, 'Same process or durable.', 'Use a queue for payments, reports and anything that must not be lost.')
K.quiz('x', 'In the style of an MIT 6.1810 operating systems exam: why can one async process serve hundreds of waiting requests while a thread per request server needs hundreds of threads?', ['It cannot', 'A waiting coroutine only keeps a small object and gives the loop back at await, while each thread needs its own stack and the OS must switch between them', 'Async code runs on many cores', 'Threads cannot wait'], 1, 'Cheap waiting.', 'CPU heavy work still needs processes, because one loop runs on one core.')
K.quiz('x', 'In the style of a Stanford CS 144 networking exam: an endpoint calls three services that each take 0.3 s and do not depend on each other. How fast can it answer, and how?', ['0.9 s always', 'About 0.3 s, by awaiting the three calls together with asyncio.gather', '0.1 s', '0.6 s'], 1, 'Run the waits at the same time.', 'In a row they would add up to 0.9 s.')

K.calc('e', '10 requests each wait 0.2 s with await on one event loop. About how many seconds in total?', '0.2', 'They wait together.', ['Each await gives the loop back.', 'All ten waits overlap.', eq('&asymp; 0.2 s')], check=0.2, tol=0.01)
K.calc('e', 'The same 10 requests with time.sleep(0.2) inside async def. How many seconds?', '2', 'One after another.', ['The loop is blocked during each sleep.', '10 &times; 0.2.', eq('2.0 s')], check=10 * 0.2, tol=0.01)
K.calc('e', 'Three service calls of 0.3 s in a row. How many seconds?', '0.9', 'Add them.', ['Each waits for the one before.', '0.3 &times; 3.', eq('0.9 s')], check=0.3 * 3, tol=0.01)
K.calc('m', '500 requests a second, each takes 0.2 s. How many are in flight at once on average?', '100', "Little's law.", ['in flight = rate &times; time.', '500 &times; 0.2.', eq('100 requests')], check=500 * 0.2)
K.calc('m', 'A thread pool has 40 threads and each request blocks one thread for 0.2 s. How many requests a second at most?', '200', 'threads / time.', ['One thread serves 1 / 0.2 = 5 requests a second.', '40 &times; 5.', eq('200 requests a second')], check=40 / 0.2)
K.calc('m', 'Using the rule 2 &times; cores + 1, how many workers for a server with 4 cores?', '9', '2 &times; 4 + 1.', ['2 &times; 4 = 8.', 'Plus 1.', eq('9 workers')], check=2 * 4 + 1)
K.calc('m', 'A Field(gt=0, le=10) for quantity. How many whole numbers are allowed?', '10', 'From 1 to 10.', ['gt=0 means at least 1.', 'le=10 means at most 10.', eq('10 values')], check=10)
K.calc('m', 'A sku pattern is three capital letters, a hyphen and four digits. How many different skus exist?', '175760000', '26<sup>3</sup> &times; 10<sup>4</sup>.', ['26<sup>3</sup> = 17,576 letter parts.', '10<sup>4</sup> = 10,000 digit parts.', '17,576 &times; 10,000.', eq('175,760,000')], check=26 ** 3 * 10 ** 4)
K.calc('h', 'At 500 requests a second and 200 per process (thread limit), how many processes are needed?', '3', 'Round up 500 / 200.', ['500 / 200 = 2.5.', 'A part process is a whole process.', eq('3 processes')], check=-(-500 // 200))
K.calc('x', 'In the style of a CMU 15-440 distributed systems exam: three independent calls of 0.3 s each fail 1 % of the time. With asyncio.gather, what is the chance that all three succeed? Answer in percent, rounded to 2 places.', '97.03', '0.99<sup>3</sup>.', ['Each succeeds with 0.99.', 'All three: 0.99 &times; 0.99 &times; 0.99 = 0.970299.', 'Times 100.', eq('&asymp; 97.03 %')], check=round(0.99 ** 3 * 100, 2), tol=0.005)

K.assign('product', 'e', 'Write a Pydantic model for products',
         '<p>Finish the model <code>Product</code>, the same kind of model FastAPI uses for a request body. name: 2 to 40 characters after stripping spaces. price: a number greater than 0. sku: three capital letters, a hyphen and four digits, such as TEA-0001. stock: a whole number, 0 or more, 0 by default. tags: a list of text that is stripped, lower case, without empty tags and without repeats, in the order given. parse_product(data) returns ["ok", the data] or ["errors", the sorted names of the bad fields].</p>',
         r'''
from pydantic import BaseModel, Field, ValidationError, field_validator


class Product(BaseModel):
    name: str
    price: float
    sku: str
    stock: int = 0
    tags: list[str] = []


def parse_product(data):
    try:
        product = Product(**data)
    except ValidationError as error:
        return ["errors", sorted(".".join(str(part) for part in problem["loc"]) for problem in error.errors())]
    return ["ok", product.model_dump()]
''', [('parse_product({"name": " Green tea ", "price": 3.5, "sku": "TEA-0001", "tags": ["Hot", "drink", "hot ", ""]})', ['ok', {'name': 'Green tea', 'price': 3.5, 'sku': 'TEA-0001', 'stock': 0, 'tags': ['hot', 'drink']}]), ('parse_product({"name": "Cake", "price": "5", "sku": "CAK-0042", "stock": "7"})', ['ok', {'name': 'Cake', 'price': 5.0, 'sku': 'CAK-0042', 'stock': 7, 'tags': []}]), ('parse_product({"name": "X", "price": 0, "sku": "tea-1", "stock": -1})', ['errors', ['name', 'price', 'sku', 'stock']]), ('parse_product({"price": 2})', ['errors', ['name', 'sku']]), ('parse_product({"name": "Pie", "price": "cheap", "sku": "PIE-0007"})', ['errors', ['price']])],
         r'''
from pydantic import BaseModel, Field, ValidationError, field_validator


class Product(BaseModel):
    name: str = Field(min_length=2, max_length=40)
    price: float = Field(gt=0)
    sku: str = Field(pattern="^[A-Z]{3}-[0-9]{4}$")       # like ABC-1234
    stock: int = Field(default=0, ge=0)
    tags: list[str] = []

    @field_validator("name")
    @classmethod
    def strip_name(cls, value):
        return value.strip()

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, value):
        result = []
        for tag in value:
            tag = tag.strip().lower()
            if tag and tag not in result:
                result.append(tag)
        return result


def parse_product(data):
    try:
        product = Product(**data)
    except ValidationError as error:
        return ["errors", sorted(".".join(str(part) for part in problem["loc"]) for problem in error.errors())]
    return ["ok", product.model_dump()]
''', 'Field(min_length=2, max_length=40), Field(gt=0), Field(pattern="^[A-Z]&#123;3&#125;-[0-9]&#123;4&#125;$") and Field(default=0, ge=0) cover the rules. A @field_validator("tags") cleans the list.', '<p>Pydantic also converts "5" into 5.0 and "7" into 7 by itself, which is why the second test passes even with text. FastAPI runs exactly this check on every request body and turns the errors into a 422 answer.</p>')
K.assign('depends', 'm', 'Build dependency injection like Depends',
         '<p>Write <code>solve(func, request, cache)</code>, a small version of what FastAPI does with Depends. Look at the parameters of func with inspect.signature. A parameter whose default is Need(provider) gets the result of solve(provider, ...), and each provider runs only once per request, so keep results in cache. Any other parameter comes from the request dict, or uses its default, or raises KeyError("missing NAME"). run_request shows which providers ran.</p>',
         r'''
import inspect


class Need:
    """Marks a parameter that another function must provide, like FastAPI's Depends."""

    def __init__(self, provider):
        self.provider = provider


def solve(func, request, cache=None):
    """Call func. Parameters with a Need default are solved first (each provider once per request),
    the others are read from the request dict."""
    args = {}
    for name, param in inspect.signature(func).parameters.items():
        if name in request:
            args[name] = request[name]
    return func(**args)


CALLS = []


def get_db():
    CALLS.append("db")
    return {"ann": ["buy milk"], "bob": []}


def get_user(token, db=Need(get_db)):
    CALLS.append("user")
    name = token.removeprefix("secret-")
    return name if name in db else None


def list_notes(user=Need(get_user), db=Need(get_db), limit=10):
    if user is None:
        return [401, "not logged in"]
    return [200, db[user][:limit]]


def run_request(request):
    CALLS.clear()
    try:
        result = solve(list_notes, request)
    except KeyError as error:
        result = [422, str(error).strip("'")]
    return [result, list(CALLS)]
''', [('run_request({"token": "secret-ann"})', [[200, ['buy milk']], ['db', 'user']]), ('run_request({"token": "secret-ann", "limit": 0})', [[200, []], ['db', 'user']]), ('run_request({"token": "secret-zed"})', [[401, 'not logged in'], ['db', 'user']]), ('run_request({})', [[422, 'missing token'], []])],
         r'''
import inspect


class Need:
    """Marks a parameter that another function must provide, like FastAPI's Depends."""

    def __init__(self, provider):
        self.provider = provider


def solve(func, request, cache=None):
    """Call func. Parameters with a Need default are solved first (each provider once per request),
    the others are read from the request dict."""
    if cache is None:
        cache = {}
    args = {}
    for name, param in inspect.signature(func).parameters.items():
        if isinstance(param.default, Need):
            provider = param.default.provider
            if provider not in cache:
                cache[provider] = solve(provider, request, cache)
            args[name] = cache[provider]
        elif name in request:
            args[name] = request[name]
        elif param.default is not inspect.Parameter.empty:
            args[name] = param.default
        else:
            raise KeyError(f"missing {name}")
    return func(**args)


CALLS = []


def get_db():
    CALLS.append("db")
    return {"ann": ["buy milk"], "bob": []}


def get_user(token, db=Need(get_db)):
    CALLS.append("user")
    name = token.removeprefix("secret-")
    return name if name in db else None


def list_notes(user=Need(get_user), db=Need(get_db), limit=10):
    if user is None:
        return [401, "not logged in"]
    return [200, db[user][:limit]]


def run_request(request):
    CALLS.clear()
    try:
        result = solve(list_notes, request)
    except KeyError as error:
        result = [422, str(error).strip("'")]
    return [result, list(CALLS)]
''', 'param.default is the Need object. Check isinstance(param.default, Need). Pass the same cache dict into every recursive call, and use inspect.Parameter.empty to see that a parameter has no default.', '<p>FastAPI does the same with the parameters of your endpoint: Depends(get_db) runs get_db once per request even when two dependencies need it, which is why tests can swap get_db with app.dependency_overrides. This pattern is called dependency injection.</p>')
K.assign('typed_router', 'h', 'Build a router that reads type hints',
         '<p>Finish <code>TypedRouter.call</code>. Read the parameters of the handler with inspect.signature. Each value comes from the path, or else from the query string, and is converted to the parameter&#39;s type hint with convert(), which is ready. A missing value without a default gives "NAME: field required". Collect every error and return [422, errors], or return [200, handler(**args)]. Matching the URL is done for you.</p>',
         r'''
import inspect


def convert(name, text, kind):
    """Turn the text from a URL into the type of the parameter, or raise ValueError with a message."""
    if kind is int:
        if not text.lstrip("-").isdigit():
            raise ValueError(f"{name}: must be an integer")
        return int(text)
    if kind is float:
        try:
            return float(text)
        except ValueError:
            raise ValueError(f"{name}: must be a number") from None
    if kind is bool:
        if text.lower() not in ("true", "false", "1", "0"):
            raise ValueError(f"{name}: must be true or false")
        return text.lower() in ("true", "1")
    return text


class TypedRouter:
    def __init__(self):
        self.routes = []

    def get(self, pattern):
        def register(handler):
            self.routes.append((pattern.strip("/").split("/"), handler))
            return handler
        return register

    def handle(self, url):
        path, _, query = url.partition("?")
        params = dict(pair.split("=", 1) for pair in query.split("&") if "=" in pair)
        parts = path.strip("/").split("/")
        for pattern, handler in self.routes:
            if len(pattern) != len(parts):
                continue
            found = {}
            for want, got in zip(pattern, parts):
                if want.startswith("{") and want.endswith("}"):
                    found[want[1:-1]] = got
                elif want != got:
                    break
            else:
                return self.call(handler, found, params)
        return [404, "Not Found"]

    def call(self, handler, path_values, query_values):
        args = dict(query_values)
        args.update(path_values)
        return [200, handler(**args)]


router = TypedRouter()


@router.get("/items/{item_id}")
def read_item(item_id: int, details: bool = False):
    return {"item_id": item_id, "details": details}


@router.get("/prices")
def prices(min_price: float, currency: str = "EUR"):
    return {"min_price": min_price, "currency": currency}
''', [('router.handle("/items/42")', [200, {'item_id': 42, 'details': False}]), ('router.handle("/items/42?details=true")', [200, {'item_id': 42, 'details': True}]), ('router.handle("/items/abc?details=maybe")', [422, ['item_id: must be an integer', 'details: must be true or false']]), ('router.handle("/prices?min_price=2.5")', [200, {'min_price': 2.5, 'currency': 'EUR'}]), ('router.handle("/prices?currency=USD")', [422, ['min_price: field required']]), ('router.handle("/prices?min_price=x")', [422, ['min_price: must be a number']]), ('router.handle("/nothing/here")', [404, 'Not Found'])],
         r'''
import inspect


def convert(name, text, kind):
    """Turn the text from a URL into the type of the parameter, or raise ValueError with a message."""
    if kind is int:
        if not text.lstrip("-").isdigit():
            raise ValueError(f"{name}: must be an integer")
        return int(text)
    if kind is float:
        try:
            return float(text)
        except ValueError:
            raise ValueError(f"{name}: must be a number") from None
    if kind is bool:
        if text.lower() not in ("true", "false", "1", "0"):
            raise ValueError(f"{name}: must be true or false")
        return text.lower() in ("true", "1")
    return text


class TypedRouter:
    def __init__(self):
        self.routes = []

    def get(self, pattern):
        def register(handler):
            self.routes.append((pattern.strip("/").split("/"), handler))
            return handler
        return register

    def handle(self, url):
        path, _, query = url.partition("?")
        params = dict(pair.split("=", 1) for pair in query.split("&") if "=" in pair)
        parts = path.strip("/").split("/")
        for pattern, handler in self.routes:
            if len(pattern) != len(parts):
                continue
            found = {}
            for want, got in zip(pattern, parts):
                if want.startswith("{") and want.endswith("}"):
                    found[want[1:-1]] = got
                elif want != got:
                    break
            else:
                return self.call(handler, found, params)
        return [404, "Not Found"]

    def call(self, handler, path_values, query_values):
        args, errors = {}, []
        for name, param in inspect.signature(handler).parameters.items():
            kind = param.annotation if param.annotation is not inspect.Parameter.empty else str
            text = path_values.get(name, query_values.get(name))
            if text is None:
                if param.default is inspect.Parameter.empty:
                    errors.append(f"{name}: field required")
                else:
                    args[name] = param.default
                continue
            try:
                args[name] = convert(name, text, kind)
            except ValueError as error:
                errors.append(str(error))
        if errors:
            return [422, errors]
        return [200, handler(**args)]


router = TypedRouter()


@router.get("/items/{item_id}")
def read_item(item_id: int, details: bool = False):
    return {"item_id": item_id, "details": details}


@router.get("/prices")
def prices(min_price: float, currency: str = "EUR"):
    return {"min_price": min_price, "currency": currency}
''', 'param.annotation is the type hint, or inspect.Parameter.empty when there is none (use str then). Catch ValueError from convert and keep going, so all errors are listed at once.', '<p>This is the core idea of FastAPI: the type hints of your function are the rules. FastAPI does it with Pydantic, so the same hints also give the OpenAPI docs and the 422 errors with their locations.</p>')

K.must('Endpoints', '@app.get("/books/{book_id}") def get_book(book_id: int). Query parameters are plain parameters, Query(10, le=100) adds limits. A Pydantic model parameter is the body. response_model, status_code, HTTPException(404, "...").')
K.must('Pydantic', 'class BookIn(BaseModel) with Field(gt=0), Field(min_length=...), Literal, nested models, @field_validator, @model_validator. model_dump(), model_dump_json(), model_json_schema(). Bad input is a 422 with locations.')
K.must('Dependencies', 'Depends(get_db) and Annotated[T, Depends(f)]. yield for clean up. Header() for tokens, OAuth2PasswordBearer for logins. app.dependency_overrides in tests.')
K.must('Async', 'async def only with awaitable libraries (httpx.AsyncClient, asyncpg). Plain def for blocking code, which runs in a thread pool. Never time.sleep or requests.get in async def. BackgroundTasks, lifespan.')
K.must('Run and test', 'fastapi dev main.py, fastapi run or uvicorn main:app --workers 4. /openapi.json, /docs, /redoc. TestClient(app) with pytest fixtures and parametrize.')

T = K.topic(
    slug='py-fastapi', topic='py-fastapi', step=(5, 'Building APIs: Django REST framework and FastAPI', 'py-w5', 'Build JSON APIs two ways: Django REST framework on top of a Django project, and FastAPI with type hints and automatic docs.', 'Advanced'),
    title='FastAPI: fast, typed APIs with automatic docs', short='FastAPI', badge='5.2', minutes=110,
    lead='Build APIs with FastAPI. Let type hints and Pydantic check every request, get docs at /docs for free, share code with dependencies, use async def the right way and test it all with pytest.',
    desc='What FastAPI is and how it compares with Flask and DRF, Pydantic models with Field limits, Literal, nested models and validators, path, query, body and header parameters, response_model, status codes and HTTPException, automatic 422 errors, OpenAPI with Swagger UI and ReDoc, dependencies with Depends, yield and Annotated, token checks and dependency_overrides, async def versus def and the event loop, BackgroundTasks and lifespan, testing with TestClient and pytest, ASGI, Starlette and Uvicorn, and the maths of concurrency, workers and timeouts.',
    summary='Pydantic models, typed parameters, response_model, Depends, async def and the event loop, docs and pytest.',
    keywords=['FastAPI', 'Pydantic', 'type hints', 'Depends', 'response_model', 'async', 'event loop', 'OpenAPI', 'TestClient', 'Uvicorn'],
    recap='<p>Type hints and Pydantic check every request and write the docs, Depends shares the database and the user, and async def serves many waiting requests at once when nothing inside it blocks.</p>',
    added='2026-11-08', leet=leet_items())
