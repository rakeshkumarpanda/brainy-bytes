# Chapter 5.1: dominance and the dominant strategy equilibrium. Source: lecture 6 (strict domination, how to check it
# in a table and the mistake made twice in class, the Prisoner's Dilemma, the altruistic version, Rock Paper Scissors,
# the Marketing War partial ranking, dominating, dominated, dominant and submissive, the strict partial order proof,
# weak domination and the slide against textbook definitions, the voting example and its correction, domination by a
# mixed strategy, the dominant strategy equilibrium, the uniqueness lemma and theorem, existence, uniqueness and
# invariance report, which payoff changes do not matter, and theorem 4 that rational players never play dominated
# strategies) and practice problems B1, B3 and C from the lecture 6 notes.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('dominates', r'''
# Strict and weak dominance for the row player of a bimatrix
mkt = [[(6, 6), (2, 8), (0, 4)],
       [(8, 2), (4, 4), (1, 3)],
       [(4, 0), (3, 1), (2, 2)]]
names = ["L", "M", "H"]

def strict(t, a, b):          # row a strictly dominates row b
    return all(t[a][c][0] > t[b][c][0] for c in range(len(t[0])))

def weak(t, a, b):            # textbook version: >= everywhere and > somewhere
    ge = all(t[a][c][0] >= t[b][c][0] for c in range(len(t[0])))
    return ge and any(t[a][c][0] > t[b][c][0] for c in range(len(t[0])))

for a in range(3):
    for b in range(3):
        if a != b and strict(mkt, a, b):
            print(names[a], "strictly dominates", names[b])
print("M vs H:", strict(mkt, 1, 2), " H vs M:", strict(mkt, 2, 1), " so M and H are not comparable")
''')

K.code('belief', r'''
# Theorem 4: a strictly dominated strategy is worse under every belief about the other player
import random
random.seed(1)
C_row = [-1, -4]          # Prisoner's Dilemma, player 1 confesses, against (M, C)
M_row = [-2, -5]          # player 1 stays mum
for trial in range(5):
    p = random.random()                    # belief that player 2 stays mum
    eC = p * C_row[0] + (1 - p) * C_row[1]
    eM = p * M_row[0] + (1 - p) * M_row[1]
    print(f"belief P(M) = {p:.2f}: E[C] = {eC:6.2f}  E[M] = {eM:6.2f}  C better: {eC > eM}")
''')

K.lesson('strict', 'Strict domination', f'''
<p>Sometimes one of your strategies is better than another whatever the others do. Then you never need to guess what they will do to know you should not play the worse one.</p>
{fxs(
    fx('Strict domination', '<i>s</i><sub><i>i</i></sub> ▷<sub><i>i</i></sub> <i>s</i>′<sub><i>i</i></sub> ⟺ <i>v</i><sub><i>i</i></sub>(<i>s</i><sub><i>i</i></sub>, <i>s</i><sub>−<i>i</i></sub>) &gt; <i>v</i><sub><i>i</i></sub>(<i>s</i>′<sub><i>i</i></sub>, <i>s</i><sub>−<i>i</i></sub>) for every <i>s</i><sub>−<i>i</i></sub>', 'Only player i\'s own payoffs are compared, once for each situation the others can create.', key=True),
    fx('Weak domination', '<i>s</i><sub><i>i</i></sub> ⊵<sub><i>i</i></sub> <i>s</i>′<sub><i>i</i></sub> ⟺ ≥ for every <i>s</i><sub>−<i>i</i></sub>', 'Textbooks add "and &gt; for at least one s₋ᵢ". State which version you use in an exam.'))}
{note('The mistake made twice in class: checking player 1 by mixing in the second number of each cell, or by moving down a column. Rule: for the row player compare first numbers, moving across columns. For the column player compare second numbers, moving down rows. Moving along the other player\'s strategies is exactly "for every s₋ᵢ".', 'warn')}
{steps('Lecture examples', [
    'Prisoner\'s Dilemma: against M, C gives −1 &gt; −2. Against C, −4 &gt; −5. So C ▷₁ M, and by symmetry C ▷₂ M.',
    'With altruism ½ the table is (−3, −3), (−5.5, −3.5), (−3.5, −5.5), (−6, −6). Now −3 &gt; −3.5 and −5.5 &gt; −6, so M ▷₁ C. The direction reversed.',
    'Rock, Paper, Scissors: each strategy is the only best reply to something, so nothing dominates anything, not even weakly.',
    eq('Marketing War: M ▷₁ L (8 &gt; 6, 4 &gt; 2, 1 &gt; 0), but M and H are not comparable (1 &lt; 2 against H)')])}
{viz('dominance')}
{code('dominates')}
''', kw=['strict domination', 'weak domination', 'dominance check', 'row player', 'column player', 'altruism reversal'])

K.lesson('vocab', 'Dominating, dominated, dominant, submissive', f'''
{table(['Term', 'Needs', 'Meaning for strategy sᵢ'], [
    ['Dominating', 'at least one', 'sᵢ beats some other strategy'],
    ['Dominated', 'at least one', 'some other strategy beats sᵢ'],
    ['Dominant', 'all others', 'sᵢ beats every other strategy'],
    ['Submissive', 'all others', 'every other strategy beats sᵢ']])}
{table(['Strategy', 'Dominating', 'Dominated', 'Dominant', 'Submissive'], [
    ['PD: C', 'yes', 'no', 'yes', 'no'], ['PD: M', 'no', 'yes', 'no', 'yes'],
    ['Marketing: M', 'yes', 'no', 'no, does not beat H', 'no'], ['Marketing: L', 'no', 'yes', 'no', 'no, H does not beat it'],
    ['Marketing: H', 'no', 'no', 'no', 'no'], ['RPS: any', 'no', 'no', 'no', 'no']])}
