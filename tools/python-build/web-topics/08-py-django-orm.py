# Web and APIs 4.2: the Django ORM in depth, migrations, forms, users and tests. Checked against the Django 6.1
# documentation (making queries, QuerySet API reference, aggregation, query expressions, database access
# optimization, migrations and writing migrations, forms and ModelForms, form and field validation, the auth system
# and permissions, database transactions, testing tools) with real runs of Django 6.1.3 on Python 3.14.
# The migrations program runs real manage.py commands and uses local(). The others run in the page.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, lc, leet, files, grow, leet_items

chapter('py-django-orm')
K = Kit()

K.code('orm_queries', r'''
import os

import django
from django.apps import AppConfig
from django.conf import settings


class ShopConfig(AppConfig):
    name = "__main__"
    label = "shop"
    path = os.getcwd()


settings.configure(
    SECRET_KEY="dev-only",
    INSTALLED_APPS=["__main__.ShopConfig"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
)
django.setup()

from django.db import connection, models
from django.db.models import Avg, Count, F, Q, Sum


class Author(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=50)


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)


class Book(models.Model):
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")   # many books, one author
    tags = models.ManyToManyField(Tag, related_name="books")                             # many to many

    def __str__(self):
        return self.title


with connection.schema_editor() as editor:
    for model in (Author, Tag, Book):
        editor.create_model(model)

herbert = Author.objects.create(name="Frank Herbert", country="USA")
austen = Author.objects.create(name="Jane Austen", country="UK")
gibson = Author.objects.create(name="William Gibson", country="USA")
sf, classic = Tag.objects.create(name="sf"), Tag.objects.create(name="classic")
for title, year, price, stock, author, tags in [
    ("Dune", 1965, "9.99", 4, herbert, [sf, classic]),
    ("Dune Messiah", 1969, "8.50", 0, herbert, [sf]),
    ("Emma", 1815, "5.00", 2, austen, [classic]),
    ("Persuasion", 1817, "6.00", 1, austen, [classic]),
    ("Neuromancer", 1984, "9.00", 3, gibson, [sf]),
]:
    book = Book.objects.create(title=title, year=year, price=price, stock=stock, author=author)
    book.tags.set(tags)

# 1. A QuerySet is lazy: building it runs no SQL, reading it does
query = Book.objects.filter(year__gte=1900).exclude(stock=0).order_by("-price")
print("built, not run yet. Reading:", [book.title for book in query])

# 2. Q objects for OR and NOT, lookups across relations
either = Book.objects.filter(Q(author__country="UK") | Q(tags__name="sf", stock__gt=3)).distinct()
print("UK or (sf and stock > 3):", sorted(book.title for book in either))
print("not by Herbert:", list(Book.objects.filter(~Q(author=herbert)).values_list("title", flat=True)))

# 3. F expressions compare and change columns inside the database
print("price above 2 x stock:", list(Book.objects.filter(price__gt=F("stock") * 2).values_list("title", flat=True)))
Book.objects.filter(title="Emma").update(stock=F("stock") + 10)     # UPDATE ... SET stock = stock + 10
print("Emma stock now", Book.objects.get(title="Emma").stock)

# 4. aggregate gives one answer, annotate gives one answer per row
print(Book.objects.aggregate(books=Count("id"), average=Avg("price"), in_stock=Sum("stock")))
per_author = Author.objects.annotate(n=Count("books")).filter(n__gte=2).order_by("name")
print("authors with 2 or more books:", [(a.name, a.n) for a in per_author])
print(list(Tag.objects.annotate(n=Count("books")).order_by("name").values("name", "n")))

# 5. values, exists, first and the SQL behind it
print(Book.objects.filter(author__name="Jane Austen").values("title", "year").first())
print("any book before 1800?", Book.objects.filter(year__lt=1800).exists())
print(Author.objects.annotate(n=Count("books")).filter(n__gte=2).query)''', long=True)
K.code('n_plus_one', r'''
import os

import django
from django.apps import AppConfig
from django.conf import settings


class ShopConfig(AppConfig):
    name = "__main__"
    label = "shop"
    path = os.getcwd()


settings.configure(
    SECRET_KEY="dev-only",
    INSTALLED_APPS=["__main__.ShopConfig"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
)
django.setup()

from django.db import connection, models
from django.test.utils import CaptureQueriesContext


class Author(models.Model):
    name = models.CharField(max_length=100)


class Tag(models.Model):
    name = models.CharField(max_length=30)


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    tags = models.ManyToManyField(Tag)


with connection.schema_editor() as editor:
    for model in (Author, Tag, Book):
        editor.create_model(model)

tags = [Tag.objects.create(name=name) for name in ["sf", "classic", "funny"]]
for i in range(20):
    author = Author.objects.create(name=f"Author {i}")
    book = Book.objects.create(title=f"Book {i}", author=author)
    book.tags.set(tags[: i % 3 + 1])


def count_queries(label, make_rows):
    with CaptureQueriesContext(connection) as captured:
        rows = make_rows()
    print(f"{label:38} {len(captured.captured_queries):3} queries   first row: {rows[0]}")
    return captured


# 1. The N + 1 problem: one query for the books, then one more for EACH author
count_queries("plain loop, book.author", lambda: [(b.title, b.author.name) for b in Book.objects.all()])

# 2. select_related follows a ForeignKey with a JOIN: one query in total
done = count_queries("select_related('author')",
                     lambda: [(b.title, b.author.name) for b in Book.objects.select_related("author")])
print("   SQL:", done.captured_queries[0]["sql"][:110], "...")

# 3. Many to many cannot be a simple JOIN. Without help: 1 + 20 queries
count_queries("plain loop, book.tags.all()", lambda: [(b.title, len(b.tags.all())) for b in Book.objects.all()])

# 4. prefetch_related runs ONE extra query for all tags and joins them in Python: 2 queries
count_queries("prefetch_related('tags')",
              lambda: [(b.title, len(b.tags.all())) for b in Book.objects.prefetch_related("tags")])

# 5. Ask only for what you need: values_list reads two columns, no model objects at all
count_queries("values_list('title', 'author__name')",
              lambda: list(Book.objects.values_list("title", "author__name")))''', long=True)
