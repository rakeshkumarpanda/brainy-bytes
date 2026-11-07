# 3.2 Lists: storing, changing, sorting and copying
# Example "unpack" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

point = [3, 7]
x, y = point                     # unpack two items
print(x, y)
first, *rest = [10, 20, 30, 40]  # star takes the rest as a list
print(first, rest)
*start, last = "python"
print(start, last)
x, y = y, x                      # swap without a third name
print(x, y)
squares = [n * n for n in range(1, 6)]     # a list comprehension (more in Core 4.3)
evens = [n for n in range(10) if n % 2 == 0]
print(squares, evens)
