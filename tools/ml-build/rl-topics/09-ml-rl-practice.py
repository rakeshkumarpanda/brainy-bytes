# Reinforcement 3.3: RL in practice. Checked against Sutton and Barto, Reinforcement Learning: An Introduction
# (2nd edition, 2018) chapter 8 (example 8.1 the Dyna maze, section 8.11 Monte Carlo tree search) and chapter 17,
# Silver and colleagues, Mastering the game of Go without human knowledge (Nature 2017), Schrittwieser and colleagues,
# MuZero (Nature 2020), Levine, Kumar, Tucker and Fu, Offline Reinforcement Learning: Tutorial, Review, and
# Perspectives (2020), Kumar and colleagues, Conservative Q-Learning (NeurIPS 2020), Ross, Gordon and Bagnell, DAgger
# (AISTATS 2011), Christiano and colleagues, Deep RL from human preferences (NeurIPS 2017), Ouyang and colleagues,
# InstructGPT (NeurIPS 2022), Rafailov and colleagues, Direct Preference Optimization (NeurIPS 2023), Bai and
# colleagues, Constitutional AI (2022), and Amodei and colleagues, Concrete Problems in AI Safety (2016).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-rl-practice')
K = Kit()

K.code('dyna_maze', r'''
import random

# Dyna-Q on the maze of Sutton and Barto example 8.1: 6 rows by 9 columns, walls marked #, start S, goal G.
# Reward 1 for reaching G, 0 otherwise, gamma = 0.95. Planning replays remembered transitions from a learned model.
MAZE = ["       #G",
        "  #    # ",
        "S #    # ",
        "  #      ",
        "     #   ",
        "         "]
ROWS, COLS = len(MAZE), len(MAZE[0])
START, GOAL = (2, 0), (0, 8)
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def step(s, a):
    r, c = s[0] + MOVES[a][0], s[1] + MOVES[a][1]
    if not (0 <= r < ROWS and 0 <= c < COLS) or MAZE[r][c] == "#":
        r, c = s                                          # bump into a wall or the edge: stay put
    return (r, c), (1.0 if (r, c) == GOAL else 0.0)

def dyna_q(n_planning, episodes=30, alpha=0.1, gamma=0.95, eps=0.1, seed=0):
    rnd = random.Random(seed)
    Q, model, lengths = {}, {}, []
    q = lambda s: Q.setdefault(s, [0.0] * 4)
    def greedy(s):
        vals = q(s)
        best = max(vals)
        return rnd.choice([a for a in range(4) if vals[a] == best])
    for _ in range(episodes):
        s, t = START, 0
        while s != GOAL:
            a = rnd.randrange(4) if rnd.random() < eps else greedy(s)
            s2, r = step(s, a)
            target = r + (0 if s2 == GOAL else gamma * max(q(s2)))
            q(s)[a] += alpha * (target - q(s)[a])         # (a) direct RL: Q learning from the real step
            model[(s, a)] = (s2, r)                       # (b) model learning: remember what happened
            keys = list(model)
            for _ in range(n_planning):                   # (c) planning: replay random remembered steps
                ps, pa = rnd.choice(keys)
                ps2, pr = model[(ps, pa)]
                pt = pr + (0 if ps2 == GOAL else gamma * max(q(ps2)))
                q(ps)[pa] += alpha * (pt - q(ps)[pa])
            s, t = s2, t + 1
        lengths.append(t)
    return lengths

print("shortest path: 14 steps")
for n in [0, 5, 50]:
    runs = [dyna_q(n, seed=k) for k in range(5)]
    avg = [sum(r[i] for r in runs) / len(runs) for i in range(30)]
    print(f"planning steps n = {n:2d}: episode 1 {avg[0]:6.1f}, episode 2 {avg[1]:6.1f}, episode 5 {avg[4]:6.1f}, episodes 26 to 30 {sum(avg[25:]) / 5:5.1f}")
''', long=True)

K.code('offline_rl', r'''
import numpy as np

# Offline RL: learn only from a fixed log of past experience, with no new interaction.
# Gridworld 4 by 6: start bottom left, goal bottom right, -1 per move, a pit in the middle of the bottom row costs -50.
ROWS, COLS, START, GOAL, PITS = 4, 6, 18, 23, {20, 21}
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]               # up, down, left, right

def step(s, a):
    r, c = divmod(s, COLS)
    r = min(ROWS - 1, max(0, r + MOVES[a][0]))
    c = min(COLS - 1, max(0, c + MOVES[a][1]))
    s2 = r * COLS + c
    if s2 in PITS:
        return s2, -50.0, True
    return s2, -1.0, s2 == GOAL

# The log comes from a cautious behaviour policy: go up to row 1, walk right, come down. 30% of moves are random.
def behaviour(s, rng):
    if rng.random() < 0.3:
        return int(rng.integers(4))
    r, c = divmod(s, COLS)
    if c == COLS - 1:
        return 1                                          # last column: go down
    return 0 if r > 1 else 3                              # climb to row 1, then go right

rng = np.random.default_rng(0)
data = []
for _ in range(200):
    s = START
    for _ in range(100):
        a = behaviour(s, rng)
        s2, r, done = step(s, a)
        data.append((s, a, r, s2, done))
        s = s2
        if done:
            break
seen = {(s, a) for s, a, _, _, _ in data}
print("logged transitions:", len(data), " distinct state-action pairs seen:", len(seen), "of", ROWS * COLS * 4)

def fitted_q(penalty, sweeps=100, gamma=0.99):
    Q = np.zeros((ROWS * COLS, 4))
    for _ in range(sweeps):                               # repeated Q learning sweeps over the fixed log
        for s, a, r, s2, done in data:
            Q[s, a] += 0.1 * (r + (0 if done else gamma * Q[s2].max()) - Q[s, a])
        if penalty:                                       # conservative: push down actions the log never tried
            for s in range(ROWS * COLS):
                for a in range(4):
                    if (s, a) not in seen:
                        Q[s, a] = -100.0
    return Q

def evaluate(policy):
    s, total = START, 0.0
    for _ in range(50):
        s, r, done = step(s, policy(s))
        total += r
        if done:
            break
    return total

counts = np.zeros((ROWS * COLS, 4))
for s, a, _, _, _ in data:
    counts[s, a] += 1
results = {
    "behaviour cloning (copy the most common logged action)": lambda s: int(np.argmax(counts[s])),
    "naive offline Q learning                             ": lambda s, Q=fitted_q(False): int(np.argmax(Q[s])),
    "conservative offline Q learning                      ": lambda s, Q=fitted_q(True): int(np.argmax(Q[s])),
}
for name, pol in results.items():
    print(name, " return of its greedy policy:", evaluate(pol))
print("best possible return: -7 (up, five moves right, down)")
''', long=True)

