# Foundations 2.2: calculus and optimisation for machine learning. Checked against Deisenroth, Faisal and Ong,
# Mathematics for Machine Learning (2020) chapters 5 and 7, Goodfellow, Bengio and Courville, Deep Learning (2016)
# chapter 4 (numerical computation, gradient descent, conditioning), Boyd and Vandenberghe, Convex Optimization (2004)
# chapter 3 for convexity, and the Stanford CS229 notes on gradient descent and stochastic gradient descent.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-calculus')
K = Kit()

K.code('slope_by_hand', r'''
def f(x):
    return x * x

x = 3
for h in [1, 0.1, 0.01, 0.001]:
    slope = (f(x + h) - f(x)) / h      # rise over run between two close points
    print("h =", h, "slope =", round(slope, 4))
print("the slopes settle on 6, and the rule f'(x) = 2x gives 2 x 3 = 6")
''')

K.code('derivative_rules', r'''
def numeric_derivative(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)     # central difference: more accurate

x = 2.0
print("power rule   d/dx x^3 = 3x^2 :", round(numeric_derivative(lambda t: t ** 3, x), 4), "vs", 3 * x ** 2)
print("constant     d/dx 5x = 5     :", round(numeric_derivative(lambda t: 5 * t, x), 4))
print("sum rule     d/dx x^2 + 4x   :", round(numeric_derivative(lambda t: t ** 2 + 4 * t, x), 4), "vs", 2 * x + 4)
print("product rule d/dx x^2 * x    :", round(numeric_derivative(lambda t: (t ** 2) * t, x), 4), "vs", 2 * x * x + x ** 2)
''')

K.code('chain_rule', r'''
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
''')

K.code('gradient_of_two', r'''
# f(w1, w2) = (w1 - 3)^2 + 2 * (w2 + 1)^2   has its lowest point at (3, -1)
def f(w1, w2):
    return (w1 - 3) ** 2 + 2 * (w2 + 1) ** 2

def gradient(w1, w2):
    d_w1 = 2 * (w1 - 3)          # partial derivative: treat w2 as a fixed number
    d_w2 = 4 * (w2 + 1)          # partial derivative: treat w1 as a fixed number
    return [d_w1, d_w2]

w1, w2 = 0.0, 0.0
print("gradient at (0, 0):", gradient(w1, w2))
for step in range(5):
    g = gradient(w1, w2)
    w1 = w1 - 0.2 * g[0]
    w2 = w2 - 0.2 * g[1]
    print("step", step + 1, "w =", [round(w1, 3), round(w2, 3)], "f =", round(f(w1, w2), 4))
''')

K.code('fit_line_gd', r'''
# Fit price = w * size + b with gradient descent on the mean squared error
sizes = [1.0, 2.0, 3.0, 4.0]        # in 100 m2
prices = [30.0, 50.0, 70.0, 90.0]   # in lakh (true rule: 20 * size + 10)
n = len(sizes)

w = 0.0
b = 0.0
learning_rate = 0.05
for epoch in range(301):
    d_w = 0.0
    d_b = 0.0
    for x, y in zip(sizes, prices):
        error = (w * x + b) - y
        d_w = d_w + 2 * error * x / n      # partial derivative of MSE with respect to w
        d_b = d_b + 2 * error / n          # partial derivative of MSE with respect to b
    w = w - learning_rate * d_w
    b = b - learning_rate * d_b
    if epoch % 100 == 0:
        mse = sum(((w * x + b) - y) ** 2 for x, y in zip(sizes, prices)) / n
        print("epoch", epoch, "w =", round(w, 3), "b =", round(b, 3), "mse =", round(mse, 4))
print("learned: price =", round(w, 2), "x size +", round(b, 2))
''', long=True)

K.code('batch_sgd_minibatch', r'''
import numpy as np

rng = np.random.default_rng(0)
X = rng.uniform(0, 5, size=40)
y = 3 * X + 2 + rng.normal(0, 0.5, size=40)      # true rule y = 3x + 2 plus noise

def train(batch_size, epochs=20, lr=0.02):
    w, b = 0.0, 0.0
    order = np.arange(len(X))
    for epoch in range(epochs):
        rng2 = np.random.default_rng(epoch)
        rng2.shuffle(order)
        for start in range(0, len(X), batch_size):
            idx = order[start:start + batch_size]
            err = w * X[idx] + b - y[idx]
            w -= lr * 2 * np.mean(err * X[idx])
            b -= lr * 2 * np.mean(err)
    mse = np.mean((w * X + b - y) ** 2)
    return "w = " + str(round(float(w), 2)) + "  b = " + str(round(float(b), 2)) + "  mse = " + str(round(float(mse), 3))

print("true rule:  w = 3  b = 2")
print("batch      (40 rows, 20 steps): ", train(40))
print("mini-batch (8 rows, 100 steps): ", train(8))
print("stochastic (1 row, 800 steps):  ", train(1))
''', long=True)

