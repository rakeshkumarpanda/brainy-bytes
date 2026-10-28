# Chapter 3.1: Zipf's law. Source: lectures 4 to 6 (how to represent language computationally, Zipf's law, the
# 50th against 150th question, coverage by harmonic numbers, least effort, Mandelbrot and Heaps, the Zipf mystery,
# monkey typing and the bigram homework). Brown numbers are the lower cased counts quoted in the notes.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('rankfreq', r'''
# Count, sort, rank: the recipe Zipf's students followed by hand
text = """the cat sat on the mat and the dog sat on the log and the cat saw the dog
and the dog saw the cat and the bird saw them all from the top of the tree"""

counts = {}
for w in text.split():
    counts[w] = counts.get(w, 0) + 1

ranked = sorted(counts.items(), key=lambda kv: -kv[1])
for r, (w, f) in enumerate(ranked[:6], start=1):
    print(r, w, f, " f x r =", f * r)
print("types:", len(counts), " seen once:", sum(1 for f in counts.values() if f == 1))
''')

K.code('coverage', r'''
# If f = k / r exactly, what share of all tokens do the top n words cover?
import math
GAMMA = 0.5772156649                 # the Euler Mascheroni constant

def harmonic(n):                     # H_n is close to ln n + gamma for large n
    return math.log(n) + GAMMA

V = 50000
for n in [1, 10, 100, 1000]:
    exact_small = sum(1 / r for r in range(1, n + 1)) if n <= 10 else harmonic(n)
    print("top", n, "words cover", round(100 * exact_small / harmonic(V), 1), "percent")
''')

K.code('alpha', r'''
# The Zipf exponent of random typing: alpha = 1 - ln(1 - s) / ln M
import math

def alpha(M, s):
    return 1 - math.log(1 - s) / math.log(M)

for M, s in [(26, 1 / 27), (26, 0.2), (4, 0.2), (2, 1 / 3)]:
    print("M =", M, " s =", round(s, 3), " alpha =", round(alpha(M, s), 4))
''')

K.lesson('frequency', 'Do words have an average frequency?', f'''
<p>The lecture opened with two ways to describe a language. A grammar says what is allowed: English puts the verb before the object, Hindi after it. Statistics say what is likely: after "apples and" you expect "oranges" more than "bananas". This step is about the second view, and it starts with a plain question. In a page of text, do most words occur about an average number of times?</p>
<p>Many things in life follow the bell shaped normal curve: heights of children in a class, marks of 100 students, the sum of three dice. Most values sit near the middle and extremes are rare. For three dice there are 6 × 6 × 6 = 216 outcomes. Only one gives a sum of 3, while 27 give a sum of 10, so the middle wins.</p>
{fxs(
    fx('Three dice', 'P(sum = 3) = ' + frac('1', '216') + ' ≈ 0.005, &nbsp; P(sum = 10) = ' + frac('27', '216') + ' = 0.125', 'Counts for sums 3 to 18: 1, 3, 6, 10, 15, 21, 25, 27, 27, 25, 21, 15, 10, 6, 3, 1.'),
    fx('Words', 'c(the) = 69,971, &nbsp; types seen once = 16,540', 'Brown corpus, lower cased. One word fills about 7% of the text while thousands of words appear once. There is no typical value.'))}
