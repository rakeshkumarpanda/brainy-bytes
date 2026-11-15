# 1.1 Certificates, PKI and TLS 1.3
# Example "chain_verify" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# How a browser checks a certificate chain, with toy RSA keys and certificates as dictionaries
import hashlib
from datetime import date

def make_key(p, q, e=65537):
    n = p * q
    return {"n": n, "e": e, "d": pow(e, -1, (p - 1) * (q - 1))}

def digest(cert, n):
    text = repr(sorted((k, v) for k, v in cert.items() if k != "sig"))
    return int.from_bytes(hashlib.sha256(text.encode()).digest(), "big") % n

def sign(cert, issuer_key):
    cert["sig"] = pow(digest(cert, issuer_key["n"]), issuer_key["d"], issuer_key["n"])

root_key = make_key(1000000007, 998244353)              # toy primes, far too small for real use
mid_key = make_key(1000000009, 999999937)
site_key = make_key(1000000021, 999999929)

root = {"subject": "Toy Root CA", "issuer": "Toy Root CA", "ca": True, "key": (root_key["n"], 65537),
        "from": date(2020, 1, 1), "to": date(2035, 1, 1)}
mid = {"subject": "Toy Issuing CA", "issuer": "Toy Root CA", "ca": True, "key": (mid_key["n"], 65537),
       "from": date(2024, 1, 1), "to": date(2029, 1, 1)}
leaf = {"subject": "shop.example", "issuer": "Toy Issuing CA", "ca": False, "key": (site_key["n"], 65537),
        "names": ["shop.example", "www.shop.example"], "from": date(2026, 9, 1), "to": date(2026, 11, 30)}
sign(root, root_key)                                     # a root signs itself
sign(mid, root_key)
sign(leaf, mid_key)

trusted = {"Toy Root CA": root}                          # the browser's root store
revoked = set()

def check(chain, host, today):
    for cert, issuer in zip(chain, chain[1:] + [None]):
        issuer = issuer or trusted.get(cert["issuer"])
        if issuer is None:
            return "unknown issuer: " + cert["issuer"]
        n, e = issuer["key"]
        if pow(cert["sig"], e, n) != digest(cert, n):
            return "bad signature on " + cert["subject"]
        if not (cert["from"] <= today <= cert["to"]):
            return "expired or not yet valid: " + cert["subject"]
        if cert is not chain[0] and not cert["ca"]:
            return cert["subject"] + " is not allowed to issue certificates"
        if cert["subject"] in revoked:
            return "revoked: " + cert["subject"]
    if host not in chain[0]["names"]:
        return "name mismatch: certificate is not for " + host
    return "OK, chain trusted"

today = date(2026, 11, 14)
print("1.", check([leaf, mid], "shop.example", today))
print("2.", check([leaf, mid], "bank.example", today))
print("3.", check([leaf, mid], "shop.example", date(2026, 12, 25)))
leaf["names"].append("bank.example")                     # tampering breaks the signature
print("4.", check([leaf, mid], "bank.example", today))
leaf["names"].remove("bank.example")
revoked.add("shop.example")
print("5.", check([leaf, mid], "shop.example", today))
