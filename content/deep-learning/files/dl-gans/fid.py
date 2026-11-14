# 3.2 Generative adversarial networks
# Example "fid" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Frechet distance (the idea behind FID) between sets of digit images.
# Real FID uses features from an Inception network. Here PCA features of 8 x 8 digits play that role.
import numpy as np
from scipy.linalg import sqrtm
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

X, y = load_digits(return_X_y=True)
X = X / 16.0
rng = np.random.default_rng(0)
idx = rng.permutation(len(X))
train, test, y_train = X[idx[:900]], X[idx[900:]], y[idx[:900]]
pca = PCA(n_components=20).fit(train)


def frechet(a, b):
    fa, fb = pca.transform(a), pca.transform(b)
    mu_a, mu_b = fa.mean(axis=0), fb.mean(axis=0)
    cov_a, cov_b = np.cov(fa, rowvar=False), np.cov(fb, rowvar=False)
    root = sqrtm(cov_a @ cov_b).real
    return np.sum((mu_a - mu_b) ** 2) + np.trace(cov_a + cov_b - 2 * root)


candidates = {
    'other real digits': train,
    'real digits plus noise (std 0.2)': np.clip(train + rng.normal(0, 0.2, train.shape), 0, 1),
    'real digits plus noise (std 0.4)': np.clip(train + rng.normal(0, 0.4, train.shape), 0, 1),
    'only real 1s (mode collapse)': train[y_train == 1],
    'the average image, repeated': np.tile(train.mean(axis=0), (900, 1)) + rng.normal(0, 0.01, (900, 64)),
}
for name, images in candidates.items():
    print(f'{name:34s} distance to the test digits: {frechet(images, test):6.2f}')
