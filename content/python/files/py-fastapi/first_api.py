# 5.2 FastAPI: fast, typed APIs with automatic docs
# Example "first_api" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import warnings

warnings.filterwarnings("ignore", message="Using `httpx` with")   # a notice from Starlette 1.10 about its test client

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI(title="Book shop API", version="1.0")


class BookIn(BaseModel):                                   # what a client sends
    title: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=0, le=2026)
    price: float = Field(gt=0)


class BookOut(BookIn):                                     # what the API sends back
    id: int


BOOKS: dict[int, BookOut] = {1: BookOut(id=1, title="Dune", year=1965, price=9.99)}


@app.get("/books", response_model=list[BookOut])
def list_books(min_year: int = 0, limit: int = Query(10, ge=1, le=100)):     # query parameters with types
    found = [book for book in BOOKS.values() if book.year >= min_year]
    return found[:limit]


@app.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: int):                                # a path parameter, checked as int
    if book_id not in BOOKS:
        raise HTTPException(status_code=404, detail="Book not found")
    return BOOKS[book_id]


@app.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def add_book(book: BookIn):                                # the JSON body, checked by Pydantic
    new = BookOut(id=max(BOOKS) + 1, **book.model_dump())
    BOOKS[new.id] = new
    return new


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    if BOOKS.pop(book_id, None) is None:
        raise HTTPException(status_code=404, detail="Book not found")


client = TestClient(app)
for method, url, body in [
    ("get", "/books", None),
    ("post", "/books", {"title": "Emma", "year": 1815, "price": 5}),
    ("get", "/books?min_year=1900&limit=5", None),
    ("get", "/books/2", None),
    ("get", "/books/abc", None),
    ("post", "/books", {"title": "", "year": 3000}),
    ("get", "/books?limit=500", None),
    ("delete", "/books/2", None),
    ("delete", "/books/2", None),
]:
    response = client.request(method.upper(), url, json=body)
    data = response.json() if response.content else None
    if response.status_code == 422:                        # show only where and why for validation errors
        data = [(".".join(map(str, e["loc"])), e["msg"]) for e in data["detail"]]
    print(f"{method.upper():6} {url:28} {response.status_code} {data}")

schema = client.get("/openapi.json").json()               # the docs FastAPI wrote by itself
print("OpenAPI paths:", {path: sorted(ops) for path, ops in schema["paths"].items()})
print("Swagger UI at /docs:", client.get("/docs").status_code, "| ReDoc at /redoc:", client.get("/redoc").status_code)
