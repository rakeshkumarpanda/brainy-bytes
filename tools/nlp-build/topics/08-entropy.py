# Chapter 3.2: surprisal, entropy, codes and redundancy. Source: lectures 4 to 6 (Shannon and Turing at Bell Labs,
# the weight of evidence, the u after q, Shannon's n-th order approximations, surprisal and entropy, the 8 sided die
# and coin activities, Hartley units, what entropy does not measure, the reading lamp activity and the 50% redundancy
# of English). Numbers marked Brown come from the study notes, which computed them on the Brown corpus.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('entropy', r'''
# Entropy is the average surprisal: H = sum of p * log2(1/p)
import math

def entropy(probs):
    return sum(p * math.log2(1 / p) for p in probs if p > 0)   # 0 log 0 counts as 0

print("fair coin     ", round(entropy([0.5, 0.5]), 3))
print("coin 0.9/0.1  ", round(entropy([0.9, 0.1]), 3))
print("8 sided die   ", round(entropy([1 / 8] * 8), 3))
print("loaded die    ", round(entropy([0.5, 0.1, 0.1, 0.1, 0.1, 0.1]), 3))
print("certain event ", round(entropy([1.0, 0.0]), 3))
''')

K.code('huffman', r'''
# The Huffman method. Keep merging the two least likely items, then read codes from the root
import heapq

probs = {"a": 0.4, "b": 0.3, "c": 0.2, "d": 0.1}
heap = [(p, i, {s: ""}) for i, (s, p) in enumerate(probs.items())]
heapq.heapify(heap)
order = len(heap)
while len(heap) > 1:
    p1, i1, low = heapq.heappop(heap)            # least likely
    p2, i2, high = heapq.heappop(heap)           # next least likely
    left, right = (low, high) if i1 < i2 else (high, low)   # the older item goes left
    codes = {s: "0" + c for s, c in left.items()}
    codes.update({s: "1" + c for s, c in right.items()})
    heapq.heappush(heap, (p1 + p2, order, codes))
    order += 1

codes = heap[0][2]
print(codes)
print("average length:", round(sum(probs[s] * len(c) for s, c in codes.items()), 3), "bits")
''')

K.code('context', r'''
# How much does one letter of context help? Compare H(next letter) with H(next letter | previous letter)
import math
text = "the theme of the thesis is that the theory then thins out"

def H(counts):
    n = sum(counts.values())
    return -sum(c / n * math.log2(c / n) for c in counts.values())

uni, pairs = {}, {}
for a, b in zip(text, text[1:]):
    uni[b] = uni.get(b, 0) + 1
    pairs.setdefault(a, {})
    pairs[a][b] = pairs[a].get(b, 0) + 1

n = len(text) - 1
cond = sum(sum(nxt.values()) / n * H(nxt) for nxt in pairs.values())
print("H(next letter)                 =", round(H(uni), 3), "bits")
print("H(next letter | previous one)  =", round(cond, 3), "bits")
''')

K.lesson('surprisal', 'Information is surprise', f'''
<p>In 1943 Alan Turing visited Bell Labs in New York, where Claude Shannon worked. They could not discuss their secret war work, but both were asking the same question: how can information and computation be described with mathematics? Turing had broken Enigma messages by tracking how each new clue changed the probability of a guess. Shannon turned the same idea into a theory of communication, published in 1948.</p>
<p>The professor's example: "Keep the flower on the table" tells you little that is new. "Keep the flower on the laptop" is surprising, so it tells you more. Information and surprise are the same quantity.</p>
{fxs(
    fx('Surprisal of one outcome', '<i>I</i>(<i>x</i>) = −log₂ <i>p</i>(<i>x</i>) = log₂ ' + frac('1', '<i>p</i>(<i>x</i>)'), 'Measured in bits. A certain event (p = 1) gives 0 bits. Every halving of the probability adds exactly 1 bit.', key=True),
    fx('Units', 'log₂ → bits, &nbsp; ln → nats, &nbsp; log₁₀ → hartleys', '1 nat = 1.4427 bits and 1 hartley = 3.3219 bits. Changing the base only rescales.'))}
{steps('Why a logarithm? The proof', [
    'We want a measure I(p) of the information in an outcome of probability p.',
    'Rule 1: a certain event tells us nothing, so I(1) = 0.',
    'Rule 2: rarer is more informative, so I falls as p rises.',
    'Rule 3: for independent events information adds, so I(p · q) = I(p) + I(q).',
    'The only continuous functions with f(pq) = f(p) + f(q) are f(p) = c log p. Rule 2 makes c negative.',
    eq('So I(p) = −log p, up to the choice of base.')])}
