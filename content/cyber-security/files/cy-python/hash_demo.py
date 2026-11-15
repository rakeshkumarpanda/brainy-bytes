# 2.3 Python for security: bytes, hashes, logs, packets and safe code
# Example "hash_demo" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Hashes: a fixed size fingerprint of any data
import hashlib
import hmac
import io

a = hashlib.sha256(b"pay 100 to Riya").hexdigest()
b = hashlib.sha256(b"pay 900 to Riya").hexdigest()
print("A:", a)
print("B:", b)

def bits_different(hex1, hex2):
    x = int(hex1, 16) ^ int(hex2, 16)    # XOR keeps a 1 where the bits differ
    return bin(x).count("1")

print("bits that differ:", bits_different(a, b), "of 256")

# Hash a big file piece by piece, so even a 50 GB file needs little memory
fake_file = io.BytesIO(b"A" * 100000)     # stands in for open("big.iso", "rb")
h = hashlib.sha256()
pieces = 0
while True:
    chunk = fake_file.read(8192)
    if not chunk:
        break
    h.update(chunk)
    pieces = pieces + 1
print("file read in", pieces, "pieces, hash starts", h.hexdigest()[:16])

# Compare secrets with compare_digest, not ==
published = h.hexdigest()
print("download is genuine:", hmac.compare_digest(published, h.hexdigest()))
print("MD5 is", len(hashlib.md5(b"x").hexdigest()) * 4, "bits and broken: never use it for security")
