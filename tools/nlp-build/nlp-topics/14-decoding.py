# NLP section, chapter 4.3: decoding. Source: FoVL lecture 3 slides 111 to 122 (autoregressive generation at inference,
# which words to generate at each step, the issue with greedy decoding on the SLP3 example tree, what is globally optimal,
# beam search with beam size 2, its stopping criterion and finishing up, Holtzman et al. 2020 on degenerate text,
# deterministic against sampling decoders and the quality against diversity trade off).
from cvkit import Kit, fx, fxs, frac, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('beam', r'''
# Greedy against beam search on the SLP3 style tree (log probabilities)
import math
P = {"START": {"a": 0.5, "the": 0.4, "one": 0.1},
     "a": {"cat": 0.4, "dog": 0.3, "mat": 0.3}, "the": {"cat": 0.9, "dog": 0.1}, "one": {"cat": 0.5, "dog": 0.5}}

def beam_search(k):
    beams = [(0.0, ["START"])]
    for step in range(2):
        cand = []
        for score, seq in beams:
            for w, p in P[seq[-1]].items():
                cand.append((score + math.log(p), seq + [w]))
        beams = sorted(cand, key=lambda c: -c[0])[:k]
    return beams

for k in [1, 2, 3]:
    best = beam_search(k)[0]
    print("k =", k, " best:", " ".join(best[1][1:]), " P =", round(math.exp(best[0]), 4))
''')

K.code('sample', r'''
# Temperature, top-k and top-p on next word scores
import math
logits = {"books": 3.0, "laptops": 2.5, "exams": 2.0, "minds": 1.0, "zoo": -1.0, "bananas": -2.0}

def dist(T=1.0, top_k=0, top_p=1.0):
    e = {w: math.exp(s / T) for w, s in logits.items()}
    Z = sum(e.values())
    p = sorted(((w, v / Z) for w, v in e.items()), key=lambda x: -x[1])
    if top_k:
        p = p[:top_k]
    if top_p < 1.0:
        keep, c = [], 0.0
        for w, v in p:
            keep.append((w, v))
            c += v
            if c >= top_p:
                break
        p = keep
    s = sum(v for _, v in p)
    return [(w, round(v / s, 4)) for w, v in p]

print("T = 1  ", dist())
print("T = 0.5", dist(T=0.5))
print("top-k 3", dist(top_k=3))
print("top-p .9", dist(top_p=0.9))
''')

K.lesson('greedy', 'Greedy decoding and its problem', f'''
<p>At inference time the decoder generates one token at a time and feeds it back in. Which word should it pick at each step? The simplest answer is greedy decoding: take the single most probable word, argmax<sub>w</sub> P(w | y<sub>&lt;t</sub>, x), every time.</p>
{fxs(fx('Greedy step', 'ŷ<sub>t</sub> = argmax<sub>w ∈ V</sub> P(w | ŷ<sub>&lt;t</sub>, x)', 'One choice per step, never revisited.', key=True),
     fx('What we really want', 'ŷ = argmax<sub>y</sub> P(y | x) = argmax<sub>y</sub> ∏<sub>t</sub> P(y<sub>t</sub> | y<sub>&lt;t</sub>, x)', 'The best whole sequence, not the best word at each step.', key=True))}
{viz('beam', k=1)}
{steps('The slide question: what will greedy decoding choose?', [
    'First step: a 0.5, the 0.4, one 0.1. Greedy takes "a".',
    'After "a": cat 0.4, dog 0.3, mat 0.3. Greedy takes "cat". Total 0.5 × 0.4 = 0.20.',
    'What is globally optimal? "the cat" scores 0.4 × 0.9 = 0.36, and "one cat" 0.1 × 0.5 = 0.05.',
    eq('Greedy returns "a cat" (0.20), the best sequence is "the cat" (0.36)')])}
<p>The issue with greedy decoding is that it has no way to undo decisions. A word that looks best now can lead to a poor continuation, and a slightly weaker first word can lead to a much better sentence. In translation, greedy decoding of "il a m’ entarté" can commit to "he hit a" and then has nothing sensible to say.</p>
{note('Greedy is fast and often fine, but it is not optimal. Exams ask for an example where greedy fails: show a first choice with a high probability followed by low probabilities, against a lower first choice followed by a high one.', 'exam')}
''', kw=['greedy decoding', 'argmax', 'no undo', 'globally optimal'])

