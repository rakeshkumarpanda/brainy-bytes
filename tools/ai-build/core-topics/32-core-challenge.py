# Chapter 11.1: challenge problems across Core AI. Original problems in the style of top university exams, one set
# for each step, with proofs and a method guide. They draw on AIMA 3rd ed. chapters 3 to 21 and the uploaded slides on
# search, CSPs and games. Every number in this chapter was checked by running its code and the animations.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()
STEP11 = (11, 'Challenge and revision', 'cai-review', 'Bring it all together: the hardest exam style problems across Core AI, then a revision guide from school level to top universities.', 'All levels')

K.code('trap', r'''
# A* graph search with an admissible but inconsistent heuristic.
# Without reopening closed nodes it returns a path that is not the cheapest.
import heapq
edges = {'S': [('A', 4), ('B', 1)], 'B': [('A', 1)], 'A': [('G', 4)], 'G': []}
h = {'S': 0, 'A': 0, 'B': 5, 'G': 0}       # h(B) = 5 > cost(B, A) + h(A) = 1

def astar(reopen):
    frontier = [(h['S'], 0, 'S', ['S'])]
    best_g = {}
    while frontier:
        f, g, node, path = heapq.heappop(frontier)
        if node == 'G':
            return g, path
        if node in best_g and (not reopen or best_g[node] <= g):
            continue                       # already expanded
        best_g[node] = g
        for nxt, cost in edges[node]:
            heapq.heappush(frontier, (g + cost + h[nxt], g + cost, nxt, path + [nxt]))

print("no reopening:  ", astar(False))
print("with reopening:", astar(True))
''')

K.code('ab', r'''
# Alpha beta on the three by three tree from AIMA figure 5.5. Counts the leaves it looks at.
leaves_seen = []

def alphabeta(node, alpha, beta, is_max):
    if type(node) == int:
        leaves_seen.append(node)
        return node
    if is_max:
        value = -1000
        for child in node:
            value = max(value, alphabeta(child, alpha, beta, False))
            if value >= beta:
                return value               # MIN above will never allow this
            alpha = max(alpha, value)
    else:
        value = 1000
        for child in node:
            value = min(value, alphabeta(child, alpha, beta, True))
            if value <= alpha:
                return value               # MAX above already has better
            beta = min(beta, value)
    return value

tree = [[3, 12, 8], [2, 4, 6], [14, 5, 2]]
print("value:", alphabeta(tree, -1000, 1000, True))
print("leaves seen:", leaves_seen, "of 9")
''')

K.code('ac3', r'''
# AC-3 on X < Y < Z with every domain {1, 2, 3}.
domains = {'X': [1, 2, 3], 'Y': [1, 2, 3], 'Z': [1, 2, 3]}
less = [('X', 'Y'), ('Y', 'Z')]                 # first < second
arcs = []
for a, b in less:
    arcs.append((a, b))
    arcs.append((b, a))

def ok(a, va, b, vb):
    if (a, b) in less:
        return va < vb
    return vb < va

queue = list(arcs)
while queue:
    a, b = queue.pop(0)
    keep = [va for va in domains[a] if any(ok(a, va, b, vb) for vb in domains[b])]
    if len(keep) < len(domains[a]):
        print("revise", a, "against", b, ":", domains[a], "becomes", keep)
        domains[a] = keep
        for c, d in arcs:
            if d == a and c != b:
                queue.append((c, d))
print(domains)
''')

K.code('vi2', r'''
# Value iteration is a contraction: the biggest change shrinks by a factor gamma each sweep.
# Two states. In s0, "stay" gives 1 and stays, "go" gives 0 and moves to s1. In s1 every action gives 2 and stays.
gamma = 0.9
V = [0.0, 0.0]
for k in range(1, 8):
    new0 = max(1 + gamma * V[0], 0 + gamma * V[1])
    new1 = 2 + gamma * V[1]
    change = max(abs(new0 - V[0]), abs(new1 - V[1]))
    V = [new0, new1]
    print("sweep", k, "V =", [round(v, 3) for v in V], "change =", round(change, 3))
print("exact: V(s1) =", round(2 / (1 - gamma), 3), " V(s0) =", round(max(1 / (1 - gamma), gamma * 2 / (1 - gamma)), 3))
''')

K.lesson('how', 'How to attack a hard Core AI problem', f'''
{src('Original challenge problems written for this course in the style of exams at top universities (MIT 6.034, Berkeley CS188, Stanford CS221, CMU 15-381, IIT and IISc AI courses, and the GATE Data Science and AI paper). None is copied from a real past paper. They draw on AIMA 3rd ed. chapters 3 to 21, the uploaded slides on search, CSPs and games, and every earlier chapter of this subject. Every number was checked by running the code on this page.')}
{wwh('A <b>challenge problem</b> mixes two or more ideas, hides a trap, or asks you to prove why a method works. This chapter has one challenge set for each step of Core AI, then proofs, then a guide for choosing a method.',
     'Easy questions test whether you remember a formula. Hard questions test whether you know <i>when</i> the formula holds. Top exams almost always ask about the edge: an inconsistent heuristic, a collider that becomes open, a discount that breaks the bound.',
     'Use the same five moves every time: name the model (search, CSP, game, logic, plan, Bayes net or MDP), write the formula, check its conditions, work the numbers one step at a time, and say what the answer means.')}
{table(['Move', 'Ask yourself', 'Example'], [
    ['1. Name the model', 'What are the states, actions, variables or rules?', 'A route finder is a search problem with a step cost.'],
    ['2. Write the formula', 'Which equation decides the answer?', 'f(n) = g(n) + h(n) for A*.'],
    ['3. Check the conditions', 'Does the theorem’s condition hold here?', 'Is h consistent, or only admissible?'],
    ['4. Work it step by step', 'Can a reader follow each line?', 'Write the frontier after every expansion.'],
    ['5. Say what it means', 'Is the answer sensible?', 'A probability must lie between 0 and 1.']])}
{note('Each challenge below names the chapter that teaches the idea, so you can go back if a step is not clear.', 'tip')}
''', kw=['problem solving', 'exam strategy', 'challenge problems', 'MIT', 'Berkeley', 'Stanford', 'CMU', 'IIT', 'GATE'])

