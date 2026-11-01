# NLP section, chapter 3.1: language models, the fixed window neural model and recurrent neural networks. Source: FoVL
# lecture 3 slides 1 to 50 and 70 to 72 (language modelling as next word prediction, n-grams and the Markov assumption,
# the 4-gram example with "students opened their" seen 1000 times, sparsity with smoothing and backoff, storage,
# generating "today the price of gold ...", composition functions, the fixed window model of Bengio et al. 2003 and its
# three problems, the simple RNN language model, the 96 parameter exercise, the cross-entropy examples 0.51 and 2.99,
# teacher forcing, sentence level SGD, autoregressive generation and perplexity 1.44 against 4.07).
from cvkit import Kit, fx, fxs, frac, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('bigram', r'''
# A count based n-gram model: P(w | context) = count(context w) / count(context)
text = "the students opened their books . the students opened their exams . the students opened their books ."
w = text.split()
def count(seq):
    n = len(seq)
    return sum(1 for i in range(len(w) - n + 1) if w[i:i + n] == seq)

ctx = ["students", "opened", "their"]
for nxt in ["books", "exams", "laptops"]:
    print("P(" + nxt + " | students opened their) =", count(ctx + [nxt]), "/", count(ctx), "=", round(count(ctx + [nxt]) / count(ctx), 4))
V = len(set(w))
print("add-one smoothing for laptops:", round((count(ctx + ["laptops"]) + 1) / (count(ctx) + V), 4), "with V =", V)
''')

K.code('rnn', r'''
# A one number RNN: h_t = tanh(w_h h_(t-1) + w_x x_t + b), and the gradient of h_T with respect to h_1
import math
wh, wx, b = 0.9, 1.0, 0.0
xs = [1, 0, 0, 0, 0]
h, hs = 0.0, []
for x in xs:
    h = math.tanh(wh * h + wx * x + b)
    hs.append(h)
print("states:", [round(v, 4) for v in hs])
g = 1.0
for t in range(1, len(hs)):
    g *= wh * (1 - hs[t] ** 2)       # chain rule through one step: w_h times tanh'
print("d h_5 / d h_1 =", round(g, 5))
''')

K.code('ppl', r'''
# Cross-entropy and perplexity of one sentence
import math
p_true = [0.6, 0.3, 0.5, 0.4]       # probability the model gave each correct next word
losses = [-math.log(p) for p in p_true]
J = sum(losses) / len(losses)
print("losses:", [round(x, 4) for x in losses])
print("J =", round(J, 4), " perplexity = exp(J) =", round(math.exp(J), 4))
print("uniform over 4 words:", round(math.exp(-math.log(0.25)), 4))
''')

