# Reinforcement 3.1: function approximation and deep Q networks. Checked against Sutton and Barto, Reinforcement
# Learning: An Introduction (2nd edition, 2018) chapters 9 to 11 (example 9.1 the 1000 state random walk, example 10.1
# mountain car, section 11.2 Baird's counterexample, section 11.3 the deadly triad), Mnih and colleagues, Human-level
# control through deep reinforcement learning (Nature 2015), van Hasselt, Guez and Silver, Deep Reinforcement Learning
# with Double Q-learning (AAAI 2016), Wang and colleagues, Dueling Network Architectures (ICML 2016), Schaul and
# colleagues, Prioritized Experience Replay (ICLR 2016), and Hessel and colleagues, Rainbow (AAAI 2018).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-dqn')
K = Kit()

K.code('state_aggregation', r'''
import numpy as np

# Sutton and Barto example 9.1: a random walk over 1000 states, starting in the middle (state 500).
# Each step jumps 1 to 100 states left or right at random. Falling off the left end gives -1, the right end +1.
# A table would need 1000 numbers. State aggregation uses only 10: one shared value per group of 100 states.
N, JUMP, GROUPS = 1000, 100, 10

def true_values():
    v = np.zeros(N)
    for _ in range(5000):                                 # dynamic programming, as in chapter 2.1, done with whole arrays
        padded = np.concatenate([-np.ones(JUMP), v, np.ones(JUMP)])   # jumping past an end counts as that end
        c = np.concatenate([[0], np.cumsum(padded)])
        idx = np.arange(N) + JUMP
        left = c[idx] - c[idx - JUMP]                     # sum of the 100 values just to the left
        right = c[idx + JUMP + 1] - c[idx + 1]            # sum of the 100 values just to the right
        new = (left + right) / (2 * JUMP)
        if np.abs(new - v).max() < 1e-7:
            break
        v = new
    return v

def episode(rng):
    s, states = 500, []
    while 1 <= s <= N:
        states.append(s)
        s += int(rng.integers(1, JUMP + 1)) * (1 if rng.random() < 0.5 else -1)
    return states, (1 if s > N else -1)

def group(s):
    return (s - 1) * GROUPS // N                          # states 1..100 share group 0, and so on

def gradient_mc(episodes, rng):
    w, visits = np.zeros(GROUPS), np.zeros(GROUPS)
    for _ in range(episodes):
        states, G = episode(rng)                          # no discount, reward only at the end, so G is the same for every state
        for s in states:
            g = group(s)
            visits[g] += 1
            w[g] += (G - w[g]) / visits[g]                # step size 1/n: the gradient of a one hot feature is 1 for its own group
    return w

def semi_gradient_td(episodes, alpha, rng):
    w = np.zeros(GROUPS)
    for _ in range(episodes):
        states, G = episode(rng)
        for i, s in enumerate(states):
            target = w[group(states[i + 1])] if i + 1 < len(states) else G
            w[group(s)] += alpha * (target - w[group(s)])  # the target uses w itself, but we do not differentiate it
    return w

v = true_values()
rng = np.random.default_rng(0)
w_mc = gradient_mc(2000, rng)
w_td = semi_gradient_td(2000, 0.01, rng)
truth = [v[g * 100:(g + 1) * 100].mean() for g in range(GROUPS)]
print("group   true average   gradient MC   semi gradient TD")
for g in range(GROUPS):
    print(f"{g * 100 + 1:4d}-{(g + 1) * 100:<4d}   {truth[g]:9.3f}   {w_mc[g]:11.3f}   {w_td[g]:14.3f}")
err = lambda w: np.sqrt(np.mean((np.repeat(w, 100) - v) ** 2))
print("root mean squared error over all 1000 states: MC", round(err(w_mc), 3), " TD", round(err(w_td), 3))
print("10 weights stand in for 1000 values. The values inside a group are forced to be equal, so some error always remains.")
''', long=True)

K.code('mountain_car_tiles', r'''
import numpy as np

# Sutton and Barto example 10.1: an underpowered car must reach the top of a hill (position 0.5).
# State: position in [-1.2, 0.5] and velocity in [-0.07, 0.07], both continuous, so no table can list every state.
# Actions: push left, do nothing, push right. Every step costs -1 until the car reaches the top.
def step(pos, vel, a):
    vel = np.clip(vel + 0.001 * (a - 1) - 0.0025 * np.cos(3 * pos), -0.07, 0.07)
    pos = pos + vel
    if pos < -1.2:
        pos, vel = -1.2, 0.0                              # hitting the left wall stops the car
    return pos, vel, pos >= 0.5

# Tile coding: 8 grids of 8 by 8 tiles, each shifted a little. A state switches on exactly one tile in each grid.
TILINGS, SIZE = 8, 8

def active_tiles(pos, vel):
    x = (pos + 1.2) / 1.7 * SIZE                         # scale both numbers to the range 0..8
    y = (vel + 0.07) / 0.14 * SIZE
    tiles = []
    for t in range(TILINGS):
        dx, dy = t / TILINGS, (3 * t / TILINGS) % 1       # grid t is shifted by a different fraction of a tile in each direction
        i, j = int(x + dx), int(y + dy)                   # 0..8, so each grid has 9 by 9 tiles to cover the shift
        tiles.append(t * (SIZE + 1) ** 2 + i * (SIZE + 1) + j)
    return tiles

w = np.zeros((3, TILINGS * (SIZE + 1) ** 2))              # one weight vector per action
q = lambda tiles: w[:, tiles].sum(axis=1)                 # Q(s, a) = sum of the weights of the active tiles
alpha, gamma = 0.5 / TILINGS, 1.0
rng = np.random.default_rng(0)
lengths = []
for ep in range(60):
    pos, vel = rng.uniform(-0.6, -0.4), 0.0
    tiles = active_tiles(pos, vel)
    a = int(np.argmax(q(tiles)))                         # greedy: starting all weights at 0 is optimistic, so it explores
    for t in range(1, 5001):
        pos, vel, done = step(pos, vel, a)
        if done:
            w[a, tiles] += alpha * (-1 - q(tiles)[a])     # semi gradient SARSA, terminal target is just the reward
            break
        tiles2 = active_tiles(pos, vel)
        a2 = int(np.argmax(q(tiles2)))
        target = -1 + gamma * q(tiles2)[a2]
        w[a, tiles] += alpha * (target - q(tiles)[a])     # the gradient is 1 for each active tile, 0 elsewhere
        tiles, a = tiles2, a2
    lengths.append(t)
print("steps to reach the top in episodes 1 to 10:", lengths[:10])
print("average steps in episodes 51 to 60:", np.mean(lengths[50:]).round(1))
print("weights:", w.size, " active tiles per state:", TILINGS)
''', long=True)

