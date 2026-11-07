# 3.2 Testing: unittest, pytest and mocks
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


# ================================================================== task 1: A tiny test runner
# Write run_cases(func, cases). cases is a list of (args, expected) pairs, where args is a tuple.
# Call func(*args) for each case and return the list of indexes of the cases that fail. A case also
# fails if func raises an exception.
# Hint: Wrap the call in try and except Exception, and treat an exception as a failure.

def run_cases(func, cases):
    failing = []
    for i in range(len(cases)):
        args, expected = cases[i]
        if func(*args) != expected:
            failing.append(i)
    return failing


# ================================================================== task 2: A converter tested with Mock
# Write convert(amount, currency, client) that returns amount in rupees, rounded to 2 places, using
# client.get_rate(currency). For "INR" return amount without calling the client at all. For a
# negative amount raise ValueError, also without calling the client. The tests use
# unittest.mock.Mock as the client.
# Hint: Check the amount first, then the INR case, and only then call client.get_rate once.

from unittest.mock import Mock


def convert(amount, currency, client):
    return amount * client.get_rate(currency)


def try_negative():
    client = Mock()
    try:
        convert(-5, "USD", client)
    except ValueError:
        return "ValueError", client.get_rate.call_count
    return "no error", client.get_rate.call_count


# ================================================================== task 3: Write tests that catch buggy Stacks
# Write a unittest TestCase TestStack with at least 3 tests. Each test makes its stack with
# self.stack_class(). Your tests must all pass for the correct Stack, and must FAIL for each buggy
# version: QueueStack (pop takes the oldest item), SilentStack (pop on an empty stack returns None
# instead of raising IndexError) and EatingPeekStack (peek removes the item). run_tests is the
# helper the checker uses.
# Hint: One test per promise of a stack: last in first out, popping an empty stack raises
# IndexError, and peek does not remove the item.

import unittest


class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.items:
            raise IndexError("pop from empty stack")
        return self.items.pop()

    def peek(self):
        return self.items[-1]

    def size(self):
        return len(self.items)


class QueueStack(Stack):
    def pop(self):
        if not self.items:
            raise IndexError("pop from empty stack")
        return self.items.pop(0)


class SilentStack(Stack):
    def pop(self):
        if not self.items:
            return None
        return self.items.pop()


class EatingPeekStack(Stack):
    def peek(self):
        return self.items.pop()


class TestStack(unittest.TestCase):
    stack_class = Stack

    def test_push(self):
        s = self.stack_class()
        s.push(1)
        self.assertEqual(s.size(), 1)


def run_tests(case, stack_class):
    test_case = type("Run", (case,), {"stack_class": stack_class})
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_case)
    result = unittest.TestResult()
    suite.run(result)
    return result.testsRun, len(result.failures) + len(result.errors)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A tiny test runner", [('run_cases(abs, [((-2,), 2), ((3,), 3), ((0,), 1)])', [2]), ('run_cases(int, [(("7",), 7), (("x",), 0)])', [1]), ('run_cases(max, [])', [])]))
    results.append(check("Task 2: A converter tested with Mock", [('(lambda m: (convert(10, "USD", m), m.get_rate.call_count))(Mock(**{"get_rate.return_value": 83.456}))', [834.56, 1]), ('(lambda m: (convert(50, "INR", m), m.get_rate.call_count))(Mock())', [50, 0]), ('(lambda m: (convert(2, "EUR", m), list(m.get_rate.call_args.args)))(Mock(**{"get_rate.return_value": 90}))', [180, ['EUR']]), ('try_negative()', ['ValueError', 0])]))
    results.append(check("Task 3: Write tests that catch buggy Stacks", [('(lambda r: [r[0] >= 3, r[1]])(run_tests(TestStack, Stack))', [True, 0]), ('run_tests(TestStack, QueueStack)[1] > 0', True), ('run_tests(TestStack, SilentStack)[1] > 0', True), ('run_tests(TestStack, EatingPeekStack)[1] > 0', True)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
