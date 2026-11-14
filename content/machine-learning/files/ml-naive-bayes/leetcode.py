# 2.3 Naive Bayes: classify by counting clues
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


# ================================================================== 242. Valid Anagram (Easy)
# https://leetcode.com/problems/valid-anagram/
# Pattern: Compare two count tables
# Idea: Two strings are anagrams when every letter appears the same number of times. Build a count
# table for each and compare them, exactly like comparing word counts per class.

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


# ================================================================== 383. Ransom Note (Easy)
# https://leetcode.com/problems/ransom-note/
# Pattern: Counts as a budget
# Idea: Count the letters in the magazine. Each letter of the note uses one count. If a count would
# go below zero, the note cannot be made.

def can_construct(ransom_note, magazine):
    counts = {}
    for ch in magazine:
        counts[ch] = counts.get(ch, 0) + 1
    for ch in ransom_note:
        if counts.get(ch, 0) == 0:
            return False
        counts[ch] = counts[ch] - 1
    return True


# ================================================================== 819. Most Common Word (Easy)
# https://leetcode.com/problems/most-common-word/
# Pattern: Tokenise, then count
# Idea: Turn punctuation into spaces, lower the case, split into words, skip banned words, and
# count. This is the same tokenising step CountVectorizer does before naive Bayes.

def most_common_word(paragraph, banned):
    clean = ""
    for ch in paragraph.lower():
        if ch.isalpha():
            clean = clean + ch
        else:
            clean = clean + " "
    blocked = set(banned)
    counts = {}
    for w in clean.split():
        if w not in blocked:
            counts[w] = counts.get(w, 0) + 1
    return max(counts, key=counts.get)


# ================================================================== 884. Uncommon Words from Two Sentences (Easy)
# https://leetcode.com/problems/uncommon-words-from-two-sentences/
# Pattern: Count words across both texts
# Idea: A word is uncommon when it appears exactly once in the two sentences together. Count all
# words of both and keep the ones with count 1.

def uncommon_from_sentences(s1, s2):
    counts = {}
    for w in (s1 + " " + s2).split():
        counts[w] = counts.get(w, 0) + 1
    return sorted([w for w in counts if counts[w] == 1])


# ================================================================== 1160. Find Words That Can Be Formed by Characters (Easy)
# https://leetcode.com/problems/find-words-that-can-be-formed-by-characters/
# Pattern: Compare counts per word
# Idea: Count the available characters once. A word is good when, for every letter, it needs no more
# than are available. Add up the lengths of the good words.

def count_characters(words, chars):
    have = {}
    for ch in chars:
        have[ch] = have.get(ch, 0) + 1
    total = 0
    for word in words:
        need = {}
        for ch in word:
            need[ch] = need.get(ch, 0) + 1
        ok = True
        for ch in need:
            if need[ch] > have.get(ch, 0):
                ok = False
        if ok:
            total = total + len(word)
    return total


# ================================================================== 692. Top K Frequent Words (Medium)
# https://leetcode.com/problems/top-k-frequent-words/
# Pattern: Count, then sort by count and word
# Idea: Count every word. Sort by count from high to low, and alphabetically when counts tie. Keep
# the first k. This is how you find the most telling words of a class.

def top_k_frequent(words, k):
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    ordered = sorted(counts, key=lambda w: (-counts[w], w))
    return ordered[:k]


if __name__ == "__main__":
    results = []
    results.append(check("242. Valid Anagram", [('is_anagram("anagram", "nagaram")', True), ('is_anagram("rat", "car")', False)]))
    results.append(check("383. Ransom Note", [('can_construct("a", "b")', False), ('can_construct("aa", "aab")', True)]))
    results.append(check("819. Most Common Word", [('most_common_word("Bob hit a ball, the hit BALL flew far after it was hit.", ["hit"])', 'ball'), ('most_common_word("a.", [])', 'a')]))
    results.append(check("884. Uncommon Words from Two Sentences", [('uncommon_from_sentences("this apple is sweet", "this apple is sour")', ['sour', 'sweet']), ('uncommon_from_sentences("apple apple", "banana")', ['banana'])]))
    results.append(check("1160. Find Words That Can Be Formed by Characters", [('count_characters(["cat", "bt", "hat", "tree"], "atach")', 6), ('count_characters(["hello", "world", "leetcode"], "welldonehoneyr")', 10)]))
    results.append(check("692. Top K Frequent Words", [('top_k_frequent(["i", "love", "leetcode", "i", "love", "coding"], 2)', ['i', 'love']), ('top_k_frequent(["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], 4)', ['the', 'is', 'sunny', 'day'])]))
    if all(results):
        print("Every solution passes its tests.")
