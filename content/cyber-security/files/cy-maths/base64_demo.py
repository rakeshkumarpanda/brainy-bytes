# 1.3 The maths for security: bits, XOR, mod, counting, probability and entropy
# Example "base64_demo" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

import base64
import math

# Base64 turns any bytes into 64 safe text characters. Every 3 bytes become 4 characters.
data = "Hi!".encode()
text = base64.b64encode(data).decode()
print(data, "->", text)
print("back:", base64.b64decode(text))

for n in [1, 2, 3, 10, 100]:
    print(n, "bytes ->", 4 * math.ceil(n / 3), "Base64 characters")

# Base64 is an ENCODING, not encryption: anyone can decode it
print(base64.b64decode("cGFzc3dvcmQxMjM=").decode())