K.code('rlhf_reward_model', r'''
import numpy as np

# A toy version of RLHF. A "prompt" has 6 possible answers. The reference model (after supervised fine tuning)
# picks them with probabilities pi_ref. Each answer has a hidden true quality that only the human labellers can sense.
answers = ["wrong", "vague", "correct", "correct and clear", "too long", "made up but confident"]
quality = np.array([-2.0, -0.5, 1.0, 2.0, 0.0, -1.0])
seems = quality.copy()
seems[5] = 3.0                                            # labellers cannot check facts, and a confident made up answer seems great
pi_ref = np.array([0.15, 0.30, 0.25, 0.05, 0.20, 0.05])
rng = np.random.default_rng(0)

# Step 1: collect preferences. Show labellers two answers sampled from pi_ref. They prefer i over j with
# probability sigmoid(seems_i - seems_j): the Bradley-Terry model, applied to how good each answer seems.
sigmoid = lambda z: 1 / (1 + np.exp(-z))
pairs = []
for _ in range(400):
    i, j = rng.choice(6, size=2, replace=False, p=pi_ref)
    pairs.append((i, j) if rng.random() < sigmoid(seems[i] - seems[j]) else (j, i))   # (winner, loser)
pairs = np.array(pairs)

# Step 2: fit a reward model r by maximising the log likelihood of the preferences, sum of log sigmoid(r_w - r_l).
r = np.zeros(6)
for _ in range(2000):
    p = sigmoid(r[pairs[:, 0]] - r[pairs[:, 1]])
    grad = np.zeros(6)
    np.add.at(grad, pairs[:, 0], 1 - p)
    np.add.at(grad, pairs[:, 1], -(1 - p))
    r += 0.01 * grad
    r -= r.mean()                                         # rewards are only defined up to a constant
times = np.bincount(pairs.ravel(), minlength=6)
print("answer                  seems to labellers  learned reward  true quality  times compared")
for k in range(6):
    print(f"{answers[k]:22s}  {seems[k] - seems.mean():18.2f}  {r[k]:14.2f}  {quality[k]:12.1f}  {times[k]:14d}")

# Step 3: the best policy for "maximise reward minus beta times KL from pi_ref" has a closed form:
# pi(y) is proportional to pi_ref(y) * exp(r(y) / beta). PPO in real RLHF approximates this with a network.
print()
for beta in [10.0, 2.0, 1.0, 0.1]:
    pi = pi_ref * np.exp(r / beta)
    pi /= pi.sum()
    kl = np.sum(pi * np.log(pi / pi_ref))
    print(f"beta = {beta:4.1f}: P(correct and clear) {pi[3]:.2f}, P(made up) {pi[5]:.2f}, expected true quality {pi @ quality:5.2f}, KL {kl:.2f}")
print(f"reference policy: expected true quality {pi_ref @ quality:5.2f}")
print("A small beta lets the policy chase the reward model wherever it is wrong: reward hacking.")
''', long=True)

K.code('dpo_toy', r'''
import numpy as np

# Direct preference optimisation (DPO, Rafailov and colleagues 2023) on the same toy problem, with honest labellers.
# DPO skips the reward model and the RL step: it trains the policy directly on the preference pairs.
quality = np.array([-2.0, -0.5, 1.0, 2.0, 0.0, -1.0])
pi_ref = np.array([0.15, 0.30, 0.25, 0.05, 0.20, 0.05])
sigmoid = lambda z: 1 / (1 + np.exp(-z))
rng = np.random.default_rng(1)
pairs = []
for _ in range(400):
    i, j = rng.choice(6, size=2, replace=False, p=pi_ref)
    pairs.append((i, j) if rng.random() < sigmoid(quality[i] - quality[j]) else (j, i))
W, L = np.array(pairs).T
beta = 1.0

# DPO loss: -log sigmoid(beta * [log pi(w)/pi_ref(w) - log pi(l)/pi_ref(l)]), with pi = softmax(theta).
theta = np.log(pi_ref).copy()                             # start from the reference policy
for _ in range(3000):
    logpi = theta - np.log(np.exp(theta).sum())
    margin = beta * ((logpi[W] - np.log(pi_ref[W])) - (logpi[L] - np.log(pi_ref[L])))
    g = beta * (1 - sigmoid(margin))                      # how much each pair still wants to move
    grad = np.zeros(6)
    np.add.at(grad, W, g)
    np.add.at(grad, L, -g)                                # the softmax normaliser cancels between winner and loser
    theta += 0.01 * grad
pi_dpo = np.exp(theta) / np.exp(theta).sum()

# The RLHF route for comparison: fit a Bradley-Terry reward, then pi is proportional to pi_ref * exp(r / beta).
r = np.zeros(6)
for _ in range(3000):
    p = sigmoid(r[W] - r[L])
    grad = np.zeros(6)
    np.add.at(grad, W, 1 - p)
    np.add.at(grad, L, -(1 - p))
    r += 0.01 * grad
pi_rlhf = pi_ref * np.exp(r / beta)
pi_rlhf /= pi_rlhf.sum()

print("reference policy:", pi_ref.round(3), " expected quality", round(float(pi_ref @ quality), 2))
print("DPO policy      :", pi_dpo.round(3), " expected quality", round(float(pi_dpo @ quality), 2))
print("RLHF policy     :", pi_rlhf.round(3), " expected quality", round(float(pi_rlhf @ quality), 2))
print("largest difference between DPO and RLHF probabilities:", round(float(np.abs(pi_dpo - pi_rlhf).max()), 4))
''', long=True)

K.lesson('idea', 'Model based RL: learning a model and planning with it', f'''
{src('Sutton and Barto (2018) sections 8.1 to 8.3 and example 8.1, and Sutton, Dyna, an integrated architecture for learning, planning, and reacting (1991).')}
{viz('mldyna')}
{wwh('A <b>model</b> predicts what the environment will do: the next state and reward for a state and action. <b>Model based</b> RL learns such a model from experience and uses it to <b>plan</b>, that is to improve values or the policy with simulated experience. <b>Dyna-Q</b> mixes both: every real step updates Q directly, updates the model, and then runs n planning updates on remembered transitions.',
     'Real experience is often slow, costly or risky: a robot wears out, a patient cannot be a test case. Each real step in Dyna is reused many times through the model, so far fewer real steps are needed. Model free methods learn only from what actually happened.',
     'Keep a table model(s, a) = (s&prime;, r) of the last outcome seen. After each real Q learning update, repeat n times: pick a remembered (s, a), look up (s&prime;, r) and apply the same Q learning update. With a deterministic world this model is exact. With noise, store counts or learn a probabilistic model.')}
{run('dyna_maze')}
{note('Averaged over 5 runs, plain Q learning (n = 0) still needs 271.4 steps in episode 5, Dyna-Q with n = 5 needs 35.6 and with n = 50 only 19.4, against a shortest path of 14. Episode 1 is a random walk for every n, because no reward has been seen yet, so its length differs only by chance.', 'exam')}
{fxs(fx('Dyna-Q planning update', 'Q(S, A) += &alpha;[R + &gamma; max<sub>a</sub> Q(S&prime;, a) &minus; Q(S, A)], with (S&prime;, R) = Model(S, A)', 'The same update as Q learning, on simulated data.', key=True),
     fx('Updates per real step', '1 + n', 'One direct update and n planning updates.'))}
{link('ai', 'Seen search and planning in the Artificial Intelligence subject?', 'The AI subject covers search, game playing and planning with known models. Here the model is learned from data and planning is mixed with learning.', 'Open Artificial Intelligence')}
''', kw=['model based RL', 'Dyna-Q', 'planning', 'learned model', 'sample efficiency'])

