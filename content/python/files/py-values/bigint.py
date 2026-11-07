# 1.2 Variables, values, types and numeral systems
# Example "bigint" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import sys
big = 2 ** 100
print(big)
print(len(str(big)), "digits")
print(sys.maxsize)                 # the largest index a list can have, not a limit on int
print(sys.int_info.bits_per_digit) # CPython stores big ints in chunks of 30 bits
print((2 ** 64).bit_length())