K.code('dqn_cartpole', r'''
import numpy as np

# CartPole: keep a pole balanced on a cart by pushing left or right. +1 reward per step, at most 200 steps.
# The physics follows the classic Barto, Sutton and Anderson (1983) task used by OpenAI Gym.
def cart_step(s, a):
    x, v, th, om = s
    force = 10.0 if a == 1 else -10.0
    cos, sin = np.cos(th), np.sin(th)
    tmp = (force + 0.05 * om * om * sin) / 1.1
    alpha = (9.8 * sin - cos * tmp) / (0.5 * (4 / 3 - 0.1 * cos * cos / 1.1))
    acc = tmp - 0.05 * alpha * cos / 1.1
    s = np.array([x + 0.02 * v, v + 0.02 * acc, th + 0.02 * om, om + 0.02 * alpha])
    return s, abs(s[0]) > 2.4 or abs(s[2]) > 0.2095     # fails if the cart leaves the track or the pole tilts past 12 degrees

# A small network: 4 inputs, 32 hidden units with ReLU, 2 outputs (one Q value per action).
def init(rng):
    return [rng.normal(0, 0.5, (4, 32)), np.zeros(32), rng.normal(0, 0.1, (32, 2)), np.zeros(2)]

SCALE = np.array([2.4, 3.0, 0.21, 3.0])                  # bring every input to roughly -1..1

def forward(p, X):
    h = np.maximum(0, (X / SCALE) @ p[0] + p[1])
    return h @ p[2] + p[3], h

def train_step(p, X, A, Y, lr, opt):
    q, h = forward(p, X)
    err = np.zeros_like(q)
    rows = np.arange(len(A))
    err[rows, A] = q[rows, A] - Y                         # only the action taken has a target
    err = np.clip(err, -1, 1) / len(A)                   # clipping the error is the Huber loss trick from DQN
    dh = (err @ p[2].T) * (h > 0)
    grads = [(X / SCALE).T @ dh, dh.sum(0), h.T @ err, err.sum(0)]
    opt["t"] += 1
    for k, (w, g) in enumerate(zip(p, grads)):           # Adam: a step size for each weight, from running averages of the gradient
        opt["m"][k] = 0.9 * opt["m"][k] + 0.1 * g
        opt["v"][k] = 0.999 * opt["v"][k] + 0.001 * g * g
        m_hat = opt["m"][k] / (1 - 0.9 ** opt["t"])
        v_hat = opt["v"][k] / (1 - 0.999 ** opt["t"])
        w -= lr * m_hat / (np.sqrt(v_hat) + 1e-8)

rng = np.random.default_rng(1)
online = init(rng)
opt = {"t": 0, "m": [np.zeros_like(w) for w in online], "v": [np.zeros_like(w) for w in online]}
target = [w.copy() for w in online]                       # the target network: a frozen copy, refreshed every 100 steps
buffer, CAP = [], 10000                                   # experience replay memory
gamma, lr, batch = 0.95, 0.003, 32
returns, steps = [], 0
for ep in range(150):
    s, total, done = rng.uniform(-0.05, 0.05, 4), 0, False
    while not done and total < 200:
        eps = max(0.05, 1 - ep / 60)                     # explore a lot at first, then less
        a = int(rng.integers(2)) if rng.random() < eps else int(np.argmax(forward(online, s[None])[0]))
        s2, done = cart_step(s, a)
        total += 1
        buffer.append((s, a, 1.0, s2, float(done)))
        if len(buffer) > CAP:
            buffer.pop(0)
        s = s2
        steps += 1
        if len(buffer) >= 200:
            idx = rng.integers(len(buffer), size=batch)   # a random minibatch breaks the link between neighbouring steps
            S, A, R, S2, D = (np.array(x) for x in zip(*[buffer[i] for i in idx]))
            Y = R + gamma * (1 - D) * forward(target, S2)[0].max(axis=1)
            train_step(online, S, A.astype(int), Y, lr, opt)
        if steps % 100 == 0:
            target = [w.copy() for w in online]
    returns.append(total)
for k in range(0, 150, 25):
    print(f"episodes {k + 1:3d} to {k + 25:3d}: average steps balanced {np.mean(returns[k:k + 25]):6.1f}")
print("total environment steps:", steps)

tests = []
for _ in range(10):                                       # test the greedy policy, with no exploring and no learning
    s, total, done = rng.uniform(-0.05, 0.05, 4), 0, False
    while not done and total < 200:
        s, done = cart_step(s, int(np.argmax(forward(online, s[None])[0])))
        total += 1
    tests.append(total)
print("greedy test episodes (200 is the maximum):", tests)
''', long=True)

K.code('baird_divergence', r'''
import numpy as np

# Baird's counterexample (1995), Sutton and Barto section 11.2. 7 states, every reward is 0, so the true values are all 0.
# Behaviour policy: "dashed" (go to one of states 0..5 at random) with chance 6/7, "solid" (go to state 6) with chance 1/7.
# Target policy: always "solid". Learning about one policy from another's data is off policy learning.
X = np.zeros((7, 8))
for i in range(6):
    X[i, i], X[i, 7] = 2, 1                              # v(state i) = 2 w_i + w_7
X[6, 6], X[6, 7] = 1, 2                                  # v(state 6) = w_6 + 2 w_7

def run(features, steps=1000, alpha=0.01, gamma=0.99, seed=0):
    rng = np.random.default_rng(seed)
    w = np.ones(features.shape[1])
    if features.shape[1] == 8:
        w[6] = 10                                         # the starting weights used in the book
    s, norms = int(rng.integers(7)), []
    for t in range(steps + 1):
        if t % 200 == 0:
            norms.append(round(float(np.linalg.norm(w)), 2))
        solid = rng.random() < 1 / 7
        s2 = 6 if solid else int(rng.integers(6))
        rho = 7.0 if solid else 0.0                       # importance ratio pi / b: 1 / (1/7) for solid, 0 / (6/7) for dashed
        delta = 0 + gamma * features[s2] @ w - features[s] @ w
        w += alpha * rho * delta * features[s]            # semi gradient off policy TD(0)
        s = s2
    return norms

print("size of w at steps 0, 200, ..., 1000")
print("linear features, 8 weights :", run(X))
print("a table, 7 separate values :", run(np.eye(7)))
print("All three of function approximation, bootstrapping and off policy data together make the weights blow up.")
''', long=True)

