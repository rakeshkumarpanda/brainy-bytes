# Reinforcement 1.2: multi armed bandits. Checked against Sutton and Barto, Reinforcement Learning: An Introduction
# (2nd edition, 2018) chapter 2, Auer, Cesa-Bianchi and Fischer, Finite-time Analysis of the Multiarmed Bandit Problem
# (Machine Learning 2002), Lai and Robbins, Asymptotically Efficient Adaptive Allocation Rules (1985), Thompson (1933),
# Chapelle and Li, An Empirical Evaluation of Thompson Sampling (NeurIPS 2011), Russo and colleagues, A Tutorial on
# Thompson Sampling (2018), and Li, Chu, Langford and Schapire, LinUCB (WWW 2010).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-bandits')
K = Kit()

K.code('incremental_mean', r'''
rewards = [4, 6, 5, 9, 1]
Q, n = 0.0, 0
for r in rewards:
    n += 1
    Q = Q + (r - Q) / n                                  # new estimate = old + step size * (target - old)
    print("reward", r, " estimate after", n, "pulls:", round(Q, 3))
print("plain average:", sum(rewards) / len(rewards))

# A constant step size forgets old rewards, which helps when the arm changes over time
Q, alpha = 0.0, 0.5
for r in [1, 1, 1, 10, 10, 10]:
    Q = Q + alpha * (r - Q)
    print("constant step 0.5, reward", r, " estimate", round(Q, 3))
''')

K.code('epsilon_greedy', r'''
import numpy as np

true_means = np.array([0.2, 0.5, 0.8, 0.3, 0.6])         # arm 2 is best, but the agent does not know
runs, steps = 500, 1000                                  # 500 separate experiments, played side by side
rng = np.random.default_rng(0)
rows = np.arange(runs)

def play(eps):
    Q, N = np.zeros((runs, 5)), np.zeros((runs, 5))
    total, best = 0.0, 0
    for t in range(steps):
        explore = rng.random(runs) < eps
        a = np.where(explore, rng.integers(0, 5, runs), Q.argmax(axis=1))
        r = rng.normal(true_means[a], 1.0)               # noisy reward
        N[rows, a] += 1
        Q[rows, a] += (r - Q[rows, a]) / N[rows, a]      # incremental average
        total += r.sum()
        best += (a == 2).sum()
    return total / (runs * steps), best / (runs * steps)

for eps in [0.0, 0.01, 0.1, 0.3]:
    avg, opt = play(eps)
    print("epsilon", str(eps).ljust(4), " average reward", round(avg, 3), " best arm chosen", str(round(100 * opt, 1)) + "%")
print("always picking the best arm would average", true_means.max())
''', long=True)

K.code('ucb', r'''
import numpy as np

true_means = np.array([0.2, 0.5, 0.8, 0.3, 0.6])
runs, steps = 500, 2000
rng = np.random.default_rng(1)
rows = np.arange(runs)

def play(rule, c=0.0, eps=0.0):
    Q, N, regret = np.zeros((runs, 5)), np.zeros((runs, 5)), 0.0
    for t in range(1, steps + 1):
        if rule == "ucb":
            bonus = np.where(N > 0, c * np.sqrt(np.log(t) / np.maximum(N, 1)), np.inf)   # untried arms first
            a = (Q + bonus).argmax(axis=1)
        else:
            a = np.where(rng.random(runs) < eps, rng.integers(0, 5, runs), Q.argmax(axis=1))
        r = rng.normal(true_means[a], 1.0)
        N[rows, a] += 1
        Q[rows, a] += (r - Q[rows, a]) / N[rows, a]
        regret += (true_means.max() - true_means[a]).sum()  # reward lost against always playing the best arm
    return regret / runs

print("average total regret over", steps, "pulls (lower is better)")
print("epsilon greedy, 0.1:", round(play("eps", eps=0.1), 1))
for c in [0.5, 1.0, 2.0]:
    print("UCB, c =", str(c).ljust(3), "      ", round(play("ucb", c=c), 1))
''', long=True)