<p>The difference matters. A dominant strategy, needed by the first solution concept, is rare. A dominated strategy, which is what elimination deletes, is common. A student thought a column could only be deleted if every other column beat it. One dominator is enough, because a rational player would switch to it. With only two strategies dominating equals dominant, which is why the Prisoner\'s Dilemma hides the difference.</p>
{steps('Theorem 1: strict domination is a strict partial order', [
    'Irreflexive: sᵢ ▷ sᵢ would need a number strictly bigger than itself.',
    'Asymmetric: sᵢ ▷ s′ᵢ and s′ᵢ ▷ sᵢ would give x &gt; y and y &gt; x at the same s₋ᵢ.',
    'Transitive: for every s₋ᵢ, a &gt; b and b &gt; c give a &gt; c.',
    eq('Not complete: M and H in the Marketing War, or any pair in RPS, are incomparable')])}
{deep('Domination by a mixed strategy', '<p>Player 1 has U = (3, 0), M = (0, 3) and D = (1, 1) against (L, R). Neither U nor M dominates D. But the 50/50 mix of U and M earns 1.5 against L and 1.5 against R, more than D\'s 1 in both. D is strictly dominated by a mixture. This course uses pure strategies for now, and a fuller elimination later removes such strategies too.</p>')}
{scene('the voting correction', '<p>In class, voting for your favourite candidate was offered as a weakly dominant strategy in plurality voting with alphabetical tie breaks. It is not. Voter 3 ranks c ≻ b ≻ a. Voter 1 votes a and voter 2 votes b. Voting sincerely for c makes a three way tie that a wins, her worst outcome. Voting for b makes b win. What is true is that voting for your least favourite is weakly dominated. The Gibbard Satterthwaite theorem says every non dictatorial rule with three or more candidates sometimes rewards insincere voting.</p>')}
''', kw=['dominant', 'dominated', 'dominating', 'submissive', 'partial order', 'mixed strategy domination', 'voting', 'Gibbard Satterthwaite'])

K.lesson('dse', 'The dominant strategy equilibrium', f'''
{fxs(
    fx('Strict dominant strategy equilibrium', '<i>s</i><sup>D</sup> with <i>s</i><sub><i>i</i></sub><sup>D</sup> strictly dominant for every player <i>i</i>', 'Everyone plays the strategy that is best against everything. No one needs to predict anyone.', key=True),
    fx('Rational players and dominated strategies', 'E<sub>μ</sub>[<i>v</i><sub><i>i</i></sub>(<i>s</i><sub><i>i</i></sub>)] − E<sub>μ</sub>[<i>v</i><sub><i>i</i></sub>(<i>s</i>′<sub><i>i</i></sub>)] = ∑ μ(<i>s</i><sub>−<i>i</i></sub>)[<i>v</i><sub><i>i</i></sub>(<i>s</i><sub><i>i</i></sub>, <i>s</i><sub>−<i>i</i></sub>) − <i>v</i><sub><i>i</i></sub>(<i>s</i>′<sub><i>i</i></sub>, <i>s</i><sub>−<i>i</i></sub>)] &gt; 0', 'Theorem 4: whatever the belief μ, a strictly dominated strategy has lower expected payoff, so a rational player never uses it.', key=True))}
