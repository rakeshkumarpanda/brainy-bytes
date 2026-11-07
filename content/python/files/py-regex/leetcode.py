# 6.1 Regular expressions
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


# ================================================================== 1805. Number of Different Integers in a String (Easy)
# https://leetcode.com/problems/number-of-different-integers-in-a-string/
# Pattern: findall the digit runs
# Idea: r"\d+" finds every run of digits. int() removes leading zeros, and a set keeps the different
# values.

import re


def num_different_integers(word):
    return len({int(run) for run in re.findall(r"\d+", word)})


# ================================================================== 2114. Maximum Number of Words Found in Sentences (Easy)
# https://leetcode.com/problems/maximum-number-of-words-found-in-sentences/
# Pattern: Count words with split
# Idea: split() with no argument splits on any run of whitespace, which is the same as
# re.split(r"\s+", s.strip()).

def most_words_found(sentences):
    return max(len(s.split()) for s in sentences)


# ================================================================== 2788. Split Strings by Separator (Easy)
# https://leetcode.com/problems/split-strings-by-separator/
# Pattern: re.split with an escaped separator
# Idea: The separator may be a character that is special in regex, such as "." or "|", so pass it
# through re.escape. Drop empty pieces.

import re


def split_words_by_separator(words, separator):
    result = []
    for word in words:
        result += [piece for piece in re.split(re.escape(separator), word) if piece]
    return result


# ================================================================== 1910. Remove All Occurrences of a Substring (Medium)
# https://leetcode.com/problems/remove-all-occurrences-of-a-substring/
# Pattern: A stack of characters
# Idea: Removing one copy can create a new one, so a single re.sub is not enough. Build the result
# character by character and cut the part off whenever it ends with it.

def remove_occurrences(s, part):
    result = []
    n = len(part)
    for ch in s:
        result.append(ch)
        if len(result) >= n and "".join(result[-n:]) == part:
            del result[-n:]
    return "".join(result)


# ================================================================== 722. Remove Comments (Medium)
# https://leetcode.com/problems/remove-comments/
# Pattern: Join the lines, then one regex
# Idea: Join the source with newlines. r"//.*|/\*(.|\n)*?\*/" matches a line comment or a block
# comment (lazy, across lines). Remove them, split again and drop empty lines.

import re


def remove_comments(source):
    text = "\n".join(source)
    text = re.sub(r"//.*|/\*(?:.|\n)*?\*/", "", text)
    return [line for line in text.split("\n") if line]


# ================================================================== 1023. Camelcase Matching (Medium)
# https://leetcode.com/problems/camelcase-matching/
# Pattern: Build a regex from the pattern
# Idea: Between and around the pattern letters, only lower case letters may be added: "FB" becomes
# ^[a-z]*F[a-z]*B[a-z]*$.

import re


def camel_match(queries, pattern):
    regex = "^[a-z]*" + "[a-z]*".join(re.escape(ch) for ch in pattern) + "[a-z]*$"
    return [re.match(regex, q) is not None for q in queries]


# ================================================================== 1451. Rearrange Words in a Sentence (Medium)
# https://leetcode.com/problems/rearrange-words-in-a-sentence/
# Pattern: A stable sort by length
# Idea: Lower case the words, sort by length (sorted is stable, so equal lengths keep their order),
# then capitalise the first letter of the result.

def arrange_words(text):
    words = sorted(text.lower().split(), key=len)
    sentence = " ".join(words)
    return sentence[0].upper() + sentence[1:]


# ================================================================== 10. Regular Expression Matching (Hard)
# https://leetcode.com/problems/regular-expression-matching/
# Pattern: Dynamic programming over the two strings
# Idea: match(i, j) asks whether s[i:] matches p[j:]. With a * after p[j], either skip "x*" or use
# it once if the first characters match. Memoise with lru_cache.

from functools import lru_cache


def is_match(s, p):
    @lru_cache(maxsize=None)
    def match(i, j):
        if j == len(p):
            return i == len(s)
        first = i < len(s) and p[j] in (s[i], ".")
        if j + 1 < len(p) and p[j + 1] == "*":
            return match(i, j + 2) or (first and match(i + 1, j))
        return first and match(i + 1, j + 1)

    return match(0, 0)


# ================================================================== 44. Wildcard Matching (Hard)
# https://leetcode.com/problems/wildcard-matching/
# Pattern: The same dynamic programming with ? and *
# Idea: ? matches one character, * any run (also empty). A * can either match nothing (move in the
# pattern) or one more character (move in the text).

from functools import lru_cache


