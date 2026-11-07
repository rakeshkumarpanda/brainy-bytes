# 4.1 Complexity, timing and profiling
# Example "profiling" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import cProfile
import pstats


def slow_unique(items):
    result = []
    for item in items:
        if item not in result:                 # a list search inside a loop: O(n * k)
            result.append(item)
    return result


def fast_unique(items):
    return list(dict.fromkeys(items))          # one dict lookup per item: O(n)


def main():
    data = [i % 500 for i in range(5000)]
    return slow_unique(data) == fast_unique(data)


profiler = cProfile.Profile()
profiler.enable()
same = main()
profiler.disable()
print("same answer:", same)

stats = pstats.Stats(profiler)
rows = []
for (filename, line, name), (cc, ncalls, tottime, cumtime, callers) in stats.stats.items():
    if name in ("main", "slow_unique", "fast_unique"):
        rows.append((cumtime, name, ncalls))
rows.sort(reverse=True)
for cumtime, name, ncalls in rows:
    print(f"{name:<12} called {ncalls} time")
print("the slow part is", rows[1][1])
