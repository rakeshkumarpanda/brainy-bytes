# 6.2 Web revision exam: HTTP, Flask, Django, FastAPI and security
# Example "paper_d" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import base64
import hashlib
import hmac
import ipaddress
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal

import jwt
from pydantic import BaseModel, Field, ValidationError


class Item(BaseModel):
    name: str
    qty: int = 1
    size: Literal["S", "M", "L"] = "M"
    tags: list[str] = []


print("Q1", Item(name="tea", qty="3").qty, Item(name="tea").tags is Item(name="cake").tags)
try:
    Item(name="tea", qty="3.5", size="XL")
except ValidationError as err:
    print("Q2", err.error_count(), [e["loc"][0] for e in err.errors()])


class Address(BaseModel):
    city: str
    zip_code: str = Field(pattern=r"^\d{5}$")


class Order(BaseModel):
    id: int
    ship_to: Address
    note: str | None = None


try:
    Order(id=1, ship_to={"city": "Bonn", "zip_code": "5311"})
except ValidationError as err:
    print("Q3", err.errors()[0]["loc"])
o = Order(id=1, ship_to={"city": "Bonn", "zip_code": "53111"})
print("Q4", o.model_dump(exclude_none=True), o.model_dump_json(include={"id"}))

KEY = "k" * 32
token = jwt.encode({"sub": "ann", "aud": "shop", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}, KEY, algorithm="HS256")
print("Q5", token[:3], token.count("."), base64.urlsafe_b64encode(b'{"a').decode())
for kwargs in [{}, {"algorithms": ["HS256"]}, {"algorithms": ["HS256"], "audience": "shop"}]:
    try:
        jwt.decode(token, KEY, **kwargs)
        print("Q6", "ok")
    except jwt.InvalidTokenError as err:
        print("Q6", type(err).__name__)

digest = hashlib.pbkdf2_hmac("sha256", b"pw", b"salt", 1000)
print("Q7", len(digest), len(digest.hex()), len(secrets.token_hex(16)), len(secrets.token_urlsafe(16)))
print("Q8", hmac.compare_digest("abc", "abc"), hmac.new(b"k", b"msg", "sha256").hexdigest() == hmac.new(b"k", b"msg", "sha256").hexdigest())
print("Q9", [ipaddress.ip_address(a).is_private for a in ["10.1.2.3", "172.32.0.1", "192.168.0.9", "8.8.8.8", "::1"]])
print("Q10", hashlib.sha256(b"a").hexdigest() == hashlib.sha256(b"a").hexdigest(),
      hashlib.pbkdf2_hmac("sha256", b"a", b"s1", 10) == hashlib.pbkdf2_hmac("sha256", b"a", b"s2", 10))
