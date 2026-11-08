# Web and APIs 5.1: Django REST framework. Checked against the DRF 3.18 documentation (tutorial parts 1 to 6,
# serializers, ModelSerializer, validators, requests and responses, function and class views, generic views and
# mixins, viewsets and routers, authentication, permissions, throttling, filtering, pagination, testing, status
# codes) and real runs of DRF 3.18.3 with Django 6.1.3 on Python 3.14. Every program runs in the page.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, lc, leet, files, grow, leet_items

chapter('py-drf')
K = Kit()

K.code('serializers_views', r'''
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
    print(f"{method.upper():6} {url:16} {response.status_code} {body}")''', long=True)
K.code('viewsets_routers', r'''
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
show("get", "/api/books/1/")''', long=True)
K.code('auth_permissions', r'''
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
    INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth", "rest_framework",
                    "rest_framework.authtoken", "__main__.ShopConfig"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.TokenAuthentication"],
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
        "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
        "DEFAULT_THROTTLE_RATES": {"anon": "3/minute"},
    },
)
django.setup()
logging.getLogger("django.request").setLevel(logging.ERROR)

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection, models
from django.urls import include, path
from rest_framework import permissions, serializers, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from rest_framework.test import APIClient

call_command("migrate", verbosity=0)                       # users and tokens


class Note(models.Model):
    text = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


with connection.schema_editor() as editor:
    editor.create_model(Note)


class IsOwnerOrReadOnly(permissions.BasePermission):        # a permission of your own, checked per object
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.owner == request.user


class NoteSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Note
        fields = ["id", "text", "owner"]


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.order_by("id")
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):                   # the owner comes from the token, never from the body
        serializer.save(owner=self.request.user)


router = DefaultRouter()
router.register("notes", NoteViewSet)
urlpatterns = [path("api/", include(router.urls)), path("api/token/", obtain_auth_token)]

User.objects.create_user("ann", password="ann secret 123")
User.objects.create_user("bob", password="bob secret 456")


def show(label, response):
    print(f"{label:34} {response.status_code} {response.json() if response.content else None}")


anon = APIClient()
show("anon POST /api/notes/", anon.post("/api/notes/", {"text": "hi"}, format="json"))
show("anon POST /api/token/ (wrong pw)", anon.post("/api/token/", {"username": "ann", "password": "nope"}, format="json"))
token = anon.post("/api/token/", {"username": "ann", "password": "ann secret 123"}, format="json").json()["token"]
print("ann's token:", token[:8] + "...", "stored:", Token.objects.filter(user__username="ann").exists())

ann = APIClient()
ann.credentials(HTTP_AUTHORIZATION="Token " + token)       # sent with every request from now on
show("ann POST /api/notes/", ann.post("/api/notes/", {"text": "buy milk", "owner": "bob"}, format="json"))

bob = APIClient()
bob.force_authenticate(User.objects.get(username="bob"))    # a test shortcut: no token needed
show("bob GET /api/notes/1/", bob.get("/api/notes/1/"))
show("bob DELETE /api/notes/1/", bob.delete("/api/notes/1/"))
show("ann PATCH /api/notes/1/", ann.patch("/api/notes/1/", {"text": "buy oat milk"}, format="json"))

throttled = APIClient()
for i in range(4):                                          # anonymous users may make 3 requests a minute
    response = throttled.get("/api/notes/")
    print(f"anon GET #{i + 1}: {response.status_code}", response.get("Retry-After", ""))''', long=True)
K.code('nested_tests', r'''
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
print("all passed" if result.wasSuccessful() else "some tests failed")''', long=True)

PLAY = '''

def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results
'''

K.lesson('idea', 'What Django REST framework adds', f'''
{src('Django REST framework 3.18 documentation: tutorial, serializers, views, generic views, viewsets and routers, authentication, permissions, throttling, filtering, pagination, status codes and testing.')}
{wwh('<b>Django REST framework</b> (DRF) is a library on top of Django for building <b>JSON APIs</b>. It adds serializers that turn models into JSON and check incoming JSON, views and ViewSets made for APIs, routers that write the URLs, and ready parts for logins, permissions, rate limits, filters and pages.',
     'A mobile app or a JavaScript front end does not want HTML pages, it wants JSON. With plain Django you would parse JSON by hand, check every field, turn objects into dicts, pick status codes and write the same list, create, read, update and delete views for every model.',
     'A <b>serializer</b> does for JSON what a form does for HTML: it checks the input and gives clean data, and it turns objects into dicts. A <b>ModelViewSet</b> plus a <b>router</b> gives all the usual endpoints of a model in a few lines, and settings switch on token logins, permissions, throttles and pagination for every view.')}
{viz('pydrf')}
{versus('Building a JSON API in Python', ['', 'Plain Django views', 'Django REST framework', 'FastAPI'], [
    ['Input checks', 'By hand or with forms', 'Serializers', 'Pydantic models from type hints'],
    ['CRUD endpoints', 'Write each view', 'ModelViewSet and a router', 'Write each function'],
    ['Logins, permissions, limits', 'Django sessions only', 'Token, session, JWT (add on), permissions, throttles', 'Dependencies you write or add'],
    ['Docs', 'None', 'Browsable API, OpenAPI with an add on', 'OpenAPI and Swagger UI built in'],
    ['Good for', 'One or two JSON endpoints', 'APIs on top of a Django project and its models', 'New API only services, async work']],
    'Pick DRF when you already have Django models and the admin. Pick FastAPI (chapter 5.2) for a new, API only service.')}
''', kw=['Django REST framework', 'DRF', 'REST API', 'JSON', 'serializer', 'ViewSet', 'router', 'FastAPI'])