K.code('thompson', r'''
import numpy as np

click_rates = np.array([0.04, 0.05, 0.07])                # three web page designs, true click rates unknown
visitors, repeats = 5000, 200                            # 200 separate experiments, run side by side
rng = np.random.default_rng(2)
rows = np.arange(repeats)

def ab_test(test_share=0.5):
    shown, clicks = np.zeros((repeats, 3)), np.zeros((repeats, 3))
    for v in range(visitors):
        if v < visitors * test_share:
            a = np.full(repeats, v % 3)                  # split traffic evenly during the test
        else:
            a = (clicks / np.maximum(shown, 1)).argmax(axis=1)   # then show the winner to everyone
        shown[rows, a] += 1
        clicks[rows, a] += rng.random(repeats) < click_rates[a]
    return clicks.sum(axis=1), shown

def thompson():
    wins, losses = np.ones((repeats, 3)), np.ones((repeats, 3))   # Beta(1, 1) prior for each design
    for v in range(visitors):
        a = rng.beta(wins, losses).argmax(axis=1)        # sample a plausible rate for each design, show the best
        click = rng.random(repeats) < click_rates[a]
        wins[rows, a] += click
        losses[rows, a] += 1 - click
    return wins.sum(axis=1) - 3, wins + losses - 2

for name, f in [("A/B test, then winner", ab_test), ("Thompson sampling", thompson)]:
    clicks, shown = f()
    print(name.ljust(22), " average clicks", round(clicks.mean(), 1), " visitors per design", shown.mean(axis=0).round(0))
print("best possible on average:", round(visitors * click_rates.max()))
''', long=True)

K.lesson('idea', 'The bandit problem and running averages', f'''
{src('Sutton and Barto (2018) sections 2.1 to 2.5.')}
{wwh('A <b>multi armed bandit</b> is the simplest RL problem: there is only one state. You face k slot machines (arms), each paying rewards from its own unknown distribution. Each round you pull one arm and see its reward. The goal is the largest total reward, which means finding the best arm while losing as little as possible on the way.',
     'It isolates the explore or exploit trade off with nothing else in the way. Real uses are everywhere: which ad or headline to show, which price to test, which treatment to give in an adaptive clinical trial, which server answers fastest.',
     'Keep an estimate Q(a) of each arm’s mean reward and the count N(a) of pulls. After each pull update the estimate with the running average Q &larr; Q + (r &minus; Q) / N, which needs no list of old rewards. Then choose the next arm with a rule that balances using high estimates and testing uncertain ones.')}
{run('incremental_mean')}
{note('The running average gives 4, 5, 5, 6, 5, exactly the plain average at each point, without storing the rewards. With a constant step size of 0.5 the estimate forgets the past: after three rewards of 1 and then rewards of 10 it climbs to 8.859 within three pulls. A constant step size suits arms whose payouts drift over time.', 'exam')}
{fxs(fx('Running average', 'Q<sub>n+1</sub> = Q<sub>n</sub> + (r<sub>n</sub> &minus; Q<sub>n</sub>) / n', 'New estimate = old + step &times; (target &minus; old).', key=True),
     fx('Constant step size', 'Q<sub>n+1</sub> = Q<sub>n</sub> + &alpha;(r<sub>n</sub> &minus; Q<sub>n</sub>)', 'Weights reward k pulls ago by &alpha;(1 &minus; &alpha;)<sup>k</sup>.'),
     fx('Regret', 'regret(T) = T &mu;* &minus; &Sigma;<sub>t</sub> &mu;<sub>a<sub>t</sub></sub>', 'Reward lost against always pulling the best arm.', key=True))}
''', kw=['multi armed bandit', 'arm', 'action value', 'running average', 'incremental update', 'constant step size', 'regret'])

K.lesson('egreedy', 'Greedy and epsilon greedy', f'''
{src('Sutton and Barto (2018) section 2.3, the 10 armed testbed.')}
{viz('mlbandit')}
{wwh('<b>Greedy</b> always pulls the arm with the highest estimate. <b>&epsilon; greedy</b> does the same most of the time but, with a small chance &epsilon;, pulls an arm at random.',
     'Greedy can lock onto a worse arm forever after one lucky early reward, because it never tests the others again. A little random exploration keeps every estimate improving, so the best arm is found eventually.',
     'Pick &epsilon; between 0.01 and 0.1 for a start. Lower &epsilon; wastes less once the best arm is known but finds it more slowly. A common improvement is to lower &epsilon; over time, or to start all estimates optimistically high so that every arm gets tried early.')}
{run('epsilon_greedy')}
{note('Averaged over 500 experiments of 1,000 pulls, greedy chooses the best arm only 25% of the time and earns 0.497 per pull. &epsilon; = 0.1 earns the most, 0.705, picking the best arm 68% of the time. &epsilon; = 0.3 explores too much: it knows the best arm but still pulls a random one 30% of the time.', 'exam')}
{table(['Rule', 'Explores by', 'Weakness'], [
    ['Greedy', 'Never', 'Stuck on an early lucky arm'],
    ['&epsilon; greedy', 'Random arm with chance &epsilon;', 'Explores bad arms as often as promising ones, forever'],
    ['Optimistic start', 'High first estimates force early tries', 'Only helps at the start'],
    ['UCB', 'Bonus for rarely pulled arms', 'Needs a bonus size c'],
    ['Thompson sampling', 'Random draws from beliefs', 'Needs a model of the rewards']])}
''', kw=['greedy', 'epsilon greedy', 'exploration rate', 'optimistic initial values', '10 armed testbed'])

