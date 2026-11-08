# 6.2 Web revision exam: HTTP, Flask, Django, FastAPI and security
# Example "paper_b" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
    print("Q10", url_for("get_book", book_id=7), url_for("admin.stats"), url_for("search", q="a b", page=2))
