# 3.3 Tuples and sets: fixed records and unique items
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


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


# ================================================================== 217. Contains Duplicate (Easy)
# https://leetcode.com/problems/contains-duplicate/
# Pattern: Seen set
# Idea: Add each number to a set. If it is already there, you found a duplicate.

def contains_duplicate(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False


# ================================================================== 349. Intersection of Two Arrays (Easy)
# https://leetcode.com/problems/intersection-of-two-arrays/
# Pattern: Set intersection
# Idea: Turn both lists into sets and take the intersection.

def intersection(nums1, nums2):
    common = set(nums1) & set(nums2)
    return sorted(common)


# ================================================================== 771. Jewels and Stones (Easy)
# https://leetcode.com/problems/jewels-and-stones/
# Pattern: Set membership
# Idea: Put the jewel letters in a set, then count the stones that are in it.

def num_jewels_in_stones(jewels, stones):
    jewel_set = set(jewels)
    count = 0
    for stone in stones:
        if stone in jewel_set:
            count = count + 1
    return count


# ================================================================== 1832. Check if the Sentence Is Pangram (Easy)
# https://leetcode.com/problems/check-if-the-sentence-is-pangram/
# Pattern: Set size
# Idea: A pangram uses every letter a to z. The set of its letters has 26 items.

def check_if_pangram(sentence):
    return len(set(sentence)) == 26


# ================================================================== 268. Missing Number (Easy)
# https://leetcode.com/problems/missing-number/
# Pattern: Gauss sum
# Idea: The numbers 0 to n add up to n(n + 1)/2. The missing one is that total minus the sum of the
# list.

def missing_number(nums):
    n = len(nums)
    expected = n * (n + 1) // 2
    return expected - sum(nums)


# ================================================================== 2215. Find the Difference of Two Arrays (Easy)
# https://leetcode.com/problems/find-the-difference-of-two-arrays/
# Pattern: Set difference
# Idea: A − B and B − A answer the two parts.

def find_difference(nums1, nums2):
    a = set(nums1)
    b = set(nums2)
    return [sorted(a - b), sorted(b - a)]


# ================================================================== 1436. Destination City (Easy)
# https://leetcode.com/problems/destination-city/
# Pattern: Set difference
# Idea: The destination is a city that appears as an end but never as a start.

def dest_city(paths):
    starts = set()
    ends = set()
    for start, end in paths:
        starts.add(start)
        ends.add(end)
    answer = ends - starts
    return answer.pop()


# ================================================================== 645. Set Mismatch (Easy)
# https://leetcode.com/problems/set-mismatch/
# Pattern: Set and Gauss sum
# Idea: The repeated number is sum(nums) − sum(set(nums)). The missing number is n(n + 1)/2 −
# sum(set(nums)).

def find_error_nums(nums):
    n = len(nums)
    unique_sum = sum(set(nums))
    repeated = sum(nums) - unique_sum
    missing = n * (n + 1) // 2 - unique_sum
    return [repeated, missing]


# ================================================================== 3. Longest Substring Without Repeating Characters (Medium)
# https://leetcode.com/problems/longest-substring-without-repeating-characters/
# Pattern: Sliding window with a set
# Idea: Grow the window on the right. While the new letter is already in the window, drop letters
# from the left.

def length_of_longest_substring(s):
    window = set()
    left = 0
    best = 0
    for right in range(len(s)):
        while s[right] in window:
            window.remove(s[left])
            left = left + 1
        window.add(s[right])
        if right - left + 1 > best:
            best = right - left + 1
    return best


# ================================================================== 128. Longest Consecutive Sequence (Medium)
# https://leetcode.com/problems/longest-consecutive-sequence/
# Pattern: Set, start only at the beginning of a run
# Idea: Put all numbers in a set. Start counting only from x where x − 1 is not in the set, so each
# run is walked once: O(n).

def longest_consecutive(nums):
    values = set(nums)
    best = 0
    for x in values:
        if x - 1 not in values:
            length = 1
            while x + length in values:
                length = length + 1
            if length > best:
                best = length
    return best


if __name__ == "__main__":
    results = []
    results.append(check("217. Contains Duplicate", [('contains_duplicate([1, 2, 3, 1])', True), ('contains_duplicate([1, 2, 3, 4])', False)]))
    results.append(check("349. Intersection of Two Arrays", [('intersection([1, 2, 2, 1], [2, 2])', [2]), ('intersection([4, 9, 5], [9, 4, 9, 8, 4])', [4, 9])]))
    results.append(check("771. Jewels and Stones", [('num_jewels_in_stones("aA", "aAAbbbb")', 3), ('num_jewels_in_stones("z", "ZZ")', 0)]))
    results.append(check("1832. Check if the Sentence Is Pangram", [('check_if_pangram("thequickbrownfoxjumpsoverthelazydog")', True), ('check_if_pangram("leetcode")', False)]))
    results.append(check("268. Missing Number", [('missing_number([3, 0, 1])', 2), ('missing_number([9, 6, 4, 2, 3, 5, 7, 0, 1])', 8), ('missing_number([0])', 1)]))
    results.append(check("2215. Find the Difference of Two Arrays", [('find_difference([1, 2, 3], [2, 4, 6])', [[1, 3], [4, 6]]), ('find_difference([1, 2, 3, 3], [1, 1, 2, 2])', [[3], []])]))
    results.append(check("1436. Destination City", [('dest_city([["London", "New York"], ["New York", "Lima"], ["Lima", "Sao Paulo"]])', 'Sao Paulo'), ('dest_city([["A", "Z"]])', 'Z')]))
    results.append(check("645. Set Mismatch", [('find_error_nums([1, 2, 2, 4])', [2, 3]), ('find_error_nums([1, 1])', [1, 2])]))
    results.append(check("3. Longest Substring Without Repeating Characters", [('length_of_longest_substring("abcabcbb")', 3), ('length_of_longest_substring("bbbbb")', 1), ('length_of_longest_substring("pwwkew")', 3), ('length_of_longest_substring("")', 0)]))
    results.append(check("128. Longest Consecutive Sequence", [('longest_consecutive([100, 4, 200, 1, 3, 2])', 4), ('longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1])', 9), ('longest_consecutive([])', 0)]))
    if all(results):
        print("Every solution passes its tests.")
