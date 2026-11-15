# 2.1 Number theory for cryptography: modular arithmetic to primes
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


# ================================================================== task 1: A modular inverse
# Write modinv(a, n) that returns the inverse of a modulo n (a number from 1 to n − 1), or None if
# it does not exist. Use the extended Euclidean algorithm, not pow.
# Hint: Track only r and s: at the end old_r is the gcd and old_s the coefficient of a.

def modinv(a, n):
    # your code here
    pass


# ================================================================== task 2: Square and multiply
# Write power_mod(b, e, n) that returns be mod n using square and multiply over the bits of e. Do
# not use pow or **.
# Hint: Loop over bin(e)[2:]. Square every time, multiply by b when the bit is "1", and reduce mod n
# each time.

def power_mod(b, e, n):
    # your code here
    pass


# ================================================================== task 3: The Chinese remainder theorem
# Write crt(remainders, moduli) for pairwise coprime moduli. Return the x from 0 to M − 1 that has
# every given remainder.
# Hint: Compute M, then add ai · Mi · yi for each condition, where yi is the inverse of Mi mod mi.

def crt(remainders, moduli):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A modular inverse", [('modinv(3, 11)', 4), ('modinv(17, 3120)', 2753), ('modinv(6, 9)', None), ('modinv(1, 7)', 1)]))
    results.append(check("Task 2: Square and multiply", [('power_mod(4, 13, 497)', 445), ('power_mod(2, 10, 1000)', 24), ('power_mod(7, 0, 13)', 1), ('power_mod(123456789, 65537, 1000003)', 752575)]))
    results.append(check("Task 3: The Chinese remainder theorem", [('crt([2, 3, 2], [3, 5, 7])', 23), ('crt([1, 2], [4, 9])', 29), ('crt([0, 0, 1], [2, 3, 5])', 6)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
