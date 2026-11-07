# 3.1 Strings: text, slicing, methods and Unicode
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


# ================================================================== 344. Reverse String (Easy)
# https://leetcode.com/problems/reverse-string/
# Pattern: Two pointers
# Idea: The input is a list of characters. Swap the first and last, then move both ends inward.

def reverse_string(s):
    left = 0
    right = len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left = left + 1
        right = right - 1
    return s


# ================================================================== 125. Valid Palindrome (Easy)
# https://leetcode.com/problems/valid-palindrome/
# Pattern: Clean then compare
# Idea: Keep only letters and digits in lower case, then compare the text with its reverse.

def is_palindrome(s):
    clean = ""
    for ch in s:
        if ch.isalnum():
            clean = clean + ch.lower()
    return clean == clean[::-1]


# ================================================================== 58. Length of Last Word (Easy)
# https://leetcode.com/problems/length-of-last-word/
# Pattern: split
# Idea: split() with no argument ignores extra spaces. Take the last word.

def length_of_last_word(s):
    words = s.split()
    return len(words[-1])


# ================================================================== 1768. Merge Strings Alternately (Easy)
# https://leetcode.com/problems/merge-strings-alternately/
# Pattern: Index loop over the longer length
# Idea: Loop i up to the longer length and add word1[i] and word2[i] when they exist.

def merge_alternately(word1, word2):
    result = []
    longest = max(len(word1), len(word2))
    for i in range(longest):
        if i < len(word1):
            result.append(word1[i])
        if i < len(word2):
            result.append(word2[i])
    return "".join(result)


# ================================================================== 14. Longest Common Prefix (Easy)
# https://leetcode.com/problems/longest-common-prefix/
# Pattern: Compare column by column
# Idea: Take the first word. For each position, check that every other word has the same character
# there.

def longest_common_prefix(strs):
    first = strs[0]
    for i in range(len(first)):
        for word in strs[1:]:
            if i >= len(word) or word[i] != first[i]:
                return first[:i]
    return first


# ================================================================== 28. Find the Index of the First Occurrence in a String (Easy)
# https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/
# Pattern: Sliding window of slices
# Idea: Try every start i and compare haystack[i:i + len(needle)] with needle. str.find does this
# for you.

def str_str(haystack, needle):
    size = len(needle)
    for i in range(len(haystack) - size + 1):
        if haystack[i:i + size] == needle:
            return i
    return -1


# ================================================================== 13. Roman to Integer (Easy)
# https://leetcode.com/problems/roman-to-integer/
# Pattern: Look ahead one character
# Idea: Add each value, but subtract it when the next symbol is bigger (IV, IX, XL).

def roman_to_int(s):
    value = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i in range(len(s)):
        if i + 1 < len(s) and value[s[i]] < value[s[i + 1]]:
            total = total - value[s[i]]
        else:
            total = total + value[s[i]]
    return total


# ================================================================== 151. Reverse Words in a String (Medium)
# https://leetcode.com/problems/reverse-words-in-a-string/
# Pattern: split and join
# Idea: split() removes the extra spaces. Reverse the list of words and join with one space.

def reverse_words(s):
    words = s.split()
    words.reverse()
    return " ".join(words)


# ================================================================== 6. Zigzag Conversion (Medium)
# https://leetcode.com/problems/zigzag-conversion/
# Pattern: Simulate rows
# Idea: Keep one string per row. Walk down and up the rows, adding each character to the current
# row.

def convert(s, num_rows):
    if num_rows == 1 or num_rows >= len(s):
        return s
    rows = [""] * num_rows
    row = 0
    step = 1
    for ch in s:
        rows[row] = rows[row] + ch
        if row == 0:
            step = 1
        elif row == num_rows - 1:
            step = -1
        row = row + step
    return "".join(rows)


# ================================================================== 5. Longest Palindromic Substring (Medium)
# https://leetcode.com/problems/longest-palindromic-substring/
# Pattern: Expand around the centre
# Idea: Every palindrome has a centre: a letter or the gap between two letters. Grow outwards from
# each of the 2n − 1 centres.

def longest_palindrome(s):
    best = ""
    for centre in range(len(s)):
        for left, right in [(centre, centre), (centre, centre + 1)]:
            while left >= 0 and right < len(s) and s[left] == s[right]:
                left = left - 1
                right = right + 1
            part = s[left + 1:right]
            if len(part) > len(best):
                best = part
    return best


if __name__ == "__main__":
    results = []
    results.append(check("344. Reverse String", [('reverse_string(list("hello"))', ['o', 'l', 'l', 'e', 'h']), ('reverse_string(list("Hannah"))', ['h', 'a', 'n', 'n', 'a', 'H'])]))
    results.append(check("125. Valid Palindrome", [('is_palindrome("A man, a plan, a canal: Panama")', True), ('is_palindrome("race a car")', False), ('is_palindrome(" ")', True)]))
    results.append(check("58. Length of Last Word", [('length_of_last_word("Hello World")', 5), ('length_of_last_word("   fly me   to   the moon  ")', 4)]))
    results.append(check("1768. Merge Strings Alternately", [('merge_alternately("abc", "pqr")', 'apbqcr'), ('merge_alternately("ab", "pqrs")', 'apbqrs')]))
    results.append(check("14. Longest Common Prefix", [('longest_common_prefix(["flower", "flow", "flight"])', 'fl'), ('longest_common_prefix(["dog", "racecar", "car"])', ''), ('longest_common_prefix(["a"])', 'a')]))
    results.append(check("28. Find the Index of the First Occurrence in a String", [('str_str("sadbutsad", "sad")', 0), ('str_str("leetcode", "leeto")', -1), ('str_str("hello", "ll")', 2)]))
    results.append(check("13. Roman to Integer", [('roman_to_int("III")', 3), ('roman_to_int("LVIII")', 58), ('roman_to_int("MCMXCIV")', 1994)]))
    results.append(check("151. Reverse Words in a String", [('reverse_words("the sky is blue")', 'blue is sky the'), ('reverse_words("  hello world  ")', 'world hello'), ('reverse_words("a good   example")', 'example good a')]))
    results.append(check("6. Zigzag Conversion", [('convert("PAYPALISHIRING", 3)', 'PAHNAPLSIIGYIR'), ('convert("PAYPALISHIRING", 4)', 'PINALSIGYAHRPI'), ('convert("A", 1)', 'A')]))
    results.append(check("5. Longest Palindromic Substring", [('longest_palindrome("babad") in ("bab", "aba")', True), ('longest_palindrome("cbbd")', 'bb'), ('longest_palindrome("forgeeksskeegfor")', 'geeksskeeg')]))
    if all(results):
        print("Every solution passes its tests.")