<h3>Turing's weight of evidence</h3>
{steps('How a clue changes a probability', [
    'Hypothesis: the U-boat is in square A. Before any clue, 100 squares are equally likely, so P = 0.01 and the uncertainty is log₂ 100 = 6.64 bits.',
    'A radio intercept is 20 times more likely if the boat is in A. Turing measured this as 10 log₁₀ 20 = 13.0 decibans.',
    'Bayes in odds form: posterior odds = prior odds × 20 = (0.01 ÷ 0.99) × 20 = 0.202.',
    eq('P(A | clue) = 0.202 ÷ 1.202 = 0.168'),
    'If later clues narrow it to 5 equal squares, uncertainty falls to log₂ 5 = 2.32 bits. The clues gave 6.64 − 2.32 = 4.32 bits of information.'])}
{note('Because these measures are logarithms, independent pieces of evidence simply add. That is the reason Turing, Hartley and Shannon all used logs.', 'tip')}
''', kw=['surprisal', 'self information', 'information', 'bits', 'nats', 'hartleys', 'Shannon', 'Turing', 'weight of evidence'])

K.lesson('entropy', 'Entropy: average surprise', f'''
<p>Surprisal measures one outcome. Entropy measures a whole random variable: it is the surprisal you expect on average. A student in class spotted the link: it has the shape of an expected value, E[X] = Σ x p(x), with x replaced by log 1/p(x).</p>
{fxs(
    fx("Shannon's entropy", '<i>H</i>(<i>X</i>) = −∑<sub><i>x</i></sub> <i>p</i>(<i>x</i>) log₂ <i>p</i>(<i>x</i>) = E[ −log₂ <i>p</i>(<i>X</i>) ]', 'The average uncertainty, the expected surprise, and the fewest bits per outcome any code can use on average. 0 log 0 is taken as 0.', key=True),
    fx('Bounds', '0 ≤ <i>H</i>(<i>X</i>) ≤ log₂ <i>n</i>', 'H = 0 only when one outcome is certain. H = log₂ n only when all n outcomes are equally likely.', key=True))}
{viz('entropy')}
{code('entropy')}
{table(['Source', 'Probabilities', 'Entropy'], [
    ['Fair coin', '½, ½', '1 bit'], ['Coin with P(heads) = 0.9', '0.9, 0.1', '0.469 bits'], ['Coin with P(heads) = 0.99', '0.99, 0.01', '0.081 bits'],
    ['Fair 8 sided die', '⅛ each', '3 bits'], ['Fair 6 sided die', '⅙ each', '2.585 bits'], ['Loaded die', 'P(6) = 0.5, others 0.1', '2.161 bits'], ['Certain event', '1, 0', '0 bits']])}
{steps('Class activity: entropy of a fair 8 sided die', [
    'X is the face shown, with p(i) = 1/8 for i = 1 to 8.',
    'H(X) = −Σ (1/8) log₂(1/8). All eight terms are equal.',
    'So H = −8 × (1/8) × log₂(1/8) = −log₂(1/8).',
    eq('log₂(1/8) = −3, so H = 3 bits'),
    'Meaning: each roll can be sent with a 3 digit binary code, 001, 010, … and 000 for 8.'])}
{deep('Proofs of the bounds', '<p>Lower bound: each p is between 0 and 1, so log p ≤ 0 and every term −p log p ≥ 0. A sum of non negative terms is non negative. Upper bound: log is concave, so Jensen\'s inequality gives E[log Z] ≤ log E[Z]. Take Z = 1/p(X). Then H = E[log 1/p(X)] ≤ log E[1/p(X)] = log Σ p(x)/p(x) = log n, with equality only when every p(x) = 1/n.</p><p>Hartley (1928) had already measured a message of n symbols from an alphabet of s as n log s, assuming all symbols equally likely. Shannon\'s formula gives exactly log s per symbol in that case and less when the symbols are unequal.</p>')}
<h3>What entropy does not measure</h3>
<p>ABABABAB and AABBBABA both contain half A and half B, so their single symbol entropy is 1 bit each. Yet the first is perfectly predictable. Entropy looks only at how often each symbol occurs, not at their order. Language depends on history, so we also need entropy given the context, which is the next lesson and chapter 3.3.</p>
''', kw=['entropy', 'expected surprise', 'uncertainty', 'binary entropy', 'Hartley', 'Jensen', 'maximum entropy', 'uniform distribution'])

K.lesson('coding', 'Entropy as the shortest code', f'''
<p>How many bits are needed to send the numbers 1 to 8? A student said 0 to 7 needs 3 bits but 8 needs 4. What matters is the number of different values, not their labels: 8 values need 3 bits, with 8 written as 000. In general a fixed length code for n values needs ⌈log₂ n⌉ bits. For 26 letters that is 5, since 2⁴ = 16 is too few and 2⁵ = 32 is enough.</p>
{fxs(
    fx('Fixed length code', 'bits = ⌈log₂ <i>n</i>⌉', '20 amino acids need 5 bits, 100 words need 7, 50,000 words need 16.'),
    fx('Source coding theorem', '<i>H</i>(<i>X</i>) ≤ <i>L̄</i> &lt; <i>H</i>(<i>X</i>) + 1', 'No lossless code can average fewer than H bits per symbol. The best symbol by symbol code, Huffman, is within 1 bit.', key=True))}
