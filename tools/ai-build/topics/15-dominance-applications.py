# Chapter 5.3: dominance at work. Source: lecture 6 (section 9, IESDS in the Cournot duopoly with the halving intervals
# [0, 45], [22.5, 45], [22.5, 33.75] and the limit 30; practice problems E1 with a = 130 giving 40, E2 the second price
# auction, E3 the first price auction, E4 below cost Bertrand prices only weakly dominated, E5 asymmetric Cournot,
# D5 the Hotelling location game, D6 discrete Bertrand, F1 the streetlamp with refunds, F2 guess two thirds of the
# average) and the voting side topic.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('halving', r'''
# IESDS in the Cournot duopoly: the surviving interval [lo, hi] shrinks towards (a - c) / 3b
a, b, c = 100, 1, 10

def br(q):
    return max(0.0, (a - c - b * q) / (2 * b))

lo, hi = 0.0, float("inf")
hi = br(0)                                  # round 1: nothing above the monopoly quantity
print("round 1:", [lo, hi])
for k in range(2, 9):
    if k % 2 == 0:
        lo = br(hi)                         # too small is now dominated
    else:
        hi = br(lo)                         # too large is now dominated
    print(f"round {k}:", [round(lo, 4), round(hi, 4)])
print("limit (a - c) / 3b =", (a - c) / (3 * b))
''')

K.code('vickrey', r'''
# Second price auction: bidding your value v never does worse than any other bid
v = 60
bids = [40, 60, 80]
rivals = [30, 50, 70, 90]
for B in rivals:                            # highest rival bid
    row = []
    for b in bids:
        pay = v - B if b > B else 0         # win and pay the second price, or lose
        row.append(pay)
    print(f"rival bid {B}: payoff when bidding 40, 60, 80 -> {row}")
''')

K.lesson('cournot', 'IESDS solves the Cournot duopoly', f'''
<p>Cournot firms have no dominant quantity. Yet some quantities are strictly dominated, and IESDS solves the whole game. This was the professor\'s homework at the end of lecture 6.</p>
{fxs(
    fx('Profit with the rival fixed', 'π<sub><i>i</i></sub> = (<i>a</i> − <i>c</i> − <i>bq</i><sub><i>j</i></sub>) <i>q</i><sub><i>i</i></sub> − <i>b q</i><sub><i>i</i></sub>²', 'An upside down parabola in qᵢ, with its peak at the best response.'),
    fx('Best response', 'BR<sub><i>i</i></sub>(<i>q</i><sub><i>j</i></sub>) = max{{ 0, ' + frac('<i>a</i> − <i>c</i> − <i>bq</i><sub><i>j</i></sub>', '2<i>b</i>') + ' }}', 'With a = 100, b = 1, c = 10 this is max{0, (90 − qⱼ)/2}.', key=True),
    fx('Without calculus', '<i>Kq</i> − <i>bq</i>² = −<i>b</i>(<i>q</i> − ' + frac('<i>K</i>', '2<i>b</i>') + ')² + ' + frac('<i>K</i>²', '4<i>b</i>'), 'Completing the square shows the peak at q = K/2b, where K = a − c − bqⱼ.'))}
{steps('The rounds of elimination', [
    'Round 1: the peak is largest when the rival makes 0, at the monopoly quantity 45. Any q above 45 is beaten by 45 whatever the rival does. Survivors [0, 45].',
    'Round 2: the rival makes at most 45, so every peak is at least BR(45) = 22.5. Any q below 22.5 is beaten by 22.5. Survivors [22.5, 45].',
    'Round 3: the rival makes at least 22.5, so every peak is at most BR(22.5) = 33.75. Survivors [22.5, 33.75].',
    'Round 4: BR(33.75) = 28.125. Survivors [28.125, 33.75]. The width halves each round.',
    eq('Limit q* = (a − c)/3b = 30, the only survivor')])}
{viz('cournotiesds')}
{code('halving')}
{steps('Practice E1: p = 130 − Q and c = 10', [
    'BR(q) = (120 − q)/2. Round 1: [0, 60].',
    'Round 2: BR(60) = 30, so [30, 60]. Round 3: BR(30) = 45, so [30, 45].',
    'Round 4: BR(45) = 37.5. Round 5: BR(37.5) = 41.25.',
    eq('Limit 120/3 = 40, price 130 − 80 = 50, profit 40 × 40 = 1,600 each')])}
