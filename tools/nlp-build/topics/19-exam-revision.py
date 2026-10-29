# Chapter 6.1: exam revision. One place to revise the whole subject, organised by the kind of exam rather than by topic:
# school and first year questions, university semester and IIT course numericals, multiple choice and numerical answer
# papers in the NPTEL and GATE style, and derivation questions in the style of MIT, Stanford and Cambridge.
# Every question here is an original practice question written in the style of that tier, not a copy of a past paper.
# Every number was checked with Python before it was written down. The course's own exam remarks come from the
# lecture 7 to 9 notes (section 1.1: derivations, hand computation of HMM decoding, definitions with examples).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('drill', r'''
# Exam drill: from the probability of each predicted token to log probability and perplexity
import math
probs = [float(x) for x in input("probabilities of each predicted token (</s> included): ").split()]
lp10 = sum(math.log10(p) for p in probs)
lp2 = sum(math.log2(p) for p in probs)
n = len(probs)
print("P(sentence)        =", round(math.prod(probs), 6))
print("log10 probability  =", round(lp10, 5))
print("cross entropy H    =", round(-lp2 / n, 4), "bits per token")
print("perplexity 2 ** H  =", round(2 ** (-lp2 / n), 4))
print("same as 10 ** (-lp10 / n) =", round(10 ** (-lp10 / n), 4))
''', stdin='0.2 0.4 0.3333333 0.4\n')

K.lesson('map', 'How NLP is examined', f'''
<p>This chapter is for the week before an exam. It does not teach new material. It shows the shapes questions take at each level, with worked answers, and points back to the chapter where each idea is taught. The questions are original practice questions written in the style of each tier, not copies of real past papers.</p>
{table(['Tier', 'Typical format', 'What earns the marks', 'Where to practise'], [
    ['School and first year', 'Short answers, counting, small probabilities', 'Clear definitions with an example, careful counting', 'Lesson 2'],
    ['University semester and IIT course exams', 'Numericals by hand, short notes, compare and contrast', 'Formula first, every step shown, the final answer stated with its meaning', 'Lesson 3'],
    ['NPTEL and GATE style papers', 'Multiple choice, multiple select and numerical answer type, no partial credit', 'Speed, recognising the trap option, exact rounding', 'Lesson 4'],
    ['MIT, Stanford and Cambridge style', 'Derivations, proofs, design and critique', 'Assumptions named, a complete argument, when it breaks', 'Lesson 5']])}
