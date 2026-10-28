# Chapter 4.1: n-gram models. Source: lectures 7 and 8 (true against estimated probability, the chain rule, the
# Markov assumption, the unigram, bigram and trigram windows of "He put the coffee on the table", counting and the MLE
# with its proof, the Markov chain of slide 61, the in-class activity on the five sentence corpus, the <s> and </s>
# debate, questions 1 and 2 with the corrections to the answer sheet, and problems A1 to C10 of the problem bank).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('counts', r'''
# Count unigrams and bigrams of the activity corpus, with the start and end tags
from collections import Counter
corpus = ["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"]

uni, bi = Counter(), Counter()
for line in corpus:
    t = ["<s>"] + line.split() + ["</s>"]
    uni.update(t[1:])                    # <s> is never predicted, so it is not counted in N
    bi.update(zip(t, t[1:]))

N = sum(uni.values())
print("N =", N, " types =", len(uni))
print("C(I) =", uni["I"], " C(I am) =", bi[("I", "am")], " C(am I) =", bi[("am", "I")])
print("P(am | I) =", bi[("I", "am")], "/", uni["I"], "=", bi[("I", "am")] / uni["I"])
''')

K.code('bigram', r'''
# Question 1: the bigram probability of two sentences
from collections import Counter
from math import log10
corpus = ["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"]
hist, bi = Counter(), Counter()
for line in corpus:
    t = ["<s>"] + line.split() + ["</s>"]
    for h, w in zip(t, t[1:]):
        hist[h] += 1
        bi[(h, w)] += 1

def p_sentence(s):
    t = ["<s>"] + s.split() + ["</s>"]
    p = 1.0
    for h, w in zip(t, t[1:]):
        p *= bi[(h, w)] / hist[h]
    return p

for s in ["Sam I do I like", "Sam I am"]:
    p = p_sentence(s)
    print(s, " P =", round(p, 6), " log10 P =", round(log10(p), 5))
''')

K.code('unigram', r'''
# Question 2: the same sentences under the unigram model, N = 22
from collections import Counter
from math import log10
corpus = ["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"]
uni = Counter(w for line in corpus for w in line.split() + ["</s>"])
N = sum(uni.values())

for s in ["Sam I do I like", "Sam I am", "am I Sam"]:
    p = 1.0
    for w in s.split() + ["</s>"]:
        p *= uni[w] / N
    print(s, " P =", f"{p:.4e}", " log10 P =", round(log10(p), 5))
''')

K.code('chain', r'''
# The Markov chain of slide 61: score a string and find the best three word strings
names = ["He", "cool", "is"]
pi = [0.7, 0.1, 0.2]
A = [[0.1, 0.3, 0.6],     # from He
     [0.2, 0.0, 0.8],     # from cool
     [0.5, 0.5, 0.0]]     # from is

def prob(words):
    i = [names.index(w) for w in words]
    p = pi[i[0]]
    for a, b in zip(i, i[1:]):
        p *= A[a][b]
    return p

