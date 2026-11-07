# 1.3 Operators, expressions and the order Python works them out
# Example "floor" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

# Floor division rounds DOWN (towards minus infinity), and % follows the divisor's sign
for a, b in [(7, 2), (-7, 2), (7, -2), (-7, -2)]:
    q, r = a // b, a % b
    print(f"{a:3} // {b:2} = {q:3}   {a:3} % {b:2} = {r:3}   check: {q} * {b} + {r} = {q * b + r}")
