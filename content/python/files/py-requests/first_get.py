# 2.1 Calling web APIs with requests
# Example "first_get" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import requests

# ---------- A tiny practice API on your own computer, so this file needs no internet ----------
BOOKS = [{"id": 1, "title": "Dune", "year": 1965}, {"id": 2, "title": "Emma", "year": 1815},
         {"id": 3, "title": "Dune Messiah", "year": 1969}]


class PracticeAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlsplit(self.path)
        words = parse_qs(url.query).get("q", [""])[0].lower()
        found = [book for book in BOOKS if words in book["title"].lower()]
        body = json.dumps(found).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), PracticeAPI)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_address[1]}"

# ---------- The part to learn: calling the API with requests ----------
r = requests.get(BASE + "/books", params={"q": "dune messiah", "page": 1}, timeout=5)
print("url:", r.url.replace(BASE, ""))           # params became a query string, the space became +
print("status:", r.status_code, r.reason, "ok:", r.ok)
print("content type:", r.headers["content-type"])  # header names ignore upper and lower case
print("text:", r.text)
books = r.json()                                   # JSON text to Python lists and dicts
print("python:", type(books).__name__, books[0]["title"], books[0]["year"])

r = requests.get(BASE + "/books", params={"q": "dune"}, timeout=5)
for book in r.json():
    print(book["id"], book["title"])
print("we sent the header User-Agent:", r.request.headers["User-Agent"].split("/")[0])
server.shutdown()