K.lesson('serializers', 'Serializers and API views', f'''
{run('serializers_views')}
{table(['Serializer part', 'What it does'], [
    ['ModelSerializer with Meta.model and Meta.fields', 'Makes the fields from the model, with its rules'],
    ['serializer.data', 'Object to dict, ready to become JSON'],
    ['Serializer(data=...).is_valid()', 'Checks incoming data. errors holds the messages, validated_data the clean values'],
    ['validate_&lt;field&gt;(self, value)', 'A rule for one field'],
    ['validate(self, data)', 'A rule for several fields. Errors go to non_field_errors'],
    ['SerializerMethodField', 'A read only value from a get_&lt;name&gt; method'],
    ['read_only=True, write_only=True', 'Shown but never written, or accepted but never shown (passwords)'],
    ['save()', 'Calls create() or update(), which you can override']])}
{steps('What the example shows', [
    'BookSerializer(book).data turned a model object into a dict, with the extra age field.',
    'Bad data gave one message per field, before anything touched the database.',
    '<b>@api_view</b> reads request.data from JSON, returns Response objects and answers 405 for other methods.',
    'is_valid(raise_exception=True) turned the validation error into a 400 answer by itself.',
    'The status codes follow REST: 200 read, 201 created, 204 deleted, 400 bad input, 404 missing, 405 wrong method.'])}
{note('Response(data) is not JSON yet. The renderer turns it into JSON for programs and into the browsable HTML page for a person with a browser. That page lets you try the API by hand.', 'tip')}
''', kw=['serializer', 'ModelSerializer', 'is_valid', 'validated_data', 'validate', 'SerializerMethodField', 'api_view', 'Response', 'request.data', 'status codes'])

K.lesson('viewsets', 'ViewSets, routers, filters and pages', f'''
{run('viewsets_routers')}
{table(['HTTP request', 'ViewSet action', 'Answer'], [
    ['GET /api/books/', 'list', '200, a page of books'],
    ['POST /api/books/', 'create', '201, the new book'],
    ['GET /api/books/7/', 'retrieve', '200 or 404'],
    ['PUT /api/books/7/', 'update', '200, every field replaced'],
    ['PATCH /api/books/7/', 'partial_update', '200, only the fields sent'],
    ['DELETE /api/books/7/', 'destroy', '204, empty body'],
    ['GET /api/books/oldest/', '@action(detail=False)', 'Your own extra endpoint']])}
{versus('Three levels of DRF views', ['', 'APIView or @api_view', 'Generic views', 'ViewSets'], [
    ['You write', 'Each method yourself', 'queryset and serializer_class', 'queryset and serializer_class'],
    ['Example', 'def get(self, request)', 'ListCreateAPIView', 'ModelViewSet'],
    ['URLs', 'path() for each', 'path() for each', 'One router.register'],
    ['Good for', 'Special endpoints', 'A few endpoints', 'Full CRUD of a model']],
    'Start with a ModelViewSet for each model. Override get_queryset, perform_create or one action when you need something special, and write an APIView only for endpoints that do not fit.')}
{note('SearchFilter and OrderingFilter come with DRF. For filters such as ?year=1965&amp;author=2, the django-filter add on reads them from a filterset_fields list. Always order the queryset, otherwise pages can show a row twice.', 'exam')}
''', kw=['ViewSet', 'ModelViewSet', 'router', 'DefaultRouter', 'action', 'get_queryset', 'SearchFilter', 'OrderingFilter', 'pagination', 'PageNumberPagination', 'generic views'])

K.lesson('auth', 'Authentication, permissions and throttling', f'''
{run('auth_permissions')}
{table(['Setting or class', 'Job'], [
    ['TokenAuthentication', 'Reads "Authorization: Token ..." and finds the user'],
    ['SessionAuthentication', 'Uses the Django login cookie, for a front end on the same site (needs CSRF)'],
    ['JWT (djangorestframework-simplejwt)', 'Signed tokens that expire, no database lookup per request'],
    ['IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser', 'Who may use the view'],
    ['has_object_permission', 'Rules for one object, such as "only the owner may change it"'],
    ['AnonRateThrottle, UserRateThrottle', 'Limits such as 100/hour per IP or per user, answered with 429'],
    ['perform_create(serializer)', 'Adds server side values such as owner=request.user']])}
{versus('401 and 403', ['', '401 Unauthorized', '403 Forbidden'], [
    ['Means', 'We do not know who you are', 'We know who you are, and you may not'],
    ['Example', 'No token, or a wrong token', 'Bob deletes ann&#39;s note'],
    ['The client should', 'Log in and try again', 'Not try again']],
    'DRF picks the right one: no credentials give 401, credentials without the right permission give 403.')}
{note('Never trust ids or owners from the request body. The example ignores "owner": "bob" in the body and sets the owner from the token in perform_create. Mark such fields read only in the serializer.', 'tip')}
''', kw=['authentication', 'TokenAuthentication', 'JWT', 'SessionAuthentication', 'permissions', 'IsAuthenticatedOrReadOnly', 'has_object_permission', 'throttling', '429', '401', '403', 'perform_create'])

K.lesson('nested', 'Nested data and API tests', f'''
{run('nested_tests')}
{steps('What the example shows', [
    'A serializer can hold another serializer: each author shows its books inside it.',
    'DRF does not save nested data by itself. The create() method saves the author and the books inside transaction.atomic(), so a bad book saves nothing.',
    'prefetch_related("books") makes the list two queries for any number of authors, and assertNumQueries(2) keeps it that way.',
    'An error in book number 0 comes back under its index: &#123;"books": &#123;"0": &#123;"title": [...]&#125;&#125;&#125;.',
    '<b>APITestCase</b> gives self.client, an APIClient, and rolls back the database after every test.'])}
{table(['Way to show a relation', 'Gives', 'Good for'], [
    ['PrimaryKeyRelatedField (the default)', '"author": 2', 'Small answers, the client looks up more if needed'],
    ['StringRelatedField or source="author.name"', '"author": "Jane Austen"', 'Showing a name, read only'],
    ['A nested serializer', '"author": &#123;"id": 2, "name": ...&#125;', 'Fewer requests for the client'],
    ['HyperlinkedRelatedField', '"author": "http://.../authors/2/"', 'APIs that link resources together']])}
''', kw=['nested serializer', 'relations', 'PrimaryKeyRelatedField', 'HyperlinkedRelatedField', 'APITestCase', 'APIClient', 'force_authenticate', 'transaction.atomic', 'prefetch_related'])

