# 1.1 What cybersecurity is: goals, threats and layers
# Example "layered_defence" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

import random

# Each layer has a chance to MISS an attack. An attack gets in only if every layer misses it.
layers = [("email filter", 0.3), ("user training", 0.5), ("antivirus", 0.4), ("MFA login", 0.1)]

chance = 1.0
for name, miss in layers:
    chance = chance * miss
print("chance one attack gets through:", round(chance, 4))
print("expected breaches out of 1000:", round(1000 * chance, 1))

# Check it by simulation: send 1000 pretend attacks through the layers
random.seed(7)
got_in = 0
for attack in range(1000):
    passed = True
    for name, miss in layers:
        if random.random() > miss:     # this layer caught it
            passed = False
            break
    if passed:
        got_in = got_in + 1
print("simulated breaches out of 1000:", got_in)
