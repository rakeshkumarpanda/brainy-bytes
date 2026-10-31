# Chapter 4.3: solution concepts and Pareto optimality. Source: lecture 5 (what a solution concept and an equilibrium
# are, why not a physics equilibrium, the vacuous concept against the dominant strategy concept, the four assumptions
# rational, intelligent, common knowledge, self enforcement, the lawyer threat example, existence, uniqueness and
# invariance, the Prisoner's Dilemma with altruism, Rock Paper Scissors as zero sum, the Marketing Campaign War,
# Pareto dominance and its two tests, the zero sum proof, practice problems A (farmers) and C (ride hailing), fairness)
# and lecture 6 (Pareto optimality in the dominance lecture).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('pareto', r'''
# Pareto optimal profiles of a bimatrix game
game = {("H","H"): (2,2), ("H","Mod"): (5,0),          # practice problem A, the farmers
        ("Mod","H"): (0,5), ("Mod","Mod"): (3,3)}

def dominates(x, y):            # x Pareto dominates y
    return all(a >= b for a, b in zip(x, y)) and any(a > b for a, b in zip(x, y))

for prof, pay in game.items():
    beaten_by = [p for p, q in game.items() if dominates(q, pay)]
    print(prof, pay, "Pareto optimal" if not beaten_by else f"dominated by {beaten_by[0]}")
''')

K.code('altruism', r'''
# Prisoner's Dilemma with altruism: add alpha times the other player's payoff
pd = {("M","M"): (-2,-2), ("M","C"): (-5,-1), ("C","M"): (-1,-5), ("C","C"): (-4,-4)}
for alpha in (0, 0.25, 0.5):
    g = {s: (a + alpha * b, b + alpha * a) for s, (a, b) in pd.items()}
    c_best = g[("C","M")][0] > g[("M","M")][0] and g[("C","C")][0] > g[("M","C")][0]
    print(f"alpha = {alpha}: (M,C) -> {g[('M','C')]},  confessing still dominant: {c_best}")
''')

K.lesson('concepts', 'What a solution concept is for', f'''
<p>Writing down a game does not tell us what will happen. A solution concept is a method that narrows all possible profiles down to the reasonable ones, either to advise players or to predict them. Whatever profile it selects is called an equilibrium of that concept.</p>
<p>The professor warned against the physics picture of equilibrium, a state a system returns to after a push. In game theory an equilibrium is simply what a chosen concept selects. There is no implied motion towards it.</p>
{table(['Candidate concept', 'Prisoner\'s Dilemma answer', 'Verdict'], [
    ['"Anything can happen"', 'All four profiles', 'Always exists, but gives no advice or prediction'],
    ['Play a strategy that is best whatever others do', '(C, C)', 'Sharp and useful, but not always available'],
    ['Nash equilibrium (later in the course)', '(C, C)', 'Exists far more often']])}
<h3>The four assumptions of equilibrium analysis</h3>
{table(['Assumption', 'Meaning in this course'], [
    ['Rational', 'Each player maximizes her own (expected) payoff'],
    ['Intelligent', 'Each player knows every action, the outcome map and everyone\'s preferences, as well as the analyst does'],
    ['Common knowledge', 'That everyone is rational and intelligent is itself common knowledge'],
    ['Self enforcement', 'The equilibrium must hold without any outside enforcer']])}
{scene('the gang lawyer', '<p>Suppose each suspect in the Prisoner\'s Dilemma gets a lawyer from the same gang who threatens his family if he confesses. Both stay mum and (M, M) results. That outcome is not self enforcing. It holds only because of a third party. Remove the threat and each suspect gains by confessing alone.</p>')}
<h3>What we want from a good concept</h3>
{table(['Property', 'Question it asks'], [
    ['Existence', 'Does it give an answer for every game?'],
    ['Uniqueness', 'Does it pick a small set, ideally one profile? "Anything can happen" fails badly here.'],
    ['Invariance', 'Does a small change in payoffs that keeps every ranking leave the answer the same?']])}
