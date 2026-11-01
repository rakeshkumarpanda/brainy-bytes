# NLP section, chapter 2.3: skip-gram with negative sampling. Source: FoVL lecture 2 slides 21 to 29 (the cost of
# the normalisation term, binary logistic regressions for a true pair against noise pairs, the "The cat sat on the mat"
# example with apple, car and quickly as negatives, the objective of Mikolov et al. 2013 "Distributed Representations
# of Words and Phrases", sigmoid instead of softmax, the unigram distribution U(w) raised to 3/4), the class notebook
# Negative_samples.ipynb (K = 3, counts ** 0.75) and the lecture 5 question on sigmoid computations (answer 44).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from nlpkit import listing

K = Kit()

K.code('dist', r'''
# The negative sampling distribution of the notebook: counts ** 0.75, normalised
counts = {"balls": 2, "cats": 3, "chase": 2, "dogs": 2, "drink": 1, "like": 2, "milk": 3}
total = sum(counts.values())
powered = {w: c ** 0.75 for w, c in counts.items()}
Z = sum(powered.values())
for w in counts:
    print(w.ljust(6), "U =", round(counts[w] / total, 4), " Pn =", round(powered[w] / Z, 4))
''')

K.code('loss', r'''
# Negative sampling loss for one true pair and three noise words
import math
sig = lambda x: 1 / (1 + math.exp(-x))
pos = 1.0                      # u_o . v_c for the true context word
negs = [0.5, -1.0, 2.0]        # u_k . v_c for K = 3 noise words

J = -math.log(sig(pos))
for s in negs:
    J += -math.log(sig(-s))
print("terms:", round(-math.log(sig(pos)), 4), [round(-math.log(sig(-s)), 4) for s in negs])
print("J_neg =", round(J, 4))
''')

NB = '''
counts = np.zeros(V)
for sentence in sentences:
    for word in sentence:
        counts[word_to_id[word]] += 1
neg_probs = counts ** 0.75                     # standard word2vec sampling distribution
neg_probs = neg_probs / neg_probs.sum()

def sample_negatives(context, K):
    negatives = []
    while len(negatives) < K:
        w = np.random.choice(V, p=neg_probs)
        if w != context:                       # never use the true context word as noise
            negatives.append(w)
    return negatives

for epoch in range(epochs):
    for center, context in pairs:
        h = E[center]
        targets = [context] + sample_negatives(context, K)
        labels = [1] + [0] * K
        for t, label in zip(targets, labels):
            score = sigmoid(h @ W[t])
            g = score - label                  # sigmoid output minus label
            grad_h += g * W[t]
            W[t] -= learning_rate * g * h
        E[center] -= learning_rate * grad_h
'''
NB_OUT = '''Number of positive pairs: 20
Learned word embeddings:
balls [ 4.543 -1.73   0.464]
cats [ 0.719 -1.73   0.492]
chase [1.838 1.247 1.484]
dogs [ 1.724 -2.477  0.866]
drink [-0.401  0.347  2.883]
like [-0.332  0.468  2.046]
milk [-0.123 -3.174  1.823]
Words similar to cats: [('dogs', 0.979), ('milk', 0.888), ('balls', 0.686)]
Words similar to dogs: [('cats', 0.979), ('balls', 0.817), ('milk', 0.803)]'''

K.lesson('why', 'The expensive denominator', f'''
<p>The softmax of chapter 2.2 divides by a sum over every word of the vocabulary, maybe 100,000 words. Every single update pays for 100,000 dot products and exponentials. That is far too slow. Standard word2vec therefore trains skip-gram with negative sampling instead.</p>
{fxs(fx('The costly part', 'P(o | c) = ' + frac('exp(u<sub>o</sub>·v<sub>c</sub>)', '∑<sub>w ∈ V</sub> exp(u<sub>w</sub>·v<sub>c</sub>)'), 'The denominator sums over all words in the vocabulary.'))}
<p>The main idea is to train binary logistic regressions. One classifier step asks "is this a real pair seen in the text?" for the true pair (centre, context), and several noise pairs (the centre word with random words) are asked the same question with the answer no.</p>
{table(['Pair', 'Label', 'Training pushes'], [['(cat, sat)', 'real, 1', 'cat and sat closer'], ['(cat, the)', 'real, 1', 'closer'], ['(cat, apple)', 'noise, 0', 'cat and apple apart'], ['(cat, car)', 'noise, 0', 'apart'], ['(cat, quickly)', 'noise, 0', 'apart']])}
{scene('learning to spot a friend in a crowd', '<p>To learn your best friend’s face you do not need to compare it with every person on Earth. A few random strangers at a time are enough: "this is my friend, those are not". Negative sampling teaches the model the same way, with a handful of random words instead of the whole vocabulary.</p>')}
''', kw=['negative sampling', 'softmax cost', 'binary classification', 'noise pairs', 'logistic regression'])

