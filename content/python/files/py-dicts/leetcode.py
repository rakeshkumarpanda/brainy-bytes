# 3.4 Dictionaries: keys, values and hash tables
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


# ================================================================== 1. Two Sum (Easy)
# https://leetcode.com/problems/two-sum/
# Pattern: Dict of seen values
# Idea: For each number x, the partner is target − x. Keep a dict from value to index of the numbers
# seen so far.

def two_sum(nums, target):
    seen = {}
    for i in range(len(nums)):
        need = target - nums[i]
        if need in seen:
            return [seen[need], i]
        seen[nums[i]] = i
    return []


# ================================================================== 242. Valid Anagram (Easy)
# https://leetcode.com/problems/valid-anagram/
# Pattern: Count letters
# Idea: Two words are anagrams when every letter appears the same number of times.

def is_anagram(s, t):
    if len(s) != len(t):
        return False
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    for ch in t:
        if counts.get(ch, 0) == 0:
            return False
        counts[ch] = counts[ch] - 1
    return True


# ================================================================== 387. First Unique Character in a String (Easy)
# https://leetcode.com/problems/first-unique-character-in-a-string/
# Pattern: Count, then scan again
# Idea: First count every letter. Then walk the text again and return the first index whose letter
# count is 1.

def first_uniq_char(s):
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    for i in range(len(s)):
        if counts[s[i]] == 1:
            return i
    return -1


# ================================================================== 383. Ransom Note (Easy)
# https://leetcode.com/problems/ransom-note/
# Pattern: Count and spend
# Idea: Count the magazine letters. Each letter of the note uses one up.

def can_construct(ransom_note, magazine):
    counts = {}
    for ch in magazine:
        counts[ch] = counts.get(ch, 0) + 1
    for ch in ransom_note:
        if counts.get(ch, 0) == 0:
            return False
        counts[ch] = counts[ch] - 1
    return True


# ================================================================== 1512. Number of Good Pairs (Easy)
# https://leetcode.com/problems/number-of-good-pairs/
# Pattern: Count as you go
# Idea: Each new copy of a value makes a pair with every earlier copy, so add the count so far
# before increasing it.

def num_identical_pairs(nums):
    counts = {}
    pairs = 0
    for x in nums:
        pairs = pairs + counts.get(x, 0)
        counts[x] = counts.get(x, 0) + 1
    return pairs


# ================================================================== 169. Majority Element (Easy)
# https://leetcode.com/problems/majority-element/
# Pattern: Count, or Boyer Moore voting
# Idea: Count each value and return the one seen more than n/2 times. The O(1) memory trick is the
# Boyer Moore vote.

def majority_element(nums):
    candidate = None
    votes = 0
    for x in nums:
        if votes == 0:
            candidate = x
        if x == candidate:
            votes = votes + 1
        else:
            votes = votes - 1
    return candidate


# ================================================================== 205. Isomorphic Strings (Easy)
# https://leetcode.com/problems/isomorphic-strings/
# Pattern: Two dicts, one per direction
# Idea: Each letter of s must always map to the same letter of t, and no two letters may map to the
# same one.

def is_isomorphic(s, t):
    s_to_t = {}
    t_to_s = {}
    for a, b in zip(s, t):
        if a in s_to_t and s_to_t[a] != b:
            return False
        if b in t_to_s and t_to_s[b] != a:
            return False
        s_to_t[a] = b
        t_to_s[b] = a
    return True


# ================================================================== 290. Word Pattern (Easy)
# https://leetcode.com/problems/word-pattern/
# Pattern: Two dicts, one per direction
# Idea: Split the text into words. Then it is Isomorphic Strings with letters on one side and words
# on the other.

def word_pattern(pattern, s):
    words = s.split()
    if len(words) != len(pattern):
        return False
    letter_to_word = {}
    word_to_letter = {}
    for letter, word in zip(pattern, words):
        if letter_to_word.get(letter, word) != word:
            return False
        if word_to_letter.get(word, letter) != letter:
            return False
        letter_to_word[letter] = word
        word_to_letter[word] = letter
    return True