K.lesson('search', 'Challenge set 1: search and heuristics', f'''
<h3>Challenge 1. An admissible heuristic that still gives a wrong answer</h3>
<p>Edges: S to A costs 4, S to B costs 1, B to A costs 1, A to G costs 4. The heuristic is h(S) = 0, h(A) = 0, h(B) = 5, h(G) = 0. Is h admissible? Is it consistent? What does A* graph search return if it never reopens a closed node? (Chapters 3.1 and 3.2.)</p>
{steps('Model answer', [
    'True costs to G: from A it is 4, from B it is 1 + 4 = 5, from S it is 1 + 1 + 4 = 6. Every h is at most the true cost, so h is admissible.',
    'Consistency needs h(B) ≤ c(B, A) + h(A) = 1 + 0 = 1. But h(B) = 5, so h is not consistent.',
    'Start: frontier S (f = 0). Expand S: A gets g = 4, f = 4. B gets g = 1, f = 1 + 5 = 6.',
    'A has the smaller f, so A is expanded first with g = 4 and closed. G gets g = 8, f = 8.',
    'Next B (f = 6). It finds A again with g = 2, but A is closed, so this better path is thrown away.',
    eq('G is popped with cost 8, but the best path S, B, A, G costs 6')])}
{code('trap')}
{note('The fix: use a consistent heuristic, or let graph search reopen a closed node when a cheaper path to it turns up. Tree search with an admissible heuristic is always optimal, because it never closes anything.', 'exam')}
<h3>Challenge 2. How much extra work does iterative deepening do?</h3>
{steps('Branching factor b = 10, solution depth d = 5. Count the nodes generated by BFS and by IDS.', [
    'BFS generates b + b² + … + b⁵ = 10 + 100 + 1,000 + 10,000 + 100,000 = 111,110.',
    'IDS generates level i once for every limit from i to d, that is (d + 1 − i) times.',
    'IDS: 5 × 10 + 4 × 100 + 3 × 1,000 + 2 × 10,000 + 1 × 100,000 = 123,450.',
    eq('IDS does only about 11 percent more work, and needs only O(bd) memory')])}
<h3>Challenge 3. Effective branching factor</h3>
{steps('A* generates N = 52 nodes and finds a solution at depth d = 5. Find the effective branching factor b*.', [
    'b* is the branching factor of a uniform tree of depth d with N + 1 nodes: N + 1 = 1 + b* + (b*)² + … + (b*)⁵.',
    'So 53 = 1 + b* + (b*)² + (b*)³ + (b*)⁴ + (b*)⁵. Try b* = 2: the sum is 63, too big. Try 1.9: it is about 51.5, a little small.',
    'Halving the interval a few times gives b* ≈ 1.92.',
    eq('b* ≈ 1.92, the value given in AIMA section 3.6.1')])}
{viz('searchgraph', alg='astar', gr='romania', start='Arad', goal='Bucharest')}
''', kw=['admissible', 'consistent', 'inconsistent heuristic', 'reopening', 'graph search', 'iterative deepening cost', 'effective branching factor'])

K.lesson('csp', 'Challenge set 2: constraint satisfaction and local search', f'''
<h3>Challenge 4. AC-3 alone solves this CSP</h3>
<p>Variables X, Y and Z each have the domain 1, 2, 3, with constraints X &lt; Y and Y &lt; Z. Run AC-3. (Chapter 5.1.)</p>
{steps('Model answer', [
    'Arc X to Y: X = 3 has no larger Y, so remove it. X becomes 1, 2.',
    'Arc Y to X: Y = 1 has no smaller X, so remove it. Y becomes 2, 3.',
    'Arc Y to Z: Y = 3 has no larger Z, so remove it. Y becomes 2. Arc Z to Y: Z must be above 2, so Z becomes 3.',
    'Y changed, so the arc X to Y goes back on the queue. X = 2 has no larger Y now, so X becomes 1.',
    eq('X = 1, Y = 2, Z = 3, found with no search at all')])}
{code('ac3')}
{viz('ac3', pre='custom', dom='X: 1 2 3\nY: 1 2 3\nZ: 1 2 3', cons='X < Y\nY < Z')}
<h3>Challenge 5. Why a tree shaped CSP is easy</h3>
{steps('A CSP has n = 10 variables, each with d = 3 values, and its constraint graph is a tree. Bound the work.', [
    'Pick a root and order the variables so every parent comes before its children.',
    'Go backwards, making each arc from parent to child consistent. Each of the n − 1 arcs needs at most d² checks.',
    'Then assign values from the root down. Arc consistency means a good value is always left, so there is no backtracking.',
    eq('(n − 1) d² = 9 × 9 = 81 checks, against dⁿ = 59,049 full assignments')])}
<h3>Challenge 6. Simulated annealing accepts a worse move</h3>
{steps('The current state has value 10. A random neighbour has value 8, so ΔE = −2 when we maximise. The temperature is T = 1. What is the chance of moving?', [
    'A worse move is taken with probability e^(ΔE ÷ T).',
    'e^(−2 ÷ 1) = e^(−2).',
    eq('≈ 0.135. At T = 10 it would be e^(−0.2) ≈ 0.819')])}
''', kw=['AC-3', 'arc consistency', 'tree structured CSP', 'topological order', 'simulated annealing', 'acceptance probability'])

