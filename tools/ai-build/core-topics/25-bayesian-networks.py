# Chapter 9.2: Bayesian networks and Markov networks (directed and undirected models). The uploaded slides and
# transcripts do not cover this step, so it follows AIMA 3rd ed. chapter 14 (4th ed. chapter 13), Pearl (1988) and
# Koller and Friedman (2009). Every number in this chapter was checked by running its code and the animations.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()
STEP9 = (9, 'Probability and Bayesian networks', 'cai-bayes', 'Reason when facts are uncertain: probability, Bayesian networks, directed and undirected models, exact and sampling inference, and causality.', 'College')

K.code('alarm', r'''
# The burglary network of AIMA figure 14.2. Each table gives P(variable = true | its parents).
parents = {"B": [], "E": [], "A": ["B", "E"], "J": ["A"], "M": ["A"]}
table = {"B": {(): 0.001}, "E": {(): 0.002},
         "A": {(True, True): 0.95, (True, False): 0.94, (False, True): 0.29, (False, False): 0.001},
         "J": {(True,): 0.90, (False,): 0.05}, "M": {(True,): 0.70, (False,): 0.01}}

def prob(var, value, world):
    key = tuple(world[p] for p in parents[var])
    p = table[var][key]
    return p if value else 1 - p

def joint(world):
    # chain rule shortened by the network: multiply P(x | parents(x)) for every variable
    result = 1
    for var in ["B", "E", "A", "J", "M"]:
        result = result * prob(var, world[var], world)
    return result

w = {"B": False, "E": False, "A": True, "J": True, "M": True}
print("P(j, m, a, not b, not e) =", round(joint(w), 6))

count = 0
for var in parents:
    count = count + 2 ** len(parents[var])
print("numbers in the network:", count, " numbers in the full joint:", 2 ** 5 - 1)
''')

K.code('dsep', r'''
# d-separation by the moral ancestral graph (Lauritzen and others, 1990):
# X and Y are d-separated by Z exactly when they are not connected in the graph built below.
parents = {"Cloudy": [], "Sprinkler": ["Cloudy"], "Rain": ["Cloudy"], "WetGrass": ["Sprinkler", "Rain"]}

def d_separated(x, y, z):
    # 1. keep only x, y, z and their ancestors
    keep = [x, y] + z
    i = 0
    while i < len(keep):
        for p in parents[keep[i]]:
            if p not in keep:
                keep.append(p)
        i = i + 1
    # 2. moralise: join each child to its parents, and the parents of a child to each other
    edges = []
    for v in keep:
        ps = parents[v]
        for p in ps:
            edges.append((p, v))
        for a in ps:
            for b in ps:
                if a < b:
                    edges.append((a, b))
    # 3. delete the evidence z, then look for a path from x to y
    seen = [x]
    todo = [x]
    while todo:
        u = todo.pop()
        for a, b in edges:
            for s, t in [(a, b), (b, a)]:
                if s == u and t not in z and t not in seen:
                    seen.append(t)
                    todo.append(t)
    return y not in seen

print("Sprinkler, Rain | Cloudy:", d_separated("Sprinkler", "Rain", ["Cloudy"]))
print("Sprinkler, Rain | Cloudy, WetGrass:", d_separated("Sprinkler", "Rain", ["Cloudy", "WetGrass"]))
print("Cloudy, WetGrass | Sprinkler, Rain:", d_separated("Cloudy", "WetGrass", ["Sprinkler", "Rain"]))
''')

K.code('mrf', r'''
# The misconception Markov network of Koller and Friedman (2009): A - B - C - D - A.
# phi[(X, Y)][(x, y)] scores how well x and y fit together.
phi = {("A", "B"): {(0, 0): 30, (0, 1): 5, (1, 0): 1, (1, 1): 10},
       ("B", "C"): {(0, 0): 100, (0, 1): 1, (1, 0): 1, (1, 1): 100},
       ("C", "D"): {(0, 0): 1, (0, 1): 100, (1, 0): 100, (1, 1): 1},
       ("D", "A"): {(0, 0): 100, (0, 1): 1, (1, 0): 1, (1, 1): 100}}

Z = 0
best, best_world = 0, None
for a in [0, 1]:
    for b in [0, 1]:
        for c in [0, 1]:
            for d in [0, 1]:
                w = {"A": a, "B": b, "C": c, "D": d}
                score = 1
                for (x, y), f in phi.items():
                    score = score * f[(w[x], w[y])]
                Z = Z + score
                if score > best:
                    best, best_world = score, (a, b, c, d)
print("Z =", Z)
print("most likely world (A, B, C, D) =", best_world, " P =", round(best / Z, 3))
''')

