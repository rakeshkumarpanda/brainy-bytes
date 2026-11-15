# 2.3 Differential privacy
# Example "exp_mechanism" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# The exponential mechanism (McSherry and Talwar 2007): pick the best option privately, for example the most
# common weak password pattern in a breach dataset, without revealing exact counts.
import math
import random

random.seed(4)
counts = {"name + year": 410, "123456 style": 395, "keyboard walk": 220, "word + !": 180, "random": 15}
SENS = 1                               # one person changes any count by at most 1

def probabilities(eps):
    weights = {k: math.exp(eps * c / (2 * SENS)) for k, c in counts.items()}
    total = sum(weights.values())
    return {k: w / total for k, w in weights.items()}

for eps in (0.01, 0.05, 0.2):
    p = probabilities(eps)
    print(f"eps {eps}: " + ", ".join(f"{k} {v:.3f}" for k, v in p.items()))

p = probabilities(0.05)
pick = random.choices(list(p), weights=list(p.values()))[0]
print("\nreleased answer with eps 0.05:", pick)
