# NLP section, chapter 4.2: attention in encoder-decoder models. Source: FoVL lecture 3 slides 86 to 91 (encoder-decoder
# with attention from Bahdanau et al. 2015 "Neural Machine Translation by Jointly Learning to Align and Translate", the
# dynamic context of each decoder state, attention in equations from SLP3, the dot-product problem with encoder states
# [2, 0], [-1, 2], [1, -1], [0, 1] and decoder state [1, -2], attention for translation and the summarisation model of
# Rush et al. 2015) and CS224n lecture 7 for the variants.
from cvkit import Kit, fx, fxs, frac, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('dotattn', r'''
# The lecture problem: dot-product attention over four encoder states
import math
H = [[2, 0], [-1, 2], [1, -1], [0, 1]]     # encoder hidden states h_1 ... h_4
s = [1, -2]                                # decoder hidden state s_t
e = [h[0] * s[0] + h[1] * s[1] for h in H]
ex = [math.exp(v) for v in e]
Z = sum(ex)
a = [v / Z for v in ex]
c = [sum(a[i] * H[i][k] for i in range(4)) for k in range(2)]
print("scores e =", e)
print("exp =", [round(v, 4) for v in ex], " sum =", round(Z, 4))
print("weights alpha =", [round(v, 4) for v in a])
print("context a_t =", [round(v, 4) for v in c])
''')

K.code('variants', r'''
# Three ways to score one encoder state h against one decoder state s
import math
h, s = [1, 0], [0, 1]
dot = h[0] * s[0] + h[1] * s[1]
W = [[1, 0], [0, 2]]
Wh = [W[0][0] * h[0] + W[0][1] * h[1], W[1][0] * h[0] + W[1][1] * h[1]]
mult = s[0] * Wh[0] + s[1] * Wh[1]
v = [1, 1]
add = sum(v[k] * math.tanh(h[k] + s[k]) for k in range(2))   # W1 = W2 = I for the example
print("dot product s.h =", dot)
print("multiplicative s.W h =", mult)
print("additive v.tanh(W1 h + W2 s) =", round(add, 4))
''')

K.lesson('idea', 'The idea of attention', f'''
<p>Attention fixes the bottleneck. On each step of the decoder, it uses a direct connection to the encoder to focus on a particular part of the source sentence. Instead of one fixed summary vector, each decoder state gets a different, dynamic context, which is a function of all the encoder states.</p>
{viz('seq2seq', attn=True)}
{steps('Translating "il a m’ entarté" with attention', [
    'The encoder produces one state for each source word: il, a, m’, entarté.',
    'To write "he", the decoder state compares itself with all four. The scores are highest for "il", so most attention goes there.',
    'The weighted mix of encoder states (the context) is joined with the decoder state to predict "he".',
    'For "hit" and "pie" the attention moves to "entarté", the word that means "hit with a pie". One source word can feed several target words.'])}
{table(['', 'Without attention', 'With attention'], [['what the decoder sees of the source', 'one vector, the last encoder state', 'a fresh weighted mix of all encoder states at every step'], ['long sentences', 'quality drops', 'quality stays high'], ['alignment', 'hidden', 'visible in the attention weights']])}
{scene('a human translator with the source open', '<p>A professional translator does not read a long paragraph once, close the book and write the translation from memory. They keep the source open and look back at the relevant phrase for every sentence they write. Attention gives the decoder the same open book.</p>')}
''', kw=['attention', 'dynamic context', 'alignment', 'Bahdanau'])

