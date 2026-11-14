# 3.3 Explainability and fairness
# Model solutions. Try practice.py first.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
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


# ================================================================== task 1: Permutation importance from scores
# Write perm_importance(base, shuffled). base is the test score of the model and shuffled a list of
# scores after shuffling one feature several times. Return the mean drop, base minus the mean of
# shuffled, rounded to 3 decimals.
# Why it works: A negative result means shuffling made the score slightly better by chance, so the
# feature is useless. Real tools report the spread across shuffles too.

def perm_importance(base, shuffled):
    return round(base - sum(shuffled) / len(shuffled) + 0.0, 3)


# ================================================================== task 2: Exact Shapley values for two features
# Write shapley_two(v0, v1, v2, v12). The arguments are the value with no features known, with only
# feature 1, with only feature 2, and with both. Return a tuple (φ1, φ2), each rounded to 4
# decimals, by averaging what each feature adds over the two orders.
# Why it works: Check the efficiency property: v0 + φ1 + φ2 always equals v12.

def shapley_two(v0, v1, v2, v12):
    phi1 = ((v1 - v0) + (v12 - v2)) / 2
    phi2 = ((v2 - v0) + (v12 - v1)) / 2
    return (round(phi1 + 0.0, 4), round(phi2 + 0.0, 4))


# ================================================================== task 3: Disparate impact by group
# Write disparate_impact(approve, group). approve is a list of 0 and 1 decisions and group the group
# label of each person. Compute the approval rate of every group and return the lowest rate divided
# by the highest, rounded to 3 decimals.
# Why it works: Taking the lowest over the highest rate works for any number of groups. A result
# below 0.8 fails the four fifths rule.

def disparate_impact(approve, group):
    totals, yes = {}, {}
    for a, g in zip(approve, group):
        totals[g] = totals.get(g, 0) + 1
        yes[g] = yes.get(g, 0) + a
    rates = [yes[g] / totals[g] for g in totals]
    return round(min(rates) / max(rates), 3)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Permutation importance from scores", [('perm_importance(0.9, [0.8, 0.7])', 0.15), ('perm_importance(0.9, [0.9, 0.9, 0.9])', 0.0), ('perm_importance(0.5, [0.6])', -0.1), ('perm_importance(0.936, [0.77, 0.76, 0.768])', 0.17)]))
    results.append(check("Task 2: Exact Shapley values for two features", [('shapley_two(0.4, 0.6, 0.5, 0.9)', (0.3, 0.2)), ('shapley_two(0, 1, 1, 2)', (1.0, 1.0)), ('shapley_two(0.5, 0.5, 0.5, 0.5)', (0.0, 0.0)), ('shapley_two(0.45, 0.3, 0.2, 0.1)', (-0.125, -0.225))]))
    results.append(check("Task 3: Disparate impact by group", [("disparate_impact([1, 1, 0, 1, 0, 0], ['A', 'A', 'A', 'B', 'B', 'B'])", 0.5), ("disparate_impact([1, 0, 1, 0], ['A', 'A', 'B', 'B'])", 1.0), ("disparate_impact([1, 1, 1, 1, 0, 1, 0, 0], ['A', 'A', 'A', 'A', 'B', 'B', 'B', 'B'])", 0.25), ("disparate_impact([1, 0, 1, 1, 1, 0], ['A', 'A', 'B', 'B', 'C', 'C'])", 0.5)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
