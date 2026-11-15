# 1.3 Wireless security: from WEP to WPA3
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


# ================================================================== task 1: The WPS checksum digit
# Write wps_checksum(pin7) for a 7 digit number. Walk from the rightmost digit: add 3 times that
# digit, then add the next digit once, and repeat. Return (10 − total mod 10) mod 10.
# Why it works: Because this digit is computed, only 107 PINs are valid, and the split confirmation
# cuts the search to 11000.

def wps_checksum(pin7):
    accum = 0
    while pin7:
        accum += 3 * (pin7 % 10)
        pin7 //= 10
        accum += pin7 % 10
        pin7 //= 10
    return (10 - accum % 10) % 10


# ================================================================== task 2: Birthday probability for IVs
# Write iv_repeat(n, bits) that returns the approximate chance that n random IVs of the given size
# contain a repeat: 1 − e−n²/(2N) with N = 2bits, rounded to 2 decimal places.
# Why it works: For 32 bits, 65536 = √N gives n²/2N = 1/2, so 1 − e−0.5 ≈ 0.39.

import math

def iv_repeat(n, bits):
    N = 2 ** bits
    return round(1 - math.exp(-n * n / (2 * N)), 2)


# ================================================================== task 3: Recover a WPA2 pass phrase from a word list
# Write find_passphrase(words, ssid, target_hex). For each word compute PMK = PBKDF2-HMAC-SHA1(word,
# ssid, 4096 rounds, 32 bytes) with hashlib.pbkdf2_hmac, and return the first word whose PMK in hex
# equals target_hex. Return None if no word matches.
# Why it works: Both targets are the test vectors from IEEE 802.11i. Real attacks check the
# handshake MIC instead of the PMK, but the expensive step, PBKDF2 per guess, is the same.

import hashlib

def find_passphrase(words, ssid, target_hex):
    for word in words:
        pmk = hashlib.pbkdf2_hmac("sha1", word.encode(), ssid.encode(), 4096, 32)
        if pmk.hex() == target_hex:
            return word
    return None


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: The WPS checksum digit", [('wps_checksum(1234567)', 0), ('wps_checksum(1111111)', 5), ('wps_checksum(5551234)', 3)]))
    results.append(check("Task 2: Birthday probability for IVs", [('iv_repeat(4823, 24)', 0.5), ('iv_repeat(1000, 24)', 0.03), ('iv_repeat(65536, 32)', 0.39)]))
    results.append(check("Task 3: Recover a WPA2 pass phrase from a word list", [('find_passphrase(["letmein", "password", "qwerty"], "IEEE", "f42c6fc52df0ebef9ebb4b90b38a5f902e83fe1b135a70e23aed762e9710a12e")', 'password'), ('find_passphrase(["ThisIsAPassword"], "ThisIsASSID", "0dc0d6eb90555ed6419756b9a15ec3e3209b63df707dd508d14581f8982721af")', 'ThisIsAPassword'), ('find_passphrase(["abc"], "IEEE", "00" * 32)', None)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
