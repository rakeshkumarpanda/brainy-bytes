# Chapter 10.2: passive reinforcement learning. The uploaded slides and transcripts do not cover this step, so it
# follows AIMA 3rd ed. sections 21.1 and 21.2 (4th ed. 22.1 and 22.2) and Sutton and Barto (2018). Every number in
# this chapter was checked by running its code and the tdlearn animation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()
STEP10 = (10, 'Reinforcement learning', 'cai-rl', 'Decide over time and learn from rewards: Markov decision processes, policies, Q-values, passive and active reinforcement learning, and policy search.', 'College')

K.code('trials', r'''
# The three trials of AIMA section 21.2 in the 4 x 3 world. Each step costs -0.04, the end square gives +1 or -1.
trials = [["11", "12", "13", "12", "13", "23", "33", "43"],
          ["11", "12", "13", "23", "33", "32", "33", "43"],
          ["11", "21", "31", "32", "42"]]
end = {"43": 1.0, "42": -1.0}

# Direct utility estimation: average the reward to go of every visit.
total, count = {}, {}
for t in trials:
    for i in range(len(t) - 1):
        to_go = -0.04 * (len(t) - 1 - i) + end[t[-1]]
        s = t[i]
        total[s] = total.get(s, 0) + to_go
        count[s] = count.get(s, 0) + 1
print("direct estimate of U(1,1):", round(total["11"] / count["11"], 4))

# Adaptive dynamic programming learns the model first: count where each square led.
moves = {}
for t in trials:
    for i in range(len(t) - 1):
        moves.setdefault(t[i], []).append(t[i + 1])
for s in ["13", "33"]:
    nxt = moves[s]
    print("from", s, ":", {n: str(nxt.count(n)) + "/" + str(len(nxt)) for n in sorted(set(nxt))})
''')

K.code('td', r'''
# TD(0) on the five state random walk of Sutton and Barto (example 6.2).
# States A to E, start at C, move left or right with chance 1/2. Leaving on the right gives 1, on the left 0.
import random
rng = random.Random(3)
names = ["A", "B", "C", "D", "E"]
V = {s: 0.5 for s in names}
V["left"], V["right"] = 0.0, 0.0
alpha = 0.1

for episode in range(6):
    i = 2
    while 0 <= i <= 4:
        j = i + (1 if rng.random() < 0.5 else -1)
        nxt = "left" if j < 0 else "right" if j > 4 else names[j]
        reward = 1.0 if nxt == "right" else 0.0
        V[names[i]] = V[names[i]] + alpha * (reward + V[nxt] - V[names[i]])   # TD(0) update
        i = j
print("after 6 episodes:", {s: round(V[s], 3) for s in names})
print("true values:      ", {s: round((k + 1) / 6, 3) for k, s in enumerate(names)})
''')

K.lesson('passive', 'Passive learning: judge a fixed policy without a model', f'''
{src('AIMA 3rd ed., sections 21.1 and 21.2 (4th ed., 22.1 and 22.2), Sutton and Barto (2018), Reinforcement Learning: An Introduction, chapters 5 and 6. The uploaded slides and transcripts do not cover this step.')}
{wwh('<b>Reinforcement learning</b> (RL) learns to act well from rewards alone, without being told the transition model P or the reward function R. In <b>passive</b> RL the policy π is fixed, and the agent only learns how good it is: the utilities U^π(s).',
     'In most real problems nobody can write down P and R: a robot does not know how its wheels slip on a new floor, a game program does not know how its opponents play. The agent must learn from trials.',
     'Run trials from a start state to an end state, following π, and record the states and rewards seen. Then use them in one of three ways: average what followed each state (direct estimation), learn P and R and solve the Bellman equations (adaptive dynamic programming), or nudge each U(s) towards what happened next (temporal difference learning).')}
{table(['Method', 'What it learns', 'Update', 'Speed'], [
    ['Direct utility estimation', 'U(s) as an average', 'average of all rewards to go seen from s', 'slow: ignores links between states'],
    ['Adaptive dynamic programming (ADP)', 'P̂(s′ | s, π(s)) and R(s)', 'solve U(s) = R(s) + γ Σ P̂ U(s′) after each step', 'fastest per trial, costly per step'],
    ['Temporal difference (TD)', 'U(s) directly', 'U(s) ← U(s) + α (R(s) + γ U(s′) − U(s))', 'cheap per step, a bit slower than ADP']])}
{code('trials')}
{steps('Worked example: direct estimation of U(1,1) from the three textbook trials', [
    'Trial 1 visits (1,1) once, then 6 more squares before reaching +1: reward to go = 7 × (−0.04) + 1 = 0.72.',
    'Trial 2 also gives 0.72.',
    'Trial 3 goes (1,1), (2,1), (3,1), (3,2) and ends at −1: 4 × (−0.04) − 1 = −1.16.',
    eq('U(1,1) ≈ (0.72 + 0.72 − 1.16) ÷ 3 ≈ 0.0933, far from the true 0.705 after only 3 trials')])}
''', kw=['reinforcement learning', 'passive learning', 'fixed policy', 'trial', 'reward to go', 'direct utility estimation', 'adaptive dynamic programming'])

