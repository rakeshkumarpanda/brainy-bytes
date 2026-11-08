# 6.1 API security: passwords, JWT, OAuth 2.0, CORS and OWASP
# Example "pyjwt_tokens" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
    print("   after k1 is removed:", err)
