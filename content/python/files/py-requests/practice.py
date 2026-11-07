# 2.1 Calling web APIs with requests
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


# ================================================================== task 1: Pick data out of an API answer
# REPOS is a list of repositories as an API like GitHub returns it. Write top_repos(repos, n): the
# names of the n repositories with the most stars ("stars"), and on a tie the name that comes first
# A to Z. Write language_counts(repos): a dict from language to how many repositories use it, where
# a language that is null or missing counts as "unknown".
# Hint: Sort by (minus stars, name) so more stars come first and ties go A to Z.
# repo.get("language") or "unknown" covers both a missing key and None.

def top_repos(repos, n):
    ranked = sorted(repos, key=lambda repo: repo["stars"])
    return [repo["name"] for repo in ranked[:n]]


def language_counts(repos):
    counts = {}
    for repo in repos:
        language = repo["language"]
        counts[language] = counts.get(language, 0) + 1
    return counts


REPOS = [
    {"name": "flask", "stars": 68000, "language": "Python"},
    {"name": "requests", "stars": 52000, "language": "Python"},
    {"name": "httpx", "stars": 13000, "language": "Python"},
    {"name": "express", "stars": 65000, "language": "JavaScript"},
    {"name": "awesome-list", "stars": 52000, "language": None},
    {"name": "notes", "stars": 3},
]


# ================================================================== task 2: Read a value from nested JSON by a path
# Write get_path(data, path, default=None). The path is keys and list positions joined by dots, such
# as "user.address.city" or "orders.1.total". When the current value is a list, the part must be a
# number and is used as a position. Return default when a key is missing, a position is out of
# range, or the value is not a dict or a list.
# Hint: Look at the type of the current value at each step: a dict needs the key, a list needs a
# number in range, anything else means the path is wrong. A key that is there with the value null
# gives None, not the default.

def get_path(data, path, default=None):
    value = data
    for part in path.split("."):
        value = value[part]
    return value


DATA = {
    "user": {"name": "Ann", "address": {"city": "Pune", "zip": None}},
    "orders": [{"id": 7, "total": 250}, {"id": 9, "total": 99}],
}


# ================================================================== task 3: Write a small API client you can test
# BookClient gets a send(method, path, body=None) function that returns (status, data). In real code
# send would use requests, and in the tests it is FakeServer.send. Write get_book(book_id): the book
# dict, None for 404, and for a 5xx status try again, 3 tries in total, then raise RuntimeError.
# Write create_book(title): POST /books with {"title": title}, return the new book for 201, raise
# ValueError with the message from the server for 422. Never retry the POST, and raise RuntimeError
# for any other status.
# Hint: A for loop with an else block fits the retry: break when the status is below 500, and the
# else part runs only when every try failed. Map each status to a return value or an exception.

class FakeServer:
    """Pretends to be the book API. send(method, path, body) returns (status, data)."""

    def __init__(self):
        self.books = {1: {"id": 1, "title": "Dune"}}
        self.calls = 0
        self.fail_next = 0

    def send(self, method, path, body=None):
        self.calls += 1
        if self.fail_next > 0:
            self.fail_next -= 1
            return 503, {"error": "busy, try later"}
        if method == "GET" and path.startswith("/books/"):
            book_id = int(path.split("/")[2])
            if book_id in self.books:
                return 200, self.books[book_id]
            return 404, {"error": "not found"}
        if method == "POST" and path == "/books":
            title = str((body or {}).get("title", "")).strip()
            if not title:
                return 422, {"error": "title is required"}
            new_id = max(self.books) + 1
            self.books[new_id] = {"id": new_id, "title": title}
            return 201, self.books[new_id]
        return 405, {"error": "method not allowed"}


class BookClient:
    def __init__(self, send):
        self.send = send

    def get_book(self, book_id):
        status, data = self.send("GET", f"/books/{book_id}")
        return data

    def create_book(self, title):
        status, data = self.send("POST", "/books", {"title": title})
        return data


def try_get(book_id):
    return BookClient(FakeServer().send).get_book(book_id)


def create(title):
    return BookClient(FakeServer().send).create_book(title)


def create_error(title):
    try:
        create(title)
    except ValueError as err:
        return f"ValueError: {err}"
    return "no error"


def flaky(failures):
    server = FakeServer()
    server.fail_next = failures
    try:
        book = BookClient(server.send).get_book(1)
    except RuntimeError:
        return ["RuntimeError", server.calls]
    return [book, server.calls]


def flaky_post():
    server = FakeServer()
    server.fail_next = 1
    try:
        BookClient(server.send).create_book("Emma")
    except RuntimeError:
        return ["RuntimeError", server.calls]
    return ["no error", server.calls]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Pick data out of an API answer", [('top_repos(REPOS, 3)', ['flask', 'express', 'awesome-list']), ('top_repos(REPOS, 1)', ['flask']), ('top_repos([], 2)', []), ('language_counts(REPOS)', {'Python': 3, 'JavaScript': 1, 'unknown': 2}), ('language_counts([])', {})]))
    results.append(check("Task 2: Read a value from nested JSON by a path", [('get_path(DATA, "user.address.city")', 'Pune'), ('get_path(DATA, "orders.1.total")', 99), ('get_path(DATA, "orders.5.total", "none")', 'none'), ('get_path(DATA, "user.phone", "?")', '?'), ('get_path(DATA, "user.name.first", "?")', '?'), ('get_path(DATA, "orders.x", 0)', 0), ('get_path(DATA, "user.address.zip", "empty")', None)]))
    results.append(check("Task 3: Write a small API client you can test", [('try_get(1)', {'id': 1, 'title': 'Dune'}), ('try_get(5)', None), ('create("  Emma ")', {'id': 2, 'title': 'Emma'}), ('create_error("")', 'ValueError: title is required'), ('flaky(2)', [{'id': 1, 'title': 'Dune'}, 3]), ('flaky(3)', ['RuntimeError', 3]), ('flaky_post()', ['RuntimeError', 1])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
