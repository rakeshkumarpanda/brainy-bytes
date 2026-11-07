# 2.1 Iterators and generators
# Example "infinite" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from itertools import islice
import sys


def fibonacci():
    a, b = 0, 1
    while True:                                # never ends, and that is fine
        yield a
        a, b = b, a + b


print(list(islice(fibonacci(), 10)))           # take only the first 10
for n in fibonacci():
    if n > 1000:
        print("first above 1000:", n)
        break

squares_list = [n * n for n in range(100_000)]
squares_gen = (n * n for n in range(100_000))
print(sys.getsizeof(squares_list) // 1000, "KB for the list")
print(sys.getsizeof(squares_gen), "bytes for the generator")
