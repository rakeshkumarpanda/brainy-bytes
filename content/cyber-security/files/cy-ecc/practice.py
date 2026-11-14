# 2.4 Elliptic curve cryptography: ECDH, X25519, ECDSA and Ed25519
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


# ================================================================== task 1: Count the points of a curve
# Write count_points(p, a, b) that returns the number of points on y2 = x3 + ax + b mod p, including
# the point at infinity. Trying every (x, y) is fine for small p.
# Hint: Start at 1 for the point at infinity, then add 1 for every (x, y) that satisfies the
# equation mod p.

def count_points(p, a, b):
    # your code here
    pass


# ================================================================== task 2: Add two points
# Write ec_add(P, Q, p, a) for points given as tuples (x, y), with None for the point at infinity.
# Handle P = O, Q = O, Q = −P, doubling and the general case. Return a tuple or None.
# Hint: Deal with None first, then the vertical line case, then pick the tangent or chord slope and
# apply the two formulas.

def ec_add(P, Q, p, a):
    # your code here
    pass


# ================================================================== task 3: Double and add
# Write ec_multiply(k, P, p, a) that returns kP by double and add over the bits of k. You may
# include your own point addition inside. kP for k = 0 is None.
# Hint: Start with R = None. For each bit of bin(k)[2:], set R = R + R, and add P when the bit is
# "1".

def ec_multiply(k, P, p, a):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Count the points of a curve", [('count_points(17, 2, 2)', 19), ('count_points(61, 0, 7)', 61), ('count_points(5, 1, 1)', 9)]))
    results.append(check("Task 2: Add two points", [('ec_add((5, 1), (6, 3), 17, 2) == (10, 6)', True), ('ec_add((5, 1), (5, 1), 17, 2) == (6, 3)', True), ('ec_add((5, 1), (5, 16), 17, 2) is None', True), ('ec_add(None, (5, 1), 17, 2) == (5, 1)', True)]))
    results.append(check("Task 3: Double and add", [('ec_multiply(2, (5, 1), 17, 2) == (6, 3)', True), ('ec_multiply(11, (5, 1), 17, 2) == (13, 10)', True), ('ec_multiply(19, (5, 1), 17, 2) is None', True), ('ec_multiply(0, (5, 1), 17, 2) is None', True), ('ec_multiply(32, (5, 1), 17, 2) == (16, 4)', True)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
