# Chapter 4.2: perplexity and evaluation. Source: lectures 7 and 8 (pointwise, total and average entropy of a word
# sequence, log bases, the board derivation of perplexity, the branching factor, the "He put the coffee on" example,
# PP against PP1, file level perplexity, extrinsic and intrinsic evaluation, underflow, the WSJ table, comparable
# vocabularies, never training on the test set) and problems F1 to F10 of the problem bank.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('pp', r'''
# Perplexity from per word probabilities, two equivalent routes
import math
probs = [0.2, 0.1, 0.25, 0.05, 0.4]          # He put the coffee on

bits = [-math.log2(p) for p in probs]
H = sum(bits) / len(probs)
print("surprisals:", [round(b, 3) for b in bits])
print("total =", round(sum(bits), 3), " average H =", round(H, 3), " PP = 2^H =", round(2 ** H, 3))

P = math.prod(probs)
print("root form: P^(-1/N) =", round(P ** (-1 / len(probs)), 3))
''')

K.code('file', r'''
# File perplexity is computed from the total log probability, not by averaging sentence perplexities
lp = [-2.01773, -1.14267]          # bigram log10 P of S1 and S2
words = [5, 3]

for l, w in zip(lp, words):
    print("sentence: ppl =", round(10 ** (-l / (w + 1)), 5), " ppl1 =", round(10 ** (-l / w), 5))
tot = sum(lp)
print("file: logprob =", round(tot, 5), " ppl =", round(10 ** (-tot / (sum(words) + 2)), 5),
      " ppl1 =", round(10 ** (-tot / sum(words)), 5))
''')

K.code('underflow', r'''
# Multiplying many small probabilities underflows to 0. Adding logs does not.
import math
p = 0.001 ** 1000                       # 1,000 tokens, each with probability 0.001
logp = 1000 * math.log10(0.001)          # the same thing as a sum of 1,000 logs
print("product:", p)
print("smallest double near:", 5e-324, " and 5e-325 is stored as", 5e-325)
print("sum of logs:", round(logp, 3), " PP =", round(10 ** (-logp / 1000), 3))
''')

K.code('lazy', r'''
# A model with a tiny vocabulary looks better, but only because the task changed
from collections import Counter
corpus = ["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"]
keep = {"Sam", "</s>"}

c = Counter()
for line in corpus:
    for w in line.split() + ["</s>"]:
        c[w if w in keep else "<UNK>"] += 1
N = sum(c.values())
test = [w if w in keep else "<UNK>" for w in "Sam I do I like".split() + ["</s>"]]
P = 1.0
for w in test:
    P *= c[w] / N
