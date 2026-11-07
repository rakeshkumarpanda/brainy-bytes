# 3.1 Flask basics: routes, templates, forms and JSON
# Example "real_server" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import logging
import threading

import requests
from flask import Flask
from werkzeug.serving import make_server

app = Flask(__name__)
logging.getLogger("werkzeug").setLevel(logging.ERROR)     # hide the one log line per request


@app.get("/api/ping")
def ping():
    return {"pong": True}


# What "flask --app real_server run" does, but in a thread so this one file can also call it
server = make_server("127.0.0.1", 0, app)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_port}/api/ping"

r = requests.get(url, timeout=5)
print(r.status_code, r.headers["Content-Type"], r.json())
print("served by:", r.headers["Server"].split("/")[0])
server.shutdown()
