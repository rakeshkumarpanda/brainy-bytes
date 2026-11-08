# Web and APIs 6.1: API security. Checked against RFC 7519 (JWT), RFC 7518 (JWA, HS256), RFC 6749 (OAuth 2.0),
# RFC 7636 (PKCE), RFC 6750 (Bearer tokens), the WHATWG Fetch standard (CORS), the OWASP API Security Top 10 2023,
# the OWASP Password Storage and Secrets Management cheat sheets, the FastAPI 0.162 security tutorial, PyJWT 2.15
# and Django 6.1 password hashers, with real runs of Python 3.14, PyJWT 2.15.1, FastAPI 0.162.0, Starlette 1.10.0
# and Pydantic 2.14.3. The FastAPI programs use the test client, which needs threads, so they are shown with local().
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, lc, leet, files, grow, leet_items

chapter('py-api-security')
K = Kit()

K.code('passwords', r'''
# Storing passwords: never the password, never a fast hash, always a slow salted hash.
import base64
import hashlib
import hmac
import secrets
import time

print("1. A plain fast hash is not enough")
for pw in ["sunshine", "sunshine", "Sunshine1"]:
    print(f"   sha256({pw!r:12}) = {hashlib.sha256(pw.encode()).hexdigest()[:24]}...")
print("   The same password always gives the same hash, so one stolen table of")
print("   precomputed hashes (a rainbow table) cracks every user who picked it.")


def hash_password(password, iterations=600_000, salt=None):
    """Return a Django style string: algorithm$iterations$salt$hash."""
    salt = salt or secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${base64.b64encode(digest).decode()}"


def check_password(password, stored):
    algorithm, iterations, salt, _ = stored.split("$")
    again = hash_password(password, int(iterations), salt)
    return hmac.compare_digest(again, stored)


print("\n2. A salted slow hash (PBKDF2, the default in Django)")
a = hash_password("sunshine", salt="Qx81LmZ0aa7Kc3d1")
b = hash_password("sunshine", salt="pW2nB7tRr4Ee9oYs")
print("   ann:", a[:60] + "...")
print("   ben:", b[:60] + "...")
print("   same password, different salt, different hash:", a != b)
print("   check 'sunshine' :", check_password("sunshine", a))
print("   check 'sunshine!':", check_password("sunshine!", a))

print("\n3. Slow on purpose")
for rounds in [1_000, 100_000, 600_000]:
    start = time.perf_counter()
    hash_password("sunshine", rounds, "fixedsalt")
    ms = (time.perf_counter() - start) * 1000
    print(f"   {rounds:>7,} rounds: {ms:7.1f} ms per guess")
print("   One login waits a fraction of a second. An attacker with a list of a")
print("   billion guesses must pay that cost a billion times for every user.")

print("\n4. scrypt also needs lots of memory, which slows down graphics cards")
digest = hashlib.scrypt(b"sunshine", salt=b"Qx81LmZ0aa7Kc3d1", n=2**14, r=8, p=1)
print("   scrypt:", digest.hex()[:32] + "...", f"({128 * 2**14 * 8 // 2**20} MB of memory per guess)")

print("\n5. Secrets for tokens come from the secrets module, never from random")
print("   API key      :", len(secrets.token_urlsafe(32)), "characters from 32 random bytes")
print("   reset code   :", len(f"{secrets.randbelow(10**6):06d}"), "digits")
print("   random.random() is predictable once an attacker sees a few outputs.")''', long=True)
K.code('jwt_by_hand', r'''
# A JSON Web Token (JWT) built with the standard library only, so you can see every part.
# Real projects use a library such as PyJWT (next program), but the steps are exactly these.
import base64
import hashlib
import hmac
import json

SECRET = b"change-me-to-32-random-bytes-in-real-life"
NOW = 1_800_000_000          # a fixed "now" (Unix seconds) so the output never changes


def b64url(data: bytes) -> str:
    """Base64 for URLs: + becomes -, / becomes _, and the = padding is removed."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64url_decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def sign(payload: dict, key: bytes) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    part1 = b64url(json.dumps(header, separators=(",", ":")).encode())
    part2 = b64url(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{part1}.{part2}".encode()
    signature = hmac.new(key, signing_input, hashlib.sha256).digest()
    return f"{part1}.{part2}.{b64url(signature)}"


def verify(token: str, key: bytes, now: int) -> dict:
    try:
        part1, part2, part3 = token.split(".")
    except ValueError:
        raise ValueError("malformed: a JWT has exactly 3 parts") from None
    header = json.loads(b64url_decode(part1))
    if header.get("alg") != "HS256":                  # never let the token choose the algorithm
        raise ValueError(f"refused algorithm {header.get('alg')!r}")
    expected = hmac.new(key, f"{part1}.{part2}".encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(expected, b64url_decode(part3)):   # constant time comparison
        raise ValueError("bad signature: the token was changed or signed with another key")
    payload = json.loads(b64url_decode(part2))
    if payload["exp"] <= now:
        raise ValueError("expired")
    return payload


print("1. Sign a token for ann")
token = sign({"sub": "ann", "role": "user", "iat": NOW, "exp": NOW + 900}, SECRET)
head, body, sig = token.split(".")
print("   header   :", head)
print("   payload  :", body)
print("   signature:", sig)
print("   length   :", len(token), "characters")

print("\n2. Anyone can READ a JWT. It is signed, not encrypted")
print("  ", json.loads(b64url_decode(head)))
print("  ", json.loads(b64url_decode(body)))

print("\n3. The server checks it")
print("   ok:", verify(token, SECRET, NOW + 60))

print("\n4. An attacker changes role to admin and keeps the old signature")
evil = json.loads(b64url_decode(body))
evil["role"] = "admin"
forged = f"{head}.{b64url(json.dumps(evil, separators=(',', ':')).encode())}.{sig}"
for label, tok, key, now in [
    ("forged payload", forged, SECRET, NOW + 60),
    ("signed with another key", sign({"sub": "ann", "exp": NOW + 900}, b"guessed-key"), SECRET, NOW + 60),
    ("16 minutes later", token, SECRET, NOW + 960),
]:
    try:
        verify(tok, key, now)
        print(f"   {label:24} accepted")
    except ValueError as err:
        print(f"   {label:24} rejected: {err}")

print('\n5. The "alg": "none" trick')
none_head = b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode())
none_token = f"{none_head}.{b64url(json.dumps(evil).encode())}."
try:
    verify(none_token, SECRET, NOW)
except ValueError as err:
    print("   rejected:", err)
print("   A careless server that trusts the header would skip the signature and accept it.")

print("\n6. Why compare_digest")
print("   == stops at the first different byte, so the time it takes leaks how many bytes were right.")
print("   hmac.compare_digest always looks at every byte:", hmac.compare_digest(b"abc", b"abd"))''', long=True)
K.code('pyjwt_tokens', r'''
# JWTs with PyJWT (pip install pyjwt): expiry, audience, issuer, refresh tokens and key rotation.
import secrets
from datetime import datetime, timedelta, timezone

import jwt

KEYS = {"k1": secrets.token_urlsafe(32)}     # in real life: read from an environment variable or a vault
CURRENT = "k1"
ISSUER = "https://auth.bookshop.example"


def make_token(user, kind, minutes, scopes=()):
    now = datetime.now(timezone.utc)
    claims = {
        "sub": user, "type": kind, "scope": " ".join(scopes),
        "iss": ISSUER, "aud": "bookshop-api",
        "iat": now, "exp": now + timedelta(minutes=minutes),
        "jti": secrets.token_hex(8),          # a unique id, so one token can be revoked
    }
    return jwt.encode(claims, KEYS[CURRENT], algorithm="HS256", headers={"kid": CURRENT})


def read_token(token, kind="access"):
    kid = jwt.get_unverified_header(token).get("kid")   # only to pick the key, never trusted on its own
    if kid not in KEYS:
        raise jwt.InvalidTokenError(f"unknown key id {kid!r}")
    claims = jwt.decode(token, KEYS[kid], algorithms=["HS256"],      # pin the algorithm
                        audience="bookshop-api", issuer=ISSUER,
                        options={"require": ["exp", "sub", "aud", "iss"]})
    if claims["type"] != kind:
        raise jwt.InvalidTokenError(f"a {claims['type']} token cannot be used here")
    return claims


print("1. Login gives a short access token and a long refresh token")
access = make_token("ann", "access", 15, ["books:read", "orders:write"])
refresh = make_token("ann", "refresh", 60 * 24 * 7)
claims = read_token(access)
print("   access token for", claims["sub"], "with scope", repr(claims["scope"]))
print("   lives", (claims["exp"] - claims["iat"]) // 60, "minutes")

print("\n2. Each check that PyJWT does for you")
tests = {
    "expired": jwt.encode({"sub": "ann", "type": "access", "iss": ISSUER, "aud": "bookshop-api",
                           "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
                          KEYS["k1"], algorithm="HS256", headers={"kid": "k1"}),
    "other audience": jwt.encode({"sub": "ann", "type": "access", "iss": ISSUER, "aud": "admin-api",
                                  "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
                                 KEYS["k1"], algorithm="HS256", headers={"kid": "k1"}),
    "refresh used as access": refresh,
    "wrong key": jwt.encode({"sub": "ann"}, secrets.token_urlsafe(32), algorithm="HS256", headers={"kid": "k1"}),
    "not a JWT": "hello.world",
}
for label, token in tests.items():
    try:
        read_token(token)
        print(f"   {label:24} accepted")
    except jwt.InvalidTokenError as err:
        print(f"   {label:24} {type(err).__name__}: {err}")

print("\n3. Refresh: trade the refresh token for a new access token")
used_refresh = set()


def refresh_access(token):
    claims = read_token(token, kind="refresh")
    if claims["jti"] in used_refresh:
        raise jwt.InvalidTokenError("refresh token used twice: someone stole it, log the user out everywhere")
    used_refresh.add(claims["jti"])                     # rotation: each refresh token works once
    return make_token(claims["sub"], "access", 15), make_token(claims["sub"], "refresh", 60 * 24 * 7)


new_access, new_refresh = refresh_access(refresh)
print("   new access token works for", read_token(new_access)["sub"])
try:
    refresh_access(refresh)
except jwt.InvalidTokenError as err:
    print("   second use:", err)

print("\n4. Key rotation with kid")
KEYS["k2"] = secrets.token_urlsafe(32)
CURRENT = "k2"
fresh = make_token("ben", "access", 15)
print("   new tokens use", jwt.get_unverified_header(fresh)["kid"], "and old ones still pass:",
      read_token(new_access)["sub"])
del KEYS["k1"]                                           # after the longest token lifetime has passed
try:
    read_token(new_access)
except jwt.InvalidTokenError as err:
    print("   after k1 is removed:", err)''', long=True)
