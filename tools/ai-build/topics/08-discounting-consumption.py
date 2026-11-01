# Chapter 3.2: discounting and consumption over time. Source: lecture 4 (the bank interest derivation of
# delta = 1/(1+r), A delta^n, delta as patience not a choice, the operation example, the discounted R&D branch 10 delta - 1,
# exponential against hyperbolic discounting, two period ln consumption x1 = K/(1+delta), the three period whiteboard
# solution, diminishing marginal utility, homework 1 with linear utility, homework 2 time consistency, the convex x^2
# corner example with K = 10 and delta = 0.8, practice problem B (520.2) and practice problem D (K = 181 gives 100 and 81)).
from cvkit import Kit, fx, fxs, frac, sqrt, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('pv', r'''
# Present value of a stream of payments with discount factor delta
def present_value(payments, delta):
    return sum(x * delta ** t for t, x in enumerate(payments, start=1))

delta = 0.9
print("scholarship PV =", round(present_value([200, 150, 300], delta), 2))
print("implied interest rate r =", round(1 / delta - 1, 4))
for d in (1.0, 0.9, 0.5, 0.1):
    print(f"delta = {d}: 100 a year for 5 years is worth {present_value([100] * 5, d):7.2f} today")
''')

K.code('consume', r'''
# Three period consumption with u = ln x: the formula, then a check that nearby plans are worse
import math
K, d = 100, 0.9
s = 1 + d + d * d
plan = (K / s, d * K / s, d * d * K / s)
print("formula :", [round(x, 3) for x in plan])

def V(x1, x2):
    return math.log(x1) + d * math.log(x2) + d * d * math.log(K - x1 - x2)

# Move 1 unit between periods: every nearby plan is worse
for dx1, dx2 in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]:
    gap = V(plan[0] + dx1, plan[1] + dx2) - V(plan[0], plan[1])
    print("shift", (dx1, dx2), "change in value", round(gap, 5))

# Time consistency: re-plan in period 2 with what is left
R = K - plan[0]
print("re-plan :", round(R / (1 + d), 3), round(d * R / (1 + d), 3), " same as the original x2, x3")
''')

K.lesson('discount', 'Why money later is worth less', f'''
<p>Put 100 rupees in a bank paying interest r. After a year you have 100(1 + r). Now turn the question round. Someone promises you 100 a year from now. What is that promise worth today? It is the amount X that would grow into 100, so X(1 + r) = 100.</p>
{fxs(
    fx('Discount factor', 'δ = ' + frac('1', '1 + <i>r</i>') + ', &nbsp; 0 &lt; δ &lt; 1', 'A rupee next period is worth δ rupees today.', key=True),
    fx('n periods ahead', 'value today of <i>A</i> received after <i>n</i> periods = <i>A</i> δ<sup><i>n</i></sup> = ' + frac('<i>A</i>', '(1 + <i>r</i>)<sup><i>n</i></sup>'), 'Two periods: 100 grows to 100(1 + r)², so it is worth 100δ² today.', key=True),
    fx('Present value of a stream', 'PV = ∑<sub><i>t</i></sub> <i>x</i><sub><i>t</i></sub> δ<sup><i>t</i></sup>', 'Discount each payment by its own delay, then add.'))}
<p>δ is not something you choose. It describes how patient you are. The professor\'s example: if you need money for an operation today, a payment tomorrow is worth very little to you, so your δ is close to 0. Someone with no urgent needs has δ close to 1.</p>
{viz('discount')}
{steps('Practice problem B: a scholarship pays 200, 150 and 300 at the ends of years 1, 2 and 3, with δ = 0.9', [
    '200 × 0.9 = 180.',
    '150 × 0.81 = 121.5.',
    '300 × 0.729 = 218.7.',
    eq('PV = 180 + 121.5 + 218.7 = 520.2'),
    'The implied interest rate is r = 1/δ − 1 = 1/0.9 − 1 ≈ 11.1% a year.'])}
<h3>Discounting inside a decision tree</h3>
<p>In the discounted R&D tree, research costs 1 today and pays 10 next period if it works. The branch value is 10δ − 1, not (10 − 1)δ. The cost is paid now, so it is not discounted. Only the later gain is.</p>
{code('pv')}
''', kw=['discount factor', 'present value', 'interest rate', 'patience', 'delta', 'time value of money', 'practice problem B'])

