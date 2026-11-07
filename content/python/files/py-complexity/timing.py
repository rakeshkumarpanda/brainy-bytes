# 4.1 Complexity, timing and profiling
# Example "timing" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import timeit

numbers = list(range(100_000))
number_set = set(numbers)

list_time = timeit.timeit(lambda: 99_999 in numbers, number=200)
set_time = timeit.timeit(lambda: 99_999 in number_set, number=200)
print("set lookup is faster:", set_time < list_time)
print("more than 100 times faster:", list_time > 100 * set_time)

# repeat() runs the whole test several times. Keep the smallest time: it has the least noise.
times = timeit.repeat("sum(range(1000))", repeat=5, number=1000)
print("timings:", len(times))
best = min(times)
print("best per call is under 1 second:", best / 1000 < 1)
