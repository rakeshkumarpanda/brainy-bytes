# 1.2 Symmetric encryption: AES, GF(2⁸) and modes of operation
# Example "gf_maths" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Arithmetic in GF(2^8), the field of 256 bytes that AES works in
def xtime(a):                       # multiply by 2: shift left, and reduce if a 9th bit appears
    a = a << 1
    if a & 0x100:
        a = a ^ 0x11B               # x^8 + x^4 + x^3 + x + 1
    return a

def gmul(a, b):                     # multiply: add (XOR) shifted copies, like long multiplication
    result = 0
    while b:
        if b & 1:
            result = result ^ a
        a = xtime(a)
        b = b >> 1
    return result

print("addition is XOR: {57} + {83} =", hex(0x57 ^ 0x83))

a = 0x57
for power in [1, 2, 4, 8, 16]:
    print("{57} x", power, "=", hex(a))
    a = xtime(a)

print("{57} x {83} =", hex(gmul(0x57, 0x83)))
print("{57} x {13} =", hex(gmul(0x57, 0x13)))

for b in range(1, 256):             # every non zero byte has an inverse
    if gmul(0x53, b) == 1:
        print("inverse of {53} is", hex(b))
        break
