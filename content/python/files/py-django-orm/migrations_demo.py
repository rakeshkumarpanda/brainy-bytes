# 4.2 Django in depth: ORM, migrations, forms, users and tests
# Example "migrations_demo" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
manage("showmigrations", "books")
