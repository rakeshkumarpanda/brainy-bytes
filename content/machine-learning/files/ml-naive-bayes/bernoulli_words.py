# 2.3 Naive Bayes: classify by counting clues
# Example "bernoulli_words" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
from sklearn.naive_bayes import BernoulliNB

# columns: contains "free", contains "win", contains "meeting", contains "lunch"
X = [[1, 1, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0], [1, 1, 0, 1],
     [0, 0, 1, 0], [0, 0, 1, 1], [0, 0, 0, 1], [1, 0, 1, 0]]
y = [1, 1, 1, 1, 0, 0, 0, 0]
model = BernoulliNB(alpha=1.0).fit(X, y)
print("P(word present | spam):", np.round(np.exp(model.feature_log_prob_[1]), 2).tolist())
print("message with free and win:", np.round(model.predict_proba([[1, 1, 0, 0]])[0], 3).tolist())
print("message with only meeting:", np.round(model.predict_proba([[0, 0, 1, 0]])[0], 3).tolist())
