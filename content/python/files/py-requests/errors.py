# 2.1 Calling web APIs with requests
# Example "errors" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

# ---------- A tiny practice API with a missing book, a slow page and a page that is not JSON ----------
class PracticeAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/slow":
            time.sleep(1)
        if self.path == "/html":
            status, kind, body = 200, "text/html", b"<h1>Hello</h1>"
        elif self.path == "/books/1":
            status, kind, body = 200, "application/json", b'{"id": 1, "title": "Dune"}'
        else:
            status, kind, body = 404, "application/json", b'{"error": "not found"}'
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), PracticeAPI)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_address[1]}"

# ---------- The part to learn: every way a call can fail ----------
r = requests.get(BASE + "/books/99", timeout=5)
print("404 is not an exception:", r.status_code, r.ok)
try:
    r.raise_for_status()
except requests.HTTPError as err:
    print("HTTPError:", err.response.status_code, err.response.json())

try:
    requests.get(BASE + "/slow", timeout=0.2)
except requests.Timeout as err:
    print("Timeout:", type(err).__name__)

try:
    requests.get("http://127.0.0.1:9", timeout=2)        # nothing listens on port 9
except requests.ConnectionError as err:
    print("ConnectionError:", type(err).__name__)

try:
    requests.get(BASE + "/html", timeout=5).json()
except requests.JSONDecodeError:
    print("JSONDecodeError: the body is not JSON")


def get_json(url):
    """Return (data, None) when it works, or (None, a short message) when it fails."""
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json(), None
    except requests.HTTPError as err:
        return None, f"server said {err.response.status_code}"
    except requests.JSONDecodeError:                  # must come before RequestException, its parent
        return None, "the answer was not JSON"
    except requests.RequestException as err:         # the parent of all requests errors
        return None, f"network problem: {type(err).__name__}"


for path in ["/books/1", "/books/7", "/html"]:
    print(path, get_json(BASE + path))
print(get_json("http://127.0.0.1:9/books"))
server.shutdown()
