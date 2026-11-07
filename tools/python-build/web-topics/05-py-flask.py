# Web and APIs 3.1: Flask basics. Checked against the Flask 3.1 documentation (quickstart, routing and converters,
# the request and response objects, returning dicts and lists as JSON, templates, sessions and flashing, error
# handlers, the test client, deploying), the Jinja 3.1 template designer documentation and Werkzeug 3.1 serving.
# Flask's test client sends requests to the app with no network, so most programs run in the page (Flask is installed
# into the browser on first use). The one that starts a real server uses local().
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, lc, leet, files, grow, leet_items

chapter('py-flask')
K = Kit()

K.code('routes', r'''
from flask import Flask, url_for
from markupsafe import escape

app = Flask(__name__)


@app.route("/")
def home():
    return "Welcome to the book shop"


@app.route("/hello/<name>")                    # <name> is a part of the URL that changes
def hello(name):
    return f"Hello, {escape(name)}!"           # escape: a name like <script> cannot run in the page


@app.route("/add/<int:a>/<int:b>")             # int: only matches whole numbers and converts them
def add(a, b):
    return f"{a} + {b} = {a + b}"


@app.route("/books", methods=["GET", "POST"])
def books():
    return "list of books"


# The test client sends requests to the app without a real server or network
client = app.test_client()
for path in ["/", "/hello/Ann", "/hello/<i>Ann", "/add/2/40", "/add/2/x", "/nothing"]:
    response = client.get(path)
    text = response.get_data(as_text=True) if response.status_code == 200 else ""
    print(path, "->", response.status, text)

print("POST /books ->", client.post("/books").status_code)
print("DELETE /books ->", client.delete("/books").status_code, "(method not allowed)")

with app.test_request_context():
    print(url_for("hello", name="Bob"), url_for("add", a=1, b=2), url_for("home", page=3))

for rule in app.url_map.iter_rules():
    if rule.endpoint != "static":
        print(rule.rule, "->", rule.endpoint, sorted(rule.methods - {"HEAD", "OPTIONS"}))
''')
K.code('request_response', r'''
from flask import Flask, abort, jsonify, make_response, redirect, request, url_for

app = Flask(__name__)


@app.route("/search")
def search():
    words = request.args.get("q", "")              # ?q=... from the URL, "" when it is missing
    page = request.args.get("page", 1, type=int)   # converted to int, 1 when missing or not a number
    return f"searching {words!r}, page {page}"


@app.route("/login", methods=["POST"])
def login():
    user = request.form.get("user", "")            # fields of an HTML form
    return f"form said user={user}"


@app.route("/echo", methods=["POST"])
def echo():
    data = request.get_json(silent=True)          # the JSON body, or None when it is not JSON
    if data is None:
        return {"error": "send JSON"}, 400        # a (body, status) pair
    return {"you_sent": data, "keys": len(data)}   # a dict becomes a JSON response


@app.route("/old-page")
def old_page():
    return redirect(url_for("search", q="moved"))  # 302 and a Location header


@app.route("/secret")
def secret():
    abort(403)                                    # stop here with an error status


@app.route("/custom")
def custom():
    response = make_response("made by hand", 201)
    response.headers["X-Shop"] = "brainy"
    response.set_cookie("theme", "dark")
    return response


@app.errorhandler(404)
def not_found(error):
    return jsonify(error="not found", path=request.path), 404


client = app.test_client()
print(client.get("/search?q=dune&page=2").get_data(as_text=True))
print(client.get("/search?page=abc").get_data(as_text=True))
print(client.post("/login", data={"user": "ann"}).get_data(as_text=True))
print(client.post("/echo", json={"title": "Emma", "year": 1815}).get_json())
r = client.post("/echo", data="not json")
print(r.status_code, r.get_json())
r = client.get("/old-page")
print(r.status_code, r.headers["Location"])
print(client.get("/secret").status_code)
r = client.get("/custom")
print(r.status_code, r.headers["X-Shop"], r.headers["Set-Cookie"])
print(client.get("/missing").get_json())
''', long=True)
K.code('templates', r'''
from flask import Flask, render_template
from jinja2 import DictLoader

app = Flask(__name__)

# In a real project these are files in a folder called templates/. Here they live in a dict.
app.jinja_loader = DictLoader({
    "base.html": """<html><title>{% block title %}Shop{% endblock %}</title>
<body>{% block body %}{% endblock %}</body></html>""",

    "books.html": """{% extends "base.html" %}
{% block title %}Books ({{ books|length }}){% endblock %}
{% block body %}<h1>Hello {{ user }}</h1>
<ul>{% for book in books %}
  <li>{{ loop.index }}. {{ book.title|upper }} ({{ book.year }}){% if book.year < 1900 %} classic{% endif %}</li>
{%- else %}<li>No books yet</li>{% endfor %}
</ul>{% endblock %}""",
})

BOOKS = [{"title": "Dune", "year": 1965}, {"title": "Emma", "year": 1815}]


@app.route("/books/<user>")
def books(user):
    return render_template("books.html", user=user, books=BOOKS)


@app.route("/empty")
def empty():
    return render_template("books.html", user="Bob", books=[])


client = app.test_client()
print(client.get("/books/Ann").get_data(as_text=True))
page = client.get("/books/<b>Ann").get_data(as_text=True)
print([line for line in page.split("\n") if "<h1>" in line][0])   # Jinja escaped the < and >
print(client.get("/empty").get_data(as_text=True))
''', long=True)
K.code('forms_session', r'''
import base64

from flask import Flask, flash, get_flashed_messages, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = "change-me"          # signs the session cookie. In real apps read it from an environment variable

PAGE = """{% for message in get_flashed_messages() %}[{{ message }}] {% endfor %}
{% if session.user %}Logged in as {{ session.user }}{% else %}Please log in{% endif %}"""

USERS = {"ann": "pw123"}


@app.route("/")
def home():
    return render_template_string(PAGE)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("user", "").strip().lower()
        if USERS.get(name) == request.form.get("pw"):
            session["user"] = name
            flash("Welcome back!")
            return redirect(url_for("home"))        # Post, Redirect, Get: a refresh will not post again
        flash("Wrong name or password")
    return render_template_string(PAGE + '\n<form method="post">...</form>'), 200


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Bye")
    return redirect(url_for("home"))


client = app.test_client()                       # keeps cookies between requests, like a browser
print(client.get("/").get_data(as_text=True))
print("---")
r = client.post("/login", data={"user": "ann", "pw": "nope"})
print(r.status_code, r.get_data(as_text=True))
print("---")
r = client.post("/login", data={"user": "Ann", "pw": "pw123"})
print(r.status_code, "Location:", r.headers["Location"])
print(client.get("/").get_data(as_text=True))
print("---")
cookie = client.get_cookie("session")
data_part = cookie.value.split(".")[0]
print("anyone can read the cookie:", base64.urlsafe_b64decode(data_part + "=="))   # signed, NOT encrypted
r = client.get("/logout", follow_redirects=True)
print(r.get_data(as_text=True))
''', long=True)
K.code('json_api', r'''
from flask import Flask, request

app = Flask(__name__)
BOOKS = {1: {"id": 1, "title": "Dune", "year": 1965}}
next_id = 2


def bad_book(data):
    """Return an error message, or None when the data is a good book."""
    if not isinstance(data, dict):
        return "send a JSON object"
    if not str(data.get("title", "")).strip():
        return "title is required"
    if not isinstance(data.get("year"), int):
        return "year must be a whole number"
    return None


@app.get("/api/books")                          # @app.get is short for @app.route(..., methods=["GET"])
def list_books():
    return list(BOOKS.values())                  # lists become JSON too (Flask 2.2 and later)


@app.get("/api/books/<int:book_id>")
def get_book(book_id):
    if book_id not in BOOKS:
        return {"error": f"book {book_id} not found"}, 404
    return BOOKS[book_id]


@app.post("/api/books")
def create_book():
    global next_id
    data = request.get_json(silent=True)
    problem = bad_book(data)
    if problem:
        return {"error": problem}, 422
    book = {"id": next_id, "title": data["title"].strip(), "year": data["year"]}
    BOOKS[next_id] = book
    next_id += 1
    return book, 201, {"Location": f"/api/books/{book['id']}"}


@app.delete("/api/books/<int:book_id>")
def delete_book(book_id):
    if BOOKS.pop(book_id, None) is None:
        return {"error": f"book {book_id} not found"}, 404
    return "", 204


client = app.test_client()
r = client.post("/api/books", json={"title": " Emma ", "year": 1815})
print(r.status_code, r.headers["Location"], r.get_json())
r = client.post("/api/books", json={"title": "", "year": 2000})
print(r.status_code, r.get_json())
r = client.post("/api/books", json={"title": "Ulysses", "year": "1922"})
print(r.status_code, r.get_json())
print(client.get("/api/books").get_json())
print(client.get("/api/books/7").status_code, client.get("/api/books/7").get_json())
print(client.delete("/api/books/1").status_code, client.delete("/api/books/1").status_code)
print(client.get("/api/books").get_json())
''', long=True)
K.code('real_server', r'''
import logging
import threading

import requests
from flask import Flask
from werkzeug.serving import make_server

app = Flask(__name__)
logging.getLogger("werkzeug").setLevel(logging.ERROR)     # hide the one log line per request


@app.get("/api/ping")
def ping():
    return {"pong": True}


# What "flask --app real_server run" does, but in a thread so this one file can also call it
server = make_server("127.0.0.1", 0, app)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_port}/api/ping"

r = requests.get(url, timeout=5)
print(r.status_code, r.headers["Content-Type"], r.json())
print("served by:", r.headers["Server"].split("/")[0])
server.shutdown()
''')

