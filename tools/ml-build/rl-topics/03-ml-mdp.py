# Reinforcement 1.3: Markov decision processes and the Bellman equations. Checked against Sutton and Barto,
# Reinforcement Learning: An Introduction (2nd edition, 2018) chapter 3 and example 4.1 (the 4 x 4 gridworld),
# Bellman, Dynamic Programming (1957), Puterman, Markov Decision Processes (1994), Silver, UCL Course on RL lecture 2,
# and Norris, Markov Chains (1997) for stationary distributions.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-mdp')
K = Kit()

K.code('markov_chain', r'''
import numpy as np

states = ["sunny", "cloudy", "rainy"]
P = np.array([[0.7, 0.2, 0.1],                           # row = today, column = tomorrow
              [0.3, 0.4, 0.3],
              [0.2, 0.4, 0.4]])
print("each row sums to 1:", P.sum(axis=1))

rng = np.random.default_rng(0)
s, visits = 0, np.zeros(3)
for day in range(10000):                                 # walk the chain for 10,000 days
    visits[s] += 1
    s = rng.choice(3, p=P[s])                            # tomorrow depends only on today
print("share of days in each state:", (visits / visits.sum()).round(3))

dist = np.array([1.0, 0.0, 0.0])                          # start: certainly sunny
for _ in range(50):
    dist = dist @ P                                      # distribution after one more day
print("distribution after 50 days:", dist.round(3))
w, v = np.linalg.eig(P.T)
pi = np.real(v[:, np.argmin(abs(w - 1))])
print("stationary distribution (left eigenvector for eigenvalue 1):", (pi / pi.sum()).round(3))
print("two days ahead from rainy:", (np.array([0, 0, 1.0]) @ P @ P).round(3))
''', long=True)

K.code('mrp_value', r'''
import numpy as np

states = ["Wake", "Gym", "Work", "Couch", "End"]
P = np.array([[0.0, 0.5, 0.0, 0.5, 0.0],                 # Wake: gym or couch
              [0.0, 0.0, 0.8, 0.2, 0.0],                 # Gym: work or couch
              [0.0, 0.0, 0.0, 0.4, 0.6],                 # Work: couch or done for the day
              [0.4, 0.0, 0.0, 0.6, 0.0],                 # Couch: stay or wake up again
              [0.0, 0.0, 0.0, 0.0, 1.0]])                # End: stays there, no more reward
R = np.array([-1.0, -2.0, 10.0, -1.0, 0.0])              # reward for leaving each state
gamma = 0.9

V_exact = np.linalg.solve(np.eye(5) - gamma * P, R)      # Bellman equation V = R + gamma P V, solved at once
print("exact values:      ", {name: round(float(v), 3) for name, v in zip(states, V_exact)})

V = np.zeros(5)
for sweep in range(1, 101):
    V = R + gamma * P @ V                                # apply the Bellman equation as an update
    if sweep in (1, 2, 5, 20, 100):
        print("after", str(sweep).rjust(3), "sweeps:", V.round(3))
''')

K.code('gridworld_values', r'''
import numpy as np

# 4 x 4 grid, cells 0 to 15. Cells 0 and 15 are exits. Every move costs -1. Moves off the grid leave you in place.
n, gamma = 16, 1.0
moves = {"up": -4, "down": 4, "left": -1, "right": 1}

def step(s, a):
    if s in (0, 15):
        return s, 0.0
    r, c = divmod(s, 4)
    if (a == "up" and r == 0) or (a == "down" and r == 3) or (a == "left" and c == 0) or (a == "right" and c == 3):
        return s, -1.0
    return s + moves[a], -1.0

P, R = np.zeros((n, n)), np.zeros(n)                       # the random policy: each move with chance 1/4
for s in range(n):
    for a in moves:
        s2, r = step(s, a)
        P[s, s2] += 0.25
        R[s] += 0.25 * r
P[[0, 15]] = 0                                           # exits: no future
V = np.linalg.solve(np.eye(n) - gamma * P, R)
print("value of each cell under the random policy:")
print(V.reshape(4, 4).round(1))
''', long=True)

K.code('q_and_greedy', r'''
import numpy as np

n, gamma = 16, 1.0
moves = {"up": -4, "down": 4, "left": -1, "right": 1}

def step(s, a):
    if s in (0, 15):
        return s, 0.0
    r, c = divmod(s, 4)
    if (a == "up" and r == 0) or (a == "down" and r == 3) or (a == "left" and c == 0) or (a == "right" and c == 3):
        return s, -1.0
    return s + moves[a], -1.0

P, R = np.zeros((n, n)), np.zeros(n)
for s in range(n):
    for a in moves:
        s2, r = step(s, a)
        P[s, s2] += 0.25
        R[s] += 0.25 * r
P[[0, 15]] = 0
V = np.linalg.solve(np.eye(n) - gamma * P, R)            # value of the random policy

s = 6                                                    # row 1, column 2
for a in moves:
    s2, r = step(s, a)
    print(f"Q(cell 6, {a.ljust(5)}) = r + gamma * V(next) = {r:.0f} + ({V[s2]:.1f}) = {r + gamma * V[s2]:.1f}")
arrows = {"up": "^", "down": "v", "left": "<", "right": ">"}
grid = []
for s in range(n):
    if s in (0, 15):
        grid.append("X")
        continue
    q = {a: step(s, a)[1] + gamma * V[step(s, a)[0]] for a in moves}
    grid.append(arrows[max(q, key=q.get)])               # greedy with respect to the random policy's values
print("greedy policy from those values:")
for r in range(4):
    print(" ".join(grid[4 * r:4 * r + 4]))
''', long=True)

