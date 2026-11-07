# 3.3 Tuples and sets: fixed records and unique items
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


# ================================================================== task 1: Common friends
# Write common_friends(a, b) where a and b are lists of names. Return a sorted list of the names
# that are in both, each name once.
# Hint: Turn both lists into sets and use &. Then sorted() gives a list.

def common_friends(a, b):
    # your code here
    pass


# ================================================================== task 2: First repeated item
# Write first_repeat(items) that returns the first item that appears for the second time when you
# read from the left, or None if nothing repeats.
# Hint: Walk left to right with a set of items seen so far. The first item already in the set is the
# answer.

def first_repeat(items):
    # your code here
    pass


# ================================================================== task 3: All subsets of a small set
# Write all_subsets(items) that takes a list of different items and returns a list of all its
# subsets, each one as a sorted tuple, and the whole list sorted. [1, 2] gives [(), (1,), (1, 2),
# (2,)].
# Hint: Start with [[]]. For each item, make a copy of every subset so far with the item added. The
# count doubles each time.

def all_subsets(items):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Common friends", [('common_friends(["Asha", "Ravi", "Asha"], ["Ravi", "John", "Asha"])', ['Asha', 'Ravi']), ('common_friends(["x"], ["y"])', []), ('common_friends([], ["y"])', [])]))
    results.append(check("Task 2: First repeated item", [('first_repeat([3, 1, 4, 1, 3])', 1), ('first_repeat(["a", "b"])', None), ('first_repeat("abca")', 'a')]))
    results.append(check("Task 3: All subsets of a small set", [('all_subsets([1, 2])', [(), (1,), (1, 2), (2,)]), ('len(all_subsets([1, 2, 3, 4]))', 16), ('all_subsets([])', [()])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
