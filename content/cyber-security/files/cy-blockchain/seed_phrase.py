# 3.1 Blockchain security: hash chains, mining, consensus and wallets
# Example "seed_phrase" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Why a 12 word recovery phrase is safe, and why a phrase you invent yourself is not (BIP 39 maths)
import hashlib
import math
import secrets

WORDS = 2048                               # BIP 39 has 2048 words, so each word carries 11 bits
for n_words, ent_bits in ((12, 128), (24, 256)):
    checksum = ent_bits // 32
    print(f"{n_words} words = {n_words * 11} bits = {ent_bits} random bits + {checksum} checksum bits")

entropy = secrets.token_bytes(16)          # 128 random bits from the operating system
check = hashlib.sha256(entropy).digest()[0] >> 4           # the first 4 bits of SHA-256
bits = bin(int.from_bytes(entropy, "big"))[2:].zfill(128) + bin(check)[2:].zfill(4)
indices = [int(bits[i:i + 11], 2) for i in range(0, 132, 11)]
print("word numbers (0 to 2047):", len(indices), "words, all below 2048:", all(i < 2048 for i in indices))

guesses_per_second = 1e12
years = 2 ** 128 / guesses_per_second / (3600 * 24 * 365)
print(f"guessing 2^128 at a trillion a second: {years:.2e} years")

# a human chosen 'brain wallet': 4 common words from a 5,000 word vocabulary
human = 5000 ** 4
print(f"4 common words: {math.log2(human):.1f} bits, found in {human / guesses_per_second:.3f} seconds")