K.lesson('tdl', 'Temporal difference learning', f'''
{src('Sutton (1988), Learning to predict by the methods of temporal differences, and AIMA 3rd ed., section 21.2.3.')}
{wwh('TD learning updates the guess U(s) after every single step, using the guess for the next state: the target is R(s) + γ U(s′). The difference between the target and the old guess is the <b>TD error</b>.',
     'It needs no model and no waiting until the end of a trial. Because the target uses U(s′), information about rewards flows backwards from state to state, much faster than averaging whole trials.',
     'After the move s → s′, compute δ = R(s) + γ U(s′) − U(s), then set U(s) ← U(s) + α δ. With a learning rate α that shrinks the right way, U converges to U^π.')}
{fxs(fx('TD(0) update', 'U(s) ← U(s) + α (R(s) + γ U(s′) − U(s))', 'α is the learning rate.', key=True),
     fx('TD error', 'δ = R(s) + γ U(s′) − U(s)', 'Positive: things went better than expected.'),
     fx('Learning rate schedule', 'Σ αₙ = ∞ and Σ αₙ² < ∞, for example αₙ = 1 ÷ n or 60 ÷ (59 + n)', 'Robbins and Monro (1951). Then TD converges.'),
     fx('TD(λ)', 'U(x) ← U(x) + α δ e(x), with traces e(x) that decay by γ λ each step', 'λ = 0 is TD(0), λ = 1 is like averaging whole trials.'))}
{viz('tdlearn')}
{code('td')}
{steps('Worked example: one TD update', [
    'U(s) = 0.5, the agent moves to s′ with U(s′) = 0.8, R(s) = −0.04, γ = 1, α = 0.1.',
    'TD error δ = −0.04 + 0.8 − 0.5 = 0.26.',
    'U(s) ← 0.5 + 0.1 × 0.26.',
    eq('U(s) = 0.526')])}
{note('TD learning from experience is the same idea as the Bellman update, but it uses the one next state that actually happened instead of an average over all next states. Over many steps, states are reached in proportion to P(s′ | s, a), so the averages come out right.', 'tip')}
''', kw=['temporal difference', 'TD(0)', 'TD error', 'learning rate', 'Robbins Monro', 'TD(lambda)', 'eligibility trace'])

K.lesson('adp', 'Adaptive dynamic programming', f'''
{src('AIMA 3rd ed., section 21.2.2, and Moore and Atkeson (1993) for prioritised sweeping.')}
{wwh('An ADP agent learns the transition model from the counts of what happened, then solves the Bellman equations of the learned MDP for the fixed policy.',
     'It uses every bit of the data: each observed move updates the model and, through the equations, all utilities at once. It learns from the fewest trials.',
     'Keep counts N(s, a, s′). Set P̂(s′ | s, a) = N(s, a, s′) ÷ N(s, a). After each step, run policy evaluation on (P̂, R). Prioritised sweeping updates first the states whose values are most likely to change.')}
{fxs(fx('Learned model', 'P̂(s′ | s, a) = N(s, a, s′) ÷ N(s, a)', 'Maximum likelihood from counts.', key=True))}
{steps('Worked example: the model from the three trials', [
    '(1,3) was left 3 times with the action Right: twice to (2,3), once to (1,2).',
    'P̂((2,3) | (1,3), Right) = 2 ÷ 3.',
    '(3,3) was left 3 times with Right: twice to (4,3), once to (3,2).',
    eq('P̂((4,3) | (3,3), Right) = 2 ÷ 3, close to the true 0.8 only after more trials')])}
''', kw=['adaptive dynamic programming', 'model based', 'learned model', 'counts', 'prioritised sweeping'])

