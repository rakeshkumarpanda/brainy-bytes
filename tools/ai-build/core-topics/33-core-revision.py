# Chapter 11.2: exam revision for Core AI. One place to revise the whole section, organised by the kind of exam:
# school and first year questions, university semester and IIT course exams, GATE and NPTEL style papers, and proofs in
# the style of MIT, Berkeley, Stanford, CMU and IISc. Every question is an original practice question written in the
# style of that tier, not a copy of a past paper. Every number was checked with Python before it was written down.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import src

K = Kit()
STEP11 = (11, 'Challenge and revision', 'cai-review', 'Bring it all together: the hardest exam style problems across Core AI, then a revision guide from school level to top universities.', 'All levels')

K.code('drill', r'''
# Exam drill: Bayes rule for a test result. Type the prior, the hit rate and the false alarm rate.
prior, hit, false_alarm = [float(x) for x in input("prior, P(+ | ill), P(+ | healthy): ").split()]
p_pos = hit * prior + false_alarm * (1 - prior)          # total probability
print("P(+)          =", round(p_pos, 4))
print("P(ill | +)    =", round(hit * prior / p_pos, 4))
p_neg = 1 - p_pos
print("P(ill | -)    =", round((1 - hit) * prior / p_neg, 4))
''', stdin='0.01 0.9 0.1\n')

K.code('ucsastar', r'''
# Exam drill: uniform cost search and A* by hand on one small graph. The frontier is printed before each expansion.
import heapq
edges = {'S': [('A', 1), ('B', 5)], 'A': [('B', 2), ('G', 6)], 'B': [('G', 1)], 'G': []}
h = {'S': 3, 'A': 3, 'B': 1, 'G': 0}

def search(use_h):
    frontier = [(h['S'] if use_h else 0, 0, 'S', 'S')]
    done = set()
    while frontier:
        print("  frontier:", sorted((f, n) for f, g, n, p in frontier))
        f, g, node, path = heapq.heappop(frontier)
        if node in done:
            continue
        if node == 'G':
            return path, g
        done.add(node)
        for nxt, cost in edges[node]:
            if nxt not in done:
                heapq.heappush(frontier, (g + cost + (h[nxt] if use_h else 0), g + cost, nxt, path + nxt))

print("UCS:", search(False))
print("A*: ", search(True))
''')

K.lesson('map', 'How Core AI is examined', f'''
{src('Original practice questions written in the style of each exam tier. None is copied from a real past paper. The topics follow AIMA 3rd ed. chapters 3 to 21, the uploaded slides on search, CSPs and games, and the AI part of the GATE Data Science and AI syllabus (search, logic, and reasoning under uncertainty with conditional independence, variable elimination and sampling). Every number was checked with Python.')}
<p>This chapter is for the week before an exam. It does not teach new material. It shows the shapes questions take at each level, with worked answers, and points back to the chapter where each idea is taught.</p>
{table(['Tier', 'Typical format', 'What earns the marks', 'Where to practise'], [
    ['School and first year', 'Short answers, small trees, simple chances', 'A clear definition with an example, careful counting', 'Lesson 2'],
    ['University semester and IIT course exams', 'Run an algorithm by hand on a small graph, net or MDP', 'The frontier or table after every step, the answer stated with its meaning', 'Lesson 3'],
    ['GATE and NPTEL style papers', 'Multiple choice, multiple select and numerical answer type', 'Speed, quick checks that rule out options, exact rounding', 'Lesson 4'],
    ['MIT, Berkeley, Stanford, CMU and IISc style', 'Proofs, derivations and critique of a method', 'Conditions named, a complete argument, when it breaks', 'Lesson 5']])}
<h3>The fifteen ideas examined most often</h3>
<ol>
<li>PEAS and the types of environment (chapter 1.1).</li>
<li>The five parts of a search problem and the four ways to judge a search (chapter 1.2).</li>
<li>BFS, UCS, DFS and IDS: completeness, optimality, time and memory (chapters 2.1 and 2.2).</li>
<li>A*: admissible and consistent heuristics, dominance, relaxed problems (chapters 3.1 and 3.2).</li>
<li>Hill climbing, simulated annealing and genetic algorithms (chapters 4.1 and 4.2).</li>
<li>CSP formulation, AC-3, backtracking with MRV, degree and LCV, forward checking (chapters 5.1 and 5.2).</li>
<li>Minimax, alpha beta and its best case, expectimax (chapters 6.1 to 6.3).</li>
<li>Entailment, truth tables, CNF and resolution (chapters 7.1 and 7.2).</li>
<li>Translating English to first order logic, unification, forward and backward chaining (chapters 7.3 and 7.4).</li>
<li>STRIPS actions, forward and backward planning, partial order planning and threats (chapters 8.1 to 8.3).</li>
<li>Bayes rule, marginalising and normalising (chapter 9.1).</li>
<li>Bayesian network structure, parameter counts and d-separation (chapter 9.2).</li>
<li>Inference by enumeration, variable elimination and sampling (chapter 9.3).</li>
<li>MDPs, the Bellman equation, value and policy iteration (chapter 10.1).</li>
<li>TD learning, Q-learning, SARSA and exploration (chapters 10.2 to 10.4).</li>
</ol>
''', kw=['exam pattern', 'revision', 'school', 'university exam', 'IIT', 'NPTEL', 'GATE', 'GATE DA', 'MIT', 'Berkeley', 'Stanford'])

