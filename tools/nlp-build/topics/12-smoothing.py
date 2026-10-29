# Chapter 4.3: smoothing. Source: lecture 8 (question 3 and the problem of zeros, the Berkeley Restaurant table,
# <UNK>, the bag of fruit, Laplace and add-k with the proof that they sum to 1, the corrected answer sheet, absolute
# discounting, Good-Turing, Witten-Bell, Kneser-Ney, Katz backoff and its problems, interpolation with its proof, tuning
# lambda on held out data) and problems D1 to E10 of the problem bank.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('laplace', r'''
# Laplace (add-one) bigram for "Sam I do like linguistics", V = 7 with <unk>
from collections import Counter
from math import log10
corpus = ["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"]
hist, bi = Counter(), Counter()
for line in corpus:
    t = ["<s>"] + line.split() + ["</s>"]
    for h, w in zip(t, t[1:]):
        hist[h] += 1
        bi[(h, w)] += 1
vocab = {"I", "am", "Sam", "do", "like", "</s>", "<unk>"}
V, k = len(vocab), 1

t = ["<s>"] + [w if w in vocab else "<unk>" for w in "Sam I do like linguistics".split()] + ["</s>"]
lp = 0
for h, w in zip(t, t[1:]):
    p = (bi[(h, w)] + k) / (hist[h] + k * V)
    lp += log10(p)
    print(f"P({w} | {h}) = ({bi[(h, w)]} + 1) / ({hist[h]} + 7) = {p:.4f}")
print("log10 P =", round(lp, 5), " PP =", round(10 ** (-lp / 6), 4))
''')

K.code('kn', r'''
# Kneser-Ney: how many different words come before each word?
from collections import Counter
corpus = ["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"]
pairs = set()
for line in corpus:
    t = ["<s>"] + line.split() + ["</s>"]
    pairs.update(zip(t, t[1:]))

before = Counter(w for h, w in pairs)
types = len(pairs)
for w in ["I", "Sam", "</s>", "do", "like", "am"]:
    print(w, " comes after", before[w], "different words  P_cont =", round(before[w] / types, 4))
''')

K.code('interp', r'''
# Interpolation: 0.7 x MLE bigram + 0.3 x Laplace unigram, for every factor of S3
from collections import Counter
from math import log10
corpus = ["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"]
hist, bi, uni = Counter(), Counter(), Counter()
for line in corpus:
    t = ["<s>"] + line.split() + ["</s>"]
    uni.update(t[1:])
    for h, w in zip(t, t[1:]):
        hist[h] += 1
        bi[(h, w)] += 1
N, V, lam = 22, 7, 0.7

t = ["<s>", "Sam", "I", "do", "like", "<unk>", "</s>"]
lp = 0
for h, w in zip(t, t[1:]):
    p_bi = bi[(h, w)] / hist[h] if hist[h] else 0.0
    p_uni = (uni[w] + 1) / (N + V)
    p = lam * p_bi + (1 - lam) * p_uni
    lp += log10(p)
print("log10 P =", round(lp, 5), " PP =", round(10 ** (-lp / 6), 4))
''')

K.code('gt', r'''
# Good-Turing on the 14 seen bigram types of the activity corpus
from collections import Counter
counts = [3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1]
N = sum(counts)
Nc = Counter(counts)
print("N =", N, " N1, N2, N3 =", Nc[1], Nc[2], Nc[3])
print("mass for all unseen bigrams = N1 / N =", round(Nc[1] / N, 4))
for c in [1, 2]:
    print("c =", c, " c* = (c + 1) N(c+1) / Nc =", (c + 1) * Nc[c + 1] / Nc[c])
''')

K.lesson('zeros', 'Two kinds of zero', f'''
<p>Question 3 of the activity asked for the probability of S3 = Sam I do like linguistics. The first four bigrams are fine. Then the model needs P(linguistics | like), and linguistics never occurred in training. One zero factor makes the whole product 0, the log −∞ and the perplexity infinite. A model that does that cannot be compared with any other.</p>
{table(['', 'Out of vocabulary word', 'Unseen n-gram of known words'], [
    ['Example', '"linguistics" was never seen at all', '"am do": both words were seen, never together'],
    ['Even the unigram is', '0', 'fine'],
    ['Fix', 'Map it to an &lt;UNK&gt; token', 'Smoothing, backoff or interpolation']])}