K.code('oauth2_api', r'''
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
      list(scheme["flows"]["password"]["scopes"]))''', long=True)
K.code('cors_headers', r'''
# CORS and security headers in FastAPI. pip install fastapi httpx
import warnings

warnings.filterwarnings("ignore", message="Using `httpx` with")   # a notice from Starlette 1.10 about its test client
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shop.example.com"],          # an exact list, never "*" with cookies
    allow_origin_regex=r"https://[a-z0-9-]+\.preview\.example\.com",
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.get("/orders")
def orders():
    return [{"id": 1, "total": 12.5}]


client = TestClient(app)
CORS = ["access-control-allow-origin", "access-control-allow-credentials", "access-control-allow-methods",
        "access-control-allow-headers", "access-control-max-age", "vary"]


def show(label, r):
    print(f"{label} -> {r.status_code}")
    for name in CORS:
        if name in r.headers:
            print(f"   {name}: {r.headers[name]}")
    if not any(name in r.headers for name in CORS[:1]):
        print("   (no Access-Control-Allow-Origin, so the browser hides the answer from the page)")


print("1. A simple GET from the shop's own front end")
show("GET /orders  Origin: https://shop.example.com",
     client.get("/orders", headers={"Origin": "https://shop.example.com"}))

print("\n2. The same GET from an unknown site")
r = client.get("/orders", headers={"Origin": "https://evil.example"})
show("GET /orders  Origin: https://evil.example", r)
print("   but the server still answered", r.json())
print("   CORS is checked by the browser, not the server, so it never replaces a login")

print("\n3. A preflight: the browser asks before a POST with an Authorization header")
show("OPTIONS /orders  from a preview site", client.options("/orders", headers={
    "Origin": "https://pr-42.preview.example.com",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "authorization,content-type"}))

print("\n4. A preflight for DELETE, which is not allowed")
r = client.options("/orders", headers={"Origin": "https://shop.example.com", "Access-Control-Request-Method": "DELETE"})
print(f"OPTIONS /orders  DELETE -> {r.status_code} {r.text}")

print("\n5. Security headers on every answer")
r = client.get("/orders")
for name in ["strict-transport-security", "x-content-type-options", "content-security-policy", "referrer-policy"]:
    print(f"   {name}: {r.headers[name]}")''', long=True)
K.code('owasp_demo', r'''
# Four common API holes and their fixes: injection, mass assignment, SSRF and unlimited results.
import ipaddress
import sqlite3
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, ValidationError

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, is_admin INTEGER)")
db.executemany("INSERT INTO users (name, email, is_admin) VALUES (?, ?, ?)",
               [("ann", "ann@shop.example", 0), ("ben", "ben@shop.example", 0), ("root", "root@shop.example", 1)])

print("1. SQL injection")
name = "x' OR '1'='1"
unsafe = f"SELECT name, email FROM users WHERE name = '{name}'"
print("   query built with an f-string:", unsafe)
print("   rows:", db.execute(unsafe).fetchall())
safe = db.execute("SELECT name, email FROM users WHERE name = ?", (name,)).fetchall()
print("   with a ? placeholder        :", safe, "(the input is only ever a value)")

print("\n2. Mass assignment: the client sends a field it should never set")
body = {"name": "eve", "email": "eve@shop.example", "is_admin": True}


class SignupIn(BaseModel):
    model_config = ConfigDict(extra="forbid")        # unknown fields are an error, not silently used
    name: str = Field(min_length=2, max_length=30)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[a-z]+$")


naive = dict(body)                                   # copying the whole body into the database row
print("   naive copy would store is_admin =", naive["is_admin"])
try:
    SignupIn(**body)
except ValidationError as err:
    first = err.errors()[0]
    print("   with an allowlist model:", first["loc"], first["msg"])

print("\n3. SSRF: the API fetches a URL that the user gives (a webhook, an avatar)")


def safe_to_fetch(url):
    parts = urlsplit(url)
    if parts.scheme != "https":
        return "refused: only https"
    try:
        ip = ipaddress.ip_address(parts.hostname)
    except ValueError:
        return "allowed (a name: resolve it and check the IP again before connecting)"
    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
        return f"refused: {ip} is an internal address"
    return "allowed"


for url in ["https://hooks.partner.example/new-order", "http://hooks.partner.example/x",
            "https://127.0.0.1:8000/admin", "https://169.254.169.254/latest/meta-data/",
            "https://10.0.0.5/internal", "https://93.184.215.14/ping"]:
    print(f"   {url:44} {safe_to_fetch(url)}")

print("\n4. Unlimited results: always cap the page size")


def list_users(limit=20):
    limit = max(1, min(limit, 100))                  # the client asks, the server decides
    return db.execute("SELECT id, name FROM users ORDER BY id LIMIT ?", (limit,)).fetchall()


print("   limit=2       ->", list_users(2))
print("   limit=1000000 -> at most 100 rows, here", len(list_users(1_000_000)))''', long=True)

WHY = 'FastAPI&#39;s test client runs the app in a helper thread, and threads do not work in the browser&#39;s Python. Install everything with <code>pip install fastapi httpx pyjwt python-multipart</code>.'

K.lesson('idea', 'What API security is and why every endpoint needs it', f'''
{src('RFC 7519 (JWT), RFC 6749 (OAuth 2.0), RFC 7636 (PKCE), RFC 6750 (Bearer tokens), the WHATWG Fetch standard (CORS), the OWASP API Security Top 10 2023, the OWASP Password Storage and Secrets Management cheat sheets, the FastAPI security tutorial, PyJWT 2.15 and the Django 6.1 password hashers.')}
{wwh('<b>API security</b> is the set of checks that decide who is calling (<b>authentication</b>), what they may do (<b>authorization</b>), and how much they may ask for. It also covers how secrets such as passwords and keys are stored, and what a browser is allowed to share between sites.',
     'An API is open to the whole internet. Anyone can send any request with curl, change an id in the URL, add a field to the JSON or send a million requests. Most real breaches of APIs are not clever cryptography attacks. They are a missing check on one endpoint.',
     'Passwords are stored as slow salted hashes. A login gives a <b>signed token</b> (often a JWT) that each request carries in the Authorization header. Every endpoint checks the token, the scope and the owner of the object. CORS tells browsers which other sites may read the answers. Rate limits, input models and secret keys outside the code close the rest.')}
{viz('pyapisec')}
{versus('Four ways to know who is calling', ['', 'Session cookie', 'JWT bearer token', 'API key', 'OAuth 2.0'], [
    ['What the client holds', 'A random session id in a cookie', 'A signed token with claims', 'A long random string', 'An access token from an authorization server'],
    ['What the server keeps', 'A session table', 'Only the secret key', 'A table of hashed keys', 'Depends on the token type'],
    ['Log out at once', 'Easy: delete the session', 'Hard: wait for exp or keep a deny list', 'Delete the key', 'Revoke at the authorization server'],
    ['Watch out for', 'CSRF, so use SameSite and CSRF tokens', 'Long lifetimes, alg confusion, storing in localStorage', 'Keys leaked in code or logs', 'Using the wrong flow'],
    ['Good for', 'Websites with server pages (Django, Flask)', 'APIs and mobile apps', 'Server to server calls', 'Letting another app act for a user']],
    'These are not rivals. A typical system uses OAuth 2.0 to log in, gets a JWT as the access token, and uses API keys for partner servers.')}
''', kw=['API security', 'authentication', 'authorization', 'JWT', 'OAuth 2.0', 'API key', 'session cookie', 'CORS', 'OWASP'])