K.code('migrations_demo', r'''
import os
import subprocess
import sys
import tempfile

# A real project in a temporary folder. Each manage.py command runs exactly as in a terminal.
work = tempfile.mkdtemp()


def manage(*command):
    print("$ python manage.py", " ".join(command))
    result = subprocess.run([sys.executable, "manage.py", *command], cwd=site, capture_output=True, text=True)
    output = (result.stdout + result.stderr).strip()
    if output:
        print("  " + output.replace("\n", "\n  "))


def write(relative_path, text):
    with open(os.path.join(site, relative_path), "w") as f:
        f.write(text)


subprocess.run([sys.executable, "-m", "django", "startproject", "mysite", work], check=True)
site = work
subprocess.run([sys.executable, "manage.py", "startapp", "books"], cwd=site, check=True)
settings_path = os.path.join(site, "mysite", "settings.py")
text = open(settings_path).read().replace('"django.contrib.staticfiles",', '"django.contrib.staticfiles",\n    "books",')
open(settings_path, "w").write(text)

# Version 1 of the model
write("books/models.py", "from django.db import models\n\n\nclass Book(models.Model):\n"
                         "    title = models.CharField(max_length=200)\n")
manage("makemigrations", "books")
manage("migrate", "books")
manage("shell", "--no-imports", "-c", "from books.models import Book; Book.objects.create(title='Dune Messiah'); "
                      "Book.objects.create(title='The Hobbit'); print(Book.objects.count(), 'books')")

# Version 2: a new field with a default, so old rows get a value
write("books/models.py", "from django.db import models\n\n\nclass Book(models.Model):\n"
                         "    title = models.CharField(max_length=200)\n"
                         "    slug = models.SlugField(max_length=200, default='')\n")
manage("makemigrations", "books", "--name", "add_slug")
manage("sqlmigrate", "books", "0002")

# A data migration: Python code that fills the new column for the rows that already exist
manage("makemigrations", "books", "--empty", "--name", "fill_slugs")
write("books/migrations/0003_fill_slugs.py", """from django.db import migrations
from django.utils.text import slugify


def fill_slugs(apps, schema_editor):
    Book = apps.get_model("books", "Book")        # the model as it was at this migration
    for book in Book.objects.all():
        book.slug = slugify(book.title)
        book.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [("books", "0002_add_slug")]
    operations = [migrations.RunPython(fill_slugs, migrations.RunPython.noop)]
""")
manage("migrate", "books")
manage("shell", "--no-imports", "-c", "from books.models import Book; print(list(Book.objects.values_list('title', 'slug')))")
manage("showmigrations", "books")
manage("migrate", "books", "0001")                  # going back: Django undoes 0003 and 0002
manage("showmigrations", "books")''', long=True)
K.code('forms_demo', r'''
import os

import django
from django.apps import AppConfig
from django.conf import settings


class ShopConfig(AppConfig):
    name = "__main__"
    label = "shop"
    path = os.getcwd()


settings.configure(
    SECRET_KEY="dev-only",
    INSTALLED_APPS=["__main__.ShopConfig"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
)
django.setup()

from django import forms
from django.db import connection, models


class Book(models.Model):
    title = models.CharField(max_length=40, unique=True)
    year = models.PositiveIntegerField()
    isbn = models.CharField(max_length=17, blank=True)     # room for the hyphens people type


with connection.schema_editor() as editor:
    editor.create_model(Book)
Book.objects.create(title="Dune", year=1965)


# ---------- forms.py: a plain Form checks any input ----------
class ContactForm(forms.Form):
    name = forms.CharField(max_length=50)
    email = forms.EmailField()
    age = forms.IntegerField(min_value=13, required=False)


form = ContactForm({"name": "Ann", "email": "ann@example", "age": "9"})
print("valid?", form.is_valid())
print("errors:", form.errors.get_json_data())

form = ContactForm({"name": " Ann ", "email": "ann@example.com", "age": "42"})
print("valid?", form.is_valid(), "cleaned:", form.cleaned_data)       # strings became int, spaces were stripped


# ---------- A ModelForm builds its fields from the model ----------
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "year", "isbn"]

    def clean_isbn(self):                                  # check one field
        isbn = self.cleaned_data["isbn"].replace("-", "")
        if isbn and (len(isbn) != 13 or not isbn.isdigit()):
            raise forms.ValidationError("An ISBN has 13 digits.")
        return isbn

    def clean(self):                                       # check fields together
        data = super().clean()
        if data.get("year") and data["year"] > 2026:
            self.add_error("year", "That year is in the future.")
        return data


for posted in [
    {"title": "Dune", "year": "1965", "isbn": ""},                       # unique title already used
    {"title": "Emma", "year": "2999", "isbn": "978-0-14-143958-7"},      # year in the future
    {"title": "Emma", "year": "1815", "isbn": "12-34"},                  # bad ISBN
    {"title": "Emma", "year": "1815", "isbn": "978-0-14-143958-7"},      # all good
]:
    form = BookForm(posted)
    if form.is_valid():
        book = form.save()                                 # INSERT, with the cleaned values
        print("saved:", book.id, book.title, book.year, book.isbn)
    else:
        print("errors:", {field: [e["message"] for e in errs] for field, errs in form.errors.get_json_data().items()})

print(BookForm()["title"])                                 # how one field renders as HTML''', long=True)
K.code('auth_demo', r'''
import logging

import django
from django.conf import settings

settings.configure(
    DEBUG=True,
    SECRET_KEY="dev-only",
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=["testserver"],
    INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions"],
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    ],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    LOGIN_URL="/login/",
)
django.setup()
logging.getLogger("django.request").setLevel(logging.ERROR)

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, Permission, User
from django.core.management import call_command
from django.http import HttpResponse
from django.test import Client
from django.urls import path

call_command("migrate", verbosity=0)                      # the tables of users, groups, permissions and sessions

# 1. Users: the password is stored only as a salted, slow hash
ann = User.objects.create_user("ann", "ann@example.com", "correct horse 42")
print("stored:", ann.password[:42], "...")
print("check:", ann.check_password("correct horse 42"), ann.check_password("wrong"))
print("authenticate:", authenticate(username="ann", password="correct horse 42"), authenticate(username="ann", password="x"))

# 2. Permissions: each model gets add, change, delete and view. Groups bundle them.
editors = Group.objects.create(name="editors")
editors.permissions.add(Permission.objects.get(codename="change_user"))
bob = User.objects.create_user("bob", password="another long one 7")
bob.groups.add(editors)
print("bob can change users?", bob.has_perm("auth.change_user"), " ann?", ann.has_perm("auth.change_user"))


# 3. Views protected by decorators
@login_required
def profile(request):
    return HttpResponse(f"Hello {request.user.username}")


@permission_required("auth.change_user", raise_exception=True)
def edit_users(request):
    return HttpResponse("You may edit users")


urlpatterns = [path("profile/", profile), path("users/edit/", edit_users)]

client = Client()
response = client.get("/profile/")
print("anonymous /profile/:", response.status_code, "->", response["Location"])
client.login(username="ann", password="correct horse 42")
print("ann /profile/:", client.get("/profile/").content.decode(), "| /users/edit/:", client.get("/users/edit/").status_code)
client.logout()
client.login(username="bob", password="another long one 7")
print("bob /users/edit/:", client.get("/users/edit/").status_code, client.get("/users/edit/").content.decode())''', long=True)
K.code('transactions_tests', r'''
import os
import sys
import unittest

import django
from django.apps import AppConfig
from django.conf import settings


class BankConfig(AppConfig):
    name = "__main__"
    label = "bank"
    path = os.getcwd()


settings.configure(
    SECRET_KEY="dev-only",
    INSTALLED_APPS=["__main__.BankConfig"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
)
django.setup()

from django.db import connection, models, transaction
from django.db.models import F
from django.test import TestCase


class Account(models.Model):
    owner = models.CharField(max_length=50)
    balance = models.IntegerField(default=0)                       # in cents, never a float for money


class NotEnoughMoney(Exception):
    pass


def transfer(from_id, to_id, cents):
    """Move money between two accounts: both changes happen, or neither does."""
    with transaction.atomic():
        Account.objects.filter(pk=to_id).update(balance=F("balance") + cents)
        sender = Account.objects.get(pk=from_id)
        if sender.balance < cents:
            raise NotEnoughMoney(f"{sender.owner} has only {sender.balance}")   # rolls back the update above
        Account.objects.filter(pk=from_id).update(balance=F("balance") - cents)


with connection.schema_editor() as editor:
    editor.create_model(Account)


# ---------- tests.py: each test runs inside a transaction that is rolled back afterwards ----------
class TransferTests(TestCase):
    @classmethod
    def setUpTestData(cls):                                         # runs once for the whole class
        cls.ann = Account.objects.create(owner="ann", balance=5000)
        cls.bob = Account.objects.create(owner="bob", balance=1000)

    def balances(self):
        return list(Account.objects.order_by("owner").values_list("balance", flat=True))

    def test_transfer_moves_money(self):
        transfer(self.ann.pk, self.bob.pk, 1500)
        self.assertEqual(self.balances(), [3500, 2500])

    def test_not_enough_money_changes_nothing(self):
        with self.assertRaises(NotEnoughMoney):
            transfer(self.bob.pk, self.ann.pk, 9999)
        self.assertEqual(self.balances(), [5000, 1000])           # bob was NOT paid half a transfer

    def test_each_test_starts_clean(self):
        self.assertEqual(self.balances(), [5000, 1000])           # the transfer of the first test is gone

    def test_query_count(self):
        with self.assertNumQueries(5):     # SAVEPOINT, UPDATE, SELECT, UPDATE, RELEASE (atomic inside a test)
            transfer(self.ann.pk, self.bob.pk, 1)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TransferTests)
result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
print("all passed" if result.wasSuccessful() else "some tests failed")''', long=True)

ORM = '''

import os

import django
from django.apps import AppConfig
from django.conf import settings

if not settings.configured:                     # the first solution in the file sets Django up for all of them
    class LeetConfig(AppConfig):
        name = __name__
        label = "leet"
        path = os.getcwd()

    settings.configure(INSTALLED_APPS=[__name__ + ".LeetConfig"], DEFAULT_AUTO_FIELD="django.db.models.AutoField",
                       DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}})
    django.setup()

from django.db import connection, models


def load(model, rows):
    """Create the table once, then fill it with the rows of the example (helper for the tests)."""
    if model._meta.db_table not in connection.introspection.table_names():
        with connection.schema_editor() as editor:
            editor.create_model(model)
    model.objects.all().delete()
    model.objects.bulk_create([model(**row) for row in rows])
'''

K.lesson('idea', 'The ORM: asking the database in Python', f'''
{src('Django 6.1 documentation: making queries, the QuerySet API, aggregation, query expressions, database access optimization, migrations, forms and ModelForms, validation, authentication and permissions, transactions and testing tools.')}
{wwh('An <b>ORM</b> (object relational mapper) lets you read and change database rows as Python objects. In Django you write Book.objects.filter(year__gte=1900) and Django writes, sends and reads the SQL for you.',
     'Writing SQL by hand for every page is slow, easy to get wrong and easy to make unsafe. Each database (SQLite, PostgreSQL, MySQL) also speaks a slightly different SQL. And the code that turns rows into objects is the same boring work every time.',
     'A QuerySet collects your conditions step by step and runs one SQL query only when you read the results. Values always travel as parameters, so input cannot change the SQL. The same Python works on every supported database, and migrations keep the tables in step with the models.')}
{viz('pydjangoorm')}
{versus('Three ways to talk to a database from Python', ['', 'Raw SQL (sqlite3)', 'Django ORM', 'SQLAlchemy'], [
    ['You write', 'SQL text with ? placeholders', 'Book.objects.filter(...)', 'select(Book).where(...) or the ORM'],
    ['Changes to tables', 'ALTER TABLE by hand', 'makemigrations and migrate', 'Alembic'],
    ['Joins', 'Written by hand', 'author__name follows the ForeignKey', 'join() or relationships'],
    ['Hard reports', 'Full SQL power', 'annotate, Subquery, Window, or raw() when needed', 'Very close to SQL'],
    ['Used with', 'Small scripts', 'Django', 'Flask, FastAPI, scripts']],
    'Use the ORM for almost everything in Django. Look at the SQL it writes with str(queryset.query) or the query count in tests, and drop to raw SQL only for the rare report the ORM cannot express.')}
''', kw=['ORM', 'QuerySet', 'SQL', 'lazy evaluation', 'SQLAlchemy', 'raw SQL', 'database'])

