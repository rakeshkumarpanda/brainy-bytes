# Cryptography 2.4: elliptic curve cryptography. Checked against Hankerson, Menezes and Vanstone, Guide to Elliptic
# Curve Cryptography, Washington, Elliptic Curves (2nd edition), Paar and Pelzl, Understanding Cryptography (the toy curve
# y^2 = x^3 + 2x + 2 mod 17), SEC 2 (secp256k1), FIPS 186-5, RFC 6979, RFC 7748 and RFC 8032 (test vectors checked with
# the cryptography package), Biehl, Meyer and Mueller (2000), and Bernstein and Lange, SafeCurves.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-ecc')
K = Kit()

K.code('ec_points', r'''
# The points of a small elliptic curve y^2 = x^3 + 2x + 2 over the field of 17 elements
p, a, b = 17, 2, 2
print("discriminant 4a^3 + 27b^2 mod p =", (4 * a ** 3 + 27 * b ** 2) % p, "(must not be 0)")

points = []
for x in range(p):
    right = (x ** 3 + a * x + b) % p
    for y in range(p):
        if (y * y) % p == right:
            points.append((x, y))
print("points:", points)
print("count with the point at infinity:", len(points) + 1)

# Hasse's theorem: |#E - (p + 1)| <= 2 sqrt(p)
count = len(points) + 1
print("Hasse bound:", p + 1, "+/-", round(2 * p ** 0.5, 2), "| holds:", abs(count - (p + 1)) <= 2 * p ** 0.5)

# Fast count with Euler's criterion: right side is a square when right^((p-1)/2) = 1
fast = 1                                   # the point at infinity
for x in range(p):
    right = (x ** 3 + a * x + b) % p
    if right == 0:
        fast = fast + 1
    elif pow(right, (p - 1) // 2, p) == 1:
        fast = fast + 2                    # y and -y
print("count by Euler's criterion:", fast)
''', long=True)

K.code('ec_arith', r'''
# Point addition, doubling and scalar multiplication on y^2 = x^3 + 2x + 2 mod 17
p, a, b = 17, 2, 2
O = None                                   # the point at infinity, the "zero" of the group

def on_curve(P):
    if P is O:
        return True
    x, y = P
    return (y * y - (x ** 3 + a * x + b)) % p == 0

def add(P, Q):
    if P is O:
        return Q
    if Q is O:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return O                           # P + (-P) = O
    if P == Q:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p   # slope of the tangent
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p          # slope of the chord
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def multiply(k, P):                        # double and add, reading k from the top bit
    R = O
    for bit in bin(k)[2:]:
        R = add(R, R)
        if bit == "1":
            R = add(R, P)
    return R

G = (5, 1)
print("G on curve:", on_curve(G))
print("G + G =", add(G, G), " (5,1) + (6,3) =", add(G, (6, 3)))

row = []
for k in range(1, 20):
    row.append(multiply(k, G))
print("kG for k = 1..19:", row)
print("19G is the point at infinity, so G has order 19:", multiply(19, G) is O)
print("associative check (G + 2G) + 3G == G + (2G + 3G):",
      add(add(G, multiply(2, G)), multiply(3, G)) == add(G, add(multiply(2, G), multiply(3, G))))
print("13G =", multiply(13, G), "and 13 mod 19 shows the cycle: 32G =", multiply(32, G))
''', long=True)

K.code('ecdh_toy', r'''
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
''', long=True)

K.code('ec_compress', r'''
# Point compression: store x and one bit for y, then rebuild y with a modular square root
p = 2 ** 256 - 2 ** 32 - 977               # secp256k1. p mod 4 = 3, so square roots are one power
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
print("p mod 4 =", p % 4)

def compress(P):
    x, y = P
    prefix = b"\x03" if y % 2 == 1 else b"\x02"      # 02 for even y, 03 for odd y
    return prefix + x.to_bytes(32, "big")

def decompress(data):
    x = int.from_bytes(data[1:], "big")
    right = (x ** 3 + 7) % p
    y = pow(right, (p + 1) // 4, p)        # a square root of right, because p = 3 mod 4
    if y * y % p != right:
        raise ValueError("x is not on the curve")
    if y % 2 != data[0] % 2:
        y = p - y                          # pick the root with the right parity
    return (x, y)

c = compress(G)
print("compressed G:", c.hex()[:20] + "...", len(c), "bytes instead of 65")
print("rebuilt correctly:", decompress(c) == G)
try:
    decompress(b"\x02" + (5).to_bytes(32, "big"))
except ValueError as error:
    print("x = 5:", error)
''')

K.code('ecdsa_toy', r'''
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
''', long=True)

K.code('ec_invalid', r'''
# Invalid curve attack: a server that skips the "is this point on my curve?" check leaks its secret
p, a, b = 17, 2, 2                         # the real curve y^2 = x^3 + 2x + 2, G = (5, 1) of order 19

def add(P, Q):                             # note: the formulas never use b
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)

def multiply(k, P):
    R = None
    for i in range(k):
        R = add(R, P)
    return R

def order(P):
    k, R = 1, P
    while R is not None:
        R = add(R, P)
        k = k + 1
    return k

def on_curve(P):
    x, y = P
    return (y * y - x ** 3 - a * x - b) % p == 0

server_secret = 13                         # the attacker does not know this

def careless_server(P):                    # returns d * P without checking P
    return multiply(server_secret, P)

# The attacker searches other curves y^2 = x^3 + 2x + b2 for points of small order
found = {}
for b2 in range(p):
    for x in range(p):
        for y in range(p):
            if (y * y - x ** 3 - a * x - b2) % p == 0 and b2 != b:
                r = order((x, y))
                if r in (2, 3, 5) and r not in found:
                    found[r] = (x, y)
print("small order points on other curves:", found)

remainders = {}
for r, P in found.items():
    reply = careless_server(P)
    for k in range(r):                     # only r possibilities, try them all
        if multiply(k, P) == reply:
            remainders[r] = k
print("secret mod 2, 3, 5:", remainders)

x = next(v for v in range(30) if all(v % r == k for r, k in remainders.items()))
print("CRT gives the secret mod 30:", x, "| real secret:", server_secret)
print("the fix, checking the point first: on_curve =", [on_curve(P) for P in found.values()])
''', long=True)

