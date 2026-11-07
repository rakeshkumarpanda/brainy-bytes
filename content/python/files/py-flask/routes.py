# 3.1 Flask basics: routes, templates, forms and JSON
# Example "routes" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