print("P(is He cool) =", round(prob(["is", "He", "cool"]), 4))
best = sorted(((prob([a, b, c]), a, b, c) for a in names for b in names for c in names), reverse=True)
print("top three:", [(round(p, 3), a, b, c) for p, a, b, c in best[:3]])
''')

K.lesson('predict', 'Why predict the next word?', f'''
<p>Say "He put the coffee" to a room of people and pause. Almost everyone finishes with "on the table" or "on the desk". Nobody says "on the elephant". People carry a sense of which words are likely next, and that sense is shared. A language model is a program with the same skill: it gives every possible next word a probability.</p>
<p>The lecture gave several uses. In speech recognition, "I will be back soonish" and "I will be bassoon dish" sound almost the same, and the language model picks the likely word string. Spelling correction, machine translation, phone keyboard suggestions and every large language model work the same way. The professor's advice was to master the simple n-gram first: RNNs, LSTMs and Transformers all predict the next token from a history, so they are easy to follow once n-grams are clear.</p>
<h3>True probability and estimated probability</h3>
<p>How likely is "jelly" after "peanut butter and"? We cannot open a speaker's mind and read the true probability P. Instead we take a corpus of millions of words, assume it is a fair sample of the language, and estimate. The estimate is written m, and the slide's definition is short: a language model is a probability distribution over sentences.</p>
{fxs(
    fx('Conditional estimate', 'm(jelly | peanut butter and) = ' + frac('C(peanut butter and jelly)', 'C(peanut butter and)'), 'Count the whole four word sequence, then divide by how often the three word history occurred.', key=True),
    fx('Chain rule (exact)', 'P(<i>w</i>₁ … <i>w<sub>n</sub></i>) = P(<i>w</i>₁) · P(<i>w</i>₂ | <i>w</i>₁) · P(<i>w</i>₃ | <i>w</i>₁ <i>w</i>₂) ⋯ P(<i>w<sub>n</sub></i> | <i>w</i>₁ … <i>w</i><sub><i>n</i>−1</sub>)', 'No approximation yet. Every word is conditioned on everything before it.', key=True))}
{note('A student first answered "count jelly and divide by the total number of words". That is P(jelly), the unigram probability, which ignores the history. The question asks for the conditional probability, which needs the joint count of the whole sequence.', 'warn')}
<p>Why count "put the coffee" and not just "coffee" when estimating P(coffee | put the)? Because P(x | y) = P(x, y) ÷ P(y). C(coffee) counts coffee anywhere, after "a", after "black", at the start of a sentence. Dividing it by C(put the) mixes two unrelated events and can even give a number above 1.</p>
{steps('Counting a phrase in a big file', [
    'Numerator: how many times does "put the coffee" occur? Denominator: how many times does "put the" occur?',
    'grep -c counts matching lines, not matches. A line with the phrase twice counts once, so use grep -o "put the coffee" file | wc -l.',
    'Add word boundaries, or "output theory" will match "put the".',
    'The scalable way is one pass that counts every n-gram into a table. That is what SRILM\'s ngram-count does, and any probability is then a look up.'])}
{scene('a phone keyboard', '<p>You type "see you" and the keyboard offers "tomorrow", "soon" and "later". It has counted, across millions of messages, which words follow "see you" and offers the three with the largest counts. It does not understand meetings or time. It only knows what usually comes next.</p>')}
''', kw=['language model', 'next word prediction', 'true probability', 'estimate', 'chain rule', 'conditional probability', 'speech recognition', 'grep'])

K.lesson('markov', 'The Markov assumption', f'''
<p>The chain rule is exact but useless as it stands. To estimate P(table | He put the coffee on the) we would need that whole seven word history many times in the corpus, and long histories almost never repeat. The fix is to forget most of the past.</p>
{fxs(
    fx('Markov assumption', 'P(<i>w<sub>i</sub></i> | <i>w</i>₁ … <i>w</i><sub><i>i</i>−1</sub>) ≈ P(<i>w<sub>i</sub></i> | <i>w</i><sub><i>i</i>−<i>n</i>+1</sub> … <i>w</i><sub><i>i</i>−1</sub>)', 'The next word depends only on the last n − 1 words. An n-gram has n words: n − 1 of context and one predicted.', key=True),
    fx('Bigram model', 'P(<i>w</i>₁ … <i>w<sub>n</sub></i>) ≈ ∏<sub><i>i</i></sub> P(<i>w<sub>i</sub></i> | <i>w</i><sub><i>i</i>−1</sub>)', 'A bigram model is a first order Markov chain over words. A trigram model is second order.'))}
{table(['Model', 'n', 'Context words', 'Factor for "coffee" in "He put the coffee on the table"'], [
    ['Unigram', '1', '0', 'P(coffee)'],
    ['Bigram', '2', '1', 'P(coffee | the)'],
    ['Trigram', '3', '2', 'P(coffee | put the)'],
    ['4-gram', '4', '3', 'P(coffee | He put the)'],
    ['5-gram', '5', '4', 'P(on | He put the coffee)']])}
{note('In class the answer to "how many context words does a 5-gram have?" came out garbled. The rule is simple: n words in total, the last is predicted, so a 5-gram has 4 context words.', 'exam')}
<h3>The model as a machine</h3>
<p>A bigram model can be drawn as a graph. Each word is a state, each arrow carries P(next | current), and a start distribution π says where sentences begin. The slide used three states: He, cool and is.</p>
{viz('markov')}
{steps('Probability of "is He cool" from the chain', [
    'Start in "is": π(is) = 0.2.',
    'Follow is → He: P(He | is) = 0.5.',
    'Follow He → cool: P(cool | He) = 0.3.',
    eq('P(is He cool) = 0.2 × 0.5 × 0.3 = 0.03'),
    'Sanity check: the arrows leaving each state add to 1. He: 0.1 + 0.3 + 0.6, cool: 0.2 + 0 + 0.8, is: 0.5 + 0.5 + 0.'])}
{code('chain')}
{deep('Is a self loop allowed?', '<p>A student objected that the loop from He back to He is a mistake, as it would be in a compiler diagram. The professor was right to keep it. Self loops are legal in every kind of finite state machine, deterministic or not, weighted or not. Language repeats ("very very good"), so a word can follow itself. The chain has one real gap: it has no end state, so it only scores strings of a fixed length. Adding a state for &lt;/s&gt; turns it into a model of whole sentences.</p>')}
''', kw=['Markov assumption', 'n-gram', 'bigram', 'trigram', 'context window', 'Markov chain', 'finite state machine', 'self loop', 'start distribution'])

K.lesson('mle', 'Counting: the maximum likelihood estimate', f'''
<p>Every probability in an n-gram model is a ratio of two counts. The slide described the bigram case as "count of the bigram, normalised by the sum of all bigrams that share the same first word", and that sum is just the count of the first word.</p>
{fxs(
    fx('Bigram MLE', 'P(<i>w<sub>n</sub></i> | <i>w</i><sub><i>n</i>−1</sub>) = ' + frac('C(<i>w</i><sub><i>n</i>−1</sub> <i>w<sub>n</sub></i>)', 'C(<i>w</i><sub><i>n</i>−1</sub>)'), 'Because every occurrence of a word is followed by exactly one token, possibly &lt;/s&gt;, the bigram counts in a row add up to the count of the history.', key=True),
    fx('General n-gram MLE', 'P(<i>w<sub>n</sub></i> | <i>w</i><sub><i>n</i>−<i>N</i>+1</sub> … <i>w</i><sub><i>n</i>−1</sub>) = ' + frac('C(<i>w</i><sub><i>n</i>−<i>N</i>+1</sub> … <i>w</i><sub><i>n</i>−1</sub> <i>w<sub>n</sub></i>)', 'C(<i>w</i><sub><i>n</i>−<i>N</i>+1</sub> … <i>w</i><sub><i>n</i>−1</sub>)'), 'Pad each sentence with n − 1 start tags so the first word also has a full history.'),
    fx('Unigram MLE', 'P(<i>w</i>) = ' + frac('C(<i>w</i>)', '<i>N</i>'), 'N counts every token the model must predict: the words and one &lt;/s&gt; per sentence, never &lt;s&gt;.'))}