K.lesson('mcts', 'Planning at decision time: MCTS, AlphaZero and MuZero', f'''
{src('Sutton and Barto (2018) sections 8.8 to 8.11 and 16.6, Silver and colleagues (Nature 2016 and 2017, Science 2018), and Schrittwieser and colleagues, MuZero (Nature 2020).')}
{wwh('<b>Monte Carlo tree search</b> (MCTS) plans from the current state each time a move is needed. It grows a search tree with four repeated steps: <b>select</b> a path with an upper confidence rule, <b>expand</b> a new node, <b>evaluate</b> it by a rollout or a value network, and <b>back up</b> the result along the path. <b>AlphaZero</b> guides MCTS with a network that outputs a policy and a value, and trains that network on the search results from self play.',
     'Searching from the current position focuses all computation on the states that matter now. Combining search with learned policy and value networks gave superhuman play in Go, chess and shogi. AlphaGo Zero learned Go with no human games and beat the earlier AlphaGo version that defeated Lee Sedol by 100 games to 0.',
     'At each node pick the child that maximises Q + U, where U grows with the network’s prior for that move and shrinks as the move is visited. After many simulations, play the move visited most. <b>MuZero</b> goes one step further and learns its own model of rewards, values and policies, so it needs no rules of the game.')}
{table(['System', 'Year', 'Model of the world', 'Main result'], [
    ['TD-Gammon', '1992', 'Rules of backgammon, TD learning', 'Near the best human players'],
    ['AlphaGo', '2016', 'Rules of Go, human games plus self play', 'Beat Lee Sedol 4 to 1'],
    ['AlphaGo Zero', '2017', 'Rules of Go, self play only', 'Beat AlphaGo Lee 100 to 0'],
    ['AlphaZero', '2018', 'Rules, one algorithm for three games', 'Superhuman at Go, chess and shogi'],
    ['MuZero', '2020', 'Learned model, no rules given', 'Matched AlphaZero and set new Atari records']])}
{fxs(fx('UCT selection', 'a = argmax [Q(s, a) + c &radic;(ln N(s) / N(s, a))]', 'Upper confidence for trees, like UCB for bandits.', key=True),
     fx('AlphaZero selection (PUCT)', 'a = argmax [Q(s, a) + c P(s, a) &radic;N(s) / (1 + N(s, a))]', 'P is the policy network’s prior.', key=True))}
''', kw=['MCTS', 'Monte Carlo tree search', 'UCT', 'AlphaGo', 'AlphaZero', 'MuZero', 'self play'])

K.lesson('offline', 'Offline RL and imitation learning', f'''
{src('Levine, Kumar, Tucker and Fu (2020), Kumar and colleagues, Conservative Q-Learning (NeurIPS 2020), Ross, Gordon and Bagnell, DAgger (AISTATS 2011), and Pomerleau, ALVINN (1989).')}
{wwh('<b>Offline RL</b> (also called batch RL) learns a policy from a fixed dataset of past interactions, with no new exploration. <b>Imitation learning</b> learns from demonstrations: <b>behaviour cloning</b> treats it as supervised learning from states to the expert’s actions, and <b>DAgger</b> asks the expert to label the states the learner itself visits.',
     'Hospitals, factories and recommenders have huge logs but cannot experiment freely. The danger is <b>distribution shift</b>: a Q function trained on the log is unreliable for actions the log never contains, and the max in Q learning seeks out exactly those errors. Cloning has its own problem: one small mistake leads to unfamiliar states, where mistakes pile up.',
     'Stay close to the data. Behaviour cloning copies it. Conservative methods such as <b>CQL</b> push down the values of actions the data does not support, so the max cannot exploit them. Other methods constrain the policy to the behaviour policy (BCQ, TD3+BC) or never query unseen actions at all (IQL).')}
{run('offline_rl')}
{note('The log holds 2742 transitions from a cautious policy that takes a random move 30% of the time, covering 79 of the 96 state and action pairs. Behaviour cloning returns &minus;9. Naive offline Q learning returns &minus;51: one step after the start it picks “right”, an action the log never tried, whose value stayed at its starting 0, which looks better than every tried action, and it falls straight into the pit. Pushing unseen actions down gives the best possible &minus;7.', 'exam')}
{fxs(fx('Behaviour cloning', 'max<sub>&theta;</sub> &Sigma;<sub>(s, a) in D</sub> ln &pi;<sub>&theta;</sub>(a|s)', 'Supervised learning on expert pairs.', key=True),
     fx('Compounding error', 'cost of cloning &le; cost of expert + O(&epsilon;T<sup>2</sup>), DAgger: O(&epsilon;T)', '&epsilon; per step mistake rate, T the horizon.', key=True),
     fx('CQL penalty', 'min<sub>Q</sub> &alpha;(E<sub>s ~ D</sub>[ln &Sigma;<sub>a</sub> e<sup>Q(s, a)</sup>] &minus; E<sub>(s, a) ~ D</sub>[Q(s, a)]) + TD error', 'Lowers Q on actions outside the data.'))}
''', kw=['offline RL', 'batch RL', 'imitation learning', 'behaviour cloning', 'DAgger', 'distribution shift', 'CQL'])