K.lesson('passwords', 'Storing passwords and secrets', f'''
{run('passwords')}
{table(['Way to store a password', 'Verdict', 'Why'], [
    ['Plain text', 'Never', 'One leak shows every password, and people reuse them on other sites'],
    ['Encrypted', 'Never', 'Whoever has the key can read them all'],
    ['sha256(password)', 'Never', 'Billions of guesses a second on a graphics card, and the same password gives the same hash'],
    ['sha256(salt + password)', 'Weak', 'The salt stops shared tables, but the hash is still fast'],
    ['PBKDF2, bcrypt, scrypt, Argon2id', 'Yes', 'Salted and slow on purpose. Argon2id and scrypt also need memory']])}
{steps('What the example shows', [
    'The two sha256 lines for sunshine are identical, so one cracked hash cracks every user with that password.',
    'With a random salt the same password gave two different PBKDF2 strings. The stored string keeps the algorithm, rounds and salt, exactly in the format Django uses (Django&#39;s own hasher produced the same string in a check).',
    '600,000 rounds took about 120 ms. The OWASP Password Storage cheat sheet asks for at least 600,000 rounds of PBKDF2-SHA256, and Django 6.1 uses 1,500,000.',
    'hmac.compare_digest compares in constant time, so the response time leaks nothing.',
    'Tokens, keys and reset codes come from the secrets module. The random module is for games and simulations only.'])}
{note('Keep secret keys out of the code: read them with <code>os.environ["SECRET_KEY"]</code>, keep a local .env file in .gitignore, and use a vault (AWS Secrets Manager, HashiCorp Vault) in production. A key that was ever pushed to git is burnt: rotate it, because deleting the commit does not remove copies.', 'exam')}
''', kw=['password hashing', 'salt', 'PBKDF2', 'bcrypt', 'scrypt', 'Argon2id', 'rainbow table', 'compare_digest', 'secrets', 'environment variables'])

K.lesson('jwt', 'JSON Web Tokens from scratch', f'''
{run('jwt_by_hand')}
{table(['Part', 'What it holds', 'Example'], [
    ['Header', 'The algorithm and the type', '&#123;"alg": "HS256", "typ": "JWT"&#125;'],
    ['Payload (claims)', 'Who, what and until when', 'sub (user), exp (expiry), iat (issued), nbf (not before), aud (audience), iss (issuer), jti (id), scope'],
    ['Signature', 'HMAC-SHA256 of header.payload with the secret key', 'base64url of 32 bytes'],
    ['Encoding', 'base64url without = padding, parts joined with dots', 'eyJhbGci... . eyJzdWIi... . Q46Cf6DE...']])}
{steps('What the example shows', [
    'A JWT is three base64url parts. The first two are plain JSON that anyone can decode, so a JWT hides nothing. It only proves who made it.',
    'Changing role to admin without the secret made the signature check fail. So did a token signed with another key.',
    'A token past its exp was refused even though the signature was fine.',
    'The verify function decides the algorithm itself. A token that says "alg": "none" is refused instead of trusted.',
    'PyJWT, the library used next, made the exact same token from the same claims and key, byte for byte.'])}
{deep('HS256 or RS256', '<p><b>HS256</b> uses one shared secret to sign and to check, so every service that checks tokens could also make them. <b>RS256</b> and <b>ES256</b> sign with a private key and check with a public key, which an auth server publishes as a <b>JWKS</b> (a JSON list of public keys, chosen by the kid in the header). Use them when many services must check tokens but only one may issue them.</p>')}
''', kw=['JWT', 'claims', 'HS256', 'HMAC', 'base64url', 'exp', 'alg none', 'RS256', 'JWKS'])

K.lesson('tokens', 'Real tokens with PyJWT: expiry, refresh and key rotation', f'''
{run('pyjwt_tokens')}
{table(['Practice', 'Why'], [
    ['Pin algorithms=["HS256"] when decoding', 'Stops alg confusion and alg none tricks'],
    ['Short access tokens (5 to 15 minutes)', 'A stolen token is useful only for minutes'],
    ['Long refresh tokens that work once (rotation)', 'A second use shows theft, so all sessions can be ended'],
    ['Check aud and iss', 'A token for another API or from another issuer is refused'],
    ['kid in the header with a key table', 'Keys can be swapped without logging everyone out'],
    ['jti and a deny list for log out', 'A JWT cannot be deleted, so remember the ids of revoked ones until they expire'],
    ['Keep tokens out of URLs and logs', 'URLs end up in browser history, proxies and log files']])}
{note('In a browser, an HttpOnly, Secure, SameSite cookie is the safest place for a token, because JavaScript (and so an XSS bug) cannot read it. localStorage is readable by any script on the page.', 'tip')}
''', kw=['PyJWT', 'access token', 'refresh token', 'rotation', 'audience', 'issuer', 'kid', 'jti', 'revocation', 'HttpOnly cookie'])

K.lesson('oauth', 'OAuth 2.0 logins, scopes and owner checks in FastAPI', f'''
{local('oauth2_api', WHY)}
{table(['OAuth 2.0 flow', 'Who uses it', 'Notes'], [
    ['Authorization code with PKCE', 'Web, mobile and single page apps logging users in', 'The standard choice today. PKCE stops a stolen code from being used'],
    ['Client credentials', 'A server calling another server, with no user', 'The client id and secret give a token'],
    ['Device code', 'TVs and command line tools', 'The user types a short code on another device'],
    ['Password (resource owner)', 'Only your own first party app', 'Legacy. The FastAPI tutorial uses it because it is simple'],
    ['Implicit', 'Nobody', 'Deprecated. Tokens in the URL leaked']])}
{steps('What the example shows', [
    'A wrong password gave 401 with WWW-Authenticate: Bearer, the header RFC 6750 asks for. The message does not say whether the name or the password was wrong.',
    'The login hashes a password even for an unknown name, so the response time does not reveal which names exist.',
    'Ben asked for notes:write but only got the scopes he really has. Writing then gave 403, which means logged in but not allowed.',
    'Ben&#39;s valid token could not read Ann&#39;s note: the owner check answered 404. A valid token is not the same as permission for every object.',
    'OAuth2PasswordBearer also put the login and the scopes into the OpenAPI docs, so /docs shows an Authorize button.'])}
{versus('401 or 403', ['', '401 Unauthorized', '403 Forbidden'], [
    ['Meaning', 'We do not know who you are', 'We know who you are, and the answer is no'],
    ['Typical cause', 'No token, bad signature, expired', 'Missing scope or role'],
    ['Client should', 'Log in or refresh the token', 'Not retry, ask for access']],
    'For another user&#39;s object many APIs answer 404, so that the caller cannot tell which ids exist.')}
''', kw=['OAuth 2.0', 'PKCE', 'authorization code', 'client credentials', 'scopes', 'OAuth2PasswordBearer', 'Security', '401', '403', 'WWW-Authenticate'])

K.lesson('cors', 'CORS, CSRF and security headers', f'''
{local('cors_headers', 'FastAPI&#39;s test client runs the app in a helper thread, and threads do not work in the browser&#39;s Python. Install everything with <code>pip install fastapi httpx</code>.')}
{steps('What the example shows', [
    'For the listed origin the answer carried Access-Control-Allow-Origin with that exact origin, plus Vary: Origin so caches keep one copy per origin.',
    'For an unknown origin the header was missing, so a browser hides the answer. The server still ran the request, which is why CORS never replaces a login.',
    'The preflight OPTIONS listed the allowed methods and headers. Starlette also lists the safe headers that browsers always allow, such as Accept.',
    'A preflight for DELETE was refused with 400.',
    'A small middleware added HSTS (always use HTTPS), nosniff, a strict Content-Security-Policy and no referrer to every answer.'])}
{versus('CORS and CSRF', ['', 'CORS', 'CSRF'], [
    ['What it is', 'Rules that let a server allow other sites to READ its answers in a browser', 'An attack where another site makes your browser SEND a request with your cookies'],
    ['Who enforces it', 'The browser, from the server&#39;s headers', 'The server, with tokens and cookie settings'],
    ['When it matters', 'Any API called from a page on another origin', 'When the login is a cookie the browser adds by itself'],
    ['The fix or setting', 'An exact list of origins, never * with credentials', 'SameSite=Lax or Strict cookies plus a CSRF token (Django has it built in)'],
    ['Bearer tokens', 'Still needed', 'Not a risk: the browser never adds the Authorization header by itself']],
    'CORS loosens the same origin policy on purpose. CSRF protection closes a hole that cookies open.')}
''', kw=['CORS', 'preflight', 'Access-Control-Allow-Origin', 'same origin policy', 'CSRF', 'SameSite', 'HSTS', 'Content-Security-Policy', 'security headers'])

