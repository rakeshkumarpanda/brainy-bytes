# Chapter 3.3: two variables. Source: lectures 5 and 6 (joint and conditional entropy, the weather and umbrella example,
# the chain rule and the John went to Patna sentence, mutual information and its symmetry, studying and passing,
# New Delhi and collocations, KL divergence and cross entropy, the appendix on the noisy channel and acress).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('umbrella', r'''
# All the entropies of the weather and umbrella example
import math

def H(probs):
    return -sum(p * math.log2(p) for p in probs if p > 0)

p_sunny, p_umb_sunny, p_umb_rainy = 0.6, 0.2, 0.9
joint = {("sunny", "umb"): p_sunny * p_umb_sunny, ("sunny", "none"): p_sunny * (1 - p_umb_sunny),
         ("rainy", "umb"): (1 - p_sunny) * p_umb_rainy, ("rainy", "none"): (1 - p_sunny) * (1 - p_umb_rainy)}
HX = H([p_sunny, 1 - p_sunny])
HY = H([joint[("sunny", "umb")] + joint[("rainy", "umb")], joint[("sunny", "none")] + joint[("rainy", "none")]])
HXY = H(joint.values())
print("H(X) =", round(HX, 3), " H(Y) =", round(HY, 3), " H(X,Y) =", round(HXY, 3))
print("H(Y|X) =", round(HXY - HX, 3), " I(X : Y) =", round(HX + HY - HXY, 3))
''')

K.code('pmi', r'''
# Pointwise mutual information from corpus counts
import math
N = 1_000_000
pairs = [("New", "Delhi", 2000, 500, 400), ("new", "car", 2000, 1000, 20),
         ("ice", "cream", 3000, 2500, 900), ("of", "the", 40000, 70000, 10000)]

for x, y, cx, cy, cxy in pairs:
    pmi = math.log2(cxy * N / (cx * cy))
    print(f"{x} {y}: P(y|x) = {cxy / cx:.3f}, P(y) = {cy / N:.4f}, PMI = {pmi:.2f} bits")
''')

K.code('kl', r'''
# KL divergence and cross entropy, and why KL is not symmetric
import math

def kl(p, q):
    return sum(a * math.log2(a / b) for a, b in zip(p, q) if a > 0)

def cross(p, q):
    return -sum(a * math.log2(b) for a, b in zip(p, q) if a > 0)

p = [0.7, 0.2, 0.1]          # true weather in city A
q = [0.3, 0.3, 0.4]          # a model fitted in city B
Hp = -sum(a * math.log2(a) for a in p)
print("H(p) =", round(Hp, 4), " H(p,q) =", round(cross(p, q), 4), " D(p||q) =", round(kl(p, q), 4))
print("D(q||p) =", round(kl(q, p), 4), " (a different number)")
''')

K.code('channel', r'''
# Noisy channel spelling correction: argmax over words of P(word) * P(typo | word)
candidates = {"actress": (1.4e-5, 1.2e-4), "across": (2.9e-4, 2.1e-6),
              "acres": (3.2e-5, 3.1e-5), "access": (1.8e-4, 1.0e-6)}

scores = {w: prior * channel for w, (prior, channel) in candidates.items()}
total = sum(scores.values())
for w, s in sorted(scores.items(), key=lambda kv: -kv[1]):
    print(w, f"{s:.2e}", "share", round(s / total, 3))
