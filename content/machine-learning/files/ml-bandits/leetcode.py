# 1.2 Multi armed bandits
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


# ================================================================== 1431. Kids With the Greatest Number of Candies (Easy)
# https://leetcode.com/problems/kids-with-the-greatest-number-of-candies/
# Pattern: Compare each value plus the extra with the current maximum
# Idea: Find the maximum once, then check each kid against it. A greedy bandit makes this comparison
# every round: which estimate is the highest right now.

def kids_with_candies(candies, extra_candies):
    best = max(candies)
    return [c + extra_candies >= best for c in candies]


# ================================================================== 1672. Richest Customer Wealth (Easy)
# https://leetcode.com/problems/richest-customer-wealth/
# Pattern: The largest row sum
# Idea: Add up each customer’s accounts and take the maximum. Total payout per arm, then the best
# arm, is the same calculation.

def maximum_wealth(accounts):
    return max(sum(a) for a in accounts)


# ================================================================== 398. Random Pick Index (Medium)
# https://leetcode.com/problems/random-pick-index/
# Pattern: Reservoir sampling: keep the i-th match with chance 1/i
# Idea: Walk the list. At the i-th time you meet the target, replace your choice with chance 1/i.
# Every matching index ends up equally likely, and no extra memory is needed. Our helper picks many
# times and returns the set of indices seen, so the answer can be checked.

import random


class RandomPickIndex:
    def __init__(self, nums):
        self.nums = nums

    def pick(self, target):
        chosen, seen = -1, 0
        for i, v in enumerate(self.nums):
            if v == target:
                seen += 1
                if random.randrange(seen) == 0:
                    chosen = i
        return chosen


def pick_many(nums, target, times):
    picker = RandomPickIndex(nums)
    return sorted(set(picker.pick(target) for _ in range(times)))


# ================================================================== 470. Implement Rand10() Using Rand7() (Medium)
# https://leetcode.com/problems/implement-rand10-using-rand7/
# Pattern: Build a uniform number from 1 to 49, reject anything above 40
# Idea: Two calls of rand7 give 49 equally likely outcomes. Keep only the first 40 and map them to 1
# to 10. Rejection sampling like this is how random draws from one distribution are turned into
# another, as Thompson sampling needs. Our check confirms all ten values appear about equally often.

import random


def rand7():
    return random.randint(1, 7)


def rand10():
    while True:
        v = (rand7() - 1) * 7 + rand7()
        if v <= 40:
            return (v - 1) % 10 + 1


def rand10_counts(times):
    counts = [0] * 10
    for _ in range(times):
        counts[rand10() - 1] += 1
    return all(abs(c - times / 10) < times / 20 for c in counts)


# ================================================================== 710. Random Pick with Blacklist (Hard)
# https://leetcode.com/problems/random-pick-with-blacklist/
# Pattern: Draw from the first n minus b numbers and remap blacklisted ones
# Idea: Let size be the count of allowed numbers. Draw uniformly from 0 to size minus 1. Any
# blacklisted number in that range is mapped once, at the start, to an allowed number above the
# range. Each pick is then one random draw and one dictionary lookup. Our helper returns the set of
# values picked.

import random


class BlacklistPicker:
    def __init__(self, n, blacklist):
        self.size = n - len(blacklist)
        black = set(blacklist)
        spare = (x for x in range(self.size, n) if x not in black)
        self.remap = {b: next(spare) for b in blacklist if b < self.size}

    def pick(self):
        x = random.randrange(self.size)
        return self.remap.get(x, x)


def blacklist_picks(n, blacklist, times):
    p = BlacklistPicker(n, blacklist)
    return sorted(set(p.pick() for _ in range(times)))


if __name__ == "__main__":
    results = []
    results.append(check("1431. Kids With the Greatest Number of Candies", [('kids_with_candies([2, 3, 5, 1, 3], 3)', [True, True, True, False, True]), ('kids_with_candies([12, 1, 12], 10)', [True, False, True])]))
    results.append(check("1672. Richest Customer Wealth", [('maximum_wealth([[1, 2, 3], [3, 2, 1]])', 6), ('maximum_wealth([[1, 5], [7, 3], [3, 5]])', 10)]))
    results.append(check("398. Random Pick Index", [('pick_many([1, 2, 3, 3, 3], 3, 300)', [2, 3, 4]), ('pick_many([1, 2, 3, 3, 3], 1, 50)', [0])]))
    results.append(check("470. Implement Rand10() Using Rand7()", [('rand10_counts(20000)', True)]))
    results.append(check("710. Random Pick with Blacklist", [('blacklist_picks(7, [2, 3, 5], 300)', [0, 1, 4, 6]), ('blacklist_picks(3, [0], 100)', [1, 2])]))
    if all(results):
        print("Every solution passes its tests.")
