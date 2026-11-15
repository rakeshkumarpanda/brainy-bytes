# 2.2 Attacks and defences in federated learning
# Example "robust_train" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A full federated run with 3 malicious clients out of 10: plain FedAvg against a coordinate wise median
import math
import random
import statistics as st

random.seed(7)
def make(n):
    data = []
    for _ in range(n):
        y = random.randint(0, 1)
        c = 0.7 if y else 0.3
        data.append(([random.gauss(c, 0.12), random.gauss(c, 0.12)], y))
    return data

clients = [make(40) for _ in range(10)]
test = make(300)
MALICIOUS = {7, 8, 9}

def local_update(w, data, bad, steps=20, lr=0.5):
    w = list(w)
    for _ in range(steps):
        g = [0.0, 0.0, 0.0]
        for x, y in data:
            if bad:
                y = 1 - y                                   # flip every label
            p = 1 / (1 + math.exp(-(w[0] * x[0] + w[1] * x[1] + w[2])))
            g = [g[0] + (p - y) * x[0], g[1] + (p - y) * x[1], g[2] + (p - y)]
        w = [w[k] - lr * g[k] / len(data) for k in range(3)]
    if bad:
        w = [v * 3 for v in w]                              # and boost the bad model
    return w

def accuracy(w):
    return sum(((w[0] * x[0] + w[1] * x[1] + w[2]) > 0) == y for x, y in test) / len(test)

for rule in ("mean", "median"):
    w = [0.0, 0.0, 0.0]
    for rnd in range(15):
        locals_ = [local_update(w, d, i in MALICIOUS) for i, d in enumerate(clients)]
        if rule == "mean":
            w = [sum(l[k] for l in locals_) / len(locals_) for k in range(3)]
        else:
            w = [st.median(l[k] for l in locals_) for k in range(3)]
    print(f"{rule:6} aggregation: test accuracy {accuracy(w):.3f}")
