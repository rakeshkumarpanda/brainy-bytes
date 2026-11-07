# 1.1 HTTP and REST: how the web talks
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


# ================================================================== 1961. Check If String Is a Prefix of Array (Easy)
# https://leetcode.com/problems/check-if-string-is-a-prefix-of-array/
# Pattern: Join pieces until the text is long enough
# Idea: Like building a URL path from its parts. Add the words one by one and stop as soon as the
# joined text is as long as s.

def is_prefix_string(s, words):
    joined = ""
    for word in words:
        joined += word
        if len(joined) >= len(s):
            return joined == s
    return False


# ================================================================== 1309. Decrypt String from Alphabet to Integer Mapping (Easy)
# https://leetcode.com/problems/decrypt-string-from-alphabet-to-integer-mapping/
# Pattern: Look two places ahead for #
# Idea: This is decoding, like reading %20 in a URL. If the character two places ahead is #, read
# two digits, otherwise one.

def freq_alphabets(s):
    result = []
    i = 0
    while i < len(s):
        if i + 2 < len(s) and s[i + 2] == "#":
            number = int(s[i:i + 2])
            i += 3
        else:
            number = int(s[i])
            i += 1
        result.append(chr(ord("a") + number - 1))
    return "".join(result)


# ================================================================== 1773. Count Items Matching a Rule (Easy)
# https://leetcode.com/problems/count-items-matching-a-rule/
# Pattern: Pick the column by its name
# Idea: Like a query string such as ?color=silver filtering records. Map the rule key to a column
# index with a dict.

def count_matches(items, rule_key, rule_value):
    column = {"type": 0, "color": 1, "name": 2}[rule_key]
    return sum(1 for item in items if item[column] == rule_value)


# ================================================================== 2185. Counting Words With a Given Prefix (Easy)
# https://leetcode.com/problems/counting-words-with-a-given-prefix/
# Pattern: str.startswith
# Idea: Routers match URL paths by prefix in the same way. Count the words that start with the
# prefix.

def prefix_count(words, pref):
    return sum(1 for word in words if word.startswith(pref))


# ================================================================== 811. Subdomain Visit Count (Medium)
# https://leetcode.com/problems/subdomain-visit-count/
# Pattern: Every suffix of a host name
# Idea: A visit to discuss.leetcode.com also counts for leetcode.com and com. Split on dots and add
# the count to every ending with a Counter.

from collections import Counter


def subdomain_visits(cpdomains):
    counts = Counter()
    for entry in cpdomains:
        number, domain = entry.split()
        parts = domain.split(".")
        for i in range(len(parts)):
            counts[".".join(parts[i:])] += int(number)
    return sorted(f"{count} {name}" for name, count in counts.items())


# ================================================================== 93. Restore IP Addresses (Medium)
# https://leetcode.com/problems/restore-ip-addresses/
# Pattern: Try every split into four parts
# Idea: Each part is 0 to 255 with no leading zero, like a real IPv4 address. Try lengths 1, 2 and 3
# for each of the four parts.

def restore_ip_addresses(s):
    found = []

    def valid(part):
        return part == "0" or (part[0] != "0" and int(part) <= 255)

    def build(start, parts):
        if len(parts) == 4:
            if start == len(s):
                found.append(".".join(parts))
            return
        for length in (1, 2, 3):
            part = s[start:start + length]
            if len(part) == length and valid(part):
                build(start + length, parts + [part])

    build(0, [])
    return found


# ================================================================== 1268. Search Suggestions System (Medium)
# https://leetcode.com/problems/search-suggestions-system/
# Pattern: Sort once, then filter by the growing prefix
# Idea: This is what a search box API returns while you type. Sort the products, and for each typed
# prefix keep the first three that start with it.

def suggested_products(products, search_word):
    products = sorted(products)
    result = []
    prefix = ""
    for ch in search_word:
        prefix += ch
        matches = [p for p in products if p.startswith(prefix)]
        result.append(matches[:3])
    return result


# ================================================================== 2284. Sender With Largest Word Count (Medium)
# https://leetcode.com/problems/sender-with-largest-word-count/
# Pattern: A Counter, then max with a tuple key
# Idea: Count the words each sender wrote. Pick the largest count, and on a tie the name that is
# largest in alphabetical order: max by (count, name).

from collections import Counter


def largest_word_count(messages, senders):
    words = Counter()
    for message, sender in zip(messages, senders):
        words[sender] += len(message.split())
    return max(words, key=lambda name: (words[name], name))


# ================================================================== 140. Word Break II (Hard)
# https://leetcode.com/problems/word-break-ii/
# Pattern: Recursion with a cache of endings
# Idea: All the ways to cut a string into dictionary words. sentences(start) returns every sentence
# for s[start:], and functools.cache remembers each answer.

