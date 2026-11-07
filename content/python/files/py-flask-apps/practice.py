# 3.2 Real Flask apps: structure, database, login and tests
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


# ================================================================== task 1: Write a login_required decorator
# In this app, before_request puts the user name from the header X-User into g.user (None when the
# header is missing). Write the decorator login_required(view): when g.user is None it returns
# ({"error": "login required"}, 401) without running the view, otherwise it runs the view with its
# arguments. Use functools.wraps so the view keeps its name. ask() sends a request and returns
# [status, json].
# Hint: Check g.user at the start of wrapped and return the error pair early. @functools.wraps(view)
# copies the name, so Flask sees two different endpoints, profile and order.

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


# ================================================================== task 2: Safe database helpers with sqlite3
# fresh_db() gives an in-memory database with the table book(id, title, year). Write add_book(db,
# title, year) that inserts a row with ? placeholders, commits and returns the new id. Write
# find_books(db, words): titles that contain the words, ignoring upper and lower case, sorted A to
# Z. Write books_per_decade(db): a list of [decade, count] such as [1960, 2], sorted by decade.
# Titles may contain quotes, so never build SQL with f-strings.
# Hint: Pass values as a tuple after the SQL. The % signs of LIKE go into the value, not into the
# SQL text. Integer division (year / 10) * 10 gives the decade in SQLite because year is an INTEGER.

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


# ================================================================== task 3: Hash and check passwords with PBKDF2
# Write make_hash(password, salt_hex, iterations) that returns "pbkdf2:sha256:ITERATIONS$SALT$HASH",
# where HASH is the hex of hashlib.pbkdf2_hmac("sha256", password bytes, salt bytes, iterations).
# Write verify(password, stored) that splits the stored text, hashes the password again with the
# same salt and iterations, and compares with hmac.compare_digest. Write
# password_problems(password): a list of problems, "too short" (under 12 characters), "no digit",
# "too common" (in COMMON, ignoring case), in that order.
# Hint: bytes.fromhex turns the salt text into bytes and .hex() turns the result back into text. In
# verify, split on "$" to get the method, the salt and the hash, and read the iterations from the
# method part.

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


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Write a login_required decorator", [('ask("/profile", "ann")', [200, {'user': 'ann'}]), ('ask("/profile")', [401, {'error': 'login required'}]), ('ask("/orders/7", "bob")', [200, {'user': 'bob', 'order': 7}]), ('ask("/orders/7")', [401, {'error': 'login required'}]), ('[profile.__name__, order.__name__]', ['profile', 'order'])]))
    results.append(check("Task 2: Safe database helpers with sqlite3", [('add_book(fresh_db(), "Dune", 1965)', 1), ('(lambda db: [add_book(db, "A", 2000), add_book(db, "B", 2001)])(fresh_db())', [1, 2]), ('find_books(shop(), "dune")', ['Dune', 'Dune Messiah']), ('find_books(shop(), "o\'brien")', ["O'Brien's Guide"]), ('find_books(shop(), "zzz")', []), ('books_per_decade(shop())', [[1810, 1], [1930, 1], [1960, 3]])]))
    results.append(check("Task 3: Hash and check passwords with PBKDF2", [('make_hash("correct horse", "a1b2c3d4", 1000)', 'pbkdf2:sha256:1000$a1b2c3d4$31515ce4c7c935e24ae552c68ab3588b42efb5439692e0b45bec70b90b59dd09'), ('make_hash("pw", "00ff", 10)', 'pbkdf2:sha256:10$00ff$a608065ff13679da143c85c9d4183ca1d088d7fbb1ce8dbfe8da1eefb8fc7f70'), ('verify("correct horse", make_hash("correct horse", "a1b2c3d4", 1000))', True), ('verify("correct horsE", make_hash("correct horse", "a1b2c3d4", 1000))', False), ('password_problems("abc")', ['too short', 'no digit']), ('password_problems("Password123")', ['too short', 'too common']), ('password_problems("QWERTY123456")', ['too common']), ('password_problems("blue train 42 jumps")', [])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
