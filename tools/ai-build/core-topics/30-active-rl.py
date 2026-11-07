# Chapter 10.3: active reinforcement learning. The uploaded slides and transcripts do not cover this step, so it
# follows AIMA 3rd ed. sections 21.3 and 21.4 (4th ed. 22.3 and 22.4), Sutton and Barto (2018), Watkins and Dayan
# (1992) and Mnih and others (2015). Every number in this chapter was checked by running its code and the qlearn
# animation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()
STEP10 = (10, 'Reinforcement learning', 'cai-rl', 'Decide over time and learn from rewards: Markov decision processes, policies, Q-values, passive and active reinforcement learning, and policy search.', 'College')

K.code('expfn', r'''
# The exploration function of AIMA section 21.3.1: be optimistic about actions tried fewer than Ne times.
R_PLUS, NE = 2.0, 5

def f(u, n):
    return R_PLUS if n < NE else u

# Two actions in one state: the agent has tried "safe" 20 times and "new" only twice.
estimate = {"safe": 0.6, "new": 0.1}
tries = {"safe": 20, "new": 2}
for a in estimate:
    print(a, " estimate", estimate[a], " tries", tries[a], " value used", f(estimate[a], tries[a]))
print("chosen:", max(estimate, key=lambda a: f(estimate[a], tries[a])))
''')

K.code('qcorr', r'''
# Q-learning in a corridor of 4 squares: 0 1 2 3. Square 3 is the goal (+1). Each other step gives 0.
import random
rng = random.Random(4)
Q = {(s, a): 0.0 for s in range(4) for a in ["L", "R"]}
alpha, gamma, eps = 0.5, 0.9, 0.3

for episode in range(6):
    s = 0
    while s != 3:
        if rng.random() < eps:                       # explore
            a = rng.choice(["L", "R"])
        else:                                        # exploit: best known action (R wins ties)
            a = "R" if Q[(s, "R")] >= Q[(s, "L")] else "L"
        s2 = max(0, s - 1) if a == "L" else s + 1
        r = 1.0 if s2 == 3 else 0.0
        best_next = 0.0 if s2 == 3 else max(Q[(s2, "L")], Q[(s2, "R")])
        Q[(s, a)] = Q[(s, a)] + alpha * (r + gamma * best_next - Q[(s, a)])
        s = s2
print({k: round(v, 3) for k, v in Q.items() if v != 0})
print("greedy policy:", ["R" if Q[(s, "R")] >= Q[(s, "L")] else "L" for s in range(3)])
''')

K.lesson('explore', 'Active learning: explore or exploit', f'''
{src('AIMA 3rd ed., section 21.3.1 (4th ed., 22.3), Sutton and Barto (2018), chapter 2, and Auer, Cesa-Bianchi and Fischer (2002) for UCB1. The uploaded slides and transcripts do not cover this step.')}
{wwh('In <b>active</b> RL the agent picks its own actions. It must balance <b>exploitation</b> (take the action that looks best now) and <b>exploration</b> (try other actions to learn whether they are better).',
     'A purely greedy agent locks onto the first policy that looks good and never finds out that another route was better. A purely random agent learns a lot but never uses it. Both lose reward.',
     'Explore more at first and less later. ε-greedy takes a random action with probability ε. An exploration function makes rarely tried actions look attractive. UCB adds a bonus that shrinks as an action is tried more often.')}
{fxs(fx('ε-greedy', 'with probability ε a random action, otherwise argmax over a of Q(s, a)', 'Simple and widely used.'),
     fx('Exploration function (AIMA)', 'f(u, n) = R⁺ if n < N_e, else u', 'Optimistic about actions tried fewer than N_e times.', key=True),
     fx('UCB1', 'pick argmax over i of x̄ᵢ + √(2 ln n ÷ nᵢ)', 'Mean so far plus a bonus for uncertainty. Its regret grows only like log n.'),
     fx('GLIE', 'try every action infinitely often, and become greedy in the limit', 'A condition under which the learned policy becomes optimal.'))}
{code('expfn')}
{note('The same trade off appears in the expectimax chapter (6.3) in UCT, which uses UCB1 inside Monte Carlo tree search to pick which move to try next.', 'tip')}
''', kw=['active reinforcement learning', 'exploration', 'exploitation', 'epsilon greedy', 'exploration function', 'UCB1', 'GLIE', 'regret', 'multi armed bandit'])

