# 2.3 Diffie-Hellman, ElGamal and the discrete logarithm
# Model solutions. Try practice.py first.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: A Diffie-Hellman key
# Write dh_key(p, other_public, my_secret) that returns the shared key. Reject bad public values:
# return None unless 1 < other_public < p − 1.
# Why it works: Real code also checks that the value lies in the right subgroup, Aq mod p = 1 for a
# safe prime p = 2q + 1.

def dh_key(p, other_public, my_secret):
    if not 1 < other_public < p - 1:
        return None
    return pow(other_public, my_secret, p)


# ================================================================== task 2: Baby step, giant step
# Write bsgs(g, h, p) that returns the smallest x ≥ 0 with gx mod p = h, using baby step giant step
# with m = isqrt(p − 1) + 1. Return None if there is no answer.
# Why it works: Keeping only the first j for each value makes the answer the smallest x, which
# matters when g is not a generator and values repeat.

from math import isqrt

def bsgs(g, h, p):
    m = isqrt(p - 1) + 1
    table = {}
    value = 1
    for j in range(m):
        if value not in table:
            table[value] = j
        value = value * g % p
    step = pow(g, -m, p)
    y = h % p
    for i in range(m):
        if y in table:
            return i * m + table[y]
        y = y * step % p
    return None


# ================================================================== task 3: Decrypt ElGamal
# Write elgamal_decrypt(p, x, c1, c2) that returns m = c2 · (c1x)−1 mod p.
# Why it works: The second test is a small example with p = 467, g = 2, private key x = 127 and
# random k = 213, built the same way as the worked problem.

def elgamal_decrypt(p, x, c1, c2):
    s = pow(c1, x, p)
    return c2 * pow(s, -1, p) % p


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A Diffie-Hellman key", [('dh_key(23, 19, 6)', 2), ('dh_key(23, 8, 15)', 2), ('dh_key(23, 1, 6)', None), ('dh_key(23, 22, 15)', None), ('dh_key(1000003, 777, 271828)', 379974)]))
    results.append(check("Task 2: Baby step, giant step", [('bsgs(2, 48, 101)', 73), ('bsgs(5, 100, 383)', 270), ('bsgs(2, 1, 101)', 0), ('bsgs(4, pow(4, 123456, 1000003), 1000003)', 123456)]))
    results.append(check("Task 3: Decrypt ElGamal", [('elgamal_decrypt(23, 6, 10, 14)', 10), ('elgamal_decrypt(467, 127, pow(2, 213, 467), 100 * pow(pow(2, 127, 467), 213, 467) % 467)', 100), ('elgamal_decrypt(23, 6, 1, 5)', 5)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