<h3>Sparsity is the normal state</h3>
<p>The slide showed bigram counts from 9,222 sentences of the Berkeley Restaurant Project. The table is mostly zeros: "i to" and "i chinese" never occur, even though "I want to eat Chinese food" is a fine sentence. The toy corpus shows the same effect in miniature.</p>
{viz('bigramtable')}
{steps('Why more context means more zeros', [
    'With V = 10,000 words a unigram model has about 10⁴ parameters, a bigram 10⁸ and a trigram 10¹².',
    'A corpus of 10⁶ tokens contains at most 10⁶ different trigrams.',
    'So at least 99.9999% of possible trigrams are never seen.',
    'The toy trigram gives P(I | I do) = 0 for "Sam I do I like", although both bigrams "I do" and "do I" were seen. The bigram model gave 0.0096.'])}
{viz('ngramlm', test='Sam I do I like', n='3')}
{deep('Should a zero always be smoothed away?', '<p>A student asked why we back off when we really want the trigram. The professor\'s answer used "John eats blue". That trigram is missing because the sentence is nonsense, and its absence is informative. Backing off to the frequent bigram "John eats" would give the nonsense a sizeable probability. The same goes for "I eats". Some zeros are accidental (the corpus is too small), some are structural (the grammar rules them out), and counts alone cannot tell them apart. Better discounting, class based models and neural models reduce the damage.</p>')}
''', kw=['zero probability', 'OOV', 'unseen bigram', 'sparsity', 'Berkeley Restaurant Project', 'parameters', 'John eats blue', 'structural zeros'])

K.lesson('laplace', '<UNK>, Laplace and add-k', f'''
<p>Step one: add a special token &lt;UNK&gt; to the vocabulary and map every unseen test word to it. "Sam I do like linguistics" becomes "Sam I do like &lt;UNK&gt;". The vocabulary grows from 6 to V = 7. But &lt;UNK&gt; has count 0 in training, so the MLE still gives it 0. Step two is smoothing.</p>
{fxs(
    fx('Laplace (add-one)', 'P<sub>Lap</sub>(<i>w</i>) = ' + frac('C(<i>w</i>) + 1', '<i>N</i> + <i>V</i>') + ', &nbsp; P<sub>Lap</sub>(<i>w</i> | <i>h</i>) = ' + frac('C(<i>h w</i>) + 1', 'C(<i>h</i>) + <i>V</i>'), 'V counts the types the model can predict: here 7, with &lt;/s&gt; and &lt;UNK&gt; but not &lt;s&gt;.', key=True),
    fx('Add-k', 'P(<i>w</i> | <i>h</i>) = ' + frac('C(<i>h w</i>) + <i>k</i>', 'C(<i>h</i>) + <i>kV</i>'), 'A smaller k, such as 0.5 or 0.01, steals less from the seen words. Choose k on a dev set.'))}
