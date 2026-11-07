# 5.3 Files: reading, writing, modes, paths and streams
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


# ================================================================== task 1: Count words in a file
# Write count_words(path) that opens a UTF-8 text file and returns the number of words (separated by
# any spaces or new lines). If the file does not exist, return 0. make_file() is a helper for the
# tests.
# Hint: Open with with inside try. Add len(line.split()) for each line. Return 0 in except
# FileNotFoundError.

def count_words(path):
    # your code here
    pass


def make_file(text):
    import tempfile
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    f.write(text)
    f.close()
    return f.name


# ================================================================== task 2: Append a log line
# Write add_log(path, message, stamp) that adds one line "stamp | message" to the end of the file
# (creating it if needed) and returns the number of lines the file now has.
# Hint: Open with "a" to add the line (with a new line character). Then open again with "r" and
# count the lines.

def add_log(path, message, stamp):
    # your code here
    pass


def new_path():
    import os, tempfile
    return os.path.join(tempfile.mkdtemp(), "app.log")


# ================================================================== task 3: Copy a file in chunks
# Write copy_file(src, dst, chunk=4) that copies any file byte for byte, reading at most chunk bytes
# at a time in binary mode. Return the number of read calls that returned data.
# Hint: Open src with "rb" and dst with "wb". Loop: read(chunk), stop at b"", write the block.

def copy_file(src, dst, chunk=4):
    # your code here
    pass


def make_bin(data):
    import tempfile
    f = tempfile.NamedTemporaryFile("wb", delete=False)
    f.write(data)
    f.close()
    return f.name


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Count words in a file", [('count_words(make_file("one two\\nthree"))', 3), ('count_words(make_file(""))', 0), ('count_words("/no/such/file.txt")', 0), ('count_words(make_file("  a  b  \\n\\n c "))', 3)]))
    results.append(check("Task 2: Append a log line", [('(lambda p: (add_log(p, "start", "09:00"), add_log(p, "stop", "17:00")))(new_path())', (1, 2)), ('(lambda p: (add_log(p, "x", "1"), open(p).read()))(new_path())[1]', '1 | x\n')]))
    results.append(check("Task 3: Copy a file in chunks", [('(lambda s: (copy_file(s, s + ".copy"), open(s + ".copy", "rb").read() == bytes(range(10))))(make_bin(bytes(range(10))))', (3, True)), ('copy_file(make_bin(b""), make_bin(b"x"))', 0)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
