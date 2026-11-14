# Reinforcement 2.1: dynamic programming. Checked against Sutton and Barto, Reinforcement Learning: An Introduction
# (2nd edition, 2018) chapter 4 (example 4.1 gridworld, example 4.3 gambler's problem), Bellman, Dynamic Programming
# (1957), Howard, Dynamic Programming and Markov Processes (1960) for policy iteration, Puterman, Markov Decision
# Processes (1994), and the Gymnasium FrozenLake environment (map and slippery dynamics).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-dp')
K = Kit()

K.code('policy_evaluation', r'''
import numpy as np

# 4 x 4 gridworld: exits in cells 0 and 15, every move costs -1, the policy moves each way with chance 1/4
moves = [-4, 4, -1, 1]                                   # up, down, left, right

def step(s, m):
    r, c = divmod(s, 4)
    if (m == -4 and r == 0) or (m == 4 and r == 3) or (m == -1 and c == 0) or (m == 1 and c == 3):
        return s                                         # bumping a wall leaves you in place
    return s + m

V = np.zeros(16)
for k in range(1, 1000):
    new = np.zeros(16)
    for s in range(1, 15):                               # the exits keep value 0
        new[s] = sum(0.25 * (-1 + V[step(s, m)]) for m in moves)
    delta = np.abs(new - V).max()
    V = new
    if k in (1, 2, 3, 10):
        print("after sweep", k)
        print(V.reshape(4, 4).round(1))
    if delta < 1e-4:
        break
print("converged after", k, "sweeps (largest change below 0.0001)")
print(V.reshape(4, 4).round(1))
''', long=True)

K.code('policy_iteration', r'''
import numpy as np

# The 4 x 4 FrozenLake map from Gymnasium: S start, F frozen, H hole, G goal. The ice is slippery:
# the agent moves the way it chose with chance 1/3, and to each side of it with chance 1/3.
MAP = "SFFF" "FHFH" "FFFH" "HFFG"
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]                # left, down, right, up (Gymnasium order)

def model():
    P = {}
    for s in range(16):
        for a in range(4):
            P[s, a] = []
            if MAP[s] in "HG":
                P[s, a].append((1.0, s, 0.0, True))
                continue
            for b in (a - 1, a, a + 1):
                r, c = divmod(s, 4)
                dr, dc = DIRS[b % 4]
                r, c = min(max(r + dr, 0), 3), min(max(c + dc, 0), 3)
                s2 = 4 * r + c
                P[s, a].append((1 / 3, s2, 1.0 if MAP[s2] == "G" else 0.0, MAP[s2] in "HG"))
    return P

gamma, ARROWS = 0.99, "<v>^"

def evaluate(policy, theta=1e-8):
    V = np.zeros(16)
    while True:
        delta = 0.0
        for s in range(16):
            v = sum(p * (r + gamma * V[s2] * (not done)) for p, s2, r, done in P[s, policy[s]])
            delta, V[s] = max(delta, abs(v - V[s])), v      # update in place
        if delta < theta:
            return V

def q_values(V, s):
    return [sum(p * (r + gamma * V[s2] * (not done)) for p, s2, r, done in P[s, a]) for a in range(4)]

P = model()
policy = [0] * 16                                        # start: always go left
for it in range(1, 20):
    V = evaluate(policy)                                 # 1. policy evaluation
    new = [int(np.argmax(np.round(q_values(V, s), 10))) for s in range(16)]   # 2. greedy improvement
    print("iteration", it, " value of the start", round(V[0], 3), " policy", "".join(ARROWS[a] if MAP[s] in "SF" else MAP[s] for s, a in enumerate(policy)))
    if new == policy:
        print("policy is stable, so it is optimal")
        break
    policy = new
''', long=True)

K.code('value_iteration', r'''
import numpy as np

# The 4 x 4 FrozenLake map from Gymnasium: S start, F frozen, H hole, G goal. The ice is slippery:
# the agent moves the way it chose with chance 1/3, and to each side of it with chance 1/3.
MAP = "SFFF" "FHFH" "FFFH" "HFFG"
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]                # left, down, right, up (Gymnasium order)

def model():
    P = {}
    for s in range(16):
        for a in range(4):
            P[s, a] = []
            if MAP[s] in "HG":
                P[s, a].append((1.0, s, 0.0, True))
                continue
            for b in (a - 1, a, a + 1):
                r, c = divmod(s, 4)
                dr, dc = DIRS[b % 4]
                r, c = min(max(r + dr, 0), 3), min(max(c + dc, 0), 3)
                s2 = 4 * r + c
                P[s, a].append((1 / 3, s2, 1.0 if MAP[s2] == "G" else 0.0, MAP[s2] in "HG"))
    return P

gamma, ARROWS = 0.99, "<v>^"
P = model()
V = np.zeros(16)
for sweep in range(1, 10000):
    delta = 0.0
    for s in range(16):
        best = max(sum(p * (r + gamma * V[s2] * (not done)) for p, s2, r, done in P[s, a]) for a in range(4))
        delta, V[s] = max(delta, abs(best - V[s])), best     # Bellman optimality backup
    if sweep in (1, 2, 5, 20, 100):
        print("sweep", str(sweep).rjust(3), " value of the start", round(V[0], 4))
    if delta < 1e-8:
        break
print("converged after", sweep, "sweeps")
policy = [int(np.argmax(np.round([sum(p * (r + gamma * V[s2] * (not done)) for p, s2, r, done in P[s, a]) for a in range(4)], 10))) for s in range(16)]
grid = "".join(ARROWS[a] if MAP[s] in "SF" else MAP[s] for s, a in enumerate(policy))
for row in range(4):
    print(grid[4 * row:4 * row + 4], " ", V[4 * row:4 * row + 4].round(3))
''', long=True)

