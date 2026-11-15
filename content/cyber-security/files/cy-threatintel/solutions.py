# 2.1 Threat intelligence: knowing the attacker
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


# ================================================================== task 1: Count log lines that match indicators
# Write count_matches(lines, iocs) that returns how many lines contain at least one of the indicator
# strings.
# Why it works: Real SIEMs match on parsed fields, not raw text, so that an IP inside a longer
# number does not match by mistake.

def count_matches(lines, iocs):
    count = 0
    for line in lines:
        for ioc in iocs:
            if ioc in line:
                count += 1
                break
    return count


# ================================================================== task 2: ATT&amp;CK tactic coverage
# rules is a list of tactic names, one per rule (a tactic may repeat). Write tactic_coverage(rules,
# total=14) that returns the percent of tactics with at least one rule, rounded to 1 decimal.
# Why it works: Counting techniques gives a much harder and more honest picture, since a tactic can
# have dozens of techniques.

def tactic_coverage(rules, total=14):
    covered = len(set(rules))
    return round(covered / total * 100, 1)


# ================================================================== task 3: Bayes with likelihood ratios
# Write posterior(prior, ratios) that turns the prior probability into odds, multiplies by every
# likelihood ratio, turns the odds back into a probability and returns it rounded to 4 decimals.
# Why it works: Working in odds turns Bayes’ rule into plain multiplication, which is why analysts
# and spam filters like it.

def posterior(prior, ratios):
    odds = prior / (1 - prior)
    for ratio in ratios:
        odds = odds * ratio
    return round(odds / (1 + odds), 4)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Count log lines that match indicators", [('count_matches(["a 1.2.3.4", "b evil.example", "c ok"], ["1.2.3.4", "evil.example"])', 2), ('count_matches(["x 1.2.3.4 evil.example"], ["1.2.3.4", "evil.example"])', 1), ('count_matches([], ["1.2.3.4"])', 0), ('count_matches(["clean"], [])', 0)]))
    results.append(check("Task 2: ATT&amp;CK tactic coverage", [('tactic_coverage(["Execution", "Impact"])', 14.3), ('tactic_coverage(["Execution", "Execution"])', 7.1), ('tactic_coverage([])', 0.0), ('tactic_coverage(["A", "B", "C", "D"], total=4)', 100.0)]))
    results.append(check("Task 3: Bayes with likelihood ratios", [('posterior(0.2, [4])', 0.5), ('posterior(0.2, [4, 4])', 0.8), ('posterior(0.2, [4, 9, 1])', 0.9), ('posterior(0.01, [9])', 0.0833), ('posterior(0.5, [])', 0.5)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