print(dict(c), " P =", round(P, 5), " PP =", round(P ** (-1 / len(test)), 4))
''')

K.lesson('surprise', 'From surprise to perplexity', f'''
<p>Chapter 3 measured how surprising a single event is. A sentence is a chain of events, so its surprise is the sum of the surprises of its words. The lecture built perplexity from that idea in three small steps.</p>
{fxs(
    fx('Pointwise conditional entropy', '−log₂ m(<i>w<sub>i</sub></i> | <i>h<sub>i</sub></i>)', 'The surprise of one word given its history.'),
    fx('Total surprise', '<i>H</i><sub>total</sub> = −∑<sub><i>i</i></sub> log₂ m(<i>w<sub>i</sub></i> | <i>h<sub>i</sub></i>) = −log₂ m(<i>w</i>₁ … <i>w<sub>N</sub></i>)', 'Logs turn the chain rule product into a sum.'),
    fx('Perplexity', 'PP = 2<sup><i>Ĥ</i></sup>, &nbsp; <i>Ĥ</i> = ' + frac('<i>H</i><sub>total</sub>', '<i>N</i>') + ', &nbsp; so &nbsp; PP = m(<i>w</i>₁ … <i>w<sub>N</sub></i>)<sup>−1/<i>N</i></sup>', 'Lower perplexity means the model found the text less surprising.', key=True))}
{steps('The board derivation: why 2 to the average entropy is the N-th root', [
    'Start from PP = 2<sup>Ĥ</sup> with Ĥ = H<sub>total</sub> ÷ N.',
    'Substitute H<sub>total</sub> = −log₂ m(w₁ … w<sub>N</sub>): Ĥ = −(1/N) log₂ m.',
    'Move the factor inside the log: a log x = log x<sup>a</sup>, so Ĥ = log₂ (m<sup>−1/N</sup>).',
    eq('PP = 2<sup>log₂ (m<sup>−1/N</sup>)</sup> = m<sup>−1/N</sup> = ᴺ√(1 ÷ m)')])}
{viz('perplexity')}
{steps('Worked example: He put the coffee on', [
    'Model probabilities: P(He) = 0.2, P(put | He) = 0.1, P(the | put) = 0.25, P(coffee | the) = 0.05, P(on | coffee) = 0.4.',
    'Product: 0.2 × 0.1 × 0.25 × 0.05 × 0.4 = 1.0 × 10⁻⁴.',
    'Surprises in bits: 2.322, 3.322, 2.000, 4.322, 1.322. Total 13.288 bits.',
    'Average Ĥ = 13.288 ÷ 5 = 2.658 bits per word.',
    eq('PP = 2<sup>2.658</sup> = 6.31, and the root form (10⁻⁴)<sup>−1/5</sup> = 10<sup>0.8</sup> = 6.31 agrees')])}
{code('pp')}
<h3>Perplexity is a branching factor</h3>
<p>If a model spreads its probability evenly over k words at every step, each factor is 1/k, the product is (1/k)<sup>N</sup>, and PP = ((1/k)<sup>N</sup>)<sup>−1/N</sup> = k. So a perplexity of 109 means the model is as uncertain as if it had to pick fairly among 109 words at each position. For a real model it is an effective number of choices, not a literal count.</p>
{note('Base 2 gives bits, base e gives nats, base 10 gives hartleys. Perplexity does not depend on the base as long as you raise the same base you took the log with: 2<sup>Ĥ in bits</sup> = 10<sup>Ĥ in hartleys</sup>. That is why SRILM can print log₁₀ values and still match the textbook.', 'tip')}
{deep('Are perplexity and entropy the same thing?', '<p>They move together but answer different questions. Entropy is in bits and adds: one extra bit means twice the choices. Perplexity counts the choices and multiplies. Going from 7 bits to 6 bits halves perplexity from 128 to 64. The professor called perplexity "almost proportional" to entropy. Strictly it is exponential in entropy. Ranking models by either gives the same order.</p>')}
''', kw=['perplexity', 'surprisal', 'average entropy', 'branching factor', 'derivation', 'log base', 'bits', 'hartleys'])

K.lesson('ppl1', 'PP, PP1 and whole files', f'''
<p>SRILM prints two perplexities for every sentence and for the whole file. Both use the same log probability. They differ only in what they divide by.</p>
{fxs(
    fx('ppl', 'ppl = 10<sup>−logprob ÷ (words − OOVs − zeroprobs + sentences)</sup>', 'Counts one &lt;/s&gt; per sentence: how hard is it to predict every token, including where the sentence ends?', key=True),
    fx('ppl1', 'ppl1 = 10<sup>−logprob ÷ (words − OOVs − zeroprobs)</sup>', 'Words only. The cost of predicting the end is charged to the words, so ppl1 ≥ ppl always.', key=True))}
{viz('ngramlm', test='Sam I do I like\nSam I am', view='srilm')}
{steps('The file line of the SRILM output', [
    'Sentence totals from the activity: log₁₀ P(S1) = −2.01773 with 5 words, log₁₀ P(S2) = −1.14267 with 3 words.',
    'File logprob = −2.01773 + (−1.14267) = −3.16040.',
    'Tokens: 8 words + 2 end tags = 10 for ppl, 8 for ppl1.',
    eq('ppl = 10<sup>3.16040/10</sup> = 2.07033, &nbsp; ppl1 = 10<sup>3.16040/8</sup> = 2.48342'),
    'This is not the average of 2.169 and 1.930. Perplexity is a geometric mean over tokens, so it is computed from the totals.'])}
{code('file')}
{note('For long documents PP and PP1 converge, since there is one end tag per twenty or more words. For three word toy sentences they differ a lot (1.93 against 2.40). In an exam, say which N you used and never compare PP from one model with PP1 from another.', 'exam')}
<h3>OOVs and zero probabilities in the toolkit</h3>
<p>In the demo SRILM did not print −∞ for the sentence with "linguistics". The professor put it this way: the model "kicked the culprit out". It reports the word as 1 OOV and computes logprob and perplexity over the rest. A known word with probability 0 is reported as a zeroprob and skipped in the same way. So a perplexity with OOVs is not comparable with one without. Always read the OOV and zeroprob counts on the line.</p>
''', kw=['ppl', 'ppl1', 'file perplexity', 'geometric mean', 'SRILM output', 'OOV', 'zeroprobs', 'end of sentence'])

K.lesson('evaluate', 'Evaluating language models', f'''
<p>How do we know one language model is better than another? There are two ways, and both appear in the slides.</p>
{table(['', 'Extrinsic', 'Intrinsic'], [
    ['What', 'Put the model inside an application and measure the application', 'Measure the model alone on held out text'],
    ['Examples', 'The London word order task, translation, speech recognition, spelling correction', 'Likelihood, log likelihood, perplexity on a test set'],
    ['Strength', 'Measures what we really care about', 'Cheap, fast and repeatable'],
    ['Weakness', 'Slow and expensive', 'A lower perplexity usually, but not always, gives a better application']])}
{fxs(
    fx('The three intrinsic measures', 'likelihood m(test), &nbsp; log likelihood log m(test), &nbsp; PP = m(test)<sup>−1/N</sup>', 'Higher likelihood, higher log likelihood and lower perplexity all mean the same thing, on the same test set and vocabulary.', key=True))}
