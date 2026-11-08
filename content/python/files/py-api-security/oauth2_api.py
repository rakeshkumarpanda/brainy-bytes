# 6.1 API security: passwords, JWT, OAuth 2.0, CORS and OWASP
# Example "oauth2_api" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

# A FastAPI login with OAuth2 password flow, JWT access tokens, scopes and an owner check.
# pip install fastapi httpx pyjwt python-multipart
import warnings

warnings.filterwarnings("ignore", message="Using `httpx` with")   # a notice from Starlette 1.10 about its test client
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from fastapi.testclient import TestClient

SECRET = secrets.token_urlsafe(32)


def pw_hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()


USERS = {
    "ann": {"salt": "s1", "hash": pw_hash("tea-for-two", "s1"), "scopes": ["notes:read", "notes:write"]},
    "ben": {"salt": "s2", "hash": pw_hash("coffee-time", "s2"), "scopes": ["notes:read"]},
}
NOTES = {1: {"owner": "ann", "text": "Buy milk"}, 2: {"owner": "ben", "text": "Call mum"}}

app = FastAPI()
oauth2 = OAuth2PasswordBearer(tokenUrl="token", scopes={"notes:read": "Read notes", "notes:write": "Write notes"})


@app.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = USERS.get(form.username)
    # hash even when the user does not exist, so the time does not reveal which names exist
    given = pw_hash(form.password, user["salt"] if user else "x")
    if not user or not hmac.compare_digest(given, user["hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    granted = [s for s in form.scopes if s in user["scopes"]]      # never more than the user has
    exp = datetime.now(timezone.utc) + timedelta(minutes=15)
    token = jwt.encode({"sub": form.username, "scope": " ".join(granted), "exp": exp}, SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


def current_user(scopes: SecurityScopes, token: Annotated[str, Depends(oauth2)]):
    try:
        claims = jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    have = claims["scope"].split()
    for needed in scopes.scopes:
        if needed not in have:
            raise HTTPException(403, f"Missing scope {needed}")
    return claims["sub"]


@app.get("/notes/{note_id}")
def read_note(note_id: int, user: Annotated[str, Security(current_user, scopes=["notes:read"])]):
    note = NOTES.get(note_id)
    if note is None or note["owner"] != user:          # the object level check (OWASP API1)
        raise HTTPException(404, "Note not found")      # 404, not 403: do not confirm that it exists
    return note


@app.post("/notes", status_code=201)
def add_note(text: str, user: Annotated[str, Security(current_user, scopes=["notes:write"])]):
    note_id = max(NOTES) + 1
    NOTES[note_id] = {"owner": user, "text": text}
    return {"id": note_id}


client = TestClient(app)


def login_as(name, password, scope):
    r = client.post("/token", data={"username": name, "password": password, "scope": scope})
    return r


def show(label, r):
    print(f"{label:42} {r.status_code} {r.json()}")


r = login_as("ann", "wrong", "notes:read")
show("ann, wrong password", r)
print(" " * 43 + "WWW-Authenticate:", r.headers["www-authenticate"])
ann = login_as("ann", "tea-for-two", "notes:read notes:write").json()["access_token"]
ben = login_as("ben", "coffee-time", "notes:read notes:write").json()["access_token"]
print("ann logged in, token starts", ann[:20] + "...")
A = {"Authorization": f"Bearer {ann}"}
B = {"Authorization": f"Bearer {ben}"}

show("no token", client.get("/notes/1"))
show("garbage token", client.get("/notes/1", headers={"Authorization": "Bearer abc.def.ghi"}))
show("ann reads her note 1", client.get("/notes/1", headers=A))
show("ben reads ann's note 1", client.get("/notes/1", headers=B))
show("ann writes a note", client.post("/notes", params={"text": "Pay rent"}, headers=A))
show("ben writes (asked for write, not granted)", client.post("/notes", params={"text": "Hi"}, headers=B))
scheme = client.get("/openapi.json").json()["components"]["securitySchemes"]["OAuth2PasswordBearer"]
print("docs know the login:", scheme["type"], scheme["flows"]["password"]["tokenUrl"],
      list(scheme["flows"]["password"]["scopes"]))
