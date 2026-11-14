# 1.1 Certificates, PKI and TLS 1.3
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


# ================================================================== task 1: Days until a certificate expires
# Write days_left(not_after, today) where both are strings like "2026-11-30". Return the number of
# days from today to not_after (negative if already expired). Use datetime.date.fromisoformat.
# Why it works: Monitoring tools run exactly this check every day and alert when fewer than about 20
# days remain, so automated renewal failures are noticed in time.

from datetime import date

def days_left(not_after, today):
    end = date.fromisoformat(not_after)
    now = date.fromisoformat(today)
    return (end - now).days


# ================================================================== task 2: Host name matching with wildcards
# Write name_matches(host, names) that returns True if host matches any entry in names. Matching
# ignores case. A wildcard entry like "*.shop.example" matches exactly one extra label on the left:
# a.shop.example yes, shop.example no, a.b.shop.example no.
# Why it works: RFC 6125 and the CA/Browser Forum rules allow the wildcard only as the whole left
# most label, which is what this check enforces.

def name_matches(host, names):
    host = host.lower()
    for name in names:
        name = name.lower()
        if name == host:
            return True
        if name.startswith("*."):
            rest = name[2:]
            if host.endswith("." + rest) and "." not in host[:-len(rest) - 1]:
                return True
    return False


# ================================================================== task 3: A Certificate Transparency Merkle root
# Write ct_root(entries) for a list of byte strings. Hash leaves as SHA-256(0x00 + entry), inner
# nodes as SHA-256(0x01 + left + right), and split a list of size n at the largest power of two
# below n (RFC 6962). Return the root as a hex string.
# Why it works: Splitting at the largest power of two below n keeps the tree append only: adding
# entries never changes the shape of the part already built.

import hashlib

def ct_root(entries):
    def tree(items):
        if len(items) == 1:
            return hashlib.sha256(b"\x00" + items[0]).digest()
        k = 1
        while k * 2 < len(items):
            k = k * 2
        return hashlib.sha256(b"\x01" + tree(items[:k]) + tree(items[k:])).digest()
    return tree(entries).hex()


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Days until a certificate expires", [('days_left("2026-11-30", "2026-11-14")', 16), ('days_left("2026-10-30", "2026-11-14")', -15), ('days_left("2027-02-12", "2026-11-14")', 90)]))
    results.append(check("Task 2: Host name matching with wildcards", [('name_matches("shop.example", ["shop.example"])', True), ('name_matches("WWW.Shop.Example", ["*.shop.example"])', True), ('name_matches("shop.example", ["*.shop.example"])', False), ('name_matches("a.b.shop.example", ["*.shop.example"])', False), ('name_matches("bank.example", ["shop.example", "*.shop.example"])', False)]))
    results.append(check("Task 3: A Certificate Transparency Merkle root", [('ct_root([b"a"])', '022a6979e6dab7aa5ae4c3e5e45f7e977112a7e63593820dbec1ec738a24f93c'), ('ct_root([b"a", b"b"])', 'b137985ff484fb600db93107c77b0365c80d78f5b429ded0fd97361d077999eb'), ('len(ct_root([b"x"] * 7))', 64)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