K.lesson('idea', 'Why tables break, and learning a value function', f'''
{src('Sutton and Barto (2018) sections 9.1 to 9.4 and example 9.1.')}
{viz('mlaggregate')}
{wwh('<b>Value function approximation</b> replaces the table with a function v&#770;(s, <b>w</b>) that has far fewer weights than there are states. Learning means adjusting <b>w</b> so that v&#770; matches the true values on the states the agent visits. Changing one weight changes the values of many states at once, which is called <b>generalisation</b>.',
     'Backgammon has about 10<sup>20</sup> states, Go about 10<sup>170</sup>, and a robot with continuous sensors has infinitely many. No table can hold them, and most states are never seen twice. A function that generalises lets experience in one state improve the estimate in similar states.',
     'Pick features and a model, then use stochastic gradient descent on the squared error. <b>Gradient Monte Carlo</b> moves <b>w</b> towards the return G<sub>t</sub>. <b>Semi gradient TD(0)</b> moves it towards r + &gamma;v&#770;(s&prime;, <b>w</b>) and treats that target as a fixed number when taking the gradient, which is why it is only a semi gradient.')}
{run('state_aggregation')}
{note('With 10 groups of 100 states, 10 weights stand in for 1000 values. After 2000 episodes gradient Monte Carlo reaches a root mean squared error of 0.058, close to the best any staircase can do. Semi gradient TD reaches 0.11 because its target leans on the next group’s weight, which is itself only an average. Its steps near the two ends stay closer to 0.', 'exam')}
{fxs(fx('Prediction objective', 'VE(<b>w</b>) = &Sigma;<sub>s</sub> &mu;(s) [v<sub>&pi;</sub>(s) &minus; v&#770;(s, <b>w</b>)]<sup>2</sup>', '&mu;(s) is the share of time spent in s.', key=True),
     fx('Gradient Monte Carlo', '<b>w</b> &larr; <b>w</b> + &alpha;[G<sub>t</sub> &minus; v&#770;(S<sub>t</sub>, <b>w</b>)] &nabla;v&#770;(S<sub>t</sub>, <b>w</b>)', 'Unbiased target, converges to a local minimum of VE.', key=True),
     fx('Semi gradient TD(0)', '<b>w</b> &larr; <b>w</b> + &alpha;[R + &gamma;v&#770;(S&prime;, <b>w</b>) &minus; v&#770;(S, <b>w</b>)] &nabla;v&#770;(S, <b>w</b>)', 'The target also depends on <b>w</b>, but we ignore that in the gradient.', key=True))}
{link('ai', 'Seen function approximation in the Artificial Intelligence subject?', 'The AI subject introduces function approximation with features and deep Q networks from the Russell and Norvig point of view. This chapter adds more maths, tile coding, working code and why approximation can diverge.', 'Open Artificial Intelligence')}
''', kw=['function approximation', 'generalisation', 'state aggregation', 'gradient Monte Carlo', 'semi gradient TD', 'value error'])

K.lesson('linear', 'Linear features and tile coding', f'''
{src('Sutton and Barto (2018) sections 9.4, 9.5, 10.1 and example 10.1, and Albus, A new approach to manipulator control: the CMAC (1975).')}
{wwh('A <b>linear</b> approximator computes v&#770;(s, <b>w</b>) = <b>w</b> &middot; <b>x</b>(s), a weighted sum of features. Its gradient is simply the feature vector <b>x</b>(s). <b>Tile coding</b> covers the state space with several grids (tilings), each shifted a little. A state switches on one tile in each grid, and its value is the sum of those tiles’ weights.',
     'Linear methods are fast, easy to analyse and, with on policy data, semi gradient TD is guaranteed to converge for them. Tile coding gives local generalisation: nearby states share most of their tiles, distant states share none. The shifts give fine resolution from coarse grids.',
     'Scale each state variable, find the active tile in every tiling, and keep one weight per tile and action. Q(s, a) is the sum of the active weights. With n tilings use a step size of about &alpha; = 0.1/n to 0.5/n, so one update moves the value by about &alpha;n of the error.')}
{run('mountain_car_tiles')}
{note('Mountain car with 8 tilings of 9 by 9 tiles and 3 actions uses 1944 weights. The first episode takes 2111 steps, because every weight starts at 0, which is optimistic when each step costs &minus;1, so the car tries everything. By episodes 51 to 60 it needs about 149 steps on average. It has learned to rock back and forth to build up speed.', 'exam')}
{table(['Features', 'How they work', 'Good for'], [
    ['State aggregation', 'One weight per group of states', 'A first try, easy to understand'],
    ['Polynomials', 'Powers and products of state variables', 'Smooth values in a few dimensions'],
    ['Fourier basis', 'Cosines of different frequencies', 'Smooth values, simple to set up'],
    ['Tile coding', 'Several shifted grids, one active tile each', 'Low dimensional control, fast updates'],
    ['Radial basis functions', 'Bumps centred at chosen points', 'Smooth local generalisation'],
    ['Neural networks', 'Features are learned, not designed', 'Images, text, high dimensional input']])}
{fxs(fx('Linear value', 'v&#770;(s, <b>w</b>) = <b>w</b><sup>T</sup><b>x</b>(s), &nbsp; &nabla;v&#770; = <b>x</b>(s)', 'The gradient is the feature vector.', key=True),
     fx('Tile coding step size', '&alpha; = 0.5 / n for n tilings', 'Each update moves the value about half way to the target.'))}
''', kw=['linear function approximation', 'tile coding', 'CMAC', 'mountain car', 'features', 'Fourier basis'])