<p>Word counts look nothing like a bell. A few words are used constantly and a huge number are rare. The notebook already showed this: "the" alone was 5.40% of the 1,161,192 Brown tokens counted case sensitively (69,971 once The and the are merged).</p>
{table(['Function words', 'Content words'], [
    ['the, of, and, to, a, in, that', 'nouns, verbs, adjectives, adverbs'],
    ['Short and extremely frequent', 'Longer and rarer'],
    ['A closed class: new ones almost never appear', 'An open class: new words appear all the time'],
    ['Glue that joins the content words', 'Carry the meaning and the topic'],
    ['Little information each, since they are predictable', 'Much information each, since they are surprising']])}
{code('rankfreq')}
{note('Why no bell curve? A normal curve appears when a value is the sum of many small independent effects. Word frequency is not a sum. It comes from people choosing words, and a few grammatical words are chosen in almost every sentence.', 'tip')}
''', kw=['corpus', 'normal distribution', 'heavy tail', 'function words', 'content words', 'word frequency', 'dice'])

K.lesson('law', "Zipf's law", f'''
<p>In 1912 the French stenographer Jean-Baptiste Estoup noticed a regularity in word counts. In 1932 the Harvard linguist George Kingsley Zipf made it famous, with students counting the words of books by hand. The method is the one used for ranking students by marks: count every word, sort from most to least frequent, give the top word rank 1, the next rank 2, and plot frequency against rank.</p>
{fxs(
    fx("Zipf's law", '<i>f</i> = ' + frac('<i>k</i>', '<i>r</i>') + ' &nbsp; or &nbsp; <i>f</i> × <i>r</i> ≈ <i>k</i>', 'f is the frequency of the word of rank r and k is a constant for the corpus. The frequency falls as one over the rank.', key=True),
    fx('Ratio rule', frac('<i>f</i><sub><i>a</i></sub>', '<i>f</i><sub><i>b</i></sub>') + ' = ' + frac('<i>b</i>', '<i>a</i>'), 'The top word is about twice the second, three times the third. The 50th word is three times the 150th.', key=True))}
{viz('zipf')}
<h3>Checking it on Brown</h3>
{table(['Rank r', 'Word', 'Frequency f', 'f × r'], [
    ['1', 'the', '69,971', '69,971'], ['2', 'of', '36,412', '72,824'], ['3', 'and', '28,853', '86,559'], ['10', 'he', '9,548', '95,480'],
    ['50', 'no', '2,139', '106,950'], ['150', 'three', '610', '91,500'], ['1,000', 'eight', '104', '104,000'], ['10,000', 'incredibly', '7', '70,000']])}