K.code('gambler', r'''
import numpy as np

# Sutton and Barto example 4.3: bet part of your money on coin flips until you reach 100 or lose it all.
# Heads (chance 0.4) wins the stake, tails loses it. Reward 1 only for reaching 100.
p_heads, goal = 0.4, 100
V = np.zeros(goal + 1)
V[goal] = 1.0                                            # reaching the goal is worth 1
for sweep in range(1, 1000):
    delta = 0.0
    for s in range(1, goal):
        stakes = range(1, min(s, goal - s) + 1)
        best = max(p_heads * V[s + b] + (1 - p_heads) * V[s - b] for b in stakes)
        delta, V[s] = max(delta, abs(best - V[s])), best
    if delta < 1e-10:
        break
print("value iteration converged after", sweep, "sweeps")
for s in [10, 25, 40, 50, 60, 75, 90]:
    stakes = list(range(1, min(s, goal - s) + 1))
    q = np.round([p_heads * V[s + b] + (1 - p_heads) * V[s - b] for b in stakes], 9)
    print("capital", str(s).rjust(2), " chance of winning", round(V[s], 4), " best stake", stakes[int(np.argmax(q))])
''', long=True)

K.lesson('idea', 'Dynamic programming and policy evaluation', f'''
{src('Sutton and Barto (2018) sections 4.1 and 4.2, example 4.1.')}
{viz('mlpolicyeval')}
{wwh('<b>Dynamic programming</b> (DP) solves an MDP when the full model p(s&prime;, r | s, a) is known. Its first tool is <b>iterative policy evaluation</b>: start with any values and repeatedly replace every v(s) with the right side of the Bellman expectation equation for the policy, until the values stop changing.',
     'Solving the linear system directly costs about n<sup>3</sup> operations for n states. Sweeps cost about n<sup>2</sup> each (much less when each state has few successors), and the values converge geometrically. DP is also the foundation for every other RL method, which can be seen as DP with samples instead of a model.',
     'Loop over states, compute the expected one step reward plus discounted value of the next state under &pi;, and stop when the largest change in a sweep is below a small threshold &theta;. Updating in place (using new values as soon as they exist) usually converges faster than keeping two arrays.')}
{run('policy_evaluation')}
{note('After sweep 1 every cell is &minus;1. After sweep 2 a cell next to an exit is 0.25 &times; (&minus;1) + 0.75 &times; (&minus;2) = &minus;1.75, and others are &minus;2. With &gamma; = 1 it takes 173 sweeps for the largest change to fall below 0.0001, and the final values are the &minus;14 to &minus;22 seen in the last chapter.', 'exam')}
{fxs(fx('Policy evaluation update', 'v<sub>k+1</sub>(s) = &Sigma;<sub>a</sub> &pi;(a|s) &Sigma;<sub>s&prime;,r</sub> p(s&prime;, r | s, a)[r + &gamma; v<sub>k</sub>(s&prime;)]', 'Repeat until max change &lt; &theta;.', key=True),
     fx('Error after k sweeps', '&#8214;v<sub>k</sub> &minus; v<sub>&pi;</sub>&#8214;<sub>&infin;</sub> &le; &gamma;<sup>k</sup> &#8214;v<sub>0</sub> &minus; v<sub>&pi;</sub>&#8214;<sub>&infin;</sub>', 'Geometric convergence for &gamma; &lt; 1.'))}
''', kw=['dynamic programming', 'policy evaluation', 'iterative policy evaluation', 'synchronous update', 'in place update', 'convergence threshold'])

