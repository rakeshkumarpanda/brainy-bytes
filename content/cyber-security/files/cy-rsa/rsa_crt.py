# 2.2 RSA: keys, proofs, signatures and attacks
# Example "rsa_crt" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# RSA-CRT decryption, and the Bellcore fault attack that breaks it
from math import gcd

p, q = 61, 53
n, e, d = p * q, 17, 2753
dp = d % (p - 1)                         # 53
dq = d % (q - 1)                         # 49
q_inv = pow(q, -1, p)                    # 38
print("dp =", dp, " dq =", dq, " q_inv =", q_inv)

def crt_power(c, fault=False):
    mp = pow(c, dp, p)                   # half size work mod p
    mq = pow(c, dq, q)                   # half size work mod q
    if fault:
        mq = (mq + 1) % q                # a glitch spoils the mod q half
    h = q_inv * (mp - mq) % p            # Garner's formula
    return mq + h * q

c = 2790
print("CRT decrypt:", crt_power(c), " direct:", pow(c, d, n))

# A signature is the same operation. A faulty one leaks a prime factor.
m = 1234
s_good = crt_power(m)
s_bad = crt_power(m, fault=True)
print("good signature verifies:", pow(s_good, e, n) == m)
print("faulty signature verifies:", pow(s_bad, e, n) == m)
leak = gcd(pow(s_bad, e, n) - m, n)
print("gcd(s'^e - m, n) =", leak, "->", leak, "x", n // leak, "= n")

# The defence: check before you release
def safe_sign(m):
    s = crt_power(m, fault=True)
    if pow(s, e, n) != m:
        return None                      # refuse to output a bad signature
    return s
print("safe_sign with a fault returns:", safe_sign(m))