''')

K.lesson('joint', 'Joint and conditional entropy', f'''
<p>Language depends on history, so one variable at a time is not enough. We need the uncertainty of two variables together, and the uncertainty of one when the other is known. The professor's slide summed it up: language modelling is fundamentally about conditional probability.</p>
{fxs(
    fx('Joint entropy', '<i>H</i>(<i>X</i>, <i>Y</i>) = −∑<sub><i>x</i>,<i>y</i></sub> <i>p</i>(<i>x</i>, <i>y</i>) log₂ <i>p</i>(<i>x</i>, <i>y</i>)', 'The information needed on average to specify both values, like "New" and "Delhi" together.'),
    fx('Conditional entropy', '<i>H</i>(<i>Y</i> | <i>X</i>) = ∑<sub><i>x</i></sub> <i>p</i>(<i>x</i>) <i>H</i>(<i>Y</i> | <i>X</i> = <i>x</i>) = −∑<sub><i>x</i>,<i>y</i></sub> <i>p</i>(<i>x</i>, <i>y</i>) log₂ <i>p</i>(<i>y</i> | <i>x</i>)', 'The extra information still needed for Y once X is known. The joint probability goes outside the log, the conditional inside.', key=True),
    fx('Chain rule', '<i>H</i>(<i>X</i>, <i>Y</i>) = <i>H</i>(<i>X</i>) + <i>H</i>(<i>Y</i> | <i>X</i>)', 'Specify X, then specify Y given X. For n variables: H(X₁ … Xₙ) = Σ H(Xᵢ | X₁ … Xᵢ₋₁).', key=True))}
{note('A student guessed −Σ p(x,y) log p(x|y). That is not H(Y|X), but it is a correct formula for H(X|Y): the conditioning just runs the other way. In the umbrella example it gives 0.593 bits against 0.621 for H(Y|X).', 'warn')}
<h3>The weather and the umbrella</h3>
<p>X is the weather (sunny 0.6, rainy 0.4). Y is whether I carry an umbrella: probability 0.2 on a sunny day and 0.9 on a rainy day.</p>
{viz('jointent')}
{steps('All the entropies, step by step', [
    'Joint probabilities, multiplying along the branches: P(S, U) = 0.12, P(S, N) = 0.48, P(R, U) = 0.36, P(R, N) = 0.04.',
    'Marginals: P(U) = 0.12 + 0.36 = 0.48. So H(Y) = H(0.48) = 0.999 bits, almost a fair coin. H(X) = H(0.6) = 0.971 bits.',
    'Given sunny: H(0.2) = 0.722. Given rainy: H(0.9) = 0.469.',
    eq('H(Y|X) = 0.6 × 0.722 + 0.4 × 0.469 = 0.433 + 0.188 = 0.621 bits'),
    'Joint: H(X, Y) = −(0.12 log 0.12 + 0.48 log 0.48 + 0.36 log 0.36 + 0.04 log 0.04) = 1.592 bits.',
    eq('Chain rule check: 0.971 + 0.621 = 1.592, which matches'),
    'Knowing the weather cut the umbrella uncertainty from 0.999 to 0.621 bits, a saving of 0.378 bits.'])}
{code('umbrella')}
<h3>Does conditioning always reduce entropy?</h3>
<p>On average, yes: H(Y | X) ≤ H(Y), with equality only when X and Y are independent. For one particular value it can go up. If P(X = a) = 0.9 and Y is then always y₁, while X = b makes Y a fair coin, then H(Y) = H(0.95) = 0.286 bits but H(Y | X = b) = 1 bit. The average H(Y | X) = 0.9 × 0 + 0.1 × 1 = 0.1 bits is still lower. Brown shows the same: after "of" the next word has 8.62 bits, but after "of the" it has 11.02 bits, because once "the" is used almost any noun can follow.</p>
{steps('The chain rule for a sentence', [
    'P(John went to Patna) = P(John) · P(went | John) · P(to | John went) · P(Patna | John went to).',
    'Take −log₂: the total surprise is the sum of the four surprises.',
    'With model probabilities 0.001, 0.05, 0.4 and 0.01 the surprises are 9.97 + 4.32 + 1.32 + 6.64.',
    eq('Total = 22.25 bits, and 0.001 × 0.05 × 0.4 × 0.01 = 2 × 10⁻⁷ = 2<sup>−22.25</sup>, which matches')])}