K.code('learning_rate_effect', r'''
# Minimise f(x) = x^2 (slope 2x) from x = 5 with different learning rates
for lr in [0.01, 0.1, 0.5, 0.9, 1.1]:
    x = 5.0
    for step in range(10):
        x = x - lr * 2 * x
    print("learning rate", lr, "-> x after 10 steps =", round(x, 4))
''', long=True)

K.code('local_minima', r'''
# f(x) = x^4 - 3x^2 + x has two valleys
def slope(x):
    return 4 * x ** 3 - 6 * x + 1

def f(x):
    return x ** 4 - 3 * x ** 2 + x

for start in [-2.0, -0.5, 0.5, 2.0]:
    x = start
    for step in range(200):
        x = x - 0.01 * slope(x)
    print("start", start, "-> ends at x =", round(x, 3), "with f =", round(f(x), 3))
print("Where you start decides which valley you reach.")
''', long=True)

K.lesson('derivative', 'Derivatives: how fast something changes', f'''
{src('Deisenroth, Faisal and Ong, Mathematics for Machine Learning chapters 5 and 7, Goodfellow and others, Deep Learning chapter 4, and Boyd and Vandenberghe, Convex Optimization chapter 3.')}
{viz('mlslope')}
{wwh('The <b>derivative</b> of a function at a point is its slope there: how much the output changes when the input moves a tiny bit. We write it f′(x) or df/dx.',
     'Training a model means making the loss smaller. The derivative of the loss tells us, for each parameter, whether to increase or decrease it and how strongly it matters. Without derivatives we would have to guess blindly.',
     'Take two points on the curve that are h apart, compute rise over run, and let h shrink towards 0. In practice we use rules (power, sum, product, chain) to write the derivative as a formula, and libraries compute it automatically.')}
{run('slope_by_hand')}
{scene('the speedometer in a car', '<p>Your car’s trip meter shows distance. The speedometer shows how fast that distance is changing right now. Speed is the derivative of distance. If you drive 60 km in one hour, the average speed is 60 km per hour, but the speedometer shows the speed at this exact moment: the limit over a tiny time step.</p>')}
''', kw=['derivative', 'slope', 'rate of change', 'limit', 'tangent line', 'difference quotient'])

K.lesson('rules', 'The derivative rules you need', f'''
{table(['Rule', 'Formula', 'Example'], [
    ['Constant', 'd/dx c = 0', 'd/dx 7 = 0'],
    ['Power', 'd/dx x<sup>n</sup> = n x<sup>n&minus;1</sup>', 'd/dx x<sup>3</sup> = 3x<sup>2</sup>'],
    ['Constant multiple', 'd/dx c f(x) = c f′(x)', 'd/dx 5x<sup>2</sup> = 10x'],
    ['Sum', '(f + g)′ = f′ + g′', 'd/dx (x<sup>2</sup> + 4x) = 2x + 4'],
    ['Product', '(f g)′ = f′ g + f g′', 'd/dx x<sup>2</sup> &middot; x = 2x &middot; x + x<sup>2</sup> = 3x<sup>2</sup>'],
    ['Exponential', 'd/dx e<sup>x</sup> = e<sup>x</sup>', 'Its own slope'],
    ['Logarithm', 'd/dx ln x = 1/x', 'Used in log loss'],
    ['Sigmoid', 'd/dx &sigma;(x) = &sigma;(x)(1 &minus; &sigma;(x))', 'Largest at x = 0, value 0.25'],
    ['ReLU', 'd/dx max(0, x) = 1 if x &gt; 0, else 0', 'Used in neural networks']])}
{run('derivative_rules')}
{note('The central difference (f(x + h) &minus; f(x &minus; h)) / 2h is much more accurate than the one sided version. Use it to check hand written gradients ("gradient checking").', 'tip')}
''', kw=['power rule', 'sum rule', 'product rule', 'exponential', 'logarithm', 'sigmoid derivative', 'ReLU derivative', 'central difference'])

K.lesson('chain', 'The chain rule: slopes multiply', f'''
{wwh('The <b>chain rule</b> gives the derivative of a function inside another function: if y = f(g(x)), then dy/dx = f′(g(x)) &times; g′(x). The slopes of the steps multiply.',
     'Every model is a chain of simple steps: multiply by weights, add, squash with a sigmoid, compute a loss. To know how the loss depends on a weight deep inside, we chain the slopes of each step. This is exactly what backpropagation does in neural networks (Deep Learning 1.2).',
     'Write the computation as small steps. Find the slope of each step on its own. Multiply them along the path from the weight to the output.')}
{run('chain_rule')}
{steps('Worked example: chain rule by hand', [
    'y = (3x + 1)<sup>2</sup>. Inner g(x) = 3x + 1, outer f(u) = u<sup>2</sup>.',
    'Slope of the outer step: f′(u) = 2u = 2(3x + 1).',
    'Slope of the inner step: g′(x) = 3.',
    eq('dy/dx = 2(3x + 1) &times; 3 = 6(3x + 1)'),
    'At x = 1: dy/dx = 6 &times; 4 = 24. A tiny nudge of x by 0.001 changes y by about 0.024.'])}
''', kw=['chain rule', 'composite function', 'backpropagation preview', 'sigmoid', 'computational graph'])

