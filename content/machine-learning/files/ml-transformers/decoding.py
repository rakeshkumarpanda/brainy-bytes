# 2.3 Attention and transformers
# Example "decoding" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# How a GPT style model turns scores into text: temperature, top k, top p, and perplexity.
import numpy as np

words = ['mat', 'sofa', 'roof', 'moon', 'piano']
logits = np.array([3.0, 2.0, 1.0, -1.0, -2.0])     # the model's scores for the next word after "The cat sat on the"


def softmax(z):
    e = np.exp(z - z.max())
    return e / e.sum()


for temp in [0.5, 1.0, 2.0]:
    p = softmax(logits / temp)
    print(f'temperature {temp}: ' + ', '.join(f'{w} {q:.3f}' for w, q in zip(words, p)))

p = softmax(logits)
top_k = np.argsort(p)[::-1][:2]
print('top k = 2 keeps:', [words[i] for i in top_k], 'renormalised to', np.round(p[top_k] / p[top_k].sum(), 3))

order = np.argsort(p)[::-1]
cum = np.cumsum(p[order])
keep = order[:np.searchsorted(cum, 0.9) + 1]
print('top p = 0.9 keeps:', [words[i] for i in keep], f'(they hold {p[keep].sum():.3f} of the probability)')

rng = np.random.default_rng(0)
samples = rng.choice(len(words), size=1000, p=p)
print('1000 samples at temperature 1:', {w: int((samples == i).sum()) for i, w in enumerate(words)})

# perplexity: e to the average negative log probability of the true next words
true_probs = np.array([0.60, 0.25, 0.10, 0.40])
ce = -np.log(true_probs).mean()
print(f'cross entropy {ce:.3f} nats, perplexity {np.exp(ce):.2f}')
print('a model that guesses uniformly over 50,000 tokens has perplexity 50,000')

# attention compares every token with every token: cost grows with T squared
for T in [512, 2048, 8192]:
    print(f'context {T}: {T * T:,} attention scores per head per layer')
