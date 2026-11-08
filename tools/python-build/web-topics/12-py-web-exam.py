# Web and APIs 6.2: revision exam for the whole Web and APIs part. Teaches nothing new. Four predict the output papers
# (HTTP and REST with the standard library, Flask, Django with DRF, Pydantic with PyJWT and security), a find the bug
# listing, the traps, a system design answer, a mock quiz and timed problems. Every question is original and every
# answer was printed by a real run of Python 3.14 with Flask 3, Django 6.1.3, DRF 3.18.3, Pydantic 2.14.3 and
# PyJWT 2.15.1. All four papers run in the page, because none of them needs a thread or a server.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items, show

chapter('py-web-exam')
K = Kit()


def answers(title, body):
    return f'<details class="deep"><summary>{title}</summary><div class="deep-b">{body}</div></details>'


PAPER_A = r'''
import json
from http import HTTPStatus
from http.cookies import SimpleCookie
from urllib.parse import parse_qs, quote, urlencode, urljoin, urlsplit

u = urlsplit("https://api.shop.example:8443/v2/books?q=python&page=2#top")
print("Q1", u.scheme, u.hostname, u.port, u.path, u.query, u.fragment)

print("Q2", parse_qs("tag=a&tag=b&empty="), parse_qs("tag=a&tag=b&empty=", keep_blank_values=True)["empty"])

print("Q3", urlencode({"q": "tea & cake", "page": 1}), quote("/a b/"), quote("/a b/", safe=""))

print("Q4", urljoin("https://x.example/api/v1/", "books"), urljoin("https://x.example/api/v1", "books"),
      urljoin("https://x.example/api/v1/", "/books"))

print("Q5", [s.value for s in (HTTPStatus(201), HTTPStatus.NOT_FOUND)], HTTPStatus(429).phrase,
      [code // 100 for code in (204, 301, 422, 503)])

SAFE = {"GET", "HEAD", "OPTIONS"}
IDEMPOTENT = SAFE | {"PUT", "DELETE"}
print("Q6", sorted(m for m in ["GET", "POST", "PUT", "PATCH", "DELETE"] if m not in IDEMPOTENT))

c = SimpleCookie()
c.load("session=abc123; theme=dark")
print("Q7", c["session"].value, sorted(c))

body = json.dumps({"price": 9.5, "tags": ("a", "b"), "ok": None, 1: "one"})
print("Q8", body, json.loads(body)["1"])

raw = "HTTP/1.1 301 Moved Permanently\r\nLocation: /new\r\nContent-Length: 0\r\n\r\n"
status_line, *header_lines = raw.split("\r\n")[:-2]
headers = dict(line.split(": ", 1) for line in header_lines)
print("Q9", status_line.split(" ", 2), headers["Location"])

print("Q10", len("café".encode()), len("café"), "caf%C3%A9" == quote("café"))'''
PAPER_B = r'''
from flask import Blueprint, Flask, abort, g, jsonify, request, session, url_for

app = Flask(__name__)
app.secret_key = "exam-only"
BOOKS = {1: "Emma", 2: "Dune"}


@app.get("/books/<int:book_id>")
def get_book(book_id):
    if book_id not in BOOKS:
        abort(404)
    return {"id": book_id, "title": BOOKS[book_id]}


@app.post("/books")
def add_book():
    data = request.get_json(silent=True) or {}
    if "title" not in data:
        return jsonify(error="title is required"), 400
    new_id = max(BOOKS) + 1
    BOOKS[new_id] = data["title"]
    return {"id": new_id}, 201, {"Location": url_for("get_book", book_id=new_id)}


@app.get("/search")
def search():
    page = request.args.get("page", 1, type=int)
    return {"q": request.args.get("q"), "page": page}


@app.before_request
def load_user():
    g.user = request.headers.get("X-User", "guest")


@app.get("/me")
def me():
    session["visits"] = session.get("visits", 0) + 1
    return {"user": g.user, "visits": session["visits"]}


@app.errorhandler(404)
def not_found(err):
    return {"error": "not found", "path": request.path}, 404


admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.get("/stats")
def stats():
    return {"books": len(BOOKS)}


app.register_blueprint(admin)
client = app.test_client()

r = client.get("/books/2")
print("Q1", r.status_code, r.get_json())
print("Q2", client.get("/books/two").status_code, client.get("/books/9").get_json())
print("Q3", client.delete("/books/1").status_code, client.post("/books/1").status_code)
r = client.post("/books", json={"title": "Ulysses"})
print("Q4", r.status_code, r.get_json(), r.headers["Location"])
print("Q5", client.post("/books", data="not json").get_json())
print("Q6", client.get("/search?q=tea&page=x").get_json(), client.get("/search?page=3").get_json())
client.get("/me")
print("Q7", client.get("/me", headers={"X-User": "ann"}).get_json())
print("Q8", app.test_client().get("/me").get_json()["visits"])
print("Q9", client.get("/admin/stats").get_json(), client.get("/stats").status_code)
with app.test_request_context():
    print("Q10", url_for("get_book", book_id=7), url_for("admin.stats"), url_for("search", q="a b", page=2))'''
