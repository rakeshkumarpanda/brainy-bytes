# 3.2 Association rules and market basket analysis
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


# ================================================================== 1. Two Sum (Easy)
# https://leetcode.com/problems/two-sum/
# Pattern: Remember each value you have seen
# Idea: Walk the list and keep a dictionary from value to index. For each number, check whether
# target minus it has been seen. Finding pairs that belong together quickly is the heart of pair
# counting.

def two_sum(nums, target):
    seen = {}
    for i, v in enumerate(nums):
        if target - v in seen:
            return [seen[target - v], i]
        seen[v] = i
    return []


# ================================================================== 349. Intersection of Two Arrays (Easy)
# https://leetcode.com/problems/intersection-of-two-arrays/
# Pattern: Set intersection
# Idea: Turn both lists into sets and intersect them. Support counting asks the same question many
# times: is every item of this set in that basket. Ours sorts the answer so it can be checked.

def intersection(nums1, nums2):
    return sorted(set(nums1) & set(nums2))


# ================================================================== 78. Subsets (Medium)
# https://leetcode.com/problems/subsets/
# Pattern: Each item is in or out
# Idea: Start with the empty set and, for every item, add it to every subset found so far. n items
# give 2n subsets, which is exactly why Apriori avoids listing them all. Ours sorts the subsets so
# the answer can be checked.

def subsets(nums):
    result = [[]]
    for v in nums:
        result = result + [s + [v] for s in result]
    return sorted(sorted(s) for s in result)


# ================================================================== 77. Combinations (Medium)
# https://leetcode.com/problems/combinations/
# Pattern: Backtrack, choosing numbers in increasing order
# Idea: Build each combination by adding numbers larger than the last one, and record it once it has
# k numbers. Generating all size k sets in order is how candidate itemsets are listed.

def combine(n, k):
    result = []

    def build(start, current):
        if len(current) == k:
            result.append(current[:])
            return
        for v in range(start, n + 1):
            current.append(v)
            build(v + 1, current)
            current.pop()

    build(1, [])
    return result


# ================================================================== 49. Group Anagrams (Medium)
# https://leetcode.com/problems/group-anagrams/
# Pattern: Use the sorted letters as a key
# Idea: Words with the same letters share the same sorted string. Group by that key in a dictionary.
# Turning a basket into a sorted key is also how identical itemsets are counted together. Ours sorts
# the groups so the answer can be checked.

def group_anagrams(strs):
    groups = {}
    for s in strs:
        groups.setdefault("".join(sorted(s)), []).append(s)
    return sorted(sorted(g) for g in groups.values())


# ================================================================== 1178. Number of Valid Words for Each Puzzle (Hard)
# https://leetcode.com/problems/number-of-valid-words-for-each-puzzle/
# Pattern: Count word letter sets as bitmasks, then enumerate each puzzle’s subsets
# Idea: Turn each word into a bitmask of its letters and count masks. A puzzle has only 7 letters,
# so list all subsets of its letters that contain its first letter (at most 64) and add up their
# counts. Enumerating subsets of a small itemset is exactly how rules are generated from a frequent
# itemset.

def find_num_of_valid_words(words, puzzles):
    count = {}
    for w in words:
        m = 0
        for ch in w:
            m = m | (1 << (ord(ch) - 97))
        count[m] = count.get(m, 0) + 1
    answer = []
    for p in puzzles:
        first = 1 << (ord(p[0]) - 97)
        rest = 0
        for ch in p[1:]:
            rest = rest | (1 << (ord(ch) - 97))
        total = 0
        sub = rest
        while True:
            total = total + count.get(sub | first, 0)
            if sub == 0:
                break
            sub = (sub - 1) & rest
        answer.append(total)
    return answer


if __name__ == "__main__":
    results = []
    results.append(check("1. Two Sum", [('two_sum([2, 7, 11, 15], 9)', [0, 1]), ('two_sum([3, 2, 4], 6)', [1, 2])]))
    results.append(check("349. Intersection of Two Arrays", [('intersection([1, 2, 2, 1], [2, 2])', [2]), ('intersection([4, 9, 5], [9, 4, 9, 8, 4])', [4, 9])]))
    results.append(check("78. Subsets", [('subsets([1, 2, 3])', [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]), ('subsets([0])', [[], [0]])]))
    results.append(check("77. Combinations", [('combine(4, 2)', [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]), ('combine(1, 1)', [[1]])]))
    results.append(check("49. Group Anagrams", [('group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])', [['ate', 'eat', 'tea'], ['bat'], ['nat', 'tan']])]))
    results.append(check("1178. Number of Valid Words for Each Puzzle", [('find_num_of_valid_words(["aaaa", "asas", "able", "ability", "actt", "actor", "access"], ["aboveyz", "abrodyz", "abslute", "absoryz", "actresz", "gaswxyz"])', [1, 1, 3, 2, 4, 0])]))
    if all(results):
        print("Every solution passes its tests.")
