# 3.2 Association rules and market basket analysis
# Practice tasks. Fill in each function, then run this file.
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
# Hint: A basket counts when the item set is a subset of it.

def support(baskets, items):
    # your code here
    pass


# ================================================================== task 2: Support, confidence and lift of a rule
# Write rule_stats(baskets, a, b) for the rule "if all of a then all of b". Return [support,
# confidence, lift], each rounded to 4 decimals.
# Hint: Compute the three supports, then combine them.

def rule_stats(baskets, a, b):
    # your code here
    pass


# ================================================================== task 3: All frequent pairs
# Write frequent_pairs(baskets, min_count) that returns every pair of items [x, y] with x before y
# alphabetically that appears together in at least min_count baskets, as a sorted list.
# Hint: For each basket, count every pair of its items once.

def frequent_pairs(baskets, min_count):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Support of an itemset", [('support([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], ["a", "b"])', 0.5), ('support([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], ["c"])', 0.5), ('support([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], ["a", "c"])', 0.25)]))
    results.append(check("Task 2: Support, confidence and lift of a rule", [('rule_stats([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], ["a"], ["b"])', [0.5, 0.6667, 0.8889]), ('rule_stats([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], ["c"], ["b"])', [0.5, 1.0, 1.3333])]))
    results.append(check("Task 3: All frequent pairs", [('frequent_pairs([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], 2)', [['a', 'b'], ['b', 'c']]), ('frequent_pairs([["bread", "milk"], ["bread", "butter", "milk"], ["bread", "butter"], ["milk", "tea"], ["bread", "butter", "jam"], ["bread", "milk", "butter"], ["tea", "biscuits"], ["bread", "jam"], ["milk", "biscuits", "tea"], ["bread", "butter", "milk", "jam"]], 3)', [['bread', 'butter'], ['bread', 'jam'], ['bread', 'milk'], ['butter', 'milk']])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
