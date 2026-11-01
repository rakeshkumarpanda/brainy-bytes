# Chapter 4.2: modelling games. Source: lecture 5 (Cournot duopoly: the airline story, price taking, inverse demand
# P = a - bq, the two case payoff, S_i = [0, inf), best response s_i = (a - c_i - b s_j)/(2b), symmetric (a - c)/(3b)
# with a = 100, c = 10 giving 30, price 40, profit 900, practice problem B (a = 40 gives 10, 20, 100), practice problem F
# with c1 = 12 and c2 = 18 giving 18 and 12) and lecture 6 (Bertrand: S_i = [0, a], the three case payoff, the
# numerical check with p2 = 40, the Bertrand paradox; the streetlamp public good with v_i = 3 x 1[sum >= 2] - s_i, the
# 8 profiles, free riding and the self enforcing profiles; the modelling recipe players, strategies, payoffs by cases).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('cournot', r'''
# Cournot: iterate best responses from any start and watch them meet at (a - c) / 3b
a, b, c1, c2 = 100, 1, 10, 10

def br(c, other):
    return max(0, (a - c - b * other) / (2 * b))

q1, q2 = 0.0, 0.0
for step in range(8):
    q1 = br(c1, q2)
    q2 = br(c2, q1)
    print(f"step {step}: q1 = {q1:7.3f}  q2 = {q2:7.3f}")
P = a - b * (q1 + q2)
print("price", round(P, 3), " profits", round((P - c1) * q1, 1), round((P - c2) * q2, 1))
''')

K.code('bertrand', r'''
# Bertrand payoff of firm 1 with the rival fixed at p2 = 40
a, b, c = 100, 1, 10

def v1(p1, p2):
    if p1 < p2:
        q = (a - p1) / b               # whole market
    elif p1 == p2:
        q = (a - p1) / (2 * b)         # split in half
    else:
        q = 0                          # nobody buys from the dearer firm
    return p1 * q - c * q

for p1 in (30, 39.9, 40, 50):
    print(f"p1 = {p1:5}: profit {v1(p1, 40):8.2f}")
''')

K.code('lamp', r'''
# Streetlamp: built if at least 2 of 3 contribute 1, worth 3 to everyone
from itertools import product

def v(i, s):
    return 3 * (sum(s) >= 2) - s[i]

for s in product((1, 0), repeat=3):
    pay = [v(i, s) for i in range(3)]
    stable = all(v(i, s) >= v(i, s[:i] + (1 - s[i],) + s[i + 1:]) for i in range(3))
    print(s, pay, "self enforcing" if stable else "")
''')

K.lesson('recipe', 'How to write any game down', f'''
<p>Lecture 6 opens with a recipe. Before you solve a game you must state it precisely, and almost every mistake in class came from skipping a step.</p>
{steps('The modelling recipe', [
    'Players: who makes a decision?',
    'Strategies: what exactly does each player choose, a quantity, a price, contribute or not? What is the smallest and largest allowed value?',
    'Payoffs: split into cases. In each case write what the player receives minus what it costs.',
    eq('Game = ⟨N, {{Sᵢ}}, {{vᵢ}}⟩')])}