K.lesson('design', 'Designing a good API', f'''
{table(['Rule', 'Good', 'Avoid'], [
    ['Nouns in URLs, HTTP methods as verbs', 'POST /api/orders/', 'POST /api/createOrder'],
    ['Plural names, ids in the path', '/api/books/7/', '/api/book?id=7'],
    ['Filters, search and order in the query string', '/api/books/?author=2&amp;ordering=-year', 'A different URL for each filter'],
    ['Always paginate lists', 'count, next, previous, results', 'Returning 100,000 rows'],
    ['Use the right status code', '201 with the new object, 204 after delete', '200 with &#123;"error": ...&#125;'],
    ['Same error shape everywhere', '&#123;"field": ["message"]&#125; or &#123;"detail": "..."&#125;', 'Plain text errors'],
    ['Version when you break things', '/api/v2/ or an Accept header', 'Changing fields under existing clients'],
    ['Make retries safe', 'PUT and DELETE are idempotent, POST can take an Idempotency-Key', 'Charging a card twice on retry']])}
{scene('a mobile app and a shop', '<p>A shop has a Django site with the admin for staff. The new mobile app needs the same products and orders. The team adds DRF: a ModelViewSet for products (read only for everyone), one for orders (only the owner, token login), pagination of 20, and a throttle of 60 requests a minute per user. The admin and the web pages keep working on the same models, and the tests check every endpoint with APIClient.</p>')}
''', kw=['REST design', 'resources', 'status codes', 'pagination', 'versioning', 'idempotency', 'errors'])

K.lesson('maths', 'The maths: pages, limits and payload size', f'''
{fxs(fx('Number of pages', 'pages = &lceil; count / page size &rceil;', '5 books at 2 a page: &lceil;2.5&rceil; = 3 pages.', key=True),
     fx('Requests allowed', 'rate = requests / window', '3/minute: the 4th request in 60 s gets 429.', key=True),
     fx('Wait time in a sliding window', 'Retry-After = oldest + window &minus; now', 'Requests at 0, 10 and 20 s, a 4th at 30 s: 0 + 60 &minus; 30 = 30 s.', key=True),
     fx('Requests per day at a limit', 'per day = rate &times; windows per day', '100/hour: 100 &times; 24 = 2,400 a day.'),
     fx('Payload size', 'bytes &asymp; rows &times; bytes per row', '20 books of 120 bytes: 2,400 bytes. All 50,000: 6 MB.'),
     fx('Requests to read everything', 'requests = &lceil; count / page size &rceil;', '50,000 rows at 100 a page: 500 requests.'))}
{steps('Worked example: choosing a page size', [
    'A list has 50,000 books of about 120 bytes each in JSON.',
    'Without pages one answer is 50,000 &times; 120 = 6,000,000 bytes, about 6 MB, too much for a phone.',
    'At 20 per page an answer is 2,400 bytes, and the first screen appears at once.',
    'A client that really needs everything makes &lceil;50,000 / 100&rceil; = 500 requests at a page size of 100, so allow a larger page_size (with max_page_size) for such clients.',
    eq('small pages for people, larger pages with a limit for programs')])}
''', kw=['pagination', 'rate limit', 'Retry-After', 'sliding window', 'payload size', 'page size'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Write a ModelSerializer and @api_view functions, and test them with APIClient.</p>',
    '<p>Use ModelViewSet with a router, add pagination, search and ordering, and validate input with validate methods.</p>',
    '<p>Add token or JWT logins, permissions per object, throttles, nested serializers and APITestCase suites with query counts.</p>',
    '<p>Design versioned APIs, write OpenAPI docs (drf-spectacular), cache answers, and keep queries fast under load.</p>')}
{grow('Endpoints that work.', 'Endpoints that are safe.', 'An API others can rely on.')}
{deep('What happens inside a DRF view', '<p>APIView.dispatch wraps the Django request in a DRF Request, then runs initial(): perform_authentication, check_permissions and check_throttles, in this order. Then it calls the handler for the method (get, post, or the ViewSet action). An exception anywhere goes to handle_exception, which turns APIException, Http404 and PermissionDenied into JSON answers. Finally the Response is rendered by the renderer the client asked for.</p>')}
''', kw=['beginner', 'expert', 'dispatch', 'initial', 'handle_exception', 'OpenAPI', 'drf-spectacular', 'caching'])

lc(1408, 'String Matching in an Array', 'string-matching-in-an-array', 'e', 'Check each word against the others with in', 'Like the SearchFilter of an API: a word is a match when it appears inside another word. Two loops and the in operator are enough for small lists.', r'''
def string_matching(words):
    result = []
    for word in words:
        for other in words:
            if other != word and word in other:
                result.append(word)
                break
    return result
''', [('string_matching(["mass", "as", "hero", "superhero"])', ['as', 'hero']), ('string_matching(["leetcode", "et", "code"])', ['et', 'code']), ('string_matching(["blue", "green", "bu"])', [])])
lc(1207, 'Unique Number of Occurrences', 'unique-number-of-occurrences', 'e', 'Counter, then compare the counts with a set', 'A validation rule in a serializer often counts things. Count each value with Counter, then the counts are unique when a set of them has the same size.', r'''
from collections import Counter


def unique_occurrences(arr):
    counts = list(Counter(arr).values())
    return len(counts) == len(set(counts))
''', [('unique_occurrences([1, 2, 2, 1, 1, 3])', True), ('unique_occurrences([1, 2])', False), ('unique_occurrences([-3, 0, 1, -3, 1, 1, 1, -3, 10, 0])', True)])
lc(1640, 'Check Array Formation Through Concatenation', 'check-array-formation-through-concatenation', 'e', 'A dict from first number to piece', 'Like joining pages of API results back into one list. Each piece starts with a different number, so a dict from first number to piece finds the next piece at once.', r'''
def can_form_array(arr, pieces):
    by_first = {piece[0]: piece for piece in pieces}
    i = 0
    while i < len(arr):
        piece = by_first.get(arr[i])
        if piece is None or arr[i:i + len(piece)] != piece:
            return False
        i += len(piece)
    return True