''', kw=['Cournot IESDS', 'halving interval', 'monopoly quantity', 'best response', 'completing the square', 'practice E1'])

K.lesson('auctions', 'Auctions: when truth telling is dominant', f'''
<p>In a sealed bid auction each bidder privately values the object at v and submits a bid b. Let B be the highest rival bid.</p>
{fxs(
    fx('Second price (Vickrey)', 'payoff = <i>v</i> − <i>B</i> if <i>b</i> &gt; <i>B</i>, otherwise 0', 'The winner pays the second highest bid. Bidding b = v weakly dominates every other bid.', key=True),
    fx('First price', 'payoff = <i>v</i> − <i>b</i> if <i>b</i> &gt; <i>B</i>, otherwise 0', 'The winner pays her own bid. Overbidding is weakly dominated, but bidding v is not dominant.', key=True))}
{table(['Second price, value v', 'Rival bid B below v', 'B between v and the overbid', 'B above both'], [
    ['Bid v', 'win, v − B', 'lose, 0', 'lose, 0'],
    ['Overbid b &gt; v', 'win, v − B (same)', 'win, v − B &lt; 0 (worse)', 'lose, 0']])}
{steps('Why underbidding is never better in a second price auction', [
    'If B is below the low bid, both bids win and pay B: same payoff.',
    'If B is between the low bid and v, the truthful bid wins v − B &gt; 0 while the low bid loses.',
    'If B is above v, both lose.',
    eq('Never worse, sometimes strictly better: b = v is weakly dominant')])}
{viz('auction')}
{code('vickrey')}
<p>In a first price auction, winning with b = v gives v − v = 0. Shading the bid below v can win with a positive surplus, so truthful bidding is not dominant and bidders shade. No dominant strategy exists there, which is why first price auctions need the Nash equilibrium analysis later in the course.</p>
{scene('online ad auctions', '<p>Search engines sell ad slots in automated auctions millions of times a day. Early systems used a first price rule and bidders kept adjusting their bids against each other. The move to second price style rules was meant to make simple truthful bidding safe. Display advertising later moved back to first price with automated bid shading, which shows the trade offs are still debated.</p>')}
''', kw=['auction', 'second price', 'Vickrey', 'first price', 'truthful bidding', 'weakly dominant', 'bid shading'])

K.lesson('more', 'Voting, prices and puzzles', f'''
<h3>Practice D5: where should a candidate stand?</h3>
<p>Two candidates choose a position 1 to 5 on a line. One voter sits at each position and votes for the nearer candidate, splitting ties. The payoff is the number of votes.</p>
{steps('IESDS in the location game', [
    'Round 1: position 2 beats 1 against every rival position (4 &gt; 2.5, 2.5 &gt; 1, 2 &gt; 1.5, 2.5 &gt; 2, 3 &gt; 2.5). By symmetry 4 beats 5. Delete 1 and 5.',
    'Round 2: against rivals in {{2, 3, 4}}, position 3 earns (3, 2.5, 3), beating both 2 and 4, which earn (2.5, 2, 2.5).',
    eq('Both candidates stand at 3, the median voter')])}
{viz('iesds', pre='hotel', mode='all')}
<h3>Practice D6: Bertrand with whole number prices</h3>
{steps('Prices 1 to 5, unit cost 1, 10 buyers', [
    'Against a rival price of 1 every price earns 0, so no price beats another strictly in every column. Strict IESDS deletes nothing.',
    'Weak elimination: 2 weakly beats 1 and 4 weakly beats 5. Then 3 beats 4, then 2 beats 3.',
    eq('Weak IESDS ends at (2, 2), one step above cost'),
    'But (1, 1), (2, 2) and (3, 3) are all self enforcing. Weak elimination threw two of them away.'])}
{viz('iesds', pre='dbert', mode='weak', order='first')}
<h3>Practice E4: below cost Bertrand prices</h3>
<p>Pricing at cost c always earns 0. Pricing below cost earns a loss when you are cheapest or tied, and 0 when the rival is cheaper still. So pᵢ = c weakly but not strictly dominates pᵢ &lt; c, and strict IESDS cannot start. The Bertrand prediction needs Nash equilibrium.</p>
<h3>Puzzles F1 and F2</h3>
{table(['Puzzle', 'Answer'], [
    ['F1. Streetlamp with refunds when the lamp is not built', 'Contributing ties with not contributing when nobody else pays, wins with one other payer, and loses with two. Still no dominance. Refunds remove the risk but not the free riding.'],
    ['F2. Two players guess an integer in [0, 100]. Closer to two thirds of the average wins', 'The lower guess always wins, so 0 weakly dominates every other guess, but not strictly: if the rival guesses above you, both 0 and your guess win.']])}
{viz('lamp', refund=True)}
{deep('Mechanism design in one line', '<p>The Vickrey auction and the subsidy in the Marketing War (chapter 5.2) share an idea: instead of predicting play in a given game, change the rules so that the outcome you want becomes dominant. That reverse question, choosing a game to get a desired equilibrium, is mechanism design, and the Gibbard Satterthwaite theorem marks where it runs out for voting.</p>')}
{ladder(
    '<p>Even when no single choice is always best, some choices are always bad. Removing them again and again can lead to one clear answer, as with two shops on a street both moving to the middle.</p>',
    '<p>Cournot IESDS halves the surviving interval each round to (a − c)/3b. In a second price auction bidding your value is weakly dominant. The location game ends at the median. Weak elimination can delete self enforcing outcomes, as in discrete Bertrand.</p>',
    '<p>For Cournot with more than two firms, IESDS no longer pins down a single quantity, while the Nash equilibrium is still unique. The revenue equivalence theorem shows first and second price auctions give the same expected revenue with independent private values.</p>',
    '<p>Generalized second price auctions for search ads are not truthful, which led to work on their equilibria (Edelman, Ostrovsky and Schwarz 2007, Varian 2007). Learning agents bidding repeatedly in first price auctions are now studied as online learning problems with regret guarantees.</p>')}
