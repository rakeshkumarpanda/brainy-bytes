# Deep learning 1.1: neural networks. Checked against Goodfellow, Bengio and Courville, Deep Learning (MIT Press 2016)
# chapter 6, McCulloch and Pitts (1943), Rosenblatt, The Perceptron (Psychological Review 1958), Novikoff (1962, the
# perceptron convergence theorem), Minsky and Papert, Perceptrons (1969), Rumelhart, Hinton and Williams (Nature
# 1986), Cybenko (1989) and Hornik (1991) on universal approximation, Nair and Hinton (ICML 2010, ReLU), Hendrycks and
# Gimpel (2016, GELU), and the scikit-learn 1.8 MLPClassifier documentation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('dl-neural-nets')
K = Kit()

K.code('perceptron', r'''
import numpy as np

# Rosenblatt's perceptron (1958): predict 1 if w . x + b > 0, else 0. When it is wrong, nudge w towards the input.
def train(X, y, epochs=20):
    w, b = np.zeros(X.shape[1]), 0.0
    for epoch in range(1, epochs + 1):
        mistakes = 0
        for xi, target in zip(X, y):
            pred = 1 if w @ xi + b > 0 else 0
            if pred != target:
                w += (target - pred) * xi                 # +x when it should have fired, -x when it should not
                b += target - pred
                mistakes += 1
        if mistakes == 0:
            return w, b, epoch
    return w, b, None

rng = np.random.default_rng(0)
X = rng.normal(size=(40, 2))
y = (X[:, 0] + 2 * X[:, 1] > 0.5).astype(int)            # a straight line separates the two classes
w, b, epoch = train(X, y)
print("separable data: no mistakes after epoch", epoch, " w =", w.round(2), " b =", b)

for name, t in [("AND", [0, 0, 0, 1]), ("OR", [0, 1, 1, 1]), ("XOR", [0, 1, 1, 0])]:
    Xg = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
    w, b, epoch = train(Xg, np.array(t), epochs=100)
    preds = [(1 if w @ x + b > 0 else 0) for x in Xg]
    print(f"{name}: targets {t}, predictions {preds}, " + (f"learned in {epoch} epochs" if epoch else "never learned in 100 epochs"))
''', long=True)

K.code('mlp_xor', r'''
import numpy as np

# A tiny multilayer perceptron for XOR: 2 inputs, 3 hidden units with tanh, 1 output with a sigmoid.
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
y = np.array([[0], [1], [1], [0]], dtype=float)
rng = np.random.default_rng(1)
W1, b1 = rng.normal(0, 1, (2, 3)), np.zeros(3)
W2, b2 = rng.normal(0, 1, (3, 1)), np.zeros(1)
sigmoid = lambda z: 1 / (1 + np.exp(-z))
lr = 0.5
for step in range(1, 3001):
    h = np.tanh(X @ W1 + b1)                              # forward pass: hidden layer
    p = sigmoid(h @ W2 + b2)                              # output: probability of class 1
    loss = -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
    d_out = (p - y) / len(X)                              # backward pass (chapter 1.2 explains every line)
    dW2, db2 = h.T @ d_out, d_out.sum(0)
    d_h = (d_out @ W2.T) * (1 - h ** 2)
    dW1, db1 = X.T @ d_h, d_h.sum(0)
    W1 -= lr * dW1; b1 -= lr * db1; W2 -= lr * dW2; b2 -= lr * db2
    if step in (1, 100, 500, 3000):
        print(f"step {step:4d}: loss {loss:.4f}, outputs {p.ravel().round(3)}")
print("hidden layer values for the 4 inputs:")
print(np.tanh(X @ W1 + b1).round(2))
print("The hidden units turn the inputs into new features where one straight line can separate XOR.")
''', long=True)

K.code('activations', r'''
import numpy as np

# Common activation functions and their slopes. The slope matters because backpropagation multiplies by it.
z = np.array([-5.0, -1.0, 0.0, 1.0, 5.0])
sig = 1 / (1 + np.exp(-z))
funcs = {
    "sigmoid": (sig, sig * (1 - sig)),
    "tanh": (np.tanh(z), 1 - np.tanh(z) ** 2),
    "ReLU": (np.maximum(0, z), (z > 0).astype(float)),
    "leaky ReLU": (np.where(z > 0, z, 0.01 * z), np.where(z > 0, 1.0, 0.01)),
}
gelu = 0.5 * z * (1 + np.tanh(np.sqrt(2 / np.pi) * (z + 0.044715 * z ** 3)))   # the tanh approximation used in GPT-2
funcs["GELU"] = (gelu, None)
print("z:".ljust(12), z)
for name, (f, df) in funcs.items():
    print(f"{name:11s} value {np.round(f, 3) + 0.0}")
    if df is not None:
        print(f"{'':11s} slope {np.round(df, 3)}")
print("sigmoid's largest slope is", round(float(sig[2] * (1 - sig[2])), 3), "so ten sigmoid layers can shrink a gradient by", 0.25 ** 10)
''')

