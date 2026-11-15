# 2.1 Authentication: passwords, MFA, passkeys and single sign on
# Example "jwt_check" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# JSON Web Tokens (RFC 7519): how they are signed and the checks a server must never skip
import base64
import hashlib
import hmac
import json

SECRET = b"server-side secret, 32+ random bytes in real life"

def b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def unb64(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))

def make(claims):
    header = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body = b64(json.dumps(claims).encode())
    sig = b64(hmac.new(SECRET, f"{header}.{body}".encode(), hashlib.sha256).digest())
    return f"{header}.{body}.{sig}"

def verify(token, now):
    try:
        header, body, sig = token.split(".")
    except ValueError:
        return "rejected: not three parts"
    if json.loads(unb64(header)).get("alg") != "HS256":
        return "rejected: unexpected algorithm"         # never let the token choose, e.g. "none"
    good = b64(hmac.new(SECRET, f"{header}.{body}".encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(sig, good):
        return "rejected: bad signature"
    claims = json.loads(unb64(body))
    if claims["exp"] < now:
        return "rejected: expired"
    return f"accepted: user {claims['sub']}, role {claims['role']}"

now = 1_700_000_000
token = make({"sub": "asha", "role": "user", "exp": now + 900})
print("token:", token[:40], "...")
print("payload is only encoded, anyone can read it:", unb64(token.split(".")[1]).decode())
print("valid token:   ", verify(token, now))
h, b, s = token.split(".")
admin = b64(json.dumps({"sub": "asha", "role": "admin", "exp": now + 900}).encode())
print("role changed:  ", verify(f"{h}.{admin}.{s}", now))
none_header = b64(json.dumps({"alg": "none", "typ": "JWT"}).encode())
print("alg none trick:", verify(f"{none_header}.{admin}.", now))
print("after 15 min:  ", verify(token, now + 901))