''', kw=['Hotelling', 'median voter', 'location game', 'discrete Bertrand', 'below cost prices', 'streetlamp refunds', 'guess two thirds', 'mechanism design'])


K.lesson('levels', 'From intuition to research', f'''
<p>Dominance shows up wherever rules can be designed. The second price auction is the cleanest case, and it is worth checking by hand.</p>
{scene('a sealed bid auction for a used bicycle', '<p>Each bidder writes a bid in an envelope. The highest bidder wins but pays the second highest bid. Your value for the bicycle is 70. Should you write 70, or try to be clever?</p>')}
{steps('Work it out: why bidding your value is safe', ['Others’ highest bid 60: bid 70, win and pay 60, gain 10. Bidding 50 loses, gain 0.', 'Others’ highest bid 80: bid 70, lose, gain 0. Bidding 90 wins but pays 80, gain −10.', 'Your bid only decides whether you win, never the price you pay.', eq('Bidding your true value is weakly dominant')])}
{deep('the analysis', '<p>Proof sketch: let b be the highest other bid. If b < v, any bid above b wins and pays b, and bidding v does so. If b > v, winning means paying more than v, and bidding v avoids it. If b = v you get 0 either way. In no case does another bid do strictly better, and in some cases it does strictly worse.</p>')}
{deep('the research view', '<p>Search engines first ran generalised second price auctions for ad slots, which are not truthful, and much research compares them with the truthful VCG auction. Revenue equivalence says that under standard assumptions first price, second price and many other auctions earn the same expected revenue.</p>')}
{note('In a second price auction you do not pay your own bid. Students who forget this conclude that shading the bid is wise.', 'warn')}
''', kw=['second price auction', 'truthful bidding', 'Vickrey', 'ad auctions', 'revenue equivalence'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In the Cournot duopoly with a = 100, b = 1, c = 10, what survives round 1 of IESDS?', ['[0, 30]', '[0, 45]', '[22.5, 45]', '{30}'], 1,
       'Monopoly quantity.', 'Anything above BR(0) = 45 is dominated by 45.')
K.quiz('e', 'In a second price auction the winner pays', ['Her own bid', 'The second highest bid', 'Her value', 'Nothing'], 1,
       'Vickrey.', 'The winner pays the highest losing bid.')
K.quiz('e', 'In the location game with voters at 1 to 5, IESDS sends both candidates to', ['1', '2', '3', '5'], 2,
       'The median.', 'Positions 1 and 5 go first, then 2 and 4.')
K.quiz('e', 'In a first price auction, bidding exactly your value', ['Is dominant', 'Always gives payoff 0 when you win', 'Is dominated by overbidding', 'Guarantees a win'], 1,
       'v − v.', 'Winning at your value leaves no surplus, so shading can do better.')
K.quiz('m', 'Each round of Cournot IESDS', ['Doubles the interval', 'Halves the width of the surviving interval', 'Removes one point', 'Does nothing'], 1,
       'BR has slope −½.', 'The best response shrinks distances by a factor of 2.')
K.quiz('m', 'Why is bidding v weakly but not strictly dominant in a second price auction?', ['It is strictly dominant', 'Against some rival bids, other bids give the same payoff', 'It is dominated', 'Because of ties only'], 1,
       'Look at B below both bids.', 'When the rival bid is low, both bids win and pay B, a tie.')
K.quiz('m', 'Practice E1 (p = 130 − Q, c = 10) gives each firm', ['30', '40', '45', '60'], 1,
       '(a − c)/3b.', '120 ÷ 3 = 40.')
K.quiz('m', 'In discrete Bertrand, strict IESDS', ['Ends at (1, 1)', 'Ends at (2, 2)', 'Deletes nothing', 'Ends at (5, 5)'], 2,
       'Against a rival price of 1 everything ties.', 'Every price earns 0 against a price of 1, so no strict domination.')
K.quiz('h', 'Weak IESDS in discrete Bertrand ends at (2, 2). Which self enforcing profiles did it delete?', ['None', '(1, 1) and (3, 3)', '(4, 4)', '(5, 5)'], 1,
       'Weak elimination can remove equilibria.', 'At (1, 1) and (3, 3) no firm gains by deviating alone.')
K.quiz('h', 'Below cost prices in Bertrand are', ['Strictly dominated by c', 'Weakly but not strictly dominated by c', 'Dominant', 'Not dominated'], 1,
       'When the rival is cheaper.', 'If the rival is cheaper, both pᵢ < c and c earn 0, a tie.')
K.quiz('x', 'With refunds in the streetlamp game, contributing is', ['Strictly dominant', 'Weakly dominant', 'Not dominant either way', 'Strictly dominated'], 2,
       'Two other payers.', 'With two others paying, not paying gives 3 against 2, so free riding remains.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Cournot a = 100, b = 1, c = 10: what is BR(45)?', '22.5', '(90 − q)/2.',
       ['90 − 45 = 45.', 'Divide by 2.', eq('BR(45) = 22.5')], check=22.5)
K.calc('e', 'Same game: what is BR(22.5)?', '33.75', '(90 − 22.5)/2.',
       ['90 − 22.5 = 67.5.', 'Divide by 2.', eq('BR(22.5) = 33.75')], check=33.75)
K.calc('e', 'Second price auction, v = 60, rival bid 50. What is your payoff if you bid 60?', '10', 'You win and pay 50.',
       ['60 &gt; 50, so you win.', 'You pay the second price, 50.', eq('payoff = 60 − 50 = 10')], check=10)
K.calc('m', 'Second price auction, v = 60, rival bid 70. What is your payoff if you overbid 80?', '-10', 'You win and pay 70.',
       ['80 &gt; 70, so you win.', 'You pay 70 for an object worth 60.', eq('payoff = 60 − 70 = −10, while bidding 60 gives 0')], check=-10)
K.calc('m', 'First price auction, v = 60, rival bid 40. What is your payoff if you bid 50?', '10', 'You pay your own bid.',
       ['50 &gt; 40, so you win.', 'You pay 50.', eq('payoff = 60 − 50 = 10, better than 0 from bidding 60')], check=10)
K.calc('m', 'Practice E1: what is the market price at the limit?', '50', 'Each firm makes 40.',
       ['Q = 80.', 'P = 130 − 80.', eq('P = 50')], check=50)
K.calc('m', 'Cournot a = 100, c = 10: after round 4 the interval is [28.125, 33.75]. What is its width?', '5.625', 'Subtract.',
       ['33.75 − 28.125.', 'Round 1 width was 45.', eq('width = 5.625 = 45 ÷ 8')], check=5.625)
K.calc('h', 'Practice E5: p = 100 − Q, c₁ = 10, c₂ = 20. What is the market price at the IESDS limit? Two decimals.', '43.33', 'q₁ = 100/3, q₂ = 70/3.',
       ['q₁ = (90 − q₂)/2 and q₂ = (80 − q₁)/2 meet at q₁ = 33.33, q₂ = 23.33.', 'Q = 170/3 = 56.67.', eq('P = 100 − 56.67 = 43.33')], check=100 - 170 / 3, tol=0.005)
K.calc('h', 'Location game: what does position 3 earn against a rival at 2?', '3', 'Voters at 3, 4, 5 are nearer to 3.',
       ['Voter 1 and voter 2 are nearer to 2.', 'Voters 3, 4 and 5 are nearer to 3.', eq('3 votes')], check=3)
K.calc('h', 'Discrete Bertrand (prices 1 to 5, cost 1, 10 buyers): what does a firm earn at (3, 3)?', '10', 'Tie, half the market.',
       ['Tie, so 5 buyers each.', 'Margin 3 − 1 = 2.', eq('5 × 2 = 10')], check=10)
K.calc('x', 'Cournot IESDS with a = 100, b = 1, c = 10: how many rounds until the interval width is below 1?', '7', 'Width 45 / 2^(k−1).',
       ['After round k the width is 45 ÷ 2<sup>k−1</sup>.', 'Round 6: 45 ÷ 32 = 1.41. Round 7: 45 ÷ 64 = 0.70.', eq('7 rounds')], check=7)

# ---------------------------------------------------------------- assignments
K.assign('interval', 'm', 'Cournot elimination intervals',
         '<p>Write <code>cournot_rounds(a, b, c, k)</code> that returns the surviving interval [lo, hi] after k rounds, starting from [0, BR(0)] after round 1, then alternately raising lo to BR(hi) and lowering hi to BR(lo). Round each end to 4 decimals.</p>',
         '''
