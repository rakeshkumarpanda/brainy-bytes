# 4.3 lambda, map, filter and comprehensions
# Practice tasks. Fill in each function, then run this file.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


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


# ================================================================== task 1: Pass or fail labels
# Write labels(marks) that returns a list with "pass" for each mark of 40 or more and "fail" for the
# rest, using one list comprehension.
# Hint: The if-else goes before for: [a if test else b for m in marks].

def labels(marks):
    # your code here
    pass


# ================================================================== task 2: Top scorers
# Write top_scorers(scores, k). scores is a dict from name to mark. Return the names of the k best
# students, best first. Equal marks go in alphabetical order.
# Hint: Sort the names with key=lambda name: (-scores[name], name), then slice the first k.

def top_scorers(scores, k):
    # your code here
    pass


# ================================================================== task 3: Words grouped by length
# Write by_length(words) that returns a dict from each word length to a sorted list of the different
# words with that length. Use comprehensions.
# Hint: First make the set of lengths. Then, for each length n, a sorted generator of the words of
# that length.

def by_length(words):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Pass or fail labels", [('labels([72, 39, 40])', ['pass', 'fail', 'pass']), ('labels([])', [])]))
    results.append(check("Task 2: Top scorers", [('top_scorers({"Asha": 88, "Ravi": 72, "Meera": 95, "John": 88}, 3)', ['Meera', 'Asha', 'John']), ('top_scorers({"A": 1}, 5)', ['A']), ('top_scorers({}, 2)', [])]))
    results.append(check("Task 3: Words grouped by length", [('by_length(["fig", "kiwi", "pear", "fig", "plum", "apple"])', {3: ['fig'], 4: ['kiwi', 'pear', 'plum'], 5: ['apple']}), ('by_length([])', {})]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
