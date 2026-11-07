# 3.1 Flask basics: routes, templates, forms and JSON
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


# ================================================================== 434. Number of Segments in a String (Easy)
# https://leetcode.com/problems/number-of-segments-in-a-string/
# Pattern: str.split() with no argument
# Idea: Like counting the words a user typed into a search box. split() with no argument skips any
# amount of spaces, so empty parts never appear.

def count_segments(s):
    return len(s.split())


# ================================================================== 1662. Check If Two String Arrays are Equivalent (Easy)
# https://leetcode.com/problems/check-if-two-string-arrays-are-equivalent/
# Pattern: Join and compare
# Idea: A page built from template parts must give the same text however it was cut. Join both lists
# and compare the results.

def array_strings_are_equal(word1, word2):
    return "".join(word1) == "".join(word2)


# ================================================================== 1544. Make The String Great (Easy)
# https://leetcode.com/problems/make-the-string-great/
# Pattern: A stack of letters
# Idea: Cleaning user input with a stack. Push each letter, but pop instead when it is the same
# letter in the other case as the top.

def make_good(s):
    stack = []
    for ch in s:
        if stack and stack[-1] != ch and stack[-1].lower() == ch.lower():
            stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)


# ================================================================== 2696. Minimum String Length After Removing Substrings (Easy)
# https://leetcode.com/problems/minimum-string-length-after-removing-substrings/
# Pattern: A stack removes pairs as they appear
# Idea: Removing "AB" and "CD" again and again is the same as a stack that pops when the new letter
# completes a pair with the top.

def min_length(s):
    stack = []
    for ch in s:
        if stack and stack[-1] + ch in ("AB", "CD"):
            stack.pop()
        else:
            stack.append(ch)
    return len(stack)


# ================================================================== 648. Replace Words (Medium)
# https://leetcode.com/problems/replace-words/
# Pattern: Check the shortest roots first
# Idea: Like a router that finds the shortest registered prefix of a path. Put the roots in a set
# and try prefixes from short to long.

def replace_words(dictionary, sentence):
    roots = set(dictionary)
    result = []
    for word in sentence.split():
        replacement = word
        for end in range(1, len(word) + 1):
            if word[:end] in roots:
                replacement = word[:end]
                break
        result.append(replacement)
    return " ".join(result)


# ================================================================== 1209. Remove All Adjacent Duplicates in String II (Medium)
# https://leetcode.com/problems/remove-all-adjacent-duplicates-in-string-ii/
# Pattern: A stack of [letter, count]
# Idea: Keep each letter with how many times it repeats on top of the stack. When the count reaches
# k, pop the whole group.

def remove_duplicates(s, k):
    stack = []
    for ch in s:
        if stack and stack[-1][0] == ch:
            stack[-1][1] += 1
            if stack[-1][1] == k:
                stack.pop()
        else:
            stack.append([ch, 1])
    return "".join(ch * count for ch, count in stack)


# ================================================================== 820. Short Encoding of Words (Medium)
# https://leetcode.com/problems/short-encoding-of-words/
# Pattern: Drop words that are endings of other words
# Idea: A word that is the end of another word needs no space of its own. Remove every ending of
# every word from a set, then add len(word) + 1 for each word that is left.

def minimum_length_encoding(words):
    keep = set(words)
    for word in words:
        for start in range(1, len(word)):
            keep.discard(word[start:])
    return sum(len(word) + 1 for word in keep)


# ================================================================== 916. Word Subsets (Medium)
# https://leetcode.com/problems/word-subsets/
# Pattern: Merge the needs into one Counter
# Idea: A word is universal when it has every letter of every word in words2, as often as needed.
# Merge words2 into one Counter of the largest counts, then check each word once.

from collections import Counter


def word_subsets(words1, words2):
    need = Counter()
    for word in words2:
        for ch, count in Counter(word).items():
            need[ch] = max(need[ch], count)
    result = []
    for word in words1:
        have = Counter(word)
        if all(have[ch] >= count for ch, count in need.items()):
            result.append(word)
    return result