''', [('can_form_array([15, 88], [[88], [15]])', True), ('can_form_array([49, 18, 16], [[16, 18, 49]])', False), ('can_form_array([91, 4, 64, 78], [[78], [4, 64], [91]])', True)])
lc(911, 'Online Election', 'online-election', 'm', 'Precompute the leader after each vote, then binary search the time', 'Like an API that answers "what was true at time t". Work out the leader after every vote once, then each question is a binary search on the times.', r'''
import bisect
from collections import defaultdict


class TopVotedCandidate:
    def __init__(self, persons, times):
        self.times = times
        self.leaders = []
        votes = defaultdict(int)
        leader = None
        for person in persons:
            votes[person] += 1
            if leader is None or votes[person] >= votes[leader]:
                leader = person
            self.leaders.append(leader)

    def q(self, t):
        i = bisect.bisect_right(self.times, t) - 1
        return self.leaders[i]
''' + PLAY, [('play(TopVotedCandidate, ["TopVotedCandidate", "q", "q", "q", "q", "q", "q"], [[[0, 1, 1, 0, 0, 1, 0], [0, 5, 10, 15, 20, 25, 30]], [3], [12], [25], [15], [24], [8]])', [None, 0, 1, 1, 0, 0, 1])])
lc(2080, 'Range Frequency Queries', 'range-frequency-queries', 'm', 'Positions per value, then two binary searches', 'Like an API filter ?value=4&from=1&to=2. Keep the sorted positions of each value, then count the positions inside the range with bisect.', r'''
import bisect
from collections import defaultdict


class RangeFreqQuery:
    def __init__(self, arr):
        self.positions = defaultdict(list)
        for i, value in enumerate(arr):
            self.positions[value].append(i)

    def query(self, left, right, value):
        places = self.positions.get(value, [])
        return bisect.bisect_right(places, right) - bisect.bisect_left(places, left)
''' + PLAY, [('play(RangeFreqQuery, ["RangeFreqQuery", "query", "query"], [[[12, 33, 4, 56, 22, 2, 34, 33, 22, 12, 34, 56]], [1, 2, 4], [0, 11, 33]])', [None, 1, 2])])
lc(2707, 'Extra Characters in a String', 'extra-characters-in-a-string', 'm', 'Dynamic programming from the end of the string', 'Like splitting a URL into known resource names. best[i] is the fewest extra letters from position i. Either skip the letter at i, or jump over a dictionary word that starts at i.', r'''
def min_extra_char(s, dictionary):
    words = set(dictionary)
    n = len(s)
    best = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        best[i] = best[i + 1] + 1
        for end in range(i + 1, n + 1):
            if s[i:end] in words:
                best[i] = min(best[i], best[end])
    return best[0]
''', [('min_extra_char("leetscode", ["leet", "code", "leetcode"])', 1), ('min_extra_char("sayhelloworld", ["hello", "world"])', 3)])
lc(381, 'Insert Delete GetRandom O(1) - Duplicates allowed', 'insert-delete-getrandom-o1-duplicates-allowed', 'h', 'A list plus a dict of index sets, swap with the last item to delete', 'Like a load balancer that picks a random server where some servers count twice. The list gives random choice in O(1), the dict of positions finds an item to remove, and swapping with the last item keeps removal O(1).', r'''
import random
from collections import defaultdict


class RandomizedCollection:
    def __init__(self):
        self.items = []
        self.where = defaultdict(set)

    def insert(self, val):
        self.where[val].add(len(self.items))
        self.items.append(val)
        return len(self.where[val]) == 1

    def remove(self, val):
        if not self.where[val]:
            return False
        i = self.where[val].pop()
        last = self.items[-1]
        self.items[i] = last
        self.where[last].add(i)
        self.where[last].discard(len(self.items) - 1)
        self.items.pop()
        return True

    def getRandom(self):
        return random.choice(self.items)


def random_check():
    """The random part cannot have one fixed answer, so this checks that it only returns stored values."""
    bag = RandomizedCollection()
    for value in [1, 1, 2]:
        bag.insert(value)
    bag.remove(1)
    return sorted(set(bag.getRandom() for _ in range(50)))
''' + PLAY, [('play(RandomizedCollection, ["RandomizedCollection", "insert", "insert", "insert", "remove", "remove", "remove"], [[], [1], [1], [2], [1], [1], [1]])', [None, True, False, True, True, True, False]), ('random_check()', [1, 2])])
lc(715, 'Range Module', 'range-module', 'h', 'A sorted list of disjoint intervals', 'Like a cache that remembers which ranges of ids it already fetched from an API. Keep the ranges sorted and merged, and use bisect to find the ones that touch a new range.', r'''
import bisect


class RangeModule:
    def __init__(self):
        self.edges = []                      # [start1, end1, start2, end2, ...] sorted, half open ranges

    def addRange(self, left, right):
        i = bisect.bisect_left(self.edges, left)
        j = bisect.bisect_right(self.edges, right)
        middle = []
        if i % 2 == 0:
            middle.append(left)
        if j % 2 == 0:
            middle.append(right)
        self.edges[i:j] = middle

    def queryRange(self, left, right):
        i = bisect.bisect_right(self.edges, left)
        j = bisect.bisect_left(self.edges, right)
        return i == j and i % 2 == 1

    def removeRange(self, left, right):
        i = bisect.bisect_left(self.edges, left)
        j = bisect.bisect_right(self.edges, right)
        middle = []
        if i % 2 == 1:
            middle.append(left)
        if j % 2 == 1:
            middle.append(right)
        self.edges[i:j] = middle
''' + PLAY, [('play(RangeModule, ["RangeModule", "addRange", "removeRange", "queryRange", "queryRange", "queryRange"], [[], [10, 20], [14, 16], [10, 14], [13, 15], [16, 17]])', [None, None, None, True, False, True])])
lc(2276, 'Count Integers in Intervals', 'count-integers-in-intervals', 'h', 'Merge intervals as they arrive and keep a running total', 'Like counting how many ids a set of API keys may read. Keep disjoint intervals sorted by start, merge every new one with the ones it touches, and update the total on the way.', r'''
import bisect


