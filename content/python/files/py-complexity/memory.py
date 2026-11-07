# 4.1 Complexity, timing and profiling
# Example "memory" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import sys
import tracemalloc

squares_list = [n * n for n in range(100_000)]
squares_gen = (n * n for n in range(100_000))
print("the list is over 100 KB:", sys.getsizeof(squares_list) > 100_000)
print("the generator is under 1 KB:", sys.getsizeof(squares_gen) < 1_000)
print("same total:", sum(squares_gen) == sum(squares_list))


def peak_memory(func):
    tracemalloc.start()
    func()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


list_peak = peak_memory(lambda: sum([n * n for n in range(100_000)]))
gen_peak = peak_memory(lambda: sum(n * n for n in range(100_000)))
print("the list needs over 10 times more memory:", list_peak > 10 * gen_peak)
numbers = [1, 2, 3]
size_before = sys.getsizeof(numbers)
numbers[0] = 10 ** 50                          # a far bigger number in the same slot
print("same size:", sys.getsizeof(numbers) == size_before)   # shallow: the items are not counted
