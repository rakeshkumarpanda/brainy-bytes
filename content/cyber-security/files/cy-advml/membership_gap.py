# 1.2 Attacks on machine learning and their defences
# Example "membership_gap" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Membership inference (Shokri et al. 2017): a model that memorises is more confident on the people it trained on
import math
import random

random.seed(3)
def person():
    # two health measures and a noisy diagnosis: the same measures can come with either label
    x = [random.random(), random.random()]
    y = 1 if x[0] + x[1] + random.gauss(0, 0.35) > 1 else 0
    return x, y

members = [person() for _ in range(100)]      # patients in the training set
others = [person() for _ in range(100)]       # similar people who were not

def confidence(x, y, k):
    """kNN model trained on the members: share of the k nearest members that have label y."""
    near = sorted(members, key=lambda m: math.dist(m[0], x))[:k]
    return sum(1 for _, yy in near if yy == y) / k

def attack(k, threshold):
    # the attacker guesses "member" when the model is very sure about the true label
    tpr = sum(confidence(x, y, k) >= threshold for x, y in members) / len(members)
    fpr = sum(confidence(x, y, k) >= threshold for x, y in others) / len(others)
    return tpr, fpr

def accuracy(data, k):
    return sum(confidence(x, y, k) > 0.5 for x, y in data) / len(data)

for k, name in [(1, "k = 1, memorises"), (25, "k = 25, smooths")]:
    tpr, fpr = attack(k, 1.0 if k == 1 else 0.8)
    print(f"{name:18} train acc {accuracy(members, k):.2f}  test acc {accuracy(others, k):.2f}   "
          f"attack TPR {tpr:.2f}  FPR {fpr:.2f}  advantage {tpr - fpr:+.2f}")
print("\nAdvantage = TPR - FPR. Zero means the attacker learns nothing about who was in the training data.")