''', kw=['joint entropy', 'conditional entropy', 'chain rule', 'umbrella example', 'conditioning reduces entropy', 'sentence probability'])

K.lesson('mutual', 'Mutual information', f'''
<p>A student called it "common information", and that is the best everyday description. Mutual information is how much knowing one variable reduces the uncertainty about the other.</p>
{fxs(
    fx('Mutual information', '<i>I</i>(<i>X</i> : <i>Y</i>) = <i>H</i>(<i>Y</i>) − <i>H</i>(<i>Y</i> | <i>X</i>) = <i>H</i>(<i>X</i>) + <i>H</i>(<i>Y</i>) − <i>H</i>(<i>X</i>, <i>Y</i>)', 'The overlap of the two entropy circles, in bits. Many textbooks put a semicolon between X and Y in this notation.', key=True),
    fx('Probability form', '<i>I</i>(<i>X</i> : <i>Y</i>) = ∑<sub><i>x</i>,<i>y</i></sub> <i>p</i>(<i>x</i>, <i>y</i>) log₂ ' + frac('<i>p</i>(<i>x</i>, <i>y</i>)', '<i>p</i>(<i>x</i>) <i>p</i>(<i>y</i>)'), 'Zero exactly when p(x, y) = p(x) p(y) for every pair, which is independence.'))}
<h3>Three facts and their proofs</h3>
<ul>
<li><b>Independent means zero.</b> If p(x, y) = p(x)p(y), every ratio inside the log is 1 and log 1 = 0. The class answered "zero, zero, zero".</li>
<li><b>Symmetric.</b> p(x, y) is the same number as p(y, x) and p(x)p(y) equals p(y)p(x), so swapping X and Y changes no term. I(X : Y) = I(Y : X).</li>
<li><b>Never negative.</b> The probability form is a KL divergence, which is never negative (next lesson). So H(Y | X) ≤ H(Y) on average.</li>
</ul>
{steps('Studying and passing', [
    '60% of students study. Of those, 90% pass. Of the rest, 20% pass.',
    'Joint: P(study, pass) = 0.54, P(study, fail) = 0.06, P(no study, pass) = 0.08, P(no study, fail) = 0.32.',
    'Marginals: P(pass) = 0.62. H(X) = H(0.6) = 0.971, H(Y) = H(0.62) = 0.958, H(X, Y) = 1.541.',
    eq('I(X : Y) = 0.971 + 0.958 − 1.541 = 0.388 bits'),
    'Cell by cell the four terms are +0.290, −0.116, −0.131 and +0.344. Single cells can be negative but the total cannot.'])}
