# 1.1 What a program is and your first Python program
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


# ================================================================== task 1: The exact text print() writes
# Write printed(values, sep, end) that returns the exact text print(*values, sep=sep, end=end) would
# write. values is a list. Turn each value into text with str().
# Hint: Make a list of str(value) for each value, join it with sep, then add end.

def printed(values, sep, end):
    # your code here
    pass


# ================================================================== task 2: Fix the greeting
# The starter code has two mistakes. Fix them so that greet(name) returns "Hello, " then the name
# then "!". For example greet("Asha") returns "Hello, Asha!".
# Hint: Compare the text you build with the one you want, character by character: a comma is missing
# and so is the !.

def greet(name):
    message = "Hello " + name
    return message


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: The exact text print() writes", [('printed(["Total", 3, "apples"], " ", "\\n")', 'Total 3 apples\n'), ('printed(["2026", "11", "07"], "-", "")', '2026-11-07'), ('printed([], " ", "\\n")', '\n'), ('printed([1.5, True, None], "|", "!")', '1.5|True|None!')]))
    results.append(check("Task 2: Fix the greeting", [('greet("Asha")', 'Hello, Asha!'), ('greet("Ravi")', 'Hello, Ravi!'), ('greet("")', 'Hello, !')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
