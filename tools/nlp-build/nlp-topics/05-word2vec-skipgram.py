# NLP section, chapter 2.2: word2vec with the full softmax. Source: FoVL lecture 2 slides 7 to 20 (Mikolov et al.
# 2013, centre and outside words, the window of size 2 around "banking", the likelihood and its three transformations,
# the prediction function as dot product, exponentiation and softmax, the network view with a one-hot input, the
# WORD2VEC-SKIPGRAM pseudo-code, stochastic gradient descent, two vectors per word, skip-gram against CBOW against
# GloVe), the class notebook word2vec 1.ipynb (five sentences, window 1, d = 3, η = 0.05, 500 epochs) and the
# practice questions on slides 123 and 124 of lecture 3.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from nlpkit import listing

K = Kit()

K.code('pairs', r'''
# Training pairs exactly as the notebook builds them (window = 1)
corpus = ["cats like milk", "cats drink milk", "dogs like milk", "dogs chase balls", "cats chase balls"]
sentences = [s.split() for s in corpus]
vocab = sorted(set(w for s in sentences for w in s))
word_to_id = {w: i for i, w in enumerate(vocab)}
print("Vocabulary:", vocab)

window = 1
pairs = []
for sentence in sentences:
    ids = [word_to_id[w] for w in sentence]
    for i, center in enumerate(ids):
        for j in range(max(0, i - window), min(len(ids), i + window + 1)):
            if i != j:
                pairs.append((center, ids[j]))
print(len(pairs), "pairs, first six:", pairs[:6])
''')

K.code('softmax', r'''
# Forward pass and loss for one (centre, context) pair, as in the sgstep animation
import math
h = [0.2, 0.1]                                   # E[cats]
U = {"cats": [0.1, 0.3], "like": [0.5, -0.2], "milk": [0.2, 0.4], "dogs": [-0.3, 0.1]}

scores = {w: sum(a * b for a, b in zip(h, u)) for w, u in U.items()}
Z = sum(math.exp(s) for s in scores.values())
probs = {w: math.exp(s) / Z for w, s in scores.items()}
for w in U:
    print(w.ljust(5), "score", round(scores[w], 3), "p", round(probs[w], 4))
print("loss for context 'like':", round(-math.log(probs["like"]), 4))
''')

NB = '''
np.random.seed(42)
E = np.random.randn(V, d) * 0.1          # input (centre) vectors, one row per word
W = np.random.randn(d, V) * 0.1          # output weights, one column per word

def softmax(x):
    x = x - np.max(x)
    exp_x = np.exp(x)
    return exp_x / np.sum(exp_x)

for epoch in range(epochs):              # epochs = 500, learning_rate = 0.05, d = 3
    np.random.shuffle(pairs)
    for center, context in pairs:
        h = E[center].copy()             # forward pass
        scores = h @ W
        probabilities = softmax(scores)
        loss = -np.log(probabilities[context] + 1e-12)
        error = probabilities.copy()     # backpropagation
        error[context] -= 1
        gradient_W = np.outer(h, error)
        gradient_h = W @ error
        W -= learning_rate * gradient_W
        E[center] -= learning_rate * gradient_h
'''
NB_OUT = '''Learned word embeddings:
balls [-1.266 -1.971 -1.919]
cats [ 0.009 -1.334  0.439]
chase [ 1.113  0.284 -1.355]
dogs [-1.852 -1.044  0.163]
drink [0.983 1.665 1.2  ]
like [-0.486  1.588 -0.12 ]
milk [-0.314 -0.637  2.018]
Words similar to cats: [('milk', 0.577), ('dogs', 0.483), ('balls', 0.417)]
Words similar to dogs: [('balls', 0.634), ('cats', 0.483), ('milk', 0.345)]'''

