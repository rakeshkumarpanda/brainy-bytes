# 1.3 Wireless security: from WEP to WPA3
# Example "wep_flaws" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Why WEP failed: a 24 bit IV repeats quickly, a repeated keystream leaks plaintext, and CRC-32 is not a MAC
import math
import random
import zlib

def rc4(key, n):                         # RC4 keystream, the cipher WEP used
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    out = []
    for _ in range(n):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(S[(S[i] + S[j]) % 256])
    return bytes(out)

root_key = b"\x13\x37\xc0\xde\x42"      # the shared 40 bit WEP key, the same for every packet

# 1. Birthday paradox: how soon does a random 24 bit IV repeat?
N = 2 ** 24
print("packets for a 50% chance of a repeated IV:", round(math.sqrt(2 * math.log(2) * N)))
rng = random.Random(7)
seen, count = set(), 0
while True:
    iv = rng.randrange(N)
    count += 1
    if iv in seen:
        break
    seen.add(iv)
print("this run saw its first repeat after", count, "packets")

# 2. Same IV means same keystream, and XOR of two ciphertexts is XOR of the two plaintexts
iv = b"\x00\x00\x2a"
ks = rc4(iv + root_key, 32)
p1, p2 = b"GET /bank/login HTTP/1.1  ", b"user=asha&pin=4821&go=yes "
c1 = bytes(a ^ b for a, b in zip(p1, ks))
c2 = bytes(a ^ b for a, b in zip(p2, ks))
leak = bytes(a ^ b for a, b in zip(c1, c2))
print("attacker who guesses p1 recovers p2:", bytes(a ^ b for a, b in zip(leak, p1)))

# 3. CRC-32 is linear: flip bits in the message and fix the checksum without the key
msg = b"pay 0100 to bob"
crc = zlib.crc32(msg)
delta = bytes(a ^ b for a, b in zip(msg, b"pay 9900 to eve"))
fixed_crc = crc ^ zlib.crc32(delta) ^ zlib.crc32(bytes(len(msg)))
print("forged message passes the CRC check:", fixed_crc == zlib.crc32(b"pay 9900 to eve"))