K.lesson('pi', 'Policy improvement and policy iteration', f'''
{src('Howard, Dynamic Programming and Markov Processes (1960), and Sutton and Barto (2018) sections 4.2 and 4.3.')}
{wwh('The <b>policy improvement theorem</b> says that acting greedily with respect to q<sub>&pi;</sub> gives a policy at least as good as &pi; in every state. <b>Policy iteration</b> alternates two steps: evaluate the current policy, then make it greedy with respect to its own values. It stops when the greedy policy no longer changes, and that policy is optimal.',
     'There are only finitely many deterministic policies and each step is a strict improvement until the end, so policy iteration must finish, usually in very few iterations, often fewer than 10 even for large problems.',
     'Start with any policy. Evaluate it fully. For every state pick argmax<sub>a</sub> q(s, a) using one step lookahead with the model. If nothing changed, stop. Break ties in a fixed way, or the loop can flip between equally good policies forever.')}
{run('policy_iteration')}
{note('Starting from "always go left", the value of the start rises from 0 to 0.121, 0.52, 0.532 and finally 0.542 after 7 iterations, when the policy stops changing. The optimal first move at the start is left, into the wall. On ice where you slide sideways two times in three, pushing against the wall means you can only slide down or stay put, never into danger. Good policies on slippery ice look odd but are safe.', 'exam')}
{steps('Policy iteration', [
    'Initialise &pi; arbitrarily, for example always left.',
    'Policy evaluation: compute v<sub>&pi;</sub> (sweeps or a linear solve).',
    'Policy improvement: &pi;&prime;(s) = argmax<sub>a</sub> &Sigma; p(s&prime;, r | s, a)[r + &gamma; v<sub>&pi;</sub>(s&prime;)] for every s.',
    'If &pi;&prime; = &pi;, stop: &pi; is optimal and v<sub>&pi;</sub> = v*.',
    'Otherwise set &pi; = &pi;&prime; and go back to step 2.'])}
''', kw=['policy improvement theorem', 'policy iteration', 'greedy policy', 'Howard', 'convergence in finite steps'])

K.lesson('vi', 'Value iteration', f'''
{src('Bellman (1957), and Sutton and Barto (2018) section 4.4.')}
{viz('mlvalueiter')}
{wwh('<b>Value iteration</b> skips the full evaluation. Each sweep applies the Bellman optimality equation as an update: v(s) &larr; max<sub>a</sub> &Sigma; p(s&prime;, r | s, a)[r + &gamma; v(s&prime;)]. When the values stop changing, the greedy policy for them is optimal.',
     'It is policy iteration with evaluation cut to a single sweep, which is often cheaper overall. It is also the direct ancestor of Q learning, which applies the same max backup using samples instead of the model.',
     'Initialise v = 0, sweep with the max backup until the largest change is below &theta;, then extract the policy with one step lookahead. The values spread backwards from the rewards, about one step per sweep, so the number of sweeps grows with the distance to reward and with 1 / (1 &minus; &gamma;).')}
{run('value_iteration')}
{note('Value iteration reaches exactly the same policy and the same start value, 0.542, as policy iteration, but needs 324 sweeps against 7 policy iterations (each of which hides many evaluation sweeps). The start value stays 0 for the first 5 sweeps because the reward is 6 steps away. The best cells are the two on the bottom row just before the goal: 0.863 and 0.742.', 'exam')}
{run('gambler')}
{note('Sutton and Barto’s gambler with a 0.4 coin: the best play is bold. With 50 you stake everything (win chance 0.4). With 25 you stake 25 to reach 50, so the win chance is 0.4 &times; 0.4 = 0.16. With 75 you stake 25 to reach 100 or fall back to 50, giving 0.4 + 0.6 &times; 0.4 = 0.64. When the odds are against you, fewer bets mean less time for the house edge to work.', 'tip')}
''', kw=['value iteration', 'Bellman optimality backup', 'policy extraction', 'FrozenLake', 'gambler problem', 'bold play'])

K.lesson('gpi', 'Generalised policy iteration and the limits of DP', f'''
{src('Sutton and Barto (2018) sections 4.5 to 4.8.')}
{wwh('<b>Generalised policy iteration</b> (GPI) is the idea behind almost every RL method: keep a value estimate and a policy, and let them improve each other. Evaluation makes the values match the policy, improvement makes the policy greedy for the values. How much of each step you do is a choice. <b>Asynchronous DP</b> updates states in any order, for example only those the agent visits.',
     'DP needs the full model and touches every state, so it breaks down when the model is unknown or the state space is huge. Bellman called this the <b>curse of dimensionality</b>: the number of states grows exponentially with the number of state variables. Seeing every later method as GPI with approximations makes them easy to place.',
     'Use DP when the model is known and the states fit in memory: inventory control, small games, robot planning on grids, and checking other algorithms. For unknown models, learn from samples (Monte Carlo and TD, next chapter). For huge spaces, approximate values with functions such as neural networks (deep RL).')}
{table(['Method', 'Model needed', 'Backup', 'Per step uses'], [
    ['Policy evaluation', 'Yes', 'Expected, under &pi;', 'All successor states'],
    ['Policy iteration', 'Yes', 'Full evaluation, then greedy', 'All successor states'],
    ['Value iteration', 'Yes', 'Expected, max over actions', 'All successor states'],
    ['Monte Carlo', 'No', 'Sampled full return', 'One episode'],
    ['TD and Q learning', 'No', 'Sampled one step, bootstrapped', 'One transition']])}
{deep('Linear programming and the cost of solving MDPs exactly', '<p>An MDP can also be solved as a linear program: minimise &Sigma;<sub>s</sub> v(s) subject to v(s) &ge; &Sigma; p(s&prime;, r | s, a)[r + &gamma;v(s&prime;)] for every state and action. The smallest v that satisfies all the constraints is v*, which proves that MDPs can be solved in polynomial time. Policy iteration needs at most a number of iterations that is polynomial in the number of states and actions for a fixed &gamma; (Ye, 2011), and in practice far fewer. Value iteration needs about log(1/&epsilon;) / (1 &minus; &gamma;) sweeps for accuracy &epsilon;, so &gamma; close to 1 makes it slow. Prioritised sweeping, which updates the states whose values would change most first, speeds DP up a lot on large sparse problems.</p>')}
''', kw=['generalised policy iteration', 'asynchronous DP', 'curse of dimensionality', 'linear programming', 'prioritised sweeping'])