K.lesson('ngram', 'Language models and n-grams', f'''
<p>A language model predicts what word comes next. Given "the students opened their", it gives a probability to every word of the vocabulary: books, laptops, exams, minds. Equivalently, it assigns a probability to a whole piece of text. You use one every day in phone keyboards and search suggestions, and ChatGPT is a language model too.</p>
{fxs(fx('Next word distribution', 'P(x<sup>(t+1)</sup> | x<sup>(t)</sup>, ..., x<sup>(1)</sup>)', 'x<sup>(t+1)</sup> can be any word of the vocabulary V.', key=True),
     fx('Probability of a text (chain rule)', 'P(x<sup>(1)</sup>, ..., x<sup>(T)</sup>) = ∏<sub>t=1</sub><sup>T</sup> P(x<sup>(t)</sup> | x<sup>(t−1)</sup>, ..., x<sup>(1)</sup>)', 'Exact. Every model below approximates the conditional terms.'),
     fx('n-gram (Markov) assumption', 'P(x<sup>(t+1)</sup> | x<sup>(t)</sup>, ..., x<sup>(1)</sup>) ≈ P(x<sup>(t+1)</sup> | x<sup>(t)</sup>, ..., x<sup>(t−n+2)</sup>) ≈ ' + frac('count(x<sup>(t−n+2)</sup> ... x<sup>(t+1)</sup>)', 'count(x<sup>(t−n+2)</sup> ... x<sup>(t)</sup>)'), 'Only the last n − 1 words matter. Probabilities come from counting.', key=True))}
{steps('The lecture 4-gram example', [
    'Text: "as the proctor started the clock, the students opened their ___". A 4-gram model keeps only the last 3 words, "students opened their", and discards the rest.',
    '"students opened their" occurred 1000 times. "students opened their books" occurred 400 times.',
    eq('P(books | students opened their) = 400 ÷ 1000 = 0.4'),
    '"students opened their exams" occurred 100 times, so P(exams | ...) = 0.1. The discarded word "proctor" was a strong hint for exams.'])}
{code('bigram')}
{table(['Problem', 'What goes wrong', 'Partial fix'], [['Sparsity 1', 'the full n-gram never occurred, so a valid word gets probability 0', 'smoothing: add a small δ to every count'], ['Sparsity 2', 'the context never occurred, so nothing can be computed', 'backoff: condition on fewer words, "opened their"'], ['Storage', 'every seen n-gram must be stored', 'none: bigger n or corpus means a bigger model'], ['Short context', 'n above 5 makes sparsity much worse', 'move to neural models']])}
<p>Sampling from a trigram model trained on news gives text such as "today the price of gold per ton , while production of shoe lasts and shoe industry , the bank intervened ...". It is surprisingly grammatical but incoherent, because three words of context are not enough.</p>
{fxs(fx('Add-one (Laplace) smoothing', 'P(w | c) = ' + frac('count(c, w) + 1', 'count(c) + |V|'), 'No probability is ever 0. With δ instead of 1 it is add-δ smoothing.'))}
{note('Questions often ask for an n-gram probability from counts and then what happens when a count is 0. Say "sparsity", name smoothing and backoff, and give the Markov assumption.', 'exam')}
''', kw=['language model', 'n-gram', 'Markov assumption', 'sparsity', 'smoothing', 'backoff'])

K.lesson('window', 'A fixed window neural language model', f'''
<p>Bengio and others (2003) replaced counting with a neural network. Take the last few words, look up their embeddings, concatenate them, pass them through a hidden layer and finish with a softmax over the vocabulary. The prefix is turned into one vector by a composition function. Choices include a sum of embeddings, concatenation, a feed-forward network, a CNN, an RNN or a transformer.</p>
{fxs(fx('Fixed window model', 'e = [e<sup>(1)</sup>, e<sup>(2)</sup>, e<sup>(3)</sup>, e<sup>(4)</sup>], &nbsp; h = f(We + b₁), &nbsp; ŷ = softmax(Uh + b₂)', 'e<sup>(i)</sup> is the embedding of the i-th window word. ŷ is a distribution over V.', key=True),
     fx('Output matrix shape', 'U ∈ ℝ<sup>|V| × d<sub>h</sub></sup>', 'One row per vocabulary word. Row w scores how well the prefix fits word w.'))}
{table(['Improvement over n-grams', 'Remaining problem'], [['no sparsity problem: every word gets a probability', 'the fixed window is too small'], ['no need to store all observed n-grams', 'enlarging the window enlarges W'], ['similar words share similar embeddings', 'x<sup>(1)</sup> and x<sup>(2)</sup> are multiplied by different parts of W, so there is no symmetry']])}
{steps('Why "no symmetry" matters', [
    '"the students opened their" and "yesterday students opened their" mean nearly the same.',
    'In the first, "students" is in slot 2 and meets the weights W₂. In the second it is in slot 3 and meets W₃.',
    'The model must learn "students in slot 2", "students in slot 3" and "students in slot 4" as separate patterns.',
    eq('No parameter sharing, so learning does not transfer across positions and more data is needed')])}
{steps('Count the parameters of a fixed window model', [
    'V = 10,000, embeddings d = 100, window 4, hidden size 500, biases ignored.',
    'Embeddings E: 10,000 × 100 = 1,000,000. W: 500 × (4 × 100) = 200,000.',
    'U: 10,000 × 500 = 5,000,000.',
    eq('Total = 6,200,000, most of it in the output layer')])}
{scene('predictive text on a phone', '<p>Early phone keyboards used n-gram counts and suggested only words they had seen after the last two words. A neural model can suggest "laptops" after "opened their" even if that exact phrase was rare, because "laptops" has an embedding close to "books".</p>')}
''', kw=['fixed window', 'Bengio', 'neural language model', 'composition function', 'parameter sharing'])

