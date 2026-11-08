# 6.1 API security: passwords, JWT, OAuth 2.0, CORS and OWASP
# Model solutions. Try practice.py first.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: Store passwords like Django
# Finish three functions. make_hash(password, salt, iterations) returns
# "pbkdf2_sha256$ITERATIONS$SALT$HASH", where HASH is the base64 text of
# hashlib.pbkdf2_hmac("sha256", ...). verify_hash(password, stored) returns True only when the
# password matches, compares with hmac.compare_digest and returns False for a string in any other
# format. needs_upgrade(stored, iterations) returns True when the stored hash used fewer rounds than
# the current setting. The tests use only 1,000 rounds so they run fast.
# Why it works: This is exactly the string Django stores in auth_user.password, so your verify_hash
# can check real Django hashes. needs_upgrade is how Django raises the rounds over the years: it
# re-hashes at the next successful login, the only moment the password is known.

import base64
import hashlib
import hmac


def make_hash(password, salt, iterations):
    """Return "pbkdf2_sha256$ITERATIONS$SALT$HASH" with the hash in base64, like Django."""
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${base64.b64encode(digest).decode()}"


def verify_hash(password, stored):
    """True when the password matches the stored string. Compare in constant time."""
    parts = stored.split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return False
    _, iterations, salt, _ = parts
    return hmac.compare_digest(make_hash(password, salt, int(iterations)), stored)


def needs_upgrade(stored, iterations):
    """True when the stored hash used fewer rounds than the current setting."""
    return int(stored.split("$")[1]) < iterations


# ================================================================== task 2: Sign and check JWTs by hand
# sign_jwt and the helpers are ready. Finish verify_jwt(token, key, now). Return ["error",
# "malformed"] when the token does not have three parts or a part is not valid base64url JSON,
# ["error", "algorithm"] when the header alg is not HS256, ["error", "signature"] when the HMAC does
# not match, ["error", "expired"] when now >= exp, ["error", "not yet valid"] when now < nbf, and
# otherwise ["ok", payload]. Check in exactly that order.
# Why it works: PyJWT checks the same things in the same spirit, and the token from sign_jwt is
# accepted by jwt.decode(token, "k3y", algorithms=["HS256"]). The order matters: the signature is
# checked before any claim is trusted, and the algorithm is chosen by the server, never by the
# token.

import base64
import hashlib
import hmac
import json


