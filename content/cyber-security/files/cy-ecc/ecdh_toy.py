# 2.4 Elliptic curve cryptography: ECDH, X25519, ECDSA and Ed25519
# Example "ecdh_toy" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# ECDH: Diffie-Hellman with points. First on the toy curve, then on secp256k1 (Bitcoin's curve).
import secrets

def add(P, Q, p, a):                       # works on any curve y^2 = x^3 + ax + b mod p
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None                        # the point at infinity
    if P == Q:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)

def multiply(k, P, p, a):                  # double and add
    R = None
    for bit in bin(k)[2:]:
        R = add(R, R, p, a)
        if bit == "1":
            R = add(R, P, p, a)
    return R

# Toy curve y^2 = x^3 + 2x + 2 mod 17, G = (5, 1) of order 19
G = (5, 1)
alice, bob = 3, 10
A = multiply(alice, G, 17, 2)
B = multiply(bob, G, 17, 2)
print("toy: A =", A, " B =", B, " Alice gets", multiply(alice, B, 17, 2), " Bob gets", multiply(bob, A, 17, 2))

# secp256k1: y^2 = x^3 + 7
p = 2 ** 256 - 2 ** 32 - 977
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141     # prime order of G
print("G on the curve:", (G[1] ** 2 - G[0] ** 3 - 7) % p == 0, "| n*G = infinity:", multiply(n, G, p, 0) is None)

a_secret = secrets.randbelow(n - 1) + 1
b_secret = secrets.randbelow(n - 1) + 1
A = multiply(a_secret, G, p, 0)
B = multiply(b_secret, G, p, 0)
print("256 bit ECDH, same shared point:", multiply(a_secret, B, p, 0) == multiply(b_secret, A, p, 0))
print("a public key is 33 bytes (compressed). RSA needs 384 bytes for the same 128 bit strength.")
