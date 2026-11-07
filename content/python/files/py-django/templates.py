# 4.1 Django basics: project, URLs, views, templates, models and admin
# Example "templates" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import datetime

import django
from django.conf import settings

# In a project the templates are files in books/templates/books/. Here they live in a dict.
TEMPLATE_FILES = {
    "base.html": (
        "<title>{% block title %}Book shop{% endblock %}</title>\n"
        "<nav><a href=\"{% url 'home' %}\">Home</a></nav>\n"
        "{% block content %}{% endblock %}"
    ),
    "books/list.html": (
        "{% extends 'base.html' %}\n"
        "{% block title %}{{ books|length }} books{% endblock %}\n"
        "{% block content %}<h1>Hello {{ user_name|default:'guest'|title }}</h1>\n"
        "<ul>{% for book in books %}\n"
        "  <li>{{ forloop.counter }}. {{ book.title }}{% if book.year < 1900 %} (classic){% endif %}"
        " {{ book.price|floatformat:2 }}</li>"
        "{% empty %}\n  <li>No books yet</li>{% endfor %}\n</ul>\n"
        "<p>Updated {{ updated|date:'j M Y' }}. Note: {{ note }}</p>{% endblock %}"
    ),
}

settings.configure(
    DEBUG=True,
    SECRET_KEY="dev-only",
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=["testserver"],
    INSTALLED_APPS=[],
    TEMPLATES=[{
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {"loaders": [("django.template.loaders.locmem.Loader", TEMPLATE_FILES)]},
    }],
)
django.setup()

from django.shortcuts import render
from django.test import Client
from django.urls import path


def home(request):
    return render(request, "books/list.html", {"books": []})


def book_list(request):
    context = {
        "books": [
            {"title": "Emma", "year": 1815, "price": 5},
            {"title": "Dune", "year": 1965, "price": 9.5},
        ],
        "user_name": request.GET.get("name", ""),
        "updated": datetime.date(2026, 11, 7),
        "note": "<script>alert('hi')</script>",              # escaped, so it is shown as text
    }
    return render(request, "books/list.html", context)


urlpatterns = [path("", home, name="home"), path("books/", book_list, name="book-list")]

client = Client()
print(client.get("/books/?name=ann lee").content.decode())
print("-----")
print(client.get("/").content.decode())
