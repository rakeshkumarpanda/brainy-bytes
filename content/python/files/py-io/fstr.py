# 1.4 Input, output and formatting text
# Example "fstr" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

name, price, qty = "Notebook", 45.5, 3
print(f"{name} costs {price} rupees")
print(f"{qty} x {price} = {qty * price}")       # any expression works
print(f"{name!r} has {len(name)} letters")       # !r uses repr()
print(f"{price = }")                             # the = shows the expression too
width = 12
print(f"[{name:>{width}}]")                      # a nested value for the width