K.lesson('maths', 'The maths: bias, variance and fixed points', f'''
{fxs(
    fx('Monte Carlo target', 'Gₜ = Rₜ + γ Rₜ₊₁ + γ² Rₜ₊₂ + ...', 'Unbiased, but high variance: it depends on every later random step.'),
    fx('TD target', 'Rₜ + γ U(Sₜ₊₁)', 'Biased while U is wrong, but low variance: it depends on one step.', key=True),
    fx('Eligibility trace', 'e(s) ← γ λ e(s), then e(Sₜ) ← e(Sₜ) + 1', 'Credit fades by γλ per step.'),
    fx('Batch TD answer', 'the values of the maximum likelihood Markov model of the data', 'Batch Monte Carlo gives the averages of the observed returns instead.'))}
{steps('Worked example: batch TD versus Monte Carlo (Sutton and Barto, example 6.4)', [
    'Eight episodes: once A, 0, B, 0. Six times B, 1. Once B, 0. (γ = 1)',
    'Both methods: U(B) = 6 ÷ 8 = 0.75.',
    'Monte Carlo: the only episode through A returned 0, so U(A) = 0.',
    'Batch TD: A always went to B with reward 0, so U(A) = 0 + U(B).',
    eq('U(A) = 0.75 by TD, 0 by Monte Carlo. TD uses the Markov structure.')])}
''', kw=['Monte Carlo', 'bias', 'variance', 'eligibility trace', 'batch TD', 'certainty equivalence'])

K.lesson('compare', 'Passive learners compared', f'''
{versus('Learning U^π from trials', ['', 'Direct estimation (Monte Carlo)', 'ADP', 'TD(0)', 'TD(λ)'], [
    ['Needs a model', 'No', 'learns one', 'No', 'No'],
    ['Work per step', 'tiny', 'solve a system of equations', 'one update', 'update all traced states'],
    ['Data needed', 'most', 'least', 'medium', 'medium, often less than TD(0)'],
    ['Uses the Markov links', 'No', 'Yes, fully', 'Yes, one step', 'Yes, mixed'],
    ['Famous use', 'Monte Carlo evaluation', 'model based RL', 'TD-Gammon (Tesauro, 1995)', 'TD-Gammon also used TD(λ)']],
    'TD learning is the usual choice: almost as data efficient as ADP, and as cheap as direct estimation.')}
{scene('TD-Gammon', '<p>Gerald Tesauro’s TD-Gammon (1992 to 1995) learned backgammon by playing about 1.5 million games against itself, with a neural network trained by TD(λ) to predict the chance of winning. It reached the level of the best human players and changed how experts play some opening moves.</p>')}
''', kw=['comparison', 'TD-Gammon', 'self play', 'Monte Carlo evaluation'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>You learn how good a place is by going there many times. TD learning updates your opinion of a place as soon as you see where it led, not only at the end of the trip.</p>',
    '<p>Passive RL: fixed π, learn U^π. Direct estimation averages rewards to go. ADP learns P̂ and solves the equations. TD(0): U(s) ← U(s) + α(R + γU(s′) − U(s)).</p>',
    '<p>Robbins Monro conditions for convergence. TD as stochastic approximation of the Bellman operator. Bias and variance of TD and Monte Carlo targets. TD(λ) and n step returns as a family between them.</p>',
    '<p>Research: off policy evaluation (estimating a new policy from old logs), TD with neural networks and the deadly triad (function approximation, bootstrapping and off policy data can diverge), and distributional RL that learns the whole return distribution.</p>')}
