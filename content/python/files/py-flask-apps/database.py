# 3.2 Real Flask apps: structure, database, login and tests
# Example "database" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
