# 1.1 Special methods and operator overloading
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


# ================================================================== task 1: Money with safe addition and ordering
# Write a class Money(amount, currency). a + b returns a new Money when the currencies match and
# raises ValueError otherwise. a == b is True when amount and currency are equal. a < b compares
# amounts of the same currency (use functools.total_ordering so <=, > and >= also work). repr gives
# text like Money(5, 'INR'). raises() is a test helper.
# Hint: Write __repr__, __add__, __eq__ and __lt__, and put @total_ordering above the class.

from functools import total_ordering


class Money:
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    # your code here


def raises(func, *args):
    """Test helper: the name of the exception func(*args) raises, or None."""
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None


# ================================================================== task 2: A 2 by 2 matrix with @
# Write Matrix(a, b, c, d) for the matrix [[a, b], [c, d]]. Support m @ n (matrix product), m == n,
# m * k and k * m for a number k, and a det() method that returns ad − bc. Store the four numbers as
# a tuple in self.cells.
# Hint: Row times column: the top left of the product is a*e + b*g. __rmul__ can return self * k.

class Matrix:
    def __init__(self, a, b, c, d):
        self.cells = (a, b, c, d)

    # your code here


# ================================================================== task 3: A Sentence container
# Write Sentence(text) that splits text into words. len(s) is the number of words, s[i] is a word,
# "word" in s ignores upper and lower case, and for w in s loops over the words.
# Hint: Four short methods: __len__, __getitem__, __contains__ and __iter__, each using self.words.

class Sentence:
    def __init__(self, text):
        self.words = text.split()

    # your code here


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Money with safe addition and ordering", [('repr(Money(5, "INR") + Money(7, "INR"))', "Money(12, 'INR')"), ('raises(lambda: Money(5, "INR") + Money(5, "USD"))', 'ValueError'), ('Money(5, "INR") == Money(5, "INR")', True), ('Money(5, "INR") == Money(5, "USD")', False), ('Money(3, "INR") < Money(5, "INR")', True), ('Money(5, "INR") >= Money(5, "INR")', True), ('sorted([Money(9, "INR"), Money(2, "INR")])[0].amount', 2)]))
    results.append(check("Task 2: A 2 by 2 matrix with @", [('(Matrix(1, 2, 3, 4) @ Matrix(5, 6, 7, 8)).cells', [19, 22, 43, 50]), ('Matrix(1, 2, 3, 4) == Matrix(1, 2, 3, 4)', True), ('(Matrix(1, 2, 3, 4) * 2).cells', [2, 4, 6, 8]), ('(3 * Matrix(1, 0, 0, 1)).cells', [3, 0, 0, 3]), ('Matrix(1, 2, 3, 4).det()', -2)]))
    results.append(check("Task 3: A Sentence container", [('len(Sentence("the quick brown fox"))', 4), ('Sentence("the quick brown fox")[1]', 'quick'), ('"QUICK" in Sentence("the quick brown fox")', True), ('[w.upper() for w in Sentence("a b")]', ['A', 'B']), ('"cat" in Sentence("a b")', False)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
