# Chapter 5.3: decoding with Viterbi and the forward algorithm. Source: lecture 9 (POS deck slides 25 to 30: the
# decoding objective, q to the power T, the Viterbi idea "use the best path until here"), the class questions on ties and
# on trigram HMMs, the notes' three tag "they can fish" model, and problems G6 to G10 and H8.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

HMM = r'''tags = ["N", "M", "V"]
pi = {"N": 0.7, "M": 0.1, "V": 0.2}
A = {"N": {"N": 0.2, "M": 0.4, "V": 0.4}, "M": {"N": 0.1, "M": 0.0, "V": 0.9}, "V": {"N": 0.6, "M": 0.1, "V": 0.3}}
B = {"N": {"they": 0.3, "can": 0.2, "fish": 0.5}, "M": {"can": 1.0}, "V": {"can": 0.3, "fish": 0.7}}
'''

K.code('brute', r'''
# Brute force: score every one of the 3 ** 3 = 27 tag sequences
from itertools import product
''' + HMM + r'''
words = ["they", "can", "fish"]
scores = []
for T in product(tags, repeat=3):
    p = pi[T[0]] * B[T[0]].get(words[0], 0)
    for i in (1, 2):
        p *= A[T[i - 1]][T[i]] * B[T[i]].get(words[i], 0)
    if p > 0:
        scores.append((round(p, 6), " ".join(T)))
print(len(scores), "of 27 sequences are non zero")
print(sorted(scores, reverse=True))
''')

K.code('viterbi', r'''
# Viterbi: one best score and one back pointer per (word, tag) cell
''' + HMM + r'''
words = ["they", "can", "fish"]
v = [{t: pi[t] * B[t].get(words[0], 0) for t in tags}]
back = [{}]
for w in words[1:]:
    col, bp = {}, {}
    for t in tags:
        best = max(tags, key=lambda s: v[-1][s] * A[s][t])
        col[t] = v[-1][best] * A[best][t] * B[t].get(w, 0)
        bp[t] = best
    v.append(col)
    back.append(bp)
last = max(tags, key=lambda t: v[-1][t])
path = [last]
for bp in reversed(back[1:]):
    path.insert(0, bp[path[0]])
print("columns:", [{t: round(x, 5) for t, x in c.items()} for c in v])
print("best path:", path, " probability:", round(v[-1][last], 5))
''')

K.code('forward', r'''
# Forward: the same table with sum in place of max gives P(words)
''' + HMM + r'''
words = ["they", "can", "fish"]
alpha = {t: pi[t] * B[t].get(words[0], 0) for t in tags}
for w in words[1:]:
    alpha = {t: sum(alpha[s] * A[s][t] for s in tags) * B[t].get(w, 0) for t in tags}
pw = sum(alpha.values())
print("last column:", {t: round(x, 6) for t, x in alpha.items()})
print("P(they can fish) =", round(pw, 6))
print("P(N M V | words) =", round(0.05292 / pw, 4))
''')

K.code('size', r'''
# Paths that brute force must score against Viterbi steps
for q, T in [(2, 4), (12, 10), (45, 25), (87, 10)]:
    print("q =", q, " T =", T, "  sequences:", "%.3e" % q ** T, "  Viterbi steps:", T * q * q)
''')