''', kw=['solution concept', 'equilibrium', 'rational', 'intelligent', 'common knowledge', 'self enforcement', 'existence', 'uniqueness', 'invariance'])

K.lesson('pareto', 'Pareto optimality', f'''
<p>Pareto optimality is not a solution concept. It does not predict anything. It is a yardstick for judging the answer a solution concept gives: does the equilibrium waste payoff that everyone could have shared?</p>
{fxs(
    fx('Pareto dominance', '<i>s</i> Pareto dominates <i>s</i>′ ⟺ <i>v</i><sub><i>i</i></sub>(<i>s</i>) ≥ <i>v</i><sub><i>i</i></sub>(<i>s</i>′) for all <i>i</i>, and &gt; for at least one <i>j</i>', 'Nobody is worse off and someone is strictly better off.', key=True),
    fx('Pareto optimal', '<i>s</i>′ is not Pareto dominated by any profile', 'Also called Pareto efficient.', key=True))}
{table(['Test', 'How to apply it'], [
    ['Direct test', 'Search for a profile that is at least as good for everyone and strictly better for someone. If one exists, the candidate is not optimal.'],
    ['Improvement test', 'Try to make one player strictly better off. If every such move hurts someone, the candidate is optimal.']])}
{steps('Prisoner\'s Dilemma', [
    '(M, M) = (−2, −2) beats (C, C) = (−4, −4) for both players, so (C, C) is not Pareto optimal.',
    'Nothing beats (M, M): (M, C) is worse for player 1, (C, M) worse for player 2, (C, C) worse for both.',
    '(M, C) and (C, M) hold the best payoff for one player, so nothing can dominate them.',
    eq('Pareto optimal: (M, M), (M, C), (C, M). Not optimal: (C, C), the dominant strategy outcome')])}
{viz('pareto')}
{code('pareto')}
{steps('Marketing Campaign War (rows and columns L, M, H)', [
    'Payoffs: (L,L) 6,6. (L,M) 2,8. (L,H) 0,4. (M,L) 8,2. (M,M) 4,4. (M,H) 1,3. (H,L) 4,0. (H,M) 3,1. (H,H) 2,2.',
    '(L, L) = (6, 6) beats (M, M) and every profile with H, strictly for both players.',
    '(L, M) and (M, L) contain 8, the largest single payoff, so nothing dominates them. Nothing dominates (6, 6) either.',
    eq('Pareto optimal: (L, L), (L, M), (M, L)')])}
{note('Pareto optimality says nothing about fairness. (2, 8) and (8, 2) are Pareto optimal next to the balanced (6, 6). It only rules out waste.', 'warn')}
''', kw=['Pareto optimal', 'Pareto dominance', 'Pareto efficient', 'direct test', 'improvement test', 'Marketing Campaign War', 'fairness'])

K.lesson('zerosum', 'Zero sum games, altruism and the practice problems', f'''
<h3>Rock, Paper, Scissors and a general proof</h3>
<p>In Rock, Paper, Scissors the winner gets 1 and the loser −1, and a tie gives 0 to both. The two payoffs always add to 0, so the game is zero sum. Checking nine cells one by one caused confusion in class. A short proof settles every cell at once.</p>
{steps('Claim: in a two player zero sum game every profile is Pareto optimal', [
    'Suppose s Pareto dominates s′. Then v₁(s) ≥ v₁(s′) and v₂(s) ≥ v₂(s′), with one strict.',
    'Zero sum means v₂ = −v₁, so the second inequality says −v₁(s) ≥ −v₁(s′), that is v₁(s) ≤ v₁(s′).',
    'Together with v₁(s) ≥ v₁(s′) this forces v₁(s) = v₁(s′), and then v₂(s) = v₂(s′) too.',
    eq('No inequality is strict, a contradiction. Every profile is Pareto optimal.')])}
