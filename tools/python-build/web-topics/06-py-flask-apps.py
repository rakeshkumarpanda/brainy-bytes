# Web and APIs 3.2: real Flask apps. Checked against the Flask 3.1 documentation (tutorial "flaskr": application
# factory, blueprints, sqlite3 with g and teardown_appcontext, init-db command, register and login with
# werkzeug.security, login_required, tests with pytest fixtures, deploy to production), Flask configuration handling
# (from_mapping, from_prefixed_env), Flask error handling and logging, and the Werkzeug 3.1 security helpers.
# All programs use the test client and sqlite3, so they run in the page.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, lc, leet, files, grow, leet_items

chapter('py-flask-apps')
K = Kit()

K.code('factory_blueprints', r'''
from flask import Blueprint, Flask, current_app, url_for

# ---------- shop/main.py: the pages for people ----------
main = Blueprint("main", __name__)


@main.route("/")
def home():
    return f"Home of {current_app.config['SHOP_NAME']}"


# ---------- shop/api.py: the JSON API, all under /api ----------
api = Blueprint("api", __name__, url_prefix="/api")


@api.get("/books")
def list_books():
    return [{"id": 1, "title": "Dune"}]


@api.get("/status")
def status():
    return {"testing": current_app.testing, "home": url_for("main.home")}


# ---------- shop/__init__.py: the application factory ----------
def create_app(settings=None):
    app = Flask(__name__)
    app.config.from_mapping(SHOP_NAME="Brainy Books", SECRET_KEY="dev")   # safe defaults
    if settings:
        app.config.update(settings)                                       # tests or production override them
    app.register_blueprint(main)
    app.register_blueprint(api)
    return app


real = create_app()
test = create_app({"TESTING": True, "SHOP_NAME": "Test Shop"})

print(real.test_client().get("/").get_data(as_text=True))
print(test.test_client().get("/").get_data(as_text=True))
print(test.test_client().get("/api/status").get_json())
print(real.test_client().get("/api/books").get_json())
for rule in sorted(real.url_map.iter_rules(), key=str):
    if rule.endpoint != "static":
        print(f"{rule.rule:14} -> {rule.endpoint}")
''')
K.code('database', r'''
import os
import sqlite3
import tempfile

from flask import Flask, current_app, g, request

SCHEMA = """
DROP TABLE IF EXISTS book;
CREATE TABLE book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    year INTEGER NOT NULL
);
"""


def get_db():
    """One connection per request, kept on g and reused inside the same request."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row            # rows work like dicts: row["title"]
        print("  (opened a connection)")
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
        print("  (closed the connection)")


def create_app(db_path):
    app = Flask(__name__)
    app.config["DATABASE"] = db_path

    app.teardown_appcontext(close_db)            # runs after every request, even after an error

    @app.cli.command("init-db")                  # run it with: flask --app shop init-db
    def init_db():
        get_db().executescript(SCHEMA)
        print("  made the empty tables")

    @app.get("/books")
    def list_books():
        rows = get_db().execute("SELECT id, title, year FROM book ORDER BY year").fetchall()
        return [dict(row) for row in rows]

    @app.post("/books")
    def add_book():
        data = request.get_json()
        db = get_db()
        cursor = db.execute("INSERT INTO book (title, year) VALUES (?, ?)",    # ? keeps SQL injection out
                            (data["title"], data["year"]))
        db.commit()
        return {"id": cursor.lastrowid, **data}, 201

    return app


app = create_app(os.path.join(tempfile.mkdtemp(), "shop.sqlite"))
result = app.test_cli_runner().invoke(args=["init-db"])     # the same as typing the command in a terminal
print(result.output, end="")
client = app.test_client()
print(client.post("/books", json={"title": "Dune", "year": 1965}).get_json())
print(client.post("/books", json={"title": "Emma", "year": 1815}).get_json())
print(client.post("/books", json={"title": "x'); DROP TABLE book; --", "year": 2000}).status_code)
print(client.get("/books").get_json())
''', long=True)
K.code('auth', r'''
import functools

from flask import Blueprint, Flask, g, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

USERS = {}                                         # name -> password hash. A real app uses a database table.
auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.post("/register")
def register():
    name, password = request.form["name"], request.form["password"]
    if name in USERS:
        return {"error": f"{name} is already taken"}, 409
    if len(password) < 8:
        return {"error": "use at least 8 characters"}, 422
    USERS[name] = generate_password_hash(password, method="pbkdf2:sha256")
    return {"registered": name}, 201


@auth.post("/login")
def login():
    name, password = request.form["name"], request.form["password"]
    stored = USERS.get(name)
    if stored is None or not check_password_hash(stored, password):
        return {"error": "wrong name or password"}, 401     # do not say which one was wrong
    session.clear()
    session["user"] = name
    return redirect(url_for("orders"))


@auth.before_app_request                           # runs before EVERY request of the app
def load_user():
    g.user = session.get("user")


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("auth.login_page"))
        return view(*args, **kwargs)
    return wrapped


@auth.get("/login")
def login_page():
    return "please log in"


app = Flask(__name__)
app.secret_key = "dev only, read a long random key from the environment in production"
app.register_blueprint(auth)


@app.get("/orders")
@login_required
def orders():
    return {"user": g.user, "orders": [101, 102]}


client = app.test_client()
print(client.post("/auth/register", data={"name": "ann", "password": "short"}).get_json())
print(client.post("/auth/register", data={"name": "ann", "password": "correct horse"}).get_json())
print("stored:", USERS["ann"][:21] + "...", "(never the password itself)")
print(client.get("/orders").headers["Location"])
print(client.post("/auth/login", data={"name": "ann", "password": "wrong pass"}).get_json())
r = client.post("/auth/login", data={"name": "ann", "password": "correct horse"}, follow_redirects=True)
print(r.status_code, r.get_json())
same = generate_password_hash("correct horse", method="pbkdf2:sha256")
print("same password, different hash (salt):", same != USERS["ann"])
''', long=True)
K.code('testing', r'''
from flask import Flask, request


def create_app(settings=None):
    app = Flask(__name__)
    app.config.update(settings or {})
    notes = []

    @app.get("/api/notes")
    def list_notes():
        return notes

    @app.post("/api/notes")
    def add_note():
        text = (request.get_json(silent=True) or {}).get("text", "").strip()
        if not text:
            return {"error": "text is required"}, 422
        notes.append({"id": len(notes) + 1, "text": text})
        return notes[-1], 201

    return app


# ---------- tests/conftest.py: with pytest this is a fixture (see the note below) ----------
def make_client():
    return create_app({"TESTING": True}).test_client()     # a NEW app, so every test starts clean


# ---------- tests/test_notes.py ----------
def test_starts_empty(client):
    assert client.get("/api/notes").get_json() == []


def test_add_note(client):
    r = client.post("/api/notes", json={"text": " milk "})
    assert r.status_code == 201
    assert client.get("/api/notes").get_json() == [{"id": 1, "text": "milk"}]


def test_empty_text_is_rejected(client):
    r = client.post("/api/notes", json={"text": "   "})
    assert r.status_code == 422
    assert r.get_json()["error"] == "text is required"


def test_wrong_on_purpose(client):
    assert client.get("/api/notes").status_code == 201, "a list answers 200, not 201"


# ---------- what pytest does for you: find test_ functions, give each a fresh client ----------
tests = [test_starts_empty, test_add_note, test_empty_text_is_rejected, test_wrong_on_purpose]
passed = 0
for test in tests:
    try:
        test(make_client())
        print("PASSED", test.__name__)
        passed += 1
    except AssertionError as error:
        print("FAILED", test.__name__, "-", error)
print(passed, "passed,", len(tests) - passed, "failed")
''', long=True)
K.code('config_logging', r'''
import logging
import os
import sys

from flask import Flask, request
from werkzeug.exceptions import HTTPException

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

# Normally these come from the shell, a .env file or the hosting service, never from the code
os.environ["FLASK_SHOP_NAME"] = "Env Shop"
os.environ["FLASK_PAGE_SIZE"] = "25"


def create_app():
    app = Flask("shop")
    app.config.from_mapping(SHOP_NAME="Dev Shop", PAGE_SIZE=10, SECRET_KEY="dev")   # defaults
    app.config.from_prefixed_env()           # FLASK_X=value becomes config["X"], and "25" becomes 25

    @app.get("/")
    def home():
        app.logger.info("home page for %s", request.remote_addr)
        return f"{app.config['SHOP_NAME']} shows {app.config['PAGE_SIZE']} books per page"

    @app.get("/boom")
    def boom():
        return str(1 / 0)

    @app.errorhandler(Exception)
    def any_error(error):
        if isinstance(error, HTTPException):  # 404, 405 ... keep their normal answer
            return error
        app.logger.error("crash on %s: %r", request.path, error)
        return {"error": "something went wrong, we are looking at it"}, 500

    return app


app = create_app()
client = app.test_client()
print(client.get("/").get_data(as_text=True))
r = client.get("/boom")
print(r.status_code, r.get_json())
print(client.get("/nope").status_code)
print(type(app.config["PAGE_SIZE"]).__name__, app.config["SECRET_KEY"] == "dev")
''', long=True)