<p>This chapter applies the recipe to three games used throughout the course: Cournot competition in quantities, Bertrand competition in prices, and the streetlamp public good.</p>
''', kw=['modelling', 'recipe', 'players', 'strategies', 'payoffs by cases'])

K.lesson('cournot', 'Cournot: competing in quantities', f'''
<p>Two airlines, say IndiGo and SpiceJet, decide how many seats to put on the same route. They do not name a price. The market sets the price from the total supply through the inverse demand function. A potato farmer is in the same position: he can grow as much as he likes, but he cannot also fix the price.</p>
{fxs(
    fx('Inverse demand', '<i>P</i>(<i>q</i>) = <i>a</i> − <i>bq</i> if this is ≥ 0, and 0 otherwise', 'q is the total quantity of both firms. a and b are common knowledge.'),
    fx('Cournot payoff', '<i>v</i><sub><i>i</i></sub>(<i>s</i><sub><i>i</i></sub>, <i>s</i><sub><i>j</i></sub>) = (<i>a</i> − <i>b</i>(<i>s</i><sub><i>i</i></sub> + <i>s</i><sub><i>j</i></sub>)) <i>s</i><sub><i>i</i></sub> − <i>C</i><sub><i>i</i></sub>(<i>s</i><sub><i>i</i></sub>), &nbsp; or −<i>C</i><sub><i>i</i></sub>(<i>s</i><sub><i>i</i></sub>) if the price would be negative', 'Strategy set Sᵢ = [0, ∞), so the game is infinite.', key=True),
    fx('Best response, linear cost cᵢ', '<i>s</i><sub><i>i</i></sub> = ' + frac('<i>a</i> − <i>c</i><sub><i>i</i></sub> − <i>b s</i><sub><i>j</i></sub>', '2<i>b</i>'), 'From ∂vᵢ/∂sᵢ = a − 2bsᵢ − bsⱼ − cᵢ = 0. Your best output falls by half of the rival\'s.', key=True),
    fx('Symmetric equilibrium', '<i>s</i>* = ' + frac('<i>a</i> − <i>c</i>', '3<i>b</i>'), 'Put sⱼ = s* in the best response: 3bs* = a − c.', key=True))}
{viz('cournot')}
{steps('Lecture numbers: a = 100, b = 1, c = 10', [
    'Each firm: s* = (100 − 10) ÷ 3 = 30.',
    'Total Q = 60, so the price is 100 − 60 = 40.',
    'Profit of each firm = (40 − 10) × 30.',
    eq('= 900 each')])}
{code('cournot')}
{steps('Practice problem F: different costs, a = 60, b = 1, c₁ = 12, c₂ = 18', [
    'Best responses: s₁ = (48 − s₂) ÷ 2 and s₂ = (42 − s₁) ÷ 2.',
    'Substitute: s₁ = 13.5 + s₁ ÷ 4, so s₁* = 18 and s₂* = 12.',
    'General formula: s₁* = (a − 2c₁ + c₂) ÷ 3b = 54 ÷ 3 = 18.',
    eq('Price 30, profits 18 × 18 = 324 and 12 × 12 = 144'),
    'The cheaper firm makes more and earns more. Constant costs do not mean equal costs.'])}
