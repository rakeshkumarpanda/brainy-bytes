# Web and APIs 4.1: Django basics. Checked against the Django 6.1 documentation (tutorial parts 1 to 7, URL dispatcher,
# writing views, class based views, the template language and built in filters, models and fields, the admin site,
# settings, middleware, the CSRF guide, deployment checklist) with real runs of Django 6.1.3 on Python 3.14.
# Every program configures Django in one file with settings.configure, so it runs in the page. The one that runs
# startproject and migrate as real commands uses local().
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, lc, leet, files, grow, leet_items

chapter('py-django')
K = Kit()

K.code('real_project', r'''
import os
import subprocess
import sys
import tempfile

# The same commands you type in a terminal, run from Python so you can see each step and its output
work = tempfile.mkdtemp()


def run(*command, cwd=None):
    print("$", " ".join(command))
    result = subprocess.run([sys.executable, *command], cwd=cwd or work, capture_output=True, text=True)
    output = (result.stdout + result.stderr).strip()
    if output:
        print("  " + output.replace("\n", "\n  "))
    return result


run("-m", "django", "startproject", "mysite")
site = os.path.join(work, "mysite")
run("manage.py", "startapp", "books", cwd=site)

for folder, _, names in sorted(os.walk(site)):
    depth = folder[len(site):].count(os.sep)
    if "__pycache__" not in folder and "migrations" not in folder:
        print("  " * depth + os.path.basename(folder) + "/", " ".join(sorted(n for n in names if n.endswith(".py"))))

with open(os.path.join(site, "books", "models.py"), "w") as f:
    f.write(
        "from django.db import models\n\n\n"
        "class Book(models.Model):\n"
        "    title = models.CharField(max_length=200)\n"
        "    year = models.PositiveIntegerField()\n"
    )
settings_path = os.path.join(site, "mysite", "settings.py")
text = open(settings_path).read().replace('"django.contrib.staticfiles",', '"django.contrib.staticfiles",\n    "books",')
open(settings_path, "w").write(text)

run("manage.py", "makemigrations", "books", cwd=site)
run("manage.py", "sqlmigrate", "books", "0001", cwd=site)
result = run("manage.py", "migrate", cwd=site)
run("manage.py", "check", cwd=site)''', long=True)
K.code('urls_views', r'''
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
print("reverse:", reverse("book-detail", args=[42]), reverse("hello", kwargs={"name": "Bob"}))''', long=True)
K.code('templates', r'''
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
print(client.get("/").content.decode())''', long=True)
K.code('models_intro', r'''
import os

import django
from django.apps import AppConfig
from django.conf import settings


class ShopConfig(AppConfig):          # in a project this is books/apps.py, made by startapp
    name = "__main__"                 # the module that holds the models: this file
    label = "shop"                    # table names start with this label: shop_book
    path = os.getcwd()


settings.configure(
    SECRET_KEY="dev-only",
    INSTALLED_APPS=["__main__.ShopConfig"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
)
django.setup()

from django.db import connection, models


# ---------- models.py: one class is one table, one field is one column ----------
class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")

    class Meta:
        ordering = ["year"]

    def __str__(self):
        return f"{self.title} ({self.year})"


# In a project, makemigrations and migrate make the tables. In one file we ask the schema editor.
with connection.schema_editor() as editor:
    editor.create_model(Author)
    editor.create_model(Book)

# Create
herbert = Author.objects.create(name="Frank Herbert")
austen = Author.objects.create(name="Jane Austen")
Book.objects.create(title="Dune", year=1965, price="9.99", author=herbert)
Book.objects.create(title="Dune Messiah", year=1969, price="8.50", author=herbert)
emma = Book(title="Emma", year=1815, author=austen)
emma.save()                                        # same as create, in two steps

# Read
print(Book.objects.count(), "books:", list(Book.objects.all()))
print("after 1900:", list(Book.objects.filter(year__gte=1900).values_list("title", flat=True)))
print("Emma was written by", Book.objects.get(title="Emma").author)
print("Herbert wrote", list(herbert.books.all()))  # the other side of the ForeignKey

# Update and delete
Book.objects.filter(author=herbert).update(price="7.00")
print("new prices:", [str(book.price) for book in herbert.books.all()])
emma.delete()
print("left:", Book.objects.count())

# The SQL Django writes for you
query = Book.objects.filter(author__name__startswith="Frank").only("title")
print(str(query.query))''', long=True)
K.code('admin_site', r'''
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
print("apps on the home page:", re.findall(r'<caption>\s*<a[^>]*>([^<]+)</a>', response.content.decode()))''', long=True)

PLAY = '''

def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results
'''

K.lesson('idea', 'What Django is and why it has so much built in', f'''
{src('Django 6.1 documentation: tutorial parts 1 to 7, URL dispatcher, views, class based views, templates, models, the admin site, settings, middleware, CSRF protection and the deployment checklist.')}
{wwh('<b>Django</b> is a Python web framework with everything a website needs in one package: URL routing, views, a template language, an <b>ORM</b> that turns Python classes into database tables, <b>migrations</b>, users and logins, forms, an <b>admin site</b> and strong security defaults.',
     'With a small framework you choose and connect many libraries yourself: one for the database, one for migrations, one for logins, one for forms, one for an admin page. Each choice takes time, and the parts do not always fit together. Most business websites need all of these parts.',
     'Django gives one tested way to do each job, and all parts know each other. A model you write is used by migrations, forms, the admin and the ORM at the same time. You write models.py, views.py, urls.py and templates, and Django does the rest of the work around them.')}
{viz('pydjango')}
{versus('Three popular Python web frameworks', ['', 'Flask', 'Django', 'FastAPI'], [
    ['Style', 'Small core, add what you need', 'Everything built in', 'Built for JSON APIs, uses type hints'],
    ['Database', 'Your choice (sqlite3, SQLAlchemy)', 'The Django ORM with migrations', 'Your choice (SQLAlchemy, SQLModel)'],
    ['Users and admin', 'Extensions such as Flask-Login', 'Built in: auth and a full admin site', 'Write them or add libraries'],
    ['HTML pages', 'Jinja templates', 'Django templates', 'Possible, but not its focus'],
    ['Good for', 'Small apps, services, learning', 'Shops, news sites, internal tools, big projects', 'Fast APIs with automatic docs'],
    ['Used by', 'Pinterest (early), many services', 'Instagram, Mozilla, Disqus', 'Many new API services']],
    'Pick Django when the site has users, data and an admin team. Pick Flask or FastAPI for a small service or an API without pages. Step 5 shows Django REST framework and FastAPI.')}
{note('Django calls its pattern <b>MTV</b>: the <b>Model</b> holds the data, the <b>Template</b> shows it, and the <b>View</b> decides what to show. It is the same idea as MVC, only the names differ: the Django view does the job of an MVC controller.', 'exam')}
''', kw=['Django', 'framework', 'ORM', 'migrations', 'admin', 'MTV', 'MVC', 'Flask', 'FastAPI', 'batteries included'])