<h3>The Prisoner\'s Dilemma with altruism</h3>
{fxs(fx('Altruistic payoff', '<i>v</i><sub><i>i</i></sub><sup>alt</sup>(<i>s</i>) = <i>v</i><sub><i>i</i></sub>(<i>s</i>) + ½ <i>v</i><sub><i>j</i></sub>(<i>s</i>)', 'Your own jail term at full weight plus half of the other\'s. Not an extra penalty added on top.', key=True))}
{table(['Profile', 'Original', 'With altruism ½'], [
    ['(M, M)', '(−2, −2)', '(−3, −3)'], ['(M, C)', '(−5, −1)', '(−5.5, −3.5)'], ['(C, M)', '(−1, −5)', '(−3.5, −5.5)'], ['(C, C)', '(−4, −4)', '(−6, −6)']])}
{code('altruism')}
<p>With weight ½, staying mum becomes the better reply to both choices: −3 beats −3.5 and −5.5 beats −6. Caring about the other person turns the dilemma into a game whose sensible outcome is also Pareto optimal. Chapter 5.1 finds the exact weight, ⅓, where this switch happens.</p>
{steps('Practice problem A: two farmers and one aquifer, pump Heavily (H) or Moderately (Mod)', [
    'Payoffs: (H,H) 2,2. (H,Mod) 5,0. (Mod,H) 0,5. (Mod,Mod) 3,3.',
    'H beats Mod for player 1 against H (2 &gt; 0) and against Mod (5 &gt; 3). The table is symmetric.',
    'So both pump heavily and get (2, 2). But (Mod, Mod) = (3, 3) Pareto dominates it.',
    eq('Pareto optimal: (Mod, Mod), (H, Mod), (Mod, H). The predicted outcome is the wasteful one.')])}
{steps('Practice problem C: two ride hailing apps choose driver incentives Small, Medium, Large', [
    'Payoffs: (S,S) 5,5. (S,Md) 9,2. (S,Lg) 3,3. (Md,S) 2,9. (Md,Md) 6,6. (Md,Lg) 1,4. (Lg,S) 3,3. (Lg,Md) 4,1. (Lg,Lg) 2,2.',
    '(Md, Md) = (6, 6) dominates (S, S) and all profiles with Lg.',
    '(S, Md) and (Md, S) contain 9, the largest payoff.',
    eq('Pareto optimal: (S, Md), (Md, S), (Md, Md)')])}
{viz('pareto', pre='farmers')}
{deep('The tragedy of the commons', '<p>The farmers game is a two player preview of the tragedy of the commons, studied with n players and continuous effort next in the course. When each user of a shared resource gets the full benefit of extra use but bears only a share of the damage, self interest pushes total use above the level that would be best for the group. Elinor Ostrom\'s field work showed communities avoiding this with monitoring and graduated sanctions, which change the game rather than the players.</p>')}
{ladder(
    '<p>A rule for predicting games should always give an answer, a clear one, and not change wildly over tiny details. Separately, we can ask whether the result wastes anything that would make someone better off for free.</p>',
    '<p>Equilibrium analysis assumes rational, intelligent players, common knowledge of both, and self enforcement. Pareto dominance is ≥ for all and &gt; for one. In the Prisoner\'s Dilemma the dominant outcome (C, C) is the only profile that is not Pareto optimal. In zero sum games all profiles are optimal.</p>',
    '<p>The Pareto frontier of a game is the set of undominated payoff vectors. Folk theorems for repeated games show that patient players can sustain Pareto superior outcomes such as (M, M) as equilibria, which links efficiency to the shadow of the future.</p>',
    '<p>Measuring the price of anarchy (Koutsoupias and Papadimitriou 1999) quantifies how far equilibria can fall below the social optimum, for example in routing networks and congestion games. Multi agent learning research studies how to steer self interested learners towards Pareto efficient outcomes, through reward shaping, communication or opponent shaping.</p>')}
