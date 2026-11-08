# 6.1 API security: passwords, JWT, OAuth 2.0, CORS and OWASP
# Example "jwt_by_hand" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
print("   hmac.compare_digest always looks at every byte:", hmac.compare_digest(b"abc", b"abd"))