K.code('x25519_ed25519', r'''
# X25519 key exchange and Ed25519 signatures, checked against the RFC test vectors (pip install cryptography)
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

raw = serialization.Encoding.Raw
pub_raw = serialization.PublicFormat.Raw

# RFC 7748, section 6.1
alice = X25519PrivateKey.from_private_bytes(bytes.fromhex("77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a"))
bob_public = X25519PublicKey.from_public_bytes(bytes.fromhex("de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f"))
print("Alice's public key matches RFC 7748:",
      alice.public_key().public_bytes(raw, pub_raw).hex() == "8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a")
shared = alice.exchange(bob_public)
print("shared secret matches RFC 7748:", shared.hex() == "4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742")

# Fresh keys, the normal way
a, b = X25519PrivateKey.generate(), X25519PrivateKey.generate()
print("fresh X25519 exchange agrees:", a.exchange(b.public_key()) == b.exchange(a.public_key()), "| key size: 32 bytes")

# RFC 8032, Ed25519 test 1 (empty message)
signer = Ed25519PrivateKey.from_private_bytes(bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"))
signature = signer.sign(b"")
print("Ed25519 signature matches RFC 8032:", signature.hex().startswith("e5564300c360ac72") and signature.hex().endswith("438e7a100b"))
print("signing twice gives the same signature (deterministic nonce):", signer.sign(b"") == signature)

key = Ed25519PrivateKey.generate()
sig = key.sign(b"firmware v3.1")
key.public_key().verify(sig, b"firmware v3.1")
print("verified,", len(sig), "byte signature")
try:
    key.public_key().verify(sig, b"firmware v3.2")
except InvalidSignature:
    print("changed firmware rejected")
''')

K.lesson('idea', 'Why elliptic curves', f'''
{talk('In 1985, Neal Koblitz at the University of Washington and Victor Miller at IBM independently suggested a new home for the discrete logarithm problem: the points of an elliptic curve over a finite field. Elliptic curves had been studied by mathematicians for more than a century, and they were at the heart of Andrew Wiles’s proof of Fermat’s Last Theorem in 1995. What made them attractive for cryptography is that the clever sub exponential attacks that work modulo a prime, index calculus and the number field sieve, do not work on well chosen curves. The best known attack is the generic one, Pollard’s rho, which takes about the square root of the group size. So a 256 bit curve gives about 128 bits of security, which needs a 3072 bit RSA key. Smaller keys mean faster handshakes, smaller certificates and less power on phones and smart cards. Adoption was slow at first because of patents and caution, but the NSA endorsed elliptic curves in its Suite B in 2005, Bitcoin chose the curve secp256k1 in 2009, and today X25519 and ECDSA or Ed25519 protect most TLS connections, SSH logins and messaging apps.')}
{src('Koblitz, Elliptic Curve Cryptosystems (1987), Miller, Use of Elliptic Curves in Cryptography (CRYPTO 1985), Hankerson, Menezes and Vanstone, Guide to Elliptic Curve Cryptography, Washington, Elliptic Curves: Number Theory and Cryptography, SEC 2, FIPS 186-5, RFC 6979, RFC 7748, RFC 8032, Bernstein and Lange, SafeCurves.')}
{wwh('<b>Elliptic curve cryptography</b> (ECC) does Diffie-Hellman, signatures and encryption in the group of points of an elliptic curve over a finite field, where the <b>elliptic curve discrete log problem</b> (ECDLP) is hard.',
     'It gives the same security as RSA or finite field Diffie-Hellman with keys about 12 times smaller and much faster private key operations.',
     'Points are added with simple formulas. A private key is a number d, the public key is the point Q = dG. Finding d from Q is the ECDLP, which takes about &radic;n steps for a group of size n.')}
{table(['Security level', 'Symmetric key', 'RSA or DH modulus', 'Elliptic curve'], [
    ['112 bits', '3DES (retired)', '2048 bits', '224 bits'],
    ['128 bits', 'AES-128', '3072 bits', '256 bits (P-256, Curve25519, secp256k1)'],
    ['192 bits', 'AES-192', '7680 bits', '384 bits (P-384)'],
    ['256 bits', 'AES-256', '15360 bits', '512 or 521 bits (P-521)']])}
''', kw=['elliptic curve cryptography', 'ECC', 'Koblitz', 'Miller', 'ECDLP', 'key size', 'Suite B', 'secp256k1', 'Curve25519'])

K.lesson('curves', 'Elliptic curves over a finite field', f'''
{talk('An elliptic curve, despite the name, has nothing to do with ellipses. The name comes from elliptic integrals, which mathematicians used to measure the length of an ellipse in the 1800s. For cryptography, a curve is the set of solutions of an equation of the form y squared equals x cubed plus a x plus b, called the short Weierstrass form after Karl Weierstrass. Over the real numbers it is a smooth curve, symmetric about the x axis. The condition that 4 a cubed plus 27 b squared is not zero makes sure it has no sharp point or self crossing. In cryptography we take x and y modulo a prime p, so the curve becomes a finite set of grid points. One extra point, called the point at infinity and written O, is added, and it will play the role of zero. How many points are there? Helmut Hasse proved in 1933 that the count is always close to p plus 1, within two times the square root of p. Counting exactly for a 256 bit prime is not done by trying every x, of course. René Schoof found a polynomial time algorithm in 1985, and that is how the sizes of standard curves were certified.')}
{wwh('An <b>elliptic curve</b> over F<sub>p</sub> is the set of (x, y) with y<sup>2</sup> &equiv; x<sup>3</sup> + ax + b (mod p), together with the <b>point at infinity</b> O, where 4a<sup>3</sup> + 27b<sup>2</sup> &#8802; 0 (mod p).',
     'These points, with the addition rule of the next lesson, form a group whose discrete log problem is hard. Standard curves fix p, a, b, a base point G and its order n.',
     'For each x, compute the right side and check if it is a square mod p (Euler’s criterion). Each square gives two points (x, y) and (x, p &minus; y), and a zero gives one.')}
{viz('cycurve')}
{run('ec_points')}
{fxs(fx('Short Weierstrass form', 'E: y<sup>2</sup> = x<sup>3</sup> + ax + b, with 4a<sup>3</sup> + 27b<sup>2</sup> &ne; 0', 'Toy curve: a = 2, b = 2, p = 17, discriminant term 4 &middot; 8 + 27 &middot; 4 = 140 &equiv; 4.', key=True),
     fx('Hasse’s theorem', '|#E(F<sub>p</sub>) &minus; (p + 1)| &le; 2&radic;p', 'p = 17: between 18 &minus; 8.25 and 18 + 8.25, and the toy curve has 19.', key=True),
     fx('Cofactor', '#E = h &middot; n, with n the prime order of G', 'P-256 and secp256k1 have h = 1. Curve25519 has h = 8, which needs care.'))}
{table(['Curve', 'Equation and field', 'Where it is used'], [
    ['P-256 (secp256r1)', 'y<sup>2</sup> = x<sup>3</sup> &minus; 3x + b, p = 2<sup>256</sup> &minus; 2<sup>224</sup> + 2<sup>192</sup> + 2<sup>96</sup> &minus; 1', 'TLS certificates, smart cards, passkeys (WebAuthn)'],
    ['secp256k1', 'y<sup>2</sup> = x<sup>3</sup> + 7, p = 2<sup>256</sup> &minus; 2<sup>32</sup> &minus; 977', 'Bitcoin, Ethereum'],
    ['Curve25519', 'y<sup>2</sup> = x<sup>3</sup> + 486662x<sup>2</sup> + x, p = 2<sup>255</sup> &minus; 19 (Montgomery form)', 'X25519 in TLS, SSH, Signal, WireGuard'],
    ['Edwards25519', 'the same curve in twisted Edwards form', 'Ed25519 signatures in SSH, Git, Tor']])}
''', kw=['elliptic curve', 'Weierstrass', 'finite field', 'point at infinity', 'Hasse theorem', 'Schoof', 'cofactor', 'P-256', 'secp256k1', 'Curve25519'])

