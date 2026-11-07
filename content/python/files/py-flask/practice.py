# 3.1 Flask basics: routes, templates, forms and JSON
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


# ================================================================== task 1: Match URLs the way Flask does
# Write match(pattern, path). A pattern such as "/users/<int:uid>/posts/<slug>" has fixed parts and
# variable parts in angle brackets. Return a dict of the variable parts when the path fits (int:
# parts must be digits and become int), or None when it does not fit. Then write route(routes,
# path): routes is a list of (pattern, endpoint) pairs. Return [endpoint, params] for the first
# pattern that fits, or ["404", {}]. Careful: a pattern with no variables gives an empty dict, which
# still means a match.
# Hint: Split both on "/" and compare part by part: the counts must be equal, fixed parts must be
# equal, and variable parts go into the dict. In route, test "is not None", because an empty dict is
# a match too.

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


# ================================================================== task 2: Build and test a small notes API
# Write create_app() that returns a Flask app with a notes API. GET /api/notes gives the list of
# notes. POST /api/notes with {"text": ...} adds a note {"id", "text", "done": false} with the text
# stripped, answers 201, and answers 422 with {"error": "text is required"} for empty text. PATCH
# /api/notes/<id> with {"done": true} changes done and returns the note, 404 with {"error": "not
# found"} for an unknown id, and 422 with {"error": "done must be true or false"} when done is not a
# bool. Each app starts empty with ids from 1. run_steps() sends requests with the test client.
# Hint: Keep the notes in a dict by id inside create_app, so every app starts empty. Use
# request.get_json(silent=True) or {} so bad JSON does not crash, and return (body, status) pairs
# for the errors.

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


# ================================================================== task 3: Write a tiny template engine
# Write render(template, context) that replaces every {{ ... }} in the template. Inside the braces
# there is a name, maybe with dots for nested dicts ("user.city"), and maybe filters after |
# ("name|upper", "books|length"). Spaces inside the braces do not matter. A missing name gives "".
# Supported filters: upper, lower, title and length, and any other filter raises ValueError. Like
# Jinja, escape the final text with html.escape, so a < in a value becomes &lt;.
# Hint: A regular expression finds each placeholder, and re.sub calls a function for every match.
# Split the inside on "|", walk the dotted name through the dicts, apply the filters in order, then
# escape.

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


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Match URLs the way Flask does", [('match("/books/<book_id>", "/books/42")', {'book_id': '42'}), ('match("/users/<int:uid>/posts/<slug>", "/users/7/posts/hello-world")', {'uid': 7, 'slug': 'hello-world'}), ('match("/users/<int:uid>", "/users/abc")', None), ('match("/books/<book_id>", "/books/42/reviews")', None), ('route(ROUTES, "/")', ['home', {}]), ('route(ROUTES, "/books/9")', ['book', {'book_id': 9}]), ('route(ROUTES, "/books/new")', ['new_book', {}]), ('route(ROUTES, "/users/ann/books")', ['user_books', {'name': 'ann'}]), ('route(ROUTES, "/cart")', ['404', {}])]))
    results.append(check("Task 2: Build and test a small notes API", [('run_steps([("GET", "/api/notes", None)])', [[200, []]]), ('run_steps([("POST", "/api/notes", {"text": " buy milk "}), ("GET", "/api/notes", None)])', [[201, {'id': 1, 'text': 'buy milk', 'done': False}], [200, [{'id': 1, 'text': 'buy milk', 'done': False}]]]), ('run_steps([("POST", "/api/notes", {"text": "  "})])', [[422, {'error': 'text is required'}]]), ('run_steps([("POST", "/api/notes", {"text": "a"}), ("PATCH", "/api/notes/1", {"done": True})])', [[201, {'id': 1, 'text': 'a', 'done': False}], [200, {'id': 1, 'text': 'a', 'done': True}]]), ('run_steps([("PATCH", "/api/notes/9", {"done": True})])', [[404, {'error': 'not found'}]]), ('run_steps([("POST", "/api/notes", {"text": "a"}), ("PATCH", "/api/notes/1", {"done": "yes"})])', [[201, {'id': 1, 'text': 'a', 'done': False}], [422, {'error': 'done must be true or false'}]]), ('run_steps([("DELETE", "/api/notes", None)])', [[405, None]])]))
    results.append(check("Task 3: Write a tiny template engine", [('render("Hello {{ name }}!", {"name": "Ann"})', 'Hello Ann!'), ('render("{{name}} has {{ books|length }} books", {"name": "Ann", "books": ["a", "b"]})', 'Ann has 2 books'), ('render("{{ user.city|upper }} / {{ user.zip }}", {"user": {"city": "Pune", "zip": 411001}})', 'PUNE / 411001'), ('render("Hi {{ who }}", {"who": "<b>Bob</b>"})', 'Hi &lt;b&gt;Bob&lt;/b&gt;'), ('render("[{{ missing }}] [{{ user.age }}]", {"user": {}})', '[] []'), ('render("{{ title|lower|title }}", {"title": "the HOBBIT"})', 'The Hobbit'), ('render_error("{{ x|shout }}")', 'ValueError')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