K.lesson('dqn', 'Deep Q networks: replay memory and a target network', f'''
{src('Mnih and colleagues, Playing Atari with Deep Reinforcement Learning (2013) and Human-level control through deep reinforcement learning (Nature 2015).')}
{viz('mldqn')}
{wwh('A <b>deep Q network</b> (DQN) is Q learning with a neural network Q(s, a, &theta;) that outputs one value per action. Two ideas make it stable. <b>Experience replay</b> stores transitions in a large memory and trains on random minibatches. A <b>target network</b> is a frozen copy &theta;<sup>&minus;</sup> of the weights, used only to compute targets and refreshed every C steps.',
     'Naive Q learning with a network tends to oscillate or diverge. Consecutive steps are strongly correlated, which breaks the assumption behind stochastic gradient descent, and every update also moves the target it is chasing. Replay breaks the correlation and reuses each transition many times. The target network holds the target still for a while.',
     'Act &epsilon; greedily and push (s, a, r, s&prime;, done) into the memory. Each training step, sample a minibatch, compute y = r + &gamma; max<sub>a&prime;</sub> Q(s&prime;, a&prime;, &theta;<sup>&minus;</sup>) (just r if done), and take a gradient step on (y &minus; Q(s, a, &theta;))<sup>2</sup>, usually with the Huber loss. Copy &theta; into &theta;<sup>&minus;</sup> every C steps.')}
{run('dqn_cartpole')}
{note('This DQN is written in plain NumPy: 4 inputs, 32 hidden units and 2 outputs, Adam, a memory of 10,000 and a target copy every 100 steps. It balances the pole for about 11 to 23 steps on average in the first 75 episodes, then 58.6, 131.1 and 171.4 in later blocks of 25 episodes. Ten greedy test runs last 134 to 147 steps out of 200. Deep RL is sensitive to settings and seeds, so real work compares several seeds.', 'exam')}
{scene('The Atari result', '<p>The 2015 Nature DQN learned 49 Atari 2600 games from raw pixels and the score alone, with the same network and settings for every game. The input was the last 4 frames, shrunk to 84 by 84 grey pixels. It used a replay memory of 1,000,000 transitions, minibatches of 32, a target update every 10,000 steps, &gamma; = 0.99, &epsilon; falling from 1 to 0.1 over the first million frames, and rewards clipped to &minus;1, 0 or +1. It reached more than 75% of a professional human tester’s score on 29 of the 49 games.</p>')}
{fxs(fx('DQN loss', 'L(&theta;) = E<sub>(s, a, r, s&prime;) ~ D</sub>[(r + &gamma; max<sub>a&prime;</sub> Q(s&prime;, a&prime;, &theta;<sup>&minus;</sup>) &minus; Q(s, a, &theta;))<sup>2</sup>]', 'D is the replay memory, &theta;<sup>&minus;</sup> the target weights.', key=True),
     fx('Huber loss', 'L<sub>&delta;</sub>(e) = e<sup>2</sup>/2 if |e| &le; 1, else |e| &minus; 1/2', 'Same as clipping the error to [&minus;1, 1] in the gradient.'))}
''', kw=['DQN', 'deep Q network', 'experience replay', 'target network', 'Atari', 'Huber loss', 'CartPole'])

K.lesson('better', 'Double DQN, dueling networks, prioritised replay and Rainbow', f'''
{src('van Hasselt, Guez and Silver (AAAI 2016), Wang and colleagues (ICML 2016), Schaul and colleagues (ICLR 2016), and Hessel and colleagues, Rainbow (AAAI 2018).')}
{wwh('Many improvements followed DQN. <b>Double DQN</b> chooses the next action with the online network and evaluates it with the target network. A <b>dueling</b> network splits the output into a state value V(s) and advantages A(s, a). <b>Prioritised replay</b> samples surprising transitions, those with a large TD error, more often. <b>Rainbow</b> combines six such ideas.',
     'DQN overestimates values because of the maximisation bias from chapter 2.3, and Double DQN fixes that at no extra cost. Dueling helps when many actions have similar values, because V is learned from every update. Prioritised replay spends updates where there is most to learn. Together they made learning on Atari much faster and stronger.',
     'Double DQN: y = r + &gamma;Q(s&prime;, argmax<sub>a</sub> Q(s&prime;, a, &theta;), &theta;<sup>&minus;</sup>). Dueling: Q = V + A &minus; mean of A. Prioritised replay: sample transition i with chance p<sub>i</sub><sup>&alpha;</sup> / &Sigma; p<sub>k</sub><sup>&alpha;</sup> with p<sub>i</sub> = |&delta;<sub>i</sub>| + small constant, and correct the bias with importance weights (N P(i))<sup>&minus;&beta;</sup>.')}
{table(['Rainbow part', 'What it changes', 'Why it helps'], [
    ['Double Q learning', 'Select with online, evaluate with target', 'Removes overestimation'],
    ['Prioritised replay', 'Sample by TD error', 'Learns faster from rare, surprising events'],
    ['Dueling network', 'Q = V + A &minus; mean A', 'Better values when actions matter little'],
    ['Multi step returns', 'n step targets, n = 3', 'Rewards travel back faster'],
    ['Distributional RL (C51)', 'Learns the whole spread of returns in 51 bins', 'Richer signal, more stable learning'],
    ['Noisy nets', 'Learned noise in the weights', 'Exploration without a hand set &epsilon;']])}
{note('Hessel and colleagues found that prioritised replay and multi step returns mattered most: removing either one hurt Rainbow the most. Removing dueling or Double Q learning hurt the least on average.', 'exam')}
{fxs(fx('Double DQN target', 'y = r + &gamma;Q(s&prime;, argmax<sub>a</sub> Q(s&prime;, a, &theta;), &theta;<sup>&minus;</sup>)', 'Online network selects, target network evaluates.', key=True),
     fx('Dueling aggregation', 'Q(s, a) = V(s) + A(s, a) &minus; (1/|A|) &Sigma;<sub>a&prime;</sub> A(s, a&prime;)', 'Subtracting the mean makes V and A identifiable.', key=True),
     fx('Prioritised sampling', 'P(i) = p<sub>i</sub><sup>&alpha;</sup> / &Sigma;<sub>k</sub> p<sub>k</sub><sup>&alpha;</sup>, &nbsp; w<sub>i</sub> = (N P(i))<sup>&minus;&beta;</sup> / max<sub>j</sub> w<sub>j</sub>', '&alpha; = 0 gives uniform sampling.'))}
''', kw=['Double DQN', 'dueling network', 'prioritised experience replay', 'Rainbow', 'distributional RL', 'noisy nets', 'multi step'])

K.lesson('triad', 'The deadly triad: when approximation diverges', f'''
{src('Baird, Residual algorithms (ICML 1995), Tsitsiklis and Van Roy (1997), Sutton and Barto (2018) sections 11.2 and 11.3, and Sutton and colleagues, Fast gradient descent methods for TD learning with linear function approximation (ICML 2009).')}
{wwh('The <b>deadly triad</b> is the combination of function approximation, bootstrapping and off policy training. Any two of them are safe. All three together can make the weights grow without limit, even on a tiny problem whose true values are all 0.',
     'DQN has all three: a network, a TD target and a replay memory of old, off policy data. Knowing the triad explains why target networks, replay and careful step sizes matter, and why research on stable off policy methods is still active.',
     'Baird’s counterexample has 7 states, 8 weights and zero rewards. Semi gradient off policy TD makes the weights explode. Fixes: drop one leg of the triad (use Monte Carlo targets, on policy data or a table), slow the target down (target networks), or use true gradient methods such as gradient TD (GTD2, TDC) or emphatic TD.')}
{run('baird_divergence')}
{note('With linear features the size of the weight vector grows from 10.34 to 452.23 in 1000 steps, although every true value is 0. With a table (one value per state) and the same off policy data, it slowly shrinks, from 2.65 to 2.61. The problem is not off policy data alone, but all three parts of the triad together.', 'exam')}
{fxs(fx('Importance ratio', '&rho; = &pi;(a|s) / b(a|s)', 'Reweights off policy samples. In Baird’s example &rho; = 7 for solid and 0 for dashed.', key=True),
     fx('Linear TD fixed point', '<b>w</b><sub>TD</sub> = <b>A</b><sup>&minus;1</sup><b>b</b>, <b>A</b> = E[<b>x</b><sub>t</sub>(<b>x</b><sub>t</sub> &minus; &gamma;<b>x</b><sub>t+1</sub>)<sup>T</sup>], <b>b</b> = E[R<sub>t+1</sub><b>x</b><sub>t</sub>]', 'Stable when <b>A</b> is positive definite, which holds on policy.'),
     fx('TD error bound', 'VE(<b>w</b><sub>TD</sub>) &le; VE(best <b>w</b>) / (1 &minus; &gamma;)', 'On policy linear TD, Tsitsiklis and Van Roy (1997).'))}
''', kw=['deadly triad', 'Baird counterexample', 'divergence', 'off policy', 'gradient TD', 'emphatic TD'])

