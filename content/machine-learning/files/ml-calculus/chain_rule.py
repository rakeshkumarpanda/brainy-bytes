# 2.2 Calculus for ML: derivatives, gradients and gradient descent
# Example "chain_rule" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import math

def sigmoid(z):
    return 1 / (1 + math.exp(-z))

def sigmoid_slope(z):
    s = sigmoid(z)
    return s * (1 - s)              # from the chain rule

# A tiny model: z = w * x, p = sigmoid(z). How does p change when w changes?
x = 2.0
w = 0.5
z = w * x
dp_dz = sigmoid_slope(z)            # outer function
dz_dw = x                           # inner function
dp_dw = dp_dz * dz_dw               # chain rule: multiply the two slopes
print("p =", round(sigmoid(z), 4))
print("dp/dw by the chain rule:", round(dp_dw, 4))

h = 1e-6
numeric = (sigmoid((w + h) * x) - sigmoid((w - h) * x)) / (2 * h)
print("dp/dw by a tiny nudge:  ", round(numeric, 4))
