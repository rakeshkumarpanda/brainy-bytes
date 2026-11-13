# Deep learning 1.2: backpropagation. Checked against Goodfellow, Bengio and Courville, Deep Learning (MIT Press 2016)
# sections 6.5 and 8.2, Linnainmaa (1970, reverse mode automatic differentiation), Werbos (1974), Rumelhart, Hinton and
# Williams, Learning representations by back-propagating errors (Nature 1986), Baydin and colleagues, Automatic
# differentiation in machine learning: a survey (JMLR 2018), Glorot and Bengio (AISTATS 2010), He and colleagues,
# Delving deep into rectifiers (ICCV 2015), Pascanu, Mikolov and Bengio (ICML 2013), and the Stanford CS231n notes.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-backprop')
K = Kit()

K.code('chain_rule', r'''
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
''')

K.code('tiny_autograd', r'''
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
''', long=True)

K.code('backprop_mlp', r'''
import numpy as np

# Backpropagation for a 2 layer network with ReLU and softmax, written with matrices, plus a gradient check.
rng = np.random.default_rng(0)
N, D, H, C = 90, 2, 16, 3                                 # 90 points, 2 features, 16 hidden units, 3 classes
X = np.vstack([rng.normal(loc=m, scale=1.0, size=(30, 2)) for m in ([0, 1], [1, -0.5], [-1, -0.5])])
y = np.repeat([0, 1, 2], 30)
params = {"W1": rng.normal(0, 0.5, (D, H)), "b1": np.zeros(H), "W2": rng.normal(0, 0.5, (H, C)), "b2": np.zeros(C)}

def loss_and_grads(p):
    z1 = X @ p["W1"] + p["b1"]                            # forward
    h = np.maximum(0, z1)
    s = h @ p["W2"] + p["b2"]
    s = s - s.max(axis=1, keepdims=True)
    probs = np.exp(s) / np.exp(s).sum(axis=1, keepdims=True)
    loss = -np.log(probs[np.arange(N), y]).mean()
    ds = probs.copy()                                     # backward: softmax + cross entropy gives probs - one hot
    ds[np.arange(N), y] -= 1
    ds /= N
    g = {"W2": h.T @ ds, "b2": ds.sum(0)}
    dh = ds @ p["W2"].T
    dz1 = dh * (z1 > 0)                                   # ReLU passes the gradient only where z1 > 0
    g["W1"], g["b1"] = X.T @ dz1, dz1.sum(0)
    return loss, g

loss, grads = loss_and_grads(params)
for name in ["W1", "W2"]:                                 # gradient check on 3 random entries of each matrix
    errs = []
    for _ in range(3):
        idx = tuple(rng.integers(n) for n in params[name].shape)
        old = params[name][idx]
        params[name][idx] = old + 1e-5
        up = loss_and_grads(params)[0]
        params[name][idx] = old - 1e-5
        down = loss_and_grads(params)[0]
        params[name][idx] = old
        num = (up - down) / 2e-5
        errs.append(abs(num - grads[name][idx]) / max(1e-12, abs(num) + abs(grads[name][idx])))
    print(f"gradient check {name}: largest relative error {max(errs):.1e}")

for step in range(1, 301):                                # train with plain gradient descent
    loss, grads = loss_and_grads(params)
    for k in params:
        params[k] -= 0.5 * grads[k]
    if step in (1, 50, 300):
        h = np.maximum(0, X @ params["W1"] + params["b1"])
        acc = ((h @ params["W2"] + params["b2"]).argmax(1) == y).mean()
        print(f"step {step:3d}: loss {loss:.4f}, accuracy {acc:.3f}")
''', long=True)

K.code('vanishing', r'''
import numpy as np

# How big is the gradient at each layer of a deep network? Push a batch through 20 layers, send a gradient of 1s
# back from the top, and measure its size at every layer.
def gradient_sizes(act, init, depth=20, width=64, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(256, width))
    Ws, zs = [], []
    for _ in range(depth):
        scale = {"small": 0.01, "xavier": np.sqrt(1 / width), "he": np.sqrt(2 / width)}[init]
        W = rng.normal(0, scale, (width, width))
        z = x @ W
        x = 1 / (1 + np.exp(-z)) if act == "sigmoid" else np.tanh(z) if act == "tanh" else np.maximum(0, z)
        Ws.append(W); zs.append(z)
    g, sizes = np.ones_like(x), []
    for W, z in zip(reversed(Ws), reversed(zs)):          # backward, from the top layer down to the first
        if act == "sigmoid":
            s = 1 / (1 + np.exp(-z)); g = g * s * (1 - s)
        elif act == "tanh":
            g = g * (1 - np.tanh(z) ** 2)
        else:
            g = g * (z > 0)
        g = g @ W.T
        sizes.append(np.abs(g).mean())
    return sizes[::-1]                                    # sizes[0] is the first layer

print("average gradient size at layers 1, 5, 10, 15 and 20 (layer 20 is next to the output)")
for act, init in [("sigmoid", "xavier"), ("tanh", "small"), ("tanh", "xavier"), ("relu", "xavier"), ("relu", "he")]:
    s = gradient_sizes(act, init)
    print(f"{act:7s} with {init:6s} init:", "  ".join(f"{s[i]:.1e}" for i in (0, 4, 9, 14, 19)))
''', long=True)

