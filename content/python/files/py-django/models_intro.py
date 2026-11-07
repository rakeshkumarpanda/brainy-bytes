# 4.1 Django basics: project, URLs, views, templates, models and admin
# Example "models_intro" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
print(str(query.query))