K.lesson('beam', 'Beam search', f'''
<p>Exhaustive search would score every possible sequence: |V|<sup>T</sup> of them, which is far too many. Beam search is the practical middle way. On each step it keeps track of the k most probable partial translations, called hypotheses. k is the beam size, in practice around 5 to 10.</p>
{fxs(fx('Hypothesis score', 'score(y<sub>1</sub>, ..., y<sub>t</sub>) = log P(y<sub>1:t</sub> | x) = ∑<sub>i=1</sub><sup>t</sup> log P(y<sub>i</sub> | y<sub>&lt;i</sub>, x)', 'All scores are negative. Higher is better. Logs turn products into sums.', key=True),
     fx('One beam step', 'expand each of the k hypotheses by every word, keep the top k of the k·|V| candidates', 'k = 1 is greedy decoding.', key=True))}
{viz('beam')}
{code('beam')}
{steps('Beam size 2 on the slide tree (slide 116)', [
    'Step 1: keep the top 2 of {a 0.5, the 0.4, one 0.1}: "a" (log 0.5 = −0.693) and "the" (log 0.4 = −0.916).',
    'Step 2: expand both. a cat −1.609, a dog −1.897, a mat −1.897, the cat −1.022, the dog −3.219.',
    'Keep the top 2: "the cat" (−1.022) and "a cat" (−1.609).',
    eq('Beam search returns "the cat" with P = 0.36, the same as the optimal solution here')])}
{note('Beam search is not guaranteed to find the optimal solution. It is much more efficient than exhaustive search, and a larger k gets closer to the optimum at a higher cost.', 'warn')}
''', kw=['beam search', 'beam size', 'hypotheses', 'log probability', 'exhaustive search'])

K.lesson('finish', 'Stopping, length and cost', f'''
<p>In greedy decoding we stop when the model produces &lt;END&gt;. In beam search different hypotheses can end at different times. When a hypothesis produces &lt;END&gt; it is complete: place it aside and continue exploring the others.</p>
{table(['Stopping criterion (slide 117)', 'Meaning'], [['reach a time step T', 'a preset maximum length'], ['have n completed hypotheses', 'a preset number of finished candidates']])}
<p>Finishing up: pick the completed hypothesis with the best score. One problem: longer hypotheses have lower scores, because every extra word adds another negative log probability. Fix it by normalising by length.</p>
{fxs(fx('Length normalised score', frac('1', 't') + ' ∑<sub>i=1</sub><sup>t</sup> log P(y<sub>i</sub> | y<sub>&lt;i</sub>, x)', 'Average log probability per word, used to pick the final answer.', key=True),
     fx('Cost per step', 'exhaustive: |V|<sup>T</sup> sequences in total, &nbsp; beam: k · |V| candidates per step', 'Beam search is linear in T.'))}
{steps('Why length normalisation matters', [
    'Hypothesis A: 2 words with log probabilities −0.5 and −0.6, total −1.1.',
    'Hypothesis B: 4 words, each −0.4, total −1.6.',
    'Raw totals prefer A (−1.1 > −1.6). Per word: A −0.55, B −0.40.',
    eq('Normalised scores prefer B, the longer and more fluent hypothesis')])}
{steps('How many sequences would exhaustive search score?', [
    '|V| = 10,000 and T = 10.',
    eq('10,000<sup>10</sup> = 10<sup>40</sup> sequences'),
    'Beam search with k = 5 scores 5 × 10,000 = 50,000 candidates per step, 500,000 in total.',
    'That is 2 × 10<sup>34</sup> times fewer than exhaustive search.'])}
''', kw=['stopping criterion', 'END token', 'length normalisation', 'search cost'])

