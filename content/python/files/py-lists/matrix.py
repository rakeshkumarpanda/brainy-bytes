# 3.2 Lists: storing, changing, sorting and copying
# Example "matrix" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

matrix = [
    [1, 2, 3],
    [4, 5, 6],
]
print(matrix[1][2])            # row 1, column 2
for row in matrix:
    for value in row:
        print(value, end=" ")
    print()

rows = len(matrix)
cols = len(matrix[0])
turned = []                    # transpose: rows become columns
for c in range(cols):
    new_row = []
    for r in range(rows):
        new_row.append(matrix[r][c])
    turned.append(new_row)
print(turned)