<h3>Word pairs: New Delhi</h3>
<p>Seeing "New" sharply raises the chance that the next word is "Delhi". For one specific pair we use the pointwise version.</p>
{fxs(fx('Pointwise mutual information', 'PMI(<i>x</i>, <i>y</i>) = log₂ ' + frac('<i>p</i>(<i>x</i>, <i>y</i>)', '<i>p</i>(<i>x</i>) <i>p</i>(<i>y</i>)') + ' = log₂ ' + frac('c(<i>x y</i>) · <i>N</i>', 'c(<i>x</i>) · c(<i>y</i>)'), 'Above 0 the words attract, 0 means independent, below 0 they avoid each other. MI is the average of PMI over all pairs.', key=True))}
{viz('pmi')}
{code('pmi')}
<p>On real Brown counts, c(new) = 1,635, c(york) = 302 and c(new york) = 296 of N = 991,429 give PMI = 9.22 bits, and 98% of all "york" tokens follow "new".</p>
{table(['', 'Collocation', 'Association'], [
    ['Examples', 'New Delhi, fast food, strong tea, make a decision', 'new car, doctor and nurse'],
    ['Can a word be swapped?', 'No: quick food and powerful tea sound wrong', 'Yes: new bike, new dress'],
    ['Meaning', 'Often not built from the parts', 'Built from the parts'],
    ['PMI', 'Highest', 'Positive but lower']])}
{note('PMI over rewards rare pairs. Two words seen once, together, score log₂ N, more than New Delhi. Always use a minimum count, or a t-score or log likelihood ratio, alongside it.', 'warn')}
''', kw=['mutual information', 'PMI', 'pointwise mutual information', 'collocation', 'association', 'symmetry', 'independence', 'New Delhi'])

K.lesson('kl', 'KL divergence and cross entropy', f'''
<p>Mutual information compares two variables. Relative entropy compares two probability distributions over the same events. A student gave the right intuition: a model built on New York data, used in India, wastes bits because it expects the wrong things.</p>
{fxs(
    fx('Kullback Leibler divergence', '<i>D</i>(<i>p</i> ‖ <i>q</i>) = ∑<sub><i>x</i></sub> <i>p</i>(<i>x</i>) log₂ ' + frac('<i>p</i>(<i>x</i>)', '<i>q</i>(<i>x</i>)'), 'The average number of bits wasted by coding data from p with a code built for q.', key=True),
    fx('Cross entropy', '<i>H</i>(<i>p</i>, <i>q</i>) = −∑<sub><i>x</i></sub> <i>p</i>(<i>x</i>) log₂ <i>q</i>(<i>x</i>) = <i>H</i>(<i>p</i>) + <i>D</i>(<i>p</i> ‖ <i>q</i>)', 'Training a language model with cross entropy loss lowers the KL from the truth to the model, since H(p) is fixed by the data.', key=True))}
{viz('kl')}
{code('kl')}
{steps("Gibbs' inequality: D(p ‖ q) ≥ 0", [
    'Use ln z ≤ z − 1 for z &gt; 0, with equality only at z = 1. The line z − 1 touches ln z at z = 1 and lies above it.',
    'Put z = q(x)/p(x) and sum over x with p(x) &gt; 0: Σ p ln(q/p) ≤ Σ p (q/p − 1) = Σ q − Σ p ≤ 1 − 1 = 0.',
    'The left side is −D(p ‖ q) × ln 2, so D(p ‖ q) ≥ 0.',
    'Equality needs q/p = 1 everywhere, that is p = q.',
    'Consequences: I(X : Y) ≥ 0, H(Y | X) ≤ H(Y), and no model has lower cross entropy than the truth.'])}
{table(['Example', 'D(p ‖ q)', 'D(q ‖ p)'], [
    ['p = (0.5, 0.25, 0.25), q uniform', '0.0850 bits', '0.0817 bits'],
    ['City A weather (0.7, 0.2, 0.1) against city B (0.3, 0.3, 0.4)', '0.539 bits', '0.609 bits'],
    ['p = (0.5, 0.5, 0), q = (0.4, 0.4, 0.2)', '0.322 bits', '∞']])}
{note('If a model gives probability 0 to something that happens, KL and perplexity become infinite. That single fact is why every n-gram model in chapter 4 is smoothed, and why neural models use a softmax, which never outputs exactly 0.', 'exam')}
''', kw=['KL divergence', 'relative entropy', 'cross entropy', "Gibbs' inequality", 'asymmetric', 'domain shift', 'zero probability', 'smoothing'])

K.lesson('channel', 'The noisy channel', f'''
<p>Shannon's model of communication has a sender, an encoder, a noisy channel and a decoder. Engineers design the encoder to add just enough redundancy to correct errors. In language we cannot design the encoder, since people type and speak as they do. We can only decode: given what came out, find the most likely thing that went in.</p>
{fxs(
    fx('Noisy channel decoding', '<i>î</i> = argmax<sub><i>i</i></sub> <i>p</i>(<i>i</i> | <i>o</i>) = argmax<sub><i>i</i></sub> <i>p</i>(<i>i</i>) · <i>p</i>(<i>o</i> | <i>i</i>)', 'p(i) is the language model (how likely is this input). p(o | i) is the channel model (how likely is this output from it). Used for spelling correction, speech recognition, OCR and translation.', key=True),
    fx('Channel capacity', '<i>C</i> = max<sub><i>p</i>(<i>X</i>)</sub> <i>I</i>(<i>X</i> : <i>Y</i>)', 'A binary channel that flips 10% of bits has C = 1 − H(0.1) = 0.531 bits per use.'))}