PAPER_C = r'''
import logging
import os

import django
from django.apps import AppConfig
from django.conf import settings


class ExamConfig(AppConfig):
    name = "__main__"
    label = "exam"
    path = os.getcwd()


settings.configure(
    DEBUG=False, SECRET_KEY="exam-only", ROOT_URLCONF=__name__, ALLOWED_HOSTS=["testserver"],
    INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth", "rest_framework", "__main__.ExamConfig"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    REST_FRAMEWORK={"UNAUTHENTICATED_USER": None},
)
django.setup()
logging.getLogger("django.request").setLevel(logging.ERROR)

from django.db import connection, models
from django.db.models import Count, F, Q
from django.http import JsonResponse
from django.template import Context, Engine
from django.urls import path, resolve, reverse
from rest_framework import serializers
from rest_framework.test import APIClient


class Author(models.Model):
    name = models.CharField(max_length=50)


class Book(models.Model):
    title = models.CharField(max_length=100)
    year = models.IntegerField()
    stock = models.IntegerField(default=0)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")


with connection.schema_editor() as editor:
    editor.create_model(Author)
    editor.create_model(Book)
ann = Author.objects.create(name="Ann")
bob = Author.objects.create(name="Bob")
for title, year, stock, who in [("Emma", 1815, 3, ann), ("Dune", 1965, 0, bob), ("Ubik", 1969, 5, bob)]:
    Book.objects.create(title=title, year=year, stock=stock, author=who)


def book_detail(request, pk):
    return JsonResponse({"pk": pk})


urlpatterns = [path("books/<int:pk>/", book_detail, name="book-detail")]

qs = Book.objects.filter(year__gt=1900)
print("Q1", type(qs).__name__, qs.count(), list(qs.values_list("title", flat=True)))

print("Q2", Book.objects.filter(Q(stock=0) | Q(author__name="Ann")).order_by("title").values_list("title", flat=True)[:5])

Book.objects.filter(stock__gt=0).update(stock=F("stock") - 1)
print("Q3", list(Book.objects.order_by("id").values_list("stock", flat=True)))

counts = Author.objects.annotate(n=Count("books")).order_by("-n").values_list("name", "n")
print("Q4", list(counts))

print("Q5", "JOIN" in str(Book.objects.filter(author__name="Bob").query), str(Book.objects.all().query).count("SELECT"))

print("Q6", reverse("book-detail", args=[7]), resolve("/books/7/").kwargs, resolve("/books/7/").url_name)

tpl = Engine().from_string("{% for b in books %}{{ b|upper }}{% if not forloop.last %}, {% endif %}{% empty %}none{% endfor %} {{ html }}")
print("Q7", tpl.render(Context({"books": ["emma", "dune"], "html": "<b>hi</b>"})))


class BookSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=10)
    year = serializers.IntegerField(min_value=1450)
    stock = serializers.IntegerField(required=False, default=0)


s = BookSerializer(data={"title": "A very long title", "year": "1200"})
print("Q8", s.is_valid(), sorted(s.errors))
s = BookSerializer(data={"title": "Emma", "year": "1815"})
print("Q9", s.is_valid(), dict(s.validated_data))

r = APIClient().get("/books/42/")
print("Q10", r.status_code, r.json(), APIClient().get("/books/x/").status_code)'''
PAPER_D = r'''
import base64
import hashlib
import hmac
import ipaddress
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal

import jwt
from pydantic import BaseModel, Field, ValidationError


class Item(BaseModel):
    name: str
    qty: int = 1
    size: Literal["S", "M", "L"] = "M"
    tags: list[str] = []


print("Q1", Item(name="tea", qty="3").qty, Item(name="tea").tags is Item(name="cake").tags)
try:
    Item(name="tea", qty="3.5", size="XL")
except ValidationError as err:
    print("Q2", err.error_count(), [e["loc"][0] for e in err.errors()])


class Address(BaseModel):
    city: str
    zip_code: str = Field(pattern=r"^\d{5}$")


class Order(BaseModel):
    id: int
    ship_to: Address
    note: str | None = None


try:
    Order(id=1, ship_to={"city": "Bonn", "zip_code": "5311"})
except ValidationError as err:
    print("Q3", err.errors()[0]["loc"])
o = Order(id=1, ship_to={"city": "Bonn", "zip_code": "53111"})
print("Q4", o.model_dump(exclude_none=True), o.model_dump_json(include={"id"}))

KEY = "k" * 32
token = jwt.encode({"sub": "ann", "aud": "shop", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}, KEY, algorithm="HS256")
print("Q5", token[:3], token.count("."), base64.urlsafe_b64encode(b'{"a').decode())
for kwargs in [{}, {"algorithms": ["HS256"]}, {"algorithms": ["HS256"], "audience": "shop"}]:
    try:
        jwt.decode(token, KEY, **kwargs)
        print("Q6", "ok")
    except jwt.InvalidTokenError as err:
        print("Q6", type(err).__name__)

digest = hashlib.pbkdf2_hmac("sha256", b"pw", b"salt", 1000)
print("Q7", len(digest), len(digest.hex()), len(secrets.token_hex(16)), len(secrets.token_urlsafe(16)))
print("Q8", hmac.compare_digest("abc", "abc"), hmac.new(b"k", b"msg", "sha256").hexdigest() == hmac.new(b"k", b"msg", "sha256").hexdigest())
print("Q9", [ipaddress.ip_address(a).is_private for a in ["10.1.2.3", "172.32.0.1", "192.168.0.9", "8.8.8.8", "::1"]])
print("Q10", hashlib.sha256(b"a").hexdigest() == hashlib.sha256(b"a").hexdigest(),
      hashlib.pbkdf2_hmac("sha256", b"a", b"s1", 10) == hashlib.pbkdf2_hmac("sha256", b"a", b"s2", 10))'''

BUGGY = r'''
import sqlite3

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"
db = sqlite3.connect("shop.db", check_same_thread=False)


@app.get("/orders/<int:order_id>")
def get_order(order_id):
    row = db.execute(f"SELECT id, customer, total FROM orders WHERE id = {order_id}").fetchone()
    return jsonify(row)


@app.post("/users")
def create_user():
    data = request.get_json()
    db.execute("INSERT INTO users (name, is_admin) VALUES (?, ?)", (data["name"], data.get("is_admin", 0)))
    return jsonify(data), 200


@app.get("/rate")
def rate():
    answer = requests.get("https://rates.example/eur")
    return answer.json()


@app.get("/orders")
def list_orders():
    limit = int(request.args.get("limit", 20))
    rows = db.execute("SELECT id, total FROM orders LIMIT ?", (limit,)).fetchall()
    return jsonify(rows)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
'''

K.code('paper_a', PAPER_A, long=True)
K.code('paper_b', PAPER_B, long=True)
K.code('paper_c', PAPER_C, long=True)
K.code('paper_d', PAPER_D, long=True)

K.lesson('map', 'How to use this revision chapter', f'''
{src('Original practice questions written for this course. Every answer was printed by a real run of Python 3.14 with Flask 3, Django 6.1, Django REST framework 3.18, Pydantic 2.14 and PyJWT 2.15.')}
<p>This chapter teaches nothing new. It revises the whole Web and APIs part in the style of a university web programming exam and a backend job interview: four predict the output papers, a find the bug listing, the traps in one table, a system design answer, a mock quiz in the Quiz tab and timed LeetCode problems. Python web frameworks have no single official certificate, so the questions follow what interviews and university courses test most often.</p>
{table(['Paper', 'Covers', 'Chapters'], [
    ['A', 'URLs, query strings, encoding, status codes, idempotency, cookies, JSON and raw HTTP', '1.1 HTTP, 1.2 sockets, 2.1 requests, 2.2 API data'],
    ['B', 'Flask routes, converters, 404 and 405, JSON bodies, query arguments, g, sessions, blueprints, url_for', '3.1 Flask, 3.2 Flask apps'],
    ['C', 'Django QuerySets, Q and F, annotate, JOINs, URLs, templates and autoescape, DRF serializers', '4.1 Django, 4.2 ORM, 5.1 DRF'],
    ['D', 'Pydantic conversion and errors, nested models, model_dump, PyJWT checks, hashes, secrets and IP checks', '5.2 FastAPI, 6.1 API security']])}
{note('Cover the answers, write down what you think each line prints, then open the answers. Every wrong guess points to the chapter in brackets. All four papers run in this page, so press Run to see the real output too.', 'tip')}
''', kw=['revision', 'exam', 'interview', 'web programming', 'predict the output', 'mock quiz'])

