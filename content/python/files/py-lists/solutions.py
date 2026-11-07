# 3.2 Lists: storing, changing, sorting and copying
# Model solutions. Try practice.py first.
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


# ================================================================== task 1: Second largest without sorting
# Write second_largest(nums) that returns the second largest different value in a list with at least
# two different values. Use one loop and no sort.
# Why it works: This is the running maximum pattern from Core 2.2 with one more name. It takes one
# pass, O(n), while sorting takes O(n log n).

def second_largest(nums):
    first = None
    second = None
    for x in nums:
        if first is None or x > first:
            second = first
            first = x
        elif x != first and (second is None or x > second):
            second = x
    return second


# ================================================================== task 2: Rotate a list to the right
# Write rotate_right(items, k) that returns a new list with every item moved k places to the right,
# wrapping round. k can be bigger than the length. An empty list gives [].
# Why it works: When k is 0, items[-0:] is the whole list, so the k = 0 case needs its own branch.
# LeetCode 189 asks for the same in place.

def rotate_right(items, k):
    if not items:
        return []
    k = k % len(items)
    return items[-k:] + items[:-k] if k else items[:]


# ================================================================== task 3: Flatten a list of lists
# Write flatten(rows) that turns a list of lists into one list with every item in order. [[1, 2],
# [3], []] becomes [1, 2, 3].
# Why it works: result.extend(row) does the inner loop for you. The one line version is [item for
# row in rows for item in row] (Core 4.3).

def flatten(rows):
    result = []
    for row in rows:
        for item in row:
            result.append(item)
    return result


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Second largest without sorting", [('second_largest([4, 9, 2, 7])', 7), ('second_largest([5, 5, 3])', 3), ('second_largest([-1, -5])', -5)]))
    results.append(check("Task 2: Rotate a list to the right", [('rotate_right([1, 2, 3, 4, 5], 2)', [4, 5, 1, 2, 3]), ('rotate_right([1, 2, 3], 4)', [3, 1, 2]), ('rotate_right([], 3)', [])]))
    results.append(check("Task 3: Flatten a list of lists", [('flatten([[1, 2], [3], []])', [1, 2, 3]), ('flatten([])', []), ('flatten([["a"], ["b", "c"]])', ['a', 'b', 'c'])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
