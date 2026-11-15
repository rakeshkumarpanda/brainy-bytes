# 1.2 Attacks on machine learning and their defences
# Example "label_flip" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Data poisoning by label flipping, and a defence: drop training points whose label disagrees with their neighbours
import math
import random

random.seed(4)
def make(n):
    data = []
    for _ in range(n):
        y = random.randint(0, 1)                  # 1 = malicious
        c = 0.68 if y else 0.32
        data.append(([random.gauss(c, 0.1), random.gauss(c, 0.1)], y))
    return data

train, test = make(160), make(200)

def fit(data, epochs=80, lr=0.5):
    w, b = [0.0, 0.0], 0.0
    for _ in range(epochs):
        for x, y in data:
            p = 1 / (1 + math.exp(-(w[0] * x[0] + w[1] * x[1] + b)))
            w = [w[0] - lr * (p - y) * x[0], w[1] - lr * (p - y) * x[1]]
            b -= lr * (p - y)
    return w, b

def acc(model, data):
    w, b = model
    return sum(((w[0] * x[0] + w[1] * x[1] + b) > 0) == y for x, y in data) / len(data)

def missed_malicious(model):
    w, b = model
    bad = [x for x, y in test if y == 1]
    return sum((w[0] * x[0] + w[1] * x[1] + b) <= 0 for x in bad)

m0 = fit(train)
print(f"clean training:        test accuracy {acc(m0, test):.3f}, malicious missed {missed_malicious(m0)}")

# the attacker controls part of the training feed and relabels about a quarter of the malicious rows as benign
poisoned = [(x, 0 if (y == 1 and i % 4 == 0) else y) for i, (x, y) in enumerate(train)]
flipped = sum(1 for (a, y1), (c, y2) in zip(train, poisoned) if y1 != y2)
m1 = fit(poisoned)
print(f"{flipped} labels flipped:     test accuracy {acc(m1, test):.3f}, malicious missed {missed_malicious(m1)}")

# defence: k nearest neighbours label check (k = 5); keep a point only if most neighbours agree with its label
def knn_clean(data, k=5):
    keep = []
    for i, (x, y) in enumerate(data):
        d = sorted((math.dist(x, x2), y2) for j, (x2, y2) in enumerate(data) if j != i)[:k]
        if sum(y2 == y for _, y2 in d) > k // 2:
            keep.append((x, y))
    return keep

cleaned = knn_clean(poisoned)
m2 = fit(cleaned)
print(f"after kNN cleaning:    test accuracy {acc(m2, test):.3f}, malicious missed {missed_malicious(m2)}  ({len(poisoned) - len(cleaned)} points dropped)")
