# 1.2 Backpropagation and automatic differentiation
# Example "vanishing" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# How big is the gradient at each layer of a deep network? Push a batch through 20 layers, send a gradient of 1s
# back from the top, and measure its size at every layer.
def gradient_sizes(act, init, depth=20, width=64, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(256, width))
    Ws, zs = [], []
    for _ in range(depth):
        scale = {"small": 0.01, "xavier": np.sqrt(1 / width), "he": np.sqrt(2 / width)}[init]
        W = rng.normal(0, scale, (width, width))
        z = x @ W
        x = 1 / (1 + np.exp(-z)) if act == "sigmoid" else np.tanh(z) if act == "tanh" else np.maximum(0, z)
        Ws.append(W); zs.append(z)
    g, sizes = np.ones_like(x), []
    for W, z in zip(reversed(Ws), reversed(zs)):          # backward, from the top layer down to the first
        if act == "sigmoid":
            s = 1 / (1 + np.exp(-z)); g = g * s * (1 - s)
        elif act == "tanh":
            g = g * (1 - np.tanh(z) ** 2)
        else:
            g = g * (z > 0)
        g = g @ W.T
        sizes.append(np.abs(g).mean())
    return sizes[::-1]                                    # sizes[0] is the first layer

print("average gradient size at layers 1, 5, 10, 15 and 20 (layer 20 is next to the output)")
for act, init in [("sigmoid", "xavier"), ("tanh", "small"), ("tanh", "xavier"), ("relu", "xavier"), ("relu", "he")]:
    s = gradient_sizes(act, init)
    print(f"{act:7s} with {init:6s} init:", "  ".join(f"{s[i]:.1e}" for i in (0, 4, 9, 14, 19)))
