# NLP section, chapter 5.1: exam revision for the neural NLP part. Organised by the kind of exam rather than by topic:
# school and first year questions, university semester and IIT course numericals, MCQ, MSQ and numerical answer papers
# in the NPTEL and GATE style (with negative marking), and derivations in the style of MIT, Stanford and Cambridge.
# Every question is an original practice question in the style of that tier, not a copy of a past paper, and every
# number was checked with Python. The course's own quiz remarks come from the lecture transcript: 10 questions in about
# 20 minutes, MCQ and MSQ plus numericals, a calculator allowed, formulas given, negative marking, and questions from the
# steps of neural networks, word embeddings, the co-occurrence matrix and GloVe.
from cvkit import Kit, fx, fxs, frac, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('drill', r'''
# Exam drill: softmax, cross-entropy, perplexity and the gradient y_hat - y in one go
import math
scores = [float(x) for x in input("scores (logits), space separated: ").split()]
gold = int(input("position of the gold word, starting at 1: ")) - 1
m = max(scores)
e = [math.exp(s - m) for s in scores]
p = [v / sum(e) for v in e]
print("softmax      =", [round(v, 4) for v in p])
print("cross-entropy =", round(-math.log(p[gold]), 4), " perplexity of this one step =", round(1 / p[gold], 4))
print("gradient dJ/dz = y_hat - y =", [round(v - (1 if i == gold else 0), 4) for i, v in enumerate(p)])
''', stdin='2 1 0.1\n1\n')

K.code('counts', r'''
# Every parameter count of the course in one table (no biases)
rows = [
    ("RNN LM, one-hot 5, hidden 6", 5 * 6 + 6 * 6 + 6 * 5),
    ("RNN POS tagger, E 300, H 50, 50 tags", 300 * 50 + 50 * 50 + 50 * 50),
    ("RNN NER tagger, 5 types in BIO (11 labels)", 300 * 50 + 50 * 50 + 50 * 11),
    ("BiLSTM, E 60, H 32 each way, 4 tags", 2 * 4 * 32 * (60 + 32) + 64 * 4),
    ("skip-gram, V 10,000, d 300", 2 * 10000 * 300),
    ("GloVe notebook, V 21, d 20, two biases", 2 * 21 * 20 + 2 * 21),
    ("seq2seq Spanish to French (stated assumptions)", 35000 * 256 + 45000 * 256 + 256 * 128 + 128 * 128 + 128 * 256 + 2 * 256 * 256 + 256 * 128 + 384 * 45000),
]
for name, n in rows:
    print(name.ljust(48), format(n, ","))
''')

K.lesson('map', 'How the neural NLP part is examined', f'''
<p>This chapter is for the week before an exam. It does not teach new material. It shows the shapes questions take at each level, with worked answers, and points back to the chapter where each idea is taught. The questions are original practice questions in the style of each tier, not copies of past papers.</p>
<p>The course quiz format, as announced in class: about 10 questions in 20 minutes, MCQ (one correct option) and MSQ (several correct options) plus numerical questions. A calculator is allowed, the formulas are given, and there is negative marking. The instructor said questions come from the steps of neural networks, word embeddings, the co-occurrence matrix and GloVe, so know each algorithm step by step.</p>
{table(['Tier', 'Typical format', 'What earns the marks', 'Where to practise'], [
    ['School and first year', 'Short answers, small sums, one formula', 'Clear definitions with an example', 'Lesson 2'],
    ['University semester and IIT course exams', 'Numericals by hand, parameter counts, compare and contrast', 'Formula first, every step shown, the answer with its meaning', 'Lesson 3'],
    ['NPTEL and GATE style papers', 'MCQ, MSQ and numerical answer type, negative marking', 'Speed, spotting the trap option, exact rounding', 'Lesson 4'],
    ['MIT, Stanford and Cambridge style', 'Derivations, design and critique', 'Assumptions named, a complete argument, when it fails', 'Lesson 5']])}
<h3>The twelve ideas examined most often</h3>
<ol>
<li>Gradient descent updates and the learning rate limit (chapter 1.1).</li>
<li>A neuron with sigmoid, the chain rule and one backpropagation step (chapters 1.2 and 1.3).</li>
<li>One-hot vectors, cosine similarity and the distributional hypothesis (chapter 2.1).</li>
<li>Skip-gram pairs, softmax probability and parameter counts (chapter 2.2).</li>
<li>Negative sampling loss, the 3/4 power and the 44 sigmoid question (chapter 2.3).</li>
<li>Co-occurrence matrix by hand, GloVe ratio, loss and f(x) (chapter 2.4).</li>
<li>Intrinsic against extrinsic evaluation, fastText n-grams, debiasing (chapter 2.5).</li>
<li>n-gram probability, RNN equations, cross-entropy and perplexity (chapter 3.1).</li>
<li>BIO tags 2n + 1 and the 20,000 and 18,050 parameter answers (chapter 3.2).</li>
<li>LSTM and GRU equations and the 23,808 BiLSTM answer (chapter 3.3).</li>
<li>The conditional language model and the bottleneck (chapter 4.1).</li>
<li>Dot-product attention by hand and greedy against beam search (chapters 4.2 and 4.3).</li>
</ol>
''', kw=['exam pattern', 'revision', 'MCQ', 'MSQ', 'negative marking', 'IIT', 'NPTEL', 'GATE', 'MIT', 'Stanford', 'Cambridge'])