K.lesson('idea', 'What Flask is', f'''
{src('Flask 3.1 documentation (quickstart, API, testing, deploying), Jinja 3.1 template designer documentation and PEP 3333 (WSGI).')}
{wwh('<b>Flask</b> is a small web framework for Python. You write normal functions and tell Flask which URL each one answers with <b>@app.route</b>. Flask gives every function the <b>request</b> (the URL, the form, the JSON, the cookies) and turns what it returns into an HTTP <b>response</b>. It comes with Jinja templates for HTML pages and a test client.',
     'With only http.server you would parse paths, read bodies, set headers, escape HTML and keep sessions yourself, for every page. That is slow to write and easy to get wrong, for example by letting users inject scripts.',
     'Flask does the repeated work and stays small: routing, request and response objects, templates with automatic escaping, signed session cookies and error handlers. Everything else (database, login, forms) you add with plain Python or extensions, only when you need it. That is why it is called a <b>micro</b>framework.')}
{viz('pyflask')}
{versus('Python web frameworks', ['', 'http.server', 'Flask', 'Django', 'FastAPI'], [
    ['Size', 'Standard library, very basic', 'Small core, add what you need', 'Batteries included: ORM, admin, auth, forms', 'Small core focused on APIs'],
    ['Routing', 'Write if statements on self.path', '@app.route("/books/&lt;int:id&gt;")', 'urls.py with path("books/&lt;int:id&gt;/", view)', '@app.get("/books/&#123;id&#125;")'],
    ['Data checks', 'By hand', 'By hand or an extension', 'Forms and serializers', 'Automatic from type hints (pydantic)'],
    ['Interface', 'Its own', 'WSGI (sync), async views possible', 'WSGI and ASGI', 'ASGI (async)'],
    ['Good for', 'Learning, tiny tools', 'Small and medium sites, APIs, prototypes', 'Big sites with users, admin and a database', 'Fast JSON APIs with automatic docs']],
    'Learn Flask first: you see every moving part. Django (step 4) then shows what a full framework adds, and FastAPI (step 5) what type hints add for APIs.')}
''', kw=['Flask', 'web framework', 'microframework', 'WSGI', 'route', 'view function', 'request', 'response', 'Jinja', 'Django', 'FastAPI'])