<p>When the probabilities are unequal, we do better than a fixed length code by giving frequent symbols short codes and rare symbols long ones, as Morse code does with E and T. Huffman's algorithm builds the best such code.</p>
{viz('huffman')}
{steps('Huffman for a 0.4, b 0.3, c 0.2, d 0.1', [
    'Entropy: H = 0.529 + 0.521 + 0.464 + 0.332 = 1.846 bits.',
    'Merge the two smallest, c and d, into a node of 0.3.',
    'Now a 0.4, b 0.3, cd 0.3. Merge b and cd into 0.6.',
    'Merge a and the 0.6 node into the root, 1.0.',
    'Read the codes: a = 0, b = 10, c = 110, d = 111. No code starts another, so decoding is never ambiguous.',
    eq('L̄ = 0.4 × 1 + 0.3 × 2 + 0.2 × 3 + 0.1 × 3 = 1.9 bits ≥ H = 1.846')])}
{code('huffman')}
{scene('why a ZIP file is small', '<p>ZIP uses DEFLATE, which first replaces repeated strings with pointers back to an earlier copy (LZ77) and then gives frequent symbols short Huffman codes. Ordinary English text compresses to about 2 to 3 bits per character from the 8 bits of ASCII. Shannon\'s theorem says no lossless method can beat the true entropy of the source.</p>')}
''', kw=['source coding', 'Huffman', 'prefix code', 'code length', 'compression', 'ZIP', 'DEFLATE', 'fixed length code'])

K.lesson('redundancy', 'Context and redundancy', f'''
<p>Wherever q appears in English, the u after it is almost certain. The u carries almost no new information, so it is redundant. Shannon asked how much of English is like this.</p>
{steps('How redundant is the u after q? (Brown)', [
    'Without context, u is 2.24% of all characters, so seeing a u carries −log₂ 0.0224 = 5.48 bits.',
    'After q, Brown has 4,936 u out of 5,006 q, so P(u | q) = 0.986.',
    eq('Surprisal of u after q = −log₂ 0.986 = 0.020 bits'),
    'The context q removed about 5.46 bits. The few exceptions are names such as Iraq and abbreviations such as Q.'])}