K.lesson('queries', 'QuerySets: filter, Q, F, aggregate and annotate', f'''
{run('orm_queries')}
{table(['Tool', 'Example', 'SQL it becomes'], [
    ['filter and exclude', 'filter(year__gte=1900).exclude(stock=0)', 'WHERE year &gt;= 1900 AND NOT stock = 0'],
    ['Lookups', 'title__icontains="dune", year__in=[1965, 1969], author__country="UK"', 'LIKE, IN, a JOIN to author'],
    ['Q objects', 'Q(a) | Q(b), ~Q(c)', 'OR and NOT'],
    ['F expressions', 'filter(price__gt=F("stock") * 2), update(stock=F("stock") + 10)', 'Compare or change columns inside the database'],
    ['aggregate', 'aggregate(Avg("price"))', 'One answer for the whole QuerySet: a dict'],
    ['annotate', 'annotate(n=Count("books"))', 'One extra value per row, with GROUP BY'],
    ['values, values_list', 'values("title", "year"), values_list("title", flat=True)', 'Only these columns, as dicts or tuples'],
    ['Relations', 'ForeignKey, ManyToManyField, OneToOneField', 'author_id column, a join table, a unique author_id']])}
{steps('What the example shows', [
    'Building the QuerySet ran no SQL. Reading it in the list comprehension ran exactly one query.',
    'Q objects combine conditions with | (OR) and ~ (NOT). distinct() removes the copies that a join through tags can make.',
    'F("stock") means "the value in this row". update(stock=F("stock") + 10) runs inside the database, so two users at the same time cannot overwrite each other.',
    'aggregate returned one dict. annotate gave every author an n, and filter(n__gte=2) after it became HAVING.',
    'The printed SQL shows the LEFT OUTER JOIN, GROUP BY and HAVING that Django wrote.'])}
{note('The QuerySet keeps the rows it read. Looping twice over the same QuerySet runs one query, but calling filter() again builds a new QuerySet and runs new SQL. Save a QuerySet in a variable when you need it twice.', 'tip')}
''', kw=['filter', 'exclude', 'lookups', 'Q objects', 'F expressions', 'aggregate', 'annotate', 'Count', 'Avg', 'values', 'ManyToManyField', 'distinct', 'HAVING'])

K.lesson('nplus1', 'Fast queries: the N + 1 problem', f'''
{run('n_plus_one')}
{versus('select_related and prefetch_related', ['', 'select_related("author")', 'prefetch_related("tags")'], [
    ['Works for', 'ForeignKey and OneToOne (one related row)', 'ManyToMany and the reverse of a ForeignKey (many rows)'],
    ['How', 'One query with a JOIN', 'One extra query with WHERE id IN (...), joined in Python'],
    ['Queries for 20 books', '1', '2'],
    ['Watch out', 'Joining many tables makes wide rows', 'Filtering inside needs a Prefetch object']],
    'Look at every loop in a template that reads a related object. If it reads one row per item, use select_related. If it reads a list per item, use prefetch_related.')}
{table(['More ways to make queries cheaper', 'Why'], [
    ['only("title") or defer("description")', 'Read fewer columns'],
    ['values_list("title", flat=True)', 'No model objects at all, only the values'],
    ['exists() instead of len(qs) &gt; 0', 'The database stops at the first row'],
    ['count() instead of len(qs)', 'SELECT COUNT(*), not every row'],
    ['bulk_create, bulk_update', 'Many rows in one query'],
    ['db_index=True or Meta.indexes', 'An index makes filters and order_by on that column fast'],
    ['iterator()', 'Streams a huge QuerySet without keeping it all in memory']])}
{note('In tests, assertNumQueries(n) fails when a change adds queries, so an N + 1 problem cannot sneak back in. In development, django-debug-toolbar shows every query of a page.', 'exam')}
''', kw=['N+1 problem', 'select_related', 'prefetch_related', 'JOIN', 'only', 'defer', 'exists', 'count', 'bulk_create', 'index', 'assertNumQueries', 'CaptureQueriesContext'])

K.lesson('migrations', 'Migrations: changing tables safely', f'''
{local('migrations_demo', 'It makes a real project in a temporary folder and runs manage.py commands. Install Django first with <code>pip install django</code>.')}
{table(['Command', 'What it does'], [
    ['makemigrations', 'Compares the models with the migration files and writes a new file with the changes'],
    ['makemigrations --empty --name fill_slugs', 'An empty migration for your own code, such as a data migration'],
    ['migrate', 'Runs every migration that is not applied yet, in dependency order'],
    ['migrate books 0001', 'Goes back: undoes every later migration of books'],
    ['sqlmigrate books 0002', 'Shows the SQL of a migration without running it'],
    ['showmigrations', 'Lists the migrations with [X] for applied'],
    ['makemigrations --check', 'Fails when a model change has no migration yet, useful in CI']])}
{steps('Rules that keep migrations safe', [
    'Commit the migration files to git together with the model change. Never edit a migration that others have already run, write a new one instead.',
    'A new column on a table with rows needs a default or null=True, otherwise Django asks what to put into the old rows.',
    'Split big changes: add the new column, fill it with a data migration (RunPython), and only then remove the old column in a later release.',
    'Inside RunPython use apps.get_model("books", "Book"), the model as it was at that migration, never an import of the current model.',
    'Give RunPython a reverse function (or RunPython.noop) so the migration can be undone.'])}
{note('SQLite cannot change most column types in place, so the SQL above makes a new table, copies the rows and renames it. PostgreSQL runs a short ALTER TABLE instead. Django picks the right way for each database.', 'tip')}
''', kw=['migrations', 'makemigrations', 'migrate', 'sqlmigrate', 'showmigrations', 'data migration', 'RunPython', 'apps.get_model', 'rollback', 'default'])

K.lesson('forms', 'Forms: checking what users send', f'''
{run('forms_demo')}
{table(['Step', 'What runs', 'Where your code goes'], [
    ['1. Bind', 'form = BookForm(request.POST)', 'In the view'],
    ['2. Field checks', 'to_python, required, max_length, min_value, unique (ModelForm)', 'Field options'],
    ['3. One field', 'clean_isbn() after the field checks pass', 'def clean_&lt;field&gt;(self): return the value'],
    ['4. Many fields', 'clean() with all cleaned values', 'def clean(self): use self.add_error'],
    ['5. Result', 'is_valid() is True: cleaned_data, or save() for a ModelForm', 'Redirect after saving'],
    ['6. Errors', 'form.errors, shown next to each field in the template', 'Render the form again']])}
{versus('Form and ModelForm', ['', 'forms.Form', 'forms.ModelForm'], [
    ['Fields come from', 'You list them', 'The model (Meta.model, Meta.fields)'],
    ['Saves to the database', 'No, you do it', 'form.save() makes or updates the row'],
    ['Model rules', 'Not used', 'max_length, unique and choices are checked for you'],
    ['Good for', 'Search, contact, login', 'Create and edit pages for a model']],
    'Use a ModelForm whenever the form edits a model, so the rules live in one place. Always list the fields in Meta.fields, so a new model field such as is_admin is never editable by accident.')}
{note('The usual view: if request.method == "POST", bind and check the form, save and redirect when it is valid. Otherwise make an empty form. Either way render the template, which shows the errors. In the template put &#123;% csrf_token %&#125; inside the form tag.', 'exam')}
''', kw=['forms', 'Form', 'ModelForm', 'is_valid', 'cleaned_data', 'clean_field', 'clean', 'ValidationError', 'add_error', 'form.errors', 'save'])