K.lesson('add', 'Adding points: the group law', f'''
{talk('The magic of elliptic curves is that you can add two points and get a third point on the same curve. Over the real numbers the rule is geometric. Draw the straight line through P and Q. Because the equation is cubic, the line meets the curve in exactly one more point. Reflect that point across the x axis, and the result is P plus Q. To double a point, use the tangent line instead. If the line is vertical, it meets the curve at the point at infinity, so P plus its mirror image is O, which is why O acts as zero. The geometry turns into short formulas for the slope lambda and the new coordinates, and the same formulas work modulo p, where division means multiplying by an inverse. The hardest fact to prove is that this addition is associative, meaning that P plus Q, then plus R, equals P plus the sum of Q and R. A direct proof by algebra fills pages, and a clean proof uses deeper geometry. The program checks it on examples.')}
{viz('cyecadd')}
{run('ec_arith')}
{fxs(fx('Chord (P &ne; Q)', '&lambda; = (y<sub>2</sub> &minus; y<sub>1</sub>) / (x<sub>2</sub> &minus; x<sub>1</sub>) mod p', '(5, 1) + (6, 3): &lambda; = 2 / 1 = 2.', key=True),
     fx('Tangent (P = Q)', '&lambda; = (3x<sub>1</sub><sup>2</sup> + a) / (2y<sub>1</sub>) mod p', '2 &middot; (5, 1): &lambda; = 77 &middot; 2<sup>&minus;1</sup> &equiv; 9 &middot; 9 = 81 &equiv; 13 (mod 17).', key=True),
     fx('New point', 'x<sub>3</sub> = &lambda;<sup>2</sup> &minus; x<sub>1</sub> &minus; x<sub>2</sub>, y<sub>3</sub> = &lambda;(x<sub>1</sub> &minus; x<sub>3</sub>) &minus; y<sub>1</sub>', '(5, 1) + (6, 3) = (10, 6). 2 &middot; (5, 1) = (6, 3).', key=True),
     fx('Group rules', 'P + O = P, P + (&minus;P) = O with &minus;(x, y) = (x, &minus;y), P + Q = Q + P, (P + Q) + R = P + (Q + R)', 'The points form an abelian group. On the toy curve it has 19 elements, so it is cyclic and every point except O generates it.'))}
{steps('Worked example: 2G for G = (5, 1) on y<sup>2</sup> = x<sup>3</sup> + 2x + 2 mod 17', [
    'Tangent slope: 3 &middot; 5<sup>2</sup> + 2 = 77 &equiv; 9 (mod 17).',
    '2y<sub>1</sub> = 2, and 2<sup>&minus;1</sup> mod 17 = 9 because 2 &times; 9 = 18 &equiv; 1.',
    '&lambda; = 9 &times; 9 = 81 &equiv; 13.',
    'x<sub>3</sub> = 13<sup>2</sup> &minus; 5 &minus; 5 = 159 &equiv; 6.',
    'y<sub>3</sub> = 13 &times; (5 &minus; 6) &minus; 1 = &minus;14 &equiv; 3. So 2G = (6, 3).'])}
''', kw=['point addition', 'point doubling', 'chord and tangent', 'group law', 'slope lambda', 'associativity', 'abelian group'])

K.lesson('scalar', 'Scalar multiplication and the ECDLP', f'''
{talk('Adding G to itself k times gives the point k G, called scalar multiplication. Done naively, k G for a 256 bit k would need an impossible number of additions. Instead we use double and add, the same idea as square and multiply: read k in binary, double at every bit and add G when the bit is 1. That is about 256 doublings and 128 additions. Going backwards, from the point k G to the number k, is the elliptic curve discrete logarithm problem. On a good curve, nobody knows anything better than Pollard’s rho, which needs about the square root of the group order, so about 2 to the 128 steps for a 256 bit curve. The largest prime field ECDLP solved in public was 112 bits, in 2009, using a cluster of 200 PlayStation 3 consoles. The animation shows how the multiples of G jump around the curve in a pattern that looks random. Real code must also be careful about time: a double and add loop that does extra work on 1 bits leaks the secret, so libraries use the Montgomery ladder or other constant time methods.')}
{wwh('<b>Scalar multiplication</b>: kG = G + G + ... + G (k times). The <b>ECDLP</b>: given G and Q = kG, find k.',
     'A private key is a random k from 1 to n &minus; 1 and the public key is Q = kG. ECDH and ECDSA are secure only while the ECDLP is hard.',
     'Double and add: R = O, then for each bit of k from the top, R = 2R, and if the bit is 1, R = R + G. Constant time code uses the Montgomery ladder, which does one doubling and one addition for every bit.')}
{viz('cyecdh')}
{run('ecdh_toy')}
{fxs(fx('Double and add cost', 'about log<sub>2</sub> k doublings and (log<sub>2</sub> k) / 2 additions', '256 bit k: about 256 doublings and 128 additions.', key=True),
     fx('Pollard rho on ECDLP', 'about &radic;(&pi;n / 4) group operations (using the &plusmn;P symmetry)', 'n &asymp; 2<sup>256</sup>: about 2<sup>128</sup>. This is why a 256 bit curve gives 128 bit security.', key=True),
     fx('ECDH', 'A = aG, B = bG, shared S = aB = bA = abG', 'Toy curve: a = 3, b = 10, S = 30G = 11G = (13, 10). Use the x coordinate of S, through HKDF.', key=True))}
{run('ec_compress')}
{note('A public key Q = (x, y) can be stored as 33 bytes: a prefix 02 or 03 for the parity of y, then x. The receiver rebuilds y with a square root mod p. This is the compressed format used by Bitcoin and TLS.', 'tip')}
''', kw=['scalar multiplication', 'double and add', 'ECDLP', 'Pollard rho', 'ECDH', 'Montgomery ladder', 'point compression', 'public key'])

