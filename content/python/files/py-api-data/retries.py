# 2.2 Real API work: pages, retries, limits and validation
# Example "retries" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import json
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------- A tiny practice API that fails a few times before it works ----------
calls = {"/flaky": 0, "/limited": 0, "/auto": 0}


class PracticeAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        calls[self.path] += 1
        n = calls[self.path]
        if self.path in ("/flaky", "/auto") and n <= 2:
            status, extra = 503, {}
        elif self.path == "/limited" and n == 1:
            status, extra = 429, {"Retry-After": "1"}
        else:
            status, extra = 200, {}
        body = json.dumps({"try": n}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for name, value in extra.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), PracticeAPI)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_address[1]}"

# ---------- The part to learn: retries with backoff, jitter and Retry-After ----------
RETRY_STATUS = {429, 500, 502, 503, 504}


def get_with_retries(session, url, tries=4, base=0.1, cap=2.0):
    for attempt in range(tries):
        try:
            r = session.get(url, timeout=5)
            if r.status_code not in RETRY_STATUS:
                return r
            reason = r.status_code
            told = r.headers.get("Retry-After")
        except (requests.ConnectionError, requests.Timeout) as err:
            reason, told = type(err).__name__, None
        if attempt == tries - 1:
            break
        if told:
            wait = float(told)                                     # the server said how long
        else:
            wait = random.uniform(0, min(cap, base * 2 ** attempt))   # backoff with full jitter
        print(f"  try {attempt + 1} got {reason}, waiting {wait:.2f} s")
        time.sleep(wait)
    raise RuntimeError(f"gave up after {tries} tries")


random.seed(7)
with requests.Session() as session:
    print("flaky:", get_with_retries(session, BASE + "/flaky").json())
    start = time.perf_counter()
    print("limited:", get_with_retries(session, BASE + "/limited").json(),
          f"after {time.perf_counter() - start:.1f} s")

    # The same idea built into requests: mount an HTTPAdapter with a urllib3 Retry
    retry = Retry(total=3, backoff_factor=0.05, status_forcelist=sorted(RETRY_STATUS),
                  allowed_methods={"GET", "HEAD", "PUT", "DELETE"}, respect_retry_after_header=True)
    session.mount("http://", HTTPAdapter(max_retries=retry))
    r = session.get(BASE + "/auto", timeout=5)
    print("auto:", r.status_code, r.json(), "server saw", calls["/auto"], "requests")
server.shutdown()
