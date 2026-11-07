# 3.2 Real Flask apps: structure, database, login and tests
# Example "factory_blueprints" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from flask import Blueprint, Flask, current_app, url_for

# ---------- shop/main.py: the pages for people ----------
main = Blueprint("main", __name__)


@main.route("/")
def home():
    return f"Home of {current_app.config['SHOP_NAME']}"


# ---------- shop/api.py: the JSON API, all under /api ----------
api = Blueprint("api", __name__, url_prefix="/api")


@api.get("/books")
def list_books():
    return [{"id": 1, "title": "Dune"}]


@api.get("/status")
def status():
    return {"testing": current_app.testing, "home": url_for("main.home")}


# ---------- shop/__init__.py: the application factory ----------
def create_app(settings=None):
    app = Flask(__name__)
    app.config.from_mapping(SHOP_NAME="Brainy Books", SECRET_KEY="dev")   # safe defaults
    if settings:
        app.config.update(settings)                                       # tests or production override them
    app.register_blueprint(main)
    app.register_blueprint(api)
    return app


real = create_app()
test = create_app({"TESTING": True, "SHOP_NAME": "Test Shop"})

print(real.test_client().get("/").get_data(as_text=True))
print(test.test_client().get("/").get_data(as_text=True))
print(test.test_client().get("/api/status").get_json())
print(real.test_client().get("/api/books").get_json())
for rule in sorted(real.url_map.iter_rules(), key=str):
    if rule.endpoint != "static":
        print(f"{rule.rule:14} -> {rule.endpoint}")
