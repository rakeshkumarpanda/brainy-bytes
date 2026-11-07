# 2.2 Real API work: pages, retries, limits and validation
# Example "validate" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from pydantic import BaseModel, Field, TypeAdapter, ValidationError


class Author(BaseModel):
    name: str
    born: int | None = None


class Book(BaseModel):
    id: int
    title: str = Field(min_length=1)
    year: int = Field(ge=0, le=2100)
    tags: list[str] = []
    author: Author


good = {"id": "7", "title": "Dune", "year": 1965, "extra": "ignored",
        "author": {"name": "Frank Herbert", "born": 1920}}
book = Book.model_validate(good)
print(book.id, type(book.id).__name__, book.title, book.author.name, book.tags)
print(book.model_dump())

bad = {"id": "seven", "title": "", "year": 3000, "author": {}}
try:
    Book.model_validate(bad)
except ValidationError as err:
    print(err.error_count(), "problems:")
    for problem in err.errors():
        where = ".".join(str(part) for part in problem["loc"])
        print(" ", where, "-", problem["msg"])

text = '[{"id": 1, "title": "Emma", "year": 1815, "author": {"name": "Jane Austen"}}]'
books = TypeAdapter(list[Book]).validate_json(text)        # straight from the JSON text of a response
print(len(books), books[0].title, books[0].author.born)
print(Book.model_json_schema()["required"])
