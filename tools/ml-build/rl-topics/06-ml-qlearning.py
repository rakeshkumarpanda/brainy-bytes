# Reinforcement 2.3: SARSA and Q learning. Checked against Sutton and Barto, Reinforcement Learning: An Introduction
# (2nd edition, 2018) chapters 5 and 6 (example 6.6 cliff walking, example 6.7 maximisation bias), Watkins, Learning
# from Delayed Rewards (PhD thesis, Cambridge 1989), Watkins and Dayan, Q-learning (Machine Learning 1992), Rummery
# and Niranjan, On-line Q-learning using connectionist systems (1994, the origin of SARSA), van Seijen and colleagues,
# A Theoretical and Empirical Analysis of Expected Sarsa (2009), and van Hasselt, Double Q-learning (NeurIPS 2010).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-qlearning')
K = Kit()

K.code('sarsa_cliff', r'''
import numpy as np

# Cliff walking (Sutton and Barto example 6.6): a 4 x 12 grid. Start bottom left, goal bottom right.
# The cells between them on the bottom row are a cliff: stepping in costs -100 and sends you back to the start.
# Every other move costs -1. Actions: 0 up, 1 down, 2 left, 3 right.
ROWS, COLS = 4, 12
START, GOAL = (3, 0), (3, 11)
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def step(state, a):
    r, c = state[0] + MOVES[a][0], state[1] + MOVES[a][1]
    r, c = min(max(r, 0), ROWS - 1), min(max(c, 0), COLS - 1)
    if r == 3 and 1 <= c <= 10:
        return START, -100, False                        # fell off the cliff
    return (r, c), -1, (r, c) == GOAL

def eps_greedy(Q, s, eps, rng):
    if rng.random() < eps:
        return int(rng.integers(4))
    q = Q[s]
    return int(rng.choice(np.flatnonzero(q == q.max())))  # break ties at random

def greedy_path(Q):
    s, path = START, [START]
    for _ in range(50):
        s, _, done = step(s, int(np.argmax(Q[s])))
        path.append(s)
        if done:
            break
    rows = [["." for _ in range(COLS)] for _ in range(ROWS)]
    for c in range(1, 11):
        rows[3][c] = "C"
    for (r, c) in path:
        rows[r][c] = "o"
    return "\n".join("".join(row) for row in rows)

rng = np.random.default_rng(0)
Q = np.zeros((ROWS, COLS, 4))
alpha, gamma, eps = 0.5, 1.0, 0.1
totals = []
for ep in range(500):
    s, done, total = START, False, 0
    a = eps_greedy(Q, s, eps, rng)
    while not done:
        s2, r, done = step(s, a)
        a2 = eps_greedy(Q, s2, eps, rng)                  # SARSA: pick the next action first
        target = r + (0 if done else gamma * Q[s2][a2])   # and learn from the action it will really take
        Q[s][a] += alpha * (target - Q[s][a])
        s, a, total = s2, a2, total + r
    totals.append(total)
print("SARSA, average reward per episode over the last 100:", np.mean(totals[-100:]))
print("greedy path (o) after learning, C = cliff:")
print(greedy_path(Q))
''', long=True)

K.code('q_learning_cliff', r'''
import numpy as np

# Cliff walking (Sutton and Barto example 6.6): a 4 x 12 grid. Start bottom left, goal bottom right.
# The cells between them on the bottom row are a cliff: stepping in costs -100 and sends you back to the start.
# Every other move costs -1. Actions: 0 up, 1 down, 2 left, 3 right.
ROWS, COLS = 4, 12
START, GOAL = (3, 0), (3, 11)
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def step(state, a):
    r, c = state[0] + MOVES[a][0], state[1] + MOVES[a][1]
    r, c = min(max(r, 0), ROWS - 1), min(max(c, 0), COLS - 1)
    if r == 3 and 1 <= c <= 10:
        return START, -100, False                        # fell off the cliff
    return (r, c), -1, (r, c) == GOAL

def eps_greedy(Q, s, eps, rng):
    if rng.random() < eps:
        return int(rng.integers(4))
    q = Q[s]
    return int(rng.choice(np.flatnonzero(q == q.max())))  # break ties at random

def greedy_path(Q):
    s, path = START, [START]
    for _ in range(50):
        s, _, done = step(s, int(np.argmax(Q[s])))
        path.append(s)
        if done:
            break
    rows = [["." for _ in range(COLS)] for _ in range(ROWS)]
    for c in range(1, 11):
        rows[3][c] = "C"
    for (r, c) in path:
        rows[r][c] = "o"
    return "\n".join("".join(row) for row in rows)

rng = np.random.default_rng(0)
Q = np.zeros((ROWS, COLS, 4))
alpha, gamma, eps = 0.5, 1.0, 0.1
totals = []
for ep in range(500):
    s, done, total = START, False, 0
    while not done:
        a = eps_greedy(Q, s, eps, rng)
        s2, r, done = step(s, a)
        target = r + (0 if done else gamma * Q[s2].max())   # Q learning: assume the best action next
        Q[s][a] += alpha * (target - Q[s][a])
        s, total = s2, total + r
    totals.append(total)
print("Q learning, average reward per episode over the last 100:", np.mean(totals[-100:]))
print("greedy path (o) after learning, C = cliff:")
print(greedy_path(Q))
''', long=True)