K.lesson('routes', 'Routes and URLs', f'''
{run('routes')}
{table(['Converter', 'Matches', 'Gives the view'], [
    ['&lt;name&gt; or &lt;string:name&gt;', 'Any text without a slash', 'str'],
    ['&lt;int:id&gt;', 'Whole numbers such as 42', 'int'],
    ['&lt;float:price&gt;', 'Numbers such as 9.5', 'float'],
    ['&lt;path:rest&gt;', 'Text that may contain slashes', 'str'],
    ['&lt;uuid:key&gt;', 'A UUID', 'uuid.UUID']])}
{note('Build links with <code>url_for("hello", name="Bob")</code> and never by hand. If you rename a URL later, every link still works, and url_for escapes special characters for you. Extra arguments become the query string, as with page=3 above.', 'tip')}
{note('A route answers only GET (and HEAD, OPTIONS) unless you pass methods=. A wrong method gives <b>405 Method Not Allowed</b>, a URL that matches no rule gives <b>404 Not Found</b>.', 'exam')}
''', kw=['route', '@app.route', 'converter', 'int converter', 'url_for', 'methods', 'url_map', 'endpoint', '404', '405', 'escape'])

K.lesson('request', 'The request and the response', f'''
{run('request_response')}
{table(['On request', 'Holds', 'Example'], [
    ['request.args', 'The query string, like a dict', 'request.args.get("page", 1, type=int)'],
    ['request.form', 'Fields of an HTML form', 'request.form["user"]'],
    ['request.get_json()', 'The JSON body', 'silent=True gives None instead of an error'],
    ['request.files', 'Uploaded files', 'request.files["photo"].save(path)'],
    ['request.headers, cookies', 'Headers and cookies', 'request.headers["User-Agent"]'],
    ['request.method, path, url', 'The method and the address', '"POST", "/login"']])}
{table(['A view returns', 'Flask sends'], [
    ['A str', '200 with Content-Type text/html'],
    ['A dict or a list', '200 with JSON (keys sorted by default)'],
    ['(body, status) or (body, status, headers)', 'Your status and extra headers'],
    ['redirect(url)', '302 with a Location header'],
    ['abort(code)', 'Stops at once with that error status'],
    ['make_response(...)', 'A Response object you can change: headers, cookies']])}
{note('<code>request</code> looks like a global variable, but each request in each thread sees its own. Flask does this with context variables, so two users at the same moment never see each other&#39;s data.', 'tip')}
''', kw=['request.args', 'request.form', 'get_json', 'request.files', 'headers', 'make_response', 'jsonify', 'redirect', 'abort', 'errorhandler', 'status code'])

K.lesson('templates', 'Templates with Jinja', f'''
{run('templates')}
{table(['Jinja', 'Does', 'Example'], [
    ['&#123;&#123; value &#125;&#125;', 'Prints a value, HTML escaped', '&#123;&#123; user &#125;&#125;'],
    ['&#123;% for ... %&#125; ... &#123;% endfor %&#125;', 'A loop, with loop.index and an else part for empty lists', 'for book in books'],
    ['&#123;% if ... %&#125;', 'A condition', 'if book.year &lt; 1900'],
    ['value|filter', 'Changes a value', 'upper, length, default("none"), round(2)'],
    ['&#123;% extends %&#125; and &#123;% block %&#125;', 'One base page, other pages fill its blocks', 'extends "base.html"'],
    ['&#123;% include %&#125;, macros', 'Reuse a part of a page', 'include "nav.html"']])}
{note('Jinja <b>escapes</b> every value by default in .html templates, so a name such as &lt;script&gt; is shown as text and never runs. This stops cross site scripting (XSS). Only mark text as safe with |safe when you made it yourself.', 'warn')}
{scene('a shop with 40 pages', '<p>All 40 pages of a shop share the same header, menu and footer. With template inheritance there is one base.html with a block for the content, and each page only fills that block. Changing the menu means editing one file, not 40.</p>')}
''', kw=['Jinja', 'template', 'render_template', 'extends', 'block', 'for loop', 'filters', 'autoescape', 'XSS', 'template inheritance'])

K.lesson('forms', 'Forms, sessions and flash messages', f'''
{run('forms_session')}
{steps('How the login works', [
    'GET /login shows the form. The browser sends it back as POST /login with the fields in the body.',
    'The view reads request.form, checks the password and stores the user name in <b>session</b>.',
    'Flask puts the session into a cookie, signed with app.secret_key. The user can read it but cannot change it, because the signature would not match.',
    'The view answers with a <b>redirect</b> (Post, Redirect, Get), so pressing refresh does not send the form again.',
    '<b>flash()</b> stores a short message that the next page shows once.'])}
{note('The session cookie is signed, NOT encrypted: the example decodes it and reads the user name. Never put secrets in it, keep secret_key secret and long, and read it from an environment variable.', 'warn')}
{note('Real forms also need protection against cross site request forgery (CSRF), so another website cannot post forms as your user. The extension Flask-WTF adds a hidden token to every form and checks it.', 'exam')}
''', kw=['form', 'POST', 'session', 'secret_key', 'signed cookie', 'flash', 'redirect', 'Post Redirect Get', 'CSRF', 'Flask-WTF'])

K.lesson('api', 'A JSON API in Flask', f'''
{run('json_api')}
{table(['Request', 'View', 'Success', 'Errors'], [
    ['GET /api/books', 'list_books', '200 and a JSON list', ''],
    ['GET /api/books/7', 'get_book', '200 and the book', '404 with a JSON error'],
    ['POST /api/books', 'create_book', '201, the book and Location', '422 for bad data'],
    ['DELETE /api/books/1', 'delete_book', '204 with an empty body', '404']])}
{note('@app.get, @app.post, @app.put, @app.patch and @app.delete are short forms of @app.route with one method. They make an API easier to read.', 'tip')}
{note('A global dict like BOOKS is fine for learning, but it is lost when the server restarts, and each Gunicorn worker process has its own copy. Real apps keep data in a database, as the next chapter shows.', 'warn')}
''', kw=['JSON API', 'REST', '@app.get', '@app.post', 'status codes', '201', '204', '404', '422', 'validation', 'Location header'])