K.lesson('school', 'Tier 1: school and first year', f'''
<p>Questions at this level check that you can describe an agent, follow a search order and work out a simple chance.</p>
{fxs(
    fx('Rows of a truth table', '2ⁿ', 'n symbols, each true or false.', key=True),
    fx('Nodes at depth d', 'bᵈ', 'Each node has b children.', key=True),
    fx('Chance of an event', 'P(A) = favourable cases ÷ all equally likely cases', 'Only when every case is equally likely.'))}
{steps('Question 1. Give the PEAS description of a robot vacuum cleaner.', [
    'Performance measure: how clean the floor is, the time taken and the power used.',
    'Environment: the rooms, the dirt, the furniture and the people.',
    'Actuators: wheels, brushes and the suction motor. Sensors: a dirt sensor, bump sensors and a camera.',
    'The environment is partially observable, stochastic and dynamic (chapter 1.1).'])}
{steps('Question 2. A tree has root A with children B and C. B has children D and E. C has child F. List the order in which BFS and DFS visit the nodes (left child first).', [
    'BFS goes level by level: A, then B and C, then D, E and F.',
    'DFS goes as deep as it can first: A, B, D, then back up to E, then C and F.',
    'BFS: A B C D E F. DFS: A B D E C F.'])}
{steps('Question 3. Two fair dice are thrown. What is the chance the total is 7?', [
    'There are 6 × 6 = 36 equally likely pairs.',
    'The pairs that give 7 are (1, 6), (2, 5), (3, 4), (4, 3), (5, 2) and (6, 1). That is 6 pairs.',
    eq('P = 6 ÷ 36 = 1 ÷ 6 ≈ 0.167')])}
{steps('Question 4. MAX moves first. Move 1 lets MIN choose 3 or 5. Move 2 lets MIN choose 2 or 9. Which move should MAX play?', [
    'MIN picks the smaller value: move 1 is worth min(3, 5) = 3, move 2 is worth min(2, 9) = 2.',
    'MAX picks the larger: max(3, 2) = 3.',
    'MAX plays move 1. The 9 looks tempting, but MIN would never allow it.'])}
{viz('gametree', mode='minimax', pat='mm2', b=2, leaves='3 5 2 9')}
{steps('Question 5. How many rows does a truth table for P, Q, R and S need?', [
    'Each symbol can be true or false.',
    '2 × 2 × 2 × 2.',
    eq('2⁴ = 16 rows')])}
''', kw=['PEAS', 'BFS order', 'DFS order', 'dice probability', 'minimax by hand', 'truth table rows', 'short answer'])