K.lesson('bn', 'Bayesian networks: a graph plus small tables', f'''
{src('Pearl (1988), Probabilistic Reasoning in Intelligent Systems, and AIMA 3rd ed., sections 14.1 and 14.2 (4th ed., 13.1 and 13.2). The burglary network is AIMA figure 14.2.')}
{wwh('A <b>Bayesian network</b> is a directed graph with no cycles. Each node is a random variable. An arrow X → Y means X directly influences Y. Each node has a conditional probability table (CPT) giving P(node | its parents).',
     'The full joint has 2ⁿ entries. Most variables only depend directly on a few others. The network stores only those local tables, so a model of hundreds of variables fits in a few thousand numbers, and experts can read and check it.',
     'The joint probability of any world is the product of one entry from each table: P(x₁, ..., xₙ) = Π P(xᵢ | parents(Xᵢ)). This is the chain rule, with each condition cut down to the parents.')}
{fxs(fx('Network semantics', 'P(x₁, ..., xₙ) = Π over i of P(xᵢ | parents(Xᵢ))', 'One table entry per variable.', key=True),
     fx('Size of a CPT', 'a true or false node with k true or false parents needs 2ᵏ numbers', 'One number per row, since P(false) = 1 − P(true).'),
     fx('Size of the network', 'Σ over nodes of 2^(number of parents)', 'n nodes with at most k parents: at most n 2ᵏ, against 2ⁿ − 1.'))}
{table(['Node', 'Parents', 'Table (P of true)'], [
    ['Burglary', 'none', '0.001'], ['Earthquake', 'none', '0.002'],
    ['Alarm', 'Burglary, Earthquake', 'b e: 0.95, b ¬e: 0.94, ¬b e: 0.29, ¬b ¬e: 0.001'],
    ['JohnCalls', 'Alarm', 'a: 0.90, ¬a: 0.05'], ['MaryCalls', 'Alarm', 'a: 0.70, ¬a: 0.01']])}
{code('alarm')}
{steps('Worked example: P(j, m, a, ¬b, ¬e)', [
    'Take one entry from each table: P(j | a) = 0.90, P(m | a) = 0.70, P(a | ¬b, ¬e) = 0.001.',
    'P(¬b) = 0.999, P(¬e) = 0.998.',
    'Multiply: 0.90 × 0.70 × 0.001 × 0.999 × 0.998.',
    eq('≈ 0.000628')])}
{note('Build a network in causal order: causes first, then effects. The diagnostic order (MaryCalls, JohnCalls, Alarm, Burglary, Earthquake) is still correct but needs more arrows and harder numbers, such as P(Earthquake | Burglary, Alarm).', 'tip')}
''', kw=['Bayesian network', 'belief network', 'CPT', 'directed acyclic graph', 'chain rule', 'compactness', 'causal order'])

K.lesson('dsepl', 'Reading independence from the graph: d-separation', f'''
{src('Pearl (1988), Geiger, Verma and Pearl (1990), and AIMA 3rd ed., section 14.2.2.')}
{wwh('The graph says which variables are conditionally independent. Each node is independent of its non descendants given its parents. More generally, X and Y are independent given Z when Z <b>d-separates</b> them: every path between them is blocked.',
     'With d-separation we can see from the drawing alone which evidence matters for a query. Inference programs use it to skip whole parts of the network.',
     'Check each path three nodes at a time. A chain A → M → B or a fork A ← M → B is blocked when M is observed. A collider A → M ← B is blocked unless M or one of its descendants is observed.')}
{table(['Pattern', 'Example', 'Blocked when', 'Plain meaning'], [
    ['Chain A → M → B', 'Burglary → Alarm → JohnCalls', 'M is observed', 'once you know the alarm rang, the burglary tells nothing more about John'],
    ['Fork A ← M → B', 'JohnCalls ← Alarm → MaryCalls', 'M is observed', 'both calls depend only on the alarm'],
    ['Collider A → M ← B', 'Burglary → Alarm ← Earthquake', 'M and all its descendants are not observed', 'two causes are independent until we see their common effect (explaining away)']])}
{viz('dsep')}
{fxs(fx('Markov blanket', 'parents, children, and the children’s other parents', 'Given its blanket, a node is independent of every other node.', key=True))}
{code('dsep')}
{note('Explaining away: if the alarm rang, a burglary is likely. If we then learn an earthquake happened, the burglary becomes less likely, because the earthquake already explains the alarm. The two causes were independent before we saw the alarm.', 'tip')}
''', kw=['d-separation', 'chain', 'fork', 'collider', 'explaining away', 'Markov blanket', 'local Markov property'])

