# NLP section, chapter 2.1: from symbols to word vectors. Source: FoVL lecture 2 slides 2 to 6 (one-hot vectors of
# size 500,000+, "Seattle motel" against "Seattle hotel", orthogonality, why WordNet synonym lists fail, distributional
# semantics and Firth 1957, the banking contexts, the 8 number banking and monetary vectors, embeddings as a
# distributed representation) and the lecture 2 recording.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('onehot', r'''
# One-hot vectors: every pair of different words has dot product 0
vocab = ["hotel", "motel", "banking", "monetary", "banana"]

def one_hot(word):
    return [1 if w == word else 0 for w in vocab]

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

print("hotel =", one_hot("hotel"))
print("motel =", one_hot("motel"))
print("hotel . motel =", dot(one_hot("hotel"), one_hot("motel")))
print("hotel . hotel =", dot(one_hot("hotel"), one_hot("hotel")))
''')

K.code('cosine', r'''
# The two dense vectors from the slide
import math
banking  = [0.286, 0.792, -0.177, -0.107, 0.109, -0.542, 0.349, 0.271]
monetary = [0.413, 0.582, -0.007, 0.247, 0.216, -0.718, 0.147, 0.051]

dot = sum(a * b for a, b in zip(banking, monetary))
nb = math.sqrt(sum(a * a for a in banking))
nm = math.sqrt(sum(b * b for b in monetary))
print("dot    =", round(dot, 4))
print("norms  =", round(nb, 4), round(nm, 4))
print("cosine =", round(dot / (nb * nm), 4))
''')

K.code('contexts', r'''
# Collect the context words of "banking" within a window of 2, from the three slide sentences
sents = ["government debt problems turning into banking crises as happened in 2009",
         "saying that Europe needs unified banking regulation to replace the hodgepodge",
         "India has just given its banking system a shot in the arm"]
m = 2
ctx = []
for s in sents:
    w = s.split()
    i = w.index("banking")
    ctx += w[max(0, i - m):i] + w[i + 1:i + 1 + m]
print(ctx)
''')

K.lesson('symbols', 'Words as symbols: the one-hot problem', f'''
<p>Traditional NLP treats each word as a separate symbol. In a vector this becomes a one-hot vector: a 1 in the word’s own position and 0 everywhere else. The length of the vector is the size of the vocabulary, which for real text is 500,000 or more.</p>
{fxs(fx('One-hot vector', 'motel = [0 0 0 0 0 0 0 0 0 0 1 0 0 0 0] &nbsp; hotel = [0 0 0 0 0 0 0 1 0 0 0 0 0 0 0]', 'A localist representation: one position means one word.'),
     fx('Every pair is orthogonal', 'hotel · motel = 0 &nbsp; and &nbsp; ‖hotel − motel‖ = √2', 'All different words are equally far apart, so the vectors carry no similarity at all.', key=True))}
{code('onehot')}
{scene('web search', '<p>Someone searches for "Seattle motel". A page about a "Seattle hotel" would be just as useful, but with one-hot vectors the words hotel and motel share nothing, so the search engine sees no match. The slide uses this exact example.</p>')}
<p>Could we fix this with a hand made thesaurus such as WordNet? The lecture lists why that fails: synonym lists are incomplete and miss new words, similarity is not just yes or no, and the meaning of a word changes with its context.</p>
{note('One-hot vectors are not useless. They are how a word enters a network: multiplying a one-hot vector by an embedding matrix simply picks out one row. That lookup is the first step of word2vec.', 'tip')}
''', kw=['one-hot', 'localist representation', 'orthogonal', 'WordNet', 'sparse vector'])

K.lesson('context', 'You shall know a word by the company it keeps', f'''
<p>Distributional semantics is the idea that the meaning of a word is given by the words that often appear near it. J. R. Firth said it in 1957. It is one of the most successful ideas in modern statistical NLP, and every model in this section is built on it.</p>
{fxs(fx('Context of a word', 'context(<i>w</i>) = the words within a window of ±<i>m</i> positions around each occurrence of <i>w</i>', 'Many occurrences give many contexts. Together they describe the word.'))}
{table(['Left context', 'Word', 'Right context'], [['problems turning into', '<b>banking</b>', 'crises as happened'], ['Europe needs unified', '<b>banking</b>', 'regulation to replace'], ['given its', '<b>banking</b>', 'system a shot']])}
{code('contexts')}
{viz('sgwindow')}
{ladder(
    '<p>If you hear an unknown word used with "spoon", "plate" and "hungry", you guess it is about food. Computers do the same by looking at neighbour words.</p>',
    '<p>The distributional hypothesis says words in similar contexts have similar meanings. Count based methods (co-occurrence matrices) and prediction based methods (word2vec) both turn context statistics into vectors.</p>',
    '<p>Formally, skip-gram with negative sampling implicitly factorises a shifted pointwise mutual information matrix, PMI(w, c) − log k (Levy and Goldberg, 2014), so prediction and counting are two views of one quantity.</p>',
    '<p>Static vectors give one point per word type, so the two senses of bank share a vector. Contextual models (ELMo, BERT) compute a new vector for every occurrence, and probing studies ask what linguistic structure those vectors encode.</p>')}
