# 1.2 Risk in numbers: matrices, ALE, attack trees and continuity
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


# ================================================================== task 1: Annualised loss expectancy
# Write ale(asset_value, exposure_factor, aro) that returns the annualised loss expectancy: first
# the single loss expectancy (asset value times exposure factor), then times the yearly rate.
# Hint: Two multiplications: AV × EF gives the SLE, then SLE × ARO.

def ale(asset_value, exposure_factor, aro):
    # your code here
    pass


# ================================================================== task 2: Is the control worth it?
# Write control_value(ale_before, ale_after, cost) that returns a pair: the yearly value of the
# control (before minus after minus cost) and the word "buy" when the value is above 0, otherwise
# "skip".
# Hint: Work out the value first, then decide the word with one if.

def control_value(ale_before, ale_after, cost):
    # your code here
    pass


# ================================================================== task 3: The cheapest attack in an attack tree
# Write cheapest(node). A node is either a number (the cost of one action) or a list whose first
# item is "AND" or "OR" followed by its children. An AND node costs the sum of its children, an OR
# node costs its cheapest child. For example ["OR", ["AND", 1, 5], 3] costs 3.
# Hint: A number is its own cost. For a list, work out each child with the same function
# (recursion), then add for AND or take the smallest for OR.

def cheapest(node):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Annualised loss expectancy", [('ale(2000000, 0.4, 0.5)', 400000.0), ('ale(100, 1, 3)', 300), ('ale(500000, 0.2, 0)', 0.0)]))
    results.append(check("Task 2: Is the control worth it?", [('control_value(400000, 80000, 60000)', [260000, 'buy']), ('control_value(10000, 9000, 5000)', [-4000, 'skip']), ('control_value(100, 50, 50)', [0, 'skip'])]))
    results.append(check("Task 3: The cheapest attack in an attack tree", [('cheapest(["OR", ["AND", 1, 5], 3])', 3), ('cheapest(7)', 7), ('cheapest(["OR", ["AND", 1, 5], 3, 20, ["AND", 4, 50]])', 3), ('cheapest(["AND", ["OR", 9, 4], ["OR", 2, ["AND", 1, 1]]])', 6)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
