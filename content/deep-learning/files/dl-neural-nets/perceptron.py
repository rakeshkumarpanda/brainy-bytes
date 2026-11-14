# 1.1 Neural networks: from perceptrons to MLPs
# Example "perceptron" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Rosenblatt's perceptron (1958): predict 1 if w . x + b > 0, else 0. When it is wrong, nudge w towards the input.
def train(X, y, epochs=20):
    w, b = np.zeros(X.shape[1]), 0.0
    for epoch in range(1, epochs + 1):
        mistakes = 0
        for xi, target in zip(X, y):
            pred = 1 if w @ xi + b > 0 else 0
            if pred != target:
                w += (target - pred) * xi                 # +x when it should have fired, -x when it should not
                b += target - pred
                mistakes += 1
        if mistakes == 0:
            return w, b, epoch
    return w, b, None

rng = np.random.default_rng(0)
X = rng.normal(size=(40, 2))
y = (X[:, 0] + 2 * X[:, 1] > 0.5).astype(int)            # a straight line separates the two classes
w, b, epoch = train(X, y)
print("separable data: no mistakes after epoch", epoch, " w =", w.round(2), " b =", b)

for name, t in [("AND", [0, 0, 0, 1]), ("OR", [0, 1, 1, 1]), ("XOR", [0, 1, 1, 0])]:
    Xg = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
    w, b, epoch = train(Xg, np.array(t), epochs=100)
    preds = [(1 if w @ x + b > 0 else 0) for x in Xg]
    print(f"{name}: targets {t}, predictions {preds}, " + (f"learned in {epoch} epochs" if epoch else "never learned in 100 epochs"))