K.lesson('ucb', 'Upper confidence bounds: optimism under uncertainty', f'''
{src('Auer, Cesa-Bianchi and Fischer, Finite-time Analysis of the Multiarmed Bandit Problem (2002), and Lai and Robbins (1985).')}
{wwh('<b>UCB</b> scores each arm by its estimate plus a bonus for uncertainty: Q(a) + c &radic;(ln t / N(a)). It pulls the arm with the highest score. An arm that has been pulled rarely has a big bonus, so it gets tried. As N(a) grows the bonus shrinks and the score settles on the true mean.',
     'Unlike &epsilon; greedy, UCB explores where it matters: it stops testing arms that are clearly bad and keeps testing arms that might still be best. Its regret grows only like log T, which Lai and Robbins proved is the best possible order.',
     'Pull every arm once, then always pull the arm with the highest Q + bonus. Tune c: about &radic;2 is the classic choice for rewards between 0 and 1, and noisy rewards may need another value. Too large a c explores too much, too small acts greedy.')}
{run('ucb')}
{note('Over 2,000 pulls, UCB with c = 1 loses 67.3 in regret, about half of &epsilon; greedy’s 141.2. But c = 2 does worse than &epsilon; greedy (167.7) because its bonus keeps forcing pulls of bad arms, and c = 0.5 lands in between (96.2). UCB is better in principle, yet its bonus size still has to fit the noise in the rewards.', 'exam')}
{fxs(fx('UCB score', 'A<sub>t</sub> = argmax<sub>a</sub> [Q(a) + c &radic;(ln t / N(a))]', 'Optimism in the face of uncertainty.', key=True),
     fx('UCB1', 'Q(a) + &radic;(2 ln t / N(a))', 'Auer and colleagues, rewards in [0, 1].'),
     fx('Hoeffding bound', 'P(&mu; &gt; Q + u) &le; e<sup>&minus;2 N u<sup>2</sup></sup>', 'Where the bonus comes from.'))}
''', kw=['UCB', 'upper confidence bound', 'UCB1', 'optimism in the face of uncertainty', 'logarithmic regret', 'Hoeffding inequality'])

K.lesson('thompson', 'Thompson sampling and A/B tests', f'''
{src('Thompson (1933), Chapelle and Li, An Empirical Evaluation of Thompson Sampling (NeurIPS 2011), and Russo and colleagues, A Tutorial on Thompson Sampling (2018).')}
{viz('mlthompson')}
{wwh('<b>Thompson sampling</b> keeps a probability distribution of belief about each arm’s mean. For click or no click rewards this is a <b>Beta</b>(wins + 1, losses + 1) curve. Each round it draws one random value from every arm’s curve and pulls the arm with the highest draw. The chance an arm is pulled equals the chance it is the best, given the data so far.',
     'It is simple, needs no bonus size, and in practice often matches or beats UCB. Companies use it to choose between web page designs, ads and recommendations, because it moves traffic to the winner while the test is still running, instead of wasting half the visitors on losers as a fixed A/B test does.',
     'Start every arm at Beta(1, 1), the flat curve. After a click add 1 to wins, after no click add 1 to losses. Each round draw, pick the largest, show, update. For rewards that are not 0 or 1, use other prior and posterior pairs such as normal curves.')}
{run('thompson')}
{note('Over 5,000 visitors and 200 repeats, Thompson sampling earned 323 clicks against 305.3 for an A/B test that split the first half of visitors evenly and then showed the winner. Thompson showed the worst design only 354 times on average, against 844 in the A/B test. The best possible was 350. The A/B test gives a cleaner statistical answer, Thompson gives more clicks while learning.', 'exam')}
{table(['', 'Fixed A/B test', 'Bandit (Thompson or UCB)'], [
    ['Traffic split', 'Fixed, often even', 'Shifts towards the winner as data arrives'],
    ['Lost reward while testing', 'High', 'Low'],
    ['Clean significance test', 'Yes', 'Harder, the samples are not balanced'],
    ['Best for', 'Learning which is better, with a clear answer', 'Earning while learning, many options, short campaigns']])}
''', kw=['Thompson sampling', 'Beta distribution', 'posterior sampling', 'Bayesian bandit', 'A/B testing', 'adaptive experiments'])

