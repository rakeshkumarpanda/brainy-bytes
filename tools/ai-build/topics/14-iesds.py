# Chapter 5.2: iterated elimination of strictly dominated strategies. Source: lecture 6 (why common knowledge lets us
# eliminate repeatedly, the blue eyed islanders, the IESDS algorithm and the two slide 9 corrections, the Marketing
# War to {M, H}, the slide 11 game cell by cell giving (U, L) = (4, 3) via C, then M and D, then R, self enforcement and
# Pareto of (U, L), theorems 5 to 8 with proofs, weak elimination depending on order, the report card) and lecture 5
# (section 8, practice problem E giving (Y, P) = (6, 7)), with practice problems D2, D3 and D7 from the lecture 6 notes.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('iesds', r'''
# IESDS on the slide 11 game: delete every strictly dominated row and column each round
G = {"U": {"L": (4, 3), "C": (5, 1), "R": (6, 2)},
     "M": {"L": (2, 1), "C": (8, 4), "R": (3, 6)},
     "D": {"L": (3, 0), "C": (9, 6), "R": (2, 8)}}
rows, cols = ["U", "M", "D"], ["L", "C", "R"]
k = 0
while True:
    dr = [r for r in rows if any(all(G[o][c][0] > G[r][c][0] for c in cols) for o in rows if o != r)]
    dc = [c for c in cols if any(all(G[r][o][1] > G[r][c][1] for r in rows) for o in cols if o != c)]
    if not dr and not dc:
        break
    k += 1
    print("round", k, "delete rows", dr, "columns", dc)
    rows = [r for r in rows if r not in dr]
    cols = [c for c in cols if c not in dc]