K.lesson('x25519', 'X25519: Diffie-Hellman done safely', f'''
{talk('In 2006 Daniel J. Bernstein published Curve25519, designed from the start to be fast and hard to misuse. The prime 2 to the 255 minus 19 makes reduction quick on ordinary processors. The curve is written in Montgomery form, where Peter Montgomery’s ladder from 1987 computes k times a point using only x coordinates, the same number of steps for every key, so timing does not leak. Every 32 byte string is accepted as a public key, and the maths is arranged so that a bad or invalid point cannot leak the secret, which removes a whole class of bugs. Secret keys are clamped: three low bits are cleared so the key is a multiple of the cofactor 8, which neutralises small subgroup points, and the top bit is fixed so the ladder always runs the same length. The scheme is called X25519 and is defined in RFC 7748 from 2016. It is now the default key exchange in TLS 1.3, SSH, Signal and the WireGuard VPN. The program checks the library against the test vectors printed in the RFC.')}
{wwh('<b>X25519</b> is elliptic curve Diffie-Hellman on Curve25519 using only x coordinates. Keys and shared secrets are 32 bytes.',
     'It is fast, constant time by design, accepts any 32 byte public value safely, and avoids the invalid curve and timing bugs that hit many ECDH implementations.',
     'Clamp the 32 byte secret, run the Montgomery ladder on the received x coordinate, output the x coordinate of the result. Then feed the shared secret to HKDF.')}
{local('x25519_ed25519', 'It needs the cryptography package: python3 -m pip install cryptography.')}
{fxs(fx('Curve25519', 'y<sup>2</sup> = x<sup>3</sup> + 486662x<sup>2</sup> + x over F<sub>p</sub>, p = 2<sup>255</sup> &minus; 19', 'Order 8 &middot; &ell;, with &ell; = 2<sup>252</sup> + 27742317777372353535851937790883648493 prime.', key=True),
     fx('Clamping', 'k[0] &amp;= 248, k[31] &amp;= 127, k[31] |= 64', 'Clear the 3 low bits (multiple of the cofactor 8), clear bit 255, set bit 254.'))}
''', kw=['X25519', 'Curve25519', 'Bernstein', 'Montgomery ladder', 'clamping', 'cofactor', 'RFC 7748', 'WireGuard', 'TLS 1.3'])

K.lesson('ecdsa', 'ECDSA signatures and the nonce rule', f'''
{talk('ECDSA, the elliptic curve digital signature algorithm, became an ANSI standard in 1999 and a NIST standard in 2000. To sign, the signer picks a fresh secret random number k, called the nonce, computes the point k G and takes its x coordinate as r. Then s is k inverse times the hash plus r times the private key, all modulo the group order n. The signature is the pair r and s. Anyone can verify using the public key Q. The nonce is the weak spot. If the same k is used for two different messages, two lines of algebra recover the private key. In December 2010, the group fail0verflow showed that Sony had signed PlayStation 3 software with the same k every time, so they computed Sony’s master private key. In 2013 a flaw in Android’s random number generator caused repeated nonces in Bitcoin wallets, and coins were stolen. Even a few biased bits of k are enough for lattice attacks, as the Minerva and TPM-Fail studies showed in 2019. The fix, RFC 6979 by Thomas Pornin in 2013, derives k deterministically from the private key and the message hash, so a broken random generator can no longer leak the key.')}
{wwh('<b>ECDSA</b>: sign with nonce k: r = (kG).x mod n, s = k<sup>&minus;1</sup>(H(m) + r d) mod n. Verify: u<sub>1</sub> = H(m) s<sup>&minus;1</sup>, u<sub>2</sub> = r s<sup>&minus;1</sup>, accept if (u<sub>1</sub>G + u<sub>2</sub>Q).x mod n = r.',
     'It is the most widely deployed elliptic curve signature: TLS certificates, passkeys, Bitcoin before Taproot, code signing and smart cards.',
     'Correctness: u<sub>1</sub>G + u<sub>2</sub>Q = s<sup>&minus;1</sup>(H + r d)G = kG, so its x coordinate is r. The nonce k must be secret, uniform and never reused.')}
{run('ecdsa_toy')}
{fxs(fx('Sign', 'r = (kG)<sub>x</sub> mod n, s = k<sup>&minus;1</sup>(h + r d) mod n', 'Toy curve, n = 19, d = 7, h = 10, k = 3: r = 10, s = 13 &middot; 80 mod 19 = 14.', key=True),
     fx('Verify', 'w = s<sup>&minus;1</sup>, X = (h w)G + (r w)Q, accept if X<sub>x</sub> mod n = r', 'Uses only public values: G, Q, h, r, s.', key=True),
     fx('Nonce reuse', 'k = (h<sub>1</sub> &minus; h<sub>2</sub>) / (s<sub>1</sub> &minus; s<sub>2</sub>), d = (s<sub>1</sub>k &minus; h<sub>1</sub>) / r mod n', 'Same r in two signatures is the giveaway. Toy: k = 5 / 8 &equiv; 3, d = 32 / 10 &equiv; 7 (mod 19).', key=True),
     fx('Malleability', 'if (r, s) is valid, so is (r, n &minus; s)', 'Bitcoin requires the low s value to stop transaction ID changes.'))}
{note('Never write your own nonce generator. Use a library that implements RFC 6979 or the hedged variant, or use Ed25519, which is deterministic by design.', 'warn')}
''', kw=['ECDSA', 'nonce', 'nonce reuse', 'PlayStation 3', 'fail0verflow', 'RFC 6979', 'deterministic nonce', 'Minerva', 'TPM-Fail', 'lattice attack', 'signature malleability'])

K.lesson('eddsa', 'Schnorr signatures and Ed25519', f'''
{talk('Claus Schnorr designed a simpler and cleaner signature in 1989, with a neat security proof, but he patented it, and ECDSA was designed partly to avoid the patent. After the patent expired in 2008, Schnorr style signatures came back. Ed25519, published in 2011 by Daniel Bernstein, Niels Duif, Tanja Lange, Peter Schwabe and Bo-Yin Yang, is a Schnorr signature on the Edwards form of Curve25519. It fixes the nonce problem by design: the nonce is a hash of a secret prefix and the message, so the same message always gives the same signature and no random generator is needed. Twisted Edwards curves have one formula for all additions, including doubling, which makes constant time code easier. Ed25519 keys are 32 bytes and signatures 64 bytes. It is standardised in RFC 8032 and in FIPS 186-5, and used for SSH keys, Git commit signing, Tor and many other systems. Bitcoin added Schnorr signatures on secp256k1 in its Taproot upgrade in November 2021, partly because Schnorr signatures can be added together for multi signatures.')}
{wwh('A <b>Schnorr signature</b> is (R, s) with R = kG and s = k + H(R, Q, m) d. <b>Ed25519</b> is a Schnorr signature on Edwards25519 with k = H(prefix, m), so it is deterministic.',
     'It removes the nonce reuse disaster of ECDSA, is faster, has a simpler security proof, and supports aggregation for multi signatures.',
     'Verify by checking sG = R + H(R, Q, m) Q. If k were reused for two messages, the same algebra as ECDSA would expose d, so the deterministic nonce matters.')}
{fxs(fx('Schnorr', 'R = kG, e = H(R &#8214; Q &#8214; m), s = k + e d mod n, verify sG = R + eQ', 'Linear in d, which makes proofs and multi signatures simple.', key=True),
     fx('Ed25519 nonce', 'r = H(prefix &#8214; m) mod &ell;', 'prefix is the second half of SHA-512 of the secret seed. Same message, same signature.', key=True))}
{table(['Feature', 'ECDSA (P-256)', 'Ed25519'], [
    ['Nonce', 'Random, or RFC 6979 deterministic', 'Deterministic by design'],
    ['Formula', 's = k<sup>&minus;1</sup>(h + rd), needs an inverse', 's = k + e d, no inverse'],
    ['Public key, signature', '33 or 65 bytes, about 70 bytes (DER)', '32 bytes, 64 bytes'],
    ['Malleability', '(r, n &minus; s) also valid', 'Strict checks make it non malleable'],
    ['Standard', 'FIPS 186-5, X9.62', 'RFC 8032, FIPS 186-5']])}
''', kw=['Schnorr signature', 'Ed25519', 'EdDSA', 'twisted Edwards', 'RFC 8032', 'deterministic', 'Taproot', 'multi signature', 'patent'])