<p>Why can p(o) be dropped? Bayes gives p(i | o) = p(i) p(o | i) ÷ p(o). The observation is fixed while we compare candidates, so p(o) is the same positive number for all of them and cannot change which is largest.</p>
{viz('noisychannel')}
{steps('Correcting "acress"', [
    'Candidates with P(word) and P(acress | word), in the style of Kernighan, Church and Gale (1990): actress 1.4e-5 and 1.2e-4, across 2.9e-4 and 2.1e-6, acres 3.2e-5 and 3.1e-5, access 1.8e-4 and 1.0e-6.',
    'Products: actress 1.68e-9, across 6.09e-10, acres 9.92e-10, access 1.80e-10.',
    eq('Winner: actress, with share 1.68 ÷ 3.46 ≈ 0.485'),
    'across is a far more common word, but turning across into acress needs an unlikely change, so its channel probability is small.'])}
{code('channel')}
{scene('voice typing an address', '<p>A delivery app hears "I will be back soonish" and "I will be bassoon dish", which sound almost the same. The acoustic model (the channel) scores both about equally. The language model knows the first is a normal sentence and the second is not, so the product picks the right one. This is the same argmax as the spelling example.</p>')}
{ladder(
    '<p>Knowing one thing can tell you about another: the weather tells you about umbrellas, "New" tells you about "Delhi". Mutual information measures how much.</p>',
    '<p>H(X,Y) = H(X) + H(Y|X), I(X : Y) = H(Y) − H(Y|X), PMI scores single word pairs, D(p‖q) ≥ 0 measures wasted bits, and the noisy channel picks argmax p(i) p(o|i).</p>',
    '<p>MI equals D(p(x,y) ‖ p(x)p(y)), which proves non negativity and subadditivity H(X,Y) ≤ H(X) + H(Y). Cross entropy loss equals entropy plus KL, so minimising it is maximum likelihood. Channel capacity is the largest MI over input distributions.</p>',
    '<p>Contrastive losses such as InfoNCE bound mutual information, I ≥ log N − L (Oord et al., 2018), which links CLIP style training to this chapter. Research studies estimating MI in high dimensions, the asymmetry of forward and reverse KL in model distillation, and noisy channel reranking in neural translation.</p>')}
