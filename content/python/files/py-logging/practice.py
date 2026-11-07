# 3.3 Logging and debugging
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


# ================================================================== task 1: Is this message shown?
# Write is_shown(logger_level, message_level) where both are level names like "WARNING". Return True
# if a message at message_level passes a logger at logger_level. Use the numbers from the logging
# module (getattr(logging, name)) instead of writing your own table.
# Hint: getattr(logging, "WARNING") is 30. A message passes when its number is at least the logger
# level number.

import logging


def is_shown(logger_level, message_level):
    return logger_level == message_level


# ================================================================== task 2: Capture the log lines of a function
# Write log_lines(func, *args). It attaches a handler to the logger named "app" (level DEBUG), runs
# func(*args), removes the handler again (even if func raises), and returns (result, lines) where
# lines are strings like "DEBUG:dividing 6 by 3". divide is a sample function that logs.
# Hint: Subclass logging.Handler and append in emit. record.getMessage() fills in the %s arguments.
# Remove the handler in a finally block.

import logging


def log_lines(func, *args):
    return func(*args), []


def divide(a, b):
    logger = logging.getLogger("app")
    logger.debug("dividing %s by %s", a, b)
    if b == 0:
        logger.error("cannot divide by zero")
        return None
    return a / b


# ================================================================== task 3: Summarise a log file
# Lines look like "2026-11-07 10:00:01 ERROR shop.cart: payment failed". Write error_report(lines)
# that returns a dict with "errors" (how many ERROR lines), "warnings" (how many WARNING lines),
# "by_logger" (a dict of logger name to its ERROR count) and "first" (the time and message of the
# first ERROR, like "10:00:01 payment failed", or None). Skip lines that do not have all the parts.
# Hint: split(" ", 4) gives date, time, level, "name:" and the message. Check the LEVEL field, not
# whether the word ERROR appears somewhere in the line.

def error_report(lines):
    errors = 0
    for line in lines:
        if "ERROR" in line:
            errors += 1
    return {"errors": errors, "warnings": 0, "by_logger": {}, "first": None}


SAMPLE = [
    "2026-11-07 10:00:00 INFO shop.cart: cart opened",
    "2026-11-07 10:00:01 ERROR shop.pay: payment failed",
    "broken line",
    "2026-11-07 10:00:05 WARNING shop.cart: stock low",
    "2026-11-07 10:00:09 ERROR shop.pay: card declined",
    "2026-11-07 10:01:00 ERROR shop.cart: ERROR in totals",
]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Is this message shown?", [('is_shown("WARNING", "ERROR")', True), ('is_shown("INFO", "DEBUG")', False), ('is_shown("DEBUG", "DEBUG")', True), ('[is_shown("ERROR", m) for m in ["INFO", "WARNING", "CRITICAL"]]', [False, False, True])]))
    results.append(check("Task 2: Capture the log lines of a function", [('log_lines(divide, 6, 3)', [2.0, ['DEBUG:dividing 6 by 3']]), ('log_lines(divide, 1, 0)', [None, ['DEBUG:dividing 1 by 0', 'ERROR:cannot divide by zero']]), ('(log_lines(divide, 1, 1), len(logging.getLogger("app").handlers))[1]', 0)]))
    results.append(check("Task 3: Summarise a log file", [('error_report(SAMPLE)', {'errors': 3, 'warnings': 1, 'by_logger': {'shop.pay': 2, 'shop.cart': 1}, 'first': '10:00:01 payment failed'}), ('error_report([])', {'errors': 0, 'warnings': 0, 'by_logger': {}, 'first': None}), ('error_report(["2026-11-07 09:00:00 INFO a: ERROR mentioned"])["errors"]', 0)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