K.lesson('versus', 'Tables, linear models and deep networks compared', f'''
{versus('Three ways to store values', ['', 'Table', 'Linear features', 'Deep network'], [
    ['Parameters', 'One per state (and action)', 'One per feature', 'Thousands to millions'],
    ['Generalisation', 'None', 'Through designed features', 'Through learned features'],
    ['Convergence', 'Proven for TD and Q learning', 'Proven for on policy TD', 'No guarantee, needs tricks'],
    ['Inputs', 'Small discrete states', 'Low dimensional states', 'Pixels, text, many sensors'],
    ['Typical method', 'Q learning, SARSA', 'Semi gradient SARSA with tile coding', 'DQN, Double DQN, Rainbow']],
    'use a table when the states fit in memory, linear features for low dimensional control, and a deep network when the input is high dimensional such as images.')}
''', kw=['tabular vs linear vs deep', 'choosing a function approximator'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Value error', 'VE(<b>w</b>) = &Sigma;<sub>s</sub> &mu;(s)[v<sub>&pi;</sub>(s) &minus; v&#770;(s, <b>w</b>)]<sup>2</sup>', 'The prediction objective.', key=True),
     fx('Semi gradient TD(0)', '<b>w</b> += &alpha;&delta;&nabla;v&#770;(S, <b>w</b>), &delta; = R + &gamma;v&#770;(S&prime;, <b>w</b>) &minus; v&#770;(S, <b>w</b>)', 'Linear: &nabla;v&#770; = <b>x</b>(S).', key=True),
     fx('Semi gradient SARSA', '<b>w</b> += &alpha;[R + &gamma;q&#770;(S&prime;, A&prime;, <b>w</b>) &minus; q&#770;(S, A, <b>w</b>)]&nabla;q&#770;(S, A, <b>w</b>)', 'Control with features.', key=True),
     fx('DQN target', 'y = r + &gamma;(1 &minus; done) max<sub>a&prime;</sub> Q(s&prime;, a&prime;, &theta;<sup>&minus;</sup>)', 'Frozen target weights.', key=True),
     fx('Double DQN target', 'y = r + &gamma;Q(s&prime;, argmax<sub>a</sub> Q(s&prime;, a, &theta;), &theta;<sup>&minus;</sup>)', 'Removes most overestimation.'),
     fx('Dueling', 'Q = V + A &minus; mean(A)', 'Splits state value and advantage.'))}
{steps('Worked example: one semi gradient TD update with linear features', [
    'Features <b>x</b>(s) = [1, 2], <b>x</b>(s&prime;) = [1, 1], weights <b>w</b> = [0.5, 1.0], reward 1, &gamma; = 0.9, &alpha; = 0.1.',
    eq('v&#770;(s) = 0.5 + 2.0 = 2.5, &nbsp; v&#770;(s&prime;) = 0.5 + 1.0 = 1.5'),
    eq('&delta; = 1 + 0.9 &times; 1.5 &minus; 2.5 = &minus;0.15'),
    eq('<b>w</b> += 0.1 &times; (&minus;0.15) &times; [1, 2] = [&minus;0.015, &minus;0.03]'),
    'New weights [0.485, 0.97]. Both weights moved, so the values of every state that uses these features changed too. That is generalisation, and it is also why updates can interfere with each other.'])}
{deep('Why semi gradient, and what a true gradient would need', '<p>The squared TD error (R + &gamma;v&#770;(S&prime;, <b>w</b>) &minus; v&#770;(S, <b>w</b>))<sup>2</sup> depends on <b>w</b> through both terms. Semi gradient methods differentiate only the second term. They are faster and usually learn better, but they are not gradient descent on any objective, which is why they can diverge off policy. Differentiating both terms gives the residual gradient algorithm of Baird (1995), which is stable but slow and, with random transitions, converges to the wrong values unless two independent next states are sampled. Gradient TD methods such as GTD2 and TDC instead minimise the projected Bellman error with a second set of weights, and they converge off policy with linear features at the cost of extra parameters and a second step size.</p>')}
''', kw=['value error formula', 'semi gradient', 'DQN target formula', 'residual gradient', 'projected Bellman error'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>When there are too many situations to remember one by one, the agent learns a formula that guesses the value of a situation from its features, so similar situations get similar values.</p>',
    '<p>Implement gradient Monte Carlo and semi gradient TD with state aggregation, semi gradient SARSA with tile coding, and a small DQN with replay and a target network.</p>',
    '<p>Explain why replay and target networks stabilise DQN, the deadly triad, Double DQN, dueling networks, prioritised replay and the Rainbow ablations.</p>',
    '<p>Study the linear TD fixed point and its error bound, gradient TD and emphatic TD, distributional RL, and theory of deep RL such as the neural tangent kernel view of fitted Q iteration.</p>')}
{grow('Explain how an agent can value situations it has never seen.',
      'Build and tune approximate value methods and DQN.',
      'Analyse stability, bias and the design choices of deep RL.')}
''', kw=['beginner', 'expert', 'fitted Q iteration', 'emphatic TD'])