K.lesson('idea', 'The Markov property and Markov chains', f'''
{src('Sutton and Barto (2018) section 3.1, and Norris, Markov Chains (1997) chapter 1.')}
{viz('mlmarkov')}
{wwh('A process has the <b>Markov property</b> when the future depends only on the present state, not on how it got there. A <b>Markov chain</b> is a set of states plus a <b>transition matrix</b> P, where P[i][j] is the chance of moving from state i to state j in one step. Each row adds up to 1.',
     'If the state holds everything that matters, the agent can decide using the state alone and forget the past. That makes planning possible. Markov chains also power PageRank, text generation by n grams, queueing models and MCMC sampling.',
     'Write the states, fill the transition matrix, and push a probability distribution forward with d<sub>next</sub> = d P. After many steps most chains settle into a <b>stationary distribution</b> &pi; with &pi; = &pi;P, whatever the start.')}
{run('markov_chain')}
{note('Walking the chain for 10,000 days gives shares 0.468, 0.304 and 0.228. Pushing the starting distribution through P 50 times gives 0.462, 0.308 and 0.231, the same as the left eigenvector of P for eigenvalue 1. Two days ahead from rainy, sunny has chance 0.2 &times; 0.7 + 0.4 &times; 0.3 + 0.4 &times; 0.2 = 0.34.', 'exam')}
{fxs(fx('Markov property', 'P(S<sub>t+1</sub> | S<sub>t</sub>, S<sub>t&minus;1</sub>, ..., S<sub>0</sub>) = P(S<sub>t+1</sub> | S<sub>t</sub>)', 'The present holds all that matters.', key=True),
     fx('k steps ahead', 'd<sub>t+k</sub> = d<sub>t</sub> P<sup>k</sup>', 'Row vector times matrix powers.', key=True),
     fx('Stationary distribution', '&pi; = &pi; P, &Sigma; &pi;<sub>i</sub> = 1', 'Left eigenvector for eigenvalue 1.', key=True))}
''', kw=['Markov property', 'Markov chain', 'transition matrix', 'stationary distribution', 'eigenvector', 'PageRank'])

K.lesson('mdp', 'Markov reward processes and decision processes', f'''
{src('Sutton and Barto (2018) sections 3.1 to 3.5, and Silver, UCL Course on RL lecture 2.')}
{viz('mlbackup')}
{wwh('A <b>Markov reward process</b> (MRP) adds a reward R(s) to each state of a Markov chain and a discount &gamma;. The <b>value</b> V(s) is the expected discounted return starting from s. A <b>Markov decision process</b> (MDP) adds actions: the tuple (S, A, P, R, &gamma;), where P(s&prime; | s, a) depends on the action chosen. An MDP plus a fixed policy &pi; is again an MRP.',
     'The MDP is the standard language of RL. Every algorithm in this section, from dynamic programming to deep Q networks, solves an MDP or an estimate of one. Writing a problem as an MDP shows what the state must contain and what the agent controls.',
     'Values satisfy the <b>Bellman equation</b> V(s) = R(s) + &gamma; &Sigma;<sub>s&prime;</sub> P(s&prime; | s) V(s&prime;). In matrix form V = R + &gamma;PV, so V = (I &minus; &gamma;P)<sup>&minus;1</sup> R. For small problems solve this directly. For large ones, repeat the equation as an update until the values stop changing.')}
{run('mrp_value')}
{note('Solving the linear system gives Work 9.179, Gym 4.198, Wake &minus;0.138 and Couch &minus;2.282. Repeating V &larr; R + &gamma;PV from all zeros reaches the same numbers: within 0.01 after 20 sweeps and exactly after 100. Check Work by hand: 10 + 0.9 &times; (0.4 &times; (&minus;2.282) + 0.6 &times; 0) = 9.179.', 'exam')}
{table(['Model', 'Has', 'Answers'], [
    ['Markov chain', 'States, transitions', 'Where will I be?'],
    ['Markov reward process', '+ rewards, &gamma;', 'How good is each state?'],
    ['Markov decision process', '+ actions', 'What should I do in each state?'],
    ['Partially observable MDP', '+ observations that hide the state', 'What should I do when I cannot see the state?']])}
''', kw=['Markov reward process', 'Markov decision process', 'MDP tuple', 'value function', 'Bellman equation', 'linear system', 'POMDP'])