K.lesson('owasp', 'The OWASP API Security Top 10', f'''
{run('owasp_demo')}
{table(['OWASP API 2023', 'What goes wrong', 'Python fix'], [
    ['API1 Broken Object Level Authorization', 'Change the id in the URL and read someone else&#39;s data', 'Check the owner on every object (filter by user in the query)'],
    ['API2 Broken Authentication', 'Weak passwords, no rate limit on login, tokens that never expire', 'Slow hashes, login limits, short exp, pinned algorithms'],
    ['API3 Broken Object Property Level Authorization', 'Mass assignment (is_admin from the body) or returning secret fields', 'Input models with extra="forbid", response_model for output'],
    ['API4 Unrestricted Resource Consumption', 'Huge pages, huge uploads, no rate limit', 'Cap limit, body size and requests per client'],
    ['API5 Broken Function Level Authorization', 'A normal user can call an admin endpoint', 'Role and scope checks as dependencies'],
    ['API6 Unrestricted Access to Sensitive Business Flows', 'Bots buy every ticket or create many accounts', 'Limits per account, device and payment, CAPTCHA'],
    ['API7 Server Side Request Forgery', 'The API fetches a user URL that points inside the network', 'https only, block internal addresses, an allowlist'],
    ['API8 Security Misconfiguration', 'Debug pages, open CORS, missing headers, default keys', 'DEBUG off, exact CORS list, security headers'],
    ['API9 Improper Inventory Management', 'An old /v1 or a test server nobody patches', 'A list of every API version and host, retire old ones'],
    ['API10 Unsafe Consumption of APIs', 'Trusting data from a partner API without checks', 'Validate it with models, use timeouts, follow no redirects blindly']])}
{steps('What the example shows', [
    'The f-string query turned the input into SQL and returned every user. The ? placeholder sent it as a value and returned nothing. Injection is on the main OWASP Top 10 list, and the fix is the same in every database driver and ORM.',
    'A model with extra="forbid" refused is_admin instead of saving it.',
    'The URL check refused http, 127.0.0.1, the cloud metadata address 169.254.169.254 and a private 10.x address.',
    'A client that asked for a million rows got at most 100.'])}
{scene('a bug bounty report', '<p>A tester signs up for a delivery app and opens their own order: GET /api/orders/81234. They change the number to 81233 and see a stranger&#39;s name, address and phone. Every endpoint checked that the token was valid, and none checked who owned the order. The fix was to write Order.objects.get(id=order_id, customer=request.user), and a test now calls every id endpoint with a second user and expects 404.</p>')}
''', kw=['OWASP API Top 10', 'BOLA', 'mass assignment', 'SQL injection', 'SSRF', 'resource consumption', 'misconfiguration', 'extra forbid'])

K.lesson('ops', 'Rate limits, HTTPS, logging and secrets in production', f'''
{table(['Control', 'How in Python', 'Notes'], [
    ['HTTPS everywhere', 'TLS at the proxy (nginx, a cloud load balancer), HSTS header', 'Tokens and passwords travel in every request'],
    ['Rate limits', 'A token bucket per client, often in Redis, or slowapi for FastAPI and DRF throttles', 'Send 429 Too Many Requests with Retry-After'],
    ['Login limits', 'Count failures per account and per IP, slow down or lock for a while', 'Stops password guessing'],
    ['Secrets', 'os.environ, a vault, never in git, rotate on a schedule', 'Scan commits with a secret scanner in CI'],
    ['Logging', 'Log user id, path, status and time, never passwords or tokens', 'Mask Authorization headers in error reports'],
    ['Dependencies', 'pip-audit or the GitHub dependency alerts', 'Most vulnerabilities come from old libraries'],
    ['Least privilege', 'A database user that can only do what the app needs', 'A leak then exposes less']])}
{steps('A security checklist before an API goes live', [
    'Every endpoint has an authentication dependency, and public ones are marked public on purpose.',
    'Every endpoint that takes an id filters by the caller, and a test with a second user proves it.',
    'Input models forbid extra fields, response models hide secret fields, and page sizes are capped.',
    'Passwords use a slow salted hash, tokens are short lived and checked with pinned algorithms, aud and iss.',
    'CORS lists exact origins, security headers are set, DEBUG is off and keys come from the environment.',
    'Login and expensive endpoints have rate limits, and logs never contain tokens.'])}
''', kw=['HTTPS', 'TLS', 'rate limiting', '429', 'token bucket', 'secrets management', 'logging', 'pip-audit', 'least privilege'])

K.lesson('maths', 'The maths: guessing, entropy, hashing cost and rate limits', f'''
{fxs(fx('Entropy of a random secret', 'bits = length &times; log<sub>2</sub>(alphabet size)', '12 random lower case letters: 12 &times; log<sub>2</sub> 26 &asymp; 56.4 bits.', key=True),
     fx('Guesses to try every value', 'guesses = 2<sup>bits</sup>', 'A 6 digit code: 10<sup>6</sup> = 1,000,000 values.', key=True),
     fx('Time to crack', 'time = guesses &times; cost per guess / machines', 'With PBKDF2 at 0.12 s, one million guesses take 120,000 s on one core.', key=True),
     fx('Chance to guess with a rate limit', 'P = attempts / values', '5 tries on a 6 digit code: 5 / 1,000,000 = 0.0005 %.'),
     fx('Token bucket', 'allowed in t seconds &le; capacity + rate &times; t', 'Capacity 10, rate 2 per second: at most 10 + 2 &times; 60 = 130 requests in a minute.'),
     fx('Birthday bound for random ids', 'P(any repeat) &asymp; n<sup>2</sup> / 2<sup>bits + 1</sup>', '1 billion random 128 bit ids: about 10<sup>18</sup> / 2<sup>129</sup>, practically zero.'))}
{steps('Worked example: is a 6 digit login code safe?', [
    'There are 10<sup>6</sup> = 1,000,000 codes, which is about 20 bits.',
    'Without a limit a script tries them all in minutes, because each guess costs only one HTTP request.',
    'With 5 attempts per code and a new code each time, the chance of a lucky guess is 5 / 1,000,000.',
    'The code also expires after 10 minutes, so an attacker cannot collect tries over days.',
    eq('short codes are only safe together with attempt limits and expiry')])}
{deep('Why HMAC and not sha256(secret + message)', '<p>SHA-256 is built so that from sha256(secret + message) anyone can compute sha256(secret + message + more) without knowing the secret. This is the <b>length extension attack</b>. HMAC hashes twice with two derived keys, which closes it. That is why JWTs, webhooks and signed cookies all use HMAC.</p>')}
''', kw=['entropy', 'brute force', 'key stretching', 'token bucket', 'birthday bound', 'length extension', 'HMAC'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Never store passwords in plain text, keep secrets out of code, use HTTPS and know 401 from 403.</p>',
    '<p>Hash passwords with PBKDF2 or Argon2, issue and check JWTs with PyJWT, protect FastAPI endpoints with OAuth2PasswordBearer and scopes, and set CORS correctly.</p>',
    '<p>Add owner checks everywhere, refresh token rotation, key rotation with kid, rate limits and security headers, and test each with a second user.</p>',
    '<p>Run an OAuth 2.0 server with PKCE and RS256 keys published as JWKS, threat model each API against the OWASP list, and audit logs and dependencies in CI.</p>')}
{grow('Safe defaults.', 'Correct tokens and checks.', 'Defence in depth.')}
{deep('OpenID Connect', '<p>OAuth 2.0 only says what an app may do. <b>OpenID Connect</b> adds who the user is: the auth server also returns an <b>ID token</b>, a JWT with the user&#39;s id, name and e-mail, signed with RS256. "Log in with Google" is OpenID Connect. Libraries such as Authlib handle the flow in Flask, Django and FastAPI.</p>')}
''', kw=['beginner', 'expert', 'OpenID Connect', 'ID token', 'Authlib', 'threat model'])

lc(2325, 'Decode the Message', 'decode-the-message', 'e', 'Build a substitution table from first appearances', 'This is a simple substitution cipher. The first time each letter appears in the key it stands for the next letter of the alphabet. A dict holds the table, and spaces stay as they are. Ciphers like this are easy to break, which is why real systems use keys and HMAC instead.', r'''
def decode_message(key, message):
    table = {" ": " "}
    for ch in key:
        if ch != " " and ch not in table:
            table[ch] = chr(ord("a") + len(table) - 1)
    return "".join(table[ch] for ch in message)
