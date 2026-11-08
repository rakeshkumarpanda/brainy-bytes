# 5.1 Django REST framework: JSON APIs on top of Django
# Example "nested_tests" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os
import sys
import unittest

import django
from django.apps import AppConfig
from django.conf import settings


class ShopConfig(AppConfig):
    name = "__main__"
    label = "shop"
    path = os.getcwd()


settings.configure(
    SECRET_KEY="dev-only",
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=["testserver"],
    INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth", "rest_framework", "__main__.ShopConfig"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    REST_FRAMEWORK={"UNAUTHENTICATED_USER": None},
)
django.setup()

from django.db import connection, models, transaction
from django.urls import include, path
from rest_framework import serializers, viewsets
from rest_framework.routers import DefaultRouter
from rest_framework.test import APITestCase


class Author(models.Model):
    name = models.CharField(max_length=100)


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")


with connection.schema_editor() as editor:
    editor.create_model(Author)
    editor.create_model(Book)


class BookInAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title"]


class AuthorSerializer(serializers.ModelSerializer):
    books = BookInAuthorSerializer(many=True)               # nested: the books inside each author
    book_count = serializers.IntegerField(source="books.count", read_only=True)

    class Meta:
        model = Author
        fields = ["id", "name", "book_count", "books"]

    def create(self, validated_data):                       # nested writes are yours to write
        books = validated_data.pop("books")
        with transaction.atomic():                          # the author and the books together, or nothing
            author = Author.objects.create(**validated_data)
            for book in books:
                Book.objects.create(author=author, **book)
        return author


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.prefetch_related("books").order_by("id")   # no N + 1 for the nested books
    serializer_class = AuthorSerializer


router = DefaultRouter()
router.register("authors", AuthorViewSet)
urlpatterns = [path("api/", include(router.urls))]


# ---------- tests.py: APITestCase gives self.client (an APIClient) and a rollback after each test ----------
class AuthorApiTests(APITestCase):
    def test_create_author_with_books(self):
        body = {"name": "Jane Austen", "books": [{"title": "Emma"}, {"title": "Persuasion"}]}
        response = self.client.post("/api/authors/", body, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["book_count"], 2)
        self.assertEqual(Book.objects.count(), 2)

    def test_book_needs_a_title(self):
        response = self.client.post("/api/authors/", {"name": "X", "books": [{"title": ""}]}, format="json")
        self.assertEqual(response.status_code, 400)
        errors = response.json()["books"]                    # the errors of book number 0 in the list
        self.assertEqual(errors, {"0": {"title": ["This field may not be blank."]}})
        self.assertEqual(Author.objects.count(), 0)          # nothing was saved

    def test_list_uses_two_queries(self):
        for i in range(5):
            author = Author.objects.create(name=f"Author {i}")
            Book.objects.create(title=f"Book {i}", author=author)
        with self.assertNumQueries(2):     # authors, then all books at once (count() uses the prefetched rows)
            response = self.client.get("/api/authors/")
        self.assertEqual(len(response.json()), 5)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(AuthorApiTests)
result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
print("all passed" if result.wasSuccessful() else "some tests failed")
