# 1.1 The web: sessions, origins, tokens and the OWASP Top 10
# Example "jwt_hs256" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# JSON Web Tokens signed with HMAC-SHA-256, built from scratch, and the classic "alg": "none" trick
import base64, hashlib, hmac, json

def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def b64url_decode(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))

def sign(payload, key):
    header = {"alg": "HS256", "typ": "JWT"}
    h = b64url(json.dumps(header, separators=(",", ":")).encode())
    p = b64url(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(key, f"{h}.{p}".encode(), hashlib.sha256).digest()
    return f"{h}.{p}.{b64url(sig)}"

def verify(token, key, now):
    h, p, s = token.split(".")
    header = json.loads(b64url_decode(h))
    if header.get("alg") != "HS256":                     # never let the token choose the algorithm
        return False, "rejected: algorithm " + str(header.get("alg"))
    good = hmac.new(key, f"{h}.{p}".encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(good, b64url_decode(s)):  # constant time comparison
        return False, "rejected: bad signature"
    payload = json.loads(b64url_decode(p))
    if payload["exp"] < now:
        return False, "rejected: expired"
    return True, payload

KEY = b"server-secret-key-32-bytes-long!"
NOW = 1_700_000_000
token = sign({"sub": "alice", "role": "user", "exp": NOW + 900}, KEY)
print("token:", token[:60] + "...")
print("valid token:      ", verify(token, KEY, NOW))

h, p, s = token.split(".")
evil_p = b64url(json.dumps({"sub": "alice", "role": "admin", "exp": NOW + 900}, separators=(",", ":")).encode())
print("edited payload:   ", verify(f"{h}.{evil_p}.{s}", KEY, NOW))

none_h = b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode())
print("alg none, no sig: ", verify(f"{none_h}.{evil_p}.", KEY, NOW))
print("after 15 minutes: ", verify(token, KEY, NOW + 901))
print("payload is only encoded, not encrypted:", json.loads(b64url_decode(p)))