''', kw=['Cournot', 'quantity competition', 'inverse demand', 'best response function', 'reaction curve', 'practice problem F', 'duopoly'])

K.lesson('bertrand', 'Bertrand: competing in prices', f'''
<p>Now the firms choose prices and the market decides how much each sells. Buyers go only to the cheaper firm, and split evenly when prices are equal. In class, students first said the strategy was a quantity, then "0 to infinity", then "MRP". The professor corrected each in turn.</p>
{steps('Step 2 of the recipe: the strategy set', [
    'A firm chooses a price pᵢ, not a quantity.',
    'A price cannot be negative, so pᵢ ≥ 0.',
    'The highest price the market can produce is at q = 0, which gives p = a.',
    eq('Sᵢ = [0, a]'),
    'Prices above a sell nothing, exactly like a, so they add nothing. MRP, a legal price cap, plays no part in this model.'])}
{fxs(
    fx('Quantity from price', '<i>q</i> = ' + frac('<i>a</i> − <i>p</i>', '<i>b</i>'), 'Turn the demand rule around: p = a − bq gives bq = a − p.'),
    fx('Bertrand payoff', '<i>v</i><sub><i>i</i></sub> = <i>p</i><sub><i>i</i></sub> ' + frac('<i>a</i> − <i>p</i><sub><i>i</i></sub>', '<i>b</i>') + ' − <i>C</i><sub><i>i</i></sub>(' + frac('<i>a</i> − <i>p</i><sub><i>i</i></sub>', '<i>b</i>') + ') if cheaper, &nbsp; half the market (divide by 2<i>b</i>) if tied, &nbsp; −<i>C</i><sub><i>i</i></sub>(0) if dearer', 'Three cases. The −Cᵢ(0) term is a fixed cost paid even when nothing sells.', key=True))}
{table(['p₁ (with p₂ = 40)', 'Case', 'Quantity', 'Profit'], [
    ['30', 'cheaper', '70', '30 × 70 − 700 = 1,400'], ['39.9', 'cheaper', '60.1', '2,397.99 − 601 = 1,796.99'], ['40', 'tie', '30', '1,200 − 300 = 900'], ['50', 'dearer', '0', '0']])}
{viz('bertrand')}
{code('bertrand')}
<p>The payoff jumps. Just below 40 the firm earns about 1,800, exactly at 40 it earns 900, and just above it earns 0. Undercutting by one paisa roughly doubles profit. That is why price competition is so fierce.</p>
{note('The Bertrand paradox: with equal unit cost c, the only stable prices are p₁ = p₂ = c. Two firms are enough to drive profit to zero, while Cournot firms keep the price at 40, well above cost 10.', 'exam')}
''', kw=['Bertrand', 'price competition', 'strategy set', 'discontinuous payoff', 'undercutting', 'Bertrand paradox', 'MRP'])

K.lesson('lamp', 'The streetlamp: a public good', f'''
<p>Three neighbours each decide whether to pay 1 towards a streetlamp. It is built only if at least two pay, and once built it is worth 3 to everyone, including anyone who did not pay. There is no refund if it is not built.</p>
{fxs(fx('Streetlamp payoff', '<i>v</i><sub><i>i</i></sub>(<i>s</i>) = 3 · 1[ ∑<sub><i>j</i></sub> <i>s</i><sub><i>j</i></sub> ≥ 2 ] − <i>s</i><sub><i>i</i></sub>, &nbsp; <i>s</i><sub><i>i</i></sub> ∈ {{0, 1}}', 'The indicator 1[·] is 1 when the statement is true and 0 otherwise. Split on the sum, not on the eight profiles one by one.', key=True))}
{table(['Others who pay', 'You pay', 'You do not pay', 'Better for you'], [
    ['0', '−1 (not built)', '0', 'Do not pay'], ['1', '2 (you complete it)', '0', 'Pay, you are pivotal'], ['2', '2', '3 (free ride)', 'Do not pay']])}
{viz('lamp')}
{code('lamp')}
<p>Neither choice is always best, so the game has no dominant strategy. From (1, 1, 1) each neighbour gains by stopping alone, 3 against 2, so everyone paying is not self enforcing. The self enforcing profiles are the three with exactly two payers, and the unhappy (0, 0, 0), where a lone payer would just lose 1.</p>
{scene('all or nothing crowdfunding', '<p>A crowdfunding campaign that only charges backers if a target is reached is a threshold public good. Everyone wants the project, but each backer hopes others will cover the target. Open source maintenance and herd immunity from vaccination have the same structure: a good that nobody can be excluded from and that needs enough contributors.</p>')}
{deep('Comparing the three models', '<p>Cournot payoffs are smooth and concave in a firm\'s own quantity, so calculus finds the best response, and the price stays above cost. Bertrand payoffs jump at pᵢ = pⱼ, so there is no smooth maximum and price falls to cost. The streetlamp is finite, with two strategies each, and its interest lies in coordination and free riding rather than in calculus. Choosing the right strategy variable changes the prediction completely.</p>')}
{ladder(
    '<p>To study a game, first write down who plays, what each can choose, and what each gets in every case. Firms that choose amounts behave differently from firms that choose prices, and shared goods tempt people to let others pay.</p>',
    '<p>Cournot: sᵢ = (a − cᵢ − bsⱼ)/2b and s* = (a − c)/3b, so 30 each, price 40, profit 900. Bertrand: Sᵢ = [0, a] and a three case payoff, and price falls to cost. Streetlamp: vᵢ = 3·1[Σ ≥ 2] − sᵢ.</p>',
    '<p>With n Cournot firms s* = (a − c)/((n + 1)b), and the price tends to c as n grows, so Cournot converges to perfect competition. Bertrand with capacity limits (Edgeworth) or differentiated products restores positive margins.</p>',
    '<p>Learning agents in repeated pricing games can learn to keep prices above the Bertrand level without communicating (Calvano et al. 2020, algorithmic collusion), which is now a question for competition law. Mechanism design asks how to set rules so that public goods are funded despite free riding.</p>')}