''', kw=['stochastic approximation', 'n step returns', 'off policy evaluation', 'deadly triad', 'distributional RL'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Passive RL: the policy is fixed, the agent learns U^π(s) from trials without knowing P or R.',
    'Direct estimation averages rewards to go. Three textbook trials give U(1,1) ≈ 0.093.',
    'ADP learns P̂(s′ | s, a) = N(s, a, s′) ÷ N(s, a) and solves the Bellman equations. Most data efficient.',
    'TD(0): U(s) ← U(s) + α (R(s) + γ U(s′) − U(s)). It converges with a learning rate that satisfies Robbins Monro.',
    'TD targets have lower variance than Monte Carlo returns but are biased while U is wrong.'],
    'chapter 10.3 lets the agent choose its own actions: active RL, exploration and Q-learning.')}
{nbcard('passive-rl', 'Estimate utilities from the textbook trials and run TD(0) on the random walk, then write direct estimation, the TD update and a full TD learner yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In passive reinforcement learning the agent', ['chooses its actions', 'follows a fixed policy and learns how good it is', 'knows P and R', 'learns nothing'], 1,
       'Fixed π.', 'It learns U^π.')
K.quiz('e', 'The reward to go of a state in a trial is', ['the next reward only', 'the sum of rewards from that state to the end of the trial', 'the reward of the start', 'always 1'], 1,
       'From here to the end.', 'Direct estimation averages these.')
K.quiz('e', 'The TD update target is', ['the final reward', 'R(s) + γ U(s′)', 'U(s′) − U(s)', 'α'], 1,
       'One step plus the guess.', 'Then move U(s) a fraction α of the way.')
K.quiz('e', 'ADP stands for', ['adaptive dynamic programming', 'average direct prediction', 'action decision policy', 'advanced depth planning'], 0,
       'Learn the model, solve the MDP.', 'It counts transitions.')
K.quiz('m', 'Why does direct utility estimation learn slowly?', ['it uses a model', 'it ignores that U(s) depends on the utilities of the next states', 'it needs γ < 1', 'it updates too often'], 1,
       'No Bellman links.', 'Each state is averaged on its own.')
K.quiz('m', 'TD learning needs a transition model', ['yes', 'no: the observed next state takes the place of the average over P', 'only for γ = 1', 'only at the end'], 1,
       'Model free.', 'Frequent next states are seen more often, so averages come out right.')
K.quiz('m', 'Which learning rate schedule guarantees TD convergence?', ['α = 0.5 always', 'αₙ = 1 ÷ n', 'αₙ = 1 ÷ n²', 'α = 0'], 1,
       'Robbins Monro.', 'Σ 1/n = ∞ and Σ 1/n² < ∞. 1/n² sums to a finite number, so learning stops too early.')
K.quiz('m', 'Compared with Monte Carlo targets, TD targets have', ['higher variance', 'lower variance but some bias', 'no bias and no variance', 'the same'], 1,
       'One random step.', 'They lean on a guess, which may be wrong.')
K.quiz('h', 'TD(λ) with λ = 1 behaves like', ['TD(0)', 'averaging whole returns (Monte Carlo)', 'ADP', 'random play'], 1,
       'Full traces.', 'Credit reaches back to every earlier state without fading by λ.')
K.quiz('h', 'Prioritised sweeping', ['samples states uniformly', 'updates first the states whose values are most likely to change', 'ignores rewards', 'is a TD rule'], 1,
       'Moore and Atkeson, 1993.', 'It makes ADP cheaper per step.')
K.quiz('x', 'In the style of a Stanford CS234 exam: on the batch data A, 0, B, 0 once, B, 1 six times, B, 0 once, batch TD(0) gives U(A) =', ['0', '0.75', '1', '0.5'], 1,
       'Markov model of the data.', 'A always led to B with reward 0, and U(B) = 0.75.')
K.quiz('x', 'In the style of a Berkeley CS285 exam: the deadly triad that can make TD diverge is', ['bias, variance, noise', 'function approximation, bootstrapping and off policy data', 'states, actions, rewards', 'α, γ, λ'], 1,
       'Sutton and Barto, section 11.3.', 'Any two are safe. All three together can blow up.')

# ---------------------------------------------------------------- calc
K.calc('e', 'Reward to go of (1,1) in textbook trial 1 (7 steps at −0.04, then +1).', '0.72', '−0.28 + 1.',
       ['7 × (−0.04) = −0.28.', 'Plus 1.', eq('0.72')], check=0.72, tol=0.0005)
K.calc('e', 'Reward to go of (1,1) in textbook trial 3 (4 steps at −0.04, then −1).', '-1.16', '−0.16 − 1.',
       ['4 × (−0.04) = −0.16.', 'Then −1.', eq('−1.16')], check=-1.16, tol=0.0005)
K.calc('e', 'ADP estimate P̂((2,3) | (1,3), Right) from the three trials. Give 3 decimals.', '0.667', '2 of 3 moves.',
       ['(1,3) was left 3 times.', '2 of them went to (2,3).', eq('2 ÷ 3 ≈ 0.667')], check=0.667, tol=0.001)
K.calc('m', 'Direct estimate of U(1,1) from the three trials, to 4 decimals.', '0.0933', 'Average 0.72, 0.72 and −1.16.',
       ['Sum: 0.72 + 0.72 − 1.16 = 0.28.', 'Divide by 3.', eq('≈ 0.0933')], check=0.0933, tol=0.0005)
K.calc('m', 'TD update: U(s) = 0.5, U(s′) = 0.8, R = −0.04, γ = 1, α = 0.1. New U(s)?', '0.526', 'δ = 0.26.',
       ['δ = −0.04 + 0.8 − 0.5 = 0.26.', 'α δ = 0.026.', eq('0.526')], check=0.526, tol=0.0005)
K.calc('m', 'TD error δ with r = 0, γ = 0.9, V(s′) = 0.6, V(s) = 0.5.', '0.04', 'r + γV(s′) − V(s).',
       ['0.9 × 0.6 = 0.54.', '0.54 − 0.5.', eq('0.04')], check=0.04, tol=0.0005)
K.calc('m', 'Learning rate α = 60 ÷ (59 + n) after n = 61 visits.', '0.5', '60 ÷ 120.',
       ['59 + 61 = 120.', '60 ÷ 120.', eq('0.5')], check=0.5, tol=0.0005)
K.calc('m', 'True value of state D in the five state random walk (exit right gives 1). Give 3 decimals.', '0.667', 'States A to E have values 1/6 to 5/6.',
       ['The chance of leaving on the right from the k-th state is k ÷ 6.', 'D is the 4th state.', eq('4 ÷ 6 ≈ 0.667')], check=0.667, tol=0.001)
K.calc('h', 'An eligibility trace with γ = 0.9 and λ = 0.8, three steps after the visit. Give 3 decimals.', '0.373', '(γλ)³.',
       ['γλ = 0.72.', '0.72³.', eq('≈ 0.373')], check=0.373, tol=0.001)
K.calc('x', 'Batch TD(0) on: A, 0, B, 0 once, B, 1 six times, B, 0 once. U(A)?', '0.75', 'U(A) = 0 + U(B).',
       ['U(B) = 6 ÷ 8 = 0.75.', 'A always moved to B with reward 0.', eq('U(A) = 0.75')], check=0.75, tol=0.0005)

# ---------------------------------------------------------------- assignments
TRI = '''TRIALS = [["11", "12", "13", "12", "13", "23", "33", "43"],
          ["11", "12", "13", "23", "33", "32", "33", "43"],
          ["11", "21", "31", "32", "42"]]
