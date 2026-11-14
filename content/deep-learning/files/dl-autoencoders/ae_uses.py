# 3.1 Autoencoders and variational autoencoders
# Example "ae_uses" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Two everyday uses of autoencoders, with scikit-learn's MLPRegressor as the network.
import numpy as np
from sklearn.datasets import load_digits
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import roc_auc_score

digits = load_digits()
X, y = digits.data / 16.0, digits.target
rng = np.random.default_rng(0)
idx = rng.permutation(len(X))
tr, te = idx[:1400], idx[1400:]

# 1. Denoising: learn to map a noisy image back to the clean one
noisy = np.clip(X + rng.normal(scale=0.3, size=X.shape), 0, 1)
dae = MLPRegressor(hidden_layer_sizes=(64, 16, 64), max_iter=400, random_state=0)
dae.fit(noisy[tr], X[tr])
cleaned = np.clip(dae.predict(noisy[te]), 0, 1)
print(f'error of the noisy test images:   {np.mean((noisy[te] - X[te]) ** 2):.4f}')
print(f'error after the denoising network: {np.mean((cleaned - X[te]) ** 2):.4f}')

# 2. Anomaly detection: train only on digits 0 to 4, then digits 5 to 9 rebuild badly
normal_tr = tr[y[tr] <= 4]
ae = MLPRegressor(hidden_layer_sizes=(32, 8, 32), max_iter=400, random_state=0)
ae.fit(X[normal_tr], X[normal_tr])
err = np.mean((ae.predict(X[te]) - X[te]) ** 2, axis=1)
is_new = (y[te] >= 5).astype(int)
print(f'average reconstruction error, digits 0 to 4: {err[is_new == 0].mean():.4f}')
print(f'average reconstruction error, digits 5 to 9: {err[is_new == 1].mean():.4f}')
print(f'ROC AUC of using the error to spot digits 5 to 9: {roc_auc_score(is_new, err):.3f}')
