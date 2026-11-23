# 4.2 Mobile security: sandboxes, permissions, signing and the OWASP Mobile Top 10
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


# ================================================================== task 1: Flag unnecessary permissions
# Write extra(asked, needed) that returns a sorted list of permissions in asked that are not in
# needed.
# Why it works: App review teams and tools like the permission audit program do this at scale, then
# ask developers to justify every extra permission.

def extra(asked, needed):
    return sorted(set(asked) - set(needed))


# ================================================================== task 2: Check a certificate pin
# Write pin_ok(key_bytes, pins) that computes the base64 encoded SHA-256 of key_bytes and returns
# True if it is in the set pins.
# Why it works: The third test is the backup pin at work: the bank rotated to its backup key and the
# app kept working.

import base64
import hashlib

def pin_ok(key_bytes, pins):
    pin = base64.b64encode(hashlib.sha256(key_bytes).digest()).decode()
    return pin in pins


# ================================================================== task 3: How long does a brute force take?
# A phone allows free guesses with no delay, then makes every further guess wait delay seconds.
# Write worst_hours(digits, free, delay) that returns the worst case time in hours to try every PIN
# of that many digits, rounded to 1 decimal.
# Why it works: Even a 4 digit PIN takes days with a 30 second delay. Delays plus an optional wipe
# are what make short PINs workable on phones.

def worst_hours(digits, free, delay):
    total = 10 ** digits
    slow = max(0, total - free)
    return round(slow * delay / 3600, 1)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Flag unnecessary permissions", [('extra(["CAMERA", "READ_SMS", "READ_CONTACTS"], ["CAMERA"])', ['READ_CONTACTS', 'READ_SMS']), ('extra(["CAMERA"], ["CAMERA"])', []), ('extra([], ["INTERNET"])', [])]))
    results.append(check("Task 2: Check a certificate pin", [('pin_ok(b"bank", {base64.b64encode(hashlib.sha256(b"bank").digest()).decode()})', True), ('pin_ok(b"attacker", {base64.b64encode(hashlib.sha256(b"bank").digest()).decode()})', False), ('pin_ok(b"backup", {base64.b64encode(hashlib.sha256(b"bank").digest()).decode(), base64.b64encode(hashlib.sha256(b"backup").digest()).decode()})', True)]))
    results.append(check("Task 3: How long does a brute force take?", [('worst_hours(4, 5, 30)', 83.3), ('worst_hours(6, 9, 3600)', 999991.0), ('worst_hours(4, 10000, 30)', 0.0)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