K.lesson('idea', 'From one file to a real app', f'''
{src('Flask 3.1 tutorial (flaskr), Flask configuration, error handling, logging, testing and deployment documentation, and the Werkzeug 3.1 security helpers.')}
{wwh('A <b>real Flask app</b> is the same Flask, organised so it can grow: an <b>application factory</b> that builds the app, <b>blueprints</b> that split it into parts, a <b>database</b>, <b>logins</b> with hashed passwords, <b>tests</b>, <b>configuration</b> from the environment and a way to <b>deploy</b> it.',
     'One app.py with global objects is fine for 50 lines. At 2,000 lines it gets hard to find things, tests change each other&#39;s data, secrets end up in git, and two people cannot work on it at the same time without conflicts.',
     'create_app() builds a fresh app each time, so tests and production get their own settings. Blueprints put each feature in its own file. The database connection lives on g for one request and is closed by teardown. Passwords are stored only as salted hashes. pytest fixtures give every test a clean app and database.')}
{viz('pyflaskapp')}
{versus('Ways to organise a Python web app', ['', 'One app.py file', 'Factory and blueprints', 'Django project'], [
    ['Where code lives', 'Everything in one file', 'A package: __init__.py, auth.py, books.py, db.py', 'Apps with models.py, views.py, urls.py'],
    ['Tests', 'Share one global app', 'Each test builds its own app', 'A test runner with a test database'],
    ['Settings', 'Often written in the code', 'Defaults, then settings, then environment', 'settings.py, often read from the environment'],
    ['Database and login', 'By hand', 'sqlite3 by hand, or Flask-SQLAlchemy and Flask-Login', 'Built in: ORM, migrations, auth, admin'],
    ['Good for', 'Demos', 'Most Flask apps', 'Big apps that need everything']],
    'Use the factory and blueprints for anything you will keep. It costs a few lines and saves a lot when the app grows.')}
''', kw=['application factory', 'create_app', 'blueprint', 'project structure', 'database', 'login', 'testing', 'configuration', 'deployment'])

K.lesson('layout', 'The application factory and blueprints', f'''
{run('factory_blueprints')}
{table(['File or folder', 'Holds'], [
    ['shop/__init__.py', 'create_app(): config, database setup, register_blueprint for each part'],
    ['shop/db.py', 'get_db(), close_db(), the init-db command'],
    ['shop/auth.py', 'Blueprint auth: register, login, logout, login_required'],
    ['shop/books.py', 'Blueprint books: the pages of the shop'],
    ['shop/api.py', 'Blueprint api with url_prefix="/api": the JSON API'],
    ['shop/templates/, shop/static/', 'Jinja templates, CSS, JavaScript and images'],
    ['instance/', 'Files that belong to one installation: the SQLite file, a local config. Not in git'],
    ['tests/conftest.py, tests/test_*.py', 'pytest fixtures and tests'],
    ['pyproject.toml', 'The package name and its dependencies']])}
{note('Inside a blueprint, link with the blueprint name: url_for("api.status") or url_for(".status") for the same blueprint. Use <b>current_app</b> instead of a global app variable, because with a factory there is no global app.', 'exam')}
''', kw=['create_app', 'application factory', 'Blueprint', 'register_blueprint', 'url_prefix', 'current_app', 'project layout', 'instance folder'])