K.lesson('cpts', 'Compact tables: deterministic nodes, noisy OR and continuous variables', f'''
{src('AIMA 3rd ed., section 14.3, and Pearl (1988) for noisy OR.')}
{wwh('Some CPTs follow a simple rule, so they need far fewer than 2ᵏ numbers. A <b>noisy OR</b> node has a separate chance qᵢ that cause i fails to produce the effect, and the failures are independent.',
     'A disease with 10 possible causes needs 1024 rows in a full CPT. Noisy OR needs 10 numbers, which an expert can actually give.',
     'The effect is false only if every present cause fails: P(¬effect | present causes) = product of their qᵢ. Deterministic nodes are fixed functions of their parents. Continuous nodes use formulas, such as a linear Gaussian whose mean is a linear function of the parents.')}
{fxs(fx('Noisy OR', 'P(¬x | parents) = Π over true parents j of q_j', 'q_j is the chance that cause j alone fails.', key=True),
     fx('Linear Gaussian', 'P(x | h) = N(x | mean a h + b, variance σ²)', 'A continuous child of a continuous parent h.'))}
{steps('Worked example: fever with q_cold = 0.6, q_flu = 0.2, q_malaria = 0.1 (AIMA)', [
    'Cold and flu present, no malaria.',
    'P(¬fever) = 0.6 × 0.2 = 0.12.',
    eq('P(fever | cold, flu, ¬malaria) = 1 − 0.12 = 0.88')])}
''', kw=['noisy OR', 'deterministic node', 'linear Gaussian', 'hybrid network', 'canonical distribution'])

K.lesson('undirected', 'Undirected models: Markov networks', f'''
{src('Kindermann and Snell (1980), Koller and Friedman (2009), Probabilistic Graphical Models, chapter 4 (the misconception example), and AIMA 4th ed., section 13.2.')}
{wwh('A <b>Markov network</b> (Markov random field) is an undirected graph. Each clique (a set of nodes all joined to each other) has a <b>factor</b> φ, a table of non negative numbers that scores how well the values fit together.',
     'Some relations have no direction: neighbouring pixels in an image tend to share a colour, friends tend to share opinions. Forcing arrows on them gives the wrong independencies. Undirected models state them directly.',
     'Multiply the factors of a world to get its score. Divide by the partition function Z, the sum of the scores of all worlds, to get a probability. Two sets of nodes are independent given S when every path between them passes through S.')}
{fxs(fx('Gibbs distribution', 'P(x) = (1 ÷ Z) Π over cliques c of φ_c(x_c)', 'Factors need not add up to 1.', key=True),
     fx('Partition function', 'Z = Σ over all worlds x of Π φ_c(x_c)', 'A sum with 2ⁿ terms: computing it is the hard part.'),
     fx('Hammersley Clifford theorem', 'a positive distribution has the independencies of the graph exactly when it factorises over the cliques', 'Links the graph to the formula.'),
     fx('Log linear (energy) form', 'P(x) = (1 ÷ Z) exp(Σ wᵢ fᵢ(x))', 'Used by conditional random fields and Boltzmann machines.'))}
{viz('markovnet')}
{code('mrf')}
{table(['', 'Bayesian network (directed)', 'Markov network (undirected)'], [
    ['Parts', 'CPTs P(X | parents)', 'factors φ on cliques'],
    ['Normalised', 'each CPT row adds up to 1, so the product is a probability', 'only after dividing by Z'],
    ['Independence test', 'd-separation', 'plain graph separation'],
    ['Can express', 'explaining away (colliders)', 'cycles of mutual influence, such as A - B - C - D - A'],
    ['Learning the numbers', 'counting, one table at a time', 'needs Z, so iterative methods']])}
{note('To turn a Bayesian network into a Markov network, <b>moralise</b> it: join the parents of each child (they "marry"), then drop the arrow heads. The result may lose some independencies, such as Burglary ⫫ Earthquake.', 'tip')}
''', kw=['Markov network', 'Markov random field', 'undirected model', 'factor', 'clique', 'partition function', 'Hammersley Clifford', 'moralisation', 'Gibbs distribution'])