K.lesson('objective', 'The negative sampling objective', f'''
<p>Mikolov and others (2013) replace the softmax with sigmoids. For a true pair we want σ(u<sub>o</sub>·v<sub>c</sub>) close to 1. For each of K noise words drawn from a distribution P<sub>n</sub> we want σ(u<sub>k</sub>·v<sub>c</sub>) close to 0, which is the same as σ(−u<sub>k</sub>·v<sub>c</sub>) close to 1.</p>
{fxs(fx('Loss for one pair', 'J<sub>neg</sub>(o, v<sub>c</sub>, U) = −log σ(u<sub>o</sub>·v<sub>c</sub>) − ∑<sub>k=1</sub><sup>K</sup> log σ(−u<sub>k</sub>·v<sub>c</sub>)', 'First term: make the real pair likely. Second: make each noise pair unlikely.', key=True),
     fx('Symmetry of the sigmoid', 'σ(−x) = 1 − σ(x)', 'So log σ(−u<sub>k</sub>·v<sub>c</sub>) = log(1 − σ(u<sub>k</sub>·v<sub>c</sub>)).'),
     fx('Gradients', frac('∂J', '∂v<sub>c</sub>') + ' = (σ(u<sub>o</sub>·v<sub>c</sub>) − 1)u<sub>o</sub> + ∑<sub>k</sub> σ(u<sub>k</sub>·v<sub>c</sub>)u<sub>k</sub>, &nbsp; ' + frac('∂J', '∂u<sub>k</sub>') + ' = σ(u<sub>k</sub>·v<sub>c</sub>)v<sub>c</sub>', 'Each term is (prediction − label) × the other vector. Only 1 + K output vectors change.', key=True))}
{viz('sgns')}
{code('loss')}
{steps('Lecture 5 question: how many sigmoids per centre word?', [
    'Window 2 on each side, the full window used: 4 context words.',
    'For each context word: 1 positive pair and K = 10 negative pairs, so 11 sigmoids.',
    'A student answered 11 at first. That counts one context word only.',
    eq('11 × 4 = 44 sigmoid computations for one centre word occurrence')])}
{note('Count positives and negatives per context word, then multiply by the number of context words. Read whether the question gives K per pair or per centre word.', 'exam')}
''', kw=['objective', 'sigmoid', 'J_neg', 'gradient', 'K negatives', '44 sigmoids'])

K.lesson('sampling', 'Which words to use as noise: U(w) to the 3/4', f'''
<p>U(w) is the unigram distribution, how often each word appears in the corpus. Sampling negatives straight from U(w) would mostly pick "the" and "of". Those words appear in almost every context, so they teach the model little. Raising U(w) to the power 3/4 reshapes the distribution: common words drop a little and rare words rise.</p>
{fxs(fx('Noise distribution', 'P<sub>n</sub>(w) = ' + frac('U(w)<sup>3/4</sup>', '∑<sub>w′</sub> U(w′)<sup>3/4</sup>'), 'α = 3/4 was found to work best. α = 1 is the raw unigram, α = 0 is uniform.', key=True))}
{viz('negsample')}
{code('dist')}
{table(['Word', 'Count', 'U(w)', 'P<sub>n</sub>(w)'], [['the', '1000', '0.6002', '0.5409'], ['of', '600', '0.3601', '0.3687'], ['bank', '40', '0.0240', '0.0484'], ['river', '20', '0.0120', '0.0288'], ['skillet', '5', '0.0030', '0.0102'], ['aardvark', '1', '0.0006', '0.0030']])}
{deep('what negative sampling really optimises', '<p>Negative sampling is a simplified form of noise contrastive estimation. NCE would recover the true softmax probabilities, while negative sampling drops the correction term and only learns good vectors. Levy and Goldberg (2014) showed that at its optimum u<sub>o</sub>·v<sub>c</sub> = PMI(o, c) − log K, so the dot product estimates how much more often the two words co-occur than chance, shifted by log K. The 3/4 power smooths the PMI, which reduces its well known bias toward rare words.</p>')}
''', kw=['unigram distribution', 'noise distribution', 'power 3/4', 'sampling', 'PMI'])

