# 6.2 Web revision exam: HTTP, Flask, Django, FastAPI and security
# Example "paper_c" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import logging
import os

import django
from django.apps import AppConfig
from django.conf import settings


class ExamConfig(AppConfig):
    name = "__main__"
    label = "exam"
    path = os.getcwd()


settings.configure(
    DEBUG=False, SECRET_KEY="exam-only", ROOT_URLCONF=__name__, ALLOWED_HOSTS=["testserver"],
    INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth", "rest_framework", "__main__.ExamConfig"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    REST_FRAMEWORK={"UNAUTHENTICATED_USER": None},
)
django.setup()
logging.getLogger("django.request").setLevel(logging.ERROR)

from django.db import connection, models
from django.db.models import Count, F, Q
from django.http import JsonResponse
from django.template import Context, Engine
from django.urls import path, resolve, reverse
from rest_framework import serializers
from rest_framework.test import APIClient


class Author(models.Model):
    name = models.CharField(max_length=50)


class Book(models.Model):
    title = models.CharField(max_length=100)
    year = models.IntegerField()
    stock = models.IntegerField(default=0)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")


with connection.schema_editor() as editor:
    editor.create_model(Author)
    editor.create_model(Book)
ann = Author.objects.create(name="Ann")
bob = Author.objects.create(name="Bob")
for title, year, stock, who in [("Emma", 1815, 3, ann), ("Dune", 1965, 0, bob), ("Ubik", 1969, 5, bob)]:
    Book.objects.create(title=title, year=year, stock=stock, author=who)


def book_detail(request, pk):
    return JsonResponse({"pk": pk})


urlpatterns = [path("books/<int:pk>/", book_detail, name="book-detail")]

qs = Book.objects.filter(year__gt=1900)
print("Q1", type(qs).__name__, qs.count(), list(qs.values_list("title", flat=True)))

print("Q2", Book.objects.filter(Q(stock=0) | Q(author__name="Ann")).order_by("title").values_list("title", flat=True)[:5])

Book.objects.filter(stock__gt=0).update(stock=F("stock") - 1)
print("Q3", list(Book.objects.order_by("id").values_list("stock", flat=True)))

counts = Author.objects.annotate(n=Count("books")).order_by("-n").values_list("name", "n")
print("Q4", list(counts))

print("Q5", "JOIN" in str(Book.objects.filter(author__name="Bob").query), str(Book.objects.all().query).count("SELECT"))

print("Q6", reverse("book-detail", args=[7]), resolve("/books/7/").kwargs, resolve("/books/7/").url_name)

tpl = Engine().from_string("{% for b in books %}{{ b|upper }}{% if not forloop.last %}, {% endif %}{% empty %}none{% endfor %} {{ html }}")
print("Q7", tpl.render(Context({"books": ["emma", "dune"], "html": "<b>hi</b>"})))


class BookSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=10)
    year = serializers.IntegerField(min_value=1450)
    stock = serializers.IntegerField(required=False, default=0)


s = BookSerializer(data={"title": "A very long title", "year": "1200"})
print("Q8", s.is_valid(), sorted(s.errors))
s = BookSerializer(data={"title": "Emma", "year": "1815"})
print("Q9", s.is_valid(), dict(s.validated_data))

r = APIClient().get("/books/42/")
print("Q10", r.status_code, r.json(), APIClient().get("/books/x/").status_code)