<h3>The activity corpus</h3>
<p>Five sentences, adapted from Jurafsky and Martin, with start and end tags: &lt;s&gt; I am Sam &lt;/s&gt;, &lt;s&gt; Sam I am &lt;/s&gt;, &lt;s&gt; Sam I like &lt;/s&gt;, &lt;s&gt; Sam I do like &lt;/s&gt;, &lt;s&gt; do I like Sam &lt;/s&gt;.</p>
{table(['Token', '&lt;s&gt;', 'I', 'Sam', 'am', 'do', 'like', '&lt;/s&gt;', 'Words', 'Words and &lt;/s&gt;'], [
    ['Count', '5', '5', '5', '2', '2', '3', '5', '17', '22']])}
{viz('bigramtable')}
{code('counts')}
<h3>Why 22, and not 17 or 27?</h3>
<p>This was the most asked question of the week. The rule used in class, and by SRILM: &lt;s&gt; is only context. It conditions the first word, as in P(Sam | &lt;s&gt;), but it is never predicted and never counted in N. &lt;/s&gt; is a real token that the model predicts, as in P(&lt;/s&gt; | like). So N = 17 words + 5 end tags = 22.</p>
<ul>
<li><b>With 17</b> the model can never end a sentence, so "Sam I" and "Sam I am" do not compete for the same probability and the total over all sentences exceeds 1.</li>
<li><b>With 27</b> the token &lt;s&gt; takes 5/27 of the mass but is never predicted, so the real tokens add to only 22/27.</li>
<li><b>With 22</b> the unigram values 5/22, 5/22, 5/22, 3/22, 2/22, 2/22 add to exactly 1.</li>
</ul>
<p>The professor's short reason: if you know the end tag, you know a start follows, so counting both adds a redundant event.</p>
{steps('Proof that the counting estimate is the best one (MLE)', [
    'Fix a history h seen C(h) times, followed by word w C(h w) times. Let θ<sub>w</sub> = P(w | h), with Σ θ<sub>w</sub> = 1.',
    'The part of the training log likelihood that depends on h is L(θ) = Σ<sub>w</sub> C(h w) log θ<sub>w</sub>.',
    'Add a Lagrange multiplier μ for the constraint and set the derivative to 0: C(h w) ÷ θ<sub>w</sub> − μ = 0, so θ<sub>w</sub> = C(h w) ÷ μ.',
    'The constraint gives Σ C(h w) ÷ μ = C(h) ÷ μ = 1, so μ = C(h).',
    eq('θ<sub>w</sub> = C(h w) ÷ C(h), the relative frequency'),
    'Check on the row of I: am 2, like 2, do 1, so 2/5 + 2/5 + 1/5 = 1.'])}