K.lesson('contextual', 'Contextual bandits and where bandits fit', f'''
{src('Li, Chu, Langford and Schapire, A Contextual-Bandit Approach to Personalized News Article Recommendation (WWW 2010).')}
{wwh('A <b>contextual bandit</b> sees some features (the context) before each choice, such as the user’s device, time and history, and learns which arm is best for each context. <b>LinUCB</b> models each arm’s expected reward as a linear function of the context and adds a UCB style bonus for uncertainty.',
     'The best headline for a phone user at night may differ from the best one for a desktop user at noon. Contextual bandits personalise, yet stay simpler than full RL because one choice does not change the next context.',
     'Plain bandit: one state, no context. Contextual bandit: a context each round, but actions do not affect the future. Full RL: actions change the next state. Choose the simplest one that fits the problem.')}
{steps('LinUCB in four lines', [
    'For each arm a keep A<sub>a</sub> = I (a d by d matrix) and b<sub>a</sub> = 0 (a vector), where d is the number of context features.',
    'For context x, estimate &theta;<sub>a</sub> = A<sub>a</sub><sup>&minus;1</sup> b<sub>a</sub> and score p<sub>a</sub> = &theta;<sub>a</sub> &middot; x + &alpha; &radic;(x<sup>T</sup> A<sub>a</sub><sup>&minus;1</sup> x).',
    'Pull the arm with the highest score and observe reward r.',
    'Update that arm: A<sub>a</sub> &larr; A<sub>a</sub> + x x<sup>T</sup> and b<sub>a</sub> &larr; b<sub>a</sub> + r x.'])}
{table(['Problem', 'States', 'Context', 'Actions change the future'], [
    ['Multi armed bandit', 'One', 'No', 'No'],
    ['Contextual bandit', 'One per round', 'Yes', 'No'],
    ['Full reinforcement learning', 'Many', 'Yes (the state)', 'Yes']])}
''', kw=['contextual bandit', 'LinUCB', 'personalisation', 'bandit vs reinforcement learning'])

K.lesson('versus', 'Bandit strategies compared', f'''
{versus('Four ways to choose an arm', ['', 'Greedy', '&epsilon; greedy', 'UCB', 'Thompson sampling'], [
    ['Explores', 'No', 'At random, a fixed share', 'Where uncertainty is high', 'In proportion to the chance of being best'],
    ['Settings', 'None', '&epsilon;', 'c', 'A prior'],
    ['Regret over time', 'Can grow linearly', 'Grows linearly with fixed &epsilon;', 'Logarithmic', 'Logarithmic'],
    ['Randomness', 'None', 'Yes', 'None, deterministic', 'Yes'],
    ['Typical use', 'Never alone', 'A quick baseline', 'Theory and simple systems', 'Web experiments, ads']],
    'use Thompson sampling or UCB for real problems and &epsilon; greedy as a baseline. Never rely on pure greedy.')}
''', kw=['epsilon greedy vs UCB', 'UCB vs Thompson sampling', 'bandit comparison'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Action value', 'q*(a) = E[R<sub>t</sub> | A<sub>t</sub> = a]', 'The true mean of arm a.', key=True),
     fx('Sample average', 'Q<sub>t</sub>(a) = (sum of rewards from a) / N<sub>t</sub>(a)', 'Converges to q*(a) by the law of large numbers.'),
     fx('Incremental form', 'Q &larr; Q + (1/N)(r &minus; Q)', 'Any step size &alpha;<sub>n</sub> with &Sigma; &alpha;<sub>n</sub> = &infin; and &Sigma; &alpha;<sub>n</sub><sup>2</sup> &lt; &infin; converges.', key=True),
     fx('&epsilon; greedy choice', 'P(greedy arm) = 1 &minus; &epsilon; + &epsilon;/k', 'The random pick can also land on it.'),
     fx('UCB', 'argmax<sub>a</sub> Q(a) + c &radic;(ln t / N(a))', 'Regret O(log T).', key=True),
     fx('Beta posterior', 'Beta(1, 1) + s clicks and f misses &rArr; Beta(1 + s, 1 + f), mean (1 + s)/(2 + s + f)', 'Conjugate to the Bernoulli.', key=True),
     fx('Lai and Robbins bound', 'regret(T) &ge; (&Sigma;<sub>a: &Delta;<sub>a</sub>&gt;0</sub> &Delta;<sub>a</sub> / KL(a, a*)) ln T, as T grows', 'No rule can beat log T.'))}
{steps('Worked example: one UCB decision', [
    'Round t = 100. Arm A: Q = 0.6 after 25 pulls. Arm B: Q = 0.5 after 4 pulls. c = 1.',
    'ln 100 = 4.605.',
    eq('Arm A: 0.6 + &radic;(4.605 / 25) = 0.6 + 0.429 = 1.029'),
    eq('Arm B: 0.5 + &radic;(4.605 / 4) = 0.5 + 1.073 = 1.573'),
    'UCB pulls arm B: its estimate is lower but much less certain.'])}
{deep('Why UCB’s regret is logarithmic', '<p>Hoeffding’s inequality says that after N pulls the sample mean is more than u below the true mean with chance at most e<sup>&minus;2Nu<sup>2</sup></sup>. Choosing u = &radic;(2 ln t / N) makes that chance at most t<sup>&minus;4</sup>, so with high probability every arm’s score is above its true mean. A worse arm with gap &Delta; is then pulled only while its bonus exceeds &Delta;, that is while N &lt; 8 ln t / &Delta;<sup>2</sup>. Summing over arms gives regret at most about &Sigma; 8 ln T / &Delta;<sub>a</sub> plus a constant, which matches the Lai and Robbins lower bound up to constants. Thompson sampling has the same order of regret (Agrawal and Goyal, 2012).</p>')}
''', kw=['action value', 'sample average', 'step size conditions', 'UCB regret', 'Beta posterior', 'Lai Robbins bound'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A bandit means choosing again and again between options with unknown payouts, trying some and using the best one found.</p>',
    '<p>Keep running averages, implement greedy, &epsilon; greedy, UCB and Thompson sampling, and measure average reward and regret.</p>',
    '<p>Tune &epsilon; and c, explain why UCB and Thompson sampling have logarithmic regret, handle drifting arms with constant step sizes, and compare bandits with A/B tests.</p>',
    '<p>Study contextual bandits such as LinUCB, regret lower bounds, adversarial bandits (EXP3), best arm identification, and off policy evaluation from logged bandit data.</p>')}
{grow('Explain the explore or exploit trade off.',
      'Build and compare bandit algorithms.',
      'Analyse regret and design adaptive experiments.')}
''', kw=['beginner', 'expert', 'EXP3', 'best arm identification', 'off policy evaluation'])

