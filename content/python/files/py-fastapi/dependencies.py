# 5.2 FastAPI: fast, typed APIs with automatic docs
# Example "dependencies" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import warnings

warnings.filterwarnings("ignore", message="Using `httpx` with")   # a notice from Starlette 1.10 about its test client

import sqlite3
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()
TOKENS = {"secret-ann": "ann", "secret-bob": "bob"}


# ---------- Dependencies: small functions FastAPI calls for you before the endpoint ----------
def get_db():
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.execute("CREATE TABLE note (id INTEGER PRIMARY KEY, owner TEXT, text TEXT)")
    db.executemany("INSERT INTO note (owner, text) VALUES (?, ?)",
                   [("ann", "buy milk"), ("ann", "call mum"), ("bob", "fix bike"), ("ann", "read Dune")])
    print("   [get_db] connection opened")
    try:
        yield db                                           # the endpoint runs here
    finally:
        db.close()                                         # runs after the answer, even after an error
        print("   [get_db] connection closed")


def current_user(authorization: Annotated[str | None, Header()] = None):
    token = (authorization or "").removeprefix("Bearer ")
    if token not in TOKENS:
        raise HTTPException(status_code=401, detail="Not logged in", headers={"WWW-Authenticate": "Bearer"})
    return TOKENS[token]


def paging(skip: int = 0, limit: int = 2):                # shared query parameters
    return {"skip": skip, "limit": min(limit, 50)}


DB = Annotated[sqlite3.Connection, Depends(get_db)]
User = Annotated[str, Depends(current_user)]
Page = Annotated[dict, Depends(paging)]


@app.get("/notes")
def my_notes(db: DB, user: User, page: Page):
    rows = db.execute("SELECT id, text FROM note WHERE owner = ? ORDER BY id LIMIT ? OFFSET ?",
                      (user, page["limit"], page["skip"])).fetchall()
    return {"user": user, "notes": [{"id": i, "text": t} for i, t in rows]}


client = TestClient(app)
response = client.get("/notes")
print("no token:", response.status_code, response.json())          # get_db still ran: it comes first in my_notes
headers = {"Authorization": "Bearer secret-ann"}
print("ann page 1:", client.get("/notes", headers=headers).json())
print("ann page 2:", client.get("/notes?skip=2", headers=headers).json())

# ---------- In tests, swap a dependency for a fake one ----------
app.dependency_overrides[current_user] = lambda: "bob"
print("override, no token needed:", client.get("/notes").json())
app.dependency_overrides.clear()