K.lesson('project', 'A project and its apps', f'''
{local('real_project', 'It runs the real django-admin and manage.py commands in a temporary folder. Install Django first with <code>pip install django</code>.')}
{table(['File', 'What it is for'], [
    ['manage.py', 'Runs every command: runserver, startapp, makemigrations, migrate, createsuperuser, shell, test'],
    ['mysite/settings.py', 'All settings: INSTALLED_APPS, MIDDLEWARE, DATABASES, TEMPLATES, DEBUG, SECRET_KEY, ALLOWED_HOSTS'],
    ['mysite/urls.py', 'The first URL list. It sends parts of the site to the apps with include()'],
    ['mysite/wsgi.py, asgi.py', 'The entry point for Gunicorn (WSGI) or Uvicorn (ASGI) in production'],
    ['books/models.py', 'The models of the app, one class for each table'],
    ['books/views.py, books/urls.py', 'The views of the app and their URL patterns (you make urls.py yourself)'],
    ['books/admin.py', 'Which models show up in the admin site, and how'],
    ['books/migrations/', 'The migration files that makemigrations writes. Keep them in git'],
    ['books/templates/books/', 'The HTML templates of the app. The second books folder stops name clashes between apps']])}
{steps('The commands you use every day', [
    '<code>django-admin startproject mysite</code> makes the project once. <code>python manage.py startapp books</code> makes each app.',
    'Add the app to INSTALLED_APPS, write the models, then run <code>python manage.py makemigrations</code> and <code>python manage.py migrate</code>.',
    '<code>python manage.py createsuperuser</code> makes an admin user. <code>python manage.py runserver</code> starts the development server at http://127.0.0.1:8000/.',
    '<code>python manage.py shell</code> opens Python with your project loaded, which is handy to try ORM queries.',
    '<code>python manage.py check --deploy</code> lists settings that are not safe for production.'])}
{note('A <b>project</b> is the whole website with its settings. An <b>app</b> is one feature, such as books, accounts or payments. A good app does one thing, so you could even reuse it in another project.', 'tip')}
''', kw=['startproject', 'startapp', 'manage.py', 'settings.py', 'INSTALLED_APPS', 'project', 'app', 'runserver', 'makemigrations', 'migrate', 'createsuperuser'])

K.lesson('urls', 'URLs and views', f'''
{run('urls_views')}
{table(['Path converter', 'Matches', 'Gives the view'], [
    ['&lt;str:name&gt; (the default)', 'Any text without a slash', 'str'],
    ['&lt;int:book_id&gt;', '0 or a positive whole number', 'int'],
    ['&lt;slug:slug&gt;', 'Letters, digits, hyphens and underscores, such as dune-messiah', 'str'],
    ['&lt;uuid:token&gt;', 'A UUID such as 075194d3-6885-417e-a8a8-6c931e272f00', 'uuid.UUID'],
    ['&lt;path:file&gt;', 'Any text, slashes too', 'str'],
    ['re_path(r"...")', 'A regular expression, for special cases', 'str for each group']])}
{versus('Two ways to write a view', ['', 'Function based view', 'Class based view'], [
    ['Looks like', 'def book_list(request): ...', 'class BookList(ListView): model = Book'],
    ['HTTP methods', 'if request.method == "POST": ... or @require_http_methods', 'A method for each: get(), post()'],
    ['Reuse', 'Helpers and decorators', 'Inheritance and mixins, many generic views ready made'],
    ['Good for', 'Clear, special logic', 'Standard pages: lists, details, create, update, delete']],
    'Start with functions, because you can read them from top to bottom. Use generic class based views such as ListView and DetailView when a page is a standard list or detail page.')}
{steps('What the example shows', [
    'Django tries <b>urlpatterns</b> from top to bottom and calls the first view that matches. The names, such as "book-detail", let <b>reverse()</b> and the template tag url build links, so a URL can change in one place.',
    'request.GET holds the query string and request.POST the form fields. HttpResponse sends text, JsonResponse sends JSON.',
    'Raising <b>Http404</b> gives a 404 answer. @require_http_methods(["POST"]) gives 405 to every other method.',
    '<b>redirect("book-detail", book_id=3)</b> sends a 302 to the new page. This is the Post, Redirect, Get pattern again.',
    '/hello/Ann without the last slash gets a <b>301</b> to /hello/Ann/, because CommonMiddleware with APPEND_SLASH adds it.'])}
{note('The test client does not check CSRF tokens unless you ask it to, so the POST in the example works without one. In a real project CsrfViewMiddleware is on, and every POST form needs <code>&#123;% csrf_token %&#125;</code>. The animation above shows what happens without it.', 'exam')}
''', kw=['urlpatterns', 'path', 'path converters', 'reverse', 'view', 'HttpRequest', 'HttpResponse', 'JsonResponse', 'Http404', 'redirect', 'class based views', 'APPEND_SLASH', 'CSRF'])

