# Chapter 2.1: lotteries and distributions. Source: lecture 2 (from deterministic to uncertain decisions, nature as a
# player, the action dependent distribution P(. | a), simple lotteries, continuous outcomes such as crop yield, the CDF
# and its four properties, CDF against PDF, interval probabilities, practice problems 5, 7, 8 and 10) and the matching
# review in lecture 3 (sections 16 to 20).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('lottery', r'''
# A simple lottery is a list of (outcome, probability). Check it and build its CDF
lottery = [(10, 0.3), (20, 0.5), (50, 0.2)]

assert all(0 <= p <= 1 for _, p in lottery)
assert abs(sum(p for _, p in lottery) - 1) < 1e-9          # one outcome must happen

def F(x):                       # P(X <= x)
    return sum(p for v, p in lottery if v <= x)

for x in [0, 10, 15, 20, 49.9, 50, 100]:
    print(f"F({x}) = {F(x):.2f}")
print("P(15 < X <= 50) =", round(F(50) - F(15), 2))
''')

K.code('uniform', r'''
# Crop yield uniform between 20 and 60: the CDF is a ramp and every single point has probability 0
lo, hi = 20, 60

def F(x):
    if x <= lo:
        return 0.0
    if x >= hi:
        return 1.0
    return (x - lo) / (hi - lo)

def f(x):                      # density, the slope of F
    return 1 / (hi - lo) if lo <= x <= hi else 0.0

print("F(30) =", F(30), " F(50) =", F(50))
print("P(30 < X <= 50) =", F(50) - F(30))
print("density f(40) =", f(40), " but P(X = 40) = F(40) - F(40) =", F(40) - F(40))
''')

K.lesson('nature', 'When an action has more than one outcome', f'''
<p>So far each action led to one known outcome. Real life is rarely like that. Investing in research may succeed or fail. A crop may yield a lot or a little depending on the rain. The course models this by adding a second player called nature. You choose an action, then nature picks the outcome at random.</p>
<p>Nature is not a person. It stands for weather, markets, disease, traffic, and anything else outside your control. What you know is the probability with which nature picks each outcome, and that probability can depend on your action.</p>
{fxs(
    fx('Lottery of an action', '<i>P</i>( <i>x</i><sub><i>i</i></sub> | <i>a</i> ) = <i>p</i><sub><i>i</i></sub>, &nbsp; 0 ≤ <i>p</i><sub><i>i</i></sub> ≤ 1, &nbsp; ∑ <i>p</i><sub><i>i</i></sub> = 1', 'A simple lottery lists every final outcome with its probability. The probabilities add to 1 because exactly one outcome happens.', key=True),
    fx('Deterministic as a special case', '<i>P</i>( <i>c</i>(<i>a</i>) | <i>a</i> ) = 1', 'A certain action is a lottery that puts all its probability on one outcome.'))}
{table(['', 'Deterministic choice', 'Risky choice'], [
    ['Action leads to', 'One known outcome', 'A distribution of outcomes'],
    ['Compare', 'u(c(a))', 'E[u(X) | a]'],
    ['Tree contains', 'Decision nodes only', 'Decision nodes and chance nodes'],
    ['Ranking enough?', 'Yes, ordinal utility works', 'No, cardinal utility is needed (chapter 2.2)']])}
{steps('Lecture example of a simple lottery', [
    'Action a gives x₁ with 0.6, x₂ with 0.3, x₃ with 0.1.',
    'Each probability lies between 0 and 1.',
    eq('0.6 + 0.3 + 0.1 = 1, so this is a valid lottery')])}
''', kw=['lottery', 'nature', 'uncertainty', 'chance node', 'simple lottery', 'conditional distribution'])

K.lesson('cdf', 'The cumulative distribution function', f'''
<p>When the outcome can be any number, such as a crop yield of 1.2, 1.21 or 1.2135 tonnes, we cannot list every outcome with its own probability. Instead we ask: what is the chance the outcome is at most x? That function of x is the CDF.</p>
{fxs(
    fx('CDF of an action', '<i>F</i><sub><i>a</i></sub>(<i>x</i>) = <i>P</i>( <i>X</i> ≤ <i>x</i> | <i>a</i> )', 'The probability that the outcome is at most x when you take action a.', key=True),
    fx('Interval probability', '<i>P</i>( <i>r</i> &lt; <i>X</i> ≤ <i>s</i> | <i>a</i> ) = <i>F</i><sub><i>a</i></sub>(<i>s</i>) − <i>F</i><sub><i>a</i></sub>(<i>r</i>)', 'Everything up to s minus everything up to r.', key=True))}