K.lesson('games', 'Challenge set 3: adversarial search', f'''
<h3>Challenge 7. Which leaves does alpha beta skip?</h3>
<p>A MAX root has three MIN children with leaves 3 12 8, 2 4 6 and 14 5 2, read left to right. Find the minimax value and the leaves alpha beta never looks at. (Chapters 6.1 and 6.2.)</p>
{steps('Model answer', [
    'First MIN node: min(3, 12, 8) = 3. Now α = 3 at the root.',
    'Second MIN node: its first leaf is 2. Its value can only be 2 or less, and MAX already has 3.',
    'So the leaves 4 and 6 are pruned.',
    'Third MIN node: 14, then 5, then 2. None of 14 or 5 is at most 3, so all three are read. Its value is 2.',
    eq('root = max(3, ≤ 2, 2) = 3, with 7 of the 9 leaves read')])}
{code('ab')}
{viz('gametree', mode='ab', pat='mm2', b=3, leaves='3 12 8 2 4 6 14 5 2')}
<h3>Challenge 8. The best case for alpha beta</h3>
{steps('With perfect move ordering, how many leaves does alpha beta read for b = 3 and depth d = 4?', [
    'Knuth and Moore (1975): the best case reads b^⌈d ÷ 2⌉ + b^⌊d ÷ 2⌋ − 1 leaves.',
    '3² + 3² − 1.',
    eq('17 leaves out of 3⁴ = 81. Search can go about twice as deep in the same time')])}
<h3>Challenge 9. Expectimax is not safe under a change of scale</h3>
{steps('A chance node picks between leaves 0 and 4 with equal chance. Another branch gives 3 for sure. Replace every leaf x by x². Can MAX change its move?', [
    'Before: the chance node is 0.5 × 0 + 0.5 × 4 = 2 and the sure branch is 3, so MAX picks the sure 3.',
    'After: the chance node is 0.5 × 0 + 0.5 × 16 = 8 and the sure branch is 9. MAX still picks the sure branch.',
    'Now try leaves 0 and 6 against a sure 4. Before squaring: 3 against 4, so MAX picks the sure branch. After squaring: 18 against 16, so MAX picks the gamble.',
    eq('minimax only needs the order of leaf values, expectimax needs the values themselves')])}
''', kw=['alpha beta', 'pruning', 'move ordering', 'best case', 'Knuth and Moore', 'expectimax', 'monotonic transformation'])

K.lesson('logic', 'Challenge set 4: logic and inference', f'''
<h3>Challenge 10. A resolution proof</h3>
<p>KB: P ⇒ Q, Q ⇒ R, P. Prove R by resolution. (Chapter 7.2.)</p>
{steps('Model answer', [
    'Turn the KB into clauses: ¬P ∨ Q, ¬Q ∨ R, P. Add the negated goal ¬R.',
    'Resolve ¬R with ¬Q ∨ R to get ¬Q.',
    'Resolve ¬Q with ¬P ∨ Q to get ¬P.',
    'Resolve ¬P with P to get the empty clause.',
    eq('KB ∧ ¬R is unsatisfiable, so KB ⊨ R')])}
{viz('resolution', kb='P ⇒ Q\nQ ⇒ R\nP', q='R')}
<h3>Challenge 11. Count the models</h3>
{steps('How many models over P, Q and R make (P ∨ Q) ∧ (¬P ∨ R) true?', [
    'If P is true, the first clause holds and the second needs R true. Q is free: 2 models.',
    'If P is false, the second clause holds and the first needs Q true. R is free: 2 models.',
    eq('2 + 2 = 4 models out of 8')])}
<h3>Challenge 12. Unification and the occurs check</h3>
{steps('Unify Knows(John, x) with Knows(y, Mother(y)). Then try x with F(x).', [
    'First arguments: John and y, so bind y to John.',
    'Second arguments: x and Mother(y), which is now Mother(John). Bind x to Mother(John).',
    'The most general unifier is y/John, x/Mother(John).',
    eq('x with F(x) fails: x would have to contain itself, which the occurs check forbids')])}
{note('Forward chaining is complete for definite clauses only. Resolution is refutation complete for any clauses. A favourite exam trap gives a KB with a disjunction such as A ∨ B and asks for forward chaining.', 'exam')}
''', kw=['resolution proof', 'CNF', 'model counting', 'unification', 'most general unifier', 'occurs check', 'forward chaining limits'])

