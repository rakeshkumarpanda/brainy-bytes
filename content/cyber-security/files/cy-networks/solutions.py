# 2.2 Networks for security: layers, addresses, subnets, TCP and DNS
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


# ================================================================== task 1: Network address of an IP and prefix
# Write network(ip, prefix). ip is text such as "192.168.10.77" and prefix a number from 1 to 32.
# Return the network address as text, by setting every host bit to 0. Do not use the ipaddress
# module.
# Why it works: Shifting right then left is the same as AND with the mask. Firewalls and routers do
# exactly this comparison for every packet.

def network(ip, prefix):
    n = 0
    for part in ip.split("."):
        n = n * 256 + int(part)
    host_bits = 32 - prefix
    n = (n >> host_bits) << host_bits
    out = []
    for shift in [24, 16, 8, 0]:
        out.append(str((n >> shift) & 255))
    return ".".join(out)


# ================================================================== task 2: Usable hosts in a subnet
# Write usable_hosts(prefix) that returns 2 to the power (32 minus prefix) minus 2. For /31 return 2
# and for /32 return 1, the two special cases.
# Why it works: /31 links between two routers use both addresses (RFC 3021), and /32 names one host.
# Every other subnet loses two addresses to the network and broadcast.

def usable_hosts(prefix):
    if prefix == 32:
        return 1
    if prefix == 31:
        return 2
    return 2 ** (32 - prefix) - 2


# ================================================================== task 3: Is this address private?
# Write is_private(ip) that returns True when the IPv4 address is in 10.0.0.0/8, 172.16.0.0/12 or
# 192.168.0.0/16, else False. Use the numbers only, no modules.
# Why it works: Log analysts flag traffic where a private address appears on an internet facing
# interface, because private sources should never arrive from outside. That is a classic sign of
# spoofing.

def is_private(ip):
    a, b, c, d = [int(x) for x in ip.split(".")]
    if a == 10:
        return True
    if a == 172 and 16 <= b <= 31:
        return True
    if a == 192 and b == 168:
        return True
    return False


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Network address of an IP and prefix", [('network("192.168.10.77", 26)', '192.168.10.64'), ('network("10.1.5.200", 22)', '10.1.4.0'), ('network("8.8.8.8", 32)', '8.8.8.8'), ('network("172.31.9.9", 12)', '172.16.0.0')]))
    results.append(check("Task 2: Usable hosts in a subnet", [('usable_hosts(24)', 254), ('usable_hosts(26)', 62), ('usable_hosts(31)', 2), ('usable_hosts(32)', 1), ('usable_hosts(8)', 16777214)]))
    results.append(check("Task 3: Is this address private?", [('is_private("10.4.2.1")', True), ('is_private("172.20.0.9")', True), ('is_private("172.32.0.1")', False), ('is_private("192.168.1.1")', True), ('is_private("8.8.8.8")', False)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
