# NLP section, chapter 1.3: non-linearities. Source: FoVL lecture 1 slides "Non-linearities, old and new"
# (threshold units, logistic, tanh, hard tanh, tanh(z) = 2 logistic(2z) − 1, ReLU and the gradient at x < 0, leaky and
# parametric ReLU, swish arXiv 1710.05941, GELU arXiv 1606.08415 with x·logistic(1.702x), and "why they are needed":
# W1 W2 x = Wx, linear layers stretch and rotate space while non-linearities bend it).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq, mat

K = Kit()

K.code('acts', r'''
# The activation functions from the slide, evaluated at a few inputs
import math
sig = lambda z: 1 / (1 + math.exp(-z))
acts = {
    "sigmoid": sig,
    "tanh": math.tanh,
    "hardtanh": lambda z: max(-1.0, min(1.0, z)),
    "relu": lambda z: max(0.0, z),
    "leaky": lambda z: z if z > 0 else 0.01 * z,
    "swish": lambda z: z * sig(z),
    "gelu": lambda z: z * sig(1.702 * z),
}
for name, f in acts.items():
    print(name.ljust(9), [round(f(z), 3) for z in (-2, -0.5, 0, 0.5, 2)])
''')

K.code('collapse', r'''
# Two linear layers without an activation are one linear layer in disguise
W1 = [[1, 2], [0, 1]]
W2 = [[2, 0], [1, 1]]
x = [3, 1]

def mv(M, v):
    return [sum(M[i][k] * v[k] for k in range(len(v))) for i in range(len(M))]

def mm(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]

print("two layers:", mv(W2, mv(W1, x)))
W = mm(W2, W1)
print("one layer W = W2 W1 =", W, "->", mv(W, x))
relu = lambda v: [max(0, t) for t in v]
print("with ReLU between:", mv(W2, relu(mv(W1, [-3, 1]))), "against", mv(W, [-3, 1]))
''')

K.lesson('why', 'Why a network needs a bend', f'''
<p>At the end of the day a neural network is a function approximator. It maps inputs to outputs for regression and classification. If every layer were only a matrix multiplication, stacking layers would change nothing, because the product of matrices is one matrix.</p>
{fxs(fx('Linear layers collapse', '<i>W</i>₂(<i>W</i>₁<b>x</b>) = (<i>W</i>₂<i>W</i>₁)<b>x</b> = <i>W</i><b>x</b>', 'Ten linear layers are still one linear layer, with ten times the compute.', key=True),
     fx('A layer with an activation', '<b>h</b> = f(<i>W</i><b>x</b> + <b>b</b>)', 'f is applied to each number separately. That one bend is what gives depth its power.'))}
{steps('Worked example: the collapse in numbers', [
    'W₁ = ' + mat([['1', '2'], ['0', '1']]) + ', W₂ = ' + mat([['2', '0'], ['1', '1']]) + ', x = (3, 1).',
    'W₁x = (5, 1), then W₂(5, 1) = (10, 6).',
    'W₂W₁ = ' + mat([['2', '4'], ['1', '3']]) + ' and (W₂W₁)x = (10, 6), the same answer.',
    eq('With ReLU between them, x = (−3, 1) gives (0, 1) after the first layer, so the output is (0, 1), not the linear (−2, −2)')])}
{code('collapse')}
{scene('folding paper', '<p>A linear layer can stretch, rotate or slide a sheet of paper but never fold it. Two red and blue patterns that are mixed up on the sheet stay mixed up. An activation folds the sheet along a line. After a few folds, points that were tangled can be separated with one straight cut. This is the slide line: linear layers stretch and rotate space, non-linearities bend it.</p>')}
{ladder(
    '<p>Adding up and multiplying can only draw straight lines. To draw curves, each neuron needs a little bend. The bend is the activation function.</p>',
    '<p>Without activations an L layer network is the linear map W = W<sub>L</sub> … W₁. With them, a network with one hidden layer of enough units can approximate any continuous function on a bounded region (the universal approximation theorem).</p>',
    '<p>The theorem says nothing about how many units are needed or whether gradient descent finds them. Depth helps because composing bends multiplies the number of linear pieces: a ReLU network of depth L can produce a number of regions that grows exponentially with L.</p>',
    '<p>Activation choice interacts with initialisation (He for ReLU, Glorot for tanh), with normalisation and with the loss landscape. Smooth gates such as GELU and SwiGLU are standard in transformers, and research still compares them by trainability more than by expressive power.</p>')}
{note('More non-linear layers give more expressive power but also harder optimisation and a higher risk of overfitting. The slide closes with exactly this warning.', 'warn')}
''', kw=['non-linearity', 'activation', 'linear collapse', 'universal approximation', 'depth'])

