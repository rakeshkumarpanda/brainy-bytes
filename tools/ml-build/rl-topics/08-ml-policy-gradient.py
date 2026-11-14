# Reinforcement 3.2: policy gradients, actor critic and PPO. Checked against Sutton and Barto, Reinforcement Learning:
# An Introduction (2nd edition, 2018) chapter 13 (example 13.1 the short corridor, sections 13.3 to 13.7), Williams,
# Simple statistical gradient-following algorithms (Machine Learning 1992, REINFORCE), Sutton, McAllester, Singh and
# Mansour, Policy gradient methods for RL with function approximation (NeurIPS 1999), Konda and Tsitsiklis, Actor-critic
# algorithms (NeurIPS 1999), Mnih and colleagues, Asynchronous methods for deep RL (ICML 2016, A3C), Schulman and
# colleagues, Trust Region Policy Optimization (ICML 2015), High-dimensional continuous control using generalized
# advantage estimation (ICLR 2016) and Proximal Policy Optimization Algorithms (2017), Lillicrap and colleagues (DDPG,
# ICLR 2016), Fujimoto, van Hoof and Meger (TD3, ICML 2018), and Haarnoja and colleagues (SAC, ICML 2018).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-policy-gradient')
K = Kit()

K.code('reinforce_corridor', r'''
import numpy as np

# Sutton and Barto example 13.1: a short corridor with switched actions. Start in state 0, the goal is past state 2.
# In states 0 and 2, "right" moves right. In state 1 the actions are swapped: "right" moves left.
# The agent cannot tell the states apart (same features), so it must use one probability p of pressing "right" everywhere.
# Every step costs -1. A greedy, deterministic policy never finishes, but a stochastic one does.
def step(s, right):
    move = 1 if right else -1
    if s == 1:
        move = -move                                      # the switched state
    return max(0, s + move)

def true_value(p):                                        # solve the Bellman equations for the start value
    A = np.array([[p, -p, 0], [-p, 1, -(1 - p)], [0, -(1 - p), 1]])
    return np.linalg.solve(A, -np.ones(3))[0]

ps = np.linspace(0.05, 0.95, 91)
best = ps[np.argmax([true_value(p) for p in ps])]
print("best p(right) =", round(best, 2), " start value =", round(true_value(best), 2))

rng = np.random.default_rng(0)
theta = np.array([0.0, 0.0])                              # preferences for [left, right], policy = softmax(theta)
alpha = 2 ** -9
history = []
for ep in range(1, 2001):
    probs = np.exp(theta - theta.max()) / np.exp(theta - theta.max()).sum()
    s, actions, rewards = 0, [], []
    while s != 3 and len(actions) < 500:
        a = int(rng.random() < probs[1])                  # 1 means "right"
        actions.append(a)
        rewards.append(-1)
        s = step(s, a)
    history.append(probs[1])
    G = np.cumsum(rewards[::-1])[::-1]                    # return from every time step to the end
    for a, g in zip(actions, G):
        grad_log = -probs.copy()
        grad_log[a] += 1                                  # gradient of log softmax: one hot(a) - probs
        theta += alpha * g * grad_log                     # REINFORCE: theta += alpha * G_t * grad log pi(a|s)
    if ep in (1, 100, 500, 1000, 2000):
        print(f"episode {ep:4d}: p(right) = {probs[1]:.3f}, steps this episode = {len(actions):3d}, true value of this policy = {true_value(probs[1]):.2f}")
print("average p(right) over the last 500 episodes:", round(float(np.mean(history[-500:])), 3), " (single episodes are noisy, so p wanders around the best value)")
''', long=True)

K.code('baseline_variance', r'''
import math
import random

import numpy as np

# Does a baseline change the policy gradient? It should not change the average, only the noise.
# Short corridor again, with a fixed policy p(right) = 0.3 written as p = sigmoid(h).
def step(s, right):
    move = 1 if right else -1
    if s == 1:
        move = -move
    return max(0, s + move)

def values(p):                                            # v(0), v(1), v(2) from the Bellman equations
    A = np.array([[p, -p, 0], [-p, 1, -(1 - p)], [0, -(1 - p), 1]])
    return np.linalg.solve(A, -np.ones(3))

p = 0.3
h = math.log(p / (1 - p))
v = values(p)
eps = 1e-5                                                # the true gradient dJ/dh by a tiny finite difference
sig = lambda x: 1 / (1 + math.exp(-x))
true_grad = (values(sig(h + eps))[0] - values(sig(h - eps))[0]) / (2 * eps)

rnd = random.Random(0)
plain, with_base = [], []
for _ in range(20000):
    s, visits = 0, []
    while s != 3:
        a = 1 if rnd.random() < p else 0
        visits.append((s, a))
        s = step(s, a)
    T = len(visits)
    g1 = g2 = 0.0
    for t, (st, a) in enumerate(visits):
        G = -(T - t)
        g1 += G * (a - p)                                 # REINFORCE estimate of dJ/dh
        g2 += (G - v[st]) * (a - p)                       # the same with baseline b(s) = v(s)
    plain.append(g1)
    with_base.append(g2)

print("true gradient dJ/dh:", round(true_grad, 2))
print("without baseline: average", round(np.mean(plain), 2), " standard deviation", round(np.std(plain), 2))
print("with baseline   : average", round(np.mean(with_base), 2), " standard deviation", round(np.std(with_base), 2))
print("Both averages agree with the true gradient up to sampling error. The baseline only removes noise.")
''', long=True)

