# 3.3 Recommender systems
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


# ================================================================== 506. Relative Ranks (Easy)
# https://leetcode.com/problems/relative-ranks/
# Pattern: Sort indices by score, best first
# Idea: Sort the positions by score from high to low, then hand out "Gold Medal", "Silver Medal",
# "Bronze Medal" and numbers in that order. Turning scores into ranks is the last step of every
# recommender.

def find_relative_ranks(score):
    order = sorted(range(len(score)), key=lambda i: -score[i])
    medals = ["Gold Medal", "Silver Medal", "Bronze Medal"]
    answer = [""] * len(score)
    for place, i in enumerate(order):
        answer[i] = medals[place] if place < 3 else str(place + 1)
    return answer


# ================================================================== 1636. Sort Array by Increasing Frequency (Easy)
# https://leetcode.com/problems/sort-array-by-increasing-frequency/
# Pattern: Sort by a key made of the count and the negative value
# Idea: Count each value, then sort by (count, minus value). A sort key with a tie breaker is how
# popularity lists are ordered when two items have the same score.

def frequency_sort(nums):
    count = {}
    for v in nums:
        count[v] = count.get(v, 0) + 1
    return sorted(nums, key=lambda v: (count[v], -v))


# ================================================================== 1311. Get Watched Videos by Your Friends (Medium)
# https://leetcode.com/problems/get-watched-videos-by-your-friends/
# Pattern: Breadth first search to the given level, then count
# Idea: Walk the friend graph level by level from the person, keeping a visited set, and stop at the
# asked level. Count the videos those friends watched and sort by count, then by name. This is the
# simplest social recommender: suggest what your friends watched.

from collections import deque


def watched_videos_by_friends(watched_videos, friends, id, level):
    seen = {id}
    frontier = deque([id])
    for _ in range(level):
        nxt = deque()
        for person in frontier:
            for f in friends[person]:
                if f not in seen:
                    seen.add(f)
                    nxt.append(f)
        frontier = nxt
    count = {}
    for person in frontier:
        for v in watched_videos[person]:
            count[v] = count.get(v, 0) + 1
    return sorted(count, key=lambda v: (count[v], v))


# ================================================================== 1268. Search Suggestions System (Medium)
# https://leetcode.com/problems/search-suggestions-system/
# Pattern: Sort the products, then binary search each prefix
# Idea: After sorting, all products with a given prefix sit next to each other. For each prefix
# typed so far, find the first match with bisect and take up to three products that still start with
# the prefix. Suggestions while typing are a recommender with a very simple score.

from bisect import bisect_left


def suggested_products(products, search_word):
    products = sorted(products)
    answer = []
    prefix = ""
    for ch in search_word:
        prefix = prefix + ch
        start = bisect_left(products, prefix)
        answer.append([p for p in products[start:start + 3] if p.startswith(prefix)])
    return answer


# ================================================================== 1366. Rank Teams by Votes (Medium)
# https://leetcode.com/problems/rank-teams-by-votes/
# Pattern: Count votes per position and sort by the whole count list
# Idea: For each team, count how many voters put it in each position. Sort teams by those counts,
# highest first position by position, and by name to break full ties. Combining many people’s
# rankings into one is the core of popularity and group recommendations.

def rank_teams(votes):
    n = len(votes[0])
    count = {t: [0] * n for t in votes[0]}
    for v in votes:
        for pos, t in enumerate(v):
            count[t][pos] = count[t][pos] + 1
    return "".join(sorted(votes[0], key=lambda t: ([-c for c in count[t]], t)))


# ================================================================== 2102. Sequentially Ordinal Rank Tracker (Hard)
# https://leetcode.com/problems/sequentially-ordinal-rank-tracker/
# Pattern: Two heaps: the items already shown, and the rest
# Idea: Keep the i best items seen so far in a heap whose top is the worst of them, and every other
# item in a heap whose top is the best. To add, push into the first heap and move its worst item to
# the second. To get, move the best of the second heap into the first and return it. Each call costs
# O(log n), the pattern behind serving a ranked feed that keeps changing.

import heapq


class _Worst:
    def __init__(self, score, name):
        self.score, self.name = score, name

    def __lt__(self, other):
        return (self.score, other.name) < (other.score, self.name)


class SORTracker:
    def __init__(self):
        self.shown = []
        self.rest = []

    def add(self, name, score):
        heapq.heappush(self.shown, _Worst(score, name))
        w = heapq.heappop(self.shown)
        heapq.heappush(self.rest, (-w.score, w.name))

    def get(self):
        s, name = heapq.heappop(self.rest)
        heapq.heappush(self.shown, _Worst(-s, name))
        return name


def sor_tracker_run(ops):
    t = SORTracker()
    out = []
    for op in ops:
        if op[0] == "add":
            t.add(op[1], op[2])
        else:
            out.append(t.get())
    return out


if __name__ == "__main__":
    results = []
    results.append(check("506. Relative Ranks", [('find_relative_ranks([5, 4, 3, 2, 1])', ['Gold Medal', 'Silver Medal', 'Bronze Medal', '4', '5']), ('find_relative_ranks([10, 3, 8, 9, 4])', ['Gold Medal', '5', 'Bronze Medal', 'Silver Medal', '4'])]))
    results.append(check("1636. Sort Array by Increasing Frequency", [('frequency_sort([1, 1, 2, 2, 2, 3])', [3, 1, 1, 2, 2, 2]), ('frequency_sort([2, 3, 1, 3, 2])', [1, 3, 3, 2, 2])]))
    results.append(check("1311. Get Watched Videos by Your Friends", [('watched_videos_by_friends([["A", "B"], ["C"], ["B", "C"], ["D"]], [[1, 2], [0, 3], [0, 3], [1, 2]], 0, 1)', ['B', 'C']), ('watched_videos_by_friends([["A", "B"], ["C"], ["B", "C"], ["D"]], [[1, 2], [0, 3], [0, 3], [1, 2]], 0, 2)', ['D'])]))
    results.append(check("1268. Search Suggestions System", [('suggested_products(["mobile", "mouse", "moneypot", "monitor", "mousepad"], "mouse")', [['mobile', 'moneypot', 'monitor'], ['mobile', 'moneypot', 'monitor'], ['mouse', 'mousepad'], ['mouse', 'mousepad'], ['mouse', 'mousepad']])]))
    results.append(check("1366. Rank Teams by Votes", [('rank_teams(["ABC", "ACB", "ABC", "ACB", "ACB"])', 'ACB'), ('rank_teams(["WXYZ", "XYZW"])', 'XWYZ')]))
    results.append(check("2102. Sequentially Ordinal Rank Tracker", [('sor_tracker_run([["add", "bradford", 2], ["add", "branford", 3], ["get"], ["add", "alps", 2], ["get"], ["add", "orland", 2], ["get"], ["add", "orlando", 3], ["get"], ["add", "alpine", 2], ["get"], ["get"]])', ['branford', 'alps', 'bradford', 'bradford', 'bradford', 'orland'])]))
    if all(results):
        print("Every solution passes its tests.")