print("survivors:", rows, cols)
''')

K.lesson('why', 'Why we may eliminate again and again', f'''
<p>Chapter 5.1 showed that a rational player never uses a strictly dominated strategy. Common knowledge of rationality lets us go further, one layer at a time.</p>
{table(['Layer', 'Reasoning on the slide 11 game'], [
    ['0', 'Player 2 is rational, so she never plays column C (R beats it)'],
    ['1', 'Player 1 knows player 2 is rational, so he ignores C. In the smaller game M and D become dominated'],
    ['2', 'Player 2 knows player 1 knows she is rational, so she expects only row U. Now R is dominated'],
    ['k', 'Each round of elimination uses one more layer of "I know that you know that…"']])}
{fxs(
    fx('IESDS, round k', '<i>DS</i><sub><i>i</i></sub><sup><i>k</i></sup> = {{ <i>s</i><sub><i>i</i></sub> ∈ <i>S</i><sub><i>i</i></sub><sup><i>k</i></sup> : some <i>s</i>′<sub><i>i</i></sub> ∈ <i>S</i><sub><i>i</i></sub><sup><i>k</i></sup> beats it against every <i>s</i><sub>−<i>i</i></sub> ∈ <i>S</i><sub>−<i>i</i></sub><sup><i>k</i></sup> }}', 'Compare only against strategies that still survive.', key=True),
    fx('Update', '<i>S</i><sub><i>i</i></sub><sup><i>k</i>+1</sup> = <i>S</i><sub><i>i</i></sub><sup><i>k</i></sup> ∖ <i>DS</i><sub><i>i</i></sub><sup><i>k</i></sup>', 'Remove the elements. Stop when no player has a dominated strategy. Every profile of survivors is a prediction.', key=True))}
{note('Two small slip ups on slide 9: the dominator must range over the current set Sᵢᵏ, and the update is Sᵢᵏ minus DSᵢᵏ, not minus a set that contains DSᵢᵏ. Slide 6 also says "strictly" where it means "weakly" in two places. The formulas are the correct part.', 'tip')}
{scene('the blue eyed islanders', '<p>Islanders must leave on the night they work out that their own eyes are blue. A visitor announces "at least one of you has blue eyes". Everyone already knew it, yet the announcement makes it common knowledge, and with k blue eyed people all leave on night k. Each night peels off one layer of "knows that knows", just like each round of IESDS. In "guess two thirds of the average" experiments, real people stop after one to three layers, which is why predictions needing many rounds are less reliable in practice.</p>')}
''', kw=['IESDS', 'common knowledge of rationality', 'layers of reasoning', 'algorithm', 'blue eyed islanders', 'guess two thirds'])

K.lesson('slide11', 'Worked examples: the Marketing War and slide 11', f'''
{steps('Marketing War (slide 10)', [
    'Round 1: M ▷₁ L (8 &gt; 6, 4 &gt; 2, 1 &gt; 0) and by symmetry M ▷₂ L. Delete row L and column L together.',
    'Round 2 on {{M, H}}: against M, 4 &gt; 3, but against H, 1 &lt; 2. No domination for either player.',
    eq('Survivors {{M, H}} × {{M, H}}: four profiles. IESDS says "nobody goes low" but no more'),
    'Among the four, only (M, M) and (H, H) are self enforcing. Finding them needs Nash equilibrium.'])}
{table(['Slide 11 game', 'L', 'C', 'R'], [['U', '4, 3', '5, 1', '6, 2'], ['M', '2, 1', '8, 4', '3, 6'], ['D', '3, 0', '9, 6', '2, 8']])}
{steps('Slide 11, cell by cell', [
    'Round 1, player 1: U is best against L (4) and D is best against C (9), so neither can be dominated. M is beaten by U against L but wins against C, so nothing goes.',
    'Round 1, player 2: R = (2, 6, 8) against C = (1, 4, 6): 2 &gt; 1, 6 &gt; 4, 8 &gt; 6, so R ▷₂ C. Delete C. One dominator is enough.',
    'Round 2, player 1 against L and R only: U = (4, 6) beats M = (2, 3) and D = (3, 2). Delete M and D.',
    'Round 3, player 2 with only row U: L gives 3, R gives 2. Delete R.',
    eq('IESDS equilibrium (U, L) with payoffs (4, 3). Order: C, then M and D, then R')])}
{viz('iesds')}
{code('iesds')}
<p>Neither player has a dominant strategy here, so the dominant strategy equilibrium says nothing, yet IESDS pins down one answer. Is it self enforcing? Yes: player 1 moving down column L gets 2 or 3, less than 4, and player 2 moving along row U gets 1 or 2, less than 3. Is it the best? No. (D, C) = (9, 6) Pareto dominates it, and the Pareto optimal profiles are (9, 6) and (2, 8). Solving each player\'s problem separately, holding the others fixed, need not maximize anything for the group.</p>
{steps('Lecture 5 practice problem E', [
    'Round 1: Z is dominated by Y for firm A (6 &gt; 1, 5 &gt; 0, 2 &gt; 0). Delete Z.',
    'Round 2: with rows X and Y, R is dominated by P for firm B (3 &gt; 1, 7 &gt; 0). Delete R.',
    'Round 3: with columns P and Q, X is dominated by Y (6 &gt; 4, 5 &gt; 3). Delete X.',
    eq('Round 4: in row Y, P gives 7 against Q\'s 6. IESDS gives (Y, P) = (6, 7)')])}
''', kw=['Marketing War', 'slide 11', 'worked example', 'self enforcing', 'practice problem E', 'Pareto dominated equilibrium'])

K.lesson('theorems', 'Theorems about IESDS', f'''
{table(['Theorem', 'Statement'], [
    ['5', 'If a strict dominant strategy equilibrium exists, IESDS leaves exactly it after one round'],
    ['6', 'Every Nash equilibrium survives IESDS'],
    ['7', 'In a finite game, if IESDS leaves one profile, it is the unique Nash equilibrium'],
    ['8', 'For strict dominance in finite games, the order of deletion does not change the survivors (Gilboa, Kalai and Zemel 1990)']])}
{fxs(fx('Nash equilibrium (preview)', '<i>v</i><sub><i>i</i></sub>(<i>s</i><sub><i>i</i></sub>*, <i>s</i>*<sub>−<i>i</i></sub>) ≥ <i>v</i><sub><i>i</i></sub>(<i>s</i><sub><i>i</i></sub>, <i>s</i>*<sub>−<i>i</i></sub>) for every <i>i</i> and every <i>s</i><sub><i>i</i></sub>', 'No player gains by a unilateral deviation. The course defines it fully in later lectures.', key=True))}
{steps('Proof of theorem 6: Nash equilibria are never deleted', [
    'Suppose some part of a Nash equilibrium s* is deleted. Let round k be the first time, and sᵢ* the strategy deleted.',
    'Before round k nothing of s* was deleted, so s*₋ᵢ is still available in round k.',
    'Deletion means some s′ᵢ beats sᵢ* against every surviving s₋ᵢ, in particular against s*₋ᵢ.',
    'So vᵢ(s′ᵢ, s*₋ᵢ) &gt; vᵢ(sᵢ*, s*₋ᵢ), and player i gains by deviating from s*.',
    eq('That contradicts s* being a Nash equilibrium.')])}
