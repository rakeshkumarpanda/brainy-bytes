# Chapter 4.1: local search, hill climbing and simulated annealing. Source: slide Set 2, slides 77 to 83 and 87
# (beyond classical search, the ballpark of 10^100 states, the basic philosophy of local search, the state space
# landscape, local maxima, ridges and plateaux, simulated annealing with exploration and exploitation, the table of
# e^x values, the five cooling schedules and their parameters, food for thought VI) and the class of 1 February 2026.
# The 8 queens figures are our own run of 2,000 random boards (AIMA 4th ed., section 4.1, reports 14 and 94 percent).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('queens', r'''
# The 8 queens objective: h = number of pairs of queens that attack each other.
# board[c] is the row of the queen in column c (one queen per column).
def attacking_pairs(board):
    count = 0
    n = len(board)
    for c1 in range(n):
        for c2 in range(c1 + 1, n):
            same_row = board[c1] == board[c2]
            same_diagonal = abs(board[c1] - board[c2]) == c2 - c1
            if same_row or same_diagonal:
                count = count + 1
    return count

print("h =", attacking_pairs([4, 5, 6, 3, 4, 5, 6, 5]))   # the textbook start state, h = 17
print("h =", attacking_pairs([0, 4, 7, 5, 2, 6, 1, 3]))   # a solution, h = 0
''')

K.code('anneal', r'''
# Hill climbing and simulated annealing on a small landscape. value[x] is the height of state x.
# Neighbours of x are x - 1 and x + 1. We want the highest point.
import math
import random

value = [1, 3, 5, 4, 4, 6, 7, 9, 6, 3]

def hill_climb(x):
    while True:
        best = x
        for n in [x - 1, x + 1]:
            if 0 <= n < len(value) and value[n] > value[best]:
                best = n
        if best == x:
            return x                      # no neighbour is higher: a peak (maybe only a local one)
        x = best

def anneal(x, T, alpha, rounds, seed):
    random.seed(seed)
    for k in range(rounds):
        n = x + random.choice([-1, 1])
        if n < 0 or n >= len(value):
            continue
        delta = value[n] - value[x]
        if delta > 0 or random.random() < math.exp(delta / T):
            x = n                         # always go up, sometimes go down
        T = T * alpha                     # geometric cooling
    return x

print("hill climbing from 1 stops at", hill_climb(1), "with height", value[hill_climb(1)])
x = anneal(1, 5.0, 0.85, 30, 4)
print("annealing from 1 ends at", x, "with height", value[x])
# Annealing is random. Over seeds 0 to 199 it reaches the top (x = 7) in 90 runs. Hill climbing from 1 never does.
''')

K.lesson('idea', 'Local search: forget the path, improve the state', f'''
{src('slide Set 2, slides 77 to 80, and the class of 1 February 2026.')}
<p>The search methods so far explore paths systematically. They can handle spaces of up to roughly 10<sup>100</sup> states (about 500 binary variables, a ballpark number). Some real problems are far bigger, for example 10<sup>30,000</sup> states. And in many problems, like 8 queens or timetabling, only the final state matters, not the path to it.</p>
{wwh('Local search keeps one current state (or a few) and moves to a neighbouring state that is better, judged by an objective function. It does not store paths.',
     'It uses very little memory, usually a constant amount, and it can find good solutions in huge or even continuous spaces where systematic search is hopeless.',
     'Start from a guess (often random, maybe not even valid). Measure its quality. Make a small local change using a neighbourhood function. Repeat until a goal is found, time runs out, or the result is good enough.')}