''', kw=['MLE', 'maximum likelihood', 'relative frequency', 'bigram counts', 'start tag', 'end tag', 'N = 22', 'Lagrange multiplier', 'activity corpus'])

K.lesson('activity', 'The activity: which sentence is better?', f'''
<p>The questions sheet asked: under a bigram model, which sentence gets the higher probability, S1 = Sam I do I like or S2 = Sam I am? Then the same with a unigram model. "Better" here means "higher probability under the model". That is a sensible stand in for human preference: "John went to London in the late afternoon" and "John went in the late afternoon to London" are both grammatical, yet almost everyone votes for the first. Grammar cannot decide, probability can.</p>
{viz('ngramlm', test='Sam I do I like\nSam I am')}
{steps('Question 1(a): bigram probability of S1', [
    'Pad: &lt;s&gt; Sam I do I like &lt;/s&gt;. That is 5 words and one &lt;/s&gt;, so 6 factors.',
    'P(Sam | &lt;s&gt;) = 3/5, P(I | Sam) = 3/5, P(do | I) = 1/5, P(I | do) = 1/2, P(like | I) = 2/5, P(&lt;/s&gt; | like) = 2/3.',
    eq('P(S1) = 3/5 × 3/5 × 1/5 × 1/2 × 2/5 × 2/3 = 6/625 = 0.0096'),
    'log₁₀ P = −0.22185 − 0.22185 − 0.69897 − 0.30103 − 0.39794 − 0.17609 = −2.01773.',
    'PP = 10<sup>2.01773/6</sup> = 2.16914. PP1 divides by 5 words only: 2.53248.'])}
{steps('Question 1(b): bigram probability of S2', [
    'Pad: &lt;s&gt; Sam I am &lt;/s&gt;, 4 factors.',
    'P(Sam | &lt;s&gt;) = 3/5, P(I | Sam) = 3/5, P(am | I) = 2/5, P(&lt;/s&gt; | am) = 1/2.',
    eq('P(S2) = 9/125 = 0.072, log₁₀ P = −1.14267, PP = 1.93049'),
    'S2 is about 7.5 times more probable than S1 and also wins per word, so the bigram model prefers Sam I am.'])}
{code('bigram')}
{steps('Question 2: the unigram model', [
    'Unigram factors are plain C(w) ÷ 22, no condition: P(Sam) = P(I) = P(&lt;/s&gt;) = 5/22, P(like) = 3/22, P(do) = 2/22.',
    'S1: 5/22 × 5/22 × 2/22 × 5/22 × 3/22 × 5/22 = 3.3075 × 10⁻⁵, log₁₀ −4.48050, PP 5.5815, PP1 7.8723.',
    'S2: 5/22 × 5/22 × 2/22 × 5/22 = 1.06721 × 10⁻³, log₁₀ −2.97175, PP 5.5327, PP1 9.7855.',
    'S2 is about 32 times more probable. Per word the two almost tie, because a unigram model ignores order and sees only frequencies.'])}
{code('unigram')}
{note('Three errors in the answer sheet are worth knowing. It labels unigram factors as P(Sam | &lt;s&gt;), but a unigram has no condition. Its product for S1 lists three numbers and gives 3.25 × 10⁻⁵, which comes from rounding 5/22 to 0.227. The exact value is 3.3075 × 10⁻⁵. And many students used N = 17 or 27, or conditioned the unigram on the previous word.', 'warn')}
{note('PP divides the total surprise by words plus &lt;/s&gt;, PP1 by words only, so PP1 is always the larger. The N in PP = P<sup>−1/N</sup> is the length of the sentence being scored, 6 for S1, not the 22 tokens of the training corpus. The professor saw that mistake in many submissions.', 'exam')}
{ladder(
    '<p>Count how often each word follows each other word in some text, and use those counts to guess the next word.</p>',
    '<p>Under the Markov assumption P(sentence) is a product of n-gram factors, each C(history word) ÷ C(history). The sentence tags make it a proper distribution over sentences of every length.</p>',
    '<p>The MLE maximises training likelihood (proof by Lagrange multipliers). An n-gram model is an order n − 1 Markov chain with V<sup>n−1</sup>(V − 1) free parameters, which is why data sparsity grows so fast with n.</p>',
    '<p>Neural language models keep the chain rule but drop the Markov cut off. Research compares how much of their gain comes from longer context against better generalisation across similar words, and studies n-gram statistics inside trained Transformers.</p>')}