K.lesson('ql', 'Q-learning', f'''
{src('Watkins (1989), Watkins and Dayan (1992), and AIMA 3rd ed., section 21.3.2.')}
{wwh('<b>Q-learning</b> learns Q(s, a), the value of each action in each state, straight from experience. The agent acts, sees the reward and the next state, and moves Q(s, a) towards r + γ max over a′ of Q(s′, a′).',
     'With Q the agent can pick the best action by looking up a table: no transition model is needed, neither for learning nor for choosing actions. That makes it model free all the way.',
     'After each step (s, a, r, s′): Q(s, a) ← Q(s, a) + α (r + γ max over a′ of Q(s′, a′) − Q(s, a)). Act with ε-greedy or an exploration function. With every pair tried infinitely often and a Robbins Monro learning rate, Q converges to Q*.')}
{fxs(fx('Q-learning update', 'Q(s, a) ← Q(s, a) + α [r + γ max over a′ of Q(s′, a′) − Q(s, a)]', 'Off policy: the target uses the best next action.', key=True),
     fx('SARSA update', 'Q(s, a) ← Q(s, a) + α [r + γ Q(s′, a′) − Q(s, a)]', 'On policy: a′ is the action the agent really takes next.'),
     fx('Greedy policy', 'π(s) = argmax over a of Q(s, a)', 'No model needed.'))}
{code('qcorr')}
{steps('Worked example: one Q-learning update', [
    'Q(s, a) = 0.2. The agent gets r = 0 and lands in s′, where the best Q value is 0.8. γ = 0.9, α = 0.5.',
    'Target: 0 + 0.9 × 0.8 = 0.72.',
    'Error: 0.72 − 0.2 = 0.52.',
    eq('Q(s, a) ← 0.2 + 0.5 × 0.52 = 0.46')])}
''', kw=['Q-learning', 'off policy', 'model free', 'Q table', 'Watkins'])

K.lesson('sarsal', 'SARSA, on policy and off policy', f'''
{src('Rummery and Niranjan (1994), and Sutton and Barto (2018), section 6.5 and example 6.6 (cliff walking).')}
{wwh('SARSA is named after the five things in its update: State, Action, Reward, next State, next Action. It learns the value of the policy it actually follows, exploration included. Q-learning learns the value of the greedy policy, whatever it does while exploring.',
     'When exploration is costly, the difference matters. On a cliff edge, an exploring agent sometimes slips. SARSA learns to keep a safe distance. Q-learning learns the shortest path along the edge, which is optimal only for an agent that never explores.',
     'Both use the same loop. SARSA chooses a′ first and uses Q(s′, a′) in the target. Q-learning uses max over a′ of Q(s′, a′) and may then take a different a′.')}
{viz('qlearn')}
{table(['', 'Q-learning', 'SARSA'], [
    ['Learns', 'Q* of the greedy policy (off policy)', 'Q of the ε-greedy policy it follows (on policy)'],
    ['Cliff walking path', 'shortest, along the edge (13 steps)', 'safer, one or two rows up'],
    ['Reward while learning', 'lower: it falls more while exploring', 'higher'],
    ['Can learn from', 'any data, even another agent’s', 'its own current policy only']])}
''', kw=['SARSA', 'on policy', 'off policy', 'cliff walking', 'exploration cost'])

