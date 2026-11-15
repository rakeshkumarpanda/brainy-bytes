# 2.2 Networks for security: layers, addresses, subnets, TCP and DNS
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


# ================================================================== task 1: Network address of an IP and prefix
# Write network(ip, prefix). ip is text such as "192.168.10.77" and prefix a number from 1 to 32.
# Return the network address as text, by setting every host bit to 0. Do not use the ipaddress
# module.
# Hint: Turn the four numbers into one 32 bit number, shift right by the host bits and back left
# (this clears them), then split into four bytes again.

def network(ip, prefix):
    # your code here
    pass


# ================================================================== task 2: Usable hosts in a subnet
# Write usable_hosts(prefix) that returns 2 to the power (32 minus prefix) minus 2. For /31 return 2
# and for /32 return 1, the two special cases.
# Hint: Handle 32 and 31 first, then use the formula.

def usable_hosts(prefix):
    # your code here
    pass


# ================================================================== task 3: Is this address private?
# Write is_private(ip) that returns True when the IPv4 address is in 10.0.0.0/8, 172.16.0.0/12 or
# 192.168.0.0/16, else False. Use the numbers only, no modules.
# Hint: Split into four numbers. Check the first byte, and for 172 also check that the second byte
# is from 16 to 31.

def is_private(ip):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Network address of an IP and prefix", [('network("192.168.10.77", 26)', '192.168.10.64'), ('network("10.1.5.200", 22)', '10.1.4.0'), ('network("8.8.8.8", 32)', '8.8.8.8'), ('network("172.31.9.9", 12)', '172.16.0.0')]))
    results.append(check("Task 2: Usable hosts in a subnet", [('usable_hosts(24)', 254), ('usable_hosts(26)', 62), ('usable_hosts(31)', 2), ('usable_hosts(32)', 1), ('usable_hosts(8)', 16777214)]))
    results.append(check("Task 3: Is this address private?", [('is_private("10.4.2.1")', True), ('is_private("172.20.0.9")', True), ('is_private("172.32.0.1")', False), ('is_private("192.168.1.1")', True), ('is_private("8.8.8.8")', False)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