# ================================================================== 49. Group Anagrams (Medium)
# https://leetcode.com/problems/group-anagrams/
# Pattern: Group by a sorted key
# Idea: Anagrams have the same letters in sorted order. Use that sorted text as the dict key and a
# list of words as the value.

def group_anagrams(strs):
    groups = {}
    for word in strs:
        key = "".join(sorted(word))
        if key not in groups:
            groups[key] = []
        groups[key].append(word)
    return list(groups.values())


# ================================================================== 347. Top K Frequent Elements (Medium)
# https://leetcode.com/problems/top-k-frequent-elements/
# Pattern: Count, then bucket by count
# Idea: Count each number. Put numbers into buckets by their count, then read the buckets from the
# highest count down.

def top_k_frequent(nums, k):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    buckets = []
    for _ in range(len(nums) + 1):
        buckets.append([])
    for value, count in counts.items():
        buckets[count].append(value)
    result = []
    for count in range(len(nums), 0, -1):
        for value in buckets[count]:
            result.append(value)
            if len(result) == k:
                return result
    return result


# ================================================================== 560. Subarray Sum Equals K (Medium)
# https://leetcode.com/problems/subarray-sum-equals-k/
# Pattern: Prefix sums in a dict
# Idea: A part from i to j sums to k when prefix[j] − prefix[i] = k. Count how often each prefix sum
# has appeared.

def subarray_sum(nums, k):
    seen = {0: 1}
    total = 0
    count = 0
    for x in nums:
        total = total + x
        count = count + seen.get(total - k, 0)
        seen[total] = seen.get(total, 0) + 1
    return count


if __name__ == "__main__":
    results = []
    results.append(check("1. Two Sum", [('two_sum([2, 7, 11, 15], 9)', [0, 1]), ('two_sum([3, 2, 4], 6)', [1, 2]), ('two_sum([3, 3], 6)', [0, 1])]))
    results.append(check("242. Valid Anagram", [('is_anagram("anagram", "nagaram")', True), ('is_anagram("rat", "car")', False)]))
    results.append(check("387. First Unique Character in a String", [('first_uniq_char("leetcode")', 0), ('first_uniq_char("loveleetcode")', 2), ('first_uniq_char("aabb")', -1)]))
    results.append(check("383. Ransom Note", [('can_construct("a", "b")', False), ('can_construct("aa", "ab")', False), ('can_construct("aa", "aab")', True)]))
    results.append(check("1512. Number of Good Pairs", [('num_identical_pairs([1, 2, 3, 1, 1, 3])', 4), ('num_identical_pairs([1, 1, 1, 1])', 6), ('num_identical_pairs([1, 2, 3])', 0)]))
    results.append(check("169. Majority Element", [('majority_element([3, 2, 3])', 3), ('majority_element([2, 2, 1, 1, 1, 2, 2])', 2)]))
    results.append(check("205. Isomorphic Strings", [('is_isomorphic("egg", "add")', True), ('is_isomorphic("foo", "bar")', False), ('is_isomorphic("badc", "baba")', False)]))
    results.append(check("290. Word Pattern", [('word_pattern("abba", "dog cat cat dog")', True), ('word_pattern("abba", "dog cat cat fish")', False), ('word_pattern("aaaa", "dog cat cat dog")', False)]))
    results.append(check("49. Group Anagrams", [('sorted(sorted(g) for g in group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))', [['ate', 'eat', 'tea'], ['bat'], ['nat', 'tan']]), ('group_anagrams([""])', [['']])]))
    results.append(check("347. Top K Frequent Elements", [('sorted(top_k_frequent([1, 1, 1, 2, 2, 3], 2))', [1, 2]), ('top_k_frequent([1], 1)', [1])]))
    results.append(check("560. Subarray Sum Equals K", [('subarray_sum([1, 1, 1], 2)', 2), ('subarray_sum([1, 2, 3], 3)', 2), ('subarray_sum([1, -1, 0], 0)', 3)]))
    if all(results):
        print("Every solution passes its tests.")
