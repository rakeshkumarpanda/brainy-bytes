# 2.2 Secure development: threat models, scanners, fuzzing and the supply chain
# Example "fuzz" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Coverage guided fuzzing in miniature (the idea behind AFL and libFuzzer): mutate inputs, keep the ones
# that reach new code, and find a bug that random inputs almost never hit.
import random

def parse(data):
    """A toy parser for messages like b'MSG' + length + body. It has a hidden bug."""
    path = []
    if len(data) < 4:
        return path, None
    path.append("len>=4")
    if data[0:1] == b"M":
        path.append("M")
        if data[1:2] == b"S":
            path.append("MS")
            if data[2:3] == b"G":
                path.append("MSG")
                n = data[3]
                body = data[4:]
                if n > len(body):                       # the bug: trusts the length byte, like Heartbleed
                    return path, "CRASH: read past the end of the buffer"
    return path, None

def mutate(rng, data):
    d = bytearray(data)
    op = rng.randrange(3)
    if op == 0 and d:
        d[rng.randrange(len(d))] = rng.randrange(256)    # change a byte
    elif op == 1:
        d.insert(rng.randrange(len(d) + 1), rng.randrange(256))   # insert a byte
    elif d:
        del d[rng.randrange(len(d))]                     # delete a byte
    return bytes(d)

def fuzz(guided, budget=200000, seed=1):
    rng = random.Random(seed)
    corpus, seen = [b"AAAAAAAA"], set()
    for i in range(1, budget + 1):
        parent = rng.choice(corpus) if guided else b"AAAAAAAA"
        child = mutate(rng, parent)
        for _ in range(rng.randrange(4)):
            child = mutate(rng, child)
        path, crash = parse(child)
        if crash:
            return i, child, len(corpus)
        key = tuple(path)
        if guided and key not in seen:                   # new coverage: keep this input
            seen.add(key)
            corpus.append(child)
    return None, None, len(corpus)

for guided in (False, True):
    tries, crasher, size = fuzz(guided)
    name = "coverage guided" if guided else "blind random   "
    print(f"{name}: " + (f"crash after {tries:6} inputs, input {crasher!r}, corpus {size}" if tries else f"no crash in 200000 inputs"))
