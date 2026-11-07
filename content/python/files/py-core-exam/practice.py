# 7.1 Exam practice: PCEP and PCAP style papers
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


# ================================================================== task 1: Marks report
# Write report(marks) for a dict of name to mark. Return a tuple of (average rounded to 1 decimal
# place, the name with the highest mark, a sorted list of the names with marks below 40). For an
# empty dict return (0, None, []).
# Hint: Loop once over the names. Keep a running total, the best name so far and a list of low
# names.

def report(marks):
    # your code here
    pass


# ================================================================== task 2: Caesar cipher
# Write caesar(text, shift) that moves each letter shift places along the alphabet, wrapping from z
# to a. Keep capitals as capitals and leave every other character unchanged. A negative shift moves
# backwards.
# Hint: Turn a letter into 0 to 25 with ord(ch) − ord("a"), add the shift, take % 26, and turn it
# back with chr.

def caesar(text, shift):
    # your code here
    pass


# ================================================================== task 3: Settings parser
# Write parse_settings(text) that reads lines like name = value into a dict. Strip spaces around
# names and values, skip blank lines and lines that start with #. If a line has no =, raise
# ValueError with the message "line 3: missing =" (the real line number, counting from 1). raises()
# is a test helper.
# Hint: Count lines as you loop. split("=", 1) splits only at the first =, so values may contain =
# too.

def parse_settings(text):
    # your code here
    pass


def raises(func, *args):
    """Test helper: the name of the exception func(*args) raises, or None."""
    try:
        func(*args)
    except Exception as err:
        return type(err).__name__ + ": " + str(err)
    return None


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Marks report", [('report({"Asha": 88, "Ravi": 35, "Meera": 95, "Ali": 20})', [59.5, 'Meera', ['Ali', 'Ravi']]), ('report({})', [0, None, []]), ('report({"Zoe": 40})', [40.0, 'Zoe', []])]))
    results.append(check("Task 2: Caesar cipher", [('caesar("abc xyz", 3)', 'def abc'), ('caesar("Hello, World!", 1)', 'Ifmmp, Xpsme!'), ('caesar("def", -3)', 'abc'), ('caesar(caesar("Python 3.14", 7), -7)', 'Python 3.14')]))
    results.append(check("Task 3: Settings parser", [('parse_settings("host = example.com\\nport=8080\\n")', {'host': 'example.com', 'port': '8080'}), ('parse_settings("# comment\\n\\nmode = fast")', {'mode': 'fast'}), ('raises(parse_settings, "a = 1\\n\\nbroken")', 'ValueError: line 3: missing ='), ('parse_settings("url = a=b")', {'url': 'a=b'})]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
