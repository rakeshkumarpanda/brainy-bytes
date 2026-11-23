# 3.1 Blockchain security: hash chains, mining, consensus and wallets
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


# ================================================================== task 1: Check a hash chain
# Each block is a dict with keys n, prev, data and hash, where hash is the SHA-256 hex of
# f"{n}|{prev}|{data}". Write chain_valid(chain) that returns the index of the first bad block
# (stored hash wrong, or prev not equal to the hash before), or -1 if the chain is valid.
# Hint: Loop with enumerate. Recompute each hash with bh, then compare prev with the previous
# block’s hash.

import hashlib

def bh(n, prev, data):
    return hashlib.sha256(f"{n}|{prev}|{data}".encode()).hexdigest()

def make(datas):
    chain, prev = [], "0" * 64
    for i, d in enumerate(datas):
        h = bh(i, prev, d)
        chain.append({"n": i, "prev": prev, "data": d, "hash": h})
        prev = h
    return chain

def chain_valid(chain):
    # your code here
    pass


# ================================================================== task 2: Check a proof of work
# Write meets_target(data, nonce, zeros) that returns True when the SHA-256 hex of f"{data}|{nonce}"
# starts with zeros zero characters. Then write first_nonce(data, zeros) that returns the smallest
# nonce from 0 upward that meets the target.
# Hint: startswith("0" * zeros) does the check. first_nonce keeps adding 1 until meets_target is
# True.

import hashlib

def meets_target(data, nonce, zeros):
    # your code here
    pass

def first_nonce(data, zeros):
    # your code here
    pass


# ================================================================== task 3: Build a Merkle root
# Write merkle_root(items) for a non empty list of strings. Hash each item with SHA-256 (hex). Then,
# while more than one hash is left, join neighbours as h(left + right), pairing an odd last hash
# with itself. Return the final hex string.
# Hint: Make the first level with a list comprehension. In the loop, copy the last hash when the
# length is odd, then hash pairs.

import hashlib

def h(s):
    return hashlib.sha256(s.encode()).hexdigest()

def merkle_root(items):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Check a hash chain", [('chain_valid(make(["genesis", "a pays b 5", "b pays c 2"]))', -1), ('chain_valid([dict(b, data="a pays b 50") if b["n"] == 1 else b for b in make(["genesis", "a pays b 5", "b pays c 2"])])', 1), ('chain_valid([dict(b, prev="0" * 64) if b["n"] == 2 else b for b in make(["genesis", "x", "y"])])', 2), ('chain_valid([])', -1)]))
    results.append(check("Task 2: Check a proof of work", [('meets_target("x", first_nonce("x", 2), 2)', True), ('all(not meets_target("x", n, 2) for n in range(first_nonce("x", 2)))', True), ('meets_target("anything", 0, 0)', True), ('first_nonce("Block 7", 1) < 200', True)]))
    results.append(check("Task 3: Build a Merkle root", [('merkle_root(["a"]) == h("a")', True), ('merkle_root(["a", "b"]) == h(h("a") + h("b"))', True), ('merkle_root(["a", "b", "c"]) == h(h(h("a") + h("b")) + h(h("c") + h("c")))', True), ('merkle_root(["a", "b", "c", "d"]) != merkle_root(["a", "b", "d", "c"])', True)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