K.lesson('paper_a', 'Paper A: HTTP, URLs and JSON', f'''
{show('Paper A: what does each line print', PAPER_A)}
{answers('Open the answers for paper A', table(['Q', 'Output', 'Why (chapter)'], [
    ['1', 'https api.shop.example 8443 /v2/books q=python&amp;page=2 top', 'urlsplit gives each part. The port is an int, and the fragment after # is never sent to the server (1.1)'],
    ['2', "&#123;'tag': ['a', 'b']&#125; ['']", 'parse_qs always gives lists and drops empty values unless keep_blank_values=True (2.1)'],
    ['3', 'q=tea+%26+cake&amp;page=1 /a%20b/ %2Fa%20b%2F', 'urlencode writes a space as + and &amp; as %26. quote keeps / unless safe="" (2.1)'],
    ['4', 'https://x.example/api/v1/books https://x.example/api/books https://x.example/books', 'Without the trailing slash, the last part of the base is replaced. A leading / starts again at the root (2.1)'],
    ['5', '[201, 404] Too Many Requests [2, 3, 4, 5]', 'The class of a status code is code // 100: 2 success, 3 redirect, 4 client error, 5 server error (1.1)'],
    ['6', "['PATCH', 'POST']", 'GET, HEAD, OPTIONS, PUT and DELETE are idempotent: repeating them changes nothing more. POST and PATCH are not (1.1)'],
    ['7', "abc123 ['session', 'theme']", 'A Cookie header holds name=value pairs separated by semicolons, and SimpleCookie reads them (1.1)'],
    ['8', '&#123;"price": 9.5, "tags": ["a", "b"], "ok": null, "1": "one"&#125; one', 'JSON turns a tuple into a list, None into null and the int key 1 into the string "1" (2.2)'],
    ['9', "['HTTP/1.1', '301', 'Moved Permanently'] /new", 'A raw response is a status line, headers and a blank line. A 301 sends the new address in Location (1.2)'],
    ['10', '5 4 True', 'é takes 2 bytes in UTF-8, and Content-Length counts bytes. Percent encoding also works on the UTF-8 bytes (1.2)']]) + run('paper_a'))}
''', kw=['urlsplit', 'parse_qs', 'urlencode', 'quote', 'urljoin', 'HTTPStatus', 'idempotent', 'cookies', 'JSON', 'Content-Length'])

K.lesson('paper_b', 'Paper B: Flask', f'''
{show('Paper B: what does each line print', PAPER_B)}
{answers('Open the answers for paper B', table(['Q', 'Output', 'Why (chapter)'], [
    ['1', "200 &#123;'id': 2, 'title': 'Dune'&#125;", 'A view that returns a dict is sent as JSON (3.1)'],
    ['2', "404 &#123;'error': 'not found', 'path': '/books/9'&#125;", '"two" does not fit int:, so no route matches and the answer is 404, not 400. The 404 handler formats both cases (3.1)'],
    ['3', '405 405', 'The path exists but not for DELETE or POST: 405 Method Not Allowed (3.1)'],
    ['4', "201 &#123;'id': 3&#125; /books/3", 'A view can return (body, status, headers). url_for builds the Location from the view name (3.1)'],
    ['5', "&#123;'error': 'title is required'&#125;", 'get_json(silent=True) returns None for a body that is not JSON instead of failing (3.1)'],
    ['6', "&#123;'page': 1, 'q': 'tea'&#125; &#123;'page': 3, 'q': None&#125;", 'type=int falls back to the default when the value is not a number. A missing argument is None. Flask sorts the keys of JSON answers (3.1)'],
    ['7', "&#123;'user': 'ann', 'visits': 2&#125;", 'before_request fills g for each request. The session cookie from the first call came back with the second (3.2)'],
    ['8', '1', 'A new test client has no cookie, so it starts a new session (3.2)'],
    ['9', "&#123;'books': 3&#125; 404", 'The blueprint adds the prefix /admin, so /stats alone does not exist (3.2)'],
    ['10', '/books/7 /admin/stats /search?q=a+b&amp;page=2', 'Blueprint views are named blueprint.view. Arguments that are not in the rule become the query string (3.1)']]) + run('paper_b'))}
''', kw=['Flask', 'converters', '404', '405', 'get_json', 'request.args', 'g', 'session', 'Blueprint', 'url_for', 'errorhandler'])

K.lesson('paper_c', 'Paper C: Django and Django REST framework', f'''
{show('Paper C: what does each line print', PAPER_C)}
{answers('Open the answers for paper C', table(['Q', 'Output', 'Why (chapter)'], [
    ['1', "QuerySet 2 ['Dune', 'Ubik']", 'filter gives a lazy QuerySet. year__gt is a field lookup, and SQL runs only when the values are needed (4.2)'],
    ['2', "&lt;QuerySet ['Dune', 'Emma']&gt;", 'Q objects joined with | make an OR. A slice of a QuerySet is still a QuerySet (4.2)'],
    ['3', '[2, 0, 4]', 'update with F("stock") - 1 runs one SQL UPDATE, only on the rows with stock above 0 (4.2)'],
    ['4', "[('Bob', 2), ('Ann', 1)]", 'annotate(Count("books")) adds a count per author, using the related_name (4.2)'],
    ['5', 'True 1', 'Filtering across the foreign key adds a JOIN. all() is a single SELECT (4.2)'],
    ['6', "/books/7/ &#123;'pk': 7&#125; book-detail", 'reverse turns a name into a URL and resolve turns a URL back into the view and its arguments (4.1)'],
    ['7', 'EMMA, DUNE <code>&amp;lt;b&amp;gt;hi&amp;lt;/b&amp;gt;</code>', 'upper is a filter, forloop.last skips the last comma, and autoescape turns <code>&lt;</code> into <code>&amp;lt;</code> so user text cannot inject HTML (4.1)'],
    ['8', "False ['title', 'year']", 'Every field is checked and all errors are collected: the title is longer than 10 and 1200 is below 1450 (5.1)'],
    ['9', "True &#123;'title': 'Emma', 'year': 1815, 'stock': 0&#125;", '"1815" becomes the int 1815, and the default fills the missing stock (5.1)'],
    ['10', "200 &#123;'pk': 42&#125; 404", 'int: converts 42 and refuses x, which gives 404 (4.1)']]) + run('paper_c'))}
''', kw=['QuerySet', 'Q', 'F', 'annotate', 'JOIN', 'reverse', 'resolve', 'templates', 'autoescape', 'serializer', 'validated_data'])

