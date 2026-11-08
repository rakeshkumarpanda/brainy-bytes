# 6.1 API security: passwords, JWT, OAuth 2.0, CORS and OWASP
# Example "owasp_demo" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
print("   limit=1000000 -> at most 100 rows, here", len(list_users(1_000_000)))
