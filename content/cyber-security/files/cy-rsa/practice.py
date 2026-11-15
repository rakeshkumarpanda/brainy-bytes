# 2.2 RSA: keys, proofs, signatures and attacks
# Practice tasks. Fill in each function, then run this file.
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


# ================================================================== task 1: Compute the private exponent
# Write rsa_private(p, q, e) that returns d = e−1 mod (p − 1)(q − 1), or None when gcd(e, φ) is not
# 1. You may use pow(e, -1, phi) after checking the gcd.
# Hint: Compute phi first, check gcd(e, phi), then invert.

from math import gcd

def rsa_private(p, q, e):
    # your code here
    pass


# ================================================================== task 2: RSA decryption with CRT
# Write crt_decrypt(c, p, q, d) that decrypts with dp, dq, qinv and Garner’s formula. Do not compute
# pow(c, d, p * q).
# Hint: Compute mp and mq with the reduced exponents, then h = q_inv * (mp - mq) mod p and m = mq +
# h q.

def crt_decrypt(c, p, q, d):
    # your code here
    pass


# ================================================================== task 3: The integer cube root behind the small e attack
# Write cube_root(x) that returns the largest whole number r with r3 ≤ x, for any x ≥ 0. Use binary
# search on whole numbers, not floats, because floats lose precision for big numbers.
# Hint: Double high until high cubed passes x, then binary search keeping low cubed at most x.

def cube_root(x):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Compute the private exponent", [('rsa_private(61, 53, 17)', 2753), ('rsa_private(5, 11, 3)', 27), ('rsa_private(5, 11, 5)', None), ('rsa_private(11, 13, 7)', 103)]))
    results.append(check("Task 2: RSA decryption with CRT", [('crt_decrypt(2790, 61, 53, 2753)', 65), ('crt_decrypt(8, 5, 11, 27)', 2), ('crt_decrypt(598195729194, 1000003, 1000033, 983264276609)', 424242)]))
    results.append(check("Task 3: The integer cube root behind the small e attack", [('cube_root(1000000)', 100), ('cube_root(27)', 3), ('cube_root(26)', 2), ('cube_root(0)', 0), ('cube_root(12345 ** 3)', 12345), ('cube_root(2 ** 300) == 2 ** 100', True)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