<p>The product f × r is not exactly constant, but it stays between about 70,000 and 107,000 while the rank grows ten thousand times. The top word is 1.92 times the second, close to the predicted 2.</p>
<h3>Why a straight line on log axes</h3>
{steps('Proof: a power law is a straight line on a log log plot', [
    'Start from the general power law f = k · r<sup>−a</sup>. Zipf is the case a = 1.',
    'Take logarithms of both sides: log f = log k + log r<sup>−a</sup>.',
    'The power comes down: log f = log k − a · log r.',
    'Write Y = log f and X = log r. Then Y = log k − a X, a straight line with slope −a.',
    eq('Zipf predicts slope −1. Brown gives about −1.08 for ranks 10 to 10,000.')])}
{note('The class question "should the 50th word occur three times as often as the 150th?" has answer yes: f₅₀ ÷ f₁₅₀ = 150 ÷ 50 = 3. On Brown the real ratio is 2,139 ÷ 610 = 3.51, a little steeper, as the slope of −1.08 suggests.', 'exam')}
''', kw=["Zipf's law", 'rank', 'frequency', 'power law', 'log log plot', 'Estoup', 'slope minus one', 'f times r'])

K.lesson('coverage', 'How much text do the top words cover?', f'''
<p>If Zipf's law held exactly, we could work out how much of all text the most common words make up. The answer uses the harmonic numbers.</p>
{fxs(
    fx('Share of the top n words', 'share(<i>n</i>) = ' + frac('<i>H</i><sub><i>n</i></sub>', '<i>H</i><sub><i>V</i></sub>') + ', &nbsp; <i>H</i><sub><i>n</i></sub> = 1 + ' + frac('1', '2') + ' + ' + frac('1', '3') + ' + … + ' + frac('1', '<i>n</i>'), 'V is the vocabulary size. Total tokens are k H<sub>V</sub> and the top n words have k H<sub>n</sub> of them.', key=True),
    fx('Approximation', '<i>H</i><sub><i>n</i></sub> ≈ ln <i>n</i> + γ, &nbsp; γ ≈ 0.5772', 'γ is the Euler Mascheroni constant. The sum of 1/r grows like the area under 1/x.'))}
{steps('Coverage for a 50,000 word vocabulary', [
    eq('H<sub>50000</sub> ≈ ln 50,000 + 0.5772 = 10.820 + 0.577 = 11.397'),
    'Top 1 word: 1 ÷ 11.397 = 8.8% (Brown\'s "the" is 7.1%).',
    'Top 10: H<sub>10</sub> = 2.929, so 2.929 ÷ 11.397 = 25.7% (Brown: 24.8%).',
    'Top 100: H<sub>100</sub> = 5.187, so 45.5% (Brown: 48.5%).',
    'Top 1,000: H<sub>1000</sub> = 7.485, so 65.7% (Brown: 70.1%).',
    'About 100 words make up half of everything we write.'])}
{code('coverage')}
<h3>Why language is shaped like this</h3>
<p>The professor's answer is the <b>principle of least effort</b>. Words we use often should be quick to say, so frequent words are short. But short words are easy to mishear and carry little information, while long words are robust and informative. Language balances the speaker's effort against the listener's need to recover the message despite noise. In Brown the ten most frequent words average 2.4 letters, while words ranked beyond 10,000 average 8.1. This is Zipf's law of abbreviation.</p>
{deep('Mandelbrot and Heaps', '<p>Benoit Mandelbrot (1953) proposed f = k ÷ (r + b)<sup>a</sup>. The shift b flattens the top few ranks and a near 1 controls the tail. With k = 100,000, a = 1 and b = 2.7, rank 1 gets about 27,000 instead of 100,000. Heaps\' law is the companion law for vocabulary growth: V ≈ K N<sup>β</sup> with β between about 0.4 and 0.6. The vocabulary never stops growing, which is why every language model meets unseen words and needs smoothing.</p>')}
{scene('sizing the vocabulary of a phone keyboard', '<p>A keyboard app for Indian English must fit its word list on the phone. Zipf\'s law says a few thousand words cover most of what people type (on Brown the top 2,000 cover 77.5% and the top 3,000 cover 81.9%). The long tail of names and rare words is handled with subword pieces instead of storing every word ever seen.</p>')}
''', kw=['coverage', 'harmonic number', 'Euler Mascheroni', 'least effort', 'law of abbreviation', 'Mandelbrot', "Heaps' law", 'vocabulary growth'])

K.lesson('monkey', 'The Zipf mystery: monkey typing', f'''
<p>The professor set an experiment after a documentary on the "Zipf mystery". Give a monkey a keyboard with 26 letters and a space bar, each pressed with probability 1/27. A word is whatever falls between two spaces. Type a million characters, count the words, rank them and plot. Will this meaningless text follow Zipf's law?</p>
<p>Students who ran it found that it broadly does. George Miller pointed this out in 1957 and Wentian Li made it precise in 1992. The reason is counting, not meaning.</p>
{viz('monkey')}
{steps('Proof: random typing gives a power law', [
    'Each letter has probability (1 − s) ÷ M and the space has probability s. A word of length L is L letters then a space, so P(word) = ((1 − s)/M)<sup>L</sup> · s.',
    'Every word of length L has the same probability, and each extra letter divides it by M/(1 − s).',
    'There are M<sup>L</sup> words of length L. They sit at ranks of about c · M<sup>L</sup>, so L ≈ ln(r/c) ÷ ln M.',
    'Put this L into P(word): f ∝ ((1 − s)/M)<sup>ln r / ln M</sup> = r<sup>ln((1 − s)/M) / ln M</sup>.',
    eq('f ∝ r<sup>−α</sup>, &nbsp; α = 1 − ln(1 − s) ÷ ln M'),
    'For 27 equally likely keys: α = ln 27 ÷ ln 26 = 1.0116, practically Zipf\'s exponent of 1.'])}
{fxs(fx('Random typing exponent', 'α = 1 − ' + frac('ln(1 − <i>s</i>)', 'ln <i>M</i>'), 'M letters, space probability s. As M grows α tends to 1 for any fixed s.', key=True))}
{code('alpha')}
<h3>What the experiment shows, and what it does not</h3>
<ul>
<li>A Zipf like curve can come from pure chance plus the convention that spaces mark word boundaries. Zipf's law alone does not prove language is special.</li>
<li>The monkey's curve is a staircase, because all words of the same length tie. Real text gives a smooth curve.</li>
<li>Most importantly, the monkey's next letter cannot be predicted from the previous ones. Human language is highly predictable from context, which is what entropy measures in the next chapter.</li>
</ul>
<h3>The bigram homework</h3>
<p>A student asked whether pairs of words also follow Zipf. On Brown the top bigrams are "of the" (9,771), "in the" (6,155), "to the" (3,525), "on the" (2,491) and "and the" (2,297), all function word pairs. Their rank frequency curve is also close to a straight line on log axes, but flatter, with slope about −0.76, because counts are spread over many more possible pairs.</p>
{ladder(
    '<p>Count every word in a book and sort them. The top word appears about twice as often as the second and three times as often as the third. A few words fill most of the pages.</p>',
    '<p>Zipf\'s law f = k/r is a power law, a straight line of slope −1 on log log axes. The top n words cover H<sub>n</sub>/H<sub>V</sub> of the text. Least effort explains why frequent words are short.</p>',
    '<p>Zipf Mandelbrot f = k/(r + b)<sup>a</sup> fits the head better. Random typing gives α = 1 − ln(1 − s)/ln M, so the exponent alone cannot separate language from noise. Heaps\' law V ≈ KN<sup>β</sup> drives the need for smoothing and subword vocabularies.</p>',
    '<p>Research asks which mechanism produces Zipf in real language: least effort optimisation (Ferrer i Cancho and Solé, 2003), preferential attachment, or sampling artefacts. Piantadosi (2014) reviews the evidence across languages, where exponents vary between about 0.8 and 1.2, and argues that the law constrains but does not explain the lexicon.</p>')}