K.lesson('semester', 'Tier 2: university semester and IIT course exams', f'''
<p>Here the examiner gives a small graph, tree, net or MDP and asks you to run the algorithm by hand. Write the frontier or the table after every step.</p>
<h3>Question 6. UCS and A* on one graph</h3>
<p>Edges: S to A costs 1, S to B costs 5, A to B costs 2, A to G costs 6, B to G costs 1. Heuristic: h(S) = 3, h(A) = 3, h(B) = 1, h(G) = 0. Run UCS and A* and give the path and its cost.</p>
{steps('Model answer', [
    'UCS frontier (g values): S 0. Expand S: A 1, B 5. Expand A: B 3 (a cheaper way in), G 7. Expand B (3): G 4.',
    'UCS takes G out with cost 4. Path S, A, B, G.',
    'A* frontier (f = g + h): S 3. Expand S: A 4, B 6. Expand A: B 3 + 1 = 4, G 7. Expand B: G 4 + 0 = 4.',
    'A* also finds S, A, B, G with cost 4. Here h is consistent, so A* graph search is safe.',
    eq('both return S, A, B, G with cost 4')])}
{code('ucsastar')}
<h3>Question 7. Alpha beta on the tree of the slides</h3>
{steps('Leaves 2 3 5 9 0 1 7 5 under MAX, MIN, MAX. Find the root value and the pruned parts.', [
    'The first MAX node is max(2, 3) = 3, so the MIN node above it has β = 3.',
    'The next MAX node reads 5, which is at least β = 3. MIN will never let play reach it, so the 9 is pruned.',
    'The left MIN node is 3, so the root has α = 3. On the right, the first MAX node is max(0, 1) = 1, so that MIN node is at most 1.',
    'That is below α = 3, so the whole last MAX node (7 and 5) is pruned.',
    eq('root = 3, the same as plain minimax')])}
{viz('gametree', mode='ab', pat='mm3', b=2, leaves='2 3 5 9 0 1 7 5')}
<h3>Question 8. Bayes rule with a sum in the bottom</h3>
{steps('It rains on 20 percent of days. The grass is wet on 90 percent of rainy days and on 10 percent of dry days. The grass is wet. P(rain | wet)?', [
    'P(wet) = 0.9 × 0.2 + 0.1 × 0.8 = 0.18 + 0.08 = 0.26.',
    'P(rain | wet) = P(wet | rain) P(rain) ÷ P(wet) = 0.18 ÷ 0.26.',
    eq('≈ 0.692')])}
{code('drill')}
<h3>Question 9. One sweep of value iteration</h3>
{steps('The racing car MDP of chapter 10.1, γ = 0.9, starting from V = 0. Find V₁(cool) and V₁(warm).', [
    'Cool: slow gives 1. Fast gives 0.5 × 2 + 0.5 × 2 = 2. So V₁(cool) = 2.',
    'Warm: slow gives 1. Fast gives −10. So V₁(warm) = 1.',
    'The next sweep gives V₂(cool) = 3.35 and V₂(warm) = 2.35, and the values reach 15.5 and 14.5.',
    eq('V₁ = (2, 1)')])}
<p>The animation below runs the same kind of sweep on the 4 by 3 grid world of chapter 10.1, one sweep at a time.</p>
{viz('gridmdp', alg='vi')}
<h3>Question 10. Convert to CNF</h3>
{steps('Convert A ⇔ (B ∨ C) to conjunctive normal form.', [
    'Replace ⇔ by two implications: (A ⇒ B ∨ C) ∧ (B ∨ C ⇒ A).',
    'Replace each ⇒: (¬A ∨ B ∨ C) ∧ (¬(B ∨ C) ∨ A).',
    'Push ¬ inwards with De Morgan: ¬(B ∨ C) is ¬B ∧ ¬C. Then distribute ∨ over ∧.',
    eq('(¬A ∨ B ∨ C) ∧ (¬B ∨ A) ∧ (¬C ∨ A)')])}
''', kw=['UCS by hand', 'A* by hand', 'frontier table', 'alpha beta by hand', 'Bayes rule', 'value iteration sweep', 'CNF conversion'])