<h3>The four properties of every CDF</h3>
{table(['Property', 'Formula', 'Plain meaning'], [
    ['Non decreasing', 'x &lt; y ⟹ F(x) ≤ F(y)', 'More room below means at least as much probability'],
    ['Lower limit', 'F(x) → 0 as x → −∞', 'Nothing lies below everything'],
    ['Upper limit', 'F(x) → 1 as x → +∞', 'Everything lies below infinity'],
    ['Right continuous', 'F(x) = lim F(x + h) as h ↓ 0', 'At a jump the filled dot sits on the upper step']])}
{viz('cdf')}
{note('F(50) = 0.7 means a 70% chance the outcome is at most 50. It does not mean a 70% chance the outcome is exactly 50. This misreading is the most common exam error on CDFs.', 'warn')}
{code('lottery')}
{steps('Practice problem 8: F(50) = 0.8 and F(20) = 0.3. Find P(20 &lt; X ≤ 50)', [
    'Use the interval rule P(r &lt; X ≤ s) = F(s) − F(r).',
    'Here r = 20 and s = 50.',
    eq('P = 0.8 − 0.3 = 0.5')])}
''', kw=['CDF', 'cumulative distribution function', 'right continuous', 'non decreasing', 'interval probability', 'crop yield'])

K.lesson('pdf', 'Densities and continuous outcomes', f'''
<p>For a continuous outcome the CDF has a slope. That slope is the probability density function, the PDF. The density says how crowded the probability is near x. It is not itself a probability, and it can be bigger than 1.</p>
{fxs(
    fx('From density to CDF', '<i>F</i><sub><i>a</i></sub>(<i>x</i>) = ∫<sub>−∞</sub><sup><i>x</i></sup> <i>f</i><sub><i>a</i></sub>(<i>t</i>) d<i>t</i>', 'Add up the density from the far left up to x.', key=True),
    fx('From CDF to density', '<i>f</i><sub><i>a</i></sub>(<i>x</i>) = ' + frac('d', 'd<i>x</i>') + ' <i>F</i><sub><i>a</i></sub>(<i>x</i>)', 'Wherever the derivative exists.'),
    fx('Single points', '<i>P</i>( <i>X</i> = <i>x</i> ) = 0 &nbsp; for a continuous <i>X</i>', 'Only intervals carry probability.'))}
{code('uniform')}
{table(['Lottery', 'CDF F(x)', 'Shape'], [
    ['Discrete, outcomes xᵢ with pᵢ', 'Sum of pᵢ with xᵢ ≤ x', 'A staircase with jumps of size pᵢ'],
    ['Uniform on [L, U]', '(x − L) ÷ (U − L) inside', 'A straight ramp from 0 to 1'],
    ['Exponential with rate λ', '1 − e<sup>−λx</sup> for x ≥ 0', 'Rises fast then flattens'],
    ['Normal with mean μ and spread σ', 'Φ((x − μ) ÷ σ)', 'An S curve centred on μ']])}
{viz('cdf', kind='unif', a=20, b=60, r=30, s=50)}
{scene('a fertilizer decision', '<p>A farmer choosing how much fertilizer to buy faces a different yield distribution for each choice. Light fertilizer might give a yield uniform on 20 to 40 tonnes, heavy fertilizer uniform on 15 to 60. Heavy has more upside and more downside. The CDF of each action is what the farmer compares, and chapter 2.2 shows how expected utility turns that comparison into one number per action.</p>')}
{deep('First order stochastic dominance', '<p>Action a dominates action b in the first order sense when F<sub>a</sub>(x) ≤ F<sub>b</sub>(x) for every x, with strict inequality somewhere. In words, a is less likely than b to fall below any threshold. Every agent who prefers more to less then prefers a, whatever its risk attitude. When the two CDFs cross, the choice depends on the utility function, which is why expected utility is needed.</p>')}
{ladder(
    '<p>When you cannot be sure what will happen, list what could happen and how likely each thing is. That list is a lottery.</p>',
    '<p>An action under risk gives a distribution P(· | a). The CDF F(x) = P(X ≤ x) is non decreasing, goes from 0 to 1 and is right continuous. Intervals use F(s) − F(r). A density is the slope of F.</p>',
    '<p>The CDF determines the distribution completely, and expectations are written as Lebesgue Stieltjes integrals ∫ u dF, which handle discrete, continuous and mixed cases with one formula. First and second order stochastic dominance compare CDFs directly.</p>',
    '<p>Distributional reinforcement learning (Bellemare, Dabney and Munos 2017) learns the whole return distribution, often through its quantile function, the inverse of the CDF, rather than only its mean. Risk sensitive policies then optimize a quantile or a tail measure such as CVaR.</p>')}