''', kw=['Zipf mystery', 'monkey typing', 'random text', 'Miller', 'Li', 'exponent', 'staircase', 'bigram Zipf'])

# ---------------------------------------------------------------- quiz
K.quiz('e', "Zipf's law says frequency is", ['Proportional to rank', 'Proportional to one over rank', 'The same for every word', 'Normally distributed'], 1,
       'Rank 2 has half the count of rank 1.', 'f = k/r, so f × r stays roughly constant.')
K.quiz('e', 'The most frequent word gets which rank?', ['0', '1', 'The largest number', 'It depends on the length'], 1,
       'Like the top student in a class.', 'Rank 1 is the top. Higher rank numbers mean lower frequency.')
K.quiz('e', 'Should the 50th most common word occur three times as often as the 150th?', ['No, the same', 'Yes, three times', 'No, one third as often', 'Nine times'], 1,
       'Use f_a / f_b = b / a.', '150 / 50 = 3. On Brown the real ratio is 3.51.')
K.quiz('e', 'Which group of words is short, frequent and a closed class?', ['Content words', 'Function words', 'Proper nouns', 'Rare words'], 1,
       'the, of, and, to.', 'Function words glue sentences together and new ones almost never appear.')
K.quiz('m', "On a log log plot, Zipf's law looks like", ['A bell curve', 'A straight line with slope −1', 'A horizontal line', 'A parabola'], 1,
       'log f = log k − log r.', 'Taking logs turns the power law into a straight line with slope −a, and a = 1.')
K.quiz('m', 'Which principle did the lecture use to explain why frequent words are short?', ['Central limit theorem', 'Principle of least effort', 'Occam\'s razor', 'Markov property'], 1,
       'Speakers want to save energy.', 'Frequent words should cost little effort, balanced against the listener\'s need to understand.')
K.quiz('m', 'Random monkey typing produces', ['No pattern at all', 'A Zipf like power law with a staircase shape', 'A perfect bell curve', 'Exactly the curve of English'], 1,
       'Words of the same length tie.', 'Counting alone gives a power law, but all words of one length share a probability, so the curve has steps.')
K.quiz('m', 'Compared with single words, the Brown bigram rank frequency line is', ['Steeper', 'Flatter (slope about −0.76)', 'Not a line', 'Identical'], 1,
       'There are many more possible pairs.', 'Counts spread over more types, so the slope is gentler.')
K.quiz('h', 'Under exact Zipf with V = 50,000, about what share of tokens do the top 100 words cover?', ['5%', '25%', '45%', '90%'], 2,
       'H₁₀₀ ÷ H₅₀₀₀₀.', '5.187 ÷ 11.397 ≈ 45.5%. Brown gives 48.5%.')
K.quiz('h', "What does the Mandelbrot shift b in f = k/(r + b)^a change?", ['The tail slope', 'The flat top of the curve at the first few ranks', 'The corpus size', 'Nothing'], 1,
       'Look at rank 1.', 'Adding b to small ranks changes them a lot and large ranks hardly at all, so the head flattens.')
K.quiz('x', 'Why can Zipf\'s law alone not prove that a text is human language?', ['It never holds for language', 'Random typing also gives a power law with exponent near 1', 'It needs a grammar', 'It only works for English'], 1,
       'Think of the monkey.', 'Combinatorics alone produces α = 1 − ln(1 − s)/ln M near 1. Predictability is what separates language from noise.')
K.quiz('x', "Heaps' law V ≈ K N^β with β ≈ 0.5 implies that", ['The vocabulary stops growing', 'Quadrupling the text roughly doubles the vocabulary, so new words never stop appearing', 'Every word is seen twice', 'The type token ratio rises'], 1,
       '4^0.5 = 2.', 'V keeps growing, so any model must handle unseen words.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Under exact Zipf the top word occurs 60,000 times. How often does the word of rank 3 occur?', '20000', 'f = k / r with k = 60,000.',
       ['Zipf: f = k ÷ r.', 'At rank 1, f₁ = k ÷ 1, so k = 60,000.', eq('f₃ = 60,000 ÷ 3 = 20,000')], check=20000)
K.calc('e', 'With k = 60,000, which rank has frequency 1,000?', '60', 'Solve k / r = 1,000.',
       ['Zipf: f = k ÷ r with k = 60,000.', 'Set 60,000 ÷ r = 1,000.', eq('r = 60,000 ÷ 1,000 = 60')], check=60)
K.calc('e', 'Three dice are rolled. How many of the 216 outcomes give a sum of 3?', '1', 'Only one triple works.',
       ['Each die shows at least 1, so the smallest sum is 3.', 'The only way to reach it is 1 + 1 + 1.', eq('1 outcome, so P = 1/216 ≈ 0.005')], check=1)
K.calc('m', 'Brown: "the" 69,971 and "of" 36,412. What is the ratio, to two decimals?', '1.92', 'Divide.',
       ['Zipf predicts f₁/f₂ = 2.', eq('69,971 ÷ 36,412 ≈ 1.92'), 'Close to the predicted 2.'], check=69971 / 36412, tol=0.005)
K.calc('m', 'Brown: rank 50 "no" has 2,139 and rank 150 "three" has 610. What is the ratio, to two decimals?', '3.51', 'Divide the counts.',
       ['Zipf predicts 150 ÷ 50 = 3.', eq('2,139 ÷ 610 ≈ 3.51'), 'A little above 3 because the real slope is about −1.08.'], check=2139 / 610, tol=0.005)
K.calc('m', 'What is the harmonic number H₁₀ to three decimals?', '2.929', 'Add 1/1 to 1/10.',
       ['1 + 0.5 + 0.333 + 0.25 + 0.2 = 2.283.', '1/6 + 1/7 + 1/8 + 1/9 + 1/10 = 0.646.', eq('H₁₀ = 2.283 + 0.646 ≈ 2.929')], check=sum(1 / r for r in range(1, 11)), tol=0.0005)
K.calc('m', 'Under exact Zipf with V = 50,000, what percentage of tokens do the top 10 words cover? One decimal.', '25.7', 'H₁₀ ÷ H₅₀₀₀₀.',
       ['H₁₀ = 2.929.', 'H₅₀₀₀₀ ≈ ln 50,000 + 0.5772 = 11.397.', eq('2.929 ÷ 11.397 ≈ 25.7%')], check=100 * 2.9289682539682538 / 11.397, tol=0.05)
K.calc('h', 'A power law has f = 100,000 at rank 1 and f = 1,000 at rank 100. What is the slope on log log axes?', '-1', 'Rise over run in log units.',
       ['Δ log f = log 1,000 − log 100,000 = 3 − 5 = −2.', 'Δ log r = log 100 − log 1 = 2 − 0 = 2.', eq('slope = −2 ÷ 2 = −1')], check=-1)
K.calc('h', 'Random typing with M = 4 letters and space probability s = 0.2. What is the Zipf exponent α? Four decimals.', '1.1610', 'α = 1 − ln(1 − s)/ln M.',
       ['ln(1 − 0.2) = ln 0.8 = −0.2231.', 'ln 4 = 1.3863.', eq('α = 1 + 0.2231 ÷ 1.3863 ≈ 1.1610')], check=1.160964047443681, tol=0.00005)
K.calc('h', 'With Mandelbrot k = 100,000, a = 1 and b = 2.7, what is the frequency of rank 1, to the nearest whole number?', '27027', 'f = k / (r + b)^a.',
       ['r + b = 1 + 2.7 = 3.7.', eq('f = 100,000 ÷ 3.7 ≈ 27,027'), 'Plain Zipf would give 100,000, so the head is flattened.'], check=100000 / 3.7, tol=0.5)
K.calc('x', "Heaps' law with K = 30 and β = 0.5. A corpus grows from 1 million to 4 million tokens. How many new types appear?", '30000', 'Compute V for both sizes.',
       ['V(10⁶) = 30 × 1,000 = 30,000.', 'V(4 × 10⁶) = 30 × 2,000 = 60,000.', eq('60,000 − 30,000 = 30,000 new types')], check=30000)

# ---------------------------------------------------------------- assignments
K.assign('zipfpred', 'e', 'Predict with Zipf',
         '<p>Write <code>predict(k, ranks)</code> that returns the list of Zipf frequencies k / r for each rank, rounded to the nearest whole number.</p>',
         '''