<p>Picture the <b>state space landscape</b>: each state is a location, and its objective value is the height. Maximising means finding the highest peak (the global maximum). Minimising a cost means finding the lowest valley (the global minimum). The same ideas work for both by flipping the sign.</p>
{table(['Feature of the landscape', 'What it is', 'Why it is a problem'], [
    ['Local maximum', 'A peak higher than all its neighbours but lower than the global maximum', 'Every move goes down, so a greedy climber stops'],
    ['Ridge', 'A narrow line of peaks with slopes on both sides', 'No single move goes up along the ridge, so the climber zig zags slowly'],
    ['Plateau: flat local maximum', 'A flat area with no uphill exit', 'No neighbour is better'],
    ['Plateau: shoulder', 'A flat area from which you can still go up later', 'The climber cannot see that, and stops unless it may move sideways']])}
''', kw=['local search', 'objective function', 'state space landscape', 'local maximum', 'ridge', 'plateau', 'shoulder'])

K.lesson('hc', 'Hill climbing', f'''
{wwh('Steepest ascent hill climbing moves to the best neighbour, as long as it is better than the current state. It stops when no neighbour is better.',
     'It is the simplest local search: fast, almost no memory, and often good enough. Each step uses only the current state.',
     'Compute the objective of every neighbour. If the best one is higher, move there. Otherwise stop and return the current state, which is a peak, but maybe only a local one.')}
{viz('hillclimb', alg='hc', land='slide', x0=56)}
{algo('Steepest ascent hill climbing', [
    'function HILL-CLIMBING(problem):',
    '    current = initial state',
    '    loop:',
    '        neighbour = the highest valued successor of current',
    '        if VALUE(neighbour) <= VALUE(current): return current',
    '        current = neighbour'])}
<h3>8 queens</h3>
<p>States: 8 queens, one per column. A move: move one queen within its column, so each state has 8 × 7 = 56 neighbours. The cost h is the number of attacking pairs, which we want to bring down to 0.</p>
{code('queens')}
{table(['Method on random 8 queens boards (our run, 2,000 boards)', 'Solved', 'Average steps when it works', 'Average steps when stuck'], [
    ['Steepest ascent hill climbing', '14.8 percent', '4.0', '3.1'],
    ['With up to 100 sideways moves', '93.8 percent', '19.3', '60.9']])}
