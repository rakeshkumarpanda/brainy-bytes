# 2.2 Monte Carlo and temporal difference learning
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


# ================================================================== 933. Number of Recent Calls (Easy)
# https://leetcode.com/problems/number-of-recent-calls/
# Pattern: Keep a queue and drop old calls from the front
# Idea: Add each call to the back and remove calls older than 3,000 milliseconds from the front.
# Keeping only recent history is what a constant step size does to an estimate: old data fades out.
# Our helper returns the count after each ping.

from collections import deque


class RecentCounter:
    def __init__(self):
        self.calls = deque()

    def ping(self, t):
        self.calls.append(t)
        while self.calls[0] < t - 3000:
            self.calls.popleft()
        return len(self.calls)


def recent_counts(times):
    rc = RecentCounter()
    return [rc.ping(t) for t in times]


# ================================================================== 1716. Calculate Money in Leetcode Bank (Easy)
# https://leetcode.com/problems/calculate-money-in-leetcode-bank/
# Pattern: Day d deposits d // 7 + d % 7 + 1
# Idea: Each Monday starts one higher than the last, and each day adds one more. Adding up rewards
# day by day is how a Monte Carlo return is built.

def total_money(n):
    total = 0
    for d in range(n):
        total += d // 7 + d % 7 + 1
    return total


# ================================================================== 1352. Product of the Last K Numbers (Medium)
# https://leetcode.com/problems/product-of-the-last-k-numbers/
# Pattern: Prefix products, reset at every zero
# Idea: Keep running products. The product of the last k numbers is the last prefix divided by the
# one k places earlier. A zero wipes the history, so restart the list. Running quantities that let
# you answer about any recent window are the idea behind n step returns. Our helper runs a list of
# operations.

class ProductOfNumbers:
    def __init__(self):
        self.prefix = [1]

    def add(self, num):
        if num == 0:
            self.prefix = [1]
        else:
            self.prefix.append(self.prefix[-1] * num)

    def get_product(self, k):
        if k >= len(self.prefix):
            return 0
        return self.prefix[-1] // self.prefix[-1 - k]


def product_run(ops):
    p, out = ProductOfNumbers(), []
    for op in ops:
        if op[0] == "add":
            p.add(op[1])
        else:
            out.append(p.get_product(op[1]))
    return out


# ================================================================== 1423. Maximum Points You Can Obtain from Cards (Medium)
# https://leetcode.com/problems/maximum-points-you-can-obtain-from-cards/
# Pattern: Taking k cards from the ends leaves a middle window of n minus k cards
# Idea: Find the middle window with the smallest sum by sliding it across, and subtract it from the
# total. Sliding a fixed size window and updating its sum in O(1) per step is the same bookkeeping
# an n step TD learner keeps.

def max_score(card_points, k):
    n = len(card_points)
    window = sum(card_points[:n - k])
    low = window
    for i in range(n - k, n):
        window += card_points[i] - card_points[i - (n - k)]
        low = min(low, window)
    return sum(card_points) - low


# ================================================================== 239. Sliding Window Maximum (Hard)
# https://leetcode.com/problems/sliding-window-maximum/
# Pattern: A deque of indices with decreasing values
# Idea: Before adding a new index, pop smaller values from the back, since they can never be a
# maximum again. Pop the front once it leaves the window. The front is always the current maximum.
# Each index enters and leaves once, so the whole pass is O(n).

from collections import deque


def max_sliding_window(nums, k):
    dq, out = deque(), []
    for i, v in enumerate(nums):
        while dq and nums[dq[-1]] <= v:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out


if __name__ == "__main__":
    results = []
    results.append(check("933. Number of Recent Calls", [('recent_counts([1, 100, 3001, 3002])', [1, 2, 3, 3])]))
    results.append(check("1716. Calculate Money in Leetcode Bank", [('total_money(4)', 10), ('total_money(10)', 37), ('total_money(20)', 96)]))
    results.append(check("1352. Product of the Last K Numbers", [('product_run([["add", 3], ["add", 0], ["add", 2], ["add", 5], ["add", 4], ["get", 2], ["get", 3], ["get", 4], ["add", 8], ["get", 2]])', [20, 40, 0, 32])]))
    results.append(check("1423. Maximum Points You Can Obtain from Cards", [('max_score([1, 2, 3, 4, 5, 6, 1], 3)', 12), ('max_score([2, 2, 2], 2)', 4), ('max_score([9, 7, 7, 9, 7, 7, 9], 7)', 55)]))
    results.append(check("239. Sliding Window Maximum", [('max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)', [3, 3, 5, 5, 6, 7]), ('max_sliding_window([1], 1)', [1])]))
    if all(results):
        print("Every solution passes its tests.")
