# NLP section, chapter 2.4: count based word vectors and GloVe. Source: FoVL lecture 2 slides 30 to 44 (why not count
# co-occurrences directly, window against document matrices, the window 1 matrix for "I like deep learning / I like NLP /
# I enjoy flying", SVD of X and the COALS hacks of Rohde et al. 2005, GloVe of Pennington et al. 2014 with the ice and
# steam probability ratios, the nine implementation steps, the weighting function and the algorithm box with 1 / distance
# counts and W = w + w_tilde) and the GloVe cell of the class notebook word2vec_1.ipynb (window 2, d = 20, x_max = 10,
# alpha = 0.75, Adagrad with lr 0.03, 300 epochs).
from cvkit import Kit, fx, fxs, frac, mat, ladder, scene, note, deep, table, steps, code, viz, eq
from nlpkit import listing

K = Kit()

K.code('slide', r'''
# The window 1 co-occurrence matrix of the lecture slide
corpus = ["I like deep learning .", "I like NLP .", "I enjoy flying ."]
vocab = ["I", "like", "enjoy", "deep", "learning", "NLP", "flying", "."]
X = {a: {b: 0 for b in vocab} for a in vocab}
for line in corpus:
    w = line.split()
    for i in range(len(w) - 1):
        X[w[i]][w[i + 1]] += 1      # right neighbour
        X[w[i + 1]][w[i]] += 1      # symmetric: left neighbour too
for a in vocab:
    print(a.ljust(9), [X[a][b] for b in vocab])
''')

K.code('weight', r'''
# The GloVe weighting function f(x) for the paper and the notebook settings
def f(x, x_max, alpha):
    if x == 0:
        return 0.0
    return (x / x_max) ** alpha if x < x_max else 1.0

for x in [0, 0.5, 1, 2, 5, 10, 20, 100, 500]:
    print("x =", str(x).ljust(4), " paper f =", round(f(x, 100, 0.75), 4), " notebook f =", round(f(x, 10, 0.75), 4))
''')

K.code('svd', r'''
# Top singular value of a 2 x 2 count matrix by power iteration on X^T X
X = [[3, 0], [4, 5]]
A = [[sum(X[k][i] * X[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
print("X^T X =", A)
v = [1.0, 0.0]
for step in range(8):
    w = [A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]]
    n = (w[0] ** 2 + w[1] ** 2) ** 0.5
    v = [w[0] / n, w[1] / n]
lam = v[0] * (A[0][0] * v[0] + A[0][1] * v[1]) + v[1] * (A[1][0] * v[0] + A[1][1] * v[1])
print("top eigenvalue of X^T X =", round(lam, 4))
print("sigma_1 =", round(lam ** 0.5, 4), " direction v1 =", [round(t, 4) for t in v])
''')

SLIDE = [['I', '0', '2', '1', '0', '0', '0', '0', '0'],
         ['like', '2', '0', '0', '1', '0', '1', '0', '0'],
         ['enjoy', '1', '0', '0', '0', '0', '0', '1', '0'],
         ['deep', '0', '1', '0', '0', '1', '0', '0', '0'],
         ['learning', '0', '0', '0', '1', '0', '0', '0', '1'],
         ['NLP', '0', '1', '0', '0', '0', '0', '0', '1'],
         ['flying', '0', '0', '1', '0', '0', '0', '0', '1'],
         ['.', '0', '0', '0', '0', '1', '1', '1', '0']]

NB = '''
window_size = 2
cooccurrence = defaultdict(float)
for sentence in sentences:
    for i, target_word in enumerate(sentence):
        target_id = word_to_id[target_word]
        start = max(0, i - window_size)
        end = min(len(sentence), i + window_size + 1)
        for j in range(start, end):
            if i == j:
                continue
            context_id = word_to_id[sentence[j]]
            distance = abs(i - j)
            cooccurrence[(target_id, context_id)] += 1.0 / distance   # closer words weigh more

log_counts = torch.log(counts)
embedding_dim, epochs, learning_rate = 20, 300, 0.03
x_max, alpha = 10.0, 0.75
weights = torch.where(counts < x_max, (counts / x_max) ** alpha, torch.ones_like(counts))

for epoch in range(epochs):
    predictions = model(target_ids, context_ids)       # w_i . w~_j + b_i + b~_j
    loss = (weights * (predictions - log_counts) ** 2).mean()
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()                                   # Adagrad

embeddings = (model.target_embeddings.weight + model.context_embeddings.weight).cpu().numpy()
'''
NB_OUT = '''Vocabulary size: 21
Number of observed pairs: 80
Epoch  50/300, Loss = 0.000000
Epoch 300/300, Loss = 0.000000
Embedding matrix shape: (21, 20)
Cosine similarities:
ice vs water: -0.7507
ice vs steam: 0.3048
cats vs dogs: 0.7455
Words similar to 'cats':
[('dogs', 0.7455), ('like', 0.7217), ('is', 0.3452), ('melts', 0.3105), ('steam', 0.2303)]
Prediction inspection:
Target word: ice
Context word: water
Observed co-occurrence count: 0.5
Predicted log count: -0.6931'''