K.lesson('approx', 'Function approximation and deep Q-networks', f'''
{src('AIMA 3rd ed., section 21.4, Mnih and others (2015), Human level control through deep reinforcement learning, Nature, and Tesauro (1995).')}
{wwh('A table with one entry per state is impossible for chess (about 10⁴⁰ positions) or for screen images. <b>Function approximation</b> replaces the table with a formula Q̂_θ(s, a) that has a few parameters θ, such as a weighted sum of features or a neural network.',
     'The formula generalises: what is learned in one state carries over to similar states never seen before. A few thousand parameters can stand for billions of states.',
     'Use the same TD target, and move θ a little in the direction that reduces the error: θ ← θ + α [r + γ max over a′ of Q̂(s′, a′) − Q̂(s, a)] ∇_θ Q̂(s, a). DQN does this with a deep network, plus a replay buffer of past steps and a slowly updated target network for stability.')}
{fxs(fx('Linear approximation', 'Û_θ(s) = θ₀ + θ₁ f₁(s) + ... + θₙ fₙ(s)', 'f are features, such as the x and y of a square.'),
     fx('Gradient TD update', 'θᵢ ← θᵢ + α [target − Q̂(s, a)] ∂Q̂ ÷ ∂θᵢ', 'For a linear Q̂ the derivative is just the feature value.', key=True))}
{steps('Worked example: a linear utility for the 4 × 3 world', [
    'Û(x, y) = θ₀ + θ₁ x + θ₂ y with θ = (0.5, 0.2, 0.1). At (1,1): Û = 0.5 + 0.2 + 0.1 = 0.8.',
    'The observed reward to go is 0.705 (the true value), so the error is 0.705 − 0.8 = −0.095.',
    'With α = 0.1: θ₀ ← 0.5 + 0.1 × (−0.095) × 1 = 0.4905.',
    eq('θ₁ and θ₂ also fall by 0.0095, since x = y = 1')])}
{note('With function approximation, Q-learning can diverge: off policy data, bootstrapping and approximation together (the deadly triad). DQN’s replay buffer and target network were added to keep training stable.', 'warn')}
''', kw=['function approximation', 'features', 'gradient TD', 'deep Q-network', 'DQN', 'experience replay', 'target network', 'generalisation'])

K.lesson('maths', 'The maths: the Bellman equation for Q and convergence', f'''
{fxs(
    fx('Bellman optimality for Q', 'Q*(s, a) = Σ P(s′ | s, a) [R(s, a, s′) + γ max over a′ of Q*(s′, a′)]', 'Q-learning is a sampled version of this.', key=True),
    fx('ε-greedy action chances', 'best action: 1 − ε + ε ÷ |A|, each other action: ε ÷ |A|', 'The random choice can also pick the best action.'),
    fx('Convergence of Q-learning', 'every (s, a) tried infinitely often, Σ αₜ = ∞, Σ αₜ² < ∞', 'Watkins and Dayan, 1992, for tables.'),
    fx('UCB1 regret', 'expected regret after n pulls is O(log n)', 'Lai and Robbins (1985) showed log n is the best possible order.'))}
{steps('Worked example: the optimal Q values of the corridor 0 1 2 3 (goal 3 gives +1, γ = 0.9)', [
    'Q*(2, R) = 1: one step to the goal.',
    'Q*(1, R) = 0 + 0.9 × 1 = 0.9.',
    'Q*(0, R) = 0.9 × 0.9 = 0.81.',
    'Q*(1, L) = 0 + 0.9 × max Q*(0, ·) = 0.9 × 0.81.',
    eq('Q*(1, L) = 0.729')])}
''', kw=['Bellman optimality', 'Q star', 'convergence', 'epsilon greedy probability', 'regret bound'])