K.lesson('planning', 'Challenge set 5: planning', f'''
<h3>Challenge 13. The Sussman anomaly</h3>
<p>C is on A, and A and B are on the table. The goal is On(A, B) ∧ On(B, C). Why does solving one sub-goal at a time fail? (Chapters 8.2 and 8.3.)</p>
{steps('Model answer', [
    'Try On(A, B) first: move C to the table, put A on B. Now B is under A, and to get On(B, C) we must take A off again.',
    'Try On(B, C) first: put B on C. Now A is buried under C and B, and to get On(A, B) we must undo On(B, C).',
    'Either order undoes the sub-goal it reached first. The sub-goals interact.',
    eq('the shortest plan interleaves them: C to table, B on C, A on B')])}
{viz('pop', dom='sussman')}
<h3>Challenge 14. Regress a goal through an action</h3>
{steps('Goal: At(B) ∧ Have(Milk). Action Go(A, B): precondition At(A), add At(B), delete At(A). Regress the goal.', [
    'The action is relevant because it adds At(B), part of the goal. It deletes nothing in the goal.',
    'Regression removes what the action adds and adds its preconditions: (goal minus add list) plus preconditions.',
    eq('the new goal is At(A) ∧ Have(Milk)')])}
<h3>Challenge 15. Resolve a threat</h3>
{steps('A partial order plan has a causal link from Buy to Cook that protects Have(Milk). Another step Drink deletes Have(Milk). Fix it.', [
    'Drink is a threat: if it runs between Buy and Cook, Cook loses its precondition.',
    'Demotion puts Drink before Buy. Promotion puts Drink after Cook.',
    eq('pick whichever ordering keeps the plan consistent, and backtrack if neither does')])}
''', kw=['Sussman anomaly', 'sub-goal interaction', 'interleaving', 'regression', 'threat', 'promotion', 'demotion'])

K.lesson('bayes', 'Challenge set 6: probability and Bayesian networks', f'''
<h3>Challenge 16. A positive test for a rare disease</h3>
{steps('A disease affects 1 percent of people. The test is positive for 90 percent of the ill and for 10 percent of the healthy. P(ill | positive)?', [
    'P(pos) = 0.9 × 0.01 + 0.1 × 0.99 = 0.009 + 0.099 = 0.108.',
    'Bayes rule: P(ill | pos) = 0.009 ÷ 0.108.',
    eq('≈ 0.083. Most positives are healthy people, because healthy people are so many more')])}
<h3>Challenge 17. Parameters saved by a Bayesian network</h3>
{steps('The burglary network has Boolean nodes B, E, A (parents B and E), J and M (parent A each). Count the numbers needed.', [
    'B and E need 1 each. A needs 4, one for each pair of parent values. J and M need 2 each.',
    '1 + 1 + 4 + 2 + 2 = 10.',
    eq('10 numbers, against 2⁵ − 1 = 31 for the full joint table')])}
<h3>Challenge 18. When does a collider open?</h3>
{steps('In the same network, are B and E independent? Are they independent given J?', [
    'With no evidence, the only path B, A, E has a collider at A with nothing observed below it. It is blocked, so B and E are independent.',
    'J is a child of A. Observing a descendant of a collider opens it.',
    eq('B and E become dependent given J: explaining away')])}
{viz('dsep')}
{note('The answer P(B | j, m) ≈ 0.284 from chapter 9.3 is worth knowing by heart. Exams often give the burglary tables and ask for it, or for P(J | b) by summing out A.', 'exam')}
''', kw=['Bayes rule', 'base rate', 'false positive', 'parameter count', 'd-separation', 'collider', 'explaining away'])

K.lesson('rl', 'Challenge set 7: MDPs and reinforcement learning', f'''
<h3>Challenge 19. Watch value iteration shrink its error</h3>
<p>State s1 always pays 2 and stays. In s0, "stay" pays 1 and stays, "go" pays 0 and moves to s1. γ = 0.9. (Chapter 10.1.)</p>
{steps('Model answer', [
    'Exact values: V(s1) = 2 ÷ (1 − 0.9) = 20. Staying in s0 forever is worth 1 ÷ 0.1 = 10. Going is worth 0 + 0.9 × 20 = 18.',
    'So V(s0) = 18 and the best action in s0 is "go".',
    'Starting from 0, the biggest change in each sweep is 2, 1.8, 1.62, and so on: it shrinks by γ every time.',
    eq('that is the contraction property: ‖BU − BU′‖ ≤ γ ‖U − U′‖')])}
{code('vi2')}
<h3>Challenge 20. How many sweeps are enough?</h3>
{steps('With R_max = 1 and γ = 0.9, how many sweeps make the error at most ε = 0.1, using the bound N = ⌈log(2 R_max ÷ (ε (1 − γ))) ÷ log(1 ÷ γ)⌉ from AIMA?', [
    '2 R_max ÷ (ε (1 − γ)) = 2 ÷ (0.1 × 0.1) = 200.',
    'log 200 ÷ log(1 ÷ 0.9) ≈ 5.298 ÷ 0.1054 ≈ 50.3.',
    eq('N = 51 sweeps')])}
<h3>Challenge 21. One Q-learning step</h3>
{steps('Q(s, a) = 2, α = 0.5, γ = 0.9. The agent gets r = 1 and the best Q in s′ is 3. Update Q(s, a).', [
    'Target = r + γ max Q(s′, a′) = 1 + 0.9 × 3 = 3.7.',
    'Error = 3.7 − 2 = 1.7.',
    eq('Q(s, a) ← 2 + 0.5 × 1.7 = 2.85')])}
{viz('qlearn')}
''', kw=['value iteration', 'contraction', 'number of iterations', 'Q-learning update', 'discount', 'Bellman operator'])

