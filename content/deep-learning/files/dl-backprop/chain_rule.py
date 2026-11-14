# 1.2 Backpropagation and automatic differentiation
# Example "chain_rule" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import math

# Backpropagation by hand on a tiny graph: f = (x * y + z) * w, then a sigmoid, then the squared error against 1.
x, y, z, w = 2.0, -1.0, 3.0, 0.5

# forward pass: compute and keep every intermediate value
a = x * y                     # -2
b = a + z                     # 1
c = b * w                     # 0.5
s = 1 / (1 + math.exp(-c))    # sigmoid
loss = (s - 1) ** 2
print(f"forward: a = {a}, b = {b}, c = {c}, s = {s:.4f}, loss = {loss:.4f}")

# backward pass: start with dloss/dloss = 1 and apply the chain rule node by node, from the end to the start
d_s = 2 * (s - 1)             # derivative of (s - 1)^2
d_c = d_s * s * (1 - s)       # sigmoid'(c) = s(1 - s)
d_b = d_c * w                 # c = b * w, so dc/db = w
d_w = d_c * b                 #             dc/dw = b
d_a = d_b * 1                 # b = a + z: an add passes the gradient through unchanged
d_z = d_b * 1
d_x = d_a * y                 # a = x * y: a multiply swaps the inputs
d_y = d_a * x
print(f"backward: d_x = {d_x:.4f}, d_y = {d_y:.4f}, d_z = {d_z:.4f}, d_w = {d_w:.4f}")

# check one gradient with a tiny nudge: (f(x + h) - f(x - h)) / 2h
def f(x, y, z, w):
    s = 1 / (1 + math.exp(-((x * y + z) * w)))
    return (s - 1) ** 2

h = 1e-5
print(f"numerical d_x = {(f(x + h, y, z, w) - f(x - h, y, z, w)) / (2 * h):.4f}   numerical d_w = {(f(x, y, z, w + h) - f(x, y, z, w - h)) / (2 * h):.4f}")