K.code('compare_control', r'''
import numpy as np

# Cliff walking (Sutton and Barto example 6.6): a 4 x 12 grid. Start bottom left, goal bottom right.
# The cells between them on the bottom row are a cliff: stepping in costs -100 and sends you back to the start.
# Every other move costs -1. Actions: 0 up, 1 down, 2 left, 3 right.
ROWS, COLS = 4, 12
START, GOAL = (3, 0), (3, 11)
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def step(state, a):
    r, c = state[0] + MOVES[a][0], state[1] + MOVES[a][1]
    r, c = min(max(r, 0), ROWS - 1), min(max(c, 0), COLS - 1)
    if r == 3 and 1 <= c <= 10:
        return START, -100, False                        # fell off the cliff
    return (r, c), -1, (r, c) == GOAL

def eps_greedy(Q, s, eps, rng):
    if rng.random() < eps:
        return int(rng.integers(4))
    q = Q[s]
    return int(rng.choice(np.flatnonzero(q == q.max())))  # break ties at random

def run(method, episodes=200, alpha=0.5, eps=0.1, seed=0):
    rng = np.random.default_rng(seed)
    Q = np.zeros((ROWS, COLS, 4))
    totals = []
    for ep in range(episodes):
        s, done, total = START, False, 0
        a = eps_greedy(Q, s, eps, rng)
        while not done:
            s2, r, done = step(s, a)
            a2 = eps_greedy(Q, s2, eps, rng)
            if done:
                nxt = 0.0
            elif method == "Q learning":
                nxt = Q[s2].max()
            elif method == "SARSA":
                nxt = Q[s2][a2]
            else:                                        # expected SARSA: average over the epsilon greedy choice
                probs = np.full(4, eps / 4)
                probs[np.argmax(Q[s2])] += 1 - eps
                nxt = probs @ Q[s2]
            Q[s][a] += alpha * (r + nxt - Q[s][a])
            s, a, total = s2, a2, total + r
        totals.append(total)
    return np.mean(totals[-100:])

for method in ["Q learning", "SARSA", "Expected SARSA"]:
    scores = [run(method, seed=k) for k in range(5)]
    print(method.ljust(15), " average reward per episode while learning (last 100 of 200, 5 runs):", round(float(np.mean(scores)), 1))
''', long=True)

K.code('double_q', r'''
import numpy as np

# Sutton and Barto example 6.7. From A, "right" ends the episode with reward 0. "left" moves to B with reward 0,
# and every one of B's 10 actions ends the episode with a reward drawn from a normal curve with mean -0.1.
# So going left is a bad idea on average, but the max over noisy estimates of B's actions looks positive.
def run(double, episodes=300, alpha=0.1, eps=0.1, seed=0):
    rng = np.random.default_rng(seed)
    QA = [np.zeros(2), np.zeros(2)]                       # two tables for double Q learning (A: 0 left, 1 right)
    QB = [np.zeros(10), np.zeros(10)]
    lefts = []
    for ep in range(episodes):
        qa = QA[0] + QA[1] if double else QA[0]
        a = int(rng.integers(2)) if rng.random() < eps else int(rng.choice(np.flatnonzero(qa == qa.max())))
        lefts.append(a == 0)
        if a == 1:
            i = int(rng.integers(2)) if double else 0
            QA[i][1] += alpha * (0 - QA[i][1])
            continue
        i = int(rng.integers(2)) if double else 0           # update table i, using the other table to judge its best action
        j = 1 - i if double else 0
        best_b = int(np.argmax(QB[i]))
        QA[i][0] += alpha * (0 + QB[j][best_b] - QA[i][0])
        qb = QB[0] + QB[1] if double else QB[0]
        b = int(rng.integers(10)) if rng.random() < eps else int(np.argmax(qb))
        r = rng.normal(-0.1, 1.0)
        k = int(rng.integers(2)) if double else 0
        QB[k][b] += alpha * (r - QB[k][b])
    return np.array(lefts)

for double in [False, True]:
    lefts = np.mean([run(double, seed=s) for s in range(100)], axis=0)
    name = "Double Q learning" if double else "Q learning"
    print(name.ljust(18), " share of episodes going left at episodes 10, 50, 300:", lefts[9].round(2), lefts[49].round(2), lefts[299].round(2))
print("the best possible share is 0.05 (only the random epsilon moves go left)")
''', long=True)