<p>Hill climbing is fast (only about 4 steps), but it gets stuck on 85 percent of the boards. The state space has 8⁸ ≈ 16.8 million states.</p>
''', kw=['hill climbing', 'steepest ascent', '8 queens', 'attacking pairs', 'greedy local search'])

K.lesson('variants', 'Ways out: sideways moves, randomness and restarts', f'''
{table(['Variant', 'Idea', 'Helps with'], [
    ['Sideways moves', 'Allow moves to an equal valued neighbour, up to a limit (to avoid looping on a flat top)', 'Shoulders'],
    ['Stochastic hill climbing', 'Pick a random uphill move, with more chance for steeper ones', 'Some ridges, slower but sometimes better'],
    ['First choice hill climbing', 'Generate random neighbours until one is better, take it', 'States with thousands of neighbours'],
    ['Random restart hill climbing', 'Run hill climbing again from new random starts, keep the best result', 'Local maxima. Complete with probability approaching 1'],
    ['Local beam search', 'Keep k states. Generate all their successors, keep the best k overall', 'Shares information between the k searches'],
    ['Stochastic beam search', 'Keep k successors chosen at random, better ones more likely', 'Stops all k states crowding onto one hill']])}
{viz('hillclimb', alg='side', land='slide', x0=8, side=12)}
{fxs(fx('Random restart', 'expected restarts = 1 ⁄ p', 'p is the chance one run succeeds. For 8 queens p ≈ 0.148, so about 7 runs: 6 failures (about 3 steps each) and 1 success (about 4 steps), roughly 22 steps in all.', key=True))}
{note('Local beam search is not k independent restarts. If one state finds a great region, its children can fill all k places, so the search moves its effort to where the progress is.', 'tip')}
''', kw=['sideways moves', 'stochastic hill climbing', 'first choice', 'random restart', 'local beam search', 'stochastic beam search'])

K.lesson('sa', 'Simulated annealing', f'''
{src('slide Set 2, slides 82 and 83.')}
{wwh('Simulated annealing is hill climbing that sometimes accepts a worse move. The chance of accepting a worse move depends on how much worse it is and on a temperature T that slowly goes down.',
     'A pure climber never goes down, so it gets stuck on the first peak. A random walk explores but never settles. Annealing starts like a random walk (exploration) and ends like a climber (exploitation), so it can escape local peaks early and settle on a good one later.',
     'Pick a random neighbour. If it is better, move. If it is worse by ΔE &lt; 0, move with probability e<sup>ΔE⁄T</sup>. Lower T after each step by the cooling schedule.')}
{fxs(
    fx('Acceptance probability', 'P(accept) = e<sup>ΔE ⁄ T</sup> for ΔE &lt; 0, and 1 for ΔE ≥ 0', 'High T: P near 1, almost any move is accepted. Low T: P near 0, only uphill moves.', key=True),
    fx('Why the slide table', 'as T grows, ΔE ⁄ T → 0 and e<sup>ΔE⁄T</sup> → e<sup>0</sup> = 1', 'The slide lists e<sup>x</sup> for x = 1, 1⁄2, 1⁄4, ..., 1⁄1024: 2.718, 1.649, 1.284, ..., 1.001. As the exponent shrinks, the value approaches 1.'))}
{table(['Cooling schedule (slide 83)', 'Formula', 'Comment'], [
    ['Geometric', 'T<sub>k+1</sub> = α T<sub>k</sub>, 0.8 ≤ α ≤ 1', 'The most common. α near 1 cools slowly and explores longer.'],
    ['Linear', 'T<sub>k</sub> = T<sub>0</sub> − k ΔT', 'Drops by the same amount each step.'],
    ['Logarithmic', 'T<sub>k</sub> = C ⁄ ln(k + 2)', 'C = the highest energy barrier to cross. Very slow, but with it annealing finds the global optimum with probability approaching 1.'],
    ['Constant', 'T<sub>k</sub> = C', 'This is the Metropolis algorithm, no cooling.'],
    ['Exponential', 'T<sub>k</sub> = T<sub>0</sub> α<sup>k</sup>', 'The closed form of geometric cooling.']])}
{viz('hillclimb', alg='sa', land='slide', x0=56, T0=30, al=0.9, seed=4)}
{code('anneal')}
{note('Choose T0 so that most worse moves are accepted at the start, often from the average cost difference between neighbours. Too fast cooling turns annealing into plain hill climbing.', 'tip')}
''', kw=['simulated annealing', 'temperature', 'acceptance probability', 'cooling schedule', 'geometric cooling', 'logarithmic cooling', 'exploration', 'exploitation'])

K.lesson('maths', 'The maths: acceptance, restarts and gradients', f'''
{steps('Worked example: acceptance probability', [
    'A worse move with ΔE = −2.',
    'At T = 10: e<sup>−2⁄10</sup> = e<sup>−0.2</sup> ≈ 0.819. Accepted about 82 percent of the time.',
    'At T = 1: e<sup>−2</sup> ≈ 0.135.',
    eq('at T = 0.2: e<sup>−10</sup> ≈ 0.0000454, almost never')])}
{steps('Worked example: geometric cooling', [
    'T0 = 100, α = 0.9. After k steps T = 100 × 0.9<sup>k</sup>.',
    'We want T &lt; 1: 0.9<sup>k</sup> &lt; 0.01, so k &gt; ln 0.01 ⁄ ln 0.9 = 4.605 ⁄ 0.1054 ≈ 43.7.',
    eq('44 steps to cool from 100 to below 1')])}
{fxs(
    fx('Gradient ascent for continuous states', 'x ← x + η ∇f(x)', 'In continuous spaces, move a small step η along the gradient. Too big η overshoots, too small is slow.', key=True),
    fx('Newton Raphson step', 'x ← x − H<sub>f</sub>(x)<sup>−1</sup> ∇f(x)', 'Uses the second derivatives (Hessian H) to choose the step. Very fast near an optimum.'),
    fx('Probability of success with r restarts', '1 − (1 − p)<sup>r</sup>', 'p = 0.148, r = 10: 1 − 0.852¹⁰ ≈ 0.80.'))}
