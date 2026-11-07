# 2.3 Context managers and the with statement
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


# ================================================================== task 1: A Setting manager that always restores
# Write a class Setting(config, key, value). On enter it puts value into config[key]. On exit it
# puts back the old value, or removes the key if it was not there before. This must also happen
# after an error, and errors must not be hidden. use and use_error are helpers that run it.
# Why it works: Remembering "was it there" separately from the old value matters: a key whose value
# is None is not the same as a missing key.

class Setting:
    def __init__(self, config, key, value):
        self.config = config
        self.key = key
        self.value = value

    def __enter__(self):
        self.had_key = self.key in self.config
        self.old = self.config.get(self.key)
        self.config[self.key] = self.value
        return self.config

    def __exit__(self, kind, err, tb):
        if self.had_key:
            self.config[self.key] = self.old
        else:
            del self.config[self.key]
        return False


def use(config):
    with Setting(config, "mode", "test"):
        inside = config["mode"]
    return inside, config.get("mode"), "mode" in config


def use_error(config):
    try:
        with Setting(config, "mode", "test"):
            raise ValueError("boom")
    except ValueError:
        return "error seen", config.get("mode")
    return "error hidden", config.get("mode")


# ================================================================== task 2: A log_block manager with @contextmanager
# Write log_block(log, name) with @contextmanager. It appends "start name" to the list log, then
# runs the body. If the body works it appends "end name". If the body raises, it appends "error
# name: ErrorType" and lets the error continue. ok and bad are helpers.
# Why it works: A bare raise inside except re raises the error with its original traceback.
# Forgetting it would silently swallow every error in the body.

from contextlib import contextmanager


@contextmanager
def log_block(log, name):
    log.append("start " + name)
    try:
        yield
    except Exception as err:
        log.append("error " + name + ": " + type(err).__name__)
        raise
    log.append("end " + name)


def ok():
    log = []
    with log_block(log, "load"):
        log.append("working")
    return log


def bad():
    log = []
    try:
        with log_block(log, "save"):
            raise KeyError("x")
    except KeyError:
        return log, "KeyError reached the caller"
    return log, "error hidden"


def nested():
    log = []
    with log_block(log, "outer"):
        with log_block(log, "inner"):
            pass
    return log


# ================================================================== task 3: A Transaction that rolls back
# Write a class Transaction(account) for a dict like {"balance": 100}. On enter it saves the balance
# and returns itself. It has deposit(n) and withdraw(n), and withdraw raises ValueError if the
# balance would go below 0. On exit after ANY error it restores the saved balance. It hides
# ValueError (returns True) but lets every other error continue. run is a helper.
# Why it works: This is how database transactions work: all the changes in the block happen, or none
# of them do. sqlite3 connections behave the same way in a with block.

class Transaction:
    def __init__(self, account):
        self.account = account

    def __enter__(self):
        self.saved = self.account["balance"]
        return self

    def deposit(self, n):
        self.account["balance"] += n

    def withdraw(self, n):
        if self.account["balance"] - n < 0:
            raise ValueError("not enough money")
        self.account["balance"] -= n

    def __exit__(self, kind, err, tb):
        if kind is None:
            return False
        self.account["balance"] = self.saved   # roll back after any error
        return issubclass(kind, ValueError)    # hide only ValueError


def run(steps):
    account = {"balance": 100}
    try:
        with Transaction(account) as t:
            for action, amount in steps:
                if action == "crash":
                    raise RuntimeError("power cut")
                getattr(t, action)(amount)
    except RuntimeError:
        return account["balance"], "RuntimeError passed on"
    return account["balance"], "finished"


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A Setting manager that always restores", [('use({"mode": "live"})', ['test', 'live', True]), ('use({})', ['test', None, False]), ('use_error({"mode": "live"})', ['error seen', 'live'])]))
    results.append(check("Task 2: A log_block manager with @contextmanager", [('ok()', ['start load', 'working', 'end load']), ('bad()', [['start save', 'error save: KeyError'], 'KeyError reached the caller']), ('nested()', ['start outer', 'start inner', 'end inner', 'end outer'])]))
    results.append(check("Task 3: A Transaction that rolls back", [('run([("deposit", 50), ("withdraw", 30)])', [120, 'finished']), ('run([("deposit", 50), ("withdraw", 500)])', [100, 'finished']), ('run([("deposit", 50), ("crash", 0)])', [100, 'RuntimeError passed on'])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
