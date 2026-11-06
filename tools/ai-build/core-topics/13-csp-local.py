# Chapter 5.3: local search for CSPs and the structure of problems. Source: the syllabus item "local search for CSPs"
# with slide Set 2, slides 78 and 79 (local search philosophy) and slide Set 4 (CSP formulation), and the class of
# 8 February 2026. Min-conflicts, its results on the million queens problem and the Hubble telescope, tree
# structured CSPs, cutset conditioning and tree decomposition follow Russell and Norvig, AIMA 4th ed., sections 6.4
# and 6.5. The min-conflicts run below is our own, with a fixed random seed.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('minconf', r'''
# Min-conflicts for 4 queens. board[c] is the row of the queen in column c.
import random
random.seed(2)
n = 4
board = [random.randrange(n) for c in range(n)]   # a random complete assignment

def conflicts(col, row):
    count = 0
    for c in range(n):
        if c != col and (board[c] == row or abs(board[c] - row) == abs(c - col)):
            count = count + 1
    return count

print("start:", board)
for step in range(10):
    attacked = [c for c in range(n) if conflicts(c, board[c]) > 0]
    if len(attacked) == 0:
        print("solved:", board)
        break
    col = random.choice(attacked)                 # a variable in conflict, picked at random
    counts = [conflicts(col, r) for r in range(n)]
    best = min(counts)
    board[col] = random.choice([r for r in range(n) if counts[r] == best])
    print("column", col, "attacks per row", counts, "-> move to row", board[col])
''')

K.code('tree', r'''
# Solving a tree shaped CSP with one pass backward and one pass forward.
# The tree: A is the root, B and C are children of A, D is a child of B. Every edge says "different colours".
order = ["A", "B", "C", "D"]                       # parents always come before children
parent = {"B": "A", "C": "A", "D": "B"}
domains = {"A": ["red", "green"], "B": ["red"], "C": ["red", "green"], "D": ["green", "red"]}

# backward pass: make each arc (parent, child) consistent, from the last child to the first
for child in reversed(order[1:]):
    p = parent[child]
    for v in domains[p][:]:
        partner = False
        for w in domains[child]:
            if w != v:
                partner = True
        if not partner:
            domains[p].remove(v)
            print("remove", v, "from", p, "because", child, "would have no colour left")
print("after the backward pass:", domains)

# forward pass: give each variable any value that fits its parent. No backtracking is ever needed.
value = {}
for x in order:
    for v in domains[x]:
        if x not in parent or v != value[parent[x]]:
            value[x] = v
            break
