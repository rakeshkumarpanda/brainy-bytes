# 1.1 Logging, monitoring and the SIEM
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


# ================================================================== task 1: Parse an SSH log line
# Write parse_ssh(line). If the line contains Failed password for USER from IP or Accepted password
# for USER from IP, return a tuple (user, ip, outcome) where outcome is "failure" or "success".
# Otherwise return None.
# Why it works: Real SSH logs also have lines such as "Invalid user" and "Disconnected", so real
# parsers carry several patterns.

import re

def parse_ssh(line):
    match = re.search(r"(Failed|Accepted) password for (\S+) from (\S+)", line)
    if match is None:
        return None
    word, user, ip = match.groups()
    outcome = "failure" if word == "Failed" else "success"
    return (user, ip, outcome)


# ================================================================== task 2: A sliding window brute force rule
# events is a list of (minute, ip) failures in time order. Write window_alerts(events, n, w) that
# returns the list of IPs, in the order they first alert, that have at least n failures with minutes
# in the range minute − w < t ≤ minute at the moment of a failure. Each IP alerts at most once.
# Why it works: This simple version looks back over the whole list each time. A real SIEM keeps a
# queue per IP, as in the brute_rule program, so each event costs almost nothing.

def window_alerts(events, n, w):
    alerted = []
    for minute, ip in events:
        if ip in alerted:
            continue
        count = 0
        for t, other_ip in events:
            if other_ip == ip and minute - w < t <= minute:
                count += 1
        if count >= n:
            alerted.append(ip)
    return alerted


# ================================================================== task 3: Find the tampered line in a hash chained log
# Each record is [text, tag], where tag is the first 12 hex digits of SHA-256 of previous_tag + "|"
# + text and the first previous tag is "start". Write first_broken(records) that returns the line
# number (from 1) of the first record whose tag does not match, or None if all match. Use the stored
# tag as the previous tag for the next record.
# Why it works: Real systems use an HMAC with a secret key, so an intruder cannot simply recompute
# all the tags after a change.

import hashlib

def make_tag(prev, text):
    return hashlib.sha256((prev + "|" + text).encode()).hexdigest()[:12]

def first_broken(records):
    prev = "start"
    number = 1
    for text, stored in records:
        if make_tag(prev, text) != stored:
            return number
        prev = stored
        number += 1
    return None


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Parse an SSH log line", [('parse_ssh("Nov 15 09:12:04 web1 sshd[811]: Failed password for root from 203.0.113.9 port 52144 ssh2")', ('root', '203.0.113.9', 'failure')), ('parse_ssh("Nov 15 09:14:40 web1 sshd[815]: Accepted password for deploy from 10.0.0.5 port 50001 ssh2")', ('deploy', '10.0.0.5', 'success')), ('parse_ssh("Nov 15 09:20:00 web1 cron[90]: job started")', None)]))
    results.append(check("Task 2: A sliding window brute force rule", [('window_alerts([(10, "C"), (11, "C"), (11, "C"), (12, "C"), (12, "C")], 5, 5)', ['C']), ('window_alerts([(1, "B"), (7, "B"), (13, "B"), (19, "B"), (25, "B")], 5, 5)', []), ('window_alerts([(1, "B"), (7, "B"), (13, "B"), (19, "B"), (25, "B")], 5, 60)', ['B']), ('window_alerts([(1, "A"), (2, "B"), (2, "A"), (3, "B"), (3, "A")], 3, 5)', ['A'])]))
    results.append(check("Task 3: Find the tampered line in a hash chained log", [('first_broken([["a", make_tag("start", "a")], ["b", make_tag(make_tag("start", "a"), "b")]])', None), ('first_broken([["a", make_tag("start", "a")], ["B", make_tag(make_tag("start", "a"), "b")]])', 2), ('first_broken([["x", "000000000000"]])', 1), ('first_broken([])', None)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