<p>Examples: the Prisoner\'s Dilemma gives (C, C) with (−4, −4). With altruism it gives (M, M) with (−3, −3). Rock, Paper, Scissors and the Marketing War have none.</p>
{steps('Theorem 3: a strict dominant strategy equilibrium is unique (the proof many students missed the first time)', [
    'Assume two different ones, s and s′. Then some player j has sⱼ ≠ s′ⱼ.',
    'In s, sⱼ is strictly dominant, so it beats s′ⱼ: vⱼ(sⱼ, s₋ⱼ) &gt; vⱼ(s′ⱼ, s₋ⱼ) for all s₋ⱼ.',
    'In s′, s′ⱼ is strictly dominant, so vⱼ(s′ⱼ, s₋ⱼ) &gt; vⱼ(sⱼ, s₋ⱼ) for all s₋ⱼ.',
    'Fix one s₋ⱼ. The first line says x &gt; y and the second y &gt; x. Impossible.',
    eq('So there is at most one. With ≥ instead of &gt; the argument breaks, and weak ones can be many.')])}
{viz('altruism')}
{code('belief')}
{table(['Property', 'Strict DSE', 'Why'], [
    ['Existence', 'Fails', 'RPS, Marketing War, Cournot, Bertrand, streetlamp have none'],
    ['Uniqueness', 'Holds', 'Theorem 3 (fails for the weak version)'],
    ['Invariance', 'Fails', 'Altruism ½ flips (C, C) to (M, M)'],
    ['Pareto optimality', 'Fails', 'PD picks (C, C), the only wasteful profile']])}
{deep('Which payoff changes cannot affect dominance', '<p>Dominance compares player i\'s own payoffs with s₋ᵢ held fixed. So it is unchanged by any strictly increasing f(vᵢ), and by adding any term h(s₋ᵢ) that depends only on the others: f(vᵢ(sᵢ, s₋ᵢ)) + h(s₋ᵢ) &gt; f(vᵢ(s′ᵢ, s₋ᵢ)) + h(s₋ᵢ) exactly when vᵢ(sᵢ, s₋ᵢ) &gt; vᵢ(s′ᵢ, s₋ᵢ). Altruism is not of this form because vⱼ depends on player i\'s own choice too, which is why it could flip the prediction.</p>')}
{ladder(
    '<p>If one choice is better than another no matter what anyone else does, never make the worse choice. If one choice beats all the others, make it.</p>',
    '<p>sᵢ ▷ s′ᵢ needs vᵢ larger for every s₋ᵢ. Dominant beats all, dominated is beaten by one. A strict DSE is unique when it exists, but often does not exist, is not robust, and can be Pareto dominated.</p>',
    '<p>Strict domination by pure or mixed strategies is equivalent to never being a best response to any belief (for two players, via linear programming duality). Dominant strategy implementation is the strongest form of incentive compatibility in mechanism design.</p>',
    '<p>Strategy proof mechanisms, where truth telling is dominant, include the Vickrey auction and its generalization VCG. The Gibbard Satterthwaite theorem limits them for voting, and work on large markets and approximate strategy proofness studies how close practical systems such as school choice can get.</p>')}
