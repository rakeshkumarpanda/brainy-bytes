# 1.3 Operators, expressions and the order Python works them out
# Example "compare" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

x = 7
print(x > 5, x == 7, x != 7)
print(1 < x < 10)            # chained: means 1 < x and x < 10
print(3 == 3.0)              # different types, same value
print("apple" < "banana")    # text compares letter by letter
print("Zebra" < "apple")     # capital letters come first (Unicode order)
print(0.1 + 0.2 == 0.3)      # float rounding!
import math
print(math.isclose(0.1 + 0.2, 0.3))