K.lesson('mcq', 'Tier 3: GATE and NPTEL style papers', f'''
<p>In these papers there is no partial credit and often a penalty for a wrong option. Learn the quick checks below and use them to rule out options before you compute.</p>
{table(['Quick check', 'Use it to'], [
    ['BFS and IDS are optimal only when every step costs the same', 'Reject "BFS is optimal" for unequal costs'],
    ['DFS is not complete on infinite or cyclic spaces without a check', 'Reject "DFS always finds a solution"'],
    ['The max of admissible heuristics is admissible, the sum usually is not', 'Settle multiple select questions on heuristics'],
    ['Alpha beta never changes the root value', 'Reject options where pruning gives a new answer'],
    ['A node is independent of its non descendants given its parents', 'Read independence straight off a net'],
    ['P(A ∨ B) = P(A) + P(B) − P(A ∧ B)', 'Avoid adding overlapping cases twice'],
    ['Rejection sampling keeps about N × P(e) samples', 'Spot why it fails for rare evidence'],
    ['Q-learning is off policy, SARSA is on policy', 'Answer the cliff walking question in one line']])}
{steps('Question 11 (numerical answer). BFS with b = 2 and the goal at depth 3. How many nodes are generated, not counting the root?', [
    'Depth 1 has 2, depth 2 has 4, depth 3 has 8.',
    '2 + 4 + 8.',
    eq('14')])}
{steps('Question 12 (multiple select). For the 8 puzzle, which are admissible? (a) misplaced tiles h₁ (b) Manhattan distance h₂ (c) max(h₁, h₂) (d) h₁ + h₂', [
    'h₁ and h₂ are both exact costs of relaxed problems, so they never overestimate. (a) and (b) are true.',
    'The max of two admissible values is still below the true cost. (c) is true.',
    'The sum can overestimate: one tile one step away counts 1 in each, giving 2 when the true cost is 1. (d) is false.',
    eq('answer: a, b, c')])}
{steps('Question 13 (numerical answer). P(A) = 0.5, P(B) = 0.4, P(A ∧ B) = 0.2. P(A ∨ B)?', [
    'P(A ∨ B) = P(A) + P(B) − P(A ∧ B).',
    '0.5 + 0.4 − 0.2.',
    eq('0.7')])}
{steps('Question 14 (numerical answer). The evidence has probability 0.01. About how many of 1,000 rejection samples are kept?', [
    'Each sample agrees with the evidence with chance 0.01.',
    '1,000 × 0.01.',
    eq('about 10. Likelihood weighting keeps all 1,000 and weights them instead')])}
{steps('Question 15 (multiple choice). In standard first order logic, is ∀x P(x) ⇒ ∃x P(x) valid?', [
    'Standard semantics needs at least one object in every model.',
    'If P holds for every object, it holds for that object, so some x has P(x).',
    eq('valid. It would fail only if empty domains were allowed')])}
{note('Round only at the very end. A numerical answer type key often has a narrow range such as 0.69 to 0.70.', 'exam')}
''', kw=['MCQ', 'MSQ', 'numerical answer type', 'GATE', 'GATE DA', 'NPTEL', 'quick checks', 'admissible heuristics', 'rejection sampling'])