K.code('actor_critic_cliff', r'''
import numpy as np

# One step actor critic on the cliff walk from chapter 2.3 (4 by 12 grid, -1 per move, -100 and back to start for a fall).
# Actor: softmax preferences theta[s, a]. Critic: state values V[s]. The critic's TD error tells the actor how good the action was.
ROWS, COLS, START, GOAL = 4, 12, 36, 47
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]               # up, down, left, right

def step(s, a):
    r, c = divmod(s, COLS)
    r = min(ROWS - 1, max(0, r + MOVES[a][0]))
    c = min(COLS - 1, max(0, c + MOVES[a][1]))
    if r == ROWS - 1 and 1 <= c <= COLS - 2:
        return START, -100, False                         # fell off the cliff
    s2 = r * COLS + c
    return s2, -1, s2 == GOAL

rng = np.random.default_rng(0)
theta = np.zeros((ROWS * COLS, 4))
V = np.zeros(ROWS * COLS)
alpha_actor, alpha_critic = 0.1, 0.5
rewards = []
for ep in range(500):
    s, total = START, 0
    for t in range(1000):
        prefs = theta[s] - theta[s].max()
        pi = np.exp(prefs) / np.exp(prefs).sum()
        a = rng.choice(4, p=pi)
        s2, r, done = step(s, a)
        delta = r + (0 if done else V[s2]) - V[s]         # TD error: the advantage estimate
        V[s] += alpha_critic * delta                      # critic: TD(0)
        grad = -pi
        grad[a] += 1
        theta[s] += alpha_actor * delta * grad            # actor: policy gradient step with the TD error in place of G
        total += r
        s = s2
        if done:
            break
    rewards.append(total)

s, path = START, [START]
while s != GOAL and len(path) < 50:                       # follow the most likely action from each cell
    s = step(s, int(np.argmax(theta[s])))[0]
    path.append(s)
rows_used = sorted({p // COLS for p in path})
print("average reward per block of 100 episodes:", [round(float(np.mean(rewards[i:i + 100])), 1) for i in range(0, 500, 100)])
print("most likely path:", len(path) - 1, "moves, using rows", rows_used, "(row 3 is the bottom row with the cliff)")
''', long=True)

K.code('ppo_cartpole', r'''
import numpy as np

# PPO with the clipped objective on CartPole. Policy: pi(right | s) = sigmoid(theta . s), only 4 weights.
# Critic: a least squares fit of the return on simple features. Each batch of data is reused for several epochs.
def cart_step(s, a):                                      # the same physics as before
    x, v, th, om = s
    force = 10.0 if a == 1 else -10.0
    cos, sin = np.cos(th), np.sin(th)
    tmp = (force + 0.05 * om * om * sin) / 1.1
    alpha = (9.8 * sin - cos * tmp) / (0.5 * (4 / 3 - 0.1 * cos * cos / 1.1))
    acc = tmp - 0.05 * alpha * cos / 1.1
    s = np.array([x + 0.02 * v, v + 0.02 * acc, th + 0.02 * om, om + 0.02 * alpha])
    return s, abs(s[0]) > 2.4 or abs(s[2]) > 0.2095

feats = lambda S: np.hstack([np.ones((len(S), 1)), S, S ** 2])   # critic features: 1, s and s squared
sigmoid = lambda z: 1 / (1 + np.exp(-z))
def train(use_clip, seed=0, gamma=0.99, lam=0.95, clip=0.2, lr=2.0):
    rng = np.random.default_rng(seed)
    theta, w = np.zeros(4), np.zeros(9)
    for it in range(1, 16):
        S, A, R, D, lengths = [], [], [], [], []
        while len(S) < 1000:                                  # collect a batch of about 1000 steps with the current policy
            s, done, t = rng.uniform(-0.05, 0.05, 4), False, 0
            while not done and t < 200:
                a = int(rng.random() < sigmoid(theta @ s))
                s2, done = cart_step(s, a)
                S.append(s); A.append(a); R.append(1.0); D.append(done or t == 199)
                s, t = s2, t + 1
            lengths.append(t)
        S, A, R, D = np.array(S), np.array(A), np.array(R), np.array(D)
        V = feats(S) @ w
        adv, ret, gae = np.zeros(len(S)), np.zeros(len(S)), 0.0
        for t in reversed(range(len(S))):                     # generalised advantage estimation
            next_v = 0.0 if D[t] else V[t + 1]
            delta = R[t] + gamma * next_v - V[t]
            gae = delta + (0.0 if D[t] else gamma * lam * gae)
            adv[t], ret[t] = gae, gae + V[t]
        adv = (adv - adv.mean()) / (adv.std() + 1e-8)
        p_old = np.where(A == 1, sigmoid(S @ theta), 1 - sigmoid(S @ theta))
        for epoch in range(10):                               # reuse the same batch 10 times
            p1 = sigmoid(S @ theta)
            p_new = np.where(A == 1, p1, 1 - p1)
            ratio = p_new / p_old
            if use_clip:                                  # outside the clip range the gradient is 0
                active = ((adv > 0) & (ratio < 1 + clip)) | ((adv < 0) & (ratio > 1 - clip))
            else:
                active = np.ones(len(S))
            grad_logp = (A - p1)[:, None] * S
            theta += lr * ((active * adv * ratio)[:, None] * grad_logp).mean(axis=0)
        w = np.linalg.lstsq(feats(S), ret, rcond=None)[0]     # refit the critic
        if it in (1, 5, 10, 15):
            print(f"  iteration {it:2d}: average episode length {np.mean(lengths):6.1f}, ratios in the 10th epoch from {ratio.min():.2f} to {ratio.max():.2f}")

for use_clip in [True, False]:
    print("PPO with the clip (epsilon = 0.2):" if use_clip else "The same without the clip:")
    train(use_clip)
''', long=True)

K.lesson('idea', 'Learning the policy directly: REINFORCE', f'''
{src('Sutton and Barto (2018) sections 13.1 to 13.3 and example 13.1, and Williams, Simple statistical gradient-following algorithms (1992).')}
{viz('mlcorridorpg')}
{wwh('A <b>policy gradient</b> method keeps a parameterised policy &pi;(a|s, &theta;), for example a softmax over action preferences, and adjusts &theta; by gradient ascent on the expected return J(&theta;). It needs no value table to choose actions. <b>REINFORCE</b> is the simplest such method: after each episode it raises the log probability of every action taken in proportion to the return that followed.',
     'Policies can be simpler than value functions, they handle continuous actions naturally, and they can learn <b>stochastic</b> policies. In the short corridor the agent cannot tell its states apart, and the best policy presses right with probability 0.59. A greedy value based method can only press always right or always left, and both never finish.',
     'Run an episode with the current policy. For each step t compute the return G<sub>t</sub> and update &theta; += &alpha;G<sub>t</sub>&nabla;ln &pi;(A<sub>t</sub>|S<sub>t</sub>, &theta;). For a softmax policy the gradient of ln &pi;(a) with respect to the preferences is one hot(a) minus the probabilities.')}
{run('reinforce_corridor')}
{note('Solving the Bellman equations for every p shows the best policy is p(right) = 0.59, worth &minus;11.66 per episode, while p = 0.5 is worth &minus;12. REINFORCE starts at 0.5 and, averaged over its last 500 episodes, sits at p = 0.593. Single episodes are noisy, so p wanders around the best value.', 'exam')}
{fxs(fx('Softmax policy', '&pi;(a|s, &theta;) = e<sup>h(s, a, &theta;)</sup> / &Sigma;<sub>b</sub> e<sup>h(s, b, &theta;)</sup>', 'h are action preferences.', key=True),
     fx('REINFORCE update', '&theta; &larr; &theta; + &alpha; G<sub>t</sub> &nabla; ln &pi;(A<sub>t</sub>|S<sub>t</sub>, &theta;)', 'Monte Carlo policy gradient, Williams (1992).', key=True),
     fx('Softmax log gradient', '&nabla;<sub>h</sub> ln &pi;(a) = one hot(a) &minus; &pi;', 'For two actions: a &minus; p.', key=True))}
{link('ai', 'Seen policy search in the Artificial Intelligence subject?', 'The AI subject introduces policy search from the Russell and Norvig point of view. This chapter derives the policy gradient theorem and builds REINFORCE, actor critic and PPO in code.', 'Open Artificial Intelligence')}
''', kw=['policy gradient', 'REINFORCE', 'softmax policy', 'stochastic policy', 'short corridor', 'Williams'])

