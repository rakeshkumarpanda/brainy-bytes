# 5.1 Django REST framework: JSON APIs on top of Django
# Example "serializers_views" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import logging
import os

import django
from django.apps import AppConfig
from django.conf import settings


class ShopConfig(AppConfig):
    name = "__main__"
    label = "shop"
    path = os.getcwd()


settings.configure(
    DEBUG=True,
    SECRET_KEY="dev-only",
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=["testserver"],
    INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth", "rest_framework", "__main__.ShopConfig"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    REST_FRAMEWORK={"UNAUTHENTICATED_USER": None},          # no login in this first example
)
django.setup()
logging.getLogger("django.request").setLevel(logging.ERROR)

from django.db import connection, models
from django.urls import path
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.test import APIClient


class Book(models.Model):
    title = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)


with connection.schema_editor() as editor:
    editor.create_model(Book)
Book.objects.create(title="Dune", year=1965, price="9.99")


# ---------- serializers.py: Python objects to JSON and back, with validation ----------
class BookSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()                # an extra, read only value

    class Meta:
        model = Book
        fields = ["id", "title", "year", "price", "age"]

    def get_age(self, book):
        return 2026 - book.year

    def validate_year(self, value):                          # like clean_year in a form
        if value > 2026:
            raise serializers.ValidationError("The year is in the future.")
        return value


# 1. Serialize: a model object becomes a dict that is ready for JSON
print("to JSON:", BookSerializer(Book.objects.get(title="Dune")).data)

# 2. Deserialize: incoming data is checked before anything is saved
bad = BookSerializer(data={"title": "", "year": 3000, "price": "abc"})
print("valid?", bad.is_valid(), "errors:", {k: [str(e) for e in v] for k, v in bad.errors.items()})


# ---------- views.py: @api_view handles content types, status codes and errors ----------
@api_view(["GET", "POST"])
def book_list(request):
    if request.method == "GET":
        return Response(BookSerializer(Book.objects.order_by("id"), many=True).data)
    serializer = BookSerializer(data=request.data)           # request.data reads JSON, forms and files
    serializer.is_valid(raise_exception=True)                # sends 400 with the errors when invalid
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "DELETE"])
def book_detail(request, pk):
    book = Book.objects.filter(pk=pk).first()
    if book is None:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    if request.method == "DELETE":
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(BookSerializer(book).data)


urlpatterns = [path("api/books/", book_list), path("api/books/<int:pk>/", book_detail)]

client = APIClient()
for method, url, body in [
    ("get", "/api/books/", None),
    ("post", "/api/books/", {"title": "Emma", "year": 1815, "price": "5.00"}),
    ("post", "/api/books/", {"title": "Future", "year": 2999, "price": "1.00"}),
    ("get", "/api/books/2/", None),
    ("delete", "/api/books/2/", None),
    ("get", "/api/books/2/", None),
    ("put", "/api/books/", {}),
]:
    response = getattr(client, method)(url, body, format="json")
    body = response.json() if response.content else None    # the JSON text the client really receives
    print(f"{method.upper():6} {url:16} {response.status_code} {body}")
