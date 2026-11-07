# 4.1 Django basics: project, URLs, views, templates, models and admin
# Model solutions. Try practice.py first.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: Write the views and URLs of a book shop
# The settings and the home page are ready. Write two views and add them to urlpatterns. book_list
# at /books/ answers {"count": ..., "titles": [...]} with the titles sorted A to Z. With ?after=YEAR
# it keeps only books newer than that year, and when YEAR is not a number it answers 400 with
# {"error": "after must be a year"}. book_detail at /books/<int:book_id>/ answers the book, or 404
# with {"error": "not found"}. Name the URLs "book-list" and "book-detail". visit(url) sends a GET
# with the test client and returns [status, json].
# Why it works: /books without the slash gives 301 because CommonMiddleware adds the slash. Raising
# Http404 would also give 404, but with an HTML page, so a JSON API returns its own JSON error
# instead. Step 5 shows Django REST framework, which does this work for you.

import logging

import django
from django.conf import settings

settings.configure(DEBUG=True, SECRET_KEY="dev-only", ROOT_URLCONF=__name__, ALLOWED_HOSTS=["testserver"],
                   MIDDLEWARE=["django.middleware.common.CommonMiddleware"])
django.setup()
logging.getLogger("django.request").setLevel(logging.ERROR)   # hide the request log lines

from django.http import JsonResponse
from django.test import Client
from django.urls import path, reverse

STOCK = [
    {"id": 1, "title": "Dune", "year": 1965},
    {"id": 2, "title": "Emma", "year": 1815},
    {"id": 3, "title": "Hamlet", "year": 1603},
]


def home(request):
    return JsonResponse({"shop": "Django books"})


def book_list(request):
    books = STOCK
    after = request.GET.get("after")
    if after is not None:
        if not after.isdigit():
            return JsonResponse({"error": "after must be a year"}, status=400)
        books = [book for book in books if book["year"] > int(after)]
    titles = sorted(book["title"] for book in books)
    return JsonResponse({"count": len(titles), "titles": titles})


def book_detail(request, book_id):
    for book in STOCK:
        if book["id"] == book_id:
            return JsonResponse(book)
    return JsonResponse({"error": "not found"}, status=404)


urlpatterns = [
    path("", home, name="home"),
    path("books/", book_list, name="book-list"),
    path("books/<int:book_id>/", book_detail, name="book-detail"),
]


def visit(url):
    response = Client().get(url)
    try:
        body = response.json()
    except ValueError:
        body = None
    return [response.status_code, body]


# ================================================================== task 2: Write three Django template filters yourself
# Django templates have filters such as {{ title|slugify }}. Write them as plain functions.
# slugify_text(value): change accented letters to plain ones (é becomes e), use lower case, remove
# everything that is not a letter, digit, underscore, space or hyphen, turn each run of spaces and
# hyphens into one hyphen, and strip hyphens and underscores at both ends. truncate_words(value,
# count): keep the first count words and add " ..." when words were cut. pluralize(number,
# suffix="s"): "" for 1 and suffix otherwise, and with a suffix such as "y,ies" the part before the
# comma for 1 and the part after it for every other number.
# Why it works: This is almost exactly how django.utils.text.slugify works, and a real run of Django
# gave the same five slugs. Django's truncatewords adds the single character … instead of three
# dots. Slugs make readable URLs such as /books/creme-brulee/.

import re
import unicodedata


