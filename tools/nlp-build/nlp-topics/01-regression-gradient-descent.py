# NLP section, chapter 1.1: from regression to learning by gradient descent. Source: FoVL lecture 1 (the pats and
# wags data, w = 0.25 and b = 0.68, the cost function, the NN() = b teaching model with cost (b − 4)², slope and
# learning rate, the 3D cost bowl, partial derivatives) and the lecture 5 recording (the tanh derivative question and
# "does a negative gradient always lower the cost").
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq, mat

HESS = mat([['42', '14'], ['14', '6']])
HGEN = mat([['∑x²', '∑x'], ['∑x', 'n']])

K = Kit()

K.code('cost', r'''
# Cost of a straight line model on the pats and wags data from the lecture
data = [(1, 2), (2, 4), (4, 5)]

def cost(w, b):
    total = 0.0
    for x, y in data:
        pred = w * x + b
        total += (pred - y) ** 2
    return total

print("w=0.25 b=0.68 ->", round(cost(0.25, 0.68), 4))
print("w=1.00 b=1.37 ->", round(cost(1.00, 1.37), 4))
print("w=13/14 b=1.5 ->", round(cost(13 / 14, 1.5), 4))
''')

K.code('gd', r'''
# Gradient descent on the teaching model NN() = b with target 4
b, lr = 0.0, 0.1
for step in range(1, 9):
    slope = 2 * (b - 4)          # d cost / d b
    b = b - lr * slope
    print(step, "b =", round(b, 4), "cost =", round((b - 4) ** 2, 4))
''')

K.code('gd2', r'''
# Gradient descent on both w and b at once (partial derivatives)
data = [(1, 2), (2, 4), (4, 5)]
w, b, lr = 1.0, 1.37, 0.02
for step in range(1, 6):
    dw = sum(2 * (w * x + b - y) * x for x, y in data)
    db = sum(2 * (w * x + b - y) for x, y in data)
    w, b = w - lr * dw, b - lr * db
    c = sum((w * x + b - y) ** 2 for x, y in data)
    print(step, round(w, 4), round(b, 4), "cost", round(c, 4))
''')

K.lesson('fit', 'A model is a guess with knobs', f'''
<p>A dog gets patted and wags its tail. The lecture records three dogs: pats 1, 2 and 4 gave wags 2, 4 and 5. We want a rule that predicts wags from pats. The simplest rule is a straight line with two knobs.</p>
{fxs(fx('Linear model', 'wags(pats) = <i>w</i> · pats + <i>b</i>', '<i>w</i> is the weight (how steep), <i>b</i> is the bias (where the line starts at pats = 0).'))}
<p>A first random guess on the slide was <i>w</i> = 0.25 and <i>b</i> = 0.68. It predicts 0.93, 1.18 and 1.68, far below the real 2, 4 and 5. A second guess, <i>w</i> = 1.00 and <i>b</i> = 1.37, predicts 2.37, 3.37 and 5.37, much closer. Learning is the job of turning a bad guess into a good one automatically.</p>
{viz('regline')}
{scene('a taxi fare app', '<p>A taxi app predicts the fare from distance. Fare = rate × km + base fare. The rate is <i>w</i> and the base fare is <i>b</i>. The app learns both from thousands of past trips, exactly the way this lesson learns <i>w</i> and <i>b</i> from three dogs.</p>')}
{ladder(
    '<p>A model is a rule with dials. You turn the dials until the rule gives answers close to the real ones. Here the dials are <i>w</i> and <i>b</i>.</p>',
    '<p>Linear regression fits ŷ = <i>w</i>x + <i>b</i> by minimising squared error. With one input it has a closed form, but we learn it by gradient descent because that method also works for neural networks with millions of weights.</p>',
    '<p>The squared error cost is a convex quadratic in (<i>w</i>, <i>b</i>), so it has one minimum. Its Hessian, 2 times the matrix of ∑x², ∑x and n, sets the curvature and with it the largest safe learning rate.</p>',
    '<p>Neural language models are the same story at scale: a parametric function, a differentiable loss (cross entropy instead of squared error) and stochastic gradient methods. Research studies why non-convex losses of huge networks are still easy to optimise in practice.</p>')}
''', kw=['linear regression', 'weight', 'bias', 'model', 'prediction', 'pats and wags'])

