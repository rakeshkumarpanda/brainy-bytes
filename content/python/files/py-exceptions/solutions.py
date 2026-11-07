# 5.1 Exceptions: try, except, else, finally and raise
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


# ================================================================== task 1: Safe integer reader
# Write to_int(text, default=0) that returns int(text), or default if the text is not a whole
# number. Use try and except, not isdigit().
# Why it works: isdigit() would reject "-7" and " 9 ", which int() accepts. Asking int() itself
# (EAFP) gives exactly its rules.

def to_int(text, default=0):
    try:
        return int(text)
    except ValueError:
        return default


# ================================================================== task 2: Validate a username
# Write check_username(name). Raise TypeError if name is not a str. Raise ValueError if it has fewer
# than 3 or more than 12 characters, or if it contains anything other than letters, digits and _.
# Otherwise return the name in lower case. The helper raises() is only there for the tests.
# Why it works: The order of checks matters: len(5) would raise its own TypeError with a less
# helpful message.

def check_username(name):
    if not isinstance(name, str):
        raise TypeError("name must be text")
    if len(name) < 3 or len(name) > 12:
        raise ValueError("name must have 3 to 12 characters")
    for ch in name:
        if not (ch.isalnum() or ch == "_"):
            raise ValueError("only letters, digits and _ are allowed")
    return name.lower()


def raises(func, *args):
    """Test helper: the name of the exception func(*args) raises, or None."""
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None


# ================================================================== task 3: Retry helper
# Write retry(action, tries). Call action() up to tries times. Return its result as soon as one call
# does not raise. If every call raises, raise the last exception again. make_flaky() and raises()
# are helpers for the tests.
# Why it works: Real code adds a wait that doubles after each failure (exponential back off), as in
# the maths lesson.

def retry(action, tries):
    last_error = None
    for attempt in range(tries):
        try:
            return action()
        except Exception as err:
            last_error = err
    raise last_error


def make_flaky(failures):
    """Test helper: an action that raises ConnectionError the first failures times, then returns "ok"."""
    state = {"left": failures}

    def action():
        if state["left"] > 0:
            state["left"] = state["left"] - 1
            raise ConnectionError("try again")
        return "ok"

    return action


def raises(func, *args):
    """Test helper: the name of the exception func(*args) raises, or None."""
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__
    return None


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Safe integer reader", [('to_int("42")', 42), ('to_int("abc")', 0), ('to_int("-7")', -7), ('to_int("4.5", -1)', -1), ('to_int(" 9 ")', 9)]))
    results.append(check("Task 2: Validate a username", [('check_username("Asha_21")', 'asha_21'), ('raises(check_username, 5)', 'TypeError'), ('raises(check_username, "ab")', 'ValueError'), ('raises(check_username, "no spaces")', 'ValueError'), ('raises(check_username, "abcdefghijklm")', 'ValueError')]))
    results.append(check("Task 3: Retry helper", [('retry(lambda: 5, 3)', 5), ('retry(make_flaky(2), 3)', 'ok'), ('raises(retry, make_flaky(5), 3)', 'ConnectionError')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
