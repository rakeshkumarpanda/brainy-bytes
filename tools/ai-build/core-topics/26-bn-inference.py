# Chapter 9.3: inference in Bayesian networks, exact and approximate. The uploaded slides and transcripts do not cover
# this step, so it follows AIMA 3rd ed. sections 14.4 and 14.5 (4th ed. 13.3 and 13.4). Every number in this chapter
# was checked by running its code and the varelim and sampling animations.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()
STEP9 = (9, 'Probability and Bayesian networks', 'cai-bayes', 'Reason when facts are uncertain: probability, Bayesian networks, directed and undirected models, exact and sampling inference, and causality.', 'College')

K.code('enum', r'''
# Inference by enumeration on the burglary network (AIMA figure 14.9): P(Burglary | j, m).
parents = {"B": [], "E": [], "A": ["B", "E"], "J": ["A"], "M": ["A"]}
table = {"B": {(): 0.001}, "E": {(): 0.002},
         "A": {(True, True): 0.95, (True, False): 0.94, (False, True): 0.29, (False, False): 0.001},
         "J": {(True,): 0.90, (False,): 0.05}, "M": {(True,): 0.70, (False,): 0.01}}
order = ["B", "E", "A", "J", "M"]

def prob(var, value, world):
    p = table[var][tuple(world[q] for q in parents[var])]
    return p if value else 1 - p

def enum_all(i, world):
    if i == len(order):
        return 1.0
    var = order[i]
    if var in world:                                   # evidence or query: one value
        return prob(var, world[var], world) * enum_all(i + 1, world)
    total = 0                                          # hidden: sum over both values
    for v in [True, False]:
        world[var] = v
        total = total + prob(var, v, world) * enum_all(i + 1, world)
    del world[var]
    return total

yes = enum_all(0, {"B": True, "J": True, "M": True})
no = enum_all(0, {"B": False, "J": True, "M": True})
print("unnormalised:", round(yes, 7), round(no, 7))
print("P(Burglary | j, m) =", round(yes / (yes + no), 3))
''')

K.code('lw', r'''
# Likelihood weighting on the sprinkler network: estimate P(Rain | Sprinkler = true, WetGrass = true).
import random
rng = random.Random(1)
parents = {"C": [], "S": ["C"], "R": ["C"], "W": ["S", "R"]}
table = {"C": {(): 0.5}, "S": {(True,): 0.1, (False,): 0.5}, "R": {(True,): 0.8, (False,): 0.2},
         "W": {(True, True): 0.99, (True, False): 0.90, (False, True): 0.90, (False, False): 0.0}}
evidence = {"S": True, "W": True}

rain_w, total_w = 0, 0
for n in range(10):
    world, weight = {}, 1.0
    for var in ["C", "S", "R", "W"]:
        p = table[var][tuple(world[q] for q in parents[var])]
        if var in evidence:                    # fix the evidence and multiply in its likelihood
            world[var] = evidence[var]
            weight = weight * (p if evidence[var] else 1 - p)
        else:                                  # sample the others from their tables
            world[var] = rng.random() < p
    total_w = total_w + weight
    if world["R"]:
        rain_w = rain_w + weight
    print("sample", n + 1, "C =", world["C"], "R =", world["R"], "weight =", round(weight, 3))
print("estimate:", round(rain_w / total_w, 3), " exact: 0.3204")
''')

