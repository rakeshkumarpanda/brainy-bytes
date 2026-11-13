# Reinforcement 2.2: Monte Carlo and temporal difference learning. Checked against Sutton and Barto, Reinforcement
# Learning: An Introduction (2nd edition, 2018) chapters 5, 6, 7 and 12 (example 6.2 random walk, example 6.4 batch
# updating), Sutton, Learning to Predict by the Methods of Temporal Differences (Machine Learning 1988), Tesauro,
# TD-Gammon (Communications of the ACM 1995), and Singh and Sutton, Reinforcement Learning with Replacing Eligibility
# Traces (1996).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-td')
K = Kit()

K.code('mc_prediction', r'''
import numpy as np

# Random walk: states A to E (1 to 5) between two ends. Start in C, step left or right with chance 1/2.
# Reaching the right end gives reward 1, everything else 0. True values: 1/6, 2/6, 3/6, 4/6, 5/6.
rng = np.random.default_rng(0)
true_v = np.arange(1, 6) / 6

def episode():
    s, visited = 3, []
    while 1 <= s <= 5:
        visited.append(s)
        s += rng.choice([-1, 1])
    return visited, 1.0 if s == 6 else 0.0               # the states seen and the final reward

V, N = np.full(7, 0.5), np.zeros(7)                       # start every estimate at 0.5
for ep in range(1, 1001):
    visited, G = episode()                               # gamma = 1 and one final reward, so every state's return is G
    for s in set(visited):                               # first visit Monte Carlo: average the returns seen
        N[s] += 1
        V[s] += (G - V[s]) / N[s]
    if ep in (1, 10, 100, 1000):
        print("after", str(ep).rjust(4), "episodes:", V[1:6].round(3), " RMS error", round(float(np.sqrt(np.mean((V[1:6] - true_v) ** 2))), 3))
print("true values:              ", true_v.round(3))
''', long=True)

K.code('td_prediction', r'''
import numpy as np

rng = np.random.default_rng(0)
true_v = np.arange(1, 6) / 6
V = np.full(7, 0.5)
V[0] = V[6] = 0.0                                        # the two ends are terminal: value 0
alpha = 0.1
for ep in range(1, 1001):
    s = 3
    while 1 <= s <= 5:
        s2 = s + rng.choice([-1, 1])
        r = 1.0 if s2 == 6 else 0.0
        td_error = r + V[s2] - V[s]                       # TD target r + gamma V(s'), with gamma = 1
        V[s] += alpha * td_error                          # update now, without waiting for the episode to end
        s = s2
    if ep in (1, 10, 100, 1000):
        print("after", str(ep).rjust(4), "episodes:", V[1:6].round(3), " RMS error", round(float(np.sqrt(np.mean((V[1:6] - true_v) ** 2))), 3))
print("true values:              ", true_v.round(3))
''', long=True)

K.code('mc_vs_td', r'''
import numpy as np

true_v = np.arange(1, 6) / 6
runs, episodes = 100, 100
rng = np.random.default_rng(1)

def run(method, alpha):
    err = np.zeros(episodes)
    for _ in range(runs):
        V = np.full(7, 0.5)
        V[0] = V[6] = 0.0
        for ep in range(episodes):
            s, path = 3, []
            while 1 <= s <= 5:
                s2 = s + (1 if rng.random() < 0.5 else -1)
                r = 1.0 if s2 == 6 else 0.0
                if method == "TD":
                    V[s] += alpha * (r + V[s2] - V[s])
                path.append(s)
                s = s2
            if method == "MC":
                G = 1.0 if s == 6 else 0.0
                for x in path:                           # every visit Monte Carlo with a constant step size
                    V[x] += alpha * (G - V[x])
            err[ep] += np.sqrt(np.mean((V[1:6] - true_v) ** 2))
    return err / runs

for method, alpha in [("MC", 0.01), ("MC", 0.03), ("TD", 0.05), ("TD", 0.15)]:
    e = run(method, alpha)
    print(method, "alpha", str(alpha).ljust(4), " RMS error after 10, 50, 100 episodes:", e[9].round(3), e[49].round(3), e[99].round(3))
''', long=True)