K.lesson('rnn', 'Recurrent neural networks', f'''
<p>A recurrent neural network reads one word at a time and keeps a hidden state, a running summary of everything so far. The core idea is to apply the same weights at every step. That handles any input length, and the model size does not grow with the context.</p>
{fxs(fx('RNN hidden state', 'h<sup>(t)</sup> = σ(W<sub>h</sub> h<sup>(t−1)</sup> + W<sub>e</sub> e<sup>(t)</sup> + b₁)', 'h<sup>(0)</sup> is the initial state. σ is usually tanh. W<sub>h</sub> and W<sub>e</sub> are shared across time.', key=True),
     fx('RNN output', 'ŷ<sup>(t)</sup> = softmax(U h<sup>(t)</sup> + b₂) ∈ ℝ<sup>|V|</sup>', 'The distribution over the next word after step t.', key=True),
     fx('Parameters (no biases, one-hot input)', '|V| d<sub>h</sub> + d<sub>h</sub>² + d<sub>h</sub> |V|', 'Input to hidden, hidden to hidden, hidden to output.'))}
{viz('rnnunroll')}
{code('rnn')}
{table(['RNN advantages', 'RNN disadvantages'], [['any input length', 'recurrent computation is slow, steps cannot run in parallel'], ['step t can in theory use information from many steps back', 'in practice it is hard to use information from many steps back'], ['model size does not grow with the context', ''], ['the same weights at every step, so inputs are treated symmetrically', '']])}
{steps('The lecture exercise: 96 parameters', [
    'Vocabulary {I, he, go, walk, eat}, one-hot input of size 5, hidden size 6, no biases.',
    'Input to hidden W<sub>xh</sub>: 5 × 6 = 30. Hidden to hidden W<sub>hh</sub>: 6 × 6 = 36.',
    'Hidden to output W<sub>hy</sub>: 6 × 5 = 30.',
    eq('30 + 36 + 30 = 96')])}
{viz('paramcount')}
{note('The RNN parameter count never depends on the sentence length T. A common wrong answer multiplies by T.', 'warn')}
''', kw=['RNN', 'hidden state', 'parameter sharing', 'unrolling', '96 parameters'])

K.lesson('training', 'Training: cross-entropy and teacher forcing', f'''
<p>Train an RNN language model on a big corpus. At every step t the model outputs a distribution ŷ<sup>(t)</sup>, and the loss is the cross-entropy with the true next word x<sup>(t+1)</sup>. Because the target is one-hot, the cross-entropy is just minus the log of the probability given to the correct word.</p>
{fxs(fx('Loss at step t', 'J<sup>(t)</sup>(θ) = −∑<sub>w ∈ V</sub> y<sub>w</sub><sup>(t)</sup> log ŷ<sub>w</sub><sup>(t)</sup> = −log ŷ<sup>(t)</sup><sub>x<sup>(t+1)</sup></sub>', 'Only the true word counts.', key=True),
     fx('Overall loss', 'J(θ) = ' + frac('1', 'T') + ' ∑<sub>t=1</sub><sup>T</sup> J<sup>(t)</sup>(θ)', 'An average over all steps, in practice over a batch of sentences.', key=True),
     fx('Backpropagation through time', frac('∂J<sup>(t)</sup>', '∂W<sub>h</sub>') + ' = ∑<sub>i=1</sub><sup>t</sup> ' + frac('∂J<sup>(t)</sup>', '∂W<sub>h</sub>') + '|<sub>(i)</sub>', 'W<sub>h</sub> is used at every step, so its gradient is the sum of the gradients at each use.'))}
{steps('The two slide examples', [
    'Gold [0, 1, 0, 0], predicted [0.1, 0.6, 0.2, 0.1]: the true word got 0.6.',
    eq('J = −ln 0.6 = 0.51'),
    'Predicted [0.4, 0.3, 0.05, 0.25] and the true word got 0.05 (it must be the third word for the slide value).',
    eq('J = −ln 0.05 = 2.99, a strong penalty for being confidently wrong'),
    'If the gold were still the second word, the loss would be −ln 0.3 = 1.20. Always read which word is gold.'])}
{viz('celoss')}
<p>Teacher forcing: during training the input at step t + 1 is the true word from the corpus, not the word the model predicted. The losses for "students", "opened", "their" and "exams" are added and averaged. Computing over the whole corpus at once is too expensive, so we use stochastic gradient descent on a sentence or a batch of sentences.</p>
{note('Why cross-entropy: logs turn products of probabilities into sums, confident wrong answers are penalised hard, and the gradient with softmax is simply ŷ − y, which is stable.', 'tip')}
{deep('exposure bias', '<p>Teacher forcing means the model never sees its own mistakes during training, but at generation time it must continue from its own outputs. This mismatch is called exposure bias. Scheduled sampling (Bengio et al. 2015) gradually replaces gold inputs with model samples during training.</p>')}
''', kw=['cross-entropy', 'teacher forcing', 'BPTT', 'SGD', '0.51 and 2.99'])