def jwt_part(data):
    """dict -> compact JSON -> base64url without = padding."""
    raw = json.dumps(data, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def jwt_unpart(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def jwt_mac(key, signing_input):
    digest = hmac.new(key.encode(), signing_input.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def sign_jwt(payload, key):
    head = jwt_part({"alg": "HS256", "typ": "JWT"})
    body = jwt_part(payload)
    return f"{head}.{body}.{jwt_mac(key, head + '.' + body)}"


def verify_jwt(token, key, now):
    parts = token.split(".")
    if len(parts) != 3:
        return ["error", "malformed"]
    head, body, sig = parts
    try:
        header = json.loads(jwt_unpart(head))
        payload = json.loads(jwt_unpart(body))
    except ValueError:
        return ["error", "malformed"]
    if header.get("alg") != "HS256":
        return ["error", "algorithm"]
    if not hmac.compare_digest(jwt_mac(key, head + "." + body), sig):
        return ["error", "signature"]
    if "exp" in payload and now >= payload["exp"]:
        return ["error", "expired"]
    if "nbf" in payload and now < payload["nbf"]:
        return ["error", "not yet valid"]
    return ["ok", payload]


# ================================================================== task 3: Write the CORS rules a server applies
# Finish origin_allowed and cors_answer(config, request). An origin is allowed when it is in the
# list, when the list has "*", or when a rule such as "https://*.preview.example.com" matches a
# subdomain (not preview.example.com itself). A preflight is OPTIONS with an
# Access-Control-Request-Method header: refuse it with [400, "origin"], [400, "method"] or [400,
# "headers"], or answer with Allow-Methods (the config list joined by ", "), Allow-Headers (the
# requested names, lower case and sorted, only when some were asked) and Max-Age. Every allowed
# answer has Allow-Origin: "*" only when the list has "*" and credentials is False, otherwise the
# origin itself plus Vary: Origin. Add Allow-Credentials: "true" when credentials is True. A normal
# request from an origin that is not allowed gets [200, {}]. Header names in the request can be in
# any case.
# Why it works: Starlette's CORSMiddleware, used in the lesson, follows the same steps. The rule
# about "*" and credentials comes from the Fetch standard: a browser refuses Allow-Origin: * on a
# request with cookies, so a server has to echo the exact origin, and Vary: Origin stops a cache
# from serving one site's answer to another.

def origin_allowed(origin, allowed):
    """Exact match, "*" for any site, or "https://*.example.com" for its subdomains (not example.com itself)."""
    for rule in allowed:
        if rule == "*" or rule == origin:
            return True
        if "://*." in rule:
            scheme, rest = rule.split("://*.", 1)
            prefix = scheme + "://"
            if origin.startswith(prefix) and origin.endswith("." + rest):
                label = origin[len(prefix):-len(rest) - 1]
                if all(part and part.replace("-", "").isalnum() for part in label.split(".")):
                    return True
    return False


def cors_answer(config, request):
    headers = {k.lower(): v for k, v in request["headers"].items()}
    origin = headers.get("origin")
    if origin is None:
        return [200, {}]
    ok = origin_allowed(origin, config["origins"])
    preflight = request["method"] == "OPTIONS" and "access-control-request-method" in headers
    if preflight:
        if not ok:
            return [400, "origin"]
        if headers["access-control-request-method"].upper() not in config["methods"]:
            return [400, "method"]
        asked = sorted(h.strip().lower() for h in headers.get("access-control-request-headers", "").split(",") if h.strip())
        allowed_headers = {h.lower() for h in config["headers"]}
        if any(h not in allowed_headers for h in asked):
            return [400, "headers"]
    if not ok:
        return [200, {}]
    answer = {}
    if "*" in config["origins"] and not config["credentials"]:
        answer["Access-Control-Allow-Origin"] = "*"
    else:
        answer["Access-Control-Allow-Origin"] = origin
        answer["Vary"] = "Origin"
    if config["credentials"]:
        answer["Access-Control-Allow-Credentials"] = "true"
    if preflight:
        answer["Access-Control-Allow-Methods"] = ", ".join(config["methods"])
        if asked:
            answer["Access-Control-Allow-Headers"] = ", ".join(asked)
        answer["Access-Control-Max-Age"] = str(config["max_age"])
    return [200, answer]


SHOP = {"origins": ["https://shop.example.com", "https://*.preview.example.com"], "methods": ["GET", "POST"],
        "headers": ["Authorization", "Content-Type"], "credentials": True, "max_age": 600}
OPEN_DATA = {"origins": ["*"], "methods": ["GET"], "headers": [], "credentials": False, "max_age": 86400}


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Store passwords like Django", [('make_hash("sunshine", "Qx81LmZ0", 1000)', 'pbkdf2_sha256$1000$Qx81LmZ0$573A5bEvMdabWwPELFbyXnHJdyLkqV5TIjWKk4Xm3/0='), ('make_hash("sunshine", "pW2nB7tR", 1000) != make_hash("sunshine", "Qx81LmZ0", 1000)', True), ('verify_hash("sunshine", make_hash("sunshine", "Qx81LmZ0", 1000))', True), ('verify_hash("Sunshine", make_hash("sunshine", "Qx81LmZ0", 1000))', False), ('verify_hash("sunshine", "md5$abc$def")', False), ('[needs_upgrade(make_hash("a", "s", 1000), 2000), needs_upgrade(make_hash("a", "s", 2000), 2000)]', [True, False])]))
    results.append(check("Task 2: Sign and check JWTs by hand", [('sign_jwt({"sub": "ann", "exp": 1800000900}, "k3y")', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbm4iLCJleHAiOjE4MDAwMDA5MDB9.NZgcMYFCwP1_uYAVTk0otA3VOXrSzJzB0cNoR1hLs5Q'), ('verify_jwt(sign_jwt({"sub": "ann", "exp": 1800000900}, "k3y"), "k3y", 1800000000)', ['ok', {'sub': 'ann', 'exp': 1800000900}]), ('verify_jwt(sign_jwt({"sub": "ann", "exp": 1800000900}, "k3y"), "other", 1800000000)', ['error', 'signature']), ('verify_jwt(sign_jwt({"sub": "ann", "exp": 1800000900}, "k3y"), "k3y", 1800000900)', ['error', 'expired']), ('verify_jwt(sign_jwt({"sub": "ann", "nbf": 1800000100}, "k3y"), "k3y", 1800000000)', ['error', 'not yet valid']), ('verify_jwt(jwt_part({"alg": "none", "typ": "JWT"}) + "." + jwt_part({"sub": "root"}) + ".", "k3y", 0)', ['error', 'algorithm']), ('verify_jwt("only.two", "k3y", 0)', ['error', 'malformed']), ('verify_jwt(sign_jwt({"sub": "ann", "role": "user"}, "k3y").replace(jwt_part({"sub": "ann", "role": "user"}), jwt_part({"sub": "ann", "role": "admin"})), "k3y", 0)', ['error', 'signature'])]))
    results.append(check("Task 3: Write the CORS rules a server applies", [('cors_answer(SHOP, {"method": "GET", "headers": {}})', [200, {}]), ('cors_answer(SHOP, {"method": "GET", "headers": {"Origin": "https://shop.example.com"}})', [200, {'Access-Control-Allow-Origin': 'https://shop.example.com', 'Vary': 'Origin', 'Access-Control-Allow-Credentials': 'true'}]), ('cors_answer(SHOP, {"method": "GET", "headers": {"Origin": "https://evil.example"}})', [200, {}]), ('cors_answer(SHOP, {"method": "OPTIONS", "headers": {"Origin": "https://pr-7.preview.example.com", "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "Content-Type, authorization"}})', [200, {'Access-Control-Allow-Origin': 'https://pr-7.preview.example.com', 'Vary': 'Origin', 'Access-Control-Allow-Credentials': 'true', 'Access-Control-Allow-Methods': 'GET, POST', 'Access-Control-Allow-Headers': 'authorization, content-type', 'Access-Control-Max-Age': '600'}]), ('cors_answer(SHOP, {"method": "OPTIONS", "headers": {"Origin": "https://preview.example.com", "Access-Control-Request-Method": "GET"}})', [400, 'origin']), ('cors_answer(SHOP, {"method": "OPTIONS", "headers": {"Origin": "https://shop.example.com", "Access-Control-Request-Method": "DELETE"}})', [400, 'method']), ('cors_answer(SHOP, {"method": "OPTIONS", "headers": {"Origin": "https://shop.example.com", "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "X-Debug"}})', [400, 'headers']), ('cors_answer(OPEN_DATA, {"method": "GET", "headers": {"origin": "https://anyone.example"}})', [200, {'Access-Control-Allow-Origin': '*'}]), ('cors_answer(OPEN_DATA, {"method": "OPTIONS", "headers": {"origin": "https://anyone.example", "access-control-request-method": "get"}})', [200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET', 'Access-Control-Max-Age': '86400'}])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