lc(703, 'Kth Largest Element in a Stream', 'kth-largest-element-in-a-stream', 'e', 'Keep a min heap of the k largest values', 'Push each new value and pop the smallest whenever the heap holds more than k. The top of the heap is then the kth largest. Keeping only the most important items from a stream is what prioritised replay does with surprising transitions. Our helper returns the answer after each add.', r"""
import heapq


class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.heap = []
        for x in nums:
            self.add(x)

    def add(self, val):
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        return self.heap[0]


def kth_largest_run(k, nums, adds):
    kl = KthLargest(k, nums)
    return [kl.add(v) for v in adds]
""", [('kth_largest_run(3, [4, 5, 8, 2], [3, 5, 10, 9, 4])', [4, 5, 5, 8, 8]), ('kth_largest_run(1, [], [-3, -2, -4, 0, 4])', [-3, -2, -2, 0, 4])])
lc(1046, 'Last Stone Weight', 'last-stone-weight', 'e', 'A max heap: smash the two heaviest each time', 'Python’s heapq is a min heap, so store negative weights. Pop the two largest, push back their difference if it is not zero, and repeat. Always taking the biggest first is how prioritised replay picks the transitions with the largest TD error.', r"""
import heapq


def last_stone_weight(stones):
    heap = [-s for s in stones]
    heapq.heapify(heap)
    while len(heap) > 1:
        a = -heapq.heappop(heap)
        b = -heapq.heappop(heap)
        if a != b:
            heapq.heappush(heap, -(a - b))
    return -heap[0] if heap else 0
""", [('last_stone_weight([2, 7, 4, 1, 8, 1])', 1), ('last_stone_weight([1])', 1), ('last_stone_weight([3, 3])', 0)])
lc(622, 'Design Circular Queue', 'design-circular-queue', 'm', 'A fixed array with a head index and a count', 'Store items in a list of fixed size. The next free slot is (head + count) mod size. This ring buffer is exactly how a DQN replay memory is stored: when it is full, the newest transition overwrites the oldest. Our helper runs a list of operations.', r"""
class MyCircularQueue:
    def __init__(self, k):
        self.data = [0] * k
        self.head = 0
        self.count = 0

    def enQueue(self, value):
        if self.isFull():
            return False
        self.data[(self.head + self.count) % len(self.data)] = value
        self.count += 1
        return True

    def deQueue(self):
        if self.isEmpty():
            return False
        self.head = (self.head + 1) % len(self.data)
        self.count -= 1
        return True

    def Front(self):
        return -1 if self.isEmpty() else self.data[self.head]

    def Rear(self):
        return -1 if self.isEmpty() else self.data[(self.head + self.count - 1) % len(self.data)]

    def isEmpty(self):
        return self.count == 0

    def isFull(self):
        return self.count == len(self.data)


def circular_run(k, ops):
    q, out = MyCircularQueue(k), []
    for op in ops:
        out.append(getattr(q, op[0])(*op[1:]))
    return out
""", [('circular_run(3, [("enQueue", 1), ("enQueue", 2), ("enQueue", 3), ("enQueue", 4), ("Rear",), ("isFull",), ("deQueue",), ("enQueue", 4), ("Rear",)])', [True, True, True, False, 3, True, True, True, 4])])
lc(146, 'LRU Cache', 'lru-cache', 'm', 'An ordered dictionary: move used keys to the end, evict from the front', 'OrderedDict keeps keys in order of use. On get or put move the key to the end, and when the cache is too big remove the first key, the least recently used. Choosing what to forget when memory is full is the same question a replay memory answers, and DQN simply forgets the oldest. Our helper runs a list of operations and returns the results of get.', r"""
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.store = OrderedDict()

    def get(self, key):
        if key not in self.store:
            return -1
        self.store.move_to_end(key)
        return self.store[key]

    def put(self, key, value):
        self.store[key] = value
        self.store.move_to_end(key)
        if len(self.store) > self.capacity:
            self.store.popitem(last=False)


def lru_run(capacity, ops):
    cache, out = LRUCache(capacity), []
    for op in ops:
        if op[0] == "get":
            out.append(cache.get(op[1]))
        else:
            cache.put(op[1], op[2])
    return out
""", [('lru_run(2, [("put", 1, 1), ("put", 2, 2), ("get", 1), ("put", 3, 3), ("get", 2), ("put", 4, 4), ("get", 1), ("get", 3), ("get", 4)])', [1, -1, -1, 3, 4])])
lc(480, 'Sliding Window Median', 'sliding-window-median', 'h', 'Keep the window sorted and insert and remove with binary search', 'Hold the current window in a sorted list. Use bisect to insert the new value and remove the one leaving, then read the middle. Medians of recent results are a robust way to report RL progress, because single episodes can be wildly high or low.', r"""
import bisect


def median_sliding_window(nums, k):
    window = sorted(nums[:k])
    out = []
    for i in range(k, len(nums) + 1):
        if k % 2:
            out.append(float(window[k // 2]))
        else:
            out.append((window[k // 2 - 1] + window[k // 2]) / 2)
        if i == len(nums):
            break
        window.pop(bisect.bisect_left(window, nums[i - k]))
        bisect.insort(window, nums[i])
    return out
""", [('median_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)', [1.0, -1.0, -1.0, 3.0, 5.0, 6.0]), ('median_sliding_window([1, 2, 3, 4, 2, 3, 1, 4, 2], 3)', [2.0, 3.0, 3.0, 3.0, 2.0, 3.0, 2.0]), ('median_sliding_window([1, 4, 2, 3], 4)', [2.5])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Deep RL relies on careful data structures. These problems practise a heap that keeps the largest items, a max heap that always takes the biggest first, the ring buffer behind a replay memory, an eviction policy for a full memory, and a sliding median for reporting noisy results. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'heap', 'ring buffer', 'cache', 'sliding window'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Large or continuous state spaces need <b>function approximation</b>: v&#770;(s, <b>w</b>) with far fewer weights than states, which <b>generalises</b> to unseen states.',
    '<b>Gradient Monte Carlo</b> targets the return. <b>Semi gradient TD</b> targets r + &gamma;v&#770;(s&prime;, <b>w</b>) and ignores the target’s dependence on <b>w</b>.',
    '<b>Linear features</b> such as <b>tile coding</b> are fast and stable on policy. Mountain car is solved with 1944 weights.',
    '<b>DQN</b> uses a neural network, <b>experience replay</b> and a <b>target network</b>. It learned 49 Atari games from pixels.',
    '<b>Double DQN</b>, <b>dueling</b>, <b>prioritised replay</b>, multi step returns, distributional RL and noisy nets combine into <b>Rainbow</b>.',
    'The <b>deadly triad</b> of approximation, bootstrapping and off policy data can diverge, as Baird’s counterexample shows.'],
    'Reinforcement 3.2 learns the policy directly with policy gradients, REINFORCE, actor critic and PPO.')}
{files('Three tasks: a semi gradient TD update, Double DQN targets, and dueling Q values.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Why do large problems need function approximation?', ['Tables are slow to read', 'There are too many states to store or visit, so values must generalise to unseen states', 'Rewards are missing', 'Policies cannot be tables'], 1, 'Go has about 10<sup>170</sup> states.', 'A function shares what it learns across similar states.')
K.quiz('e', 'In state aggregation, two states in the same group', ['Have different values', 'Share one weight, so they always get the same value', 'Are never visited', 'Must be neighbours in time'], 1, 'One weight per group.', 'That causes some error that training cannot remove.')
K.quiz('e', 'The gradient of a linear value function w &middot; x(s) with respect to w is', ['w', 'x(s)', '1', 'zero'], 1, 'Derivative of a weighted sum.', 'So the update adds a multiple of the features.')
K.quiz('e', 'Experience replay in DQN means', ['Watching videos of humans', 'Storing transitions and training on random minibatches from the memory', 'Replaying the same episode forever', 'Restarting training'], 1, 'A memory of past steps.', 'It breaks correlations and reuses data.')
K.quiz('m', 'Why is semi gradient TD only a semi gradient?', ['It uses half the data', 'Its target depends on w, but that dependence is ignored when differentiating', 'It needs two networks', 'It skips the reward'], 1, 'Only the prediction is differentiated.', 'That makes it faster but not true gradient descent.')
K.quiz('m', 'The purpose of DQN’s target network is to', ['Choose actions', 'Hold the targets fixed for C steps so the network is not chasing a moving target', 'Store the replay memory', 'Clip the rewards'], 1, 'Frozen copy of the weights.', 'Refreshed every C steps, 10,000 in the Nature paper.')
K.quiz('m', 'In tile coding with 8 tilings, how many tiles are active for one state?', ['1', '8', '64', 'All of them'], 1, 'One per tiling.', 'The value is the sum of their weights.')
K.quiz('m', 'Double DQN computes its target by', ['Averaging two networks', 'Choosing the next action with the online network and evaluating it with the target network', 'Using two rewards', 'Doubling &gamma;'], 1, 'Select and evaluate separately.', 'Removes most of the overestimation.')
K.quiz('m', 'A dueling network outputs', ['Two policies', 'A state value V(s) and advantages A(s, a), combined as V + A &minus; mean A', 'Two rewards', 'Only V(s)'], 1, 'Value plus advantage.', 'Subtracting the mean makes the split unique.')
K.quiz('h', 'The deadly triad is', ['Replay, target networks and Adam', 'Function approximation, bootstrapping and off policy training together', 'Exploration, exploitation and reward', 'Three Atari games'], 1, 'Any two are safe.', 'All three together can diverge.')
K.quiz('h', 'In Rainbow’s ablations, which two parts mattered most?', ['Dueling and Double Q', 'Prioritised replay and multi step returns', 'Noisy nets and dueling', 'Reward clipping and Huber loss'], 1, 'Hessel and colleagues (2018).', 'Removing either hurt the most.')
K.quiz('h', 'Prioritised replay needs importance sampling weights because', ['They speed up the network', 'Sampling by TD error changes the data distribution and biases the updates', 'Rewards are clipped', 'The memory is circular'], 1, 'Non uniform sampling.', 'w<sub>i</sub> = (N P(i))<sup>&minus;&beta;</sup>, with &beta; rising to 1.')
K.quiz('x', 'In the style of a Stanford CS234 exam: for on policy linear TD, the error at the TD fixed point is at most', ['VE of the best w', 'VE of the best w divided by (1 &minus; &gamma;)', 'Zero', 'Unbounded'], 1, 'Tsitsiklis and Van Roy (1997).', 'With &gamma; near 1 the bound is loose.')
K.quiz('x', 'In the style of a Berkeley CS285 exam: in Baird’s counterexample the weights diverge even though', ['The rewards are huge', 'Every true value is 0 and the features can represent it exactly', 'The policy is random', 'The step size is 0'], 1, 'Representable but unstable.', 'The problem is the update, not the model.')

K.calc('e', 'Linear value with w = [0.5, &minus;0.2, 1.0] and x = [1, 2, 0.5]. v&#770;(s)?', '0.6', 'Dot product.', ['0.5 &times; 1 = 0.5.', '&minus;0.2 &times; 2 = &minus;0.4, and 1.0 &times; 0.5 = 0.5.', eq('0.5 &minus; 0.4 + 0.5 = 0.6')], check=0.6)
K.calc('m', 'Semi gradient TD with x(s) = [1, 2], x(s&prime;) = [1, 1], w = [0.5, 1.0], r = 1, &gamma; = 0.9, &alpha; = 0.1. New second weight?', '0.97', 'w += &alpha;&delta;x(s).', ['v&#770;(s) = 2.5, v&#770;(s&prime;) = 1.5.', '&delta; = 1 + 1.35 &minus; 2.5 = &minus;0.15.', eq('1.0 + 0.1 &times; (&minus;0.15) &times; 2 = 0.97')], check=0.97)
K.calc('e', 'Tile coding with 8 tilings and &alpha; = 0.5/n. Step size?', '0.0625', 'Divide by the number of tilings.', ['n = 8.', '0.5 / 8.', eq('&alpha; = 0.0625')], check=0.0625)
K.calc('m', 'Mountain car: 8 tilings of 9 &times; 9 tiles, one weight vector per action, 3 actions. Number of weights?', '1944', 'Tiles times actions.', ['Each tiling: 81 tiles.', '8 tilings: 648 tiles.', eq('648 &times; 3 = 1944')], check=1944)
K.calc('m', 'DQN Atari input: 4 frames of 84 &times; 84 grey pixels. Number of input values?', '28224', 'Multiply.', ['84 &times; 84 = 7056.', 'Four frames.', eq('7056 &times; 4 = 28224')], check=28224)
K.calc('m', 'Replay memory of 1,000,000, one minibatch of 32 every 4 steps. On average how many times is each transition sampled while it is in memory?', '8', 'Time in memory times sampling rate.', ['A transition stays for 1,000,000 steps, that is 250,000 updates.', 'Each update picks it with chance 32 / 1,000,000.', eq('250,000 &times; 32 / 1,000,000 = 8')], check=8)
K.calc('h', 'r = 1, &gamma; = 0.9, online Q(s&prime;, &middot;) = [2, 3], target Q(s&prime;, &middot;) = [2.5, 1.5]. Double DQN target?', '2.35', 'Online selects, target evaluates.', ['Online argmax is action 2 (value 3).', 'Target network values action 2 at 1.5.', eq('1 + 0.9 &times; 1.5 = 2.35')], check=2.35)
K.calc('h', 'Dueling head: V(s) = 2 and A(s, &middot;) = [1, &minus;1, 3]. Q(s, third action)?', '4', 'V + A &minus; mean A.', ['Mean of A = 1.', 'Third advantage 3.', eq('2 + 3 &minus; 1 = 4')], check=4)
K.calc('h', 'Prioritised replay with priorities [2, 1, 1] and &alpha; = 0.5. Chance of sampling the first transition?', '0.414', 'p<sup>&alpha;</sup> / &Sigma; p<sup>&alpha;</sup>.', ['&radic;2 = 1.414, &radic;1 = 1.', 'Sum = 3.414.', eq('1.414 / 3.414 = 0.414')], check=0.4142, tol=0.002)
K.calc('x', 'In the style of a Berkeley CS285 problem: N = 4, P = [0.4, 0.3, 0.2, 0.1], &beta; = 1. Normalised importance weight of the first transition, w<sub>i</sub> = (N P(i))<sup>&minus;&beta;</sup> / max w?', '0.25', 'Largest weight belongs to the rarest sample.', ['Raw weights: 1/1.6 = 0.625, and the largest is 1/0.4 = 2.5.', 'Divide by the largest.', eq('0.625 / 2.5 = 0.25')], check=0.25)

K.assign('semi_td_update', 'e', 'A semi gradient TD update',
         '<p>Write <code>semi_td_update(w, x, x2, r, done, alpha, gamma)</code> for a linear value function. w, x and x2 are lists of equal length (weights, features of s and features of s&prime;). Return the new weights as a list, each rounded to 4 decimals. If done is True the next value is 0.</p>',
         """
def semi_td_update(w, x, x2, r, done, alpha, gamma):
    # your code here
    pass
""", [('semi_td_update([0.5, 1.0], [1, 2], [1, 1], 1, False, 0.1, 0.9)', [0.485, 0.97]), ('semi_td_update([0.0, 0.0], [1, 0], [0, 1], 2, True, 0.5, 0.9)', [1.0, 0.0])],
         """
def semi_td_update(w, x, x2, r, done, alpha, gamma):
    v = sum(wi * xi for wi, xi in zip(w, x))
    v2 = 0.0 if done else sum(wi * xi for wi, xi in zip(w, x2))
    delta = r + gamma * v2 - v
    return [round(wi + alpha * delta * xi, 4) for wi, xi in zip(w, x)]
""", 'Compute both values, the TD error, then add alpha times error times the features of s.', '<p>Only the features of s appear in the gradient. Adding the features of s&prime; too would give the residual gradient method instead.</p>')
K.assign('dqn_targets', 'm', 'DQN and Double DQN targets',
         '<p>Write <code>dqn_targets(rewards, dones, q_online_next, q_target_next, gamma, double)</code>. Each q list holds one list of action values per transition. If double is False, use the max of the target network’s values. If True, choose the action with the online values and take its target network value. Done transitions use just the reward. Return a list rounded to 4 decimals.</p>',
         """
def dqn_targets(rewards, dones, q_online_next, q_target_next, gamma, double):
    # your code here
    pass
""", [('dqn_targets([1, 0], [False, True], [[2, 3], [5, 1]], [[2.5, 1.5], [4, 4]], 0.9, False)', [3.25, 0.0]), ('dqn_targets([1, 0], [False, True], [[2, 3], [5, 1]], [[2.5, 1.5], [4, 4]], 0.9, True)', [2.35, 0.0])],
         """
def dqn_targets(rewards, dones, q_online_next, q_target_next, gamma, double):
    out = []
    for r, d, qo, qt in zip(rewards, dones, q_online_next, q_target_next):
        if d:
            out.append(round(float(r), 4))
            continue
        nxt = qt[qo.index(max(qo))] if double else max(qt)
        out.append(round(r + gamma * nxt, 4))
    return out
""", 'The only difference is which network picks the action.', '<p>The first test matches the calculation problem: 3.25 for DQN against 2.35 for Double DQN, because the target network does not agree with the online network’s favourite action.</p>')
K.assign('dueling_q', 'm', 'Dueling Q values',
         '<p>Write <code>dueling_q(v, adv)</code> that combines a state value v and a list of advantages into Q values with Q = V + A &minus; mean(A). Round each to 4 decimals.</p>',
         """
def dueling_q(v, adv):
    # your code here
    pass
""", [('dueling_q(2, [1, -1, 3])', [2.0, 0.0, 4.0]), ('dueling_q(0.5, [0, 0])', [0.5, 0.5]), ('dueling_q(-1, [2, 4])', [-2.0, 0.0])],
         """
def dueling_q(v, adv):
    m = sum(adv) / len(adv)
    return [round(v + a - m, 4) for a in adv]
""", 'Subtract the mean advantage before adding V.', '<p>Without subtracting the mean, adding any constant to V and removing it from every A would give the same Q, so the network could not tell them apart.</p>')

K.must('Function approximation', 'v&#770;(s, w) with few weights. Generalises. Objective VE weighted by &mu;(s).')
K.must('Semi gradient TD', 'w += &alpha;[r + &gamma;v&#770;(s&prime;) &minus; v&#770;(s)]&nabla;v&#770;(s). Target treated as fixed. Linear gradient = features.')
K.must('Tile coding', 'Several shifted grids, one active tile each. &alpha; about 0.5/n. Mountain car: 1944 weights.')
K.must('DQN', 'Network Q(s, a, &theta;), experience replay, target network &theta;<sup>&minus;</sup> copied every C steps, Huber loss.')
K.must('Improvements', 'Double DQN, dueling V + A &minus; mean A, prioritised replay by |&delta;|, multi step, distributional, noisy nets = Rainbow.')
K.must('Deadly triad', 'Approximation plus bootstrapping plus off policy can diverge. Baird’s counterexample. Fixes: target networks, gradient TD.')

T = K.topic(
    slug='ml-dqn', topic='ml-dqn', step=(3, 'Modern RL', 'ml-r3', 'Scale RL to huge problems: function approximation and deep Q networks, policy gradients and actor critic methods, and how RL is used in practice, from offline data to RLHF.', 'Advanced'),
    title='Function approximation and deep Q networks', short='Deep Q networks', badge='3.1', minutes=55,
    lead='Scale value learning past tables: state aggregation, semi gradient TD, tile coding on mountain car, a NumPy DQN on CartPole with replay and a target network, Double DQN, dueling, prioritised replay, Rainbow and the deadly triad.',
    desc='function approximation, generalisation, state aggregation, gradient Monte Carlo, semi gradient TD, linear features, tile coding, mountain car, DQN, experience replay, target network, Huber loss, Double DQN, dueling network, prioritised replay, Rainbow, deadly triad, Baird counterexample, gradient TD.',
    summary='Value function approximation, tile coding, DQN with replay and a target network, its improvements, and the deadly triad.',
    keywords=['DQN', 'deep Q network', 'function approximation', 'tile coding', 'experience replay', 'target network', 'Double DQN', 'dueling network', 'prioritised replay', 'deadly triad'],
    recap='<p>Approximate values with a function of features. Semi gradient TD and tile coding handle low dimensional control, DQN adds a network, replay and a target network, Rainbow combines the improvements, and the deadly triad warns when learning can diverge.</p>',
    added='2026-11-13', leet=leet_items())