<h3>The bag of fruit</h3>
<p>The professor's analogy: a bag holds 2 bananas and 2 apples. Someone asks for an orange and there is none. You want an orange in the bag, but the bag should keep its proportions. So if you add one orange, you also add one apple and one banana. That is why we add 1 to every count and grow the denominator by V.</p>
{viz('addk')}
{steps('Proof that Laplace still sums to 1', [
    'Unigram: Σ<sub>w</sub> (C(w) + 1) = Σ C(w) + Σ 1 = N + V.',
    'Divide by N + V: the total is (N + V) ÷ (N + V) = 1.',
    'Bigram, fixed history h: Σ<sub>w</sub> (C(h w) + 1) = C(h) + V, using Σ<sub>w</sub> C(h w) = C(h).',
    eq('Σ<sub>w</sub> P<sub>Lap</sub>(w | h) = (C(h) + V) ÷ (C(h) + V) = 1'),
    'The same argument with k gives C(h) + kV. Adding 1 only to &lt;UNK&gt; would leave the others unnormalised.'])}
{viz('ngramlm', test='Sam I do like linguistics', k=1, unk=True)}
{steps('Laplace bigram for S3', [
    'Factors: (3+1)/(5+7) = 1/3, (3+1)/(5+7) = 1/3, (1+1)/(5+7) = 1/6, (1+1)/(2+7) = 2/9.',
    'P(&lt;UNK&gt; | like) = (0+1)/(3+7) = 1/10, and P(&lt;/s&gt; | &lt;UNK&gt;) = (0+1)/(0+7) = 1/7.',
    eq('P = 1/3 × 1/3 × 1/6 × 2/9 × 1/10 × 1/7 = 1/17010 = 5.8789 × 10⁻⁵'),
    'log₁₀ P = −4.23070, PP = 5.0713, PP1 = 7.0168.',
    'The Laplace unigram gives 4.3576 × 10⁻⁶ and PP 7.8245, so the bigram still wins once both are smoothed.'])}
{code('laplace')}
{note('The answer sheet got this one wrong twice. It wrote P(linguistics | like) = 0.01 instead of 1/10. Then it multiplied in the unigram values 0.034 and 0.207 in brackets, which is neither a Laplace bigram nor a proper backoff, and does not sum to 1. SRILM\'s vocabulary also contains &lt;s&gt; (its file lists 8 unigrams), so its add-one numbers can differ slightly. In the exam, state your V.', 'warn')}
<p>Add-one has a cost. Rare words gain a lot (2 → 3 is +50%) while frequent words lose (5/22 = 0.227 drops to 6/29 = 0.207). With a real vocabulary of 50,000 types, add-one hands most of the probability to words never seen. That is why better methods exist.</p>
''', kw=['UNK', 'Laplace smoothing', 'add-one', 'add-k', 'bag of fruit', 'normalisation proof', 'answer sheet', 'reconstituted counts'])

K.lesson('discount', 'Better smoothing: discounting', f'''
<p>Add-k gives every unseen word the same share. The better methods take a little from each seen count and give the freed mass to unseen words in proportion to a lower order model. The slide named four.</p>
{fxs(
    fx('Absolute discounting', 'P(<i>w</i> | <i>h</i>) = ' + frac('max(C(<i>h w</i>) − <i>d</i>, 0)', 'C(<i>h</i>)') + ' + λ(<i>h</i>) P(<i>w</i>), &nbsp; λ(<i>h</i>) = ' + frac('<i>d</i> · N₁₊(<i>h</i> •)', 'C(<i>h</i>)'), 'Subtract a fixed d of about 0.75 from every seen count. N₁₊(h •) is the number of different words seen after h.', key=True),
    fx('Good-Turing', '<i>c</i>* = (<i>c</i> + 1) ' + frac('<i>N</i><sub><i>c</i>+1</sub>', '<i>N<sub>c</sub></i>') + ', &nbsp; P(unseen) = ' + frac('<i>N</i>₁', '<i>N</i>'), 'N<sub>c</sub> = number of types seen exactly c times. Things seen once tell you how much is still unseen.'),
    fx('Witten-Bell', 'λ(<i>h</i>) = ' + frac('N₁₊(<i>h</i> •)', 'N₁₊(<i>h</i> •) + C(<i>h</i>)'), 'A history followed by many different words is likely to be followed by a new one.'),
    fx('Kneser-Ney', 'P<sub>cont</sub>(<i>w</i>) = ' + frac('|{<i>v</i> : C(<i>v w</i>) &gt; 0}|', 'number of bigram types'), 'Absolute discounting, but the lower order model counts how many different words come before w, not how often w occurs.', key=True))}
{viz('smoothrow')}
{steps('Problem D10: Kneser-Ney after "like" with d = 0.75', [
    'Different words before each token: I 3, Sam 3, &lt;/s&gt; 3, do 2, like 2, am 1. There are 14 bigram types.',
    'P<sub>cont</sub>: I = Sam = &lt;/s&gt; = 3/14, do = like = 2/14, am = 1/14. Compare the MLE unigram, where am and do tie at 2/22.',
    'like occurs 3 times, followed by &lt;/s&gt; twice and Sam once, so λ = 0.75 × 2 ÷ 3 = 0.5.',
    eq('P<sub>KN</sub>(&lt;/s&gt; | like) = (2 − 0.75)/3 + 0.5 × 3/14 = 0.4167 + 0.1071 = 0.5238'),
    'P<sub>KN</sub>(Sam | like) = 0.0833 + 0.1071 = 0.1905. Unseen: I 0.1071, do and like 0.0714, am 0.0357. Total 1.'])}
{code('kn')}
<p>The textbook example for Kneser-Ney is "San Francisco". Francisco is a frequent word, but it almost only follows San. In a new context it should get a low backoff probability, and the continuation count gives it exactly that, while a plain unigram would rate it highly.</p>
{viz('goodturing')}
{code('gt')}
{note('Chen and Goodman (1998) compared all of these. Modified Kneser-Ney with interpolation was the most accurate classic n-gram smoother, and it is still the default in toolkits such as KenLM. In assignment 2 it also won on the Brown corpus.', 'exam')}
''', kw=['absolute discounting', 'Good-Turing', 'Witten-Bell', 'Kneser-Ney', 'continuation probability', 'San Francisco', 'Chen and Goodman', 'frequency of frequencies'])

K.lesson('backoff', 'Backoff, interpolation and choosing λ', f'''
<p>When the trigram has no evidence, use the bigram, and if that has none, the unigram. There are two ways to combine the levels.</p>
{fxs(
    fx('Backoff (Katz 1987)', 'P<sub>BO</sub>(<i>w</i> | <i>h</i>) = P*(<i>w</i> | <i>h</i>) if C(<i>h w</i>) &gt; 0, else α(<i>h</i>) P<sub>BO</sub>(<i>w</i> | shorter <i>h</i>)', 'Non linear: use the highest order with evidence. P* is discounted and α hands exactly the freed mass to the lower order, so the result sums to 1.'),
    fx('Linear interpolation', 'P̂(<i>w</i> | <i>h</i>) = λ₃ P(<i>w</i> | <i>u v</i>) + λ₂ P(<i>w</i> | <i>v</i>) + λ₁ P(<i>w</i>), &nbsp; Σ λ = 1, λ ≥ 0', 'Always mix all levels. Proof of normalisation: Σ<sub>w</sub> P̂ = λ₃ · 1 + λ₂ · 1 + λ₁ · 1 = 1.', key=True))}
{steps('Problem E9: Katz backoff after "do" with d = 0.5', [
    'do is followed once by I and once by like, so P*(I | do) = P*(like | do) = (1 − 0.5)/2 = 0.25. Left over β = 0.5.',
    'Unseen followers: Sam, am, do and &lt;/s&gt;, with unigram mass (5 + 2 + 2 + 5)/22 = 14/22.',
    eq('α(do) = 0.5 ÷ (14/22) = 11/14 = 0.7857'),
    'P(Sam | do) = P(&lt;/s&gt; | do) = α × 5/22 = 0.1786, P(am | do) = P(do | do) = 0.0714. Total 1.',
    'Without α the sum would be 0.5 + 14/22 = 1.136, not a distribution.'])}
{steps('Problem E4: interpolating S3, λ = 0.7', [
    'Each factor = 0.7 × MLE bigram + 0.3 × Laplace unigram.',
    'Sam | &lt;s&gt;: 0.7 × 0.6 + 0.3 × 0.2069 = 0.4821. The same for I | Sam. do | I: 0.1710. like | do: 0.3914.',
    '&lt;UNK&gt; | like: 0.7 × 0 + 0.3 × 1/29 = 0.0103. &lt;/s&gt; | &lt;UNK&gt;: 0.7 × 0 + 0.3 × 6/29 = 0.0621.',
    eq('P ≈ 9.99 × 10⁻⁶, log₁₀ P = −5.0005, PP = 6.814'),
    'Nothing is zero any more, and the seen part keeps most of its bigram strength.'])}
{viz('ngramlm', test='Sam I do like linguistics', unk=True, mix=True)}
{code('interp')}
<h3>Choosing λ</h3>
<p>The professor's answer to "what will the λ values be?" was the standard machine learning recipe: split the data into train, dev and test. Train the counts, try λ values on dev, keep the one with the lowest dev perplexity, and report the test perplexity once.</p>
{viz('lambdagrid')}
{table(['λ', '0.1', '0.3', '0.5', '0.7', '0.9'], [['dev PP', '7.248', '6.605', '6.438', '6.814', '8.924']])}
<p>Grid search works for one or two values. A finer search puts the minimum near λ = 0.48 with PP ≈ 6.43. For many λ values, such as one per bucket of history counts in Jelinek-Mercer smoothing, the EM algorithm maximises held out likelihood and never makes it worse from one step to the next.</p>
{deep('Stupid backoff', '<p>Brants and colleagues (2007) built translation systems on web scale data with a shortcut: use the relative frequency if the n-gram was seen, otherwise 0.4 times the score of the shorter history, with no discounting. For "do I am Sam" with a trigram it gives 0.2 × 1 × (0.4 × 0.4) × 0.5 × 1 = 0.016. It is not a probability, since a row can sum to more than 1, so no true perplexity can be computed. With enough data it ranks candidates well.</p>')}
{ladder(
    '<p>Never let a model say "impossible" about a sentence that could happen. Borrow a little probability from what was seen and share it with what was not.</p>',
    '<p>&lt;UNK&gt; handles unknown words. Add-k is simple but crude. Discounting methods (absolute, Good-Turing, Witten-Bell, Kneser-Ney) take a little from seen counts. Backoff uses the highest order with evidence. Interpolation mixes all orders with λ tuned on dev data.</p>',
    '<p>Every smoother must keep each conditional distribution normalised: Laplace by adding kV to the denominator, backoff through α, interpolation through Σλ = 1. Kneser-Ney\'s continuation count is the marginal constraint that makes lower order models predict well in new contexts.</p>',
    '<p>Kneser-Ney is a limiting case of a hierarchical Pitman-Yor process (Teh 2006). Neural models avoid zeros with a softmax, and research still uses n-gram statistics for retrieval, data deduplication and checking test set contamination.</p>')}
