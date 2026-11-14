# 1.3 Training deep networks: optimisers, normalisation and regularisation
# Example "schedules" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Mini-batch SGD on a noisy linear regression: batch size and learning rate schedules.
import math
import numpy as np

rng = np.random.default_rng(0)
n, d = 1000, 5
X = rng.normal(size=(n, d))
true_w = np.array([2.0, -1.0, 0.5, 3.0, -2.0])
y = X @ true_w + rng.normal(scale=1.0, size=n)
best = np.linalg.lstsq(X, y, rcond=None)[0]
best_loss = np.mean((X @ best - y) ** 2) / 2


def train(batch, epochs, schedule, lr0=0.1, seed=1):
    r = np.random.default_rng(seed)
    w = np.zeros(d)
    steps_per_epoch = n // batch
    total = epochs * steps_per_epoch
    t = 0
    for epoch in range(epochs):
        order = r.permutation(n)
        for k in range(steps_per_epoch):
            idx = order[k * batch:(k + 1) * batch]
            g = X[idx].T @ (X[idx] @ w - y[idx]) / batch
            lr = schedule(lr0, t, total)
            w -= lr * g
            t += 1
    return np.mean((X @ w - y) ** 2) / 2 - best_loss, t


def constant(lr0, t, total):
    return lr0


def step_decay(lr0, t, total):
    return lr0 * 0.1 ** (3 * t // total)          # divide by 10 at 1/3 and 2/3


def cosine(lr0, t, total):
    return 0.5 * lr0 * (1 + math.cos(math.pi * t / total))


def warmup_cosine(lr0, t, total, warm=50):
    if t < warm:
        return lr0 * (t + 1) / warm
    return cosine(lr0, t - warm, total - warm)


print(f'best possible loss {best_loss:.4f}')
print('extra loss above the best, batch 8, 6 epochs')
for name, sch in [('constant', constant), ('step decay', step_decay), ('cosine', cosine), ('warmup + cosine', warmup_cosine)]:
    gap, t = train(8, 6, sch)
    print(f'  {name:16s} {gap:.5f}')

print('batch size, constant lr 0.1, 6 epochs')
for batch in [1, 8, 64, 1000]:
    gap, t = train(batch, 6, constant)
    print(f'  batch {batch:4d}: {t:5d} updates, extra loss {gap:.5f}')
