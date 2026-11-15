# 2.2 Cloud security: shared responsibility, identity, settings and keys
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


# ================================================================== task 1: Addresses in a CIDR block
# Write cidr_size(prefix) that returns how many IPv4 addresses a block with that prefix length has
# (0 to 32).
# Why it works: Real clouds reserve a few addresses in every subnet (AWS keeps 5), so usable
# addresses are slightly fewer.

def cidr_size(prefix):
    return 2 ** (32 - prefix)


# ================================================================== task 2: An IAM policy decision
# policy is a list of (effect, action, resource) where effect is "Allow" or "Deny" and patterns may
# use *. Write iam_decide(policy, action, resource) that returns "Deny" if any matching statement is
# a Deny, "Allow" if any matching statement is an Allow, and "Deny" otherwise. Use fnmatch for the
# patterns.
# Why it works: Real AWS evaluation also joins service control policies, permission boundaries and
# resource policies, but each still follows the explicit deny first rule.

from fnmatch import fnmatch

def iam_decide(policy, action, resource):
    allowed = False
    for effect, act, res in policy:
        if fnmatch(action, act) and fnmatch(resource, res):
            if effect == "Deny":
                return "Deny"
            allowed = True
    if allowed:
        return "Allow"
    return "Deny"


# ================================================================== task 3: Addresses that can reach admin ports
# rules is a list of (cidr, port). Write admin_exposure(rules) that returns how many distinct IPv4
# addresses can reach port 22 or 3389. Overlapping blocks must be counted once (hint:
# ipaddress.collapse_addresses).
# Why it works: CSPM tools do this across thousands of rules and also follow routes and peering,
# because a rule is only open if traffic can actually get there.

import ipaddress

def admin_exposure(rules):
    nets = []
    for cidr, port in rules:
        if port in (22, 3389):
            nets.append(ipaddress.ip_network(cidr))
    total = 0
    for net in ipaddress.collapse_addresses(nets):
        total += net.num_addresses
    return total


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Addresses in a CIDR block", [('cidr_size(24)', 256), ('cidr_size(32)', 1), ('cidr_size(20)', 4096), ('cidr_size(0)', 4294967296)]))
    results.append(check("Task 2: An IAM policy decision", [('iam_decide([("Allow", "s3:GetObject", "b/*")], "s3:GetObject", "b/x")', 'Allow'), ('iam_decide([("Allow", "s3:GetObject", "b/*"), ("Deny", "s3:*", "b/pay/*")], "s3:GetObject", "b/pay/n")', 'Deny'), ('iam_decide([("Allow", "s3:GetObject", "b/*")], "s3:DeleteObject", "b/x")', 'Deny'), ('iam_decide([], "s3:GetObject", "b/x")', 'Deny')]))
    results.append(check("Task 3: Addresses that can reach admin ports", [('admin_exposure([("10.0.0.0/24", 22), ("10.0.0.128/25", 22), ("203.0.113.0/28", 3389), ("0.0.0.0/0", 443)])', 272), ('admin_exposure([("0.0.0.0/0", 443)])', 0), ('admin_exposure([("10.0.0.0/25", 22), ("10.0.0.128/25", 3389)])', 256), ('admin_exposure([("0.0.0.0/0", 22)])', 4294967296)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
