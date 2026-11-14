# 3.4 Energy based models: Hopfield networks, Boltzmann machines and RBMs
# Example "dbn_digits" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A deep belief network the classic way: pretrain RBMs one layer at a time without labels, then fine tune the
# whole stack as a deep sigmoid network with backpropagation. Only 100 labelled digits are used for fine tuning.
import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neural_network import BernoulliRBM

X, y = load_digits(return_X_y=True)                                 # 8x8 handwritten digits
X = X / 16.0                                                        # pixels in 0..1, read as probabilities
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
few = np.concatenate([np.where(y_tr == d)[0][:10] for d in range(10)])   # 10 labelled images per digit

# 1. Greedy layer wise pretraining on all 1257 training images, labels never used
rbm1 = BernoulliRBM(n_components=100, learning_rate=0.05, n_iter=80, random_state=0).fit(X_tr)
rbm2 = BernoulliRBM(n_components=50, learning_rate=0.05, n_iter=80, random_state=0).fit(rbm1.transform(X_tr))

sig = lambda x: 1 / (1 + np.exp(-x))


def fine_tune(Ws, bs, epochs=300, lr=0.5):
    """Backpropagation through sigmoid layers plus a softmax output, on the 100 labelled images."""
    Ws = [w.copy() for w in Ws] + [np.random.default_rng(0).normal(0, 0.01, (Ws[-1].shape[1], 10))]
    bs = [b.copy() for b in bs] + [np.zeros(10)]
    Xl, Y = X_tr[few], np.eye(10)[y_tr[few]]
    for _ in range(epochs):
        acts = [Xl]
        for w, b in zip(Ws[:-1], bs[:-1]):
            acts.append(sig(acts[-1] @ w + b))
        z = acts[-1] @ Ws[-1] + bs[-1]
        p = np.exp(z - z.max(axis=1, keepdims=True))
        d = (p / p.sum(axis=1, keepdims=True) - Y) / len(Xl)        # gradient of cross entropy at the output
        for i in range(len(Ws) - 1, -1, -1):
            gW, gb = acts[i].T @ d, d.sum(axis=0)
            if i:
                d = (d @ Ws[i].T) * acts[i] * (1 - acts[i])         # back through a sigmoid layer
            Ws[i] -= lr * gW
            bs[i] -= lr * gb
    a = X_te
    for w, b in zip(Ws[:-1], bs[:-1]):
        a = sig(a @ w + b)
    return np.mean(np.argmax(a @ Ws[-1] + bs[-1], axis=1) == y_te)


rng = np.random.default_rng(1)
print('Deep network 64-100-50-10, fine tuned on 100 labels, test accuracy:')
print(f'  started from the pretrained RBMs:      {fine_tune([rbm1.components_.T, rbm2.components_.T], [rbm1.intercept_hidden_, rbm2.intercept_hidden_]):.3f}')
print(f'  started from tiny random weights:      {fine_tune([rng.normal(0, 0.01, (64, 100)), rng.normal(0, 0.01, (100, 50))], [np.zeros(100), np.zeros(50)]):.3f}')
print(f'  started from scaled random weights:    {fine_tune([rng.normal(0, 1 / 8, (64, 100)), rng.normal(0, 0.1, (100, 50))], [np.zeros(100), np.zeros(50)]):.3f}')
base = LogisticRegression(max_iter=5000).fit(X_tr[few], y_tr[few]).score(X_te, y_te)
print(f'Logistic regression on raw pixels, same 100 labels: {base:.3f}')