K.lesson('gradient', 'Partial derivatives and the gradient', f'''
{wwh('When a function has many inputs, a <b>partial derivative</b> is its slope along one input while the others stay fixed. The <b>gradient</b> is the list of all the partial derivatives, written &nabla;f.',
     'A model has many weights. The gradient of the loss says, for every weight at once, which way and how strongly to change it. It points in the direction where the loss grows fastest.',
     'Compute each partial derivative by treating the other variables as constants. Then step against the gradient: w<sub>new</sub> = w &minus; &eta; &nabla;L(w). Each weight moves by its own partial derivative.')}
{run('gradient_of_two')}
{fxs(fx('Gradient', '&nabla;f(w) = [&part;f/&part;w<sub>1</sub>, &part;f/&part;w<sub>2</sub>, ..., &part;f/&part;w<sub>d</sub>]', 'One partial derivative per parameter.', key=True),
     fx('Gradient descent update', 'w &larr; w &minus; &eta; &nabla;L(w)', '&eta; is the learning rate. Move against the gradient.', key=True),
     fx('MSE gradient for a line', '&part;L/&part;w = (2/n) &Sigma; (ŷ<sub>i</sub> &minus; y<sub>i</sub>) x<sub>i</sub>, &part;L/&part;b = (2/n) &Sigma; (ŷ<sub>i</sub> &minus; y<sub>i</sub>)', 'Used to fit ŷ = w x + b.', key=True))}
{run('fit_line_gd')}
''', kw=['partial derivative', 'gradient', 'nabla', 'gradient descent update', 'MSE gradient', 'steepest ascent'])

K.lesson('descent', 'Gradient descent: walking downhill', f'''
{viz('mlgd')}
{run('learning_rate_effect')}
{table(['Learning rate', 'What happens'], [
    ['Too small', 'Safe but very slow. Training takes forever'],
    ['About right', 'Loss drops quickly and settles'],
    ['A little too big', 'Bounces from side to side, still settles'],
    ['Far too big', 'Each step overshoots more and the loss explodes (diverges)']])}
{scene('walking down a hill in fog', '<p>Imagine you are on a hill in thick fog and want to reach the valley. You cannot see the valley, but you can feel which way the ground slopes under your feet. You take a step downhill, feel again, and repeat. Big steps are fast but you might jump over the valley. Tiny steps are safe but slow. That is gradient descent, and the step size is the learning rate.</p>')}
''', kw=['gradient descent', 'learning rate', 'divergence', 'overshooting', 'convergence'])

K.lesson('variants', 'Batch, stochastic and mini-batch gradient descent', f'''
<p>All three versions use the same update rule. They only differ in how many rows they look at before they take one step. The program below trains the same line for 20 epochs with each version.</p>
{run('batch_sgd_minibatch')}
<p>Look at the number of steps. Batch gradient descent used all 40 rows for each step, so 20 epochs gave only 20 steps and b is still far from 2. Mini-batch took 100 steps and stochastic took 800 steps in the same 20 passes, so they moved much closer to the true rule. Stochastic steps are noisy, so its final error is not the smallest. Mini-batch sits in the middle and wins here.</p>
{versus('Three ways to compute the gradient', ['', 'Batch GD', 'Stochastic GD (SGD)', 'Mini-batch GD'], [
    ['Rows per step', 'All n', '1', 'A small group, often 32 to 512'],
    ['Steps per pass over the data (epoch)', '1', 'n', 'n / batch size'],
    ['Path to the minimum', 'Smooth', 'Very noisy', 'A little noisy'],
    ['Memory', 'Needs all data at once', 'Tiny', 'Small'],
    ['Used for', 'Small datasets', 'Online learning, streams', 'Almost all deep learning']],
    'mini-batch is the everyday choice. Its small noise even helps escape shallow valleys.')}
{note('An epoch is one full pass over the training data. With 1,000 rows and a batch size of 100, one epoch has 10 update steps.', 'exam')}
''', kw=['batch gradient descent', 'stochastic gradient descent', 'SGD', 'mini-batch', 'epoch', 'batch size'])