K.lesson('enumeration', 'Exact inference by enumeration', f'''
{src('AIMA 3rd ed., section 14.4.1 (4th ed., 13.3.1), figures 14.8 and 14.9.')}
{wwh('Inference means computing P(query | evidence) from the network. Enumeration writes the answer as a sum of products of CPT entries, summing over every value of every hidden variable.',
     'It is the simplest correct method and the reference that every faster method must agree with.',
     'Go through the variables in topological order. For a query or evidence variable, multiply in its table entry. For a hidden variable, try both values, recurse, and add. Do this for each query value, then normalise.')}
{fxs(fx('Enumeration', 'P(B | j, m) = α Σ_e Σ_a P(B) P(e) P(a | B, e) P(j | a) P(m | a)', 'Hidden variables E and A are summed out.', key=True),
     fx('Moving factors outside', 'α P(B) Σ_e P(e) Σ_a P(a | B, e) P(j | a) P(m | a)', 'P(B) does not depend on e or a, so it moves out of both sums.'),
     fx('Cost', 'time O(2ⁿ), memory O(n)', 'Depth first over the hidden variables.'))}
{code('enum')}
{steps('Worked example: P(b, j, m) for the burglary network', [
    'P(b) = 0.001. For each e and a, multiply P(e) P(a | b, e) P(j | a) P(m | a).',
    'e true: 0.002 × (0.95 × 0.9 × 0.7 + 0.05 × 0.05 × 0.01) = 0.002 × 0.598525.',
    'e false: 0.998 × (0.94 × 0.9 × 0.7 + 0.06 × 0.05 × 0.01) = 0.998 × 0.59223.',
    'Sum: 0.00119705 + 0.59104554 = 0.59224259. Times P(b): 0.00059224.',
    eq('P(¬b, j, m) ≈ 0.0014919 in the same way, so P(b | j, m) = 0.00059224 ÷ 0.00208414 ≈ 0.284')])}
{note('Enumeration repeats work: P(j | a) P(m | a) is computed again for each value of e. Variable elimination stores such parts once.', 'warn')}
''', kw=['inference by enumeration', 'hidden variables', 'enumeration tree', 'normalisation', 'repeated work'])

K.lesson('ve', 'Variable elimination', f'''
{src('Zhang and Poole (1994), Dechter (1999), and AIMA 3rd ed., section 14.4.2.')}
{wwh('Variable elimination does the sums of enumeration from the inside out and keeps the results as tables called factors, so nothing is computed twice.',
     'It turns many repeated products into a few table operations. On a polytree (a network with at most one path between any two nodes) it runs in time linear in the size of the network.',
     'Make one factor per CPT with the evidence plugged in. For each hidden variable in some order: multiply all factors that mention it (a pointwise product) and sum the variable out. At the end multiply what is left and normalise.')}
{fxs(fx('Pointwise product', 'f(X, Y) × g(Y, Z) = h(X, Y, Z), with h(x, y, z) = f(x, y) g(y, z)', 'The result covers the union of the variables.'),
     fx('Summing out', 'h(X, Z) = Σ_y f(X, y, Z)', 'Add the entries for each value of the removed variable.', key=True),
     fx('Cost', 'exponential in the size of the largest factor made, which depends on the order', 'The best possible largest factor size, minus one, is the treewidth of the graph.'))}
{viz('varelim')}
{note('Irrelevant variables: every variable that is not an ancestor of the query or the evidence can be removed before starting. Summing it out only gives factors full of 1s, as the second tip of the animation shows.', 'tip')}
{deep('Complexity of exact inference', '<p>On polytrees, variable elimination and Pearl’s message passing are linear. In general, exact inference in Bayesian networks is #P-hard (Cooper, 1990), because it can count the solutions of a SAT formula. Finding the best elimination order is NP-hard, so programs use greedy rules such as min fill or min degree. The junction tree algorithm (Lauritzen and Spiegelhalter, 1988) groups variables into clusters so that all marginals come from one pass of messages.</p>')}
''', kw=['variable elimination', 'factor', 'pointwise product', 'sum out', 'elimination order', 'treewidth', 'polytree', 'junction tree', 'irrelevant variables'])