<h3>Why logs: underflow</h3>
<p>A double precision number cannot hold values below about 10⁻³⁰⁸. A test set of 1,000 words with average probability 0.001 has P = 10⁻³⁰⁰⁰, which becomes exactly 0. Its log₁₀ is simply −3000, no problem at all. Toolkits add log probabilities for this reason.</p>
{code('underflow')}
<h3>The WSJ table</h3>
{table(['Model', 'Perplexity', 'Bits per word'], [['Unigram', '962', '9.91'], ['Bigram', '170', '7.41'], ['Trigram', '109', '6.77']])}
<p>Trained on 38 million words of the Wall Street Journal and tested on 1.5 million (Jurafsky and Martin). Each extra word of context cuts the effective number of choices. The gains shrink, and on finite data they eventually reverse: a 6-gram has so many unseen histories that, without very good smoothing, test perplexity rises again.</p>
<h3>Three rules from class</h3>
<ul>
<li><b>Never train on the test set.</b> An MLE model trained on the test sentence gives it the highest probability any model of its kind can, so its perplexity says nothing about new text. Tuning λ or k on the test set is the same cheating. Use a dev set.</li>
<li><b>Compare perplexities only with identical vocabularies.</b> The professor flagged this as a likely exam question. A model that maps most words to &lt;UNK&gt; finds the text easy because the task changed.</li>
<li><b>Report everything.</b> Log probability, PP and PP1, the number of words, sentences and OOVs.</li>
</ul>
{code('lazy')}
{steps('The vocabulary trick in numbers', [
    'A lazy model keeps only Sam and &lt;/s&gt;. I, am, do and like all become &lt;UNK&gt; with count 5 + 2 + 2 + 3 = 12.',
    'S1 becomes Sam &lt;UNK&gt; &lt;UNK&gt; &lt;UNK&gt; &lt;UNK&gt; &lt;/s&gt;, so P = (5/22)(12/22)⁴(5/22) = 0.00457.',
    eq('PP = 0.00457<sup>−1/6</sup> = 2.45, lower than the honest unigram\'s 5.58'),
    'Yet the lazy model cannot tell I from like. The lower number comes from the easier task, not a better model.'])}
{scene('a spelling app update', '<p>An app team reports that the new keyboard model has perplexity 40 against the old one\'s 65. Before celebrating, the reviewer asks two questions. Were both scored on the same held out messages? Do both use the same vocabulary and tokeniser? If the new model splits words into smaller pieces, its perplexity is per piece, and the two numbers measure different things.</p>')}
''', kw=['extrinsic evaluation', 'intrinsic evaluation', 'likelihood', 'underflow', 'log probability', 'WSJ', 'test set', 'dev set', 'vocabulary', 'comparability'])

K.lesson('crossent', 'Perplexity as cross entropy', f'''
<p>What a model measures on test data is not the true entropy of the language but a cross entropy: the average surprise of real text under the model's probabilities.</p>
{fxs(
    fx('Test set cross entropy', '<i>Ĥ</i> = −' + frac('1', '<i>N</i>') + ' log₂ m(<i>w</i>₁ … <i>w<sub>N</sub></i>) ≈ <i>H</i>(<i>p</i>, m) = <i>H</i>(<i>p</i>) + <i>D</i>(<i>p</i> ‖ m)', 'For long text this tends to the cross entropy of the truth p with the model m.', key=True))}
{steps('Problem F8: perplexity can never beat the truth', [
    'True next word distribution p = (0.5, 0.25, 0.25). The model q is uniform, 1/3 each.',
    'H(p) = 0.5 × 1 + 2 × 0.25 × 2 = 1.5 bits, so the best possible perplexity is 2<sup>1.5</sup> = 2.828.',
    'H(p, q) = −Σ p log₂ (1/3) = log₂ 3 = 1.585 bits, so the model\'s perplexity is 3.',
    eq('KL = 1.585 − 1.5 = 0.085 bits ≥ 0, by Gibbs\' inequality'),
    'Test perplexity estimates 2<sup>H(p,q)</sup> ≥ 2<sup>H(p)</sup>. The gap is the KL divergence from chapter 3.3.'])}