K.lesson('idea', 'The chain rule on a computational graph', f'''
{src('Goodfellow, Bengio and Courville (2016) section 6.5, and the Stanford CS231n notes on backpropagation.')}
{viz('mlcompgraph')}
{wwh('<b>Backpropagation</b> computes the gradient of the loss with respect to every weight by applying the <b>chain rule</b> backwards through a <b>computational graph</b>. The forward pass computes and stores every intermediate value. The backward pass starts from the loss with gradient 1 and, at each node, multiplies the incoming gradient by the node’s local derivative.',
     'Training needs the gradient of one number, the loss, with respect to millions of weights. Backpropagation gets all of them for roughly the cost of two forward passes, whatever the number of weights. Without it, deep learning would be impossibly slow.',
     'Learn three patterns. An <b>add</b> node passes its gradient unchanged to both inputs. A <b>multiply</b> node sends each input the gradient times the other input. A function node such as sigmoid multiplies by its own slope, &sigma;(1 &minus; &sigma;). When a value feeds several nodes, add up the gradients that come back.')}
{run('chain_rule')}
{note('For f = (x y + z) w followed by a sigmoid and a squared error, the backward pass gives &part;L/&part;x = 0.0887 and &part;L/&part;w = &minus;0.1774. Nudging x and w by 0.00001 in each direction gives the same numbers to four decimals. This numerical check is how libraries test their gradients.', 'exam')}
{fxs(fx('Chain rule', '&part;L/&part;x = (&part;L/&part;u)(&part;u/&part;x)', 'Multiply local slopes along the path.', key=True),
     fx('Add and multiply gates', 'u = a + b: &part;u/&part;a = 1. &nbsp; u = ab: &part;u/&part;a = b', 'Add passes, multiply swaps.', key=True),
     fx('Several paths', '&part;L/&part;x = &Sigma;<sub>paths</sub> &Pi; local slopes', 'Gradients add where a value branches.', key=True))}
{link('ml-maths', 'Need a refresher on derivatives and the chain rule?', 'The Maths for Machine Learning subject covers derivatives, partial derivatives, gradients and the chain rule with worked examples.', 'Open Maths for Machine Learning')}
''', kw=['backpropagation', 'chain rule', 'computational graph', 'forward pass', 'backward pass', 'local gradient'])

K.lesson('autograd', 'Automatic differentiation', f'''
{src('Linnainmaa (1970), Baydin, Pearlmutter, Radul and Siskind, Automatic differentiation in machine learning: a survey (JMLR 2018), and the PyTorch autograd documentation.')}
{wwh('<b>Automatic differentiation</b> (autodiff) records each operation as it runs, building the graph on the fly, and then walks it backwards to compute exact gradients. Backpropagation is <b>reverse mode</b> autodiff. PyTorch, TensorFlow and JAX all work this way, so you write only the forward pass.',
     'Deriving gradients by hand for every new model is slow and error prone. Autodiff gives exact derivatives (not approximations like finite differences) at a cost of a small constant times the forward pass, for any program built from differentiable pieces.',
     'Each value stores its data, its gradient, its parents and a small function that pushes its gradient to the parents. backward() sorts the graph so every node comes after its inputs, sets the output gradient to 1, and calls those functions in reverse order. Reset gradients to 0 before each step, because they accumulate.')}
{run('tiny_autograd')}
{note('In about forty lines, the engine gets d(x&middot;x + x)/dx = 7 at x = 3, adding the three contributions from the three uses of x. It then trains a tanh neuron from a loss of 3.7673 to 0.0047 in 50 steps, and the neuron outputs 0.98 and &minus;0.935 for targets +1 and &minus;1.', 'exam')}
{table(['Way to get gradients', 'Exact', 'Cost for n inputs, one output', 'Used for'], [
    ['By hand', 'Yes, if no mistakes', 'Human time', 'Small models, exams'],
    ['Finite differences', 'No, approximate', 'About n + 1 or 2n evaluations', 'Checking gradients'],
    ['Symbolic', 'Yes', 'Expressions can blow up in size', 'Computer algebra systems'],
    ['Forward mode autodiff', 'Yes', 'n passes', 'Few inputs, many outputs'],
    ['Reverse mode (backprop)', 'Yes', 'About 1 forward plus 1 backward pass', 'Neural networks: many inputs, one loss']])}
{fxs(fx('Reverse mode cost', 'cost(&nabla;L) &le; c &middot; cost(L), c a small constant', 'The cheap gradient principle.', key=True),
     fx('Accumulation', '&part;L/&part;v += &part;L/&part;u &middot; &part;u/&part;v for every child u of v', 'Why gradients must be zeroed each step.', key=True))}
''', kw=['automatic differentiation', 'autograd', 'reverse mode', 'forward mode', 'PyTorch', 'topological sort'])