K.code('batch_mc_td', r'''
# Sutton and Barto example 6.4. Eight episodes were observed:
# A,0,B,0 once, then B,1 six times, then B,0 once. What are V(A) and V(B)?
episodes = [[("A", 0), ("B", 0)]] + [[("B", 1)]] * 6 + [[("B", 0)]]

# Monte Carlo: average the returns that followed each state
returns = {"A": [], "B": []}
for ep in episodes:
    for i, (s, _) in enumerate(ep):
        returns[s].append(sum(r for _, r in ep[i:]))
print("Monte Carlo:", {s: round(sum(g) / len(g), 3) for s, g in returns.items()})

# Batch TD(0): sweep the same data again and again with small steps until the values settle
V = {"A": 0.0, "B": 0.0, "end": 0.0}
for _ in range(3000):
    for ep in episodes:
        for i, (s, r) in enumerate(ep):
            nxt = ep[i + 1][0] if i + 1 < len(ep) else "end"
            V[s] += 0.01 * (r + V[nxt] - V[s])
print("Batch TD:   ", {s: round(V[s], 3) for s in ("A", "B")})
''', long=True)

K.lesson('idea', 'Learning without a model: Monte Carlo prediction', f'''
{src('Sutton and Barto (2018) sections 5.1 and 5.2, and example 6.2 (the random walk).')}
{wwh('When the transition probabilities are unknown, the agent can still learn values from experience. <b>Monte Carlo</b> (MC) prediction plays whole episodes and, for each state visited, averages the returns that actually followed it. <b>First visit</b> MC counts only the first visit to a state in an episode, <b>every visit</b> MC counts them all.',
     'Most real problems have no model: nobody can write down the chance of every outcome in a game against people, or in a robot’s contact with the floor. MC needs only the ability to run episodes, in the world or in a simulator, and its estimates have no bias because they average real returns.',
     'Run an episode with the policy. Walk backwards through it to compute the return G from each step. Update V(s) towards G with a running average or a small constant step size. Repeat for many episodes.')}
{run('mc_prediction')}
{note('The walk starts in C and moves left or right at random. Reaching the right end gives 1, so the true value of a state is its chance of finishing on the right: 1/6 to 5/6. After one episode MC knows only that one walk ended on the right. After 1,000 episodes its averages are within 0.011 of the truth (RMS error). MC is unbiased but needs many episodes because single returns vary a lot.', 'exam')}
{fxs(fx('Monte Carlo update', 'V(S<sub>t</sub>) &larr; V(S<sub>t</sub>) + &alpha;[G<sub>t</sub> &minus; V(S<sub>t</sub>)]', 'Target: the full return G<sub>t</sub>. Waits for the episode to end.', key=True),
     fx('Sample average form', '&alpha; = 1 / N(S<sub>t</sub>)', 'Converges to v<sub>&pi;</sub> by the law of large numbers.'))}
''', kw=['Monte Carlo prediction', 'first visit', 'every visit', 'model free', 'return', 'random walk'])

K.lesson('td', 'Temporal difference learning: TD(0)', f'''
{src('Sutton, Learning to Predict by the Methods of Temporal Differences (1988), and Sutton and Barto (2018) sections 6.1 to 6.3.')}
{viz('mltdstep')}
{wwh('<b>Temporal difference</b> (TD) learning updates after every single step. Its target is the reward just received plus the discounted current estimate of the next state: r + &gamma;V(s&prime;). The gap between target and old estimate is the <b>TD error</b> &delta;. Using an estimate to update an estimate is called <b>bootstrapping</b>.',
     'TD learns during the episode, works for tasks that never end, and its targets vary much less than full returns, so it usually learns faster than MC. It is the core of Q learning, SARSA, actor critic methods and DQN. Tesauro’s TD-Gammon learned to play backgammon at world class level with it in the early 1990s.',
     'After each step compute &delta; = r + &gamma;V(s&prime;) &minus; V(s) and set V(s) &larr; V(s) + &alpha;&delta;. Terminal states have value 0. Keep &alpha; small and constant for drifting problems, or shrink it over time for exact convergence.')}
{run('td_prediction')}
{note('TD reaches an error of 0.075 after 100 episodes, against MC’s 0.095 in the previous program. With a constant &alpha; of 0.1 it then keeps fluctuating around the truth (0.071 after 1,000 episodes) instead of settling, while MC with sample averages kept improving. A constant step size trades exact convergence for the ability to track change.', 'exam')}
{fxs(fx('TD(0) update', 'V(S<sub>t</sub>) &larr; V(S<sub>t</sub>) + &alpha;[R<sub>t+1</sub> + &gamma;V(S<sub>t+1</sub>) &minus; V(S<sub>t</sub>)]', 'Target: one reward plus a guess.', key=True),
     fx('TD error', '&delta;<sub>t</sub> = R<sub>t+1</sub> + &gamma;V(S<sub>t+1</sub>) &minus; V(S<sub>t</sub>)', 'Also the signal dopamine neurons appear to carry (Schultz, Dayan and Montague, 1997).', key=True),
     fx('MC error as TD errors', 'G<sub>t</sub> &minus; V(S<sub>t</sub>) = &Sigma;<sub>k&ge;t</sub> &gamma;<sup>k&minus;t</sup> &delta;<sub>k</sub>', 'If V does not change during the episode.'))}
''', kw=['temporal difference', 'TD(0)', 'TD error', 'bootstrapping', 'TD target', 'TD-Gammon', 'dopamine'])