<h3>With weak dominance, order matters</h3>
{table(['Order game', 'L', 'R'], [['T', '1, 1', '0, 0'], ['M', '1, 1', '2, 1'], ['B', '0, 0', '2, 1']])}
{steps('Two orders, two answers', [
    'M weakly dominates both T and B for player 1.',
    'Delete T first: on rows M and B, R = (1, 1) weakly beats L = (1, 0). Delete L. Payoff (2, 1).',
    'Delete B first: on rows T and M, L = (1, 1) weakly beats R = (0, 1). Delete R. Payoff (1, 1).',
    eq('Different orders give different predictions, one reason the course uses strict dominance')])}
{viz('iesds', pre='weak', mode='weak', order='first')}
{table(['Property', 'IESDS', 'Why'], [
    ['Existence', 'Holds', 'A finite strict partial order always has an undominated element'],
    ['Uniqueness', 'Fails', 'Marketing War leaves four profiles, RPS deletes nothing'],
    ['Stronger than DSE', 'Yes', 'Finds any DSE in one round and solves slide 11, which has none'],
    ['Needs', 'Common knowledge', 'One more layer of "knows that knows" per round'],
    ['Pareto optimal', 'Fails', 'Slide 11 ends at (4, 3), dominated by (9, 6)']])}
{deep('Proof idea of theorem 8, order independence', '<p>Removing the opponents\' strategies only shrinks the list of s₋ᵢ to check, so a strategy strictly dominated in a game stays strictly dominated in every smaller game that keeps its dominator. If the dominator was deleted first, its own dominator takes over, by transitivity, and that chain ends at a survivor because the game is finite. So a deletion can be postponed but never lost, and every maximal sequence of deletions ends at the same sets. With weak dominance a tie can make the replacement fail, which is exactly what the order game shows.</p>')}
{ladder(
    '<p>Cross out the choices nobody sensible would make, then look again: with fewer options left, more choices become silly. Keep going until nothing more can be crossed out.</p>',
    '<p>IESDS deletes all strictly dominated strategies, compared only within the current game, round after round. Slide 11 ends at (U, L) = (4, 3). Strict IESDS is order independent, always leaves something, finds any DSE, and keeps every Nash equilibrium. Weak IESDS depends on order.</p>',
    '<p>With mixed strategy domination, IESDS gives the rationalizable strategies in two player games (Bernheim 1984, Pearce 1984). Rationalizability is exactly what common knowledge of rationality implies, a weaker prediction than Nash equilibrium.</p>',
    '<p>Level k and cognitive hierarchy models (Stahl and Wilson, Camerer, Ho and Chong 2004) replace common knowledge with a small number of reasoning steps and fit laboratory data better. In AI, iterated best response and double oracle methods for large games are computational relatives of iterated elimination.</p>')}