K.lesson('database', 'A database with sqlite3', f'''
{run('database')}
{versus('Ways to use a database in Flask', ['', 'sqlite3 by hand', 'Flask-SQLAlchemy', 'Django ORM'], [
    ['You write', 'SQL text with ? placeholders', 'Python classes, queries as method calls', 'Python classes, queries as method calls'],
    ['Changing tables later', 'Write ALTER TABLE yourself', 'Flask-Migrate (Alembic) makes migration files', 'makemigrations and migrate are built in'],
    ['Other databases', 'Change the code for PostgreSQL', 'Change one URL in the config', 'Change the settings'],
    ['Good for', 'Learning SQL, small apps', 'Most Flask apps that grow', 'Django apps']],
    'Learn it by hand first, as here, so you know what an ORM writes for you. Step 4 shows the Django ORM.')}
{steps('The connection rules in the example', [
    'get_db() opens one connection the first time a request needs it and keeps it on <b>g</b>. g lives for one request only.',
    'sqlite3.Row lets you read row["title"] and turn a row into a dict with dict(row).',
    'Always pass values as ? placeholders. The SQL injection attempt above is stored as harmless text.',
    'Call commit() after changes. teardown_appcontext closes the connection after every request, even after an error.',
    '@app.cli.command adds flask init-db, and app.test_cli_runner() runs it from a test.'])}
''', kw=['sqlite3', 'g', 'teardown_appcontext', 'get_db', 'sqlite3.Row', 'placeholders', 'SQL injection', 'commit', 'cli command', 'Flask-SQLAlchemy', 'migrations'])

K.lesson('auth', 'Users, passwords and login_required', f'''
{run('auth')}
{table(['Rule', 'Why'], [
    ['Store generate_password_hash(...), never the password', 'A stolen database must not reveal passwords'],
    ['Use a slow hash with a salt (scrypt or PBKDF2, Werkzeug picks scrypt by default)', 'Slow makes guessing expensive, the salt makes the same password give different hashes'],
    ['Say "wrong name or password", not which one', 'Attackers cannot test which names exist'],
    ['session.clear() before storing the user', 'No data from before the login survives (session fixation)'],
    ['Set SESSION_COOKIE_SECURE and SESSION_COOKIE_HTTPONLY in production', 'The cookie only travels over HTTPS and JavaScript cannot read it'],
    ['Limit login attempts, for example 5 a minute per user', 'Stops fast guessing']])}
{note('login_required is a normal decorator (Advanced step 2). functools.wraps keeps the view name, which Flask needs, because the endpoint name comes from the function name.', 'tip')}
{note('For bigger apps, Flask-Login manages the logged in user and "remember me", and Flask-WTF adds CSRF tokens to forms. They do the same jobs as the code here, with more cases covered.', 'exam')}
''', kw=['authentication', 'password hashing', 'generate_password_hash', 'check_password_hash', 'salt', 'scrypt', 'PBKDF2', 'login_required', 'session', 'before_app_request', 'Flask-Login'])

K.lesson('testing', 'Testing a Flask app', f'''
{run('testing')}
{note('With pytest the helper becomes a fixture in tests/conftest.py, and pytest passes it to every test that has a parameter called client: <pre>import pytest\nfrom notes import create_app\n\n@pytest.fixture\ndef client():\n    app = create_app(&#123;"TESTING": True&#125;)\n    return app.test_client()</pre> Then run <code>python3 -m pytest -q</code>. A real run of exactly this printed "2 passed in 0.18s".', 'tip')}
{table(['Kind of test', 'Checks', 'Tool'], [
    ['Unit test', 'One function, such as bad_book(data)', 'pytest'],
    ['Route test', 'One URL: status code, JSON, redirects', 'app.test_client()'],
    ['Command test', 'flask init-db and other commands', 'app.test_cli_runner()'],
    ['End to end test', 'A real browser clicking through pages', 'Playwright or Selenium (see those subjects)'],
    ['Coverage', 'Which lines the tests ran', 'coverage run -m pytest, then coverage report']])}
''', kw=['pytest', 'fixture', 'conftest', 'test_client', 'test_cli_runner', 'TESTING', 'assert', 'coverage', 'unit test'])

K.lesson('config', 'Configuration, errors and logging', f'''
{run('config_logging')}
{table(['Source', 'Example', 'Use it for'], [
    ['Defaults in create_app', 'app.config.from_mapping(PAGE_SIZE=10)', 'Values that are safe everywhere'],
    ['Settings passed to create_app', 'create_app(&#123;"TESTING": True&#125;)', 'Tests'],
    ['A file in instance/', 'app.config.from_pyfile("config.py", silent=True)', 'One installation'],
    ['Environment variables', 'FLASK_SECRET_KEY=... with from_prefixed_env()', 'Secrets and production values']])}
{note('Flask turns an exception in a view into a 500 answer. An errorhandler(Exception) can log it and send a friendly message, but must pass HTTPExceptions such as 404 through unchanged, as the example does. Use app.logger, never print, so logs get levels and can go to files or a log service.', 'tip')}
''', kw=['config', 'from_mapping', 'from_prefixed_env', 'environment variables', 'SECRET_KEY', 'errorhandler', 'HTTPException', 'logging', 'app.logger', '500'])

K.lesson('deploy', 'Deploying a Flask app', f'''
{steps('From your computer to a public server', [
    'List the dependencies in pyproject.toml or requirements.txt (pip freeze &gt; requirements.txt).',
    'Never use flask run --debug in public. Run the app with a WSGI server: <code>gunicorn -w 4 -b 0.0.0.0:8000 "shop:create_app()"</code>.',
    'Put nginx (or the hosting platform) in front: it serves HTTPS, static files and passes the rest to Gunicorn.',
    'Set SECRET_KEY, the database URL and other secrets as environment variables on the server.',
    'Use PostgreSQL or MySQL instead of SQLite when many users write at the same time, and run migrations on each release.',
    'Add a health check URL such as /health that returns 200, so the platform can restart the app when it stops answering.'])}
{table(['Way to host', 'You manage', 'Example'], [
    ['A platform (PaaS)', 'Only the code and settings', 'Render, Railway, Fly.io, Google App Engine'],
    ['A container', 'A Dockerfile, the platform runs it', 'Docker image on Cloud Run, AWS ECS, Kubernetes'],
    ['Your own server', 'Everything: Linux, nginx, Gunicorn, updates', 'A virtual machine with systemd']])}
{scene('a small team ships every day', '<p>A team keeps its Flask shop in git. Every push runs the pytest suite in CI (see the Git and CI/CD subject). When the tests pass on the main branch, CI builds a Docker image with Gunicorn inside and the platform swaps it in. SECRET_KEY and DATABASE_URL live in the platform settings, never in the repository.</p>')}
''', kw=['deployment', 'Gunicorn', 'nginx', 'WSGI', 'environment variables', 'Docker', 'PaaS', 'PostgreSQL', 'health check', 'requirements.txt'])

