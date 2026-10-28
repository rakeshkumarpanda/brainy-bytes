# Chapter 5.2: finite state automata and the hidden Markov model. Source: lecture 9 (POS deck slides 10 to 29:
# the FSA five tuple, cat and car, sheep talk, the HMM five tuple, Mealy and Moore machines, the validity check of the
# killer clown HMM, training by counting, scoring every tag sequence) and problems G1 to G5 and H1 to H3.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('fsa', r'''
# A finite state automaton as a dictionary: (state, symbol) -> next state
delta = {("q0", "c"): "q1", ("q1", "a"): "q2", ("q2", "t"): "q3", ("q2", "r"): "q3"}
final = {"q3"}

def accepts(s):
    state = "q0"
    for ch in s:
        if (state, ch) not in delta:
            return False, state + " has no arrow for " + ch
        state = delta[(state, ch)]
    return state in final, "ended in " + state

for word in ["cat", "car", "ca", "cut", "cart"]:
    print(word, accepts(word))
''')

K.code('valid', r'''
# Check the two validity rules of an HMM: every row of A and every row of B sums to 1
from fractions import Fraction as F
pi = {"A": F(1, 2), "N": F(1, 2)}
A = {"A": {"A": F(1, 3), "N": F(2, 3)}, "N": {"A": F(1, 10), "N": F(9, 10)}}
B = {"A": {"crazy": F(1)}, "N": {"killer": F(1, 3), "clown": F(1, 3), "problem": F(1, 3)}}

print("start sums to", sum(pi.values()))
for t in A:
    print("from", t, ": transitions sum to", sum(A[t].values()), " emissions sum to", sum(B[t].values()))
''')

K.code('joint', r'''
# The joint probability of words and tags: start, then emission, transition, emission, ...
pi = {"A": 0.25, "N": 0.75}
A = {"A": {"A": 0.0, "N": 1.0}, "N": {"A": 0.5, "N": 0.5}}
B = {"A": {"killer": 0.0, "clown": 0.0}, "N": {"killer": 0.3, "clown": 0.4}}

def joint(words, tags):
    p = pi[tags[0]] * B[tags[0]][words[0]]
    for i in range(1, len(words)):
        p *= A[tags[i - 1]][tags[i]] * B[tags[i]][words[i]]
    return p

words = ["killer", "clown"]
for tags in [["A", "A"], ["A", "N"], ["N", "A"], ["N", "N"]]:
    print(" ".join(tags), round(joint(words, tags), 4))
''')

K.code('train', r'''
# Supervised HMM training is counting: start tags, tag bigrams and (tag, word) pairs
from collections import Counter
corpus = [[("they", "N"), ("can", "M"), ("fish", "V")], [("they", "N"), ("fish", "V")],
          [("fish", "N"), ("can", "M"), ("swim", "V")], [("they", "N"), ("can", "V"), ("fish", "N")],
          [("swim", "V")]]
start, trans, emit, out, tagc = Counter(), Counter(), Counter(), Counter(), Counter()
for s in corpus:
    start[s[0][1]] += 1
    for (w, t) in s:
        emit[(t, w)] += 1
        tagc[t] += 1
    for (_, a), (_, b) in zip(s, s[1:]):
        trans[(a, b)] += 1
        out[a] += 1

