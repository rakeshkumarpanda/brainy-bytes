# 2.3 Differential privacy
# Example "dp_sgd" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# DP-SGD (Abadi et al. 2016) on a tiny logistic regression: clip each example's gradient, add Gaussian noise
import math
import random

random.seed(2)
def make(n):
    out = []
    for _ in range(n):
        y = random.randint(0, 1)
        c = 0.65 if y else 0.35
        out.append(([random.gauss(c, 0.12), random.gauss(c, 0.12)], y))
    return out

train, test = make(600), make(400)

def grad(w, x, y):
    p = 1 / (1 + math.exp(-(w[0] * x[0] + w[1] * x[1] + w[2])))
    return [(p - y) * x[0], (p - y) * x[1], p - y]

def accuracy(w):
    return sum(((w[0] * x[0] + w[1] * x[1] + w[2]) > 0) == y for x, y in test) / len(test)

def train_model(private, C=1.0, sigma=1.0, batch=60, steps=300, lr=0.5):
    w = [0.0, 0.0, 0.0]
    for _ in range(steps):
        sample = random.sample(train, batch)
        total = [0.0, 0.0, 0.0]
        for x, y in sample:
            g = grad(w, x, y)
            if private:
                norm = math.sqrt(sum(v * v for v in g))
                g = [v * min(1, C / norm) for v in g] if norm > 0 else g   # 1. clip to length C
            total = [t + v for t, v in zip(total, g)]
        if private:
            total = [t + random.gauss(0, sigma * C) for t in total]         # 2. add noise to the sum
        w = [wi - lr * t / batch for wi, t in zip(w, total)]
    return w

print(f"ordinary SGD:             test accuracy {accuracy(train_model(False)):.3f}")
for sigma in (0.5, 4.0, 30.0):
    print(f"DP-SGD, noise sigma {sigma:4}: test accuracy {accuracy(train_model(True, sigma=sigma)):.3f}")
print(f"\nsampling rate q = 60 / 600 = {60 / 600}. A privacy accountant turns q, sigma and the number of steps into (eps, delta).")
