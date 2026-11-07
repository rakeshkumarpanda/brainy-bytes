# 1.2 Variables, values, types and numeral systems
# Example "bases" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

n = 156
print(bin(n), oct(n), hex(n))        # number to text in base 2, 8, 16
print(int("10011100", 2))            # text in base 2 back to a number
print(int("9c", 16), int("0o234", 0)) # base 0 reads the prefix
print(0b1111 + 0x10)                 # literals in any base are just ints
print(f"{n:b} {n:o} {n:x} {n:#X}")   # format codes do the same