K.lesson('compare', 'Active learners compared', f'''
{versus('Learning to act', ['', 'Greedy ADP', 'ADP + exploration function', 'Q-learning', 'SARSA', 'DQN'], [
    ['Model', 'learned', 'learned', 'none', 'none', 'none'],
    ['Exploration', 'none, gets stuck', 'optimistic values', 'ε-greedy or similar', 'ε-greedy or similar', 'ε-greedy'],
    ['Learns', 'a policy that may be poor', 'near optimal policy', 'Q* (off policy)', 'Q of its own policy (on policy)', 'Q* with a neural network'],
    ['Data use', 'best', 'best', 'one update per step', 'one update per step', 'replays old steps many times'],
    ['Weak when', 'always', 'big state spaces (must solve the model)', 'huge state spaces without approximation', 'same as Q-learning', 'needs millions of frames, can be unstable']],
    'model based learning uses data best, model free learning is simpler and scales with function approximation. Modern systems such as AlphaZero and MuZero mix both.')}
{scene('Deep reinforcement learning milestones', '<p>DQN (2015) learned 49 Atari games from screen pixels and the score, and played many of them as well as a professional human tester. AlphaGo (Silver and others, 2016) beat Lee Sedol at Go, combining policy and value networks with Monte Carlo tree search. RL from human feedback (Christiano and others, 2017, and later chat models) trains language models with a reward learned from people’s preferences.</p>')}
''', kw=['comparison', 'model based', 'model free', 'AlphaGo', 'AlphaZero', 'MuZero', 'RLHF'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>To learn which choices are good, sometimes try something new. Keep a score for each choice in each situation and update it after every try.</p>',
    '<p>Exploration (ε-greedy, exploration functions, UCB). Q-learning: Q ← Q + α(r + γ max Q′ − Q), off policy. SARSA: on policy. Function approximation with gradient TD.</p>',
    '<p>GLIE conditions, Watkins and Dayan convergence for tabular Q-learning, regret bounds for bandits, maximisation bias in Q-learning and double Q-learning (van Hasselt, 2010), the deadly triad.</p>',
    '<p>Research: sample efficient exploration (count based bonuses, curiosity), offline RL from fixed datasets, safe RL with constraints, and RL for reasoning in large language models.</p>')}