<h3>Shannon's approximations to English</h3>
<p>Without a computer, Shannon generated text from a book. For a second order letter sample he opened a random page, found the current letter and wrote down the letter that followed it. Each order uses one more letter of context.</p>
{table(['Order', 'Constraint', "Shannon's sample"], [
    ['0', 'All 27 symbols equally likely', 'XFOML RXKHRJFFJUJ ZLPWCFWKCYJ'],
    ['1', 'English letter frequencies', 'OCRO HLI RGWR NIMILWIS EU LL'],
    ['2', 'Letter pairs match English', 'ON IE ANTSOUTINYS ARE T INCTORE ST'],
    ['3', 'Letter triples match English', 'IN NO IST LAT WHEY CRATICT FROURE'],
    ['Words, 2', 'Word pairs match English', 'THE HEAD AND IN FRONTAL ATTACK ON AN ENGLISH WRITER']])}
{viz('shannon')}
<h3>The reading lamp activity</h3>
{table(['Context so far', 'Class guesses', 'Choices'], [
    ['A ___', 'any noun', 'huge'], ['A SMALL ___', 'bus, book, kitchen, kid', 'drastically fewer'], ['A SMALL OBLONG ___', 'table, desk, board', 'a surprising word raises uncertainty for a moment'],
    ['… OBLONG READING ___', 'lamp', 'almost certain'], ['… LAMP ON THE D___', 'desk', 'one letter removes almost all doubt']])}
<p>On Brown the next word has 10.44 bits of entropy with no context, like choosing from about 1,389 equally likely words. One word of context cuts it to 6.52 bits (about 92 choices). After "united" the next word is nearly fixed: "states" follows 392 times out of 482.</p>
{code('context')}
{fxs(
    fx('Redundancy', '<i>R</i> = 1 − ' + frac('<i>H</i>', '<i>H</i><sub>max</sub>'), 'R = 0 for random text. R near 1 means most of the text could be predicted and removed.', key=True),
    fx("Shannon's estimate for English", '<i>R</i> = 1 − ' + frac('2.3', 'log₂ 26') + ' = 1 − ' + frac('2.3', '4.70') + ' ≈ 51%', 'With about 8 letters of context each character carries about 2.3 bits, not 5. English is roughly half redundant.'))}
{note('Ths sntnc s stll rdbl. Removing the vowels deletes about 38% of the letters but almost none of the information, because vowels are predictable from the consonants. That is redundancy you can see.', 'tip')}
{ladder(
    '<p>A surprising word carries more information than an expected one. Entropy is the average surprise. Because English is full of patterns, about half of every message could be guessed.</p>',
    '<p>Surprisal is −log₂ p and entropy H = −Σ p log₂ p lies between 0 and log₂ n. Huffman codes come within one bit of H. Shannon\'s n-th order approximations and the 50% redundancy estimate show how context lowers uncertainty.</p>',
    '<p>For sequences the right quantity is the entropy rate lim H(X<sub>n</sub> | X<sub>1</sub> … X<sub>n−1</sub>). Shannon\'s 1951 guessing experiments bounded English at roughly 0.6 to 1.3 bits per character with long context. Plug in estimates on finite corpora are biased low at high orders because contexts are seen once.</p>',
    '<p>Modern language models are compressors: their cross entropy in bits per character is an upper bound on the entropy rate of text, and large models reach under 1 bit per character on English. Arithmetic coding with a neural model turns that prediction directly into compression, which is why prediction and compression are studied as one problem.</p>')}
