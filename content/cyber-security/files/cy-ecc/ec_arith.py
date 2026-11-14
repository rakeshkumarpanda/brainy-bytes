# 2.4 Elliptic curve cryptography: ECDH, X25519, ECDSA and Ed25519
# Example "ec_arith" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

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