K.lesson('sampling', 'Approximate inference by sampling', f'''
{src('AIMA 3rd ed., section 14.5 (4th ed., 13.4). Likelihood weighting: Fung and Chang (1989), Shachter and Peot (1989). Gibbs sampling: Geman and Geman (1984).')}
{wwh('Sampling methods draw many random worlds from the network and count. The fraction of samples where the query holds estimates its probability.',
     'Exact inference can take exponential time on big networks with many loops. Sampling gives an answer of any wanted accuracy, and more samples give a better answer.',
     'Prior sampling sets each variable from its CPT, parents first. <b>Rejection sampling</b> throws away samples that disagree with the evidence. <b>Likelihood weighting</b> fixes the evidence and weights each sample by how likely that evidence was. <b>Gibbs sampling</b> walks from world to world, resampling one hidden variable at a time from its Markov blanket.')}
{fxs(fx('Rejection sampling', 'P(X | e) ≈ N(X, e) ÷ N(e)', 'Consistent, but wastes the fraction 1 − P(e) of samples.'),
     fx('Likelihood weight', 'w = Π over evidence variables Eᵢ of P(eᵢ | parents(Eᵢ))', 'Estimate: sum of weights with X true ÷ sum of all weights.', key=True),
     fx('Gibbs step', 'P(x | mb(X)) = α P(x | parents(X)) Π over children Y of P(y | parents(Y))', 'Only the Markov blanket is needed.'),
     fx('Error of an estimate', 'standard error ≈ √(p (1 − p) ÷ N)', 'Four times the samples halves the error.'))}
{viz('sampling')}
{code('lw')}
{steps('Worked example: one likelihood weighted sample for P(Rain | Sprinkler = true, WetGrass = true)', [
    'Cloudy is sampled from P(Cloudy) = 0.5: say true.',
    'Sprinkler is evidence (true): weight × P(s | c) = 0.1.',
    'Rain is sampled from P(Rain | c) = 0.8: say true.',
    'WetGrass is evidence (true): weight × P(w | s, r) = 0.99.',
    eq('w = 0.1 × 0.99 = 0.099, the textbook example')])}
{note('Likelihood weighting suffers when evidence comes late in the order (at the leaves): the samples ignore it while choosing the earlier variables, so most of them get tiny weights.', 'warn')}
''', kw=['sampling', 'prior sampling', 'rejection sampling', 'likelihood weighting', 'Gibbs sampling', 'MCMC', 'Markov blanket', 'standard error'])

K.lesson('maths', 'The maths: why the samplers give the right answer', f'''
{fxs(
    fx('Prior sampling is consistent', 'S(x₁, ..., xₙ) = Π P(xᵢ | parents(Xᵢ)) = P(x₁, ..., xₙ)', 'Each world is drawn with exactly its probability.'),
    fx('Likelihood weighting is consistent', 'S_WS(z, e) w(z, e) = Π P(zᵢ | parents) × Π P(eᵢ | parents) = P(z, e)', 'The sampling distribution times the weight is the true joint.', key=True),
    fx('Gibbs sampling', 'the posterior P(x | e) is the stationary distribution of the Markov chain', 'Detailed balance: π(x) q(x → x′) = π(x′) q(x′ → x).'),
    fx('Variable elimination size', 'eliminating X makes a factor over all variables that share a factor with X', 'Bad orders build large factors.'))}
{steps('Worked example: a Gibbs step for Cloudy, with Sprinkler = true and Rain = false', [
    'The Markov blanket of Cloudy is its two children, Sprinkler and Rain. Cloudy has no parents, and its children have no other parents.',
    'Cloudy true: P(c) P(s | c) P(¬r | c) = 0.5 × 0.1 × 0.2 = 0.01.',
    'Cloudy false: 0.5 × 0.5 × 0.8 = 0.2.',
    eq('P(Cloudy | s, ¬r) = 0.01 ÷ 0.21 ≈ 0.0476')])}
''', kw=['consistency', 'sampling distribution', 'stationary distribution', 'detailed balance', 'Gibbs step example'])