K.lesson('compare', 'Monte Carlo against TD: bias, variance and batch learning', f'''
{src('Sutton and Barto (2018) sections 6.2 and 6.3, figure 6.2 and example 6.4.')}
{viz('mlmctd')}
{wwh('MC targets (whole returns) are <b>unbiased but high variance</b>: they include the randomness of every later step. TD targets are <b>biased but low variance</b>: they depend on one step of randomness plus a guess that may be wrong. On the same fixed data, MC finds the values that best fit the observed returns, while batch TD finds the values of the <b>most likely Markov model</b> behind the data.',
     'Knowing why TD usually wins, and when it does not, helps choose between them. TD exploits the Markov property. If the state is not truly Markov, MC can be safer.',
     'Compare them on the same episodes with several step sizes, as below, and look at the error curves over time. For batch data, replay the whole set many times with small steps until the values settle.')}
{run('mc_vs_td')}
{note('Averaged over 100 runs, TD with &alpha; = 0.05 reaches an error of 0.035 after 100 episodes, against 0.094 for MC with either step size. TD with a large &alpha; of 0.15 is fastest early (0.095 after 10 episodes) but then stalls near 0.07, because each step jumps too far. Step size matters as much as the method.', 'exam')}
{run('batch_mc_td')}
{note('Eight episodes: A then B with no reward once, then B alone six times with reward 1 and once with 0. Both methods give V(B) = 0.75. MC gives V(A) = 0, because the only return seen after A was 0. Batch TD gives V(A) = 0.75, because A always led to B and B is worth 0.75. TD’s answer is the one a Markov model of the data implies, and it usually predicts future data better.', 'tip')}
''', kw=['bias variance trade off', 'MC vs TD', 'batch TD', 'certainty equivalence', 'step size'])

K.lesson('nstep', 'Between the two: n step TD and TD(&lambda;)', f'''
{src('Sutton and Barto (2018) chapters 7 and 12, and Singh and Sutton (1996).')}
{wwh('<b>n step TD</b> uses n real rewards and then bootstraps: G<sub>t:t+n</sub> = R<sub>t+1</sub> + &gamma;R<sub>t+2</sub> + ... + &gamma;<sup>n&minus;1</sup>R<sub>t+n</sub> + &gamma;<sup>n</sup>V(S<sub>t+n</sub>). n = 1 is TD(0), and n = &infin; is Monte Carlo. <b>TD(&lambda;)</b> averages all n step returns with weights (1 &minus; &lambda;)&lambda;<sup>n&minus;1</sup>, and <b>eligibility traces</b> compute this online, step by step.',
     'An intermediate n often beats both ends: fewer steps of variance than MC, less reliance on wrong guesses than TD(0). Eligibility traces also solve the <b>credit assignment</b> problem neatly: each TD error is shared among recently visited states, more for more recent ones.',
     'Try n between 2 and 10, or &lambda; between 0.7 and 0.95. With traces: keep e(s) for every state, decay all traces by &gamma;&lambda; each step, add 1 to the current state’s trace, and update every state by &alpha;&delta;e(s).')}
{table(['Method', 'Target', 'Bias', 'Variance', 'Updates'], [
    ['TD(0)', 'r + &gamma;V(s&prime;)', 'Higher', 'Lowest', 'Every step'],
    ['n step TD', 'n rewards + &gamma;<sup>n</sup>V', 'Medium', 'Medium', 'n steps late'],
    ['TD(&lambda;)', 'Weighted mix of all n step returns', 'Tunable', 'Tunable', 'Every step, with traces'],
    ['Monte Carlo', 'Full return G', 'None', 'Highest', 'End of episode']])}
{steps('TD(&lambda;) with accumulating traces, one step', [
    'Compute &delta; = r + &gamma;V(s&prime;) &minus; V(s).',
    'Increase the trace of the current state: e(s) &larr; e(s) + 1.',
    'For every state x: V(x) &larr; V(x) + &alpha;&delta;e(x).',
    'Decay every trace: e(x) &larr; &gamma;&lambda;e(x).',
    'Move to s&prime;. At the end of an episode reset all traces to 0.'])}
''', kw=['n step TD', 'TD lambda', 'eligibility traces', 'lambda return', 'credit assignment'])

