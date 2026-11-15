# 1.1 The web: sessions, origins, tokens and the OWASP Top 10
# Practice tasks. Fill in each function, then run this file.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.


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


# ================================================================== task 1: The origin of a URL
# Write url_origin(url) that returns the origin as a string "scheme://host:port". Use
# urllib.parse.urlsplit, and fill in the default port 80 for http and 443 for https when none is
# given.
# Hint: urlsplit gives scheme, hostname and port. port is None when not written.

from urllib.parse import urlsplit

def url_origin(url):
    # your code here
    pass


# ================================================================== task 2: Is this session cookie safe?
# Write cookie_ok(header) for a Set-Cookie header value. Return True only if it has the Secure flag,
# the HttpOnly flag, and SameSite set to Lax or Strict. Attribute names and values are case
# insensitive.
# Hint: Skip the first part (the name and value), then build a dictionary of lower case attributes.

def cookie_ok(header):
    # your code here
    pass


# ================================================================== task 3: Verify an HS256 JWT
# Write verify_hs256(token, key). Split the token into header, payload and signature. Return False
# unless the header’s alg is exactly "HS256" and HMAC-SHA-256(key, header + "." + payload),
# base64url encoded without padding, equals the signature (compare with hmac.compare_digest).
# Otherwise return the payload’s sub claim.
# Hint: Decode the header to check alg, sign the first two parts as text, and compare base64url
# strings.

import base64, hashlib, hmac, json

def verify_hs256(token, key):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: The origin of a URL", [('url_origin("https://shop.example.com/cart")', 'https://shop.example.com:443'), ('url_origin("http://shop.example.com/x?y=1")', 'http://shop.example.com:80'), ('url_origin("https://api.example.com:8443/v1")', 'https://api.example.com:8443'), ('url_origin("https://shop.example.com:443/") == url_origin("https://shop.example.com/a")', True)]))
    results.append(check("Task 2: Is this session cookie safe?", [('cookie_ok("sid=1; Path=/; Secure; HttpOnly; SameSite=Lax")', True), ('cookie_ok("sid=1; Path=/")', False), ('cookie_ok("sid=1; secure; httponly; samesite=strict")', True), ('cookie_ok("sid=1; Secure; HttpOnly; SameSite=None")', False), ('cookie_ok("sid=1; Secure; SameSite=Lax")', False)]))
    results.append(check("Task 3: Verify an HS256 JWT", [('verify_hs256("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJib2IiLCJleHAiOjIwMDAwMDAwMDB9.zIp874XFP9-SZ04qEY7htT9HnTaRl6-uz4-tcnL8Eus", b"k3y-for-tests-0123456789abcdefgh")', 'bob'), ('verify_hs256("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MjAwMDAwMDAwMH0.zIp874XFP9-SZ04qEY7htT9HnTaRl6-uz4-tcnL8Eus", b"k3y-for-tests-0123456789abcdefgh")', False), ('verify_hs256("eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJib2IiLCJleHAiOjIwMDAwMDAwMDB9.", b"k3y-for-tests-0123456789abcdefgh")', False), ('verify_hs256("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJib2IiLCJleHAiOjIwMDAwMDAwMDB9.zIp874XFP9-SZ04qEY7htT9HnTaRl6-uz4-tcnL8Eus", b"wrong-key")', False)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