''', kw=['redundancy', 'u after q', 'n-th order approximation', 'Shannon', 'context', 'reading lamp', 'conditional entropy', 'English entropy'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What is the entropy of a fair coin?', ['0 bits', '0.5 bits', '1 bit', '2 bits'], 2,
       'Two equal outcomes.', 'H = −2 × ½ log₂ ½ = 1 bit.')
K.quiz('e', 'What is the entropy of a fair 8 sided die?', ['1 bit', '3 bits', '8 bits', '0.125 bits'], 1,
       'log₂ 8.', 'Eight equally likely outcomes give log₂ 8 = 3 bits.')
K.quiz('e', 'An event with probability 1 carries how much information?', ['1 bit', '0 bits', 'Infinite', 'Depends on the base'], 1,
       'Nothing new is learned.', '−log 1 = 0.')
K.quiz('e', 'What is the unit of entropy when the logarithm has base 10?', ['bit', 'nat', 'hartley', 'byte'], 2,
       'Named after a scientist.', 'Base 10 gives hartleys (also called bans). Base e gives nats.')
K.quiz('m', 'When is the entropy of n outcomes largest?', ['When one outcome is certain', 'When all outcomes are equally likely', 'When n = 2', 'Never bounded'], 1,
       'Most choice means most uncertainty.', 'H reaches log₂ n only for the uniform distribution.')
K.quiz('m', 'ABABABAB and AABBBABA have the same single symbol entropy. Why does entropy miss that the first is predictable?', ['It is computed wrongly', 'It uses only symbol frequencies, not their order', 'Entropy depends on length', 'A and B are vowels'], 1,
       'Look at what H depends on.', 'H(X) depends only on p(A) and p(B). Order needs conditional entropy or the entropy rate.')
K.quiz('m', 'How many bits does a fixed length code need for 26 letters?', ['4', '5', '6', '26'], 1,
       '2⁴ = 16, 2⁵ = 32.', '⌈log₂ 26⌉ = 5.')
K.quiz('m', 'In a Huffman code, frequent symbols get', ['Long codes', 'Short codes', 'Random codes', 'Codes of 8 bits'], 1,
       'Like E in Morse code.', 'Merging the least likely items first pushes rare symbols deep into the tree, so they get long codes.')
K.quiz('h', 'Why is the u after q nearly free of information?', ['u is a vowel', 'P(u | q) ≈ 0.986, so its surprisal is about 0.02 bits', 'q is rare', 'u is short'], 1,
       'Compute −log₂ P(u | q).', 'An almost certain event carries almost no surprise.')
K.quiz('h', "Shannon estimated English redundancy at about", ['10%', '25%', '50%', '90%'], 2,
       '2.3 bits of 4.7 to 5.', '1 − 2.3/4.70 ≈ 51%, roughly half.')
K.quiz('h', 'The source coding theorem says the average code length L̄ of the best lossless code satisfies', ['L̄ < H', 'H ≤ L̄ < H + 1', 'L̄ = log₂ n', 'L̄ = 2H'], 1,
       'Entropy is the limit.', 'No code beats H, and Huffman is always within one bit of it.')
K.quiz('x', 'Why are high order plug in entropy estimates on a million word corpus too optimistic?', ['Computers round numbers', 'Most long contexts occur once, so their next symbol looks certain', 'Entropy cannot be estimated', 'Brown is too large'], 1,
       'Think of data sparsity.', 'With one observation per context the estimated conditional entropy is 0, which is over fitting.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'What is the surprisal, in bits, of an outcome with probability 1/8?', '3', '−log₂ p.',
       ['Surprisal = −log₂ p.', '1/8 = 2⁻³.', eq('−log₂ 2⁻³ = 3 bits')], check=3)
K.calc('e', 'What is the entropy in bits of a fair 4 sided die?', '2', 'Equal outcomes give log₂ n.',
       ['p = 1/4 for each face.', 'H = −4 × ¼ × log₂ ¼.', eq('H = −log₂ ¼ = 2 bits')], check=2)
K.calc('e', 'A source emits A, B, C, D with probabilities 1/2, 1/4, 1/8, 1/8. What is H in bits?', '1.75', 'Weight each surprisal by its probability.',
       ['Surprisals: 1, 2, 3, 3 bits.', 'H = ½ × 1 + ¼ × 2 + ⅛ × 3 + ⅛ × 3.', eq('H = 0.5 + 0.5 + 0.375 + 0.375 = 1.75 bits')], check=1.75)
K.calc('m', 'What is the entropy of a coin with P(heads) = 0.9? Three decimals.', '0.469', 'Two terms.',
       ['−0.9 log₂ 0.9 = 0.9 × 0.152 = 0.137.', '−0.1 log₂ 0.1 = 0.1 × 3.322 = 0.332.', eq('H = 0.137 + 0.332 = 0.469 bits')], check=0.4689955935892812, tol=0.0005)
K.calc('m', 'A die has P(6) = 0.5 and 0.1 for each other face. What is its entropy in bits? Three decimals.', '2.161', 'One term for 6 and five equal terms.',
       ['−0.5 log₂ 0.5 = 0.5.', 'Each other face: −0.1 log₂ 0.1 = 0.332, five of them give 1.661.', eq('H = 0.5 + 1.661 = 2.161 bits'), 'Less than the fair die\'s 2.585.'], check=2.1609640474436813, tol=0.0005)
K.calc('m', 'Huffman codes a = 0, b = 10, c = 110, d = 111 for probabilities 0.4, 0.3, 0.2, 0.1. What is the average code length?', '1.9', 'Σ p × length.',
       ['0.4 × 1 = 0.4.', '0.3 × 2 = 0.6.', '0.2 × 3 + 0.1 × 3 = 0.9.', eq('L̄ = 0.4 + 0.6 + 0.9 = 1.9 bits')], check=1.9, tol=0.001)
K.calc('m', 'How many bits is one hartley? Four decimals.', '3.3219', 'Convert log base 10 into log base 2.',
       ['1 hartley is the information of a 1 in 10 choice.', 'In bits that is log₂ 10.', eq('log₂ 10 = 3.3219 bits')], check=3.321928094887362, tol=0.00005)
K.calc('h', 'u is 2.24% of Brown characters, but P(u | q) = 0.986. How many bits of surprisal does the context q remove? Two decimals.', '5.46', 'Subtract the two surprisals.',
       ['Without context: −log₂ 0.0224 = 5.48 bits.', 'After q: −log₂ 0.986 = 0.020 bits.', eq('5.48 − 0.02 = 5.46 bits')], check=5.480357457491845 - 0.02031589653891395, tol=0.005)
K.calc('h', 'English carries about 2.3 bits per character over a 26 letter alphabet. What is its redundancy in percent, to the nearest whole number?', '51', 'R = 1 − H/H_max.',
       ['H<sub>max</sub> = log₂ 26 = 4.70 bits.', 'H / H<sub>max</sub> = 2.3 ÷ 4.70 = 0.489.', eq('R = 1 − 0.489 ≈ 51%')], check=100 * (1 - 2.3 / 4.700439718141092), tol=0.5)
K.calc('h', 'A U-boat is in one of 100 equal squares. A clue is 20 times likelier if it is in square A. What is P(A | clue)? Three decimals.', '0.168', 'Use odds.',
       ['Prior odds = 0.01 ÷ 0.99 = 0.0101.', 'Posterior odds = 0.0101 × 20 = 0.202.', eq('P = 0.202 ÷ (1 + 0.202) ≈ 0.168')], check=0.16806722689075632, tol=0.0005)
K.calc('x', 'With long context English may carry 1.3 bits per character over 27 symbols. What is the redundancy in percent? One decimal.', '72.7', 'H_max = log₂ 27.',
       ['H<sub>max</sub> = log₂ 27 = 4.755 bits.', 'H / H<sub>max</sub> = 1.3 ÷ 4.755 = 0.273.', eq('R = 1 − 0.273 = 72.7%'), 'An ideal compressor would need about 1,300 bits for 1,000 characters instead of 8,000 in ASCII.'], check=100 * (1 - 1.3 / 4.754887502163468), tol=0.05)

# ---------------------------------------------------------------- assignments
K.assign('entropy', 'e', 'Compute entropy',
         '<p>Write <code>entropy(probs)</code> that returns −Σ p log₂ p rounded to 3 decimals, treating 0 log 0 as 0.</p>',
         '''