''', kw=['activity', 'question 1', 'question 2', 'bigram probability', 'unigram probability', 'Sam I am', 'answer sheet errors', 'PP1', 'grammar against probability'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'How many context words does a trigram model use?', ['1', '2', '3', '0'], 1,
       'n words in total, the last one is predicted.', 'A trigram has 3 words: 2 of context and 1 predicted.')
K.quiz('e', 'In the class convention, which tag is counted in N?', ['Only &lt;s&gt;', 'Only &lt;/s&gt;', 'Both', 'Neither'], 1,
       'Which tag does the model ever predict?', '&lt;/s&gt; is predicted, &lt;s&gt; is only context, so N = 17 + 5 = 22.')
K.quiz('e', 'The unigram model gives "Sam I am" and "am I Sam" probabilities that are', ['Very different', 'Exactly equal', 'Both 0', 'Undefined'], 1,
       'The unigram ignores order.', 'The same words in a different order give the same product of C(w) ÷ N.')
K.quiz('e', 'P(am | I) in the activity corpus is', ['2/22', '2/5', '1/2', '5/22'], 1,
       'C(I am) ÷ C(I).', 'C(I am) = 2 and I occurs 5 times as a history.')
K.quiz('m', 'A bigram model is a Markov chain of order', ['0', '1', '2', 'n'], 1,
       'Each state is the previous word.', 'An n-gram model is a Markov chain of order n − 1.')
K.quiz('m', 'Why is C(coffee) ÷ C(put the) a wrong estimate of P(coffee | put the)?', ['It is too small', 'C(coffee) counts coffee in every context, not only after put the', 'It ignores &lt;/s&gt;', 'It is the MLE'], 1,
       'The numerator must be the joint event.', 'Only C(put the coffee) counts the cases where the history occurred and was followed by coffee.')
K.quiz('m', 'What is missing from a three state Markov chain with no end state?', ['Start probabilities', 'Self loops', 'A way to end sentences of different lengths', 'Transition probabilities'], 2,
       'It always emits strings of the length you ask for.', 'Without an end state it is a distribution over strings of fixed length, not over sentences.')
K.quiz('m', 'Which row sum must equal C(I) in a bigram table?', ['The column of I', 'The row of history I', 'The diagonal', 'All cells'], 1,
       'Every I is followed by one token.', 'Σ<sub>w</sub> C(I w) = C(I), which is why each row of probabilities adds to 1.')
K.quiz('h', 'A student used N = 27, counting both tags. What goes wrong?', ['Nothing', 'The predicted tokens add to only 22/27', 'Probabilities exceed 1', 'The bigram model breaks'], 1,
       '&lt;s&gt; takes mass but is never predicted.', 'P(&lt;s&gt;) = 5/27 is wasted, so the six real tokens share only 22/27.')
K.quiz('h', 'For a perplexity of the test sentence S1 = Sam I do I like, N is', ['22', '5 for PP, 6 for PP1', '6 for PP, 5 for PP1', '17'], 2,
       'Count the tokens of the sentence being scored.', '5 words and one &lt;/s&gt; give 6 for PP. PP1 uses the 5 words.')
K.quiz('h', 'Which proof shows that C(h w) ÷ C(h) is the MLE?', ['Bayes rule', 'Lagrange multipliers on Σ C(h w) log θ<sub>w</sub>', 'Jensen on entropy', 'The chain rule'], 1,
       'Maximise the log likelihood under Σ θ = 1.', 'The stationary point gives θ<sub>w</sub> = C(h w) ÷ μ with μ = C(h).')
K.quiz('x', 'With V = 10,000 word types, about how many free parameters does a trigram model have?', ['10⁴', '10⁸', '10¹²', '10¹⁶'], 2,
       'One distribution per pair of previous words.', 'V² histories each with V − 1 free values, about 10¹². No corpus can fill that.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'What is P(Sam | &lt;s&gt;) in the activity corpus?', '0.6', 'How many sentences start with Sam?',
       ['Three sentences start with Sam: Sam I am, Sam I like, Sam I do like.', 'C(&lt;s&gt;) = 5.', eq('P(Sam | &lt;s&gt;) = 3/5 = 0.6')], check=0.6, tol=1e-9)
K.calc('e', 'What is the unigram probability P(like), with N = 22?', '0.1364', 'like occurs 3 times.',
       ['C(like) = 3.', 'N = 17 words + 5 end tags = 22.', eq('P(like) = 3/22 ≈ 0.1364')], check=3 / 22, tol=0.0001)
K.calc('e', 'Markov chain: π(is) = 0.2, P(He | is) = 0.5, P(cool | He) = 0.3. What is P(is He cool)?', '0.03', 'Multiply along the path.',
       ['Start: π(is) = 0.2.', 'Two transitions: 0.5 and 0.3.', eq('0.2 × 0.5 × 0.3 = 0.03')], check=0.03, tol=1e-9)
K.calc('m', 'Bigram probability of &lt;s&gt; I am Sam &lt;/s&gt;? Exact decimal.', '0.016', 'Four factors.',
       ['P(I | &lt;s&gt;) = 1/5, P(am | I) = 2/5.', 'P(Sam | am) = 1/2, P(&lt;/s&gt; | Sam) = 2/5.', eq('1/5 × 2/5 × 1/2 × 2/5 = 2/125 = 0.016')], check=0.016, tol=1e-9)
K.calc('m', 'Bigram probability of S1 = Sam I do I like? Four decimals.', '0.0096', 'Six factors including &lt;/s&gt;.',
       ['3/5 × 3/5 = 9/25.', '× 1/5 × 1/2 = 9/250.', '× 2/5 × 2/3 = 36/3750 = 6/625.', eq('P(S1) = 0.0096')], check=6 / 625, tol=1e-6)
K.calc('m', 'log₁₀ of P(S2) = 0.072? Five decimals.', '−1.14267', 'log₁₀ 0.072.',
       ['0.072 = 9/125.', 'log₁₀ 9 = 0.95424, log₁₀ 125 = 2.09691.', eq('0.95424 − 2.09691 = −1.14267')], check=-1.1426675035687315, tol=0.00001)
K.calc('m', 'Unigram probability of "Sam I am" (with &lt;/s&gt;)? Give it in units of 10⁻³, three decimals.', '1.067', '5/22 × 5/22 × 2/22 × 5/22.',
       ['Numerator: 5 × 5 × 2 × 5 = 250.', 'Denominator: 22⁴ = 234,256.', eq('250 ÷ 234,256 = 1.067 × 10⁻³')], check=250 / 22**4 * 1000, tol=0.001)
K.calc('h', 'Trigram probability of &lt;s&gt; &lt;s&gt; Sam I am &lt;/s&gt; on the activity corpus? One decimal.', '0.1', 'P(Sam | &lt;s&gt; &lt;s&gt;) × P(I | &lt;s&gt; Sam) × P(am | Sam I) × P(&lt;/s&gt; | I am).',
       ['P(Sam | &lt;s&gt; &lt;s&gt;) = 3/5 and P(I | &lt;s&gt; Sam) = 3/3 = 1.', 'P(am | Sam I) = 1/3: Sam I is followed by am, like and do once each.', 'P(&lt;/s&gt; | I am) = 1/2: I am is followed once by Sam and once by &lt;/s&gt;.', eq('3/5 × 1 × 1/3 × 1/2 = 1/10 = 0.1')], check=0.1, tol=1e-9)
K.calc('h', 'Markov chain of slide 61: what is P(He cool is)? Three decimals.', '0.168', 'π(He) × P(cool | He) × P(is | cool).',
       ['π(He) = 0.7.', 'P(cool | He) = 0.3, P(is | cool) = 0.8.', eq('0.7 × 0.3 × 0.8 = 0.168')], check=0.168, tol=1e-9)
K.calc('h', 'Unigram entropy of the activity corpus (six tokens, counts 5, 5, 5, 3, 2, 2 out of 22) in bits? Four decimals.', '2.4783', 'Σ −p log₂ p.',
       ['Three tokens with p = 5/22: each −p log₂ p = 0.22727 × 2.1375 = 0.48580, total 1.45739.', 'like, p = 3/22: 0.13636 × 2.87447 = 0.39197.', 'am and do, p = 2/22: 2 × 0.09091 × 3.45943 = 0.62899.', eq('H = 1.45739 + 0.39197 + 0.62899 = 2.4783 bits')], check=2.4783, tol=0.0002)
K.calc('x', 'A unigram model with &lt;/s&gt; makes sentences by drawing tokens until it draws &lt;/s&gt; (P = 5/22). What is the expected number of words before &lt;/s&gt;? One decimal.', '3.4', 'A geometric distribution.',
       ['Each draw ends the sentence with probability q = 5/22.', 'The number of words before the first &lt;/s&gt; has mean (1 − q) ÷ q.', eq('(17/22) ÷ (5/22) = 17/5 = 3.4'), 'This equals the training average of 17 words in 5 sentences.'], check=3.4, tol=0.01)

# ---------------------------------------------------------------- assignments
TOYPY = '["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"]'
K.assign('bigramp', 'e', 'One bigram probability',
         '<p>Write <code>bigram_p(corpus, h, w)</code>. corpus is a list of sentences. Add &lt;s&gt; and &lt;/s&gt; to each, then return C(h w) ÷ C(h) as a float, or 0.0 if h never occurs as a history.</p>',
         '''