''', kw=['theorems', 'Nash equilibrium preview', 'order independence', 'weak elimination', 'rationalizability', 'report card', 'level k'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'IESDS stands for', ['Iterated elimination of strictly dominated strategies', 'Independent equilibrium of strategic decision systems', 'Iterated expected strategy decision search', 'None of these'], 0,
       'Elimination.', 'Delete strictly dominated strategies, then repeat in the smaller game.')
K.quiz('e', 'In slide 11, which strategy is deleted first?', ['M', 'C', 'R', 'U'], 1,
       'Look at player 2.', 'R strictly dominates C: 2 > 1, 6 > 4, 8 > 6.')
K.quiz('e', 'The IESDS outcome of slide 11 is', ['(M, C) = (8, 4)', '(D, C) = (9, 6)', '(U, L) = (4, 3)', '(U, R) = (6, 2)'], 2,
       'C, then M and D, then R.', 'Only U and L survive.')
K.quiz('e', 'What survives IESDS in the Marketing War?', ['(L, L)', '{M, H} for each player', '(H, H)', 'Everything'], 1,
       'L goes in round 1.', 'After L is deleted, M and H are incomparable.')
K.quiz('m', 'What justifies the second and later rounds of IESDS?', ['Pareto optimality', 'Common knowledge of rationality', 'Fairness', 'Randomness'], 1,
       'Knowing that others are rational.', 'Each round uses one more layer of "I know that you know".')
K.quiz('m', 'In slide 11, M and D become dominated only after', ['L is deleted', 'C is deleted', 'R is deleted', 'U is deleted'], 1,
       'D was best against C.', 'Without C, U beats M and D in both remaining columns.')
K.quiz('m', 'Does strict IESDS depend on the order of deletion in finite games?', ['Yes', 'No', 'Only with three players', 'Only in zero sum games'], 1,
       'Theorem 8.', 'Strict elimination always reaches the same survivors.')
K.quiz('m', 'Can IESDS remove a Nash equilibrium?', ['Yes, often', 'No, every Nash equilibrium survives', 'Only weak ones', 'Only in Cournot'], 1,
       'Theorem 6.', 'Deleting part of s* would give a profitable deviation, a contradiction.')
K.quiz('h', 'Is the slide 11 prediction (4, 3) Pareto optimal?', ['Yes', 'No, (9, 6) dominates it', 'No, (8, 4) is the only better one', 'It is zero sum'], 1,
       'Look at (D, C).', '(9, 6) is better for both. The Pareto optimal profiles are (9, 6) and (2, 8).')
K.quiz('h', 'In the weak order game, deleting T first gives player 1', ['1', '2', '0', 'Undefined'], 1,
       'Then R beats L.', 'The path ends at M or B with R, payoff 2.')
K.quiz('x', 'If IESDS leaves a single profile in a finite game, that profile is', ['Pareto optimal', 'The unique Nash equilibrium', 'A mixed equilibrium', 'Not self enforcing'], 1,
       'Theorem 7.', 'Every Nash equilibrium survives, and a single survivor must be stable.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Slide 11: how many rounds does IESDS take before nothing more can be deleted?', '3', 'C, then M and D, then R.',
       ['Round 1: delete C.', 'Round 2: delete M and D.', 'Round 3: delete R.', eq('3 rounds of deletion')], check=3)
K.calc('e', 'Marketing War: how many profiles survive IESDS?', '4', '{M, H} for each.',
       ['Each player keeps M and H.', 'Profiles = 2 × 2.', eq('4')], check=4)
K.calc('e', 'Slide 11: what is player 2\'s payoff at the IESDS outcome?', '3', '(U, L).',
       ['Survivor (U, L).', 'Payoffs (4, 3).', eq('player 2 gets 3')], check=3)
K.calc('m', 'Slide 11: what is the total payoff at (U, L) and at (D, C)? Give (D, C) minus (U, L).', '8', '15 against 7.',
       ['(U, L) total: 4 + 3 = 7.', '(D, C) total: 9 + 6 = 15.', eq('15 − 7 = 8')], check=8)
K.calc('m', 'Practice D7: in slide 11 change (U, R) to (6, 4). What is player 2\'s payoff at the new IESDS outcome?', '4', 'R becomes dominant.',
       ['Column R = (4, 6, 8) now beats L = (3, 1, 0) and C = (1, 4, 6).', 'Against R only: U = 6, M = 3, D = 2. Keep U.', eq('outcome (U, R) = (6, 4)')], check=4)
K.calc('m', 'Practice D8: Marketing War with a subsidy of 3 to any firm choosing L. What does each firm get in the new dominant strategy equilibrium?', '9', 'L becomes dominant.',
       ['Player 1\'s row L becomes (9, 5, 3), beating M = (8, 4, 1) and H = (4, 3, 2).', 'By symmetry L is dominant for player 2.', eq('(L, L) = (6 + 3, 6 + 3) = (9, 9)')], check=9)
K.calc('m', 'Lecture 5 practice E: what is the sum of payoffs at the IESDS outcome (Y, P)?', '13', '(6, 7).',
       ['Survivor (Y, P).', 'Payoffs (6, 7).', eq('6 + 7 = 13')], check=13)
K.calc('h', 'A 4 × 4 game where each round deletes exactly one row or one column, ending at a single profile. How many rounds?', '6', 'Count deletions.',
       ['Start with 4 rows and 4 columns, end with 1 and 1.', 'Rows to delete: 3. Columns to delete: 3.', eq('3 + 3 = 6 rounds')], check=6)
K.calc('h', 'Weak order game: deleting B first, what payoff does player 1 end with?', '1', 'Then L beats R.',
       ['Rows T and M left.', 'Player 2: L = (1, 1) weakly beats R = (0, 1). Delete R.', eq('In column L, T and M both give player 1 a payoff of 1')], check=1)
K.calc('h', 'Practice D2, the 4 × 4 game with rows A to D and columns W to Z (load the d2 preset). Run strict IESDS. How many profiles survive?', '6', 'W goes first, then D, then Z.',
       ['Round 1: column W is strictly dominated for player 2, since Z beats it in every row (4 &gt; 2, 1 &gt; 0, 1 &gt; 0, 8 &gt; 5). No row is dominated yet.', 'Round 2: without W, row D is strictly dominated for player 1.', 'Round 3: without D, column Z is strictly dominated.', eq('Survivors: rows A, B, C and columns X, Y, so 3 × 2 = 6 profiles'), 'IESDS narrows the game but does not solve it, so Nash equilibrium is needed.'], check=6)
K.calc('x', 'Guess two thirds of the average, guesses in [0, 100]. After k rounds of eliminating guesses above (2/3)ᵏ × 100, what is the upper bound after 5 rounds? Two decimals.', '13.17', '(2/3)⁵ × 100.',
       ['Round 1: no guess above 66.67 can be best.', 'Each round multiplies the bound by 2/3.', eq('(2/3)⁵ × 100 = 13.17'), 'With common knowledge the bound goes to 0, the only survivor.'], check=100 * (2 / 3) ** 5, tol=0.005)

# ---------------------------------------------------------------- assignments
K.assign('iesds', 'm', 'Run IESDS on a bimatrix',
         '<p>Write <code>iesds(table)</code> for a bimatrix (list of rows of [a, b]). Each round delete every strictly dominated row and column, comparing only surviving strategies. Return [surviving row indices, surviving column indices].</p>',
         '''
