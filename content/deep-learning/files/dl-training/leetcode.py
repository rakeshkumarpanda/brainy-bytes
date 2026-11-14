# 1.3 Training deep networks: optimisers, normalisation and regularisation
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
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


# ================================================================== 2574. Left and Right Sum Differences (Easy)
# https://leetcode.com/problems/left-and-right-sum-differences/
# Pattern: Keep a running sum from the left and get the right sum from the total
# Idea: Walk once from left to right. The right sum is the total minus the left sum minus the
# current value. Keeping one running total instead of recomputing everything is how momentum and
# Adam store their averages.

def left_right_difference(nums):
    total, left, out = sum(nums), 0, []
    for v in nums:
        right = total - left - v
        out.append(abs(left - right))
        left += v
    return out


# ================================================================== 1870. Minimum Speed to Arrive on Time (Medium)
# https://leetcode.com/problems/minimum-speed-to-arrive-on-time/
# Pattern: Binary search for the smallest speed that is fast enough
# Idea: Being on time only gets easier as the speed rises, so binary search on the answer. Every
# train but the last waits for the next whole hour. Searching for the largest safe value of a
# setting is how a learning rate range test works.

import math


def min_speed_on_time(dist, hour):
    def time_at(speed):
        t = sum(math.ceil(d / speed) for d in dist[:-1])
        return t + dist[-1] / speed

    lo, hi = 1, 10 ** 7
    if time_at(hi) > hour:
        return -1
    while lo < hi:
        mid = (lo + hi) // 2
        if time_at(mid) <= hour:
            hi = mid
        else:
            lo = mid + 1
    return lo


# ================================================================== 2064. Minimized Maximum of Products Distributed to Any Store (Medium)
# https://leetcode.com/problems/minimized-maximum-of-products-distributed-to-any-store/
# Pattern: Binary search the largest load and count the stores it needs
# Idea: For a candidate maximum x, product q needs ceil(q / x) stores. Find the smallest x whose
# total fits in n stores. Splitting work into equal pieces is the same arithmetic as choosing a
# batch size.

import math


def minimized_maximum(n, quantities):
    lo, hi = 1, max(quantities)
    while lo < hi:
        mid = (lo + hi) // 2
        if sum(math.ceil(q / mid) for q in quantities) <= n:
            hi = mid
        else:
            lo = mid + 1
    return lo


# ================================================================== 1552. Magnetic Force Between Two Balls (Medium)
# https://leetcode.com/problems/magnetic-force-between-two-balls/
# Pattern: Binary search the gap and place balls greedily
# Idea: Sort the positions. For a candidate gap, place a ball whenever the distance from the last
# one is big enough, and check whether m balls fit. Keep the largest gap that works.

def max_distance(position, m):
    position = sorted(position)

    def fits(gap):
        count, last = 1, position[0]
        for p in position[1:]:
            if p - last >= gap:
                count, last = count + 1, p
        return count >= m

    lo, hi = 1, position[-1] - position[0]
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if fits(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo


# ================================================================== 410. Split Array Largest Sum (Hard)
# https://leetcode.com/problems/split-array-largest-sum/
# Pattern: Binary search the largest piece sum and split greedily
# Idea: For a limit, cut a new piece whenever adding the next number would pass it, and count the
# pieces. The smallest limit that needs at most k pieces is the answer. This is how data and
# pipeline parallel training balance work across devices.

def split_array(nums, k):
    def pieces(limit):
        count, current = 1, 0
        for v in nums:
            if current + v > limit:
                count, current = count + 1, 0
            current += v
        return count

    lo, hi = max(nums), sum(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if pieces(mid) <= k:
            hi = mid
        else:
            lo = mid + 1
    return lo


if __name__ == "__main__":
    results = []
    results.append(check("2574. Left and Right Sum Differences", [('left_right_difference([10, 4, 8, 3])', [15, 1, 11, 22]), ('left_right_difference([1])', [0])]))
    results.append(check("1870. Minimum Speed to Arrive on Time", [('min_speed_on_time([1, 3, 2], 6)', 1), ('min_speed_on_time([1, 3, 2], 2.7)', 3), ('min_speed_on_time([1, 3, 2], 1.9)', -1)]))
    results.append(check("2064. Minimized Maximum of Products Distributed to Any Store", [('minimized_maximum(6, [11, 6])', 3), ('minimized_maximum(7, [15, 10, 10])', 5), ('minimized_maximum(1, [100000])', 100000)]))
    results.append(check("1552. Magnetic Force Between Two Balls", [('max_distance([1, 2, 3, 4, 7], 3)', 3), ('max_distance([5, 4, 3, 2, 1, 1000000000], 2)', 999999999)]))
    results.append(check("410. Split Array Largest Sum", [('split_array([7, 2, 5, 10, 8], 2)', 18), ('split_array([1, 2, 3, 4, 5], 2)', 9), ('split_array([1, 4, 4], 3)', 4)]))
    if all(results):
        print("Every solution passes its tests.")