def bigram_p(corpus, h, w):
    # your code here
    pass
''', [(f'bigram_p({TOYPY}, "I", "am")', 0.4), (f'bigram_p({TOYPY}, "<s>", "Sam")', 0.6), (f'bigram_p({TOYPY}, "like", "</s>")', 2 / 3), (f'bigram_p({TOYPY}, "cat", "Sam")', 0.0)],
         '''
def bigram_p(corpus, h, w):
    pair, hist = 0, 0
    for line in corpus:
        t = ["<s>"] + line.split() + ["</s>"]
        for a, b in zip(t, t[1:]):
            if a == h:
                hist += 1
                if b == w:
                    pair += 1
    return pair / hist if hist else 0.0
''', 'Walk over adjacent pairs of the padded sentence and count two things at once.', '<p>The last test is an unseen history: 0 ÷ 0 is undefined, and returning 0.0 is the safe choice here.</p>')
K.assign('sentp', 'm', 'Sentence probability under a bigram model',
         '<p>Write <code>sentence_p(corpus, s)</code> that returns the MLE bigram probability of sentence s, with the tags, rounded to 6 decimals.</p>',
         '''
def sentence_p(corpus, s):
    # your code here
    pass
''', [(f'sentence_p({TOYPY}, "Sam I do I like")', 0.0096), (f'sentence_p({TOYPY}, "Sam I am")', 0.072), (f'sentence_p({TOYPY}, "I am do")', 0.0)],
         '''