K.lesson('idea', 'From prediction to control: action values and SARSA', f'''
{src('Sutton and Barto (2018) sections 5.3, 5.4 and 6.4, and Rummery and Niranjan (1994).')}
{viz('mlqstep')}
{wwh('To choose actions without a model, learn <b>action values</b> Q(s, a) instead of state values, because picking argmax<sub>a</sub> Q(s, a) needs no knowledge of where actions lead. <b>SARSA</b> is TD control: after each step it updates Q(s, a) towards r + &gamma;Q(s&prime;, a&prime;), where a&prime; is the next action the agent actually takes. Its name lists what one update uses: S, A, R, S&prime;, A&prime;.',
     'With state values alone, the agent would need the model to look one step ahead. Action values carry that information directly. SARSA learns while acting, keeps exploring with &epsilon; greedy, and slowly improves its own policy, which is generalised policy iteration with samples.',
     'Initialise Q to 0. Choose a from s &epsilon; greedily. Each step: take a, observe r and s&prime;, choose a&prime; from s&prime; &epsilon; greedily, update Q(s, a) += &alpha;[r + &gamma;Q(s&prime;, a&prime;) &minus; Q(s, a)], then move on with s &larr; s&prime; and a &larr; a&prime;. Use Q = 0 for terminal states.')}
{run('sarsa_cliff')}
{note('On the cliff walk SARSA earns an average of &minus;24.42 per episode over its last 100 episodes while still exploring with &epsilon; = 0.1. Its greedy path climbs to the top row before heading right. The path is longer than needed, but a random step there costs one move, not a fall of &minus;100.', 'exam')}
{fxs(fx('SARSA update', 'Q(S, A) &larr; Q(S, A) + &alpha;[R + &gamma;Q(S&prime;, A&prime;) &minus; Q(S, A)]', 'A&prime; is the action actually taken next.', key=True),
     fx('&epsilon; greedy', '&pi;(a|s) = 1 &minus; &epsilon; + &epsilon;/|A| for the greedy a, and &epsilon;/|A| for others', 'Keeps exploring.', key=True))}
''', kw=['TD control', 'action values', 'SARSA', 'on policy', 'epsilon greedy', 'generalised policy iteration'])

K.lesson('q', 'Q learning: learning the best policy while exploring', f'''
{src('Watkins (1989), Watkins and Dayan, Q-learning (1992), and Sutton and Barto (2018) section 6.5.')}
{viz('mlcliff')}
{wwh('<b>Q learning</b> updates towards r + &gamma; max<sub>a&prime;</sub> Q(s&prime;, a&prime;): the value of the best next action, whatever action the agent takes next. It is <b>off policy</b>: it learns the optimal greedy policy (the <b>target policy</b>) while following an exploring policy (the <b>behaviour policy</b>).',
     'It is the most famous RL algorithm and the basis of DQN. It converges to q* in a table as long as every state and action keeps being tried and the step sizes shrink suitably, no matter how the agent explores. That freedom lets it learn from old data, from other agents or from humans.',
     'Same loop as SARSA, but the target uses the max over next actions, so the next action does not need to be chosen before the update. Act &epsilon; greedily, update with the max, and act greedily once training is done.')}
{run('q_learning_cliff')}
{note('Q learning finds the truly shortest path, straight along the cliff edge (13 moves, reward &minus;13). Yet while it still explores, its average reward is only &minus;70.01, far worse than SARSA’s, because &epsilon; greedy steps near the edge keep sending it over the cliff. Q learning values the policy it would follow without exploring, SARSA values the policy it really follows.', 'exam')}
{fxs(fx('Q learning update', 'Q(S, A) &larr; Q(S, A) + &alpha;[R + &gamma; max<sub>a</sub> Q(S&prime;, a) &minus; Q(S, A)]', 'The sample version of the Bellman optimality equation.', key=True))}
''', kw=['Q learning', 'off policy', 'target policy', 'behaviour policy', 'cliff walking', 'Watkins'])

K.lesson('expected', 'Expected SARSA, and comparing the three', f'''
{src('van Seijen, van Hasselt, Whiteson and Wiering, A Theoretical and Empirical Analysis of Expected Sarsa (2009).')}
{wwh('<b>Expected SARSA</b> replaces the sampled next action with the average over what the policy might do: target r + &gamma; &Sigma;<sub>a&prime;</sub> &pi;(a&prime;|s&prime;) Q(s&prime;, a&prime;). With a greedy target policy it becomes Q learning, and with the behaviour policy it is an on policy method like SARSA, but with less noise.',
     'Removing the randomness of the next action lowers the variance of every update, so expected SARSA can use larger step sizes and usually learns faster and more stably than SARSA, at a little more computation per step.',
     'Compute the &epsilon; greedy probabilities of the next state’s actions, take the probability weighted average of their Q values, and use it in the target.')}
{run('compare_control')}
{note('Averaged over 5 runs, the reward per episode while learning (last 100 of 200 episodes) is &minus;49.2 for Q learning, &minus;34.6 for SARSA and &minus;21.1 for expected SARSA. Expected SARSA learns the safe route like SARSA, with steadier updates. Results vary from run to run, so real comparisons average many seeds.', 'exam')}
{table(['Method', 'Target', 'Policy learned', 'On the cliff'], [
    ['SARSA', 'r + &gamma;Q(s&prime;, a&prime;), a&prime; sampled', 'The exploring policy (on policy)', 'Safe path, good reward while learning'],
    ['Expected SARSA', 'r + &gamma; &Sigma; &pi;(a&prime;|s&prime;)Q(s&prime;, a&prime;)', 'The exploring policy, less noise', 'Safe path, best reward while learning'],
    ['Q learning', 'r + &gamma; max Q(s&prime;, a&prime;)', 'The greedy policy (off policy)', 'Optimal edge path, worse reward while learning']])}
''', kw=['expected SARSA', 'variance reduction', 'on policy vs off policy', 'cliff walking comparison'])

