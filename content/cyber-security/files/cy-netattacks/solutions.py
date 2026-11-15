# 1.1 Network attacks and defences: spoofing, floods, scans and poisoning
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


# ================================================================== task 1: Half open connections in a SYN flood
# Write half_open(rate, timeout, backlog) that returns how many half open connections a server holds
# in the steady state: rate × timeout, but never more than the backlog.
# Why it works: When the result equals the backlog, new SYNs are dropped unless SYN cookies are on.

def half_open(rate, timeout, backlog):
    return min(rate * timeout, backlog)


# ================================================================== task 2: Detect ARP spoofing
# Write arp_changes(replies). replies is a list of [ip, mac] pairs in the order they arrived. Keep a
# cache, and return the list of IP addresses whose MAC changed, each IP once, in the order the first
# change happened.
# Why it works: A repeated identical reply is normal. Only a change of MAC for the same IP is
# suspicious, and a real network card swap also triggers it, so alerts need a human look.

def arp_changes(replies):
    cache, changed = {}, []
    for ip, mac in replies:
        if ip in cache and cache[ip] != mac and ip not in changed:
            changed.append(ip)
        cache[ip] = mac
    return changed


# ================================================================== task 3: A sliding window port scan detector
# Write scan_alert(log, window, limit). log is a list of [source, port, time] entries sorted by
# time. Return a sorted list of the sources that touch more than limit distinct ports within any
# period of window seconds (times t with start ≤ t < start + window, where start is the time of one
# of that source’s entries).
# Why it works: Slow scans spread probes over hours to slip under such windows, which is why
# detectors also keep longer term counts per source.

def scan_alert(log, window, limit):
    by_source = {}
    for src, port, t in log:
        by_source.setdefault(src, []).append((t, port))
    found = []
    for src, events in by_source.items():
        for start, port in events:
            ports = {p for t, p in events if start <= t < start + window}
            if len(ports) > limit:
                found.append(src)
                break
    return sorted(found)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Half open connections in a SYN flood", [('half_open(50, 30, 1024)', 1024), ('half_open(30, 30, 1024)', 900), ('half_open(0, 30, 1024)', 0)]))
    results.append(check("Task 2: Detect ARP spoofing", [('arp_changes([["10.0.0.1", "aa"], ["10.0.0.5", "bb"], ["10.0.0.1", "cc"], ["10.0.0.5", "cc"], ["10.0.0.1", "dd"]])', ['10.0.0.1', '10.0.0.5']), ('arp_changes([["10.0.0.1", "aa"], ["10.0.0.1", "aa"]])', []), ('arp_changes([])', [])]))
    results.append(check("Task 3: A sliding window port scan detector", [('scan_alert([["a", p, p] for p in range(20)], 10, 5)', ['a']), ('scan_alert([["a", p, 100 * p] for p in range(20)], 10, 5)', []), ('scan_alert([["b", 80, 1], ["b", 80, 2], ["c", 22, 1], ["c", 23, 2], ["c", 25, 3]], 60, 2)', ['c'])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
