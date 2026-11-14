# 2.3 Python for security: bytes, hashes, logs, packets and safe code
# Example "random_vs_secrets" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# random is for games and simulations. secrets is for passwords, tokens and keys.
import random
import secrets

random.seed(2026)
first = []
for i in range(6):
    first.append(random.randint(0, 9))

random.seed(2026)
second = []
for i in range(6):
    second.append(random.randint(0, 9))

print("random with the same seed:", first, second, "same:", first == second)

token = secrets.token_hex(16)            # 16 random bytes from the operating system
print("secrets token:", token)
print("length:", len(token), "hex digits =", len(token) * 4, "bits")
print("URL safe token:", secrets.token_urlsafe(16))