K.lesson('idea', 'The word2vec idea: predict the neighbours', f'''
<p>Word2vec (Mikolov and others, 2013) learns word vectors by a simple game. Walk through a long text. At each position t there is a centre word c and outside words o within a window. Use the similarity of the vectors of c and o to compute the probability of o given c, and keep adjusting the vectors to make the true neighbours more probable.</p>
{viz('sgwindow')}
{fxs(fx('Likelihood of the whole text', 'L(θ) = ∏<sub>t=1</sub><sup>T</sup> ∏<sub>−m ≤ j ≤ m, j ≠ 0</sub> P(w<sub>t+j</sub> | w<sub>t</sub>, θ)', 'θ is every word vector. The product runs over every position and every neighbour in the window.'),
     fx('Objective to minimise', 'J(θ) = −' + frac('1', 'T') + ' ∑<sub>t</sub> ∑<sub>j</sub> log P(w<sub>t+j</sub> | w<sub>t</sub>, θ)', 'The average negative log likelihood.', key=True))}
{steps('Three transformations of the likelihood, from the slide', [
    'Take the log: products become sums and tiny numbers no longer underflow.',
    'Put a minus sign in front: optimisers minimise, so we minimise the negative log likelihood.',
    'Divide by T: the average does not grow with the length of the corpus.',
    eq('Minimising J is the same as maximising the likelihood L')])}
{code('pairs')}
{scene('guessing a missing word', '<p>On a phone keyboard, after "I will call you" the words "later" and "tomorrow" are offered. A model that has seen millions of sentences learns that both often sit in the same places, so their vectors end up close. Word2vec is that guessing game played on a whole corpus, keeping the vectors and throwing away the guesses.</p>')}
''', kw=['word2vec', 'skip-gram', 'centre word', 'context word', 'likelihood', 'objective function'])

K.lesson('predict', 'The prediction function: dot, exponentiate, normalise', f'''
<p>Each word has two vectors: v<sub>w</sub> when it is the centre word and u<sub>w</sub> when it is an outside word. The lecture stresses that these are not two meanings of the word but two roles it can play. The probability of an outside word is a softmax over dot products.</p>
{fxs(fx('Skip-gram prediction function', 'P(o | c) = ' + frac('exp(u<sub>o</sub> · v<sub>c</sub>)', '∑<sub>w ∈ V</sub> exp(u<sub>w</sub> · v<sub>c</sub>)'), 'Step 1 dot product (similarity), step 2 exp (always positive), step 3 divide by the sum (a distribution).', key=True),
     fx('Softmax', 'softmax(x)<sub>i</sub> = ' + frac('exp(x<sub>i</sub>)', '∑<sub>j</sub> exp(x<sub>j</sub>)'), '"Max" because large scores dominate, "soft" because small ones still get some probability.'))}
{table(['Step', 'What it does', 'Why'], [['1. Dot product u<sub>o</sub>·v<sub>c</sub>', 'Scores how compatible the two words are', 'banking and crises score high, banking and skillet low'], ['2. Exponentiate', 'Makes every score positive', 'Probabilities cannot be negative, and big scores grow much bigger'], ['3. Normalise', 'Divides by the sum over the vocabulary', 'The probabilities add to 1']])}
<p>In network terms the input is the one-hot vector of the centre word, which simply selects its row of the embedding matrix E. That vector h is compared by dot product with every output vector, giving one score per vocabulary word. Softmax turns the scores into probabilities. Training raises the probability of the true context words, and over time words that appear in similar contexts get similar vectors.</p>
{viz('sgstep')}
{code('softmax')}
{note('Sigmoid or softmax? The lecture answer: sigmoid for a yes or no (binary) decision, softmax for picking one of many classes. Full word2vec picks one word out of V, so it uses softmax. Negative sampling turns it into many yes or no decisions, so it uses sigmoids.', 'exam')}
''', kw=['softmax', 'prediction function', 'two vectors per word', 'one-hot input', 'embedding matrix', 'dot product'])