<h3>How do people predict each other?</h3>
<p>Students answered "context, shared interest, past conversations". Underneath that, the professor said, we speak the same language, and language is built from predictable units: short frequent words, "the" followed by a noun. As context grows, the number of plausible next words falls for both speaker and listener. Psycholinguists find that reading time grows roughly in line with surprisal (Hale 2001, Levy 2008, Smith and Levy 2013), which suggests the listener runs something like a language model.</p>
{note('Adding another source of information, such as tone of voice or a facial expression, can only lower conditional entropy on average: H(Y | X, Z) ≤ H(Y | X). Sarcasm is the classic case where the text misleads and the voice resolves it.', 'tip')}
{ladder(
    '<p>Perplexity says how many words the model is effectively choosing between at each step. Smaller is better.</p>',
    '<p>PP = 2<sup>Ĥ</sup> = P<sup>−1/N</sup>. ppl counts &lt;/s&gt;, ppl1 does not. Compare only on the same test set and vocabulary, after tuning on a dev set.</p>',
    '<p>Test perplexity is the exponential of cross entropy, which equals entropy plus KL, so it bounds the true entropy from above. Minimising it is maximum likelihood. Per token perplexities of models with different tokenisers must be converted to bits per character before comparing.</p>',
    '<p>Perplexity correlates imperfectly with downstream quality, especially for large models. Research studies calibration, bits per byte across tokenisers, test set contamination in web scale training data, and surprisal as a predictor of human reading times.</p>')}