K.lesson('consume', 'Spreading consumption over time', f'''
<p>You have a total income K to spend over several periods. Each period you enjoy u(x) from spending x, with u′ &gt; 0 (more is better) and u″ &lt; 0 (each extra rupee adds a little less). Later enjoyment is discounted by δ. How should you split K?</p>
{fxs(
    fx('Two periods, u = ln x', 'max ln <i>x</i>₁ + δ ln(<i>K</i> − <i>x</i>₁) &nbsp; ⟹ &nbsp; <i>x</i>₁* = ' + frac('<i>K</i>', '1 + δ') + ', &nbsp; <i>x</i>₂* = ' + frac('δ<i>K</i>', '1 + δ'), 'From 1/x₁ = δ/(K − x₁).', key=True),
    fx('Three periods, u = ln x', '<i>x</i>₁* = ' + frac('<i>K</i>', '1 + δ + δ²') + ', &nbsp; <i>x</i>₂* = ' + frac('δ<i>K</i>', '1 + δ + δ²') + ', &nbsp; <i>x</i>₃* = ' + frac('δ²<i>K</i>', '1 + δ + δ²'), 'The board solution from lecture 4.', key=True),
    fx('Equal discounted marginal utility', '1/<i>x</i>₁* = δ/<i>x</i>₂* = δ²/<i>x</i>₃*', 'No small move of money between two periods can raise the total.'))}
{steps('The whiteboard derivation for three periods', [
    'Maximize ln x₁ + δ ln x₂ + δ² ln(K − x₁ − x₂).',
    '∂/∂x₁: 1/x₁ − δ²/(K − x₁ − x₂) = 0. ∂/∂x₂: δ/x₂ − δ²/(K − x₁ − x₂) = 0.',
    'Both equal the same δ²/x₃, so 1/x₁ = δ/x₂, giving x₁ = x₂/δ. Likewise x₃ = δx₂.',
    'ln is increasing, so spend everything: x₂/δ + x₂ + δx₂ = K.',
    eq('x₂*(1 + δ + δ²) = δK, so x₂* = δK/(1 + δ + δ²)')])}
{viz('consume')}
{code('consume')}
{note('Diminishing marginal utility means u″ &lt; 0, not u′ falling to zero. Going from 10 to 11 rupees adds more than going from 110 to 111, but both add something. The first order condition sets the derivative of the whole objective to zero, never u′ itself.', 'tip')}
{steps('Practice problem D: u = √x, two periods', [
    'Maximize √x₁ + δ√(K − x₁).',
    'Derivative: 1/(2√x₁) − δ/(2√(K − x₁)) = 0, so √(K − x₁) = δ√x₁.',
    'Square: K − x₁ = δ²x₁, so x₁* = K/(1 + δ²).',
    eq('K = 181, δ = 0.9: x₁* = 181/1.81 = 100 and x₂* = 81')])}
''', kw=['consumption smoothing', 'two period', 'three period', 'first order conditions', 'diminishing marginal utility', 'practice problem D', 'Euler equation'])

