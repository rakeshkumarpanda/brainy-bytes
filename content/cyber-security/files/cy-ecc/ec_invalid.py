# 2.4 Elliptic curve cryptography: ECDH, X25519, ECDSA and Ed25519
# Example "ec_invalid" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

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