lc(1431, 'Kids With the Greatest Number of Candies', 'kids-with-the-greatest-number-of-candies', 'e', 'Compare each value plus the extra with the current maximum', 'Find the maximum once, then check each kid against it. A greedy bandit makes this comparison every round: which estimate is the highest right now.', r"""
def kids_with_candies(candies, extra_candies):
    best = max(candies)
    return [c + extra_candies >= best for c in candies]
""", [('kids_with_candies([2, 3, 5, 1, 3], 3)', [True, True, True, False, True]), ('kids_with_candies([12, 1, 12], 10)', [True, False, True])])
lc(1672, 'Richest Customer Wealth', 'richest-customer-wealth', 'e', 'The largest row sum', 'Add up each customer’s accounts and take the maximum. Total payout per arm, then the best arm, is the same calculation.', r"""
def maximum_wealth(accounts):
    return max(sum(a) for a in accounts)
""", [('maximum_wealth([[1, 2, 3], [3, 2, 1]])', 6), ('maximum_wealth([[1, 5], [7, 3], [3, 5]])', 10)])
lc(398, 'Random Pick Index', 'random-pick-index', 'm', 'Reservoir sampling: keep the i-th match with chance 1/i', 'Walk the list. At the i-th time you meet the target, replace your choice with chance 1/i. Every matching index ends up equally likely, and no extra memory is needed. Our helper picks many times and returns the set of indices seen, so the answer can be checked.', r"""
import random


class RandomPickIndex:
    def __init__(self, nums):
        self.nums = nums

    def pick(self, target):
        chosen, seen = -1, 0
        for i, v in enumerate(self.nums):
            if v == target:
                seen += 1
                if random.randrange(seen) == 0:
                    chosen = i
        return chosen


def pick_many(nums, target, times):
    picker = RandomPickIndex(nums)
    return sorted(set(picker.pick(target) for _ in range(times)))
""", [('pick_many([1, 2, 3, 3, 3], 3, 300)', [2, 3, 4]), ('pick_many([1, 2, 3, 3, 3], 1, 50)', [0])])
lc(470, 'Implement Rand10() Using Rand7()', 'implement-rand10-using-rand7', 'm', 'Build a uniform number from 1 to 49, reject anything above 40', 'Two calls of rand7 give 49 equally likely outcomes. Keep only the first 40 and map them to 1 to 10. Rejection sampling like this is how random draws from one distribution are turned into another, as Thompson sampling needs. Our check confirms all ten values appear about equally often.', r"""
import random


def rand7():
    return random.randint(1, 7)


def rand10():
    while True:
        v = (rand7() - 1) * 7 + rand7()
        if v <= 40:
            return (v - 1) % 10 + 1


def rand10_counts(times):
    counts = [0] * 10
    for _ in range(times):
        counts[rand10() - 1] += 1
    return all(abs(c - times / 10) < times / 20 for c in counts)
""", [('rand10_counts(20000)', True)])
lc(710, 'Random Pick with Blacklist', 'random-pick-with-blacklist', 'h', 'Draw from the first n minus b numbers and remap blacklisted ones', 'Let size be the count of allowed numbers. Draw uniformly from 0 to size minus 1. Any blacklisted number in that range is mapped once, at the start, to an allowed number above the range. Each pick is then one random draw and one dictionary lookup. Our helper returns the set of values picked.', r"""
import random


class BlacklistPicker:
    def __init__(self, n, blacklist):
        self.size = n - len(blacklist)
        black = set(blacklist)
        spare = (x for x in range(self.size, n) if x not in black)
        self.remap = {b: next(spare) for b in blacklist if b < self.size}

    def pick(self):
        x = random.randrange(self.size)
        return self.remap.get(x, x)


def blacklist_picks(n, blacklist, times):
    p = BlacklistPicker(n, blacklist)
    return sorted(set(p.pick() for _ in range(times)))
""", [('blacklist_picks(7, [2, 3, 5], 300)', [0, 1, 4, 6]), ('blacklist_picks(3, [0], 100)', [1, 2])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Bandits compare estimates and make random choices. These problems practise finding the current best option, totals per option, reservoir sampling, rejection sampling, and uniform draws from an allowed set. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'argmax', 'reservoir sampling', 'rejection sampling', 'randomised algorithms'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>bandit</b> has one state and k arms with unknown means. Maximise total reward, or equally minimise <b>regret</b>.',
    'Estimate each arm with a running average Q &larr; Q + (r &minus; Q)/N, or a constant step size for drifting arms.',
    '<b>Greedy</b> can get stuck. <b>&epsilon; greedy</b> explores at random with chance &epsilon;.',
    '<b>UCB</b> adds a bonus c &radic;(ln t / N) to rarely pulled arms and has logarithmic regret.',
    '<b>Thompson sampling</b> draws from Beta beliefs and pulls the best draw. It beats fixed A/B tests on reward during the test.',
    '<b>Contextual bandits</b> such as LinUCB choose per context. Full RL adds states that actions change.'],
    'Reinforcement 1.3 covers Markov decision processes: states, transitions, value functions and the Bellman equations.')}
{files('Three tasks: running estimates, a UCB choice, and the long run reward of &epsilon; greedy.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'A multi armed bandit has', ['Many states', 'One state and several actions with unknown rewards', 'No rewards', 'A known best arm'], 1, 'Slot machines.', 'The simplest RL setting.')
K.quiz('e', 'Greedy action selection always', ['Picks at random', 'Picks the arm with the highest current estimate', 'Picks the least pulled arm', 'Stops'], 1, 'Exploit only.', 'It never explores.')
K.quiz('e', 'With &epsilon; = 0.1, how often does &epsilon; greedy pick a random arm?', ['Never', '10% of the time', '90% of the time', 'Always'], 1, 'Chance &epsilon;.', 'The rest of the time it is greedy.')
K.quiz('e', 'Regret measures', ['Total reward', 'Reward lost compared with always pulling the best arm', 'The number of arms', 'Running time'], 1, 'Lost reward.', 'Lower is better.')
K.quiz('m', 'Why can pure greedy fail?', ['It is slow', 'An early lucky reward can make it stick to a worse arm forever', 'It explores too much', 'It needs labels'], 1, 'No testing of others.', 'Estimates of unpulled arms never improve.')
K.quiz('m', 'The UCB bonus for an arm', ['Grows with its pulls', 'Shrinks as the arm is pulled more', 'Is constant', 'Is random'], 1, '&radic;(ln t / N).', 'Uncertainty falls with data.')
K.quiz('m', 'After 3 clicks and 7 misses, starting from Beta(1, 1), the belief is', ['Beta(3, 7)', 'Beta(4, 8)', 'Beta(7, 3)', 'Beta(10, 10)'], 1, 'Add 1 to each.', 'Wins + 1, losses + 1.')
K.quiz('m', 'A constant step size &alpha; is useful when', ['Arms never change', 'Arm payouts drift over time', 'There is one arm', 'Rewards are zero'], 1, 'Forgetting.', 'Recent rewards weigh more.')
K.quiz('m', 'Compared with a fixed A/B test, Thompson sampling usually', ['Loses more reward', 'Earns more during the test by shifting traffic to the leader', 'Needs no data', 'Gives cleaner p values'], 1, 'Earn while learning.', 'At some cost to clean statistics.')
K.quiz('h', 'UCB with a very large c behaves', ['Greedily', 'Like heavy exploration, pulling bad arms too often', 'Like Thompson sampling', 'Randomly'], 1, 'Bonus dominates.', 'As the program showed with c = 2.')
K.quiz('h', 'The best possible growth of regret over T pulls is of order', ['T', '&radic;T', 'log T', 'Constant'], 2, 'Lai and Robbins (1985).', 'UCB and Thompson sampling achieve it.')
K.quiz('h', 'A contextual bandit differs from full RL because', ['It has no rewards', 'Its actions do not change future contexts', 'It has no actions', 'It needs a model'], 1, 'No state transitions caused by actions.', 'Each round is independent of the last choice.')
K.quiz('x', 'In the style of a Stanford CS234 exam: &epsilon; greedy with a fixed &epsilon; &gt; 0 has regret that grows', ['Logarithmically', 'Linearly in T', 'Not at all', 'Exponentially'], 1, 'It keeps exploring forever.', 'About &epsilon; times the average gap per pull.')
K.quiz('x', 'In the style of a Stanford CS234 exam: in Thompson sampling the probability of pulling an arm equals', ['1/k', 'The posterior probability that it is the best arm', 'Its estimate', 'Its count'], 1, 'Probability matching.', 'That is the defining property.')

K.calc('e', 'Q = 5 after 4 pulls. The next reward is 10. New Q?', '6', 'Q + (r &minus; Q)/N.', ['N becomes 5.', 'r &minus; Q = 5.', eq('5 + 5 / 5 = 6')], check=6)
K.calc('e', '&epsilon; = 0.1 and 5 arms. Chance the greedy arm is chosen?', '0.92', '1 &minus; &epsilon; + &epsilon;/k.', ['Greedy pick: 0.9.', 'Random pick lands on it: 0.1 / 5 = 0.02.', eq('0.9 + 0.02 = 0.92')], check=0.92)
K.calc('m', 'Constant step &alpha; = 0.5, Q = 0.875, reward 10. New Q?', '5.438', 'Q + &alpha;(r &minus; Q).', ['r &minus; Q = 9.125.', '&alpha; &times; 9.125 = 4.5625.', eq('0.875 + 4.5625 = 5.4375')], check=5.4375, tol=0.001)
K.calc('m', 'UCB with c = 1 at t = 100: Q = 0.6 after 25 pulls. Score?', '1.029', 'Q + c&radic;(ln t / N).', ['ln 100 = 4.605.', '&radic;(4.605 / 25) = 0.429.', eq('0.6 + 0.429 = 1.029')], check=1.029, tol=0.002)
K.calc('m', 'Best arm mean 0.7. You pulled an arm with mean 0.3 ten times and the best arm 90 times. Regret?', '4', 'Gap times pulls.', ['Gap = 0.4.', 'Only the 10 bad pulls cost anything.', eq('10 &times; 0.4 = 4')], check=4)
K.calc('m', 'Beta(1, 1) prior, then 3 clicks and 7 misses. Posterior mean?', '0.333', 'a / (a + b).', ['Posterior Beta(4, 8).', 'a + b = 12.', eq('4 / 12 = 0.333')], check=0.3333, tol=0.001)
K.calc('h', 'UCB1 bonus &radic;(2 ln t / N) at t = 1,000 for an arm pulled 10 times?', '1.175', 'ln 1,000 = 6.908.', ['2 ln t = 13.816.', 'Divide by 10: 1.3816.', eq('&radic;1.3816 = 1.175')], check=1.1754, tol=0.002)
K.calc('h', 'Arms with means 0.2, 0.5, 0.8, 0.3, 0.6. &epsilon; greedy with &epsilon; = 0.1 already knows the best arm. Regret over 1,000 pulls?', '32', 'Random pulls lose the average gap.', ['Average of all arms: 2.4 / 5 = 0.48, so a random pull loses 0.8 &minus; 0.48 = 0.32.', 'Random pulls: 0.1 &times; 1,000 = 100.', eq('100 &times; 0.32 = 32')], check=32)
K.calc('h', 'An A/B test splits 2,500 visitors evenly over designs with click rates 0.04, 0.05 and 0.07. Expected clicks lost against showing the best design to all?', '41.67', 'Visitors per design times gap.', ['833.3 visitors each.', 'Gaps: 0.03 and 0.02, total 0.05.', eq('833.3 &times; 0.05 = 41.67')], check=41.67, tol=0.05)
K.calc('x', 'In the style of a Stanford CS234 problem: at t = 1,000, how many pulls N make the UCB1 bonus &radic;(2 ln t / N) smaller than 0.1?', '1382', 'N &gt; 2 ln t / 0.01.', ['2 ln 1,000 = 13.816.', 'Divide by 0.1<sup>2</sup> = 0.01: 1,381.6.', eq('N = 1,382')], check=1382)

K.assign('running_estimates', 'e', 'Running estimates',
         '<p>Write <code>running_estimates(rewards)</code> that returns the running average after each reward, using Q &larr; Q + (r &minus; Q)/n, each rounded to 3 decimals.</p>',
         """
def running_estimates(rewards):
    # your code here
    pass
""", [('running_estimates([4, 6, 5, 9, 1])', [4.0, 5.0, 5.0, 6.0, 5.0]), ('running_estimates([1, 0, 0])', [1.0, 0.5, 0.333])],
         """
def running_estimates(rewards):
    Q, out = 0.0, []
    for n, r in enumerate(rewards, start=1):
        Q = Q + (r - Q) / n
        out.append(round(Q, 3))
    return out
""", 'Keep one number Q and the count n.', '<p>The update never stores old rewards, which matters when a bandit runs for millions of rounds.</p>')
K.assign('ucb_choose', 'm', 'A UCB choice',
         '<p>Write <code>ucb_choose(Q, N, t, c)</code>. Q and N are lists of estimates and pull counts. If any arm has N = 0 return the first such index. Otherwise return the index with the highest Q + c &radic;(ln t / N), the first one on a tie.</p>',
         """
import math


def ucb_choose(Q, N, t, c):
    # your code here
    pass
""", [('ucb_choose([0.6, 0.5], [25, 4], 100, 1.0)', 1), ('ucb_choose([0.6, 0.5], [25, 4], 100, 0.1)', 0), ('ucb_choose([0.9, 0.1, 0.5], [3, 0, 2], 6, 1.0)', 1)],
         """
import math


def ucb_choose(Q, N, t, c):
    for i, n in enumerate(N):
        if n == 0:
            return i
    scores = [q + c * math.sqrt(math.log(t) / n) for q, n in zip(Q, N)]
    return scores.index(max(scores))
""", 'Handle untried arms first, then compute every score.', '<p>The first test is the worked example: the less certain arm wins with c = 1. With a small c = 0.1 the bonus barely matters and the higher estimate wins.</p>')
K.assign('eps_greedy_value', 'm', 'Long run reward of epsilon greedy',
         '<p>Write <code>eps_greedy_value(means, eps)</code>: the expected reward per pull of &epsilon; greedy once it knows which arm is best. With chance 1 &minus; &epsilon; it pulls the best arm, and with chance &epsilon; a uniformly random arm. Round to 4 decimals.</p>',
         """
def eps_greedy_value(means, eps):
    # your code here
    pass
""", [('eps_greedy_value([0.2, 0.5, 0.8, 0.3, 0.6], 0.1)', 0.768), ('eps_greedy_value([1, 0], 0.5)', 0.75), ('eps_greedy_value([0.4, 0.4], 0.3)', 0.4)],
         """
def eps_greedy_value(means, eps):
    best = max(means)
    avg = sum(means) / len(means)
    return round((1 - eps) * best + eps * avg, 4)
""", 'Mix the best mean and the average mean with weights 1 &minus; &epsilon; and &epsilon;.', '<p>The first test gives 0.768, so even a perfect &epsilon; greedy loses 0.032 per pull against the best arm’s 0.8. That is why &epsilon; is often lowered over time.</p>')

K.must('Problem', 'One state, k arms, unknown means. Maximise total reward or minimise regret T&mu;* &minus; &Sigma; &mu;<sub>a<sub>t</sub></sub>.')
K.must('Update', 'Q &larr; Q + (r &minus; Q)/N. Constant &alpha; for drifting arms.')
K.must('&epsilon; greedy', 'Random arm with chance &epsilon;, else greedy. Simple, but linear regret with fixed &epsilon;.')
K.must('UCB', 'argmax Q + c&radic;(ln t / N). Untried arms first. Logarithmic regret. Tune c.')
K.must('Thompson', 'Beta(1 + wins, 1 + losses). Draw from each, pull the best draw. Probability matching.')
K.must('Context', 'Contextual bandits (LinUCB) choose per context. Bandits beat fixed A/B tests on reward, A/B tests give cleaner answers.')

T = K.topic(
    slug='ml-bandits', topic='ml-bandits', step=(1, 'RL basics', 'ml-r1', 'Learn how an agent learns from rewards: returns and discounting, bandits that balance trying and using, and the Markov decision process behind every RL problem.', 'Intermediate'),
    title='Multi armed bandits', short='Bandits', badge='1.2', minutes=45,
    lead='Balance trying and using with multi armed bandits: running averages and regret, greedy and epsilon greedy, upper confidence bounds, Thompson sampling against A/B tests, and contextual bandits.',
    desc='multi armed bandit, action value, running average, regret, greedy, epsilon greedy, optimistic initial values, UCB, UCB1, Hoeffding, Thompson sampling, Beta distribution, A/B testing, contextual bandit, LinUCB, Lai Robbins bound.',
    summary='Running averages and regret, epsilon greedy, UCB, Thompson sampling against A/B tests, and contextual bandits.',
    keywords=['multi armed bandit', 'epsilon greedy', 'UCB', 'Thompson sampling', 'regret', 'A/B testing', 'contextual bandit', 'LinUCB', 'exploration', 'Beta distribution'],
    recap='<p>Bandits isolate the explore or exploit choice. Keep running averages, prefer UCB or Thompson sampling to plain epsilon greedy, and use contextual bandits when each choice comes with features.</p>',
    added='2026-11-13', leet=leet_items())