import math

def entropy(probs):
    # your code here
    pass
''', [('entropy([0.5, 0.5])', 1.0), ('entropy([1/8] * 8)', 3.0), ('entropy([0.9, 0.1])', 0.469), ('entropy([1.0, 0.0])', 0.0)],
         '''
import math

def entropy(probs):
    return round(sum(-p * math.log2(p) for p in probs if p > 0), 3)
''', 'Skip zero probabilities. log2(0) would be an error.', '<p>The last test is the certain event from class: no uncertainty at all.</p>')
K.assign('avglen', 'm', 'Average code length',
         '<p>Write <code>avg_length(probs, codes)</code>. Both are dictionaries keyed by symbol. Return Σ p × len(code) rounded to 3 decimals.</p>',
         '''
def avg_length(probs, codes):
    # your code here
    pass
''', [("avg_length({'a': 0.4, 'b': 0.3, 'c': 0.2, 'd': 0.1}, {'a': '0', 'b': '10', 'c': '110', 'd': '111'})", 1.9),
      ("avg_length({'A': 0.5, 'B': 0.25, 'C': 0.125, 'D': 0.125}, {'A': '0', 'B': '10', 'C': '110', 'D': '111'})", 1.75),
      ("avg_length({'x': 1.0}, {'x': '0'})", 1.0)],
         '''