def is_wildcard_match(s, p):
    @lru_cache(maxsize=None)
    def match(i, j):
        if j == len(p):
            return i == len(s)
        if p[j] == "*":
            return match(i, j + 1) or (i < len(s) and match(i + 1, j))
        return i < len(s) and p[j] in (s[i], "?") and match(i + 1, j + 1)

    return match(0, 0)


# ================================================================== 591. Tag Validator (Hard)
# https://leetcode.com/problems/tag-validator/
# Pattern: Regex for the pieces, a stack for the nesting
# Idea: Regex cannot check nesting, so use it only for the pieces: remove CDATA blocks, then find
# tags with a regex and match open and close tags with a stack.

import re


def is_valid_tag_code(code):
    code = re.sub(r"<!\[CDATA\[.*?\]\]>", "c", code)
    stack = []
    i = 0
    while i < len(code):
        if i > 0 and not stack:
            return False
        m = re.match(r"<(/?)([A-Z]{1,9})>", code[i:])
        if m:
            name = m.group(2)
            if m.group(1):
                if not stack or stack.pop() != name:
                    return False
            else:
                stack.append(name)
            i += m.end()
        elif code[i] == "<":
            return False
        else:
            i += 1
    return not stack and len(code) > 0 and code.startswith("<")


if __name__ == "__main__":
    results = []
    results.append(check("1805. Number of Different Integers in a String", [('num_different_integers("a123bc34d8ef34")', 3), ('num_different_integers("leet1234code234")', 2), ('num_different_integers("a1b01c001")', 1)]))
    results.append(check("2114. Maximum Number of Words Found in Sentences", [('most_words_found(["alice and bob love leetcode", "i think so too", "this is great thanks very much"])', 6), ('most_words_found(["please wait", "continue to fight", "continue to win"])', 3)]))
    results.append(check("2788. Split Strings by Separator", [('split_words_by_separator(["one.two.three", "four.five", "six"], ".")', ['one', 'two', 'three', 'four', 'five', 'six']), ('split_words_by_separator(["$easy$", "$problem$"], "$")', ['easy', 'problem']), ('split_words_by_separator(["|||"], "|")', [])]))
    results.append(check("1910. Remove All Occurrences of a Substring", [('remove_occurrences("daabcbaabcbc", "abc")', 'dab'), ('remove_occurrences("axxxxyyyyb", "xy")', 'ab')]))
    results.append(check("722. Remove Comments", [('remove_comments(["/*Test program */", "int main()", "{ ", "  // variable declaration ", "int a, b, c;", "/* This is a test", "   multiline  ", "   comment for ", "   testing */", "a = b + c;", "}"])', ['int main()', '{ ', '  ', 'int a, b, c;', 'a = b + c;', '}']), ('remove_comments(["a/*comment", "line", "more_comment*/b"])', ['ab'])]))
    results.append(check("1023. Camelcase Matching", [('camel_match(["FooBar", "FooBarTest", "FootBall", "FrameBuffer", "ForceFeedBack"], "FB")', [True, False, True, True, False]), ('camel_match(["FooBar", "FooBarTest", "FootBall", "FrameBuffer", "ForceFeedBack"], "FoBa")', [True, False, True, False, False])]))
    results.append(check("1451. Rearrange Words in a Sentence", [('arrange_words("Leetcode is cool")', 'Is cool leetcode'), ('arrange_words("Keep calm and code on")', 'On and keep calm code'), ('arrange_words("To be or not to be")', 'To be or to be not')]))
    results.append(check("10. Regular Expression Matching", [('is_match("aa", "a")', False), ('is_match("aa", "a*")', True), ('is_match("ab", ".*")', True), ('is_match("mississippi", "mis*is*p*.")', False), ('is_match("aab", "c*a*b")', True)]))
    results.append(check("44. Wildcard Matching", [('is_wildcard_match("aa", "a")', False), ('is_wildcard_match("aa", "*")', True), ('is_wildcard_match("cb", "?a")', False), ('is_wildcard_match("adceb", "*a*b")', True), ('is_wildcard_match("acdcb", "a*c?b")', False)]))
    results.append(check("591. Tag Validator", [('is_valid_tag_code("<DIV>This is the first line <![CDATA[<div>]]></DIV>")', True), ('is_valid_tag_code("<DIV>>>  ![cdata[]] <![CDATA[<div>]>]]>]]>>]</DIV>")', True), ('is_valid_tag_code("<A>  <B> </A>   </B>")', False), ('is_valid_tag_code("<DIV>  div tag is not closed  <DIV>")', False), ('is_valid_tag_code("<A></A><B></B>")', False)]))
    if all(results):
        print("Every solution passes its tests.")