def iesds(table):
    # your code here
    pass
''', [("iesds([[[4, 3], [5, 1], [6, 2]], [[2, 1], [8, 4], [3, 6]], [[3, 0], [9, 6], [2, 8]]])", [[0], [0]]),
      ("iesds([[[6, 6], [2, 8], [0, 4]], [[8, 2], [4, 4], [1, 3]], [[4, 0], [3, 1], [2, 2]]])", [[1, 2], [1, 2]]),
      ("iesds([[[0, 0], [-1, 1], [1, -1]], [[1, -1], [0, 0], [-1, 1]], [[-1, 1], [1, -1], [0, 0]]])", [[0, 1, 2], [0, 1, 2]])],
         '''
def iesds(table):
    rows = list(range(len(table)))
    cols = list(range(len(table[0])))
    while True:
        dr = [r for r in rows if any(all(table[o][c][0] > table[r][c][0] for c in cols) for o in rows if o != r)]
        dc = [c for c in cols if any(all(table[r][o][1] > table[r][c][1] for r in rows) for o in cols if o != c)]
        if not dr and not dc:
            return [rows, cols]
        rows = [r for r in rows if r not in dr]
        cols = [c for c in cols if c not in dc]
''', 'Find both players\' dominated strategies first, then delete them together.',
         '<p>The tests are slide 11, the Marketing War, and Rock, Paper, Scissors, where nothing is ever deleted.</p>')
K.assign('ne', 'h', 'Check theorem 6 on a game',
         '<p>Write <code>ne_survive(table)</code>. Find every pure Nash equilibrium (no profitable unilateral deviation) and return True if each one survives strict IESDS, which it always should.</p>',
         '''