''', kw=['zero sum', 'Rock Paper Scissors', 'altruism', 'practice problem A', 'practice problem C', 'tragedy of the commons', 'price of anarchy'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Pareto optimality is', ['A solution concept that predicts play', 'A way to judge whether an outcome wastes payoff', 'The same as fairness', 'The same as Nash equilibrium'], 1,
       'It evaluates, it does not predict.', 'It asks whether someone could be made better off without hurting anyone.')
K.quiz('e', 'Which Prisoner\'s Dilemma profile is NOT Pareto optimal?', ['(M, M)', '(M, C)', '(C, M)', '(C, C)'], 3,
       'Compare with (M, M).', '(M, M) is better for both than (C, C).')
K.quiz('e', 'In a zero sum game', ['Some profiles are not Pareto optimal', 'Every profile is Pareto optimal', 'No profile is Pareto optimal', 'Only ties are Pareto optimal'], 1,
       'One player\'s gain is the other\'s loss.', 'Making one better off always makes the other worse off.')
K.quiz('e', 'Self enforcement means', ['A court enforces the outcome', 'No outside party is needed to keep the outcome', 'Players sign a contract', 'Nature picks the outcome'], 1,
       'The gang lawyer example.', 'An outcome kept only by a threat from outside is not self enforcing.')
K.quiz('m', 'The vacuous concept "anything can happen" fails which property?', ['Existence', 'Uniqueness', 'Invariance', 'Rationality'], 1,
       'It selects everything.', 'It always exists but never narrows the profiles.')
K.quiz('m', 'In the Marketing Campaign War, which profiles are Pareto optimal?', ['Only (L, L)', '(L, L), (L, M), (M, L)', 'All with H', '(M, M) only'], 1,
       '(6, 6) beats many.', '(L, L) dominates (M, M) and every H profile. (L, M) and (M, L) hold the payoff 8.')
K.quiz('m', 'In the PD with altruism ½, v₁(M, C) is', ['−5', '−5.5', '−3.5', '−6'], 1,
       '−5 + ½(−1).', 'Own −5 plus half of the other\'s −1.')
K.quiz('m', '"Intelligent" in equilibrium analysis means', ['High IQ', 'Knowing all actions, the outcome map and everyone\'s preferences', 'Maximizing payoff', 'Able to compute fast'], 1,
       'Separate from rational.', 'Rational is about maximizing. Intelligent is about knowing the game as well as the analyst.')
K.quiz('h', 'Practice problem A (farmers): the dominant strategy outcome is', ['(Mod, Mod), Pareto optimal', '(H, H), not Pareto optimal', '(H, Mod)', 'None'], 1,
       'H beats Mod against both.', '(H, H) = (2, 2) is dominated by (Mod, Mod) = (3, 3), the same structure as the Prisoner\'s Dilemma.')
K.quiz('h', 'Invariance asks that', ['The game has one equilibrium', 'Small payoff changes that keep every ranking do not change the answer much', 'All players are identical', 'Payoffs are integers'], 1,
       'Robustness.', 'A concept that flips with tiny rank preserving changes is fragile.')
K.quiz('x', 'Is (2, 8) in the Marketing War Pareto optimal?', ['No, it is unfair', 'Yes, nothing gives player 2 at least 8 with player 1 at least 2 and one strictly more', 'No, (6, 6) dominates it', 'Only if zero sum'], 1,
       'Check the column player\'s 8.', 'No profile gives player 2 eight or more except (L, M) itself.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'PD with altruism ½: what is v₁(M, M)?', '-3', '−2 + ½(−2).',
       ['Own payoff −2.', 'Half of the other\'s −2 is −1.', eq('−2 − 1 = −3')], check=-3)
K.calc('e', 'PD with altruism ½: what is v₂(M, C)?', '-3.5', 'Player 2 confessed.',
       ['Own payoff −1.', 'Half of player 1\'s −5 is −2.5.', eq('−1 − 2.5 = −3.5')], check=-3.5)
K.calc('e', 'How many profiles of the Marketing War are Pareto optimal?', '3', 'Use (6, 6).',
       ['(6, 6) dominates (M, M) and all five profiles with H.', '(L, M) and (M, L) contain the top payoff 8.', eq('3 Pareto optimal profiles')], check=3)
K.calc('m', 'How many of the 9 Rock, Paper, Scissors profiles are Pareto optimal?', '9', 'Zero sum.',
       ['Every cell sums to 0.', 'In a zero sum game no profile can dominate another.', eq('All 9')], check=9)
K.calc('m', 'Practice problem C: how many profiles does (Md, Md) Pareto dominate?', '6', 'Count cells with both payoffs below 6.',
       ['(S, S) = (5, 5).', '(S, Lg), (Md, Lg), (Lg, S), (Lg, Md), (Lg, Lg) are all below 6 in both.', eq('1 + 5 = 6')], check=6)
K.calc('m', 'PD: by how much does the total payoff fall from (M, M) to (C, C)?', '4', 'Sum both players.',
       ['(M, M) total: −4.', '(C, C) total: −8.', eq('fall = 4')], check=4)
K.calc('m', 'PD with altruism α: v₁(M, M) − v₁(C, M) = (−2 − 2α) − (−1 − 5α). For α = ½, what is it?', '0.5', 'Positive means M is the better reply to M.',
       ['−2 − 2α + 1 + 5α = −1 + 3α.', 'At α = ½: −1 + 1.5.', eq('= 0.5 &gt; 0, so M beats C against M')], check=0.5)
K.calc('h', 'PD with altruism α: at which α is player 1 indifferent between M and C against M? Four decimals.', '0.3333', 'Solve −1 + 3α = 0.',
       ['From the previous problem: v₁(M, M) − v₁(C, M) = −1 + 3α.', 'Against C: v₁(M, C) − v₁(C, C) = (−5 − α) − (−4 − 4α) = −1 + 3α as well.', eq('α = 1/3 = 0.3333')], check=1 / 3, tol=0.00005)
K.calc('h', 'Farmers game: what is the total payoff lost by self interest compared with the Pareto best symmetric outcome?', '2', '(Mod, Mod) against (H, H).',
       ['(Mod, Mod) total = 6.', '(H, H) total = 4.', eq('loss = 2')], check=2)
K.calc('h', 'A 3 × 3 game has payoffs (k, k) on the diagonal for k = 1, 2, 3 and (0, 0) elsewhere. How many profiles are Pareto optimal?', '1', 'Look for the best for both.',
       ['(3, 3) is at least as good as every cell for both players.', 'It is strictly better than every other cell for both.', eq('Only (3, 3) is Pareto optimal')], check=1)
K.calc('x', 'Price of anarchy for the PD as a cost game: total years at the worst equilibrium divided by the fewest total years. Give the ratio.', '2', 'Years, not payoffs.',
       ['Equilibrium (C, C): 4 + 4 = 8 years.', 'Best total: (M, M) with 2 + 2 = 4 years.', eq('8 ÷ 4 = 2')], check=2)

# ---------------------------------------------------------------- assignments
K.assign('pareto', 'm', 'Pareto optimal cells',
         '<p>Write <code>pareto_cells(table)</code> for a bimatrix (list of rows of [a, b]). Return the sorted list of [row, col] that no other cell Pareto dominates.</p>',
         '''