K.lesson('theorem', 'The policy gradient theorem and baselines', f'''
{src('Sutton, McAllester, Singh and Mansour (NeurIPS 1999), and Sutton and Barto (2018) sections 13.2 and 13.4.')}
{wwh('The <b>policy gradient theorem</b> gives the gradient of J without differentiating the state distribution: it is the expected value of q<sub>&pi;</sub>(s, a)&nabla;ln &pi;(a|s). Subtracting any <b>baseline</b> b(s) that does not depend on the action leaves this expectation unchanged but can make each sample far less noisy.',
     'Changing the policy changes which states are visited, and that effect is hard to compute. The theorem shows we can ignore it, which is what makes sampling the gradient possible. Raw returns are very noisy, so a good baseline, usually the state value v(s), is the cheapest way to speed up learning.',
     'Use G<sub>t</sub> &minus; b(S<sub>t</sub>) in place of G<sub>t</sub>. A learned v&#770;(s, <b>w</b>) is the usual choice, trained like gradient Monte Carlo. The quantity G<sub>t</sub> &minus; v(S<sub>t</sub>) estimates the <b>advantage</b>: how much better this action was than the policy’s average.')}
{run('baseline_variance')}
{note('For the fixed policy p = 0.3 the true gradient is 8.48. Over 20,000 episodes the plain REINFORCE estimate averages 8.53 with a standard deviation of 39.65, and with the baseline b(s) = v(s) it averages 8.59 with a standard deviation of 25.33. Same direction on average, about 36% less noise per episode.', 'exam')}
{steps('Why a baseline adds no bias', [
    'The extra term is E<sub>a ~ &pi;</sub>[b(s)&nabla;ln &pi;(a|s)] = b(s) &Sigma;<sub>a</sub> &pi;(a|s)&nabla;ln &pi;(a|s).',
    eq('&pi; &nabla;ln &pi; = &nabla;&pi;, so the sum is b(s) &nabla; &Sigma;<sub>a</sub> &pi;(a|s)'),
    eq('&Sigma;<sub>a</sub> &pi;(a|s) = 1 for every &theta;, so its gradient is 0'),
    'The baseline term averages to exactly 0. It only changes the noise, never the expected direction.'])}
{fxs(fx('Policy gradient theorem', '&nabla;J(&theta;) &prop; &Sigma;<sub>s</sub> &mu;(s) &Sigma;<sub>a</sub> q<sub>&pi;</sub>(s, a) &nabla;&pi;(a|s, &theta;)', 'No derivative of &mu;(s) needed.', key=True),
     fx('Score function form', '&nabla;J(&theta;) = E<sub>&pi;</sub>[G<sub>t</sub> &nabla;ln &pi;(A<sub>t</sub>|S<sub>t</sub>, &theta;)]', 'Uses the log derivative trick &nabla;&pi; = &pi;&nabla;ln &pi;.', key=True),
     fx('With baseline', '&theta; += &alpha;(G<sub>t</sub> &minus; b(S<sub>t</sub>))&nabla;ln &pi;(A<sub>t</sub>|S<sub>t</sub>, &theta;)', 'Unbiased for any b that ignores the action.', key=True))}
''', kw=['policy gradient theorem', 'baseline', 'variance reduction', 'advantage', 'log derivative trick', 'score function'])

K.lesson('ac', 'Actor critic methods', f'''
{src('Sutton and Barto (2018) section 13.5, Konda and Tsitsiklis (NeurIPS 1999), Mnih and colleagues, Asynchronous methods for deep RL (ICML 2016), and Schulman and colleagues, Generalized advantage estimation (ICLR 2016).')}
{wwh('An <b>actor critic</b> method learns two things: the <b>actor</b> is the policy, and the <b>critic</b> is a value function. After each step the critic’s TD error &delta; = r + &gamma;v&#770;(s&prime;) &minus; v&#770;(s) tells the actor whether the action turned out better or worse than expected, and the actor moves in that direction.',
     'REINFORCE must wait for the end of an episode and suffers from noisy returns. Bootstrapping from the critic lets the actor learn after every step, with much lower variance, at the cost of some bias from an imperfect critic. A2C, A3C, PPO, DDPG and SAC are all actor critic methods.',
     'Each step: compute &delta;, update the critic <b>w</b> += &alpha;<sub>w</sub>&delta;&nabla;v&#770;(s), and update the actor &theta; += &alpha;<sub>&theta;</sub>&delta;&nabla;ln &pi;(a|s). In deep RL both are networks, often sharing layers. <b>Generalised advantage estimation</b> (GAE) mixes n step advantages with a parameter &lambda; to trade bias against variance.')}
{run('actor_critic_cliff')}
{note('On the cliff walk from chapter 2.3, a tabular actor critic improves from an average reward of &minus;47.1 in its first 100 episodes to about &minus;19 in later blocks. Its most likely path takes 19 moves and visits every row, keeping well away from the cliff edge, much like SARSA. Like SARSA it learns about the policy it actually follows, and as its policy sharpens it explores less, so it earns more than SARSA’s &minus;24.42 while learning.', 'exam')}
{table(['Method', 'Year', 'Key idea'], [
    ['A3C', '2016', 'Many actors run in parallel threads and update a shared network asynchronously'],
    ['A2C', '2016 onwards', 'The synchronous version of A3C: wait for all actors, then one batched update'],
    ['GAE', '2016', 'Advantage = sum of (&gamma;&lambda;)<sup>l</sup> &delta;<sub>t+l</sub>, &lambda; trades bias for variance'],
    ['TRPO', '2015', 'Limit each update by a KL divergence constraint, a trust region'],
    ['PPO', '2017', 'Keep updates small with a clipped probability ratio, simple and robust']])}
{fxs(fx('One step actor critic', '&theta; += &alpha;<sub>&theta;</sub> &delta; &nabla;ln &pi;(A|S, &theta;), &nbsp; &delta; = R + &gamma;v&#770;(S&prime;, <b>w</b>) &minus; v&#770;(S, <b>w</b>)', 'The TD error estimates the advantage.', key=True),
     fx('GAE', 'A&#770;<sub>t</sub> = &Sigma;<sub>l &ge; 0</sub> (&gamma;&lambda;)<sup>l</sup> &delta;<sub>t+l</sub>', '&lambda; = 0 gives the one step TD error, &lambda; = 1 the Monte Carlo advantage.', key=True))}
''', kw=['actor critic', 'critic', 'TD error advantage', 'A2C', 'A3C', 'GAE', 'TRPO'])

