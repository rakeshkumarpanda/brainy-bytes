# 3.3 Tuples and sets: fixed records and unique items
# Example "speed" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import time

big_list = list(range(1_000_000))
big_set = set(big_list)

start = time.perf_counter()
for _ in range(20):
    999_999 in big_list
list_time = time.perf_counter() - start

start = time.perf_counter()
for _ in range(20):
    999_999 in big_set
set_time = time.perf_counter() - start

print("the list search is more than 100 times slower:", list_time > 100 * set_time)