print("pi:", {t: c / len(corpus) for t, c in start.items()})
print("A:", {a + "->" + b: c / out[a] for (a, b), c in sorted(trans.items())})
print("B:", {t + ":" + w: round(c / tagc[t], 2) for (t, w), c in sorted(emit.items())})
''')

K.lesson('fsa', 'Finite state automata', f'''
<p>Before probabilities come in, here is the machine underneath. A finite state automaton (FSA) reads a string one symbol at a time. It sits in one state, follows the arrow labelled with the symbol it reads, and at the end it says yes or no. Lift buttons, vending machines and traffic lights all work this way: a small set of situations and fixed rules for moving between them.</p>
{fxs(fx('The FSA five tuple', '(<i>Q</i>, Σ, <i>q</i>₀, δ, <i>F</i>)', '<i>Q</i> is the set of states, Σ the alphabet of symbols, <i>q</i>₀ the start state, δ the transition function (state, symbol) → state, and <i>F</i> the final states, drawn as double circles.', key=True))}
<p>The slide machine has Q = {{q0, q1, q2, q3}}, Σ = {{c, a, t, r}}, F = {{q3}} and four arrows: q0 c q1, q1 a q2, q2 t q3 and q2 r q3. A string is accepted only if two things hold: every symbol has an arrow to follow, and the machine ends in a final state.</p>
{viz('fsa')}
{table(['Input', 'Path', 'Result', 'Reason'], [
    ['cat', 'q0 → q1 → q2 → q3', 'accept', 'ends in q3, a final state'],
    ['car', 'q0 → q1 → q2 → q3', 'accept', 'the arrow q2 r q3 exists'],
    ['ca', 'q0 → q1 → q2', 'reject', 'q2 is not final'],
    ['cut', 'q0 → q1, stuck', 'reject', 'q1 has no arrow for u'],
    ['cart', 'q0 → … → q3, stuck', 'reject', 'q3 has no arrow for t']])}
<h3>Sheep talk</h3>
<p>The second slide machine accepts baa!, baaa!, baaaa! and so on: b, then at least two a\'s, then !. A self loop on q3 eats any number of extra a\'s. The regular expression is /baa+!/. Kleene\'s theorem says every regular expression has an equivalent FSA and the other way round.</p>
{deep('Why is the loop on q3 and not on q2?', '<p>A student asked this. Many machines accept the same language. A loop on any state reached after the first two a\'s gives /baa+!/. A loop on q1 would be wrong, since it would let "ba!" through with only one a. For every regular language there is one smallest deterministic machine, the minimal DFA.</p>')}
{code('fsa')}
{note('How does this help with language? Finite state machines run tokenisers, regular expression taggers, spelling checkers and morphology (leaves maps to leaf + N + PL). Put probabilities on the arrows and you get a Markov chain, the n-gram model of step 4. Let each state also emit a word and you get the HMM.', 'tip')}
''', kw=['finite state automaton', 'FSA', 'five tuple', 'states', 'transition function', 'final state', 'accept', 'reject', 'sheep talk', 'regular expression', 'Kleene'])

K.lesson('hmm', 'The hidden Markov model', f'''
<p>In tagging we see the words but not the tags. A hidden Markov model (HMM) explains the words with a hidden walk over tags. Picture a person in another room who flips between moods you cannot see, and each mood makes them shout certain words. You hear only the words and must guess the moods.</p>
{fxs(
    fx('The HMM five tuple', '(<i>Q</i>, <i>A</i>, <i>O</i>, <i>B</i>, π)', '<i>Q</i> the tag states, <i>A</i> the transition table P(tag | previous tag), <i>O</i> the vocabulary of words, <i>B</i> the emission table P(word | tag), π the start probabilities.', key=True),
    fx('Joint probability of words and tags', 'P(<i>W</i>, <i>T</i>) = π(<i>t</i>₁) <i>b</i><sub><i>t</i>₁</sub>(<i>w</i>₁) ∏<sub><i>i</i>=2</sub><sup><i>n</i></sup> <i>a</i><sub><i>t</i><sub><i>i</i>−1</sub><i>t<sub>i</sub></i></sub> <i>b</i><sub><i>t<sub>i</sub></i></sub>(<i>w<sub>i</sub></i>)', 'One start, n emissions and n − 1 transitions: 2n factors in all. "We multiply the transition probability with the emission probability" at every position.', key=True))}
{steps('The two assumptions that make the formula short', [
    'Markov assumption: a tag depends only on the tag before it. P(t<sub>i</sub> | t<sub>1</sub> … t<sub>i−1</sub>) ≈ P(t<sub>i</sub> | t<sub>i−1</sub>).',
    'Output independence: a word depends only on its own tag. P(w<sub>i</sub> | all tags and other words) ≈ P(w<sub>i</sub> | t<sub>i</sub>).',
    'Start from the exact chain rule P(W, T) = P(T) P(W | T).',
    'The first assumption turns P(T) into π(t₁) × a product of tag bigrams.',
    'The second turns P(W | T) into a product of emissions b<sub>t<sub>i</sub></sub>(w<sub>i</sub>). Multiply the two and regroup position by position.'])}
