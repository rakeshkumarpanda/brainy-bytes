# 2.2 Real API work: pages, retries, limits and validation
# Example "pagination" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import requests

# ---------- A tiny practice API with page numbers and with cursors ----------
ITEMS = [f"item{n}" for n in range(1, 8)]      # newest first: item1 is the newest


class PracticeAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlsplit(self.path)
        query = {name: values[0] for name, values in parse_qs(url.query).items()}
        size = int(query.get("size", 3))
        if url.path == "/pages":                 # ?page=1&size=3
            page = int(query.get("page", 1))
            start = (page - 1) * size
            data = {"items": ITEMS[start:start + size], "page": page,
                    "pages": (len(ITEMS) + size - 1) // size}
        else:                                    # /cursor?after=item3&size=3
            after = query.get("after")
            start = ITEMS.index(after) + 1 if after else 0
            chunk = ITEMS[start:start + size]
            more = start + size < len(ITEMS)
            data = {"items": chunk, "next": chunk[-1] if more else None}
        body = json.dumps(data).encode()
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

# ---------- The part to learn: generators that walk through every page ----------
def by_page(session, size=3):
    page = 1
    while True:
        data = session.get(BASE + "/pages", params={"page": page, "size": size}, timeout=5).json()
        yield from data["items"]
        if page >= data["pages"]:
            return
        page += 1


def by_cursor(session, size=3):
    after = None
    while True:
        params = {"size": size}
        if after:
            params["after"] = after
        data = session.get(BASE + "/cursor", params=params, timeout=5).json()
        yield from data["items"]
        after = data["next"]
        if after is None:
            return


with requests.Session() as session:
    print("pages: ", list(by_page(session)))
    print("cursor:", list(by_cursor(session)))

    # A new item arrives while we read. Page numbers shift, cursors do not.
    pages = by_page(session)
    first = [next(pages) for _ in range(3)]
    ITEMS.insert(0, "item0")
    print("pages while adding: ", first + list(pages))

    ITEMS.remove("item0")
    cursor = by_cursor(session)
    first = [next(cursor) for _ in range(3)]
    ITEMS.insert(0, "item0")
    print("cursor while adding:", first + list(cursor))
server.shutdown()