K.lesson('auth', 'Users, logins and permissions', f'''
{run('auth_demo')}
{table(['Part', 'What Django gives you'], [
    ['User model', 'username, email, password (a hash), is_active, is_staff, is_superuser, groups, user_permissions'],
    ['Passwords', 'create_user and set_password store PBKDF2 with 1,500,000 iterations and a random salt, check_password compares'],
    ['Login', 'authenticate(username=..., password=...) then login(request, user), or the ready LoginView'],
    ['In views', '@login_required, @permission_required, LoginRequiredMixin, PermissionRequiredMixin'],
    ['In templates', 'user.is_authenticated, user.username, perms.books.change_book'],
    ['Permissions', 'add, change, delete and view for every model, grouped with Group'],
    ['Your own user', 'AUTH_USER_MODEL = "accounts.User", set before the first migrate']])}
{note('Start every new project with a custom user model (class User(AbstractUser): pass) and AUTH_USER_MODEL. Changing it later, when tables already point to auth.User, is a painful migration.', 'tip')}
{note('login_required sends a person who is not logged in to LOGIN_URL with ?next=, as the 302 above shows. permission_required with raise_exception=True gives 403 instead, which is right for a logged in user who simply may not do this.', 'exam')}
''', kw=['authentication', 'User', 'create_user', 'check_password', 'authenticate', 'login', 'login_required', 'permission_required', 'permissions', 'Group', 'AUTH_USER_MODEL', 'AbstractUser'])

K.lesson('testing', 'Transactions and tests', f'''
{run('transactions_tests')}
{table(['Tool', 'Use it for'], [
    ['transaction.atomic()', 'Changes that must all happen or none: a with block or a decorator'],
    ['F("balance") + amount', 'Change a value inside the database, safe when two requests run at the same time'],
    ['select_for_update()', 'Lock rows until the transaction ends (PostgreSQL, MySQL)'],
    ['TestCase', 'Every test runs in a transaction that is rolled back, so tests never see each other&#39;s data'],
    ['setUpTestData', 'Rows made once for the whole class, which is fast'],
    ['self.client', 'The test client inside a TestCase: get, post, login, force_login'],
    ['assertContains, assertRedirects, assertNumQueries', 'Check a page, a redirect, or the number of queries'],
    ['python manage.py test', 'Finds tests.py and test_*.py, makes a test database, runs everything']])}
{note('Look at the query count: inside a test the atomic() of transfer becomes SAVEPOINT and RELEASE, because TestCase already opened a transaction around the test. Outside tests it is BEGIN and COMMIT.', 'exam')}
''', kw=['transaction', 'atomic', 'rollback', 'savepoint', 'select_for_update', 'TestCase', 'setUpTestData', 'assertNumQueries', 'manage.py test', 'test database'])

K.lesson('maths', 'The maths: query counts, indexes and transactions', f'''
{fxs(fx('Queries in a loop', 'N + 1 without help, 1 with select_related, 2 with prefetch_related', '20 books: 21, 1 and 2 queries.', key=True),
     fx('Time of a page', 'time &asymp; queries &times; round trip + work', '21 queries at 1.5 ms: 31.5 ms. 1 query: 1.5 ms plus a bigger row.', key=True),
     fx('Search without an index', 'rows read = n', '1,000,000 books: the database reads all of them.'),
     fx('Search with a B-tree index', 'steps &asymp; log<sub>b</sub>(n)', 'With about 100 keys per page: log<sub>100</sub>(1,000,000) = 3 page reads.', key=True),
     fx('Rows from a join table (many to many)', 'pairs = books &times; average tags', '20 books with 2 tags each: 40 rows in book_tags.'),
     fx('Weighted average (LeetCode 1251)', 'average = &Sigma;(price &times; units) / &Sigma;units', '(5 &times; 100 + 20 &times; 15) / 115 = 800 / 115 &asymp; 6.96.'))}
{steps('Worked example: is the index worth it?', [
    'A shop has 1,000,000 orders and the page filters by customer_id.',
    'Without an index the database scans every row: 1,000,000 rows.',
    'A B-tree index with about 100 keys per page needs log<sub>100</sub>(10<sup>6</sup>) = 6 / 2 = 3 page reads to find the first match.',
    'The cost: every INSERT also updates the index, and the index takes disk space. For a column you filter on often, that is a good deal.',
    eq('1,000,000 rows &rarr; about 3 page reads')])}
''', kw=['N+1', 'query count', 'index', 'B-tree', 'logarithm', 'weighted average', 'join table'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Write filter, exclude, get and order_by queries, and add relations with ForeignKey and ManyToManyField.</p>',
    '<p>Use Q, F, aggregate and annotate, run makemigrations and migrate, and check input with forms and ModelForms.</p>',
    '<p>Find N + 1 problems and fix them, write data migrations, protect views with permissions and test with TestCase and assertNumQueries.</p>',
    '<p>Read the SQL Django writes, design indexes, use Subquery, Window and transactions with locking, and plan zero downtime migrations.</p>')}
{grow('Queries that are right.', 'Queries that are fast.', 'Changes that are safe.')}
{deep('Subquery and OuterRef', '<p>A Subquery puts one query inside another. OuterRef("id") inside it means "the id of the row in the outer query". The LeetCode solutions use it to find the unique id of each employee and the price that was valid on each sale date. Django writes it as a correlated subquery in one SQL statement.</p>')}
{deep('Zero downtime migrations', '<p>On a busy site the old code keeps running while the new one starts. So a migration must work with both: first add a nullable column and deploy code that writes it, then fill old rows, then make the column required, and only in a later release remove what the old code needed. This is called expand and contract.</p>')}
''', kw=['beginner', 'expert', 'Subquery', 'OuterRef', 'Window', 'zero downtime', 'expand and contract'])

lc(1683, 'Invalid Tweets', 'invalid-tweets', 'e', 'annotate(Length(...)) then filter', 'A computed column: annotate each tweet with the length of its text, then keep the ones longer than 15.', ORM + r'''
from django.db.models.functions import Length


class Tweet(models.Model):
    tweet_id = models.IntegerField(primary_key=True)
    content = models.CharField(max_length=500)


def invalid_tweets(rows):
    load(Tweet, rows)
    long_ones = Tweet.objects.annotate(size=Length("content")).filter(size__gt=15)
    return sorted(long_ones.values_list("tweet_id", flat=True))
''', [('invalid_tweets([{"tweet_id": 1, "content": "Let us Code"}, {"tweet_id": 2, "content": "More than fifteen chars are here!"}])', [2])])
lc(1378, 'Replace Employee ID With The Unique Identifier', 'replace-employee-id-with-the-unique-identifier', 'e', 'Subquery with OuterRef, a LEFT JOIN without a ForeignKey', 'The two tables share an id but have no ForeignKey. A Subquery that looks up the unique id for each employee works like a LEFT JOIN, and gives None when there is no match.', ORM + r'''
from django.db.models import OuterRef, Subquery


class Employee(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)


class EmployeeUNI(models.Model):
    id = models.IntegerField(primary_key=True)
    unique_id = models.IntegerField()


def replace_employee_id(employees, uni):
    load(Employee, employees)
    load(EmployeeUNI, uni)
    match = EmployeeUNI.objects.filter(id=OuterRef("id")).values("unique_id")[:1]
    rows = Employee.objects.annotate(unique_id=Subquery(match)).order_by("name")
    return [[row.unique_id, row.name] for row in rows]
''', [('replace_employee_id([{"id": 1, "name": "Alice"}, {"id": 7, "name": "Bob"}, {"id": 11, "name": "Meir"}, {"id": 90, "name": "Winston"}, {"id": 3, "name": "Jonathan"}], [{"id": 3, "unique_id": 1}, {"id": 11, "unique_id": 2}, {"id": 90, "unique_id": 3}])', [[None, 'Alice'], [None, 'Bob'], [1, 'Jonathan'], [2, 'Meir'], [3, 'Winston']])])
lc(1068, 'Product Sales Analysis I', 'product-sales-analysis-i', 'e', 'Follow a ForeignKey inside values()', 'With a ForeignKey, product__product_name in values() makes Django write the JOIN for you.', ORM + r'''
class Product(models.Model):
    product_id = models.IntegerField(primary_key=True)
    product_name = models.CharField(max_length=50)


class Sale(models.Model):
    sale_id = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    year = models.IntegerField()
    price = models.IntegerField()


def sales_analysis(sales, products):
    load(Product, products)
    load(Sale, sales)                    # product_id fills the ForeignKey
    rows = Sale.objects.order_by("sale_id").values_list("product__product_name", "year", "price")
    return [list(row) for row in rows]
''', [('sales_analysis([{"sale_id": 1, "product_id": 100, "year": 2008, "price": 5000}, {"sale_id": 2, "product_id": 100, "year": 2009, "price": 5000}, {"sale_id": 7, "product_id": 200, "year": 2011, "price": 9000}], [{"product_id": 100, "product_name": "Nokia"}, {"product_id": 200, "product_name": "Apple"}, {"product_id": 300, "product_name": "Samsung"}])', [['Nokia', 2008, 5000], ['Nokia', 2009, 5000], ['Apple', 2011, 9000]])])
lc(1661, 'Average Time of Process per Machine', 'average-time-of-process-per-machine', 'e', 'Conditional aggregation with Sum(Case(When(...)))', 'Group by machine. Add the end times and subtract the start times with Case and When, then divide by the number of processes.', ORM + r'''
from django.db.models import Case, Count, F, FloatField, Sum, When


