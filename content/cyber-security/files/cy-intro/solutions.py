# 1.1 What cybersecurity is: goals, threats and layers
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


# ================================================================== task 1: Chance an attack passes every layer
# Write breach_chance(miss). It gets a list of miss chances, one per layer, and returns the chance
# an attack passes all of them (their product). An empty list means there is no defence, so return
# 1.
# Why it works: This is the defence in depth formula. It assumes the layers fail independently, so
# in real life it is the best case.

def breach_chance(miss):
    chance = 1
    for m in miss:
        chance = chance * m
    return chance


# ================================================================== task 2: At least one success in many tries
# Write at_least_one(p, n) that returns the chance that at least one of n independent tries
# succeeds, when each succeeds with chance p. Round the answer to 4 decimal places.
# Why it works: Attackers only need one success. This formula shows why a big company almost always
# has someone who clicks a phishing link.

def at_least_one(p, n):
    nobody = (1 - p) ** n
    return round(1 - nobody, 4)


# ================================================================== task 3: Which goals does an incident break?
# Write goals_broken(read, changed, down). The three inputs are True or False: was secret data read,
# was data changed, was the service down. Return a list of the broken goals in the order "C", "I",
# "A". For example, data read and service down gives ["C", "A"].
# Why it works: Analysts tag every incident with the goals it broke. This decides who must be told
# (a confidentiality breach of personal data often must be reported by law) and which controls to
# improve.

def goals_broken(read, changed, down):
    broken = []
    if read:
        broken.append("C")
    if changed:
        broken.append("I")
    if down:
        broken.append("A")
    return broken


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Chance an attack passes every layer", [('breach_chance([0.5, 0.2])', 0.1), ('breach_chance([])', 1), ('round(breach_chance([0.3, 0.5, 0.4, 0.1]), 6)', 0.006)]))
    results.append(check("Task 2: At least one success in many tries", [('at_least_one(0.1, 2)', 0.19), ('at_least_one(0.03, 100)', 0.9524), ('at_least_one(0.5, 0)', 0.0)]))
    results.append(check("Task 3: Which goals does an incident break?", [('goals_broken(True, False, True)', ['C', 'A']), ('goals_broken(False, False, False)', []), ('goals_broken(True, True, True)', ['C', 'I', 'A'])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
