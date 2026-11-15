# 1.3 Hash functions, MACs and password storage
# Example "length_extension" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# The length extension attack on SHA-256(secret + message), with SHA-256 written out in full
import hashlib
import struct

K = []
H0 = []

def is_prime(n):
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            return False
    return True

def frac_bits(x):                        # first 32 bits of the fractional part
    return int((x - int(x)) * 2 ** 32)

n = 2
while len(K) < 64:                       # constants from square and cube roots of primes (FIPS 180-4)
    if is_prime(n):
        if len(H0) < 8:
            H0.append(frac_bits(n ** 0.5))
        K.append(frac_bits(n ** (1 / 3)))
    n = n + 1

def rotr(x, r):
    return ((x >> r) | (x << (32 - r))) & 0xFFFFFFFF

def compress(state, block):              # one 64 byte block updates the 8 word state
    w = list(struct.unpack(">16I", block))
    for i in range(16, 64):
        s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >> 3)
        s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >> 10)
        w.append((w[i - 16] + s0 + w[i - 7] + s1) & 0xFFFFFFFF)
    a, b, c, d, e, f, g, h = state
    for i in range(64):
        t1 = (h + (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + w[i]) & 0xFFFFFFFF
        t2 = ((rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) & 0xFFFFFFFF
        h, g, f, e, d, c, b, a = g, f, e, (d + t1) & 0xFFFFFFFF, c, b, a, (t1 + t2) & 0xFFFFFFFF
    return [(x + y) & 0xFFFFFFFF for x, y in zip(state, [a, b, c, d, e, f, g, h])]

def padding(length):                     # 0x80, zeros, then the length in bits as 8 bytes
    zeros = (55 - length) % 64
    return b"\x80" + b"\x00" * zeros + struct.pack(">Q", length * 8)

def sha256(data, state=None, done=0):
    if state is None:
        state = H0
    data = data + padding(done + len(data))
    for i in range(0, len(data), 64):
        state = compress(state, data[i:i + 64])
    return b"".join(struct.pack(">I", x) for x in state)

print("our SHA-256 matches hashlib:", sha256(b"abc").hex() == hashlib.sha256(b"abc").hexdigest())

# The server signs with SHA-256(secret + message). The attacker sees message and tag, never the secret.
secret = b"k3y-only-server-knows"
message = b"user=riya&role=reader"
tag = hashlib.sha256(secret + message).digest()

guess = 21                               # the attacker tries secret lengths until one works
glue = padding(guess + len(message))
extra = b"&role=admin"
state = list(struct.unpack(">8I", tag))  # the tag IS the internal state after the last block
forged_tag = sha256(extra, state, guess + len(message) + len(glue))
forged_message = message + glue + extra

print("forged message:", forged_message)
print("server accepts the forged tag:", hashlib.sha256(secret + forged_message).digest() == forged_tag)