<p>The professor of this course said three things plainly. Derivations will be examined: "if you know how to derive, you know how it works". Hand computation will be examined: given a word sequence and the emission, transition and start tables, you must find the most likely tag sequence. Definitions will be asked with examples: stem against lemma, why perplexities are only comparable with the same vocabulary, and why we never train on the test set.</p>
<h3>The twelve ideas examined most often</h3>
<ol>
<li>Kinds of ambiguity with an example of each (chapter 1.2).</li>
<li>Tokens against types, sentence segmentation traps (chapter 2.1).</li>
<li>Stem against lemma, the Porter steps (chapter 2.2).</li>
<li>Zipf\'s law, f × r ≈ constant (chapter 3.1).</li>
<li>Surprisal, entropy and redundancy (chapter 3.2).</li>
<li>Conditional entropy, mutual information, KL and cross entropy (chapter 3.3).</li>
<li>Bigram MLE from a toy corpus with &lt;s&gt; and &lt;/s&gt; (chapter 4.1).</li>
<li>Log probability, perplexity, and the effect of &lt;/s&gt; and OOVs (chapters 4.2 and 4.4).</li>
<li>Laplace, add-k, interpolation and backoff (chapter 4.3).</li>
<li>The HMM joint probability and a validity check (chapter 5.2).</li>
<li>Viterbi by hand, forward and the posterior (chapter 5.3).</li>
<li>IOB, constituency tests, dependency trees and PCFG attachment (chapters 5.4 and 5.5).</li>
</ol>
''', kw=['exam pattern', 'revision', 'school', 'university exam', 'IIT', 'NPTEL', 'GATE', 'MIT', 'Stanford', 'Cambridge', 'derivations', 'hand computation'])

K.lesson('school', 'Tier 1: school and first year', f'''
<p>Questions at this level check that you can count words, read a simple probability and explain an idea with an example.</p>
{fxs(
    fx('Type token ratio', 'TTR = ' + frac('number of types', 'number of tokens'), 'Types are distinct words. Tokens are running words.', key=True),
    fx('Zipf\'s law', '<i>f</i> × <i>r</i> ≈ <i>C</i>', 'The word of rank r appears about C ÷ r times.', key=True),
    fx('Entropy', '<i>H</i> = −Σ <i>p</i> log₂ <i>p</i>', 'Average surprise in bits. A fair coin has 1 bit.'))}
{steps('Question 1. Count tokens and types in "the cat sat on the mat".', [
    'Tokens: the, cat, sat, on, the, mat, so 6.',
    'Types: the, cat, sat, on, mat, so 5, since the appears twice.',
    'TTR = 5 ÷ 6 ≈ 0.833.'])}
{steps('Question 2. The commonest word in a corpus appears 60,000 times. By Zipf\'s law, about how often does the third commonest appear?', [
    'f × r ≈ C, so C ≈ 60,000 × 1 = 60,000.',
    'For r = 3, f ≈ 60,000 ÷ 3.',
    '≈ 20,000 times. Real counts wobble around this line, especially at the top ranks.'])}
{steps('Question 3. Give the stem and the lemma of "studies" and of "better".', [
    'A stemmer chops suffixes by rule: studies → studi, better → better.',
    'A lemmatiser looks words up: studies → study, better → good (as an adjective).',
    'A stem need not be a real word, a lemma always is.'])}
{steps('Question 4. Four outcomes have probabilities 1/2, 1/4, 1/8 and 1/8. Find the entropy.', [
    'Surprisals: 1, 2, 3 and 3 bits.',
    'H = 1/2 × 1 + 1/4 × 2 + 1/8 × 3 + 1/8 × 3.',
    '= 0.5 + 0.5 + 0.375 + 0.375 = 1.75 bits.'])}
<p>Short answer favourites: name the six levels of linguistic structure (chapter 1.1), give one lexical and one structural ambiguity (chapter 1.2), explain what the Turing test checks and what it misses (chapter 1.3), and say why "Mr. Smith arrived." is hard for a sentence splitter (chapter 2.1).</p>
{note('Do not mix tokens and types. "How many words" is ambiguous in an exam. Say which you counted.', 'warn')}
''', kw=['tokens', 'types', 'type token ratio', 'Zipf', 'stem', 'lemma', 'entropy', 'bits', 'short answer', 'definitions'])

K.lesson('semester', 'Tier 2: university semester and IIT course exams', f'''
<p>Here the examiner gives a toy corpus or a set of tables and asks you to work by hand. Show every step. The corpus below is the one used in the n-gram chapters.</p>
{table(['Training corpus'], [['&lt;s&gt; I am Sam &lt;/s&gt;'], ['&lt;s&gt; Sam I am &lt;/s&gt;'], ['&lt;s&gt; Sam I like &lt;/s&gt;'], ['&lt;s&gt; Sam I do like &lt;/s&gt;'], ['&lt;s&gt; do I like Sam &lt;/s&gt;']])}
{viz('ngramlm')}
{steps('Question 5. Find P(I like Sam) with a bigram MLE model, including &lt;/s&gt;.', [
    'P(I | &lt;s&gt;) = C(&lt;s&gt; I) ÷ C(&lt;s&gt;) = 1 ÷ 5 = 0.2.',
    'P(like | I) = 2 ÷ 5 = 0.4. P(Sam | like) = 1 ÷ 3. P(&lt;/s&gt; | Sam) = 2 ÷ 5 = 0.4.',
    eq('0.2 × 0.4 × 0.3333 × 0.4 = 0.010667')])}
{steps('Question 6. Find the perplexity of that sentence.', [
    'Predicted tokens: I, like, Sam and &lt;/s&gt;, so N = 4. &lt;s&gt; is only context.',
    'PP = P<sup>−1/N</sup> = 0.010667<sup>−1/4</sup>.',
    eq('PP ≈ 3.112')])}
{steps('Question 7. Redo P(I | &lt;s&gt;) with Laplace smoothing. The vocabulary has V = 6 types (I, am, Sam, like, do, &lt;/s&gt;).', [
    'P<sub>Lap</sub>(w | h) = (C(h w) + 1) ÷ (C(h) + V).',
    '(1 + 1) ÷ (5 + 6) = 2 ÷ 11.',
    eq('≈ 0.1818, a little lower than 0.2, since mass moved to unseen pairs')])}
{steps('Question 8. Decode "they can fish" with the three tag HMM of chapter 5.3.', [
    't = 1: v(N) = 0.7 × 0.3 = 0.21, M and V are 0.',
    't = 2: v(M) = 0.21 × 0.4 × 1.0 = 0.084, v(V) = 0.21 × 0.4 × 0.3 = 0.0252, v(N) = 0.0084.',
    't = 3: v(V) = max(0.00336, 0.0756, 0.00756) × 0.7 = 0.05292 from M.',
    eq('they/N can/M fish/V, P = 0.05292')])}
{steps('Question 9. A PCFG gives P(VP → VP PP) = 0.3 and P(NP → NP PP) = 0.2, and the two parses of "I shot an elephant in my pajamas" share every other rule. Which wins?', [
    'Shared rules cancel in the ratio.',
    'VP attachment ∝ 0.3 × P(VP → V NP) = 0.3 × 0.7 = 0.21. NP attachment ∝ 0.7 × 0.2 = 0.14.',
    'Ratio 1.5, so VP attachment: I wore the pajamas.'])}
