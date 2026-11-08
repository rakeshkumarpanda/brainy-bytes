# 5.1 Django REST framework: JSON APIs on top of Django
# Example "viewsets_routers" from the lesson.
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
    REST_FRAMEWORK={
        "UNAUTHENTICATED_USER": None,
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 2,
    },
)
django.setup()
logging.getLogger("django.request").setLevel(logging.ERROR)

from django.db import connection, models
from django.urls import include, path
from rest_framework import filters, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.test import APIClient


class Author(models.Model):
    name = models.CharField(max_length=100)


class Book(models.Model):
    title = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")


with connection.schema_editor() as editor:
    editor.create_model(Author)
    editor.create_model(Book)
herbert, austen = Author.objects.create(name="Frank Herbert"), Author.objects.create(name="Jane Austen")
for title, year, author in [("Dune", 1965, herbert), ("Emma", 1815, austen), ("Dune Messiah", 1969, herbert),
                            ("Persuasion", 1817, austen), ("Children of Dune", 1976, herbert)]:
    Book.objects.create(title=title, year=year, author=author)


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True)   # read from the related row

    class Meta:
        model = Book
        fields = ["id", "title", "year", "author", "author_name"]


# ---------- One ViewSet gives list, create, retrieve, update, partial_update and destroy ----------
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("author").order_by("id")
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "author__name"]               # ?search=dune
    ordering_fields = ["year", "title"]                     # ?ordering=-year

    def get_queryset(self):                                 # a filter of your own: ?after=1900
        queryset = super().get_queryset()
        after = self.request.query_params.get("after")
        return queryset.filter(year__gt=int(after)) if after and after.isdigit() else queryset

    @action(detail=False)                                   # an extra URL: /api/books/oldest/
    def oldest(self, request):
        return Response(BookSerializer(self.get_queryset().order_by("year").first()).data)


router = DefaultRouter()
router.register("books", BookViewSet)                       # makes all the URL patterns
urlpatterns = [path("api/", include(router.urls))]
print("URL names made by the router:", sorted({p.name for p in router.urls}))

client = APIClient()


def show(method, url, body=None):
    response = getattr(client, method)(url, body, format="json")
    data = response.json() if response.content else None
    if isinstance(data, dict) and "results" in data:        # a page: show the count, the links and the titles
        data = {"count": data["count"], "next": data["next"], "titles": [b["title"] for b in data["results"]]}
    print(f"{method.upper():6} {url:40} {response.status_code} {data}")


show("get", "/api/books/")
show("get", "/api/books/?page=3")
show("get", "/api/books/?search=dune&ordering=-year")
show("get", "/api/books/?after=1900&ordering=title")
show("get", "/api/books/oldest/")
show("patch", "/api/books/2/", {"year": 1816})
show("post", "/api/books/", {"title": "Sense and Sensibility", "year": 1811, "author": austen.id})
show("delete", "/api/books/1/")
show("get", "/api/books/1/")
