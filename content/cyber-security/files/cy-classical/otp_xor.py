# 1.1 Classical ciphers: Caesar, substitution, Vigenère and the one time pad
# Example "otp_xor" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# The one time pad with XOR, and why a pad must never be used twice
import secrets

def xor(a, b):
    out = []
    for i in range(len(a)):
        out.append(a[i] ^ b[i])
    return bytes(out)

p1 = b"ATTACK AT DAWN"
p2 = b"RETREAT AT TEN"
pad = secrets.token_bytes(len(p1))       # truly random, as long as the message

c1 = xor(p1, pad)
print("c1 (looks random):", c1.hex())
print("decrypt c1       :", xor(c1, pad))

# The mistake: the same pad for a second message
c2 = xor(p2, pad)
print("c1 XOR c2 == p1 XOR p2:", xor(c1, c2) == xor(p1, p2))   # the pad cancels out

# If the attacker can guess p1, they get p2 without ever seeing the pad
print("attacker recovers p2:", xor(xor(c1, c2), p1))
