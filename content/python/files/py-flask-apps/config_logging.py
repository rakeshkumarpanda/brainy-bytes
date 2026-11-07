# 3.2 Real Flask apps: structure, database, login and tests
# Example "config_logging" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import logging
import os
import sys

from flask import Flask, request
from werkzeug.exceptions import HTTPException

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

# Normally these come from the shell, a .env file or the hosting service, never from the code
os.environ["FLASK_SHOP_NAME"] = "Env Shop"
os.environ["FLASK_PAGE_SIZE"] = "25"


def create_app():
    app = Flask("shop")
    app.config.from_mapping(SHOP_NAME="Dev Shop", PAGE_SIZE=10, SECRET_KEY="dev")   # defaults
    app.config.from_prefixed_env()           # FLASK_X=value becomes config["X"], and "25" becomes 25

    @app.get("/")
    def home():
        app.logger.info("home page for %s", request.remote_addr)
        return f"{app.config['SHOP_NAME']} shows {app.config['PAGE_SIZE']} books per page"

    @app.get("/boom")
    def boom():
        return str(1 / 0)

    @app.errorhandler(Exception)
    def any_error(error):
        if isinstance(error, HTTPException):  # 404, 405 ... keep their normal answer
            return error
        app.logger.error("crash on %s: %r", request.path, error)
        return {"error": "something went wrong, we are looking at it"}, 500

    return app


app = create_app()
client = app.test_client()
print(client.get("/").get_data(as_text=True))
r = client.get("/boom")
print(r.status_code, r.get_json())
print(client.get("/nope").status_code)
print(type(app.config["PAGE_SIZE"]).__name__, app.config["SECRET_KEY"] == "dev")
