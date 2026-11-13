# 2.3 Probability and statistics for ML
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


# ================================================================== 1227. Airplane Seat Assignment Probability (Medium)
# https://leetcode.com/problems/airplane-seat-assignment-probability/
# Pattern: Probability by cases
# Idea: Try small n by hand. With one person the answer is 1. With more, the first person picks
# their own seat or the last person’s seat with the same chance, and every other choice just passes
# the same problem to someone else, so the answer is 0.5.

def nth_person_gets_nth_seat(n):
    # f(1) = 1. For n >= 2 the first passenger picks seat 1 (last person wins) or seat n (last person loses)
    # with equal chance, and any other pick restarts the same game with fewer people. So f(n) = 0.5.
    if n == 1:
        return 1.0
    return 0.5


# ================================================================== 528. Random Pick with Weight (Medium)
# https://leetcode.com/problems/random-pick-with-weight/
# Pattern: Prefix sums and binary search
# Idea: Turn the weights into running totals. Pick a random number from 1 to the total and binary
# search for the first running total that reaches it. Index i is chosen with chance w[i] / total.

import random


class Solution:
    def __init__(self, w):
        self.totals = []
        running = 0
        for weight in w:
            running = running + weight
            self.totals.append(running)

    def pickIndex(self):
        target = random.randint(1, self.totals[-1])
        low = 0
        high = len(self.totals) - 1
        while low < high:
            mid = (low + high) // 2
            if self.totals[mid] < target:
                low = mid + 1
            else:
                high = mid
        return low


def pick_shares(w, picks):
    random.seed(0)
    s = Solution(w)
    counts = [0] * len(w)
    for i in range(picks):
        counts[s.pickIndex()] += 1
    return [round(c / picks, 1) for c in counts]


# ================================================================== 1093. Statistics from a Large Sample (Medium)
# https://leetcode.com/problems/statistics-from-a-large-sample/
# Pattern: Mean, median and mode from counts
# Idea: count[v] says how many times value v appears. Walk the counts once for the minimum, maximum,
# total, and the most common value. For the median, walk again until you pass the middle position
# (or the two middle positions).

