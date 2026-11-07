# 4.2 collections, heapq and bisect
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


# ================================================================== task 1: The most common words
# Write top_words(text, k) that returns the k most common words of text as a list of [word, count]
# pairs, most common first. Make the text lower case and split it on spaces. Use collections.Counter
# and its most_common method. For equal counts keep the order in which the words first appear.
# Why it works: The results are tuples, and the tests compare them as lists because they go through
# JSON. Counter.most_common uses a heap (heapq.nlargest) when k is given, so it is O(n log k).

from collections import Counter


def top_words(text, k):
    counts = Counter(text.lower().split())
    return counts.most_common(k)


# ================================================================== task 2: The hot potato game
# Children stand in a circle (names in order). The potato is passed k times, moving the front child
# to the back each time, and then the child at the front leaves. Write hot_potato(names, k) that
# returns the names in the order they leave. Use a deque and its rotate method (rotate(-k) moves k
# items from the front to the back).
# Why it works: This is the Josephus problem. With a list, moving the front to the back costs O(n)
# each time. With a deque, rotate(-k) costs O(k) and popleft O(1).

from collections import deque


def hot_potato(names, k):
    circle = deque(names)
    order = []
    while circle:
        circle.rotate(-k)
        order.append(circle.popleft())
    return order


# ================================================================== task 3: The fewest meeting rooms
# Each meeting is [start, end]. A room is free again at the end time, so a meeting starting at 10
# can use a room whose meeting ends at 10. Write min_rooms(meetings) that returns the fewest rooms
# needed. Sort by start time and keep a heap of the end times of the rooms in use.
# Why it works: Sorting is O(n log n) and each heap step O(log n), so O(n log n) in total.
# heapreplace pops the smallest and pushes the new item in one step, which is faster than heappop
# then heappush.

import heapq


def min_rooms(meetings):
    ends = []
    for start, end in sorted(meetings):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)
        else:
            heapq.heappush(ends, end)
    return len(ends)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: The most common words", [('top_words("the cat and the hat and the bat", 2)', [['the', 3], ['and', 2]]), ('top_words("A a b", 1)', [['a', 2]]), ('top_words("one", 3)', [['one', 1]]), ('top_words("", 2)', [])]))
    results.append(check("Task 2: The hot potato game", [('hot_potato(["A", "B", "C", "D"], 1)', ['B', 'D', 'C', 'A']), ('hot_potato(["A", "B", "C", "D"], 0)', ['A', 'B', 'C', 'D']), ('hot_potato(["Ann", "Bo", "Cy"], 2)', ['Cy', 'Ann', 'Bo']), ('hot_potato([], 3)', [])]))
    results.append(check("Task 3: The fewest meeting rooms", [('min_rooms([[0, 30], [5, 10], [15, 20]])', 2), ('min_rooms([[7, 10], [2, 4]])', 1), ('min_rooms([])', 0), ('min_rooms([[1, 5], [2, 6], [3, 7], [5, 8]])', 3), ('min_rooms([[1, 10], [10, 20], [20, 30]])', 1)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
