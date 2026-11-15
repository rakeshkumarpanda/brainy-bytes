# 1.1 The web: sessions, origins, tokens and the OWASP Top 10
# Example "same_origin" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# The same origin policy: two URLs share an origin only if scheme, host and port all match
from urllib.parse import urlsplit

DEFAULT_PORT = {"http": 80, "https": 443}

def origin(url):
    u = urlsplit(url)
    return (u.scheme, u.hostname, u.port or DEFAULT_PORT[u.scheme])

def same_origin(a, b):
    return origin(a) == origin(b)

page = "https://shop.example.com/cart"
tests = [
    "https://shop.example.com/account?id=7",   # same scheme, host, port
    "http://shop.example.com/cart",            # scheme differs
    "https://api.example.com/cart",            # host differs (subdomain)
    "https://shop.example.com:8443/cart",      # port differs
    "https://shop.example.com:443/help",       # explicit default port: same
    "https://shop.example.com.evil.io/cart",   # looks similar, different host
]
print("page origin:", origin(page))
for t in tests:
    o = origin(t)
    why = "same origin" if o == origin(page) else "different " + ", ".join(
        name for name, x, y in zip(("scheme", "host", "port"), o, origin(page)) if x != y)
    print(f"{t:42} {why}")
