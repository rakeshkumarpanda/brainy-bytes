# Chapter 2.3: attitudes to risk and the St Petersburg paradox. Source: lecture 3 (risk neutral, risk averse and risk
# loving through E[u(X)] against u(E[X]), concave and convex utility, the fair gamble, the certainty equivalent, the
# St Petersburg game with payoff 2^(n-1), log utility giving ln 2 and CE 2, u = x^2 diverging, practice problems 4
# and 5) and lecture 2 (practice problem 6).
from cvkit import Kit, fx, fxs, frac, sqrt, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('attitude', r'''
# Compare E[u(X)] with u(E[X]) and find the certainty equivalent for three utility functions
import math
lottery = [(0, 0.5), (100, 0.5)]
utils = {"linear x": (lambda x: x, lambda y: y),
         "sqrt x":   (math.sqrt, lambda y: y * y),
         "x squared": (lambda x: x * x, math.sqrt)}
mean = sum(p * x for x, p in lottery)
for name, (u, inv) in utils.items():
    eu = sum(p * u(x) for x, p in lottery)
    ce = inv(eu)                          # u(CE) = E[u(X)]
    kind = "neutral" if abs(ce - mean) < 1e-9 else ("averse" if ce < mean else "loving")
    print(f"{name:9}  E[u] = {eu:8.2f}  u(E[X]) = {u(mean):8.2f}  CE = {ce:6.2f}  risk {kind}")
''')

K.code('stpete', r'''
# St Petersburg: first tail on toss n pays 2**(n-1) with probability 1/2**n
import math
for N in (10, 20, 40):
    money = sum(2 ** (n - 1) / 2 ** n for n in range(1, N + 1))
    logu = sum(math.log(2 ** (n - 1)) / 2 ** n for n in range(1, N + 1))
    print(f"N = {N:2}: expected money {money:5.1f}   expected log utility {logu:.6f}")
print("ln 2 =", round(math.log(2), 6), " so the certainty equivalent is e**ln2 =", round(math.exp(math.log(2)), 6))
''')

K.lesson('attitudes', 'Three attitudes to risk', f'''
<p>Would you rather have 50 rupees for sure, or a coin toss that pays 100 or nothing? Both have the same expected money, 50. Most people take the sure 50. Expected utility explains this through the shape of u.</p>
{fxs(
    fx('Risk neutral', 'E[ <i>u</i>(<i>X</i>) ] = <i>u</i>( E[<i>X</i>] )', 'u is linear, u(x) = ax + b. Only expected money matters.', key=True),
    fx('Risk averse', 'E[ <i>u</i>(<i>X</i>) ] ≤ <i>u</i>( E[<i>X</i>] )', 'u is concave (u″ &lt; 0), for example ln x or √x. The sure amount is preferred.', key=True),
    fx('Risk loving', 'E[ <i>u</i>(<i>X</i>) ] ≥ <i>u</i>( E[<i>X</i>] )', 'u is convex (u″ &gt; 0), for example x². The gamble is preferred.', key=True))}
<p>The picture behind this is Jensen\'s inequality. Draw u and join the two outcomes with a straight chord. The chord\'s height at the mean is E[u(X)], and the curve\'s height there is u(E[X]). For a concave curve the chord is below, so the gamble is worth less than its mean.</p>
{viz('risk')}
{steps('The fair gamble from lecture 3', [
    'Pay 1 to enter. Win 2 with probability 0.5, or nothing.',
    'Net outcomes: +1 with 0.5 and −1 with 0.5, so expected money is 0.',
    'Not playing gives 0 for sure, also expected money 0.',
    eq('Play when 0.5 u(1) + 0.5 u(−1) &gt; u(0)'),
    'A risk averse agent refuses, a risk neutral one is indifferent, and a risk lover plays.'])}
{steps('Practice problem 5: u = x², 0 or 10 with 0.5 each', [
    'E[X] = 5, so u(E[X]) = 25.',
    'E[u(X)] = 0.5 × 0 + 0.5 × 100 = 50.',
    eq('50 &gt; 25, so this agent is risk loving')])}
''', kw=['risk averse', 'risk neutral', 'risk loving', 'concave', 'convex', 'Jensen', 'fair gamble'])

