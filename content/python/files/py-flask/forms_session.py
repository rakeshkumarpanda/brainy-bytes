# 3.1 Flask basics: routes, templates, forms and JSON
# Example "forms_session" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import base64

from flask import Flask, flash, get_flashed_messages, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = "change-me"          # signs the session cookie. In real apps read it from an environment variable

PAGE = """{% for message in get_flashed_messages() %}[{{ message }}] {% endfor %}
{% if session.user %}Logged in as {{ session.user }}{% else %}Please log in{% endif %}"""

USERS = {"ann": "pw123"}


@app.route("/")
def home():
    return render_template_string(PAGE)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("user", "").strip().lower()
        if USERS.get(name) == request.form.get("pw"):
            session["user"] = name
            flash("Welcome back!")
            return redirect(url_for("home"))        # Post, Redirect, Get: a refresh will not post again
        flash("Wrong name or password")
    return render_template_string(PAGE + '\n<form method="post">...</form>'), 200


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Bye")
    return redirect(url_for("home"))


client = app.test_client()                       # keeps cookies between requests, like a browser
print(client.get("/").get_data(as_text=True))
print("---")
r = client.post("/login", data={"user": "ann", "pw": "nope"})
print(r.status_code, r.get_data(as_text=True))
print("---")
r = client.post("/login", data={"user": "Ann", "pw": "pw123"})
print(r.status_code, "Location:", r.headers["Location"])
print(client.get("/").get_data(as_text=True))
print("---")
cookie = client.get_cookie("session")
data_part = cookie.value.split(".")[0]
print("anyone can read the cookie:", base64.urlsafe_b64decode(data_part + "=="))   # signed, NOT encrypted
r = client.get("/logout", follow_redirects=True)
print(r.get_data(as_text=True))
