# 3.2 Vulnerabilities: CVE, CVSS, patching and hardening
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


# ================================================================== task 1: The CVSS impact sub score
# Write cvss_iss(c, i, a) where each argument is one of "H", "L" or "N". Use the weights H = 0.56, L
# = 0.22, N = 0 and return ISS = 1 − (1 − C)(1 − I)(1 − A), rounded to 4 decimal places.
# Why it works: The product form means a second high impact adds less than the first: one H gives
# 0.56, two give 0.8064, three give 0.9148.

def cvss_iss(c, i, a):
    w = {"H": 0.56, "L": 0.22, "N": 0.0}
    return round(1 - (1 - w[c]) * (1 - w[i]) * (1 - w[a]), 4)


# ================================================================== task 2: The CVSS Roundup function
# Write roundup(x) that returns the smallest number with one decimal place that is greater than or
# equal to x, as CVSS v3.1 defines it. Work on integers to avoid floating point noise: multiply by
# 100000 and round, and if the result is a multiple of 10000 return it divided by 100000, otherwise
# return (floor(i / 10000) + 1) / 10.
# Why it works: The last test shows why: 4.000001 rounds to 400000 at five decimals, so it stays
# 4.0. A plain math.ceil(x * 10) / 10 would give 4.1, and earlier CVSS calculators disagreed on such
# cases.

import math

def roundup(x):
    i = round(x * 100000)
    if i % 10000 == 0:
        return i / 100000.0
    return (math.floor(i / 10000) + 1) / 10.0


# ================================================================== task 3: A full CVSS v3.1 base scorer
# Write cvss31(vector) for a vector such as "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H". Use the
# weights from the lesson (remember that PR depends on scope), compute ISS, Impact, Exploitability
# and the base score with Roundup, and return the base score as a float.
# Why it works: Compare your answers with the FIRST online calculator. The no impact case returns
# 0.0 before the exploitability is even used, as the specification says.

import math

def roundup(x):
    i = round(x * 100000)
    return i / 100000.0 if i % 10000 == 0 else (math.floor(i / 10000) + 1) / 10.0

def cvss31(vector):
    m = dict(part.split(":") for part in vector.split("/")[1:])
    changed = m["S"] == "C"
    av = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}[m["AV"]]
    ac = {"L": 0.77, "H": 0.44}[m["AC"]]
    pr = {"N": 0.85, "L": 0.68 if changed else 0.62, "H": 0.5 if changed else 0.27}[m["PR"]]
    ui = {"N": 0.85, "R": 0.62}[m["UI"]]
    w = {"H": 0.56, "L": 0.22, "N": 0.0}
    iss = 1 - (1 - w[m["C"]]) * (1 - w[m["I"]]) * (1 - w[m["A"]])
    impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15 if changed else 6.42 * iss
    if impact <= 0:
        return 0.0
    exploit = 8.22 * av * ac * pr * ui
    total = 1.08 * (impact + exploit) if changed else impact + exploit
    return roundup(min(total, 10))


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: The CVSS impact sub score", [('cvss_iss("H", "H", "H")', 0.9148), ('cvss_iss("H", "N", "N")', 0.56), ('cvss_iss("L", "L", "N")', 0.3916), ('cvss_iss("N", "N", "N")', 0.0)]))
    results.append(check("Task 2: The CVSS Roundup function", [('roundup(4.02)', 4.1), ('roundup(4.0)', 4.0), ('roundup(7.4822)', 7.5), ('roundup(9.7601)', 9.8), ('roundup(4.000001)', 4.0)]))
    results.append(check("Task 3: A full CVSS v3.1 base scorer", [('cvss31("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")', 9.8), ('cvss31("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H")', 10.0), ('cvss31("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N")', 7.5), ('cvss31("CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H")', 7.8), ('cvss31("CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N")', 6.1), ('cvss31("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N")', 0.0)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