''', [('decode_message("the quick brown fox jumps over the lazy dog", "vkbs bs t suepuv")', 'this is a secret'), ('decode_message("eljuxhpwnyrdgtqkviszcfmabo", "zwx hnfx lqantp mnoeius ycgk vcnjrdb")', 'the five boxing wizards jump quickly')])
lc(1844, 'Replace All Digits with Characters', 'replace-all-digits-with-characters', 'e', 'Shift a letter by a digit', 'Every digit says how far to move the letter before it, the same idea as a Caesar shift. chr(ord(letter) + digit) does the move.', r'''
def replace_digits(s):
    out = list(s)
    for i in range(1, len(s), 2):
        out[i] = chr(ord(s[i - 1]) + int(s[i]))
    return "".join(out)
''', [('replace_digits("a1c1e1")', 'abcdef'), ('replace_digits("a1b2c3d4e")', 'abbdcfdhe')])
lc(1528, 'Shuffle String', 'shuffle-string', 'e', 'Put each character at its target index', 'A transposition: indices[i] says where s[i] belongs. Fill a list of the right length, then join it.', r'''
def restore_string(s, indices):
    out = [""] * len(s)
    for ch, place in zip(s, indices):
        out[place] = ch
    return "".join(out)
''', [('restore_string("codeleet", [4, 5, 6, 7, 0, 2, 1, 3])', 'leetcode'), ('restore_string("abc", [0, 1, 2])', 'abc')])
lc(1461, 'Check If a String Contains All Binary Codes of Size K', 'check-if-a-string-contains-all-binary-codes-of-size-k', 'm', 'A set of every window of length k', 'There are 2<sup>k</sup> codes of length k, the same count an attacker must try to guess a k bit token. Put every window of the string in a set and compare its size with 2<sup>k</sup>.', r'''
def has_all_codes(s, k):
    seen = {s[i:i + k] for i in range(len(s) - k + 1)}
    return len(seen) == 2 ** k
''', [('has_all_codes("00110110", 2)', True), ('has_all_codes("0110", 1)', True), ('has_all_codes("0110", 2)', False)])
lc(187, 'Repeated DNA Sequences', 'repeated-dna-sequences', 'm', 'Two sets: seen once and seen again', 'Slide a window of 10 letters and remember each one in a set. A window that is already there is a repeat, like a replayed request id that a server must refuse. The answer is sorted here so the tests can compare it.', r'''
def find_repeated_dna_sequences(s):
    seen, repeated = set(), set()
    for i in range(len(s) - 9):
        part = s[i:i + 10]
        if part in seen:
            repeated.add(part)
        seen.add(part)
    return sorted(repeated)
''', [('find_repeated_dna_sequences("AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT")', ['AAAAACCCCC', 'CCCCCAAAAA']), ('find_repeated_dna_sequences("AAAAAAAAAAAAA")', ['AAAAAAAAAA'])])
lc(1980, 'Find Unique Binary String', 'find-unique-binary-string', 'm', 'Cantor diagonal: differ from string i at place i', 'Take bit i of string i and flip it. The new string differs from every given string in at least one place, so it cannot be any of them. The same trick proves that some sets cannot be listed.', r'''
def find_different_binary_string(nums):
    return "".join("1" if nums[i][i] == "0" else "0" for i in range(len(nums)))
''', [('find_different_binary_string(["01", "10"])', '11'), ('find_different_binary_string(["00", "01"]) not in ["00", "01"]', True), ('find_different_binary_string(["111", "011", "001"])', '000')])
lc(721, 'Accounts Merge', 'accounts-merge', 'm', 'Union find over e-mail addresses', 'Two accounts are one person when they share an e-mail, like linking identities in a login system. Union find joins every e-mail with the first e-mail of its account, then each group becomes one sorted account. The list is sorted at the end so the tests can compare it.', r'''
def accounts_merge(accounts):
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    owner = {}
    for name, *emails in accounts:
        for email in emails:
            parent.setdefault(email, email)
            owner[email] = name
            parent[find(email)] = find(emails[0])
    groups = {}
    for email in parent:
        groups.setdefault(find(email), []).append(email)
    return sorted([owner[root]] + sorted(emails) for root, emails in groups.items())
''', [('accounts_merge([["John", "johnsmith@mail.com", "john_newyork@mail.com"], ["John", "johnsmith@mail.com", "john00@mail.com"], ["Mary", "mary@mail.com"], ["John", "johnnybravo@mail.com"]])', [['John', 'john00@mail.com', 'john_newyork@mail.com', 'johnsmith@mail.com'], ['John', 'johnnybravo@mail.com'], ['Mary', 'mary@mail.com']]), ('accounts_merge([["Gabe", "Gabe0@m.co", "Gabe3@m.co", "Gabe1@m.co"], ["Kevin", "Kevin3@m.co", "Kevin5@m.co", "Kevin0@m.co"], ["Ethan", "Ethan5@m.co", "Ethan4@m.co", "Ethan0@m.co"], ["Hanzo", "Hanzo3@m.co", "Hanzo1@m.co", "Hanzo0@m.co"], ["Fern", "Fern5@m.co", "Fern1@m.co", "Fern0@m.co"]])', [['Ethan', 'Ethan0@m.co', 'Ethan4@m.co', 'Ethan5@m.co'], ['Fern', 'Fern0@m.co', 'Fern1@m.co', 'Fern5@m.co'], ['Gabe', 'Gabe0@m.co', 'Gabe1@m.co', 'Gabe3@m.co'], ['Hanzo', 'Hanzo0@m.co', 'Hanzo1@m.co', 'Hanzo3@m.co'], ['Kevin', 'Kevin0@m.co', 'Kevin3@m.co', 'Kevin5@m.co']])])
lc(420, 'Strong Password Checker', 'strong-password-checker', 'h', 'Count runs, then spend deletions where they save a replacement', 'A strong password has 6 to 20 characters, a lower case letter, an upper case letter and a digit, and never three equal characters in a row. Short passwords only need inserts. Long ones need deletes, and a delete in a run whose length is a multiple of 3 saves one replacement, so spend deletes on those runs first, then on runs with remainder 1 (two deletes) and then three at a time.', r'''
def strong_password_checker(password):
    n = len(password)
    missing = 3 - (any(c.islower() for c in password) + any(c.isupper() for c in password)
                   + any(c.isdigit() for c in password))
    if n < 6:
        return max(missing, 6 - n)
    replace = one = two = 0
    i = 2
    while i < n:
        if password[i] == password[i - 1] == password[i - 2]:
            length = 2
            while i < n and password[i] == password[i - 1]:
                length += 1
                i += 1
            replace += length // 3
            if length % 3 == 0:
                one += 1
            elif length % 3 == 1:
                two += 1
        else:
            i += 1
    if n <= 20:
        return max(missing, replace)
    delete = n - 20
    replace -= min(delete, one)
    replace -= min(max(delete - one, 0), two * 2) // 2
    replace -= max(delete - one - 2 * two, 0) // 3
    return delete + max(missing, replace)
''', [('strong_password_checker("a")', 5), ('strong_password_checker("aA1")', 3), ('strong_password_checker("1337C0d3")', 0), ('strong_password_checker("aaa111")', 2), ('strong_password_checker("aaaaaaaaaaaaaaaaaaaaa")', 7), ('strong_password_checker("bbaaaaaaaaaaaaaaacccccc")', 8)])
lc(2156, 'Find Substring With Given Hash Value', 'find-substring-with-given-hash-value', 'h', 'Rolling hash, walking from the right', 'The hash gives the first letter the power p<sup>0</sup>, so it is easy to add a letter on the LEFT: multiply by p and add the new value. Walk from the end of the string, drop the letter that falls out of the window, and remember the leftmost window that matches. Rolling hashes also power rsync and duplicate file checks.', r'''
def sub_str_hash(s, power, modulo, k, hash_value):
    n = len(s)
    top = pow(power, k - 1, modulo)
    h = 0
    best = 0
    for i in range(n - 1, -1, -1):
        h = (h * power + ord(s[i]) - 96) % modulo
        if i + k < n:
            h = (h - (ord(s[i + k]) - 96) * top * power) % modulo
        if i + k <= n and h == hash_value:
            best = i
    return s[best:best + k]
''', [('sub_str_hash("leetcode", 7, 20, 2, 0)', 'ee'), ('sub_str_hash("fbxzaad", 31, 100, 3, 32)', 'fbx')])
lc(1392, 'Longest Happy Prefix', 'longest-happy-prefix', 'h', 'The KMP failure table', 'A happy prefix is also a suffix. The prefix function of KMP stores, for each position, the longest proper prefix that ends there, and its last value is the answer. It runs in O(n), with no hash collisions to worry about.', r'''
def longest_prefix(s):
    fail = [0] * len(s)
    j = 0
    for i in range(1, len(s)):
        while j and s[i] != s[j]:
            j = fail[j - 1]
        if s[i] == s[j]:
            j += 1
        fail[i] = j
    return s[:fail[-1]]