K.lesson('sampling', 'Sampling: temperature, top-k and top-p', f'''
<p>Greedy and beam search are deterministic: the same input always gives the same output. For open ended generation such as stories or chat, that leads to bland and repetitive text. Holtzman et al. (2020) showed that beam search on open ended text often loops, repeating the same phrase. Sampling decoders bring in some randomness instead.</p>
{fxs(fx('Pure sampling', 'y<sub>t</sub> ~ P(· | y<sub>&lt;t</sub>, x)', 'Draw the next word at random from the full distribution.'),
     fx('Temperature', 'P<sub>T</sub>(w) = ' + frac('exp(s<sub>w</sub> ÷ T)', '∑<sub>w′</sub> exp(s<sub>w′</sub> ÷ T)'), 'T < 1 sharpens (more greedy), T > 1 flattens (more diverse). T → 0 is greedy.', key=True),
     fx('Top-k', 'sample only from the k most probable words, renormalised', 'A fixed number of candidates.', key=True),
     fx('Top-p (nucleus)', 'sample from the smallest set V<sub>p</sub> with ∑<sub>w ∈ V<sub>p</sub></sub> P(w) ≥ p', 'The number of candidates adapts to how sure the model is.', key=True))}
{viz('sampling')}
{code('sample')}
{steps('Top-p with p = 0.9 on "the students opened their ___"', [
    'Probabilities at T = 1: books 0.4684, laptops 0.2841, exams 0.1723, minds 0.0634, zoo 0.0086, bananas 0.0032.',
    'Running sums: 0.4684, 0.7525, 0.9248. The third word passes 0.9.',
    eq('Nucleus = {books, laptops, exams}'),
    'Renormalised: books 0.5065, laptops 0.3072, exams 0.1863. "zoo" and "bananas" can no longer be drawn.'])}
{table(['Decoder', 'Deterministic', 'Quality', 'Diversity', 'Typical use'], [['greedy', 'yes', 'good for short outputs', 'none', 'quick baselines'], ['beam search', 'yes', 'high for translation and summaries', 'low, can repeat', 'machine translation'], ['pure sampling', 'no', 'can drift into nonsense', 'high', 'rarely used alone'], ['temperature, top-k, top-p', 'no', 'good balance', 'tunable', 'chatbots, story writing']])}
{note('This is the quality against diversity trade off. Lower T, smaller k or smaller p give safer and more repetitive text. Higher values give more varied and riskier text.', 'tip')}
''', kw=['sampling', 'temperature', 'top-k', 'top-p', 'nucleus sampling', 'quality vs diversity'])

