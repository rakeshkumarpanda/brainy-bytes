# 2.1 Number theory for cryptography: modular arithmetic to primes
# Example "euclid" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Euclid's algorithm, the extended version, and modular inverses
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def extended_gcd(a, b):
    # returns g, s, t with g = gcd(a, b) = s*a + t*b
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t

def inverse(a, n):
    g, s, t = extended_gcd(a, n)
    if g != 1:
        return None                     # no inverse when a and n share a factor
    return s % n

print("gcd(48, 18) =", gcd(48, 18))
g, s, t = extended_gcd(240, 46)
print("gcd(240, 46) =", g, "=", s, "* 240 +", t, "* 46")
print("inverse of 17 mod 3120 =", inverse(17, 3120))
print("check: 17 * 2753 mod 3120 =", 17 * 2753 % 3120)
print("inverse of 6 mod 9 =", inverse(6, 9))
print("Python 3.8+ can do it too:", pow(17, -1, 3120))