K.lesson('maths', 'The maths: counting parameters and checking independence', f'''
{fxs(
    fx('Parameters with at most k parents', 'n 2ᵏ, against 2ⁿ − 1 for the full joint', 'n = 30, k = 5: 960 against about 1.07 × 10⁹.', key=True),
    fx('Local Markov property', 'X ⫫ NonDescendants(X) | Parents(X)', 'Equivalent to the product formula for a Bayesian network.'),
    fx('Markov blanket property', 'P(X | everything else) = P(X | MB(X)) ∝ P(X | parents) × Π over children Y of P(y | parents(Y))', 'Used by Gibbs sampling in chapter 9.3.'),
    fx('Moral ancestral graph test', 'X ⫫ Y | Z exactly when X and Y are not joined in the moralised graph of the ancestors of X, Y and Z, after removing Z', 'Lauritzen and others, 1990. This is the algorithm in the code above.'))}
{steps('Worked example: P(Cloudy, ¬Sprinkler, Rain, WetGrass) in the sprinkler network', [
    'P(Cloudy) = 0.5.',
    'P(¬Sprinkler | Cloudy) = 1 − 0.1 = 0.9. P(Rain | Cloudy) = 0.8.',
    'P(WetGrass | ¬Sprinkler, Rain) = 0.9.',
    eq('0.5 × 0.9 × 0.8 × 0.9 = 0.324')])}
{steps('Worked example: Z for the chain A - B - C where each factor gives 4 to equal values and 1 to different values', [
    'Worlds 000 and 111 score 4 × 4 = 16 each: 32.',
    'Worlds with one disagreement (001, 011, 100, 110) score 4 × 1 = 4 each: 16.',
    'Worlds 010 and 101 disagree twice and score 1 each: 2.',
    eq('Z = 32 + 16 + 2 = 50')])}
''', kw=['parameter count', 'local Markov property', 'Markov blanket', 'moral graph', 'partition function example'])

K.lesson('compare', 'Graphical models compared', f'''
{versus('Choosing a model for uncertain knowledge', ['', 'Full joint table', 'Naive Bayes', 'Bayesian network', 'Markov network', 'Factor graph'], [
    ['Structure', 'none', 'one cause, independent effects', 'directed graph, no cycles', 'undirected graph', 'variables joined to factors'],
    ['Size', '2ⁿ − 1', '2n + 1', 'Σ 2^(parents)', 'Σ clique table sizes', 'Σ factor table sizes'],
    ['Strength', 'answers anything', 'tiny and fast', 'causal, readable, easy to learn from counts', 'symmetric relations, images, text labels', 'one form for both directed and undirected models, used by message passing'],
    ['Weakness', 'exponential size', 'ignores links between effects', 'cannot show some symmetric dependencies', 'Z is hard, numbers are hard to read', 'less intuitive for experts']],
    'use a Bayesian network when causes and effects are clear, a Markov network for symmetric relations, and a factor graph inside inference code.')}
{scene('Bayesian networks in real use', '<p>Microsoft’s Windows printer troubleshooter (1990s) used a Bayesian network to pick the next question to ask. The Pathfinder system (Heckerman, 1991) diagnosed lymph node diseases at expert level. The CTBT monitoring system NET-VISA (Arora, Russell and Sudderth, 2013), which detects nuclear tests from seismic signals, is a large probabilistic model of this family. Image segmentation and part of speech tagging used Markov random fields and conditional random fields (Lafferty, McCallum and Pereira, 2001).</p>')}
''', kw=['comparison', 'factor graph', 'conditional random field', 'Pathfinder', 'NET-VISA', 'troubleshooter'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Draw arrows from causes to effects, and for each effect write how likely it is for each mix of its causes. The drawing tells you what can affect what.</p>',
    '<p>A Bayesian network is a DAG with CPTs, and the joint is the product of the CPT entries. d-separation (chain, fork, collider) reads independence from the graph. Markov networks use clique factors and Z.</p>',
    '<p>I-maps and perfect maps: some distributions have no perfect directed map and some no perfect undirected map. Markov equivalence: graphs with the same skeleton and the same colliders (v-structures) encode the same independencies, so data alone cannot always fix arrow directions.</p>',
    '<p>Research: learning the structure of a network from data (score based search, the PC algorithm), deep generative models seen as graphical models (variational autoencoders), and relational models (Markov logic networks) that mix first order logic with Markov networks.</p>')}
