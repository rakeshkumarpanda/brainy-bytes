# 1.1 HTTP and REST: how the web talks
# Example "book_api" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import json
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.error import HTTPError

BOOKS = {1: {"id": 1, "title": "Dune"}, 2: {"id": 2, "title": "Emma"}}


class BookAPI(BaseHTTPRequestHandler):
    def send_json(self, status, data, extra_headers=None):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/books":
            return self.send_json(200, list(BOOKS.values()))
        parts = self.path.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "books" and parts[1].isdigit():
            book = BOOKS.get(int(parts[1]))
            if book is None:
                return self.send_json(404, {"error": f"book {parts[1]} not found"})
            return self.send_json(200, book)
        self.send_json(404, {"error": "no such page"})

    def do_POST(self):
        if self.path != "/books":
            return self.send_json(404, {"error": "no such page"})
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length))
            title = data["title"].strip()
        except (ValueError, KeyError, AttributeError):
            return self.send_json(400, {"error": "send JSON with a title"})
        new_id = max(BOOKS) + 1
        BOOKS[new_id] = {"id": new_id, "title": title}
        self.send_json(201, BOOKS[new_id], {"Location": f"/books/{new_id}"})

    def log_message(self, *args):
        pass


server = HTTPServer(("127.0.0.1", 0), BookAPI)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_address[1]}"


def call(method, path, data=None):
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(BASE + path, data=body, method=method,
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, response.headers.get("Location"), json.loads(response.read())
    except HTTPError as err:                     # urllib raises for 4xx and 5xx
        return err.code, None, json.loads(err.read())


print(call("GET", "/books"))
print(call("GET", "/books/2"))
print(call("GET", "/books/99"))
print(call("POST", "/books", {"title": "Ulysses"}))
print(call("POST", "/books", {"name": "no title"}))
print(call("GET", "/books"))
server.shutdown()