K.lesson('versus', 'Policy iteration and value iteration compared', f'''
{versus('Two ways to solve a known MDP', ['', 'Policy iteration', 'Value iteration'], [
    ['Each iteration', 'Full evaluation, then greedy improvement', 'One sweep of max backups'],
    ['Iterations to finish', 'Few (often under 10)', 'Many (hundreds when &gamma; is near 1)'],
    ['Cost per iteration', 'High (a full evaluation)', 'Low (one sweep)'],
    ['Stops when', 'The policy does not change', 'Values change less than &theta;'],
    ['Gives', 'Exact optimal policy', 'Near optimal values, then the greedy policy'],
    ['Leads on to', 'Actor critic methods', 'Q learning']],
    'use policy iteration when evaluation is cheap or the number of policies is small, value iteration when sweeps are cheap. Both give the same optimal policy.')}
''', kw=['policy iteration vs value iteration', 'dynamic programming comparison'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Policy evaluation', 'v<sub>k+1</sub> = r<sub>&pi;</sub> + &gamma; P<sub>&pi;</sub> v<sub>k</sub>', 'Matrix form for a fixed policy.', key=True),
     fx('Greedy improvement', '&pi;&prime;(s) = argmax<sub>a</sub> q<sub>&pi;</sub>(s, a)', 'Never worse than &pi;.', key=True),
     fx('Policy improvement theorem', 'q<sub>&pi;</sub>(s, &pi;&prime;(s)) &ge; v<sub>&pi;</sub>(s) for all s &rArr; v<sub>&pi;&prime;</sub>(s) &ge; v<sub>&pi;</sub>(s) for all s', 'Sutton and Barto section 4.2.', key=True),
     fx('Value iteration', 'v<sub>k+1</sub>(s) = max<sub>a</sub> &Sigma;<sub>s&prime;,r</sub> p(s&prime;, r | s, a)[r + &gamma; v<sub>k</sub>(s&prime;)]', 'The optimality operator applied once per sweep.', key=True),
     fx('Sweeps for accuracy &epsilon;', 'k &ge; log(&epsilon; / e<sub>0</sub>) / log &gamma;', 'From e<sub>k</sub> &le; &gamma;<sup>k</sup> e<sub>0</sub>.'),
     fx('Stopping rule', 'if &#8214;v<sub>k+1</sub> &minus; v<sub>k</sub>&#8214; &lt; &theta;(1 &minus; &gamma;)/(2&gamma;) then the greedy policy is &theta; optimal', 'Williams and Baird (1993).'),
     fx('Cost of one sweep', 'O(|S|<sup>2</sup> |A|)', 'Less with sparse transitions.'))}
{steps('Worked example: one value iteration backup', [
    '&gamma; = 0.9. Action a: with chance 0.5 reward 1 and the episode ends, with chance 0.5 reward 0 and a state worth 10.',
    'Action b: reward 0 for sure and a state worth 6.',
    eq('Q(a) = 0.5 &times; (1 + 0) + 0.5 &times; (0 + 0.9 &times; 10) = 0.5 + 4.5 = 5'),
    eq('Q(b) = 0 + 0.9 &times; 6 = 5.4'),
    'The backup sets v(s) = max(5, 5.4) = 5.4, and the greedy action is b.'])}
{deep('Proof sketch of the policy improvement theorem', '<p>Suppose q<sub>&pi;</sub>(s, &pi;&prime;(s)) &ge; v<sub>&pi;</sub>(s) everywhere. Start from v<sub>&pi;</sub>(s) &le; q<sub>&pi;</sub>(s, &pi;&prime;(s)) = E[R<sub>t+1</sub> + &gamma; v<sub>&pi;</sub>(S<sub>t+1</sub>) | A<sub>t</sub> = &pi;&prime;(s)]. Apply the same inequality to v<sub>&pi;</sub>(S<sub>t+1</sub>) inside the expectation, then to v<sub>&pi;</sub>(S<sub>t+2</sub>), and so on. After unrolling, the right side becomes the expected discounted return of following &pi;&prime; forever, which is v<sub>&pi;&prime;</sub>(s). If the greedy step changes nothing, then v<sub>&pi;</sub> satisfies the Bellman optimality equation, so it equals v* and &pi; is optimal.</p>')}
''', kw=['policy evaluation matrix form', 'policy improvement theorem', 'value iteration formula', 'stopping rule', 'proof'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>When you know exactly how the world works, you can compute the best plan by repeatedly asking "what is each state worth?" until the answers settle.</p>',
    '<p>Code iterative policy evaluation, policy iteration and value iteration, extract a greedy policy, and pick a sensible stopping threshold.</p>',
    '<p>Explain the policy improvement theorem, compare the costs of policy and value iteration, use asynchronous and in place updates, and place every RL method within generalised policy iteration.</p>',
    '<p>Study the linear programming view, complexity bounds for policy iteration, prioritised sweeping, approximate DP with function approximation, and real time DP.</p>')}
{grow('Explain how values and policies improve each other.',
      'Solve small known MDPs with DP.',
      'Analyse convergence and cost of DP methods.')}
''', kw=['beginner', 'expert', 'approximate dynamic programming', 'real time dynamic programming'])

