# 1.2 Firewalls, intrusion detection, VPNs and zero trust
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


# ================================================================== task 1: A first match port filter
# Write first_match(rules, port). Each rule is [port, action], where port is a number or the text
# "any". Return the action of the first rule that matches the port, or "deny" if none matches.
# Why it works: The third test shows shadowing: the deny for port 23 is never reached because "any"
# matches first.

def first_match(rules, port):
    for rule_port, action in rules:
        if rule_port == "any" or rule_port == port:
            return action
    return "deny"


# ================================================================== task 2: A packet filter with networks
# Write cidr_filter(rules, src, port). Each rule is [action, network, port] such as ["allow",
# "10.0.0.0/8", 22]. A rule matches if src is inside the network and the port is equal. Return the
# first matching action, or "deny". Use ipaddress.ip_address and ipaddress.ip_network.
# Why it works: 0.0.0.0/0 contains every IPv4 address, so it is the usual way to write "from
# anyone".

from ipaddress import ip_address, ip_network

def cidr_filter(rules, src, port):
    for action, net, rule_port in rules:
        if ip_address(src) in ip_network(net) and port == rule_port:
            return action
    return "deny"


# ================================================================== task 3: Z score anomaly alerts
# Write z_alerts(counts, k) that returns the list of positions i where |counts[i] − mean| / sd is
# greater than k. Use the population standard deviation (statistics.pstdev). If the standard
# deviation is 0, return an empty list.
# Why it works: Including the attack in the data raises the mean and sd, which can hide it. Real
# detectors learn the baseline from clean training data, as the animation does.

import statistics

def z_alerts(counts, k):
    mean = statistics.mean(counts)
    sd = statistics.pstdev(counts)
    if sd == 0:
        return []
    return [i for i, x in enumerate(counts) if abs(x - mean) / sd > k]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A first match port filter", [('first_match([[443, "allow"], [23, "deny"]], 443)', 'allow'), ('first_match([[443, "allow"], [23, "deny"]], 22)', 'deny'), ('first_match([["any", "allow"], [23, "deny"]], 23)', 'allow')]))
    results.append(check("Task 2: A packet filter with networks", [('cidr_filter([["allow", "10.0.0.0/8", 22]], "10.1.2.3", 22)', 'allow'), ('cidr_filter([["allow", "10.0.0.0/8", 22]], "203.0.113.5", 22)', 'deny'), ('cidr_filter([["deny", "192.168.1.0/24", 80], ["allow", "0.0.0.0/0", 80]], "192.168.1.9", 80)', 'deny'), ('cidr_filter([["deny", "192.168.1.0/24", 80], ["allow", "0.0.0.0/0", 80]], "192.168.2.9", 80)', 'allow')]))
    results.append(check("Task 3: Z score anomaly alerts", [('z_alerts([4, 5, 3, 6, 4, 5, 4, 3, 6, 4, 40], 3)', [10]), ('z_alerts([1, 2, 3, 4, 5], 1)', [0, 4]), ('z_alerts([5, 5, 5, 5], 2)', [])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