K.lesson('versus', 'Prediction methods compared', f'''
{versus('Three ways to estimate v<sub>&pi;</sub>', ['', 'Dynamic programming', 'Monte Carlo', 'Temporal difference'], [
    ['Needs a model', 'Yes', 'No', 'No'],
    ['Bootstraps', 'Yes', 'No', 'Yes'],
    ['Samples', 'No (expected updates)', 'Yes (whole episodes)', 'Yes (single steps)'],
    ['Works without episode ends', 'Yes', 'No', 'Yes'],
    ['Bias, variance', 'No sampling noise', 'Unbiased, high variance', 'Biased, low variance'],
    ['Uses the Markov property', 'Yes', 'No', 'Yes']],
    'use DP when you have the model, TD as the default when learning from experience, and MC when episodes are short and the state may not be Markov.')}
''', kw=['DP vs MC vs TD', 'bootstrapping vs sampling', 'model free prediction'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Return', 'G<sub>t</sub> = R<sub>t+1</sub> + &gamma;G<sub>t+1</sub>', 'The Monte Carlo target.', key=True),
     fx('TD(0)', 'V(s) &larr; V(s) + &alpha;[r + &gamma;V(s&prime;) &minus; V(s)]', 'The TD target bootstraps.', key=True),
     fx('n step return', 'G<sub>t:t+n</sub> = &Sigma;<sub>k=0</sub><sup>n&minus;1</sup> &gamma;<sup>k</sup>R<sub>t+k+1</sub> + &gamma;<sup>n</sup>V(S<sub>t+n</sub>)', 'n = 1 TD(0), n = &infin; MC.', key=True),
     fx('&lambda; return', 'G<sub>t</sub><sup>&lambda;</sup> = (1 &minus; &lambda;) &Sigma;<sub>n&ge;1</sub> &lambda;<sup>n&minus;1</sup> G<sub>t:t+n</sub>', '&lambda; = 0 TD(0), &lambda; = 1 MC.'),
     fx('Accumulating trace', 'e<sub>t</sub>(s) = &gamma;&lambda;e<sub>t&minus;1</sub>(s) + 1[S<sub>t</sub> = s]', 'Recent and frequent states get more credit.'),
     fx('Robbins Monro conditions', '&Sigma; &alpha;<sub>t</sub> = &infin;, &Sigma; &alpha;<sub>t</sub><sup>2</sup> &lt; &infin;', 'Step sizes that guarantee convergence, such as 1/t.'),
     fx('Random walk truth', 'v(k) = k / 6 for states k = 1 to 5', 'Gambler’s ruin with a fair coin.'))}
{steps('Worked example: one TD update and one MC update', [
    'V(s) = 0.5, the next state has V(s&prime;) = 0.7, reward 0, &gamma; = 1, &alpha; = 0.1.',
    eq('TD: &delta; = 0 + 0.7 &minus; 0.5 = 0.2, so V(s) = 0.5 + 0.1 &times; 0.2 = 0.52'),
    'Suppose the episode later ends on the right, so the return from s is G = 1.',
    eq('MC: V(s) = 0.5 + 0.1 &times; (1 &minus; 0.5) = 0.55'),
    'TD moved towards its neighbour’s guess at once. MC waited and moved towards what really happened.'])}
{deep('Why TD converges, and when it can fail', '<p>For a fixed policy and a table of values, TD(0) converges to v<sub>&pi;</sub> with probability 1 if every state is visited infinitely often and the step sizes meet the Robbins Monro conditions (Sutton 1988, Dayan 1992, Jaakkola, Jordan and Singh 1994). With linear function approximation and on policy data, TD converges to a point close to the best linear fit (Tsitsiklis and Van Roy, 1997). The danger appears when three things combine, which Sutton and Barto call the <b>deadly triad</b>: function approximation, bootstrapping and off policy training. Then values can diverge, which is why DQN needs extra tricks such as target networks (chapter 3.1).</p>')}
''', kw=['TD update formula', 'n step return', 'lambda return', 'eligibility trace', 'Robbins Monro', 'deadly triad'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Without a map of the world, you can still learn how good each place is: either wait to see how things end (Monte Carlo) or adjust after every step using your next guess (TD).</p>',
    '<p>Code first visit MC and TD(0), compute TD errors, compare their learning curves, and choose a step size.</p>',
    '<p>Explain bias and variance of MC and TD targets, batch TD as the certainty equivalence estimate, n step returns and TD(&lambda;) with eligibility traces.</p>',
    '<p>Study convergence proofs, TD with function approximation and the deadly triad, true online TD(&lambda;), emphatic TD, and the TD error as a model of dopamine signals.</p>')}
{grow('Explain how values can be learned from experience alone.',
      'Implement and compare MC and TD prediction.',
      'Analyse bias, variance and convergence of TD methods.')}
''', kw=['beginner', 'expert', 'true online TD', 'emphatic TD'])