''', kw=['dominant strategy equilibrium', 'uniqueness proof', 'rationality theorem', 'beliefs', 'existence', 'invariance', 'strategy proof'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'sᵢ strictly dominates s′ᵢ when', ['vᵢ(sᵢ, s₋ᵢ) > vᵢ(s′ᵢ, s₋ᵢ) for some s₋ᵢ', 'vᵢ(sᵢ, s₋ᵢ) > vᵢ(s′ᵢ, s₋ᵢ) for every s₋ᵢ', 'The other player prefers sᵢ', 'sᵢ has the largest single payoff'], 1,
       'Every situation.', 'Strict domination needs a strict win against every choice of the others.')
K.quiz('e', 'To check dominance for the row player you compare', ['Second numbers down a column', 'First numbers across the columns', 'Totals', 'Diagonals'], 1,
       'Own payoff, each column.', 'Row player: first numbers, one comparison per column.')
K.quiz('e', 'In the Prisoner\'s Dilemma, C is', ['Strictly dominated', 'Strictly dominant', 'Submissive', 'Incomparable with M'], 1,
       'Better against both.', 'C wins against M and against C.')
K.quiz('e', 'The dominant strategy equilibrium of the PD with altruism ½ is', ['(C, C)', '(M, M)', '(M, C)', 'None'], 1,
       'Altruism flips dominance.', '−3 > −3.5 and −5.5 > −6, so M dominates.')
K.quiz('m', 'In the Marketing War, M and H are', ['M dominates H', 'H dominates M', 'Incomparable', 'Equal'], 2,
       'Check against H.', 'M wins against L and M but loses against H (1 < 2).')
K.quiz('m', 'A strategy beaten by at least one other strategy is', ['Dominant', 'Dominated', 'Submissive', 'Dominating'], 1,
       'At least one.', 'Submissive would need every other strategy to beat it.')
K.quiz('m', 'Does Rock, Paper, Scissors have any dominated strategy?', ['Yes, Rock', 'Yes, all of them', 'No, not even weakly', 'Only weakly'], 2,
       'Each is a best reply to something.', 'A strategy that is the unique best reply to some s₋ᵢ cannot be dominated.')
K.quiz('m', 'Strict domination as a relation is', ['A total order', 'A strict partial order', 'An equivalence relation', 'Symmetric'], 1,
       'Irreflexive, asymmetric, transitive.', 'It need not be complete, so it is partial.')
K.quiz('h', 'Why can each player have at most one strictly dominant strategy?', ['By definition', 'Two would each strictly beat the other, contradicting asymmetry', 'Because of Pareto', 'Because games are finite'], 1,
       'Lemma 2.', 'If sᵢ and s′ᵢ were both dominant, sᵢ ▷ s′ᵢ and s′ᵢ ▷ sᵢ.')
K.quiz('h', 'Which change can never alter dominance for player i?', ['Adding altruism', 'Replacing vᵢ by 2vᵢ + 7', 'Changing another player\'s strategy set', 'Swapping rows'], 1,
       'Increasing transforms keep comparisons.', 'Dominance uses only > between player i\'s own payoffs with s₋ᵢ fixed.')
K.quiz('x', 'D = (1, 1) is not dominated by U = (3, 0) or M = (0, 3). It is strictly dominated by', ['Nothing', 'The 50/50 mixture of U and M', 'U alone', 'M alone'], 1,
       'Average U and M.', 'The mix earns 1.5 against both columns, more than 1.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'PD: by how much does C beat M for player 1 when player 2 plays M?', '1', '−1 against −2.',
       ['v₁(C, M) = −1.', 'v₁(M, M) = −2.', eq('difference = 1')], check=1)
K.calc('e', 'Marketing War: how many columns must you check to test whether M ▷₁ L?', '3', 'One per strategy of player 2.',
       ['Player 2 has L, M, H.', 'Each gives one comparison of first numbers.', eq('3 comparisons: 8 &gt; 6, 4 &gt; 2, 1 &gt; 0')], check=3)
K.calc('e', 'PD with altruism ½: what is v₁(C, M)?', '-3.5', '−1 + ½(−5).',
       ['Own payoff −1.', 'Half of the other\'s −5 is −2.5.', eq('−3.5')], check=-3.5)
K.calc('m', 'Altruistic PD: by how much does M beat C for player 1 when player 2 plays C?', '0.5', '−5.5 against −6.',
       ['v₁(M, C) = −5.5.', 'v₁(C, C) = −6.', eq('difference = 0.5')], check=0.5)
K.calc('m', 'Mixed domination: what does the 50/50 mix of U = (3, 0) and M = (0, 3) earn against column L?', '1.5', 'Average the first column.',
       ['U gives 3 against L.', 'M gives 0 against L.', eq('½ × 3 + ½ × 0 = 1.5 &gt; 1')], check=1.5)
K.calc('m', 'With U = (3, 0), M = (0, 3), D = (1, 1): the mix αU + (1 − α)M beats D against R when 3(1 − α) &gt; 1. What is the largest α allowed?', '0.6667', 'Solve 3 − 3α = 1.',
       ['Against R the mix earns 0α + 3(1 − α).', 'Need 3 − 3α &gt; 1, so α &lt; 2/3.', eq('largest α (not included) = 0.6667'), 'Against L the mix needs 3α &gt; 1, so α &gt; 1/3. Any α strictly between 1/3 and 2/3 works.'], check=2 / 3, tol=0.00005)
K.calc('m', 'How many ordered pairs of strategies must you test to find all strict dominance relations for a player with 4 strategies?', '12', 'Each ordered pair once.',
       ['Choose the dominator: 4 ways.', 'Choose a different dominated strategy: 3 ways.', eq('4 × 3 = 12')], check=12)
K.calc('h', 'Practice B1: rows T = (4, 2) and B = (3, 1) for player 1, columns L = (3, 1) and R = (4, 2) for player 2. How many strictly dominant strategies are there in total?', '2', 'Check each player.',
       ['Player 1: T beats B (4 &gt; 3, 2 &gt; 1), so T is dominant.', 'Player 2 (second numbers): R gets 4 against T and 2 against B, L gets 3 and 1. R is dominant.', eq('2 dominant strategies, DSE (T, R) = (2, 4)')], check=2)
K.calc('h', 'Altruistic PD with weight α: for which α does M become strictly better than C against M? Give the threshold, four decimals.', '0.3333', 'v₁(M, M) − v₁(C, M) = −1 + 3α.',
       ['v₁(M, M) = −2 − 2α and v₁(C, M) = −1 − 5α.', 'Difference = −1 + 3α.', eq('Positive when α &gt; 1/3 = 0.3333')], check=1 / 3, tol=0.00005)
K.calc('h', 'Expected payoffs with belief P(player 2 plays M) = 0.3 in the PD: what is E[C] − E[M] for player 1?', '1', 'The gap is 1 in each column.',
       ['E[C] = 0.3 × (−1) + 0.7 × (−4) = −3.1.', 'E[M] = 0.3 × (−2) + 0.7 × (−5) = −4.1.', eq('E[C] − E[M] = 1, whatever the belief')], check=1)
K.calc('x', 'Weak IESDS on the order game T = (1,1)(0,0), M = (1,1)(2,1), B = (0,0)(2,1): deleting T first, what payoff does player 1 end with?', '2', 'Then compare L and R for player 2.',
       ['After T goes, rows M and B. Player 2: R = (1, 1) against L = (1, 0), so R weakly dominates L.', 'Delete L. Player 1 gets 2 in column R from M or B.', eq('Final payoff to player 1 = 2'), 'Deleting B first instead leads to payoff 1, so weak elimination depends on order.'], check=2)

# ---------------------------------------------------------------- assignments
K.assign('dom', 'e', 'Does one row strictly dominate another?',
         '<p>Write <code>row_dominates(table, a, b)</code> for a bimatrix (list of rows of [x, y]). Return True if row a strictly dominates row b for the row player.</p>',
         '''
