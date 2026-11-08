# 5.2 FastAPI: fast, typed APIs with automatic docs
# Example "pytest_api" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os
import subprocess
import sys
import tempfile

# Two real files, main.py (the app) and test_main.py (the tests), then a real pytest run
APP = """
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


def get_store():
    return {}                                   # in a real app: a database session


@app.post("/items", status_code=201)
def add_item(item: Item, store: dict = Depends(get_store)):
    if item.name in store:
        raise HTTPException(409, "Item exists")
    store[item.name] = item.price
    return {"name": item.name, "price": item.price, "count": len(store)}
"""

TESTS = """
import pytest
import warnings
warnings.filterwarnings("ignore", message="Using `httpx` with")
from fastapi.testclient import TestClient

from main import app, get_store


@pytest.fixture
def client():
    store = {}
    app.dependency_overrides[get_store] = lambda: store     # every test gets its own empty store
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_add_item(client):
    r = client.post("/items", json={"name": "tea", "price": 3})
    assert r.status_code == 201
    assert r.json() == {"name": "tea", "price": 3.0, "count": 1}


def test_same_item_twice_is_409(client):
    client.post("/items", json={"name": "tea", "price": 3})
    r = client.post("/items", json={"name": "tea", "price": 4})
    assert r.status_code == 409
    assert r.json()["detail"] == "Item exists"


@pytest.mark.parametrize("body", [{}, {"name": "tea"}, {"name": "tea", "price": "free"}])
def test_bad_bodies_are_422(client, body):
    assert client.post("/items", json=body).status_code == 422
"""

folder = tempfile.mkdtemp()
for name, text in [("main.py", APP), ("test_main.py", TESTS)]:
    with open(os.path.join(folder, name), "w") as f:
        f.write(text)
result = subprocess.run([sys.executable, "-m", "pytest", "-v", "-p", "no:cacheprovider"], cwd=folder,
                        capture_output=True, text=True)
for line in result.stdout.splitlines():
    if "::" in line or "passed" in line or "failed" in line:
        print(line.split(" [")[0].replace(folder + os.sep, "").rstrip())      # the test lines and the summary