K.lesson('bias', 'Maximisation bias and double Q learning', f'''
{src('van Hasselt, Double Q-learning (NeurIPS 2010), and Sutton and Barto (2018) section 6.7, example 6.7.')}
{wwh('Taking the max of noisy estimates overestimates the max of the true values: if all true values are 0, some estimates will be above 0 by chance, and the max picks them. This <b>maximisation bias</b> makes Q learning favour actions whose values are merely uncertain. <b>Double Q learning</b> keeps two tables: one chooses the best next action, the other estimates its value.',
     'Overestimation can steer an agent towards bad but noisy options and slow learning a lot. The double estimator removes the bias, and the same idea in Double DQN improved Atari results substantially.',
     'Keep Q<sub>1</sub> and Q<sub>2</sub>. Each step, flip a coin and update one of them, say Q<sub>1</sub>, with the target r + &gamma;Q<sub>2</sub>(s&prime;, argmax<sub>a</sub> Q<sub>1</sub>(s&prime;, a)). Act &epsilon; greedily on Q<sub>1</sub> + Q<sub>2</sub>.')}
{run('double_q')}
{note('In state A, going left leads to B, where every action pays &minus;0.1 on average with a lot of noise, so left is a mistake. Plain Q learning still goes left in 86% of episodes at episode 10 and 16% at episode 300, because the max over B’s noisy estimates looks positive. Double Q learning goes left only 40% of the time at episode 10 and settles at the best possible 5% (the random &epsilon; moves) by episode 50.', 'exam')}
{fxs(fx('Bias of the max', 'E[max<sub>a</sub> Q&#770;(a)] &ge; max<sub>a</sub> E[Q&#770;(a)]', 'Jensen’s inequality: max is convex.', key=True),
     fx('Double Q target', 'r + &gamma; Q<sub>2</sub>(s&prime;, argmax<sub>a</sub> Q<sub>1</sub>(s&prime;, a))', 'Select with one table, evaluate with the other.', key=True),
     fx('Two noisy zeros', 'E[max(X<sub>1</sub>, X<sub>2</sub>)] = 1/&radic;&pi; &asymp; 0.564 for X<sub>i</sub> ~ N(0, 1)', 'Although both true values are 0.'))}
''', kw=['maximisation bias', 'overestimation', 'double Q learning', 'double estimator', 'Jensen inequality'])

K.lesson('versus', 'TD control methods compared', f'''
{versus('Four ways to learn Q', ['', 'Monte Carlo control', 'SARSA', 'Expected SARSA', 'Q learning'], [
    ['Target', 'Full return G', 'r + &gamma;Q(s&prime;, a&prime;)', 'r + &gamma;E<sub>&pi;</sub>[Q(s&prime;, &middot;)]', 'r + &gamma; max Q(s&prime;, &middot;)'],
    ['On or off policy', 'On (or off with importance sampling)', 'On', 'Either', 'Off'],
    ['Learns', 'v of the exploring policy', 'q of the exploring policy', 'q of the target policy', 'q*'],
    ['Variance', 'High', 'Medium', 'Low', 'Low'],
    ['Risk', 'Slow', 'None special', 'More computation', 'Maximisation bias, unsafe exploration']],
    'use Q learning (or double Q learning) to learn the best policy, especially from logged data. Use SARSA or expected SARSA when mistakes during learning are costly.')}
''', kw=['SARSA vs Q learning', 'Monte Carlo control', 'on policy vs off policy control'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('SARSA', 'Q(s, a) += &alpha;[r + &gamma;Q(s&prime;, a&prime;) &minus; Q(s, a)]', 'On policy TD control.', key=True),
     fx('Q learning', 'Q(s, a) += &alpha;[r + &gamma; max<sub>a&prime;</sub> Q(s&prime;, a&prime;) &minus; Q(s, a)]', 'Off policy TD control.', key=True),
     fx('Expected SARSA', 'Q(s, a) += &alpha;[r + &gamma; &Sigma;<sub>a&prime;</sub> &pi;(a&prime;|s&prime;)Q(s&prime;, a&prime;) &minus; Q(s, a)]', 'Averages out the next action.', key=True),
     fx('Double Q learning', 'Q<sub>1</sub>(s, a) += &alpha;[r + &gamma;Q<sub>2</sub>(s&prime;, argmax Q<sub>1</sub>(s&prime;, &middot;)) &minus; Q<sub>1</sub>(s, a)]', 'Swap roles at random.'),
     fx('GLIE', 'every (s, a) tried infinitely often and &epsilon;<sub>k</sub> &rarr; 0, for example &epsilon;<sub>k</sub> = 1/k', 'Greedy in the limit with infinite exploration: makes SARSA converge to q*.'),
     fx('Convergence of Q learning', '&Sigma;<sub>t</sub> &alpha;<sub>t</sub>(s, a) = &infin;, &Sigma;<sub>t</sub> &alpha;<sub>t</sub>(s, a)<sup>2</sup> &lt; &infin; for every pair', 'Watkins and Dayan (1992), tabular case.'))}
{steps('Worked example: the same transition, three targets', [
    'Q(s, a) = 2, reward 1, &gamma; = 0.9, &alpha; = 0.5. Next state values Q(s&prime;, &middot;) = 3, 1, 1, 1, and the agent will next take an action worth 1.',
    eq('Q learning: target 1 + 0.9 &times; 3 = 3.7, new Q = 2 + 0.5 &times; 1.7 = 2.85'),
    eq('SARSA: target 1 + 0.9 &times; 1 = 1.9, new Q = 2 + 0.5 &times; (&minus;0.1) = 1.95'),
    'Expected SARSA with &epsilon; = 0.2: probabilities 0.85, 0.05, 0.05, 0.05, so E[Q] = 2.55 + 0.15 = 2.7.',
    eq('Expected SARSA: target 1 + 0.9 &times; 2.7 = 3.43, new Q = 2 + 0.5 &times; 1.43 = 2.715')])}
{deep('Off policy learning with importance sampling', '<p>Monte Carlo and n step methods can also learn off policy, but their targets contain actions chosen by the behaviour policy b, not the target policy &pi;. The fix is to reweight each return by the importance sampling ratio &rho; = &Pi;<sub>k</sub> &pi;(A<sub>k</sub>|S<sub>k</sub>) / b(A<sub>k</sub>|S<sub>k</sub>) over the actions after the first. Ordinary importance sampling is unbiased but can have huge variance, while weighted importance sampling divides by the sum of the ratios and is biased but far steadier. One step Q learning avoids ratios altogether because its target already uses the target policy’s choice, the max. This is why Q learning is the natural off policy method, and why multi step off policy methods such as Retrace need careful corrections.</p>')}
''', kw=['SARSA formula', 'Q learning formula', 'expected SARSA formula', 'GLIE', 'importance sampling'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>The agent keeps a score for every action in every situation and nudges the score after each move, so good actions rise to the top.</p>',
    '<p>Implement SARSA, Q learning and expected SARSA with &epsilon; greedy exploration, and read learning curves on the cliff walk.</p>',
    '<p>Explain on policy against off policy learning, why Q learning walks the edge, maximisation bias and double Q learning, and GLIE conditions.</p>',
    '<p>Study importance sampling, Retrace and tree backup, convergence proofs for tabular Q learning, and how these ideas carry over to deep Q networks.</p>')}
{grow('Explain how an agent learns which action is best.',
      'Implement and compare TD control methods.',
      'Analyse bias, exploration and off policy learning.')}
''', kw=['beginner', 'expert', 'Retrace', 'tree backup'])

