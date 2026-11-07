# 1.4 Exceptions in depth, copying and serialisation
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


# ================================================================== task 1: An exception hierarchy with chaining
# Write ConfigError(Exception) and a child MissingKey(ConfigError). Then write get_port(config) that
# returns int(config["port"]). If the key is missing, raise MissingKey("port") from the KeyError. If
# the value is not a number, raise ConfigError("port must be a number") from the ValueError. what()
# is a test helper that returns the error type, its message and the type of its __cause__.
# Why it works: Callers can catch ConfigError for every config problem, and the original KeyError or
# ValueError is kept as the cause for debugging.

class ConfigError(Exception):
    pass


class MissingKey(ConfigError):
    pass


def get_port(config):
    try:
        text = config["port"]
    except KeyError as err:
        raise MissingKey("port") from err
    try:
        return int(text)
    except ValueError as err:
        raise ConfigError("port must be a number") from err


def what(func, *args):
    try:
        return func(*args)
    except Exception as err:
        return [type(err).__name__, str(err), type(err.__cause__).__name__]


# ================================================================== task 2: Safe copies of a nested config
# Write with_override(config, section, key, value) that returns a NEW config dict with
# config[section][key] set to value, without changing the original in any way.
# Why it works: With config.copy() the first test fails: the original port changes too, because the
# inner dict is shared.

import copy


def with_override(config, section, key, value):
    new = copy.deepcopy(config)
    new[section][key] = value
    return new


# ================================================================== task 3: Save a high score table with pickle
# Write save_scores(path, scores) that pickles a dict of name to score into the file, and
# top_scores(path, n) that loads it and returns a list of the n best (name, score) pairs, highest
# first (ties by name A to Z). If the file does not exist, top_scores returns []. new_path() is a
# helper.
# Why it works: The key (-score, name) sorts by score from high to low and breaks ties
# alphabetically, in one sort.

import pickle


def save_scores(path, scores):
    with open(path, "wb") as f:
        pickle.dump(scores, f)


def top_scores(path, n):
    try:
        with open(path, "rb") as f:
            scores = pickle.load(f)
    except FileNotFoundError:
        return []
    pairs = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return pairs[:n]


def new_path():
    import os, tempfile
    return os.path.join(tempfile.mkdtemp(), "scores.pkl")


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: An exception hierarchy with chaining", [('get_port({"port": "8080"})', 8080), ('what(get_port, {})', ['MissingKey', 'port', 'KeyError']), ('what(get_port, {"port": "abc"})', ['ConfigError', 'port must be a number', 'ValueError']), ('issubclass(MissingKey, ConfigError)', True)]))
    results.append(check("Task 2: Safe copies of a nested config", [('(lambda c: (with_override(c, "db", "port", 5433)["db"]["port"], c["db"]["port"]))({"db": {"port": 5432}, "debug": False})', [5433, 5432]), ('(lambda c: with_override(c, "db", "host", "x") is c)({"db": {}})', False)]))
    results.append(check("Task 3: Save a high score table with pickle", [('(lambda p: (save_scores(p, {"asha": 90, "ravi": 75, "meera": 90, "ali": 60}), top_scores(p, 3))[1])(new_path())', [['asha', 90], ['meera', 90], ['ravi', 75]]), ('top_scores(new_path(), 5)', [])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