K.lesson('paper_d', 'Paper D: Pydantic, tokens and security', f'''
{show('Paper D: what does each line print', PAPER_D)}
{answers('Open the answers for paper D', table(['Q', 'Output', 'Why (chapter)'], [
    ['1', '3 False', '"3" becomes 3. Pydantic copies a mutable default, so each object gets its own list (5.2)'],
    ['2', "2 ['qty', 'size']", '"3.5" is not a whole number and XL is not one of the Literal values. Pydantic lists every error (5.2)'],
    ['3', "('ship_to', 'zip_code')", 'Errors in nested models have the full path, which FastAPI puts after body in a 422 answer (5.2)'],
    ['4', "&#123;'id': 1, 'ship_to': &#123;'city': 'Bonn', 'zip_code': '53111'&#125;&#125; &#123;&quot;id&quot;:1&#125;", 'exclude_none drops note. include keeps only the named fields, and model_dump_json writes compact JSON (5.2)'],
    ['5', 'eyJ 2 eyJh', 'Every JWT starts with eyJ because it is base64 of &#123;" and has three parts, so two dots (6.1)'],
    ['6', 'DecodeError, InvalidAudienceError, ok', 'PyJWT 2 refuses to decode without algorithms=. A token with aud needs audience= as well (6.1)'],
    ['7', '32 64 32 22', 'SHA-256 gives 32 bytes, which is 64 hex digits. token_hex(16) gives 32 characters and token_urlsafe(16) gives 22 (6.1)'],
    ['8', 'True True', 'The same key and message always give the same HMAC. compare_digest only changes how long the comparison takes (6.1)'],
    ['9', '[True, False, True, False, True]', '172.16.0.0/12 ends at 172.31.255.255, so 172.32.0.1 is public. ::1 is the IPv6 loopback (6.1)'],
    ['10', 'True False', 'A hash is the same for the same input. Different salts give different results, which defeats precomputed tables (6.1)']]) + run('paper_d'))}
''', kw=['Pydantic', 'Literal', 'ValidationError', 'model_dump', 'JWT', 'PyJWT', 'audience', 'SHA-256', 'secrets', 'ipaddress'])

K.lesson('bugs', 'Find the bugs', f'''
{show('This Flask service has eight problems. Find them before you read on', BUGGY)}
{steps('The eight problems', [
    '<b>A secret in the code.</b> SECRET_KEY = "dev" signs the session cookies, so anyone who reads the repository can forge them. Read it from os.environ (6.1).',
    '<b>No owner check.</b> Any caller can read any order by changing the number. Filter by the logged in user and answer 404 for other people&#39;s orders (6.1, OWASP API1).',
    '<b>SQL built with an f-string.</b> Here int: happens to protect it, but the habit leads to injection. Always use ? placeholders (4.2, 6.1).',
    '<b>Mass assignment.</b> is_admin comes from the request body, so anyone can make themselves an admin. Accept only the fields you expect (6.1, OWASP API3).',
    '<b>No commit and the wrong status.</b> The INSERT is never committed, and a create should answer 201 with the new id, not echo the input with 200 (3.1, 4.2).',
    '<b>No timeout and no status check.</b> requests.get without timeout= can hang the worker for ever, and a 500 from the partner is passed on as if it were data. Use timeout=5 and raise_for_status() (2.1).',
    '<b>No upper limit.</b> limit=10000000 makes the database send every row. Cap it, for example min(limit, 100), and refuse values that are not numbers with 400 (6.1, OWASP API4).',
    '<b>Debug mode on every network interface.</b> debug=True with host 0.0.0.0 offers the interactive debugger, which can run code, to anyone who can reach the port, with only a PIN in the way. Use a real server such as gunicorn with debug off (3.2).'])}
''', kw=['find the bug', 'code review', 'SECRET_KEY', 'BOLA', 'SQL injection', 'mass assignment', 'timeout', 'debug mode'])

K.lesson('traps', 'The traps in one table', f'''
{table(['Trap', 'Looks like', 'Really', 'Chapter'], [
    ['URL fragment', 'Sent to the server', 'Stays in the browser', '1.1'],
    ['PUT and PATCH', 'The same', 'PUT replaces the whole resource and is idempotent, PATCH changes part of it', '1.1'],
    ['requests.get(url)', 'Gives up after a while', 'Waits for ever without timeout=', '2.1'],
    ['A 404 or 500 from requests', 'Raises an error', 'Only raise_for_status() raises', '2.1'],
    ['JSON keys', 'Keep their type', 'Always become strings', '2.2'],
    ['Flask int: converter', 'Bad values give 400', 'They give 404 because no route matches', '3.1'],
    ['A route without methods=', 'Accepts every method', 'Only GET (and HEAD, OPTIONS)', '3.1'],
    ['Flask debug=True', 'Fine on a server', 'The debugger can run code: never in production', '3.2'],
    ['QuerySet', 'Runs SQL when made', 'Runs when looped, sliced with a step, counted or printed', '4.2'],
    ['book.author in a loop', 'One query', 'One query per book (N + 1): use select_related', '4.2'],
    ['|safe in a template', 'Just formatting', 'Turns off autoescape: XSS if the text came from a user', '4.1'],
    ['serializer.data before is_valid()', 'Works', 'Raises an AssertionError for input data', '5.1'],
    ['time.sleep in async def', 'Waits only this request', 'Blocks every request on the event loop', '5.2'],
    ['A JWT payload', 'Secret', 'Readable by anyone, only signed', '6.1'],
    ['CORS', 'Protects the API', 'Only tells browsers which sites may read answers', '6.1'],
    ['A valid token', 'Can read anything', 'Still needs the owner check on every object', '6.1']])}
''', kw=['exam traps', 'common mistakes', 'gotchas', 'web traps'])

K.lesson('design', 'A system design answer: a link shortener API', f'''
<p>Interviews for backend roles often end with a design question. Here is a model answer for "Design an API that shortens links", using only what this part taught.</p>
{steps('The answer, step by step', [
    '<b>Requirements.</b> POST /links with a long URL gives a short code. GET /&#123;code&#125; redirects. Owners can list and delete their links. Expect 100 new links and 10,000 redirects a second.',
    '<b>API.</b> POST /links (201, Location header), GET /&#123;code&#125; (301 or 302 with Location), GET /links?cursor=... (cursor pagination), DELETE /links/&#123;code&#125; (204). Pydantic or a DRF serializer checks the URL (5.1, 5.2).',
    '<b>Codes.</b> 7 characters from 62 letters and digits give 62<sup>7</sup> &asymp; 3.5 &times; 10<sup>12</sup> codes. Make them from secrets or a counter turned into base 62, and retry on the rare clash (6.1).',
    '<b>Storage.</b> A table code (primary key), url, owner, created. Redirects read by primary key, which is one index lookup (4.2).',
    '<b>Speed.</b> Reads are 100 times the writes, so put a cache (Redis) in front: most redirects never touch the database. Answer 301 when links never change, so browsers cache them too (1.1).',
    '<b>Safety.</b> Only http and https URLs, a block list for known bad sites, a login for POST and DELETE, an owner check on delete, and a rate limit per user (6.1).',
    '<b>Async.</b> The redirect does no slow work, so plain workers are fine. Click counting goes to a queue so the redirect never waits for it (5.2).'])}
{fxs(fx('Codes available', 'codes = alphabet<sup>length</sup>', '62<sup>7</sup> &asymp; 3.52 &times; 10<sup>12</sup>.', key=True),
     fx('Storage per year', 'rows = writes per second &times; seconds per year', '100 &times; 31,536,000 &asymp; 3.2 &times; 10<sup>9</sup> rows.'),
     fx('Load on the database with a cache', 'reads to the database = reads &times; (1 &minus; hit rate)', '10,000 &times; (1 &minus; 0.99) = 100 a second.'))}
''', kw=['system design', 'URL shortener', 'base 62', 'cache', 'Redis', 'redirect', 'interview'])

