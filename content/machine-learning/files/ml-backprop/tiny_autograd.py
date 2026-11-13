# 1.2 Backpropagation and automatic differentiation
# Example "tiny_autograd" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import math
import random

# A tiny automatic differentiation engine. Each Value remembers how it was made, so backward() can apply
# the chain rule through the whole graph in reverse order. PyTorch and JAX do the same thing for arrays.
class Value:
    def __init__(self, data, parents=(), grad_fn=None):
        self.data, self.grad = data, 0.0
        self.parents, self.grad_fn = parents, grad_fn

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other))
        out.grad_fn = lambda: (self._add(out.grad), other._add(out.grad))
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other))
        out.grad_fn = lambda: (self._add(other.data * out.grad), other._add(self.data * out.grad))
        return out

    def tanh(self):
        t = math.tanh(self.data)
        out = Value(t, (self,))
        out.grad_fn = lambda: self._add((1 - t * t) * out.grad)
        return out

    def _add(self, g):
        self.grad += g                                    # gradients add up when a value is used more than once

    def backward(self):
        order, seen = [], set()
        def visit(v):                                     # topological order: every node after its parents
            if id(v) not in seen:
                seen.add(id(v))
                for p in v.parents:
                    visit(p)
                order.append(v)
        visit(self)
        self.grad = 1.0
        for v in reversed(order):
            if v.grad_fn:
                v.grad_fn()

# Check: d/dx of x*x + x at x = 3 is 2x + 1 = 7. The value x is used three times.
x = Value(3.0)
y = x * x + x
y.backward()
print("y =", y.data, " dy/dx =", x.grad)

# Train one tanh neuron to output +1 for (1, 2) and -1 for (-1, -1), using only Value and backward().
random.seed(3)
w = [Value(random.uniform(-1, 1)) for _ in range(2)]
b = Value(0.0)
data = [((1.0, 2.0), 1.0), ((-1.0, -1.0), -1.0)]
for step in range(1, 51):
    loss = Value(0.0)
    for (x1, x2), target in data:
        out = (w[0] * x1 + w[1] * x2 + b).tanh()
        diff = out + (-target)
        loss = loss + diff * diff
    for p in w + [b]:
        p.grad = 0.0                                      # reset, because gradients accumulate
    loss.backward()
    for p in w + [b]:
        p.data -= 0.1 * p.grad
    if step in (1, 10, 50):
        print(f"step {step:2d}: loss {loss.data:.4f}")
print("final outputs:", [round(math.tanh(w[0].data * x1 + w[1].data * x2 + b.data), 3) for (x1, x2), _ in data])
