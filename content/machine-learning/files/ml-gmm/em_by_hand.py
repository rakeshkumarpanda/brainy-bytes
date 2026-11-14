# 1.3 Gaussian mixture models and EM
# Example "em_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Heights of ten people (cm): a mix of two groups, but nobody tells us who is in which
x = np.array([150.0, 152, 155, 157, 160, 170, 174, 176, 179, 182])
mu = np.array([155.0, 165.0])        # first guesses for the two means
sd = np.array([10.0, 10.0])
w = np.array([0.5, 0.5])             # mixing weights

def normal(v, m, s):
    return np.exp(-0.5 * ((v - m) / s) ** 2) / (s * np.sqrt(2 * np.pi))

for it in range(1, 11):
    dens = w * normal(x[:, None], mu, sd)              # 10 x 2 table: weight times density
    loglik = np.log(dens.sum(axis=1)).sum()
    r = dens / dens.sum(axis=1, keepdims=True)         # E step: responsibilities
    nk = r.sum(axis=0)                                 # M step: effective counts
    w = nk / len(x)
    mu = (r * x[:, None]).sum(axis=0) / nk
    sd = np.sqrt((r * (x[:, None] - mu) ** 2).sum(axis=0) / nk)
    print("round", it, " log likelihood", round(float(loglik), 3), " means", np.round(mu, 1).tolist(),
          " sds", np.round(sd, 1).tolist(), " weights", np.round(w, 2).tolist())
print("chance that 165 cm belongs to group 2:", round(float((w * normal(165, mu, sd))[1] / (w * normal(165, mu, sd)).sum()), 3))