K.lesson('classic', 'Threshold, sigmoid, tanh and hard tanh', f'''
<p>The oldest units fired 1 or 0, a threshold. They have no useful slope, so gradient descent gets no signal and cannot learn. The logistic sigmoid replaced them with a smooth curve and a probabilistic reading. tanh is the same curve rescaled to (−1, 1).</p>
{fxs(fx('tanh from the sigmoid', 'tanh(z) = 2σ(2z) − 1', 'Twice as steep at 0 (slope 1 against 0.25) and centred on zero.', key=True),
     fx('Slopes', 'σ′ = σ(1 − σ) &nbsp;&nbsp; tanh′ = 1 − tanh²', 'Both shrink toward 0 for large |z|: the saturation problem.'),
     fx('Hard tanh', 'hardtanh(z) = −1 for z < −1, z in between, 1 for z > 1', 'Straight pieces instead of curves, so no exponentials are needed.'))}
{viz('activations')}
{table(['Unit', 'Range', 'Good', 'Problem'], [['Threshold', '0 or 1', 'Simple', 'Slope 0, no learning'], ['Sigmoid', '(0, 1)', 'Probability reading', 'Saturates, outputs always positive'], ['tanh', '(−1, 1)', 'Zero centred, faster convergence', 'Saturates, needs exponentials'], ['Hard tanh', '[−1, 1]', 'Cheap to compute', 'Flat outside [−1, 1]']])}
{steps('Check the identity at z = 0.5', [
    'σ(2 × 0.5) = σ(1) = 0.73106.',
    '2 × 0.73106 − 1 = 0.46212.',
    eq('tanh 0.5 = 0.46212, the same number')])}
{note('Sigmoid outputs are always positive, so the gradients of all weights into the next neuron share one sign. Updates zig-zag. tanh avoids this, which is why it was preferred in hidden layers.', 'tip')}
''', kw=['threshold unit', 'sigmoid', 'tanh', 'hard tanh', 'saturation', 'zero centred'])

