# 3.3 Diffusion models
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


# ================================================================== 1720. Decode XORed Array (Easy)
# https://leetcode.com/problems/decode-xored-array/
# Pattern: Undo each step: if a ^ b = e then b = a ^ e
# Idea: Start from first and undo the encoding one element at a time, like a reverse process that
# walks back step by step.

def decode(encoded, first):
    arr = [first]
    for e in encoded:
        arr.append(arr[-1] ^ e)            # a ^ b = e  means  b = a ^ e
    return arr


# ================================================================== 2007. Find Original Array From Doubled Array (Medium)
# https://leetcode.com/problems/find-original-array-from-doubled-array/
# Pattern: Sort and count: the smallest remaining value must be an original, so remove its double
# Idea: Work from the smallest value up. Each x needs one 2x to pair with. Zeros pair with zeros.
# Time O(n log n).

from collections import Counter


def findOriginalArray(changed):
    if len(changed) % 2:
        return []
    count = Counter(changed)
    original = []
    for x in sorted(count):                # smallest first: the smallest value must be an original
        if count[x] == 0:
            continue
        if x == 0:
            if count[0] % 2:
                return []
            original += [0] * (count[0] // 2)
            continue
        if count[2 * x] < count[x]:
            return []
        original += [x] * count[x]
        count[2 * x] -= count[x]
    return original


# ================================================================== 1734. Decode XORed Permutation (Medium)
# https://leetcode.com/problems/decode-xored-permutation/
# Pattern: Recover the first element from the xor of 1..n and the xor of every other encoded value
# Idea: The xor of the whole permutation is the xor of 1 to n. The encoded values at odd positions
# xor to perm[1] ^ ... ^ perm[n minus 1]. Their xor is perm[0], and the rest follows by undoing each
# step.

def decodePerm(encoded):
    n = len(encoded) + 1
    total = 0
    for v in range(1, n + 1):
        total ^= v                          # xor of the whole permutation
    rest = 0
    for i in range(1, n - 1, 2):
        rest ^= encoded[i]                  # perm[1] ^ perm[2] ^ ... ^ perm[n - 1]
    perm = [total ^ rest]
    for e in encoded:
        perm.append(perm[-1] ^ e)
    return perm


# ================================================================== 950. Reveal Cards In Increasing Order (Medium)
# https://leetcode.com/problems/reveal-cards-in-increasing-order/
# Pattern: Simulate the reveal process on positions with a queue, then place the sorted cards
# Idea: Run the reveal on the positions 0 to n minus 1 instead of on cards. The order in which
# positions come out is where the smallest, next smallest and so on must go.

from collections import deque


def deckRevealedIncreasing(deck):
    order = deque(range(len(deck)))         # positions in the order they will be revealed
    result = [0] * len(deck)
    for card in sorted(deck):
        result[order.popleft()] = card
        if order:
            order.append(order.popleft())   # the next card goes to the bottom
    return result


# ================================================================== 780. Reaching Points (Hard)
# https://leetcode.com/problems/reaching-points/
# Pattern: Run the moves backwards from the target: the larger coordinate came last, and modulo
# skips many steps at once
# Idea: Forwards there are two choices at every step, backwards only one, just as the reverse
# process of a diffusion model walks back one determined path. Use modulo to jump many subtractions,
# like DDIM skips steps. Time O(log max).

def reachingPoints(sx, sy, tx, ty):
    while tx >= sx and ty >= sy:            # run the moves backwards: the larger number came last
        if tx == ty:
            break
        if tx > ty:
            if ty > sy:
                tx %= ty
            else:
                return (tx - sx) % ty == 0
        else:
            if tx > sx:
                ty %= tx
            else:
                return (ty - sy) % tx == 0
    return tx == sx and ty == sy


if __name__ == "__main__":
    results = []
    results.append(check("1720. Decode XORed Array", [('decode([1, 2, 3], 1)', [1, 0, 2, 1]), ('decode([6, 2, 7, 3], 4)', [4, 2, 0, 7, 4])]))
    results.append(check("2007. Find Original Array From Doubled Array", [('findOriginalArray([1, 3, 4, 2, 6, 8])', [1, 3, 4]), ('findOriginalArray([6, 3, 0, 1])', []), ('findOriginalArray([1])', []), ('findOriginalArray([0, 0, 0, 0])', [0, 0])]))
    results.append(check("1734. Decode XORed Permutation", [('decodePerm([3, 1])', [1, 2, 3]), ('decodePerm([6, 5, 4, 6])', [2, 4, 1, 5, 3])]))
    results.append(check("950. Reveal Cards In Increasing Order", [('deckRevealedIncreasing([17, 13, 11, 2, 3, 5, 7])', [2, 13, 3, 11, 5, 17, 7]), ('deckRevealedIncreasing([1, 1000])', [1, 1000])]))
    results.append(check("780. Reaching Points", [('reachingPoints(1, 1, 3, 5)', True), ('reachingPoints(1, 1, 2, 2)', False), ('reachingPoints(1, 1, 1, 1)', True), ('reachingPoints(3, 7, 3, 4)', False), ('reachingPoints(9, 5, 12, 8)', False)]))
    if all(results):
        print("Every solution passes its tests.")
