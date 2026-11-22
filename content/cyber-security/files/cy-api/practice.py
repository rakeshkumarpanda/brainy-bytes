# 4.4 API security: BOLA, rate limits, mass assignment and the OWASP API Top 10
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


# ================================================================== task 1: Add an owner check
# orders maps an order id to a dict with an "owner" key. Write get_order(orders, caller, oid) that
# returns (200, order) when the order exists and belongs to caller, and (404, None) otherwise,
# including when it belongs to someone else.
# Hint: Look up the order with .get, then compare its owner with caller.

def get_order(orders, caller, oid):
    # your code here
    pass


# ================================================================== task 2: A token bucket limiter
# Write run_bucket(capacity, rate, times). The bucket starts full. times is a sorted list of request
# times in seconds. Before each request, add rate × (time since the last request) tokens, capped at
# capacity. If at least 1 token is left, spend it and record True, else record False. Return the
# list of results.
# Hint: Keep tokens and the last time. Refill by rate times the gap, cap it, then spend one if you
# can.

def run_bucket(capacity, rate, times):
    # your code here
    pass


# ================================================================== task 3: Allow list for writable fields
# Write apply_patch(record, body, writable) that returns a pair (new_record, ignored). new_record is
# a copy of record with only the keys in writable updated from body. ignored is the sorted list of
# body keys that were not writable. Do not change record itself.
# Hint: Copy with dict(record), loop over body, and split keys into written and ignored.

def apply_patch(record, body, writable):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Add an owner check", [('get_order({1: {"owner": "a"}, 2: {"owner": "b"}}, "a", 1)', (200, {'owner': 'a'})), ('get_order({1: {"owner": "a"}, 2: {"owner": "b"}}, "a", 2)', (404, None)), ('get_order({}, "a", 9)', (404, None))]))
    results.append(check("Task 2: A token bucket limiter", [('run_bucket(2, 1.0, [0, 0, 0, 1, 1])', [True, True, False, True, False]), ('run_bucket(1, 0.5, [0, 1, 2, 3, 4])', [True, False, True, False, True]), ('run_bucket(3, 0, [])', [])]))
    results.append(check("Task 3: Allow list for writable fields", [('apply_patch({"name": "a", "role": "user"}, {"name": "b", "role": "admin"}, {"name"})', ({'name': 'b', 'role': 'user'}, ['role'])), ('apply_patch({"x": 1}, {}, {"x"})', ({'x': 1}, [])), ('apply_patch({"e": "o"}, {"e": "n", "credits": 9, "admin": True}, {"e"})', ({'e': 'n'}, ['admin', 'credits']))]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