K.lesson('cost', 'A cost function scores a guess', f'''
<p>To improve a guess we need one number that says how bad it is. The lecture uses the squared error: subtract the target from the prediction, square it, and add up over all examples.</p>
{fxs(fx('Squared error cost', 'C(<i>w</i>, <i>b</i>) = ∑<sub><i>i</i></sub> (<i>w</i>x<sub><i>i</i></sub> + <i>b</i> − y<sub><i>i</i></sub>)²', 'Squaring makes every error positive and punishes big errors much more than small ones.', key=True),
     fx('Mean squared error', 'MSE = ' + frac('1', 'n') + ' ∑ (ŷ<sub><i>i</i></sub> − y<sub><i>i</i></sub>)²', 'The same cost divided by the number of examples, so it does not grow with the data size.'))}
{steps('Worked example: the cost of w = 1.00, b = 1.37', [
    'Predictions: 1 × 1 + 1.37 = 2.37, then 3.37, then 5.37.',
    'Errors: 2.37 − 2 = 0.37, 3.37 − 4 = −0.63, 5.37 − 5 = 0.37.',
    'Squares: 0.1369, 0.3969, 0.1369.',
    eq('C = 0.1369 + 0.3969 + 0.1369 = 0.6707, the 0.67 on the slide')])}
{code('cost')}
{table(['Guess', 'Predictions', 'Cost'], [['<i>w</i> = 0.25, <i>b</i> = 0.68', '0.93, 1.18, 1.68', '20.12'], ['<i>w</i> = 1.00, <i>b</i> = 1.37', '2.37, 3.37, 5.37', '0.67'], ['<i>w</i> = 13/14, <i>b</i> = 1.5 (best)', '2.43, 3.36, 5.21', '0.643']])}
{note('The cost is a function of the knobs <i>w</i> and <i>b</i>, not of the data. The data is fixed. That is why we can draw it as a curve or a surface over the knobs.', 'tip')}
''', kw=['cost function', 'squared error', 'MSE', 'loss', 'error'])

K.lesson('descent', 'Rolling downhill: gradient descent', f'''
<p>The lecture first strips the network to its smallest form: NN() = <i>b</i>, no input at all, with target 4. The cost is (<i>b</i> − 4)², a U shaped parabola with its bottom at <i>b</i> = 4. We pretend we cannot see the answer and only feel the slope under our feet.</p>
{fxs(fx('Slope of the teaching cost', 'd C ÷ d<i>b</i> = 2(<i>b</i> − 4)', 'Positive slope: move left. Negative slope: move right. Zero: you are at the bottom.'),
     fx('Gradient descent update', '<i>b</i> ← <i>b</i> − η · ' + frac('dC', 'd<i>b</i>'), 'η is the learning rate, the fraction of the slope we step by.', key=True))}
{viz('gd1d')}
{steps('Worked example: two steps from b = 0 with η = 0.1', [
    'Slope at 0 is 2(0 − 4) = −8. New b = 0 − 0.1 × (−8) = 0.8.',
    'Slope at 0.8 is 2(0.8 − 4) = −6.4. New b = 0.8 + 0.64 = 1.44.',
    'The distance to 4 went 4, 3.2, 2.56: each step multiplies it by 1 − 2η = 0.8.',
    eq('Distance after n steps = 4 × 0.8<sup>n</sup>, so it shrinks but never jumps past the target')])}
{code('gd')}
{table(['Learning rate η', 'Factor 1 − 2η', 'What happens'], [['0.02', '0.96', 'Very slow, many steps'], ['0.1', '0.8', 'Smooth and steady'], ['0.5', '0', 'Lands on 4 in one step'], ['0.9', '−0.8', 'Jumps across, oscillates, settles'], ['1.05', '−1.1', 'Each jump grows: diverges']])}
{note('A negative slope does not by itself promise a lower cost after the step. If η is too large the step overshoots and the cost can go up. The lecture asked exactly this.', 'warn')}
{note('Expect "if ∂C/∂w is negative, does w increase or decrease after the update?" It increases, because w − η × (negative) adds a positive amount.', 'exam')}
''', kw=['gradient descent', 'learning rate', 'slope', 'derivative', 'overshoot', 'divergence'])