''', kw=['noisy channel', 'Bayes rule', 'language model', 'channel model', 'spelling correction', 'acress', 'channel capacity', 'binary symmetric channel'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'If X and Y are independent, I(X : Y) equals', ['1', '0', 'H(X)', 'H(X, Y)'], 1,
       'Neither tells you about the other.', 'p(x,y) = p(x)p(y), every log term is log 1 = 0.')
K.quiz('e', 'Which formula is the chain rule for entropy?', ['H(X,Y) = H(X) × H(Y)', 'H(X,Y) = H(X) + H(Y|X)', 'H(X,Y) = H(X) − H(Y)', 'H(X,Y) = I(X : Y)'], 1,
       'Specify X, then Y given X.', 'The joint uncertainty splits into X and the rest of Y.')
K.quiz('e', 'In the noisy channel model, p(i) is called', ['The channel model', 'The language model', 'The capacity', 'The noise'], 1,
       'How likely is the input itself.', 'p(i) scores the input as a sentence or word, which is a language model.')
K.quiz('m', 'Knowing the weather lowered the umbrella uncertainty from 0.999 to 0.621 bits. What is 0.378?', ['H(X)', 'I(X : Y)', 'H(X, Y)', 'D(p ‖ q)'], 1,
       'The saving from knowing X.', 'H(Y) − H(Y|X) is the mutual information.')
K.quiz('m', 'Is mutual information symmetric?', ['No, I(X : Y) > I(Y : X) always', 'Yes, I(X : Y) = I(Y : X)', 'Only for binary variables', 'Only when independent'], 1,
       'p(x,y) = p(y,x).', 'Every term of the sum is unchanged when the names are swapped.')
K.quiz('m', 'Is KL divergence symmetric?', ['Yes', 'No, D(p‖q) and D(q‖p) usually differ', 'Only for uniform q', 'It is always 0'], 1,
       'Check the weather example.', '0.539 against 0.609 bits. KL is not a distance.')
K.quiz('m', 'Why is "of the" not a strong collocation despite being very frequent?', ['It is rare', 'of and the are so common they meet often by chance, so PMI is only about 1.84 bits', 'It is ungrammatical', 'PMI ignores frequency'], 1,
       'PMI divides by the chance level.', 'c(x)c(y)/N is large for two very common words, so the ratio stays small.')
K.quiz('h', 'Can H(Y | X = x) for one specific x be larger than H(Y)?', ['Never', 'Yes, but the average H(Y|X) cannot exceed H(Y)', 'Only if X = Y', 'Only for continuous variables'], 1,
       'Brown: after "of the" the next word has more entropy than after "of".', 'Pointwise conditioning can raise uncertainty, expected conditioning cannot.')
K.quiz('h', 'A model gives probability 0 to an event that occurs. Its D(p ‖ q) is', ['0', '1', 'Infinite', 'Negative'], 2,
       'log of p/0.', 'The term p log(p/0) is infinite, which is why models are smoothed.')
K.quiz('h', 'Why can P(o) be dropped when choosing argmax_i P(i | o)?', ['P(o) is always 1', 'P(o) is the same for every candidate i', 'P(o) is 0', 'It cannot be dropped'], 1,
       'o is fixed during the search.', 'Dividing all scores by the same positive constant keeps the same winner.')
K.quiz('x', 'Minimising cross entropy H(p, q) over a model q is the same as minimising', ['H(p)', 'D(p ‖ q)', 'D(q ‖ p)', 'I(X : Y)'], 1,
       'H(p, q) = H(p) + D(p ‖ q).', 'H(p) does not depend on q, so only the KL term can be lowered.')
K.quiz('x', 'Which is the capacity of a binary channel that flips each bit with probability 0.5?', ['1 bit', '0.5 bits', '0 bits', '0.531 bits'], 2,
       'The output tells you nothing.', 'C = 1 − H(0.5) = 1 − 1 = 0.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'P(sunny) = 0.6 and P(umbrella | sunny) = 0.2. What is P(sunny, umbrella)?', '0.12', 'Multiply along the branch.',
       ['p(x, y) = p(x) p(y | x).', 'p(sunny) = 0.6, p(umbrella | sunny) = 0.2.', eq('0.6 × 0.2 = 0.12')], check=0.12, tol=1e-9)
K.calc('e', 'In a 1,000,000 word corpus, c(new) = 2,000, c(car) = 1,000 and c(new car) = 20. What is PMI(new, car) in bits? Two decimals.', '3.32', 'log₂ of c(xy) N / (c(x) c(y)).',
       ['c(xy) × N = 20 × 10⁶ = 2 × 10⁷.', 'c(x) c(y) = 2,000 × 1,000 = 2 × 10⁶.', eq('PMI = log₂ 10 = 3.32 bits')], check=3.321928094887362, tol=0.005)
K.calc('e', 'H(X) = 0.971 and H(Y | X) = 0.621 bits. What is H(X, Y)?', '1.592', 'Chain rule.',
       ['Chain rule: H(X, Y) = H(X) + H(Y | X).', 'Add the two numbers.', eq('0.971 + 0.621 = 1.592 bits')], check=1.592, tol=0.0005)
K.calc('m', 'Using c(new) = 2,000, c(Delhi) = 500, c(New Delhi) = 400 and N = 10⁶, what is PMI(New, Delhi)? Two decimals.', '8.64', 'Compute the ratio first.',
       ['400 × 10⁶ = 4 × 10⁸.', '2,000 × 500 = 10⁶.', eq('PMI = log₂ 400 ≈ 8.64 bits')], check=8.643856189774725, tol=0.005)
K.calc('m', 'For the joint table P(a,0) = 0.25, P(a,1) = 0.25, P(b,0) = 0.40, P(b,1) = 0.10, what is H(X, Y)? Three decimals.', '1.861', 'Sum −p log₂ p over the four cells.',
       ['Two cells of 0.25 give 0.5 + 0.5 = 1.0.', '0.40 gives 0.529 and 0.10 gives 0.332.', eq('H(X, Y) = 1.0 + 0.529 + 0.332 = 1.861 bits')], check=1.860964047443681, tol=0.0005)
K.calc('m', 'For the same table, H(X) = 1 and H(Y) = 0.934. What is I(X : Y)? Three decimals.', '0.073', 'H(X) + H(Y) − H(X, Y).',
       ['H(X) + H(Y) = 1.934.', 'H(X, Y) = 1.861.', eq('I = 1.934 − 1.861 = 0.073 bits'), 'A weak dependence.'], check=0.07310400793180993, tol=0.0005)
K.calc('m', 'p = (0.5, 0.25, 0.25) and q = (1/3, 1/3, 1/3). What is D(p ‖ q) in bits? Four decimals.', '0.0850', 'Cross entropy minus entropy is easiest.',
       ['H(p) = 0.5 + 0.5 + 0.5 = 1.5 bits.', 'H(p, q) = −Σ p log₂ ⅓ = log₂ 3 = 1.5850.', eq('D = 1.5850 − 1.5 = 0.0850 bits')], check=0.08496250072115619, tol=0.00005)
K.calc('h', 'p = (0.7, 0.2, 0.1), q = (0.3, 0.3, 0.4). What is D(p ‖ q)? Three decimals.', '0.539', 'Three terms p log₂(p/q).',
       ['0.7 log₂(0.7/0.3) = 0.7 × 1.222 = 0.856.', '0.2 log₂(0.2/0.3) = −0.117.', '0.1 log₂(0.1/0.4) = −0.200.', eq('D = 0.856 − 0.117 − 0.200 = 0.539 bits')], check=0.5386821947912824, tol=0.0005)
K.calc('h', 'In the acress example, what share of P(word | acress) does actress get? Three decimals.', '0.485', 'Normalise the products.',
       ['Products: 1.68e-9, 6.09e-10, 9.92e-10, 1.80e-10.', 'Sum = 3.461e-9.', eq('1.68e-9 ÷ 3.461e-9 ≈ 0.485')], check=0.48540884137532503, tol=0.0005)
K.calc('h', 'What is the capacity of a binary symmetric channel that flips 10% of bits? Three decimals.', '0.531', 'C = 1 − H(0.1).',
       ['H(0.1) = −0.1 log₂ 0.1 − 0.9 log₂ 0.9 = 0.332 + 0.137 = 0.469.', 'H(Y) can reach 1 bit with equally likely inputs.', eq('C = 1 − 0.469 = 0.531 bits per use')], check=0.5310044064107188, tol=0.0005)
K.calc('x', 'Brown: c(new) = 1,635, c(york) = 302, c(new york) = 296, N = 991,429. What is PMI(new, york)? Two decimals.', '9.22', 'log₂(296 × 991,429 ÷ (1,635 × 302)).',
       ['Numerator: 296 × 991,429 = 293,462,984.', 'Denominator: 1,635 × 302 = 493,770.', 'Ratio ≈ 594.3.', eq('PMI = log₂ 594.3 ≈ 9.22 bits')], check=9.215123639631788, tol=0.005)

# ---------------------------------------------------------------- assignments
K.assign('mi', 'm', 'Mutual information from a joint table',
         '<p>Write <code>mutual_info(joint)</code>. joint is a list of rows, joint[i][j] = P(X = i, Y = j). Return I(X : Y) in bits rounded to 3 decimals.</p>',
         '''
