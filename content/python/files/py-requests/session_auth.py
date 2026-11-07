# 2.1 Calling web APIs with requests
# Example "session_auth" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

# ---------- A tiny practice API with a login cookie and a token ----------
TOKEN = "secret-token-123"


class PracticeAPI(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"                   # keep the connection open between requests

    def send_json(self, status, data, cookie=None):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):                               # POST /login
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        self.send_json(200, {"logged_in": True}, cookie="session=ann42; HttpOnly")

    def do_GET(self):
        if self.path == "/me" and "session=ann42" in self.headers.get("Cookie", ""):
            self.send_json(200, {"user": "ann", "via": "cookie"})
        elif self.path == "/orders" and self.headers.get("Authorization") == f"Bearer {TOKEN}":
            self.send_json(200, {"orders": [101, 102], "via": "token"})
        elif self.path == "/port":
            self.send_json(200, {"client_port": self.client_address[1]})
        else:
            self.send_json(401, {"error": "please log in"})

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), PracticeAPI)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_address[1]}"

# ---------- The part to learn: Session keeps cookies, headers and the connection ----------
print("without a session:", requests.get(BASE + "/me", timeout=5).status_code)

with requests.Session() as session:
    session.post(BASE + "/login", json={"user": "ann", "pw": "pw"}, timeout=5)
    print("cookies kept:", session.cookies.get_dict())
    print("with the session:", session.get(BASE + "/me", timeout=5).json())

    ports = {session.get(BASE + "/port", timeout=5).json()["client_port"] for _ in range(3)}
    print("3 requests used", len(ports), "connection")

with requests.Session() as api:
    api.headers.update({"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"})
    print("token:", api.get(BASE + "/orders", timeout=5).json())

ports = {requests.get(BASE + "/port", timeout=5).json()["client_port"] for _ in range(3)}
print("3 requests without a session used", len(ports), "connections")
server.shutdown()