<h3>British Left Waffles written out</h3>
<p>For the reading N N V P N N the twelve factors are:</p>
<p>{eq('P(N) P(British | N) · P(N | N) P(Left | N) · P(V | N) P(Waffles | V) · P(P | V) P(on | P) · P(N | P) P(Falkland | N) · P(N | N) P(Islands | N)')}</p>
<p>A tag bigram alone would miss the words. A word bigram alone would miss the tags. The HMM multiplies both because it scores words and tags together.</p>
<h3>Two kinds of machine</h3>
{table(['Machine', 'Output is attached to', 'In the HMM'], [
    ['Mealy', 'each arrow (transition)', 'not used'],
    ['Moore', 'each state', 'yes: a tag state emits a word']])}
<p>The two are equally powerful. The professor\'s summary: an HMM is essentially the finite state automaton with probabilities, a probabilistic Moore machine. It starts in state i with probability π<sub>i</sub>, moves from i to j with P(j | i) and emits word o from state j with P(o | j).</p>
{note('Do not confuse an HMM with a bigram word model. In the bigram model the thing you condition on, the previous word, is visible. In the HMM it is a hidden tag, so to find tags you must search (Viterbi) or sum (forward) over them.', 'warn')}
''', kw=['hidden Markov model', 'HMM', 'five tuple', 'transition', 'emission', 'start probability', 'Markov assumption', 'output independence', 'joint probability', 'Mealy', 'Moore'])

K.lesson('valid', 'Is this HMM valid?', f'''
<p>Two rules, checked row by row. Every state\'s outgoing transitions sum to 1. Every state\'s emissions sum to 1. The start probabilities sum to 1 as well.</p>
<p>The slide HMM has two tags, A (adjective) and N (noun), and four words: crazy, killer, clown and problem.</p>
{table(['', 'to A', 'to N', 'Sum'], [
    ['π (start)', '1/2', '1/2', '1'],
    ['from A', '1/3', '2/3', '1'],
    ['from N', '1/10', '9/10', '1']])}
{table(['Emits', 'crazy', 'killer', 'clown', 'problem', 'Sum'], [
    ['A', '1', '0', '0', '0', '1'],
    ['N', '0', '1/3', '1/3', '1/3', '1']])}
{steps('The class exercise, one line at a time', [
    'From A: 1/3 + 2/3 = 1.',
    'From N: 1/10 + 9/10 = 1.',
    'A emits only crazy, with probability 1. So b<sub>A</sub>(killer) = 0, "not because killer is a noun, but because A already spends all its probability on crazy".',
    'N emits killer, clown and problem at 1/3 each, which is 1. So b<sub>N</sub>(crazy) = 0.',
    'Start: 1/2 + 1/2 = 1. Every row sums to 1, so the HMM is valid.'])}
{code('valid')}
{note('Exam questions often hide one cell. Fill it with 1 minus the rest of its row (problem G2). The rows are what sum to 1, never the columns: P(N | A) + P(N | N) = 2/3 + 9/10 is not 1 and does not need to be.', 'exam')}
''', kw=['valid HMM', 'rows sum to one', 'killer clown', 'crazy', 'missing cell', 'stochastic matrix'])

K.lesson('train', 'Training an HMM is counting', f'''
<p>Give the model sentences with their correct tags, and it fills three look up tables using the same maximum likelihood counting as the n-grams of step 4.</p>
{fxs(
    fx('Start', 'π(<i>t</i>) = ' + frac('C(sentences starting with <i>t</i>)', 'number of sentences'), ''),
    fx('Transition', '<i>a</i>(<i>t</i> → <i>u</i>) = ' + frac('C(<i>t u</i>)', 'C(<i>t</i> followed by any tag)'), 'The tag bigram MLE.', key=True),
    fx('Emission', '<i>b</i>(<i>w</i> | <i>t</i>) = ' + frac('C(<i>w</i> tagged <i>t</i>)', 'C(<i>t</i>)'), 'A unigram model of words for each tag.', key=True))}
{viz('hmmtrain')}
{steps('Problem G5 by hand', [
    'Corpus: they/N can/M fish/V · they/N fish/V · fish/N can/M swim/V · they/N can/V fish/N · swim/V.',
    'Start tags: N four times, V once. π = (N 4/5, V 1/5).',
    'Tag bigrams: N M 2, N V 2, M V 2, V N 1. Out of N there are 4, so a(N → M) = a(N → V) = 1/2. a(M → V) = 1 and a(V → N) = 1.',
    'Emissions: N is they 3 and fish 2 (5 in all), M is can 2, V is fish 2, swim 2 and can 1 (5 in all).',
    'b<sub>N</sub>: they 3/5, fish 2/5. b<sub>M</sub>(can) = 1. b<sub>V</sub>: fish 2/5, swim 2/5, can 1/5.',
    'Read the zeros: N never followed N, so "fish fish" as N N gets probability 0. Real taggers smooth A and B, exactly as in chapter 4.3.'])}
{code('train')}
{deep('Training without tags', '<p>If you have only raw text, the Baum-Welch algorithm (an instance of expectation maximisation) guesses tag counts from the forward and backward probabilities, re-estimates A and B from those soft counts, and repeats. Each round cannot lower the likelihood of the text, but it can stop at a poor local optimum, and the hidden states it finds need not match linguists\' tags.</p>')}
''', kw=['training', 'MLE', 'counting', 'start probability', 'transition count', 'emission count', 'zeros', 'smoothing', 'Baum-Welch', 'EM'])

K.lesson('score', 'Scoring every tag sequence', f'''
<p>With the tables in hand, the HMM can score any tag sequence for a sentence. For a short sentence you can simply score them all and keep the largest. The slide 27 HMM has π<sub>A</sub> = 0.25, π<sub>N</sub> = 0.75, a<sub>AA</sub> = 0, a<sub>AN</sub> = 1, a<sub>NA</sub> = a<sub>NN</sub> = 0.5, b<sub>N</sub>(killer) = 0.3, b<sub>N</sub>(clown) = 0.4 and A emits neither word.</p>
{table(['Tags', 'π · b(killer) · a · b(clown)', 'P(W, T)'], [
    ['A A', '0.25 × 0 × 0 × 0', '0'],
    ['A N', '0.25 × 0 × 1.0 × 0.4', '0'],
    ['N A', '0.75 × 0.3 × 0.5 × 0', '0'],
    ['N N', '0.75 × 0.3 × 0.5 × 0.4', '<b>0.045</b>']])}