K.lesson('attacks', 'Attacks on careless ECC and on curve choice', f'''
{talk('The mathematics of good curves has held up for forty years, but implementations and curve choices have failed many times. The invalid curve attack, described by Ingrid Biehl, Bernd Meyer and Volker Müller in 2000, uses a quiet fact: the addition formulas never use the constant b. If a server multiplies a received point by its secret without checking that the point is on the curve, an attacker can send points from other curves that have small order, learn the secret modulo many small numbers, and join the pieces with the Chinese remainder theorem. In 2015 researchers showed this against real TLS libraries. Some curves are weak by structure: supersingular curves allow the MOV attack, which moves the problem into a finite field, and curves with exactly p points allow an attack in linear time. Curve choice itself raised trust questions. NIST’s curves were generated from seeds whose origin was never explained, and the random number generator Dual EC DRBG, standardised in 2006, turned out to contain what was widely seen as an NSA backdoor, as reports from 2013 suggested. And in January 2020, Windows CryptoAPI was found to accept certificates with a custom curve generator, a bug called CurveBall, reported by the NSA itself.')}
{safe('The invalid curve demo runs on a toy curve inside the program. Testing a real server for this flaw needs the owner’s written permission.')}
{run('ec_invalid')}
{attack([
    ['Sends a point from another curve with small order (invalid curve attack)', 'Check the point is on the curve and not O, or use X25519'],
    ['Sends a small order point on a curve with a cofactor', 'Multiply by the cofactor or clamp the key, check the result is not O'],
    ['Collects two ECDSA signatures with the same nonce', 'RFC 6979 deterministic nonces, or Ed25519'],
    ['Measures timing or power during scalar multiplication', 'Constant time ladder, blinding the scalar'],
    ['Pushes a weak or backdoored curve or generator', 'Use vetted curves (P-256, Curve25519) and fixed generators, check certificate curve parameters'],
    ['Records traffic for a future quantum computer', 'Hybrid key exchange with ML-KEM now']])}
{scene('Dual EC DRBG', '<p>In 2006 NIST published SP 800-90 with four random number generators. One, Dual EC DRBG, used two elliptic curve points P and Q. In 2007 Dan Shumow and Niels Ferguson of Microsoft showed that whoever knew a number e with P = eQ could predict all future output from a small sample. In 2013 documents leaked by Edward Snowden suggested the NSA had pushed the standard, and Reuters reported that RSA Security had been paid 10 million US dollars to make it the default in its BSAFE library. NIST withdrew the generator in 2014. The lesson for designers: constants in a standard should be explainable, and "nothing up my sleeve" numbers like the digits of &pi; are preferred.</p>')}
''', kw=['invalid curve attack', 'small subgroup', 'twist', 'MOV attack', 'anomalous curve', 'Dual EC DRBG', 'backdoor', 'CurveBall', 'CVE-2020-0601', 'SafeCurves', 'side channel'])

