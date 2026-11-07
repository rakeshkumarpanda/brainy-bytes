# 3.1 Flask basics: routes, templates, forms and JSON
# Example "request_response" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
