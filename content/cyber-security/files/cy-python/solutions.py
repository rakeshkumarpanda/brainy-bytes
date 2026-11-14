# 2.3 Python for security: bytes, hashes, logs, packets and safe code
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


# ================================================================== task 1: Text to hex
# Write to_hex(text) that returns the UTF-8 bytes of the text as a lower case hex string with no
# spaces. For example "Hi" gives "4869".
# Why it works: Hashes, keys and packet dumps are shown as hex. Remember that text must become bytes
# before any hash or hex step.

def to_hex(text):
    data = text.encode("utf-8")
    return data.hex()


# ================================================================== task 2: Count failed logins per address
# Write failed_ips(lines, limit). lines is a list of sshd log lines. Count lines that contain
# "Failed password for", with or without "invalid user", and capture the address after "from".
# Return a sorted list of addresses with at least limit failures.
# Why it works: The first test only passes if the "invalid user" line is counted, which is the trap
# from the lesson.

import re

def failed_ips(lines, limit):
    pattern = re.compile(r"Failed password for (?:invalid user )?\S+ from ([\d.]+)")
    counts = {}
    for line in lines:
        m = pattern.search(line)
        if m:
            ip = m.group(1)
            counts[ip] = counts.get(ip, 0) + 1
    found = []
    for ip in counts:
        if counts[ip] >= limit:
            found.append(ip)
    return sorted(found)


# ================================================================== task 3: A safe path check
# Write is_safe(base, name). Join base and name with posixpath.join, normalise with
# posixpath.normpath, and return True only when the result equals base or starts with base + "/".
# Why it works: Joining with an absolute name such as /etc/shadow throws away the base completely,
# which is why the check must come after the join.

import posixpath

def is_safe(base, name):
    full = posixpath.normpath(posixpath.join(base, name))
    return full == base or full.startswith(base + "/")


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Text to hex", [('to_hex("Hi")', '4869'), ('to_hex("é")', 'c3a9'), ('to_hex("")', ''), ('to_hex("A1")', '4131')]))
    results.append(check("Task 2: Count failed logins per address", [('failed_ips(["Failed password for root from 1.2.3.4 port 1", "Failed password for invalid user x from 1.2.3.4 port 2", "Accepted password for a from 5.6.7.8 port 3"], 2)', ['1.2.3.4']), ('failed_ips([], 1)', []), ('failed_ips(["Failed password for a from 9.9.9.9 port 1", "Failed password for b from 8.8.8.8 port 1"], 1)', ['8.8.8.8', '9.9.9.9'])]))
    results.append(check("Task 3: A safe path check", [('is_safe("/srv/files", "a.txt")', True), ('is_safe("/srv/files", "../../etc/passwd")', False), ('is_safe("/srv/files", "/etc/shadow")', False), ('is_safe("/srv/files", "x/../../files2/y")', False), ('is_safe("/srv/files", "x/../y.txt")', True)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