def pareto_cells(table):
    # your code here
    pass
''', [("pareto_cells([[[-2, -2], [-5, -1]], [[-1, -5], [-4, -4]]])", [[0, 0], [0, 1], [1, 0]]),
      ("pareto_cells([[[6, 6], [2, 8], [0, 4]], [[8, 2], [4, 4], [1, 3]], [[4, 0], [3, 1], [2, 2]]])", [[0, 0], [0, 1], [1, 0]]),
      ("pareto_cells([[[0, 0], [-1, 1]], [[1, -1], [0, 0]]])", [[0, 0], [0, 1], [1, 0], [1, 1]])],
         '''
def pareto_cells(table):
    cells = [(r, c, tuple(x)) for r, row in enumerate(table) for c, x in enumerate(row)]
    def dom(x, y):
        return all(a >= b for a, b in zip(x, y)) and any(a > b for a, b in zip(x, y))
    return [[r, c] for r, c, x in cells if not any(dom(y, x) for _, _, y in cells)]
''', 'Compare every cell with every other cell using the definition: ≥ in all coordinates and > in one.',
         '<p>The tests are the Prisoner\'s Dilemma, the Marketing War, and a small zero sum game where every cell is optimal.</p>')
K.assign('altruism', 'e', 'Add altruism to a game',
         '<p>Write <code>altruistic(table, alpha)</code> that returns a new bimatrix where each cell [a, b] becomes [a + alpha·b, b + alpha·a].</p>',
         '''
