# NLP section, chapter 2.5: evaluating and improving word embeddings. Source: FoVL lecture 2 slides 45 to 69
# (intrinsic against extrinsic evaluation, the four intrinsic families of Schnabel et al. 2015, initialising with
# pre-trained vectors, fixed against fine-tuned and concatenated embeddings, "no one size fits all", the four weaknesses
# dog / dogs, whale / fish and dog / perro, non-interpretable axes and bias, character and morpheme based embeddings,
# character n-grams for "where", Faruqui et al. 2014, Artetxe et al. 2017, Zhang et al. 2017, sparse embeddings with an
# L1 term, the debiasing of Bolukbasi et al. 2016 and the fastText case study with "playing") and the lecture discussion.
from cvkit import Kit, fx, fxs, frac, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('spear', r'''
# Relatedness test: Spearman correlation between human scores and model cosines
human = {"car-automobile": 9.5, "coast-shore": 9.1, "cup-coffee": 6.6, "king-cabbage": 0.2, "forest-graveyard": 1.8}
model = {"car-automobile": 0.92, "coast-shore": 0.71, "cup-coffee": 0.74, "king-cabbage": 0.05, "forest-graveyard": 0.21}

def ranks(scores):
    order = sorted(scores, key=lambda k: -scores[k])
    return {k: i + 1 for i, k in enumerate(order)}

rh, rm = ranks(human), ranks(model)
d2 = sum((rh[k] - rm[k]) ** 2 for k in human)
n = len(human)
print("human ranks:", rh)
print("model ranks:", rm)
print("sum d^2 =", d2, " rho =", 1 - 6 * d2 / (n * (n * n - 1)))
''')

K.code('grams', r'''
# fastText character n-grams with boundary marks
def ngrams(word, lo, hi):
    s = "<" + word + ">"
    return [s[i:i + n] for n in range(lo, hi + 1) for i in range(len(s) - n + 1)]

for n in range(3, 7):
    print(n, ngrams("where", n, n))
print("total for where:", len(ngrams("where", 3, 6)), "plus the word itself")
print("playing, trigrams:", ngrams("playing", 3, 3))
''')

K.code('neutral', r'''
# Neutralise a word along the bias direction g (Bolukbasi et al. 2016)
he, she = [0, -1], [0, 1]
d = [she[0] - he[0], she[1] - he[1]]
n = (d[0] ** 2 + d[1] ** 2) ** 0.5
g = [d[0] / n, d[1] / n]
for word, v in [("programmer", [3, -0.8]), ("homemaker", [3, 0.9]), ("doctor", [2.5, -0.6])]:
    p = v[0] * g[0] + v[1] * g[1]
    new = [round(v[0] - p * g[0], 4), round(v[1] - p * g[1], 4)]
    print(word.ljust(11), "part along g =", p, " neutralised =", new)
''')

K.lesson('intrinsic', 'Intrinsic evaluation: test the vectors on their own', f'''
<p>After training, how do we know the embedding is good? NLP has two kinds of evaluation. Intrinsic evaluation checks the vectors on a small subtask. Extrinsic evaluation plugs them into a real system and measures that system.</p>
{table(['', 'Intrinsic', 'Extrinsic'], [['Evaluated on', 'a specific intermediate subtask', 'a real task such as NER or translation'], ['Speed', 'fast to compute', 'can take a long time'], ['Strength', 'helps to understand the embedding', 'tells you if it really helps'], ['Weakness', 'not clear it helps unless it correlates with a real task', 'unclear whether the embedding or another part is the problem']])}
<p>Schnabel and others (2015) group intrinsic tests into four families.</p>
{table(['Family', 'Method', 'Data and metric'], [['Relatedness', 'cosine of word pairs against human similarity scores', 'WordSim-353, SimLex-999, Spearman or Pearson correlation'], ['Analogy', 'b − a + c, nearest word by cosine', 'Google analogy test set, BATS, accuracy'], ['Categorisation', 'cluster the vectors with k-means', 'purity or F-score against gold categories'], ['Selectional preference', 'score verb and noun pairs', 'eat-apple should beat eat-rock']])}
{fxs(fx('Spearman correlation (no ties)', 'ρ = 1 − ' + frac('6 ∑ d<sub>i</sub>²', 'n(n² − 1)'), 'd<sub>i</sub> is the difference between the human rank and the model rank of pair i.', key=True),
     fx('Analogy', 'd = argmax<sub>w ∉ {a, b, c}</sub> cos(w, b − a + c)', 'man : king :: woman : queen. The three input words are excluded.', key=True),
     fx('Cluster purity', 'purity = ' + frac('1', 'N') + ' ∑<sub>clusters</sub> max<sub>class</sub> |cluster ∩ class|', 'Each cluster votes for its majority class.'))}
{viz('analogy')}
{code('spear')}
{steps('Purity by hand', [
    'k-means gives cluster 1 = {dog, cat, apple} and cluster 2 = {orange, banana, horse}.',
    'Cluster 1 majority class: animal, 2 words. Cluster 2 majority class: fruit, 2 words.',
    eq('purity = (2 + 2) ÷ 6 = 0.667'),
    'A perfect embedding would give purity 1.'])}
{note('A Spearman question gives two lists of scores. Rank both lists first, then use the formula. Pearson uses the raw scores instead.', 'exam')}
''', kw=['intrinsic evaluation', 'relatedness', 'Spearman', 'analogy', 'purity', 'selectional preference'])