def cournot_rounds(a, b, c, k):
    # your code here
    pass
''', [("cournot_rounds(100, 1, 10, 1)", [0.0, 45.0]), ("cournot_rounds(100, 1, 10, 3)", [22.5, 33.75]), ("cournot_rounds(130, 1, 10, 5)", [37.5, 41.25])],
         '''
def cournot_rounds(a, b, c, k):
    br = lambda q: max(0.0, (a - c - b * q) / (2 * b))
    lo, hi = 0.0, br(0)
    for r in range(2, k + 1):
        if r % 2 == 0:
            lo = br(hi)
        else:
            hi = br(lo)
    return [round(lo, 4), round(hi, 4)]
''', 'Even rounds move the lower end, odd rounds the upper end.', '<p>The last test is practice E1 after five rounds.</p>')
K.assign('auction', 'e', 'Auction payoffs',
         '<p>Write <code>auction_payoff(kind, v, b, B)</code>. kind is "first" or "second", v the value, b your bid and B the highest rival bid. You win only if b &gt; B. Return your payoff.</p>',
         '''
def auction_payoff(kind, v, b, B):
    # your code here
    pass
''', [("auction_payoff('second', 60, 60, 50)", 10), ("auction_payoff('second', 60, 80, 70)", -10), ("auction_payoff('first', 60, 50, 40)", 10), ("auction_payoff('first', 60, 30, 40)", 0)],
         '''
