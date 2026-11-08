# 4.2 Django in depth: ORM, migrations, forms, users and tests
# Example "forms_demo" from the lesson.
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

print(BookForm()["title"])                                 # how one field renders as HTML