K.lesson('maths', 'The maths: hashing cost, commits and capacity', f'''
{fxs(fx('Guesses per second against a slow hash', 'guesses/s = raw hashes per second / iterations', '10 million SHA-256 per second, 1,000,000 PBKDF2 iterations: 10 guesses per second.', key=True),
     fx('Number of passwords', 'N = (letters in the alphabet)<sup>length</sup>', '8 lower case letters: 26<sup>8</sup> &asymp; 2.09 &times; 10<sup>11</sup>.'),
     fx('Average time to guess', 'time &asymp; N / 2 / guesses per second', '2.09 &times; 10<sup>11</sup> / 2 / 10 per second &asymp; 331 years.', key=True),
     fx('Commits', 'many commits cost n &times; commit time, one transaction costs one', '200 inserts with a 5 ms commit each: 1,000 ms. In one transaction: about 15 ms.'),
     fx('Salt collisions (birthday bound)', 'n &asymp; 1.18 &times; &radic;(number of salts) for a 50 % chance', '32 bit salts: 1.18 &times; 65,536 &asymp; 77,000 users. Werkzeug uses 16 random characters, far more.'),
     fx('Test suite time', 'time = tests &times; time per test', '120 tests at 15 ms: 1.8 s, fast enough to run on every save.'))}
{steps('Worked example: why a fast hash is not enough', [
    'A leaked database stores SHA-256 of each password with no salt. A graphics card computes about 10 billion SHA-256 a second.',
    'All 26<sup>8</sup> &asymp; 2.09 &times; 10<sup>11</sup> lower case passwords of 8 letters take about 21 seconds.',
    'With PBKDF2 and 1,000,000 iterations each guess costs a million hashes: 10,000 guesses a second.',
    'The same search now takes 2.09 &times; 10<sup>11</sup> / 10,000 &asymp; 2.1 &times; 10<sup>7</sup> s, about 242 days, and a salt stops one search from cracking every user at once.',
    eq('slow, salted hashes turn seconds into months')])}
''', kw=['password hashing cost', 'PBKDF2 iterations', 'brute force', 'transactions', 'birthday bound', 'salt', 'test speed'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Split an app into blueprints, use an application factory, and store data with sqlite3 and ? placeholders.</p>',
    '<p>Add register and login with hashed passwords and login_required, and write pytest tests with a fixture for the client.</p>',
    '<p>Configure the app from the environment, log errors properly, and deploy it with Gunicorn behind HTTPS.</p>',
    '<p>Move to an ORM with migrations, add CSRF protection, rate limits and monitoring, and design the app for many workers and a shared database.</p>')}
{grow('Structure the code.', 'Add users and tests.', 'Run it safely in production.')}
{deep('Application context and request context', '<p>current_app and g work only inside an <b>application context</b>, and request and session only inside a <b>request context</b>. Flask pushes both for every request, and the test client does the same. In a script or a test without a request, use with app.app_context(): to get current_app and g.</p>')}
''', kw=['beginner', 'expert', 'application context', 'request context', 'ORM', 'CSRF', 'monitoring'])

PLAY = '''

def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results
'''

lc(595, 'Big Countries', 'big-countries', 'e', 'WHERE with OR', 'A country is big when its area is at least 3,000,000 or its population at least 25,000,000. One WHERE with OR does it.', r'''
import sqlite3


def big_countries(world):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE World (name TEXT, continent TEXT, area INTEGER, population INTEGER, gdp INTEGER)")
    db.executemany("INSERT INTO World VALUES (?, ?, ?, ?, ?)", world)
    rows = db.execute("""
        SELECT name, population, area FROM World
        WHERE area >= 3000000 OR population >= 25000000 ORDER BY name""").fetchall()
    db.close()
    return rows
''', [('big_countries([("Afghanistan", "Asia", 652230, 25500100, 20343000000), ("Albania", "Europe", 28748, 2831741, 12960000000), ("Algeria", "Africa", 2381741, 37100000, 188681000000), ("Andorra", "Europe", 468, 78115, 3712000000), ("Angola", "Africa", 1246700, 20609294, 100990000000)])', [['Afghanistan', 25500100, 652230], ['Algeria', 37100000, 2381741]])])
lc(1757, 'Recyclable and Low Fat Products', 'recyclable-and-low-fat-products', 'e', 'WHERE with AND', 'Both columns must be "Y". The kind of filter a shop page runs for every search.', r'''
import sqlite3


def find_products(products):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Products (product_id INTEGER, low_fats TEXT, recyclable TEXT)")
    db.executemany("INSERT INTO Products VALUES (?, ?, ?)", products)
    rows = db.execute("""
        SELECT product_id FROM Products
        WHERE low_fats = 'Y' AND recyclable = 'Y' ORDER BY product_id""").fetchall()
    db.close()
    return [row[0] for row in rows]
''', [('find_products([(0, "Y", "N"), (1, "Y", "Y"), (2, "N", "Y"), (3, "Y", "Y"), (4, "N", "N")])', [1, 3])])
lc(584, 'Find Customer Referee', 'find-customer-referee', 'e', 'NULL needs IS NULL', 'referee_id != 2 is not true for NULL, because NULL compared with anything is unknown. Add OR referee_id IS NULL.', r'''
import sqlite3


def find_customer_referee(customers):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Customer (id INTEGER, name TEXT, referee_id INTEGER)")
    db.executemany("INSERT INTO Customer VALUES (?, ?, ?)", customers)
    rows = db.execute("""
        SELECT name FROM Customer
        WHERE referee_id != 2 OR referee_id IS NULL ORDER BY id""").fetchall()
    db.close()
    return [row[0] for row in rows]
''', [('find_customer_referee([(1, "Will", None), (2, "Jane", None), (3, "Alex", 2), (4, "Bill", None), (5, "Zack", 1), (6, "Mark", 2)])', ['Will', 'Jane', 'Bill', 'Zack'])])
lc(1148, 'Article Views I', 'article-views-i', 'e', 'DISTINCT with a column compared to another', 'Authors who viewed their own article: author_id = viewer_id. DISTINCT removes repeats.', r'''
import sqlite3


def own_article_views(views):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Views (article_id INTEGER, author_id INTEGER, viewer_id INTEGER, view_date TEXT)")
    db.executemany("INSERT INTO Views VALUES (?, ?, ?, ?)", views)
    rows = db.execute("SELECT DISTINCT author_id FROM Views WHERE author_id = viewer_id ORDER BY author_id").fetchall()
    db.close()
    return [row[0] for row in rows]
''', [('own_article_views([(1, 3, 5, "2019-08-01"), (1, 3, 6, "2019-08-02"), (2, 7, 7, "2019-08-01"), (2, 7, 6, "2019-08-02"), (4, 7, 1, "2019-07-22"), (3, 4, 4, "2019-07-21"), (3, 4, 4, "2019-07-21")])', [4, 7])])
lc(570, 'Managers with at Least 5 Direct Reports', 'managers-with-at-least-5-direct-reports', 'm', 'GROUP BY with HAVING, then join back', 'Count the people per managerId, keep the ones with 5 or more, and join with the table again to get the names.', r'''
import sqlite3