''', kw=['distributional semantics', 'Firth', 'context window', 'context words', 'co-occurrence'])

K.lesson('vectors', 'Dense word vectors and cosine similarity', f'''
<p>Instead of one huge sparse vector we give each word a short dense vector, for example 8 or 300 numbers, chosen so that words in similar contexts get similar vectors. These are called word vectors, word embeddings or neural word representations. Meaning is spread over all the numbers, a distributed representation.</p>
{fxs(fx('Dot product', '<b>a</b> · <b>b</b> = ∑<sub>i</sub> a<sub>i</sub>b<sub>i</sub>', 'Large when the vectors point the same way. Word2vec uses it directly as a similarity score.', key=True),
     fx('Cosine similarity', 'cos(<b>a</b>, <b>b</b>) = ' + frac('<b>a</b> · <b>b</b>', '‖<b>a</b>‖ ‖<b>b</b>‖'), '1 for the same direction, 0 for unrelated, −1 for opposite. It ignores vector length.', key=True))}
{viz('onehot')}
{steps('Worked example: banking against monetary from the slide', [
    'banking = (0.286, 0.792, −0.177, −0.107, 0.109, −0.542, 0.349, 0.271).',
    'monetary = (0.413, 0.582, −0.007, 0.247, 0.216, −0.718, 0.147, 0.051).',
    'Dot product = 1.0317. Lengths ‖banking‖ = 1.1193 and ‖monetary‖ = 1.0755.',
    eq('cos = 1.0317 ÷ (1.1193 × 1.0755) = 0.857, close in meaning')])}
{code('cosine')}
{deep('why the dot product and not the distance', '<p>For unit length vectors the two agree: ‖a − b‖² = 2 − 2 cos(a, b). Word2vec scores with the raw dot product, which also grows with vector length, and frequent words tend to get longer vectors. That is why similarity is reported with cosine, which removes length. In high dimensions random vectors are almost orthogonal, so a cosine of 0.86 between two 300 dimensional vectors is a very strong signal.</p>')}
{note('Cosine similarity is not a probability and can be negative. Do not compare a cosine with a probability.', 'warn')}
''', kw=['word vector', 'embedding', 'dense vector', 'cosine similarity', 'dot product', 'distributed representation'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'A one-hot vector for a vocabulary of 50,000 words has how many 1s?', ['0', '1', '2', '50,000'], 1, 'One hot.', 'Exactly one position is 1.')
K.quiz('e', 'The dot product of the one-hot vectors of hotel and motel is', ['1', '0', '0.5', '−1'], 1, 'No shared position.', 'They are orthogonal.')
K.quiz('e', '"You shall know a word by the company it keeps" was said by', ['Turing', 'Firth', 'Chomsky', 'Shannon'], 1, '1957.', 'J. R. Firth.')
K.quiz('e', 'Another name for a word vector is', ['a token', 'a word embedding', 'a parse tree', 'a lemma'], 1, 'Slide note.', 'Word vectors are also called embeddings or neural word representations.')
K.quiz('m', 'Why does WordNet not solve word similarity?', ['It is too small to download', 'Synonym lists are incomplete, similarity is graded and context changes meaning', 'It is only in French', 'It uses one-hot vectors'], 1, 'Three reasons on the slide.', 'Hand made lists cannot keep up and are all or nothing.')
K.quiz('m', 'Cosine similarity of (1, 2) and (2, 4) is', ['0', '0.5', '1', '2'], 2, 'Same direction.', 'One is twice the other, so the angle is 0.')
K.quiz('m', 'A distributed representation means', ['each dimension is one word', 'meaning is spread across many dimensions', 'the vector is stored on many computers', 'the vector is random'], 1, 'Opposite of localist.', 'No single number means "money". The pattern does.')
K.quiz('m', 'Which pair should have the highest cosine in good embeddings?', ['banking and skillet', 'banking and monetary', 'banking and banana', 'banking and the'], 1, 'Similar contexts.', 'Both appear near finance words.')
K.quiz('h', 'The Euclidean distance between any two different one-hot vectors is', ['0', '1', '√2', 'the vocabulary size'], 2, 'Two positions differ by 1.', '√(1² + 1²) = √2, the same for every pair.')
K.quiz('h', 'For unit vectors a and b, ‖a − b‖² equals', ['cos(a, b)', '2 − 2 cos(a, b)', '1 − cos(a, b)', 'a · b'], 1, 'Expand the square.', '‖a‖² + ‖b‖² − 2a·b = 2 − 2 cos.')
K.quiz('h', 'Multiplying a one-hot vector by an embedding matrix', ['adds all rows', 'selects one row, the word’s vector', 'gives a probability', 'normalises the matrix'], 1, 'Only one 1.', 'It is a table lookup.')
K.quiz('x', 'Levy and Goldberg showed that skip-gram with negative sampling implicitly factorises', ['the identity matrix', 'a shifted PMI matrix, PMI − log k', 'the adjacency matrix of WordNet', 'the one-hot matrix'], 1, 'Counting meets predicting.', 'The optimum satisfies u·v = PMI(w, c) − log k.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Vocabulary of 500,000 words. How many numbers are in one one-hot vector?', '500000', 'Length = vocabulary size.', ['One position per word.', 'All but one are 0.', eq('500,000')], check=500000, tol=1e-9)
K.calc('e', 'Dot product of (1, 2, 0) and (0, 1, 3)?', '2', 'Multiply position by position and add.', ['1 × 0 = 0.', '2 × 1 = 2, 0 × 3 = 0.', eq('2')], check=2, tol=1e-9)
K.calc('e', 'Cosine of (1, 0) and (0, 1)?', '0', 'Dot product first.', ['Dot = 0.', 'Both lengths are 1.', eq('cos = 0, unrelated')], check=0, tol=1e-9)
K.calc('m', 'Cosine of (3, 4) and (4, 3). Two decimals.', '0.96', 'Lengths are 5.', ['Dot = 12 + 12 = 24.', 'Lengths 5 and 5.', eq('cos = 24 ÷ 25 = 0.96')], check=0.96, tol=1e-9)
K.calc('m', 'Dot product of the slide vectors banking and monetary. Four decimals.', '1.0317', 'Eight products.', ['0.286 × 0.413 + 0.792 × 0.582 = 0.1181 + 0.4609.', 'Add the other six products: 0.0012 − 0.0264 + 0.0235 + 0.3892 + 0.0513 + 0.0138.', eq('dot = 1.0317')], check=1.031696, tol=5e-5)
K.calc('m', 'Cosine of banking and monetary. Three decimals.', '0.857', 'Divide by both lengths.', ['‖banking‖ = 1.1193.', '‖monetary‖ = 1.0755.', eq('1.0317 ÷ 1.2038 = 0.857')], check=0.8570493105815337, tol=5e-4)
K.calc('m', 'Distance between two different one-hot vectors. Four decimals.', '1.4142', '√2.', ['They differ in two places.', 'Each difference is 1.', eq('√2 = 1.4142')], check=2 ** 0.5, tol=5e-5)
K.calc('h', 'A sentence of 8 words, window 2 on each side. How many (centre, context) pairs?', '26', 'Edge words have fewer neighbours.', ['Words 1 and 8 have 2 neighbours each, words 2 and 7 have 3.', 'Words 3 to 6 have 4 each: 16.', eq('2 + 3 + 16 + 3 + 2 = 26')], check=26, tol=1e-9)
K.calc('h', 'In "problems turning into banking crises as", how many context words does banking have with window 2?', '4', 'Two left, two right.', ['Left: turning, into.', 'Right: crises, as.', eq('4')], check=4, tol=1e-9)
K.calc('h', 'V = 10,000 and d = 300. How many numbers does a table of dense vectors need, against a table of one-hot vectors?', '3000000', 'V × d for dense.', ['Dense: 10,000 × 300 = 3,000,000.', 'One-hot: 10,000 × 10,000 = 100,000,000.', eq('3,000,000, about 33 times less')], check=3000000, tol=1e-9)
K.calc('x', 'Unit vectors a and b have cosine 0.857. What is ‖a − b‖? Three decimals.', '0.535', '‖a − b‖² = 2 − 2cos.', ['2 − 2 × 0.857 = 0.286.', 'Square root.', eq('‖a − b‖ = 0.535')], check=(2 - 2 * 0.857) ** 0.5, tol=5e-4)

# ---------------------------------------------------------------- assignments
K.assign('onehot', 'e', 'Build one-hot vectors',
         '<p>Write <code>one_hot(word, vocab)</code> returning a list with 1 at the position of word in vocab and 0 elsewhere. Write <code>dot(a, b)</code> as well.</p>',
         '''