import math

def mutual_info(joint):
    # your code here
    pass
''', [('mutual_info([[0.12, 0.48], [0.36, 0.04]])', 0.378), ('mutual_info([[0.25, 0.25], [0.40, 0.10]])', 0.073), ('mutual_info([[0.25, 0.25], [0.25, 0.25]])', 0.0)],
         '''
import math

def mutual_info(joint):
    px = [sum(r) for r in joint]
    py = [sum(c) for c in zip(*joint)]
    total = 0.0
    for i, row in enumerate(joint):
        for j, p in enumerate(row):
            if p > 0:
                total += p * math.log2(p / (px[i] * py[j]))
    return round(total, 3)
''', 'Row sums give p(x), column sums give p(y). Then use the probability form.', '<p>The first test is the umbrella example, the second is practice problem P5, the third is two independent fair coins.</p>')
K.assign('pmi', 'e', 'Rank pairs by PMI',
         '<p>Write <code>rank_pmi(pairs, N)</code>. pairs is a list of <code>[name, cx, cy, cxy]</code> with cxy &gt; 0. Return the names sorted from highest to lowest PMI.</p>',
         '''
import math

def rank_pmi(pairs, N):
    # your code here
    pass
''', [("rank_pmi([['of the', 40000, 70000, 10000], ['ice cream', 3000, 2500, 900], ['white house', 6000, 4000, 700]], 10**6)", ['ice cream', 'white house', 'of the']),
      ("rank_pmi([['a', 10, 10, 1]], 100)", ['a'])],
         '''