def managers_with_five(employees):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Employee (id INTEGER, name TEXT, department TEXT, managerId INTEGER)")
    db.executemany("INSERT INTO Employee VALUES (?, ?, ?, ?)", employees)
    rows = db.execute("""
        SELECT boss.name FROM Employee boss
        JOIN (SELECT managerId FROM Employee GROUP BY managerId HAVING COUNT(*) >= 5) big
          ON boss.id = big.managerId
        ORDER BY boss.name""").fetchall()
    db.close()
    return [row[0] for row in rows]
''', [('managers_with_five([(101, "John", "A", None), (102, "Dan", "A", 101), (103, "James", "A", 101), (104, "Amy", "A", 101), (105, "Anne", "A", 101), (106, "Ron", "B", 101)])', ['John'])])
lc(1934, 'Confirmation Rate', 'confirmation-rate', 'm', 'LEFT JOIN, AVG of a CASE, IFNULL', 'Every user who signed up must appear, even with no confirmations, so use a LEFT JOIN. The rate is the average of 1 for confirmed and 0 otherwise.', r'''
import sqlite3


def confirmation_rate(signups, confirmations):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Signups (user_id INTEGER, time_stamp TEXT)")
    db.execute("CREATE TABLE Confirmations (user_id INTEGER, time_stamp TEXT, action TEXT)")
    db.executemany("INSERT INTO Signups VALUES (?, ?)", signups)
    db.executemany("INSERT INTO Confirmations VALUES (?, ?, ?)", confirmations)
    rows = db.execute("""
        SELECT s.user_id,
               ROUND(IFNULL(AVG(CASE WHEN c.action = 'confirmed' THEN 1.0 ELSE 0.0 END), 0), 2)
        FROM Signups s LEFT JOIN Confirmations c ON s.user_id = c.user_id
        GROUP BY s.user_id ORDER BY s.user_id""").fetchall()
    db.close()
    return rows
''', [('confirmation_rate([(3, "2020-03-21 10:16:13"), (7, "2022-01-04 13:57:59"), (2, "2020-07-29 23:09:44"), (6, "2020-12-09 10:39:37")], [(3, "2021-01-06 03:30:46", "timeout"), (3, "2021-07-14 14:00:00", "timeout"), (7, "2021-06-12 11:57:29", "confirmed"), (7, "2021-06-13 12:58:28", "confirmed"), (7, "2021-06-14 13:59:27", "confirmed"), (2, "2021-01-22 00:00:00", "confirmed"), (2, "2021-02-28 23:59:59", "timeout")])', [[2, 0.5], [3, 0.0], [6, 0.0], [7, 1.0]])])
lc(180, 'Consecutive Numbers', 'consecutive-numbers', 'm', 'Join the table with itself twice', 'Pair each row with the next two ids. If all three have the same number, that number appears at least three times in a row.', r'''
import sqlite3


def consecutive_numbers(logs):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Logs (id INTEGER, num INTEGER)")
    db.executemany("INSERT INTO Logs VALUES (?, ?)", logs)
    rows = db.execute("""
        SELECT DISTINCT a.num FROM Logs a
        JOIN Logs b ON b.id = a.id + 1 AND b.num = a.num
        JOIN Logs c ON c.id = a.id + 2 AND c.num = a.num
        ORDER BY a.num""").fetchall()
    db.close()
    return [row[0] for row in rows]
''', [('consecutive_numbers([(1, 1), (2, 1), (3, 1), (4, 2), (5, 1), (6, 2), (7, 2)])', [1]), ('consecutive_numbers([(1, 3), (2, 3), (3, 4), (4, 4), (5, 4), (6, 3), (7, 3), (8, 3)])', [3, 4])])
lc(550, 'Game Play Analysis IV', 'game-play-analysis-iv', 'm', 'First day per player, then look for the next day', 'Find each player&#39;s first login with MIN, check whether they came back the day after, and divide by the number of players.', r'''
import sqlite3


def came_back_next_day(activity):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Activity (player_id INTEGER, device_id INTEGER, event_date TEXT, games_played INTEGER)")
    db.executemany("INSERT INTO Activity VALUES (?, ?, ?, ?)", activity)
    row = db.execute("""
        WITH first AS (SELECT player_id, MIN(event_date) AS day FROM Activity GROUP BY player_id)
        SELECT ROUND(1.0 * COUNT(a.player_id) / (SELECT COUNT(*) FROM first), 2)
        FROM first f
        LEFT JOIN Activity a ON a.player_id = f.player_id AND a.event_date = DATE(f.day, '+1 day')""").fetchone()
    db.close()
    return row[0]
''', [('came_back_next_day([(1, 2, "2016-03-01", 5), (1, 2, "2016-03-02", 6), (2, 3, "2017-06-25", 1), (3, 1, "2016-03-02", 0), (3, 4, "2018-07-03", 5)])', 0.33)])
lc(601, 'Human Traffic of Stadium', 'human-traffic-of-stadium', 'h', 'Window function: id minus row number groups a run', 'Keep the days with 100 or more people. Within a run of consecutive ids, id minus ROW_NUMBER() stays the same, so it names the run. Keep runs of 3 or more.', r'''
import sqlite3


def busy_days(stadium):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE Stadium (id INTEGER, visit_date TEXT, people INTEGER)")
    db.executemany("INSERT INTO Stadium VALUES (?, ?, ?)", stadium)
    rows = db.execute("""
        WITH busy AS (
            SELECT id, visit_date, people, id - ROW_NUMBER() OVER (ORDER BY id) AS run
            FROM Stadium WHERE people >= 100),
        runs AS (SELECT run FROM busy GROUP BY run HAVING COUNT(*) >= 3)
        SELECT id, visit_date, people FROM busy WHERE run IN (SELECT run FROM runs)
        ORDER BY visit_date""").fetchall()
    db.close()
    return rows
''', [('busy_days([(1, "2017-01-01", 10), (2, "2017-01-02", 109), (3, "2017-01-03", 150), (4, "2017-01-04", 99), (5, "2017-01-05", 145), (6, "2017-01-06", 1455), (7, "2017-01-07", 199), (8, "2017-01-09", 188)])', [[5, '2017-01-05', 145], [6, '2017-01-06', 1455], [7, '2017-01-07', 199], [8, '2017-01-09', 188]])])
lc(432, "All O`one Data Structure", 'all-oone-data-structure', 'h', 'A dict of counts (simple version)', 'Count page views per key and ask for the most and least viewed key. This simple version keeps a dict and uses max and min. The O(1) version keeps a linked list of buckets, one bucket for each count.', r'''
class AllOne:
    def __init__(self):
        self.counts = {}

    def inc(self, key):
        self.counts[key] = self.counts.get(key, 0) + 1

    def dec(self, key):
        self.counts[key] -= 1
        if self.counts[key] == 0:
            del self.counts[key]

    def getMaxKey(self):
        if not self.counts:
            return ""
        return max(self.counts, key=self.counts.get)

    def getMinKey(self):
        if not self.counts:
            return ""
        return min(self.counts, key=self.counts.get)
