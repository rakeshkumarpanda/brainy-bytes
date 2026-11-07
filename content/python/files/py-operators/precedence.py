# 1.3 Operators, expressions and the order Python works them out
# Example "precedence" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

print(2 + 3 * 4)        # * before +        -> 14
print((2 + 3) * 4)      # brackets first    -> 20
print(-2 ** 2)          # ** before unary - -> -4
print((-2) ** 2)        #                   -> 4
print(2 ** 3 ** 2)      # ** from the right -> 512
print(100 / 10 / 5)     # / from the left   -> 2.0
print(7 - 4 - 2)        # - from the left   -> 1