K.lesson('running', 'Running a Flask app for real', f'''
{local('real_server', 'It starts a real web server on your computer and calls it with requests. Install both with <code>pip install flask requests</code>.')}
{steps('From one file to a running site', [
    'Make a virtual environment and install Flask: <code>python3 -m venv .venv</code>, activate it, then <code>pip install flask</code>.',
    'Save the app as app.py and start the development server with <code>flask --app app run --debug</code>. Open http://127.0.0.1:5000 in a browser.',
    '<b>--debug</b> reloads the code when you save a file and shows an interactive error page. Never use it on a public server: the error page can run Python code.',
    'In production run the app with a real WSGI server such as <code>gunicorn -w 4 "app:app"</code>, behind a web server such as nginx that handles HTTPS.',
    'Keep settings such as SECRET_KEY and the database address in environment variables, not in the code.'])}
''', kw=['flask run', 'debug mode', 'virtual environment', 'Werkzeug', 'Gunicorn', 'nginx', 'WSGI server', 'production', 'environment variables'])

K.lesson('maths', 'The maths: workers, time and limits', f'''
{fxs(fx('Requests in progress (Little&#39;s law)', 'L = &lambda; &times; W', '120 requests/s, 0.2 s each: 24 requests at the same moment, so at least 24 workers or threads.', key=True),
     fx('Gunicorn starting point', 'workers = 2 &times; CPU cores + 1', '4 cores: 9 worker processes.'),
     fx('Throughput of sync workers', 'requests/s &le; workers / time per request', '9 workers, 50 ms each: 9 / 0.05 = 180 requests/s.', key=True),
     fx('Python time limit with threads (GIL)', 'requests/s &le; 1 / CPU time per request, per process', '10 ms of Python per request: at most 100 requests/s for one process, however many threads.'),
     fx('Cookie size', 'base64 makes data 4 / 3 as big', 'A 4,096 byte cookie holds about 3,072 bytes of session data.'),
     fx('Error rate', 'rate = errors / requests &times; 100 %', '30 errors out of 600 requests: 5 %.'))}
{steps('Worked example: how many workers?', [
    'A page needs 10 ms of Python and 40 ms of waiting for the database: 50 ms in total.',
    'You expect 300 requests per second at the busiest time.',
    'Little&#39;s law: 300 &times; 0.05 = 15 requests are in progress at once, so you need at least 15 workers or threads.',
    'CPU limit: each request needs 10 ms of Python, so one process can do at most 100 per second. You need at least 3 processes, for example 4 workers with 4 threads each.',
    eq('workers &times; threads &ge; &lambda; &times; W, and processes &ge; &lambda; &times; CPU time')])}
''', kw=['Little law', 'workers', 'Gunicorn', 'throughput', 'GIL', 'cookie size', 'error rate', 'capacity planning'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Write routes that return text, read the query string, and render a template with a loop.</p>',
    '<p>Handle forms and sessions with redirects and flash messages, build a JSON API with the right status codes, and test it with the test client.</p>',
    '<p>Use template inheritance, error handlers and hooks, and run the app with Gunicorn, configured by environment variables.</p>',
    '<p>Understand WSGI, the application and request contexts, signed cookies and CSRF, and size a deployment with Little&#39;s law.</p>')}
{grow('Make pages and simple APIs.', 'Handle forms, sessions and errors.', 'Deploy and scale safely.')}
{deep('What WSGI is', '<p>WSGI (PEP 3333) is the agreement between Python web servers and frameworks. The server calls app(environ, start_response): environ is a dict with the request, and start_response receives the status and headers. A Flask app is such a callable. That is why the same Flask app runs on Werkzeug, Gunicorn, uWSGI or Waitress without changes. ASGI is the async version that FastAPI and Django channels use.</p>')}
''', kw=['beginner', 'expert', 'WSGI', 'PEP 3333', 'ASGI', 'application context', 'request context'])

lc(434, 'Number of Segments in a String', 'number-of-segments-in-a-string', 'e', 'str.split() with no argument', 'Like counting the words a user typed into a search box. split() with no argument skips any amount of spaces, so empty parts never appear.', r'''
def count_segments(s):
    return len(s.split())
''', [('count_segments("Hello, my name is John")', 5), ('count_segments("Hello")', 1), ('count_segments("   ")', 0)])
lc(1662, 'Check If Two String Arrays are Equivalent', 'check-if-two-string-arrays-are-equivalent', 'e', 'Join and compare', 'A page built from template parts must give the same text however it was cut. Join both lists and compare the results.', r'''
def array_strings_are_equal(word1, word2):
    return "".join(word1) == "".join(word2)
''', [('array_strings_are_equal(["ab", "c"], ["a", "bc"])', True), ('array_strings_are_equal(["a", "cb"], ["ab", "c"])', False), ('array_strings_are_equal(["abc", "d", "defg"], ["abcddefg"])', True)])
lc(1544, 'Make The String Great', 'make-the-string-great', 'e', 'A stack of letters', 'Cleaning user input with a stack. Push each letter, but pop instead when it is the same letter in the other case as the top.', r'''
def make_good(s):
    stack = []
    for ch in s:
        if stack and stack[-1] != ch and stack[-1].lower() == ch.lower():
            stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)
''', [('make_good("leEeetcode")', 'leetcode'), ('make_good("abBAcC")', ''), ('make_good("s")', 's')])
lc(2696, 'Minimum String Length After Removing Substrings', 'minimum-string-length-after-removing-substrings', 'e', 'A stack removes pairs as they appear', 'Removing "AB" and "CD" again and again is the same as a stack that pops when the new letter completes a pair with the top.', r'''
def min_length(s):
    stack = []
    for ch in s:
        if stack and stack[-1] + ch in ("AB", "CD"):
            stack.pop()
        else:
            stack.append(ch)
    return len(stack)
''', [('min_length("ABFCACDB")', 2), ('min_length("ACBBD")', 5)])
lc(648, 'Replace Words', 'replace-words', 'm', 'Check the shortest roots first', 'Like a router that finds the shortest registered prefix of a path. Put the roots in a set and try prefixes from short to long.', r'''
def replace_words(dictionary, sentence):
    roots = set(dictionary)
    result = []
    for word in sentence.split():
        replacement = word
        for end in range(1, len(word) + 1):
            if word[:end] in roots:
                replacement = word[:end]
                break
        result.append(replacement)
    return " ".join(result)