import math

def rank_pmi(pairs, N):
    score = lambda p: math.log2(p[3] * N / (p[1] * p[2]))
    return [p[0] for p in sorted(pairs, key=score, reverse=True)]
''', 'Compute PMI for each pair, then sort.', '<p>ice cream 6.91, white house 4.87, of the 1.84 bits. The most frequent pair is the weakest collocation.</p>')
K.assign('kl', 'h', 'KL divergence with zeros',
         '<p>Write <code>kl(p, q)</code> that returns D(p ‖ q) in bits rounded to 3 decimals. Terms with p = 0 add nothing. If some q is 0 where p &gt; 0, return the string <code>"inf"</code>.</p>',
         '''
import math

def kl(p, q):
    # your code here
    pass
''', [('kl([0.5, 0.5, 0], [0.4, 0.4, 0.2])', 0.322), ('kl([0.4, 0.4, 0.2], [0.5, 0.5, 0])', 'inf'), ('kl([0.7, 0.2, 0.1], [0.7, 0.2, 0.1])', 0.0)],
         '''
import math

def kl(p, q):
    total = 0.0
    for a, b in zip(p, q):
        if a == 0:
            continue
        if b == 0:
            return "inf"
        total += a * math.log2(a / b)
    return round(total, 3)
''', 'Check p first, then q, before taking the log.', '<p>The second test is practice problem P8: a model that rules out an event that happens pays infinitely many bits.</p>')

K.must('Joint and conditional', 'H(Y|X) = Σ p(x) H(Y|X=x) = −Σ p(x,y) log p(y|x). Chain rule H(X,Y) = H(X) + H(Y|X). Umbrella: 0.971 + 0.621 = 1.592.')
K.must('Mutual information', 'I = H(Y) − H(Y|X) = H(X) + H(Y) − H(X,Y) = Σ p(x,y) log p(x,y)/(p(x)p(y)). Symmetric, ≥ 0, 0 iff independent. Umbrella 0.378.')
K.must('PMI', 'log₂ c(xy)N/(c(x)c(y)). New Delhi 8.64, new car 3.32. Collocations score highest. Rare pairs are over rewarded.')
K.must('KL and cross entropy', 'D(p‖q) = Σ p log p/q ≥ 0, not symmetric, infinite if q = 0 where p > 0. H(p,q) = H(p) + D(p‖q).')
K.must('Noisy channel', 'argmax p(i) p(o|i): language model times channel model. acress → actress (0.485). BSC 10%: C = 0.531.')

T = K.topic(
    slug='information', topic='information', step=(3, 'Information and surprise', 'nlp-info', 'Measure how predictable language is with Zipf\'s law, entropy, mutual information and the noisy channel.', 'College and masters'),
    title='Mutual information, KL and the noisy channel', short='Information between variables', badge='3.3', minutes=45,
    lead='Measure how much one thing tells you about another, find word pairs that belong together, count the bits a wrong model wastes, and correct typos with the noisy channel.',
    desc='Joint and conditional entropy with the umbrella example, the chain rule, mutual information and its proofs, PMI and collocations such as New Delhi, KL divergence and cross entropy with Gibbs\' inequality, and noisy channel spelling correction with channel capacity.',
    summary='Joint and conditional entropy, the chain rule, mutual information and PMI, KL divergence and cross entropy, and noisy channel decoding.',
    keywords=['mutual information', 'conditional entropy', 'chain rule', 'PMI', 'collocation', 'KL divergence', 'cross entropy', 'noisy channel'],
    recap='<p>Context helps because variables share information. Conditional entropy is what remains, mutual information is what is shared, KL is the price of a wrong model, and the noisy channel combines a language model with an error model to decode.</p>')