def auction_payoff(kind, v, b, B):
    if b <= B:
        return 0
    return v - B if kind == "second" else v - b
''', 'Losing pays 0. The winner pays B in a second price auction and b in a first price auction.', '<p>The second test is the overbidding trap: winning at a price above your value.</p>')

K.must('Cournot IESDS', 'BR = max{0, (a − c − bq)/2b}. Rounds: [0, 45], [22.5, 45], [22.5, 33.75], … halving to (a − c)/3b = 30. E1: 40, price 50, profit 1,600.')
K.must('Second price auction', 'Payoff v − B if b > B. Bidding v weakly dominates every bid (never worse, sometimes better). Strategy proof.')
K.must('First price auction', 'Payoff v − b if you win. Overbidding weakly dominated, but bidding v not dominant: bidders shade.')
K.must('Location and prices', 'Hotelling 1 to 5: delete 1, 5 then 2, 4, both at 3 (median). Discrete Bertrand: strict deletes nothing, weak ends at (2, 2) losing (1, 1), (3, 3).')
K.must('Weak only', 'Below cost Bertrand prices and the guess game: weakly but not strictly dominated, so strict IESDS cannot start.')

T = K.topic(
    slug='dominance-applications', topic='dominance-applications', step=(5, 'Dominance and iterated elimination', 'aai-dom', 'Predict play without guessing: dominance, the dominant strategy equilibrium, iterated elimination, and applications to Cournot, auctions and voting.', 'Masters'),
    title='Dominance at work: Cournot, auctions and voting', short='Applications', badge='5.3', minutes=45,
    lead='Watch IESDS solve the Cournot duopoly by halving intervals, prove that truthful bidding is dominant in a second price auction, and see candidates move to the median voter.',
    desc='IESDS in the Cournot duopoly with and without calculus, practice problems E1 and E5, second and first price auctions, below cost Bertrand prices, the Hotelling location game, discrete Bertrand with strict and weak elimination, the streetlamp with refunds and the guess two thirds puzzle.',
    summary='Cournot solved by iterated elimination, truthful bidding in second price auctions, the median voter, and where weak dominance misleads.',
    keywords=['Cournot', 'IESDS', 'Vickrey auction', 'first price auction', 'Hotelling', 'median voter', 'mechanism design'],
    recap='<p>Iterated elimination solves the Cournot duopoly by halving the surviving interval to 30. In a second price auction bidding your value is weakly dominant, and two candidates on a line both end at the median.</p>')
