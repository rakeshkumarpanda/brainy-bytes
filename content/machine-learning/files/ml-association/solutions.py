# 3.2 Association rules and market basket analysis
# Model solutions. Try practice.py first.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn


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


# ================================================================== task 1: Support of an itemset
# Write support(baskets, items) that returns the share of baskets containing every item in items,
# rounded to 4 decimals.
# Why it works: Using sets makes the subset test one operator: need <= set(b).

def support(baskets, items):
    need = set(items)
    hits = sum(1 for b in baskets if need <= set(b))
    return round(hits / len(baskets), 4)


# ================================================================== task 2: Support, confidence and lift of a rule
# Write rule_stats(baskets, a, b) for the rule "if all of a then all of b". Return [support,
# confidence, lift], each rounded to 4 decimals.
# Why it works: In the first test a appears with b two times out of three, but b is in three of four
# baskets anyway, so the lift is below 1.

def rule_stats(baskets, a, b):
    n = len(baskets)
    sa = sum(1 for t in baskets if set(a) <= set(t)) / n
    sb = sum(1 for t in baskets if set(b) <= set(t)) / n
    sab = sum(1 for t in baskets if set(a) | set(b) <= set(t)) / n
    conf = sab / sa
    return [round(sab, 4), round(conf, 4), round(conf / sb, 4)]


# ================================================================== task 3: All frequent pairs
# Write frequent_pairs(baskets, min_count) that returns every pair of items [x, y] with x before y
# alphabetically that appears together in at least min_count baskets, as a sorted list.
# Why it works: Counting pairs basket by basket only touches pairs that actually occur, which is far
# cheaper than checking every possible pair against every basket.

from itertools import combinations


def frequent_pairs(baskets, min_count):
    counts = {}
    for b in baskets:
        for x, y in combinations(sorted(set(b)), 2):
            counts[(x, y)] = counts.get((x, y), 0) + 1
    return sorted([list(p) for p, c in counts.items() if c >= min_count])


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Support of an itemset", [('support([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], ["a", "b"])', 0.5), ('support([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], ["c"])', 0.5), ('support([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], ["a", "c"])', 0.25)]))
    results.append(check("Task 2: Support, confidence and lift of a rule", [('rule_stats([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], ["a"], ["b"])', [0.5, 0.6667, 0.8889]), ('rule_stats([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], ["c"], ["b"])', [0.5, 1.0, 1.3333])]))
    results.append(check("Task 3: All frequent pairs", [('frequent_pairs([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], 2)', [['a', 'b'], ['b', 'c']]), ('frequent_pairs([["bread", "milk"], ["bread", "butter", "milk"], ["bread", "butter"], ["milk", "tea"], ["bread", "butter", "jam"], ["bread", "milk", "butter"], ["tea", "biscuits"], ["bread", "jam"], ["milk", "biscuits", "tea"], ["bread", "butter", "milk", "jam"]], 3)', [['bread', 'butter'], ['bread', 'jam'], ['bread', 'milk'], ['butter', 'milk']])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