K.lesson('bowl', 'Two knobs: partial derivatives and the cost bowl', f'''
<p>With both <i>w</i> and <i>b</i> free, the cost is a surface over a flat plane of (<i>w</i>, <i>b</i>) pairs. The lecture plotted it in 3D: it is a bowl with one lowest point. To walk downhill we need the slope in each direction separately, which is what a partial derivative is.</p>
{fxs(fx('Partial derivatives of the squared error', frac('∂C', '∂<i>w</i>') + ' = ∑ 2(<i>w</i>x + <i>b</i> − y) · x &nbsp;&nbsp; ' + frac('∂C', '∂<i>b</i>') + ' = ∑ 2(<i>w</i>x + <i>b</i> − y)', 'Hold the other knob fixed and take the ordinary derivative.', key=True),
     fx('Update both at once', '<i>w</i> ← <i>w</i> − η ∂C/∂<i>w</i>, &nbsp; <i>b</i> ← <i>b</i> − η ∂C/∂<i>b</i>', 'The vector (∂C/∂<i>w</i>, ∂C/∂<i>b</i>) is the gradient. It points uphill, so we subtract it.'))}
{viz('gdbowl')}
{steps('Worked example: the gradient at w = 1, b = 1.37', [
    'Errors are 0.37, −0.63, 0.37 at x = 1, 2, 4.',
    '∂C/∂w = 2(0.37 × 1 − 0.63 × 2 + 0.37 × 4) = 2 × 0.59 = 1.18.',
    '∂C/∂b = 2(0.37 − 0.63 + 0.37) = 0.22.',
    eq('With η = 0.01: w = 1 − 0.0118 = 0.9882 and b = 1.37 − 0.0022 = 1.3678')])}
{code('gd2')}
{deep('why this bowl has a speed limit', '<p>The cost is quadratic, so its curvature is a constant matrix, the Hessian H = 2 {HGEN} = {HESS} for this data. Its eigenvalues are 46.80 and 1.196. Gradient descent is stable only when η < 2 ÷ λ<sub>max</sub> = 0.0427. The ratio 46.80 ÷ 1.196 ≈ 39 is the condition number: the bowl is a long narrow valley, which is why plain gradient descent zig-zags and why methods with momentum or per parameter rates (Adam) were invented.</p>')}
{note('Derivatives matter because they are the exact slope. No guessing is needed, and the same rule works for models with billions of knobs.', 'tip')}
''', kw=['partial derivative', 'gradient', 'cost surface', 'bowl', 'Hessian', 'condition number'])