def one_hot(word, vocab):
    pass

def dot(a, b):
    pass
''', [('one_hot("motel", ["hotel", "motel", "inn"])', [0, 1, 0]), ('dot(one_hot("hotel", ["hotel", "motel"]), one_hot("motel", ["hotel", "motel"]))', 0), ('dot([1, 2, 3], [4, 5, 6])', 32)],
         '''
def one_hot(word, vocab):
    return [1 if w == word else 0 for w in vocab]

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))
''', 'A list comprehension does it in one line.', '<p>Different words always give dot product 0.</p>')
K.assign('cos', 'm', 'Cosine similarity and the nearest word',
         '<p>Write <code>cosine(a, b)</code> rounded to 4 decimals and <code>nearest(word, vecs)</code> where vecs is a dict from word to vector. Return the other word with the highest cosine.</p>',
         '''
import math

def cosine(a, b):
    pass

def nearest(word, vecs):
    pass
''', [('cosine([3, 4], [4, 3])', 0.96), ('nearest("hotel", {"hotel": [0.8, 0.6], "motel": [0.75, 0.65], "banana": [-0.6, 0.5]})', 'motel'), ('cosine([1, 0], [-1, 0])', -1.0)],
         '''
import math

def cosine(a, b):
    d = sum(x * y for x, y in zip(a, b))
    return round(d / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))), 4)