''', kw=['streetlamp', 'public good', 'free rider', 'indicator function', 'threshold', 'pivotal', 'crowdfunding'])


K.lesson('levels', 'From intuition to research', f'''
<p>Writing a real situation as a game is a skill. Here it is practised on two tea stalls, with the numbers worked out and a modern twist with pricing algorithms.</p>
{scene('two tea stalls choosing how many cups to make', '<p>Two stalls sell tea on the same street. The more cups both make, the lower the price customers will pay. Each owner decides how many cups to prepare, knowing the other is doing the same. This is a Cournot game.</p>')}
{steps('Work it out: Cournot with P = 100 − q₁ − q₂ and cost 10 per cup', ['Profit of stall 1: (100 − q₁ − q₂ − 10) q₁. Best response q₁ = (90 − q₂) ÷ 2.', 'Symmetric equilibrium: q = (90 − q) ÷ 2, so q = 30 each, price 40.', 'Profit each: (40 − 10) × 30 = 900.', eq('A single owner would make 45 cups at price 55 for 2025, or 1012.5 each if shared, more than 900')])}
{deep('the analysis', '<p>Cournot competition gives more output and lower prices than a monopoly but less than perfect competition. Bertrand competition in prices with identical goods drives the price down to cost with just two firms, the Bertrand paradox, because undercutting by a tiny amount captures the whole market. The streetlamp shows the public good problem: each person’s contribution helps everyone, so each contributes too little.</p>')}
{deep('the research view', '<p>Calvano et al. (2020) showed that simple Q-learning pricing algorithms, playing a repeated Bertrand game, learn to keep prices above the competitive level without any communication. This has become a question for competition law as more prices are set by AI.</p>')}
{note('The Cournot equilibrium is not the joint best outcome for the firms. Each firm ignores that its extra output lowers the other’s price.', 'warn')}
''', kw=['Cournot', 'Bertrand paradox', 'public good', 'algorithmic collusion', 'best response'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In Cournot competition firms choose', ['Prices', 'Quantities', 'Advertising', 'Locations'], 1,
       'The market sets the price.', 'Each firm picks how much to supply and P = a − bq gives the price.')
K.quiz('e', 'In Bertrand competition the strategy set of each firm is', ['[0, ∞)', '[0, a]', '{0, 1}', 'The MRP'], 1,
       'Highest price is at q = 0.', 'Prices run from 0 to a, the price at which demand is zero.')
K.quiz('e', 'Cournot with a = 100, b = 1, c = 10 gives each firm', ['20', '30', '45', '90'], 1,
       '(a − c)/3b.', '90 ÷ 3 = 30.')
K.quiz('e', 'The streetlamp is built when', ['Anyone pays', 'At least 2 of the 3 pay', 'All 3 pay', 'Never'], 1,
       'The threshold.', 'Σ sⱼ ≥ 2.')
K.quiz('m', 'Cournot best response of firm i is', ['(a − c − bsⱼ)/(2b)', '(a − c)/(3b)', '(a − c)/b', 'a − bsⱼ'], 0,
       'Differentiate profit.', 'a − 2bsᵢ − bsⱼ − c = 0.')
K.quiz('m', 'In Bertrand, if p₁ = p₂ each firm sells', ['(a − p)/b', '(a − p)/(2b)', '0', 'a/b'], 1,
       'Split the market.', 'Half of total demand (a − p)/b.')
K.quiz('m', 'In the streetlamp game, when exactly one other neighbour pays, you should', ['Pay', 'Not pay', 'Either', 'Ask for a refund'], 0,
       'You are pivotal.', 'Paying gives 2, not paying gives 0.')
K.quiz('m', 'Why is (1, 1, 1) not self enforcing in the streetlamp game?', ['The lamp is not built', 'Each player gains 1 by stopping alone', 'It costs too much', 'It is Pareto dominated'], 1,
       'Free riding.', 'With the other two still paying, a quitter gets 3 instead of 2.')
K.quiz('h', 'The Bertrand paradox says that with equal unit cost c', ['Prices are (a + c)/2', 'Prices fall to c and profits to 0', 'One firm leaves', 'Prices equal a'], 1,
       'Undercutting.', 'Any price above c can be profitably undercut.')
K.quiz('h', 'Practice problem F (a = 60, c₁ = 12, c₂ = 18): firm 1 produces', ['12', '15', '18', '20'], 2,
       '(a − 2c₁ + c₂)/3b.', '(60 − 24 + 18)/3 = 18.')
K.quiz('x', 'With n identical Cournot firms, each produces', ['(a − c)/(nb)', '(a − c)/((n + 1)b)', '(a − c)/(2b)', '(a − c)/(3b)'], 1,
       'n = 2 gives 3b.', 'The symmetric solution of n best responses gives (a − c)/((n + 1)b).')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Cournot a = 100, b = 1, c = 10: what is the market price?', '40', 'Q = 60.',
       ['Each firm: 30.', 'Q = 60.', eq('P = 100 − 60 = 40')], check=40)
K.calc('e', 'Same game: what is each firm\'s profit?', '900', '(P − c) × q.',
       ['P − c = 30.', 'q = 30.', eq('profit = 900')], check=900)
K.calc('e', 'Practice problem B: a = 40, b = 1, c = 10. What does each firm produce?', '10', '(a − c)/3b.',
       ['a − c = 30.', '3b = 3.', eq('s* = 10')], check=10)
K.calc('m', 'Practice problem B: what is each firm\'s profit?', '100', 'Price 20.',
       ['Q = 20, so P = 40 − 20 = 20.', 'P − c = 10.', eq('profit = 10 × 10 = 100')], check=100)
K.calc('m', 'Cournot a = 100, b = 1, c = 10: what is firm 1\'s best response if firm 2 produces 50?', '20', 'Plug in.',
       ['sᵢ = (100 − 10 − 50) ÷ 2.', '= 40 ÷ 2.', eq('= 20')], check=20)
K.calc('m', 'Bertrand a = 100, b = 1, c = 10, p₂ = 40: what is firm 1\'s profit at p₁ = 35?', '1625', 'Cheaper, so the whole market.',
       ['q = 100 − 35 = 65.', 'Revenue 35 × 65 = 2,275, cost 650.', eq('profit = 1,625')], check=1625)
K.calc('m', 'Practice problem F: what is firm 2\'s profit?', '144', 'Price 30, s₂ = 12.',
       ['s₁ = 18, s₂ = 12, so Q = 30 and P = 30.', 'P − c₂ = 12.', eq('profit = 12 × 12 = 144')], check=144)
K.calc('h', 'Streetlamp: what is the total payoff of all three at (1, 1, 0)?', '7', 'Two payers, lamp built.',
       ['Payers get 3 − 1 = 2 each.', 'The free rider gets 3.', eq('2 + 2 + 3 = 7')], check=7)
K.calc('h', 'Cournot with 3 identical firms, a = 100, b = 1, c = 10: what is the price?', '32.5', 'Each makes (a − c)/4.',
       ['Each firm: 90 ÷ 4 = 22.5.', 'Q = 67.5.', eq('P = 100 − 67.5 = 32.5')], check=32.5)
K.calc('h', 'Cournot a = 100, b = 1, c = 10: a monopolist would produce (a − c)/2b. How much more total profit does the monopoly earn than the duopoly?', '225', 'Compare 2 × 900 with the monopoly profit.',
       ['Monopoly: q = 45, P = 55, profit 45 × 45 = 2,025.', 'Duopoly total: 2 × 900 = 1,800.', eq('2,025 − 1,800 = 225')], check=225)
K.calc('x', 'Asymmetric Cournot: a = 100, b = 1, c₁ = 10, c₂ = 20. What is s₁*? Two decimals.', '33.33', '(a − 2c₁ + c₂)/3b.',
       ['a − 2c₁ + c₂ = 100 − 20 + 20 = 100.', 'Divide by 3.', eq('s₁* = 33.33 and s₂* = (100 − 40 + 10)/3 = 23.33')], check=100 / 3, tol=0.005)

# ---------------------------------------------------------------- assignments
K.assign('cournot', 'm', 'Cournot equilibrium with different costs',
         '<p>Write <code>cournot(a, b, c1, c2)</code> that returns [s1, s2, price] at the Cournot equilibrium with linear costs, using s₁ = (a − 2c₁ + c₂)/3b and s₂ = (a − 2c₂ + c₁)/3b. Round each to 2 decimals.</p>',
         '''