K.code('mlp_moons', r'''
from sklearn.datasets import make_moons
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

# Two interleaving half circles: no straight line separates them.
X, y = make_moons(n_samples=600, noise=0.25, random_state=0)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0)

logreg = LogisticRegression().fit(X_tr, y_tr)
print(f"logistic regression (a straight line): test accuracy {logreg.score(X_te, y_te):.3f}")
for hidden in [(2,), (8,), (32,), (32, 32)]:
    mlp = MLPClassifier(hidden_layer_sizes=hidden, activation="relu", max_iter=2000, random_state=0).fit(X_tr, y_tr)
    n_params = sum(w.size for w in mlp.coefs_) + sum(b.size for b in mlp.intercepts_)
    print(f"MLP hidden layers {str(hidden):9s}: {n_params:5d} weights, train {mlp.score(X_tr, y_tr):.3f}, test {mlp.score(X_te, y_te):.3f}")
''', long=True)

K.lesson('idea', 'From one neuron to the perceptron', f'''
{src('McCulloch and Pitts (1943), Rosenblatt (1958), Novikoff (1962), and Goodfellow, Bengio and Courville (2016) section 6.1.')}
{viz('mlperceptron')}
{wwh('An artificial <b>neuron</b> computes a weighted sum of its inputs plus a bias, z = <b>w</b> &middot; <b>x</b> + b, and passes it through an <b>activation function</b>. The <b>perceptron</b> uses a step activation: output 1 if z &gt; 0, else 0. Its learning rule adds the input to the weights when it should have fired and subtracts it when it should not.',
     'Every deep network is built from these units. The perceptron is the simplest learning machine that draws a decision boundary, and its failure on XOR explains why we need hidden layers.',
     'For each training point compute the prediction &ycirc;. If it is wrong, update <b>w</b> += &eta;(y &minus; &ycirc;)<b>x</b> and b += &eta;(y &minus; &ycirc;). Repeat over the data until an epoch has no mistakes. If a separating line exists, this always stops.')}
{run('perceptron')}
{note('On 40 points that a line can separate, the perceptron makes no mistakes after epoch 6. It learns AND in 6 epochs and OR in 4, but after 100 epochs on XOR it still predicts [1, 1, 0, 0] for targets [0, 1, 1, 0]. Minsky and Papert’s 1969 book made this limit famous.', 'exam')}
{fxs(fx('Neuron', 'a = &phi;(<b>w</b> &middot; <b>x</b> + b)', '&phi; is the activation function.', key=True),
     fx('Perceptron rule', '<b>w</b> &larr; <b>w</b> + &eta;(y &minus; &ycirc;)<b>x</b>, &nbsp; b &larr; b + &eta;(y &minus; &ycirc;)', 'Only wrong predictions change anything.', key=True),
     fx('Convergence bound', 'mistakes &le; (R / &gamma;)<sup>2</sup>', 'R: largest input size, &gamma;: margin of the best separating line (Novikoff 1962).', key=True))}
{link('ml-maths', 'Need the vectors and dot products behind a neuron?', 'The Maths for Machine Learning subject explains vectors, dot products and matrix multiplication, which is all a layer of neurons computes.', 'Open Maths for Machine Learning')}
''', kw=['neuron', 'perceptron', 'activation', 'perceptron learning rule', 'XOR', 'linear separability'])

K.lesson('mlp', 'Multilayer networks and why hidden layers matter', f'''
{src('Rumelhart, Hinton and Williams (Nature 1986), Cybenko (1989), Hornik (1991), and Goodfellow, Bengio and Courville (2016) sections 6.1 to 6.4.')}
{viz('mlhidden')}
{wwh('A <b>multilayer perceptron</b> (MLP) stacks layers of neurons: inputs, one or more <b>hidden layers</b>, and an output layer. Each layer computes <b>h</b> = &phi;(W<b>x</b> + <b>b</b>). The hidden layers learn new features of the input, and the output layer combines them.',
     'Without a nonlinear activation, stacked layers collapse into one linear map and can only draw straight boundaries. With it, the <b>universal approximation theorem</b> says one hidden layer with enough units can approximate any continuous function on a bounded region as closely as we like. Depth makes many functions far cheaper to represent.',
     'Choose the layer sizes and activations, initialise weights randomly, compute the forward pass, measure the loss, and adjust every weight with gradient descent using backpropagation (chapter 1.2). For classification, end with a sigmoid (two classes) or softmax (many classes) and use cross entropy.')}
{run('mlp_xor')}
{note('A network with 3 tanh hidden units learns XOR: the loss falls from 0.7471 to 0.0018 in 3000 steps and the outputs become 0, 0.998, 0.998 and 0.003. The hidden values show what happened: each input point got new coordinates in which a single line separates the two classes.', 'exam')}
{fxs(fx('Layer', '<b>h</b> = &phi;(W<b>x</b> + <b>b</b>)', 'W has one row per neuron.', key=True),
     fx('Two layer network', '&ycirc; = &sigma;(<b>w</b><sub>2</sub> &middot; tanh(W<sub>1</sub><b>x</b> + <b>b</b><sub>1</sub>) + b<sub>2</sub>)', 'The network used for XOR.', key=True),
     fx('Why nonlinearity', 'W<sub>2</sub>(W<sub>1</sub><b>x</b>) = (W<sub>2</sub>W<sub>1</sub>)<b>x</b>', 'Without &phi;, two layers equal one.', key=True))}
''', kw=['multilayer perceptron', 'MLP', 'hidden layer', 'universal approximation', 'feature learning', 'depth'])