K.lesson('extrinsic', 'Extrinsic evaluation: use the vectors in a real system', f'''
<p>Extrinsic evaluation asks whether embeddings help a downstream task: sentiment analysis, named entity recognition, machine translation or question answering. It reports the end metric, such as accuracy, F1 or BLEU. If replacing exactly one subsystem with another raises the score, the new embedding wins.</p>
{table(['Way to use pre-trained vectors', 'Pros', 'Cons'], [['Fixed (frozen)', 'fewer parameters, less overfitting', 'cannot adapt to task specific meaning'], ['Fine-tuned', 'adapts to the task', 'may forget general knowledge'], ['Concatenated [pre-trained, learned]', 'general and task specific information together', 'bigger model, more computation']])}
{fxs(fx('Concatenation', 'x<sub>w</sub> = [e<sub>pre</sub>(w), e<sub>task</sub>(w)] ∈ ℝ<sup>d₁ + d₂</sup>', 'A 300-dimensional GloVe vector plus a learned 100-dimensional vector gives 400 inputs.'),
     fx('Trainable embedding parameters', 'frozen: 0, &nbsp; fine-tuned: V × d', 'With V = 10,000 and d = 300, fine-tuning trains 3 million extra numbers.'))}
{steps('Count the parameters of a concatenated input', [
    'Vocabulary V = 10,000. Pre-trained part 300 dimensions, frozen. Learned part 100 dimensions.',
    'Trainable numbers in the learned table: 10,000 × 100 = 1,000,000.',
    'Frozen numbers: 10,000 × 300 = 3,000,000, which do not change.',
    eq('Input size per word = 300 + 100 = 400, trainable embedding parameters = 1,000,000')])}
{scene('choosing vectors for a hospital chatbot', '<p>A team builds a chatbot for patient questions with only 5,000 labelled messages. Training embeddings from scratch on so little text gives poor vectors, so they start from pre-trained vectors. Freezing them protects against overfitting the small set, and a small learned part captures hospital words such as "OPD" and "discharge summary". They compare each choice by the F1 score of the final intent classifier, which is an extrinsic evaluation.</p>')}
<p>The lecture's conclusion from Schnabel and others: no embedding wins on every metric. SGNS wins some columns, GloVe others. Be aware of the trade offs and pick the best one for your task.</p>
{note('Pre-trained vectors help most when the labelled data is small. With a huge labelled set, vectors trained on the task can catch up.', 'tip')}
''', kw=['extrinsic evaluation', 'downstream task', 'pre-trained embeddings', 'fine-tuning', 'concatenation'])