K.lesson('brute', 'Why brute force fails', f'''
<p>Decoding means finding the tag sequence with the highest score. With q tags and T words, every position can take any tag, so there are q<sup>T</sup> sequences. For two words and two tags that is 4, fine by hand. For a 25 word newspaper sentence with the 45 Penn Treebank tags it is about 2 × 10⁴¹. A computer scoring a billion sequences a second would need far longer than the age of the universe.</p>
{fxs(fx('The decoding objective', '<i>T̂</i> = argmax<sub><i>t</i>₁ … <i>t<sub>n</sub></i></sub> ∏<sub><i>i</i></sub> P(<i>w<sub>i</sub></i> | <i>t<sub>i</sub></i>) · P(<i>t<sub>i</sub></i> | <i>t</i><sub><i>i</i>−1</sub>)', 'The first factor is the emission, the second the transition. P(t₁ | t₀) means the start probability π(t₁).', key=True))}
{viz('searchsize')}
{table(['q (tags)', 'T (words)', 'Sequences q<sup>T</sup>', 'Viterbi steps T × q²'], [
    ['2', '4', '16', '16'],
    ['12', '10', '6.19 × 10¹⁰', '1,440'],
    ['45', '25', '2.14 × 10⁴¹', '50,625'],
    ['87', '10', '2.48 × 10¹⁹', '75,690']])}
{code('size')}
{code('brute')}
<p>Brute force on "they can fish" scores 27 sequences and finds only six with a non zero score. Most of the work is wasted on paths that died at the first impossible emission.</p>
''', kw=['brute force', 'search space', 'q to the T', 'exponential', 'decoding objective', 'argmax', 'Penn Treebank 45 tags', 'Brown 87 tags'])

K.lesson('viterbi', 'The Viterbi algorithm', f'''
<p>The professor\'s summary: "If you have reached here, there is a best path until here. When you go further, use that best path. Do not start from scratch again." A road trip works the same way. To find the fastest route from Delhi to Chennai through Nagpur, you only need the fastest route to Nagpur. Any slower way of reaching Nagpur can be thrown away, since the rest of the trip does not care how you got there.</p>
{fxs(
    fx('Viterbi recursion', '<i>v</i><sub>1</sub>(<i>j</i>) = π<sub><i>j</i></sub> <i>b<sub>j</sub></i>(<i>w</i>₁) &nbsp; &nbsp; <i>v<sub>t</sub></i>(<i>j</i>) = max<sub><i>i</i></sub> <i>v</i><sub><i>t</i>−1</sub>(<i>i</i>) · <i>a<sub>ij</sub></i> · <i>b<sub>j</sub></i>(<i>w<sub>t</sub></i>)', '<i>v<sub>t</sub></i>(<i>j</i>) is the probability of the best tag path that ends in tag <i>j</i> after reading <i>t</i> words. Store the winning <i>i</i> as a back pointer.', key=True),
    fx('Cost', 'O(<i>T</i> · <i>q</i>²) time, &nbsp; O(<i>T</i> · <i>q</i>) memory', 'For each of T positions and q tags, compare q predecessors.'))}
<p>The model has three tags, N (noun), M (modal) and V (verb), and "they can fish" has two readings: they are able to fish (N M V) and they put fish in cans (N V N).</p>
{table(['π', 'N 0.7', 'M 0.1', 'V 0.2'], [])}
{table(['A (from ↓, to →)', 'N', 'M', 'V'], [['N', '0.2', '0.4', '0.4'], ['M', '0.1', '0', '0.9'], ['V', '0.6', '0.1', '0.3']])}
{table(['B', 'they', 'can', 'fish'], [['N', '0.3', '0.2', '0.5'], ['M', '0', '1.0', '0'], ['V', '0', '0.3', '0.7']])}
{viz('viterbi')}
{steps('Viterbi for "they can fish"', [
    'they: v₁(N) = 0.7 × 0.3 = 0.21. v₁(M) = 0.1 × 0 = 0. v₁(V) = 0.2 × 0 = 0.',
    'can, N: 0.21 × 0.2 = 0.042, × b<sub>N</sub>(can) 0.2 = 0.0084. Back pointer N.',
    'can, M: 0.21 × 0.4 = 0.084, × 1.0 = 0.084. Back pointer N.',
    'can, V: 0.21 × 0.4 = 0.084, × 0.3 = 0.0252. Back pointer N.',
    'fish, N: candidates 0.0084 × 0.2 = 0.00168, 0.084 × 0.1 = 0.0084, 0.0252 × 0.6 = 0.01512. Best from V, × 0.5 = 0.00756.',
    'fish, M: b<sub>M</sub>(fish) = 0, so 0.',
    'fish, V: candidates 0.0084 × 0.4 = 0.00336, 0.084 × 0.9 = 0.0756, 0.0252 × 0.3 = 0.00756. Best from M, × 0.7 = 0.05292.',
    'The largest final cell is V with 0.05292. Follow the back pointers: V ← M ← N.',
    eq('they/N can/M fish/V, P = 0.05292')])}
{code('viterbi')}
{deep('Proof that keeping one path per cell is safe', '<p>Take a best complete path whose tag at time t is j. Its score splits into [score of its first t steps] × [score of the rest]. Under the Markov assumption the rest depends on the past only through j.</p><p>Suppose its first t steps were not the best path into j. Swap them for the best one. The rest factor is unchanged and the first factor grows, so the total grows. That contradicts the path being best. So the best overall path always runs through the best partial path into each of its cells, and storing one number and one back pointer per cell loses nothing. This is Bellman\'s principle of optimality.</p>')}
{note('Exam recipe. 1: write π, A and B as tables and check the rows. 2: if T ≤ 3 and q ≤ 2, enumerating all paths is fine, show every product. 3: otherwise fill a q × T table column by column, writing the winning predecessor in each cell. 4: back trace from the best last cell. 5: state the tag sequence and its probability. Strike out zero emissions first.', 'exam')}
''', kw=['Viterbi', 'dynamic programming', 'trellis', 'back pointer', 'principle of optimality', 'Bellman', 'they can fish', 'recursion', 'exam recipe'])