class Activity(models.Model):
    machine_id = models.IntegerField()
    process_id = models.IntegerField()
    activity_type = models.CharField(max_length=5)
    timestamp = models.FloatField()


def average_processing_time(rows):
    load(Activity, rows)
    signed = Case(When(activity_type="end", then=F("timestamp")), default=-F("timestamp"), output_field=FloatField())
    groups = (Activity.objects.values("machine_id")
              .annotate(total=Sum(signed), processes=Count("process_id", distinct=True))
              .order_by("machine_id"))
    return [[g["machine_id"], round(g["total"] / g["processes"], 3)] for g in groups]
''', [('average_processing_time([{"machine_id": 0, "process_id": 0, "activity_type": "start", "timestamp": 0.712}, {"machine_id": 0, "process_id": 0, "activity_type": "end", "timestamp": 1.52}, {"machine_id": 0, "process_id": 1, "activity_type": "start", "timestamp": 3.14}, {"machine_id": 0, "process_id": 1, "activity_type": "end", "timestamp": 4.12}, {"machine_id": 1, "process_id": 0, "activity_type": "start", "timestamp": 0.55}, {"machine_id": 1, "process_id": 0, "activity_type": "end", "timestamp": 1.55}, {"machine_id": 1, "process_id": 1, "activity_type": "start", "timestamp": 0.43}, {"machine_id": 1, "process_id": 1, "activity_type": "end", "timestamp": 1.42}, {"machine_id": 2, "process_id": 0, "activity_type": "start", "timestamp": 4.1}, {"machine_id": 2, "process_id": 0, "activity_type": "end", "timestamp": 4.512}, {"machine_id": 2, "process_id": 1, "activity_type": "start", "timestamp": 2.5}, {"machine_id": 2, "process_id": 1, "activity_type": "end", "timestamp": 5.0}])', [[0, 0.894], [1, 0.995], [2, 1.456]])])
lc(1280, 'Students and Examinations', 'students-and-examinations', 'e', 'Count per group, then fill in the zeros', 'Every student must appear with every subject, even with 0 exams. Count the exams per (student, subject) with values() and annotate(), then loop over all pairs.', ORM + r'''
from django.db.models import Count


class Student(models.Model):
    student_id = models.IntegerField(primary_key=True)
    student_name = models.CharField(max_length=50)


class Subject(models.Model):
    subject_name = models.CharField(max_length=50, primary_key=True)


class Examination(models.Model):
    student_id = models.IntegerField()
    subject_name = models.CharField(max_length=50)


def students_and_examinations(students, subjects, exams):
    load(Student, students)
    load(Subject, subjects)
    load(Examination, exams)
    counts = {}
    for row in Examination.objects.values("student_id", "subject_name").annotate(n=Count("id")):
        counts[(row["student_id"], row["subject_name"])] = row["n"]
    result = []
    for student in Student.objects.order_by("student_id"):
        for subject in Subject.objects.order_by("subject_name"):
            key = (student.student_id, subject.subject_name)
            result.append([student.student_id, student.student_name, subject.subject_name, counts.get(key, 0)])
    return result
''', [('students_and_examinations([{"student_id": 1, "student_name": "Alice"}, {"student_id": 2, "student_name": "Bob"}], [{"subject_name": "Math"}, {"subject_name": "Physics"}], [{"student_id": 1, "subject_name": "Math"}, {"student_id": 1, "subject_name": "Math"}, {"student_id": 2, "subject_name": "Physics"}])', [[1, 'Alice', 'Math', 2], [1, 'Alice', 'Physics', 0], [2, 'Bob', 'Math', 0], [2, 'Bob', 'Physics', 1]])])
lc(1251, 'Average Selling Price', 'average-selling-price', 'e', 'Subquery for the price on the sale date, then a weighted average', 'Each sale needs the price that was valid on its date. A Subquery with OuterRef and two date lookups finds it, then Sum(price times units) / Sum(units) gives the weighted average.', ORM + r'''
from django.db.models import F, OuterRef, Subquery, Sum


class Price(models.Model):
    product_id = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.IntegerField()


class UnitSold(models.Model):
    product_id = models.IntegerField()
    purchase_date = models.DateField()
    units = models.IntegerField()


def average_selling_price(prices, sold):
    load(Price, prices)
    load(UnitSold, sold)
    price_then = Price.objects.filter(product_id=OuterRef("product_id"), start_date__lte=OuterRef("purchase_date"),
                                      end_date__gte=OuterRef("purchase_date")).values("price")[:1]
    totals = (UnitSold.objects.annotate(price=Subquery(price_then)).values("product_id")
              .annotate(money=Sum(F("price") * F("units")), units_total=Sum("units")))
    found = {row["product_id"]: round(row["money"] / row["units_total"], 2) for row in totals}
    products = sorted(set(Price.objects.values_list("product_id", flat=True)))
    return [[product, found.get(product, 0)] for product in products]
''', [('average_selling_price([{"product_id": 1, "start_date": "2019-02-17", "end_date": "2019-02-28", "price": 5}, {"product_id": 1, "start_date": "2019-03-01", "end_date": "2019-03-22", "price": 20}, {"product_id": 2, "start_date": "2019-02-01", "end_date": "2019-02-20", "price": 15}, {"product_id": 2, "start_date": "2019-02-21", "end_date": "2019-03-31", "price": 30}, {"product_id": 3, "start_date": "2019-01-01", "end_date": "2019-01-31", "price": 9}], [{"product_id": 1, "purchase_date": "2019-02-25", "units": 100}, {"product_id": 1, "purchase_date": "2019-03-01", "units": 15}, {"product_id": 2, "purchase_date": "2019-02-10", "units": 200}, {"product_id": 2, "purchase_date": "2019-03-22", "units": 30}])', [[1, 6.96], [2, 16.96], [3, 0]])])
lc(1211, 'Queries Quality and Percentage', 'queries-quality-and-percentage', 'e', 'Avg of a computed value and Count with a filter', 'Group by query name. Avg(rating / position) gives the quality, and Count with filter=Q(rating__lt=3) counts the poor results.', ORM + r'''
from django.db.models import Avg, Count, F, FloatField, Q
from django.db.models.functions import Cast


class QueryResult(models.Model):
    query_name = models.CharField(max_length=30)
    result = models.CharField(max_length=50)
    position = models.IntegerField()
    rating = models.IntegerField()


def queries_stats(rows):
    load(QueryResult, rows)
    groups = (QueryResult.objects.values("query_name")
              .annotate(quality=Avg(Cast("rating", FloatField()) / F("position")),
                        poor=Count("id", filter=Q(rating__lt=3)), total=Count("id"))
              .order_by("query_name"))
    return [[g["query_name"], round(g["quality"], 2), round(100 * g["poor"] / g["total"], 2)] for g in groups]
''', [('queries_stats([{"query_name": "Dog", "result": "Golden Retriever", "position": 1, "rating": 5}, {"query_name": "Dog", "result": "German Shepherd", "position": 2, "rating": 5}, {"query_name": "Dog", "result": "Mule", "position": 200, "rating": 1}, {"query_name": "Cat", "result": "Shirazi", "position": 5, "rating": 2}, {"query_name": "Cat", "result": "Siamese", "position": 3, "rating": 3}, {"query_name": "Cat", "result": "Sphynx", "position": 7, "rating": 4}])', [['Cat', 0.66, 33.33], ['Dog', 2.5, 33.33]])])
lc(607, 'Sales Person', 'sales-person', 'e', 'exclude with a subquery of ids', 'Find the sales people with an order for the company RED, as a QuerySet of ids, and exclude them. Django puts the inner query into one SQL statement with NOT IN.', ORM + r'''
class SalesPerson(models.Model):
    sales_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)


class Company(models.Model):
    com_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)


class SalesOrder(models.Model):
    order_id = models.IntegerField(primary_key=True)
    com_id = models.IntegerField()
    sales_id = models.IntegerField()


def sales_person(people, companies, orders):
    load(SalesPerson, people)
    load(Company, companies)
    load(SalesOrder, orders)
    red = Company.objects.filter(name="RED").values("com_id")
    sold_to_red = SalesOrder.objects.filter(com_id__in=red).values("sales_id")
    return sorted(SalesPerson.objects.exclude(sales_id__in=sold_to_red).values_list("name", flat=True))
