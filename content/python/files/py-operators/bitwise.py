# 1.3 Operators, expressions and the order Python works them out
# Example "bitwise" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

a, b = 12, 10
print(f"a = {a:04b}, b = {b:04b}")
print(f"a & b  = {a & b:04b} = {a & b}")
print(f"a | b  = {a | b:04b} = {a | b}")
print(f"a ^ b  = {a ^ b:04b} = {a ^ b}")
print("~a     =", ~a)             # always -a - 1
print("a << 2 =", a << 2)         # a * 4
print("a >> 2 =", a >> 2)         # a // 4
print("is 13 odd?", 13 & 1 == 1)
