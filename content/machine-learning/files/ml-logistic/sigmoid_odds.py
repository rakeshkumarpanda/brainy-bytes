# 2.1 Logistic regression: probabilities for classification
# Example "sigmoid_odds" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import math

def sigmoid(z):
    return 1 / (1 + math.exp(-z))

for z in [-4, -2, 0, 2, 4]:
    p = sigmoid(z)
    odds = p / (1 - p)
    print("z =", str(z).rjust(2), " probability", round(p, 3), " odds", round(odds, 3), " log odds", round(math.log(odds), 3))