''', kw=['cross entropy', 'KL divergence', 'upper bound', 'true entropy', 'human prediction', 'surprisal theory', 'reading time'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'A model gives probability 1/7 to every token. Its perplexity is', ['1', '7', '1/7', '49'], 1,
       'A uniform choice among k words gives PP = k.', '((1/7)<sup>N</sup>)<sup>−1/N</sup> = 7.')
K.quiz('e', 'Lower perplexity means', ['A worse model', 'The model found the test text less surprising', 'More OOV words', 'A bigger vocabulary'], 1,
       'PP = P<sup>−1/N</sup>.', 'Higher probability on the test text gives lower perplexity.')
K.quiz('e', 'Why do toolkits add log probabilities instead of multiplying probabilities?', ['It is more accurate for large numbers', 'Products of many small numbers underflow to 0', 'Logs are required by law', 'It changes the ranking'], 1,
       'Doubles stop near 10⁻³⁰⁸.', 'Adding logs keeps the same information without underflow.')
K.quiz('e', 'Which is an extrinsic evaluation?', ['Test set perplexity', 'Log likelihood', 'Word error rate of a speech recogniser using the model', 'Counting OOVs'], 2,
       'It measures an application.', 'Extrinsic means plugging the model into a task and measuring the task.')
K.quiz('m', 'ppl1 is always at least ppl because', ['It uses a different model', 'It divides the same log probability by fewer tokens', 'It counts OOVs', 'It uses base 2'], 1,
       'Same numerator.', 'ppl1 leaves the end tags out of the count, so the exponent is larger.')
K.quiz('m', 'S1 has PP 2.169 and S2 has PP 1.930. The file perplexity of both together is', ['Their average, 2.050', '2.070, from the total log probability over 10 tokens', '4.099', '1.930'], 1,
       'Perplexity is a geometric mean over tokens.', '10<sup>3.1604/10</sup> = 2.070, not the mean of the two values.')
K.quiz('m', 'A lazy model maps most words to &lt;UNK&gt; and gets a lower perplexity. This shows', ['It is a better model', 'Perplexities are only comparable with the same vocabulary', 'UNK is always good', 'Perplexity is broken'], 1,
       'The task changed.', 'Predicting &lt;UNK&gt; is easy. Compare models only with identical vocabularies.')
K.quiz('m', 'Changing from log₂ to log₁₀ throughout the calculation changes the perplexity by', ['A factor of 3.32', 'Nothing', 'A factor of 10', 'Squaring it'], 1,
       'Raise the base you logged with.', '2<sup>Ĥ in bits</sup> = 10<sup>Ĥ in hartleys</sup>.')
K.quiz('h', 'Why is λ tuned on a dev set, not on the test set?', ['The dev set is bigger', 'Choosing on the test set makes the test perplexity optimistically biased', 'The test set has no &lt;/s&gt;', 'λ does not affect perplexity'], 1,
       'Any choice made with the test data leaks information.', 'The reported number must come from data that played no part in any decision.')
K.quiz('h', 'In SRILM output a sentence shows "1 OOVs". Its ppl', ['Includes −∞', 'Is computed without that word, so it is not comparable with a run without OOVs', 'Is always higher', 'Is undefined'], 1,
       'The toolkit kicked the culprit out.', 'OOV words are skipped and counted separately.')
K.quiz('h', 'Going from 7 bits to 6 bits of cross entropy per word changes perplexity from', ['7 to 6', '128 to 64', '49 to 36', '10⁷ to 10⁶'], 1,
       'PP = 2<sup>Ĥ</sup>.', '2⁷ = 128, 2⁶ = 64. One bit halves the choices.')
K.quiz('x', 'Test set perplexity of any model is at least 2<sup>H(p)</sup> for the true distribution p because', ['Of the chain rule', 'Cross entropy = entropy + KL and KL ≥ 0', 'Of Zipf\'s law', 'Of underflow'], 1,
       'Problem F8.', 'H(p, m) = H(p) + D(p ‖ m) ≥ H(p).')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A 3 word sentence has log₁₀ P = −1.14267. What is its ppl (4 tokens with &lt;/s&gt;)? Four decimals.', '1.9305', '10 to the power of 1.14267 ÷ 4.',
       ['N = 3 words + 1 &lt;/s&gt; = 4.', '1.14267 ÷ 4 = 0.28567.', eq('ppl = 10<sup>0.28567</sup> = 1.9305')], check=10 ** (1.14267 / 4), tol=0.0002)
K.calc('e', 'Same sentence: what is ppl1? Four decimals.', '2.4037', 'Divide by 3 words.',
       ['ppl1 leaves out the end tag, so N = 3.', '1.14267 ÷ 3 = 0.38089.', eq('ppl1 = 10<sup>0.38089</sup> = 2.4037')], check=10 ** (1.14267 / 3), tol=0.0002)
K.calc('e', 'Convert the SRILM value −0.221849 back to a probability. One decimal.', '0.6', 'p = 10 to the log value.',
       ['SRILM stores log₁₀ p.', 'p = 10<sup>−0.221849</sup>.', eq('p = 0.6, which is 3/5 = P(Sam | &lt;s&gt;)')], check=0.6, tol=0.0005)
K.calc('m', 'Probabilities 0.2, 0.1, 0.25, 0.05, 0.4 for five words. What is the perplexity? Two decimals.', '6.31', 'Product, then the minus one fifth power.',
       ['Product = 1.0 × 10⁻⁴.', 'PP = (10⁻⁴)<sup>−1/5</sup> = 10<sup>4/5</sup>.', eq('10<sup>0.8</sup> = 6.31')], check=10 ** 0.8, tol=0.005)
K.calc('m', 'Unigram file: log₁₀ P(S1) = −4.48050 (5 words), log₁₀ P(S2) = −2.97175 (3 words). What is the file ppl? Four decimals.', '5.5619', 'Total log probability over 8 words + 2 end tags.',
       ['Total = −7.45225.', 'Tokens = 8 + 2 = 10.', eq('ppl = 10<sup>0.745225</sup> = 5.5619')], check=10 ** (7.45225 / 10), tol=0.0005)
K.calc('m', 'S2 = Sam I am has bigram P = 0.072 over 4 tokens. What is the cross entropy Ĥ in bits per token? Four decimals.', '0.9490', '−log₂ 0.072 ÷ 4.',
       ['log₂ 0.072 = ln 0.072 ÷ ln 2 = −2.63109 ÷ 0.69315 = −3.7959.', 'Divide by 4 tokens: 0.9490.', eq('Ĥ = 0.9490 bits, and 2<sup>0.9490</sup> = 1.9305 = PP')], check=0.9489783543, tol=0.0002)
K.calc('m', 'A test set of 1,000 tokens has every token at probability 0.001. What is the perplexity?', '1000', 'Uniform over 1,000 choices.',
       ['log₁₀ P = 1,000 × (−3) = −3,000. P itself would underflow.', 'PP = 10<sup>3000/1000</sup>.', eq('PP = 10³ = 1000')], check=1000, tol=0.01)
K.calc('h', 'Lazy model: P = (5/22)(12/22)⁴(5/22) over 6 tokens. What is its perplexity? Two decimals.', '2.45', 'P<sup>−1/6</sup>.',
       ['(5/22)² = 0.05165.', '(12/22)⁴ = 0.08852, so P = 0.004572.', eq('PP = 0.004572<sup>−1/6</sup> = 2.45')], check=((5 / 22) ** 2 * (12 / 22) ** 4) ** (-1 / 6), tol=0.005)
K.calc('h', 'WSJ: convert the bigram perplexity 170 to bits per word. Two decimals.', '7.41', 'log₂ PP.',
       ['Bits per word = log₂ PP.', 'log₂ 170 = ln 170 ÷ ln 2 = 5.1358 ÷ 0.6931.', eq('log₂ 170 = 7.41 bits')], check=7.409390936, tol=0.005)
K.calc('h', 'Model M1 gives five tokens 0.4, 0.3, 0.1, 0.5, 0.2. What is its PP? Three decimals.', '3.839', 'Sum the log₁₀ values first.',
       ['log₁₀: −0.39794, −0.52288, −1, −0.30103, −0.69897.', 'Total −2.92082.', eq('PP = 10<sup>2.92082/5</sup> = 3.839')], check=10 ** (2.920818754 / 5), tol=0.0005)
K.calc('x', 'For a 1,000 word text, how many orders of magnitude more probable is it under a trigram with PP 109 than under a unigram with PP 962? Whole number.', '946', 'P = PP<sup>−N</sup>, so the ratio is (962/109)<sup>1000</sup>.',
       ['Ratio = (962 ÷ 109)<sup>1000</sup> = 8.826<sup>1000</sup>.', 'log₁₀ 8.826 = 0.9458.', 'Times 1,000: 945.8.', eq('About 10<sup>946</sup>: small perplexity gaps are enormous likelihood gaps')], check=1000 * __import__('math').log10(962 / 109), tol=0.6)

# ---------------------------------------------------------------- assignments
K.assign('ppl', 'e', 'ppl and ppl1 from per token probabilities',
         '<p>Write <code>ppl(probs)</code> where probs are the probabilities of the words of one sentence followed by the probability of &lt;/s&gt;. Return a pair (ppl, ppl1), each rounded to 4 decimals.</p>',
         '''
