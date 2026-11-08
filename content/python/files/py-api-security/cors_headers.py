# 6.1 API security: passwords, JWT, OAuth 2.0, CORS and OWASP
# Example "cors_headers" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
    print(f"   {name}: {r.headers[name]}")