K.lesson('counts', 'Count the neighbours directly', f'''
<p>Word2vec walks through the corpus again and again, one window at a time. A simpler question from the lecture: why not walk through the corpus once and write down how often every pair of words appears near each other? The result is a co-occurrence matrix X. Row i belongs to word i, column j to word j, and X<sub>ij</sub> counts how often j appears within the window of i.</p>
{fxs(fx('Window co-occurrence', 'X<sub>ij</sub> = number of times word j appears within m words of word i', 'A symmetric window counts left and right neighbours. Window 1 on the slide, 5 to 10 is more common.', key=True),
     fx('Word vector by counting', 'vector(i) = row i of X', 'Its length is the vocabulary size V, so the vector grows with the vocabulary.'))}
<p>There are two kinds of matrix. A window matrix counts nearby words, like word2vec, and captures both syntax and meaning (word space). A word by document matrix counts which documents a word appears in. That gives general topics, for example all sports words get similar rows, and leads to Latent Semantic Analysis (document space).</p>
<p>The slide corpus is "I like deep learning .", "I like NLP ." and "I enjoy flying ." with window 1 and a symmetric count.</p>
{table(['', 'I', 'like', 'enjoy', 'deep', 'learning', 'NLP', 'flying', '.'], SLIDE)}
{viz('cooc')}
{code('slide')}
{steps('Read one row of the slide matrix: the row "like"', [
    '"like" appears in sentence 1 between I and deep, and in sentence 2 between I and NLP.',
    'Left neighbours: I twice. Right neighbours: deep once, NLP once.',
    eq('row(like) = (I 2, like 0, enjoy 0, deep 1, learning 0, NLP 1, flying 0, . 0)'),
    'Rows "like" and "enjoy" share the column I, so the two verbs already look a little alike.'])}
<p>Raw count vectors have three problems. They are as long as the vocabulary, so they need a lot of storage. They are sparse, most cells are 0, so classifiers built on them are less robust. And frequent function words such as "the" and "has" dominate the counts. The cure is to keep the important information in a small dense vector of 25 to 1000 numbers.</p>
{scene('a supermarket learning what is bought together', '<p>A supermarket can keep a table of every pair of products that appear on the same receipt. Bread and butter get a high count, bread and engine oil a low one. Two products with similar rows, such as two brands of butter, play the same role for shoppers. That table is a co-occurrence matrix, and the rows are product vectors.</p>')}
''', kw=['co-occurrence matrix', 'window', 'word-document matrix', 'LSA', 'sparse vectors'])