''', kw=['double Q-learning', 'maximisation bias', 'curiosity', 'offline RL', 'safe RL'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Active RL: the agent chooses actions and must balance exploration and exploitation. Greedy agents get stuck.',
    'ε-greedy, exploration functions f(u, n) and UCB1 make the agent try uncertain actions.',
    'Q-learning: Q(s, a) ← Q(s, a) + α [r + γ max Q(s′, a′) − Q(s, a)]. Off policy, model free, converges to Q*.',
    'SARSA uses the next action actually taken. On the cliff it learns a safer path than Q-learning.',
    'Function approximation and deep networks (DQN) scale Q-learning to huge state spaces, with care for stability.'],
    'chapter 10.4 skips values and searches directly for a good policy: policy gradient methods.')}
{nbcard('active-rl', 'Run Q-learning in a corridor and try the exploration function, then write the Q update, ε-greedy action choice and a full Q-learner yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Exploitation means', ['trying random actions', 'taking the action that looks best now', 'learning the model', 'stopping'], 1,
       'Use what you know.', 'Exploration tries other actions to learn more.')
K.quiz('e', 'With ε = 0.1, ε-greedy takes a random action', ['never', '10 percent of the time', '90 percent of the time', 'always'], 1,
       'ε is the chance.', 'The rest of the time it is greedy.')
K.quiz('e', 'Q-learning needs a transition model', ['to learn', 'to pick actions', 'neither', 'both'], 2,
       'Model free.', 'Both learning and acting use only Q.')
K.quiz('e', 'The Q-learning target is', ['r', 'r + γ max over a′ of Q(s′, a′)', 'Q(s, a)', 'U(s)'], 1,
       'Best next action.', 'Then move Q(s, a) towards it.')
K.quiz('m', 'SARSA is on policy because', ['it uses a model', 'its target uses the next action the agent actually takes', 'it never explores', 'it uses max'], 1,
       'S, A, R, S′, A′.', 'It values the policy it follows.')
K.quiz('m', 'On the cliff walking task with ε = 0.1, Q-learning’s greedy path is', ['the safe path far from the edge', 'the shortest path along the edge', 'random', 'into the cliff'], 1,
       'Off policy: ignores its own exploring slips.', 'SARSA keeps a safe distance.')
K.quiz('m', 'A purely greedy learning agent', ['always finds the optimal policy', 'can lock onto a poor policy and never learn that others are better', 'explores too much', 'needs no data'], 1,
       'No exploration.', 'It never tries the actions that look worse but might be better.')
K.quiz('m', 'The exploration function f(u, n) returns R⁺ when', ['u is large', 'the action has been tried fewer than N_e times', 'n is large', 'always'], 1,
       'Optimism.', 'After N_e tries it trusts the estimate u.')
K.quiz('h', 'With ε = 0.2 and 4 actions, ε-greedy picks the best action with probability', ['0.8', '0.85', '0.95', '0.2'], 1,
       'The random choice can pick it too.', '0.8 + 0.2 ÷ 4 = 0.85.')
K.quiz('h', 'DQN keeps training stable with', ['a larger ε', 'a replay buffer and a target network', 'no rewards', 'a transition model'], 1,
       'Mnih and others, 2015.', 'Replay breaks correlations, the target network keeps targets steady.')
K.quiz('x', 'In the style of a Stanford CS234 exam: Q-learning tends to overestimate values because', ['α is too small', 'taking a max over noisy estimates is biased upwards (maximisation bias), which double Q-learning fixes', 'γ < 1', 'it is on policy'], 1,
       'E[max] ≥ max E.', 'Double Q-learning uses one estimate to pick the action and another to value it.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: which is true for tabular Q-learning with a fixed learning rate α = 0.5 in a deterministic world?', ['it never learns', 'it can still converge to Q*, since targets do not vary in a deterministic world once the Q values downstream settle', 'it needs SARSA', 'it diverges'], 1,
       'Noise free targets.', 'Decaying α is needed for random outcomes. With deterministic outcomes, a fixed α still settles.')

# ---------------------------------------------------------------- calc
K.calc('e', 'Q(s, a) = 0, α = 0.5, the step reaches the goal with r = 1 (no next state). New Q(s, a)?', '0.5', 'Target is 1.',
       ['Target r = 1, no future term.', 'Error 1 − 0 = 1.', eq('0 + 0.5 × 1 = 0.5')], check=0.5, tol=0.0005)
K.calc('e', 'Exploration function with R⁺ = 2, N_e = 5: f(0.1, 2)?', '2', 'n < N_e.',
       ['2 < 5.', 'So return R⁺.', eq('2')], check=2)
K.calc('e', 'A linear utility θ = (0.5, 0.2, 0.1) for Û = θ₀ + θ₁ x + θ₂ y. Û(1, 1)?', '0.8', 'Add them.',
       ['θ₁ x = 0.2.', 'θ₂ y = 0.1.', eq('0.5 + 0.2 + 0.1 = 0.8')], check=0.8, tol=0.0005)
K.calc('m', 'Q(s, a) = 0.2, r = 0, γ = 0.9, max Q(s′, ·) = 0.8, α = 0.5. New Q(s, a) by Q-learning?', '0.46', 'Target 0.72.',
       ['Target = 0.9 × 0.8 = 0.72.', 'Error = 0.52.', eq('0.2 + 0.26 = 0.46')], check=0.46, tol=0.0005)
K.calc('m', 'Same step, but the agent will next take an exploring action with Q(s′, a′) = 0.3. New Q(s, a) by SARSA?', '0.235', 'Target 0.27.',
       ['Target = 0.9 × 0.3 = 0.27.', 'Error = 0.07.', eq('0.2 + 0.035 = 0.235')], check=0.235, tol=0.0005)
K.calc('m', 'ε-greedy with ε = 0.1 and 4 actions: chance of the best action?', '0.925', '0.9 + 0.1 ÷ 4.',
       ['Greedy part: 0.9.', 'Random part picks it with 0.1 ÷ 4 = 0.025.', eq('0.925')], check=0.925, tol=0.0005)
K.calc('m', 'Corridor 0 1 2 3, goal +1, γ = 0.9: Q*(0, R)?', '0.81', 'Two discounts.',
       ['Q*(2, R) = 1.', 'Q*(1, R) = 0.9.', eq('Q*(0, R) = 0.81')], check=0.81, tol=0.0005)
K.calc('h', 'UCB1 index of an arm with mean 0.5, pulled 10 times out of n = 100. Give 2 decimals.', '1.46', 'x̄ + √(2 ln n ÷ nᵢ).',
       ['ln 100 ≈ 4.605, so 2 ln n ≈ 9.21.', '9.21 ÷ 10 = 0.921, √0.921 ≈ 0.960.', eq('0.5 + 0.96 ≈ 1.46')], check=1.46, tol=0.005)
K.calc('h', 'Gradient update of θ₀: θ₀ = 0.5, α = 0.1, target 0.705, Û = 0.8, feature for θ₀ is 1. Give 4 decimals.', '0.4905', 'θ₀ + α (target − Û).',
       ['Error = 0.705 − 0.8 = −0.095.', 'α × error = −0.0095.', eq('0.4905')], check=0.4905, tol=0.00005)
K.calc('x', 'Corridor 0 1 2 3, goal +1, γ = 0.9: Q*(1, L)?', '0.729', 'Go left to 0, then act optimally.',
       ['Moving left gives r = 0 and lands in 0.', 'max Q*(0, ·) = Q*(0, R) = 0.81.', eq('0.9 × 0.81 = 0.729')], check=0.729, tol=0.0005)

# ---------------------------------------------------------------- assignments
K.assign('qup', 'e', 'One Q-learning update',
         '<p>Write <code>q_update(q, r, best_next, alpha, gamma)</code> that returns the new Q(s, a). best_next is max over a′ of Q(s′, a′) (0 at the goal).</p>',
         '''
