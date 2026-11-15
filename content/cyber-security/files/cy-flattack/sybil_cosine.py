# 2.2 Attacks and defences in federated learning
# Example "sybil_cosine" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Spotting Sybils (fake clients run by one attacker): their updates point the same way round after round.
# FoolsGold (Fung et al.) lowers the weight of clients whose update history is too similar to another client's.
import math
import random

random.seed(11)
def honest_update():
    return [random.gauss(0, 1) for _ in range(6)]       # honest users have different data, so different directions

goal = [0.0, 0.0, 0.0, 0.0, 2.0, -2.0]                  # the attacker's poisoned direction
history = {f"user{i}": [0.0] * 6 for i in range(1, 6)}
history.update({f"sybil{i}": [0.0] * 6 for i in range(1, 4)})

for rnd in range(5):                                    # add up each client's updates over 5 rounds
    for name in history:
        if name.startswith("sybil"):
            u = [g + random.gauss(0, 0.1) for g in goal]
        else:
            u = honest_update()
        history[name] = [h + v for h, v in zip(history[name], u)]

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))

names = list(history)
for a in names:
    top = max(cosine(history[a], history[b]) for b in names if b != a)
    weight = max(0.0, min(1.0, 1 - top))                # very similar to someone else: weight near 0
    print(f"{a:7} highest similarity to another client {top:5.2f}  -> weight {weight:.2f}")
