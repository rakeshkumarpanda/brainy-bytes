# 4.3 lambda, map, filter and comprehensions
# Example "nestedcomp" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

pairs = [(x, y) for x in range(1, 4) for y in "ab"]     # the left for is the outer loop
print(pairs)

matrix = [[1, 2, 3], [4, 5, 6]]
flat = [v for row in matrix for v in row]
print(flat)

transposed = [[row[c] for row in matrix] for c in range(3)]   # a comprehension inside one
print(transposed)

table = [[r * c for c in range(1, 4)] for r in range(1, 4)]
print(table)