def predict(k, ranks):
    # your code here
    pass
''', [('predict(60000, [1, 2, 3, 10])', [60000, 30000, 20000, 6000]), ('predict(69971, [50, 150])', [1399, 466]), ('predict(10, [])', [])],
         '''
def predict(k, ranks):
    return [round(k / r) for r in ranks]
''', 'One division per rank.', '<p>Compare 1,399 and 466 with the real Brown counts 2,139 and 610: the real tail is a little heavier at these ranks.</p>')
K.assign('rankfr', 'm', 'Rank and f × r',
         '<p>Write <code>rank_table(text, n)</code>. Lower case the text, split on spaces, count words and return the top n as <code>[rank, word, count, count × rank]</code>, most frequent first, ties in order of first appearance.</p>',
         '''
def rank_table(text, n):
    # your code here
    pass
''', [("rank_table('the cat the dog the cat', 2)", [[1, 'the', 3, 3], [2, 'cat', 2, 4]]), ("rank_table('A a b', 5)", [[1, 'a', 2, 2], [2, 'b', 1, 2]]), ("rank_table('', 3)", [])],
         '''
def rank_table(text, n):
    counts = {}
    for w in text.lower().split():
        counts[w] = counts.get(w, 0) + 1
    order = sorted(counts.items(), key=lambda kv: -kv[1])[:n]
    return [[i + 1, w, c, c * (i + 1)] for i, (w, c) in enumerate(order)]