K.lesson('notebook', 'The negative sampling notebook', f'''
<p>The second notebook keeps the five sentences, window 1, d = 3, η = 0.05 and 500 epochs, and adds K = 3 negatives per positive pair drawn from counts<sup>0.75</sup>. It never uses the true context word as noise. With this objective cats and dogs become the closest pair, cosine 0.98, because they share like, chase and milk contexts.</p>
{listing(NB, NB_OUT, title='Negative_samples.ipynb, the sampling and training cells (plotting trimmed)', cap='Output recorded in the class notebook')}
{viz('w2vtrain', mode='neg')}
{table(['Notebook run', 'Nearest to cats', 'Nearest to dogs'], [['Full softmax', 'milk 0.577, dogs 0.483', 'balls 0.634, cats 0.483'], ['Negative sampling, K = 3', 'dogs 0.979, milk 0.888', 'cats 0.979, balls 0.817']])}
{ladder(
    '<p>Instead of comparing a word with every other word, we compare it with its real neighbour and a few random words. That is much faster and still teaches which words belong together.</p>',
    '<p>Each positive pair becomes 1 + K logistic regression examples. The cost per pair drops from V dot products to K + 1, so training scales to billions of words.</p>',
    '<p>The class question "should the clusters be the same with and without negative sampling?" has the answer no in general. The two objectives have different optima: softmax models P(o | c), negative sampling models shifted PMI, and a tiny corpus with random initialisation amplifies the difference.</p>',
    '<p>Contrastive learning with sampled negatives is now everywhere: sentence embeddings, CLIP for images and text, retrieval models. The choice of negatives (random, in batch, hard negatives) is a research topic of its own.</p>')}
{note('Stop words such as "the" are still used as positive pairs when they appear in the window. They are only down weighted as negatives. This was asked in class.', 'tip')}
''', kw=['notebook', 'K = 3', 'cosine', 'cats and dogs', 'contrastive learning'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Negative sampling replaces the softmax with', ['ReLU', 'sigmoids', 'tanh', 'a decision tree'], 1, 'Binary decisions.', 'Each pair is a yes or no question answered by a sigmoid.')
K.quiz('e', 'A negative sample is', ['a word with a negative vector', 'the centre word paired with a random word', 'a misspelled word', 'a stop word removed from the text'], 1, 'Noise pair.', 'A random word that is not the true context.')
K.quiz('e', 'For a true pair the model wants σ(u<sub>o</sub>·v<sub>c</sub>) to be close to', ['0', '0.5', '1', '−1'], 2, 'Label 1.', 'Real pairs should look real.')
K.quiz('e', 'The power used on the unigram distribution in word2vec is', ['1/2', '3/4', '1', '2'], 1, 'Notebook: counts ** 0.75.', 'α = 0.75.')
K.quiz('m', 'Why not sample negatives from the raw unigram distribution?', ['It is not normalised', 'It mostly picks very frequent words like "the", which are not informative', 'It never picks frequent words', 'It is too slow to compute'], 1, 'Slide 29.', 'Frequent words appear everywhere and teach little.')
K.quiz('m', 'σ(−x) equals', ['−σ(x)', '1 − σ(x)', 'σ(x)²', '1 ÷ σ(x)'], 1, 'Symmetry.', 'That is why the noise term uses σ(−u<sub>k</sub>·v<sub>c</sub>).')
K.quiz('m', 'With K negatives, how many output vectors change per pair?', ['1', 'K', 'K + 1', 'V'], 2, 'The true one plus the noise.', 'Only the vectors that appear in the loss get gradients.')
K.quiz('m', 'Raising α from 0.75 to 1 makes rare words', ['more likely as negatives', 'less likely as negatives', 'impossible', 'unchanged'], 1, 'α = 1 is the raw distribution.', 'The 0.75 power lifted them, α = 1 removes the lift.')
K.quiz('h', 'Lecture 5: window 2, K = 10, full window. Sigmoids per centre word occurrence?', ['11', '14', '40', '44'], 3, 'Per context word: 1 + K.', '(1 + 10) × 4 = 44.')
K.quiz('h', 'In the notebook, cats and dogs became nearest neighbours only with negative sampling. The best explanation is', ['a bug in the softmax run', 'the two objectives have different optima and the corpus is tiny', 'negative sampling always clusters animals', 'the seed was different'], 1, 'Same data, different loss.', 'Softmax models probabilities, negative sampling models shifted PMI.')
K.quiz('h', 'The gradient of J<sub>neg</sub> for a noise vector u<sub>k</sub> is', ['−v<sub>c</sub>', 'σ(u<sub>k</sub>·v<sub>c</sub>) v<sub>c</sub>', '(σ − 1) u<sub>k</sub>', '0'], 1, 'Prediction minus label 0.', 'd/du<sub>k</sub> of −log σ(−u<sub>k</sub>·v<sub>c</sub>) = σ(u<sub>k</sub>·v<sub>c</sub>)v<sub>c</sub>.')
K.quiz('x', 'At its optimum, skip-gram with negative sampling makes u<sub>o</sub>·v<sub>c</sub> equal', ['log P(o)', 'PMI(o, c) − log K', 'the co-occurrence count', '0'], 1, 'Levy and Goldberg 2014.', 'The dot product estimates shifted pointwise mutual information.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Window 2 (4 context words) and K = 10. How many sigmoid computations per centre word?', '44', '(1 + K) per context word.',
       ['Per context word: 1 positive + 10 negative = 11.', '4 context words.', eq('11 × 4 = 44')], check=44, tol=1e-9)
K.calc('e', 'σ(1) to four decimals.', '0.7311', '1 ÷ (1 + e<sup>−1</sup>).',
       ['e<sup>−1</sup> = 0.36788.', '1 ÷ 1.36788.', eq('0.7311')], check=0.7310585786300049, tol=5e-5)
K.calc('e', 'The notebook corpus has 15 tokens and "drink" appears once. What is U(drink)? Four decimals.', '0.0667', 'count ÷ total.',
       ['count = 1.', 'total = 15.', eq('1 ÷ 15 = 0.0667')], check=1 / 15, tol=5e-5)
K.calc('m', 'With counts^0.75 on the notebook counts (2, 3, 2, 2, 1, 2, 3), what is P<sub>n</sub>(drink)? Four decimals.', '0.0814', '1 ÷ ∑ c^0.75.',
       ['2<sup>0.75</sup> = 1.6818 (four words), 3<sup>0.75</sup> = 2.2795 (two words), 1<sup>0.75</sup> = 1.', 'Sum = 4 × 1.6818 + 2 × 2.2795 + 1 = 12.286.', eq('1 ÷ 12.286 = 0.0814')], check=0.0814, tol=5e-5)
K.calc('m', 'True score 1.0 and noise scores 0.5, −1, 2. What is J<sub>neg</sub>? Four decimals.', '3.7275', 'Sum −log σ(pos) and −log σ(−neg).',
       ['−log σ(1) = 0.3133.', 'Noise terms: −log σ(−0.5) = 0.9741, −log σ(1) = 0.3133, −log σ(−2) = 2.1269.', eq('J = 0.3133 + 0.9741 + 0.3133 + 2.1269 = 3.7275')], check=3.7275283702595248, tol=5e-4)
K.calc('m', 'A well trained pair: true score 4, three noise scores −3. J<sub>neg</sub>? Four decimals.', '0.1639', '−log σ(4) − 3 log σ(3).',
       ['σ(4) = 0.98201, −ln = 0.01815.', 'σ(3) = 0.95257, −ln = 0.04859, three times 0.14577.', eq('J = 0.1639')], check=0.16391198263903545, tol=5e-4)
K.calc('m', 'Notebook: 20 positive pairs and K = 3. How many noise pairs per epoch?', '60', 'K per positive pair.',
       ['Each positive pair draws 3 negatives.', '20 pairs.', eq('60 noise pairs, 80 sigmoid terms in total')], check=60, tol=1e-9)
K.calc('h', 'v<sub>c</sub> = (1, 0), u<sub>o</sub> = (1, 1), noise u₁ = (0, 1), u₂ = (−1, 0). First component of ∂J/∂v<sub>c</sub>. Four decimals.', '-0.5379', '(σ(u<sub>o</sub>·v<sub>c</sub>) − 1)u<sub>o</sub> + ∑ σ(u<sub>k</sub>·v<sub>c</sub>)u<sub>k</sub>.',
       ['Scores: u<sub>o</sub>·v<sub>c</sub> = 1, u₁·v<sub>c</sub> = 0, u₂·v<sub>c</sub> = −1.', 'σ values 0.7311, 0.5, 0.2689.', eq('(0.7311 − 1) × 1 + 0.5 × 0 + 0.2689 × (−1) = −0.5379')], check=-0.5378828427399902, tol=5e-5)
K.calc('h', 'Same setup, second component of ∂J/∂v<sub>c</sub>. Four decimals.', '0.2311', 'Use the second coordinates.',
       ['(0.7311 − 1) × 1 = −0.2689.', '0.5 × 1 = 0.5, 0.2689 × 0 = 0.', eq('−0.2689 + 0.5 = 0.2311')], check=0.2310585786300049, tol=5e-5)
K.calc('h', 'V = 100,000 and K = 5. How many times fewer output scores per pair than the full softmax? Whole number.', '16667', 'V ÷ (K + 1).',
       ['Full softmax: 100,000 scores.', 'Negative sampling: 1 + 5 = 6 scores.', eq('100,000 ÷ 6 ≈ 16,667')], check=100000 / 6, tol=0.5)
K.calc('x', 'Counts the = 1000, aardvark = 1 (plus others). How much bigger is the ratio P<sub>n</sub>(aardvark) ÷ P<sub>n</sub>(the) than U(aardvark) ÷ U(the)? One decimal.', '5.6', 'Compare 1000<sup>−0.75</sup> with 1000<sup>−1</sup>.',
       ['Raw ratio 1 ÷ 1000.', 'Powered ratio 1 ÷ 1000<sup>0.75</sup> = 1 ÷ 177.8.', eq('1000 ÷ 177.8 = 1000<sup>0.25</sup> = 5.6 times more chance for the rare word')], check=1000 ** 0.25, tol=0.06)

# ---------------------------------------------------------------- assignments
K.assign('pn', 'e', 'The noise distribution',
         '<p>Write <code>noise_dist(counts, alpha)</code> where counts is a dict from word to count. Return a dict from word to P<sub>n</sub>(w) = c<sup>α</sup> ÷ ∑ c<sup>α</sup>, rounded to 4 decimals.</p>',
         '''
def noise_dist(counts, alpha):
    pass
''', [('noise_dist({"a": 1, "b": 1}, 0.75)', {'a': 0.5, 'b': 0.5}), ('noise_dist({"the": 3, "cat": 1}, 1)', {'the': 0.75, 'cat': 0.25}), ('noise_dist({"balls": 2, "cats": 3, "chase": 2, "dogs": 2, "drink": 1, "like": 2, "milk": 3}, 0.75)["drink"]', 0.0814)],
         '''
def noise_dist(counts, alpha):
    p = {w: c ** alpha for w, c in counts.items()}
    s = sum(p.values())
    return {w: round(v / s, 4) for w, v in p.items()}
''', 'Raise, sum, divide.', '<p>The third test is the notebook vocabulary.</p>')
K.assign('jneg', 'm', 'The negative sampling loss',
         '<p>Write <code>j_neg(vc, uo, negs)</code> where vc and uo are vectors and negs a list of noise vectors. Return −log σ(u<sub>o</sub>·v<sub>c</sub>) − ∑ log σ(−u<sub>k</sub>·v<sub>c</sub>), rounded to 4 decimals. Also write <code>n_sigmoids(window, K)</code> for the number of sigmoids per centre word with the full window.</p>',
         '''
import math

def j_neg(vc, uo, negs):
    pass

def n_sigmoids(window, K):
    pass
''', [('j_neg([1, 0], [1, 1], [[0, 1], [-1, 0]])', 1.3197), ('n_sigmoids(2, 10)', 44), ('j_neg([0, 0], [1, 1], [])', 0.6931)],
         '''
import math

def j_neg(vc, uo, negs):
    sig = lambda x: 1 / (1 + math.exp(-x))
    d = lambda a, b: sum(x * y for x, y in zip(a, b))
    J = -math.log(sig(d(uo, vc)))
    for u in negs:
        J -= math.log(sig(-d(u, vc)))
    return round(J, 4)

def n_sigmoids(window, K):
    return 2 * window * (1 + K)
''', 'With v<sub>c</sub> = 0 every sigmoid is 0.5, so each term is ln 2 = 0.6931.', '<p>The first test: −ln σ(1) − ln σ(0) − ln σ(1) = 0.3133 + 0.6931 + 0.3133 = 1.3197.</p>')
K.assign('sgnsstep', 'h', 'One negative sampling update',
         '<p>Write <code>ns_step(vc, uo, negs, lr)</code> that computes the gradients of J<sub>neg</sub> at the old values and returns (new_vc, new_uo, new_negs), every number rounded to 4 decimals.</p>',
         '''
import math

def ns_step(vc, uo, negs, lr):
    pass
''', [('ns_step([1, 0], [1, 1], [[0, 1], [-1, 0]], 1.0)[0]', [1.5379, -0.2311]), ('ns_step([1, 0], [1, 1], [[0, 1], [-1, 0]], 1.0)[1]', [1.2689, 1.0])],
         '''
import math

def ns_step(vc, uo, negs, lr):
    sig = lambda x: 1 / (1 + math.exp(-x))
    d = lambda a, b: sum(x * y for x, y in zip(a, b))
    go = sig(d(uo, vc)) - 1
    gvc = [go * u for u in uo]
    newnegs = []
    for u in negs:
        gk = sig(d(u, vc))
        gvc = [g + gk * x for g, x in zip(gvc, u)]
        newnegs.append([round(x - lr * gk * c, 4) for x, c in zip(u, vc)])
    newuo = [round(x - lr * go * c, 4) for x, c in zip(uo, vc)]
    newvc = [round(c - lr * g, 4) for c, g in zip(vc, gvc)]
    return (newvc, newuo, newnegs)
''', 'Every gradient is (prediction − label) times the other vector.', '<p>The centre vector moves toward u<sub>o</sub> and away from the noise vectors.</p>')

K.must('Why', 'The softmax denominator sums over the whole vocabulary. Negative sampling replaces it with 1 + K binary logistic regressions.')
K.must('Objective', 'J<sub>neg</sub> = −log σ(u<sub>o</sub>·v<sub>c</sub>) − ∑<sub>k</sub> log σ(−u<sub>k</sub>·v<sub>c</sub>), σ(−x) = 1 − σ(x).')
K.must('Noise distribution', 'P<sub>n</sub>(w) ∝ U(w)<sup>3/4</sup>: frequent words like "the" drop, rare words rise. The true context is never used as noise.')
K.must('Counting question', 'Sigmoids per centre word = (1 + K) × number of context words: window 2, K = 10 gives 44.')
K.must('Notebook', 'K = 3, counts<sup>0.75</sup>, 500 epochs: cats and dogs become nearest neighbours (cosine 0.98). Optimum: u·v = PMI − log K.')

T = K.topic(
    slug='negative-sampling', topic='nn-negative-sampling', step=(2, 'Word vectors', 'nn-vectors', 'Turn words into vectors that capture meaning: one-hot vectors and their limits, word2vec with softmax and negative sampling, co-occurrence counts, GloVe, and how to test and improve embeddings.', 'College'),
    title='Skip-gram with negative sampling', short='Negative sampling', badge='2.3', minutes=40, added='2026-11-01',
    lead='Skip the expensive softmax: score the true pair against a few random noise words with sigmoids, pick the noise with U(w) to the 3/4, and rerun the class notebook.',
    desc='Why the softmax denominator is too costly, binary logistic regressions on true and noise pairs, the J_neg objective and its gradients, the unigram distribution to the power 3/4, the 44 sigmoid question, the negative sampling notebook and the shifted PMI view.',
    summary='Negative sampling objective, gradients, the 3/4 noise distribution, sigmoid counting and the notebook.',
    keywords=['negative sampling', 'SGNS', 'sigmoid', 'noise distribution', 'unigram 3/4', 'PMI', 'notebook'],
    recap='<p>Negative sampling turns one expensive softmax into a few cheap yes or no questions: is this pair real, or is it noise drawn from U(w) to the 3/4? Only 1 + K output vectors change per pair, so word2vec scales to billions of words.</p>')