<p>The winner is killer/N clown/N. A zero emission kills a path at once, so strike those out first.</p>
{code('joint')}
{note('Two different killer clown HMMs appear in the deck. Slides 23 and 24 give P(killer clown, N N) = 1/2 × 1/3 × 9/10 × 1/3 = 0.05. Slide 27 gives 0.045. Same winner, different number. Always use the tables the question gives you (problem G4).', 'warn')}
{scene('reading a shipping label', '<p>A warehouse scanner reads "ORANGE BOX 12". Is ORANGE a colour (adjective) or a fruit (noun)? A small HMM trained on past labels scores both tag paths. Adjective then noun then number is common on labels, noun noun number is rarer, so the scanner files it under colour. With two or three words, scoring every path is instant. With a 25 word sentence and 45 tags it would never finish, which is the subject of the next chapter.</p>')}
{ladder(
    '<p>Hidden tags walk from one to the next, and each tag says a word. Multiply the chance of each step and each word, and pick the walk with the biggest result.</p>',
    '<p>An HMM is (Q, A, O, B, π). P(W, T) is a product of 2n factors. Train by counting. Check that each row sums to 1. For tiny inputs, enumerate all q<sup>n</sup> sequences.</p>',
    '<p>The HMM is a generative model of P(W, T) with a first order Markov chain over hidden states and conditionally independent emissions. Supervised MLE is closed form. Unsupervised training uses Baum-Welch. Inference is dynamic programming over the trellis.</p>',
    '<p>HMMs are the simplest dynamic Bayesian networks. Extensions include higher order HMMs (TnT), factorial and hierarchical HMMs, and neural HMMs where emissions come from a network. Linear chain CRFs are their discriminative counterpart.</p>')}
