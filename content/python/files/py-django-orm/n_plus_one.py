# 4.2 Django in depth: ORM, migrations, forms, users and tests
# Example "n_plus_one" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
              lambda: list(Book.objects.values_list("title", "author__name")))