K.lesson('matrix', 'Backpropagation with matrices, and gradient checking', f'''
{src('Goodfellow, Bengio and Courville (2016) section 6.5.4, and the Stanford CS231n notes on gradient checks.')}
{wwh('Real networks process a whole batch at once with matrix operations, and their gradients are matrix formulas too. For a dense layer Z = XW + <b>b</b>, the gradients are &part;L/&part;W = X<sup>T</sup>(&part;L/&part;Z), &part;L/&part;<b>b</b> = column sums of &part;L/&part;Z, and &part;L/&part;X = (&part;L/&part;Z)W<sup>T</sup>. A <b>gradient check</b> compares these with finite differences.',
     'Vectorised gradients run fast on CPUs and GPUs. A gradient check catches the most common bug in a hand written backward pass, and it is worth running whenever you write a new layer.',
     'Match shapes: a gradient always has the same shape as the thing it is a gradient of, which tells you where the transposes go. For softmax with cross entropy, the gradient of the scores is simply the probabilities minus the one hot labels, divided by the batch size. Check with the relative error |a &minus; n| / (|a| + |n|), which should be below about 1e&minus;7 in double precision.')}
{run('backprop_mlp')}
{note('The hand written backward pass agrees with finite differences to a relative error of 7.9e&minus;10 for W1 and 5.6e&minus;10 for W2. Training on 90 overlapping points from 3 classes takes the loss from 1.2295 to 0.3874 and accuracy to 0.822.', 'exam')}
{fxs(fx('Dense layer gradients', '&part;L/&part;W = X<sup>T</sup>G, &nbsp; &part;L/&part;<b>b</b> = &Sigma;<sub>rows</sub> G, &nbsp; &part;L/&part;X = GW<sup>T</sup>', 'G = &part;L/&part;Z.', key=True),
     fx('Softmax with cross entropy', '&part;L/&part;<b>z</b> = <b>p</b> &minus; <b>y</b>', 'Probabilities minus one hot.', key=True),
     fx('ReLU backward', '&part;L/&part;z = &part;L/&part;h &middot; [z &gt; 0]', 'Blocks the gradient where the unit was off.', key=True),
     fx('Gradient check', 'rel = |a &minus; n| / (|a| + |n|), n = (L(&theta; + h) &minus; L(&theta; &minus; h)) / 2h', 'Use h near 1e&minus;5.'))}
''', kw=['matrix backpropagation', 'dense layer gradient', 'softmax cross entropy gradient', 'gradient check', 'finite differences'])

K.lesson('vanish', 'Vanishing and exploding gradients', f'''
{src('Hochreiter (1991), Bengio, Simard and Frasconi (1994), Glorot and Bengio (AISTATS 2010), He and colleagues (ICCV 2015 and CVPR 2016), and Pascanu, Mikolov and Bengio (ICML 2013).')}
{viz('mlvanish')}
{wwh('Backpropagation multiplies by each layer’s weights and activation slope on the way down. If those factors are mostly below 1, the gradient shrinks exponentially with depth and early layers stop learning: <b>vanishing gradients</b>. If they are above 1, it grows exponentially: <b>exploding gradients</b>.',
     'This is why deep networks were hard to train before about 2010, and why recurrent networks struggle with long sequences. The fixes, careful initialisation, ReLU, normalisation and residual connections, are what make 100 layer networks possible.',
     'Initialise weights so the signal keeps its size: <b>Xavier</b> (Glorot) variance 2/(n<sub>in</sub> + n<sub>out</sub>) for tanh, <b>He</b> variance 2/n<sub>in</sub> for ReLU. Use ReLU family activations. Add normalisation layers and residual connections (chapter 1.3 and 2.1). <b>Clip</b> the gradient norm to stop explosions.')}
{run('vanishing')}
{note('With 20 layers, sigmoid with Xavier initialisation shrinks the gradient from 1.8e&minus;1 at the top to 9.0e&minus;14 at layer 1. Tanh with tiny weights (0.01) is even worse, 6.0e&minus;23. ReLU with Xavier shrinks it about 250 times. ReLU with He initialisation keeps it between 1.1 and 3.3 at every layer.', 'exam')}
{fxs(fx('Gradient through L layers', '&part;L/&part;<b>h</b><sub>1</sub> = &Pi;<sub>l</sub> (W<sub>l</sub><sup>T</sup> diag(&phi;&prime;(<b>z</b><sub>l</sub>))) &part;L/&part;<b>h</b><sub>L</sub>', 'A product of L factors.', key=True),
     fx('Xavier initialisation', 'Var(W) = 2 / (n<sub>in</sub> + n<sub>out</sub>)', 'Glorot and Bengio (2010).', key=True),
     fx('He initialisation', 'Var(W) = 2 / n<sub>in</sub>', 'For ReLU: half the units are off, so double the variance.', key=True),
     fx('Gradient clipping', '<b>g</b> &larr; <b>g</b> &middot; min(1, c / ||<b>g</b>||)', 'Pascanu and colleagues (2013).'))}
''', kw=['vanishing gradient', 'exploding gradient', 'Xavier initialisation', 'He initialisation', 'gradient clipping', 'depth'])

