# NLP section, chapter 1.2: one neuron, the sigmoid and backpropagation. Source: FoVL lecture 1 (the flower
# length and width data, NN(m1, m2) = sigmoid(w1·m1 + w2·m2 + b), the 0.82 example, why sigmoid, the 0.5 threshold)
# and the class notebook flowers 1.ipynb (eight flowers, the mystery flower (4.5, 1), sigmoid_p, 10,000 random
# steps with learning rate 0.1 and the chain rule written out as dcost_dpred, dpred_dz and dz_dw1).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from nlpkit import listing

K = Kit()

K.code('forward', r'''
# The neuron from the slide: NN(m1, m2) = sigmoid(w1*m1 + w2*m2 + b)
import math

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

w1, w2, b = 0.5, 0.2, 0.3
for length, width in [(2, 1), (3, 1.5), (4.5, 1)]:
    z = w1 * length + w2 * width + b
    pred = sigmoid(z)
    print(length, width, "z =", round(z, 2), "pred =", round(pred, 4), "red" if pred >= 0.5 else "blue")
''')

K.code('backprop', r'''
# One training step on one flower, with the chain rule written out as in the notebook
import math
sigmoid = lambda x: 1 / (1 + math.exp(-x))
sigmoid_p = lambda x: sigmoid(x) * (1 - sigmoid(x))

w1, w2, b, lr = 0.5, 0.2, 0.3, 0.1
length, width, target = 2, 1, 0           # a blue flower
z = length * w1 + width * w2 + b
pred = sigmoid(z)
cost = (pred - target) ** 2

dcost_dpred = 2 * (pred - target)
dpred_dz = sigmoid_p(z)
dcost_dz = dcost_dpred * dpred_dz
w1 = w1 - lr * dcost_dz * length
w2 = w2 - lr * dcost_dz * width
b = b - lr * dcost_dz * 1
print("cost before", round(cost, 4))
print("new w1, w2, b:", round(w1, 4), round(w2, 4), round(b, 4))
print("new pred", round(sigmoid(length * w1 + width * w2 + b), 4))
''')

NB_SRC = '''
data = [[3, 1.5, 1], [2, 1, 0], [4, 1.5, 1], [3, 1, 0],
        [3.5, .5, 1], [2, .5, 0], [5.5, 1, 1], [1, 1, 0]]
mystery_flower = [4.5, 1]

def sigmoid(x):
    return 1/(1+np.exp(-x))

def sigmoid_p(x):
    return sigmoid(x) * (1-sigmoid(x))

def train():
    w1, w2, b = np.random.randn(), np.random.randn(), np.random.randn()
    iterations, learning_rate = 10000, 0.1
    for i in range(iterations):
        point = data[np.random.randint(len(data))]
        z = point[0] * w1 + point[1] * w2 + b
        pred = sigmoid(z)
        target = point[2]
        dcost_dpred = 2 * (pred - target)
        dpred_dz = sigmoid_p(z)
        dcost_dz = dcost_dpred * dpred_dz
        w1 = w1 - learning_rate * dcost_dz * point[0]
        w2 = w2 - learning_rate * dcost_dz * point[1]
        b = b - learning_rate * dcost_dz * 1
    return w1, w2, b

w1, w2, b = train()
z = w1 * mystery_flower[0] + w2 * mystery_flower[1] + b
print(sigmoid(z))
print("close to 0 -> blue, close to 1 -> red")
'''