K.lesson('school', 'Tier 1: school and first year', f'''
<p>Questions at this level check that you can apply one formula and explain an idea with an everyday example.</p>
{fxs(fx('Sigmoid', 'σ(z) = ' + frac('1', '1 + e<sup>−z</sup>'), 'Squashes any number into 0 to 1.', key=True),
     fx('Cosine similarity', 'cos(a, b) = ' + frac('a · b', '‖a‖ ‖b‖'), '1 same direction, 0 unrelated, −1 opposite.', key=True),
     fx('Gradient descent', 'w ← w − η ' + frac('∂J', '∂w'), 'Step downhill by the learning rate times the slope.', key=True))}
{steps('Question 1. Why can one-hot vectors not show that "hotel" and "motel" are similar?', [
    'Each word has a 1 in its own position and 0 elsewhere.',
    'The dot product of two different one-hot vectors is always 0.',
    'So every pair of different words is equally unrelated. Dense word vectors fix this.'])}
{steps('Question 2. Cosine similarity of (1, 2) and (2, 4).', [
    'Dot product 1 × 2 + 2 × 4 = 10.',
    'Lengths √5 and √20, product √100 = 10.',
    eq('cos = 10 ÷ 10 = 1, the same direction')])}
{steps('Question 3. J(w) = (w − 3)², w = 0, η = 0.1. Find w after one step.', [
    'Slope dJ/dw = 2(w − 3) = −6.',
    'w ← 0 − 0.1 × (−6).',
    eq('w = 0.6, a step towards the minimum at 3')])}
{steps('Question 4. Turn "Sachin Tendulkar played for India" into BIO tags with PER and GPE.', [
    'Sachin begins a person: B-PER. Tendulkar continues it: I-PER.',
    'played and for are outside: O, O.',
    eq('India: B-GPE')])}
<p>Short answer favourites: what a language model does (chapter 3.1), why "the cat" beats "a cat" in the beam example (chapter 4.3), what the forget gate does (chapter 3.3), and what "you shall know a word by the company it keeps" means (chapter 2.1).</p>
{note('Do not confuse similarity with relatedness. "cup" and "coffee" are related (they appear together) but not similar (one is a container, one is a drink).', 'warn')}
''', kw=['sigmoid', 'cosine similarity', 'gradient descent', 'one-hot', 'BIO', 'short answer'])

K.lesson('semester', 'Tier 2: university semester and IIT course exams', f'''
<p>Here the examiner gives sizes, vectors or counts and asks you to compute by hand. Write the formula, substitute, and state the meaning of the answer.</p>
{code('counts')}
{viz('paramcount')}
{steps('Question 5. Skip-gram with V = 6,000, d = 200, window 2. (a) one-hot size (b) hidden size (c) training pairs from an 8 word sentence.', [
    '(a) The one-hot input has V = 6,000 entries.',
    '(b) The hidden layer is the embedding, 200 numbers.',
    '(c) Middle words have 4 neighbours, edge words fewer: 2 + 3 + 4 × 4 + 3 + 2.',
    eq('= 26 training pairs')])}
{steps('Question 6. Co-occurrence with window 1 on "I like NLP . I like deep learning .". Find X(I, like) and X(like, NLP).', [
    'Treat each sentence separately. "I like" appears in both sentences.',
    'X(I, like) = 2 with a symmetric window.',
    'X(like, NLP) = 1 from the first sentence.',
    eq('X(I, like) = 2, X(like, NLP) = 1')])}
{steps('Question 7. GloVe with x<sub>max</sub> = 100, α = 0.75. Compute f(10) and f(150).', [
    'f(10) = (10 ÷ 100)<sup>0.75</sup> = 0.1<sup>0.75</sup>.',
    eq('f(10) = 0.1778'),
    eq('f(150) = 1 because 150 ≥ x<sub>max</sub>')])}
{steps('Question 8. Dot-product attention: encoder states [1, 0] and [0, 1], decoder state [2, 0]. Context vector.', [
    'Scores 2 and 0.',
    'Weights e² ÷ (e² + 1) = 0.8808 and 0.1192.',
    eq('context = 0.8808 [1, 0] + 0.1192 [0, 1] = [0.8808, 0.1192]')])}
{note('Units and assumptions earn marks. Write "excluding biases", "natural log", "window counted on both sides" next to the answer.', 'exam')}
''', kw=['numericals', 'parameter counts', 'skip-gram pairs', 'co-occurrence', 'GloVe weighting', 'attention'])