K.lesson('svd', 'Shrink the matrix with SVD', f'''
<p>The classic way to get short dense vectors from X is the Singular Value Decomposition. Every matrix can be written as a rotation, a stretch along a few axes and another rotation. Keeping only the k biggest stretches gives the best possible rank k copy of X, and the first k columns of U become k-dimensional word vectors.</p>
{fxs(fx('SVD', 'X = U Σ V<sup>T</sup>', 'U and V are orthonormal: unit columns at right angles. Σ is diagonal with singular values σ₁ ≥ σ₂ ≥ ... ≥ 0.', key=True),
     fx('Truncated SVD', 'X<sub>k</sub> = U<sub>k</sub> Σ<sub>k</sub> V<sub>k</sub><sup>T</sup>', 'Keep the top k singular values. Word i gets the vector row i of U<sub>k</sub>Σ<sub>k</sub>.', key=True),
     fx('Singular values', 'σ<sub>i</sub> = √λ<sub>i</sub>(X<sup>T</sup>X)', 'The square roots of the eigenvalues of X<sup>T</sup>X.'),
     fx('Kept energy', frac('σ₁² + ... + σ<sub>k</sub>²', '∑ σ<sub>i</sub>²'), 'The share of the squared size of X that the rank k copy keeps.'))}
{steps('A 2 × 2 example by hand', [
    'X = ' + mat([['3', '0'], ['4', '5']]) + '. Then X<sup>T</sup>X = ' + mat([['25', '20'], ['20', '25']]) + '.',
    'Eigenvalues of X<sup>T</sup>X: 25 + 20 = 45 and 25 − 20 = 5, with directions (1, 1) and (1, −1).',
    eq('σ₁ = √45 = 6.708, σ₂ = √5 = 2.236'),
    'Rank 1 keeps 45 ÷ (45 + 5) = 90 percent of the energy, so one number per row already describes most of X.'])}
{code('svd')}
<p>The lecture warns that SVD on raw counts does not work well. Function words are too frequent, so syntax has too much influence. Rohde and others (2005, COALS) used several fixes.</p>
{table(['Fix', 'What it does'], [['log of the counts', 'squeezes 1000 and 10 into 6.9 and 2.3'], ['min(X, t) with t ≈ 100', 'caps very frequent pairs'], ['ignore function words', 'drops the, he, has from the counts'], ['ramped windows', 'closer words count more than far ones'], ['Pearson correlation, negatives set to 0', 'measures association instead of raw frequency']])}
{note('SVD costs about O(V³) time for a V × V matrix and must be redone when new words arrive. That is one reason prediction based methods such as word2vec took over, and GloVe tries to combine the two.', 'warn')}
{deep('why truncated SVD is the best low rank copy', '<p>The Eckart and Young theorem says that X<sub>k</sub> minimises the Frobenius error ‖X − A‖ over every matrix A of rank k, and the error left over is √(σ<sub>k+1</sub>² + ... ). Levy and Goldberg (2014) showed that skip-gram with negative sampling implicitly factorises a shifted PMI matrix, so SVD of a PMI matrix and word2vec are close relatives.</p>')}
''', kw=['SVD', 'singular values', 'truncated SVD', 'COALS', 'log counts', 'Eckart-Young'])

K.lesson('ratios', 'GloVe: meaning lives in probability ratios', f'''
<p>GloVe (Pennington, Socher and Manning, 2014) is a matrix factorisation method motivated by ratios of probabilities. First turn counts into probabilities: P(k | i) = X<sub>ik</sub> ÷ X<sub>i</sub>, where X<sub>i</sub> = ∑<sub>k</sub> X<sub>ik</sub> is the total count of row i.</p>
{table(['Probe word k', 'P(k | ice)', 'P(k | steam)', 'Ratio'], [['solid', '1.9 × 10<sup>−4</sup>', '2.2 × 10<sup>−5</sup>', '8.9'], ['gas', '6.6 × 10<sup>−5</sup>', '7.8 × 10<sup>−4</sup>', '8.5 × 10<sup>−2</sup>'], ['water', '3.0 × 10<sup>−3</sup>', '2.2 × 10<sup>−3</sup>', '1.36'], ['fashion', '1.7 × 10<sup>−5</sup>', '1.8 × 10<sup>−5</sup>', '0.96']])}
<p>A single probability says little, because water is common near both words. The ratio is what separates them. Much bigger than 1 means k belongs with ice, much smaller than 1 means k belongs with steam, and close to 1 means k does not help tell them apart.</p>
{viz('glove')}
{steps('From the ratio to the GloVe model', [
    'Goal: a function of word vectors that gives the ratio, F(w<sub>i</sub>, w<sub>j</sub>, w̃<sub>k</sub>) = P(k | i) ÷ P(k | j).',
    'Vectors are linear spaces, so use the difference and a dot product: F((w<sub>i</sub> − w<sub>j</sub>)·w̃<sub>k</sub>).',
    'A ratio should turn into a difference. Choose F = exp, then w<sub>i</sub>·w̃<sub>k</sub> = log P(k | i) = log X<sub>ik</sub> − log X<sub>i</sub>.',
    'log X<sub>i</sub> does not depend on k, so it becomes a bias b<sub>i</sub>. Add b̃<sub>k</sub> to keep i and k symmetric.',
    eq('w<sub>i</sub>·w̃<sub>k</sub> + b<sub>i</sub> + b̃<sub>k</sub> = log X<sub>ik</sub>')])}
{fxs(fx('GloVe model equation', 'w<sub>i</sub>·w̃<sub>j</sub> + b<sub>i</sub> + b̃<sub>j</sub> ≈ log X<sub>ij</sub>', 'Each word has a word vector w, a context vector w̃ and two biases.', key=True),
     fx('Ratio in vector form', '(w<sub>i</sub> − w<sub>j</sub>)·w̃<sub>k</sub> = log ' + frac('P(k | i)', 'P(k | j)'), 'Differences of word vectors encode ratios, which is why analogies such as king − man + woman work.'))}
{note('Exams like the table: given two probabilities, compute the ratio and say whether the probe word is an ice word, a steam word or neutral. 8.9 is an ice word, 0.085 a steam word, 1.36 and 0.96 neutral.', 'exam')}
''', kw=['GloVe', 'probability ratio', 'ice and steam', 'log-bilinear', 'biases'])

