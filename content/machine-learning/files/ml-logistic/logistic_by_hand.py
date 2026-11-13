# 2.1 Logistic regression: probabilities for classification
# Example "logistic_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import math

hours = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
passed = [0, 0, 0, 0, 1, 0, 1, 1, 1, 1]

def sigmoid(z):
    return 1 / (1 + math.exp(-z))

w = 0.0
b = 0.0
rate = 0.5
n = len(hours)
for epoch in range(2001):
    grad_w = 0.0
    grad_b = 0.0
    loss = 0.0
    for x, y in zip(hours, passed):
        p = sigmoid(w * x + b)
        grad_w = grad_w + (p - y) * x / n
        grad_b = grad_b + (p - y) / n
        loss = loss - (y * math.log(p) + (1 - y) * math.log(1 - p)) / n
    if epoch in (0, 100, 500, 2000):
        print("epoch", str(epoch).rjust(4), " w", round(w, 3), " b", round(b, 3), " log loss", round(loss, 4))
    w = w - rate * grad_w
    b = b - rate * grad_b

print("chance to pass after 3.2 hours:", round(sigmoid(w * 3.2 + b), 3))
print("50% point (decision boundary): x =", round(-b / w, 2), "hours")
