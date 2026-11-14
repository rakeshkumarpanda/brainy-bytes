# 1.2 Symmetric encryption: AES, GF(2⁸) and modes of operation
# Model solutions. Try practice.py first.
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


# ================================================================== task 1: PKCS 7 padding
# Write pad(data, size) that adds N bytes of value N, where N = size − (len(data) mod size). N is
# never 0.
# Why it works: A message that already fills its last block still gets a full block of padding, so
# unpad never has to guess.

def pad(data, size):
    n = size - len(data) % size
    return data + bytes([n]) * n


# ================================================================== task 2: Check and remove padding
# Write unpad(data, size). Read N from the last byte. Return the data without padding if 1 ≤ N ≤
# size and the last N bytes all equal N. Otherwise return None.
# Why it works: In a real system, never tell the sender which check failed. Different answers for
# bad padding and bad data are exactly the padding oracle.

def unpad(data, size):
    n = data[-1]
    if n < 1 or n > size:
        return None
    if data[-n:] != bytes([n]) * n:
        return None
    return data[:-n].decode()


# ================================================================== task 3: Multiply by 2 in GF(2<sup>8</sup>)
# Write xtime(a) for a byte a: shift left by one bit, and if the result has bit 8 set (it is 256 or
# more), XOR it with 0x11B.
# Why it works: These are the FIPS 197 values: {57}·2 = {ae} and {57}·4 = {47}. Every AES
# multiplication is built from this one step.

def xtime(a):
    a = a << 1
    if a & 0x100:
        a = a ^ 0x11B
    return a


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: PKCS 7 padding", [('pad(b"HELLO", 8).hex()', '48454c4c4f030303'), ('len(pad(b"12345678", 8))', 16), ('pad(b"", 4).hex()', '04040404')]))
    results.append(check("Task 2: Check and remove padding", [('unpad(bytes.fromhex("48454c4c4f030303"), 8)', 'HELLO'), ('unpad(bytes.fromhex("48454c4c4f030302"), 8)', None), ('unpad(bytes.fromhex("4142434400000000"), 8)', None)]))
    results.append(check("Task 3: Multiply by 2 in GF(2<sup>8</sup>)", [('xtime(0x57)', 174), ('xtime(0xae)', 71), ('xtime(0x80)', 27), ('xtime(0)', 0)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
