# 1.2 Injection: SQL, blind SQL, commands, SSRF and paths
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


# ================================================================== task 1: A parameterised login
# The starter creates an in memory SQLite table users(name, pw). Write safe_login(name, pw) that
# returns True if a row matches both values and False otherwise, using a query with ? placeholders.
# The injection attempts in the tests must fail.
# Hint: Pass the values as a tuple in the second argument of execute.

import sqlite3

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE users (name TEXT, pw TEXT)")
db.execute("INSERT INTO users VALUES ('alice', 'h_7f3a'), ('bob', 'h_91cc')")

def safe_login(name, pw):
    # your code here
    pass


# ================================================================== task 2: Binary search over a yes or no oracle
# Write leak(oracle, lo, hi). oracle(m) returns True when the secret is greater than m. Find the
# secret in the range lo to hi with binary search and return [secret, questions], where questions is
# how many times you called the oracle.
# Hint: Keep lo and hi, ask about the middle, and move one end each time.

def leak(oracle, lo, hi):
    # your code here
    pass


# ================================================================== task 3: A safe file path
# Write safe_path(base, name) using posixpath. Join base and name, normalise the result, and return
# it if it is still inside base (use posixpath.commonpath). Otherwise return None.
# Hint: join, then normpath, then compare commonpath with base.

import posixpath

def safe_path(base, name):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A parameterised login", [('safe_login("bob", "h_91cc")', True), ('safe_login("bob", "wrong")', False), ('safe_login("alice\' --", "x")', False), ('safe_login("\' OR \'1\'=\'1", "\' OR \'1\'=\'1")', False)]))
    results.append(check("Task 2: Binary search over a yes or no oracle", [('leak(lambda m: 75 > m, 32, 126)', [75, 7]), ('leak(lambda m: 126 > m, 32, 126)', [126, 6]), ('leak(lambda m: 5 > m, 0, 9)', [5, 4]), ('leak(lambda m: 0 > m, 0, 0)', [0, 0])]))
    results.append(check("Task 3: A safe file path", [('safe_path("/srv/up", "a.pdf")', '/srv/up/a.pdf'), ('safe_path("/srv/up", "../../etc/passwd")', None), ('safe_path("/srv/up", "x/../a.pdf")', '/srv/up/a.pdf'), ('safe_path("/srv/up", "/etc/shadow")', None), ('safe_path("/srv/up", "../up2/a")', None)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