K.lesson('mcq', 'Tier 3: MCQ, MSQ and numerical answer papers', f'''
<p>These papers reward speed and precision. With negative marking, a blind guess is not free. With no partial credit in MSQ, every ticked option must be right.</p>
{fxs(fx('Expected mark of a guess', 'E = p · (+1) + (1 − p) · (−m)', 'p chance of being right, m the penalty per wrong answer.', key=True))}
{steps('Question 9. Four options, +1 for right, −1/3 for wrong. Is a blind guess worth it? And after ruling out one option?', [
    'Blind: p = 1/4, E = 1/4 − 3/4 × 1/3 = 0. No gain on average.',
    'One option ruled out: p = 1/3, E = 1/3 − 2/3 × 1/3 = 1/9.',
    eq('Guess only when you can eliminate at least one option')])}
{steps('Question 10 (MSQ). Which are true of negative sampling? (A) it replaces the softmax with sigmoids (B) noise words come from U(w)<sup>3/4</sup> (C) the true context can be a negative (D) only 1 + K output vectors change per pair.', [
    '(A) True, binary logistic regressions.',
    '(B) True, the 3/4 power.',
    '(C) False, the notebook skips the true context word.',
    eq('Answer: A, B and D')])}
{steps('Question 11 (numerical). Window 2, K = 5, full window. Sigmoid computations per centre word?', [
    '4 context words.',
    'Each: 1 positive + 5 negatives = 6.',
    eq('4 × 6 = 24')])}
{table(['Trap', 'How to avoid it'], [['log base', 'perplexity = exp(J) with natural logs, 2<sup>H</sup> with bits'], ['counting T in RNN parameters', 'weights are shared, length does not matter'], ['BIO count', '2n + 1, not 2n'], ['top-p', 'keep words until the sum reaches p, include the one that crosses it'], ['beam size 1', 'is greedy decoding'], ['rounding', 'keep 4 or more decimals until the final line']])}
''', kw=['MCQ', 'MSQ', 'negative marking', 'expected value', 'numerical answer', 'traps'])