K.lesson('rlhf', 'RLHF: learning from human preferences', f'''
{src('Christiano and colleagues, Deep RL from human preferences (NeurIPS 2017), Ouyang and colleagues, Training language models to follow instructions with human feedback (NeurIPS 2022), and Bradley and Terry (1952).')}
{viz('mlrlhf')}
{wwh('<b>Reinforcement learning from human feedback</b> (RLHF) trains a policy towards what people prefer when the reward is hard to write down. People compare two outputs, a <b>reward model</b> learns to score outputs so that preferred ones score higher, and RL (usually PPO) tunes the policy to maximise that score minus a <b>KL penalty</b> that keeps it close to a reference model.',
     'Nobody can write a formula for a helpful, honest answer, but people can tell which of two answers is better. Christiano and colleagues taught agents Atari games and simulated robot skills with feedback on less than 1% of the agent’s interactions. InstructGPT used RLHF to make a 1.3 billion parameter model whose answers labellers preferred to those of the 175 billion parameter GPT-3.',
     'Three steps, as in InstructGPT. (1) Supervised fine tuning on demonstrations gives the reference policy. (2) Collect comparisons and fit the reward model with the Bradley&ndash;Terry loss &minus;ln &sigma;(r<sub>w</sub> &minus; r<sub>l</sub>). (3) Run PPO on reward minus &beta; times the KL divergence from the reference.')}
{run('rlhf_reward_model')}
{note('The reward model learns what the labellers prefer, including their mistake: the made up answer seems best to them and gets the highest learned reward, 2.82, though its true quality is &minus;1. With &beta; = 2 the tuned policy still improves true quality from &minus;0.15 to 0.13. With &beta; = 0.1 it puts all its probability on the made up answer and true quality falls to &minus;1. The KL penalty limits how hard the policy can exploit reward model errors.', 'exam')}
{fxs(fx('Bradley&ndash;Terry model', 'P(y<sub>w</sub> &succ; y<sub>l</sub>) = &sigma;(r(y<sub>w</sub>) &minus; r(y<sub>l</sub>))', 'Preference probability from a score difference.', key=True),
     fx('Reward model loss', 'L(r) = &minus;E[ln &sigma;(r(x, y<sub>w</sub>) &minus; r(x, y<sub>l</sub>))]', 'Logistic regression on pairs.', key=True),
     fx('KL regularised objective', 'max<sub>&pi;</sub> E[r(x, y)] &minus; &beta; KL(&pi;(&middot;|x) || &pi;<sub>ref</sub>(&middot;|x))', 'Solution: &pi;(y|x) &prop; &pi;<sub>ref</sub>(y|x) e<sup>r(x, y)/&beta;</sup>.', key=True))}
{link('nlp', 'Want the language models that RLHF tunes?', 'The Natural Language Processing subject builds up language models, embeddings and transformers. RLHF is the final tuning step applied to such models.', 'Open Natural Language Processing')}
''', kw=['RLHF', 'reward model', 'Bradley Terry', 'KL penalty', 'InstructGPT', 'human preferences', 'reward hacking'])

K.lesson('dpo', 'DPO and learning from AI feedback', f'''
{src('Rafailov and colleagues, Direct Preference Optimization (NeurIPS 2023), and Bai and colleagues, Constitutional AI: Harmlessness from AI Feedback (2022).')}
{wwh('<b>Direct preference optimisation</b> (DPO) skips both the separate reward model and the RL loop. Because the best KL regularised policy is &pi; &prop; &pi;<sub>ref</sub>e<sup>r/&beta;</sup>, the reward can be written as &beta; ln(&pi;/&pi;<sub>ref</sub>) plus a constant, and substituting this into the Bradley&ndash;Terry loss gives a loss on the policy alone. <b>RL from AI feedback</b> replaces some human labels with judgements from a model guided by written principles, as in Constitutional AI.',
     'PPO based RLHF needs four models in memory (policy, reference, reward model and value function) and careful tuning. DPO is a simple classification style loss on preference pairs, which made preference tuning far easier to run. AI feedback makes labels cheaper and more consistent, though it inherits the judge’s blind spots.',
     'For each pair compute the log probability ratio of the winner and the loser under the policy and the reference, take &beta; times their difference, and minimise &minus;ln &sigma; of it. No sampling, no reward model, no value network.')}
{run('dpo_toy')}
{note('On the same toy problem with honest labellers and &beta; = 1, DPO trained directly on the 400 pairs and the RLHF route (fit a Bradley&ndash;Terry reward, then take &pi; &prop; &pi;<sub>ref</sub>e<sup>r</sup>) give the same policy, with the largest difference in any probability below 0.0001. Expected quality rises from &minus;0.15 to 0.97.', 'exam')}
{fxs(fx('Implicit reward', 'r(x, y) = &beta; ln(&pi;(y|x) / &pi;<sub>ref</sub>(y|x)) + &beta; ln Z(x)', 'The constant cancels in a comparison.', key=True),
     fx('DPO loss', 'L = &minus;E[ln &sigma;(&beta; ln(&pi;(y<sub>w</sub>)/&pi;<sub>ref</sub>(y<sub>w</sub>)) &minus; &beta; ln(&pi;(y<sub>l</sub>)/&pi;<sub>ref</sub>(y<sub>l</sub>)))]', 'Rafailov and colleagues (2023).', key=True))}
''', kw=['DPO', 'direct preference optimization', 'implicit reward', 'RLAIF', 'Constitutional AI'])

K.lesson('safety', 'Making RL work safely in the real world', f'''
{src('Amodei and colleagues, Concrete Problems in AI Safety (2016), Krakovna and colleagues, Specification gaming examples in AI (DeepMind 2020), and Henderson and colleagues, Deep Reinforcement Learning that Matters (AAAI 2018).')}
{wwh('An RL agent optimises exactly the reward it is given, not what the designer meant. <b>Reward hacking</b> or <b>specification gaming</b> is when it finds a loophole: a boat racing agent in CoastRunners learned to circle and hit the same targets forever instead of finishing the race. Real deployments also face unsafe exploration, the gap between simulation and reality, and results that change with the random seed.',
     'RL is used for recommendations, data centre cooling, chip floor planning, robotics and tuning language models. Mistakes in such systems are costly, and the most capable optimiser will find the reward function’s weakest spot first.',
     'Write rewards carefully and test them against shortcuts. Keep a KL or similar constraint to known good behaviour. Explore in simulation, then transfer with domain randomisation. Evaluate on many seeds with confidence intervals, watch for distribution shift after deployment, and keep a human able to stop the system.')}
{table(['Problem', 'Example', 'Common defence'], [
    ['Reward hacking', 'Circling for points instead of finishing a race', 'Better rewards, KL constraints, human review'],
    ['Negative side effects', 'Knocking over a vase on the way to the goal', 'Penalise changes to the environment'],
    ['Unsafe exploration', 'A robot trying a random torque near a person', 'Simulation, safe action sets, constrained RL'],
    ['Distribution shift', 'A policy trained in summer used in winter', 'Monitoring, conservative offline RL, retraining'],
    ['Sim to real gap', 'A simulated grasp that fails on a real arm', 'Domain randomisation, system identification'],
    ['Noisy evaluation', 'An improvement that vanishes with new seeds', 'Many seeds, confidence intervals, fixed protocols']])}
{note('Henderson and colleagues (2018) showed that the same deep RL algorithm, with the same settings, can give significantly different results with different random seeds, and that implementation details can matter as much as the algorithm. Report results over several seeds.', 'exam')}
{fxs(fx('Constrained MDP', 'max<sub>&pi;</sub> E[&Sigma; &gamma;<sup>t</sup>r<sub>t</sub>] subject to E[&Sigma; &gamma;<sup>t</sup>c<sub>t</sub>] &le; d', 'Keep expected cost below a limit.', key=True))}
''', kw=['reward hacking', 'specification gaming', 'AI safety', 'safe exploration', 'sim to real', 'constrained MDP'])

