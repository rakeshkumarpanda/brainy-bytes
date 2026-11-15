# 2.2 RSA: keys, proofs, signatures and attacks
# Example "rsa_toy" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Textbook RSA with small numbers, then a real size key made the same way
import secrets
from math import gcd

p, q = 61, 53
n = p * q                                # public modulus
phi = (p - 1) * (q - 1)                  # Euler's phi, kept secret
e = 17                                   # public exponent
print("n =", n, " phi =", phi, " gcd(e, phi) =", gcd(e, phi))
d = pow(e, -1, phi)                      # private exponent
print("public key (n, e) =", (n, e), " private d =", d)

m = 65                                   # the message as a number below n
c = pow(m, e, n)                         # encrypt with the public key
print("encrypt 65 ->", c)
print("decrypt", c, "->", pow(c, d, n))

# The same steps at real size: two random 1024 bit primes
def is_prime(n, rounds=40):
    if n < 4:
        return n in (2, 3)
    for small in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29):
        if n % small == 0:
            return n == small
    d, s = n - 1, 0
    while d % 2 == 0:
        d, s = d // 2, s + 1
    for i in range(rounds):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for j in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True

def random_prime(bits):
    while True:
        candidate = secrets.randbits(bits) | (3 << (bits - 2)) | 1   # top two bits set, odd
        if candidate % 65537 != 1 and is_prime(candidate):
            return candidate

e = 65537
p = random_prime(1024)
q = random_prime(1024)
n = p * q
d = pow(e, -1, (p - 1) * (q - 1))
print("n has", n.bit_length(), "bits, d has", d.bit_length(), "bits")
m = int.from_bytes(b"meet at the library at 6", "big")
c = pow(m, e, n)
back = pow(c, d, n)
print("round trip ok:", back == m, "->", back.to_bytes(24, "big"))