''' + PLAY, [('play(AllOne, ["AllOne", "inc", "inc", "getMaxKey", "getMinKey", "inc", "getMaxKey", "getMinKey"], [[], ["hello"], ["hello"], [], [], ["leet"], [], []])', [None, None, None, 'hello', 'hello', None, 'hello', 'leet'])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Most Flask apps sit on a database, so these are SQL problems from the LeetCode database set, each solved with Python and an in-memory sqlite3 database: filters, NULL handling, self joins, grouping, rates and window functions. The last one is a counting structure for page views.</p>'), kw=['LeetCode', 'SQL', 'sqlite3', 'NULL', 'GROUP BY', 'self join', 'window functions', 'design'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'create_app() builds a fresh app with layered config. Blueprints split features into files, and current_app replaces a global app.',
    'get_db() keeps one sqlite3 connection on g per request, teardown_appcontext closes it, and values always go in as ? placeholders.',
    'Store only salted slow hashes (generate_password_hash), clear the session at login, and protect views with a login_required decorator.',
    'Test with pytest fixtures that build a new app and client for each test. Run commands with test_cli_runner.',
    'Configure from the environment, log with app.logger, and deploy with Gunicorn behind HTTPS, never with the debug server.'],
    'Next: Django, the framework with everything built in.')}
{files('Three tasks: write a login_required decorator, write safe database helpers with sqlite3, and hash and check passwords with PBKDF2.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does an application factory do?', ['Makes HTML pages', 'Builds and returns a new Flask app each time it is called', 'Starts Gunicorn', 'Creates database tables'], 1, 'create_app().', 'Tests can then build apps with their own settings.')
K.quiz('e', 'What is a Blueprint for?', ['Drawing diagrams', 'Grouping related routes, templates and code into one part of the app', 'Making the app faster', 'Storing passwords'], 1, 'Parts of an app.', 'Each blueprint is registered with app.register_blueprint.')
K.quiz('e', 'How should a password be stored?', ['As plain text', 'As a salted, slow hash', 'Base64 encoded', 'In the session cookie'], 1, 'Never the password itself.', 'Use generate_password_hash and check_password_hash.')
K.quiz('m', 'What is g in Flask?', ['A global that lives for the whole program', 'A place for data that lives for one request, such as the database connection', 'The config', 'The session cookie'], 1, 'One request.', 'Each request gets a new, empty g.')
K.quiz('m', 'Why use ? placeholders in SQL?', ['They are faster to type', 'The values are sent apart from the SQL, so input cannot change the query (no SQL injection)', 'SQLite needs them', 'To save memory'], 1, 'Data stays data.', 'Never build SQL with f-strings and user input.')
K.quiz('m', 'Why does the same password give a different hash each time?', ['A bug', 'A random salt is added before hashing', 'The time is added', 'Hashes are random'], 1, 'Salt.', 'The salt is stored inside the hash string, so check_password_hash can repeat it.')
K.quiz('m', 'What does teardown_appcontext(close_db) do?', ['Deletes the database', 'Calls close_db after every request, even after an error', 'Closes the app', 'Runs only in tests'], 1, 'Clean up.', 'So connections are never left open.')
K.quiz('m', 'Why does each test call create_app again?', ['To make tests slower', 'So every test starts with a clean app and data and tests cannot affect each other', 'pytest requires it', 'To load templates'], 1, 'Isolation.', 'A pytest fixture does this for every test.')
K.quiz('m', 'Why must an errorhandler(Exception) return HTTPExceptions unchanged?', ['It must not', 'Otherwise 404 and 405 errors would turn into 500 answers', 'For speed', 'Because of logging'], 1, 'HTTPException is an Exception too.', 'abort(404) raises an HTTPException.')
K.quiz('h', 'Why should a login error say "wrong name or password" and not "no such user"?', ['It is shorter', 'Attackers could learn which user names exist', 'Browsers need it', 'For translations'], 1, 'User enumeration.', 'Also keep the time the same for both cases where you can.')
K.quiz('h', 'Which command runs a factory app with 4 Gunicorn workers?', ['flask run -w 4', 'gunicorn -w 4 "shop:create_app()"', 'python shop.py --workers 4', 'gunicorn shop.app'], 1, 'Call the factory.', 'Gunicorn can call a factory written as "module:function()".')
K.quiz('x', 'In the style of a Stanford CS 155 exam: a site stores unsalted SHA-256 password hashes. Why is that much worse than salted PBKDF2, even though SHA-256 is secure?', ['It is not worse', 'SHA-256 is fast and unsalted, so attackers test billions of guesses a second against every user at once and can use precomputed tables', 'SHA-256 can be reversed', 'SHA-256 is too long'], 1, 'Speed and sharing.', 'A slow hash makes each guess cost a lot, and a salt forces a separate search for each user.')
K.quiz('x', 'In the style of a CMU 15-445 database exam: why are 200 INSERTs in one transaction much faster in SQLite than 200 separate commits?', ['They are not', 'Each commit waits for the disk to confirm the write (fsync), one transaction waits only once', 'SQLite caches SQL text', 'Indexes are skipped'], 1, 'Durability costs a disk sync.', 'Group writes that belong together into one transaction.')

K.calc('e', 'A graphics card makes 10,000,000 SHA-256 hashes a second. PBKDF2 uses 1,000,000 iterations. How many password guesses per second?', '10', 'Divide by the iterations.', ['Each guess needs 1,000,000 hashes.', '10,000,000 / 1,000,000.', eq('10 guesses per second')], check=10_000_000 // 1_000_000)
K.calc('e', 'Flask keeps a permanent session for 31 days by default. How many seconds is that?', '2678400', 'days &times; 24 &times; 60 &times; 60.', ['One day is 86,400 s.', '31 &times; 86,400.', eq('2,678,400 s')], check=31 * 86400)
K.calc('e', '200 INSERTs, each committed alone, and every commit takes 5 ms. How many ms in total?', '1000', '200 &times; 5.', ['Each commit waits for the disk.', '200 &times; 5.', eq('1,000 ms')], check=200 * 5)
K.calc('m', 'The same 200 INSERTs in one transaction: each insert takes 0.05 ms and the one commit 5 ms. How many ms?', '15', 'Inserts plus one commit.', ['200 &times; 0.05 = 10 ms.', 'Plus 5 ms for the commit.', eq('15 ms')], check=200 * 0.05 + 5, tol=0.01)
K.calc('m', 'How many passwords of exactly 8 lower case letters exist?', '208827064576', '26<sup>8</sup>.', ['26 choices for each place.', '26 &times; 26 &times; ... 8 times.', eq('208,827,064,576')], check=26 ** 8)
K.calc('m', '120 tests take 15 ms each. How many seconds for the whole suite?', '1.8', 'tests &times; time.', ['120 &times; 15 = 1,800 ms.', 'Divide by 1,000.', eq('1.8 s')], check=120 * 15 / 1000, tol=0.01)
K.calc('m', 'The tests ran 450 of 600 lines. What is the line coverage in percent?', '75', 'run / total &times; 100.', ['450 / 600 = 0.75.', 'Times 100.', eq('75 %')], check=450 / 600 * 100)
K.calc('m', '9 Gunicorn workers use 80 MB each. How many MB in total?', '720', 'Each worker is a separate process.', ['Processes do not share this memory.', '9 &times; 80.', eq('720 MB')], check=9 * 80)
K.calc('h', 'At 10 guesses per second, how many years on average to guess one of 26<sup>8</sup> passwords (half the space, 1 year = 31,536,000 s)? Round to a whole number.', '331', 'N / 2 / rate, then into years.', ['26<sup>8</sup> / 2 &asymp; 1.044 &times; 10<sup>11</sup> guesses.', 'Divide by 10 per second: 1.044 &times; 10<sup>10</sup> s.', 'Divide by 31,536,000.', eq('&asymp; 331 years')], check=26 ** 8 / 2 / 10 / 31536000, tol=0.6)
K.calc('x', 'In the style of a Stanford CS 255 exam: salts are random 32 bit numbers. About how many users until there is a 50 % chance that two share a salt? Use 1.1774 &times; &radic;N.', '77163', 'N = 2<sup>32</sup>, &radic;N = 2<sup>16</sup> = 65,536.', ['&radic;(2<sup>32</sup>) = 65,536.', '1.1774 &times; 65,536.', eq('&asymp; 77,163')], check=1.1774 * 2 ** 16, tol=60)

K.assign('loginreq', 'e', 'Write a login_required decorator',
         '<p>In this app, before_request puts the user name from the header X-User into g.user (None when the header is missing). Write the decorator <code>login_required(view)</code>: when g.user is None it returns (&#123;"error": "login required"&#125;, 401) without running the view, otherwise it runs the view with its arguments. Use functools.wraps so the view keeps its name. ask() sends a request and returns [status, json].</p>',
         '''
