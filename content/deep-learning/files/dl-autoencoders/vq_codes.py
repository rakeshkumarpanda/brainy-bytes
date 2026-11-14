# 3.1 Autoencoders and variational autoencoders
# Example "vq_codes" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Discrete codes, the idea behind VQ-VAE: replace each continuous code by the nearest entry of a codebook.
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

X = load_digits().data / 16.0
pca = PCA(n_components=8, random_state=0).fit(X)
codes = pca.transform(X)                              # continuous 8 number codes (a linear encoder)
cont_err = np.mean((pca.inverse_transform(codes) - X) ** 2)
print(f'continuous 8 number code: error {cont_err:.4f}')

for size in [4, 16, 256]:
    km = KMeans(n_clusters=size, n_init=4, random_state=0).fit(codes)
    quantised = km.cluster_centers_[km.labels_]       # snap each code to its nearest codebook vector
    err = np.mean((pca.inverse_transform(quantised) - X) ** 2)
    print(f'codebook of {size:3d} vectors: {int(np.log2(size))} bits per image, error {err:.4f}')

# an image becomes a token id, so a transformer can model images as sequences of tokens
print('first 10 images as token ids (codebook of 16):', KMeans(n_clusters=16, n_init=4, random_state=0).fit(codes).labels_[:10])