# ================================================================== 30. Substring with Concatenation of All Words (Hard)
# https://leetcode.com/problems/substring-with-concatenation-of-all-words/
# Pattern: Cut each window into words and compare Counters
# Idea: Find every place where all the words appear joined in any order, like spotting a set of
# template parts in a page. Each window has a fixed length, so cut it into word sized pieces and
# compare counts.

from collections import Counter


def find_substring(s, words):
    size = len(words[0])
    total = size * len(words)
    need = Counter(words)
    starts = []
    for start in range(len(s) - total + 1):
        pieces = [s[start + i * size:start + (i + 1) * size] for i in range(len(words))]
        if Counter(pieces) == need:
            starts.append(start)
    return starts


# ================================================================== 224. Basic Calculator (Hard)
# https://leetcode.com/problems/basic-calculator/
# Pattern: A stack of (result, sign) for each bracket
# Idea: Templates and config files evaluate small expressions. Walk the text, build numbers digit by
# digit, and push the result so far when a bracket opens.

def calculate(s):
    result = 0
    number = 0
    sign = 1
    stack = []
    for ch in s:
        if ch.isdigit():
            number = number * 10 + int(ch)
        elif ch in "+-":
            result += sign * number
            number = 0
            sign = 1 if ch == "+" else -1
        elif ch == "(":
            stack.append((result, sign))
            result = 0
            sign = 1
        elif ch == ")":
            result += sign * number
            number = 0
            before, outer_sign = stack.pop()
            result = before + outer_sign * result
    return result + sign * number


if __name__ == "__main__":
    results = []
    results.append(check("434. Number of Segments in a String", [('count_segments("Hello, my name is John")', 5), ('count_segments("Hello")', 1), ('count_segments("   ")', 0)]))
    results.append(check("1662. Check If Two String Arrays are Equivalent", [('array_strings_are_equal(["ab", "c"], ["a", "bc"])', True), ('array_strings_are_equal(["a", "cb"], ["ab", "c"])', False), ('array_strings_are_equal(["abc", "d", "defg"], ["abcddefg"])', True)]))
    results.append(check("1544. Make The String Great", [('make_good("leEeetcode")', 'leetcode'), ('make_good("abBAcC")', ''), ('make_good("s")', 's')]))
    results.append(check("2696. Minimum String Length After Removing Substrings", [('min_length("ABFCACDB")', 2), ('min_length("ACBBD")', 5)]))
    results.append(check("648. Replace Words", [('replace_words(["cat", "bat", "rat"], "the cattle was rattled by the battery")', 'the cat was rat by the bat'), ('replace_words(["a", "b", "c"], "aadsfasf absbs bbab cadsfafs")', 'a a b c')]))
    results.append(check("1209. Remove All Adjacent Duplicates in String II", [('remove_duplicates("abcd", 2)', 'abcd'), ('remove_duplicates("deeedbbcccbdaa", 3)', 'aa'), ('remove_duplicates("pbbcggttciiippooaais", 2)', 'ps')]))
    results.append(check("820. Short Encoding of Words", [('minimum_length_encoding(["time", "me", "bell"])', 10), ('minimum_length_encoding(["t"])', 2)]))
    results.append(check("916. Word Subsets", [('word_subsets(["amazon", "apple", "facebook", "google", "leetcode"], ["e", "o"])', ['facebook', 'google', 'leetcode']), ('word_subsets(["amazon", "apple", "facebook", "google", "leetcode"], ["l", "e"])', ['apple', 'google', 'leetcode'])]))
    results.append(check("30. Substring with Concatenation of All Words", [('find_substring("barfoothefoobarman", ["foo", "bar"])', [0, 9]), ('find_substring("wordgoodgoodgoodbestword", ["word", "good", "best", "word"])', []), ('find_substring("barfoofoobarthefoobarman", ["bar", "foo", "the"])', [6, 9, 12])]))
    results.append(check("224. Basic Calculator", [('calculate("1 + 1")', 2), ('calculate(" 2-1 + 2 ")', 3), ('calculate("(1+(4+5+2)-3)+(6+8)")', 23), ('calculate("-(2+3)")', -5)]))
    if all(results):
        print("Every solution passes its tests.")