K.lesson('loss', 'The GloVe loss and its weighting function', f'''
<p>GloVe fits the model equation with weighted least squares over every pair that was seen at least once. Rare pairs are noisy and very frequent pairs should not dominate, so each pair gets a weight f(X<sub>ij</sub>).</p>
{fxs(fx('GloVe objective', 'J = ∑<sub>i,j</sub> f(X<sub>ij</sub>) (w<sub>i</sub>·w̃<sub>j</sub> + b<sub>i</sub> + b̃<sub>j</sub> − log X<sub>ij</sub>)²', 'Only pairs with X<sub>ij</sub> > 0 enter, because f(0) = 0 and log 0 is undefined.', key=True),
     fx('Weighting function', 'f(x) = (x ÷ x<sub>max</sub>)<sup>α</sup> if x < x<sub>max</sub>, else 1', 'The paper uses x<sub>max</sub> = 100 and α = 3/4. The class notebook uses x<sub>max</sub> = 10.', key=True),
     fx('Gradient for one pair', frac('∂J', '∂w<sub>i</sub>') + ' = 2 f(X<sub>ij</sub>) e<sub>ij</sub> w̃<sub>j</sub>, &nbsp; ' + frac('∂J', '∂b<sub>i</sub>') + ' = 2 f(X<sub>ij</sub>) e<sub>ij</sub>', 'e<sub>ij</sub> = prediction − log X<sub>ij</sub>, the error of that pair.'),
     fx('Final vector', 'W<sub>i</sub> = w<sub>i</sub> + w̃<sub>i</sub>', 'The two vectors play symmetric roles, so adding them (or averaging) is a little better than either alone.'))}
<p>f has three jobs from the slide: it is 0 when X is 0 so non-occurrences are ignored, it grows for small counts, and it saturates at 1 for very large counts.</p>
{code('weight')}
{steps('One pair by hand', [
    'w<sub>i</sub> = (0.5, 0.2), w̃<sub>j</sub> = (0.4, −0.1), b<sub>i</sub> = 0.1, b̃<sub>j</sub> = 0.2, X<sub>ij</sub> = 2, x<sub>max</sub> = 10, α = 0.75.',
    'Prediction: 0.5 × 0.4 + 0.2 × (−0.1) + 0.1 + 0.2 = 0.48. Target: log 2 = 0.6931.',
    'Error e = 0.48 − 0.6931 = −0.2131. Weight f(2) = 0.2<sup>0.75</sup> = 0.2991.',
    eq('loss = 0.2991 × (−0.2131)² = 0.0136, and ∂J/∂b<sub>i</sub> = 2 × 0.2991 × (−0.2131) = −0.1275'),
    'The gradient is negative, so gradient descent raises b<sub>i</sub> and the prediction moves up toward log 2.'])}
{table(['Step on the slide', 'What happens'], [['1 to 3', 'collect a corpus, choose a window (for example ±5), count X'], ['4', 'take log X because raw counts are noisy and biased by frequency'], ['5 and 6', 'predict w<sub>i</sub>·w̃<sub>j</sub> + b<sub>i</sub> + b̃<sub>j</sub> and match it to log X<sub>ij</sub>'], ['7', 'weight each pair with f(X<sub>ij</sub>)'], ['8', 'minimise the weighted squared error with gradient descent'], ['9', 'use w<sub>i</sub> or (w<sub>i</sub> + w̃<sub>i</sub>) ÷ 2 as the final vector']])}
{note('The loss is a weighted squared error on log counts, not a cross entropy. Students often write −log P like word2vec.', 'warn')}
''', kw=['GloVe loss', 'weighting function', 'x_max', 'alpha 3/4', 'least squares', 'w + w tilde'])