''', kw=['enumeration', 'score tag sequence', 'killer clown', 'slide 27', 'zero emission', 'two HMMs'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In an FSA, a double circle marks', ['The start state', 'A final (accepting) state', 'A dead state', 'A loop'], 1,
       'Where may the machine stop?', 'Strings are accepted only if they end in one of these.')
K.quiz('e', 'The cat and car FSA reads "ca". The result is', ['Accept', 'Reject, q2 is not final', 'Reject, no arrow for a', 'It loops forever'], 1,
       'Where does it stop?', 'It reaches q2, which is not a final state.')
K.quiz('e', 'Which regular expression matches sheep talk?', ['/ba+!/', '/baa+!/', '/b+a!/', '/(ba)+!/'], 1,
       'At least two a\'s.', 'b, a, then one or more extra a\'s, then !.')
K.quiz('e', 'In an HMM, which part is hidden?', ['The words', 'The tags', 'The vocabulary', 'The number of states'], 1,
       'What must we infer?', 'We observe words and infer the tags that generated them.')
K.quiz('m', 'P(British | N) is', ['A transition probability', 'An emission probability', 'A start probability', 'A perplexity'], 1,
       'Word given tag.', 'It is the probability that tag N emits the word British.')
K.quiz('m', 'How many factors does P(W, T) have for a 7 word sentence?', ['7', '13', '14', '49'], 2,
       '1 start, n emissions, n − 1 transitions.', '1 + 7 + 6 = 14 = 2n.')
K.quiz('m', 'An HMM is closest to which kind of machine?', ['A Mealy machine', 'A probabilistic Moore machine', 'A Turing machine', 'A stack machine'], 1,
       'Is output on states or on arrows?', 'Each tag state emits a word.')
K.quiz('m', 'In the slide 24 HMM, why is b<sub>A</sub>(killer) = 0?', ['Killer is a noun', 'A spends all its emission probability on crazy', 'Killer is rare', 'A is never a start state'], 1,
       'Rows sum to 1.', 'A emits crazy with probability 1, so nothing is left for other words.')
K.quiz('m', 'Which sums to 1 in a valid HMM?', ['Each column of A', 'Each row of A and each row of B', 'The diagonal of A', 'All of B together'], 1,
       'Outgoing from each state.', 'Transitions out of a state and emissions from a state are each a distribution.')
K.quiz('h', 'From G5, a(N → N) = 0. What happens to "fish fish" tagged N N?', ['It gets a small probability', 'It gets probability 0 until A is smoothed', 'It is rejected by the FSA', 'It becomes N V'], 1,
       'Any zero factor.', 'One zero factor makes the whole product 0. Smoothing fixes this.')
K.quiz('h', 'Which assumption lets us write P(W | T) as a product of b<sub>t<sub>i</sub></sub>(w<sub>i</sub>)?', ['Markov assumption', 'Output independence', 'Zipf\'s law', 'Bayes rule'], 1,
       'Words depend on what?', 'Each word depends only on its own tag.')
K.quiz('x', 'A loop on q1 reading a in the sheep machine would', ['Accept the same language', 'Also accept "ba!"', 'Reject everything', 'Accept "b!"'], 1,
       'How many a\'s are then required?', 'It lets a string with only one a reach the ! arrow, so "ba!" would be accepted, which is wrong.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'How many factors does the HMM joint probability have for a 5 word sentence?', '10', '1 start, n emissions, n − 1 transitions.',
       ['Start: 1 factor.', 'Emissions: 5. Transitions: 4.', eq('1 + 5 + 4 = 10 = 2 × 5')], check=10, tol=0.01)
K.calc('e', 'P(A | N) = 1/10. What is P(N | N) in a two tag HMM? Give a decimal.', '0.9', 'Outgoing arcs sum to 1.',
       ['Out of N the only tags are A and N.', 'P(A | N) + P(N | N) = 1.', eq('P(N | N) = 1 − 0.1 = 0.9')], check=0.9, tol=0.001)
K.calc('e', 'Problem H3: an FSA accepts (he or she) then (is or was) then (happy or sad). How many sentences does it accept?', '8', 'Each step chooses one of two words.',
       ['Step 1: 2 choices.', 'Step 2: 2 choices. Step 3: 2 choices.', eq('2 × 2 × 2 = 8')], check=8, tol=0.01)
K.calc('m', 'Slide 27 HMM: π<sub>N</sub> = 0.75, b<sub>N</sub>(killer) = 0.3, a<sub>NN</sub> = 0.5, b<sub>N</sub>(clown) = 0.4. What is P(killer clown, N N)? Three decimals.', '0.045', 'Start, emit, move, emit.',
       ['π<sub>N</sub> × b<sub>N</sub>(killer) = 0.75 × 0.3 = 0.225.', '× a<sub>NN</sub> = 0.225 × 0.5 = 0.1125.', eq('× b<sub>N</sub>(clown) = 0.1125 × 0.4 = 0.045')], check=0.045, tol=0.0005)
K.calc('m', 'Slide 24 HMM: π<sub>N</sub> = 1/2, b<sub>N</sub>(killer) = 1/3, a<sub>NN</sub> = 9/10, b<sub>N</sub>(clown) = 1/3. What is P(killer clown, N N)? Two decimals.', '0.05', 'Multiply the four fractions.',
       ['1/2 × 1/3 = 1/6.', '1/6 × 9/10 = 9/60 = 3/20.', eq('3/20 × 1/3 = 1/20 = 0.05')], check=0.05, tol=0.0005)
K.calc('m', 'Problem G3, slide 24 HMM: score "crazy clown" as A N. π<sub>A</sub> = 1/2, b<sub>A</sub>(crazy) = 1, a<sub>AN</sub> = 2/3, b<sub>N</sub>(clown) = 1/3. Four decimals.', '0.1111', 'Only A N survives.',
       ['1/2 × 1 = 1/2.', '1/2 × 2/3 = 1/3.', eq('1/3 × 1/3 = 1/9 = 0.1111')], check=1 / 9, tol=0.0001)
K.calc('m', 'Problem G5: in the corpus, tag V is used 5 times and emits fish twice. What is b<sub>V</sub>(fish)?', '0.4', 'Count of (V, fish) over count of V.',
       ['C(fish tagged V) = 2.', 'C(V) = 5.', eq('2 ÷ 5 = 0.4')], check=0.4, tol=0.001)
K.calc('h', 'With the G5 tables, score they/N can/M fish/V. π<sub>N</sub> = 4/5, b<sub>N</sub>(they) = 3/5, a(N → M) = 1/2, b<sub>M</sub>(can) = 1, a(M → V) = 1, b<sub>V</sub>(fish) = 2/5. Three decimals.', '0.096', 'Six factors.',
       ['4/5 × 3/5 = 12/25.', '× 1/2 × 1 = 6/25.', '× 1 × 2/5 = 12/125.', eq('12/125 = 0.096')], check=0.096, tol=0.0005)
K.calc('h', 'Problem H8 shares every factor except these. Reading N N V P: 0.3 × 0.01 × 0.4 × 0.001 × 0.4. Reading N V N P: 0.4 × 0.02 × 0.5 × 0.005 × 0.3. How many times more likely is N V N P N N? One decimal.', '12.5', 'Compute both middle products and divide.',
       ['N N V P: 0.3 × 0.01 × 0.4 × 0.001 × 0.4 = 4.8 × 10⁻⁷.', 'N V N P: 0.4 × 0.02 × 0.5 × 0.005 × 0.3 = 6.0 × 10⁻⁶.', 'The shared start and tail cancel in the ratio.', eq('6.0 × 10⁻⁶ ÷ 4.8 × 10⁻⁷ = 12.5')], check=12.5, tol=0.01)
K.calc('h', 'How many strings of length 6 or less does the sheep machine /baa+!/ accept?', '3', 'The shortest is baa!.',
       ['Accepted strings are b, then k ≥ 2 a\'s, then !, so length k + 2.', 'Length ≤ 6 means k ≤ 4, so k = 2, 3 or 4.', eq('baa!, baaa!, baaaa!: 3 strings')], check=3, tol=0.01)
K.calc('x', 'An HMM has 45 tags and a vocabulary of 10,000 words. How many free parameters do π, A and B have together (each distribution sums to 1)?', '451979', 'Each distribution of size k has k − 1 free values.',
       ['π: 45 − 1 = 44.', 'A: 45 rows × 44 = 1,980.', 'B: 45 rows × 9,999 = 449,955.', eq('44 + 1,980 + 449,955 = 451,979')], check=451979, tol=0.5)

# ---------------------------------------------------------------- assignments
K.assign('runfsa', 'e', 'Run a finite state automaton',
         '<p>Write <code>accepts(delta, final, s)</code>. delta is a dict from (state, symbol) to the next state, final is a set of final states, the start state is "q0" and s is a string read one character at a time. Return True only if every character has an arrow and the last state is final.</p>',
         '''
