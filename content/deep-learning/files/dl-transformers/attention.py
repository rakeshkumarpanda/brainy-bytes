# 2.3 Attention and transformers
# Example "attention" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Scaled dot product attention, step by step, with numpy.
import numpy as np


def softmax(s, axis=-1):
    e = np.exp(s - s.max(axis=axis, keepdims=True))
    return e / e.sum(axis=axis, keepdims=True)


def attention(Q, K, V, mask=None):
    d_k = Q.shape[-1]
    scores = Q @ K.T / np.sqrt(d_k)          # how well each query matches each key
    if mask is not None:
        scores = np.where(mask, scores, -1e9)  # blocked positions get almost zero weight
    weights = softmax(scores)                 # each row adds up to 1
    return weights @ V, weights


# 4 tokens, each with a 2 number query, key and value (chosen by hand to be easy to follow)
Q = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 0.0]])
K = np.array([[2.0, 0.0], [0.0, 2.0], [1.0, 1.0], [-1.0, 0.0]])
V = np.array([[10.0, 0.0], [0.0, 10.0], [5.0, 5.0], [0.0, 0.0]])
out, w = attention(Q, K, V)
print('attention weights (row = query, column = key):')
print(np.round(w, 3))
print('outputs:')
print(np.round(out, 2))

# a causal mask: token t may only look at tokens 1..t (used in GPT style decoders)
causal = np.tril(np.ones((4, 4), dtype=bool))
_, w_causal = attention(Q, K, V, causal)
print('causal attention weights:')
print(np.round(w_causal, 3))

# why divide by sqrt(d_k): dot products of random vectors grow with the dimension
rng = np.random.default_rng(0)
for d in [4, 64, 512]:
    q, k = rng.normal(size=(10000, d)), rng.normal(size=(10000, d))
    dots = (q * k).sum(axis=1)
    print(f'd = {d:3d}: std of q.k = {dots.std():6.2f}, after dividing by sqrt(d) = {(dots / np.sqrt(d)).std():.2f}')