''', [('longest_prefix("level")', 'l'), ('longest_prefix("ababab")', 'abab'), ('longest_prefix("abc")', '')])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Problems that match the ideas of this chapter: substitution and shift ciphers, a transposition, the space of k bit codes, spotting replayed sequences, a value that differs from every known one, linking accounts that share an e-mail, a full strong password checker, a rolling hash and the KMP prefix table.</p>'), kw=['LeetCode', 'hashing', 'rolling hash', 'union find', 'KMP', 'greedy', 'strings'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Store passwords with a slow salted hash (PBKDF2, bcrypt, scrypt or Argon2id), compare with hmac.compare_digest and make tokens with the secrets module.',
    'A JWT is header.payload.signature in base64url. Anyone can read it, only the key holder can sign it. Pin the algorithm and check exp, aud and iss.',
    'Use short access tokens, refresh tokens that work once, and a kid for key rotation. OAuth 2.0 with PKCE is the standard login flow.',
    'Authentication is not authorization: check scopes (403) and the owner of every object (404) on every endpoint.',
    'CORS lets listed origins read answers in a browser, CSRF needs SameSite cookies and tokens, and the OWASP API Top 10 lists the common holes.'],
    'Next: the web revision exam.')}
{files('Three tasks: store passwords like Django, sign and check JWTs by hand, and write the CORS rules a server applies.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which way of storing passwords is correct?', ['Plain text in a safe table', 'sha256 of the password', 'A slow salted hash such as PBKDF2 or Argon2id', 'Encrypted with a key in the code'], 2, 'Slow and salted.', 'A fast hash can be guessed billions of times a second.')
K.quiz('e', 'Can anyone read the payload of a JWT without the secret key?', ['No, it is encrypted', 'Yes, it is only base64url encoded and signed', 'Only the server', 'Only with the private key'], 1, 'Signed, not encrypted.', 'Never put secrets in the payload.')
K.quiz('e', 'Which status code means "logged in, but not allowed to do this"?', ['401', '403', '404', '429'], 1, 'Forbidden.', '401 means the server does not know who you are.')
K.quiz('m', 'Why does every user get a random salt?', ['To make hashing faster', 'So the same password gives different hashes and precomputed tables do not work', 'To encrypt the password', 'Because Django needs it'], 1, 'Unique hashes.', 'The salt is stored next to the hash. It is not a secret.')
K.quiz('m', 'An attacker changes "role": "user" to "admin" in a JWT. What happens on a correct server?', ['They become admin', 'The signature check fails and the token is refused', 'The token is decrypted', 'The server asks for a password'], 1, 'The HMAC no longer matches.', 'They would need the secret key to sign the new payload.')
K.quiz('m', 'Why pass algorithms=["HS256"] to jwt.decode?', ['It is faster', 'So the token cannot choose a weaker algorithm such as "none"', 'PyJWT has no default', 'To encrypt it'], 1, 'Pin the algorithm.', 'Never let the token decide how it is checked.')
K.quiz('m', 'Ben has a valid token and requests /notes/1, which belongs to Ann. What should the API do?', ['Return the note, the token is valid', 'Refuse with 404 (or 403) after checking the owner', 'Return 500', 'Log Ben out'], 1, 'Object level authorization.', 'It is number 1 on the OWASP API Top 10.')
K.quiz('m', 'What does CORS protect?', ['The server from all attacks', 'Users: it decides which other sites may read the answers in a browser', 'Passwords in the database', 'The network from DDoS'], 1, 'Browser rule.', 'curl and scripts ignore CORS completely.')
K.quiz('m', 'Why is a refresh token rotated (usable once)?', ['To save memory', 'A second use shows the token was stolen, so the server can end all sessions', 'Because JWTs expire', 'It is required by HTTP'], 1, 'Theft detection.', 'Access tokens stay short, refresh tokens are long but single use.')
K.quiz('h', 'Why can allow_origins=["*"] not be combined with credentials (cookies) in CORS?', ['It can', 'Browsers refuse the wildcard with credentials, because any site could then read logged in data', 'It is slower', 'FastAPI forbids it only in debug'], 1, 'Cookies plus any site would be a leak.', 'Echo the exact listed origin and add Vary: Origin.')
K.quiz('h', 'An API uses Bearer tokens in the Authorization header only, no cookies. How big is the CSRF risk?', ['Very high', 'Very low, because the browser never adds that header to a request from another site by itself', 'The same as with cookies', 'CSRF only affects GET'], 1, 'No automatic credentials.', 'CSRF needs credentials the browser attaches on its own, like cookies.')
K.quiz('x', 'In the style of a Stanford CS 155 computer security exam: why is HMAC-SHA256(key, message) used for tokens instead of SHA256(key + message)?', ['HMAC is shorter', 'SHA256(key + message) allows a length extension attack: the attacker can append data and compute a valid hash without the key', 'SHA256 is broken', 'HMAC is encryption'], 1, 'Length extension.', 'HMAC hashes twice with inner and outer keys, which blocks it.')
K.quiz('x', 'In the style of an MIT 6.5660 computer systems security exam: a login endpoint answers "no such user" in 1 ms and "wrong password" in 120 ms. What is the problem and the fix?', ['None', 'The timing reveals which user names exist. Hash a dummy password for unknown users and return one message for both', 'The hash is too slow', 'Use 403 instead'], 1, 'A timing side channel.', 'The FastAPI example hashes even when the user is missing.')

K.calc('e', 'A reset code has 6 random digits. How many different codes exist?', '1000000', '10 choices for each place.', ['Each digit has 10 values.', '10<sup>6</sup>.', eq('1,000,000 codes')], check=10 ** 6)
K.calc('e', 'An access token lives 15 minutes. How many seconds is its exp after iat?', '900', '15 &times; 60.', ['One minute is 60 s.', '15 &times; 60.', eq('900 s')], check=15 * 60)
K.calc('e', 'secrets.token_urlsafe(32) uses 32 random bytes. How many random bits is that?', '256', '8 bits a byte.', ['One byte is 8 bits.', '32 &times; 8.', eq('256 bits')], check=32 * 8)
K.calc('m', 'How many bits of entropy has a random 12 letter lower case password? Round to 1 place.', '56.4', '12 &times; log<sub>2</sub> 26.', ['log<sub>2</sub> 26 &asymp; 4.700.', '12 &times; 4.700 = 56.4.', eq('&asymp; 56.4 bits')], check=56.4, tol=0.05)
K.calc('m', 'PBKDF2 takes 0.12 s per guess. How many seconds does one core need for 1,000,000 guesses?', '120000', 'guesses &times; time.', ['1,000,000 &times; 0.12.', 'That is about 33 hours for ONE user.', eq('120,000 s')], check=1_000_000 * 0.12, tol=1)
K.calc('m', 'A token bucket holds 10 tokens and refills 2 per second. At most how many requests can pass in 60 seconds?', '130', 'capacity + rate &times; time.', ['Start full: 10.', 'Refill 2 &times; 60 = 120.', '10 + 120.', eq('130 requests')], check=10 + 2 * 60)
K.calc('m', 'A JWT base64url encodes a 32 byte HMAC without padding. How many characters is the signature part?', '43', '4 characters for every 3 bytes, no padding.', ['32 bytes = 256 bits.', 'Each base64 character holds 6 bits: 256 / 6 = 42.67.', 'Round up.', eq('43 characters')], check=-(-32 * 8 // 6))
K.calc('m', 'With 5 attempts allowed on a 6 digit code, what is the chance of a lucky guess, in percent?', '0.0005', 'attempts / values &times; 100.', ['5 / 1,000,000 = 0.000005.', 'Times 100.', eq('0.0005 %')], check=5 / 10 ** 6 * 100, tol=0.000001)
K.calc('h', 'Django 6.1 uses 1,500,000 PBKDF2 rounds. How many times slower per guess is that than 600,000 rounds?', '2.5', 'Time grows with rounds.', ['The cost is linear in the rounds.', '1,500,000 / 600,000.', eq('2.5 times')], check=1_500_000 / 600_000)
K.calc('x', 'In the style of a Berkeley CS 161 exam: an API issues 2<sup>32</sup> random session ids of 64 bits. Using the birthday estimate n<sup>2</sup> / 2<sup>65</sup>, what is the chance of at least one repeat? Answer in percent, rounded to 1 place.', '50.0', 'n<sup>2</sup> = 2<sup>64</sup>.', ['n = 2<sup>32</sup>, so n<sup>2</sup> = 2<sup>64</sup>.', '2<sup>64</sup> / 2<sup>65</sup> = 0.5.', 'The estimate is rough at this size (the exact value is about 39 %), but it shows that 64 bits is too few.', eq('&asymp; 50 %, so use 128 bits or more')], check=round(2 ** 64 / 2 ** 65 * 100, 1), tol=0.05)

K.assign('pwstore', 'e', 'Store passwords like Django',
         '<p>Finish three functions. <code>make_hash(password, salt, iterations)</code> returns "pbkdf2_sha256$ITERATIONS$SALT$HASH", where HASH is the base64 text of hashlib.pbkdf2_hmac("sha256", ...). <code>verify_hash(password, stored)</code> returns True only when the password matches, compares with hmac.compare_digest and returns False for a string in any other format. <code>needs_upgrade(stored, iterations)</code> returns True when the stored hash used fewer rounds than the current setting. The tests use only 1,000 rounds so they run fast.</p>',
         r'''