K.lesson('derive', 'Tier 4: derivations, design and critique', f'''
<p>Research university exams ask why, not only what. Expect to derive a gradient, justify a design, and say when a method fails.</p>
{steps('Derivation 1. Softmax with cross-entropy gives the gradient ŷ − y.', [
    'J = −log ŷ<sub>c</sub> with ŷ<sub>k</sub> = e<sup>z<sub>k</sub></sup> ÷ ∑<sub>j</sub> e<sup>z<sub>j</sub></sup>, so J = −z<sub>c</sub> + log ∑<sub>j</sub> e<sup>z<sub>j</sub></sup>.',
    '∂J/∂z<sub>k</sub> = −[k = c] + e<sup>z<sub>k</sub></sup> ÷ ∑<sub>j</sub> e<sup>z<sub>j</sub></sup> = ŷ<sub>k</sub> − y<sub>k</sub>.',
    'Example: ŷ = [0.1, 0.6, 0.2, 0.1], gold 2. Gradient = [0.1, −0.4, 0.2, 0.1].',
    eq('∂J/∂z = ŷ − y: push the gold score up, the others down in proportion')])}
{steps('Derivation 2. Why does a plain RNN forget, and why does the LSTM cell help?', [
    '∂h<sup>(t)</sup>/∂h<sup>(j)</sup> = ∏ diag(tanh′) W<sub>h</sub>, so its size is at most (‖W<sub>h</sub>‖)<sup>t−j</sup> for tanh.',
    'If ‖W<sub>h</sub>‖ < 1 this shrinks exponentially: the gradient vanishes.',
    'For the LSTM, c<sup>(t)</sup> = f ⊙ c<sup>(t−1)</sup> + i ⊙ c̃ gives ∂c<sup>(t)</sup>/∂c<sup>(t−1)</sup> ≈ diag(f).',
    eq('The factor is a learned gate, near 1 when memory should be kept')])}
{steps('Derivation 3. From probability ratios to the GloVe model.', [
    'Want F((w<sub>i</sub> − w<sub>j</sub>)·w̃<sub>k</sub>) = P(k | i) ÷ P(k | j).',
    'Choose F = exp, then w<sub>i</sub>·w̃<sub>k</sub> = log P(k | i) = log X<sub>ik</sub> − log X<sub>i</sub>.',
    'Absorb log X<sub>i</sub> into b<sub>i</sub> and add b̃<sub>k</sub> for symmetry.',
    eq('w<sub>i</sub>·w̃<sub>k</sub> + b<sub>i</sub> + b̃<sub>k</sub> = log X<sub>ik</sub>, fitted by weighted least squares')])}
{steps('Design question. You must translate between two low-resource languages with 20,000 parallel sentences. Propose a system and critique it.', [
    'Start from a multilingual pre-trained model (transfer learning) rather than training from scratch.',
    'Add back translated data from monolingual text in the target language.',
    'Decode with beam search (k about 5) and length normalisation.',
    'Risks: synthetic data copies the errors of the back translation model, and BLEU on a tiny test set is noisy. Report confidence intervals.'])}
{ladder(
    '<p>At school level, explain ideas with examples and do one-step sums: a sigmoid, a cosine, a single gradient step.</p>',
    '<p>At university level, compute by hand: parameter counts, co-occurrence entries, GloVe weights, attention weights, perplexity. Show every step.</p>',
    '<p>In competitive papers, recognise the formula fast, avoid traps around log bases, BIO counts and shared weights, and guess only when an option is ruled out.</p>',
    '<p>At research level, derive gradients, explain why gating and attention fix gradient flow, and critique designs with their failure modes and evaluation risks.</p>')}
''', kw=['derivation', 'softmax gradient', 'vanishing gradient proof', 'GloVe derivation', 'design', 'critique'])

K.lesson('sheet', 'Formula sheet and last minute checks', f'''
{fxs(fx('Softmax', 'ŷ<sub>k</sub> = e<sup>z<sub>k</sub></sup> ÷ ∑<sub>j</sub> e<sup>z<sub>j</sub></sup>', 'Subtract the maximum score first for stability.'),
     fx('Skip-gram', 'P(o | c) = exp(u<sub>o</sub>·v<sub>c</sub>) ÷ ∑<sub>w</sub> exp(u<sub>w</sub>·v<sub>c</sub>)', 'Parameters 2Vd.'),
     fx('Negative sampling', 'J = −log σ(u<sub>o</sub>·v<sub>c</sub>) − ∑<sub>k</sub> log σ(−u<sub>k</sub>·v<sub>c</sub>)', 'Noise from U(w)<sup>3/4</sup>.'),
     fx('GloVe', 'J = ∑ f(X<sub>ij</sub>)(w<sub>i</sub>·w̃<sub>j</sub> + b<sub>i</sub> + b̃<sub>j</sub> − log X<sub>ij</sub>)²', 'f(x) = (x ÷ x<sub>max</sub>)<sup>α</sup> below x<sub>max</sub>, else 1.'),
     fx('RNN', 'h<sup>(t)</sup> = tanh(W<sub>h</sub>h<sup>(t−1)</sup> + W<sub>e</sub>e<sup>(t)</sup> + b)', 'Parameters E·H + H·H + H·K.'),
     fx('Perplexity', 'PP = exp(J)', 'J is the average cross-entropy in natural logs.'),
     fx('LSTM', 'c = f ⊙ c<sub>old</sub> + i ⊙ c̃, h = o ⊙ tanh(c)', 'Parameters 4H(E + H).'),
     fx('GRU', 'h = (1 − z) ⊙ h<sub>old</sub> + z ⊙ h̃', 'Parameters 3H(E + H).'),
     fx('Attention', 'α = softmax(s<sup>T</sup>h<sub>i</sub>), a = ∑ α<sub>i</sub>h<sub>i</sub>', 'Scaled version divides by √d.'),
     fx('Beam score', '(1 ÷ t) ∑ log P(y<sub>i</sub> | y<sub>&lt;i</sub>, x)', 'Length normalised.'))}
{code('drill')}
{table(['Number to remember', 'Where it comes from'], [['96', 'RNN LM, one-hot 5, hidden 6'], ['44', 'sigmoids per centre word, window 2, K = 10'], ['20,000 and 18,050', 'RNN POS and NER taggers'], ['23,808', 'BiLSTM language identification'], ['0.4', '4-gram example 400 ÷ 1000'], ['0.51 and 2.99', 'cross-entropy for 0.6 and 0.05'], ['[1.262, −0.722]', 'the attention problem'], ['0.36 against 0.20', 'beam against greedy on the slide tree']])}
{note('Last minute checks: weights in an RNN are shared over time, the softmax denominator covers the whole vocabulary, BIO needs 2n + 1 tags, attention weights change every decoder step, and beam search is not guaranteed optimal.', 'tip')}
''', kw=['formula sheet', 'numbers to remember', 'last minute checks'])