''', [('replace_words(["cat", "bat", "rat"], "the cattle was rattled by the battery")', 'the cat was rat by the bat'), ('replace_words(["a", "b", "c"], "aadsfasf absbs bbab cadsfafs")', 'a a b c')])
lc(1209, 'Remove All Adjacent Duplicates in String II', 'remove-all-adjacent-duplicates-in-string-ii', 'm', 'A stack of [letter, count]', 'Keep each letter with how many times it repeats on top of the stack. When the count reaches k, pop the whole group.', r'''
def remove_duplicates(s, k):
    stack = []
    for ch in s:
        if stack and stack[-1][0] == ch:
            stack[-1][1] += 1
            if stack[-1][1] == k:
                stack.pop()
        else:
            stack.append([ch, 1])
    return "".join(ch * count for ch, count in stack)
''', [('remove_duplicates("abcd", 2)', 'abcd'), ('remove_duplicates("deeedbbcccbdaa", 3)', 'aa'), ('remove_duplicates("pbbcggttciiippooaais", 2)', 'ps')])
lc(820, 'Short Encoding of Words', 'short-encoding-of-words', 'm', 'Drop words that are endings of other words', 'A word that is the end of another word needs no space of its own. Remove every ending of every word from a set, then add len(word) + 1 for each word that is left.', r'''
def minimum_length_encoding(words):
    keep = set(words)
    for word in words:
        for start in range(1, len(word)):
            keep.discard(word[start:])
    return sum(len(word) + 1 for word in keep)
''', [('minimum_length_encoding(["time", "me", "bell"])', 10), ('minimum_length_encoding(["t"])', 2)])
lc(916, 'Word Subsets', 'word-subsets', 'm', 'Merge the needs into one Counter', 'A word is universal when it has every letter of every word in words2, as often as needed. Merge words2 into one Counter of the largest counts, then check each word once.', r'''
from collections import Counter


def word_subsets(words1, words2):
    need = Counter()
    for word in words2:
        for ch, count in Counter(word).items():
            need[ch] = max(need[ch], count)
    result = []
    for word in words1:
        have = Counter(word)
        if all(have[ch] >= count for ch, count in need.items()):
            result.append(word)
    return result
''', [('word_subsets(["amazon", "apple", "facebook", "google", "leetcode"], ["e", "o"])', ['facebook', 'google', 'leetcode']), ('word_subsets(["amazon", "apple", "facebook", "google", "leetcode"], ["l", "e"])', ['apple', 'google', 'leetcode'])])
lc(30, 'Substring with Concatenation of All Words', 'substring-with-concatenation-of-all-words', 'h', 'Cut each window into words and compare Counters', 'Find every place where all the words appear joined in any order, like spotting a set of template parts in a page. Each window has a fixed length, so cut it into word sized pieces and compare counts.', r'''
from collections import Counter


def find_substring(s, words):
    size = len(words[0])
    total = size * len(words)
    need = Counter(words)
    starts = []
    for start in range(len(s) - total + 1):
        pieces = [s[start + i * size:start + (i + 1) * size] for i in range(len(words))]
        if Counter(pieces) == need:
            starts.append(start)
    return starts
''', [('find_substring("barfoothefoobarman", ["foo", "bar"])', [0, 9]), ('find_substring("wordgoodgoodgoodbestword", ["word", "good", "best", "word"])', []), ('find_substring("barfoofoobarthefoobarman", ["bar", "foo", "the"])', [6, 9, 12])])
lc(224, 'Basic Calculator', 'basic-calculator', 'h', 'A stack of (result, sign) for each bracket', 'Templates and config files evaluate small expressions. Walk the text, build numbers digit by digit, and push the result so far when a bracket opens.', r'''
def calculate(s):
    result = 0
    number = 0
    sign = 1
    stack = []
    for ch in s:
        if ch.isdigit():
            number = number * 10 + int(ch)
        elif ch in "+-":
            result += sign * number
            number = 0
            sign = 1 if ch == "+" else -1
        elif ch == "(":
            stack.append((result, sign))
            result = 0
            sign = 1
        elif ch == ")":
            result += sign * number
            number = 0
            before, outer_sign = stack.pop()
            result = before + outer_sign * result
    return result + sign * number
