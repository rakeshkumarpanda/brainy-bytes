# 2.2 RSA: keys, proofs, signatures and attacks
# Example "rsa_attacks" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Attacks on careless RSA, all on toy keys made right here
import random
from math import gcd, isqrt

rng = random.Random(2026)                # fixed seed so the demo is repeatable. NEVER use random for real keys.

def is_prime(n):
    if n < 4:
        return n in (2, 3)
    if n % 2 == 0:
        return False
    d, s = n - 1, 0
    while d % 2 == 0:
        d, s = d // 2, s + 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1) or a % n == 0:
            continue
        for j in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True

def prime_for_e3(bits):                  # p mod 3 = 2, so gcd(3, p - 1) = 1
    while True:
        p = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if p % 3 == 2 and is_prime(p):
            return p

def cube_root(x):                        # the whole number r with r^3 <= x < (r + 1)^3
    low, high = 0, 1 << (x.bit_length() // 3 + 1)
    while low < high:
        mid = (low + high + 1) // 2
        if mid ** 3 <= x:
            low = mid
        else:
            high = mid - 1
    return low

# 1. Malleability: anyone can turn an encryption of m into one of 2m
n, e, d = 3233, 17, 2753
c = pow(65, e, n)
c2 = c * pow(2, e, n) % n
print("1. c * 2^e decrypts to", pow(c2, d, n))

# 2. Small e with no padding: if m^3 < n, the ciphertext is just m^3
p, q = prime_for_e3(512), prime_for_e3(512)
n = p * q
m = int.from_bytes(b"PIN 4321", "big")
c = pow(m, 3, n)
print("2. m^3 < n:", m ** 3 < n, " cube root gives", cube_root(c).to_bytes(8, "big"))

# 3. Hastad: the same m sent with e = 3 to three people
keys = [prime_for_e3(256) * prime_for_e3(256) for i in range(3)]
m = int.from_bytes(b"the secret meeting is at noon", "big")
cs = [pow(m, 3, k) for k in keys]
N = keys[0] * keys[1] * keys[2]
x = 0
for ci, ki in zip(cs, keys):             # Chinese remainder theorem gives m^3 mod N = m^3
    Ni = N // ki
    x = x + ci * Ni * pow(Ni, -1, ki)
x = x % N
print("3. Hastad recovers:", cube_root(x).to_bytes(29, "big"))

# 4. Two keys that share a prime (bad randomness at boot)
shared = prime_for_e3(256)
n1 = shared * prime_for_e3(256)
n2 = shared * prime_for_e3(256)
g = gcd(n1, n2)
print("4. gcd(n1, n2) finds the shared prime:", g == shared)

# 5. Fermat factoring when p and q are too close
def fermat_factor(n):
    a = isqrt(n)
    if a * a < n:
        a = a + 1
    tries = 0
    while True:
        b2 = a * a - n
        b = isqrt(b2)
        tries = tries + 1
        if b * b == b2:
            return a - b, a + b, tries
        a = a + 1

print("5. 5959 =", fermat_factor(5959))
p = prime_for_e3(512)
q = p + 2
while not is_prime(q):
    q = q + 2
f1, f2, tries = fermat_factor(p * q)
print("   1024 bit n with close primes factored in", tries, "try:", {f1, f2} == {p, q})