def accepts(delta, final, s):
    # your code here
    pass
''', [('accepts({("q0", "c"): "q1", ("q1", "a"): "q2", ("q2", "t"): "q3", ("q2", "r"): "q3"}, {"q3"}, "car")', True),
      ('accepts({("q0", "c"): "q1", ("q1", "a"): "q2", ("q2", "t"): "q3"}, {"q3"}, "ca")', False),
      ('accepts({("q0", "b"): "q1", ("q1", "a"): "q2", ("q2", "a"): "q3", ("q3", "a"): "q3", ("q3", "!"): "q4"}, {"q4"}, "baaaa!")', True),
      ('accepts({("q0", "b"): "q1", ("q1", "a"): "q2", ("q2", "a"): "q3", ("q3", "a"): "q3", ("q3", "!"): "q4"}, {"q4"}, "ba!")', False)],
         '''
def accepts(delta, final, s):
    state = "q0"
    for ch in s:
        if (state, ch) not in delta:
            return False
        state = delta[(state, ch)]
    return state in final
''', 'Stop with False as soon as an arrow is missing.', '<p>Both failure modes appear in the tests: "ca" ends in a non final state and "ba!" gets stuck.</p>')
K.assign('jointp', 'm', 'The HMM joint probability',
         '<p>Write <code>joint(pi, A, B, words, tags)</code> that returns P(words, tags) rounded to 6 decimals. pi maps tag to probability, A[t][u] is P(u | t) and B[t] maps words to P(word | t). A word missing from B[t] has probability 0.</p>',
         '''
