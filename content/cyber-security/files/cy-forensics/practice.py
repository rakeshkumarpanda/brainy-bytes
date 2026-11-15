# 1.3 Digital forensics: collecting and reading evidence
# Practice tasks. Fill in each function, then run this file.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.


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


# ================================================================== task 1: Order evidence by volatility
# Write order_volatility(items). Use this ranking, most fragile first: "memory" 1, "temp files" 2,
# "disk" 3, "remote logs" 4, "backups" 5. Return the items sorted by rank.
# Hint: A dictionary of ranks and sorted with a key.

def order_volatility(items):
    # your code here
    pass


# ================================================================== task 2: Find magic numbers in raw bytes
# Write find_magic(data) that returns a list of (offset, kind) for every place where a header
# starts, sorted by offset. Headers: "jpeg" is bytes FF D8 FF, "png" is 89 50 4E 47, "pdf" is
# b"%PDF", "zip" is b"PK" followed by bytes 03 04.
# Hint: Use bytes.find in a loop for each header, starting one past the last hit, then sort.

def find_magic(data):
    # your code here
    pass


# ================================================================== task 3: Carve JPEG files
# Write carve_jpegs(data) that returns a list of carved files, each written as an upper case hex
# string with .hex().upper(). Each file starts at a JPEG header FF D8 FF and ends at the first FF D9
# after it, both included. A header with no footer after it is skipped. After a carve, keep
# searching after the footer.
# Hint: Find a header, then the first footer after it, slice, and search again after the footer.

def carve_jpegs(data):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Order evidence by volatility", [('order_volatility(["disk", "memory"])', ['memory', 'disk']), ('order_volatility(["backups", "remote logs", "temp files", "disk", "memory"])', ['memory', 'temp files', 'disk', 'remote logs', 'backups']), ('order_volatility([])', [])]))
    results.append(check("Task 2: Find magic numbers in raw bytes", [('find_magic(bytes.fromhex("00FFD8FF00"))', [(1, 'jpeg')]), ('find_magic(b"xx%PDF-1.7 PK\\x03\\x04")', [(2, 'pdf'), (11, 'zip')]), ('find_magic(bytes.fromhex("89504E47") + bytes.fromhex("FFD8FF"))', [(0, 'png'), (4, 'jpeg')]), ('find_magic(b"nothing here")', [])]))
    results.append(check("Task 3: Carve JPEG files", [('carve_jpegs(bytes.fromhex("00FFD8FFE011FFD900"))', ['FFD8FFE011FFD9']), ('carve_jpegs(bytes.fromhex("FFD8FF01FFD9AAFFD8FF02FFD9"))', ['FFD8FF01FFD9', 'FFD8FF02FFD9']), ('carve_jpegs(bytes.fromhex("FFD8FF0102"))', []), ('carve_jpegs(b"")', [])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
