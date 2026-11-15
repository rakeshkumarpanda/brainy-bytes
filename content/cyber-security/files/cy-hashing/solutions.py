# 1.3 Hash functions, MACs and password storage
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


# ================================================================== task 1: A short hash for experiments
# Write short_hash(text, bits) that returns the first bits bits of SHA-256 of the UTF-8 text, as a
# whole number.
# Why it works: SHA-256("abc") starts with ba78, so 8 bits give 0xba = 186. Short hashes make
# birthday and preimage attacks small enough to run on a laptop.

import hashlib

def short_hash(text, bits):
    full = int(hashlib.sha256(text.encode()).hexdigest(), 16)
    return full >> (256 - bits)


# ================================================================== task 2: HMAC-SHA256 by hand
# Write hmac_tag(key, msg) for byte strings. Hash keys longer than 64 bytes first, pad with zero
# bytes to 64, then return the hex HMAC using ipad 0x36 and opad 0x5c. Do not use the hmac module.
# Why it works: The first test is RFC 4231 test case 2, the official check value for HMAC-SHA256.

import hashlib

def hmac_tag(key, msg):
    if len(key) > 64:
        key = hashlib.sha256(key).digest()
    key = key + bytes(64 - len(key))
    inner_key = bytes([b ^ 0x36 for b in key])
    outer_key = bytes([b ^ 0x5C for b in key])
    inner = hashlib.sha256(inner_key + msg).digest()
    return hashlib.sha256(outer_key + inner).hexdigest()


# ================================================================== task 3: A Merkle root
# Write merkle_root(items) for a list of strings whose length is a power of 2. Leaves are SHA-256 of
# each UTF-8 string. Each parent is SHA-256 of left + right (raw 32 byte digests). Return the root
# as hex.
# Why it works: Hash the raw digests, not their hex text. A list with one item has its leaf hash as
# the root.

import hashlib

def merkle_root(items):
    level = []
    for item in items:
        level.append(hashlib.sha256(item.encode()).digest())
    while len(level) > 1:
        parents = []
        for i in range(0, len(level), 2):
            parents.append(hashlib.sha256(level[i] + level[i + 1]).digest())
        level = parents
    return level[0].hex()


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A short hash for experiments", [('short_hash("abc", 8)', 186), ('short_hash("abc", 16)', 47736), ('short_hash("abc", 4)', 11)]))
    results.append(check("Task 2: HMAC-SHA256 by hand", [('hmac_tag(b"Jefe", b"what do ya want for nothing?")', '5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843'), ('hmac_tag(b"shared secret", b"PAY RIYA 100")', 'e8d3387d800cb5a07006ec9d27f3d03351363b7c56384ce321fa1a838ebecb3b')]))
    results.append(check("Task 3: A Merkle root", [('merkle_root(["a", "b", "c", "d"])', '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'), ('merkle_root(["tx1", "tx2"])', 'bbea820f07f7f89aeea1ab4a354ecea39f2f72accd05c64371522ee371cd0c48'), ('merkle_root(["only"])', 'f905b19542ed08c9a9c26543cca32e5711d207dcffb81b4cdb44ce0b989431c9')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