K.lesson('ppo', 'PPO: small, safe policy updates', f'''
{src('Schulman and colleagues, Trust Region Policy Optimization (ICML 2015) and Proximal Policy Optimization Algorithms (2017), and Ouyang and colleagues, Training language models to follow instructions with human feedback (2022).')}
{viz('mlppoclip')}
{wwh('<b>Proximal policy optimisation</b> (PPO) collects a batch with the current policy, then takes several epochs of gradient steps on that batch. To stop the new policy drifting too far from the one that collected the data, it clips the probability ratio r = &pi;<sub>new</sub>(a|s) / &pi;<sub>old</sub>(a|s) to [1 &minus; &epsilon;, 1 + &epsilon;] inside a pessimistic minimum.',
     'Plain policy gradient uses each sample once and can collapse after one large step. TRPO solved this with a KL constraint but needs second order optimisation. PPO gets most of the benefit with a few lines of code. It became the default on policy algorithm and was used for OpenAI Five and for the RLHF stage of InstructGPT.',
     'Compute advantages with GAE and normalise them. For K epochs, maximise the average of min(r A, clip(r, 1 &minus; &epsilon;, 1 + &epsilon;) A), with &epsilon; = 0.2 in the paper, plus a value loss and often an entropy bonus. Samples on the flat part of the minimum give no gradient.')}
{run('ppo_cartpole')}
{note('With the clip, average episode length grows from 23.4 to 172.8 in 15 iterations of about 1000 steps, reusing each batch 10 times. The ratios still leave [0.8, 1.2] a little, because the clip only silences samples already outside the range while the others keep pushing. Without the clip this easy, linear problem also learns, but the ratios swing from 0.11 to 1.92 in the first iteration: the new policy moves far from the data, which with neural networks often ends in collapse.', 'exam')}
{fxs(fx('PPO clipped objective', 'L(&theta;) = E[min(r<sub>t</sub>(&theta;)A&#770;<sub>t</sub>, clip(r<sub>t</sub>(&theta;), 1 &minus; &epsilon;, 1 + &epsilon;)A&#770;<sub>t</sub>)]', 'r<sub>t</sub> = &pi;<sub>&theta;</sub>(a<sub>t</sub>|s<sub>t</sub>) / &pi;<sub>old</sub>(a<sub>t</sub>|s<sub>t</sub>).', key=True),
     fx('TRPO', 'max E[r<sub>t</sub>A&#770;<sub>t</sub>] subject to E[KL(&pi;<sub>old</sub> || &pi;<sub>&theta;</sub>)] &le; &delta;', 'A trust region on the policy.', key=True),
     fx('Full PPO loss', 'L = L<sup>CLIP</sup> &minus; c<sub>1</sub>(V<sub>&theta;</sub>(s) &minus; V<sup>target</sup>)<sup>2</sup> + c<sub>2</sub> H(&pi;<sub>&theta;</sub>)', 'Value loss and entropy bonus.'))}
''', kw=['PPO', 'proximal policy optimization', 'clipped objective', 'probability ratio', 'TRPO', 'KL divergence', 'RLHF'])

K.lesson('continuous', 'Continuous actions: Gaussian policies, DDPG, TD3 and SAC', f'''
{src('Sutton and Barto (2018) section 13.7, Silver and colleagues, Deterministic policy gradient algorithms (ICML 2014), Lillicrap and colleagues (ICLR 2016), Fujimoto, van Hoof and Meger (ICML 2018), and Haarnoja and colleagues (ICML 2018).')}
{wwh('For a continuous action such as a motor torque, a policy can output the mean &mu;(s) and standard deviation &sigma;(s) of a <b>Gaussian</b>, and the agent samples from it. Off policy actor critic methods for continuous control learn a Q function as the critic: <b>DDPG</b> uses a deterministic actor, <b>TD3</b> fixes its overestimation, and <b>SAC</b> adds an entropy bonus to keep exploring.',
     'Robots, cars and many control problems have continuous actions, where taking a max over actions, as Q learning does, is itself an optimisation problem. These methods reuse replay data, so they need far fewer environment steps than on policy methods such as PPO.',
     'Gaussian policy: &nabla;<sub>&mu;</sub> ln &pi;(a|s) = (a &minus; &mu;) / &sigma;<sup>2</sup>. DDPG: the actor follows &nabla;<sub>a</sub>Q(s, a) through the action. TD3: two critics and take the smaller, delay actor updates, and add noise to target actions. SAC: maximise reward plus &alpha; times the policy’s entropy.')}
{table(['Method', 'Policy', 'On or off policy', 'Key trick'], [
    ['REINFORCE', 'Stochastic', 'On', 'Monte Carlo returns'],
    ['PPO', 'Stochastic', 'On', 'Clipped ratio, several epochs per batch'],
    ['DDPG', 'Deterministic plus noise', 'Off', 'Deterministic policy gradient through Q'],
    ['TD3', 'Deterministic plus noise', 'Off', 'Clipped double Q, delayed actor, target smoothing'],
    ['SAC', 'Stochastic', 'Off', 'Maximum entropy objective']])}
{fxs(fx('Gaussian policy gradient', '&nabla;<sub>&mu;</sub> ln &pi;(a|s) = (a &minus; &mu;(s)) / &sigma;(s)<sup>2</sup>', 'Push the mean towards good actions.', key=True),
     fx('Deterministic policy gradient', '&nabla;J = E[&nabla;<sub>a</sub>Q(s, a)|<sub>a = &mu;(s)</sub> &nabla;<sub>&theta;</sub>&mu;(s)]', 'Silver and colleagues (2014).'),
     fx('Maximum entropy objective', 'J(&pi;) = E[&Sigma;<sub>t</sub> r<sub>t</sub> + &alpha; H(&pi;(&middot;|s<sub>t</sub>))]', 'SAC.'))}
''', kw=['continuous actions', 'Gaussian policy', 'DDPG', 'TD3', 'SAC', 'deterministic policy gradient', 'maximum entropy'])