def slugify_text(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def truncate_words(value, count):
    words = value.split()
    if len(words) <= count:
        return " ".join(words)
    return " ".join(words[:count]) + " ..."


def pluralize(number, suffix="s"):
    if "," in suffix:
        one, many = suffix.split(",")
    else:
        one, many = "", suffix
    return one if number == 1 else many


# ================================================================== task 3: Build a tiny QuerySet
# Write the class MiniQuerySet(rows) over a list of dicts, with the same feel as the Django ORM.
# filter(**lookups) and exclude(**lookups) return a new MiniQuerySet. A key is a field name, maybe
# followed by __ and a lookup: exact (the default), gt, gte, lt, lte, in, startswith and icontains.
# Every lookup in one call must match. An unknown lookup raises ValueError. order_by(*fields) sorts
# by several fields, and a leading "-" means largest first. values_list, count and first are ready.
# Why it works: The real QuerySet does not filter Python lists. It builds an SQL query step by step
# and runs it only when you read the results, which is called lazy evaluation. Chapter 4.2 shows
# that, with the SQL Django writes.

LOOKUPS = {
    "exact": lambda value, wanted: value == wanted,
    "gt": lambda value, wanted: value > wanted,
    "gte": lambda value, wanted: value >= wanted,
    "lt": lambda value, wanted: value < wanted,
    "lte": lambda value, wanted: value <= wanted,
    "in": lambda value, wanted: value in wanted,
    "startswith": lambda value, wanted: str(value).startswith(wanted),
    "icontains": lambda value, wanted: str(wanted).lower() in str(value).lower(),
}


class MiniQuerySet:
    def __init__(self, rows):
        self.rows = list(rows)

    def _matches(self, row, lookups):
        for key, wanted in lookups.items():
            field, _, lookup = key.partition("__")
            lookup = lookup or "exact"
            if lookup not in LOOKUPS:
                raise ValueError(f"unknown lookup {lookup!r}")
            if not LOOKUPS[lookup](row[field], wanted):
                return False
        return True

    def filter(self, **lookups):
        return MiniQuerySet(row for row in self.rows if self._matches(row, lookups))

    def exclude(self, **lookups):
        return MiniQuerySet(row for row in self.rows if not self._matches(row, lookups))

    def order_by(self, *fields):
        rows = list(self.rows)
        for field in reversed(fields):            # sort by the last field first, sorted() keeps ties in order
            reverse = field.startswith("-")
            name = field.lstrip("-")
            rows = sorted(rows, key=lambda row: row[name], reverse=reverse)
        return MiniQuerySet(rows)

    def values_list(self, field):
        return [row[field] for row in self.rows]

    def count(self):
        return len(self.rows)

    def first(self):
        return self.rows[0] if self.rows else None


BOOKS = [
    {"title": "Dune", "year": 1965, "genre": "sf", "price": 9},
    {"title": "Emma", "year": 1815, "genre": "novel", "price": 5},
    {"title": "Dune Messiah", "year": 1969, "genre": "sf", "price": 8},
    {"title": "Hamlet", "year": 1603, "genre": "play", "price": 5},
    {"title": "Neuromancer", "year": 1984, "genre": "sf", "price": 9},
]


def query_error(lookup):
    try:
        MiniQuerySet(BOOKS).filter(**{lookup: 1})
    except ValueError:
        return "ValueError"
    return "no error"


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Write the views and URLs of a book shop", [('visit("/")', [200, {'shop': 'Django books'}]), ('visit("/books/")', [200, {'count': 3, 'titles': ['Dune', 'Emma', 'Hamlet']}]), ('visit("/books/?after=1700")', [200, {'count': 2, 'titles': ['Dune', 'Emma']}]), ('visit("/books/?after=old")', [400, {'error': 'after must be a year'}]), ('visit("/books/2/")', [200, {'id': 2, 'title': 'Emma', 'year': 1815}]), ('visit("/books/9/")', [404, {'error': 'not found'}]), ('visit("/books")', [301, None]), ('[reverse("book-list"), reverse("book-detail", args=[3])]', ['/books/', '/books/3/'])]))
    results.append(check("Task 2: Write three Django template filters yourself", [('slugify_text("Hello World!")', 'hello-world'), ('slugify_text("  Django  is   fun ")', 'django-is-fun'), ('slugify_text("Crème brûlée")', 'creme-brulee'), ('slugify_text("C\'est la vie - 2026")', 'cest-la-vie-2026'), ('slugify_text("--Top_10 books--")', 'top_10-books'), ('truncate_words("The quick brown fox jumps", 3)', 'The quick brown ...'), ('truncate_words("Short title", 5)', 'Short title'), ('truncate_words("  many   spaces here ", 2)', 'many spaces ...'), ('[pluralize(1), pluralize(2), pluralize(0)]', ['', 's', 's']), ('[pluralize(1, "es"), pluralize(3, "es")]', ['', 'es']), ('[pluralize(1, "y,ies"), pluralize(4, "y,ies")]', ['y', 'ies'])]))
    results.append(check("Task 3: Build a tiny QuerySet", [('MiniQuerySet(BOOKS).filter(genre="sf").values_list("title")', ['Dune', 'Dune Messiah', 'Neuromancer']), ('MiniQuerySet(BOOKS).filter(year__gte=1900, price__lt=9).values_list("title")', ['Dune Messiah']), ('MiniQuerySet(BOOKS).exclude(genre="sf").order_by("-year").values_list("title")', ['Emma', 'Hamlet']), ('MiniQuerySet(BOOKS).order_by("price", "-year").values_list("title")', ['Emma', 'Hamlet', 'Dune Messiah', 'Neuromancer', 'Dune']), ('MiniQuerySet(BOOKS).filter(title__icontains="DUNE").count()', 2), ('MiniQuerySet(BOOKS).filter(genre__in=["play", "novel"]).order_by("year").first()["title"]', 'Hamlet'), ('MiniQuerySet(BOOKS).filter(title__startswith="Z").first()', None), ('query_error("year__between")', 'ValueError')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
