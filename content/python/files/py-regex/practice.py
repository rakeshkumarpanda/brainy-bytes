# 6.1 Regular expressions
# Practice tasks. Fill in each function, then run this file.
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


# ================================================================== task 1: Find the email addresses
# Write find_emails(text) that returns every email address in text, in order. An address here is one
# or more of letters, digits, dots, underscores or dashes, then @, then a domain made of words
# separated by dots, ending in a dot and 2 or more letters. Use re.findall.
# Hint: Name part: [\w.-]+. Domain: (?:\w+\.)+ for "shop." and "co.", then [A-Za-z]{2,} for the
# ending. The group must be non-capturing, or findall would return only the group.

import re


def find_emails(text):
    return re.findall(r"\w+@\w+", text)


# ================================================================== task 2: Turn dates around with named groups
# Write us_to_iso(text) that changes every US date like 11/07/2026 (month/day/year) into the ISO
# form 2026-11-07, and leaves everything else alone. Use re.sub with named groups (?P<month>...) and
# refer to them in the replacement as \g<name>. Months and days always have two digits.
# Hint: In month/day/year the month is first. The starter swaps day and month. Names make the order
# impossible to get wrong: \g<year>-\g<month>-\g<day>.

import re


def us_to_iso(text):
    return re.sub(r"(\d{2})/(\d{2})/(\d{4})", r"\3-\2-\1", text)


# ================================================================== task 3: A tokenizer for arithmetic
# Write tokenize(expr) that splits an expression like "3 + 4.5*(x - 2)" into a list of [kind, text]
# pairs, skipping spaces. Kinds: NUMBER (digits with an optional decimal part), NAME (a letter or _
# then letters, digits or _), OP (one of + - * / ( )). Any other character raises ValueError. Use
# one pattern with named alternatives and re.finditer, checking m.lastgroup.
# Hint: One VERBOSE pattern with named alternatives in priority order. m.lastgroup is the name of
# the alternative that matched. A last catch all (?P<ERROR>.) finds bad characters.

import re


def tokenize(expr):
    return [["OP", ch] for ch in expr if ch != " "]


def error_of(expr):
    try:
        tokenize(expr)
    except ValueError:
        return "ValueError"
    return "no error"


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Find the email addresses", [('find_emails("Write to ann.lee@mail.com or bo_2@shop.co.uk today.")', ['ann.lee@mail.com', 'bo_2@shop.co.uk']), ('find_emails("no email here, just @ and .com")', []), ('find_emails("x-y@a.io, z@b")', ['x-y@a.io'])]))
    results.append(check("Task 2: Turn dates around with named groups", [('us_to_iso("Due 11/07/2026.")', 'Due 2026-11-07.'), ('us_to_iso("01/02/2025 and 12/31/2025")', '2025-01-02 and 2025-12-31'), ('us_to_iso("no dates, 5/6 is a fraction")', 'no dates, 5/6 is a fraction')]))
    results.append(check("Task 3: A tokenizer for arithmetic", [('tokenize("3 + 4.5*(x - 2)")', [['NUMBER', '3'], ['OP', '+'], ['NUMBER', '4.5'], ['OP', '*'], ['OP', '('], ['NAME', 'x'], ['OP', '-'], ['NUMBER', '2'], ['OP', ')']]), ('tokenize("rate_2/10")', [['NAME', 'rate_2'], ['OP', '/'], ['NUMBER', '10']]), ('tokenize("")', []), ('error_of("2 $ 3")', 'ValueError')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