K.lesson('train', 'Training: the gradient and the notebook loop', f'''
<p>The slide pseudo-code WORD2VEC-SKIPGRAM builds the vocabulary, initialises E and W randomly, generates the training pairs, and then for each epoch shuffles the pairs and runs one forward pass, one loss and one update per pair. The gradient has a beautiful form: what the model expected minus what it saw.</p>
{fxs(fx('Gradient for the centre vector', frac('∂J', '∂v<sub>c</sub>') + ' = −u<sub>o</sub> + ∑<sub>w ∈ V</sub> P(w | c) u<sub>w</sub>', 'Observed context vector against the expected context vector under the model.', key=True),
     fx('In the notebook’s matrix form', 'error = p − y, &nbsp; ∂J/∂h = W · error, &nbsp; ∂J/∂W = h ⊗ error', 'y is the one-hot vector of the true context word. ⊗ is the outer product.'),
     fx('Stochastic gradient descent', 'θ ← θ − η ∇<sub>θ</sub> J<sub>window</sub>(θ)', 'Update after each sampled window, not after the whole corpus.'))}
{steps('Derive the centre gradient in three lines', [
    'log P(o | c) = u<sub>o</sub>·v<sub>c</sub> − log ∑<sub>w</sub> exp(u<sub>w</sub>·v<sub>c</sub>).',
    'Differentiate the first term: u<sub>o</sub>. Differentiate the log sum: ∑<sub>w</sub> exp(u<sub>w</sub>·v<sub>c</sub>) u<sub>w</sub> ÷ ∑<sub>x</sub> exp(u<sub>x</sub>·v<sub>c</sub>) = ∑<sub>w</sub> P(w | c) u<sub>w</sub>.',
    eq('∂(−log P(o | c)) ÷ ∂v<sub>c</sub> = −u<sub>o</sub> + ∑<sub>w</sub> P(w | c) u<sub>w</sub>')])}
{listing(NB, NB_OUT, title='word2vec 1.ipynb, the training cell (full softmax)', cap='Output recorded in the class notebook')}
{viz('w2vtrain')}
{note('J depends on every window in the corpus, possibly billions. Computing the full gradient before one update would take forever, so all neural NLP models use stochastic or mini batch gradient descent.', 'tip')}
{note('With full softmax the error vector p − y has V entries, so every single update touches all V output vectors. That is the cost negative sampling removes.', 'warn')}
''', kw=['gradient', 'SGD', 'mini batch', 'training loop', 'notebook', 'outer product', 'pseudo-code'])