''', kw=['backoff', 'Katz', 'alpha', 'interpolation', 'lambda', 'dev set', 'grid search', 'EM', 'stupid backoff', 'Jelinek-Mercer'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What does &lt;UNK&gt; fix?', ['Unseen bigrams of known words', 'Words never seen in training', 'Underflow', 'Long sentences'], 1,
       'It is one token for every unknown word.', 'Unknown test words are mapped to &lt;UNK&gt;, which then needs smoothing too.')
K.quiz('e', 'Laplace smoothing adds', ['1 to every count and V to the denominator', '1 only to unseen words', 'V to every count', 'k to the denominator only'], 0,
       'Keep the bag in proportion.', 'Adding 1 to each of V counts adds V to the total.')
K.quiz('e', 'In linear interpolation the λ values must', ['Be equal', 'Be non negative and sum to 1', 'Sum to 0', 'Be larger than 1'], 1,
       'Problem E2: 0.6 + 0.6 gives a sum of 1.2.', 'Only then is the mixture a probability distribution.')
K.quiz('e', 'Which method won in Chen and Goodman\'s comparison?', ['Add-one', 'Good-Turing', 'Modified Kneser-Ney with interpolation', 'Stupid backoff'], 2,
       'It also won assignment 2.', 'Interpolated modified Kneser-Ney is the most accurate classic smoother.')
K.quiz('m', 'Why does add-one smoothing work badly with a large vocabulary?', ['It is slow', 'It gives too much probability to the many unseen words', 'It does not sum to 1', 'It ignores &lt;/s&gt;'], 1,
       'kV in the denominator grows with V.', 'With 50,000 types most of the mass moves to words never seen.')
K.quiz('m', 'Good-Turing estimates the total probability of all unseen events as', ['N₀ / N', 'N₁ / N', '1 / V', 'k / N'], 1,
       'Use the things seen once.', 'The singletons predict how much is still unseen.')
K.quiz('m', 'Kneser-Ney gives "Francisco" a low lower order probability because', ['It is rare', 'It follows very few different words', 'It is long', 'It is a name'], 1,
       'Continuation, not frequency.', 'Francisco is frequent but nearly always follows San.')
K.quiz('m', 'Backoff differs from interpolation in that it', ['Always mixes all orders', 'Uses the lower order only when the higher order has no evidence', 'Needs no discount', 'Uses no unigram'], 1,
       'Non linear.', 'Backoff switches levels, interpolation always blends them.')
K.quiz('h', 'What is the problem with backing off for "John eats blue"?', ['The bigram is unseen', 'The trigram is missing because the phrase is nonsense, but backoff still gives it a sizeable probability', 'Backoff makes it 0', 'There is no unigram'], 1,
       'Unseen does not always mean sparse.', 'Some zeros are informative. Backoff treats every zero as missing data.')
K.quiz('h', 'In Katz backoff, what is α(h) for?', ['To make seen probabilities larger', 'To hand exactly the discounted mass to the lower order so the row sums to 1', 'To choose the order', 'To count types'], 1,
       'Problem E9.', 'Without α the row after "do" would sum to 1.136.')
K.quiz('h', 'Why is stupid backoff not a probability?', ['It uses logs', 'Seen n-grams are not discounted, so a row can sum to more than 1', 'It ignores unigrams', 'It needs λ'], 1,
       'Nothing is taken from the seen counts.', 'Adding 0.4 times lower order scores on top of full relative frequencies overshoots 1.')
K.quiz('x', 'With many λ values (one per history bucket), they are best set by', ['Grid search on test', 'EM on held out data', 'Setting all to 1', 'Laplace'], 1,
       'Maximise held out likelihood.', 'EM never decreases the held out likelihood from one iteration to the next.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Laplace unigram with N = 22 and V = 7: what is P(&lt;UNK&gt;)? Four decimals.', '0.0345', '(0 + 1) ÷ (22 + 7).',
       ['C(&lt;UNK&gt;) = 0.', 'Denominator N + V = 29.', eq('P = 1/29 = 0.0345')], check=1 / 29, tol=0.0001)
K.calc('e', 'Laplace bigram: P(like | do) with C(do like) = 1, C(do) = 2, V = 7? Four decimals.', '0.2222', '(1 + 1) ÷ (2 + 7).',
       ['Numerator 1 + 1 = 2.', 'Denominator 2 + 7 = 9.', eq('2/9 = 0.2222')], check=2 / 9, tol=0.0001)
K.calc('e', 'λ = 0.7: P(am | I) = 0.4 and P(am) = 2/22. What is the interpolated value? Four decimals.', '0.3073', '0.7 × bigram + 0.3 × unigram.',
       ['0.7 × 0.4 = 0.28.', '0.3 × 0.0909 = 0.0273.', eq('0.28 + 0.0273 = 0.3073')], check=0.7 * 0.4 + 0.3 * 2 / 22, tol=0.0001)
K.calc('m', 'Add-one bigram of &lt;s&gt; Sam I am &lt;/s&gt; with V = 7? Give it in units of 10⁻³, two decimals.', '6.17', 'Four smoothed factors.',
       ['(3+1)/(5+7) = 1/3 twice.', '(2+1)/(5+7) = 1/4 and (1+1)/(2+7) = 2/9.', eq('1/3 × 1/3 × 1/4 × 2/9 = 1/162 = 6.17 × 10⁻³'), 'The MLE gave 0.072: smoothing lowers seen sentences.'], check=1000 / 162, tol=0.005)
K.calc('m', 'Good-Turing: N₁ = 8, N₂ = 4, N₃ = 2 over N = 22 tokens. What is the re-estimated count c*(2)?', '1.5', '(c + 1) N₃ ÷ N₂.',
       ['c = 2, so use N₃ and N₂.', '(2 + 1) × 2 = 6.', eq('c*(2) = 6 ÷ 4 = 1.5')], check=1.5, tol=1e-9)
K.calc('m', 'Same counts: what total probability does Good-Turing give to unseen bigrams? Three decimals.', '0.364', 'N₁ ÷ N.',
       ['N₁ = 8 types seen once.', 'N = 1×8 + 2×4 + 3×2 = 22.', eq('8 ÷ 22 = 0.364')], check=8 / 22, tol=0.0005)
K.calc('m', 'Absolute discounting, d = 0.5, history like (C = 3, followers &lt;/s&gt; 2 and Sam 1), MLE unigram. What is P(&lt;/s&gt; | like)? Four decimals.', '0.5758', 'Discounted count plus λ × P(&lt;/s&gt;).',
       ['λ = 0.5 × 2 ÷ 3 = 1/3.', 'Discounted part: (2 − 0.5)/3 = 0.5.', 'Lower order: 1/3 × 5/22 = 0.0758.', eq('0.5 + 0.0758 = 0.5758')], check=0.5 + 5 / 66, tol=0.0001)
K.calc('h', 'Add-k with k = 0.5 on S3 (V = 7): what is log₁₀ P? Five decimals.', '−4.04734', 'Six factors (C + 0.5) ÷ (C(h) + 3.5).',
       ['Sam | &lt;s&gt; = 3.5/8.5, I | Sam = 3.5/8.5, do | I = 1.5/8.5.', 'like | do = 1.5/5.5, &lt;UNK&gt; | like = 0.5/6.5, &lt;/s&gt; | &lt;UNK&gt; = 0.5/3.5.', 'Product = 63/702559 = 8.96722 × 10⁻⁵.', eq('log₁₀ P = −4.04734, PP = 4.7267')], check=-4.04734, tol=0.00002)
K.calc('h', 'Kneser-Ney, d = 0.75: P<sub>KN</sub>(Sam | like) with P<sub>cont</sub>(Sam) = 3/14 and λ(like) = 0.5? Four decimals.', '0.1905', '(1 − 0.75)/3 + 0.5 × 3/14.',
       ['C(like Sam) = 1, C(like) = 3.', '(1 − 0.75)/3 = 0.0833.', '0.5 × 3/14 = 0.1071.', eq('0.0833 + 0.1071 = 0.1905')], check=0.25 / 3 + 0.5 * 3 / 14, tol=0.0001)
K.calc('h', 'Three way interpolation λ₃ = 0.5, λ₂ = 0.3, λ₁ = 0.2: P(am | Sam I) = 1/3, P(am | I) = 0.4, P(am) = 2/22. Result? Four decimals.', '0.3048', 'Weighted sum.',
       ['0.5 × 1/3 = 0.1667.', '0.3 × 0.4 = 0.12.', '0.2 × 0.0909 = 0.0182.', eq('0.1667 + 0.12 + 0.0182 = 0.3048')], check=0.5 / 3 + 0.12 + 0.2 * 2 / 22, tol=0.0001)
K.calc('x', 'Katz backoff after do (d = 0.5, followers I 1 and like 1). Unseen followers have unigram mass 14/22. What is α(do)? Four decimals.', '0.7857', 'β ÷ unseen unigram mass.',
       ['Discounted seen: (1 − 0.5)/2 = 0.25 each, total 0.5.', 'β = 1 − 0.5 = 0.5.', eq('α = 0.5 ÷ (14/22) = 11/14 = 0.7857')], check=11 / 14, tol=0.0001)

# ---------------------------------------------------------------- assignments
K.assign('addk', 'm', 'An add-k bigram with &lt;unk&gt;',
         '<p>Write <code>addk_logprob(corpus, s, k)</code>. Map test words not seen in training to &lt;unk&gt;. The vocabulary is the training words, &lt;/s&gt; and &lt;unk&gt;. Return log₁₀ P(s) under the add-k bigram (with &lt;s&gt; and &lt;/s&gt;) rounded to 5 decimals.</p>',
         '''