import functools

from flask import Flask, g, request


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        return view(*args, **kwargs)
    return wrapped


app = Flask(__name__)


@app.before_request
def load_user():
    g.user = request.headers.get("X-User")


@app.get("/profile")
@login_required
def profile():
    return {"user": g.user}


@app.get("/orders/<int:number>")
@login_required
def order(number):
    return {"user": g.user, "order": number}


def ask(path, user=None):
    headers = {"X-User": user} if user else {}
    r = app.test_client().get(path, headers=headers)
    return [r.status_code, r.get_json()]
''', [('ask("/profile", "ann")', [200, {'user': 'ann'}]), ('ask("/profile")', [401, {'error': 'login required'}]), ('ask("/orders/7", "bob")', [200, {'user': 'bob', 'order': 7}]), ('ask("/orders/7")', [401, {'error': 'login required'}]), ('[profile.__name__, order.__name__]', ['profile', 'order'])],
         '''
import functools

from flask import Flask, g, request


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return {"error": "login required"}, 401
        return view(*args, **kwargs)
    return wrapped


app = Flask(__name__)


@app.before_request
def load_user():
    g.user = request.headers.get("X-User")


@app.get("/profile")
@login_required
def profile():
    return {"user": g.user}


@app.get("/orders/<int:number>")
@login_required
def order(number):
    return {"user": g.user, "order": number}


def ask(path, user=None):
    headers = {"X-User": user} if user else {}
    r = app.test_client().get(path, headers=headers)
    return [r.status_code, r.get_json()]
''', 'Check g.user at the start of wrapped and return the error pair early. @functools.wraps(view) copies the name, so Flask sees two different endpoints, profile and order.', '<p>Without functools.wraps both views would be called "wrapped", and Flask would refuse to register the second one with "View function mapping is overwriting an existing endpoint function". A real app would read the user from the session, not from a header anyone can send.</p>')
K.assign('bookdb', 'm', 'Safe database helpers with sqlite3',
         '<p>fresh_db() gives an in-memory database with the table book(id, title, year). Write <code>add_book(db, title, year)</code> that inserts a row with ? placeholders, commits and returns the new id. Write <code>find_books(db, words)</code>: titles that contain the words, ignoring upper and lower case, sorted A to Z. Write <code>books_per_decade(db)</code>: a list of [decade, count] such as [1960, 2], sorted by decade. Titles may contain quotes, so never build SQL with f-strings.</p>',
         '''
import sqlite3


def fresh_db():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE book (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, year INTEGER NOT NULL)")
    return db


def add_book(db, title, year):
    db.execute(f"INSERT INTO book (title, year) VALUES ('{title}', {year})")
    return 0


def find_books(db, words):
    rows = db.execute(f"SELECT title FROM book WHERE title LIKE '%{words}%'").fetchall()
    return [row[0] for row in rows]


def books_per_decade(db):
    return []


def shop():
    db = fresh_db()
    for title, year in [("Dune", 1965), ("Dune Messiah", 1969), ("Emma", 1815), ("The Hobbit", 1937), ("O'Brien's Guide", 1961)]:
        add_book(db, title, year)
    return db
''', [('add_book(fresh_db(), "Dune", 1965)', 1), ('(lambda db: [add_book(db, "A", 2000), add_book(db, "B", 2001)])(fresh_db())', [1, 2]), ('find_books(shop(), "dune")', ['Dune', 'Dune Messiah']), ("find_books(shop(), \"o'brien\")", ["O'Brien's Guide"]), ('find_books(shop(), "zzz")', []), ('books_per_decade(shop())', [[1810, 1], [1930, 1], [1960, 3]])],
         '''
import sqlite3


def fresh_db():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE book (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, year INTEGER NOT NULL)")
    return db