K.lesson('derive', 'Tier 4: proofs, derivations and critique', f'''
<p>Exams in the style of MIT, Berkeley, Stanford, CMU and IISc reward a complete argument more than a final number. State the conditions, prove the claim, then say when it fails. Chapter 11.1 has five more proofs.</p>
<h3>Question 16. If h₁ and h₂ are consistent, show that h = max(h₁, h₂) is consistent.</h3>
{steps('Model answer', [
    'Take an edge from n to n′ with cost c. For each i, hᵢ(n) ≤ c + hᵢ(n′) ≤ c + h(n′), since h(n′) is at least hᵢ(n′).',
    'So both h₁(n) and h₂(n) are at most c + h(n′). Their max, h(n), is too.',
    'At the goal both are 0, so h(goal) = 0. So h is consistent, and it dominates each hᵢ, so A* expands no more nodes with it.'])}
<h3>Question 17. Show that the two parents of a collider are independent when nothing is observed.</h3>
{steps('Model answer', [
    'In the net B, E, A with A having parents B and E: P(b, e) = Σ over a of P(b) P(e) P(a | b, e).',
    'P(b) P(e) does not depend on a, so it comes out of the sum: P(b) P(e) Σ over a of P(a | b, e).',
    'The sum of a conditional distribution over its values is 1.',
    eq('P(b, e) = P(b) P(e), so B ⫫ E')])}
<h3>Question 18. Derive the value of a fixed policy in closed form.</h3>
{steps('Model answer', [
    'For a fixed policy π, the Bellman equation is linear: V(s) = R(s) + γ Σ P(s′ | s, π(s)) V(s′).',
    'In matrix form V = R + γ P_π V, so (I − γ P_π) V = R.',
    'For γ &lt; 1 the matrix I − γ P_π can be inverted, because every eigenvalue of P_π has size at most 1.',
    eq('V^π = (I − γ P_π)⁻¹ R, which policy iteration uses for exact evaluation')])}
<h3>Question 19. Show that UCS is optimal when every step cost is at least some ε &gt; 0.</h3>
{steps('Model answer', [
    'UCS takes nodes out in order of g. Every step adds at least ε, so g grows along any path, and only finitely many nodes have g below any bound.',
    'When the goal is taken out with cost C, every node with g &lt; C has already been taken out.',
    'Any cheaper path to the goal would have a node with g &lt; C on the frontier, which would come out first. So no cheaper path exists.',
    'With zero cost steps, UCS can loop forever on a zero cost cycle. That is why the ε condition is needed for completeness.'])}
<h3>Critique questions</h3>
<p>A critique question gives a claim and asks what is wrong. For example, "use greedy best first search because it is faster than A*". The answer: greedy search ignores the cost so far, so it is not optimal, and in tree search it can loop. Another favourite: "a Bayesian network arrow means cause". The answer: a network only encodes conditional independence. Many graphs give the same independences, and only a causal model with interventions (chapter 9.4) supports cause and effect.</p>
{note('In proofs, name each condition when you use it: consistency, positive step costs, definite clauses, a finite domain, γ &lt; 1. Examiners often ask what breaks when one fails.', 'exam')}
{ladder(
    '<p>At school you describe agents, follow BFS and DFS on a tree, count rows and cases, and pick a move by minimax.</p>',
    '<p>At university you run UCS, A*, alpha beta, AC-3, enumeration and value iteration by hand, writing the frontier or table after each step.</p>',
    '<p>In GATE and NPTEL papers you recognise the right fact fast, use quick checks to drop options and round only at the end.</p>',
    '<p>At research universities you prove optimality, consistency and independence results, derive closed forms such as V = (I − γP)⁻¹R, and critique methods by their conditions.</p>')}
''', kw=['proof', 'max of heuristics', 'collider independence', 'policy evaluation closed form', 'UCS optimality', 'critique', 'MIT', 'Berkeley', 'Stanford', 'CMU', 'IISc'])

K.lesson('sheet', 'Formula sheet and last minute checks', f'''
{table(['Topic', 'Formula or fact'], [
    ['BFS nodes, IDS nodes', 'b + b² + … + bᵈ, &nbsp; Σ (d + 1 − i) bⁱ'],
    ['Search memory', 'BFS O(bᵈ), DFS O(bm), IDS O(bd)'],
    ['A*', 'f(n) = g(n) + h(n), optimal with admissible h (tree) or consistent h (graph)'],
    ['Consistency', 'h(n) ≤ c(n, n′) + h(n′) and h(goal) = 0'],
    ['Effective branching factor', 'N + 1 = 1 + b* + (b*)² + … + (b*)ᵈ'],
    ['Simulated annealing', 'accept a worse move with probability e^(ΔE ÷ T)'],
    ['Tree CSP', 'O(n d²)'],
    ['Alpha beta best case', 'b^⌈d ÷ 2⌉ + b^⌊d ÷ 2⌋ − 1 leaves'],
    ['Resolution', 'from A ∨ ℓ and B ∨ ¬ℓ infer A ∨ B, prove KB ⊨ α by refuting KB ∧ ¬α'],
    ['STRIPS regression', 'new goal = (goal minus add list) plus preconditions'],
    ['Bayes rule', 'P(h | e) = P(e | h) P(h) ÷ P(e), &nbsp; P(e) = Σ P(e | h) P(h)'],
    ['Bayesian network', 'P(x₁, …, xₙ) = Π P(xᵢ | parents(Xᵢ))'],
    ['Adjustment for a cause', 'P(y | do(x)) = Σ over z of P(y | x, z) P(z)'],
    ['Bellman optimality', 'V(s) = max over a of Σ P(s′ | s, a) (R + γ V(s′))'],
    ['TD and Q-learning', 'V ← V + α (r + γ V(s′) − V), &nbsp; Q ← Q + α (r + γ max Q(s′, ·) − Q)'],
    ['REINFORCE', 'θ ← θ + α (G − b) ∇ log π(a | s)']])}
<h3>Ten mistakes that cost marks</h3>
<ol>
<li>Testing the goal when a node is added in UCS or A*, which can return a costlier path.</li>
<li>Calling an admissible heuristic safe for graph search without checking consistency.</li>
<li>Adding two admissible heuristics and calling the sum admissible.</li>
<li>Forgetting to put arcs back on the AC-3 queue after a domain shrinks.</li>
<li>Mixing up α and β in alpha beta: α is the value MAX can already guarantee on the path, β the value MIN can guarantee. Prune only when they cross.</li>
<li>Using forward chaining on clauses that are not definite clauses.</li>
<li>Unifying x with F(x) without the occurs check.</li>
<li>Forgetting the base rate in Bayes rule.</li>
<li>Saying a collider path is open with no evidence, or blocked when a descendant is observed.</li>
<li>Using max in a SARSA update, or the action actually taken in a Q-learning update.</li>
</ol>
''', kw=['formula sheet', 'common mistakes', 'last minute revision', 'A*', 'Bayes rule', 'Bellman', 'Q-learning'])