def q_update(q, r, best_next, alpha, gamma):
    # your code here
    pass
''', [("round(q_update(0.2, 0.0, 0.8, 0.5, 0.9), 4)", 0.46), ("q_update(0.0, 1.0, 0.0, 0.5, 0.9)", 0.5),
      ("round(q_update(0.81, 0.0, 0.9, 1.0, 0.9), 4)", 0.81)],
         '''
def q_update(q, r, best_next, alpha, gamma):
    target = r + gamma * best_next
    return q + alpha * (target - q)
''', 'Target first, then move a fraction alpha of the way.', '<p>Test 3: the value is already right, so it stays at 0.81.</p>')
K.assign('egreedy', 'm', 'ε-greedy action choice',
         '<p>Write <code>egreedy(qs, eps, rng)</code>: qs maps actions to Q values. With probability eps (use <code>rng.random() < eps</code>) return <code>rng.choice(sorted(qs))</code>, otherwise return the action with the largest value.</p>',
         '''import random

def egreedy(qs, eps, rng):
    # your code here
    pass
''', [("egreedy({'L': 0.1, 'R': 0.5}, 0.0, random.Random(1))", 'R'),
      ("8700 < sum(egreedy({'L': 0.1, 'R': 0.5}, 0.2, rng) == 'R' for rng in [random.Random(3)] for _ in range(10000)) < 9300", True),
      ("egreedy({'a': -1.0, 'b': -2.0, 'c': -0.5}, 0.0, random.Random(2))", 'c')],
         '''import random

def egreedy(qs, eps, rng):
    if rng.random() < eps:
        return rng.choice(sorted(qs))
    best = None
    for a in qs:
        if best is None or qs[a] > qs[best]:
            best = a
    return best