<p>Short notes and compare questions at this level: stemming against lemmatisation (chapter 2.2), backoff against interpolation (chapter 4.3), PP against PP1 in SRILM (chapter 4.4), generative against discriminative taggers (chapter 5.1), Mealy against Moore machines (chapter 5.2), chunks against constituents (chapter 5.4), dependency against phrase structure (chapter 5.5).</p>
{note('State your convention for &lt;s&gt; and &lt;/s&gt; before computing. Counting &lt;/s&gt; as a predicted token changes both the probability and the N in perplexity.', 'warn')}
''', kw=['bigram MLE', 'toy corpus', 'perplexity by hand', 'Laplace', 'Viterbi by hand', 'PCFG', 'compare and contrast', 'short notes'])

K.lesson('mcq', 'Tier 3: multiple choice and numerical answer papers', f'''
<p>NPTEL course exams and GATE style papers use multiple choice, multiple select and numerical answer questions with no partial credit. Learn the shortcuts and the trap options.</p>
{table(['Shortcut', 'Use it for'], [
    ['Uniform over k outcomes: H = log₂ k, PP = k', 'Instant entropy and perplexity of a uniform model'],
    ['PP = 2<sup>H</sup> = 10<sup>−log10 P ÷ N</sup>', 'Switching between bits and SRILM\'s base 10'],
    ['n-gram table size V<sup>n</sup>', 'Why trigrams are sparse'],
    ['IOB labels 2k + 1, BIOES 4k + 1', 'Label counts for k entity types'],
    ['Brute force q<sup>T</sup>, Viterbi T q², trigram HMM T q³', 'Complexity questions'],
    ['Dependency tree: n words, n arcs with ROOT', 'Counting arcs'],
    ['KL ≥ 0, equal to 0 only when P = Q', 'True or false on divergences'],
    ['H(X, Y) = H(X) + H(Y | X)', 'Chain rule for entropy']])}
{steps('Question 10. P = (1/2, 1/2), Q = (3/4, 1/4). Find KL(P ‖ Q) in bits.', [
    'KL = Σ P log₂(P ÷ Q).',
    '= 0.5 log₂(0.5 ÷ 0.75) + 0.5 log₂(0.5 ÷ 0.25) = 0.5 × (−0.585) + 0.5 × 1.',
    eq('≈ 0.2075 bits. Cross entropy H(P, Q) = H(P) + KL = 1.2075 bits')])}
{steps('Question 11. P(x, y) = 0.01, P(x) = 0.05 and P(y) = 0.1. Find the pointwise mutual information.', [
    'PMI = log₂ P(x, y) ÷ (P(x) P(y)).',
    'P(x) P(y) = 0.005, so the ratio is 2.',
    eq('PMI = 1 bit: they occur together twice as often as chance')])}
{steps('Question 12. A model gives every word of a 1,000 word vocabulary the same probability. What is its perplexity?', [
    'P(w) = 1 ÷ 1,000 for every word.',
    'H = log₂ 1,000 ≈ 9.97 bits.',
    eq('PP = 2<sup>H</sup> = 1,000')])}
{note('Trap options to expect: counting &lt;s&gt; as a predicted token, mixing log base 2 and 10, forgetting to add V in the Laplace denominator, treating columns of an HMM table as summing to 1, and calling a chunk a constituent.', 'exam')}
''', kw=['MCQ', 'numerical answer', 'NPTEL', 'GATE', 'shortcuts', 'KL divergence', 'PMI', 'uniform perplexity', 'complexity', 'traps'])

K.lesson('derive', 'Tier 4: derivations, design and critique', f'''
<p>Research university exams in the style of MIT, Stanford and Cambridge reward a complete argument more than a final number. State assumptions, derive the result, then say when it fails.</p>
<h3>Question 13. Show that the bigram MLE is a relative frequency.</h3>
{steps('Model answer', [
    'For one history h, maximise L = Σ<sub>w</sub> C(h w) log θ<sub>w</sub> subject to Σ<sub>w</sub> θ<sub>w</sub> = 1.',
    'Lagrangian: Σ C(h w) log θ<sub>w</sub> − λ (Σ θ<sub>w</sub> − 1). Setting the derivative to 0 gives C(h w) ÷ θ<sub>w</sub> = λ.',
    'So θ<sub>w</sub> = C(h w) ÷ λ. Summing over w gives λ = Σ C(h w) = C(h).',
    eq('θ<sub>w</sub> = C(h w) ÷ C(h)'),
    'It fails for unseen pairs, which get 0. That is why we smooth.'])}
