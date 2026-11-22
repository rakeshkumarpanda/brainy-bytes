# 4.3 IoT and industrial control security: Mirai, Modbus, Purdue and Stuxnet
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


# ================================================================== task 1: Find devices with factory passwords
# devices is a list of (name, user, password) tuples and defaults is a set of (user, password)
# pairs. Write weak(devices, defaults) that returns the sorted list of names whose login is in
# defaults.
# Why it works: The third test matters: passwords are case sensitive, so "Admin" is not "admin".
# Real audits also try common variants, because attackers do.

def weak(devices, defaults):
    return sorted(name for name, user, pw in devices if (user, pw) in defaults)


# ================================================================== task 2: Name a Modbus function code
# Write func_name(frame_hex). frame_hex is a Modbus TCP frame as a hex string (spaces allowed). The
# function code is byte 8 (index 7). Return "read" for codes 1, 2, 3, 4, "write" for 5, 6, 15, 16,
# and "other" otherwise.
# Why it works: Industrial firewalls and monitors make exactly this decision on every packet: reads
# are usually fine from many places, writes only from the operator stations.

def func_name(frame_hex):
    data = bytes.fromhex(frame_hex.replace(" ", ""))
    code = data[7]
    if code in (1, 2, 3, 4):
        return "read"
    if code in (5, 6, 15, 16):
        return "write"
    return "other"


# ================================================================== task 3: Is there an allowed path into the plant?
# allow is a set of (from, to) pairs. Write reachable(allow, start, goal) that returns True if goal
# can be reached from start by following allowed pairs (breadth first search).
# Why it works: Auditors run this kind of search over real firewall rules to find forgotten paths
# from the office network into control systems.

from collections import deque

def reachable(allow, start, goal):
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == goal:
            return True
        for a, b in allow:
            if a == node and b not in seen:
                seen.add(b)
                queue.append(b)
    return False


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Find devices with factory passwords", [('weak([("cam", "admin", "admin"), ("dvr", "root", "xc3511"), ("tv", "u", "Qx!9")], {("admin", "admin"), ("root", "xc3511")})', ['cam', 'dvr']), ('weak([], {("a", "b")})', []), ('weak([("x", "admin", "Admin")], {("admin", "admin")})', [])]))
    results.append(check("Task 2: Name a Modbus function code", [('func_name("002A 0000 0006 01 05 0010 FF00")', 'write'), ('func_name("0001 0000 0006 01 03 0000 000A")', 'read'), ('func_name("0001 0000 0002 01 2B")', 'other')]))
    results.append(check("Task 3: Is there an allowed path into the plant?", [('reachable({("office", "dmz"), ("dmz", "hmi"), ("hmi", "plc")}, "office", "plc")', True), ('reachable({("office", "dmz"), ("hmi", "plc")}, "office", "plc")', False), ('reachable(set(), "plc", "plc")', True)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
