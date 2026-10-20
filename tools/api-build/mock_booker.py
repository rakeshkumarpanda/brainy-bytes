"""A small local copy of the public Restful Booker practice API (https://restful-booker.herokuapp.com).

Every example on the API Automation Testing page targets Restful Booker. This server copies its
documented behaviour so the examples can be run without internet access:

  GET    /ping                       201 Created
  POST   /auth                       {"token": "..."} for admin / password123, else {"reason": "Bad credentials"}
  GET    /booking                    [{"bookingid": n}], filters: firstname, lastname, checkin, checkout
  GET    /booking/{id}               the booking, or 404 Not Found
  POST   /booking                    {"bookingid": n, "booking": {...}}
  PUT    /booking/{id}               needs Cookie token=... or Basic admin:password123, else 403 Forbidden
  PATCH  /booking/{id}               same auth, partial update
  DELETE /booking/{id}               same auth, 201 Created (the real API answers 201 here too)

Usage:  python3 tools/api-build/mock_booker.py [port]      (default port 3001)
"""
import base64
import json
import secrets
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

LOCK = threading.Lock()
TOKENS = set()
BOOKINGS = {}
NEXT = [1]
FIELDS = ['firstname', 'lastname', 'totalprice', 'depositpaid', 'bookingdates', 'additionalneeds']


def seed():
    for f, l, p, d, ci, co, n in [
        ('Sally', 'Brown', 111, True, '2026-01-01', '2026-01-05', 'Breakfast'),
        ('Jim', 'Jones', 220, False, '2026-02-10', '2026-02-12', 'Late checkout'),
        ('Mary', 'Ericsson', 540, True, '2026-03-03', '2026-03-09', 'Lunch'),
    ]:
        add({'firstname': f, 'lastname': l, 'totalprice': p, 'depositpaid': d,
             'bookingdates': {'checkin': ci, 'checkout': co}, 'additionalneeds': n})


def add(b):
    with LOCK:
        i = NEXT[0]
        NEXT[0] += 1
        BOOKINGS[i] = b
        return i


def valid(b):
    return (isinstance(b, dict) and isinstance(b.get('firstname'), str) and isinstance(b.get('lastname'), str)
            and isinstance(b.get('totalprice'), (int, float)) and isinstance(b.get('depositpaid'), bool)
            and isinstance(b.get('bookingdates'), dict) and 'checkin' in b['bookingdates'] and 'checkout' in b['bookingdates'])


class H(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *a):
        pass

    def send(self, code, body, ctype='application/json; charset=utf-8'):
        data = (json.dumps(body) if not isinstance(body, str) else body).encode()
        if isinstance(body, str):
            ctype = 'text/plain; charset=utf-8'
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('X-Powered-By', 'Express')
        self.end_headers()
        self.wfile.write(data)

    def body(self):
        n = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(n) if n else b''
        try:
            return json.loads(raw or b'null')
        except ValueError:
            return None

    def authed(self):
        cookie = self.headers.get('Cookie') or ''
        for part in cookie.split(';'):
            k, _, v = part.strip().partition('=')
            if k == 'token' and v in TOKENS:
                return True
        a = self.headers.get('Authorization') or ''
        if a.startswith('Basic '):
            try:
                return base64.b64decode(a[6:]).decode() == 'admin:password123'
            except ValueError:
                return False
        return False

    def route(self):
        u = urlparse(self.path)
        parts = [p for p in u.path.split('/') if p]
        return u, parts

    def do_GET(self):
        u, p = self.route()
        if p == ['ping']:
            return self.send(201, 'Created')
        if p == ['booking']:
            q = {k: v[0] for k, v in parse_qs(u.query).items()}
            out = []
            for i, b in sorted(BOOKINGS.items()):
                if 'firstname' in q and b['firstname'] != q['firstname']:
                    continue
                if 'lastname' in q and b['lastname'] != q['lastname']:
                    continue
                if 'checkin' in q and b['bookingdates']['checkin'] < q['checkin']:
                    continue
                if 'checkout' in q and b['bookingdates']['checkout'] > q['checkout']:
                    continue
                out.append({'bookingid': i})
            return self.send(200, out)
        if len(p) == 2 and p[0] == 'booking' and p[1].isdigit() and int(p[1]) in BOOKINGS:
            return self.send(200, BOOKINGS[int(p[1])])
        return self.send(404, 'Not Found')

    def do_POST(self):
        u, p = self.route()
        b = self.body()
        if p == ['auth']:
            if isinstance(b, dict) and b.get('username') == 'admin' and b.get('password') == 'password123':
                t = secrets.token_hex(8)
                TOKENS.add(t)
                return self.send(200, {'token': t})
            return self.send(200, {'reason': 'Bad credentials'})
        if p == ['booking']:
            if not valid(b):
                return self.send(500, 'Internal Server Error')
            b = {k: b[k] for k in FIELDS if k in b}
            return self.send(200, {'bookingid': add(b), 'booking': b})
        return self.send(404, 'Not Found')

    def change(self, partial):
        u, p = self.route()
        b = self.body()   # always read the body, so a keep-alive connection stays in sync
        if not (len(p) == 2 and p[0] == 'booking' and p[1].isdigit()):
            return self.send(404, 'Not Found')
        if not self.authed():
            return self.send(403, 'Forbidden')
        i = int(p[1])
        if i not in BOOKINGS:
            return self.send(405, 'Method Not Allowed')
        if partial:
            if not isinstance(b, dict):
                return self.send(400, 'Bad Request')
            BOOKINGS[i] = {**BOOKINGS[i], **{k: b[k] for k in FIELDS if k in b}}
        else:
            if not valid(b):
                return self.send(400, 'Bad Request')
            BOOKINGS[i] = {k: b[k] for k in FIELDS if k in b}
        return self.send(200, BOOKINGS[i])

    def do_PUT(self):
        self.change(False)

    def do_PATCH(self):
        self.change(True)

    def do_DELETE(self):
        u, p = self.route()
        self.body()
        if not (len(p) == 2 and p[0] == 'booking' and p[1].isdigit()):
            return self.send(404, 'Not Found')
        if not self.authed():
            return self.send(403, 'Forbidden')
        if BOOKINGS.pop(int(p[1]), None) is None:
            return self.send(405, 'Method Not Allowed')
        return self.send(201, 'Created')


if __name__ == '__main__':
    seed()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3001
    print(f'Restful Booker copy on http://localhost:{port}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()