K.lesson('versus', 'Ways to compute gradients compared', f'''
{versus('Four ways to get a derivative', ['', 'Finite differences', 'Symbolic', 'Forward mode', 'Reverse mode (backprop)'], [
    ['Accuracy', 'Approximate, rounding errors', 'Exact', 'Exact', 'Exact'],
    ['Cost for n parameters', 'About 2n loss evaluations', 'Can blow up', 'n passes', 'About 2 to 3 passes'],
    ['Memory', 'Small', 'Large expressions', 'Small', 'Stores all forward values'],
    ['Best for', 'Testing gradients', 'Formulas on paper', 'Few inputs', 'Neural networks']],
    'use reverse mode autodiff for training, finite differences only to test a new backward pass.')}
''', kw=['finite differences vs autodiff', 'forward vs reverse mode'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Chain rule', 'dL/dx = (dL/du)(du/dx)', 'One path.', key=True),
     fx('Multivariable chain rule', '&part;L/&part;x = &Sigma;<sub>i</sub> (&part;L/&part;u<sub>i</sub>)(&part;u<sub>i</sub>/&part;x)', 'Sum over every child u<sub>i</sub>.', key=True),
     fx('Sigmoid derivative', '&sigma;&prime;(z) = &sigma;(z)(1 &minus; &sigma;(z))', 'Reuses the forward value.', key=True),
     fx('Dense layer', '&part;L/&part;W = X<sup>T</sup>G, &part;L/&part;X = GW<sup>T</sup>', 'Shapes decide the transposes.', key=True),
     fx('Softmax cross entropy', '&part;L/&part;z<sub>i</sub> = p<sub>i</sub> &minus; y<sub>i</sub>', 'Clean and stable.'),
     fx('Backward memory', 'O(number of stored activations)', 'Gradient checkpointing trades compute for memory.'))}
{steps('Worked example: the softmax and cross entropy gradient', [
    'Scores <b>z</b>, probabilities p<sub>i</sub> = e<sup>z<sub>i</sub></sup> / &Sigma;<sub>j</sub> e<sup>z<sub>j</sub></sup>, true class k, loss L = &minus;ln p<sub>k</sub> = &minus;z<sub>k</sub> + ln &Sigma;<sub>j</sub> e<sup>z<sub>j</sub></sup>.',
    eq('&part;L/&part;z<sub>i</sub> = &minus;[i = k] + e<sup>z<sub>i</sub></sup> / &Sigma;<sub>j</sub> e<sup>z<sub>j</sub></sup> = p<sub>i</sub> &minus; [i = k]'),
    'Example: p = (0.7, 0.2, 0.1) and k = 0.',
    eq('&part;L/&part;<b>z</b> = (0.7 &minus; 1, 0.2, 0.1) = (&minus;0.3, 0.2, 0.1)'),
    'The correct class’s score is pushed up, the others down, in proportion to how much probability they wrongly hold.'])}
{deep('Memory, checkpointing and higher derivatives', '<p>Reverse mode needs the values from the forward pass, so its memory grows with the depth of the network and the batch size. For very deep or long models this, not compute, is often the limit. <b>Gradient checkpointing</b> (Chen and colleagues 2016) stores only some activations and recomputes the others during the backward pass, cutting memory for an n layer network from O(n) to O(&radic;n) at the cost of about one extra forward pass. Autodiff can also be applied to itself: differentiating a gradient gives Hessian vector products in about the cost of two gradients, which second order methods and some meta learning algorithms use. JAX exposes this directly with jvp, vjp, grad and hessian transforms.</p>')}
''', kw=['chain rule formula', 'softmax gradient derivation', 'gradient checkpointing', 'Hessian vector product'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>To learn, a network needs to know which way to nudge each weight. Backpropagation works this out by passing blame backwards from the error, layer by layer.</p>',
    '<p>Backpropagate by hand through small graphs, write a tiny autograd engine, implement matrix backprop for an MLP and check it with finite differences.</p>',
    '<p>Derive dense layer and softmax gradients, explain reverse against forward mode, and diagnose vanishing and exploding gradients with initialisation and clipping.</p>',
    '<p>Study autodiff theory and the cheap gradient principle, checkpointing, Hessian vector products, dynamical isometry and signal propagation in deep networks.</p>')}
{grow('Explain how a network finds out which way to change each weight.',
      'Implement and test backpropagation.',
      'Analyse gradient flow through deep networks.')}
''', kw=['beginner', 'expert', 'signal propagation', 'dynamical isometry'])

