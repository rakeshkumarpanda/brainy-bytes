# 1.2 Post quantum cryptography: Shor, lattices, ML-KEM and ML-DSA
# Example "shor_classical" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# The number theory inside Shor's algorithm. A quantum computer finds the period r quickly.
# Here we find it slowly by trying powers, which is fine for tiny numbers like 15 and 21.
from math import gcd

def period(a, N):                       # smallest r > 0 with a^r = 1 mod N
    r, value = 1, a % N
    while value != 1:
        value = value * a % N
        r = r + 1
    return r

def shor_factor(N, a):
    g = gcd(a, N)
    if g != 1:
        return g, N // g, "lucky: a shares a factor with N"
    r = period(a, N)
    if r % 2 == 1:
        return None, None, f"period r = {r} is odd, pick another a"
    x = pow(a, r // 2, N)
    if x == N - 1:
        return None, None, f"a^(r/2) = -1 mod N, pick another a"
    return gcd(x - 1, N), gcd(x + 1, N), f"period r = {r}, a^(r/2) mod N = {x}"

print("powers of 7 mod 15:", [pow(7, k, 15) for k in range(1, 9)])
for N, a in [(15, 7), (21, 2), (35, 3), (15, 14)]:
    p, q, note = shor_factor(N, a)
    print(f"N = {N}, a = {a}: {note} -> factors {p} and {q}")