def avg_length(probs, codes):
    return round(sum(p * len(codes[s]) for s, p in probs.items()), 3)
''', 'Loop over the symbols and weight each code length by its probability.', '<p>For the dyadic source the average equals the entropy, 1.75 bits, which is the best possible.</p>')
K.assign('condH', 'h', 'Entropy of the next letter',
         '<p>Write <code>cond_entropy(text)</code> that returns H(next letter | previous letter) in bits, rounded to 3 decimals, using every adjacent pair of characters in text: Σ over previous letters a of P(a) × H(next | a), where P(a) is the share of pairs that start with a.</p>',
         '''
import math

def cond_entropy(text):
    # your code here
    pass
''', [("cond_entropy('abababab')", 0.0), ("cond_entropy('aaaa')", 0.0), ("cond_entropy('abba')", 0.667)],
         '''
import math

def cond_entropy(text):
    pairs = {}
    for a, b in zip(text, text[1:]):
        pairs.setdefault(a, {})
        pairs[a][b] = pairs[a].get(b, 0) + 1
    n = len(text) - 1
    total = 0.0
    for nxt in pairs.values():
        m = sum(nxt.values())
        h = -sum(c / m * math.log2(c / m) for c in nxt.values())
        total += m / n * h
    return round(total, 3)
''', 'Group pairs by their first letter, compute the entropy of each group, and weight it by the group size.',
         '<p>abababab has single letter entropy 1 bit but conditional entropy 0: the previous letter fixes the next. In abba, after b the next is b or a with equal chance (1 bit), and 2 of the 3 pairs start with b, so the answer is 2/3.</p>')

K.must('Surprisal', 'I(x) = −log₂ p(x). p = 1 gives 0 bits, each halving adds 1 bit. Bits, nats, hartleys.')
K.must('Entropy', 'H = −Σ p log₂ p = expected surprise. 0 ≤ H ≤ log₂ n. Coin 1 bit, 8 sided die 3 bits, certain event 0.')
K.must('Codes', 'Fixed length needs ⌈log₂ n⌉ bits. Huffman merges the two least likely. H ≤ L̄ < H + 1. Example 1.9 against H 1.846.')
K.must('Redundancy', 'R = 1 − H/H_max. English about 2.3 of 4.7 bits per letter, so about 50% redundant. u after q carries 0.02 bits.')
K.must('Limits of H', 'Single symbol entropy ignores order (ABAB has 1 bit). Language needs conditional entropy: context reduces uncertainty.')

T = K.topic(
    slug='entropy', topic='entropy', step=(3, 'Information and surprise', 'nlp-info', 'Measure how predictable language is with Zipf\'s law, entropy, mutual information and the noisy channel.', 'College and masters'),
    title='Surprise, entropy and redundancy', short='Entropy', badge='3.2', minutes=45,
    lead='Measure information as surprise, compute entropy for coins, dice and words, build the shortest code with Huffman, and see how context makes English about half redundant.',
    desc="Shannon and Turing, surprisal and why it is a logarithm, entropy with its bounds and proofs, the class die and coin activities, units, Huffman coding and the source coding theorem, the u after q, Shannon's n-th order approximations, the reading lamp activity and the redundancy of English.",
    summary='Surprisal, entropy and its bounds, Huffman codes and the source coding limit, Shannon\'s approximations, context and the 50% redundancy of English.',
    keywords=['entropy', 'surprisal', 'information theory', 'Shannon', 'Huffman', 'redundancy', 'bits', 'source coding'],
    recap='<p>Information is surprise, −log₂ p. Entropy is the average surprise and the shortest possible average code length. Context makes the next symbol more predictable, which is why English is about half redundant.</p>')