K.lesson('ce', 'The certainty equivalent', f'''
<p>How much is a gamble worth to you in sure money? That amount is its certainty equivalent. It turns any lottery into one number you can compare with cash.</p>
{fxs(
    fx('Certainty equivalent', '<i>u</i>(CE) = E[ <i>u</i>(<i>X</i>) ] &nbsp; ⟹ &nbsp; CE = <i>u</i><sup>−1</sup>( E[<i>u</i>(<i>X</i>)] )', 'The sure amount you value exactly as much as the lottery.', key=True),
    fx('Risk premium', 'RP = E[<i>X</i>] − CE', 'What you would give up in expectation to remove the risk. Positive for a risk averse agent.'),
    fx('Ordering', 'averse: CE ≤ E[X], &nbsp; neutral: CE = E[X], &nbsp; loving: CE ≥ E[X]', ''))}
{steps('Practice problem 4: √x, 100 with 0.2 against 30 for sure', [
    'EU(A) = 0.2 × √100 + 0.8 × √0 = 0.2 × 10 = 2.',
    'EU(B) = √30 = 5.477. Choose B.',
    'Certainty equivalent of A: √CE = 2, so CE = 4.',
    eq('E[A] = 20 but CE(A) = 4, a risk premium of 16')])}
{code('attitude')}
{table(['Utility', 'u″', 'Attitude', 'CE of 0 or 100 at 50/50'], [
    ['x', '0', 'Neutral', '50'], ['√x', '−¼ x<sup>−3/2</sup> &lt; 0', 'Averse', '25'], ['ln(1 + x)', '−1 ÷ (1 + x)² &lt; 0', 'Averse', '9.05'], ['x²', '2 &gt; 0', 'Loving', '70.71']])}
{scene('insurance', '<p>A home worth 100 lakh has a 1% chance of being destroyed. Expected loss is 1 lakh. A risk averse owner with u = ln(wealth) would pay a premium above 1 lakh to remove the risk, and the insurer, being close to risk neutral across many homes, is happy to sell at that price. The gap between the two is the risk premium, and it is why insurance exists.</p>')}
''', kw=['certainty equivalent', 'risk premium', 'insurance', 'inverse utility', 'practice problem 4'])

