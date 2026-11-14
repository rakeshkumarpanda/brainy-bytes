# 2.4 Elliptic curve cryptography: ECDH, X25519, ECDSA and Ed25519
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


# ================================================================== task 1: Count the points of a curve
# Write count_points(p, a, b) that returns the number of points on y2 = x3 + ax + b mod p, including
# the point at infinity. Trying every (x, y) is fine for small p.
# Why it works: A faster version loops over x only and uses Euler’s criterion to decide whether the
# right side is a square, adding 2 for a non zero square and 1 for zero.

def count_points(p, a, b):
    count = 1
    for x in range(p):
        for y in range(p):
            if (y * y - (x ** 3 + a * x + b)) % p == 0:
                count = count + 1
    return count


# ================================================================== task 2: Add two points
# Write ec_add(P, Q, p, a) for points given as tuples (x, y), with None for the point at infinity.
# Handle P = O, Q = O, Q = −P, doubling and the general case. Return a tuple or None.
# Why it works: The vertical line check must come before the doubling branch, so that a point with y
# = 0 doubles to O instead of dividing by zero.

def ec_add(P, Q, p, a):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


# ================================================================== task 3: Double and add
# Write ec_multiply(k, P, p, a) that returns kP by double and add over the bits of k. You may
# include your own point addition inside. kP for k = 0 is None.
# Why it works: Because G has order 19 on the toy curve, 32G = 13G = (16, 4), the same point the
# chapter program prints.

def ec_multiply(k, P, p, a):
    def add(P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2 and (y1 + y2) % p == 0:
            return None
        if P == Q:
            lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
        else:
            lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (lam * lam - x1 - x2) % p
        return (x3, (lam * (x1 - x3) - y1) % p)
    R = None
    for bit in bin(k)[2:]:
        R = add(R, R)
        if bit == "1":
            R = add(R, P)
    return R


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Count the points of a curve", [('count_points(17, 2, 2)', 19), ('count_points(61, 0, 7)', 61), ('count_points(5, 1, 1)', 9)]))
    results.append(check("Task 2: Add two points", [('ec_add((5, 1), (6, 3), 17, 2) == (10, 6)', True), ('ec_add((5, 1), (5, 1), 17, 2) == (6, 3)', True), ('ec_add((5, 1), (5, 16), 17, 2) is None', True), ('ec_add(None, (5, 1), 17, 2) == (5, 1)', True)]))
    results.append(check("Task 3: Double and add", [('ec_multiply(2, (5, 1), 17, 2) == (6, 3)', True), ('ec_multiply(11, (5, 1), 17, 2) == (13, 10)', True), ('ec_multiply(19, (5, 1), 17, 2) is None', True), ('ec_multiply(0, (5, 1), 17, 2) is None', True), ('ec_multiply(32, (5, 1), 17, 2) == (16, 4)', True)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
