# 4.1 Functions: def, return and every kind of argument
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


# ================================================================== task 1: Average of any number of values
# Write average(*values) that returns the mean of all the numbers passed in, rounded to 2 decimal
# places. With no values, return 0.
# Hint: values is a tuple. Check len(values) == 0 first to avoid dividing by zero.

def average(*values):
    # your code here
    pass


# ================================================================== task 2: Receipt line with keyword-only options
# Write receipt(item, price, *, qty=1, discount=0) that returns text like "3 x pen = 27.00". The
# total is price × qty × (100 − discount) / 100, with 2 decimals. qty and discount must be
# keyword-only.
# Hint: Add a bare * after price. Format the total with :.2f.

def receipt(item, price, qty=1, discount=0):
    # your code here (and fix the signature)
    pass


# ================================================================== task 3: Append without the mutable default trap
# Write add_tag(tag, tags=None) that adds tag to the list tags and returns the list. If no list is
# given, start a new empty list on every call.
# Hint: Use None as the default and make the list inside the function.

def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Average of any number of values", [('average(2, 4, 9)', 5.0), ('average()', 0), ('average(1, 2)', 1.5), ('average(1, 1, 2)', 1.33)]))
    results.append(check("Task 2: Receipt line with keyword-only options", [('receipt("pen", 10, qty=3, discount=10)', '3 x pen = 27.00'), ('receipt("book", 250)', '1 x book = 250.00'), ('receipt.__kwdefaults__', {'qty': 1, 'discount': 0})]))
    results.append(check("Task 3: Append without the mutable default trap", [('add_tag("a")', ['a']), ('(add_tag("x"), add_tag("y"))[1]', ['y']), ('add_tag("c", ["b"])', ['b', 'c'])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