def joint(pi, A, B, words, tags):
    # your code here
    pass
''', [('joint({"A": 0.25, "N": 0.75}, {"A": {"A": 0, "N": 1}, "N": {"A": 0.5, "N": 0.5}}, {"A": {}, "N": {"killer": 0.3, "clown": 0.4}}, ["killer", "clown"], ["N", "N"])', 0.045),
      ('joint({"A": 0.25, "N": 0.75}, {"A": {"A": 0, "N": 1}, "N": {"A": 0.5, "N": 0.5}}, {"A": {}, "N": {"killer": 0.3, "clown": 0.4}}, ["killer", "clown"], ["N", "A"])', 0.0),
      ('joint({"N": 0.8, "M": 0, "V": 0.2}, {"N": {"N": 0, "M": 0.5, "V": 0.5}, "M": {"N": 0, "M": 0, "V": 1}, "V": {"N": 1, "M": 0, "V": 0}}, {"N": {"they": 0.6, "fish": 0.4}, "M": {"can": 1}, "V": {"fish": 0.4, "swim": 0.4, "can": 0.2}}, ["they", "can", "fish"], ["N", "M", "V"])', 0.096)],
         '''
def joint(pi, A, B, words, tags):
    p = pi[tags[0]] * B[tags[0]].get(words[0], 0)
    for i in range(1, len(words)):
        p *= A[tags[i - 1]][tags[i]] * B[tags[i]].get(words[i], 0)
    return round(p, 6)