K.lesson('plan', 'Exam technique and a study plan', f'''
{steps('Two weeks of revision', [
    'Days 1 to 3: paper A, then chapters 1.1 to 2.2. Write a requests call with a timeout, retries and raise_for_status from memory.',
    'Days 4 to 6: paper B, then 3.1 and 3.2. Build a small Flask JSON API with a blueprint and a test with test_client.',
    'Days 7 to 10: paper C, then 4.1, 4.2 and 5.1. Write a model, a serializer, a ViewSet and one APITestCase without notes.',
    'Days 11 to 13: paper D, then 5.2 and 6.1. Add a JWT login and an owner check to a FastAPI app.',
    'Day 14: the bug listing, the traps table, the design answer and the mock quiz in the Quiz tab under a timer.'])}
{note('In a written exam, trace each snippet on paper before you look at the options, and watch for the answers "404", "405" and "the code raises". In an interview, say your assumptions out loud, start with the simplest working API, then add caching, security and limits.', 'exam')}
{ladder(
    '<p>Explain HTTP methods and status codes, call an API with requests, and build a small Flask app.</p>',
    '<p>Build a Django site with models and the admin, and JSON APIs with DRF and FastAPI, all with tests.</p>',
    '<p>Make it fast and safe: no N + 1 queries, async used correctly, tokens, scopes, owner checks and rate limits.</p>',
    '<p>Design whole services: choose the framework, the storage, the cache and the security for given traffic, and defend the choice.</p>')}
{grow('Can build it.', 'Can test and secure it.', 'Can design it.')}
''', kw=['exam technique', 'study plan', 'interview', 'revision plan'])

lc(1629, 'Slowest Key', 'slowest-key', 'e', 'One pass over the gaps between times', 'Like finding the slowest request in an access log: each duration is the gap to the previous time. Keep the longest, and on a tie the larger letter.', r'''
def slowest_key(release_times, keys_pressed):
    best_time, best_key = release_times[0], keys_pressed[0]
    for i in range(1, len(release_times)):
        took = release_times[i] - release_times[i - 1]
        if (took, keys_pressed[i]) > (best_time, best_key):
            best_time, best_key = took, keys_pressed[i]
    return best_key
''', [('slowest_key([9, 29, 49, 50], "cbcd")', 'c'), ('slowest_key([12, 23, 36, 46, 62], "spuda")', 'a')])
lc(1701, 'Average Waiting Time', 'average-waiting-time', 'm', 'Simulate one worker with a clock', 'One server handles requests in the order they arrive. The clock is the time the server becomes free. A request starts at max(clock, arrival), and its waiting time is the finish time minus the arrival.', r'''
def average_waiting_time(customers):
    clock = 0
    waited = 0
    for arrival, work in customers:
        clock = max(clock, arrival) + work
        waited += clock - arrival
    return waited / len(customers)
''', [('average_waiting_time([[1, 2], [2, 5], [4, 3]])', 5.0), ('average_waiting_time([[5, 2], [5, 4], [10, 3], [20, 1]])', 3.25)])
lc(210, 'Course Schedule II', 'course-schedule-ii', 'm', 'Topological sort with in-degrees (Kahn)', 'The same problem as running database migrations or loading apps in dependency order. Start with every item that depends on nothing, and each time one is done, lower the count of the items waiting for it. A cycle leaves items behind, so the answer is empty.', r'''
from collections import deque


def find_order(num_courses, prerequisites):
    waiting = [0] * num_courses
    unlocks = [[] for _ in range(num_courses)]
    for course, before in prerequisites:
        waiting[course] += 1
        unlocks[before].append(course)
    ready = deque(c for c in range(num_courses) if waiting[c] == 0)
    order = []
    while ready:
        c = ready.popleft()
        order.append(c)
        for nxt in unlocks[c]:
            waiting[nxt] -= 1
            if waiting[nxt] == 0:
                ready.append(nxt)
    return order if len(order) == num_courses else []
''', [('find_order(2, [[1, 0]])', [0, 1]), ('find_order(4, [[1, 0], [2, 0], [3, 1], [3, 2]])', [0, 1, 2, 3]), ('find_order(1, [])', [0]), ('find_order(2, [[0, 1], [1, 0]])', [])])
lc(399, 'Evaluate Division', 'evaluate-division', 'm', 'A weighted graph and a search', 'Like a currency API that only knows some rates: a / b = 2 is an edge from a to b with weight 2 and from b to a with 0.5. A query multiplies the weights along any path, or gives -1.0 when there is none.', r'''
def calc_equation(equations, values, queries):
    graph = {}
    for (a, b), v in zip(equations, values):
        graph.setdefault(a, {})[b] = v
        graph.setdefault(b, {})[a] = 1 / v

    def search(start, goal):
        if start not in graph or goal not in graph:
            return -1.0
        stack, seen = [(start, 1.0)], {start}
        while stack:
            node, product = stack.pop()
            if node == goal:
                return product
            for nxt, w in graph[node].items():
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append((nxt, product * w))
        return -1.0

    return [search(a, b) for a, b in queries]
''', [('calc_equation([["a", "b"], ["b", "c"]], [2.0, 3.0], [["a", "c"], ["b", "a"], ["a", "e"], ["a", "a"], ["x", "x"]])', [6.0, 0.5, -1.0, 1.0, -1.0])])
lc(1942, 'The Number of the Smallest Unoccupied Chair', 'the-number-of-the-smallest-unoccupied-chair', 'm', 'Two heaps: free chairs and busy chairs by leaving time', 'This is exactly how a connection pool hands out the lowest free connection number. Go through arrivals in time order, first free every chair whose guest has left, then give the smallest free one.', r'''
import heapq


def smallest_chair(times, target_friend):
    order = sorted(range(len(times)), key=lambda i: times[i][0])
    free = list(range(len(times)))
    busy = []
    for i in order:
        arrive, leave = times[i]
        while busy and busy[0][0] <= arrive:
            heapq.heappush(free, heapq.heappop(busy)[1])
        chair = heapq.heappop(free)
        if i == target_friend:
            return chair
        heapq.heappush(busy, (leave, chair))
''', [('smallest_chair([[1, 4], [2, 3], [4, 6]], 1)', 1), ('smallest_chair([[3, 10], [1, 5], [2, 6]], 0)', 2)])
lc(1438, 'Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit', 'longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit', 'm', 'Sliding window with a max deque and a min deque', 'Like finding the longest stretch where response times stayed within a band. Two deques keep the window&#39;s maximum and minimum in O(1). When max minus min is too big, move the left edge.', r'''
from collections import deque


def longest_subarray(nums, limit):
    high, low = deque(), deque()
    left = best = 0
    for right, x in enumerate(nums):
        while high and high[-1] < x:
            high.pop()
        high.append(x)
        while low and low[-1] > x:
            low.pop()
        low.append(x)
        while high[0] - low[0] > limit:
            if nums[left] == high[0]:
                high.popleft()
            if nums[left] == low[0]:
                low.popleft()
            left += 1
        best = max(best, right - left + 1)
    return best
''', [('longest_subarray([8, 2, 4, 7], 4)', 2), ('longest_subarray([10, 1, 2, 4, 7, 2], 5)', 4), ('longest_subarray([4, 2, 2, 2, 4, 4, 2, 2], 0)', 3)])
lc(752, 'Open the Lock', 'open-the-lock', 'm', 'Breadth first search over 10,000 states', 'A 4 digit lock has only 10<sup>4</sup> codes, which is why short codes need attempt limits. BFS from 0000 turns one wheel up or down at each step and skips the dead ends, so the first time it reaches the target is the fewest turns.', r'''
from collections import deque


def open_lock(deadends, target):
    dead = set(deadends)
    if "0000" in dead:
        return -1
    queue, seen = deque([("0000", 0)]), {"0000"}
    while queue:
        code, turns = queue.popleft()
        if code == target:
            return turns
        for i in range(4):
            d = int(code[i])
            for nd in ((d + 1) % 10, (d - 1) % 10):
                nxt = code[:i] + str(nd) + code[i + 1:]
                if nxt not in seen and nxt not in dead:
                    seen.add(nxt)
                    queue.append((nxt, turns + 1))
    return -1
''', [('open_lock(["0201", "0101", "0102", "1212", "2002"], "0202")', 6), ('open_lock(["8888"], "0009")', 1), ('open_lock(["8887", "8889", "8878", "8898", "8788", "8988", "7888", "9888"], "8888")', -1)])
lc(2050, 'Parallel Courses III', 'parallel-courses-iii', 'h', 'Longest path in a DAG, in topological order', 'Like a deployment pipeline where jobs run in parallel once their needs are done: a job finishes at its own time plus the latest finish among the jobs it waits for. The answer is the latest finish of all.', r'''
from collections import deque


def minimum_time(n, relations, time):
    waiting = [0] * (n + 1)
    unlocks = [[] for _ in range(n + 1)]
    for before, after in relations:
        unlocks[before].append(after)
        waiting[after] += 1
    start = [0] * (n + 1)
    ready = deque(c for c in range(1, n + 1) if waiting[c] == 0)
    finish = [0] * (n + 1)
    while ready:
        c = ready.popleft()
        finish[c] = start[c] + time[c - 1]
        for nxt in unlocks[c]:
            start[nxt] = max(start[nxt], finish[c])
            waiting[nxt] -= 1
            if waiting[nxt] == 0:
                ready.append(nxt)
    return max(finish)
''', [('minimum_time(3, [[1, 3], [2, 3]], [3, 2, 5])', 8), ('minimum_time(5, [[1, 5], [2, 5], [3, 5], [3, 4], [4, 5]], [1, 2, 3, 4, 5])', 12)])
lc(1235, 'Maximum Profit in Job Scheduling', 'maximum-profit-in-job-scheduling', 'h', 'Sort by end time, DP with binary search', 'Like choosing which paid batch jobs a single worker should run. Sort jobs by end time. The best profit up to a job is either the best without it, or its profit plus the best among jobs that end by its start, found with bisect.', r'''
import bisect


def job_scheduling(start_time, end_time, profit):
    jobs = sorted(zip(end_time, start_time, profit))
    ends = [0]
    best = [0]
    for end, start, gain in jobs:
        i = bisect.bisect_right(ends, start) - 1
        value = max(best[-1], best[i] + gain)
        ends.append(end)
        best.append(value)
    return best[-1]
''', [('job_scheduling([1, 2, 3, 3], [3, 4, 5, 6], [50, 10, 40, 70])', 120), ('job_scheduling([1, 2, 3, 4, 6], [3, 5, 10, 6, 9], [20, 20, 100, 70, 60])', 150), ('job_scheduling([1, 1, 1], [2, 3, 4], [5, 6, 4])', 6)])
lc(630, 'Course Schedule III', 'course-schedule-iii', 'h', 'Greedy by deadline with a max heap of durations', 'Take tasks in order of their deadline. When the total time passes a deadline, drop the longest task taken so far, because that frees the most time while keeping the count. A max heap (negative numbers in heapq) finds it.', r'''
import heapq


def schedule_course(courses):
    taken = []
    total = 0
    for duration, last_day in sorted(courses, key=lambda c: c[1]):
        heapq.heappush(taken, -duration)
        total += duration
        if total > last_day:
            total += heapq.heappop(taken)
    return len(taken)
''', [('schedule_course([[100, 200], [200, 1300], [1000, 1250], [2000, 3200]])', 3), ('schedule_course([[1, 2]])', 1), ('schedule_course([[3, 2], [4, 3]])', 0)])