from math import log10

def addk_logprob(corpus, s, k):
    # your code here
    pass
''', [('addk_logprob(["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"], "Sam I do like linguistics", 1)', -4.2307),
      ('addk_logprob(["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"], "Sam I do like linguistics", 0.5)', -4.04734)],
         '''
from collections import Counter
from math import log10

def addk_logprob(corpus, s, k):
    hist, bi, words = Counter(), Counter(), set()
    for line in corpus:
        words.update(line.split())
        t = ["<s>"] + line.split() + ["</s>"]
        for a, b in zip(t, t[1:]):
            hist[a] += 1
            bi[(a, b)] += 1
    V = len(words) + 2
    t = ["<s>"] + [w if w in words else "<unk>" for w in s.split()] + ["</s>"]
    return round(sum(log10((bi[(a, b)] + k) / (hist[a] + k * V)) for a, b in zip(t, t[1:])), 5)
''', 'V is the number of training word types plus 2.', '<p>k = 1 reproduces the Laplace answer 1/17010. k = 0.5 is problem D5.</p>')
K.assign('pcont', 'h', 'Kneser-Ney continuation probabilities',
         '<p>Write <code>p_cont(corpus)</code> that returns a dict from each predicted token (words and &lt;/s&gt;) to the number of different tokens that precede it, divided by the number of different bigram types. Round to 4 decimals.</p>',
         '''