K.lesson('proofs', 'Proofs examiners ask for', f'''
<p>At the top universities, about a third of the marks are for short proofs. Each model answer below names the assumption it uses, which is where marks are lost.</p>
<h3>Proof 1. A* graph search with a consistent heuristic is optimal</h3>
{steps('Model answer', [
    'If n′ is a successor of n, then g(n′) = g(n) + c(n, n′), so f(n′) = g(n) + c(n, n′) + h(n′) ≥ g(n) + h(n) = f(n) by consistency. So f never goes down along a path.',
    'Suppose A* expands a node n with a path that is not the cheapest. Some node m on the cheapest path to n is on the frontier, with f(m) ≤ f(n) on that path.',
    'Since f does not decrease, m would be expanded before n. Repeating the argument, the cheapest path reaches n first.',
    'So every node is first expanded with its cheapest g. The goal is too, and h(goal) = 0 gives f = the optimal cost.'])}
<h3>Proof 2. Alpha beta returns the minimax value</h3>
{steps('Model answer', [
    'At a MIN node with value v ≤ α, MAX above already has a choice worth α, so MAX will never choose this node. Its exact value cannot change the root.',
    'At a MAX node with v ≥ β, MIN above has a choice worth β and will avoid it. The same reasoning applies.',
    'Only these branches are cut, so every node on the principal line keeps its exact minimax value.'])}
<h3>Proof 3. The Bellman update is a contraction</h3>
{steps('Model answer', [
    'Write (BU)(s) = R(s) + γ max over a of Σ P(s′ | s, a) U(s′).',
    'For any two functions f and g, |max f − max g| ≤ max |f − g|.',
    'So |(BU)(s) − (BU′)(s)| ≤ γ max over a of Σ P(s′ | s, a) |U(s′) − U′(s′)| ≤ γ ‖U − U′‖.',
    'With γ &lt; 1 the error shrinks each sweep, so there is one fixed point and value iteration reaches it from any start (Banach fixed point theorem).'])}
<h3>Proof 4. Resolution is sound</h3>
{steps('Model answer', [
    'Take clauses A ∨ ℓ and B ∨ ¬ℓ, and a model that makes both true.',
    'If ℓ is true in it, then ¬ℓ is false, so B must be true. If ℓ is false, A must be true.',
    'Either way A ∨ B is true. So every model of the parents is a model of the resolvent.'])}
<h3>Proof 5. Tree shaped CSPs need no backtracking</h3>
{steps('Model answer', [
    'Order the variables so each one comes after its parent, then make every parent to child arc consistent, last to first.',
    'Assign the root any value left in its domain. For each child, arc consistency guarantees a value that agrees with the parent’s value.',
    'Each variable has only one parent, so no other constraint can rule that value out. So the forward pass never fails, in O(n d²) time.'])}
''', kw=['proof', 'A* optimality', 'consistency', 'alpha beta correctness', 'contraction mapping', 'Banach', 'soundness of resolution', 'tree CSP'])

K.lesson('choose', 'Choosing the right method', f'''
{versus('Which Core AI method fits the problem', ['Problem looks like', 'Use', 'Why', 'Watch out for'], [
    ['Find a path, all step costs equal', 'BFS or IDS', 'Optimal for equal costs, IDS uses little memory', 'BFS memory grows as bᵈ'],
    ['Find the cheapest path, a good estimate known', 'A* (IDA* or SMA* if memory is short)', 'Optimal with a consistent h, focused search', 'Inconsistent h in graph search'],
    ['Actions may fail or have several outcomes', 'AND-OR search, AO*', 'Returns a conditional plan', 'Cycles need loops in the plan'],
    ['Only the final state matters', 'Hill climbing, annealing, genetic algorithms', 'Little memory, works on huge spaces', 'Local maxima and plateaus'],
    ['Assign values under constraints', 'Backtracking with MRV, forward checking, AC-3, or min-conflicts', 'Prunes whole sets of assignments', 'Variable order changes the time a lot'],
    ['An opponent moves against you', 'Minimax with alpha beta, MCTS for huge trees', 'Assumes the opponent plays well', 'Evaluation function quality'],
    ['Chance moves in a game', 'Expectimax, expectiminimax', 'Uses averages over chance', 'Needs real values, not only their order'],
    ['Facts and rules, need a proof', 'Forward or backward chaining, resolution', 'Sound and complete for their logic', 'First order logic is only semi decidable'],
    ['Reach a goal by a sequence of actions', 'STRIPS with forward or backward search, partial order planning', 'Factored states, reuse of heuristics', 'Sub-goal interaction'],
    ['Uncertain facts', 'Bayesian networks, exact or sampling inference', 'Compact, answers any query', 'Exact inference is NP hard in general'],
    ['Cause and effect, an intervention', 'Causal graphs and do-calculus', 'Separates seeing from doing', 'Hidden confounders'],
    ['Decide over time, model known', 'Value or policy iteration', 'Exact optimal policy', 'Large state spaces'],
    ['Decide over time, model unknown', 'TD learning, Q-learning, SARSA, policy gradients', 'Learn from experience', 'Exploration and slow learning']],
    'name the model first. The model decides the family of methods, and the conditions of each theorem decide which member to trust.')}
''', kw=['method selection', 'comparison', 'which algorithm', 'decision guide'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Every Core AI method answers one question: what should I do next? Search tries paths, logic proves facts, Bayes nets weigh chances, and RL learns from rewards.</p>',
    '<p>Run each method by hand on a small example: A* with a table of f values, AC-3 on three variables, alpha beta with α and β written at every node, enumeration on the burglary net, and a value iteration sweep.</p>',
    '<p>Know when each theorem holds: consistency for A* graph search, definite clauses for chaining, d-separation for independence, γ &lt; 1 for contraction, and the conditions for Q-learning to converge (every pair visited forever, step sizes with Σ α = ∞ and Σ α² &lt; ∞).</p>',
    '<p>Research problems join the steps: learned heuristics for search (AlphaZero joins MCTS and deep networks), neuro symbolic reasoning, planning with learned models (MuZero), causal reinforcement learning, and large language models used as planners and checked by classical planners or verifiers.</p>')}