from collections import Counter

def sentence_p(corpus, s):
    hist, bi = Counter(), Counter()
    for line in corpus:
        t = ["<s>"] + line.split() + ["</s>"]
        for a, b in zip(t, t[1:]):
            hist[a] += 1
            bi[(a, b)] += 1
    t = ["<s>"] + s.split() + ["</s>"]
    p = 1.0
    for a, b in zip(t, t[1:]):
        p *= bi[(a, b)] / hist[a] if hist[a] else 0.0
    return round(p, 6)
''', 'Count once, then multiply the factors of the padded test sentence.', '<p>"I am do" contains the unseen bigrams "am do" and "do &lt;/s&gt;", so one zero factor makes the whole product 0. Chapter 4.3 fixes this.</p>')
K.assign('unigramp', 'm', 'Unigram probability with the right N',
         '<p>Write <code>unigram_p(corpus, s)</code>: the MLE unigram probability of s with one &lt;/s&gt;, where N counts every word and one &lt;/s&gt; per training sentence but no &lt;s&gt;. Round to 8 decimals.</p>',
         '''
def unigram_p(corpus, s):
    # your code here
    pass
''', [(f'unigram_p({TOYPY}, "Sam I am")', 0.00106721), (f'unigram_p({TOYPY}, "am I Sam")', 0.00106721), (f'unigram_p({TOYPY}, "Sam I do I like")', 3.307e-05)],
         '''
