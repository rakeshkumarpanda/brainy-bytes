# 2.3 Attention and transformers
# Example "transformer_block" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# One transformer encoder block in numpy: multi head attention, residuals, layer norm and a feed forward network.
import numpy as np

rng = np.random.default_rng(0)
T, d_model, n_heads, d_ff = 6, 16, 4, 64
d_head = d_model // n_heads


def softmax(s):
    e = np.exp(s - s.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


def layer_norm(x, eps=1e-5):
    return (x - x.mean(axis=-1, keepdims=True)) / np.sqrt(x.var(axis=-1, keepdims=True) + eps)


def positional_encoding(T, d):
    pos = np.arange(T)[:, None]
    i = np.arange(0, d, 2)[None, :]
    angle = pos / 10000 ** (i / d)
    pe = np.zeros((T, d))
    pe[:, 0::2], pe[:, 1::2] = np.sin(angle), np.cos(angle)
    return pe


W = {name: rng.normal(scale=1 / np.sqrt(d_model), size=(d_model, d_model)) for name in ['q', 'k', 'v', 'o']}
W1 = rng.normal(scale=1 / np.sqrt(d_model), size=(d_model, d_ff))
W2 = rng.normal(scale=1 / np.sqrt(d_ff), size=(d_ff, d_model))


def multi_head_attention(x):
    def split(m):                                  # (T, d_model) -> (heads, T, d_head)
        return m.reshape(T, n_heads, d_head).transpose(1, 0, 2)
    q, k, v = split(x @ W['q']), split(x @ W['k']), split(x @ W['v'])
    weights = softmax(q @ k.transpose(0, 2, 1) / np.sqrt(d_head))   # (heads, T, T)
    heads = weights @ v                                              # (heads, T, d_head)
    joined = heads.transpose(1, 0, 2).reshape(T, d_model)
    return joined @ W['o'], weights


def encoder_block(x):
    a, weights = multi_head_attention(x)
    x = layer_norm(x + a)                          # residual, then layer norm
    f = np.maximum(0, x @ W1) @ W2                 # position wise feed forward network
    return layer_norm(x + f), weights


tokens = rng.normal(size=(T, d_model))             # stand in for 6 word embeddings
x = tokens + positional_encoding(T, d_model)
out, weights = encoder_block(x)
print('input shape', x.shape, '-> output shape', out.shape)
print('attention weights of head 1, each row sums to', np.round(weights[0].sum(axis=1), 3))

# attention has no idea of order: shuffle the tokens and the outputs shuffle the same way
perm = np.array([5, 4, 3, 2, 1, 0])
out_plain, _ = encoder_block(tokens)
out_shuffled, _ = encoder_block(tokens[perm])
print('without positions, shuffling only reorders the outputs:', np.allclose(out_shuffled, out_plain[perm]))

# weights in one block of a real model (biases and layer norm ignored)
for name, d, blocks in [('BERT base', 768, 12), ('GPT 3', 12288, 96)]:
    per_block = 4 * d * d + 2 * d * 4 * d          # Q, K, V, O plus the two feed forward matrices
    print(f'{name}: {per_block / 1e6:.1f} million weights per block, {blocks} blocks, {blocks * per_block / 1e6:,.0f} million in all blocks')
