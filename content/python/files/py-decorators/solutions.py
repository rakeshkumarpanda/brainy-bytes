# 1.2 Extended arguments, closures and decorators
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


# ================================================================== task 1: A call counting decorator
# Write a decorator count_calls that counts how many times the decorated function has been called,
# in an attribute calls on the decorated function. It must return the original result and keep the
# original __name__ (use functools.wraps).
# Why it works: A function is an object, so it can carry its own attributes like calls. The test
# reads double.calls, which is really wrapper.calls.

from functools import wraps


def count_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls = wrapper.calls + 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper


@count_calls
def double(n):
    return n * 2


# ================================================================== task 2: A retry decorator
# Write retry(attempts), a decorator with an argument. The wrapper calls the function up to attempts
# times. If a call succeeds, return its result at once. If every attempt raises an exception, raise
# the last exception again. make_flaky(n) is a helper that fails n times and then returns "ok".
# Why it works: retry(3)(make_flaky(2)) is exactly what @retry(3) does: it fails twice and succeeds
# on the third attempt. Real code adds a growing wait between attempts (backoff).

from functools import wraps


def retry(attempts):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    last_error = err
            raise last_error
        return wrapper
    return decorate


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
# Why it works: The check lives in one decorator and protects every function it is put on. This is
# how validation decorators in web frameworks work.

from functools import wraps


def positive_args(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for value in args:
            if value <= 0:
                raise ValueError("arguments must be positive")
        return func(*args, **kwargs)
    return wrapper


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