K.lesson('neuron', 'A neuron: weigh, add, squash', f'''
<p>The lecture moves from one input to two. Each flower has a length and a width, and is red (type 1) or blue (type 0). A mystery flower of length 4.5 and width 1 has an unknown colour. A neuron answers with a number between 0 and 1.</p>
{fxs(fx('One neuron with two inputs', 'NN(m₁, m₂) = σ(<i>w</i>₁m₁ + <i>w</i>₂m₂ + <i>b</i>)', 'Multiply each input by its weight, add the bias, then squash with the sigmoid σ.', key=True),
     fx('Sigmoid', 'σ(z) = ' + frac('1', '1 + e<sup>−z</sup>'), 'Maps any real number into (0, 1). σ(0) = 0.5.', key=True))}
{table(['length', '3', '2', '4', '3', '3.5', '2', '5.5', '1', '4.5'], [['width', '1.5', '1', '1.5', '1', '0.5', '0.5', '1', '1', '1'], ['type', '1', '0', '1', '0', '1', '0', '1', '0', '?']])}
{steps('Slide example: NN(2, 1) with w₁ = 0.5, w₂ = 0.2, b = 0.3', [
    'Weighted sum z = 0.5 × 2 + 0.2 × 1 + 0.3 = 1.5.',
    'σ(1.5) = 1 ÷ (1 + e<sup>−1.5</sup>) = 1 ÷ 1.2231.',
    eq('NN(2, 1) = 0.8176, about 0.82'),
    'But the flower (2, 1) is blue, type 0. These starting weights are wrong, which is why we must train.'])}
{code('forward')}
{ladder(
    '<p>A neuron is a tiny voting machine. Each input gets a vote strength (the weight). It adds the votes and then says "how sure am I" as a number from 0 to 1.</p>',
    '<p>One sigmoid neuron is logistic regression: a linear score z = <b>w</b>·<b>x</b> + b followed by σ. Its output is read as P(class 1 | x), and the decision boundary σ(z) = 0.5 is the straight line z = 0.</p>',
    '<p>With cross entropy loss, logistic regression is a convex problem whose gradient is (σ(z) − y)<b>x</b>. The notebook uses squared error instead, which works here but is not convex and gives weaker gradients when the neuron is confidently wrong.</p>',
    '<p>Every output layer of a word2vec, RNN or transformer model is this same unit, generalised from σ to softmax over a vocabulary. Calibration of these probabilities and their behaviour far from the training data are active research topics.</p>')}
''', kw=['neuron', 'sigmoid', 'logistic regression', 'weights', 'flowers'])

K.lesson('why', 'Why the sigmoid, and where to draw the line', f'''
<p>A plain linear score can be any number from −∞ to +∞. A value like 12 or −7 has no probabilistic meaning and no natural cutoff. The sigmoid fixes that: it squeezes the score into (0, 1), so we can read it as a probability and use 0.5 as the cutoff.</p>
{fxs(fx('Decision rule', 'class 1 if σ(z) ≥ 0.5, which is the same as z ≥ 0', 'The boundary is the line <i>w</i>₁·length + <i>w</i>₂·width + <i>b</i> = 0.'),
     fx('Inverse of the sigmoid (logit)', 'z = ln ' + frac('p', '1 − p'), 'p = 0.8 needs z = ln 4 = 1.386.'),
     fx('Symmetry', 'σ(−z) = 1 − σ(z)', 'Used again in negative sampling.'))}
{viz('flowers')}
{table(['Output', 'Reading'], [['0.92', 'very likely red'], ['0.5', 'cannot tell, on the boundary'], ['0.08', 'very likely blue']])}
{scene('spam filter', '<p>An email filter adds up weighted clues: the word "free", a strange sender, many links. The sigmoid turns the total into "92 percent spam". The filter only moves the mail when the number passes a threshold, and that threshold can be moved to make it stricter or more relaxed.</p>')}
{note('The 0.5 threshold is a choice, not a law. A cancer screening test may use 0.2 to miss fewer cases. Changing the threshold moves the decision line without retraining.', 'tip')}
''', kw=['decision boundary', 'threshold', 'logit', 'probability', 'classification'])

