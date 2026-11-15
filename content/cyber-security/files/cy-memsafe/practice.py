# 2.1 Memory safety: overflows, ASLR, use after free and Rust
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


# ================================================================== task 1: A safe 32 bit multiply
# Write mul32(a, b) for non negative integers. Return a × b if it fits in an unsigned 32 bit integer
# (at most 232 − 1), and return None if it would overflow. Check before multiplying, as you would in
# C.
# Hint: Compare a with MAX // b instead of computing a * b first.

def mul32(a, b):
    # your code here
    pass


# ================================================================== task 2: Expected ASLR guesses
# Write aslr_expected(bits, same_layout). With n random bits there are 2n offsets. If the layout
# stays the same after each crash, return (2n + 1) / 2. If every try gets a fresh layout, return 2n.
# Return a float.
# Hint: Without replacement the mean position is (n + 1) / 2, with replacement it is n.

def aslr_expected(bits, same_layout):
    # your code here
    pass


# ================================================================== task 3: A bounded string copy
# Write strlcpy(dst_size, src) that models the BSD function. It copies at most dst_size − 1
# characters of src (leaving room for the terminating zero byte) and returns [copied, len(src)]. If
# dst_size is 0, copy nothing. The caller detects truncation when the second value is at least
# dst_size.
# Hint: Slice to dst_size - 1 and always report the full source length.

def strlcpy(dst_size, src):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A safe 32 bit multiply", [('mul32(1000, 4)', 4000), ('mul32(0x40000001, 4)', None), ('mul32(65535, 65537)', 4294967295), ('mul32(65536, 65536)', None), ('mul32(0, 999999999999)', 0)]))
    results.append(check("Task 2: Expected ASLR guesses", [('aslr_expected(8, True)', 128.5), ('aslr_expected(8, False)', 256.0), ('aslr_expected(16, True)', 32768.5), ('aslr_expected(1, False)', 2.0)]))
    results.append(check("Task 3: A bounded string copy", [('strlcpy(8, "alice")', ['alice', 5]), ('strlcpy(8, "AAAAAAAAAAAA")', ['AAAAAAA', 12]), ('strlcpy(1, "x")', ['', 1]), ('strlcpy(0, "x")', ['', 1]), ('strlcpy(6, "hello")', ['hello', 5])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
