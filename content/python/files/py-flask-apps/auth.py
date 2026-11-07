# 3.2 Real Flask apps: structure, database, login and tests
# Example "auth" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import functools

from flask import Blueprint, Flask, g, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

USERS = {}                                         # name -> password hash. A real app uses a database table.
auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.post("/register")
def register():
    name, password = request.form["name"], request.form["password"]
    if name in USERS:
        return {"error": f"{name} is already taken"}, 409
    if len(password) < 8:
        return {"error": "use at least 8 characters"}, 422
    USERS[name] = generate_password_hash(password, method="pbkdf2:sha256")
    return {"registered": name}, 201


@auth.post("/login")
def login():
    name, password = request.form["name"], request.form["password"]
    stored = USERS.get(name)
    if stored is None or not check_password_hash(stored, password):
        return {"error": "wrong name or password"}, 401     # do not say which one was wrong
    session.clear()
    session["user"] = name
    return redirect(url_for("orders"))


@auth.before_app_request                           # runs before EVERY request of the app
def load_user():
    g.user = session.get("user")


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("auth.login_page"))
        return view(*args, **kwargs)
    return wrapped


@auth.get("/login")
def login_page():
    return "please log in"


app = Flask(__name__)
app.secret_key = "dev only, read a long random key from the environment in production"
app.register_blueprint(auth)


@app.get("/orders")
@login_required
def orders():
    return {"user": g.user, "orders": [101, 102]}


client = app.test_client()
print(client.post("/auth/register", data={"name": "ann", "password": "short"}).get_json())
print(client.post("/auth/register", data={"name": "ann", "password": "correct horse"}).get_json())
print("stored:", USERS["ann"][:21] + "...", "(never the password itself)")
print(client.get("/orders").headers["Location"])
print(client.post("/auth/login", data={"name": "ann", "password": "wrong pass"}).get_json())
r = client.post("/auth/login", data={"name": "ann", "password": "correct horse"}, follow_redirects=True)
print(r.status_code, r.get_json())
same = generate_password_hash("correct horse", method="pbkdf2:sha256")
print("same password, different hash (salt):", same != USERS["ann"])
