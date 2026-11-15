# 1.1 The web: sessions, origins, tokens and the OWASP Top 10
# Example "cookie_audit" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Audit Set-Cookie headers: session cookies need Secure, HttpOnly and SameSite
def parse_set_cookie(header):
    parts = [p.strip() for p in header.split(";")]
    name, value = parts[0].split("=", 1)
    attrs = {}
    for p in parts[1:]:
        key, _, val = p.partition("=")
        attrs[key.lower()] = val or True
    return name, value, attrs

def audit(header):
    name, value, a = parse_set_cookie(header)
    problems = []
    if "secure" not in a:
        problems.append("no Secure: can be sent over plain HTTP and sniffed")
    if "httponly" not in a:
        problems.append("no HttpOnly: JavaScript (and so XSS) can read it")
    same = str(a.get("samesite", "")).lower()
    if same not in ("lax", "strict"):
        problems.append("SameSite missing or None: sent on cross site requests (CSRF risk)")
    if name.startswith("__Host-") and ("domain" in a or a.get("path") != "/"):
        problems.append("__Host- prefix needs Path=/ and no Domain")
    return name, problems

headers = [
    "session=8f3a91c2; Path=/",
    "session=8f3a91c2; Path=/; Secure; HttpOnly; SameSite=Lax",
    "__Host-sid=77ab; Path=/; Secure; HttpOnly; SameSite=Strict",
    "sid=91ce; Path=/; Secure; SameSite=None",
]
for h in headers:
    name, problems = audit(h)
    print(f"{name:11} {'OK' if not problems else str(len(problems)) + ' problem(s)'}")
    for p in problems:
        print("            -", p)
