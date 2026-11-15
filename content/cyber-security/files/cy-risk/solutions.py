# 1.2 Risk in numbers: matrices, ALE, attack trees and continuity
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


# ================================================================== task 1: Annualised loss expectancy
# Write ale(asset_value, exposure_factor, aro) that returns the annualised loss expectancy: first
# the single loss expectancy (asset value times exposure factor), then times the yearly rate.
# Why it works: ALE puts every risk on a money scale per year, so a manager can compare risks of
# very different kinds.

def ale(asset_value, exposure_factor, aro):
    sle = asset_value * exposure_factor
    return sle * aro


# ================================================================== task 2: Is the control worth it?
# Write control_value(ale_before, ale_after, cost) that returns a pair: the yearly value of the
# control (before minus after minus cost) and the word "buy" when the value is above 0, otherwise
# "skip".
# Why it works: A control that costs more than the loss it removes is not worth it, however
# impressive it sounds. This simple test stops wasteful spending.

def control_value(ale_before, ale_after, cost):
    value = ale_before - ale_after - cost
    if value > 0:
        return [value, "buy"]
    return [value, "skip"]


# ================================================================== task 3: The cheapest attack in an attack tree
# Write cheapest(node). A node is either a number (the cost of one action) or a list whose first
# item is "AND" or "OR" followed by its children. An AND node costs the sum of its children, an OR
# node costs its cheapest child. For example ["OR", ["AND", 1, 5], 3] costs 3.
# Why it works: This bottom up rule is exactly how attack tree tools rank routes. The same recursion
# with other rules gives the chance of success or the time an attack needs.

def cheapest(node):
    if not isinstance(node, list):
        return node
    kind = node[0]
    costs = []
    for child in node[1:]:
        costs.append(cheapest(child))
    if kind == "AND":
        return sum(costs)
    return min(costs)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Annualised loss expectancy", [('ale(2000000, 0.4, 0.5)', 400000.0), ('ale(100, 1, 3)', 300), ('ale(500000, 0.2, 0)', 0.0)]))
    results.append(check("Task 2: Is the control worth it?", [('control_value(400000, 80000, 60000)', [260000, 'buy']), ('control_value(10000, 9000, 5000)', [-4000, 'skip']), ('control_value(100, 50, 50)', [0, 'skip'])]))
    results.append(check("Task 3: The cheapest attack in an attack tree", [('cheapest(["OR", ["AND", 1, 5], 3])', 3), ('cheapest(7)', 7), ('cheapest(["OR", ["AND", 1, 5], 3, 20, ["AND", 4, 50]])', 3), ('cheapest(["AND", ["OR", 9, 4], ["OR", 2, ["AND", 1, 1]]])', 6)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
