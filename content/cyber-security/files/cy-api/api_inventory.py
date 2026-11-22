# 4.4 API security: BOLA, rate limits, mass assignment and the OWASP API Top 10
# Example "api_inventory" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Find shadow and zombie APIs: compare what the documentation says with what the gateway logs show
documented = {("GET", "/v2/orders/{id}"), ("POST", "/v2/orders"), ("GET", "/v2/users/me"),
              ("PATCH", "/v2/users/me")}
retired = {("GET", "/v1/orders/{id}")}          # old version, meant to be switched off

log = ["GET /v2/orders/1001", "GET /v1/orders/1002", "GET /v1/orders/1003", "POST /v2/orders",
       "GET /v2/users/me", "GET /internal/debug/config", "GET /v2/orders/1004", "PATCH /v2/users/me"]

def to_route(line):
    method, path = line.split()
    parts = ["{id}" if p.isdigit() else p for p in path.split("/")]
    return method, "/".join(parts)

seen = {}
for line in log:
    r = to_route(line)
    seen[r] = seen.get(r, 0) + 1

for route, n in sorted(seen.items()):
    kind = "documented" if route in documented else "ZOMBIE (retired but still answering)" if route in retired else "SHADOW (nobody documented it)"
    print(f"{route[0]:6s} {route[1]:28s} {n} calls  {kind}")
