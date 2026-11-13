# 1.3 Gaussian mixture models and EM
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
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


# ================================================================== 1854. Maximum Population Year (Easy)
# https://leetcode.com/problems/maximum-population-year/
# Pattern: Add 1 at each birth, subtract 1 at each death, and sweep
# Idea: Mark +1 at each birth year and −1 at each death year, then take running totals. The year
# with the highest total is the densest point on the time line, the same idea as finding where a
# density is highest.

def maximum_population(logs):
    change = [0] * 101
    for birth, death in logs:
        change[birth - 1950] += 1
        change[death - 1950] -= 1
    best_year, best, alive = 1950, 0, 0
    for i in range(101):
        alive = alive + change[i]
        if alive > best:
            best, best_year = alive, 1950 + i
    return best_year


# ================================================================== 2848. Points That Intersect With Cars (Easy)
# https://leetcode.com/problems/points-that-intersect-with-cars/
# Pattern: Mark every covered point in a set
# Idea: Put every integer from start to end of each car into a set and count the set. Overlaps count
# once, just as a mixture covers a point whichever component it came from.

def number_of_points(nums):
    covered = set()
    for start, end in nums:
        for p in range(start, end + 1):
            covered.add(p)
    return len(covered)


# ================================================================== 2028. Find Missing Observations (Medium)
# https://leetcode.com/problems/find-missing-observations/
# Pattern: Work out the missing total from the mean
# Idea: The full mean fixes the total sum, so the missing n rolls must add up to mean × (m + n)
# minus the known sum. If that total is outside n to 6n, it is impossible. Otherwise share it out as
# evenly as possible. Our answer puts the extra 1s first, and LeetCode accepts any valid answer.

def missing_rolls(rolls, mean, n):
    total = mean * (len(rolls) + n) - sum(rolls)
    if total < n or total > 6 * n:
        return []
    base, extra = divmod(total, n)
    return [base + 1] * extra + [base] * (n - extra)


# ================================================================== 1109. Corporate Flight Bookings (Medium)
# https://leetcode.com/problems/corporate-flight-bookings/
# Pattern: Difference array, then running sums
# Idea: Add the seats at the first flight of each booking and subtract them after the last flight. A
# running sum then gives every flight’s total in one pass, the same sweep used to build a histogram
# of overlapping ranges.

def corp_flight_bookings(bookings, n):
    diff = [0] * (n + 1)
    for first, last, seats in bookings:
        diff[first - 1] += seats
        diff[last] -= seats
    answer, running = [], 0
    for i in range(n):
        running = running + diff[i]
        answer.append(running)
    return answer


# ================================================================== 1094. Car Pooling (Medium)
# https://leetcode.com/problems/car-pooling/
# Pattern: Sweep the stops and track the load
# Idea: Add passengers where they get on and remove them where they get off, then sweep the stops in
# order. If the load ever goes above the capacity, the answer is no.

def car_pooling(trips, capacity):
    change = {}
    for people, start, end in trips:
        change[start] = change.get(start, 0) + people
        change[end] = change.get(end, 0) - people
    load = 0
    for stop in sorted(change):
        load = load + change[stop]
        if load > capacity:
            return False
    return True


# ================================================================== 4. Median of Two Sorted Arrays (Hard)
# https://leetcode.com/problems/median-of-two-sorted-arrays/
# Pattern: Binary search for the split of the shorter array
# Idea: Cut both arrays so that the left parts hold half of all the values and every left value is
# at most every right value. Binary search the cut in the shorter array. The median then comes from
# the values next to the cut. It finds the middle of two combined groups without merging them.

def find_median_sorted_arrays(a, b):
    if len(a) > len(b):
        a, b = b, a
    m, n = len(a), len(b)
    half = (m + n + 1) // 2
    lo, hi = 0, m
    while lo <= hi:
        i = (lo + hi) // 2
        j = half - i
        a_left = a[i - 1] if i > 0 else float("-inf")
        a_right = a[i] if i < m else float("inf")
        b_left = b[j - 1] if j > 0 else float("-inf")
        b_right = b[j] if j < n else float("inf")
        if a_left <= b_right and b_left <= a_right:
            if (m + n) % 2:
                return float(max(a_left, b_left))
            return (max(a_left, b_left) + min(a_right, b_right)) / 2
        if a_left > b_right:
            hi = i - 1
        else:
            lo = i + 1
    return 0.0


if __name__ == "__main__":
    results = []
    results.append(check("1854. Maximum Population Year", [('maximum_population([[1993, 1999], [2000, 2010]])', 1993), ('maximum_population([[1950, 1961], [1960, 1971], [1970, 1981]])', 1960)]))
    results.append(check("2848. Points That Intersect With Cars", [('number_of_points([[3, 6], [1, 5], [4, 7]])', 7), ('number_of_points([[1, 3], [5, 8]])', 7)]))
    results.append(check("2028. Find Missing Observations", [('missing_rolls([3, 2, 4, 3], 4, 2)', [6, 6]), ('missing_rolls([1, 5, 6], 3, 4)', [3, 2, 2, 2]), ('missing_rolls([1, 2, 3, 4], 6, 4)', [])]))
    results.append(check("1109. Corporate Flight Bookings", [('corp_flight_bookings([[1, 2, 10], [2, 3, 20], [2, 5, 25]], 5)', [10, 55, 45, 25, 25]), ('corp_flight_bookings([[1, 2, 10], [2, 2, 15]], 2)', [10, 25])]))
    results.append(check("1094. Car Pooling", [('car_pooling([[2, 1, 5], [3, 3, 7]], 4)', False), ('car_pooling([[2, 1, 5], [3, 3, 7]], 5)', True)]))
    results.append(check("4. Median of Two Sorted Arrays", [('find_median_sorted_arrays([1, 3], [2])', 2.0), ('find_median_sorted_arrays([1, 2], [3, 4])', 2.5)]))
    if all(results):
        print("Every solution passes its tests.")