''', kw=['AlphaZero', 'MuZero', 'neuro symbolic', 'LLM planning', 'causal RL', 'research'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Use five moves on any problem: name the model, write the formula, check its conditions, work step by step, and say what the answer means.',
    'Search: an admissible but inconsistent h can fool A* graph search. IDS costs only about 11 percent more than BFS for b = 10.',
    'CSPs and games: AC-3 can solve a CSP alone, tree CSPs take O(n d²), alpha beta reads b^⌈d ÷ 2⌉ + b^⌊d ÷ 2⌋ − 1 leaves at best.',
    'Logic and planning: refute KB ∧ ¬α by resolution, use the occurs check, interleave interacting sub-goals, and fix threats by promotion or demotion.',
    'Uncertainty and RL: mind the base rate, open colliders by observing a descendant, and use the γ contraction to bound value iteration.'],
    'the last chapter is a revision guide by exam tier, with a formula sheet and a mock quiz.')}
{nbcard('core-challenge', 'Run the inconsistent heuristic trap, alpha beta with a leaf counter, AC-3 and value iteration, then write the IDS node count, a consistency checker and alpha beta yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Which search is complete and optimal when every step costs the same, and uses only O(bd) memory?', ['BFS', 'DFS', 'Iterative deepening search', 'Greedy best first search'], 2,
       'Deepen step by step.', 'IDS repeats shallow levels but needs little memory.')
K.quiz('e', 'A heuristic is admissible if it', ['never overestimates the true cost to the goal', 'is always 0', 'is consistent', 'is the exact cost'], 0,
       'Optimistic.', 'h(n) ≤ h*(n) for every n.')
K.quiz('e', 'In alpha beta, the root value compared with plain minimax is', ['always smaller', 'the same', 'always larger', 'random'], 1,
       'Pruning is safe.', 'Only branches that cannot change the root are cut.')
K.quiz('m', 'An admissible but inconsistent heuristic can make A* return a worse path when', ['A* uses tree search', 'A* uses graph search and never reopens closed nodes', 'all costs are equal', 'h = 0'], 1,
       'Challenge 1.', 'A node can be closed with a g that is too big.')
K.quiz('m', 'In the burglary network, B and E are', ['dependent with no evidence', 'independent with no evidence, dependent given J', 'always independent', 'dependent only given B'], 1,
       'Collider at A.', 'Observing J, a child of A, opens the collider.')
K.quiz('m', 'Regressing At(B) ∧ Have(Milk) through Go(A, B) (pre At(A), add At(B), del At(A)) gives', ['At(B)', 'At(A) ∧ Have(Milk)', 'Have(Milk)', 'At(A) ∧ At(B)'], 1,
       'Remove adds, add preconditions.', 'At(B) comes from the action, At(A) is its precondition.')
K.quiz('m', 'Why does solving sub-goals one at a time fail on the Sussman anomaly?', ['STRIPS cannot express it', 'reaching either sub-goal first blocks the other, so the plan must interleave them', 'it has no solution', 'it needs a heuristic'], 1,
       'Interacting sub-goals.', 'The shortest plan is C to table, B on C, A on B.')
K.quiz('h', 'The most general unifier of Knows(John, x) and Knows(y, Mother(y)) is', ['x/John, y/Mother(John)', 'y/John, x/Mother(John)', 'no unifier', 'y/x'], 1,
       'Left to right.', 'Bind y first, then x to Mother(John).')
K.quiz('h', 'Squaring every leaf value can change the decision of', ['minimax', 'expectimax', 'both', 'neither'], 1,
       'Order or size.', 'Minimax needs only the order, expectimax averages, so a monotonic change can flip it.')
K.quiz('h', 'A tree shaped CSP with n variables and d values can be solved in', ['O(dⁿ)', 'O(n d²)', 'O(n²d)', 'O(2ⁿ)'], 1,
       'Arc consistency then one pass.', 'n − 1 arcs with d² checks each, then no backtracking.')
K.quiz('x', 'In the style of an MIT 6.034 exam: the key step that makes A* graph search optimal with a consistent h is', ['h(goal) = 0 only', 'f is non decreasing along every path', 'the branching factor is finite', 'the frontier is a stack'], 1,
       'Proof 1.', 'Consistency gives f(n′) ≥ f(n), so nodes are expanded in order of f.')
K.quiz('x', 'In the style of a Stanford CS221 exam: value iteration converges for γ &lt; 1 because the Bellman update', ['is linear', 'is a γ contraction in the max norm', 'is greedy', 'uses a model'], 1,
       'Proof 3.', '‖BU − BU′‖ ≤ γ ‖U − U′‖, so there is one fixed point.')

# ---------------------------------------------------------------- calc
K.calc('e', 'BFS with b = 10 and solution depth d = 5: nodes generated?', '111110', 'b + b² + … + bᵈ.',
       ['10 + 100 + 1,000.', '+ 10,000 + 100,000.', eq('111,110')], check=sum(10 ** i for i in range(1, 6)))
K.calc('e', 'IDS with b = 10 and d = 5: nodes generated?', '123450', 'Σ (d + 1 − i) bⁱ.',
       ['5 × 10 + 4 × 100 = 450.', '3 × 1,000 + 2 × 10,000 = 23,000.', eq('450 + 23,000 + 100,000 = 123,450')], check=sum((6 - i) * 10 ** i for i in range(1, 6)))
K.calc('e', 'Number of numbers in the burglary Bayesian network?', '10', '1 + 1 + 4 + 2 + 2.',
       ['B and E: 1 each.', 'A has 2 parents: 4. J and M: 2 each.', eq('10')], check=10)
K.calc('m', 'Effective branching factor when A* generates 52 nodes for a solution at depth 5? Two decimals.', '1.92', '53 = 1 + b* + … + (b*)⁵.',
       ['b* = 2 gives 63, too many.', 'b* = 1.9 gives about 51.5, too few.', eq('b* ≈ 1.92')], check=1.9167, tol=0.006)
K.calc('m', 'Leaves read by alpha beta on 3 12 8 | 2 4 6 | 14 5 2?', '7', 'Only 4 and 6 are pruned.',
       ['First MIN reads 3.', 'Second MIN stops after 2.', eq('3 + 1 + 3 = 7')], check=7)
K.calc('m', 'Best case leaves for alpha beta with b = 3, d = 4?', '17', 'b^⌈d/2⌉ + b^⌊d/2⌋ − 1.',
       ['3² = 9.', '9 + 9 = 18.', eq('18 − 1 = 17')], check=17)
K.calc('m', 'Models of (P ∨ Q) ∧ (¬P ∨ R) over P, Q, R?', '4', 'Split on P.',
       ['P true needs R: Q free, 2.', 'P false needs Q: R free, 2.', eq('4')], check=4)
K.calc('m', 'P(ill | positive) with prior 0.01, sensitivity 0.9, false positive rate 0.1? Three decimals.', '0.083', '0.009 ÷ 0.108.',
       ['P(pos) = 0.009 + 0.099 = 0.108.', '0.009 ÷ 0.108.', eq('≈ 0.083')], check=0.009 / 0.108, tol=0.0005)
K.calc('m', 'Q-learning: Q = 2, α = 0.5, γ = 0.9, r = 1, max Q(s′) = 3. New Q?', '2.85', 'Q + α (r + γ max − Q).',
       ['Target 1 + 2.7 = 3.7.', 'Error 1.7.', eq('2 + 0.85 = 2.85')], check=2 + 0.5 * (1 + 0.9 * 3 - 2), tol=0.0005)
K.calc('h', 'Annealing: ΔE = −2, T = 1. Chance of taking the worse move? Three decimals.', '0.135', 'e^(ΔE ÷ T).',
       ['ΔE ÷ T = −2.', 'e^(−2).', eq('≈ 0.135')], check=0.1353, tol=0.0005)
K.calc('h', 'Value iteration sweeps for error ε = 0.1 with R_max = 1, γ = 0.9, by the AIMA bound?', '51', '⌈log(2R_max ÷ ε(1 − γ)) ÷ log(1 ÷ γ)⌉.',
       ['2 ÷ 0.01 = 200.', 'log 200 ÷ log(1 ÷ 0.9) ≈ 50.3.', eq('round up to 51')], check=51)
K.calc('x', 'Challenge 1: cost returned by A* graph search without reopening, minus the optimal cost?', '2', '8 − 6.',
       ['Returned path S, A, G costs 8.', 'Best path S, B, A, G costs 6.', eq('8 − 6 = 2')], check=2)
K.calc('x', 'Tree CSP with n = 10, d = 3: worst case arc checks (n − 1) d²?', '81', '9 × 9.',
       ['n − 1 = 9 arcs.', 'd² = 9 checks each.', eq('81')], check=81)

# ---------------------------------------------------------------- assignments
K.assign('idscount', 'e', 'Count the nodes of BFS and IDS',
         '<p>Write <code>bfs_nodes(b, d)</code> that returns b + b² + … + bᵈ, and <code>ids_nodes(b, d)</code> that returns the sum of (d + 1 − i) bⁱ for i from 1 to d.</p>',
         '''def bfs_nodes(b, d):
    # your code here
    pass