print("solution:", value)
''')

K.lesson('idea', 'Local search for CSPs: min-conflicts', f'''
{src('slide Set 2, slides 78 and 79, and slide Set 4.')}
{wwh('Min-conflicts starts with a complete assignment, maybe breaking many constraints, and repeatedly picks a variable that is in conflict and gives it the value that breaks the fewest constraints.',
     'Backtracking builds a solution one variable at a time and can get lost deep in a huge tree. For many large CSPs, solutions are spread densely all over the space, so starting from a full guess and repairing it is much faster.',
     'Assign every variable at random. Loop: if no constraint is broken, stop. Otherwise choose a conflicted variable at random, count the conflicts for each of its values, and move it to a value with the fewest conflicts (ties at random).')}
{algo('MIN-CONFLICTS (AIMA figure 6.8)', [
    'function MIN-CONFLICTS(csp, max_steps):',
    '    current = a complete assignment (random, or greedy)',
    '    for i = 1 to max_steps:',
    '        if current is a solution: return current',
    '        var = a randomly chosen conflicted variable',
    '        value = the value v of var that minimises CONFLICTS(var, v, current)',
    '        set var = value in current',
    '    return failure'])}
{viz('minconflicts', n=6, seed=48)}
{code('minconf')}
<p>AIMA reports that min-conflicts solves even the <b>million queens</b> problem in about 50 steps on average after the initial assignment, and that a min-conflicts style method cut the time to schedule a week of Hubble Space Telescope observations from three weeks to around 10 minutes.</p>
''', kw=['min-conflicts', 'local search for CSP', 'complete assignment', 'repair', 'million queens', 'Hubble'])

K.lesson('landscape', 'Plateaux, tabu search and constraint weighting', f'''
<p>Min-conflicts is hill climbing (chapter 4.1) with the number of broken constraints as the cost. It has the same traps: plateaux where every move keeps the same number of conflicts, and local minima.</p>
{viz('minconflicts', n=6, seed=9, max=40)}
{table(['Fix', 'Idea'], [
    ['Sideways moves', 'Allow moves to a value with the same number of conflicts, so the search can cross a plateau'],
    ['Tabu search', 'Keep a short list of recently visited states (or recently changed variables) and do not go back to them, so the search does not bounce between the same few states'],
    ['Constraint weighting', 'Give every constraint a weight, starting at 1. After each step, add 1 to the weight of every broken constraint. Minimise the total weight. Hard constraints that keep breaking become expensive, which changes the landscape and pushes the search out of local minima'],
    ['Random restarts and random walk', 'Start again, or sometimes make a random move instead of the best one'],
    ['Online repair', 'When the problem changes (a flight is cancelled), start min-conflicts from the old solution: only a few variables need to change']])}
{note('Local search cannot prove that a CSP has no solution. It just fails to find one. Backtracking with propagation can prove it, for example that 2 colours are not enough for Australia.', 'warn')}
''', kw=['plateau', 'tabu search', 'constraint weighting', 'random walk', 'online repair'])

K.lesson('structure', 'Using the shape of the problem: independent parts and trees', f'''
{fxs(
    fx('Independent sub problems', 'connected components solved separately: O(d<sup>c</sup> · n ⁄ c) instead of O(d<sup>n</sup>)', 'Tasmania is not connected to the mainland, so colour it on its own. If n = 80 splits into 4 parts of 20 with d = 2: 4 × 2²⁰ ≈ 4 million against 2⁸⁰ ≈ 10²⁴.', key=True),
    fx('Tree structured CSP', 'solvable in O(n d²)', 'If the constraint graph is a tree (no loops), there is no need to backtrack at all.', key=True))}
{steps('The tree algorithm', [
    'Pick any variable as the root and list the variables so that each parent comes before its children (a topological order).',
    'Backward pass: for j from n down to 2, make the arc (parent of X<sub>j</sub>, X<sub>j</sub>) arc consistent. This is called directional arc consistency.',
    'Forward pass: for j from 1 to n, give X<sub>j</sub> any value consistent with its parent\'s value.',
    eq('each arc is revised once at cost d², so the total is O(n d²), and the forward pass never gets stuck')])}
{code('tree')}
{viz('ac3', pre='custom', dom='A: 1 2 3 4\nB: 1 2 3 4\nC: 1 2 3 4\nD: 1 2 3 4', cons='A < B\nB < C\nC < D')}
<p>A chain A &lt; B &lt; C &lt; D is a tree. After arc consistency each variable has two values left, and a forward pass in order A, B, C, D always finds a solution, for example A = 1, B = 2, C = 3, D = 4.</p>
''', kw=['tree structured CSP', 'topological order', 'directional arc consistency', 'independent sub problems', 'O(n d squared)'])

K.lesson('cutset', 'Cutset conditioning and tree decomposition', f'''
{wwh('Cutset conditioning turns a graph with loops into a tree by assigning a few variables first. Tree decomposition groups variables into overlapping clusters that form a tree.',
     'Most real constraint graphs are not trees, but many are close to trees. Both methods use that closeness to get far below d<sup>n</sup>.',
     '<b>Cutset</b>: choose a set S of variables whose removal leaves a tree (a cycle cutset). For every consistent assignment of S, remove the values in the rest that clash with it, and solve the remaining tree in O((n − c) d²). <b>Tree decomposition</b>: solve each cluster as a mega variable whose values are the cluster\'s solutions, and join the clusters with the tree algorithm.')}
{fxs(
    fx('Cutset conditioning', 'O(d<sup>c</sup> · (n − c) d²)', 'c is the size of the cutset. Australia: removing SA leaves a tree (a chain plus T), so c = 1.', key=True),
    fx('Tree decomposition', 'O(n d<sup>w+1</sup>)', 'w is the tree width: the size of the largest cluster minus 1. CSPs with small tree width are easy.'))}
{steps('Worked example: Australia with the cutset {SA}', [
    'Assign SA one of 3 colours.',
    'Remove that colour from WA, NT, Q, NSW and V. They now form the chain WA, NT, Q, NSW, V, plus T on its own.',
    'Solve that tree in O((n − 1) d²) = 6 × 9 = 54 checks at most.',
    eq('total work at most 3 × 54 = 162 checks, against 3⁷ = 2,187 assignments')])}
