# 2.2 itertools, functools and operator
# Example "endless" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from itertools import count, cycle, repeat, islice

ticket = count(start=100, step=5)              # 100, 105, 110, ... for ever
print(next(ticket), next(ticket), next(ticket))

players = cycle(["Asha", "Ravi", "Meera"])     # go round and round
turns = []
for turn in range(5):
    turns.append(next(players))
print(turns)

print(list(repeat("-", 3)))
print(list(map(pow, [2, 3, 4], repeat(2))))    # repeat feeds the same value to map
print(list(zip(count(1), "abc")))              # numbering without enumerate
print(list(islice(count(), 2, 12, 3)))         # start 2, stop before 12, step 3
