# 6.1 Regular expressions
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


# ================================================================== task 1: Find the email addresses
# Write find_emails(text) that returns every email address in text, in order. An address here is one
# or more of letters, digits, dots, underscores or dashes, then @, then a domain made of words
# separated by dots, ending in a dot and 2 or more letters. Use re.findall.
# Why it works: Real email rules (RFC 5322) are far more complex. For checking addresses in a sign
# up form, a simple pattern plus sending a confirmation email is the usual approach.

import re


def find_emails(text):
    return re.findall(r"[\w.-]+@(?:\w+\.)+[A-Za-z]{2,}", text)


# ================================================================== task 2: Turn dates around with named groups
# Write us_to_iso(text) that changes every US date like 11/07/2026 (month/day/year) into the ISO
# form 2026-11-07, and leaves everything else alone. Use re.sub with named groups (?P<month>...) and
# refer to them in the replacement as \g<name>. Months and days always have two digits.
# Why it works: Named groups document themselves. For real date work, parse with datetime.strptime
# and format with strftime, which also checks that the date exists.

import re


def us_to_iso(text):
    return re.sub(r"(?P<month>\d{2})/(?P<day>\d{2})/(?P<year>\d{4})", r"\g<year>-\g<month>-\g<day>", text)


# ================================================================== task 3: A tokenizer for arithmetic
# Write tokenize(expr) that splits an expression like "3 + 4.5*(x - 2)" into a list of [kind, text]
# pairs, skipping spaces. Kinds: NUMBER (digits with an optional decimal part), NAME (a letter or _
# then letters, digits or _), OP (one of + - * / ( )). Any other character raises ValueError. Use
# one pattern with named alternatives and re.finditer, checking m.lastgroup.
# Why it works: This is how real tokenizers start, including Python's own tokenize module and the
# first step of compilers. The tokens then go to a parser that understands precedence and brackets.

import re

TOKEN = re.compile(r"""
    (?P<NUMBER>\d+(?:\.\d+)?)
  | (?P<NAME>[A-Za-z_]\w*)
  | (?P<OP>[-+*/()])
  | (?P<SPACE>\s+)
  | (?P<ERROR>.)
""", re.VERBOSE)


def tokenize(expr):
    tokens = []
    for m in TOKEN.finditer(expr):
        kind = m.lastgroup
        if kind == "SPACE":
            continue
        if kind == "ERROR":
            raise ValueError(f"unexpected character {m.group()!r} at {m.start()}")
        tokens.append([kind, m.group()])
    return tokens


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
