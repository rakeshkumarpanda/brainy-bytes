# 4.1 Django basics: project, URLs, views, templates, models and admin
# Example "admin_site" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import logging
import os
import re

import django
from django.apps import AppConfig
from django.conf import settings


class ShopConfig(AppConfig):
    name = "__main__"
    label = "shop"
    verbose_name = "Book shop"
    path = os.getcwd()


settings.configure(
    DEBUG=True,
    SECRET_KEY="dev-only",
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=["testserver"],
    INSTALLED_APPS=[
        "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
        "django.contrib.sessions", "django.contrib.messages", "__main__.ShopConfig",
    ],
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
    ],
    TEMPLATES=[{
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    }],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
)
django.setup()
logging.getLogger("django.request").setLevel(logging.ERROR)

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection, models
from django.test import Client
from django.urls import path


# ---------- models.py ----------
class Book(models.Model):
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField()
    in_stock = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# ---------- admin.py: three lines give a full page to search, add, change and delete books ----------
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "year", "in_stock"]
    list_filter = ["in_stock"]
    search_fields = ["title"]


# ---------- urls.py ----------
urlpatterns = [path("admin/", admin.site.urls)]

call_command("migrate", verbosity=0)                       # the tables of auth, sessions and admin
with connection.schema_editor() as editor:                 # and the Book table (makemigrations does this in a project)
    editor.create_model(Book)
for title, year in [("Dune", 1965), ("Dune Messiah", 1969), ("Emma", 1815)]:
    Book.objects.create(title=title, year=year)
User.objects.create_superuser("boss", "boss@example.com", "a long secret 42")


def rows(html):
    """The titles shown in the admin list table."""
    return re.findall(r'<th class="field-title"><a href="[^"]+">([^<]+)</a>', html)


client = Client()
response = client.get("/admin/shop/book/")
print("not logged in:", response.status_code, "->", response["Location"])

client.login(username="boss", password="a long secret 42")
response = client.get("/admin/shop/book/")
print("logged in:", response.status_code, rows(response.content.decode()))
response = client.get("/admin/shop/book/?q=dune")
print("search 'dune':", rows(response.content.decode()))
response = client.get("/admin/")
print("apps on the home page:", re.findall(r'<caption>\s*<a[^>]*>([^<]+)</a>', response.content.decode()))