<h3>Question 14. Show that perplexity is 2 to the power of the cross entropy.</h3>
{steps('Model answer', [
    'Per token cross entropy of the test text: H = −(1 ÷ N) log₂ P(w₁ … w<sub>N</sub>).',
    'Then 2<sup>H</sup> = 2<sup>−(1/N) log₂ P</sup> = P<sup>−1/N</sup>.',
    'That is the definition PP = P<sup>−1/N</sup>. A perplexity of k means the model is as unsure as a fair choice among k words.',
    'It is only comparable across models with the same vocabulary and tokenisation, since N and the event space must match.'])}
<h3>Question 15. Show that a generative tagger and a discriminative tagger choose the same sequence, and prove Viterbi is exact.</h3>
{steps('Model answer', [
    'P(T | W) = P(W, T) ÷ P(W), and P(W) is one positive constant for the fixed sentence, so the argmax is unchanged.',
    'Viterbi: under the Markov assumption, the score after time t depends on the past only through the tag at t.',
    'If a best path used a non best prefix into its tag at t, swapping in the best prefix would raise its score, a contradiction.',
    'So one best score per (t, tag) suffices, costing T q² instead of q<sup>T</sup>. It breaks when the model is not Markov, for example with features of the whole tag sequence, which is why CRFs with global features need other inference.'])}
<h3>Question 16. Show that KL divergence is never negative.</h3>
{steps('Model answer', [
    '−KL(P ‖ Q) = Σ P log(Q ÷ P).',
    'log is concave, so by Jensen\'s inequality Σ P log(Q ÷ P) ≤ log Σ P (Q ÷ P) = log Σ Q ≤ log 1 = 0.',
    'So KL ≥ 0, with equality only when Q ÷ P is constant, that is P = Q.',
    'Consequence: cross entropy H(P, Q) = H(P) + KL ≥ H(P). No model beats the true entropy on average.'])}
<h3>Design and critique questions</h3>
<p>A design question such as build a tagger for tweets in Hinglish has no single answer. Structure it as: the data and labels you need, the tagset, the model family and why, how you handle unknown words (suffixes, capitals, subwords), the metric, the error analysis, and the failure cases. A critique question gives an experiment, for example "the new language model has perplexity 40 against 65", and asks what could be wrong: a different vocabulary, a different tokeniser, tuning on the test set, or a test set that overlaps the training data.</p>
{note('In derivations, name each assumption when you use it: Markov, output independence, a fixed vocabulary, independent sentences. Examiners often ask what breaks when one fails.', 'exam')}
{ladder(
    '<p>At school you count words, read small probabilities and explain ideas with examples.</p>',
    '<p>At university you are given a toy corpus or HMM tables and must compute probabilities, perplexity and the best tag sequence by hand, step by step.</p>',
    '<p>In competitive papers you must recognise the right formula quickly, avoid the traps around &lt;s&gt;, &lt;/s&gt;, log bases and smoothing, and round only at the end.</p>',
    '<p>At research universities you derive MLE, perplexity, Viterbi and KL from first principles, state the assumptions and argue when they fail.</p>')}