K.lesson('variants', 'Skip-gram, CBOW and why two vectors', f'''
<p>Word2vec comes in two model variants and several loss functions. Each word keeps two vectors because that makes the optimisation easier (a word is rarely its own neighbour). At the end the two are usually averaged.</p>
{table(['Model', 'Predicts', 'Learns'], [['Skip-gram', 'the context words from the centre word', 'vectors that capture co-occurrence patterns, good for rare words'], ['CBOW', 'the centre word from the bag of context words', 'similar vectors, faster to train'], ['GloVe (chapter 2.4)', 'log co-occurrence counts', 'vectors that encode global count statistics']])}
{fxs(fx('CBOW input', 'h = ' + frac('1', '2m') + ' ∑<sub>−m ≤ j ≤ m, j ≠ 0</sub> v<sub>w<sub>t+j</sub></sub>', 'Average the context vectors, then predict the centre word with the same softmax.'),
     fx('Parameters of skip-gram with full softmax', '|E| + |W| = V·d + d·V = 2Vd', 'V = 10,000 and d = 300 give 6,000,000 numbers.', key=True))}
{table(['Loss', 'Cost per pair', 'Note'], [['Naive softmax', 'V dot products', 'Simple but expensive with many output classes'], ['Hierarchical softmax', 'about log₂ V', 'A binary tree over the vocabulary'], ['Negative sampling', '1 + K sigmoids', 'The standard choice, chapter 2.3']])}
{ladder(
    '<p>Skip-gram looks at one word and guesses its neighbours. CBOW looks at the neighbours and guesses the missing word, like a fill in the blank exercise.</p>',
    '<p>Both are shallow networks: an embedding lookup, a dot product layer and a softmax. Skip-gram makes 2m training examples per position, CBOW one, so skip-gram sees rare words more often.</p>',
    '<p>The softmax normaliser costs O(V) per example. Hierarchical softmax replaces it with a path of log₂ V binary decisions in a Huffman tree, and negative sampling with a noise contrastive objective of K + 1 terms.</p>',
    '<p>Static embeddings give one vector per word type. Their ideas survive inside modern models: the input embedding table of a transformer is E, the output projection is W, and many models tie the two, which is exactly the "average the two vectors" observation made trainable.</p>')}
''', kw=['CBOW', 'skip-gram', 'hierarchical softmax', 'parameters', 'two vectors'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In skip-gram the model predicts', ['the centre word from its context', 'the context words from the centre word', 'the next sentence', 'the part of speech'], 1, 'Skip over the centre.', 'Given the centre word, predict the outside words.')
K.quiz('e', 'Word2vec was introduced by', ['Pennington et al. 2014', 'Mikolov et al. 2013', 'Bengio et al. 2003', 'Firth 1957'], 1, 'Two papers in 2013.', 'Mikolov and colleagues at Google.')
K.quiz('e', 'Exponentiating the dot product makes the score', ['negative', 'always positive', 'zero', 'an integer'], 1, 'exp is never negative.', 'Probabilities need positive numbers.')
K.quiz('e', 'Why take the log of the likelihood?', ['It makes the numbers larger', 'Products become sums and underflow is avoided', 'It removes the window', 'The slide forgot it'], 1, 'Transformation 1.', 'Sums are easier to differentiate and numerically safe.')
K.quiz('m', 'With window 1, "cats like milk" gives how many skip-gram pairs?', ['2', '3', '4', '6'], 2, 'cats has 1 neighbour, like 2, milk 1.', '1 + 2 + 1 = 4.')
K.quiz('m', 'The one-hot input vector times the embedding matrix gives', ['the sum of all embeddings', 'the row of the centre word', 'a probability', 'the softmax denominator'], 1, 'Lookup.', 'Only one 1, so it selects one row.')
K.quiz('m', 'CBOW predicts', ['the context from the centre', 'the centre word from the averaged context', 'the document topic', 'co-occurrence counts'], 1, 'Continuous bag of words.', 'It averages the context vectors.')
K.quiz('m', 'The two vectors per word, v and u, are', ['two meanings of the word', 'two roles: centre and outside', 'the word and its stem', 'forward and backward'], 1, 'The slide quote.', 'Not two meanings, two roles.')
K.quiz('h', 'The gradient ∂J/∂v<sub>c</sub> = −u<sub>o</sub> + ∑ P(w | c) u<sub>w</sub> is zero when', ['all vectors are zero', 'the model’s expected context vector equals the observed one', 'the learning rate is zero', 'V = 1'], 1, 'Expected minus observed.', 'At the optimum the model’s average prediction matches what is seen.')
K.quiz('h', 'Why is the naive softmax expensive?', ['It needs the sigmoid', 'The denominator sums over the whole vocabulary', 'It uses one-hot vectors', 'It needs labelled data'], 1, '100,000 terms per update.', 'Every update computes V exponentials.')
K.quiz('h', 'Why use SGD instead of full gradient descent for word2vec?', ['SGD is exact', 'The full gradient needs every window in a corpus of billions of words before one update', 'Full gradient descent diverges', 'SGD needs no learning rate'], 1, 'Slide on SGD.', 'Updating after each sample makes progress immediately.')
K.quiz('x', 'Hierarchical softmax reduces the cost per prediction to about', ['O(1)', 'O(log V)', 'O(V)', 'O(V²)'], 1, 'A binary tree.', 'One binary decision per tree level, about log₂ V levels.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Softmax of the scores (2, 1, 0): probability of the first. Four decimals.', '0.6652', 'e² ÷ (e² + e + 1).',
       ['e² = 7.389, e¹ = 2.718, e⁰ = 1.', 'Sum = 11.107.', eq('7.389 ÷ 11.107 = 0.6652')], check=0.6652409557748219, tol=5e-5)
K.calc('e', 'Five notebook sentences of three words each, window 1. How many training pairs?', '20', 'Each sentence gives 4.',
       ['Per sentence: 1 + 2 + 1 = 4 pairs.', 'Five sentences.', eq('5 × 4 = 20, as the notebook prints')], check=20, tol=1e-9)
K.calc('e', 'Practice question: V = 6,000. What is the length of the one-hot input vector?', '6000', 'One position per word.',
       ['A one-hot vector has V entries.', 'V = 6,000.', eq('6,000')], check=6000, tol=1e-9)
K.calc('m', 'Practice question: V = 10,000, d = 300, full softmax. Total parameters without biases?', '6000000', 'E is V × d and W is d × V.',
       ['E: 10,000 × 300 = 3,000,000.', 'W: 300 × 10,000 = 3,000,000.', eq('6,000,000')], check=6000000, tol=1e-9)
K.calc('m', 'In the sgstep example h = (0.2, 0.1) and u<sub>like</sub> = (0.5, −0.2). What is the score u·h?', '0.08', 'Dot product.',
       ['0.2 × 0.5 = 0.10.', '0.1 × (−0.2) = −0.02.', eq('0.08')], check=0.08, tol=1e-9)
K.calc('m', 'The four scores are 0.05, 0.08, 0.08, −0.05. What is P(like | cats)? Four decimals.', '0.2598', 'exp(0.08) ÷ sum of the four exps.',
       ['exp values: 1.05127, 1.08329, 1.08329, 0.95123.', 'Sum = 4.16908.', eq('1.08329 ÷ 4.16908 = 0.2598')], check=0.25983873089368464, tol=5e-5)
K.calc('m', 'The loss −ln P(like | cats) for that pair. Four decimals.', '1.3477', '−ln 0.2598.',
       ['P = 0.25984.', 'ln 0.25984 = −1.34769.', eq('loss = 1.3477')], check=1.347694106204539, tol=5e-5)
K.calc('h', 'An untrained model gives every one of V = 7 words the same probability. What is the loss per pair? Four decimals.', '1.9459', '−ln(1/7).',
       ['Uniform: P = 1/7.', '−ln(1/7) = ln 7.', eq('1.9459, the starting point of the notebook loss curve')], check=1.9459101490553132, tol=5e-5)
K.calc('h', 'Practice question: V = 6,000, d = 200, window 2, a sentence of 8 words. How many skip-gram pairs?', '26', 'Edge words have fewer neighbours.',
       ['Positions 1 and 8: 2 each. Positions 2 and 7: 3 each.', 'Positions 3 to 6: 4 each, 16 in total.', eq('2 + 3 + 16 + 3 + 2 = 26')], check=26, tol=1e-9)
K.calc('h', 'The notebook runs 500 epochs over 20 pairs. How many single pair updates is that?', '10000', 'Epochs × pairs.',
       ['One update per pair per epoch.', '500 × 20.', eq('10,000 updates')], check=10000, tol=1e-9)
K.calc('x', 'V = 100,000 and d = 300. How many multiplications does the naive softmax score layer need for one pair?', '30000000', 'One d long dot product per vocabulary word.',
       ['Each score u<sub>w</sub>·v<sub>c</sub> is 300 multiplications.', 'There are 100,000 words.', eq('3 × 10⁷ multiplications per pair, before any exponentials')], check=30000000, tol=1e-9)

# ---------------------------------------------------------------- assignments
K.assign('pairs', 'e', 'Generate skip-gram pairs',
         '<p>Write <code>make_pairs(sentences, window)</code> returning the list of (centre, context) word pairs in the order the notebook makes them. sentences is a list of token lists.</p>',
         '''
def make_pairs(sentences, window):
    pass
''', [('make_pairs([["cats", "like", "milk"]], 1)', [('cats', 'like'), ('like', 'cats'), ('like', 'milk'), ('milk', 'like')]), ('len(make_pairs([["a", "b", "c", "d", "e", "f", "g", "h"]], 2))', 26)],
         '''
def make_pairs(sentences, window):
    out = []
    for s in sentences:
        for i, c in enumerate(s):
            for j in range(max(0, i - window), min(len(s), i + window + 1)):
                if i != j:
                    out.append((c, s[j]))
    return out
''', 'Two nested loops and skip j = i.', '<p>The second test is the practice question with 8 words and window 2.</p>')
K.assign('softmax', 'm', 'Softmax and the skip-gram loss',
         '<p>Write <code>softmax(xs)</code> returning probabilities rounded to 4 decimals (subtract the maximum first for stability), and <code>sg_loss(h, U, o)</code> returning −ln P(o | c) rounded to 4 decimals, where h is the centre vector, U a list of output vectors and o the index of the true context word.</p>',
         '''
import math

def softmax(xs):
    pass

def sg_loss(h, U, o):
    pass
''', [('softmax([2, 1, 0])', [0.6652, 0.2447, 0.09]), ('sg_loss([0.2, 0.1], [[0.1, 0.3], [0.5, -0.2], [0.2, 0.4], [-0.3, 0.1]], 1)', 1.3477), ('softmax([1000, 1000])', [0.5, 0.5])],
         '''
import math

def softmax(xs):
    m = max(xs)
    e = [math.exp(x - m) for x in xs]
    s = sum(e)
    return [round(v / s, 4) for v in e]

def sg_loss(h, U, o):
    sc = [sum(a * b for a, b in zip(h, u)) for u in U]
    m = max(sc)
    lse = m + math.log(sum(math.exp(s - m) for s in sc))
    return round(lse - sc[o], 4)
''', 'Without subtracting the maximum, exp(1000) overflows. The third test checks that.', '<p>−log P(o | c) = log ∑ exp(s) − s<sub>o</sub>, the log sum exp form.</p>')
K.assign('sgdstep', 'h', 'One full softmax update',
         '<p>Write <code>sg_step(h, U, o, lr)</code> that does one notebook update: error = p − y, grad_h = ∑<sub>k</sub> error<sub>k</sub> U<sub>k</sub>, U<sub>k</sub> ← U<sub>k</sub> − lr · error<sub>k</sub> · h, h ← h − lr · grad_h. Use the old h when updating U. Return (new_h, new_U) with every number rounded to 4 decimals.</p>',
         '''
import math

def sg_step(h, U, o, lr):
    pass
''', [('sg_step([0.2, 0.1], [[0.1, 0.3], [0.5, -0.2], [0.2, 0.4], [-0.3, 0.1]], 1, 1.0)[0]', [0.5613, -0.2504]),
      ('sg_step([0.0, 0.0], [[1.0, 0.0], [0.0, 1.0]], 0, 0.5)', ([0.25, -0.25], [[1.0, 0.0], [0.0, 1.0]]))],
         '''
import math

def sg_step(h, U, o, lr):
    sc = [sum(a * b for a, b in zip(h, u)) for u in U]
    m = max(sc)
    e = [math.exp(s - m) for s in sc]
    p = [v / sum(e) for v in e]
    err = [p[k] - (1 if k == o else 0) for k in range(len(U))]
    gh = [sum(err[k] * U[k][a] for k in range(len(U))) for a in range(len(h))]
    newU = [[round(U[k][a] - lr * err[k] * h[a], 4) for a in range(len(h))] for k in range(len(U))]
    newh = [round(h[a] - lr * gh[a], 4) for a in range(len(h))]
    return (newh, newU)
''', 'Compute every gradient from the old values before changing anything.', '<p>The second test starts from h = 0, where every output vector gets a zero update but h moves toward the true context vector.</p>')

K.must('Word2vec idea', 'Slide a window over the text. Use the centre word to predict each outside word, and adjust the vectors to make true neighbours probable (Mikolov et al. 2013).')
K.must('Objective', 'J(θ) = −(1/T) ∑<sub>t</sub> ∑<sub>j</sub> log P(w<sub>t+j</sub> | w<sub>t</sub>): log, minus sign, average.')
K.must('Prediction', 'P(o | c) = exp(u<sub>o</sub>·v<sub>c</sub>) ÷ ∑<sub>w</sub> exp(u<sub>w</sub>·v<sub>c</sub>): dot product, exp, normalise. Two vectors per word, two roles.')
K.must('Gradient', '∂J/∂v<sub>c</sub> = −u<sub>o</sub> + ∑ P(w | c)u<sub>w</sub>, observed minus expected. Trained with SGD, one window at a time.')
K.must('Variants and size', 'Skip-gram predicts context from centre, CBOW centre from averaged context. Full softmax has 2Vd parameters: 6,000,000 for V = 10,000, d = 300.')

T = K.topic(
    slug='word2vec-skipgram', topic='nn-word2vec', step=(2, 'Word vectors', 'nn-vectors', 'Turn words into vectors that capture meaning: one-hot vectors and their limits, word2vec with softmax and negative sampling, co-occurrence counts, GloVe, and how to test and improve embeddings.', 'College'),
    title='Word2vec: skip-gram with the full softmax', short='Word2vec skip-gram', badge='2.2', minutes=45, added='2026-11-01',
    lead='Learn word vectors by predicting neighbours: the skip-gram objective, the softmax prediction, the gradient, and the class notebook trained live in your browser.',
    desc='The word2vec idea, centre and outside words, the likelihood and the three transformations to J(θ), the softmax prediction function, one-hot input as a lookup, the gradient as observed minus expected, SGD, the notebook training loop, CBOW, hierarchical softmax and parameter counts.',
    summary='Skip-gram objective, softmax prediction, gradients, SGD, the notebook, CBOW and parameter counts.',
    keywords=['word2vec', 'skip-gram', 'CBOW', 'softmax', 'objective function', 'SGD', 'notebook'],
    recap='<p>Skip-gram turns raw text into a prediction task: from each centre word, predict its neighbours with a softmax over dot products. Gradient descent on the negative log likelihood pulls words with shared contexts together, and their centre vectors become the word embeddings.</p>')