K.lesson('compare', 'Inference methods compared', f'''
{versus('Inference in graphical models', ['', 'Enumeration', 'Variable elimination', 'Junction tree', 'Rejection sampling', 'Likelihood weighting', 'Gibbs sampling (MCMC)', 'Loopy belief propagation'], [
    ['Exact', 'Yes', 'Yes', 'Yes', 'No (converges)', 'No (converges)', 'No (converges)', 'No (may not converge)'],
    ['Cost', 'O(2ⁿ) time, O(n) memory', 'exponential in the largest factor', 'exponential in the largest cluster', 'grows as 1 ÷ P(e)', 'cheap per sample', 'cheap per step', 'cheap per pass'],
    ['Good for', 'tiny networks, checking', 'one query, small treewidth', 'all marginals at once', 'likely evidence', 'evidence near the roots', 'large networks, any evidence', 'large networks with loops, error correcting codes'],
    ['Weak when', 'more than about 25 variables', 'large treewidth', 'large treewidth', 'rare evidence', 'evidence at the leaves', 'near deterministic tables (slow mixing)', 'strong loops']],
    'use variable elimination or the junction tree when the treewidth is small, and Gibbs sampling or other MCMC methods when it is not.')}
{scene('Inference at work', '<p>Turbo codes and LDPC codes in mobile phones and Wi-Fi are decoded with belief propagation on a loopy graph (McEliece, MacKay and Cheng, 1998). Stan and PyMC run Hamiltonian Monte Carlo, a modern MCMC method, for statistics in medicine and science. Bayesian network tools such as Hugin and GeNIe use the junction tree for exact answers in medical and fault diagnosis.</p>')}
''', kw=['comparison', 'loopy belief propagation', 'Hamiltonian Monte Carlo', 'Stan', 'Hugin', 'turbo codes'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Exact inference adds up every way the world could be. Sampling plays the world many times at random and counts what happened.</p>',
    '<p>Enumeration sums products over hidden variables. Variable elimination stores factors and sums out one variable at a time. Rejection sampling, likelihood weighting and Gibbs sampling estimate the answer, with error about √(p(1 − p) ÷ N).</p>',
    '<p>Exact inference is #P-hard, and even approximating it within a fixed error is NP-hard in general (Dagum and Luby, 1993). Treewidth decides exact cost. Variational methods turn inference into optimisation of a simpler distribution by minimising a KL divergence.</p>',
    '<p>Research: amortised inference, where a neural network learns to output posteriors fast (as in variational autoencoders), sequential Monte Carlo (particle filters) for changing worlds, and knowledge compilation into arithmetic circuits for fast exact queries.</p>')}
