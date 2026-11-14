# 1.3 The maths for security: bits, XOR, mod, counting, probability and entropy
# Example "to_binary" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Turn a number into binary by dividing by 2 and keeping the remainders
number = 202
n = number
remainders = []
while n > 0:
    remainders.append(n % 2)     # the remainder is the next bit (from the right)
    n = n // 2

bits = ""
for r in reversed(remainders):   # read the remainders from the bottom up
    bits = bits + str(r)
print(number, "in binary is", bits)
print("Python agrees:", bin(number), hex(number))

# A character is stored as a number too
for ch in "Hi!":
    code = ord(ch)
    print(ch, "->", code, "->", format(code, "08b"), "-> hex", format(code, "02X"))