''', kw=['I-map', 'Markov equivalence', 'v-structure', 'structure learning', 'Markov logic'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A Bayesian network is a directed graph with no cycles plus a CPT per node. P(x₁, ..., xₙ) = Π P(xᵢ | parents(Xᵢ)).',
    'It needs Σ 2^(parents) numbers instead of 2ⁿ − 1. The burglary network needs 10 instead of 31.',
    'd-separation: chains and forks are blocked by observing the middle, colliders are opened by observing the middle or a descendant.',
    'Noisy OR, deterministic and linear Gaussian nodes make tables even smaller.',
    'Markov networks use clique factors: P(x) = (1 ÷ Z) Π φ_c(x_c). Z is a sum over all worlds, which is what makes them hard.'],
    'chapter 9.3 computes answers from these models: exact variable elimination and approximate sampling.')}
{nbcard('bayesian-networks', 'Compute a joint entry of the burglary network, test d-separation with the moral ancestral graph and compute Z of a Markov network, then write joint probability, parameter counting, Markov blankets and d-separation yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'An arrow X → Y in a Bayesian network means', ['Y causes X', 'X directly influences Y, and Y’s table depends on X', 'X and Y are independent', 'X happens before Y in time, always'], 1,
       'Parents and children.', 'The CPT of Y has a row for each value of X.')
K.quiz('e', 'A true or false node with 3 true or false parents needs how many numbers in its CPT?', ['3', '6', '8', '16'], 2,
       '2³ rows.', 'One number per row.')
K.quiz('e', 'The joint probability of a world in a Bayesian network is', ['the sum of the CPT entries', 'the product of one CPT entry per node', 'the largest CPT entry', 'always 1 ÷ 2ⁿ'], 1,
       'Chain rule.', 'Π P(xᵢ | parents).')
K.quiz('e', 'How many numbers does the burglary network need?', ['5', '10', '31', '32'], 1,
       '1 + 1 + 4 + 2 + 2.', 'The full joint needs 31.')
K.quiz('m', 'In Burglary → Alarm ← Earthquake, with nothing observed, Burglary and Earthquake are', ['dependent', 'independent', 'the same variable', 'both certain'], 1,
       'Collider.', 'An unobserved collider blocks the path.')
K.quiz('m', 'After observing JohnCalls, Burglary and Earthquake are', ['still independent', 'dependent, because JohnCalls is a descendant of the collider Alarm', 'impossible', 'both true'], 1,
       'Descendants open colliders.', 'Explaining away.')
K.quiz('m', 'The Markov blanket of a node is', ['its parents only', 'its children only', 'its parents, children and children’s other parents', 'every node'], 2,
       'Three groups.', 'Given the blanket, the node is independent of the rest.')
K.quiz('m', 'In a Markov network, Z is', ['the number of nodes', 'the sum of the factor products over all worlds', 'the largest factor', 'the evidence'], 1,
       'Partition function.', 'Divide by Z to get probabilities.')
K.quiz('h', 'Noisy OR with q₁ = 0.5, q₂ = 0.4: P(effect | both causes) is', ['0.2', '0.8', '0.9', '0.1'], 1,
       'P(¬effect) = q₁ q₂.', '1 − 0.5 × 0.4 = 0.8.')
K.quiz('h', 'Moralising Burglary → Alarm ← Earthquake gives', ['no edges', 'Burglary - Alarm, Earthquake - Alarm and Burglary - Earthquake', 'only Burglary - Earthquake', 'arrows reversed'], 1,
       'Marry the parents, drop the arrow heads.', 'The new edge Burglary - Earthquake loses their independence.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: which pair of graphs encodes the same independencies?', ['A → B → C and A → B ← C', 'A → B → C and A ← B ← C', 'A → B ← C and A ← B → C', 'none of these'], 1,
       'Same skeleton, same colliders.', 'Chains in either direction and the fork are Markov equivalent. Only the collider differs.')
K.quiz('x', 'In the style of a Stanford CS228 exam: a 4 cycle A - B - C - D - A of pairwise relations has', ['a perfect directed map', 'no Bayesian network that encodes exactly its independencies', 'no Markov network', 'only one world'], 1,
       'A ⫫ C | B, D and B ⫫ D | A, C together.', 'Any directed version adds a collider or loses one of them, which is why undirected models are needed.')

# ---------------------------------------------------------------- calc
K.calc('e', 'Numbers in the burglary network.', '10', 'Sum of 2^(parents).',
       ['Burglary 1, Earthquake 1.', 'Alarm 2² = 4, JohnCalls 2, MaryCalls 2.', eq('1 + 1 + 4 + 2 + 2 = 10')], check=10)
K.calc('e', 'Free numbers in the full joint of the 5 burglary variables.', '31', '2⁵ − 1.',
       ['2⁵ = 32 worlds.', 'They add up to 1.', eq('31')], check=31)
K.calc('e', 'Size of the Markov blanket of Alarm in the burglary network.', '4', 'Parents, children, children’s other parents.',
       ['Parents: Burglary, Earthquake.', 'Children: JohnCalls, MaryCalls. They have no other parents.', eq('4')], check=4)
K.calc('m', 'P(j, m, a, ¬b, ¬e) in the burglary network, to 6 decimals.', '0.000628', 'Multiply one entry per node.',
       ['0.90 × 0.70 = 0.63.', '0.63 × 0.001 = 0.00063.', eq('0.00063 × 0.999 × 0.998 ≈ 0.000628')], check=0.000628, tol=0.000001)
K.calc('m', 'A network of 30 true or false nodes, each with exactly 5 parents (the first nodes have fewer, ignore that). How many numbers?', '960', '30 × 2⁵.',
       ['Each node: 2⁵ = 32 numbers.', '30 nodes.', eq('30 × 32 = 960')], check=960)
K.calc('m', 'P(Cloudy, ¬Sprinkler, Rain, WetGrass) in the sprinkler network.', '0.324', '0.5 × 0.9 × 0.8 × 0.9.',
       ['0.5 × 0.9 = 0.45.', '0.45 × 0.8 = 0.36.', eq('0.36 × 0.9 = 0.324')], check=0.324, tol=0.0005)
K.calc('m', 'Noisy OR: P(fever | cold, flu, ¬malaria) with q_cold = 0.6, q_flu = 0.2.', '0.88', '1 − 0.6 × 0.2.',
       ['Only the present causes count.', 'P(¬fever) = 0.12.', eq('0.88')], check=0.88, tol=0.0005)
K.calc('h', 'Noisy OR: P(fever | cold, flu, malaria) with q = 0.6, 0.2, 0.1.', '0.988', '1 − 0.6 × 0.2 × 0.1.',
       ['P(¬fever) = 0.6 × 0.2 × 0.1 = 0.012.', 'All three causes fail together with that chance.', eq('1 − 0.012 = 0.988')], check=0.988, tol=0.0005)
K.calc('h', 'Z for the chain A - B - C with factors φ(equal) = 4, φ(different) = 1 on both edges.', '50', '8 worlds.',
       ['000 and 111: 16 each.', '001, 011, 100, 110: 4 each. 010 and 101: 1 each.', eq('32 + 16 + 2 = 50')], check=50)
K.calc('x', 'In the misconception network (Z = 7,201,840), the world A = 0, B = 1, C = 1, D = 0 scores 5 × 100 × 100 × 100. Its probability to 3 decimals?', '0.694', '5,000,000 ÷ 7,201,840.',
       ['Score = 5,000,000.', 'Divide by Z.', eq('≈ 0.694')], check=0.694, tol=0.001)

# ---------------------------------------------------------------- assignments
NET = '''PARENTS = {"B": [], "E": [], "A": ["B", "E"], "J": ["A"], "M": ["A"]}
TABLE = {"B": {(): 0.001}, "E": {(): 0.002},
         "A": {(True, True): 0.95, (True, False): 0.94, (False, True): 0.29, (False, False): 0.001},
         "J": {(True,): 0.90, (False,): 0.05}, "M": {(True,): 0.70, (False,): 0.01}}
