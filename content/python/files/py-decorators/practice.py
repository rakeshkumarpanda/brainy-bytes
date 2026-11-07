# 1.2 Extended arguments, closures and decorators
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


# ================================================================== task 1: A call counting decorator
# Write a decorator count_calls that counts how many times the decorated function has been called,
# in an attribute calls on the decorated function. It must return the original result and keep the
# original __name__ (use functools.wraps).
# Hint: Inside count_calls define wrapper(*args, **kwargs) with @wraps(func). Set wrapper.calls = 0
# before returning wrapper, and add 1 inside it.

from functools import wraps


def count_calls(func):
    # your code here
    return func


@count_calls
def double(n):
    return n * 2


# ================================================================== task 2: A retry decorator
# Write retry(attempts), a decorator with an argument. The wrapper calls the function up to attempts
# times. If a call succeeds, return its result at once. If every attempt raises an exception, raise
# the last exception again. make_flaky(n) is a helper that fails n times and then returns "ok".
# Hint: Three levels: retry(attempts) returns decorate(func), which returns wrapper. In the wrapper
# loop attempts times with try and return, remember the error, and raise it after the loop.

from functools import wraps


def retry(attempts):
    # your code here
    pass


def make_flaky(failures):
    """Helper for the tests: a function that raises ConnectionError failures times, then returns "ok"."""
    state = {"left": failures}
    def flaky():
        if state["left"] > 0:
            state["left"] -= 1
            raise ConnectionError("try again")
        return "ok"
    return flaky


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None


# ================================================================== task 3: Check that arguments are positive
# Write a decorator positive_args that raises ValueError if any positional argument is a number that
# is 0 or less, before calling the function. Otherwise it calls the function and returns its result.
# Keep the name with wraps.
# Hint: Loop over args in the wrapper and raise ValueError for any value that is not above 0. Then
# return func(*args, **kwargs).

from functools import wraps


def positive_args(func):
    # your code here
    return func


@positive_args
def area(w, h):
    return w * h


def raises(func, *args):
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A call counting decorator", [('(double(2), double(5), double.calls)', [4, 10, 2]), ('double.__name__', 'double')]))
    results.append(check("Task 2: A retry decorator", [('retry(3)(make_flaky(2))()', 'ok'), ('raises(retry(2)(make_flaky(2)))', 'ConnectionError'), ('retry(1)(make_flaky(0))()', 'ok')]))
    results.append(check("Task 3: Check that arguments are positive", [('area(3, 4)', 12), ('raises(area, 3, -1)', 'ValueError'), ('raises(area, 0, 5)', 'ValueError'), ('area.__name__', 'area')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