# ---------------------------------------------------------------- quiz (a mock paper)
K.quiz('e', 'Cosine similarity of (1, 0) and (0, 1) is', ['−1', '0', '0.5', '1'], 1, 'Dot product 0.', 'At right angles, unrelated.')
K.quiz('e', 'Which is a language model task?', ['predict the next word', 'count vowels', 'sort a list', 'compress an image'], 0, 'Chapter 3.1.', 'Next word prediction.')
K.quiz('e', 'GRU gates are', ['forget and output', 'update and reset', 'input and output', 'only one gate'], 1, 'Chapter 3.3.', 'z and r.')
K.quiz('m', 'BIO tags for 3 entity types', ['3', '6', '7', '9'], 2, '2n + 1.', '7.')
K.quiz('m', 'A blind guess with 4 options, +1 right and −1/3 wrong, has expected mark', ['−1/3', '0', '1/4', '1/9'], 1, '1/4 − 3/4 × 1/3.', 'Exactly zero.')
K.quiz('m', 'Skip-gram parameters with V = 10,000 and d = 300 (no biases)', ['3,000,000', '6,000,000', '600,000', '10,300'], 1, 'Two V × d matrices.', '6 million.')
K.quiz('m', 'In GloVe, f(0) is', ['1', '0', 'undefined', 'x_max'], 1, 'Never-seen pairs.', 'They are dropped.')
K.quiz('m', 'Gradient of softmax cross-entropy with respect to the scores', ['y − ŷ', 'ŷ − y', 'ŷ(1 − ŷ)', 'log ŷ'], 1, 'Derivation 1.', 'Prediction minus one-hot target.')
K.quiz('h', 'Window 2, K = 5, full window. Sigmoids per centre word?', ['6', '20', '24', '30'], 2, '(1 + K) × 4.', '24.')
K.quiz('h', 'Which statements are true? Pick the option listing exactly the true ones. (P) beam size 1 is greedy (Q) beam search is optimal (R) top-p adapts its size', ['P only', 'P and R', 'Q and R', 'P, Q and R'], 1, 'MSQ style.', 'Beam search is not guaranteed optimal.')
K.quiz('h', 'Encoder states [1, 0] and [0, 1], decoder [2, 0]. Weight on the first state', ['0.50', '0.73', '0.88', '1.00'], 2, 'e² ÷ (e² + 1).', '0.8808.')
K.quiz('x', 'Why does the LSTM ease vanishing gradients?', ['more layers', 'an additive cell path with gradient ≈ f', 'ReLU inside', 'smaller vocabulary'], 1, 'Derivation 2.', 'A learned gate near 1 keeps the signal.')
K.quiz('x', 'The GloVe biases come from', ['regularisation', 'the log X<sub>i</sub> term that does not depend on k', 'the learning rate', 'negative sampling'], 1, 'Derivation 3.', 'It is absorbed into b<sub>i</sub>.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'σ(0)?', '0.5', '1 ÷ (1 + 1).',
       ['e<sup>0</sup> = 1.', '1 ÷ 2.', eq('0.5')], check=0.5, tol=1e-9)
K.calc('e', 'J(w) = (w − 3)², w = 0, η = 0.1. w after one gradient step.', '0.6', 'w − η · 2(w − 3).',
       ['Slope −6.', '0 + 0.6.', eq('0.6')], check=0.6, tol=1e-9)