def p_cont(corpus):
    # your code here
    pass
''', [('p_cont(["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"])["am"]', 0.0714),
      ('p_cont(["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"])["</s>"]', 0.2143),
      ('p_cont(["San Francisco", "San Francisco", "a new city"])["Francisco"]', 0.1429)],
         '''
def p_cont(corpus):
    pairs = set()
    for line in corpus:
        t = ["<s>"] + line.split() + ["</s>"]
        pairs.update(zip(t, t[1:]))
    out = {}
    for a, b in pairs:
        out[b] = out.get(b, 0) + 1
    return {w: round(n / len(pairs), 4) for w, n in out.items()}
''', 'Use a set of bigram types so repeats count once.', '<p>Francisco appears twice but only ever after San, so it gets one continuation out of seven bigram types.</p>')
K.assign('interp', 'm', 'Interpolated sentence perplexity',
         '<p>Write <code>interp_ppl(corpus, s, lam)</code>: each factor is lam × MLE bigram + (1 − lam) × Laplace unigram, with unknown words mapped to &lt;unk&gt; and V = training types + 2. An unseen history gives an MLE bigram of 0. Return the perplexity over words + &lt;/s&gt;, rounded to 4 decimals.</p>',
         '''
from math import log10

def interp_ppl(corpus, s, lam):
    # your code here
    pass