from collections import Counter

def unigram_p(corpus, s):
    c = Counter(w for line in corpus for w in line.split() + ["</s>"])
    N = sum(c.values())
    p = 1.0
    for w in s.split() + ["</s>"]:
        p *= c[w] / N
    return round(p, 8)
''', 'N should come out as 22.', '<p>The first two tests have the same answer: the unigram model cannot see word order.</p>')

K.must('Markov assumption', 'An n-gram looks at n − 1 previous words. Bigram = first order Markov chain. Chain rule is exact, the n-gram is an approximation.')
K.must('MLE', 'P(w | h) = C(h w) ÷ C(h). Unigram P(w) = C(w) ÷ N. Proof: Lagrange multiplier gives the relative frequency.')
K.must('The tags', '&lt;s&gt; is context only, &lt;/s&gt; is predicted. Activity corpus: N = 17 + 5 = 22, six predicted types.')
K.must('Activity answers', 'Bigram S1 = 6/625 = 0.0096 (log −2.01773, PP 2.169), S2 = 0.072. Unigram S1 = 3.3075e-5, S2 = 1.0672e-3.')
K.must('Perplexity N', 'Use the tokens of the sentence being scored: words + &lt;/s&gt; for PP, words for PP1. Never the training N.')

T = K.topic(
    slug='ngram-models', topic='ngrams', step=(4, 'Language models', 'nlp-lm', 'Predict the next word with n-gram models, measure them with perplexity, smooth away the zeros and run the SRILM assignment.', 'College and masters'),
    title='N-gram models and the Markov assumption', short='N-gram models', badge='4.1', minutes=50,
    lead='Turn word counts into a model that predicts the next word, draw it as a Markov chain, and solve the in-class activity by hand.',
    desc='True against estimated probability, the chain rule, the Markov assumption and n-gram windows, the Markov chain of slide 61, counting and the MLE with its proof, the start and end tag convention, and questions 1 and 2 of the activity with the corrections to the answer sheet.',
    summary='The chain rule, the Markov assumption, MLE counting, the start and end tags, and the bigram and unigram activity.',
    keywords=['n-gram', 'bigram', 'unigram', 'trigram', 'Markov assumption', 'Markov chain', 'MLE', 'start and end tags', 'language model'],
    recap='<p>A language model gives every sentence a probability. The chain rule splits it into next word factors, the Markov assumption keeps only the last n − 1 words, and counting gives each factor as C(history word) ÷ C(history). The end tag is predicted, the start tag is not, so the activity corpus has N = 22.</p>')
