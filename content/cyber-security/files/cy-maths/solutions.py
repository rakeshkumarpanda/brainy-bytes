# 1.3 The maths for security: bits, XOR, mod, counting, probability and entropy
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


# ================================================================== task 1: A number to binary by hand
# Write to_binary(n) that returns the binary digits of a whole number n as a string, using repeated
# division by 2 (do not use bin()). to_binary(0) returns "0".
# Why it works: This is the same repeated division the animation shows. Reading the remainders from
# the bottom up is the same as putting each new bit at the front.

def to_binary(n):
    if n == 0:
        return "0"
    bits = ""
    while n > 0:
        bits = str(n % 2) + bits
        n = n // 2
    return bits


# ================================================================== task 2: XOR two byte lists
# Write xor_bytes(data, key). data and key are lists of numbers from 0 to 255. Return a new list
# where each data byte is XORed with a key byte, repeating the key when it is shorter.
# Why it works: The third test shows that XOR twice with the same key returns the data. A repeating
# key like this is weak, as you will see in the Cryptography section, but every stream cipher uses
# this XOR step.

def xor_bytes(data, key):
    out = []
    for i in range(len(data)):
        out.append(data[i] ^ key[i % len(key)])
    return out


# ================================================================== task 3: Shannon entropy of a string
# Write entropy(text) that returns the Shannon entropy of the characters in text, in bits per
# character, rounded to 3 decimal places. Use math.log2.
# Why it works: Analysts run exactly this over chunks of a file. Chunks near 8 bits per byte are
# probably encrypted or compressed, which in a program often means hidden malware code.

import math

def entropy(text):
    counts = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    h = 0.0
    for c in counts.values():
        p = c / len(text)
        h = h - p * math.log2(p)
    return round(abs(h), 3)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A number to binary by hand", [('to_binary(202)', '11001010'), ('to_binary(0)', '0'), ('to_binary(1)', '1'), ('to_binary(255)', '11111111')]))
    results.append(check("Task 2: XOR two byte lists", [('xor_bytes([72, 73], [75])', [3, 2]), ('xor_bytes([1, 2, 3], [1, 2, 3])', [0, 0, 0]), ('xor_bytes(xor_bytes([10, 20, 30], [7, 9]), [7, 9])', [10, 20, 30])]))
    results.append(check("Task 3: Shannon entropy of a string", [('entropy("aaaa")', 0.0), ('entropy("aabb")', 1.0), ('entropy("abcd")', 2.0), ('entropy("aab")', 0.918)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