END = {"43": 1.0, "42": -1.0}
'''
K.assign('direct', 'e', 'Direct utility estimation',
         '<p>Write <code>direct(trials, end, step)</code> that returns a dictionary from each visited non end square to the average of its rewards to go. Every step from a square costs step, and the last square gives end[last]. Count every visit.</p>',
         TRI + '''
def direct(trials, end, step):
    # your code here
    pass
''', [("round(direct(TRIALS, END, -0.04)['11'], 4)", 0.0933), ("round(direct(TRIALS, END, -0.04)['33'], 4)", 0.9333),
      ("round(direct(TRIALS, END, -0.04)['21'], 2)", -1.12), ("sorted(direct(TRIALS, END, -0.04))", ['11', '12', '13', '21', '23', '31', '32', '33'])],
         TRI + '''
def direct(trials, end, step):
    total = {}
    count = {}
    for t in trials:
        for i in range(len(t) - 1):
            to_go = step * (len(t) - 1 - i) + end[t[-1]]
            s = t[i]
            total[s] = total.get(s, 0) + to_go
            count[s] = count.get(s, 0) + 1
    result = {}
    for s in total:
        result[s] = total[s] / count[s]
    return result
''', 'The square at position i of a trial has len(t) − 1 − i steps before the end.', '<p>(3,3) is visited 3 times with rewards to go 0.96, 0.96 and 0.88.</p>')
K.assign('tdup', 'e', 'One TD update',
         '<p>Write <code>td_update(u_s, r, u_next, alpha, gamma)</code> that returns the new U(s) after one TD(0) update.</p>',
         '''
