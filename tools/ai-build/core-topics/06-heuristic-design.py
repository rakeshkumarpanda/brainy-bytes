# Chapter 3.2: designing heuristics. Source: slide Set 2, slides 54 to 57 and 67 to 70 (what a heuristic is, food
# for thought IV and V on finding and comparing heuristics) and the class of 31 January 2026. The 8 puzzle
# heuristics, relaxed problems, dominance, pattern databases and the effective branching factor follow Russell and
# Norvig, AIMA 4th ed., section 3.6. The table of nodes generated is our own run: 100 random 8 puzzle states for
# each solution depth, graph search, counting generated nodes (tools in this repository can reproduce it).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('h12', r'''
# Two heuristics for the 8 puzzle. A state is a list of 9 numbers read row by row, 0 is the blank.
start = [7, 2, 4,
         5, 0, 6,
         8, 3, 1]
goal = [0, 1, 2,
        3, 4, 5,
        6, 7, 8]

def misplaced(state):                     # h1: tiles not in their goal square
    count = 0
    for i in range(9):
        if state[i] != 0 and state[i] != goal[i]:
            count = count + 1
    return count

def manhattan(state):                     # h2: total up, down, left, right distance of every tile
    total = 0
    for i in range(9):
        tile = state[i]
        if tile != 0:
            j = goal.index(tile)
            total = total + abs(i // 3 - j // 3) + abs(i % 3 - j % 3)
    return total

print("h1 =", misplaced(start))
print("h2 =", manhattan(start))
''')

K.code('bstar', r'''
# Effective branching factor: find b so that 1 + b + b^2 + ... + b^d = N + 1.
# We use halving (bisection): the left side grows with b, so we can squeeze b between two bounds.
def tree_size(b, d):
    total = 0
    for i in range(d + 1):
        total = total + b ** i
    return total

def effective_b(N, d):
    low = 1.0
    high = 10.0
    for step in range(20):
        mid = (low + high) / 2
        if tree_size(mid, d) < N + 1:
            low = mid
        else:
            high = mid
    return round(low, 2)

print("N = 52, d = 5:", effective_b(52, 5))
# try effective_b(57, 12) and effective_b(164, 12), the A* runs with h2 and h1 at depth 12
''')

K.lesson('idea', 'Two heuristics for the 8 puzzle', f'''
{src('slide Set 2, slides 54 to 56 (food for thought IV), and AIMA 4th ed., section 3.6.')}
<p>The 8 puzzle has 8 numbered tiles and one blank on a 3 × 3 board. A move slides a tile into the blank. The average solution of a random puzzle is about 22 moves, and there are 9! ⁄ 2 = 181,440 reachable states. Two classic heuristics:</p>
{fxs(
    fx('h1: misplaced tiles', 'h1(n) = number of tiles not in their goal square', 'Every misplaced tile needs at least one move.'),
    fx('h2: Manhattan distance', 'h2(n) = ∑<sub>tiles</sub> (|row − goal row| + |column − goal column|)', 'Every tile needs at least as many moves as its distance in rows plus columns.', key=True))}
{viz('puzzle8', s='7 2 4 5 0 6 8 3 1', t='0 1 2 3 4 5 6 7 8')}
{code('h12')}
<p>For the textbook start state, all 8 tiles are misplaced, so h1 = 8, and h2 = 3 + 1 + 2 + 2 + 2 + 3 + 3 + 2 = 18. The true solution needs 26 moves. Both heuristics are admissible, and h2 is closer to the truth.</p>
{wwh('A good heuristic is admissible (never too big) and as large as possible, so it is close to the true cost h*.',
     'The closer h is to h*, the fewer nodes A* expands. With h = h* A* walks straight to the goal. With h = 0 it is uniform cost search.',
     'Find h by solving an easier version of the problem exactly (a relaxed problem), or by storing exact costs of sub problems (pattern databases), and take the max of several admissible heuristics.')}
''', kw=['8 puzzle', 'misplaced tiles', 'Manhattan distance', 'h1', 'h2', 'admissible heuristic'])

K.lesson('relax', 'Relaxed problems: where heuristics come from', f'''
<p>A <b>relaxed problem</b> has fewer rules than the real one. Every solution of the real problem is still a solution of the relaxed one, so the cost of the optimal relaxed solution can never be larger than the real optimal cost. That makes it an admissible heuristic. It is also consistent, because it is an exact cost in a real (relaxed) problem.</p>
{table(['Real rule: a tile can move from square A to square B if', 'Remove this part', 'Heuristic you get'], [
    ['A is next to B and B is blank', '"and B is blank"', 'h2: Manhattan distance'],
    ['A is next to B and B is blank', '"A is next to B"', 'Gaschnig\'s heuristic: number of swaps with the blank'],
    ['A is next to B and B is blank', 'both conditions', 'h1: misplaced tiles (each tile jumps in one move)']])}
{table(['Problem', 'Relaxation', 'Heuristic'], [
    ['Romania road trip', 'You may fly in a straight line', 'Straight line distance h<sub>SLD</sub>'],
    ['Robot on a grid with walls', 'No walls', 'Manhattan or octile distance'],
    ['Water jugs, get 2 litres', 'Pour any amount you like', '0 if a jug holds 2, else 1'],
    ['Travelling salesperson', 'The tour need not be a cycle', 'Cost of a minimum spanning tree']])}
{note('The relaxed problem must be easy to solve, or computing h will cost more than the search saves. Manhattan distance is a sum of independent tile problems, which takes 9 small steps.', 'tip')}
{scene('food for thought V from the slides', '<p>Making a cup of tea: a relaxation lets you do every step at once, so h = number of steps not done yet (water not boiled, no tea, no milk, ...). It is admissible because every step must still be done at least once. For buying a book, h = number of checkout stages left. For a doctor, h might be the number of tests still needed to separate the remaining possible diseases.</p>')}
''', kw=['relaxed problem', 'relaxation', 'Gaschnig', 'minimum spanning tree', 'straight line distance'])

K.lesson('dominance', 'Dominance and combining heuristics', f'''
{fxs(
    fx('Dominance', 'h2 dominates h1 if h2(n) ≥ h1(n) for every n, and both are admissible', 'Then A* with h2 expands no more nodes than A* with h1 (apart from ties).', key=True),
    fx('Why', 'A* surely expands every n with f(n) &lt; C*, that is h(n) &lt; C* − g(n)', 'A node with h2(n) &lt; C* − g(n) also has h1(n) &lt; C* − g(n). So every node expanded with h2 is also expanded with h1.'),
    fx('Combining', 'h(n) = max(h1(n), ..., hk(n))', 'The max of admissible heuristics is admissible, and it dominates each of them. The max of consistent heuristics is consistent.', key=True))}
{steps('Worked example: Manhattan dominates misplaced', [
    'A misplaced tile is at distance at least 1 from its goal square.',
    'So each misplaced tile adds 1 to h1 and at least 1 to h2. A tile in place adds 0 to both.',
    'So h2(n) ≥ h1(n) for every n.',
    eq('the start state: h2 = 18 ≥ h1 = 8')])}
<h3>How much it helps: our own experiment</h3>
<p>We solved 100 random 8 puzzle states for each depth d with graph search A* and counted the nodes generated on average.</p>
{table(['Depth d', 'BFS nodes', 'A*(h1) nodes', 'A*(h2) nodes', 'b* BFS', 'b* h1', 'b* h2'], [
    ['2', '7', '6', '6', '2.15', '2.00', '2.00'],
    ['6', '81', '17', '15', '1.83', '1.31', '1.26'],
    ['10', '602', '72', '34', '1.74', '1.35', '1.21'],
    ['12', '1,580', '164', '57', '1.72', '1.38', '1.23'],
    ['16', '10,198', '953', '207', '1.68', '1.42', '1.27'],
    ['20', '47,880', '5,508', '725', '1.63', '1.45', '1.29']])}
<p>At depth 20, Manhattan distance generates about 66 times fewer nodes than BFS and 7.6 times fewer than misplaced tiles. On the textbook start (depth 26), A* generated 62,443 nodes with h1 and 6,172 with h2.</p>
''', kw=['dominance', 'max of heuristics', 'effective branching factor', 'experiment'])

K.lesson('pdb', 'Pattern databases and learned heuristics', f'''
{wwh('A pattern database (PDB) stores the exact cost to solve a sub problem, for example to put tiles 1 to 4 in place while the other tiles count as "don\'t care", for every possible position of those tiles.',
     'Manhattan distance treats tiles as independent, so it misses how tiles block each other. A PDB captures those interactions exactly for a group of tiles, giving a much larger admissible h.',
     'Before the search, run a backward BFS from the goal in the abstract space of the pattern tiles and store each cost in a table. During the search, look up the pattern of the current state. Take the max over several PDBs.')}
{fxs(
    fx('Disjoint pattern databases', 'h = PDB(tiles 1 to 4) + PDB(tiles 5 to 8)', 'Adding two PDBs is admissible only if each counts only the moves of its own tiles. Then no move is counted twice.', key=True),
    fx('Size of a PDB', 'for k pattern tiles plus the blank on 9 squares: 9! ⁄ (9 − k − 1)! entries', 'For k = 4: 9 × 8 × 7 × 6 × 5 = 15,120 entries.'))}
{deep('learning heuristics from data', '<p>A heuristic can be learned: solve many random instances, record features of each state (Manhattan distance, linear conflicts, number of tiles in the right row) and the true cost, and fit a model such as a linear regression h(n) = c1 x1(n) + c2 x2(n). A learned h is usually not admissible, so A* loses its guarantee, but it can find near optimal answers much faster. DeepCubeA (2019) learned a neural network heuristic for the Rubik\'s cube with reinforcement learning and solved it with weighted A*.</p>')}
''', kw=['pattern database', 'disjoint pattern database', 'learned heuristic', 'DeepCubeA'])

K.lesson('maths', 'The maths: effective branching factor', f'''
{fxs(fx('Effective branching factor b*', 'N + 1 = 1 + b* + (b*)² + ... + (b*)<sup>d</sup>', 'N nodes generated for a solution at depth d. b* is the branching factor a uniform tree of depth d would need to hold N + 1 nodes. A good heuristic has b* close to 1.', key=True))}
{steps('Worked example: N = 52, d = 5', [
    'We need 1 + b + b² + b³ + b⁴ + b⁵ = 53.',
    'b = 1.9: 1 + 1.9 + 3.61 + 6.86 + 13.03 + 24.76 = 51.2, a bit low.',
    'b = 1.92: 1 + 1.92 + 3.69 + 7.08 + 13.59 + 26.09 = 53.4, a bit high.',
    eq('b* ≈ 1.92')])}
{code('bstar')}
{steps('Worked example: what one heuristic is worth', [
    'At d = 20, b* = 1.63 for BFS and 1.29 for A*(h2).',
    '1.63²⁰ ≈ 17,500 and 1.29²⁰ ≈ 163.',
    eq('a smaller b* compounds over every level, which is why a good h wins by orders of magnitude')])}
''', kw=['effective branching factor', 'bisection', 'b star'])

K.lesson('compare', 'Comparing heuristics', f'''
{versus('Heuristics for the 8 puzzle', ['Heuristic', 'Admissible', 'Value at the start state', 'Cost to compute', 'Nodes at d = 20'], [
    ['h = 0 (uniform cost)', 'Yes', '0', 'None', 'about 48,000 (BFS)'],
    ['h1 misplaced tiles', 'Yes', '8', '9 checks', '5,508'],
    ['h2 Manhattan', 'Yes', '18', '9 small sums', '725'],
    ['max(h1, h2)', 'Yes', '18 (= h2, since h2 dominates)', 'Both', '725'],
    ['Pattern database', 'Yes', 'At least as large as one group of tiles needs', 'One table lookup, after building the table', 'Much fewer'],
    ['h* (perfect)', 'Yes', '26', 'As hard as the problem', '26 (straight to the goal)']],
    'pick the largest admissible heuristic that is cheap to compute. Dominance tells you which is better without running anything.')}
{note('Larger is better only while h stays admissible. 2 × h2 is larger, but it overestimates, so A* may then return a longer solution.', 'warn')}
''', kw=['heuristic comparison', 'pattern database', 'perfect heuristic'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A heuristic is a smart guess. For the sliding puzzle, count how far each tile is from home. The better the guess, the less you need to try.</p>',
    '<p>Get admissible heuristics from relaxed problems. If h2 ≥ h1 everywhere, A* with h2 expands no more nodes. Measure a heuristic with the effective branching factor b*. Combine heuristics with max.</p>',
    '<p>Pattern databases store exact abstract costs, disjoint PDBs can be added, and the 15 puzzle is solved optimally in milliseconds with them. The time to compute h must be weighed against the nodes saved.</p>',
    '<p>Research looks at heuristics from abstraction hierarchies, landmark heuristics in planning (chapter 8.2), cost partitioning to add many heuristics safely, and neural heuristics trained by self play (DeepCubeA), with work on keeping bounded suboptimality when h is learned.</p>')}
''', kw=['abstraction', 'landmarks', 'cost partitioning'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '8 puzzle: h1 = misplaced tiles, h2 = Manhattan distance. The textbook start has h1 = 8, h2 = 18 and needs 26 moves.',
    'A <b>relaxed problem</b> removes rules. Its exact cost is an admissible and consistent heuristic (h1, h2, straight line distance).',
    '<b>Dominance</b>: if h2 ≥ h1 and both are admissible, A* with h2 expands no more nodes. The max of admissible heuristics is admissible.',
    '<b>Effective branching factor</b> b* solves N + 1 = 1 + b* + ... + (b*)<sup>d</sup>. At d = 20 we measured 1.63 for BFS, 1.45 for h1 and 1.29 for h2.',
    '<b>Pattern databases</b> store exact costs of sub problems. Disjoint ones can be added.'],
    'chapter 3.3 keeps A* optimal while cutting its memory, with IDA*, RBFS and SMA*.')}
{nbcard('heuristic-design', 'Compute misplaced tiles and Manhattan distance, measure the effective branching factor, and write both functions yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'h1 for the 8 puzzle counts', ['Moves made', 'Misplaced tiles', 'Total Manhattan distance', 'Blank moves'], 1,
       'Misplaced.', 'The number of tiles not in their goal square.')
K.quiz('e', 'For the textbook start 7 2 4 5 0 6 8 3 1, h2 is', ['8', '18', '26', '22'], 1,
       'Add the distances.', '3 + 1 + 2 + 2 + 2 + 3 + 3 + 2 = 18.')
K.quiz('e', 'Straight line distance on Romania comes from which relaxation?', ['Roads are one way', 'You may fly straight to the goal', 'Cities are merged', 'Costs are zero'], 1,
       'Ignore the roads.', 'Flying straight is never longer than driving.')
K.quiz('e', 'A heuristic with b* close to 1 is', ['Very good', 'Very bad', 'Inadmissible', 'Inconsistent'], 0,
       'Like a straight line.', 'b* = 1 means the search walks straight down to the goal.')
K.quiz('m', 'h2 dominates h1 means', ['h2 ≤ h1 everywhere', 'h2 ≥ h1 everywhere and both are admissible', 'h2 is faster to compute', 'h2 is inconsistent'], 1,
       'Bigger but still optimistic.', 'Then A* with h2 expands no more nodes than with h1.')
K.quiz('m', 'Why is the cost of an optimal relaxed solution admissible?', ['It is always 0', 'Every real solution is also a relaxed solution', 'It is random', 'It is computed by A*'], 1,
       'Fewer rules.', 'So the best relaxed solution is at most as costly as the best real one.')
K.quiz('m', 'Which combination of admissible h1, h2 is guaranteed admissible?', ['h1 + h2', 'max(h1, h2)', '2 × h1', 'h1 × h2'], 1,
       'The larger, not the sum.', 'max(h1, h2) ≤ h* because each is ≤ h*.')
K.quiz('m', 'Removing only "B is blank" from the 8 puzzle rule gives', ['h1', 'h2', 'Gaschnig', 'h = 0'], 1,
       'Tiles move to neighbours freely.', 'Each tile then needs exactly its Manhattan distance.')
K.quiz('h', 'When can two pattern database values be added and stay admissible?', ['Always', 'When the patterns use disjoint tiles and each counts only its own tiles\' moves', 'Never', 'Only for the 15 puzzle'], 1,
       'No double counting.', 'Then every real move is counted in at most one table.')
K.quiz('h', 'A learned heuristic from regression is usually', ['Admissible', 'Not guaranteed admissible', 'Always consistent', 'Equal to h*'], 1,
       'A fit can overestimate.', 'It may overestimate, so A* loses its optimality guarantee.')
K.quiz('x', 'In the style of a Stanford CS221 exam: h1 and h2 are admissible. Is h = (h1 + h2) ⁄ 2 admissible?', ['Yes, always', 'No, never', 'Only if h1 = h2', 'Only if consistent'], 0,
       'Average of two lower bounds.', 'If both are ≤ h*, so is their average. It is dominated by max(h1, h2).')
K.quiz('x', 'In the style of a CMU 15-381 exam: is the number of tiles out of their goal ROW plus the number out of their goal COLUMN admissible for the 8 puzzle?', ['Yes', 'No', 'Only for even states', 'Only if the blank is in place'], 0,
       'Each tile out of its row needs a vertical move.', 'A tile out of its row needs at least one up or down move and out of its column at least one sideways move. It is a relaxed bound, at most h2.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'h1 for the state 1 2 0 3 4 5 6 7 8 with goal 0 1 2 3 4 5 6 7 8.', '2', 'Compare each tile.',
       ['Square 0 holds 1 (goal 0, so tile 1 is out). Square 1 holds 2 (out).', 'Squares 3 to 8 match.', eq('h1 = 2')], check=2)
K.calc('e', 'h2 for the same state 1 2 0 3 4 5 6 7 8.', '2', 'Tile 1 is 1 column from home, tile 2 is 1 column from home.',
       ['Tile 1 at square 0, goal square 1: distance 1.', 'Tile 2 at square 1, goal square 2: distance 1.', eq('h2 = 2')], check=2)
K.calc('e', 'Size of a pattern database for 4 tiles plus the blank on 9 squares: 9 × 8 × 7 × 6 × 5.', '15120', 'Multiply.',
       ['9 × 8 = 72, × 7 = 504.', '504 × 6 = 3,024.', eq('3,024 × 5 = 15,120')], check=15120)
K.calc('m', 'Effective branching factor when N = 6 at depth d = 2. Solve 7 = 1 + b + b².', '2', 'b² + b − 6 = 0.',
       ['(b + 3)(b − 2) = 0.', 'b must be positive.', eq('b* = 2')], check=2)
K.calc('m', 'Effective branching factor for N = 52 at d = 5 (2 decimals).', '1.92', 'Bisection.',
       ['b = 1.9 gives 51.2, too low.', 'b = 1.92 gives 53.4, close to 53.', eq('b* ≈ 1.92')], check=1.92, tol=0.01)
K.calc('m', 'From our table at d = 20: how many times fewer nodes does A*(h2) generate than A*(h1)? 5,508 against 725, one decimal.', '7.6', 'Divide.',
       ['5,508 ⁄ 725.', '= 7.597.', eq('≈ 7.6')], check=5508 / 725, tol=0.05)
K.calc('m', 'Manhattan distance of a tile at square 8 (bottom right) whose goal is square 0 (top left).', '4', '2 rows and 2 columns.',
       ['Row 2 to row 0: 2.', 'Column 2 to column 0: 2.', eq('4')], check=4)
K.calc('h', 'b* = 1.29 at d = 20. Estimate (1.29)²⁰, the size of the last level, to the nearest whole number.', '163', 'Use powers.',
       ['1.29² = 1.664. 1.29⁴ = 2.769. 1.29⁵ = 3.572.', '1.29¹⁰ = 3.572² = 12.76.', eq('1.29²⁰ = 12.76² ≈ 163')], check=1.29 ** 20, tol=1)
K.calc('h', 'Start state 7 2 4 5 0 6 8 3 1: what is h2 − h1?', '10', '18 − 8.',
       ['h1 = 8.', 'h2 = 18.', eq('10')], check=10)
K.calc('x', 'In the style of an Oxford exam: the 15 puzzle has 16! ⁄ 2 reachable states. How many is that, in billions to 1 decimal?', '10461.4', '16! = 20,922,789,888,000.',
       ['16! = 20,922,789,888,000.', 'Half: 10,461,394,944,000.', eq('≈ 10,461.4 billion (about 10¹³)')], check=10461394944000 / 1e9, tol=0.1)

# ---------------------------------------------------------------- assignments
K.assign('h12', 'e', 'Misplaced tiles and Manhattan distance',
         '<p>Write <code>heuristics(state, goal)</code> for the 8 puzzle. Both are lists of 9 numbers (0 is the blank). Return [h1, h2]: misplaced tiles and Manhattan distance. Never count the blank.</p>',
         '''
def heuristics(state, goal):
    # your code here
    pass
''', [("heuristics([7, 2, 4, 5, 0, 6, 8, 3, 1], [0, 1, 2, 3, 4, 5, 6, 7, 8])", [8, 18]),
      ("heuristics([1, 0, 2, 3, 4, 5, 6, 7, 8], [0, 1, 2, 3, 4, 5, 6, 7, 8])", [1, 1]),
      ("heuristics([1, 2, 3, 4, 5, 6, 7, 8, 0], [1, 2, 3, 4, 5, 6, 7, 8, 0])", [0, 0])],
         '''
def heuristics(state, goal):
    h1 = 0
    h2 = 0
    for i in range(9):
        tile = state[i]
        if tile != 0:
            j = goal.index(tile)
            if i != j:
                h1 = h1 + 1
            h2 = h2 + abs(i // 3 - j // 3) + abs(i % 3 - j % 3)
    return [h1, h2]
''', 'Square i is at row i // 3 and column i % 3.', '<p>The first test is the textbook start: 8 and 18.</p>')
K.assign('ebf', 'm', 'Effective branching factor',
         '<p>Write <code>effective_b(N, d)</code> that returns b* rounded to 2 decimals, where 1 + b* + ... + (b*)<sup>d</sup> = N + 1. Use bisection between 1 and N + 1.</p>',
         '''
def effective_b(N, d):
    # your code here
    pass
''', [("effective_b(6, 2)", 2.0), ("effective_b(52, 5)", 1.92), ("effective_b(14, 3)", 2.0), ("effective_b(57, 12)", 1.23)],
         '''
def effective_b(N, d):
    low = 1.0
    high = N + 1.0
    for step in range(60):
        mid = (low + high) / 2
        total = 0
        for i in range(d + 1):
            total = total + mid ** i
        if total < N + 1:
            low = mid
        else:
            high = mid
    return round((low + high) / 2, 2)
''', 'The left side grows with b. If it is too small, move the low end up, else move the high end down.', '<p>57 nodes at depth 12 gives b* ≈ 1.23, the value of A*(h2) in our table.</p>')

K.must('8 puzzle heuristics', 'h1 misplaced tiles, h2 Manhattan distance. Textbook start: h1 = 8, h2 = 18, true cost 26.')
K.must('Relaxed problem', 'Remove rules. The exact relaxed cost is admissible and consistent.')
K.must('Dominance', 'h2 ≥ h1 and both admissible: A* with h2 expands no more nodes.')
K.must('Combining', 'max of admissible heuristics is admissible and dominates each one.')
K.must('Effective branching factor', 'N + 1 = 1 + b* + ... + (b*)<sup>d</sup>. Close to 1 is good.')
K.must('Pattern database', 'Exact costs of a sub problem, looked up during search. Disjoint PDBs can be added.')

T = K.topic(
    slug='heuristic-design', topic='heuristic-design', step=(3, 'Informed search', 'cai-informed', 'Search with a hint of where the goal is: greedy best first, A*, heuristic design, memory bounded and AND OR search.', 'College'),
    title='Designing and comparing heuristics', short='Heuristic design', badge='3.2', minutes=45,
    lead='Where good heuristics come from, how to tell which of two heuristics is better, and how to measure one. The 8 puzzle, relaxed problems, dominance, pattern databases and the effective branching factor.',
    desc='Misplaced tiles and Manhattan distance, relaxed problems, Gaschnig, dominance and its proof, the max of heuristics, pattern databases, learned heuristics, the effective branching factor and our own measured table.',
    summary='8 puzzle heuristics, relaxed problems, dominance, max, pattern databases and the effective branching factor.',
    keywords=['heuristic design', '8 puzzle', 'Manhattan distance', 'relaxed problem', 'dominance', 'pattern database', 'effective branching factor'],
    recap='<p>Relax the rules to get admissible heuristics, prefer the dominant one, and measure with b*.</p>',
    nb={'h12': 'Misplaced tiles and Manhattan distance on the 8 puzzle', 'bstar': 'Finding the effective branching factor'})