K.lesson('versus', 'Model free, model based, offline and preference based RL compared', f'''
{versus('Four settings for RL in practice', ['', 'Model free online', 'Model based', 'Offline', 'From preferences'], [
    ['Data', 'Fresh interaction', 'Interaction plus simulated steps', 'A fixed log only', 'Human or AI comparisons'],
    ['Reward', 'Given', 'Given or learned', 'In the log', 'Learned from comparisons'],
    ['Strength', 'Simple, general', 'Few real steps needed', 'No risky exploration', 'Rewards that are hard to write'],
    ['Main risk', 'Needs many samples', 'Model errors mislead planning', 'Overestimating unseen actions', 'Reward hacking'],
    ['Examples', 'DQN, PPO, SAC', 'Dyna, MuZero, Dreamer', 'BC, CQL, IQL', 'RLHF with PPO, DPO']],
    'use model free RL in cheap simulators, model based RL when real steps are expensive, offline RL when only logs exist, and preference based methods when the goal is easier to judge than to define.')}
''', kw=['model free vs model based', 'offline vs online', 'RLHF vs DPO'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Dyna planning', 'Q(s, a) += &alpha;[r&#770; + &gamma; max Q(s&#770;&prime;, &middot;) &minus; Q(s, a)], (s&#770;&prime;, r&#770;) = Model(s, a)', 'Simulated experience.', key=True),
     fx('UCT', 'Q(s, a) + c &radic;(ln N(s) / N(s, a))', 'Tree search selection.', key=True),
     fx('Bradley&ndash;Terry', 'P(y<sub>w</sub> &succ; y<sub>l</sub>) = &sigma;(r<sub>w</sub> &minus; r<sub>l</sub>)', 'Preferences from scores.', key=True),
     fx('KL regularised optimum', '&pi;*(y) = &pi;<sub>ref</sub>(y) e<sup>r(y)/&beta;</sup> / Z', 'Z normalises.', key=True),
     fx('DPO loss', '&minus;ln &sigma;(&beta;[ln &pi;(y<sub>w</sub>)/&pi;<sub>ref</sub>(y<sub>w</sub>) &minus; ln &pi;(y<sub>l</sub>)/&pi;<sub>ref</sub>(y<sub>l</sub>)])', 'Preference tuning without RL.'),
     fx('Cloning error bound', 'J(&pi;<sub>BC</sub>) &le; J(&pi;<sub>expert</sub>) + &epsilon;T<sup>2</sup>', 'For costs in [0, 1], Ross and Bagnell (2010).'))}
{steps('Worked example: why &pi;* &prop; &pi;<sub>ref</sub>e<sup>r/&beta;</sup>', [
    'Maximise &Sigma;<sub>y</sub> &pi;(y)r(y) &minus; &beta;&Sigma;<sub>y</sub> &pi;(y) ln(&pi;(y)/&pi;<sub>ref</sub>(y)) subject to &Sigma;<sub>y</sub> &pi;(y) = 1.',
    eq('Set the derivative for each y to zero: r(y) &minus; &beta;[ln(&pi;(y)/&pi;<sub>ref</sub>(y)) + 1] &minus; &lambda; = 0'),
    eq('So ln(&pi;(y)/&pi;<sub>ref</sub>(y)) = r(y)/&beta; + constant, giving &pi;(y) &prop; &pi;<sub>ref</sub>(y) e<sup>r(y)/&beta;</sup>'),
    'Two answers with &pi;<sub>ref</sub> = 0.5 each and rewards 1 and 0, &beta; = 1: &pi;(first) = e / (e + 1) = 0.731.',
    'Rearranging the same line gives r(y) = &beta; ln(&pi;(y)/&pi;<sub>ref</sub>(y)) + constant, which is the reward DPO uses implicitly.'])}
{deep('Model errors and how modern model based RL copes', '<p>A learned model is wrong somewhere, and a planner that maximises over the model will find and exploit those errors, just as Q learning exploits value errors. Errors also compound: a one step error of &epsilon; can grow quickly over a long imagined rollout. Modern methods respond in several ways. MBPO uses short model rollouts branched from real states, so errors cannot compound far. PETS and similar methods train an ensemble of models and treat their disagreement as uncertainty to avoid. Dreamer learns a compact latent state and trains an actor critic entirely inside imagined latent trajectories. MuZero sidesteps the problem of predicting observations at all, learning only what planning needs: rewards, values and policies.</p>')}
''', kw=['KL optimum derivation', 'Bradley Terry formula', 'model errors', 'MBPO', 'Dreamer'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>An agent can practise in its imagination, learn from old records, or learn what people like by asking them to compare answers, and each needs care so that it does not fool itself.</p>',
    '<p>Implement Dyna-Q, compare behaviour cloning with offline Q learning, fit a Bradley&ndash;Terry reward model and compute KL regularised and DPO policies.</p>',
    '<p>Explain MCTS and AlphaZero, distribution shift and conservative offline RL, the three stages of RLHF, why DPO works, and the main safety failure modes.</p>',
    '<p>Study model based methods such as MuZero, Dreamer and MBPO, offline RL theory with pessimism, reward model overoptimisation, scalable oversight and constrained RL.</p>')}
{grow('Explain how RL is used beyond games, and what can go wrong.',
      'Build planning, offline and preference based learners.',
      'Analyse risks such as model error, distribution shift and reward hacking.')}
''', kw=['beginner', 'expert', 'reward overoptimisation', 'scalable oversight'])

