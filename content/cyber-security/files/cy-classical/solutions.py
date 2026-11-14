# 1.1 Classical ciphers: Caesar, substitution, Vigenère and the one time pad
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


# ================================================================== task 1: A Caesar cipher that keeps spaces
# Write caesar(text, k) for upper case text. Shift every letter A to Z by k places with wrap round.
# Keep every other character as it is. A negative k decrypts.
# Why it works: Python’s % gives a result from 0 to 25 even when k is negative, so the same function
# decrypts.

def caesar(text, k):
    abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    out = ""
    for ch in text:
        if ch in abc:
            out = out + abc[(abc.index(ch) + k) % 26]
        else:
            out = out + ch
    return out


# ================================================================== task 2: Vigenère decryption
# Write vig_decrypt(cipher, key). Both are upper case letters only. Subtract the key letter numbers
# (repeating the key) modulo 26.
# Why it works: LXFOPVEFRNHR with LEMON is the classic textbook example. The key position i %
# len(key) is exactly the repetition that Kasiski exploits.

def vig_decrypt(cipher, key):
    abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    out = ""
    for i in range(len(cipher)):
        c = abc.index(cipher[i])
        k = abc.index(key[i % len(key)])
        out = out + abc[(c - k) % 26]
    return out


# ================================================================== task 3: XOR two byte strings
# Write xor_bytes(a, b) that returns a bytes object where each byte is a[i] XOR b[i]. Both inputs
# have the same length.
# Why it works: XOR with a space (32) flips upper case letters to lower case, which is why the first
# test gives b"ab". This same function is the one time pad, and later the heart of stream ciphers
# and AES rounds.

def xor_bytes(a, b):
    out = []
    for i in range(len(a)):
        out.append(a[i] ^ b[i])
    return bytes(out)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A Caesar cipher that keeps spaces", [('caesar("ATTACK AT DAWN", 3)', 'DWWDFN DW GDZQ'), ('caesar("XYZ", 3)', 'ABC'), ('caesar("DWWDFN", -3)', 'ATTACK'), ('caesar("HI, YOU!", 13)', 'UV, LBH!')]))
    results.append(check("Task 2: Vigenère decryption", [('vig_decrypt("LXFOPVEFRNHR", "LEMON")', 'ATTACKATDAWN'), ('vig_decrypt("ABC", "A")', 'ABC'), ('vig_decrypt("B", "B")', 'A')]))
    results.append(check("Task 3: XOR two byte strings", [('xor_bytes(b"AB", b"  ").decode()', 'ab'), ('len(xor_bytes(b"", b""))', 0), ('list(xor_bytes(bytes([255, 0]), bytes([15, 15])))', [240, 15])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
