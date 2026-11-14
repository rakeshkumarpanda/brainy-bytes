# 1.1 Neural networks: from perceptrons to MLPs
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


# ================================================================== 1486. XOR Operation in an Array (Easy)
# https://leetcode.com/problems/xor-operation-in-an-array/
# Pattern: Build each number and fold them with XOR
# Idea: The numbers are start, start + 2, start + 4 and so on. XOR them one by one. XOR is the
# function a single perceptron cannot learn, so it is worth knowing well.

def xor_operation(n, start):
    out = 0
    for i in range(n):
        out ^= start + 2 * i
    return out


# ================================================================== 2433. Find The Original Array of Prefix Xor (Medium)
# https://leetcode.com/problems/find-the-original-array-of-prefix-xor/
# Pattern: XOR neighbouring prefixes to undo them
# Idea: Because a ^ a = 0, the original value at i is pref[i] ^ pref[i − 1]. Undoing a running
# combination step by step is the same idea as peeling layers back during backpropagation.

def find_array(pref):
    return [pref[0]] + [pref[i] ^ pref[i - 1] for i in range(1, len(pref))]


# ================================================================== 1442. Count Triplets That Can Form Two Arrays of Equal XOR (Medium)
# https://leetcode.com/problems/count-triplets-that-can-form-two-arrays-of-equal-xor/
# Pattern: Equal XOR halves mean the whole range XORs to 0
# Idea: a == b exactly when arr[i] ^ ... ^ arr[k] is 0, which means two prefix XORs are equal. For
# each such pair of prefix positions, every split point in between works. Turning a condition into a
# simpler hidden feature is what hidden layers do.

def count_triplets(arr):
    prefix = [0]
    for x in arr:
        prefix.append(prefix[-1] ^ x)
    total = 0
    for i in range(len(prefix)):
        for k in range(i + 1, len(prefix)):
            if prefix[i] == prefix[k]:
                total += k - i - 1
    return total


# ================================================================== 421. Maximum XOR of Two Numbers in an Array (Medium)
# https://leetcode.com/problems/maximum-xor-of-two-numbers-in-an-array/
# Pattern: Decide the answer one bit at a time, from the top
# Idea: Try to set each bit of the answer from the highest down. Keep the set of prefixes of the
# numbers and check whether two prefixes XOR to the answer you want. Building a result greedily, bit
# by bit, mirrors how a deep network builds features layer by layer.

def find_maximum_xor(nums):
    best = 0
    for bit in range(31, -1, -1):
        best <<= 1
        prefixes = {x >> bit for x in nums}
        want = best | 1
        if any((want ^ p) in prefixes for p in prefixes):
            best = want
    return best


# ================================================================== 1707. Maximum XOR With an Element From Array (Hard)
# https://leetcode.com/problems/maximum-xor-with-an-element-from-array/
# Pattern: Sort queries by their limit and grow a binary trie
# Idea: Answer queries in order of their limit m, inserting every number up to m into a trie of
# bits. For each query walk the trie, choosing the opposite bit whenever possible. Processing inputs
# in a clever order so that one structure serves every query is a common trick in efficient training
# pipelines.

def maximize_xor(nums, queries):
    nums = sorted(nums)
    order = sorted(range(len(queries)), key=lambda i: queries[i][1])
    trie, ans, j = {}, [-1] * len(queries), 0
    for qi in order:
        x, m = queries[qi]
        while j < len(nums) and nums[j] <= m:
            node = trie
            for bit in range(29, -1, -1):
                node = node.setdefault((nums[j] >> bit) & 1, {})
            j += 1
        if not trie:
            continue
        node, val = trie, 0
        for bit in range(29, -1, -1):
            b = (x >> bit) & 1
            if 1 - b in node:
                val |= 1 << bit
                node = node[1 - b]
            else:
                node = node[b]
        ans[qi] = val
    return ans


if __name__ == "__main__":
    results = []
    results.append(check("1486. XOR Operation in an Array", [('xor_operation(5, 0)', 8), ('xor_operation(4, 3)', 8)]))
    results.append(check("2433. Find The Original Array of Prefix Xor", [('find_array([5, 2, 0, 3, 1])', [5, 7, 2, 3, 2]), ('find_array([13])', [13])]))
    results.append(check("1442. Count Triplets That Can Form Two Arrays of Equal XOR", [('count_triplets([2, 3, 1, 6, 7])', 4), ('count_triplets([1, 1, 1, 1, 1])', 10)]))
    results.append(check("421. Maximum XOR of Two Numbers in an Array", [('find_maximum_xor([3, 10, 5, 25, 2, 8])', 28), ('find_maximum_xor([14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70])', 127)]))
    results.append(check("1707. Maximum XOR With an Element From Array", [('maximize_xor([0, 1, 2, 3, 4], [[3, 1], [1, 3], [5, 6]])', [3, 3, 7]), ('maximize_xor([5, 2, 4, 6, 6, 3], [[12, 4], [8, 1], [6, 3]])', [15, -1, 5])]))
    if all(results):
        print("Every solution passes its tests.")