K.lesson('versus', 'Value based, policy based and actor critic compared', f'''
{versus('Three families of RL methods', ['', 'Value based (DQN)', 'Policy based (REINFORCE)', 'Actor critic (PPO, SAC)'], [
    ['Learns', 'Q(s, a)', '&pi;(a|s)', 'Both &pi; and V or Q'],
    ['Actions', 'Discrete, needs a max', 'Discrete or continuous', 'Discrete or continuous'],
    ['Stochastic policies', 'No, greedy plus &epsilon;', 'Yes', 'Yes'],
    ['Variance', 'Low', 'High', 'Medium'],
    ['Sample efficiency', 'Good, uses replay', 'Poor, on policy', 'PPO medium, SAC good']],
    'use DQN style methods for discrete actions and plenty of logged data, PPO as a robust default, and SAC or TD3 for continuous control when samples are expensive.')}
''', kw=['value based vs policy based', 'actor critic comparison', 'choosing an RL algorithm'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Objective', 'J(&theta;) = v<sub>&pi;<sub>&theta;</sub></sub>(s<sub>0</sub>) = E<sub>&pi;<sub>&theta;</sub></sub>[G<sub>0</sub>]', 'Expected return from the start.', key=True),
     fx('Log derivative trick', '&nabla;<sub>&theta;</sub> &pi;(a|s, &theta;) = &pi;(a|s, &theta;) &nabla;<sub>&theta;</sub> ln &pi;(a|s, &theta;)', 'Turns a gradient of a sum into an expectation.', key=True),
     fx('REINFORCE with baseline', '&theta; += &alpha;(G<sub>t</sub> &minus; b(S<sub>t</sub>))&nabla;ln &pi;(A<sub>t</sub>|S<sub>t</sub>)', 'Unbiased, lower variance.', key=True),
     fx('Advantage', 'A(s, a) = q<sub>&pi;</sub>(s, a) &minus; v<sub>&pi;</sub>(s)', 'Estimated by the TD error or by GAE.', key=True),
     fx('GAE', 'A&#770;<sub>t</sub> = &delta;<sub>t</sub> + &gamma;&lambda;A&#770;<sub>t+1</sub>', 'Computed backwards through a batch.'),
     fx('PPO clip', 'min(rA, clip(r, 1 &minus; &epsilon;, 1 + &epsilon;)A)', 'No gradient where the minimum is flat.'))}
{steps('Worked example: one REINFORCE step for two actions', [
    'Preference h = 0, so p(right) = 0.5. The agent pressed right (a = 1) and the return from that step was G = &minus;4. Step size &alpha; = 0.1.',
    eq('&nabla;<sub>h</sub> ln &pi;(right) = a &minus; p = 1 &minus; 0.5 = 0.5'),
    eq('h += 0.1 &times; (&minus;4) &times; 0.5 = &minus;0.2, so p(right) falls to 0.450'),
    'With a baseline b = &minus;6, the same step uses G &minus; b = 2, so h += 0.1 &times; 2 &times; 0.5 = +0.1 and p(right) rises to 0.525.',
    'Without a baseline every return here is negative, so every action taken is pushed down, and only the size of the push separates good from bad. The baseline makes better than average actions go up and worse ones go down.'])}
{deep('Natural gradients and why trust regions work', '<p>Ordinary gradient ascent measures a step by how far &theta; moves, but two policies with nearby parameters can behave very differently, and two with distant parameters can behave alike. The <b>natural policy gradient</b> (Kakade 2001) measures the step by how much the policy itself changes, using the KL divergence. To second order, KL(&pi;<sub>&theta;</sub> || &pi;<sub>&theta;+&Delta;</sub>) &asymp; &frac12;&Delta;<sup>T</sup>F&Delta;, where F is the Fisher information matrix, so the natural gradient is F<sup>&minus;1</sup>&nabla;J. TRPO takes the largest natural gradient step whose average KL stays below &delta;, using conjugate gradients to avoid forming F, and it comes with a bound that guarantees improvement of a lower bound on J. PPO drops the second order machinery and keeps only the idea of staying close, through the clip.</p>')}
''', kw=['log derivative trick', 'advantage', 'GAE formula', 'natural gradient', 'Fisher information'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Instead of scoring every action, the agent keeps a set of probabilities for what to do and nudges them up for actions that worked out well and down for those that did not.</p>',
    '<p>Implement REINFORCE with and without a baseline, a tabular actor critic, and PPO with the clipped objective and GAE.</p>',
    '<p>Derive the policy gradient theorem, prove that baselines add no bias, explain GAE’s bias and variance trade off, and compare PPO, TRPO, DDPG, TD3 and SAC.</p>',
    '<p>Study natural gradients and the Fisher matrix, monotonic improvement bounds, convergence of policy gradient for softmax policies, and the implementation details that decide PPO results in practice.</p>')}
{grow('Explain how an agent can learn its probabilities of acting directly.',
      'Build and tune policy gradient and actor critic agents.',
      'Analyse variance, bias and stability in policy optimisation.')}
''', kw=['beginner', 'expert', 'natural gradient', 'PPO implementation details'])