K.lesson('choose', 'Choosing a decoder', f'''
<p>The decoder is chosen at inference time and does not change the trained model. The same NMT network can be decoded greedily for speed, with beam search for quality, or with sampling for variety.</p>
{scene('one model, three products', '<p>A company trains one model that writes product descriptions. For the legal summary on the checkout page they use beam search with k = 4: the most probable, stable wording every time. For marketing emails they use top-p = 0.9 at T = 0.8, so every customer gets a slightly different but sensible text. For a brainstorming tool they raise T to 1.2 and accept some odd ideas in exchange for more surprising ones.</p>')}
{steps('Temperature by hand', [
    'Two words with scores 2 and 1.',
    'T = 1: e² ÷ (e² + e¹) = 7.389 ÷ 10.107 = 0.731.',
    'T = 0.5: scores become 4 and 2, so e⁴ ÷ (e⁴ + e²) = 0.881.',
    eq('T = 2: scores 1 and 0.5, weight 0.622. Lower T sharpens, higher T flattens')])}
{ladder(
    '<p>To write a sentence, the model picks one word at a time. It can always pick the top word, keep a few good options open (beam search), or pick at random from the likely words to be more creative.</p>',
    '<p>Greedy takes argmax each step. Beam search keeps the top k hypotheses by summed log probability and normalises by length at the end. Sampling uses temperature, top-k or top-p to trade quality for diversity.</p>',
    '<p>Beam search approximates the MAP sequence. Its search error can be small while the MAP itself is poor: Stahlberg and Byrne (2019) found the exact MAP translation is often the empty sentence, which is why length normalisation and moderate beams work best.</p>',
    '<p>Modern LLMs combine temperature with top-p or min-p sampling, use repetition penalties, and add speculative decoding (a small draft model proposes tokens that the large model verifies) to speed up generation without changing the output distribution.</p>')}
''', kw=['choosing a decoder', 'temperature', 'MAP decoding', 'speculative decoding'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Greedy decoding picks', ['a random word', 'the most probable word at each step', 'the longest word', 'k words'], 1, 'argmax.', 'One best word per step.')
K.quiz('e', 'Beam search with k = 1 is the same as', ['sampling', 'greedy decoding', 'exhaustive search', 'top-p'], 1, 'One hypothesis.', 'Keeping only the best is greedy.')
K.quiz('e', 'A temperature below 1 makes the distribution', ['flatter', 'sharper', 'uniform', 'negative'], 1, 'Divide by a small T.', 'Differences grow, the top word dominates.')
K.quiz('e', 'Greedy and beam search are', ['random', 'deterministic', 'unsupervised', 'trained'], 1, 'Slide 121.', 'Same input, same output.')
K.quiz('m', 'On the slide tree greedy returns "a cat" (0.20). The best sequence is', ['a dog', 'the cat', 'one cat', 'a mat'], 1, '0.4 × 0.9.', '"the cat" with 0.36.')
K.quiz('m', 'Beam search scores hypotheses with', ['the product of probabilities without logs', 'the sum of log probabilities', 'the number of words', 'the attention weights'], 1, 'Slide 115.', 'Logs avoid tiny numbers.')
K.quiz('m', 'Why normalise beam scores by length?', ['to speed up search', 'longer hypotheses get lower raw scores', 'to make scores positive', 'to remove END'], 1, 'More negative terms.', 'Divide by t to compare fairly.')
K.quiz('m', 'Top-p = 0.9 keeps', ['the 9 best words', 'the smallest set of words whose probabilities add to at least 0.9', 'words with probability above 0.9', 'all words'], 1, 'Nucleus.', 'Its size adapts to the distribution.')
K.quiz('m', 'When a hypothesis produces &lt;END&gt; in beam search', ['search stops at once', 'it is set aside as complete and search continues', 'it is deleted', 'k grows'], 1, 'Slide 118.', 'Others may still finish with better scores.')
K.quiz('h', 'Beam search is guaranteed to find the most probable sequence', ['yes, always', 'no, but it is much more efficient than exhaustive search', 'only for k = 1', 'only with sampling'], 1, 'Slide 115.', 'It is a heuristic search.')
K.quiz('h', 'Exhaustive search over |V| = 10,000 and T = 10 scores', ['100,000 sequences', '10<sup>40</sup> sequences', '10,000 sequences', '10<sup>10</sup> sequences'], 1, '|V|<sup>T</sup>.', '10<sup>4×10</sup>.')
K.quiz('h', 'Holtzman et al. (2020) found that for open ended text beam search tends to', ['produce random words', 'produce repetitive, degenerate text', 'be too slow', 'fail on short prompts'], 1, 'The curious case of neural text degeneration.', 'This motivated nucleus sampling.')
K.quiz('x', 'Top-k with k = 3 versus top-p with p = 0.9 when the model is very sure (top word 0.95):', ['both keep 3 words', 'top-k keeps 3, top-p keeps only 1', 'top-p keeps 3', 'both keep 1'], 1, 'Adaptive size.', '0.95 ≥ 0.9 already.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Slide tree: probability of the greedy output "a cat".', '0.2', '0.5 × 0.4.',
       ['First step: a 0.5.', 'Second: cat 0.4.', eq('0.20')], check=0.2, tol=1e-9)
K.calc('e', 'Slide tree: probability of "the cat".', '0.36', '0.4 × 0.9.',
       ['First: the 0.4.', 'Second: cat 0.9.', eq('0.36')], check=0.36, tol=1e-9)
K.calc('e', 'Log score of "the cat", four decimals.', '-1.0217', 'ln 0.4 + ln 0.9.',
       ['ln 0.4 = −0.9163.', 'ln 0.9 = −0.1054.', eq('−1.0217')], check=-1.0216512475319812, tol=5e-4)
K.calc('m', 'Length normalised score of "the cat", four decimals.', '-0.5108', 'Divide by 2.',
       ['Total −1.0217.', '2 words.', eq('−0.5108')], check=-0.5108256237659906, tol=5e-4)
K.calc('m', 'Two words with scores 2 and 1 at temperature 1. Probability of the first, three decimals.', '0.731', 'Softmax.',
       ['e² = 7.389, e¹ = 2.718.', 'Sum 10.107.', eq('0.731')], check=0.7310585786300049, tol=5e-4)
K.calc('m', 'Same scores at T = 0.5. Probability of the first, three decimals.', '0.881', 'Scores become 4 and 2.',
       ['e⁴ = 54.598, e² = 7.389.', 'Sum 61.987.', eq('0.881')], check=0.8807970779778823, tol=5e-4)
K.calc('m', 'Next word probabilities 0.4684, 0.2841, 0.1723, 0.0634, ... How many words does top-p = 0.9 keep?', '3', 'Running sum until ≥ 0.9.',
       ['0.4684, then 0.7525.', 'Then 0.9248 ≥ 0.9.', eq('3 words')], check=3, tol=1e-9)
K.calc('m', 'Top-k = 3 on the same distribution. Renormalised probability of the top word, four decimals.', '0.5065', '0.4684 ÷ (0.4684 + 0.2841 + 0.1723).',
       ['Sum of top 3 = 0.9248.', '0.4684 ÷ 0.9248.', eq('0.5065')], check=0.4684 / 0.9248, tol=5e-4)
K.calc('h', 'Beam k = 5, |V| = 10,000, T = 10. Total candidates scored.', '500000', 'k |V| T.',
       ['Per step: 5 × 10,000 = 50,000.', '10 steps.', eq('500,000')], check=500000, tol=1e-9)
K.calc('h', 'Hypothesis A has log probabilities −0.5, −0.6. B has four of −0.4. Normalised score of B minus that of A.', '0.15', '−0.40 − (−0.55).',
       ['A: −1.1 ÷ 2 = −0.55.', 'B: −1.6 ÷ 4 = −0.40.', eq('0.15 in favour of B')], check=0.15, tol=1e-9)
K.calc('h', 'With scores 3.0, 2.5, 2.0, 1.0, −1.0, −2.0 at T = 1, probability of "books" (score 3.0), four decimals.', '0.4684', 'Softmax.',
       ['Exponentials 20.09, 12.18, 7.389, 2.718, 0.368, 0.135.', 'Sum 42.88.', eq('20.09 ÷ 42.88 = 0.4684')], check=0.4684, tol=5e-4)
K.calc('x', 'Number of possible sequences of length 10 over a 10,000 word vocabulary, as a power of 10. Give the exponent.', '40', '(10<sup>4</sup>)<sup>10</sup>.',
       ['|V| = 10<sup>4</sup>.', 'Raise to T = 10.', eq('10<sup>40</sup>, exponent 40')], check=40, tol=1e-9)

# ---------------------------------------------------------------- assignments
K.assign('temp', 'e', 'Softmax with temperature',
         '<p>Write <code>softmax_t(scores, T)</code> that returns softmax(scores ÷ T) as a list rounded to 4 decimals.</p>',
         '''
import math

def softmax_t(scores, T):
    pass
''', [('softmax_t([2, 1], 1)', [0.7311, 0.2689]), ('softmax_t([2, 1], 0.5)', [0.8808, 0.1192]), ('softmax_t([0, 0, 0, 0], 3)', [0.25, 0.25, 0.25, 0.25])],
         '''
import math

def softmax_t(scores, T):
    z = [s / T for s in scores]
    m = max(z)
    e = [math.exp(v - m) for v in z]
    S = sum(e)
    return [round(v / S, 4) for v in e]
''', 'Divide by T before the softmax.', '<p>Equal scores stay uniform at every temperature.</p>')
K.assign('nucleus', 'm', 'Top-p filtering',
         '<p>Write <code>top_p(probs, p)</code> where probs is a dict word to probability. Sort by probability, keep the smallest prefix whose sum is at least p, renormalise and return a dict rounded to 4 decimals.</p>',
         '''
def top_p(probs, p):
    pass
''', [('top_p({"books": 0.4684, "laptops": 0.2841, "exams": 0.1723, "minds": 0.0634, "zoo": 0.0086, "bananas": 0.0032}, 0.9)', {'books': 0.5065, 'laptops': 0.3072, 'exams': 0.1863}),
      ('top_p({"a": 0.95, "b": 0.05}, 0.9)', {'a': 1.0}), ('top_p({"a": 0.5, "b": 0.5}, 1.0)', {'a': 0.5, 'b': 0.5})],
         '''
def top_p(probs, p):
    items = sorted(probs.items(), key=lambda kv: -kv[1])
    keep, c = [], 0.0
    for w, v in items:
        keep.append((w, v))
        c += v
        if c >= p - 1e-12:
            break
    s = sum(v for _, v in keep)
    return {w: round(v / s, 4) for w, v in keep}
''', 'Add probabilities from the top until the sum reaches p.', '<p>When the top word alone passes p, the nucleus has one word and sampling becomes greedy.</p>')
K.assign('beamk', 'h', 'Beam search on a tree',
         '<p>Write <code>beam(tree, start, steps, k)</code>. tree maps a word to a dict of next words and probabilities (look up only the last word). Run beam search for the given number of steps with summed natural log probabilities, keeping the top k. Return (best words without start, probability rounded to 4 decimals).</p>',
         '''
import math

def beam(tree, start, steps, k):
    pass
''', [('beam({"S": {"a": 0.5, "the": 0.4, "one": 0.1}, "a": {"cat": 0.4, "dog": 0.3, "mat": 0.3}, "the": {"cat": 0.9, "dog": 0.1}, "one": {"cat": 0.5, "dog": 0.5}}, "S", 2, 1)', (['a', 'cat'], 0.2)),
      ('beam({"S": {"a": 0.5, "the": 0.4, "one": 0.1}, "a": {"cat": 0.4, "dog": 0.3, "mat": 0.3}, "the": {"cat": 0.9, "dog": 0.1}, "one": {"cat": 0.5, "dog": 0.5}}, "S", 2, 2)', (['the', 'cat'], 0.36)),
      ('beam({"S": {"x": 1.0}, "x": {"y": 1.0}}, "S", 2, 3)', (['x', 'y'], 1.0))],
         '''
import math

def beam(tree, start, steps, k):
    beams = [(0.0, [start])]
    for _ in range(steps):
        cand = []
        for sc, seq in beams:
            for w, p in tree.get(seq[-1], {}).items():
                cand.append((sc + math.log(p), seq + [w]))
        beams = sorted(cand, key=lambda c: -c[0])[:k]
    sc, seq = beams[0]
    return (seq[1:], round(math.exp(sc), 4))
''', 'Expand every hypothesis, then keep the k best by log score.', '<p>k = 1 reproduces the greedy answer "a cat", k = 2 finds "the cat".</p>')

K.must('Greedy', 'Pick argmax at each step. Fast, cannot undo decisions. Slide tree: greedy "a cat" 0.20, optimal "the cat" 0.36.')
K.must('Beam search', 'Keep the k best hypotheses by ∑ log P, expand each, keep the top k again. k = 1 is greedy. Not guaranteed optimal, far cheaper than |V|<sup>T</sup>.')
K.must('Stopping and length', 'A hypothesis that emits &lt;END&gt; is set aside. Stop at time T or after n complete hypotheses. Pick the best by (1 ÷ t) ∑ log P.')
K.must('Sampling', 'Temperature softmax(s ÷ T): low T sharp, high T flat. Top-k keeps k words, top-p the smallest set with mass ≥ p. Adds diversity.')
K.must('Trade off', 'Greedy and beam are deterministic and can repeat in open ended text. Sampling trades some quality for diversity.')

T = K.topic(
    slug='decoding', topic='nn-decoding', step=(4, 'Translation, attention and decoding', 'nn-seq2seq', 'Translate and generate text: the encoder-decoder model as a conditional language model, the bottleneck, attention with its worked problem, and greedy, beam and sampling decoders.', 'Masters'),
    title='Decoding: greedy, beam search and sampling', short='Decoding', badge='4.3', minutes=40, added='2026-11-01',
    lead='Choose the words a trained model actually writes: greedy decoding and why it fails, beam search with its stopping rules and length normalisation, and temperature, top-k and top-p sampling.',
    desc='Autoregressive generation at inference, greedy decoding on the slide tree and why it cannot undo decisions, beam search with log probability scores and beam size 2, stopping criteria and length normalisation, the cost of exhaustive search, deterministic against sampling decoders, temperature, top-k and nucleus sampling and the quality against diversity trade off.',
    summary='Greedy and beam search, stopping and length normalisation, and temperature, top-k and top-p sampling.',
    keywords=['decoding', 'greedy', 'beam search', 'length normalisation', 'temperature', 'top-k', 'top-p'],
    recap='<p>A trained model gives next word probabilities, and the decoder decides what to write. Greedy decoding is fast but cannot undo choices, beam search keeps k hypotheses and usually finds better sequences, and sampling with temperature, top-k or top-p trades some quality for diversity.</p>')