def td_update(u_s, r, u_next, alpha, gamma):
    # your code here
    pass
''', [("round(td_update(0.5, -0.04, 0.8, 0.1, 1.0), 4)", 0.526), ("round(td_update(0.5, 0.0, 0.6, 0.5, 0.9), 4)", 0.52),
      ("td_update(1.0, 0.0, 1.0, 0.3, 1.0)", 1.0)],
         '''
def td_update(u_s, r, u_next, alpha, gamma):
    error = r + gamma * u_next - u_s
    return u_s + alpha * error
''', 'Compute the TD error first.', '<p>Test 3: the target equals the guess, so nothing changes.</p>')
K.assign('tdwalk', 'm', 'TD(0) on the random walk',
         '<p>Write <code>td_walk(episodes, alpha, seed)</code> for the five state random walk (start at C, step left or right with chance 1/2 using <code>rng.random() < 0.5</code> for right, reward 1 only when leaving on the right, γ = 1, all values start at 0.5). Return the dictionary of values.</p>',
         '''import random

def td_walk(episodes, alpha, seed):
    rng = random.Random(seed)
    # your code here
    pass
''', [("all(abs(td_walk(2000, 0.02, 1)[s] - (k + 1) / 6) < 0.1 for k, s in enumerate('ABCDE'))", True),
      ("all(abs(td_walk(2000, 0.02, 9)[s] - (k + 1) / 6) < 0.1 for k, s in enumerate('ABCDE'))", True)],
         '''import random

def td_walk(episodes, alpha, seed):
    rng = random.Random(seed)
    names = ["A", "B", "C", "D", "E"]
    V = {}
    for s in names:
        V[s] = 0.5
    for e in range(episodes):
        i = 2
        while 0 <= i <= 4:
            if rng.random() < 0.5:
                j = i + 1
            else:
                j = i - 1
            if j < 0:
                target = 0.0
            elif j > 4:
                target = 1.0
            else:
                target = V[names[j]]
            V[names[i]] = V[names[i]] + alpha * (target - V[names[i]])
            i = j
    return V
''', 'The target is 0 when leaving on the left, 1 when leaving on the right, and V of the next state otherwise.', '<p>With a small α the values settle near 1/6, 2/6, 3/6, 4/6 and 5/6.</p>')

K.must('Passive RL', 'Fixed π, unknown P and R, learn U^π from trials. Direct estimation, ADP, TD.')
K.must('TD(0)', 'U(s) ← U(s) + α (R(s) + γ U(s′) − U(s)). δ = TD error. Robbins Monro: Σα = ∞, Σα² < ∞.')
K.must('ADP', 'P̂(s′ | s, a) = N(s, a, s′) ÷ N(s, a), then policy evaluation. Fewest trials, most work per step.')
K.must('Bias and variance', 'Monte Carlo return: unbiased, high variance. TD target: biased, low variance. TD(λ) mixes.')
K.must('Key numbers', 'Three trials: U(1,1) ≈ 0.0933 (true 0.705). P̂((2,3) | (1,3)) = 2/3. Random walk values k ÷ 6.')

T = K.topic(
    slug='passive-rl', topic='passive-rl', step=STEP10,
    title='Passive reinforcement learning', short='Passive RL', badge='10.2', minutes=45,
    lead='Learn how good a fixed policy is from experience alone. Average rewards to go, learn a model and solve it, or update after every step with temporal difference learning.',
    desc='Reinforcement learning without a model, passive learning of a fixed policy, direct utility estimation, adaptive dynamic programming with learned transition models, temporal difference learning, the TD error, learning rate schedules and the Robbins Monro conditions, TD(λ) and eligibility traces, bias and variance of Monte Carlo and TD targets, batch TD, and TD-Gammon.',
    summary='Direct utility estimation, adaptive dynamic programming and temporal difference learning for a fixed policy.',
    keywords=['passive reinforcement learning', 'direct utility estimation', 'adaptive dynamic programming', 'temporal difference', 'TD error', 'learning rate', 'TD lambda', 'Monte Carlo'],
    recap='<p>Fixed π. Average rewards to go, or learn P̂ and solve, or TD: U(s) += α(R + γU(s′) − U(s)).</p>',
    nb={'trials': 'Direct estimation and a learned model from three trials', 'td': 'TD(0) on the five state random walk'})
