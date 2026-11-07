# 3.1 Flask basics: routes, templates, forms and JSON
# Example "json_api" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