K.lesson('act', 'Activation functions', f'''
{src('Nair and Hinton (ICML 2010), Glorot, Bordes and Bengio, Deep sparse rectifier neural networks (AISTATS 2011), Hendrycks and Gimpel, Gaussian Error Linear Units (2016), and Goodfellow, Bengio and Courville (2016) section 6.3.')}
{wwh('The activation function decides what each neuron passes on. <b>Sigmoid</b> squashes to (0, 1), <b>tanh</b> to (&minus;1, 1), <b>ReLU</b> keeps positive values and zeroes negative ones, <b>leaky ReLU</b> lets a small slope through for negatives, and <b>GELU</b> is a smooth version of ReLU used in transformers. The output layer uses <b>softmax</b> to turn scores into class probabilities.',
     'Backpropagation multiplies the slopes of the activations layer after layer. Sigmoid’s slope is at most 0.25 and almost 0 for large inputs, so gradients vanish in deep sigmoid networks. ReLU has slope 1 for positive inputs, which is a main reason deep networks became trainable around 2010.',
     'Use ReLU or GELU in hidden layers by default. Use sigmoid for a single probability output, softmax for several classes, and no activation for regression outputs. Watch for dead ReLU units that output 0 for every input, and try leaky ReLU if many die.')}
{run('activations')}
{note('Sigmoid’s slope is 0.25 at 0 and 0.007 at &plusmn;5. Tanh’s slope is 1 at 0 but 0 at &plusmn;5 (to three decimals). ReLU’s slope is exactly 1 for every positive input. Multiplying ten sigmoid slopes of at most 0.25 can shrink a gradient by a factor of about one millionth.', 'exam')}
{table(['Activation', 'Formula', 'Range', 'Use'], [
    ['Sigmoid', '1 / (1 + e<sup>&minus;z</sup>)', '(0, 1)', 'Binary output, gates in LSTMs'],
    ['Tanh', '(e<sup>z</sup> &minus; e<sup>&minus;z</sup>) / (e<sup>z</sup> + e<sup>&minus;z</sup>)', '(&minus;1, 1)', 'Recurrent networks, small MLPs'],
    ['ReLU', 'max(0, z)', '[0, &infin;)', 'Default for hidden layers'],
    ['Leaky ReLU', 'max(0.01z, z)', '(&minus;&infin;, &infin;)', 'When many ReLUs die'],
    ['GELU', 'z &Phi;(z)', 'about (&minus;0.17, &infin;)', 'Transformers such as BERT and GPT'],
    ['Softmax', 'e<sup>z<sub>i</sub></sup> / &Sigma;<sub>j</sub> e<sup>z<sub>j</sub></sup>', 'Probabilities summing to 1', 'Multi class output']])}
{fxs(fx('Sigmoid slope', '&sigma;&prime;(z) = &sigma;(z)(1 &minus; &sigma;(z)) &le; 0.25', 'Largest at z = 0.', key=True),
     fx('Tanh slope', 'tanh&prime;(z) = 1 &minus; tanh<sup>2</sup>(z)', 'Equals 1 at z = 0.', key=True),
     fx('Softmax', 'p<sub>i</sub> = e<sup>z<sub>i</sub></sup> / &Sigma;<sub>j</sub> e<sup>z<sub>j</sub></sup>', 'Subtract max z first for numerical safety.', key=True))}
''', kw=['activation function', 'sigmoid', 'tanh', 'ReLU', 'leaky ReLU', 'GELU', 'softmax', 'vanishing gradient'])

