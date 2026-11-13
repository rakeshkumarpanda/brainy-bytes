# 2.3 Probability and statistics for ML
# Example "entropy_loss" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.metrics import log_loss

def entropy(p):
    p = np.array(p)
    return -np.sum(p * np.log2(p))

print("fair coin entropy:", entropy([0.5, 0.5]), "bit")
print("biased coin 0.9 / 0.1:", round(entropy([0.9, 0.1]), 3), "bits")
print("fair die:", round(entropy([1 / 6] * 6), 3), "bits")

true = np.array([1, 0, 0])          # the real class is the first one
pred = np.array([0.7, 0.2, 0.1])    # what the model said
ce = -np.sum(true * np.log(pred))
print("cross entropy:", round(ce, 4), " equals -ln(0.7)")

p = np.array([0.5, 0.5])
q = np.array([0.9, 0.1])
kl = np.sum(p * np.log(p / q))
print("KL(p || q):", round(kl, 4), " KL(q || p):", round(np.sum(q * np.log(q / p)), 4))

y = [1, 0, 1, 1]
probs = [0.9, 0.2, 0.6, 0.8]
by_hand = -np.mean([np.log(pr) if t == 1 else np.log(1 - pr) for t, pr in zip(y, probs)])
print("log loss by hand:", round(by_hand, 4), " sklearn:", round(log_loss(y, probs), 4))