lc(933, 'Number of Recent Calls', 'number-of-recent-calls', 'e', 'Keep a queue and drop old calls from the front', 'Add each call to the back and remove calls older than 3,000 milliseconds from the front. Keeping only recent history is what a constant step size does to an estimate: old data fades out. Our helper returns the count after each ping.', r"""
from collections import deque


class RecentCounter:
    def __init__(self):
        self.calls = deque()

    def ping(self, t):
        self.calls.append(t)
        while self.calls[0] < t - 3000:
            self.calls.popleft()
        return len(self.calls)


def recent_counts(times):
    rc = RecentCounter()
    return [rc.ping(t) for t in times]
""", [('recent_counts([1, 100, 3001, 3002])', [1, 2, 3, 3])])
lc(1716, 'Calculate Money in Leetcode Bank', 'calculate-money-in-leetcode-bank', 'e', 'Day d deposits d // 7 + d % 7 + 1', 'Each Monday starts one higher than the last, and each day adds one more. Adding up rewards day by day is how a Monte Carlo return is built.', r"""
def total_money(n):
    total = 0
    for d in range(n):
        total += d // 7 + d % 7 + 1
    return total
""", [('total_money(4)', 10), ('total_money(10)', 37), ('total_money(20)', 96)])
lc(1352, 'Product of the Last K Numbers', 'product-of-the-last-k-numbers', 'm', 'Prefix products, reset at every zero', 'Keep running products. The product of the last k numbers is the last prefix divided by the one k places earlier. A zero wipes the history, so restart the list. Running quantities that let you answer about any recent window are the idea behind n step returns. Our helper runs a list of operations.', r"""
class ProductOfNumbers:
    def __init__(self):
        self.prefix = [1]

    def add(self, num):
        if num == 0:
            self.prefix = [1]
        else:
            self.prefix.append(self.prefix[-1] * num)

    def get_product(self, k):
        if k >= len(self.prefix):
            return 0
        return self.prefix[-1] // self.prefix[-1 - k]


def product_run(ops):
    p, out = ProductOfNumbers(), []
    for op in ops:
        if op[0] == "add":
            p.add(op[1])
        else:
            out.append(p.get_product(op[1]))
    return out
""", [('product_run([["add", 3], ["add", 0], ["add", 2], ["add", 5], ["add", 4], ["get", 2], ["get", 3], ["get", 4], ["add", 8], ["get", 2]])', [20, 40, 0, 32])])
lc(1423, 'Maximum Points You Can Obtain from Cards', 'maximum-points-you-can-obtain-from-cards', 'm', 'Taking k cards from the ends leaves a middle window of n minus k cards', 'Find the middle window with the smallest sum by sliding it across, and subtract it from the total. Sliding a fixed size window and updating its sum in O(1) per step is the same bookkeeping an n step TD learner keeps.', r"""
def max_score(card_points, k):
    n = len(card_points)
    window = sum(card_points[:n - k])
    low = window
    for i in range(n - k, n):
        window += card_points[i] - card_points[i - (n - k)]
        low = min(low, window)
    return sum(card_points) - low
""", [('max_score([1, 2, 3, 4, 5, 6, 1], 3)', 12), ('max_score([2, 2, 2], 2)', 4), ('max_score([9, 7, 7, 9, 7, 7, 9], 7)', 55)])
lc(239, 'Sliding Window Maximum', 'sliding-window-maximum', 'h', 'A deque of indices with decreasing values', 'Before adding a new index, pop smaller values from the back, since they can never be a maximum again. Pop the front once it leaves the window. The front is always the current maximum. Each index enters and leaves once, so the whole pass is O(n).', r"""
from collections import deque


def max_sliding_window(nums, k):
    dq, out = deque(), []
    for i, v in enumerate(nums):
        while dq and nums[dq[-1]] <= v:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out
""", [('max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)', [3, 3, 5, 5, 6, 7]), ('max_sliding_window([1], 1)', [1])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>MC and TD keep running estimates over streams of experience. These problems practise forgetting old data with a queue, summing rewards over days, running products over recent windows, sliding window sums, and a monotonic deque for window maxima. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'sliding window', 'queue', 'deque', 'prefix product', 'streams'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Monte Carlo</b> averages real returns after episodes end. No model, no bias, high variance.',
    '<b>TD(0)</b> updates every step towards r + &gamma;V(s&prime;). The <b>TD error</b> &delta; drives learning. It bootstraps.',
    'TD usually learns faster on Markov problems because its targets vary less. Step size matters as much as the method.',
    'On fixed data, MC fits observed returns, batch TD fits the most likely Markov model (V(A) = 0 against 0.75).',
    '<b>n step TD</b> and <b>TD(&lambda;)</b> sit between TD(0) and MC. Eligibility traces share each TD error with recent states.',
    'Function approximation + bootstrapping + off policy data (the deadly triad) can diverge.'],
    'Reinforcement 2.3 turns prediction into control: SARSA, Q learning and expected SARSA on the cliff walk.')}
{files('Three tasks: a TD(0) update, first visit Monte Carlo averages, and an n step return.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Monte Carlo prediction updates a state’s value', ['After every step', 'After the episode ends, using the actual return', 'Using the model', 'Never'], 1, 'Waits for G.', 'Needs complete episodes.')
K.quiz('e', 'The TD target is', ['The full return', 'r + &gamma;V(s&prime;)', 'The reward only', 'The average reward'], 1, 'One step plus a guess.', 'Bootstrapping.')
K.quiz('e', 'Bootstrapping means', ['Restarting the computer', 'Updating an estimate from another estimate', 'Resampling data', 'Using labels'], 1, 'Guess from a guess.', 'DP and TD bootstrap, MC does not.')
K.quiz('e', 'Which methods need a model of the environment?', ['MC and TD', 'Only dynamic programming', 'Only TD', 'None'], 1, 'Expected updates.', 'MC and TD learn from samples.')
K.quiz('m', 'Compared with MC targets, TD targets have', ['More variance, no bias', 'Less variance, some bias', 'No variance', 'The same properties'], 1, 'One step of noise.', 'The guess V(s&prime;) can be wrong.')
K.quiz('m', 'TD can learn in continuing tasks with no episode end because', ['It ignores rewards', 'It updates after each step without waiting for a return', 'It uses a model', 'It needs labels'], 1, 'Online.', 'MC needs episodes to end.')
K.quiz('m', 'In example 6.4, batch MC gives V(A) = 0 and batch TD gives V(A) = 0.75 because TD', ['Has a bug', 'Uses the fact that A always led to B, which is worth 0.75', 'Ignores A', 'Uses a larger step'], 1, 'Markov model.', 'Certainty equivalence estimate.')
K.quiz('m', 'n step TD with n equal to the episode length is', ['TD(0)', 'Monte Carlo', 'Dynamic programming', 'Q learning'], 1, 'No bootstrapping left.', 'All real rewards.')
K.quiz('m', 'A constant step size &alpha; in TD means the estimates', ['Converge exactly', 'Keep fluctuating near the truth but can track changes', 'Diverge', 'Stay at 0'], 1, 'Recent data weighs more.', 'Shrink &alpha; for exact convergence.')
K.quiz('h', 'An eligibility trace e(s)', ['Stores rewards', 'Marks how recently and often s was visited, to share credit for each TD error', 'Is the policy', 'Is the discount'], 1, 'Decays by &gamma;&lambda;.', 'Backward view of TD(&lambda;).')
K.quiz('h', 'TD(&lambda;) with &lambda; = 1 behaves like', ['TD(0)', 'Monte Carlo', 'Value iteration', 'A bandit'], 1, 'Full returns.', '&lambda; = 0 is TD(0).')
K.quiz('h', 'The deadly triad is', ['Three bad rewards', 'Function approximation, bootstrapping and off policy training together', 'Three states', 'MC, TD and DP'], 1, 'Sutton and Barto chapter 11.', 'Can make values diverge.')
K.quiz('x', 'In the style of a Stanford CS234 exam: when the state is not truly Markov, which estimate is often safer?', ['TD(0)', 'Monte Carlo', 'Both are equal', 'Neither works'], 1, 'TD relies on the Markov property.', 'MC averages real returns.')
K.quiz('x', 'In the style of a Stanford CS234 exam: the step sizes &alpha;<sub>t</sub> = 1/t satisfy', ['Neither condition', 'Both Robbins Monro conditions', 'Only &Sigma; &alpha;<sup>2</sup> &lt; &infin;', 'Only &Sigma; &alpha; = &infin;'], 1, 'Harmonic series diverges, squares converge.', 'So they guarantee convergence.')

K.calc('e', 'V(s) = 0.5, reward 0, V(s&prime;) = 0.7, &gamma; = 1, &alpha; = 0.1. New V(s) after TD(0)?', '0.52', 'V + &alpha;&delta;.', ['&delta; = 0 + 0.7 &minus; 0.5 = 0.2.', '&alpha;&delta; = 0.02.', eq('0.5 + 0.02 = 0.52')], check=0.52)
K.calc('e', 'V(s) = 0.5, return G = 1, &alpha; = 0.1. New V(s) after a Monte Carlo update?', '0.55', 'V + &alpha;(G &minus; V).', ['G &minus; V = 0.5.', '&alpha; &times; 0.5 = 0.05.', eq('0.5 + 0.05 = 0.55')], check=0.55)
K.calc('m', 'r = 1, V(s&prime;) = 2, V(s) = 2, &gamma; = 0.9. TD error?', '0.8', 'r + &gamma;V(s&prime;) &minus; V(s).', ['&gamma;V(s&prime;) = 1.8.', 'Target = 2.8.', eq('2.8 &minus; 2 = 0.8')], check=0.8)
K.calc('m', 'Random walk with 5 states A to E between two ends, reward 1 for the right end. True value of B?', '0.333', 'Chance of finishing right.', ['B is position 2 of 6.', 'Fair walk: chance k / N.', eq('2 / 6 = 0.333')], check=0.3333, tol=0.001)
K.calc('m', 'Rewards 0 then 0, then bootstrap from V = 0.5 two steps ahead, &gamma; = 0.9. The 2 step return?', '0.405', '&gamma;<sup>2</sup>V.', ['Rewards add 0.', '&gamma;<sup>2</sup> = 0.81.', eq('0.81 &times; 0.5 = 0.405')], check=0.405)
K.calc('m', 'Example 6.4: B was followed by reward 1 in 6 of 8 visits, and A always led to B with reward 0. Batch TD value of A?', '0.75', 'V(A) = 0 + V(B).', ['V(B) = 6 / 8.', 'A gives 0 and then B.', eq('V(A) = 0.75')], check=0.75)
K.calc('h', 'Weight of the 3 step return in the &lambda; return with &lambda; = 0.8?', '0.128', '(1 &minus; &lambda;)&lambda;<sup>n&minus;1</sup>.', ['1 &minus; &lambda; = 0.2.', '&lambda;<sup>2</sup> = 0.64.', eq('0.2 &times; 0.64 = 0.128')], check=0.128)
K.calc('h', 'A state was visited once, 3 steps ago. &gamma; = 0.9, &lambda; = 0.8. Its accumulating trace now?', '0.373', '(&gamma;&lambda;)<sup>3</sup>.', ['&gamma;&lambda; = 0.72.', '0.72<sup>2</sup> = 0.5184.', eq('0.5184 &times; 0.72 = 0.373')], check=0.3732, tol=0.001)
K.calc('h', 'Random walk from C (position 3 of 6). Expected number of steps until an end?', '9', 'k(N &minus; k).', ['k = 3.', 'N &minus; k = 3.', eq('3 &times; 3 = 9')], check=9)
K.calc('x', 'In the style of a Stanford CS234 problem: in example 6.4, the single return observed after A was 0. Squared error of the batch TD estimate V(A) = 0.75 on that return?', '0.5625', '(G &minus; V)<sup>2</sup>.', ['G &minus; V = &minus;0.75.', 'Square it.', eq('0.5625, while MC’s V(A) = 0 has error 0 on the training data')], check=0.5625)

K.assign('td0_update', 'e', 'A TD(0) update',
         '<p>Write <code>td0_update(V, s, r, s2, alpha, gamma)</code>. V is a dictionary of values. Return the new value of V[s] after one TD(0) update, rounded to 4 decimals. Treat a next state s2 that is missing from V as terminal (value 0).</p>',
         """
def td0_update(V, s, r, s2, alpha, gamma):
    # your code here
    pass
""", [('td0_update({"a": 0.5, "b": 0.7}, "a", 0, "b", 0.1, 1.0)', 0.52), ('td0_update({"a": 2.0, "b": 2.0}, "a", 1, "b", 0.5, 0.9)', 2.4), ('td0_update({"e": 0.5}, "e", 1, "end", 0.1, 1.0)', 0.55)],
         """
def td0_update(V, s, r, s2, alpha, gamma):
    target = r + gamma * V.get(s2, 0.0)
    return round(V[s] + alpha * (target - V[s]), 4)
""", 'Target r + gamma V(s2), then move V(s) a fraction alpha towards it.', '<p>Using V.get with a default of 0 is a tidy way to give terminal states value 0.</p>')
K.assign('mc_first_visit', 'm', 'First visit Monte Carlo',
         '<p>Write <code>mc_first_visit(episodes)</code>. Each episode is a list of [state, reward] pairs, where the reward follows that state. With &gamma; = 1, return a dictionary from each state to the average of the returns after its first visit in each episode, rounded to 3 decimals.</p>',
         """
def mc_first_visit(episodes):
    # your code here
    pass
""", [('mc_first_visit([[["A", 0], ["B", 0]]] + [[["B", 1]]] * 6 + [[["B", 0]]])', {'A': 0.0, 'B': 0.75}), ('mc_first_visit([[["x", 1], ["y", 2], ["x", 3]], [["y", 4]]])', {'x': 6.0, 'y': 4.5})],
         """
def mc_first_visit(episodes):
    totals, counts = {}, {}
    for ep in episodes:
        G = 0
        first = {}
        for i in range(len(ep) - 1, -1, -1):
            s, r = ep[i]
            G = G + r
            first[s] = G
        for s, g in first.items():
            totals[s] = totals.get(s, 0) + g
            counts[s] = counts.get(s, 0) + 1
    return {s: round(totals[s] / counts[s], 3) for s in totals}
""", 'Walk each episode backwards. The last time you write a state’s return going backwards is its first visit.', '<p>In the second test, x is visited twice in the first episode. Its first visit return is 1 + 2 + 3 = 6, and the later visit (return 3) is ignored.</p>')
K.assign('n_step_return', 'm', 'n step return',
         '<p>Write <code>n_step_return(rewards, v_boot, gamma)</code>: the n step return &Sigma; &gamma;<sup>k</sup> rewards[k] + &gamma;<sup>n</sup> v_boot, where n is the number of rewards. Round to 4 decimals.</p>',
         """
def n_step_return(rewards, v_boot, gamma):
    # your code here
    pass
""", [('n_step_return([0, 0], 0.5, 0.9)', 0.405), ('n_step_return([1], 2.0, 0.9)', 2.8), ('n_step_return([1, 1, 1], 0.0, 0.5)', 1.75)],
         """
def n_step_return(rewards, v_boot, gamma):
    G = v_boot
    for r in reversed(rewards):
        G = r + gamma * G
    return round(G, 4)
""", 'Start from the bootstrap value and fold the rewards in backwards.', '<p>With one reward this is the TD(0) target, and with v_boot = 0 at the end of an episode it is the Monte Carlo return.</p>')

K.must('MC', 'V(s) &larr; V(s) + &alpha;(G &minus; V(s)). Full returns, no model, unbiased, high variance, needs episode ends.')
K.must('TD(0)', '&delta; = r + &gamma;V(s&prime;) &minus; V(s), V(s) &larr; V(s) + &alpha;&delta;. Bootstraps, online, lower variance, biased.')
K.must('Compare', 'TD usually faster on Markov problems. Batch MC fits returns, batch TD fits the Markov model (example 6.4).')
K.must('Step size', 'Constant &alpha; tracks change but fluctuates. Robbins Monro: &Sigma; &alpha; = &infin;, &Sigma; &alpha;<sup>2</sup> &lt; &infin;.')
K.must('n step and &lambda;', 'G<sub>t:t+n</sub> mixes n rewards and a bootstrap. TD(&lambda;) weights (1 &minus; &lambda;)&lambda;<sup>n&minus;1</sup>. Traces decay by &gamma;&lambda;.')
K.must('Warning', 'Deadly triad: function approximation + bootstrapping + off policy can diverge.')

T = K.topic(
    slug='ml-td', topic='ml-td', step=(2, 'Solving MDPs', 'ml-r2', 'Find good policies: plan with a known model by dynamic programming, then learn from experience with Monte Carlo, temporal difference learning, SARSA and Q learning.', 'Advanced'),
    title='Monte Carlo and temporal difference learning', short='Monte Carlo and TD', badge='2.2', minutes=50,
    lead='Learn values from experience without a model: Monte Carlo prediction, TD(0) and the TD error, bias against variance, batch updating, n step returns, TD(lambda) and eligibility traces.',
    desc='Monte Carlo prediction, first visit, every visit, temporal difference learning, TD(0), TD error, bootstrapping, random walk, bias variance, batch TD, certainty equivalence, n step TD, TD lambda, eligibility traces, Robbins Monro, deadly triad.',
    summary='Monte Carlo and TD(0) prediction, their bias and variance, batch updating, n step TD and TD(lambda).',
    keywords=['Monte Carlo', 'temporal difference', 'TD learning', 'TD error', 'bootstrapping', 'eligibility traces', 'TD lambda', 'n step TD', 'random walk', 'model free'],
    recap='<p>Without a model, learn from experience. MC waits for real returns, TD updates every step from its own next guess. TD usually learns faster, and n step methods and traces blend the two.</p>',
    added='2026-11-13', leet=leet_items())