'''
K.assign('jointbn', 'e', 'The probability of one world',
         '<p>Write <code>joint(world)</code> for the burglary network. world maps "B", "E", "A", "J", "M" to True or False. Multiply P(x | parents) over all five variables.</p>',
         NET + '''
def joint(world):
    # your code here
    pass
''', [("round(joint({'B': False, 'E': False, 'A': True, 'J': True, 'M': True}), 6)", 0.000628),
      ("round(joint({'B': False, 'E': False, 'A': False, 'J': False, 'M': False}), 4)", 0.9367),
      ("round(joint({'B': True, 'E': True, 'A': True, 'J': True, 'M': True}) * 10 ** 6, 3)", 1.197)],
         NET + '''
def joint(world):
    result = 1
    for var in PARENTS:
        key = tuple(world[p] for p in PARENTS[var])
        p = TABLE[var][key]
        if world[var]:
            result = result * p
        else:
            result = result * (1 - p)
    return result
''', 'For each variable, build the key from the parents’ values, look up P(true), and use 1 − p when the variable is false.', '<p>Test 2: nothing happens, 0.999 × 0.998 × 0.999 × 0.95 × 0.99 ≈ 0.9367.</p>')
K.assign('params', 'e', 'Count the numbers a network needs',
         '<p>Write <code>count_params(parents)</code> for a network of true or false nodes: the sum over nodes of 2 to the power of the number of parents.</p>',
         '''