''', kw=['derivation', 'MLE', 'Lagrange multiplier', 'perplexity derivation', 'cross entropy', 'Bayes', 'Viterbi proof', 'KL nonnegative', 'Jensen', 'design question', 'critique', 'MIT', 'Cambridge', 'Stanford'])

K.lesson('sheet', 'Formula sheet and last minute checks', f'''
{table(['Topic', 'Formula'], [
    ['Zipf', 'f × r ≈ C'],
    ['Surprisal, entropy', 'I(x) = −log₂ p(x), &nbsp; H = −Σ p log₂ p'],
    ['Conditional entropy, chain rule', 'H(Y | X) = H(X, Y) − H(X)'],
    ['Mutual information', 'I(X : Y) = H(X) − H(X | Y), &nbsp; PMI = log₂ P(x, y) ÷ P(x) P(y)'],
    ['KL, cross entropy', 'KL(P ‖ Q) = Σ P log₂(P ÷ Q), &nbsp; H(P, Q) = H(P) + KL'],
    ['Bigram MLE', 'P(w | h) = C(h w) ÷ C(h)'],
    ['Laplace, add-k', '(C(h w) + 1) ÷ (C(h) + V), &nbsp; (C(h w) + k) ÷ (C(h) + kV)'],
    ['Interpolation', 'λ₃ P(w | u v) + λ₂ P(w | v) + λ₁ P(w), λs sum to 1'],
    ['Perplexity', 'P<sup>−1/N</sup> = 2<sup>H</sup>, &nbsp; SRILM ppl = 10<sup>−lp ÷ (words − OOV + sents)</sup>'],
    ['HMM joint', 'π(t₁) b(w₁ | t₁) ∏ a(t<sub>i−1</sub> → t<sub>i</sub>) b(w<sub>i</sub> | t<sub>i</sub>)'],
    ['Viterbi, forward', 'v<sub>t</sub>(j) = max<sub>i</sub> v<sub>t−1</sub>(i) a<sub>ij</sub> b<sub>j</sub>(w<sub>t</sub>), &nbsp; α with Σ'],
    ['Entity F1', '2PR ÷ (P + R) on exact spans'],
    ['PCFG', 'P(tree) = ∏ P(rule)'],
    ['Catalan', 'C<sub>n</sub> = (2n)! ÷ ((n + 1)! n!)']])}
{code('drill')}
<h3>Ten mistakes that cost marks</h3>
<ol>
<li>Counting &lt;s&gt; as a predicted token.</li>
<li>Forgetting &lt;/s&gt; when the question includes it.</li>
<li>Using V without &lt;unk&gt; when the question adds it, or the other way round.</li>
<li>Mixing log base 2 and log base 10.</li>
<li>Rounding in the middle of a long product.</li>
<li>Summing columns instead of rows when checking an HMM.</li>
<li>Forgetting the start probability in the first Viterbi column.</li>
<li>Reporting the best final cell without tracing the back pointers.</li>
<li>Calling a stem a lemma.</li>
<li>Comparing perplexities across different vocabularies.</li>
</ol>
''', kw=['formula sheet', 'common mistakes', 'last minute revision', 'perplexity', 'Laplace', 'Viterbi', 'KL', 'mutual information'])

# ---------------------------------------------------------------- mock quiz
K.quiz('e', 'How many types are in "to be or not to be"?', ['6', '4', '3', '5'], 1,
       'Distinct words.', 'to, be, or, not.')
K.quiz('e', 'A lemmatiser maps "mice" to', ['mic', 'mouse', 'mice', 'mi'], 1,
       'A dictionary form.', 'Lemmas are real dictionary words.')
K.quiz('e', 'The entropy of a fair coin is', ['0 bits', '0.5 bits', '1 bit', '2 bits'], 2,
       'Two equal outcomes.', 'log₂ 2 = 1.')
K.quiz('m', 'In a bigram model, &lt;s&gt; is', ['Predicted', 'Only context', 'Ignored entirely', 'Counted in V'], 1,
       'It is never generated.', 'It conditions the first word but is never a predicted token.')
K.quiz('m', 'Laplace smoothing adds 1 to every bigram count and adds what to the denominator?', ['1', 'N', 'V', 'V²'], 2,
       'One per possible next word.', 'There are V possible next words, each gets 1.')
K.quiz('m', 'A uniform model over 64 words has perplexity', ['6', '8', '64', '4,096'], 2,
       'Uniform over k gives k.', 'H = 6 bits and 2⁶ = 64.')
K.quiz('m', 'Which rows of an HMM must sum to 1?', ['Columns of A', 'Rows of A and rows of B', 'Only π', 'The diagonal'], 1,
       'Outgoing from each state.', 'Each state\'s transitions and emissions are distributions.')
K.quiz('h', 'KL(P ‖ Q) = 0 means', ['P and Q are independent', 'P = Q', 'Q is uniform', 'H(P) = 0'], 1,
       'Gibbs inequality.', 'Equality holds only when the two distributions are the same.')
K.quiz('h', 'Viterbi on 20 words with 12 tags takes about how many steps?', ['240', '2,880', '12²⁰', '20¹²'], 1,
       'T × q².', '20 × 144 = 2,880.')
K.quiz('h', 'Why can perplexities of a word model and a subword model not be compared directly?', ['Different hardware', 'They predict different units, so N and the event space differ', 'Subwords have no perplexity', 'They can'], 1,
       'Per what?', 'Perplexity is per predicted unit, so the units must match.')
K.quiz('x', 'The MLE of a bigram is derived with', ['Gradient descent only', 'A Lagrange multiplier for the sum to 1 constraint', 'Bayes rule', 'Viterbi'], 1,
       'Constrained maximisation.', 'The multiplier comes out as C(h), giving C(h w) ÷ C(h).')
K.quiz('x', 'With k PPs after "V NP", the number of projective attachments is', ['2<sup>k</sup>', 'k!', 'the Catalan number C<sub>k+1</sub>', 'k²'], 2,
       '2, 5, 14, 42 …', 'Catalan growth, which is why chart parsing shares sub trees.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Type token ratio of "the cat sat on the mat"? Three decimals.', '0.833', 'Types ÷ tokens.',
       ['Tokens: 6.', 'Types: 5.', eq('5 ÷ 6 = 0.833')], check=5 / 6, tol=0.0005)
K.calc('e', 'By Zipf\'s law, if rank 1 appears 60,000 times, how often does rank 3 appear?', '20000', 'f × r ≈ C.',
       ['C ≈ 60,000.', 'f = C ÷ r.', eq('60,000 ÷ 3 = 20,000')], check=20000, tol=0.5)
K.calc('e', 'Entropy of (1/2, 1/4, 1/8, 1/8) in bits?', '1.75', 'Sum p × surprisal.',
       ['Surprisals 1, 2, 3, 3.', '0.5 + 0.5 + 0.375 + 0.375.', eq('1.75 bits')], check=1.75, tol=0.001)
K.calc('m', 'Toy corpus: P(I like Sam) with &lt;/s&gt;, bigram MLE. Six decimals.', '0.010667', 'Four bigrams.',
       ['0.2 × 0.4 = 0.08.', '× 1/3 = 0.026667.', eq('× 0.4 = 0.010667')], check=0.2 * 0.4 / 3 * 0.4, tol=0.0000005)
K.calc('m', 'Perplexity of that sentence (N = 4 predicted tokens)? Three decimals.', '3.112', 'P to the power −1/N.',
       ['P = 0.010667.', 'PP = 0.010667<sup>−1/4</sup>.', eq('≈ 3.112')], check=(0.2 * 0.4 / 3 * 0.4) ** -0.25, tol=0.0005)
K.calc('m', 'Laplace P(I | &lt;s&gt;) with C(&lt;s&gt; I) = 1, C(&lt;s&gt;) = 5, V = 6? Four decimals.', '0.1818', '(C + 1) ÷ (C(h) + V).',
       ['Numerator 1 + 1 = 2.', 'Denominator 5 + 6 = 11.', eq('2 ÷ 11 = 0.1818')], check=2 / 11, tol=0.00005)
K.calc('m', 'KL(P ‖ Q) for P = (1/2, 1/2), Q = (3/4, 1/4) in bits? Four decimals.', '0.2075', 'Σ P log₂(P ÷ Q).',
       ['0.5 log₂(2/3) = −0.2925.', '0.5 log₂ 2 = 0.5.', eq('0.5 − 0.2925 = 0.2075')], check=0.20751875, tol=0.00005)
K.calc('m', 'PMI for P(x, y) = 0.01, P(x) = 0.05, P(y) = 0.1, in bits?', '1', 'log₂ of the ratio.',
       ['P(x) P(y) = 0.005.', 'Ratio 0.01 ÷ 0.005 = 2.', eq('log₂ 2 = 1 bit')], check=1, tol=0.001)
K.calc('h', 'Viterbi v₃(V) for they can fish, from v₂(M) = 0.084, a(M → V) = 0.9, b<sub>V</sub>(fish) = 0.7 (the best predecessor)? Five decimals.', '0.05292', 'Best predecessor times emission.',
       ['0.084 × 0.9 = 0.0756.', 'It beats 0.00336 and 0.00756.', eq('0.0756 × 0.7 = 0.05292')], check=0.05292, tol=0.000005)
K.calc('h', 'Posterior of N M V given P(W) = 0.073164? Four decimals.', '0.7233', 'Joint ÷ P(W).',
       ['P(W, N M V) = 0.05292.', '0.05292 ÷ 0.073164.', eq('= 0.7233')], check=0.05292 / 0.073164, tol=0.0001)
K.calc('h', 'Perplexity of a model with cross entropy 9.97 bits per word? Nearest whole number.', '1003', '2<sup>H</sup>.',
       ['PP = 2<sup>9.97</sup>.', '2¹⁰ = 1,024 and 2<sup>−0.03</sup> ≈ 0.9794.', eq('1,024 × 0.9794 ≈ 1,003')], check=2 ** 9.97, tol=0.6)
K.calc('x', 'Cross entropy H(P, Q) for P = (1/2, 1/2), Q = (3/4, 1/4)? Four decimals.', '1.2075', 'H(P) + KL.',
       ['H(P) = 1 bit.', 'KL = 0.2075 bits.', eq('H(P, Q) = 1.2075 bits')], check=1.20751875, tol=0.00005)
K.calc('x', 'Number of possible trigrams over a 20,000 word vocabulary?', '8000000000000', 'V³.',
       ['V = 2 × 10⁴.', 'V³ = 8 × 10¹².', eq('8,000,000,000,000, far more than any corpus can fill')], check=8e12, tol=0.5)
K.calc('x', 'Parses for 5 PPs after "V NP" (Catalan C₆ = 12! ÷ (7! 6!))?', '132', 'Compute the factorials.',
       ['12! = 479,001,600.', '7! × 6! = 5,040 × 720 = 3,628,800.', eq('479,001,600 ÷ 3,628,800 = 132')], check=132, tol=0.01)

T = K.topic(
    slug='exam-revision', topic='exam-revision', kind='revision',
    step=(6, 'Exam revision', 'nlp-revision', 'Revise the whole subject by exam style, from school questions to IIT numericals, NPTEL and GATE style papers, and MIT and Cambridge style derivations.', 'All levels'),
    title='Exam revision: from school to research universities', short='Exam revision', badge='6.1', minutes=60,
    lead='Practise the question shapes of every level with worked answers: counting words, n-gram and perplexity numericals by hand, quick multiple choice tricks, and derivations with their assumptions.',
    desc='Exam patterns by tier, worked questions on tokens and types, Zipf, entropy, stems and lemmas, bigram probability, perplexity, Laplace, Viterbi, PCFG attachment, KL and PMI, derivations of the MLE, perplexity, Viterbi and Gibbs inequality, a formula sheet and common mistakes.',
    summary='Exam style questions from school level to research universities, with worked answers, a formula sheet and a mock quiz.',
    keywords=['exam', 'revision', 'formula sheet', 'mock quiz', 'numericals', 'derivations', 'IIT', 'NPTEL', 'GATE', 'MIT', 'Cambridge', 'Stanford'],
    recap='')