K.lesson('sklearn', 'MLPs in practice with scikit-learn', f'''
{src('scikit-learn 1.8 documentation, Neural network models (supervised), MLPClassifier.')}
{wwh('scikit-learn’s <b>MLPClassifier</b> and <b>MLPRegressor</b> train fully connected networks with backpropagation and the Adam optimiser. You choose the hidden layer sizes, the activation and the regularisation strength alpha, and call fit and predict like any other model.',
     'For small tabular problems an MLP in scikit-learn is the quickest way to try a neural network and compare it with logistic regression, trees or boosting under the same cross validation. For images, text or large data, use a deep learning library such as PyTorch or JAX, which run on GPUs.',
     'Scale the inputs (MLPs are sensitive to feature scales), start with one or two hidden layers of 32 to 128 units, set max_iter high enough to converge, and tune alpha and the layer sizes with cross validation. Check training against test accuracy for overfitting.')}
{run('mlp_moons')}
{note('On two noisy half moons, logistic regression reaches 0.861 test accuracy. An MLP with 2 hidden units (9 weights) does no better, 0.856. With 32 units it reaches 0.883, and with two layers of 32 (1185 weights) 0.900, while training accuracy climbs to 0.952. More capacity fits the curve better, but the gap between train and test grows too.', 'exam')}
{table(['Setting', 'Default', 'What it does'], [
    ['hidden_layer_sizes', '(100,)', 'Units in each hidden layer'],
    ['activation', 'relu', 'relu, tanh, logistic or identity'],
    ['solver', 'adam', 'adam, sgd or lbfgs (good for small data)'],
    ['alpha', '0.0001', 'L2 penalty on the weights'],
    ['learning_rate_init', '0.001', 'Step size for adam and sgd'],
    ['early_stopping', 'False', 'Hold out 10% and stop when it stops improving']])}
''', kw=['MLPClassifier', 'scikit-learn', 'hidden_layer_sizes', 'alpha', 'Adam', 'make_moons'])

K.lesson('versus', 'Perceptron, logistic regression and MLP compared', f'''
{versus('Three linear and nonlinear classifiers', ['', 'Perceptron', 'Logistic regression', 'MLP'], [
    ['Output', 'Hard 0 or 1', 'Probability', 'Probability'],
    ['Boundary', 'Straight line', 'Straight line', 'Any shape, given enough units'],
    ['Learning', 'Fix mistakes only', 'Gradient descent on cross entropy', 'Backpropagation on cross entropy'],
    ['Converges', 'Only if separable', 'Yes, convex loss', 'To a local minimum, loss is not convex'],
    ['XOR', 'Cannot', 'Cannot', 'Can']],
    'use logistic regression as a strong simple baseline, and an MLP when the boundary is clearly curved and there is enough data.')}
''', kw=['perceptron vs logistic regression', 'MLP vs linear models'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Neuron', 'a = &phi;(&Sigma;<sub>i</sub> w<sub>i</sub>x<sub>i</sub> + b)', 'Weighted sum, then activation.', key=True),
     fx('Layer in matrix form', '<b>h</b> = &phi;(W<b>x</b> + <b>b</b>)', 'Shape: W is (units out) by (units in).', key=True),
     fx('Number of parameters', 'n<sub>out</sub>(n<sub>in</sub> + 1) per dense layer', 'Weights plus one bias per unit.', key=True),
     fx('Binary cross entropy', 'L = &minus;[y ln &ycirc; + (1 &minus; y) ln(1 &minus; &ycirc;)]', 'Loss for a sigmoid output.', key=True),
     fx('Universal approximation', '|f(<b>x</b>) &minus; &Sigma;<sub>j</sub> v<sub>j</sub>&sigma;(<b>w</b><sub>j</sub> &middot; <b>x</b> + b<sub>j</sub>)| &lt; &epsilon; on a bounded set', 'Cybenko (1989): one hidden layer suffices, given enough units.'),
     fx('ReLU', 'max(0, z), slope 1 for z &gt; 0', 'No vanishing for positive inputs.'))}
{steps('Worked example: XOR with two ReLU units, built by hand', [
    'Hidden units h<sub>1</sub> = ReLU(x<sub>1</sub> + x<sub>2</sub>) and h<sub>2</sub> = ReLU(x<sub>1</sub> + x<sub>2</sub> &minus; 1). Output y = h<sub>1</sub> &minus; 2h<sub>2</sub>.',
    eq('(0, 0): h = (0, 0), y = 0'),
    eq('(0, 1) and (1, 0): h = (1, 0), y = 1'),
    eq('(1, 1): h = (2, 1), y = 2 &minus; 2 = 0'),
    'Two hidden units and three layers of arithmetic compute XOR exactly, which no single perceptron can.'])}
{deep('Why depth helps', '<p>The universal approximation theorem promises that one hidden layer is enough, but not that it is efficient. Some functions need exponentially many units in a shallow network yet only a modest number in a deep one. A classic example is the parity of n bits (XOR of all of them): a deep network can compute it with a number of units that grows in proportion to n, while a network with one hidden layer of threshold units needs a number that grows exponentially. Montufar and colleagues (2014) showed that deep ReLU networks can carve the input space into exponentially more linear regions than shallow ones with the same number of units. In practice depth also matches the structure of data such as images, where edges combine into parts and parts into objects.</p>')}
''', kw=['neuron formula', 'parameter count', 'cross entropy', 'universal approximation theorem', 'depth efficiency'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A neural network is many small calculators in layers. Each one adds up its inputs with weights and passes the result on, and training adjusts the weights until the answers come out right.</p>',
    '<p>Implement a perceptron and a small MLP in NumPy, choose activations, and train MLPs with scikit-learn.</p>',
    '<p>Explain linear separability and XOR, the perceptron convergence bound, why nonlinearity is needed, vanishing gradients, and universal approximation.</p>',
    '<p>Study depth separation results, the number of linear regions of ReLU networks, the loss landscape of overparameterised networks, and the neural tangent kernel.</p>')}
{grow('Explain what a neural network is and why it needs hidden layers.',
      'Build and train small networks in NumPy and scikit-learn.',
      'Analyse capacity, activations and the theory of approximation.')}
''', kw=['beginner', 'expert', 'neural tangent kernel', 'linear regions'])

