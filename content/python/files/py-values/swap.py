# 1.2 Variables, values, types and numeral systems
# Example "swap" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

a, b = 5, 9          # two names at once (tuple unpacking)
a, b = b, a          # swap without a third variable
print(a, b)
x = y = z = 0        # chained assignment: three names, one object
print(x, y, z)
count = 10
count += 5           # same as count = count + 5
count *= 2
print(count)
