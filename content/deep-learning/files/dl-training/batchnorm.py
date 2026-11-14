# 1.3 Training deep networks: optimisers, normalisation and regularisation
# Example "batchnorm" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Batch normalisation and dropout, written by hand with numpy.
import numpy as np

rng = np.random.default_rng(0)


def batchnorm(h, gamma, beta, eps=1e-5):
    mean = h.mean(axis=0)
    var = h.var(axis=0)
    return gamma * (h - mean) / np.sqrt(var + eps) + beta


# 1. A deep tanh network with weights that are a little too small
X = rng.normal(size=(256, 100))
for use_bn in [False, True]:
    h = X
    stds = []
    for layer in range(10):
        W = rng.normal(scale=0.5 / np.sqrt(100), size=(100, 100))
        z = h @ W
        if use_bn:
            z = batchnorm(z, np.ones(100), np.zeros(100))
        h = np.tanh(z)
        stds.append(h.std())
    label = 'with batch norm   ' if use_bn else 'without batch norm'
    print(label, 'activation std at layers 1, 5, 10:', [round(float(stds[i]), 4) for i in (0, 4, 9)])

# 2. Batch norm output: each feature has mean 0 and std 1 before gamma and beta
z = rng.normal(loc=5.0, scale=3.0, size=(64, 3))
out = batchnorm(z, np.array([1.0, 2.0, 1.0]), np.array([0.0, 0.0, 10.0]))
print('feature means after batch norm:', np.round(out.mean(axis=0), 3) + 0.0)
print('feature stds after batch norm: ', np.round(out.std(axis=0), 3))

# 3. Inverted dropout keeps the expected activation the same
a = np.ones(100000)
p_keep = 0.8
mask = rng.random(a.shape) < p_keep
dropped = a * mask / p_keep
print(f'kept fraction {mask.mean():.3f}, mean before {a.mean():.3f}, mean after {dropped.mean():.3f}')
print('at test time dropout is switched off and nothing is rescaled')
