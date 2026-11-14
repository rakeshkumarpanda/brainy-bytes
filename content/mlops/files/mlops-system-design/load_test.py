# 4.1 Designing an ML system end to end
# Example "load_test" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A small load test for a model API, using only the Python standard library.
#   python load_test.py                                  tests a built-in demo server (4 workers, 20 ms a prediction)
#   python load_test.py --url http://127.0.0.1:8000/predict   tests your own FastAPI or Docker service from MLOps 2.2 and 2.3
import argparse
import json
import statistics
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

FLOWER = {'sepal_length': 5.9, 'sepal_width': 3.0, 'petal_length': 5.1, 'petal_width': 1.8}
NO_PROXY = urllib.request.build_opener(urllib.request.ProxyHandler({}))   # talk to the server directly
WORKERS = threading.Semaphore(4)                                     # the demo server can work on 4 requests at once


class DemoModel(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers.get('Content-Length', 0)))
        with WORKERS:                                                # extra requests wait in a queue here
            time.sleep(0.020)                                        # pretend the model needs 20 ms
        body = json.dumps({'species': 'virginica', 'probability': 0.97}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):                                    # keep the terminal quiet
        pass


class DemoServer(ThreadingHTTPServer):
    request_queue_size = 128                                         # the default backlog of 5 is too small for 16 users


def one_call(url):
    data = json.dumps(FLOWER).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    start = time.perf_counter()
    with NO_PROXY.open(req, timeout=10) as r:
        r.read()
    return (time.perf_counter() - start) * 1000


def run_level(url, users, total):
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=users) as pool:
        ms = sorted(pool.map(lambda _: one_call(url), range(total)))
    seconds = time.perf_counter() - start
    pct = lambda q: ms[min(len(ms) - 1, int(q * len(ms)))]
    return total / seconds, statistics.median(ms), pct(0.95), pct(0.99)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--url', help='the /predict address of a running service')
    ap.add_argument('--requests', type=int, default=300)
    args = ap.parse_args()
    url, server = args.url, None
    if not url:
        server = DemoServer(('127.0.0.1', 0), DemoModel)              # port 0: the system picks a free port
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}/predict'
        print('No --url given, so testing the built-in demo server: 4 workers, 20 ms a prediction')
    one_call(url)                                                    # warm up
    print(f'{"users":>5s} {"req/s":>7s} {"p50 ms":>7s} {"p95 ms":>7s} {"p99 ms":>7s}')
    for users in [1, 2, 4, 8, 16]:
        rps, p50, p95, p99 = run_level(url, users, args.requests)
        print(f'{users:5d} {rps:7.0f} {p50:7.1f} {p95:7.1f} {p99:7.1f}')
    print("Little's law: requests/s is about users / latency until the workers are full.")
    print('After that, more users only make every request wait longer.')
    if server:
        server.shutdown()


if __name__ == '__main__':
    main()
