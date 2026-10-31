# Chapter 6.1: Quiz 1 of Advanced AI (CSL 7580), solved. Source: the quiz paper (submission date 13.09.2026, 40 points,
# four questions of 10 points). Every number below was checked in Python before it was written down.
# Q1 Cournot with p(q) = a/(q + 1), C(q) = cq, q_i > 0: symmetric NE solves a(q + 1) = c(2q + 1)^2, so
#    q* = ((a - 4c) + sqrt(a^2 + 8ac))/(8c), not (a - c)/3 (a = 10, c = 1 gives 2.4271 against 3), S1 false.
#    Monopoly with cost 2cQ: Q* = sqrt(a/(2c)) - 1 exists whenever a > 2c, so S2 is false in general. Answer B.
# Q2 bananas 0.50 (1.20, 0.60, 0.30), candy 0.25 (0.40, 0.20, 0.10), cash 1.25: buy 2 bananas and 1 candy, spends
#    exactly 1.25, net gain 0.95. Answer A.
# Q3 u = sqrt(w), w = 400, lottery 900 w.p. 0.4 or 10 w.p. 0.6, price p: buys iff 0.4 sqrt(1300 - p) + 0.6 sqrt(410 - p)
#    >= 20, true up to p* = 267.99. A and B both hold, C and D fail. The ambiguity is flagged.
# Q4 u = x^2, delta = 1/2, three periods: convex objective, corner (K, 0, 0) with payoff K^2.
from cvkit import Kit, fx, fxs, frac, sqrt, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('q1', r'''
# Quiz 1, question 1: symmetric Cournot equilibrium with p = a / (q + 1) and cost c q
import math
a, c = 10, 1
q = ((a - 4 * c) + math.sqrt(a * a + 8 * a * c)) / (8 * c)      # root of 4c q^2 + (4c - a) q + (c - a) = 0
print("equilibrium q per firm:", round(q, 4), "  claimed (a - c) / 3:", round((a - c) / 3, 4))
print("check a(q + 1) = c(2q + 1)^2:", round(a * (q + 1), 4), round(c * (2 * q + 1) ** 2, 4))
print("price:", round(a / (2 * q + 1), 4))

# a firm's best reply to q = 3 is not 3, so (3, 3) cannot be an equilibrium
profit = lambda qi, qj: a * qi / (qi + qj + 1) - c * qi
print("profit at 3 vs 2.5 when the rival plays 3:", round(profit(3, 3), 4), round(profit(2.5, 3), 4))

Q = math.sqrt(a / (2 * c)) - 1                                    # joint monopoly with cost 2cQ
print("monopoly quantity:", round(Q, 4), " exists because a > 2c:", a > 2 * c)
''')

K.code('q2', r'''
# Quiz 1, question 2: try every affordable basket
cash, pb, pc = 1.25, 0.50, 0.25
def value(first, n):                   # 1.20 + 0.60 + 0.30 ... halves each time
    return sum(first / 2 ** k for k in range(n))

best = None
for b in range(0, 4):
    for k in range(0, 6):
        cost = b * pb + k * pc
        if cost <= cash + 1e-9:
            net = value(1.20, b) + value(0.40, k) - cost
            if best is None or net > best[0] + 1e-9:
                best = (round(net, 2), b, k, cost)
print("best: net", best[0], "with", best[1], "bananas and", best[2], "candy, spending", best[3])
''')

K.code('q3', r'''
# Quiz 1, question 3: buy when expected utility after paying p beats keeping 400
import math
def gain(p):
    return 0.4 * math.sqrt(400 - p + 900) + 0.6 * math.sqrt(400 - p + 10) - math.sqrt(400)

lo, hi = 0, 410
for _ in range(60):                    # bisection for the break even price
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if gain(mid) > 0 else (lo, mid)
print("gain at p = 18:", round(gain(18), 3))
print("break even price p* =", round(lo, 2))
for p in (0, 18, 100, 268, 300):
    print("p =", p, "buy" if gain(p) > 0 else "do not buy")
''')

