# 2.1 Number theory for cryptography: modular arithmetic to primes
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


# ================================================================== task 1: A modular inverse
# Write modinv(a, n) that returns the inverse of a modulo n (a number from 1 to n − 1), or None if
# it does not exist. Use the extended Euclidean algorithm, not pow.
# Why it works: 17 and 3120 are the e and φ(n) of the classic RSA example with p = 61 and q = 53, so
# the answer 2753 is that example’s private exponent.

def modinv(a, n):
    old_r, r = a, n
    old_s, s = 1, 0
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
    if old_r != 1:
        return None
    return old_s % n


# ================================================================== task 2: Square and multiply
# Write power_mod(b, e, n) that returns be mod n using square and multiply over the bits of e. Do
# not use pow or **.
# Why it works: For e = 0, bin(0) is "0b0", so the loop squares 1 once and the answer is 1, which is
# correct.

def power_mod(b, e, n):
    result = 1 % n
    for bit in bin(e)[2:]:
        result = result * result % n
        if bit == "1":
            result = result * b % n
    return result


# ================================================================== task 3: The Chinese remainder theorem
# Write crt(remainders, moduli) for pairwise coprime moduli. Return the x from 0 to M − 1 that has
# every given remainder.
# Why it works: Each term is ai modulo its own mi and 0 modulo every other modulus, so the sum has
# all the right remainders at once.

def crt(remainders, moduli):
    M = 1
    for m in moduli:
        M = M * m
    x = 0
    for i in range(len(moduli)):
        m = moduli[i]
        Mi = M // m
        yi = pow(Mi, -1, m)
        x = x + remainders[i] * Mi * yi
    return x % M


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A modular inverse", [('modinv(3, 11)', 4), ('modinv(17, 3120)', 2753), ('modinv(6, 9)', None), ('modinv(1, 7)', 1)]))
    results.append(check("Task 2: Square and multiply", [('power_mod(4, 13, 497)', 445), ('power_mod(2, 10, 1000)', 24), ('power_mod(7, 0, 13)', 1), ('power_mod(123456789, 65537, 1000003)', 752575)]))
    results.append(check("Task 3: The Chinese remainder theorem", [('crt([2, 3, 2], [3, 5, 7])', 23), ('crt([1, 2], [4, 9])', 29), ('crt([0, 0, 1], [2, 3, 5])', 6)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