K.lesson('subwords', 'Subword embeddings and fastText', f'''
<p>Word2vec and GloVe treat each word form as a separate symbol. "dog" and "dogs" get two unrelated vectors, and they do not know that -s marks a plural. Rare words get poor vectors, and a word never seen in training (out of vocabulary, OOV) gets none at all.</p>
<p>Three fixes from the slides break a word into smaller pieces, give each piece a vector, and combine them.</p>
{table(['Pieces', 'Example', 'Combined with'], [['characters', 'c, a, t, s', 'a BiLSTM or CNN over the characters'], ['morphemes', 'un + fortunate + ly', 'an RNN or a sum'], ['character n-grams (fastText)', '&lt;wh, whe, her, ere, re&gt;, ...', 'a sum or average']])}
{fxs(fx('fastText word vector', 'v<sub>w</sub> = z<sub>w</sub> + ∑<sub>g ∈ G(w)</sub> z<sub>g</sub>', 'G(w) is the set of character n-grams of w (usually n = 3 to 6) with boundary marks &lt; and &gt;.', key=True),
     fx('Number of n-grams', '∑<sub>n = lo</sub><sup>hi</sup> (L + 2 − n + 1)', 'L is the word length. The marks add 2 characters.'),
     fx('Training', 'skip-gram score s(w, c) = ∑<sub>g ∈ G(w)</sub> z<sub>g</sub>·u<sub>c</sub>', 'Same skip-gram or CBOW as word2vec, but the update goes to every n-gram vector of the word.'))}
{viz('subword')}
{code('grams')}
{steps('Count the n-grams of "where" for n = 3 to 6', [
    'With marks the string is &lt;where&gt;, 7 characters.',
    'n = 3: 7 − 3 + 1 = 5. n = 4: 4. n = 5: 3. n = 6: 2.',
    eq('5 + 4 + 3 + 2 = 14 n-grams, plus the whole word'),
    'The trigram &lt;her&gt; of the word "her" differs from her inside "where", thanks to the marks.'])}
{note('The slide lists the trigrams of "playing" as &lt;pl, pla, lay, ayi, yin, ing, ng&gt;: 7 trigrams. The last one is ng&gt;, the suffix shared by every -ing word.', 'warn')}
{deep('hashing the n-grams', '<p>There are far too many distinct n-grams to store, so fastText hashes each one into a fixed number of buckets, 2 million by default. Two n-grams can share a bucket. This bounds memory and still gives any new word, even a typo, a reasonable vector from its pieces.</p>')}
''', kw=['subword', 'character n-grams', 'fastText', 'OOV', 'morphemes', 'dog and dogs'])

K.lesson('align', 'Knowledge, languages and alignment', f'''
<p>Embeddings capture statistics of text, not facts. "whale" sits near "fish" because both appear near "ocean", not because whales are fish. Embeddings trained separately for English and Spanish are not aligned either: "dog" and "perro" may end up far apart, because each training run picks its own orientation.</p>
<p>The fix is a mapping from one space to the other. Faruqui and Dyer (2014) used a bilingual dictionary. The surprising later result is that no dictionary is needed, because co-occurrence patterns are similar in every language, so the two point clouds have about the same shape.</p>
{table(['Method', 'Anchor', 'How the mapping is found'], [['Faruqui and Dyer 2014', 'a bilingual dictionary', 'project both spaces into a shared space (CCA)'], ['Artetxe et al. 2017', 'identical strings: numbers, names, "COVID", "2025", "UN"', 'learn a linear map W from the anchors, then refine with mutual nearest neighbours'], ['Zhang et al. 2017', 'none', 'adversarial training: a generator W against a discriminator that guesses the language']])}
{fxs(fx('Linear mapping', 'min<sub>W</sub> ∑<sub>i</sub> ‖W x<sub>i</sub> − y<sub>i</sub>‖²', 'x<sub>i</sub> is a source word, y<sub>i</sub> its translation.', key=True),
     fx('Orthogonal Procrustes', 'W = U V<sup>T</sup> where U Σ V<sup>T</sup> = SVD(Y X<sup>T</sup>)', 'Forcing W<sup>T</sup>W = I (a rotation) keeps distances, and this closed form solves it.'))}
{viz('crossling')}
{steps('Map one word with a known rotation', [
    'Suppose the Spanish space is the English space turned by 90 degrees: W = ' + mat([['0', '−1'], ['1', '0']]) + '.',
    'English "cat" is x = (0.8, 0.6).',
    eq('W x = (0 × 0.8 − 1 × 0.6, 1 × 0.8 + 0 × 0.6) = (−0.6, 0.8)'),
    'The nearest Spanish vector to (−0.6, 0.8) should be "gato". Length stays 1, so the rotation kept distances.'])}
{note('The adversarial method stops when the discriminator cannot tell a mapped English vector from a real Spanish one. At that point the two spaces are statistically indistinguishable.', 'tip')}
''', kw=['cross-lingual', 'alignment', 'Procrustes', 'identical words', 'adversarial', 'whale and fish'])