K.lesson('backprop', 'Backpropagation is the chain rule', f'''
<p>To train, the notebook picks a random flower, predicts, measures the squared cost and nudges w₁, w₂ and b downhill. The slope of the cost with respect to each weight comes from the chain rule, one link at a time. The notebook names every link, and so do we.</p>
{fxs(fx('The three links', frac('∂cost', '∂w₁') + ' = ' + frac('∂cost', '∂pred') + ' · ' + frac('∂pred', '∂z') + ' · ' + frac('∂z', '∂w₁') + ' = 2(pred − target) · σ′(z) · length', 'For w₂ the last link is width, for b it is 1.', key=True),
     fx('Slope of the sigmoid', 'σ′(z) = σ(z)(1 − σ(z))', 'Largest at z = 0, where it is 0.25. Called sigmoid_p in the notebook.', key=True))}
{steps('Worked step on the blue flower (2, 1) with η = 0.1', [
    'Forward: z = 1.5, pred = 0.8176, cost = (0.8176 − 0)² = 0.6684.',
    'dcost/dpred = 2 × 0.8176 = 1.6351. dpred/dz = 0.8176 × 0.1824 = 0.1491.',
    'dcost/dz = 1.6351 × 0.1491 = 0.2439. dcost/dw₁ = 0.2439 × 2 = 0.4878.',
    eq('w₁ ← 0.5 − 0.1 × 0.4878 = 0.4512. w₂ and b also drop, and the next prediction is lower')])}
{code('backprop')}
{note('Do not forget the σ′(z) link. Without it you are differentiating a straight line, not a neuron.', 'warn')}
{note('A typical question gives ŷ = σ(wx + b) or tanh(wx + b), one data point and the cost, and asks for ∂L/∂w, the predicted value, and the direction w moves.', 'exam')}
''', kw=['backpropagation', 'chain rule', 'sigmoid derivative', 'sigmoid_p', 'update rule'])