K.lesson('templates', 'Templates', f'''
{run('templates')}
{table(['Template code', 'What it does'], [
    ['<code>&#123;&#123; book.title &#125;&#125;</code>', 'Shows a value. The dot tries a dict key, then an attribute, then a list index'],
    ['<code>&#123;&#123; name|default:"guest"|title &#125;&#125;</code>', 'Filters change a value, and you can chain them'],
    ['<code>&#123;% for book in books %&#125; ... &#123;% empty %&#125; ... &#123;% endfor %&#125;</code>', 'A loop, with a part for an empty list. forloop.counter counts from 1'],
    ['<code>&#123;% if book.year &lt; 1900 %&#125; ... &#123;% endif %&#125;</code>', 'A condition'],
    ['<code>&#123;% url "book-detail" book.id %&#125;</code>', 'Builds a link from the URL name, like reverse()'],
    ['<code>&#123;% extends "base.html" %&#125;</code> and <code>&#123;% block content %&#125;</code>', 'Template inheritance: a page fills the blocks of a base layout'],
    ['<code>&#123;% csrf_token %&#125;</code>', 'The hidden token that every POST form needs'],
    ['<code>&#123;# a comment #&#125;</code>', 'A comment that never reaches the browser']])}
{versus('Django templates and Jinja', ['', 'Django template language', 'Jinja (used by Flask)'], [
    ['Calling functions', 'No arguments allowed, keeps logic out of the page', 'Full expressions such as f(x, y)'],
    ['Speed', 'Fast enough for most sites', 'Faster for heavy templates'],
    ['Escaping', 'On by default', 'On by default in Flask'],
    ['In Django', 'The default', 'Possible, as a second backend in TEMPLATES']],
    'Both escape HTML by default. The Django language is kept simple on purpose, so designers can edit templates and logic stays in the views.')}
{note('Every value is <b>escaped</b>, so the script tag in the note shows up as harmless text. Only mark text as safe (the safe filter or mark_safe) when you made it yourself, never for text a user typed.', 'tip')}
''', kw=['templates', 'render', 'context', 'filters', 'tags', 'for', 'if', 'url tag', 'extends', 'block', 'template inheritance', 'escaping', 'Jinja'])

K.lesson('models', 'Models: Python classes that become tables', f'''
{run('models_intro')}
{table(['Field', 'Column in SQLite', 'Use it for'], [
    ['CharField(max_length=200)', 'varchar(200)', 'Short text such as a title'],
    ['TextField()', 'text', 'Long text such as a description'],
    ['IntegerField(), PositiveIntegerField()', 'integer', 'Whole numbers'],
    ['DecimalField(max_digits=6, decimal_places=2)', 'decimal', 'Money. Never use FloatField for money'],
    ['BooleanField(default=True)', 'bool', 'Yes or no'],
    ['DateField(), DateTimeField(auto_now_add=True)', 'date, datetime', 'Dates. auto_now_add fills in the time of creation'],
    ['ForeignKey(Author, on_delete=models.CASCADE)', 'author_id plus an index', 'Many books for one author'],
    ['EmailField(), URLField(), SlugField()', 'varchar', 'Text with a check in forms']])}
{steps('What the example shows', [
    'Each model class becomes a table named app label plus model name, here shop_book. Django adds an id column as the primary key.',
    '<b>Book.objects</b> is the manager. create() inserts a row, all() and filter() give a <b>QuerySet</b>, get() returns exactly one object.',
    'Lookups such as <b>year__gte=1900</b> or <b>author__name__startswith="Frank"</b> become WHERE clauses. The double underscore can even follow a ForeignKey into the other table.',
    'related_name="books" gives the other direction: herbert.books.all().',
    'update() and delete() on a QuerySet change many rows with one SQL statement. str(queryset.query) shows the SQL Django wrote.'])}
{note('In a project you never call schema_editor yourself. You change models.py, run makemigrations to write a migration file, and migrate to run it. Chapter 4.2 goes much deeper into the ORM and migrations.', 'exam')}
''', kw=['models', 'fields', 'CharField', 'ForeignKey', 'DecimalField', 'manager', 'objects', 'QuerySet', 'filter', 'get', 'lookups', 'related_name', 'ORM', 'SQL'])

K.lesson('admin', 'The admin site', f'''
{run('admin_site')}
{table(['ModelAdmin option', 'What it changes'], [
    ['list_display = ["title", "year"]', 'The columns of the list page'],
    ['list_filter = ["in_stock"]', 'A filter box at the side'],
    ['search_fields = ["title"]', 'A search box. ?q=dune becomes WHERE title LIKE %dune%'],
    ['ordering = ["-year"]', 'The order of the list'],
    ['list_per_page = 50', 'How many rows on each page'],
    ['readonly_fields, fields, fieldsets', 'What the edit form shows and how'],
    ['inlines = [ReviewInline]', 'Edit related rows, such as reviews, on the same page']])}
{scene('a small shop with an office team', '<p>A bookshop keeps its stock in Django. The developers write the models and three lines of admin.py for each. The office team logs in at /admin/, searches books, fixes prices and adds new titles. Each person gets only the permissions they need, for example "can change book" but not "can delete book", and the admin keeps a history of every change.</p>')}
{note('The admin is for trusted staff, not for customers. Use a long random password for the superuser, keep DEBUG off in production, and consider a less obvious address than /admin/.', 'tip')}
''', kw=['admin', 'ModelAdmin', 'admin.register', 'list_display', 'search_fields', 'list_filter', 'createsuperuser', 'is_staff', 'permissions'])