''', [('sales_person([{"sales_id": 1, "name": "John"}, {"sales_id": 2, "name": "Amy"}, {"sales_id": 3, "name": "Mark"}, {"sales_id": 4, "name": "Pam"}, {"sales_id": 5, "name": "Alex"}], [{"com_id": 1, "name": "RED"}, {"com_id": 2, "name": "ORANGE"}, {"com_id": 3, "name": "YELLOW"}, {"com_id": 4, "name": "GREEN"}], [{"order_id": 1, "com_id": 3, "sales_id": 4}, {"order_id": 2, "com_id": 4, "sales_id": 5}, {"order_id": 3, "com_id": 1, "sales_id": 1}, {"order_id": 4, "com_id": 1, "sales_id": 4}])', ['Alex', 'Amy', 'Mark'])])
lc(1193, 'Monthly Transactions I', 'monthly-transactions-i', 'm', 'Group by a computed month, Count and Sum with filters', 'Annotate each row with its month (the first 7 characters of the date), group by month and country, and use filter=Q(state="approved") inside Count and Sum.', ORM + r'''
from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce, Substr


class Transaction(models.Model):
    id = models.IntegerField(primary_key=True)
    country = models.CharField(max_length=10)
    state = models.CharField(max_length=10)
    amount = models.IntegerField()
    trans_date = models.CharField(max_length=10)


def monthly_transactions(rows):
    load(Transaction, rows)
    approved = Q(state="approved")
    groups = (Transaction.objects.annotate(month=Substr("trans_date", 1, 7)).values("month", "country")
              .annotate(trans_count=Count("id"), approved_count=Count("id", filter=approved),
                        trans_total=Sum("amount"), approved_total=Coalesce(Sum("amount", filter=approved), 0))
              .order_by("month", "country"))
    return [[g["month"], g["country"], g["trans_count"], g["approved_count"], g["trans_total"], g["approved_total"]] for g in groups]
''', [('monthly_transactions([{"id": 121, "country": "US", "state": "approved", "amount": 1000, "trans_date": "2018-12-18"}, {"id": 122, "country": "US", "state": "declined", "amount": 2000, "trans_date": "2018-12-19"}, {"id": 123, "country": "US", "state": "approved", "amount": 2000, "trans_date": "2019-01-01"}, {"id": 124, "country": "DE", "state": "approved", "amount": 2000, "trans_date": "2019-01-07"}])', [['2018-12', 'US', 2, 1, 3000, 1000], ['2019-01', 'DE', 1, 1, 2000, 2000], ['2019-01', 'US', 1, 1, 2000, 2000]])])
lc(1174, 'Immediate Food Delivery II', 'immediate-food-delivery-ii', 'm', 'Subquery for the first order of each customer', 'Find each customer&#39;s first order date with a Subquery that sorts by date and takes one row, keep only those first orders, then count how many were delivered on the day they were ordered.', ORM + r'''
from django.db.models import F, OuterRef, Subquery


class Delivery(models.Model):
    delivery_id = models.IntegerField(primary_key=True)
    customer_id = models.IntegerField()
    order_date = models.DateField()
    customer_pref_delivery_date = models.DateField()


def immediate_percentage(rows):
    load(Delivery, rows)
    first_date = Delivery.objects.filter(customer_id=OuterRef("customer_id")).order_by("order_date").values("order_date")[:1]
    first_orders = Delivery.objects.filter(order_date=Subquery(first_date))
    immediate = first_orders.filter(customer_pref_delivery_date=F("order_date")).count()
    return round(100 * immediate / first_orders.count(), 2)
''', [('immediate_percentage([{"delivery_id": 1, "customer_id": 1, "order_date": "2019-08-01", "customer_pref_delivery_date": "2019-08-02"}, {"delivery_id": 2, "customer_id": 2, "order_date": "2019-08-02", "customer_pref_delivery_date": "2019-08-02"}, {"delivery_id": 3, "customer_id": 1, "order_date": "2019-08-11", "customer_pref_delivery_date": "2019-08-12"}, {"delivery_id": 4, "customer_id": 3, "order_date": "2019-08-24", "customer_pref_delivery_date": "2019-08-24"}, {"delivery_id": 5, "customer_id": 3, "order_date": "2019-08-21", "customer_pref_delivery_date": "2019-08-22"}, {"delivery_id": 6, "customer_id": 2, "order_date": "2019-08-11", "customer_pref_delivery_date": "2019-08-13"}, {"delivery_id": 7, "customer_id": 4, "order_date": "2019-08-09", "customer_pref_delivery_date": "2019-08-09"}])', 50.0)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>SQL problems from the LeetCode database set, each solved with the Django ORM in place of SQL: computed columns, a LEFT JOIN with Subquery, following a ForeignKey, conditional aggregation with Case and When, Count with a filter, a weighted average, NOT IN with exclude, grouping by a computed month and the first row per group. Each solution makes its tables in an in-memory SQLite database, so leetcode.py runs on its own.</p>'), kw=['LeetCode', 'SQL', 'Django ORM', 'Subquery', 'annotate', 'aggregate', 'Case', 'When'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A QuerySet is lazy: filter, exclude and order_by build one SQL query that runs when you read it. Q gives OR and NOT, F uses column values inside the database.',
    'aggregate gives one answer, annotate gives one per row with GROUP BY. select_related (a JOIN) and prefetch_related (one more query) fix the N + 1 problem.',
    'makemigrations writes the changes into a file for git, migrate runs them, and RunPython moves data. Old rows need a default.',
    'Forms turn text into checked Python values: field checks, clean_&lt;field&gt;, clean, then cleaned_data or save(). Always redirect after a save.',
    'Users store only password hashes, login_required and permissions protect views, atomic() keeps changes all or nothing, and TestCase rolls back after every test.'],
    'Next: APIs with Django REST framework and FastAPI.')}
{files('Three tasks: write a sign up form with Django forms, plan migrations like migrate does, and build atomic() with savepoints.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'When does a QuerySet run its SQL?', ['When filter() is called', 'When you read the results, for example in a for loop or with list()', 'When the program starts', 'Never'], 1, 'Lazy evaluation.', 'Chaining filter, exclude and order_by is free.')
K.quiz('e', 'Which command writes a migration file after you change a model?', ['python manage.py migrate', 'python manage.py makemigrations', 'python manage.py sqlmigrate', 'python manage.py shell'], 1, 'Make, then apply.', 'migrate runs the file afterwards.')
K.quiz('e', 'How does Django store a user&#39;s password?', ['As plain text', 'As a salted, slow hash (PBKDF2 by default)', 'Encrypted with SECRET_KEY', 'In the session'], 1, 'Never the password itself.', 'check_password hashes the input the same way and compares.')
K.quiz('m', 'Which query finds books by UK authors OR with stock above 3?', ['filter(author__country="UK", stock__gt=3)', 'filter(Q(author__country="UK") | Q(stock__gt=3))', 'filter(author__country="UK").filter(stock__gt=3)', 'exclude(author__country="UK")'], 1, 'Commas mean AND.', 'Q objects with | give OR.')
K.quiz('m', 'What is the difference between aggregate and annotate?', ['None', 'aggregate gives one result for the whole QuerySet, annotate adds a value to every row', 'annotate is slower', 'aggregate changes data'], 1, 'One answer or one per row.', 'annotate(n=Count("books")) gives each author its own n.')
K.quiz('m', 'Why use update(stock=F("stock") - 1) instead of reading, changing and saving?', ['It is shorter only', 'The change runs inside the database in one step, so two requests at the same time do not overwrite each other', 'F is required by Django', 'It skips validation for speed'], 1, 'A race condition.', 'Read, change, save can lose an update when two users buy the last copy.')
K.quiz('m', 'A template loops over 50 orders and shows order.customer.name. How do you avoid 51 queries?', ['prefetch_related("customer") only', 'Order.objects.select_related("customer")', 'Add an index', 'Use values()'], 1, 'One related row per order.', 'select_related joins the tables in one query.')
K.quiz('m', 'Where do you check that two password fields match?', ['clean_password2 only', 'In the form&#39;s clean() method, which sees all fields', 'In the model', 'In the template'], 1, 'Rules across fields.', 'Use self.add_error("password2", ...) to attach the message to a field.')
K.quiz('m', 'You add a required field to a model whose table already has rows. What must you give?', ['Nothing', 'A default (or null=True), so the old rows get a value', 'A new table name', 'A superuser'], 1, 'Old rows need a value.', 'makemigrations asks for a one off default if you forget.')
K.quiz('h', 'Why does each Django TestCase test see a clean database?', ['Django deletes all tables', 'Each test runs inside a transaction that is rolled back at the end', 'Tests use different databases', 'Tests run in separate processes'], 1, 'Rollback after every test.', 'That is also why atomic() inside a test becomes a SAVEPOINT.')
K.quiz('h', 'Inside a data migration, why use apps.get_model("books", "Book") instead of importing Book?', ['It is faster', 'It gives the model as it was at that migration, so the migration still works after the model changes later', 'Imports are not allowed', 'For permissions'], 1, 'Historical models.', 'The current model may have fields the old table does not have yet.')
K.quiz('x', 'In the style of a Berkeley CS 186 database exam: a page reads 20 books and, for each, all of its tags. Which plan does prefetch_related("tags") use, and how many queries?', ['20 JOINs, 20 queries', 'One query for the books and one query for all their tags with WHERE book_id IN (...), 2 queries', 'One query with a JOIN per tag', '21 queries'], 1, 'Two queries whatever the number of books.', 'The tags are matched to the books in Python.')
K.quiz('x', 'In the style of an MIT 6.033 systems exam: two clients run transfer() at the same time on the same account with read, change, save. What can go wrong, and the Django fix?', ['Nothing, Django locks every row', 'A lost update: both read the old balance and one write is lost. Use F() expressions, or select_for_update() inside atomic()', 'A deadlock always happens', 'The migration fails'], 1, 'Read, change, save is not atomic.', 'F() makes the database do the change, select_for_update() locks the row until the transaction ends.')

K.calc('e', 'A page shows 20 books and reads book.author for each, with no select_related. How many queries?', '21', 'N + 1.', ['1 query for the books.', '1 for each of the 20 authors.', eq('21 queries')], check=20 + 1)
K.calc('e', 'The same page with prefetch_related for the tags of the 20 books. How many queries?', '2', 'Always 2.', ['1 query for the books.', '1 query for all their tags.', eq('2 queries')], check=2)
K.calc('e', '20 books with 2 tags each. How many rows are in the many to many join table?', '40', 'books &times; tags.', ['Each book and tag pair is one row.', '20 &times; 2.', eq('40 rows')], check=20 * 2)
K.calc('m', 'Each query takes 1.5 ms. How many ms does the N + 1 page with 20 books spend on queries?', '31.5', 'queries &times; time.', ['21 queries.', '21 &times; 1.5 ms.', eq('31.5 ms')], check=21 * 1.5, tol=0.01)
K.calc('m', 'A B-tree index has about 100 keys per page. How many page reads to find one key among 1,000,000?', '3', 'log<sub>100</sub>(n).', ['1,000,000 = 100<sup>3</sup>.', 'So the tree has 3 levels.', eq('3 page reads')], check=3)
K.calc('m', 'Weighted average price: 100 units at 5 and 15 units at 20. Round to 2 places.', '6.96', '&Sigma;(price &times; units) / &Sigma;units.', ['5 &times; 100 + 20 &times; 15 = 800.', '100 + 15 = 115 units.', '800 / 115.', eq('&asymp; 6.96')], check=round(800 / 115, 2), tol=0.005)
K.calc('m', 'Django 6.1 hashes passwords with PBKDF2 and 1,500,000 iterations. At 3,000,000,000 SHA-256 a second, how many guesses per second?', '2000', 'Divide by the iterations.', ['Each guess costs 1,500,000 hashes.', '3,000,000,000 / 1,500,000.', eq('2,000 guesses per second')], check=3_000_000_000 // 1_500_000)
K.calc('m', 'Migrations 0001 to 0007 are applied. How many does migrate books 0004 undo?', '3', 'Everything after the target.', ['0005, 0006 and 0007 come after 0004.', 'They are undone newest first.', eq('3 migrations')], check=7 - 4)
K.calc('h', 'Two of 4 customers got their first order delivered on the same day. What percentage is immediate (LeetCode 1174)?', '50', 'immediate / customers &times; 100.', ['Only the first order of each customer counts.', '2 / 4 = 0.5.', eq('50 %')], check=2 / 4 * 100)
K.calc('x', 'In the style of a CMU 15-445 exam: a table with 1,000,000 rows, 10 rows per page. A full scan reads every page, and an index lookup reads 3 index pages plus 1 data page. How many times fewer page reads?', '25000', 'Pages for the scan, then divide.', ['Scan: 1,000,000 / 10 = 100,000 pages.', 'Index: 3 + 1 = 4 pages.', '100,000 / 4.', eq('25,000 times fewer')], check=100_000 // 4)

K.assign('signup', 'e', 'Write a sign up form with Django forms',
         '<p>Finish <code>SignupForm</code>. The fields and their basic checks are ready. Add <code>clean_username</code>: change the name to lower case, raise ValidationError("Use only letters and digits.") when it has anything else, and "This name is taken." when it is in TAKEN. Add <code>clean</code>: when both passwords are there but differ, add the error "The passwords do not match." to password2. try_signup(data) returns ["ok", username] or ["errors", &#123;field: [messages]&#125;].</p>',
         r'''