K.lesson('stpete', 'The St Petersburg paradox', f'''
<p>A fair coin is tossed until the first tail. If the first tail is on toss n you win 2<sup>n−1</sup>. How much would you pay to play?</p>
{fxs(
    fx('Expected money', 'E[<i>X</i>] = ∑<sub><i>n</i>=1</sub><sup>∞</sup> ' + frac('1', '2<sup><i>n</i></sup>') + ' · 2<sup><i>n</i>−1</sup> = ∑ ' + frac('1', '2') + ' = ∞', 'Every toss adds exactly one half to the sum, forever.', key=True),
    fx('Expected log utility', 'E[ln <i>X</i>] = ∑ ' + frac('(<i>n</i> − 1) ln 2', '2<sup><i>n</i></sup>') + ' = ln 2', 'Since ∑ (n − 1) ÷ 2ⁿ = 1. Finite.', key=True),
    fx('Its certainty equivalent', 'CE = e<sup>ln 2</sup> = 2', 'A log utility agent would pay only about 2.'))}
<p>The paradox is that expected money says pay any amount, yet nobody pays much. Daniel Bernoulli resolved it in 1738 with a concave, logarithmic utility. Extra money matters less the more you already have.</p>
{viz('stpete')}
{steps('Why Σ (n − 1) ÷ 2ⁿ = 1', [
    'Write S = Σ<sub>n≥1</sub> (n − 1) ÷ 2ⁿ = 0/2 + 1/4 + 2/8 + 3/16 + …',
    'Put m = n − 1: S = Σ<sub>m≥0</sub> m ÷ 2<sup>m+1</sup> = ½ Σ m ÷ 2<sup>m</sup>.',
    'The known sum Σ m xᵐ = x ÷ (1 − x)² gives Σ m ÷ 2ᵐ = ½ ÷ ¼ = 2.',
    eq('S = ½ × 2 = 1, so E[ln X] = ln 2')])}
{code('stpete')}
{note('Concavity is what tames the paradox. With the convex u = x² the terms are 2ⁿ⁻² and the sum still diverges. Even √x converges, to about 1.707, which gives a certainty equivalent near 2.91.', 'exam')}
{deep('Bounded utility and the real resolution', '<p>Menger showed in 1934 that for any unbounded utility you can design a super St Petersburg game whose payoffs grow fast enough to make expected utility infinite again. With log utility, pay e<sup>2ⁿ</sup> instead of 2ⁿ. A fully safe theory needs bounded utility. In practice the bank cannot pay more than it owns: with a cap of about 10¹² the expected money is only about 20.</p>')}
{ladder(
    '<p>Most people would take a sure 50 over a coin toss for 100 or nothing. Extra money feels less important the more you have, and that makes people careful with risk.</p>',
    '<p>Concave u means risk averse (E[u] ≤ u(E[X]), CE ≤ E[X]), linear means neutral, convex means loving. CE = u⁻¹(E[u]). St Petersburg has infinite expected money, but log utility gives E = ln 2 and CE = 2.</p>',
    '<p>The Arrow Pratt coefficient −u″(x) ÷ u′(x) measures absolute risk aversion. For a small gamble with variance σ², the risk premium is about ½ σ² times this coefficient. CRRA utilities x<sup>1−γ</sup> ÷ (1 − γ) give constant relative risk aversion γ, with ln x at γ = 1.</p>',
    '<p>Rabin\'s calibration theorem (2000) shows that turning down small fair gambles at all wealth levels implies absurd aversion to large ones under expected utility, which supports reference dependent models. In reinforcement learning, exponential utility gives risk sensitive control and entropic risk measures.</p>')}
''', kw=['St Petersburg paradox', 'Bernoulli', 'log utility', 'infinite expectation', 'bounded utility', 'Menger', 'Arrow Pratt'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'A concave utility function means the agent is', ['Risk loving', 'Risk neutral', 'Risk averse', 'Irrational'], 2,
       'u″ < 0.', 'The chord lies below the curve, so E[u] ≤ u(E[X]).')
K.quiz('e', 'Which utility is risk loving?', ['ln x', '√x', 'x', 'x²'], 3,
       'Convex.', 'x² has u″ = 2 > 0.')
K.quiz('e', 'The certainty equivalent satisfies', ['CE = E[X]', 'u(CE) = E[u(X)]', 'CE = E[u(X)]', 'u(CE) = u(E[X])'], 1,
       'Same utility as the lottery.', 'CE is the sure amount whose utility equals the lottery\'s expected utility.')
K.quiz('e', 'Expected money in the St Petersburg game is', ['2', 'ln 2', '1', 'Infinite'], 3,
       'Each term is ½.', 'Σ ½ over all n diverges.')
K.quiz('m', 'For a risk averse agent', ['CE > E[X]', 'CE = E[X]', 'CE ≤ E[X]', 'CE is negative'], 2,
       'The risk premium is positive.', 'Risk aversion means the gamble is worth less than its mean in sure money.')
K.quiz('m', 'Practice problem 4 (√x, 100 with 0.2 against 30 sure): the agent chooses', ['The lottery', 'The sure 30', 'Indifferent', 'Cannot tell'], 1,
       '2 against 5.48.', 'EU(lottery) = 2 < √30 ≈ 5.477.')
K.quiz('m', 'With u = ln x, the St Petersburg certainty equivalent is', ['ln 2', '2', 'e', 'Infinite'], 1,
       'CE = e^E[ln X].', 'E[ln X] = ln 2, so CE = 2.')
K.quiz('m', 'A risk neutral agent has utility', ['ln x', 'ax + b with a > 0', 'x²', '√x'], 1,
       'Linear.', 'Linear utility gives E[u(X)] = u(E[X]).')
K.quiz('h', 'With u = x² the St Petersburg expected utility', ['Converges to 2', 'Converges to ln 2', 'Diverges', 'Is negative'], 2,
       'Terms 2^(n−2).', 'The terms grow, so the sum is infinite. Concavity, not just any utility, solves the paradox.')
K.quiz('h', 'The risk premium of a lottery is', ['E[u(X)] − u(E[X])', 'E[X] − CE', 'CE − E[X]', 'Var(X)'], 1,
       'Mean minus certainty equivalent.', 'It is the expected money you give up to remove the risk.')
K.quiz('x', 'The Arrow Pratt coefficient of absolute risk aversion for u = 1 − e^(−αx) is', ['α', '1/α', 'αx', 'e^(−αx)'], 0,
       '−u″/u′.', 'u′ = α e^(−αx), u″ = −α² e^(−αx), so −u″/u′ = α, constant in wealth.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Practice problem 5: u = x², outcomes 0 and 10 at 0.5 each. What is u(E[X])?', '25', 'E[X] first.',
       ['E[X] = 0.5 × 0 + 0.5 × 10 = 5.', 'u(5) = 5².', eq('u(E[X]) = 25')], check=25)
K.calc('e', 'Same problem: what is E[u(X)]?', '50', 'Square first, then average.',
       ['u(0) = 0, u(10) = 100.', '0.5 × 0 + 0.5 × 100.', eq('E[u(X)] = 50 &gt; 25, risk loving')], check=50)
K.calc('e', 'Practice problem 4: √x, 100 with 0.2 and 0 otherwise. What is EU?', '2', 'Only the 100 counts.',
       ['√100 = 10, √0 = 0.', '0.2 × 10 + 0.8 × 0.', eq('EU = 2')], check=2)
K.calc('m', 'Same lottery: what is its certainty equivalent?', '4', 'Solve √CE = 2.',
       ['u(CE) = EU = 2.', '√CE = 2.', eq('CE = 4')], check=4)
K.calc('m', 'u = √x, outcomes 0 and 100 at 0.5 each. What is the risk premium?', '25', 'E[X] − CE.',
       ['E[X] = 50.', 'EU = 0.5 × 10 = 5, so CE = 5² = 25.', eq('RP = 50 − 25 = 25')], check=25)
K.calc('m', 'u = x², outcomes 0 and 100 at 0.5 each. What is CE? Two decimals.', '70.71', 'CE = √E[u].',
       ['EU = 0.5 × 10,000 = 5,000.', 'CE = √5,000.', eq('CE = 70.71 &gt; 50, risk loving')], check=5000 ** 0.5, tol=0.005)
K.calc('m', 'St Petersburg: what is the expected money from the first 12 tosses only?', '6', 'Each toss adds ½.',
       ['Term n is (1 ÷ 2ⁿ) × 2<sup>n−1</sup> = ½.', 'Twelve terms.', eq('12 × ½ = 6')], check=6)
K.calc('h', 'St Petersburg with u = ln x: what is E[u] to four decimals?', '0.6931', 'ln 2.',
       ['u(2<sup>n−1</sup>) = (n − 1) ln 2.', 'E[u] = ln 2 × Σ (n − 1) ÷ 2ⁿ = ln 2 × 1.', eq('E[u] = ln 2 = 0.6931')], check=0.6931471805599453, tol=0.00005)
K.calc('h', 'St Petersburg with the bank capped: payoffs stop growing after toss 30 (every n ≥ 30 pays 2²⁹). What is the expected money? Two decimals.', '15.5', 'Terms up to 29 give ½ each. The tail pays 2²⁹ with probability 2⁻²⁹.',
       ['Tosses 1 to 29: 29 × ½ = 14.5.', 'P(first tail at 30 or later) = 2<sup>−29</sup>, and the prize is capped at 2²⁹.', 'Tail contribution: 2<sup>−29</sup> × 2<sup>29</sup> = 1.', eq('E[X] = 14.5 + 1 = 15.5')], check=15.5)
K.calc('h', 'Fair gamble from lecture 3 with u(x) = 1 − e^(−x): is it accepted? Give 0.5u(1) + 0.5u(−1) − u(0) to four decimals.', '-0.5431', 'Compute each utility.',
       ['u(1) = 1 − e<sup>−1</sup> = 0.6321.', 'u(−1) = 1 − e = −1.7183.', 'u(0) = 0.', eq('0.5 × 0.6321 + 0.5 × (−1.7183) = −0.5431 &lt; 0, refuse')], check=0.5 * (1 - 2.718281828459045 ** -1) + 0.5 * (1 - 2.718281828459045), tol=0.00005)
K.calc('x', 'Wealth 100, u = ln w, a 50/50 gamble of +h or −h with h = 10. What is the risk premium? Three decimals.', '0.501', 'CE of final wealth = exp(E[ln w]).',
       ['E[ln w] = 0.5 ln 110 + 0.5 ln 90 = ln √(9,900).', 'CE of wealth = √9,900 = 99.499.', 'Risk premium = 100 − 99.499.', eq('RP = 0.501'), 'Arrow Pratt predicts ½ σ² × (1/w) = ½ × 100 × 0.01 = 0.5, very close.'], check=100 - 9900 ** 0.5, tol=0.0005)

# ---------------------------------------------------------------- assignments
K.assign('attitude', 'e', 'Classify a risk attitude',
         '<p>Write <code>attitude(lot, u)</code>. Compute E[u(X)] and u(E[X]) for the lottery (pairs of outcome and probability). Return "averse" if E[u] is smaller by more than 1e-9, "loving" if larger by more than 1e-9, and "neutral" otherwise.</p>',
         '''
def attitude(lot, u):
    # your code here
    pass
''', [("attitude([(0, 0.5), (10, 0.5)], lambda x: x * x)", 'loving'), ("attitude([(0, 0.5), (100, 0.5)], lambda x: x ** 0.5)", 'averse'),
      ("attitude([(0, 0.5), (100, 0.5)], lambda x: 3 * x + 1)", 'neutral')],
         '''
def attitude(lot, u):
    eu = sum(p * u(x) for x, p in lot)
    ue = u(sum(p * x for x, p in lot))
    if eu < ue - 1e-9:
        return "averse"
    if eu > ue + 1e-9:
        return "loving"
    return "neutral"
''', 'Compute both numbers and compare with a small tolerance.', '<p>The first test is practice problem 5 from lecture 3.</p>')
K.assign('ce', 'm', 'Certainty equivalent by bisection',
         '<p>Write <code>certainty_equivalent(lot, u)</code> for an increasing u. Find CE with u(CE) = E[u(X)] by bisection between the smallest and largest outcome, and return it rounded to 2 decimals.</p>',
         '''
def certainty_equivalent(lot, u):
    # your code here
    pass
''', [("certainty_equivalent([(100, 0.2), (0, 0.8)], lambda x: x ** 0.5)", 4.0), ("certainty_equivalent([(0, 0.5), (100, 0.5)], lambda x: x * x)", 70.71),
      ("certainty_equivalent([(20, 0.5), (60, 0.5)], lambda x: x)", 40.0)],
         '''
def certainty_equivalent(lot, u):
    target = sum(p * u(x) for x, p in lot)
    lo = min(x for x, _ in lot)
    hi = max(x for x, _ in lot)
    for _ in range(100):
        mid = (lo + hi) / 2
        if u(mid) < target:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 2)
''', 'Keep halving the interval: if u(mid) is below the target, the answer is to the right.', '<p>The first test is practice problem 4: the lottery is worth only 4 in sure money.</p>')

K.must('Three attitudes', 'Concave u (ln, √): averse, E[u] ≤ u(E[X]). Linear: neutral. Convex (x²): loving. Jensen with the chord picture.')
K.must('Certainty equivalent', 'u(CE) = E[u(X)]. Risk premium = E[X] − CE. √x with 100 at 0.2: EU = 2, CE = 4, sure 30 wins.')
K.must('Fair gamble', '+1 or −1 at 50/50 has mean 0. Play when 0.5u(1) + 0.5u(−1) > u(0). Averse agents refuse.')
K.must('St Petersburg', 'Pays 2ⁿ⁻¹ w.p. 1/2ⁿ. E[X] = Σ ½ = ∞. Log utility: E = ln 2, CE = 2. x² still diverges.')
K.must('Practice 5', 'u = x², 0 or 10: E[X] = 5, u(E[X]) = 25, E[u] = 50, so risk loving.')

T = K.topic(
    slug='risk-attitudes', topic='risk-attitudes', step=(2, 'Choice under risk', 'aai-risk', 'Choose when outcomes are uncertain: lotteries, CDFs, expected utility, compound lotteries and attitudes to risk.', 'College'),
    title='Risk attitudes and the St Petersburg paradox', short='Risk attitudes', badge='2.3', minutes=45,
    lead='See how the curve of a utility function makes someone careful, neutral or bold with risk, price any gamble in sure money, and resolve the St Petersburg paradox.',
    desc='Risk neutral, averse and loving utility through Jensen\'s inequality, the fair gamble, certainty equivalents and risk premiums, practice problems 4 and 5, the St Petersburg game with infinite expected money, log utility giving ln 2 and a certainty equivalent of 2, and why convex utility does not help.',
    summary='Risk attitudes from concavity, certainty equivalent and risk premium, and the St Petersburg paradox with its log utility resolution.',
    keywords=['risk aversion', 'certainty equivalent', 'risk premium', 'St Petersburg paradox', 'log utility', 'concave utility', 'Jensen inequality'],
    recap='<p>Concave utility makes a gamble worth less than its average. The certainty equivalent prices any lottery in sure money, and log utility turns the infinite St Petersburg game into one worth about 2.</p>')