lc(1137, 'N-th Tribonacci Number', 'n-th-tribonacci-number', 'e', 'Carry the last three values forward', 'Each term is the sum of the three before it. Update three variables at once. Carrying a small state forward and updating it again and again is what every DP sweep does.', r"""
def tribonacci(n):
    a, b, c = 0, 1, 1
    for _ in range(n):
        a, b, c = b, c, a + b + c
    return a
""", [('tribonacci(4)', 4), ('tribonacci(25)', 1389537)])
lc(118, "Pascal's Triangle", 'pascals-triangle', 'e', 'Each row comes from the row above', 'Every inner number is the sum of the two numbers above it. Building a new row entirely from the previous one is a synchronous sweep: the old values are read, the new ones written.', r"""
def generate(num_rows):
    rows = [[1]]
    for _ in range(num_rows - 1):
        prev = rows[-1]
        rows.append([1] + [prev[i] + prev[i + 1] for i in range(len(prev) - 1)] + [1])
    return rows
""", [('generate(5)', [[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1]]), ('generate(1)', [[1]])])
lc(198, 'House Robber', 'house-robber', 'm', 'Two values: best total if you rob this house, and if you skip it', 'At each house choose the better of robbing it (the previous skip total plus its money) or skipping it (the better of the two previous totals). A max over two actions at every step is a Bellman optimality backup.', r"""
def rob(nums):
    take, skip = 0, 0
    for v in nums:
        take, skip = skip + v, max(take, skip)
    return max(take, skip)
""", [('rob([1, 2, 3, 1])', 4), ('rob([2, 7, 9, 3, 1])', 12)])
lc(322, 'Coin Change', 'coin-change', 'm', 'Fewest coins for each amount, built from smaller amounts', 'best[a] is the minimum over coins c of best[a &minus; c] + 1. Each amount is a state, each coin an action with cost 1, and the table is filled like value iteration on a deterministic MDP.', r"""
def coin_change(coins, amount):
    INF = amount + 1
    best = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and best[a - c] + 1 < best[a]:
                best[a] = best[a - c] + 1
    return best[amount] if best[amount] <= amount else -1
""", [('coin_change([1, 2, 5], 11)', 3), ('coin_change([2], 3)', -1), ('coin_change([1], 0)', 0)])
lc(787, 'Cheapest Flights Within K Stops', 'cheapest-flights-within-k-stops', 'm', 'Bellman Ford for k + 1 rounds, reading only last round’s costs', 'Run k + 1 rounds of relaxing every flight, but compute each round from a copy of the previous costs, so a round adds at most one flight. Bellman Ford is value iteration for shortest paths: each round is one sweep of the Bellman backup with costs.', r"""
def find_cheapest_price(n, flights, src, dst, k):
    INF = float("inf")
    cost = [INF] * n
    cost[src] = 0
    for _ in range(k + 1):
        new = cost[:]
        for u, v, w in flights:
            if cost[u] + w < new[v]:
                new[v] = cost[u] + w
        cost = new
    return cost[dst] if cost[dst] < INF else -1
""", [('find_cheapest_price(4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1)', 700), ('find_cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1)', 200), ('find_cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0)', 500)])
lc(1463, 'Cherry Pickup II', 'cherry-pickup-ii', 'h', 'State = the two robots’ columns, swept row by row', 'Both robots move down one row at a time, so the state is the pair of columns. For each row, every pair of moves (9 of them) updates the best total for the new pair, counting a shared cell once. Sweeping a state table forward row by row with a max over joint actions is DP over a joint state space.', r"""
def cherry_pickup(grid):
    rows, cols = len(grid), len(grid[0])
    NEG = float("-inf")
    best = [[NEG] * cols for _ in range(cols)]
    best[0][cols - 1] = grid[0][0] + (grid[0][cols - 1] if cols > 1 else 0)
    for r in range(1, rows):
        new = [[NEG] * cols for _ in range(cols)]
        for a in range(cols):
            for b in range(cols):
                if best[a][b] == NEG:
                    continue
                for na in (a - 1, a, a + 1):
                    for nb in (b - 1, b, b + 1):
                        if 0 <= na < cols and 0 <= nb < cols:
                            gain = grid[r][na] + (grid[r][nb] if na != nb else 0)
                            if best[a][b] + gain > new[na][nb]:
                                new[na][nb] = best[a][b] + gain
        best = new
    return max(max(row) for row in best)
""", [('cherry_pickup([[3, 1, 1], [2, 5, 1], [1, 5, 5], [2, 1, 1]])', 24), ('cherry_pickup([[1, 0, 0, 0, 0, 0, 1], [2, 0, 0, 0, 0, 3, 0], [2, 0, 9, 0, 0, 0, 0], [0, 3, 0, 5, 4, 0, 0], [1, 0, 2, 3, 0, 0, 6]])', 28)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Dynamic programming in RL fills a table of values by repeated backups. These problems practise carrying a small state forward, synchronous row by row updates, a max over two actions, minimum cost backups over many actions, Bellman Ford rounds that read only the previous round, and DP over a joint state of two agents. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'dynamic programming', 'Bellman Ford', 'shortest paths', 'state space'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Dynamic programming</b> solves MDPs with a known model by repeated Bellman backups over all states.',
    '<b>Policy evaluation</b> sweeps v(s) &larr; &Sigma; &pi; &Sigma; p (r + &gamma;v) until the largest change is below &theta;.',
    '<b>Policy improvement</b>: being greedy on q<sub>&pi;</sub> is never worse. <b>Policy iteration</b> alternates both and stops in few iterations.',
    '<b>Value iteration</b> sweeps v(s) &larr; max<sub>a</sub> &Sigma; p (r + &gamma;v), then extracts the greedy policy.',
    'On slippery FrozenLake both reach start value 0.542, and the best first move points into a wall for safety.',
    '<b>GPI</b>: values and policies improve each other. DP needs a model and suffers the curse of dimensionality.'],
    'Reinforcement 2.2 learns without a model: Monte Carlo and temporal difference learning.')}
{files('Three tasks: evaluate a policy, make a policy greedy, and run value iteration.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Dynamic programming in RL requires', ['No model', 'A full model of transitions and rewards', 'A neural network', 'Labels'], 1, 'Planning.', 'p(s&prime;, r | s, a) must be known.')
K.quiz('e', 'Policy evaluation computes', ['The best policy', 'The value of a given policy', 'The rewards', 'The transition matrix'], 1, 'Prediction.', 'v<sub>&pi;</sub>.')
K.quiz('e', 'Policy iteration alternates', ['Training and testing', 'Evaluation and greedy improvement', 'Exploration and exploitation', 'Sampling and sorting'], 1, 'Two steps.', 'Until the policy stops changing.')
K.quiz('e', 'Value iteration updates each state with', ['The average over actions', 'The maximum over actions of the expected backup', 'A random action', 'The reward only'], 1, 'Optimality backup.', 'max<sub>a</sub>.')
K.quiz('m', 'Greedy improvement on q<sub>&pi;</sub> gives a policy that is', ['Possibly worse', 'At least as good as &pi; in every state', 'Random', 'Always the same as &pi;'], 1, 'Policy improvement theorem.', 'Strictly better unless already optimal.')
K.quiz('m', 'Why does policy iteration stop after finitely many steps?', ['It has a timer', 'There are finitely many deterministic policies and each step strictly improves until the end', 'Values are bounded', 'Because &gamma; &lt; 1'], 1, 'No cycles.', 'With consistent tie breaking.')
K.quiz('m', 'Compared with policy iteration, value iteration usually needs', ['Fewer iterations', 'More but cheaper iterations', 'No iterations', 'A neural network'], 1, 'One sweep each.', 'Hundreds on FrozenLake against 7.')
K.quiz('m', 'On very slippery FrozenLake the best first move at the start points left into the wall because', ['It is a bug', 'Pushing into the wall means you can only slide down or stay, never into a hole', 'Left is always best', 'The goal is on the left'], 1, 'Safety.', 'Sliding happens to the sides of the chosen direction.')
K.quiz('m', 'In place updates during a sweep', ['Never converge', 'Use new values immediately and often converge faster', 'Are forbidden', 'Need two arrays'], 1, 'Gauss Seidel style.', 'Still converge for &gamma; &lt; 1.')
K.quiz('h', 'The curse of dimensionality means', ['Too few states', 'The number of states grows exponentially with the number of state variables', 'Rewards are delayed', 'Policies are random'], 1, 'Bellman.', 'Ten variables with ten values give 10<sup>10</sup> states.')
K.quiz('h', 'Generalised policy iteration describes', ['Only DP', 'Almost all RL methods: values and policy improving each other', 'Supervised learning', 'Bandits only'], 1, 'Evaluation and improvement interleaved.', 'Sutton and Barto section 4.6.')
K.quiz('h', 'Value iteration slows down as &gamma; approaches 1 because', ['Rewards grow', 'The error shrinks only by a factor &gamma; per sweep', 'States multiply', 'The max is harder'], 1, 'Contraction factor.', 'About log(1/&epsilon;)/(1 &minus; &gamma;) sweeps.')
K.quiz('x', 'In the style of a Stanford CS234 exam: an MDP can be solved exactly in polynomial time by', ['Brute force over policies', 'Linear programming', 'Random search', 'Gradient descent only'], 1, 'Constraints v &ge; backup.', 'Minimise the sum of values.')
K.quiz('x', 'In the style of a Stanford CS234 exam: the gambler with a 0.4 coin and 25 dollars of 100 should', ['Bet 1 at a time', 'Bet 25 to reach 50', 'Never bet', 'Bet half'], 1, 'Bold play.', 'Fewer bets give the house edge less time.')

K.calc('e', 'Gridworld random policy, &gamma; = 1. After sweep 1 all cells are &minus;1. Sweep 2 value of a cell next to an exit (one of four moves reaches the exit)?', '-1.75', 'Average over four moves.', ['Into the exit: &minus;1 + 0 = &minus;1.', 'Other three moves: &minus;1 + (&minus;1) = &minus;2 each.', eq('0.25 &times; (&minus;1) + 0.75 &times; (&minus;2) = &minus;1.75')], check=-1.75)
K.calc('e', '&gamma; = 0.9. Action a: chance 0.5 of reward 1 and the end, chance 0.5 of reward 0 and a state worth 10. Action b: reward 0 and a state worth 6. Value iteration backup?', '5.4', 'Max of the two.', ['Q(a) = 0.5 + 0.5 &times; 9 = 5.', 'Q(b) = 0.9 &times; 6 = 5.4.', eq('max(5, 5.4) = 5.4')], check=5.4)
K.calc('m', 'Start error 10 and &gamma; = 0.9. Bound on the error after 20 sweeps?', '1.216', 'e<sub>0</sub> &gamma;<sup>k</sup>.', ['0.9<sup>20</sup> = 0.1216.', 'Times 10.', eq('1.216')], check=1.2158, tol=0.002)
K.calc('m', 'Start error 10 and &gamma; = 0.9. Sweeps needed to guarantee error below 0.01?', '66', 'k &ge; log(0.001)/log(0.9).', ['Need 0.9<sup>k</sup> &le; 0.001.', 'log(0.001) / log(0.9) = 65.56.', eq('k = 66')], check=66)
K.calc('m', 'Slippery FrozenLake (1/3 chosen way, 1/3 each side). At the start (top left) the agent chooses left. Chance it stays in the start cell?', '0.667', 'Which slides hit a wall?', ['Left hits the wall: stay.', 'Sliding up hits the wall: stay. Sliding down moves.', eq('1/3 + 1/3 = 2/3 = 0.667')], check=0.6667, tol=0.001)
K.calc('m', 'Gambler, coin 0.4, capital 50, stake 50. Chance of reaching 100?', '0.4', 'One flip decides.', ['Heads: 100, worth 1.', 'Tails: 0, worth 0.', eq('0.4 &times; 1 + 0.6 &times; 0 = 0.4')], check=0.4)
K.calc('h', 'Gambler, coin 0.4, capital 25, stake 25, and V(50) = 0.4. V(25)?', '0.16', '0.4 &times; V(50).', ['Heads: 50, worth 0.4.', 'Tails: 0, worth 0.', eq('0.4 &times; 0.4 = 0.16')], check=0.16)
K.calc('h', 'How many deterministic policies does the 16 state, 4 action FrozenLake have?', '4294967296', '4<sup>16</sup>.', ['4 choices per state.', '4<sup>16</sup> = 2<sup>32</sup>.', eq('4,294,967,296')], check=4294967296)
K.calc('h', 'Dense model with 16 states and 4 actions. Multiply adds in one value iteration sweep (every state, action and next state)?', '1024', '|S|<sup>2</sup> |A|.', ['16 &times; 16 = 256.', 'Times 4 actions.', eq('1,024')], check=1024)
K.calc('x', 'In the style of a Stanford CS234 problem: FrozenLake without sliding, &gamma; = 0.99, reward 1 on reaching the goal 6 moves away. Optimal value of the start?', '0.951', 'The reward is on the 6th transition.', ['v(cell before goal) = 1.', 'Each earlier cell multiplies by &gamma;: 5 more factors.', eq('0.99<sup>5</sup> = 0.951')], check=0.951, tol=0.001)

K.assign('evaluate_policy', 'm', 'Policy evaluation',
         '<p>Write <code>evaluate_policy(P, R, policy, gamma, theta)</code>. P[s][a] is a list of [chance, next state] pairs, R[s][a] the reward for taking a in s, and policy[s] the action taken in s. Sweep in place until the largest change is below theta. Return the values rounded to 3 decimals.</p>',
         """
def evaluate_policy(P, R, policy, gamma, theta):
    # your code here
    pass
""", [('evaluate_policy([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], [1, 1, 0], 0.9, 1e-9)', [1.0, 0.9, 0.0]), ('evaluate_policy([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], [0, 0, 0], 0.9, 1e-9)', [4.5, 5.0, 0.0])],
         """
def evaluate_policy(P, R, policy, gamma, theta):
    V = [0.0] * len(P)
    while True:
        delta = 0.0
        for s in range(len(P)):
            a = policy[s]
            v = R[s][a] + gamma * sum(p * V[s2] for p, s2 in P[s][a])
            delta = max(delta, abs(v - V[s]))
            V[s] = v
        if delta < theta:
            return [round(v, 3) for v in V]
""", 'For each state use only the action the policy picks.', '<p>In the small test MDP, state 2 loops to itself with reward 0, so it plays the role of a terminal state with value 0.</p>')
K.assign('greedy_policy', 'm', 'Greedy policy from values',
         '<p>Write <code>greedy_policy(P, R, V, gamma)</code> that returns, for every state, the action with the largest R[s][a] + gamma &Sigma; chance &times; V[next]. On a tie pick the lowest action number.</p>',
         """
def greedy_policy(P, R, V, gamma):
    # your code here
    pass
""", [('greedy_policy([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], [1.0, 0.9, 0.0], 0.9)', [1, 0, 0]), ('greedy_policy([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], [4.5, 5.0, 0.0], 0.9)', [0, 0, 0])],
         """
def greedy_policy(P, R, V, gamma):
    policy = []
    for s in range(len(P)):
        q = [R[s][a] + gamma * sum(p * V[s2] for p, s2 in P[s][a]) for a in range(len(P[s]))]
        policy.append(q.index(max(q)))
    return policy
""", 'Compute the action values for each state and take the first maximum.', '<p>Feeding the values of policy [1, 1, 0] into this function gives [1, 0, 0], a better policy. Repeating evaluation and this step is policy iteration.</p>')
K.assign('value_iteration_solve', 'h', 'Value iteration',
         '<p>Write <code>value_iteration_solve(P, R, gamma, theta)</code> in the same format. Sweep v(s) &larr; max<sub>a</sub> [R[s][a] + gamma &Sigma; chance &times; v(next)] in place until the largest change is below theta. Return [values rounded to 3 decimals, greedy policy], with ties going to the lowest action.</p>',
         """
def value_iteration_solve(P, R, gamma, theta):
    # your code here
    pass
""", [('value_iteration_solve([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], 0.9, 1e-9)', [[4.5, 5.0, 0.0], [0, 0, 0]]), ('value_iteration_solve([[[[1, 1]], [[1, 2]]], [[[1, 2]], [[1, 0]]], [[[1, 2]], [[1, 2]]]], [[0, 1], [5, 0], [0, 0]], 0.1, 1e-9)', [[1.0, 5.0, 0.0], [1, 0, 0]])],
         """
def value_iteration_solve(P, R, gamma, theta):
    n = len(P)
    V = [0.0] * n

    def q_of(s, a):
        return R[s][a] + gamma * sum(p * V[s2] for p, s2 in P[s][a])

    while True:
        delta = 0.0
        for s in range(n):
            best = max(q_of(s, a) for a in range(len(P[s])))
            delta = max(delta, abs(best - V[s]))
            V[s] = best
        if delta < theta:
            break
    policy = []
    for s in range(n):
        q = [q_of(s, a) for a in range(len(P[s]))]
        policy.append(q.index(max(q)))
    return [[round(v, 3) for v in V], policy]
""", 'Same backup as policy evaluation, but with a max over actions.', '<p>With &gamma; = 0.9 it pays to wait one step for the 5 (worth 4.5 now). With &gamma; = 0.1 the 5 is worth only 0.5 from state 0, so taking the 1 at once is better.</p>')

K.must('DP', 'Known model, sweeps of Bellman backups over all states. Stop when max change &lt; &theta;.')
K.must('Evaluation', 'v(s) &larr; &Sigma; &pi;(a|s) &Sigma; p (r + &gamma;v(s&prime;)). Error shrinks by &gamma; per sweep. In place is fine.')
K.must('Policy iteration', 'Evaluate, then greedy improve. Improvement theorem. Few iterations, stops when the policy is stable.')
K.must('Value iteration', 'v(s) &larr; max<sub>a</sub> &Sigma; p (r + &gamma;v(s&prime;)), then greedy extraction. Many cheap sweeps.')
K.must('Examples', 'Gridworld &minus;14 to &minus;22, FrozenLake start 0.542 (slippery, &gamma; 0.99), gambler bets boldly at 25, 50, 75.')
K.must('Limits', 'GPI is the pattern of all RL. DP needs a model and suffers the curse of dimensionality. LP solves MDPs in polynomial time.')

T = K.topic(
    slug='ml-dp', topic='ml-dp', step=(2, 'Solving MDPs', 'ml-r2', 'Find good policies: plan with a known model by dynamic programming, then learn from experience with Monte Carlo, temporal difference learning, SARSA and Q learning.', 'Advanced'),
    title='Dynamic programming: policy and value iteration', short='Dynamic programming', badge='2.1', minutes=50,
    lead='Solve MDPs with a known model: iterative policy evaluation, the policy improvement theorem and policy iteration, value iteration on slippery FrozenLake and the gambler’s problem, and generalised policy iteration.',
    desc='dynamic programming, policy evaluation, policy improvement theorem, policy iteration, value iteration, Bellman backup, greedy policy, FrozenLake, gambler problem, generalised policy iteration, asynchronous DP, curse of dimensionality, linear programming.',
    summary='Policy evaluation, policy iteration, value iteration on FrozenLake and the gambler, and generalised policy iteration.',
    keywords=['dynamic programming', 'policy iteration', 'value iteration', 'policy evaluation', 'policy improvement', 'FrozenLake', 'gambler problem', 'generalised policy iteration', 'Bellman backup', 'curse of dimensionality'],
    recap='<p>With a known model, sweep Bellman backups. Policy iteration evaluates and improves, value iteration backs up the max. Both reach the optimal policy, and their pattern, GPI, runs through all of RL.</p>',
    added='2026-11-13', leet=leet_items())