K.lesson('forward', 'The forward algorithm and confidence', f'''
<p>Replace max with a sum and the same table answers a different question: how likely is the sentence itself, adding up every way the tags could have produced it? This turns the HMM into a language model.</p>
{fxs(
    fx('Forward recursion', 'α<sub>1</sub>(<i>j</i>) = π<sub><i>j</i></sub> <i>b<sub>j</sub></i>(<i>w</i>₁) &nbsp; &nbsp; α<sub><i>t</i></sub>(<i>j</i>) = Σ<sub><i>i</i></sub> α<sub><i>t</i>−1</sub>(<i>i</i>) · <i>a<sub>ij</sub></i> · <i>b<sub>j</sub></i>(<i>w<sub>t</sub></i>)', 'α<sub><i>t</i></sub>(<i>j</i>) is the total probability of the first t words with tag j at position t.', key=True),
    fx('Sentence probability and posterior', 'P(<i>W</i>) = Σ<sub><i>j</i></sub> α<sub><i>T</i></sub>(<i>j</i>) &nbsp; &nbsp; P(<i>T</i> | <i>W</i>) = ' + frac('P(<i>W</i>, <i>T</i>)', 'P(<i>W</i>)'), 'The posterior says how sure the model is of one tagging.'))}
{steps('Problem G9: P(they can fish)', [
    'α₁: N 0.21, M 0, V 0, as in Viterbi.',
    'α₂: only N is alive at t = 1, so sums equal maxima here. N 0.0084, M 0.084, V 0.0252.',
    'α₃(N) = (0.0084 × 0.2 + 0.084 × 0.1 + 0.0252 × 0.6) × 0.5 = (0.00168 + 0.0084 + 0.01512) × 0.5 = 0.0126.',
    'α₃(V) = (0.0084 × 0.4 + 0.084 × 0.9 + 0.0252 × 0.3) × 0.7 = (0.00336 + 0.0756 + 0.00756) × 0.7 = 0.060564. α₃(M) = 0.',
    eq('P(W) = 0.0126 + 0.060564 = 0.073164'),
    eq('P(N M V | W) = 0.05292 ÷ 0.073164 = 0.7233')])}
{code('forward')}
<h3>Problem G10: every non zero path</h3>
{table(['Tags', 'P(W, T)', 'P(T | W)'], [
    ['N M V', '0.052920', '0.7233'], ['N V N', '0.007560', '0.1033'], ['N V V', '0.005292', '0.0723'],
    ['N M N', '0.004200', '0.0574'], ['N N V', '0.002352', '0.0321'], ['N N N', '0.000840', '0.0115']])}
<p>The posteriors add up to 1, and the order is the same in both columns, since every row was divided by the same P(W). Counting multiplications: brute force uses 27 × 5 = 135, Viterbi uses 3 + 18 + 18 = 39. The gap grows exponentially with length.</p>
{deep('Posterior decoding and forward backward', '<p>A backward pass β<sub>t</sub>(i) = Σ<sub>j</sub> a<sub>ij</sub> b<sub>j</sub>(w<sub>t+1</sub>) β<sub>t+1</sub>(j) gives the probability of the rest of the sentence. Then P(t<sub>i</sub> = j | W) = α<sub>i</sub>(j) β<sub>i</sub>(j) ÷ P(W) for every word separately. Picking the best tag per word maximises the expected number of correct tags, while Viterbi maximises the chance that the whole sequence is right. The two can disagree. The same α and β give the soft counts used by Baum-Welch.</p>')}
''', kw=['forward algorithm', 'sum instead of max', 'sentence probability', 'posterior', 'confidence', 'forward backward', 'posterior decoding', 'G9', 'G10'])

