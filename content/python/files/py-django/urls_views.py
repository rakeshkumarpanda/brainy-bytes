# 4.1 Django basics: project, URLs, views, templates, models and admin
# Example "urls_views" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import logging

import django
from django.conf import settings

# ---------- settings.py: written here in code, so the whole project fits in one file ----------
settings.configure(
    DEBUG=True,
    SECRET_KEY="dev-only",
    ROOT_URLCONF=__name__,                                # the URL patterns are in this file
    ALLOWED_HOSTS=["testserver", "localhost"],
    MIDDLEWARE=["django.middleware.common.CommonMiddleware"],
    INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
)
django.setup()
logging.getLogger("django.request").setLevel(logging.ERROR)   # hide the "Not Found" log lines in this demo

from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.test import Client
from django.urls import path, reverse
from django.views import View
from django.views.decorators.http import require_http_methods

BOOKS = {1: "Dune", 2: "Emma"}


# ---------- views.py: a view takes a request and returns a response ----------
def home(request):
    return HttpResponse("Welcome to the Django book shop")


def hello(request, name):
    lang = request.GET.get("lang", "en")                  # ?lang=fr in the URL
    greeting = {"en": "Hello", "fr": "Bonjour"}.get(lang, "Hello")
    return HttpResponse(f"{greeting}, {name}!")


def book_detail(request, book_id):
    if book_id not in BOOKS:
        raise Http404("No such book")                     # Django answers 404
    return JsonResponse({"id": book_id, "title": BOOKS[book_id]})


@require_http_methods(["POST"])                           # GET gives 405
def add_book(request):
    title = request.POST.get("title", "").strip()
    new_id = max(BOOKS) + 1
    BOOKS[new_id] = title
    return redirect("book-detail", book_id=new_id)        # 302 to /books/3/


class StatusView(View):                                   # a class based view: one method per HTTP method
    def get(self, request):
        return JsonResponse({"books": len(BOOKS), "method": request.method})


# ---------- urls.py: the URL patterns, in order ----------
urlpatterns = [
    path("", home, name="home"),
    path("hello/<str:name>/", hello, name="hello"),
    path("books/<int:book_id>/", book_detail, name="book-detail"),
    path("books/add/", add_book, name="book-add"),
    path("status/", StatusView.as_view(), name="status"),
]

client = Client()                                         # Django's test client, like Flask's
for url in ["/", "/hello/Ann/?lang=fr", "/books/2/", "/books/9/", "/books/seven/", "/hello/Ann", "/books/add/", "/status/"]:
    response = client.get(url)
    extra = response.content.decode()[:40] if response.status_code == 200 else response.get("Location", "")
    print(f"GET  {url:20} {response.status_code} {extra}")

response = client.post("/books/add/", {"title": "Hamlet"})
print(f"POST /books/add/          {response.status_code} -> {response['Location']}")
print("then", client.get(response["Location"]).json())
print("reverse:", reverse("book-detail", args=[42]), reverse("hello", kwargs={"name": "Bob"}))
