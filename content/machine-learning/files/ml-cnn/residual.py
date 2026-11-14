# 2.1 Convolutional neural networks
# Example "residual" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Why residual connections (ResNet) let very deep networks train.
# Compare the gradient that reaches layer 1 in a plain network and in a residual network.
import numpy as np

rng = np.random.default_rng(0)
width, depth = 64, 50
x = rng.normal(size=(128, width))
weights = [rng.normal(scale=0.1 * np.sqrt(2 / width), size=(width, width)) for _ in range(depth)]


def grad_at_first_layer(residual):
    hs, zs = [x], []
    for W in weights:
        z = hs[-1] @ W
        f = np.maximum(z, 0)
        zs.append(z)
        hs.append(hs[-1] + f if residual else f)
    g = np.ones_like(hs[-1]) / len(x)              # gradient of sum(output) / batch
    for W, z in zip(reversed(weights), reversed(zs)):
        branch = (g * (z > 0)) @ W.T
        g = g + branch if residual else branch      # the skip path adds the gradient straight through
    return np.abs(g).mean() * len(x)              # gradient at layer 1 relative to the output gradient


for residual in [False, True]:
    ratio = grad_at_first_layer(residual)
    name = 'residual' if residual else 'plain   '
    print(f'{name} {depth} layers: gradient at layer 1 is {ratio:.2e} times the gradient at the output')

# with the branch weights at zero, a residual block is exactly the identity
h = rng.normal(size=5)
print('zero branch keeps the input:', np.allclose(h + np.maximum(h @ np.zeros((5, 5)), 0), h))