def count_params(parents):
    # your code here
    pass
''', [("count_params({'B': [], 'E': [], 'A': ['B', 'E'], 'J': ['A'], 'M': ['A']})", 10),
      ("count_params({'C': [], 'S': ['C'], 'R': ['C'], 'W': ['S', 'R']})", 9),
      ("count_params({'X': []})", 1),
      ("count_params({'A': [], 'B': [], 'C': [], 'D': ['A', 'B', 'C']})", 11)],
         '''
def count_params(parents):
    total = 0
    for node in parents:
        total = total + 2 ** len(parents[node])
    return total
''', 'Loop over the nodes and add 2 ** len(parents[node]).', '<p>Test 2 is the sprinkler network: 1 + 2 + 2 + 4 = 9.</p>')
K.assign('blanket', 'm', 'The Markov blanket',
         '<p>Write <code>blanket(parents, x)</code> that returns the sorted list of nodes in the Markov blanket of x: its parents, its children, and the other parents of its children.</p>',
         '''
def blanket(parents, x):
    # your code here
    pass
''', [("blanket({'B': [], 'E': [], 'A': ['B', 'E'], 'J': ['A'], 'M': ['A']}, 'A')", ['B', 'E', 'J', 'M']),
      ("blanket({'B': [], 'E': [], 'A': ['B', 'E'], 'J': ['A'], 'M': ['A']}, 'B')", ['A', 'E']),
      ("blanket({'C': [], 'S': ['C'], 'R': ['C'], 'W': ['S', 'R']}, 'S')", ['C', 'R', 'W']),
      ("blanket({'C': [], 'S': ['C'], 'R': ['C'], 'W': ['S', 'R']}, 'W')", ['R', 'S'])],
         '''
def blanket(parents, x):
    out = []
    for p in parents[x]:
        out.append(p)
    for child in parents:
        if x in parents[child]:
            if child not in out:
                out.append(child)
            for p in parents[child]:
                if p != x and p not in out:
                    out.append(p)
    return sorted(out)
