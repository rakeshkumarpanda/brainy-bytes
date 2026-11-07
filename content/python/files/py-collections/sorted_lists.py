# 4.2 collections, heapq and bisect
# Example "sorted_lists" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import bisect

scores = [10, 20, 20, 30, 40]
print(bisect.bisect_left(scores, 20), bisect.bisect_right(scores, 20))
bisect.insort(scores, 25)                      # insert and stay sorted
print(scores)


def grade(mark):
    limits = [50, 60, 70, 80]                  # where D, C, B and A start
    letters = "FDCBA"
    return letters[bisect.bisect_right(limits, mark)]


print([grade(m) for m in [33, 50, 69, 70, 95]])


def count_between(sorted_items, low, high):
    """How many items are from low to high, in O(log n)."""
    return bisect.bisect_right(sorted_items, high) - bisect.bisect_left(sorted_items, low)


ages = [12, 15, 18, 18, 21, 30, 45]
print(count_between(ages, 18, 30))

people = [("ann", 31), ("bo", 25), ("cy", 40)]
people.sort(key=lambda person: person[1])
index = bisect.bisect_left(people, 30, key=lambda person: person[1])   # key= since Python 3.10
print(index, people[index])