''', kw=['acceptance probability', 'geometric cooling', 'gradient ascent', 'Newton Raphson', 'restarts'])

K.lesson('compare', 'Comparing local search methods', f'''
{src('slide Set 2, slide 87, food for thought VI.')}
{versus('Hill climbing, simulated annealing and genetic algorithms (chapter 4.2)', ['', 'Hill climbing', 'Simulated annealing', 'Genetic algorithm'], [
    ['Breadth of the search', 'One state, narrow', 'One state, wanders widely while hot', 'A population, broad'],
    ['Tests worse solutions', 'Never', 'Yes, with probability e<sup>ΔE⁄T</sup>', 'Yes, weak individuals may still breed'],
    ['Avoids local optima', 'No (only with restarts)', 'Yes, if cooled slowly', 'Often, through crossover and mutation'],
    ['Memory', 'One state', 'One state', 'k states'],
    ['Speed', 'Fastest per run', 'Medium, depends on the schedule', 'Slowest per generation'],
    ['Prefer it when', 'The landscape is smooth or you can restart cheaply', 'There are many local optima and one good answer is enough', 'Good solutions are made of good parts that can be combined']],
    'start with hill climbing and random restarts. Move to annealing when restarts keep landing on poor peaks, and to a genetic algorithm when solutions have reusable building blocks.')}
{scene('chip layout and timetabling', '<p>Placing millions of logic cells on a chip so that wires are short is a huge optimisation problem. Simulated annealing was one of the first methods to do it well (Kirkpatrick and others, 1983), and annealing style placers are still used. University timetabling uses local search too: start with any timetable, then repeatedly move one lecture to a different room or time if it reduces clashes.</p>')}
''', kw=['comparison', 'food for thought VI', 'chip placement', 'timetabling'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Hill climbing is like walking up a hill in fog: you only feel the ground at your feet, so you always step uphill. You may end on a small hill. Annealing is like shaking a tray of marbles: shake hard at first, then gently, so the marbles settle into the deepest holes.</p>',
    '<p>Local search keeps one state and an objective. Hill climbing stops at local maxima, ridges and plateaux. Fixes: sideways moves, random restarts (1 ⁄ p runs), beam search. Annealing accepts worse moves with e<sup>ΔE⁄T</sup> and cools T by a schedule.</p>',
    '<p>With logarithmic cooling T<sub>k</sub> = C ⁄ ln(k + 2), annealing converges to a global optimum with probability 1, because it is a Markov chain whose stationary distribution concentrates on the optima as T → 0. The price is an impractically slow schedule, so real systems use geometric cooling and restarts.</p>',
    '<p>Research looks at parallel tempering (many temperatures that swap states), tabu search (forbid recent moves), large neighbourhood search that solves a sub problem exactly at each step, and quantum annealing hardware that uses tunnelling to cross energy barriers.</p>')}
''', kw=['fog', 'marbles', 'Markov chain', 'parallel tempering', 'tabu search', 'quantum annealing'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Local search</b> keeps one state, moves to better neighbours, and stores no path. It uses constant memory and works on huge spaces.',
    '<b>Hill climbing</b> takes the best neighbour until none is better. It stops at local maxima, ridges and plateaux. On 8 queens it solves about 14 percent of boards in about 4 steps.',
    '<b>Sideways moves</b> raise that to about 94 percent. <b>Random restarts</b> need about 1 ⁄ p runs. <b>Local beam search</b> keeps the best k states.',
    '<b>Simulated annealing</b> accepts a worse move with probability e<sup>ΔE⁄T</sup>. High T explores, low T exploits.',
    'Cooling schedules: geometric α T, linear T0 − kΔT, logarithmic C ⁄ ln(k + 2), constant, exponential T0 α<sup>k</sup>.'],
    'chapter 4.2 searches with a whole population: genetic algorithms.')}
{nbcard('hill-climbing', 'Count attacking queens, run hill climbing and simulated annealing on a small landscape, then write the 8 queens hill climber yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Local search stores', ['The whole search tree', 'Only the current state (or a few)', 'Every explored state', 'The path from the start'], 1,
       'No paths.', 'It keeps the current state, so memory is constant.')
K.quiz('e', 'Hill climbing stops when', ['T reaches 0', 'No neighbour is better than the current state', 'It has made 100 moves', 'It finds the global maximum'], 1,
       'Nothing uphill.', 'It returns the current peak, which may only be local.')
K.quiz('e', 'A flat area from which you can still go up later is called', ['A ridge', 'A shoulder', 'A local maximum', 'A valley'], 1,
       'A flat step.', 'A shoulder is a plateau with an uphill exit further on.')
K.quiz('e', 'In simulated annealing, a high temperature means', ['Almost only uphill moves', 'Many worse moves are accepted', 'The search stops', 'The step size is 0'], 1,
       'Exploration.', 'e<sup>ΔE⁄T</sup> is close to 1 when T is large.')
K.quiz('m', 'How many neighbours does an 8 queens state have when one queen moves within its column?', ['8', '28', '56', '64'], 2,
       '8 columns × 7 other rows.', '8 × 7 = 56.')
K.quiz('m', 'Which variant shares information between several searches?', ['Random restart', 'Local beam search', 'First choice hill climbing', 'Sideways moves'], 1,
       'The best k overall.', 'Successors of all k states compete for the k places.')
K.quiz('m', 'The cooling schedule T<sub>k</sub> = C ⁄ ln(k + 2) is called', ['Geometric', 'Linear', 'Logarithmic', 'Exponential'], 2,
       'ln.', 'Logarithmic cooling, slow but with a convergence guarantee.')
K.quiz('m', 'Constant temperature annealing is also known as', ['Hill climbing', 'The Metropolis algorithm', 'Beam search', 'Gradient descent'], 1,
       'No cooling.', 'At a fixed T it samples states by the Metropolis rule.')
K.quiz('h', 'What is the chance of accepting a move with ΔE = −2 at T = 1?', ['0.135', '0.5', '0.819', '0.018'], 0,
       'e<sup>−2</sup>.', 'e<sup>−2</sup> ≈ 0.135.')
K.quiz('h', 'Random restart hill climbing with success probability p per run needs on average', ['p runs', '1 ⁄ p runs', 'p² runs', 'log p runs'], 1,
       'Geometric distribution.', 'The expected number of trials to the first success is 1 ⁄ p.')
K.quiz('x', 'In the style of an MIT 6.034 exam: why can a ridge stop hill climbing even though a higher point exists nearby?', ['Ridges are always flat', 'Every single move from the ridge goes down, though moving along it diagonally would go up', 'The objective is undefined there', 'Hill climbing has no neighbours'], 1,
       'Think of the allowed moves.', 'If the ridge runs between the allowed move directions, each single move steps off it, so all neighbours look worse.')
K.quiz('x', 'In the style of a Stanford CS221 exam: with T → 0 from the start, simulated annealing becomes', ['A random walk', 'A form of (first choice style) hill climbing that accepts only improvements', 'Breadth first search', 'A genetic algorithm'], 1,
       'P(worse) = 0.', 'It picks random neighbours and moves only when they are better.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'How many states does 8 queens (one per column) have? 8⁸.', '16777216', '8 rows for each of 8 columns.',
       ['8² = 64. 8⁴ = 4,096.', '8⁸ = 4,096².', eq('16,777,216')], check=8 ** 8)
K.calc('e', 'How many pairs of queens are there among 8?', '28', '8 choose 2.',
       ['8 × 7 = 56.', 'Each pair counted twice.', eq('56 ⁄ 2 = 28')], check=28)
K.calc('e', 'Acceptance probability e<sup>ΔE⁄T</sup> for ΔE = −2 at T = 10 (3 decimals).', '0.819', 'e<sup>−0.2</sup>.',
       ['ΔE ⁄ T = −0.2.', 'e<sup>−0.2</sup>.', eq('≈ 0.819')], check=0.8187, tol=0.001)
K.calc('m', 'Geometric cooling T0 = 100, α = 0.9. Temperature after 10 steps (1 decimal)?', '34.9', '100 × 0.9¹⁰.',
       ['0.9¹⁰ = 0.3487.', '× 100.', eq('≈ 34.9')], check=100 * 0.9 ** 10, tol=0.05)
K.calc('m', 'Linear cooling T0 = 50, ΔT = 2. Temperature after 15 steps?', '20', 'T0 − kΔT.',
       ['15 × 2 = 30.', '50 − 30.', eq('20')], check=20)
K.calc('m', 'Logarithmic cooling with C = 10. T at k = 0 (2 decimals)?', '14.43', 'C ⁄ ln 2.',
       ['ln(0 + 2) = ln 2 = 0.6931.', '10 ⁄ 0.6931.', eq('≈ 14.43')], check=10 / 0.693147, tol=0.01)
K.calc('m', 'Random restart with p = 0.148 per run. Expected number of runs (1 decimal)?', '6.8', '1 ⁄ p.',
       ['1 ⁄ 0.148.', '= 6.76.', eq('≈ 6.8 runs')], check=1 / 0.148, tol=0.05)
K.calc('h', 'Chance that at least one of 10 restarts succeeds, p = 0.148 (2 decimals).', '0.80', '1 − (1 − p)¹⁰.',
       ['1 − p = 0.852.', '0.852¹⁰ ≈ 0.201.', eq('1 − 0.201 ≈ 0.80')], check=1 - 0.852 ** 10, tol=0.01)
K.calc('h', 'Geometric cooling from T0 = 100 with α = 0.9: how many steps until T first drops below 1?', '44', 'k &gt; ln 0.01 ⁄ ln 0.9.',
       ['ln 0.01 = −4.605. ln 0.9 = −0.1054.', '4.605 ⁄ 0.1054 = 43.7.', eq('the first whole k above 43.7 is 44')], check=44)
K.calc('x', 'In the style of a CMU 10-701 problem: a worse move with ΔE = −3 should be accepted with probability 0.5. What temperature T is needed? (2 decimals)', '4.33', 'Solve e<sup>−3⁄T</sup> = 0.5.',
       ['−3 ⁄ T = ln 0.5 = −0.6931.', 'T = 3 ⁄ 0.6931.', eq('T ≈ 4.33')], check=3 / 0.693147, tol=0.01)

# ---------------------------------------------------------------- assignments
K.assign('pairs', 'e', 'Count attacking queens',
         '<p>Write <code>attacking_pairs(board)</code> where board[c] is the row of the queen in column c. Return the number of pairs of queens in the same row or on the same diagonal.</p>',
         '''
def attacking_pairs(board):
    # your code here
    pass
''', [("attacking_pairs([4, 5, 6, 3, 4, 5, 6, 5])", 17), ("attacking_pairs([0, 4, 7, 5, 2, 6, 1, 3])", 0), ("attacking_pairs([0, 0, 0, 0])", 6), ("attacking_pairs([0, 1, 2, 3])", 6)],
         '''
def attacking_pairs(board):
    count = 0
    for c1 in range(len(board)):
        for c2 in range(c1 + 1, len(board)):
            if board[c1] == board[c2] or abs(board[c1] - board[c2]) == c2 - c1:
                count = count + 1
    return count
''', 'Two queens attack on a diagonal when the row difference equals the column difference.', '<p>The textbook start state has h = 17.</p>')
K.assign('hc', 'm', 'Steepest descent on 8 queens',
         '<p>Write <code>hill_climb(board)</code> that repeats: try every move of one queen to another row in its column, and take the move with the fewest attacking pairs (the first such move in column then row order) if it is strictly better than now. Stop when no move is better. Return [final board, final number of attacking pairs]. A helper attacking_pairs is given.</p>',
         '''
def attacking_pairs(board):
    count = 0
    for c1 in range(len(board)):
        for c2 in range(c1 + 1, len(board)):
            if board[c1] == board[c2] or abs(board[c1] - board[c2]) == c2 - c1:
                count = count + 1
    return count

def hill_climb(board):
    # your code here
    pass
''', [("hill_climb([0, 4, 7, 5, 2, 6, 1, 3])", [[0, 4, 7, 5, 2, 6, 1, 3], 0]),
      ("hill_climb([1, 3, 0, 2])[1]", 0),
      ("hill_climb([0, 0, 0, 0])[1] < 6", True),
      ("hill_climb([4, 5, 6, 3, 4, 5, 6, 5])[1] < 17", True)],
         '''
def attacking_pairs(board):
    count = 0
    for c1 in range(len(board)):
        for c2 in range(c1 + 1, len(board)):
            if board[c1] == board[c2] or abs(board[c1] - board[c2]) == c2 - c1:
                count = count + 1
    return count

def hill_climb(board):
    board = board[:]
    current = attacking_pairs(board)
    while True:
        best_board = None
        best_value = current
        for col in range(len(board)):
            for row in range(len(board)):
                if row != board[col]:
                    trial = board[:]
                    trial[col] = row
                    value = attacking_pairs(trial)
                    if value < best_value:
                        best_value = value
                        best_board = trial
        if best_board is None:
            return [board, current]
        board = best_board
        current = best_value
''', 'Copy the board for each trial move. Keep the best trial only if it is strictly better.', '<p>It always ends at a local minimum, which is a solution only sometimes.</p>')

K.must('Local search', 'One current state, an objective, neighbours. No path, constant memory, works on huge spaces.')
K.must('Hill climbing', 'Best neighbour until none is better. Stuck at local maxima, ridges and plateaux. 8 queens: about 14 percent solved.')
K.must('Fixes', 'Sideways moves (about 94 percent), random restarts (1 ⁄ p runs), stochastic and first choice, local beam search.')
K.must('Simulated annealing', 'Accept worse with e<sup>ΔE⁄T</sup>. High T explores, low T exploits.')
K.must('Cooling schedules', 'Geometric T ← αT (0.8 ≤ α ≤ 1), linear T0 − kΔT, logarithmic C ⁄ ln(k + 2), constant, exponential T0 α<sup>k</sup>.')

T = K.topic(
    slug='hill-climbing', topic='hill-climbing', step=(4, 'Local and evolutionary search', 'cai-local', 'Improve one state or a population step by step when the space is too big to explore: hill climbing, annealing and genetic algorithms.', 'College'),
    title='Local search: hill climbing and simulated annealing', short='Hill climbing and annealing', badge='4.1', minutes=50,
    lead='When the space is too big to search and only the final state matters, keep one state and improve it. Hill climbing is fast but gets stuck. Restarts, beam search and simulated annealing help it escape.',
    desc='Local search and the state space landscape, local maxima, ridges and plateaux, steepest ascent hill climbing on 8 queens, sideways moves, random restarts and beam search, simulated annealing with acceptance probability and five cooling schedules, gradient methods and a comparison with genetic algorithms.',
    summary='Hill climbing and its traps, sideways moves, restarts, beam search, and simulated annealing with cooling schedules.',
    keywords=['local search', 'hill climbing', 'simulated annealing', 'cooling schedule', '8 queens', 'local beam search', 'random restart'],
    recap='<p>Climb to better neighbours, and use sideways moves, restarts or annealing to escape local peaks.</p>',
    nb={'queens': 'The 8 queens objective: attacking pairs', 'anneal': 'Hill climbing against simulated annealing on a small landscape'})