K.lesson('corners', 'Corners, homework and time consistency', f'''
<h3>Homework 1: linear utility</h3>
<p>With u(x) = x the objective is x₁ + δx₂ + δ²x₃ with x₁ + x₂ + x₃ = K. The coefficient on x₁ is the largest because 1 &gt; δ &gt; δ². There is no curvature to reward spreading, so all the money goes to the earliest period.</p>
{fxs(fx('Linear utility', '<i>x</i>* = (<i>K</i>, 0, 0)', 'A linear objective over a budget is maximized at a corner.'))}
<h3>Convex utility: the derivative finds the worst point</h3>
<p>With u(x) = x² in two periods, v(x) = x² + δ(K − x)² is convex in x. Setting v′ = 0 finds its minimum, the worst split. The best plan is a corner: compare v(K) = K² with v(0) = δK². Since δ &lt; 1, consume everything now. With δ = 1 the two corners tie, but splitting is still worse.</p>
{steps('Lecture example: K = 10, δ = 0.8, u = x²', [
    'v(x) = x² + 0.8(10 − x)².',
    'v′(x) = 2x − 1.6(10 − x) = 0 gives x = 16/3.6 = 4.44, where v = 44.4. That is the minimum.',
    'Corners: v(10) = 100 and v(0) = 80.',
    eq('Best: x₁ = 10, x₂ = 0, payoff 100')])}
<h3>Homework 2: is the plan time consistent?</h3>
{steps('Re-plan in period 2 with what is left', [
    'After x₁* = K/(1 + δ + δ²), the remaining money is R = Kδ(1 + δ)/(1 + δ + δ²).',
    'From period 2 the problem is the two period one with R: x₂ = R/(1 + δ), x₃ = δR/(1 + δ).',
    'Substitute R: x₂ = Kδ/(1 + δ + δ²) and x₃ = Kδ²/(1 + δ + δ²).',
    eq('These are the original x₂* and x₃*, so the plan is time consistent')])}
{table(['Discounting', 'Weight on period t', 'Re-planning later'], [
    ['Exponential', 'δ<sup>t</sup>', 'Keeps the original plan (time consistent)'],
    ['Hyperbolic', '1/(1 + kt)', 'Wants to change it (time inconsistent): impatience is strongest about the near future']])}
{deep('Why exponential discounting is time consistent', '<p>The trade off between periods t and t + 1 has relative weight δ<sup>t+1</sup>/δ<sup>t</sup> = δ, the same no matter when you look at it. So today\'s view of tomorrow against the day after is the same as tomorrow\'s view. With hyperbolic weights 1/(1 + kt), the ratio between t and t + 1 seen from today is (1 + kt)/(1 + k(t + 1)), close to 1 for large t, but seen from period t it becomes 1/(1 + k), much smaller. Plans made today for the far future look too patient once that future arrives, which is the economics of procrastination.</p>')}
{ladder(
    '<p>A rupee today is worth more than a rupee next year, because today\'s rupee could earn interest. If more money makes you a little less happy each time, you should spread spending out instead of spending it all at once.</p>',
    '<p>δ = 1/(1 + r), and A received in n periods is worth Aδⁿ. With concave u the optimal plan equalizes discounted marginal utilities, so for ln x the shares are 1 : δ : δ². Linear or convex u sends everything to a corner.</p>',
    '<p>The intertemporal Euler equation u′(x<sub>t</sub>) = δ(1 + r) u′(x<sub>t+1</sub>) generalizes the first order conditions. Exponential discounting is the only time consistent stationary scheme. Quasi hyperbolic β δ discounting (Laibson 1997) models present bias.</p>',
    '<p>In reinforcement learning the discount γ in Σ γ<sup>t</sup> r<sub>t</sub> plays the role of δ, keeping returns finite and trading off near against far rewards. Work on hyperbolic discounting in RL (Fedus et al. 2019) learns values for many γ at once and combines them into a hyperbolic weighting.</p>')}
''', kw=['corner solution', 'linear utility', 'convex utility', 'time consistency', 'exponential discounting', 'hyperbolic discounting', 'homework'])