import django
from django.conf import settings

settings.configure(SECRET_KEY="dev-only")
django.setup()

from django import forms

TAKEN = {"ann", "admin"}


class SignupForm(forms.Form):
    username = forms.CharField(max_length=20)
    email = forms.EmailField()
    password = forms.CharField(min_length=10)
    password2 = forms.CharField()

    def clean_username(self):
        return self.cleaned_data["username"]


def try_signup(data):
    form = SignupForm(data)
    if form.is_valid():
        return ["ok", form.cleaned_data["username"]]
    return ["errors", {field: [e["message"] for e in errors] for field, errors in form.errors.get_json_data().items()}]
''', [('try_signup({"username": "Zed42", "email": "zed@example.com", "password": "long enough 1", "password2": "long enough 1"})', ['ok', 'zed42']), ('try_signup({"username": "ANN", "email": "a@example.com", "password": "long enough 1", "password2": "long enough 1"})', ['errors', {'username': ['This name is taken.']}]), ('try_signup({"username": "zed 42", "email": "zed@example.com", "password": "long enough 1", "password2": "long enough 1"})', ['errors', {'username': ['Use only letters and digits.']}]), ('try_signup({"username": "zed", "email": "zed@example.com", "password": "long enough 1", "password2": "long enough 2"})', ['errors', {'password2': ['The passwords do not match.']}]), ('try_signup({"username": "zed", "email": "nope", "password": "short", "password2": "short"})', ['errors', {'email': ['Enter a valid email address.'], 'password': ['Ensure this value has at least 10 characters (it has 5).']}]), ('try_signup({"username": "", "email": "zed@example.com", "password": "long enough 1", "password2": "long enough 1"})', ['errors', {'username': ['This field is required.']}])],
         r'''
import django
from django.conf import settings

settings.configure(SECRET_KEY="dev-only")
django.setup()

from django import forms

TAKEN = {"ann", "admin"}


class SignupForm(forms.Form):
    username = forms.CharField(max_length=20)
    email = forms.EmailField()
    password = forms.CharField(min_length=10)
    password2 = forms.CharField()

    def clean_username(self):
        name = self.cleaned_data["username"].lower()
        if not name.isalnum():
            raise forms.ValidationError("Use only letters and digits.")
        if name in TAKEN:
            raise forms.ValidationError("This name is taken.")
        return name

    def clean(self):
        data = super().clean()
        if data.get("password") and data.get("password2") and data["password"] != data["password2"]:
            self.add_error("password2", "The passwords do not match.")
        return data


def try_signup(data):
    form = SignupForm(data)
    if form.is_valid():
        return ["ok", form.cleaned_data["username"]]
    return ["errors", {field: [e["message"] for e in errors] for field, errors in form.errors.get_json_data().items()}]
''', 'self.cleaned_data["username"] holds the value after the field&#39;s own checks. Return the cleaned value from clean_username. In clean, call super().clean() first and use self.add_error("password2", ...).', '<p>clean_&lt;field&gt; runs only when the field&#39;s own checks passed, so an empty username shows "This field is required." and never reaches your method. In a real site you would use UserCreationForm, which also checks the password against the validators in AUTH_PASSWORD_VALIDATORS.</p>')
K.assign('plan', 'm', 'Plan migrations like migrate does',
         '<p>Each migration lists the migrations it depends on, as in GRAPH. Write <code>apply_plan(dependencies, applied)</code>: the migrations not applied yet, each one after everything it depends on, and when several are free, take them in name order (visit the names sorted, and the parents of each sorted). Raise ValueError for a circular dependency. Write <code>rollback_plan(dependencies, applied, target)</code>: the applied migrations that depend on target, directly or through others, newest first, which is what <code>migrate books 0001</code> undoes.</p>',
         r'''
def apply_plan(dependencies, applied):
    """The migrations still to run, each after the ones it depends on. Ties go in name order."""
    return sorted(name for name in dependencies if name not in applied)


def rollback_plan(dependencies, applied, target):
    """The applied migrations to undo so that target is the last one left: every migration that needs target, newest first."""
    return []
GRAPH = {
    "books.0001": [],
    "books.0002": ["books.0001"],
    "books.0003": ["books.0002", "users.0001"],
    "users.0001": [],
    "users.0002": ["users.0001"],
}


def plan_error(graph):
    try:
        apply_plan(graph, [])
    except ValueError:
        return "ValueError"
    return "no error"