K.lesson('equations', 'Attention in equations', f'''
<p>Let the encoder states be h<sub>1</sub>, ..., h<sub>N</sub> ∈ ℝ<sup>d</sup> and the decoder state at step t be s<sub>t</sub> ∈ ℝ<sup>d</sup>. Attention has three steps: score, normalise, mix.</p>
{fxs(fx('1. Scores', 'e<sup>t</sup> = [s<sub>t</sub><sup>T</sup>h<sub>1</sub>, ..., s<sub>t</sub><sup>T</sup>h<sub>N</sub>] ∈ ℝ<sup>N</sup>', 'One dot product per source position.', key=True),
     fx('2. Attention distribution', 'α<sup>t</sup> = softmax(e<sup>t</sup>) ∈ ℝ<sup>N</sup>', 'Non-negative weights that add to 1.', key=True),
     fx('3. Attention output (context)', 'a<sub>t</sub> = ∑<sub>i=1</sub><sup>N</sup> α<sub>i</sub><sup>t</sup> h<sub>i</sub> ∈ ℝ<sup>d</sup>', 'A weighted average of the encoder states.', key=True),
     fx('4. Use it', 'ŷ<sub>t</sub> = softmax(W<sub>o</sub>[a<sub>t</sub>, s<sub>t</sub>])', 'Concatenate the context with the decoder state and continue as before.'))}
{viz('attention', dec='-1 2')}
{note('The weights depend on the decoder state, so they change at every output step. That is what makes the context dynamic. A common exam slip is to compute one set of weights for the whole sentence.', 'warn')}
{deep('attention as soft dictionary lookup', '<p>A dictionary returns the value whose key matches the query exactly. Attention compares the query s<sub>t</sub> with every key h<sub>i</sub>, turns the similarities into weights with softmax, and returns a weighted average of the values. In the general form keys and values can differ: output = ∑ softmax(q·k<sub>i</sub>) v<sub>i</sub>. Transformers use exactly this with learned projections for q, k and v.</p>')}
''', kw=['scores', 'softmax weights', 'context vector', 'concatenation', 'query key value'])

K.lesson('problem', 'The lecture problem, fully worked', f'''
<p>A sequence-to-sequence RNN uses dot-product attention. The encoder outputs four hidden states of dimension 2: [2, 0], [−1, 2], [1, −1] and [0, 1]. At one decoding step the decoder state is [1, −2]. Compute the context vector.</p>
{steps('Step by step', [
    'Scores, s·h<sub>i</sub>: 1×2 + (−2)×0 = 2, then 1×(−1) + (−2)×2 = −5, then 1×1 + (−2)×(−1) = 3, then 1×0 + (−2)×1 = −2.',
    'Exponentials: e<sup>2</sup> = 7.3891, e<sup>−5</sup> = 0.0067, e<sup>3</sup> = 20.0855, e<sup>−2</sup> = 0.1353. Sum = 27.6167.',
    eq('α = (0.2676, 0.0002, 0.7273, 0.0049)'),
    'First component: 0.2676 × 2 + 0.0002 × (−1) + 0.7273 × 1 + 0.0049 × 0 = 1.2622.',
    'Second component: 0.2676 × 0 + 0.0002 × 2 + 0.7273 × (−1) + 0.0049 × 1 = −0.7219.',
    eq('a<sub>t</sub> ≈ [1.262, −0.722]')])}
{code('dotattn')}
{table(['h<sub>i</sub>', 'score', 'weight', 'reading'], [['[2, 0]', '2', '0.2676', 'second most relevant'], ['[−1, 2]', '−5', '0.0002', 'points away from s, ignored'], ['[1, −1]', '3', '0.7273', 'most aligned with s, dominates'], ['[0, 1]', '−2', '0.0049', 'almost ignored']])}
{viz('attention')}
{note('Show the scores, the softmax and the weighted sum as three separate lines. Keep 4 decimals in the weights, and check that they add to 1 (0.2676 + 0.0002 + 0.7273 + 0.0049 = 1.0000).', 'exam')}
''', kw=['dot-product attention', 'worked problem', 'context vector', '[1.262, -0.722]'])