K.lesson('leetcode', 'LeetCode review set', leet('<p>Ten problems with the shape of backend work: the slowest call in a log, a request queue on one server, migration order, conversion rates in a graph, a connection pool, a stable latency window, a lock with only 10,000 codes, a deployment pipeline, paid batch jobs and deadlines. Try each in under 30 minutes, as in an interview.</p>'), kw=['LeetCode', 'review', 'topological sort', 'heaps', 'BFS', 'sliding window', 'dynamic programming', 'greedy'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'HTTP: the fragment stays in the browser, status class is code // 100, POST and PATCH are not idempotent, JSON keys become strings.',
    'Flask: a bad int: value gives 404, a wrong method 405, dicts become JSON, blueprints add prefixes, and debug=True never goes to production.',
    'Django and DRF: QuerySets are lazy, F updates in SQL, select_related stops N + 1, templates escape by default, serializers list every error.',
    'FastAPI and Pydantic: hints convert and check, every error has a location, async def must not block.',
    'Security: slow salted hashes, signed short lived tokens with pinned algorithms, owner checks on every object, timeouts and limits everywhere.'],
    'You have finished the Web and APIs part. The interview set and the cheatsheet cover the whole subject in one place.')}
{files('Three exam style tasks: pick the right status code, build a Flask style URL router with converters, and add ETags for caching and safe updates.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which status code fits a successful POST that created a resource?', ['200', '201', '204', '302'], 1, 'Created.', 'Add a Location header with the new URL.')
K.quiz('e', 'Which Flask call turns a view name into its URL?', ['redirect()', 'url_for()', 'reverse()', 'route()'], 1, 'Flask names.', 'In Django the same job is done by reverse().')
K.quiz('e', 'Which Django tool makes the tables from your models?', ['runserver', 'makemigrations, then migrate', 'collectstatic', 'createsuperuser'], 1, 'Migrations.', 'makemigrations writes the plan, migrate runs it.')
K.quiz('m', 'requests.get(url) returns a 500 answer. What happens?', ['An exception is raised', 'Nothing special: r.status_code is 500 until you call raise_for_status()', 'requests retries', 'It returns None'], 1, 'Only raise_for_status raises.', 'Also always pass timeout=.')
K.quiz('m', 'A loop prints book.author.name for 50 books. How many queries without select_related?', ['1', '51', '50', '2'], 1, 'N + 1.', 'select_related("author") makes it one query with a JOIN.')
K.quiz('m', 'What does a DRF ModelViewSet registered with a router give you?', ['Only GET', 'List, create, retrieve, update, partial update and delete URLs', 'An admin page', 'A template'], 1, 'Six actions.', 'The router writes /books/ and /books/&#123;pk&#125;/.')
K.quiz('m', 'In FastAPI, where does q come from in def search(q: str | None = None)?', ['The body', 'The query string', 'A header', 'The path'], 1, 'Simple types outside the path.', 'A Pydantic model parameter would be the body.')
K.quiz('m', 'Why answer 404 instead of 403 when a user asks for another user&#39;s order?', ['404 is faster', 'So the caller cannot learn which ids exist', 'HTTP forbids 403', 'Browsers cache 403'], 1, 'Hide existence.', 'Both are fine, but 404 leaks less.')
K.quiz('m', 'Which header tells a browser that a page from another origin may read the answer?', ['Authorization', 'Access-Control-Allow-Origin', 'Content-Type', 'Set-Cookie'], 1, 'CORS.', 'Never * together with credentials.')
K.quiz('m', 'What does WSGI have that ASGI improves on?', ['Nothing', 'WSGI is one request per call and sync only, ASGI is async and also supports WebSockets', 'ASGI is for Java', 'WSGI is newer'], 1, 'Async gateway.', 'Flask and classic Django use WSGI, FastAPI uses ASGI.')
K.quiz('h', 'Two users load the same record and both save changes. How do ETags with If-Match prevent the lost update?', ['They cannot', 'The second PUT carries the old ETag, the server sees it no longer matches and answers 412', 'The server merges both', 'The first save is undone'], 1, 'Optimistic concurrency.', 'The second user reloads and tries again.')
K.quiz('x', 'In the style of a CMU 15-445 database systems exam: a page lists 50 orders, each with its customer and its items. Which pair of tools loads it in 2 queries?', ['select_related for both', 'select_related("customer") for the foreign key and prefetch_related("items") for the reverse many relation', 'prefetch_related for both', 'raw SQL only'], 1, 'JOIN plus one IN query.', 'select_related works only for single valued relations.')
K.quiz('x', 'In the style of a Stanford CS 142 web applications exam: why must a site that uses session cookies protect POST forms against CSRF while a Bearer token API usually need not?', ['It must not', 'The browser adds cookies to cross site requests by itself, but never adds an Authorization header by itself', 'Cookies are encrypted', 'Bearer tokens expire'], 1, 'Ambient credentials.', 'SameSite cookies and CSRF tokens close the hole.')

K.calc('e', 'An API serves 200 requests a second and each takes 0.05 s. How many are in flight on average?', '10', "Little's law.", ['in flight = rate &times; time.', '200 &times; 0.05.', eq('10 requests')], check=200 * 0.05)
K.calc('e', 'What is the class of status code 418?', '4', 'code // 100.', ['418 // 100.', 'Class 4 means a client error.', eq('4')], check=418 // 100)
K.calc('e', '95 items, 10 per page. How many pages?', '10', 'Round up.', ['95 / 10 = 9.5.', 'A part page is a page.', eq('10 pages')], check=-(-95 // 10))
K.calc('m', 'Page 7 with 20 items per page. What OFFSET does the SQL need?', '120', '(page &minus; 1) &times; size.', ['Pages start at 1.', '(7 &minus; 1) &times; 20.', eq('OFFSET 120')], check=(7 - 1) * 20)
K.calc('m', 'How many bytes is the UTF-8 text "naïve café" (with the space)?', '12', 'ï and é take 2 bytes.', ['10 characters.', 'Two of them take 2 bytes.', '10 + 2.', eq('12 bytes')], check=len('naïve café'.encode()))
K.calc('m', '4 worker processes, 40 threads each, every request blocks a thread for 0.2 s. Requests per second at most?', '800', 'threads / time.', ['4 &times; 40 = 160 threads.', '160 / 0.2.', eq('800 requests a second')], check=4 * 40 / 0.2)
K.calc('m', 'A cache answers 99 % of 10,000 redirects a second. How many reach the database each second?', '100', 'reads &times; (1 &minus; hit rate).', ['1 &minus; 0.99 = 0.01.', '10,000 &times; 0.01.', eq('100 a second')], check=round(10_000 * (1 - 0.99)))
K.calc('m', 'A token bucket holds 20 tokens and refills 5 a second. At most how many requests pass in 10 seconds?', '70', 'capacity + rate &times; time.', ['20 at the start.', '5 &times; 10 = 50 more.', eq('70 requests')], check=20 + 5 * 10)
K.calc('h', 'Two services in a row are each up 99.9 % of the time, independently. What is the availability of the whole path, in percent, rounded to 2 places?', '99.8', 'Multiply.', ['0.999 &times; 0.999 = 0.998001.', 'Times 100.', eq('&asymp; 99.80 %')], check=round(0.999 * 0.999 * 100, 2), tol=0.005)
K.calc('x', 'In the style of an MIT 6.1800 computer systems exam: how many 7 character codes from 62 letters and digits exist? Give the answer in trillions, rounded to 2 places.', '3.52', '62<sup>7</sup>.', ['62<sup>7</sup> = 3,521,614,606,208.', 'Divide by 10<sup>12</sup>.', eq('&asymp; 3.52 trillion')], check=round(62 ** 7 / 1e12, 2), tol=0.005)

K.assign('statuspick', 'e', 'Pick the right status code',
         '<p>Finish <code>pick_status(method, logged_in, allowed, found, valid)</code>. Check in this order: not logged in gives 401, not allowed 403, not found 404, invalid input 422. When everything is fine, POST gives 201, DELETE gives 204 and every other method 200. status_table() collects six cases.</p>',
         r'''
def pick_status(method, logged_in=True, allowed=True, found=True, valid=True):
    """Return the HTTP status a REST API should send. Check in this order: who, may, exists, valid, success."""
    # TODO: 401, 403, 404 and 422 in that order, then 201 for POST, 204 for DELETE and 200 otherwise
    if not found:
        return 404
    return 200


def status_table():
    return [pick_status("GET"), pick_status("POST"), pick_status("DELETE"), pick_status("PUT", valid=False),
            pick_status("GET", logged_in=False, found=False), pick_status("PATCH", allowed=False, found=False)]
''', [('status_table()', [200, 201, 204, 422, 401, 403]), ('pick_status("DELETE", valid=False)', 422), ('pick_status("POST", logged_in=False, allowed=False)', 401), ('pick_status("HEAD")', 200)],
         r'''
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
''', 'The order of the checks is the whole task: who are you, may you, does it exist, is the input right, then what kind of success.', '<p>This order is what DRF and FastAPI do too: authentication runs first, then permissions, then the object lookup, then validation. That is why a logged out caller gets 401 even for an id that does not exist, and learns nothing about the data.</p>')
K.assign('urlrouter', 'm', 'Build a Flask style URL router',
         '<p>Finish <code>UrlRouter.bind</code> and <code>match</code>. A rule such as /books/&lt;int:book_id&gt; has fixed pieces, &lt;name&gt; for any one piece, &lt;int:name&gt; for digits only (given as an int) and &lt;path:name&gt; for the rest of the URL with its slashes. match(method, url) returns [200, name, params] for the first rule that fits the URL and the method, [405, None, &#123;&#125;] when some rule fits the URL but not the method, and [404, None, &#123;&#125;] when nothing fits.</p>',
         r'''
class UrlRouter:
    """A tiny Flask style router with the converters <name>, <int:name> and <path:name>."""

    def __init__(self):
        self.rules = []

    def add(self, methods, rule, name):
        self.rules.append((set(methods), rule.strip("/").split("/"), name))

    def bind(self, pattern, parts):
        # TODO: compare piece by piece. Fixed pieces must be equal, <name> takes any piece,
        # <int:name> needs digits and gives an int, <path:name> takes the rest joined with "/".
        # Return the dict of params, or None when the URL does not fit.
        if pattern == parts:
            return {}
        return None

    def match(self, method, url):
        parts = url.strip("/").split("/")
        for methods, pattern, name in self.rules:
            params = self.bind(pattern, parts)
            if params is not None and method in methods:
                return [200, name, params]
        # TODO: 405 when a rule fits the URL but not the method
        return [404, None, {}]


def shop_router():
    r = UrlRouter()
    r.add(["GET"], "/books", "list_books")
    r.add(["POST"], "/books", "add_book")
    r.add(["GET", "PUT"], "/books/<int:book_id>", "book")
    r.add(["GET"], "/authors/<name>/books", "author_books")
    r.add(["GET"], "/files/<path:rest>", "file")
    return r
''', [('shop_router().match("GET", "/books")', [200, 'list_books', {}]), ('shop_router().match("POST", "/books/")', [200, 'add_book', {}]), ('shop_router().match("PUT", "/books/42")', [200, 'book', {'book_id': 42}]), ('shop_router().match("GET", "/books/abc")', [404, None, {}]), ('shop_router().match("DELETE", "/books/42")', [405, None, {}]), ('shop_router().match("GET", "/authors/ann/books")', [200, 'author_books', {'name': 'ann'}]), ('shop_router().match("GET", "/files/img/2026/cat.png")', [200, 'file', {'rest': 'img/2026/cat.png'}]), ('shop_router().match("GET", "/files")', [404, None, {}])],
         r'''
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
''', 'Walk over the pieces of the rule with enumerate. A path converter takes "/".join(parts[i:]) and ends the walk. Otherwise the rule and the URL must have the same number of pieces. In match, remember that a rule fitted the URL even when the method was wrong.', '<p>Werkzeug, the router inside Flask, works the same way with compiled regular expressions, and it also answers 405 with an Allow header listing the methods that would work. Django&#39;s path() converters (int, str, slug, uuid, path) follow the same idea.</p>')
K.assign('etagstore', 'h', 'Add ETags for caching and safe updates',
         '<p>make_etag is ready. Finish <code>handle(store, method, key, headers, body)</code>. A missing key gives [404, None, None]. GET answers [200, tag, doc], or [304, tag, None] when If-None-Match equals the current tag. PUT without If-Match answers [428, None, None], with a tag that is not current [412, tag, None], and otherwise saves the body and answers [200, new tag, body]. lost_update_story shows two users who both read the same version.</p>',
         r'''
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
        # TODO: 304 when If-None-Match equals the current tag
        return [200, tag, doc]
    if method == "PUT":
        # TODO: 428 without If-Match, 412 when it does not match
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
''', [('make_etag({"b": 1, "a": 2}) == make_etag({"a": 2, "b": 1})', True), ('lost_update_story()', [200, 412, 304, 2]), ('handle({"k": {"x": 1}}, "PUT", "k", {}, {"x": 2})', [428, None, None]), ('handle({}, "GET", "k")', [404, None, None]), ('handle({"k": {"x": 1}}, "GET", "k", {"If-None-Match": "stale"})[0]', 200)],
         r'''
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
''', 'Compute the current tag once, right after loading the document. For PUT, check that If-Match is there before you compare it.', '<p>304 saves bandwidth because the client keeps its copy. 412 is optimistic concurrency: nobody locks the record, but the second writer is told that it changed and must reload. 428 Precondition Required (RFC 6585) forces clients to send If-Match at all.</p>')

K.must('HTTP', 'Status classes 2xx, 3xx, 4xx, 5xx. 201 with Location, 204, 301, 304, 400, 401, 403, 404, 405, 412, 422, 429. Idempotent: GET, PUT, DELETE. requests.get(url, timeout=5) and raise_for_status().')
K.must('Flask', '@app.get("/books/&lt;int:book_id&gt;"), request.args.get("page", 1, type=int), request.get_json(), return dict, status, headers. g, session, Blueprint(url_prefix=...), url_for, errorhandler, test_client().')
K.must('Django and DRF', 'Lazy QuerySets, Q, F, annotate, select_related and prefetch_related, makemigrations and migrate, reverse and resolve, autoescape. Serializer.is_valid() then validated_data, ModelViewSet with a router.')
K.must('FastAPI', 'Type hints decide path, query and body. Pydantic gives 422 with locations. response_model, Depends with yield, async def only with await, TestClient and dependency_overrides.')
K.must('Security', 'Slow salted hashes, JWT with pinned algorithms and short exp, scopes give 403, owner checks give 404, CORS for browsers, ? placeholders, caps on page size, secrets in the environment.')

T = K.topic(
    slug='py-web-exam', topic='py-web-exam', kind='revision',
    step=(6, 'Securing APIs and the web revision exam', 'py-w6', 'Protect what you built: passwords, tokens, OAuth 2.0, CORS and the OWASP API Top 10, then test the whole web section in one exam.', 'Advanced'),
    title='Web revision exam: HTTP, Flask, Django, FastAPI and security', short='Web revision exam', badge='6.2', minutes=100,
    lead='Revise the whole Web and APIs part: four predict the output papers that run in the page, a Flask service with eight bugs, the traps in one table, a system design answer, a mock quiz and timed problems.',
    desc='Predict the output papers on URLs, query strings, encoding, status codes, idempotency, cookies and JSON, on Flask routes, converters, 404 and 405, sessions and blueprints, on Django QuerySets, Q, F, annotate, URLs, templates and DRF serializers, and on Pydantic, PyJWT, hashes and secrets, a find the bug listing, a traps table, a link shortener system design answer, a study plan, a mock quiz and interview style coding tasks.',
    summary='Four papers that run in the page, eight bugs, the web traps, a design answer and a mock quiz.',
    keywords=['web revision', 'exam practice', 'mock quiz', 'predict output', 'find the bug', 'system design', 'Flask', 'Django', 'FastAPI', 'interview'],
    recap='<p>Trace every snippet on paper, know the status codes and the traps by heart, and practise the design answer out loud. Interviews reward a working simple API first, then speed and security.</p>',
    added='2026-11-08', leet=leet_items())