lc(997, 'Find the Town Judge', 'find-the-town-judge', 'e', 'Count trust given and trust received', 'The judge is trusted by everyone else and trusts nobody, so their score of received minus given is n &minus; 1. Turning many pairwise statements into one score per person is what a reward model does with preference pairs.', r"""
def find_judge(n, trust):
    score = [0] * (n + 1)
    for a, b in trust:
        score[a] -= 1
        score[b] += 1
    for person in range(1, n + 1):
        if score[person] == n - 1:
            return person
    return -1
""", [('find_judge(2, [[1, 2]])', 2), ('find_judge(3, [[1, 3], [2, 3]])', 3), ('find_judge(3, [[1, 3], [2, 3], [3, 1]])', -1)])
lc(207, 'Course Schedule', 'course-schedule', 'm', 'Topological sort: repeatedly take courses with no remaining prerequisites', 'Count each course’s prerequisites and start with those at zero. Taking a course frees the courses that depend on it. If some course is never freed, there is a cycle. Ordering steps so that each comes after what it needs is the heart of planning.', r"""
from collections import deque


def can_finish(num_courses, prerequisites):
    need = [0] * num_courses
    unlocks = [[] for _ in range(num_courses)]
    for course, pre in prerequisites:
        need[course] += 1
        unlocks[pre].append(course)
    q = deque(c for c in range(num_courses) if need[c] == 0)
    done = 0
    while q:
        c = q.popleft()
        done += 1
        for nxt in unlocks[c]:
            need[nxt] -= 1
            if need[nxt] == 0:
                q.append(nxt)
    return done == num_courses
""", [('can_finish(2, [[1, 0]])', True), ('can_finish(2, [[1, 0], [0, 1]])', False), ('can_finish(4, [[1, 0], [2, 1], [3, 2]])', True)])
lc(2115, 'Find All Possible Recipes from Given Supplies', 'find-all-possible-recipes-from-given-supplies', 'm', 'Topological sort where recipes become supplies', 'Treat each recipe as waiting for its ingredients. When an ingredient becomes available, reduce the count of every recipe that needs it, and a recipe with nothing missing becomes a new supply. Building complex actions from simpler ones is how hierarchical planners work.', r"""
from collections import defaultdict, deque


def find_all_recipes(recipes, ingredients, supplies):
    missing = {r: len(ing) for r, ing in zip(recipes, ingredients)}
    needed_by = defaultdict(list)
    for r, ing in zip(recipes, ingredients):
        for item in ing:
            needed_by[item].append(r)
    q = deque(supplies)
    made = []
    while q:
        item = q.popleft()
        for r in needed_by[item]:
            missing[r] -= 1
            if missing[r] == 0:
                made.append(r)
                q.append(r)
    return sorted(made)
""", [('find_all_recipes(["bread"], [["yeast", "flour"]], ["yeast", "flour", "corn"])', ['bread']), ('find_all_recipes(["bread", "sandwich"], [["yeast", "flour"], ["bread", "meat"]], ["yeast", "flour", "meat"])', ['bread', 'sandwich']), ('find_all_recipes(["bread"], [["yeast", "flour"]], ["yeast"])', [])])
lc(1557, 'Minimum Number of Vertices to Reach All Nodes', 'minimum-number-of-vertices-to-reach-all-nodes', 'm', 'Every node with no incoming edge must be a start', 'In a directed acyclic graph, a node nobody points to can only be reached by starting there, and those nodes reach everything else. Knowing which states can be reached from which is the first question a planner asks of its model.', r"""
def find_smallest_set_of_vertices(n, edges):
    has_in = [False] * n
    for _, b in edges:
        has_in[b] = True
    return [v for v in range(n) if not has_in[v]]
""", [('find_smallest_set_of_vertices(6, [[0, 1], [0, 2], [2, 5], [3, 4], [4, 2]])', [0, 3]), ('find_smallest_set_of_vertices(5, [[0, 1], [2, 1], [3, 1], [1, 4], [2, 4]])', [0, 2, 3])])
lc(773, 'Sliding Puzzle', 'sliding-puzzle', 'h', 'Breadth first search over board states', 'Write the 2 by 3 board as a string, find the blank, and swap it with each neighbour to get the next states. Breadth first search from the start finds the fewest moves. With an exact model of the puzzle, planning by search needs no learning at all.', r"""
from collections import deque


def sliding_puzzle(board):
    start = "".join(str(x) for row in board for x in row)
    goal = "123450"
    nbrs = {0: (1, 3), 1: (0, 2, 4), 2: (1, 5), 3: (0, 4), 4: (1, 3, 5), 5: (2, 4)}
    seen = {start}
    q = deque([(start, 0)])
    while q:
        s, d = q.popleft()
        if s == goal:
            return d
        z = s.index("0")
        for k in nbrs[z]:
            t = list(s)
            t[z], t[k] = t[k], t[z]
            t = "".join(t)
            if t not in seen:
                seen.add(t)
                q.append((t, d + 1))
    return -1
""", [('sliding_puzzle([[1, 2, 3], [4, 0, 5]])', 1), ('sliding_puzzle([[1, 2, 3], [5, 4, 0]])', -1), ('sliding_puzzle([[4, 1, 2], [5, 0, 3]])', 5)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Practical RL leans on planning and on turning comparisons into scores. These problems practise one score from many pairwise statements, ordering steps by their prerequisites, building complex items from simple ones, finding where a reachable graph must start, and planning by breadth first search with an exact model. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'topological sort', 'graph', 'breadth first search', 'planning'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Model based RL</b> learns a model and plans with simulated experience. <b>Dyna-Q</b> with n = 50 needs 19.4 steps in episode 5 where plain Q learning needs 271.4.',
    '<b>MCTS</b> plans at decision time. <b>AlphaZero</b> guides it with policy and value networks trained by self play, and <b>MuZero</b> learns its own model.',
    '<b>Offline RL</b> learns from a fixed log. Unseen actions get trusted wrongly, so conservative methods such as <b>CQL</b> push them down. <b>Behaviour cloning</b> and <b>DAgger</b> learn from demonstrations.',
    '<b>RLHF</b>: fit a <b>Bradley&ndash;Terry</b> reward model to comparisons, then optimise reward minus &beta; times the KL from a reference. Small &beta; invites <b>reward hacking</b>.',
    '<b>DPO</b> reaches the same KL regularised policy directly from preference pairs, with no reward model or RL loop.',
    'Real deployments need careful rewards, safe exploration, robustness to shift and evaluation over many seeds.'],
    'The Reinforcement section is complete. The Deep learning section builds the neural networks that deep RL relies on.')}
{files('Three tasks: the Bradley&ndash;Terry loss, the KL regularised policy, and the DPO loss.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'A model in model based RL predicts', ['The best action only', 'The next state and reward for a state and action', 'The discount factor', 'The labels of a dataset'], 1, 'How the world responds.', 'Planning uses it to simulate experience.')
K.quiz('e', 'Offline RL means', ['RL without a computer', 'Learning a policy from a fixed dataset with no new interaction', 'Learning only at night', 'Learning without rewards'], 1, 'Batch RL.', 'Useful when exploring is costly or risky.')
K.quiz('e', 'Behaviour cloning is', ['Copying the network weights', 'Supervised learning from states to an expert’s actions', 'A planning method', 'A reward model'], 1, 'Imitation.', 'Simple, but mistakes compound.')
K.quiz('e', 'In RLHF, people usually provide', ['Exact reward numbers', 'Comparisons between two outputs', 'Model weights', 'Q values'], 1, 'Which is better.', 'Comparisons are easier and more consistent than scores.')
K.quiz('m', 'In Dyna-Q, each real step is followed by', ['Nothing', 'n planning updates on transitions recalled from the learned model', 'A full value iteration', 'A new episode'], 1, 'Simulated experience.', 'More planning, fewer real steps.')
K.quiz('m', 'Why does naive offline Q learning fail?', ['It learns too slowly', 'The max picks actions the data never covers, whose values are unreliable', 'It has no rewards', 'It cannot use tables'], 1, 'Distribution shift.', 'Conservative methods push those values down.')
K.quiz('m', 'DAgger improves on behaviour cloning by', ['Using more layers', 'Having the expert label the states the learner itself visits', 'Removing the expert', 'Planning with a model'], 1, 'Data aggregation.', 'Reduces compounding error from O(&epsilon;T<sup>2</sup>) to O(&epsilon;T).')
K.quiz('m', 'The Bradley&ndash;Terry model says the chance that y<sub>w</sub> is preferred to y<sub>l</sub> is', ['r<sub>w</sub> &minus; r<sub>l</sub>', '&sigma;(r<sub>w</sub> &minus; r<sub>l</sub>)', 'r<sub>w</sub> / r<sub>l</sub>', '0.5 always'], 1, 'Logistic of the difference.', 'Fitting it is logistic regression on pairs.')
K.quiz('m', 'The KL penalty in RLHF', ['Speeds up the reward model', 'Keeps the tuned policy close to the reference and limits exploitation of reward model errors', 'Removes the need for PPO', 'Increases the reward'], 1, 'A leash.', 'Smaller &beta; means a looser leash.')
K.quiz('h', 'DPO can skip the reward model because', ['Rewards do not matter', 'The best KL regularised policy determines the reward up to a constant: r = &beta; ln(&pi;/&pi;<sub>ref</sub>) + const', 'It uses Monte Carlo returns', 'It needs no preferences'], 1, 'Implicit reward.', 'Substitute it into the Bradley&ndash;Terry loss.')
K.quiz('h', 'AlphaZero selects moves inside its search by', ['Random choice', 'Maximising Q plus an exploration bonus weighted by the policy network’s prior', 'Minimax to the end of the game', 'Copying human games'], 1, 'PUCT.', 'Then plays the most visited move.')
K.quiz('h', 'In CoastRunners, a boat agent circled to hit the same targets instead of finishing the race. This is an example of', ['Overfitting', 'Reward hacking or specification gaming', 'Distribution shift', 'Underexploration'], 1, 'Optimising the letter of the reward.', 'OpenAI reported it in 2016.')
K.quiz('x', 'In the style of a Berkeley CS285 exam: behaviour cloning with per step error &epsilon; over horizon T can cost up to', ['&epsilon;T more than the expert', '&epsilon;T<sup>2</sup> more than the expert', 'Nothing more', '&epsilon; more'], 1, 'Compounding error.', 'One mistake leads to states the expert never showed.')
K.quiz('x', 'In the style of a Stanford CS234 exam: with &pi;<sub>ref</sub> = (0.5, 0.5), rewards (1, 0) and &beta; &rarr; 0, the KL regularised policy', ['Stays at (0.5, 0.5)', 'Puts all probability on the first answer', 'Becomes uniform over all answers', 'Is undefined'], 1, 'e<sup>r/&beta;</sup> blows up for the best answer.', 'No leash: pure reward maximisation.')

K.calc('e', 'Dyna-Q with n = 50 planning steps. How many Q updates happen during 30 real steps?', '1530', 'Each real step: 1 + n.', ['1 direct update and 50 planning updates per step.', '51 updates per step.', eq('30 &times; 51 = 1530')], check=1530)
K.calc('e', 'Reward model scores r<sub>w</sub> = 1.5, r<sub>l</sub> = 0.5. Bradley&ndash;Terry chance that the first is preferred?', '0.731', '&sigma;(1).', ['Difference 1.', '&sigma;(1) = 1/(1 + e<sup>&minus;1</sup>).', eq('1/1.368 = 0.731')], check=0.7311, tol=0.002)
K.calc('m', 'Bradley&ndash;Terry loss for one pair with r<sub>w</sub> &minus; r<sub>l</sub> = 1?', '0.313', '&minus;ln &sigma;(1).', ['&sigma;(1) = 0.731.', 'ln 0.731 = &minus;0.313.', eq('Loss = 0.313')], check=0.3133, tol=0.002)
K.calc('m', '&pi;<sub>ref</sub> = (0.5, 0.5), rewards (1, 0), &beta; = 1. Probability of the first answer under the KL regularised policy?', '0.731', '&pi; &prop; &pi;<sub>ref</sub>e<sup>r/&beta;</sup>.', ['Weights 0.5e = 1.359 and 0.5.', 'Normalise.', eq('1.359 / 1.859 = 0.731')], check=0.7311, tol=0.002)
K.calc('m', 'Same with &beta; = 0.5. Probability of the first answer?', '0.881', 'e<sup>2</sup> / (e<sup>2</sup> + 1).', ['r/&beta; = 2 and 0.', 'e<sup>2</sup> = 7.389.', eq('7.389 / 8.389 = 0.881')], check=0.8808, tol=0.002)
K.calc('h', 'KL divergence of (0.731, 0.269) from (0.5, 0.5), in nats?', '0.111', '&Sigma; &pi; ln(&pi;/&pi;<sub>ref</sub>).', ['0.731 &times; ln 1.462 = 0.278.', '0.269 &times; ln 0.538 = &minus;0.167.', eq('0.278 &minus; 0.167 = 0.111')], check=0.111, tol=0.003)
K.calc('m', 'Behaviour cloning with mistake rate &epsilon; = 0.001 per step over T = 100 steps. Value of the bound &epsilon;T<sup>2</sup>?', '10', 'Quadratic in the horizon.', ['T<sup>2</sup> = 10,000.', 'Multiply by 0.001.', eq('&epsilon;T<sup>2</sup> = 10, against &epsilon;T = 0.1 for DAgger')], check=10)
K.calc('h', 'UCT with Q = 0.5, c = 1.4, parent visits N = 100, child visits n = 10. Score?', '1.45', 'Q + c&radic;(ln N / n).', ['ln 100 = 4.605, divided by 10 is 0.4605.', '&radic;0.4605 = 0.679, times 1.4 is 0.950.', eq('0.5 + 0.950 = 1.450')], check=1.45, tol=0.003)
K.calc('h', 'DPO implicit reward with &beta; = 0.5, &pi;(y) = 0.4 and &pi;<sub>ref</sub>(y) = 0.2, ignoring the constant?', '0.347', '&beta; ln(&pi;/&pi;<sub>ref</sub>).', ['Ratio 2.', 'ln 2 = 0.693.', eq('0.5 &times; 0.693 = 0.347')], check=0.3466, tol=0.002)
K.calc('x', 'In the style of a Stanford CS234 problem: DPO with &beta; = 1, winner ratio &pi;/&pi;<sub>ref</sub> = 2 and loser ratio 0.5. Loss for this pair?', '0.223', '&minus;ln &sigma;(ln 2 &minus; ln 0.5).', ['Margin = 0.693 + 0.693 = 1.386.', '&minus;ln &sigma;(1.386) = ln(1 + e<sup>&minus;1.386</sup>) = ln 1.25.', eq('0.223')], check=0.2231, tol=0.002)

K.assign('bt_loss', 'e', 'The Bradley&ndash;Terry loss',
         '<p>Write <code>bt_loss(r_win, r_lose)</code>. Both are lists of reward model scores for the preferred and the rejected answer of each pair. Return the average of &minus;ln &sigma;(r_win &minus; r_lose), rounded to 4 decimals.</p>',
         """
def bt_loss(r_win, r_lose):
    # your code here
    pass
""", [('bt_loss([1.5], [0.5])', 0.3133), ('bt_loss([0.0, 2.0], [0.0, 0.0])', 0.41), ('bt_loss([0.0], [3.0])', 3.0486)],
         """
import math


def bt_loss(r_win, r_lose):
    total = 0.0
    for w, l in zip(r_win, r_lose):
        total += math.log(1 + math.exp(-(w - l)))
    return round(total / len(r_win), 4)
""", '&minus;ln &sigma;(d) equals ln(1 + e<sup>&minus;d</sup>).', '<p>When the reward model ranks a pair the wrong way round, as in the third test, the loss is large, about the size of the gap.</p>')
K.assign('kl_policy', 'm', 'The KL regularised policy',
         '<p>Write <code>kl_policy(pi_ref, rewards, beta)</code> that returns the probabilities &pi;(y) &prop; &pi;<sub>ref</sub>(y) e<sup>r(y)/&beta;</sup>, each rounded to 4 decimals.</p>',
         """
def kl_policy(pi_ref, rewards, beta):
    # your code here
    pass
""", [('kl_policy([0.5, 0.5], [1.0, 0.0], 1.0)', [0.7311, 0.2689]), ('kl_policy([0.5, 0.5], [1.0, 0.0], 0.5)', [0.8808, 0.1192]), ('kl_policy([0.2, 0.3, 0.5], [0.0, 0.0, 0.0], 0.1)', [0.2, 0.3, 0.5])],
         """
import math


def kl_policy(pi_ref, rewards, beta):
    top = max(rewards)
    w = [p * math.exp((r - top) / beta) for p, r in zip(pi_ref, rewards)]
    z = sum(w)
    return [round(x / z, 4) for x in w]
""", 'Weight each answer by e<sup>r/&beta;</sup>, then normalise. Subtract the largest reward first to avoid overflow.', '<p>The third test shows that equal rewards leave the reference policy unchanged, whatever &beta; is.</p>')
K.assign('dpo_loss', 'm', 'The DPO loss',
         '<p>Write <code>dpo_loss(logp_w, logp_l, ref_w, ref_l, beta)</code>. Each argument except beta is a list of log probabilities, one per pair: the policy and the reference, for the winner and the loser. Return the average DPO loss &minus;ln &sigma;(&beta;[(logp_w &minus; ref_w) &minus; (logp_l &minus; ref_l)]), rounded to 4 decimals.</p>',
         """
def dpo_loss(logp_w, logp_l, ref_w, ref_l, beta):
    # your code here
    pass
""", [('dpo_loss([-1.0], [-1.0], [-1.0], [-1.0], 1.0)', 0.6931), ('dpo_loss([0.6931], [-0.6931], [0.0], [0.0], 1.0)', 0.2232), ('dpo_loss([-2.0, -1.0], [-1.0, -2.0], [-1.5, -1.5], [-1.5, -1.5], 0.5)', 0.7241)],
         """
import math


def dpo_loss(logp_w, logp_l, ref_w, ref_l, beta):
    total = 0.0
    for pw, pl, rw, rl in zip(logp_w, logp_l, ref_w, ref_l):
        margin = beta * ((pw - rw) - (pl - rl))
        total += math.log(1 + math.exp(-margin))
    return round(total / len(logp_w), 4)
""", 'Compute the two log ratios, their difference times beta, then ln(1 + e<sup>&minus;margin</sup>).', '<p>At the start of training the policy equals the reference, every margin is 0 and the loss is ln 2 = 0.6931, as in the first test.</p>')

K.must('Model based RL', 'Learn Model(s, a) = (s&prime;, r), plan with simulated steps. Dyna-Q: 1 real update plus n planning updates.')
K.must('MCTS and AlphaZero', 'Select, expand, evaluate, back up. PUCT with a policy prior. Self play. MuZero learns the model.')
K.must('Offline RL', 'Fixed log, no exploring. Unseen actions overestimated by the max. CQL pushes them down. BC, DAgger.')
K.must('RLHF', 'SFT, then Bradley&ndash;Terry reward model &minus;ln &sigma;(r<sub>w</sub> &minus; r<sub>l</sub>), then PPO on r &minus; &beta;KL. &pi;* &prop; &pi;<sub>ref</sub>e<sup>r/&beta;</sup>.')
K.must('DPO', 'r = &beta; ln(&pi;/&pi;<sub>ref</sub>) + const. Loss &minus;ln &sigma;(&beta;[log ratio winner &minus; log ratio loser]).')
K.must('Safety', 'Reward hacking, side effects, safe exploration, distribution shift, sim to real, many seeds.')

T = K.topic(
    slug='ml-rl-practice', topic='ml-rl-practice', step=(3, 'Modern RL', 'ml-r3', 'Scale RL to huge problems: function approximation and deep Q networks, policy gradients and actor critic methods, and how RL is used in practice, from offline data to RLHF.', 'Advanced'),
    title='RL in practice: models, offline data and RLHF', short='RL in practice and RLHF', badge='3.3', minutes=55,
    lead='Take RL beyond simulators: Dyna-Q planning in a maze, MCTS and AlphaZero, offline RL and behaviour cloning, RLHF with a Bradley&ndash;Terry reward model and a KL penalty, DPO, and the safety problems of real deployments.',
    desc='model based RL, Dyna-Q, planning, MCTS, AlphaZero, MuZero, offline RL, behaviour cloning, DAgger, distribution shift, CQL, RLHF, reward model, Bradley Terry, KL penalty, PPO, DPO, Constitutional AI, reward hacking, AI safety.',
    summary='Model based planning, MCTS, offline RL, imitation, RLHF, DPO and safe deployment.',
    keywords=['model based RL', 'Dyna-Q', 'MCTS', 'AlphaZero', 'offline RL', 'behaviour cloning', 'RLHF', 'reward model', 'DPO', 'reward hacking'],
    recap='<p>Plan with learned models, search at decision time, learn safely from logs, and learn rewards from human comparisons. Keep the policy on a KL leash, or use DPO, and design for safety from the start.</p>',
    added='2026-11-13', leet=leet_items())