K.lesson('maths', 'The maths: URL matching, pages, queries and hashing', f'''
{fxs(fx('URL matching', 'checks for a URL &le; number of patterns', 'Django tries patterns from the top: with 40 patterns the worst case is 40 checks, still well under a millisecond.'),
     fx('Number of pages', 'pages = &lceil; n / per page &rceil;', '1,234 books at 50 a page: &lceil;24.68&rceil; = 25 pages.', key=True),
     fx('OFFSET of a page', 'OFFSET = (page &minus; 1) &times; per page', 'Page 3 at 50 a page: LIMIT 50 OFFSET 100.', key=True),
     fx('The N + 1 problem', 'queries = 1 + n', 'A list of 50 books that reads book.author in the template: 1 + 50 = 51 queries. select_related makes it 1.', key=True),
     fx('Hashing cost', 'guesses/s = hashes per second / iterations', 'Django 6.1 uses PBKDF2 with 1,500,000 iterations: 10<sup>9</sup> hashes per second give about 667 guesses per second.'),
     fx('Workers needed (Little&#39;s law)', 'busy workers = requests per second &times; seconds per request', '200 requests per second at 0.05 s each keep 10 workers busy.'))}
{steps('Worked example: why the list page is slow', [
    'A page shows 50 books with their authors. The view uses Book.objects.all() and the template shows book.author.name.',
    'The first query reads the 50 books. Each book.author then runs one more query, 50 in total.',
    'At 2 ms a query that is 51 &times; 2 = 102 ms only for the database.',
    'Book.objects.select_related("author") joins the two tables, so one query reads everything: about 3 ms.',
    eq('51 queries &rarr; 1 query, about 34 times faster')])}
''', kw=['URL matching', 'pagination', 'OFFSET', 'N+1 problem', 'select_related', 'PBKDF2', "Little's law", 'workers'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Make a project and an app, write views and URL patterns, and show data with templates.</p>',
    '<p>Write models, run migrations, use QuerySets with lookups, and register the models in the admin.</p>',
    '<p>Use template inheritance, class based views, include() for each app&#39;s URLs, and keep settings safe for production.</p>',
    '<p>Know the whole request cycle: the handler, middleware order, URL resolving, the ORM&#39;s SQL, and how ASGI views and caching change it.</p>')}
{grow('Pages from URLs, views and templates.', 'Data from models and the admin.', 'A project you can deploy and grow.')}
{deep('How Django starts', '<p>django.setup() reads the settings, then fills the <b>apps registry</b>: it imports each app in INSTALLED_APPS, then each app&#39;s models module. Only after that can you use models, which is why the programs on this page import models after django.setup(). manage.py and wsgi.py do the same thing for you, using the DJANGO_SETTINGS_MODULE environment variable to find settings.py.</p>')}
{deep('Middleware is an onion', '<p>Each middleware wraps the next one. A request passes them from the top of MIDDLEWARE to the bottom, and the response passes them from the bottom to the top. A middleware can also answer at once, as CommonMiddleware does with the 301 and CsrfViewMiddleware with the 403. That is why the order in settings.MIDDLEWARE matters: SessionMiddleware must come before AuthenticationMiddleware, which needs the session.</p>')}
''', kw=['beginner', 'expert', 'apps registry', 'django.setup', 'DJANGO_SETTINGS_MODULE', 'middleware order', 'request cycle', 'ASGI'])

lc(257, 'Binary Tree Paths', 'binary-tree-paths', 'e', 'Depth first search that carries the path so far', 'Like listing every URL of a project whose urls.py files include each other. Walk down the tree, add each value to the path, and save the path at every leaf.', r'''
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(values):
    """Build a tree from a level order list like [1, 2, 3, None, 5] (helper for the tests)."""
    if not values:
        return None
    nodes = [None if v is None else TreeNode(v) for v in values]
    kids = nodes[1:]
    k = 0
    for node in nodes:
        if node is not None:
            if k < len(kids):
                node.left = kids[k]
            if k + 1 < len(kids):
                node.right = kids[k + 1]
            k += 2
    return nodes[0]


def binary_tree_paths(root):
    paths = []

    def walk(node, path):
        if node is None:
            return
        path = path + [str(node.val)]
        if node.left is None and node.right is None:
            paths.append("->".join(path))
            return
        walk(node.left, path)
        walk(node.right, path)

    walk(root, [])
    return paths
''', [('binary_tree_paths(build_tree([1, 2, 3, None, 5]))', ['1->2->5', '1->3']), ('binary_tree_paths(build_tree([1]))', ['1'])])
lc(228, 'Summary Ranges', 'summary-ranges', 'e', 'Walk once and close a range when the next number is not one more', 'The admin and paginators show ranges such as 1-3. Keep where the current range starts and close it when the numbers stop following each other.', r'''
def summary_ranges(nums):
    result = []
    i = 0
    while i < len(nums):
        start = nums[i]
        while i + 1 < len(nums) and nums[i + 1] == nums[i] + 1:
            i += 1
        if nums[i] == start:
            result.append(str(start))
        else:
            result.append(f"{start}->{nums[i]}")
        i += 1
    return result
''', [('summary_ranges([0, 1, 2, 4, 5, 7])', ['0->2', '4->5', '7']), ('summary_ranges([0, 2, 3, 4, 6, 8, 9])', ['0', '2->4', '6', '8->9']), ('summary_ranges([])', [])])
lc(599, 'Minimum Index Sum of Two Lists', 'minimum-index-sum-of-two-lists', 'e', 'A dict from name to position', 'Like joining two lists of favourites in the ORM. Store the positions of the first list in a dict, then look up each name of the second list once.', r'''
def find_restaurant(list1, list2):
    position = {name: i for i, name in enumerate(list1)}
    best = None
    result = []
    for j, name in enumerate(list2):
        if name in position:
            total = position[name] + j
            if best is None or total < best:
                best = total
                result = [name]
            elif total == best:
                result.append(name)
    return result
''', [('find_restaurant(["Shogun", "Tapioca Express", "Burger King", "KFC"], ["Piatti", "The Grill at Torrey Pines", "Hungry Hunter Steakhouse", "Shogun"])', ['Shogun']), ('find_restaurant(["Shogun", "Tapioca Express", "Burger King", "KFC"], ["KFC", "Shogun", "Burger King"])', ['Shogun']), ('find_restaurant(["happy", "sad", "good"], ["sad", "happy", "good"])', ['sad', 'happy'])])
lc(1441, 'Build an Array With Stack Operations', 'build-an-array-with-stack-operations', 'm', 'Write down the operations, like makemigrations does', 'makemigrations writes a list of operations that turn the old state into the new one. Here: read the numbers 1, 2, 3 ... in order, Push each one, and Pop it again when it is not in target.', r'''
def build_array(target, n):
    operations = []
    wanted = set(target)
    for number in range(1, target[-1] + 1):
        operations.append("Push")
        if number not in wanted:
            operations.append("Pop")
    return operations
