# 2.4 Elliptic curve cryptography: ECDH, X25519, ECDSA and Ed25519
# Example "ecdsa_toy" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# ECDSA on secp256k1 written out in full, and how one reused nonce gives away the private key
import hashlib
import secrets

p = 2 ** 256 - 2 ** 32 - 977
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = 3 * x1 * x1 * pow(2 * y1, -1, p) % p        # a = 0 on this curve
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)

def multiply(k, P):
    R = None
    for bit in bin(k)[2:]:
        R = add(R, R)
        if bit == "1":
            R = add(R, P)
    return R

def h(message):
    return int.from_bytes(hashlib.sha256(message).digest(), "big")

def sign(d, message, k=None):
    if k is None:
        k = secrets.randbelow(n - 1) + 1   # the nonce: secret, random, NEVER reused
    r = multiply(k, G)[0] % n
    s = pow(k, -1, n) * (h(message) + r * d) % n
    return r, s

def verify(Q, message, r, s):
    if not (0 < r < n and 0 < s < n):
        return False
    w = pow(s, -1, n)
    X = add(multiply(h(message) * w % n, G), multiply(r * w % n, Q))
    return X is not None and X[0] % n == r

d = secrets.randbelow(n - 1) + 1           # private key
Q = multiply(d, G)                         # public key
r, s = sign(d, b"send 1 BTC to Asha")
print("valid:", verify(Q, b"send 1 BTC to Asha", r, s))
print("changed message valid:", verify(Q, b"send 9 BTC to Asha", r, s))

# The PlayStation 3 mistake: the same k for two messages
k = secrets.randbelow(n - 1) + 1
m1, m2 = b"game update 1.0", b"game update 2.0"
r1, s1 = sign(d, m1, k)
r2, s2 = sign(d, m2, k)
print("same r in both signatures:", r1 == r2)
k_found = (h(m1) - h(m2)) * pow(s1 - s2, -1, n) % n
d_found = (s1 * k_found - h(m1)) * pow(r1, -1, n) % n
print("private key recovered:", d_found == d)