K.lesson('notebook', 'The flowers notebook, line by line', f'''
<p>The class notebook trains the neuron for 10,000 steps, each on one random flower, with learning rate 0.1. Every 100 steps it adds the cost over all eight flowers to a list so that you can plot it going down. After training the mystery flower scores 0.9917: red.</p>
{listing(NB_SRC, '0.9917291708851436\nclose to 0 -> blue, close to 1 -> red', title='flowers 1.ipynb, the training cells (numpy and matplotlib parts trimmed)', cap='Output recorded in the class notebook')}
{steps('What each part does', [
    'np.random.randn() gives each weight a random start, so every run begins somewhere different.',
    'One random flower per step is stochastic gradient descent: cheap, noisy steps that still head downhill on average.',
    'The cost list is only for watching. It plays no part in the updates.',
    'The final picture colours a 20 × 20 grid by the prediction. The colours split along the straight line where z = 0.'])}
{deep('squared error against cross entropy for a sigmoid', '<p>With squared error the gradient is 2(σ − y)σ(1 − σ)x. If the neuron is confidently wrong, for example σ = 0.001 when y = 1, the factor σ(1 − σ) is about 0.001 and learning almost stops. With binary cross entropy L = −[y ln σ + (1 − y) ln(1 − σ)] the σ′ term cancels and the gradient is simply (σ − y)x, strong exactly when the mistake is big. That is why classification layers use cross entropy, and why the RNN chapters do too.</p>')}
''', kw=['notebook', 'stochastic gradient descent', 'training loop', 'mystery flower', 'cross entropy'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What does σ(0) equal?', ['0', '0.25', '0.5', '1'], 2, '1 ÷ (1 + e⁰).', 'e⁰ = 1, so σ(0) = 1 ÷ 2.')
K.quiz('e', 'The sigmoid output always lies', ['between −1 and 1', 'between 0 and 1', 'above 1', 'below 0'], 1, 'It is used as a probability.', 'σ maps every real number into (0, 1).')
K.quiz('e', 'With threshold 0.5, an output of 0.92 for the flowers means', ['blue', 'red', 'no answer', 'the flower is wrong'], 1, 'Type 1 is red.', 'Above 0.5 means class 1, red.')
K.quiz('e', 'How many trainable numbers does the two input neuron have?', ['2', '3', '4', '8'], 1, 'Count the weights and the bias.', 'w₁, w₂ and b.')
K.quiz('m', 'σ(z) = 0.5 exactly when', ['z = 0', 'z = 0.5', 'z = 1', 'z is very large'], 0, 'Where e<sup>−z</sup> = 1.', 'So the decision boundary is the line z = 0.')
K.quiz('m', 'Which expression is σ′(z)?', ['σ(z)(1 − σ(z))', '1 − σ(z)²', 'e<sup>−z</sup>', 'σ(z) + 1'], 0, '1 − σ² belongs to tanh.', 'The derivative of the logistic function is σ(1 − σ).')
K.quiz('m', 'The notebook picks one random flower per update. This is called', ['batch gradient descent', 'stochastic gradient descent', 'Newton’s method', 'grid search'], 1, 'One sample at a time.', 'Each step uses one example, so the steps are cheap and noisy.')
K.quiz('m', 'The decision boundary of one sigmoid neuron on two inputs is', ['a circle', 'a straight line', 'two lines', 'any curve'], 1, 'z = w₁x + w₂y + b = 0.', 'A linear equation in two variables is a line.')
K.quiz('h', 'A neuron outputs 0.001 for a red flower (target 1), with squared error loss. Learning is slow because', ['the learning rate is zero', 'σ′(z) is tiny, about 0.001', 'the flower is too long', 'the bias is positive'], 1, 'Look at the middle link.', 'σ(1 − σ) ≈ 0.001 multiplies the whole gradient.')
K.quiz('h', 'Why can one sigmoid neuron not learn XOR of two binary inputs?', ['It has no bias', 'XOR is not separable by one straight line', 'Sigmoid is too slow', 'XOR needs negative weights'], 1, 'Draw the four points.', '(0,1) and (1,0) are class 1, (0,0) and (1,1) class 0. No single line splits them.')
K.quiz('h', 'σ(−z) equals', ['−σ(z)', '1 − σ(z)', '1 ÷ σ(z)', 'σ(z)'], 1, 'Add the two fractions.', '1 ÷ (1 + e<sup>z</sup>) = e<sup>−z</sup> ÷ (1 + e<sup>−z</sup>) = 1 − σ(z).')
K.quiz('x', 'With binary cross entropy loss, the gradient of the loss with respect to z for a sigmoid neuron is', ['(σ − y)σ(1 − σ)', 'σ − y', '2(σ − y)', '(σ − y)²'], 1, 'The σ′ cancels.', 'dL/dz = (σ − y), which is why cross entropy learns fast when the neuron is confidently wrong.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Compute NN(2, 1) = σ(0.5 × 2 + 0.2 × 1 + 0.3). Four decimals.', '0.8176', 'First z, then σ.',
       ['z = 1 + 0.2 + 0.3 = 1.5.', 'e<sup>−1.5</sup> = 0.22313.', eq('σ = 1 ÷ 1.22313 = 0.8176')], check=0.8175744761936437, tol=5e-5)
K.calc('e', 'What is σ′(0)?', '0.25', 'σ(0)(1 − σ(0)).',
       ['σ(0) = 0.5.', '1 − σ(0) = 0.5.', eq('σ′(0) = 0.25')], check=0.25, tol=1e-9)
K.calc('e', 'With w₁ = 0.5, w₂ = 0.2, b = 0.3, what is z for the flower (3, 1.5)? One decimal.', '2.1', 'w₁·length + w₂·width + b.',
       ['0.5 × 3 = 1.5.', '0.2 × 1.5 = 0.3.', eq('z = 1.5 + 0.3 + 0.3 = 2.1')], check=2.1, tol=1e-9)
K.calc('m', 'Squared cost of the blue flower (2, 1) under the same weights. Four decimals.', '0.6684', '(pred − 0)².',
       ['pred = 0.81757.', 'Target 0.', eq('cost = 0.81757² = 0.6684')], check=0.6684280241233108, tol=5e-5)
K.calc('m', 'For that flower, find dcost/dw₁ = 2(pred − target)σ′(z) × length. Four decimals.', '0.4878', 'σ′(1.5) = 0.8176 × 0.1824.',
       ['2(pred − 0) = 1.63515.', 'σ′(1.5) = 0.14915.', eq('1.63515 × 0.14915 × 2 = 0.4878')], check=0.4877533297101711, tol=5e-5)
K.calc('m', 'Update w₁ = 0.5 with η = 0.1 using that gradient. Four decimals.', '0.4512', 'w₁ − η × gradient.',
       ['η × gradient = 0.04878.', '0.5 − 0.04878.', eq('w₁ = 0.4512')], check=0.4512246670289829, tol=5e-5)
K.calc('m', 'Which z gives σ(z) = 0.8? Four decimals.', '1.3863', 'z = ln(p ÷ (1 − p)).',
       ['p ÷ (1 − p) = 0.8 ÷ 0.2 = 4.', 'z = ln 4.', eq('z = 1.3863')], check=1.3862943611198906, tol=5e-5)
K.calc('h', 'Weights w₁ = 2, w₂ = 1, b = −7. Along width = 1, at what length is the neuron exactly 0.5?', '3', 'Solve 2·length + 1 − 7 = 0.',
       ['Boundary: z = 0.', '2 × length + 1 × 1 − 7 = 0.', eq('length = 3')], check=3, tol=1e-9)
K.calc('h', 'Binary cross entropy for prediction 0.9 and target 1, natural log. Four decimals.', '0.1054', 'L = −ln 0.9.',
       ['Only the y ln σ term survives when y = 1.', 'ln 0.9 = −0.10536.', eq('L = 0.1054')], check=0.10536051565782628, tol=5e-5)
K.calc('h', 'How small is σ′(5)? Give it to five decimals.', '0.00665', 'σ(5) = 0.99331.',
       ['σ(5) = 1 ÷ (1 + e<sup>−5</sup>) = 0.993307.', '1 − σ(5) = 0.006693.', eq('σ′(5) = 0.993307 × 0.006693 = 0.00665')], check=0.006648056670790033, tol=5e-6)
K.calc('x', 'Ten sigmoid layers in a row. What is the largest possible product of their ten slopes? Scientific notation, three digits.', '9.54e-7', 'Each slope is at most 0.25.',
       ['Maximum of σ′ is 0.25 at z = 0.', '0.25<sup>10</sup> = 1 ÷ 4<sup>10</sup> = 1 ÷ 1,048,576.', eq('9.54 × 10⁻⁷: the vanishing gradient that RNN chapters return to')], check=9.5367431640625e-07, tol=5e-9)

# ---------------------------------------------------------------- assignments
K.assign('predict', 'e', 'Predict a flower',
         '<p>Write <code>predict(w1, w2, b, length, width)</code> returning the sigmoid output rounded to 4 decimals, and <code>colour(...)</code> with the same arguments returning "red" when the output is at least 0.5, else "blue".</p>',
         '''
import math

def predict(w1, w2, b, length, width):
    # your code here
    pass

def colour(w1, w2, b, length, width):
    # your code here
    pass
''', [('predict(0.5, 0.2, 0.3, 2, 1)', 0.8176), ('colour(0.5, 0.2, 0.3, 2, 1)', 'red'), ('colour(2, 1, -7, 2, 1)', 'blue'), ('predict(0, 0, 0, 4, 4)', 0.5)],
         '''
import math

def predict(w1, w2, b, length, width):
    z = w1 * length + w2 * width + b
    return round(1 / (1 + math.exp(-z)), 4)

def colour(w1, w2, b, length, width):
    return "red" if predict(w1, w2, b, length, width) >= 0.5 else "blue"
''', 'z first, then 1 ÷ (1 + e<sup>−z</sup>).', '<p>The first test is the slide example.</p>')
K.assign('sgdstep', 'm', 'One backpropagation step',
         '<p>Write <code>step(w1, w2, b, point, lr)</code> where point is [length, width, target]. Use squared error and the chain rule from the notebook. Return the new (w1, w2, b), each rounded to 4 decimals.</p>',
         '''
import math

def step(w1, w2, b, point, lr):
    # your code here
    pass
''', [('step(0.5, 0.2, 0.3, [2, 1, 0], 0.1)', (0.4512, 0.1756, 0.2756)), ('step(0.5, 0.2, 0.3, [3, 1.5, 1], 0.1)', (0.5064, 0.2032, 0.3021))],
         '''
import math

def step(w1, w2, b, point, lr):
    s = lambda x: 1 / (1 + math.exp(-x))
    z = point[0] * w1 + point[1] * w2 + b
    pred = s(z)
    dz = 2 * (pred - point[2]) * pred * (1 - pred)
    return (round(w1 - lr * dz * point[0], 4), round(w2 - lr * dz * point[1], 4), round(b - lr * dz, 4))
''', 'dcost_dz = 2(pred − target) × σ(z)(1 − σ(z)). Then multiply by length, width and 1.', '<p>A blue flower pushes every weight down and a red flower pushes them up.</p>')
K.assign('train', 'h', 'Train the neuron with a fixed order',
         '<p>Write <code>train(data, lr, epochs)</code>. Start from w1 = w2 = b = 0. In each epoch visit the flowers in the given order and do one step per flower (squared error, as in the notebook). Return (w1, w2, b) rounded to 3 decimals. Also write <code>accuracy(data, w1, w2, b)</code> returning the fraction classified correctly with threshold 0.5.</p>',
         '''
import math

def train(data, lr, epochs):
    # your code here
    pass

def accuracy(data, w1, w2, b):
    # your code here
    pass
''', [('accuracy([[3,1.5,1],[2,1,0],[4,1.5,1],[3,1,0],[3.5,.5,1],[2,.5,0],[5.5,1,1],[1,1,0]], *train([[3,1.5,1],[2,1,0],[4,1.5,1],[3,1,0],[3.5,.5,1],[2,.5,0],[5.5,1,1],[1,1,0]], 0.5, 2000))', 1.0),
      ('train([[1, 1, 1]], 0.1, 0)', (0.0, 0.0, 0.0))],
         '''
import math

def train(data, lr, epochs):
    s = lambda x: 1 / (1 + math.exp(-x))
    w1 = w2 = b = 0.0
    for _ in range(epochs):
        for x1, x2, t in data:
            p = s(w1 * x1 + w2 * x2 + b)
            dz = 2 * (p - t) * p * (1 - p)
            w1, w2, b = w1 - lr * dz * x1, w2 - lr * dz * x2, b - lr * dz
    return (round(w1, 3), round(w2, 3), round(b, 3))

def accuracy(data, w1, w2, b):
    s = lambda x: 1 / (1 + math.exp(-x))
    ok = sum((s(w1 * x1 + w2 * x2 + b) >= 0.5) == (t == 1) for x1, x2, t in data)
    return ok / len(data)
''', 'Reuse your step function inside two loops.', '<p>With a fixed order, η = 0.5 and 2,000 epochs the line separates all eight notebook flowers. After only 400 epochs one blue flower (3, 1) is still on the red side, because it sits very close to the red flower (3, 1.5).</p>')

K.must('Neuron', 'NN(x) = σ(w·x + b) with σ(z) = 1 ÷ (1 + e<sup>−z</sup>). NN(2, 1) with w = (0.5, 0.2), b = 0.3 is 0.82. Output above 0.5 means class 1.')
K.must('Boundary', 'σ(z) = 0.5 exactly at z = 0, so one neuron draws a straight line. It cannot separate XOR.')
K.must('Chain rule', '∂cost/∂w₁ = 2(pred − target) · σ(z)(1 − σ(z)) · x₁. For b the last factor is 1. Update w ← w − η · gradient.')
K.must('Notebook', '10,000 random single flower steps with η = 0.1 from random weights. The mystery flower (4.5, 1) comes out 0.99, red.')
K.must('Loss choice', 'Squared error with a sigmoid learns slowly when confidently wrong. Cross entropy gives the clean gradient (σ − y)x.')

T = K.topic(
    slug='neuron-backprop', topic='nn-neuron', step=(1, 'Neurons and learning', 'nn-learn', 'See how a model learns: costs, gradient descent, one neuron with a sigmoid, backpropagation by the chain rule and the activation functions that make deep networks work.', 'School and college'),
    title='One neuron, the sigmoid and backpropagation', short='Neuron and backprop', badge='1.2', minutes=40, added='2026-11-01',
    lead='Teach a single neuron to tell red flowers from blue ones, exactly as the class notebook does, and see backpropagation as nothing more than the chain rule.',
    desc='The two input neuron, the sigmoid and why it is needed, decision boundaries and the 0.5 threshold, the logit, backpropagation by the chain rule, the flowers notebook line by line, and squared error against cross entropy.',
    summary='A neuron, the sigmoid, the decision line, backpropagation and the flowers notebook.',
    keywords=['neuron', 'sigmoid', 'logistic regression', 'backpropagation', 'chain rule', 'flowers notebook', 'SGD'],
    recap='<p>A neuron weighs its inputs, adds a bias and squashes the result with a sigmoid into a probability. Training follows the chain rule backwards from the cost to every weight, one small step per example.</p>')