K.lesson('versus', 'Elliptic curves compared', f'''
{talk('With several curves and schemes in use, the choice comes down to the job and the rules you must follow. For key exchange, X25519 is the modern default. For signatures, Ed25519 is the easiest to use safely. P-256 with ECDSA is required where FIPS rules apply, and it is what most TLS certificates, smart cards and passkeys use. secp256k1 is mainly for cryptocurrencies. Ed448 and P-384 give more margin for long term keys. RSA is still needed to talk to older systems. None of these survive a large quantum computer. A 2017 estimate by Martin Roetteler and colleagues found that breaking P-256 with Shor’s algorithm would need about 2,300 logical qubits, fewer than RSA-2048, so the move to post quantum schemes covers elliptic curves too.')}
{versus('Picking a curve and scheme', ['', 'X25519', 'Ed25519', 'ECDSA P-256', 'secp256k1', 'RSA-3072'], [
    ['Job', 'Key exchange', 'Signatures', 'Signatures (and ECDH)', 'Signatures (Bitcoin)', 'Signatures and key transport'],
    ['Security', '128 bit', '128 bit', '128 bit', '128 bit', '128 bit'],
    ['Public key', '32 bytes', '32 bytes', '33 or 65 bytes', '33 bytes', '384 bytes'],
    ['Misuse risk', 'Low: any input is safe', 'Low: deterministic nonce', 'Nonce and point checks needed', 'Nonce and point checks needed', 'Padding needed'],
    ['Standards', 'RFC 7748, TLS 1.3', 'RFC 8032, FIPS 186-5', 'FIPS 186-5, X9.62', 'SEC 2', 'FIPS 186-5, PKCS #1'],
    ['Quantum safe', 'No', 'No', 'No', 'No', 'No']],
    'Use X25519 for key exchange and Ed25519 for signatures unless a rule requires P-256. Plan hybrids with ML-KEM and ML-DSA for the quantum transition.')}
''', kw=['comparison', 'X25519', 'Ed25519', 'P-256', 'secp256k1', 'Ed448', 'P-384', 'quantum', 'Roetteler'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('Elliptic curves reach from a picture you can sketch to research mathematics. A beginner learns that an elliptic curve key is a small number, the public key a point, and that the same security as RSA comes from much shorter keys. A college student can add and double points by hand, run double and add, compute ECDH and ECDSA on a toy curve, and recover a key from a reused nonce. A masters student studies the group structure and Hasse’s theorem, point counting with Schoof’s algorithm, the MOV, anomalous and invalid curve attacks, pairings, and coordinate systems such as projective and Edwards coordinates that make code fast and constant time. At the research level, people work on pairing based cryptography, used in some zero knowledge proof systems, lattice attacks on biased nonces, formally verified implementations such as those in the Fiat Cryptography project, and isogenies between curves as a source of post quantum schemes. The 2022 break of SIKE showed that this area still holds surprises.')}
{ladder(
    '<p>An elliptic curve key pair is a secret number and a public point. Turning the number into the point is fast. Going back is extremely hard, and keys are much shorter than RSA keys for the same safety.</p>',
    '<p>Check points, count points with Euler’s criterion, add and double with the chord and tangent formulas, multiply by double and add, run ECDH, sign and verify ECDSA on a toy curve, and recover a key from a reused nonce.</p>',
    '<p>Hasse’s theorem and Schoof’s algorithm, projective, Jacobian and Edwards coordinates, the Montgomery ladder, cofactors and clamping, MOV and anomalous curve attacks, invalid curve and twist attacks, Schnorr proofs in the random oracle model, and RFC 6979.</p>',
    '<p>Pairings (Weil and Tate) and pairing friendly curves (BLS12-381) for BLS signatures and zk-SNARKs, lattice (hidden number problem) attacks on biased nonces, verified implementations (Fiat Cryptography), Shor resource estimates for ECDLP, and isogeny based cryptography after the SIKE break.</p>')}
{grow('Explain that an ECC key is a number and a point, and why the keys are short.',
      'Compute point additions, ECDH and ECDSA by hand, and spot nonce and point validation mistakes.',
      'Analyse curve security, pairings, lattice nonce attacks and post quantum isogeny research.')}
''', kw=['beginner', 'expert', 'Schoof', 'projective coordinates', 'pairing', 'BLS12-381', 'hidden number problem', 'Fiat Cryptography', 'isogeny'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Curve</b>: y<sup>2</sup> = x<sup>3</sup> + ax + b over F<sub>p</sub> plus O, with 4a<sup>3</sup> + 27b<sup>2</sup> &ne; 0. Hasse: |#E &minus; (p + 1)| &le; 2&radic;p. Toy curve mod 17 has 19 points.',
    '<b>Addition</b>: chord slope (y<sub>2</sub> &minus; y<sub>1</sub>)/(x<sub>2</sub> &minus; x<sub>1</sub>), tangent slope (3x<sup>2</sup> + a)/(2y). x<sub>3</sub> = &lambda;<sup>2</sup> &minus; x<sub>1</sub> &minus; x<sub>2</sub>, y<sub>3</sub> = &lambda;(x<sub>1</sub> &minus; x<sub>3</sub>) &minus; y<sub>1</sub>.',
    '<b>Scalar multiplication</b> by double and add or the Montgomery ladder. <b>ECDLP</b>: best attack Pollard rho, about &radic;n, so 256 bit curves give 128 bit security.',
    '<b>ECDH</b>: S = aB = bA = abG. <b>X25519</b>: x only ladder, clamping, any input safe, RFC 7748.',
    '<b>ECDSA</b>: r = (kG)<sub>x</sub>, s = k<sup>&minus;1</sup>(h + rd). Reused k gives d (PS3, 2010). Use RFC 6979.',
    '<b>Ed25519</b>: Schnorr on Edwards25519 with a deterministic nonce, 32 byte keys, 64 byte signatures.',
    '<b>Attacks</b>: invalid curve points, small subgroups, biased nonces, side channels, weak or unexplained curves (Dual EC DRBG, CurveBall).',
    'All of RSA, DH and ECC fall to Shor’s algorithm. Hybrids with ML-KEM and ML-DSA are the way forward.'],
    'Step 3 of this section turns to applied cryptography: certificates, PKI and TLS 1.3, then post quantum standards, then secret sharing, zero knowledge and homomorphic encryption.')}
{files('Three tasks: count the points of a curve, add two points, and scalar multiplication by double and add.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Why are elliptic curve keys shorter than RSA keys for the same security?', ['Curves are newer', 'The best attack on good curves is generic (about &radic;n), with no sub exponential shortcut', 'They use AES inside', 'They are less secure'], 1, 'No number field sieve.', 'Index calculus and the NFS do not apply, so 256 bits give about 128 bit security.')
K.quiz('e', 'In ECC, the public key is', ['A prime number', 'A point Q = dG', 'The curve equation', 'A hash'], 1, 'Number times point.', 'The private key d is a number, and the public key is the point dG.')
K.quiz('e', 'What plays the role of zero for point addition?', ['(0, 0)', 'The point at infinity O', 'G', 'p'], 1, 'Vertical lines.', 'P + O = P, and P + (&minus;P) = O.')
K.quiz('e', 'What is &minus;P for P = (5, 1) on a curve mod 17?', ['(5, &minus;1) = (5, 16)', '(&minus;5, 1)', '(12, 16)', '(1, 5)'], 0, 'Mirror in the x axis.', '&minus;(x, y) = (x, &minus;y), and &minus;1 &equiv; 16 (mod 17).')
K.quiz('m', 'Which formula gives the slope for doubling a point?', ['(y<sub>2</sub> &minus; y<sub>1</sub>)/(x<sub>2</sub> &minus; x<sub>1</sub>)', '(3x<sup>2</sup> + a)/(2y)', 'x<sup>3</sup> + ax + b', '2y/x'], 1, 'Tangent.', 'Differentiate y<sup>2</sup> = x<sup>3</sup> + ax + b: 2y y&prime; = 3x<sup>2</sup> + a.')
K.quiz('m', 'Hasse’s theorem says the number of points on E over F<sub>p</sub> is', ['Exactly p', 'Within 2&radic;p of p + 1', 'Always prime', 'About p<sup>2</sup>'], 1, 'Close to p + 1.', '|#E &minus; (p + 1)| &le; 2&radic;p.')
K.quiz('m', 'Scalar multiplication kG for a 256 bit k uses', ['k additions', 'About 256 doublings and 128 additions (double and add)', 'One multiplication', 'A hash'], 1, 'Like square and multiply.', 'Double at each bit, add G on 1 bits.')
K.quiz('m', 'Why does X25519 clamp the secret key?', ['To make it shorter', 'To make it a multiple of the cofactor 8 and fix its top bit, defusing small subgroup points and timing differences', 'To encrypt it', 'For compression'], 1, 'Cofactor 8.', 'Clearing the 3 low bits kills small order components, and a fixed top bit gives a constant ladder length.')
K.quiz('m', 'What makes Ed25519 immune to the nonce reuse disaster of careless ECDSA?', ['Bigger keys', 'Its nonce is a hash of a secret prefix and the message', 'It has no nonce', 'It uses RSA'], 1, 'Deterministic.', 'The same message always gives the same nonce, and different messages give unrelated nonces.')
K.quiz('h', 'Two ECDSA signatures share the same r. What follows?', ['Nothing', 'The same nonce k was used, and the private key can be computed', 'The messages were equal', 'The curve is weak'], 1, 'r = (kG)<sub>x</sub>.', 'k = (h<sub>1</sub> &minus; h<sub>2</sub>)/(s<sub>1</sub> &minus; s<sub>2</sub>), then d = (s k &minus; h)/r mod n.')
K.quiz('h', 'The invalid curve attack works because', ['The curve is singular', 'The addition formulas do not use b, so points from other curves are processed without error', 'AES is weak', 'n is not prime'], 1, 'Check the point.', 'Points on other curves with small order leak the secret modulo small numbers.')
K.quiz('h', 'If (r, s) is a valid ECDSA signature, which other pair is also valid?', ['(s, r)', '(r, n &minus; s)', '(n &minus; r, s)', '(r, 2s)'], 1, 'Negate k.', 'Using &minus;k gives the point &minus;kG with the same x coordinate and s replaced by n &minus; s.')
K.quiz('h', 'What was Dual EC DRBG?', ['A curve for Bitcoin', 'A NIST random number generator whose constants allowed whoever knew a secret relation to predict its output', 'A signature scheme', 'A TLS cipher suite'], 1, 'P = eQ.', 'Shumow and Ferguson showed the trapdoor in 2007, and NIST withdrew it in 2014.')
K.quiz('x', 'In the style of a Berkeley CS 276 question: why do pairings make supersingular curves weak for ECDLP (the MOV attack)?', ['They do not', 'A pairing maps the ECDLP to a discrete log in a small extension field F<sub>p<sup>k</sup></sub>, where index calculus applies', 'They reveal the cofactor', 'They compress points'], 1, 'Embedding degree.', 'For supersingular curves the embedding degree k is at most 6 (at most 2 over prime fields with p &gt; 3), so the finite field log is sub exponential.')
K.quiz('x', 'In the style of a Stanford CS 255 exam: in ECDSA verification, why does u<sub>1</sub>G + u<sub>2</sub>Q equal kG?', ['It does not', 'u<sub>1</sub>G + u<sub>2</sub>Q = s<sup>&minus;1</sup>(h + r d)G and s<sup>&minus;1</sup>(h + rd) = k mod n', 'Because Q = G', 'Because r = s'], 1, 'Substitute Q = dG.', 's = k<sup>&minus;1</sup>(h + rd) so s<sup>&minus;1</sup>(h + rd) = k.')

K.calc('e', 'On y<sup>2</sup> = x<sup>3</sup> + 2x + 2 mod 17, compute the right side at x = 5.', '1', '125 + 10 + 2.', ['137 = 8 &times; 17 + 1.', 'So y<sup>2</sup> = 1, and y = 1 or 16.', eq('x<sup>3</sup> + 2x + 2 &equiv; 1')], check=(5 ** 3 + 2 * 5 + 2) % 17)
K.calc('e', 'How many points, including O, does y<sup>2</sup> = x<sup>3</sup> + 2x + 2 mod 17 have?', '19', 'Count squares, add one for O.', ['18 grid points come in 9 mirror pairs.', 'Add the point at infinity.', eq('#E = 19')], check=1 + sum(1 for x in range(17) for y in range(17) if (y * y - x ** 3 - 2 * x - 2) % 17 == 0))
K.calc('e', 'For G = (5, 1) mod 17, what is the y coordinate of &minus;G?', '16', 'Negate y mod 17.', ['&minus;1 mod 17.', '= 16.', eq('&minus;G = (5, 16)')], check=-1 % 17)
K.calc('m', 'Doubling G = (5, 1) on the toy curve (a = 2, p = 17): what is &lambda;?', '13', '(3x<sup>2</sup> + a)(2y)<sup>&minus;1</sup>.', ['3 &middot; 25 + 2 = 77 &equiv; 9, 2<sup>&minus;1</sup> = 9.', '9 &times; 9 = 81 &equiv; 13.', eq('&lambda; = 13')], check=(3 * 25 + 2) * pow(2, -1, 17) % 17)
K.calc('m', 'With &lambda; = 13, what is the x coordinate of 2G for G = (5, 1) mod 17?', '6', '&lambda;<sup>2</sup> &minus; 2x<sub>1</sub>.', ['169 &minus; 10 = 159.', '159 = 9 &times; 17 + 6.', eq('x<sub>3</sub> = 6')], check=(13 * 13 - 10) % 17)
K.calc('m', 'Add (5, 1) + (6, 3) mod 17. What is the x coordinate of the sum?', '10', '&lambda; = (3 &minus; 1)/(6 &minus; 5) = 2.', ['&lambda;<sup>2</sup> = 4.', '4 &minus; 5 &minus; 6 = &minus;7 &equiv; 10.', eq('x<sub>3</sub> = 10')], check=(2 * 2 - 5 - 6) % 17)
K.calc('m', 'ECDH on the toy curve with order n = 19: a = 3, b = 10. The shared point is kG for which k between 1 and 18?', '11', 'ab mod n.', ['3 &times; 10 = 30.', '30 mod 19 = 11.', eq('S = 11G = (13, 10)')], check=30 % 19)
K.calc('m', 'By Hasse’s theorem, what is the largest possible number of points on a curve over F<sub>17</sub>? Round down.', '26', 'p + 1 + 2&radic;p.', ['2&radic;17 &asymp; 8.25.', '18 + 8.25 = 26.25.', eq('#E &le; 26')], check=int(18 + 2 * 17 ** 0.5))
K.calc('h', 'Pollard rho on a curve with a 256 bit prime order takes about 2<sup>k</sup> steps. What is k?', '128', '&radic;n.', ['&radic;(2<sup>256</sup>) = 2<sup>128</sup>.', 'Constant factors change this by under one bit.', eq('k = 128')], check=128)
K.calc('h', 'Toy ECDSA, n = 19, d = 7, h = 10, k = 3, kG = (10, 6). What is s?', '14', 's = k<sup>&minus;1</sup>(h + rd) mod n with r = 10.', ['3<sup>&minus;1</sup> mod 19 = 13, h + rd = 80 &equiv; 4.', '13 &times; 4 = 52 &equiv; 14.', eq('s = 14')], check=pow(3, -1, 19) * ((10 + 10 * 7) % 19) % 19)
K.calc('h', 'How many bytes is a compressed point on a 256 bit curve?', '33', 'One prefix byte plus x.', ['x takes 32 bytes.', 'The prefix 02 or 03 holds the parity of y.', eq('1 + 32 = 33')], check=1 + 32)
K.calc('x', 'In the style of an IIT Delhi exam: two toy ECDSA signatures (n = 19) share r = 10, with h<sub>1</sub> = 10, s<sub>1</sub> = 14, h<sub>2</sub> = 5, s<sub>2</sub> = 6. Recover the nonce k.', '3', 'k = (h<sub>1</sub> &minus; h<sub>2</sub>)(s<sub>1</sub> &minus; s<sub>2</sub>)<sup>&minus;1</sup>.', ['h<sub>1</sub> &minus; h<sub>2</sub> = 5, s<sub>1</sub> &minus; s<sub>2</sub> = 8, 8<sup>&minus;1</sup> mod 19 = 12.', '5 &times; 12 = 60 &equiv; 3.', eq('k = 3')], check=5 * pow(8, -1, 19) % 19)
K.calc('x', 'Continue: with k = 3, r = 10, s<sub>1</sub> = 14, h<sub>1</sub> = 10 and n = 19, recover the private key d.', '7', 'd = (s<sub>1</sub>k &minus; h<sub>1</sub>) r<sup>&minus;1</sup>.', ['14 &times; 3 &minus; 10 = 32 &equiv; 13, 10<sup>&minus;1</sup> mod 19 = 2.', '13 &times; 2 = 26 &equiv; 7.', eq('d = 7')], check=(14 * 3 - 10) * pow(10, -1, 19) % 19)

K.assign('count_points', 'e', 'Count the points of a curve',
         '<p>Write <code>count_points(p, a, b)</code> that returns the number of points on y<sup>2</sup> = x<sup>3</sup> + ax + b mod p, including the point at infinity. Trying every (x, y) is fine for small p.</p>',
         '''
def count_points(p, a, b):
    # your code here
    pass
''', [('count_points(17, 2, 2)', 19), ('count_points(61, 0, 7)', 1 + sum(1 for x in range(61) for y in range(61) if (y * y - x ** 3 - 7) % 61 == 0)), ('count_points(5, 1, 1)', 9)],
         '''
def count_points(p, a, b):
    count = 1
    for x in range(p):
        for y in range(p):
            if (y * y - (x ** 3 + a * x + b)) % p == 0:
                count = count + 1
    return count
''', 'Start at 1 for the point at infinity, then add 1 for every (x, y) that satisfies the equation mod p.', '<p>A faster version loops over x only and uses Euler’s criterion to decide whether the right side is a square, adding 2 for a non zero square and 1 for zero.</p>')
K.assign('ec_add', 'm', 'Add two points',
         '<p>Write <code>ec_add(P, Q, p, a)</code> for points given as tuples (x, y), with None for the point at infinity. Handle P = O, Q = O, Q = &minus;P, doubling and the general case. Return a tuple or None.</p>',
         '''
def ec_add(P, Q, p, a):
    # your code here
    pass
''', [('ec_add((5, 1), (6, 3), 17, 2) == (10, 6)', True), ('ec_add((5, 1), (5, 1), 17, 2) == (6, 3)', True), ('ec_add((5, 1), (5, 16), 17, 2) is None', True), ('ec_add(None, (5, 1), 17, 2) == (5, 1)', True)],
         '''
def ec_add(P, Q, p, a):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)
''', 'Deal with None first, then the vertical line case, then pick the tangent or chord slope and apply the two formulas.', '<p>The vertical line check must come before the doubling branch, so that a point with y = 0 doubles to O instead of dividing by zero.</p>')
K.assign('ec_multiply', 'm', 'Double and add',
         '<p>Write <code>ec_multiply(k, P, p, a)</code> that returns kP by double and add over the bits of k. You may include your own point addition inside. kP for k = 0 is None.</p>',
         '''