K.lesson('convex', 'Valleys, convexity and local minima', f'''
{run('local_minima')}
{wwh('A function is <b>convex</b> when it is shaped like a bowl: any line between two points on the curve lies above it. A convex function has only one valley, so gradient descent cannot get stuck in a wrong one.',
     'Linear regression with squared error and logistic regression have convex losses, so they always reach the best answer. Neural networks do not, so where training starts and how it moves matters.',
     'A <b>local minimum</b> is a point lower than everything nearby but not the lowest overall (the <b>global minimum</b>). A <b>saddle point</b> has slope 0 but goes down in some direction. Random starts, momentum and noise from mini-batches help in non convex problems.')}
{fxs(fx('Convex test (one variable)', 'f′′(x) &ge; 0 everywhere', 'The second derivative (curvature) is never negative.', key=True),
     fx('At a minimum', 'f′(x) = 0 and f′′(x) &gt; 0', 'Flat and curving up.'),
     fx('Second order step (Newton)', 'x &larr; x &minus; f′(x) / f′′(x)', 'Uses curvature to pick the step size. Fast but costly with many parameters.'))}
{note('Gradient descent finds a point where the gradient is near 0. For a convex loss this is the best answer. For a non convex loss it may be a local minimum or a saddle point.', 'warn')}
''', kw=['convex function', 'local minimum', 'global minimum', 'saddle point', 'second derivative', 'Newton method'])

K.lesson('versus', 'Optimisers compared', f'''
{versus('Ways to find the best parameters', ['', 'Closed form (solve equations)', 'Gradient descent', 'Newton method', 'Search without gradients'], [
    ['Needs', 'A formula for the answer', 'The gradient', 'Gradient and curvature (Hessian)', 'Only the loss value'],
    ['Speed per step', 'One big computation', 'Cheap', 'Expensive (d &times; d matrix)', 'Cheap but many tries'],
    ['Steps needed', 'One', 'Many', 'Few', 'Very many'],
    ['Works for', 'Linear regression', 'Almost every model', 'Small, smooth problems', 'Hyperparameters, black boxes'],
    ['Example', 'Normal equation', 'Training a neural network', 'Logistic regression solvers (lbfgs is a cheaper cousin)', 'Grid or random search']],
    'gradient descent and its upgrades (momentum, Adam, Deep Learning 1.3) train most models today.')}
{link('ml-maths', 'More calculus practice', 'Maths for Machine Learning has chapters on derivatives, gradients and backpropagation, gradient descent and optimisation, and Taylor series with automatic differentiation.', 'Open Maths for ML')}
''', kw=['closed form', 'Newton method', 'Hessian', 'lbfgs', 'gradient free', 'optimiser comparison'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Derivative', 'f′(x) = lim<sub>h&rarr;0</sub> (f(x + h) &minus; f(x)) / h', 'The slope at a single point.', key=True),
     fx('Chain rule', 'd/dx f(g(x)) = f′(g(x)) g′(x)', 'Slopes along a chain multiply.', key=True),
     fx('Gradient descent', 'w<sub>t+1</sub> = w<sub>t</sub> &minus; &eta; &nabla;L(w<sub>t</sub>)', 'One step for every parameter at once.', key=True),
     fx('Steps on f(x) = a x<sup>2</sup>', 'x<sub>t+1</sub> = (1 &minus; 2 a &eta;) x<sub>t</sub>', 'Converges when |1 &minus; 2a&eta;| &lt; 1, so &eta; &lt; 1/a.'),
     fx('Central difference', 'f′(x) &asymp; (f(x + h) &minus; f(x &minus; h)) / 2h', 'Error shrinks like h<sup>2</sup>. Used for gradient checks.'))}
{steps('Worked example: two steps of gradient descent by hand', [
    'Minimise L(w) = (w &minus; 5)<sup>2</sup>, start w = 1, learning rate 0.25.',
    'L′(w) = 2(w &minus; 5). At w = 1: slope = &minus;8. New w = 1 &minus; 0.25 &times; (&minus;8) = 3.',
    'At w = 3: slope = &minus;4. New w = 3 &minus; 0.25 &times; (&minus;4) = 4.',
    eq('Each step halves the distance to 5: 4, 2, 1, 0.5, ...'),
    'Distance factor = 1 &minus; 2 &times; 1 &times; 0.25 = 0.5, as the formula above predicts.'])}
{deep('Why gradient descent slows down in long narrow valleys', '<p>If the loss curves strongly in one direction and gently in another (a large condition number, the ratio of the largest to the smallest curvature), a learning rate small enough for the steep direction is far too small for the flat one, and the path zig zags. Feature scaling makes the valley round, which is why it speeds up training. Momentum and Adam help too. Convergence for a convex quadratic takes about &kappa; log(1/&epsilon;) steps, where &kappa; is the condition number.</p>')}
''', kw=['limit definition', 'chain rule', 'gradient descent formula', 'convergence condition', 'condition number', 'gradient checking'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A derivative is a slope. Gradient descent looks at the slope of the error and takes a small step downhill, again and again, until the error is as small as it can get.</p>',
    '<p>Use the power, sum, product and chain rules, compute partial derivatives and the gradient, apply w &larr; w &minus; &eta;&nabla;L, pick a learning rate, and know batch, stochastic and mini-batch versions and the idea of an epoch.</p>',
    '<p>Convex losses (least squares, logistic) have one minimum. Non convex losses have local minima and saddle points. The Hessian measures curvature, its condition number controls speed, and feature scaling and momentum improve conditioning.</p>',
    '<p>For L-smooth convex functions, gradient descent with &eta; = 1/L converges at rate O(1/t), and Nesterov acceleration reaches the optimal O(1/t<sup>2</sup>). SGD with decaying steps converges in expectation (Robbins and Monro, 1951). In deep networks most critical points in high dimensions are saddles rather than bad local minima (Dauphin and others, 2014).</p>')}
{grow('Explain a derivative as a slope and run a few gradient descent steps by hand.',
      'Derive the MSE gradient for a line, code gradient descent, and choose batch size and learning rate.',
      'Reason about convexity, curvature and conditioning, and explain convergence rates and why SGD works.')}
''', kw=['beginner', 'expert', 'Hessian', 'L smooth', 'Nesterov', 'Robbins Monro', 'saddle points'])