''', kw=['#P-hard', 'variational inference', 'KL divergence', 'amortised inference', 'particle filter', 'arithmetic circuits'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Enumeration: P(X | e) = α Σ over hidden y of Π CPT entries. O(2ⁿ) time, O(n) memory. P(b | j, m) ≈ 0.284.',
    'Variable elimination multiplies factors and sums out hidden variables one at a time. Its cost depends on the largest factor, set by the order and the treewidth.',
    'Exact inference is linear on polytrees and #P-hard in general.',
    'Rejection sampling wastes samples that disagree with rare evidence. Likelihood weighting fixes evidence and weights samples by its likelihood.',
    'Gibbs sampling resamples one variable from its Markov blanket and converges to the posterior.'],
    'chapter 9.4 asks a different question: what happens if we act on the world, not just watch it. That is causality.')}
{nbcard('bn-inference', 'Run enumeration on the burglary network and likelihood weighting on the sprinkler network, then write enumeration, rejection sampling and likelihood weighting yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In P(Burglary | j, m), the hidden variables are', ['JohnCalls and MaryCalls', 'Earthquake and Alarm', 'Burglary only', 'none'], 1,
       'Neither query nor evidence.', 'They are summed out.')
K.quiz('e', 'Inference by enumeration needs memory', ['O(2ⁿ)', 'O(n)', 'O(1)', 'O(n²)'], 1,
       'Depth first.', 'Time is O(2ⁿ).')
K.quiz('e', 'Rejection sampling throws away samples that', ['have low weight', 'disagree with the evidence', 'are repeated', 'come late'], 1,
       'Reject.', 'Only samples that match the evidence are counted.')
K.quiz('e', 'In likelihood weighting, evidence variables are', ['sampled like the others', 'fixed to their observed values, and the weight is multiplied by their likelihood', 'ignored', 'removed from the network'], 1,
       'Fix and weight.', 'No sample is wasted.')
K.quiz('m', 'Summing out Y from f(X, Y) gives', ['f(X)', 'Σ_y f(X, y), a factor over X', 'max over y', 'f(X) × f(Y)'], 1,
       'Add the entries.', 'The variable disappears.')
K.quiz('m', 'On a polytree, variable elimination runs in', ['exponential time', 'time linear in the size of the network', 'constant time', 'it cannot run'], 1,
       'At most one path between nodes.', 'Factors stay small.')
K.quiz('m', 'Gibbs sampling resamples a variable from', ['its prior', 'its Markov blanket', 'the evidence only', 'a uniform distribution'], 1,
       'Blanket.', 'P(x | mb(X)) ∝ P(x | parents) Π P(child | its parents).')
K.quiz('m', 'Rejection sampling is poor when', ['the evidence is likely', 'the evidence is unlikely', 'there are few variables', 'the network is a chain'], 1,
       'Most samples are rejected.', 'Expected kept samples = N P(e).')
K.quiz('h', 'Exact inference in a general Bayesian network is', ['polynomial', '#P-hard', 'undecidable', 'linear'], 1,
       'Cooper 1990.', 'It can count SAT solutions.')
K.quiz('h', 'To halve the error of a sampling estimate you need', ['twice the samples', 'four times the samples', 'half the samples', 'the same'], 1,
       'Error ∝ 1 ÷ √N.', '√4 = 2.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: for P(B | j, m), which variables can be pruned before variable elimination?', ['none: every variable is an ancestor of the query or the evidence', 'Earthquake', 'Alarm', 'JohnCalls'], 0,
       'Ancestors of {B, J, M}.', 'Alarm and Earthquake are ancestors of J and M, so all stay.')
K.quiz('x', 'In the style of a CMU 10-708 exam: Gibbs sampling mixes badly when', ['the network is small', 'CPTs are close to deterministic, so one variable cannot change without others', 'evidence is at the roots', 'there are no loops'], 1,
       'Stuck chains.', 'Changing one variable at a time cannot cross between two near certain worlds.')

# ---------------------------------------------------------------- calc
K.calc('e', 'For P(B | j, m) by enumeration, how many full joint terms are added (both values of B)?', '8', '2 hidden variables.',
       ['Hidden E and A: 2 × 2 = 4 terms per value of B.', 'B has 2 values.', eq('8')], check=8)
K.calc('e', 'Rejection sampling for P(Rain | Sprinkler = true), with P(Sprinkler = true) = 0.3. Of 1000 samples, how many are kept on average?', '300', 'N × P(e).',
       ['P(e) = 0.3.', '1000 samples.', eq('300')], check=300)
K.calc('e', 'Evidence with probability 0.001: on average how many samples does rejection sampling draw for each one it keeps?', '1000', '1 ÷ P(e).',
       ['Each sample is kept with chance 0.001.', 'The waiting time has mean 1 ÷ 0.001.', eq('1000')], check=1000)
K.calc('m', 'Enumeration: P(b, j, m) to 7 decimals.', '0.0005922', 'P(b) times the double sum.',
       ['Double sum ≈ 0.59224.', 'Times P(b) = 0.001.', eq('≈ 0.0005922')], check=0.0005922, tol=0.0000002)
K.calc('m', 'P(b | j, m) from P(b, j, m) = 0.00059224 and P(¬b, j, m) = 0.0014919.', '0.284', 'Normalise.',
       ['Sum = 0.00208414.', 'Divide.', eq('≈ 0.284')], check=0.284, tol=0.0005)
K.calc('m', 'Likelihood weight of the sample Cloudy = true, Rain = true, with evidence Sprinkler = true and WetGrass = true.', '0.099', 'P(s | c) × P(w | s, r).',
       ['P(s | c) = 0.1.', 'P(w | s, r) = 0.99.', eq('0.099')], check=0.099, tol=0.0005)
K.calc('m', 'With no evidence and Alarm eliminated first, the product of the factors that mention Alarm covers how many entries?', '32', 'Variables B, E, A, J, M.',
       ['fA(B, E, A), fJ(A, J), fM(A, M).', 'Union: 5 variables.', eq('2⁵ = 32')], check=32)
K.calc('h', 'Gibbs step: P(Cloudy | Sprinkler = true, Rain = false), to 4 decimals.', '0.0476', 'P(c) P(s | c) P(¬r | c), normalised.',
       ['True: 0.5 × 0.1 × 0.2 = 0.01.', 'False: 0.5 × 0.5 × 0.8 = 0.2.', eq('0.01 ÷ 0.21 ≈ 0.0476')], check=0.0476, tol=0.0005)
K.calc('h', 'Standard error of an estimate with p = 0.3 and N = 10,000 samples, to 4 decimals.', '0.0046', '√(p(1 − p) ÷ N).',
       ['p(1 − p) = 0.21.', '0.21 ÷ 10,000 = 0.000021.', eq('√0.000021 ≈ 0.0046')], check=0.0046, tol=0.0001)
K.calc('x', 'Gibbs step: P(Rain | Cloudy = true, Sprinkler = true, WetGrass = true), to 4 decimals.', '0.8148', 'P(r | c) P(w | s, r), normalised.',
       ['True: 0.8 × 0.99 = 0.792.', 'False: 0.2 × 0.90 = 0.18.', eq('0.792 ÷ 0.972 ≈ 0.8148')], check=0.8148, tol=0.0005)

# ---------------------------------------------------------------- assignments
NET = '''PARENTS = {"B": [], "E": [], "A": ["B", "E"], "J": ["A"], "M": ["A"]}
TABLE = {"B": {(): 0.001}, "E": {(): 0.002},
         "A": {(True, True): 0.95, (True, False): 0.94, (False, True): 0.29, (False, False): 0.001},
         "J": {(True,): 0.90, (False,): 0.05}, "M": {(True,): 0.70, (False,): 0.01}}
