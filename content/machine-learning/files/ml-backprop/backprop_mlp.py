# 1.2 Backpropagation and automatic differentiation
# Example "backprop_mlp" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Backpropagation for a 2 layer network with ReLU and softmax, written with matrices, plus a gradient check.
rng = np.random.default_rng(0)
N, D, H, C = 90, 2, 16, 3                                 # 90 points, 2 features, 16 hidden units, 3 classes
X = np.vstack([rng.normal(loc=m, scale=1.0, size=(30, 2)) for m in ([0, 1], [1, -0.5], [-1, -0.5])])
y = np.repeat([0, 1, 2], 30)
params = {"W1": rng.normal(0, 0.5, (D, H)), "b1": np.zeros(H), "W2": rng.normal(0, 0.5, (H, C)), "b2": np.zeros(C)}

def loss_and_grads(p):
    z1 = X @ p["W1"] + p["b1"]                            # forward
    h = np.maximum(0, z1)
    s = h @ p["W2"] + p["b2"]
    s = s - s.max(axis=1, keepdims=True)
    probs = np.exp(s) / np.exp(s).sum(axis=1, keepdims=True)
    loss = -np.log(probs[np.arange(N), y]).mean()
    ds = probs.copy()                                     # backward: softmax + cross entropy gives probs - one hot
    ds[np.arange(N), y] -= 1
    ds /= N
    g = {"W2": h.T @ ds, "b2": ds.sum(0)}
    dh = ds @ p["W2"].T
    dz1 = dh * (z1 > 0)                                   # ReLU passes the gradient only where z1 > 0
    g["W1"], g["b1"] = X.T @ dz1, dz1.sum(0)
    return loss, g

loss, grads = loss_and_grads(params)
for name in ["W1", "W2"]:                                 # gradient check on 3 random entries of each matrix
    errs = []
    for _ in range(3):
        idx = tuple(rng.integers(n) for n in params[name].shape)
        old = params[name][idx]
        params[name][idx] = old + 1e-5
        up = loss_and_grads(params)[0]
        params[name][idx] = old - 1e-5
        down = loss_and_grads(params)[0]
        params[name][idx] = old
        num = (up - down) / 2e-5
        errs.append(abs(num - grads[name][idx]) / max(1e-12, abs(num) + abs(grads[name][idx])))
    print(f"gradient check {name}: largest relative error {max(errs):.1e}")

for step in range(1, 301):                                # train with plain gradient descent
    loss, grads = loss_and_grads(params)
    for k in params:
        params[k] -= 0.5 * grads[k]
    if step in (1, 50, 300):
        h = np.maximum(0, X @ params["W1"] + params["b1"])
        acc = ((h @ params["W2"] + params["b2"]).argmax(1) == y).mean()
        print(f"step {step:3d}: loss {loss:.4f}, accuracy {acc:.3f}")