K.lesson('beyond', 'Ties, trigrams and real taggers', f'''
<h3>What if two paths tie?</h3>
<p>A student asked what happens if two sequences both score 0.45. The professor: "Very nice question. Then you need a tie breaking rule. The tagger may return either one. If you really want, you can write code that emits both." In practice exact ties are rare, since scores are products of many estimated numbers. Python\'s max keeps the first maximum it meets, so the order of the tag list decides. Principled options are the k best list (k best Viterbi) or per word posteriors from forward backward.</p>
<h3>Going to a trigram HMM</h3>
{fxs(fx('Second order HMM', 'P(<i>t<sub>i</sub></i> | <i>t</i><sub><i>i</i>−2</sub>, <i>t</i><sub><i>i</i>−1</sub>) &nbsp; &nbsp; cost O(<i>T</i> · <i>q</i>³)', 'Viterbi now runs over pairs of tags. There are q³ transition parameters instead of q², so sparsity grows and interpolation is needed, exactly as for trigram language models.'))}
<p>The TnT tagger (Brants 2000) is a trigram HMM with interpolated smoothing and a suffix model for unknown words. It reaches about 96.7% on the Penn Treebank. The professor\'s warning when students asked for a trigram: "You can take it further, but you have to make sure the probabilities still sum to one."</p>
<h3>British Left Waffles decided by an HMM</h3>
<p>Problem H8 gives practice tables (they are invented for the exercise, and so are the starting values for V and P in the animation). Load the H8 preset in the trellis above. The middle factors decide it: N N V P gives 4.8 × 10⁻⁷ and N V N P gives 6.0 × 10⁻⁶. With these numbers the tagger reads "British [people] left waffles", 12.5 times ahead, because left is commoner as a verb and waffles as a noun. Only context beyond the headline would favour the political reading.</p>
{scene('voice assistant transcripts', '<p>A speech recogniser hears "I scream" or "ice cream". Underneath, it runs the same Viterbi search over a much larger hidden state graph: sounds as hidden states, audio frames as observations. Without dynamic programming, real time speech recognition would be impossible. The posterior from the forward pass also tells the assistant when it is unsure and should ask again.</p>')}
{ladder(
    '<p>Fill a table one word at a time. In each box keep only the best way to get there and an arrow back. At the end, follow the arrows.</p>',
    '<p>v<sub>t</sub>(j) = max<sub>i</sub> v<sub>t−1</sub>(i) a<sub>ij</sub> b<sub>j</sub>(w<sub>t</sub>). Replace max with sum for the forward algorithm and P(W). Cost T q² instead of q<sup>T</sup>.</p>',
    '<p>Viterbi is max product dynamic programming on a chain. Its correctness is the principle of optimality under the Markov assumption. In log space it is a shortest path problem. Forward backward computes marginals, k best Viterbi gives ranked lists, and beam search prunes the trellis for large q.</p>',
    '<p>The same semiring view (max product, sum product) covers CKY parsing, CRF inference and belief propagation on trees. Modern neural taggers still use Viterbi in their CRF output layer, and constrained decoding of language models reuses the same trellis ideas.</p>')}
''', kw=['tie breaking', 'k best', 'trigram HMM', 'TnT', 'second order', 'British Left Waffles', 'H8', 'speech recognition', 'semiring'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'With 3 tags and 4 words, brute force scores how many sequences?', ['12', '64', '81', '4'], 2,
       'q to the power T.', '3⁴ = 81.')
K.quiz('e', 'Each Viterbi cell stores', ['Every path into it', 'The best score into it and a back pointer', 'The word count', 'Only the emission'], 1,
       'One number and one arrow.', 'Keeping only the best path into each cell is what makes it fast.')
K.quiz('e', 'Viterbi for an HMM costs about', ['q<sup>T</sup>', 'T × q²', 'T²', 'q'], 1,
       'For each position and tag, compare q predecessors.', 'T positions × q tags × q predecessors.')
K.quiz('m', 'The forward algorithm differs from Viterbi by', ['Using a trigram', 'Summing over predecessors instead of taking the max', 'Running right to left', 'Ignoring emissions'], 1,
       'Same table.', 'Sum gives the total probability, max gives the best path.')
K.quiz('m', 'After filling the last column, Viterbi', ['Returns the column sum', 'Takes the best final cell and follows back pointers', 'Restarts', 'Picks the best tag per word'], 1,
       'How is the path recovered?', 'The back pointers trace the best path backwards.')
K.quiz('m', 'In "they can fish", the reading "they put fish in cans" is', ['N M V', 'N V N', 'N N N', 'V V V'], 1,
       'Can is the verb.', 'they/N can/V fish/N.')
K.quiz('m', 'Why is keeping only the best path into each cell safe?', ['Ties never happen', 'The future depends on the past only through the current tag', 'Emissions are small', 'Paths are short'], 1,
       'Markov assumption.', 'Swapping in a better prefix can only increase the total, so a non best prefix is never needed.')
K.quiz('m', 'P(N M V | they can fish) = 0.7233 means', ['72% of tokens are nouns', 'The model gives 72% of the sentence\'s probability to this tagging', 'Accuracy is 72%', 'The path is wrong 72% of the time'], 1,
       'Posterior.', 'It is P(W, T) ÷ P(W), the model\'s confidence in that sequence.')
K.quiz('h', 'Two sequences tie exactly. A Python tagger using max will', ['Crash', 'Return the first one it meets in its tag order', 'Return both', 'Average them'], 1,
       'How does max treat ties?', 'max keeps the first maximum, so the tag order decides.')
K.quiz('h', 'A trigram HMM tagger runs Viterbi in', ['O(T q)', 'O(T q²)', 'O(T q³)', 'O(q<sup>T</sup>)'], 2,
       'States become tag pairs.', 'q² pair states, each with q predecessors.')
K.quiz('h', 'Picking the best tag for each word from posteriors', ['Always equals Viterbi', 'Maximises expected correct tags and can differ from Viterbi', 'Is impossible', 'Needs no forward pass'], 1,
       'Per word against whole sequence.', 'It optimises a different goal and can even produce a sequence with probability 0.')
K.quiz('x', 'In log space Viterbi becomes', ['A sorting problem', 'A shortest (or longest) path problem on a graph', 'Matrix inversion', 'Gradient descent'], 1,
       'Logs turn products into sums.', 'Maximising a sum of log weights along a path is a longest path in a DAG, or shortest with negated logs.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'How many tag sequences must brute force score for q = 2 tags and T = 4 words?', '16', 'q to the power T.',
       ['Each word: 2 choices.', 'Four words multiply the choices.', eq('2⁴ = 16')], check=16, tol=0.01)
K.calc('e', 'They can fish: v₁(N) = π<sub>N</sub> × b<sub>N</sub>(they) with π<sub>N</sub> = 0.7 and b<sub>N</sub>(they) = 0.3. Two decimals.', '0.21', 'Start times emission.',
       ['First column uses start probabilities.', 'π<sub>N</sub> = 0.7, b<sub>N</sub>(they) = 0.3.', eq('0.7 × 0.3 = 0.21')], check=0.21, tol=0.001)
K.calc('m', 'Viterbi steps T × q² for a 25 word sentence with 45 tags?', '50625', 'Multiply.',
       ['q² = 45 × 45 = 2,025.', 'T = 25.', eq('25 × 2,025 = 50,625')], check=50625, tol=0.5)
K.calc('m', 'They can fish: v₂(M) from v₁(N) = 0.21, a(N → M) = 0.4 and b<sub>M</sub>(can) = 1. Three decimals.', '0.084', 'Only N is alive at t = 1.',
       ['Predecessors M and V have score 0.', 'From N: 0.21 × 0.4 = 0.084.', eq('× b<sub>M</sub>(can) 1.0 = 0.084')], check=0.084, tol=0.0005)
K.calc('m', 'They can fish: v₃(V). Predecessors v₂ = N 0.0084, M 0.084, V 0.0252. a(N → V) = 0.4, a(M → V) = 0.9, a(V → V) = 0.3, b<sub>V</sub>(fish) = 0.7. Five decimals.', '0.05292', 'Take the max, then multiply by the emission.',
       ['From N: 0.0084 × 0.4 = 0.00336.', 'From M: 0.084 × 0.9 = 0.0756. From V: 0.0252 × 0.3 = 0.00756.', 'Max is 0.0756, from M.', eq('0.0756 × 0.7 = 0.05292')], check=0.05292, tol=0.000005)
K.calc('m', 'They can fish: v₃(N). Predecessors as before, a(N → N) = 0.2, a(M → N) = 0.1, a(V → N) = 0.6, b<sub>N</sub>(fish) = 0.5. Five decimals.', '0.00756', 'Same pattern.',
       ['From N: 0.0084 × 0.2 = 0.00168.', 'From M: 0.084 × 0.1 = 0.0084. From V: 0.0252 × 0.6 = 0.01512.', 'Max is 0.01512, from V.', eq('0.01512 × 0.5 = 0.00756')], check=0.00756, tol=0.000005)
K.calc('h', 'Forward: α₃(V) for they can fish, with the same numbers. Six decimals.', '0.060564', 'Sum instead of max.',
       ['0.00336 + 0.0756 + 0.00756 = 0.08652.', 'Multiply by b<sub>V</sub>(fish) = 0.7.', eq('0.08652 × 0.7 = 0.060564')], check=0.060564, tol=0.0000005)
K.calc('h', 'P(they can fish) = α₃(N) + α₃(M) + α₃(V) with 0.0126, 0 and 0.060564. Then P(N M V | W) for P(W, NMV) = 0.05292. Four decimals.', '0.7233', 'Sum, then divide.',
       ['P(W) = 0.0126 + 0 + 0.060564 = 0.073164.', 'Posterior = 0.05292 ÷ 0.073164.', eq('= 0.7233')], check=0.05292 / 0.073164, tol=0.0001)
K.calc('h', 'Problem G8: decode "fish can fish". t₁: N 0.35, V 0.14. t₂: N 0.0168, M 0.14, V 0.042. With a(M → V) = 0.9 and b<sub>V</sub>(fish) = 0.7, what is v₃(V)? Four decimals.', '0.0882', 'Compare the three predecessors.',
       ['From N: 0.0168 × 0.4 = 0.00672.', 'From M: 0.14 × 0.9 = 0.126. From V: 0.042 × 0.3 = 0.0126.', 'Max is 0.126, from M.', eq('0.126 × 0.7 = 0.0882')], check=0.0882, tol=0.00005)
K.calc('x', 'Problem G10: how many multiplications does brute force use for they can fish (each sequence needs π·b then two a·b pairs)?', '135', '27 sequences × 5 products.',
       ['3³ = 27 sequences.', 'Each: π × b is 1, then (× a × b) twice is 4 more, so 5.', eq('27 × 5 = 135, against 39 for Viterbi')], check=135, tol=0.5)
K.calc('x', 'A trigram HMM with 45 tags runs Viterbi in about T × q³ steps. How many for a 25 word sentence?', '2278125', 'q³ = 91,125.',
       ['q³ = 45 × 45 × 45 = 91,125.', 'T = 25.', eq('25 × 91,125 = 2,278,125')], check=2278125, tol=0.5)

# ---------------------------------------------------------------- assignments
SET = '''{"N": 0.7, "M": 0.1, "V": 0.2}, {"N": {"N": 0.2, "M": 0.4, "V": 0.4}, "M": {"N": 0.1, "M": 0.0, "V": 0.9}, "V": {"N": 0.6, "M": 0.1, "V": 0.3}}, {"N": {"they": 0.3, "can": 0.2, "fish": 0.5}, "M": {"can": 1.0}, "V": {"can": 0.3, "fish": 0.7}}'''
G7 = '''{"N": 0.8, "M": 0, "V": 0.2}, {"N": {"N": 0, "M": 0.5, "V": 0.5}, "M": {"N": 0, "M": 0, "V": 1}, "V": {"N": 1, "M": 0, "V": 0}}, {"N": {"they": 0.6, "fish": 0.4}, "M": {"can": 1}, "V": {"fish": 0.4, "swim": 0.4, "can": 0.2}}'''
K.assign('vit', 'h', 'Write Viterbi',
         '<p>Write <code>viterbi(pi, A, B, words)</code>. The tags are the keys of pi, in order. A[s][t] is P(t | s), B[t] maps words to P(word | t) and a missing word has probability 0. Return (list of tags, probability rounded to 6 decimals). Break ties by the first tag in pi\'s order.</p>',
         '''
def viterbi(pi, A, B, words):
    # your code here
    pass
''', [(f'viterbi({SET}, ["they", "can", "fish"])', (['N', 'M', 'V'], 0.05292)),
      (f'viterbi({SET}, ["fish", "can", "fish"])', (['N', 'M', 'V'], 0.0882)),
      (f'viterbi({G7}, ["they", "can", "fish"])', (['N', 'M', 'V'], 0.096))],
         '''
def viterbi(pi, A, B, words):
    tags = list(pi)
    v = [{t: pi[t] * B[t].get(words[0], 0) for t in tags}]
    back = []
    for w in words[1:]:
        col, bp = {}, {}
        for t in tags:
            best = max(tags, key=lambda s: v[-1][s] * A[s][t])
            col[t] = v[-1][best] * A[best][t] * B[t].get(w, 0)
            bp[t] = best
        v.append(col)
        back.append(bp)
    last = max(tags, key=lambda t: v[-1][t])
    path = [last]
    for bp in reversed(back):
        path.insert(0, bp[path[0]])
    return (path, round(v[-1][last], 6))
''', 'Keep one dictionary of scores and one of back pointers per word. max over a list keeps the first maximum, which gives the tie rule for free.', '<p>The third test is problem G7, the HMM trained in chapter 5.2.</p>')
K.assign('fwd', 'm', 'Write the forward algorithm',
         '<p>Write <code>forward(pi, A, B, words)</code> that returns P(words) summed over every tag sequence, rounded to 6 decimals. Same table format as the Viterbi assignment.</p>',
         '''
def forward(pi, A, B, words):
    # your code here
    pass
''', [(f'forward({SET}, ["they", "can", "fish"])', 0.073164),
      ('forward({"A": 0.25, "N": 0.75}, {"A": {"A": 0, "N": 1}, "N": {"A": 0.5, "N": 0.5}}, {"A": {}, "N": {"killer": 0.3, "clown": 0.4}}, ["killer", "clown"])', 0.045)],
         '''
def forward(pi, A, B, words):
    tags = list(pi)
    alpha = {t: pi[t] * B[t].get(words[0], 0) for t in tags}
    for w in words[1:]:
        alpha = {t: sum(alpha[s] * A[s][t] for s in tags) * B[t].get(w, 0) for t in tags}
    return round(sum(alpha.values()), 6)
''', 'Change max to sum and drop the back pointers.', '<p>For killer clown only one path is non zero, so the sum equals the best path, 0.045.</p>')
K.assign('size', 'e', 'Brute force against Viterbi',
         '<p>Write <code>search(q, T)</code> that returns (q ** T, T * q * q) and <code>speedup(q, T)</code> that returns the first divided by the second, rounded to 1 decimal.</p>',
         '''
def search(q, T):
    # your code here
    pass

def speedup(q, T):
    # your code here
    pass
''', [('search(2, 4)', (16, 16)), ('search(12, 10)', (61917364224, 1440)), ('speedup(3, 3)', 1.0), ('speedup(12, 10)', 42998169.6)],
         '''
def search(q, T):
    return (q ** T, T * q * q)

def speedup(q, T):
    a, b = search(q, T)
    return round(a / b, 1)
''', 'Use integer powers so large values stay exact.', '<p>For tiny inputs the two are equal, which is why the slide examples look easy. The gap explodes as soon as sentences get long.</p>')

K.must('Search size', 'Brute force scores q^T sequences. Viterbi does about T × q² steps. PTB 45 tags, 25 words: 2.1 × 10^41 against 50,625.')
K.must('Viterbi recursion', 'v1(j) = πj bj(w1). vt(j) = max over i of vt−1(i) aij bj(wt). Keep back pointers, take the best last cell and trace back.')
K.must('Forward', 'Same table with sum: P(W) = sum of the last column. Posterior P(T | W) = P(W, T) ÷ P(W). they can fish: 0.073164 and 0.7233.')
K.must('Why it works', 'Principle of optimality: under the Markov assumption the best path passes through the best partial path into each cell.')
K.must('Ties and trigrams', 'Ties: pick either, or return k best. Trigram HMM (TnT): O(T q³), needs smoothing, about 96.7% on PTB.')

T = K.topic(
    slug='viterbi', topic='viterbi', step=(5, 'Tagging and syntax', 'nlp-syntax', 'Tag every word with its part of speech using HMMs and Viterbi, mark chunks and names with IOB, and draw constituency and dependency trees.', 'College and masters'),
    title='Decoding with Viterbi', short='Viterbi', badge='5.3', minutes=50,
    lead='See why scoring every tag sequence is hopeless, fill the Viterbi trellis by hand, prove it is safe, and turn the same table into the forward algorithm.',
    desc='The decoding objective, q to the power T against T times q squared, the Viterbi recursion and back pointers on "they can fish", the proof of optimality, the forward algorithm with P(W) and the posterior, ties, trigram HMMs and the British Left Waffles headline decided by an HMM.',
    summary='Brute force against dynamic programming, the Viterbi and forward recursions, posteriors, ties and trigram HMMs.',
    keywords=['Viterbi', 'trellis', 'back pointer', 'forward algorithm', 'posterior', 'dynamic programming', 'TnT', 'search space'],
    recap='<p>Brute force grows as q<sup>T</sup>. Viterbi keeps one best score and back pointer per cell, costs T q², and is exact by the principle of optimality. The forward algorithm swaps max for sum to get P(W), and dividing by it gives the model\'s confidence in a tagging.</p>')