K.lesson('perplexity', 'Perplexity and generating text', f'''
<p>The standard metric for language models is perplexity: the inverse probability of the corpus, normalised by the number of words. It equals the exponential of the cross-entropy loss. Lower is better.</p>
{fxs(fx('Perplexity', 'PP = ∏<sub>t=1</sub><sup>T</sup> (' + frac('1', 'P<sub>LM</sub>(x<sup>(t+1)</sup> | x<sup>(t)</sup>, ..., x<sup>(1)</sup>)') + ')<sup>1/T</sup> = exp(J(θ))', 'J is the average cross-entropy in natural logs.', key=True),
     fx('Meaning', 'PP = k ⇔ the model is as unsure as a uniform choice among k words', 'A perfect model has PP = 1. Guessing uniformly over V gives PP = |V|.'))}
{table(['Perplexity', 'Interpretation from the slide'], [['1.44', 'on average the model chooses between about 1.44 words: confident and mostly right'], ['4.07', 'the model is confused, almost guessing among 4 words']])}
{code('ppl')}
<p>Generation is autoregressive: feed a start token, sample a word from ŷ<sup>(1)</sup>, feed that word back as the next input, and repeat. RNNs serve three uses from the slides: text generation, sequence labelling (one output per word) and text classification (one output per sentence).</p>
{ladder(
    '<p>A language model guesses the next word. Old models counted short word groups. An RNN reads words one by one and keeps a memory, so it can use more of the sentence.</p>',
    '<p>An RNN applies the same weights at every step: h<sup>(t)</sup> = tanh(W<sub>h</sub>h<sup>(t−1)</sup> + W<sub>e</sub>e<sup>(t)</sup>). It is trained with the average cross-entropy using teacher forcing, and measured with perplexity = exp(J).</p>',
    '<p>The gradient through time is a product of Jacobians W<sub>h</sub><sup>T</sup>diag(tanh′). When their norms are below 1 it vanishes, above 1 it explodes. That limits how far back an RNN can learn, which motivates LSTM and GRU in chapter 3.3.</p>',
    '<p>Perplexity on benchmarks such as Penn Treebank fell from about 140 for n-gram models to about 80 with LSTMs and below 20 for large transformers on bigger corpora. Perplexity is only comparable between models with the same vocabulary and tokenisation.</p>')}
''', kw=['perplexity', 'exp of cross-entropy', 'autoregressive generation', '1.44 and 4.07'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'A language model', ['translates text', 'predicts the next word', 'tags parts of speech', 'removes stop words'], 1, 'Slide 2.', 'It gives a distribution over the next word.')
K.quiz('e', 'A 4-gram model conditions on', ['1 word', '3 words', '4 words', 'the whole sentence'], 1, 'n − 1.', 'It keeps the last 3 words.')
K.quiz('e', 'Adding a small number to every count is called', ['backoff', 'smoothing', 'pruning', 'dropout'], 1, 'Sparsity problem 1.', 'Smoothing stops probabilities from being 0.')
K.quiz('e', 'Lower perplexity means', ['a worse model', 'a better model', 'a longer text', 'more parameters'], 1, 'Inverse probability.', 'The model is less surprised by the real text.')
K.quiz('m', 'Using "opened their" when "students opened their" was never seen is', ['smoothing', 'backoff', 'teacher forcing', 'beam search'], 1, 'Sparsity problem 2.', 'Back off to a shorter context.')
K.quiz('m', 'Which problem of the fixed window model does an RNN fix?', ['softmax cost', 'different weights for different positions', 'the need for embeddings', 'the need for training data'], 1, 'Symmetry.', 'The RNN uses the same weights at every step.')
K.quiz('m', 'One-hot input 5, hidden 6, no biases. RNN language model parameters?', ['66', '72', '96', '102'], 2, '5×6 + 6×6 + 6×5.', '30 + 36 + 30 = 96.')
K.quiz('m', 'Teacher forcing means', ['the teacher labels the data', 'the true previous word is fed as input during training', 'the model is trained on generated text', 'gradients are clipped'], 1, 'Slide 45.', 'Gold words are inputs, not model predictions.')
K.quiz('m', 'The true word got probability 0.6. Cross-entropy?', ['0.22', '0.51', '0.60', '2.99'], 1, '−ln 0.6.', '0.511.')
K.quiz('h', 'Perplexity 1.44 corresponds to an average cross-entropy (natural log) of about', ['0.36', '0.69', '1.44', '4.07'], 0, 'ln PP.', 'ln 1.44 = 0.365.')
K.quiz('h', 'Why does the RNN parameter count not depend on sentence length?', ['sentences are padded', 'the same matrices are reused at every step', 'the hidden size grows', 'gradients are averaged'], 1, 'Weight sharing.', 'Unrolling copies the computation, not the weights.')
K.quiz('h', 'The gradient of W<sub>h</sub> in backpropagation through time is', ['the gradient at the last step only', 'the sum of its gradients at each time step', 'the average of the hidden states', 'zero'], 1, 'Multivariable chain rule.', 'W<sub>h</sub> appears at every step, so the contributions add.')
K.quiz('x', 'A model that spreads probability uniformly over a 10,000 word vocabulary has perplexity', ['1', '100', '10,000', 'ln 10,000'], 2, 'PP = |V| for uniform.', 'exp(−ln(1 ÷ 10,000)) = 10,000.')

# ---------------------------------------------------------------- worked problems
K.calc('e', '"students opened their" occurs 1000 times and "students opened their books" 400 times. P(books | students opened their)?', '0.4', 'count ratio.',
       ['Numerator 400.', 'Denominator 1000.', eq('0.4')], check=0.4, tol=1e-9)
K.calc('e', 'RNN language model, one-hot input 5, hidden 6, no biases. Number of parameters.', '96', 'Three matrices.',
       ['W<sub>xh</sub> 5 × 6 = 30.', 'W<sub>hh</sub> 6 × 6 = 36, W<sub>hy</sub> 6 × 5 = 30.', eq('96')], check=96, tol=1e-9)
K.calc('e', 'Gold word got probability 0.05. Cross-entropy loss, three decimals.', '2.996', '−ln 0.05.',
       ['ln 0.05 = −2.9957.', 'Negate.', eq('2.99 (2.9957)')], check=2.995732273553991, tol=0.006)
K.calc('m', 'Add-one smoothing: count(context) = 1000, count(context, laptops) = 0, |V| = 10,000. P(laptops | context), four decimals.', '0.0001', '(0 + 1) ÷ (1000 + 10,000).',
       ['Numerator 1.', 'Denominator 11,000.', eq('1 ÷ 11,000 = 0.0000909, about 0.0001')], check=1 / 11000, tol=5e-5)
K.calc('m', 'Same counts with "exams" seen 100 times. Add-one smoothed probability, four decimals.', '0.0092', '(100 + 1) ÷ 11,000.',
       ['Numerator 101.', 'Denominator 11,000.', eq('0.0092, much less than the raw 0.1 because |V| is large')], check=101 / 11000, tol=5e-5)
K.calc('m', 'Probabilities of the true words over a sentence: 0.6, 0.3, 0.5, 0.4. Average cross-entropy, four decimals.', '0.8311', 'Mean of −ln p.',
       ['−ln values: 0.5108, 1.2040, 0.6931, 0.9163.', 'Sum 3.3242.', eq('J = 3.3242 ÷ 4 = 0.8311')], check=0.8310590851315067, tol=5e-4)
K.calc('m', 'Same sentence. Perplexity, three decimals.', '2.296', 'exp(J).',
       ['J = 0.8311.', 'e<sup>0.8311</sup>.', eq('PP = 2.296')], check=2.2957488466614326, tol=5e-3)
K.calc('m', 'Fixed window model: V = 10,000, d = 100, window 4, hidden 500, no biases. Total parameters including the embeddings.', '6200000', 'E + W + U.',
       ['E: 1,000,000.', 'W: 500 × 400 = 200,000. U: 10,000 × 500 = 5,000,000.', eq('6,200,000')], check=6.2e6, tol=0.5)
K.calc('h', 'h<sub>t</sub> = tanh(0.9 h<sub>t−1</sub> + x<sub>t</sub>), h<sub>0</sub> = 0, inputs 1, 0, 0. Compute h<sub>3</sub> to four decimals.', '0.4896', 'Three steps.',
       ['h₁ = tanh(1) = 0.7616.', 'h₂ = tanh(0.6854) = 0.5950.', eq('h₃ = tanh(0.5355) = 0.4896')], check=0.4896, tol=2e-4)
K.calc('h', 'Same RNN. ∂h₃/∂h₁ = w(1 − h₂²) × w(1 − h₃²) with w = 0.9. Four decimals.', '0.3978', 'Product of two step factors.',
       ['Step 2 factor: 0.9 × (1 − 0.5950²) = 0.5814.', 'Step 3 factor: 0.9 × (1 − 0.4896²) = 0.6843.', eq('0.5814 × 0.6843 = 0.3978')], check=0.3977835632753607, tol=5e-4)
K.calc('h', 'With a constant step factor of 0.5, how big is the gradient back over 7 steps? Four decimals.', '0.0078', '0.5<sup>7</sup>.',
       ['Each step multiplies by 0.5.', '7 steps.', eq('0.5<sup>7</sup> = 0.0078, a vanishing gradient')], check=0.5 ** 7, tol=5e-5)
K.calc('x', 'Perplexity 4.07. What average probability (geometric mean) does the model give the true word? Three decimals.', '0.246', '1 ÷ PP.',
       ['PP = 1 ÷ geometric mean of p.', '1 ÷ 4.07.', eq('0.246')], check=1 / 4.07, tol=5e-4)

# ---------------------------------------------------------------- assignments
K.assign('ngram', 'e', 'An n-gram probability by counting',
         '<p>Write <code>ngram_prob(tokens, context, word)</code> that returns count(context + [word]) ÷ count(context) in the token list, rounded to 4 decimals, or 0.0 when the context never occurs.</p>',
         '''
def ngram_prob(tokens, context, word):
    pass
''', [('ngram_prob("a b c a b d a b c".split(), ["a", "b"], "c")', 0.6667), ('ngram_prob("a b c".split(), ["x"], "c")', 0.0), ('ngram_prob("the cat sat the cat ran".split(), ["the"], "cat")', 1.0)],
         '''
def ngram_prob(tokens, context, word):
    def count(seq):
        n = len(seq)
        return sum(1 for i in range(len(tokens) - n + 1) if tokens[i:i + n] == seq)
    c = count(context)
    if c == 0:
        return 0.0
    return round(count(context + [word]) / c, 4)
''', 'Count a sliding window that matches the sequence.', '<p>"a b" occurs 3 times and "a b c" twice, so the answer is 2 ÷ 3.</p>')
K.assign('rnnfwd', 'm', 'Run a one number RNN',
         '<p>Write <code>rnn_states(xs, wh, wx, b, h0)</code> that returns the list of states h<sub>t</sub> = tanh(wh·h<sub>t−1</sub> + wx·x<sub>t</sub> + b), each rounded to 4 decimals (round only the output, not the running state).</p>',
         '''
import math

def rnn_states(xs, wh, wx, b, h0):
    pass
''', [('rnn_states([1, 0, 0], 0.9, 1, 0, 0)', [0.7616, 0.595, 0.4896]), ('rnn_states([0, 0], 0.5, 1, 0, 1)', [0.4621, 0.227]), ('rnn_states([], 1, 1, 0, 0)', [])],
         '''
import math

def rnn_states(xs, wh, wx, b, h0):
    h, out = h0, []
    for x in xs:
        h = math.tanh(wh * h + wx * x + b)
        out.append(round(h, 4))
    return out
''', 'The same three weights at every step.', '<p>The first test is the worked problem of the lesson.</p>')
K.assign('perp', 'h', 'Perplexity of a sentence',
         '<p>Write <code>perplexity(probs)</code> where probs are the probabilities the model gave each true next word. Return exp of the mean of −ln p, rounded to 4 decimals.</p>',
         '''
import math

def perplexity(probs):
    pass
''', [('perplexity([0.25, 0.25, 0.25, 0.25])', 4.0), ('perplexity([1, 1, 1])', 1.0), ('perplexity([0.6, 0.3, 0.5, 0.4])', 2.2957)],
         '''
import math

def perplexity(probs):
    J = sum(-math.log(p) for p in probs) / len(probs)
    return round(math.exp(J), 4)
''', 'Average the losses first, then exponentiate.', '<p>Uniform probability 1 ÷ k always gives perplexity k.</p>')

K.must('Language model', 'Predicts P(next word | previous words). Chain rule gives the probability of a text. n-gram models keep only n − 1 words and count.')
K.must('n-gram problems', 'Sparsity (fix: smoothing, backoff), storage, and a context that cannot exceed about 5 words. 4-gram example: 400 ÷ 1000 = 0.4.')
K.must('RNN', 'h<sup>(t)</sup> = tanh(W<sub>h</sub>h<sup>(t−1)</sup> + W<sub>e</sub>e<sup>(t)</sup> + b₁), ŷ = softmax(Uh + b₂). Same weights at each step. One-hot 5, hidden 6: 96 parameters.')
K.must('Training', 'J<sup>(t)</sup> = −log ŷ of the true next word, averaged over steps. Teacher forcing feeds gold words. −ln 0.6 = 0.51, −ln 0.05 = 2.99.')
K.must('Perplexity', 'PP = exp(J), lower is better. PP = k means choosing among about k words: 1.44 confident, 4.07 confused.')

T = K.topic(
    slug='language-models-rnn', topic='nn-language-models-rnn', step=(3, 'Language models and RNNs', 'nn-rnn', 'Predict the next word: n-gram models and their limits, fixed window and recurrent neural language models, sequence labelling with BIO tags, and why LSTM and GRU fix vanishing gradients.', 'College and masters'),
    title='Language models and recurrent networks', short='LMs and RNNs', badge='3.1', minutes=50, added='2026-11-01',
    lead='From counting n-grams to a neural network that reads one word at a time: the Markov assumption, the fixed window model, the RNN, cross-entropy with teacher forcing and perplexity.',
    desc='Language modelling, n-grams with the Markov assumption and the 4-gram example, sparsity, smoothing and backoff, the fixed window neural model of Bengio et al., the RNN language model and its 96 parameter exercise, cross-entropy with the 0.51 and 2.99 examples, teacher forcing, backpropagation through time and perplexity.',
    summary='n-gram LMs, the fixed window model, RNN equations and parameters, cross-entropy training and perplexity.',
    keywords=['language model', 'n-gram', 'RNN', 'cross-entropy', 'teacher forcing', 'perplexity', 'BPTT'],
    recap='<p>A language model predicts the next word. n-grams count short contexts and suffer from sparsity. An RNN reads any length with shared weights, is trained with the average cross-entropy under teacher forcing, and is measured by perplexity, the exponential of that loss.</p>')