''', kw=['PDF', 'density', 'uniform', 'exponential', 'normal', 'stochastic dominance', 'continuous outcome'])


K.lesson('levels', 'From intuition to research', f'''
<p>A lottery lists what can happen and how likely each outcome is. The cumulative distribution function packs the same information into one rising curve.</p>
{scene('a cricket forecast', '<p>Before a match a forecaster says: win 0.6, draw 0.1, lose 0.3. That is a lottery over three outcomes. The probabilities add to 1, and a team choosing whether to declare early is really choosing between two such lotteries.</p>')}
{steps('Work it out: the CDF of a fair die', ['X takes 1 to 6, each with probability 1/6.', 'F(x) = P(X ≤ x). F(3) = 3/6 = 0.5.', 'F(3.5) is still 0.5, because no outcome lies between 3 and 3.5.', eq('P(2 < X ≤ 5) = F(5) − F(2) = 5/6 − 2/6 = 0.5')])}
{deep('the analysis', '<p>Every CDF is non-decreasing, right continuous, tends to 0 on the left and to 1 on the right, and P(a < X ≤ b) = F(b) − F(a). For a discrete lottery F is a staircase whose jumps are the probabilities. For a continuous one F is smooth and its slope is the density f = F′.</p>')}
{deep('the research view', '<p>First order stochastic dominance compares whole distributions: if F<sub>A</sub>(x) ≤ F<sub>B</sub>(x) for every x, then every person who prefers more to less prefers A. Machine learning papers now use this test to compare the score distributions of models over many random seeds instead of comparing single averages (Dror et al. 2019, "Deep Dominance").</p>')}
{note('A density can be larger than 1. The uniform density on [0, 0.5] equals 2. Only the area under it must be 1.', 'warn')}
''', kw=['lottery', 'CDF', 'step function', 'stochastic dominance', 'model comparison'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In a decision tree, what does nature stand for?', ['A second rational player', 'Randomness outside your control', 'The best action', 'The utility function'], 1,
       'Weather, markets, luck.', 'Nature picks an outcome at random with known probabilities.')
K.quiz('e', 'The probabilities of a simple lottery must', ['Add to 1', 'Add to 100', 'All be equal', 'Be larger than 0.5'], 0,
       'One outcome must happen.', 'Each pᵢ lies in [0, 1] and they add to 1.')
K.quiz('e', 'F(x) is', ['P(X = x)', 'P(X ≤ x)', 'P(X > x)', 'The density at x'], 1,
       'Cumulative.', 'The CDF accumulates all probability at or below x.')
K.quiz('e', 'F(20) = 0.4 means', ['X equals 20 with probability 0.4', 'X is at most 20 with probability 0.4', 'X is above 20 with probability 0.4', 'The density at 20 is 0.4'], 1,
       'At most.', 'Practice problem 7: a 40% chance the outcome is at most 20.')
K.quiz('m', 'Which is NOT a property of every CDF?', ['Non decreasing', 'Tends to 1 at +∞', 'Right continuous', 'Differentiable everywhere'], 3,
       'Think of a staircase.', 'A discrete lottery has jumps, so its CDF is not differentiable there.')
K.quiz('m', 'F(50) = 0.8 and F(20) = 0.3. P(20 < X ≤ 50) =', ['0.3', '0.5', '0.8', '1.1'], 1,
       'Subtract.', '0.8 − 0.3 = 0.5.')
K.quiz('m', 'For a continuous X, P(X = 40) is', ['f(40)', 'F(40)', '0', '1'], 2,
       'A single point has no width.', 'Only intervals have positive probability for a continuous variable.')
K.quiz('m', 'A density f can be', ['Only between 0 and 1', 'Larger than 1 on a short interval', 'Negative', 'Decreasing only'], 1,
       'It is not a probability.', 'Uniform on [0, 0.5] has density 2. Only the area under f must be 1.')
K.quiz('h', 'The CDF of a discrete lottery jumps at each outcome by', ['1', 'That outcome\'s probability', 'The outcome value', '0.5'], 1,
       'Staircase.', 'The jump at xᵢ is P(X = xᵢ) = pᵢ.')
K.quiz('h', 'At a jump of a discrete CDF, the value F(x) equals', ['The lower step', 'The upper step', 'The average of both', 'Undefined'], 1,
       'Right continuity.', 'F(x) includes P(X = x), so the filled dot is on the upper step.')
K.quiz('x', 'Action a first order stochastically dominates b when', ['E[a] > E[b]', 'Fa(x) ≤ Fb(x) for all x', 'Fa(x) ≥ Fb(x) for all x', 'Var(a) < Var(b)'], 1,
       'a is less likely to fall below any level.', 'Lower CDF everywhere means more probability on high outcomes.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'An action gives 100 with probability 0.3 and 40 otherwise. What is P(40)?', '0.7', 'Probabilities add to 1.',
       ['There are two outcomes.', 'P(100) + P(40) = 1.', eq('P(40) = 1 − 0.3 = 0.7')], check=0.7)
K.calc('e', 'Lottery: 10 with 0.3, 20 with 0.5, 50 with 0.2. What is F(20)?', '0.8', 'Add the outcomes at or below 20.',
       ['Outcomes ≤ 20 are 10 and 20.', 'Their probabilities are 0.3 and 0.5.', eq('F(20) = 0.3 + 0.5 = 0.8')], check=0.8)
K.calc('e', 'For the same lottery, what is F(15)?', '0.3', 'Only 10 is at or below 15.',
       ['10 ≤ 15, 20 &gt; 15.', 'Only P(10) counts.', eq('F(15) = 0.3')], check=0.3)
K.calc('m', 'For the same lottery, what is P(15 &lt; X ≤ 50)?', '0.7', 'F(50) − F(15).',
       ['F(50) = 1, since every outcome is at most 50.', 'F(15) = 0.3.', eq('P = 1 − 0.3 = 0.7')], check=0.7)
K.calc('m', 'Yield is uniform on [20, 60]. What is F(50)?', '0.75', 'A straight ramp.',
       ['F(x) = (x − 20) ÷ (60 − 20) inside the interval.', '(50 − 20) ÷ 40 = 30 ÷ 40.', eq('F(50) = 0.75')], check=0.75)
K.calc('m', 'Yield is uniform on [20, 60]. What is the density f(x) inside the interval?', '0.025', 'Area 1 over width 40.',
       ['The density is constant on [20, 60].', 'Total area must be 1, and the width is 40.', eq('f = 1 ÷ 40 = 0.025')], check=0.025)
K.calc('m', 'Practice problem 10: S with 0.6 then 10 with 0.8, or F with 0.4 then 10 with 0.3. What is P(10)?', '0.6', 'Multiply along paths, add paths.',
       ['Path S then 10: 0.6 × 0.8 = 0.48.', 'Path F then 10: 0.4 × 0.3 = 0.12.', eq('P(10) = 0.48 + 0.12 = 0.60')], check=0.6)
K.calc('h', 'Waiting time is exponential with F(x) = 1 − e^(−0.5x). What is P(2 &lt; X ≤ 4)? Four decimals.', '0.2325', 'F(4) − F(2).',
       ['F(4) = 1 − e<sup>−2</sup> = 0.8647.', 'F(2) = 1 − e<sup>−1</sup> = 0.6321.', eq('P = 0.8647 − 0.6321 = 0.2325')], check=0.23254415793482963, tol=0.00005)
K.calc('h', 'F(x) = x² on [0, 1]. What is the density at x = 0.75?', '1.5', 'Differentiate.',
       ['f(x) = d/dx x² = 2x.', 'At x = 0.75: 2 × 0.75.', eq('f(0.75) = 1.5'), 'A density above 1 is fine. Only its total area must be 1.'], check=1.5)
K.calc('h', 'A lottery has F(30) = 0.45 and P(X = 30) = 0.15. What is P(X &lt; 30)?', '0.3', 'F includes the point itself.',
       ['F(30) = P(X &lt; 30) + P(X = 30).', '0.45 = P(X &lt; 30) + 0.15.', eq('P(X &lt; 30) = 0.30')], check=0.3)
K.calc('x', 'Action a has yield uniform on [20, 40], action b uniform on [15, 60]. At which x do their CDFs cross?', '24', 'Set the two ramps equal.',
       ['F<sub>a</sub>(x) = (x − 20) ÷ 20 and F<sub>b</sub>(x) = (x − 15) ÷ 45.', '45(x − 20) = 20(x − 15), so 45x − 900 = 20x − 300.', eq('25x = 600, x = 24'), 'Below 24 action a is safer. The CDFs cross, so neither action dominates in the first order sense.'], check=24)

# ---------------------------------------------------------------- assignments
K.assign('valid', 'e', 'Is it a lottery?',
         '<p>Write <code>is_lottery(lot)</code> for a list of (outcome, probability) pairs. Return True when every probability is in [0, 1] and they add to 1 within 1e-9.</p>',
         '''