''', 'sorted is stable, so ties keep first appearance order.', '<p>This is the table Zipf\'s students built by hand, and the one in the Brown check.</p>')
K.assign('share', 'h', 'Coverage of the top words',
         '<p>Write <code>share(n, V)</code> that returns the percentage of tokens covered by the top n words under exact Zipf with vocabulary V, using exact harmonic sums, rounded to 1 decimal.</p>',
         '''
def share(n, V):
    # your code here
    pass
''', [('share(1, 50000)', 8.8), ('share(10, 50000)', 25.7), ('share(100, 50000)', 45.5), ('share(4, 4)', 100.0)],
         '''
def share(n, V):
    Hn = sum(1 / r for r in range(1, n + 1))
    HV = sum(1 / r for r in range(1, V + 1))
    return round(100 * Hn / HV, 1)
''', 'Both sums are 1 + 1/2 + ... up to n and up to V.', '<p>The exact sum H₅₀₀₀₀ = 11.397 agrees with ln 50,000 + γ to five decimals.</p>')
K.assign('monkeyalpha', 'm', 'The monkey exponent',
         '<p>Write <code>alpha(M, s)</code> that returns 1 − ln(1 − s) ÷ ln M rounded to 4 decimals.</p>',
         '''
import math

def alpha(M, s):
    # your code here
    pass
