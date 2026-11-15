# 2.2 Secure development: threat models, scanners, fuzzing and the supply chain
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


# ================================================================== task 1: STRIDE per element
# Write stride_letters(kind) that returns the STRIDE letters for a data flow diagram element:
# "external entity" gives "SR", "process" gives "STRIDE", "data store" gives "TRID" and "data flow"
# gives "TID". Return "" for anything else.
# Why it works: Counting len(stride_letters(k)) over all elements gives the number of threats to
# review, as in the calculations above.

def stride_letters(kind):
    table = {"external entity": "SR", "process": "STRIDE", "data store": "TRID", "data flow": "TID"}
    return table.get(kind, "")


# ================================================================== task 2: Cheapest attack in an attack tree
# A tree is a list: ["LEAF", cost], ["OR", [children]] or ["AND", [children]]. Write tree_cost(node)
# that returns the attacker’s cheapest cost: a leaf’s cost, the minimum over an OR node’s children,
# or the sum over an AND node’s children.
# Why it works: The last test is the chapter’s tree: the backup path at cost 100 is the cheapest, so
# that is where to defend first.

def tree_cost(node):
    kind = node[0]
    if kind == "LEAF":
        return node[1]
    costs = [tree_cost(child) for child in node[1]]
    return min(costs) if kind == "OR" else sum(costs)


# ================================================================== task 3: Entropy for secret scanning
# Write str_entropy(s) that returns the Shannon entropy of the characters of s in bits per
# character, H = −Σ p log2 p, rounded to 2 decimal places. Return 0.0 for an empty string.
# Why it works: Scanners combine this with length, character classes and known prefixes, because
# short or structured strings can score high by chance.

import math
from collections import Counter

def str_entropy(s):
    if not s:
        return 0.0
    n = len(s)
    h = -sum(c / n * math.log2(c / n) for c in Counter(s).values())
    return round(abs(h), 2)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: STRIDE per element", [('stride_letters("process")', 'STRIDE'), ('stride_letters("data flow")', 'TID'), ('stride_letters("external entity")', 'SR'), ('stride_letters("data store")', 'TRID'), ('stride_letters("cloud")', '')]))
    results.append(check("Task 2: Cheapest attack in an attack tree", [('tree_cost(["LEAF", 7])', 7), ('tree_cost(["OR", [["LEAF", 3000], ["LEAF", 500], ["LEAF", 100]]])', 100), ('tree_cost(["AND", [["LEAF", 2000], ["LEAF", 1000]]])', 3000), ('tree_cost(["OR", [["AND", [["LEAF", 2000], ["LEAF", 1000]]], ["LEAF", 500], ["AND", [["LEAF", 100], ["LEAF", 0]]]]])', 100)]))
    results.append(check("Task 3: Entropy for secret scanning", [('str_entropy("aaaa")', 0.0), ('str_entropy("abcdefgh")', 3.0), ('str_entropy("q8Zr3VbN1xTt6YwP0kLm9sDf2GhJ4cXe")', 5.0), ('str_entropy("")', 0.0), ('str_entropy("aab")', 0.92)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