''', [('build_array([1, 3], 3)', ['Push', 'Push', 'Pop', 'Push']), ('build_array([1, 2, 3], 3)', ['Push', 'Push', 'Push']), ('build_array([1, 2], 4)', ['Push', 'Push'])])
lc(1003, 'Check If Word Is Valid After Substitutions', 'check-if-word-is-valid-after-substitutions', 'm', 'A stack, the same way template tags must close', 'A Django template is only valid when every {% block %} has its {% endblock %} in the right order. Here "abc" plays that part: push letters and remove "abc" whenever it appears on top.', r'''
def is_valid(s):
    stack = []
    for ch in s:
        stack.append(ch)
        if stack[-3:] == ["a", "b", "c"]:
            del stack[-3:]
    return not stack
''', [('is_valid("aabcbc")', True), ('is_valid("abcabcababcc")', True), ('is_valid("abccba")', False)])
lc(1487, 'Making File Names Unique', 'making-file-names-unique', 'm', 'A dict with the next free number for each name', 'When two users upload photo.jpg, Django storage saves the second one under a new name. Keep the next number to try for each name, so no name is checked again and again.', r'''
def get_folder_names(names):
    next_number = {}
    result = []
    for name in names:
        if name not in next_number:
            next_number[name] = 1
            result.append(name)
            continue
        k = next_number[name]
        while f"{name}({k})" in next_number:
            k += 1
        new_name = f"{name}({k})"
        next_number[name] = k + 1
        next_number[new_name] = 1
        result.append(new_name)
    return result
''', [('get_folder_names(["pes", "fifa", "gta", "pes(2019)"])', ['pes', 'fifa', 'gta', 'pes(2019)']), ('get_folder_names(["gta", "gta(1)", "gta", "avalon"])', ['gta', 'gta(1)', 'gta(2)', 'avalon']), ('get_folder_names(["onepiece", "onepiece(1)", "onepiece(2)", "onepiece(3)", "onepiece"])', ['onepiece', 'onepiece(1)', 'onepiece(2)', 'onepiece(3)', 'onepiece(4)']), ('get_folder_names(["kaido", "kaido(1)", "kaido", "kaido(1)"])', ['kaido', 'kaido(1)', 'kaido(2)', 'kaido(1)(1)'])])
lc(1048, 'Longest String Chain', 'longest-string-chain', 'm', 'Sort by length, then dynamic programming on a dict', 'Like a migration history where every migration adds one field. Sort the words by length and, for each word, try removing one letter to find the best chain that ends just before it.', r'''
def longest_str_chain(words):
    best = {}
    for word in sorted(words, key=len):
        best[word] = 1
        for i in range(len(word)):
            shorter = word[:i] + word[i + 1:]
            if shorter in best:
                best[word] = max(best[word], best[shorter] + 1)
    return max(best.values())
''', [('longest_str_chain(["a", "b", "ba", "bca", "bda", "bdca"])', 4), ('longest_str_chain(["xbc", "pcxbcf", "xb", "cxbc", "pcxbc"])', 5), ('longest_str_chain(["abcd", "dbqca"])', 1)])
lc(1912, 'Design Movie Rental System', 'design-movie-rental-system', 'h', 'Sorted lists play the part of ORDER BY with an index', 'This is a small ORM: one table of copies, a query "cheapest 5 shops for a movie" and a report "cheapest 5 rented copies". Keep sorted lists of (price, shop) and (price, shop, movie) so each query only reads the first 5.', r'''
import bisect


class MovieRentingSystem:
    def __init__(self, n, entries):
        self.price = {}
        self.unrented = {}            # movie -> sorted list of (price, shop)
        self.rented = []              # sorted list of (price, shop, movie)
        for shop, movie, price in entries:
            self.price[(shop, movie)] = price
            bisect.insort(self.unrented.setdefault(movie, []), (price, shop))

    def search(self, movie):
        return [shop for price, shop in self.unrented.get(movie, [])[:5]]

    def rent(self, shop, movie):
        price = self.price[(shop, movie)]
        self.unrented[movie].remove((price, shop))
        bisect.insort(self.rented, (price, shop, movie))

    def drop(self, shop, movie):
        price = self.price[(shop, movie)]
        self.rented.remove((price, shop, movie))
        bisect.insort(self.unrented[movie], (price, shop))

    def report(self):
        return [[shop, movie] for price, shop, movie in self.rented[:5]]
''' + PLAY, [('play(MovieRentingSystem, ["MovieRentingSystem", "search", "rent", "rent", "report", "drop", "search"], [[3, [[0, 1, 5], [0, 2, 6], [0, 3, 7], [1, 1, 4], [1, 2, 7], [2, 1, 5]]], [1], [0, 1], [1, 2], [], [1, 2], [2]])', [None, [1, 0, 2], None, None, [[0, 1], [1, 2]], None, [0, 1]])])
lc(736, 'Parse Lisp Expression', 'parse-lisp-expression', 'h', 'A recursive parser with a stack of scopes', 'Like the context of a Django template: {% with %} adds names that live only inside its block, and inner names hide outer ones. Parse the tokens recursively and pass a new dict of names into every let.', r'''
def evaluate(expression):
    tokens = expression.replace("(", " ( ").replace(")", " ) ").split()
    pos = 0

    def lookup(name, scopes):
        for scope in reversed(scopes):
            if name in scope:
                return scope[name]
        return 0

    def value_of(token, scopes):
        if token[0] == "-" or token.isdigit():
            return int(token)
        return lookup(token, scopes)

    def parse(scopes):
        nonlocal pos
        if tokens[pos] != "(":
            token = tokens[pos]
            pos += 1
            return value_of(token, scopes)
        pos += 1                                   # skip "("
        word = tokens[pos]
        pos += 1
        if word == "add" or word == "mult":
            first = parse(scopes)
            second = parse(scopes)
            result = first + second if word == "add" else first * second
        else:                                      # let
            scopes = scopes + [{}]
            while True:
                if tokens[pos] == "(" or tokens[pos + 1] == ")":
                    result = parse(scopes)         # the last part is the value of the let
                    break
                name = tokens[pos]
                pos += 1
                scopes[-1][name] = parse(scopes)
        pos += 1                                   # skip ")"
        return result

    return parse([])