class CountIntervals:
    def __init__(self):
        self.starts = []
        self.ends = []
        self.total = 0

    def add(self, left, right):
        i = bisect.bisect_left(self.ends, left)          # the first interval that ends at or after left
        while i < len(self.starts) and self.starts[i] <= right:
            left = min(left, self.starts[i])
            right = max(right, self.ends[i])
            self.total -= self.ends[i] - self.starts[i] + 1
            del self.starts[i]
            del self.ends[i]
        self.starts.insert(i, left)
        self.ends.insert(i, right)
        self.total += right - left + 1

    def count(self):
        return self.total
''' + PLAY, [('play(CountIntervals, ["CountIntervals", "add", "add", "count", "add", "count"], [[], [2, 3], [7, 10], [], [5, 8], []])', [None, None, None, 6, None, 8])])
lc(1622, 'Fancy Sequence', 'fancy-sequence', 'h', 'Store one lazy formula a &times; x + b for every value', 'Like update(price=F("price") * 2 + 1) for every row at once: never touch each value. Keep one global formula and store each new value "undone" with the modular inverse, so the formula applies to it correctly later.', r'''
MOD = 10 ** 9 + 7


class Fancy:
    def __init__(self):
        self.values = []
        self.mul = 1                         # every real value = stored * mul + add
        self.add = 0

    def append(self, val):
        inverse = pow(self.mul, MOD - 2, MOD)            # Fermat: mul ** (MOD - 2) is 1 / mul
        self.values.append((val - self.add) * inverse % MOD)

    def addAll(self, inc):
        self.add = (self.add + inc) % MOD

    def multAll(self, m):
        self.mul = self.mul * m % MOD
        self.add = self.add * m % MOD

    def getIndex(self, idx):
        if idx >= len(self.values):
            return -1
        return (self.values[idx] * self.mul + self.add) % MOD
''' + PLAY, [('play(Fancy, ["Fancy", "append", "addAll", "append", "multAll", "getIndex", "addAll", "append", "multAll", "getIndex", "getIndex", "getIndex"], [[], [2], [3], [7], [2], [0], [3], [10], [2], [0], [1], [2]])', [None, None, None, None, None, 10, None, None, None, 26, 34, 20])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Problems that match the work of an API: searching words, validating counts, joining pages of results, answering "what was true at time t", range filters, splitting a path into known names, random choice for load balancing, remembering fetched id ranges, counting ids that keys may read, and applying one update lazily to every value.</p>'), kw=['LeetCode', 'binary search', 'design', 'intervals', 'dynamic programming', 'hash map'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'DRF adds serializers, API views, ViewSets, routers, authentication, permissions, throttles, filters and pagination on top of Django.',
    'A serializer turns objects into dicts and checks incoming data: field checks, validate_&lt;field&gt;, validate, then save().',
    'A ModelViewSet and router.register give list, create, retrieve, update, partial_update and destroy. get_queryset and perform_create change the details.',
    'Authentication finds the user, permissions decide (401 or 403), throttles limit the rate (429). Set the owner on the server, never from the body.',
    'Nested serializers need your own create(). Test every endpoint with APITestCase and keep the query count fixed.'],
    'Next: FastAPI, the type hint based API framework.')}
{files('Three tasks: write a serializer for shop orders, write page number and cursor pagination, and build a sliding window rate limiter.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does a DRF serializer do?', ['Draws pages', 'Turns objects into dicts for JSON and checks incoming data', 'Runs migrations', 'Starts the server'], 1, 'Like a form for JSON.', 'serializer.data out, serializer.validated_data in.')
K.quiz('e', 'Which status code fits a successful POST that created a book?', ['200', '201', '204', '302'], 1, 'Created.', 'Send the new object in the body.')
K.quiz('e', 'What does router.register("books", BookViewSet) do?', ['Creates the table', 'Makes the URL patterns for every action of the ViewSet', 'Adds a permission', 'Logs in a user'], 1, 'URLs for you.', 'book-list and book-detail, plus @action URLs.')
K.quiz('m', 'Which ViewSet action handles PATCH /api/books/7/?', ['update', 'partial_update', 'create', 'retrieve'], 1, 'Only some fields.', 'PUT calls update and replaces every field.')
K.quiz('m', 'A request without a token tries to create a note. What does IsAuthenticatedOrReadOnly answer?', ['200', '401', '403', '404'], 1, 'Nobody is logged in.', '403 is for a known user without permission.')
K.quiz('m', 'Where should the owner of a new note come from?', ['The JSON body', 'request.user, set in perform_create', 'A query parameter', 'The serializer default'], 1, 'Never trust the body.', 'serializer.save(owner=self.request.user).')
K.quiz('m', 'Why give a ViewSet an ordered queryset when it uses pagination?', ['It is required by Python', 'Without an order the database may return rows in a different order on each page, so rows can repeat or go missing', 'For speed only', 'For the router'], 1, 'Stable pages.', 'DRF warns about unordered querysets.')
K.quiz('m', 'Bad input reaches serializer.is_valid(raise_exception=True). What happens?', ['A 500 error', 'A ValidationError that DRF turns into a 400 answer with the messages', 'The data is saved anyway', 'A 404'], 1, 'Errors become 400.', 'No if statement needed in the view.')
K.quiz('m', 'What does a throttle answer when the limit is reached?', ['403', '429 with a Retry-After header', '500', '301'], 1, 'Too Many Requests.', 'The client should wait that many seconds.')
K.quiz('h', 'A nested serializer shows authors with their books. Why does saving a new author with books need your own create()?', ['It does not', 'DRF does not know how to save the related rows, so create() must make the author and then each book, best inside atomic()', 'For permissions', 'Because of pagination'], 1, 'Writable nested serializers.', 'Without it DRF raises an error that tells you to write create().')
K.quiz('h', 'In which order does a DRF view run its checks?', ['Throttle, permission, authentication', 'Authentication, permissions, throttles, then the handler', 'Handler first', 'Permissions only'], 1, 'Who, may they, how often.', 'That is why a request that fails permissions does not use up the throttle.')
K.quiz('x', 'In the style of a Stanford CS 253 web security exam: an API uses SessionAuthentication for its own JavaScript front end. Which attack must it still defend against, and how does DRF do it?', ['SQL injection, by escaping', 'Cross site request forgery, because the browser sends the cookie by itself. DRF enforces Django&#39;s CSRF check for logged in session users', 'Clickjacking only', 'Nothing, sessions are safe'], 1, 'Cookies travel automatically.', 'Token authentication in a header is not sent by the browser on its own, so it does not need CSRF.')
K.quiz('x', 'In the style of a CMU 17-214 design exam: why can page number pagination show the same item twice while a user scrolls, and what avoids it?', ['It cannot', 'New rows added at the top shift every later row to the next page. Cursor pagination asks for rows after the last seen id', 'Because of caching', 'Because of throttling'], 1, 'Page drift.', 'DRF has CursorPagination for feeds.')

K.calc('e', '5 books, 2 per page. How many pages?', '3', 'Round up.', ['5 / 2 = 2.5.', 'A part page is still a page.', eq('3 pages')], check=-(-5 // 2))
K.calc('e', 'A limit of 100 requests an hour. How many requests a day at most?', '2400', 'rate &times; hours.', ['24 hours in a day.', '100 &times; 24.', eq('2,400 requests')], check=100 * 24)
K.calc('e', '20 books of 120 bytes each in one page. About how many bytes?', '2400', 'rows &times; bytes.', ['Each row is about 120 bytes of JSON.', '20 &times; 120.', eq('2,400 bytes')], check=20 * 120)
K.calc('m', 'Rate 3/minute. Requests at 0, 10 and 20 s, then one at 30 s. What is Retry-After in seconds?', '30', 'oldest + window &minus; now.', ['The oldest is at 0 s.', 'It leaves the window at 60 s.', '60 &minus; 30.', eq('30 s')], check=0 + 60 - 30)
K.calc('m', '50,000 rows at 100 per page. How many requests to read all of them?', '500', 'Round up count / size.', ['50,000 / 100 = 500.', 'No part page.', eq('500 requests')], check=50000 // 100)
K.calc('m', 'All 50,000 rows of 120 bytes in one answer. How many MB (1 MB = 1,000,000 bytes)?', '6', 'rows &times; bytes.', ['50,000 &times; 120 = 6,000,000 bytes.', 'Divide by 1,000,000.', eq('6 MB')], check=50000 * 120 / 1_000_000)
K.calc('m', 'Page 7 with 20 per page. What OFFSET does the SQL use?', '120', '(page &minus; 1) &times; size.', ['Pages 1 to 6 are skipped.', '6 &times; 20.', eq('OFFSET 120')], check=(7 - 1) * 20)
K.calc('m', 'A list of authors with nested books, 5 authors, with prefetch_related. How many queries?', '2', 'Authors, then all books.', ['1 query for the authors.', '1 query for the books of all 5.', eq('2 queries')], check=2)
K.calc('h', 'Without prefetch_related the same list reads each author&#39;s books in its own query. How many queries for 50 authors?', '51', 'N + 1.', ['1 for the authors.', '1 for the books of each of the 50.', eq('51 queries')], check=1 + 50)
K.calc('x', 'In the style of a Berkeley CS 162 exam: 4 workers each throttle with their own memory instead of a shared cache. The rule is 60 requests a minute per user. Requests are spread evenly across workers. How many requests a minute can one user really make?', '240', 'Each worker counts alone.', ['Each worker allows 60 a minute.', 'There are 4 workers.', '60 &times; 4.', eq('240 a minute, so use a shared cache such as Redis')], check=60 * 4)

K.assign('order', 'e', 'Write a serializer for shop orders',
         '<p>Finish <code>OrderSerializer</code>. The fields are ready. Add <code>validate_coupon</code>: strip spaces, use upper case, and raise ValidationError("Unknown coupon.") when the coupon is not empty and not in COUPONS. Change <code>validate</code>: raise ValidationError("HALF needs at least 2 items.") when the coupon is HALF and the quantity is under 2, and set data["total"] to price times quantity minus the coupon percent. try_order(data) returns ["ok", validated data] or ["errors", &#123;field: [messages]&#125;].</p>',
         r'''