lc(852, 'Peak Index in a Mountain Array', 'peak-index-in-a-mountain-array', 'm', 'Follow the slope (binary search)', 'Look at the middle. If the next value is bigger, the slope goes up, so the peak is to the right. Otherwise it is here or to the left. This is gradient ascent on a list.', r'''
def peak_index_in_mountain_array(arr):
    low = 0
    high = len(arr) - 1
    while low < high:
        mid = (low + high) // 2
        if arr[mid] < arr[mid + 1]:
            low = mid + 1
        else:
            high = mid
    return low
''', [('peak_index_in_mountain_array([0, 1, 0])', 1), ('peak_index_in_mountain_array([0, 2, 1, 0])', 1), ('peak_index_in_mountain_array([0, 10, 5, 2])', 1)])
lc(441, 'Arranging Coins', 'arranging-coins', 'e', 'Binary search on a growing function', 'k full rows need k(k + 1)/2 coins, which grows with k. Binary search for the largest k that fits in n.', r'''
def arrange_coins(n):
    low = 0
    high = n
    while low < high:
        mid = (low + high + 1) // 2
        if mid * (mid + 1) // 2 <= n:
            low = mid
        else:
            high = mid - 1
    return low
''', [('arrange_coins(5)', 2), ('arrange_coins(8)', 3), ('arrange_coins(1)', 1)])
lc(633, 'Sum of Square Numbers', 'sum-of-square-numbers', 'm', 'Two pointers on a monotone sum', 'Start with a = 0 and b = the integer square root of c. If a<sup>2</sup> + b<sup>2</sup> is too small, raise a. If too big, lower b.', r'''
def judge_square_sum(c):
    a = 0
    b = int(c ** 0.5)
    while b * b > c:
        b = b - 1
    while a <= b:
        total = a * a + b * b
        if total == c:
            return True
        if total < c:
            a = a + 1
        else:
            b = b - 1
    return False
''', [('judge_square_sum(5)', True), ('judge_square_sum(3)', False), ('judge_square_sum(0)', True)])
lc(1283, 'Find the Smallest Divisor Given a Threshold', 'find-the-smallest-divisor-given-a-threshold', 'm', 'Binary search on the answer', 'A bigger divisor makes the sum of rounded up quotients smaller. Binary search for the smallest divisor whose sum is at most the threshold.', r'''
def smallest_divisor(nums, threshold):
    low = 1
    high = max(nums)
    while low < high:
        mid = (low + high) // 2
        total = 0
        for x in nums:
            total = total + (x + mid - 1) // mid
        if total <= threshold:
            high = mid
        else:
            low = mid + 1
    return low
''', [('smallest_divisor([1, 2, 5, 9], 6)', 5), ('smallest_divisor([44, 22, 33, 11, 1], 5)', 44)])
lc(1011, 'Capacity To Ship Packages Within D Days', 'capacity-to-ship-packages-within-d-days', 'm', 'Binary search on the answer', 'The capacity is at least the heaviest package and at most the total. For a guess, count the days needed by filling each day greedily. Fewer days with more capacity: binary search.', r'''
def days_needed(weights, capacity):
    days = 1
    load = 0
    for w in weights:
        if load + w > capacity:
            days = days + 1
            load = 0
        load = load + w
    return days


def ship_within_days(weights, days):
    low = max(weights)
    high = sum(weights)
    while low < high:
        mid = (low + high) // 2
        if days_needed(weights, mid) <= days:
            high = mid
        else:
            low = mid + 1
    return low
''', [('ship_within_days([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5)', 15), ('ship_within_days([3, 2, 2, 4, 1, 4], 3)', 6)])
lc(2529, 'Maximum Count of Positive Integer and Negative Integer', 'maximum-count-of-positive-integer-and-negative-integer', 'e', 'Binary search for where the sign changes', 'The list is sorted, so find the first index that is at least 0 and the first index that is above 0. The counts follow from those two positions.', r'''
def first_index(nums, limit):
    low = 0
    high = len(nums)
    while low < high:
        mid = (low + high) // 2
        if nums[mid] < limit:
            low = mid + 1
        else:
            high = mid
    return low


def maximum_count(nums):
    negatives = first_index(nums, 0)
    positives = len(nums) - first_index(nums, 1)
    return max(negatives, positives)
''', [('maximum_count([-2, -1, -1, 1, 2, 3])', 3), ('maximum_count([-3, -2, -1, 0, 0, 1, 2])', 3), ('maximum_count([5, 20, 66, 1314])', 4)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Optimisation means searching for the best value. These problems search smartly: follow the slope to a peak, binary search on a growing function, and binary search on the answer itself. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'binary search', 'binary search on answer', 'peak finding', 'monotone function'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'The <b>derivative</b> is the slope at a point: the limit of rise over run as the run shrinks to 0.',
    'Rules: power n x<sup>n&minus;1</sup>, sum, product, e<sup>x</sup> stays e<sup>x</sup>, ln x gives 1/x, sigmoid gives &sigma;(1 &minus; &sigma;).',
    'The <b>chain rule</b> multiplies the slopes of the steps. It is the base of backpropagation.',
    'The <b>gradient</b> lists all partial derivatives and points uphill. Gradient descent steps against it: w &larr; w &minus; &eta;&nabla;L.',
    'The learning rate must be neither too small (slow) nor too big (diverges). On a x<sup>2</sup>, &eta; must be below 1/a.',
    'Batch uses all rows per step, SGD one row, mini-batch a small group. One epoch is one pass over the data.',
    'Convex losses have one valley. Non convex ones have local minima and saddle points.'],
    'Foundations 2.3 adds probability and statistics: how models deal with uncertainty and where loss functions come from.')}
{files('Three tasks: the derivative of a polynomial, a numeric slope with the central difference, and gradient descent on a bowl.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does the derivative of a function tell you?', ['Its largest value', 'Its slope (rate of change) at a point', 'Its area', 'Its average'], 1, 'Speedometer.', 'The derivative is the instantaneous rate of change.')
K.quiz('e', 'd/dx x<sup>2</sup> is', ['x', '2x', 'x<sup>3</sup>/3', '2'], 1, 'Power rule.', 'n x<sup>n&minus;1</sup> with n = 2 gives 2x.')
K.quiz('e', 'In gradient descent we move', ['In the direction of the gradient', 'Against the gradient', 'At random', 'Only to the right'], 1, 'The gradient points uphill.', 'Moving against the gradient lowers the loss.')
K.quiz('e', 'One full pass over the training data is called', ['A step', 'An epoch', 'A batch', 'A gradient'], 1, 'Many steps make one.', 'An epoch is one pass over every training example.')
K.quiz('m', 'd/dx (3x + 1)<sup>2</sup> is', ['2(3x + 1)', '6(3x + 1)', '9x<sup>2</sup>', '3'], 1, 'Chain rule.', 'Outer 2(3x + 1) times inner 3.')
K.quiz('m', 'For f(w<sub>1</sub>, w<sub>2</sub>) = w<sub>1</sub><sup>2</sup> + 3w<sub>2</sub>, what is &part;f/&part;w<sub>2</sub>?', ['2w<sub>1</sub>', '3', '3w<sub>2</sub>', '0'], 1, 'Treat w<sub>1</sub> as a constant.', 'Only 3w<sub>2</sub> depends on w<sub>2</sub>, and its slope is 3.')
K.quiz('m', 'The loss gets bigger every step and grows without limit. The most likely cause is', ['Learning rate too small', 'Learning rate too big', 'Too much data', 'A convex loss'], 1, 'Overshooting.', 'Steps overshoot the minimum more and more, so it diverges.')
K.quiz('m', 'With 2,000 rows and batch size 50, how many update steps are in one epoch?', ['50', '40', '2,000', '100'], 1, 'n / batch size.', '2,000 / 50 = 40.')
K.quiz('m', 'Sigmoid derivative at x = 0 is', ['1', '0.25', '0.5', '0'], 1, '&sigma;(0) = 0.5.', '0.5 &times; (1 &minus; 0.5) = 0.25.')
K.quiz('h', 'Which loss is convex in its parameters?', ['A deep neural network loss', 'Mean squared error of linear regression', 'Any loss with ReLU', 'k means objective in the centres and labels'], 1, 'Bowl shaped.', 'MSE of a linear model is a convex quadratic in w.')
K.quiz('h', 'A point where the gradient is 0 but the loss goes down in some direction is a', ['Global minimum', 'Saddle point', 'Local maximum only', 'Plateau'], 1, 'Like a horse saddle.', 'It curves up one way and down another.')
K.quiz('h', 'Why does feature scaling help gradient descent?', ['It removes outliers', 'It makes the loss valley rounder, so one learning rate suits every direction', 'It makes the loss convex', 'It reduces the number of features'], 1, 'Condition number.', 'Similar scales give similar curvature in every direction.')
K.quiz('x', 'In the style of a Stanford CS229 exam: gradient descent on f(x) = 4x<sup>2</sup>. For which learning rates does it converge?', ['&eta; &lt; 1', '&eta; &lt; 0.25', '&eta; &lt; 0.125', 'Any &eta;'], 1, 'Factor 1 &minus; 2a&eta; with a = 4.', 'Need |1 &minus; 8&eta;| &lt; 1, so 0 &lt; &eta; &lt; 0.25.')
K.quiz('x', 'In the style of a CMU 10-725 (convex optimisation) exam: one Newton step on f(x) = (x &minus; 3)<sup>2</sup> from x = 10 lands at', ['6.5', '3', '0', '10'], 1, 'x &minus; f′/f′′.', 'f′ = 14, f′′ = 2. 10 &minus; 14/2 = 3. Newton solves a quadratic in one step.')

K.calc('e', 'd/dx x<sup>3</sup> at x = 2?', '12', '3x<sup>2</sup>.', ['Power rule gives 3x<sup>2</sup>.', 'x<sup>2</sup> = 4.', eq('3 &times; 4 = 12')], check=12)
K.calc('e', 'Slope of f(x) = 5x + 7?', '5', 'Constant slope.', ['5x has slope 5.', '7 has slope 0.', eq('5')], check=5)
K.calc('e', 'w = 4, gradient 2, learning rate 0.5. New w?', '3', 'w &minus; &eta; g.', ['&eta; g = 1.', '4 &minus; 1.', eq('3')], check=4 - 0.5 * 2)
K.calc('m', 'f(x) = x<sup>2</sup> + 4x. Slope at x = 3?', '10', '2x + 4.', ['Derivative 2x + 4.', 'Put x = 3.', eq('6 + 4 = 10')], check=2 * 3 + 4)
K.calc('m', 'y = (2x + 1)<sup>3</sup>. dy/dx at x = 1?', '54', 'Chain rule: 3(2x + 1)<sup>2</sup> &times; 2.', ['2x + 1 = 3.', '3 &times; 9 = 27.', eq('27 &times; 2 = 54')], check=3 * 9 * 2)
K.calc('m', 'Gradient of f = (w<sub>1</sub> &minus; 3)<sup>2</sup> + 2(w<sub>2</sub> + 1)<sup>2</sup> at (0, 0): the second component?', '4', '4(w<sub>2</sub> + 1).', ['Partial in w<sub>2</sub> is 4(w<sub>2</sub> + 1).', 'w<sub>2</sub> = 0.', eq('4')], check=4)
K.calc('m', 'Batch size 32, 3,200 rows, 10 epochs. Total update steps?', '1000', 'Steps per epoch &times; epochs.', ['3,200 / 32 = 100.', '10 epochs.', eq('100 &times; 10 = 1,000')], check=3200 // 32 * 10)
K.calc('h', 'MSE gradient &part;L/&part;w for points (1, 3) and (2, 5) at w = 1, b = 0. Use (2/n)&Sigma;(ŷ &minus; y)x.', '-8', 'Predictions 1 and 2.', ['Errors: 1 &minus; 3 = &minus;2 and 2 &minus; 5 = &minus;3.', 'Times x: &minus;2 and &minus;6, sum &minus;8.', eq('(2/2) &times; (&minus;8) = &minus;8')], check=(2 / 2) * (-2 * 1 + -3 * 2))
K.calc('h', 'Gradient descent on L = (w &minus; 5)<sup>2</sup> from w = 1 with &eta; = 0.25. Where is w after 3 steps?', '4.5', 'The distance halves each step.', ['Distance 4, then 2, then 1, then 0.5.', 'w = 5 &minus; 0.5.', eq('4.5')], check=5 - 4 * 0.5 ** 3)
K.calc('x', 'In the style of an MIT 6.7900 problem: for f(x) = a x<sup>2</sup> with a = 2.5, what learning rate makes gradient descent jump straight to 0 in one step?', '0.2', 'Need 1 &minus; 2a&eta; = 0.', ['1 &minus; 2 &times; 2.5 &times; &eta; = 0.', '5&eta; = 1.', eq('&eta; = 0.2 = 1/(2a)')], check=1 / (2 * 2.5))

K.assign('polyd', 'e', 'Derivative of a polynomial',
         '<p>A polynomial is stored as its coefficients from the constant up: [c0, c1, c2] means c0 + c1 x + c2 x<sup>2</sup>. Write <code>poly_derivative(coeffs)</code> that returns the coefficients of its derivative. The derivative of a constant is [0].</p>',
         '''
def poly_derivative(coeffs):
    # your code here
    pass
''', [('poly_derivative([7, 4, 1])', [4, 2]), ('poly_derivative([0, 0, 0, 2])', [0, 0, 6]), ('poly_derivative([5])', [0])],
         '''
def poly_derivative(coeffs):
    if len(coeffs) == 1:
        return [0]
    result = []
    for power in range(1, len(coeffs)):
        result.append(power * coeffs[power])
    return result
''', 'The term c<sub>k</sub> x<sup>k</sup> becomes k c<sub>k</sub> x<sup>k&minus;1</sup>. So skip c0 and multiply each other coefficient by its power.', '<p>This is the power rule applied to every term, plus the sum rule that lets you do each term on its own.</p>')
K.assign('numslope', 'm', 'Numeric slope with the central difference',
         '<p>Write <code>numeric_slope(f, x)</code> that returns (f(x + h) &minus; f(x &minus; h)) / (2h) with h = 0.00001, rounded to 4 decimals. f is any function of one number.</p>',
         '''
def numeric_slope(f, x):
    # your code here
    pass
''', [('numeric_slope(lambda t: t * t, 3)', 6.0), ('numeric_slope(lambda t: t ** 3, 2)', 12.0), ('numeric_slope(lambda t: 5 * t + 1, 0)', 5.0)],
         '''
def numeric_slope(f, x):
    h = 0.00001
    return round((f(x + h) - f(x - h)) / (2 * h), 4)
''', 'Call f twice, once a little right of x and once a little left, and divide the difference by 2h.', '<p>This is gradient checking: compare a hand derived gradient with this number. If they differ, the hand derivation has a bug.</p>')
K.assign('gdbowl', 'm', 'Gradient descent on a bowl',
         '<p>Write <code>descend(target, start, rate, steps)</code> that minimises f(x) = (x &minus; target)<sup>2</sup> with gradient descent. Start at start, take the given number of steps with x = x &minus; rate &times; 2(x &minus; target), and return x rounded to 4 decimals.</p>',
         '''
def descend(target, start, rate, steps):
    # your code here
    pass
''', [('descend(5, 1, 0.25, 3)', 4.5), ('descend(0, 10, 0.5, 1)', 0.0), ('descend(2, 0, 0.1, 10)', 1.7853)],
         '''
def descend(target, start, rate, steps):
    x = start
    for i in range(steps):
        slope = 2 * (x - target)
        x = x - rate * slope
    return round(x, 4)
''', 'Loop steps times. Each time compute the slope 2(x &minus; target) and move against it.', '<p>Each step multiplies the distance to the target by (1 &minus; 2 &times; rate). With rate 0.5 that factor is 0, so one step lands exactly on the target.</p>')

K.must('Derivative', 'Slope at a point, the limit of (f(x+h) &minus; f(x))/h. Power rule n x<sup>n&minus;1</sup>. e<sup>x</sup> to e<sup>x</sup>, ln x to 1/x, &sigma;′ = &sigma;(1 &minus; &sigma;).')
K.must('Chain rule', 'd/dx f(g(x)) = f′(g(x)) g′(x). Slopes along a chain multiply. Base of backpropagation.')
K.must('Gradient', 'Vector of partial derivatives, points uphill. Update w &larr; w &minus; &eta;&nabla;L.')
K.must('Learning rate', 'Too small is slow, too big diverges. On a x<sup>2</sup>, need &eta; &lt; 1/a. Feature scaling helps.')
K.must('Variants', 'Batch (all rows), SGD (1 row), mini-batch (32 to 512). Epoch = one pass. Steps per epoch = n / batch size.')
K.must('Convexity', 'Convex losses (linear and logistic regression) have one minimum. Networks have local minima and saddles.')

T = K.topic(
    slug='ml-calculus', topic='ml-calculus', step=(2, 'Maths you need', 'ml-f2', 'The linear algebra, calculus and probability that every model uses, explained with simple words, pictures and code.', 'Beginner'),
    title='Calculus for ML: derivatives, gradients and gradient descent', short='Calculus and gradient descent', badge='2.2', minutes=60,
    lead='Learn how a model knows which way to change its weights: derivatives as slopes, the rules and the chain rule, gradients for many weights, gradient descent and its batch, stochastic and mini-batch versions, learning rates and convexity.',
    desc='derivative as slope and limit, power sum product rules, exponential, logarithm, sigmoid and ReLU derivatives, central difference, chain rule, partial derivatives, gradient, gradient descent update, MSE gradient, learning rate, divergence, batch, stochastic and mini-batch gradient descent, epoch, convexity, local and global minima, saddle points, Newton method, condition number.',
    summary='derivatives, the chain rule, gradients, gradient descent, learning rates, SGD and mini-batches, and convexity.',
    keywords=['derivative', 'chain rule', 'gradient', 'gradient descent', 'learning rate', 'SGD', 'mini-batch', 'epoch', 'convex', 'local minimum'],
    recap='<p>Derivatives tell a model which way is downhill. Gradient descent follows them, step by step, until the loss stops falling.</p>',
    added='2026-11-13', leet=leet_items())