lc(2373, 'Largest Local Values in a Matrix', 'largest-local-values-in-a-matrix', 'e', 'Take the max of every 3 by 3 block', 'For each top left corner, take the largest of the nine values below and to the right. A max over a small neighbourhood is what Q learning computes over the next state’s actions.', r"""
def largest_local(grid):
    n = len(grid)
    return [[max(grid[r][c] for r in range(i, i + 3) for c in range(j, j + 3)) for j in range(n - 2)] for i in range(n - 2)]
""", [('largest_local([[9, 9, 8, 1], [5, 6, 2, 6], [8, 2, 6, 4], [6, 2, 2, 2]])', [[9, 9], [8, 6]])])
lc(62, 'Unique Paths', 'unique-paths', 'm', 'Paths to a cell = paths from above + paths from the left', 'Keep one row of counts and add the left neighbour into each cell, row after row. Counting routes on a grid shows how quickly the number of possible paths grows, which is why RL learns values instead of listing paths.', r"""
def unique_paths(m, n):
    row = [1] * n
    for _ in range(m - 1):
        for j in range(1, n):
            row[j] += row[j - 1]
    return row[-1]
""", [('unique_paths(3, 7)', 28), ('unique_paths(3, 2)', 3)])
lc(1091, 'Shortest Path in Binary Matrix', 'shortest-path-in-binary-matrix', 'm', 'Breadth first search over 8 directions', 'With equal cost moves, breadth first search finds the shortest path, visiting cells in order of distance. Q learning on a grid with &minus;1 per move learns the same distances as negative values, but from trial and error instead of a known map.', r"""
from collections import deque


def shortest_path_binary_matrix(grid):
    n = len(grid)
    if grid[0][0] or grid[n - 1][n - 1]:
        return -1
    dist = {(0, 0): 1}
    q = deque([(0, 0)])
    while q:
        r, c = q.popleft()
        if (r, c) == (n - 1, n - 1):
            return dist[(r, c)]
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and not grid[nr][nc] and (nr, nc) not in dist:
                    dist[(nr, nc)] = dist[(r, c)] + 1
                    q.append((nr, nc))
    return -1
""", [('shortest_path_binary_matrix([[0, 1], [1, 0]])', 2), ('shortest_path_binary_matrix([[0, 0, 0], [1, 1, 0], [1, 1, 0]])', 4), ('shortest_path_binary_matrix([[1, 0, 0], [1, 1, 0], [1, 1, 0]])', -1)])
lc(1926, 'Nearest Exit from Entrance in Maze', 'nearest-exit-from-entrance-in-maze', 'm', 'Breadth first search until you reach a border cell other than the entrance', 'Search outward from the entrance and stop at the first open cell on the border. A maze with exits is a gridworld: the answer is minus the optimal value of the entrance when each move costs 1.', r"""
from collections import deque


def nearest_exit(maze, entrance):
    rows, cols = len(maze), len(maze[0])
    start = tuple(entrance)
    seen = {start}
    q = deque([(start, 0)])
    while q:
        (r, c), d = q.popleft()
        if (r, c) != start and (r in (0, rows - 1) or c in (0, cols - 1)):
            return d
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == "." and (nr, nc) not in seen:
                seen.add((nr, nc))
                q.append(((nr, nc), d + 1))
    return -1
""", [('nearest_exit([["+", "+", ".", "+"], [".", ".", ".", "+"], ["+", "+", "+", "."]], [1, 2])', 1), ('nearest_exit([["+", "+", "+"], [".", ".", "."], ["+", "+", "+"]], [1, 0])', 2), ('nearest_exit([[".", "+"]], [0, 0])', -1)])
lc(1293, 'Shortest Path in a Grid with Obstacles Elimination', 'shortest-path-in-a-grid-with-obstacles-elimination', 'h', 'Add the number of eliminations left to the state', 'Position alone is not enough to decide what to do next: you also need to know how many walls you can still break. Search over (row, column, eliminations left). Choosing a state that holds everything needed for the future is exactly the Markov property from chapter 1.3.', r"""
from collections import deque


def shortest_path_elimination(grid, k):
    m, n = len(grid), len(grid[0])
    if k >= m + n - 2:
        return m + n - 2
    seen = {(0, 0, k)}
    q = deque([(0, 0, k, 0)])
    while q:
        r, c, left, d = q.popleft()
        if (r, c) == (m - 1, n - 1):
            return d
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < m and 0 <= nc < n:
                nl = left - grid[nr][nc]
                if nl >= 0 and (nr, nc, nl) not in seen:
                    seen.add((nr, nc, nl))
                    q.append((nr, nc, nl, d + 1))
    return -1
""", [('shortest_path_elimination([[0, 0, 0], [1, 1, 0], [0, 0, 0], [0, 1, 1], [0, 0, 0]], 1)', 6), ('shortest_path_elimination([[0, 1, 1], [1, 1, 1], [1, 0, 0]], 1)', -1)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Control on a grid means taking maxima over actions and finding short paths. These problems practise a max over neighbourhoods, counting grid paths, breadth first search for shortest paths and nearest exits, and enlarging the state until it is Markov. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'grid', 'breadth first search', 'shortest path', 'state design'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Control needs <b>action values</b> Q(s, a), because argmax over Q needs no model.',
    '<b>SARSA</b> (on policy) targets r + &gamma;Q(s&prime;, a&prime;) with the action really taken next. It learns safe behaviour under exploration.',
    '<b>Q learning</b> (off policy) targets r + &gamma; max Q(s&prime;, &middot;). It learns q* while exploring, walks the cliff edge, and earns less while learning.',
    '<b>Expected SARSA</b> averages over next actions: lower variance, often the best of both.',
    '<b>Maximisation bias</b>: the max of noisy estimates is too high. <b>Double Q learning</b> selects with one table and evaluates with another.',
    'Convergence needs every pair tried often (GLIE) and suitable step sizes.'],
    'Reinforcement 3.1 scales Q learning to huge state spaces with function approximation and deep Q networks.')}
{files('Three tasks: a Q learning update, the three TD control targets, and epsilon greedy probabilities.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Why learn Q(s, a) rather than V(s) for control without a model?', ['It is smaller', 'Choosing argmax<sub>a</sub> Q(s, a) needs no model of where actions lead', 'V cannot be learned', 'Q needs no rewards'], 1, 'Acting directly.', 'With V you need a model to look ahead.')
K.quiz('e', 'SARSA is named after', ['A person', 'The quintuple S, A, R, S&prime;, A&prime; used in each update', 'A game', 'A library'], 1, 'What one update uses.', 'Rummery and Niranjan (1994) introduced it.')
K.quiz('e', 'Q learning’s target uses', ['The next action actually taken', 'The best next action’s value', 'The full return', 'A random action'], 1, 'max.', 'Off policy.')
K.quiz('e', 'An off policy method learns about', ['Only the policy it follows', 'A target policy different from the behaviour policy', 'No policy', 'The reward function'], 1, 'Two policies.', 'Q learning: greedy target, exploring behaviour.')
K.quiz('m', 'On the cliff walk with &epsilon; = 0.1, Q learning’s greedy path is', ['Along the top row', 'Right along the cliff edge, the shortest route', 'Random', 'Into the cliff'], 1, 'Optimal ignoring exploration.', '13 moves.')
K.quiz('m', 'Why does SARSA earn more reward while learning on the cliff?', ['It has a model', 'Its values include the cost of its own random steps, so it keeps away from the edge', 'It never explores', 'It uses a bigger &alpha;'], 1, 'On policy.', 'It learns the value of what it really does.')
K.quiz('m', 'Expected SARSA reduces variance by', ['Using a model', 'Averaging over the next action instead of sampling it', 'Ignoring rewards', 'Using two tables'], 1, 'Expectation.', 'Σ &pi;(a&prime;|s&prime;)Q(s&prime;, a&prime;).')
K.quiz('m', 'With a greedy target policy, expected SARSA becomes', ['SARSA', 'Q learning', 'Monte Carlo', 'Value iteration'], 1, 'Expectation under greedy = max.', 'All weight on the best action.')
K.quiz('m', 'Maximisation bias means Q learning tends to', ['Underestimate values', 'Overestimate values of uncertain actions', 'Ignore actions', 'Converge faster'], 1, 'Max of noisy estimates.', 'E[max] &ge; max E.')
K.quiz('h', 'Double Q learning fixes maximisation bias by', ['Halving the reward', 'Choosing the best action with one table and evaluating it with the other', 'Using a smaller &gamma;', 'Removing exploration'], 1, 'van Hasselt (2010).', 'Independent noise in selection and evaluation.')
K.quiz('h', 'For SARSA to converge to q*, exploration must', ['Stay at &epsilon; = 0.5', 'Be GLIE: every pair tried infinitely often and &epsilon; shrinking to 0', 'Be zero from the start', 'Use only random actions'], 1, 'Greedy in the limit.', 'Then the policy becomes greedy.')
K.quiz('h', 'Q learning can learn from logged data of another agent because', ['It needs no rewards', 'Its target does not depend on which action the data’s policy takes next', 'It uses a model', 'It is on policy'], 1, 'Off policy.', 'As long as the data covers enough states and actions.')
K.quiz('x', 'In the style of a Stanford CS234 exam: for two independent N(0, 1) estimates of actions whose true values are 0, the expected max is about', ['0', '0.564', '1', '&minus;0.564'], 1, '1/&radic;&pi;.', 'Positive although both true values are 0.')
K.quiz('x', 'In the style of a Stanford CS234 exam: off policy Monte Carlo needs importance sampling but one step Q learning does not because', ['Q learning has no policy', 'Q learning’s target already uses the target policy’s choice (the max) at the next state', 'MC has no returns', 'Importance sampling is always zero'], 1, 'No behaviour actions in the target.', 'Only the first action, which is being evaluated, comes from b.')

K.calc('e', 'Q(s, a) = 2, r = 1, max Q(s&prime;, &middot;) = 3, &gamma; = 0.9, &alpha; = 0.5. New Q after a Q learning update?', '2.85', 'Q + &alpha;(target &minus; Q).', ['Target = 1 + 2.7 = 3.7.', 'Error = 1.7.', eq('2 + 0.5 &times; 1.7 = 2.85')], check=2.85)
K.calc('e', 'Same, but SARSA’s next action is worth 1. New Q?', '1.95', 'Target r + &gamma;Q(s&prime;, a&prime;).', ['Target = 1 + 0.9 = 1.9.', 'Error = &minus;0.1.', eq('2 &minus; 0.05 = 1.95')], check=1.95)
K.calc('m', 'Next values 3, 1, 1, 1 with &epsilon; = 0.2 over 4 actions. Expected SARSA target with r = 1, &gamma; = 0.9?', '3.43', 'Weighted average first.', ['Best action probability 0.8 + 0.05 = 0.85, others 0.05.', 'E[Q] = 2.55 + 0.15 = 2.7.', eq('1 + 0.9 &times; 2.7 = 3.43')], check=3.43)
K.calc('m', 'Cliff walk 4 &times; 12, start and goal at the bottom corners, &minus;1 per move. Reward of the shortest safe route along the edge?', '-13', 'Up, across, down.', ['1 move up.', '11 moves right, then 1 down.', eq('13 moves, reward &minus;13')], check=-13)
K.calc('m', 'Corridor of 5 cells, +1 for reaching cell 4, &gamma; = 0.9. Optimal Q(0, right)?', '0.729', 'Reward 3 moves after the first.', ['Q(3, right) = 1.', 'Each step back multiplies by 0.9.', eq('0.9<sup>3</sup> = 0.729')], check=0.729)
K.calc('m', '&epsilon; = 0.1 with 4 actions. Chance one step on the edge path is a random move straight down into the cliff?', '0.025', '&epsilon; / |A|.', ['Random move with chance 0.1.', 'It is down with chance 1/4.', eq('0.1 / 4 = 0.025')], check=0.025)
K.calc('h', 'Walking 11 steps along the cliff edge with a 0.025 chance of falling at each step. Chance of at least one fall?', '0.243', '1 &minus; (1 &minus; p)<sup>11</sup>.', ['0.975<sup>11</sup> = 0.757.', 'Complement.', eq('1 &minus; 0.757 = 0.243')], check=0.2431, tol=0.002)
K.calc('h', 'Expected max of two independent standard normal estimates whose true values are 0?', '0.564', '1/&radic;&pi;.', ['&radic;&pi; = 1.7725.', 'Invert it.', eq('0.564')], check=0.5642, tol=0.002)
K.calc('h', 'How many entries does the Q table of the 4 &times; 12 cliff walk have with 4 actions?', '192', 'States times actions.', ['48 cells.', '4 actions each.', eq('48 &times; 4 = 192')], check=192)
K.calc('x', 'In the style of a Stanford CS234 problem: GLIE schedule &epsilon;<sub>k</sub> = 1/k with 4 actions. Chance the greedy action is chosen in episode 100?', '0.9925', '1 &minus; &epsilon; + &epsilon;/|A|.', ['&epsilon; = 0.01.', '&epsilon;/4 = 0.0025.', eq('0.99 + 0.0025 = 0.9925')], check=0.9925)

K.assign('q_update', 'e', 'A Q learning update',
         '<p>Write <code>q_update(Q, s, a, r, s2, done, alpha, gamma)</code>. Q is a dictionary from state to a list of action values. Return the new Q[s][a] after one Q learning update, rounded to 4 decimals. If done is True the next value is 0.</p>',
         """
def q_update(Q, s, a, r, s2, done, alpha, gamma):
    # your code here
    pass
""", [('q_update({"s": [2.0, 0.0], "t": [3.0, 1.0, 1.0]}, "s", 0, 1, "t", False, 0.5, 0.9)', 2.85), ('q_update({"s": [2.0, 0.0]}, "s", 1, 5, "end", True, 0.1, 0.9)', 0.5)],
         """
def q_update(Q, s, a, r, s2, done, alpha, gamma):
    nxt = 0.0 if done else max(Q[s2])
    return round(Q[s][a] + alpha * (r + gamma * nxt - Q[s][a]), 4)
""", 'Target r + gamma max Q[s2], or just r when done.', '<p>Forgetting the done check is a classic bug: the agent then adds value after the episode has ended.</p>')
K.assign('control_target', 'm', 'Three TD control targets',
         '<p>Write <code>control_target(method, q_next, a_next, r, eps, gamma)</code>. q_next is the list of next state action values and a_next the next action the agent will take. method is "q", "sarsa" or "expected". For "expected" use &epsilon; greedy probabilities: &epsilon;/n for every action plus 1 &minus; &epsilon; for the first best action. Return the target rounded to 4 decimals.</p>',
         """
def control_target(method, q_next, a_next, r, eps, gamma):
    # your code here
    pass
""", [('control_target("q", [3, 1, 1, 1], 1, 1, 0.2, 0.9)', 3.7), ('control_target("sarsa", [3, 1, 1, 1], 1, 1, 0.2, 0.9)', 1.9), ('control_target("expected", [3, 1, 1, 1], 1, 1, 0.2, 0.9)', 3.43)],
         """
def control_target(method, q_next, a_next, r, eps, gamma):
    if method == "q":
        nxt = max(q_next)
    elif method == "sarsa":
        nxt = q_next[a_next]
    else:
        n = len(q_next)
        best = q_next.index(max(q_next))
        nxt = sum((eps / n + (1 - eps if i == best else 0)) * v for i, v in enumerate(q_next))
    return round(r + gamma * nxt, 4)
""", 'Only the value of the next state differs between the three methods.', '<p>The three tests use the same transition as the worked example: 3.7, 1.9 and 3.43.</p>')
K.assign('eps_greedy_probs', 'm', 'Epsilon greedy probabilities',
         '<p>Write <code>eps_greedy_probs(q, eps)</code> that returns the probability of each action under &epsilon; greedy: every action gets &epsilon;/n, and the 1 &minus; &epsilon; greedy share is split equally between all actions tied for the best value. Round each to 4 decimals.</p>',
         """
def eps_greedy_probs(q, eps):
    # your code here
    pass
""", [('eps_greedy_probs([3, 1, 1, 1], 0.2)', [0.85, 0.05, 0.05, 0.05]), ('eps_greedy_probs([2, 2, 0], 0.3)', [0.45, 0.45, 0.1]), ('eps_greedy_probs([5, 1], 0.0)', [1.0, 0.0])],
         """
def eps_greedy_probs(q, eps):
    n = len(q)
    best = max(q)
    ties = [i for i, v in enumerate(q) if v == best]
    return [round(eps / n + ((1 - eps) / len(ties) if i in ties else 0), 4) for i in range(n)]
""", 'Give everyone eps / n, then share 1 &minus; eps among the tied best actions.', '<p>Splitting ties evenly avoids always favouring the first action, which can bias exploration early on when every value is 0.</p>')

K.must('Action values', 'Learn Q(s, a), act with argmax. No model needed. Explore with &epsilon; greedy.')
K.must('SARSA', 'Target r + &gamma;Q(s&prime;, a&prime;), a&prime; actually taken. On policy, safe under exploration.')
K.must('Q learning', 'Target r + &gamma; max Q(s&prime;, &middot;). Off policy, learns q*. Cliff: edge path, worse reward while learning.')
K.must('Expected SARSA', 'Target r + &gamma; &Sigma; &pi; Q. Lower variance. Greedy &pi; gives Q learning.')
K.must('Double Q', 'Max of noisy estimates is biased up. Select with Q<sub>1</sub>, evaluate with Q<sub>2</sub>.')
K.must('Convergence', 'GLIE exploration, Robbins Monro step sizes, every pair visited. Tabular only. Deep versions need more care.')

T = K.topic(
    slug='ml-qlearning', topic='ml-qlearning', step=(2, 'Solving MDPs', 'ml-r2', 'Find good policies: plan with a known model by dynamic programming, then learn from experience with Monte Carlo, temporal difference learning, SARSA and Q learning.', 'Advanced'),
    title='SARSA and Q learning', short='SARSA and Q learning', badge='2.3', minutes=50,
    lead='Learn to act without a model: action values, SARSA on policy control, Q learning off policy control on the cliff walk, expected SARSA, maximisation bias and double Q learning.',
    desc='TD control, action values, SARSA, Q learning, expected SARSA, on policy, off policy, target policy, behaviour policy, epsilon greedy, cliff walking, maximisation bias, double Q learning, GLIE, importance sampling.',
    summary='SARSA, Q learning and expected SARSA on the cliff walk, on and off policy learning, and double Q learning.',
    keywords=['Q learning', 'SARSA', 'expected SARSA', 'double Q learning', 'cliff walking', 'off policy', 'on policy', 'epsilon greedy', 'maximisation bias', 'action values'],
    recap='<p>Learn Q(s, a) from experience. SARSA learns the policy it follows, Q learning learns the best policy while exploring, expected SARSA lowers variance, and double Q learning removes the overestimate of the max.</p>',
    added='2026-11-13', leet=leet_items())