# ---------------------------------------------------------------- mock quiz
K.quiz('e', 'In PEAS, the S stands for', ['Search', 'Sensors', 'States', 'Strategy'], 1,
       'What the agent perceives with.', 'Performance, Environment, Actuators, Sensors.')
K.quiz('e', 'Which search uses a queue in first in, first out order?', ['DFS', 'BFS', 'A*', 'Hill climbing'], 1,
       'Level by level.', 'BFS takes the oldest node first.')
K.quiz('e', 'Two fair dice: the chance the total is 7 is', ['1/12', '1/6', '1/36', '7/36'], 1,
       'Count pairs.', '6 of 36 pairs.')
K.quiz('m', 'A* graph search is optimal if the heuristic is', ['admissible only', 'consistent', 'zero at the start', 'larger than the true cost'], 1,
       'Graph search closes nodes.', 'Consistency makes f non decreasing, so a node is closed with its best g.')
K.quiz('m', 'The sum of two admissible heuristics is', ['always admissible', 'not admissible in general', 'always consistent', 'always 0'], 1,
       'Question 12.', 'The max is admissible, the sum can overestimate.')
K.quiz('m', 'P(A) = 0.5, P(B) = 0.4, P(A ∧ B) = 0.2. P(A ∨ B) is', ['0.9', '0.7', '0.2', '0.5'], 1,
       'Subtract the overlap.', '0.5 + 0.4 − 0.2 = 0.7.')
K.quiz('m', 'A ⇔ B in CNF is', ['(A ∨ B) ∧ (¬A ∨ ¬B)', '(¬A ∨ B) ∧ (¬B ∨ A)', 'A ∧ B', '¬A ∨ ¬B'], 1,
       'Two implications.', 'A ⇒ B and B ⇒ A.')
K.quiz('h', 'Which update uses the action actually taken in the next state?', ['Q-learning', 'SARSA', 'value iteration', 'REINFORCE'], 1,
       'On policy.', 'SARSA uses Q(s′, a′) for the a′ it really takes.')
K.quiz('h', 'Rejection sampling with evidence of probability 0.001 keeps about how many of 10,000 samples?', ['1', '10', '100', '1,000'], 1,
       'N × P(e).', '10,000 × 0.001 = 10.')
K.quiz('h', 'UCS can fail to be complete when', ['all costs are 1', 'there are zero cost cycles', 'the graph is a tree', 'h = 0'], 1,
       'Question 19.', 'It can loop forever along a zero cost cycle.')
K.quiz('x', 'For a fixed policy with γ &lt; 1, the exact values are', ['V = R', 'V = (I − γ P_π)⁻¹ R', 'V = γ P_π R', 'V = max R'], 1,
       'Question 18.', 'The Bellman equation for a fixed policy is linear.')
K.quiz('x', 'If h₁ and h₂ are consistent, then max(h₁, h₂) is', ['admissible but not consistent', 'consistent and dominates both', 'neither', 'equal to h₁ + h₂'], 1,
       'Question 16.', 'Each hᵢ(n) ≤ c + h(n′), so the max is too.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Rows in a truth table for 4 symbols?', '16', '2ⁿ.',
       ['Each symbol has 2 values.', '2 × 2 × 2 × 2.', eq('16')], check=16)