ORDER = ["B", "E", "A", "J", "M"]
'''
SPR = '''import random
PARENTS = {"C": [], "S": ["C"], "R": ["C"], "W": ["S", "R"]}
TABLE = {"C": {(): 0.5}, "S": {(True,): 0.1, (False,): 0.5}, "R": {(True,): 0.8, (False,): 0.2},
         "W": {(True, True): 0.99, (True, False): 0.90, (False, True): 0.90, (False, False): 0.0}}
ORDER = ["C", "S", "R", "W"]
'''
K.assign('enumask', 'm', 'Enumeration on the burglary network',
         '<p>Write <code>ask(evidence)</code> that returns P(B = True | evidence) by enumeration. evidence maps some of "J", "M" to True or False.</p>',
         NET + '''
def ask(evidence):
    # your code here
    pass
''', [("round(ask({'J': True, 'M': True}), 3)", 0.284), ("round(ask({'J': True}), 4)", 0.0163),
      ("round(ask({'M': True}), 4)", 0.0561), ("round(ask({}), 4)", 0.001)],
         NET + '''
def prob(var, value, world):
    p = TABLE[var][tuple(world[q] for q in PARENTS[var])]
    if value:
        return p
    return 1 - p

def enum_all(i, world):
    if i == len(ORDER):
        return 1.0
    var = ORDER[i]
    if var in world:
        return prob(var, world[var], world) * enum_all(i + 1, world)
    total = 0
    for v in [True, False]:
        world[var] = v
        total = total + prob(var, v, world) * enum_all(i + 1, world)
    del world[var]
    return total

def ask(evidence):
    yes = dict(evidence)
    yes["B"] = True
    no = dict(evidence)
    no["B"] = False
    a = enum_all(0, yes)
    b = enum_all(0, no)
    return a / (a + b)
''', 'Write a recursive helper over ORDER. Fixed variables multiply in one entry, hidden ones add over True and False.', '<p>Mary alone raises P(b) more than John alone (0.056 against 0.016), because Mary has fewer false alarms (0.01 against 0.05).</p>')
K.assign('rejection', 'm', 'Rejection sampling',
         '<p>Write <code>rejection(n, seed)</code> that draws n prior samples of the sprinkler network with <code>rng = random.Random(seed)</code>, keeps those with Sprinkler = True, and returns the fraction of kept samples with Rain = True.</p>',
         SPR + '''
def rejection(n, seed):
    rng = random.Random(seed)
    # your code here
    pass