K.lesson('variants', 'Ways to compute the scores', f'''
<p>The dot product needs the decoder and encoder states to have the same size and gives no learnable control. Several variants exist. All of them compute a score e<sub>i</sub> from h<sub>i</sub> and s, then use the same softmax and weighted sum.</p>
{fxs(fx('Basic dot product', 'e<sub>i</sub> = s<sup>T</sup>h<sub>i</sub>', 'Needs d<sub>s</sub> = d<sub>h</sub>. No parameters.', key=True),
     fx('Multiplicative (bilinear, Luong)', 'e<sub>i</sub> = s<sup>T</sup>W h<sub>i</sub>, &nbsp; W ∈ ℝ<sup>d<sub>s</sub> × d<sub>h</sub></sup>', 'Works for different sizes. d<sub>s</sub> × d<sub>h</sub> parameters.', key=True),
     fx('Reduced rank multiplicative', 'e<sub>i</sub> = (Us)<sup>T</sup>(Vh<sub>i</sub>), &nbsp; U ∈ ℝ<sup>k × d<sub>s</sub></sup>, V ∈ ℝ<sup>k × d<sub>h</sub></sup>', 'k much smaller than d. The form transformers use.'),
     fx('Additive (Bahdanau)', 'e<sub>i</sub> = v<sup>T</sup> tanh(W<sub>1</sub>h<sub>i</sub> + W<sub>2</sub>s)', 'A small neural network scores each pair. d<sub>a</sub> is its hidden size.', key=True),
     fx('Scaled dot product', 'e<sub>i</sub> = ' + frac('s<sup>T</sup>h<sub>i</sub>', '√d'), 'Keeps scores from growing with d, so the softmax does not saturate.'))}
{code('variants')}
{steps('Scaled scores on the lecture problem', [
    'd = 2, so divide the scores 2, −5, 3, −2 by √2 = 1.414.',
    'Scaled scores: 1.414, −3.536, 2.121, −1.414.',
    eq('α = (0.3232, 0.0023, 0.6554, 0.0191), context ≈ [1.300, −0.632]'),
    'The weights spread out a little because the scores are closer together.'])}
{table(['Variant', 'Parameters (d<sub>h</sub> = 128, d<sub>s</sub> = 256, d<sub>a</sub> = 64)'], [['dot product', '0, and it cannot be used because the sizes differ'], ['multiplicative', '256 × 128 = 32,768'], ['additive', '64 × 128 + 64 × 256 + 64 = 24,640']])}
''', kw=['dot product', 'multiplicative', 'bilinear', 'additive', 'scaled dot product'])