K.lesson('sparse-bias', 'Interpretable and fairer embeddings', f'''
<p>Dense vectors spread information over every dimension, so no axis has a clear meaning. We can say king − man + woman ≈ queen, but we cannot point at a "gender" or "royalty" axis. Sparse embeddings add a penalty that pushes most values to 0, so each active dimension tends to mean one feature, such as "is animal" or "is a place".</p>
{fxs(fx('Sparsity penalty', 'J<sub>sparse</sub> = J + λ ∑<sub>i</sub> ‖w<sub>i</sub>‖₁', '‖w‖₁ = ∑ |w<sub>k</sub>|. A bigger λ gives more zeros.', key=True))}
<p>Embeddings also learn the biases in the text they read. In early word2vec vectors trained on Google News, the analogy man : computer programmer :: woman : ? returned homemaker. Bolukbasi and others (2016) reduce this in three steps.</p>
{table(['Step', 'What it does'], [['1. Identify', 'pick definitional pairs such as he and she, man and woman'], ['2. Direction', 'compute the bias direction g from their differences (the top principal component)'], ['3. Neutralise', 'remove the g part of words that should be neutral, such as programmer or nurse'], ['(Equalise)', 'make each pair equally far from every neutral word']])}
{fxs(fx('Neutralise', 'v′ = v − (v·g) g', 'g is a unit vector. After this v′·g = 0.', key=True))}
{viz('debias')}
{code('neutral')}
{steps('Neutralise a word with a tilted direction', [
    'g = (0.6, 0.8), a unit vector. Word vector v = (2, 1).',
    'v·g = 2 × 0.6 + 1 × 0.8 = 2.0.',
    eq('v′ = (2 − 2.0 × 0.6, 1 − 2.0 × 0.8) = (0.8, −0.6)'),
    'Check: v′·g = 0.48 − 0.48 = 0, so the bias part is gone.'])}
{ladder(
    '<p>Computers learn word meanings from books and the web. If the text often says "he is an engineer" and "she is a nurse", the computer learns that too. We can find the he to she direction and remove it from job words.</p>',
    '<p>Evaluate embeddings intrinsically (similarity, analogy, clusters) and extrinsically (task scores). Improve them with subwords, cross-lingual mapping, sparsity and debiasing by projection.</p>',
    '<p>Each fix is linear algebra: n-gram sums, an orthogonal map from Procrustes, an L1 penalty, and a projection onto the complement of g. The analogy test itself assumes relations are parallel offsets, which holds only roughly.</p>',
    '<p>Gonen and Goldberg (2019) showed that projection debiasing hides bias rather than removing it: neutralised words still cluster by their old gender association. Measuring bias with tests such as WEAT and debiasing contextual models remain open problems.</p>')}
{note('Perfect debiasing remains hard. The slide says embeddings become more balanced, not unbiased. A balanced or filtered corpus is the other approach.', 'warn')}
''', kw=['sparse embeddings', 'L1', 'interpretability', 'bias', 'debiasing', 'neutralise'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Testing embeddings on word similarity scores rated by people is', ['extrinsic', 'intrinsic', 'adversarial', 'unsupervised mapping'], 1, 'A subtask.', 'Relatedness is an intrinsic test.')
K.quiz('e', 'man : king :: woman : ?', ['prince', 'queen', 'girl', 'crown'], 1, 'b − a + c.', 'king − man + woman ≈ queen.')
K.quiz('e', 'Which model builds words from character n-grams?', ['GloVe', 'word2vec', 'fastText', 'LSA'], 2, 'Facebook AI Research 2016.', 'fastText sums n-gram vectors.')
K.quiz('e', 'Measuring sentiment classifier accuracy with different embeddings is', ['intrinsic', 'extrinsic', 'categorisation', 'selectional preference'], 1, 'A real task.', 'Extrinsic evaluation uses a downstream task.')
K.quiz('m', 'Which dataset is used for the analogy test?', ['WordSim-353', 'SimLex-999', 'Google analogy test set', 'CoNLL-2003'], 2, 'Also BATS.', 'WordSim and SimLex are relatedness sets.')
K.quiz('m', 'Fine-tuning pre-trained embeddings risks', ['too few parameters', 'forgetting general knowledge', 'losing OOV words', 'a bigger input'], 1, 'Slide 49.', 'The vectors drift toward the small task.')
K.quiz('m', 'Why does fastText handle an unseen word such as "catsy"?', ['it looks it up online', 'it builds a vector from the character n-grams', 'it uses the vector of the nearest word', 'it cannot'], 1, 'Pieces are shared.', 'Every n-gram of catsy has a vector from training.')
K.quiz('m', 'How many character n-grams of length 3 to 6 does "where" have with boundary marks?', ['10', '12', '14', '15'], 2, '5 + 4 + 3 + 2.', 'Plus the whole word as a separate unit.')
K.quiz('m', 'Artetxe et al. 2017 align languages without a dictionary using', ['adversarial training', 'identical strings such as numbers and names', 'translation pairs', 'character n-grams'], 1, 'Anchors.', 'Then refine with mutual nearest neighbours.')
K.quiz('h', 'After neutralising v with unit bias direction g, v′·g equals', ['1', '0', '‖v‖', 'v·g'], 1, 'v′ = v − (v·g)g.', 'v′·g = v·g − v·g × g·g = 0.')
K.quiz('h', 'Human ranks 1, 2, 3, 4, 5 and model ranks 2, 1, 3, 5, 4. Spearman ρ is', ['0.6', '0.7', '0.8', '0.9'], 2, '∑d² = 4.', '1 − 24 ÷ 120 = 0.8.')
K.quiz('h', 'Why force the cross-lingual map W to be orthogonal?', ['to make it sparse', 'to keep distances and angles, so the monolingual structure survives', 'to reduce the vocabulary', 'to remove bias'], 1, 'A rotation.', 'Orthogonal maps preserve cosine similarity.')
K.quiz('x', 'Gonen and Goldberg (2019) found that projection debiasing', ['removes all bias', 'mostly hides bias: neutralised words still cluster by gender', 'works only for fastText', 'increases analogy accuracy'], 1, '"Lipstick on a pig".', 'Bias remains in the geometry of the neighbours.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Human ranks 1, 2, 3, 4, 5 and model ranks 2, 1, 3, 5, 4. Compute Spearman ρ.', '0.8', '1 − 6∑d² ÷ n(n² − 1).',
       ['d = (−1, 1, 0, −1, 1), ∑d² = 4.', 'n(n² − 1) = 5 × 24 = 120.', eq('ρ = 1 − 24 ÷ 120 = 0.8')], check=0.8, tol=1e-9)
K.calc('e', 'How many trigrams does "playing" have with boundary marks?', '7', 'L + 2 − 3 + 1.',
       ['&lt;playing&gt; has 9 characters.', '9 − 3 + 1.', eq('7 trigrams')], check=7, tol=1e-9)
K.calc('e', 'Clusters {dog, cat, apple} and {orange, banana, horse}. Purity, three decimals.', '0.667', 'Majority per cluster.',
       ['Cluster 1 majority: 2 animals.', 'Cluster 2 majority: 2 fruits.', eq('(2 + 2) ÷ 6 = 0.667')], check=4 / 6, tol=5e-4)
K.calc('m', 'Number of character n-grams with n = 3 to 6 for a 5-letter word.', '14', 'Marks make 7 characters.',
       ['n = 3: 5, n = 4: 4.', 'n = 5: 3, n = 6: 2.', eq('14')], check=14, tol=1e-9)
K.calc('m', 'Number of character n-grams with n = 3 to 6 for "embedding" (9 letters).', '30', '11 characters with marks.',
       ['n = 3: 9, n = 4: 8.', 'n = 5: 7, n = 6: 6.', eq('9 + 8 + 7 + 6 = 30')], check=30, tol=1e-9)
K.calc('m', 'A model answers 12,000 of the 19,544 Google analogy questions. Accuracy in percent, one decimal.', '61.4', 'correct ÷ total.',
       ['12,000 ÷ 19,544 = 0.6140.', 'Times 100.', eq('61.4 percent')], check=100 * 12000 / 19544, tol=0.05)
K.calc('m', 'V = 10,000, a frozen 300-dimensional pre-trained table and a learned 100-dimensional table are concatenated. Trainable embedding parameters.', '1000000', 'Only the learned part trains.',
       ['Frozen: 3,000,000, not trained.', 'Learned: 10,000 × 100.', eq('1,000,000 trainable')], check=1e6, tol=0.5)
K.calc('h', 'g = (0.6, 0.8) and v = (2, 1). First component of the neutralised vector v − (v·g)g.', '0.8', 'v·g first.',
       ['v·g = 1.2 + 0.8 = 2.0.', '(v·g)g = (1.2, 1.6).', eq('v′ = (0.8, −0.6), first component 0.8')], check=0.8, tol=1e-9)
K.calc('h', 'Same g and v. Second component of v′.', '-0.6', '1 − 2.0 × 0.8.',
       ['(v·g)g = (1.2, 1.6).', '1 − 1.6.', eq('−0.6')], check=-0.6, tol=1e-9)
K.calc('h', 'W rotates by 90 degrees, W = ' + mat([['0', '−1'], ['1', '0']]) + '. Map x = (0.8, 0.6). Give the first component.', '-0.6', 'Row 1 of W times x.',
       ['Row 1: (0, −1).', '0 × 0.8 − 1 × 0.6.', eq('−0.6, and the full result is (−0.6, 0.8)')], check=-0.6, tol=1e-9)
K.calc('h', 'λ = 0.1 and a word vector (0.5, −0.2, 0, 0.3). The L1 sparsity penalty for this word.', '0.1', 'λ ∑|w|.',
       ['|0.5| + |−0.2| + 0 + |0.3| = 1.0.', 'Times λ.', eq('0.1 × 1.0 = 0.1')], check=0.1, tol=1e-9)
K.calc('x', 'a = man (1, 1), b = king (4, 1.2), c = woman (1, 3). Compute b − a + c and give its second component.', '3.2', 'Component by component.',
       ['b − a = (3, 0.2).', 'Add c = (1, 3).', eq('(4, 3.2), exactly the toy vector of queen')], check=3.2, tol=1e-9)

# ---------------------------------------------------------------- assignments
K.assign('grams', 'e', 'fastText n-grams',
         '<p>Write <code>ngrams(word, lo, hi)</code> that adds the marks &lt; and &gt; and returns every character n-gram with lo ≤ n ≤ hi, shortest first, left to right.</p>',
         '''
def ngrams(word, lo, hi):
    pass
''', [('len(ngrams("where", 3, 6))', 14), ('ngrams("playing", 3, 3)', ['<pl', 'pla', 'lay', 'ayi', 'yin', 'ing', 'ng>']), ('ngrams("a", 3, 3)', ['<a>'])],
         '''
def ngrams(word, lo, hi):
    s = "<" + word + ">"
    return [s[i:i + n] for n in range(lo, hi + 1) for i in range(len(s) - n + 1)]
''', 'Slide a window of n letters across the marked word.', '<p>A one letter word with marks is 3 characters, so it has one trigram.</p>')
K.assign('spearman', 'm', 'Spearman correlation from scores',
         '<p>Write <code>spearman(a, b)</code> for two lists of scores without ties. Rank each list (highest score is rank 1) and return 1 − 6∑d² ÷ n(n² − 1), rounded to 4 decimals.</p>',
         '''
def spearman(a, b):
    pass
''', [('spearman([9.5, 9.1, 6.6, 0.2, 1.8], [0.92, 0.71, 0.74, 0.05, 0.21])', 0.9), ('spearman([1, 2, 3], [3, 2, 1])', -1.0), ('spearman([0.1, 0.5, 0.9, 0.3], [0.2, 0.6, 0.8, 0.1])', 0.8)],
         '''
def spearman(a, b):
    def ranks(x):
        order = sorted(range(len(x)), key=lambda i: -x[i])
        r = [0] * len(x)
        for k, i in enumerate(order):
            r[i] = k + 1
        return r
    ra, rb = ranks(a), ranks(b)
    n = len(a)
    d2 = sum((p - q) ** 2 for p, q in zip(ra, rb))
    return round(1 - 6 * d2 / (n * (n * n - 1)), 4)
''', 'Turn scores into ranks first.', '<p>The first test is the relatedness example of the lesson: only cup-coffee and coast-shore swap, so ∑d² = 2.</p>')
K.assign('neutralise', 'h', 'Neutralise a bias direction',
         '<p>Write <code>neutralise(v, a, b)</code>. Compute g as the unit vector of b − a, then return v − (v·g)g with every number rounded to 4 decimals.</p>',
         '''
def neutralise(v, a, b):
    pass
''', [('neutralise([2, 1], [0, 0], [0.6, 0.8])', [0.8, -0.6]), ('neutralise([3, -0.8], [0, -1], [0, 1])', [3.0, 0.0]), ('neutralise([1, 2, 3], [0, 0, 0], [0, 0, 5])', [1.0, 2.0, 0.0])],
         '''
def neutralise(v, a, b):
    d = [y - x for x, y in zip(a, b)]
    n = sum(t * t for t in d) ** 0.5
    g = [t / n for t in d]
    p = sum(x * y for x, y in zip(v, g))
    return [round(x - p * y, 4) for x, y in zip(v, g)]
''', 'Normalise the direction before projecting.', '<p>The third test removes the whole z component, because g points along z.</p>')

K.must('Intrinsic and extrinsic', 'Intrinsic: fast subtasks (relatedness with Spearman, analogy, categorisation with purity, selectional preference). Extrinsic: score of a real task.')
K.must('Using pre-trained vectors', 'Fixed (fewer parameters, no adaptation), fine-tuned (adapts, may forget), concatenated (both, bigger). No embedding wins on every test.')
K.must('Subwords', 'fastText: v<sub>w</sub> = sum of character n-gram vectors with marks &lt; &gt;, n = 3 to 6. "where" has 14 n-grams. Handles rare and unseen words.')
K.must('Cross-lingual', 'Map spaces with W, often orthogonal (Procrustes W = UV<sup>T</sup>). Anchors: a dictionary, identical strings (Artetxe) or none (adversarial, Zhang).')
K.must('Sparsity and bias', 'Sparse: add λ‖w‖₁. Debias: bias direction g from pairs, neutralise v′ = v − (v·g)g, then equalise. Bias is reduced, not removed.')

T = K.topic(
    slug='evaluate-improve-embeddings', topic='nn-evaluate-embeddings', step=(2, 'Word vectors', 'nn-vectors', 'Turn words into vectors that capture meaning: one-hot vectors and their limits, word2vec with softmax and negative sampling, co-occurrence counts, GloVe, and how to test and improve embeddings.', 'College'),
    title='Evaluating and improving embeddings', short='Evaluate and improve', badge='2.5', minutes=45, added='2026-11-01',
    lead='Test embeddings with similarity, analogies and real tasks, then fix their weak spots: fastText subwords, cross-lingual alignment, sparse vectors and debiasing.',
    desc='Intrinsic against extrinsic evaluation, relatedness with Spearman correlation, analogies, categorisation purity and selectional preference, fixed, fine-tuned and concatenated pre-trained vectors, character and n-gram subword models with fastText, cross-lingual mapping and Procrustes, sparse L1 embeddings and the projection debiasing of Bolukbasi et al.',
    summary='Intrinsic and extrinsic tests, fastText n-grams, cross-lingual mapping, sparse embeddings and debiasing.',
    keywords=['intrinsic evaluation', 'extrinsic evaluation', 'Spearman', 'analogy', 'fastText', 'cross-lingual', 'debiasing', 'sparse embeddings'],
    recap='<p>Good embeddings score well on intrinsic tests and, more importantly, on real tasks. Character n-grams fix rare and unseen words, a rotation aligns languages, an L1 penalty makes axes readable, and projecting out a bias direction reduces stereotypes.</p>')