K.lesson('tanh', 'The exam question: a tanh model by the chain rule', f'''
<p>In the revision class the model was changed to ŷ = tanh(<i>w</i>x + <i>b</i>) with one training example x = 1, y = 0.35 and loss L = (ŷ − y)². The task was to write ∂L/∂<i>w</i>. The chain rule breaks it into three small derivatives you already know.</p>
{fxs(fx('Chain rule for one neuron', frac('∂L', '∂<i>w</i>') + ' = ' + frac('∂L', '∂ŷ') + ' · ' + frac('∂ŷ', '∂z') + ' · ' + frac('∂z', '∂<i>w</i>') + ' = 2(ŷ − y) · (1 − ŷ²) · x', 'z = <i>w</i>x + <i>b</i>. The derivative of tanh z is 1 − tanh² z.', key=True))}
{steps('Worked example with w = 0.5, b = 0.1', [
    'z = 0.5 × 1 + 0.1 = 0.6, so ŷ = tanh 0.6 = 0.53705.',
    '∂L/∂ŷ = 2(0.53705 − 0.35) = 0.37410.',
    '∂ŷ/∂z = 1 − 0.53705² = 0.71158, and ∂z/∂w = x = 1.',
    eq('∂L/∂w = 0.37410 × 0.71158 × 1 = 0.2662. Positive, so the update lowers w')])}
{note('Formulas for derivatives are given in the exam if you need them. If none is given, the question can be answered without one. This was said in class.', 'exam')}
''', kw=['chain rule', 'tanh', 'backpropagation', 'exam question', 'derivative'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In wags(pats) = w · pats + b, the number b is called the', ['weight', 'bias', 'learning rate', 'cost'], 1,
       'It is where the line starts.', 'b shifts the whole line up or down. It is the bias.')
K.quiz('e', 'Why is the error squared in the cost?', ['To make it smaller', 'So errors cannot cancel and big errors count more', 'Because the data is squared', 'To make the cost negative'], 1,
       'Think of +2 and −2.', 'Squares are never negative and grow fast, so large mistakes dominate.')
K.quiz('e', 'The slope of the cost at the current b is positive. To lower the cost, b should', ['increase', 'decrease', 'stay the same', 'become zero'], 1,
       'Positive slope means uphill to the right.', 'Move against the slope: b − η × (positive) is smaller.')
K.quiz('e', 'The learning rate controls', ['how many examples there are', 'the size of each step', 'the number of layers', 'the target value'], 1,
       'It multiplies the slope.', 'Step = η × slope.')
K.quiz('m', 'For the cost (b − 4)², which η lands exactly on the minimum in one step from any start?', ['0.1', '0.25', '0.5', '1'], 2,
       'Next b = b − 2η(b − 4).', 'With η = 0.5, next b = b − (b − 4) = 4.')
K.quiz('m', 'For the same cost, which η makes gradient descent diverge?', ['0.3', '0.7', '0.95', '1.2'], 3,
       'The distance is multiplied by 1 − 2η.', '|1 − 2 × 1.2| = 1.4 > 1, so the distance grows.')
K.quiz('m', 'A partial derivative ∂C/∂w measures', ['the change in C when only w moves', 'the change in w when C moves', 'the sum of all slopes', 'the second derivative'], 0,
       'The other knob is frozen.', 'b is treated as a constant while w varies.')
K.quiz('m', 'The cost over (w, b) for squared error on a straight line looks like', ['a bowl with one lowest point', 'a flat plane', 'many separate valleys', 'a single straight ridge'], 0,
       'It is a quadratic.', 'A convex quadratic has one minimum, the bowl on the slide.')
K.quiz('h', 'The total gradient ∂C/∂w is negative. Does one update always lower the cost?', ['Yes, always', 'No, a step that is too large can overshoot', 'Only if b is zero', 'Only for tanh'], 1,
       'The class discussion.', 'The gradient gives a direction. The step size decides whether you land lower or jump past.')
K.quiz('h', 'For ŷ = tanh(wx + b) and L = (ŷ − y)², which factor appears in ∂L/∂w?', ['1 − ŷ²', 'ŷ(1 − ŷ)', 'e<sup>−z</sup>', 'w²'], 0,
       'Derivative of tanh.', 'd tanh z ÷ dz = 1 − tanh² z = 1 − ŷ².')
K.quiz('h', 'Why do we learn w and b by gradient descent when linear regression has a closed form?', ['The closed form is wrong', 'The same method scales to neural networks that have no closed form', 'Gradient descent is exact', 'It needs no data'], 1,
       'Think ahead to word2vec and RNNs.', 'Neural models have no formula for the best weights, but they all have gradients.')
K.quiz('x', 'For this data the Hessian of the cost has eigenvalues 46.8 and 1.2. Plain gradient descent will', ['converge for any η', 'be stable only for η < 0.0427 and zig-zag in the steep direction', 'never converge', 'converge in one step'], 1,
       'Stability needs |1 − ηλ| < 1 for every eigenvalue.', 'η < 2 ÷ 46.8. The large ratio of eigenvalues makes a narrow valley.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'With w = 0.25 and b = 0.68, what does the model predict for pats = 4?', '1.68', 'Multiply then add.',
       ['wags = w × pats + b.', '0.25 × 4 = 1.00.', eq('1.00 + 0.68 = 1.68')], check=1.68, tol=1e-9)
K.calc('e', 'What is the cost of w = 1, b = 1.37 on the data (1, 2), (2, 4), (4, 5)? Four decimals.', '0.6707', 'Errors 0.37, −0.63, 0.37.',
       ['Predictions 2.37, 3.37, 5.37.', 'Squared errors 0.1369, 0.3969, 0.1369.', eq('C = 0.6707')], check=0.6707, tol=1e-6)
K.calc('e', 'What is the slope of (b − 4)² at b = 1?', '-6', 'Slope = 2(b − 4).',
       ['d/db (b − 4)² = 2(b − 4).', 'At b = 1: 2 × (−3).', eq('slope = −6')], check=-6, tol=1e-9)
K.calc('e', 'From b = 1 with η = 0.1, what is the new b?', '1.6', 'b − η × slope.',
       ['Slope at 1 is −6.', 'η × slope = −0.6.', eq('new b = 1 − (−0.6) = 1.6')], check=1.6, tol=1e-9)
K.calc('m', 'What is the cost of w = 0.25, b = 0.68 on the lecture data? Four decimals.', '20.1197', 'Errors −1.07, −2.82, −3.32.',
       ['Predictions 0.93, 1.18, 1.68.', 'Squares 1.1449, 7.9524, 11.0224.', eq('C = 20.1197')], check=20.1197, tol=1e-6)
K.calc('m', 'Starting at b = 0 with η = 0.1 and target 4, what is b after two steps?', '1.44', 'The distance shrinks by 0.8 each step.',
       ['Distance 4, then 3.2, then 2.56.', 'b = 4 − 2.56.', eq('b = 1.44')], check=1.44, tol=1e-9)
K.calc('m', 'At w = 1, b = 1.37, what is ∂C/∂w on the lecture data? Two decimals.', '1.18', 'Sum 2 × error × x.',
       ['Errors 0.37, −0.63, 0.37 at x = 1, 2, 4.', 'Sum of error × x = 0.37 − 1.26 + 1.48 = 0.59.', eq('∂C/∂w = 2 × 0.59 = 1.18')], check=1.18, tol=1e-9)
K.calc('m', 'At the same point, what is ∂C/∂b? Two decimals.', '0.22', 'Sum 2 × error.',
       ['Sum of errors = 0.37 − 0.63 + 0.37 = 0.11.', 'Times 2.', eq('∂C/∂b = 0.22')], check=0.22, tol=1e-9)
K.calc('h', 'Least squares slope for (1, 2), (2, 4), (4, 5): w = Sxy ÷ Sxx. Give w to four decimals.', '0.9286', 'Means are 7/3 and 11/3.',
       ['Deviations of x: −4/3, −1/3, 5/3. Of y: −5/3, 1/3, 4/3.', 'Sxy = (20 − 1 + 20) ÷ 9 = 13/3. Sxx = (16 + 1 + 25) ÷ 9 = 14/3.', eq('w = 13/14 = 0.9286 and b = 11/3 − (13/14)(7/3) = 1.5')], check=13 / 14, tol=5e-5)
K.calc('h', 'Revision class: ŷ = tanh(wx + b), x = 1, y = 0.35, L = (ŷ − y)². With w = 0.5, b = 0.1, find ∂L/∂w. Four decimals.', '0.2662', 'Chain rule: 2(ŷ − y)(1 − ŷ²)x.',
       ['z = 0.6, ŷ = tanh 0.6 = 0.53705.', '2(ŷ − y) = 0.37410 and 1 − ŷ² = 0.71158.', eq('∂L/∂w = 0.37410 × 0.71158 × 1 = 0.2662')], check=0.2662006247547416, tol=5e-5)
K.calc('h', 'With η = 0.1 and target 4 from b = 0, how many steps until b is within 0.01 of 4? Whole number.', '27', 'Distance = 4 × 0.8<sup>n</sup>.',
       ['Need 4 × 0.8<sup>n</sup> < 0.01, so 0.8<sup>n</sup> < 0.0025.', 'n > ln 0.0025 ÷ ln 0.8 = 26.85.', eq('n = 27 steps')], check=27, tol=1e-9)
K.calc('x', 'The Hessian of the cost is ' + HESS + '. What is the largest stable learning rate 2 ÷ λ<sub>max</sub>? Four decimals.', '0.0427', 'λ = (trace ± √(trace² − 4 det)) ÷ 2.',
       ['Trace 48, determinant 42 × 6 − 14² = 56.', 'λ<sub>max</sub> = (48 + √(2304 − 224)) ÷ 2 = (48 + 45.607) ÷ 2 = 46.80.', eq('η<sub>max</sub> = 2 ÷ 46.80 = 0.0427')], check=0.042731839214901444, tol=5e-5)

# ---------------------------------------------------------------- assignments
K.assign('cost', 'e', 'The squared error cost',
         '<p>Write <code>cost(w, b, data)</code> that returns the sum of squared errors of the line w·x + b on a list of (x, y) pairs, rounded to 4 decimals.</p>',
         '''
def cost(w, b, data):
    # your code here
    pass
''', [('cost(1.0, 1.37, [(1, 2), (2, 4), (4, 5)])', 0.6707), ('cost(0.25, 0.68, [(1, 2), (2, 4), (4, 5)])', 20.1197), ('cost(2.0, 0.0, [(1, 2), (3, 6)])', 0.0)],
         '''
def cost(w, b, data):
    return round(sum((w * x + b - y) ** 2 for x, y in data), 4)
''', 'Loop over the pairs, square each error, add.', '<p>The first two tests are the two guesses on the lecture slides.</p>')
K.assign('gd1', 'm', 'Gradient descent on one knob',
         '<p>Write <code>descend(b, lr, target, n)</code> that runs n steps of gradient descent on (b − target)² and returns the list of b values after each step, each rounded to 4 decimals.</p>',
         '''
def descend(b, lr, target, n):
    # your code here
    pass
''', [('descend(0.0, 0.1, 4, 3)', [0.8, 1.44, 1.952]), ('descend(0.0, 0.5, 4, 2)', [4.0, 4.0]), ('descend(2.0, 0.9, 4, 2)', [5.6, 2.72])],
         '''
def descend(b, lr, target, n):
    out = []
    for _ in range(n):
        b = b - lr * 2 * (b - target)
        out.append(round(b, 4))
    return out
''', 'The slope is 2(b − target).', '<p>η = 0.5 lands in one step and η = 0.9 jumps across the target and back.</p>')
K.assign('grad2', 'h', 'Both partial derivatives',
         '<p>Write <code>grad(w, b, data)</code> returning (∂C/∂w, ∂C/∂b) of the squared error cost, each rounded to 4 decimals. Then write <code>step(w, b, data, lr)</code> returning the updated (w, b), rounded to 4 decimals.</p>',
         '''
def grad(w, b, data):
    # your code here
    pass

def step(w, b, data, lr):
    # your code here
    pass
''', [('grad(1.0, 1.37, [(1, 2), (2, 4), (4, 5)])', (1.18, 0.22)), ('step(1.0, 1.37, [(1, 2), (2, 4), (4, 5)], 0.01)', (0.9882, 1.3678)), ('grad(13/14, 1.5, [(1, 2), (2, 4), (4, 5)])', (0.0, 0.0))],
         '''
def grad(w, b, data):
    dw = sum(2 * (w * x + b - y) * x for x, y in data)
    db = sum(2 * (w * x + b - y) for x, y in data)
    return (round(dw, 4) + 0.0, round(db, 4) + 0.0)

def step(w, b, data, lr):
    dw, db = grad(w, b, data)
    return (round(w - lr * dw, 4), round(b - lr * db, 4))
''', 'Use the two formulas from the lesson. At the least squares answer both are zero.', '<p>The third test checks the bottom of the bowl, where the gradient vanishes. Adding 0.0 turns a −0.0 into 0.0.</p>')

K.must('Model and cost', 'A model has knobs (weights w and bias b). The squared error cost C = ∑(ŷ − y)² scores a guess. For the lecture data w = 1, b = 1.37 gives 0.67.')
K.must('Gradient descent', 'Move each knob against its slope: θ ← θ − η ∂C/∂θ. Too large η overshoots or diverges, too small η is slow.')
K.must('One knob example', 'NN() = b, cost (b − 4)², slope 2(b − 4). The distance to 4 is multiplied by 1 − 2η each step, η = 0.5 lands in one step.')
K.must('Partial derivatives', '∂C/∂w = ∑2(wx + b − y)x and ∂C/∂b = ∑2(wx + b − y). The cost over (w, b) is a bowl with one minimum.')
K.must('Chain rule', 'For ŷ = tanh(wx + b): ∂L/∂w = 2(ŷ − y)(1 − ŷ²)x. A negative gradient raises w, but a large step can still raise the cost.')

T = K.topic(
    slug='regression-gradient-descent', topic='nn-gradient-descent', step=(1, 'Neurons and learning', 'nn-learn', 'See how a model learns: costs, gradient descent, one neuron with a sigmoid, backpropagation by the chain rule and the activation functions that make deep networks work.', 'School and college'),
    title='From regression to learning by gradient descent', short='Gradient descent', badge='1.1', minutes=40, added='2026-11-01',
    lead='Fit a line to the pats and wags data from the lecture, score it with a cost, and let gradient descent find the best weight and bias by walking downhill.',
    desc='Linear models with a weight and a bias, the squared error cost, the NN() = b teaching model, slopes and the learning rate, partial derivatives on the cost bowl, the Hessian speed limit and the tanh chain rule question from the revision class.',
    summary='Weights, bias, squared error, gradient descent, learning rate, partial derivatives and the chain rule.',
    keywords=['linear regression', 'cost function', 'gradient descent', 'learning rate', 'partial derivative', 'chain rule'],
    recap='<p>A model has knobs. A cost scores a guess. Gradient descent moves every knob a small step against its slope until the cost stops falling. The learning rate decides whether the walk is slow, smooth, oscillating or explosive.</p>')
