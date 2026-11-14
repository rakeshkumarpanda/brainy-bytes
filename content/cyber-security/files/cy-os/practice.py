# 2.1 Operating systems: users, permissions, processes and logs
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


# ================================================================== task 1: An octal digit to letters
# Write rwx(digit) that turns one octal digit (0 to 7) into its three letters, using "-" for a
# missing right. For example 5 gives "r-x".
# Hint: Test each bit with & 4, & 2 and & 1 and add a letter or a dash.

def rwx(digit):
    # your code here
    pass


# ================================================================== task 2: The Linux access decision
# Write allowed(is_owner, in_group, mode, bit). mode is a whole number such as 0o754, bit is 4
# (read), 2 (write) or 1 (execute). Use the owner digit if is_owner is True, else the group digit if
# in_group is True, else the other digit. Return True when that digit has the bit.
# Hint: The owner digit is (mode // 64) % 8, the group digit (mode // 8) % 8 and the other digit
# mode % 8. Pick only the first that matches.

def allowed(is_owner, in_group, mode, bit):
    # your code here
    pass


# ================================================================== task 3: Count failed logons per account
# Write suspects(events, limit). events is a list of [event_id, account] pairs. Count the 4625
# (failed logon) events per account and return a sorted list of the accounts with at least limit
# failures.
# Hint: Count only event 4625 in a dict, then keep the accounts whose count reaches the limit, and
# sort them.

def suspects(events, limit):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: An octal digit to letters", [('rwx(7)', 'rwx'), ('rwx(5)', 'r-x'), ('rwx(0)', '---'), ('rwx(6)', 'rw-')]))
    results.append(check("Task 2: The Linux access decision", [('allowed(True, True, 0o754, 2)', True), ('allowed(False, True, 0o754, 2)', False), ('allowed(False, True, 0o604, 4)', False), ('allowed(False, False, 0o604, 4)', True)]))
    results.append(check("Task 3: Count failed logons per account", [('suspects([[4625, "admin"], [4625, "admin"], [4624, "riya"], [4625, "riya"]], 2)', ['admin']), ('suspects([], 1)', []), ('suspects([[4625, "b"], [4625, "a"], [4625, "b"], [4625, "a"]], 2)', ['a', 'b'])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