K.lesson('values', 'State values and action values for a policy', f'''
{src('Sutton and Barto (2018) section 3.5 and example 4.1, the 4 &times; 4 gridworld.')}
{wwh('For a policy &pi;, the <b>state value</b> v<sub>&pi;</sub>(s) is the expected return from s when following &pi;. The <b>action value</b> q<sub>&pi;</sub>(s, a) is the expected return from s if you first take action a and then follow &pi;. They are linked: v is the &pi; weighted average of q, and q is the reward plus the discounted value of the next state.',
     'Values turn a long future into one number per state, so the agent can compare choices locally. The action value is especially useful: picking the action with the largest q needs no model of the environment, which is the key to Q learning.',
     'Build the MRP that the policy creates, then solve its Bellman equation. Here the policy moves in all four directions with chance 1/4 on a 4 &times; 4 grid with exits in two corners and a cost of &minus;1 per move.')}
{run('gridworld_values')}
{note('These are the values from Sutton and Barto’s example 4.1. Next to an exit the random walker still needs 14 moves on average (value &minus;14), and in the far corners 22. Values are expected costs to finish, so they tell you how hopeless the random policy is, not how short the best path is.', 'exam')}
{run('q_and_greedy')}
{note('In cell 6 the four action values are &minus;21, &minus;19, &minus;19 and &minus;21, and their average is &minus;20, exactly v<sub>&pi;</sub>(6). Picking the best action in every cell gives arrows that already lead straight to the exits. Acting greedily on the values of even a poor policy gives a better policy. This is policy improvement, the next chapter’s main idea.', 'tip')}
{fxs(fx('State value', 'v<sub>&pi;</sub>(s) = E<sub>&pi;</sub>[G<sub>t</sub> | S<sub>t</sub> = s]', 'How good it is to be in s.', key=True),
     fx('Action value', 'q<sub>&pi;</sub>(s, a) = E<sub>&pi;</sub>[G<sub>t</sub> | S<sub>t</sub> = s, A<sub>t</sub> = a]', 'How good it is to take a in s.', key=True),
     fx('Links', 'v<sub>&pi;</sub>(s) = &Sigma;<sub>a</sub> &pi;(a|s) q<sub>&pi;</sub>(s, a), q<sub>&pi;</sub>(s, a) = &Sigma;<sub>s&prime;,r</sub> p(s&prime;, r | s, a)[r + &gamma; v<sub>&pi;</sub>(s&prime;)]', 'Average over actions, then over outcomes.', key=True))}
''', kw=['state value function', 'action value function', 'Q function', 'gridworld', 'policy evaluation', 'greedy policy'])

K.lesson('optimal', 'Optimal values and the Bellman optimality equation', f'''
{src('Bellman, Dynamic Programming (1957), and Sutton and Barto (2018) section 3.6.')}
{wwh('The <b>optimal value</b> v*(s) is the largest value any policy can reach from s, and q*(s, a) the largest action value. They satisfy the <b>Bellman optimality equation</b>: v*(s) = max<sub>a</sub> &Sigma; p(s&prime;, r | s, a)[r + &gamma; v*(s&prime;)]. Any policy that is greedy with respect to q* is optimal.',
     'Every finite MDP has at least one deterministic optimal policy, and all optimal policies share the same v* and q*. So the whole problem of acting well reduces to finding q*, and then acting is just taking the argmax.',
     'The max makes the optimality equation nonlinear, so there is no single matrix solve. It is solved by repeating it as an update (value iteration), by alternating evaluation and greedy improvement (policy iteration), or from samples without a model (Q learning). The next chapters do each one.')}
{steps('Optimal values in the 4 &times; 4 gridworld, by reasoning', [
    'Every move costs &minus;1 and moves are certain, so the best policy walks the shortest path to the nearer exit.',
    'v*(s) = &minus;(number of moves to the nearer exit).',
    'Cell 6 (row 1, column 2) is 3 moves from both corners, so v*(6) = &minus;3, against &minus;20 for the random policy.',
    'q*(6, up) = &minus;1 + v*(2) = &minus;1 + (&minus;2) = &minus;3, and q*(6, right) = &minus;1 + v*(7) = &minus;3 as well. Several actions can be optimal.'])}
{table(['Equation', 'Relates', 'Linear?', 'Solved by'], [
    ['Bellman expectation for v<sub>&pi;</sub>', 'A state and its successors under &pi;', 'Yes', 'Matrix solve or iterative evaluation'],
    ['Bellman optimality for v*', 'A state and its successors under the best action', 'No (max)', 'Value iteration, policy iteration'],
    ['Bellman optimality for q*', 'An action and the best next actions', 'No (max)', 'Q learning, DQN']])}
{deep('Why the Bellman update always converges', '<p>Write the update as an operator T on value functions: (TV)(s) = max<sub>a</sub> &Sigma; p(s&prime;, r | s, a)[r + &gamma;V(s&prime;)]. For any two value functions U and V, the largest difference between TU and TV is at most &gamma; times the largest difference between U and V. So T is a <b>contraction</b> in the max norm when &gamma; &lt; 1, and by the Banach fixed point theorem it has exactly one fixed point, v*, which repeated updates reach from any start, with the error shrinking by a factor &gamma; each sweep. The same argument works for the expectation operator of a fixed policy. With &gamma; = 1 convergence needs every policy to reach a terminal state eventually, as in the gridworld.</p>')}
''', kw=['optimal value function', 'Bellman optimality equation', 'optimal policy', 'greedy policy', 'contraction mapping', 'Banach fixed point'])