def ec_multiply(k, P, p, a):
    # your code here
    pass
''', [('ec_multiply(2, (5, 1), 17, 2) == (6, 3)', True), ('ec_multiply(11, (5, 1), 17, 2) == (13, 10)', True), ('ec_multiply(19, (5, 1), 17, 2) is None', True), ('ec_multiply(0, (5, 1), 17, 2) is None', True), ('ec_multiply(32, (5, 1), 17, 2) == (16, 4)', True)],
         '''
def ec_multiply(k, P, p, a):
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
            lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
        else:
            lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (lam * lam - x1 - x2) % p
        return (x3, (lam * (x1 - x3) - y1) % p)
    R = None
    for bit in bin(k)[2:]:
        R = add(R, R)
        if bit == "1":
            R = add(R, P)
    return R
''', 'Start with R = None. For each bit of bin(k)[2:], set R = R + R, and add P when the bit is "1".', '<p>Because G has order 19 on the toy curve, 32G = 13G = (16, 4), the same point the chapter program prints.</p>')

K.must('Curve', 'y<sup>2</sup> = x<sup>3</sup> + ax + b mod p plus O, 4a<sup>3</sup> + 27b<sup>2</sup> &ne; 0. Hasse |#E &minus; (p + 1)| &le; 2&radic;p.')
K.must('Add', '&lambda; = (y<sub>2</sub> &minus; y<sub>1</sub>)/(x<sub>2</sub> &minus; x<sub>1</sub>) or (3x<sup>2</sup> + a)/2y. x<sub>3</sub> = &lambda;<sup>2</sup> &minus; x<sub>1</sub> &minus; x<sub>2</sub>, y<sub>3</sub> = &lambda;(x<sub>1</sub> &minus; x<sub>3</sub>) &minus; y<sub>1</sub>.')
K.must('ECDLP and ECDH', 'Q = dG. Rho &asymp; &radic;n, 256 bit = 128 bit security. S = abG. X25519: ladder, clamping, RFC 7748.')
K.must('ECDSA', 'r = (kG)<sub>x</sub>, s = k<sup>&minus;1</sup>(h + rd). Reused k: k = &Delta;h/&Delta;s, d = (sk &minus; h)/r. RFC 6979.')
K.must('Ed25519', 'Schnorr s = k + e d, k = H(prefix, m). 32 byte keys, 64 byte signatures. RFC 8032.')
K.must('Attacks', 'Invalid curve and small subgroup points, biased nonces, timing, MOV and anomalous curves, Dual EC DRBG, CurveBall.')

T = K.topic(
    slug='cy-ecc', topic='cy-ecc', step=(2, 'Public key cryptography and its maths', 'cy-c2', 'The number theory behind public keys, then RSA, Diffie-Hellman and elliptic curves, each with its proofs and its attacks.', 'Advanced'),
    title='Elliptic curve cryptography: ECDH, X25519, ECDSA and Ed25519', short='Elliptic curves', badge='2.4', minutes=90,
    lead='Elliptic curves from the ground up: curves over finite fields and Hasse’s theorem, the chord and tangent group law with worked numbers, scalar multiplication and the ECDLP, ECDH and point compression, X25519, ECDSA with the nonce reuse attack, Schnorr and Ed25519, invalid curve and other attacks, Dual EC DRBG, and how to choose a curve.',
    desc='elliptic curve cryptography, ECC, Koblitz, Miller, Weierstrass, finite field, point at infinity, Hasse theorem, Schoof, cofactor, point addition, doubling, group law, scalar multiplication, double and add, Montgomery ladder, ECDLP, Pollard rho, ECDH, point compression, secp256k1, P-256, Curve25519, X25519, clamping, ECDSA, nonce reuse, PlayStation 3, RFC 6979, Minerva, Schnorr, Ed25519, EdDSA, Taproot, invalid curve attack, MOV, Dual EC DRBG, CurveBall',
    summary='curves over F_p, the group law, scalar multiplication and ECDLP, ECDH and X25519, ECDSA and its nonce, Ed25519, attacks and curve choice.',
    keywords=['elliptic curve', 'point addition', 'ECDLP', 'ECDH', 'X25519', 'ECDSA', 'nonce reuse', 'Ed25519', 'invalid curve', 'secp256k1'],
    recap='<p>A number times a point is easy, the reverse is hard. Short keys, but every detail counts: check points, never repeat a nonce, use constant time code and vetted curves.</p>',
    added='2026-11-14')