def ids_nodes(b, d):
    # your code here
    pass
''', [("bfs_nodes(10, 5)", 111110), ("ids_nodes(10, 5)", 123450), ("ids_nodes(2, 3)", 22), ("bfs_nodes(3, 1)", 3)],
         '''def bfs_nodes(b, d):
    total = 0
    for i in range(1, d + 1):
        total = total + b ** i
    return total

def ids_nodes(b, d):
    total = 0
    for i in range(1, d + 1):
        total = total + (d + 1 - i) * b ** i
    return total
''', 'Loop over the depth i from 1 to d and add up the terms.', '<p>Test 3: 3 × 2 + 2 × 4 + 1 × 8 = 22.</p>')
K.assign('consistent', 'm', 'Check a heuristic',
         '<p>Write <code>bad_edges(edges, h, goal)</code>. <code>edges</code> is a list of (from, to, cost) and <code>h</code> a dict. Return the list of edges (from, to) where h(from) &gt; cost + h(to), in the order given, followed by True if h(goal) == 0 else False.</p>',
         '''def bad_edges(edges, h, goal):
    # your code here
    pass
''', [("bad_edges([('S', 'A', 4), ('S', 'B', 1), ('B', 'A', 1), ('A', 'G', 4)], {'S': 0, 'A': 0, 'B': 5, 'G': 0}, 'G')", [['B', 'A'], True]),
      ("bad_edges([('S', 'G', 2)], {'S': 2, 'G': 0}, 'G')", [True]),
      ("bad_edges([('S', 'G', 2)], {'S': 4, 'G': 1}, 'G')", [['S', 'G'], False])],
         '''def bad_edges(edges, h, goal):
    out = []
    for a, b, cost in edges:
        if h[a] > cost + h[b]:
            out.append((a, b))
    out.append(h[goal] == 0)
    return out