''', kw=['cutset conditioning', 'cycle cutset', 'tree decomposition', 'tree width'])

K.lesson('maths', 'The maths of problem structure', f'''
{fxs(
    fx('Backtracking worst case', 'O(d<sup>n</sup>)', 'For any CSP.'),
    fx('Tree CSP', 'O(n d²)', 'Linear in n.'),
    fx('Cutset', 'O(d<sup>c</sup> (n − c) d²)', 'Exponential only in the cutset size c.'),
    fx('Tree decomposition', 'O(n d<sup>w+1</sup>)', 'Exponential only in the tree width w.'))}
{steps('Worked example: how much a tree saves', [
    'n = 20 variables, d = 3 values, the graph is a tree.',
    'Backtracking worst case: 3²⁰ ≈ 3.5 × 10⁹.',
    'Tree algorithm: 20 × 3² = 180 checks.',
    eq('about 19 million times less work')])}
{steps('Worked example: a cutset', [
    'A graph of n = 30 variables with d = 2 becomes a tree after removing c = 3 variables.',
    'd<sup>c</sup> = 2³ = 8 assignments of the cutset.',
    'Each leaves a tree of 27 variables: 27 × 2² = 108 checks.',
    eq('8 × 108 = 864 checks, against 2³⁰ ≈ 1.07 × 10⁹')])}