K.calc('e', 'Cosine of (1, 2) and (2, 4).', '1', 'Same direction.',
       ['Dot 10.', 'Lengths multiply to 10.', eq('1')], check=1, tol=1e-9)
K.calc('m', 'Skip-gram pairs, window 2, sentence of 8 words.', '26', 'Edge words have fewer neighbours.',
       ['Words 1 and 8: 2 each. Words 2 and 7: 3 each.', 'Words 3 to 6: 4 each, 16.', eq('2 + 3 + 16 + 3 + 2 = 26')], check=26, tol=1e-9)
K.calc('m', 'GloVe f(10) with x<sub>max</sub> = 100 and α = 0.75, four decimals.', '0.1778', '0.1<sup>0.75</sup>.',
       ['10 ÷ 100 = 0.1.', 'ln 0.1 × 0.75 = −1.727.', eq('e<sup>−1.727</sup> = 0.1778')], check=0.1 ** 0.75, tol=5e-5)
K.calc('m', 'Attention weight on [1, 0] for decoder [2, 0] against states [1, 0] and [0, 1], four decimals.', '0.8808', 'softmax(2, 0).',
       ['e² = 7.389.', 'Sum 8.389.', eq('0.8808')], check=0.8807970779778823, tol=5e-5)
K.calc('m', 'Expected mark of a guess after ruling out one of four options (+1, −1/3). Three decimals.', '0.111', 'p = 1/3.',
       ['1/3 × 1 = 0.333.', '2/3 × 1/3 = 0.222.', eq('0.111')], check=1 / 9, tol=5e-4)
K.calc('m', 'Sigmoids per centre word with window 2 (4 context words) and K = 5.', '24', '(1 + K) × 4.',
       ['Per context word 6.', '4 context words.', eq('24')], check=24, tol=1e-9)
K.calc('h', 'Gradient of softmax cross-entropy for ŷ = [0.1, 0.6, 0.2, 0.1] with gold position 2. Give the second component.', '-0.4', 'ŷ − y.',
       ['y = [0, 1, 0, 0].', '0.6 − 1.', eq('−0.4')], check=-0.4, tol=1e-9)
K.calc('h', 'LSTM layer with E = 50, H = 100, no biases. Parameters.', '60000', '4H(E + H).',
       ['E + H = 150.', '4 × 100 = 400.', eq('60,000')], check=60000, tol=1e-9)
K.calc('h', 'Perplexity of a model whose average cross-entropy is 1.5 (natural log), three decimals.', '4.482', 'exp(J).',
       ['e<sup>1.5</sup>.', '= 4.4817.', eq('4.482')], check=4.4816890703380645, tol=5e-4)
K.calc('x', 'Softmax of scores (2, 1, 0.1): probability of the first, four decimals.', '0.659', 'e² ÷ (e² + e + e<sup>0.1</sup>).',
       ['e² = 7.389, e¹ = 2.718, e<sup>0.1</sup> = 1.105.', 'Sum 11.212.', eq('0.659')], check=0.6590011388859679, tol=5e-4)

T = K.topic(
    slug='nn-exam-revision', topic='nn-exam-revision', kind='revision',
    step=(5, 'Exam revision', 'nn-revision', 'Revise the neural NLP section by exam style, from school questions to IIT numericals, MCQ and MSQ papers with negative marking, and MIT and Cambridge style derivations.', 'All levels'),
    title='Exam revision for neural NLP', short='Exam revision', badge='5.1', minutes=60, added='2026-11-01',
    lead='Practise the question shapes of every level with worked answers: one-step sums, parameter counts and attention by hand, MCQ and MSQ tactics under negative marking, and derivations with their assumptions.',
    desc='The course quiz pattern, exam tiers from school to research universities, worked questions on sigmoid, cosine, gradient descent, BIO, skip-gram pairs, co-occurrence, GloVe weights and attention, MCQ and MSQ strategy with negative marking, derivations of the softmax gradient, vanishing gradients and GloVe, a formula sheet and a mock paper.',
    summary='Exam style questions for neural NLP from school level to research universities, with worked answers, a formula sheet and a mock paper.',
    keywords=['exam', 'revision', 'formula sheet', 'mock paper', 'MCQ', 'MSQ', 'negative marking', 'IIT', 'GATE', 'MIT', 'Cambridge'],
    recap='')