def is_lottery(lot):
    # your code here
    pass
''', [("is_lottery([(1, 0.6), (2, 0.3), (3, 0.1)])", True), ("is_lottery([(1, 0.6), (2, 0.6)])", False), ("is_lottery([(1, 1.2), (2, -0.2)])", False)],
         '''
def is_lottery(lot):
    ps = [p for _, p in lot]
    return all(0 <= p <= 1 for p in ps) and abs(sum(ps) - 1) < 1e-9
''', 'Check both conditions. The third test adds to 1 but has an invalid probability.', '<p>Both conditions matter. Probabilities outside [0, 1] can still add to 1.</p>')
K.assign('cdf', 'm', 'CDF and interval of a discrete lottery',
         '<p>Write <code>interval(lot, r, s)</code> that returns P(r &lt; X ≤ s) for a discrete lottery given as (outcome, probability) pairs, rounded to 4 decimals. Return 0 when r ≥ s.</p>',
         '''
def interval(lot, r, s):
    # your code here
    pass
''', [("interval([(10, 0.3), (20, 0.5), (50, 0.2)], 15, 50)", 0.7), ("interval([(10, 0.3), (20, 0.5), (50, 0.2)], 10, 20)", 0.5),
      ("interval([(10, 0.3), (20, 0.5), (50, 0.2)], 60, 20)", 0)],
         '''