''', 'Test each edge with the consistency rule, then add the goal test at the end.', '<p>An empty list before True means h is consistent.</p>')
K.assign('abcount', 'h', 'Alpha beta with a leaf counter',
         '<p>Write <code>alphabeta(node, alpha, beta, is_max, seen)</code> for a tree of nested lists with numbers at the leaves. Append every leaf you read to the list <code>seen</code>, prune with α and β, and return the value.</p>',
         '''def alphabeta(node, alpha, beta, is_max, seen):
    # your code here
    pass
''', [("alphabeta([[3, 12, 8], [2, 4, 6], [14, 5, 2]], -1000, 1000, True, [])", 3),
      ("(lambda s: (alphabeta([[3, 12, 8], [2, 4, 6], [14, 5, 2]], -1000, 1000, True, s), len(s)))([])", [3, 7]),
      ("(lambda s: (alphabeta([[2, 3], [5, 9], [0, 1], [7, 5]], -1000, 1000, False, s), s))([])", [1, [2, 3, 5, 0, 1, 7]]),
      ("alphabeta([[[2, 3], [5, 9]], [[0, 1], [7, 5]]], -1000, 1000, True, [])", 3)],
         '''def alphabeta(node, alpha, beta, is_max, seen):
    if type(node) == int:
        seen.append(node)
        return node
    if is_max:
        value = -1000
        for child in node:
            value = max(value, alphabeta(child, alpha, beta, False, seen))
            if value >= beta:
                return value
            alpha = max(alpha, value)
        return value
    value = 1000
    for child in node:
        value = min(value, alphabeta(child, alpha, beta, True, seen))
        if value <= alpha:
            return value
        beta = min(beta, value)
    return value
''', 'Copy minimax, then stop the loop at a MAX node when value ≥ β, and at a MIN node when value ≤ α.', '<p>Test 4 is the alpha beta example of the slides, with root value 3.</p>')

K.must('Five moves', 'Name the model, write the formula, check its conditions, work step by step, say what it means.')
K.must('Search traps', 'Admissible is not enough for graph search without reopening. IDS costs about b ÷ (b − 1) times BFS.')
K.must('CSPs and games', 'Tree CSP O(n d²). Alpha beta best case b^⌈d/2⌉ + b^⌊d/2⌋ − 1. Expectimax needs real values.')
K.must('Logic and planning', 'Resolution refutes KB ∧ ¬α. Occurs check. Regress: (goal − add) ∪ pre. Promotion or demotion.')
K.must('Uncertainty and RL', 'Base rates. Observed descendant opens a collider. ‖BU − BU′‖ ≤ γ ‖U − U′‖. Q += α (r + γ max Q′ − Q).')

T = K.topic(
    slug='core-challenge', topic='core-challenge', step=STEP11,
    title='Challenge problems across Core AI', short='Challenge problems', badge='11.1', minutes=75,
    lead='Twenty one hard problems in the style of top university exams, one set for each step of Core AI, then the proofs examiners ask for and a guide for choosing a method.',
    desc='Hard mixed problems on search with inconsistent heuristics, iterative deepening cost and the effective branching factor, AC-3, tree CSPs and simulated annealing, alpha beta pruning and its best case, expectimax under a change of scale, resolution, model counting and unification, the Sussman anomaly, regression and threats, Bayes rule with base rates, network parameter counts and colliders, value iteration contraction and bounds, and Q-learning, with proofs of A* optimality, alpha beta correctness, Bellman contraction, resolution soundness and tree CSP solving.',
    summary='Hard exam style problems across every Core AI step, with proofs and a method guide.',
    keywords=['challenge problems', 'hard questions', 'proofs', 'A* optimality', 'alpha beta', 'resolution', 'Sussman anomaly', 'Bayes rule', 'value iteration', 'Q-learning'],
    recap='<p>Name the model, check the conditions, then compute. Know the five classic proofs.</p>',
    nb={'trap': 'A* with an inconsistent heuristic', 'ab': 'Alpha beta with a leaf counter', 'ac3': 'AC-3 on X < Y < Z', 'vi2': 'Value iteration as a contraction'})