def cournot(a, b, c1, c2):
    # your code here
    pass
''', [("cournot(100, 1, 10, 10)", [30.0, 30.0, 40.0]), ("cournot(60, 1, 12, 18)", [18.0, 12.0, 30.0]), ("cournot(40, 1, 10, 10)", [10.0, 10.0, 20.0])],
         '''
def cournot(a, b, c1, c2):
    s1 = (a - 2 * c1 + c2) / (3 * b)
    s2 = (a - 2 * c2 + c1) / (3 * b)
    return [round(s1, 2), round(s2, 2), round(a - b * (s1 + s2), 2)]
''', 'Compute both quantities, then the price from the inverse demand.', '<p>The tests are the lecture example and practice problems F and B.</p>')
K.assign('bertrand', 'e', 'Bertrand payoff',
         '<p>Write <code>bertrand(p1, p2, a, b, c)</code> that returns firm 1\'s profit with unit cost c and no fixed cost, using the three cases of the lecture. Round to 2 decimals.</p>',
         '''
def bertrand(p1, p2, a, b, c):
    # your code here
    pass
''', [("bertrand(30, 40, 100, 1, 10)", 1400.0), ("bertrand(40, 40, 100, 1, 10)", 900.0), ("bertrand(50, 40, 100, 1, 10)", 0.0), ("bertrand(39.9, 40, 100, 1, 10)", 1796.99)],
         '''