''', [('evaluate("(let x 2 (mult x (let x 3 y 4 (add x y))))")', 14), ('evaluate("(let x 3 x 2 x)")', 2), ('evaluate("(let x 1 y 2 x (add x y) (add x y))")', 5), ('evaluate("(add 1 -2)")', -1)])
lc(472, 'Concatenated Words', 'concatenated-words', 'h', 'Word break with a set and memory', 'Like checking that a URL slug such as "redbookshop" is made only of known words. For each word, test every cut point and remember which endings were already solved.', r'''
from functools import lru_cache


def find_all_concatenated_words_in_a_dict(words):
    known = set(words)
    result = []
    for word in words:
        if not word:
            continue

        @lru_cache(maxsize=None)
        def can_split(start):
            for end in range(start + 1, len(word) + 1):
                part = word[start:end]
                if part in known and part != word:
                    if end == len(word) or can_split(end):
                        return True
            return False

        if can_split(0):
            result.append(word)
    return result
''', [('sorted(find_all_concatenated_words_in_a_dict(["cat", "cats", "catsdogcats", "dog", "dogcatsdog", "hippopotamuses", "rat", "ratcatdogcat"]))', ['catsdogcats', 'dogcatsdog', 'ratcatdogcat']), ('find_all_concatenated_words_in_a_dict(["cat", "dog", "catdog"])', ['catdog'])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Problems that match the work of a Django project: paths in a tree of URL files, ranges for page links, joining two lists, writing operations like makemigrations, checking that tags close in order, unique upload names, a small ORM with ordered queries, scoped template variables and slugs made of words.</p>'), kw=['LeetCode', 'trees', 'stack', 'hash map', 'dynamic programming', 'parsing', 'design'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Django includes routing, views, templates, an ORM with migrations, users and an admin site. Its MTV pattern is MVC with other names.',
    'startproject makes the project, startapp makes each app, and manage.py runs every command. Add each app to INSTALLED_APPS.',
    'urlpatterns are tried from the top. Converters such as int: change the type, and names let reverse() and the url tag build links.',
    'render() fills a template with a context. Values are escaped, filters change them, and extends with blocks shares one layout.',
    'A model class is a table, makemigrations writes the changes and migrate runs them. QuerySets with lookups become SQL, and admin.register gives a full admin page.'],
    'Next: the Django ORM in depth, forms, users and tests.')}
{files('Three tasks: write the views and URLs of a book shop, write three Django template filters yourself, and build a tiny QuerySet with lookups and ordering.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which command makes a new app inside a Django project?', ['django-admin startproject books', 'python manage.py startapp books', 'python manage.py migrate books', 'pip install books'], 1, 'An app is one feature.', 'Then add "books" to INSTALLED_APPS.')
K.quiz('e', 'Where do you list the URL patterns?', ['settings.py', 'In urlpatterns in a urls.py file', 'models.py', 'admin.py'], 1, 'The URL dispatcher.', 'The project urls.py can include() the urls.py of each app.')
K.quiz('e', 'What does a Django model class become in the database?', ['A view', 'A table, with one column for each field', 'A template', 'A migration only'], 1, 'One class, one table.', 'makemigrations and migrate create the table.')
K.quiz('m', 'You added a model, but makemigrations says "No changes detected". What is the most likely reason?', ['The database is full', 'The app is not in INSTALLED_APPS', 'DEBUG is False', 'The model has no __str__'], 1, 'Django only looks at installed apps.', 'Add the app, then run makemigrations again.')
K.quiz('m', 'What does path("books/&lt;int:book_id&gt;/", book_detail) do with /books/seven/?', ['Calls book_detail with "seven"', 'Does not match, so Django tries the next pattern and maybe answers 404', 'Raises ValueError', 'Redirects to /books/7/'], 1, 'The int converter only matches digits.', 'So the view always gets an int.')
K.quiz('m', 'Why use reverse("book-detail", args=[3]) instead of writing "/books/3/"?', ['It is faster', 'The URL is written in one place, so links keep working when the pattern changes', 'It adds a CSRF token', 'It checks the database'], 1, 'Names, not addresses.', 'The template tag url does the same in templates.')
K.quiz('m', 'Why does /books get a 301 to /books/?', ['A bug', 'CommonMiddleware with APPEND_SLASH adds the missing slash when only the slash version matches', 'The browser adds it', 'Because of CSRF'], 1, 'APPEND_SLASH.', 'It only works for GET, because a redirect loses the POST body.')
K.quiz('m', 'A template shows &#123;&#123; note &#125;&#125; and note is "&lt;b&gt;hi&lt;/b&gt;". What does the browser show?', ['hi in bold', 'The text &lt;b&gt;hi&lt;/b&gt;, because Django escapes it', 'Nothing', 'An error'], 1, 'Autoescape.', 'This blocks cross site scripting (XSS).')
K.quiz('m', 'What is the difference between get() and filter() on a manager?', ['None', 'get() returns one object and raises an error for zero or many rows, filter() returns a QuerySet of any size', 'filter() is slower', 'get() changes data'], 1, 'One object or a set.', 'get() raises DoesNotExist or MultipleObjectsReturned.')
K.quiz('h', 'A POST form in your template always gets 403 Forbidden. What is missing?', ['A model', 'The &#123;% csrf_token %&#125; tag inside the form', 'APPEND_SLASH', 'A superuser'], 1, 'CsrfViewMiddleware.', 'The token proves the form came from your own site.')
K.quiz('h', 'Why must SessionMiddleware come before AuthenticationMiddleware?', ['It does not matter', 'Authentication reads the user id from the session, so the session must be loaded first', 'For speed', 'Because of templates'], 1, 'Order of the onion.', 'Middleware runs from the top of the list on the way in.')
K.quiz('x', 'In the style of an MIT 6.170 software design exam: a list page shows 100 orders and their customers, and the database log shows 101 queries. What is the problem, and the Django fix?', ['Too many indexes, drop them', 'The N + 1 problem: one query for the orders and one per order for its customer. Use select_related("customer")', 'Missing migrations, run migrate', 'The template cache, clear it'], 1, 'Count: 1 + n.', 'select_related joins the tables so one query reads everything.')
K.quiz('x', 'In the style of a Stanford CS 142 web exam: why is DEBUG = True dangerous on a public server?', ['It is slower only', 'Error pages show code, settings and data to anyone, and Django keeps every SQL query in memory', 'It turns off the admin', 'It removes CSRF'], 1, 'Detailed error pages.', 'Run python manage.py check --deploy before going live.')

K.calc('e', '1,234 books, 50 on each page. How many pages?', '25', 'Round up.', ['1,234 / 50 = 24.68.', 'A part page is still a page, so round up.', eq('25 pages')], check=-(-1234 // 50))
K.calc('e', 'Page 3 with 50 books a page. What is the OFFSET in SQL?', '100', '(page &minus; 1) &times; size.', ['Pages 1 and 2 are skipped.', '(3 &minus; 1) &times; 50.', eq('OFFSET 100')], check=(3 - 1) * 50)
K.calc('e', 'A list shows 50 books and reads book.author for each. How many queries without select_related?', '51', '1 + n.', ['1 query for the books.', '1 more for each of the 50 authors.', eq('51 queries')], check=1 + 50)
K.calc('m', 'Each query takes 2 ms. How many ms does the database work of that page take?', '102', 'queries &times; time.', ['51 queries.', '51 &times; 2 ms.', eq('102 ms')], check=51 * 2)
K.calc('m', 'A computer makes 10<sup>9</sup> SHA-256 hashes a second. Django uses 1,500,000 PBKDF2 iterations. About how many guesses per second? Round to a whole number.', '667', 'Divide by the iterations.', ['Each guess costs 1,500,000 hashes.', '1,000,000,000 / 1,500,000 &asymp; 666.7.', eq('&asymp; 667 guesses per second')], check=10 ** 9 / 1_500_000, tol=0.5)
K.calc('m', '200 requests a second, 0.05 s each. How many workers are busy on average?', '10', "Little's law.", ['Busy = rate &times; time.', '200 &times; 0.05.', eq('10 workers')], check=200 * 0.05)
K.calc('m', 'urlpatterns has 40 entries and the URL matches the last one. How many patterns does Django test?', '40', 'Top to bottom.', ['It stops at the first match.', 'The match is entry 40.', eq('40 checks')], check=40)
K.calc('m', 'Django keeps a session for 2 weeks by default (SESSION_COOKIE_AGE). How many seconds is that?', '1209600', 'weeks &times; 7 &times; 86,400.', ['One day is 86,400 s.', '14 days &times; 86,400.', eq('1,209,600 s')], check=14 * 86400)
K.calc('h', 'A DecimalField has max_digits=6 and decimal_places=2. What is the largest value it can hold?', '9999.99', '6 digits in total, 2 after the point.', ['4 digits before the point and 2 after.', 'All digits 9.', eq('9999.99')], check=9999.99, tol=0.001)
K.calc('x', 'In the style of a CMU 15-445 exam: the list of 1,000,000 books is sorted by title with an index. Reading page 20,000 with OFFSET reads all rows before it. With 50 a page, how many rows are read and thrown away?', '999950', 'OFFSET = (page &minus; 1) &times; size.', ['(20,000 &minus; 1) &times; 50 = 999,950.', 'All of these rows are read only to be skipped.', 'Keyset pagination (WHERE title &gt; last title) avoids this.', eq('999,950 rows')], check=(20000 - 1) * 50)

K.assign('views', 'e', 'Write the views and URLs of a book shop',
         '<p>The settings and the home page are ready. Write two views and add them to urlpatterns. <code>book_list</code> at /books/ answers &#123;"count": ..., "titles": [...]&#125; with the titles sorted A to Z. With ?after=YEAR it keeps only books newer than that year, and when YEAR is not a number it answers 400 with &#123;"error": "after must be a year"&#125;. <code>book_detail</code> at /books/&lt;int:book_id&gt;/ answers the book, or 404 with &#123;"error": "not found"&#125;. Name the URLs "book-list" and "book-detail". visit(url) sends a GET with the test client and returns [status, json].</p>',
         r'''
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
    titles = [book["title"] for book in STOCK]
    return JsonResponse({"titles": titles})