K.lesson('benefits', 'Why attention is so helpful', f'''
<p>Attention significantly improved NMT and quickly spread to every encoder-decoder task, for example abstractive summarisation (Rush et al. 2015).</p>
{table(['Benefit', 'Why'], [['better translations', 'the decoder can focus on the relevant source words'], ['solves the bottleneck', 'the decoder reads the source directly instead of through one vector'], ['helps vanishing gradients', 'there is a shortcut from every decoder step to every source word'], ['interpretability', 'the attention weights show what the decoder was looking at'], ['alignment for free', 'the model learns which source word matches which target word without being told']])}
{steps('Soft alignment', [
    'Plot α<sup>t</sup> for every output step t as a row of a matrix: target words down, source words across.',
    'For English to French the matrix is close to the diagonal, because word order is similar.',
    '"European Economic Area" and "zone économique européenne" show a reversed block: the model learned the adjective order.',
    eq('No one supplied alignments, the network learned them from translation pairs only')])}
{ladder(
    '<p>When the model writes each translated word, it looks back at the source sentence and decides which words to pay attention to, like a person pointing at the words they are translating.</p>',
    '<p>Score each encoder state against the decoder state, softmax the scores, and take the weighted average as the context. Variants differ only in the score: dot, multiplicative, additive or scaled.</p>',
    '<p>Attention is a differentiable soft lookup: a query is compared with keys and returns a mix of values. Its cost is O(N) per decoder step, O(NT) for a translation, and it gives direct gradient paths between any two positions.</p>',
    '<p>Self-attention applies the same lookup within one sequence. Removing recurrence entirely and stacking multi-head self-attention gives the transformer (Vaswani et al. 2017), the basis of BERT, GPT and every current large language model.</p>')}
''', kw=['benefits', 'alignment', 'interpretability', 'summarisation', 'self-attention'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Attention lets each decoder step', ['skip the softmax', 'look at all encoder states', 'use a bigger vocabulary', 'run in parallel with the encoder'], 1, 'Direct connection.', 'A fresh weighted mix of the source.')
K.quiz('e', 'The attention weights at one step add up to', ['0', '1', 'N', 'it varies'], 1, 'Softmax.', 'They form a probability distribution.')
K.quiz('e', 'Which problem does attention mainly solve?', ['tokenisation', 'the bottleneck', 'overfitting', 'slow embeddings'], 1, 'One vector for the whole source.', 'Attention removes the single vector bottleneck.')
K.quiz('e', 'The context vector is', ['the last encoder state', 'a weighted sum of encoder states', 'the decoder state', 'the softmax output'], 1, 'a<sub>t</sub> = ∑ α<sub>i</sub>h<sub>i</sub>.', 'A weighted average.')
K.quiz('m', 'Scores 2, −5, 3, −2. The largest attention weight is about', ['0.27', '0.50', '0.73', '0.99'], 2, 'e³ ÷ sum.', '20.09 ÷ 27.62 = 0.727.')
K.quiz('m', 'The dot-product score of s = [1, −2] and h = [−1, 2] is', ['3', '−3', '5', '−5'], 3, '1×(−1) + (−2)×2.', '−5.')
K.quiz('m', 'Multiplicative attention is preferred over the plain dot product when', ['the vocabulary is small', 'encoder and decoder states have different sizes', 'there is no softmax', 'the sentence is short'], 1, 's<sup>T</sup>Wh.', 'W maps between the two sizes.')
K.quiz('m', 'Scaling scores by 1 ÷ √d', ['makes the weights sharper', 'keeps scores from growing with d so the softmax does not saturate', 'removes the softmax', 'doubles the context'], 1, 'Transformers.', 'Large scores give near one-hot weights and tiny gradients.')
K.quiz('m', 'Attention helps with vanishing gradients because', ['it uses ReLU', 'it gives a shortcut from each decoder step to every source state', 'it has fewer parameters', 'it removes the decoder'], 1, 'Short paths.', 'Gradients do not have to pass through every encoder step.')
K.quiz('h', 'In additive attention v<sup>T</sup>tanh(W<sub>1</sub>h + W<sub>2</sub>s) with d<sub>h</sub> = 128, d<sub>s</sub> = 256, d<sub>a</sub> = 64, the parameter count is', ['24,576', '24,640', '32,768', '8,256'], 1, '64×128 + 64×256 + 64.', '8,192 + 16,384 + 64 = 24,640.')
K.quiz('h', 'Raising a softmax temperature on the scores makes attention', ['harder', 'closer to uniform', 'zero', 'negative'], 1, 'Divide scores by T.', 'Scores move together, weights even out.')
K.quiz('h', 'The weights at decoder step t depend on', ['only the encoder', 'only the decoder', 'the decoder state s<sub>t</sub> and all encoder states', 'the vocabulary'], 2, 'Score uses both.', 'That is why they change every step.')
K.quiz('x', 'Self-attention differs from encoder-decoder attention in that', ['it uses no softmax', 'queries, keys and values come from the same sequence', 'it needs an RNN', 'it only works for images'], 1, 'Transformers.', 'Every position attends to every other position of the same sequence.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Score of s = [1, −2] with h = [2, 0].', '2', 's·h.',
       ['1 × 2 = 2.', '(−2) × 0 = 0.', eq('2')], check=2, tol=1e-9)
K.calc('e', 'Two scores of 1 and 1. Attention weight of the first.', '0.5', 'Equal scores.',
       ['e¹ and e¹ are equal.', 'Each is half the sum.', eq('0.5')], check=0.5, tol=1e-9)
K.calc('e', 'Lecture problem: sum of the exponentials of the scores 2, −5, 3, −2, four decimals.', '27.6167', 'Add e<sup>e<sub>i</sub></sup>.',
       ['7.3891 + 0.0067.', '+ 20.0855 + 0.1353.', eq('27.6167')], check=27.6167, tol=5e-4)
K.calc('m', 'Lecture problem: attention weight of h<sub>3</sub> = [1, −1], four decimals.', '0.7273', 'e³ ÷ sum.',
       ['e³ = 20.0855.', 'Sum 27.6167.', eq('0.7273')], check=0.7273, tol=5e-4)
K.calc('m', 'Lecture problem: weight of h<sub>1</sub> = [2, 0], four decimals.', '0.2676', 'e² ÷ sum.',
       ['e² = 7.3891.', 'Divide by 27.6167.', eq('0.2676')], check=0.2676, tol=5e-4)
K.calc('h', 'Lecture problem: first component of the context vector, four decimals.', '1.2622', '∑ α<sub>i</sub> h<sub>i,1</sub>.',
       ['0.2676 × 2 = 0.5352, 0.0002 × (−1) = −0.0002.', '0.7273 × 1 = 0.7273, 0.0049 × 0 = 0.', eq('1.2622')], check=1.2622, tol=5e-4)
K.calc('h', 'Lecture problem: second component of the context vector, four decimals.', '-0.7219', '∑ α<sub>i</sub> h<sub>i,2</sub>.',
       ['0.0002 × 2 = 0.0005.', '0.7273 × (−1) = −0.7273, 0.0049 × 1 = 0.0049.', eq('−0.7219')], check=-0.7219, tol=5e-4)
K.calc('m', 'Multiplicative score s<sup>T</sup>Wh with s = [1, −2], W = ' + mat([['1', '0'], ['0', '2']]) + ', h = [−1, 2].', '-9', 'Wh first.',
       ['Wh = [−1, 4].', 's·[−1, 4] = −1 − 8.', eq('−9')], check=-9, tol=1e-9)
K.calc('m', 'Additive score v<sup>T</sup>tanh(h + s) with h = [1, 0], s = [0, 1], v = [1, 1]. Four decimals.', '1.5232', 'Element-wise tanh.',
       ['h + s = [1, 1].', 'tanh(1) = 0.7616 each.', eq('0.7616 + 0.7616 = 1.5232')], check=2 * 0.7615941559557649, tol=5e-4)
K.calc('h', 'Scaled dot product on the lecture problem (divide by √2). Weight of h<sub>3</sub>, four decimals.', '0.6554', 'softmax of scores ÷ 1.414.',
       ['Scaled scores 1.414, −3.536, 2.121, −1.414.', 'Exponentials 4.113, 0.029, 8.340, 0.243, sum 12.725.', eq('8.340 ÷ 12.725 = 0.6554')], check=0.6554, tol=5e-4)
K.calc('h', 'Additive attention with d<sub>h</sub> = 128, d<sub>s</sub> = 256 and d<sub>a</sub> = 64. Parameters (W<sub>1</sub>, W<sub>2</sub>, v).', '24640', 'd<sub>a</sub>d<sub>h</sub> + d<sub>a</sub>d<sub>s</sub> + d<sub>a</sub>.',
       ['64 × 128 = 8,192.', '64 × 256 = 16,384, v: 64.', eq('24,640')], check=24640, tol=1e-9)
K.calc('x', 'Encoder states for 40 source words, 30 decoder steps. How many dot-product scores in total?', '1200', 'N per step.',
       ['Each step scores all 40 states.', '30 steps.', eq('1,200 scores, O(NT)')], check=1200, tol=1e-9)

# ---------------------------------------------------------------- assignments
K.assign('weights', 'e', 'Attention weights',
         '<p>Write <code>attn_weights(enc, s)</code> that returns the softmax of the dot products of s with each encoder state, rounded to 4 decimals.</p>',
         '''
import math

def attn_weights(enc, s):
    pass
''', [('attn_weights([[2, 0], [-1, 2], [1, -1], [0, 1]], [1, -2])', [0.2676, 0.0002, 0.7273, 0.0049]), ('attn_weights([[1, 0], [1, 0]], [3, 3])', [0.5, 0.5]), ('attn_weights([[0, 0]], [1, 1])', [1.0])],
         '''
import math

def attn_weights(enc, s):
    e = [sum(a * b for a, b in zip(h, s)) for h in enc]
    m = max(e)
    ex = [math.exp(v - m) for v in e]
    Z = sum(ex)
    return [round(v / Z, 4) for v in ex]
''', 'Score, subtract the maximum for safety, exponentiate, normalise.', '<p>Subtracting the maximum score does not change the softmax but avoids overflow.</p>')
K.assign('context', 'm', 'The context vector',
         '<p>Write <code>context(enc, s, scale)</code>. Score with dot products, divide by √d when scale is True (d is the state size), softmax, and return the weighted sum of the encoder states rounded to 4 decimals.</p>',
         '''
import math

def context(enc, s, scale):
    pass
''', [('context([[2, 0], [-1, 2], [1, -1], [0, 1]], [1, -2], False)', [1.2622, -0.7219]), ('context([[2, 0], [-1, 2], [1, -1], [0, 1]], [1, -2], True)', [1.2995, -0.6318]), ('context([[1, 2], [3, 4]], [0, 0], False)', [2.0, 3.0])],
         '''
import math

def context(enc, s, scale):
    d = len(s)
    e = [sum(a * b for a, b in zip(h, s)) for h in enc]
    if scale:
        e = [v / math.sqrt(d) for v in e]
    m = max(e)
    ex = [math.exp(v - m) for v in e]
    Z = sum(ex)
    w = [v / Z for v in ex]
    return [round(sum(w[i] * enc[i][k] for i in range(len(enc))), 4) for k in range(d)]
''', 'Keep the full precision weights for the sum, round only at the end.', '<p>With s = 0 every score is 0, so the context is the plain average of the states.</p>')
K.assign('additive', 'h', 'Additive attention scores',
         '<p>Write <code>additive_scores(enc, s, W1, W2, v)</code> that returns v<sup>T</sup>tanh(W1 h + W2 s) for every encoder state h, rounded to 4 decimals. W1 and W2 are lists of rows.</p>',
         '''
import math

def additive_scores(enc, s, W1, W2, v):
    pass
''', [('additive_scores([[1, 0]], [0, 1], [[1, 0], [0, 1]], [[1, 0], [0, 1]], [1, 1])', [1.5232]), ('additive_scores([[0, 0], [1, 1]], [0, 0], [[1, 0], [0, 1]], [[1, 0], [0, 1]], [1, -1])', [0.0, 0.0]), ('additive_scores([[2, 0]], [0, 0], [[1, 0]], [[0, 0]], [2])', [1.9281])],
         '''
import math

def additive_scores(enc, s, W1, W2, v):
    mv = lambda M, x: [sum(a * b for a, b in zip(r, x)) for r in M]
    out = []
    ws = mv(W2, s)
    for h in enc:
        z = [math.tanh(a + b) for a, b in zip(mv(W1, h), ws)]
        out.append(round(sum(a * b for a, b in zip(v, z)), 4))
    return out
''', 'Multiply, add, tanh, then dot with v.', '<p>In the third test W1 has one row, so the attention hidden size is 1 and the score is 2 tanh(2).</p>')

K.must('Attention idea', 'At each decoder step, look directly at all encoder states and focus on the relevant ones. A dynamic context per step solves the bottleneck.')
K.must('Equations', 'e<sub>i</sub> = s<sub>t</sub><sup>T</sup>h<sub>i</sub>, α = softmax(e), a<sub>t</sub> = ∑ α<sub>i</sub>h<sub>i</sub>, then predict from [a<sub>t</sub>, s<sub>t</sub>].')
K.must('Lecture problem', 'Scores 2, −5, 3, −2, weights 0.2676, 0.0002, 0.7273, 0.0049, context ≈ [1.262, −0.722].')
K.must('Variants', 'Dot (same size), multiplicative s<sup>T</sup>Wh, reduced rank (Us)<sup>T</sup>(Vh), additive v<sup>T</sup>tanh(W<sub>1</sub>h + W<sub>2</sub>s), scaled by 1 ÷ √d.')
K.must('Benefits', 'Better NMT, no bottleneck, gradient shortcuts, interpretable weights and soft alignment learned for free. Leads to self-attention and transformers.')

T = K.topic(
    slug='attention', topic='nn-attention', step=(4, 'Translation, attention and decoding', 'nn-seq2seq', 'Translate and generate text: the encoder-decoder model as a conditional language model, the bottleneck, attention with its worked problem, and greedy, beam and sampling decoders.', 'Masters'),
    title='Attention in encoder-decoder models', short='Attention', badge='4.2', minutes=45, added='2026-11-01',
    lead='Let every decoder step look back at the whole source: scores, softmax and the context vector, the lecture problem worked to four decimals, the scoring variants and why attention changed NLP.',
    desc='The attention idea and dynamic context, the three steps score, softmax and weighted sum, the dot-product problem with encoder states [2, 0], [−1, 2], [1, −1], [0, 1] and decoder state [1, −2], multiplicative, reduced rank, additive and scaled scores with their parameter counts, and the benefits from better translation to soft alignment.',
    summary='Attention steps, the lecture problem, scoring variants and the benefits of attention.',
    keywords=['attention', 'context vector', 'dot product', 'multiplicative', 'additive', 'scaled dot product', 'alignment'],
    recap='<p>Attention scores every encoder state against the current decoder state, turns the scores into weights with softmax and mixes the states into a context vector. It removes the bottleneck, eases gradient flow, shows an alignment, and is the building block of transformers.</p>')