''', 'A child is any node that lists x among its parents.', '<p>Test 2: Earthquake is in the blanket of Burglary because both are parents of Alarm.</p>')
K.assign('dsep', 'h', 'd-separation with the moral ancestral graph',
         '<p>Write <code>d_separated(parents, x, y, z)</code>: keep x, y, the list z and all their ancestors, moralise (join each node to its parents and parents of a common child to each other), delete z, and return True when no path joins x and y.</p>',
         '''
def d_separated(parents, x, y, z):
    # your code here
    pass
''', [("d_separated({'B': [], 'E': [], 'A': ['B', 'E'], 'J': ['A'], 'M': ['A']}, 'B', 'E', [])", True),
      ("d_separated({'B': [], 'E': [], 'A': ['B', 'E'], 'J': ['A'], 'M': ['A']}, 'B', 'E', ['J'])", False),
      ("d_separated({'B': [], 'E': [], 'A': ['B', 'E'], 'J': ['A'], 'M': ['A']}, 'J', 'M', ['A'])", True),
      ("d_separated({'C': [], 'S': ['C'], 'R': ['C'], 'W': ['S', 'R']}, 'S', 'R', ['C', 'W'])", False)],
         '''
def d_separated(parents, x, y, z):
    keep = [x, y] + z
    i = 0
    while i < len(keep):
        for p in parents[keep[i]]:
            if p not in keep:
                keep.append(p)
        i = i + 1
    edges = []
    for v in keep:
        for p in parents[v]:
            edges.append((p, v))
        for a in parents[v]:
            for b in parents[v]:
                if a < b:
                    edges.append((a, b))
    seen = [x]
    todo = [x]
    while todo:
        u = todo.pop()
        for a, b in edges:
            for s, t in [(a, b), (b, a)]:
                if s == u and t not in z and t not in seen:
                    seen.append(t)
                    todo.append(t)
    return y not in seen
''', 'Grow the list of ancestors first. Then build the moral edges, and search from x without stepping on any node in z.', '<p>Test 2: J is a descendant of the collider A, so A and J are kept, B and E get married, and B reaches E.</p>')

K.must('Bayesian network', 'DAG + CPT per node. P(x₁..xₙ) = Π P(xᵢ | parents). Size Σ 2^(parents). Burglary: 10 vs 31.')
K.must('d-separation', 'Chain and fork blocked if the middle is observed. Collider blocked unless the middle or a descendant is observed.')
K.must('Markov blanket', 'Parents, children, children’s other parents. Given it, a node is independent of all others.')
K.must('Noisy OR', 'P(¬x | causes) = Π q_j over present causes. n numbers instead of 2ⁿ.')
K.must('Markov network', 'P(x) = (1 ÷ Z) Π φ_c(x_c), Z = Σ_x Π φ_c. Separation in the graph gives independence. Moralise a BN: marry parents, drop arrows.')
K.must('Key numbers', 'P(j, m, a, ¬b, ¬e) ≈ 0.000628. Misconception network Z = 7,201,840.')

T = K.topic(
    slug='bayesian-networks', topic='bayesian-networks', step=STEP9,
    title='Bayesian networks and Markov networks', short='Bayesian networks', badge='9.2', minutes=55,
    lead='Draw uncertain knowledge as a graph. Directed Bayesian networks store small tables P(node | parents), d-separation reads independence from the arrows, and undirected Markov networks score worlds with factors and a partition function.',
    desc='Bayesian network semantics, CPTs, the chain rule, compactness and causal order, d-separation with chains, forks and colliders, explaining away, the Markov blanket, noisy OR and linear Gaussian nodes, Markov networks with clique factors, the partition function, the Hammersley Clifford theorem, moralisation, Markov equivalence, and directed versus undirected models.',
    summary='Directed and undirected graphical models: CPTs, d-separation, Markov blankets, factors and Z.',
    keywords=['Bayesian network', 'CPT', 'd-separation', 'explaining away', 'Markov blanket', 'noisy OR', 'Markov network', 'partition function', 'directed model', 'undirected model'],
    recap='<p>Joint = Π P(x | parents). d-separation reads independence. Markov networks: product of factors divided by Z.</p>',
    nb={'alarm': 'A joint entry of the burglary network', 'dsep': 'd-separation by the moral ancestral graph', 'mrf': 'The partition function of the misconception network'})