def row_dominates(table, a, b):
    # your code here
    pass
''', [("row_dominates([[[-2, -2], [-5, -1]], [[-1, -5], [-4, -4]]], 1, 0)", True), ("row_dominates([[[6, 6], [2, 8], [0, 4]], [[8, 2], [4, 4], [1, 3]], [[4, 0], [3, 1], [2, 2]]], 1, 2)", False),
      ("row_dominates([[[6, 6], [2, 8], [0, 4]], [[8, 2], [4, 4], [1, 3]], [[4, 0], [3, 1], [2, 2]]], 1, 0)", True)],
         '''
def row_dominates(table, a, b):
    return all(table[a][c][0] > table[b][c][0] for c in range(len(table[0])))
''', 'Use only the first number of each cell, column by column.', '<p>The tests are C over M in the PD, and M against H and L in the Marketing War.</p>')
K.assign('dse', 'm', 'Find the dominant strategy equilibrium',
         '<p>Write <code>dse(table)</code> for a bimatrix. Return [row, col] if each player has a strictly dominant strategy, otherwise None.</p>',
         '''
def dse(table):
    # your code here
    pass
''', [("dse([[[-2, -2], [-5, -1]], [[-1, -5], [-4, -4]]])", [1, 1]), ("dse([[[-3, -3], [-5.5, -3.5]], [[-3.5, -5.5], [-6, -6]]])", [0, 0]),
      ("dse([[[6, 6], [2, 8], [0, 4]], [[8, 2], [4, 4], [1, 3]], [[4, 0], [3, 1], [2, 2]]])", None)],
         '''