K.lesson('q1', 'Question 1: Cournot with a curved demand', f'''
<p><b>The question (10 points).</b> Market demand is p(q) = a/(q + 1) with a &gt; 0. Two firms each have cost C(q) = cq with c &gt; 0, and neither may choose qᵢ = 0. S1: if the firms choose quantities simultaneously to maximize profit, in the Nash equilibrium each firm produces (a − c)/3 and the price is a ÷ (2(a − c)/3 + 1). S2: if the firms collude as a monopoly with joint cost C*(q) = 2cq, no total quantity maximizes total profit. Options: A both true, B both false, C only S1 true, D only S2 true.</p>
{fxs(
    fx('Profit of firm i', 'π<sub><i>i</i></sub> = ' + frac('<i>a q</i><sub><i>i</i></sub>', '<i>q</i><sub><i>i</i></sub> + <i>q</i><sub><i>j</i></sub> + 1') + ' − <i>c q</i><sub><i>i</i></sub>', 'Price times own quantity, minus cost.'),
    fx('First order condition', frac('<i>a</i>(<i>q</i><sub><i>j</i></sub> + 1)', '(<i>q</i><sub><i>i</i></sub> + <i>q</i><sub><i>j</i></sub> + 1)²') + ' = <i>c</i>', 'The derivative of a qᵢ/(qᵢ + qⱼ + 1) is a(qⱼ + 1)/(Q + 1)².', key=True),
    fx('Symmetric equilibrium', '<i>q</i>* = ' + frac('(<i>a</i> − 4<i>c</i>) + ' + sqrt('<i>a</i>² + 8<i>ac</i>'), '8<i>c</i>'), 'From a(q + 1) = c(2q + 1)², a quadratic 4cq² + (4c − a)q + (c − a) = 0.', key=True),
    fx('Joint monopoly', '<i>Q</i>* = ' + sqrt(frac('<i>a</i>', '2<i>c</i>')) + ' − 1', 'From a/(Q + 1)² = 2c. Positive exactly when a &gt; 2c.', key=True))}
{steps('Statement S1', [
    'Set qᵢ = qⱼ = q in the first order condition: a(q + 1) = c(2q + 1)².',
    'Expand: 4cq² + (4c − a)q + (c − a) = 0. The positive root is q* = ((a − 4c) + √(a² + 8ac)) ÷ 8c.',
    'Try a = 10, c = 1: q* = (6 + √180) ÷ 8 = 2.4271, while (a − c)/3 = 3.',
    'Check directly: if the rival makes 3, producing 2.5 earns more than producing 3, so (3, 3) is not an equilibrium.',
    eq('S1 is false. The formula (a − c)/3b belongs to linear demand a − bq, not to a/(q + 1)')])}
{steps('Statement S2', [
    'Joint profit Π(Q) = aQ/(Q + 1) − 2cQ for Q &gt; 0.',
    'Π′(Q) = a/(Q + 1)² − 2c = 0 gives Q* = √(a/2c) − 1, and Π″ = −2a/(Q + 1)³ &lt; 0, so it is a maximum.',
    'Q* &gt; 0 whenever a &gt; 2c. With a = 10, c = 1, Q* = 1.236.',
    'Only when a ≤ 2c does profit fall from the start, so that no positive Q is best, since Q = 0 is ruled out.',
    eq('S2 claims no maximizer in general, which is false. Answer B: both statements are false')])}
{viz('q1cournot')}
{code('q1')}
{note('The trap in S1 is pattern matching. (a − c)/3 is the textbook Cournot answer, but it comes from demand a − bq. With a different demand curve you must redo the first order condition.', 'exam')}
''', kw=['Quiz 1', 'question 1', 'Cournot', 'nonlinear demand', 'first order condition', 'monopoly', 'answer B'])

K.lesson('q2', 'Question 2: bananas and candy', f'''
<p><b>The question (10 points).</b> A banana costs $0.50 and a candy $0.25. You have $1.25 and you value money. The first banana is worth $1.20 to you and each further one half the previous ($0.60, $0.30, …). The first candy is worth $0.40, then $0.20, $0.10, … The two values do not affect each other. Should you spend all your money? Options: A yes, B no, C not enough information.</p>
{fxs(fx('Buy one more unit when', 'marginal value ≥ price', 'Because you value money, a unit is worth buying only if it is worth more to you than what it costs.', key=True))}
{table(['Unit', 'Marginal value', 'Price', 'Worth buying?'], [
    ['Banana 1', '$1.20', '$0.50', 'Yes, +0.70'], ['Banana 2', '$0.60', '$0.50', 'Yes, +0.10'], ['Banana 3', '$0.30', '$0.50', 'No, −0.20'],
    ['Candy 1', '$0.40', '$0.25', 'Yes, +0.15'], ['Candy 2', '$0.20', '$0.25', 'No, −0.05']])}
{steps('Solve it', [
    'Every unit worth more than its price: two bananas and one candy.',
    'Cost: 2 × 0.50 + 0.25 = $1.25, exactly your cash.',
    'Value: 1.20 + 0.60 + 0.40 = $2.20.',
    eq('Net gain = 2.20 − 1.25 = $0.95, the best of all affordable baskets'),
    'The best basket uses all the money, so the answer is A: yes, spend it all.'])}
{viz('snacks')}
{code('q2')}
{note('The answer depends on the numbers, not on a rule like "always spend" or "never spend". With $3 you would still stop at $1.25, because the third banana and the second candy are worth less than they cost.', 'tip')}
''', kw=['Quiz 1', 'question 2', 'marginal value', 'budget', 'diminishing value', 'answer A'])