import django
from django.conf import settings

settings.configure(SECRET_KEY="dev-only", INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth", "rest_framework"])
django.setup()

from rest_framework import serializers

PRICES = {"tea": 3, "cake": 5, "sandwich": 7}
COUPONS = {"HALF": 50, "TEN": 10}


class OrderSerializer(serializers.Serializer):
    product = serializers.ChoiceField(choices=sorted(PRICES))
    quantity = serializers.IntegerField(min_value=1, max_value=10)
    coupon = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, data):
        data["total"] = PRICES[data["product"]] * data["quantity"]
        return data


def try_order(data):
    serializer = OrderSerializer(data=data)
    if serializer.is_valid():
        return ["ok", dict(serializer.validated_data)]
    return ["errors", {field: [str(e) for e in errors] for field, errors in serializer.errors.items()}]
''', [('try_order({"product": "cake", "quantity": 2})', ['ok', {'product': 'cake', 'quantity': 2, 'coupon': '', 'total': 10.0}]), ('try_order({"product": "tea", "quantity": 4, "coupon": " half "})', ['ok', {'product': 'tea', 'quantity': 4, 'coupon': 'HALF', 'total': 6.0}]), ('try_order({"product": "pizza", "quantity": 0})', ['errors', {'product': ['"pizza" is not a valid choice.'], 'quantity': ['Ensure this value is greater than or equal to 1.']}]), ('try_order({"product": "tea", "quantity": 1, "coupon": "FREE"})', ['errors', {'coupon': ['Unknown coupon.']}]), ('try_order({"product": "sandwich", "quantity": 1, "coupon": "HALF"})', ['errors', {'non_field_errors': ['HALF needs at least 2 items.']}]), ('try_order({"quantity": 3})', ['errors', {'product': ['This field is required.']}])],
         r'''
import django
from django.conf import settings