K.calc('e', 'Chance two fair dice total 7? Three decimals.', '0.167', '6 ÷ 36.',
       ['36 pairs.', '6 give 7.', eq('≈ 0.167')], check=6 / 36, tol=0.0005)
K.calc('e', 'Minimax value: MIN choices (3, 5) under move 1 and (2, 9) under move 2?', '3', 'max of mins.',
       ['min(3, 5) = 3.', 'min(2, 9) = 2.', eq('max(3, 2) = 3')], check=3)
K.calc('m', 'UCS cost to G in question 6?', '4', 'S, A, B, G.',
       ['S to A: 1.', 'A to B: 2, total 3.', eq('B to G: 1, total 4')], check=4)
K.calc('m', 'P(rain | wet) with P(rain) = 0.2, P(wet | rain) = 0.9, P(wet | dry) = 0.1? Three decimals.', '0.692', '0.18 ÷ 0.26.',
       ['P(wet) = 0.18 + 0.08 = 0.26.', '0.18 ÷ 0.26.', eq('≈ 0.692')], check=0.18 / 0.26, tol=0.0005)
K.calc('m', 'Racing car MDP, γ = 0.9: V₁(cool) after one sweep from 0?', '2', 'Best one step reward.',
       ['Slow gives 1.', 'Fast gives 2.', eq('V₁(cool) = 2')], check=2)
K.calc('m', 'BFS nodes generated with b = 2, goal depth 3, root not counted?', '14', '2 + 4 + 8.',
       ['Depth 1: 2.', 'Depth 2: 4, depth 3: 8.', eq('14')], check=14)
K.calc('m', 'P(A ∨ B) with P(A) = 0.5, P(B) = 0.4, P(A ∧ B) = 0.2?', '0.7', 'Inclusion and exclusion.',
       ['0.5 + 0.4 = 0.9.', 'Minus the overlap 0.2.', eq('0.7')], check=0.7, tol=0.0005)
K.calc('h', 'Rejection samples kept from 1,000 when P(e) = 0.01?', '10', 'N × P(e).',
       ['Each kept with chance 0.01.', '1,000 × 0.01.', eq('10')], check=10)
K.calc('h', 'Clauses in the CNF of A ⇔ (B ∨ C)?', '3', 'Question 10.',
       ['¬A ∨ B ∨ C.', '¬B ∨ A and ¬C ∨ A.', eq('3 clauses')], check=3)
K.calc('x', 'One state, reward 1 every step, γ = 0.9: V = (1 − γ)⁻¹ R?', '10', '1 ÷ 0.1.',
       ['I − γP = 1 − 0.9 = 0.1.', 'Its inverse is 10.', eq('V = 10')], check=1 / (1 - 0.9), tol=0.0005)
K.calc('x', 'P(ill | negative) with prior 0.01, sensitivity 0.9, false positive rate 0.1? Four decimals.', '0.0011', '(1 − 0.9) × 0.01 ÷ P(negative).',
       ['P(negative) = 1 − 0.108 = 0.892.', '0.1 × 0.01 = 0.001.', eq('0.001 ÷ 0.892 ≈ 0.0011')], check=0.001 / 0.892, tol=0.00005)

T = K.topic(
    slug='core-revision', topic='core-revision', kind='revision', step=STEP11,
    title='Exam revision: from school to research universities', short='Exam revision', badge='11.2', minutes=60,
    lead='Practise the question shapes of every level with worked answers: agents, search orders and simple chances, algorithms run by hand, quick checks for GATE and NPTEL papers, and proofs with their conditions.',
    desc='Exam patterns by tier for Core AI, worked questions on PEAS, BFS and DFS order, dice, minimax, UCS and A* by hand, alpha beta, Bayes rule, value iteration and CNF, quick checks for multiple choice and numerical answer papers, proofs on heuristics, colliders, policy evaluation and UCS optimality, a formula sheet and common mistakes.',
    summary='Core AI exam questions from school level to research universities, with worked answers, a formula sheet and a mock quiz.',
    keywords=['exam', 'revision', 'formula sheet', 'mock quiz', 'numericals', 'proofs', 'IIT', 'NPTEL', 'GATE', 'MIT', 'Berkeley'],
    recap='')