def nearest(word, vecs):
    return max((w for w in vecs if w != word), key=lambda w: cosine(vecs[word], vecs[w]))
''', 'Leave the word itself out, or it would always be its own nearest neighbour.', '<p>This is the similar_words function of the class notebook.</p>')
K.assign('ctx', 'h', 'Context counts',
         '<p>Write <code>contexts(sentences, word, m)</code> that returns a dict from each context word to how many times it appears within m positions of word, over all sentences (lists of tokens).</p>',
         '''
def contexts(sentences, word, m):
    pass
''', [('contexts([["cats", "like", "milk"], ["dogs", "like", "milk"]], "like", 1)', {'cats': 1, 'milk': 2, 'dogs': 1}),
      ('contexts([["a", "b", "a", "c"]], "a", 1)', {'b': 2, 'c': 1}), ('contexts([["x"]], "y", 2)', {})],
         '''
def contexts(sentences, word, m):
    out = {}
    for s in sentences:
        for i, w in enumerate(s):
            if w != word:
                continue
            for j in range(max(0, i - m), min(len(s), i + m + 1)):
                if j != i:
                    out[s[j]] = out.get(s[j], 0) + 1
    return out
''', 'Two loops: over the occurrences, then over the window.', '<p>These counts are one row of the co-occurrence matrix of chapter 2.4.</p>')

K.must('One-hot', 'Length = vocabulary size (500,000+), one 1. Every pair is orthogonal (dot 0, distance √2), so one-hot vectors carry no similarity.')
K.must('Distributional semantics', 'A word’s meaning comes from the words near it (Firth 1957). Context = words within ±m positions.')
K.must('Word vectors', 'Dense, short, learned so that words in similar contexts get similar vectors. Also called embeddings. A distributed representation.')
K.must('Similarity', 'Dot product and cosine = a·b ÷ (‖a‖‖b‖). banking against monetary: cosine 0.857.')
K.must('WordNet fails', 'Incomplete synonym lists, similarity is graded not binary, and context changes meaning.')

T = K.topic(
    slug='word-meaning', topic='nn-word-meaning', step=(2, 'Word vectors', 'nn-vectors', 'Turn words into vectors that capture meaning: one-hot vectors and their limits, word2vec with softmax and negative sampling, co-occurrence counts, GloVe, and how to test and improve embeddings.', 'College'),
    title='From symbols to word vectors', short='Word meaning', badge='2.1', minutes=30, added='2026-11-01',
    lead='Find out why one-hot vectors cannot say that hotel and motel are alike, and how the company a word keeps gives it a dense vector whose direction carries meaning.',
    desc='One-hot vectors and orthogonality, the Seattle motel problem, why WordNet fails, distributional semantics and Firth, context windows, dense word vectors, dot product and cosine similarity with the banking and monetary vectors from the slide.',
    summary='One-hot vectors, distributional semantics, context windows, dense embeddings and cosine similarity.',
    keywords=['one-hot', 'distributional semantics', 'word vector', 'embedding', 'cosine similarity', 'Firth'],
    recap='<p>One-hot vectors make every word equally far from every other. Distributional semantics replaces them with dense vectors learned from neighbouring words, and cosine similarity measures how close two meanings are.</p>')
