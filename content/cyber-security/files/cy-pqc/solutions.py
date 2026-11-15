# 1.2 Post quantum cryptography: Shor, lattices, ML-KEM and ML-DSA
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


# ================================================================== task 1: Quantum strength of a symmetric key
# Write quantum_bits(key_bits) that returns the approximate security in bits against Grover’s
# algorithm, which is half the key length (rounded down).
# Why it works: This is why CNSA 2.0 requires AES-256 for national security systems: it keeps 128
# bits of strength even against Grover.

def quantum_bits(key_bits):
    return key_bits // 2


# ================================================================== task 2: The classical part of Shor’s algorithm
# Write shor_step(N, a). Find the period r of ax mod N by trying powers (fine for small N). If
# gcd(a, N) > 1 return that gcd. If r is odd or ar/2 ≡ −1 (mod N), return None. Otherwise return the
# smaller of gcd(ar/2 − 1, N) and gcd(ar/2 + 1, N).
# Why it works: For a random a, the chance of success is at least one half, so Shor repeats with a
# new a a few times at most.

from math import gcd

def shor_step(N, a):
    g = gcd(a, N)
    if g > 1:
        return g
    r, value = 1, a % N
    while value != 1:
        value = value * a % N
        r = r + 1
    if r % 2 == 1:
        return None
    x = pow(a, r // 2, N)
    if x == N - 1:
        return None
    return min(gcd(x - 1, N), gcd(x + 1, N))


# ================================================================== task 3: Multiplication in the ML-KEM ring
# Write ring_mul(a, b, q) for two coefficient lists of the same length n, in Zq[x]/(xn + 1).
# Coefficient i is the constant term for xi. Remember xn = −1, so a product term that reaches degree
# n or more wraps round with a minus sign. Return a list with values from 0 to q − 1.
# Why it works: (1 + 2x)(3 + 4x) = 3 + 10x + 8x2, and x2 = −1 here, so the result is (3 − 8) + 10x =
# −5 + 10x ≡ 12 + 10x (mod 17). Real ML-KEM does this with the number theoretic transform in O(n log
# n).

def ring_mul(a, b, q):
    n = len(a)
    out = [0] * n
    for i in range(n):
        for j in range(n):
            if i + j < n:
                out[i + j] = (out[i + j] + a[i] * b[j]) % q
            else:
                out[i + j - n] = (out[i + j - n] - a[i] * b[j]) % q
    return out


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Quantum strength of a symmetric key", [('quantum_bits(128)', 64), ('quantum_bits(256)', 128), ('quantum_bits(192)', 96)]))
    results.append(check("Task 2: The classical part of Shor’s algorithm", [('shor_step(15, 7)', 3), ('shor_step(21, 2)', 3), ('shor_step(35, 3)', 5), ('shor_step(15, 14)', None), ('shor_step(15, 5)', 5)]))
    results.append(check("Task 3: Multiplication in the ML-KEM ring", [('ring_mul([0, 1, 0, 0], [0, 0, 0, 1], 3329)', [3328, 0, 0, 0]), ('ring_mul([1, 2], [3, 4], 17)', [12, 10]), ('ring_mul([1, 0, 0, 0], [5, 6, 7, 8], 97)', [5, 6, 7, 8])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