''', [('alpha(26, 1/27)', 1.0116), ('alpha(4, 0.2)', 1.161), ('alpha(2, 1/3)', 1.585)],
         '''
import math

def alpha(M, s):
    return round(1 - math.log(1 - s) / math.log(M), 4)
''', 'math.log is the natural logarithm.', '<p>As M grows, ln(1 − s)/ln M shrinks and α approaches 1 whatever s is.</p>')

K.must("Zipf's law", 'f = k/r, f × r ≈ constant, slope −1 on log log axes. f_a/f_b = b/a, so the 50th word is 3 times the 150th.')
K.must('Brown check', 'the 69,971, of 36,412 (ratio 1.92). f × r stays between about 70,000 and 107,000. Real slope about −1.08.')
K.must('Coverage', 'Top n share = H_n/H_V, H_n ≈ ln n + 0.5772. V = 50,000: top 10 = 25.7%, top 100 = 45.5%.')
K.must('Least effort', 'Frequent words are short (law of abbreviation). Language balances speaker effort and listener robustness.')
K.must('Monkey typing', 'Random keys give a power law with α = 1 − ln(1 − s)/ln M (1.0116 for 27 keys) but no predictability.')

T = K.topic(
    slug='zipfs-law', topic='zipf', step=(3, 'Information and surprise', 'nlp-info', 'Measure how predictable language is with Zipf\'s law, entropy, mutual information and the noisy channel.', 'College and masters'),
    title="Zipf's law and the shape of vocabulary", short="Zipf's law", badge='3.1', minutes=40,
    lead='See why a handful of words fill most of every page, test Zipf\'s law on real Brown counts, work out how much text the top words cover, and find out why a typing monkey obeys the same law.',
    desc="Word frequencies against the normal curve, Zipf's law and the f × r check on Brown, the log log proof, the ratio rule, coverage with harmonic numbers, least effort and the law of abbreviation, Mandelbrot and Heaps, and the monkey typing proof.",
    summary="Zipf's law f = k/r, the Brown check, coverage by harmonic numbers, least effort, Mandelbrot and Heaps, and why random typing is also Zipfian.",
    keywords=["Zipf's law", 'rank frequency', 'power law', 'harmonic number', 'least effort', 'monkey typing', "Heaps' law", 'Mandelbrot'],
    recap='<p>Word frequencies are not bell shaped. They fall like one over rank, so about a hundred words make up half of all text and most words are rare. That long tail is why models need smoothing and subword pieces.</p>')