K.lesson('versus', 'Markov models compared', f'''
{versus('From chains to decisions', ['', 'Markov chain', 'Markov reward process', 'Markov decision process', 'Bandit'], [
    ['States', 'Many', 'Many', 'Many', 'One'],
    ['Actions', 'None', 'None', 'Yes', 'Yes'],
    ['Rewards', 'None', 'Per state', 'Per state and action', 'Per action'],
    ['Question', 'Long run behaviour', 'Value of each state', 'Best policy', 'Best arm'],
    ['Main equation', '&pi; = &pi;P', 'V = R + &gamma;PV', 'v* = max over actions of the Bellman backup', 'Q &larr; Q + (r &minus; Q)/N']],
    'write a decision problem as an MDP, check that the state is Markov, and use the matching Bellman equation.')}
''', kw=['Markov chain vs MDP', 'MRP vs MDP', 'bandit vs MDP'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('MDP', '(S, A, p, R, &gamma;), p(s&prime;, r | s, a) = P(S<sub>t+1</sub> = s&prime;, R<sub>t+1</sub> = r | S<sub>t</sub> = s, A<sub>t</sub> = a)', 'The four argument dynamics function.', key=True),
     fx('MRP solution', 'V = (I &minus; &gamma;P)<sup>&minus;1</sup> R', 'Cost O(n<sup>3</sup>), fine for small n.', key=True),
     fx('Bellman expectation', 'v<sub>&pi;</sub>(s) = &Sigma;<sub>a</sub> &pi;(a|s) &Sigma;<sub>s&prime;,r</sub> p(s&prime;, r | s, a)[r + &gamma; v<sub>&pi;</sub>(s&prime;)]', 'Linear in v<sub>&pi;</sub>.', key=True),
     fx('Bellman optimality', 'v*(s) = max<sub>a</sub> &Sigma;<sub>s&prime;,r</sub> p(s&prime;, r | s, a)[r + &gamma; v*(s&prime;)]', 'Nonlinear because of the max.', key=True),
     fx('Optimal action value', 'q*(s, a) = &Sigma;<sub>s&prime;,r</sub> p(s&prime;, r | s, a)[r + &gamma; max<sub>a&prime;</sub> q*(s&prime;, a&prime;)]', 'Acting: &pi;*(s) = argmax<sub>a</sub> q*(s, a).'),
     fx('Contraction', '&#8214;TU &minus; TV&#8214;<sub>&infin;</sub> &le; &gamma; &#8214;U &minus; V&#8214;<sub>&infin;</sub>', 'Hence a unique fixed point.'),
     fx('Number of policies', '|A|<sup>|S|</sup> deterministic policies', 'Far too many to try one by one.'))}
{steps('Worked example: one Bellman expectation backup', [
    'State s has two actions, each chosen with chance 0.5. &gamma; = 0.9.',
    'Action a gives reward 1 and leads to a state with value 10. Action b gives reward 0 and leads to a state with value 4.',
    eq('q(s, a) = 1 + 0.9 &times; 10 = 10, q(s, b) = 0 + 0.9 &times; 4 = 3.6'),
    eq('v(s) = 0.5 &times; 10 + 0.5 &times; 3.6 = 6.8'),
    'The optimality backup would instead take the max: v*(s) = 10 if those next values were optimal.'])}
{deep('Partially observable MDPs', '<p>When the agent sees only an observation o that hides part of the state (a robot with noisy sensors, a card game with hidden hands), the process is a POMDP. The fix in theory is a <b>belief state</b>: the probability distribution over true states given all observations so far, updated with Bayes’ rule. The belief is Markov, so a POMDP is an MDP over beliefs, but that MDP has continuous states and is very hard to solve exactly. Practical agents approximate it by stacking recent observations (as DQN stacks 4 Atari frames) or by giving the policy a memory such as a recurrent network.</p>')}
''', kw=['MDP definition', 'Bellman expectation equation', 'Bellman optimality equation', 'q star', 'contraction', 'POMDP', 'belief state'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>An MDP describes a world where what happens next depends only on where you are now and what you do, and values say how good each place is.</p>',
    '<p>Build transition matrices, find stationary distributions, solve V = R + &gamma;PV for a small MRP, and compute v<sub>&pi;</sub> and q<sub>&pi;</sub> for a policy.</p>',
    '<p>Write the Bellman expectation and optimality equations for v and q, derive optimal values in simple MDPs, and explain greedy policy improvement.</p>',
    '<p>Prove the contraction property, study the linear programming formulation of MDPs, average reward and constrained MDPs, and POMDPs with belief states.</p>')}
{grow('Explain the Markov property and what a value means.',
      'Model problems as MDPs and compute values.',
      'Analyse the Bellman equations and their solutions.')}
''', kw=['beginner', 'expert', 'linear programming MDP', 'constrained MDP'])