''', [('calculate("1 + 1")', 2), ('calculate(" 2-1 + 2 ")', 3), ('calculate("(1+(4+5+2)-3)+(6+8)")', 23), ('calculate("-(2+3)")', -5)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>A web framework is mostly text work: splitting paths into parts, matching prefixes, cleaning input with a stack, finding template parts and evaluating small expressions. These problems practise exactly that.</p>'), kw=['LeetCode', 'strings', 'stack', 'trie', 'parsing', 'expression', 'template expansion'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Flask maps URLs to view functions with @app.route. Converters such as &lt;int:id&gt; check and convert parts of the path. url_for builds links.',
    'request gives args, form, get_json(), files, headers and cookies. A view returns a str, a dict or list (JSON), a (body, status) pair, redirect() or abort().',
    'Jinja templates print values with escaping, loop, test conditions, and share a base page with extends and block.',
    'session is a signed cookie: readable, not changeable. Use Post, Redirect, Get after forms and flash() for one time messages.',
    'Test with app.test_client(). Develop with flask run --debug, deploy with Gunicorn and keep secrets in environment variables.'],
    'Next: real Flask apps with blueprints, a database, logins and tests.')}
{files('Three tasks: write the URL matching that Flask does, build a small notes API and test it with the test client, and write a tiny template engine with filters and escaping.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does @app.route("/hello") do?', ['Starts the server', 'Connects the URL /hello to the function below it', 'Makes a template', 'Sends a request'], 1, 'A decorator on a view.', 'Flask stores the rule in app.url_map.')
K.quiz('e', 'A view returns {"ok": True}. What does Flask send?', ['An error', 'A JSON response with status 200', 'The text "{\'ok\': True}"', 'Nothing'], 1, 'dicts become JSON.', 'Lists become JSON too since Flask 2.2.')
K.quiz('e', 'Where are the fields of an HTML form?', ['request.args', 'request.form', 'request.json', 'request.cookies'], 1, 'Form data.', 'request.args holds the query string of the URL.')
K.quiz('m', 'What does /add/2/x give for the rule /add/&lt;int:a&gt;/&lt;int:b&gt;?', ['500', '404', 'It calls add with b="x"', '400'], 1, 'The converter does not match.', 'No rule matches, so Flask answers 404.')
K.quiz('m', 'A route has no methods= argument. What happens with a POST to it?', ['It works', '405 Method Not Allowed', '404', '500'], 1, 'GET only by default.', 'Add methods=["GET", "POST"] or use @app.post.')
K.quiz('m', 'Why use url_for("hello", name="Bob") instead of writing "/hello/Bob"?', ['It is faster', 'Links keep working when the URL rule changes, and special characters are escaped', 'It is required by HTTP', 'It adds a session'], 1, 'One place for each URL.', 'Templates use it too: &#123;&#123; url_for("home") &#125;&#125;.')
K.quiz('m', 'What does Jinja print for &#123;&#123; name &#125;&#125; when name is "&lt;b&gt;Ann"?', ['Ann in bold', 'The text &lt;b&gt;Ann, with the brackets escaped', 'Nothing', 'An error'], 1, 'Autoescape.', 'This protects pages against cross site scripting.')
K.quiz('m', 'Can a user read the Flask session cookie?', ['No, it is encrypted', 'Yes, it is only signed. They cannot change it without the secret key', 'Only in Chrome', 'Only with the password'], 1, 'Signed, not encrypted.', 'Never store secrets in the session.')
K.quiz('m', 'Why redirect after a successful form POST?', ['Redirects are faster', 'So a refresh repeats a harmless GET instead of sending the form again', 'Flask requires it', 'To clear the cookies'], 1, 'Post, Redirect, Get.', 'Otherwise the browser asks to resend the form data.')
K.quiz('h', 'Why must flask run --debug never be used on a public server?', ['It is slow', 'The debugger page lets a visitor run Python code on the server', 'It disables templates', 'It logs too much'], 1, 'Interactive debugger.', 'Use Gunicorn or another WSGI server in production.')
K.quiz('h', 'Two Gunicorn workers keep books in a global dict. A user adds a book and reloads. Why may it be missing?', ['Flask deletes it', 'Each worker is a separate process with its own dict', 'The browser caches it', 'JSON lost it'], 1, 'Processes do not share memory.', 'Keep shared data in a database or a cache such as Redis.')
K.quiz('x', 'In the style of a Berkeley CS 162 exam: each request needs 10 ms of Python (holding the GIL) and 40 ms of database waiting. What is the most requests per second one process with many threads can do?', ['20', '100', '25', 'No limit'], 1, 'Only the Python part is serial.', 'Threads overlap the 40 ms of waiting, but the 10 ms of Python run one at a time: 1 / 0.01 = 100.')
K.quiz('x', 'In the style of an MIT 6.858 security exam: a page prints the search words with &#123;&#123; q|safe &#125;&#125;. What is the attack?', ['SQL injection', 'Reflected XSS: a link with q=&lt;script&gt;... runs JavaScript in the victim&#39;s browser', 'CSRF', 'None, safe means safe'], 1, '|safe turns escaping off.', 'Remove |safe and let Jinja escape the value.')

K.calc('e', 'Which port does flask run use by default?', '5000', 'Look at the address it prints.', ['flask run prints the address.', 'It is http://127.0.0.1:5000.', eq('5000')], check=5000)
K.calc('e', 'A Jinja loop runs over 12 books. What is loop.index on the last one?', '12', 'loop.index starts at 1.', ['loop.index counts from 1.', 'loop.index0 would count from 0.', eq('12')], check=12)
K.calc('e', '30 of 600 requests ended with an error. What is the error rate in percent?', '5', 'errors / requests &times; 100.', ['30 / 600 = 0.05.', 'Times 100.', eq('5 %')], check=30 / 600 * 100)
K.calc('m', 'A server has 4 CPU cores. How many Gunicorn workers does the usual rule suggest?', '9', '2 &times; cores + 1.', ['2 &times; 4 = 8.', '8 + 1.', eq('9')], check=2 * 4 + 1)
K.calc('m', '9 sync workers, each request takes 50 ms. How many requests per second at most?', '180', 'workers / time.', ['One worker: 1 / 0.05 = 20 per second.', '9 workers: 9 &times; 20.', eq('180')], check=9 / 0.05)
K.calc('m', '120 requests per second, each takes 0.2 s. How many are in progress at once?', '24', 'Little&#39;s law.', ['L = &lambda; &times; W.', '120 &times; 0.2.', eq('24')], check=120 * 0.2)
K.calc('m', 'Browsers keep cookies up to about 4,096 bytes. Base64 makes data 4 / 3 as big. About how many bytes of session data fit?', '3072', 'Divide by 4 / 3.', ['4,096 &times; 3 = 12,288.', '12,288 / 4.', eq('3,072 bytes')], check=4096 * 3 // 4)
K.calc('m', 'A view needs 50 ms. Page views come at 300 per second. How many requests are in progress at once?', '15', 'L = &lambda; &times; W.', ['W = 0.05 s.', '300 &times; 0.05.', eq('15')], check=300 * 0.05)
K.calc('h', 'A template takes 20 ms to compile and 1 ms to render. How many ms does caching the compiled template save over 1,000 renders?', '19980', 'Without a cache it compiles every time.', ['Without: 1000 &times; 21 = 21,000 ms.', 'With: 20 + 1000 &times; 1 = 1,020 ms.', eq('19,980 ms saved')], check=1000 * 21 - (20 + 1000 * 1))
K.calc('x', 'In the style of a Berkeley CS 162 exam: each request has 10 ms of Python and 40 ms of waiting. How many processes are needed for 350 requests per second?', '4', 'Each process does at most 1 / 0.01 requests per second.', ['One process: at most 100 per second.', '350 / 100 = 3.5.', eq('round up: 4 processes')], check=-(-350 // 100))

K.assign('router', 'e', 'Match URLs the way Flask does',
         '<p>Write <code>match(pattern, path)</code>. A pattern such as "/users/&lt;int:uid&gt;/posts/&lt;slug&gt;" has fixed parts and variable parts in angle brackets. Return a dict of the variable parts when the path fits (int: parts must be digits and become int), or None when it does not fit. Then write <code>route(routes, path)</code>: routes is a list of (pattern, endpoint) pairs. Return [endpoint, params] for the first pattern that fits, or ["404", &#123;&#125;]. Careful: a pattern with no variables gives an empty dict, which still means a match.</p>',
         '''