def ne_survive(table):
    # your code here
    pass
''', [("ne_survive([[[4, 3], [5, 1], [6, 2]], [[2, 1], [8, 4], [3, 6]], [[3, 0], [9, 6], [2, 8]]])", True),
      ("ne_survive([[[6, 6], [2, 8], [0, 4]], [[8, 2], [4, 4], [1, 3]], [[4, 0], [3, 1], [2, 2]]])", True)],
         '''
def ne_survive(table):
    R, C = len(table), len(table[0])
    ne = [(r, c) for r in range(R) for c in range(C)
          if all(table[x][c][0] <= table[r][c][0] for x in range(R)) and all(table[r][y][1] <= table[r][c][1] for y in range(C))]
    rows, cols = list(range(R)), list(range(C))
    while True:
        dr = [r for r in rows if any(all(table[o][c][0] > table[r][c][0] for c in cols) for o in rows if o != r)]
        dc = [c for c in cols if any(all(table[r][o][1] > table[r][c][1] for r in rows) for o in cols if o != c)]
        if not dr and not dc:
            break
        rows = [r for r in rows if r not in dr]
        cols = [c for c in cols if c not in dc]
    return all(r in rows and c in cols for r, c in ne)
''', 'Reuse your IESDS function and a check for unilateral deviations.',
         '<p>In the Marketing War the Nash equilibria (M, M) and (H, H) both lie inside the surviving {M, H} × {M, H}.</p>')

K.must('Algorithm', 'Each round delete every strictly dominated strategy of every player, comparing only survivors. Stop when nothing is dominated.')
K.must('Common knowledge', 'Round k uses k layers of "I know that you know". Real people manage about 1 to 3 layers.')
K.must('Slide 11', 'R ▷ C, then U ▷ M and D, then L ▷ R. Outcome (U, L) = (4, 3), self enforcing but Pareto dominated by (9, 6).')
K.must('Theorems', 'DSE found in one round. Every NE survives. Unique survivor = unique NE. Strict IESDS is order independent.')
K.must('Limits', 'Marketing War leaves {M, H}², RPS deletes nothing. Weak IESDS depends on order: (2, 1) or (1, 1).')

T = K.topic(
    slug='iesds', topic='iesds', step=(5, 'Dominance and iterated elimination', 'aai-dom', 'Predict play without guessing: dominance, the dominant strategy equilibrium, iterated elimination, and applications to Cournot, auctions and voting.', 'Masters'),
    title='Iterated elimination of dominated strategies', short='IESDS', badge='5.2', minutes=50,
    lead='Use common knowledge of rationality to cross out dominated strategies round after round, solve the slide 11 game cell by cell, and learn the four theorems that make the method trustworthy.',
    desc='Why common knowledge allows repeated elimination, the IESDS algorithm and slide corrections, the Marketing War, the slide 11 game, lecture 5 practice problem E, self enforcement and Pareto, theorems 5 to 8 with a proof that Nash equilibria survive, weak elimination and order dependence, and the report card.',
    summary='The IESDS algorithm, the slide 11 and Marketing War examples, theorems about IESDS and Nash equilibrium, and why weak elimination depends on order.',
    keywords=['IESDS', 'iterated elimination', 'dominated strategies', 'common knowledge', 'Nash equilibrium', 'order independence', 'rationalizability'],
    recap='<p>Delete strictly dominated strategies, then look again in the smaller game. The slide 11 game ends at (U, L) = (4, 3). Strict elimination never depends on order and never removes a Nash equilibrium.</p>')