def sample_stats(count):
    n = sum(count)
    smallest = -1
    largest = -1
    total = 0
    mode = 0
    for v in range(len(count)):
        if count[v] > 0:
            if smallest == -1:
                smallest = v
            largest = v
            total = total + v * count[v]
            if count[v] > count[mode]:
                mode = v

    def value_at(position):
        seen = 0
        for v in range(len(count)):
            seen = seen + count[v]
            if seen > position:
                return v

    if n % 2 == 1:
        median = value_at(n // 2)
    else:
        median = (value_at(n // 2 - 1) + value_at(n // 2)) / 2
    return [float(smallest), float(largest), total / n, float(median), float(mode)]


def stats_of(values):
    count = [0] * 256
    for v in values:
        count[v] += 1
    return sample_stats(count)


# ================================================================== 295. Find Median from Data Stream (Hard)
# https://leetcode.com/problems/find-median-from-data-stream/
# Pattern: Two heaps
# Idea: Keep the smaller half in a max heap and the larger half in a min heap, with sizes that
# differ by at most one. The median is the top of the bigger heap, or the average of both tops.

import heapq


class MedianFinder:
    def __init__(self):
        self.low = []    # max heap of the smaller half (numbers stored as negatives)
        self.high = []   # min heap of the larger half

    def addNum(self, num):
        heapq.heappush(self.low, -num)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def findMedian(self):
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2


def medians_of(nums):
    finder = MedianFinder()
    result = []
    for x in nums:
        finder.addNum(x)
        result.append(finder.findMedian())
    return result


# ================================================================== 837. New 21 Game (Medium)
# https://leetcode.com/problems/new-21-game/
# Pattern: Probability with dynamic programming
# Idea: prob[x] is the chance of ever having exactly x points. Each draw adds 1 to maxPts with equal
# chance, so prob[x] is the sum of prob over the last maxPts totals that are still drawing (below
# k), divided by maxPts. Keep that sum in a sliding window.

def new21_game(n, k, max_pts):
    if k == 0 or n >= k - 1 + max_pts:
        return 1.0
    prob = [0.0] * (n + 1)
    prob[0] = 1.0
    window = 1.0        # sum of prob[x] for the totals that can still draw
    answer = 0.0
    for x in range(1, n + 1):
        prob[x] = window / max_pts
        if x < k:
            window = window + prob[x]
        else:
            answer = answer + prob[x]
        if x - max_pts >= 0 and x - max_pts < k:
            window = window - prob[x - max_pts]
    return round(answer, 5)


# ================================================================== 688. Knight Probability in Chessboard (Medium)
# https://leetcode.com/problems/knight-probability-in-chessboard/
# Pattern: Spread the probability step by step
# Idea: Keep a board of chances. Each move, every square sends 1/8 of its chance to each of its 8
# knight moves that stay on the board. After k moves, add up the board.

def knight_probability(n, k, row, column):
    moves = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
    board = [[0.0] * n for i in range(n)]
    board[row][column] = 1.0
    for step in range(k):
        new_board = [[0.0] * n for i in range(n)]
        for r in range(n):
            for c in range(n):
                if board[r][c] > 0:
                    for dr, dc in moves:
                        nr = r + dr
                        nc = c + dc
                        if 0 <= nr < n and 0 <= nc < n:
                            new_board[nr][nc] += board[r][c] / 8
        board = new_board
    total = 0.0
    for r in range(n):
        total = total + sum(board[r])
    return round(total, 5)


# ================================================================== 808. Soup Servings (Medium)
# https://leetcode.com/problems/soup-servings/
# Pattern: Expected value with memoised recursion
# Idea: Count in units of 25 ml. Each of the 4 serving choices has chance 0.25. The chance that A
# runs out first, plus half the chance both run out together, is the average over the 4 choices. For
# big n the answer is so close to 1 that you can return 1.

from functools import lru_cache


def soup_servings(n):
    if n > 4800:
        return 1.0
    units = (n + 24) // 25

    @lru_cache(maxsize=None)
    def chance(a, b):
        if a <= 0 and b <= 0:
            return 0.5
        if a <= 0:
            return 1.0
        if b <= 0:
            return 0.0
        return 0.25 * (chance(a - 4, b) + chance(a - 3, b - 1) + chance(a - 2, b - 2) + chance(a - 1, b - 3))

    return round(chance(units, units), 5)


if __name__ == "__main__":
    results = []
    results.append(check("1227. Airplane Seat Assignment Probability", [('nth_person_gets_nth_seat(1)', 1.0), ('nth_person_gets_nth_seat(2)', 0.5), ('nth_person_gets_nth_seat(100)', 0.5)]))
    results.append(check("528. Random Pick with Weight", [('Solution([5]).pickIndex()', 0), ('pick_shares([1, 3], 10000)', [0.2, 0.8]), ('pick_shares([1, 1, 2], 10000)', [0.2, 0.3, 0.5])]))
    results.append(check("1093. Statistics from a Large Sample", [('stats_of([1, 2, 2, 2, 3, 3, 3, 3])', [1.0, 3.0, 2.375, 2.5, 3.0]), ('stats_of([1, 2, 2, 2, 4])', [1.0, 4.0, 2.2, 2.0, 2.0])]))
    results.append(check("295. Find Median from Data Stream", [('medians_of([1, 2, 3])', [1.0, 1.5, 2.0]), ('medians_of([5, 15, 1, 3])', [5.0, 10.0, 5.0, 4.0])]))
    results.append(check("837. New 21 Game", [('new21_game(10, 1, 10)', 1.0), ('new21_game(6, 1, 10)', 0.6), ('new21_game(21, 17, 10)', 0.73278)]))
    results.append(check("688. Knight Probability in Chessboard", [('knight_probability(3, 2, 0, 0)', 0.0625), ('knight_probability(1, 0, 0, 0)', 1.0)]))
    results.append(check("808. Soup Servings", [('soup_servings(50)', 0.625), ('soup_servings(100)', 0.71875), ('soup_servings(5000)', 1.0)]))
    if all(results):
        print("Every solution passes its tests.")