import math

def ppl(probs):
    # your code here
    pass
''', [('ppl([0.6, 0.6, 0.2, 0.5, 0.4, 2/3])', (2.1691, 2.5325)), ('ppl([0.6, 0.6, 0.4, 0.5])', (1.9305, 2.4037)), ('ppl([0.5, 0.5])', (2.0, 4.0))],
         '''
import math

def ppl(probs):
    lp = sum(math.log10(p) for p in probs)
    n = len(probs)
    return (round(10 ** (-lp / n), 4), round(10 ** (-lp / (n - 1)), 4))
''', 'The end tag is in the list, so ppl1 divides by one fewer token.', '<p>The first two tests are S1 and S2 of the activity, and match SRILM.</p>')
K.assign('fileppl', 'm', 'File perplexity the way SRILM does it',
         '<p>Write <code>file_ppl(sents)</code>. Each item is (logprob, words, oovs, zeroprobs) for one sentence. Return (ppl, ppl1) for the whole file, rounded to 5 decimals. ppl divides by words − oovs − zeroprobs + sentences, ppl1 by words − oovs − zeroprobs.</p>',
         '''
def file_ppl(sents):
    # your code here
    pass
''', [('file_ppl([(-2.01773, 5, 0, 0), (-1.14267, 3, 0, 0)])', (2.07033, 2.48342)), ('file_ppl([(-2.08715, 5, 1, 0)])', (2.61475, 3.32497))],
         '''
