# 3.1 Flask basics: routes, templates, forms and JSON
# Example "templates" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from flask import Flask, render_template
from jinja2 import DictLoader

app = Flask(__name__)

# In a real project these are files in a folder called templates/. Here they live in a dict.
app.jinja_loader = DictLoader({
    "base.html": """<html><title>{% block title %}Shop{% endblock %}</title>
<body>{% block body %}{% endblock %}</body></html>""",

    "books.html": """{% extends "base.html" %}
{% block title %}Books ({{ books|length }}){% endblock %}
{% block body %}<h1>Hello {{ user }}</h1>
<ul>{% for book in books %}
  <li>{{ loop.index }}. {{ book.title|upper }} ({{ book.year }}){% if book.year < 1900 %} classic{% endif %}</li>
{%- else %}<li>No books yet</li>{% endfor %}
</ul>{% endblock %}""",
})

BOOKS = [{"title": "Dune", "year": 1965}, {"title": "Emma", "year": 1815}]


@app.route("/books/<user>")
def books(user):
    return render_template("books.html", user=user, books=BOOKS)


@app.route("/empty")
def empty():
    return render_template("books.html", user="Bob", books=[])


client = app.test_client()
print(client.get("/books/Ann").get_data(as_text=True))
page = client.get("/books/<b>Ann").get_data(as_text=True)
print([line for line in page.split("\n") if "<h1>" in line][0])   # Jinja escaped the < and >
print(client.get("/empty").get_data(as_text=True))
