# 2.1 Calling web APIs with requests
# Example "sending" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

# ---------- A tiny practice API that answers with what it received ----------
class Echo(BaseHTTPRequestHandler):
    def answer(self):
        length = int(self.headers.get("Content-Length", 0))
        received = {"method": self.command, "path": self.path,
                    "content_type": self.headers.get("Content-Type"),
                    "body": self.rfile.read(length).decode()}
        body = json.dumps(received).encode()
        self.send_response(201 if self.command == "POST" else 200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = answer

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Echo)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_address[1]}"

# ---------- The part to learn: the methods and the three ways to send data ----------
book = {"title": "Emma", "year": 1815}

r = requests.post(BASE + "/books", json=book, timeout=5)        # JSON body
print(r.status_code, r.json())

r = requests.post(BASE + "/login", data={"user": "ann", "pw": "a b"}, timeout=5)    # web form body
print(r.status_code, r.json())

r = requests.get(BASE + "/books", params={"year": 1815}, timeout=5)    # no body, data in the URL
print(r.status_code, r.json())

r = requests.put(BASE + "/books/2", json={"title": "Emma", "year": 1816}, timeout=5)   # replace it all
print(r.json()["method"], r.json()["body"])
r = requests.patch(BASE + "/books/2", json={"year": 1816}, timeout=5)                  # change a part
print(r.json()["method"], r.json()["body"])
r = requests.delete(BASE + "/books/2", timeout=5)
print(r.json()["method"], r.json()["path"], "body:", repr(r.json()["body"]))
server.shutdown()
