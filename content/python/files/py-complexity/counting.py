# 4.1 Complexity, timing and profiling
# Example "counting" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def linear_search(items, target):
    steps = 0
    for item in items:
        steps += 1
        if item == target:
            break
    return steps


def binary_search(items, target):
    steps = 0
    low = 0
    high = len(items) - 1
    while low <= high:
        steps += 1
        middle = (low + high) // 2
        if items[middle] == target:
            break
        if items[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return steps


def count_pairs(items):
    steps = 0
    for a in items:
        for b in items:
            steps += 1
    return steps


print("n      linear  binary  pairs")
for n in [10, 100, 1000]:
    data = list(range(n))
    target = n - 1                             # the last item: the worst case for linear search
    print(f"{n:<6} {linear_search(data, target):<7} {binary_search(data, target):<7} {count_pairs(data)}")