def interval(lot, r, s):
    if r >= s:
        return 0
    F = lambda x: sum(p for v, p in lot if v <= x)
    return round(F(s) - F(r), 4)
''', 'Write F(x) first, then subtract. Note that the left end is open: 10 is not in (10, 20].', '<p>The second test checks the open left end: X = 10 is excluded, X = 20 is included.</p>')

K.must('Lottery', 'Action a gives P(xᵢ | a) = pᵢ with pᵢ in [0, 1] and Σ pᵢ = 1. Nature picks the outcome.')
K.must('CDF', 'F(x) = P(X ≤ x | a). Non decreasing, 0 at −∞, 1 at +∞, right continuous. F(50) = 0.7 is "at most 50".')
K.must('Intervals', 'P(r < X ≤ s) = F(s) − F(r). Notes example 0.8 − 0.3 = 0.5.')
K.must('Density', 'F = ∫ f, f = F′. P(X = x) = 0 for continuous X. Densities can exceed 1.')
K.must('Compound paths', 'Multiply along each path, add the paths that reach the same outcome: 0.6 × 0.8 + 0.4 × 0.3 = 0.6.')

T = K.topic(
    slug='lotteries-cdf', topic='lotteries-cdf', step=(2, 'Choice under risk', 'aai-risk', 'Choose when outcomes are uncertain: lotteries, CDFs, expected utility, compound lotteries and attitudes to risk.', 'College'),
    title='Lotteries and distributions', short='Lotteries', badge='2.1', minutes=40,
    lead='Let nature pick the outcome, describe each action by a lottery, and read probabilities from a CDF without the usual traps.',
    desc='Nature and action dependent distributions, simple lotteries, continuous outcomes, the CDF and its four properties, interval probabilities, densities, uniform, exponential and normal examples, stochastic dominance, and practice problems 7, 8 and 10.',
    summary='Lotteries, the CDF and its properties, intervals, densities and continuous outcomes.',
    keywords=['lottery', 'CDF', 'PDF', 'nature', 'interval probability', 'uniform distribution', 'stochastic dominance'],
    recap='<p>Under risk an action is a lottery. The CDF F(x) = P(X ≤ x) describes it completely, and intervals come from F(s) − F(r).</p>')
