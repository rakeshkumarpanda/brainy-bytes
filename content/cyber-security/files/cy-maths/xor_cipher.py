# 1.3 The maths for security: bits, XOR, mod, counting, probability and entropy
# Example "xor_cipher" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# XOR every byte of a message with a key byte. Doing it twice gives the message back.
message = "HELLO"
key = "K"

secret = []
for i in range(len(message)):
    m = ord(message[i])
    k = ord(key[i % len(key)])   # repeat the key if it is shorter
    secret.append(m ^ k)         # ^ is XOR in Python
print("encrypted bytes:", secret)
print("as hex:", " ".join(format(b, "02X") for b in secret))

back = ""
for i in range(len(secret)):
    k = ord(key[i % len(key)])
    back = back + chr(secret[i] ^ k)
print("decrypted:", back)

# The three rules that make this work
a = 0b1011
print(a ^ a, "(a xor a is 0)")
print(a ^ 0, "(a xor 0 is a)")