''', [('apply_plan(GRAPH, [])', ['books.0001', 'books.0002', 'users.0001', 'books.0003', 'users.0002']), ('apply_plan(GRAPH, ["books.0001", "users.0001"])', ['books.0002', 'books.0003', 'users.0002']), ('apply_plan(GRAPH, list(GRAPH))', []), ('rollback_plan(GRAPH, ["books.0001", "books.0002", "users.0001", "books.0003", "users.0002"], "books.0001")', ['books.0003', 'books.0002']), ('rollback_plan(GRAPH, ["books.0001", "books.0002", "users.0001", "books.0003", "users.0002"], "users.0001")', ['users.0002', 'books.0003']), ('rollback_plan(GRAPH, ["books.0001"], "books.0001")', []), ('plan_error({"a.0001": ["a.0002"], "a.0002": ["a.0001"]})', 'ValueError')],
         r'''
def apply_plan(dependencies, applied):
    """The migrations still to run, each after the ones it depends on. Ties go in name order."""
    done = set(applied)
    plan = []
    visiting = set()

    def visit(name):
        if name in done:
            return
        if name in visiting:
            raise ValueError(f"circular dependency at {name}")
        visiting.add(name)
        for parent in sorted(dependencies[name]):
            visit(parent)
        visiting.discard(name)
        done.add(name)
        plan.append(name)

    for name in sorted(dependencies):
        visit(name)
    return plan


def rollback_plan(dependencies, applied, target):
    """The applied migrations to undo so that target is the last one left: every migration that needs target, newest first."""
    needs = set()
    changed = True
    while changed:
        changed = False
        for name in applied:
            if name not in needs and (target in dependencies[name] or needs & set(dependencies[name])):
                needs.add(name)
                changed = True
    return [name for name in reversed(applied) if name in needs]


GRAPH = {
    "books.0001": [],
    "books.0002": ["books.0001"],
    "books.0003": ["books.0002", "users.0001"],
    "users.0001": [],
    "users.0002": ["users.0001"],
}


def plan_error(graph):
    try:
        apply_plan(graph, [])
    except ValueError:
        return "ValueError"
    return "no error"
''', 'A depth first search: before adding a name, visit its parents. Keep a set of names on the current path to find a cycle. For the rollback, keep adding names that depend on target or on a name already found until nothing changes.', '<p>Django builds the same graph from the dependencies list in every migration file, then walks it in this order. That is why two developers who both add a 0002 migration get "Conflicting migrations detected" and must run makemigrations --merge.</p>')
K.assign('tx', 'h', 'Build atomic() with savepoints',
         '<p>MiniDB keeps balances in a dict. Make <code>atomic()</code> work as a context manager like Django&#39;s transaction.atomic: when the block ends with an error, every change made inside it is undone and the error goes on, and when it ends normally the changes stay. Blocks can be nested: an error in an inner block undoes only the inner block, like a savepoint. move() is ready, and it changes the receiver before it checks the sender, so a missing atomic leaves money from nowhere. bank_story(steps) runs a story and catches the errors of each block.</p>',
         r'''
import copy


class MiniDB:
    def __init__(self, data):
        self.data = dict(data)
        self.saved = []                      # a stack of copies, one for each open atomic block

    def __enter__(self):
        return self

    def __exit__(self, kind, error, trace):
        return False

    def atomic(self):
        return self

    def move(self, sender, receiver, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.data[receiver] += amount
        if self.data[sender] < amount:
            raise ValueError(f"{sender} has only {self.data[sender]}")
        self.data[sender] -= amount


def bank_story(steps):
    """steps: a list of ("move", sender, receiver, amount) or ("block", [inner steps]). Returns the balances and the errors."""
    db = MiniDB({"ann": 100, "bob": 20, "cat": 0})
    errors = []

    def run(step_list):
        for step in step_list:
            if step[0] == "move":
                db.move(*step[1:])
            else:
                try:
                    with db.atomic():
                        run(step[1])
                except ValueError as e:
                    errors.append(str(e))

    run(steps)
    return [db.data, errors]
''', [('bank_story([("move", "ann", "bob", 30)])', [{'ann': 70, 'bob': 50, 'cat': 0}, []]), ('bank_story([("block", [("move", "bob", "cat", 50)])])', [{'ann': 100, 'bob': 20, 'cat': 0}, ['bob has only 20']]), ('bank_story([("block", [("move", "ann", "cat", 10), ("move", "bob", "cat", 99)])])', [{'ann': 100, 'bob': 20, 'cat': 0}, ['bob has only 20']]), ('bank_story([("block", [("move", "ann", "cat", 10), ("block", [("move", "bob", "cat", 99)]), ("move", "ann", "bob", 5)])])', [{'ann': 85, 'bob': 25, 'cat': 10}, ['bob has only 20']]), ('bank_story([("block", [("move", "ann", "bob", 0)]), ("move", "bob", "ann", 20)])', [{'ann': 120, 'bob': 0, 'cat': 0}, ['amount must be positive']])],
         r'''
import copy


class MiniDB:
    def __init__(self, data):
        self.data = dict(data)
        self.saved = []                      # a stack of copies, one for each open atomic block

    def __enter__(self):
        self.saved.append(copy.deepcopy(self.data))
        return self

    def __exit__(self, kind, error, trace):
        snapshot = self.saved.pop()
        if kind is not None:
            self.data = snapshot             # an error inside the block: undo everything it changed
        return False                         # never hide the error

    def atomic(self):
        return self

    def move(self, sender, receiver, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.data[receiver] += amount
        if self.data[sender] < amount:
            raise ValueError(f"{sender} has only {self.data[sender]}")
        self.data[sender] -= amount


def bank_story(steps):
    """steps: a list of ("move", sender, receiver, amount) or ("block", [inner steps]). Returns the balances and the errors."""
    db = MiniDB({"ann": 100, "bob": 20, "cat": 0})
    errors = []

    def run(step_list):
        for step in step_list:
            if step[0] == "move":
                db.move(*step[1:])
            else:
                try:
                    with db.atomic():
                        run(step[1])
                except ValueError as e:
                    errors.append(str(e))

    run(steps)
    return [db.data, errors]
''', 'Keep a stack of copies. __enter__ pushes copy.deepcopy(self.data), __exit__ pops it and, when kind is not None, puts it back. Return False so the error is not hidden.', '<p>Databases do this without copying everything: they keep a log of changes and undo them on ROLLBACK. Django turns the outer atomic into BEGIN and COMMIT and each inner one into SAVEPOINT and RELEASE, exactly the nesting you built here.</p>')

K.must('QuerySets', 'Lazy until read. filter, exclude, order_by, get, first, exists, count. Lookups: __gte, __icontains, __in, author__name. Q(a) | Q(b), ~Q(c). F("col") inside filter and update.')
K.must('Aggregation and speed', 'aggregate(Avg("price")) gives a dict, annotate(n=Count("books")) adds n per row. select_related for ForeignKey, prefetch_related for ManyToMany. only, values_list, bulk_create, indexes.')
K.must('Migrations', 'makemigrations then migrate. Commit the files. New fields need a default or null=True. Data migrations use RunPython with apps.get_model. migrate app 0001 goes back. sqlmigrate shows the SQL.')
K.must('Forms', 'form = BookForm(request.POST), form.is_valid(), cleaned_data, form.save(). clean_&lt;field&gt; for one field, clean() with add_error for several. ModelForm with Meta.model and Meta.fields.')
K.must('Users, transactions, tests', 'create_user, check_password, authenticate, login_required, permission_required, Group. transaction.atomic() all or nothing. TestCase rolls back each test, setUpTestData, self.client, assertNumQueries.')

T = K.topic(
    slug='py-django-orm', topic='py-django-orm', step=(4, 'Django: the framework with everything built in', 'py-w4', 'Build full websites with Django: a project and its apps, URLs, views, templates, models and the admin, then the ORM in depth, forms, users and tests.', 'Intermediate'),
    title='Django in depth: ORM, migrations, forms, users and tests', short='Django ORM', badge='4.2', minutes=120,
    lead='Use the Django ORM well. Write rich queries with Q, F, aggregate and annotate, make them fast, change tables with migrations, check input with forms, protect pages with users and permissions, and test it all.',
    desc='The ORM and lazy QuerySets, lookups across relations, ForeignKey and ManyToManyField, Q objects, F expressions, aggregate and annotate with GROUP BY and HAVING, the N + 1 problem with select_related and prefetch_related, other query speed ups and indexes, migrations with makemigrations, migrate, sqlmigrate, data migrations and rollback, forms and ModelForms with field, clean_field and clean validation, the User model, password hashing, authenticate, login_required, permissions and groups, transaction.atomic, F for safe updates, TestCase, setUpTestData and assertNumQueries, and the maths of query counts, B-tree indexes and weighted averages.',
    summary='Q, F, aggregate, annotate, the N + 1 problem, migrations, forms, users and permissions, transactions and TestCase.',
    keywords=['Django ORM', 'QuerySet', 'Q', 'F', 'annotate', 'select_related', 'migrations', 'ModelForm', 'permissions', 'TestCase'],
    recap='<p>A lazy QuerySet becomes one SQL query, select_related and prefetch_related keep the count low, migrations change tables safely, forms check input, and atomic() and TestCase keep data correct.</p>',
    added='2026-11-08', leet=leet_items())