def bertrand(p1, p2, a, b, c):
    if p1 < p2:
        q = (a - p1) / b
    elif p1 == p2:
        q = (a - p1) / (2 * b)
    else:
        q = 0.0
    return round((p1 - c) * q, 2)
''', 'Find the quantity from the case, then profit = (p1 − c) × q.', '<p>These are the rows of the numerical check in the lecture notes.</p>')

K.must('Recipe', 'Players, strategies (with their range), payoffs split into cases. Game = ⟨N, Sᵢ, vᵢ⟩.')
K.must('Cournot', 'P = a − bq. sᵢ = (a − cᵢ − bsⱼ)/2b, s* = (a − c)/3b. a = 100, c = 10: 30 each, P = 40, profit 900.')
K.must('Asymmetric Cournot', 's₁* = (a − 2c₁ + c₂)/3b. Practice F: 18 and 12, P = 30, profits 324 and 144.')
K.must('Bertrand', 'Sᵢ = [0, a], q = (a − p)/b. Cheaper takes all, tie splits (divide by 2b), dearer gets −Cᵢ(0). Paradox: p = c.')
K.must('Streetlamp', 'vᵢ = 3·1[Σ ≥ 2] − sᵢ, 8 profiles. Pay only when pivotal. Stable: exactly two payers, or nobody.')

T = K.topic(
    slug='modelling-games', topic='modelling-games', step=(4, 'Games between rational agents', 'aai-games', 'Model interactions between several rational agents: normal form games, Cournot, Bertrand, public goods, solution concepts and Pareto optimality.', 'College and masters'),
    title='Modelling games: Cournot, Bertrand and the streetlamp', short='Modelling games', badge='4.2', minutes=50,
    lead='Turn three real stories into games: firms choosing quantities, firms choosing prices, and neighbours deciding whether to fund a streetlamp.',
    desc='The modelling recipe, Cournot competition with inverse demand, the two case payoff and best response function, the symmetric and asymmetric equilibria with practice problems B and F, Bertrand competition with its strategy set and three case payoff, the Bertrand paradox, and the streetlamp threshold public good.',
    summary='The modelling recipe, Cournot and Bertrand duopoly, and the streetlamp public good with free riding.',
    keywords=['Cournot', 'Bertrand', 'public good', 'streetlamp', 'best response function', 'duopoly', 'free rider'],
    recap='<p>Write every game as players, strategies and payoffs by cases. Cournot firms keep prices above cost, Bertrand firms drive them down to cost, and the streetlamp shows how free riding undermines shared goods.</p>')