K.lesson('modern', 'ReLU and its smooth successors', f'''
<p>For deep networks the first thing to try is ReLU: max(z, 0). It is cheap and its slope is exactly 1 for every positive input, so gradients flow back through many layers. Its weakness is the flat side: the slope for z &lt; 0 is 0, the answer to the slide question, and a neuron stuck there is dead.</p>
{fxs(fx('ReLU and leaky ReLU', 'ReLU(z) = max(z, 0) &nbsp;&nbsp; leaky(z) = z for z &gt; 0, a·z otherwise', 'Leaky ReLU keeps a small slope a (for example 0.01). Parametric ReLU learns a.', key=True),
     fx('Swish', 'swish(z) = z · σ(z)', 'A soft gate between 0 and 1 multiplies the input. Ramachandran and others, arXiv 1710.05941.'),
     fx('GELU', 'GELU(z) = z · P(X ≤ z), X ~ N(0, 1) &nbsp; ≈ z · σ(1.702 z)', 'Scales z by how likely a standard normal is to be below it. Used in BERT and RoBERTa. arXiv 1606.08415.', key=True))}
{code('acts')}
{table(['z', '−2', '−0.5', '0', '0.5', '2'], [['ReLU', '0', '0', '0', '0.5', '2'], ['leaky (a = 0.01)', '−0.02', '−0.005', '0', '0.5', '2'], ['swish', '−0.238', '−0.189', '0', '0.311', '1.762'], ['GELU (approx.)', '−0.064', '−0.150', '0', '0.350', '1.936']])}
{deep('why transformers moved to smooth gates', '<p>ReLU variants solved gradient flow, but their kink at 0 makes the loss surface less smooth. Swish and GELU behave like ReLU for large |z| and bend smoothly near 0, even passing small negative values. Gated linear units such as SwiGLU multiply one projection by a swish of another and are now standard in large language models. The gain is a small but consistent improvement in training stability and final loss.</p>')}
{note('Expect "what is the gradient of ReLU for x &lt; 0?" Answer 0. Expect also "why tanh over sigmoid in hidden layers?" Answer: zero centred and stronger slope.', 'exam')}
''', kw=['ReLU', 'dead neuron', 'leaky ReLU', 'swish', 'GELU', 'transformers'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'ReLU(−3) equals', ['−3', '0', '3', '1'], 1, 'max(z, 0).', 'Negative inputs become 0.')
K.quiz('e', 'Which function outputs values between −1 and 1?', ['sigmoid', 'ReLU', 'tanh', 'threshold'], 2, 'Zero centred.', 'tanh ranges over (−1, 1).')
K.quiz('e', 'Without activation functions, a deep network is', ['more powerful', 'equivalent to a single linear layer', 'unable to run', 'a decision tree'], 1, 'W₂W₁ = W.', 'A product of matrices is one matrix.')
K.quiz('e', 'Why did threshold units fail for learning?', ['They are too slow', 'Their slope is 0, so there is no gradient', 'They output negative numbers', 'They need a GPU'], 1, 'Flat steps.', 'Gradient descent needs a non-zero slope.')
K.quiz('m', 'The gradient of ReLU for x &lt; 0 is', ['1', '0', 'x', 'undefined everywhere'], 1, 'The slide question.', 'The function is flat there.')
K.quiz('m', 'tanh(z) can be written as', ['σ(z) − 1', '2σ(2z) − 1', 'σ(z)²', '1 − σ(z)'], 1, 'Rescale and shift the sigmoid.', 'tanh is a stretched sigmoid with range (−1, 1).')
K.quiz('m', 'A "dead" ReLU neuron is one that', ['outputs 1 always', 'has a negative input for every example, so it never updates', 'has a large bias', 'uses tanh'], 1, 'Slope 0 for all data.', 'With zero slope on every example no gradient reaches its weights.')
K.quiz('m', 'GELU is most associated with', ['LeNet', 'BERT and RoBERTa', 'word2vec', 'HMM taggers'], 1, 'Transformers.', 'BERT style models use GELU in their feed forward layers.')
K.quiz('h', 'Leaky ReLU differs from ReLU because it', ['is bounded', 'keeps a small slope for negative inputs', 'is smooth at 0', 'outputs probabilities'], 1, 'a·z for z &lt; 0.', 'The small slope lets a stuck neuron recover.')
K.quiz('h', 'The universal approximation theorem guarantees that', ['training always succeeds', 'a wide enough one hidden layer network can approximate a continuous function on a bounded region', 'deep is always better than wide', 'ReLU is optimal'], 1, 'Existence, not learnability.', 'It says such weights exist, not that gradient descent finds them.')
K.quiz('h', 'Why were sigmoid outputs a problem in hidden layers?', ['They are negative', 'They are always positive, which biases updates and makes them zig-zag', 'They are not differentiable', 'They are too fast'], 1, 'Slide: outputs always positive.', 'All inputs to the next layer have the same sign.')
K.quiz('x', 'A ReLU network maps the input space into pieces on which it is', ['constant', 'linear', 'quadratic', 'random'], 1, 'Each unit is on or off.', 'With the on and off pattern fixed, the network is a linear map, so it is piecewise linear.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'What is ReLU(2.5)?', '2.5', 'max(z, 0).', ['2.5 is positive.', 'ReLU keeps positive values.', eq('ReLU(2.5) = 2.5')], check=2.5, tol=1e-9)
K.calc('e', 'Leaky ReLU with a = 0.01 at z = −2. Two decimals.', '-0.02', 'a × z.', ['z is negative.', '0.01 × (−2).', eq('−0.02')], check=-0.02, tol=1e-9)
K.calc('e', 'Compute tanh(0.5) through 2σ(1) − 1. Four decimals.', '0.4621', 'σ(1) = 0.73106.', ['σ(1) = 1 ÷ (1 + e<sup>−1</sup>) = 0.73106.', '2 × 0.73106 = 1.46212.', eq('1.46212 − 1 = 0.4621')], check=0.46211715726000974, tol=5e-5)
K.calc('m', 'What is the slope of tanh at 0?', '1', '1 − tanh² 0.', ['tanh 0 = 0.', '1 − 0² = 1.', eq('tanh′(0) = 1, four times the sigmoid’s 0.25')], check=1, tol=1e-9)
K.calc('m', 'Swish at z = 1 (z · σ(z)). Four decimals.', '0.7311', 'σ(1) = 0.73106.', ['σ(1) = 0.73106.', 'Multiply by z = 1.', eq('swish(1) = 0.7311')], check=0.7310585786300049, tol=5e-5)
K.calc('m', 'GELU approximation at z = 1, z · σ(1.702z). Four decimals.', '0.8458', 'σ(1.702).', ['1.702 × 1 = 1.702.', 'σ(1.702) = 1 ÷ (1 + e<sup>−1.702</sup>) = 0.84580.', eq('GELU(1) ≈ 0.8458')], check=0.8457957659328212, tol=5e-5)
K.calc('m', 'W₁ = ((1, 2), (0, 1)), W₂ = ((2, 0), (1, 1)). What is the top left entry of W₂W₁?', '2', 'Row 1 of W₂ times column 1 of W₁.', ['Row (2, 0), column (1, 0).', '2 × 1 + 0 × 0.', eq('2')], check=2, tol=1e-9)
K.calc('h', 'Same matrices: the bottom right entry of W₂W₁?', '3', 'Row 2 of W₂ times column 2 of W₁.', ['Row (1, 1), column (2, 1).', '1 × 2 + 1 × 1.', eq('3, so W₂W₁ = ((2, 4), (1, 3))')], check=3, tol=1e-9)
K.calc('h', 'A layer maps 300 inputs to 100 units with a bias. How many parameters?', '30100', 'Weights plus biases.', ['Weights 300 × 100 = 30,000.', 'Biases 100.', eq('30,100')], check=30100, tol=1e-9)
K.calc('h', 'How many times steeper is tanh than the sigmoid at z = 0?', '4', 'Compare 1 with 0.25.', ['tanh′(0) = 1.', 'σ′(0) = 0.25.', eq('ratio 4')], check=4, tol=1e-9)
K.calc('x', 'A signal passes back through 6 sigmoid layers, each at its best slope 0.25, with weights of size 1. By what factor is the gradient multiplied? Scientific notation.', '2.44e-4', '0.25⁶.', ['Each layer multiplies by σ′ × w = 0.25.', '0.25⁶ = 1 ÷ 4096.', eq('2.44 × 10⁻⁴. With ReLU on active units the factor would be 1')], check=0.25 ** 6, tol=5e-7)

# ---------------------------------------------------------------- assignments
K.assign('acts', 'e', 'Write the activations',
         '<p>Write <code>relu(z)</code>, <code>leaky(z, a)</code>, <code>hardtanh(z)</code> and <code>swish(z)</code>. Return floats. Round swish to 4 decimals.</p>',
         '''
import math

def relu(z):
    pass

def leaky(z, a):
    pass

def hardtanh(z):
    pass

def swish(z):
    pass
''', [('relu(-3.0)', 0.0), ('relu(2.5)', 2.5), ('leaky(-2.0, 0.01)', -0.02), ('hardtanh(3.0)', 1.0), ('hardtanh(-0.4)', -0.4), ('swish(1.0)', 0.7311)],
         '''
import math

def relu(z):
    return max(0.0, z)

def leaky(z, a):
    return z if z > 0 else a * z

def hardtanh(z):
    return max(-1.0, min(1.0, z))

def swish(z):
    return round(z / (1 + math.exp(-z)), 4)
''', 'Each is one line.', '<p>swish(z) = z · σ(z) = z ÷ (1 + e<sup>−z</sup>).</p>')
K.assign('slope', 'm', 'Slopes by finite differences',
         '<p>Write <code>slope(f, z)</code> that estimates f′(z) with the central difference (f(z + h) − f(z − h)) ÷ 2h, h = 1e-5, rounded to 4 decimals. Use it to confirm σ′(0) = 0.25 and tanh′(0) = 1.</p>',
         '''
import math

def slope(f, z):
    pass
''', [('slope(math.tanh, 0.0)', 1.0), ('slope(lambda x: 1 / (1 + math.exp(-x)), 0.0)', 0.25), ('slope(lambda x: max(0.0, x), 2.0)', 1.0)],
         '''
import math

def slope(f, z):
    h = 1e-5
    return round((f(z + h) - f(z - h)) / (2 * h), 4)
''', 'Central differences are accurate to about h².', '<p>Gradient checking compares backpropagation with this estimate to catch bugs.</p>')
K.assign('collapse', 'h', 'Collapse a stack of linear layers',
         '<p>Write <code>collapse(layers)</code>. layers is a list of matrices [W₁, W₂, …] applied in that order to a column vector. Return the single matrix W that does the same job.</p>',
         '''
def collapse(layers):
    pass
''', [('collapse([[[1, 2], [0, 1]], [[2, 0], [1, 1]]])', [[2, 4], [1, 3]]), ('collapse([[[1, 0], [0, 1]]])', [[1, 0], [0, 1]]), ('collapse([[[1, 2, 3]], [[2], [1]]])', [[2, 4, 6], [1, 2, 3]])],
         '''
def collapse(layers):
    def mm(A, B):
        return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
    W = layers[0]
    for L in layers[1:]:
        W = mm(L, W)
    return W
''', 'Later layers multiply from the left: W = W<sub>L</sub> … W₂W₁.', '<p>The third test maps 3 numbers to 1 and back to 2, still one matrix of shape 2 × 3.</p>')

K.must('Why', 'Without activations W₂W₁x = Wx: depth adds nothing. Non-linearities bend space and make networks universal function approximators.')
K.must('Classic units', 'Threshold (no gradient), sigmoid (0, 1), tanh = 2σ(2z) − 1 in (−1, 1), hard tanh. Sigmoid and tanh saturate.')
K.must('ReLU', 'max(z, 0). Slope 1 for z &gt; 0 and 0 for z &lt; 0 (dead neurons). Leaky and parametric ReLU keep a small negative slope.')
K.must('Smooth gates', 'swish = z·σ(z), GELU = z·Φ(z) ≈ z·σ(1.702z), used in BERT and RoBERTa.')
K.must('Trade off', 'More non-linear layers mean more expressive power but harder optimisation and overfitting risk.')

T = K.topic(
    slug='activation-functions', topic='nn-activations', step=(1, 'Neurons and learning', 'nn-learn', 'See how a model learns: costs, gradient descent, one neuron with a sigmoid, backpropagation by the chain rule and the activation functions that make deep networks work.', 'School and college'),
    title='Activation functions: why networks need a bend', short='Activations', badge='1.3', minutes=30, added='2026-11-01',
    lead='See why stacked linear layers collapse into one, and compare threshold, sigmoid, tanh, hard tanh, ReLU, leaky ReLU, swish and GELU by their shape and their slope.',
    desc='Why non-linearities are needed, the collapse W₂W₁x = Wx, threshold units, sigmoid, tanh and the identity tanh(z) = 2σ(2z) − 1, hard tanh, ReLU and dead neurons, leaky and parametric ReLU, swish and GELU.',
    summary='Why networks need non-linear activations, and how the classic and modern ones compare.',
    keywords=['activation function', 'sigmoid', 'tanh', 'ReLU', 'leaky ReLU', 'GELU', 'swish', 'non-linearity'],
    recap='<p>Activations put a bend into each neuron. Without them a deep network is one matrix. Old units saturate and starve learning of gradient. ReLU keeps gradients alive for positive inputs, and smooth gates like GELU power transformers.</p>')