''', [('interp_ppl(["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"], "Sam I do like linguistics", 0.7)', 6.8142),
      ('interp_ppl(["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"], "Sam I do like linguistics", 0.5)', 6.4376)],
         '''
from collections import Counter
from math import log10

def interp_ppl(corpus, s, lam):
    hist, bi, uni = Counter(), Counter(), Counter()
    for line in corpus:
        t = ["<s>"] + line.split() + ["</s>"]
        uni.update(t[1:])
        for a, b in zip(t, t[1:]):
            hist[a] += 1
            bi[(a, b)] += 1
    N, V = sum(uni.values()), len(uni) + 1
    t = ["<s>"] + [w if w in uni else "<unk>" for w in s.split()] + ["</s>"]
    lp = 0.0
    for a, b in zip(t, t[1:]):
        pb = bi[(a, b)] / hist[a] if hist[a] else 0.0
        lp += log10(lam * pb + (1 - lam) * (uni[b] + 1) / (N + V))
    return round(10 ** (-lp / (len(t) - 1)), 4)
''', 'uni already contains &lt;/s&gt;, so V = len(uni) + 1 for &lt;unk&gt;.', '<p>λ = 0.7 is problem E4, λ = 0.5 is the best value on the coarse grid of problem E8.</p>')

K.must('Two zeros', 'OOV word: map to &lt;UNK&gt;. Unseen n-gram of known words: smooth, back off or interpolate. One zero factor gives P = 0 and PP = ∞.')
K.must('Laplace and add-k', '(C + k) ÷ (C(h) + kV). V = 7 for the activity. S3 Laplace bigram = 1/17010, PP 5.07. Sums to 1 by adding kV.')
K.must('Discounting', 'Absolute: max(C − d, 0)/C(h) + λP(w), λ = d N₁₊/C(h). Good-Turing: c* = (c+1)N<sub>c+1</sub>/N<sub>c</sub>, unseen N₁/N. KN uses continuation counts.')
K.must('Backoff', 'Use the highest order with evidence, discounted, with α so the row sums to 1. Problem: "John eats blue", unseen is not always sparse.')
K.must('Interpolation', 'Σλ P = 1 when Σλ = 1. Tune λ on dev (S3: best near 0.48, PP 6.43), report test once. EM for many λ.')

T = K.topic(
    slug='smoothing', topic='smoothing', step=(4, 'Language models', 'nlp-lm', 'Predict the next word with n-gram models, measure them with perplexity, smooth away the zeros and run the SRILM assignment.', 'College and masters'),
    title='Unseen words and smoothing', short='Smoothing', badge='4.3', minutes=55,
    lead='Stop one unseen word from making a whole sentence impossible: &lt;UNK&gt;, add-k, Good-Turing, Kneser-Ney, backoff and interpolation, with λ tuned on held out data.',
    desc='The two kinds of zero and why sparsity grows with n, <UNK>, Laplace and add-k with the bag of fruit and the normalisation proof, the corrected answer sheet, absolute discounting, Good-Turing, Witten-Bell and Kneser-Ney, Katz backoff and its problem, linear interpolation and choosing λ on a dev set.',
    summary='<UNK>, Laplace and add-k, discounting methods and Kneser-Ney, backoff, interpolation and λ tuning.',
    keywords=['smoothing', 'UNK', 'Laplace', 'add-k', 'Good-Turing', 'Kneser-Ney', 'backoff', 'interpolation', 'lambda'],
    recap='<p>Unseen words go to &lt;UNK&gt;, unseen n-grams get a share of probability taken from the seen ones. Add-k is the simplest and the weakest. Discounting with a good lower order model, best of all Kneser-Ney, does far better. Backoff switches to a shorter history, interpolation blends them all, and λ is chosen on dev data, never on test.</p>')