lc(2016, 'Maximum Difference Between Increasing Elements', 'maximum-difference-between-increasing-elements', 'e', 'Track the smallest value seen so far', 'Walk left to right, keep the minimum so far, and record the largest value minus that minimum when it is positive. Comparing a value with a reference level is what an advantage does: it compares a return with the baseline.', r"""
def maximum_difference(nums):
    best, low = -1, nums[0]
    for x in nums[1:]:
        if x > low:
            best = max(best, x - low)
        low = min(low, x)
    return best
""", [('maximum_difference([7, 1, 5, 4])', 4), ('maximum_difference([9, 4, 3, 2])', -1), ('maximum_difference([1, 5, 2, 10])', 9)])
lc(55, 'Jump Game', 'jump-game', 'm', 'Keep the furthest index you can reach', 'Scan once, updating the furthest reachable index. If you ever stand beyond it, you are stuck. Like the short corridor, whether you can reach the goal depends on which moves are allowed in each cell.', r"""
def can_jump(nums):
    reach = 0
    for i, n in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + n)
    return True
""", [('can_jump([2, 3, 1, 1, 4])', True), ('can_jump([3, 2, 1, 0, 4])', False), ('can_jump([0])', True)])
lc(45, 'Jump Game II', 'jump-game-ii', 'm', 'Greedy breadth first search by layers', 'Treat each jump as a layer: from the current range find the furthest next reach, and count a jump each time you pass the end of the range. The answer is the shortest number of moves, the same as minus the best return when every move costs 1.', r"""
def jump(nums):
    jumps, end, far = 0, 0, 0
    for i in range(len(nums) - 1):
        far = max(far, i + nums[i])
        if i == end:
            jumps += 1
            end = far
    return jumps
""", [('jump([2, 3, 1, 1, 4])', 2), ('jump([2, 3, 0, 1, 4])', 2), ('jump([1])', 0)])
lc(1696, 'Jump Game VI', 'jump-game-vi', 'm', 'Dynamic programming with a sliding window maximum', 'The best score at i is nums[i] plus the best score among the previous k cells. A deque of indices with decreasing scores gives that maximum in constant time. Adding the reward now to the best value reachable next is a Bellman backup.', r"""
from collections import deque


def max_result(nums, k):
    score = [0] * len(nums)
    score[0] = nums[0]
    dq = deque([0])
    for i in range(1, len(nums)):
        while dq[0] < i - k:
            dq.popleft()
        score[i] = nums[i] + score[dq[0]]
        while dq and score[dq[-1]] <= score[i]:
            dq.pop()
        dq.append(i)
    return score[-1]
""", [('max_result([1, -1, -2, 4, -7, 3], 2)', 7), ('max_result([10, -5, -2, 4, 0, 3], 3)', 17), ('max_result([1, -5, -20, 4, -1, 3, -6, -3], 2)', 0)])
lc(1345, 'Jump Game IV', 'jump-game-iv', 'h', 'Breadth first search, and clear each value’s list after first use', 'From index i you may step to i &minus; 1, i + 1 or any index with the same value. Breadth first search finds the fewest steps. Emptying a value’s index list once used stops the search from scanning it again. Shortcuts that connect distant states make credit travel fast, which is why the same idea appears in options and skills in hierarchical RL.', r"""
from collections import defaultdict, deque


def min_jumps(arr):
    n = len(arr)
    same = defaultdict(list)
    for i, v in enumerate(arr):
        same[v].append(i)
    seen = {0}
    q = deque([(0, 0)])
    while q:
        i, d = q.popleft()
        if i == n - 1:
            return d
        for j in same[arr[i]] + [i - 1, i + 1]:
            if 0 <= j < n and j not in seen:
                seen.add(j)
                q.append((j, d + 1))
        same[arr[i]] = []
    return -1
""", [('min_jumps([100, -23, -23, 404, 100, 23, 23, 23, 3, 404])', 3), ('min_jumps([7])', 0), ('min_jumps([7, 6, 9, 6, 9, 6, 9, 7])', 1)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Policy learning is about which moves lead where, and how good a result is compared with a reference. These problems practise a value against a running minimum, reachability, fewest moves, a Bellman style recurrence with a sliding maximum, and breadth first search with shortcuts. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'jump game', 'greedy', 'sliding window maximum', 'breadth first search'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Policy gradient</b> methods learn &pi;(a|s, &theta;) directly by gradient ascent on the expected return, and can learn <b>stochastic</b> and continuous policies.',
    '<b>REINFORCE</b>: &theta; += &alpha;G<sub>t</sub>&nabla;ln &pi;(A<sub>t</sub>|S<sub>t</sub>). In the short corridor it finds the best p(right) of 0.59.',
    'The <b>policy gradient theorem</b> removes the need to differentiate the state distribution. A <b>baseline</b> leaves the gradient unbiased and cuts its noise.',
    '<b>Actor critic</b>: the critic’s TD error replaces the return. GAE blends n step advantages with &lambda;.',
    '<b>PPO</b> reuses each batch for several epochs and clips the probability ratio to keep updates small. TRPO uses a KL trust region.',
    'Continuous control: Gaussian policies, <b>DDPG</b>, <b>TD3</b> and <b>SAC</b>.'],
    'Reinforcement 3.3 looks at RL in practice: models and planning, learning from fixed datasets, RLHF for language models, and safety.')}
{files('Three tasks: the softmax log gradient, generalised advantage estimates, and the PPO clipped objective.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'A policy gradient method adjusts', ['A Q table', 'The parameters of the policy itself, by gradient ascent on the expected return', 'The reward function', 'The discount factor'], 1, 'Learn &pi;(a|s, &theta;).', 'No value table is needed to act.')
K.quiz('e', 'REINFORCE updates the policy', ['After every step using a critic', 'After each episode, using the returns that followed each action', 'Only at the start', 'Without any rewards'], 1, 'Monte Carlo.', 'Williams (1992).')
K.quiz('e', 'For a softmax policy, the gradient of ln &pi;(a) with respect to the preferences is', ['&pi;', 'one hot(a) minus &pi;', 'Always 1', 'Zero'], 1, 'Indicator minus probabilities.', 'For two actions it is a &minus; p.')
K.quiz('e', 'In an actor critic method, the critic', ['Chooses actions', 'Estimates values and tells the actor how good an action turned out', 'Stores the replay memory', 'Sets the reward'], 1, 'Value function.', 'Its TD error drives the actor.')
K.quiz('m', 'Why can a policy gradient method solve the short corridor while greedy Q learning with the same features cannot?', ['It uses more memory', 'It can learn a stochastic policy, and the best policy here is random with p(right) = 0.59', 'It sees the true state', 'It ignores rewards'], 1, 'Deterministic policies never finish.', 'Always right or always left both loop forever.')
K.quiz('m', 'Subtracting a baseline b(s) from the return', ['Biases the gradient', 'Keeps the expected gradient the same and can reduce its variance', 'Doubles the step size', 'Removes exploration'], 1, '&Sigma;<sub>a</sub> &nabla;&pi; = 0.', 'The best simple choice is v(s).')
K.quiz('m', 'The advantage A(s, a) is', ['The reward', 'q(s, a) &minus; v(s): how much better an action is than the policy’s average', 'The return', 'The KL divergence'], 1, 'Relative value.', 'Estimated by the TD error or GAE.')
K.quiz('m', 'In GAE, setting &lambda; = 0 gives', ['The Monte Carlo advantage', 'The one step TD error', 'Zero advantage', 'The reward only'], 1, 'Only the first term survives.', '&lambda; = 1 gives G &minus; V.')
K.quiz('m', 'PPO’s clip range in the original paper was', ['&epsilon; = 0.01', '&epsilon; = 0.2', '&epsilon; = 1', '&epsilon; = 5'], 1, 'Schulman and colleagues (2017).', 'Ratios outside [0.8, 1.2] stop contributing gradient in the helpful direction.')
K.quiz('h', 'For a sample with A &gt; 0 and ratio r = 1.5, with &epsilon; = 0.2, the PPO objective', ['Has a large gradient', 'Is flat at 1.2A, so this sample gives no gradient', 'Becomes negative', 'Is undefined'], 1, 'Clipped above 1 + &epsilon;.', 'The policy already moved far enough in the good direction.')
K.quiz('h', 'TD3 improves DDPG by', ['Using a stochastic policy', 'Taking the smaller of two critics, delaying actor updates and smoothing target actions', 'Removing the critic', 'Using Monte Carlo returns'], 1, 'Three tricks.', 'Fujimoto, van Hoof and Meger (2018).')
K.quiz('h', 'SAC differs from DDPG mainly by', ['Being on policy', 'Maximising reward plus an entropy bonus with a stochastic policy', 'Having no critic', 'Using tables'], 1, 'Maximum entropy RL.', 'It keeps exploring by design.')
K.quiz('x', 'In the style of a Berkeley CS285 exam: the policy gradient theorem is useful because', ['It removes the need for rewards', 'The gradient of J does not require the derivative of the state distribution', 'It makes J convex', 'It removes variance'], 1, 'Sutton and colleagues (1999).', 'Sampling states from the current policy is enough.')
K.quiz('x', 'In the style of a Stanford CS234 exam: TRPO measures the size of a policy update by', ['The parameter distance', 'The average KL divergence between the old and new policies', 'The reward change', 'The number of epochs'], 1, 'A trust region in policy space.', 'To second order this uses the Fisher information matrix.')

K.calc('e', 'Two actions with preferences [1, 0]. Probability of the first action under softmax?', '0.731', 'e / (e + 1).', ['e<sup>1</sup> = 2.718, e<sup>0</sup> = 1.', 'Sum 3.718.', eq('2.718 / 3.718 = 0.731')], check=0.7311, tol=0.002)
K.calc('e', 'Softmax policy gives the chosen action probability 0.7. Gradient of ln &pi; with respect to that action’s own preference?', '0.3', '1 &minus; &pi;(a).', ['one hot entry 1.', 'Subtract 0.7.', eq('1 &minus; 0.7 = 0.3')], check=0.3)
K.calc('m', 'h = 0 (p = 0.5), action right, return G = &minus;4, &alpha; = 0.1. New preference h?', '-0.2', 'h += &alpha;G(a &minus; p).', ['a &minus; p = 0.5.', '0.1 &times; (&minus;4) &times; 0.5.', eq('h = &minus;0.2')], check=-0.2)
K.calc('m', 'Same step with baseline b = &minus;6. New preference h?', '0.1', 'Use G &minus; b.', ['G &minus; b = &minus;4 + 6 = 2.', '0.1 &times; 2 &times; 0.5.', eq('h = 0.1')], check=0.1)
K.calc('m', 'Short corridor with p(right) = 0.5. Using v<sub>1</sub> = (&minus;2 &minus; q)/(1 &minus; p &minus; q<sup>2</sup>) and v<sub>0</sub> = v<sub>1</sub> &minus; 1/p, the start value?', '-12', 'q = 1 &minus; p.', ['q = 0.5, denominator 1 &minus; 0.5 &minus; 0.25 = 0.25.', 'v<sub>1</sub> = &minus;2.5 / 0.25 = &minus;10.', eq('v<sub>0</sub> = &minus;10 &minus; 2 = &minus;12')], check=-12)
K.calc('m', 'Critic values V(s) = &minus;10, V(s&prime;) = &minus;8, reward &minus;1, &gamma; = 1. TD error used by the actor?', '1', 'r + &gamma;V(s&prime;) &minus; V(s).', ['Target &minus;1 &minus; 8 = &minus;9.', 'Subtract &minus;10.', eq('&delta; = 1')], check=1)
K.calc('h', 'TD errors &delta;<sub>0</sub> = 1 and &delta;<sub>1</sub> = 0.5 (then the episode ends), &gamma; = 0.9, &lambda; = 0.8. GAE at t = 0?', '1.36', 'A<sub>0</sub> = &delta;<sub>0</sub> + &gamma;&lambda;&delta;<sub>1</sub>.', ['&gamma;&lambda; = 0.72.', '0.72 &times; 0.5 = 0.36.', eq('1 + 0.36 = 1.36')], check=1.36)
K.calc('h', 'PPO with &epsilon; = 0.2: ratio r = 1.3 and advantage A = 2. Objective for this sample?', '2.4', 'min(rA, clip(r)A).', ['rA = 2.6.', 'clip(1.3) = 1.2, so 2.4.', eq('min(2.6, 2.4) = 2.4')], check=2.4)
K.calc('h', 'PPO with &epsilon; = 0.2: ratio r = 0.7 and A = &minus;1. Objective for this sample?', '-0.8', 'Minimum of the two terms.', ['rA = &minus;0.7.', 'clip(0.7) = 0.8, so &minus;0.8.', eq('min(&minus;0.7, &minus;0.8) = &minus;0.8')], check=-0.8)
K.calc('x', 'In the style of a Berkeley CS285 problem: Gaussian policy with &mu; = 0.5, &sigma; = 0.5, sampled action a = 1. Gradient of ln &pi; with respect to &mu;?', '2', '(a &minus; &mu;)/&sigma;<sup>2</sup>.', ['a &minus; &mu; = 0.5.', '&sigma;<sup>2</sup> = 0.25.', eq('0.5 / 0.25 = 2')], check=2)

K.assign('softmax_log_grad', 'e', 'The softmax log gradient',
         '<p>Write <code>softmax_log_grad(prefs, a)</code> that returns the gradient of ln &pi;(a) with respect to each preference for a softmax policy: one hot(a) minus the probabilities. Round each value to 4 decimals.</p>',
         """
def softmax_log_grad(prefs, a):
    # your code here
    pass
""", [('softmax_log_grad([0.0, 0.0], 1)', [-0.5, 0.5]), ('softmax_log_grad([1.0, 0.0], 0)', [0.2689, -0.2689]), ('softmax_log_grad([0.0, 0.0, 0.0, 0.0], 2)', [-0.25, -0.25, 0.75, -0.25])],
         """
import math


def softmax_log_grad(prefs, a):
    m = max(prefs)
    e = [math.exp(p - m) for p in prefs]
    total = sum(e)
    return [round((1.0 if i == a else 0.0) - x / total, 4) for i, x in enumerate(e)]
""", 'Compute stable softmax probabilities, then subtract them from the one hot vector.', '<p>Subtracting the largest preference before exponentiating avoids overflow without changing the probabilities.</p>')
K.assign('gae', 'm', 'Generalised advantage estimation',
         '<p>Write <code>gae(rewards, values, gamma, lam)</code> for one episode that ends after the last reward. values has one more entry than rewards: the last one is the value after the final step and is 0 at the end of an episode. Return the advantages, each rounded to 4 decimals.</p>',
         """
def gae(rewards, values, gamma, lam):
    # your code here
    pass
""", [('gae([0, 1], [0.5, 0.8, 0.0], 0.9, 0.8)', [0.364, 0.2]), ('gae([1, 1, 1], [0, 0, 0, 0], 1.0, 1.0)', [3.0, 2.0, 1.0]), ('gae([1, 1], [0, 0, 0], 1.0, 0.0)', [1.0, 1.0])],
         """
def gae(rewards, values, gamma, lam):
    adv, running = [0.0] * len(rewards), 0.0
    for t in reversed(range(len(rewards))):
        delta = rewards[t] + gamma * values[t + 1] - values[t]
        running = delta + gamma * lam * running
        adv[t] = round(running, 4)
    return adv
""", 'Work backwards: A<sub>t</sub> = &delta;<sub>t</sub> + &gamma;&lambda;A<sub>t+1</sub>.', '<p>The second test with &lambda; = 1 and zero values gives the plain returns 3, 2 and 1. The third with &lambda; = 0 gives the one step TD errors.</p>')
K.assign('ppo_objective', 'm', 'The PPO clipped objective',
         '<p>Write <code>ppo_objective(ratios, advantages, eps)</code> that returns the average over samples of min(r A, clip(r, 1 &minus; eps, 1 + eps) A), rounded to 4 decimals.</p>',
         """
def ppo_objective(ratios, advantages, eps):
    # your code here
    pass
""", [('ppo_objective([1.3], [2.0], 0.2)', 2.4), ('ppo_objective([0.7], [-1.0], 0.2)', -0.8), ('ppo_objective([1.0, 1.5, 0.5], [1.0, 1.0, 1.0], 0.2)', 0.9)],
         """
def ppo_objective(ratios, advantages, eps):
    total = 0.0
    for r, a in zip(ratios, advantages):
        clipped = min(max(r, 1 - eps), 1 + eps)
        total += min(r * a, clipped * a)
    return round(total / len(ratios), 4)
""", 'Clip each ratio, compute both terms, keep the smaller, then average.', '<p>In the third test the sample with r = 0.5 and A = 1 keeps its unclipped value 0.5: the minimum never forgives a drop in the probability of a good action.</p>')

K.must('Policy gradient', 'Learn &pi;(a|s, &theta;) by gradient ascent on J. Stochastic and continuous policies. Short corridor: best p = 0.59.')
K.must('REINFORCE', '&theta; += &alpha;G<sub>t</sub>&nabla;ln &pi;. Softmax: one hot(a) &minus; &pi;. Monte Carlo, high variance.')
K.must('Baseline', 'Use G &minus; b(s). Unbiased because &Sigma;<sub>a</sub>&nabla;&pi; = 0. Best simple choice v(s). Gives the advantage.')
K.must('Actor critic', 'Critic TD error &delta; replaces G. GAE: A&#770;<sub>t</sub> = &Sigma;(&gamma;&lambda;)<sup>l</sup>&delta;<sub>t+l</sub>. A2C, A3C.')
K.must('PPO and TRPO', 'PPO: min(rA, clip(r, 1 &minus; &epsilon;, 1 + &epsilon;)A), &epsilon; = 0.2, several epochs per batch. TRPO: KL trust region.')
K.must('Continuous control', 'Gaussian policy (a &minus; &mu;)/&sigma;<sup>2</sup>. DDPG, TD3 (double critics, delayed actor, smoothing), SAC (entropy).')

T = K.topic(
    slug='ml-policy-gradient', topic='ml-policy-gradient', step=(3, 'Modern RL', 'ml-r3', 'Scale RL to huge problems: function approximation and deep Q networks, policy gradients and actor critic methods, and how RL is used in practice, from offline data to RLHF.', 'Advanced'),
    title='Policy gradients, actor critic and PPO', short='Policy gradients and PPO', badge='3.2', minutes=55,
    lead='Learn the policy directly: REINFORCE on the short corridor, the policy gradient theorem and baselines, a tabular actor critic on the cliff walk, PPO with GAE on CartPole, and continuous control with DDPG, TD3 and SAC.',
    desc='policy gradient, REINFORCE, softmax policy, stochastic policy, policy gradient theorem, baseline, advantage, actor critic, TD error, GAE, A2C, A3C, TRPO, PPO, clipped objective, Gaussian policy, DDPG, TD3, SAC, natural gradient.',
    summary='REINFORCE, baselines, actor critic, GAE, PPO and TRPO, and continuous control methods.',
    keywords=['policy gradient', 'REINFORCE', 'actor critic', 'PPO', 'TRPO', 'GAE', 'advantage', 'baseline', 'SAC', 'DDPG'],
    recap='<p>Learn the policy directly with the policy gradient theorem. Baselines reduce noise, actor critic methods bootstrap from a critic, PPO keeps updates small with a clipped ratio, and Gaussian policies with DDPG, TD3 or SAC handle continuous actions.</p>',
    added='2026-11-13', leet=leet_items())