lc(509, 'Fibonacci Number', 'fibonacci-number', 'e', 'Each value comes from the two before it', 'Keep only the last two numbers and step forward. A value defined by earlier values is the simplest recursion, the same shape as a Bellman equation.', r"""
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
""", [('fib(2)', 1), ('fib(4)', 3), ('fib(10)', 55)])
lc(746, 'Min Cost Climbing Stairs', 'min-cost-climbing-stairs', 'e', 'Best cost to reach step i = min of the two ways in', 'The cheapest cost to stand on step i is the cheaper of coming from i &minus; 1 or i &minus; 2, plus that step’s cost. Choosing the best of several moves and adding a cost is a Bellman optimality backup with costs instead of rewards.', r"""
def min_cost_climbing_stairs(cost):
    a = b = 0
    for i in range(2, len(cost) + 1):
        a, b = b, min(b + cost[i - 1], a + cost[i - 2])
    return b
""", [('min_cost_climbing_stairs([10, 15, 20])', 15), ('min_cost_climbing_stairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1])', 6)])
lc(64, 'Minimum Path Sum', 'minimum-path-sum', 'm', 'Work backwards from the goal', 'The best total from a cell is its own cost plus the better of the best totals to the right and below. Filling the table from the goal backwards is exactly how optimal values are found in a deterministic gridworld.', r"""
def min_path_sum(grid):
    m, n = len(grid), len(grid[0])
    best = [[0] * n for _ in range(m)]
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            if i == m - 1 and j == n - 1:
                best[i][j] = grid[i][j]
            elif i == m - 1:
                best[i][j] = grid[i][j] + best[i][j + 1]
            elif j == n - 1:
                best[i][j] = grid[i][j] + best[i + 1][j]
            else:
                best[i][j] = grid[i][j] + min(best[i + 1][j], best[i][j + 1])
    return best[0][0]
""", [('min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]])', 7), ('min_path_sum([[1, 2, 3], [4, 5, 6]])', 12)])
lc(120, 'Triangle', 'triangle', 'm', 'Collapse the triangle from the bottom row up', 'Start with the bottom row as the best totals. Each number above adds the smaller of its two children. One pass from the bottom gives the answer at the top, in the style of a backward Bellman sweep.', r"""
def minimum_total(triangle):
    below = triangle[-1][:]
    for row in reversed(triangle[:-1]):
        below = [v + min(below[i], below[i + 1]) for i, v in enumerate(row)]
    return below[0]
""", [('minimum_total([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]])', 11), ('minimum_total([[-10]])', -10)])
lc(935, 'Knight Dialer', 'knight-dialer', 'm', 'Count numbers by pushing counts through the knight’s moves', 'Keep how many numbers end on each digit. Each step, every digit passes its count to the digits a knight can jump to. This is a Markov chain transition applied n &minus; 1 times, with counts instead of probabilities.', r"""
def knight_dialer(n):
    MOD = 10 ** 9 + 7
    jumps = {0: [4, 6], 1: [6, 8], 2: [7, 9], 3: [4, 8], 4: [0, 3, 9], 5: [], 6: [0, 1, 7], 7: [2, 6], 8: [1, 3], 9: [2, 4]}
    count = [1] * 10
    for _ in range(n - 1):
        nxt = [0] * 10
        for d in range(10):
            for e in jumps[d]:
                nxt[e] = (nxt[e] + count[d]) % MOD
        count = nxt
    return sum(count) % MOD
""", [('knight_dialer(1)', 10), ('knight_dialer(2)', 20), ('knight_dialer(3131)', 136006598)])
lc(174, 'Dungeon Game', 'dungeon-game', 'h', 'Go backwards from the princess: health needed on entering each room', 'Forward search fails because the best path depends on what comes later. Instead compute, from the goal backwards, the least health needed when entering each room: one less than the smaller need of the next rooms minus this room’s value, but at least 1. Backward induction like this is how finite horizon MDPs are solved.', r"""
def calculate_minimum_hp(dungeon):
    m, n = len(dungeon), len(dungeon[0])
    INF = float("inf")
    need = [[INF] * (n + 1) for _ in range(m + 1)]
    need[m][n - 1] = need[m - 1][n] = 1
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            need[i][j] = max(1, min(need[i + 1][j], need[i][j + 1]) - dungeon[i][j])
    return need[0][0]
""", [('calculate_minimum_hp([[-2, -3, 3], [-5, -10, 1], [10, 30, -5]])', 7), ('calculate_minimum_hp([[0]])', 1)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Bellman equations define a value from the values that follow it. These problems practise recursions from earlier values, best of several moves plus a cost, backward sweeps from a goal over grids and triangles, pushing counts through a transition table like a Markov chain, and backward induction when the future decides what is needed now. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'dynamic programming', 'backward induction', 'grid DP', 'Markov chain counting'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Markov property</b>: the next state depends only on the current one. A chain is states plus a transition matrix P.',
    'Distributions move as d P<sup>k</sup>. Most chains settle at a <b>stationary distribution</b> &pi; = &pi;P.',
    'An <b>MRP</b> adds rewards: V = R + &gamma;PV, so V = (I &minus; &gamma;P)<sup>&minus;1</sup>R. An <b>MDP</b> adds actions: (S, A, p, R, &gamma;).',
    'v<sub>&pi;</sub>(s) and q<sub>&pi;</sub>(s, a) are expected returns. v is the &pi; average of q, and q is reward plus discounted next v.',
    'The <b>Bellman optimality equation</b> uses a max. A policy greedy with respect to q* is optimal.',
    'The Bellman operator is a &gamma; contraction, so repeated backups converge to a unique answer.'],
    'Reinforcement 2.1 solves MDPs with dynamic programming: policy evaluation, policy iteration and value iteration.')}
{files('Three tasks: a distribution after k steps, MRP values by repeated backups, and a one step lookahead.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'The Markov property says the next state depends on', ['The whole history', 'Only the current state (and action)', 'Nothing', 'The reward only'], 1, 'Memoryless.', 'The present holds all that matters.')
K.quiz('e', 'Each row of a transition matrix', ['Adds up to 0', 'Adds up to 1', 'Is all equal', 'Holds rewards'], 1, 'Probabilities.', 'From one state you must go somewhere.')
K.quiz('e', 'An MDP adds to a Markov reward process', ['States', 'Actions chosen by the agent', 'Rewards', 'A discount'], 1, 'Decisions.', '(S, A, p, R, &gamma;).')
K.quiz('e', 'The value V(s) of a state is', ['Its reward', 'The expected discounted return starting from s', 'The number of actions', 'A probability'], 1, 'Long run.', 'Not just the next reward.')
K.quiz('m', 'The stationary distribution &pi; of a chain satisfies', ['&pi; = P&pi;', '&pi; = &pi;P', '&pi; = 0', '&pi; = P<sup>2</sup>'], 1, 'Row vector.', 'Left eigenvector, eigenvalue 1.')
K.quiz('m', 'For a small MRP the values can be found exactly by', ['Guessing', 'Solving V = (I &minus; &gamma;P)<sup>&minus;1</sup>R', 'Sorting', 'Sampling once'], 1, 'Linear system.', 'Cubic cost in the number of states.')
K.quiz('m', 'q<sub>&pi;</sub>(s, a) differs from v<sub>&pi;</sub>(s) because it', ['Ignores rewards', 'Fixes the first action to a, then follows &pi;', 'Uses no discount', 'Is always larger'], 1, 'First action fixed.', 'v is the &pi; average of q.')
K.quiz('m', 'An MDP with a fixed policy becomes', ['A bandit', 'A Markov reward process', 'A neural network', 'Nothing useful'], 1, 'Actions are averaged out.', 'Then the linear Bellman equation applies.')
K.quiz('m', 'Acting greedily on the values of the random policy in the gridworld gives', ['A random policy', 'A much better policy that heads to the exits', 'The worst policy', 'No policy'], 1, 'Policy improvement.', 'The arrows already point to the exits.')
K.quiz('h', 'Why can the Bellman optimality equation not be solved with one matrix inverse?', ['It has no solution', 'The max over actions makes it nonlinear', 'It needs labels', 'Matrices are too small'], 1, 'Nonlinear.', 'Use value or policy iteration.')
K.quiz('h', 'Every finite MDP has', ['No optimal policy', 'At least one deterministic optimal policy', 'Only random optimal policies', 'Exactly one optimal action per state'], 1, 'Puterman (1994).', 'Ties allow several.')
K.quiz('h', 'Repeated Bellman backups converge for &gamma; &lt; 1 because the operator is', ['Linear', 'A contraction in the max norm', 'Random', 'Convex'], 1, 'Shrinks differences by &gamma;.', 'Banach fixed point theorem.')
K.quiz('x', 'In the style of a Stanford CS234 exam: an MDP has 10 states and 4 actions. How many deterministic stationary policies?', ['40', '10<sup>4</sup>', '4<sup>10</sup>', '14'], 2, 'One action per state.', '4<sup>10</sup> = 1,048,576.')
K.quiz('x', 'In the style of a Stanford CS234 exam: a POMDP becomes an MDP over', ['Observations', 'Belief states (distributions over hidden states)', 'Actions', 'Rewards'], 1, 'Bayes updates.', 'The belief is Markov.')

K.calc('e', 'P(sunny to sunny) = 0.7. Starting sunny, chance of two more sunny days in a row?', '0.49', 'Multiply the steps.', ['First day: 0.7.', 'Second day: 0.7 again.', eq('0.7 &times; 0.7 = 0.49')], check=0.49)
K.calc('e', 'R(s) = 2, &gamma; = 0.5, and s always moves to a state with value 4. V(s)?', '4', 'R + &gamma; V(next).', ['&gamma; &times; 4 = 2.', 'Add R = 2.', eq('2 + 2 = 4')], check=4)
K.calc('m', 'Weather chain: from rainy the chances are 0.2, 0.4, 0.4. Sunny row 0.7, 0.2, 0.1, cloudy row 0.3, 0.4, 0.3, rainy row 0.2, 0.4, 0.4. Chance of sunny two days after rainy?', '0.34', 'Sum over the middle day.', ['Via sunny: 0.2 &times; 0.7 = 0.14.', 'Via cloudy: 0.4 &times; 0.3 = 0.12. Via rainy: 0.4 &times; 0.2 = 0.08.', eq('0.14 + 0.12 + 0.08 = 0.34')], check=0.34)
K.calc('m', 'V(Work) = 10 + 0.9 &times; (0.4 &times; V(Couch) + 0.6 &times; 0) with V(Couch) = &minus;2.282. V(Work)?', '9.179', 'Plug in.', ['0.4 &times; (&minus;2.282) = &minus;0.9128.', '0.9 &times; (&minus;0.9128) = &minus;0.8215.', eq('10 &minus; 0.8215 = 9.179')], check=9.1785, tol=0.002)
K.calc('m', 'Two actions with chance 0.5 each, &gamma; = 0.9. Action a: reward 1, next value 10. Action b: reward 0, next value 4. v(s)?', '6.8', 'Average the two q values.', ['q(a) = 1 + 9 = 10.', 'q(b) = 0 + 3.6 = 3.6.', eq('0.5 &times; 10 + 0.5 &times; 3.6 = 6.8')], check=6.8)
K.calc('m', 'Cell 6 action values under the random policy are &minus;21, &minus;19, &minus;19, &minus;21. v<sub>&pi;</sub>(6)?', '-20', 'v = &Sigma; &pi; q.', ['Each action has chance 1/4.', 'Sum = &minus;80.', eq('&minus;80 / 4 = &minus;20')], check=-20)
K.calc('h', 'Gridworld with &minus;1 per move and exits in cells 0 and 15. Optimal value of cell 6 (row 1, column 2)?', '-3', 'Shortest path.', ['To cell 0: 1 up and 2 left = 3 moves.', 'To cell 15: 2 down and 1 right = 3 moves.', eq('v*(6) = &minus;3')], check=-3)
K.calc('h', 'Two state chain with P = [[0.9, 0.1], [0.5, 0.5]]. Stationary share of state 1?', '0.833', 'Balance the flows.', ['Flow out of 1: &pi;<sub>1</sub> &times; 0.1. Flow into 1: &pi;<sub>2</sub> &times; 0.5.', 'So &pi;<sub>1</sub> = 5&pi;<sub>2</sub> and &pi;<sub>1</sub> + &pi;<sub>2</sub> = 1.', eq('&pi;<sub>1</sub> = 5/6 = 0.833')], check=0.8333, tol=0.001)
K.calc('h', 'A state with reward &minus;1 stays with chance 0.6, else ends (value 0). &gamma; = 0.9. Its value?', '-2.174', 'V = &minus;1 + 0.9 &times; 0.6 V.', ['V &minus; 0.54V = &minus;1.', '0.46V = &minus;1.', eq('V = &minus;1 / 0.46 = &minus;2.174')], check=-2.1739, tol=0.002)
K.calc('x', 'In the style of a Stanford CS234 problem: how many deterministic stationary policies does an MDP with 10 states and 4 actions have?', '1048576', '|A|<sup>|S|</sup>.', ['4 choices in each of 10 states.', '4<sup>10</sup> = 2<sup>20</sup>.', eq('1,048,576')], check=1048576)

K.assign('step_distribution', 'e', 'Distribution after k steps',
         '<p>Write <code>step_distribution(dist, P, k)</code>. dist is a list of probabilities over states and P a transition matrix (list of rows). Return the distribution after k steps, each entry rounded to 3 decimals.</p>',
         """
def step_distribution(dist, P, k):
    # your code here
    pass
""", [('step_distribution([0, 0, 1], [[0.7, 0.2, 0.1], [0.3, 0.4, 0.3], [0.2, 0.4, 0.4]], 2)', [0.34, 0.36, 0.3]), ('step_distribution([1, 0], [[0.9, 0.1], [0.5, 0.5]], 1)', [0.9, 0.1]), ('step_distribution([1, 0], [[0.9, 0.1], [0.5, 0.5]], 50)', [0.833, 0.167])],
         """
def step_distribution(dist, P, k):
    d = list(dist)
    n = len(d)
    for _ in range(k):
        d = [sum(d[i] * P[i][j] for i in range(n)) for j in range(n)]
    return [round(v, 3) for v in d]
""", 'Each step, the new chance of j is the sum over i of d[i] times P[i][j].', '<p>After 50 steps the two state chain is at its stationary distribution, 5/6 and 1/6, whatever the start.</p>')
K.assign('mrp_values', 'm', 'Values by repeated backups',
         '<p>Write <code>mrp_values(P, R, gamma, sweeps)</code> that starts with all values 0 and repeats V &larr; R + &gamma;PV the given number of times. Return the values rounded to 3 decimals.</p>',
         """
def mrp_values(P, R, gamma, sweeps):
    # your code here
    pass
""", [('mrp_values([[0, 0.5, 0, 0.5, 0], [0, 0, 0.8, 0.2, 0], [0, 0, 0, 0.4, 0.6], [0.4, 0, 0, 0.6, 0], [0, 0, 0, 0, 1]], [-1, -2, 10, -1, 0], 0.9, 200)', [-0.138, 4.198, 9.179, -2.282, 0.0]), ('mrp_values([[0.6, 0.4], [0, 1]], [-1, 0], 0.9, 200)', [-2.174, 0.0]), ('mrp_values([[0, 1], [0, 1]], [5, 0], 0.5, 1)', [5.0, 0.0])],
         """
def mrp_values(P, R, gamma, sweeps):
    n = len(R)
    V = [0.0] * n
    for _ in range(sweeps):
        V = [R[s] + gamma * sum(P[s][t] * V[t] for t in range(n)) for s in range(n)]
    return [round(v, 3) for v in V]
""", 'Build the whole new list from the old one each sweep.', '<p>The first test matches the day MRP in the lesson. A synchronous update, which uses only old values, is the textbook form. Updating in place also converges and is often faster.</p>')
K.assign('one_step_lookahead', 'm', 'One step lookahead',
         '<p>Write <code>one_step_lookahead(P, R, V, gamma)</code> for one state. P[a] is the list of next state chances for action a, R[a] its expected reward, and V the list of next state values. Return the list of action values R[a] + &gamma; &Sigma; P[a][s&prime;] V[s&prime;], each rounded to 3 decimals.</p>',
         """
def one_step_lookahead(P, R, V, gamma):
    # your code here
    pass
""", [('one_step_lookahead([[1, 0], [0.5, 0.5]], [1, 2], [10, 0], 0.9)', [10.0, 6.5]), ('one_step_lookahead([[0, 1], [1, 0]], [-1, -1], [-20, -18], 1.0)', [-19.0, -21.0])],
         """
def one_step_lookahead(P, R, V, gamma):
    return [round(R[a] + gamma * sum(p * v for p, v in zip(P[a], V)), 3) for a in range(len(R))]
""", 'One line per action: reward plus discounted expected next value.', '<p>Taking the argmax of this list is the greedy step used by policy iteration and value iteration in the next chapter.</p>')

K.must('Markov', 'Next state depends only on the current state. Chain: P with rows adding to 1. d<sub>t+k</sub> = d<sub>t</sub>P<sup>k</sup>, stationary &pi; = &pi;P.')
K.must('MDP', '(S, A, p, R, &gamma;). MDP + fixed policy = MRP. MRP: V = R + &gamma;PV, V = (I &minus; &gamma;P)<sup>&minus;1</sup>R.')
K.must('Values', 'v<sub>&pi;</sub>(s) = E[G | s], q<sub>&pi;</sub>(s, a) = E[G | s, a]. v = &Sigma; &pi; q, q = &Sigma; p (r + &gamma;v).')
K.must('Optimality', 'v*(s) = max<sub>a</sub> &Sigma; p (r + &gamma;v*). Greedy on q* is optimal. Nonlinear, solved iteratively.')
K.must('Convergence', 'Bellman operator is a &gamma; contraction, unique fixed point, error shrinks by &gamma; per sweep.')
K.must('Gridworld', 'Random policy values &minus;14 to &minus;22, optimal values = &minus;distance to exit. Greedy on v<sub>&pi;</sub> improves &pi;.')

T = K.topic(
    slug='ml-mdp', topic='ml-mdp', step=(1, 'RL basics', 'ml-r1', 'Learn how an agent learns from rewards: returns and discounting, bandits that balance trying and using, and the Markov decision process behind every RL problem.', 'Intermediate'),
    title='Markov decision processes and Bellman equations', short='MDPs and Bellman', badge='1.3', minutes=50,
    lead='Frame every RL problem as a Markov decision process: the Markov property and chains, reward processes and their exact values, state and action values of a policy, and the Bellman expectation and optimality equations.',
    desc='Markov property, Markov chain, transition matrix, stationary distribution, Markov reward process, Markov decision process, value function, action value, Q function, Bellman expectation equation, Bellman optimality equation, optimal policy, gridworld, contraction, POMDP.',
    summary='Markov chains, reward processes, MDPs, state and action values, and the Bellman expectation and optimality equations.',
    keywords=['Markov decision process', 'MDP', 'Markov chain', 'Bellman equation', 'value function', 'Q function', 'optimal policy', 'stationary distribution', 'gridworld', 'POMDP'],
    recap='<p>An MDP is states, actions, transitions, rewards and a discount. Values obey the Bellman equations, a fixed policy gives a linear system, and the optimal policy acts greedily on q*.</p>',
    added='2026-11-13', leet=leet_items())