''', [("abs(rejection(20000, 1) - 0.3) < 0.03", True), ("abs(rejection(20000, 7) - 0.3) < 0.03", True)],
         SPR + '''
def rejection(n, seed):
    rng = random.Random(seed)
    kept = 0
    rain = 0
    for i in range(n):
        world = {}
        for var in ORDER:
            p = TABLE[var][tuple(world[q] for q in PARENTS[var])]
            world[var] = rng.random() < p
        if world["S"]:
            kept = kept + 1
            if world["R"]:
                rain = rain + 1
    return rain / kept
''', 'Sample each variable in ORDER with rng.random() < P(true | parents). Count only samples with S True.', '<p>The exact answer is 0.3, and about 70 percent of the samples are thrown away.</p>')
K.assign('lweight', 'h', 'Likelihood weighting',
         '<p>Write <code>lw(n, seed)</code> that estimates P(Rain = True | Sprinkler = True, WetGrass = True) with n likelihood weighted samples.</p>',
         SPR + '''
def lw(n, seed):
    rng = random.Random(seed)
    # your code here
    pass
''', [("abs(lw(20000, 2) - 0.3204) < 0.03", True), ("abs(lw(20000, 5) - 0.3204) < 0.03", True)],
         SPR + '''
def lw(n, seed):
    rng = random.Random(seed)
    evidence = {"S": True, "W": True}
    rain = 0
    total = 0
    for i in range(n):
        world = {}
        weight = 1.0
        for var in ORDER:
            p = TABLE[var][tuple(world[q] for q in PARENTS[var])]
            if var in evidence:
                world[var] = evidence[var]
                if evidence[var]:
                    weight = weight * p
                else:
                    weight = weight * (1 - p)
            else:
                world[var] = rng.random() < p
        total = total + weight
        if world["R"]:
            rain = rain + weight
    return rain / total
''', 'For evidence variables, set the value and multiply the weight by its probability. Add weights, not counts.', '<p>The exact answer 0.3204 comes from enumeration.</p>')

K.must('Enumeration', 'P(X | e) = α Σ_y Π P(xᵢ | parents). O(2ⁿ) time, O(n) space. P(b | j, m) ≈ 0.284.')
K.must('Variable elimination', 'Factors from CPTs with evidence. Multiply factors with X, sum out X. Cost exponential in the largest factor (treewidth). Drop non ancestors.')
K.must('Complexity', 'Polytree: linear. General: #P-hard (Cooper 1990).')
K.must('Samplers', 'Rejection: N(x, e) ÷ N(e). LW: w = Π P(eᵢ | parents). Gibbs: sample from P(x | mb(X)). Error ≈ √(p(1 − p) ÷ N).')
K.must('Key numbers', 'LW sample weight 0.1 × 0.99 = 0.099. P(Rain | s, w) = 0.3204. P(Rain | s) = 0.3.')

T = K.topic(
    slug='bn-inference', topic='bn-inference', step=STEP9,
    title='Inference in Bayesian networks', short='Inference', badge='9.3', minutes=55,
    lead='Get answers out of a Bayesian network. Sum exactly with enumeration and variable elimination, see why exact inference can be hard, and estimate with rejection sampling, likelihood weighting and Gibbs sampling.',
    desc='Exact inference by enumeration, variable elimination with factors, pointwise products and summing out, elimination order and treewidth, irrelevant variables, complexity on polytrees and the #P-hardness of general inference, the junction tree, approximate inference by prior sampling, rejection sampling, likelihood weighting and Gibbs sampling, consistency proofs, standard error and a comparison of inference methods.',
    summary='Enumeration, variable elimination, complexity, rejection sampling, likelihood weighting and Gibbs sampling.',
    keywords=['inference', 'enumeration', 'variable elimination', 'factor', 'treewidth', 'polytree', 'rejection sampling', 'likelihood weighting', 'Gibbs sampling', 'MCMC'],
    recap='<p>Exact: sum out hidden variables, best with variable elimination. Approximate: sample, reject or weight, or walk with Gibbs.</p>',
    nb={'enum': 'Enumeration for P(Burglary | j, m)', 'lw': 'Ten likelihood weighted samples'})