''', 'Draw one random number to decide between exploring and exploiting.', '<p>Test 2: with ε = 0.2 and 2 actions, R is chosen 0.8 + 0.1 = 90 percent of the time.</p>')
K.assign('qlearn', 'h', 'Q-learning in the corridor',
         '<p>Write <code>learn(episodes, seed)</code> for the corridor 0 1 2 3 (goal 3 gives +1, other steps 0, Left from 0 stays at 0). Use α = 0.5, γ = 0.9, ε = 0.3, start each episode at 0, and break ties towards "R". Return the Q dictionary keyed by (state, action).</p>',
         '''import random

def learn(episodes, seed):
    rng = random.Random(seed)
    # your code here
    pass
''', [("round(learn(300, 1)[(2, 'R')], 2)", 1.0), ("round(learn(300, 1)[(0, 'R')], 2)", 0.81),
      ("all(learn(300, 5)[(s, 'R')] > learn(300, 5)[(s, 'L')] for s in range(3))", True)],
         '''import random

def learn(episodes, seed):
    rng = random.Random(seed)
    Q = {}
    for s in range(4):
        for a in ["L", "R"]:
            Q[(s, a)] = 0.0
    for e in range(episodes):
        s = 0
        while s != 3:
            if rng.random() < 0.3:
                a = rng.choice(["L", "R"])
            elif Q[(s, "R")] >= Q[(s, "L")]:
                a = "R"
            else:
                a = "L"
            if a == "L":
                s2 = max(0, s - 1)
            else:
                s2 = s + 1
            if s2 == 3:
                r = 1.0
                best = 0.0
            else:
                r = 0.0
                best = max(Q[(s2, "L")], Q[(s2, "R")])
            Q[(s, a)] = Q[(s, a)] + 0.5 * (r + 0.9 * best - Q[(s, a)])
            s = s2
    return Q
''', 'Follow the loop of the example program, but for many episodes.', '<p>The world is deterministic, so even with a fixed α the Q values of the moves to the right settle at 1, 0.9 and 0.81.</p>')

K.must('Explore or exploit', 'ε-greedy, exploration function f(u, n) = R⁺ if n < N_e else u, UCB1 x̄ + √(2 ln n ÷ nᵢ). GLIE.')
K.must('Q-learning', 'Q ← Q + α [r + γ max Q(s′, a′) − Q]. Off policy, model free. Converges with every pair tried and Robbins Monro α.')
K.must('SARSA', 'Q ← Q + α [r + γ Q(s′, a′) − Q] with the a′ actually taken. On policy. Safer path on the cliff.')
K.must('Approximation', 'θ ← θ + α [target − Q̂] ∇Q̂. DQN: replay buffer + target network. Deadly triad.')
K.must('Key numbers', 'ε-greedy best action: 1 − ε + ε/|A|. Corridor Q*: 1, 0.9, 0.81. Cliff: Q-learning path 13 steps.')

T = K.topic(
    slug='active-rl', topic='active-rl', step=STEP10,
    title='Active reinforcement learning', short='Active RL', badge='10.3', minutes=50,
    lead='Let the agent choose its own actions. Balance exploration and exploitation, learn action values with Q-learning and SARSA, see why they differ on a cliff, and scale up with function approximation.',
    desc='Active reinforcement learning, exploration and exploitation, ε-greedy, exploration functions, UCB1 and regret, GLIE, Q-learning and its convergence, SARSA, on policy and off policy learning, cliff walking, function approximation with features and gradient TD, deep Q-networks with replay and target networks, maximisation bias, and milestones from TD-Gammon to AlphaGo.',
    summary='Exploration, Q-learning, SARSA, function approximation and deep Q-networks.',
    keywords=['active reinforcement learning', 'exploration', 'epsilon greedy', 'UCB', 'Q-learning', 'SARSA', 'on policy', 'off policy', 'function approximation', 'DQN'],
    recap='<p>Explore, then exploit. Q-learning: Q += α(r + γ max Q′ − Q). SARSA uses the next action taken.</p>',
    nb={'qcorr': 'Q-learning in a corridor', 'expfn': 'The exploration function'})
