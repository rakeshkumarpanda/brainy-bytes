# 6.2 Web revision exam: HTTP, Flask, Django, FastAPI and security
# Example "paper_a" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import json
from http import HTTPStatus
from http.cookies import SimpleCookie
from urllib.parse import parse_qs, quote, urlencode, urljoin, urlsplit

u = urlsplit("https://api.shop.example:8443/v2/books?q=python&page=2#top")
print("Q1", u.scheme, u.hostname, u.port, u.path, u.query, u.fragment)

print("Q2", parse_qs("tag=a&tag=b&empty="), parse_qs("tag=a&tag=b&empty=", keep_blank_values=True)["empty"])

print("Q3", urlencode({"q": "tea & cake", "page": 1}), quote("/a b/"), quote("/a b/", safe=""))

print("Q4", urljoin("https://x.example/api/v1/", "books"), urljoin("https://x.example/api/v1", "books"),
      urljoin("https://x.example/api/v1/", "/books"))

print("Q5", [s.value for s in (HTTPStatus(201), HTTPStatus.NOT_FOUND)], HTTPStatus(429).phrase,
      [code // 100 for code in (204, 301, 422, 503)])

SAFE = {"GET", "HEAD", "OPTIONS"}
IDEMPOTENT = SAFE | {"PUT", "DELETE"}
print("Q6", sorted(m for m in ["GET", "POST", "PUT", "PATCH", "DELETE"] if m not in IDEMPOTENT))

c = SimpleCookie()
c.load("session=abc123; theme=dark")
print("Q7", c["session"].value, sorted(c))

body = json.dumps({"price": 9.5, "tags": ("a", "b"), "ok": None, 1: "one"})
print("Q8", body, json.loads(body)["1"])

raw = "HTTP/1.1 301 Moved Permanently\r\nLocation: /new\r\nContent-Length: 0\r\n\r\n"
status_line, *header_lines = raw.split("\r\n")[:-2]
headers = dict(line.split(": ", 1) for line in header_lines)
print("Q9", status_line.split(" ", 2), headers["Location"])

print("Q10", len("café".encode()), len("café"), "caf%C3%A9" == quote("café"))