''', kw=['complexity of CSP methods', 'cutset example', 'tree example'])

K.lesson('compare', 'Backtracking against min-conflicts against structure', f'''
{versus('Three ways to solve a CSP', ['', 'Backtracking with propagation', 'Min-conflicts (local search)', 'Structure based (tree, cutset)'], [
    ['Starts from', 'An empty assignment', 'A complete random assignment', 'The shape of the constraint graph'],
    ['Complete (finds a solution if one exists)', 'Yes', 'No', 'Yes'],
    ['Can prove no solution', 'Yes', 'No', 'Yes'],
    ['Memory', 'O(n) for the path', 'O(n), one assignment', 'O(n d) for the domains'],
    ['Best on', 'Tight problems with few solutions', 'Large problems with many solutions spread out (N queens, scheduling)', 'Graphs that are trees or nearly trees'],
    ['N queens with a million queens', 'Very slow', 'About 50 steps (AIMA)', 'Not a tree']],
    'use min-conflicts when solutions are plentiful and the problem is big or keeps changing. Use backtracking with MRV and MAC when solutions are rare or you need a proof. Check the graph shape first: a tree is solved in linear time.')}
{scene('airline crew rescheduling', '<p>When a storm cancels flights, an airline must reassign crews quickly. Starting from scratch would move almost everyone. Min-conflicts style repair starts from yesterday\'s schedule, which is almost right, and changes only the crews involved in broken constraints. The new schedule is close to the old one, which crews and passengers prefer.</p>')}
''', kw=['comparison', 'crew rescheduling', 'complete', 'local search'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Min-conflicts is fixing a messy seating plan: put everyone somewhere, then keep moving one unhappy person to the seat where the fewest neighbours bother them, until everyone is happy.</p>',
    '<p>Min-conflicts: random full assignment, then move a conflicted variable to its least conflicting value. Very fast on N queens, but incomplete. Tree CSPs: O(n d²) with a backward arc consistency pass and a forward assignment pass. Cutset conditioning: O(d<sup>c</sup>(n − c)d²). Tree decomposition: O(n d<sup>w+1</sup>).</p>',
    '<p>Min-conflicts works well when the ratio of constraints to variables is low, because solutions are dense. Near the phase transition, where random problems switch from mostly solvable to mostly unsolvable, all methods slow down. Finding a minimum cycle cutset or an optimal tree decomposition is itself NP hard, so heuristics are used.</p>',
    '<p>Modern local search solvers for SAT and CSP (WalkSAT, constraint weighting methods such as breakout) are competitive on random instances, and hybrid solvers run local search and systematic search together, sharing learned clauses. Tree width also explains why Bayesian network inference (chapter 9.3) is easy on some graphs and hard on others.</p>')}
''', kw=['phase transition', 'WalkSAT', 'breakout', 'tree width', 'hybrid solvers'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Min-conflicts</b>: start from a complete assignment, pick a conflicted variable at random, move it to the value with the fewest conflicts. AIMA reports about 50 steps for a million queens.',
    'It is hill climbing on the number of broken constraints: helped by sideways moves, tabu lists, constraint weighting and restarts. It cannot prove that no solution exists.',
    '<b>Independent sub problems</b> are solved separately. <b>Tree structured</b> CSPs take O(n d²): directional arc consistency backward, then assign forward with no backtracking.',
    '<b>Cutset conditioning</b>: assign a cycle cutset of size c, then solve the tree, O(d<sup>c</sup>(n − c)d²). Australia has the cutset {SA}.',
    '<b>Tree decomposition</b>: O(n d<sup>w+1</sup>) for tree width w.'],
    'chapter 6.1 moves to games, where an opponent works against you: minimax.')}
{nbcard('csp-local', 'Run min-conflicts on 4 queens and the tree algorithm on a small map, then write min-conflicts for N queens and the tree solver yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Min-conflicts starts from', ['An empty assignment', 'A complete assignment', 'The goal', 'A single variable'], 1,
       'Repair, not build.', 'It assigns everything first, then repairs it.')
K.quiz('e', 'Which variable does min-conflicts change?', ['The first one', 'A randomly chosen variable that is in conflict', 'The one with the most values', 'All of them'], 1,
       'Only troubled ones.', 'A conflicted variable is chosen at random.')
K.quiz('e', 'A tree structured CSP can be solved in', ['O(d<sup>n</sup>)', 'O(n d²)', 'O(n!)', 'O(2<sup>n</sup>)'], 1,
       'Linear in n.', 'One arc consistency pass and one forward pass.')
K.quiz('e', 'Why can Tasmania be coloured on its own?', ['It is small', 'It shares no constraints with the mainland', 'It is red', 'It has degree 5'], 1,
       'Independent sub problem.', 'It is a separate connected component of the constraint graph.')
K.quiz('m', 'Min-conflicts is a form of', ['Breadth first search', 'Hill climbing on the number of broken constraints', 'A*', 'Minimax'], 1,
       'Local search.', 'It moves to a neighbour with the fewest conflicts.')
K.quiz('m', 'Which can min-conflicts NOT do?', ['Solve big N queens', 'Repair a schedule', 'Prove that no solution exists', 'Use random restarts'], 2,
       'Incomplete.', 'Failing to find a solution is not a proof that none exists.')
K.quiz('m', 'Removing which region turns the Australia graph into a tree?', ['WA', 'T', 'SA', 'V'], 2,
       'The hub.', 'SA touches all the other mainland regions. Without it they form a chain.')
K.quiz('m', 'Constraint weighting', ['Ignores hard constraints', 'Raises the weight of constraints that stay broken, changing the landscape', 'Removes constraints', 'Sorts variables'], 1,
       'Learning where it hurts.', 'Repeatedly broken constraints become expensive, which pushes the search out of local minima.')
K.quiz('h', 'The cost of cutset conditioning with a cutset of size c is', ['O(d<sup>n</sup>)', 'O(d<sup>c</sup> (n − c) d²)', 'O(c d)', 'O(n d<sup>c</sup>)'], 1,
       'Try every cutset assignment, then solve a tree.', 'd<sup>c</sup> assignments times a tree solve.')
K.quiz('h', 'In the tree algorithm, why is no backtracking needed in the forward pass?', ['Luck', 'The backward pass left only parent values that have a partner in every child', 'Domains are size 1', 'Trees have no constraints'], 1,
       'Directional arc consistency.', 'Every remaining value of a parent can be extended to each child, all the way down.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: a constraint graph has 10 variables, domain size 3, and a cycle cutset of size 2. What is the bound on the work, d<sup>c</sup> (n − c) d²?', ['648', '59,049', '90', '27'], 0,
       '3² × 8 × 9.', '9 × 8 × 9 = 648.')
K.quiz('x', 'In the style of a CMU 15-780 exam: why does min-conflicts get faster, not slower, per variable as N queens grows?', ['Larger boards have fewer solutions', 'Solutions become denser in the space, so a repair is almost always a few moves away', 'It uses more memory', 'It switches to backtracking'], 1,
       'Density of solutions.', 'For large N, a random placement is close to many solutions, so few repairs are needed.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Tree CSP with n = 10, d = 3: how many checks does n d² give?', '90', '10 × 9.',
       ['d² = 9.', 'n d² = 10 × 9.', eq('90')], check=90)
K.calc('e', 'Backtracking worst case for n = 10, d = 3: d<sup>n</sup>.', '59049', '3¹⁰.',
       ['3⁵ = 243.', '243².', eq('59,049')], check=3 ** 10)
K.calc('e', 'Pairs of queens among 4 queens (the most attacking pairs possible).', '6', '4 × 3 ⁄ 2.',
       ['4 × 3 = 12.', 'Each pair counted twice.', eq('6')], check=6)
K.calc('m', 'Cutset conditioning on Australia with c = 1, n = 7, d = 3: d<sup>c</sup> (n − c) d².', '162', '3 × 6 × 9.',
       ['d<sup>c</sup> = 3.', '(n − c) d² = 6 × 9 = 54.', eq('3 × 54 = 162')], check=162)
K.calc('m', 'Independent parts: n = 80 split into 4 parts of 20 with d = 2. Work 4 × 2²⁰?', '4194304', '2²⁰ = 1,048,576.',
       ['2²⁰ = 1,048,576.', '× 4.', eq('4,194,304')], check=4 * 2 ** 20)
K.calc('m', 'Tree decomposition with n = 50, d = 2 and tree width w = 3: n d<sup>w+1</sup>.', '800', '50 × 2⁴.',
       ['d<sup>w+1</sup> = 2⁴ = 16.', '50 × 16.', eq('800')], check=800)
K.calc('m', 'Cutset with n = 30, d = 2, c = 3: d<sup>c</sup> (n − c) d².', '864', '8 × 27 × 4.',
       ['2³ = 8.', '27 × 4 = 108.', eq('8 × 108 = 864')], check=864)
K.calc('h', 'Chain A &lt; B &lt; C &lt; D with domains {1, ..., 4}. How many solutions does it have?', '1', 'Strictly increasing from 4 values.',
       ['We need 4 different values in increasing order.', 'Only 1, 2, 3, 4.', eq('exactly 1 solution')], check=1)
K.calc('h', 'Same chain with domains {1, ..., 5}: number of solutions (choose 4 of 5 values in order).', '5', '5 choose 4.',
       ['Any 4 of the 5 values, sorted, give one solution.', '5 choose 4 = 5.', eq('5 solutions')], check=5)
K.calc('x', 'In the style of an IIT Madras exam: a min-conflicts step on 8 queens checks every row of the chosen column against all other queens. How many queen pair checks is that per step?', '56', '8 rows × 7 other queens.',
       ['8 rows to try.', 'Each row is checked against the 7 other queens.', eq('8 × 7 = 56 checks')], check=56)

# ---------------------------------------------------------------- assignments
K.assign('mcq', 'm', 'Min-conflicts for N queens',
         '<p>Write <code>min_conflicts(board, max_steps, seed)</code>. board[c] is the row of the queen in column c. Call random.seed(seed) first. Each step: list the attacked columns. If there are none, return the board. Otherwise pick one with random.choice, count its conflicts in every row, and move it to a row with the fewest conflicts (random.choice among ties). After max_steps return the board as it is. A helper count_attacks is given for the checks.</p>',
         '''
import random

def count_attacks(board):
    count = 0
    for c1 in range(len(board)):
        for c2 in range(c1 + 1, len(board)):
            if board[c1] == board[c2] or abs(board[c1] - board[c2]) == c2 - c1:
                count = count + 1
    return count

def min_conflicts(board, max_steps, seed):
    # your code here
    pass
''', [("count_attacks(min_conflicts([0, 0, 0, 0, 0, 0, 0, 0], 300, 1))", 0),
      ("count_attacks(min_conflicts([4, 5, 6, 3, 4, 5, 6, 5], 300, 3))", 0),
      ("count_attacks(min_conflicts([0] * 20, 300, 2))", 0),
      ("min_conflicts([1, 3, 0, 2], 10, 5)", [1, 3, 0, 2])],
         '''
import random

def count_attacks(board):
    count = 0
    for c1 in range(len(board)):
        for c2 in range(c1 + 1, len(board)):
            if board[c1] == board[c2] or abs(board[c1] - board[c2]) == c2 - c1:
                count = count + 1
    return count

def min_conflicts(board, max_steps, seed):
    random.seed(seed)
    board = board[:]
    n = len(board)

    def conflicts(col, row):
        count = 0
        for c in range(n):
            if c != col and (board[c] == row or abs(board[c] - row) == abs(c - col)):
                count = count + 1
        return count

    for step in range(max_steps):
        attacked = []
        for c in range(n):
            if conflicts(c, board[c]) > 0:
                attacked.append(c)
        if len(attacked) == 0:
            return board
        col = random.choice(attacked)
        counts = []
        for r in range(n):
            counts.append(conflicts(col, r))
        best = min(counts)
        rows = []
        for r in range(n):
            if counts[r] == best:
                rows.append(r)
        board[col] = random.choice(rows)
    return board
''', 'Write a helper conflicts(col, row) inside the function. Build the list of attacked columns and the list of best rows with plain loops.', '<p>With random choices the search almost never cycles. Try the same board with a different seed: the solution may differ, but it is found in a few dozen steps. If you always picked the first attacked column and the first best row instead, the search would often go round in circles.</p>')
K.assign('treecsp', 'h', 'Solve a tree CSP',
         '<p>Write <code>solve_tree(order, parent, domains)</code> for a tree CSP where every edge means "different values". order lists the variables with parents first. Do the backward pass (remove parent values with no different value left in the child), then the forward pass (first value in the domain that differs from the parent). Return the assignment dict, or None if a domain becomes empty.</p>',
         '''
def solve_tree(order, parent, domains):
    # your code here
    pass
''', [("solve_tree(['A', 'B', 'C', 'D'], {'B': 'A', 'C': 'A', 'D': 'B'}, {'A': ['red', 'green'], 'B': ['red'], 'C': ['red', 'green'], 'D': ['green', 'red']})", {'A': 'green', 'B': 'red', 'C': 'red', 'D': 'green'}),
      ("solve_tree(['A', 'B'], {'B': 'A'}, {'A': ['x'], 'B': ['x']})", None),
      ("solve_tree(['A'], {}, {'A': ['x', 'y']})", {'A': 'x'})],
         '''
def solve_tree(order, parent, domains):
    dom = {}
    for v in domains:
        dom[v] = list(domains[v])
    for child in reversed(order[1:]):
        p = parent[child]
        for v in dom[p][:]:
            partner = False
            for w in dom[child]:
                if w != v:
                    partner = True
            if not partner:
                dom[p].remove(v)
        if len(dom[p]) == 0:
            return None
    value = {}
    for x in order:
        chosen = None
        for v in dom[x]:
            if x not in parent or v != value[parent[x]]:
                chosen = v
                break
        if chosen is None:
            return None
        value[x] = chosen
    return value
''', 'Walk the order backwards for the first pass and forwards for the second. Copy the domains first.', '<p>B can only be red, so A loses red in the backward pass, exactly as in the lesson.</p>')

K.must('Min-conflicts', 'Complete random assignment, move a random conflicted variable to its least conflicting value. About 50 steps for a million queens (AIMA).')
K.must('Escaping traps', 'Sideways moves, tabu search, constraint weighting, restarts. Local search cannot prove no solution.')
K.must('Tree CSP', 'O(n d²): directional arc consistency backward, then assign forward, no backtracking.')
K.must('Cutset conditioning', 'O(d<sup>c</sup>(n − c)d²). Australia: cutset {SA}.')
K.must('Tree decomposition', 'O(n d<sup>w+1</sup>), w = tree width.')

T = K.topic(
    slug='csp-local', topic='csp-local', step=(5, 'Constraint satisfaction', 'cai-csp', 'Problems made of variables, domains and constraints: arc consistency, backtracking with smart ordering, and local search.', 'College'),
    title='Local search for CSPs and problem structure', short='Min-conflicts and structure', badge='5.3', minutes=45,
    lead='Repair a complete assignment instead of building one: min-conflicts solves huge N queens problems in a few steps. Then use the shape of the constraint graph: trees are solved in linear time, and cutsets turn near trees into trees.',
    desc='Min-conflicts and its results, plateaux, tabu search and constraint weighting, independent sub problems, tree structured CSPs in O(nd²), cutset conditioning, tree decomposition and a comparison with backtracking.',
    summary='Min-conflicts local search, tabu and weighting, tree CSPs, cutset conditioning and tree decomposition.',
    keywords=['min-conflicts', 'local search CSP', 'tree structured CSP', 'cutset conditioning', 'tree decomposition', 'tabu search'],
    recap='<p>Repair a full assignment with min-conflicts, or exploit tree shape to solve without backtracking.</p>',
    nb={'minconf': 'Min-conflicts on 4 queens', 'tree': 'Solving a tree shaped CSP'})
