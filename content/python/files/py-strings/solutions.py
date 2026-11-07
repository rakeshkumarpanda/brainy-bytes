# 3.1 Strings: text, slicing, methods and Unicode
# Model solutions. Try practice.py first.
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


# ================================================================== task 1: Palindrome sentence
# Write is_pal_sentence(text) that returns True when the letters of text, read in lower case and
# ignoring every space and symbol, are the same forwards and backwards.
# Why it works: This is LeetCode 125 with letters only. Cleaning the text first and then using one
# simple test is a common pattern.

def is_pal_sentence(text):
    letters = ""
    for ch in text:
        if ch.isalpha():
            letters = letters + ch.lower()
    return letters == letters[::-1]


# ================================================================== task 2: Run length compression
# Write compress(text) that replaces each run of the same character with the character and the run
# length. "aaabcc" becomes "a3b1c2". An empty text gives "".
# Why it works: Run length encoding is used in fax machines and simple image formats. The "do not
# forget the last run" step catches many people.

def compress(text):
    if text == "":
        return ""
    parts = []
    current = text[0]
    count = 1
    for ch in text[1:]:
        if ch == current:
            count = count + 1
        else:
            parts.append(current + str(count))
            current = ch
            count = 1
    parts.append(current + str(count))
    return "".join(parts)


# ================================================================== task 3: Capitalise every word
# Write cap_words(text) that makes the first letter of every word upper case and the rest lower
# case, keeping single spaces between words. Do not use title().
# Why it works: title() treats an apostrophe as a word break, so "it's".title() gives "It'S".
# Writing it yourself avoids that.

def cap_words(text):
    result = []
    for word in text.split():
        result.append(word[0].upper() + word[1:].lower())
    return " ".join(result)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Palindrome sentence", [('is_pal_sentence("Never odd or even")', True), ('is_pal_sentence("Hello")', False), ('is_pal_sentence("Was it a car or a cat I saw?")', True)]))
    results.append(check("Task 2: Run length compression", [('compress("aaabcc")', 'a3b1c2'), ('compress("")', ''), ('compress("abc")', 'a1b1c1'), ('compress("zzzzzzzzzzzz")', 'z12')]))
    results.append(check("Task 3: Capitalise every word", [('cap_words("hello wORLD")', 'Hello World'), ('cap_words("python")', 'Python'), ('cap_words("a b c")', 'A B C')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
