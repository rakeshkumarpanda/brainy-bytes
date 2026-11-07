# 5.2 Modules and packages: import, the standard library and pip
# Example "randmod" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import random

random.seed(42)                     # the same seed gives the same "random" numbers
print(random.random())              # a float from 0.0 up to (not including) 1.0
print(random.randint(1, 6))         # a whole number from 1 to 6, both included
print(random.choice(["a", "b", "c"]))
print(random.sample(range(10), 3))  # 3 different items

cards = list(range(1, 11))
random.shuffle(cards)               # changes the list in place
print(cards)
print(random.randrange(0, 100, 10)) # like range: 0, 10, ..., 90
print(round(random.uniform(1.5, 2.5), 3))