K.lesson('q3', 'Question 3: buying a lottery ticket', f'''
<p><b>The question (10 points).</b> A decision maker with u(w) = √w and wealth ₹400 is offered a lottery that pays ₹900 with probability 0.4 and ₹10 with probability 0.6, sold at ₹p. Options: A she will definitely buy if p &lt; 18, B she will definitely buy if p = 18, C she will definitely buy if p &gt; 18, D she will never buy.</p>
{fxs(
    fx('Buy when', '0.4 ' + sqrt('400 − <i>p</i> + 900') + ' + 0.6 ' + sqrt('400 − <i>p</i> + 10') + ' ≥ ' + sqrt('400') + ' = 20', 'Expected utility of final wealth after paying p and receiving the prize, against keeping ₹400.', key=True),
    fx('Break even price', '<i>p</i>* ≈ 267.99', 'Found by bisection. Below p* she buys, above it she does not.', key=True))}
{steps('Solve it', [
    'At p = 18: 0.4 × √1282 + 0.6 × √392 = 0.4 × 35.805 + 0.6 × 19.799 = 14.322 + 11.879 = 26.20.',
    '26.20 &gt; 20, so she buys at 18. The left side falls as p rises, so she buys at every p &lt; 18 too.',
    'The left side reaches 20 at about p* = 267.99. At p = 300 she refuses, so C fails, and D fails as well.',
    eq('A is true and B is true under this reading')])}
{viz('buylottery')}
{code('q3')}
{note('This question has two true options under the standard reading (prizes added to wealth after paying p). If only one option may be marked, A is the safer choice because it covers every price below 18, and B is a special case. It is worth asking the instructor whether the question allows more than one answer.', 'warn')}
{deep('Other readings and why they do not change the verdict', '<p>If wealth is ignored, the lottery alone has E[√X] = 0.4 × 30 + 0.6 × 3.162 = 13.90, a certainty equivalent of about ₹193, still far above 18. If she were risk neutral, the break even price would be the expected prize, 0.4 × 900 + 0.6 × 10 = ₹366. Under every sensible reading the price 18 is well below the break even price, so A and B hold and C and D fail.</p>')}
''', kw=['Quiz 1', 'question 3', 'lottery', 'square root utility', 'break even price', 'certainty equivalent', 'ambiguous question'])