def add_book(db, title, year):
    cursor = db.execute("INSERT INTO book (title, year) VALUES (?, ?)", (title, year))
    db.commit()
    return cursor.lastrowid


def find_books(db, words):
    rows = db.execute("SELECT title FROM book WHERE LOWER(title) LIKE ? ORDER BY title",
                      ("%" + words.lower() + "%",)).fetchall()
    return [row[0] for row in rows]


def books_per_decade(db):
    rows = db.execute("SELECT (year / 10) * 10 AS decade, COUNT(*) FROM book GROUP BY decade ORDER BY decade").fetchall()
    return [list(row) for row in rows]


def shop():
    db = fresh_db()
    for title, year in [("Dune", 1965), ("Dune Messiah", 1969), ("Emma", 1815), ("The Hobbit", 1937), ("O'Brien's Guide", 1961)]:
        add_book(db, title, year)
    return db
''', 'Pass values as a tuple after the SQL. The % signs of LIKE go into the value, not into the SQL text. Integer division (year / 10) * 10 gives the decade in SQLite because year is an INTEGER.', '<p>The starter breaks on the title O&#39;Brien&#39;s Guide: the quote ends the SQL string early. That is exactly how SQL injection starts. With placeholders the database never mixes data with SQL.</p>')
K.assign('passwords', 'h', 'Hash and check passwords with PBKDF2',
         '<p>Write <code>make_hash(password, salt_hex, iterations)</code> that returns "pbkdf2:sha256:ITERATIONS$SALT$HASH", where HASH is the hex of hashlib.pbkdf2_hmac("sha256", password bytes, salt bytes, iterations). Write <code>verify(password, stored)</code> that splits the stored text, hashes the password again with the same salt and iterations, and compares with hmac.compare_digest. Write <code>password_problems(password)</code>: a list of problems, "too short" (under 12 characters), "no digit", "too common" (in COMMON, ignoring case), in that order.</p>',
         '''
import hashlib
import hmac

COMMON = {"password123", "qwerty123456", "letmein12345", "iloveyou1234"}


def make_hash(password, salt_hex, iterations):
    digest = hashlib.sha256(password.encode()).hexdigest()
    return f"sha256${digest}"


def verify(password, stored):
    return make_hash(password, "", 0) == stored


def password_problems(password):
    if len(password) < 12:
        return ["too short"]
    return []
''', [('make_hash("correct horse", "a1b2c3d4", 1000)', 'pbkdf2:sha256:1000$a1b2c3d4$31515ce4c7c935e24ae552c68ab3588b42efb5439692e0b45bec70b90b59dd09'), ('make_hash("pw", "00ff", 10)', 'pbkdf2:sha256:10$00ff$a608065ff13679da143c85c9d4183ca1d088d7fbb1ce8dbfe8da1eefb8fc7f70'), ('verify("correct horse", make_hash("correct horse", "a1b2c3d4", 1000))', True), ('verify("correct horsE", make_hash("correct horse", "a1b2c3d4", 1000))', False), ('password_problems("abc")', ['too short', 'no digit']), ('password_problems("Password123")', ['too short', 'too common']), ('password_problems("QWERTY123456")', ['too common']), ('password_problems("blue train 42 jumps")', [])],
         '''
import hashlib
import hmac

COMMON = {"password123", "qwerty123456", "letmein12345", "iloveyou1234"}


def make_hash(password, salt_hex, iterations):
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), iterations)
    return f"pbkdf2:sha256:{iterations}${salt_hex}${digest.hex()}"


def verify(password, stored):
    method, salt_hex, expected = stored.split("$")
    iterations = int(method.split(":")[2])
    again = make_hash(password, salt_hex, iterations).split("$")[2]
    return hmac.compare_digest(again, expected)


def password_problems(password):
    problems = []
    if len(password) < 12:
        problems.append("too short")
    if not any(ch.isdigit() for ch in password):
        problems.append("no digit")
    if password.lower() in COMMON:
        problems.append("too common")
    return problems
''', 'bytes.fromhex turns the salt text into bytes and .hex() turns the result back into text. In verify, split on "$" to get the method, the salt and the hash, and read the iterations from the method part.', '<p>This is the same format Werkzeug uses for method="pbkdf2:sha256". hmac.compare_digest takes the same time however many characters match, so an attacker cannot learn the hash from timing. Real apps let the library choose the salt with secrets.token_hex.</p>')

K.must('Structure', 'create_app(settings) returns a new app. Blueprint(name, __name__, url_prefix=...), app.register_blueprint(bp). url_for("bp.view"). current_app, not a global app.')
K.must('Database', 'get_db() on g, sqlite3.Row, ? placeholders, commit(), app.teardown_appcontext(close_db), @app.cli.command("init-db").')
K.must('Auth', 'generate_password_hash / check_password_hash (salted, slow). session.clear() then session["user_id"]. before_app_request loads g.user. login_required with functools.wraps.')
K.must('Tests', 'pytest fixture in conftest.py builds create_app({"TESTING": True}) and returns app.test_client(). app.test_cli_runner() for commands.')
K.must('Production', 'Config from environment (from_prefixed_env), app.logger, errorhandler passing HTTPException through, gunicorn "shop:create_app()" behind HTTPS.')

T = K.topic(
    slug='py-flask-apps', topic='py-flask-apps', step=(3, 'Flask: small and flexible web apps', 'py-w3', 'Build websites and JSON APIs with Flask: routes, requests, templates, forms and sessions, then app structure, a database, logins, tests and deployment.', 'Intermediate'),
    title='Real Flask apps: structure, database, login and tests', short='Flask apps', badge='3.2', minutes=100,
    lead='Turn a one file Flask app into one you can keep. Build it with an application factory and blueprints, store data with sqlite3, add users with hashed passwords, test it with pytest, configure it from the environment and deploy it.',
    desc='Application factory and blueprints, project layout, current_app, sqlite3 with g and teardown_appcontext, placeholders and SQL injection, a CLI init-db command, register and login with werkzeug.security, salted slow hashes, login_required, before_app_request, testing with pytest fixtures and the test client, configuration layers and environment variables, error handlers and logging, deployment with Gunicorn, nginx and containers, and the maths of hashing cost, transactions and salts.',
    summary='Application factory, blueprints, sqlite3, login with hashed passwords, pytest, config and deployment.',
    keywords=['application factory', 'blueprint', 'sqlite3', 'login', 'password hash', 'pytest', 'fixture', 'config', 'Gunicorn', 'deployment'],
    recap='<p>A factory builds a fresh app, blueprints split it into parts, g holds the database for one request, hashes protect passwords, and fixtures give every test a clean start.</p>',
    added='2026-11-07', leet=leet_items())
