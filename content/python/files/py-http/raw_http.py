# 1.1 HTTP and REST: how the web talks
# Example "raw_http" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


class Hello(BaseHTTPRequestHandler):
    def do_GET(self):
        print("server got:", self.requestline)
        print("server saw the header Accept:", self.headers["Accept"])
        body = b"Hello from the server\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):            # keep the console quiet
        pass


server = HTTPServer(("127.0.0.1", 0), Hello)    # port 0: the system picks a free port
threading.Thread(target=server.serve_forever, daemon=True).start()
port = server.server_address[1]

request = (
    "GET /hello?name=ann HTTP/1.1\r\n"
    f"Host: 127.0.0.1:{port}\r\n"
    "Accept: text/plain\r\n"
    "Connection: close\r\n"
    "\r\n"                                      # the blank line ends the headers
)
with socket.create_connection(("127.0.0.1", port)) as sock:
    sock.sendall(request.encode())
    raw = b""
    while True:
        chunk = sock.recv(1024)
        if not chunk:
            break
        raw += chunk

print("--- the raw response ---")
for line in raw.decode().split("\r\n"):
    if not line.startswith(("Date:", "Server:")):   # these two change on every run
        print(repr(line))
server.shutdown()
