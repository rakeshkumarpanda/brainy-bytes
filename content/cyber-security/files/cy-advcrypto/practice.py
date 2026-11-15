# 1.3 Advanced cryptography: secret sharing, zero knowledge, homomorphic encryption and MPC
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


# ================================================================== task 1: Finish a set of additive shares
# Write finish_shares(value, parts, M). You are given the random parts for all parties but the last.
# Return the full list of parts, with the last part chosen so that all parts add up to value modulo
# M. Every part must be between 0 and M − 1.
# Hint: The last part is value minus the sum of the others, reduced mod M.

def finish_shares(value, parts, M):
    # your code here
    pass


# ================================================================== task 2: Rebuild a Shamir secret
# Write rebuild(shares, P), where shares is a list of [x, y] pairs on a polynomial mod the prime P.
# Use Lagrange interpolation at x = 0 and return the secret f(0) from 0 to P − 1. Use pow(d, -1, P)
# for a modular inverse.
# Hint: For each share multiply (0 − xj) on top and (xi − xj) below over all other shares, then add
# yi times top times the inverse of below.

def rebuild(shares, P):
    # your code here
    pass


# ================================================================== task 3: Sum Paillier ciphertexts
# Toy Paillier key: n = 35, g = 36, λ = 12, μ = 3. Write paillier_sum(ciphertexts, n, lam, mu) that
# multiplies all ciphertexts mod n2 and then decrypts the product with m = L(cλ mod n2) · μ mod n,
# where L(u) = (u − 1) // n. The ciphertexts 88, 512 and 257 hide 4, 9 and 5.
# Hint: Start with c = 1, multiply in each ciphertext mod n * n, then apply L and multiply by mu mod
# n.

def paillier_sum(ciphertexts, n, lam, mu):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Finish a set of additive shares", [('finish_shares(40, [77, 15], 101)', [77, 15, 49]), ('finish_shares(5, [1, 2, 3], 11)', [1, 2, 3, 10]), ('sum(finish_shares(1840, [123456, 98765], 2 ** 61 - 1)) % (2 ** 61 - 1)', 1840)]))
    results.append(check("Task 2: Rebuild a Shamir secret", [('rebuild([[1, 1], [2, 10], [3, 1]], 11)', 7), ('rebuild([[2, 10], [4, 7], [5, 6]], 11)', 7), ('rebuild([[1, 5], [2, 9]], 11)', 1)]))
    results.append(check("Task 3: Sum Paillier ciphertexts", [('paillier_sum([88], 35, 12, 3)', 4), ('paillier_sum([88, 512], 35, 12, 3)', 13), ('paillier_sum([88, 512, 257], 35, 12, 3)', 18)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