''', 'Start with pi times the first emission, then multiply a transition and an emission for each later word.', '<p>The third test is problem G7\'s winning path, 12/125.</p>')
K.assign('trainhmm', 'm', 'Train the start and transition tables',
         '<p>Write <code>train(sents)</code>. sents is a list of sentences of (word, tag) pairs. Return (pi, A) where pi maps each start tag to its share of sentences and A maps the string "t u" to C(t u) ÷ C(t followed by any tag). Round every value to 4 decimals.</p>',
         '''
def train(sents):
    # your code here
    pass
''', [('train([[("they", "N"), ("can", "M"), ("fish", "V")], [("they", "N"), ("fish", "V")], [("fish", "N"), ("can", "M"), ("swim", "V")], [("they", "N"), ("can", "V"), ("fish", "N")], [("swim", "V")]])',
       ({'N': 0.8, 'V': 0.2}, {'N M': 0.5, 'M V': 1.0, 'N V': 0.5, 'V N': 1.0})),
      ('train([[("a", "D"), ("dog", "N")], [("dogs", "N")]])', ({'D': 0.5, 'N': 0.5}, {'D N': 1.0}))],
         '''
from collections import Counter

def train(sents):
    start, pair, out = Counter(), Counter(), Counter()
    for s in sents:
        start[s[0][1]] += 1
        for (_, a), (_, b) in zip(s, s[1:]):
            pair[(a, b)] += 1
            out[a] += 1
    pi = {t: round(c / len(sents), 4) for t, c in start.items()}
    A = {a + " " + b: round(c / out[a], 4) for (a, b), c in pair.items()}
    return (pi, A)
''', 'Count transitions out of each tag, not the total uses of the tag. The last tag of a sentence has no transition.', '<p>This is problem G5. The single word sentence "swim/V" adds a start but no transition.</p>')

K.must('FSA', 'Five tuple (Q, Σ, q0, δ, F). Accept only if every symbol has an arrow and the machine ends in a final state. Sheep talk is /baa+!/.')
K.must('HMM', 'Five tuple (Q, A, O, B, π). Tags are hidden, words are observed. A probabilistic Moore machine: states emit words.')
K.must('Joint probability', 'P(W, T) = π(t1) b(w1 | t1) × product over i ≥ 2 of a(t(i−1) → ti) b(wi | ti). 2n factors. Markov and output independence assumptions.')
K.must('Validity', 'Each row of A, each row of B and π sums to 1. A missing cell is 1 minus the rest of its row.')
K.must('Training', 'Count starts, tag bigrams and (tag, word) pairs, then divide by row totals. Zeros need smoothing.')

T = K.topic(
    slug='hmm', topic='hmm', step=(5, 'Tagging and syntax', 'nlp-syntax', 'Tag every word with its part of speech using HMMs and Viterbi, mark chunks and names with IOB, and draw constituency and dependency trees.', 'College and masters'),
    title='Finite state machines and the HMM', short='FSA and HMM', badge='5.2', minutes=45,
    lead='Run strings through a finite state automaton, add probabilities to get a hidden Markov model, check that it is valid, train it by counting and score every tag sequence.',
    desc='The FSA five tuple with the cat and car machine and sheep talk, the HMM five tuple with its two assumptions, Mealy and Moore machines, the joint probability of British Left Waffles, the killer clown validity check, training by counting with problem G5, and scoring all tag sequences.',
    summary='FSAs, the HMM five tuple, the joint probability, validity checks, training by counting and enumeration.',
    keywords=['FSA', 'finite state automaton', 'HMM', 'transition', 'emission', 'Moore machine', 'killer clown', 'training'],
    recap='<p>An FSA accepts or rejects strings by following arrows. An HMM adds probabilities: hidden tags move with transition probabilities and emit words with emission probabilities. Every row sums to 1, training is counting, and a tag sequence scores the product of 2n factors.</p>')