import base64
import hashlib
import hmac


def make_hash(password, salt, iterations):
    """Return "pbkdf2_sha256$ITERATIONS$SALT$HASH" with the hash in base64, like Django."""
    # TODO: use hashlib.pbkdf2_hmac("sha256", ...) with the salt and the number of rounds
    digest = hashlib.sha256(password.encode()).digest()
    return f"pbkdf2_sha256${iterations}${salt}${base64.b64encode(digest).decode()}"


def verify_hash(password, stored):
    """True when the password matches the stored string. Compare in constant time."""
    # TODO: split the stored string, hash the password again with the same salt and rounds,
    # and compare with hmac.compare_digest. A string in another format gives False.
    return False


def needs_upgrade(stored, iterations):
    """True when the stored hash used fewer rounds than the current setting."""
    # TODO
    return False
''', [('make_hash("sunshine", "Qx81LmZ0", 1000)', 'pbkdf2_sha256$1000$Qx81LmZ0$573A5bEvMdabWwPELFbyXnHJdyLkqV5TIjWKk4Xm3/0='), ('make_hash("sunshine", "pW2nB7tR", 1000) != make_hash("sunshine", "Qx81LmZ0", 1000)', True), ('verify_hash("sunshine", make_hash("sunshine", "Qx81LmZ0", 1000))', True), ('verify_hash("Sunshine", make_hash("sunshine", "Qx81LmZ0", 1000))', False), ('verify_hash("sunshine", "md5$abc$def")', False), ('[needs_upgrade(make_hash("a", "s", 1000), 2000), needs_upgrade(make_hash("a", "s", 2000), 2000)]', [True, False])],
         r'''
import base64
import hashlib
import hmac


def make_hash(password, salt, iterations):
    """Return "pbkdf2_sha256$ITERATIONS$SALT$HASH" with the hash in base64, like Django."""
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${base64.b64encode(digest).decode()}"


def verify_hash(password, stored):
    """True when the password matches the stored string. Compare in constant time."""
    parts = stored.split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return False
    _, iterations, salt, _ = parts
    return hmac.compare_digest(make_hash(password, salt, int(iterations)), stored)


def needs_upgrade(stored, iterations):
    """True when the stored hash used fewer rounds than the current setting."""
    return int(stored.split("$")[1]) < iterations
''', 'stored.split("$") gives four parts: the algorithm, the rounds, the salt and the hash. Hash the password again with the same salt and rounds, then compare the two whole strings.', '<p>This is exactly the string Django stores in auth_user.password, so your verify_hash can check real Django hashes. needs_upgrade is how Django raises the rounds over the years: it re-hashes at the next successful login, the only moment the password is known.</p>')
K.assign('jwtcheck', 'm', 'Sign and check JWTs by hand',
         '<p><code>sign_jwt</code> and the helpers are ready. Finish <code>verify_jwt(token, key, now)</code>. Return ["error", "malformed"] when the token does not have three parts or a part is not valid base64url JSON, ["error", "algorithm"] when the header alg is not HS256, ["error", "signature"] when the HMAC does not match, ["error", "expired"] when now &gt;= exp, ["error", "not yet valid"] when now &lt; nbf, and otherwise ["ok", payload]. Check in exactly that order.</p>',
         r'''
import base64
import hashlib
import hmac
import json