def match(pattern, path):
    if pattern == path:
        return {}
    return None


def route(routes, path):
    for pattern, endpoint in routes:
        params = match(pattern, path)
        if params:
            return [endpoint, params]
    return ["404", {}]


ROUTES = [("/", "home"), ("/books/<int:book_id>", "book"), ("/books/new", "new_book"), ("/users/<name>/books", "user_books")]
''', [('match("/books/<book_id>", "/books/42")', {'book_id': '42'}), ('match("/users/<int:uid>/posts/<slug>", "/users/7/posts/hello-world")', {'uid': 7, 'slug': 'hello-world'}), ('match("/users/<int:uid>", "/users/abc")', None), ('match("/books/<book_id>", "/books/42/reviews")', None), ('route(ROUTES, "/")', ['home', {}]), ('route(ROUTES, "/books/9")', ['book', {'book_id': 9}]), ('route(ROUTES, "/books/new")', ['new_book', {}]), ('route(ROUTES, "/users/ann/books")', ['user_books', {'name': 'ann'}]), ('route(ROUTES, "/cart")', ['404', {}])],
         '''
def match(pattern, path):
    pattern_parts = pattern.strip("/").split("/")
    path_parts = path.strip("/").split("/")
    if len(pattern_parts) != len(path_parts):
        return None
    params = {}
    for want, got in zip(pattern_parts, path_parts):
        if want.startswith("<") and want.endswith(">"):
            inside = want[1:-1]
            if inside.startswith("int:"):
                if not got.isdigit():
                    return None
                params[inside[4:]] = int(got)
            else:
                if got == "":
                    return None
                params[inside] = got
        elif want != got:
            return None
    return params


def route(routes, path):
    for pattern, endpoint in routes:
        params = match(pattern, path)
        if params is not None:
            return [endpoint, params]
    return ["404", {}]


ROUTES = [("/", "home"), ("/books/<int:book_id>", "book"), ("/books/new", "new_book"), ("/users/<name>/books", "user_books")]
''', 'Split both on "/" and compare part by part: the counts must be equal, fixed parts must be equal, and variable parts go into the dict. In route, test "is not None", because an empty dict is a match too.', '<p>Werkzeug, the library under Flask, turns each rule into a regular expression and also sorts the rules so that fixed parts win over variables. That is why /books/new would work in Flask even if it came after /books/&lt;name&gt;.</p>')
K.assign('notes', 'm', 'Build and test a small notes API',
         '<p>Write <code>create_app()</code> that returns a Flask app with a notes API. GET /api/notes gives the list of notes. POST /api/notes with &#123;"text": ...&#125; adds a note &#123;"id", "text", "done": false&#125; with the text stripped, answers 201, and answers 422 with &#123;"error": "text is required"&#125; for empty text. PATCH /api/notes/&lt;id&gt; with &#123;"done": true&#125; changes done and returns the note, 404 with &#123;"error": "not found"&#125; for an unknown id, and 422 with &#123;"error": "done must be true or false"&#125; when done is not a bool. Each app starts empty with ids from 1. run_steps() sends requests with the test client.</p>',
         '''
from flask import Flask, request


def create_app():
    app = Flask(__name__)
    notes = []

    @app.get("/api/notes")
    def list_notes():
        return notes

    return app


def run_steps(steps):
    """steps: a list of (method, path, json body). Returns [status, json] for each answer."""
    client = create_app().test_client()
    results = []
    for method, path, body in steps:
        r = client.open(path, method=method, json=body)
        results.append([r.status_code, r.get_json(silent=True)])
    return results
''', [('run_steps([("GET", "/api/notes", None)])', [[200, []]]), ('run_steps([("POST", "/api/notes", {"text": " buy milk "}), ("GET", "/api/notes", None)])', [[201, {'id': 1, 'text': 'buy milk', 'done': False}], [200, [{'id': 1, 'text': 'buy milk', 'done': False}]]]), ('run_steps([("POST", "/api/notes", {"text": "  "})])', [[422, {'error': 'text is required'}]]), ('run_steps([("POST", "/api/notes", {"text": "a"}), ("PATCH", "/api/notes/1", {"done": True})])', [[201, {'id': 1, 'text': 'a', 'done': False}], [200, {'id': 1, 'text': 'a', 'done': True}]]), ('run_steps([("PATCH", "/api/notes/9", {"done": True})])', [[404, {'error': 'not found'}]]), ('run_steps([("POST", "/api/notes", {"text": "a"}), ("PATCH", "/api/notes/1", {"done": "yes"})])', [[201, {'id': 1, 'text': 'a', 'done': False}], [422, {'error': 'done must be true or false'}]]), ('run_steps([("DELETE", "/api/notes", None)])', [[405, None]])],
         '''
from flask import Flask, request


def create_app():
    app = Flask(__name__)
    notes = {}
    counter = {"next": 1}

    @app.get("/api/notes")
    def list_notes():
        return list(notes.values())

    @app.post("/api/notes")
    def add_note():
        data = request.get_json(silent=True) or {}
        text = str(data.get("text", "")).strip()
        if not text:
            return {"error": "text is required"}, 422
        note = {"id": counter["next"], "text": text, "done": False}
        notes[note["id"]] = note
        counter["next"] += 1
        return note, 201

    @app.patch("/api/notes/<int:note_id>")
    def change_note(note_id):
        if note_id not in notes:
            return {"error": "not found"}, 404
        data = request.get_json(silent=True) or {}
        if "done" in data:
            if not isinstance(data["done"], bool):
                return {"error": "done must be true or false"}, 422
            notes[note_id]["done"] = data["done"]
        return notes[note_id]

    return app


