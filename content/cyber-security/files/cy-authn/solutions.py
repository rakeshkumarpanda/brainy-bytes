# 2.1 Authentication: passwords, MFA, passkeys and single sign on
# Model solutions. Try practice.py first.
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


# ================================================================== task 1: Online guessing odds
# Write guess_odds(tries, digits) that returns the chance of guessing a random numeric code of the
# given length within the number of tries: tries / 10digits, but never more than 1.
# Why it works: Lockouts turn a tiny 4 digit space into a strong control. Offline, the same space
# falls in microseconds.

def guess_odds(tries, digits):
    return min(1, tries / 10 ** digits)


# ================================================================== task 2: HOTP from RFC 4226
# Write hotp(secret, counter, digits). secret is a text string. Compute HMAC-SHA-1 of the counter as
# 8 big endian bytes, take offset = last byte & 0x0F, read 4 bytes from there as a big endian
# number, clear the top bit (& 0x7FFFFFFF), take the remainder mod 10digits, and return it as a
# string padded with zeros.
# Why it works: These are the RFC 4226 test values. TOTP is the same function with counter = Unix
# time // 30.

import hashlib
import hmac
import struct

def hotp(secret, counter, digits):
    mac = hmac.new(secret.encode(), struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = mac[-1] & 0x0F
    code = int.from_bytes(mac[offset:offset + 4], "big") & 0x7FFFFFFF
    return str(code % 10 ** digits).zfill(digits)


# ================================================================== task 3: A safe JWT verifier
# Write jwt_verify(token, secret, now) for HS256 tokens. Split into header, payload and signature.
# Return None if the header’s alg is not "HS256", if the base64url HMAC-SHA-256 of "header.payload"
# with secret (text) does not equal the signature (use hmac.compare_digest), or if the payload’s exp
# is less than now. Otherwise return the payload’s sub.
# Why it works: The four tests are a valid token, an expired one, one signed with a different key,
# and an alg none forgery. Real verifiers also check iss, aud and nbf.

import base64
import hashlib
import hmac
import json

def b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def unb64(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))

def jwt_verify(token, secret, now):
    header, payload, sig = token.split(".")
    if json.loads(unb64(header)).get("alg") != "HS256":
        return None
    good = b64(hmac.new(secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(sig, good):
        return None
    claims = json.loads(unb64(payload))
    if claims["exp"] < now:
        return None
    return claims["sub"]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Online guessing odds", [('guess_odds(10, 6)', 1e-05), ('guess_odds(3, 4)', 0.0003), ('guess_odds(2000, 3)', 1)]))
    results.append(check("Task 2: HOTP from RFC 4226", [('hotp("12345678901234567890", 0, 6)', '755224'), ('hotp("12345678901234567890", 1, 6)', '287082'), ('hotp("12345678901234567890", 9, 6)', '520489')]))
    results.append(check("Task 3: A safe JWT verifier", [('jwt_verify("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhc2hhIiwiZXhwIjoyMDAwfQ.5bD7oiqVcBUVub0e5wzgVySQX-Ssuo2FG6iyXMKsOg4", "k3y", 1500)', 'asha'), ('jwt_verify("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyYXZpIiwiZXhwIjoxMDAwfQ.DdSAkRRs5h6rdcwu7AG77uA5vM-L9RkEeQHE9hPtb1Y", "k3y", 1500)', None), ('jwt_verify("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhc2hhIiwiZXhwIjoyMDAwfQ.sYpIBzuiHElL370LtCS2tMuKywvLyzYL6XCeLC4h2R4", "k3y", 1500)', None), ('jwt_verify("eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJldmUiLCJleHAiOjIwMDB9.", "k3y", 1500)', None)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