K.lesson('q4', 'Question 4: consumption with a convex payoff', f'''
<p><b>The question (10 points).</b> A decision maker lives for 3 periods and splits ₹K among them. Each period\'s payoff is u(xₜ) = xₜ², discounted by δ = ½, so v(x₁, x₂, x₃) = x₁² + ½x₂² + ¼x₃² with 0 ≤ xₜ ≤ K and x₁ + x₂ + x₃ = K. Find the optimal plan.</p>
{fxs(
    fx('Objective', '<i>v</i> = <i>x</i>₁² + ½ <i>x</i>₂² + ¼ <i>x</i>₃²', 'A convex function on the triangle x₁ + x₂ + x₃ = K.'),
    fx('Answer', '(<i>x</i>₁, <i>x</i>₂, <i>x</i>₃) = (<i>K</i>, 0, 0), &nbsp; <i>v</i> = <i>K</i>²', 'Spend everything in period 1.', key=True))}
{steps('Solve it', [
    'u = x² has u″ = 2 &gt; 0, so v is convex. Setting the derivatives to zero finds a minimum, not a maximum.',
    'A convex function on a triangle is maximized at a corner: (K, 0, 0), (0, K, 0) or (0, 0, K).',
    'The corner values are K², ½K² and ¼K².',
    eq('Best: (K, 0, 0) with total payoff K²'),
    'Why not spread? Moving ε from period 1 to period 2 changes v by −2Kε + ε² + ½ε², which is negative for small ε.'])}
{viz('consume', T='3', u='sq', d=0.5, K=100)}
{steps('What the Lagrange method would have given', [
    'Interior first order conditions: 2x₁ = λ, x₂ = λ, ½x₃ = λ, so x₁ : x₂ : x₃ = 1 : 2 : 4.',
    'With K = 7 that is (1, 2, 4) and v = 1 + 2 + 4 = 7.',
    eq('The corner gives K² = 49. The stationary point is the minimum, as in lecture 4\'s x² example')])}
{ladder(
    '<p>Read the question carefully, do not trust a formula you remember from a different setting, and check the answer with numbers.</p>',
    '<p>Q1: redo the first order conditions for the new demand. Q2: buy while marginal value ≥ price. Q3: compare expected utility of final wealth with the sure wealth. Q4: convex payoffs go to a corner.</p>',
    '<p>Each question tests the second order condition in disguise: concavity guarantees that first order conditions find a maximum, and its failure (Q4) or the boundary (Q1, S2 with a ≤ 2c) changes the answer.</p>',
    '<p>Existence of Cournot equilibria with general demand needs conditions such as decreasing marginal revenue (Novshek 1985). Convex intertemporal objectives appear in models of lumpy consumption and in risk seeking reinforcement learning, where policies collapse to extreme actions.</p>')}
''', kw=['Quiz 1', 'question 4', 'convex', 'corner solution', 'consumption', 'Lagrange', 'answer K squared'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Quiz 1 Q1: the correct option is', ['A', 'B', 'C', 'D'], 1,
       'Check each statement.', 'S1 is false (q* = 2.427 for a = 10, c = 1, not 3) and S2 is false whenever a > 2c.')
K.quiz('e', 'Quiz 1 Q2: should you spend all $1.25?', ['Yes', 'No', 'Not enough information'], 0,
       'Two bananas and one candy.', 'That basket costs exactly 1.25 and gives the largest net gain, 0.95.')
K.quiz('e', 'Quiz 1 Q4: the optimal plan is', ['(K/3, K/3, K/3)', '(K, 0, 0)', '(0, 0, K)', '(K/7, 2K/7, 4K/7)'], 1,
       'Convex objective.', 'A convex payoff is maximized at a corner, and period 1 has the largest weight.')
K.quiz('m', 'Quiz 1 Q3: at p = 18, the expected utility of buying is about', ['13.9', '20', '26.2', '30'], 2,
       '0.4√1282 + 0.6√392.', '14.32 + 11.88 = 26.20 > 20, so she buys.')
K.quiz('m', 'Quiz 1 Q3: the break even price is about', ['18', '193', '268', '366'], 2,
       'Solve the buy condition with equality.', 'Bisection gives p* = 267.99.')
K.quiz('m', 'Why is (a − c)/3 wrong in Quiz 1 Q1?', ['It is right', 'It comes from linear demand a − bq, not from a/(q + 1)', 'Costs are quadratic', 'There are three firms'], 1,
       'Where does the formula come from?', 'The first order condition depends on the demand curve, so the answer changes with it.')
K.quiz('m', 'Quiz 1 Q2: why not buy a third banana with spare money?', ['It costs too much in total', 'Its value 0.30 is below its price 0.50', 'Bananas run out', 'Candy is better'], 1,
       'Marginal value against price.', 'Keeping the money is worth more than the third banana.')
K.quiz('h', 'Quiz 1 Q1, S2 is true only when', ['a > 2c', 'a ≤ 2c', 'a = c', 'Never'], 1,
       'When is √(a/2c) − 1 positive?', 'If a ≤ 2c joint profit falls on Q > 0, and Q = 0 is not allowed, so no maximizer exists.')
K.quiz('h', 'Quiz 1 Q4: setting the derivatives to zero finds', ['The maximum', 'The minimum on the budget line', 'A saddle', 'Nothing'], 1,
       'Convex objective.', 'The stationary point x₁ : x₂ : x₃ = 1 : 2 : 4 is the worst plan on the line.')
K.quiz('x', 'Quiz 1 Q3: which options hold under the standard reading?', ['Only A', 'Only B', 'A and B', 'C and D'], 2,
       'p = 18 is far below 268.', 'She buys at every price up to about 268, so both A and B are true.')

# ---------------------------------------------------------------- worked problems
K.calc('m', 'Quiz 1 Q1: with a = 10 and c = 1, what is the equilibrium quantity of each firm? Four decimals.', '2.4271', 'q* = ((a − 4c) + √(a² + 8ac)) ÷ 8c.',
       ['a − 4c = 6.', '√(100 + 80) = √180 = 13.4164.', eq('q* = 19.4164 ÷ 8 = 2.4271')], check=((10 - 4) + 180 ** 0.5) / 8, tol=0.00005)
K.calc('m', 'Quiz 1 Q1: with a = 10 and c = 1, what is the equilibrium price? Four decimals.', '1.7082', 'p = a ÷ (2q* + 1).',
       ['2q* + 1 = 5.8541.', 'p = 10 ÷ 5.8541.', eq('p = 1.7082')], check=10 / (2 * ((6 + 180 ** 0.5) / 8) + 1), tol=0.00005)
K.calc('m', 'Quiz 1 Q1: with a = 10 and c = 1, what joint quantity maximizes the colluding firms\' profit? Four decimals.', '1.2361', '√(a/2c) − 1.',
       ['a/2c = 5.', '√5 = 2.2361.', eq('Q* = 1.2361')], check=5 ** 0.5 - 1, tol=0.00005)
K.calc('e', 'Quiz 1 Q2: what is the net gain of the best basket?', '0.95', 'Value minus cost.',
       ['Two bananas and one candy: value 1.20 + 0.60 + 0.40 = 2.20.', 'Cost 1.25.', eq('net = 0.95')], check=0.95)
K.calc('e', 'Quiz 1 Q2: what is the net gain of buying only two bananas?', '0.8', 'Value 1.80, cost 1.00.',
       ['Value 1.20 + 0.60 = 1.80.', 'Cost 1.00.', eq('net = 0.80 &lt; 0.95')], check=0.8)
K.calc('m', 'Quiz 1 Q3: what is 0.4√1282 + 0.6√392? Two decimals.', '26.2', 'Wealth after paying 18 and winning or losing.',
       ['√1282 = 35.805, times 0.4 = 14.322.', '√392 = 19.799, times 0.6 = 11.879.', eq('sum = 26.20 &gt; 20')], check=0.4 * 1282 ** 0.5 + 0.6 * 392 ** 0.5, tol=0.005)
K.calc('h', 'Quiz 1 Q3: what is the break even price p*? Two decimals.', '267.99', 'Solve 0.4√(1300 − p) + 0.6√(410 − p) = 20.',
       ['The left side falls as p rises.', 'At p = 260 it is 20.17, at p = 270 it is 19.95.', 'Bisection narrows it down.', eq('p* = 267.99')], check=267.99133448222767, tol=0.005)
K.calc('h', 'Quiz 1 Q3: what would the break even price be for a risk neutral buyer?', '366', 'Expected prize.',
       ['With u(w) = w, buy when 400 − p + E[prize] ≥ 400.', 'E[prize] = 0.4 × 900 + 0.6 × 10 = 366.', eq('p* = 366, higher than 268 because there is no risk discount')], check=366)
K.calc('e', 'Quiz 1 Q4: with K = 10, what is the optimal total payoff?', '100', 'Plan (K, 0, 0).',
       ['All in period 1: x₁ = 10.', 'v = 10² + 0 + 0.', eq('v = 100')], check=100)
K.calc('h', 'Quiz 1 Q4: with K = 7, what is the payoff of the stationary point x₁ : x₂ : x₃ = 1 : 2 : 4?', '7', 'Plan (1, 2, 4).',
       ['x₁² = 1.', '½ × 2² = 2 and ¼ × 4² = 4.', eq('v = 7, far below K² = 49')], check=7)

T = K.topic(
    slug='quiz1-solved', topic='quiz1-solved', kind='revision',
    step=(6, 'Quiz and exam revision', 'aai-review', 'Check yourself with Quiz 1 fully solved, then revise the whole subject by exam style from school level to IIT, MIT and Cambridge.', 'All levels'),
    title='Quiz 1 solved: all four questions', short='Quiz 1 solved', badge='6.1', minutes=45,
    lead='Every question of Advanced AI Quiz 1 with the full working, an animation to test each answer, and the traps that cost marks.',
    desc='Question 1 on Cournot with demand a/(q + 1) and collusion, question 2 on bananas and candy, question 3 on buying a lottery with square root utility, and question 4 on consumption with a convex payoff, each with steps, code and a note on the trap.',
    summary='Worked answers to Quiz 1: B, A, A and B under the standard reading, and (K, 0, 0).',
    keywords=['Quiz 1', 'solutions', 'Cournot', 'lottery', 'consumption', 'marginal value', 'CSL 7580'],
    recap='')