lc(2236, 'Root Equals Sum of Children', 'root-equals-sum-of-children', 'e', 'Compare the root with the sum of its two children', 'One comparison does it. In a computational graph an add node’s value is exactly the sum of its inputs, which is why its gradient passes straight through. Our helper builds the three node tree from a list.', r"""
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def check_tree(root):
    return root.val == root.left.val + root.right.val


def root_equals_sum(values):
    root = TreeNode(values[0], TreeNode(values[1]), TreeNode(values[2]))
    return check_tree(root)
""", [('root_equals_sum([10, 4, 6])', True), ('root_equals_sum([5, 3, 1])', False)])
lc(1376, 'Time Needed to Inform All Employees', 'time-needed-to-inform-all-employees', 'm', 'Recursion from the head down, taking the slowest branch', 'Build the tree of who manages whom. The time for a manager is their inform time plus the largest time among their reports. Passing a quantity along every path of a tree and combining at each node is the shape of both the forward and the backward pass.', r"""
from collections import defaultdict


def num_of_minutes(n, head_id, manager, inform_time):
    children = defaultdict(list)
    for e, m in enumerate(manager):
        if m != -1:
            children[m].append(e)

    def time(e):
        return inform_time[e] + max((time(c) for c in children[e]), default=0)

    return time(head_id)
""", [('num_of_minutes(1, 0, [-1], [0])', 0), ('num_of_minutes(6, 2, [2, 2, -1, 2, 2, 2], [0, 0, 1, 0, 0, 0])', 1)])
lc(1443, 'Minimum Time to Collect All Apples in a Tree', 'minimum-time-to-collect-all-apples-in-a-tree', 'm', 'Post order: a subtree costs 2 per edge if it holds an apple', 'Search depth first. After visiting a child, add its cost plus 2 for the edge there and back, but only if the child’s subtree has an apple. Computing children first and combining their results on the way back up is exactly the order of the backward pass.', r"""
from collections import defaultdict


def min_time(n, edges, has_apple):
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    def dfs(node, parent):
        total = 0
        for nxt in adj[node]:
            if nxt != parent:
                cost = dfs(nxt, node)
                if cost or has_apple[nxt]:
                    total += cost + 2
        return total

    return dfs(0, -1)
""", [('min_time(7, [[0, 1], [0, 2], [1, 4], [1, 5], [2, 3], [2, 6]], [False, False, True, False, True, True, False])', 8), ('min_time(7, [[0, 1], [0, 2], [1, 4], [1, 5], [2, 3], [2, 6]], [False, False, True, False, False, True, False])', 6), ('min_time(7, [[0, 1], [0, 2], [1, 4], [1, 5], [2, 3], [2, 6]], [False, False, False, False, False, False, False])', 0)])
lc(2192, 'All Ancestors of a Node in a Directed Acyclic Graph', 'all-ancestors-of-a-node-in-a-directed-acyclic-graph', 'm', 'A node’s ancestors are its parents plus their ancestors, memoised', 'Store each node’s parents and compute ancestors recursively with a cache. In a computational graph, a value’s ancestors are everything it depends on, and backpropagation sends gradients to exactly those nodes.', r"""
from collections import defaultdict
from functools import lru_cache


def get_ancestors(n, edges):
    parents = defaultdict(list)
    for a, b in edges:
        parents[b].append(a)

    @lru_cache(maxsize=None)
    def anc(v):
        out = set()
        for p in parents[v]:
            out.add(p)
            out |= anc(p)
        return frozenset(out)

    return [sorted(anc(v)) for v in range(n)]
""", [('get_ancestors(8, [[0, 3], [0, 4], [1, 3], [2, 4], [2, 7], [3, 5], [3, 6], [3, 7], [4, 6]])', [[], [], [], [0, 1], [0, 2], [0, 1, 3], [0, 1, 2, 3, 4], [0, 1, 2, 3]])])
lc(329, 'Longest Increasing Path in a Matrix', 'longest-increasing-path-in-a-matrix', 'h', 'Depth first search with memoisation over a hidden DAG', 'Moving to a strictly larger neighbour can never loop, so the cells form a directed acyclic graph. The best path from a cell is 1 plus the best from any larger neighbour, cached so each cell is solved once. Reusing stored results for every node of a DAG is what makes backpropagation cost about the same as one forward pass.', r"""
from functools import lru_cache


def longest_increasing_path(matrix):
    rows, cols = len(matrix), len(matrix[0])

    @lru_cache(maxsize=None)
    def best(r, c):
        out = 1
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] > matrix[r][c]:
                out = max(out, 1 + best(nr, nc))
        return out

    return max(best(r, c) for r in range(rows) for c in range(cols))
""", [('longest_increasing_path([[9, 9, 4], [6, 6, 8], [2, 1, 1]])', 4), ('longest_increasing_path([[3, 4, 5], [3, 2, 6], [2, 2, 1]])', 4), ('longest_increasing_path([[1]])', 1)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Backpropagation is dynamic programming on a graph. These problems practise an add node, combining results down a tree, post order accumulation from children to parents, finding everything a node depends on, and memoised search over a DAG. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'tree', 'DAG', 'post order', 'memoisation'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Backpropagation</b> applies the <b>chain rule</b> backwards through a computational graph: store values going forward, multiply local slopes coming back.',
    'Add passes gradients through, multiply swaps its inputs, sigmoid multiplies by &sigma;(1 &minus; &sigma;), and gradients <b>add up</b> where a value branches.',
    '<b>Reverse mode autodiff</b> gives every gradient for about the cost of a forward and a backward pass. PyTorch, TensorFlow and JAX do it for you.',
    'Matrix form: &part;L/&part;W = X<sup>T</sup>G, &part;L/&part;X = GW<sup>T</sup>, and softmax with cross entropy gives <b>p</b> &minus; <b>y</b>. Always <b>gradient check</b> a new layer.',
    'Deep products of slopes cause <b>vanishing</b> or <b>exploding</b> gradients. Use ReLU, <b>He</b> or <b>Xavier</b> initialisation, and gradient clipping.'],
    'Deep learning 1.3 covers training in practice: optimisers, normalisation, dropout and learning rate schedules.')}
{files('Three tasks: gradients of (x + y) z, a numerical gradient, and the softmax cross entropy gradient.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Backpropagation computes', ['The forward pass only', 'The gradient of the loss with respect to every weight, using the chain rule backwards', 'The best learning rate', 'The training data'], 1, 'Gradients for all weights.', 'Then gradient descent uses them.')
K.quiz('e', 'An add node in the backward pass', ['Doubles the gradient', 'Passes the incoming gradient unchanged to both inputs', 'Sends zero', 'Swaps the inputs'], 1, 'Local slope 1.', 'Like a distributor.')
K.quiz('e', 'A multiply node u = ab sends to a', ['The gradient times a', 'The gradient times b', 'The gradient unchanged', 'Nothing'], 1, '&part;u/&part;a = b.', 'Multiply swaps its inputs.')
K.quiz('e', 'Why must gradients be reset to zero before each training step in PyTorch style code?', ['To save memory', 'Because gradients accumulate by adding', 'To change the learning rate', 'To shuffle data'], 1, 'They add up.', 'Otherwise old gradients mix with new ones.')
K.quiz('m', 'Reverse mode autodiff is preferred for neural networks because', ['It is approximate', 'It gets the gradient for all parameters of one loss in about one backward pass', 'It needs no memory', 'It works only for linear models'], 1, 'Many inputs, one output.', 'Forward mode would need one pass per parameter.')
K.quiz('m', 'For softmax with cross entropy, the gradient of the scores is', ['The probabilities', 'The probabilities minus the one hot label', 'The label', 'Zero'], 1, 'p &minus; y.', 'Clean and numerically stable.')
K.quiz('m', 'A gradient check compares', ['Two optimisers', 'The analytic gradient with a finite difference estimate', 'Train and test loss', 'Two random seeds'], 1, 'Numerical against analytic.', 'Relative error below about 1e&minus;7 is good.')
K.quiz('m', 'He initialisation uses variance 2/n<sub>in</sub> because', ['It is simpler', 'ReLU zeroes about half the units, so the variance is doubled to keep the signal size', 'Sigmoid needs it', 'It removes biases'], 1, 'Half the units are off.', 'He and colleagues (2015).')
K.quiz('m', 'When a value is used by two later nodes, its gradient is', ['The larger of the two', 'The sum of the gradients from both', 'Their product', 'Undefined'], 1, 'Multivariable chain rule.', 'Accumulate.')
K.quiz('h', 'Vanishing gradients in deep sigmoid networks happen because', ['Sigmoid is not differentiable', 'Backprop multiplies many slopes of at most 0.25, so the product shrinks exponentially', 'The learning rate is too large', 'Biases are zero'], 1, 'Products of small factors.', 'ReLU and good initialisation help.')
K.quiz('h', 'Gradient clipping by norm', ['Sets small gradients to zero', 'Rescales the gradient when its norm exceeds a threshold, keeping its direction', 'Removes biases', 'Clips the weights'], 1, 'g &larr; g &middot; c/||g||.', 'Common in RNNs and transformers.')
K.quiz('h', 'Gradient checkpointing reduces memory by', ['Using smaller weights', 'Storing only some activations and recomputing the rest in the backward pass', 'Skipping the backward pass', 'Using float16 only'], 1, 'Trade compute for memory.', 'O(&radic;n) memory for n layers.')
K.quiz('x', 'In the style of a Stanford CS231n exam: for f = (x + y)z at x = &minus;2, y = 5, z = &minus;4, the gradient &part;f/&part;x is', ['3', '&minus;4', '&minus;12', '1'], 1, 'Through the add, then the multiply.', '&part;f/&part;q = z = &minus;4, and the add passes it on.')
K.quiz('x', 'In the style of a CMU 10-714 exam: for Z = XW with X of shape (N, D) and W of shape (D, H), &part;L/&part;W has shape and formula', ['(N, H), XW', '(D, H), X<sup>T</sup>(&part;L/&part;Z)', '(D, N), W X', '(H, D), Z<sup>T</sup>X'], 1, 'Same shape as W.', 'Shapes force the transpose.')

K.calc('e', 'f = (x + y)z with x = &minus;2, y = 5, z = &minus;4. &part;f/&part;z?', '3', 'The other input of the multiply.', ['q = x + y = 3.', '&part;f/&part;z = q.', eq('3')], check=3)
K.calc('e', 'Same graph. &part;f/&part;x?', '-4', 'z, passed through the add.', ['&part;f/&part;q = z = &minus;4.', 'Add passes it unchanged.', eq('&minus;4')], check=-4)
K.calc('m', 'Local slope of a sigmoid whose output is 0.731?', '0.197', '&sigma;(1 &minus; &sigma;).', ['1 &minus; 0.731 = 0.269.', 'Multiply.', eq('0.731 &times; 0.269 = 0.197')], check=0.1966, tol=0.002)
K.calc('m', 'f(x) = (2x + 1)<sup>2</sup>. f&prime;(1) by the chain rule?', '12', '2(2x + 1) &times; 2.', ['Inner 2x + 1 = 3.', 'Outer slope 2 &times; 3 = 6.', eq('6 &times; 2 = 12')], check=12)
K.calc('m', 'Softmax probabilities (0.7, 0.2, 0.1), true class 0. Gradient of the loss with respect to the first score?', '-0.3', 'p<sub>0</sub> &minus; 1.', ['One hot is (1, 0, 0).', 'p &minus; y.', eq('0.7 &minus; 1 = &minus;0.3')], check=-0.3)
K.calc('m', 'He initialisation for a layer with 50 inputs. Standard deviation of the weights?', '0.2', '&radic;(2/n).', ['2/50 = 0.04.', 'Square root.', eq('0.2')], check=0.2)
K.calc('h', 'Xavier initialisation with n<sub>in</sub> = n<sub>out</sub> = 256. Standard deviation?', '0.0625', '&radic;(2/(n<sub>in</sub> + n<sub>out</sub>)).', ['2/512 = 0.003906.', 'Square root.', eq('0.0625')], check=0.0625)
K.calc('h', 'Central finite differences for a model with 1,000,000 parameters. Loss evaluations needed for one full gradient?', '2000000', 'Two per parameter.', ['L(&theta; + h) and L(&theta; &minus; h).', 'For every parameter.', eq('2 &times; 1,000,000 = 2,000,000')], check=2000000)
K.calc('h', 'Analytic gradient 0.5001, numerical 0.5. Relative error?', '0.0001', '|a &minus; n| / (|a| + |n|).', ['Difference 0.0001.', 'Sum 1.0001.', eq('&asymp; 0.0001')], check=0.0001, tol=0.000002)
K.calc('x', 'In the style of a Stanford CS231n problem: each of 50 layers multiplies the gradient by 0.9. Factor at the first layer?', '0.00515', '0.9<sup>50</sup>.', ['ln 0.9 = &minus;0.10536.', 'Times 50 = &minus;5.268.', eq('e<sup>&minus;5.268</sup> = 0.00515')], check=0.00515, tol=0.00005)

K.assign('add_mul_grads', 'e', 'Gradients of (x + y) z',
         '<p>Write <code>add_mul_grads(x, y, z)</code> that returns the list [&part;f/&part;x, &part;f/&part;y, &part;f/&part;z] for f = (x + y) z, computed with the backward pass rules.</p>',
         """
def add_mul_grads(x, y, z):
    # your code here
    pass
""", [('add_mul_grads(-2, 5, -4)', [-4, -4, 3]), ('add_mul_grads(1, 1, 0)', [0, 0, 2])],
         """
def add_mul_grads(x, y, z):
    q = x + y
    dq = z
    return [dq, dq, q]
""", 'The multiply gives z to q and q to z. The add copies q’s gradient to x and y.', '<p>Compare with the animation’s first graph: the same three numbers appear in red.</p>')
K.assign('numeric_grad', 'm', 'A numerical gradient',
         '<p>Write <code>numeric_grad(f, x, h=1e-5)</code> that estimates f&prime;(x) with the central difference (f(x + h) &minus; f(x &minus; h)) / 2h and rounds it to 4 decimals.</p>',
         """
def numeric_grad(f, x, h=1e-5):
    # your code here
    pass
""", [('numeric_grad(lambda v: v * v, 3.0)', 6.0), ('numeric_grad(lambda v: (2 * v + 1) ** 2, 1.0)', 12.0), ('numeric_grad(lambda v: v ** 3, 2.0)', 12.0)],
         """
def numeric_grad(f, x, h=1e-5):
    return round((f(x + h) - f(x - h)) / (2 * h), 4)
""", 'Evaluate just above and just below x and divide by the gap.', '<p>The central difference has error proportional to h<sup>2</sup>, much smaller than the one sided (f(x + h) &minus; f(x)) / h with error proportional to h.</p>')
K.assign('softmax_ce_grad', 'm', 'The softmax cross entropy gradient',
         '<p>Write <code>softmax_ce_grad(scores, label)</code> that returns the gradient of the cross entropy loss with respect to the scores, softmax(scores) minus the one hot label, each rounded to 4 decimals.</p>',
         """
def softmax_ce_grad(scores, label):
    # your code here
    pass
""", [('softmax_ce_grad([0.0, 0.0], 0)', [-0.5, 0.5]), ('softmax_ce_grad([2.0, 1.0, 0.0], 0)', [-0.3348, 0.2447, 0.09]), ('softmax_ce_grad([1.0, 1.0, 1.0, 1.0], 3)', [0.25, 0.25, 0.25, -0.75])],
         """
import math


def softmax_ce_grad(scores, label):
    m = max(scores)
    e = [math.exp(s - m) for s in scores]
    z = sum(e)
    return [round(v / z - (1.0 if i == label else 0.0), 4) for i, v in enumerate(e)]
""", 'Compute stable softmax probabilities, then subtract 1 at the label.', '<p>The gradient entries always add up to 0, because the probabilities add up to 1 and the one hot label does too.</p>')

K.must('Backpropagation', 'Chain rule backwards on the graph. Store forward values. Add passes, multiply swaps, &sigma;&prime; = &sigma;(1 &minus; &sigma;).')
K.must('Accumulation', 'A value used twice gets the sum of both gradients. Zero gradients before each step.')
K.must('Autodiff', 'Reverse mode: all gradients for about 2 to 3 forward costs. Forward mode: one pass per input.')
K.must('Matrix gradients', '&part;L/&part;W = X<sup>T</sup>G, &part;L/&part;b = row sum of G, &part;L/&part;X = GW<sup>T</sup>. Softmax CE: p &minus; y.')
K.must('Gradient check', 'Central difference with h &asymp; 1e&minus;5, relative error below 1e&minus;7.')
K.must('Gradient flow', 'Vanishing and exploding from products of slopes. He 2/n<sub>in</sub> for ReLU, Xavier for tanh, clip by norm.')

T = K.topic(
    slug='ml-backprop', topic='ml-backprop', step=(1, 'Neural network basics', 'ml-d1', 'Build neural networks from single neurons: perceptrons and multilayer networks, backpropagation, and the tricks that make deep networks train well.', 'Intermediate'),
    title='Backpropagation and automatic differentiation', short='Backpropagation', badge='1.2', minutes=50,
    lead='See how a network finds every gradient: the chain rule on computational graphs, a tiny autograd engine, matrix backpropagation with a gradient check, and vanishing and exploding gradients.',
    desc='backpropagation, chain rule, computational graph, automatic differentiation, reverse mode, forward mode, autograd, gradient check, finite differences, softmax cross entropy gradient, vanishing gradient, exploding gradient, Xavier initialisation, He initialisation, gradient clipping.',
    summary='The chain rule on graphs, autodiff, matrix backprop with gradient checks, and gradient flow through depth.',
    keywords=['backpropagation', 'chain rule', 'automatic differentiation', 'autograd', 'gradient check', 'vanishing gradient', 'exploding gradient', 'He initialisation', 'Xavier initialisation', 'computational graph'],
    recap='<p>Store values going forward, multiply local slopes coming back, and add gradients where values branch. Reverse mode autodiff does this for any program, and good initialisation keeps gradients alive through depth.</p>',
    added='2026-11-13', leet=leet_items())