K.lesson('notebook', 'The GloVe notebook and what it teaches', f'''
<p>The class notebook trains GloVe on ten tiny sentences: ice, water, steam and gas sentences plus the cats and dogs sentences. It counts with window 2 and adds 1 ÷ distance, as the algorithm box of the slides does, so a word two places away adds 0.5. Then it trains 20-dimensional vectors for 300 epochs with Adagrad.</p>
{listing(NB, NB_OUT, title='word2vec_1.ipynb, the GloVe cell (printing trimmed)', cap='Output recorded in the class notebook')}
{steps('Why the loss reaches 0 and ice is far from water', [
    'Parameters: 21 words × 20 numbers × 2 vectors + 21 × 2 biases = 882.',
    'Equations to satisfy: only 80 observed pairs.',
    '882 free numbers for 80 targets can fit every target exactly, so the loss is 0.000000 after 50 epochs.',
    'The model memorises, it does not generalise. Pairs never seen together get no constraint at all, so cosine values such as ice vs water = −0.75 are almost random.',
    eq('Lesson: GloVe needs many more pairs than parameters, which is why real GloVe uses billions of tokens')])}
{note('The prediction inspection shows log 0.5 = −0.6931 for the pair (ice, water). Counts below 1 give negative targets. That is fine, because the target is a log count, not a probability.', 'tip')}
{table(['Method', 'Uses', 'Strength', 'Weakness'], [['Count + SVD (LSA, COALS)', 'global counts', 'fast training, uses all statistics', 'poor at analogies, frequent words dominate'], ['Prediction (word2vec)', 'local windows', 'good analogies, scales with the corpus', 'ignores global statistics, many passes'], ['GloVe', 'global counts, trained with gradient descent', 'fast, good on small and large data', 'a big X must be stored']])}
{ladder(
    '<p>Count which words appear near each other. Words with similar neighbour counts mean similar things. GloVe squeezes those counts into short lists of numbers.</p>',
    '<p>GloVe learns vectors whose dot product plus two biases equals the log co-occurrence count, with a weight that ignores missing pairs and caps very frequent ones.</p>',
    '<p>The objective follows from asking that vector differences encode probability ratios. It is a weighted factorisation of the log count matrix and trains only on non-zero cells, so its cost grows with the number of seen pairs, not with V².</p>',
    '<p>Levy, Goldberg and Dagan (2015) showed that once hyperparameters such as window weighting and context distribution smoothing are matched, SVD of PMI, SGNS and GloVe perform about the same. The gains came from the tricks as much as from the models.</p>')}
''', kw=['notebook', '1 / distance', 'Adagrad', 'overfitting', 'count vs predict'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In a window co-occurrence matrix X<sub>ij</sub> counts', ['how often word i appears in the corpus', 'how often word j appears within the window of word i', 'the distance between i and j', 'the number of documents'], 1, 'Neighbours.', 'Row i, column j: j seen near i.')
K.quiz('e', 'In the slide matrix with window 1, X(I, like) is', ['0', '1', '2', '3'], 2, 'Sentences 1 and 2.', '"I like" appears twice.')
K.quiz('e', 'A word by document matrix tends to capture', ['syntax', 'general topics', 'spelling', 'word order'], 1, 'Latent Semantic Analysis.', 'Words in the same documents share topics.')
K.quiz('e', 'GloVe stands for', ['Global Vectors', 'Gradient Logistic Vectors', 'General Linear Vectors', 'Global Overlap'], 0, 'Pennington et al. 2014.', 'Global Vectors for Word Representation.')
K.quiz('m', 'In X = UΣV<sup>T</sup>, U and V are', ['diagonal', 'orthonormal', 'sparse', 'symmetric'], 1, 'Slide 33.', 'Unit length columns at right angles.')
K.quiz('m', 'Why does SVD on raw counts work poorly?', ['SVD needs negative numbers', 'function words are too frequent, so syntax has too much impact', 'the matrix is too small', 'counts are not integers'], 1, 'Slide 34.', 'Log counts, caps and ignoring function words help.')
K.quiz('m', 'P(k | ice) ÷ P(k | steam) = 0.085 means k is', ['an ice word', 'a steam word', 'neutral', 'missing from the corpus'], 1, 'Much smaller than 1.', 'gas is far more common near steam.')
K.quiz('m', 'The GloVe weighting function gives f(0) =', ['0', '1', 'undefined', 'x_max'], 0, 'Ignore non-occurrences.', 'Pairs never seen together drop out, which also avoids log 0.')
K.quiz('m', 'With x<sub>max</sub> = 100, a pair seen 500 times gets weight', ['5', '0.2', '1', '0'], 2, 'f saturates.', 'Above x<sub>max</sub> the weight stays 1.')
K.quiz('h', 'The GloVe loss is', ['cross entropy over the vocabulary', 'a weighted squared error between w·w̃ + b + b̃ and log X', 'a hinge loss', 'negative sampling'], 1, 'Least squares.', 'J = ∑ f(X)(w·w̃ + b + b̃ − log X)².')
K.quiz('h', 'The notebook loss drops to 0.000000. The main reason is', ['GloVe always reaches 0', '882 parameters for 80 observed pairs, so the model fits every target exactly', 'Adagrad has a bug', 'the learning rate is 0'], 1, 'Count parameters and equations.', 'Over-parameterised on a tiny corpus, it memorises.')
K.quiz('h', 'Where does the bias b<sub>i</sub> come from in the derivation?', ['regularisation', 'the term log X<sub>i</sub>, which does not depend on k', 'the window size', 'the learning rate'], 1, 'log P(k | i) = log X<sub>ik</sub> − log X<sub>i</sub>.', 'A term that depends only on i becomes a bias.')
K.quiz('x', 'Which final vector does the GloVe algorithm box return?', ['w only', 'w̃ only', 'w + w̃', 'w − w̃'], 2, 'Step 5 of the algorithm.', 'The two vectors are symmetric, so their sum is used.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Slide corpus, window 1. What is X(like, NLP)?', '1', '"I like NLP".',
       ['NLP appears only in sentence 2.', 'Its left neighbour is like.', eq('X(like, NLP) = 1')], check=1, tol=1e-9)
K.calc('e', 'A vocabulary of 50,000 words. How many cells does the full window co-occurrence matrix have?', '2500000000', 'V × V.',
       ['Rows: 50,000.', 'Columns: 50,000.', eq('50,000² = 2.5 × 10<sup>9</sup> cells')], check=2.5e9, tol=0.5)
K.calc('e', 'P(solid | ice) = 1.9 × 10<sup>−4</sup> and P(solid | steam) = 2.2 × 10<sup>−5</sup>. Ratio to two decimals.', '8.64', 'Divide.',
       ['1.9 × 10<sup>−4</sup> ÷ 2.2 × 10<sup>−5</sup>.', '= 1.9 ÷ 0.22.', eq('8.64 (the paper shows 8.9 from unrounded numbers)')], check=1.9e-4 / 2.2e-5, tol=0.005)
K.calc('e', 'Paper settings x<sub>max</sub> = 100, α = 0.75. Compute f(20) to four decimals.', '0.2991', '(20 ÷ 100)<sup>0.75</sup>.',
       ['20 is below x<sub>max</sub>.', '20 ÷ 100 = 0.2.', eq('0.2<sup>0.75</sup> = 0.2991')], check=0.2 ** 0.75, tol=5e-5)
K.calc('m', 'Notebook settings x<sub>max</sub> = 10, α = 0.75. Compute f(0.5) to four decimals.', '0.1057', '(0.5 ÷ 10)<sup>0.75</sup>.',
       ['0.5 ÷ 10 = 0.05.', 'ln 0.05 = −2.9957, times 0.75 = −2.2468.', eq('e<sup>−2.2468</sup> = 0.1057')], check=0.05 ** 0.75, tol=5e-5)
K.calc('m', 'X = ' + mat([['3', '0'], ['4', '5']]) + '. Largest singular value to three decimals.', '6.708', 'Eigenvalues of X<sup>T</sup>X.',
       ['X<sup>T</sup>X = ' + mat([['25', '20'], ['20', '25']]) + '.', 'Eigenvalues 45 and 5.', eq('σ₁ = √45 = 6.708')], check=45 ** 0.5, tol=5e-4)
K.calc('m', 'Same X. What share of the energy does the rank 1 approximation keep? Two decimals.', '0.9', 'σ₁² ÷ (σ₁² + σ₂²).',
       ['σ₁² = 45, σ₂² = 5.', 'Total 50.', eq('45 ÷ 50 = 0.90')], check=0.9, tol=0.005)
K.calc('m', 'Notebook counting with window 2 and 1 ÷ distance. In "ice and water are related", what does water add to X(ice, water)?', '0.5', 'Distance 2.',
       ['ice is position 0, water position 2.', 'Distance 2, inside the window.', eq('1 ÷ 2 = 0.5')], check=0.5, tol=1e-9)
K.calc('h', 'w<sub>i</sub> = (0.5, 0.2), w̃<sub>j</sub> = (0.4, −0.1), b<sub>i</sub> = 0.1, b̃<sub>j</sub> = 0.2, X<sub>ij</sub> = 2, x<sub>max</sub> = 10, α = 0.75. Weighted loss of this pair, four decimals.', '0.0136', 'f(X)(prediction − log X)².',
       ['Prediction 0.2 − 0.02 + 0.3 = 0.48.', 'Error 0.48 − 0.6931 = −0.2131, f(2) = 0.2991.', eq('0.2991 × 0.04543 = 0.0136')], check=0.2 ** 0.75 * (0.48 - 0.6931471805599453) ** 2, tol=5e-5)
K.calc('h', 'Same pair. ∂J/∂b<sub>i</sub> to four decimals.', '-0.1275', '2 f(X) e.',
       ['e = −0.2131.', 'f = 0.2991.', eq('2 × 0.2991 × (−0.2131) = −0.1275')], check=2 * 0.2 ** 0.75 * (0.48 - 0.6931471805599453), tol=5e-5)
K.calc('h', 'Notebook GloVe: 21 words, d = 20, two vectors and two biases per word. Number of parameters.', '882', '2Vd + 2V.',
       ['Vectors: 2 × 21 × 20 = 840.', 'Biases: 2 × 21 = 42.', eq('840 + 42 = 882')], check=882, tol=1e-9)
K.calc('x', 'With x<sub>max</sub> = 100 and α = 0.75, how many times more weight does a pair seen 50 times get than a pair seen 5 times? Two decimals.', '5.62', '(50 ÷ 5)<sup>0.75</sup>.',
       ['Both are below x<sub>max</sub>, so the x<sub>max</sub> cancels.', 'Ratio = 10<sup>0.75</sup>.', eq('10<sup>0.75</sup> = 5.62, less than the raw factor 10')], check=10 ** 0.75, tol=0.005)

# ---------------------------------------------------------------- assignments
K.assign('cooc', 'e', 'Build the co-occurrence counts',
         '<p>Write <code>cooc(sentences, m, inv)</code>. sentences is a list of token lists. Return a dict from (word, context) to its count with a symmetric window of m words. If inv is True each neighbour adds 1 ÷ distance, otherwise 1.</p>',
         '''
def cooc(sentences, m, inv):
    pass
''', [('cooc([["I", "like", "deep", "learning", "."], ["I", "like", "NLP", "."], ["I", "enjoy", "flying", "."]], 1, False)[("I", "like")]', 2),
      ('cooc([["ice", "and", "water", "are", "related"]], 2, True)[("ice", "water")]', 0.5),
      ('len(cooc([["a", "b", "c"]], 1, False))', 4)],
         '''
def cooc(sentences, m, inv):
    X = {}
    for s in sentences:
        for i, w in enumerate(s):
            for j in range(max(0, i - m), min(len(s), i + m + 1)):
                if j == i:
                    continue
                add = 1 / abs(i - j) if inv else 1
                X[(w, s[j])] = X.get((w, s[j]), 0) + add
    return X
''', 'Loop over every position and every neighbour in the window.', '<p>For "a b c" with window 1 the pairs are (a, b), (b, a), (b, c) and (c, b).</p>')
K.assign('gloss', 'm', 'The GloVe loss for a few pairs',
         '<p>Write <code>glove_loss(items, x_max, alpha)</code>. Each item is (w, wt, b, bt, x) with two vectors, two biases and the count. Return ∑ f(x)(w·wt + b + bt − log x)², rounded to 4 decimals.</p>',
         '''
import math

def glove_loss(items, x_max, alpha):
    pass
''', [('glove_loss([([0.5, 0.2], [0.4, -0.1], 0.1, 0.2, 2)], 10, 0.75)', 0.0136),
      ('glove_loss([([1, 0], [1, 0], 0, 0, math.e)], 10, 1)', 0.0),
      ('glove_loss([([0, 0], [0, 0], 0, 0, 200), ([0, 0], [0, 0], 0, 0, 1)], 100, 0.75)', 28.0722)],
         '''
import math

def glove_loss(items, x_max, alpha):
    J = 0.0
    for w, wt, b, bt, x in items:
        f = (x / x_max) ** alpha if x < x_max else 1.0
        e = sum(p * q for p, q in zip(w, wt)) + b + bt - math.log(x)
        J += f * e * e
    return round(J, 4)
''', 'Weight first, then the squared error of the log count.', '<p>In the third test the first pair is capped at weight 1 and has error −log 200, while the count 1 has target 0 and adds nothing.</p>')
K.assign('topsv', 'h', 'The top singular value by power iteration',
         '<p>Write <code>top_singular(X, iters)</code> for a list of rows X. Form A = X<sup>T</sup>X, start from a vector of ones, repeat v = Av ÷ ‖Av‖ for iters steps, and return √(v·Av) rounded to 4 decimals.</p>',
         '''
def top_singular(X, iters):
    pass
''', [('top_singular([[3, 0], [4, 5]], 30)', 6.7082), ('top_singular([[2, 0], [0, 1]], 30)', 2.0), ('top_singular([[1, 2], [2, 4]], 5)', 5.0)],
         '''
def top_singular(X, iters):
    n = len(X[0])
    A = [[sum(r[i] * r[j] for r in X) for j in range(n)] for i in range(n)]
    mul = lambda v: [sum(A[i][j] * v[j] for j in range(n)) for i in range(n)]
    v = [1.0] * n
    for _ in range(iters):
        w = mul(v)
        s = sum(t * t for t in w) ** 0.5
        v = [t / s for t in w]
    Av = mul(v)
    return round(sum(p * q for p, q in zip(v, Av)) ** 0.5, 4)
''', 'Power iteration finds the biggest eigenvalue of X<sup>T</sup>X, and σ₁ is its square root.', '<p>The third matrix has rank 1, so σ₁ = √25 = 5 and σ₂ = 0.</p>')

K.must('Co-occurrence matrix', 'X<sub>ij</sub> counts word j inside the window of word i. Window matrices give word space, word by document matrices give topics (LSA).')
K.must('SVD', 'X = UΣV<sup>T</sup>, keep the top k singular values for k-dimensional vectors. Raw counts need log, caps or removing function words first.')
K.must('GloVe idea', 'Meaning is in ratios P(k | i) ÷ P(k | j): much more than 1, much less than 1, or about 1 (ice, steam, solid, gas, water, fashion).')
K.must('GloVe loss', 'J = ∑ f(X<sub>ij</sub>)(w<sub>i</sub>·w̃<sub>j</sub> + b<sub>i</sub> + b̃<sub>j</sub> − log X<sub>ij</sub>)², f(x) = (x ÷ x<sub>max</sub>)<sup>α</sup> below x<sub>max</sub> else 1, x<sub>max</sub> = 100, α = 3/4.')
K.must('Notebook', 'Window 2 with 1 ÷ distance, d = 20, x<sub>max</sub> = 10, final vectors w + w̃. 882 parameters for 80 pairs, so the loss hits 0 and the tiny model memorises.')

T = K.topic(
    slug='cooccurrence-glove', topic='nn-cooccurrence-glove', step=(2, 'Word vectors', 'nn-vectors', 'Turn words into vectors that capture meaning: one-hot vectors and their limits, word2vec with softmax and negative sampling, co-occurrence counts, GloVe, and how to test and improve embeddings.', 'College'),
    title='Co-occurrence counts, SVD and GloVe', short='Counts and GloVe', badge='2.4', minutes=45, added='2026-11-01',
    lead='Count which words appear together, shrink the counts with SVD, then learn GloVe vectors whose dot products match log counts, with the ice and steam ratios and the class notebook.',
    desc='Window and document co-occurrence matrices, the slide matrix for "I like deep learning", SVD and truncated SVD with the COALS fixes, GloVe probability ratios and the derivation of its model, the weighted least squares loss and f(x), the 1 / distance notebook and why it overfits.',
    summary='Co-occurrence matrices, SVD, GloVe ratios, the GloVe loss and weighting function, and the notebook.',
    keywords=['co-occurrence', 'SVD', 'LSA', 'GloVe', 'weighting function', 'x_max', 'log counts', 'notebook'],
    recap='<p>Counting neighbours gives huge sparse vectors. SVD shrinks them, and GloVe learns short vectors whose dot product plus biases equals the log count, weighted by f(x) so that missing pairs drop out and frequent pairs are capped.</p>')