settings.configure(SECRET_KEY="dev-only", INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth", "rest_framework"])
django.setup()

from rest_framework import serializers

PRICES = {"tea": 3, "cake": 5, "sandwich": 7}
COUPONS = {"HALF": 50, "TEN": 10}


class OrderSerializer(serializers.Serializer):
    product = serializers.ChoiceField(choices=sorted(PRICES))
    quantity = serializers.IntegerField(min_value=1, max_value=10)
    coupon = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_coupon(self, value):
        value = value.strip().upper()
        if value and value not in COUPONS:
            raise serializers.ValidationError("Unknown coupon.")
        return value

    def validate(self, data):
        if data["coupon"] == "HALF" and data["quantity"] < 2:
            raise serializers.ValidationError("HALF needs at least 2 items.")
        total = PRICES[data["product"]] * data["quantity"]
        data["total"] = total * (100 - COUPONS.get(data["coupon"], 0)) / 100
        return data


def try_order(data):
    serializer = OrderSerializer(data=data)
    if serializer.is_valid():
        return ["ok", dict(serializer.validated_data)]
    return ["errors", {field: [str(e) for e in errors] for field, errors in serializer.errors.items()}]
''', 'validate_&lt;field&gt; gets one value and returns the cleaned value. validate(data) gets all fields, and an error raised there appears under non_field_errors. The total is total &times; (100 &minus; percent) / 100.', '<p>This is the same pattern as forms in chapter 4.2: field checks first, then validate_&lt;field&gt;, then validate. In a ViewSet, serializer.is_valid(raise_exception=True) turns these errors into a 400 answer for you.</p>')
K.assign('paging', 'm', 'Write page number and cursor pagination',
         '<p>Write <code>paginate(items, page, page_size, base_url)</code> that returns &#123;"count", "next", "previous", "results"&#125; like DRF&#39;s PageNumberPagination. Pages start at 1, next and previous are base_url + "?page=N" or None, an empty list still has a page 1, and a page that is not a whole number from 1 to the last page raises ValueError("Invalid page."). Write <code>cursor_page(rows, after_id, size)</code>: the ids of the next size rows with id greater than after_id, sorted by id, and next_cursor, the last id of the page, or None when nothing is left.</p>',
         r'''
def page_url(base_url, page):
    return None if page is None else f"{base_url}?page={page}"


def paginate(items, page, page_size, base_url):
    """One page in the shape DRF's PageNumberPagination returns."""
    start = page * page_size
    return {"count": len(items), "next": None, "previous": None, "results": items[start:start + page_size]}


def cursor_page(rows, after_id, size):
    """Cursor pagination: the rows with id greater than after_id, sorted by id, and the cursor for the next page."""
    return {"results": [row["id"] for row in rows[:size]], "next_cursor": None}


def page_error(page):
    try:
        paginate(list(range(5)), page, 2, "/api/books/")
    except ValueError as error:
        return str(error)
    return "no error"
''', [('paginate(list(range(1, 6)), 1, 2, "/api/books/")', {'count': 5, 'next': '/api/books/?page=2', 'previous': None, 'results': [1, 2]}), ('paginate(list(range(1, 6)), 2, 2, "/api/books/")', {'count': 5, 'next': '/api/books/?page=3', 'previous': '/api/books/?page=1', 'results': [3, 4]}), ('paginate(list(range(1, 6)), 3, 2, "/api/books/")', {'count': 5, 'next': None, 'previous': '/api/books/?page=2', 'results': [5]}), ('paginate([], 1, 2, "/api/books/")', {'count': 0, 'next': None, 'previous': None, 'results': []}), ('[page_error(0), page_error(4), page_error(3)]', ['Invalid page.', 'Invalid page.', 'no error']), ('cursor_page([{"id": 5}, {"id": 2}, {"id": 9}, {"id": 7}], 0, 2)', {'results': [2, 5], 'next_cursor': 5}), ('cursor_page([{"id": 5}, {"id": 2}, {"id": 9}, {"id": 7}], 5, 2)', {'results': [7, 9], 'next_cursor': None})],
         r'''
def page_url(base_url, page):
    return None if page is None else f"{base_url}?page={page}"


def paginate(items, page, page_size, base_url):
    """One page in the shape DRF's PageNumberPagination returns."""
    if not isinstance(page, int) or page < 1:
        raise ValueError("Invalid page.")
    last = max(1, -(-len(items) // page_size))           # ceiling division, an empty list still has page 1
    if page > last:
        raise ValueError("Invalid page.")
    start = (page - 1) * page_size
    return {
        "count": len(items),
        "next": page_url(base_url, page + 1 if page < last else None),
        "previous": page_url(base_url, page - 1 if page > 1 else None),
        "results": items[start:start + page_size],
    }


def cursor_page(rows, after_id, size):
    """Cursor pagination: the rows with id greater than after_id, sorted by id, and the cursor for the next page."""
    newer = sorted((row for row in rows if row["id"] > after_id), key=lambda row: row["id"])
    chunk = newer[:size]
    next_cursor = chunk[-1]["id"] if len(newer) > size else None
    return {"results": [row["id"] for row in chunk], "next_cursor": next_cursor}


def page_error(page):
    try:
        paginate(list(range(5)), page, 2, "/api/books/")
    except ValueError as error:
        return str(error)
    return "no error"
''', 'The last page is the ceiling of len(items) / page_size, and at least 1. -(-a // b) is a ceiling division. For the cursor, sort the newer rows and check whether more rows exist after the page.', '<p>Page numbers are easy to show, but new rows move items between pages while someone reads them (chapter 2.2). A cursor asks for "rows after id 5", so nothing is skipped or shown twice, and the database uses the index instead of a large OFFSET. DRF has CursorPagination for this.</p>')
K.assign('throttle', 'h', 'Build a sliding window rate limiter',
         '<p>Finish <code>SlidingWindowLimiter</code>, the idea behind DRF&#39;s throttles. parse_rate is ready: "3/minute" gives 3 requests per 60 seconds. <code>allow(key, now)</code> keeps the times of the accepted requests of each key. First forget the times that are window seconds old or older. When the key already has the allowed number of requests, return [False, seconds until the oldest one leaves the window] and do not store the request. Otherwise store it and return [True, 0]. Each key (an IP address or a user) has its own history.</p>',
         r'''
UNITS = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}


def parse_rate(rate):
    """ "3/minute" becomes (3, 60), as in DRF's SimpleRateThrottle."""
    count, unit = rate.split("/")
    if unit not in UNITS or not count.isdigit():
        raise ValueError(f"bad rate {rate!r}")
    return int(count), UNITS[unit]


class SlidingWindowLimiter:
    def __init__(self, rate):
        self.allowed, self.window = parse_rate(rate)
        self.history = {}                         # key -> times of the accepted requests, oldest first

    def allow(self, key, now):
        times = self.history.setdefault(key, [])
        times.append(now)
        return [len(times) <= self.allowed, 0]


def limiter_story(rate, events):
    """events: a list of (key, time). Returns [allowed, retry_after] for each."""
    limiter = SlidingWindowLimiter(rate)
    return [limiter.allow(key, now) for key, now in events]


def rate_error(rate):
    try:
        parse_rate(rate)
    except ValueError:
        return "ValueError"
    return "no error"
''', [('limiter_story("3/minute", [("ip1", 0), ("ip1", 10), ("ip1", 20), ("ip1", 30)])', [[True, 0], [True, 0], [True, 0], [False, 30]]), ('limiter_story("3/minute", [("ip1", 0), ("ip1", 10), ("ip1", 20), ("ip1", 60), ("ip1", 61)])', [[True, 0], [True, 0], [True, 0], [True, 0], [False, 9]]), ('limiter_story("1/second", [("a", 0), ("b", 0), ("a", 0.5), ("a", 1)])', [[True, 0], [True, 0], [False, 0.5], [True, 0]]), ('limiter_story("2/hour", [("u", 0), ("u", 100), ("u", 200), ("u", 3600), ("u", 3601)])', [[True, 0], [True, 0], [False, 3400], [True, 0], [False, 99]]), ('[rate_error("3/minute"), rate_error("3/week"), rate_error("many/day")]', ['no error', 'ValueError', 'ValueError'])],
         r'''
UNITS = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}


def parse_rate(rate):
    """ "3/minute" becomes (3, 60), as in DRF's SimpleRateThrottle."""
    count, unit = rate.split("/")
    if unit not in UNITS or not count.isdigit():
        raise ValueError(f"bad rate {rate!r}")
    return int(count), UNITS[unit]


class SlidingWindowLimiter:
    def __init__(self, rate):
        self.allowed, self.window = parse_rate(rate)
        self.history = {}                         # key -> times of the accepted requests, oldest first

    def allow(self, key, now):
        times = self.history.setdefault(key, [])
        while times and times[0] <= now - self.window:
            times.pop(0)                          # forget requests that left the window
        if len(times) >= self.allowed:
            return [False, times[0] + self.window - now]
        times.append(now)
        return [True, 0]


def limiter_story(rate, events):
    """events: a list of (key, time). Returns [allowed, retry_after] for each."""
    limiter = SlidingWindowLimiter(rate)
    return [limiter.allow(key, now) for key, now in events]


def rate_error(rate):
    try:
        parse_rate(rate)
    except ValueError:
        return "ValueError"
    return "no error"
''', 'Remove times while times[0] &lt;= now &minus; window. The wait is times[0] + window &minus; now. Rejected requests must not be added, or a client that keeps trying would never get in.', '<p>DRF keeps the same list of times in the cache (Redis in production, so all workers share it) and sends the wait in the Retry-After header of the 429 answer. A token bucket (chapter 2.2) allows short bursts, a sliding window is stricter and easier to explain.</p>')

K.must('Serializers', 'class BookSerializer(serializers.ModelSerializer) with Meta.model, Meta.fields. serializer.data, Serializer(data=...).is_valid(raise_exception=True), validated_data, save(). validate_&lt;field&gt;, validate, SerializerMethodField, read_only.')
K.must('Views and routers', '@api_view(["GET", "POST"]) with Response(data, status=201). class BookViewSet(viewsets.ModelViewSet) with queryset and serializer_class. router.register("books", BookViewSet). @action. get_queryset, perform_create.')
K.must('Security', 'DEFAULT_AUTHENTICATION_CLASSES (Token, Session, JWT). permission_classes: IsAuthenticated, IsAuthenticatedOrReadOnly, has_object_permission. 401 no credentials, 403 not allowed. Throttles answer 429 with Retry-After.')
K.must('Lists', 'DEFAULT_PAGINATION_CLASS PageNumberPagination with PAGE_SIZE: count, next, previous, results. SearchFilter ?search=, OrderingFilter ?ordering=-year. Always order the queryset. CursorPagination for feeds.')
K.must('Tests and design', 'APITestCase, self.client.post(url, data, format="json"), force_authenticate, assertNumQueries. Nouns in URLs, right status codes, one error shape, versioning, idempotent retries.')

T = K.topic(
    slug='py-drf', topic='py-drf', step=(5, 'Building APIs: Django REST framework and FastAPI', 'py-w5', 'Build JSON APIs two ways: Django REST framework on top of a Django project, and FastAPI with type hints and automatic docs.', 'Advanced'),
    title='Django REST framework: JSON APIs on top of Django', short='Django REST framework', badge='5.1', minutes=110,
    lead='Build JSON APIs with Django REST framework. Turn models into JSON with serializers, get every endpoint from a ViewSet and a router, add pages, search, token logins, permissions and rate limits, and test it all.',
    desc='What DRF adds to Django, serializers and ModelSerializer, validation with validate_field and validate, SerializerMethodField, @api_view and Response, status codes, generic views and ViewSets, routers and @action, get_queryset and perform_create, SearchFilter, OrderingFilter and PageNumberPagination, token, session and JWT authentication, permission classes and object permissions, 401 and 403, throttling and 429, nested serializers with a writable create, APITestCase and APIClient, REST API design rules, and the maths of pages, rate limits and payload size.',
    summary='Serializers, ViewSets and routers, pagination and filters, authentication, permissions, throttles and API tests.',
    keywords=['Django REST framework', 'serializer', 'ModelViewSet', 'router', 'pagination', 'TokenAuthentication', 'permissions', 'throttling', 'APITestCase', 'REST'],
    recap='<p>A serializer checks and shapes the JSON, a ViewSet with a router gives the endpoints, and authentication, permissions and throttles decide who may call them and how often.</p>',
    added='2026-11-08', leet=leet_items())