from functools import cache


def word_break(s, word_dict):
    words = set(word_dict)

    @cache
    def sentences(start):
        if start == len(s):
            return [""]
        found = []
        for end in range(start + 1, len(s) + 1):
            word = s[start:end]
            if word in words:
                for rest in sentences(end):
                    found.append(word + (" " + rest if rest else ""))
        return found

    return sorted(sentences(0))


# ================================================================== 301. Remove Invalid Parentheses (Hard)
# https://leetcode.com/problems/remove-invalid-parentheses/
# Pattern: Breadth first search by number of removals
# Idea: Check all strings with one character removed, then two, and so on. The first level that has
# valid strings gives the answer with the fewest removals.

def remove_invalid_parentheses(s):
    def valid(text):
        depth = 0
        for ch in text:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth < 0:
                    return False
        return depth == 0

    level = {s}
    while True:
        good = [text for text in level if valid(text)]
        if good:
            return sorted(good)
        next_level = set()
        for text in level:
            for i in range(len(text)):
                if text[i] in "()":
                    next_level.add(text[:i] + text[i + 1:])
        level = next_level


if __name__ == "__main__":
    results = []
    results.append(check("1961. Check If String Is a Prefix of Array", [('is_prefix_string("iloveleetcode", ["i", "love", "leetcode", "apples"])', True), ('is_prefix_string("iloveleetcode", ["apples", "i", "love", "leetcode"])', False), ('is_prefix_string("/api/books", ["/api", "/books", "/1"])', True)]))
    results.append(check("1309. Decrypt String from Alphabet to Integer Mapping", [('freq_alphabets("10#11#12")', 'jkab'), ('freq_alphabets("1326#")', 'acz')]))
    results.append(check("1773. Count Items Matching a Rule", [('count_matches([["phone", "blue", "pixel"], ["computer", "silver", "lenovo"], ["phone", "gold", "iphone"]], "color", "silver")', 1), ('count_matches([["phone", "blue", "pixel"], ["computer", "silver", "phone"], ["phone", "gold", "iphone"]], "type", "phone")', 2)]))
    results.append(check("2185. Counting Words With a Given Prefix", [('prefix_count(["pay", "attention", "practice", "attend"], "at")', 2), ('prefix_count(["leetcode", "win", "loops", "success"], "code")', 0)]))
    results.append(check("811. Subdomain Visit Count", [('subdomain_visits(["9001 discuss.leetcode.com"])', ['9001 com', '9001 discuss.leetcode.com', '9001 leetcode.com']), ('subdomain_visits(["900 google.mail.com", "50 yahoo.com", "1 intel.mail.com", "5 wiki.org"])', ['1 intel.mail.com', '5 org', '5 wiki.org', '50 yahoo.com', '900 google.mail.com', '901 mail.com', '951 com'])]))
    results.append(check("93. Restore IP Addresses", [('restore_ip_addresses("25525511135")', ['255.255.11.135', '255.255.111.35']), ('restore_ip_addresses("0000")', ['0.0.0.0']), ('restore_ip_addresses("101023")', ['1.0.10.23', '1.0.102.3', '10.1.0.23', '10.10.2.3', '101.0.2.3'])]))
    results.append(check("1268. Search Suggestions System", [('suggested_products(["mobile", "mouse", "moneypot", "monitor", "mousepad"], "mouse")', [['mobile', 'moneypot', 'monitor'], ['mobile', 'moneypot', 'monitor'], ['mouse', 'mousepad'], ['mouse', 'mousepad'], ['mouse', 'mousepad']])]))
    results.append(check("2284. Sender With Largest Word Count", [('largest_word_count(["Hello userTwooo", "Hi userThree", "Wonderful day Alice", "Nice day userThree"], ["Alice", "userTwo", "userThree", "Alice"])', 'Alice'), ('largest_word_count(["How is leetcode for everyone", "Leetcode is useful for practice"], ["Bob", "Charlie"])', 'Charlie')]))
    results.append(check("140. Word Break II", [('word_break("catsanddog", ["cat", "cats", "and", "sand", "dog"])', ['cat sand dog', 'cats and dog']), ('word_break("pineapplepenapple", ["apple", "pen", "applepen", "pine", "pineapple"])', ['pine apple pen apple', 'pine applepen apple', 'pineapple pen apple']), ('word_break("catsandog", ["cats", "dog", "sand", "and", "cat"])', [])]))
    results.append(check("301. Remove Invalid Parentheses", [('remove_invalid_parentheses("()())()")', ['(())()', '()()()']), ('remove_invalid_parentheses("(a)())()")', ['(a())()', '(a)()()']), ('remove_invalid_parentheses(")(")', [''])]))
    if all(results):
        print("Every solution passes its tests.")