def book_detail(request, book_id):
    return JsonResponse(STOCK[0])


urlpatterns = [
    path("", home, name="home"),
]


def visit(url):
    response = Client().get(url)
    try:
        body = response.json()
    except ValueError:
        body = None
    return [response.status_code, body]

''', [('visit("/")', [200, {'shop': 'Django books'}]), ('visit("/books/")', [200, {'count': 3, 'titles': ['Dune', 'Emma', 'Hamlet']}]), ('visit("/books/?after=1700")', [200, {'count': 2, 'titles': ['Dune', 'Emma']}]), ('visit("/books/?after=old")', [400, {'error': 'after must be a year'}]), ('visit("/books/2/")', [200, {'id': 2, 'title': 'Emma', 'year': 1815}]), ('visit("/books/9/")', [404, {'error': 'not found'}]), ('visit("/books")', [301, None]), ('[reverse("book-list"), reverse("book-detail", args=[3])]', ['/books/', '/books/3/'])],
         r'''
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

''', 'Read request.GET.get("after") and check it with isdigit() before int(). JsonResponse(data, status=404) sets the status. The int converter in the pattern already turns the id into an int.', '<p>/books without the slash gives 301 because CommonMiddleware adds the slash. Raising Http404 would also give 404, but with an HTML page, so a JSON API returns its own JSON error instead. Step 5 shows Django REST framework, which does this work for you.</p>')
K.assign('filters', 'm', 'Write three Django template filters yourself',
         '<p>Django templates have filters such as &#123;&#123; title|slugify &#125;&#125;. Write them as plain functions. <code>slugify_text(value)</code>: change accented letters to plain ones (é becomes e), use lower case, remove everything that is not a letter, digit, underscore, space or hyphen, turn each run of spaces and hyphens into one hyphen, and strip hyphens and underscores at both ends. <code>truncate_words(value, count)</code>: keep the first count words and add " ..." when words were cut. <code>pluralize(number, suffix="s")</code>: "" for 1 and suffix otherwise, and with a suffix such as "y,ies" the part before the comma for 1 and the part after it for every other number.</p>',
         r'''
import re
import unicodedata


def slugify_text(value):
    return value.lower().replace(" ", "-")


