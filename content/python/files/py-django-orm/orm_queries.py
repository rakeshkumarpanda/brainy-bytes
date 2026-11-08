# 4.2 Django in depth: ORM, migrations, forms, users and tests
# Example "orm_queries" from the lesson.
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
print(Author.objects.annotate(n=Count("books")).filter(n__gte=2).query)