def jwt_part(data):
    """dict -> compact JSON -> base64url without = padding."""
    raw = json.dumps(data, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def jwt_unpart(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def jwt_mac(key, signing_input):
    digest = hmac.new(key.encode(), signing_input.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def sign_jwt(payload, key):
    head = jwt_part({"alg": "HS256", "typ": "JWT"})
    body = jwt_part(payload)
    return f"{head}.{body}.{jwt_mac(key, head + '.' + body)}"


def verify_jwt(token, key, now):
    head, body, sig = token.split(".")
    payload = json.loads(jwt_unpart(body))
    # TODO: check the parts, the algorithm, the signature (compare_digest), exp and nbf, in that order
    return ["ok", payload]
''', [('sign_jwt({"sub": "ann", "exp": 1800000900}, "k3y")', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbm4iLCJleHAiOjE4MDAwMDA5MDB9.NZgcMYFCwP1_uYAVTk0otA3VOXrSzJzB0cNoR1hLs5Q'), ('verify_jwt(sign_jwt({"sub": "ann", "exp": 1800000900}, "k3y"), "k3y", 1800000000)', ['ok', {'sub': 'ann', 'exp': 1800000900}]), ('verify_jwt(sign_jwt({"sub": "ann", "exp": 1800000900}, "k3y"), "other", 1800000000)', ['error', 'signature']), ('verify_jwt(sign_jwt({"sub": "ann", "exp": 1800000900}, "k3y"), "k3y", 1800000900)', ['error', 'expired']), ('verify_jwt(sign_jwt({"sub": "ann", "nbf": 1800000100}, "k3y"), "k3y", 1800000000)', ['error', 'not yet valid']), ('verify_jwt(jwt_part({"alg": "none", "typ": "JWT"}) + "." + jwt_part({"sub": "root"}) + ".", "k3y", 0)', ['error', 'algorithm']), ('verify_jwt("only.two", "k3y", 0)', ['error', 'malformed']), ('verify_jwt(sign_jwt({"sub": "ann", "role": "user"}, "k3y").replace(jwt_part({"sub": "ann", "role": "user"}), jwt_part({"sub": "ann", "role": "admin"})), "k3y", 0)', ['error', 'signature'])],
         r'''
import base64
import hashlib
import hmac
import json


def jwt_part(data):
    """dict -> compact JSON -> base64url without = padding."""
    raw = json.dumps(data, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def jwt_unpart(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def jwt_mac(key, signing_input):
    digest = hmac.new(key.encode(), signing_input.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def sign_jwt(payload, key):
    head = jwt_part({"alg": "HS256", "typ": "JWT"})
    body = jwt_part(payload)
    return f"{head}.{body}.{jwt_mac(key, head + '.' + body)}"


def verify_jwt(token, key, now):
    parts = token.split(".")
    if len(parts) != 3:
        return ["error", "malformed"]
    head, body, sig = parts
    try:
        header = json.loads(jwt_unpart(head))
        payload = json.loads(jwt_unpart(body))
    except ValueError:
        return ["error", "malformed"]
    if header.get("alg") != "HS256":
        return ["error", "algorithm"]
    if not hmac.compare_digest(jwt_mac(key, head + "." + body), sig):
        return ["error", "signature"]
    if "exp" in payload and now >= payload["exp"]:
        return ["error", "expired"]
    if "nbf" in payload and now < payload["nbf"]:
        return ["error", "not yet valid"]
    return ["ok", payload]
''', 'token.split(".") must give 3 parts. Catch ValueError (json and base64 errors are both ValueError). Compare jwt_mac(key, head + "." + body) with the third part using hmac.compare_digest. exp and nbf are optional claims.', '<p>PyJWT checks the same things in the same spirit, and the token from sign_jwt is accepted by jwt.decode(token, "k3y", algorithms=["HS256"]). The order matters: the signature is checked before any claim is trusted, and the algorithm is chosen by the server, never by the token.</p>')
K.assign('corsgate', 'h', 'Write the CORS rules a server applies',
         '<p>Finish <code>origin_allowed</code> and <code>cors_answer(config, request)</code>. An origin is allowed when it is in the list, when the list has "*", or when a rule such as "https://*.preview.example.com" matches a subdomain (not preview.example.com itself). A <b>preflight</b> is OPTIONS with an Access-Control-Request-Method header: refuse it with [400, "origin"], [400, "method"] or [400, "headers"], or answer with Allow-Methods (the config list joined by ", "), Allow-Headers (the requested names, lower case and sorted, only when some were asked) and Max-Age. Every allowed answer has Allow-Origin: "*" only when the list has "*" and credentials is False, otherwise the origin itself plus Vary: Origin. Add Allow-Credentials: "true" when credentials is True. A normal request from an origin that is not allowed gets [200, &#123;&#125;]. Header names in the request can be in any case.</p>',
         r'''
def origin_allowed(origin, allowed):
    """Exact match, "*" for any site, or "https://*.example.com" for its subdomains (not example.com itself)."""
    # TODO: add the "*" rule and the "scheme://*.domain" rule
    return origin in allowed


def cors_answer(config, request):
    headers = {k.lower(): v for k, v in request["headers"].items()}
    origin = headers.get("origin")
    if origin is None:
        return [200, {}]
    # TODO: handle a preflight (OPTIONS with Access-Control-Request-Method): check the origin, the method and
    # every requested header, and add Allow-Methods, Allow-Headers and Max-Age. Handle "*" with and without
    # credentials. Add Vary: Origin whenever the answer depends on the origin.
    if not origin_allowed(origin, config["origins"]):
        return [200, {}]
    return [200, {"Access-Control-Allow-Origin": origin}]


SHOP = {"origins": ["https://shop.example.com", "https://*.preview.example.com"], "methods": ["GET", "POST"],
        "headers": ["Authorization", "Content-Type"], "credentials": True, "max_age": 600}
OPEN_DATA = {"origins": ["*"], "methods": ["GET"], "headers": [], "credentials": False, "max_age": 86400}
''', [('cors_answer(SHOP, {"method": "GET", "headers": {}})', [200, {}]), ('cors_answer(SHOP, {"method": "GET", "headers": {"Origin": "https://shop.example.com"}})', [200, {'Access-Control-Allow-Origin': 'https://shop.example.com', 'Vary': 'Origin', 'Access-Control-Allow-Credentials': 'true'}]), ('cors_answer(SHOP, {"method": "GET", "headers": {"Origin": "https://evil.example"}})', [200, {}]), ('cors_answer(SHOP, {"method": "OPTIONS", "headers": {"Origin": "https://pr-7.preview.example.com", "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "Content-Type, authorization"}})', [200, {'Access-Control-Allow-Origin': 'https://pr-7.preview.example.com', 'Vary': 'Origin', 'Access-Control-Allow-Credentials': 'true', 'Access-Control-Allow-Methods': 'GET, POST', 'Access-Control-Allow-Headers': 'authorization, content-type', 'Access-Control-Max-Age': '600'}]), ('cors_answer(SHOP, {"method": "OPTIONS", "headers": {"Origin": "https://preview.example.com", "Access-Control-Request-Method": "GET"}})', [400, 'origin']), ('cors_answer(SHOP, {"method": "OPTIONS", "headers": {"Origin": "https://shop.example.com", "Access-Control-Request-Method": "DELETE"}})', [400, 'method']), ('cors_answer(SHOP, {"method": "OPTIONS", "headers": {"Origin": "https://shop.example.com", "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "X-Debug"}})', [400, 'headers']), ('cors_answer(OPEN_DATA, {"method": "GET", "headers": {"origin": "https://anyone.example"}})', [200, {'Access-Control-Allow-Origin': '*'}]), ('cors_answer(OPEN_DATA, {"method": "OPTIONS", "headers": {"origin": "https://anyone.example", "access-control-request-method": "get"}})', [200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET', 'Access-Control-Max-Age': '86400'}])],
         r'''
def origin_allowed(origin, allowed):
    """Exact match, "*" for any site, or "https://*.example.com" for its subdomains (not example.com itself)."""
    for rule in allowed:
        if rule == "*" or rule == origin:
            return True
        if "://*." in rule:
            scheme, rest = rule.split("://*.", 1)
            prefix = scheme + "://"
            if origin.startswith(prefix) and origin.endswith("." + rest):
                label = origin[len(prefix):-len(rest) - 1]
                if all(part and part.replace("-", "").isalnum() for part in label.split(".")):
                    return True
    return False


def cors_answer(config, request):
    headers = {k.lower(): v for k, v in request["headers"].items()}
    origin = headers.get("origin")
    if origin is None:
        return [200, {}]
    ok = origin_allowed(origin, config["origins"])
    preflight = request["method"] == "OPTIONS" and "access-control-request-method" in headers
    if preflight:
        if not ok:
            return [400, "origin"]
        if headers["access-control-request-method"].upper() not in config["methods"]:
            return [400, "method"]
        asked = sorted(h.strip().lower() for h in headers.get("access-control-request-headers", "").split(",") if h.strip())
        allowed_headers = {h.lower() for h in config["headers"]}
        if any(h not in allowed_headers for h in asked):
            return [400, "headers"]
    if not ok:
        return [200, {}]
    answer = {}
    if "*" in config["origins"] and not config["credentials"]:
        answer["Access-Control-Allow-Origin"] = "*"
    else:
        answer["Access-Control-Allow-Origin"] = origin
        answer["Vary"] = "Origin"
    if config["credentials"]:
        answer["Access-Control-Allow-Credentials"] = "true"
    if preflight:
        answer["Access-Control-Allow-Methods"] = ", ".join(config["methods"])
        if asked:
            answer["Access-Control-Allow-Headers"] = ", ".join(asked)
        answer["Access-Control-Max-Age"] = str(config["max_age"])
    return [200, answer]


SHOP = {"origins": ["https://shop.example.com", "https://*.preview.example.com"], "methods": ["GET", "POST"],
        "headers": ["Authorization", "Content-Type"], "credentials": True, "max_age": 600}
OPEN_DATA = {"origins": ["*"], "methods": ["GET"], "headers": [], "credentials": False, "max_age": 86400}
''', 'Split the rule at "://*." into the scheme and the domain. The origin must start with the scheme and "://" and end with "." plus the domain, with at least one label in between. For the requested headers split on commas, strip and lower case them.', '<p>Starlette&#39;s CORSMiddleware, used in the lesson, follows the same steps. The rule about "*" and credentials comes from the Fetch standard: a browser refuses Allow-Origin: * on a request with cookies, so a server has to echo the exact origin, and Vary: Origin stops a cache from serving one site&#39;s answer to another.</p>')

K.must('Passwords', 'hashlib.pbkdf2_hmac("sha256", pw, salt, 600_000) or Argon2id. Random salt per user, stored as algorithm$rounds$salt$hash. hmac.compare_digest. secrets.token_urlsafe(32), never random. Keys from os.environ, never in git.')
K.must('JWT', 'header.payload.signature in base64url, HS256 = HMAC-SHA256. Readable by anyone. jwt.encode(claims, key, algorithm="HS256"). jwt.decode(token, key, algorithms=["HS256"], audience=..., issuer=...). Claims sub, exp, iat, nbf, aud, iss, jti. Short access, rotated refresh, kid for keys.')
K.must('FastAPI auth', 'OAuth2PasswordBearer(tokenUrl="token", scopes=...), OAuth2PasswordRequestForm, Security(current_user, scopes=[...]). 401 with WWW-Authenticate: Bearer, 403 for missing scope, 404 for another user&#39;s object.')
K.must('Browser rules', 'CORSMiddleware(allow_origins=[exact list], allow_credentials=True, allow_methods, allow_headers). Preflight OPTIONS. Never * with credentials. CSRF: SameSite cookies and CSRF tokens. Headers: HSTS, nosniff, Content-Security-Policy.')
K.must('OWASP API Top 10', 'API1 object level checks, API2 authentication, API3 property level (mass assignment, extra="forbid"), API4 resource limits, API5 function level, API7 SSRF. ? placeholders against injection. Rate limits with 429 and Retry-After.')

T = K.topic(
    slug='py-api-security', topic='py-api-security', step=(6, 'Securing APIs and the web revision exam', 'py-w6', 'Protect what you built: passwords, tokens, OAuth 2.0, CORS and the OWASP API Top 10, then test the whole web section in one exam.', 'Advanced'),
    title='API security: passwords, JWT, OAuth 2.0, CORS and OWASP', short='API security', badge='6.1', minutes=120,
    lead='Secure a Python API. Store passwords with slow salted hashes, build and check JWTs by hand and with PyJWT, protect FastAPI endpoints with OAuth 2.0 scopes and owner checks, set CORS and security headers, and close the holes on the OWASP API Top 10.',
    desc='Authentication and authorization, sessions, JWTs, API keys and OAuth 2.0 compared, password hashing with salts, PBKDF2, scrypt and Argon2id, hmac.compare_digest and the secrets module, JWT structure, HS256 and RS256, claims, expiry, alg none and alg pinning, PyJWT with audience, issuer, refresh token rotation and key rotation with kid, OAuth 2.0 flows with PKCE, FastAPI OAuth2PasswordBearer and scopes, 401 versus 403, object level checks, CORS with preflight, CSRF and SameSite cookies, security headers, the OWASP API Security Top 10 2023 with SQL injection, mass assignment and SSRF, rate limits, HTTPS, logging and secrets in production, and the maths of entropy, guessing, hashing cost and token buckets.',
    summary='Password hashing, JWTs by hand and with PyJWT, OAuth 2.0 scopes in FastAPI, CORS and CSRF, and the OWASP API Top 10.',
    keywords=['API security', 'JWT', 'PyJWT', 'OAuth 2.0', 'password hashing', 'PBKDF2', 'CORS', 'CSRF', 'OWASP', 'rate limiting'],
    recap='<p>Store passwords as slow salted hashes, sign short lived tokens and pin their algorithm, check the scope and the owner on every endpoint, and let only listed origins read your answers in a browser.</p>',
    added='2026-11-08', leet=leet_items())