def truncate_words(value, count):
    return value


def pluralize(number, suffix="s"):
    return suffix
''', [('slugify_text("Hello World!")', 'hello-world'), ('slugify_text("  Django  is   fun ")', 'django-is-fun'), ('slugify_text("Crème brûlée")', 'creme-brulee'), ('slugify_text("C\'est la vie - 2026")', 'cest-la-vie-2026'), ('slugify_text("--Top_10 books--")', 'top_10-books'), ('truncate_words("The quick brown fox jumps", 3)', 'The quick brown ...'), ('truncate_words("Short title", 5)', 'Short title'), ('truncate_words("  many   spaces here ", 2)', 'many spaces ...'), ('[pluralize(1), pluralize(2), pluralize(0)]', ['', 's', 's']), ('[pluralize(1, "es"), pluralize(3, "es")]', ['', 'es']), ('[pluralize(1, "y,ies"), pluralize(4, "y,ies")]', ['y', 'ies'])],
         r'''
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
''', 'unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii") removes the accents. Then two re.sub calls do the rest. split() with no argument handles any spaces.', '<p>This is almost exactly how django.utils.text.slugify works, and a real run of Django gave the same five slugs. Django&#39;s truncatewords adds the single character … instead of three dots. Slugs make readable URLs such as /books/creme-brulee/.</p>')
K.assign('queryset', 'h', 'Build a tiny QuerySet',
         '<p>Write the class <code>MiniQuerySet(rows)</code> over a list of dicts, with the same feel as the Django ORM. <code>filter(**lookups)</code> and <code>exclude(**lookups)</code> return a new MiniQuerySet. A key is a field name, maybe followed by __ and a lookup: exact (the default), gt, gte, lt, lte, in, startswith and icontains. Every lookup in one call must match. An unknown lookup raises ValueError. <code>order_by(*fields)</code> sorts by several fields, and a leading "-" means largest first. values_list, count and first are ready.</p>',
         r'''
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

    def filter(self, **lookups):
        return MiniQuerySet(self.rows)

    def exclude(self, **lookups):
        return MiniQuerySet(self.rows)

    def order_by(self, *fields):
        return MiniQuerySet(self.rows)

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
''', [('MiniQuerySet(BOOKS).filter(genre="sf").values_list("title")', ['Dune', 'Dune Messiah', 'Neuromancer']), ('MiniQuerySet(BOOKS).filter(year__gte=1900, price__lt=9).values_list("title")', ['Dune Messiah']), ('MiniQuerySet(BOOKS).exclude(genre="sf").order_by("-year").values_list("title")', ['Emma', 'Hamlet']), ('MiniQuerySet(BOOKS).order_by("price", "-year").values_list("title")', ['Emma', 'Hamlet', 'Dune Messiah', 'Neuromancer', 'Dune']), ('MiniQuerySet(BOOKS).filter(title__icontains="DUNE").count()', 2), ('MiniQuerySet(BOOKS).filter(genre__in=["play", "novel"]).order_by("year").first()["title"]', 'Hamlet'), ('MiniQuerySet(BOOKS).filter(title__startswith="Z").first()', None), ('query_error("year__between")', 'ValueError')],
         r'''
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
''', 'key.partition("__") splits "year__gte" into the field and the lookup. Keep the lookups in a dict of small functions. For order_by, sort once per field starting from the last one, because sorted() keeps the order of equal items.', '<p>The real QuerySet does not filter Python lists. It builds an SQL query step by step and runs it only when you read the results, which is called lazy evaluation. Chapter 4.2 shows that, with the SQL Django writes.</p>')

K.must('Project', 'django-admin startproject mysite, python manage.py startapp books, add "books" to INSTALLED_APPS. manage.py runserver, makemigrations, migrate, createsuperuser, shell, check --deploy.')
K.must('URLs and views', 'urlpatterns = [path("books/&lt;int:book_id&gt;/", views.book_detail, name="book-detail")], include("books.urls"). A view takes request and returns HttpResponse or JsonResponse. Http404, redirect, reverse.')
K.must('Templates', 'render(request, "books/list.html", context). {{ value|filter }}, {% for %}{% empty %}{% endfor %}, {% if %}, {% url "name" arg %}, {% extends %} with {% block %}, {% csrf_token %} in POST forms. Values are escaped.')
K.must('Models', 'class Book(models.Model) with CharField, DecimalField, ForeignKey(on_delete=...). Book.objects.create / all / filter(year__gte=1900) / get / update / delete. related_name for the other side.')
K.must('Admin', '@admin.register(Book) class BookAdmin(admin.ModelAdmin) with list_display, list_filter, search_fields. path("admin/", admin.site.urls). Only staff users can log in.')

T = K.topic(
    slug='py-django', topic='py-django', step=(4, 'Django: the framework with everything built in', 'py-w4', 'Build full websites with Django: a project and its apps, URLs, views, templates, models and the admin, then the ORM in depth, forms, users and tests.', 'Intermediate'),
    title='Django basics: project, URLs, views, templates, models and admin', short='Django basics', badge='4.1', minutes=110,
    lead='Build your first Django site. Make a project and an app, send URLs to views, show pages with templates, store data with models and manage it in the admin site.',
    desc='What Django is and the MTV pattern, Django compared with Flask and FastAPI, startproject and startapp, the files of a project, manage.py commands, urlpatterns and path converters, reverse and named URLs, function and class based views, HttpRequest, HttpResponse, JsonResponse, Http404 and redirect, APPEND_SLASH and CSRF, the template language with filters, tags and inheritance, autoescaping, models and fields, the manager and QuerySets with lookups, the admin site with ModelAdmin, the request cycle through middleware, and the maths of pagination, the N + 1 problem and workers.',
    summary='Project and apps, urlpatterns, views, templates, models with QuerySets, and the admin site.',
    keywords=['Django', 'startproject', 'startapp', 'urlpatterns', 'views', 'templates', 'models', 'QuerySet', 'admin', 'middleware'],
    recap='<p>urls.py sends a request to a view, the view asks the models for data and renders a template, and the admin gives staff a page for every model.</p>',
    added='2026-11-07', leet=leet_items())