lc(1486, 'XOR Operation in an Array', 'xor-operation-in-an-array', 'e', 'Build each number and fold them with XOR', 'The numbers are start, start + 2, start + 4 and so on. XOR them one by one. XOR is the function a single perceptron cannot learn, so it is worth knowing well.', r"""
def xor_operation(n, start):
    out = 0
    for i in range(n):
        out ^= start + 2 * i
    return out
""", [('xor_operation(5, 0)', 8), ('xor_operation(4, 3)', 8)])
lc(2433, 'Find The Original Array of Prefix Xor', 'find-the-original-array-of-prefix-xor', 'm', 'XOR neighbouring prefixes to undo them', 'Because a ^ a = 0, the original value at i is pref[i] ^ pref[i &minus; 1]. Undoing a running combination step by step is the same idea as peeling layers back during backpropagation.', r"""
def find_array(pref):
    return [pref[0]] + [pref[i] ^ pref[i - 1] for i in range(1, len(pref))]
""", [('find_array([5, 2, 0, 3, 1])', [5, 7, 2, 3, 2]), ('find_array([13])', [13])])
lc(1442, 'Count Triplets That Can Form Two Arrays of Equal XOR', 'count-triplets-that-can-form-two-arrays-of-equal-xor', 'm', 'Equal XOR halves mean the whole range XORs to 0', 'a == b exactly when arr[i] ^ ... ^ arr[k] is 0, which means two prefix XORs are equal. For each such pair of prefix positions, every split point in between works. Turning a condition into a simpler hidden feature is what hidden layers do.', r"""
def count_triplets(arr):
    prefix = [0]
    for x in arr:
        prefix.append(prefix[-1] ^ x)
    total = 0
    for i in range(len(prefix)):
        for k in range(i + 1, len(prefix)):
            if prefix[i] == prefix[k]:
                total += k - i - 1
    return total
""", [('count_triplets([2, 3, 1, 6, 7])', 4), ('count_triplets([1, 1, 1, 1, 1])', 10)])
lc(421, 'Maximum XOR of Two Numbers in an Array', 'maximum-xor-of-two-numbers-in-an-array', 'm', 'Decide the answer one bit at a time, from the top', 'Try to set each bit of the answer from the highest down. Keep the set of prefixes of the numbers and check whether two prefixes XOR to the answer you want. Building a result greedily, bit by bit, mirrors how a deep network builds features layer by layer.', r"""
def find_maximum_xor(nums):
    best = 0
    for bit in range(31, -1, -1):
        best <<= 1
        prefixes = {x >> bit for x in nums}
        want = best | 1
        if any((want ^ p) in prefixes for p in prefixes):
            best = want
    return best
""", [('find_maximum_xor([3, 10, 5, 25, 2, 8])', 28), ('find_maximum_xor([14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70])', 127)])
lc(1707, 'Maximum XOR With an Element From Array', 'maximum-xor-with-an-element-from-array', 'h', 'Sort queries by their limit and grow a binary trie', 'Answer queries in order of their limit m, inserting every number up to m into a trie of bits. For each query walk the trie, choosing the opposite bit whenever possible. Processing inputs in a clever order so that one structure serves every query is a common trick in efficient training pipelines.', r"""
def maximize_xor(nums, queries):
    nums = sorted(nums)
    order = sorted(range(len(queries)), key=lambda i: queries[i][1])
    trie, ans, j = {}, [-1] * len(queries), 0
    for qi in order:
        x, m = queries[qi]
        while j < len(nums) and nums[j] <= m:
            node = trie
            for bit in range(29, -1, -1):
                node = node.setdefault((nums[j] >> bit) & 1, {})
            j += 1
        if not trie:
            continue
        node, val = trie, 0
        for bit in range(29, -1, -1):
            b = (x >> bit) & 1
            if 1 - b in node:
                val |= 1 << bit
                node = node[1 - b]
            else:
                node = node[b]
        ans[qi] = val
    return ans
""", [('maximize_xor([0, 1, 2, 3, 4], [[3, 1], [1, 3], [5, 6]])', [3, 3, 7]), ('maximize_xor([5, 2, 4, 6, 6, 3], [[12, 4], [8, 1], [6, 3]])', [15, -1, 5])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>XOR is the classic function a single neuron cannot compute, so this set is all about it: folding a sequence with XOR, undoing prefix XORs, turning equal halves into a zero range, and finding the largest XOR with greedy bits and a trie. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'XOR', 'bit manipulation', 'prefix XOR', 'trie'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>neuron</b> computes &phi;(<b>w</b> &middot; <b>x</b> + b). The <b>perceptron</b> uses a step function and fixes its mistakes by adding or subtracting the input.',
    'The perceptron converges when a line separates the classes, within (R/&gamma;)<sup>2</sup> mistakes, but it can never learn <b>XOR</b>.',
    'A <b>multilayer perceptron</b> adds hidden layers with nonlinear activations. Hidden units learn new features, and one hidden layer can approximate any continuous function.',
    '<b>ReLU</b> and <b>GELU</b> are the default hidden activations. Sigmoid and tanh saturate and cause <b>vanishing gradients</b>. Softmax turns scores into probabilities.',
    'scikit-learn’s <b>MLPClassifier</b> is a quick way to try networks on tabular data. Scale the inputs and watch the train and test gap.'],
    'Deep learning 1.2 explains backpropagation: how every weight gets its gradient.')}
{files('Three tasks: a single neuron, perceptron training, and the forward pass of a small MLP.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'A single artificial neuron computes', ['A sorted list', 'An activation applied to a weighted sum of inputs plus a bias', 'The mean of its inputs', 'A random number'], 1, '&phi;(w &middot; x + b).', 'The building block of every network.')
K.quiz('e', 'The perceptron changes its weights when', ['Every time it sees a point', 'Only when its prediction is wrong', 'Only at the end', 'Never'], 1, 'Mistake driven.', '(y &minus; &ycirc;) is 0 for correct predictions.')
K.quiz('e', 'Which function can a single perceptron not learn?', ['AND', 'OR', 'XOR', 'NOT'], 2, 'Not linearly separable.', 'Minsky and Papert (1969).')
K.quiz('e', 'ReLU outputs', ['1 / (1 + e<sup>&minus;z</sup>)', 'max(0, z)', 'tanh(z)', 'z<sup>2</sup>'], 1, 'Zero for negatives.', 'The default hidden activation.')
K.quiz('m', 'Why do hidden layers need a nonlinear activation?', ['To run faster', 'Without one, stacked linear layers equal a single linear layer', 'To reduce memory', 'To avoid biases'], 1, 'W<sub>2</sub>W<sub>1</sub> is one matrix.', 'Nonlinearity lets the boundary curve.')
K.quiz('m', 'Sigmoid networks suffer from vanishing gradients because', ['Sigmoid is too fast', 'Its slope is at most 0.25 and near 0 for large inputs, and backprop multiplies slopes', 'It has no bias', 'It outputs negatives'], 1, 'Products of small numbers.', 'ReLU’s slope is 1 for positive inputs.')
K.quiz('m', 'The universal approximation theorem says', ['Deep networks always generalise', 'One hidden layer with enough units can approximate any continuous function on a bounded set', 'Training always finds the global minimum', 'Networks need no data'], 1, 'Representation, not learning.', 'It says nothing about how to find the weights.')
K.quiz('m', 'How many parameters does a dense layer from 784 inputs to 128 units have?', ['784', '100,352', '100,480', '128'], 2, 'Weights plus biases.', '784 &times; 128 + 128.')
K.quiz('m', 'Which output layer suits a 10 class problem?', ['ReLU', 'Softmax with cross entropy', 'Tanh', 'No activation with squared error'], 1, 'Probabilities summing to 1.', 'One output per class.')
K.quiz('h', 'The perceptron convergence theorem bounds the number of mistakes by', ['The number of points', '(R / &gamma;)<sup>2</sup>, with R the largest input norm and &gamma; the margin', 'The number of features', 'It gives no bound'], 1, 'Novikoff (1962).', 'Independent of how many points there are.')
K.quiz('h', 'A dead ReLU unit is one that', ['Outputs very large values', 'Outputs 0 for every input, so it gets no gradient and stops learning', 'Has no weights', 'Uses sigmoid'], 1, 'Stuck in the negative region.', 'Leaky ReLU or careful initialisation helps.')
K.quiz('h', 'Compared with logistic regression on the half moons data, an MLP with two hidden layers of 32 units', ['Is worse on test data', 'Fits the curved boundary better but shows a larger train and test gap', 'Is identical', 'Cannot be trained'], 1, '0.900 against 0.861 test accuracy.', 'More capacity, more risk of overfitting.')
K.quiz('x', 'In the style of an MIT 6.036 exam: a network computes y = W<sub>2</sub>(W<sub>1</sub>x + b<sub>1</sub>) + b<sub>2</sub> with no activation. Its decision boundary for classification is', ['Any curve', 'A single hyperplane', 'Two hyperplanes', 'A circle'], 1, 'Linear maps compose to a linear map.', 'Equivalent to one layer.')
K.quiz('x', 'In the style of a Stanford CS229 exam: why can depth be more efficient than width?', ['Deep networks have fewer layers', 'Some functions, such as n bit parity, need exponentially many units in one hidden layer but far fewer in a deep network', 'Width is not allowed', 'Depth removes the need for data'], 1, 'Depth separation.', 'Deep ReLU networks also make exponentially more linear regions.')

K.calc('e', 'Neuron with w = (0.5, &minus;1), b = 0.5, input x = (2, 1) and sigmoid activation. Output?', '0.622', 'z first, then &sigma;.', ['z = 1 &minus; 1 + 0.5 = 0.5.', '&sigma;(0.5) = 1/(1 + e<sup>&minus;0.5</sup>).', eq('1/1.607 = 0.622')], check=0.6225, tol=0.002)
K.calc('e', 'Perceptron with w = (0, 0), b = 0 sees x = (1, 2) with label 1 and predicts 0. Learning rate 1. New w<sub>2</sub>?', '2', 'w += (y &minus; &ycirc;)x.', ['y &minus; &ycirc; = 1.', 'w = (0, 0) + (1, 2).', eq('w<sub>2</sub> = 2')], check=2)
K.calc('m', 'Parameters in an MLP with layers 2, 32, 32, 1?', '1185', 'n<sub>out</sub>(n<sub>in</sub> + 1) per layer.', ['32 &times; 3 = 96.', '32 &times; 33 = 1056, then 1 &times; 33 = 33.', eq('96 + 1056 + 33 = 1185')], check=1185)
K.calc('m', 'Parameters in an MLP with layers 784, 128, 10?', '101770', 'Two dense layers.', ['128 &times; 785 = 100,480.', '10 &times; 129 = 1290.', eq('100,480 + 1290 = 101,770')], check=101770)
K.calc('m', 'Largest sigmoid slope multiplied over 5 layers?', '0.000977', '0.25<sup>5</sup>.', ['0.25<sup>2</sup> = 0.0625.', '0.0625<sup>2</sup> &times; 0.25.', eq('0.25<sup>5</sup> = 0.000977')], check=0.000977, tol=0.00001)
K.calc('m', 'Slope of tanh at z = 1?', '0.42', '1 &minus; tanh<sup>2</sup>.', ['tanh 1 = 0.7616.', 'Square: 0.580.', eq('1 &minus; 0.580 = 0.42')], check=0.42, tol=0.002)
K.calc('h', 'Perceptron data with largest input norm R = 2 and margin &gamma; = 0.5. Upper bound on mistakes?', '16', '(R/&gamma;)<sup>2</sup>.', ['R/&gamma; = 4.', 'Square it.', eq('16')], check=16)
K.calc('h', 'Softmax of logits (2, 1, 0). Probability of the first class?', '0.665', 'e<sup>2</sup> / (e<sup>2</sup> + e + 1).', ['e<sup>2</sup> = 7.389, e = 2.718.', 'Sum 11.107.', eq('7.389 / 11.107 = 0.665')], check=0.6652, tol=0.002)
K.calc('h', 'h<sub>1</sub> = ReLU(x<sub>1</sub> + x<sub>2</sub>), h<sub>2</sub> = ReLU(x<sub>1</sub> + x<sub>2</sub> &minus; 1), y = h<sub>1</sub> &minus; 2h<sub>2</sub>. Output for x = (1, 1)?', '0', 'Compute both units.', ['h<sub>1</sub> = 2.', 'h<sub>2</sub> = 1.', eq('y = 2 &minus; 2 = 0')], check=0)
K.calc('x', 'In the style of an MIT 6.036 problem: binary cross entropy for label y = 1 and prediction &ycirc; = 0.8?', '0.223', '&minus;ln &ycirc;.', ['Only the y ln &ycirc; term remains.', 'ln 0.8 = &minus;0.223.', eq('L = 0.223')], check=0.2231, tol=0.002)

K.assign('neuron', 'e', 'A single neuron',
         '<p>Write <code>neuron(x, w, b, act)</code> that returns &phi;(w &middot; x + b) rounded to 4 decimals, where act is "sigmoid", "tanh" or "relu".</p>',
         """
def neuron(x, w, b, act):
    # your code here
    pass
""", [('neuron([2, 1], [0.5, -1], 0.5, "sigmoid")', 0.6225), ('neuron([1, 1], [1, 1], -3, "relu")', 0.0), ('neuron([1, 0], [1, 0], 0, "tanh")', 0.7616)],
         """
import math


def neuron(x, w, b, act):
    z = sum(xi * wi for xi, wi in zip(x, w)) + b
    if act == "sigmoid":
        return round(1 / (1 + math.exp(-z)), 4)
    if act == "tanh":
        return round(math.tanh(z), 4)
    return round(float(max(0.0, z)), 4)
""", 'Weighted sum plus bias, then the chosen activation.', '<p>Returning a float from ReLU keeps the output type the same for every activation.</p>')
K.assign('perceptron_train', 'm', 'Train a perceptron',
         '<p>Write <code>perceptron_train(X, y, epochs)</code>. Start from zero weights and bias, visit the points in order, predict 1 when w &middot; x + b &gt; 0, and on a mistake add (y &minus; &ycirc;) times x to w and (y &minus; &ycirc;) to b. Stop early after an epoch with no mistakes. Return the list w followed by b, as one list.</p>',
         """
def perceptron_train(X, y, epochs):
    # your code here
    pass
""", [('perceptron_train([[0, 0], [0, 1], [1, 0], [1, 1]], [0, 0, 0, 1], 20)', [2, 1, -2]), ('perceptron_train([[0, 0], [0, 1], [1, 0], [1, 1]], [0, 1, 1, 1], 20)', [1, 1, 0])],
         """
def perceptron_train(X, y, epochs):
    w, b = [0] * len(X[0]), 0
    for _ in range(epochs):
        mistakes = 0
        for xi, t in zip(X, y):
            pred = 1 if sum(a * c for a, c in zip(w, xi)) + b > 0 else 0
            if pred != t:
                w = [a + (t - pred) * c for a, c in zip(w, xi)]
                b += t - pred
                mistakes += 1
        if mistakes == 0:
            break
    return w + [b]
""", 'Loop over epochs and points, update only on mistakes, and stop after a clean epoch.', '<p>These are the AND and OR gates. Both are linearly separable, so training stops well before 20 epochs.</p>')
K.assign('mlp_forward', 'm', 'Forward pass of a small MLP',
         '<p>Write <code>mlp_forward(x, W1, b1, W2, b2)</code>. W1 is a list of rows, one per hidden unit, and b1 a list of biases. Hidden units use ReLU. W2 is a list of rows, one per output, and b2 a list of biases, with no activation on the output. Return the outputs rounded to 4 decimals.</p>',
         """
def mlp_forward(x, W1, b1, W2, b2):
    # your code here
    pass
""", [('mlp_forward([1, 1], [[1, 1], [1, 1]], [0, -1], [[1, -2]], [0])', [0.0]), ('mlp_forward([0, 1], [[1, 1], [1, 1]], [0, -1], [[1, -2]], [0])', [1.0]), ('mlp_forward([2, -1], [[1, 0], [0, 1]], [0, 0], [[1, 1], [2, -1]], [0.5, 0])', [2.5, 4.0])],
         """
def mlp_forward(x, W1, b1, W2, b2):
    h = [max(0.0, sum(w * xi for w, xi in zip(row, x)) + b) for row, b in zip(W1, b1)]
    return [round(float(sum(w * hi for w, hi in zip(row, h)) + b), 4) for row, b in zip(W2, b2)]
""", 'Compute the hidden layer with ReLU, then the output layer without an activation.', '<p>The first two tests are the hand built XOR network from the maths lesson.</p>')

K.must('Neuron', 'a = &phi;(w &middot; x + b). Layer: h = &phi;(Wx + b). Parameters per layer n<sub>out</sub>(n<sub>in</sub> + 1).')
K.must('Perceptron', 'Step output, update w += &eta;(y &minus; &ycirc;)x on mistakes. Converges if separable, (R/&gamma;)<sup>2</sup> mistakes. Fails on XOR.')
K.must('MLP', 'Hidden layers with nonlinear activations learn features. Without &phi; layers collapse to one linear map.')
K.must('Universal approximation', 'One hidden layer, enough units, any continuous function on a bounded set. Depth is more efficient.')
K.must('Activations', 'ReLU or GELU hidden. Sigmoid slope &le; 0.25, saturates. Softmax for classes. Dead ReLU, leaky ReLU.')
K.must('In practice', 'Scale inputs, MLPClassifier(hidden_layer_sizes, alpha), compare with logistic regression, watch train and test gap.')

T = K.topic(
    slug='dl-neural-nets', topic='dl-neural-nets', step=(1, 'Neural network basics', 'dl-s1', 'Build neural networks from single neurons: perceptrons and multilayer networks, backpropagation, and the tricks that make deep networks train well.', 'Intermediate'),
    title='Neural networks: from perceptrons to MLPs', short='Neural networks', badge='1.1', minutes=50,
    lead='Start deep learning from one neuron: the perceptron and its learning rule, why it fails on XOR, multilayer networks with hidden layers, activation functions, and MLPs in scikit-learn.',
    desc='neuron, perceptron, perceptron learning rule, convergence theorem, XOR, linear separability, multilayer perceptron, hidden layer, universal approximation, activation functions, sigmoid, tanh, ReLU, GELU, softmax, vanishing gradient, MLPClassifier.',
    summary='Neurons, the perceptron and XOR, multilayer networks, activations and scikit-learn MLPs.',
    keywords=['neural network', 'perceptron', 'MLP', 'XOR', 'activation function', 'ReLU', 'sigmoid', 'softmax', 'universal approximation', 'MLPClassifier'],
    recap='<p>A neuron is a weighted sum and an activation. The perceptron learns straight boundaries only. Hidden layers with nonlinear activations learn features that bend the boundary, and ReLU keeps gradients alive.</p>',
    added='2026-11-13', leet=leet_items())