def dse(table):
    R, C = len(table), len(table[0])
    row = [r for r in range(R) if all(all(table[r][c][0] > table[o][c][0] for c in range(C)) for o in range(R) if o != r)]
    col = [c for c in range(C) if all(all(table[r][c][1] > table[r][o][1] for r in range(R)) for o in range(C) if o != c)]
    if row and col:
        return [row[0], col[0]]
    return None
''', 'A dominant row beats every other row in every column. A dominant column beats every other column in every row, using second numbers.',
         '<p>The PD gives (C, C), the altruistic PD gives (M, M), and the Marketing War has no dominant strategy equilibrium.</p>')

K.must('Strict domination', 'sᵢ ▷ s′ᵢ: vᵢ(sᵢ, s₋ᵢ) > vᵢ(s′ᵢ, s₋ᵢ) for every s₋ᵢ. Row player: first numbers across columns. Column player: second numbers down rows.')
K.must('Vocabulary', 'Dominating/dominated: beats/is beaten by at least one. Dominant/submissive: beats/is beaten by all. One dominator is enough to delete.')
K.must('Partial order', '▷ is irreflexive, asymmetric, transitive, not complete (RPS, M and H in the Marketing War). Weak: ≥ (textbook adds > once).')
K.must('DSE', 'Everyone plays a strictly dominant strategy. Unique if it exists. PD (C, C), altruistic PD (M, M), RPS and Marketing War none.')
K.must('Rationality', 'A rational player never plays a strictly dominated strategy under any belief. Increasing transforms and h(s₋ᵢ) do not change dominance.')

T = K.topic(
    slug='dominance', topic='dominance', step=(5, 'Dominance and iterated elimination', 'aai-dom', 'Predict play without guessing: dominance, the dominant strategy equilibrium, iterated elimination, and applications to Cournot, auctions and voting.', 'Masters'),
    title='Dominance and the dominant strategy equilibrium', short='Dominance', badge='5.1', minutes=50,
    lead='Spot strategies that are worse whatever others do, learn the exact vocabulary, prove that a dominant strategy equilibrium is unique, and see where this first solution concept fails.',
    desc='Strict and weak domination and how to check them in a table, the Prisoner\'s Dilemma, altruism, RPS and the Marketing War, dominating, dominated, dominant and submissive, the partial order proof, mixed strategy domination, the voting correction, the dominant strategy equilibrium, its uniqueness proof, the rationality theorem and its report card.',
    summary='Strict and weak dominance, the four dominance words, the dominant strategy equilibrium with its uniqueness proof, and its limits.',
    keywords=['dominance', 'strictly dominated', 'dominant strategy', 'dominant strategy equilibrium', 'partial order', 'altruism', 'rationality'],
    recap='<p>A strictly dominated strategy is worse whatever others do, so a rational player never uses it. When everyone has a dominant strategy the outcome is unique, but often no such strategy exists.</p>')