K.lesson('levels', 'From intuition to research', f'''
<p>Discounting compares money and happiness at different times. The same factor δ appears in savings decisions and in every reinforcement learning agent.</p>
{scene('1000 rupees now or 1100 next year', '<p>If a bank pays 8 percent interest, 1000 rupees today grows to 1080 in a year. An offer of 1100 next year is therefore better than 1000 today. The present value of 1100 is what you would need to deposit today to reach it.</p>')}
{steps('Work it out: present value at r = 0.08', ['Discount factor δ = 1 ÷ (1 + r) = 1 ÷ 1.08 = 0.9259.', 'Present value of 1100 = 1100 × 0.9259.', eq('= 1018.52 > 1000, so waiting is better'), 'At r = 0.12 the present value is 1100 ÷ 1.12 = 982.14, and taking the money now is better.'])}
{deep('the analysis', '<p>For lifetime utility ∑ δ<sup>t</sup> u(c<sub>t</sub>) with interest rate r, the first order condition is the Euler equation u′(c<sub>t</sub>) = δ(1 + r) u′(c<sub>t+1</sub>). With δ(1 + r) = 1 marginal utilities are equal across periods, so a concave u gives equal consumption: people smooth spending. Exponential discounting is time consistent, a plan made today is still optimal tomorrow.</p>')}
{deep('the research view', '<p>Reinforcement learning maximises ∑ γ<sup>t</sup> r<sub>t</sub>, and 1 ÷ (1 − γ) is the effective planning horizon: γ = 0.99 looks about 100 steps ahead. People often discount hyperbolically, 1 ÷ (1 + kt), which makes plans time inconsistent (Laibson 1997): the gym plan made on Sunday is dropped on Monday.</p>')}
{note('The discount rate r and the discount factor δ = 1 ÷ (1 + r) are different numbers. A higher rate means a lower factor.', 'warn')}
''', kw=['present value', 'discount factor', 'Euler equation', 'hyperbolic discounting', 'RL horizon'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'With interest rate r, the discount factor is', ['1 + r', '1/(1 + r)', 'r', '1 − r'], 1,
       'X(1 + r) = 100.', 'δ = 1/(1 + r), which lies between 0 and 1.')
K.quiz('e', 'A payoff A received n periods from now is worth today', ['A', 'Aδ', 'Aδⁿ', 'A/n'], 2,
       'One factor of δ per period.', 'Two periods: 100 grows to 100(1 + r)², so it is worth 100δ².')
K.quiz('e', 'A very impatient person has δ', ['Close to 1', 'Close to 0', 'Above 1', 'Negative'], 1,
       'Tomorrow matters little.', 'Small δ means future money counts for very little today.')
K.quiz('e', 'Can a player choose its own δ in this model?', ['Yes, to maximize payoff', 'No, δ describes the player\'s patience', 'Only in games', 'Only when r = 0'], 1,
       'It is a property, not an action.', 'Actions are things like g or s. δ is part of who the player is.')
K.quiz('m', 'In the discounted R&D branch, the value is', ['(10 − 1)δ', '10δ − 1', '10 − δ', '10 − 1'], 1,
       'When is each paid?', 'The cost is paid today, the gain arrives next period, so only the gain is discounted.')
K.quiz('m', 'Two periods, u = ln x: x₁* =', ['K/2', 'K/(1 + δ)', 'δK/(1 + δ)', 'K'], 1,
       '1/x₁ = δ/(K − x₁).', 'Solving gives K − x₁ = δx₁.')
K.quiz('m', 'With u(x) = x and 0 < δ < 1 over three periods, the optimal plan is', ['(K/3, K/3, K/3)', '(K, 0, 0)', '(0, 0, K)', 'Any plan'], 1,
       'Largest coefficient.', 'x₁ has weight 1, the biggest, and there is no curvature to spread for.')
K.quiz('m', 'For u = x² over two periods, setting the derivative to zero finds', ['The best split', 'The worst split', 'The time consistent plan', 'Nothing'], 1,
       'The objective is convex.', 'A convex function has a minimum at its stationary point, so the maximum is at a corner.')
K.quiz('h', 'Exponential discounting is time consistent because', ['δ is small', 'The relative weight of t + 1 against t is always δ, whenever you look', 'Money grows', 'u is concave'], 1,
       'Look at the ratio.', 'δ^(t+1)/δ^t = δ for every t, so later selves agree with earlier ones.')
K.quiz('h', 'At the ln optimum over three periods, which holds?', ['x₁ = x₂ = x₃', '1/x₁ = δ/x₂ = δ²/x₃', 'x₁ = δx₂', 'x₃ > x₂ > x₁'], 1,
       'Equal discounted marginal utility.', 'u′(x) = 1/x, weighted by δᵗ, must be equal across periods.')
K.quiz('x', 'Hyperbolic discounting 1/(1 + kt) leads to', ['Time consistency', 'Plans that later selves want to change', 'Linear utility', 'Corner solutions only'], 1,
       'Present bias.', 'The ratio of weights between two dates depends on when you evaluate it, so re-planning changes the plan.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'r = 25%. What is δ?', '0.8', 'δ = 1/(1 + r).',
       ['1 + r = 1.25.', 'δ = 1 ÷ 1.25.', eq('δ = 0.8')], check=0.8)
K.calc('e', 'δ = 0.9. What is 100 received in 2 periods worth today?', '81', '100δ².',
       ['δ² = 0.81.', '100 × 0.81.', eq('= 81')], check=81)
K.calc('e', 'Practice problem B: PV of 200, 150, 300 at the end of years 1, 2, 3 with δ = 0.9?', '520.2', 'Discount each one.',
       ['200 × 0.9 = 180.', '150 × 0.81 = 121.5 and 300 × 0.729 = 218.7.', eq('PV = 520.2')], check=520.2, tol=0.001)
K.calc('m', 'Two periods, ln utility, K = 190, δ = 0.9. What is x₁*?', '100', 'K/(1 + δ).',
       ['1 + δ = 1.9.', 'x₁* = 190 ÷ 1.9.', eq('x₁* = 100, x₂* = 90')], check=100)
K.calc('m', 'Three periods, ln utility, K = 100, δ = 0.9. What is x₁*? Three decimals.', '36.900', 'K/(1 + δ + δ²).',
       ['1 + 0.9 + 0.81 = 2.71.', 'x₁* = 100 ÷ 2.71.', eq('x₁* = 36.900, x₂* = 33.210, x₃* = 29.889')], check=100 / 2.71, tol=0.0005)
K.calc('m', 'Practice problem D: √x utility, K = 181, δ = 0.9. What is x₂*?', '81', 'δ²K/(1 + δ²).',
       ['δ² = 0.81 and 1 + δ² = 1.81.', 'x₁* = 181 ÷ 1.81 = 100.', eq('x₂* = 181 − 100 = 81')], check=81)
K.calc('m', 'Discounted R&D: what is 10δ − 1 when δ = 0.9?', '8', 'Discount only the gain.',
       ['10 × 0.9 = 9.', 'Subtract the cost paid today.', eq('9 − 1 = 8')], check=8)
K.calc('h', 'Convex example: K = 10, δ = 0.8, u = x². Where is the stationary point of v(x) = x² + 0.8(10 − x)²? Four decimals.', '4.4444', 'Solve 2x − 1.6(10 − x) = 0.',
       ['v′(x) = 2x − 1.6(10 − x).', '2x + 1.6x = 16, so 3.6x = 16.', eq('x = 4.4444, where v = 44.44, the minimum'), 'The corners give v(10) = 100 and v(0) = 80, so consume all now.'], check=16 / 3.6, tol=0.00005)
K.calc('h', 'Three periods, ln, K = 100, δ = 0.9. After x₁*, how much money R is left? Three decimals.', '63.100', 'R = K − x₁*.',
       ['x₁* = 36.900.', 'R = 100 − 36.900.', eq('R = 63.100, and R/(1 + δ) = 33.210 = x₂*')], check=100 - 100 / 2.71, tol=0.0005)
K.calc('h', 'Hyperbolic weights 1/(1 + kt) with k = 0.5. What is the PV of 100 at each of t = 1 and t = 2? Two decimals.', '116.67', 'Add 100/1.5 and 100/2.',
       ['t = 1: 100 ÷ 1.5 = 66.67.', 't = 2: 100 ÷ 2 = 50.', eq('PV = 116.67')], check=100 / 1.5 + 50, tol=0.005)
K.calc('x', 'Two periods, CRRA utility with u′(x) = x^(−2) and δ = 0.81. What share of K goes to period 1? Four decimals.', '0.5263', 'Equal discounted marginal utility: x₁^(−2) = δ x₂^(−2).',
       ['x₁<sup>−2</sup> = δ x₂<sup>−2</sup> gives x₂ = √δ x₁ = 0.9 x₁.', 'x₁ + 0.9x₁ = K.', eq('x₁ = K/1.9, share 0.5263'), 'Stronger curvature than ln makes the plan smoother: ln would give 1/1.81 = 0.5525.'], check=1 / 1.9, tol=0.00005)

# ---------------------------------------------------------------- assignments
K.assign('pv', 'e', 'Present value of a stream',
         '<p>Write <code>present_value(payments, r)</code>. payments[0] arrives at the end of period 1, payments[1] at the end of period 2, and so on. Use δ = 1/(1 + r) and return the PV rounded to 2 decimals.</p>',
         '''
def present_value(payments, r):
    # your code here
    pass
''', [("present_value([200, 150, 300], 1/0.9 - 1)", 520.2), ("present_value([100, 100], 0)", 200.0), ("present_value([121], 0.1)", 110.0)],
         '''
def present_value(payments, r):
    d = 1 / (1 + r)
    return round(sum(x * d ** t for t, x in enumerate(payments, start=1)), 2)
''', 'Start the exponent at 1, since the first payment is one period away.', '<p>The first test is practice problem B. The third shows 121 next period is worth 110 today at 10%.</p>')
K.assign('plan', 'm', 'Optimal consumption plan',
         '<p>Write <code>ln_plan(K, d, T)</code> for u = ln x over T periods with discount factor d. The optimum gives period t (starting at 0) the share dᵗ ÷ (1 + d + … + d<sup>T−1</sup>). Return the list of amounts rounded to 3 decimals.</p>',
         '''
def ln_plan(K, d, T):
    # your code here
    pass
''', [("ln_plan(190, 0.9, 2)", [100.0, 90.0]), ("ln_plan(100, 0.9, 3)", [36.9, 33.21, 29.889]), ("ln_plan(30, 1, 3)", [10.0, 10.0, 10.0])],
         '''
def ln_plan(K, d, T):
    s = sum(d ** t for t in range(T))
    return [round(K * d ** t / s, 3) for t in range(T)]
''', 'Compute the sum of weights once, then scale.', '<p>With d = 1 the plan is flat: a perfectly patient agent spreads spending evenly.</p>')

K.must('Discount factor', 'δ = 1/(1 + r), 0 < δ < 1, patience not a choice. A after n periods is worth Aδⁿ. Practice B: PV = 520.2.')
K.must('Timing', 'Discount each piece by when it happens: R&D branch 10δ − 1, not (10 − 1)δ.')
K.must('ln consumption', '2 periods K/(1 + δ), δK/(1 + δ). 3 periods K, δK, δ²K over 1 + δ + δ². Equal discounted marginal utility.')
K.must('Corners', 'Linear u: (K, 0, 0). Convex u = x²: FOC finds the minimum, best is a corner. √x: x₁ = K/(1 + δ²), K = 181 gives 100, 81.')
K.must('Time consistency', 'Exponential: re-planning keeps x₂*, x₃*. Hyperbolic 1/(1 + kt) is time inconsistent.')

T = K.topic(
    slug='discounting-consumption', topic='discounting-consumption', step=(3, 'Decisions over time', 'aai-time', 'Plan several moves ahead: backward induction, discounting, consumption over time and the value of information.', 'College and masters'),
    title='Discounting and consumption over time', short='Discounting', badge='3.2', minutes=50,
    lead='Price future payments with a discount factor, split an income over two or three periods, and see when the best plan sits at a corner and why exponential plans never need revising.',
    desc='The bank interest derivation of δ, present value of streams, discounting inside the R&D tree, two and three period consumption with ln utility, the whiteboard derivation, diminishing marginal utility, linear and convex utility corners, time consistency, hyperbolic discounting, and practice problems B and D.',
    summary='Discount factors and present value, optimal consumption with ln and √x, corner solutions, and the time consistency of exponential discounting.',
    keywords=['discount factor', 'present value', 'consumption smoothing', 'time consistency', 'hyperbolic discounting', 'corner solution', 'first order conditions'],
    recap='<p>A payment n periods away is worth δⁿ of its face value. Concave utility spreads spending in the ratio 1 : δ : δ², while linear or convex utility puts it all in one period.</p>')