def run_steps(steps):
    """steps: a list of (method, path, json body). Returns [status, json] for each answer."""
    client = create_app().test_client()
    results = []
    for method, path, body in steps:
        r = client.open(path, method=method, json=body)
        results.append([r.status_code, r.get_json(silent=True)])
    return results
''', 'Keep the notes in a dict by id inside create_app, so every app starts empty. Use request.get_json(silent=True) or &#123;&#125; so bad JSON does not crash, and return (body, status) pairs for the errors.', '<p>This is the app factory pattern from the next chapter: create_app() builds a fresh app, which makes every test start from a clean state. The test client checks the whole API in milliseconds, with no browser and no server.</p>')
K.assign('template', 'h', 'Write a tiny template engine',
         '<p>Write <code>render(template, context)</code> that replaces every &#123;&#123; ... &#125;&#125; in the template. Inside the braces there is a name, maybe with dots for nested dicts ("user.city"), and maybe filters after | ("name|upper", "books|length"). Spaces inside the braces do not matter. A missing name gives "". Supported filters: upper, lower, title and length, and any other filter raises ValueError. Like Jinja, escape the final text with html.escape, so a &lt; in a value becomes <code>&amp;lt;</code>.</p>',
         '''
def render(template, context):
    result = template
    for name, value in context.items():
        result = result.replace("{{ " + name + " }}", str(value))
    return result


def render_error(template):
    try:
        render(template, {"x": "hi"})
    except ValueError:
        return "ValueError"
    return "no error"
''', [('render("Hello {{ name }}!", {"name": "Ann"})', 'Hello Ann!'), ('render("{{name}} has {{ books|length }} books", {"name": "Ann", "books": ["a", "b"]})', 'Ann has 2 books'), ('render("{{ user.city|upper }} / {{ user.zip }}", {"user": {"city": "Pune", "zip": 411001}})', 'PUNE / 411001'), ('render("Hi {{ who }}", {"who": "<b>Bob</b>"})', 'Hi &lt;b&gt;Bob&lt;/b&gt;'), ('render("[{{ missing }}] [{{ user.age }}]", {"user": {}})', '[] []'), ('render("{{ title|lower|title }}", {"title": "the HOBBIT"})', 'The Hobbit'), ('render_error("{{ x|shout }}")', 'ValueError')],
         '''
import html
import re

FILTERS = {"upper": str.upper, "lower": str.lower, "title": str.title, "length": len}
PLACEHOLDER = re.compile(r"[{][{](.*?)[}][}]")


def lookup(context, dotted_name):
    value = context
    for part in dotted_name.split("."):
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return ""
    return value


def render(template, context):
    def fill(found):
        pieces = [piece.strip() for piece in found.group(1).split("|")]
        value = lookup(context, pieces[0])
        for name in pieces[1:]:
            if name not in FILTERS:
                raise ValueError(f"unknown filter {name!r}")
            value = FILTERS[name](value)
        return html.escape(str(value))

    return PLACEHOLDER.sub(fill, template)


def render_error(template):
    try:
        render(template, {"x": "hi"})
    except ValueError:
        return "ValueError"
    return "no error"
''', 'A regular expression finds each placeholder, and re.sub calls a function for every match. Split the inside on "|", walk the dotted name through the dicts, apply the filters in order, then escape.', '<p>Jinja does much more (loops, conditions, inheritance), and it compiles each template into Python code once, which makes rendering fast. But the core idea, find the placeholders, look up values, apply filters and escape, is the same.</p>')

K.must('Routes', '@app.route(rule, methods=[...]) or @app.get / post. Converters string, int, float, path, uuid. url_for(endpoint, **values). 404 no match, 405 wrong method.')
K.must('Request', 'request.args.get(name, default, type=int), request.form, request.get_json(silent=True), request.files, headers, cookies.')
K.must('Responses', 'str is HTML, dict or list is JSON, (body, status, headers), redirect(url_for(...)), abort(code), make_response, @app.errorhandler(404).')
K.must('Templates and sessions', 'render_template, &#123;&#123; &#125;&#125; escaped, &#123;% for %&#125;, filters, extends and block. session is a signed cookie, needs secret_key. flash and get_flashed_messages.')
K.must('Run and test', 'app.test_client() for tests. flask --app app run --debug only on your computer. gunicorn -w 4 "app:app" in production.')

T = K.topic(
    slug='py-flask', topic='py-flask', step=(3, 'Flask: small and flexible web apps', 'py-w3', 'Build websites and JSON APIs with Flask: routes, requests, templates, forms and sessions, then app structure, a database, logins, tests and deployment.', 'Intermediate'),
    title='Flask basics: routes, templates, forms and JSON', short='Flask basics', badge='3.1', minutes=100,
    lead='Build your first web app with Flask. Connect URLs to functions, read what the browser sends, make HTML pages with Jinja templates, handle forms and sessions, and write a JSON API that you test without a browser.',
    desc='What Flask is and how it compares with http.server, Django and FastAPI, routes and converters, url_for, the request object, return values and responses, redirects, abort and error handlers, Jinja templates with loops, filters, escaping and inheritance, forms, sessions, flash messages and Post Redirect Get, a JSON API with status codes, the test client, the development server and Gunicorn, and the maths of workers and capacity.',
    summary='Flask routes, request and response, Jinja templates, forms and sessions, a JSON API and running the app.',
    keywords=['Flask', 'route', 'url_for', 'request', 'Jinja', 'template', 'session', 'form', 'JSON API', 'test client'],
    recap='<p>Flask connects URLs to your functions and turns what they return into responses. Templates make the HTML, sessions remember the user, and the test client lets you check it all without a browser.</p>',
    added='2026-11-07', leet=leet_items())