def altruistic(table, alpha):
    # your code here
    pass
''', [("altruistic([[[-2, -2], [-5, -1]], [[-1, -5], [-4, -4]]], 0.5)", [[[-3.0, -3.0], [-5.5, -3.5]], [[-3.5, -5.5], [-6.0, -6.0]]]),
      ("altruistic([[[1, 2]]], 0)", [[[1, 2]]])],
         '''
def altruistic(table, alpha):
    return [[[a + alpha * b, b + alpha * a] for a, b in row] for row in table]
''', 'A nested list comprehension keeps the shape.', '<p>The first test reproduces the slide: (−3, −3), (−5½, −3½), (−3½, −5½), (−6, −6).</p>')

K.must('Solution concept', 'Narrows profiles to reasonable ones. Its pick is an equilibrium. Not a physics equilibrium.')
K.must('Four assumptions', 'Rational (maximize), intelligent (know the game), common knowledge of both, self enforcement (no outside enforcer).')
K.must('Good concept', 'Existence, uniqueness, invariance. "Anything can happen" exists but is not unique.')
K.must('Pareto', 's dominates s′: ≥ for all, > for one. PD: only (C, C) fails. Marketing War: (L,L), (L,M), (M,L). Zero sum: all optimal.')
K.must('Altruism', 'vᵢ + ½vⱼ gives (−3,−3), (−5.5,−3.5), (−3.5,−5.5), (−6,−6). Mum becomes best. Pareto is not fairness.')

T = K.topic(
    slug='solution-concepts-pareto', topic='solution-concepts-pareto', step=(4, 'Games between rational agents', 'aai-games', 'Model interactions between several rational agents: normal form games, Cournot, Bertrand, public goods, solution concepts and Pareto optimality.', 'College and masters'),
    title='Solution concepts and Pareto optimality', short='Pareto', badge='4.3', minutes=45,
    lead='Learn what a solution concept must deliver and what equilibrium analysis assumes, then judge outcomes with Pareto optimality on the Prisoner\'s Dilemma, the Marketing War and zero sum games.',
    desc='Solution concepts and equilibria, the four assumptions of equilibrium analysis, self enforcement and the gang lawyer, existence, uniqueness and invariance, Pareto dominance and its two tests, the Prisoner\'s Dilemma, the Marketing Campaign War, the zero sum proof, altruism, and practice problems A and C.',
    summary='What solution concepts are, the assumptions behind them, and Pareto optimality with worked games and the zero sum proof.',
    keywords=['solution concept', 'Pareto optimality', 'equilibrium', 'zero sum', 'altruism', 'self enforcement', 'tragedy of the commons'],
    recap='<p>A solution concept picks reasonable outcomes and should exist, be sharp and be robust. Pareto optimality judges those outcomes: the Prisoner\'s Dilemma prediction (C, C) is the only wasteful profile.</p>')