def file_ppl(sents):
    lp = sum(s[0] for s in sents)
    n1 = sum(s[1] - s[2] - s[3] for s in sents)
    return (round(10 ** (-lp / (n1 + len(sents))), 5), round(10 ** (-lp / n1), 5))
''', 'Add up the log probabilities and the token counts first, then exponentiate once.', '<p>The second test is the bigram S3 without &lt;unk&gt;: SRILM skips "linguistics" and divides by 4 words + 1.</p>')
K.assign('compare', 'h', 'Which model is better, honestly?',
         '<p>Write <code>better(m1, m2)</code>. Each model is a list of per token probabilities on the same test tokens, where None marks a token the model skipped as an OOV. If either model skipped a token, return "not comparable". Otherwise return "M1" or "M2" for the one with lower perplexity.</p>',
         '''
import math

def better(m1, m2):
    # your code here
    pass
''', [('better([0.4, 0.3, 0.1, 0.5, 0.2], [0.6, 0.2, 0.05, 0.6, 0.25])', 'M1'), ('better([0.4, 0.3, 0.1, 0.5, 0.2], [0.6, 0.2, None, 0.6, 0.25])', 'not comparable'), ('better([0.1, 0.1], [0.5, 0.5])', 'M2')],
         '''
import math

def better(m1, m2):
    if None in m1 or None in m2:
        return "not comparable"
    pp = lambda m: 10 ** (-sum(math.log10(p) for p in m) / len(m))
    return "M1" if pp(m1) < pp(m2) else "M2"
''', 'Check for skipped tokens before computing anything.', '<p>Problem F10: M2 is more confident on three tokens but its 0.05 costs too much. If it skipped that token its perplexity would drop to 2.73 and it would wrongly look best.</p>')

K.must('Perplexity', 'PP = 2<sup>Ĥ</sup> = P<sup>−1/N</sup>. Uniform over k words gives PP = k. "He put the coffee on": 13.288 bits, Ĥ 2.658, PP 6.31.')
K.must('ppl and ppl1', 'Same logprob. ppl divides by words − OOV − zeroprobs + sentences, ppl1 by words − OOV − zeroprobs. File ppl from totals, not an average.')
K.must('Evaluation', 'Extrinsic (task) against intrinsic (likelihood, log likelihood, perplexity). Use logs to avoid underflow below about 10⁻³⁰⁸.')
K.must('Rules', 'Never train or tune on the test set. Compare perplexities only with the same test text and vocabulary. Report OOVs.')
K.must('WSJ', 'Unigram 962, bigram 170, trigram 109 (9.91, 7.41, 6.77 bits). Test perplexity is 2 to the cross entropy, which is at least the true entropy.')

T = K.topic(
    slug='perplexity', topic='perplexity', step=(4, 'Language models', 'nlp-lm', 'Predict the next word with n-gram models, measure them with perplexity, smooth away the zeros and run the SRILM assignment.', 'College and masters'),
    title='Perplexity and evaluating language models', short='Perplexity', badge='4.2', minutes=45,
    lead='Turn the surprise of a test text into one number, read SRILM\'s ppl and ppl1, and learn the rules that make two perplexities comparable.',
    desc='Pointwise, total and average entropy, the board derivation of perplexity, the branching factor, ppl against ppl1 and file level perplexity, extrinsic and intrinsic evaluation, underflow, the WSJ table, comparable vocabularies, never training on the test set, and perplexity as cross entropy.',
    summary='Perplexity from entropy, ppl and ppl1, file perplexity, underflow, the WSJ table and fair comparison.',
    keywords=['perplexity', 'ppl', 'ppl1', 'cross entropy', 'evaluation', 'underflow', 'test set', 'vocabulary'],
    recap='<p>Perplexity is 2 to the average surprise per token, the number of words the model is effectively choosing between. ppl counts the end tag and ppl1 does not. A fair comparison needs the same test text, the same vocabulary and no tuning on the test set.</p>')
