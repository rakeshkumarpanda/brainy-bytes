# 3.4 Dictionaries: keys, values and hash tables
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


# ================================================================== task 1: Word frequency table
# Write word_freq(text) that returns a dict from each lower case word to how many times it appears.
# Split on spaces with split().
# Why it works: This is the core of every search engine index and of the bag of words model in NLP.

def word_freq(text):
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts


# ================================================================== task 2: Invert a dict with repeated values
# Write invert(d) that returns a new dict from each value of d to a sorted list of the keys that had
# that value. {"a": 1, "b": 2, "c": 1} becomes {1: ["a", "c"], 2: ["b"]}.
# Why it works: A plain {v: k for k, v in d.items()} loses keys when values repeat. Grouping into
# lists keeps them all.

def invert(d):
    result = {}
    for key, value in d.items():
        if value not in result:
            result[value] = []
        result[value].append(key)
    for value in result:
        result[value].sort()
    return result


# ================================================================== task 3: A tiny inventory
# Write place_order(stock, order). Both are dicts from item to quantity. If every item of the order
# is in stock in enough quantity, take the quantities away from stock and return True. Otherwise
# change nothing and return False. Return the result and stock as a tuple.
# Why it works: "Check everything, then change everything" keeps the data correct when one item
# fails. Databases call this a transaction (Advanced 6.2).

def place_order(stock, order):
    for item, qty in order.items():
        if stock.get(item, 0) < qty:
            return False, stock
    for item, qty in order.items():
        stock[item] = stock[item] - qty
    return True, stock


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Word frequency table", [('word_freq("The cat the hat")', {'the': 2, 'cat': 1, 'hat': 1}), ('word_freq("")', {}), ('word_freq("a a a")', {'a': 3})]))
    results.append(check("Task 2: Invert a dict with repeated values", [('invert({"a": 1, "b": 2, "c": 1})', {1: ['a', 'c'], 2: ['b']}), ('invert({})', {}), ('invert({"x": "y"})', {'y': ['x']})]))
    results.append(check("Task 3: A tiny inventory", [('place_order({"pen": 5, "ink": 2}, {"pen": 2})', (True, {'pen': 3, 'ink': 2})), ('place_order({"pen": 5}, {"pen": 6})', (False, {'pen': 5})), ('place_order({"pen": 5}, {"cap": 1})', (False, {'pen': 5}))]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
